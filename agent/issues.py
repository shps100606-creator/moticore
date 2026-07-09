"""Read open Issues, post comments, and close Issues via GitHub REST API."""
import re
import requests

GITHUB_API = "https://api.github.com"
GRAPHQL_API = "https://api.github.com/graphql"
OWNER = "shps100606-creator"
REPO = "moticore"

PROGRESS_ISSUE = 7  # fixed dashboard issue — skip comments for this one
MOTI_BOT_LOGIN = "github-actions[bot]"


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
    """Fetch the latest comments on an issue."""
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


def fetch_discussions(github_token: str, replied_ids: set | None = None,
                       max_discussions: int = 10) -> tuple[str, dict]:
    """Fetch recent Giscus Discussions from the moticore repo via GraphQL.

    Returns (markdown_text, label_map). markdown_text is "" if none found or
    any error. label_map maps a short reference label (e.g. "G1") to
    {"discussion_id", "comment_id", "author"} for comments NOT already in
    replied_ids — these are the comments moti can target with
    §GISCUS_REPLY label=G1 (see post_discussion_reply). Comments already
    replied to are still shown for context but excluded from label_map.
    """
    if not github_token:
        return "", {}
    replied_ids = replied_ids or set()
    query = """
    query($owner: String!, $repo: String!, $first: Int!) {
      repository(owner: $owner, name: $repo) {
        discussions(first: $first, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            id
            title
            body
            comments(last: 3) {
              nodes {
                id
                body
                author { login }
              }
            }
          }
        }
      }
    }
    """
    try:
        resp = requests.post(
            GRAPHQL_API,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "variables": {"owner": OWNER, "repo": REPO, "first": max_discussions},
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errors"):
            return "", {}
        nodes = (
            data.get("data", {})
            .get("repository", {})
            .get("discussions", {})
            .get("nodes", [])
        )
        if not nodes:
            return "", {}
        lines = ["## Giscus 留言（最新 Discussions）\n"]
        label_map = {}
        label_n = 0
        for d in nodes:
            discussion_id = d.get("id", "")
            title = _sanitize(d.get("title", ""), 80)
            body = _sanitize(d.get("body", "") or "", 200)
            lines.append(f"### {title}")
            if body:
                lines.append(body)
            comments = d.get("comments", {}).get("nodes", [])
            if comments:
                lines.append("**留言：**")
                for c in comments:
                    author = (c.get("author") or {}).get("login", "unknown")
                    cbody = _sanitize(c.get("body", "") or "", 200)
                    comment_id = c.get("id", "")
                    if comment_id and comment_id not in replied_ids and discussion_id:
                        label_n += 1
                        label = f"G{label_n}"
                        label_map[label] = {
                            "discussion_id": discussion_id,
                            "comment_id": comment_id,
                            "author": author,
                        }
                        lines.append(f"- [{label}] [{author}]: {cbody}")
                    else:
                        lines.append(f"- [{author}]: {cbody}")
            lines.append("")
        return "\n".join(lines).strip(), label_map
    except Exception:
        return "", {}


def post_discussion_reply(github_token: str, discussion_id: str,
                          reply_to_id: str, body: str) -> bool:
    """Post a threaded reply to a Giscus Discussion comment via GraphQL
    mutation. Returns True on success, False on failure — a failed reply
    must not crash the heartbeat."""
    mutation = """
    mutation($discussionId: ID!, $replyToId: ID!, $body: String!) {
      addDiscussionComment(input: {discussionId: $discussionId, replyToId: $replyToId, body: $body}) {
        comment { id }
      }
    }
    """
    try:
        resp = requests.post(
            GRAPHQL_API,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json",
            },
            json={
                "query": mutation,
                "variables": {
                    "discussionId": discussion_id,
                    "replyToId": reply_to_id,
                    "body": body,
                },
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errors"):
            print(f"[issues] Giscus reply failed: {data['errors']}")
            return False
        print("[issues] Giscus reply posted")
        return True
    except Exception as e:
        print(f"[issues] Giscus reply failed: {e}")
        return False


def format_issues_for_prompt(issues: list, token: str = "") -> str:
    if not issues:
        return "（目前無待處理 Issue）"
    lines = []
    for i in issues:
        num = i["number"]
        title = _sanitize(i.get("title", ""), 80)
        body = _sanitize(i.get("body") or "", 300)

        # skip fetching comments for the progress dashboard issue
        if num == PROGRESS_ISSUE:
            lines.append(f"- Issue #{num}: {title}\n  內容: {body}")
            continue

        comments_text = ""
        response_flag = ""
        if token:
            comments = get_issue_comments(token, num, max_comments=10)

            human_comments = [
                c for c in comments
                if c.get("user", {}).get("type") != "Bot"
                and "github-actions" not in c.get("user", {}).get("login", "")
            ]
            moti_comments = [
                c for c in comments
                if MOTI_BOT_LOGIN in c.get("user", {}).get("login", "")
            ]

            # Flag issues moti has never replied to
            if not moti_comments:
                response_flag = "  ⚠️ 【尚未回應】moti 從未回覆此 Issue，本次必須回應。\n"

            # Flag issues with new human replies
            if human_comments:
                snippets = [
                    f"    [{c['user']['login']}]: {_sanitize(c['body'], 500)}"
                    for c in human_comments[-3:]
                ]
                comments_text = "\n  ⚠️ 【人類回覆，必須回應】:\n" + "\n".join(snippets)

        lines.append(
            f"- Issue #{num}: {title}\n"
            f"  內容: {body}\n"
            f"{response_flag}"
            f"{comments_text}"
        )
    return "\n".join(lines)
