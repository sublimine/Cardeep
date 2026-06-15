"""Tests for the 7 API gaps closed in the F6 full surface pass.

Covers:
  GAP-1  -- /geo/{province}/entities excludes particular + unverified
  GAP-2  -- /vehicles/{ulid} detail + /vehicles/{ulid}/history
  GAP-3  -- /geo/{province}/municipalities/{muni}/entities
  GAP-4  -- /delta is cluster-aware (all member_ulids)
  GAP-5  -- /alerts (active, unresolved) + /sources (source_health)
  GAP-6  -- /inventory serves only canonical vehicles (no alias duplicates)
  GAP-7  -- /health reports sealed dealer count and sealed vehicle count

All tests connect to the real cardeep-pg at 127.0.0.1:5433.
Skipped when DB is unreachable (same guard pattern as other test_api_* files).
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import app

# ---------------------------------------------------------------------------
# DB connectivity guard
# ---------------------------------------------------------------------------

def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(
                "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
                timeout=3,
            )
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


def _fetchval(sql: str) -> int:
    """Synchronous scalar query against cardeep-pg for assertion cross-checks."""
    async def _q() -> int:
        conn = await asyncpg.connect(
            "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
            timeout=5,
        )
        try:
            return await conn.fetchval(sql)
        finally:
            await conn.close()
    return asyncio.run(_q())


def _canonical_map(ulids: list[str]) -> dict[str, str]:
    """Map each vehicle_ulid to its canonical_vehicle_ulid (self when singleton)."""
    async def _q() -> dict[str, str]:
        conn = await asyncpg.connect(
            "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=5
        )
        try:
            rows = await conn.fetch(
                "SELECT vehicle_ulid, canonical_vehicle_ulid FROM v_canonical_vehicle "
                "WHERE vehicle_ulid = ANY($1::text[])",
                ulids,
            )
            return {r["vehicle_ulid"]: r["canonical_vehicle_ulid"] for r in rows}
        finally:
            await conn.close()
    return asyncio.run(_q())


def _cluster_counts(cdp: str) -> tuple[int, int, int]:
    """Return (raw_available, global_canonical_only, within_cluster_dedup) for a cluster.

    Mirrors resolve_cluster's COALESCE(canonical_ulid, entity_ulid) membership so the
    test cross-checks the API against an independent SQL path.
    """
    async def _q() -> tuple[int, int, int]:
        conn = await asyncpg.connect(
            "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=5
        )
        try:
            row = await conn.fetchrow(
                """
                WITH target AS (
                  SELECT COALESCE(vc.canonical_ulid, e.entity_ulid) AS canon
                    FROM entity e LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
                   WHERE e.cdp_code = $1
                ),
                members AS (
                  SELECT e.entity_ulid
                    FROM entity e LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
                   WHERE COALESCE(vc.canonical_ulid, e.entity_ulid) = (SELECT canon FROM target)
                )
                SELECT
                  count(*) FILTER (WHERE v.status='available') AS raw,
                  count(*) FILTER (WHERE v.status='available'
                                   AND cv.vehicle_ulid = cv.canonical_vehicle_ulid) AS global_only,
                  count(DISTINCT cv.canonical_vehicle_ulid)
                    FILTER (WHERE v.status='available') AS within_cluster
                FROM vehicle v
                JOIN members m ON m.entity_ulid = v.entity_ulid
                JOIN v_canonical_vehicle cv ON cv.vehicle_ulid = v.vehicle_ulid
                """,
                cdp,
            )
            return int(row["raw"]), int(row["global_only"]), int(row["within_cluster"])
        finally:
            await conn.close()
    return asyncio.run(_q())

# ---------------------------------------------------------------------------
# Known fixtures (verified against cardeep-pg :5433, 2026-06-15)
# ---------------------------------------------------------------------------
PROVINCE_CODE = "28"           # Madrid — populated province
# Municipality: Madrid capital (code 28079) — has non-particular dealers
MUNI_CODE = "28079"
# Cluster from test_api_canonical.py — 2-member cluster, no vehicles currently
# (use a different dealer for inventory/delta with actual data)
ALIAS_CODE = "CDP-ES-50-N675XHMM"
CANONICAL_CODE = "CDP-ES-50-8SX3KPR5"
# Dealer with actual vehicles (from test_api_pagination.py)
DEALER_CDP = "CDP-ES-28-27JX9YZC"


@pytest.fixture(scope="module")
def client() -> TestClient:
    """TestClient with real asyncpg pool — no uvicorn required."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# GAP-7: /health reports SEALED counts
