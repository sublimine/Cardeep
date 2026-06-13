"""Tests for the Das WeltAuto dealer identity stability fix.

Regression suite for the B1.0 fix: cdp_code_dealer() must produce a single,
per-physical-installation cdp_code regardless of which InformationBnr variant
the portal emits for a given dealership.

Root cause: Das WeltAuto emits the Bnr in at least two formats per dealership
depending on the certified brand (VW/SEAT/SKODA/CUPRA/Audi):
  - '0'-prefixed  (e.g. '0311K', '03395', '0A311')
  - 'C'-prefixed  (e.g. 'C311K', 'C3395', 'CA311')
  - pure numeric  (e.g. '30060' — third variant seen on J.R. VALLE)

Before the fix, address=f"bnr:{d.bnr}" caused each Bnr variant to hash to a
distinct cdp_code, fragmenting one physical dealer into 2-3 CARDEEP entities.
After the fix, address=None removes the Bnr from the identity hash; the Bnr is
preserved as source_ref in entity_source for cross-source traceability only.
"""
from __future__ import annotations

import pytest

from pipeline.platform.dasweltauto_wholesale import DealerRef, cdp_code_dealer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dealer(bnr: str, name: str = "AUTOS JUANJO",
            province_code: str = "28", city: str = "ALGETE",
            postal_code: str = "28110") -> DealerRef:
    """Build a DealerRef with controllable BNR and stable location fields."""
    return DealerRef(
        bnr=bnr,
        name=name,
        province_code=province_code,
        city=city,
        postal_code=postal_code,
    )


# ---------------------------------------------------------------------------
# Positive cases: same physical dealer → one cdp_code
# ---------------------------------------------------------------------------


class TestSameDealerSameMunicipality:
    """Three vehicles from the same physical dealership with distinct BNR variants
    must all resolve to the same cdp_code (one entity, not N)."""

    def test_bnr_0prefix_and_cprefix_produce_same_code(self) -> None:
        """AUTOS JUANJO (real DB data): BNRs '0311K' and 'C311K' → identical code."""
        muni = "28106"
        d0 = _dealer("0311K")
        dc = _dealer("C311K")
        assert cdp_code_dealer(d0, muni) == cdp_code_dealer(dc, muni)

    def test_bnr_oprefix_and_cprefix_castellana_motor(self) -> None:
        """CASTELLANA MOTOR (real DB data): BNRs '0A111' and 'CA111' → identical code."""
        muni = "28079"
        d0 = _dealer("0A111", name="CASTELLANA MOTOR")
        dc = _dealer("CA111", name="CASTELLANA MOTOR")
        assert cdp_code_dealer(d0, muni) == cdp_code_dealer(dc, muni)

    def test_bnr_three_variants_jr_valle(self) -> None:
        """J.R. VALLE (real DB data): three BNR variants '0333B', 'C333B', '30060' → same code."""
        muni = "46223"
        d1 = _dealer("0333B", name="J.R. VALLE", province_code="46",
                     city="TORRENT", postal_code="46900")
        d2 = _dealer("C333B", name="J.R. VALLE", province_code="46",
                     city="TORRENT", postal_code="46900")
        d3 = _dealer("30060", name="J.R. VALLE", province_code="46",
                     city="TORRENT", postal_code="46900")
        code1 = cdp_code_dealer(d1, muni)
        code2 = cdp_code_dealer(d2, muni)
        code3 = cdp_code_dealer(d3, muni)
        assert code1 == code2 == code3, (
            f"All three BNR variants must produce one code; got {code1}, {code2}, {code3}"
        )

    def test_bnr_numeric_only_miferauto(self) -> None:
        """MIFERAUTO (real DB data): BNRs '03395' and 'C3395' → same code."""
        muni = "46145"
        d0 = _dealer("03395", name="MIFERAUTO", province_code="46",
                     city="ALDAIA", postal_code="46960")
        dc = _dealer("C3395", name="MIFERAUTO", province_code="46",
                     city="ALDAIA", postal_code="46960")
        assert cdp_code_dealer(d0, muni) == cdp_code_dealer(dc, muni)

    def test_cdp_code_format(self) -> None:
        """Output must match the CDP-ES-{province}-{8chars} format."""
        muni = "28106"
        code = cdp_code_dealer(_dealer("0311K"), muni)
        parts = code.split("-")
        assert parts[0] == "CDP"
        assert parts[1] == "ES"
        assert parts[2] == "28"
        assert len(parts[3]) == 8
        # Crockford base32 alphabet (no I, L, O, U)
        assert all(c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for c in parts[3])

    def test_code_is_stable_across_calls(self) -> None:
        """cdp_code_dealer is deterministic: same inputs always produce the same code."""
        d = _dealer("C311K")
        muni = "28106"
        assert cdp_code_dealer(d, muni) == cdp_code_dealer(d, muni)


