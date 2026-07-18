"""Tests for pipeline/identity/photo_hash.py (04-arbitrage.md F6 — identidad-captura).

Does NOT re-test the pHash algorithm itself (pipeline/delta_photo.py::hash_image_bytes
already has its own suite, tests/test_delta_photo.py — reused here, not re-derived,
00-MASTER.md C-1's spirit applied to hashing). These tests cover THIS module's own
value: the governed fetch (per-host rate limiting via pipeline.engine.governor),
error classification, and run_batch's DB read/write + idempotency contract.

Network-free by construction: the "remote" image server is a real local aiohttp.web
app (aiohttp.test_utils.TestServer) — exercises the actual HTTP + decode path with
zero external network dependency.

Rate-governor isolation: every test injects a FRESH ``RateGovernor()`` instance
(never the process-wide singleton) so per-host bucket state never bleeds between
test cases — two tests hitting "127.0.0.1" (TestServer's host, port varies but
``host_of`` strips the port) would otherwise share bucket state and become flaky/slow.

SAFETY CONTRACT (same as tests/test_arbitrage_score.py): DB-touching tests run
inside a rolled-back transaction, using a distinctive ``__CARDEEP_TEST_PH__`` make.
"""
from __future__ import annotations

import asyncio
import io
import os

import asyncpg
import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from PIL import Image

from pipeline.engine.governor import RateGovernor
from pipeline.identity.photo_hash import fetch_and_hash, run_batch
from pipeline.ids import ulid

_DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

_MAKE = "__CARDEEP_TEST_PH__"


def _fast_governor() -> RateGovernor:
    """A governor with no meaningful pacing — for tests only. Production always uses
    the real conservative default (see module docstring: never bypassed silently)."""
    return RateGovernor(rate_per_sec=1000.0, burst=1000.0, min_spacing_s=0.0, jitter_s=0.0)


def _png_bytes(color: tuple[int, int, int] = (50, 100, 150), size: int = 64) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (size, size), color=color).save(buf, format="PNG")
    return buf.getvalue()


async def _make_app() -> web.Application:
    app = web.Application()

    async def good(request: web.Request) -> web.Response:
        return web.Response(body=_png_bytes(), content_type="image/png")

    async def not_found(request: web.Request) -> web.Response:
        return web.Response(status=404)

    async def bad_image(request: web.Request) -> web.Response:
        return web.Response(body=b"not an image at all", content_type="image/jpeg")

    app.router.add_get("/good.png", good)
    app.router.add_get("/notfound.png", not_found)
    app.router.add_get("/bad.jpg", bad_image)
    return app


