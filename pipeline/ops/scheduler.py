"""B2.2 — Durable single-producer scheduler.

Architecture (from CAMPAIGN_TO_100.md §B2):
  - APScheduler 3.x BlockingScheduler with SQLAlchemyJobStore persisting jobs to
    cardeep-pg. Crash-safe: the job survives a process death and resumes on restart.
  - SINGLE-PRODUCER, SERIES: one heartbeat_tick job fires every 15 min and runs due
    connectors one at a time. Never more than one subprocess in flight at once.
    This avoids the AS24 cicatriz (two governors fighting the same host) and does not
    saturate the 16 GB AMD machine.
  - Source selection: queries source_health for rows where
      now() - COALESCE(last_ok, last_fail, '1970-01-01') >= harvest_interval_hours * interval '1 hour'
    ordered by most-overdue first. Sources with open circuit breakers (consecutive_fails
    >= 3) are skipped gracefully.
  - Each due source is launched as a subprocess (python -m <module> [args]) with a
    generous timeout. The subprocess writes its own record_run — the scheduler does NOT
    write health rows.
  - B2.4 silence_watchdog job runs every hour and fires one alert per source that has
    been silent for > 2× its harvest_interval_hours. Alert dedup is built into the
    watchdog (UPDATE on existing unresolved alert, INSERT only for new silences).

Usage:
    python -m pipeline.ops.scheduler                # start the live scheduler (blocking)
    python -m pipeline.ops.scheduler --dry-run      # print DUE sources, then exit
    python -m pipeline.ops.scheduler --check-silence  # list silent sources READ-ONLY, then exit
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import psycopg2

from pipeline.ops.silence_watchdog import (
    find_silent_sources,
    run_silence_watchdog,
)
from pipeline.ops.lock_heartbeat import (
    acquire_with_stale_retry,
    heartbeat_interval_minutes,
    record_heartbeat,
)
from pipeline.config_guard import require_prod_secrets
from pipeline.ops.registry import (
    SourceEntry,
    active_countries,
    get_harvest_registry,
)

# ---------------------------------------------------------------------------
# Logging
#
# Force the scheduler's OWN stdout to UTF-8 (with a non-raising backslashreplace
# fallback) BEFORE wiring the StreamHandler. gestionador transition/error messages
# can carry non-ASCII (e.g. a U+2192 arrow in a state-machine error, accented
# Spanish notes); a Windows cp1252 ('charmap') stream would otherwise raise
# UnicodeEncodeError on emit and MASK the real error. PYTHONIOENCODING=utf-8 is
# already injected into child connectors (_run_source); this is the same guard for
# the scheduler process itself.
# ---------------------------------------------------------------------------

def _utf8_safe_stream(stream):
    """Best-effort reconfigure a text stream to UTF-8 with a non-raising fallback.

    Returns the same stream. No-op if it cannot be reconfigured (e.g. a stream
    already wrapped by a test capture, which exposes no ``reconfigure``).
    """
    try:
        stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    return stream


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [scheduler] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=_utf8_safe_stream(sys.stdout),
)
log = logging.getLogger("cardeep.scheduler")

# ---------------------------------------------------------------------------
# DB connection URL (psycopg2 sync driver for APScheduler + query helper)
# ---------------------------------------------------------------------------
DB_URL = os.environ.get(
    "CARDEEP_DB_URL",
    "postgresql+psycopg2://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)
# Raw DSN for our own psycopg2 queries (separate from APScheduler's SA engine)
_RAW_DSN = os.environ.get(
    "CARDEEP_DSN",
    "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only",
)
# asyncpg URL DSN for the WF-INQUISITION cadence job (δ). Distinct from _RAW_DSN
# above, which is the psycopg2 keyword form; asyncpg requires a postgres:// URL.
_ASYNCPG_DSN = os.environ.get(
    "CARDEEP_ASYNCPG_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)


def _redact_dsn(dsn: str) -> str:
    """Mask the password so a DSN is safe to print to stdout/logs.

    Handles both the psycopg2 keyword form (``password=secret``) and the URL form
    (``scheme://user:secret@host``). In dev the credential is the public default, but a
    prod DSN printed by ``--dry-run`` would otherwise leak a real password into logs.
    """
    redacted = re.sub(r"(password=)[^\s]+", r"\1***", dsn)
    redacted = re.sub(r"(://[^:/@\s]+:)[^@/\s]+@", r"\1***@", redacted)
    return redacted

# ---------------------------------------------------------------------------
# Heartbeat cadence
# ---------------------------------------------------------------------------
TICK_INTERVAL_MINUTES: int = 15

# WF-INQUISITION cadence (δ): how often to scan for verdicts whose freshness TTL
# has lapsed and queue their re-verification. Independent of the harvest heartbeat.
INQUISITION_CADENCE_HOURS: int = 6

# WF-INQUISITION prosecution (audit P2 D-inquisition): adjudicate PENDING claims in cadence.
# Emission of NEW claims is OPT-IN (CARDEEP_INQUISITION_EMIT=1) and bounded — at €0 mass emission
# floods un-self-resolvable escalations; prosecute-only (default) just drains whatever is PENDING.
INQUISITION_PROSECUTE_CADENCE_HOURS: int = 6
INQUISITION_PROSECUTE_BATCH: int = int(os.environ.get("CARDEEP_INQUISITION_PROSECUTE_BATCH", "200"))
INQUISITION_EMIT_BATCH: int = int(os.environ.get("CARDEEP_INQUISITION_EMIT_BATCH", "200"))

# Gestionador price_trap detector (audit P2 price_trap v2): daily cohort price-anomaly scan.
# QUARANTINE-only + reversible. Ships behind a one-run dry-run review before being relied on in prod
# (docs/architecture/feature-designs/price_trap.md §Risks); inert until the scheduler is deployed.
GESTIONADOR_DETECT_CADENCE_HOURS: int = int(os.environ.get("CARDEEP_GESTIONADOR_CADENCE_HOURS", "24"))

# canonical_key forward-coverage (audit P2 B-canonical-key, forward-write portion): recompute + gate-
# write the audit pre-image for any entity still NULL (new entities INSERT it NULL; cdp_code, the
# hot-path dedup key, is always set). Self-verifying (writes only on re-hash match) → €0, zero-risk.
CANONICAL_KEY_BACKFILL_CADENCE_HOURS: int = int(os.environ.get("CARDEEP_CANONKEY_CADENCE_HOURS", "24"))

# F4 adaptive cadence (00-marketplace-engine.md): recompute every registered source's change-
# rate estimate daily from its own harvest_run/vehicle_event history. €0 (DB reads + targeted
# UPDATEs of the estimate columns only, migration 0076) — never flips cadence_mode.
CADENCE_ESTIMATE_CADENCE_HOURS: int = int(os.environ.get("CARDEEP_CADENCE_ESTIMATE_CADENCE_HOURS", "24"))

# F6 uptime ledger (00-marketplace-engine.md): retention window for engine_heartbeat_log
# (migration 0085) and how often the purge job runs. €0 (a single range DELETE, doctrine
# INSERT-only + purge by range — see pipeline.ops.lock_heartbeat.purge_heartbeat_log).
HEARTBEAT_LOG_RETENTION_DAYS: int = int(os.environ.get("CARDEEP_HEARTBEAT_LOG_RETENTION_DAYS", "90"))
HEARTBEAT_LOG_PURGE_CADENCE_HOURS: int = int(os.environ.get("CARDEEP_HEARTBEAT_LOG_PURGE_CADENCE_HOURS", "24"))

# Circuit breaker: skip sources with consecutive_fails >= this threshold
BREAKER_TRIP_AT: int = 3

# Subprocess timeout: generous to allow full crawls (24h sources can take ~2h)
# This is a hard wall to prevent a stuck process from blocking the scheduler forever.
SUBPROCESS_TIMEOUT_SEC: int = int(os.environ.get("CARDEEP_SUBPROCESS_TIMEOUT", 14400))  # 4h default

# ---------------------------------------------------------------------------
# Source -> module registry (motor<->pack split, COUNTRY-PACK-CONTRACT.md §4)
#
# The per-country source_key -> SourceEntry entries no longer live here: the split
# extracted them to the country packs under ``pipeline/ops/registry/<cc>.py`` (the ES set
# is ``registry/es.py``). The scheduler (motor) stays country-invariant and assembles its
# REGISTRY from ``get_harvest_registry(cc)`` over ``active_countries()``. ``SourceEntry`` is
# imported from that package (see top of file) and re-exported below for compatibility.
# ---------------------------------------------------------------------------


def _build_registry() -> dict[str, SourceEntry]:
    """Return the authoritative source_key -> SourceEntry mapping for the active tenants.

    Assembled from the country packs: for each code in ``active_countries()`` the entries
    from ``get_harvest_registry(code)`` are concatenated in order and keyed by source_key.
    With ``active_countries() == ['ES']`` this is byte-identical to the pre-split inline ES
    registry (same entries, same order) so the scheduler harvests exactly the same sources.
    """
    entries: list[SourceEntry] = []
    for country_code in active_countries():
        entries.extend(get_harvest_registry(country_code))
    return {e.source_key: e for e in entries}


# Module-level registry (built once at import time)
REGISTRY: dict[str, SourceEntry] = _build_registry()

# source_keys present in source_health that have NO mapping in REGISTRY.
# Declared explicitly (never invented) — these are excluded from scheduling.
# (audit P2 C-as24): as24_wholesale is now seeded in source_health (migration 0039) and mapped in
# REGISTRY above — it is the AS24 record_run writer, scheduled at the 0039 168h cadence. The literal
# 'as24' per-dealer driver (scale_as24.py) stays operator-run and is intentionally NOT scheduled.
UNMAPPED_KEYS: frozenset[str] = frozenset()  # populated dynamically in _gap_report()


# ---------------------------------------------------------------------------
# DB query helpers (synchronous psycopg2 — scheduler context is sync)
# ---------------------------------------------------------------------------

def _breaker_decision(
    breaker_state: str | None,
    cooldown_until: datetime | None,
    now: datetime,
) -> str:
    """Pure Hystrix-style half-open decision (F3, closes the gap vs. Hystrix 2011 documented
    in plans/cardeep-omni/00-marketplace-engine.md §3) for one source_health/source_breaker
    pair. No DB access — trivially unit-testable, and reused identically by _due_sources().

    Returns:
      "allow" — breaker CLOSED (or no source_breaker row at all — never tripped): schedule
                normally, same as before F3.
      "probe" — breaker OPEN and its cooldown_until has elapsed: eligible for a probe this
                tick. This function only decides ELIGIBILITY (read-only) — the actual
                atomic claim (source_breaker 'open' -> 'half_open') happens inside
                pipeline.ops.health.is_open(), called by the connector itself once
                launched. Deliberately NOT claimed here or in _prepare_launch(): see
                _prepare_launch()'s docstring for the double-claim bug that design would
                cause (caught live during F3's rollout).
      "skip"  — breaker OPEN and still cooling, OR breaker HALF_OPEN (a probe is already
                outstanding elsewhere, Hystrix's "exactly one request in flight"): do not
                schedule this tick.

    Before F3, exclusion was decided from source_health.consecutive_fails >= BREAKER_TRIP_AT
    alone — permanently, with no time dimension, so a tripped breaker could never again be
    scheduled even long after its cooldown had elapsed (the mechanism health.py already
    implements via source_breaker + is_open() was simply never consulted by the scheduler).
    """
    if breaker_state is None or breaker_state == "closed":
        return "allow"
    if breaker_state == "half_open":
        return "skip"
    # breaker_state == "open"
    if cooldown_until is None or now < cooldown_until:
        return "skip"
    return "probe"


def _due_sources(
    conn: "psycopg2.connection",
    countries: list[str] | None = None,
) -> list[tuple[str, int, datetime | None, datetime | None]]:
    """Return (source_key, effective_interval_hours, last_ok, last_fail) for sources that are
    DUE for harvesting, ordered by most-overdue first.

    DUE condition:
      now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
        >= effective_interval_hours * interval '1 hour'

    Scoped to ``country_code = ANY(countries)`` (OI-10); ``countries`` defaults to
    active_countries() == ['ES'], so for the single ES tenant the due set is byte-identical to
    the pre-scope query (every existing source_health row is ES).

    Circuit breaker (F3): LEFT JOINs source_breaker and applies _breaker_decision() per row.
    A CLOSED breaker (or no source_breaker row) is included as before. An OPEN breaker whose
    cooldown_until has elapsed is included too — as a half-open PROBE candidate, the fix for
    the gap where a tripped source stayed excluded forever. An OPEN-and-cooling or HALF_OPEN
    (probe already outstanding) breaker is excluded. The external 4-tuple contract is
    unchanged — the breaker columns are consumed internally, never leaked to callers. The
    actual half-open probe claim happens inside pipeline.ops.health.is_open(), called by
    the connector itself once launched — never here or in _prepare_launch() (see that
    function's docstring for why the scheduler must not also claim the slot).

    Adaptive cadence (F4): effective_interval_hours is harvest_interval_hours UNLESS the
    source has been explicitly flipped to cadence_mode='adaptive' AND has a non-null
    computed_interval_hours (pipeline/ops/cadence_estimator.py), in which case the estimated
    interval is used instead — for BOTH the DUE comparison and the ORDER BY. Every source not
    deliberately opted in (cadence_mode defaults to 'static' for all rows, migration 0076)
    behaves exactly as before F4.
    """
    if countries is None:
        countries = active_countries()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                sh.source_key,
                -- F4: use the adaptive computed_interval_hours when the source has been
                -- explicitly flipped to cadence_mode='adaptive' AND has a real estimate;
                -- every other source (the default 'static' for every pre-F4 row) falls
                -- through to harvest_interval_hours unchanged — byte-identical DUE timing
                -- to before F4 for any source not deliberately opted in.
                CASE
                    WHEN sh.cadence_mode = 'adaptive' AND sh.computed_interval_hours IS NOT NULL
                    THEN sh.computed_interval_hours
                    ELSE sh.harvest_interval_hours
                END AS effective_interval_hours,
                sh.last_ok,
                sh.last_fail,
                sh.consecutive_fails,
                sb.state,
                sb.cooldown_until
            FROM source_health sh
            LEFT JOIN source_breaker sb ON sb.source_key = sh.source_key
            WHERE
                sh.country_code = ANY(%(countries)s)
                AND now() - COALESCE(sh.last_ok, sh.last_fail, '1970-01-01'::timestamptz)
                    >= (CASE
                            WHEN sh.cadence_mode = 'adaptive' AND sh.computed_interval_hours IS NOT NULL
                            THEN sh.computed_interval_hours
                            ELSE sh.harvest_interval_hours
                        END) * interval '1 hour'
            ORDER BY
                now() - COALESCE(sh.last_ok, sh.last_fail, '1970-01-01'::timestamptz) DESC
            """,
            {"countries": countries},
        )
        rows = cur.fetchall()

    now = datetime.now(timezone.utc)
    result = []
    for source_key, interval_h, last_ok, last_fail, consecutive_fails, breaker_state, cooldown_until in rows:
        decision = _breaker_decision(breaker_state, cooldown_until, now)
        if decision == "skip":
            log.info(
                "skip %s — breaker %s (consecutive_fails=%d, cooldown_until=%s)",
                source_key, breaker_state, consecutive_fails, cooldown_until,
            )
            continue
        if decision == "probe":
            log.info(
                "PROBE-ELIGIBLE %s — half-open window reached (cooldown elapsed at %s); "
                "will attempt exactly one probe this tick",
                source_key, cooldown_until,
            )
        result.append((source_key, interval_h, last_ok, last_fail))
    return result


def _prepare_launch(source_key: str) -> bool:
    """Re-check a source's breaker immediately before launching its subprocess (F3).

    READ-ONLY — never mutates source_breaker. _due_sources() already decided ELIGIBILITY
    (including half-open probe eligibility) from a snapshot read; this is a freshness
    re-check for sources deep in a long due-list, where earlier sources in the SAME tick
    may have each taken up to SUBPROCESS_TIMEOUT_SEC to finish, so a source's breaker could
    have changed since _due_sources() read it hours earlier in the same tick.

    Deliberately does NOT perform its own CAS claim of the half-open slot (a first version
    did, and a live rollout caught the real bug that causes: pipeline.ops.health.is_open()
    — called BY THE CONNECTOR ITSELF as its own internal pre-flight check — is the ONE
    place the half-open claim happens (see is_open()'s docstring). If the scheduler ALSO
    claimed the slot here first, the connector's own subsequent is_open() call would see
    the slot already 'half_open' and treat ITS OWN authorized probe as a second, blocked,
    concurrent caller — aborting the probe before it ever attempted real work, and leaving
    the breaker stuck in 'half_open' forever (nothing left to call record_run() and resolve
    it). Observed live 2026-07-17/18 for all 7 probe-eligible sources in the first tick
    after deploy; see 00-marketplace-engine.md F3 for the full incident. Single-producer
    serialization (heartbeat_tick never overlaps itself) already provides the "exactly one
    subprocess at a time" guarantee this function's read-only re-check needs; the ACTUAL
    Hystrix single-probe-in-flight enforcement lives entirely in is_open()'s CAS, exercised
    by whichever connectors call it (tests/test_breaker_jitter_and_half_open.py).

    Uses its own short-lived psycopg2 connection (same idiom as _harvest_run_max_id).
    Fails CLOSED (returns False, blocking the launch) on any connection error: a health
    check we cannot trust must never be treated as a green light to hammer a fragile source.
    """
    try:
        conn = psycopg2.connect(_RAW_DSN)
    except psycopg2.Error as exc:
        log.error(
            "breaker re-check failed to connect for %s: %s — skipping this tick",
            source_key, exc,
        )
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT state, cooldown_until FROM source_breaker WHERE source_key=%s",
                (source_key,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return True  # never tripped
    breaker_state, cooldown_until = row
    decision = _breaker_decision(breaker_state, cooldown_until, datetime.now(timezone.utc))
    if decision == "skip":
        log.info(
            "skip %s — breaker state changed since _due_sources() read (now %s); "
            "no longer eligible this tick",
            source_key, breaker_state,
        )
        return False
    return True


def _all_source_keys(conn: "psycopg2.connection") -> list[str]:
    """Return every source_key registered in source_health."""
    with conn.cursor() as cur:
        cur.execute("SELECT source_key FROM source_health ORDER BY source_key")
        return [r[0] for r in cur.fetchall()]


def _gap_report(all_keys: list[str]) -> tuple[list[str], list[str]]:
    """Return (mapped, unmapped) source_key lists against REGISTRY."""
    mapped = [k for k in all_keys if k in REGISTRY]
    unmapped = [k for k in all_keys if k not in REGISTRY]
    return mapped, unmapped


# ---------------------------------------------------------------------------
# Subprocess launcher
# ---------------------------------------------------------------------------

def _build_cmd(entry: SourceEntry) -> list[str]:
    """Build the subprocess argv for a given SourceEntry."""
    return [sys.executable, "-m", entry.module, *entry.extra_args]


def _run_source(source_key: str) -> int:
    """Launch the connector subprocess and wait for it.

    Returns the exit code. stdout/stderr are inherited (the connector prints its own
    progress; the scheduler's log wraps it with timestamps). The connector is
    responsible for writing its own record_run row — the scheduler does NOT.

    PYTHONIOENCODING=utf-8 is injected into the child environment so that ALL
    connectors launched by this scheduler use UTF-8 I/O regardless of the
    platform default (Windows cp1252 otherwise).  This is the single-point fix
    for the B3.3 encoding bug (alert id 6: coches_com Sigma crash).
    """
    entry = REGISTRY[source_key]
    cmd = _build_cmd(entry)
    log.info("LAUNCH %s -> %s", source_key, " ".join(cmd))
    child_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            cmd,
            timeout=SUBPROCESS_TIMEOUT_SEC,
            check=False,   # do not raise on non-zero; we log the exit code
            env=child_env,
        )
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        log.error("TIMEOUT %s after %ds", source_key, SUBPROCESS_TIMEOUT_SEC)
        exit_code = -1
    except Exception as exc:  # noqa: BLE001
        log.error("ERROR launching %s: %s", source_key, exc)
        exit_code = -2

    if exit_code == 0:
        log.info("OK %s (exit=0)", source_key)
    else:
        log.warning("FAIL %s (exit=%d)", source_key, exit_code)
    return exit_code


def _harvest_run_max_id(source_key: str) -> int | None:
    """Current high-water harvest_run id for a source (or None if the query fails).

    Captured BEFORE launching a connector so a crash-before-record_run can be told apart from a
    connector that wrote its own outcome — the idempotency key for _record_crash_if_unrecorded.
    """
    try:
        conn = psycopg2.connect(_RAW_DSN)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT coalesce(max(id), 0) FROM harvest_run WHERE source_key = %s",
                (source_key,),
            )
            return int(cur.fetchone()[0])
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        log.error("scheduler: harvest_run high-water query failed for %s: %s", source_key, exc)
        return None  # unknown → record unconditionally below (better an extra alert than silence)


def _record_crash_if_unrecorded(source_key: str, exit_code: int, pre_max_id: int | None) -> None:
    """Safety net for the crash-before-record_run gap (green-review H7/M5).

    Connectors own their own record_run on every normal path (the scheduler does NOT write it).
    But a connector SIGKILLed on timeout, failing to launch, or dying before it reaches its
    record_run leaves source_health untouched — the circuit breaker never trips and the silence
    watchdog only notices after 2x the interval. Here the scheduler records the failure itself,
    but ONLY when no new harvest_run row appeared this cycle (vs the pre-launch high-water), so a
    connector that DID record its own outcome is never double-counted.
    """
    import asyncio

    import asyncpg

    from pipeline.ops.health import record_run

    async def _run() -> bool:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            if pre_max_id is not None:
                newest = await conn.fetchval(
                    "SELECT coalesce(max(id), 0) FROM harvest_run WHERE source_key = $1",
                    source_key,
                )
                if int(newest) > pre_max_id:
                    return False  # connector wrote its own record_run this cycle — do not double-count
            await record_run(
                conn,
                source_key,
                ok=False,
                error=f"scheduler: connector exited {exit_code} without recording a harvest_run",
            )
            return True
        finally:
            await conn.close()

    try:
        if asyncio.run(_run()):
            log.warning(
                "scheduler: connector %s exited %d without a record_run — recorded the failure "
                "(health/breaker engaged)", source_key, exit_code)
    except Exception as exc:  # noqa: BLE001
        log.error("scheduler: could not record crash for %s: %s", source_key, exc)


# ---------------------------------------------------------------------------
# Heartbeat tick (the single job APScheduler fires every 15 min)
# ---------------------------------------------------------------------------

def heartbeat_tick() -> None:
    """Single-producer tick: find due sources and run them in series.

    This function is synchronous and runs inside APScheduler's executor. Because
    the scheduler is configured with max_instances=1 and this job is the only
    producer, there is never more than one connector running at a time.
    """
    log.info("=== heartbeat_tick START ===")
    conn: psycopg2.extensions.connection | None = None
    try:
        conn = psycopg2.connect(_RAW_DSN)
        due = _due_sources(conn)
    except Exception as exc:  # noqa: BLE001
        log.error("DB error fetching due sources: %s", exc)
        return
    finally:
        if conn is not None:
            conn.close()

    if not due:
        log.info("heartbeat_tick: no sources due — sleeping until next tick")
        return

    log.info("heartbeat_tick: %d source(s) due", len(due))
    for source_key, interval_h, last_ok, last_fail in due:
        if source_key not in REGISTRY:
            log.warning(
                "SKIP %s — not in module registry (interval=%dh, last_ok=%s)",
                source_key, interval_h, last_ok,
            )
            continue
        if not _prepare_launch(source_key):
            continue  # breaker state changed since _due_sources() read it — logged in _prepare_launch
        pre_max_id = _harvest_run_max_id(source_key)   # high-water before launch (H7 safety net)
        exit_code = _run_source(source_key)
        if exit_code != 0:
            _record_crash_if_unrecorded(source_key, exit_code, pre_max_id)

    log.info("=== heartbeat_tick END ===")


# ---------------------------------------------------------------------------
# B2.4 — Silence watchdog job (runs every hour)
# ---------------------------------------------------------------------------

def silence_watchdog_job() -> None:
    """Hourly job: detect sources that have been silent for > 2× their interval.

    Fires one dedup-aware alert per silent source (UPDATE existing open alert or
    INSERT new). Never raises: a DB error is logged and the job exits cleanly so
    the scheduler continues.
    """
    log.info("=== silence_watchdog START ===")
    conn: psycopg2.extensions.connection | None = None
    try:
        conn = psycopg2.connect(_RAW_DSN)
        alerted = run_silence_watchdog(conn)
        log.info(
            "silence_watchdog: %d alert(s) fired/updated: %s",
            len(alerted),
            alerted or "(none)",
        )
    except Exception as exc:  # noqa: BLE001
        log.error("silence_watchdog: unexpected error: %s", exc)
    finally:
        if conn is not None:
            conn.close()
    log.info("=== silence_watchdog END ===")


def inquisition_cadence_job() -> None:
    """Periodic job (δ): queue re-verification for verdicts whose TTL has lapsed.

    Runs pipeline.ops.inquisition_schedule.schedule_reverification — finds expired
    verification_verdict rows (expires_at < now() AND not superseded) and opens
    stale_verdict gestion_items via the gestionador. €0 (DB reads + gestion_item
    upserts; it QUEUES re-verification, never runs harvest). Never raises: a DB
    error is logged and the job exits so the scheduler continues.
    """
    import asyncio
    import asyncpg

    from pipeline.ops.inquisition_schedule import schedule_reverification

    log.info("=== inquisition_cadence START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            return await schedule_reverification(conn)
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("inquisition_cadence: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("inquisition_cadence: unexpected error: %s", exc)
    log.info("=== inquisition_cadence END ===")


def inquisition_prosecute_job() -> None:
    """Periodic job (audit P2 D-inquisition): adjudicate PENDING inquisition claims in cadence.

    ALWAYS runs prosecute_pending (drains PENDING claims; at €0 → honest REFUTED:NO_INDEPENDENT_PATH
    → ESCALATE_OWNER). Emission of NEW claims from VAM verdicts is OPT-IN (CARDEEP_INQUISITION_EMIT=1)
    and bounded — at €0 mass emission would flood un-self-resolvable escalations. Writes ONLY
    inquisition_*/gestion_*/alert — never served vehicle/entity/verification_verdict. Never raises:
    a DB error is logged and the job exits so the scheduler continues.
    """
    import asyncio
    import os

    import asyncpg

    from pipeline.inquisition.prosecutor import emit_claims_from_verdicts, prosecute_pending

    log.info("=== inquisition_prosecute START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            summary: dict = {}
            if os.environ.get("CARDEEP_INQUISITION_EMIT") == "1":
                summary["emit"] = await emit_claims_from_verdicts(conn, limit=INQUISITION_EMIT_BATCH)
            summary["prosecute"] = await prosecute_pending(conn, limit=INQUISITION_PROSECUTE_BATCH)
            return summary
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("inquisition_prosecute: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("inquisition_prosecute: unexpected error: %s", exc)
    log.info("=== inquisition_prosecute END ===")


def gestionador_detect_job() -> None:
    """Daily job (audit P2 price_trap v2): run the cohort price-anomaly detector + route flags.

    QUARANTINE-only: opens reversible gestion_items that hide cohort-implausible-priced cars from
    servable_vehicle — NEVER NULLs or DELETEs vehicle.price (close the item to re-show). DB reads +
    gestion_item upserts only (€0); run_price_trap bumps work_mem so the cohort percentile scan does
    not spill to disk. Never raises: a DB error is logged and the job exits so the scheduler continues.

    Ships behind a one-run dry-run review (docs/architecture/feature-designs/price_trap.md §Risks):
    review the flagged set via `python -m pipeline.gestionador.run` before relying on it in prod.
    """
    import asyncio

    import asyncpg

    from pipeline.gestionador.run import run_all

    log.info("=== gestionador_detect (all detectors) START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            return await run_all(conn)
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("gestionador_detect: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("gestionador_detect: unexpected error: %s", exc)
    log.info("=== gestionador_detect (all detectors) END ===")


def canonical_key_backfill_job() -> None:
    """Daily job (audit P2 B-canonical-key forward-coverage): fill entity.canonical_key for new rows.

    canonical_key is the AUDIT pre-image of cdp_code; new entities INSERT it NULL while cdp_code (the
    hot-path UNIQUE dedup key) is always set, so lazy fill is correct. Self-verifying: writes a key
    ONLY when its recompute re-hashes to the row's stored cdp_code (a wrong key cannot be written).
    €0 (DB reads + targeted UPDATEs of NULL→value only — never rewrites a set key, MVCC-clean). Never
    raises: a DB error is logged and the job exits so the scheduler continues.
    """
    import asyncio

    import asyncpg

    from pipeline.identity.canonical_key_backfill import backfill_canonical_keys

    log.info("=== canonical_key_backfill START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            return await backfill_canonical_keys(conn, apply=True)
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("canonical_key_backfill: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("canonical_key_backfill: unexpected error: %s", exc)
    log.info("=== canonical_key_backfill END ===")


def cadence_estimate_job() -> None:
    """Daily job (F4, 00-marketplace-engine.md): recompute observed_change_rate /
    computed_interval_hours for EVERY registered source from its own harvest_run +
    vehicle_event history (pipeline/ops/cadence_estimator.py).

    Writes ONLY the estimate columns (migration 0076) via apply_cadence_estimate() — it
    NEVER flips cadence_mode. Flipping a source to 'adaptive' is a deliberate, gradual,
    operator-driven rollout step (scripts/enable_adaptive_cadence.py), never an automatic
    side effect of estimation; this job keeps the estimate FRESH for every source
    (including ones still in 'static' mode) so an operator reviewing a rollout candidate
    always sees a current number, not a stale one from whenever it was last computed by
    hand. A source with insufficient sample (estimate_change_rate returns None) is simply
    skipped this cycle — its columns stay whatever they were (or NULL). Never raises: a
    per-source or connection error is logged and the job continues to the next source /
    exits cleanly so the scheduler is never brought down by this job.
    """
    import asyncio

    import asyncpg

    from pipeline.ops.cadence_estimator import apply_cadence_estimate, estimate_change_rate

    log.info("=== cadence_estimate START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            rows = await conn.fetch("SELECT source_key FROM source_health ORDER BY source_key")
            computed = 0
            skipped = 0
            for row in rows:
                source_key = row["source_key"]
                try:
                    estimate = await estimate_change_rate(conn, source_key)
                except Exception as exc:  # noqa: BLE001
                    log.warning("cadence_estimate: %s failed: %s", source_key, exc)
                    skipped += 1
                    continue
                if estimate is None:
                    skipped += 1
                    continue
                await apply_cadence_estimate(conn, estimate)
                computed += 1
            return {"computed": computed, "skipped_insufficient_or_error": skipped}
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("cadence_estimate: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("cadence_estimate: unexpected error: %s", exc)
    log.info("=== cadence_estimate END ===")


def heartbeat_log_purge_job() -> None:
    """Daily job (F6, 00-marketplace-engine.md): bulk-purge engine_heartbeat_log rows older
    than HEARTBEAT_LOG_RETENTION_DAYS (default 90 days).

    Pure range DELETE (pipeline.ops.lock_heartbeat.purge_heartbeat_log) — never an UPDATE, never
    a per-row delete: the same anti-dead-tuple discipline the stack already applies to
    vehicle_event/harvest_run. Best-effort: a missing table (DB without migration 0085) purges 0
    rows silently; any other DB error is logged and the job exits so the scheduler continues —
    a failed purge must never take down the heartbeat itself.
    """
    from pipeline.ops.lock_heartbeat import purge_heartbeat_log

    log.info("=== heartbeat_log_purge START ===")
    conn: psycopg2.extensions.connection | None = None
    try:
        conn = psycopg2.connect(_RAW_DSN)
        conn.autocommit = True
        deleted = purge_heartbeat_log(conn, retention_days=HEARTBEAT_LOG_RETENTION_DAYS)
        log.info(
            "heartbeat_log_purge: deleted %d row(s) older than %d days",
            deleted, HEARTBEAT_LOG_RETENTION_DAYS,
        )
    except Exception as exc:  # noqa: BLE001
        log.error("heartbeat_log_purge: unexpected error: %s", exc)
    finally:
        if conn is not None:
            conn.close()
    log.info("=== heartbeat_log_purge END ===")


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

def _dry_run() -> None:
    """Print which sources are DUE right now and what command would be launched.

    Does NOT execute any subprocess. Safe to run at any time.
    """
    conn: psycopg2.extensions.connection | None = None
    try:
        conn = psycopg2.connect(_RAW_DSN)
        all_keys = _all_source_keys(conn)
        due = _due_sources(conn)
    finally:
        if conn is not None:
            conn.close()

    mapped_keys, unmapped_keys = _gap_report(all_keys)

    print()
    print("=" * 72)
    print("CARDEEP SCHEDULER - DRY RUN")
    print(f"  DB:        {_redact_dsn(_RAW_DSN)}")
    print(f"  Tick:      every {TICK_INTERVAL_MINUTES} min")
    print(f"  Timeout:   {SUBPROCESS_TIMEOUT_SEC}s per subprocess")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)

    print(f"\nSOURCE REGISTRY COVERAGE")
    print(f"  Total source_health rows : {len(all_keys)}")
    print(f"  Mapped to a module       : {len(mapped_keys)}")
    print(f"  UNMAPPED (gap)           : {len(unmapped_keys)}")
    if unmapped_keys:
        print("\n  [!] UNMAPPED SOURCE KEYS (excluded from scheduling):")
        for k in sorted(unmapped_keys):
            print(f"    - {k}")

    print(f"\nDUE SOURCES ({len(due)} total, ordered most-overdue first):")
    print("-" * 72)

    due_mapped = 0
    due_unmapped = 0
    for source_key, interval_h, last_ok, last_fail in due:
        overdue_since = last_ok or last_fail or "never"
        in_registry = source_key in REGISTRY
        if in_registry:
            entry = REGISTRY[source_key]
            cmd = " ".join(_build_cmd(entry))
            status = "WOULD RUN"
            due_mapped += 1
        else:
            cmd = "(no module — SKIPPED)"
            status = "UNMAPPED"
            due_unmapped += 1

        print(f"  [{status:10s}] {source_key}")
        print(f"               interval={interval_h}h | last_ok={last_ok} | last_fail={last_fail}")
        print(f"               cmd: {cmd}")
        print()

    print("-" * 72)
    print(f"SUMMARY: {due_mapped} would run, {due_unmapped} skipped (unmapped)")
    if unmapped_keys:
        print(f"GAP REPORT: {len(unmapped_keys)} source_key(s) in source_health have no module:")
        for k in sorted(unmapped_keys):
            print(f"  {k}")
    print("=" * 72)
    print()


# ---------------------------------------------------------------------------
# Check-silence mode (B2.4 read-only CLI)
# ---------------------------------------------------------------------------

def _check_silence() -> None:
    """Print sources that are SILENT right now.

    READ-ONLY: does NOT fire alerts, does NOT modify any DB row.
    A source is silent when its last event (last_ok or last_fail) is older than
    2 × harvest_interval_hours.
    """
    conn: psycopg2.extensions.connection | None = None
    try:
        conn = psycopg2.connect(_RAW_DSN)
        silent = find_silent_sources(conn)
    finally:
        if conn is not None:
            conn.close()

    print()
    print("=" * 72)
    print("CARDEEP SCHEDULER - SILENCE CHECK (read-only, no alerts fired)")
    print(f"  DB:        {_redact_dsn(_RAW_DSN)}")
    print(f"  Threshold: > 2x harvest_interval_hours without last_ok or last_fail")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)

    if not silent:
        print("\n  (no silent sources detected)")
    else:
        print(f"\nSILENT SOURCES ({len(silent)} total, most-overdue first):")
        print("-" * 72)
        for src in silent:
            source_key = src["source_key"]
            hours_silent = src["hours_silent"]
            interval_h = src["harvest_interval_hours"]
            is_tier1 = src["is_tier1"]
            last_ok = src["last_ok"]
            last_fail = src["last_fail"]
            severity = "CRITICAL" if is_tier1 else "WARNING"
            threshold_h = 2 * interval_h
            print(f"  [{severity:8s}] {source_key}")
            print(f"               silent={hours_silent:.1f}h | threshold={threshold_h}h | interval={interval_h}h")
            print(f"               last_ok={last_ok} | last_fail={last_fail}")
            print(f"               is_tier1={is_tier1}")
            print()

    print("-" * 72)
    print(f"SUMMARY: {len(silent)} silent source(s) detected")
    print("  (run without --check-silence to start the scheduler and fire real alerts)")
    print("=" * 72)
    print()


# ---------------------------------------------------------------------------
# Live scheduler
# ---------------------------------------------------------------------------

# Cadence for the product_stats cache refresh that backs a fast /stats (env-overridable).
PRODUCT_STATS_REFRESH_MIN: int = int(os.environ.get("CARDEEP_STATS_REFRESH_MIN", "30"))


def _refresh_product_stats_job() -> None:
    """Picklable cadence job: refresh the product_stats cache (fast /stats). Best-effort — a failed
    refresh must never kill the scheduler; the API falls back to a live compute until the next success.
    Runs off the request path so the heavy COUNT(DISTINCT)/JOIN never blocks a /stats caller again.
    """
    import asyncio

    try:
        from scripts.refresh_product_stats import refresh

        counts = asyncio.run(refresh(_ASYNCPG_DSN))
        log.info("product_stats refreshed: %s", counts)
    except Exception as exc:  # best-effort — never propagate into the scheduler
        log.warning("product_stats refresh failed: %s", exc)


def _lease_heartbeat_job(lock_key: int, holder: str) -> None:
    """Picklable heartbeat job: bump the observable scheduler_lease for ``lock_key``.

    Persisted in the SQLAlchemy jobstore, so it MUST be a module-level function with
    picklable args (a closure over the held _lock_conn cannot be pickled). Runs on its own
    short-lived autocommit connection; the lease row is plain data, independent of the
    advisory-lock session, so a separate connection writes it correctly. Fully best-effort:
    record_heartbeat never raises and a connect failure is swallowed — a missed beat must
    never kill the single producer. Inert (one warning) on a DB without migration 0054.
    """
    try:
        conn = psycopg2.connect(_RAW_DSN)
        conn.autocommit = True
    except psycopg2.Error as exc:
        log.warning("lease heartbeat could not connect for lock_key=%s: %s", lock_key, exc)
        return
    try:
        record_heartbeat(conn, lock_key, holder=holder)
    finally:
        try:
            conn.close()
        except psycopg2.Error:
            pass


def _start_scheduler() -> None:
    """Start the durable BlockingScheduler. Blocks until SIGINT/SIGTERM."""
    # FASE-2 ops-hardening: in prod, fail fast if any DSN still carries the dev credential (i.e. no
    # real DSN was supplied). No-op when CARDEEP_ENV is unset/dev — dev/test stays byte-identical.
    require_prod_secrets(
        (_RAW_DSN, "CARDEEP_DSN"),
        (DB_URL, "CARDEEP_DB_URL"),
        (_ASYNCPG_DSN, "CARDEEP_ASYNCPG_DSN"),
    )
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.schedulers.blocking import BlockingScheduler

    # Single-producer HOST lock (AS24 scar: never two governors on one host — that 4x-hammer lost
    # 138 dealers). max_instances=1 only prevents overlapping ticks WITHIN one process; this
    # session-level pg advisory lock prevents a SECOND scheduler process from doubling the host's
    # aggregate request rate. It fails fast if another scheduler holds it and auto-releases when
    # this connection closes at process exit. _lock_conn is intentionally kept open for the
    # process lifetime — do not close it.
    _SCHEDULER_SINGLETON_LOCK = 0x43415244  # ASCII 'CARD' = 1128354372 — fixed host-singleton key
    _lock_conn = psycopg2.connect(_RAW_DSN)
    _lock_conn.autocommit = True
    # Shared single-producer acquire (same path as discovery): take the lock, retry once ONLY if the
    # prior holder's lease is stale. pg_try_advisory_lock is the atomic mutex so a live holder is
    # never displaced (no AS24 double-producer). Best-effort stale check; inert without migration 0054.
    if not acquire_with_stale_retry(_lock_conn, _SCHEDULER_SINGLETON_LOCK):
        _lock_conn.close()
        raise SystemExit(
            "another cardeep scheduler already holds the singleton advisory lock "
            f"({_SCHEDULER_SINGLETON_LOCK}); refusing to start a second producer on this host"
        )
    log.info("Acquired singleton scheduler advisory lock %s", _SCHEDULER_SINGLETON_LOCK)
    # FASE-2 ops-hardening: claim/refresh the observable lease for this holder so a would-be
    # successor can tell a healthy holder from a crashed one. Best-effort; inert without 0054.
    record_heartbeat(_lock_conn, _SCHEDULER_SINGLETON_LOCK, holder="harvest")

    jobstores = {
        "default": SQLAlchemyJobStore(url=DB_URL),
    }
    scheduler = BlockingScheduler(jobstores=jobstores, timezone="UTC")

    # Replace any stale job definition with the current one on each start.
    # This ensures cadence changes (TICK_INTERVAL_MINUTES) take effect on restart
    # without manual DB cleanup.
    scheduler.add_job(
        heartbeat_tick,
        trigger="interval",
        minutes=TICK_INTERVAL_MINUTES,
        id="heartbeat_tick",
        name="cardeep heartbeat tick",
        replace_existing=True,
        max_instances=1,   # enforce single-producer: never two ticks overlapping
        coalesce=True,     # if the scheduler was down for multiple ticks, fire once
        misfire_grace_time=300,  # allow 5 min of slippage before skipping a misfired tick
    )

    # B2.4 — silence watchdog: independent hourly job, separate from the heartbeat.
    # Detects sources that stop running (no record_run → S-HEALTH blind spot).
    # max_instances=1 and coalesce=True prevent pile-up if a check takes too long.
    scheduler.add_job(
        silence_watchdog_job,
        trigger="interval",
        hours=1,
        id="silence_watchdog",
        name="cardeep silence watchdog",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,  # 10 min slippage allowed before skipping
    )

    # δ — WF-INQUISITION cadence: re-verify verdicts whose freshness TTL has lapsed.
    # €0: queues re-verification as stale_verdict gestion_items (the re-prosecution
    # itself is harvest-gated). Independent of the harvest heartbeat.
    scheduler.add_job(
        inquisition_cadence_job,
        trigger="interval",
        hours=INQUISITION_CADENCE_HOURS,
        id="inquisition_cadence",
        name="cardeep inquisition cadence (verdict TTL re-verification)",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    # audit P2 D-inquisition: adjudicate PENDING claims in cadence (gives the prosecutor a live caller).
    # Prosecute-only by default; NEW-claim emission is opt-in (CARDEEP_INQUISITION_EMIT=1). DB-only,
    # single-producer + host advisory lock prevent a 2nd run. +30min offset from the cadence job above.
    scheduler.add_job(
        inquisition_prosecute_job,
        trigger="interval",
        hours=INQUISITION_PROSECUTE_CADENCE_HOURS,
        # Audit pass-4 D6: enforce the +30min stagger the comment above promised but never set.
        # cadence (no start_date) first-fires at now+CADENCE_HOURS; prosecute first-fires 30min later
        # and, both being 6h intervals, trails it every cycle (cadence queues -> prosecute drains).
        start_date=datetime.now(timezone.utc) + timedelta(hours=INQUISITION_CADENCE_HOURS, minutes=30),
        id="inquisition_prosecute",
        name="cardeep inquisition prosecution (adjudicate pending claims)",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    # audit P2 price_trap v2: daily cohort price-anomaly detector. QUARANTINE-only + reversible;
    # opens gestion_items that hide cohort-implausible-priced cars from servable_vehicle. €0 (DB
    # reads + upserts). Additive job id — does NOT touch SourceEntry/source_health/connector keys.
    scheduler.add_job(
        gestionador_detect_job,
        trigger="interval",
        hours=GESTIONADOR_DETECT_CADENCE_HOURS,
        id="gestionador_detect",
        name="cardeep gestionador price_trap detector",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    # audit P2 B-canonical-key (forward-coverage): keep the audit pre-image filled as new entities
    # arrive. Self-verifying (re-hash gate) + MVCC-clean (only NULL→value UPDATEs). Additive job id;
    # touches no SourceEntry/source_health/connector key.
    scheduler.add_job(
        canonical_key_backfill_job,
        trigger="interval",
        hours=CANONICAL_KEY_BACKFILL_CADENCE_HOURS,
        id="canonical_key_backfill",
        name="cardeep canonical_key forward-coverage",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    # F4 (00-marketplace-engine.md): daily per-source change-rate re-estimate. Writes ONLY
    # the estimate columns (migration 0076); never flips cadence_mode (a separate, deliberate
    # operator rollout step). Additive job id; touches no SourceEntry/connector key.
    scheduler.add_job(
        cadence_estimate_job,
        trigger="interval",
        hours=CADENCE_ESTIMATE_CADENCE_HOURS,
        id="cadence_estimate",
        name="cardeep F4 adaptive cadence estimate",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    # FASE-2 ops-hardening: keep the observable scheduler_lease fresh so a crashed holder is
    # diagnosable (docs/DEPLOY-DURABLE-DAEMONS.md §4). Module-level picklable job + literal args
    # (the SQLAlchemy jobstore pickles jobs). Best-effort + inert without migration 0054.
    scheduler.add_job(
        _lease_heartbeat_job,
        trigger="interval",
        minutes=heartbeat_interval_minutes(),
        args=[_SCHEDULER_SINGLETON_LOCK, "harvest"],
        id="lease_heartbeat",
        name="cardeep scheduler lease heartbeat",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )

    # Refresh the product_stats cache off-request so GET /stats is a single-row read, not a ~83s
    # 5x COUNT(DISTINCT)/JOIN over millions. Best-effort + additive; the API falls back to live compute
    # until the first refresh lands. Activates on the next scheduler restart.
    scheduler.add_job(
        _refresh_product_stats_job,
        trigger="interval",
        minutes=PRODUCT_STATS_REFRESH_MIN,
        id="product_stats_refresh",
        name="cardeep product_stats cache refresh (fast /stats)",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    # F6 (00-marketplace-engine.md): daily purge of engine_heartbeat_log rows past retention.
    # Additive job id; touches no SourceEntry/source_health/connector key. Best-effort + inert
    # without migration 0085.
    scheduler.add_job(
        heartbeat_log_purge_job,
        trigger="interval",
        hours=HEARTBEAT_LOG_PURGE_CADENCE_HOURS,
        id="heartbeat_log_purge",
        name="cardeep F6 heartbeat ledger purge",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    log.info(
        "Scheduler started — heartbeat every %d min, silence watchdog every 1h, "
        "inquisition cadence every %dh — jobstore: %s",
        TICK_INTERVAL_MINUTES, INQUISITION_CADENCE_HOURS, DB_URL,
    )
    log.info("Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")
    finally:
        scheduler.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cardeep B2.2 durable scheduler — single-producer heartbeat "
            "(APScheduler 3.x + SQLAlchemyJobStore on cardeep-pg)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print which sources are DUE right now and what command would be "
            "launched, then exit WITHOUT running anything."
        ),
    )
    parser.add_argument(
        "--check-silence",
        action="store_true",
        help=(
            "Print sources that have been silent for > 2× their harvest interval. "
            "READ-ONLY: does NOT fire alerts or modify any DB row, then exit."
        ),
    )
    args = parser.parse_args()

    if args.dry_run:
        _dry_run()
        return

    if args.check_silence:
        _check_silence()
        return

    _start_scheduler()


if __name__ == "__main__":
    main()
