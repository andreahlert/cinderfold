"""Emit a Schema as SQL DDL (full CREATE TABLE for every table).

Companion to migrate: migrate is the *delta* path, dump is the *full*
path. Used to re-materialize the schema after parsing it through any of
the adapters (DSL, SQL, Postgres JSON, SQLite).
"""

from __future__ import annotations

from .migrate import _column_ddl, _create_index, _add_fk
from .model import Schema, Table


def dump_sql(schema: Schema) -> str:
    parts: list[str] = []
    for t in schema.tables:
        parts.append(_dump_table(t))
    return "\n\n".join(parts) + "\n"


def _dump_table(t: Table) -> str:
    cols = ",\n    ".join(_column_ddl(c) for c in t.columns)
    out = [f"CREATE TABLE {t.name} (\n    {cols}\n);"]
    for i in t.indexes:
        out.append(_create_index(t.name, i))
    for f in t.foreign_keys:
        out.append(_add_fk(t.name, f))
    return "\n".join(out)
