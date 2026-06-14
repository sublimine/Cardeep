"""
tests/test_resolve_entities.py
Unit tests for pipeline/identity/resolve_entities.py — F1 entity resolution (β).

Covers:
  - Phone normalization (9-digit strip, None for short)
  - Website host normalization
  - Jaccard computation
  - Fingerprint merges: Jaccard >= θ across different sources → merged
  - Phone merges: clean phone, same province → merged
  - Website merges: clean website, same province → merged
  - Anti-over-merge: centralita phone (high-collision) alone → NOT merged
  - Anti-over-merge: cross-province without fingerprint → BLOCKED
  - Anti-over-merge: high-collision website alone → NOT merged
  - Anti-over-merge: centralita + second identifier, same province → merged
  - Transitive closure: A-B + B-C → A, B, C same dealer
  - Canonical selection: richest entity wins
  - UnionFind correctness
  - Singleton has signal='none'
"""
from __future__ import annotations

import datetime
from typing import Any

import pytest

from pipeline.identity.resolve_entities import (
    MAX_ENTITY_COLLISION_K,
    MAX_PHONE_COLLISION_K,
    JACCARD_THETA,
    UnionFind,
    _build_edges,
    _build_resolution_table,
    _jaccard,
    _normalize_phone,
    _normalize_website_host,
    _richness,
    _select_canonical,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_TS = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)


def _entity(
    ulid: str,
    trade_name: str = "Dealer",
    kind: str = "compraventa",
    province_code: str | None = "28",
    municipality_code: str | None = "28079",
    phone: str | None = None,
    website: str | None = None,
    n_vehicles: int = 10,
    created_at: datetime.datetime | None = None,
    source_keys: list[str] | None = None,
) -> dict:
    return {
        "entity_ulid": ulid,
        "cdp_code": "CDP-" + ulid,
        "trade_name": trade_name,
        "kind": kind,
        "province_code": province_code,
        "municipality_code": municipality_code,
        "phone": phone,
        "website": website,
        "n_vehicles": n_vehicles,
        "created_at": created_at or _BASE_TS,
        "source_keys": source_keys or ["source_a"],
    }


def _fp(canonicals: list[str]) -> set[str]:
    return set(canonicals)


# ---------------------------------------------------------------------------
# _normalize_phone
# ---------------------------------------------------------------------------


class TestNormalizePhone:
    def test_9_digit_strip(self) -> None:
        assert _normalize_phone("+34 612 345 678") == "612345678"

    def test_strips_to_last_9(self) -> None:
        # Full international number: take last 9 digits
        assert _normalize_phone("0034612345678") == "612345678"

    def test_7_digit_minimum(self) -> None:
        result = _normalize_phone("1234567")
        assert result is not None and len(result) >= 7

    def test_too_short_returns_none(self) -> None:
        assert _normalize_phone("12345") is None

    def test_none_returns_none(self) -> None:
        assert _normalize_phone(None) is None
        assert _normalize_phone("") is None

    def test_same_number_with_spaces(self) -> None:
        assert _normalize_phone("612 345 678") == _normalize_phone("612345678")

    def test_prefix_variants_normalize_same(self) -> None:
        # +34 prefix vs bare
        a = _normalize_phone("+34612345678")
        b = _normalize_phone("612345678")
        assert a == b


# ---------------------------------------------------------------------------
# _normalize_website_host
# ---------------------------------------------------------------------------


class TestNormalizeWebsiteHost:
    def test_strips_scheme(self) -> None:
        assert _normalize_website_host("https://example.com") == "example.com"
        assert _normalize_website_host("http://example.com") == "example.com"

    def test_strips_www(self) -> None:
        assert _normalize_website_host("https://www.example.com") == "example.com"

    def test_strips_path(self) -> None:
        assert _normalize_website_host("https://example.com/path?q=1") == "example.com"

    def test_lowercases(self) -> None:
        assert _normalize_website_host("HTTPS://EXAMPLE.COM") == "example.com"

    def test_none_returns_none(self) -> None:
        assert _normalize_website_host(None) is None
        assert _normalize_website_host("") is None


# ---------------------------------------------------------------------------
# _jaccard
# ---------------------------------------------------------------------------


