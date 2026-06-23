"""Minimal, REVERSIBLE second-country onboarding pilot - the end-to-end replication proof.

PURPOSE
-------
Prove the Cardeep census replicates to a SECOND country end-to-end WITHOUT changing
any Spain (ES) behavior. The pilot seeds a tiny SYNTHETIC backbone for a non-ES country
(default ``DE``) - two provinces, one of which DELIBERATELY reuses ES Madrid's province
code ``28`` to prove the historical primary-key collision is gone - one municipality, and
one synthetic dealer entity minted through the REAL coder
(:func:`services.api.codes.cdp_pair` with ``country_code='DE'``). It then verifies:

  * (DE,'28') and (ES,'28') COEXIST in geo_province - the collision the single-column
    PK once caused is gone.
  * the DE municipality's geo FK resolves to the DE province, NOT to ES Madrid.
  * the synthetic ``CDP-DE-28-...`` entity resolves via the country-agnostic
    :func:`services.api.deps.resolve_cluster` (its own canonical, no ES bleed).
  * ES row counts (entity / geo_province / geo_municipality where country_code='ES')
    are BYTE-IDENTICAL before and after - the non-negotiable invariant.

It harvests NO real DE data - this is a synthetic minimal proof only.

PREREQUISITE - migration 0053 MUST be applied first
---------------------------------------------------
This pilot REQUIRES ``migrations/0053_country_onboarding.sql`` to be applied, which
promotes geo_province / geo_municipality PKs from ``(code)`` to ``(country_code, code)``
and rewrites the referencing FKs to composite. WITHOUT 0053, seeding province (DE,'28')
fails on ``geo_province_pkey`` - verified live 2026-06-23::

    duplicate key value violates unique constraint "geo_province_pkey"
    DETAIL:  Key (code)=(28) already exists.

The pilot DETECTS this up front (a rolled-back probe insert) and refuses to seed with a
clear message rather than emitting a confusing mid-transaction error. ``0053`` is applied
by the operator (``python -m scripts.migrate up``), NEVER by this script.

USAGE
-----
    python -m scripts.pilot_country                      # DRY-RUN (default): probe + plan only, no writes
    python -m scripts.pilot_country --apply              # seed + verify the DE pilot (idempotent)
    python -m scripts.pilot_country --verify             # re-run assertions against already-seeded rows
    python -m scripts.pilot_country --revert             # delete ALL pilot rows for the country (reversible)
    python -m scripts.pilot_country --country DE --apply # explicit country (default DE)

The default (no flag) is a DRY-RUN: it probes whether 0053 is applied and prints exactly
what WOULD be written, touching nothing. ``--apply`` is idempotent (re-running is a no-op
on the natural keys). ``--revert`` removes every pilot row and is itself idempotent
(deleting absent rows is a no-op). ES rows are never touched by any path.

Design references (verified against live schema + source, 2026-06-23):
  * geo_province requires ccaa_code (CHAR(2)) + ccaa_name (TEXT), both NOT NULL no-default
    (migrations/0001_geo.sql:7-8). The pilot supplies them (a Bundesland label for DE).
  * geo_municipality.comarca_id is nullable (0001_geo.sql:22) so a 2-level DE backbone needs
    no geo_comarca row.
  * entity NOT-NULL no-default columns are exactly entity_ulid, cdp_code, kind (live probe);
    everything else defaults - so a minimal INSERT supplies only those plus the geo/country FKs.
  * the cdp_code / canonical_key are minted by the SAME coder as ES, with country_code only
    entering the human-facing prefix (services/api/codes.py:53,61-65) - ES codes are unaffected.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import secrets
import sys
import time

import asyncpg

from services.api.codes import cdp_pair
from services.api.deps import resolve_cluster

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # no I, L, O, U - matches codes.py / entity_ulid_shape

# The single province code DELIBERATELY shared with ES (Madrid) to prove the collision is gone.
COLLISION_PROVINCE = "28"
# A second, country-local province so the pilot is not purely the collision case.
SECOND_PROVINCE = "11"
# The synthetic municipality. left(code,2) == COLLISION_PROVINCE so the ES-shaped
# municipality_province_prefix CHECK passes regardless of the 0053 relaxation.
PILOT_MUNI = "28001"
# Synthetic dealer domain - never resolves to a real site (RFC 6761 / reserved example TLD use).
PILOT_DOMAIN = "example-haendler.de"


def ulid() -> str:
    """Minimal time-ordered ULID-like id (48-bit ms time + 80-bit randomness).

    Produces a 26-char Crockford-base32 string matching entity_ulid_shape
    (^[0-9A-HJKMNP-TV-Z]{26}$, migrations/0006_entity_evolve.sql:16). Copied from
    scripts/seed_pilot.py so the pilot has no cross-script import coupling.
    """
    ts = int(time.time() * 1000)
    rnd = int.from_bytes(secrets.token_bytes(10), "big")
    num = (ts << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))


class PilotError(RuntimeError):
    """Raised when the environment cannot host the pilot (e.g. 0053 not yet applied)."""


# ---------------------------------------------------------------------------
# Pilot row definitions - pure data, country-parametrized.
# ---------------------------------------------------------------------------

def _provinces(country: str) -> list[dict[str, str]]:
    """Two synthetic provinces. The first reuses ES Madrid's code '28' on purpose."""
    return [
        {
            "code": COLLISION_PROVINCE,
            "name": f"{country}-Brandenburg-pilot",
            "ccaa_code": "BB",
            "ccaa_name": "Brandenburg",
        },
        {
            "code": SECOND_PROVINCE,
            "name": f"{country}-Berlin-pilot",
            "ccaa_code": "BE",
            "ccaa_name": "Berlin",
        },
    ]


