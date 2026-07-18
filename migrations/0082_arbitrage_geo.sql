-- 0082_arbitrage_geo.sql — 04-arbitrage F5: geo-arbitrage (geo_price_cell + geo_price_gap).
--
-- 04-arbitrage.md §4.4: celda = (make, model, year-band de 2 años, province_code), min n>=15
-- (single tier — no Tier-A/B fallback, unlike deal-score's cohort). A gap between province A and B
-- for the SAME (make,model,year_band) cohort is shown only if both cells clear n>=15 AND the gap
-- exceeds the combined uncertainty (§4.4 formula — see pipeline/arbitrage/geo.py module docstring
-- for the dimensional-consistency judgment call this migration's columns support: MAD is stored in
-- BOTH ln-domain, as the rest of this pilar's cohorts do, AND the job derives a euro-scale sigma
-- from it before comparing against a euro-scale median gap).
--
-- Additive, idempotent (IF NOT EXISTS), reversible (Rollback block at end). INSERT-only per run.

-- ---------------------------------------------------------------------------
-- 1. arbitrage_geo_run — bookkeeping (mirrors arbitrage_run / arbitrage_decay_run)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS arbitrage_geo_run (
    run_id               TEXT PRIMARY KEY,
    run_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    methodology_version  TEXT NOT NULL,
    n_cells              INT NOT NULL,     -- (cohort, province) cells clearing n>=15
    n_gaps               INT NOT NULL,     -- significant province-pair gaps found
    checks               JSONB,
    published            BOOLEAN NOT NULL DEFAULT FALSE
);

-- ---------------------------------------------------------------------------
-- 2. geo_price_cell — one row per (run, cohort, province): the median+MAD a gap is built from
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS geo_price_cell (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id            TEXT NOT NULL REFERENCES arbitrage_geo_run(run_id) ON DELETE CASCADE,
    country_code      TEXT NOT NULL,
    make              TEXT NOT NULL,
    model             TEXT NOT NULL,
    year_band_start   INT NOT NULL,
    province_code     TEXT NOT NULL,
    n                 INT NOT NULL,
    median_ln_price   DOUBLE PRECISION NOT NULL,
    mad_ln_price      DOUBLE PRECISION NOT NULL,
    median_price      NUMERIC(12,2) NOT NULL,
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_geo_price_cell_run_cell
    ON geo_price_cell (run_id, country_code, make, model, year_band_start, province_code);
CREATE INDEX IF NOT EXISTS idx_geo_price_cell_cohort
    ON geo_price_cell (run_id, country_code, make, model, year_band_start);

-- ---------------------------------------------------------------------------
-- 3. geo_price_gap — one row per significant (run, cohort, province A, province B) pair
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS geo_price_gap (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id            TEXT NOT NULL REFERENCES arbitrage_geo_run(run_id) ON DELETE CASCADE,
    country_code      TEXT NOT NULL,
    make              TEXT NOT NULL,
    model             TEXT NOT NULL,
    year_band_start   INT NOT NULL,
    province_cheap    TEXT NOT NULL,   -- lower-median province
    province_expensive TEXT NOT NULL, -- higher-median province
    median_cheap      NUMERIC(12,2) NOT NULL,
    median_expensive  NUMERIC(12,2) NOT NULL,
    gap_eur           NUMERIC(12,2) NOT NULL,
    n_cheap           INT NOT NULL,
    n_expensive       INT NOT NULL,
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_geo_price_gap_run ON geo_price_gap (run_id);
CREATE INDEX IF NOT EXISTS idx_geo_price_gap_cohort
    ON geo_price_gap (run_id, country_code, make, model, year_band_start, gap_eur DESC);

-- Rollback:
-- DROP TABLE IF EXISTS geo_price_gap;
-- DROP TABLE IF EXISTS geo_price_cell;
-- DROP TABLE IF EXISTS arbitrage_geo_run;