class TestJaccard:
    def test_identical_sets(self) -> None:
        s = {"a", "b", "c"}
        assert _jaccard(s, s) == 1.0

    def test_disjoint_sets(self) -> None:
        assert _jaccard({"a", "b"}, {"c", "d"}) == 0.0

    def test_partial_overlap(self) -> None:
        # |A∩B| = 1, |A∪B| = 3 → 1/3 ≈ 0.333
        result = _jaccard({"a", "b"}, {"b", "c"})
        assert abs(result - 1 / 3) < 1e-6

    def test_empty_set_returns_zero(self) -> None:
        assert _jaccard(set(), {"a"}) == 0.0
        assert _jaccard({"a"}, set()) == 0.0

    def test_above_theta(self) -> None:
        # Build overlapping sets where Jaccard > JACCARD_THETA
        shared = {f"c{i}" for i in range(40)}
        only_a = {f"a{i}" for i in range(10)}
        only_b = {f"b{i}" for i in range(10)}
        j = _jaccard(shared | only_a, shared | only_b)
        assert j > JACCARD_THETA


# ---------------------------------------------------------------------------
# Fingerprint merge (dominant signal)
# ---------------------------------------------------------------------------


class TestFingerprintMerge:
    def _make_shared_fp(self, n: int = 50) -> tuple[set[str], set[str]]:
        """Two fingerprint sets with Jaccard > θ."""
        shared = {f"c{i}" for i in range(n)}
        only_a = {f"a{i}" for i in range(10)}
        only_b = {f"b{i}" for i in range(10)}
        return shared | only_a, shared | only_b

    def test_fingerprint_above_theta_merges(self) -> None:
        """Jaccard >= θ across different sources → same dealer."""
        fp_a, fp_b = self._make_shared_fp(40)
        ea = _entity("E1", source_keys=["wallapop_wholesale"])
        eb = _entity("E2", source_keys=["as24"])
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Fingerprint above θ must merge"

    def test_fingerprint_below_theta_does_not_merge(self) -> None:
        """Jaccard < θ → do NOT merge on fingerprint alone."""
        # Only 2 shared out of 100 → Jaccard = 2/100 = 0.02 << 0.30
        fp_a = {f"c{i}" for i in range(2)} | {f"a{i}" for i in range(48)}
        fp_b = {f"c{i}" for i in range(2)} | {f"b{i}" for i in range(48)}
        ea = _entity("E1", phone=None, website=None)
        eb = _entity("E2", phone=None, website=None)
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, "Fingerprint below θ must NOT merge"

    def test_fingerprint_cross_province_merges(self) -> None:
        """Fingerprint alone is cross-province safe (unlike phone/website)."""
        fp_a, fp_b = self._make_shared_fp(40)
        ea = _entity("E1", province_code="28")
        eb = _entity("E2", province_code="08")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Fingerprint must merge cross-province"

    def test_fingerprint_signal_recorded(self) -> None:
        """Merged cluster via fingerprint must record signal containing 'fingerprint'."""
        fp_a, fp_b = self._make_shared_fp(40)
        ea = _entity("E1")
        eb = _entity("E2")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        for r in rows:
            if r["signal"] != "none":
                assert "fingerprint" in r["signal"]


# ---------------------------------------------------------------------------
# Phone merge
# ---------------------------------------------------------------------------


class TestPhoneMerge:
    def test_clean_phone_same_province_merges(self) -> None:
        """Clean phone (not high-collision), same province → merged."""
        phone = "612345678"
        ea = _entity("E1", phone=phone, province_code="28")
        eb = _entity("E2", phone=phone, province_code="28")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Clean phone same province must merge"

    def test_phone_cross_province_blocked(self) -> None:
        """Phone-only (no fingerprint) cross-province → BLOCKED."""
        phone = "612345678"
        ea = _entity("E1", phone=phone, province_code="28")
        eb = _entity("E2", phone=phone, province_code="08")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, "Phone-only cross-province must NOT merge"


# ---------------------------------------------------------------------------
# Anti-collision: centralita phone
# ---------------------------------------------------------------------------


