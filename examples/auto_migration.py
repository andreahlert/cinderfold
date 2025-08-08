"""Example: emit a draft migration file from two DSL snapshots.

The output is intentionally raw DDL with no transaction wrapper, no
backfill scaffolding, and no review checks. Treat it as a first draft
to be reviewed by a human before running against production.
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

from cinderfold.migrate import migrate
from cinderfold.parser import parse


def main(old_path: str, new_path: str, out_dir: str = "migrations") -> int:
    old = parse(Path(old_path).read_text())
    new = parse(Path(new_path).read_text())
    stmts = migrate(old, new)
    if not stmts:
        print("no migration needed", file=sys.stderr)
        return 0

    Path(out_dir).mkdir(exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target = Path(out_dir) / f"{ts}_auto.sql"
    target.write_text("BEGIN;\n\n" + "\n".join(stmts) + "\n\nCOMMIT;\n")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
