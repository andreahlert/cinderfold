"""Formatters for diff results.

Three sinks share the same input (list[Change] from diff.diff):
- to_text: human-friendly grouped output for terminals.
- to_json: machine-friendly stable structure for pipelines.
- to_markdown: PR-ready summary with severity legend.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable

from .diff import Change


_LEGEND = {
    "presence": "table/column/index/fk added or dropped",
    "type": "column type or fk target changed",
    "constraint": "pk, nullable, unique, on_delete, on_update",
    "auxiliary": "default or comment",
}


def to_text(changes: Iterable[Change]) -> str:
    changes = list(changes)
    if not changes:
        return "no changes\n"
    lines: list[str] = []
    bucket: dict[str, list[Change]] = {}
    for c in changes:
        bucket.setdefault(c.category, []).append(c)
    for cat in ("presence", "type", "constraint", "auxiliary"):
        items = bucket.get(cat)
        if not items:
            continue
        lines.append(f"[{cat}] ({_LEGEND[cat]})")
        for c in items:
            tag = c.table if c.column is None else f"{c.table}.{c.column}"
            lines.append(f"  - {tag}: {c.detail}")
    return "\n".join(lines) + "\n"


def to_json(changes: Iterable[Change]) -> str:
    payload = [
        {
            "category": c.category,
            "severity": c.severity,
            "table": c.table,
            "column": c.column,
            "detail": c.detail,
        }
        for c in changes
    ]
    return json.dumps(payload, indent=2) + "\n"


def to_csv(changes: Iterable[Change], delimiter: str = ",") -> str:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=delimiter)
    w.writerow(["category", "severity", "table", "column", "detail"])
    for c in changes:
        w.writerow([c.category, c.severity, c.table, c.column or "", c.detail])
    return buf.getvalue()


def to_tsv(changes: Iterable[Change]) -> str:
    return to_csv(changes, delimiter="\t")


def to_markdown(changes: Iterable[Change]) -> str:
    changes = list(changes)
    if not changes:
        return "## Schema diff\n\nNo changes.\n"
    out = ["## Schema diff", ""]
    bucket: dict[str, list[Change]] = {}
    for c in changes:
        bucket.setdefault(c.category, []).append(c)
    for cat in ("presence", "type", "constraint", "auxiliary"):
        items = bucket.get(cat)
        if not items:
            continue
        out.append(f"### {cat} ({_LEGEND[cat]})")
        out.append("")
        out.append("| Table | Column | Detail |")
        out.append("|-------|--------|--------|")
        for c in items:
            col = "" if c.column is None else c.column
            out.append(f"| {c.table} | {col} | {c.detail} |")
        out.append("")
    return "\n".join(out)
