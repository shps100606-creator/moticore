#!/usr/bin/env python3
"""moticore-agent entry point — 4-module architecture.

1. loader      : load MOTIVE.md (motivation core)
2. preprocessor: pure-code formatting of all context data
3. decision    : single Gemini call (consciousness module)
4. action      : pure-code execution of the decision
"""
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_motive
from memory import append_action
from decision import run_consciousness
from issues import get_open_issues, post_comment, close_issue, format_issues_for_prompt
from reader import get_next_chunk, save_cursor
from preprocessor import build_report

PROGRESS_ISSUE = 7
QUESTION_LABEL = "[代理提問]"


def post_progress_report(github_token, reading_context, cursor, decision):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    file_idx = cursor.get("file_index", 0) + 1 if cursor else "?"
    char_off = cursor.get("char_offset", 0) if cursor else "?"
    finished = cursor.get("finished", False) if cursor else False
    progress_line = "全部讀完！" if finished else f"第 {file_idx}/29 篇 《{reading_context}》，已讀至第 {char_off:,} 字"
    reflection = decision.get("self_reflection", "").strip()[:120] if decision else "本次跳過（Gemini 暫時不可用）"
    summary = decision.get("summary", "").strip()[:80] if decision else ""
    post_comment(github_token, PROGRESS_ISSUE,
                 f"**{now}**\n\n📖 {progress_line}\n💡 {summary}\n🧠 {reflection}")
    print(f"[run] Progress posted to Issue #{PROGRESS_ISSUE}")


def handle_issue_responses(decision, github_token):
    for r in decision.get("issue_responses", []):
        num = r.get("issue_number")
        comment = r.get("comment", "")
        if not num or not comment or num == PROGRESS_ISSUE:
            continue
        post_comment(github_token, num, comment)
        if r.get("close", False):
            close_issue(github_token, num)


def handle_file_writes(decision, repo_root: Path):
    for fw in decision.get("file_writes", []):
        path_str = fw.get("path", "")
        content = fw.get("content", "")
        if not path_str or not content:
            continue
        if path_str.strip("/").split("/")[0] == "agent":
            print(f"[run] BLOCKED: {path_str}")
            continue
        file_path = repo_root / path_str
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"[run] Written: {path_str}")


def save_read_requests(repo_root: Path, read_next: list):
    req_path = repo_root / "memory" / "read-requests.json"
    req_path.parent.mkdir(parents=True, exist_ok=True)
    req_path.write_text(json.dumps(read_next, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[run] Read requests saved: {read_next}")


def has_open_question_issue(open_issues: list) -> bool:
    return any(
        QUESTION_LABEL in i.get("title", "")
        for i in open_issues
        if i.get("number") != PROGRESS_ISSUE
    )


def open_human_question_issue(github_token, question, context):
    from issues import OWNER, REPO
    import requests
    headers = {"Authorization": f"Bearer {github_token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    body = f"{question}\n\n---\n_閱讀脈絡：{context}_"
    requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
        headers=headers,
        json={"title": f"{QUESTION_LABEL} {question[:60]}", "body": body},
    ).raise_for_status()
    print("[run] Human question Issue opened")


def call_with_retry(motive, report, reading_chunk, retries=4):
    waits = [10, 20, 40, 60]
    for attempt in range(retries):
        try:
            return run_consciousness(motive, report, reading_chunk)
        except Exception as exc:
            msg = str(exc)
            if any(k in msg for k in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]):
                wait = waits[attempt]
                print(f"[run] Gemini unavailable, retry in {wait}s ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise
    return None


def main():
    print(f"[run] moticore-agent started at {datetime.utcnow().isoformat()}Z")

    github_token = os.environ.get("GITHUB_TOKEN", "")
    dialogues_token = os.environ.get("DIALOGUES_TOKEN", "")

    # --- Module 1: Load motivation core ---
    motive = load_motive(REPO_ROOT)
    print("[run] Motive core loaded")

    # --- Fetch open issues ---
    open_issues = []
    if github_token:
        try:
            open_issues = get_open_issues(github_token)
            print(f"[run] Open Issues: {len(open_issues)}")
        except Exception as e:
            print(f"[run] Warning: {e}")

    # --- Get reading chunk ---
    reading_chunk = ""
    reading_context = ""
    new_cursor = None
    if dialogues_token:
        try:
            result = get_next_chunk(dialogues_token, REPO_ROOT)
            reading_chunk = result["chunk_text"]
            reading_context = result["conversation_title"]
            new_cursor = result["cursor"]
            print(f"[run] Reading: {reading_context}")
        except Exception as e:
            print(f"[run] Warning: {e}")

    # --- Module 2: Pre-process all context data ---
    report = build_report(
        repo_root=REPO_ROOT,
        open_issues=open_issues,
        github_token=github_token,
        cursor=new_cursor,
        format_issues_fn=format_issues_for_prompt,
    )
    print(f"[run] Pre-processed report: {len(report)} chars")

    # --- Module 3: Single AI call (consciousness module) ---
    print("[run] Calling Gemini...")
    try:
        decision = call_with_retry(motive, report, reading_chunk)
    except Exception as exc:
        print(f"[run] ERROR: {exc}")
        sys.exit(1)

    if decision is None:
        print("[run] Gemini unavailable, skipping heartbeat gracefully.")
        if github_token and reading_context:
            try:
                post_progress_report(github_token, reading_context, new_cursor or {}, None)
            except Exception:
                pass
        sys.exit(0)

    print(f"[run] Decision: {decision.get('action_type')} -- {decision.get('summary')}")

    # --- Module 4: Execute actions ---
    if github_token:
        handle_issue_responses(decision, github_token)
        human_q = decision.get("human_question", "").strip()
        if human_q:
            if has_open_question_issue(open_issues):
                print("[run] Skipping new question — unanswered [代理提問] already open")
            else:
                open_human_question_issue(github_token, human_q, reading_context)

    handle_file_writes(decision, REPO_ROOT)

    read_next = decision.get("read_next", [])
    if isinstance(read_next, list) and read_next:
        save_read_requests(REPO_ROOT, read_next)

    if new_cursor:
        save_cursor(REPO_ROOT, new_cursor)

    append_action(REPO_ROOT, decision)

    if github_token:
        try:
            post_progress_report(github_token, reading_context, new_cursor or {}, decision)
        except Exception as e:
            print(f"[run] Warning (progress): {e}")

    print("[run] Done.")


if __name__ == "__main__":
    main()
