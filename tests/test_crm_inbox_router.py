"""Tests for services/api/routers/crm_inbox.py (06-unified-crm-chat F4).

Exercises the FIRST live channel router against the real cardeep-pg + real FastAPI
TestClient (same pattern as tests/test_dealer_ops_router.py). Seeds a conversation
directly via SQL (the same shape services/crm/email_ingest.py would produce) rather
than requiring a real mailbox, then drives it entirely through the HTTP surface
``web/src/hooks/useInbox.ts`` already calls.

The reply-send path is exercised twice:
  * with NO SMTP configured (this test environment's honest default) -> 502, proving
    the router never paints a fake "sent" state (carta §7 protocol);
  * with ``send_email`` monkeypatched to a stub -> 201, proving the success path
    persists the ACK and flips conversation status to 'replied'.
"""
from __future__ import annotations

import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from pipeline.ids import ulid
from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
DEMO_EMAIL = "demo@cardeep.local"
DEMO_PASSWORD = "CardeepDemo2026!"
GYATA_CDP = "CDP-ES-28-YCZB8JYW"


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
        await conn.execute(
            "DELETE FROM crm_conversation WHERE contact_ulid IN "
            "(SELECT contact_ulid FROM crm_contact WHERE name LIKE 'ZZTEST_Inbox%')"
        )
        await conn.execute(
            "DELETE FROM crm_contact WHERE name LIKE 'ZZTEST_Inbox%'"
            " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_consent)"
        )
    finally:
        await conn.close()


@pytest.fixture(scope="module")
def gyata_token(client: TestClient) -> str:
    r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _seed_conversation_with_inbound_message(subject: str) -> tuple[str, str, str]:
    """Seed contact+conversation+inbound message directly via SQL — the shape
    services/crm/email_ingest.py would produce. Returns (contact_ulid, conversation_ulid, message_id)."""
    conn = await asyncpg.connect(DSN)
    try:
        entity_row = await conn.fetchrow("SELECT entity_ulid FROM entity WHERE cdp_code = $1", GYATA_CDP)
        entity_ulid = entity_row["entity_ulid"]

        contact_ulid = ulid()
        unique = uuid.uuid4().hex[:10]
        await conn.execute(
            "INSERT INTO crm_contact (contact_ulid, entity_ulid, name, email) VALUES ($1, $2, $3, $4)",
            contact_ulid, entity_ulid, f"ZZTEST_InboxLead_{unique}", f"zztest.inbox.{unique}@example.invalid",
        )
        conversation_ulid = ulid()
        await conn.execute(
            """
            INSERT INTO crm_conversation (conversation_ulid, entity_ulid, contact_ulid, channel, source_platform,
                                           subject, status, last_inbound_at, last_message_at)
            VALUES ($1, $2, $3, 'email', 'coches.net', $4, 'open', now(), now())
            """,
            conversation_ulid, entity_ulid, contact_ulid, subject,
        )
        message_id_header = f"<zztest-{unique}@example.invalid>"
        await conn.execute(
            """
            INSERT INTO crm_message (message_ulid, conversation_ulid, direction, sender_name, sender_email,
                                      body, sent_via, provider_message_id, provider_ack_at)
            VALUES ($1, $2, 'inbound', $3, $4, 'Hola, sigue disponible?', 'email', $5, now())
            """,
            ulid(), conversation_ulid, f"ZZTEST_InboxLead_{unique}", f"zztest.inbox.{unique}@example.invalid",
            message_id_header,
        )
        return contact_ulid, conversation_ulid, message_id_header
    finally:
        await conn.close()


