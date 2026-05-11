#!/usr/bin/env python3
"""moticore-agent entry point."""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_core
from memory import get_recent_actions, append_action
from decision import run_decision, generate_file_content
from issues import get_open_issues, post_comment, close_issue, format_issues_for_prompt
from reader import get_next_chunk, save_cursor

# Paths the agent is never allowed to modify
PROTECTED = {"agent"}


def handle_issue_responses(decision: dict, github_token: str) -> None:
    for r in decision.get("issue_responses", []):
        num = r.get("issue_number")
        comment = r.get("comment", "")
        if not num or not comment:
            continue
        post_comment(github_token, num, comment)
        if r.get("close", False):
            close_issue(github_token, num)


def handle_file_operations(decision: dict, reading_chunk: str, core: dict, repo_root: Path) -> None:
    ops = decision.get("file_operations", [])
    if not ops:
        return
    for op in ops:
        raw_path = op.get("path", "")
        description = op.get("description", "")
        mode = op.get("mode", "append")

        # Protect agent/ directory
        top = raw_path.strip("/").split("/")[0]
        if top in PROTECTED:
            print(f"[run] BLOCKED: cannot modify protected path: {raw_path}")
            continue

        print(f"[run] Generating content for {raw_path}...")
        try:
            content = generate_file_content(core, reading_chunk, raw_path, description)
        except Exception as e:
            print(f"[run] Warning: could not generate {raw_path}: {e}")
            continue

        file_path = repo_root / raw_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append":
            with file_path.open("a", encoding="utf-8") as f:
                f.write("\n\n" + content)
        else:
            file_path.write_text(content, encoding="utf-8")
        print(f"[run] Written: {raw_path}")


def open_human_question_issue(github_token: str, question: str, context: str) -> None:
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
    print("[run] Human question Issue opened")


def call_gemini_with_retry(core, recent, issues_text, reading_chunk, retries=3):
    for attempt in range(retries):
        try:
            return run_decision(core, recent, issues_text, reading_chunk)
        except Exception as exc:
            msg = str(exc)
            if "503" in msg or "UNAVAILABLE" in msg:
                wait = 2 ** (attempt + 1)
                print(f"[run] Gemini 503, retrying in {wait}s... ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini unavailable after retries")


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
                print(f"[run] Reading: {reading_context}")
        except Exception as e:
            print(f"[run] Warning: could not read prima-materia: {e}")

    print("[run] Calling Gemini (decision)...")
    try:
        decision = call_gemini_with_retry(core, recent, issues_text, reading_chunk)
    except Exception as exc:
        print(f"[run] ERROR calling Gemini: {exc}")
        sys.exit(1)

    print(f"[run] Decision: {decision.get('action_type')} -- {decision.get('summary')}")

    if github_token:
        handle_issue_responses(decision, github_token)
        human_q = decision.get("human_question", "").strip()
        if human_q:
            open_human_question_issue(github_token, human_q, reading_context)

    handle_file_operations(decision, reading_chunk, core, REPO_ROOT)

    if new_cursor:
        save_cursor(REPO_ROOT, new_cursor)

    append_action(REPO_ROOT, decision)
    print("[run] Done.")


if __name__ == "__main__":
    main()
