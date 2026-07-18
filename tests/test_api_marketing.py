"""Contract/DB tests for /entities/{cdp}/listing-audit (pilar 07-marketing, F1).

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
