-- 0061_analytic_province_width.sql -- widen the two ANALYTIC stratum province_code
-- columns from the ES-sized CHAR(2) to VARCHAR(8), the schema-genericity follow-up to
-- 0059 (which widened the GEO backbone province family but NOT these two analytic columns):
--   discovery_capture.province_code        (0048_discovery_capture.sql:39) -- capture stratum dim 1
--   exhaustiveness_estimate.province_code  (0048_discovery_capture.sql:58) -- per-stratum MSE key
--
-- WHY 0059 MISSED THEM: both are FREE-TEXT stratum labels, NOT geo_province FK-referrers
-- (no FOREIGN KEY, no CHECK), so the geo-FK-scoped 0059 widening never touched them. They
-- still rejected any non-ES province whose code exceeds 2 chars (e.g. France's overseas
-- department '971' Guadeloupe) with PostgreSQL 'value too long for type character(2)'.
--
-- THE INVARIANT (non-negotiable): every existing ES row stays byte-identical. CHAR(2)
-- blank-pads a stored value to width 2; VARCHAR does not. Every ES province code is EXACTLY
-- 2 chars (01-52, zero-padded INE), so NO ES value carries padding and the CHAR(2)->VARCHAR(8)
-- conversion is a pure 1:1 identity (verified live: '28'::char(2)::varchar(8) = '28' len 2).
-- The only deliberate semantic change is bpchar's trailing-space-insensitive equality becoming
-- varchar exact equality -- immaterial because no ES code is sub-width or padded. VARCHAR(8)
-- matches the geo province family width chosen in 0059 (FR DOM 3-digit, German Kreis AGS
-- 5-digit, NUTS-2/3 alphanumeric -- 8 is a safe EU sub-national province ceiling with headroom).
--
-- VERIFIED LIVE against the dry-run cardeep DB (:5434, @0060) before writing:
--   * Both columns are CHAR(2) (information_schema: data_type 'character', max_length 2),
--     NULL-able (NULL => national roll-up), no DEFAULT.
--   * NEITHER column carries a FOREIGN KEY or CHECK: discovery_capture has PK
--     (resolved_ulid, list_key, build_run_id) + an FK on list_key ONLY; exhaustiveness_estimate
--     has PK on id ONLY. No trigger binds either column.
--   * Two btree indexes include the column and are rebuilt AUTOMATICALLY by ALTER TYPE (no
--     explicit drop needed): ix_discovery_capture_stratum (build_run_id, province_code, segment)
--     and ix_exhaustiveness_run (build_run_id, province_code, segment).
--   * Exactly ONE view depends on either column and therefore BLOCKS ALTER COLUMN TYPE
--     ('cannot alter type of a column used by a view or rule'): v_exhaustiveness_seal (0048,
--     last redefined 0060) projects exhaustiveness_estimate.province_code. NO view depends on
--     discovery_capture.province_code. The view is dropped before the swap and recreated
--     BYTE-IDENTICAL (body is the live pg_get_viewdef @0060) after it.
--
-- ORDERING (one txn -- the runner wraps the whole migration; NO BEGIN/COMMIT here, per the
-- scripts/migrate.py convention shared by 0059/0060): (1) drop the one dependent view;
-- (2) ALTER both columns to VARCHAR(8); (3) recreate the view byte-identical.
-- IDEMPOTENT: DROP VIEW IF EXISTS; ALTER ... TYPE varchar is a no-op when already varchar;
-- CREATE OR REPLACE VIEW. The schema_migrations ledger skips an already-applied 0061 anyway.

-- 1. Drop the only view that depends on a widened column (exhaustiveness_estimate.province_code).
DROP VIEW IF EXISTS v_exhaustiveness_seal;

-- 2. Widen both analytic stratum columns to VARCHAR(8). The USING cast is a 1:1 identity for
--    the exact-width ES data (no padding to strip). The two stratum indexes are rebuilt
--    automatically; nullability is preserved (both stay NULL-able: NULL => national roll-up).
ALTER TABLE discovery_capture       ALTER COLUMN province_code TYPE varchar(8) USING province_code::varchar(8);
ALTER TABLE exhaustiveness_estimate ALTER COLUMN province_code TYPE varchar(8) USING province_code::varchar(8);

-- 3. Recreate v_exhaustiveness_seal BYTE-IDENTICAL (body is the live pg_get_viewdef @0060:
--    per-country DISTINCT ON latest build, country_code projected 17th). Its province_code
--    output column now follows the widened base type (varchar(8)) -- the intended effect.
CREATE OR REPLACE VIEW v_exhaustiveness_seal AS
 WITH latest AS (
         SELECT DISTINCT ON (exhaustiveness_estimate.country_code) exhaustiveness_estimate.country_code,
            exhaustiveness_estimate.build_run_id
           FROM exhaustiveness_estimate
          ORDER BY exhaustiveness_estimate.country_code, exhaustiveness_estimate.created_at DESC
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
     JOIN latest l ON l.build_run_id = e.build_run_id AND l.country_code = e.country_code;

-- Rollback:
-- (Reverse of the forward DDL. CLEAN ONLY while NO row holds a province_code wider than the
--  original CHAR(2) -- a varchar->char(2) cast TRUNCATES '971'. Any pilot/onboarding that
--  seeded a wide non-ES analytic province MUST delete those rows BEFORE rolling back.)
-- DROP VIEW IF EXISTS v_exhaustiveness_seal;
-- ALTER TABLE discovery_capture       ALTER COLUMN province_code TYPE char(2) USING province_code::char(2);
-- ALTER TABLE exhaustiveness_estimate ALTER COLUMN province_code TYPE char(2) USING province_code::char(2);
-- (then recreate v_exhaustiveness_seal from section 3 -- the view body is unchanged.)
