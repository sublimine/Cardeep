-- 0043_province_seal_desguace.sql — extend v_province_seal to the DESGUACE segment (SU-SEAL / B6).
-- 0042 sealed VENTA (served canonical / DIRCE-451 registral ceiling, >=85%). This adds the
-- DESGUACE segment with its OWN, structurally different semantics:
--
--   VENTA    = inventory-served coverage: canonical dealers WITH stock / registral ceiling, >=85%.
--   DESGUACE = DISCOVERY coverage: scrapyards (CATs) have no schema.org inventory, so the seal is
--              "did we find at least the official DGT census?" numerator = ALL desguaces found
--              (dgt_cat + aedra + overture + geo_sweep), denominator = the DGT CAT census subset
--              (entity_source.source_key='dgt_cat'). SELLADO when found >= census (discovery
--              complete). Verified live 2026-06-16: 52/52 SELLADO (total 1895 >= census 1292),
--              spot-checks match calc_spain_sealed.py [VERIFICADO]: Madrid 48/98, Barcelona 76/116.
--
-- The two segments are a UNION ALL — the API/consumers group by segment. Read-only view; the venta
-- branch is byte-identical to 0042. Fully reversible (the rollback restores the venta-only 0042 view).

CREATE OR REPLACE VIEW v_province_seal AS
WITH venta_num AS (
    SELECT e.province_code,
           count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
      FROM entity e
      LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
     WHERE e.kind IN ('compraventa', 'concesionario_oficial')
       AND e.province_code IS NOT NULL
       AND EXISTS (SELECT 1 FROM vehicle v
                    WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
     GROUP BY e.province_code
),
desg AS (
    SELECT e.province_code,
           count(DISTINCT e.entity_ulid)                                          AS numerator,
           count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key = 'dgt_cat')  AS denominator
      FROM entity e
      LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid
     WHERE e.kind = 'desguace' AND e.province_code IS NOT NULL
     GROUP BY e.province_code
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
       END                                             AS verdict
  FROM denominator_estimate d
  LEFT JOIN venta_num n ON n.province_code = d.province_code
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
       END                                             AS verdict
  FROM desg dg;

-- Rollback (restore the venta-only 0042 view):
-- CREATE OR REPLACE VIEW v_province_seal AS
-- WITH num AS (
--     SELECT e.province_code, count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
--       FROM entity e LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
--      WHERE e.kind IN ('compraventa','concesionario_oficial') AND e.province_code IS NOT NULL
--        AND EXISTS (SELECT 1 FROM vehicle v WHERE v.entity_ulid=e.entity_ulid AND v.status='available')
--      GROUP BY e.province_code)
-- SELECT d.province_code, 'venta'::text AS segment, d.point_est AS denominator,
--        COALESCE(n.numerator,0) AS numerator,
--        round((100.0*COALESCE(n.numerator,0)/NULLIF(d.point_est,0))::numeric,1) AS coverage_pct,
--        CASE WHEN d.point_est IS NULL OR d.point_est=0 THEN 'NO_DENOM'
--             WHEN 100.0*COALESCE(n.numerator,0)/d.point_est >= 85 THEN 'SELLADO'
--             WHEN 100.0*COALESCE(n.numerator,0)/d.point_est >= 50 THEN 'PARCIAL'
--             ELSE 'GAP' END AS verdict
--   FROM denominator_estimate d LEFT JOIN num n ON n.province_code=d.province_code
--  WHERE d.segment='venta';
