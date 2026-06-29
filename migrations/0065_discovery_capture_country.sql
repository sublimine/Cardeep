-- 0065_discovery_capture_country.sql — thread the country dimension into the CAPTURE matrix
-- (the exhaustiveness P1 follow-up to 0060). 0060 country-scoped the SEALED surface
-- (exhaustiveness_estimate + the two certificate views) but the UPSTREAM capture matrix
-- ``discovery_capture`` (0048, province_code widened to VARCHAR(8) by 0061) still had NO
-- country dimension. Its strata are keyed by (province_code, segment) ALONE, and the
-- province code space COLLIDES across tenants BY DESIGN (migrations/0053 puts DE province
-- '28' next to ES Madrid '28'). So a second-tenant build that read the matrix country-blind
-- would POOL the German and Spanish '28' captures into ONE stratum: the MSE estimate and the
-- seal denominator would be computed over a mixture of two countries — the exact pooling
-- 0060 closed downstream, still open one layer upstream at the capture seam.
--
-- THE INVARIANT (non-negotiable): DEFAULT 'ES' => byte-identical for today's sole tenant.
-- Every existing capture row is ES, so the new column backfills to 'ES' atomically and a
-- country-blind 'ES' read returns the historical row set unchanged. This is the EXACT pattern
-- 0060 used for exhaustiveness_estimate and 0053 used for denominator_estimate.
--
-- WHY ADDITIVE / FK-SAFE / REVERSIBLE:
--   1. ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES' — the DEFAULT backfills every
--      existing row to 'ES' (zero-NULL, no constraint violation possible). The PK stays
--      (resolved_ulid, list_key, build_run_id): a resolved_ulid is a globally-unique ULID
--      that belongs to exactly ONE country, so country is functionally implied by
--      resolved_ulid and the key needs no new column — two tenants can never share a
--      resolved_ulid, hence never collide on the PK even within one build_run_id.
--   2. A new country-first stratum index serves the per-country read
--      (read_patterns filters build_run_id + country_code + optional province/segment). The
--      historical ix_discovery_capture_stratum is KEPT (harmless, additive).
--   3. NO view depends on discovery_capture (verified live in 0061's header: "NO view depends
--      on discovery_capture.province_code"), so ADD COLUMN blocks nothing and needs no view
--      drop/recreate. discovery_capture is owned exclusively by pipeline/exhaustiveness/.
--
-- VERIFIED LIVE against the dry-run cardeep DB (:5434, @0064) before writing:
--   * discovery_capture columns: resolved_ulid text, list_key text, province_code varchar(8),
--     segment text, captured_at timestamptz, build_run_id text — NO country_code.
--   * PK (resolved_ulid, list_key, build_run_id); FK on list_key -> discovery_list(list_key);
--     two btree indexes (ix_discovery_capture_stratum, ix_discovery_capture_list). No trigger,
--     no CHECK on the table, no dependent view.
--
-- IDEMPOTENT (ADD COLUMN IF NOT EXISTS / CREATE INDEX IF NOT EXISTS) · REVERSIBLE (see the
-- Rollback block). NO BEGIN/COMMIT here — scripts/migrate.py wraps the whole file in one
-- transaction (the 0052/0053/0059/0060/0061/0062 convention).

-- 1. The missing tenant dimension on the capture matrix (DEFAULT 'ES' backfills all rows).
ALTER TABLE discovery_capture
    ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- 2. Country-first stratum index: a per-country build/read touches one country's rows only.
CREATE INDEX IF NOT EXISTS ix_discovery_capture_country_stratum
    ON discovery_capture (country_code, build_run_id, province_code, segment);

-- Rollback (drop the index + column; reverses to the pre-0065 country-blind matrix):
-- DROP INDEX IF EXISTS ix_discovery_capture_country_stratum;
-- ALTER TABLE discovery_capture DROP COLUMN IF EXISTS country_code;
