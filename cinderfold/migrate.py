"""Generate DDL migration statements from an (old, new) Schema pair.

This is intentionally a low-magic emitter: it does not try to reorder
operations to satisfy FK dependencies, and it does not invent backfills
for NOT NULL additions. The output is meant to be reviewed.

Supported statements:
- CREATE TABLE / DROP TABLE
- ALTER TABLE ADD COLUMN / DROP COLUMN / ALTER COLUMN TYPE
- ALTER TABLE ALTER COLUMN SET/DROP NOT NULL
- CREATE/DROP INDEX
- ALTER TABLE ADD/DROP CONSTRAINT (FOREIGN KEY)
"""

from __future__ import annotations

from .graph import topo_order
from .model import Column, ForeignKey, Index, Schema, Table


def migrate(old: Schema, new: Schema) -> list[str]:
    out: list[str] = []
    old_tables = {t.name: t for t in old.tables}
    new_tables = {t.name: t for t in new.tables}

    for name in sorted(old_tables.keys() - new_tables.keys()):
        out.append(f"DROP TABLE {name};")

    added = new_tables.keys() - old_tables.keys()
    if added:
        try:
            order = [n for n in topo_order(new) if n in added]
        except ValueError:
            order = sorted(added)
        for name in order:
            out.append(_create_table(new_tables[name]))

    for name in sorted(old_tables.keys() & new_tables.keys()):
        out.extend(_alter(old_tables[name], new_tables[name]))

    return out


def _create_table(t: Table) -> str:
    parts = [_column_ddl(c) for c in t.columns]
    body = ",\n    ".join(parts)
    out = [f"CREATE TABLE {t.name} (\n    {body}\n);"]
    for i in t.indexes:
        out.append(_create_index(t.name, i))
    for f in t.foreign_keys:
        out.append(_add_fk(t.name, f))
    return "\n".join(out)


def _column_ddl(c: Column) -> str:
    bits = [c.name, c.type.upper()]
    if c.pk:
        bits.append("PRIMARY KEY")
    if not c.nullable and not c.pk:
        bits.append("NOT NULL")
    if c.unique and not c.pk:
        bits.append("UNIQUE")
    if c.default is not None:
        bits.append(f"DEFAULT {c.default}")
    return " ".join(bits)


def _create_index(table: str, i: Index) -> str:
    unique = "UNIQUE " if i.unique else ""
    cols = ", ".join(i.columns)
    return f"CREATE {unique}INDEX {i.name} ON {table} ({cols});"


def _add_fk(table: str, f: ForeignKey) -> str:
    cols = ", ".join(f.columns)
    ref = ", ".join(f.ref_columns)
    extras = []
    if f.on_delete != "no_action":
        extras.append(f"ON DELETE {f.on_delete.replace('_', ' ').upper()}")
    if f.on_update != "no_action":
        extras.append(f"ON UPDATE {f.on_update.replace('_', ' ').upper()}")
    tail = (" " + " ".join(extras)) if extras else ""
    return (f"ALTER TABLE {table} ADD CONSTRAINT {f.name} "
            f"FOREIGN KEY ({cols}) REFERENCES {f.ref_table} ({ref}){tail};")


def _alter(old: Table, new: Table) -> list[str]:
    out: list[str] = []
    old_cols = {c.name: c for c in old.columns}
    new_cols = {c.name: c for c in new.columns}

    for n in sorted(old_cols.keys() - new_cols.keys()):
        out.append(f"ALTER TABLE {old.name} DROP COLUMN {n};")

    for n in sorted(new_cols.keys() - old_cols.keys()):
        out.append(f"ALTER TABLE {old.name} ADD COLUMN {_column_ddl(new_cols[n])};")

    for n in sorted(old_cols.keys() & new_cols.keys()):
        a, b = old_cols[n], new_cols[n]
        if a.type != b.type:
            out.append(f"ALTER TABLE {old.name} ALTER COLUMN {n} TYPE {b.type.upper()};")
        if a.nullable != b.nullable:
            verb = "DROP" if b.nullable else "SET"
            out.append(f"ALTER TABLE {old.name} ALTER COLUMN {n} {verb} NOT NULL;")

    old_ix = {i.name: i for i in old.indexes}
    new_ix = {i.name: i for i in new.indexes}
    for n in sorted(old_ix.keys() - new_ix.keys()):
        out.append(f"DROP INDEX {n};")
    for n in sorted(new_ix.keys() - old_ix.keys()):
        out.append(_create_index(old.name, new_ix[n]))

    old_fk = {f.name: f for f in old.foreign_keys}
    new_fk = {f.name: f for f in new.foreign_keys}
    for n in sorted(old_fk.keys() - new_fk.keys()):
        out.append(f"ALTER TABLE {old.name} DROP CONSTRAINT {n};")
    for n in sorted(new_fk.keys() - old_fk.keys()):
        out.append(_add_fk(old.name, new_fk[n]))

    return out
