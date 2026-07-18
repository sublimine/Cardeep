"""Tests for services/api/routers/crm_notes.py and crm_calendar.py (06-unified-crm-chat F6).

Same live-DB + TestClient pattern as the other crm_* router tests.
"""
from __future__ import annotations

import asyncio
import uuid

import asyncpg
import icalendar
import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.ratelimit import limiter

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
DEMO_EMAIL = "demo@cardeep.local"
DEMO_PASSWORD = "CardeepDemo2026!"


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
        await conn.execute("DELETE FROM crm_note WHERE title LIKE 'ZZTEST_%'")
        await conn.execute("DELETE FROM crm_event WHERE title LIKE 'ZZTEST_%'")
    finally:
        await conn.close()


def _unique(prefix: str) -> str:
    return f"ZZTEST_{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def gyata_token(client: TestClient) -> str:
    r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestNotesCrud:
    def test_requires_auth(self, client: TestClient) -> None:
        assert client.get("/notes").status_code == 401

    def test_create_list_update_delete_roundtrip(self, client: TestClient, gyata_token: str) -> None:
        title = _unique("Note")
        created = client.post(
            "/notes", json={"title": title, "body": "Cuerpo de prueba", "color": "sky", "pinned": True},
            headers=_auth(gyata_token),
        )
        assert created.status_code == 201, created.text
        note_id = created.json()["id"]
        assert created.json()["pinned"] is True

        listing = client.get("/notes", headers=_auth(gyata_token))
        assert listing.status_code == 200
        assert any(n["id"] == note_id for n in listing.json()["notes"])

        patched = client.patch(f"/notes/{note_id}", json={"pinned": False, "color": "rose"}, headers=_auth(gyata_token))
        assert patched.status_code == 200, patched.text
        assert patched.json()["pinned"] is False
        assert patched.json()["color"] == "rose"

        deleted = client.delete(f"/notes/{note_id}", headers=_auth(gyata_token))
        assert deleted.status_code == 204

        listing_after = client.get("/notes", headers=_auth(gyata_token))
        assert not any(n["id"] == note_id for n in listing_after.json()["notes"])

    def test_invalid_color_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.post("/notes", json={"title": _unique("BadColor"), "color": "purple"}, headers=_auth(gyata_token))
        assert r.status_code == 422


class TestCalendarCrud:
    def test_requires_auth(self, client: TestClient) -> None:
        assert client.get("/calendar/events").status_code == 401

    def test_create_and_list_event(self, client: TestClient, gyata_token: str) -> None:
        title = _unique("Event")
        created = client.post(
            "/calendar/events",
            json={"title": title, "startsAt": "2026-08-15T17:00:00+00:00", "type": "visit"},
            headers=_auth(gyata_token),
        )
        assert created.status_code == 201, created.text
        event_id = created.json()["id"]

        listing = client.get(
            "/calendar/events?start=2026-08-01T00:00:00Z&end=2026-08-31T23:59:59Z", headers=_auth(gyata_token)
        )
        assert listing.status_code == 200
        assert any(e["id"] == event_id for e in listing.json()["events"])

    def test_invalid_type_is_422(self, client: TestClient, gyata_token: str) -> None:
        r = client.post(
            "/calendar/events", json={"title": _unique("BadType"), "startsAt": "2026-08-15T17:00:00Z", "type": "party"},
            headers=_auth(gyata_token),
        )
        assert r.status_code == 422

    def test_delete_event(self, client: TestClient, gyata_token: str) -> None:
        created = client.post(
            "/calendar/events",
            json={"title": _unique("ToDelete"), "startsAt": "2026-08-16T10:00:00Z"},
            headers=_auth(gyata_token),
        )
        event_id = created.json()["id"]
        deleted = client.delete(f"/calendar/events/{event_id}", headers=_auth(gyata_token))
        assert deleted.status_code == 204

    def test_ics_export_is_valid_and_independently_parseable(self, client: TestClient, gyata_token: str) -> None:
        title = _unique("IcsExport")
        created = client.post(
            "/calendar/events",
            json={"title": title, "startsAt": "2026-09-01T09:00:00Z", "endsAt": "2026-09-01T10:00:00Z", "location": "Oficina"},
            headers=_auth(gyata_token),
        )
        event_id = created.json()["id"]

        ics = client.get(f"/calendar/events/{event_id}/ics", headers=_auth(gyata_token))
        assert ics.status_code == 200
        assert ics.headers["content-type"].startswith("text/calendar")

        cal = icalendar.Calendar.from_ical(ics.text)
        events = [c for c in cal.walk() if c.name == "VEVENT"]
        assert len(events) == 1
        assert str(events[0]["SUMMARY"]) == title
        assert str(events[0]["LOCATION"]) == "Oficina"
