"""Load motivation core document."""
from pathlib import Path


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_motive(repo_root: Path) -> str:
    """Load core/MOTIVE.md — used as system instruction for the consciousness module."""
    return _read(repo_root / "core" / "MOTIVE.md")
