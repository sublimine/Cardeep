"""
tests/test_cluster_vehicles.py
Unit tests for pipeline/identity/cluster_vehicles.py — B7 vehicle deduplication.

Covers:
  - photo_url normalization
  - title normalization
  - price tolerance
  - Signal A: photo_url merge
  - Signal B: firma merge (cross-entity + same title only)
  - Anti-FP: same-entity firma does NOT merge (fleet-bulk fix 2026-06-15)
  - Anti-FP: same-entity same-photo STILL merges via Signal A (genuine re-listing)
  - Anti-FP: cross-entity firma without matching title does NOT merge
  - Anti-FP: cross-province NEVER merges (firma)
  - Anti-FP: price >2% difference does NOT merge
  - Anti-FP: no shared signal does NOT merge
  - Canonical selection: oldest first_seen wins
  - Singleton has match_signal='none'
  - UnionFind correctness
  - km=0/NULL guard: new-car stock not merged without matching VIN
  - Photo high-collision guard: catalogue/stock photo excluded from Signal A
  - Firma non-null-price guard: NULL price blocks Signal B
"""
from __future__ import annotations

import datetime
import re
import unicodedata
from decimal import Decimal
from typing import Any

import pytest

from pipeline.identity.cluster_vehicles import (
    PHOTO_HIGH_COLLISION_K,
    UnionFind,
    _build_cluster_table,
    _build_edges,
    _can_merge_new_cars,
    _is_new_car,
    _normalize_photo_url,
    _normalize_title,
    _prices_within_tolerance,
    _select_canonical,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_TS = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)


def _vehicle(
    ulid: str,
    entity_ulid: str = "ENT1",
    make: str | None = "seat",
    model: str | None = "ibiza",
    year: int | None = 2020,
    km: int | None = 50000,
    price: Any = Decimal("8000.00"),
    title: str | None = "Seat Ibiza 2020",
    photo_url: str | None = None,
    province_code: str | None = "28",
    first_seen: datetime.datetime | None = None,
    vin_ref: str | None = None,
) -> dict:
    return {
        "vehicle_ulid": ulid,
        "entity_ulid": entity_ulid,
        "make": make,
        "model": model,
        "year": year,
        "km": km,
        "price": price,
        "title": title,
        "photo_url": photo_url,
        "province_code": province_code,
        "first_seen": first_seen or _BASE_TS,
        "vin_ref": vin_ref,
    }


# ---------------------------------------------------------------------------
# _normalize_photo_url
# ---------------------------------------------------------------------------


class TestNormalizePhotoUrl:
    def test_strips_query_string(self) -> None:
        url = "https://cdn.wallapop.com/cars/img.jpg?size=600x400&ts=123"
        assert _normalize_photo_url(url) == "https://cdn.wallapop.com/cars/img.jpg"

    def test_lowercases(self) -> None:
        url = "HTTPS://CDN.EXAMPLE.COM/IMG.JPG"
        assert _normalize_photo_url(url) is not None
        assert _normalize_photo_url(url) == _normalize_photo_url(url.lower())

    def test_strips_trailing_slashes(self) -> None:
        url = "https://cdn.example.com/img.jpg///"
        assert _normalize_photo_url(url) == "https://cdn.example.com/img.jpg"

    def test_none_returns_none(self) -> None:
        assert _normalize_photo_url(None) is None
        assert _normalize_photo_url("") is None
        assert _normalize_photo_url("   ") is None

    def test_same_url_same_result(self) -> None:
        url = "https://images.milanuncios.com/api/v1/ma-ad-media-pro/images/abc123.jpg"
        assert _normalize_photo_url(url) == _normalize_photo_url(url)

    def test_different_urls_differ(self) -> None:
        url_a = "https://cdn.wallapop.com/img/car1.jpg"
        url_b = "https://cdn.wallapop.com/img/car2.jpg"
        assert _normalize_photo_url(url_a) != _normalize_photo_url(url_b)


# ---------------------------------------------------------------------------
# _normalize_title
# ---------------------------------------------------------------------------


class TestNormalizeTitle:
    def test_strips_accents(self) -> None:
        assert _normalize_title("Señal") == "senal"

    def test_lowercases(self) -> None:
        assert _normalize_title("SEAT Ibiza") == "seatibiza"

    def test_removes_spaces_and_punctuation(self) -> None:
        assert _normalize_title("Seat - Ibiza, 2020") == "seatibiza2020"

    def test_none_returns_none(self) -> None:
        assert _normalize_title(None) is None
        assert _normalize_title("") is None

    def test_same_title_same_result(self) -> None:
        t = "Volkswagen Golf VII 1.6 TDI"
        assert _normalize_title(t) == _normalize_title(t)


