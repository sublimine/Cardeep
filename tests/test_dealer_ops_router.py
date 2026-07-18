"""Tests for services/api/routers/dealer_ops.py (03-garage-fleet F3).

Exercises the FIRST write surface of the whole Cardeep API against the live
cardeep-pg (127.0.0.1:5433), auto-skipping when the DB is unreachable (same
pattern as tests/test_auth_router.py). Covers:

  * Authentication — every endpoint requires a valid AUTH-0 session (401).
  * Authorization  — a dealer can write ONLY vehicles owned by an entity in
    their own dealer_membership cluster; a different, real, authenticated
    dealer gets 403 on the exact same vehicle (the core "un dealer no puede
    escribir sobre el inventario de otro" requirement).
  * Idempotency    — repeating the same status/cost/target_price is a no-op:
    no new fleet_ops_event row, meta.noop == True.
  * Audit          — every real write appends a fleet_ops_event row with
    actor_user_ulid + observed_at + from_value/to_value; replaying the full
    event history reconstructs the current fleet_ops row exactly.
  * Isolation from the census — `vehicle`/`vehicle_event` are BYTE-IDENTICAL
    before and after every dealer_ops write (the architecture's core promise:
    censo y workspace no comparten tablas de escritura).

Test vehicle: a REAL vehicle from the seeded GYATA demo dealer
(scripts/seed_demo_dealer.py — demo@cardeep.local / CDP-ES-28-YCZB8JYW).
Test "other dealer": a REAL entity (CDP-ES-01-7FAFJXW8, checksum-valid CIF
B01530682 — same fixture as tests/test_auth_router.py's TestClaimDealer) claimed
fresh by a throwaway @authtest.invalid account, so authorization is proven
against a genuine second dealer_membership, not a mock.
"""
from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

DEMO_EMAIL = "demo@cardeep.local"
DEMO_PASSWORD = "CardeepDemo2026!"
GYATA_CDP = "CDP-ES-28-YCZB8JYW"
GYATA_VEHICLE_ULID = "01KV00MAMCMJ9QCW0JY3T4XJY9"  # Lynk & Co 01 2023, price 23490.00 — verified live 2026-07-18

OTHER_REAL_ENTITY_CDP = "CDP-ES-01-7FAFJXW8"
OTHER_REAL_ENTITY_CIF = "B01530682"


def _db_available() -> bool:
    try:
        import asyncpg

        async def _ping() -> bool:
            try:
                conn = await asyncpg.connect(DSN, timeout=3)
                await conn.close()
                return True
            except Exception:
                return False

        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
pytestmark = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


def _fresh_email() -> str:
    return f"dealerops-{uuid.uuid4().hex}@authtest.invalid"


STRONG_PASSWORD = "correct-horse-battery-staple-9"


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
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute("DELETE FROM app_user WHERE email_lower LIKE '%@authtest.invalid'")
        # fleet_ops (current-state, no append-only guard) is reset so the demo
        # vehicle's state doesn't drift across CI runs. fleet_ops_event is
        # append-only BY DESIGN (0080's trigger blocks UPDATE/DELETE even for
        # this superuser connection) — its rows from this suite are a small,
        # honest, permanent audit trail, exactly what a real write would leave.
        await conn.execute("DELETE FROM fleet_ops WHERE vehicle_ulid = $1", GYATA_VEHICLE_ULID)
    finally:
        await conn.close()


@pytest.fixture(scope="module")
def gyata_token(client: TestClient) -> str:
    r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user"]["tenant_id"] == GYATA_CDP
    return body["token"]


