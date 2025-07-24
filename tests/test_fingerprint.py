from cinderfold.fingerprint import fingerprint, short_fingerprint
from cinderfold.parser import parse


def test_fingerprint_is_deterministic():
    s1 = parse("table u { id: int pk not_null; }")
    s2 = parse("table u { id: int pk not_null; }")
    assert fingerprint(s1) == fingerprint(s2)


def test_fingerprint_changes_on_column_add():
    s1 = parse("table u { id: int pk not_null; }")
    s2 = parse("table u { id: int pk not_null; email: text; }")
    assert fingerprint(s1) != fingerprint(s2)


def test_fingerprint_changes_on_attribute():
    s1 = parse("table u { id: int pk not_null; name: text not_null; }")
    s2 = parse("table u { id: int pk not_null; name: text; }")
    assert fingerprint(s1) != fingerprint(s2)


def test_short_fingerprint_length():
    s = parse("table u { id: int pk not_null; }")
    assert len(short_fingerprint(s)) == 12
    assert len(short_fingerprint(s, length=8)) == 8


def test_fingerprint_hex_chars():
    s = parse("table u { id: int pk not_null; }")
    assert all(c in "0123456789abcdef" for c in fingerprint(s))
