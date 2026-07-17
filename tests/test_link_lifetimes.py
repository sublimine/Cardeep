"""
tests/test_link_lifetimes.py
Unit tests for pipeline/identity/link_lifetimes.py — 02-history-reports F1
(vehicle lifetime re-identification: GONE -> reappears weeks/months later,
possibly at a different dealer).

TDD fixtures required by plans/cardeep-omni/02-history-reports.md F1:
  - cadenas verdaderas (true multi-episode chains)
  - falsos amigos (here: cross-country, per the F0 correction in the letter §10 —
    cross-PROVINCE is a legitimate, expected, desirable case for THIS engine: a
    resold car moving province is exactly the "vida en mercado" signal the pillar
    wants to surface, unlike vehicle_cluster's simultaneous-duplicate guard where
    cross-province IS suspicious. Only cross-COUNTRY is blocked here, matching the
    project-wide COUNTRY-PROOF convention. Declared substitution, not an omission.)
  - km retrocedido (small = noise, large = flagged but still linked — declared
    design decision, see module docstring)
  - gemelos de flota con misma foto de catálogo (trap #1: photo_hash high-collision
    guard, mirrors cluster_vehicles.py's PHOTO_HIGH_COLLISION_K)

Covers:
  - VIN normalization + strict pattern validation (anti-contamination guard,
    F0 finding: vin_ref holds non-VIN platform ids for most rows)
  - photo_hash normalization + high-collision (catalogue) exclusion
  - firma matching (make/model/year exact, normalized)
  - km evaluation (coherent / retreat-flagged / unknown)
  - temporal window (0 < gap <= LIFETIME_WINDOW_DAYS)
  - edge building end-to-end: vin_ref-only, photo_hash-only, both (upgrade)
  - anti-FP: predecessor still 'available' (hasn't left the market) -> no edge
  - anti-FP: predecessor has an active 0023-cluster sibling -> no edge
  - anti-FP: firma mismatch on a matching primary signal -> REJECTED, not
    persisted at low confidence (mirrors cluster_vehicles.py precedent)
  - anti-FP: cross-country -> never linked
  - multi-episode chains (3+ episodes) via consecutive bucket walking
  - UnionFind reuse (import from cluster_vehicles, no duplication)
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

import pytest

from pipeline.identity.link_lifetimes import (
    KM_NOISE_THRESHOLD_KM,
    LIFETIME_WINDOW_DAYS,
    PHOTO_HASH_HIGH_COLLISION_K,
    _build_edges,
    _build_photo_hash_buckets,
    _build_vin_buckets,
    _count_chains,
    _evaluate_km,
    _firma_matches,
    _normalize_photo_hash,
    _normalize_vin,
    _platform_domain,
    _within_window,
)

_BASE = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)


def _dt(days: int) -> datetime.datetime:
    return _BASE + datetime.timedelta(days=days)


def _vehicle(
    ulid: str,
    entity_ulid: str = "ENT1",
    country_code: str = "ES",
    make: str | None = "seat",
    model: str | None = "ibiza",
    year: int | None = 2020,
    km: int | None = 50000,
    vin_ref: str | None = None,
    photo_hash: str | None = None,
    status: str = "gone",
    first_seen: datetime.datetime | None = None,
    last_seen: datetime.datetime | None = None,
    deep_link: str = "https://dealer-a.example.com/car/1",
) -> dict:
    return {
        "vehicle_ulid": ulid,
        "entity_ulid": entity_ulid,
        "country_code": country_code,
        "make": make,
        "model": model,
        "year": year,
        "km": km,
        "vin_ref": vin_ref,
        "photo_hash": photo_hash,
        "status": status,
        "first_seen": first_seen or _BASE,
        "last_seen": last_seen or (first_seen or _BASE),
        "deep_link": deep_link,
    }


_VALID_VIN_1 = "YV1ZZA8TCL1035715"
_VALID_VIN_2 = "SALZB2DN3LH039280"


# ---------------------------------------------------------------------------
# _normalize_vin
# ---------------------------------------------------------------------------


class TestNormalizeVin:
    def test_accepts_valid_17_char_vin(self) -> None:
        assert _normalize_vin(_VALID_VIN_1) == _VALID_VIN_1

    def test_uppercases_and_trims(self) -> None:
        assert _normalize_vin(f"  {_VALID_VIN_1.lower()}  ") == _VALID_VIN_1

    def test_rejects_wrong_length(self) -> None:
        assert _normalize_vin("SHORT123") is None
        assert _normalize_vin(_VALID_VIN_1 + "X") is None

    def test_rejects_platform_id_contamination(self) -> None:
        # F0 finding: pipeline/sources/autoscout24.py:208 stores AS24's internal
        # listing id in vin_ref. These look like opaque ids, not VINs.
        assert _normalize_vin("pj9mo0v9dm6e") is None          # len=12
        assert _normalize_vin("603858869") is None              # len=9, digits only

    def test_rejects_forbidden_letters_i_o_q(self) -> None:
        # Real VINs never contain I, O, Q (avoid confusion with 1/0).
        bad = "I" + _VALID_VIN_1[1:]
        assert _normalize_vin(bad) is None

    def test_none_and_empty(self) -> None:
        assert _normalize_vin(None) is None
        assert _normalize_vin("") is None
        assert _normalize_vin("   ") is None


# ---------------------------------------------------------------------------
# _normalize_photo_hash
# ---------------------------------------------------------------------------


class TestNormalizePhotoHash:
    def test_trims(self) -> None:
        assert _normalize_photo_hash("  abcd1234  ") == "abcd1234"

    def test_none_and_empty(self) -> None:
        assert _normalize_photo_hash(None) is None
        assert _normalize_photo_hash("") is None
        assert _normalize_photo_hash("   ") is None


# ---------------------------------------------------------------------------
# _firma_matches
# ---------------------------------------------------------------------------


class TestFirmaMatches:
    def test_exact_match(self) -> None:
        a = _vehicle("A", make="Seat", model="Ibiza", year=2020)
        b = _vehicle("B", make="seat", model="IBIZA", year=2020)
        assert _firma_matches(a, b) is True

    def test_make_mismatch_rejects(self) -> None:
        a = _vehicle("A", make="Seat", model="Ibiza", year=2020)
        b = _vehicle("B", make="Volkswagen", model="Ibiza", year=2020)
        assert _firma_matches(a, b) is False

    def test_model_mismatch_rejects(self) -> None:
        a = _vehicle("A", make="Seat", model="Ibiza", year=2020)
        b = _vehicle("B", make="Seat", model="Leon", year=2020)
        assert _firma_matches(a, b) is False

    def test_year_mismatch_rejects(self) -> None:
        a = _vehicle("A", make="Seat", model="Ibiza", year=2020)
        b = _vehicle("B", make="Seat", model="Ibiza", year=2021)
        assert _firma_matches(a, b) is False

    def test_missing_field_rejects(self) -> None:
        a = _vehicle("A", make=None, model="Ibiza", year=2020)
        b = _vehicle("B", make="Seat", model="Ibiza", year=2020)
        assert _firma_matches(a, b) is False


# ---------------------------------------------------------------------------
# _evaluate_km — the declared km-retreat design decision
# ---------------------------------------------------------------------------


class TestEvaluateKm:
    def test_increase_is_coherent(self) -> None:
        r = _evaluate_km(50000, 52000)
        assert r["km_known"] is True
        assert r["km_delta"] == 2000
        assert r["km_retreat_flagged"] is False

    def test_small_decrease_within_noise_is_coherent(self) -> None:
        # Anti-noise threshold matches C8's own tolerance (>1000km = real retreat).
        r = _evaluate_km(50000, 49500)
        assert r["km_delta"] == -500
        assert r["km_retreat_flagged"] is False

    def test_large_decrease_flags_retreat_but_stays_evaluable(self) -> None:
        r = _evaluate_km(80000, 70000)
        assert r["km_delta"] == -10000
        assert r["km_retreat_flagged"] is True

    def test_boundary_exactly_at_threshold_is_not_flagged(self) -> None:
        r = _evaluate_km(50000, 50000 - KM_NOISE_THRESHOLD_KM)
        assert r["km_retreat_flagged"] is False

    def test_missing_km_is_unknown_not_blocking(self) -> None:
        r = _evaluate_km(None, 50000)
        assert r["km_known"] is False
        assert r["km_retreat_flagged"] is False


# ---------------------------------------------------------------------------
# _within_window
# ---------------------------------------------------------------------------


class TestWithinWindow:
    def test_valid_gap(self) -> None:
        assert _within_window(_dt(0), _dt(30)) is True

    def test_zero_or_negative_gap_rejected(self) -> None:
        assert _within_window(_dt(30), _dt(30)) is False
        assert _within_window(_dt(30), _dt(10)) is False

    def test_beyond_window_rejected(self) -> None:
        assert _within_window(_dt(0), _dt(LIFETIME_WINDOW_DAYS + 1)) is False

    def test_at_window_boundary_accepted(self) -> None:
        assert _within_window(_dt(0), _dt(LIFETIME_WINDOW_DAYS)) is True


# ---------------------------------------------------------------------------
# Bucketing
# ---------------------------------------------------------------------------


class TestBuildVinBuckets:
    def test_groups_by_normalized_vin(self) -> None:
        vs = [
            _vehicle("A", vin_ref=_VALID_VIN_1.lower()),
            _vehicle("B", vin_ref=_VALID_VIN_1),
            _vehicle("C", vin_ref=_VALID_VIN_2),
            _vehicle("D", vin_ref=_VALID_VIN_2),
        ]
        buckets = _build_vin_buckets(vs)
        assert set(buckets.keys()) == {_VALID_VIN_1, _VALID_VIN_2}
        assert {v["vehicle_ulid"] for v in buckets[_VALID_VIN_1]} == {"A", "B"}
        assert {v["vehicle_ulid"] for v in buckets[_VALID_VIN_2]} == {"C", "D"}

    def test_excludes_invalid_vins(self) -> None:
        vs = [_vehicle("A", vin_ref="pj9mo0v9dm6e"), _vehicle("B", vin_ref=None)]
        assert _build_vin_buckets(vs) == {}

    def test_singleton_buckets_excluded(self) -> None:
        vs = [_vehicle("A", vin_ref=_VALID_VIN_1)]
        assert _build_vin_buckets(vs) == {}


class TestBuildPhotoHashBuckets:
    def test_groups_by_hash(self) -> None:
        vs = [
            _vehicle("A", photo_hash="hash1"),
            _vehicle("B", photo_hash="hash1"),
        ]
        buckets = _build_photo_hash_buckets(vs)
        assert {v["vehicle_ulid"] for v in buckets["hash1"]} == {"A", "B"}

    def test_high_collision_hash_excluded(self) -> None:
        # Trap #1: a catalogue/stock photo shared by >= K listings must NOT be
        # treated as a physical-unit identity signal (fleet twins, same stock photo).
        vs = [
            _vehicle(f"V{i}", photo_hash="catalog-stock-photo")
            for i in range(PHOTO_HASH_HIGH_COLLISION_K)
        ]
        assert _build_photo_hash_buckets(vs) == {}

    def test_below_collision_threshold_kept(self) -> None:
        vs = [
            _vehicle(f"V{i}", photo_hash="shared-legit")
            for i in range(PHOTO_HASH_HIGH_COLLISION_K - 1)
        ]
        buckets = _build_photo_hash_buckets(vs)
        assert "shared-legit" in buckets


# ---------------------------------------------------------------------------
# _build_edges — end-to-end resolver logic
# ---------------------------------------------------------------------------


class TestBuildEdgesTrueChain:
    def test_two_episode_chain_via_vin(self) -> None:
        a = _vehicle(
            "A", entity_ulid="E1", vin_ref=_VALID_VIN_1, status="gone",
            first_seen=_dt(0), last_seen=_dt(30), km=50000,
            deep_link="https://dealer-a.example.com/car/1",
        )
        b = _vehicle(
            "B", entity_ulid="E2", vin_ref=_VALID_VIN_1, status="available",
            first_seen=_dt(90), last_seen=_dt(90), km=52000,
            deep_link="https://dealer-b.example.com/car/2",
        )
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert len(edges) == 1
        e = edges[0]
        assert e["vehicle_ulid_from"] == "A"
        assert e["vehicle_ulid_to"] == "B"
        assert e["match_signal"] == "vin_ref"
        assert e["evidence"]["km_retreat_flagged"] is False

    def test_three_episode_chain(self) -> None:
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20), km=40000,
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(60), last_seen=_dt(80), km=45000,
                     deep_link="https://dealer-b.example.com/car/2")
        c = _vehicle("C", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(150), last_seen=_dt(150), km=48000,
                     deep_link="https://dealer-c.example.com/car/3")
        edges = _build_edges([a, b, c], still_active_predecessors=set())
        pairs = {(e["vehicle_ulid_from"], e["vehicle_ulid_to"]) for e in edges}
        assert pairs == {("A", "B"), ("B", "C")}
        assert _count_chains(edges) == 1

    def test_both_signals_upgrade_to_both(self) -> None:
        a = _vehicle(
            "A", vin_ref=_VALID_VIN_1, photo_hash="samecar-photo",
            status="gone", first_seen=_dt(0), last_seen=_dt(20), km=40000,
            deep_link="https://dealer-a.example.com/car/1",
        )
        b = _vehicle(
            "B", vin_ref=_VALID_VIN_1, photo_hash="samecar-photo",
            status="available", first_seen=_dt(60), last_seen=_dt(60), km=41000,
            deep_link="https://dealer-b.example.com/car/2",
        )
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert len(edges) == 1
        assert edges[0]["match_signal"] == "both"

    def test_photo_hash_only_chain(self) -> None:
        a = _vehicle(
            "A", vin_ref=None, photo_hash="unique-car-photo",
            status="gone", first_seen=_dt(0), last_seen=_dt(20), km=40000,
            deep_link="https://dealer-a.example.com/car/1",
        )
        b = _vehicle(
            "B", vin_ref=None, photo_hash="unique-car-photo",
            status="available", first_seen=_dt(60), last_seen=_dt(60), km=41000,
            deep_link="https://dealer-b.example.com/car/2",
        )
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert len(edges) == 1
        assert edges[0]["match_signal"] == "photo_hash"


class TestBuildEdgesKmRetreat:
    def test_km_retreat_still_links_but_flagged(self) -> None:
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20), km=80000,
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60), km=70000,
                     deep_link="https://dealer-b.example.com/car/2")
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert len(edges) == 1
        assert edges[0]["evidence"]["km_retreat_flagged"] is True
        # Declared design decision: retreat lowers confidence but does not block.
        assert edges[0]["match_probability"] < 0.92


class TestBuildEdgesAntiFalsePositives:
    def test_cross_country_never_links(self) -> None:
        a = _vehicle("A", country_code="ES", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20),
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", country_code="PT", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60),
                     deep_link="https://dealer-b.example.com/car/2")
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []

    def test_firma_mismatch_rejects_even_with_matching_vin(self) -> None:
        # Coincidental/corrupted vin_ref match with genuinely different cars —
        # the engine must reject, not persist at low confidence (cluster_vehicles
        # precedent: rejected candidates are simply not written).
        a = _vehicle("A", make="Seat", model="Ibiza", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20),
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", make="Renault", model="Clio", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60),
                     deep_link="https://dealer-b.example.com/car/2")
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []

    def test_predecessor_still_available_blocks_link(self) -> None:
        # The car hasn't actually left the market yet (this listing hasn't gone
        # GONE) — no valid predecessor transition.
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(0), last_seen=_dt(20),
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60),
                     deep_link="https://dealer-b.example.com/car/2")
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []

    def test_active_cluster_sibling_blocks_predecessor(self) -> None:
        # A is 'gone' but a same-cluster sibling (0023) is still 'available' —
        # the physical car never left the market, just this ONE listing did.
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20),
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle("B", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60),
                     deep_link="https://dealer-b.example.com/car/2")
        edges = _build_edges([a, b], still_active_predecessors={"A"})
        assert edges == []

    def test_same_platform_domain_never_links(self) -> None:
        # REAL-WORLD FINDING (02-history-reports F1, live run 2026-07-18): every
        # single one of the first live run's 208 edges was intra-domain (same OEM
        # certified-pre-owned portal — Volvo Selekt, BMW Premium Selection,
        # Spoticar, Toyota, Mini Next — reissuing/reallocating a listing under a
        # new URL/listing_ref within the SAME manufacturer network), not a car
        # leaving one independent business and resurfacing at another. A domain
        # match is the single cleanest, cheapest signal that a "reappearance" is
        # actually portal-side listing churn, not the "coche rebotado entre
        # compraventas independientes" this pillar exists to surface — so it is a
        # hard block, not a probability discount.
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(20),
                     deep_link="https://selekt.volvocars.es/es-ES/store/used-cars/volvo-xc40-2025/AAA")
        b = _vehicle("B", vin_ref=_VALID_VIN_1, status="available", first_seen=_dt(60), last_seen=_dt(60),
                     deep_link="https://selekt.volvocars.es/es-ES/store/used-cars/volvo-xc40-2025/BBB")
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []

    def test_window_exceeded_blocks_link(self) -> None:
        a = _vehicle("A", vin_ref=_VALID_VIN_1, status="gone", first_seen=_dt(0), last_seen=_dt(0),
                     deep_link="https://dealer-a.example.com/car/1")
        b = _vehicle(
            "B", vin_ref=_VALID_VIN_1, status="available",
            first_seen=_dt(LIFETIME_WINDOW_DAYS + 5), last_seen=_dt(LIFETIME_WINDOW_DAYS + 5),
            deep_link="https://dealer-b.example.com/car/2",
        )
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []

    def test_no_signal_no_link(self) -> None:
        a = _vehicle("A", vin_ref=None, photo_hash=None, status="gone", first_seen=_dt(0), last_seen=_dt(20))
        b = _vehicle("B", vin_ref=None, photo_hash=None, status="available", first_seen=_dt(60), last_seen=_dt(60))
        edges = _build_edges([a, b], still_active_predecessors=set())
        assert edges == []


# ---------------------------------------------------------------------------
# _platform_domain — the hard anti-churn guard added after the first live run
# ---------------------------------------------------------------------------


class TestPlatformDomain:
    def test_extracts_host(self) -> None:
        assert _platform_domain("https://www.spoticar.es/comprar/peugeot-3008") == "www.spoticar.es"

    def test_case_insensitive(self) -> None:
        assert _platform_domain("HTTPS://WWW.SPOTICAR.ES/x") == "www.spoticar.es"

    def test_none_and_empty(self) -> None:
        assert _platform_domain(None) is None
        assert _platform_domain("") is None
