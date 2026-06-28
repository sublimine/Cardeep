-- 0068_orchestration_country.sql — OI-10 de-blinding (COUNTRY-PACK-CONTRACT.md §6): give the
-- ORCHESTRATION/OBSERVABILITY tables a country dimension WITHOUT changing ANY Spain (ES) behavior.
-- Additive mirror of 0052 (the geo/entity country dimension): every existing row stays ES and the
-- single-tenant scheduler/watchdog result set is byte-identical to today.
--
-- WHY. The contract's spine-finding: country_code was threaded into the SCHEMA (0052/0053) and the
-- cdp_code prefix, but the ORCHESTRATION layer stayed country-blind. source_health (0004) — the
-- table the scheduler's _due_sources and the silence watchdog's find_silent_sources read — has no
-- country dimension, so a 2nd country's producers cannot be scoped to a tenant. This migration adds
-- the missing dimension to the three orchestration tables that exist:
--   * source_health  (0004, PK source_key)          — DUE selection + silence detection read it.
--   * harvest_run    (0013, PK id, has source_key)   — the per-run audit trail.
--   * scheduler_lease (0054, PK lock_key)            — the single-producer observable lease.
-- (source_breaker / repair_attempt are NOT scoped here: they are keyed by source_key, derive their
-- tenant transitively from source_health, and no producer query filters them by country — YAGNI.)
--
-- WHY ADDITIVE / ZERO-RISK (byte-identical ES). CHAR(2) NOT NULL DEFAULT 'ES' stamps every existing
-- row 'ES' atomically (implicit, complete, zero-NULL backfill — no NOT NULL violation possible),
-- exactly as 0052 did for geo/entity. 'ES' is exactly 2 chars so CHAR(2) carries no blank-padding
-- ambiguity. ADD COLUMN touches no PK, no FK, no existing value: source_health.source_key,
-- harvest_run.id and scheduler_lease.lock_key keep resolving. With active_countries()==['ES'] every
-- new `WHERE country_code = ANY(...)` selects the same all-ES rows, so the scheduler harvests and the
-- watchdog detects exactly the same sources as before.
--
-- Idempotent: ADD COLUMN IF NOT EXISTS + CREATE INDEX IF NOT EXISTS — re-running is a no-op.
-- Reversible: the commented rollback section is the LAST `-- Rollback:` marker in the file (the
-- runner, scripts/migrate.py, strips everything from that marker onward; the header above only
-- MENTIONS rollback, it does not carry the literal marker, so the forward DDL is never truncated).

-- 1. Add the country dimension to the three orchestration tables. CHAR(2), NOT NULL, DEFAULT 'ES'.
--    DEFAULT 'ES' implicitly backfills every existing row as Spain.
ALTER TABLE source_health   ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE harvest_run     ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';
ALTER TABLE scheduler_lease ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES';

-- 2. Indexes for the country-scoped producer queries (cheap, additive). source_health is filtered
--    by country on every heartbeat tick (_due_sources) and silence sweep (find_silent_sources);
--    harvest_run gets one for future country-scoped audits. scheduler_lease holds at most a handful
--    of rows (one per advisory lock) so it needs no index.
CREATE INDEX IF NOT EXISTS idx_source_health_country ON source_health (country_code);
CREATE INDEX IF NOT EXISTS idx_harvest_run_country   ON harvest_run (country_code);

-- Rollback:
-- DROP INDEX IF EXISTS idx_harvest_run_country;
-- DROP INDEX IF EXISTS idx_source_health_country;
-- ALTER TABLE scheduler_lease DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE harvest_run     DROP COLUMN IF EXISTS country_code;
-- ALTER TABLE source_health   DROP COLUMN IF EXISTS country_code;
