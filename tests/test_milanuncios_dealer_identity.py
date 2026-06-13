"""Tests for the milanuncios dealer identity stability fix (CAMPAIGN B1.1).

Regression suite for the fix applied to cdp_code_dealer(): the function must
produce a single, per-physical-installation cdp_code regardless of which
authorId milanuncios emits for a given dealership.

Root cause: milanuncios authorId is per-listing-session unstable.  The same
physical dealer (e.g. Mercedes-Benz Aguina in Bilbao, or Sealco Motor in
Alcalá de Henares) appears under N distinct authorIds across crawl windows,
because the platform issues an authorId per active listing session rather than
per dealer registration.  Before the fix, address=f"mnauthor:{d.author_id}"
caused each authorId to hash to a distinct cdp_code, fragmenting one physical
dealer into 2-3+ CARDEEP entities (121 intra-source groups detected in prod).

After the fix, address is omitted; the identity key is name + municipality_code
(the conservative rule used for mercedes_benz and das_weltauto).  The authorId
is preserved as source_ref in entity_source for cross-run traceability only.

Private sellers (kind='particular') are UNCHANGED: cdp_code_particular() uses
particular_platform + particular_seller_id — a completely separate code path
that this fix does not touch.
"""
from __future__ import annotations

import pytest

from pipeline.platform.milanuncios_wholesale import DealerRef, ParticularRef
from pipeline.platform.milanuncios_wholesale import cdp_code_dealer, cdp_code_particular


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dealer(
    author_id: str,
    name: str = "Mercedes-Benz Aguina",
    province_code: str = "48",
    city: str = "Bilbao",
    muni: str = "48013",
) -> tuple[DealerRef, str]:
    """Build a DealerRef and its municipality code for testing."""
    ref = DealerRef(
        author_id=author_id,
        name=name,
        province_code=province_code,
        city=city,
    )
    return ref, muni


def _particular(author_id: str, name: str = "Carlos", province_code: str = "28",
                city: str = "Madrid") -> ParticularRef:
    return ParticularRef(
        author_id=author_id,
        name=name,
        province_code=province_code,
        city=city,
    )


# ---------------------------------------------------------------------------
# Positive cases: same physical dealer, different author_ids → ONE cdp_code
# ---------------------------------------------------------------------------


class TestSameDealerMultipleAuthorIds:
    """Three ads from the same physical dealer with distinct authorIds must all
    resolve to the same cdp_code (one entity, not three)."""

    def test_mercedes_aguina_three_author_ids_same_code(self) -> None:
        """Mercedes-Benz Aguina (Bilbao, real DB data): authorIds 107637030,
        209915469, 235367014 → must produce identical cdp_code."""
        muni = "48013"
        d1, _ = _dealer("107637030")
        d2, _ = _dealer("209915469")
        d3, _ = _dealer("235367014")
        code1 = cdp_code_dealer(d1, muni)
        code2 = cdp_code_dealer(d2, muni)
        code3 = cdp_code_dealer(d3, muni)
        assert code1 == code2 == code3, (
            f"All three authorIds must produce one code; got {code1}, {code2}, {code3}"
        )

    def test_sealco_motor_two_author_ids_same_code(self) -> None:
        """Sealco Motor, S.A. (Alcalá de Henares, real DB data): authorIds
        232844860, 232844903 → must produce identical cdp_code."""
        muni = "28007"
        d1 = DealerRef(author_id="232844860", name="Sealco Motor, S.A.",
                       province_code="28", city="Alcala de Henares")
        d2 = DealerRef(author_id="232844903", name="Sealco Motor, S.A.",
                       province_code="28", city="Alcala de Henares")
        assert cdp_code_dealer(d1, muni) == cdp_code_dealer(d2, muni)

    def test_code_is_stable_across_calls(self) -> None:
        """cdp_code_dealer is deterministic: same DealerRef always gives same code."""
        d, muni = _dealer("999888777")
        assert cdp_code_dealer(d, muni) == cdp_code_dealer(d, muni)

    def test_cdp_code_format(self) -> None:
        """Output must match CDP-ES-{province}-{8chars} with Crockford base32."""
        d, muni = _dealer("123456")
        code = cdp_code_dealer(d, muni)
        parts = code.split("-")
        assert parts[0] == "CDP"
        assert parts[1] == "ES"
        assert parts[2] == "48"
        assert len(parts[3]) == 8
        # Crockford base32 alphabet (no I, L, O, U)
        assert all(c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for c in parts[3])


