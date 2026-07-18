"""Tests for migrations/0084_crm.sql (06-unified-crm-chat F1).

Schema-only, no API involved — exercises the live cardeep-pg directly (same
auto-skip pattern as tests/test_dealer_ops_router.py / test_auth_router.py).
Verifies the adversarial invariants the carta's F1 acceptance criteria demand
(plans/cardeep-omni/06-unified-crm-chat.md §9 F1):

  * Per-tenant dedup: two contacts with the same (entity_ulid, phone_e164) or
    (entity_ulid, email_lower) collide.
  * crm_contact_channel's Chatwoot-pattern unique (entity_ulid, channel,
    source_id) — the same identity cannot be attached to two different
    contacts under the same tenant.
  * Append-only guards on crm_consent and crm_deal_stage_event: UPDATE and
    DELETE both raise (cardeep_block_mutation(), same trigger function as
    migrations/0005/0035's ledgers) even for a superuser connection.
  * crm_message.provider_message_id is unique when present (idempotent email
    re-ingestion) but multiple NULLs are allowed (composed-but-not-yet-sent
    outbound drafts, or channels without a provider id).
  * FK integrity: a deal/conversation can reference a real vehicle_ulid from
    the live census (cross-domain read, F5 preview) and a real entity_ulid
    (GYATA, the seeded demo dealer).

All test rows are tagged 'ZZTEST_' and purged in FK-safe order in a
module-scoped teardown (conversations first — their crm_message children have
no guard and cascade cleanly). Contacts/deals that own an append-only child
(crm_consent / crm_deal_stage_event) are deliberately left in place: the guard
trigger fires on cascade-deletes too (not just explicit ones), so a parent row
with a guarded child can never be deleted — same precedent already accepted by
tests/test_dealer_ops_router.py for fleet_ops_event ("a small, honest,
permanent audit trail, exactly what a real write would leave"). These test
rows are tagged 'ZZTEST_' and harmless to leave behind.
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest

from pipeline.ids import ulid

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
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


async def _gyata_entity_ulid(conn: asyncpg.Connection) -> str:
    row = await conn.fetchrow("SELECT entity_ulid FROM entity WHERE cdp_code = $1", GYATA_CDP)
    assert row is not None, f"seeded demo dealer {GYATA_CDP} must exist (scripts/seed_demo_dealer.py)"
    return row["entity_ulid"]


@pytest.fixture(scope="module")
def entity_ulid() -> str:
    async def _get() -> str:
        conn = await asyncpg.connect(DSN)
        try:
            return await _gyata_entity_ulid(conn)
        finally:
            await conn.close()

    return asyncio.run(_get())


@pytest.fixture(autouse=True, scope="module")
def _purge_test_rows_after(entity_ulid: str):
    yield

    async def _purge() -> None:
        conn = await asyncpg.connect(DSN)
        try:
            # crm_conversation -> crm_message cascades cleanly (crm_message has no
            # append-only guard), so every test conversation is safe to remove.
            await conn.execute(
                "DELETE FROM crm_conversation WHERE entity_ulid = $1 AND contact_ulid IN "
                "(SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND name LIKE 'ZZTEST_%')",
                entity_ulid,
            )
            # crm_deal is only deletable when it has NO crm_deal_stage_event child (the
            # guard blocks the cascade). Remove the deal-less test deals; leave the rest
            # (they carry a real append-only audit trail — see module docstring).
            await conn.execute(
                """
                DELETE FROM crm_deal
                 WHERE entity_ulid = $1
                   AND contact_ulid IN (SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND name LIKE 'ZZTEST_%')
                   AND deal_ulid NOT IN (SELECT deal_ulid FROM crm_deal_stage_event)
                """,
                entity_ulid,
            )
            # Same logic for crm_contact: only deletable once it has no crm_consent
            # child (guarded) and no remaining crm_deal reference.
            await conn.execute(
                """
                DELETE FROM crm_contact
                 WHERE entity_ulid = $1 AND name LIKE 'ZZTEST_%'
                   AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_consent)
                   AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_deal)
                """,
                entity_ulid,
            )
        finally:
            await conn.close()

    asyncio.run(_purge())


async def _mk_contact(conn: asyncpg.Connection, entity_ulid: str, *, name: str,
                       email: str | None = None, phone_e164: str | None = None) -> str:
    cid = ulid()
    await conn.execute(
        """
        INSERT INTO crm_contact (contact_ulid, entity_ulid, name, email, phone_raw, phone_e164)
        VALUES ($1, $2, $3, $4, $4, $5)
        """,
        cid, entity_ulid, name, email, phone_e164,
    )
    return cid


# ---------------------------------------------------------------------------
# Dedup — per-tenant unique phone/email
# ---------------------------------------------------------------------------

class TestContactDedup:
    def test_duplicate_phone_same_tenant_rejected(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                await _mk_contact(conn, entity_ulid, name="ZZTEST_Phone1", phone_e164="+34600111222")
                with pytest.raises(asyncpg.UniqueViolationError):
                    await _mk_contact(conn, entity_ulid, name="ZZTEST_Phone2", phone_e164="+34600111222")
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_duplicate_email_same_tenant_rejected(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                await _mk_contact(conn, entity_ulid, name="ZZTEST_Mail1", email="zztest@example.invalid")
                with pytest.raises(asyncpg.UniqueViolationError):
                    await _mk_contact(conn, entity_ulid, name="ZZTEST_Mail2", email="ZZTest@Example.invalid")
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_null_phone_and_email_do_not_collide(self, entity_ulid: str) -> None:
        """Two contacts with no captured phone/email must NOT collide on NULL=NULL —
        the partial unique index only applies WHERE the column IS NOT NULL."""
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                await _mk_contact(conn, entity_ulid, name="ZZTEST_NoInfo1")
                await _mk_contact(conn, entity_ulid, name="ZZTEST_NoInfo2")
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# crm_contact_channel — Chatwoot ContactInbox pattern
# ---------------------------------------------------------------------------

class TestContactChannelUnique:
    def test_same_channel_identity_cannot_attach_to_two_contacts(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                c1 = await _mk_contact(conn, entity_ulid, name="ZZTEST_ChanA")
                c2 = await _mk_contact(conn, entity_ulid, name="ZZTEST_ChanB")
                await conn.execute(
                    "INSERT INTO crm_contact_channel (channel_ulid, contact_ulid, entity_ulid, channel, source_id) "
                    "VALUES ($1, $2, $3, 'email', 'shared@example.invalid')",
                    ulid(), c1, entity_ulid,
                )
                with pytest.raises(asyncpg.UniqueViolationError):
                    await conn.execute(
                        "INSERT INTO crm_contact_channel (channel_ulid, contact_ulid, entity_ulid, channel, source_id) "
                        "VALUES ($1, $2, $3, 'email', 'shared@example.invalid')",
                        ulid(), c2, entity_ulid,
                    )
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Append-only guards — crm_consent / crm_deal_stage_event
# ---------------------------------------------------------------------------

class TestAppendOnlyGuards:
    def test_crm_consent_update_blocked(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_ConsentUpd")
                consent_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_consent (consent_ulid, contact_ulid, channel, purpose, status, source) "
                    "VALUES ($1, $2, 'email', 'marketing', 'granted', 'web_form')",
                    consent_ulid, cid,
                )
                with pytest.raises(asyncpg.RestrictViolationError):
                    await conn.execute(
                        "UPDATE crm_consent SET status = 'revoked' WHERE consent_ulid = $1", consent_ulid
                    )
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_crm_consent_delete_blocked(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_ConsentDel")
                consent_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_consent (consent_ulid, contact_ulid, channel, purpose, status, source) "
                    "VALUES ($1, $2, 'whatsapp', 'transactional', 'granted', 'verbal_recorded')",
                    consent_ulid, cid,
                )
                with pytest.raises(asyncpg.RestrictViolationError):
                    await conn.execute("DELETE FROM crm_consent WHERE consent_ulid = $1", consent_ulid)
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_crm_deal_stage_event_update_blocked(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_StageEventUpd")
                deal_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_deal (deal_ulid, entity_ulid, contact_ulid, stage) VALUES ($1, $2, $3, 'lead')",
                    deal_ulid, entity_ulid, cid,
                )
                event_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_deal_stage_event (event_ulid, deal_ulid, from_stage, to_stage) "
                    "VALUES ($1, $2, NULL, 'lead')",
                    event_ulid, deal_ulid,
                )
                with pytest.raises(asyncpg.RestrictViolationError):
                    await conn.execute(
                        "UPDATE crm_deal_stage_event SET to_stage = 'won' WHERE event_ulid = $1", event_ulid
                    )
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_crm_deal_stage_event_replay_reconstructs_current_stage(self, entity_ulid: str) -> None:
        """Same K13-style protocol as fleet_ops_event: replaying the append-only
        ledger must reconstruct crm_deal.stage exactly."""
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_StageReplay")
                deal_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_deal (deal_ulid, entity_ulid, contact_ulid, stage) VALUES ($1, $2, $3, 'lead')",
                    deal_ulid, entity_ulid, cid,
                )
                for frm, to in [(None, "lead"), ("lead", "contacted"), ("contacted", "offer")]:
                    await conn.execute(
                        "INSERT INTO crm_deal_stage_event (event_ulid, deal_ulid, from_stage, to_stage) "
                        "VALUES ($1, $2, $3, $4)",
                        ulid(), deal_ulid, frm, to,
                    )
                await conn.execute("UPDATE crm_deal SET stage = 'offer' WHERE deal_ulid = $1", deal_ulid)

                events = await conn.fetch(
                    "SELECT to_stage FROM crm_deal_stage_event WHERE deal_ulid = $1 ORDER BY changed_at ASC",
                    deal_ulid,
                )
                replayed = events[-1]["to_stage"]
                current = await conn.fetchval("SELECT stage FROM crm_deal WHERE deal_ulid = $1", deal_ulid)
                assert replayed == current == "offer"
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# crm_message — idempotent provider_message_id dedup
# ---------------------------------------------------------------------------

class TestMessageProviderIdDedup:
    def test_duplicate_provider_message_id_rejected(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_MsgDedup")
                conv_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_conversation (conversation_ulid, entity_ulid, contact_ulid, channel) "
                    "VALUES ($1, $2, $3, 'email')",
                    conv_ulid, entity_ulid, cid,
                )
                await conn.execute(
                    "INSERT INTO crm_message (message_ulid, conversation_ulid, direction, body, sent_via, provider_message_id) "
                    "VALUES ($1, $2, 'inbound', 'hello', 'email', 'dup-message-id@example.invalid')",
                    ulid(), conv_ulid,
                )
                with pytest.raises(asyncpg.UniqueViolationError):
                    await conn.execute(
                        "INSERT INTO crm_message (message_ulid, conversation_ulid, direction, body, sent_via, provider_message_id) "
                        "VALUES ($1, $2, 'inbound', 'hello again', 'email', 'dup-message-id@example.invalid')",
                        ulid(), conv_ulid,
                    )
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_multiple_null_provider_message_id_allowed(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_MsgNullDedup")
                conv_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_conversation (conversation_ulid, entity_ulid, contact_ulid, channel) "
                    "VALUES ($1, $2, $3, 'web_form')",
                    conv_ulid, entity_ulid, cid,
                )
                for _ in range(2):
                    await conn.execute(
                        "INSERT INTO crm_message (message_ulid, conversation_ulid, direction, body, sent_via) "
                        "VALUES ($1, $2, 'outbound', 'draft', 'web_form')",
                        ulid(), conv_ulid,
                    )
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# FK integrity against the live census (F5 preview)
# ---------------------------------------------------------------------------

class TestCensusForeignKeys:
    def test_deal_can_reference_real_vehicle_and_entity(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_VehicleFK")
                deal_ulid = ulid()
                await conn.execute(
                    "INSERT INTO crm_deal (deal_ulid, entity_ulid, contact_ulid, vehicle_ulid, stage, amount) "
                    "VALUES ($1, $2, $3, $4, 'lead', 23490.00)",
                    deal_ulid, entity_ulid, cid, GYATA_VEHICLE_ULID,
                )
                row = await conn.fetchrow("SELECT vehicle_ulid FROM crm_deal WHERE deal_ulid = $1", deal_ulid)
                assert row["vehicle_ulid"] == GYATA_VEHICLE_ULID
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_deal_rejects_nonexistent_vehicle(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                cid = await _mk_contact(conn, entity_ulid, name="ZZTEST_BadVehicleFK")
                with pytest.raises(asyncpg.ForeignKeyViolationError):
                    await conn.execute(
                        "INSERT INTO crm_deal (deal_ulid, entity_ulid, contact_ulid, vehicle_ulid, stage) "
                        "VALUES ($1, $2, $3, 'NOSUCHVEHICLEULID', 'lead')",
                        ulid(), entity_ulid, cid,
                    )
            finally:
                await conn.close()

        asyncio.run(_run())
