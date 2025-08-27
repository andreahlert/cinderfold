"""Forward-compatibility check between two schemas.

`compatible(old, new)` returns True when a reader written against `old`
can still consume rows produced under `new` without crashing. Used to
decide whether a producer can deploy ahead of consumer rollouts.

The rules are deliberately strict; if you need looser semantics, filter
the returned reasons instead of relying on the boolean.
"""

from __future__ import annotations

from .diff import diff
from .model import Schema


def compatible(old: Schema, new: Schema) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for c in diff(old, new):
        if c.category == "presence" and "dropped" in c.detail:
            reasons.append(f"{c.table}.{c.column or '*'}: {c.detail}")
        elif c.category == "type":
            reasons.append(f"{c.table}.{c.column}: {c.detail}")
        elif c.category == "constraint" and "True -> False" in c.detail and "nullable" in c.detail:
            reasons.append(f"{c.table}.{c.column}: column became NOT NULL")
    return (not reasons), reasons
