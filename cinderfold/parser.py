"""Tiny schema DSL.

Grammar:
    schema := table*
    table  := "table" IDENT "{" entry* "}"
    entry  := column | index | fkey
    column := IDENT ":" TYPE attr* ";"
    attr   := "pk" | "nullable" | "not_null" | "unique"
            | "default" "=" VALUE
            | "comment" "=" STRING
    index  := "index" IDENT "(" IDENT ("," IDENT)* ")" ["unique"] ";"
    fkey   := "fk" IDENT "(" IDENT ("," IDENT)* ")"
              "->" IDENT "(" IDENT ("," IDENT)* ")"
              ("on_delete" "=" IDENT)? ("on_update" "=" IDENT)? ";"

Example:

    table users {
        id: int pk not_null;
        email: text not_null unique;
        created_at: timestamp default = now() comment = "row birth";
        index ix_users_email (email) unique;
    }

    table orders {
        id: int pk not_null;
        user_id: int not_null;
        fk fk_orders_user (user_id) -> users (id) on_delete = cascade;
    }
"""

from __future__ import annotations

import re

from .model import Column, ForeignKey, Index, Schema, Table


_TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
    | (?P<comment>//[^\n]*)
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<arrow>->)
    | (?P<symbol>[{}():,;=])
    | (?P<number>-?\d+(?:\.\d+)?)
    | (?P<word>[A-Za-z_][\w.()]*)
    """,
    re.VERBOSE,
)


class ParseError(Exception):
    pass


def _tokenize(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise ParseError(f"lex error at {text[pos:pos+20]!r}")
        pos = m.end()
        if m.group("ws") or m.group("comment"):
            continue
        if m.group("string") is not None:
            tokens.append(("STRING", m.group("string")[1:-1]))
        elif m.group("arrow"):
            tokens.append(("ARROW", "->"))
        elif m.group("symbol"):
            tokens.append(("SYM", m.group("symbol")))
        elif m.group("number"):
            tokens.append(("NUMBER", m.group("number")))
        elif m.group("word"):
            tokens.append(("WORD", m.group("word")))
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self, off=0):
        idx = self.i + off
        return self.tokens[idx] if idx < len(self.tokens) else (None, None)

    def eat(self, kind, value=None):
        k, v = self.peek()
        if k != kind or (value is not None and v != value):
            raise ParseError(f"expected {kind} {value!r}, got {k} {v!r} at pos {self.i}")
        self.i += 1
        return v

    def at_end(self):
        return self.i >= len(self.tokens)


def parse(text: str) -> Schema:
    p = _Parser(_tokenize(text))
    tables: list[Table] = []
    while not p.at_end():
        p.eat("WORD", "table")
        name = p.eat("WORD")
        p.eat("SYM", "{")
        cols: list[Column] = []
        indexes: list[Index] = []
        fks: list[ForeignKey] = []
        while not (p.peek() == ("SYM", "}")):
            kind, value = p.peek()
            if kind == "WORD" and value == "index":
                indexes.append(_parse_index(p))
            elif kind == "WORD" and value == "fk":
                fks.append(_parse_fkey(p))
            else:
                cols.append(_parse_column(p))
        p.eat("SYM", "}")
        tables.append(Table(name=name, columns=tuple(cols),
                            indexes=tuple(indexes), foreign_keys=tuple(fks)))
    return Schema(tables=tuple(tables))


def _parse_ident_list(p: _Parser) -> tuple[str, ...]:
    p.eat("SYM", "(")
    out: list[str] = [p.eat("WORD")]
    while p.peek() == ("SYM", ","):
        p.eat("SYM", ",")
        out.append(p.eat("WORD"))
    p.eat("SYM", ")")
    return tuple(out)


def _parse_index(p: _Parser) -> Index:
    p.eat("WORD", "index")
    name = p.eat("WORD")
    cols = _parse_ident_list(p)
    unique = False
    if p.peek() == ("WORD", "unique"):
        p.eat("WORD"); unique = True
    p.eat("SYM", ";")
    return Index(name=name, columns=cols, unique=unique)


def _parse_fkey(p: _Parser) -> ForeignKey:
    p.eat("WORD", "fk")
    name = p.eat("WORD")
    cols = _parse_ident_list(p)
    p.eat("ARROW")
    ref_table = p.eat("WORD")
    ref_cols = _parse_ident_list(p)
    on_delete = "no_action"
    on_update = "no_action"
    while p.peek() != ("SYM", ";"):
        k, v = p.peek()
        if k == "WORD" and v == "on_delete":
            p.eat("WORD"); p.eat("SYM", "=")
            on_delete = p.eat("WORD")
        elif k == "WORD" and v == "on_update":
            p.eat("WORD"); p.eat("SYM", "=")
            on_update = p.eat("WORD")
        else:
            raise ParseError(f"unexpected fk attr {k} {v!r}")
    p.eat("SYM", ";")
    return ForeignKey(name=name, columns=cols, ref_table=ref_table,
                      ref_columns=ref_cols, on_delete=on_delete,
                      on_update=on_update)


def _parse_column(p: _Parser) -> Column:
    col_name = p.eat("WORD")
    p.eat("SYM", ":")
    col_type = p.eat("WORD")
    pk = False
    nullable = True
    unique = False
    default: str | None = None
    comment: str | None = None
    while p.peek() != ("SYM", ";"):
        k, v = p.peek()
        if k == "WORD" and v == "pk":
            p.eat("WORD"); pk = True
        elif k == "WORD" and v == "nullable":
            p.eat("WORD"); nullable = True
        elif k == "WORD" and v == "not_null":
            p.eat("WORD"); nullable = False
        elif k == "WORD" and v == "unique":
            p.eat("WORD"); unique = True
        elif k == "WORD" and v == "default":
            p.eat("WORD"); p.eat("SYM", "=")
            tk, tv = p.peek()
            if tk in ("WORD", "STRING", "NUMBER"):
                default = tv
                p.i += 1
            else:
                raise ParseError(f"bad default value at pos {p.i}")
        elif k == "WORD" and v == "comment":
            p.eat("WORD"); p.eat("SYM", "=")
            comment = p.eat("STRING")
        else:
            raise ParseError(f"unexpected attribute {k} {v!r}")
    p.eat("SYM", ";")
    return Column(name=col_name, type=col_type, pk=pk, nullable=nullable,
                  unique=unique, default=default, comment=comment)
