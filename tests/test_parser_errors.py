import pytest

from cinderfold.parser import ParseError, parse


def test_lex_error_reports_line_and_column():
    src = "table u {\n    id: int pk not_null;\n    bad @ here;\n}\n"
    with pytest.raises(ParseError) as exc:
        parse(src)
    assert "line 3" in str(exc.value)
    assert "col" in str(exc.value)


def test_unterminated_default():
    with pytest.raises(ParseError):
        parse("table u { id: int default = func(; }")


def test_missing_semicolon():
    with pytest.raises(ParseError):
        parse("table u { id: int pk not_null }")


def test_missing_brace():
    with pytest.raises(ParseError):
        parse("table u id: int pk not_null;")
