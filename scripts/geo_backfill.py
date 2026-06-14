"""B4.3 — Reverse-geocode backfill: fill municipality_code in-place for entities
that have lat/lon or postcode but no municipality.

Strategy (applied in order per entity, first match wins):
  1. If lat IS NOT NULL AND lon IS NOT NULL:
     -> MunicipalityGeocoder.nearest_municipality(lat, lon, province_code)
     -> geocode_source = 'reverse_knn', geocode_precision = 'municipality'
  2. Elif postcode IS NOT NULL:
     -> PostcodeIndex.resolve(postcode)
     -> geocode_source = 'postcode', geocode_precision = 'municipality'
  3. Else: skip (cannot resolve without lat/lon or postcode).

PG MVCC doctrine: only UPDATE rows where municipality_code IS NULL and the
resolved code is non-null (i.e. genuinely mutated NULL -> code). The trigger
trg_entity_set_comarca fires on each UPDATE and closes comarca_id automatically.

Usage:
    python -m scripts.geo_backfill [--dry-run] [--sample N]

    --dry-run  : resolve but do not write to DB (for verification)
    --sample N : process only N entities (spot-check mode)
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Iterator

import asyncpg

from pipeline.geocode import MunicipalityGeocoder, PostcodeIndex

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Fetch entities in pages to avoid loading 80k rows in one shot.
_PAGE_SIZE: int = 2000


@dataclass(frozen=True)
class EntityRow:
    ulid: str
    kind: str
    lat: float | None
    lon: float | None
    postcode: str | None
    province_code: str | None


@dataclass
class Resolution:
    entity_ulid: str
    municipality_code: str
    geocode_source: str    # 'reverse_knn' | 'postcode'
    geocode_precision: str  # always 'municipality'
    distance_km: float | None  # set for reverse_knn, None for postcode


async def _fetch_gap_entities(
    conn: asyncpg.Connection,
    sample: int | None,
) -> list[EntityRow]:
    """Fetch all entity rows with municipality_code IS NULL that have lat/lon or postcode."""
    limit_clause = f"LIMIT {sample}" if sample else ""
    rows = await conn.fetch(f"""
        SELECT entity_ulid, kind, lat, lon, postcode, province_code
        FROM entity
        WHERE municipality_code IS NULL
          AND (
              (lat IS NOT NULL AND lon IS NOT NULL)
              OR postcode IS NOT NULL
          )
        ORDER BY entity_ulid
        {limit_clause}
    """)
    return [
        EntityRow(
            ulid=r["entity_ulid"],
            kind=r["kind"],
            lat=r["lat"],
            lon=r["lon"],
            postcode=r["postcode"],
            province_code=r["province_code"],
        )
        for r in rows
    ]


def _resolve_entities(
    entities: list[EntityRow],
    muni_geocoder: MunicipalityGeocoder,
    cp_index: PostcodeIndex,
) -> list[Resolution]:
    """Resolve municipality_code for each entity. Returns only successful resolutions."""
    results: list[Resolution] = []
    for ent in entities:
        resolved_code: str | None = None
        source: str = ""
        dist_km: float | None = None

        # Priority 1: lat/lon -> KNN reverse-geocode
        if ent.lat is not None and ent.lon is not None:
            code, dist = muni_geocoder.nearest_municipality(ent.lat, ent.lon, ent.province_code)
            if code:
                resolved_code = code
                source = "reverse_knn"
                dist_km = dist

        # Priority 2: postcode -> nomenclator lookup (only if lat/lon failed or missing)
        if resolved_code is None and ent.postcode:
            code = cp_index.resolve(ent.postcode)
            if code:
                resolved_code = code
                source = "postcode"

        if resolved_code:
            results.append(
                Resolution(
                    entity_ulid=ent.ulid,
                    municipality_code=resolved_code,
                    geocode_source=source,
                    geocode_precision="municipality",
                    distance_km=dist_km,
                )
            )
    return results


def _pages(items: list[Resolution], size: int) -> Iterator[list[Resolution]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


async def _apply_resolutions(
    conn: asyncpg.Connection,
    resolutions: list[Resolution],
) -> int:
    """Write resolved municipality_codes to DB. Returns count of rows updated."""
    if not resolutions:
        return 0

    updated = 0
    for page in _pages(resolutions, _PAGE_SIZE):
        # Build typed parameter arrays for bulk UPDATE
        ulids = [r.entity_ulid for r in page]
        codes = [r.municipality_code for r in page]
        sources = [r.geocode_source for r in page]
        precisions = [r.geocode_precision for r in page]

        # Unnest-based bulk UPDATE: only touches rows where municipality_code IS NULL
        # (guards against races or partial reruns). The trigger trg_entity_set_comarca
        # fires per row and closes comarca_id automatically.
        result = await conn.execute("""
            UPDATE entity e
            SET
                municipality_code = upd.muni_code,
                geocode_source     = upd.src,
                geocode_precision  = upd.prec
            FROM (
                SELECT
                    unnest($1::text[])    AS entity_ulid,
                    unnest($2::char(5)[]) AS muni_code,
                    unnest($3::text[])    AS src,
                    unnest($4::text[])    AS prec
            ) upd
            WHERE e.entity_ulid = upd.entity_ulid
              AND e.municipality_code IS NULL
        """, ulids, codes, sources, precisions)
        # asyncpg returns 'UPDATE N'
        n = int(result.split()[-1])
        updated += n

    return updated


async def main(dry_run: bool, sample: int | None) -> None:
    conn = await asyncpg.connect(DSN)
    try:
        # ---- Baseline count ----
        baseline = await conn.fetchrow("""
            SELECT
                count(*) FILTER (WHERE municipality_code IS NULL) AS gap_before,
                count(*) AS total
            FROM entity
        """)
        print(f"Baseline — total: {baseline['total']}, gap: {baseline['gap_before']}")

        # ---- Load geocoders ----
        print("Loading MunicipalityGeocoder from geo_municipality centroids...")
        muni_geocoder = await MunicipalityGeocoder.load(conn)
        print(
            f"  Loaded {muni_geocoder.centroid_count()} centroids "
            f"across {muni_geocoder.province_count()} provinces."
        )

        print("Loading PostcodeIndex from INE Nomenclátor...")
        cp_index = PostcodeIndex.load()
        print(
            f"  Unambiguous CPs: {cp_index.size_unambiguous()}, "
            f"Ambiguous (rejected): {cp_index.size_ambiguous()}"
        )

        # ---- Fetch gap entities ----
        print(f"Fetching gap entities (municipality_code IS NULL with lat/lon or postcode)...")
        entities = await _fetch_gap_entities(conn, sample)
        print(f"  Gap entities to process: {len(entities)}")

        if not entities:
            print("Nothing to resolve — gap is already zero for the actionable set.")
            return

        # ---- Resolve ----
        print("Resolving...")
        resolutions = _resolve_entities(entities, muni_geocoder, cp_index)

        resolved_knn = [r for r in resolutions if r.geocode_source == "reverse_knn"]
        resolved_cp = [r for r in resolutions if r.geocode_source == "postcode"]
        unresolved = len(entities) - len(resolutions)

        print(f"  Resolved via reverse_knn: {len(resolved_knn)}")
        print(f"  Resolved via postcode:    {len(resolved_cp)}")
        print(f"  Unresolved (threshold/ambiguity): {unresolved}")

        if dry_run:
            print("\n[DRY RUN] — no DB writes performed.")
            # Print sample cases
            print("\nSample resolutions (up to 20):")
            for r in resolutions[:20]:
                dist_str = f" dist={r.distance_km:.2f}km" if r.distance_km is not None else ""
                print(f"  entity={r.entity_ulid} -> {r.municipality_code} "
                      f"via {r.geocode_source}{dist_str}")
            return

        # ---- Apply ----
        print("Applying updates to DB...")
        async with conn.transaction():
            updated = await _apply_resolutions(conn, resolutions)
        print(f"  DB rows updated: {updated}")

        # ---- Post-count ----
        post = await conn.fetchrow("""
            SELECT count(*) FILTER (WHERE municipality_code IS NULL) AS gap_after
            FROM entity
        """)
        print(
            f"\nResult — gap before: {baseline['gap_before']}, "
            f"gap after: {post['gap_after']}, "
            f"closed: {baseline['gap_before'] - post['gap_after']}"
        )

        # ---- By kind ----
        kind_rows = await conn.fetch("""
            SELECT kind,
                   count(*) FILTER (WHERE geocode_source IN ('reverse_knn','postcode')
                                    AND municipality_code IS NOT NULL) AS closed_this_run
            FROM entity
            WHERE geocode_source IN ('reverse_knn', 'postcode')
            GROUP BY kind ORDER BY closed_this_run DESC
        """)
        print("\nClosed by kind:")
        for kr in kind_rows:
            print(f"  {kr['kind']}: {kr['closed_this_run']}")

        # ---- Sample cases for manual validation ----
        if resolved_knn:
            print("\nSample reverse_knn resolutions (up to 20 for manual spot-check):")
            # Use actual distances from resolution
            sample_cases = sorted(resolved_knn[:20], key=lambda r: r.distance_km or 0)
            for r in sample_cases:
                print(
                    f"  entity={r.entity_ulid} -> muni={r.municipality_code} "
                    f"dist={r.distance_km:.2f}km via reverse_knn"
                )

    finally:
        await conn.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Resolve but do not write to DB")
    parser.add_argument("--sample", type=int, default=None,
                        help="Limit to N entities (spot-check mode)")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(main(dry_run=args.dry_run, sample=args.sample))
