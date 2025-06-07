"""Schema diff classified into four severity categories.

- presence    : tables added/dropped, columns added/dropped
- type        : column type changed
- constraint  : pk, nullable (not_null -> nullable), unique flipped
- auxiliary   : default, comment

Each Change carries a `category`, a `severity` rank, and a human description.
Severity ordering: presence > type > constraint > auxiliary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .model import Column, Schema, Table


Category = Literal["presence", "type", "constraint", "auxiliary"]
SEVERITY = {"presence": 3, "type": 2, "constraint": 1, "auxiliary": 0}


@dataclass(frozen=True)
class Change:
    category: Category
    table: str
    column: str | None
    detail: str

    @property
    def severity(self) -> int:
        return SEVERITY[self.category]


def diff(old: Schema, new: Schema) -> list[Change]:
    out: list[Change] = []

    old_names = {t.name for t in old.tables}
    new_names = {t.name for t in new.tables}

    for name in sorted(new_names - old_names):
        out.append(Change("presence", name, None, "table added"))
    for name in sorted(old_names - new_names):
        out.append(Change("presence", name, None, "table dropped"))

    for name in sorted(old_names & new_names):
        out.extend(_diff_table(old.table(name), new.table(name)))

    out.sort(key=lambda c: (-c.severity, c.table, c.column or ""))
    return out


def _diff_table(old: Table, new: Table) -> list[Change]:
    out: list[Change] = []
    old_cols = {c.name: c for c in old.columns}
    new_cols = {c.name: c for c in new.columns}

    for cname in sorted(new_cols.keys() - old_cols.keys()):
        out.append(Change("presence", old.name, cname, "column added"))
    for cname in sorted(old_cols.keys() - new_cols.keys()):
        out.append(Change("presence", old.name, cname, "column dropped"))

    for cname in sorted(old_cols.keys() & new_cols.keys()):
        out.extend(_diff_column(old.name, old_cols[cname], new_cols[cname]))

    return out


def _diff_column(table: str, a: Column, b: Column) -> list[Change]:
    out: list[Change] = []
    if a.type != b.type:
        out.append(Change("type", table, a.name, f"type {a.type} -> {b.type}"))
    if a.pk != b.pk:
        out.append(Change("constraint", table, a.name, f"pk {a.pk} -> {b.pk}"))
    if a.nullable != b.nullable:
        out.append(Change("constraint", table, a.name, f"nullable {a.nullable} -> {b.nullable}"))
    if a.unique != b.unique:
        out.append(Change("constraint", table, a.name, f"unique {a.unique} -> {b.unique}"))
    if a.default != b.default:
        out.append(Change("auxiliary", table, a.name, f"default {a.default!r} -> {b.default!r}"))
    if a.comment != b.comment:
        out.append(Change("auxiliary", table, a.name, f"comment {a.comment!r} -> {b.comment!r}"))
    return out
