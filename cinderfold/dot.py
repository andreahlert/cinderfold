"""Emit a Graphviz DOT graph for a Schema.

Each table becomes a record node; each foreign key becomes an arrow
from child to parent. Useful for embedding a quick ERD into PR comments
or static site builds.

Use `dot -Tsvg schema.dot > schema.svg` to render.
"""

from __future__ import annotations

from .model import Schema, Table


def to_dot(schema: Schema, name: str = "schema") -> str:
    out = [f"digraph {name} {{", "  rankdir=LR;",
           "  node [shape=record, fontname=\"Helvetica\"];"]
    for t in schema.tables:
        out.append(_table_node(t))
    for t in schema.tables:
        for fk in t.foreign_keys:
            out.append(f'  {t.name} -> {fk.ref_table} '
                       f'[label="{",".join(fk.columns)}"];')
    out.append("}")
    return "\n".join(out) + "\n"


def _table_node(t: Table) -> str:
    rows = [t.name]
    for c in t.columns:
        marker = "*" if c.pk else ("!" if not c.nullable else "")
        rows.append(f"{marker}{c.name}: {c.type}")
    label = "|".join(rows).replace("<", "\\<").replace(">", "\\>")
    return f'  {t.name} [label="{label}"];'
