-- 0079_arbitrage.sql — 04-arbitrage F1: deal-score backend (cohort_stats + deal_score + arbitrage_run).
--
-- 04-arbitrage.md §5.2: "cohort_stats" and "deal_score" are the two tables the carta names; this
-- migration adds a third, "arbitrage_run", mirroring market_stat_run's run-bookkeeping pattern
-- (migrations/0074_market_stat.sql) — the API (F2) must serve "SOLO del último run completo" (§4.1),
-- which needs a run registry with a published/checks column, exactly like market_stat_run already
-- does for 01-market-intelligence. Names verified free (grep -rniE 'deal.?score|cohort_stats|
-- arbitrage_run' migrations/services/pipeline/scripts = 0 hits, 2026-07-17/18).
--
-- Doctrine: INSERT-only per run (PG MVCC — no UPDATE of non-mutated rows). A future purge job may
-- DELETE superseded runs' rows; nothing here is ever UPDATEd in place. Additive, idempotent
-- (IF NOT EXISTS), reversible (Rollback block at end).

-- ---------------------------------------------------------------------------
-- 1. arbitrage_run — one row per computation run (bookkeeping, mirrors market_stat_run)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS arbitrage_run (
    run_id               TEXT PRIMARY KEY,
    run_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    methodology_version  TEXT NOT NULL,
    n_in                 INT NOT NULL,             -- servable_vehicle rows scanned
    n_cohorts            INT NOT NULL,              -- cohorts that cleared min-N (both tiers)
    n_deals              INT NOT NULL,              -- deal_score rows written this run
    checks               JSONB,                     -- §7 dual-path verification result
    published            BOOLEAN NOT NULL DEFAULT FALSE
);

-- ---------------------------------------------------------------------------
-- 2. cohort_stats — one row per (run, cohort): the median+MAD the deal-score reads
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cohort_stats (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id           TEXT NOT NULL REFERENCES arbitrage_run(run_id) ON DELETE CASCADE,
    country_code     TEXT NOT NULL,
    make             TEXT NOT NULL,
    model            TEXT,                          -- NULL = Tier-B (make, year) fallback cohort
    year             INT NOT NULL,
    tier             TEXT NOT NULL CHECK (tier IN ('A', 'B')),
    n                INT NOT NULL,
    median_ln_price  DOUBLE PRECISION NOT NULL,
    mad_ln_price     DOUBLE PRECISION NOT NULL,
    median_price     NUMERIC(12,2) NOT NULL,
    computed_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cohort_stats_run ON cohort_stats (run_id);
CREATE INDEX IF NOT EXISTS idx_cohort_stats_lookup ON cohort_stats (run_id, country_code, make, year, model);

-- ---------------------------------------------------------------------------
-- 3. deal_score — one row per (run, vehicle) IN the badged opportunity range only
--    (-6.0 < z <= -2.0, per 04-arbitrage.md §4.1 bands) — NOT every servable vehicle,
--    keeping the table bounded (~2M+ servable vehicles would make an unfiltered write
--    a multi-million-row table for zero product benefit; only chollo candidates matter).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deal_score (
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id                TEXT NOT NULL REFERENCES arbitrage_run(run_id) ON DELETE CASCADE,
    vehicle_ulid          TEXT NOT NULL REFERENCES vehicle(vehicle_ulid) ON DELETE CASCADE,
    z                     DOUBLE PRECISION NOT NULL,
    band                  TEXT NOT NULL CHECK (band IN ('chollo_fuerte', 'bajo_mercado')),
    savings_eur           NUMERIC(12,2) NOT NULL,
    cohort_make           TEXT NOT NULL,
    cohort_model          TEXT,
    cohort_year           INT NOT NULL,
    cohort_tier           TEXT NOT NULL CHECK (cohort_tier IN ('A', 'B')),
    cohort_n              INT NOT NULL,
    cohort_median_price   NUMERIC(12,2) NOT NULL,
    computed_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_deal_score_run_vehicle ON deal_score (run_id, vehicle_ulid);
CREATE INDEX IF NOT EXISTS idx_deal_score_run_savings ON deal_score (run_id, savings_eur DESC);

-- Rollback:
-- DROP TABLE IF EXISTS deal_score;
-- DROP TABLE IF EXISTS cohort_stats;
-- DROP TABLE IF EXISTS arbitrage_run;
