"""Read open Issues, post comments, and close Issues via GitHub REST API."""
import os
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
    """Return open Issues (excluding pull requests), newest first."""
    resp = requests.get(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues",
        headers=_headers(token),
        params={"state": "open", "per_page": 20, "sort": "created", "direction": "desc"},
    )
    resp.raise_for_status()
    return [i for i in resp.json() if "pull_request" not in i]


def post_comment(token: str, issue_number: int, body: str) -> None:
    """Post a comment on an Issue."""
    resp = requests.post(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments",
        headers=_headers(token),
        json={"body": body},
    )
    resp.raise_for_status()
    print(f"[issues] Comment posted on Issue #{issue_number}")


def close_issue(token: str, issue_number: int) -> None:
    """Close an Issue."""
    resp = requests.patch(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}",
        headers=_headers(token),
        json={"state": "closed", "state_reason": "completed"},
    )
    resp.raise_for_status()
    print(f"[issues] Issue #{issue_number} closed")


def format_issues_for_prompt(issues: list) -> str:
    """Format open issues into readable text for the decision prompt."""
    if not issues:
        return "（目前無待處理 Issue）"
    lines = []
    for i in issues:
        lines.append(
            f"- Issue #{i['number']}: {i['title']}\n"
            f"  內容: {(i.get('body') or '（無說明）')[:300]}"
        )
    return "\n".join(lines)
