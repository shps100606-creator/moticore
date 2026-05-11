"""Load motivation core and long-term memory into context."""
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_core(repo_root: Path) -> dict:
    return {key: _read(repo_root / rel) for key, rel in CORE_FILES.items()}


def load_notes_index(repo_root: Path) -> str:
    """Load the agent's own knowledge map."""
    return _read(repo_root / "notes" / "INDEX.md") or "（尚無筆記目錄）"


def load_recent_notes(repo_root: Path, n: int = 3) -> str:
    """Load the n most recently modified note files."""
    notes_root = repo_root / "notes"
    if not notes_root.exists():
        return "（尚無筆記）"

    md_files = [f for f in notes_root.rglob("*.md") if f.name != "INDEX.md"]
    if not md_files:
        return "（尚無筆記）"

    recent = sorted(md_files, key=lambda f: f.stat().st_mtime, reverse=True)[:n]
    parts = []
    for f in recent:
        rel = f.relative_to(repo_root)
        content = _read(f)[:1000]  # cap each file at 1000 chars
        parts.append(f"### {rel}\n{content}")
    return "\n\n".join(parts)