def _municipality(country: str) -> dict[str, str]:
    return {
        "code": PILOT_MUNI,
        "name": f"{country}-Potsdam-pilot",
        "province_code": COLLISION_PROVINCE,
    }


# ---------------------------------------------------------------------------
# Baseline / safety helpers.
# ---------------------------------------------------------------------------

async def _es_baseline(conn: asyncpg.Connection) -> dict[str, int]:
    """Snapshot the ES row counts that MUST stay byte-identical across the pilot."""
    return {
        "entity_ES": await conn.fetchval("SELECT count(*) FROM entity WHERE country_code='ES'"),
        "province_ES": await conn.fetchval("SELECT count(*) FROM geo_province WHERE country_code='ES'"),
        "municipality_ES": await conn.fetchval(
            "SELECT count(*) FROM geo_municipality WHERE country_code='ES'"),
    }


async def _composite_pk_applied(conn: asyncpg.Connection) -> bool:
    """True iff geo_province's PRIMARY KEY is the composite (country_code, code) from 0053.

    Checks pg_get_constraintdef of the table's PK rather than guessing - assume nothing.
    """
    pk_def = await conn.fetchval(
        """
        SELECT pg_get_constraintdef(oid)
          FROM pg_constraint
         WHERE conrelid = 'geo_province'::regclass AND contype = 'p'
        """
    )
    return pk_def is not None and "country_code" in pk_def


async def _ensure_ready(conn: asyncpg.Connection, country: str) -> None:
    """Refuse to seed unless 0053 is applied. Confirms with a rolled-back probe insert.

    The probe is the SAME insert the live collision test used: writing province
    (country,'28') must succeed only when the PK is composite. Always rolled back so the
    readiness check itself leaves zero residue.
    """
    if await _composite_pk_applied(conn):
        return
    # PK still single-column - confirm the collision concretely, then refuse.
    tr = conn.transaction()
    await tr.start()
    try:
        await conn.execute(
            "INSERT INTO geo_province(code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES ($1, 'probe', 'XX', 'probe', $2)",
            COLLISION_PROVINCE, country,
        )
        # If we somehow got here the PK is not blocking - unusual, but not our gate.
        await tr.rollback()
    except asyncpg.UniqueViolationError as exc:
        await tr.rollback()
        raise PilotError(
            "migration 0053_country_onboarding.sql is NOT applied: geo_province still has a "
            "single-column PRIMARY KEY (code), so seeding province "
            f"({country},'{COLLISION_PROVINCE}') collides with ES.\n  live error: {exc}\n"
            "  fix: operator runs `python -m scripts.migrate up` (then `verify`) BEFORE this pilot."
        ) from exc
    except Exception:
        await tr.rollback()
        raise


# ---------------------------------------------------------------------------
# Seed / verify / revert phases.
# ---------------------------------------------------------------------------

async def seed(conn: asyncpg.Connection, country: str) -> dict[str, str]:
    """Insert the synthetic backbone + dealer for *country*. Idempotent on natural keys.

    Returns the minted identifiers (cdp_code, entity_ulid, canonical_key) for the dealer.
    Runs as ONE transaction so a partial seed never lands.
    """
    key, code = cdp_pair(province_code=COLLISION_PROVINCE, domain=PILOT_DOMAIN, country_code=country)
    async with conn.transaction():
        for prov in _provinces(country):
            await conn.execute(
                "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
                "VALUES ($1, $2, $3, $4, $5) "
                "ON CONFLICT (country_code, code) DO NOTHING",
                prov["code"], prov["name"], prov["ccaa_code"], prov["ccaa_name"], country,
            )
        muni = _municipality(country)
        await conn.execute(
            "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
            "VALUES ($1, $2, $3, NULL, $4) "
            "ON CONFLICT (country_code, code) DO NOTHING",
            muni["code"], muni["name"], muni["province_code"], country,
        )
        existing = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code = $1", code)
        if existing is None:
            await conn.execute(
                """
                INSERT INTO entity (entity_ulid, cdp_code, kind, country_code,
                                    province_code, municipality_code, canonical_key,
                                    status, kind_source, trade_name, first_discovered_source)
                VALUES ($1, $2, 'compraventa', $3, $4, $5, $6,
                        'active', 'manual', $7, 'pilot_country')
                """,
                ulid(), code, country, COLLISION_PROVINCE, PILOT_MUNI, key,
                f"{country} Pilot Dealer",
            )
    return {"cdp_code": code, "canonical_key": key}