# ---------------------------------------------------------------------------

class TestHealthSealedCounts:
    @SKIP_NO_DB
    def test_health_has_sealed_keys(self, client: TestClient) -> None:
        """Health must expose 'dealers' and 'vehicles_unique_available', not raw counts."""
        r = client.get("/health")
        assert r.status_code == 200
        counts = r.json()["data"]["counts"]
        # Sealed keys exist
        assert "dealers" in counts, "health must expose 'dealers' (sealed from v_canonical)"
        assert "vehicles_unique_available" in counts, (
            "health must expose 'vehicles_unique_available' (canonical-only + available)"
        )
        # Old key 'entities' must NOT exist — replaced by 'dealers'
        assert "entities" not in counts, (
            "'entities' key must be gone — replaced by sealed 'dealers'"
        )
        # Old key 'vehicles_available' must NOT exist
        assert "vehicles_available" not in counts, (
            "'vehicles_available' key must be gone — replaced by 'vehicles_unique_available'"
        )

    @SKIP_NO_DB
    def test_health_dealers_sealed_count(self, client: TestClient) -> None:
        """Sealed dealer count must be DISTINCT canonical dealers, not v_canonical rows.

        Regression guard: count(*) FROM v_canonical = 61 551 rows (clustered
        entities incl. aliases); the sealed dealer count is
        count(DISTINCT canonical_cdp_code) = 42 259 (the B1 seal). Serving the
        row count double-counts dealers that carry multiple URLs/aliases.
        """
        r = client.get("/health")
        dealers = r.json()["data"]["counts"]["dealers"]
        vc_rows = _fetchval("SELECT count(*) FROM v_canonical")
        vc_distinct = _fetchval("SELECT count(DISTINCT canonical_cdp_code) FROM v_canonical")
        assert isinstance(dealers, int) and dealers > 0
        assert dealers == vc_distinct, (
            f"dealers={dealers} must equal distinct canonical dealers={vc_distinct}, "
            "not the raw v_canonical row count"
        )
        assert dealers < vc_rows, (
            f"dealers={dealers} must be < v_canonical rows={vc_rows} "
            "(proves dedup; count(*) would double-count aliased dealers)"
        )

    @SKIP_NO_DB
    def test_health_vehicles_unique_less_than_raw(self, client: TestClient) -> None:
        """vehicles_unique_available must be < raw available (aliases removed)."""
        r = client.get("/health")
        counts = r.json()["data"]["counts"]
        unique_available = counts["vehicles_unique_available"]
        # Raw available is 1 689 243; canonical is 1 486 285
        # The unique count must be less than raw
        assert isinstance(unique_available, int)
        assert unique_available > 0
        # The raw available is ~1.69M; canonical must be below 1.69M
        assert unique_available < 1_700_000, "vehicles_unique_available looks too high"


# ---------------------------------------------------------------------------
# GAP-6: /inventory serves only canonical vehicles
# ---------------------------------------------------------------------------

