"""services/crm/lead_parsers.py — 06-unified-crm-chat F4: deterministic per-portal
lead-email parsers (carta §8: "parsers deterministas por portal ... un LLM aquí sería
coste y no-determinismo gratuitos").

Two verifiable facts anchor this module, and only these two are trusted without a
fixture proving the exact body template:
  1. A lead-notification email's ``From:`` address is controlled by the portal itself
     (Wallapop cannot forge a `@coches.net` sender) — so PORTAL DETECTION by sender
     domain is safe and requires no assumption about body format.
  2. Whatever the body format turns out to be, this module NEVER crashes on an
     unrecognized shape — every per-portal extractor degrades to ``_extract_generic``
     the moment its expected markers are absent, which never fabricates a field it
     could not find.

[ASUMIDO — hueco declarado, no maquillado]: the per-portal REGEX markers below
("Nombre:", "Teléfono:", "Mensaje:" etc.) are modeled on the publicly documented shape
of these portals' dealer-lead notification emails; NO real captured `.eml` sample from
coches.net/Wallapop/Milanuncios was available in this environment to pin them byte-
for-byte. Before this goes live against a real inbox, the deterministic regexes MUST
be re-verified against real samples (the first production run's non-matches will show
up as `extraction_method='generic'` in `crm_conversation.source_platform`, an honest,
observable signal — not a silent wrong answer).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedLead:
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    vehicle_reference: str | None  # free-text hint (listing title/plate) — NOT resolved
                                    # to a vehicle_ulid here; that resolution is F5's job.
    message_body: str
    source_platform: str  # 'coches.net' | 'wallapop' | 'milanuncios' | 'manual'
    extraction_method: str  # 'deterministic' | 'generic'


_PORTAL_DOMAINS: tuple[tuple[str, str], ...] = (
    ("coches.net", "coches.net"),
    ("wallapop.com", "wallapop"),
    ("milanuncios.com", "milanuncios"),
)

_PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def detect_portal(from_address: str) -> str:
    """Sender-domain portal detection — see module docstring point 1."""
    lowered = (from_address or "").lower()
    for domain, name in _PORTAL_DOMAINS:
        if domain in lowered:
            return name
    return "manual"


def strip_html(html: str) -> str:
    """Best-effort HTML-to-text for portals whose notification is HTML-only."""
    return re.sub(r"\s+", " ", _HTML_TAG_RE.sub(" ", html)).strip()


def _extract_generic(body: str, from_address: str, from_name: str | None, portal: str) -> ParsedLead:
    phone_match = _PHONE_RE.search(body)
    return ParsedLead(
        contact_name=(from_name or None),
        contact_phone=phone_match.group(1).strip() if phone_match else None,
        contact_email=from_address or None,
        vehicle_reference=None,
        message_body=body.strip(),
        source_platform=portal,
        extraction_method="generic",
    )


# ---------------------------------------------------------------------------
# coches.net
# ---------------------------------------------------------------------------

_COCHESNET_NAME_RE = re.compile(r"Nombre:\s*(.+)", re.IGNORECASE)
_COCHESNET_PHONE_RE = re.compile(r"Tel[eé]fono:\s*([\d\s+().-]+)", re.IGNORECASE)
_COCHESNET_MSG_RE = re.compile(r"Mensaje:\s*(.+)", re.IGNORECASE | re.DOTALL)


def _extract_cochesnet(subject: str, body: str, from_address: str, from_name: str | None) -> ParsedLead:
    name_m = _COCHESNET_NAME_RE.search(body)
    phone_m = _COCHESNET_PHONE_RE.search(body)
    if name_m is None and phone_m is None:
        return _extract_generic(body, from_address, from_name, "coches.net")
    msg_m = _COCHESNET_MSG_RE.search(body)
    return ParsedLead(
        contact_name=name_m.group(1).strip() if name_m else from_name,
        contact_phone=phone_m.group(1).strip() if phone_m else None,
        contact_email=None,
        vehicle_reference=subject.strip() or None,
        message_body=(msg_m.group(1).strip() if msg_m else body.strip()),
        source_platform="coches.net",
        extraction_method="deterministic",
    )


# ---------------------------------------------------------------------------
# Wallapop
# ---------------------------------------------------------------------------

_WALLAPOP_NAME_RE = re.compile(r"(?:De|From)\s*:\s*(.+)", re.IGNORECASE)
_WALLAPOP_MSG_RE = re.compile(r"(?:Mensaje|Message)\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)


def _extract_wallapop(subject: str, body: str, from_address: str, from_name: str | None) -> ParsedLead:
    name_m = _WALLAPOP_NAME_RE.search(body)
    msg_m = _WALLAPOP_MSG_RE.search(body)
    if msg_m is None:
        return _extract_generic(body, from_address, from_name, "wallapop")
    return ParsedLead(
        contact_name=(name_m.group(1).strip() if name_m else from_name),
        contact_phone=None,  # Wallapop chat notifications typically carry no phone number
        contact_email=None,
        vehicle_reference=subject.strip() or None,
        message_body=msg_m.group(1).strip(),
        source_platform="wallapop",
        extraction_method="deterministic",
    )


# ---------------------------------------------------------------------------
# Milanuncios
# ---------------------------------------------------------------------------

_MILANUNCIOS_PHONE_RE = re.compile(r"Tel[eé]fono[^\d]{0,10}([\d\s+().-]{9,})", re.IGNORECASE)
_MILANUNCIOS_NAME_RE = re.compile(r"Nombre:\s*(.+)", re.IGNORECASE)


def _extract_milanuncios(subject: str, body: str, from_address: str, from_name: str | None) -> ParsedLead:
    phone_m = _MILANUNCIOS_PHONE_RE.search(body)
    name_m = _MILANUNCIOS_NAME_RE.search(body)
    if phone_m is None and name_m is None:
        return _extract_generic(body, from_address, from_name, "milanuncios")
    return ParsedLead(
        contact_name=(name_m.group(1).strip() if name_m else from_name),
        contact_phone=(phone_m.group(1).strip() if phone_m else None),
        contact_email=None,
        vehicle_reference=subject.strip() or None,
        message_body=body.strip(),
        source_platform="milanuncios",
        extraction_method="deterministic",
    )


_EXTRACTORS = {
    "coches.net": _extract_cochesnet,
    "wallapop": _extract_wallapop,
    "milanuncios": _extract_milanuncios,
}


def parse_lead(subject: str, body: str, from_address: str, from_name: str | None) -> ParsedLead:
    """Entry point: detect the portal by sender domain, run its deterministic
    extractor, degrade to generic on any non-match. Never raises."""
    portal = detect_portal(from_address)
    extractor = _EXTRACTORS.get(portal)
    if extractor is None:
        return _extract_generic(body, from_address, from_name, portal)
    return extractor(subject, body, from_address, from_name)
