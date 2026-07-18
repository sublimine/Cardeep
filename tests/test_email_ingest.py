"""Tests for services/crm/email_ingest.py (06-unified-crm-chat F4).

Two layers, matching the module's own honesty boundary:
  1. ``ingest_message()`` business logic against the LIVE cardeep-pg (contact
     auto-creation/dedup, conversation reuse, idempotent Message-ID re-ingestion) —
     same auto-skip pattern as tests/test_crm_schema.py.
  2. ``run_once()`` IMAP orchestration against a MOCKED ``imaplib.IMAP4_SSL`` (no real
     server) — proves the protocol wiring (login/select/search/fetch/store) is correct,
     NOT that a real mailbox round-trips (that gap is declared in the module docstring).
"""
from __future__ import annotations

import asyncio
import email.message
import uuid
from unittest import mock

import asyncpg
import pytest

from pipeline.ids import ulid
from services.crm import email_ingest

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
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


@pytest.fixture(scope="module")
def entity_ulid() -> str:
    async def _get() -> str:
        conn = await asyncpg.connect(DSN)
        try:
            row = await conn.fetchrow("SELECT entity_ulid FROM entity WHERE cdp_code = $1", GYATA_CDP)
            assert row is not None
            return row["entity_ulid"]
        finally:
            await conn.close()

    return asyncio.run(_get())


@pytest.fixture(autouse=True, scope="module")
def _purge_after(entity_ulid: str):
    yield

    async def _purge() -> None:
        conn = await asyncpg.connect(DSN)
        try:
            await conn.execute(
                "DELETE FROM crm_conversation WHERE entity_ulid = $1 AND contact_ulid IN "
                "(SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND name LIKE 'ZZTEST_%')",
                entity_ulid,
            )
            await conn.execute(
                "DELETE FROM crm_contact WHERE entity_ulid = $1 AND name LIKE 'ZZTEST_%'"
                " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_consent)"
                " AND contact_ulid NOT IN (SELECT contact_ulid FROM crm_deal)",
                entity_ulid,
            )
        finally:
            await conn.close()

    asyncio.run(_purge())


