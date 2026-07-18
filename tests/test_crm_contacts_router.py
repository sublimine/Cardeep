"""Tests for services/api/routers/crm_contacts.py (06-unified-crm-chat F2).

Same live-DB + TestClient pattern as tests/test_dealer_ops_router.py /
tests/test_auth_router.py. Covers CRUD, per-tenant dedup (409), tenant isolation
(a second dealer never sees another tenant's contacts), and the unified-timeline
join (crm_activity + crm_message).
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
OTHER_REAL_ENTITY_CDP = "CDP-ES-01-7FAFJXW8"
OTHER_REAL_ENTITY_CIF = "B01530682"


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
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute("DELETE FROM app_user WHERE email_lower LIKE '%@authtest.invalid'")
        await conn.execute(
            "DELETE FROM crm_contact WHERE name LIKE 'ZZTEST_%'"
            " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_consent)"
            " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_deal)"
        )
    finally:
        await conn.close()


def _fresh_email() -> str:
    return f"crmcontacts-{uuid.uuid4().hex}@authtest.invalid"


STRONG_PASSWORD = "correct-horse-battery-staple-9"


@pytest.fixture(scope="module")
def gyata_token(client: TestClient) -> str:
    r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["token"]


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
    return token


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique_name(prefix: str) -> str:
    return f"ZZTEST_{prefix}_{uuid.uuid4().hex[:8]}"


class TestRequiresAuth:
    def test_list_requires_token(self, client: TestClient) -> None:
        assert client.get("/contacts").status_code == 401

    def test_create_requires_token(self, client: TestClient) -> None:
        assert client.post("/contacts", json={"name": "X"}).status_code == 401


class TestCreateAndList:
    def test_create_persists_for_real(self, client: TestClient, gyata_token: str) -> None:
        name = _unique_name("Create")
        r = client.post(
            "/contacts",
            json={"name": name, "email": f"{name}@example.invalid", "phone": "611222333"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["name"] == name
        assert body["phone"] == "+34611222333"
        assert body["dealCount"] == 0

        listing = client.get(f"/contacts?search={name}", headers=_auth(gyata_token))
        assert listing.status_code == 200
        assert listing.json()["total"] == 1
        assert listing.json()["contacts"][0]["id"] == body["id"]

    def test_create_missing_name_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.post("/contacts", json={"email": "x@example.invalid"}, headers=_auth(gyata_token))
        assert r.status_code == 422

    def test_duplicate_phone_same_tenant_is_409(self, client: TestClient, gyata_token: str) -> None:
        name1 = _unique_name("DupA")
        name2 = _unique_name("DupB")
        r1 = client.post("/contacts", json={"name": name1, "phone": "699888777"}, headers=_auth(gyata_token))
        assert r1.status_code == 201, r1.text
        r2 = client.post("/contacts", json={"name": name2, "phone": "699888777"}, headers=_auth(gyata_token))
        assert r2.status_code == 409, r2.text

    def test_other_dealer_cannot_see_gyata_contacts(
        self, client: TestClient, gyata_token: str, other_dealer_token: str,
    ) -> None:
        name = _unique_name("Isolation")
        r = client.post("/contacts", json={"name": name}, headers=_auth(gyata_token))
        assert r.status_code == 201, r.text
        created_id = r.json()["id"]

        other_listing = client.get(f"/contacts?search={name}", headers=_auth(other_dealer_token))
        assert other_listing.status_code == 200
        assert other_listing.json()["total"] == 0

        other_detail = client.get(f"/contacts/{created_id}", headers=_auth(other_dealer_token))
        assert other_detail.status_code == 404, "a contact must not resolve for a foreign tenant"


class TestDetailAndTimeline:
    def test_detail_includes_manual_activity_in_timeline(self, client: TestClient, gyata_token: str) -> None:
        name = _unique_name("Timeline")
        r = client.post("/contacts", json={"name": name}, headers=_auth(gyata_token))
        contact_id = r.json()["id"]

        async def _seed_activity() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                entity_row = await conn.fetchrow("SELECT entity_ulid FROM entity WHERE cdp_code = $1", GYATA_CDP)
                from pipeline.ids import ulid
                await conn.execute(
                    "INSERT INTO crm_activity (activity_ulid, entity_ulid, contact_ulid, type, body) "
                    "VALUES ($1, $2, $3, 'call', 'Llamada de prueba')",
                    ulid(), entity_row["entity_ulid"], contact_id,
                )
            finally:
                await conn.close()

        asyncio.run(_seed_activity())

        detail = client.get(f"/contacts/{contact_id}", headers=_auth(gyata_token))
        assert detail.status_code == 200, detail.text
        activities = detail.json()["activities"]
        assert len(activities) == 1
        assert activities[0]["type"] == "call"
        assert activities[0]["body"] == "Llamada de prueba"

    def test_detail_nonexistent_is_404(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/contacts/01NOSUCHCONTACTXXXXXXXXXX", headers=_auth(gyata_token))
        assert r.status_code == 404


class TestUpdateAndDelete:
    def test_patch_updates_fields(self, client: TestClient, gyata_token: str) -> None:
        name = _unique_name("Patch")
        r = client.post("/contacts", json={"name": name}, headers=_auth(gyata_token))
        contact_id = r.json()["id"]

        patched = client.patch(f"/contacts/{contact_id}", json={"phone": "622333444"}, headers=_auth(gyata_token))
        assert patched.status_code == 200, patched.text
        assert patched.json()["phone"] == "+34622333444"

    def test_delete_contact_without_relations(self, client: TestClient, gyata_token: str) -> None:
        name = _unique_name("Delete")
        r = client.post("/contacts", json={"name": name}, headers=_auth(gyata_token))
        contact_id = r.json()["id"]

        deleted = client.delete(f"/contacts/{contact_id}", headers=_auth(gyata_token))
        assert deleted.status_code == 204

        gone = client.get(f"/contacts/{contact_id}", headers=_auth(gyata_token))
        assert gone.status_code == 404

    def test_delete_contact_with_deal_is_409(self, client: TestClient, gyata_token: str) -> None:
        name = _unique_name("DeleteBlocked")
        r = client.post("/contacts", json={"name": name}, headers=_auth(gyata_token))
        contact_id = r.json()["id"]

        deal = client.post("/deals", json={"contactId": contact_id}, headers=_auth(gyata_token))
        assert deal.status_code == 201, deal.text

        blocked = client.delete(f"/contacts/{contact_id}", headers=_auth(gyata_token))
        assert blocked.status_code == 409
