"""Advisory-lock heartbeat + stale-lease detection for the single-producer daemons.

Why this exists
---------------
Both long-lived daemons guard against a second producer on the host with a PG
**session advisory lock** held on a dedicated autocommit connection:

  * harvest scheduler  — lock 0x43415244       (pipeline/ops/scheduler.py:842-844)
  * discovery daemon   — lock 0x43415244 + 1   (pipeline/discover_schedule.py:50,237-238)

A session advisory lock AUTO-RELEASES when its connection closes. On a CLEAN exit
that is instantaneous and correct. On a HARD crash / SIGKILL the OS eventually
closes the socket, but the PG backend keeps the dead session (and its lock) until
TCP keepalive / idle reaping fires — a window during which a restart hits
`pg_try_advisory_lock == false` and SystemExits, orphaning the daemon.

The advisory lock stays the hard mutex. This module adds an OBSERVABILITY layer
on top of it: a `scheduler_lease` row per lock_key whose `last_heartbeat` is bumped
on a timer by the live holder. A would-be successor can then read the lease and
distinguish "a healthy holder is alive" (recent heartbeat) from "the prior holder
is presumed dead" (heartbeat older than the TTL) — turning a silent orphan into a
loud, diagnosable CRITICAL log line.

We deliberately do NOT `pg_advisory_unlock` another session's lock — cross-session
unlock of a session advisory lock is unsupported/unsafe. "Auto-release" here means
"observable + retry on the next start once PG reaps the dead session", NOT
instantaneous takeover. See the design risk note for the explicit non-promise.

Design contract
---------------
  * Lease table schema lives in migrations/0054_scheduler_heartbeat.sql (additive,
    `CREATE TABLE IF NOT EXISTS scheduler_lease(...)`). This module NEVER creates it.
  * Every DB call here is BEST-EFFORT: wrapped so a daemon started against a DB that
    has not yet applied 0054 still boots byte-identically (the feature is simply inert
    and logs one warning). This is the backward-compat guarantee from the design spec.
  * All functions take an already-open **psycopg2 autocommit connection** — the very
    `_lock_conn` / `lock` the daemon already holds the advisory lock on. €0: no new
    connection, single-producer so no write contention on the lease row.

Public API
----------
lease_ttl_minutes() -> int
    TTL in minutes (env CARDEEP_LEASE_TTL_MIN, default 6 = 3× the 2-min heartbeat).

heartbeat_interval_minutes() -> int
    Heartbeat cadence in minutes (env CARDEEP_LEASE_HEARTBEAT_MIN, default 2).

is_lease_stale(last_heartbeat, *, now=None, ttl_minutes=None) -> bool
    Pure TTL predicate: True when now - last_heartbeat exceeds the TTL. No DB.

record_heartbeat(conn, lock_key, *, holder=None, pid=None) -> bool
    Best-effort UPSERT bumping last_heartbeat=now() for lock_key. Returns whether
    the write landed (False = lease table missing / DB error, logged, never raised).

read_lease(conn, lock_key) -> dict | None
    Best-effort read of the scheduler_lease row for lock_key, or None if absent /
    table missing. Never raises.

check_and_clear_stale_lease(conn, lock_key, *, now=None, ttl_minutes=None) -> bool
    Pre-acquire diagnostic: if a lease exists and is stale, log CRITICAL and return
    True (caller may then retry pg_try_advisory_lock — the dead session's lock will
    already be gone once PG has reaped it). Returns False when the lease is fresh,
    absent, or unreadable. Does NOT touch the advisory lock and does NOT delete the
    lease row (the live holder's next heartbeat / next acquire overwrites it).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import psycopg2  # type: ignore[import]
import psycopg2.extras  # for DictCursor

log = logging.getLogger("cardeep.lock_heartbeat")

# ---------------------------------------------------------------------------
# Cadence / TTL configuration
# ---------------------------------------------------------------------------
# Heartbeat fires every HEARTBEAT_MIN minutes; a lease is considered stale once its
# last_heartbeat is older than TTL_MIN. Default TTL = 3× the heartbeat interval so a
# single missed beat (e.g. a slow tick) never false-positives a healthy holder.
_DEFAULT_HEARTBEAT_MIN: int = 2
_DEFAULT_TTL_MIN: int = 6  # 3× the 2-min heartbeat — matches the design spec

# The lease table from migration 0054. Centralized so a rename is a one-line change.
_LEASE_TABLE: str = "scheduler_lease"

# psycopg2 SQLSTATE for "undefined_table" — raised when 0054 has not been applied.
_UNDEFINED_TABLE: str = "42P01"


def _positive_int_env(name: str, default: int) -> int:
    """Read a strictly-positive int from the environment, falling back on garbage.

    Non-numeric or non-positive values fall back to ``default`` with a warning rather
    than crashing a daemon at startup over a typo'd env var (fail-soft for config).
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw.strip())
    except (ValueError, AttributeError):
        log.warning("%s=%r is not an integer; using default %d", name, raw, default)
        return default
    if value <= 0:
        log.warning("%s=%r must be > 0; using default %d", name, raw, default)
        return default
    return value


