"""Post-hoc filtering of a Change list (output of diff.diff).

filter_changes(changes, ...)
    Drop entries whose category is below `min_severity`, or whose
    table does not match any of `include` globs, or that match any
    of `exclude` globs.
"""

from __future__ import annotations

import fnmatch
from typing import Iterable

from .diff import SEVERITY, Change


def filter_changes(
    changes: Iterable[Change],
    *,
    min_severity: str | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[Change]:
    floor = SEVERITY[min_severity] if min_severity else None
    inc = list(include) if include else None
    exc = list(exclude) if exclude else None
    out: list[Change] = []
    for c in changes:
        if floor is not None and c.severity < floor:
            continue
        if inc is not None and not any(fnmatch.fnmatchcase(c.table, p) for p in inc):
            continue
        if exc is not None and any(fnmatch.fnmatchcase(c.table, p) for p in exc):
            continue
        out.append(c)
    return out
