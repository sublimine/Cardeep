"""services/crm/email_ingest.py — 06-unified-crm-chat F4: IMAP lead ingestion worker.

Connects to a dealer's lead mailbox via IMAP, parses each UNSEEN message with
``services/crm/lead_parsers.py``, and creates/updates the matching
`crm_contact`/`crm_conversation`/`crm_message` rows — auto-creating a contact when the
sender is new (HubSpot criterion, carta §2). Idempotent by construction: a message is
identified by its RFC 5322 ``Message-ID`` (unique per `migrations/0084_crm.sql`'s
`crm_message.provider_message_id` index), so re-processing the same email twice (a
crashed run retried, or an already-seen message re-fetched) is a silent no-op, never a
duplicate conversation entry.

Scheduling decision (carta §5 declared hueco, resolved here): audited
``pipeline/ops/scheduler.py`` + ``pipeline/ops/registry.py`` before writing this worker.
That scheduler is purpose-built for the census harvest fleet — ``SourceEntry``/
``source_health``/circuit-breaker model, one subprocess per registered scraping
connector, single-producer discipline tied to harvest cadence. It is NOT a generic job
runner, and registering a mailbox poll against ``source_health`` would blur a domain
boundary that scheduler's own design deliberately enforces (scraper connectors vs.
product-feature workers). Decision: this is a STANDALONE script — run it directly
(`python -m services.crm.email_ingest`) for one pass, or `--loop` for continuous
polling — meant to be invoked by an OS-level scheduler (cron / Windows Task Scheduler)
or as its own long-lived process, the same pattern already used by
``scripts/seed_demo_dealer.py`` and other standalone scripts in this repo.

Configuration (env vars):
    CRM_IMAP_HOST         IMAP server hostname (required)
    CRM_IMAP_PORT         default 993 (IMAP over implicit TLS)
    CRM_IMAP_USER         mailbox username (required)
    CRM_IMAP_PASSWORD     mailbox password
    CRM_IMAP_MAILBOX      default "INBOX"
    CRM_IMAP_TENANT_CDP   the dealer (cdp_code) this mailbox belongs to (required) —
                          F4 v1 is single-mailbox-per-tenant; a shared multi-tenant
                          alias scheme is a scale concern deferred past this pilar.

Verification note (F4 gap, declared not masked): this worker is genuinely capable of
polling a real IMAP mailbox — but no live mailbox credentials exist in this environment,
so a true end-to-end round-trip (real email -> real IMAP server -> this worker -> DB)
has NOT been exercised here. ``tests/test_email_ingest.py`` verifies the ingestion LOGIC
(contact/conversation/message creation, idempotent re-ingestion, portal parser dispatch)
against a stub IMAP connection and constructed `.eml`-shaped fixtures — it does not prove
connectivity to a real mail server.
"""
from __future__ import annotations

import argparse
import asyncio
import email
import email.utils
import imaplib
import logging
import os
import time
from email.header import decode_header
from email.message import Message

import asyncpg

from pipeline.identity.phone import normalize_e164
from pipeline.ids import ulid
from services.crm.lead_parsers import parse_lead

logger = logging.getLogger(__name__)

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


def _imap_config() -> dict[str, str | int | None]:
    return {
        "host": os.environ.get("CRM_IMAP_HOST"),
        "port": int(os.environ.get("CRM_IMAP_PORT", "993")),
        "user": os.environ.get("CRM_IMAP_USER"),
        "password": os.environ.get("CRM_IMAP_PASSWORD"),
        "mailbox": os.environ.get("CRM_IMAP_MAILBOX", "INBOX"),
        "tenant_cdp": os.environ.get("CRM_IMAP_TENANT_CDP"),
    }


def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out: list[str] = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def extract_body(msg: Message) -> str:
    """Prefer text/plain; fall back to a stripped text/html; never raise."""
    from services.crm.lead_parsers import strip_html

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get_filename():
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    return strip_html(html)
        return ""
    payload = msg.get_payload(decode=True)
    if payload is None:
        return str(msg.get_payload())
    return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")


