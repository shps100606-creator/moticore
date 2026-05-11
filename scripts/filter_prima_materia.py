"""One-time script: filter prima-materia/conversations.json
and write back motive-theory.json + filter-report.md.
"""
import json
import os
import base64
import requests
from pathlib import Path

OWNER = "shps100606-creator"
REPO = "prima-materia"
API = "https://api.github.com"

KEYWORDS = [
    "動機", "動機論", "主體", "意識", "自由意志",
    "存在", "意志", "自我", "自治", "意圖",
    "目的", "價值", "哲學", "認知", "行動者",
    "行動理論", "心理哲學", "認識論",
    "motive", "motivation", "agency", "autonomy", "volition",
    "consciousness", "free will", "intentionality",
]


def gh_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def score(conv):
    title = conv.get("title", "").lower()
    mapping = conv.get("mapping", {})
    texts = [title]
    n = 0
    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue
        parts = msg.get("content", {}).get("parts", [])
        text = " ".join(p for p in parts if isinstance(p, str))
        if text.strip():
            texts.append(text[:500])
            n += 1
            if n >= 3:
                break
    combined = " ".join(texts).lower()
    return sum(1 for kw in KEYWORDS if kw.lower() in combined)


def put_file(token, path, content_str, message):
    """Create or update a file in prima-materia."""
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    # Get existing SHA if file exists
    r = requests.get(url, headers={**gh_headers(token), "Accept": "application/vnd.github+json"})
    sha = r.json().get("sha") if r.status_code == 200 else None
    body = {
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode(),
    }
    if sha:
        body["sha"] = sha
    r = requests.put(url, headers={**gh_headers(token), "Accept": "application/vnd.github+json"}, json=body)
    r.raise_for_status()


def main():
    token = os.environ["DIALOGUES_TOKEN"]

    print("Fetching conversations.json...")
    resp = requests.get(
        f"{API}/repos/{OWNER}/{REPO}/contents/dialogues/conversations.json",
        headers=gh_headers(token),
    )
    resp.raise_for_status()
    conversations = resp.json()
    print(f"Total: {len(conversations)} conversations")

    kept, skipped_titles = [], []
    for conv in conversations:
        s = score(conv)
        title = conv.get("title", "(untitled)")
        if s >= 2:
            kept.append(conv)
            print(f"  KEEP  (score={s:2d})  {title}")
        else:
            skipped_titles.append(title)
            print(f"  skip  (score={s:2d})  {title}")

    print(f"\nResult: kept {len(kept)}, skipped {len(skipped_titles)}")

    filtered_json = json.dumps(kept, ensure_ascii=False, indent=2)
    put_file(token, "dialogues/motive-theory.json", filtered_json,
             f"chore: filtered motive-theory ({len(kept)} conversations)")
    print("motive-theory.json written")

    lines = ["# 動機論筛選報告", "",
             f"保留 **{len(kept)}** 篇 / 略過 **{len(skipped_titles)}** 篇", "",
             "## 保留的對話"]
    for c in kept:
        lines.append(f"- {c.get('title', '(untitled)')}")
    lines += ["", "## 略過的對話"]
    for t in skipped_titles:
        lines.append(f"- {t}")
    put_file(token, "dialogues/filter-report.md", "\n".join(lines),
             "chore: filter report")
    print("filter-report.md written")


if __name__ == "__main__":
    main()
