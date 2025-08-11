from cinderfold.canon import canonicalize
from cinderfold.fingerprint import fingerprint
from cinderfold.parser import parse


def test_table_order_normalized():
    a = parse("table b { id: int pk not_null; } table a { id: int pk not_null; }")
    c = canonicalize(a)
    assert [t.name for t in c.tables] == ["a", "b"]


def test_column_order_pk_first_then_alpha():
    s = parse("table u { name: text; id: int pk not_null; email: text; }")
    c = canonicalize(s)
    assert [col.name for col in c.table("u").columns] == ["id", "email", "name"]


def test_canon_makes_fingerprint_stable_across_orderings():
    a = parse("table u { id: int pk not_null; b: text; a: text; }")
    b = parse("table u { id: int pk not_null; a: text; b: text; }")
    assert fingerprint(canonicalize(a)) == fingerprint(canonicalize(b))


def test_indexes_sorted():
    s = parse("""
        table u {
            id: int pk not_null;
            a: text;
            b: text;
            index zb (b);
            index aa (a);
        }
    """)
    c = canonicalize(s)
    assert [i.name for i in c.table("u").indexes] == ["aa", "zb"]
