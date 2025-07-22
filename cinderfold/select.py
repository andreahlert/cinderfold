"""Subset / merge utilities on Schema.

select(schema, patterns)
    Return a new Schema containing only tables whose names match any
    of the given glob patterns. Patterns use fnmatch syntax.

merge(*schemas)
    Concatenate tables. Duplicate names are a hard error; callers can
    pre-filter when intentional overlap exists.
"""

from __future__ import annotations

import fnmatch
from typing import Iterable

from .model import Schema, Table


def select(schema: Schema, patterns: Iterable[str]) -> Schema:
    pats = list(patterns)
    if not pats:
        return Schema(())
    keep: list[Table] = [t for t in schema.tables if _matches(t.name, pats)]
    return Schema(tuple(keep))


def exclude(schema: Schema, patterns: Iterable[str]) -> Schema:
    pats = list(patterns)
    keep: list[Table] = [t for t in schema.tables if not _matches(t.name, pats)]
    return Schema(tuple(keep))


def merge(*schemas: Schema) -> Schema:
    seen: dict[str, Table] = {}
    for s in schemas:
        for t in s.tables:
            if t.name in seen:
                raise ValueError(f"duplicate table {t.name!r} during merge")
            seen[t.name] = t
    return Schema(tuple(seen.values()))


def _matches(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(name, p) for p in patterns)