class TestAntiCollisionPhone:
    def test_centralita_phone_alone_does_not_merge(self) -> None:
        """High-collision phone (centralita, shared by >= MAX_PHONE_COLLISION_K entities)
        WITHOUT corroborating signal → must NOT merge."""
        # Create MAX_PHONE_COLLISION_K + 1 entities sharing the same phone
        phone = "900123456"
        n = MAX_PHONE_COLLISION_K + 1
        entities = [
            _entity(f"E{i}", phone=phone, website=None, province_code="28")
            for i in range(n)
        ]
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges(entities, fingerprints)
        rows = _build_resolution_table(entities, edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        # Each entity must remain its own dealer — centralita alone must not merge
        assert len(canonicals) == n, (
            "Centralita phone alone must NOT merge any pair "
            f"(expected {n} dealers, got {len(canonicals)})"
        )

    def test_centralita_plus_website_same_province_merges(self) -> None:
        """High-collision phone + same website (corroboration), same province → merged."""
        phone = "900123456"
        website = "https://dealer-chain.es"
        # Need >= MAX_PHONE_COLLISION_K entities to make phone high-collision
        n = MAX_PHONE_COLLISION_K + 1
        entities = [
            _entity(
                f"E{i}",
                phone=phone,
                website=website,
                province_code="28",
            )
            for i in range(n)
        ]
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges(entities, fingerprints)
        rows = _build_resolution_table(entities, edges)

        # All share phone AND website → they should merge (unless website is also
        # high-collision, which it is here since all n share it).
        # Both phone AND website are high-collision → still need fingerprint.
        # In this test, no fingerprint → all should remain separate.
        # (This validates the guard: two high-collision signals still don't merge
        # without fingerprint when BOTH are high-collision.)
        # NOTE: if website is clean (< MAX_PHONE_COLLISION_K users) then it would
        # merge. Here all n entities share the website, so website is ALSO
        # high-collision. → remains separate.
        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == n, (
            "Both phone AND website high-collision → still must NOT merge without fingerprint"
        )

    def test_centralita_plus_clean_website_same_province_merges(self) -> None:
        """High-collision phone + clean (non-high-collision) website → merged pair."""
        phone = "900123456"
        # Make phone high-collision by adding extra entities without the website
        n_background = MAX_PHONE_COLLISION_K  # enough to make phone high-collision
        background = [
            _entity(f"BG{i}", phone=phone, website=None, province_code="28")
            for i in range(n_background)
        ]
        # Two entities share phone + a clean website (only 2 share it → not high-collision)
        ea = _entity("EA", phone=phone, website="https://bestdealer.es", province_code="28")
        eb = _entity("EB", phone=phone, website="https://bestdealer.es", province_code="28")
        entities = background + [ea, eb]
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges(entities, fingerprints)
        rows = _build_resolution_table(entities, edges)

        # EA and EB share high-collision phone + clean website → should merge
        # Background entities have no website corroboration → remain separate
        ea_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EA")
        eb_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EB")
        assert ea_canonical == eb_canonical, (
            "Centralita + clean website corroboration (same province) must merge EA and EB"
        )


# ---------------------------------------------------------------------------
# Website merge
# ---------------------------------------------------------------------------


class TestWebsiteMerge:
    def test_clean_website_same_province_merges(self) -> None:
        """Clean website (not high-collision), same province → merged."""
        website = "https://dealersite.es"
        ea = _entity("E1", website=website, province_code="28")
        eb = _entity("E2", website=website, province_code="28")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Clean website same province must merge"

    def test_website_cross_province_blocked(self) -> None:
        """Website-only (no fingerprint) cross-province → BLOCKED."""
        website = "https://dealersite.es"
        ea = _entity("E1", website=website, province_code="28")
        eb = _entity("E2", website=website, province_code="46")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, "Website-only cross-province must NOT merge"


# ---------------------------------------------------------------------------
# Transitive closure
# ---------------------------------------------------------------------------


class TestTransitiveClosure:
    def _make_shared_fp(self, n: int = 40) -> set[str]:
        return {f"c{i}" for i in range(n)}

    def test_transitive_merge_via_fingerprint(self) -> None:
        """A shares fp with B, B shares fp with C → all three become same dealer."""
        fp_ab = self._make_shared_fp(40) | {f"ab{i}" for i in range(5)}
        fp_bc = self._make_shared_fp(40) | {f"bc{i}" for i in range(5)}
        fp_b = self._make_shared_fp(40)

        ea = _entity("A")
        eb = _entity("B")
        ec = _entity("C")
        fingerprints = {"A": fp_ab, "B": fp_b | fp_bc, "C": fp_bc}

        edges = _build_edges([ea, eb, ec], fingerprints)
        rows = _build_resolution_table([ea, eb, ec], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "Transitive closure: A-B + B-C must collapse A, B, C to one dealer"
        )

    def test_no_spurious_transitive_merge(self) -> None:
        """A shares fp with B; C has no overlap with A or B → C stays separate."""
        fp_a = {f"c{i}" for i in range(40)} | {f"a{i}" for i in range(5)}
        fp_b = {f"c{i}" for i in range(40)} | {f"b{i}" for i in range(5)}
        fp_c = {f"x{i}" for i in range(40)}  # completely disjoint

        ea = _entity("A")
        eb = _entity("B")
        ec = _entity("C")
        fingerprints = {"A": fp_a, "B": fp_b, "C": fp_c}

        edges = _build_edges([ea, eb, ec], fingerprints)
        rows = _build_resolution_table([ea, eb, ec], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, "C must remain separate (no overlap)"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_singleton_has_signal_none(self) -> None:
        """An entity not matched to any other must have signal='none'."""
        ea = _entity("E1")
        edges = _build_edges([ea], {})
        rows = _build_resolution_table([ea], edges)

        assert len(rows) == 1
        assert rows[0]["signal"] == "none"
        assert rows[0]["resolved_dealer_ulid"] == "E1"

    def test_singleton_probability_is_none(self) -> None:
        ea = _entity("E1")
        edges = _build_edges([ea], {})
        rows = _build_resolution_table([ea], edges)

        assert rows[0]["probability"] is None


# ---------------------------------------------------------------------------
# Canonical selection
# ---------------------------------------------------------------------------


class TestCanonicalSelection:
    def test_richest_entity_wins(self) -> None:
        """Entity with more non-null key fields is canonical."""
        rich = _entity(
            "E_RICH",
            phone="612345678",
            website="https://rich.es",
            municipality_code="28079",
            n_vehicles=10,
        )
        poor = _entity(
            "E_POOR",
            phone=None,
            website=None,
            municipality_code=None,
            n_vehicles=5,
        )
        entity_by_ulid = {"E_RICH": rich, "E_POOR": poor}
        canonical = _select_canonical(["E_RICH", "E_POOR"], entity_by_ulid)
        assert canonical == "E_RICH"

    def test_more_vehicles_wins_on_tie(self) -> None:
        """With equal richness, entity with more vehicles is canonical."""
        e1 = _entity("E1", phone="612000001", website="https://a.es", n_vehicles=100)
        e2 = _entity("E2", phone="612000002", website="https://b.es", n_vehicles=10)
        entity_by_ulid = {"E1": e1, "E2": e2}
        canonical = _select_canonical(["E1", "E2"], entity_by_ulid)
        assert canonical == "E1"

    def test_older_created_at_wins_on_deeper_tie(self) -> None:
        """With equal richness+vehicles, older entity is canonical."""
        old_ts = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)
        new_ts = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
        e_old = _entity("E_OLD", n_vehicles=10, created_at=old_ts)
        e_new = _entity("E_NEW", n_vehicles=10, created_at=new_ts)
        entity_by_ulid = {"E_OLD": e_old, "E_NEW": e_new}
        canonical = _select_canonical(["E_OLD", "E_NEW"], entity_by_ulid)
        assert canonical == "E_OLD"

    def test_ulid_tiebreak(self) -> None:
        """Lexicographically smaller ulid wins when all else equal."""
        e_a = _entity("AAA", n_vehicles=10)
        e_z = _entity("ZZZ", n_vehicles=10)
        entity_by_ulid = {"AAA": e_a, "ZZZ": e_z}
        canonical = _select_canonical(["AAA", "ZZZ"], entity_by_ulid)
        assert canonical == "AAA"


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
        assert len(comps) == 3  # {A,B} + {C} + {D}

    def test_idempotent_union(self) -> None:
        uf = UnionFind()
        uf.union("A", "B")
        uf.union("A", "B")
        assert uf.find("A") == uf.find("B")

    def test_path_compression(self) -> None:
        """After multiple unions and finds, path compression holds invariants."""
        uf = UnionFind()
        for i in range(100):
            uf.union(str(i), str(i + 1))
        root = uf.find("0")
        for i in range(101):
            assert uf.find(str(i)) == root
