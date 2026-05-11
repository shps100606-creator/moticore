#!/usr/bin/env python3
"""moticore-agent entry point."""
import os
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_core
from memory import get_recent_actions, append_action
from decision import run_decision
from issues import get_open_issues, post_comment, close_issue, format_issues_for_prompt
from reader import get_next_chunk, save_cursor


def write_report(repo_root: Path, content: str) -> None:
    if not content:
        return
    date_str = datetime.utcnow().strftime("%Y%m%d")
    report_path = repo_root / "reports" / f"heartbeat-{date_str}.md"
    report_path.parent.mkdir(exist_ok=True)
    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n{content}")


def handle_issue_responses(decision: dict, github_token: str) -> None:
    for r in decision.get("issue_responses", []):
        num = r.get("issue_number")
        comment = r.get("comment", "")
        if not num or not comment:
            continue
        post_comment(github_token, num, comment)
        if r.get("close", False):
            close_issue(github_token, num)


def handle_file_operations(decision: dict, repo_root: Path) -> None:
    """Execute file_operations from the decision: create/append/overwrite files under notes/."""
    ops = decision.get("file_operations", [])
    if not ops:
        return
    notes_root = repo_root / "notes"
    notes_root.mkdir(exist_ok=True)
    for op in ops:
        raw_path = op.get("path", "")
        content = op.get("content", "")
        mode = op.get("mode", "append")
        if not raw_path.startswith("notes/"):
            print(f"[run] Skipping file op outside notes/: {raw_path}")
            continue
        file_path = repo_root / raw_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append":
            with file_path.open("a", encoding="utf-8") as f:
                f.write("\n" + content)
        else:
            file_path.write_text(content, encoding="utf-8")
        print(f"[run] File op '{mode}': {raw_path}")


def open_human_question_issue(github_token: str, question: str, context: str) -> None:
    """Open a GitHub Issue when the agent has a question for the human."""
    from issues import OWNER, REPO
    import requests
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = f"{question}\n\n---\n_閱讀脈絡：{context}_"
    resp = requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
        headers=headers,
        json={"title": f"[代理提問] {question[:60]}", "body": body},
    )
    resp.raise_for_status()
    print(f"[run] Human question Issue opened")


def main() -> None:
    print(f"[run] moticore-agent started at {datetime.utcnow().isoformat()}Z")

    github_token = os.environ.get("GITHUB_TOKEN", "")
    dialogues_token = os.environ.get("DIALOGUES_TOKEN", "")

    core = load_core(REPO_ROOT)
    print("[run] Motivation core loaded")

    open_issues = []
    if github_token:
        try:
            open_issues = get_open_issues(github_token)
            print(f"[run] Open Issues: {len(open_issues)}")
        except Exception as e:
            print(f"[run] Warning: could not fetch Issues: {e}")

    issues_text = format_issues_for_prompt(open_issues)
    recent = get_recent_actions(REPO_ROOT, n=10)

    # Read next chunk from prima-materia
    reading_chunk = ""
    reading_context = ""
    new_cursor = None
    if dialogues_token:
        try:
            result = get_next_chunk(dialogues_token, REPO_ROOT)
            reading_chunk = result["chunk_text"]
            reading_context = result["conversation_title"]
            new_cursor = result["cursor"]
            if result["finished"] and not reading_chunk:
                print("[run] All dialogues finished")
            else:
                print(f"[run] Reading: {reading_context} (offset {new_cursor.get('message_offset', 0)})")
        except Exception as e:
            print(f"[run] Warning: could not read prima-materia: {e}")
    else:
        print("[run] DIALOGUES_TOKEN not set, skipping reading")

    print("[run] Calling Gemini API...")
    try:
        decision = run_decision(core, recent, issues_text, reading_chunk)
    except Exception as exc:
        print(f"[run] ERROR calling Gemini: {exc}")
        sys.exit(1)

    print(f"[run] Decision: {decision.get('action_type')} — {decision.get('summary')}")

    if github_token:
        handle_issue_responses(decision, github_token)

        human_q = decision.get("human_question", "").strip()
        if human_q and github_token:
            open_human_question_issue(github_token, human_q, reading_context)

    handle_file_operations(decision, REPO_ROOT)

    if new_cursor:
        save_cursor(REPO_ROOT, new_cursor)

    append_action(REPO_ROOT, decision)

    # Update heartbeat workflow to also commit notes/
    print("[run] Done.")


if __name__ == "__main__":
    main()
