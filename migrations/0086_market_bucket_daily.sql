-- 0086_market_bucket_daily.sql — trading-terminal daily aggregation (Pillar 09-trading-terminal, F1).
--
-- NUMBERING: `ls migrations/*.sql | sort -V | tail` at creation time showed 0085 as the highest
-- file on disk (0084_crm.sql, 0085_engine_heartbeat_log.sql — both written by parallel frontiers
-- of this same block, per 00-MASTER.md C-6: "ninguna carta posee un número, el ejecutor toma
-- max+1"). This migration is 0086.
--
-- Ownership: 00-MASTER.md resolution C-1 assigns `services/api/routers/market.py` and the
-- `/market/*` namespace to pilar 01-market-intelligence exclusively. This migration's tables
-- (market_symbol, market_bucket_daily) are SEPARATE from 01's market_stat/market_stat_run
-- (0074_market_stat.sql) — genuinely distinct cohort keys (01: make+model+FUEL+YEAR-band+province;
-- 09: make+model+province, no fuel/year axis — carta 09 §4 C1) — but the PERCENTILE/MEDIAN MATH
-- is the SAME shared helper (pipeline/market/cohort.py: percentile_cont/median/divergence_pct),
-- imported by pipeline/terminal/compute_buckets.py, never re-derived (C-1: "prohibido un tercer
-- cálculo independiente de mediana-por-cohorte").
--
-- F1 MEASUREMENT (verified live, cardeep-pg, this session — 09-trading-terminal.md §5.2's
-- declared gap: "no se ha verificado ... el volumen real de filas de vehicle_event ni su
-- distribución temporal"):
--   vehicle_event total: 3,749,363 rows, observed_at spanning 2026-06-12 -> 2026-07-17.
--   Distinct calendar days carrying ANY event: exactly 14 (not ~35 continuous days). The 00-
--   marketplace-engine C-8 finding ("motor parado ~18 dias, heartbeat muerto 2026-06-29") is
--   directly visible in this table: two disjoint bursts (2026-06-12..06-28, ten days with real
--   gaps inside — 06-16..06-19 and 06-24..06-26 missing entirely) then an 18-day silence (three
--   isolated single-row PRICE_CHANGE events on 07-07/08/09, zero NEW/GONE) before the engine's
--   catch-up burst on 2026-07-17 (129,466 NEW + 109,422 GONE in one day).
--
-- DESIGN CONSEQUENCE (carta amendment, declared not hidden): a smoothly-interpolated historical
-- OHLC series over "35 days" is NOT constructible from this corpus without fabricating data for
-- the silent days — exactly the dishonesty this project's antialucinación doctrine forbids.
-- market_bucket_daily therefore stores ONE ROW PER REAL CALENDAR DAY THAT ACTUALLY CARRIES
-- vehicle_event ACTIVITY for that symbol (computed by the job as
-- `SELECT DISTINCT date_trunc('day', observed_at)::date FROM vehicle_event`, never a
-- generate_series over the full range) — the terminal's chart shows genuine gaps for silent days
-- (like a stock exchange closed on a holiday: no candle, not a flat fabricated line), not a
-- continuous illusion. `bucket_date` is a real trading-day PK component, not an artificial index.
--
-- C1 (symbol): make + model + province_code (province_code NULL = the make·model·ES national
-- roll-up; §4 also names make·ES and CDX-{province}/CDX-ES composite indices — those aggregate
-- FURTHER over this table at read time by the router, they get no separate market_symbol row in
-- F1, a declared scope reduction to keep F1 to the atomic per-model-per-province symbol only).
--
-- C2 (minimum sample): >= 30 active listings AND >= 5 events in the bucket's day — enforced by
-- the job's SQL HAVING clause (a row that fails the bar is never written, mirroring 0074's own
-- "muestra insuficiente" pattern: enforced by SQL, not a post-hoc filter). NOT sourced from any
-- pre-existing shared threshold registry: 00-MASTER.md C-12 declares a future "registro único de
-- cohortes y umbrales" but, verified this session (`grep` across pipeline/ + services/ for
-- registry/threshold/COHORT_REGISTRY patterns — zero hits), no pillar has built that registry
-- file yet. These constants live in pipeline/terminal/compute_buckets.py with full citation,
-- ready to migrate into a shared registry if/when a future pass consolidates C-12 — not a
-- duplicate percentile/median implementation (that part IS shared, see above), only local
-- threshold constants pending that consolidation.
--
-- C4 (outlier exclusion): verified live against the PRIMARY source this session (Manheim's own
-- "Summary Methodology for Manheim Used Vehicle Value Index" PDF, site.manheim.com — fetched and
-- read in full, not paraphrased secondhand): "Outliers are defined as those where both price AND
-- mileage are outside of 2.6 standard deviations." The carta's original F0-authored C4 text said
-- "price O km" (an OR) — CORRECTED here to AND, matching the primary source exactly. This
-- migration's `outliers_excluded` column counts rows failing the AND-both-2.6-sigma test within
-- the symbol's 90-day (or corpus-span-clamped, see cohort.effective_window_days) window.
--
-- Doctrina MVCC del proyecto (CLAUDE.md): INSERT de bucket nuevo (idempotent upsert keyed on
-- (symbol_key, bucket_date)) + re-run of a stale day overwrites via ON CONFLICT; JAMÁS un UPDATE
-- de agregados históricos por otra vía. market_symbol rows are upserted by the same job (a
-- symbol's is_active/first_bucket/last_bucket evolve as new buckets land — this is metadata about
-- the symbol's OWN activity history, not a measured market aggregate, so it is the one table here
-- allowed to UPDATE in place, mirroring vehicle.status's own append-plus-mutable-pointer pattern).

-- ---------------------------------------------------------------------------
-- market_symbol: registry of C1 symbols this corpus has ever produced a bucket for.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_symbol (
    symbol_key    TEXT PRIMARY KEY,             -- '{MAKE}|{MODEL}|{PROVINCE}' or '{MAKE}|{MODEL}|NAT'
    make          TEXT NOT NULL,
    model         TEXT NOT NULL,
    province_code VARCHAR(2),                    -- NULL = national roll-up (make·model·ES)
    level         TEXT NOT NULL
        CHECK (level IN ('model_prov', 'model_nat')),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE, -- cleared C2 on its most recent computed bucket
    first_bucket  DATE NOT NULL,
    last_bucket   DATE NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_symbol_natural_key
    ON market_symbol (make, model, COALESCE(province_code, 'NAT'));

CREATE INDEX IF NOT EXISTS idx_market_symbol_search ON market_symbol (make, model) WHERE is_active;

-- ---------------------------------------------------------------------------
-- market_bucket_daily: one row per (symbol_key, REAL bucket_date).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_bucket_daily (
    symbol_key              TEXT NOT NULL REFERENCES market_symbol(symbol_key) ON DELETE CASCADE,
    bucket_date              DATE NOT NULL,
    active_count              INTEGER NOT NULL,     -- as-of-day snapshot (C2 gate #1)
    median_price               NUMERIC,
    p25_price                  NUMERIC,
    p75_price                  NUMERIC,
    median_km                  NUMERIC,
    new_count                  INTEGER NOT NULL DEFAULT 0,   -- exact per-day vehicle_event count
    gone_count                 INTEGER NOT NULL DEFAULT 0,
    price_change_down_count    INTEGER NOT NULL DEFAULT 0,
    price_change_up_count      INTEGER NOT NULL DEFAULT 0,
    outliers_excluded          INTEGER NOT NULL DEFAULT 0,   -- C4: failed BOTH-2.6-sigma test
    dom_p50_days                NUMERIC,                      -- C5: median days-on-market of GONE this bucket
    n_events                   INTEGER NOT NULL DEFAULT 0,   -- C2 gate #2 = new_count+gone_count+price_change*_count
    computed_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (symbol_key, bucket_date),
    CHECK (active_count >= 0 AND n_events >= 0)
);

CREATE INDEX IF NOT EXISTS idx_market_bucket_daily_symbol_date
    ON market_bucket_daily (symbol_key, bucket_date DESC);

-- Rollback:
-- DROP TABLE IF EXISTS market_bucket_daily;
-- DROP TABLE IF EXISTS market_symbol;
