import pytest

from cinderfold.parser import parse, ParseError


def test_parse_simple_table():
    s = parse("""
        table users {
            id: int pk not_null;
            email: text not_null unique;
        }
    """)
    assert len(s.tables) == 1
    t = s.tables[0]
    assert t.name == "users"
    assert len(t.columns) == 2
    id_col = t.column("id")
    assert id_col.type == "int"
    assert id_col.pk is True
    assert id_col.nullable is False


def test_parse_default_and_comment():
    s = parse("""
        table events {
            created_at: timestamp default = now() comment = "row birth";
        }
    """)
    c = s.tables[0].column("created_at")
    assert c.default == "now()"
    assert c.comment == "row birth"


def test_parse_multiple_tables():
    s = parse("""
        table a { x: int; }
        table b { y: text; }
    """)
    assert [t.name for t in s.tables] == ["a", "b"]


def test_parse_comments_ignored():
    s = parse("""
        // top-level comment
        table u { id: int pk not_null; } // trailing
    """)
    assert s.tables[0].name == "u"


def test_parse_error_on_missing_semicolon():
    with pytest.raises(ParseError):
        parse("table u { id: int pk }")


def test_parse_error_on_unknown_attr():
    with pytest.raises(ParseError):
        parse("table u { id: int wat; }")