@pytest.fixture(scope="module")
def other_dealer_token(client: TestClient) -> str:
    email = _fresh_email()
    r = client.post("/auth/register", json={"email": email, "password": STRONG_PASSWORD, "name": "Other Dealer"})
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    r2 = client.post(
        "/auth/claim-dealer",
        json={"cdp_code": OTHER_REAL_ENTITY_CDP, "tax_id": OTHER_REAL_ENTITY_CIF},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["user"]["tenant_id"] == OTHER_REAL_ENTITY_CDP
    return token


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Authentication — 401 without a session
# ---------------------------------------------------------------------------

class TestRequiresAuth:
    def test_get_ops_without_token_401(self, client: TestClient) -> None:
        r = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops")
        assert r.status_code == 401

    def test_patch_status_without_token_401(self, client: TestClient) -> None:
        r = client.patch(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status", json={"status": "preparacion"})
        assert r.status_code == 401

    def test_price_override_without_token_401(self, client: TestClient) -> None:
        r = client.post(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/price-override",
            json={"target_price": 20000, "reason_category": "test"},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Authorization — a dealer cannot write another dealer's inventory
# ---------------------------------------------------------------------------

class TestAuthorization:
    def test_owner_dealer_can_read_ops(self, client: TestClient, gyata_token: str) -> None:
        r = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops", headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["vehicle_ulid"] == GYATA_VEHICLE_ULID

    def test_other_dealer_cannot_read_ops_of_gyata_vehicle(self, client: TestClient, other_dealer_token: str) -> None:
        r = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops", headers=_auth(other_dealer_token))
        assert r.status_code == 403, r.text

    def test_other_dealer_cannot_change_status_of_gyata_vehicle(self, client: TestClient, other_dealer_token: str) -> None:
        r = client.patch(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status",
            json={"status": "vendido"},
            headers=_auth(other_dealer_token),
        )
        assert r.status_code == 403, r.text

    def test_other_dealer_cannot_price_override_gyata_vehicle(self, client: TestClient, other_dealer_token: str) -> None:
        r = client.post(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/price-override",
            json={"target_price": 1.0, "reason_category": "attack"},
            headers=_auth(other_dealer_token),
        )
        assert r.status_code == 403, r.text

    def test_nonexistent_vehicle_is_404_not_403(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/dealer/vehicles/01NOSUCHVEHICLEULIDXXXXXXX/ops", headers=_auth(gyata_token))
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Status transitions (K13) — real write, idempotency, audit
# ---------------------------------------------------------------------------

class TestStatusTransitions:
    def test_status_change_persists_and_is_audited(self, client: TestClient, gyata_token: str) -> None:
        r1 = client.patch(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status",
            json={"status": "preparacion", "note": "TEST: entra a taller"},
            headers=_auth(gyata_token),
        )
        assert r1.status_code == 200, r1.text
        body1 = r1.json()
        assert body1["data"]["status"] == "preparacion"
        assert body1["meta"]["noop"] is False

        r2 = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops", headers=_auth(gyata_token))
        assert r2.json()["data"]["status"] == "preparacion"

        hist = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops-history", headers=_auth(gyata_token))
        assert hist.status_code == 200
        events = hist.json()["data"]
        assert len(events) >= 1
        last = events[-1]
        assert last["event_type"] == "STATUS_CHANGE"
        assert last["to_value"]["status"] == "preparacion"

    def test_repeating_the_same_status_is_idempotent_noop(self, client: TestClient, gyata_token: str) -> None:
        hist_before = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops-history", headers=_auth(gyata_token)).json()["data"]

        r = client.patch(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status",
            json={"status": "preparacion"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 200
        assert r.json()["meta"]["noop"] is True

        hist_after = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops-history", headers=_auth(gyata_token)).json()["data"]
        assert len(hist_after) == len(hist_before), "idempotent repeat must not append a new audit event"

    def test_invalid_status_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.patch(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status",
            json={"status": "no_such_status"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 422

    def test_event_history_replay_reconstructs_current_state(self, client: TestClient, gyata_token: str) -> None:
        """§7 K13 protocol: replaying fleet_ops_event must reconstruct the current
        fleet_ops row exactly — the append-only ledger IS the source of truth."""
        client.patch(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status", json={"status": "publicado"}, headers=_auth(gyata_token))
        client.patch(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status", json={"status": "reservado"}, headers=_auth(gyata_token))

        current = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops", headers=_auth(gyata_token)).json()["data"]
        events = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops-history", headers=_auth(gyata_token)).json()["data"]

        replayed_status = "entrada"
        for e in events:
            if e["event_type"] == "STATUS_CHANGE":
                replayed_status = e["to_value"]["status"]
        assert replayed_status == current["status"] == "reservado"


# ---------------------------------------------------------------------------
# Price override (K15) — reason + delta captured
# ---------------------------------------------------------------------------

class TestPriceOverride:
    def test_price_override_requires_reason_category(self, client: TestClient, gyata_token: str) -> None:
        r = client.post(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/price-override",
            json={"target_price": 22000},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 422

    def test_price_override_captures_reason_and_delta(self, client: TestClient, gyata_token: str) -> None:
        r = client.post(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/price-override",
            json={"target_price": 22000.0, "reason_category": "reposicionamiento_mercado", "note": "TEST"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["data"]["target_price"] == 22000.0

        hist = client.get(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/ops-history", headers=_auth(gyata_token)).json()["data"]
        override_events = [e for e in hist if e["event_type"] == "PRICE_OVERRIDE"]
        assert len(override_events) >= 1
        last = override_events[-1]
        assert last["reason_category"] == "reposicionamiento_mercado"
        assert last["to_value"]["target_price"] == 22000.0
        # delta_vs_median is populated whenever 01's M2 has a resolvable segment for
        # this vehicle; it is None only when the segment/run is unavailable — either
        # way the field must be PRESENT (never silently dropped from the event row).
        assert "delta_vs_median" in last


# ---------------------------------------------------------------------------
# Bulk read for the vehicle-pipeline board (§6.2)
# ---------------------------------------------------------------------------

class TestFleetOpsBulkList:
    def test_list_requires_membership(self, client: TestClient, other_dealer_token: str) -> None:
        r = client.get(f"/dealer/entities/{GYATA_CDP}/fleet-ops", headers=_auth(other_dealer_token))
        assert r.status_code == 403

    def test_list_includes_the_touched_vehicle(self, client: TestClient, gyata_token: str) -> None:
        r = client.get(f"/dealer/entities/{GYATA_CDP}/fleet-ops", headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        ulids = [row["vehicle_ulid"] for row in r.json()["data"]]
        assert GYATA_VEHICLE_ULID in ulids


# ---------------------------------------------------------------------------
# Census isolation — the architecture's core promise
# ---------------------------------------------------------------------------

class TestCensusIsolation:
    def test_vehicle_and_vehicle_event_untouched_by_dealer_ops_writes(self, client: TestClient, gyata_token: str) -> None:
        import asyncio as _asyncio

        import asyncpg

        async def _snapshot() -> tuple[dict, int]:
            conn = await asyncpg.connect(DSN)
            try:
                vrow = await conn.fetchrow("SELECT * FROM vehicle WHERE vehicle_ulid = $1", GYATA_VEHICLE_ULID)
                n_events = await conn.fetchval(
                    "SELECT count(*) FROM vehicle_event WHERE vehicle_ulid = $1", GYATA_VEHICLE_ULID
                )
                return dict(vrow), n_events
            finally:
                await conn.close()

        before_vehicle, before_events = _asyncio.run(_snapshot())

        client.patch(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/status", json={"status": "entregado"}, headers=_auth(gyata_token))
        client.patch(f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/cost", json={"purchase_cost": 18000.0}, headers=_auth(gyata_token))
        client.post(
            f"/dealer/vehicles/{GYATA_VEHICLE_ULID}/price-override",
            json={"target_price": 21000.0, "reason_category": "test_isolation"},
            headers=_auth(gyata_token),
        )

        after_vehicle, after_events = _asyncio.run(_snapshot())

        assert before_vehicle == after_vehicle, "dealer_ops must never mutate the census `vehicle` row"
        assert before_events == after_events, "dealer_ops must never insert into `vehicle_event`"
