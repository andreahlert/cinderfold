import pytest

from cinderfold.graph import dependencies, reverse_dependencies, topo_order


def test_dependencies(blog_v1):
    assert dependencies(blog_v1, "posts") == {"users"}
    assert dependencies(blog_v1, "comments") == {"posts"}
    assert dependencies(blog_v1, "users") == set()


def test_reverse_dependencies(blog_v1):
    assert reverse_dependencies(blog_v1, "users") == {"posts"}
    assert reverse_dependencies(blog_v1, "posts") == {"comments"}
    assert reverse_dependencies(blog_v1, "comments") == set()


def test_topo_order_parents_first(blog_v1):
    order = topo_order(blog_v1)
    assert order.index("users") < order.index("posts") < order.index("comments")


def test_topo_order_ecommerce(ecommerce):
    order = topo_order(ecommerce)
    assert order.index("customers") < order.index("orders")
    assert order.index("orders") < order.index("order_items")
    assert order.index("products") < order.index("inventory")


def test_topo_cycle_detected():
    from cinderfold.parser import parse
    s = parse("""
        table a { id: int pk not_null; b_id: int not_null;
                  fk fk_a_b (b_id) -> b (id); }
        table b { id: int pk not_null; a_id: int not_null;
                  fk fk_b_a (a_id) -> a (id); }
    """)
    with pytest.raises(ValueError, match="cycle"):
        topo_order(s)
