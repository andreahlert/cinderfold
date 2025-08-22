from pathlib import Path

from cinderfold.dot import to_dot
from cinderfold.parser import parse


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def test_dot_has_digraph_header():
    s = parse("table u { id: int pk not_null; }")
    out = to_dot(s)
    assert out.startswith("digraph schema {")
    assert out.rstrip().endswith("}")


def test_dot_emits_arrow_per_fk():
    s = parse((FIX / "blog_v1.dsl").read_text())
    out = to_dot(s)
    assert "posts -> users" in out
    assert "comments -> posts" in out


def test_dot_marks_pk_and_not_null():
    s = parse("table u { id: int pk not_null; e: text not_null; n: text; }")
    out = to_dot(s)
    assert "*id" in out
    assert "!e" in out
    assert "|n: text" in out


def test_dot_custom_name():
    s = parse("table u { id: int pk not_null; }")
    out = to_dot(s, name="mydb")
    assert out.startswith("digraph mydb {")
