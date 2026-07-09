"""Newspaper assembler — builds the structured daily report for the main model.

Layer 1: Motivation core (always first, never truncated)
Layer 2: Today's status (code-generated summary, ~200 tokens)
Layer 3: Main task (reading chunk OR issues to respond OR synthesis task)
Layer 4: Knowledge background (selected notes + requested dialogues, truncation-safe)
"""
import json
import re
import requests as _requests
from datetime import datetime, timezone
from pathlib import Path
from issues import PROGRESS_ISSUE, MOTI_BOT_LOGIN, get_issue_comments

PRIMA_OWNER = "shps100606-creator"
PRIMA_REPO = "prima-materia"
DIALOGUES_PATH = "dialogues"


# ── helpers ──────────────────────────────────────────────────────────────────

def _read(path: Path, max_chars: int = 0) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] if max_chars else text


def _section(title: str, body: str) -> str:
    bar = "━" * 44
    return f"\n{bar}\n{title}\n{bar}\n{body}\n"


def _build_file_tree(repo_root: Path) -> str:
    """Scan key directories and return a compact file listing for path verification."""
    lines = []
    for dir_name in ["docs", "notes", "memory", "core"]:
        dir_path = repo_root / dir_name
        if not dir_path.exists():
            continue
        files = sorted([f.name for f in dir_path.iterdir() if f.is_file()])
        if files:
            lines.append(f"{dir_name}/")
            for f in files:
                lines.append(f"  {dir_name}/{f}")
    return "\n".join(lines)


def _parse_recent_summaries(repo_root: Path, n: int = 5) -> list[str]:
    """Parse the last n summary values from memory/action-log.md."""
    log_path = repo_root / "memory" / "action-log.md"
    if not log_path.exists():
        return []
    try:
        text = log_path.read_text(encoding="utf-8")
    except Exception:
        return []
    summaries = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **summary**:"):
            value = stripped[len("- **summary**:"):].strip()
            summaries.append(value)
    return summaries[-n:]


def _parse_recent_poles(repo_root: Path, n: int = 15) -> list[str]:
    """Parse the last n pole values from memory/action-log.md."""
    log_path = repo_root / "memory" / "action-log.md"
    if not log_path.exists():
        return []
    try:
        text = log_path.read_text(encoding="utf-8")
    except Exception:
        return []
    poles = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **pole**:"):
            value = stripped[len("- **pole**:"):].strip()
            poles.append(value)
    return poles[-n:]


def _count_streak(poles: list[str], target: str) -> int:
    """Count trailing consecutive occurrences of target from end of list."""
    count = 0
    for p in reversed(poles):
        if p == target:
            count += 1
        else:
            break
    return count


def _load_horizon(repo_root: Path, max_chars: int = 800) -> str:
    """Load HORIZON.md open questions for injection into L2."""
    horizon_path = repo_root / "core" / "HORIZON.md"
    if not horizon_path.exists():
        return ""
    content = horizon_path.read_text(encoding="utf-8")[:max_chars]
    return f"\n\n【HORIZON.md 開放問題】:\n{content}"


def _count_horizon_open(repo_root: Path) -> int:
    """Count how many '### ' questions currently sit under HORIZON.md's
    '## 開放中' section, so the synthesis prompt can discourage unbounded
    growth of the open-question list."""
    horizon_path = repo_root / "core" / "HORIZON.md"
    if not horizon_path.exists():
        return 0
    text = horizon_path.read_text(encoding="utf-8")
    m = re.search(r"## 開放中\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if not m:
        return 0
    return len(re.findall(r"^### ", m.group(1), re.MULTILINE))


def _fetch_url(url: str, max_chars: int = 3000) -> str:
    """Fetch external URL content via GET. Only https:// allowed."""
    try:
        resp = _requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "moticore-agent/1.0"},
        )
        resp.raise_for_status()
        return resp.text[:max_chars]
    except Exception as e:
        return f"（無法讀取 {url}：{e}）"


