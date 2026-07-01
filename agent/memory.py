"""Read and append to the agent action log."""
from pathlib import Path
from datetime import datetime

ACTION_LOG = "memory/action-log.md"


def get_recent_actions(repo_root: Path, n: int = 5) -> list[dict]:
    """Return last n parsed log entries as list of dicts."""
    log_path = repo_root / ACTION_LOG
    if not log_path.exists():
        return []
    text = log_path.read_text(encoding="utf-8")
    entries = []
    for block in text.strip().split("\n### "):
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        entry = {"timestamp": "", "action_type": "", "summary": "",
                 "result": "", "deviation_flag": "無", "files": [], "mode": "",
                 "pole": "motivation"}
        for line in lines:
            if line.startswith("20"):           # timestamp is first line
                entry["timestamp"] = line[:19]
            for key in ("action_type", "summary", "result", "deviation_flag",
                        "files", "mode", "pole"):
                prefix = f"- **{key}**:"
                if line.startswith(prefix):
                    val = line[len(prefix):].strip()
                    if key == "files":
                        entry["files"] = [p.strip() for p in val.split(",") if p.strip()]
                    else:
                        entry[key] = val
        entries.append(entry)
    return entries[-n:]


def format_recent_for_report(repo_root: Path, n: int = 3) -> str:
    """Format last n entries as compact newspaper lines."""
    entries = get_recent_actions(repo_root, n)
    if not entries:
        return "  （尚無記錄）"
    lines = []
    for e in entries:
        files_str = f" → {', '.join(e['files'])}" if e["files"] else ""
        pole_str = f" [{e.get('pole', '?')}]" if e.get('pole') else ""
        dev = e.get('deviation_flag', '無')
        dev_str = f" ⚠️{dev}" if dev and dev != "無" else ""
        lines.append(f"  {{{e['timestamp']}}} [{e['action_type']}]{pole_str} {e['summary']}{files_str}{dev_str}")
    return "\n".join(lines)


def get_recent_note_paths(repo_root: Path, n: int = 5) -> list[str]:
    """Return file paths from the last n reading entries (for Mode B context)."""
    entries = get_recent_actions(repo_root, 20)
    paths = []
    for e in reversed(entries):
        if e["action_type"] in ("reading",):
            for f in e["files"]:
                if f.startswith("notes/") and f not in paths:
                    paths.append(f)
        if len(paths) >= n:
            break
    return paths


def _truncate_action_log_if_needed(log_path: Path, keep: int = 100,
                                   archive_threshold: int = 200) -> None:
    """If log exceeds archive_threshold entries, archive oldest to dated file."""
    if not log_path.exists():
        return
    text = log_path.read_text(encoding="utf-8")
    raw_blocks = text.strip().split("\n### ")
    blocks = [b for b in raw_blocks if b.strip()]
    if len(blocks) <= archive_threshold:
        return

    archive_count = len(blocks) - keep
    to_archive = blocks[:archive_count]
    to_keep = blocks[archive_count:]

    archive_month = datetime.utcnow().strftime("%Y%m")
    archive_path = log_path.parent / f"action-log-archive-{archive_month}.md"
    header = f"# action-log 封存 {archive_month}\n（共 {archive_count} 筆）\n"
    if archive_path.exists():
        with archive_path.open("a", encoding="utf-8") as f:
            f.write("\n### " + "\n### ".join(to_archive))
    else:
        archive_path.write_text(header + "\n### ".join(to_archive), encoding="utf-8")

    log_path.write_text("\n### ".join(to_keep), encoding="utf-8")
    print(f"[memory] action-log truncated: archived {archive_count}, kept {keep}")


def append_action(repo_root: Path, decision: dict, mode: str = "",
                  file_writes: list = None) -> None:
    """Append a decision entry to the action log."""
    log_path = repo_root / ACTION_LOG
    log_path.parent.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    files = []
    if file_writes:
        files = [fw.get("path", "") for fw in file_writes if fw.get("path")]

    files_str = ", ".join(files) if files else "（無）"
    pole = decision.get("pole", "motivation")

    # `decision` comes straight from decision.py's §ACTION parser, whose keys
    # are the field names the model actually writes: "type" and "deviation"
    # (not "action_type" / "deviation_flag" — those are only the log's
    # on-disk field labels below).
    entry = (
        f"\n### {ts}\n"
        f"- **action_type**: {decision.get('type', 'unknown')}\n"
        f"- **mode**: {mode}\n"
        f"- **pole**: {pole}\n"
        f"- **summary**: {decision.get('summary', '')}\n"
        f"- **files**: {files_str}\n"
        f"- **result**: {decision.get('result', '')}\n"
        f"- **deviation_flag**: {decision.get('deviation', '無')}\n"
    )
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)

    _truncate_action_log_if_needed(log_path)
