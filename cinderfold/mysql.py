"""MySQL DDL emitter.

Differences from the default Postgres-flavored emitter in `migrate.py`:
- identifiers are quoted with backticks
- CREATE TABLE gets a trailing `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`
- AUTO_INCREMENT is emitted for `pk` columns of type int/bigint
- DROP CONSTRAINT becomes DROP FOREIGN KEY

This module emits a single full DDL dump for a target schema. It is not
a migration generator; use `migrate.migrate` for that and translate
identifiers downstream if needed.
"""

from __future__ import annotations

from .model import Column, ForeignKey, Index, Schema, Table


ENGINE_SUFFIX = " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"


def dump_mysql(schema: Schema) -> str:
    parts: list[str] = []
    for t in schema.tables:
        parts.append(_create_table(t))
    return "\n\n".join(parts)


def _q(ident: str) -> str:
    return f"`{ident}`"


def _create_table(t: Table) -> str:
    body_lines = [f"    {_column_ddl(c)}" for c in t.columns]
    body_lines.extend(f"    {_inline_index(i)}" for i in t.indexes)
    body_lines.extend(f"    {_inline_fk(f)}" for f in t.foreign_keys)
    body = ",\n".join(body_lines)
    return f"CREATE TABLE {_q(t.name)} (\n{body}\n){ENGINE_SUFFIX};"


def _column_ddl(c: Column) -> str:
    bits = [_q(c.name), c.type.upper()]
    if not c.nullable:
        bits.append("NOT NULL")
    if c.pk and c.type.lower() in {"int", "integer", "bigint", "smallint"}:
        bits.append("AUTO_INCREMENT")
    if c.pk:
        bits.append("PRIMARY KEY")
    if c.unique and not c.pk:
        bits.append("UNIQUE")
    if c.default is not None:
        bits.append(f"DEFAULT {c.default}")
    if c.comment is not None:
        escaped = c.comment.replace("'", "''")
        bits.append(f"COMMENT '{escaped}'")
    return " ".join(bits)


def _inline_index(i: Index) -> str:
    unique = "UNIQUE " if i.unique else ""
    cols = ", ".join(_q(c) for c in i.columns)
    return f"{unique}KEY {_q(i.name)} ({cols})"


def _inline_fk(f: ForeignKey) -> str:
    cols = ", ".join(_q(c) for c in f.columns)
    ref = ", ".join(_q(c) for c in f.ref_columns)
    extras = []
    if f.on_delete != "no_action":
        extras.append(f"ON DELETE {f.on_delete.replace('_', ' ').upper()}")
    if f.on_update != "no_action":
        extras.append(f"ON UPDATE {f.on_update.replace('_', ' ').upper()}")
    tail = (" " + " ".join(extras)) if extras else ""
    return (f"CONSTRAINT {_q(f.name)} FOREIGN KEY ({cols}) "
            f"REFERENCES {_q(f.ref_table)} ({ref}){tail}")
