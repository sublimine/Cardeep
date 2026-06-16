"""Unit tests for the catalogue-photo cross-generation guard (audit pass-4 D7).

The B7 car-dedup photo signal merged two listings sharing a normalized photo_url. Sub-threshold
catalogue/CDN photos (shared by 2-11 listings, below the K=12 high-collision cap) slipped through and
merged cars across generations — a 2008 Citroen C4 (€3,000, 285k km) collapsed with a 2024 C4
(€19,990, 16k km). `_photo_pair_spans_generations` is the pairwise guard that blocks such a merge
while NEVER blocking a genuine duplicate (same physical car has identical year+km). Pure function —
no DB; the re-cluster that applies it across the live corpus is a separate gated op.
"""
from pipeline.identity.cluster_vehicles import _photo_pair_spans_generations


class TestPhotoPairSpansGenerations:
    def test_same_year_km_is_legit_duplicate(self):
        # A genuine cross-platform duplicate has identical year+km -> never blocked (monotonic).
        assert _photo_pair_spans_generations({"year": 2020, "km": 45000},
                                             {"year": 2020, "km": 45000}) is False

    def test_cross_generation_year_blocked(self):
        # The confirmed defect: 2008 C4 vs 2024 C4 sharing a catalogue photo.
        assert _photo_pair_spans_generations({"year": 2008, "km": 285000},
                                             {"year": 2024, "km": 16559}) is True

    def test_small_year_diff_allowed(self):
        # <=2 model-years apart (model-year vs registration fuzz) is allowed.
        assert _photo_pair_spans_generations({"year": 2019, "km": 40000},
                                             {"year": 2021, "km": 42000}) is False

    def test_large_km_span_blocked(self):
        # Same year, but >50k km apart -> not the same physical car.
        assert _photo_pair_spans_generations({"year": 2020, "km": 20000},
                                             {"year": 2020, "km": 200000}) is True

    def test_null_year_or_km_not_blocked(self):
        # Missing data cannot prove a span -> do NOT block (Law I: under-block over mis-block;
        # the km=0/VIN guard and the K=12 cap still apply independently).
        assert _photo_pair_spans_generations({"year": None, "km": None},
                                             {"year": 2020, "km": 5000}) is False
        assert _photo_pair_spans_generations({"year": 2020, "km": None},
                                             {"year": 2024, "km": None}) is True  # year span still catches it
