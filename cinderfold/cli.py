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
from .parser import parse
from .postgres import from_information_schema
from .render import render
from .report import to_json, to_markdown, to_text
from .sql import parse_sql
from .sqlite import parse_dotschema


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
    d.add_argument("--format", choices=["text", "json", "md"], default="text")
    d.add_argument("--fail-on", choices=["presence", "type", "constraint", "auxiliary"])
    d.set_defaults(fn=cmd_diff)

    pa = sub.add_parser("parse")
    pa.add_argument("file"); pa.add_argument("--format", choices=["dsl", "json"], default="dsl")
    pa.set_defaults(fn=cmd_parse)

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
