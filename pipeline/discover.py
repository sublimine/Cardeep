"""FASE 1 — DESCUBRIR.

Runs a SourceAdapter, geo-resolves each entity to INE codes, mints an immutable
cdp_code, and upserts entity + entity_source idempotently. Closes with a VAM
count quorum gate (source declared == fetched == DB-ingested).

Usage: python -m pipeline.discover dgt_cat
"""
from __future__ import annotations

import asyncio
import os
import sys

import asyncpg

from pipeline.geo import GeoResolver
from pipeline.ids import ulid
from pipeline.sources.base import DiscoveredEntity, SourceAdapter
from pipeline.sources.dgt_cat import DgtCatAdapter
from pipeline.verify import record_count_verdict
from services.api.codes import cdp_code

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

ADAPTERS: dict[str, type[SourceAdapter]] = {
    "dgt_cat": DgtCatAdapter,
}


async def _upsert(conn: asyncpg.Connection, geo: GeoResolver, e: DiscoveredEntity) -> tuple[bool, bool]:
    """Returns (entity_was_new, geo_resolved)."""
    prov = geo.province_code(e.province_name)
    muni = geo.municipality_code(prov, e.municipality_name)
    if not prov:
        # cannot mint a province-scoped code without a province; skip honestly
        return (False, False)
    code = cdp_code(province_code=prov, domain=e.website, cif=e.cif,
                    name=e.legal_name or e.trade_name, municipality_code=muni,
                    address=e.address)
    eulid = ulid()
    row = await conn.fetchrow(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae,
               province_code, municipality_code, address, postcode, lat, lon, phone, email,
               website, is_tier1, status, first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,'active',$18, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
           RETURNING (xmax = 0) AS inserted""",
        eulid, code, e.kind, e.legal_name, e.trade_name, e.cif, e.cnae,
        prov, muni, e.address, e.postcode, e.lat, e.lon, e.phone, e.email,
        e.website, e.is_tier1, e.source_key)
    # resolve the actual entity_ulid (may differ on conflict)
    real_ulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        real_ulid, e.source_key, e.source_ref)
    return (bool(row["inserted"]), muni is not None)


async def discover(source_key: str) -> None:
    adapter = ADAPTERS[source_key]()
    declared = adapter.declared_count()
    entities = adapter.fetch()
    print(f"[{source_key}] declared={declared} fetched={len(entities)}")

    conn = await asyncpg.connect(DSN)
    try:
        geo = await GeoResolver.load(conn)
        new = resolved = skipped = 0
        for e in entities:
            was_new, geo_ok = await _upsert(conn, geo, e)
            new += int(was_new)
            resolved += int(geo_ok)
            if not geo.province_code(e.province_name):
                skipped += 1
        in_db = await conn.fetchval(
            "SELECT count(*) FROM entity WHERE first_discovered_source=$1 AND kind='desguace'",
            source_key)
        muni_rate = resolved / len(entities) if entities else 0
        print(f"[{source_key}] new={new} in_db={in_db} skipped_no_province={skipped} "
              f"municipality_resolved={resolved}/{len(entities)} ({muni_rate:.1%})")

        verdict = await record_count_verdict(
            conn, subject_type="source", subject_key=source_key,
            claim="entity count == declared count",
            paths={"db_ingested": in_db, "fetched": len(entities),
                   "source_declared": declared},
            tolerance=0.0)
        print(f"[{source_key}] VAM verdict: {verdict}")
    finally:
        await conn.close()


def main() -> None:
    key = sys.argv[1] if len(sys.argv) > 1 else "dgt_cat"
    if key not in ADAPTERS:
        print(f"unknown source '{key}'. available: {list(ADAPTERS)}")
        sys.exit(2)
    asyncio.run(discover(key))


if __name__ == "__main__":
    main()
