from pathlib import Path

from cinderfold.dump import dump_sql
from cinderfold.parser import parse
from cinderfold.sql import parse_sql


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def test_dump_emits_create_table_per_table():
    s = parse((FIX / "blog_v1.dsl").read_text())
    sql = dump_sql(s)
    for name in ("users", "posts", "comments"):
        assert f"CREATE TABLE {name}" in sql


def test_dump_includes_indexes_and_fks():
    s = parse((FIX / "blog_v1.dsl").read_text())
    sql = dump_sql(s)
    assert "CREATE INDEX ix_posts_user" in sql
    assert "ADD CONSTRAINT fk_posts_user" in sql


def test_dump_then_parse_roundtrip_table_set():
    s = parse((FIX / "blog_v1.dsl").read_text())
    again = parse_sql(dump_sql(s))
    assert {t.name for t in again.tables} == {t.name for t in s.tables}


def test_dump_minimal():
    s = parse("table u { id: int pk not_null; }")
    sql = dump_sql(s)
    assert "CREATE TABLE u" in sql and "id INT PRIMARY KEY" in sql