# ---------------------------------------------------------------------------
# fetch_and_hash against a REAL local aiohttp server (no external network)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFetchAndHash:
    @pytest.mark.asyncio
    async def test_successful_fetch_returns_hash(self):
        app = await _make_app()
        server = TestServer(app)
        await server.start_server()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                outcome = await fetch_and_hash(
                    session, "vid1", str(server.make_url("/good.png")), _fast_governor()
                )
            assert outcome.error is None
            assert outcome.photo_hash is not None
            assert len(outcome.photo_hash) == 16
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_404_recorded_as_error_not_raised(self):
        app = await _make_app()
        server = TestServer(app)
        await server.start_server()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                outcome = await fetch_and_hash(
                    session, "vid2", str(server.make_url("/notfound.png")), _fast_governor()
                )
            assert outcome.photo_hash is None
            assert outcome.error == "http_404"
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_corrupt_image_recorded_as_decode_error(self):
        app = await _make_app()
        server = TestServer(app)
        await server.start_server()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                outcome = await fetch_and_hash(
                    session, "vid3", str(server.make_url("/bad.jpg")), _fast_governor()
                )
            assert outcome.photo_hash is None
            assert outcome.error is not None and outcome.error.startswith("decode_error")
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_unreachable_host_recorded_as_fetch_error(self):
        """A connection that can never succeed (port 1 = reserved, always refused)
        must be classified as a fetch_error, never raise out of fetch_and_hash."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            outcome = await fetch_and_hash(
                session, "vid4", "http://127.0.0.1:1/unreachable.png", _fast_governor()
            )
        assert outcome.photo_hash is None
        assert outcome.error is not None and outcome.error.startswith("fetch_error")


# ---------------------------------------------------------------------------
# run_batch — end-to-end against the live DB (rolled back) + local test server
# ---------------------------------------------------------------------------

class _TestRollback(Exception):
    pass


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_conn():
    conn = await asyncpg.connect(_DSN)
    yield conn
    await conn.close()


async def _seed_vehicle(conn: asyncpg.Connection, *, photo_url: str | None) -> str:
    entity_ulid = ulid()
    vehicle_ulid = ulid()
    cdp_code = f"CDP-ES-28-TST{vehicle_ulid[-8:]}"
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, province_code, status) "
        "VALUES ($1, $2, 'compraventa', '28', 'unverified')",
        entity_ulid, cdp_code,
    )
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, make, photo_url, status) "
        "VALUES ($1,$2,$3,$4,$5,'available')",
        vehicle_ulid, entity_ulid, f"https://example.test/{vehicle_ulid}", _MAKE, photo_url,
    )
    return vehicle_ulid


@pytest.mark.integration
class TestRunBatch:
    @pytest.mark.asyncio
    async def test_hashes_reachable_vehicles_and_skips_unreachable(
        self, db_conn: asyncpg.Connection
    ) -> None:
        app = await _make_app()
        server = TestServer(app)
        await server.start_server()
        try:
            try:
                async with db_conn.transaction():
                    vid_good = await _seed_vehicle(db_conn, photo_url=str(server.make_url("/good.png")))
                    vid_404 = await _seed_vehicle(db_conn, photo_url=str(server.make_url("/notfound.png")))
                    vid_no_photo = await _seed_vehicle(db_conn, photo_url=None)

                    result = await run_batch(
                        db_conn, limit=100, concurrency=5, make_filter=[_MAKE],
                        rate_governor=_fast_governor(),
                    )

                    assert result["attempted"] >= 2  # at least the 2 with a photo_url
                    assert result["hashed"] >= 1
                    assert result["errors"].get("http_404", 0) >= 1

                    good_row = await db_conn.fetchrow(
                        "SELECT photo_hash FROM vehicle WHERE vehicle_ulid=$1", vid_good
                    )
                    assert good_row["photo_hash"] is not None
                    assert len(good_row["photo_hash"]) == 16

                    notfound_row = await db_conn.fetchrow(
                        "SELECT photo_hash FROM vehicle WHERE vehicle_ulid=$1", vid_404
                    )
                    assert notfound_row["photo_hash"] is None

                    no_photo_row = await db_conn.fetchrow(
                        "SELECT photo_hash FROM vehicle WHERE vehicle_ulid=$1", vid_no_photo
                    )
                    assert no_photo_row["photo_hash"] is None  # never attempted (no photo_url)

                    raise _TestRollback()
            except _TestRollback:
                pass
        finally:
            await server.close()

        exists = await db_conn.fetchval("SELECT EXISTS(SELECT 1 FROM vehicle WHERE make=$1)", _MAKE)
        assert not exists, "rollback failed: synthetic photo_hash vehicles leaked into real DB"

    @pytest.mark.asyncio
    async def test_idempotent_rerun_skips_already_hashed(self, db_conn: asyncpg.Connection) -> None:
        app = await _make_app()
        server = TestServer(app)
        await server.start_server()
        try:
            try:
                async with db_conn.transaction():
                    vid = await _seed_vehicle(db_conn, photo_url=str(server.make_url("/good.png")))

                    first = await run_batch(
                        db_conn, limit=100, concurrency=5, make_filter=[_MAKE],
                        rate_governor=_fast_governor(),
                    )
                    assert first["hashed"] >= 1

                    second = await run_batch(
                        db_conn, limit=100, concurrency=5, make_filter=[_MAKE],
                        rate_governor=_fast_governor(),
                    )
                    assert second["attempted"] == 0, "already-hashed vehicle must not be re-selected"

                    reattempted = await db_conn.fetchval(
                        "SELECT photo_hash IS NOT NULL FROM vehicle WHERE vehicle_ulid=$1", vid
                    )
                    assert reattempted is True

                    raise _TestRollback()
            except _TestRollback:
                pass
        finally:
            await server.close()
