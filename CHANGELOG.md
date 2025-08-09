# Changelog

## 0.2.0

### Added

- Model: `Index` and `ForeignKey` dataclasses, with referential actions.
- Parser: `index ... ;` and `fk ... -> ... ;` grammar with `on_delete` /
  `on_update`. Block comments (`/* ... */`).
- Diff: presence / type / constraint classification for indexes and FKs.
- Adapters: SQL `CREATE TABLE`, Postgres information_schema JSON,
  SQLite `.schema`.
- `render`: DSL pretty-printer, round-trips with the parser.
- `migrate`: emit ALTER/CREATE/DROP statements from a delta.
- `dump`: emit full DDL for a Schema.
- `validate`: static checks (duplicate names, orphan FKs, multiple PKs).
- `rename`: collapse drop+add pairs into rename hints.
- `filter`: severity floor and table glob filtering for Change lists.
- `select` / `exclude` / `merge`: schema subsetting.
- `stats`: table/column/index/fk counts plus density.
- `fingerprint`: stable SHA-256 of a canonical serialization.
- `serial`: lossless JSON serialization.
- `report.to_text` / `to_json` / `to_markdown`; `html.to_html`.
- CLI: `diff`, `parse`, `migrate`, `validate`, `dump`, `fingerprint`,
  `stats`, `sql2dsl`, `pg2dsl`, `sqlite2dsl`. `--include`, `--exclude`,
  `--min-severity`, `--fail-on` filters on `diff`.
- Fixtures: `blog_v1` / `blog_v2` schema pair used in integration tests.
- Benchmarks: `bench_parse.py`, `bench_diff.py`.
- Examples: CI drift gate, SQLite snapshot comparison, auto migration.

## 0.1.0

- Initial release: tiny DSL parser, presence/type/constraint/auxiliary
  classifier, mutation experiment harness.
