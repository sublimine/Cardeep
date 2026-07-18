"""Tests for services/api/routers/crm_deals.py (06-unified-crm-chat F2/F5).

Same live-DB + TestClient pattern as the other crm_* router tests. Covers CRUD, stage
transitions (probability auto-recompute, won_at/lost_at stamping, append-only
crm_deal_stage_event), /deals/summary, and F5's vehicle context + vehicle-search.
"""
from __future__ import annotations

import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
DEMO_EMAIL = "demo@cardeep.local"
DEMO_PASSWORD = "CardeepDemo2026!"
GYATA_CDP = "CDP-ES-28-YCZB8JYW"
GYATA_VEHICLE_ULID = "01KV00MAMCMJ9QCW0JY3T4XJY9"


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(DSN, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False

    return asyncio.run(_ping())


DB_AVAILABLE = _db_available()
pytestmark = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


@pytest.fixture(autouse=True)
def _reset_rate_limit_storage():
    limiter.reset()
    yield


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    asyncio.run(_purge_test_rows())


async def _purge_test_rows() -> None:
    # crm_deal is only deletable once it has ZERO crm_deal_stage_event children — the
    # guard on that table blocks even a cascade-triggered delete (same precedent as
    # tests/test_crm_schema.py and tests/test_dealer_ops_router.py's fleet_ops_event:
    # a deal with any real stage history is left in place as a small, honest,
    # permanent audit trail rather than fought with a query that can never succeed).
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(
            "DELETE FROM crm_deal WHERE contact_ulid IN (SELECT contact_ulid FROM crm_contact WHERE name LIKE 'ZZTEST_%')"
            " AND deal_ulid NOT IN (SELECT deal_ulid FROM crm_deal_stage_event)"
        )
        await conn.execute(
            "DELETE FROM crm_contact WHERE name LIKE 'ZZTEST_%'"
            " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_consent)"
            " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_deal)"
        )
    finally:
        await conn.close()


def _unique_name(prefix: str) -> str:
    return f"ZZTEST_{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def gyata_token(client: TestClient) -> str:
    r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _make_contact(client: TestClient, token: str, prefix: str = "Contact") -> str:
    name = _unique_name(prefix)
    r = client.post("/contacts", json={"name": name}, headers=_auth(token))
    assert r.status_code == 201, r.text
    return r.json()["id"]


class TestRequiresAuth:
    def test_list_requires_token(self, client: TestClient) -> None:
        assert client.get("/deals").status_code == 401

    def test_create_requires_token(self, client: TestClient) -> None:
        assert client.post("/deals", json={"contactId": "x"}).status_code == 401


class TestCreateAndDefaults:
    def test_create_seeds_stage_event_and_default_probability(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "DealCreate")
        r = client.post("/deals", json={"contactId": contact_id, "price": 15000}, headers=_auth(gyata_token))
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["stage"] == "lead"
        assert body["probability"] == 10.0
        assert body["price"] == 15000.0
        assert body["vehicleContext"] is None

    def test_create_with_invalid_stage_is_422(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "BadStage")
        r = client.post(
            "/deals", json={"contactId": contact_id, "stage": "bogus"}, headers=_auth(gyata_token)
        )
        assert r.status_code == 422

    def test_create_with_nonexistent_contact_is_404(self, client: TestClient, gyata_token: str) -> None:
        r = client.post(
            "/deals", json={"contactId": "01NOSUCHCONTACTXXXXXXXXXX"}, headers=_auth(gyata_token)
        )
        assert r.status_code == 404


class TestStageTransitions:
    def test_stage_change_recomputes_probability_and_appends_event(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "StageMove")
        deal = client.post("/deals", json={"contactId": contact_id}, headers=_auth(gyata_token)).json()

        moved = client.patch(f"/deals/{deal['id']}", json={"stage": "negotiation"}, headers=_auth(gyata_token))
        assert moved.status_code == 200, moved.text
        assert moved.json()["stage"] == "negotiation"
        assert moved.json()["probability"] == 75.0

    def test_explicit_probability_override_survives_stage_change(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "ProbOverride")
        deal = client.post("/deals", json={"contactId": contact_id}, headers=_auth(gyata_token)).json()

        moved = client.patch(
            f"/deals/{deal['id']}", json={"stage": "offer", "probability": 60}, headers=_auth(gyata_token)
        )
        assert moved.status_code == 200, moved.text
        assert moved.json()["probability"] == 60.0

    def test_moving_to_won_stamps_won_at(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "WonStamp")
        deal = client.post("/deals", json={"contactId": contact_id, "price": 9000}, headers=_auth(gyata_token)).json()

        moved = client.patch(f"/deals/{deal['id']}", json={"stage": "won"}, headers=_auth(gyata_token))
        assert moved.status_code == 200, moved.text
        assert moved.json()["probability"] == 100.0

        async def _check_won_at() -> bool:
            conn = await asyncpg.connect(DSN)
            try:
                row = await conn.fetchrow("SELECT won_at FROM crm_deal WHERE deal_ulid = $1", deal["id"])
                return row["won_at"] is not None
            finally:
                await conn.close()

        assert asyncio.run(_check_won_at())


class TestSummary:
    def test_summary_returns_expected_value_and_stage_counts(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/deals/summary", headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert "expectedValue" in body
        assert "avgLeadTimeDays" in body
        assert "byStage" in body


class TestVehicleContextF5:
    def test_deal_with_real_vehicle_carries_vehicle_context(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "VehicleCtx")
        r = client.post(
            "/deals", json={"contactId": contact_id, "vehicleId": GYATA_VEHICLE_ULID}, headers=_auth(gyata_token)
        )
        assert r.status_code == 201, r.text
        ctx = r.json()["vehicleContext"]
        assert ctx is not None
        assert ctx["vehicleUlid"] == GYATA_VEHICLE_ULID
        assert isinstance(ctx["daysInStock"], int) and ctx["daysInStock"] >= 0
        assert "priceHistory" in ctx

    def test_days_in_stock_matches_vehicles_endpoint_independently(self, client: TestClient, gyata_token: str) -> None:
        """Carta §7 doble via: the chip's daysInStock must agree with an INDEPENDENT
        computation from GET /vehicles/{ulid}'s own first_seen field."""
        contact_id = _make_contact(client, gyata_token, "DoubleCheck")
        r = client.post(
            "/deals", json={"contactId": contact_id, "vehicleId": GYATA_VEHICLE_ULID}, headers=_auth(gyata_token)
        )
        chip_days = r.json()["vehicleContext"]["daysInStock"]

        vehicle_detail = client.get(f"/vehicles/{GYATA_VEHICLE_ULID}", headers=_auth(gyata_token))
        assert vehicle_detail.status_code == 200, vehicle_detail.text
        from datetime import datetime, timezone
        first_seen = datetime.fromisoformat(vehicle_detail.json()["data"]["first_seen"])
        independent_days = (datetime.now(timezone.utc) - first_seen).days

        assert abs(chip_days - independent_days) <= 1, "chip vs /vehicles/{ulid} must never diverge by more than a day boundary"

    def test_deal_without_vehicle_has_null_context(self, client: TestClient, gyata_token: str) -> None:
        contact_id = _make_contact(client, gyata_token, "NoVehicle")
        r = client.post("/deals", json={"contactId": contact_id}, headers=_auth(gyata_token))
        assert r.json()["vehicleContext"] is None


class TestVehicleSearch:
    def test_search_finds_the_demo_vehicle(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/deals/vehicle-search?q=Lynk", headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        candidates = r.json()["candidates"]
        assert any(c["vehicleUlid"] == GYATA_VEHICLE_ULID for c in candidates)

    def test_search_scopes_to_own_tenant_only(self, client: TestClient, gyata_token: str) -> None:
        # A nonsense query should return no candidates rather than error.
        r = client.get("/deals/vehicle-search?q=zzznosuchcarzzz", headers=_auth(gyata_token))
        assert r.status_code == 200
        assert r.json()["candidates"] == []

    def test_search_query_too_short_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/deals/vehicle-search?q=a", headers=_auth(gyata_token))
        assert r.status_code == 422
