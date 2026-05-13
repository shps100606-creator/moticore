"""Pure-code pre-processing module.

Formats all context data (history, issues, status, requested files)
into a clean structured report for the consciousness module.
No AI calls — only data formatting.
"""
import json
import re
from datetime import datetime
from pathlib import Path


def _read(path: Path, max_chars: int = 0) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] if max_chars else text


def _load_recent_actions(repo_root: Path, n: int = 5) -> str:
    log_path = repo_root / "memory" / "action-log.md"
    if not log_path.exists():
        return "(尚無記錄)"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-(n * 6):] if len(lines) > n * 6 else lines
    return "\n".join(recent) or "(尚無記錄)"


def _load_requested_files(repo_root: Path) -> str:
    req_path = repo_root / "memory" / "read-requests.json"
    if not req_path.exists():
        return ""
    try:
        paths = json.loads(req_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    if not isinstance(paths, list):
        return ""
    parts = []
    for entry in paths[:5]:
        path_str = entry if isinstance(entry, str) else entry.get("path", "")
        if not path_str:
            continue
        content = _read(repo_root / path_str, max_chars=1000)
        label = content if content else "(不存在或為空)"
        parts.append(f"### {path_str}\n{label}")
    return "\n\n".join(parts)


def build_report(
    repo_root: Path,
    open_issues: list,
    github_token: str,
    cursor: dict,
    format_issues_fn,
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sections = [f"=== 前置報告 {now} ==="]

    # 閱讀進度
    if cursor:
        file_idx = cursor.get("file_index", 0) + 1
        char_off = cursor.get("char_offset", 0)
        finished = cursor.get("finished", False)
        if finished:
            progress = "全部讀完"
        else:
            progress = f"第 {file_idx}/29 篇，下次從第 {char_off:,} 字繼續"
        sections.append(f"[閱讀進度]\n{progress}")

    # 狀態核（任務 + 偏離記錄）
    status = _read(repo_root / "core" / "STATUS.md")
    if status:
        sections.append(f"[狀態核]\n{status}")

    # 系統目錄
    system_md = _read(repo_root / "memory" / "SYSTEM.md", max_chars=1000)
    if system_md:
        sections.append(f"[系統目錄]\n{system_md}")

    # 近期行動
    recent = _load_recent_actions(repo_root, n=5)
    sections.append(f"[近期行動（最近5次）]\n{recent}")

    # Issues
    issues_text = format_issues_fn(open_issues, token=github_token)
    sections.append(f"[待處理 Issues]\n{issues_text}")

    # 上次請求閱讀的檔案
    requested = _load_requested_files(repo_root)
    if requested:
        sections.append(f"[上次請求閱讀的檔案]\n{requested}")

    return "\n\n".join(sections)
