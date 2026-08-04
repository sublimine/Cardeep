"""Rebuild search_cube by atomic swap (plan Bloque 1.1).

Builds sibling tables, indexes and analyses them, then swaps them in inside one
transaction. Readers see the old cube until the instant they see the new one, and
the operation leaves ZERO dead tuples — which `REFRESH MATERIALIZED VIEW
CONCURRENTLY` cannot say, because it merges with UPDATE/DELETE.

Three tables come out of one snapshot:
  search_cube      — counts at make x model x submodel x province x year x km_bucket
  search_submodel  — the versions filed under each model, for the picker's 3rd level
  search_cube_meta — one row: when this was computed, so the counter can say so

Run:  python scripts/build_search_cube.py
      python scripts/build_search_cube.py --dry-run    # build and measure, no swap
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import asyncpg

# Run as `python scripts/build_search_cube.py` as well as `python -m scripts...`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"

# ---------------------------------------------------------------------------
# Marque resolution, including sub-brands that fold into a parent
# ---------------------------------------------------------------------------
# `make_canon.successor_slug` already existed for rebrands (SsangYong -> KGM). It
# does double duty here for SUB-BRANDS, and the reason is the buyer, not the
# corporate chart: someone shopping for an AMG looks under Mercedes-Benz, and a
# picker that files it under a separate "Mercedes-AMG" entry hides stock from the
# person most likely to buy it. Anything with a successor resolves to that
# successor and stops being a listable marque of its own.
#
# Two hops, not one: a chain like Maybach -> Mercedes-AMG -> Mercedes-Benz has to
# land on the parent, and two levels covers every case in this registry. It is
# capped deliberately rather than made recursive — an unbounded walk over data
# someone can edit is a cycle waiting to hang the build.
MAKE_RESOLVED_SQL = """
CREATE TEMP TABLE make_resolved AS
SELECT mc.slug,
       mc.norm_key,
       coalesce(p2.display_name, p1.display_name, mc.display_name) AS display_name
  FROM make_canon mc
  LEFT JOIN make_canon p1 ON p1.slug = mc.successor_slug
  LEFT JOIN make_canon p2 ON p2.slug = p1.successor_slug
"""

MAKE_RESOLVED_INDEX = "CREATE INDEX ON make_resolved (norm_key)"

# ---------------------------------------------------------------------------
# Model canonicalisation
# ---------------------------------------------------------------------------
# Model spellings fragment exactly the way marque spellings did. The picker showed
# "Leon" beside "León", "Qashqai" beside "QASHQAI", "Tucson" beside "TUCSON" and
# "Clase GLA" beside "GLA" — one car split across rows, each carrying a fraction of
# its real count. `make_canon` fixed this for brands; models had no equivalent.
#
# The key strips accents, case and punctuation, plus the Spanish "Clase " prefix
# that some sources write for Mercedes models and others omit. The DISPLAY spelling
# is never invented: it is whichever real spelling the census uses most often for
# that key, so every label on screen is something a source actually wrote.
MODEL_MAP_SQL = """
CREATE TEMP TABLE model_map AS
WITH raw AS (
    SELECT coalesce(mc.display_name, btrim(v.make), '') AS make,
           btrim(v.model)                               AS model,
           count(*)                                     AS n
      FROM v_canonical_vehicle vc
      JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
      JOIN entity e           ON e.entity_ulid = v.entity_ulid
      LEFT JOIN make_alias ma ON ma.alias_norm = make_norm(v.make)
      LEFT JOIN make_resolved mc ON mc.slug = ma.canon_slug
     WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
       AND v.status = 'available'
       AND e.country_code = 'ES'
       AND v.model IS NOT NULL AND btrim(v.model) <> ''
     GROUP BY 1, 2
), keyed AS (
    SELECT make, model, n, model_key(model) AS mkey
      FROM raw
)
SELECT DISTINCT ON (make, mkey) make, mkey, model AS display
  FROM keyed
 WHERE mkey <> ''
 ORDER BY make, mkey, n DESC, model
