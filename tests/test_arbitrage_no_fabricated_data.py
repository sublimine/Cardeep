"""Guardrail: web/src/pages/Arbitrage.tsx must NEVER regress to the pre-04-arbitrage-F3 mock.

04-arbitrage.md §9 F3 criterion: "grep = 0 arrays de datos de negocio en el TSX". The page
used to ship `const CHOLLOS: Chollo[] = [...]` / `CROSS_GAPS` / `SPREAD` / `TIME_DATA` —
five hardcoded arrays of business numbers (prices, z-scores, deal savings) rendered as if
they were live data. This test fails if that bug class reappears. Sibling of
tests/test_web_no_fabricated_data.py (same DB-free, pure-file-scan style).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_REPO = Path(__file__).resolve().parent.parent

# The page moved from `web/` to `workspace/` on 2026-07-27 (commit 8cd8c6c) and this
# path did not follow it. The four tests below had been failing with
# FileNotFoundError ever since — which is worse than a red suite, because a
# guardrail that cannot find its target is not failing loudly, it is silently
# guarding nothing. `web/` is now the marketing landing; the app lives in
# `workspace/`. Both are checked so a future move is caught rather than repeated.
_CANDIDATE_TSX = (
    _REPO / "workspace" / "src" / "pages" / "Arbitrage.tsx",
    _REPO / "web" / "src" / "pages" / "Arbitrage.tsx",
)
_ARBITRAGE_TSX = next((p for p in _CANDIDATE_TSX if p.exists()), _CANDIDATE_TSX[0])

# The exact mock identifiers this page shipped before F3 (04-arbitrage.md §1.2). Their
# reappearance ANYWHERE in the file (even renamed-but-reintroduced as a new hardcoded
# array) is the regression this test exists to catch.
_BANNED_MOCK_NAMES = ("CHOLLOS", "CROSS_GAPS", "SPREAD", "TIME_DATA", "MAX_SPREAD_PCT")

# A top-level `const NAME: Type[] = [` or `const NAME = [` immediately followed by a `{`
# (an array-of-object-literals — the fabrication shape) on the SAME or next non-blank line.
_ARRAY_OF_OBJECTS_RE = re.compile(r"^const\s+[A-Z_][A-Z0-9_]*(?:\s*:\s*\w+\[\])?\s*=\s*\[", re.MULTILINE)


def test_arbitrage_page_exists():
    assert _ARBITRAGE_TSX.is_file(), f"{_ARBITRAGE_TSX} not found — has the page moved?"


def test_no_banned_pre_f3_mock_identifiers():
    src = _ARBITRAGE_TSX.read_text(encoding="utf-8")
    offenders = [name for name in _BANNED_MOCK_NAMES if re.search(rf"\b{name}\b", src)]
    assert not offenders, (
        f"Arbitrage.tsx re-introduces pre-F3 mock identifier(s) {offenders} — every number on this "
        "page must come from /arbitrage/* (services/api/routers/arbitrage.py), never a hardcoded array."
    )


def test_no_top_level_array_of_object_literals():
    """No `const X = [{...}, {...}]` business-data array anywhere in the file."""
    src = _ARBITRAGE_TSX.read_text(encoding="utf-8")
    offenders = [m.group(0) for m in _ARRAY_OF_OBJECTS_RE.finditer(src)]
    assert not offenders, (
        "Arbitrage.tsx declares a top-level array literal — this is the exact shape of the pre-F3 "
        f"mock (CHOLLOS/CROSS_GAPS/SPREAD/TIME_DATA): {offenders}"
    )


def test_imports_the_arbitrage_api_client():
    """The page must actually consume the live client, not just avoid mock arrays."""
    src = _ARBITRAGE_TSX.read_text(encoding="utf-8")
    assert "from '../api/cardeep'" in src, "Arbitrage.tsx must import the cardeep API client"
    for fn in ("arbitrageSummary", "arbitrageDeals", "arbitrageDesync", "arbitrageTimeCurves", "arbitrageGeo"):
        assert fn in src, f"Arbitrage.tsx must call cardeep.{fn}(...) — found no reference to {fn!r}"
