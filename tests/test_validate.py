from cinderfold.model import Column, ForeignKey, Index, Schema, Table
from cinderfold.validate import validate


def _t(name, cols, indexes=(), fks=()):
    return Table(
        name=name,
        columns=tuple(Column(*c) if isinstance(c, tuple) else c for c in cols),
        indexes=indexes,
        foreign_keys=fks,
    )


def test_clean_schema_has_no_issues():
    s = Schema((
        _t("u", [("id", "int", True, False), ("email", "text", False, False)]),
    ))
    assert validate(s) == []


def test_detects_duplicate_table():
    s = Schema((
        _t("u", [("id", "int", True, False)]),
        _t("u", [("id", "int", True, False)]),
    ))
    issues = validate(s)
    assert any("duplicate table" in i.detail for i in issues)


def test_detects_duplicate_column():
    s = Schema((
        _t("u", [("id", "int", True, False), ("id", "int", False, True)]),
    ))
    issues = validate(s)
    assert any("duplicate column" in i.detail for i in issues)


def test_detects_multiple_pks():
    s = Schema((
        _t("u", [("a", "int", True, False), ("b", "int", True, False)]),
    ))
    assert any("multiple primary keys" in i.detail for i in validate(s))


def test_detects_index_on_unknown_column():
    s = Schema((
        _t("u", [("id", "int", True, False)],
           indexes=(Index("bad", ("missing",)),)),
    ))
    assert any("references unknown column" in i.detail for i in validate(s))


def test_detects_fk_to_unknown_table():
    s = Schema((
        _t("o", [("uid", "int", False, False)],
           fks=(ForeignKey("fko", ("uid",), "users", ("id",)),)),
    ))
    assert any("unknown table" in i.detail for i in validate(s))


def test_detects_fk_to_unknown_column():
    s = Schema((
        _t("u", [("id", "int", True, False)]),
        _t("o", [("uid", "int", False, False)],
           fks=(ForeignKey("fko", ("uid",), "u", ("nope",)),)),
    ))
    assert any("unknown column(s) in u" in i.detail for i in validate(s))
