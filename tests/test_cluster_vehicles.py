"""
tests/test_cluster_vehicles.py
Unit tests for pipeline/identity/cluster_vehicles.py — B7 vehicle deduplication.

Covers:
  - photo_url normalization
  - title normalization
  - price tolerance
  - Signal A: photo_url merge
  - Signal B: firma merge (with anti-FP guards)
  - Anti-FP: cross-province NEVER merges
  - Anti-FP: price >2% difference does NOT merge
  - Anti-FP: no shared signal does NOT merge
  - Anti-FP: firma-only without title/entity guard does NOT merge
  - Canonical selection: oldest first_seen wins
  - Singleton has match_signal='none'
  - UnionFind correctness
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

import pytest

from pipeline.identity.cluster_vehicles import (
    UnionFind,
    _build_cluster_table,
    _build_edges,
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
    def test_firma_exact_same_entity_merges(self) -> None:
        """Same dealer, same make/model/year/km/price → same entity guard fires."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        vb = _vehicle("V2", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        # same entity_ulid → anti-FP guard satisfied

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1

    def test_firma_exact_same_title_merges(self) -> None:
        """Different dealers, same firma + same title → title guard fires."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza 2020")
        vb = _vehicle("V2", entity_ulid="ENT2", price=Decimal("8000"), title="Seat Ibiza 2020")

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 1

    def test_firma_signal_recorded(self) -> None:
        """Merged cluster via firma must record match_signal='firma' or 'both'."""
        va = _vehicle("V1", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")
        vb = _vehicle("V2", entity_ulid="ENT1", price=Decimal("8000"), title="Seat Ibiza")

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        for r in cluster_rows:
            if r["cluster_size"] > 1:
                assert r["match_signal"] in ("firma", "both")


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

    def test_firma_without_title_or_entity_guard_does_not_merge(self) -> None:
        """Firma match without title match AND different entity must NOT merge."""
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
        # Same firma, same province, price matches, but different entity AND different title
        # → anti-FP guard must block merge

        edges, esm = _build_edges([va, vb])
        cluster_rows = _build_cluster_table([va, vb], edges, esm)

        canonical_ids = {r["canonical_vehicle_ulid"] for r in cluster_rows}
        assert len(canonical_ids) == 2, (
            "Firma-only without title/entity corroboration must NOT merge"
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
