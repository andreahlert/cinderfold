from cinderfold.parser import parse


def test_single_quoted_string_default():
    s = parse("table u { id: int pk not_null; n: text default = 'x'; }")
    assert s.table("u").column("n").default == "x"


def test_single_quoted_comment():
    s = parse("table u { id: int pk not_null comment = 'pk col'; }")
    assert s.table("u").column("id").comment == "pk col"


def test_double_quoted_still_works():
    s = parse("table u { id: int pk not_null; n: text default = \"x\"; }")
    assert s.table("u").column("n").default == "x"


def test_quote_with_escape():
    s = parse("table u { id: int pk not_null; n: text default = 'a\\'b'; }")
    assert s.table("u").column("n").default == "a\\'b"
