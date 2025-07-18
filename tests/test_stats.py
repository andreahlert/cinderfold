from pathlib import Path

from cinderfold.parser import parse
from cinderfold.stats import stats


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def test_empty_schema():
    s = stats(parse(""))
    assert s.tables == 0 and s.columns == 0 and s.density == 0.0


def test_blog_v1_counts():
    s = stats(parse((FIX / "blog_v1.dsl").read_text()))
    assert s.tables == 3
    assert s.columns == 12
    assert s.pks == 3
    assert s.indexes == 2
    assert s.foreign_keys == 2


def test_density():
    s = stats(parse("table a { id: int pk not_null; x: text; y: text; }"))
    assert s.tables == 1 and s.columns == 3
    assert s.density == 3.0


def test_not_null_and_unique_counts():
    s = stats(parse("table u { id: int pk not_null; email: text not_null unique; "
                    "nick: text; }"))
    assert s.not_null_columns == 2
    assert s.unique_columns == 1
