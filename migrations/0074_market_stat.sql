-- 0074_market_stat.sql — market-intelligence compute layer (CAMPAIGN 01-market-intelligence, F1).
--
-- NOTE ON NUMBERING: the carta 01-market-intelligence.md §5 originally proposed 0073 for this
-- migration (written when 0072 was the last on disk). By the time this migration was actually
-- created, 0073_auth.sql had already been consumed by a parallel frontier (per the project's
-- migration-numbering mandate: never fix a number a priori, always `ls migrations/*.sql | sort |
-- tail -1` at creation time and take max+1). Renumbered to 0074 without collision.
--
-- Mirrors vehicle_cluster_run/vehicle_cluster (0023) exactly in structure: a run+gate table pair,
-- non-destructive, additive. market_stat_run holds one EXECUTION of the compute job (methodology,
-- window, universe size, cross-check results, published gate). market_stat holds the computed
-- aggregate rows for that run. Doctrina MVCC del proyecto (CLAUDE.md): INSERT de run nuevo + DELETE
-- de runs caducados; JAMÁS UPDATE de una fila de market_stat una vez escrita. The ONLY field ever
-- UPDATEd after insert is market_stat_run.published (+ published_at) — same lifecycle as
-- vehicle_cluster_run.vam_verified, gated by the Director/VAM protocol (§7 of the carta), never the
-- aggregate rows themselves.
--
-- Segment key model (carta §5 + §4 M1-M10):
--   make, model         — always present when the metric is segment-scoped.
--   year                — ANCHOR of a sliding +/-1 year band (pipeline/market/cohort.py
--                          YEAR_BAND_RADIUS), NOT an exact-year filter. year=2020 means the cohort
--                          used vehicle.year IN (2019,2020,2021). NULL for metrics with no year
--                          axis (M5 province-only, M10 partially).
--   age_band             — M6's cross-sectional age-cohort label ('0-1','1-2','2-3','3-5','5-8');
--                          mutually exclusive with `year` (M6 does not use the +/-1 band, it uses
--                          discrete age buckets nation-wide). NULL for every other metric.
--   fuel                 — NULL means "all fuels" (used for province-only/national fallback rows
--                          where the product deliberately widens the cohort, e.g. M1's national
--                          fallback row per §6).
--   province_code        — NULL means "national" (the fallback row §6 mandates when the
--                          provincial n<8; also the natural key for M6's national curve).
--
-- Value shape: M1 uses p25/p50/p75 (a distribution). M3/M4/M5/M7/M9/M10 use value_num (a scalar) +
-- optional value_extra JSONB for a metric's secondary figure (e.g. M9's median price-cut alongside
-- its %-of-segment-with-cuts). No metric ever needs BOTH shapes, but a shared wide table (not one
-- table per metric) keeps the "only the last published run is served" query, the retention/DELETE
-- of expired runs, and the API's cross-metric queries all in ONE place — a table per metric would
-- fragment the publish-gate transaction across 8 tables for no benefit at this cardinality
-- (tens of thousands of rows per run, not millions).

-- ---------------------------------------------------------------------------
-- market_stat_run: one execution of compute_stats.py
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_stat_run (
    run_id               TEXT        PRIMARY KEY,             -- caller-supplied id (ULID-shaped)
    run_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    methodology_version   TEXT        NOT NULL,                -- pipeline/market/cohort.py METHODOLOGY_VERSION
    window_description    TEXT        NOT NULL,                -- human-declared window per metric (F0 gate: span<90d -> reduced windows spelled out here, never a fake 90/45/30d)
    n_in                  INTEGER     NOT NULL,                -- universe fed to the compute (canonical-strict count, F0 §9)
    metrics_computed      TEXT[]      NOT NULL DEFAULT '{}',   -- which of M1/M3/M4/M5/M6/M7/M9/M10 this run populated
    checks                JSONB,                                -- cross-check results: {sql_vs_python: {...}, run_over_run_delta_pct: {...}}
    published             BOOLEAN     NOT NULL DEFAULT FALSE,  -- gate: only a published run is served by market.py
    published_at          TIMESTAMPTZ,
    notes                 TEXT
);

CREATE INDEX IF NOT EXISTS idx_market_stat_run_published
    ON market_stat_run (published, run_at DESC) WHERE published = TRUE;

-- ---------------------------------------------------------------------------
-- market_stat: per-segment aggregate rows for one run
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_stat (
    id              BIGSERIAL   PRIMARY KEY,      -- surrogate: segment key columns are legitimately
                                                    -- NULL per metric (see header), so no natural
                                                    -- composite PK is NULL-safe across all 8 metrics.
    run_id          TEXT        NOT NULL REFERENCES market_stat_run(run_id) ON DELETE CASCADE,
    metric_id       TEXT        NOT NULL
        CHECK (metric_id IN ('M1','M3','M4','M5','M6','M7','M9','M10')),
    make            TEXT,
    model           TEXT,
    year            INT,                           -- anchor of +/-1 band; NULL where not applicable
    age_band        TEXT,                           -- M6 only
    fuel            TEXT,                           -- NULL = all fuels (national/wide fallback rows)
    province_code   VARCHAR(2),                     -- NULL = national
    n               INTEGER     NOT NULL,           -- sample size backing this row (>= MIN_COHORT_N, enforced by the job, not the DB — a defensive CHECK still guards against a job regression)
        CHECK (n >= 8),
    p25             NUMERIC,
    p50             NUMERIC,
    p75             NUMERIC,
    value_num       NUMERIC,                        -- scalar metrics (M3/M4/M5/M7/M9/M10)
    value_extra     JSONB,                           -- metric-specific secondary figures
    window_start    TIMESTAMPTZ,
    window_end      TIMESTAMPTZ,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Lookup pattern the API will use: "give me metric M for make+model+year+fuel+province of the
-- latest published run" -> join market_stat_run WHERE published, then filter market_stat by the
-- segment key. This composite index carries that filter; run_id is first because every query is
-- always scoped to exactly one run (the published one) first.
CREATE INDEX IF NOT EXISTS idx_market_stat_lookup
    ON market_stat (run_id, metric_id, make, model, year, fuel, province_code);

-- M5 (province demand ranking) queries by province_code across a metric within a run without the
-- make/model/year/fuel prefix (M5 is province-only, no vehicle segment) — a dedicated index avoids
-- a full scan of the run's rows for that access pattern.
CREATE INDEX IF NOT EXISTS idx_market_stat_province
    ON market_stat (run_id, metric_id, province_code) WHERE province_code IS NOT NULL;

-- Rollback:
-- DROP TABLE IF EXISTS market_stat;
-- DROP TABLE IF EXISTS market_stat_run;
