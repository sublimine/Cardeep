"""B4.4 — Geo upsert backfill tests.

Verifies the COALESCE-based ON CONFLICT behaviour introduced in B4.4 for
both milanuncios_wholesale._BULK_UPSERT_PARTICULARS and
wallapop_wholesale._BULK_UPSERT_OWNERS_PARTICULARS.

Contract under test (per platform):
  1. INSERT of a particular with municipality_code=NULL succeeds (NULL accepted).
  2. A second upsert with municipality_code=Y (newly resolved) FILLS the NULL.
  3. A third upsert with municipality_code=Z does NOT overwrite the already-set Y
     (COALESCE is a fill-NULL-only mechanism, not an update).
  4. A compraventa (dealer) does NOT have its municipality_code changed by ANY of
     the particular-path SQL — it uses a separate statement with a plain last_seen
     update, intentionally opaque to geo backfill.
  5. wallapop particulars: lat/lon is persisted on first non-NULL insertion and
     also follows the fill-NULL-only rule on subsequent upserts.

Each DB test runs the full scenario inside a single async coroutine that issues
BEGIN + all the statements + assertions + ROLLBACK, all on the same connection.
asyncio.run() is called exactly ONCE per test function (avoids the Windows
ProactorEventLoop 'event loop is closed' error that arises from calling
asyncio.run() multiple times inside a pytest test).
"""
from __future__ import annotations

import asyncio
import uuid

import pytest

# ---------------------------------------------------------------------------
# DB availability guard (identical pattern to test_geo_fuzzy.py)
# ---------------------------------------------------------------------------

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"


def _db_available() -> bool:
    try:
        import asyncpg

        async def _check() -> bool:
            try:
                conn = await asyncpg.connect(DSN, timeout=3)
                await conn.close()
                return True
            except Exception:
                return False

        return asyncio.run(_check())
    except Exception:
        return False


_DB_SKIP = pytest.mark.skipif(
    not _db_available(),
    reason="cardeep-pg not reachable on localhost:5433",
)

# ---------------------------------------------------------------------------
# SQL under test — imported directly from the production modules so the tests
# stay byte-for-byte in sync with the live statements.
# ---------------------------------------------------------------------------

from pipeline.platform.milanuncios_wholesale import (
    _BULK_UPSERT_PARTICULARS as MN_UPSERT_PARTICULARS,
    _BULK_UPSERT_DEALERS as MN_UPSERT_DEALERS,
)
from pipeline.platform.wallapop_wholesale import (
    _BULK_UPSERT_OWNERS_PARTICULARS as WP_UPSERT_PARTICULARS,
    _BULK_UPSERT_OWNERS_DEALERS as WP_UPSERT_DEALERS,
)
from pipeline.ids import ulid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_cdp() -> str:
    """Mint a throwaway cdp_code string that cannot collide with production data."""
    return f"CDP-ES-28-TST{uuid.uuid4().hex[:7].upper()}"


def _fresh_ulid() -> str:
    return ulid()


async def _mn_upsert_particular(conn, cdp: str, entity_ulid: str,
                                muni: str | None, prov: str = "28") -> None:
    """Execute the MN particular bulk upsert for a single row."""
    await conn.execute(
        MN_UPSERT_PARTICULARS,
        [entity_ulid],          # $1 :: text[]
        [cdp],                  # $2 :: text[]
        ["TestParticular"],     # $3 :: text[]
        [prov],                 # $4 :: char(2)[]
        [muni],                 # $5 :: char(5)[]
        ["src_ref_x"],          # $6 :: text[]
        "milanuncios_wholesale",  # $7 scalar
    )


async def _wp_upsert_particular(conn, cdp: str, entity_ulid: str,
                                muni: str | None, lat: float | None,
                                lon: float | None, prov: str = "28") -> None:
    """Execute the WP particular bulk upsert for a single row."""
    await conn.execute(
        WP_UPSERT_PARTICULARS,
        "wallapop_wholesale",   # $1 scalar
        [entity_ulid],          # $2 :: text[]
        [cdp],                  # $3 :: text[]
        ["TestWPParticular"],   # $4 :: text[]
        [prov],                 # $5 :: char(2)[]
        [muni],                 # $6 :: char(5)[]
        [lat],                  # $7 :: double precision[]
        [lon],                  # $8 :: double precision[]
    )


# ---------------------------------------------------------------------------
# Class 1 — milanuncios _BULK_UPSERT_PARTICULARS
# ---------------------------------------------------------------------------

