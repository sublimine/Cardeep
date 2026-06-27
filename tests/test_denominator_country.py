"""
tests/test_denominator_country.py

GOLDEN -- the per-province VENTA denominator load (scripts/load_denominator_provincia.py)
country-scope (red-team R3 #10).

denominator_estimate carries country_code since migration 0053 (DEFAULT 'ES') and its FK
is composite (country_code, province_code) -> geo_province. The pre-fix load was
COUNTRY-BLIND: it ``DELETE FROM denominator_estimate WHERE segment='venta'`` across ALL
countries and re-INSERTed WITHOUT country_code (relying on the DEFAULT). So an ES reload
WIPED every other country's 'venta' denominators -- and denominator_estimate feeds the
SERVED certificates v_province_seal / v_exhaustiveness_seal, so the wipe silently broke a
second tenant's seal.

The fix threads COUNTRY='ES' into the existence pre-check, the DELETE and the INSERT.

WHAT IS ASSERTED
----------------
  isolation : with a DE 'venta' denominator seeded (province '28', shared with ES Madrid),
              running the REAL ES load leaves the DE row PRESENT and unchanged. RED pre-fix
              (the country-blind DELETE removed it), GREEN post-fix.
  es-loaded : the 52 ES 'venta' rows are loaded under country_code='ES' with the exact
              CSV-derived point_est values -- the load ran and is correctly scoped
              (byte-identical to the historical single-tenant load).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). HARD-REFUSES :5433 (live
production) by DSN string AND by asserting the target census (``entity``) is EMPTY before
seeding. Every test seeds inside a transaction and ROLLS BACK -- the dry-run stays
byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import asyncio
import os

import pytest

from scripts.load_denominator_provincia import _load_rows, load

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"
DSN = os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)

_DE_PROVINCE = "28"          # shared with ES Madrid -- the deliberate 0053 dup-code coexistence
_DE_SENTINEL_EST = 4242.0    # a value no ES province produces -- uniquely identifies the DE row


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
    n = await conn.fetchval("SELECT count(*) FROM entity")
    assert n == 0, (
        f"target DB has {n} entities -- not the empty :5434 dry-run; refusing to seed")


async def _seed_es_provinces(conn) -> list[str]:
    """Seed the 52 ES provinces the load pre-checks against + FK-references."""
    codes = [pc for pc, _, _ in _load_rows()]
    for pc in codes:
        await conn.execute(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES ($1, $2, '13', 'ccaa-ES', 'ES') ON CONFLICT DO NOTHING",
            pc, f"prov-ES-{pc}")
    return codes


async def _seed_de_venta_denominator(conn) -> None:
    """A DE 'venta' registral ceiling sharing province code '28' with ES Madrid. Needs the
    DE province row for the composite FK (country_code, province_code)."""
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1, 'prov-DE-28', '13', 'reg-DE', 'DE') ON CONFLICT DO NOTHING",
        _DE_PROVINCE)
    await conn.execute(
        "INSERT INTO denominator_estimate "
        "(segment, province_code, method, point_est, ci_low, ci_high, country_code) "
        "VALUES ('venta', $1, 'registral_ceiling', $2, $2, $2, 'DE')",
        _DE_PROVINCE, _DE_SENTINEL_EST)


@pytest.mark.integration
@_DB_SKIP
def test_es_denominator_load_never_deletes_other_country():
    """A DE 'venta' denominator must SURVIVE an ES load. RED pre-fix: the country-blind
    ``DELETE ... WHERE segment='venta'`` wiped every country's 'venta' denominators."""
    if "5433" in DSN:
        pytest.skip("refusing to run the denominator-isolation golden against :5433 "
                    "(live production); point CARDEEP_DSN at the :5434 dry-run")

    async def _run() -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await _assert_empty_dry_run(conn)
                await _seed_es_provinces(conn)
                await _seed_de_venta_denominator(conn)

                await load(conn, apply=True)

                de = await conn.fetchrow(
                    "SELECT point_est FROM denominator_estimate "
                    "WHERE segment='venta' AND country_code='DE' AND province_code=$1",
                    _DE_PROVINCE)
                assert de is not None and de["point_est"] == _DE_SENTINEL_EST, (
                    f"CROSS-COUNTRY WIPE: DE 'venta' denominator for province "
                    f"'{_DE_PROVINCE}' is {de}; expected point_est={_DE_SENTINEL_EST} "
                    "(present, unchanged). The ES load deleted another country's denominator.")

                es_rows = await conn.fetchval(
                    "SELECT count(*) FROM denominator_estimate "
                    "WHERE segment='venta' AND country_code='ES'")
                assert es_rows == 52, (
                    f"ES load produced {es_rows} 'venta' rows under country='ES'; "
                    "expected 52 -- the load must run AND be country-scoped.")
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    asyncio.run(_run())


@pytest.mark.integration
@_DB_SKIP
def test_es_denominator_load_byte_identical_single_tenant():
    """With ONLY ES seeded, the load yields exactly the 52 ES 'venta' rows with the
    CSV-derived point_est values -- the country-scope is a no-op for the sole tenant
    (byte-identical to the historical country-blind load)."""
    if "5433" in DSN:
        pytest.skip("refusing to run against :5433 (live production); "
                    "point CARDEEP_DSN at the :5434 dry-run")

    async def _run() -> None:
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            async with conn.transaction():
                await _assert_empty_dry_run(conn)
                await _seed_es_provinces(conn)

                await load(conn, apply=True)

                expected = {pc: float(den) for pc, _, den in _load_rows()}
                got = {
                    r["province_code"]: r["point_est"]
                    for r in await conn.fetch(
                        "SELECT province_code, point_est FROM denominator_estimate "
                        "WHERE segment='venta' AND country_code='ES'")
                }
                assert got == expected, (
                    "ES single-tenant load not byte-identical to the CSV-derived "
                    f"denominators: {len(got)} rows, mismatch present")
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    asyncio.run(_run())
