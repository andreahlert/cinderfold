from cinderfold.parser import parse


def test_table_lookup_returns_none_on_miss():
    s = parse("table u { id: int pk not_null; }")
    assert s.table("nope") is None


def test_column_lookup_returns_none_on_miss():
    s = parse("table u { id: int pk not_null; }")
    assert s.table("u").column("nope") is None


def test_index_lookup():
    s = parse("table u { id: int pk not_null; e: text; index ix_e (e); }")
    assert s.table("u").index("ix_e") is not None
    assert s.table("u").index("nope") is None


def test_table_equality():
    a = parse("table u { id: int pk not_null; }")
    b = parse("table u { id: int pk not_null; }")
    assert a == b


def test_table_inequality_on_column_add():
    a = parse("table u { id: int pk not_null; }")
    b = parse("table u { id: int pk not_null; x: text; }")
    assert a != b
