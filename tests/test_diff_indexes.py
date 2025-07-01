from cinderfold.diff import diff
from cinderfold.parser import parse


def test_index_added_is_presence():
    a = parse("table t { id: int pk not_null; }")
    b = parse("table t { id: int pk not_null; index ix_t_id (id); }")
    out = diff(a, b)
    assert any(c.category == "presence" and "index added" in c.detail for c in out)


def test_index_dropped_is_presence():
    a = parse("table t { id: int pk not_null; index ix_t_id (id); }")
    b = parse("table t { id: int pk not_null; }")
    out = diff(a, b)
    assert any(c.category == "presence" and "index dropped" in c.detail for c in out)


def test_index_columns_change_is_constraint():
    a = parse("table t { x: int; y: int; index ix_t (x); }")
    b = parse("table t { x: int; y: int; index ix_t (y); }")
    out = diff(a, b)
    assert any(c.category == "constraint" and "index columns" in c.detail for c in out)


def test_fk_added_is_presence():
    a = parse("table o { user_id: int; }")
    b = parse("table o { user_id: int; fk fk_o (user_id) -> u (id); }")
    out = diff(a, b)
    assert any(c.category == "presence" and "fk added" in c.detail for c in out)


def test_fk_on_delete_change_is_constraint():
    a = parse("table o { user_id: int; fk fk_o (user_id) -> u (id) on_delete = cascade; }")
    b = parse("table o { user_id: int; fk fk_o (user_id) -> u (id) on_delete = restrict; }")
    out = diff(a, b)
    assert any(c.category == "constraint" and "on_delete" in c.detail for c in out)


def test_fk_target_change_is_type():
    a = parse("table o { user_id: int; fk fk_o (user_id) -> u (id); }")
    b = parse("table o { user_id: int; fk fk_o (user_id) -> accounts (id); }")
    out = diff(a, b)
    assert any(c.category == "type" and "fk target" in c.detail for c in out)
