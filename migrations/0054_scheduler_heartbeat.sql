-- 0054_scheduler_heartbeat.sql — FASE-2 ops-hardening: observable single-producer leases.
--
-- PURPOSE. The two long-lived daemons (harvest lock 1128354372, discovery lock 1128354373)
-- guard against a second producer with a PG SESSION advisory lock. A session lock auto-releases
-- on a CLEAN exit, but on a HARD crash (SIGKILL/OOM) the PG backend keeps the dead session — and
-- its lock — until TCP keepalive / idle reaping fires. During that window a restart hits
-- pg_try_advisory_lock == false and SystemExits, silently orphaning the daemon.
--
-- This table adds an OBSERVABILITY layer (NOT a second mutex): each live holder bumps
-- last_heartbeat on a timer; a would-be successor reads the lease and can distinguish a healthy
-- holder (recent heartbeat) from a presumed-dead one (heartbeat older than the TTL), turning a
-- silent orphan into a loud CRITICAL log line. We NEVER pg_advisory_unlock another session's lock
-- (cross-session unlock is unsafe) — "auto-release" stays "observable + retry on next start".
--
-- WHY ADDITIVE / ZERO-RISK: this migration only CREATEs a brand-new table (IF NOT EXISTS); it
-- touches no existing table, column, FK, or row. pipeline/ops/lock_heartbeat.py reads/writes this
-- table BEST-EFFORT (every call wrapped; UndefinedTable => inert + one warning), so a daemon
-- started against a DB WITHOUT this migration boots byte-identically. Applying it simply lets the
-- heartbeat/TTL feature write. Reversible: DROP the table (see Rollback) — nothing depends on it.
--
-- Columns mirror pipeline/ops/lock_heartbeat.py exactly:
--   lock_key       the advisory lock integer (1128354372 harvest / 1128354373 discovery), PK.
--   holder         free-text identity of the current holder (host/daemon name), refreshed/beat.
--   pid            OS pid of the current holder, refreshed on every beat.
--   started_at     when the current holder first claimed the lease.
--   last_heartbeat bumped to now() on every heartbeat; the staleness/TTL signal.

CREATE TABLE IF NOT EXISTS scheduler_lease (
    lock_key       BIGINT PRIMARY KEY,
    holder         TEXT,
    pid            INTEGER,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE scheduler_lease IS
    'FASE-2 ops-hardening: observable heartbeat/lease per single-producer advisory lock '
    '(harvest 1128354372, discovery 1128354373). Best-effort observability layer over the '
    'session advisory lock; see pipeline/ops/lock_heartbeat.py and docs/DEPLOY-DURABLE-DAEMONS.md.';

-- Rollback:
-- DROP TABLE IF EXISTS scheduler_lease;
