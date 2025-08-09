# cinderfold

Schema drift detection for tabular data pipelines.

Given two versions of a table schema (declared in a small DSL, parsed from
SQL, scraped from a Postgres information_schema dump, or read from
SQLite's `.schema`), cinderfold classifies the diff into four categories:

- **presence**: tables, columns, indexes, or foreign keys added or dropped
- **type**: column type changed; foreign key target changed
- **constraint**: pk, nullable, unique, on_delete, on_update flipped
- **auxiliary**: default value or comment changed

The goal is to give a pipeline owner a short, ordered list of changes that
need human review before a backfill.

## Layout

```
cinderfold/    library code (DSL parser, diff, adapters, render, migrate)
tests/         pytest suite
fixtures/      sample DSL pairs used in integration tests
experiments/   noisy-schema evaluation
benchmarks/    microbenchmarks for parse and diff
examples/      end-to-end usage scripts
paper.md       measured findings
```

## Module map

| Module | Purpose |
|---|---|
| `model` | Schema, Table, Column, Index, ForeignKey dataclasses |
| `parser` | DSL tokenizer and recursive-descent parser |
| `render` | Schema, DSL pretty-printer (round-trips with parser) |
| `sql` | CREATE TABLE adapter |
| `postgres` | information_schema JSON adapter |
| `sqlite` | `.schema` adapter (CREATE TABLE + CREATE INDEX) |
| `diff` | classify changes between two Schemas |
| `rename` | collapse drop+add pairs into rename hints |
| `filter` | filter Change lists by severity and table glob |
| `report` | text, JSON, markdown formatters |
| `html` | self-contained HTML report |
| `migrate` | emit ALTER/CREATE/DROP DDL from a delta |
| `dump` | emit full DDL from any Schema |
| `validate` | catch dupe names, orphan FKs, multiple PKs |
| `select` | subset/merge schemas by glob |
| `stats` | counts and density metrics |
| `fingerprint` | stable SHA-256 hash of a Schema |
| `serial` | lossless JSON serialization |
| `cli` | argparse front-end exposing the above |

## Running

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python -m experiments.run > experiments/run.log
PYTHONPATH=. python -m experiments.analyze
PYTHONPATH=. python benchmarks/bench_parse.py
```

## CLI quickstart

```bash
# Compare two snapshots
cinderfold diff old.dsl new.dsl
cinderfold diff old.dsl new.dsl --format md
cinderfold diff old.dsl new.dsl --fail-on presence

# Adapters that converge on the DSL form
cinderfold sql2dsl schema.sql
cinderfold pg2dsl pg_dump.json
cinderfold sqlite2dsl dotschema.sql

# Generate migration DDL
cinderfold migrate old.dsl new.dsl

# Static checks
cinderfold validate schema.dsl
cinderfold stats schema.dsl
cinderfold fingerprint schema.dsl
```