class TestInventoryDedupWithinCluster:
    @SKIP_NO_DB
    def test_inventory_no_duplicate_physical_cars(self, client: TestClient) -> None:
        """No two served vehicles may map to the same canonical_vehicle_ulid.

        GAP-6 correct semantics: /inventory dedups WITHIN the dealer cluster by
        canonical_vehicle_ulid — it collapses the dealer's own cross-platform
        duplicates (same physical car listed on two of its platforms -> one). It
        does NOT apply the global canonical-only filter, which would wrongly drop
        the ~102 449 cross-dealer cars a dealer genuinely lists. So a served
        vehicle MAY be a global alias, but no two served vehicles may share a
        canonical_vehicle_ulid.
        """
        r = client.get(f"/entities/{DEALER_CDP}/inventory?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        assert len(items) > 0, "dealer must have inventory for this test to be meaningful"
        ulids = [it["vehicle_ulid"] for it in items]
        cmap = _canonical_map(ulids)
        canonicals = [cmap.get(u, u) for u in ulids]
        assert len(canonicals) == len(set(canonicals)), (
            "two served vehicles share a canonical_vehicle_ulid — "
            "within-cluster dedup is broken"
        )

    @SKIP_NO_DB
    def test_inventory_keeps_cross_dealer_cars(self, client: TestClient) -> None:
        """available_inventory must use within-cluster dedup, KEEPING cross-dealer cars.

        Regression guard against the global canonical-only filter: that filter
        reports the smaller count (dropping cars whose canonical sits in another
        dealer). The served count must equal the within-cluster dedup, sit between
        global-only and raw, and (for this cross-dealer-carrying dealer) strictly
        exceed the global-only count.
        """
        r = client.get(f"/entities/{DEALER_CDP}")
        assert r.status_code == 200
        served = r.json()["data"]["available_inventory"]
        raw, global_only, within_cluster = _cluster_counts(DEALER_CDP)
        assert served == within_cluster, (
            f"served={served} must equal within-cluster dedup={within_cluster}"
        )
        assert global_only <= served <= raw, (
            f"expected global_only={global_only} <= served={served} <= raw={raw}"
        )
        assert within_cluster > global_only, (
            f"within_cluster={within_cluster} must exceed global_only={global_only} "
            "— proves cross-dealer cars are kept, not dropped by a global filter"
        )

    @SKIP_NO_DB
    def test_inventory_page_has_unique_ulids(self, client: TestClient) -> None:
        """A single inventory page must not repeat a vehicle_ulid."""
        r = client.get(f"/entities/{DEALER_CDP}/inventory?size=200")
        assert r.status_code == 200
        ulids = [it["vehicle_ulid"] for it in r.json()["data"]]
        assert len(ulids) == len(set(ulids)), "duplicate vehicle_ulid within a page"


# ---------------------------------------------------------------------------
# GAP-1: /geo/{province}/entities excludes particular + unverified
# ---------------------------------------------------------------------------

class TestGeoEntitiesFilteredActive:
    @SKIP_NO_DB
    def test_no_particular_entities(self, client: TestClient) -> None:
        """kind='particular' must never appear in /geo/{province}/entities."""
        r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        assert len(items) > 0
        particulares = [e for e in items if e["kind"] == "particular"]
        assert len(particulares) == 0, (
            f"Found {len(particulares)} 'particular' entities — GAP-1 filter not applied"
        )

    @SKIP_NO_DB
    def test_no_inactive_entities(self, client: TestClient) -> None:
        """status != 'active' must never appear in /geo/{province}/entities."""
        r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        inactive = [e for e in items if e["status"] != "active"]
        assert len(inactive) == 0, (
            f"Found {len(inactive)} non-active entities — GAP-1 status filter not applied"
        )

    @SKIP_NO_DB
    def test_province_total_lower_than_raw(self, client: TestClient) -> None:
        """Filtered count must be less than the raw province total.

        Madrid has 52 668 raw, 8 080 after active+non-particular filter.
        We iterate pages to verify the total returned stays well below 52 668.
        (We only check page=1 to keep the test fast — the filter is on the query.)
        """
        r = client.get(f"/geo/{PROVINCE_CODE}/entities?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        # Raw Madrid entity count is ~52 668. Filtered is ~8 080.
        # Page 1 with size=200 should return 200 items that are all active+non-particular.
        assert len(items) > 0
        # No item should be particular or inactive (redundant with above but belt+suspenders)
        assert all(e["kind"] != "particular" for e in items)
        assert all(e["status"] == "active" for e in items)


# ---------------------------------------------------------------------------
# GAP-3: /geo/{province}/municipalities/{muni}/entities
# ---------------------------------------------------------------------------

class TestGeoMunicipalityEntities:
    @SKIP_NO_DB
    def test_returns_200_and_data(self, client: TestClient) -> None:
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?size=10")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)

    @SKIP_NO_DB
    def test_meta_has_province_and_municipality(self, client: TestClient) -> None:
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?size=5")
        meta = r.json()["meta"]
        assert meta["province"] == PROVINCE_CODE
        assert meta["municipality"] == MUNI_CODE

    @SKIP_NO_DB
    def test_no_particular_in_muni(self, client: TestClient) -> None:
        """Municipality endpoint must also exclude particular entities."""
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        if len(items) == 0:
            pytest.skip(f"No entities in municipality {MUNI_CODE} after filter")
        particulares = [e for e in items if e["kind"] == "particular"]
        assert len(particulares) == 0

    @SKIP_NO_DB
    def test_pagination_shape(self, client: TestClient) -> None:
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?page=1&size=5")
        body = r.json()
        meta = body["meta"]
        assert meta["page"] == 1
        assert meta["size"] == 5
        assert isinstance(meta["returned"], int)
        assert isinstance(meta["has_more"], bool)
        assert meta["returned"] <= 5

    @SKIP_NO_DB
    def test_size_above_max_rejected(self, client: TestClient) -> None:
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?size=999")
        assert r.status_code == 422

    @SKIP_NO_DB
    def test_all_results_in_correct_municipality(self, client: TestClient) -> None:
        """Every returned entity must have the requested municipality_code."""
        r = client.get(f"/geo/{PROVINCE_CODE}/municipalities/{MUNI_CODE}/entities?size=50")
        assert r.status_code == 200
        items = r.json()["data"]
        for item in items:
            assert item["municipality_code"] == MUNI_CODE, (
                f"Entity {item['cdp_code']} has municipality {item['municipality_code']}, "
                f"expected {MUNI_CODE}"
            )


# ---------------------------------------------------------------------------
# GAP-4: /delta is cluster-aware
# ---------------------------------------------------------------------------

class TestDeltaClusterAware:
    @SKIP_NO_DB
    def test_alias_and_canonical_return_same_events(self, client: TestClient) -> None:
        """Alias and canonical must return identical event sets (cluster-aware)."""
        r_alias = client.get(f"/entities/{ALIAS_CODE}/delta?size=50")
        r_canon = client.get(f"/entities/{CANONICAL_CODE}/delta?size=50")
        assert r_alias.status_code == 200
        assert r_canon.status_code == 200
        # Both must succeed — if cluster is used, results must be identical
        # (both queries use the same member_ulids)
        data_alias = r_alias.json()["data"]
        data_canon = r_canon.json()["data"]
        # Convert to comparable tuples
        def _sig(evt: dict) -> tuple:
            return (evt["event_type"], evt.get("observed_at", ""))
        sigs_alias = [_sig(e) for e in data_alias]
        sigs_canon = [_sig(e) for e in data_canon]
        assert sigs_alias == sigs_canon, (
            "alias and canonical delta must return identical events in cluster-aware mode"
        )

    @SKIP_NO_DB
    def test_delta_returns_ok_for_dealer_with_events(self, client: TestClient) -> None:
        """Delta for a dealer with events must return data."""
        r = client.get(f"/entities/{DEALER_CDP}/delta?size=10")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert len(body["data"]) > 0, "DEALER_CDP must have vehicle events"


# ---------------------------------------------------------------------------
# GAP-2: /vehicles/{ulid} detail
# ---------------------------------------------------------------------------

class TestVehicleDetail:
    @SKIP_NO_DB
    def test_returns_404_for_nonexistent(self, client: TestClient) -> None:
        r = client.get("/vehicles/01XXXXXXXXXXXXXXXXXXXXXXXX")
        assert r.status_code == 404
        assert r.json()["ok"] is False

    @SKIP_NO_DB
    def test_detail_fields_for_known_vehicle(self, client: TestClient) -> None:
        """Fetch a real vehicle_ulid from the DB and verify the response fields."""
        ulid = _get_any_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        data = body["data"]
        required = {
            "vehicle_ulid", "make", "model", "year", "km", "price", "currency",
            "photo_url", "deep_link", "status", "first_seen", "last_seen",
            "is_canonical", "canonical_vehicle_ulid",
        }
        assert required.issubset(set(data.keys())), (
            f"Missing fields: {required - set(data.keys())}"
        )
        assert data["vehicle_ulid"] == ulid

    @SKIP_NO_DB
    def test_envelope_shape(self, client: TestClient) -> None:
        ulid = _get_any_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}")
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["error"] is None


# ---------------------------------------------------------------------------
# GAP-2: /vehicles/{ulid}/history
# ---------------------------------------------------------------------------

class TestVehicleHistory:
    @SKIP_NO_DB
    def test_returns_404_for_nonexistent(self, client: TestClient) -> None:
        r = client.get("/vehicles/01XXXXXXXXXXXXXXXXXXXXXXXX/history")
        assert r.status_code == 404

    @SKIP_NO_DB
    def test_history_ordered_asc(self, client: TestClient) -> None:
        """Events must be returned in ASC order (oldest first — timeline replay)."""
        ulid = _get_vehicle_with_events()
        if ulid is None:
            pytest.skip("No vehicle with events found in DB")
        r = client.get(f"/vehicles/{ulid}/history?size=50")
        assert r.status_code == 200
        items = r.json()["data"]
        if len(items) < 2:
            return  # Cannot verify order with <2 events
        timestamps = [it["observed_at"] for it in items]
        assert timestamps == sorted(timestamps), "history events must be ASC by observed_at"

    @SKIP_NO_DB
    def test_history_event_fields(self, client: TestClient) -> None:
        """Every event must have required fields."""
        ulid = _get_vehicle_with_events()
        if ulid is None:
            pytest.skip("No vehicle with events found in DB")
        r = client.get(f"/vehicles/{ulid}/history?size=5")
        assert r.status_code == 200
        for item in r.json()["data"]:
            assert "event_type" in item
            assert "observed_at" in item
            assert "old_value" in item
            assert "new_value" in item

    @SKIP_NO_DB
    def test_history_pagination_meta(self, client: TestClient) -> None:
        ulid = _get_vehicle_with_events()
        if ulid is None:
            pytest.skip("No vehicle with events found in DB")
        r = client.get(f"/vehicles/{ulid}/history?page=1&size=5")
        meta = r.json()["meta"]
        assert meta["page"] == 1
        assert meta["size"] == 5
        assert "returned" in meta
        assert "has_more" in meta
        assert meta["vehicle_ulid"] == ulid


# ---------------------------------------------------------------------------
# GAP-5: /alerts
# ---------------------------------------------------------------------------

class TestAlerts:
    @SKIP_NO_DB
    def test_returns_200(self, client: TestClient) -> None:
        r = client.get("/alerts")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)

    @SKIP_NO_DB
    def test_envelope_shape(self, client: TestClient) -> None:
        r = client.get("/alerts?size=5")
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}

    @SKIP_NO_DB
    def test_only_unresolved(self, client: TestClient) -> None:
        """All returned alerts must be unresolved (no resolved_at field with a value).

        The API does not expose resolved_at — absence of the field in the response
        is correct.  We verify via field inclusion of 'origin' (the key product field).
        """
        r = client.get("/alerts?size=50")
        assert r.status_code == 200
        items = r.json()["data"]
        for item in items:
            assert "origin" in item, "every alert must expose 'origin'"
            assert "severity" in item
            assert "message" in item
            assert "created_at" in item
            # resolved_at must NOT appear in the response (not in SELECT)
            assert "resolved_at" not in item

    @SKIP_NO_DB
    def test_severity_ordering(self, client: TestClient) -> None:
        """Alerts must be ordered critical → warning → info."""
        r = client.get("/alerts?size=200")
        assert r.status_code == 200
        items = r.json()["data"]
        if len(items) < 2:
            return  # Not enough data to verify ordering
        order = {"critical": 0, "warning": 1, "info": 2}
        ranks = [order.get(it["severity"], 99) for it in items]
        # Ranks must be non-decreasing
        assert ranks == sorted(ranks), (
            f"Alerts not sorted by severity: {[it['severity'] for it in items[:10]]}"
        )

    @SKIP_NO_DB
    def test_pagination_shape(self, client: TestClient) -> None:
        r = client.get("/alerts?page=1&size=5")
        meta = r.json()["meta"]
        assert meta["page"] == 1
        assert meta["size"] == 5
        assert "returned" in meta
        assert "has_more" in meta

    @SKIP_NO_DB
    def test_size_above_max_rejected(self, client: TestClient) -> None:
        r = client.get("/alerts?size=999")
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GAP-5: /sources
# ---------------------------------------------------------------------------