def _fetch_analytics(token: str, project_id: str) -> str:
    """Fetch Vercel Analytics summary for the last 7 days."""
    if not token or not project_id:
        return ""
    try:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        week_ago_ms = now_ms - 7 * 24 * 3600 * 1000
        resp = _requests.get(
            "https://vercel.com/api/web/insights/stats",
            headers={"Authorization": f"Bearer {token}"},
            params={"projectId": project_id, "from": week_ago_ms, "to": now_ms},
            timeout=15,
        )
        if resp.status_code == 403:
            return "（Analytics 不可用：需確認 Vercel 方案）"
        resp.raise_for_status()
        data = resp.json()
        visitors_raw = data.get("visitors", {})
        visitors = visitors_raw.get("value", visitors_raw) if isinstance(visitors_raw, dict) else visitors_raw
        pageviews_raw = data.get("pageviews", {})
        pageviews = pageviews_raw.get("value", pageviews_raw) if isinstance(pageviews_raw, dict) else pageviews_raw
        lines = [f"訪客（7天）：{visitors}", f"頁面瀏覽（7天）：{pageviews}"]
        top = (data.get("topPaths") or data.get("paths") or [])[:3]
        if top:
            top_str = "、".join(str(p.get("path", p.get("url", "?"))) for p in top)
            lines.append(f"熱門頁面：{top_str}")
        return "\n".join(lines)
    except Exception:
        return "（Analytics 不可用）"


def _load_requested_files(repo_root: Path,
                          dialogues_token: str = "") -> tuple[list[str], list[str], list[str]]:
    """Returns (note_paths, dialogue_filenames, urls) from memory/read-requests.json."""
    req_path = repo_root / "memory" / "read-requests.json"
    if not req_path.exists():
        return [], [], []
    try:
        data = json.loads(req_path.read_text(encoding="utf-8"))
    except Exception:
        return [], [], []

    if isinstance(data, list):
        return [p for p in data if isinstance(p, str)], [], []
    if isinstance(data, dict):
        notes = [p for p in data.get("notes", []) if isinstance(p, str)]
        dialogues = [f for f in data.get("dialogues", []) if isinstance(f, str)]
        urls = [
            u for u in data.get("urls", [])
            if isinstance(u, str) and u.startswith("https://")
        ]
        return notes, dialogues, urls
    return [], [], []


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


# ── mode detection ──────────────────────────────────────────────

def detect_mode(open_issues: list, github_token: str,
               cursor: dict | None = None) -> tuple[str, list]:
    """Return ('READING'|'RESPONSE'|'SYNTHESIS', pending_issues)."""
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


# ── layer builders ──────────────────────────────────────────────────────

def _layer1_motive(repo_root: Path) -> str:
    motive = _read(repo_root / "core" / "MOTIVE.md")
    return _section("【一】動機核　　（永遠完整，不可截斷）", motive)


