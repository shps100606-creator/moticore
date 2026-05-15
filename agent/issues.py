"""Read open Issues, post comments, and close Issues via GitHub REST API."""
import re
import requests

GITHUB_API = "https://api.github.com"
OWNER = "shps100606-creator"
REPO = "moticore"

PROGRESS_ISSUE = 7  # fixed dashboard issue — skip comments for this one


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


def get_issue_comments(token: str, issue_number: int, max_comments: int = 10) -> list:
    """Fetch the latest comments on an issue (human replies)."""
    resp = requests.get(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments",
        headers=_headers(token),
        params={"per_page": max_comments},
    )
    if not resp.ok:
        return []
    return resp.json()


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


def _sanitize(text: str, max_len: int = 500) -> str:
    """Strip backtick code blocks and truncate for safe prompt embedding."""
    text = re.sub(r"```[\s\S]*?```", "[code block]", text)
    text = re.sub(r"`[^`]*`", "[code]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def format_issues_for_prompt(issues: list, token: str = "") -> str:
    if not issues:
        return "（目前無待處理 Issue）"
    lines = []
    for i in issues:
        num = i["number"]
        title = _sanitize(i.get("title", ""), 80)
        body = _sanitize(i.get("body") or "", 300)

        # skip fetching comments for the progress dashboard issue
        comments_text = ""
        if token and num != PROGRESS_ISSUE:
            comments = get_issue_comments(token, num, max_comments=10)
            # filter out bot's own comments (github-actions)
            human_comments = [
                c for c in comments
                if c.get("user", {}).get("type") != "Bot"
                and "github-actions" not in c.get("user", {}).get("login", "")
            ]
            if human_comments:
                snippets = [
                    f"    [{c['user']['login']}]: {_sanitize(c['body'], 500)}"
                    for c in human_comments[-3:]
                ]
                comments_text = "\n  人類回覆:\n" + "\n".join(snippets)

        lines.append(
            f"- Issue #{num}: {title}\n"
            f"  內容: {body}"
            f"{comments_text}"
        )
    return "\n".join(lines)
