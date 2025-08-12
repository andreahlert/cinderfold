from cinderfold.diff import Change
from cinderfold.explain import annotate, explain


def test_explain_presence_added():
    msg = explain(Change("presence", "u", None, "table added"))
    assert "Backfilling" in msg or "consumer" in msg


def test_explain_presence_dropped():
    msg = explain(Change("presence", "u", None, "table dropped"))
    assert "failing" in msg.lower() or "breaking" in msg.lower()


def test_explain_column_added():
    msg = explain(Change("presence", "u", "name", "column added"))
    assert "backfill" in msg.lower() or "default" in msg.lower()


def test_explain_type_change():
    msg = explain(Change("type", "u", "n", "type int -> bigint"))
    assert "type" in msg.lower() or "widen" in msg.lower()


def test_annotate_returns_pairs():
    out = annotate([
        Change("presence", "u", None, "table added"),
        Change("auxiliary", "u", "x", "default change"),
    ])
    assert len(out) == 2
    assert all(isinstance(o[1], str) and o[1] for o in out)
