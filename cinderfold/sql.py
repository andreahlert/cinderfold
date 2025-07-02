"""Adapter: parse a CREATE TABLE statement subset into the schema model.

Supports the common SQL dialect intersection:

    CREATE TABLE name (
        col TYPE [NOT NULL] [PRIMARY KEY] [UNIQUE] [DEFAULT value],
        PRIMARY KEY (cols...),
        UNIQUE (cols...),
        FOREIGN KEY (cols) REFERENCES tbl (cols) [ON DELETE action] [ON UPDATE action]
    );

This is intentionally narrow. Production parsers use sqlglot or similar;
here we want a small, dependency-free path that's easy to reason about.
"""

from __future__ import annotations

import re

from .model import Column, ForeignKey, Schema, Table


_CREATE = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(", re.I)


def parse_sql(text: str) -> Schema:
    tables: list[Table] = []
    pos = 0
    while True:
        m = _CREATE.search(text, pos)
        if not m:
            break
        name = m.group(1)
        body, end = _take_balanced(text, m.end() - 1)
        pos = end
        tables.append(_parse_table(name, body))
    return Schema(tables=tuple(tables))


def _take_balanced(text: str, open_idx: int) -> tuple[str, int]:
    depth = 0
    i = open_idx
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i], i + 1
        i += 1
    raise ValueError("unterminated CREATE TABLE body")


def _split_top_level(body: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for c in body:
        if c == "(":
            depth += 1
            buf.append(c)
        elif c == ")":
            depth -= 1
            buf.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
    if buf:
        last = "".join(buf).strip()
        if last:
            parts.append(last)
    return parts


def _parse_table(name: str, body: str) -> Table:
    cols: list[Column] = []
    fks: list[ForeignKey] = []
    pk_cols: list[str] = []
    unique_groups: list[list[str]] = []

    for part in _split_top_level(body):
        head = part.split(None, 1)[0].upper() if part.split() else ""
        if head == "PRIMARY":
            inside = part[part.index("(") + 1:part.rindex(")")]
            pk_cols = [c.strip() for c in inside.split(",")]
        elif head == "UNIQUE":
            inside = part[part.index("(") + 1:part.rindex(")")]
            unique_groups.append([c.strip() for c in inside.split(",")])
        elif head in ("FOREIGN", "FK"):
            fks.append(_parse_fk(part))
        else:
            cols.append(_parse_column(part))

    if pk_cols:
        cols = [Column(**{**c.__dict__, "pk": c.name in pk_cols or c.pk}) for c in cols]
    if unique_groups:
        flat = {c for grp in unique_groups for c in grp}
        cols = [Column(**{**c.__dict__, "unique": c.name in flat or c.unique}) for c in cols]
    return Table(name=name, columns=tuple(cols), foreign_keys=tuple(fks))


def _parse_column(part: str) -> Column:
    toks = part.split()
    name = toks[0]
    type_ = toks[1]
    rest_raw = " ".join(toks[2:])
    rest_up = rest_raw.upper()
    pk = "PRIMARY KEY" in rest_up
    nullable = "NOT NULL" not in rest_up
    unique = "UNIQUE" in rest_up
    default = None
    m = re.search(r"DEFAULT\s+([^\s,]+(?:\([^)]*\))?)", rest_raw, re.I)
    if m:
        default = m.group(1)
    return Column(name=name, type=type_, pk=pk, nullable=nullable,
                  unique=unique, default=default)


_FK = re.compile(
    r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)"
    r"(?:\s+ON\s+DELETE\s+(\w+))?(?:\s+ON\s+UPDATE\s+(\w+))?",
    re.I,
)


def _parse_fk(part: str) -> ForeignKey:
    m = _FK.search(part)
    if not m:
        raise ValueError(f"cannot parse FK: {part!r}")
    cols = tuple(c.strip() for c in m.group(1).split(","))
    ref_table = m.group(2)
    ref_cols = tuple(c.strip() for c in m.group(3).split(","))
    on_delete = (m.group(4) or "no_action").lower()
    on_update = (m.group(5) or "no_action").lower()
    return ForeignKey(name=f"fk_{ref_table}", columns=cols, ref_table=ref_table,
                      ref_columns=ref_cols, on_delete=on_delete, on_update=on_update)
