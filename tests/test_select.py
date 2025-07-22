import pytest

from cinderfold.parser import parse
from cinderfold.select import exclude, merge, select


SRC = """
table users { id: int pk not_null; }
table posts { id: int pk not_null; }
table audit_log { id: int pk not_null; }
table audit_history { id: int pk not_null; }
"""


def test_select_glob():
    s = parse(SRC)
    got = select(s, ["audit_*"])
    assert {t.name for t in got.tables} == {"audit_log", "audit_history"}


def test_select_multiple_patterns():
    s = parse(SRC)
    got = select(s, ["users", "audit_log"])
    assert {t.name for t in got.tables} == {"users", "audit_log"}


def test_exclude():
    s = parse(SRC)
    got = exclude(s, ["audit_*"])
    assert {t.name for t in got.tables} == {"users", "posts"}


def test_merge_disjoint():
    a = parse("table a { id: int pk not_null; }")
    b = parse("table b { id: int pk not_null; }")
    out = merge(a, b)
    assert {t.name for t in out.tables} == {"a", "b"}


def test_merge_duplicate_raises():
    a = parse("table a { id: int pk not_null; }")
    b = parse("table a { id: int pk not_null; }")
    with pytest.raises(ValueError, match="duplicate"):
        merge(a, b)
