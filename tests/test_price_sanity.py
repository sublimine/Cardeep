"""Unit tests for the price sanity guard (audit P2 A-junk-sentinel-prices)."""
from decimal import Decimal

from pipeline.price_sanity import sanitize_price


class TestSanitizePrice:
    def test_junk_high_and_nonpositive_nulled(self):
        assert sanitize_price(999_999_999) is None      # Peugeot 206 at ~€1B
        assert sanitize_price(250_000_000) is None       # VW Tiguan at €250M
        # The 2026-06-16 coherence audit found these SERVED at the surface (a visible lie):
        assert sanitize_price(10_000_000) is None        # Nissan Qashqai @ €10M sentinel
        assert sanitize_price(9_999_999) is None         # truck "all-9s" price-on-request sentinel
        assert sanitize_price(5_000_001) is None         # just over the €5M ceiling
        assert sanitize_price(0) is None                 # not a real price
        assert sanitize_price(-5) is None
        assert sanitize_price(None) is None

    def test_legit_prices_preserved(self):
        # Mass-market and REAL hypercars up to the verified used-market max (~€3.6M) are kept.
        assert sanitize_price(15_000) == 15_000
        assert sanitize_price(99_999) == 99_999          # legit price-point, NOT a sentinel
        assert sanitize_price(1_100_000) == 1_100_000    # Aston Martin Valhalla
        assert sanitize_price(2_200_000) == 2_200_000    # Lamborghini Countach (legit hypercar)
        assert sanitize_price(3_300_000) == 3_300_000    # Aston Martin Valkyrie (verified live)
        assert sanitize_price(3_600_000) == 3_600_000    # Bugatti Chiron (verified live, real ceiling)
        assert sanitize_price(Decimal("18500.00")) == Decimal("18500.00")

    def test_boundary(self):
        assert sanitize_price(5_000_000) == 5_000_000    # exactly the €5M ceiling is allowed
        assert sanitize_price(5_000_001) is None          # one euro over → nulled
        assert sanitize_price(1) == 1                     # tiny but positive -> price_trap's job, not nulled here


class TestSanitizeKm:
    def test_impossible_nulled(self):
        from pipeline.price_sanity import sanitize_km
        assert sanitize_km(5_000_000) is None    # digit-concatenation artifact
        assert sanitize_km(1_500_001) is None
        assert sanitize_km(-1) is None
        assert sanitize_km(None) is None

    def test_plausible_preserved(self):
        from pipeline.price_sanity import sanitize_km
        assert sanitize_km(0) == 0               # new car
        assert sanitize_km(120_000) == 120_000
        assert sanitize_km(950_000) == 950_000   # legit high-mileage commercial


class TestSanitizeYear:
    def test_artifact_nulled(self):
        from datetime import datetime
        from pipeline.price_sanity import sanitize_year
        assert sanitize_year(2098) is None       # 'SEAT Ibiza 2098'
        assert sanitize_year(2060) is None
        assert sanitize_year(1899) is None
        assert sanitize_year(datetime.now().year + 2) is None
        assert sanitize_year(None) is None

    def test_plausible_preserved(self):
        from datetime import datetime
        from pipeline.price_sanity import sanitize_year
        assert sanitize_year(2015) == 2015
        assert sanitize_year(1925) == 1925       # genuine classic
        assert sanitize_year(datetime.now().year + 1) == datetime.now().year + 1  # next model-year


class TestSanitizeYearKm:
    """Cross-field impossible-age gate (audit P8). NULL BOTH when a ~0-1-yr car has impossible km."""

    def test_impossible_age_km_nulls_both(self):
        from datetime import datetime
        from pipeline.price_sanity import sanitize_year_km
        cur = datetime.now().year
        assert sanitize_year_km(cur, 350_000) == (None, None)       # 0-yr car, >300k km
        assert sanitize_year_km(cur - 1, 940_000) == (None, None)   # DAF XF "2025" @ 940k (served pre-fix)
        assert sanitize_year_km(cur - 1, 500_001) == (None, None)   # just over the 1-yr/500k bar

    def test_legit_or_fuzzy_preserved(self):
        from datetime import datetime
        from pipeline.price_sanity import sanitize_year_km
        cur = datetime.now().year
        assert sanitize_year_km(cur - 1, 400_000) == (cur - 1, 400_000)  # 1-yr @ 400k: commercial-plausible, LEFT
        assert sanitize_year_km(cur, 250_000) == (cur, 250_000)          # 0-yr @ 250k: below the bar, LEFT
        assert sanitize_year_km(2010, 400_000) == (2010, 400_000)        # old car, high km: legit
        assert sanitize_year_km(cur, 0) == (cur, 0)                      # new car, 0 km
        assert sanitize_year_km(None, 900_000) == (None, 900_000)        # year None -> can't cross-check
        assert sanitize_year_km(cur, None) == (cur, None)                # km None -> can't cross-check
