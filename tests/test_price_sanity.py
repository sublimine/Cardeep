"""Unit tests for the price sanity guard (audit P2 A-junk-sentinel-prices)."""
from decimal import Decimal

from pipeline.price_sanity import sanitize_price


class TestSanitizePrice:
    def test_junk_high_and_nonpositive_nulled(self):
        assert sanitize_price(999_999_999) is None      # Peugeot 206 at ~€1B
        assert sanitize_price(250_000_000) is None       # VW Tiguan at €250M
        assert sanitize_price(10_000_001) is None        # just over the ceiling
        assert sanitize_price(0) is None                 # not a real price
        assert sanitize_price(-5) is None
        assert sanitize_price(None) is None

    def test_legit_prices_preserved(self):
        # Mass-market and luxury up to the verified used-market max are kept.
        assert sanitize_price(15_000) == 15_000
        assert sanitize_price(99_999) == 99_999          # legit price-point, NOT a sentinel
        assert sanitize_price(1_100_000) == 1_100_000    # Aston Martin Valhalla
        assert sanitize_price(2_200_000) == 2_200_000    # Lamborghini Countach (legit hypercar)
        assert sanitize_price(Decimal("18500.00")) == Decimal("18500.00")

    def test_boundary(self):
        assert sanitize_price(10_000_000) == 10_000_000  # exactly the ceiling is allowed
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
