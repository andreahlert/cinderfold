from cinderfold.parser import parse


def test_line_comment_ignored():
    src = """
        // top comment
        table u {  // inline comment
            id: int pk not_null; // trailing
            // another
            email: text;
        }
    """
    s = parse(src)
    assert s.table("u").columns[0].name == "id"
    assert s.table("u").columns[1].name == "email"


def test_block_comment_ignored():
    src = """
        /* license header
           spans many
           lines */
        table u {
            id: int pk not_null;
            /* dropping name for now
               name: text; */
            email: text;
        }
    """
    s = parse(src)
    names = [c.name for c in s.table("u").columns]
    assert names == ["id", "email"]


def test_block_comment_inside_attrs():
    src = "table u { id: int /* pk maybe */ pk not_null; }"
    s = parse(src)
    assert s.table("u").columns[0].pk is True