# ---------------------------------------------------------------------------
# _normalize_title — OPEN-C sibling closure (project F3)
#
# The normalized title is the SOLE cross-entity corroboration gate for Signal B
# (firma) at cluster_vehicles.py:491-494 —
#   ta = _normalize_title(va["title"]); tb = _normalize_title(vb["title"])
#   if not (ta and tb and ta == tb): continue
# so the title normaliser is a REAL clustering signal, not display/log. The
# legacy NFKD + encode('ascii','ignore') fold ERASED every non-Latin codepoint,
# so a Greek/Cyrillic/CJK title folded to '' -> None and the gate failed (Signal
# B DEAD for non-Latin tenants = under-merge), or a short incidental Latin/digit
# residue ('1.6' -> '16') survived and made two DIFFERENT cars false-corroborate
# (over-merge). The fix reuses the dealer normaliser's per-character hybrid fold
# (name_normalize._ascii_fold_transliterate), so Spanish/Latin titles stay
# BYTE-IDENTICAL and only the previously-erased non-Latin letters gain a value.
# ---------------------------------------------------------------------------

# Non-Latin fixtures (codepoint-built so this source stays ASCII-explicit).
_NL_GREEK_SEAT_IBIZA = "".join(
    chr(c) for c in (0x3A3, 0x3B5, 0x3AC, 0x3C4, 0x20, 0x38A, 0x3BC, 0x3C0, 0x3B9, 0x3B6, 0x3B1)
)  # 'Σεάτ Ίμπιζα'  (Seat Ibiza, Greek)
_NL_CYRILLIC_VW = "".join(
    chr(c) for c in (0x412, 0x41E, 0x41B, 0x41A, 0x421, 0x412, 0x410, 0x413, 0x415, 0x41D)
)  # 'ВОЛКСВАГЕН'  (Volkswagen, Cyrillic)
_NL_JP_TOYOTA = "".join(chr(c) for c in (0x30C8, 0x30E8, 0x30BF))  # 'トヨタ'  (Toyota, katakana)
_NL_IBIZA = "".join(chr(c) for c in (0x38A, 0x3BC, 0x3C0, 0x3B9, 0x3B6, 0x3B1))  # 'Ίμπιζα'
_NL_STYLE = "".join(chr(c) for c in (0x3A3, 0x3C4, 0x3AC, 0x3C5, 0x3BB))  # 'Στάυλ'
_NL_REFER = "".join(chr(c) for c in (0x3A1, 0x3B5, 0x3C6, 0x3B5, 0x3C1, 0x3AD, 0x3BD, 0x3C2))  # 'Ρεφερένς'
# Two DIFFERENT Greek-trim Ibizas that the legacy fold both collapsed to '16'.
_NL_IBIZA_STYLE = _NL_IBIZA + " " + _NL_STYLE + " 1.6"
_NL_IBIZA_REFER = _NL_IBIZA + " " + _NL_REFER + " 1.6"

_RE_TITLE_NON_ALNUM = re.compile(r"[^a-z0-9]")


def _legacy_normalize_title(title: str | None) -> str | None:
    """Frozen copy of the pre-fix ascii-ERASE normaliser: the ES byte-identity
    oracle and the documented RED. NFKD -> encode('ascii','ignore') -> lower ->
    strip non-[a-z0-9]."""
    if not title or not title.strip():
        return None
    nfkd = unicodedata.normalize("NFKD", title)
    clean = _RE_TITLE_NON_ALNUM.sub("", nfkd.encode("ascii", "ignore").decode("ascii").lower())
    return clean if clean else None


