from cinderfold.compat import compatible
from cinderfold.parser import parse


def test_added_column_is_compatible():
    a = parse("table u { id: int pk not_null; }")
    b = parse("table u { id: int pk not_null; e: text; }")
    ok, reasons = compatible(a, b)
    assert ok and reasons == []


def test_added_default_is_compatible():
    a = parse("table u { id: int pk not_null; n: text; }")
    b = parse("table u { id: int pk not_null; n: text default = 'x'; }")
    ok, _ = compatible(a, b)
    assert ok


def test_dropped_column_breaks():
    a = parse("table u { id: int pk not_null; e: text; }")
    b = parse("table u { id: int pk not_null; }")
    ok, reasons = compatible(a, b)
    assert not ok
    assert any("dropped" in r for r in reasons)


def test_type_change_breaks():
    a = parse("table u { id: int pk not_null; n: int; }")
    b = parse("table u { id: int pk not_null; n: bigint; }")
    ok, reasons = compatible(a, b)
    assert not ok
    assert any("int -> bigint" in r for r in reasons)


def test_tightening_nullable_breaks():
    a = parse("table u { id: int pk not_null; n: text; }")
    b = parse("table u { id: int pk not_null; n: text not_null; }")
    ok, reasons = compatible(a, b)
    assert not ok
    assert any("NOT NULL" in r for r in reasons)


def test_loosening_nullable_is_compatible():
    a = parse("table u { id: int pk not_null; n: text not_null; }")
    b = parse("table u { id: int pk not_null; n: text; }")
    ok, _ = compatible(a, b)
    assert ok
