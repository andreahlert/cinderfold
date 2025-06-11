"""Apply random mutations to a schema for evaluation.

Each mutation is one of:
    add_column, drop_column, change_type, flip_nullable,
    flip_unique, change_default, change_comment, add_table, drop_table

Returns the mutated schema and the ground-truth list of (category, table,
column, detail) tuples describing what changed. The detector should
recover the same set.
"""

from __future__ import annotations

import random
from dataclasses import replace

from cinderfold.model import Column, Schema, Table


TYPES = ["int", "bigint", "text", "varchar", "timestamp", "boolean", "decimal"]


def _replace_column(table: Table, name: str, new: Column) -> Table:
    cols = tuple(new if c.name == name else c for c in table.columns)
    return Table(name=table.name, columns=cols)


def _drop_column(table: Table, name: str) -> Table:
    return Table(name=table.name, columns=tuple(c for c in table.columns if c.name != name))


def _add_column(table: Table, col: Column) -> Table:
    return Table(name=table.name, columns=table.columns + (col,))


def mutate(schema: Schema, n_mutations: int, rng: random.Random) -> tuple[Schema, list[tuple]]:
    truth: list[tuple] = []
    tables = list(schema.tables)
    applied = 0
    guard = 0
    while applied < n_mutations and guard < n_mutations * 10:
        guard += 1
        kind = rng.choice([
            "add_column", "drop_column", "change_type",
            "flip_nullable", "flip_unique",
            "change_default", "change_comment",
            "add_table", "drop_table",
        ])
        try:
            if kind == "add_table":
                tname = f"t_added_{rng.randrange(10**6)}"
                new_t = Table(name=tname, columns=(Column(name="id", type="int", pk=True, nullable=False),))
                tables.append(new_t)
                truth.append(("presence", tname, None, "table added"))
            elif kind == "drop_table" and len(tables) > 1:
                idx = rng.randrange(len(tables))
                gone = tables.pop(idx)
                truth.append(("presence", gone.name, None, "table dropped"))
            elif kind == "add_column":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                cname = f"c_added_{rng.randrange(10**6)}"
                new_col = Column(name=cname, type=rng.choice(TYPES))
                tables[idx] = _add_column(tbl, new_col)
                truth.append(("presence", tbl.name, cname, "column added"))
            elif kind == "drop_column":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                if len(tbl.columns) <= 1:
                    continue
                col = rng.choice(tbl.columns)
                tables[idx] = _drop_column(tbl, col.name)
                truth.append(("presence", tbl.name, col.name, "column dropped"))
            elif kind == "change_type":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                col = rng.choice(tbl.columns)
                new_type = rng.choice([t for t in TYPES if t != col.type])
                tables[idx] = _replace_column(tbl, col.name, replace(col, type=new_type))
                truth.append(("type", tbl.name, col.name, f"type {col.type} -> {new_type}"))
            elif kind == "flip_nullable":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                col = rng.choice(tbl.columns)
                new_n = not col.nullable
                tables[idx] = _replace_column(tbl, col.name, replace(col, nullable=new_n))
                truth.append(("constraint", tbl.name, col.name, f"nullable {col.nullable} -> {new_n}"))
            elif kind == "flip_unique":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                col = rng.choice(tbl.columns)
                new_u = not col.unique
                tables[idx] = _replace_column(tbl, col.name, replace(col, unique=new_u))
                truth.append(("constraint", tbl.name, col.name, f"unique {col.unique} -> {new_u}"))
            elif kind == "change_default":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                col = rng.choice(tbl.columns)
                new_d = str(rng.randint(0, 100))
                if new_d == col.default:
                    continue
                tables[idx] = _replace_column(tbl, col.name, replace(col, default=new_d))
                truth.append(("auxiliary", tbl.name, col.name, f"default {col.default!r} -> {new_d!r}"))
            elif kind == "change_comment":
                idx = rng.randrange(len(tables))
                tbl = tables[idx]
                col = rng.choice(tbl.columns)
                new_c = f"v{rng.randrange(10**6)}"
                if new_c == col.comment:
                    continue
                tables[idx] = _replace_column(tbl, col.name, replace(col, comment=new_c))
                truth.append(("auxiliary", tbl.name, col.name, f"comment {col.comment!r} -> {new_c!r}"))
            else:
                continue
            applied += 1
        except (ValueError, IndexError):
            continue
    return Schema(tables=tuple(tables)), truth
