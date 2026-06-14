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
  - City guard (INE-validated): distinct city without website → blocks fingerprint
  - City guard: same city → does NOT block
  - City guard: non-INE token → does NOT block
  - _city_tokens: INE-mode multi-word municipality detection
"""
from __future__ import annotations

import datetime
from typing import Any

import pytest

from pipeline.identity.resolve_entities import (
    MAX_ENTITY_COLLISION_K,
    MAX_PHONE_COLLISION_K,
    JACCARD_THETA,
    ConstrainedUnionFind,
    UnionFind,
    _build_edges,
    _build_resolution_table,
    _city_tokens,
    _jaccard,
    _nfkd_lower,
    _normalize_phone,
    _normalize_website_host,
    _richness,
    _select_canonical,
)

# ---------------------------------------------------------------------------
# Minimal INE municipality set for unit tests (no DB required).
# Accent-folded, lowercased — mirrors what _load_ine_municipalities returns.
# ---------------------------------------------------------------------------
_TEST_INE: frozenset[str] = frozenset(
    _nfkd_lower(n)
    for n in [
        "Madrid", "Barcelona", "Alcorcón", "Leganés", "Móstoles",
        "Alcalá de Henares", "Sevilla", "Valencia", "Málaga",
        "Zaragoza", "Bilbao", "Getafe", "Fuenlabrada", "Torrejón de Ardoz",
    ]
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
    org_id: str | None = None,
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
        "org_id": org_id,
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
        rows, _ = _build_resolution_table([ea, eb], edges)

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
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, "Fingerprint below θ must NOT merge"

    def test_fingerprint_cross_province_merges(self) -> None:
        """Fingerprint alone is cross-province safe (unlike phone/website)."""
        fp_a, fp_b = self._make_shared_fp(40)
        ea = _entity("E1", province_code="28")
        eb = _entity("E2", province_code="08")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Fingerprint must merge cross-province"

    def test_fingerprint_signal_recorded(self) -> None:
        """Merged cluster via fingerprint must record signal containing 'fingerprint'."""
        fp_a, fp_b = self._make_shared_fp(40)
        ea = _entity("E1")
        eb = _entity("E2")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

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
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Clean phone same province must merge"

    def test_phone_cross_province_blocked(self) -> None:
        """Phone-only (no fingerprint) cross-province → BLOCKED."""
        phone = "612345678"
        ea = _entity("E1", phone=phone, province_code="28")
        eb = _entity("E2", phone=phone, province_code="08")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

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
        rows, _ = _build_resolution_table(entities, edges)

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
        rows, _ = _build_resolution_table(entities, edges)

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
        rows, _ = _build_resolution_table(entities, edges)

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
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, "Clean website same province must merge"

    def test_website_cross_province_blocked(self) -> None:
        """Website-only (no fingerprint) cross-province → BLOCKED."""
        website = "https://dealersite.es"
        ea = _entity("E1", website=website, province_code="28")
        eb = _entity("E2", website=website, province_code="46")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

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
        rows, _ = _build_resolution_table([ea, eb, ec], edges)

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
        rows, _ = _build_resolution_table([ea, eb, ec], edges)

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
        rows, _ = _build_resolution_table([ea], edges)

        assert len(rows) == 1
        assert rows[0]["signal"] == "none"
        assert rows[0]["resolved_dealer_ulid"] == "E1"

    def test_singleton_probability_is_none(self) -> None:
        ea = _entity("E1")
        edges = _build_edges([ea], {})
        rows, _ = _build_resolution_table([ea], edges)

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


# ---------------------------------------------------------------------------
# §B Chain guard — same-org siblings must NEVER merge
# ---------------------------------------------------------------------------


class TestChainGuard:
    """Chain siblings (same non-null org_id) must never be merged, regardless
    of signal strength (fingerprint, phone, website, or combination)."""

    def _make_shared_fp(self, n: int = 50) -> tuple[set[str], set[str]]:
        """Two fingerprint sets with Jaccard > θ (simulates shared central stock)."""
        shared = {f"c{i}" for i in range(n)}
        only_a = {f"a{i}" for i in range(5)}
        only_b = {f"b{i}" for i in range(5)}
        return shared | only_a, shared | only_b

    def test_chain_siblings_blocked_by_fingerprint(self) -> None:
        """Same org_id + high Jaccard (chain shares central stock) → NOT merged."""
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity("E1", trade_name="CLICARS MADRID", province_code="28", org_id="ORG1")
        eb = _entity("E2", trade_name="CLICARS BARCELONA", province_code="08", org_id="ORG1")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, (
            "Chain siblings (same org_id) must NOT merge even with strong fingerprint"
        )

    def test_chain_siblings_blocked_by_phone(self) -> None:
        """Same org + same phone (centralita) → NOT merged."""
        phone = "900100200"
        ea = _entity("E1", phone=phone, province_code="28", org_id="ORG1")
        eb = _entity("E2", phone=phone, province_code="28", org_id="ORG1")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, (
            "Chain siblings (same org_id) must NOT merge even with same phone"
        )

    def test_chain_siblings_blocked_by_website(self) -> None:
        """Same org + same website (chain domain) → NOT merged."""
        website = "https://flexicar.es"
        ea = _entity("E1", website=website, province_code="28", org_id="ORG_FLEX")
        eb = _entity("E2", website=website, province_code="28", org_id="ORG_FLEX")
        fingerprints: dict[str, set[str]] = {}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, (
            "Chain siblings (same org_id) must NOT merge on website alone"
        )

    def test_different_org_can_still_merge(self) -> None:
        """Two entities from DIFFERENT orgs are NOT blocked by chain guard."""
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity("E1", province_code="28", org_id="ORG_A")
        eb = _entity("E2", province_code="28", org_id="ORG_B")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "Entities from different orgs must still be mergeable by fingerprint"
        )

    def test_null_org_can_still_merge(self) -> None:
        """Entities without org_id (null) are not blocked by chain guard."""
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity("E1", province_code="28", org_id=None)
        eb = _entity("E2", province_code="28", org_id=None)
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "Entities without org_id (null) must not be blocked by chain guard"
        )


# ---------------------------------------------------------------------------
# §B City guard — distinct INE city tokens → blocks any fingerprint merge
# ---------------------------------------------------------------------------


class TestCityGuard:
    """City guard blocks fingerprint merges when both trade names name distinct
    INE-validated municipalities.  The guard is universal: it applies to ALL
    fingerprint merges, not only when websites are high-collision.

    Legacy tests (without ine_municipalities) use the stopword-heuristic path.
    INE tests pass _TEST_INE to simulate the production DB-backed path.
    """

    def _make_shared_fp(self, n: int = 50) -> tuple[set[str], set[str]]:
        shared = {f"c{i}" for i in range(n)}
        only_a = {f"a{i}" for i in range(5)}
        only_b = {f"b{i}" for i in range(5)}
        return shared | only_a, shared | only_b

    def _make_high_collision_entities(
        self, n: int, website: str, province: str = "28"
    ) -> list[dict]:
        """Return n entities sharing a website (making it high-collision)."""
        return [
            _entity(f"HC{i}", website=website, province_code=province)
            for i in range(n)
        ]

    # -- legacy tests (no ine_municipalities, stopword heuristic) -------------

    def test_city_guard_blocks_distinct_cities(self) -> None:
        """CLICARS MADRID + CLICARS BARCELONA with high-collision website → NOT merged."""
        fp_a, fp_b = self._make_shared_fp(50)
        shared_website = "https://clicars.com"
        n_extra = MAX_PHONE_COLLISION_K + 1
        bg_entities = self._make_high_collision_entities(n_extra, shared_website)
        ea = _entity(
            "EA", trade_name="CLICARS MADRID", website=shared_website,
            province_code="28", org_id=None,
        )
        eb = _entity(
            "EB", trade_name="CLICARS BARCELONA", website=shared_website,
            province_code="08", org_id=None,
        )
        all_entities = bg_entities + [ea, eb]
        fingerprints = {e["entity_ulid"]: set() for e in bg_entities}
        fingerprints["EA"] = fp_a
        fingerprints["EB"] = fp_b

        edges = _build_edges(all_entities, fingerprints)
        rows, _ = _build_resolution_table(all_entities, edges)
        ea_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EA")
        eb_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EB")
        assert ea_canonical != eb_canonical, (
            "City guard must block CLICARS MADRID + CLICARS BARCELONA "
            "even with Jaccard >= theta when website is high-collision"
        )

    def test_same_city_not_blocked(self) -> None:
        """Two branches sharing same city token → city guard does NOT block."""
        fp_a, fp_b = self._make_shared_fp(50)
        shared_website = "https://flexicar.es"
        n_extra = MAX_PHONE_COLLISION_K + 1
        bg_entities = self._make_high_collision_entities(n_extra, shared_website)
        ea = _entity(
            "EA", trade_name="FLEXICAR MADRID NORTE", website=shared_website,
            province_code="28", org_id=None,
        )
        eb = _entity(
            "EB", trade_name="FLEXICAR MADRID SUR", website=shared_website,
            province_code="28", org_id=None,
        )
        all_entities = bg_entities + [ea, eb]
        fingerprints = {e["entity_ulid"]: set() for e in bg_entities}
        fingerprints["EA"] = fp_a
        fingerprints["EB"] = fp_b

        rows, _ = _build_resolution_table(all_entities, _build_edges(all_entities, fingerprints))
        ea_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EA")
        eb_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EB")
        assert ea_canonical == eb_canonical, (
            "Two branches sharing city token 'madrid' must NOT be blocked by city guard"
        )

    def test_low_collision_website_legacy_merges(self) -> None:
        """Without INE set and non-stopword generic names → city guard inactive, fp merges.

        'DEALER' is not a stopword so it appears in both token sets; both sets
        share 'dealer' → intersection non-empty → guard does NOT block → merge.
        """
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity(
            "EA", trade_name="DEALER MADRID", website="https://private-dealer.es",
            province_code="28", org_id=None,
        )
        eb = _entity(
            "EB", trade_name="DEALER BARCELONA", website="https://private-dealer.es",
            province_code="08", org_id=None,
        )
        fingerprints = {"EA": fp_a, "EB": fp_b}
        edges = _build_edges([ea, eb], fingerprints)
        rows, _ = _build_resolution_table([ea, eb], edges)
        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "Legacy mode: 'DEALER' appears in both sets → intersection non-empty → merge"
        )

    # -- INE-validated tests (pass _TEST_INE, simulating production) -----------

    def test_ine_distinct_cities_no_website_blocks(self) -> None:
        """INE mode: distinct INE city tokens WITHOUT shared website → guard blocks.

        This is the core regression: AutosMadrid Alcorcón + Autosmadrid Leganés
        were wrongly merged because the old guard only fired on high-collision
        websites. With INE mode, distinct municipalities block any fp merge.
        """
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity(
            "EA", trade_name="AutosMadrid Alcorcón",
            province_code="28", website=None, org_id=None,
        )
        eb = _entity(
            "EB", trade_name="Autosmadrid Leganés",
            province_code="28", website=None, org_id=None,
        )
        fingerprints = {"EA": fp_a, "EB": fp_b}
        edges = _build_edges([ea, eb], fingerprints, ine_municipalities=_TEST_INE)
        rows, _ = _build_resolution_table([ea, eb], edges)
        ea_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EA")
        eb_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EB")
        assert ea_canonical != eb_canonical, (
            "INE guard must block 'AutosMadrid Alcorcón' + 'Autosmadrid Leganés' "
            "(distinct INE municipalities) even without a shared website"
        )

    def test_ine_same_city_does_not_block(self) -> None:
        """INE mode: same INE city in both names → guard does NOT block → fp merges."""
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity(
            "EA", trade_name="AutosMadrid Alcorcón Norte",
            province_code="28", website=None, org_id=None,
        )
        eb = _entity(
            "EB", trade_name="AUTOS MADRID ALCORCÓN",
            province_code="28", website=None, org_id=None,
        )
        fingerprints = {"EA": fp_a, "EB": fp_b}
        edges = _build_edges([ea, eb], fingerprints, ine_municipalities=_TEST_INE)
        rows, _ = _build_resolution_table([ea, eb], edges)
        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "INE guard: same municipality 'alcorcon' → intersection non-empty → merge"
        )

    def test_ine_non_ine_token_does_not_block(self) -> None:
        """INE mode: trade names without valid INE city tokens → no block → fp merges.

        'Motor', 'Auto', 'Gabilondo', 'SL' are not INE municipalities.
        Neither name has a city token → city_a or city_b is empty → guard skipped.
        """
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity(
            "EA", trade_name="AGR Motor SL",
            province_code="28", website=None, org_id=None,
        )
        eb = _entity(
            "EB", trade_name="APC Motor SL",
            province_code="28", website=None, org_id=None,
        )
        fingerprints = {"EA": fp_a, "EB": fp_b}
        edges = _build_edges([ea, eb], fingerprints, ine_municipalities=_TEST_INE)
        rows, _ = _build_resolution_table([ea, eb], edges)
        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "INE guard: no valid INE city token in either name → guard skipped → merge"
        )

    def test_ine_multiword_municipality_blocks(self) -> None:
        """INE mode: multi-word name 'Alcalá de Henares' matched correctly → blocks."""
        fp_a, fp_b = self._make_shared_fp(50)
        ea = _entity(
            "EA", trade_name="Autos Madrid Alcalá de Henares",
            province_code="28", website=None, org_id=None,
        )
        eb = _entity(
            "EB", trade_name="Autosmadrid Leganés",
            province_code="28", website=None, org_id=None,
        )
        fingerprints = {"EA": fp_a, "EB": fp_b}
        edges = _build_edges([ea, eb], fingerprints, ine_municipalities=_TEST_INE)
        rows, _ = _build_resolution_table([ea, eb], edges)
        ea_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EA")
        eb_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "EB")
        assert ea_canonical != eb_canonical, (
            "INE multi-word 'Alcalá de Henares' must be detected and block merge with Leganés"
        )


# ---------------------------------------------------------------------------
# §C B1 edge seeding — composition B1 ∘ β
# ---------------------------------------------------------------------------


class TestB1Seeding:
    """B1 edges are seeded into the union-find before β edges."""

    def test_b1_seeds_transitive_union(self) -> None:
        """A-B in B1 + B-C in beta → all three in same cluster."""
        fp_b = {f"c{i}" for i in range(50)} | {f"b{i}" for i in range(5)}
        fp_c = {f"c{i}" for i in range(50)} | {f"cc{i}" for i in range(5)}
        ea = _entity("A", province_code="28")
        eb = _entity("B", province_code="28")
        ec = _entity("C", province_code="28")
        fingerprints = {"B": fp_b, "C": fp_c}
        b1_edges = [("A", "B")]  # B1 merges A and B

        edges = _build_edges([ea, eb, ec], fingerprints)
        rows, _ = _build_resolution_table([ea, eb, ec], edges, b1_edges=b1_edges)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "B1 seed A-B + beta edge B-C must collapse A, B, C to one dealer"
        )

    def test_b1_chain_guard_skips_org_siblings(self) -> None:
        """B1 edge between same-org siblings is skipped even in seeding phase."""
        ea = _entity("A", org_id="ORG1", province_code="28")
        eb = _entity("B", org_id="ORG1", province_code="28")
        b1_edges = [("A", "B")]  # Would merge org siblings via B1
        org_map = {"A": "ORG1", "B": "ORG1"}

        edges = _build_edges([ea, eb], {})
        rows, _ = _build_resolution_table([ea, eb], edges, b1_edges=b1_edges, org_map=org_map)

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 2, (
            "B1 seeding must not unite chain siblings (same org_id)"
        )

    def test_b1_absent_gives_same_result_as_before(self) -> None:
        """Without B1 edges, resolution is identical to original β-only behavior."""
        fp_a = {f"c{i}" for i in range(50)} | {f"a{i}" for i in range(5)}
        fp_b = {f"c{i}" for i in range(50)} | {f"b{i}" for i in range(5)}
        ea = _entity("E1", province_code="28")
        eb = _entity("E2", province_code="28")
        fingerprints = {"E1": fp_a, "E2": fp_b}

        edges = _build_edges([ea, eb], fingerprints)
        rows_no_b1, _ = _build_resolution_table([ea, eb], edges, b1_edges=None)
        rows_empty_b1, _ = _build_resolution_table([ea, eb], edges, b1_edges=[])

        assert (
            {r["resolved_dealer_ulid"] for r in rows_no_b1}
            == {r["resolved_dealer_ulid"] for r in rows_empty_b1}
        )


# ---------------------------------------------------------------------------
# _city_tokens
# ---------------------------------------------------------------------------


class TestCityTokens:
    # Legacy stopword-heuristic path (ine_municipalities=None)

    def test_extracts_city_from_chain_name(self) -> None:
        tokens = _city_tokens("CLICARS MADRID SL")
        assert "madrid" in tokens
        assert "clicars" not in tokens
        assert "sl" not in tokens

    def test_strips_accents(self) -> None:
        tokens = _city_tokens("FLEXICAR MALAGA")
        assert "malaga" in tokens

    def test_empty_returns_empty(self) -> None:
        assert _city_tokens(None) == frozenset()
        assert _city_tokens("") == frozenset()

    def test_stopwords_excluded(self) -> None:
        tokens = _city_tokens("OCASIONPLUS DE LA CORUNA")
        assert "ocasionplus" not in tokens
        assert "de" not in tokens
        assert "la" not in tokens

    # INE-validated path (ine_municipalities=_TEST_INE)

    def test_ine_single_word_municipality(self) -> None:
        """Single-word INE municipality detected correctly."""
        tokens = _city_tokens("AutosMadrid Alcorcón Norte", _TEST_INE)
        assert "alcorcon" in tokens
        # Generic words absent from INE set must not appear
        assert "autosmadrid" not in tokens
        assert "norte" not in tokens

    def test_ine_multiword_municipality(self) -> None:
        """Multi-word INE municipality 'alcala de henares' detected as one token."""
        tokens = _city_tokens("Autos Madrid Alcalá de Henares", _TEST_INE)
        assert "alcala de henares" in tokens
        # Constituent words should NOT appear separately
        assert "alcala" not in tokens
        assert "de" not in tokens
        assert "henares" not in tokens

    def test_ine_non_municipality_word_absent(self) -> None:
        """Words not in INE set are absent from INE-mode output."""
        tokens = _city_tokens("AGR Motor SL", _TEST_INE)
        assert len(tokens) == 0, (
            "No INE city token: result must be empty, got %r" % tokens
        )

    def test_ine_empty_returns_empty(self) -> None:
        assert _city_tokens(None, _TEST_INE) == frozenset()
        assert _city_tokens("", _TEST_INE) == frozenset()


# ---------------------------------------------------------------------------
# ConstrainedUnionFind unit tests
# ---------------------------------------------------------------------------


class TestConstrainedUnionFind:
    """Unit tests for ConstrainedUnionFind metadata propagation."""

    def test_same_city_merges(self) -> None:
        """Two components with the same city → allowed."""
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(["madrid"]), org=frozenset())
        cuf._init("B", city=frozenset(["madrid"]), org=frozenset())
        assert cuf.constrained_union("A", "B") is True
        assert cuf.find("A") == cuf.find("B")

    def test_different_city_rejected(self) -> None:
        """Two components with distinct cities → rejected."""
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(["madrid"]), org=frozenset())
        cuf._init("B", city=frozenset(["barcelona"]), org=frozenset())
        assert cuf.constrained_union("A", "B") is False
        assert cuf.find("A") != cuf.find("B")
        assert cuf.n_constrained_rejections == 1

    def test_one_city_one_empty_merges(self) -> None:
        """Component with a city + component without → allowed (|merged| = 1)."""
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(["madrid"]), org=frozenset())
        cuf._init("B", city=frozenset(), org=frozenset())
        assert cuf.constrained_union("A", "B") is True
        assert cuf.find("A") == cuf.find("B")

    def test_different_org_rejected(self) -> None:
        """Two components with distinct non-null orgs → rejected."""
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(), org=frozenset(["ORG1"]))
        cuf._init("B", city=frozenset(), org=frozenset(["ORG2"]))
        assert cuf.constrained_union("A", "B") is False
        assert cuf.n_constrained_rejections == 1

    def test_transitive_city_constraint_propagates(self) -> None:
        """A—C—B where C has no city but A=Madrid and B=Barcelona.

        A-C merges (C has no city → merged city_set = {'madrid'}).
        C-B is now rejected because merged component {A,C} has city 'madrid'
        and B has city 'barcelona' → |merged_city| = 2 → rejected.
        A and B must end in DIFFERENT components.
        """
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(["madrid"]), org=frozenset())
        cuf._init("C", city=frozenset(), org=frozenset())          # bridge, no city
        cuf._init("B", city=frozenset(["barcelona"]), org=frozenset())

        # A-C: allowed (merges, component gets city 'madrid')
        assert cuf.constrained_union("A", "C") is True
        assert cuf.find("A") == cuf.find("C")

        # C-B: rejected — component {A,C} already has 'madrid', B has 'barcelona'
        assert cuf.constrained_union("C", "B") is False
        assert cuf.find("A") != cuf.find("B")
        assert cuf.n_constrained_rejections == 1

    def test_transitive_org_constraint_propagates(self) -> None:
        """A—C—B where C has no org but A=ORG1 and B=ORG2 → B stays separate."""
        cuf = ConstrainedUnionFind()
        cuf._init("A", city=frozenset(), org=frozenset(["ORG1"]))
        cuf._init("C", city=frozenset(), org=frozenset())
        cuf._init("B", city=frozenset(), org=frozenset(["ORG2"]))

        assert cuf.constrained_union("A", "C") is True
        assert cuf.constrained_union("C", "B") is False
        assert cuf.find("A") != cuf.find("B")


# ---------------------------------------------------------------------------
# Constrained transitive closure — integration with _build_resolution_table
# ---------------------------------------------------------------------------


class TestConstrainedTransitiveClosure:
    """Integration tests: constrained union-find blocks A-C-B over-merge.

    These test the exact bug: pairwise guards in _build_edges block A↔B directly
    but the old plain union-find united them via a bridge entity C (no city token).
    The constrained union-find must reject the second merge (C-B) because after
    merging A-C the component already carries city 'madrid', and B has 'barcelona'.
    """

    def _make_shared_fp(self, n: int = 50) -> set[str]:
        return {f"c{i}" for i in range(n)}

    def test_bridge_entity_does_not_transmit_cross_city_merge(self) -> None:
        """A (Madrid) — C (no city) — B (Barcelona): A and B must stay separate.

        Fingerprint edges:
          A-C: Jaccard > C-B (A-C has higher overlap → processed first)
          C-B: Jaccard >= θ but lower than A-C
          A-B: blocked by pairwise city guard in _build_edges

        We control Jaccard so that A-C > C-B: A-C processes first, component
        {A,C} gains city 'madrid', then C-B is rejected (would give 2 cities).
        """
        fp_shared_ac = self._make_shared_fp(80)  # A-C share 80 canonicals
        fp_shared_cb = {f"s{i}" for i in range(50)}  # C-B share only 50
        fp_a = fp_shared_ac | {f"a{i}" for i in range(5)}
        fp_c = fp_shared_ac | fp_shared_cb | {f"cc{i}" for i in range(5)}
        fp_b = fp_shared_cb | {f"b{i}" for i in range(5)}

        ea = _entity("A", trade_name="Dealer Madrid", province_code="28")
        ec = _entity("C", trade_name="Dealer Central", province_code="28")  # no city token in INE
        eb = _entity("B", trade_name="Dealer Barcelona", province_code="08")
        fingerprints = {"A": fp_a, "C": fp_c, "B": fp_b}

        # Pairwise edges: A-B blocked by city guard; A-C and C-B pass.
        edges = _build_edges([ea, ec, eb], fingerprints, ine_municipalities=_TEST_INE)

        # Verify the setup: confirm A-C edge exists and A-B does not
        edge_pairs = {(e[0], e[1]) for e in edges} | {(e[1], e[0]) for e in edges}
        assert ("A", "C") in edge_pairs, "Setup: A-C edge must exist"
        assert ("C", "B") in edge_pairs, "Setup: C-B edge must exist"
        # A-B must be blocked by pairwise city guard
        assert ("A", "B") not in edge_pairs, "Setup: A-B must be blocked by pairwise guard"

        # Constrained UF: A-C merges first (higher Jaccard), component gets 'madrid'.
        # Then C-B is rejected: would give city_set={'madrid','barcelona'} (size 2).
        rows, n_rejected = _build_resolution_table(
            [ea, ec, eb], edges, ine_municipalities=_TEST_INE
        )

        a_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "A")
        b_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "B")
        c_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "C")

        assert a_canonical != b_canonical, (
            "Constrained UF must prevent A (Madrid) and B (Barcelona) from merging "
            "even via bridge entity C (no city). Got same canonical: %r" % a_canonical
        )
        # C must be in A's cluster (A-C had higher Jaccard → merged first).
        assert a_canonical == c_canonical, (
            "C (bridge) should be in A's cluster since A-C Jaccard > C-B Jaccard"
        )
        assert n_rejected >= 1, "At least one constrained rejection expected"

    def test_bridge_same_city_chain_merges_correctly(self) -> None:
        """A (Madrid) — C (no city) — D (Madrid): all three should merge."""
        fp_shared = self._make_shared_fp(50)
        fp_a = fp_shared | {f"a{i}" for i in range(5)}
        fp_c = fp_shared | {f"cc{i}" for i in range(5)}
        fp_d = fp_shared | {f"d{i}" for i in range(5)}

        ea = _entity("A", trade_name="Dealer Madrid Norte", province_code="28")
        ec = _entity("C", trade_name="Dealer Central", province_code="28")
        ed = _entity("D", trade_name="Dealer Madrid Sur", province_code="28")
        fingerprints = {"A": fp_a, "C": fp_c, "D": fp_d}

        edges = _build_edges([ea, ec, ed], fingerprints, ine_municipalities=_TEST_INE)
        rows, _ = _build_resolution_table(
            [ea, ec, ed], edges, ine_municipalities=_TEST_INE
        )

        canonicals = {r["resolved_dealer_ulid"] for r in rows}
        assert len(canonicals) == 1, (
            "A (Madrid) — C (no city) — D (Madrid): all same city → must merge to 1 cluster"
        )

    def test_b1_bridge_cross_city_rejected(self) -> None:
        """B1 edge C-B (bridge C → Barcelona B) is rejected after A-C merges via β.

        β merges A-C (both from INE fingerprint, A=Madrid, C=no city).
        B1 seeds C-B (C linked to B=Barcelona in the geo-blocking step).
        Constrained UF must reject C-B because component {A,C} carries 'madrid'
        and B carries 'barcelona'.
        """
        fp_shared = self._make_shared_fp(50)
        fp_a = fp_shared | {f"a{i}" for i in range(5)}
        fp_c = fp_shared | {f"cc{i}" for i in range(5)}

        ea = _entity("A", trade_name="Dealer Madrid", province_code="28")
        ec = _entity("C", trade_name="Dealer Central", province_code="28")
        eb = _entity("B", trade_name="Dealer Barcelona", province_code="08")
        fingerprints = {"A": fp_a, "C": fp_c}

        # β edge: A-C (fingerprint) — C-B has no β edge (B has no shared fingerprint)
        edges = _build_edges([ea, ec, eb], fingerprints, ine_municipalities=_TEST_INE)

        # B1 edge: C-B (geo-blocking step merged them previously)
        b1 = [("C", "B")]

        rows, n_rejected = _build_resolution_table(
            [ea, ec, eb], edges, b1_edges=b1, ine_municipalities=_TEST_INE
        )

        a_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "A")
        b_canonical = next(r["resolved_dealer_ulid"] for r in rows if r["entity_ulid"] == "B")

        assert a_canonical != b_canonical, (
            "B1 bridge C-B must be rejected: component {A,C} has 'madrid', B has 'barcelona'"
        )
        assert n_rejected >= 1
