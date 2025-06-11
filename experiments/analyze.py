"""Aggregate cinderfold results.csv across seeds for each n_mutations cell."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path


METRICS = ["precision", "recall", "recall_presence", "recall_type",
           "recall_constraint", "recall_auxiliary"]


def main() -> None:
    path = Path(__file__).parent / "results.csv"
    with open(path) as f:
        rows = list(csv.DictReader(f))
    by_n: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_n[r["n_mutations"]].append(r)
    header = f"{'n_mut':>6} " + " ".join(f"{m:>20}" for m in METRICS)
    print(header)
    for n in sorted(by_n.keys(), key=int):
        group = by_n[n]
        cells = []
        for m in METRICS:
            vals = [float(r[m]) for r in group]
            mean = statistics.fmean(vals)
            sd = statistics.pstdev(vals)
            cells.append(f"{mean:>9.3f}±{sd:<9.3f}")
        print(f"{n:>6} " + " ".join(cells))


if __name__ == "__main__":
    main()
