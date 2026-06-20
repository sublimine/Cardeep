-- 0048_discovery_capture.sql
-- Exhaustiveness Framework (§2 V2): stratified multi-list capture-recapture.
--
-- Three new tables, all idempotent (CREATE IF NOT EXISTS), owned exclusively by
-- pipeline/exhaustiveness/. They do NOT touch the existing denominator_estimate
-- table (kept intact) — this is a parallel, statistically-defensible layer.
--
--   discovery_list      reference: orthogonal-list taxonomy + orthogonality class.
--   discovery_capture   matrix: one row per (resolved_ulid, list_key) capture.
--   exhaustiveness_estimate  per-stratum N̂ + CI + sealing verdict.
--
-- Sealing doctrine: coverage is certified with the LOWER bound of the CI
-- (coverage_lower = n_obs / ci_high). The point estimate is never used to seal.

BEGIN;

-- ---------------------------------------------------------------------------
-- Reference: the orthogonal lists and their capture mechanism class.
-- orthogonality_class groups source_keys that share a capture mechanism, so
-- two keys in the same class are NOT independent and collapse to one list.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS discovery_list (
    list_key            text PRIMARY KEY,             -- canonical list id (e.g. 'GEO')
    orthogonality_class text NOT NULL,                -- mechanism family
    description         text NOT NULL,
    is_orthogonal       boolean NOT NULL DEFAULT true, -- usable as an MSE list
    created_at          timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Capture matrix: which orthogonal list saw which resolved (deduped) entity.
-- resolved_ulid is the canonical physical entity (v_dealer_resolved.resolved_ulid),
-- so cross-source duplicates collapse to one capture unit — the fix for the
-- old m=10 problem.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS discovery_capture (
    resolved_ulid       text NOT NULL,
    list_key            text NOT NULL REFERENCES discovery_list(list_key),
    province_code       char(2),                      -- stratum dimension 1
    segment             text,                         -- stratum dimension 2 (entity type)
    captured_at         timestamptz NOT NULL DEFAULT now(),
    build_run_id        text NOT NULL,                -- which build populated this row
    PRIMARY KEY (resolved_ulid, list_key, build_run_id)
);

CREATE INDEX IF NOT EXISTS ix_discovery_capture_stratum
    ON discovery_capture (build_run_id, province_code, segment);
CREATE INDEX IF NOT EXISTS ix_discovery_capture_list
    ON discovery_capture (build_run_id, list_key);

-- ---------------------------------------------------------------------------
-- Per-stratum estimate + sealing verdict.
-- One row per (build_run_id, province_code, segment).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exhaustiveness_estimate (
    id              bigserial PRIMARY KEY,
    build_run_id    text NOT NULL,
    province_code   char(2),                          -- NULL => national roll-up
    segment         text,                             -- NULL => all types
    k_lists         integer NOT NULL,                 -- orthogonal lists with data
    n_obs           integer NOT NULL,                 -- observed distinct entities
    n_hat           double precision NOT NULL,        -- point estimate of true N
    ci_low          double precision NOT NULL,
    ci_high         double precision NOT NULL,
    coverage_point  double precision NOT NULL,        -- n_obs / n_hat
    coverage_lower  double precision NOT NULL,        -- n_obs / ci_high (conservative)
    method          text NOT NULL,                    -- estimator id
    confidence      text NOT NULL,                    -- high|low|none
    seal_threshold  double precision NOT NULL,        -- X for the seal test
    sealed          boolean NOT NULL,                 -- coverage_lower >= threshold
    external_ref    double precision,                 -- triangulation (CNAE/DGT) if any
    diagnostics     jsonb,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_exhaustiveness_run
    ON exhaustiveness_estimate (build_run_id, province_code, segment);

-- ---------------------------------------------------------------------------
-- Serving view: latest build per stratum, with the certified coverage.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_exhaustiveness_seal AS
WITH latest AS (
    SELECT build_run_id
    FROM exhaustiveness_estimate
    ORDER BY created_at DESC
    LIMIT 1
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
       e.created_at
FROM exhaustiveness_estimate e
JOIN latest l ON l.build_run_id = e.build_run_id;

-- schema_migrations registration is performed by the apply runner (it computes
-- the file sha256). See pipeline/exhaustiveness/migrate.py.

COMMIT;
