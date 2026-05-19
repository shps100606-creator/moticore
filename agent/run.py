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

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_motive
from memory import append_action, format_recent_for_report, get_recent_note_paths
from decision import run_consciousness, parse_remarks
from issues import get_open_issues, post_comment, close_issue, PROGRESS_ISSUE
from reader import get_next_chunk, save_cursor, load_cursor
from preprocessor import detect_mode, build_newspaper

QUESTION_LABEL = "[代理提問]"


# ── action handlers ──────────────────────────────────────────────────────────

def handle_issue_responses(parsed: dict, github_token: str) -> None:
    for r in parsed.get("issue_responses", []):
        num = r.get("issue_number")
        comment = r.get("comment", "").strip()
        if not num or not comment or num == PROGRESS_ISSUE:
            continue
        post_comment(github_token, num, comment)
        if r.get("close", False):
            close_issue(github_token, num)


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


def post_progress_report(github_token: str, mode: str, reading_context: str,
                         cursor: dict, action: dict) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if cursor and mode == "READING":
        finished = cursor.get("finished", False)
        idx = cursor.get("file_index", 0) + 1
        off = cursor.get("char_offset", 0)
        progress = "全部讀完！" if finished else f"第 {idx}/29 篇 《{reading_context}》，至第 {off:,} 字"
    elif mode == "SYNTHESIS":
        progress = "閱讀完毕，知識綜合中"
    else:
        progress = "（回應模式，無閱讀進度）"
    summary = action.get("summary", "").strip()[:100]
    post_comment(
        github_token, PROGRESS_ISSUE,
        f"**{now}** [{mode}]\n\n📖 {progress}\n💡 {summary}"
    )
    print(f"[run] Progress posted (Issue #{PROGRESS_ISSUE})")


# ── retry wrapper ────────────────────────────────────────────────────────────

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


# ── main ───────────────────────────────────────────────────────────────────

def main():
    print(f"[run] moticore-agent started at {datetime.now(timezone.utc).isoformat()}Z")

    github_token = os.environ.get("GITHUB_TOKEN", "")
    dialogues_token = os.environ.get("DIALOGUES_TOKEN", "")

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
    )
    print(f"[run] Newspaper assembled: {len(newspaper)} chars")

    print("[run] Calling Gemini...")
    raw_output = call_with_retry(motive, newspaper)
    if not raw_output:
        print("[run] Gemini unavailable, skipping.")
        sys.exit(0)

    parsed = parse_remarks(raw_output)
    action = parsed.get("action", {})
    print(f"[run] Action: {action.get('type')} — {action.get('summary')}")

    if parsed.get("truncated"):
        print(f"[run] ⚠️ Truncated sections: {parsed['truncated']}")

    if github_token:
        handle_issue_responses(parsed, github_token)
        handle_question(parsed, open_issues, github_token, reading_context)

    written = handle_file_writes(parsed, REPO_ROOT)
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
