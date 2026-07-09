#!/usr/bin/env python3
"""moticore-agent entry point — newspaper architecture.

1. preprocessor : assemble 4-layer MOTICORE DAILY newspaper
2. decision     : single Gemini call → §SECTION-delimited remarks
3. action       : parse remarks → execute (file writes, issue replies, log)
"""
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_motive
from memory import append_action, format_recent_for_report, get_recent_note_paths
from decision import run_consciousness, parse_remarks
from issues import (get_open_issues, post_comment, close_issue, PROGRESS_ISSUE,
                     fetch_discussions, post_discussion_reply)
from reader import get_next_chunk, save_cursor, load_cursor
from preprocessor import detect_mode, build_newspaper

QUESTION_LABEL = "[代理提問]"
INSIGHT_LABEL = "[moti 洞見]"

# 每天固定三個發文時段（台北時間），確保 moti 至少每個時段公開發表一次
# 心跳的思考，而不是永遠停留在「打算發布」的反思迴圈裡。
JOURNAL_WINDOWS = [
    ("morning", 7, 11),
    ("noon", 11, 15),
    ("evening", 18, 22),
]
JOURNAL_WINDOW_LABELS = {"morning": "晨間", "noon": "午間", "evening": "晚間"}
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

HORIZON_PATH = "core/HORIZON.md"


# ── action handlers ────────────────────────────────────────────────

def handle_issue_responses(parsed: dict, github_token: str) -> None:
    for r in parsed.get("issue_responses", []):
        num = r.get("issue_number")
        comment = r.get("comment", "").strip()
        if not num or not comment or num == PROGRESS_ISSUE:
            continue
        post_comment(github_token, num, comment)
        if r.get("close", False):
            close_issue(github_token, num)


def handle_giscus_replies(parsed: dict, github_token: str, label_map: dict,
                          repo_root: Path) -> None:
    """Post moti's §GISCUS_REPLY replies and persist which comment IDs have
    been replied to, so future heartbeats stop presenting them as new."""
    replies = parsed.get("giscus_replies", [])
    if not replies or not github_token:
        return
    replied_path = repo_root / "memory" / "giscus-replied.json"
    try:
        replied_ids = set(json.loads(replied_path.read_text(encoding="utf-8"))) \
            if replied_path.exists() else set()
    except Exception:
        replied_ids = set()

    for reply in replies:
        label = reply.get("label", "")
        body = reply.get("content", "").strip()
        target = label_map.get(label)
        if not target or not body:
            print(f"[run] ⚠️ Giscus reply label 無法辨識，略過：{label}")
            continue
        ok = post_discussion_reply(
            github_token, target["discussion_id"], target["comment_id"], body
        )
        if ok:
            replied_ids.add(target["comment_id"])

    replied_path.parent.mkdir(exist_ok=True)
    replied_path.write_text(json.dumps(sorted(replied_ids)), encoding="utf-8")


def handle_file_writes(parsed: dict, repo_root: Path) -> list[dict]:
    written = []
    for fw in parsed.get("file_writes", []):
        path_str = fw.get("path", "").strip()
        content = fw.get("content", "")
        if not path_str or not content:
            continue
        if path_str.strip("/").split("/")[0] == "agent":
            print(f"[run] BLOCKED: {path_str}")
            continue
        file_path = repo_root / path_str
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"[run] Written: {path_str}")
        written.append(fw)
    return written


def check_horizon_lifecycle(action: dict, written: list[dict]) -> None:
    """crystallize/dissolve are self-reported poles that are only meaningful
    if core/HORIZON.md was actually edited to move/add the corresponding
    question. We can't fabricate that content (unlike the journal fallback),
    so instead we make the gap visible: if the pole is claimed without a
    matching HORIZON.md write, flag it in the action's own deviation field so
    the next heartbeat's "最近行動" shows the discrepancy instead of it
    silently passing as a clean 完成."""
    pole = action.get("pole", "")
    if pole not in ("crystallize", "dissolve"):
        return
    horizon_touched = any(fw.get("path") == HORIZON_PATH for fw in written)
    if horizon_touched:
        return
    label = "crystallize" if pole == "crystallize" else "dissolve"
    note = f"顯著（宣稱 {label} 但未寫 §FILE {HORIZON_PATH}，問題未真正搬動/新增）"
    existing = action.get("deviation", "").strip()
    action["deviation"] = f"{existing}；{note}" if existing and existing != "無" else note
    print(f"[run] ⚠️ pole={label} claimed without a {HORIZON_PATH} write")


