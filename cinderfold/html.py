"""HTML report rendering for diff results.

Single-file output with inline CSS so it can be attached to PR
comments, emailed, or dropped into a CI artifact directory without a
separate stylesheet.
"""

from __future__ import annotations

import html
from typing import Iterable

from .diff import Change


_CSS = """
body { font: 14px/1.4 -apple-system, system-ui, sans-serif; margin: 2em; color: #111; }
h1 { margin: 0 0 .5em; }
section { margin: 1.5em 0; }
h2 { margin: 0 0 .3em; font-size: 1.1em; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: .35em .7em; border-bottom: 1px solid #eee; }
th { background: #fafafa; font-weight: 600; }
.badge { display: inline-block; font-size: .8em; padding: .1em .5em;
         border-radius: 3px; margin-right: .4em; color: #fff; }
.b-presence { background: #c0392b; }
.b-type { background: #d68910; }
.b-constraint { background: #2874a6; }
.b-auxiliary { background: #7f8c8d; }
.empty { color: #777; font-style: italic; }
"""

_TITLES = {
    "presence": "Presence",
    "type": "Type",
    "constraint": "Constraint",
    "auxiliary": "Auxiliary",
}


def to_html(changes: Iterable[Change], title: str = "Schema diff") -> str:
    changes = list(changes)
    body = [f"<h1>{html.escape(title)}</h1>"]
    if not changes:
        body.append('<p class="empty">No changes detected.</p>')
        return _wrap(body, title)

    bucket: dict[str, list[Change]] = {}
    for c in changes:
        bucket.setdefault(c.category, []).append(c)

    for cat in ("presence", "type", "constraint", "auxiliary"):
        items = bucket.get(cat)
        if not items:
            continue
        body.append("<section>")
        body.append(
            f'<h2><span class="badge b-{cat}">{_TITLES[cat]}</span>'
            f" {len(items)} change{'s' if len(items) != 1 else ''}</h2>"
        )
        body.append("<table><thead><tr><th>Table</th><th>Column</th><th>Detail</th></tr></thead><tbody>")
        for c in items:
            col = html.escape(c.column or "")
            body.append(
                f"<tr><td>{html.escape(c.table)}</td>"
                f"<td>{col}</td>"
                f"<td>{html.escape(c.detail)}</td></tr>"
            )
        body.append("</tbody></table></section>")

    return _wrap(body, title)


def _wrap(body: list[str], title: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title>"
        f"<style>{_CSS}</style></head><body>\n"
        + "\n".join(body)
        + "\n</body></html>\n"
    )
