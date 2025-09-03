"""Shared fixtures: pre-parsed Schemas for the canned DSL fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from cinderfold.parser import parse


_FIX_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _read(name: str):
    return parse((_FIX_DIR / name).read_text())


@pytest.fixture
def blog_v1():
    return _read("blog_v1.dsl")


@pytest.fixture
def blog_v2():
    return _read("blog_v2.dsl")


@pytest.fixture
def ecommerce():
    return _read("ecommerce.dsl")
