-- 0021_harvest_cadence.sql — per-source harvest cadence (CAMPAIGN B2.1).
-- Adds harvest_interval_hours to source_health so the B2.2 scheduler knows HOW OFTEN to
-- re-harvest each source without hardcoding intervals in Python. The default of 168 h (7 days)
-- is conservative enough to cover every long-tail / OEM-VO source with low churn; tier-1
-- giants will be updated to 24 h by the cadence-population step that follows this migration.
--
-- Design note: a NOT NULL column with a sensible DEFAULT means (a) existing rows inherit 168 h
-- automatically (zero backfill needed), (b) new rows inserted by record_run without an explicit
-- value land on 168 h without error, and (c) the scheduler can always read a defined cadence —
-- no NULL-guard logic needed in Python.

ALTER TABLE source_health
    ADD COLUMN IF NOT EXISTS harvest_interval_hours INTEGER NOT NULL DEFAULT 168;

COMMENT ON COLUMN source_health.harvest_interval_hours IS
    'How often (in hours) the scheduler should re-harvest this source. '
    'Default 168 = 7 days (conservative long-tail baseline). '
    'Tier-1 giants are set to 24 h; OEM-VO/rental/auction to 168 h; '
    'long-tail families/directories to 720 h (30 days).';

-- Rollback:
-- ALTER TABLE source_health DROP COLUMN IF EXISTS harvest_interval_hours;