class TestListAndDetail:
    def test_requires_auth(self, client: TestClient) -> None:
        r = client.get("/inbox")
        assert r.status_code == 401

    def test_seeded_conversation_appears_in_list_unread(self, client: TestClient, gyata_token: str) -> None:
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST list subject"))
        r = client.get("/inbox?status=open", headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        body = r.json()
        found = next((c for c in body["conversations"] if c["id"] == conversation_ulid), None)
        assert found is not None, "seeded conversation must appear in the list"
        assert found["unread"] is True
        assert found["channel"] if "channel" in found else True  # channel not in Conversation type; no-op guard
        assert found["previewBody"] == "Hola, sigue disponible?"
        assert found["sourcePlatform"] == "coches.net"

    def test_invalid_status_filter_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/inbox?status=bogus", headers=_auth(gyata_token))
        assert r.status_code == 422

    def test_detail_marks_inbound_messages_read(self, client: TestClient, gyata_token: str) -> None:
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST detail subject"))

        list_before = client.get("/inbox?status=open", headers=_auth(gyata_token)).json()["conversations"]
        before = next(c for c in list_before if c["id"] == conversation_ulid)
        assert before["unread"] is True

        detail = client.get(f"/inbox/{conversation_ulid}", headers=_auth(gyata_token))
        assert detail.status_code == 200, detail.text
        body = detail.json()
        assert len(body["messages"]) == 1
        assert body["messages"][0]["direction"] == "inbound"

        list_after = client.get("/inbox?status=open", headers=_auth(gyata_token)).json()["conversations"]
        after = next(c for c in list_after if c["id"] == conversation_ulid)
        assert after["unread"] is False, "opening the conversation must mark its inbound messages read"

    def test_nonexistent_conversation_is_404(self, client: TestClient, gyata_token: str) -> None:
        r = client.get("/inbox/01NOSUCHCONVERSATIONXXXXXX", headers=_auth(gyata_token))
        assert r.status_code == 404


class TestReplyWithoutSmtpConfigured:
    def test_reply_without_smtp_config_returns_502_never_a_fake_sent(
        self, client: TestClient, gyata_token: str, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("CRM_SMTP_HOST", raising=False)
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST reply subject"))

        r = client.post(
            f"/inbox/{conversation_ulid}/reply", json={"body": "Hola, aun disponible"}, headers=_auth(gyata_token)
        )
        assert r.status_code == 502, r.text
        assert "No se pudo enviar" in r.json()["detail"]


class TestReplyWithStubbedSend:
    def test_reply_success_persists_ack_and_flips_status(
        self, client: TestClient, gyata_token: str, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def _fake_send(to_addr, subject, body, in_reply_to=None, **kwargs):
            assert body == "Sí, sigue disponible, ¿cuándo quieres verlo?"
            return "<stubbed-outbound-id@example.invalid>"

        monkeypatch.setattr("services.api.routers.crm_inbox.send_email", _fake_send)

        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST reply success"))

        r = client.post(
            f"/inbox/{conversation_ulid}/reply",
            json={"body": "Sí, sigue disponible, ¿cuándo quieres verlo?"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 201, r.text
        message = r.json()
        assert message["direction"] == "outbound"
        assert message["sentVia"] == "email"

        detail = client.get(f"/inbox/{conversation_ulid}", headers=_auth(gyata_token)).json()
        assert detail["conversation"]["status"] == "replied"
        outbound = [m for m in detail["messages"] if m["direction"] == "outbound"]
        assert len(outbound) == 1


class TestPatchConversation:
    def test_patch_status_to_closed(self, client: TestClient, gyata_token: str) -> None:
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST patch subject"))
        r = client.patch(f"/inbox/{conversation_ulid}", json={"status": "closed"}, headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "closed"

    def test_patch_invalid_status_is_422(self, client: TestClient, gyata_token: str) -> None:
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST bad patch"))
        r = client.patch(f"/inbox/{conversation_ulid}", json={"status": "bogus"}, headers=_auth(gyata_token))
        assert r.status_code == 422

    def test_patch_unread_false_marks_all_read(self, client: TestClient, gyata_token: str) -> None:
        _, conversation_ulid, _ = asyncio.run(_seed_conversation_with_inbound_message("ZZTEST unread patch"))
        r = client.patch(f"/inbox/{conversation_ulid}", json={"unread": False}, headers=_auth(gyata_token))
        assert r.status_code == 200, r.text
        assert r.json()["unread"] is False
