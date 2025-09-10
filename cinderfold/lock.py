"""Schema lockfile: pin a schema's fingerprint and assert against drift.

A lockfile is a small JSON document:

    {"version": 1, "fingerprint": "<sha256>", "table_count": N, "notes": "..."}

The intended flow:
    1. write_lock(schema, path)  # commit alongside DSL
    2. CI calls assert_locked(schema, path) and fails on drift.

`assert_locked` raises `LockMismatch` whose message lists the kind of
change so the CI log is actionable without rerunning the diff.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .fingerprint import fingerprint
from .model import Schema


LOCK_VERSION = 1


class LockMismatch(Exception):
    pass


@dataclass(frozen=True)
class Lock:
    version: int
    fingerprint: str
    table_count: int
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "fingerprint": self.fingerprint,
            "table_count": self.table_count,
            "notes": self.notes,
        }


def build_lock(schema: Schema, notes: str = "") -> Lock:
    return Lock(
        version=LOCK_VERSION,
        fingerprint=fingerprint(schema),
        table_count=len(schema.tables),
        notes=notes,
    )


def write_lock(schema: Schema, path: str | Path, notes: str = "") -> Lock:
    lock = build_lock(schema, notes=notes)
    Path(path).write_text(
        json.dumps(lock.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return lock


def read_lock(path: str | Path) -> Lock:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("version") != LOCK_VERSION:
        raise LockMismatch(
            f"lockfile version mismatch: got {data.get('version')!r}, "
            f"expected {LOCK_VERSION}"
        )
    return Lock(
        version=data["version"],
        fingerprint=data["fingerprint"],
        table_count=int(data["table_count"]),
        notes=data.get("notes", ""),
    )


def assert_locked(schema: Schema, path: str | Path) -> None:
    locked = read_lock(path)
    current = build_lock(schema, notes=locked.notes)
    if current.fingerprint == locked.fingerprint:
        return
    delta = current.table_count - locked.table_count
    if delta != 0:
        verb = "added" if delta > 0 else "dropped"
        raise LockMismatch(
            f"schema drift: fingerprint {locked.fingerprint[:12]} -> "
            f"{current.fingerprint[:12]}, {abs(delta)} table(s) {verb}"
        )
    raise LockMismatch(
        f"schema drift: fingerprint {locked.fingerprint[:12]} -> "
        f"{current.fingerprint[:12]}, table count unchanged"
    )
