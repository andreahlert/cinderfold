from cinderfold.migrate import migrate
from cinderfold.parser import parse


def test_create_new_table():
    old = parse("table a { id: int pk not_null; }")
    new = parse("table a { id: int pk not_null; } table b { id: int pk not_null; }")
    stmts = migrate(old, new)
    assert any(s.startswith("CREATE TABLE b") for s in stmts)


def test_drop_table():
    old = parse("table a { id: int pk not_null; } table b { id: int pk not_null; }")
    new = parse("table a { id: int pk not_null; }")
    stmts = migrate(old, new)
    assert "DROP TABLE b;" in stmts


def test_add_column():
    old = parse("table u { id: int pk not_null; }")
    new = parse("table u { id: int pk not_null; email: text not_null; }")
    stmts = migrate(old, new)
    assert any("ADD COLUMN email TEXT NOT NULL" in s for s in stmts)


def test_drop_column():
    old = parse("table u { id: int pk not_null; email: text not_null; }")
    new = parse("table u { id: int pk not_null; }")
    stmts = migrate(old, new)
    assert "ALTER TABLE u DROP COLUMN email;" in stmts


def test_change_type():
    old = parse("table u { id: int pk not_null; n: int not_null; }")
    new = parse("table u { id: int pk not_null; n: bigint not_null; }")
    stmts = migrate(old, new)
    assert any("TYPE BIGINT" in s for s in stmts)


def test_toggle_not_null():
    old = parse("table u { id: int pk not_null; name: text not_null; }")
    new = parse("table u { id: int pk not_null; name: text; }")
    stmts = migrate(old, new)
    assert any("DROP NOT NULL" in s for s in stmts)


def test_create_drop_index():
    old = parse("table u { id: int pk not_null; email: text not_null; }")
    new = parse("table u { id: int pk not_null; email: text not_null; "
                "index ix_u_email (email); }")
    fwd = migrate(old, new)
    assert any(s.startswith("CREATE INDEX ix_u_email") for s in fwd)
    back = migrate(new, old)
    assert "DROP INDEX ix_u_email;" in back
