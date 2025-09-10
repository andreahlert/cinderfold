"""cinderfold: schema drift detection."""

from .diff import Change, diff
from .dump import dump_sql
from .filter import filter_changes
from .fingerprint import fingerprint, short_fingerprint
from .lock import Lock, LockMismatch, assert_locked, build_lock, read_lock, write_lock
from .migrate import migrate
from .model import Column, ForeignKey, Index, Schema, Table
from .parser import ParseError, parse
from .postgres import from_information_schema
from .render import render
from .rename import RenameHint, detect_renames
from .report import to_json, to_markdown, to_text
from .select import exclude, merge, select
from .serial import from_dict, from_json, to_dict, to_json as serial_to_json
from .sql import parse_sql
from .sqlite import parse_dotschema
from .stats import Stats, stats
from .validate import Issue, validate

__version__ = "0.2.0"

__all__ = [
    "Change", "Column", "ForeignKey", "Index", "Issue", "Lock", "LockMismatch",
    "ParseError", "RenameHint", "Schema", "Stats", "Table",
    "assert_locked", "build_lock", "detect_renames", "diff", "dump_sql",
    "exclude", "filter_changes", "fingerprint", "from_dict",
    "from_information_schema", "from_json", "merge", "migrate", "parse",
    "parse_dotschema", "parse_sql", "read_lock", "render", "select",
    "serial_to_json", "short_fingerprint", "stats", "to_dict", "to_json",
    "to_markdown", "to_text", "validate", "write_lock",
]
