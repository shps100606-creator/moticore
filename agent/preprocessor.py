"""Newspaper assembler — builds the structured daily report for the main model.

Layer 1: Motivation core (always first, never truncated)
Layer 2: Today's status (code-generated summary, ~200 tokens)
Layer 3: Main task (reading chunk OR issues to respond)
Layer 4: Knowledge background (selected notes, truncation-safe)
"""
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


# ── mode detection ──────────────────────────────────────────────────────────

def detect_mode(open_issues: list, github_token: str) -> tuple[str, list]:
    """Return ('READING'|'RESPONSE', pending_issues).

    RESPONSE mode when any non-progress issue:
      - has never received a moti reply, OR
      - has a new human comment since last moti reply.
    """
    pending = []
    for issue in open_issues:
        num = issue.get("number")
        if num == PROGRESS_ISSUE:
            continue
        if not github_token:
            continue
        comments = get_issue_comments(github_token, num, max_comments=20)
        moti = [c for c in comments if MOTI_BOT_LOGIN in c.get("user", {}).get("login", "")]
        human = [
            c for c in comments
            if c.get("user", {}).get("type") != "Bot"
            and "github-actions" not in c.get("user", {}).get("login", "")
        ]
        if not moti or human:
            pending.append(issue)
    mode = "RESPONSE" if pending else "READING"
    return mode, pending


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
        urgent_lines = []
        for i in pending_issues:
            urgent_lines.append(f"  ⚠️  Issue #{i['number']}「{i.get('title','')[:40]}」")
        urgent = "\n".join(urgent_lines)
    else:
        urgent = "  ✅ 無"

    body = (
        f"時間：{now}\n"
        f"模式：{mode}\n"
        f"閱讀進度：{progress}\n"
        f"\n緊急事項：\n{urgent}\n"
        f"\n最近行動：\n{recent_log}"
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

        # Fetch full comment history
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


def _layer4_knowledge(repo_root: Path, mode: str,
                      recent_note_paths: list[str]) -> str:
    """Load relevant notes full text. Truncation-safe (last layer)."""
    notes = []
    seen = set()
    for rel_path in recent_note_paths:
        if rel_path in seen:
            continue
        seen.add(rel_path)
        content = _read(repo_root / rel_path, max_chars=1200)
        if content:
            notes.append(f"── {rel_path} ──\n{content}")

    # Always include index summary (first 1500 chars)
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
    else:
        l3 = _layer3_response(pending_issues, github_token)

    l4 = _layer4_knowledge(repo_root, mode, recent_note_paths)

    return "\n".join([header, l1, l2, l3, l4])
