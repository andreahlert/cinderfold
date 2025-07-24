"""Stable content hash for a Schema.

Used by CI to short-circuit drift checks: if the fingerprint matches,
no diff is needed. Sensitive to *any* observable change (column order
matters; column attributes matter). Insensitive to default re-renderings
that round-trip through the model.
"""

from __future__ import annotations

import hashlib
import json

from .model import Schema
from .serial import to_dict


def fingerprint(schema: Schema) -> str:
    payload = json.dumps(to_dict(schema), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def short_fingerprint(schema: Schema, length: int = 12) -> str:
    return fingerprint(schema)[:length]