"""

MODEL_MAP_INDEX = "CREATE INDEX ON model_map (make, mkey)"

# ---------------------------------------------------------------------------
# Version families
# ---------------------------------------------------------------------------
# The raw version strings are a transcript, not a list of choices: 106.246 distinct
# values, 51,9% of them appearing exactly once. Collapsing them into families is
# done in Python rather than SQL because the rule is three different rules — German
# premium, VAG and PSA/Renault name their cars in incompatible ways — and expressing
# that as nested CASE WHEN would be unreadable and unmaintainable.
#
# The mapping is computed once per build over the distinct triples (a few tens of
# thousands of rows), loaded into a temp table, and joined. Nothing runs per-car.
VERSION_FAMILY_DDL = """
CREATE TEMP TABLE version_family (
    make      text NOT NULL,
    model     text NOT NULL,
    submodel  text NOT NULL,
    family    text NOT NULL
)
"""

VERSION_FAMILY_INDEX = "CREATE INDEX ON version_family (make, model, submodel)"

# The distinct triples the extractor has to classify, already canonicalised so the
# families attach to the same make/model strings the cube will use.
VERSION_SOURCE_SQL = """
SELECT DISTINCT
       coalesce(mc.display_name, btrim(v.make), '') AS make,
       coalesce(mm.display, btrim(v.model), '')     AS model,
       btrim(raw.trim)                              AS submodel
  FROM v_canonical_vehicle vc
  JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
  JOIN vehicle raw        ON raw.vehicle_ulid = v.vehicle_ulid
  JOIN entity e           ON e.entity_ulid = v.entity_ulid
  LEFT JOIN make_alias ma ON ma.alias_norm = make_norm(v.make)
  LEFT JOIN make_resolved mc ON mc.slug = ma.canon_slug
  LEFT JOIN model_map mm  ON mm.make = coalesce(mc.display_name, btrim(v.make), '')
                         AND mm.mkey = model_key(v.model)
 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
   AND v.status = 'available'
   AND e.country_code = 'ES'
   AND raw.trim IS NOT NULL AND btrim(raw.trim) <> ''
"""

# ---------------------------------------------------------------------------
# The cube
# ---------------------------------------------------------------------------
# ONE ROW PER PHYSICAL CAR, not per listing.
#
# The grain matters more than anything else in this file. A first version counted
# raw `vehicle` rows and totalled 2,510,953, while /stats — which the hero quotes —
# said 1,484,687. Both were correct and they measured different things: the census
# holds the same car several times when several portals list it, and `/stats`
# collapses those through `v_canonical_vehicle`. Shipping both numbers on one screen
# would have put two contradictory totals in front of one visitor, and the search
# behind the button would have offered the same car three times.
#
# The marque is likewise stored CANONICAL rather than as the census spelled it:
# grouping by the raw string put three identically-labelled "Mercedes-Benz" rows in
# the picker — 115.360, 882 and 39 — with no way to know which to click.
BUILD_SQL = """
-- COLOUR, BODY TYPE AND is_family ARE DIMENSIONS, not decoration.
--
-- The parser resolves "coche rojo grande de familia en Sevilla" into colour +
-- is_family + province, and the panel shows all three as chips. With only province
-- in the cube, the button answered 83.159 — the count for Sevilla alone — under
-- chips promising a red family car. A number larger than the truth, printed beside
-- the conditions it ignores, is the precise failure this whole build exists to
-- prevent, and wiring the parser to the counter is what introduced it.
--
-- Cost is asymmetric and worth knowing: body_type and is_family are functionally
-- dependent on make+model, so they add ZERO rows — every row in a group already
-- shares them. Only colour genuinely splits groups, and it is populated on 11% of
-- the index, so the '' bucket absorbs the rest.
CREATE TABLE search_cube_next AS
SELECT coalesce(mc.display_name, btrim(v.make), '') AS make,
       coalesce(mm.display, btrim(v.model), '')     AS model,
       coalesce(vf.family, '')                      AS submodel,
       coalesce(raw.color, '')                      AS color,
       coalesce(mat.body_type, '')                  AS body_type,
       coalesce(mat.is_family, false)               AS is_family,
       coalesce(mat.seats, 0)::smallint             AS seats,
       fuel_norm(v.fuel)                            AS fuel,
       e.province_code,
       v.year::smallint                             AS year,
       km_bucket_of(v.km)                           AS km_bucket,
       price_bucket_of(v.price)                     AS price_bucket,
       count(*)::int                                AS n
  FROM v_canonical_vehicle vc
  JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
  JOIN vehicle raw        ON raw.vehicle_ulid = v.vehicle_ulid
  JOIN entity e           ON e.entity_ulid = v.entity_ulid
  LEFT JOIN make_alias ma ON ma.alias_norm = make_norm(v.make)
  LEFT JOIN make_resolved mc ON mc.slug = ma.canon_slug
  LEFT JOIN model_map mm  ON mm.make = coalesce(mc.display_name, btrim(v.make), '')
                         AND mm.mkey = model_key(v.model)
  LEFT JOIN version_family vf ON vf.make = coalesce(mc.display_name, btrim(v.make), '')
                             AND vf.model = coalesce(mm.display, btrim(v.model), '')
                             AND vf.submodel = btrim(raw.trim)
  LEFT JOIN model_attributes mat
         ON mat.make_raw = coalesce(mc.display_name, btrim(v.make), '')
        AND mat.model    = coalesce(mm.display, btrim(v.model), '')
 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
   AND v.status = 'available'
   AND e.country_code = 'ES'
 GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
