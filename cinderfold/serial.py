"""Lossless JSON serialization for Schema (round-trip with model classes)."""

from __future__ import annotations

import json

from .model import Column, ForeignKey, Index, Schema, Table


def to_dict(schema: Schema) -> dict:
    return {"tables": [_table_to_dict(t) for t in schema.tables]}


def from_dict(doc: dict) -> Schema:
    return Schema(tuple(_table_from_dict(t) for t in doc.get("tables", [])))


def to_json(schema: Schema, indent: int | None = 2) -> str:
    return json.dumps(to_dict(schema), indent=indent)


def from_json(text: str) -> Schema:
    return from_dict(json.loads(text))


def _table_to_dict(t: Table) -> dict:
    return {
        "name": t.name,
        "columns": [_col_to_dict(c) for c in t.columns],
        "indexes": [_ix_to_dict(i) for i in t.indexes],
        "foreign_keys": [_fk_to_dict(f) for f in t.foreign_keys],
    }


def _col_to_dict(c: Column) -> dict:
    out: dict = {"name": c.name, "type": c.type}
    if c.pk:
        out["pk"] = True
    if not c.nullable:
        out["not_null"] = True
    if c.unique:
        out["unique"] = True
    if c.default is not None:
        out["default"] = c.default
    if c.comment is not None:
        out["comment"] = c.comment
    return out


def _ix_to_dict(i: Index) -> dict:
    out = {"name": i.name, "columns": list(i.columns)}
    if i.unique:
        out["unique"] = True
    return out


def _fk_to_dict(f: ForeignKey) -> dict:
    out: dict = {
        "name": f.name,
        "columns": list(f.columns),
        "ref_table": f.ref_table,
        "ref_columns": list(f.ref_columns),
    }
    if f.on_delete != "no_action":
        out["on_delete"] = f.on_delete
    if f.on_update != "no_action":
        out["on_update"] = f.on_update
    return out


def _table_from_dict(d: dict) -> Table:
    return Table(
        name=d["name"],
        columns=tuple(_col_from_dict(c) for c in d.get("columns", [])),
        indexes=tuple(_ix_from_dict(i) for i in d.get("indexes", [])),
        foreign_keys=tuple(_fk_from_dict(f) for f in d.get("foreign_keys", [])),
    )


def _col_from_dict(d: dict) -> Column:
    return Column(
        name=d["name"],
        type=d["type"],
        pk=d.get("pk", False),
        nullable=not d.get("not_null", False),
        unique=d.get("unique", False),
        default=d.get("default"),
        comment=d.get("comment"),
    )


def _ix_from_dict(d: dict) -> Index:
    return Index(name=d["name"], columns=tuple(d["columns"]), unique=d.get("unique", False))


def _fk_from_dict(d: dict) -> ForeignKey:
    return ForeignKey(
        name=d["name"],
        columns=tuple(d["columns"]),
        ref_table=d["ref_table"],
        ref_columns=tuple(d["ref_columns"]),
        on_delete=d.get("on_delete", "no_action"),
        on_update=d.get("on_update", "no_action"),
    )
