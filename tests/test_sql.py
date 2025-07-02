from cinderfold.sql import parse_sql


def test_parse_simple_create_table():
    sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            name TEXT
        );
    """
    s = parse_sql(sql)
    t = s.table("users")
    assert t is not None
    assert {c.name for c in t.columns} == {"id", "email", "name"}
    assert t.column("id").pk is True
    assert t.column("email").nullable is False
    assert t.column("email").unique is True


def test_parse_multiple_tables():
    sql = """
        CREATE TABLE users (id INTEGER PRIMARY KEY);
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """
    s = parse_sql(sql)
    assert {t.name for t in s.tables} == {"users", "orders"}
    orders = s.table("orders")
    assert len(orders.foreign_keys) == 1
    fk = orders.foreign_keys[0]
    assert fk.ref_table == "users"
    assert fk.on_delete == "cascade"


def test_parse_table_level_primary_key():
    sql = """
        CREATE TABLE order_items (
            order_id INTEGER NOT NULL,
            line_no INTEGER NOT NULL,
            sku TEXT NOT NULL,
            PRIMARY KEY (order_id, line_no)
        );
    """
    s = parse_sql(sql)
    t = s.table("order_items")
    pk_cols = {c.name for c in t.columns if c.pk}
    assert pk_cols == {"order_id", "line_no"}


def test_parse_default_with_function_call():
    sql = "CREATE TABLE x (id INTEGER PRIMARY KEY, at TIMESTAMP NOT NULL DEFAULT now());"
    s = parse_sql(sql)
    t = s.table("x")
    assert t.column("at").default == "now()"


def test_parse_if_not_exists_ignored():
    sql = "CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY);"
    s = parse_sql(sql)
    assert s.table("t") is not None
