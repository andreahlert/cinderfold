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

from .model import Column, ForeignKey, Index, Schema, Table


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

    out.extend(_diff_indexes(old, new))
    out.extend(_diff_fks(old, new))
    return out


def _diff_indexes(old: Table, new: Table) -> list[Change]:
    out: list[Change] = []
    old_ix = {i.name: i for i in old.indexes}
    new_ix = {i.name: i for i in new.indexes}
    for n in sorted(new_ix.keys() - old_ix.keys()):
        out.append(Change("presence", old.name, n, f"index added on {new_ix[n].columns}"))
    for n in sorted(old_ix.keys() - new_ix.keys()):
        out.append(Change("presence", old.name, n, f"index dropped from {old_ix[n].columns}"))
    for n in sorted(old_ix.keys() & new_ix.keys()):
        a, b = old_ix[n], new_ix[n]
        if a.columns != b.columns:
            out.append(Change("constraint", old.name, n,
                              f"index columns {a.columns} -> {b.columns}"))
        if a.unique != b.unique:
            out.append(Change("constraint", old.name, n,
                              f"index unique {a.unique} -> {b.unique}"))
    return out


def _diff_fks(old: Table, new: Table) -> list[Change]:
    out: list[Change] = []
    old_fk = {f.name: f for f in old.foreign_keys}
    new_fk = {f.name: f for f in new.foreign_keys}
    for n in sorted(new_fk.keys() - old_fk.keys()):
        f = new_fk[n]
        out.append(Change("presence", old.name, n,
                          f"fk added {f.columns} -> {f.ref_table}{f.ref_columns}"))
    for n in sorted(old_fk.keys() - new_fk.keys()):
        out.append(Change("presence", old.name, n, "fk dropped"))
    for n in sorted(old_fk.keys() & new_fk.keys()):
        a, b = old_fk[n], new_fk[n]
        if (a.columns, a.ref_table, a.ref_columns) != (b.columns, b.ref_table, b.ref_columns):
            out.append(Change("type", old.name, n, "fk target changed"))
        if a.on_delete != b.on_delete:
            out.append(Change("constraint", old.name, n,
                              f"fk on_delete {a.on_delete} -> {b.on_delete}"))
        if a.on_update != b.on_update:
            out.append(Change("constraint", old.name, n,
                              f"fk on_update {a.on_update} -> {b.on_update}"))
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
