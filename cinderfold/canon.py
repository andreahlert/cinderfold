"""Canonicalize a Schema: sort tables, columns, indexes, foreign keys.

Two callers benefit:
- fingerprint: stable hash independent of declaration order.
- diff: reorder-agnostic comparison.

Note: cinderfold's diff already keys on names, so reorderings don't
produce spurious changes. canonicalize is useful when you want render
output to be deterministic or when migrating from a denormalized source.
"""

from __future__ import annotations

from .model import Schema, Table


def canonicalize(schema: Schema) -> Schema:
    tables = tuple(_canon_table(t) for t in sorted(schema.tables, key=lambda t: t.name))
    return Schema(tables=tables)


def _canon_table(t: Table) -> Table:
    cols = tuple(sorted(t.columns, key=lambda c: (not c.pk, c.name)))
    indexes = tuple(sorted(t.indexes, key=lambda i: i.name))
    fks = tuple(sorted(t.foreign_keys, key=lambda f: f.name))
    return Table(name=t.name, columns=cols, indexes=indexes, foreign_keys=fks)