def _current_journal_window(now_utc: datetime) -> str | None:
    """Return which fixed posting window ('morning'/'noon'/'evening') the
    given UTC time falls into (Taipei local time), or None if outside all
    windows."""
    local_hour = now_utc.astimezone(TAIPEI_TZ).hour
    for name, start, end in JOURNAL_WINDOWS:
        if start <= local_hour < end:
            return name
    return None


def _load_journal_state(repo_root: Path) -> dict:
    path = repo_root / "memory" / "journal-state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_journal_state(repo_root: Path, date_str: str, window: str) -> None:
    path = repo_root / "memory" / "journal-state.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        json.dumps({"date": date_str, "window": window}, ensure_ascii=False),
        encoding="utf-8",
    )


def handle_journal(parsed: dict, repo_root: Path, action: dict,
                   window: str | None, already_posted: bool) -> dict | None:
    """Write a public post to web/content/posts/ during a designated posting
    window, at most once per window per day. Falls back to a minimal entry
    built from the action summary if moti didn't fill in §JOURNAL, so a post
    is guaranteed whenever a window is due."""
    if not window or already_posted:
        return None

    now = datetime.now(timezone.utc)
    local_date = now.astimezone(TAIPEI_TZ).strftime("%Y-%m-%d")

    journal = parsed.get("journal", {})
    title = journal.get("title", "").strip()
    content = journal.get("content", "").strip()
    if not title or not content:
        title = title or f"心跳紀錄・{JOURNAL_WINDOW_LABELS[window]}"
        content = content or action.get("summary", "").strip() or "（本次心跳沒有可分享的具體內容）"

    # Slug is date+window only (no title). Title text varies between LLM
    # calls even for the "same" window, so a title-based slug let two
    # heartbeats that both saw already_posted=False (e.g. state update from
    # an earlier run not yet visible) write two separate files for one
    # window. A deterministic slug makes the second write collide with the
    # first instead of creating a duplicate post.
    slug = f"{now.strftime('%Y%m%d')}-{window}"
    file_path = repo_root / "web" / "content" / "posts" / f"{slug}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = f"---\ntitle: {title}\ndate: {now.strftime('%Y-%m-%d')}\n---\n\n"
    file_path.write_text(frontmatter + content + "\n", encoding="utf-8")
    _save_journal_state(repo_root, local_date, window)
    print(f"[run] Journal posted ({window}): web/content/posts/{slug}.md")
    return {"path": f"web/content/posts/{slug}.md", "content": content}


def handle_read_request(parsed: dict, repo_root: Path) -> None:
    """Persist moti's read-request for next heartbeat."""
    req = parsed.get("read_request", {})
    if not req:
        return
    req_path = repo_root / "memory" / "read-requests.json"
    req_path.parent.mkdir(exist_ok=True)
    req_path.write_text(json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
    notes = req.get("notes", [])
    dialogues = req.get("dialogues", [])
    print(f"[run] Read-request saved: {len(notes)} notes, {len(dialogues)} dialogues")


def handle_question(parsed: dict, open_issues: list, github_token: str,
                    reading_context: str) -> None:
    question = parsed.get("question", "").strip()
    if not question:
        return
    already_open = any(
        QUESTION_LABEL in i.get("title", "")
        for i in open_issues
        if i.get("number") != PROGRESS_ISSUE
    )
    if already_open:
        print("[run] Skipping question — unanswered [代理提問] already open")
        return
    from issues import OWNER, REPO
    import requests
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = f"{question}\n\n---\n_閱讀脈絡：{reading_context}_"
    requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
        headers=headers,
        json={"title": f"{QUESTION_LABEL} {question[:60]}", "body": body},
    ).raise_for_status()
    print("[run] Question issue opened")


