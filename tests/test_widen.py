from cinderfold.widen import is_widening


def test_int_to_bigint_safe():
    assert is_widening("int", "bigint") is True


def test_bigint_to_int_unsafe():
    assert is_widening("bigint", "int") is False


def test_same_type_safe():
    assert is_widening("text", "text") is True


def test_varchar_grow_safe():
    assert is_widening("varchar(10)", "varchar(20)") is True


def test_varchar_shrink_unsafe():
    assert is_widening("varchar(20)", "varchar(10)") is False


def test_varchar_to_text_safe():
    assert is_widening("varchar(10)", "text") is True


def test_text_to_int_unsafe():
    assert is_widening("text", "int") is False


def test_unknown_pair_unsafe():
    assert is_widening("uuid", "int") is False


def test_smallint_to_int():
    assert is_widening("smallint", "int") is True
    assert is_widening("smallint", "bigint") is True
