"""Load motivation core and memory into context."""
import json
from pathlib import Path

CORE_FILES = {
    "identity": "core/identity.md",
    "prime_motive": "core/prime-motive.md",
    "value_hierarchy": "core/value-hierarchy.md",
    "constitution": "core/constitution.md",
    "forbidden": "core/forbidden.md",
    "boundary": "core/boundary.md",
    "task_inbox": "core/task-inbox.md",
    "deviation_log": "core/deviation-log.md",
}


def _read(path: Path, max_chars: int = 0) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] if max_chars else text


def load_core(repo_root: Path) -> dict:
    return {key: _read(repo_root / rel) for key, rel in CORE_FILES.items()}


def load_system_manifest(repo_root: Path) -> str:
    """Load SYSTEM.md — the agent's self-maintained system directory."""
    return _read(repo_root / "memory" / "SYSTEM.md", max_chars=2000) or "(尚無系統目錄，請建立 memory/SYSTEM.md)"


def load_requested_files(repo_root: Path) -> str:
    """Load files the agent requested last heartbeat via memory/read-requests.json."""
    req_path = repo_root / "memory" / "read-requests.json"
    if not req_path.exists():
        return ""

    try:
        requests = json.loads(req_path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    if not isinstance(requests, list):
        return ""

    parts = []
    for entry in requests[:8]:  # max 8 files per heartbeat
        path_str = entry if isinstance(entry, str) else entry.get("path", "")
        if not path_str:
            continue
        file_path = repo_root / path_str
        content = _read(file_path, max_chars=1500)
        if content:
            parts.append(f"### {path_str}\n{content}")
        else:
            parts.append(f"### {path_str}\n(檔案不存在或為空)")

    return "\n\n".join(parts) if parts else ""


# kept for backward compat, still usable by agent as fallback
def load_notes_index(repo_root: Path) -> str:
    return _read(repo_root / "notes" / "INDEX.md") or "(尚無筆記目錄)"
