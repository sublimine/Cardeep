"""services/api/ics_vcard.py — 06-unified-crm-chat F6: RFC 5545 (.ics) / RFC 6350
(vCard) serialization.

Pure stdlib string building — no new runtime dependency (the same "commoditized
interop, don't reinvent, don't over-install" doctrine as services/crm/email_send.py).
Both formats mandate CRLF line endings and specific escaping rules; both are
implemented literally against their RFCs, not against a guess.

Independent verification (carta §7 "importación real del archivo en un cliente
externo... test con librería de parsing independiente"): ``requirements-dev.txt``
declares ``icalendar``/``vobject`` — parsers this module does NOT import — so
``tests/test_ics_vcard.py`` proves round-trip correctness via a codepath that shares
NO code with the generator below.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_CRLF = "\r\n"


def _escape_text(value: str) -> str:
    """RFC 5545 §3.3.11 / RFC 6350 §3.4 TEXT escaping — both specs agree on this set:
    backslash, comma, semicolon escaped with a backslash; newline becomes literal \\n."""
    return (
        value.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def _fold_line(line: str) -> str:
    """RFC 5545 §3.1 line folding: lines MUST NOT exceed 75 octets; continuation
    lines start with a single space. Simple char-count fold (ASCII-safe for this
    module's fields — the CRM does not currently accept non-Latin event titles)."""
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return _CRLF.join(parts)


def _dt_utc_stamp(dt: datetime) -> str:
    """RFC 5545 §3.3.5 DATE-TIME, UTC form: YYYYMMDDTHHMMSSZ."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_ics_event(
    *, uid: str, title: str, starts_at: datetime, ends_at: datetime | None,
    location: str | None = None, description: str | None = None,
) -> str:
    """One self-contained VCALENDAR/VEVENT .ics document for a single crm_event row."""
    now = datetime.now(timezone.utc)
    end = ends_at or (starts_at.replace() if ends_at else starts_at)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Cardeep//CRM//ES",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{uid}@cardeep.local",
        f"DTSTAMP:{_dt_utc_stamp(now)}",
        f"DTSTART:{_dt_utc_stamp(starts_at)}",
        f"DTEND:{_dt_utc_stamp(end)}",
        f"SUMMARY:{_escape_text(title)}",
    ]
    if location:
        lines.append(f"LOCATION:{_escape_text(location)}")
    if description:
        lines.append(f"DESCRIPTION:{_escape_text(description)}")
    lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return _CRLF.join(_fold_line(l) for l in lines) + _CRLF


def build_vcard(*, name: str, phone_e164: str | None, email: str | None) -> str:
    """One VCARD 3.0 document for a single crm_contact row (RFC 6350 is version-4,
    but 3.0 — RFC 2426 — has the widest real-world client compatibility for a
    minimal name/phone/email card; both share the escaping rules this module uses)."""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{_escape_text(name)}",
        f"N:{_escape_text(name)};;;;",
    ]
    if phone_e164:
        lines.append(f"TEL;TYPE=CELL:{_escape_text(phone_e164)}")
    if email:
        lines.append(f"EMAIL;TYPE=INTERNET:{_escape_text(email)}")
    lines.append("END:VCARD")
    return _CRLF.join(_fold_line(l) for l in lines) + _CRLF