def heartbeat_interval_minutes() -> int:
    """Heartbeat cadence in minutes (env CARDEEP_LEASE_HEARTBEAT_MIN, default 2)."""
    return _positive_int_env("CARDEEP_LEASE_HEARTBEAT_MIN", _DEFAULT_HEARTBEAT_MIN)


def lease_ttl_minutes() -> int:
    """Stale-lease TTL in minutes (env CARDEEP_LEASE_TTL_MIN, default 6)."""
    return _positive_int_env("CARDEEP_LEASE_TTL_MIN", _DEFAULT_TTL_MIN)


# ---------------------------------------------------------------------------
# Pure TTL math (no DB — the unit-test surface)
# ---------------------------------------------------------------------------

def _as_aware_utc(ts: datetime) -> datetime:
    """Coerce a datetime to a tz-aware UTC instant.

    Postgres TIMESTAMPTZ comes back tz-aware via psycopg2, but a naive datetime
    (e.g. a hand-built test value or a TIMESTAMP-without-tz column) is treated as
    already being in UTC so the subtraction below never raises a naive/aware mix.
    """
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def is_lease_stale(
    last_heartbeat: Optional[datetime],
    *,
    now: Optional[datetime] = None,
    ttl_minutes: Optional[int] = None,
) -> bool:
    """Return True when ``last_heartbeat`` is older than the TTL relative to ``now``.

    Pure function — the heart of stale detection, fully unit-testable with no DB.

    A ``None`` last_heartbeat is treated as STALE: a lease row that exists but was
    never beaten (or whose column is NULL) cannot vouch for a living holder.

    The boundary is strict: a heartbeat exactly TTL old is NOT yet stale (age must
    EXCEED the TTL), mirroring the silence_watchdog "> threshold" convention.
    """
    if last_heartbeat is None:
        return True

    ttl = lease_ttl_minutes() if ttl_minutes is None else ttl_minutes
    reference = datetime.now(timezone.utc) if now is None else _as_aware_utc(now)
    age = reference - _as_aware_utc(last_heartbeat)
    return age > timedelta(minutes=ttl)


# ---------------------------------------------------------------------------
# Best-effort DB layer (psycopg2, autocommit connection supplied by the caller)
# ---------------------------------------------------------------------------

def record_heartbeat(
    conn: "psycopg2.extensions.connection",
    lock_key: int,
    *,
    holder: Optional[str] = None,
    pid: Optional[int] = None,
) -> bool:
    """Best-effort UPSERT bumping last_heartbeat=now() for ``lock_key``.

    Called both at acquire time (to claim/refresh the lease) and on the periodic
    heartbeat job. Single-producer: only the lock holder ever writes its lock_key,
    so the UPSERT never contends.

    ``holder`` / ``pid`` are recorded on first insert and refreshed on every beat so
    the lease always names the CURRENT holder (a successor that took over after a
    stale reap overwrites the dead holder's identity). ``pid`` defaults to the live
    process pid when not supplied.

    Returns True if the write landed, False on any failure (table missing or DB
    error). NEVER raises — a heartbeat failure must not kill the daemon.
    """
    effective_pid = os.getpid() if pid is None else pid
    sql = f"""
        INSERT INTO {_LEASE_TABLE} (lock_key, holder, pid, started_at, last_heartbeat)
        VALUES (%(lock_key)s, %(holder)s, %(pid)s, now(), now())
        ON CONFLICT (lock_key) DO UPDATE
            SET holder = EXCLUDED.holder,
                pid = EXCLUDED.pid,
                last_heartbeat = now()
    """
    params = {"lock_key": lock_key, "holder": holder, "pid": effective_pid}
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        return True
    except psycopg2.errors.UndefinedTable:  # type: ignore[attr-defined]
        _warn_missing_lease_table(conn)
        return False
    except psycopg2.Error as exc:  # any other DB error — stay best-effort
        log.warning("lease heartbeat write failed for lock_key=%s: %s", lock_key, exc)
        _rollback_quietly(conn)
        return False