class TestNormalizeTitleNonLatin:
    """GOLDEN — the vehicle title gate must TRANSLITERATE non-Latin scripts, not
    erase them, while staying byte-identical for Spanish / Latin titles."""

    def test_greek_title_transliterated_not_erased(self) -> None:
        # RED: the legacy ascii-erase fold wipes the whole Greek title to None.
        assert _legacy_normalize_title(_NL_GREEK_SEAT_IBIZA) is None
        # GREEN: a live, legible key (Signal B corroboration restored).
        assert _normalize_title(_NL_GREEK_SEAT_IBIZA) == "seatimpiza"

    def test_cyrillic_and_cjk_titles_transliterated_not_erased(self) -> None:
        assert _legacy_normalize_title(_NL_CYRILLIC_VW) is None   # RED
        assert _legacy_normalize_title(_NL_JP_TOYOTA) is None     # RED
        assert _normalize_title(_NL_CYRILLIC_VW) == "volksvagen"  # GREEN
        assert _normalize_title(_NL_JP_TOYOTA) == "toyota"        # GREEN

    def test_latin_residue_over_merge_is_fixed(self) -> None:
        """RED: two different Greek-trim titles both collapsed to the incidental
        '1.6' -> '16' residue, so they false-corroborated. GREEN: the full title
        survives, so the two keys differ and no longer over-merge."""
        # RED — legacy collapses both distinct titles onto the same '16' residue.
        assert _legacy_normalize_title(_NL_IBIZA_STYLE) == "16"
        assert _legacy_normalize_title(_NL_IBIZA_REFER) == "16"
        assert _legacy_normalize_title(_NL_IBIZA_STYLE) == _legacy_normalize_title(_NL_IBIZA_REFER)
        # GREEN — full transliterated titles are distinct.
        assert _normalize_title(_NL_IBIZA_STYLE) == "impizastayl16"
        assert _normalize_title(_NL_IBIZA_REFER) == "impizareferens16"
        assert _normalize_title(_NL_IBIZA_STYLE) != _normalize_title(_NL_IBIZA_REFER)

    def test_es_titles_byte_identical_to_legacy(self) -> None:
        """HARD GATE: every real Spanish / Latin car-title shape normalises EXACTLY
        as the legacy fold did — the fix must not move a single ES byte."""
        es_titles = [
            "Seat Ibiza 1.6 TDI", "Volkswagen Golf VII", "Citroën C4 Picasso",
            "Peugeot 308 Allure", "SEAT León 2.0 TDI FR", "Renault Mégane",
            "BMW Série 3", "Škoda Octavia", "Audi A4 Avant 2.0 TDI 150cv",
            "Mercedes-Benz Clase A", "Señal 2020", "Seat - Ibiza, 2020",
        ]
        for t in es_titles:
            assert _normalize_title(t) == _legacy_normalize_title(t), t

    def test_per_character_survivor_byte_identity(self) -> None:
        """Formal guarantee: for EVERY codepoint whose legacy fold is non-empty (a
        'survivor'), the new normaliser yields the identical result; only codepoints
        the legacy fold ERASED may gain a transliteration. Swept Latin..Arabic."""
        violations = []
        for cp in range(0x0, 0x3000):
            ch = chr(cp)
            if unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode("ascii"):
                probe = "z" + ch + "z"
                if _normalize_title(probe) != _legacy_normalize_title(probe):
                    violations.append(hex(cp))
        assert not violations, f"survivor byte-identity divergences: {violations[:20]}"


# ---------------------------------------------------------------------------
# _prices_within_tolerance
# ---------------------------------------------------------------------------


class TestPricesTolerance:
    def test_same_price_within_tolerance(self) -> None:
        assert _prices_within_tolerance(Decimal("8000"), Decimal("8000")) is True

    def test_within_2_pct(self) -> None:
        # 8000 * 1.019 = 8152 < 8000*1.02 => within
        assert _prices_within_tolerance(Decimal("8000"), Decimal("8152")) is True

    def test_exactly_at_2_pct(self) -> None:
        # 8000 * 1.02 = 8160 — boundary, should be True
        assert _prices_within_tolerance(Decimal("8000"), Decimal("8160")) is True

    def test_above_2_pct_rejected(self) -> None:
        # 8000 * 1.021 = 8168 > 2% → reject
        assert _prices_within_tolerance(Decimal("8000"), Decimal("8168")) is False

    def test_large_difference_rejected(self) -> None:
        assert _prices_within_tolerance(Decimal("8000"), Decimal("12000")) is False

    def test_none_rejected(self) -> None:
        assert _prices_within_tolerance(None, Decimal("8000")) is False
        assert _prices_within_tolerance(Decimal("8000"), None) is False

    def test_zero_price_rejected(self) -> None:
        assert _prices_within_tolerance(Decimal("0"), Decimal("0")) is False


# ---------------------------------------------------------------------------
# Signal A: photo_url merge
# ---------------------------------------------------------------------------


class TestSignalAPhotoUrl:
    def test_same_photo_url_merges(self) -> None:
        """Two listings with identical photo URL must end up in same cluster."""
        shared_photo = "https://cdn.example.com/cars/photo_abc.jpg"
        va = _vehicle("V1", entity_ulid="ENT1", photo_url=shared_photo, province_code="28")
        vb = _vehicle("V2", entity_ulid="ENT2", photo_url=shared_photo, province_code="08")
        # NOTE: different provinces — photo_url alone overrides the province guard.

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, "Photo match must yield a single canonical"

    def test_different_photo_urls_do_not_merge_on_photo(self) -> None:
        """Two listings with different photo URLs must NOT merge via signal A."""
        va = _vehicle("V1", photo_url="https://cdn.example.com/a.jpg")
        vb = _vehicle("V2", photo_url="https://cdn.example.com/b.jpg")

        edges, esm = _build_edges([va, vb])
        # May still merge via firma — strip firma by making price far apart
        va["price"] = Decimal("8000")
        vb["price"] = Decimal("99000")
        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, "Different photo + different price must NOT merge"

    def test_photo_merge_cross_province_allowed(self) -> None:
        """Signal A (photo) is cross-province-safe — physically same car."""
        shared = "https://cdn.example.com/car_xyz.jpg"
        va = _vehicle("V1", province_code="28", photo_url=shared)
        vb = _vehicle("V2", province_code="46", photo_url=shared)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, "Same photo cross-province must merge"

    def test_photo_signal_recorded(self) -> None:
        """Merged cluster via photo must record match_signal='photo_url' or 'both'."""
        shared = "https://cdn.example.com/car_sig.jpg"
        va = _vehicle("V1", photo_url=shared)
        vb = _vehicle("V2", entity_ulid="ENT2", photo_url=shared)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        for r in cluster_rows:
            if r["cluster_size"] > 1:
                assert r["match_signal"] in ("photo_url", "both")


