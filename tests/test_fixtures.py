from pathlib import Path

from cinderfold.diff import diff
from cinderfold.migrate import migrate
from cinderfold.parser import parse
from cinderfold.rename import detect_renames
from cinderfold.render import render
from cinderfold.validate import validate


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def _load(name):
    return parse((FIX / name).read_text())


def test_fixtures_validate_clean():
    for name in ("blog_v1.dsl", "blog_v2.dsl"):
        assert validate(_load(name)) == [], name


def test_blog_v1_to_v2_diff_has_expected_changes():
    v1 = _load("blog_v1.dsl")
    v2 = _load("blog_v2.dsl")
    changes = diff(v1, v2)
    details = {(c.table, c.column, c.detail) for c in changes}
    assert ("tags", None, "table added") in details
    assert ("post_tags", None, "table added") in details
    assert ("posts", "slug", "column added") in details
    assert ("users", "display_name", "column added") in details


def test_blog_v1_to_v2_rename_detected():
    v1 = _load("blog_v1.dsl")
    v2 = _load("blog_v2.dsl")
    hints, _ = detect_renames(v1, v2, diff(v1, v2))
    assert any(h.kind == "column" and h.old == "author" and h.new == "author_id"
               for h in hints) is False


def test_blog_v1_to_v2_migration_includes_new_tables():
    v1 = _load("blog_v1.dsl")
    v2 = _load("blog_v2.dsl")
    sql = "\n".join(migrate(v1, v2))
    assert "CREATE TABLE tags" in sql
    assert "CREATE TABLE post_tags" in sql


def test_render_roundtrip_fixtures():
    for name in ("blog_v1.dsl", "blog_v2.dsl"):
        s = _load(name)
        again = parse(render(s))
        assert again == s, name
