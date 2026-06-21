"""AS24 facet drilling — block 1: the partitioning engine (adaptive price bands + faceted URL).

AS24 /lst caps at ~200 pages (~4k cars) per search, but honors price filters (verified:
0-2000=498, 2000-4000=2215). So the catalog is drained by partitioning into price bands each
under the cap. This tests the PURE partition planner + URL builder (no I/O); the per-band drain
(block 2) reuses autoscout24_wholesale's parser/ingest.
"""
import pytest

from pipeline.platform.as24_facet import FACET_CAP, _facet_url, plan_price_bands

pytestmark = pytest.mark.unit


def test_facet_url_carries_price_band_and_price_sort():
    u = _facet_url(page=1, price_from=2000, price_to=4000)
    assert "pricefrom=2000" in u
    assert "priceto=4000" in u
    assert "sort=price" in u          # stable pagination (NOT age)
    assert "page=1" in u
    assert "cy=E" in u                # Spain


def test_facet_url_open_top_band_omits_priceto():
    # the last band has no upper bound (priceto omitted or 0) so it catches the tail
    u = _facet_url(page=1, price_from=200000, price_to=None)
    assert "pricefrom=200000" in u
    assert "priceto=&" in u or u.rstrip().endswith("priceto=")


def test_plan_single_band_when_whole_range_under_cap():
    # count always under cap -> exactly one band covering the range
    plan = plan_price_bands(lambda f, t: 100, lo=0, hi=100_000)
    assert plan == [(0, 100_000)]


def test_plan_subdivides_dense_ranges_until_under_cap():
    # dense unless the band is narrow -> planner must bisect
    def count_of(f, t):
        return 100 if (t - f) <= 12_500 else 50_000
    plan = plan_price_bands(count_of, lo=0, hi=100_000)
    assert len(plan) > 1
    # every planned band is under the cap (or hit the min-width floor)
    assert all(count_of(f, t) <= FACET_CAP or (t - f) <= 12_500 for f, t in plan)
    # bands are contiguous and cover the full [0, 100000) range
    assert plan[0][0] == 0
    assert plan[-1][1] == 100_000
    for (a_from, a_to), (b_from, b_to) in zip(plan, plan[1:]):
        assert a_to == b_from   # no gaps, no overlaps
