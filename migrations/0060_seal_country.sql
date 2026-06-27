-- 0060_seal_country.sql — thread the country dimension through the two CERTIFICATE seal views
-- (generic-engine vector #5 / PROJECT 360-B): the LAST country-blind SERVED surface after the
-- dealer census got country_code in 0058. /geo/seal reads v_province_seal (0042+0043) and
-- /geo/exhaustiveness reads v_exhaustiveness_seal (0048); both were keyed by province_code ALONE,
-- so sealing a 2nd tenant that REUSES the same numeric province/municipality code space (0053 puts
-- DE province '28' next to ES Madrid '28') would POOL both countries into one numerator — a Spanish
-- seal silently counting German dealers. This makes each seal belong to exactly ONE country.
--
-- THE INVARIANT (non-negotiable): DEFAULT 'ES' => byte-identical for today's sole tenant. Every
-- existing row is ES, so the per-country GROUP BY / JOIN / filter collapses to the historical result.
--
-- WHY ADDITIVE / FK-SAFE / REVERSIBLE:
--   1. v_province_seal — its bases ALREADY carry country_code: entity (0052) and
--      denominator_estimate (0053). Country is PROPAGATED, never invented: the CTEs group by
--      (province_code, country_code) and the venta branch joins the registral ceiling on BOTH keys.
--      CREATE OR REPLACE keeps the 6 existing columns (province_code, segment, denominator, numerator,
--      coverage_pct, verdict) in order and APPENDS country_code (7th) — invisible to the explicit-column
--      readers (services/api/routers/geo.py, tests/test_province_seal_view.py).
--   2. exhaustiveness_estimate (0048) had NO country dimension, so we ADD country_code CHAR(2) NOT NULL
--      DEFAULT 'ES' — the exact pattern denominator_estimate used in 0053. The DEFAULT backfills every
--      existing row to 'ES' atomically (zero-NULL, no constraint violation possible). pipeline/
--      exhaustiveness/seal.py's INSERT omits the column, so new ES rows default to 'ES' too — a
--      per-country build sets it explicitly when a 2nd tenant exists.
--   3. v_exhaustiveness_seal — PROJECTS e.country_code (appended 17th, after created_at) and its
--      `latest` CTE becomes PER-COUNTRY (DISTINCT ON (country_code)): a newer second-country build can
--      no longer evict the ES certificate via the old single global `LIMIT 1`. Single-country => the
--      one latest build per country IS the global latest => byte-identical row set.
--
-- A view touches no row, no FK, no served cdp_code; idempotent (ADD COLUMN IF NOT EXISTS, CREATE OR
-- REPLACE); fully reversible (the Rollback section restores the pre-0060 column + view bodies). The
-- runner wraps this file in one transaction, so all four statements apply atomically.

-- 1. The missing tenant dimension on the exhaustiveness base table (DEFAULT 'ES' backfills all rows).
ALTER TABLE exhaustiveness_estimate
    ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

CREATE INDEX IF NOT EXISTS ix_exhaustiveness_country
    ON exhaustiveness_estimate (country_code, build_run_id);

-- 2. v_province_seal — country-keyed VENTA + DESGUACE seal (country propagated from entity +
--    denominator_estimate). Columns 1-6 are byte-identical to 0043; country_code is appended 7th.
CREATE OR REPLACE VIEW v_province_seal AS
WITH venta_num AS (
    SELECT e.province_code,
           e.country_code,
           count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
      FROM entity e
      LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
     WHERE e.kind IN ('compraventa', 'concesionario_oficial')
       AND e.province_code IS NOT NULL
       AND EXISTS (SELECT 1 FROM vehicle v
                    WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
     GROUP BY e.province_code, e.country_code
),
desg AS (
    SELECT e.province_code,
           e.country_code,
           count(DISTINCT e.entity_ulid)                                          AS numerator,
           count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key = 'dgt_cat')  AS denominator
      FROM entity e
      LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
     WHERE e.kind = 'desguace' AND e.province_code IS NOT NULL
     GROUP BY e.province_code, e.country_code
)
-- VENTA — inventory-served coverage vs registral ceiling (SELLADO >=85 / PARCIAL 50-85 / GAP <50)
SELECT d.province_code,
       'venta'::text                                   AS segment,
       d.point_est                                     AS denominator,
       COALESCE(n.numerator, 0)                        AS numerator,
       round((100.0 * COALESCE(n.numerator, 0) / NULLIF(d.point_est, 0))::numeric, 1)
                                                       AS coverage_pct,
       CASE
         WHEN d.point_est IS NULL OR d.point_est = 0 THEN 'NO_DENOM'
         WHEN 100.0 * COALESCE(n.numerator, 0) / d.point_est >= 85 THEN 'SELLADO'
         WHEN 100.0 * COALESCE(n.numerator, 0) / d.point_est >= 50 THEN 'PARCIAL'
         ELSE 'GAP'
       END                                             AS verdict,
       d.country_code                                  AS country_code
  FROM denominator_estimate d
  LEFT JOIN venta_num n ON n.province_code = d.province_code
                       AND n.country_code = d.country_code
 WHERE d.segment = 'venta'
UNION ALL
-- DESGUACE — discovery coverage vs DGT census (SELLADO when found >= official census)
SELECT dg.province_code,
       'desguace'::text                                AS segment,
       dg.denominator,
       dg.numerator,
       round((100.0 * dg.numerator / NULLIF(dg.denominator, 0))::numeric, 1)
                                                       AS coverage_pct,
       CASE
         WHEN dg.denominator IS NULL OR dg.denominator = 0 THEN 'NO_DENOM'
         WHEN dg.numerator >= dg.denominator THEN 'SELLADO'
         ELSE 'GAP'
       END                                             AS verdict,
       dg.country_code                                 AS country_code
  FROM desg dg;

-- 3. v_exhaustiveness_seal — project country_code (appended 16->17th) and pick the latest build
--    PER COUNTRY so a newer foreign build never evicts another tenant's certificate.
CREATE OR REPLACE VIEW v_exhaustiveness_seal AS
WITH latest AS (
    SELECT DISTINCT ON (country_code) country_code, build_run_id
    FROM exhaustiveness_estimate
    ORDER BY country_code, created_at DESC
)
SELECT e.province_code,
       e.segment,
       e.k_lists,
       e.n_obs,
       e.n_hat,
       e.ci_low,
       e.ci_high,
       e.coverage_point,
       e.coverage_lower,
       e.method,
       e.confidence,
       e.seal_threshold,
       e.sealed,
       e.external_ref,
       e.build_run_id,
       e.created_at,
       e.country_code
FROM exhaustiveness_estimate e
JOIN latest l ON l.build_run_id = e.build_run_id
             AND l.country_code = e.country_code;

-- Rollback (restore the pre-0060 country-blind defs, then drop the column + index):
-- CREATE OR REPLACE VIEW v_exhaustiveness_seal AS
-- WITH latest AS (
--     SELECT build_run_id FROM exhaustiveness_estimate ORDER BY created_at DESC LIMIT 1
-- )
-- SELECT e.province_code, e.segment, e.k_lists, e.n_obs, e.n_hat, e.ci_low, e.ci_high,
--        e.coverage_point, e.coverage_lower, e.method, e.confidence, e.seal_threshold,
--        e.sealed, e.external_ref, e.build_run_id, e.created_at
--   FROM exhaustiveness_estimate e
--   JOIN latest l ON l.build_run_id = e.build_run_id;
-- CREATE OR REPLACE VIEW v_province_seal AS
-- WITH venta_num AS (
--     SELECT e.province_code, count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
--       FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
--      WHERE e.kind IN ('compraventa','concesionario_oficial') AND e.province_code IS NOT NULL
--        AND EXISTS (SELECT 1 FROM vehicle v WHERE v.entity_ulid=e.entity_ulid AND v.status='available')
--      GROUP BY e.province_code),
-- desg AS (
--     SELECT e.province_code, count(DISTINCT e.entity_ulid) AS numerator,
--            count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key='dgt_cat') AS denominator
--       FROM entity e LEFT JOIN entity_source es ON es.entity_ulid=e.entity_ulid
--      WHERE e.kind='desguace' AND e.province_code IS NOT NULL
--      GROUP BY e.province_code)
-- SELECT d.province_code, 'venta'::text AS segment, d.point_est AS denominator,
--        COALESCE(n.numerator,0) AS numerator,
--        round((100.0*COALESCE(n.numerator,0)/NULLIF(d.point_est,0))::numeric,1) AS coverage_pct,
--        CASE WHEN d.point_est IS NULL OR d.point_est=0 THEN 'NO_DENOM'
--             WHEN 100.0*COALESCE(n.numerator,0)/d.point_est >= 85 THEN 'SELLADO'
--             WHEN 100.0*COALESCE(n.numerator,0)/d.point_est >= 50 THEN 'PARCIAL'
--             ELSE 'GAP' END AS verdict
--   FROM denominator_estimate d LEFT JOIN venta_num n ON n.province_code=d.province_code
--  WHERE d.segment='venta'
-- UNION ALL
-- SELECT dg.province_code, 'desguace'::text AS segment, dg.denominator, dg.numerator,
--        round((100.0*dg.numerator/NULLIF(dg.denominator,0))::numeric,1) AS coverage_pct,
--        CASE WHEN dg.denominator IS NULL OR dg.denominator=0 THEN 'NO_DENOM'
--             WHEN dg.numerator >= dg.denominator THEN 'SELLADO' ELSE 'GAP' END AS verdict
--   FROM desg dg;
-- DROP INDEX IF EXISTS ix_exhaustiveness_country;
-- ALTER TABLE exhaustiveness_estimate DROP COLUMN IF EXISTS country_code;
