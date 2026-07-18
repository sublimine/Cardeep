-- 0081_arbitrage_decay.sql — 04-arbitrage F4: time-arbitrage (market_decay + market_cycle_stats).
--
-- 04-arbitrage.md §5.2 names ONE table ("market_decay") carrying both the age-bucket price-decay
-- curve AND the cohort-level days-to-GONE cycle stats (n, median relative price, median days-to-
-- GONE, P25/P75) in a single row shape. This migration DEVIATES from that literal shape (declared,
-- not hidden — carta §9 F4 authorizes restructuring; the carta text is updated to match): the two
-- signals are computed over DIFFERENT populations (the price-decay curve uses every PRICE_CHANGE-
-- reconstructed price sample at every age, cycle stats use only vehicles with a completed NEW->GONE
-- cycle in the last 12 months) and coupling them into one denormalized row-per-bucket would either
-- duplicate the cohort-level cycle stats six times (once per bucket) or force both computations to
-- share a population that shouldn't be shared. Two tables, same run bookkeeping pattern as
-- arbitrage_run — cleaner to query, identical verification discipline (mínimo-N-o-silencio).
--
-- Additive, idempotent (IF NOT EXISTS), reversible (Rollback block at end). INSERT-only per run.

-- ---------------------------------------------------------------------------
-- 1. arbitrage_decay_run — bookkeeping (mirrors arbitrage_run)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS arbitrage_decay_run (
    run_id               TEXT PRIMARY KEY,
    run_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    methodology_version  TEXT NOT NULL,
    n_cycles_scanned     INT NOT NULL,      -- completed NEW->GONE cycles in the last 12 months
    n_cohorts_cycle      INT NOT NULL,      -- cohorts clearing the >=50-cycle minimum
    n_bucket_rows        INT NOT NULL,      -- age-bucket rows clearing the >=30-observation minimum
    checks               JSONB,
    published            BOOLEAN NOT NULL DEFAULT FALSE
);

-- ---------------------------------------------------------------------------
-- 2. market_cycle_stats — "Curva de salida por cohorte" (§4.3): days-to-GONE distribution
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_cycle_stats (
    id                          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id                      TEXT NOT NULL REFERENCES arbitrage_decay_run(run_id) ON DELETE CASCADE,
    country_code                TEXT NOT NULL,
    make                        TEXT NOT NULL,
    model                       TEXT NOT NULL,
    year_band_start             INT NOT NULL,   -- 2-year band: [year_band_start, year_band_start+1]
    n_cycles                    INT NOT NULL,
    median_days_to_gone         DOUBLE PRECISION NOT NULL,
    p25_days_to_gone            DOUBLE PRECISION NOT NULL,
    p75_days_to_gone            DOUBLE PRECISION NOT NULL,
    pct_price_drop_before_gone  DOUBLE PRECISION NOT NULL,
    computed_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cycle_stats_run ON market_cycle_stats (run_id);
CREATE INDEX IF NOT EXISTS idx_cycle_stats_lookup ON market_cycle_stats (run_id, country_code, make, model, year_band_start);

-- ---------------------------------------------------------------------------
-- 3. market_decay — "Curva de decaimiento por cohorte" (§4.3): age-bucket relative-price curve
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_decay (
    id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id                   TEXT NOT NULL REFERENCES arbitrage_decay_run(run_id) ON DELETE CASCADE,
    country_code             TEXT NOT NULL,
    make                     TEXT NOT NULL,
    model                    TEXT NOT NULL,
    year_band_start          INT NOT NULL,
    bucket_label             TEXT NOT NULL CHECK (bucket_label IN ('0-7','8-15','16-30','31-60','61-90','90+')),
    bucket_min_days          INT NOT NULL,
    n                        INT NOT NULL,
    median_relative_price    DOUBLE PRECISION NOT NULL,  -- median(price_at_age / price_at_first_seen)
    computed_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_market_decay_run_cell
    ON market_decay (run_id, country_code, make, model, year_band_start, bucket_label);
CREATE INDEX IF NOT EXISTS idx_market_decay_lookup ON market_decay (run_id, country_code, make, model, year_band_start);

-- Rollback:
-- DROP TABLE IF EXISTS market_decay;
-- DROP TABLE IF EXISTS market_cycle_stats;
-- DROP TABLE IF EXISTS arbitrage_decay_run;
