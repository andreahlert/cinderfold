"""Rename detection: collapse (drop X, add Y) pairs into rename hints.

Heuristic, conservative:

- Table rename: an added table T_new and a dropped table T_old qualify when
  their column structures are identical (same names, same types, in any
  order). At most one match per dropped table.

- Column rename inside a kept table: an added column and a dropped column
  qualify when they share type *and* nullable flag. Ambiguity (two
  candidates with the same signature) disqualifies all of them, so the
  diff falls back to raw add/drop.

Output is a list of RenameHint(s) plus a filtered Change list that
removes the consumed presence entries.
"""

from __future__ import annotations

from dataclasses import dataclass

from .diff import Change
from .model import Schema


@dataclass(frozen=True)
class RenameHint:
    kind: str  # "table" or "column"
    table: str  # for table renames, the new name; for column, the table name
    old: str
    new: str


def detect_renames(old: Schema, new: Schema, changes: list[Change]) -> tuple[list[RenameHint], list[Change]]:
    hints: list[RenameHint] = []
    consumed: set[tuple[str, str | None, str]] = set()

    hints.extend(_table_renames(old, new, consumed))
    hints.extend(_column_renames(old, new, consumed))

    filtered = [
        c for c in changes
        if (c.table, c.column, c.detail) not in consumed
    ]
    return hints, filtered


def _table_renames(old, new, consumed):
    out: list[RenameHint] = []
    old_names = {t.name for t in old.tables}
    new_names = {t.name for t in new.tables}
    added = [t for t in new.tables if t.name not in old_names]
    dropped = [t for t in old.tables if t.name not in new_names]

    def shape(t):
        return frozenset((c.name, c.type) for c in t.columns)

    used_added: set[str] = set()
    for d in dropped:
        match = None
        for a in added:
            if a.name in used_added:
                continue
            if shape(a) == shape(d):
                if match is not None:
                    match = None
                    break
                match = a
        if match is not None:
            used_added.add(match.name)
            out.append(RenameHint("table", match.name, d.name, match.name))
            consumed.add((d.name, None, "table dropped"))
            consumed.add((match.name, None, "table added"))
    return out


def _column_renames(old, new, consumed):
    out: list[RenameHint] = []
    old_names = {t.name for t in old.tables}
    new_names = {t.name for t in new.tables}
    for name in old_names & new_names:
        ot, nt = old.table(name), new.table(name)
        old_cols = {c.name: c for c in ot.columns}
        new_cols = {c.name: c for c in nt.columns}
        added = [c for c in nt.columns if c.name not in old_cols]
        dropped = [c for c in ot.columns if c.name not in new_cols]

        for d in dropped:
            matches = [
                a for a in added
                if a.type == d.type and a.nullable == d.nullable
            ]
            if len(matches) == 1:
                a = matches[0]
                out.append(RenameHint("column", name, d.name, a.name))
                consumed.add((name, d.name, "column dropped"))
                consumed.add((name, a.name, "column added"))
                added.remove(a)
    return out
