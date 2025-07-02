"""Adapter: parse SQLite `.schema` output (a sequence of CREATE TABLE / CREATE INDEX).

Reuses the generic SQL parser for CREATE TABLE and adds a small handler for
`CREATE [UNIQUE] INDEX name ON table (cols)`.
"""

from __future__ import annotations

import re

from .model import Column, ForeignKey, Index, Schema, Table
from .sql import parse_sql


_INDEX_RE = re.compile(
    r"CREATE\s+(UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)",
    re.I,
)


def parse_dotschema(text: str) -> Schema:
    schema = parse_sql(text)
    indexes_by_table: dict[str, list[Index]] = {}
    for m in _INDEX_RE.finditer(text):
        unique = bool(m.group(1))
        name = m.group(2)
        table = m.group(3)
        cols = tuple(c.strip() for c in m.group(4).split(","))
        indexes_by_table.setdefault(table, []).append(
            Index(name=name, columns=cols, unique=unique)
        )
    tables = tuple(
        Table(name=t.name, columns=t.columns,
              indexes=tuple(indexes_by_table.get(t.name, t.indexes)),
              foreign_keys=t.foreign_keys)
        for t in schema.tables
    )
    return Schema(tables=tables)