def read_lease(
    conn: "psycopg2.extensions.connection",
    lock_key: int,
) -> Optional[dict[str, Any]]:
    """Best-effort read of the scheduler_lease row for ``lock_key``.

    Returns a dict with keys lock_key, holder, pid, started_at, last_heartbeat, or
    None when the row is absent, the table is missing, or the read errors. Never
    raises.
    """
    sql = f"""
        SELECT lock_key, holder, pid, started_at, last_heartbeat
        FROM {_LEASE_TABLE}
        WHERE lock_key = %(lock_key)s
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, {"lock_key": lock_key})
            row = cur.fetchone()
    except psycopg2.errors.UndefinedTable:  # type: ignore[attr-defined]
        _warn_missing_lease_table(conn)
        return None
    except psycopg2.Error as exc:
        log.warning("lease read failed for lock_key=%s: %s", lock_key, exc)
        _rollback_quietly(conn)
        return None

    if row is None:
        return None
    return {
        "lock_key": row["lock_key"],
        "holder": row["holder"],
        "pid": row["pid"],
        "started_at": row["started_at"],
        "last_heartbeat": row["last_heartbeat"],
    }


def check_and_clear_stale_lease(
    conn: "psycopg2.extensions.connection",
    lock_key: int,
    *,
    now: Optional[datetime] = None,
    ttl_minutes: Optional[int] = None,
) -> bool:
    """Pre-acquire stale-lease diagnostic. Returns True iff a STALE lease was found.

    Call this immediately BEFORE `pg_try_advisory_lock`. Behaviour:
      * No lease row / table missing / read error  -> return False (nothing to say;
        proceed to acquire as usual — likely a clean start or pre-0054 DB).
      * Lease present and FRESH                     -> return False (a healthy holder
        is alive; the advisory lock will correctly refuse the second producer).
      * Lease present and STALE                     -> log CRITICAL naming the dead
        holder/pid and return True. The caller may proceed to (re)try the advisory
        lock: once PG has reaped the crashed session, the lock is free and acquire
        succeeds; if the session has NOT yet been reaped, the advisory lock still
        refuses and the daemon SystemExits as before — but now with a logged reason.

    Despite the name we do NOT delete the lease row or unlock anything: the lease is
    overwritten by the next holder's `record_heartbeat`. "Clear" refers to clearing
    the AMBIGUITY (crashed vs healthy holder), not deleting state. We never call
    pg_advisory_unlock on a foreign session — that is unsafe by design.
    """
    lease = read_lease(conn, lock_key)
    if lease is None:
        return False

    last_heartbeat = lease.get("last_heartbeat")
    if not is_lease_stale(last_heartbeat, now=now, ttl_minutes=ttl_minutes):
        return False

    ttl = lease_ttl_minutes() if ttl_minutes is None else ttl_minutes
    log.critical(
        "stale lease detected for lock_key=%s (holder=%r pid=%s last_heartbeat=%s, "
        "older than TTL=%dmin); prior holder presumed dead — retrying advisory lock",
        lock_key,
        lease.get("holder"),
        lease.get("pid"),
        last_heartbeat,
        ttl,
    )
    return True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _warn_missing_lease_table(conn: "psycopg2.extensions.connection") -> None:
    """Log the one-time 'migration 0054 not applied' warning and roll back cleanly.

    Even on an autocommit connection an aborted statement can leave the session in a
    failed state; roll back defensively so the caller's connection stays usable.
    """
    log.warning(
        "%s table is missing — migration 0054_scheduler_heartbeat.sql not applied; "
        "lease heartbeat/TTL is INERT (daemon runs byte-identically without it)",
        _LEASE_TABLE,
    )
    _rollback_quietly(conn)


def _rollback_quietly(conn: "psycopg2.extensions.connection") -> None:
    """Best-effort rollback so a failed statement never poisons the held connection."""
    try:
        conn.rollback()
    except psycopg2.Error:
        pass
