from cinderfold.diff import Change
from cinderfold.html import to_html


def test_empty_html():
    out = to_html([])
    assert "<html" in out and "No changes" in out


def test_html_groups_and_escapes():
    changes = [
        Change("presence", "users", None, "table added"),
        Change("type", "<orders>", "n", "type int -> bigint"),
    ]
    out = to_html(changes, title="My <Diff>")
    assert "<title>My &lt;Diff&gt;</title>" in out
    assert "&lt;orders&gt;" in out
    assert "Presence" in out and "Type" in out
    assert "1 change" in out


def test_html_has_table_rows():
    changes = [Change("constraint", "u", "id", "pk True -> False")]
    out = to_html(changes)
    assert "<td>u</td>" in out
    assert "<td>id</td>" in out
