"""FK-dependency graph utilities.

dependencies(schema, table) -> set[str]
    Direct parent tables that `table` references.

reverse_dependencies(schema, table) -> set[str]
    Tables that reference `table`.

topo_order(schema) -> list[str]
    Tables sorted so parents come before children; raises on cycles.
"""

from __future__ import annotations

from collections import defaultdict, deque

from .model import Schema


def dependencies(schema: Schema, table: str) -> set[str]:
    t = schema.table(table)
    if t is None:
        return set()
    return {fk.ref_table for fk in t.foreign_keys}


def reverse_dependencies(schema: Schema, table: str) -> set[str]:
    out: set[str] = set()
    for t in schema.tables:
        if any(fk.ref_table == table for fk in t.foreign_keys):
            out.add(t.name)
    return out


def topo_order(schema: Schema) -> list[str]:
    incoming: dict[str, set[str]] = defaultdict(set)
    nodes = [t.name for t in schema.tables]
    for t in schema.tables:
        for fk in t.foreign_keys:
            if fk.ref_table in {x.name for x in schema.tables} and fk.ref_table != t.name:
                incoming[t.name].add(fk.ref_table)
    queue: deque[str] = deque(n for n in nodes if not incoming[n])
    out: list[str] = []
    while queue:
        n = queue.popleft()
        out.append(n)
        for other in nodes:
            if n in incoming[other]:
                incoming[other].remove(n)
                if not incoming[other]:
                    queue.append(other)
    if len(out) != len(nodes):
        remaining = [n for n in nodes if n not in out]
        raise ValueError(f"FK cycle involving: {remaining}")
    return out
