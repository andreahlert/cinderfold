from cinderfold.diff import diff
from cinderfold.parser import parse


def parse_one(text: str):
    return parse(text)


def test_added_table_is_presence():
    a = parse_one("table u { id: int pk not_null; }")
    b = parse_one("table u { id: int pk not_null; } table p { x: int; }")
    changes = diff(a, b)
    assert any(c.category == "presence" and c.table == "p" and c.detail == "table added" for c in changes)


def test_dropped_column_is_presence():
    a = parse_one("table u { id: int; nick: text; }")
    b = parse_one("table u { id: int; }")
    changes = diff(a, b)
    assert any(c.category == "presence" and c.column == "nick" and "dropped" in c.detail for c in changes)


def test_type_change_is_type_category():
    a = parse_one("table u { x: int; }")
    b = parse_one("table u { x: bigint; }")
    changes = diff(a, b)
    assert any(c.category == "type" and "int -> bigint" in c.detail for c in changes)


def test_nullability_flip_is_constraint():
    a = parse_one("table u { x: int; }")
    b = parse_one("table u { x: int not_null; }")
    changes = diff(a, b)
    assert any(c.category == "constraint" and "nullable" in c.detail for c in changes)


def test_default_change_is_auxiliary():
    a = parse_one("table u { x: int default = 0; }")
    b = parse_one("table u { x: int default = 1; }")
    changes = diff(a, b)
    assert any(c.category == "auxiliary" and "default" in c.detail for c in changes)


def test_sorted_by_severity_descending():
    a = parse_one("table u { x: int default = 0; y: int; }")
    b = parse_one("table u { x: int default = 1; y: bigint; } table p { z: int; }")
    changes = diff(a, b)
    sev = [c.severity for c in changes]
    assert sev == sorted(sev, reverse=True)
    # the table-added (presence) ranks first
    assert changes[0].category == "presence"


def test_no_changes_when_identical():
    a = parse_one("table u { x: int pk not_null; }")
    b = parse_one("table u { x: int pk not_null; }")
    assert diff(a, b) == []
