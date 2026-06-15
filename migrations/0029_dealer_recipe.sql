-- 0029_dealer_recipe.sql — Dealer recipe coverage view.
--
-- PROBLEM: The field `recipe_version` in entity is only populated for the 537 per-dealer AS24
-- recipes (the ones written by harvest_dealer.py via pipeline/recipe.py). The remaining ~97.5%
-- of served dealers are covered by connector-level recipes (sentinel-00 platform entities with a
-- YAML in countries/ES/recipes/), but recipe_version=NULL for all of them — a misleading signal.
-- This makes recipe coverage UNAUDITABLE from the DB alone.
--
-- SOLUTION: v_dealer_recipe is a READ-ONLY view that maps every served dealer (entity with
-- kind != 'particular' and >= 1 available vehicle) to its recipe classification:
--
--   per_dealer : entity.recipe_version IS NOT NULL (the AS24 cohort: 537 dealers)
--   connector  : the dealer's source_key is served by a connector that has a sentinel-00
--                entity in DB (kind IN plataforma/oem_vo_portal/subasta, OR kind IN
--                compraventa/importador with role IN chain/standalone_pos for VO-chain heads),
--                i.e. a connector recipe exists. recipe_ref = the source_key of that connector.
--   none       : neither (directory sources: osm/acevas/aecs/aedra/geo_sweep, or other
--                discovery-only sources with no connector recipe). ~88 dealers.
--
-- KEY DESIGN DECISIONS:
--   1. This is a VIEW (not a table, not an UPDATE) — MVCC-safe: zero writes to entity rows.
--   2. The connector detection is purely relational: a source_key has a connector recipe iff
--      there exists an entity_source row pointing to a sentinel-00 entity whose kind is
--      'plataforma' or 'oem_vo_portal'. No filesystem check needed.
--   3. When a dealer has MULTIPLE source_key entries, the highest-priority kind wins:
--      per_dealer > connector > none (CASE precedence in GREATEST-style ordering).
--   4. Columns: entity_ulid, cdp_code, source_key, recipe_kind, recipe_ref.
--      recipe_ref = NULL for per_dealer (the recipe file IS the cdp_code.yaml),
--                   source_key for connector,
--                   NULL for none.
--
-- AUDIT QUERY (after apply):
--   SELECT recipe_kind, count(*), sum(veh_count)
--   FROM v_dealer_recipe
--   GROUP BY 1;
--   Expected: connector ~97.5%, per_dealer ~1.4%, none ~0.2%.
--
-- NON-DESTRUCTIVE: This migration only creates a view. Rollback drops the view only.
-- No entity rows are touched; recipe_version is left as-is (NULL = connector-covered).

-- ---------------------------------------------------------------------------
-- Connector recipe set: source_keys that have a sentinel-00 platform entity in DB.
-- A sentinel-00 platform entity (province_code IS NULL, kind IN plataforma/oem_vo_portal)
-- is the DB-resident marker that a connector recipe exists for that source_key.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_dealer_recipe AS
WITH

-- Step 1: Build the set of source_keys that have a connector recipe.
-- A connector recipe exists for source_key S iff there exists a sentinel-00 entity
-- (province_code IS NULL) whose role indicates it acts as a connector-level node:
--   - kind IN ('plataforma','oem_vo_portal','subasta') : dedicated platform entities
--   - kind IN ('compraventa','importador') AND role IN ('chain','standalone_pos') :
--     VO-chain heads (flexicar/carplus/clicars/ocasionplus) and importers (modrive)
--     that have a sentinel-00 entity in DB with a connector YAML on disk.
-- This correctly classifies all dealers served via a connector (vs directory-only dealers).
connector_source_keys AS (
    SELECT DISTINCT es.source_key
    FROM entity_source es
    JOIN entity e ON e.entity_ulid = es.entity_ulid
    WHERE e.province_code IS NULL
      AND (
        e.kind IN ('plataforma', 'oem_vo_portal', 'subasta')
        OR (e.kind IN ('compraventa', 'importador')
            AND e.role IN ('chain', 'standalone_pos'))
      )
),

-- Step 2: All served dealers (kind != 'particular', >= 1 available vehicle).
-- One row per distinct (dealer entity, source_key) pair so multi-source dealers
-- each appear once per source_key, then we fold to the best recipe_kind below.
served_dealers AS (
    SELECT DISTINCT
        e.entity_ulid,
        e.cdp_code,
        e.recipe_version,
        es.source_key
    FROM entity e
    JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'
    JOIN entity_source es ON es.entity_ulid = e.entity_ulid
    WHERE e.kind <> 'particular'
),

-- Step 3: Classify each (dealer, source_key) pair.
-- Priority: per_dealer (recipe_version IS NOT NULL) > connector > none.
classified AS (
    SELECT
        sd.entity_ulid,
        sd.cdp_code,
        sd.source_key,
        CASE
            WHEN sd.recipe_version IS NOT NULL THEN 'per_dealer'
            WHEN csk.source_key IS NOT NULL    THEN 'connector'
            ELSE                                    'none'
        END AS recipe_kind,
        CASE
            WHEN sd.recipe_version IS NOT NULL THEN NULL
            WHEN csk.source_key IS NOT NULL    THEN sd.source_key
            ELSE                                    NULL
        END AS recipe_ref,
        -- rank for dedup: per_dealer=1 (best), connector=2, none=3
        CASE
            WHEN sd.recipe_version IS NOT NULL THEN 1
            WHEN csk.source_key IS NOT NULL    THEN 2
            ELSE                                    3
        END AS rank
    FROM served_dealers sd
    LEFT JOIN connector_source_keys csk ON csk.source_key = sd.source_key
),

-- Step 4: For dealers with multiple source_keys, keep the best-ranked recipe_kind.
-- (e.g. a dealer discovered via osm AND also via coches_net_wholesale -> connector wins)
best_per_dealer AS (
    SELECT DISTINCT ON (entity_ulid)
        entity_ulid,
        cdp_code,
        source_key,
        recipe_kind,
        recipe_ref
    FROM classified
    ORDER BY entity_ulid, rank, source_key  -- deterministic: rank ASC, then source_key for ties
)

SELECT
    entity_ulid,
    cdp_code,
    source_key,
    recipe_kind,
    recipe_ref
FROM best_per_dealer;

-- Rollback:
-- DROP VIEW IF EXISTS v_dealer_recipe;