async def ingest_message(
    conn: asyncpg.Connection, entity_ulid: str, *,
    from_address: str, from_name: str, subject: str, body: str, message_id: str,
) -> bool:
    """Create/update contact+conversation+message for one parsed email.

    Returns True if a NEW message row was inserted, False on an idempotent dedup
    no-op (the Message-ID was already ingested — safe to mark \\Seen either way).
    """
    parsed = parse_lead(subject, body, from_address, from_name)

    phone_e164 = normalize_e164(parsed.contact_phone) if parsed.contact_phone else None
    email_lower = (parsed.contact_email or from_address or "").strip().lower() or None

    contact_row = None
    if email_lower:
        contact_row = await conn.fetchrow(
            "SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND email_lower = $2",
            entity_ulid, email_lower,
        )
    if contact_row is None and phone_e164:
        contact_row = await conn.fetchrow(
            "SELECT contact_ulid FROM crm_contact WHERE entity_ulid = $1 AND phone_e164 = $2",
            entity_ulid, phone_e164,
        )

    if contact_row is None:
        contact_ulid = ulid()
        await conn.execute(
            """
            INSERT INTO crm_contact (contact_ulid, entity_ulid, name, email, phone_raw, phone_e164)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            contact_ulid, entity_ulid, parsed.contact_name or from_name or "Lead sin nombre",
            email_lower, parsed.contact_phone, phone_e164,
        )
    else:
        contact_ulid = contact_row["contact_ulid"]

    # Reuse the most recent non-closed email conversation for this contact; else open one.
    conv_row = await conn.fetchrow(
        """
        SELECT conversation_ulid FROM crm_conversation
         WHERE entity_ulid = $1 AND contact_ulid = $2 AND channel = 'email' AND status != 'closed'
         ORDER BY created_at DESC LIMIT 1
        """,
        entity_ulid, contact_ulid,
    )
    if conv_row is None:
        conversation_ulid = ulid()
        await conn.execute(
            """
            INSERT INTO crm_conversation (conversation_ulid, entity_ulid, contact_ulid, channel,
                                           source_platform, subject, status, last_inbound_at, last_message_at)
            VALUES ($1, $2, $3, 'email', $4, $5, 'open', now(), now())
            """,
            conversation_ulid, entity_ulid, contact_ulid, parsed.source_platform, subject,
        )
    else:
        conversation_ulid = conv_row["conversation_ulid"]
        await conn.execute(
            """
            UPDATE crm_conversation SET status = 'open', last_inbound_at = now(), last_message_at = now()
             WHERE conversation_ulid = $1
            """,
            conversation_ulid,
        )

    try:
        await conn.execute(
            """
            INSERT INTO crm_message (message_ulid, conversation_ulid, direction, sender_name, sender_email,
                                      body, sent_via, provider_message_id, provider_ack_at)
            VALUES ($1, $2, 'inbound', $3, $4, $5, 'email', $6, now())
            """,
            ulid(), conversation_ulid, from_name or None, from_address or None, parsed.message_body, message_id,
        )
    except asyncpg.UniqueViolationError:
        return False
    return True


async def run_once() -> int:
    """One IMAP poll cycle: fetch UNSEEN, ingest, mark \\Seen. Returns count ingested."""
    cfg = _imap_config()
    missing = [k for k in ("host", "user", "tenant_cdp") if not cfg[k]]
    if missing:
        raise RuntimeError(f"CRM_IMAP_{'/'.join(m.upper() for m in missing)} not configured")

    conn = await asyncpg.connect(DSN)
    try:
        entity_row = await conn.fetchrow("SELECT entity_ulid FROM entity WHERE cdp_code = $1", cfg["tenant_cdp"])
        if entity_row is None:
            raise RuntimeError(f"tenant {cfg['tenant_cdp']} not found in the census")
        entity_ulid = entity_row["entity_ulid"]

        imap = imaplib.IMAP4_SSL(str(cfg["host"]), int(cfg["port"]))
        ingested = 0
        try:
            imap.login(str(cfg["user"]), str(cfg["password"] or ""))
            imap.select(str(cfg["mailbox"]))
            status, data = imap.search(None, "UNSEEN")
            if status != "OK":
                raise RuntimeError(f"IMAP SEARCH failed: {status}")
            for msg_num in data[0].split():
                status, msg_data = imap.fetch(msg_num, "(RFC822)")
                if status != "OK" or not msg_data or msg_data[0] is None:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                from_header = _decode_header_value(msg.get("From"))
                from_name, from_address = email.utils.parseaddr(from_header)
                subject = _decode_header_value(msg.get("Subject"))
                message_id = msg.get("Message-ID") or f"<generated-{ulid()}@cardeep.local>"
                body = extract_body(msg)

                is_new = await ingest_message(
                    conn, entity_ulid,
                    from_address=from_address, from_name=from_name, subject=subject,
                    body=body, message_id=message_id,
                )
                if is_new:
                    ingested += 1
                imap.store(msg_num, "+FLAGS", "\\Seen")
            return ingested
        finally:
            try:
                imap.close()
            except imaplib.IMAP4.error:
                pass
            imap.logout()
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="CRM email lead ingestion worker (06-unified-crm-chat F4)")
    parser.add_argument("--loop", action="store_true", help="poll continuously instead of a single pass")
    parser.add_argument("--interval-seconds", type=int, default=120)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if not args.loop:
        n = asyncio.run(run_once())
        logger.info("ingested %d new lead message(s)", n)
        return

    while True:
        try:
            n = asyncio.run(run_once())
            logger.info("ingested %d new lead message(s)", n)
        except Exception:
            logger.exception("email ingest cycle failed — isolated, next cycle will retry")
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