class TestIngestMessage:
    def test_new_sender_creates_contact_and_conversation(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                is_new = await email_ingest.ingest_message(
                    conn, entity_ulid,
                    from_address="zztest.lead1@example.invalid", from_name="ZZTEST_Lead1",
                    subject="Consulta BMW", body="Nombre: ZZTEST_Lead1\nTeléfono: 611222333\nMensaje: hola",
                    message_id="<zztest-msg-1@example.invalid>",
                )
                assert is_new is True

                contact = await conn.fetchrow(
                    "SELECT * FROM crm_contact WHERE entity_ulid = $1 AND email_lower = $2",
                    entity_ulid, "zztest.lead1@example.invalid",
                )
                assert contact is not None
                assert contact["phone_e164"] == "+34611222333"

                conv = await conn.fetchrow(
                    "SELECT * FROM crm_conversation WHERE contact_ulid = $1", contact["contact_ulid"]
                )
                assert conv is not None
                assert conv["channel"] == "email"
                assert conv["status"] == "open"

                msg = await conn.fetchrow(
                    "SELECT * FROM crm_message WHERE provider_message_id = $1", "<zztest-msg-1@example.invalid>"
                )
                assert msg is not None
                assert msg["direction"] == "inbound"
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_second_email_same_sender_reuses_contact_and_conversation(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                await email_ingest.ingest_message(
                    conn, entity_ulid,
                    from_address="zztest.lead2@example.invalid", from_name="ZZTEST_Lead2",
                    subject="Consulta", body="primer mensaje",
                    message_id="<zztest-msg-2a@example.invalid>",
                )
                is_new = await email_ingest.ingest_message(
                    conn, entity_ulid,
                    from_address="zztest.lead2@example.invalid", from_name="ZZTEST_Lead2",
                    subject="Consulta", body="segundo mensaje",
                    message_id="<zztest-msg-2b@example.invalid>",
                )
                assert is_new is True

                contacts = await conn.fetch(
                    "SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND email_lower = $2",
                    entity_ulid, "zztest.lead2@example.invalid",
                )
                assert len(contacts) == 1, "second email from the same sender must NOT create a duplicate contact"

                convs = await conn.fetch(
                    "SELECT conversation_ulid FROM crm_conversation WHERE contact_ulid = $1",
                    contacts[0]["contact_ulid"],
                )
                assert len(convs) == 1, "second email must reuse the existing open conversation, not fork a new one"
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_duplicate_message_id_is_idempotent_noop(self, entity_ulid: str) -> None:
        async def _run() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                first = await email_ingest.ingest_message(
                    conn, entity_ulid,
                    from_address="zztest.lead3@example.invalid", from_name="ZZTEST_Lead3",
                    subject="Consulta", body="mensaje original",
                    message_id="<zztest-msg-3-dup@example.invalid>",
                )
                assert first is True

                second = await email_ingest.ingest_message(
                    conn, entity_ulid,
                    from_address="zztest.lead3@example.invalid", from_name="ZZTEST_Lead3",
                    subject="Consulta", body="mensaje original",
                    message_id="<zztest-msg-3-dup@example.invalid>",
                )
                assert second is False, "re-ingesting the same Message-ID must be a silent no-op"

                count = await conn.fetchval(
                    "SELECT count(*) FROM crm_message WHERE provider_message_id = $1",
                    "<zztest-msg-3-dup@example.invalid>",
                )
                assert count == 1
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# run_once() orchestration against a mocked IMAP4_SSL — proves the protocol
# wiring without a real mailbox (declared gap, module docstring).
# ---------------------------------------------------------------------------

def _make_raw_email(from_addr: str, subject: str, body: str, message_id: str) -> bytes:
    msg = email.message.EmailMessage()
    msg["From"] = from_addr
    msg["To"] = "leads@dealer.example"
    msg["Subject"] = subject
    msg["Message-ID"] = message_id
    msg.set_content(body)
    return msg.as_bytes()


class TestRunOnceOrchestration:
    def test_run_once_requires_configuration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CRM_IMAP_HOST", raising=False)
        monkeypatch.delenv("CRM_IMAP_USER", raising=False)
        monkeypatch.delenv("CRM_IMAP_TENANT_CDP", raising=False)
        with pytest.raises(RuntimeError, match="CRM_IMAP"):
            asyncio.run(email_ingest.run_once())

    def test_run_once_fetches_unseen_ingests_and_marks_seen(
        self, monkeypatch: pytest.MonkeyPatch, entity_ulid: str,
    ) -> None:
        monkeypatch.setenv("CRM_IMAP_HOST", "imap.example.invalid")
        monkeypatch.setenv("CRM_IMAP_USER", "leads@dealer.example")
        monkeypatch.setenv("CRM_IMAP_PASSWORD", "s3cret")
        monkeypatch.setenv("CRM_IMAP_TENANT_CDP", GYATA_CDP)

        # Unique per test run — a fixed Message-ID would collide with a prior run's row
        # (crm_message.provider_message_id is globally unique by design, so a repeat run
        # correctly reports it as an idempotent no-op rather than re-ingesting it; the test
        # itself must generate fresh data each time, exactly like every other test in this
        # module already does via uuid.uuid4()).
        unique = uuid.uuid4().hex[:10]
        from_address = f"zztest.imaplead.{unique}@example.invalid"
        message_id = f"<zztest-imap-{unique}@example.invalid>"
        raw = _make_raw_email(
            from_address, "Consulta coche", f"Nombre: ZZTEST_ImapLead_{unique}\nMensaje: hola",
            message_id,
        )

        fake_imap = mock.MagicMock()
        fake_imap.login.return_value = ("OK", [b"logged in"])
        fake_imap.select.return_value = ("OK", [b"1"])
        fake_imap.search.return_value = ("OK", [b"1"])
        fake_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {123}", raw)])
        fake_imap.store.return_value = ("OK", [b""])
        fake_imap.close.return_value = ("OK", [b""])
        fake_imap.logout.return_value = ("OK", [b""])

        with mock.patch("imaplib.IMAP4_SSL", return_value=fake_imap) as ctor:
            count = asyncio.run(email_ingest.run_once())

        ctor.assert_called_once_with("imap.example.invalid", 993)
        fake_imap.login.assert_called_once_with("leads@dealer.example", "s3cret")
        fake_imap.select.assert_called_once()
        fake_imap.search.assert_called_once_with(None, "UNSEEN")
        fake_imap.fetch.assert_called_once()
        fake_imap.store.assert_called_once_with(b"1", "+FLAGS", "\\Seen")
        assert count == 1

        async def _verify() -> None:
            conn = await asyncpg.connect(DSN)
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM crm_message WHERE provider_message_id = $1", message_id
                )
                assert row is not None
            finally:
                await conn.close()

        asyncio.run(_verify())
