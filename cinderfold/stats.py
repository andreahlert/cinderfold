"""Aggregate counts and complexity metrics for a Schema.

Cheap to compute, useful as a one-line summary in CI logs and as the
basis for rough heuristics ("are these two snapshots even comparable?").
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Schema


@dataclass(frozen=True)
class Stats:
    tables: int
    columns: int
    pks: int
    indexes: int
    foreign_keys: int
    not_null_columns: int
    unique_columns: int

    @property
    def density(self) -> float:
        return self.columns / self.tables if self.tables else 0.0


def stats(schema: Schema) -> Stats:
    columns = sum(len(t.columns) for t in schema.tables)
    pks = sum(1 for t in schema.tables for c in t.columns if c.pk)
    indexes = sum(len(t.indexes) for t in schema.tables)
    fks = sum(len(t.foreign_keys) for t in schema.tables)
    nn = sum(1 for t in schema.tables for c in t.columns if not c.nullable)
    uq = sum(1 for t in schema.tables for c in t.columns if c.unique)
    return Stats(
        tables=len(schema.tables),
        columns=columns,
        pks=pks,
        indexes=indexes,
        foreign_keys=fks,
        not_null_columns=nn,
        unique_columns=uq,
    )
