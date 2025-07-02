from cinderfold.sqlite import parse_dotschema


def test_parses_create_index_after_create_table():
    text = """
        CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL);
        CREATE UNIQUE INDEX ix_users_email ON users (email);
    """
    s = parse_dotschema(text)
    t = s.table("users")
    assert len(t.indexes) == 1
    assert t.indexes[0].name == "ix_users_email"
    assert t.indexes[0].unique is True


def test_non_unique_index_parsed():
    text = """
        CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER);
        CREATE INDEX ix_orders_user ON orders (user_id);
    """
    s = parse_dotschema(text)
    assert s.table("orders").indexes[0].unique is False


def test_multi_column_index():
    text = """
        CREATE TABLE events (a INTEGER, b INTEGER, ts TIMESTAMP);
        CREATE INDEX ix_events_a_b_ts ON events (a, b, ts);
    """
    s = parse_dotschema(text)
    assert s.table("events").indexes[0].columns == ("a", "b", "ts")