# ---------------------------------------------------------------------------
# Negative cases: distinct physical dealers → distinct cdp_codes
# ---------------------------------------------------------------------------


class TestDistinctDealersDifferentCodes:
    """Two dealerships that differ in name OR municipality must get distinct codes."""

    def test_different_name_same_municipality(self) -> None:
        """Two dealers in the same municipality with different names are distinct entities."""
        muni = "48013"
        d_aguina = DealerRef(author_id="111", name="Mercedes-Benz Aguina",
                             province_code="48", city="Bilbao")
        d_other = DealerRef(author_id="222", name="Autocenter Bilbao",
                            province_code="48", city="Bilbao")
        assert cdp_code_dealer(d_aguina, muni) != cdp_code_dealer(d_other, muni)

    def test_same_name_different_municipality(self) -> None:
        """Same chain name in two different municipalities must remain distinct."""
        d_bilbao = DealerRef(author_id="111", name="Clicars",
                             province_code="28", city="Madrid")
        d_alicante = DealerRef(author_id="999", name="Clicars",
                               province_code="03", city="Alicante")
        assert cdp_code_dealer(d_bilbao, "28079") != cdp_code_dealer(d_alicante, "03014")

    def test_same_author_id_different_name_different_code(self) -> None:
        """Hypothetical: same authorId, different name → different codes.
        Name is a first-class identity component."""
        muni = "28079"
        d1 = DealerRef(author_id="123", name="Audi Retail Madrid",
                       province_code="28", city="Madrid")
        d2 = DealerRef(author_id="123", name="BMW Retail Madrid",
                       province_code="28", city="Madrid")
        assert cdp_code_dealer(d1, muni) != cdp_code_dealer(d2, muni)


# ---------------------------------------------------------------------------
# Particulars: cdp_code_particular must NOT be affected by the dealer fix
# ---------------------------------------------------------------------------


class TestParticularsUnchanged:
    """Private sellers use cdp_code_particular() — a completely separate code
    path.  The dealer fix must not alter particular identity in any way."""

    def test_particular_different_author_ids_different_codes(self) -> None:
        """Two distinct private sellers (different authorIds) must get distinct codes.
        Unlike dealers, one particular = one authorId = one entity (authorId IS stable
        per human, per the milanuncios model)."""
        p1 = _particular("555111")
        p2 = _particular("555222")
        assert cdp_code_particular(p1) != cdp_code_particular(p2)

    def test_particular_same_author_id_same_code(self) -> None:
        """Same human (same authorId) listing N cars → same cdp_code (correct collapsing)."""
        p = _particular("77788899")
        assert cdp_code_particular(p) == cdp_code_particular(p)

    def test_particular_code_does_not_equal_dealer_code(self) -> None:
        """A particular and a dealer must never share a cdp_code, even with the same name."""
        muni = "28079"
        d = DealerRef(author_id="123", name="Juan", province_code="28", city="Madrid")
        p = ParticularRef(author_id="123", name="Juan", province_code="28", city="Madrid")
        assert cdp_code_dealer(d, muni) != cdp_code_particular(p)

    def test_particular_code_format_uses_platform_key(self) -> None:
        """Particular cdp_code must encode the milanuncios platform key (not authorId hash)."""
        p = _particular("12345678")
        code = cdp_code_particular(p)
        # Must be a valid CDP-ES-{province}-{8chars} code
        parts = code.split("-")
        assert parts[0] == "CDP"
        assert parts[1] == "ES"
        assert len(parts[3]) == 8
