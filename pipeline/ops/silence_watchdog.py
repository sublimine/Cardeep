"""B2.4 — Silence watchdog.

Detects sources that have gone silent: their last_ok (or last_fail) timestamp
is more than 2× their harvest_interval_hours in the past. These sources are
INVISIBLE to the passive S-HEALTH system because they never call record_run
(the connector simply never runs, or always crashes before writing health rows).

Public API
----------
find_silent_sources(conn, countries=None) -> list[dict]
    Pure read: returns every silent source from source_health, scoped to the
    active tenants (country_code = ANY; defaults to active_countries() == ['ES']).

resolve_recovered_silence_alerts(conn, countries=None) -> list[str]
    OI-10 zombie fix: closes every open ``<src>:silence`` alert whose source is no
    longer silent (it ran again). record_run only ever resolved scrape/discover
    origins, so silence alerts were zombies — this sweep, run every cycle, ties
    resolution to the exact inverse of the firing predicate.

run_silence_watchdog(conn, countries=None) -> list[str]
    Resolves recovered silence alerts, then calls find_silent_sources and fires one
    alert per silent source via the same dedup logic as health.fire_alert (SELECT +
    UPDATE or INSERT). Returns the list of source_keys that triggered an alert.

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
# Tenant scope (OI-10 de-blinding). The orchestration tables carry country_code since
# migration 0068; the producer queries are scoped to the active tenants. A deferred import
# keeps this module free of an import-time dependency on the registry package, and with
# active_countries() == ['ES'] the scope is ['ES'] so every query is byte-identical over the
# all-ES census.
# ---------------------------------------------------------------------------

def _resolve_countries(countries: list[str] | None) -> list[str]:
    """Default the producer scope to the active tenants (foundation: active_countries())."""
    if countries is not None:
        return countries
    from pipeline.ops.registry import active_countries
    return active_countries()


# ---------------------------------------------------------------------------
# Silence detection (pure read, psycopg2)
# ---------------------------------------------------------------------------

def find_silent_sources(
    conn: "psycopg2.extensions.connection",
    countries: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return every source in source_health that is SILENT, scoped to the active tenants.

    A source is silent when:
        now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
            > SILENCE_MULTIPLIER * harvest_interval_hours * interval '1 hour'

    Scoped to ``country_code = ANY(countries)`` (OI-10); ``countries`` defaults to
    active_countries() == ['ES'], so for the single ES tenant the result set is byte-identical
    to the pre-scope query (every existing row is ES).

    Returns a list of dicts with keys:
        source_key, last_ok, last_fail, harvest_interval_hours, is_tier1,
        hours_silent   (float — fractional hours since the last event)
    """
    countries = _resolve_countries(countries)
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
            country_code = ANY(%(countries)s)
            AND now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
                > %(multiplier)s * harvest_interval_hours * interval '1 hour'
        ORDER BY hours_silent DESC
    """
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql, {"multiplier": SILENCE_MULTIPLIER, "countries": countries})
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
# Silence recovery (OI-10 zombie fix — the missing resolve path)
# ---------------------------------------------------------------------------

def resolve_recovered_silence_alerts(
    conn: "psycopg2.extensions.connection",
    countries: list[str] | None = None,
) -> list[str]:
    """Close every open ``<src>:silence`` alert whose source is NO LONGER silent.

    THE ZOMBIE (COUNTRY-PACK-CONTRACT.md §6 OI-10): this watchdog FIRES
    ``<source_key>:silence`` alerts, but nothing ever resolved them. ``health.record_run`` on
    success only closes the ``:scrape``/``:discover`` origins for its phase (``build_origin``),
    so a source that recovered left its silence alert OPEN forever — ~7 prod zombies,
    observability broken in every country. This sweep is the missing resolve path: run every
    cycle, it ties resolution to the EXACT inverse of the firing predicate — an open
    ``<src>:silence`` alert is resolved the moment source_health shows ``<src>`` is within 2×
    its cadence again (i.e. it ran). The reconstructed origin (``sh.source_key || ':silence'``)
    matches at most one source (source_key is the PK) and never touches a ``:scrape``/
    ``:discover`` alert.

    Scoped to ``country_code = ANY(countries)`` (defaults to active_countries() == ['ES']) so
    one tenant's sweep never resolves another tenant's alerts. Returns the source_keys whose
    silence alert was resolved. Commits — mirrors fire_silence_alert_sync's self-contained
    write contract, so the live watchdog cycle persists the resolution without a second commit.
    """
    countries = _resolve_countries(countries)
    sql = """
        WITH recovered AS (
            UPDATE alert a
               SET resolved_at = now()
              FROM source_health sh
             WHERE a.resolved_at IS NULL
               AND a.origin = sh.source_key || ':silence'
               AND sh.country_code = ANY(%(countries)s)
               AND now() - COALESCE(sh.last_ok, sh.last_fail, '1970-01-01'::timestamptz)
                   <= %(multiplier)s * sh.harvest_interval_hours * interval '1 hour'
            RETURNING sh.source_key AS source_key
        )
        SELECT source_key FROM recovered ORDER BY source_key
    """
    with conn.cursor() as cur:
        cur.execute(sql, {"multiplier": SILENCE_MULTIPLIER, "countries": countries})
        resolved = [row[0] for row in cur.fetchall()]
    conn.commit()
    return resolved


# ---------------------------------------------------------------------------
# Watchdog runner
# ---------------------------------------------------------------------------

def run_silence_watchdog(
    conn: "psycopg2.extensions.connection",
    countries: list[str] | None = None,
) -> list[str]:
    """Resolve recovered silence alerts, then detect silent sources and fire one dedup-aware
    alert per source.

    Returns the list of source_keys for which an alert was fired (or updated). Does NOT raise —
    the recovery sweep and individual alert failures are logged and skipped so one broken step
    does not abort the rest of the watchdog cycle.
    """
    countries = _resolve_countries(countries)

    # OI-10: close the alerts of sources that came BACK first. A recovered source's :silence
    # alert is a zombie (record_run never reaches it) until this sweep resolves it.
    try:
        recovered = resolve_recovered_silence_alerts(conn, countries)
        if recovered:
            log.info(
                "silence_watchdog: resolved %d recovered silence alert(s): %s",
                len(recovered), recovered,
            )
    except Exception as exc:  # noqa: BLE001
        log.error("silence_watchdog: failed to resolve recovered silence alerts: %s", exc)

    silent = find_silent_sources(conn, countries)
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
