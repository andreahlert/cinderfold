from cinderfold.audit import AuditEntry, audit, to_markdown
from cinderfold.parser import parse


V1 = "table u { id: int pk not_null; }"
V2 = "table u { id: int pk not_null; email: text not_null; }"
V3 = "table u { id: int pk not_null; email: text not_null; } table p { id: int pk not_null; }"


def test_audit_empty_for_no_snapshots():
    assert audit([]) == []


def test_audit_first_snapshot_diffs_against_empty():
    entries = audit([("2025-01-01", parse(V1))])
    assert len(entries) == 1
    assert any("table added" in c.detail for c in entries[0].changes)


def test_audit_skips_no_op_revisions():
    s = parse(V1)
    entries = audit([("2025-01-01", s), ("2025-02-01", s)])
    assert len(entries) == 1
    assert entries[0].date == "2025-01-01"


def test_audit_chains_consecutive_diffs():
    entries = audit([
        ("2025-01-01", parse(V1)),
        ("2025-02-01", parse(V2)),
        ("2025-03-01", parse(V3)),
    ])
    assert [e.date for e in entries] == ["2025-01-01", "2025-02-01", "2025-03-01"]


def test_to_markdown_renders_dated_sections():
    entries = audit([
        ("2025-01-01", parse(V1)),
        ("2025-02-01", parse(V2)),
    ])
    md = to_markdown(entries)
    assert "# Schema changelog" in md
    assert "## 2025-01-01" in md
    assert "## 2025-02-01" in md
    assert "**presence**" in md


def test_to_markdown_handles_empty():
    md = to_markdown([])
    assert "_No changes recorded._" in md


def test_audit_entry_is_frozen():
    e = AuditEntry(date="2025-01-01", changes=())
    try:
        e.date = "x"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("AuditEntry should be frozen")


def test_severity_ordering_within_a_date():
    s_old = parse(V1)
    s_new = parse(V3)
    entries = audit([("2025-01-01", s_old), ("2025-02-01", s_new)])
    md = to_markdown(entries)
    presence_pos = md.find("**presence**")
    auxiliary_pos = md.find("**auxiliary**")
    if auxiliary_pos != -1:
        assert presence_pos < auxiliary_pos
