"""Example: list every table that depends on a given table.

Useful before dropping or restructuring a 'hub' table; the output is
the set of downstream tables that need a coordinated migration.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cinderfold.graph import reverse_dependencies, topo_order
from cinderfold.parser import parse


def main(dsl_path: str, table: str) -> int:
    schema = parse(Path(dsl_path).read_text())
    direct = reverse_dependencies(schema, table)
    order = {n: i for i, n in enumerate(topo_order(schema))}
    print(f"direct dependents of {table}:")
    for name in sorted(direct, key=order.get):
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
