from cinderfold.diff import diff
from cinderfold.parser import parse
from cinderfold.rename import detect_renames


def test_table_rename_detected():
    old = parse("table users { id: int pk not_null; email: text not_null; }")
    new = parse("table accounts { id: int pk not_null; email: text not_null; }")
    hints, rest = detect_renames(old, new, diff(old, new))
    assert any(h.kind == "table" and h.old == "users" and h.new == "accounts" for h in hints)
    assert not any("table added" in c.detail or "table dropped" in c.detail for c in rest)


def test_column_rename_detected():
    old = parse("table u { id: int pk not_null; email: text not_null; }")
    new = parse("table u { id: int pk not_null; mail: text not_null; }")
    hints, rest = detect_renames(old, new, diff(old, new))
    assert any(h.kind == "column" and h.old == "email" and h.new == "mail" for h in hints)
    assert not any("column added" in c.detail or "column dropped" in c.detail for c in rest)


def test_ambiguous_rename_not_taken():
    old = parse("table u { id: int pk not_null; a: text not_null; }")
    new = parse("table u { id: int pk not_null; b: text not_null; c: text not_null; }")
    hints, rest = detect_renames(old, new, diff(old, new))
    assert not any(h.kind == "column" for h in hints)


def test_no_rename_when_types_differ():
    old = parse("table u { id: int pk not_null; email: text not_null; }")
    new = parse("table u { id: int pk not_null; mail: int not_null; }")
    hints, _ = detect_renames(old, new, diff(old, new))
    assert hints == []