def handle_insight(parsed: dict, open_issues: list, github_token: str) -> None:
    """Open a proactive insight Issue if §INSIGHT is present and none already open."""
    insight = parsed.get("insight", {})
    if not insight or not insight.get("title"):
        return
    already_open = any(
        INSIGHT_LABEL in i.get("title", "")
        for i in open_issues
        if i.get("number") != PROGRESS_ISSUE
    )
    if already_open:
        print("[run] Skipping insight — [moti 洞見] Issue already open")
        return
    from issues import OWNER, REPO
    import requests
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    title = insight["title"]
    content = insight.get("content", "").strip()
    body = f"{content}\n\n---\n_自動開立_" if content else "_自動開立_"
    requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
        headers=headers,
        json={"title": f"{INSIGHT_LABEL} {title[:60]}", "body": body},
    ).raise_for_status()
    print(f"[run] Insight issue opened: {title[:60]}")


def post_progress_report(github_token: str, mode: str, reading_context: str,
                         cursor: dict, action: dict) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if cursor and mode == "READING":
        finished = cursor.get("finished", False)
        idx = cursor.get("file_index", 0) + 1
        off = cursor.get("char_offset", 0)
        progress = "全部讀完！" if finished else f"第 {idx}/29 篇 《{reading_context}》，至第 {off:,} 字"
    elif mode == "SYNTHESIS":
        progress = "閱讀完畢，知識綜合中"
    else:
        progress = "（回應模式，無閱讀進度）"
    summary = action.get("summary", "").strip()[:100]
    post_comment(
        github_token, PROGRESS_ISSUE,
        f"**{now}** [{mode}]\n\n📖 {progress}\n💡 {summary}"
    )
    print(f"[run] Progress posted (Issue #{PROGRESS_ISSUE})")


# ── retry wrapper ────────────────────────────────────────────

