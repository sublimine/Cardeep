"""Unit tests for motor_es_wholesale._cursor_window — the pure resumable-cursor function that
makes a BOUNDED facet drain advance across cadence runs (FASE 4 trigger-fix for the 4h-wall
timeout). DB-free: exercises the pure function only.
"""
from __future__ import annotations

import pytest

from pipeline.platform.motor_es_wholesale import _cursor_window

pytestmark = pytest.mark.unit

CELLS = ["a", "b", "c", "d", "e"]  # n = 5


def test_empty_cells_returns_empty_zero():
    assert _cursor_window([], 0, 40) == ([], 0)
    assert _cursor_window([], 7, 40) == ([], 0)


def test_take_zero_keeps_start_modulo_n():
    assert _cursor_window(CELLS, 3, 0) == ([], 3)
    assert _cursor_window(CELLS, 7, 0) == ([], 2)  # 7 % 5 = 2


def test_basic_window_no_wrap():
    assert _cursor_window(CELLS, 0, 2) == (["a", "b"], 2)
    assert _cursor_window(CELLS, 2, 2) == (["c", "d"], 4)


def test_window_wraps_at_end_no_starvation():
    # start near the end -> window wraps to the front so no cell is starved
    assert _cursor_window(CELLS, 4, 3) == (["e", "a", "b"], 2)


def test_take_capped_at_n_never_double_drains():
    # max_cells > n: take is capped at n, next_offset returns to start (full cycle)
    window, nxt = _cursor_window(CELLS, 0, 10)
    assert window == CELLS and nxt == 0
    assert len(window) == len(set(window))  # no cell twice within one window


def test_start_beyond_n_is_modulo():
    assert _cursor_window(CELLS, 7, 2) == (["c", "d"], 4)  # 7 % 5 = 2


def test_successive_runs_cover_every_cell():
    # Repeatedly taking max_cells=2 from the advancing cursor must cover ALL cells
    # within ceil(n/2) runs (the property that makes the bounded slice complete the census).
    seen: set[str] = set()
    offset = 0
    for _ in range((len(CELLS) + 1) // 2):
        window, offset = _cursor_window(CELLS, offset, 2)
        seen.update(window)
    assert seen == set(CELLS)
