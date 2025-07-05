"""Static validation of a Schema.

Catches problems the parser cannot, because they only manifest when the
whole schema is considered:

- duplicate table names
- duplicate column names inside a table
- duplicate index/fk names inside a table
- foreign key referencing an unknown table or column
- index referencing an unknown column
- multiple primary keys on the same table
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Schema, Table


@dataclass(frozen=True)
class Issue:
    table: str
    detail: str


def validate(schema: Schema) -> list[Issue]:
    issues: list[Issue] = []

    seen: dict[str, int] = {}
    for t in schema.tables:
        seen[t.name] = seen.get(t.name, 0) + 1
    for name, count in seen.items():
        if count > 1:
            issues.append(Issue(name, f"duplicate table declared {count} times"))

    by_name = {t.name: t for t in schema.tables}

    for t in schema.tables:
        issues.extend(_validate_table(t, by_name))

    return issues


def _validate_table(t: Table, by_name: dict[str, Table]) -> list[Issue]:
    out: list[Issue] = []
    col_names = [c.name for c in t.columns]
    dupes = {n for n in col_names if col_names.count(n) > 1}
    for n in sorted(dupes):
        out.append(Issue(t.name, f"duplicate column {n!r}"))

    pks = [c.name for c in t.columns if c.pk]
    if len(pks) > 1:
        out.append(Issue(t.name, f"multiple primary keys: {pks}"))

    ix_names = [i.name for i in t.indexes]
    for n in {n for n in ix_names if ix_names.count(n) > 1}:
        out.append(Issue(t.name, f"duplicate index name {n!r}"))

    fk_names = [f.name for f in t.foreign_keys]
    for n in {n for n in fk_names if fk_names.count(n) > 1}:
        out.append(Issue(t.name, f"duplicate fk name {n!r}"))

    col_set = set(col_names)
    for i in t.indexes:
        missing = [c for c in i.columns if c not in col_set]
        if missing:
            out.append(Issue(t.name, f"index {i.name!r} references unknown column(s): {missing}"))

    for f in t.foreign_keys:
        missing = [c for c in f.columns if c not in col_set]
        if missing:
            out.append(Issue(t.name, f"fk {f.name!r} references unknown column(s): {missing}"))
        ref = by_name.get(f.ref_table)
        if ref is None:
            out.append(Issue(t.name, f"fk {f.name!r} references unknown table {f.ref_table!r}"))
            continue
        ref_cols = {c.name for c in ref.columns}
        bad = [c for c in f.ref_columns if c not in ref_cols]
        if bad:
            out.append(Issue(t.name,
                             f"fk {f.name!r} references unknown column(s) in {f.ref_table}: {bad}"))

    return out
