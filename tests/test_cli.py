import io
import json
import sys
from contextlib import redirect_stdout

import pytest

from cinderfold.cli import main


@pytest.fixture
def tmp_dsl(tmp_path):
    def write(name, body):
        p = tmp_path / name
        p.write_text(body)
        return str(p)
    return write


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def test_parse_dsl_to_json(tmp_dsl):
    f = tmp_dsl("a.dsl", "table users { id: int pk not_null; }")
    rc, out = _run(["parse", f, "--format", "json"])
    assert rc == 0
    payload = json.loads(out)
    assert payload["tables"][0]["name"] == "users"


def test_parse_dsl_roundtrip(tmp_dsl):
    f = tmp_dsl("a.dsl", "table u { id: int pk not_null; }")
    rc, out = _run(["parse", f])
    assert rc == 0
    assert "table u" in out
    assert "id: int" in out


def test_diff_text(tmp_dsl):
    a = tmp_dsl("old.dsl", "table u { id: int pk not_null; }")
    b = tmp_dsl("new.dsl", "table u { id: int pk not_null; email: text not_null; }")
    rc, out = _run(["diff", a, b])
    assert rc == 0
    assert "column added" in out


def test_diff_fail_on_presence_exits_nonzero(tmp_dsl):
    a = tmp_dsl("old.dsl", "table u { id: int pk not_null; }")
    b = tmp_dsl("new.dsl", "table u { id: int pk not_null; email: text not_null; }")
    rc, _ = _run(["diff", a, b, "--fail-on", "presence"])
    assert rc == 1


def test_diff_fail_on_higher_than_change_returns_zero(tmp_dsl):
    a = tmp_dsl("old.dsl", "table u { id: int pk not_null; ts: timestamp not_null; }")
    b = tmp_dsl("new.dsl", "table u { id: int pk not_null; ts: timestamp not_null default = now(); }")
    rc, _ = _run(["diff", a, b, "--fail-on", "presence"])
    assert rc == 0


def test_sql2dsl(tmp_dsl):
    f = tmp_dsl("schema.sql", "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL);")
    rc, out = _run(["sql2dsl", f])
    assert rc == 0
    assert "table users" in out
    assert "email" in out


def test_sqlite2dsl(tmp_dsl):
    f = tmp_dsl("dotschema.sql",
                "CREATE TABLE u (id INTEGER PRIMARY KEY, email TEXT);"
                "CREATE UNIQUE INDEX ix_u_email ON u (email);")
    rc, out = _run(["sqlite2dsl", f])
    assert rc == 0
    assert "index ix_u_email" in out


def test_migrate(tmp_dsl):
    a = tmp_dsl("old.dsl", "table u { id: int pk not_null; }")
    b = tmp_dsl("new.dsl", "table u { id: int pk not_null; email: text not_null; }")
    rc, out = _run(["migrate", a, b])
    assert rc == 0
    assert "ADD COLUMN email" in out


def test_diff_with_include(tmp_dsl):
    a = tmp_dsl("old.dsl",
                "table u { id: int pk not_null; } table p { id: int pk not_null; }")
    b = tmp_dsl("new.dsl",
                "table u { id: int pk not_null; email: text; } "
                "table p { id: int pk not_null; title: text; }")
    rc, out = _run(["diff", a, b, "--include", "u"])
    assert rc == 0
    assert "email" in out
    assert "title" not in out


def test_diff_with_min_severity(tmp_dsl):
    a = tmp_dsl("old.dsl",
                "table u { id: int pk not_null; ts: timestamp not_null; }")
    b = tmp_dsl("new.dsl",
                "table u { id: int pk not_null; ts: timestamp not_null default = now(); }")
    rc, out = _run(["diff", a, b, "--min-severity", "constraint"])
    assert rc == 0
    assert "no changes" in out


def test_dump(tmp_dsl):
    f = tmp_dsl("a.dsl", "table u { id: int pk not_null; }")
    rc, out = _run(["dump", f])
    assert rc == 0
    assert "CREATE TABLE u" in out


def test_dump_select_filters(tmp_dsl):
    f = tmp_dsl("a.dsl",
                "table u { id: int pk not_null; } "
                "table p { id: int pk not_null; }")
    rc, out = _run(["dump", f, "--select", "u"])
    assert rc == 0
    assert "CREATE TABLE u" in out
    assert "CREATE TABLE p" not in out


def test_fingerprint(tmp_dsl):
    f = tmp_dsl("a.dsl", "table u { id: int pk not_null; }")
    rc, out = _run(["fingerprint", f])
    assert rc == 0
    assert len(out.strip()) == 64


def test_stats(tmp_dsl):
    f = tmp_dsl("a.dsl", "table u { id: int pk not_null; e: text; }")
    rc, out = _run(["stats", f])
    assert rc == 0
    assert "tables=1" in out and "columns=2" in out


def test_validate_clean(tmp_dsl):
    f = tmp_dsl("good.dsl", "table u { id: int pk not_null; }")
    rc, out = _run(["validate", f])
    assert rc == 0
    assert out == ""


def test_validate_bad(tmp_dsl):
    f = tmp_dsl("bad.dsl",
                "table u { id: int pk not_null; id: int not_null; }")
    rc, out = _run(["validate", f])
    assert rc == 1
    assert "duplicate column" in out


def test_pg2dsl(tmp_dsl):
    payload = {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False, "pk": True},
                    {"name": "email", "type": "text", "nullable": False},
                ],
            }
        ]
    }
    f = tmp_dsl("pg.json", json.dumps(payload))
    rc, out = _run(["pg2dsl", f])
    assert rc == 0
    assert "table users" in out
