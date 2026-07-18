-- 0094_wanted_matcher_index.sql — 08-forum-community F2: supporting index for the
-- "Se busca" matcher (pipeline/wanted/matcher.py::build_candidate_query).
--
-- Measured, not assumed (carta §9 F2 verification requirement: "benchmark del matcher a
-- escala del inventario real — EXPLAIN + indices probados"): EXPLAIN ANALYZE against the
-- live cardeep-pg (2.67M vehicle rows) for `WHERE status='available' AND upper(trim(make))
-- = ANY(...)` WITHOUT this index took 5.6s (parallel sequential scan of the whole table,
-- 843k rows discarded by the filter for a single make). Same precedent as
-- 09-trading-terminal's migrations/0088_terminal_event_asof_index.sql: an ADDITIVE index on
-- a table this pilar does not own, added after measuring a real bottleneck, not before.
--
-- Additive, idempotent, reversible.

CREATE INDEX IF NOT EXISTS idx_vehicle_make_upper_available
    ON vehicle (upper(trim(make)))
    WHERE status = 'available';

-- Rollback:
-- DROP INDEX IF EXISTS idx_vehicle_make_upper_available;
