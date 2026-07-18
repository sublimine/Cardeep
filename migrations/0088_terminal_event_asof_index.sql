-- 0088_terminal_event_asof_index.sql — supporting index for 09-trading-terminal's AS-OF price
-- reconstruction (pipeline/terminal/compute_buckets.py).
--
-- NUMBERING: `ls migrations/*.sql | sort -V | tail` at creation time showed 0087 as the highest
-- file on disk (0087_listing_audit.sql, a parallel frontier of this same block). This is 0088.
--
-- WHY: compute_buckets.py's per-bucket-day AS-OF query does
--   SELECT DISTINCT ON (vehicle_ulid) vehicle_ulid, (new_value->>'price')::numeric AS price
--     FROM vehicle_event WHERE event_type IN ('NEW','PRICE_CHANGE') AND observed_at::date <= $1
--    ORDER BY vehicle_ulid, observed_at DESC
-- Measured live this session: without a (vehicle_ulid, observed_at) index, this required a full
-- sort of ~3M rows PER bucket day (14 real bucket days, see 0086's header) — the first backfill
-- attempt took multiple minutes per day and was aborted. `idx_event_vehicle` (0003) only covers
-- vehicle_ulid alone, forcing an explicit Sort node.
--
-- This index lets PostgreSQL stream the DISTINCT ON via an ordered Index Scan (no separate Sort
-- node) — general-purpose (not filtered to NEW/PRICE_CHANGE, no partial-index constraint), so any
-- future "most recent event for this vehicle" query benefits, not just this job.
--
-- Applied CONCURRENTLY on the live DB THIS SESSION (2026-07-18, before this migration file was
-- written — the live cardeep-pg has other pillars actively writing vehicle_event, and CREATE INDEX
-- CONCURRENTLY avoids taking the write-blocking lock a plain CREATE INDEX would hold for the
-- several seconds this build takes on ~3M rows). This migration file uses the plain (non-
-- CONCURRENTLY) form for a fresh/empty database bring-up, per scripts/migrate.py's own transaction-
-- wrapped execution model (CREATE INDEX CONCURRENTLY cannot run inside a transaction block, so it
-- is NOT compatible with scripts/migrate.py's runner as-is) — `IF NOT EXISTS` makes re-applying
-- against the already-CONCURRENTLY-built live index a no-op, not an error.

CREATE INDEX IF NOT EXISTS idx_event_vehicle_time_desc
    ON vehicle_event (vehicle_ulid, observed_at DESC);

-- Rollback:
-- DROP INDEX IF EXISTS idx_event_vehicle_time_desc;
