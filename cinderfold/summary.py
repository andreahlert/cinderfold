"""High-level rollups over a Change list."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .diff import Change


@dataclass(frozen=True)
class Summary:
    by_category: dict[str, int]
    by_table: dict[str, int]
    total: int

    @property
    def max_severity(self) -> str | None:
        order = ["presence", "type", "constraint", "auxiliary"]
        for k in order:
            if self.by_category.get(k):
                return k
        return None


def summarize(changes: Iterable[Change]) -> Summary:
    changes = list(changes)
    cats = Counter(c.category for c in changes)
    tables = Counter(c.table for c in changes)
    return Summary(by_category=dict(cats), by_table=dict(tables), total=len(changes))


def one_line(s: Summary) -> str:
    if s.total == 0:
        return "0 changes"
    parts = [f"{v} {k}" for k, v in sorted(s.by_category.items(),
                                            key=lambda kv: -["presence", "type",
                                                              "constraint", "auxiliary"
                                                              ].index(kv[0]))]
    return f"{s.total} changes ({', '.join(parts)})"
