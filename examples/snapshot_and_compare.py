"""Example: snapshot a live SQLite DB and compare against a checked-in DSL.

Run sqlite3's `.schema` against a DB, then parse it through cinderfold's
sqlite adapter, then diff against an expected schema. Useful as a daily
job that watches for unintended schema drift in staging.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from cinderfold.diff import diff
from cinderfold.parser import parse
from cinderfold.report import to_markdown
from cinderfold.sqlite import parse_dotschema


def snapshot(db_path: str) -> str:
    out = subprocess.run(
        ["sqlite3", db_path, ".schema"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout


def main(db_path: str, expected_dsl: str) -> int:
    live = parse_dotschema(snapshot(db_path))
    expected = parse(Path(expected_dsl).read_text())
    changes = diff(expected, live)
    print(to_markdown(changes))
    return 0 if not changes else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
