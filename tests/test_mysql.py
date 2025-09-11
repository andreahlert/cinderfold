from cinderfold.mysql import dump_mysql
from cinderfold.parser import parse


def test_dump_uses_backticks_and_engine_suffix():
    s = parse("table u { id: int pk not_null; email: text not_null unique; }")
    out = dump_mysql(s)
    assert "CREATE TABLE `u`" in out
    assert "`id`" in out
    assert "`email`" in out
    assert "ENGINE=InnoDB" in out
    assert "DEFAULT CHARSET=utf8mb4" in out


def test_auto_increment_on_int_pk():
    s = parse("table u { id: int pk not_null; }")
    out = dump_mysql(s)
    assert "AUTO_INCREMENT" in out
    assert "PRIMARY KEY" in out


def test_no_auto_increment_on_text_pk():
    s = parse("table u { code: text pk not_null; }")
    out = dump_mysql(s)
    assert "AUTO_INCREMENT" not in out
    assert "PRIMARY KEY" in out


def test_fk_emitted_inline_with_actions():
    s = parse("""
        table u { id: int pk not_null; }
        table o { id: int pk not_null; user_id: int not_null;
                  fk fk_ou (user_id) -> u (id) on_delete = cascade; }
    """)
    out = dump_mysql(s)
    assert "CONSTRAINT `fk_ou` FOREIGN KEY (`user_id`)" in out
    assert "REFERENCES `u` (`id`)" in out
    assert "ON DELETE CASCADE" in out


def test_index_uses_key_keyword():
    s = parse("table u { id: int pk not_null; e: text; index ix_e (e); }")
    out = dump_mysql(s)
    assert "KEY `ix_e` (`e`)" in out


def test_unique_index_inline():
    s = parse("table u { id: int pk not_null; e: text; index ix_e (e) unique; }")
    out = dump_mysql(s)
    assert "UNIQUE KEY `ix_e`" in out


def test_comment_escapes_single_quotes():
    s = parse('table u { id: int pk not_null; n: text comment = "it\'s fine"; }')
    out = dump_mysql(s)
    assert "COMMENT 'it''s fine'" in out


def test_default_emitted():
    s = parse("table u { id: int pk not_null; created_at: timestamp default = now(); }")
    out = dump_mysql(s)
    assert "DEFAULT now()" in out


def test_multiple_tables_separated_by_blank_line():
    s = parse("table a { id: int pk not_null; } table b { id: int pk not_null; }")
    out = dump_mysql(s)
    assert "\n\n" in out
