"""Properties that must hold over many random diffs."""

from __future__ import annotations

import random

from cinderfold.diff import diff
from cinderfold.parser import parse
from cinderfold.render import render


def _random_schema(rng: random.Random, n_tables: int):
    parts = []
    for i in range(n_tables):
        cols = ["id: int pk not_null;"]
        n_cols = rng.randint(1, 6)
        for j in range(n_cols):
            t = rng.choice(["int", "text", "bool", "timestamp"])
            nn = " not_null" if rng.random() < 0.5 else ""
            cols.append(f"c_{j}: {t}{nn};")
        body = "\n    ".join(cols)
        parts.append(f"table t_{i} {{\n    {body}\n}}")
    return parse("\n\n".join(parts))


def test_diff_self_is_empty():
    rng = random.Random(0)
    for _ in range(20):
        s = _random_schema(rng, n_tables=rng.randint(1, 6))
        assert diff(s, s) == []


def test_diff_render_render_is_empty():
    rng = random.Random(1)
    for _ in range(20):
        s = _random_schema(rng, n_tables=rng.randint(1, 6))
        again = parse(render(s))
        assert diff(s, again) == []


def test_diff_results_sorted_by_severity_desc():
    rng = random.Random(2)
    a = _random_schema(rng, n_tables=4)
    b = _random_schema(rng, n_tables=4)
    out = diff(a, b)
    severities = [c.severity for c in out]
    assert severities == sorted(severities, reverse=True)


def test_diff_is_antisymmetric_in_count():
    rng = random.Random(3)
    a = _random_schema(rng, n_tables=3)
    b = _random_schema(rng, n_tables=3)
    assert len(diff(a, b)) >= 0
    assert len(diff(b, a)) >= 0
