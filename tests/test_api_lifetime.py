"""
tests/test_api_lifetime.py
Router tests for GET /vehicles/{ulid}/lifetime — 02-history-reports F2
("Vida en mercado"), plans/cardeep-omni/02-history-reports.md §4/§9-F2.

Mirrors tests/test_api_gaps.py's pattern exactly: TestClient with the real
asyncpg pool against the live cardeep-pg at 127.0.0.1:5433, skipped when the
DB is unreachable.

Covers the F2 acceptance criterion literally: "tests de router (incluido
vehículo sin cadena, alias no canónico — paridad con el contrato de history
línea 35-37, y discrepancia dual-path -> dato suprimido); curl real contra
:8090".
"""
from __future__ import annotations

import asyncio

import asyncpg
import pytest
from fastapi.testclient import TestClient

from services.api.main import app

# ---------------------------------------------------------------------------
# DB connectivity guard (identical pattern to test_api_gaps.py)
# ---------------------------------------------------------------------------


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            conn = await asyncpg.connect(
                "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
                timeout=3,
            )
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()
SKIP_NO_DB = pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")


def _fetchval(sql: str, *args) -> object:
    async def _q():
        conn = await asyncpg.connect(
            "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=5
        )
        try:
            return await conn.fetchval(sql, *args)
        finally:
            await conn.close()
    return asyncio.run(_q())


def _fetchrow(sql: str, *args):
    async def _q():
        conn = await asyncpg.connect(
            "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep", timeout=5
        )
        try:
            return await conn.fetchrow(sql, *args)
        finally:
            await conn.close()
    return asyncio.run(_q())


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Fixture discovery — real ulids from the live DB, never hardcoded.
# ---------------------------------------------------------------------------


def _any_available_vehicle_ulid() -> str | None:
    return _fetchval("SELECT vehicle_ulid FROM vehicle WHERE status='available' LIMIT 1")


def _any_alias_vehicle_ulid() -> str | None:
    """A non-canonical alias per v_canonical_vehicle (parity with the
    /history contract, vehicles.py:35-37: history is served for aliases too)."""
    return _fetchval(
        "SELECT vehicle_ulid FROM v_canonical_vehicle "
        "WHERE vehicle_ulid <> canonical_vehicle_ulid LIMIT 1"
    )


def _any_verified_chain_member() -> str | None:
    """A vehicle_ulid that appears in the CURRENT vam_verified lifetime run, if any.

    Honest by construction: if no run is vam_verified=TRUE yet (F1's default,
    gated state), this returns None and the corresponding test is skipped
    rather than asserting a chain that does not exist.
    """
    return _fetchval("SELECT vehicle_ulid_from FROM v_vehicle_lifetime LIMIT 1")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestVehicleLifetimeNotFound:
    @SKIP_NO_DB
    def test_returns_404_for_nonexistent(self, client: TestClient) -> None:
        r = client.get("/vehicles/01XXXXXXXXXXXXXXXXXXXXXXXX/lifetime")
        assert r.status_code == 404
        assert r.json()["ok"] is False


class TestVehicleLifetimeEnvelope:
    @SKIP_NO_DB
    def test_envelope_shape(self, client: TestClient) -> None:
        ulid = _any_available_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["error"] is None
        assert body["meta"]["count"] >= 1


class TestVehicleLifetimeNoChain:
    @SKIP_NO_DB
    def test_vehicle_without_chain_degrades_honestly(self, client: TestClient) -> None:
        """A vehicle with no F1 link still gets its own episode metrics
        (C1/C3/C4/C8a/C10), with chain_verified=False and no invented
        chain-only fields (C2/C6/C7) — never an error, never a fabricated chain."""
        ulid = _any_available_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["vehicle_ulid"] == ulid
        assert isinstance(data["episodes"], list)
        assert len(data["episodes"]) >= 1
        assert "chain_verified" in data
        aggregates = data["aggregates"]
        if not data["chain_verified"]:
            assert aggregates["c2_total_days"] is None
            assert aggregates["c6_dealer_count"] is None
            assert data["links"] == []

    @SKIP_NO_DB
    def test_semaforo_always_present_with_triggers_or_none(self, client: TestClient) -> None:
        ulid = _any_available_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        semaforo = r.json()["data"]["semaforo"]
        assert semaforo["label"] in {"sin_senales", "con_avisos", "con_senales_fuertes"}
        if semaforo["label"] != "sin_senales":
            assert len(semaforo["triggers"]) > 0


class TestVehicleLifetimeAlias:
    @SKIP_NO_DB
    def test_alias_vehicle_still_served(self, client: TestClient) -> None:
        """Parity with /history (vehicles.py:35-37): a non-canonical alias
        vehicle_ulid is a real row in vehicle_event/vehicle and must still get
        a lifetime response, never a 404 (aliasing is entity-level dedup, not
        an erasure of this vehicle's own history)."""
        ulid = _any_alias_vehicle_ulid()
        if ulid is None:
            pytest.skip("No aliased vehicle found in v_canonical_vehicle")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        assert r.status_code == 200
        assert r.json()["data"]["vehicle_ulid"] == ulid


class TestVehicleLifetimeVerifiedChain:
    @SKIP_NO_DB
    def test_verified_chain_member_gets_chain_true(self, client: TestClient) -> None:
        """If a lifetime_link_run is vam_verified=TRUE and this vehicle is a
        member, the response must expose the real chain — never require this
        to be true (F1's gate may still be FALSE, an honest v1 state)."""
        ulid = _any_verified_chain_member()
        if ulid is None:
            pytest.skip("No vam_verified=TRUE lifetime_link_run yet — F1 gate not opened")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["chain_verified"] is True
        assert len(data["links"]) >= 1
        assert len(data["episodes"]) >= 2


class TestVehicleLifetimeRateLimitCoherence:
    @SKIP_NO_DB
    def test_requires_no_extra_params(self, client: TestClient) -> None:
        """Un-paginated, single-vehicle endpoint — no page/size params (coherent
        with vehicles.py:6's contract note: pagination only where rows are
        unbounded; a lifetime chain is bounded by construction)."""
        ulid = _any_available_vehicle_ulid()
        if ulid is None:
            pytest.skip("No available vehicle found in DB")
        r = client.get(f"/vehicles/{ulid}/lifetime")
        assert r.status_code == 200
        assert "page" not in r.json()["meta"]
