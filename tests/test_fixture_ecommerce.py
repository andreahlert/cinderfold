from pathlib import Path

from cinderfold.fingerprint import fingerprint
from cinderfold.parser import parse
from cinderfold.render import render
from cinderfold.stats import stats
from cinderfold.validate import validate


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def test_ecommerce_validates_clean():
    s = parse((FIX / "ecommerce.dsl").read_text())
    assert validate(s) == []


def test_ecommerce_counts():
    s = parse((FIX / "ecommerce.dsl").read_text())
    n = stats(s)
    assert n.tables == 5
    assert n.foreign_keys >= 4
    assert n.indexes >= 3


def test_ecommerce_render_roundtrip():
    s = parse((FIX / "ecommerce.dsl").read_text())
    again = parse(render(s))
    assert again == s


def test_ecommerce_fingerprint_stable():
    s1 = parse((FIX / "ecommerce.dsl").read_text())
    s2 = parse(render(s1))
    assert fingerprint(s1) == fingerprint(s2)
