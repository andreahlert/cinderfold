from cinderfold.diff import Change
from cinderfold.filter import filter_changes


def _changes():
    return [
        Change("presence", "users", None, "table added"),
        Change("type", "orders", "n", "type int -> bigint"),
        Change("constraint", "orders", "uid", "nullable True -> False"),
        Change("auxiliary", "logs", "created_at", "default change"),
    ]


def test_min_severity_drops_aux():
    out = filter_changes(_changes(), min_severity="constraint")
    cats = {c.category for c in out}
    assert "auxiliary" not in cats


def test_include_glob():
    out = filter_changes(_changes(), include=["orders"])
    assert {c.table for c in out} == {"orders"}


def test_exclude_glob():
    out = filter_changes(_changes(), exclude=["logs"])
    assert all(c.table != "logs" for c in out)


def test_combined():
    out = filter_changes(_changes(), min_severity="type", exclude=["users"])
    assert {(c.category, c.table) for c in out} == {("type", "orders")}


def test_passthrough_when_no_filters():
    assert len(filter_changes(_changes())) == 4
