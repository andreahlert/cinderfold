from cinderfold.model import Column, ForeignKey, Index, Schema, Table


def test_index_lookup_returns_match_or_none():
    idx = Index(name="ix_users_email", columns=("email",), unique=True)
    t = Table(name="users",
              columns=(Column(name="email", type="text"),),
              indexes=(idx,))
    assert t.index("ix_users_email") is idx
    assert t.index("none") is None


def test_foreign_key_carries_actions():
    fk = ForeignKey(
        name="fk_orders_user",
        columns=("user_id",),
        ref_table="users",
        ref_columns=("id",),
        on_delete="cascade",
        on_update="cascade",
    )
    assert fk.on_delete == "cascade"
    assert fk.on_update == "cascade"


def test_schema_tables_default_no_indexes_or_fks():
    t = Table(name="x", columns=(Column(name="id", type="int", pk=True),))
    s = Schema(tables=(t,))
    assert s.table("x").indexes == ()
    assert s.table("x").foreign_keys == ()
