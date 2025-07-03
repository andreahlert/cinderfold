"""Render a Schema back into the DSL form (round-tripper)."""

from __future__ import annotations

from .model import Column, ForeignKey, Index, Schema, Table


def render(schema: Schema) -> str:
    return "\n\n".join(_render_table(t) for t in schema.tables) + "\n"


def _render_table(t: Table) -> str:
    lines = [f"table {t.name} {{"]
    for c in t.columns:
        lines.append("    " + _render_column(c))
    for i in t.indexes:
        lines.append("    " + _render_index(i))
    for f in t.foreign_keys:
        lines.append("    " + _render_fk(f))
    lines.append("}")
    return "\n".join(lines)


def _render_column(c: Column) -> str:
    attrs = []
    if c.pk:
        attrs.append("pk")
    if not c.nullable:
        attrs.append("not_null")
    if c.unique:
        attrs.append("unique")
    if c.default is not None:
        attrs.append(f"default = {c.default}")
    if c.comment:
        attrs.append(f'comment = "{c.comment}"')
    suffix = (" " + " ".join(attrs)) if attrs else ""
    return f"{c.name}: {c.type}{suffix};"


def _render_index(i: Index) -> str:
    cols = ", ".join(i.columns)
    unique = " unique" if i.unique else ""
    return f"index {i.name} ({cols}){unique};"


def _render_fk(f: ForeignKey) -> str:
    cols = ", ".join(f.columns)
    ref = ", ".join(f.ref_columns)
    extras = []
    if f.on_delete != "no_action":
        extras.append(f"on_delete = {f.on_delete}")
    if f.on_update != "no_action":
        extras.append(f"on_update = {f.on_update}")
    suffix = (" " + " ".join(extras)) if extras else ""
    return f"fk {f.name} ({cols}) -> {f.ref_table} ({ref}){suffix};"
