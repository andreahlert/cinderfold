from cinderfold.diff import Change
from cinderfold.summary import one_line, summarize


def test_summary_groups_by_category_and_table():
    s = summarize([
        Change("presence", "u", None, "table added"),
        Change("type", "o", "n", "type a -> b"),
        Change("type", "o", "m", "type a -> b"),
        Change("auxiliary", "u", "x", "default change"),
    ])
    assert s.total == 4
    assert s.by_category == {"presence": 1, "type": 2, "auxiliary": 1}
    assert s.by_table == {"u": 2, "o": 2}


def test_summary_max_severity():
    s = summarize([
        Change("auxiliary", "u", "x", "default change"),
        Change("type", "o", "n", "type a -> b"),
    ])
    assert s.max_severity == "type"


def test_summary_empty():
    s = summarize([])
    assert s.total == 0 and s.max_severity is None
    assert one_line(s) == "0 changes"


def test_one_line_format():
    s = summarize([
        Change("presence", "u", None, "table added"),
        Change("auxiliary", "u", "x", "default change"),
    ])
    assert "2 changes" in one_line(s)
    assert "presence" in one_line(s)
