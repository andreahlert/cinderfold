"""Drift-detection evaluation.

For each (n_mutations, seed) cell:
  1. Take the seed schema.
  2. Apply n_mutations random mutations to obtain a new schema.
  3. Run cinderfold.diff(old, new).
  4. Compare the detected changes against ground truth.

Metrics: precision and recall on the (category, table, column, detail) tuple,
plus per-category recall.

Writes results.csv. No hardcoded numbers anywhere.
"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

from cinderfold.diff import diff

from .mutate import mutate
from .seed_schema import seed


MUTATION_COUNTS = [1, 2, 5, 10, 20]
SEEDS = list(range(1, 11))


def to_tuple(c):
    return (c.category, c.table, c.column, c.detail)


def run_one(n_mut: int, seed_n: int) -> dict:
    rng = random.Random(seed_n * 1000 + n_mut)
    base = seed()
    new_schema, truth = mutate(base, n_mut, rng)
    detected = [to_tuple(c) for c in diff(base, new_schema)]
    truth_set = set(truth)
    det_set = set(detected)
    tp = len(truth_set & det_set)
    fp = len(det_set - truth_set)
    fn = len(truth_set - det_set)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    per_cat = defaultdict(lambda: [0, 0])  # [tp, total]
    for t in truth_set:
        per_cat[t[0]][1] += 1
        if t in det_set:
            per_cat[t[0]][0] += 1
    return {
        "n_mutations": n_mut,
        "seed": seed_n,
        "truth_size": len(truth_set),
        "detected_size": len(det_set),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "recall_presence": per_cat["presence"][0] / per_cat["presence"][1] if per_cat["presence"][1] else 1.0,
        "recall_type": per_cat["type"][0] / per_cat["type"][1] if per_cat["type"][1] else 1.0,
        "recall_constraint": per_cat["constraint"][0] / per_cat["constraint"][1] if per_cat["constraint"][1] else 1.0,
        "recall_auxiliary": per_cat["auxiliary"][0] / per_cat["auxiliary"][1] if per_cat["auxiliary"][1] else 1.0,
    }


def main() -> None:
    out = Path(__file__).parent / "results.csv"
    rows = [run_one(n, s) for n in MUTATION_COUNTS for s in SEEDS]
    fields = list(rows[0].keys())
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
