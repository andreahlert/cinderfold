from cinderfold.parser import parse
from cinderfold.render import render


def test_roundtrip_simple_table():
    src = """
        table users {
            id: int pk not_null;
            email: text not_null unique;
        }
    """
    schema = parse(src)
    rendered = render(schema)
    re_parsed = parse(rendered)
    assert re_parsed == schema


def test_roundtrip_with_index_and_fk():
    src = """
        table orders {
            id: int pk not_null;
            user_id: int not_null;
            index ix_orders_user (user_id);
            fk fk_orders_user (user_id) -> users (id) on_delete = cascade;
        }
    """
    schema = parse(src)
    re_parsed = parse(render(schema))
    assert re_parsed == schema


def test_roundtrip_default_and_comment():
    src = """
        table x {
            id: int pk not_null;
            at: timestamp not_null default = now() comment = "row birth";
        }
    """
    schema = parse(src)
    re_parsed = parse(render(schema))
    assert re_parsed == schema