def call_with_retry(motive: str, newspaper: str, retries: int = 4) -> str:
    waits = [10, 20, 40, 60]
    for attempt in range(retries):
        try:
            return run_consciousness(motive, newspaper)
        except Exception as exc:
            msg = str(exc)
            if any(k in msg for k in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]):
                wait = waits[attempt]
                print(f"[run] Gemini unavailable, retry in {wait}s ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise
    return ""


# ── main ─────────────────────────────────────────────────

def main():
    print(f"[run] moticore-agent started at {datetime.now(timezone.utc).isoformat()}Z")

    github_token = os.environ.get("GITHUB_TOKEN", "")
    dialogues_token = os.environ.get("DIALOGUES_TOKEN", "")
    vercel_token = os.environ.get("VERCEL_TOKEN", "")
    vercel_project_id = os.environ.get("VERCEL_PROJECT_ID", "")

    motive = load_motive(REPO_ROOT)
    print("[run] Motive loaded")

    current_cursor = load_cursor(REPO_ROOT)

    open_issues = []
    if github_token:
        try:
            open_issues = get_open_issues(github_token)
            print(f"[run] Open issues: {len(open_issues)}")
        except Exception as e:
            print(f"[run] Warning (issues): {e}")

    giscus_note = ""
    giscus_label_map = {}
    if github_token:
        try:
            replied_path = REPO_ROOT / "memory" / "giscus-replied.json"
            try:
                replied_ids = set(json.loads(replied_path.read_text(encoding="utf-8"))) \
                    if replied_path.exists() else set()
            except Exception:
                replied_ids = set()

            discussions_content, giscus_label_map = fetch_discussions(
                github_token, replied_ids=replied_ids
            )
            if discussions_content:
                (REPO_ROOT / "memory" / "giscus-comments.md").write_text(
                    discussions_content, encoding="utf-8"
                )
                print("[run] giscus-comments.md updated")
            if giscus_label_map:
                giscus_note = (
                    "💬 讀者留言：\n" + discussions_content +
                    "\n\n若想回應，使用 §GISCUS_REPLY label={代號}（如 G1），"
                    "只有標了代號的留言表示尚未回覆。"
                )
        except Exception as e:
            print(f"[run] Warning (discussions): {e}")

    if github_token:
        mode, pending_issues = detect_mode(open_issues, github_token, cursor=current_cursor)
    else:
        mode, pending_issues = ("READING", [])
    print(f"[run] Mode: {mode} | Pending: {len(pending_issues)}")

    reading_chunk = ""
    reading_context = ""
    new_cursor = None
    if mode == "READING" and dialogues_token:
        try:
            result = get_next_chunk(dialogues_token, REPO_ROOT)
            reading_chunk = result["chunk_text"]
            reading_context = result["conversation_title"]
            new_cursor = result["cursor"]
            print(f"[run] Reading: {reading_context}")
        except Exception as e:
            print(f"[run] Warning (reader): {e}")

    display_cursor = new_cursor or current_cursor
    recent_log = format_recent_for_report(REPO_ROOT, n=3)
    recent_note_paths = get_recent_note_paths(REPO_ROOT, n=3)

    # Determine whether this heartbeat falls in one of the 3 daily posting
    # windows and whether that window has already been published today.
    now = datetime.now(timezone.utc)
    journal_window = _current_journal_window(now)
    journal_state = _load_journal_state(REPO_ROOT)
    local_date = now.astimezone(TAIPEI_TZ).strftime("%Y-%m-%d")
    journal_already_posted = (
        journal_window is not None
        and journal_state.get("date") == local_date
        and journal_state.get("window") == journal_window
    )
    journal_note = ""
    if journal_window and not journal_already_posted:
        label = JOURNAL_WINDOW_LABELS[journal_window]
        journal_note = (
            f"📝 發文時段：{label}（今日尚未發布）—— 請在 §JOURNAL 寫下這次要公開分享的思考，"
            "會直接發布成 moticore.org 上的一篇文章。"
        )

    newspaper = build_newspaper(
        repo_root=REPO_ROOT,
        open_issues=open_issues,
        github_token=github_token,
        cursor=display_cursor,
        reading_chunk=reading_chunk,
        reading_context=reading_context,
        recent_log=recent_log,
        recent_note_paths=recent_note_paths,
        mode=mode,
        pending_issues=pending_issues,
        dialogues_token=dialogues_token,
        analytics_token=vercel_token,
        analytics_project_id=vercel_project_id,
        journal_note=journal_note,
        giscus_note=giscus_note,
    )
    print(f"[run] Newspaper assembled: {len(newspaper)} chars")

    print("[run] Calling Gemini...")
    raw_output = call_with_retry(motive, newspaper)
    if not raw_output:
        print("[run] Gemini unavailable, skipping.")
        sys.exit(0)

    parsed = parse_remarks(raw_output)
    action = parsed.get("action", {})
    print(f"[run] Action: {action.get('type')} (pole={action.get('pole', '?')}) — {action.get('summary')}")

    if parsed.get("truncated"):
        print(f"[run] ⚠️ Truncated sections: {parsed['truncated']}")

    if github_token:
        handle_issue_responses(parsed, github_token)
        handle_question(parsed, open_issues, github_token, reading_context)
        handle_insight(parsed, open_issues, github_token)
        handle_giscus_replies(parsed, github_token, giscus_label_map, REPO_ROOT)

    written = handle_file_writes(parsed, REPO_ROOT)
    journal_write = handle_journal(parsed, REPO_ROOT, action, journal_window, journal_already_posted)
    if journal_write:
        written.append(journal_write)
    check_horizon_lifecycle(action, written)
    handle_read_request(parsed, REPO_ROOT)

    if new_cursor:
        save_cursor(REPO_ROOT, new_cursor)

    append_action(REPO_ROOT, action, mode=mode, file_writes=written)

    if github_token:
        try:
            post_progress_report(github_token, mode, reading_context, display_cursor or {}, action)
        except Exception as e:
            print(f"[run] Warning (progress): {e}")

    print("[run] Done.")


if __name__ == "__main__":
    main()
