"""Unit tests for services.api.deps.page_slice — honest N+1 pagination (frontend audit #7).

The bug: handlers computed has_more = (len(rows) == size), which is True even on the LAST real page when
the total is an exact multiple of size -> the frontend then requested a phantom empty next page. The fix
over-fetches LIMIT size+1 and page_slice returns (rows[:size], has_more = len(rows) > size). DB-free, so
it runs in CI on every push and permanently guards the logic.
"""
from __future__ import annotations

import pytest

from services.api.deps import page_slice

pytestmark = pytest.mark.unit


def test_more_rows_than_size_signals_has_more():
    # Fetched size+1 (11) -> there IS another page; return exactly size (10).
    rows, has_more = page_slice(list(range(11)), 10)
    assert rows == list(range(10))
    assert has_more is True


def test_exact_multiple_is_the_last_page_no_phantom():
    # The bug case: exactly `size` rows came back (LIMIT size+1 found no extra) -> this is the LAST page,
    # has_more MUST be False (the old len==size test wrongly said True -> phantom empty next page).
    rows, has_more = page_slice(list(range(10)), 10)
    assert rows == list(range(10))
    assert has_more is False


def test_partial_page_no_more():
    rows, has_more = page_slice(list(range(3)), 10)
    assert rows == list(range(3))
    assert has_more is False


def test_empty_page_no_more():
    assert page_slice([], 10) == ([], False)


def test_size_one_boundary():
    assert page_slice([0, 1], 1) == ([0], True)   # extra row -> more
    assert page_slice([0], 1) == ([0], False)     # last single row -> no phantom next page
