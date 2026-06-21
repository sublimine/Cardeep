"""AS24 incremental cursor: harvest must be able to start at an arbitrary page so large
drains don't re-fetch pages 1..N every run (efficiency for the ~278k-car full drain).

Pure unit test of the page-range + URL builders — no I/O.
"""
import pytest

from pipeline.platform.autoscout24_wholesale import _lst_url, _page_range

pytestmark = pytest.mark.unit


def test_page_range_incremental_start():
    # start=201, count=3 -> pages 201,202,203 (NOT 1,2,3): the incremental cursor.
    assert list(_page_range(201, 3)) == [201, 202, 203]


def test_page_range_default_start_is_one():
    # back-compat: a drain that doesn't pass start behaves as before (pages 1..N).
    assert list(_page_range(1, 3)) == [1, 2, 3]


def test_lst_url_carries_the_page_number():
    assert "page=201" in _lst_url(201)
    assert "page=1" in _lst_url(1)
