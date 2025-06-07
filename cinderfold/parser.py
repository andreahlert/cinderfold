"""Tiny schema DSL.

Grammar:
    schema := table*
    table  := "table" IDENT "{" column* "}"
    column := IDENT ":" TYPE attr* ";"
    attr   := "pk" | "nullable" | "not_null" | "unique"
            | "default" "=" VALUE
            | "comment" "=" STRING

Example:

    table users {
        id: int pk not_null;
        email: text not_null unique;
        created_at: timestamp default = now() comment = "row birth";
    }
"""

from __future__ import annotations

import re

from .model import Column, Schema, Table


_TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
    | (?P<comment>//[^\n]*)
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<symbol>[{}:;=])
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
        while not (p.peek() == ("SYM", "}")):
            cols.append(_parse_column(p))
        p.eat("SYM", "}")
        tables.append(Table(name=name, columns=tuple(cols)))
    return Schema(tables=tuple(tables))


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
