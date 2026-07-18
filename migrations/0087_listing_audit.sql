-- 0087_listing_audit.sql — 07-marketing F1: C1 listing-quality audit (plans/
-- cardeep-omni/07-marketing.md S5.2, S9 F1).
--
-- Same run+result pattern already proven by vehicle_cluster/vehicle_cluster_run
-- (0023) and market_stat/market_stat_run (0074): a versioned, re-executable batch
-- job persists ONE row per (run, vehicle) with the FULL evidence (11 checks +
-- points), never just the aggregate score — the frontend reads this table, it
-- NEVER recomputes the audit client-side (carta S4 C1: "El score se persiste con
-- la lista de checks fallados, nunca solo el agregado").
--
-- Additive, idempotent, reversible. migrate.py applies only the forward section.

CREATE TABLE IF NOT EXISTS listing_audit_run (
    run_ulid         TEXT PRIMARY KEY,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at      TIMESTAMPTZ,
    vehicles_audited INTEGER NOT NULL DEFAULT 0,
    engine_version   TEXT NOT NULL DEFAULT 'v1'
);

CREATE INDEX IF NOT EXISTS idx_listing_audit_run_started ON listing_audit_run (started_at DESC);

-- One row per (run, vehicle) — carta S5.2 "listing_audit" table. `checks` carries the
-- full CheckResult[] from pipeline/marketing/listing_audit.py (id/label/passed/
-- points_awarded/points_possible/message/evidence) so the UI can render "Sin VIN:
-- Google no te lo acepta" without a second query or a client-side recompute.
CREATE TABLE IF NOT EXISTS listing_audit (
    run_ulid      TEXT NOT NULL REFERENCES listing_audit_run(run_ulid) ON DELETE CASCADE,
    vehicle_ulid  TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    score         SMALLINT NOT NULL CHECK (score BETWEEN 0 AND 100),
    checks        JSONB NOT NULL,
    computed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_ulid, vehicle_ulid)
);

CREATE INDEX IF NOT EXISTS idx_listing_audit_vehicle ON listing_audit (vehicle_ulid, computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_listing_audit_score ON listing_audit (score);

-- "Latest run per vehicle" is the shape every consumer actually wants (carta S6
-- Bloque 1: "lista de sus coches ordenada por score C1 ascendente") — a view keeps
-- that DISTINCT ON logic in ONE place instead of every router/script re-deriving it.
CREATE OR REPLACE VIEW v_latest_listing_audit AS
SELECT DISTINCT ON (la.vehicle_ulid)
    la.vehicle_ulid, la.run_ulid, la.score, la.checks, la.computed_at
FROM listing_audit la
ORDER BY la.vehicle_ulid, la.computed_at DESC;

-- Rollback:
-- DROP VIEW IF EXISTS v_latest_listing_audit;
-- DROP TABLE IF EXISTS listing_audit;
-- DROP TABLE IF EXISTS listing_audit_run;
