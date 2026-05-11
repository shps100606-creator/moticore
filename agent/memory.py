"""Read and append entries to memory/action-log.md."""
from datetime import datetime
from pathlib import Path


LOG_PATH = "memory/action-log.md"


def get_recent_actions(repo_root: Path, n: int = 10) -> str:
    """Return the last n action entries from the log (raw text)."""
    path = repo_root / LOG_PATH
    if not path.exists():
        return "（無行動記錄）"
    text = path.read_text(encoding="utf-8")
    # Split on entry separators
    entries = [e.strip() for e in text.split("---") if e.strip()]
    recent = entries[-n:] if len(entries) > n else entries
    return "\n\n---\n\n".join(recent)


def append_action(repo_root: Path, entry: dict) -> None:
    """Append a new action entry to the log."""
    path = repo_root / LOG_PATH
    today = datetime.utcnow().strftime("%Y%m%d")

    # Count existing entries to assign sequence number
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    seq = existing.count("ID: ACT-") + 1

    entry_id = f"ACT-{today}-{seq:03d}"
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    block = f"""
---
ID: {entry_id}  
時間: {date_str}  
類型: {entry.get('action_type', '?')}  
摘要: {entry.get('summary', '')}  
主動機關連: {entry.get('motive_alignment', '')}  
執行理由: {entry.get('execution_reasoning', '')}  
風險評估: {entry.get('risk_assessment', '無')}  
偏離標記: {entry.get('deviation_flag', '無')}  
結果: {entry.get('result', '完成')}  
後續觸發: {entry.get('followup', '無')}  
"""

    with path.open("a", encoding="utf-8") as f:
        f.write(block)
