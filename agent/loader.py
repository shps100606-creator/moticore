"""Load motivation core documents from the repo into a dict."""
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


def load_core(repo_root: Path) -> dict:
    """Read all core documents; return empty string if file is missing."""
    result = {}
    for key, rel_path in CORE_FILES.items():
        p = repo_root / rel_path
        result[key] = p.read_text(encoding="utf-8") if p.exists() else ""
    return result
