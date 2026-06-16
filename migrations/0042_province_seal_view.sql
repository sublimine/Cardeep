-- 0042_province_seal_view.sql — SU-SEAL persisted as a LIVE view (audit SU-SEAL / B6).
-- The per-province VENTA seal = served canonical dealers (numerator) / DIRCE CNAE-451 registral
-- ceiling (denominator, loaded into denominator_estimate segment='venta' by
-- scripts/load_denominator_provincia.py). Until now the seal lived only in the read-only
-- snapshot script calc_spain_sealed.py (hardcoded 2026-06-14 numerator). This makes it a LIVE
-- view so the seal always reflects the current harvest with NO stale snapshot.
--
-- Numerator = COUNT(DISTINCT COALESCE(v_dealer_resolved.resolved_ulid, entity_ulid)) — the CANONICAL
-- deduped dealer (matches the API's resolve_cluster + calc_spain_sealed's cv/co_served), counting
-- only compraventa + concesionario_oficial WITH >=1 available vehicle. Using entity_ulid directly
-- (no dedup) over-counts ~2x (verified: 164.9% national vs the correct 79.4%), so the COALESCE
-- canonical key is mandatory here.
--
-- Verdict thresholds mirror calc_spain_sealed.py: SELLADO >=85%, PARCIAL 50-85%, GAP <50%.
-- coverage may exceed 100% (we can find more dealers than the registral ceiling lists) — that is
-- still SELLADO. Read-only view; additive; fully reversible (DROP VIEW).

CREATE OR REPLACE VIEW v_province_seal AS
WITH num AS (
    SELECT e.province_code,
           count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) AS numerator
      FROM entity e
      LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
     WHERE e.kind IN ('compraventa', 'concesionario_oficial')
       AND e.province_code IS NOT NULL
       AND EXISTS (SELECT 1 FROM vehicle v
                    WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
     GROUP BY e.province_code
)
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
  LEFT JOIN num n ON n.province_code = d.province_code
 WHERE d.segment = 'venta';

-- Rollback:
-- DROP VIEW IF EXISTS v_province_seal;