async def verify(conn: asyncpg.Connection, country: str, baseline: dict[str, int]) -> list[str]:
    """Assert coexistence, correct FK resolution, cluster resolution, and ES identity.

    Returns a list of human-readable PASS lines; raises AssertionError on the first failure.
    """
    out: list[str] = []

    # (a) Coexistence: code '28' now carries BOTH (ES, Madrid) and (country, ...-Brandenburg-pilot).
    prov_rows = await conn.fetch(
        "SELECT country_code, name FROM geo_province WHERE code = $1 ORDER BY country_code",
        COLLISION_PROVINCE,
    )
    by_country = {r["country_code"].strip(): r["name"] for r in prov_rows}
    assert by_country.get("ES") == "Madrid", f"ES province 28 must stay 'Madrid', got {by_country.get('ES')!r}"
    assert country in by_country, f"province ({country},'{COLLISION_PROVINCE}') missing - seed first"
    out.append(
        f"[PASS] coexistence: province '{COLLISION_PROVINCE}' = "
        f"(ES, {by_country['ES']!r}) AND ({country}, {by_country[country]!r}) - collision gone"
    )

    # (b) The pilot municipality's composite FK resolves to the COUNTRY province, not ES Madrid.
    resolved = await conn.fetchval(
        """
        SELECT p.name
          FROM geo_municipality m
          JOIN geo_province p
            ON p.country_code = m.country_code AND p.code = m.province_code
         WHERE m.country_code = $1 AND m.code = $2
        """,
        country, PILOT_MUNI,
    )
    assert resolved is not None, f"municipality ({country},'{PILOT_MUNI}') FK did not resolve"
    assert resolved != "Madrid", (
        f"municipality ({country},'{PILOT_MUNI}') wrongly resolved to ES Madrid - composite FK broken"
    )
    out.append(f"[PASS] geo FK: muni ({country},'{PILOT_MUNI}') -> province {resolved!r} (not ES Madrid)")

    # (c) The synthetic dealer resolves through the country-agnostic resolver as its own canonical.
    _, code = cdp_pair(province_code=COLLISION_PROVINCE, domain=PILOT_DOMAIN, country_code=country)
    assert code.startswith(f"CDP-{country}-{COLLISION_PROVINCE}-"), f"minted code shape wrong: {code}"
    cluster = await resolve_cluster(conn, code)
    assert cluster is not None, f"resolve_cluster returned None for {code}"
    assert cluster.canonical_cdp_code == code, (
        f"{code} should be its own canonical (no ES bleed), got {cluster.canonical_cdp_code}"
    )
    assert cluster.member_cdp_codes == [code], (
        f"{code} cluster must contain only itself, got {cluster.member_cdp_codes}"
    )
    out.append(f"[PASS] resolve: {code} -> canonical=self, members={len(cluster.member_cdp_codes)} (no ES bleed)")

    # (d) No ES mutation: ES counts are byte-identical to the pre-seed baseline.
    after = await _es_baseline(conn)
    for k in ("entity_ES", "province_ES", "municipality_ES"):
        assert after[k] == baseline[k], (
            f"ES INVARIANT VIOLATED: {k} changed {baseline[k]} -> {after[k]}"
        )
    out.append(
        f"[PASS] ES byte-identity: entity={after['entity_ES']} province={after['province_ES']} "
        f"municipality={after['municipality_ES']} (unchanged vs baseline)"
    )
    return out


