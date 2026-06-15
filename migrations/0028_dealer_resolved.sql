-- 0028_dealer_resolved.sql — Dealer resolved view (B1 ∘ dedup).
--
-- PROBLEM: v_canonical exposes the B1 canonical layer (42,259 distinct canonical
-- dealers). The /health endpoint counts distinct canonical_cdp_code from
-- v_canonical, so it reports 42,259 instead of the true post-dedup count.
-- canonical_dedup (0027) fuses B1 canonicals sharing deep_links, reducing that
-- count to 40,016 distinct B1 dealers — only when a vam_verified run exists.
-- (Net B1 reduction is 2,243, not 2,385: n_merged includes 141 non-VAM graph
--  nodes that were never B1 canonicals. The old "42,259 - 2,385 = 39,874" was a
--  miscount; authoritative deduped count = 40,016, matching v_dealer_resolved.)
--
-- SOLUTION: v_dealer_resolved applies both layers in sequence:
--   1. B1 (v_canonical): maps every entity to its canonical cdp_code & ULID.
--      Entities absent from v_canonical are their own canonical (COALESCE to self).
--   2. dedup (canonical_dedup): maps each B1 canonical to its super-canonical
--      from the most recent vam_verified canonical_dedup_run. B1 canonicals not
--      involved in any merge remain unchanged (COALESCE to self).
--   Final join to entity resolves the super-canonical cdp_code to its ULID.
--
-- RESULT (measured 2026-06-15):
--   - Distinct resolved dealers: 368,944
--   Note: this is the full entity universe (368K total entities), most of which
--   are C2C/private sellers with no B1 canonical assignment. Dealer subset
--   (canonical entities only, kind=dealer) = 40,016 after dedup (verdict 1121).
--
-- NON-DESTRUCTIVE: does not alter v_canonical, canonical_dedup, or entity.
-- The view is a read-only projection; rollback drops only the view.
--
-- EFFICIENCY: CTEs allow the planner to materialise latest_run once per query.
-- No correlated subqueries per-row. Suitable for hot paths such as /health counts.

-- ---------------------------------------------------------------------------
-- v_dealer_resolved — two-layer resolved mapping for every entity
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_dealer_resolved AS
WITH latest_run AS (
    -- Anchor to the single most-recent vam_verified dedup run.
    -- If no verified run exists this CTE returns zero rows and the dedup
    -- LEFT JOIN produces NULLs everywhere -> COALESCE falls back to B1.
    SELECT run_id
    FROM canonical_dedup_run
    WHERE vam_verified = TRUE
    ORDER BY run_id DESC
    LIMIT 1
),
b1 AS (
    -- Layer 1: map every entity to its B1 canonical (from v_canonical).
    -- Entities not present in v_canonical are their own B1 canonical.
    SELECT
        e.entity_ulid,
        e.cdp_code,
        COALESCE(vc.canonical_cdp_code, e.cdp_code)  AS b1_cdp,
        COALESCE(vc.canonical_ulid,     e.entity_ulid) AS b1_ulid
    FROM entity e
    LEFT JOIN v_canonical vc ON vc.cdp_code = e.cdp_code
),
deduped AS (
    -- Layer 2: map B1 canonical to its super-canonical (from canonical_dedup).
    -- B1 canonicals absent from the dedup run stay as-is (COALESCE to b1_cdp).
    SELECT
        b1.entity_ulid,
        b1.cdp_code,
        COALESCE(cd.super_canonical_cdp_code, b1.b1_cdp) AS resolved_cdp_code
    FROM b1
    LEFT JOIN canonical_dedup cd
        ON  cd.canonical_cdp_code = b1.b1_cdp
        AND cd.run_id = (SELECT run_id FROM latest_run)
)
-- Final projection: resolve the super-canonical cdp_code to its ULID via entity.
SELECT
    d.entity_ulid,
    d.cdp_code,
    d.resolved_cdp_code,
    er.entity_ulid AS resolved_ulid
FROM deduped d
LEFT JOIN entity er ON er.cdp_code = d.resolved_cdp_code;

-- Rollback:
-- DROP VIEW IF EXISTS v_dealer_resolved;
