#!/usr/bin/env python3
"""moticore-agent entry point.

Workflow:
1. Load motivation core documents
2. Read open GitHub Issues (incoming tasks from humans)
3. Read recent action log
4. Call Gemini API with full context
5. Post comments and close Issues based on decision
6. Append decision to action log
7. Write report if needed
"""
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


def write_report(repo_root: Path, content: str) -> None:
    if not content:
        return
    date_str = datetime.utcnow().strftime("%Y%m%d")
    report_path = repo_root / "reports" / f"heartbeat-{date_str}.md"
    report_path.parent.mkdir(exist_ok=True)
    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n{content}")
    print(f"[run] Report written to {report_path.name}")


def handle_issue_responses(decision: dict, github_token: str) -> None:
    responses = decision.get("issue_responses", [])
    if not responses:
        print("[run] No Issue responses to post")
        return
    for r in responses:
        num = r.get("issue_number")
        comment = r.get("comment", "")
        should_close = r.get("close", False)
        if not num or not comment:
            continue
        post_comment(github_token, num, comment)
        if should_close:
            close_issue(github_token, num)


def main() -> None:
    print(f"[run] moticore-agent started at {datetime.utcnow().isoformat()}Z")

    github_token = os.environ.get("GITHUB_TOKEN", "")

    # 1. Load motivation core
    core = load_core(REPO_ROOT)
    print("[run] Motivation core loaded")

    # 2. Read open Issues
    open_issues = []
    if github_token:
        try:
            open_issues = get_open_issues(github_token)
            print(f"[run] Open Issues: {len(open_issues)}")
        except Exception as e:
            print(f"[run] Warning: could not fetch Issues: {e}")
    else:
        print("[run] GITHUB_TOKEN not set, skipping Issue fetch")

    issues_text = format_issues_for_prompt(open_issues)

    # 3. Read recent actions
    recent = get_recent_actions(REPO_ROOT, n=10)

    # 4. Call Gemini
    print("[run] Calling Gemini API...")
    try:
        decision = run_decision(core, recent, issues_text)
    except Exception as exc:
        print(f"[run] ERROR calling Gemini: {exc}")
        sys.exit(1)

    print(f"[run] Decision: {decision.get('action_type')}")
    print(f"[run] Summary: {decision.get('summary')}")
    print(f"[run] Deviation flag: {decision.get('deviation_flag')}")

    # 5. Handle Issue responses
    if github_token:
        handle_issue_responses(decision, github_token)

    # 6. Append to action log
    append_action(REPO_ROOT, decision)
    print("[run] Action logged")

    # 7. Write report if any
    write_report(REPO_ROOT, decision.get("report_content", ""))

    print("[run] Done.")


if __name__ == "__main__":
    main()
