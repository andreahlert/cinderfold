from cinderfold.parser import parse


def test_parse_index_inside_table():
    s = parse("""
        table users {
            email: text not_null;
            index ix_users_email (email) unique;
        }
    """)
    t = s.table("users")
    assert len(t.indexes) == 1
    assert t.indexes[0].name == "ix_users_email"
    assert t.indexes[0].columns == ("email",)
    assert t.indexes[0].unique is True


def test_parse_multi_column_index_non_unique():
    s = parse("""
        table orders {
            user_id: int not_null;
            created_at: timestamp not_null;
            index ix_orders_user_created (user_id, created_at);
        }
    """)
    t = s.table("orders")
    assert t.indexes[0].columns == ("user_id", "created_at")
    assert t.indexes[0].unique is False


def test_parse_fkey_simple():
    s = parse("""
        table orders {
            id: int pk not_null;
            user_id: int not_null;
            fk fk_orders_user (user_id) -> users (id);
        }
    """)
    t = s.table("orders")
    assert len(t.foreign_keys) == 1
    fk = t.foreign_keys[0]
    assert fk.name == "fk_orders_user"
    assert fk.columns == ("user_id",)
    assert fk.ref_table == "users"
    assert fk.ref_columns == ("id",)
    assert fk.on_delete == "no_action"


def test_parse_fkey_with_actions():
    s = parse("""
        table orders {
            user_id: int not_null;
            fk fk_orders_user (user_id) -> users (id) on_delete = cascade on_update = restrict;
        }
    """)
    fk = s.table("orders").foreign_keys[0]
    assert fk.on_delete == "cascade"
    assert fk.on_update == "restrict"
