"""Read and append to the agent action log."""
from pathlib import Path
from datetime import datetime
import json

ACTION_LOG = "memory/action-log.md"


def get_recent_actions(repo_root: Path, n: int = 10) -> str:
    """Return the last n log entries as plain text."""
    log_path = repo_root / ACTION_LOG
    if not log_path.exists():
        return "（尚無行動記錄）"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-(n * 6):] if len(lines) > n * 6 else lines
    return "\n".join(recent) or "（尚無行動記錄）"


def append_action(repo_root: Path, decision: dict) -> None:
    """Append a decision entry to the action log."""
    log_path = repo_root / ACTION_LOG
    log_path.parent.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = (
        f"\n### {ts}\n"
        f"- **action_type**: {decision.get('action_type', 'unknown')}\n"
        f"- **summary**: {decision.get('summary', '')}\n"
        f"- **result**: {decision.get('result', '')}\n"
        f"- **deviation_flag**: {decision.get('deviation_flag', '無')}\n"
    )
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)
