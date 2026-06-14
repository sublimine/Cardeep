"""B2.4 — Silence watchdog.

Detects sources that have gone silent: their last_ok (or last_fail) timestamp
is more than 2× their harvest_interval_hours in the past. These sources are
INVISIBLE to the passive S-HEALTH system because they never call record_run
(the connector simply never runs, or always crashes before writing health rows).

Public API
----------
find_silent_sources(conn) -> list[dict]
    Pure read: returns every silent source from source_health.

run_silence_watchdog(conn) -> list[str]
    Calls find_silent_sources, then fires one alert per silent source via the
    same dedup logic as health.fire_alert (SELECT + UPDATE or INSERT).
    Returns the list of source_keys that triggered an alert.

fire_silence_alert_sync(conn, source_key, hours_silent, interval_h, is_tier1)
    Internal: write the dedup-aware alert using psycopg2 (sync). Mirrors the
    asyncpg fire_alert / build_origin contract from health.py without pulling
    in the async runtime.

Both find_silent_sources and run_silence_watchdog accept a **psycopg2
connection** (the scheduler runs a synchronous event loop — no asyncio).

CLI (read-only)
---------------
Invoked by the scheduler --check-silence flag:
    python -m pipeline.ops.scheduler --check-silence
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import psycopg2  # type: ignore[import]
import psycopg2.extras  # for DictCursor

log = logging.getLogger("cardeep.silence_watchdog")

# ---------------------------------------------------------------------------
# Silence threshold: more than 2× harvest_interval_hours without a response.
# ---------------------------------------------------------------------------
SILENCE_MULTIPLIER: int = 2

# Severity mapping: tier1 → critical, others → warning.
_SEV_CRITICAL = "critical"
_SEV_WARNING = "warning"


# ---------------------------------------------------------------------------
# Silence detection (pure read, psycopg2)
# ---------------------------------------------------------------------------

def find_silent_sources(conn: "psycopg2.extensions.connection") -> list[dict[str, Any]]:
    """Return every source in source_health that is SILENT.

    A source is silent when:
        now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
            > SILENCE_MULTIPLIER * harvest_interval_hours * interval '1 hour'

    Returns a list of dicts with keys:
        source_key, last_ok, last_fail, harvest_interval_hours, is_tier1,
        hours_silent   (float — fractional hours since the last event)
    """
    sql = """
        SELECT
            source_key,
            last_ok,
            last_fail,
            harvest_interval_hours,
            is_tier1,
            EXTRACT(EPOCH FROM (
                now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
            )) / 3600.0  AS hours_silent
        FROM source_health
        WHERE
            now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
                > %(multiplier)s * harvest_interval_hours * interval '1 hour'
        ORDER BY hours_silent DESC
    """
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql, {"multiplier": SILENCE_MULTIPLIER})
        rows = cur.fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        result.append({
            "source_key": row["source_key"],
            "last_ok": row["last_ok"],
            "last_fail": row["last_fail"],
            "harvest_interval_hours": row["harvest_interval_hours"],
            "is_tier1": row["is_tier1"],
            "hours_silent": float(row["hours_silent"]),
        })
    return result


# ---------------------------------------------------------------------------
# Alert firing (sync psycopg2 — mirrors health.fire_alert dedup contract)
# ---------------------------------------------------------------------------

def _build_origin(source_key: str, phase: str, cdp_code: str | None = None) -> str:
    """Canonical origin key: '<source_key>:<phase>[:<cdp_code>]'.

    Mirrors health.build_origin() without importing the async module.
    """
    return f"{source_key}:{phase}:{cdp_code}" if cdp_code else f"{source_key}:{phase}"


def fire_silence_alert_sync(
    conn: "psycopg2.extensions.connection",
    *,
    source_key: str,
    hours_silent: float,
    harvest_interval_hours: int,
    is_tier1: bool,
) -> int:
    """Write a silence alert with full dedup semantics (sync/psycopg2).

    Dedup contract (mirrors health.fire_alert §3.4): if an UNRESOLVED alert
    already exists for this exact origin, UPDATE its message+payload instead of
    inserting a duplicate row. Returns the alert id (existing or new).
    """
    origin = _build_origin(source_key, "silence")
    severity = _SEV_CRITICAL if is_tier1 else _SEV_WARNING
    message = (
        f"source silent {hours_silent:.1f}h, expected every {harvest_interval_hours}h"
    )
    payload = json.dumps({
        "source_key": source_key,
        "hours_silent": round(hours_silent, 2),
        "harvest_interval_hours": harvest_interval_hours,
        "is_tier1": is_tier1,
        "silence_multiplier": SILENCE_MULTIPLIER,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    })

    with conn.cursor() as cur:
        # Dedup: look for an unresolved alert on this exact origin.
        cur.execute(
            "SELECT id FROM alert "
            "WHERE origin=%s AND resolved_at IS NULL "
            "ORDER BY created_at DESC LIMIT 1",
            (origin,),
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
                (origin, severity, message, payload),
            )
            row = cur.fetchone()
            alert_id = row[0]  # type: ignore[index]

    conn.commit()
    return alert_id


# ---------------------------------------------------------------------------
# Watchdog runner
# ---------------------------------------------------------------------------

def run_silence_watchdog(conn: "psycopg2.extensions.connection") -> list[str]:
    """Detect silent sources and fire one dedup-aware alert per source.

    Returns the list of source_keys for which an alert was fired (or updated).
    Does NOT raise — individual alert failures are logged and skipped so one
    broken alert does not abort the rest of the watchdog cycle.
    """
    silent = find_silent_sources(conn)
    if not silent:
        log.info("silence_watchdog: no silent sources detected")
        return []

    log.info("silence_watchdog: %d silent source(s) detected", len(silent))
    alerted: list[str] = []

    for src in silent:
        source_key: str = src["source_key"]
        hours_silent: float = src["hours_silent"]
        interval_h: int = src["harvest_interval_hours"]
        is_tier1: bool = src["is_tier1"]
        severity = _SEV_CRITICAL if is_tier1 else _SEV_WARNING

        try:
            alert_id = fire_silence_alert_sync(
                conn,
                source_key=source_key,
                hours_silent=hours_silent,
                harvest_interval_hours=interval_h,
                is_tier1=is_tier1,
            )
            log.info(
                "silence_watchdog: alert %d fired for %s "
                "(silent %.1fh, interval %dh, severity=%s)",
                alert_id, source_key, hours_silent, interval_h, severity,
            )
            alerted.append(source_key)
        except Exception as exc:  # noqa: BLE001
            log.error(
                "silence_watchdog: failed to fire alert for %s: %s",
                source_key, exc,
            )

    return alerted
