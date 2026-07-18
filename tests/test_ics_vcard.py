"""Tests for services/api/ics_vcard.py (06-unified-crm-chat F6).

Carta §7 protocol: "importación real del archivo en un cliente externo... test con
librería de parsing independiente (icalendar/vobject en CI)". These tests parse
``build_ics_event``/``build_vcard``'s output with the THIRD-PARTY libraries
(``icalendar``, ``vobject``) — code this module never imports — so a passing test
proves the generator produces spec-valid output, not merely output this module's own
code can read back.
"""
from __future__ import annotations

from datetime import datetime, timezone

import icalendar
import vobject

from services.api.ics_vcard import build_ics_event, build_vcard


class TestIcsEvent:
    def test_independent_icalendar_library_parses_it(self) -> None:
        starts = datetime(2026, 8, 15, 17, 0, tzinfo=timezone.utc)
        ends = datetime(2026, 8, 15, 18, 0, tzinfo=timezone.utc)
        ics_text = build_ics_event(
            uid="01TESTEVENTULID", title="Visita de Juan · BMW 320d", starts_at=starts, ends_at=ends,
            location="Concesionario GYATA",
        )

        cal = icalendar.Calendar.from_ical(ics_text)
        events = [c for c in cal.walk() if c.name == "VEVENT"]
        assert len(events) == 1
        event = events[0]
        assert str(event["UID"]).startswith("01TESTEVENTULID")
        assert str(event["SUMMARY"]) == "Visita de Juan · BMW 320d"
        assert str(event["LOCATION"]) == "Concesionario GYATA"
        assert event["DTSTART"].dt == starts
        assert event["DTEND"].dt == ends

    def test_escapes_commas_and_semicolons_in_title(self) -> None:
        starts = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)
        ics_text = build_ics_event(
            uid="01TESTEVENTULID2", title="Cliente A, B; C", starts_at=starts, ends_at=None,
        )
        cal = icalendar.Calendar.from_ical(ics_text)
        event = [c for c in cal.walk() if c.name == "VEVENT"][0]
        assert str(event["SUMMARY"]) == "Cliente A, B; C"

    def test_uses_crlf_line_endings_per_rfc_5545(self) -> None:
        starts = datetime(2026, 8, 15, 17, 0, tzinfo=timezone.utc)
        ics_text = build_ics_event(uid="01X", title="T", starts_at=starts, ends_at=None)
        assert "\r\n" in ics_text
        # No bare LF without a preceding CR.
        assert "\n" not in ics_text.replace("\r\n", "")

    def test_long_title_is_folded_under_75_octets_per_line(self) -> None:
        long_title = "A" * 200
        starts = datetime(2026, 8, 15, 17, 0, tzinfo=timezone.utc)
        ics_text = build_ics_event(uid="01Y", title=long_title, starts_at=starts, ends_at=None)
        for line in ics_text.split("\r\n"):
            assert len(line) <= 75, f"line exceeds RFC 5545 fold limit: {line!r}"
        # Still round-trips through the independent parser despite folding.
        cal = icalendar.Calendar.from_ical(ics_text)
        event = [c for c in cal.walk() if c.name == "VEVENT"][0]
        assert str(event["SUMMARY"]) == long_title

    def test_no_end_time_defaults_to_start(self) -> None:
        starts = datetime(2026, 8, 15, 17, 0, tzinfo=timezone.utc)
        ics_text = build_ics_event(uid="01Z", title="T", starts_at=starts, ends_at=None)
        cal = icalendar.Calendar.from_ical(ics_text)
        event = [c for c in cal.walk() if c.name == "VEVENT"][0]
        assert event["DTEND"].dt == starts


class TestVCard:
    def test_independent_vobject_library_parses_it(self) -> None:
        vcard_text = build_vcard(name="Juan Pérez", phone_e164="+34612345678", email="juan@example.invalid")
        parsed = vobject.readOne(vcard_text)
        assert parsed.fn.value == "Juan Pérez"
        assert parsed.tel.value == "+34612345678"
        assert parsed.email.value == "juan@example.invalid"

    def test_missing_phone_and_email_still_parses(self) -> None:
        vcard_text = build_vcard(name="Sin Contacto", phone_e164=None, email=None)
        parsed = vobject.readOne(vcard_text)
        assert parsed.fn.value == "Sin Contacto"
        assert not hasattr(parsed, "tel")
        assert not hasattr(parsed, "email")

    def test_escapes_semicolons_and_commas_in_name(self) -> None:
        vcard_text = build_vcard(name="Pérez, Juan; Jr.", phone_e164=None, email=None)
        parsed = vobject.readOne(vcard_text)
        assert parsed.fn.value == "Pérez, Juan; Jr."

    def test_uses_crlf_line_endings_per_rfc_6350(self) -> None:
        vcard_text = build_vcard(name="X", phone_e164=None, email=None)
        assert "\r\n" in vcard_text
        assert "\n" not in vcard_text.replace("\r\n", "")