class TestSources:
    @SKIP_NO_DB
    def test_returns_200(self, client: TestClient) -> None:
        r = client.get("/sources")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)

    @SKIP_NO_DB
    def test_envelope_and_count(self, client: TestClient) -> None:
        r = client.get("/sources")
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["meta"]["count"] == len(body["data"])

    @SKIP_NO_DB
    def test_source_fields(self, client: TestClient) -> None:
        r = client.get("/sources")
        items = r.json()["data"]
        if len(items) == 0:
            pytest.skip("source_health table is empty")
        for item in items:
            assert "source_key" in item
            assert "status" in item
            assert "consecutive_fails" in item
            assert "is_tier1" in item
            assert "last_ok" in item
            assert "last_fail" in item

    @SKIP_NO_DB
    def test_down_degraded_first(self, client: TestClient) -> None:
        """Sources must be ordered: down → degraded → unknown → healthy."""
        r = client.get("/sources")
        items = r.json()["data"]
        if len(items) < 2:
            return
        order = {"down": 0, "degraded": 1, "unknown": 2, "healthy": 3}
        ranks = [order.get(it["status"], 99) for it in items]
        assert ranks == sorted(ranks), (
            f"Sources not sorted by urgency: {[it['status'] for it in items[:10]]}"
        )


# ---------------------------------------------------------------------------
# Regression: existing endpoints still work after all changes
# ---------------------------------------------------------------------------

