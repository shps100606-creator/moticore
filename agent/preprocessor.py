"""Newspaper assembler — builds the structured daily report for the main model.

Layer 1: Motivation core (always first, never truncated)
Layer 2: Today's status (code-generated summary, ~200 tokens)
Layer 3: Main task (reading chunk OR issues to respond OR synthesis task)
Layer 4: Knowledge background (selected notes + requested dialogues, truncation-safe)
"""
import json
import requests as _requests
from datetime import datetime, timezone
from pathlib import Path
from issues import PROGRESS_ISSUE, MOTI_BOT_LOGIN, get_issue_comments

PRIMA_OWNER = "shps100606-creator"
PRIMA_REPO = "prima-materia"
DIALOGUES_PATH = "dialogues"


# ── helpers ────────────────────────────────────────────────────────────────

def _read(path: Path, max_chars: int = 0) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] if max_chars else text


def _section(title: str, body: str) -> str:
    bar = "━" * 44
    return f"\n{bar}\n{title}\n{bar}\n{body}\n"


def _load_requested_files(repo_root: Path, dialogues_token: str = "") -> tuple[list[str], list[str]]:
    """Returns (note_paths, dialogue_filenames) from memory/read-requests.json.

    Supports two formats:
      Legacy: ["notes/foo.md", ...]  → all treated as note paths
      New:    {"notes": [...], "dialogues": ["12-xxx.md", ...]}
    """
    req_path = repo_root / "memory" / "read-requests.json"
    if not req_path.exists():
        return [], []
    try:
        data = json.loads(req_path.read_text(encoding="utf-8"))
    except Exception:
        return [], []

    if isinstance(data, list):
        return [p for p in data if isinstance(p, str)], []
    if isinstance(data, dict):
        notes = [p for p in data.get("notes", []) if isinstance(p, str)]
        dialogues = [f for f in data.get("dialogues", []) if isinstance(f, str)]
        return notes, dialogues
    return [], []


def _fetch_dialogue(token: str, filename: str, max_chars: int = 3000) -> str:
    """Fetch a single dialogue file from prima-materia via GitHub API."""
    try:
        resp = _requests.get(
            f"https://api.github.com/repos/{PRIMA_OWNER}/{PRIMA_REPO}/contents/{DIALOGUES_PATH}/{filename}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.raw+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.text[:max_chars]
    except Exception as e:
        return f"（無法載入：{e}）"


# ── mode detection ──────────────────────────────────────────────────────────

def detect_mode(open_issues: list, github_token: str, cursor: dict | None = None) -> tuple[str, list]:
    """Return ('READING'|'RESPONSE'|'SYNTHESIS', pending_issues).

    RESPONSE mode when any non-progress issue has:
      - never received a moti reply, OR
      - a human comment NEWER than moti's last reply.

    SYNTHESIS mode when reading is finished and no pending issues.
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
            pending.append(issue)
            continue

        last_moti_time = max(c["created_at"] for c in moti)
        new_human = [c for c in human if c.get("created_at", "") > last_moti_time]
        if new_human:
            pending.append(issue)

    if pending:
        return "RESPONSE", pending

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

    if pending_issues:
        urgent_lines = [f"  ⚠️  Issue #{i['number']}「{i.get('title','')[:40]}」"
                        for i in pending_issues]
        urgent = "\n".join(urgent_lines)
    else:
        urgent = "  ✅ 無"

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
    status = _read(repo_root / "core" / "STATUS.md")
    body = (
        "閱讀已全部完成。現在進入知識綜合階段。\n"
        "請閱讀 STATUS.md 中的任務清單，找出下一個未完成的步驟，並執行。\n"
        "若筆記不夠詳細，可在 §READ_REQUEST 中請求原文。\n\n"
        f"{status}"
    )
    return _section("【三】本次任務：知識綜合　（不可截斷）", body)


def _layer4_knowledge(repo_root: Path, recent_note_paths: list[str],
                      dialogues_token: str = "") -> str:
    """Load relevant notes and any requested dialogue files."""
    notes = []
    seen = set()

    requested_notes, requested_dialogues = _load_requested_files(repo_root, dialogues_token)
    all_note_paths = requested_notes + [p for p in recent_note_paths if p not in requested_notes]

    for rel_path in all_note_paths:
        if rel_path in seen:
            continue
        seen.add(rel_path)
        content = _read(repo_root / rel_path, max_chars=1500)
        if content:
            tag = "（指定讀取）" if rel_path in requested_notes else ""
            notes.append(f"── {rel_path}{tag} ──\n{content}")
        if len(notes) >= 5:
            break

    # Fetch requested dialogue files from prima-materia
    if requested_dialogues and dialogues_token:
        for filename in requested_dialogues[:2]:  # cap at 2 to protect token budget
            content = _fetch_dialogue(dialogues_token, filename, max_chars=3000)
            notes.append(f"── 《{filename}》【原文參考】 ──\n{content}")

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
    dialogues_token: str = "",
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

    l4 = _layer4_knowledge(repo_root, recent_note_paths, dialogues_token)

    return "\n".join([header, l1, l2, l3, l4])
