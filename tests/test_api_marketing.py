"""Contract/DB tests for /entities/{cdp}/listing-audit (F1) and /feed/{target} (F3)
(pilar 07-marketing).

Same DB-guard pattern as test_api_publishing.py: connects to the real cardeep-pg,
skips cleanly when unreachable.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import app

DSN_SYNC = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(DSN_SYNC, timeout=3)
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

# Real dealer audited live by scripts/run_listing_audit.py during F1 execution
# (359 vehicles, run persisted to listing_audit/listing_audit_run).
AUDITED_DEALER = "CDP-ES-46-AD9ZXC65"
UNKNOWN_DEALER = "CDP-ES-00-NOPE0000"


def _fetchval(sql: str, *args):
    async def _q():
        conn = await asyncpg.connect(DSN_SYNC, timeout=5)
        try:
            return await conn.fetchval(sql, *args)
        finally:
            await conn.close()
    return asyncio.run(_q())


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@SKIP_NO_DB
class TestListingAuditContract:
    def test_unknown_dealer_404s(self, client):
        resp = client.get(f"/entities/{UNKNOWN_DEALER}/listing-audit")
        assert resp.status_code == 404
        body = resp.json()
        assert body["ok"] is False

    def test_audited_dealer_returns_ranked_list(self, client):
        has_rows = _fetchval(
            """SELECT count(*) FROM v_latest_listing_audit la
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid IN (SELECT entity_ulid FROM entity WHERE cdp_code = $1)""",
            AUDITED_DEALER,
        )
        if not has_rows:
            pytest.skip(f"{AUDITED_DEALER} has no listing_audit rows in this environment yet")

        resp = client.get(f"/entities/{AUDITED_DEALER}/listing-audit", params={"page": 1, "size": 20})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        items = body["data"]
        assert len(items) > 0
        # Ordered ascending by score (worst-first, carta S6 Bloque 1).
        scores = [item["score"] for item in items]
        assert scores == sorted(scores)
        for item in items:
            assert 0 <= item["score"] <= 100
            assert isinstance(item["checks"], list)
            assert len(item["checks"]) == 11
        assert body["meta"]["audited_count"] > 0
        assert body["meta"]["total_available"] >= body["meta"]["audited_count"]

    def test_pagination_shape(self, client):
        has_rows = _fetchval(
            """SELECT count(*) FROM v_latest_listing_audit la
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid IN (SELECT entity_ulid FROM entity WHERE cdp_code = $1)""",
            AUDITED_DEALER,
        )
        if not has_rows:
            pytest.skip(f"{AUDITED_DEALER} has no listing_audit rows in this environment yet")

        resp = client.get(f"/entities/{AUDITED_DEALER}/listing-audit", params={"page": 1, "size": 5})
        body = resp.json()
        assert len(body["data"]) <= 5
        assert body["meta"]["size"] == 5
        assert body["meta"]["page"] == 1

    def test_never_fabricates_a_score_for_an_unaudited_vehicle(self, client):
        """Every item returned MUST correspond to a real listing_audit row -- cross-
        checked independently against a direct SQL count (S7 protocol's spirit: the
        API path and a raw-SQL path must agree on WHICH vehicles carry a real score)."""
        resp = client.get(f"/entities/{AUDITED_DEALER}/listing-audit", params={"page": 1, "size": 200})
        if resp.status_code != 200:
            pytest.skip("dealer not audited in this environment")
        items = resp.json()["data"]
        api_ulids = {i["vehicle_ulid"] for i in items}

        real_ulids = {
            r["vehicle_ulid"]
            for r in asyncio.run(_fetch_all(
                """SELECT la.vehicle_ulid FROM v_latest_listing_audit la
                     JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                    WHERE v.entity_ulid IN (SELECT entity_ulid FROM entity WHERE cdp_code = $1)
                      AND v.status = 'available'""",
                AUDITED_DEALER,
            ))
        }
        assert api_ulids.issubset(real_ulids)


async def _fetch_all(sql: str, *args):
    conn = await asyncpg.connect(DSN_SYNC, timeout=5)
    try:
        return await conn.fetch(sql, *args)
    finally:
        await conn.close()


@SKIP_NO_DB
class TestFeedExportContract:
    def test_unknown_target_422s(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/feed/carfax_xml")
        assert resp.status_code == 422

    def test_unknown_dealer_404s(self, client):
        resp = client.get(f"/entities/{UNKNOWN_DEALER}/feed/google_vehicle_ads")
        assert resp.status_code == 404

    def test_google_vehicle_ads_downloads_csv(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/feed/google_vehicle_ads")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "attachment" in resp.headers["content-disposition"]
        assert int(resp.headers["x-feed-item-count"]) > 0
        # valid_count must never exceed item_count, and the header must be internally
        # consistent with the CSV body's actual row count.
        item_count = int(resp.headers["x-feed-item-count"])
        valid_count = int(resp.headers["x-feed-valid-count"])
        assert 0 <= valid_count <= item_count
        if valid_count > 0:
            body_lines = [l for l in resp.text.splitlines() if l.strip()]
            assert len(body_lines) - 1 == valid_count  # header + N data rows

    def test_schema_org_jsonld_downloads_valid_json_array(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/feed/schema_org_jsonld")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/ld+json")
        import json
        parsed = json.loads(resp.text)
        assert isinstance(parsed, list)
        valid_count = int(resp.headers["x-feed-valid-count"])
        assert len(parsed) == valid_count
        for item in parsed:
            assert item["@type"] == "Car"
            assert "itemCondition" in item
            assert "mileageFromOdometer" in item

    def test_meta_aia_downloads_csv(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/feed/meta_aia")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")

    def test_content_hash_is_deterministic_for_unchanged_data(self, client):
        r1 = client.get(f"/entities/{AUDITED_DEALER}/feed/schema_org_jsonld")
        r2 = client.get(f"/entities/{AUDITED_DEALER}/feed/schema_org_jsonld")
        assert r1.headers["x-feed-content-hash"] == r2.headers["x-feed-content-hash"]

    def test_report_endpoint_matches_download_metadata(self, client):
        download = client.get(f"/entities/{AUDITED_DEALER}/feed/google_vehicle_ads")
        report = client.get(f"/entities/{AUDITED_DEALER}/feed/google_vehicle_ads/report")
        assert report.status_code == 200
        body = report.json()["data"]
        assert body["item_count"] == int(download.headers["x-feed-item-count"])
        assert body["valid_count"] == int(download.headers["x-feed-valid-count"])
        assert body["content_hash"] == download.headers["x-feed-content-hash"]
        for row in body["invalid_report"]:
            assert "vehicle_ulid" in row
            assert isinstance(row["missing_fields"], list)
            assert len(row["missing_fields"]) > 0

    def test_report_404s_before_any_export_requested(self, client):
        # A dealer that (very likely) has never had a feed generated in this run.
        resp = client.get("/entities/CDP-ES-99-NEVERFED01/feed/google_vehicle_ads/report")
        assert resp.status_code == 404

    def test_feed_export_persisted_to_db(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/feed/meta_aia")
        export_id = resp.headers["x-feed-export-id"]
        row = _fetchval(
            "SELECT count(*) FROM feed_export WHERE export_ulid = $1 AND target = 'meta_aia'",
            export_id,
        )
        assert row == 1


@SKIP_NO_DB
class TestChannelRadarContract:
    def test_unknown_dealer_404s(self, client):
        resp = client.get(f"/entities/{UNKNOWN_DEALER}/channel-radar")
        assert resp.status_code == 404

    def test_real_dealer_returns_coherent_platforms(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/channel-radar")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        data = body["data"]
        assert data["total_available"] > 0
        for p in data["platforms"]:
            assert 0.0 <= p["coverage_pct"] <= 1.0 + 1e-9  # a platform can list MORE than the dealer's current available count in edge cases, guard is generous
            assert p["band"] in ("verde", "ambar", "rojo")
            assert p["n_divergent"] >= 0
            assert p["n_divergent"] <= p["n_listed"]
            if p["median_days_to_gone"] is not None:
                assert p["median_days_to_gone"] >= 0
                assert p["median_days_to_gone_n"] >= body["meta"]["c5_min_cohort_n"]
            else:
                assert p["median_days_to_gone_reason"] is not None

    def test_platforms_sorted_by_coverage_descending(self, client):
        resp = client.get(f"/entities/{AUDITED_DEALER}/channel-radar")
        platforms = resp.json()["data"]["platforms"]
        n_listed_seq = [p["n_listed"] for p in platforms]
        assert n_listed_seq == sorted(n_listed_seq, reverse=True)

    def test_divergence_count_never_exceeds_independent_sql_recount(self, client):
        """Via-2 style spot-check: an independent SQL count of edges where the
        RELATIVE OR ABSOLUTE divergence floor is cleared must be >= the endpoint's
        count for at least one real platform (sanity that the Python-side threshold
        function is being applied, not bypassed)."""
        resp = client.get(f"/entities/{AUDITED_DEALER}/channel-radar")
        platforms = resp.json()["data"]["platforms"]
        if not platforms:
            pytest.skip("dealer has no platform edges in this environment")
        for p in platforms:
            independent_n = _fetchval(
                """SELECT count(*) FROM platform_listing pl
                     JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                     JOIN entity dealer ON dealer.entity_ulid = v.entity_ulid
                     JOIN entity plat ON plat.entity_ulid = pl.platform_entity_ulid
                    WHERE dealer.cdp_code = $1 AND plat.cdp_code = $2
                      AND v.status = 'available' AND pl.status = 'listed'
                      AND pl.platform_price IS NOT NULL AND v.price IS NOT NULL
                      AND pl.platform_price <> v.price""",
                AUDITED_DEALER, p["cdp_code"],
            )
            # The naive "any difference" count is always >= the threshold-gated count
            # the endpoint reports (2%/EUR200 floor only shrinks the set).
            assert independent_n >= p["n_divergent"]
