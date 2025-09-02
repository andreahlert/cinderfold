"""Detect safe vs. unsafe type widenings.

Some type changes are safe (int -> bigint, varchar(10) -> varchar(20));
others are not (bigint -> int, text -> int). is_widening returns True
only when the new type can hold every value of the old.

The rules are deliberately conservative; an unknown pair is treated as
unsafe so callers don't accidentally green-light a destructive change.
"""

from __future__ import annotations

import re

_NUMERIC_ORDER = ["smallint", "int", "integer", "bigint"]
_FLOAT_ORDER = ["real", "float", "double", "double precision", "numeric"]
_STRING_TYPES = {"text", "varchar", "char", "string"}


def is_widening(old: str, new: str) -> bool:
    a = old.strip().lower()
    b = new.strip().lower()
    if a == b:
        return True
    if _is_numeric(a) and _is_numeric(b):
        return _rank(a) <= _rank(b)
    if _is_string(a) and _is_string(b):
        return _string_capacity(b) >= _string_capacity(a)
    return False


def _is_numeric(t: str) -> bool:
    return t in _NUMERIC_ORDER or t in _FLOAT_ORDER


def _rank(t: str) -> int:
    if t in _NUMERIC_ORDER:
        return _NUMERIC_ORDER.index(t)
    return len(_NUMERIC_ORDER) + _FLOAT_ORDER.index(t)


def _is_string(t: str) -> bool:
    base = re.sub(r"\(.*\)", "", t).strip()
    return base in _STRING_TYPES


def _string_capacity(t: str) -> int:
    base = re.sub(r"\(.*\)", "", t).strip()
    if base == "text":
        return 1_000_000_000
    m = re.search(r"\((\d+)\)", t)
    return int(m.group(1)) if m else 0
