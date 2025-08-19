from cinderfold.sqlite import parse_dotschema


def test_ignores_views():
    text = """
        CREATE TABLE u (id INTEGER PRIMARY KEY);
        CREATE VIEW v AS SELECT * FROM u;
    """
    s = parse_dotschema(text)
    assert {t.name for t in s.tables} == {"u"}


def test_ignores_triggers():
    text = """
        CREATE TABLE u (id INTEGER PRIMARY KEY);
        CREATE TRIGGER tr AFTER INSERT ON u BEGIN SELECT 1; END;
    """
    s = parse_dotschema(text)
    assert {t.name for t in s.tables} == {"u"}


def test_create_unique_index_if_not_exists():
    text = """
        CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT);
        CREATE UNIQUE INDEX IF NOT EXISTS ix_u_email ON u (email);
    """
    s = parse_dotschema(text)
    ix = s.table("u").indexes[0]
    assert ix.name == "ix_u_email" and ix.unique is True


def test_two_tables_each_with_indexes():
    text = """
        CREATE TABLE u (id INTEGER PRIMARY KEY, e TEXT);
        CREATE TABLE o (id INTEGER PRIMARY KEY, uid INTEGER);
        CREATE INDEX ix_u_e ON u (e);
        CREATE INDEX ix_o_uid ON o (uid);
    """
    s = parse_dotschema(text)
    assert {i.name for i in s.table("u").indexes} == {"ix_u_e"}
    assert {i.name for i in s.table("o").indexes} == {"ix_o_uid"}