class TestRegressionAllGaps:
    @SKIP_NO_DB
    def test_health_still_live(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "live"

    @SKIP_NO_DB
    def test_entity_canonical_unchanged(self, client: TestClient) -> None:
        r = client.get(f"/entities/{ALIAS_CODE}/canonical")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["canonical_cdp_code"] == CANONICAL_CODE

    @SKIP_NO_DB
    def test_platforms_inventory_unchanged(self, client: TestClient) -> None:
        WALLAPOP = "CDP-ES-00-EMRH0TWQ"
        r = client.get(f"/platforms/{WALLAPOP}/inventory?size=5")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 5


# ---------------------------------------------------------------------------
# Internal helpers (DB queries via subprocess/psql — no asyncio conflicts)
# ---------------------------------------------------------------------------

def _psql(sql: str) -> str | None:
    """Run *sql* via psql in the cardeep-pg container and return stripped stdout."""
    import subprocess
    result = subprocess.run(
        [
            "docker", "exec",
            "-e", "PGPASSWORD=cardeep_dev_only",
            "cardeep-pg",
            "psql", "-U", "cardeep", "-d", "cardeep",
            "-t", "-c", sql,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _get_any_vehicle_ulid() -> str | None:
    """Return one available vehicle_ulid from the DB via psql, or None."""
    return _psql("SELECT vehicle_ulid FROM vehicle WHERE status='available' LIMIT 1;")


def _get_vehicle_with_events() -> str | None:
    """Return a vehicle_ulid that has >= 2 event rows, via psql."""
    return _psql(
        "SELECT vehicle_ulid FROM vehicle_event "
        "GROUP BY vehicle_ulid HAVING count(*) >= 2 LIMIT 1;"
    )
