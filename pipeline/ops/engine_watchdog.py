"""F1 (00-marketplace-engine) — Watchdog EXTERNAL to the scheduler process.

Why this exists
----------------
``pipeline/ops/silence_watchdog.py`` detects SOURCES that go quiet, but it is a JOB
INSIDE ``pipeline/ops/scheduler.py`` — when the scheduler process itself dies, its own
watchdog dies with it (exactly what happened 2026-06-29: an 18-day-silent motor with
zero alerts, because the alerter was a passenger on the vehicle that crashed).

This module is invoked by an OS-level scheduled task (Windows Task Scheduler unit
``CardeepEngineWatchdog``, see ``docs/runbook/OPERATE.md``), a completely separate
process tree from the scheduler/autopilot container. It shares NO fate with the thing
it watches:
  - runs on the HOST, not inside the ``cardeep-autopilot`` container;
  - reads the DB over the published port (127.0.0.1:5433), never the docker-internal
    hostname;
  - writes its verdict to an append-only external log file REGARDLESS of whether the
    DB itself is reachable — "el apagón de la DB también debe verse" (00-marketplace-
    engine.md F1). A DB outage is exactly the case where an alert ROW cannot be
    written, so the filesystem is the channel of last resort.

Threshold
---------
``ENGINE_STALE_THRESHOLD_MINUTES = 30`` mirrors the badge boundary in
00-marketplace-engine.md §4 ("LATIENDO si age < 2×TICK_INTERVAL = 30 min") — 2× the
15-minute ``TICK_INTERVAL_MINUTES`` scheduler.py:121 uses for its own heartbeat_tick
job. Deliberately a LOCAL constant (not an import of pipeline.ops.scheduler): the
watchdog must not share an import graph, let alone a process, with what it observes —
a bug that breaks the scheduler module at import time must never be able to break the
watchdog too.

Public API
----------
read_engine_lease(conn) -> dict | None
    Best-effort read of scheduler_lease WHERE lock_key = _HARVEST_LOCK_KEY.

classify_engine_status(last_heartbeat, *, now=None, threshold_minutes=None) -> str
    Pure function: "LATIENDO" | "DEGRADADO_PARADO" | "SIN_LEASE". No DB — the unit-test
    surface. (Only two buckets here, not the frontend's 3-way LATIENDO/DEGRADADO/PARADO
    of §4: the watchdog's job is binary — alert or don't — not to render a dashboard.)

fire_engine_down_alert_sync(conn, *, age_minutes, last_heartbeat, holder, pid) -> int
    Dedup-aware INSERT/UPDATE into `alert` (mirrors silence_watchdog.fire_silence_alert_sync
    exactly: SELECT unresolved by origin -> UPDATE or INSERT). origin='engine:heartbeat'.

resolve_engine_alert_if_recovered(conn) -> bool
    Companion sweep (mirrors silence_watchdog's OI-10 zombie fix): closes the open
    'engine:heartbeat' alert once the lease is fresh again. Returns True if it closed one.

run_watchdog_cycle(dsn, log_path, *, now=None) -> dict
    One full check: connect -> read lease -> classify -> alert-or-resolve -> ALWAYS
    append one line to ``log_path``. Never raises. Returns a summary dict (also what
    gets logged), so both the CLI and a future API surface can reuse it.

CLI
---
    python -m pipeline.ops.engine_watchdog          # one check, then exit (Task Scheduler cadence)
    python -m pipeline.ops.engine_watchdog --dry-run  # print the verdict, write no alert/log row
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import psycopg2  # type: ignore[import]
import psycopg2.extras  # for DictCursor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The harvest scheduler's singleton advisory-lock key (scheduler.py:771,
# `_SCHEDULER_SINGLETON_LOCK = 0x43415244`). Duplicated here as a literal — same
# "no shared import graph" reasoning as the threshold above.
_HARVEST_LOCK_KEY: int = 0x43415244  # 1128354372

# 2x TICK_INTERVAL_MINUTES (scheduler.py:121) == the §4 LATIENDO/DEGRADADO boundary.
ENGINE_STALE_THRESHOLD_MINUTES: int = 30

# Host-reachable DSN (published port, NOT the docker-internal `cardeep-pg` hostname —
# this process runs OUTSIDE any container). Keyword form, same shape as scheduler.py's
# own _RAW_DSN default, so the watchdog is a drop-in host-side sibling, not a fork.
_DEFAULT_DSN: str = (
    "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only"
)

_DEFAULT_LOG_PATH: Path = Path(__file__).resolve().parent.parent.parent / "state" / "engine_watchdog.log"

_ALERT_ORIGIN: str = "engine:heartbeat"
_SEV_CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Pure classification (no DB — the unit-test surface)
# ---------------------------------------------------------------------------

def classify_engine_status(
    last_heartbeat: Optional[datetime],
    *,
    now: Optional[datetime] = None,
    threshold_minutes: Optional[int] = None,
) -> str:
    """Classify engine health from a single ``last_heartbeat`` value.

    Returns one of:
      "SIN_LEASE"         -- no lease row at all (never started, or migration 0054
                              missing). Treated as down: cannot vouch for a live engine.
      "LATIENDO"          -- age <= threshold (fresh).
      "DEGRADADO_PARADO"  -- age > threshold (stale enough to alert).

    Boundary is strict (age must EXCEED the threshold), mirroring
    silence_watchdog.find_silent_sources' "> threshold" convention.
    """
    if last_heartbeat is None:
        return "SIN_LEASE"

    threshold = ENGINE_STALE_THRESHOLD_MINUTES if threshold_minutes is None else threshold_minutes
    reference = datetime.now(timezone.utc) if now is None else _as_aware_utc(now)
    age = reference - _as_aware_utc(last_heartbeat)

    if age > timedelta(minutes=threshold):
        return "DEGRADADO_PARADO"
    return "LATIENDO"


def _as_aware_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


# ---------------------------------------------------------------------------
# DB layer (sync psycopg2 — the watchdog is a short-lived CLI invocation, no asyncio)
# ---------------------------------------------------------------------------

def read_engine_lease(conn: "psycopg2.extensions.connection") -> Optional[dict[str, Any]]:
    """Best-effort read of the harvest scheduler's lease row. None if absent/unreadable."""
    sql = (
        "SELECT lock_key, holder, pid, started_at, last_heartbeat "
        "FROM scheduler_lease WHERE lock_key = %(lock_key)s"
    )
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, {"lock_key": _HARVEST_LOCK_KEY})
            row = cur.fetchone()
    except psycopg2.Error:
        conn.rollback()
        return None
    if row is None:
        return None
    return dict(row)


