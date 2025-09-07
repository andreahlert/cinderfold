from cinderfold.migrate import migrate
from cinderfold.parser import parse


def test_new_tables_created_in_topo_order():
    old = parse("")
    new = parse("""
        table comments { id: int pk not_null; post_id: int not_null;
                         fk fk_c_p (post_id) -> posts (id); }
        table posts { id: int pk not_null; user_id: int not_null;
                      fk fk_p_u (user_id) -> users (id); }
        table users { id: int pk not_null; }
    """)
    stmts = migrate(old, new)
    creates = [s.splitlines()[0] for s in stmts if s.startswith("CREATE TABLE")]
    idx = {c.split()[2]: i for i, c in enumerate(creates)}
    assert idx["users"] < idx["posts"] < idx["comments"]


def test_cycle_falls_back_to_alphabetical():
    old = parse("")
    new = parse("""
        table a { id: int pk not_null; b_id: int not_null;
                  fk fk_a_b (b_id) -> b (id); }
        table b { id: int pk not_null; a_id: int not_null;
                  fk fk_b_a (a_id) -> a (id); }
    """)
    stmts = migrate(old, new)
    creates = [s.splitlines()[0] for s in stmts if s.startswith("CREATE TABLE")]
    assert [c.split()[2] for c in creates] == ["a", "b"]
