"""Schema audit log: dated changelog from a sequence of (date, schema) snapshots.

Given an ordered list of snapshots, render a Markdown changelog grouped
by date, with each section listing the diff against the previous snapshot.
Severity-ranked so the highest-impact entries come first under each date.

This is meant for human-facing release notes, not machine consumption.
For machine consumption, run `diff` on successive snapshots directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from .diff import Change, SEVERITY, diff
from .model import Schema


@dataclass(frozen=True)
class AuditEntry:
    date: str
    changes: tuple[Change, ...]


def audit(snapshots: list[tuple[str, Schema]]) -> list[AuditEntry]:
    if not snapshots:
        return []
    out: list[AuditEntry] = []
    prev: Schema | None = None
    for date, schema in snapshots:
        if prev is None:
            base = Schema(tables=())
            changes = diff(base, schema)
        else:
            changes = diff(prev, schema)
        if changes:
            out.append(AuditEntry(date=date, changes=tuple(changes)))
        prev = schema
    return out


def to_markdown(entries: list[AuditEntry], title: str = "Schema changelog") -> str:
    lines = [f"# {title}", ""]
    if not entries:
        lines.append("_No changes recorded._")
        return "\n".join(lines)
    for e in entries:
        lines.append(f"## {e.date}")
        lines.append("")
        ranked = sorted(e.changes, key=lambda c: (-SEVERITY[c.category], c.table))
        for c in ranked:
            target = c.table if c.column is None else f"{c.table}.{c.column}"
            lines.append(f"- **{c.category}** `{target}` {c.detail}")
        lines.append("")
    return "\n".join(lines)
