#!/usr/bin/env python3
"""moticore-agent entry point.

Workflow:
1. Load motivation core documents
2. Read recent action log
3. Call Claude API with motivation core as system prompt
4. Append decision to action log
5. Write introspection report if needed
"""
import sys
from pathlib import Path
from datetime import datetime

# Allow running from repo root or agent/ directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_core
from memory import get_recent_actions, append_action
from decision import run_decision


def write_report(repo_root: Path, content: str) -> None:
    if not content:
        return
    date_str = datetime.utcnow().strftime("%Y%m%d")
    report_path = repo_root / "reports" / f"heartbeat-{date_str}.md"
    report_path.parent.mkdir(exist_ok=True)
    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n{content}")
    print(f"[run] Report written to {report_path.name}")


def main() -> None:
    print(f"[run] moticore-agent started at {datetime.utcnow().isoformat()}Z")

    # 1. Load motivation core
    core = load_core(REPO_ROOT)
    print("[run] Motivation core loaded")

    # 2. Read recent actions
    recent = get_recent_actions(REPO_ROOT, n=10)

    # 3. Call Claude
    print("[run] Calling Claude API...")
    try:
        decision = run_decision(core, recent)
    except Exception as exc:
        print(f"[run] ERROR calling Claude: {exc}")
        sys.exit(1)

    print(f"[run] Decision received: {decision.get('action_type')}")
    print(f"[run] Summary: {decision.get('summary')}")
    print(f"[run] Deviation flag: {decision.get('deviation_flag')}")

    # 4. Append to action log
    append_action(REPO_ROOT, decision)
    print("[run] Action logged")

    # 5. Write report if agent produced one
    write_report(REPO_ROOT, decision.get("report_content", ""))

    print("[run] Done.")


if __name__ == "__main__":
    main()
