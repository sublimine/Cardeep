-- 0078_dgt_corroboration.sql — M8 corroboration result storage (CAMPAIGN
-- 01-market-intelligence, F4). Additive, idempotent, reversible.
--
-- Mirrors the market_stat_run/market_stat run+gate pattern (0074): one row per
-- corroboration computation (run), children rows per cohort (province+make+model+
-- month). Cohort granularity here is DELIBERATELY coarser than market_stat's
-- make+model+year-band+fuel+province (carta §4 M8 row: "provincia+marca+modelo+mes"
-- — no year-band, no fuel, month instead of a sliding window) because the DGT side
-- has no vehicle.year/fuel equivalent readily comparable at ingest time, and the
-- carta explicitly scopes M8's cohort to province+make+model+month only.

CREATE TABLE IF NOT EXISTS dgt_corroboration_run (
    run_id                TEXT        PRIMARY KEY,
    run_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    batch_id              TEXT        NOT NULL REFERENCES dgt_transfer_batch(batch_id),
    month                 CHAR(6)     NOT NULL,
    methodology_version   TEXT        NOT NULL,
    n_cohorts             INTEGER,
    notes                 TEXT
);

CREATE INDEX IF NOT EXISTS idx_dgt_corrob_run_month ON dgt_corroboration_run (month, run_at DESC);

CREATE TABLE IF NOT EXISTS dgt_corroboration (
    id              BIGSERIAL   PRIMARY KEY,
    run_id          TEXT        NOT NULL REFERENCES dgt_corroboration_run(run_id) ON DELETE CASCADE,
    province_code   VARCHAR(2),          -- NULL = national aggregate row
    make            TEXT        NOT NULL,
    model           TEXT,                -- NULL = make-level aggregate (model matching is the
                                          -- weakest link, per carta §8 — a make-level row is
                                          -- always computable even when model text does not align)
    month           CHAR(6)     NOT NULL,
    gone_count      INTEGER     NOT NULL,   -- Cardeep GONE events, this cohort+month
    dgt_count       INTEGER     NOT NULL,   -- DGT transfer rows, this cohort+month
    ratio           DOUBLE PRECISION        -- dgt_count / gone_count; NULL when gone_count = 0
);

CREATE INDEX IF NOT EXISTS idx_dgt_corrob_run ON dgt_corroboration (run_id);
CREATE INDEX IF NOT EXISTS idx_dgt_corrob_cohort ON dgt_corroboration (province_code, make, model, month);

-- Rollback:
-- DROP TABLE IF EXISTS dgt_corroboration;
-- DROP TABLE IF EXISTS dgt_corroboration_run;
