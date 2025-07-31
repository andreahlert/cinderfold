"""cinderfold CLI.

    cinderfold diff OLD NEW [--format text|json|md]
    cinderfold parse FILE [--format dsl|json]
    cinderfold sql2dsl FILE
    cinderfold pg2dsl FILE
    cinderfold sqlite2dsl FILE
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .diff import diff
from .fingerprint import fingerprint
from .html import to_html
from .migrate import migrate
from .stats import stats
from .parser import parse
from .postgres import from_information_schema
from .render import render
from .report import to_json, to_markdown, to_text
from .sql import parse_sql
from .sqlite import parse_dotschema
from .validate import validate


def _load(path: str):
    text = Path(path).read_text()
    if path.endswith(".sql"):
        return parse_sql(text)
    if path.endswith(".json"):
        return from_information_schema(json.loads(text))
    return parse(text)


def cmd_diff(args) -> int:
    old = _load(args.old)
    new = _load(args.new)
    changes = diff(old, new)
    if args.format == "json":
        sys.stdout.write(to_json(changes))
    elif args.format == "md":
        sys.stdout.write(to_markdown(changes))
    elif args.format == "html":
        sys.stdout.write(to_html(changes))
    else:
        sys.stdout.write(to_text(changes))
    return 1 if changes and args.fail_on and _gate(changes, args.fail_on) else 0


def _gate(changes, fail_on: str) -> bool:
    floor = {"auxiliary": 0, "constraint": 1, "type": 2, "presence": 3}[fail_on]
    return any(c.severity >= floor for c in changes)


def cmd_parse(args) -> int:
    schema = _load(args.file)
    if args.format == "json":
        out = {"tables": [
            {"name": t.name,
             "columns": [c.__dict__ for c in t.columns],
             "indexes": [i.__dict__ for i in t.indexes],
             "foreign_keys": [f.__dict__ for f in t.foreign_keys]}
            for t in schema.tables
        ]}
        sys.stdout.write(json.dumps(out, indent=2, default=list) + "\n")
    else:
        sys.stdout.write(render(schema))
    return 0


def cmd_migrate(args) -> int:
    old = _load(args.old)
    new = _load(args.new)
    for s in migrate(old, new):
        sys.stdout.write(s + "\n")
    return 0


def cmd_fingerprint(args) -> int:
    schema = _load(args.file)
    sys.stdout.write(fingerprint(schema) + "\n")
    return 0


def cmd_stats(args) -> int:
    schema = _load(args.file)
    s = stats(schema)
    sys.stdout.write(
        f"tables={s.tables} columns={s.columns} pks={s.pks} "
        f"indexes={s.indexes} foreign_keys={s.foreign_keys} "
        f"not_null={s.not_null_columns} unique={s.unique_columns} "
        f"density={s.density:.2f}\n"
    )
    return 0


def cmd_validate(args) -> int:
    schema = _load(args.file)
    issues = validate(schema)
    for i in issues:
        sys.stdout.write(f"{i.table}: {i.detail}\n")
    return 1 if issues else 0


def cmd_sql2dsl(args) -> int:
    schema = parse_sql(Path(args.file).read_text())
    sys.stdout.write(render(schema))
    return 0


def cmd_pg2dsl(args) -> int:
    payload = json.loads(Path(args.file).read_text())
    schema = from_information_schema(payload)
    sys.stdout.write(render(schema))
    return 0


def cmd_sqlite2dsl(args) -> int:
    schema = parse_dotschema(Path(args.file).read_text())
    sys.stdout.write(render(schema))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cinderfold")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("diff")
    d.add_argument("old"); d.add_argument("new")
    d.add_argument("--format", choices=["text", "json", "md", "html"], default="text")
    d.add_argument("--fail-on", choices=["presence", "type", "constraint", "auxiliary"])
    d.set_defaults(fn=cmd_diff)

    pa = sub.add_parser("parse")
    pa.add_argument("file"); pa.add_argument("--format", choices=["dsl", "json"], default="dsl")
    pa.set_defaults(fn=cmd_parse)

    m = sub.add_parser("migrate")
    m.add_argument("old"); m.add_argument("new")
    m.set_defaults(fn=cmd_migrate)

    v = sub.add_parser("validate")
    v.add_argument("file")
    v.set_defaults(fn=cmd_validate)

    fp = sub.add_parser("fingerprint")
    fp.add_argument("file")
    fp.set_defaults(fn=cmd_fingerprint)

    st = sub.add_parser("stats")
    st.add_argument("file")
    st.set_defaults(fn=cmd_stats)

    for cmd, fn in (("sql2dsl", cmd_sql2dsl), ("pg2dsl", cmd_pg2dsl),
                    ("sqlite2dsl", cmd_sqlite2dsl)):
        s = sub.add_parser(cmd)
        s.add_argument("file")
        s.set_defaults(fn=fn)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