"""

# The third level of the picker: the versions actually filed under each model.
#
# Source is `vehicle.trim`, back-filled from the connectors' own `version` field
# (scripts/backfill_attributes.py) rather than parsed out of the title — 44.3% of
# available cars carry one, and what they carry is exactly what the cascade needs:
# "C 220 d", "C 200 d Estate", "Coupé C 220 d".
#
# `trim` is read from `vehicle`, not from `servable_vehicle`: that view carries an
# explicit nineteen-column list written before migration 0098 added the attribute
# columns, so `servable_vehicle.trim` does not exist. Widening the view would touch
# every one of its consumers for the benefit of this one query.
SUBMODEL_SQL = """
CREATE TABLE search_submodel_next AS
SELECT coalesce(mc.display_name, btrim(v.make), '') AS make,
       coalesce(mm.display, btrim(v.model), '')     AS model,
       vf.family                                    AS submodel,
       count(*)::int                                AS n
  FROM v_canonical_vehicle vc
  JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
  JOIN vehicle raw        ON raw.vehicle_ulid = v.vehicle_ulid
  JOIN entity e           ON e.entity_ulid = v.entity_ulid
  LEFT JOIN make_alias ma ON ma.alias_norm = make_norm(v.make)
  LEFT JOIN make_resolved mc ON mc.slug = ma.canon_slug
  LEFT JOIN model_map mm  ON mm.make = coalesce(mc.display_name, btrim(v.make), '')
                         AND mm.mkey = model_key(v.model)
  LEFT JOIN version_family vf ON vf.make = coalesce(mc.display_name, btrim(v.make), '')
                             AND vf.model = coalesce(mm.display, btrim(v.model), '')
                             AND vf.submodel = btrim(raw.trim)
 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
   AND v.status = 'available'
   AND e.country_code = 'ES'
   AND raw.trim IS NOT NULL AND btrim(raw.trim) <> ''
   AND v.make IS NOT NULL AND btrim(v.make) <> ''
   AND v.model IS NOT NULL AND btrim(v.model) <> ''
 GROUP BY 1, 2, 3
"""

INDEX_SQL = [
    "CREATE INDEX idx_search_cube_next_make ON search_cube_next (make, model, submodel, province_code, year) INCLUDE (n, km_bucket, price_bucket, color, body_type, is_family, seats, fuel)",
    # The natural-language lane arrives with no marque at all — "SUV híbrido por
    # menos de 20.000 €" is body + fuel + price and nothing else — so it needs an
    # entry point that does not start from a brand.
    "CREATE INDEX idx_search_cube_next_attrs ON search_cube_next (body_type, fuel, color, province_code) INCLUDE (n, is_family, seats, year, km_bucket, price_bucket)",
    "CREATE INDEX idx_search_cube_next_prov ON search_cube_next (province_code, year) INCLUDE (n, make, km_bucket)",
    "CREATE INDEX idx_search_submodel_next ON search_submodel_next (make, model, n DESC)",
]

SWAP_SQL = """
DROP TABLE IF EXISTS search_cube;
ALTER TABLE search_cube_next RENAME TO search_cube;
ALTER INDEX idx_search_cube_next_make RENAME TO idx_search_cube_make;
ALTER INDEX idx_search_cube_next_prov RENAME TO idx_search_cube_prov;
ALTER INDEX idx_search_cube_next_attrs RENAME TO idx_search_cube_attrs;
DROP TABLE IF EXISTS search_submodel;
ALTER TABLE search_submodel_next RENAME TO search_submodel;
ALTER INDEX idx_search_submodel_next RENAME TO idx_search_submodel;
"""

# Byte-for-byte the query services/api/stats.py uses for
# `vehicles_unique_available`. Reconciling against the definition the rest of the
# product already publishes is the whole point: if the two ever diverge, the build
# refuses to swap rather than publishing a number nobody can defend.
TRUTH_SQL = """
SELECT count(*)
  FROM v_canonical_vehicle vc
  JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
  JOIN entity e ON e.entity_ulid = v.entity_ulid
 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
   AND v.status = 'available'
   AND e.country_code = 'ES'