def fire_engine_down_alert_sync(
    conn: "psycopg2.extensions.connection",
    *,
    age_minutes: float,
    last_heartbeat: Optional[datetime],
    holder: Optional[str],
    pid: Optional[int],
    threshold_minutes: Optional[int] = None,
) -> int:
    """Dedup-aware critical alert for a stale/missing engine heartbeat.

    Mirrors silence_watchdog.fire_silence_alert_sync's exact contract: SELECT the
    open alert for this origin -> UPDATE if found, INSERT if not. Never a duplicate
    row for a persisting outage.

    ``threshold_minutes`` names the threshold that was ACTUALLY used for this verdict
    (defaults to the production constant) — so an F1 drill run with
    ``--threshold-minutes`` writes an alert message that matches the decision it made,
    instead of always citing the production default regardless of what fired it.
    """
    effective_threshold = (
        ENGINE_STALE_THRESHOLD_MINUTES if threshold_minutes is None else threshold_minutes
    )
    message = (
        f"engine heartbeat stale {age_minutes:.1f}min "
        f"(threshold {effective_threshold}min), holder={holder}, pid={pid}"
        if last_heartbeat is not None
        else "engine heartbeat MISSING — scheduler_lease has no row for the harvest lock"
    )
    payload = json.dumps({
        "age_minutes": round(age_minutes, 2) if last_heartbeat is not None else None,
        "threshold_minutes": effective_threshold,
        "last_heartbeat": last_heartbeat.isoformat() if last_heartbeat else None,
        "holder": holder,
        "pid": pid,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    })

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM alert WHERE origin=%s AND resolved_at IS NULL "
            "ORDER BY created_at DESC LIMIT 1",
            (_ALERT_ORIGIN,),
        )
        existing = cur.fetchone()
        if existing is not None:
            alert_id: int = existing[0]
            cur.execute(
                "UPDATE alert SET message=%s, payload=%s::jsonb WHERE id=%s",
                (message, payload, alert_id),
            )
        else:
            cur.execute(
                "INSERT INTO alert (origin, severity, message, payload) "
                "VALUES (%s, %s, %s, %s::jsonb) RETURNING id",
                (_ALERT_ORIGIN, _SEV_CRITICAL, message, payload),
            )
            row = cur.fetchone()
            alert_id = row[0]  # type: ignore[index]
    conn.commit()
    return alert_id


def resolve_engine_alert_if_recovered(conn: "psycopg2.extensions.connection") -> bool:
    """Close the open 'engine:heartbeat' alert if the lease is fresh again.

    Companion sweep to fire_engine_down_alert_sync — same zombie-alert fix pattern as
    silence_watchdog.resolve_recovered_silence_alerts, specialized to a single origin
    (no per-source join needed: there is exactly one engine).
    """
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE alert SET resolved_at = now() "
            "WHERE origin=%s AND resolved_at IS NULL",
            (_ALERT_ORIGIN,),
        )
        closed = cur.rowcount > 0
    conn.commit()
    return closed


# ---------------------------------------------------------------------------
# External channel: append-only log file, written REGARDLESS of DB reachability.
# ---------------------------------------------------------------------------

