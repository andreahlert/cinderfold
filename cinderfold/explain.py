"""Per-change rationale: why a Change matters and what to do about it.

The text is intentionally short (one or two sentences) and stable, so
downstream tools can group by it. Use cases:

- PR comment with actionable hints next to each change.
- Annotated CI logs that suggest a remediation rather than just a diff.
"""

from __future__ import annotations

from .diff import Change


_RATIONALE = {
    "presence:table added":
        "Backfilling readers may need to ignore this table until the consumer is deployed.",
    "presence:table dropped":
        "Anything that joins on this table will start failing immediately; "
        "check consumers before merging.",
    "presence:column added":
        "Add a default or a backfill plan; existing writers without the column will fail "
        "if it is NOT NULL.",
    "presence:column dropped":
        "Search the codebase for the column name; drop is a breaking change.",
    "type":
        "Type changes are not free; widen first, narrow last, and always backfill.",
    "constraint":
        "Constraint flips can invalidate existing rows; check for nulls/duplicates "
        "before applying.",
    "auxiliary":
        "Cosmetic for most pipelines; still worth a glance for documentation drift.",
}


def explain(change: Change) -> str:
    if change.category == "presence":
        for key, msg in _RATIONALE.items():
            if key.startswith("presence:") and key.split(":", 1)[1] in change.detail:
                return msg
        return _RATIONALE.get("presence", "")
    return _RATIONALE.get(change.category, "")


def annotate(changes) -> list[tuple[Change, str]]:
    return [(c, explain(c)) for c in changes]
