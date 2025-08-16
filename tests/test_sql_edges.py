from cinderfold.sql import parse_sql


def test_skip_other_statements():
    sql = """
        BEGIN;
        SELECT 1;
        CREATE TABLE u (id INTEGER PRIMARY KEY);
        COMMIT;
    """
    s = parse_sql(sql)
    assert s.table("u") is not None


def test_default_integer_zero():
    sql = "CREATE TABLE c (id INTEGER PRIMARY KEY, n INTEGER NOT NULL DEFAULT 0);"
    s = parse_sql(sql)
    assert s.table("c").column("n").default == "0"


def test_unique_table_level():
    sql = """
        CREATE TABLE u (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            UNIQUE (email)
        );
    """
    s = parse_sql(sql)
    assert s.table("u").column("email").unique is True


def test_on_update_cascade():
    sql = """
        CREATE TABLE p (id INTEGER PRIMARY KEY);
        CREATE TABLE c (
            id INTEGER PRIMARY KEY,
            pid INTEGER NOT NULL,
            FOREIGN KEY (pid) REFERENCES p (id) ON UPDATE CASCADE
        );
    """
    s = parse_sql(sql)
    assert s.table("c").foreign_keys[0].on_update == "cascade"


def test_lowercase_create():
    sql = "create table u (id integer primary key);"
    s = parse_sql(sql)
    assert s.table("u") is not None


def test_whitespace_and_comments_tolerated():
    sql = """
        CREATE   TABLE   u (
            id   INTEGER   PRIMARY KEY,
            x    TEXT
        );
    """
    s = parse_sql(sql)
    assert {c.name for c in s.table("u").columns} == {"id", "x"}
