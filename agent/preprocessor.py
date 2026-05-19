"""Newspaper assembler — builds the structured daily report for the main model.

Layer 1: Motivation core (always first, never truncated)
Layer 2: Today's status (code-generated summary, ~200 tokens)
Layer 3: Main task (reading chunk OR issues to respond OR synthesis task)
Layer 4: Knowledge background (selected notes, truncation-safe)
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from issues import PROGRESS_ISSUE, MOTI_BOT_LOGIN, get_issue_comments


# ── helpers ────────────────────────────────────────────────────────────────

def _read(path: Path, max_chars: int = 0) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] if max_chars else text


def _section(title: str, body: str) -> str:
    bar = "━" * 44
    return f"\n{bar}\n{title}\n{bar}\n{body}\n"


def _load_requested_files(repo_root: Path) -> list[str]:
    """Load file paths moti requested last heartbeat via memory/read-requests.json."""
    req_path = repo_root / "memory" / "read-requests.json"
    if not req_path.exists():
        return []
    try:
        data = json.loads(req_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [p for p in data if isinstance(p, str)]
    except Exception:
        pass
    return []


# ── mode detection ──────────────────────────────────────────────────────────

def detect_mode(open_issues: list, github_token: str, cursor: dict | None = None) -> tuple[str, list]:
    """Return ('READING'|'RESPONSE'|'SYNTHESIS', pending_issues).

    RESPONSE mode when any non-progress issue has:
      - never received a moti reply, OR
      - a human comment NEWER than moti's last reply.

    SYNTHESIS mode when:
      - reading is finished (cursor.finished == True), AND
      - no pending response issues.

    READING mode otherwise.
    """
    pending = []
    for issue in open_issues:
        num = issue.get("number")
        if num == PROGRESS_ISSUE:
            continue
        if not github_token:
            continue
        comments = get_issue_comments(github_token, num, max_comments=20)
        moti = [
            c for c in comments
            if MOTI_BOT_LOGIN in c.get("user", {}).get("login", "")
        ]
        human = [
            c for c in comments
            if c.get("user", {}).get("type") != "Bot"
            and "github-actions" not in c.get("user", {}).get("login", "")
        ]

        if not moti:
            # Never replied — always pending
            pending.append(issue)
            continue

        # Only pending if there are human comments NEWER than moti's last reply
        last_moti_time = max(c["created_at"] for c in moti)
        new_human = [c for c in human if c.get("created_at", "") > last_moti_time]
        if new_human:
            pending.append(issue)

    if pending:
        return "RESPONSE", pending

    # No pending responses — check if reading is finished
    reading_finished = cursor.get("finished", False) if cursor else False
    if reading_finished:
        return "SYNTHESIS", []

    return "READING", []


# ── layer builders ──────────────────────────────────────────────────────────

def _layer1_motive(repo_root: Path) -> str:
    motive = _read(repo_root / "core" / "MOTIVE.md")
    return _section("【一】動機核　　（永遠完整，不可截斷）", motive)


def _layer2_status(repo_root: Path, mode: str, cursor: dict,
                   pending_issues: list, recent_log: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Reading progress
    if cursor:
        finished = cursor.get("finished", False)
        if finished:
            progress = "全部讀完！"
        else:
            idx = cursor.get("file_index", 0) + 1
            off = cursor.get("char_offset", 0)
            progress = f"第 {idx}/29 篇，讀至第 {off:,} 字"
    else:
        progress = "（未知）"

    # Urgent items
    if pending_issues:
        urgent_lines = [f"  ⚠️  Issue #{i['number']}「{i.get('title','')[:40]}」"
                        for i in pending_issues]
        urgent = "\n".join(urgent_lines)
    else:
        urgent = "  ✅ 無"

    # Current task from STATUS.md (first 600 chars)
    status = _read(repo_root / "core" / "STATUS.md", max_chars=600)

    body = (
        f"時間：{now}\n"
        f"模式：{mode}\n"
        f"閱讀進度：{progress}\n"
        f"\n緊急事項：\n{urgent}\n"
        f"\n最近行動：\n{recent_log}\n"
        f"\n當前任務（STATUS.md）：\n{status}"
    )
    return _section("【二】今日狀態　（程式碼生成，~200 tokens）", body)


def _layer3_reading(reading_chunk: str, reading_context: str) -> str:
    body = f"篇名：{reading_context}\n\n原文：\n{reading_chunk}"
    return _section("【三】本次任務：閱讀　（不可截斷）", body)


def _layer3_response(pending_issues: list, github_token: str) -> str:
    import re

    def sanitize(text: str, max_len: int = 600) -> str:
        text = re.sub(r"```[\s\S]*?```", "[code block]", text)
        text = re.sub(r"`[^`]*`", "[code]", text)
        return re.sub(r"\s+", " ", text).strip()[:max_len]

    parts = []
    for issue in pending_issues:
        num = issue["number"]
        title = issue.get("title", "")
        body = sanitize(issue.get("body") or "")

        comments_text = ""
        if github_token:
            comments = get_issue_comments(github_token, num, max_comments=20)
            human = [
                c for c in comments
                if c.get("user", {}).get("type") != "Bot"
                and "github-actions" not in c.get("user", {}).get("login", "")
            ]
            moti_last = next(
                (c for c in reversed(comments)
                 if MOTI_BOT_LOGIN in c.get("user", {}).get("login", "")), None
            )
            if human:
                snips = [f"    [{c['user']['login']}]: {sanitize(c['body'])}"
                         for c in human[-5:]]
                comments_text = "\n  人類留言：\n" + "\n".join(snips)
            if moti_last:
                comments_text += f"\n  moti 上次回應：{sanitize(moti_last['body'], 300)}"

        parts.append(
            f"Issue #{num}「{title}」\n"
            f"  內容：{body}\n"
            f"{comments_text}"
        )

    body = "\n\n".join(parts)
    return _section("【三】本次任務：回應　（不可截斷）", body)


def _layer3_synthesis(repo_root: Path) -> str:
    """Synthesis mode: load STATUS.md task list so moti can execute next step."""
    status = _read(repo_root / "core" / "STATUS.md")
    body = (
        "閱讀已全部完成。現在進入知識綜合階段。\n"
        "請閱讀 STATUS.md 中的任務清單，找出下一個未完成的步驟，並執行。\n\n"
        f"{status}"
    )
    return _section("【三】本次任務：知識綜合　（不可截斷）", body)


def _layer4_knowledge(repo_root: Path, recent_note_paths: list[str]) -> str:
    """Load relevant notes. Priority: read-requests.json > recent_note_paths.
    Truncation-safe (last layer).
    """
    notes = []
    seen = set()

    # Priority 1: files moti explicitly requested last heartbeat
    requested = _load_requested_files(repo_root)
    all_paths = requested + [p for p in recent_note_paths if p not in requested]

    for rel_path in all_paths:
        if rel_path in seen:
            continue
        seen.add(rel_path)
        content = _read(repo_root / rel_path, max_chars=1500)
        if content:
            tag = "（指定讀取）" if rel_path in requested else ""
            notes.append(f"── {rel_path}{tag} ──\n{content}")
        if len(notes) >= 5:  # cap to keep tokens manageable
            break

    # Always include INDEX summary
    index = _read(repo_root / "notes" / "INDEX.md", max_chars=1500)
    if index:
        notes.append(f"── notes/INDEX.md（概念速查）──\n{index}")

    body = "\n\n".join(notes) if notes else "（尚無相關筆記）"
    return _section("【四】知識背景　（可截斷，損失補充資料）", body)


# ── main builder ────────────────────────────────────────────────────────────

def build_newspaper(
    repo_root: Path,
    open_issues: list,
    github_token: str,
    cursor: dict,
    reading_chunk: str,
    reading_context: str,
    recent_log: str,
    recent_note_paths: list[str],
    mode: str,
    pending_issues: list,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"╔{'═'*44}╗\n║  MOTICORE DAILY  {now}  [{mode}]\n╚{'═'*44}╝"

    l1 = _layer1_motive(repo_root)
    l2 = _layer2_status(repo_root, mode, cursor, pending_issues, recent_log)

    if mode == "READING":
        l3 = _layer3_reading(reading_chunk, reading_context)
    elif mode == "RESPONSE":
        l3 = _layer3_response(pending_issues, github_token)
    else:  # SYNTHESIS
        l3 = _layer3_synthesis(repo_root)

    l4 = _layer4_knowledge(repo_root, recent_note_paths)

    return "\n".join([header, l1, l2, l3, l4])
