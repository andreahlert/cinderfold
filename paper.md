# Severity-Classified Schema Drift Detection

**Andre Ahlert, 2025**

## Abstract

We implement `cinderfold`, a schema drift detector that classifies each
change between two declared schemas into one of four severity categories:
*presence* (added/dropped tables or columns), *type* (column type changed),
*constraint* (primary key, nullability, uniqueness), and *auxiliary*
(default, comment). Against a synthetic mutation workload over a five-table
seed schema (10 seeds), precision stays at or near 1.000 across mutation
counts from 1 to 20. Recall is perfect at 1 and 2 mutations, but drops to
0.660 ± 0.139 at 20 mutations. The recall drop is not a detector bug:
mutations applied to the same column compose (a nullable flip applied
twice cancels) so the ground-truth list of individual edits exceeds the
net diff. The detector recovers net state changes; the experiment exposes
the gap between operation history and observable state.

## Motivation

Schema drift is one of the silent risks of long-lived pipelines. A
column flipped from `not_null` to `nullable` will make a downstream
aggregation collapse without error. A type widened from `int` to
`bigint` will pass casts in tests and fail under data with values past
the old range. We want a tool that reads two schema declarations and
returns a short, ordered list, severity-first, of things a pipeline
owner must read before approving a deployment.

## Approach

`cinderfold` provides three pieces.

A tiny declarative DSL parser. Tables and columns are declared with
optional attributes (`pk`, `not_null`, `nullable`, `unique`, `default =
...`, `comment = "..."`). The parser is a 100-line hand-written
recursive descent. Defaults can be numeric, identifier or string.

A frozen data model (`Schema`, `Table`, `Column`) suitable for set
operations.

A `diff(old, new)` function that walks tables, then columns, then
attributes, producing `Change(category, table, column, detail)`
entries sorted by severity descending.

## Case study

The seed schema models a small e-commerce database (`users`, `orders`,
`order_items`, `products`, `audit_events`; 30 columns total). We apply
n mutations sampled uniformly from {add_column, drop_column,
change_type, flip_nullable, flip_unique, change_default,
change_comment, add_table, drop_table}, record the ground-truth list
of mutation tuples, then run `diff(seed, mutated)` and compare the
result set against the truth set.

```
n_mut  precision   recall   r_presence   r_type   r_constraint   r_aux
    1  1.000       1.000    1.000        1.000    1.000          1.000
    2  1.000       1.000    1.000        1.000    1.000          1.000
    5  1.000       0.960    0.975        1.000    0.950          1.000
   10  1.000       0.790    0.955        0.767    0.567          0.858
   20  0.976       0.660    0.772        0.733    0.532          0.636
```

Mean ± standard deviation across 10 seeds per row. Constraint recall
falls fastest because nullability and uniqueness are binary flags, so
double-flipping (which the mutator does not exclude) reduces them to
no-ops. Type recall drops next because a column can be retyped twice
to a third type, leaving only the net transition visible. Presence
recall is the most resilient: adding then dropping the same column
within 20 random picks is unlikely with the namespaces we use.

Precision stays at 1.000 except at n_mut = 20 (0.976 ± 0.052), where
one detected change for one seed did not appear in the truth list. On
inspection this is a real net-state difference produced by composing
mutations on a column, not a false positive against the new schema.

## Limitations

The mutator does not avoid collisions, so the recall measurement is
"recall against operation history" rather than "recall against
net-state-changes." That is the more honest metric of the two for
this study, because in production a pipeline owner cares about state
between deploys, not the intra-deploy edit log. A separate experiment
that deduplicates the truth set against the final state would be
expected to produce recall near 1.0 at all n_mut.

The DSL is intentionally small. Real schema sources (Postgres, BigQuery,
dbt) carry richer constraint shapes (CHECK, partial unique, expression
indices). `diff` would need extensions for those.

## Outlook

Three steps. (i) Add a state-deduplicated recall variant. (ii) Plug an
adapter from Postgres `information_schema` to `Schema`, so the same
diff runs against real databases. (iii) Surface the severity-ordered
changes as a one-page review document, integrating with PR checks.

## References

Code: `cinderfold/`. Reproduce with `PYTHONPATH=. python -m
experiments.run` then `PYTHONPATH=. python -m experiments.analyze`.
Numbers above come from seeds 1 through 10 on a single laptop run.
