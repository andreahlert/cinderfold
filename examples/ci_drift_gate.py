"""Example: a CI gate that fails the build on presence-level drift.

Reads two DSL files (last green snapshot vs. current HEAD) and exits
non-zero when any table or column has been added or dropped. Constraint
and type changes are reported but don't fail the build, matching the
common 'soft warning' policy.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cinderfold.diff import diff
from cinderfold.filter import filter_changes
from cinderfold.parser import parse
from cinderfold.report import to_text


def main(old_path: str, new_path: str) -> int:
    old = parse(Path(old_path).read_text())
    new = parse(Path(new_path).read_text())
    all_changes = diff(old, new)

    presence = filter_changes(all_changes, min_severity="presence")
    print(to_text(all_changes), end="")
    if presence:
        print(f"\nBUILD FAILED: {len(presence)} presence-level change(s).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
