-- 0085_engine_heartbeat_log.sql — F6, INSERT-only uptime ledger for the single-producer lease.
-- Additive, idempotent, reversible. (plans/cardeep-omni/00-marketplace-engine.md F6 / §5.1 item 1)
--
-- WHY. scheduler_lease (migration 0054) is an UPSERT of exactly one row per lock_key: it can only
-- ever answer "when did the current holder last beat", never "what was the uptime over the last
-- 30/90 days" — that history is destroyed on every UPSERT. This migration adds the append-only
-- ledger the F6 track record is computed from: one row per heartbeat, never updated, never
-- individually deleted — only purged in bulk by age (pipeline/ops/lock_heartbeat.py
-- purge_heartbeat_log(), doctrine: INSERT-only + purge by range, never UPDATE of a non-mutated
-- row, the same anti-dead-tuple discipline the rest of the stack already follows for
-- vehicle_event/harvest_run).
--
-- WRITER. pipeline/ops/lock_heartbeat.py::record_heartbeat() inserts one row here immediately
-- after the scheduler_lease UPSERT succeeds (same call site, same cadence — every
-- heartbeat_interval_minutes(), default 2 min). Best-effort: a DB without this migration applied
-- keeps writing scheduler_lease exactly as before (the ledger insert is wrapped separately and
-- degrades to a one-time warning, never breaking the lease heartbeat itself).
--
-- READER. pipeline/ops/engine_uptime.py::compute_uptime_report() buckets beat_at into fixed
-- 15-minute windows (the same cadence as TICK_INTERVAL_MINUTES, scheduler.py:121) and reports the
-- % of windows with >=1 heartbeat present, over whatever span has actually been observed (never
-- fabricating pre-ledger history as downtime — see that module's docstring). Served at
-- GET /engine/status (services/api/routers/ops.py, F5).

CREATE TABLE IF NOT EXISTS engine_heartbeat_log (
    id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lock_key BIGINT NOT NULL,
    holder   TEXT,
    pid      INTEGER,
    beat_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The uptime query is always "beats for this lock_key in [start, end)" ordered by time — a single
-- composite index serves both the WHERE and the ORDER BY without a separate sort.
CREATE INDEX IF NOT EXISTS idx_engine_heartbeat_log_lock_beat
    ON engine_heartbeat_log (lock_key, beat_at);

COMMENT ON TABLE engine_heartbeat_log IS
    'F6 (00-marketplace-engine.md): INSERT-only heartbeat history per single-producer advisory '
    'lock (harvest 1128354372, discovery 1128354373). One row per heartbeat tick (~every 2 min); '
    'never UPDATEd; purged only in bulk by age (purge_heartbeat_log, default retention 90 days). '
    'The uptime 30/90-day track record at GET /engine/status is computed from this table — '
    'scheduler_lease (0054) alone cannot answer that question, it only ever holds the latest beat.';

-- Rollback:
-- DROP TABLE IF EXISTS engine_heartbeat_log;
