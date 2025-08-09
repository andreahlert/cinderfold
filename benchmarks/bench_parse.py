"""Microbenchmark: DSL parse cost vs. schema size.

Generates schemas with N tables x M columns and measures parse time.
Reports wall-clock seconds and throughput in tables/sec.
"""

from __future__ import annotations

import time

from cinderfold.parser import parse


def gen(n_tables: int, n_cols: int) -> str:
    parts: list[str] = []
    for i in range(n_tables):
        cols = ["id: int pk not_null;"]
        for j in range(n_cols - 1):
            cols.append(f"col_{j}: text;")
        body = "\n".join("    " + c for c in cols)
        parts.append(f"table t_{i} {{\n{body}\n}}")
    return "\n\n".join(parts) + "\n"


def main() -> None:
    print(f"{'tables':>8} {'cols':>5} {'seconds':>10} {'tables/s':>12}")
    for n_tables, n_cols in [(10, 5), (100, 5), (1000, 5), (1000, 20)]:
        text = gen(n_tables, n_cols)
        t0 = time.perf_counter()
        s = parse(text)
        dt = time.perf_counter() - t0
        assert len(s.tables) == n_tables
        print(f"{n_tables:>8} {n_cols:>5} {dt:>10.4f} {n_tables/dt:>12.1f}")


if __name__ == "__main__":
    main()