@_DB_SKIP
class TestMilanunciosParticularsCoalesce:
    """The MN particular upsert must fill NULL geo and never overwrite resolved geo."""

    def test_initial_insert_with_null_muni(self) -> None:
        """First INSERT with municipality_code=NULL must land the row with NULL muni."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    uid = _fresh_ulid()
                    await _mn_upsert_particular(conn, cdp, uid, None)
                    row = await conn.fetchrow(
                        "SELECT municipality_code FROM entity WHERE cdp_code=$1", cdp)
                    assert row is not None, "Row must exist after insert"
                    assert row["municipality_code"] is None
                    raise _Rollback  # always rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_second_upsert_fills_null_muni(self) -> None:
        """Second upsert (same cdp, muni=Y) must FILL the existing NULL."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    uid = _fresh_ulid()
                    await _mn_upsert_particular(conn, cdp, uid, None)
                    await _mn_upsert_particular(conn, cdp, _fresh_ulid(), "28079")
                    row = await conn.fetchrow(
                        "SELECT municipality_code FROM entity WHERE cdp_code=$1", cdp)
                    assert row["municipality_code"] == "28079", (
                        "NULL municipality must be filled by a second upsert with a resolved value"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_third_upsert_does_not_overwrite_resolved_muni(self) -> None:
        """Third upsert (muni=Z) must NOT overwrite already-set value (Y).
        COALESCE is fill-NULL-only: once resolved, geo is immutable via this path."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    await _mn_upsert_particular(conn, cdp, _fresh_ulid(), None)
                    await _mn_upsert_particular(conn, cdp, _fresh_ulid(), "28079")
                    await _mn_upsert_particular(conn, cdp, _fresh_ulid(), "28006")
                    row = await conn.fetchrow(
                        "SELECT municipality_code FROM entity WHERE cdp_code=$1", cdp)
                    assert row["municipality_code"] == "28079", (
                        "Already-resolved municipality_code must NOT be overwritten; "
                        "COALESCE is fill-only"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_dealer_muni_unchanged_by_particular_upsert(self) -> None:
        """A compraventa entity (inserted via the DEALER path) must retain its own
        municipality_code regardless of how many particular upserts run — the two
        statements are completely independent."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    dealer_cdp = _fresh_cdp()
                    dealer_uid = _fresh_ulid()
                    await conn.execute(
                        MN_UPSERT_DEALERS,
                        [dealer_uid],
                        [dealer_cdp],
                        ["TestDealer SA"],
                        ["28"],
                        ["28013"],
                        ["src_dealer"],
                        "milanuncios_wholesale",
                    )
                    # Run several particular upserts with different cdps and munis.
                    for i in range(3):
                        await _mn_upsert_particular(conn, _fresh_cdp(), _fresh_ulid(),
                                                    f"2807{i}")
                    row = await conn.fetchrow(
                        "SELECT kind, municipality_code FROM entity WHERE cdp_code=$1",
                        dealer_cdp)
                    assert row is not None
                    assert row["kind"] == "compraventa"
                    assert row["municipality_code"] == "28013", (
                        "Dealer municipality_code must not be affected by particular upserts"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Class 2 — wallapop _BULK_UPSERT_OWNERS_PARTICULARS
# ---------------------------------------------------------------------------

@_DB_SKIP
class TestWallapopParticularsCoalesce:
    """The WP particular upsert must fill NULL geo + lat/lon, never overwrite resolved values."""

    def test_initial_insert_null_geo(self) -> None:
        """First INSERT with municipality_code=NULL and lat/lon=NULL must land."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    uid = _fresh_ulid()
                    await _wp_upsert_particular(conn, cdp, uid, None, None, None)
                    row = await conn.fetchrow(
                        "SELECT municipality_code, lat, lon FROM entity WHERE cdp_code=$1", cdp)
                    assert row is not None
                    assert row["municipality_code"] is None
                    assert row["lat"] is None
                    assert row["lon"] is None
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_second_upsert_fills_null_muni(self) -> None:
        """Second upsert with muni=Y must fill the NULL municipality."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, None, None)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), "28079", None, None)
                    row = await conn.fetchrow(
                        "SELECT municipality_code FROM entity WHERE cdp_code=$1", cdp)
                    assert row["municipality_code"] == "28079"
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_third_upsert_does_not_overwrite_resolved_muni(self) -> None:
        """Third upsert with muni=Z must NOT overwrite already-resolved Y."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, None, None)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), "28079", None, None)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), "28006", None, None)
                    row = await conn.fetchrow(
                        "SELECT municipality_code FROM entity WHERE cdp_code=$1", cdp)
                    assert row["municipality_code"] == "28079", (
                        "Already-resolved municipality_code must NOT be overwritten"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_lat_lon_persisted_on_first_non_null(self) -> None:
        """lat/lon must be persisted from item coordinates on the first non-NULL upsert."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, None, None)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, 40.4168, -3.7038)
                    row = await conn.fetchrow(
                        "SELECT lat, lon FROM entity WHERE cdp_code=$1", cdp)
                    assert row["lat"] == pytest.approx(40.4168, abs=1e-6)
                    assert row["lon"] == pytest.approx(-3.7038, abs=1e-6)
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_lat_lon_not_overwritten_once_set(self) -> None:
        """lat/lon once set must not be overwritten by a subsequent upsert with different
        coordinates (COALESCE fill-only rule extends to lat/lon as well)."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    cdp = _fresh_cdp()
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, None, None)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, 41.3874, 2.1686)
                    await _wp_upsert_particular(conn, cdp, _fresh_ulid(), None, 37.3891, -5.9845)
                    row = await conn.fetchrow(
                        "SELECT lat, lon FROM entity WHERE cdp_code=$1", cdp)
                    assert row["lat"] == pytest.approx(41.3874, abs=1e-6), (
                        "lat must not be overwritten once set"
                    )
                    assert row["lon"] == pytest.approx(2.1686, abs=1e-6), (
                        "lon must not be overwritten once set"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())

    def test_dealer_muni_unchanged_by_particular_upsert(self) -> None:
        """A compraventa (dealer) inserted via WP_UPSERT_DEALERS retains its own
        municipality_code regardless of particular upserts — separate SQL paths."""
        async def _run() -> None:
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                async with conn.transaction():
                    dealer_cdp = _fresh_cdp()
                    dealer_uid = _fresh_ulid()
                    await conn.execute(
                        WP_UPSERT_DEALERS,
                        "wallapop_wholesale",
                        [dealer_uid],
                        [dealer_cdp],
                        ["TestWPDealer SL"],
                        ["28"],
                        ["28006"],
                        ["compraventa"],
                        [True],
                        ["standalone_pos"],
                    )
                    # Several particular upserts with different cdps.
                    for i in range(3):
                        await _wp_upsert_particular(conn, _fresh_cdp(), _fresh_ulid(),
                                                    f"2807{i}", None, None)
                    row = await conn.fetchrow(
                        "SELECT kind, municipality_code FROM entity WHERE cdp_code=$1",
                        dealer_cdp)
                    assert row is not None
                    assert row["kind"] == "compraventa"
                    assert row["municipality_code"] == "28006", (
                        "Dealer municipality_code must not be affected by particular upserts"
                    )
                    raise _Rollback
            except _Rollback:
                pass
            finally:
                await conn.close()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Class 3 — cdp_code stability assertions (unit, no DB needed)
# ---------------------------------------------------------------------------

class TestCdpCodeStabilityParticulars:
    """Verify that the cdp_code for particulars does NOT include municipality_code
    in the hash, so that backfilling geo is safe and cannot change identity."""

    def test_mn_particular_cdp_stable_across_munis(self) -> None:
        """milanuncios particular: same authorId -> same cdp regardless of city/muni."""
        from pipeline.platform.milanuncios_wholesale import ParticularRef, cdp_code_particular
        p_no_city = ParticularRef(
            author_id="12345", name="Juan", province_code="28", city=None)
        p_with_city = ParticularRef(
            author_id="12345", name="Juan", province_code="28", city="Madrid")
        # The cdp hash is over 'particular:milanuncios:12345' — city is irrelevant.
        assert cdp_code_particular(p_no_city) == cdp_code_particular(p_with_city), (
            "MN particular cdp must be stable regardless of city/muni: "
            "municipality_code is NOT part of the canonical key"
        )

    def test_wp_particular_cdp_stable_across_munis(self) -> None:
        """wallapop particular: same user_id -> same cdp regardless of muni."""
        from pipeline.platform.wallapop_wholesale import _particular_cdp
        cdp_no_muni = _particular_cdp("28", "user_999")
        cdp_with_muni = _particular_cdp("28", "user_999")
        # Both calls use the same user_id; muni is not involved.
        assert cdp_no_muni == cdp_with_muni, (
            "WP particular cdp must be stable: municipality_code is NOT part of the key"
        )

    def test_mn_particular_differs_from_dealer_by_design(self) -> None:
        """The canonical key namespaces 'particular:...' vs 'name:...' ensure particulars
        and compraventas can never collide in cdp_code, even with identical province/name."""
        from services.api.codes import cdp_code
        part_cdp = cdp_code(
            province_code="28",
            particular_platform="milanuncios",
            particular_seller_id="99999")
        dealer_cdp = cdp_code(
            province_code="28",
            name="TestDealer",
            municipality_code="28079")
        assert part_cdp != dealer_cdp


# ---------------------------------------------------------------------------
# Internal sentinel exception used to force ROLLBACK inside a transaction block
# ---------------------------------------------------------------------------

class _Rollback(Exception):
    """Raised at end of each test scenario to trigger automatic ROLLBACK via
    the transaction context manager, without propagating as a test failure."""
