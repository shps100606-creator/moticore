"""Read 動機論 markdown files from prima-materia repo sequentially.

Each heartbeat reads up to CHUNK_CHARS from the current file.
When a file is finished, moves to the next one.
"""
import json
import requests
from pathlib import Path

PRIMA_OWNER = "shps100606-creator"
PRIMA_REPO = "prima-materia"
DIALOGUES_PATH = "dialogues"
CHUNK_CHARS = 20000

CHINESE_ORDER = [
    "第一", "第二", "第三", "第四", "第五", "第六", "第七", "第八", "第九",
    "第十", "第十一", "第十二", "第十三", "第十四", "第十五",
    "第十六", "第十七", "第十八", "第十九",
    "第二十", "第二十一", "第二十二", "第二十三", "第二十四", "第二十五",
    "第二十六", "第二十七", "第二十八", "第二十九",
]


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _list_md_files(token: str) -> list:
    resp = requests.get(
        f"https://api.github.com/repos/{PRIMA_OWNER}/{PRIMA_REPO}/contents/{DIALOGUES_PATH}",
        headers=_headers(token),
    )
    resp.raise_for_status()
    files = [f["name"] for f in resp.json() if f["name"].endswith(".md")]

    def sort_key(name):
        for i, num in enumerate(CHINESE_ORDER):
            if num in name:
                return i
        return 999

    return sorted(files, key=sort_key)


def _fetch_file(token: str, filename: str) -> str:
    resp = requests.get(
        f"https://api.github.com/repos/{PRIMA_OWNER}/{PRIMA_REPO}/contents/{DIALOGUES_PATH}/{filename}",
        headers={**_headers(token), "Accept": "application/vnd.github.raw+json"},
    )
    resp.raise_for_status()
    return resp.text


def load_cursor(repo_root: Path) -> dict:
    cursor_path = repo_root / "memory" / "reading-cursor.json"
    if cursor_path.exists():
        return json.loads(cursor_path.read_text(encoding="utf-8"))
    return {"file_index": 0, "char_offset": 0, "finished": False}


def save_cursor(repo_root: Path, cursor: dict) -> None:
    cursor_path = repo_root / "memory" / "reading-cursor.json"
    cursor_path.parent.mkdir(exist_ok=True)
    cursor_path.write_text(json.dumps(cursor, ensure_ascii=False, indent=2), encoding="utf-8")


def get_next_chunk(token: str, repo_root: Path) -> dict:
    cursor = load_cursor(repo_root)

    if cursor.get("finished"):
        return {"chunk_text": "", "conversation_title": "", "cursor": cursor, "finished": True}

    files = _list_md_files(token)
    if not files or cursor["file_index"] >= len(files):
        cursor["finished"] = True
        return {"chunk_text": "", "conversation_title": "", "cursor": cursor, "finished": True}

    filename = files[cursor["file_index"]]
    content = _fetch_file(token, filename)
    offset = cursor["char_offset"]
    chunk = content[offset: offset + CHUNK_CHARS]

    new_offset = offset + len(chunk)
    if new_offset >= len(content):
        # Finished this file, move to next
        cursor["file_index"] += 1
        cursor["char_offset"] = 0
        if cursor["file_index"] >= len(files):
            cursor["finished"] = True
    else:
        cursor["char_offset"] = new_offset

    title = filename.replace(".md", "")
    progress = f"{cursor['file_index']+1 if not cursor.get('finished') else len(files)}/{len(files)}"
    print(f"[reader] {title} offset={offset} chunk={len(chunk)} files={progress}")

    return {
        "chunk_text": chunk,
        "conversation_title": title,
        "cursor": cursor,
        "finished": cursor.get("finished", False),
    }
