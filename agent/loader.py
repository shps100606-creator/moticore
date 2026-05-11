"""Load motivation core documents from the repo into memory."""
from pathlib import Path


DOC_MAP = {
    "identity":          "motive-core/identity.md",
    "prime_motive":      "motive-core/prime-motive.md",
    "value_hierarchy":   "motive-core/value-hierarchy.md",
    "constitution":      "motive-core/constitution.md",
    "forbidden":         "guardrails/forbidden-patterns.md",
    "boundary":          "guardrails/boundary-rules.md",
    "action_log":        "memory/action-log.md",
    "deviation_log":     "reflexive/deviation-log.md",
    "semantic_rulings":  "reflexive/semantic-rulings.md",
    "task_inbox":        "tasks/inbox.md",
}


def load_core(repo_root: Path) -> dict:
    """Read all motivation core documents and return as a dict."""
    core = {}
    for key, rel_path in DOC_MAP.items():
        path = repo_root / rel_path
        core[key] = path.read_text(encoding="utf-8") if path.exists() else ""
    return core
