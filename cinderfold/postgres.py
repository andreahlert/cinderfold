"""Adapter: convert a Postgres information_schema dump (as JSON) to a Schema.

The expected JSON shape comes from running:

    SELECT json_build_object(
      'tables', json_agg(json_build_object(
         'name', table_name,
         'columns', cols,
         'foreign_keys', fks
      ))
    ) FROM ...

For convenience, we accept a permissive shape: a top-level list of tables,
each with `name`, `columns: [{name, type, nullable, default, pk, unique}]`,
and optionally `foreign_keys`, `indexes`. Nothing is queried live; this is
an offline transform.
"""

from __future__ import annotations

from typing import Any

from .model import Column, ForeignKey, Index, Schema, Table


def from_information_schema(payload: Any) -> Schema:
    tables_raw = payload["tables"] if isinstance(payload, dict) else payload
    tables: list[Table] = []
    for t in tables_raw:
        cols = tuple(_column_from(c) for c in t.get("columns", []))
        fks = tuple(_fk_from(f) for f in t.get("foreign_keys", []))
        ixs = tuple(_index_from(i) for i in t.get("indexes", []))
        tables.append(Table(name=t["name"], columns=cols,
                            indexes=ixs, foreign_keys=fks))
    return Schema(tables=tuple(tables))


def _column_from(d: dict) -> Column:
    return Column(
        name=d["name"],
        type=d["type"],
        pk=bool(d.get("pk", False)),
        nullable=bool(d.get("nullable", True)),
        unique=bool(d.get("unique", False)),
        default=d.get("default"),
        comment=d.get("comment"),
    )


def _fk_from(d: dict) -> ForeignKey:
    return ForeignKey(
        name=d["name"],
        columns=tuple(d["columns"]),
        ref_table=d["ref_table"],
        ref_columns=tuple(d["ref_columns"]),
        on_delete=d.get("on_delete", "no_action"),
        on_update=d.get("on_update", "no_action"),
    )


def _index_from(d: dict) -> Index:
    return Index(
        name=d["name"],
        columns=tuple(d["columns"]),
        unique=bool(d.get("unique", False)),
    )
