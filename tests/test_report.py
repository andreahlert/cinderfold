import json

from cinderfold.diff import Change
from cinderfold.report import to_json, to_markdown, to_text


def _sample():
    return [
        Change("presence", "users", None, "table added"),
        Change("type", "orders", "total", "type int -> bigint"),
        Change("constraint", "orders", "user_id", "nullable True -> False"),
        Change("auxiliary", "orders", "created_at", "default None -> 'now()'"),
    ]


def test_text_groups_by_category():
    out = to_text(_sample())
    assert "[presence]" in out
    assert "[type]" in out
    assert "[constraint]" in out
    assert "[auxiliary]" in out
    assert "users: table added" in out
    assert "orders.total" in out


def test_text_empty():
    assert to_text([]) == "no changes\n"


def test_json_roundtrips():
    out = to_json(_sample())
    data = json.loads(out)
    assert {d["category"] for d in data} == {"presence", "type", "constraint", "auxiliary"}
    assert any(d["table"] == "orders" and d["column"] == "total" for d in data)


def test_json_severity_attached():
    data = json.loads(to_json(_sample()))
    sev = {d["category"]: d["severity"] for d in data}
    assert sev["presence"] > sev["type"] > sev["constraint"] > sev["auxiliary"]


def test_markdown_has_table_per_category():
    out = to_markdown(_sample())
    assert out.startswith("## Schema diff")
    assert "### presence" in out
    assert "| Table | Column | Detail |" in out


def test_csv():
    from cinderfold.report import to_csv
    out = to_csv(_sample())
    lines = out.strip().splitlines()
    assert lines[0] == "category,severity,table,column,detail"
    assert any("orders,2,orders,total" in line or "orders" in line for line in lines)


def test_tsv_uses_tabs():
    from cinderfold.report import to_tsv
    out = to_tsv(_sample())
    assert "\t" in out.splitlines()[0]


def test_markdown_empty():
    assert "No changes" in to_markdown([])
