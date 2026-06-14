-- 0024_source_coverage.sql — post-harvest coverage verification gate (CAMPAIGN B9).
-- Introduces a per-source coverage audit table that answers "how much of <source> do we
-- have?" in one query, by three orthogonal paths: declared_total (what the source claims),
-- captured_db (what our DB holds), db_edges (platform_listing structural count).
--
-- Extends source_health with a per-source coverage floor (configurable per tier). The gate
-- is triggered automatically by record_run() whenever a connector supplies declared_total.
-- Idempotent: IF NOT EXISTS guards on CREATE; ADD COLUMN IF NOT EXISTS on ALTER. Reversible.
--
-- Run order: after 0023 (verification_verdict must already exist, and source_health must
-- already have the tuning column from 0013 and harvest_interval_hours from 0021).

CREATE TABLE IF NOT EXISTS source_coverage (
    source_key      TEXT PRIMARY KEY,
    declared_total  BIGINT,                         -- what the source CLAIMS to have
    captured_db     BIGINT,                         -- count(vehicle) of ours with that source
    db_edges        BIGINT,                         -- count(platform_listing) for that platform
    coverage_pct    NUMERIC(7, 4),                  -- captured_db / declared_total (0..1+)
    verdict         TEXT,                           -- TRUSTWORTHY | REFUTED | UNVERIFIED
    verdict_id      BIGINT REFERENCES verification_verdict (id),
    probed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE source_coverage IS
    'Per-source coverage audit (post-harvest). Refreshed on every harvest via verify_coverage(). '
    'Answers "how much of wallapop do we have?" with three orthogonal paths. '
    'verdict_id links to the full VAM evidence row in verification_verdict.';

COMMENT ON COLUMN source_coverage.declared_total IS
    'Total listings the source DECLARES for this scope (e.g. totalResults, totalHits sum). '
    'Comes from the source itself; never from our DB.';

COMMENT ON COLUMN source_coverage.captured_db IS
    'count(DISTINCT vehicle) in our DB attributed to this source via first_discovered_source '
    'or platform_listing -> vehicle join. Orthogonal to declared_total.';

COMMENT ON COLUMN source_coverage.db_edges IS
    'count(platform_listing) rows for the platform_entity that represents this source. '
    'Structural reference count, orthogonal to captured_db.';

COMMENT ON COLUMN source_coverage.coverage_pct IS
    'captured_db / declared_total. 1.00 = full coverage; <0.85 fires an alert by default. '
    'Can exceed 1.0 if the source under-declares (e.g. clamped totalHits).';

COMMENT ON COLUMN source_coverage.verdict IS
    'VAM verdict: TRUSTWORTHY (>=2 paths agree within tolerance) | REFUTED | UNVERIFIED.';

-- coverage_floor: minimum acceptable coverage ratio for this source.
-- Tier-1 giants should be set to 0.90 by a post-migration maintenance step.
-- Long-tail sources tolerate 0.80. Default 0.85 is a safe midpoint.
ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS coverage_floor NUMERIC(5, 4) NOT NULL DEFAULT 0.85;

COMMENT ON COLUMN source_health.coverage_floor IS
    'Minimum coverage ratio (0..1) that verify_coverage() accepts before firing an alert. '
    'Default 0.85; set to 0.90 for Tier-1 giants, 0.80 for long-tail.';

-- Rollback:
-- ALTER TABLE source_health DROP COLUMN IF EXISTS coverage_floor;
-- DROP TABLE IF EXISTS source_coverage;
