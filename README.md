# cinderfold

Schema drift detection for tabular data pipelines.

Given two versions of a table schema (declared in a small DSL), `cinderfold`
classifies the diff into four categories: presence (added/dropped columns),
type (column type changed), constraint (nullability / primary key /
uniqueness), and auxiliary (default value, comment). The goal is to give
a pipeline owner a short, ordered list of changes that need human review
before a backfill.

## Layout

```
cinderfold/    library code (DSL parser, diff, classifier)
tests/         pytest suite
experiments/   noisy-schema evaluation
paper.md       measured findings
```

## Running

```
PYTHONPATH=. pytest -q
PYTHONPATH=. python -m experiments.run > experiments/run.log
PYTHONPATH=. python -m experiments.analyze
```