def _layer2_status(repo_root: Path, mode: str, cursor: dict,
                   pending_issues: list, recent_log: str,
                   analytics_token: str = "",
                   analytics_project_id: str = "",
                   journal_note: str = "",
                   giscus_note: str = "") -> str:
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

    status = _read(repo_root / "docs" / "STATUS.md", max_chars=600)
    file_tree = _build_file_tree(repo_root)

    body = (
        f"時間：{now}\n"
        f"模式：{mode}\n"
        f"閱讀進度：{progress}\n"
        f"\n緊急事項：\n{urgent}\n"
        f"\n最近行動：\n{recent_log}\n"
        f"\n當前任務（STATUS.md）：\n{status}\n"
        f"\n【文件樹】寫 read_request 路徑前必須對照此列表，禁止使用未出現的路徑：\n{file_tree}"
    )

    if journal_note:
        body += f"\n\n{journal_note}"

    if giscus_note:
        body += f"\n\n{giscus_note}"

    if analytics_token and analytics_project_id:
        analytics = _fetch_analytics(analytics_token, analytics_project_id)
        if analytics:
            body += f"\n\nVercel Analytics（最近7天）：\n{analytics}"

    # 極性平衡偵測（取代舊迴圈偵測）
    poles = _parse_recent_poles(repo_root, n=15)
    if poles:
        motivation_streak = _count_streak(poles, "motivation")
        curiosity_streak = _count_streak(poles, "curiosity")
        if motivation_streak >= 5:
            body += (
                f"\n\n⚡ 極性平衡提醒（動機極連續主導 {motivation_streak} 次）\n"
                "好奇極長時間未激活。請閱讀 HORIZON.md，找出一個値得探索的開放問題，"
                "並以好奇極（pole: curiosity）為主導採取行動。"
            )
            body += _load_horizon(repo_root)
        elif curiosity_streak >= 8:
            body += (
                f"\n\n⚡ 極性平衡提醒（好奇極連續主導 {curiosity_streak} 次）\n"
                "HORIZON.md 的沈澱候選區是否有洞察已足夠成熟，"
                "可以結晶為動機核的一部分（pole: crystallize）？"
            )
    else:
        # 兼容模式：pole 欄位尚未建立，使用升級版迴圈偵測
        summaries = _parse_recent_summaries(repo_root, n=15)
        non_empty = [s for s in summaries if s]
        if non_empty:
            normalized = [re.sub(r'[\s　，。！？、]+', '', s) for s in non_empty]
            if normalized:
                most_common = max(set(normalized), key=normalized.count)
                count = normalized.count(most_common)
                if count >= 3:
                    body += (
                        f"\n\n⚠️ 迴圈偵測警告（最近 {len(summaries)} 次心跳中 {count} 次行動相似）\n"
                        "請評估：你是否陷入重複行為？請主動改變行動方向。"
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
    status = _read(repo_root / "docs" / "STATUS.md")

    # 若 STATUS 無待辦 + HORIZON 有開放問題 → 導引探索
    horizon_path = repo_root / "core" / "HORIZON.md"
    horizon_content = ""
    if horizon_path.exists():
        horizon_content = horizon_path.read_text(encoding="utf-8")[:1200]

    has_pending = any(
        keyword in status
        for keyword in ["待辦", "[ ]", "未完成", "TODO"]
    )
    has_horizon = bool(horizon_content.strip())

    if not has_pending and has_horizon:
        open_count = _count_horizon_open(repo_root)
        if open_count >= 5:
            lifecycle_note = (
                f"\n\n「開放中」目前有 {open_count} 個問題，數量已經偏多。這次請優先從中選一個做"
                " pole: crystallize（想清楚了，寫 §FILE core/HORIZON.md 把它從「開放中」整段搬到"
                "「已結晶」）或 pole: dissolve（把 MOTIVE.md 裡某個變僵化的信念重新開放成問題），"
                "暫時不要再新增。"
            )
        else:
            lifecycle_note = (
                "\n\n若探索時發現清單外的新困惑，可以直接用 §FILE core/HORIZON.md 把它加進"
                "「開放中」，不必侷限於既有問題。"
            )
        body = (
            "閱讀已全部完成，STATUS.md 目前無待辦任務。\n"
            "你的 HORIZON.md 有以下開放問題，請選擇其中一個進行探索，"
            "以好奇極（pole: curiosity）為主導採取行動，而非更新 STATUS.md。"
            f"{lifecycle_note}\n\n"
            f"{horizon_content}"
        )
    else:
        body = (
            "閱讀已全部完成。現在進入知識綜合階段。\n"
            "請閱讀 STATUS.md 中的任務清單，找出下一個未完成的步驟，並執行。\n"
            "若筆記不夠詳細，可在 §READ_REQUEST 中請求原文。\n\n"
            f"{status}"
        )

    return _section("【三】本次任務：知識綜合　（不可截斷）", body)


def _layer4_knowledge(repo_root: Path, recent_note_paths: list[str],
                      dialogues_token: str = "") -> str:
    """Load relevant notes, requested dialogue files, and external URLs."""
    notes = []
    seen = set()

    requested_notes, requested_dialogues, requested_urls = _load_requested_files(
        repo_root, dialogues_token
    )
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

    if requested_dialogues and dialogues_token:
        for filename in requested_dialogues[:2]:
            content = _fetch_dialogue(dialogues_token, filename, max_chars=3000)
            notes.append(f"── 《{filename}》【原文參考】 ──\n{content}")

    for url in requested_urls[:2]:
        content = _fetch_url(url)
        notes.append(f"── 外部 URL：{url} ──\n{content}")

    index = _read(repo_root / "notes" / "INDEX.md", max_chars=1500)
    if index:
        notes.append(f"── notes/INDEX.md（概念速查）──\n{index}")

    body = "\n\n".join(notes) if notes else "（尚無相關筆記）"
    return _section("【四】知識背景　（可截斷，損失補充資料）", body)


# ── main builder ──────────────────────────────────────────────────────

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
    analytics_token: str = "",
    analytics_project_id: str = "",
    journal_note: str = "",
    giscus_note: str = "",
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"╔{'═'*44}╗\n║  MOTICORE DAILY  {now}  [{mode}]\n╚{'═'*44}╝"

    l1 = _layer1_motive(repo_root)
    l2 = _layer2_status(repo_root, mode, cursor, pending_issues, recent_log,
                        analytics_token=analytics_token,
                        analytics_project_id=analytics_project_id,
                        journal_note=journal_note,
                        giscus_note=giscus_note)

    if mode == "READING":
        l3 = _layer3_reading(reading_chunk, reading_context)
    elif mode == "RESPONSE":
        l3 = _layer3_response(pending_issues, github_token)
    else:  # SYNTHESIS
        l3 = _layer3_synthesis(repo_root)

    l4 = _layer4_knowledge(repo_root, recent_note_paths, dialogues_token)

    return "\n".join([header, l1, l2, l3, l4])
