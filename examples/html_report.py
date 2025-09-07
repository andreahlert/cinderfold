"""Example: produce an HTML drift report for embedding in CI artifacts.

Reads two DSL files and writes an HTML file to disk. The HTML is
self-contained (inline CSS); no external assets are required.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cinderfold.diff import diff
from cinderfold.html import to_html
from cinderfold.parser import parse


def main(old_path: str, new_path: str, out_path: str = "drift.html") -> int:
    old = parse(Path(old_path).read_text())
    new = parse(Path(new_path).read_text())
    changes = diff(old, new)
    Path(out_path).write_text(to_html(changes, title=f"{old_path} -> {new_path}"))
    print(f"wrote {out_path} ({len(changes)} changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
