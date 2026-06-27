"""
tests/test_seed_centroides_country.py

GOLDEN -- the geo-centroid seed (scripts/seed_geo_centroides.py) country-scope
(red-team R3 #9).

The seed loads the INE/ES municipal centroid CSV into geo_municipality. Its PK is
(country_code, code) (migration 0052) and ``code`` is VARCHAR(16) since the geo width
widening (migration 0059). The pre-fix seed was COUNTRY-BLIND three ways:

  * the UPDATE matched ``WHERE code = $3`` ALONE -- so a single ES seed overwrote the
    lat/lon of EVERY country's municipality sharing that INE-shaped code (e.g. a DE
    muni deliberately reusing '28079');
  * the ``db_state`` dict collapsed rows by ``code`` alone, pooling countries;
  * the lookup cast ``::char(5)[]`` baked the ES INE 5-char width, truncating any
    wider (e.g. IT 6-digit ISTAT) code post-0059.

The fix threads COUNTRY='ES' into the SELECT and the UPDATE, keys ``db_state`` by
(country_code, code), and drops the width-locked cast to ``::text[]``.

WHAT IS ASSERTED
----------------
  isolation : with ES + DE municipalities sharing INE code '28079' (DE carrying a
              distinct sentinel centroid), running the REAL seed with the ES CSV leaves
              the DE row's centroid UNTOUCHED. RED pre-fix (the country-blind UPDATE
              clobbered DE with Madrid's coordinates), GREEN post-fix.
  es-served : the ES '28079' row IS updated to the exact CSV centroid -- proving the
              country-scope is a no-op for the sole ES tenant (byte-identical) and that
              the update actually ran (no vacuous green).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). HARD-REFUSES :5433
(live production) by DSN string AND by asserting the target census (``entity``) is EMPTY
before seeding. Every test seeds inside a transaction and ROLLS BACK -- the dry-run stays
byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import asyncio
import os

import pytest

from scripts.seed_geo_centroides import _load_centroides, seed

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"
DSN = os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)

_SHARED_CODE = "28079"        # Madrid capital INE code, present in the centroid CSV
_DE_SENTINEL = (55.0, 10.0)   # a plainly-German centroid the ES seed must never touch


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


_DB_SKIP = pytest.mark.skipif(not _db_available(), reason=f"cardeep-pg not reachable at {DSN}")


class _Rollback(Exception):
    """Sentinel raised at the end of a scenario to force ROLLBACK via the transaction
    context manager, without surfacing as a test failure."""


async def _assert_empty_dry_run(conn) -> None:
    """Refuse to seed unless the target ``entity`` is EMPTY (the :5434 dry-run is
    entity=0; live production holds ~452k) -- a mis-pointed DSN can never mutate real
    data."""
    n = await conn.fetchval("SELECT count(*) FROM entity")
    assert n == 0, (
        f"target DB has {n} entities -- not the empty :5434 dry-run; refusing to seed")


async def _seed_muni(conn, country: str, code: str, lat: float, lon: float) -> None:
    """Seed geo_province + one geo_municipality with an explicit centroid. The composite
    FK geo_municipality(country_code, province_code) -> geo_province is satisfied; the ES
    muni-prefix CHECK left(code,2)=province_code holds for '28079' (left='28')."""
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1, $2, '13', $3, $4) ON CONFLICT DO NOTHING",
        code[:2], f"prov-{country}-{code[:2]}", f"ccaa-{country}", country)
    await conn.execute(
        "INSERT INTO geo_municipality "
        "(code, name, province_code, comarca_id, lat, lon, country_code) "
        "VALUES ($1, $2, $3, NULL, $4, $5, $6)",
        code, f"muni-{country}-{code}", code[:2], lat, lon, country)


@pytest.mark.integration
@_DB_SKIP
def test_es_centroid_seed_never_touches_other_country():
    """ES + DE muni share INE code '28079'. Running the REAL seed with the ES CSV must
    update ONLY the ES centroid and leave the DE sentinel intact. RED pre-fix: the
    country-blind ``UPDATE ... WHERE code = $3`` clobbered the German row."""
    if "5433" in DSN:
        pytest.skip("refusing to run the centroid-isolation golden against :5433 "
                    "(live production); point CARDEEP_DSN at the :5434 dry-run")

    async def _run() -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await _assert_empty_dry_run(conn)
                # ES '28079' carries a deliberately-wrong centroid the seed must FIX;
                # DE '28079' carries a German sentinel the seed must NEVER touch.
                await _seed_muni(conn, "ES", _SHARED_CODE, 1.0, 1.0)
                await _seed_muni(conn, "DE", _SHARED_CODE, *_DE_SENTINEL)

                await seed(conn)

                de = await conn.fetchrow(
                    "SELECT lat, lon FROM geo_municipality "
                    "WHERE country_code='DE' AND code=$1", _SHARED_CODE)
                assert (de["lat"], de["lon"]) == _DE_SENTINEL, (
                    f"CROSS-COUNTRY CLOBBER: DE muni '{_SHARED_CODE}' centroid became "
                    f"{(de['lat'], de['lon'])}; expected the untouched sentinel "
                    f"{_DE_SENTINEL}. The ES centroid seed overwrote a German municipality.")

                expected = _load_centroides()[_SHARED_CODE]
                es = await conn.fetchrow(
                    "SELECT lat, lon FROM geo_municipality "
                    "WHERE country_code='ES' AND code=$1", _SHARED_CODE)
                assert (es["lat"], es["lon"]) == pytest.approx(expected), (
                    f"ES muni '{_SHARED_CODE}' centroid was {(es['lat'], es['lon'])}; "
                    f"expected the CSV value {expected} -- the ES update did not run.")
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    asyncio.run(_run())


@pytest.mark.integration
@_DB_SKIP
def test_es_centroid_seed_byte_identical_single_tenant():
    """With ONLY ES seeded, the seed updates the sole ES '28079' row to EXACTLY the CSV
    centroid and reports updated==1 -- the country-scope is a no-op for the lone tenant
    (the figure a country-blind seed would have produced)."""
    if "5433" in DSN:
        pytest.skip("refusing to run against :5433 (live production); "
                    "point CARDEEP_DSN at the :5434 dry-run")

    async def _run() -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await _assert_empty_dry_run(conn)
                await _seed_muni(conn, "ES", _SHARED_CODE, 1.0, 1.0)

                counts = await seed(conn)

                expected = _load_centroides()[_SHARED_CODE]
                es = await conn.fetchrow(
                    "SELECT lat, lon FROM geo_municipality "
                    "WHERE country_code='ES' AND code=$1", _SHARED_CODE)
                assert (es["lat"], es["lon"]) == pytest.approx(expected), (
                    f"ES single-tenant centroid {(es['lat'], es['lon'])} != CSV {expected}")
                assert counts["updated"] == 1, (
                    f"expected exactly 1 ES row updated, got {counts['updated']}")
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    asyncio.run(_run())
