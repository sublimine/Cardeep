"""Tests for dealer-identity stability in oem_mercedes_benz_wholesale.

Regression suite for the entity-explosion bug where cdp_code_dealer() used the
per-car dealerCode prefix (from "<dealerCode>-<carCode>") as an address discriminant,
producing ~1 entity per vehicle instead of 1 entity per installation.

Fix (pipeline/platform/oem_mercedes_benz_wholesale.py, cdp_code_dealer):
  address=None  -- identity is purely name + municipality_code (never fragments)
instead of:
  address=f"dealer:{d.dealer_id}"  -- varied per-car (explosion root cause)

The connector emits a CONSERVATIVE identity (name + municipality). The postal code is
deliberately NOT a discriminant here: a card that fails to parse its postal would
otherwise split off into a second entity, re-introducing the very fragmentation this
fix erases. Splitting two genuine same-name/same-municipality installations apart is
the entity_cluster's job (B1.3), not the connector's. Same rule as das_weltauto.

Confirmed explosion before fix:
  MOBILITY CENTRO   / muni 28134 -> 480 distinct cdp_codes for 488 vehicles (ratio 1.02)
  Star Madrid Retail / muni 28079 -> 446 distinct cdp_codes for 455 vehicles
"""
from __future__ import annotations

from pipeline.platform.oem_mercedes_benz_wholesale import DealerRef, cdp_code_dealer


def _dealer(
    dealer_id: str,
    name: str,
    postal_code: str | None,
    city: str | None,
    province_code: str | None,
) -> DealerRef:
    """Construct a DealerRef as parse_card_dealer() would, for a given listing card."""
    return DealerRef(
        dealer_id=dealer_id,
        name=name,
        province_code=province_code,
        city=city,
        postal_code=postal_code,
    )


# ---------------------------------------------------------------------------
# Positive: same physical dealer, different cars -> one cdp_code
# ---------------------------------------------------------------------------

class TestSamePhysicalDealerProducesOneCode:
    """N vehicles from the same installation (same name + municipality) must collapse
    to one cdp_code regardless of the per-car dealerCode prefix or the parsed postal.
    This is the core regression for the explosion bug.
    """

    MUNI = "28134"

    def test_two_cars_same_dealer_collapse(self) -> None:
        """Two cars from MOBILITY CENTRO with different listing prefixes -> same code."""
        a = _dealer("10001", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        b = _dealer("10002", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        assert cdp_code_dealer(a, self.MUNI) == cdp_code_dealer(b, self.MUNI)

    def test_extreme_id_diff_same_dealer_collapse(self) -> None:
        """A wildly different numeric prefix still collapses to the same dealer."""
        a = _dealer("10001", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        c = _dealer("99999", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        assert cdp_code_dealer(a, self.MUNI) == cdp_code_dealer(c, self.MUNI)

    def test_three_cars_one_code(self) -> None:
        """Three cards, three different dealer_id prefixes -> one unique cdp_code."""
        base = dict(name="MOBILITY CENTRO", postal_code="28034",
                    city="Las Rozas de Madrid", province_code="28")
        codes = {
            cdp_code_dealer(_dealer(did, **base), self.MUNI)  # type: ignore[arg-type]
            for did in ("10001", "10002", "99999")
        }
        assert len(codes) == 1, f"Expected 1 unique cdp_code, got {len(codes)}: {codes}"

    def test_postal_does_not_fragment(self) -> None:
        """Two cards of the same dealer, one with a parsed postal and one without,
        must STILL collapse — the postal is intentionally NOT part of the connector
        identity (preventing fragmentation when a card's location line fails to parse)."""
        with_p = _dealer("10001", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        no_p = _dealer("10002", "MOBILITY CENTRO", None, "Las Rozas de Madrid", "28")
        assert cdp_code_dealer(with_p, self.MUNI) == cdp_code_dealer(no_p, self.MUNI)

    def test_deterministic_across_calls(self) -> None:
        """Same inputs -> same code on repeated calls (no randomness)."""
        ref = _dealer("10001", "MOBILITY CENTRO", "28034", "Las Rozas de Madrid", "28")
        assert cdp_code_dealer(ref, self.MUNI) == cdp_code_dealer(ref, self.MUNI)


# ---------------------------------------------------------------------------
# Negative: genuinely distinct dealers -> distinct cdp_codes
# ---------------------------------------------------------------------------

class TestDistinctDealersProduceDifferentCodes:
    """Different name OR different municipality/province must NOT collapse."""

    def test_different_name_same_municipality(self) -> None:
        """Two dealers in the same municipality but different names -> distinct codes."""
        mob = _dealer("10001", "MOBILITY CENTRO", "28034", "Las Rozas", "28")
        star = _dealer("10002", "Star Madrid Retail", "28034", "Las Rozas", "28")
        assert cdp_code_dealer(mob, "28134") != cdp_code_dealer(star, "28134")

    def test_same_name_different_municipality(self) -> None:
        """Same brand name in two different municipalities -> two installations."""
        a = _dealer("10001", "STAR AUTO", "28034", "Las Rozas", "28")
        b = _dealer("10002", "STAR AUTO", "28079", "Madrid", "28")
        assert cdp_code_dealer(a, "28134") != cdp_code_dealer(b, "28079")

    def test_different_province(self) -> None:
        """Same name in different provinces -> distinct codes (province-scoped)."""
        mad = _dealer("10001", "AUTO CENTER", "28034", "Madrid", "28")
        bcn = _dealer("10002", "AUTO CENTER", "08034", "Barcelona", "08")
        assert cdp_code_dealer(mad, "28079") != cdp_code_dealer(bcn, "08019")
