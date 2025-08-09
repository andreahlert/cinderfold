"""Microbenchmark: diff cost between large schemas with M changes.

Builds two schemas of N tables; mutates M tables in the new copy
(adds one column each). Measures diff time.
"""

from __future__ import annotations

import time

from cinderfold.diff import diff
from cinderfold.parser import parse


def gen(n_tables: int) -> str:
    parts = []
    for i in range(n_tables):
        parts.append(f"table t_{i} {{ id: int pk not_null; x: text; y: text; }}")
    return "\n".join(parts) + "\n"


def gen_changed(n_tables: int, n_changes: int) -> str:
    parts = []
    for i in range(n_tables):
        if i < n_changes:
            parts.append(f"table t_{i} {{ id: int pk not_null; x: text; y: text; z: text; }}")
        else:
            parts.append(f"table t_{i} {{ id: int pk not_null; x: text; y: text; }}")
    return "\n".join(parts) + "\n"


def main() -> None:
    print(f"{'tables':>8} {'changes':>8} {'seconds':>10}")
    for n_tables, n_changes in [(100, 10), (1000, 10), (1000, 100), (5000, 100)]:
        old = parse(gen(n_tables))
        new = parse(gen_changed(n_tables, n_changes))
        t0 = time.perf_counter()
        out = diff(old, new)
        dt = time.perf_counter() - t0
        assert len(out) == n_changes, len(out)
        print(f"{n_tables:>8} {n_changes:>8} {dt:>10.4f}")


if __name__ == "__main__":
    main()