# ---------------------------------------------------------------------------
# Signal B: firma merge
# ---------------------------------------------------------------------------


class TestSignalBFirma:
    def test_firma_same_entity_does_not_merge(self) -> None:
        """CRITICAL (fleet-bulk fix): same dealer, same firma + same title must NOT merge.

        A dealer with 207 Renault Zoe units (same model, same price, same generic title,
        DIFFERENT physical cars) must remain 207 distinct clusters.  Signal A (shared
        photo_url) is the only permitted merge path for same-entity duplicates.
        """
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        vb = _vehicle("V2", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Same-entity firma match MUST NOT merge — these are distinct stock units; "
            "Signal A (photo) is the only valid same-entity merge path"
        )

    def test_firma_same_entity_same_photo_still_merges_via_signal_a(self) -> None:
        """Same dealer + same photo URL = same car re-listed → Signal A fires correctly."""
        shared_photo = "https://cdn.example.com/car_repost.jpg"
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza",
                      photo_url=shared_photo)
        vb = _vehicle("V2", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza",
                      photo_url=shared_photo)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "Same-entity same-photo must still merge via Signal A (genuine re-listing)"
        )
        for r in cluster_rows:
            if r["cluster_size"] > 1:
                assert r["match_signal"] in ("photo_url", "both"), (
                    "Signal A must be the recorded signal for same-entity photo merge"
                )

    def test_firma_cross_entity_same_title_merges(self) -> None:
        """Different dealers, same firma + same title → legitimate cross-platform merge."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza 2020")
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title="Seat Ibiza 2020")

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "Cross-entity firma + same normalized title must merge (same car on two platforms)"
        )

    def test_firma_cross_entity_different_title_does_not_merge(self) -> None:
        """Different dealers, same firma but DIFFERENT title → must NOT merge.

        Without title corroboration there is no cross-entity identity signal;
        two dealers can legitimately stock the same make/model/year/km at the same price.
        """
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza Sport")
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title="Seat Ibiza Reference")

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Cross-entity firma with different titles must NOT merge — no identity corroboration"
        )

    def test_firma_signal_recorded(self) -> None:
        """Merged cluster via firma must record match_signal='firma' or 'both'."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title="Seat Ibiza")
        # cross-entity + same title → firma merge

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        for r in cluster_rows:
            if r["cluster_size"] > 1:
                assert r["match_signal"] in ("firma", "both")


class TestSignalBNonLatinTitle:
    """End-to-end Signal B (firma) behaviour with non-Latin titles — proves the
    title normaliser is a REAL merge gate, not cosmetic (OPEN-C sibling, F3)."""

    def test_cross_entity_identical_greek_title_merges(self) -> None:
        """RED (pre-fix): the Greek title folded to None, the firma title gate
        failed, and two genuine cross-platform duplicates stayed SPLIT (Signal B
        dead for non-Latin tenants). GREEN: the transliterated titles match, so
        the duplicate collapses into one canonical car."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title=_NL_GREEK_SEAT_IBIZA)
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title=_NL_GREEK_SEAT_IBIZA)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "Cross-entity firma + identical non-Latin title must merge — the title "
            "gate must transliterate, not erase, the corroboration signal"
        )
        for r in cluster_rows:
            if r["cluster_size"] > 1:
                assert r["match_signal"] in ("firma", "both")

    def test_cross_entity_different_greek_trims_do_not_over_merge(self) -> None:
        """RED (pre-fix): two DIFFERENT Greek-trim Ibizas both folded to the '16'
        residue, so the gate false-corroborated and over-merged two distinct cars.
        GREEN: the full transliterated titles differ, so they stay split."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title=_NL_IBIZA_STYLE)
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title=_NL_IBIZA_REFER)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Two different non-Latin trim titles sharing only an incidental Latin "
            "residue must NOT over-merge once the full title survives"
        )


# ---------------------------------------------------------------------------
# Anti-FP guards
# ---------------------------------------------------------------------------


