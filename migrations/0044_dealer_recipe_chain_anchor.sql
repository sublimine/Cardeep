-- 0044_dealer_recipe_chain_anchor.sql — fix v_dealer_recipe recipe-coverage under-report (audit SU-A5).
-- The connector_source_keys CTE (0029) INTENDED to recognise VO-chain heads (flexicar/carplus/
-- clicars/ocasionplus) as connector sources (see its own comment), but its kind list was
-- ('compraventa','importador') with role IN ('chain','standalone_pos') — and the Flexicar national
-- anchor is kind='cadena' (a residual of the SU-0.5 chain→organization reassignment), so it was
-- MISSED. Result: 186 Flexicar dealers (+ other chain heads) with served inventory were wrongly
-- classified recipe_kind='none' despite being fully connector-covered, under-reporting recipe
-- coverage and failing G3-completion + evict Gate-2 for them.
--
-- Fix: recognise ANY national (province_code IS NULL) entity with role='chain' as a connector
-- source — a chain head IS connector-covered regardless of its kind. This is additive and cannot
-- over-broaden: role='chain' is only ever a chain anchor (created by a connector). Reporting view
-- only — does NOT touch the dealer count or the seal numerator.
-- NOTE (still open, separate fix): connectors WITHOUT any national anchor (family_*, rentacar_vo_*,
-- aecs — ~76 dealers) cannot be recognised by this anchor-heuristic at all; the robust fix is a
-- connector REGISTRY (source_key→connector). Tracked in SUPERPLAN §A5 / GitHub #11.
--
-- Idempotent (CREATE OR REPLACE). Reversible (restore the 0029 view).

CREATE OR REPLACE VIEW v_dealer_recipe AS
WITH
connector_source_keys AS (
    SELECT DISTINCT es.source_key
    FROM entity_source es
    JOIN entity e ON e.entity_ulid = es.entity_ulid
    WHERE e.province_code IS NULL
      AND (
        e.kind IN ('plataforma', 'oem_vo_portal', 'subasta')
        OR (e.kind IN ('compraventa', 'importador')
            AND e.role IN ('chain', 'standalone_pos'))
        OR e.role = 'chain'   -- NEW: chain heads regardless of kind (Flexicar anchor is kind='cadena')
      )
),
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
        CASE
            WHEN sd.recipe_version IS NOT NULL THEN 1
            WHEN csk.source_key IS NOT NULL    THEN 2
            ELSE                                    3
        END AS rank
    FROM served_dealers sd
    LEFT JOIN connector_source_keys csk ON csk.source_key = sd.source_key
),
best_per_dealer AS (
    SELECT DISTINCT ON (entity_ulid)
        entity_ulid,
        cdp_code,
        source_key,
        recipe_kind,
        recipe_ref
    FROM classified
    ORDER BY entity_ulid, rank, source_key
)
SELECT
    entity_ulid,
    cdp_code,
    source_key,
    recipe_kind,
    recipe_ref
FROM best_per_dealer;

-- Rollback (restore 0029: remove the `OR e.role = 'chain'` clause from connector_source_keys):
-- (re-apply migrations/0029_dealer_recipe.sql's view definition)
