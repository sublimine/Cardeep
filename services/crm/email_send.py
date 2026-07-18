"""services/crm/email_send.py — 06-unified-crm-chat F4: outbound email (SMTP).

Pure stdlib (``smtplib`` + ``email``) — zero new runtime dependency, matching the
project's "commoditized infra, don't reinvent, don't over-install" doctrine (carta §8).

Configuration (env vars; unset host = channel not configured, fails LOUD, never a
silent fake success — carta §7 "el check NO se pinta con solo el 200 del POST propio"):
    CRM_SMTP_HOST      SMTP server hostname (required to actually send)
    CRM_SMTP_PORT      default 587 (STARTTLS) — 465 is treated as implicit TLS (SMTP_SSL)
    CRM_SMTP_USER      auth username (optional — some relays are unauthenticated)
    CRM_SMTP_PASSWORD  auth password
    CRM_SMTP_USE_TLS   "1" (default) = STARTTLS on port 587; "0" = no TLS negotiation
    CRM_SMTP_FROM      the From: address (required)

Verification note (F4 gap, declared not masked): this module is genuinely capable of
sending real mail against any standard SMTP relay (Gmail app-password, SES SMTP,
Mailgun, a self-hosted Postfix, etc.) — but no live credentials exist in this
environment, so end-to-end delivery to a real receiving mailbox has NOT been exercised
here. ``tests/test_email_send.py`` verifies the module's own logic (message
construction, Message-ID generation, error propagation) against a local ``aiosmtpd``-free
stub SMTP transport — it does not prove real-world deliverability.
"""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid


class EmailSendError(Exception):
    """Raised whenever an email genuinely could not be sent — never swallowed."""


def _smtp_config() -> dict[str, str | int | bool | None]:
    return {
        "host": os.environ.get("CRM_SMTP_HOST"),
        "port": int(os.environ.get("CRM_SMTP_PORT", "587")),
        "user": os.environ.get("CRM_SMTP_USER"),
        "password": os.environ.get("CRM_SMTP_PASSWORD"),
        "use_tls": os.environ.get("CRM_SMTP_USE_TLS", "1") != "0",
        "from_addr": os.environ.get("CRM_SMTP_FROM"),
    }


def send_email(
    to_addr: str,
    subject: str,
    body: str,
    *,
    in_reply_to: str | None = None,
    smtp_client_factory: type[smtplib.SMTP] | None = None,
) -> str:
    """Send a plain-text email and return the Message-ID this module minted for it.

    Raises ``EmailSendError`` on ANY failure — missing configuration, connection
    refused, auth failure, recipient refused — so the caller (crm_inbox.py's
    ``/inbox/{id}/reply``) can surface a real failure instead of a fabricated
    "sent" state.

    ``smtp_client_factory`` is an injection seam for tests (defaults to
    ``smtplib.SMTP`` / ``smtplib.SMTP_SSL``, chosen by port).
    """
    cfg = _smtp_config()
    if not cfg["host"]:
        raise EmailSendError("CRM_SMTP_HOST is not configured — no channel to send through")
    if not cfg["from_addr"]:
        raise EmailSendError("CRM_SMTP_FROM is not configured")

    msg = EmailMessage()
    msg["From"] = cfg["from_addr"]
    msg["To"] = to_addr
    msg["Subject"] = subject
    message_id = make_msgid(domain=cfg["from_addr"].split("@")[-1] if "@" in str(cfg["from_addr"]) else None)
    msg["Message-ID"] = message_id
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    msg.set_content(body)

    port = int(cfg["port"])
    factory = smtp_client_factory
    try:
        if factory is not None:
            client = factory(cfg["host"], port, timeout=15)
        elif port == 465:
            client = smtplib.SMTP_SSL(cfg["host"], port, timeout=15)
        else:
            client = smtplib.SMTP(cfg["host"], port, timeout=15)

        with client as smtp:
            if port != 465 and cfg["use_tls"]:
                smtp.starttls()
            if cfg["user"]:
                smtp.login(str(cfg["user"]), str(cfg["password"] or ""))
            smtp.send_message(msg)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailSendError(str(exc)) from exc

    return message_id
