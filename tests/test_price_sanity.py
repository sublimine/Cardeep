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