class TestAntiFP:
    def test_cross_province_firma_only_does_not_merge(self) -> None:
        """CRITICAL: firma-only (no photo) across different provinces must NOT merge."""
        va = _vehicle(
            "V1", entity_ulid="ENT1", province_code="28",
            price=Decimal("8000"), title="Seat Ibiza",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT2", province_code="08",
            price=Decimal("8000"), title="Seat Ibiza",
        )
        # No shared photo_url, different province → must NOT merge.

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Cross-province firma-only MUST NOT merge (two distinct physical cars can exist)"
        )

    def test_price_above_2pct_does_not_merge(self) -> None:
        """Price difference > 2% must prevent firma merge."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        vb = _vehicle("V2", entity_ulid="ENT1", price=Decimal("8500"), title="Seat Ibiza")
        # 8500/8000 = 1.0625 → 6.25% > 2% → reject

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2

    def test_no_shared_signal_does_not_merge(self) -> None:
        """Vehicles with no overlapping signal at all must stay separate."""
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            make="seat", model="ibiza", year=2020, km=50000,
            price=Decimal("8000"),
            photo_url="https://cdn.example.com/car_a.jpg",
            province_code="28",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT2",
            make="volkswagen", model="polo", year=2019, km=30000,
            price=Decimal("9000"),
            photo_url="https://cdn.example.com/car_b.jpg",
            province_code="28",
        )

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2

    def test_firma_cross_entity_without_title_does_not_merge(self) -> None:
        """Cross-entity firma with different titles must NOT merge.

        Signal B requires BOTH cross-entity AND same normalized title.
        Different titles = no identity corroboration = no merge.
        """
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            price=Decimal("8000"), title="Seat Ibiza Sport",
            province_code="28",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT2",
            price=Decimal("8000"), title="Seat Ibiza Reference",  # different title
            province_code="28",
        )
        # Cross-entity, same firma, same province, price matches, but different titles
        # → title guard must block merge

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Cross-entity firma without same title must NOT merge"
        )

    def test_singleton_has_signal_none(self) -> None:
        """A single vehicle not matched to anything must have match_signal='none'."""
        va = _vehicle("V1", photo_url=None)

        edges, esm = _build_edges([va])
        cluster_rows = _build_cluster_table([va], edges, esm)

        assert len(cluster_rows) == 1
        assert cluster_rows[0]["match_signal"] == "none"
        assert cluster_rows[0]["cluster_size"] == 1
        assert cluster_rows[0]["canonical_vehicle_ulid"] == "V1"


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------


class TestCanonicalSelection:
    def test_oldest_first_seen_wins(self) -> None:
        """Canonical must be the listing with the earliest first_seen."""
        older = _BASE_TS - datetime.timedelta(days=10)
        newer = _BASE_TS

        va = _vehicle("V_OLD", first_seen=older)
        vb = _vehicle("V_NEW", first_seen=newer)

        vehicle_by_ulid = {v["vehicle_ulid"]: v for v in [va, vb]}
        canonical = _select_canonical(["V_OLD", "V_NEW"], vehicle_by_ulid)
        assert canonical == "V_OLD"

    def test_tiebreak_ulid_ascending(self) -> None:
        """When first_seen is identical, lower ulid wins."""
        va = _vehicle("V_AAA", first_seen=_BASE_TS)
        vb = _vehicle("V_ZZZ", first_seen=_BASE_TS)

        vehicle_by_ulid = {v["vehicle_ulid"]: v for v in [va, vb]}
        canonical = _select_canonical(["V_AAA", "V_ZZZ"], vehicle_by_ulid)
        assert canonical == "V_AAA"


# ---------------------------------------------------------------------------
# km=0 / km=NULL guard
# ---------------------------------------------------------------------------


class TestNewCarGuard:
    """km=0 and km=NULL vehicles must NOT be merged via Signal A or B
    unless they share an identical non-null vin_ref."""

    # --- helper predicates ---

    def test_is_new_car_km_zero(self) -> None:
        assert _is_new_car({"km": 0}) is True

    def test_is_new_car_km_none(self) -> None:
        assert _is_new_car({"km": None}) is True

    def test_is_new_car_km_positive(self) -> None:
        assert _is_new_car({"km": 1}) is False
        assert _is_new_car({"km": 100000}) is False

    def test_can_merge_new_cars_same_vin(self) -> None:
        va = {"vin_ref": "WDD2130562A123456"}
        vb = {"vin_ref": "WDD2130562A123456"}
        assert _can_merge_new_cars(va, vb) is True

    def test_can_merge_new_cars_different_vin(self) -> None:
        va = {"vin_ref": "WDD2130562A123456"}
        vb = {"vin_ref": "WDD2130562A999999"}
        assert _can_merge_new_cars(va, vb) is False

    def test_can_merge_new_cars_null_vin(self) -> None:
        va = {"vin_ref": None}
        vb = {"vin_ref": None}
        assert _can_merge_new_cars(va, vb) is False

    def test_can_merge_new_cars_one_null(self) -> None:
        va = {"vin_ref": "WDD2130562A123456"}
        vb = {"vin_ref": None}
        assert _can_merge_new_cars(va, vb) is False

    def test_can_merge_new_cars_vin_case_insensitive(self) -> None:
        va = {"vin_ref": "wdd2130562a123456"}
        vb = {"vin_ref": "WDD2130562A123456"}
        assert _can_merge_new_cars(va, vb) is True

    # --- Signal A: photo_url blocked for km=0 without VIN ---

    def test_km0_photo_url_different_entity_no_vin_not_merged(self) -> None:
        """Two km=0 listings with same catalogue photo and different dealers
        must NOT be merged when both lack a vin_ref."""
        shared_photo = "https://cdn.brand.com/catalogue/golf8.jpg"
        va = _vehicle("V1", entity_ulid="DEALER_A", km=0,
                      photo_url=shared_photo, vin_ref=None)
        vb = _vehicle("V2", entity_ulid="DEALER_B", km=0,
                      photo_url=shared_photo, vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "km=0 listings without VIN sharing a catalogue photo must remain distinct units"
        )

    def test_km_null_photo_url_different_entity_no_vin_not_merged(self) -> None:
        """Same as above but with km=NULL (catalogue listings without mileage)."""
        shared_photo = "https://cdn.brand.com/catalogue/polo9.jpg"
        va = _vehicle("V1", entity_ulid="DEALER_A", km=None,
                      photo_url=shared_photo, vin_ref=None)
        vb = _vehicle("V2", entity_ulid="DEALER_B", km=None,
                      photo_url=shared_photo, vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "km=NULL listings without VIN sharing a catalogue photo must remain distinct"
        )

    def test_km0_same_vin_photo_url_merged(self) -> None:
        """Two km=0 listings with same non-null VIN and same photo must merge."""
        shared_photo = "https://cdn.brand.com/catalogue/golf8.jpg"
        vin = "WVWZZZ8TZPP012345"
        va = _vehicle("V1", entity_ulid="DEALER_A", km=0,
                      photo_url=shared_photo, vin_ref=vin)
        vb = _vehicle("V2", entity_ulid="DEALER_B", km=0,
                      photo_url=shared_photo, vin_ref=vin)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "km=0 listings with matching non-null VIN must be merged"
        )

    # --- Signal B: firma blocked for km=0 without VIN ---

    def test_km0_firma_different_entity_same_title_no_vin_not_merged(self) -> None:
        """Two km=0 vehicles with identical firma + same title across different
        dealers must NOT merge when neither has a vin_ref.  Catalogue stock
        at list-price with shared titles is the canonical over-merge scenario."""
        va = _vehicle("V1", entity_ulid="DEALER_A", km=0,
                      price=Decimal("25000"), title="Volkswagen Golf 8 Life",
                      province_code="28", vin_ref=None)
        vb = _vehicle("V2", entity_ulid="DEALER_B", km=0,
                      price=Decimal("25000"), title="Volkswagen Golf 8 Life",
                      province_code="28", vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "km=0 same-firma same-title different-dealer without VIN must NOT merge"
        )

    def test_km0_firma_same_entity_no_vin_not_merged(self) -> None:
        """Two km=0 vehicles from the SAME dealer (same entity_ulid) but without
        VIN must also NOT merge — they are two distinct units of the same model."""
        va = _vehicle("V1", entity_ulid="DEALER_A", km=0,
                      price=Decimal("25000"), title="Volkswagen Golf 8",
                      province_code="28", vin_ref=None)
        vb = _vehicle("V2", entity_ulid="DEALER_A", km=0,
                      price=Decimal("25000"), title="Volkswagen Golf 8",
                      province_code="28", vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "km=0 same-dealer without VIN must NOT merge — two stock units"
        )

    def test_km0_firma_same_vin_merged(self) -> None:
        """Two km=0 vehicles with same non-null VIN and firma must merge via firma."""
        vin = "WVWZZZ8TZPP099999"
        va = _vehicle("V1", entity_ulid="DEALER_A", km=0,
                      price=Decimal("25000"), title="VW Golf 8",
                      province_code="28", vin_ref=vin)
        vb = _vehicle("V2", entity_ulid="DEALER_B", km=0,
                      price=Decimal("25000"), title="VW Golf 8",
                      province_code="28", vin_ref=vin)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "km=0 listings with matching VIN must merge"
        )

    # --- Regression: km>0 unaffected ---

    def test_km_positive_firma_still_merges(self) -> None:
        """km>0 cross-entity vehicles with matching firma + same title must still merge
        (Signal B unaffected by km=0 guard — regression for the km=0 guard introduction)."""
        va = _vehicle("V1", entity_ulid="ENT1", km=50000,
                      price=Decimal("8000"), title="Seat Ibiza 2020",
                      province_code="28", vin_ref=None)
        vb = _vehicle("V2", entity_ulid="ENT2", km=50000,  # different entity
                      price=Decimal("8000"), title="Seat Ibiza 2020",
                      province_code="28", vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "km>0 cross-entity firma merge must be unaffected by the km=0 guard"
        )

    def test_km_positive_photo_still_merges(self) -> None:
        """km>0 vehicles sharing a photo URL must still merge via Signal A."""
        shared_photo = "https://cdn.wallapop.com/img/used_car.jpg"
        va = _vehicle("V1", entity_ulid="ENT1", km=80000,
                      photo_url=shared_photo, vin_ref=None)
        vb = _vehicle("V2", entity_ulid="ENT2", km=80000,
                      photo_url=shared_photo, vin_ref=None)

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "km>0 photo_url merge must be unaffected by the km=0 guard"
        )


# ---------------------------------------------------------------------------
# UnionFind
# ---------------------------------------------------------------------------


class TestUnionFind:
    def test_initially_each_node_is_own_root(self) -> None:
        uf = UnionFind()
        uf._init("A")
        uf._init("B")
        assert uf.find("A") == "A"
        assert uf.find("B") == "B"

    def test_union_connects_nodes(self) -> None:
        uf = UnionFind()
        uf.union("A", "B")
        assert uf.find("A") == uf.find("B")

    def test_transitive_union(self) -> None:
        uf = UnionFind()
        uf.union("A", "B")
        uf.union("B", "C")
        assert uf.find("A") == uf.find("C")

    def test_components_correct(self) -> None:
        uf = UnionFind()
        for n in ["A", "B", "C", "D"]:
            uf._init(n)
        uf.union("A", "B")
        comps = uf.components()
        roots = list(comps.keys())
        # A and B should share a root; C and D each have their own
        assert len(roots) == 3

    def test_idempotent_union(self) -> None:
        uf = UnionFind()
        uf.union("A", "B")
        uf.union("A", "B")
        assert uf.find("A") == uf.find("B")


# ---------------------------------------------------------------------------
# Photo high-collision guard (new, 2026-06-15)
# ---------------------------------------------------------------------------


class TestPhotoHighCollisionGuard:
    """A photo_url shared by >= PHOTO_HIGH_COLLISION_K listings is catalogue/stock
    and must NOT be used as a merge signal (Signal A disabled for that URL)."""

    def _make_stock_photo_vehicles(self, count: int, photo: str) -> list[dict]:
        """Create `count` vehicles all sharing the same photo URL."""
        return [
            _vehicle(
                f"V{i}",
                entity_ulid=f"ENT{i}",
                km=50000 + i * 1000,
                price=Decimal("8000"),
                photo_url=photo,
                province_code="28",
            )
            for i in range(count)
        ]

    def test_stock_photo_above_threshold_does_not_merge(self) -> None:
        """A photo shared by >= PHOTO_HIGH_COLLISION_K distinct listings must NOT
        produce any merge edges (catalogue/stock image)."""
        stock_photo = "https://www1.bcaimage.com/document/placeholder.jpg"
        vehicles = self._make_stock_photo_vehicles(PHOTO_HIGH_COLLISION_K, stock_photo)

        edges, esm = _build_edges(vehicles)
        # No photo_url edges should be produced for the high-collision photo
        photo_edges = [(a, b) for a, b, sig in edges if sig in ("photo_url", "both")]
        assert photo_edges == [], (
            f"A photo shared by {PHOTO_HIGH_COLLISION_K} listings must not produce merge edges"
        )

    def test_stock_photo_above_threshold_all_singletons(self) -> None:
        """All vehicles sharing a high-collision photo must remain singletons."""
        stock_photo = "https://cdn.dealerk.es/cars/placeholder/placeholder-0x250.png"
        vehicles = self._make_stock_photo_vehicles(PHOTO_HIGH_COLLISION_K, stock_photo)

        edges, esm = _build_edges(vehicles)
        cluster_rows = _build_cluster_table(vehicles, edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == len(vehicles), (
            "Each vehicle sharing a catalogue photo must remain its own cluster"
        )

    def test_unique_photo_below_threshold_still_merges(self) -> None:
        """A photo shared by < PHOTO_HIGH_COLLISION_K listings (legitimate cross-platform
        duplicate) must still be merged via Signal A."""
        unique_photo = "https://cdn.wallapop.com/img/real_used_car_xyz123.jpg"
        # Use 3 listings (well below K=12): two platforms listing the same car
        vehicles = [
            _vehicle("V1", entity_ulid="ENT1", km=75000, photo_url=unique_photo,
                     province_code="28"),
            _vehicle("V2", entity_ulid="ENT2", km=75000, photo_url=unique_photo,
                     province_code="08"),
            _vehicle("V3", entity_ulid="ENT3", km=75000, photo_url=unique_photo,
                     province_code="46"),
        ]

        edges, esm = _build_edges(vehicles)
        cluster_rows = _build_cluster_table(vehicles, edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            f"A photo shared by 3 listings (< K={PHOTO_HIGH_COLLISION_K}) "
            f"must still trigger Signal A merge"
        )

    def test_at_threshold_minus_one_still_merges(self) -> None:
        """K-1 listings sharing a photo must still merge (boundary: K-1 is legitimate)."""
        photo = "https://cdn.example.com/borderline_photo.jpg"
        count = PHOTO_HIGH_COLLISION_K - 1
        vehicles = self._make_stock_photo_vehicles(count, photo)

        edges, esm = _build_edges(vehicles)
        cluster_rows = _build_cluster_table(vehicles, edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            f"K-1={count} listings sharing a photo must still merge (below high-collision threshold)"
        )


# ---------------------------------------------------------------------------
# Firma non-null-price guard (new, 2026-06-15)
# ---------------------------------------------------------------------------


class TestFirmaNonNullPriceGuard:
    """Signal B (firma) requires both vehicles to have price IS NOT NULL.
    A NULL price means we cannot verify price similarity → firma must not merge."""

    def test_firma_null_price_does_not_merge(self) -> None:
        """Two vehicles with identical firma but price=NULL must NOT merge via firma.
        This is the VW Caddy scenario: 1,752 listings with price=NULL and a generic
        templated title all collapsed into 1 cluster in the previous run."""
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            make="volkswagen", model="caddy", year=2019, km=120000,
            price=None,  # NULL price
            title="Volkswagen Caddy",
            province_code="28",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT1",  # same entity (strongest anti-FP corroboration)
            make="volkswagen", model="caddy", year=2019, km=120000,
            price=None,  # NULL price
            title="Volkswagen Caddy",
            province_code="28",
        )

        edges, esm = _build_edges([va, vb])
        firma_edges = [(a, b) for a, b, sig in edges if sig in ("firma", "both")]
        assert firma_edges == [], (
            "NULL price must block firma merge regardless of entity/title corroboration"
        )
        cluster_rows = _build_cluster_table([va, vb], edges, esm)
        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Two vehicles with price=NULL must remain distinct (cannot verify price similarity)"
        )

    def test_firma_one_null_price_does_not_merge(self) -> None:
        """If ONE of the two vehicles has price=NULL, firma must not merge."""
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            make="seat", model="ibiza", year=2020, km=50000,
            price=Decimal("8000"),  # valid price
            title="Seat Ibiza",
            province_code="28",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT1",
            make="seat", model="ibiza", year=2020, km=50000,
            price=None,  # NULL price on the other
            title="Seat Ibiza",
            province_code="28",
        )

        edges, esm = _build_edges([va, vb])
        firma_edges = [(a, b) for a, b, sig in edges if sig in ("firma", "both")]
        assert firma_edges == [], (
            "One NULL price must block firma merge (cannot compute ±2% tolerance)"
        )

    def test_firma_valid_price_within_tolerance_merges(self) -> None:
        """Regression: cross-entity vehicles with valid price ±2% + same title must still merge
        (non-null-price guard must not break legitimate cross-platform merges)."""
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            make="seat", model="ibiza", year=2020, km=50000,
            price=Decimal("8000"),
            title="Seat Ibiza 2020",
            province_code="28",
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT2",  # different entity — cross-platform
            make="seat", model="ibiza", year=2020, km=50000,
            price=Decimal("8100"),  # +1.25%, within ±2%
            title="Seat Ibiza 2020",
            province_code="28",
        )

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)
        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1, (
            "Cross-entity both-valid-price firma match within ±2% + same title must merge "
            "(non-null-price guard must not break legitimate cross-platform merges)"
        )

    def test_km0_guard_still_applies_with_null_price(self) -> None:
        """km=0 guard has precedence over the null-price guard — km=0 without VIN
        must not merge regardless of price (regression check for guard ordering)."""
        va = _vehicle(
            "V1", entity_ulid="ENT1",
            make="volkswagen", model="golf", year=2024, km=0,
            price=None,
            title="Volkswagen Golf",
            province_code="28",
            vin_ref=None,
        )
        vb = _vehicle(
            "V2", entity_ulid="ENT1",
            make="volkswagen", model="golf", year=2024, km=0,
            price=None,
            title="Volkswagen Golf",
            province_code="28",
            vin_ref=None,
        )

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)
        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "km=0 without VIN must not merge — km=0 guard must remain intact"
        )