"""


async def main(dry_run: bool = False) -> None:
    conn = await asyncpg.connect(DSN, command_timeout=3600)
    try:
        await conn.execute("DROP TABLE IF EXISTS search_cube_next")
        await conn.execute("DROP TABLE IF EXISTS search_submodel_next")

        # REPEATABLE READ, and the reconciliation query lives INSIDE it.
        #
        # The first attempt built the cube and then counted the source table
        # afterwards, and reported a 4,160-row discrepancy. The cube was not wrong:
        # the census is live, the build takes minutes, and in that window real cars
        # sold and flipped to 'gone'. Comparing a snapshot against a later moment
        # measures elapsed time, not correctness. One snapshot for all of it makes
        # the check mean what it claims to.
        t0 = time.monotonic()
        async with conn.transaction(isolation="repeatable_read"):
            await conn.execute(MAKE_RESOLVED_SQL)
            await conn.execute(MAKE_RESOLVED_INDEX)
            await conn.execute(MODEL_MAP_SQL)
            await conn.execute(MODEL_MAP_INDEX)

            # Classify the distinct version strings in Python, then load the result
            # back. This is the only step that leaves the database, and it runs over
            # tens of thousands of triples rather than millions of cars.
            from pipeline.search.version_family import family_of

            triples = await conn.fetch(VERSION_SOURCE_SQL)
            await conn.execute(VERSION_FAMILY_DDL)
            rows = [
                (r["make"], r["model"], r["submodel"], fam)
                for r in triples
                if (fam := family_of(r["make"], r["model"], r["submodel"]))
            ]
            await conn.copy_records_to_table("version_family", records=rows)
            await conn.execute(VERSION_FAMILY_INDEX)
            # ANALYZE on every temp table, and it is not optional.
            #
            # A freshly created temp table has no statistics at all, so the planner
            # assumes a default row count and joins it against 1,48 M cars however
            # it likes. Adding the family lookup without this pushed the build past
            # ten minutes; the tables are small and analysing them costs seconds.
            for tmp in ("make_resolved", "model_map", "version_family"):
                await conn.execute(f"ANALYZE {tmp}")
            print(f"familias: {len(rows):,} versiones clasificadas "
                  f"-> {len({r[3] for r in rows}):,} familias distintas")
            await conn.execute(BUILD_SQL)
            await conn.execute(SUBMODEL_SQL)
            truth = await conn.fetchval(TRUTH_SQL)
        build_s = time.monotonic() - t0

        rows = await conn.fetchval("SELECT count(*) FROM search_cube_next")
        vehicles = await conn.fetchval("SELECT sum(n) FROM search_cube_next")
        subs = await conn.fetchval("SELECT count(*) FROM search_submodel_next")

        t1 = time.monotonic()
        for sql in INDEX_SQL:
            await conn.execute(sql)
        await conn.execute("ANALYZE search_cube_next")
        await conn.execute("ANALYZE search_submodel_next")
        index_s = time.monotonic() - t1

        size = await conn.fetchval("SELECT pg_size_pretty(pg_total_relation_size('search_cube_next'))")

        print(f"cube: {rows:,} filas | {size} | build {build_s:.1f}s | index+analyze {index_s:.1f}s")
        print(f"submodelos: {subs:,} filas")
        print(f"suma n = {vehicles:,} | fuente = {truth:,} | {'OK' if vehicles == truth else 'DESCUADRE'}")

        if vehicles != truth:
            print("ABORTADO: el cubo no cuadra con la fuente. No se hace swap.")
            await conn.execute("DROP TABLE IF EXISTS search_cube_next")
            await conn.execute("DROP TABLE IF EXISTS search_submodel_next")
            return

        if dry_run:
            print("\nDRY-RUN — construido y verificado, sin swap.")
            await conn.execute("DROP TABLE IF EXISTS search_cube_next")
            await conn.execute("DROP TABLE IF EXISTS search_submodel_next")
            return

        async with conn.transaction():
            await conn.execute(SWAP_SQL)
            await conn.execute(
                """
                INSERT INTO search_cube_meta (only_row, computed_at, rows_in_cube, vehicles)
                VALUES (true, now(), $1, $2)
                ON CONFLICT (only_row) DO UPDATE
                   SET computed_at = now(), rows_in_cube = $1, vehicles = $2
                """, rows, vehicles)
        print("SWAP hecho.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main(dry_run="--dry-run" in sys.argv))
