"""Schema data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    pk: bool = False
    nullable: bool = True
    unique: bool = False
    default: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class Index:
    name: str
    columns: tuple[str, ...]
    unique: bool = False


@dataclass(frozen=True)
class ForeignKey:
    name: str
    columns: tuple[str, ...]
    ref_table: str
    ref_columns: tuple[str, ...]
    on_delete: str = "no_action"
    on_update: str = "no_action"


@dataclass(frozen=True)
class Table:
    name: str
    columns: tuple[Column, ...]
    indexes: tuple[Index, ...] = ()
    foreign_keys: tuple[ForeignKey, ...] = ()

    def column(self, name: str) -> Column | None:
        for c in self.columns:
            if c.name == name:
                return c
        return None

    def index(self, name: str) -> Index | None:
        for i in self.indexes:
            if i.name == name:
                return i
        return None


@dataclass(frozen=True)
class Schema:
    tables: tuple[Table, ...]

    def table(self, name: str) -> Table | None:
        for t in self.tables:
            if t.name == name:
                return t
        return None