# ---------------------------------------------------------------------------
# Negative cases: distinct dealers → distinct cdp_codes
# ---------------------------------------------------------------------------


class TestDistinctDealersDifferentCodes:
    """Two dealerships that differ in name OR municipality must get distinct codes
    so no legitimate dealer is merged into another."""

    def test_different_name_same_municipality(self) -> None:
        """GIL AUTOMOCIÓN and AUTOS JUANJO share no physical identity → different codes."""
        muni = "28106"
        d_juanjo = _dealer("0311K", name="AUTOS JUANJO")
        d_gil = _dealer("03175", name="GIL AUTOMOCION DE HENARES")
        assert cdp_code_dealer(d_juanjo, muni) != cdp_code_dealer(d_gil, muni)

    def test_same_name_different_municipality(self) -> None:
        """Two branches of a chain in different municipalities are distinct entities."""
        muni_madrid = "28079"
        muni_bcn = "08019"
        name = "AUTOCENTER"
        d_mad = _dealer("30838", name=name, province_code="28", postal_code="28001")
        d_bcn = _dealer("31158", name=name, province_code="08", postal_code="08001")
        assert cdp_code_dealer(d_mad, muni_madrid) != cdp_code_dealer(d_bcn, muni_bcn)

    def test_same_bnr_different_name_different_code(self) -> None:
        """Same Bnr with a different name (hypothetical data mismatch) → different codes.
        This documents that name is a first-class identity component."""
        muni = "28106"
        d1 = _dealer("0311K", name="AUTOS JUANJO")
        d2 = _dealer("0311K", name="AUTOCENTER MADRID")
        assert cdp_code_dealer(d1, muni) != cdp_code_dealer(d2, muni)

    def test_levante_motor_and_miferauto_different_codes(self) -> None:
        """Two real Valencia dealers that were previously fragmented: after the fix they
        each converge to one code, but their single codes remain distinct from each other."""
        muni_levante = "46250"
        muni_mifer = "46145"
        lev0 = _dealer("0A311", name="LEVANTE MOTOR", province_code="46",
                       city="ALZIRA", postal_code="46600")
        levc = _dealer("CA311", name="LEVANTE MOTOR", province_code="46",
                       city="ALZIRA", postal_code="46600")
        mif0 = _dealer("03395", name="MIFERAUTO", province_code="46",
                       city="ALDAIA", postal_code="46960")
        mifc = _dealer("C3395", name="MIFERAUTO", province_code="46",
                       city="ALDAIA", postal_code="46960")
        lev_code = cdp_code_dealer(lev0, muni_levante)
        mif_code = cdp_code_dealer(mif0, muni_mifer)
        # Both inner variants converge
        assert lev_code == cdp_code_dealer(levc, muni_levante)
        assert mif_code == cdp_code_dealer(mifc, muni_mifer)
        # But the two dealerships stay distinct
        assert lev_code != mif_code