def _append_log(log_path: Path, record: dict[str, Any]) -> None:
    """Best-effort append of one JSON line. Never raises (a logging failure must not
    make the watchdog crash-loop the scheduled task)."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except OSError:
        pass  # filesystem is the LAST resort; if even this fails there is nothing left to do


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_watchdog_cycle(
    dsn: str = _DEFAULT_DSN,
    log_path: Path = _DEFAULT_LOG_PATH,
    *,
    now: Optional[datetime] = None,
    dry_run: bool = False,
    threshold_minutes: Optional[int] = None,
) -> dict[str, Any]:
    """One full watchdog check. Never raises. Always appends one record to log_path
    (unless dry_run) — the external, DB-independent evidence trail.

    ``threshold_minutes`` overrides ``ENGINE_STALE_THRESHOLD_MINUTES`` for THIS call only.
    TEST/DRILL USE ONLY (e.g. F1 destructive-test acceleration: kill the scheduler for real,
    then verify detection at a shorter threshold instead of waiting out the full 30 min) — the
    installed Task Scheduler cadence never passes this flag, so production always alerts at the
    real 30-min boundary already covered by TestClassifyEngineStatus's boundary tests.
    """
    ts = (now or datetime.now(timezone.utc)).isoformat()
    effective_threshold = (
        ENGINE_STALE_THRESHOLD_MINUTES if threshold_minutes is None else threshold_minutes
    )

    try:
        conn = psycopg2.connect(dsn, connect_timeout=5)
        conn.autocommit = False
    except psycopg2.Error as exc:
        record = {
            "ts": ts,
            "status": "DB_UNREACHABLE",
            "detail": str(exc).strip(),
        }
        if not dry_run:
            _append_log(log_path, record)
        return record

    try:
        lease = read_engine_lease(conn)
        last_heartbeat = lease["last_heartbeat"] if lease else None
        holder = lease["holder"] if lease else None
        pid = lease["pid"] if lease else None
        status = classify_engine_status(
            last_heartbeat, now=now, threshold_minutes=effective_threshold)

        if last_heartbeat is not None:
            reference = now or datetime.now(timezone.utc)
            age_minutes = (
                _as_aware_utc(reference) - _as_aware_utc(last_heartbeat)
            ).total_seconds() / 60.0
        else:
            age_minutes = None

        alert_id: Optional[int] = None
        resolved = False
        if not dry_run:
            if status in ("DEGRADADO_PARADO", "SIN_LEASE"):
                alert_id = fire_engine_down_alert_sync(
                    conn,
                    age_minutes=age_minutes if age_minutes is not None else float("inf"),
                    last_heartbeat=last_heartbeat,
                    holder=holder,
                    pid=pid,
                    threshold_minutes=effective_threshold,
                )
            else:
                resolved = resolve_engine_alert_if_recovered(conn)

        record = {
            "ts": ts,
            "status": status,
            "age_minutes": round(age_minutes, 2) if age_minutes is not None else None,
            "threshold_minutes": effective_threshold,
            "holder": holder,
            "pid": pid,
            "last_heartbeat": last_heartbeat.isoformat() if last_heartbeat else None,
            "alert_id": alert_id,
            "alert_resolved": resolved,
        }
        if not dry_run:
            _append_log(log_path, record)
        return record
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cardeep F1 external engine watchdog — one heartbeat check, independent "
            "of the scheduler process (Task Scheduler cadence, not a daemon loop)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the verdict; write NO alert row and NO log line.",
    )
    parser.add_argument(
        "--dsn",
        default=os.environ.get("CARDEEP_WATCHDOG_DSN", _DEFAULT_DSN),
        help="psycopg2 DSN (default: host-published 127.0.0.1:5433, env CARDEEP_WATCHDOG_DSN).",
    )
    parser.add_argument(
        "--log-path",
        default=os.environ.get("CARDEEP_WATCHDOG_LOG", str(_DEFAULT_LOG_PATH)),
        help="Append-only external log file (default: state/engine_watchdog.log).",
    )
    parser.add_argument(
        "--threshold-minutes",
        type=int,
        default=None,
        help=(
            "TEST/DRILL ONLY: override the 30-min stale threshold for this run (e.g. to "
            "accelerate an F1 destructive-test drill without waiting out the real window). "
            "The installed CardeepEngineWatchdog scheduled task never passes this flag."
        ),
    )
    args = parser.parse_args()

    record = run_watchdog_cycle(
        dsn=args.dsn, log_path=Path(args.log_path), dry_run=args.dry_run,
        threshold_minutes=args.threshold_minutes)
    print(json.dumps(record, indent=2, default=str))
    # Exit non-zero on a bad verdict so Task Scheduler's own history flags failing runs too.
    if record.get("status") in ("DB_UNREACHABLE", "DEGRADADO_PARADO", "SIN_LEASE"):
        sys.exit(1)


if __name__ == "__main__":
    main()
