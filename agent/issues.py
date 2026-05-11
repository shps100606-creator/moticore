"""Read open Issues, post comments, and close Issues via GitHub REST API."""
import re
import requests

GITHUB_API = "https://api.github.com"
OWNER = "shps100606-creator"
REPO = "moticore"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_open_issues(token: str) -> list:
    resp = requests.get(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues",
        headers=_headers(token),
        params={"state": "open", "per_page": 20, "sort": "created", "direction": "desc"},
    )
    resp.raise_for_status()
    return [i for i in resp.json() if "pull_request" not in i]


def post_comment(token: str, issue_number: int, body: str) -> None:
    resp = requests.post(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments",
        headers=_headers(token),
        json={"body": body},
    )
    resp.raise_for_status()
    print(f"[issues] Comment posted on Issue #{issue_number}")


def close_issue(token: str, issue_number: int) -> None:
    resp = requests.patch(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}",
        headers=_headers(token),
        json={"state": "closed", "state_reason": "completed"},
    )
    resp.raise_for_status()
    print(f"[issues] Issue #{issue_number} closed")


def _sanitize(text: str, max_len: int = 200) -> str:
    """Strip markdown special chars and truncate for safe prompt embedding."""
    text = re.sub(r"```[\s\S]*?```", "[code block]", text)  # remove code fences
    text = re.sub(r"[`*#\[\]{}]", "", text)                  # remove inline markdown + braces
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def format_issues_for_prompt(issues: list) -> str:
    if not issues:
        return "（目前無待處理 Issue）"
    lines = []
    for i in issues:
        title = _sanitize(i.get("title", ""), 80)
        body = _sanitize(i.get("body") or "", 200)
        lines.append(f"- Issue #{i['number']}: {title}\n  內容: {body}")
    return "\n".join(lines)
