from cinderfold.diff import diff
from cinderfold.dump import dump_sql
from cinderfold.fingerprint import fingerprint
from cinderfold.migrate import migrate
from cinderfold.parser import parse
from cinderfold.render import render
from cinderfold.serial import from_dict, to_dict


def test_parse_empty_yields_empty_schema():
    s = parse("")
    assert s.tables == ()


def test_parse_only_whitespace():
    s = parse("\n\n\t   \n")
    assert s.tables == ()


def test_parse_only_comments():
    s = parse("// hello\n/* world */\n// done\n")
    assert s.tables == ()


def test_diff_empty_to_nonempty_is_all_presence():
    a = parse("")
    b = parse("table u { id: int pk not_null; }")
    out = diff(a, b)
    assert all(c.category == "presence" for c in out)


def test_migrate_empty_to_nonempty_creates_tables():
    a = parse("")
    b = parse("table u { id: int pk not_null; }")
    assert any(s.startswith("CREATE TABLE u") for s in migrate(a, b))


def test_render_empty_schema():
    assert render(parse("")).strip() == ""


def test_dump_empty():
    assert dump_sql(parse("")).strip() == ""


def test_serial_empty_roundtrip():
    s = parse("")
    assert from_dict(to_dict(s)) == s


def test_fingerprint_empty_is_stable():
    a = fingerprint(parse(""))
    b = fingerprint(parse("// nothing\n"))
    assert a == b