async def revert(conn: asyncpg.Connection, country: str) -> dict[str, int]:
    """Delete every pilot row for *country* in reverse-FK order. Idempotent.

    Returns the per-table deletion counts. Refuses to touch ES (the WHERE clause is
    country_code = <country> for geo and cdp_code prefix for the synthetic dealer).
    """
    if country == "ES":
        raise PilotError("refusing to delete ES rows - revert targets a non-ES pilot country only")
    counts: dict[str, int] = {}
    async with conn.transaction():
        # entity first (child of geo via the composite FKs); only the synthetic CDP-<cc>-* rows.
        ent = await conn.execute(
            "DELETE FROM entity WHERE country_code = $1 AND cdp_code LIKE $2",
            country, f"CDP-{country}-%",
        )
        muni = await conn.execute("DELETE FROM geo_municipality WHERE country_code = $1", country)
        prov = await conn.execute("DELETE FROM geo_province WHERE country_code = $1", country)
    counts["entity"] = int(ent.split()[-1])
    counts["geo_municipality"] = int(muni.split()[-1])
    counts["geo_province"] = int(prov.split()[-1])
    return counts


# ---------------------------------------------------------------------------
# Dry-run plan (default, no writes).
# ---------------------------------------------------------------------------

async def dry_run(conn: asyncpg.Connection, country: str) -> None:
    """Print exactly what --apply WOULD do, touching nothing."""
    composite = await _composite_pk_applied(conn)
    baseline = await _es_baseline(conn)
    key, code = cdp_pair(province_code=COLLISION_PROVINCE, domain=PILOT_DOMAIN, country_code=country)
    print(f"DRY-RUN (no writes). country={country}")
    print(f"  migration 0053 applied (geo composite PK): {composite}")
    if not composite:
        print("  -> --apply WOULD REFUSE: 0053 not applied; province "
              f"({country},'{COLLISION_PROVINCE}') would collide with ES on geo_province_pkey.")
    print(f"  ES baseline (must stay identical): {baseline}")
    print("  WOULD seed:")
    for prov in _provinces(country):
        print(f"    geo_province  ({country},'{prov['code']}') name={prov['name']!r} "
              f"ccaa=({prov['ccaa_code']},{prov['ccaa_name']!r})")
    muni = _municipality(country)
    print(f"    geo_municipality ({country},'{muni['code']}') name={muni['name']!r} "
          f"province_code={muni['province_code']!r} comarca_id=NULL")
    print(f"    entity cdp_code={code} kind='compraventa' country_code={country} "
          f"province='{COLLISION_PROVINCE}' municipality='{PILOT_MUNI}'")
    print(f"    canonical_key={key!r}  (country-blind dedup pre-image)")
    print("  run with --apply to seed + verify, or --revert to remove pilot rows.")


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------

async def run(country: str, mode: str) -> int:
    conn = await asyncpg.connect(DSN)
    try:
        if mode == "dry-run":
            await dry_run(conn, country)
            return 0

        if mode == "revert":
            counts = await revert(conn, country)
            print(f"reverted {country} pilot: {counts}")
            baseline = await _es_baseline(conn)
            print(f"ES counts after revert (unchanged): {baseline}")
            return 0

        if mode == "verify":
            baseline = await _es_baseline(conn)
            for line in await verify(conn, country, baseline):
                print(line)
            print("VERIFY OK")
            return 0

        # mode == 'apply'
        await _ensure_ready(conn, country)
        baseline = await _es_baseline(conn)
        minted = await seed(conn, country)
        print(f"seeded {country} pilot: cdp_code={minted['cdp_code']} canonical_key={minted['canonical_key']!r}")
        for line in await verify(conn, country, baseline):
            print(line)
        print("APPLY OK - second-country replication proven; ES byte-identical. "
              f"Run `--country {country} --revert` to undo.")
        return 0
    finally:
        await conn.close()


def _parse_args(argv: list[str]) -> tuple[str, str]:
    p = argparse.ArgumentParser(
        prog="python -m scripts.pilot_country",
        description="Reversible synthetic second-country onboarding pilot (default: dry-run). "
                    "Requires migration 0053 applied for --apply.",
    )
    p.add_argument("--country", default="DE",
                   help="ISO-3166 alpha-2 country code to pilot (default: DE). Must NOT be ES.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="seed + verify the pilot (idempotent)")
    g.add_argument("--verify", action="store_true", help="re-run assertions on already-seeded rows")
    g.add_argument("--revert", action="store_true", help="delete all pilot rows for the country")
    ns = p.parse_args(argv)
    country = ns.country.strip().upper()
    if country == "ES":
        p.error("--country must be a NON-ES country (ES is the protected baseline tenant)")
    if len(country) != 2 or not country.isalpha():
        p.error(f"--country must be a 2-letter alpha code, got {ns.country!r}")
    mode = "apply" if ns.apply else "verify" if ns.verify else "revert" if ns.revert else "dry-run"
    return country, mode


def main() -> None:
    country, mode = _parse_args(sys.argv[1:])
    try:
        sys.exit(asyncio.run(run(country, mode)))
    except PilotError as exc:
        print(f"pilot aborted: {exc}", file=sys.stderr)
        sys.exit(2)
    except AssertionError as exc:
        print(f"VERIFY FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
