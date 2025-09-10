import json

import pytest

from cinderfold.lock import (
    LOCK_VERSION,
    Lock,
    LockMismatch,
    assert_locked,
    build_lock,
    read_lock,
    write_lock,
)
from cinderfold.parser import parse


SRC = "table u { id: int pk not_null; name: text not_null; }"


def test_build_lock_captures_fingerprint_and_count():
    s = parse(SRC)
    lock = build_lock(s, notes="initial")
    assert lock.version == LOCK_VERSION
    assert lock.table_count == 1
    assert lock.notes == "initial"
    assert len(lock.fingerprint) == 64


def test_write_then_read_round_trips(tmp_path):
    s = parse(SRC)
    path = tmp_path / "schema.lock"
    written = write_lock(s, path, notes="pinned")
    loaded = read_lock(path)
    assert written == loaded


def test_lockfile_is_pretty_json(tmp_path):
    s = parse(SRC)
    path = tmp_path / "schema.lock"
    write_lock(s, path)
    raw = path.read_text(encoding="utf-8")
    assert raw.startswith("{\n")
    payload = json.loads(raw)
    assert payload["version"] == LOCK_VERSION


def test_assert_locked_passes_when_unchanged(tmp_path):
    s = parse(SRC)
    path = tmp_path / "schema.lock"
    write_lock(s, path)
    assert_locked(s, path)


def test_assert_locked_flags_drift_with_table_count(tmp_path):
    old = parse(SRC)
    path = tmp_path / "schema.lock"
    write_lock(old, path)
    new = parse(SRC + " table extra { id: int pk not_null; }")
    with pytest.raises(LockMismatch) as exc:
        assert_locked(new, path)
    assert "1 table(s) added" in str(exc.value)


def test_assert_locked_flags_drift_without_table_count_change(tmp_path):
    old = parse(SRC)
    path = tmp_path / "schema.lock"
    write_lock(old, path)
    new = parse("table u { id: int pk not_null; name: text; }")
    with pytest.raises(LockMismatch) as exc:
        assert_locked(new, path)
    assert "table count unchanged" in str(exc.value)


def test_read_lock_rejects_future_version(tmp_path):
    path = tmp_path / "schema.lock"
    path.write_text(json.dumps({
        "version": 99, "fingerprint": "x", "table_count": 0, "notes": "",
    }))
    with pytest.raises(LockMismatch):
        read_lock(path)


def test_lock_equality():
    s = parse(SRC)
    a = build_lock(s)
    b = build_lock(s)
    assert a == b
    assert isinstance(a, Lock)
