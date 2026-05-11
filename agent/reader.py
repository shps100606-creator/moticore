"""Read and parse ChatGPT export JSON from prima-materia repo.

Handles cursor tracking so each heartbeat reads the next chunk.
"""
import json
import os
import requests
from pathlib import Path

PRIMA_MATERIA_OWNER = "shps100606-creator"
PRIMA_MATERIA_REPO = "prima-materia"
DIALOGUES_PATH = "dialogues/conversations.json"
CHUNK_SIZE = 25  # exchanges per heartbeat


def _fetch_raw_json(token: str) -> list:
    """Fetch conversations.json from prima-materia via GitHub API."""
    url = f"https://api.github.com/repos/{PRIMA_MATERIA_OWNER}/{PRIMA_MATERIA_REPO}/contents/{DIALOGUES_PATH}"
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.raw+json",
        },
    )
    resp.raise_for_status()
    return resp.json()


def _extract_messages(conversation: dict) -> list:
    """Extract ordered messages from a single ChatGPT conversation object."""
    mapping = conversation.get("mapping", {})
    messages = []
    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue
        role = msg.get("author", {}).get("role", "")
        if role not in ("user", "assistant"):
            continue
        parts = msg.get("content", {}).get("parts", [])
        text = " ".join(p for p in parts if isinstance(p, str)).strip()
        if not text:
            continue
        create_time = msg.get("create_time") or 0
        messages.append({"role": role, "text": text, "time": create_time})
    messages.sort(key=lambda m: m["time"])
    return messages


def load_cursor(repo_root: Path) -> dict:
    cursor_path = repo_root / "memory" / "reading-cursor.json"
    if cursor_path.exists():
        return json.loads(cursor_path.read_text(encoding="utf-8"))
    return {"conversation_index": 0, "message_offset": 0, "total_conversations": 0, "finished": False}


def save_cursor(repo_root: Path, cursor: dict) -> None:
    cursor_path = repo_root / "memory" / "reading-cursor.json"
    cursor_path.parent.mkdir(exist_ok=True)
    cursor_path.write_text(json.dumps(cursor, ensure_ascii=False, indent=2), encoding="utf-8")


def get_next_chunk(token: str, repo_root: Path) -> dict:
    """Return the next chunk of dialogue and an updated cursor.

    Returns:
        {
            "chunk_text": str,       # formatted dialogue for the prompt
            "conversation_title": str,
            "cursor": dict,          # updated cursor (not yet saved)
            "finished": bool,        # True if all conversations exhausted
        }
    """
    conversations = _fetch_raw_json(token)
    cursor = load_cursor(repo_root)
    cursor["total_conversations"] = len(conversations)

    if cursor.get("finished") or cursor["conversation_index"] >= len(conversations):
        return {"chunk_text": "", "conversation_title": "", "cursor": cursor, "finished": True}

    conv = conversations[cursor["conversation_index"]]
    title = conv.get("title", f"對話 #{cursor['conversation_index'] + 1}")
    messages = _extract_messages(conv)

    offset = cursor["message_offset"]
    chunk = messages[offset: offset + CHUNK_SIZE]

    lines = [f"# {title}\n"]
    for m in chunk:
        speaker = "**你**" if m["role"] == "user" else "**GPT**"
        lines.append(f"{speaker}：{m['text']}\n")
    chunk_text = "\n".join(lines)

    new_offset = offset + len(chunk)
    if new_offset >= len(messages):
        # Move to next conversation
        cursor["conversation_index"] += 1
        cursor["message_offset"] = 0
        if cursor["conversation_index"] >= len(conversations):
            cursor["finished"] = True
    else:
        cursor["message_offset"] = new_offset

    return {
        "chunk_text": chunk_text,
        "conversation_title": title,
        "cursor": cursor,
        "finished": cursor.get("finished", False),
    }
