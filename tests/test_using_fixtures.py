from cinderfold.diff import diff
from cinderfold.summary import summarize
from cinderfold.compat import compatible


def test_blog_v1_to_v2_summary(blog_v1, blog_v2):
    s = summarize(diff(blog_v1, blog_v2))
    assert s.total > 0
    assert s.max_severity == "presence"


def test_blog_v1_to_v2_is_not_forward_compatible(blog_v1, blog_v2):
    ok, reasons = compatible(blog_v1, blog_v2)
    assert not ok
    assert any("dropped" in r or "->" in r or "NOT NULL" in r for r in reasons)


def test_ecommerce_self_diff_is_empty(ecommerce):
    assert diff(ecommerce, ecommerce) == []
