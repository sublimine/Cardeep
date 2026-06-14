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

Usage:
    python -m pipeline.ops.scheduler             # start the live scheduler (blocking)
    python -m pipeline.ops.scheduler --dry-run   # print what is DUE right now, then exit
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import NamedTuple

import psycopg2

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [scheduler] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
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

# ---------------------------------------------------------------------------
# Heartbeat cadence
# ---------------------------------------------------------------------------
TICK_INTERVAL_MINUTES: int = 15

# Circuit breaker: skip sources with consecutive_fails >= this threshold
BREAKER_TRIP_AT: int = 3

# Subprocess timeout: generous to allow full crawls (24h sources can take ~2h)
# This is a hard wall to prevent a stuck process from blocking the scheduler forever.
SUBPROCESS_TIMEOUT_SEC: int = int(os.environ.get("CARDEEP_SUBPROCESS_TIMEOUT", 14400))  # 4h default

# ---------------------------------------------------------------------------
# Source → module registry
#
# Built by grepping SOURCE_KEY/FAMILY_KEY/MB_SOURCE_KEY constants from
# pipeline/platform/*.py (verified 2026-06-14).
#
# Multi-source modules:
#   group_rentacar_vo_wholesale: 6 source_keys → same module, disambiguated
#     via --member <key> where key = source_key suffix after "group_rentacar_vo_"
#   faciliteacoches_racc_wholesale: 2 source_keys → same module, disambiguated
#     via --members <faciliteacoches|racc> (maps to "faciliteacoches" / "racc")
#   group_vo_chains_wholesale: 4 source_keys → same module, via --members <key>
#     where key = source_key suffix after "group_vo_chains_"
#   oem_bmw_mini_wholesale: 2 source_keys → same module, via --brand <bmw|mini>
#
# The "cmd" field is the full argv list that would be passed to subprocess.
# All entries use sys.executable so the correct interpreter (venv or system) is used.
# ---------------------------------------------------------------------------

class SourceEntry(NamedTuple):
    source_key: str
    module: str          # python -m <module>
    extra_args: list[str]  # additional CLI args for that specific source_key


def _build_registry() -> dict[str, SourceEntry]:
    """Return the authoritative source_key → SourceEntry mapping.

    Multi-source modules produce one entry per source_key with the appropriate
    --member / --members / --brand argument to isolate that exact source.
    """
    entries: list[SourceEntry] = [
        # ── Tier-1 (24h) ─────────────────────────────────────────────────
        SourceEntry("autocasion_wholesale",
                    "pipeline.platform.autocasion_wholesale", []),
        SourceEntry("coches_com_wholesale",
                    "pipeline.platform.coches_com_wholesale", []),
        SourceEntry("coches_net_wholesale",
                    "pipeline.platform.coches_net_wholesale", []),
        SourceEntry("milanuncios_wholesale",
                    "pipeline.platform.milanuncios_wholesale", []),
        SourceEntry("motor_es_wholesale",
                    "pipeline.platform.motor_es_wholesale", []),
        SourceEntry("wallapop_wholesale",
                    "pipeline.platform.wallapop_wholesale", []),

        # ── OEM / groups / subastas (168h) ───────────────────────────────
        SourceEntry("carandclassic_wholesale",
                    "pipeline.platform.carandclassic_wholesale", []),
        SourceEntry("dasweltauto_wholesale",
                    "pipeline.platform.dasweltauto_wholesale", []),
        # faciliteacoches_wholesale and racc_ocasion_wholesale share a module;
        # each is invoked independently via --members to guarantee individual
        # record_run writes and independent health tracking.
        SourceEntry("faciliteacoches_wholesale",
                    "pipeline.platform.faciliteacoches_racc_wholesale",
                    ["--members", "faciliteacoches"]),
        SourceEntry("racc_ocasion_wholesale",
                    "pipeline.platform.faciliteacoches_racc_wholesale",
                    ["--members", "racc"]),
        # group_importador: single source key
        SourceEntry("group_importador_modrive",
                    "pipeline.platform.group_importador_wholesale", []),
        # group_rentacar_vo: 6 source keys, same module, --member <suffix>
        SourceEntry("group_rentacar_vo_athlon",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "athlon"]),
        SourceEntry("group_rentacar_vo_okmobility",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "okmobility"]),
        SourceEntry("group_rentacar_vo_centauro",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "centauro"]),
        SourceEntry("group_rentacar_vo_recordgo",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "recordgo"]),
        SourceEntry("group_rentacar_vo_arval",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "arval"]),
        SourceEntry("group_rentacar_vo_northgate",
                    "pipeline.platform.group_rentacar_vo_wholesale",
                    ["--member", "northgate"]),
        # group_subastas: single source key (AYVENS_SOURCE_KEY = group_subastas_wholesale)
        SourceEntry("group_subastas_wholesale",
                    "pipeline.platform.group_subastas_wholesale", []),
        # group_vo_chains: 4 source keys, same module, --members <suffix>
        SourceEntry("group_vo_chains_flexicar",
                    "pipeline.platform.group_vo_chains_wholesale",
                    ["--members", "flexicar"]),
        SourceEntry("group_vo_chains_ocasionplus",
                    "pipeline.platform.group_vo_chains_wholesale",
                    ["--members", "ocasionplus"]),
        SourceEntry("group_vo_chains_clicars",
                    "pipeline.platform.group_vo_chains_wholesale",
                    ["--members", "clicars"]),
        SourceEntry("group_vo_chains_carplus",
                    "pipeline.platform.group_vo_chains_wholesale",
                    ["--members", "carplus"]),
        SourceEntry("localizavo_wholesale",
                    "pipeline.platform.localizavo_wholesale", []),
        SourceEntry("mercedes_benz_wholesale",
                    "pipeline.platform.oem_mercedes_benz_wholesale", []),
        SourceEntry("miclasico_wholesale",
                    "pipeline.platform.miclasico_wholesale", []),
        SourceEntry("motorflash_wholesale",
                    "pipeline.platform.motorflash_wholesale", []),
        SourceEntry("nissan_intelligent_choice_wholesale",
                    "pipeline.platform.oem_nissan_mazda_honda_wholesale", []),
        SourceEntry("oem_audi_wholesale",
                    "pipeline.platform.oem_audi_wholesale", []),
        # oem_bmw_mini: 2 source keys, same module, --brand <bmw|mini>
        SourceEntry("oem_bmw_premium_selection_wholesale",
                    "pipeline.platform.oem_bmw_mini_wholesale",
                    ["--brand", "bmw"]),
        SourceEntry("oem_mini_next_wholesale",
                    "pipeline.platform.oem_bmw_mini_wholesale",
                    ["--brand", "mini"]),
        SourceEntry("oem_ford_wholesale",
                    "pipeline.platform.oem_ford_wholesale", []),
        SourceEntry("oem_hyundai_wholesale",
                    "pipeline.platform.oem_hyundai_wholesale", []),
        SourceEntry("oem_kia_wholesale",
                    "pipeline.platform.oem_kia_wholesale", []),
        SourceEntry("oem_seat_cupra_new_stock",
                    "pipeline.platform.oem_seat_cupra_new_stock", []),
        SourceEntry("oem_seat_cupra_wholesale",
                    "pipeline.platform.oem_seat_cupra_wholesale", []),
        SourceEntry("oem_toyota_lexus_wholesale",
                    "pipeline.platform.oem_toyota_lexus_wholesale", []),
        SourceEntry("oem_volvo_jlr_suzuki_wholesale",
                    "pipeline.platform.oem_volvo_jlr_suzuki_wholesale", []),
        SourceEntry("renew_wholesale",
                    "pipeline.platform.renew_wholesale", []),
        SourceEntry("spoticar_wholesale",
                    "pipeline.platform.spoticar_wholesale", []),
        SourceEntry("subastacar_wholesale",
                    "pipeline.platform.subastacar_wholesale", []),

        # ── Families (720h) ───────────────────────────────────────────────
        SourceEntry("family_builder_wholesale",
                    "pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale",
                    []),
        SourceEntry("family_cms_wp",
                    "pipeline.platform.family_cms_wordpress_dominated__wholesale", []),
        SourceEntry("family_dealerk_wp",
                    "pipeline.platform.family_dealerk_wholesale", []),
        SourceEntry("family_dms_vendor_platforms",
                    "pipeline.platform.family_dms_vendor_platforms__wholesale", []),
        SourceEntry("family_framework_webbuilder",
                    "pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale",
                    []),
        SourceEntry("family_generic_custom",
                    "pipeline.platform.family_generic_custom_wholesale", []),
        SourceEntry("family_unreachable",
                    "pipeline.platform.family_unreachable_wholesale", []),
    ]
    return {e.source_key: e for e in entries}


# Module-level registry (built once at import time)
REGISTRY: dict[str, SourceEntry] = _build_registry()

# source_keys present in source_health that have NO mapping in REGISTRY.
# Declared explicitly (never invented) — these are excluded from scheduling.
# as24_wholesale has a SOURCE_KEY constant but is NOT in source_health; it is
# a special case (handled outside the scheduler via its own governor).
UNMAPPED_KEYS: frozenset[str] = frozenset()  # populated dynamically in _gap_report()


# ---------------------------------------------------------------------------
# DB query helpers (synchronous psycopg2 — scheduler context is sync)
# ---------------------------------------------------------------------------

def _due_sources(conn: "psycopg2.connection") -> list[tuple[str, int, datetime | None, datetime | None]]:
    """Return (source_key, harvest_interval_hours, last_ok, last_fail) for sources that are
    DUE for harvesting, ordered by most-overdue first.

    DUE condition:
      now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
        >= harvest_interval_hours * interval '1 hour'

    Sources with open circuit breakers (consecutive_fails >= BREAKER_TRIP_AT)
    are excluded — the breaker check is done here to avoid the extra round-trip
    to source_breaker (consecutive_fails mirrors the streak in source_health).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                source_key,
                harvest_interval_hours,
                last_ok,
                last_fail,
                consecutive_fails
            FROM source_health
            WHERE
                now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
                    >= harvest_interval_hours * interval '1 hour'
            ORDER BY
                now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz) DESC
            """
        )
        rows = cur.fetchall()

    result = []
    for source_key, interval_h, last_ok, last_fail, consecutive_fails in rows:
        if consecutive_fails >= BREAKER_TRIP_AT:
            log.info(
                "skip %s — breaker open (consecutive_fails=%d >= %d)",
                source_key, consecutive_fails, BREAKER_TRIP_AT,
            )
            continue
        result.append((source_key, interval_h, last_ok, last_fail))
    return result


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
    """
    entry = REGISTRY[source_key]
    cmd = _build_cmd(entry)
    log.info("LAUNCH %s → %s", source_key, " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            timeout=SUBPROCESS_TIMEOUT_SEC,
            check=False,   # do not raise on non-zero; we log the exit code
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
        _run_source(source_key)

    log.info("=== heartbeat_tick END ===")


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
    print("CARDEEP SCHEDULER — DRY RUN")
    print(f"  DB:        {_RAW_DSN}")
    print(f"  Tick:      every {TICK_INTERVAL_MINUTES} min")
    print(f"  Timeout:   {SUBPROCESS_TIMEOUT_SEC}s per subprocess")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)

    print(f"\nSOURCE REGISTRY COVERAGE")
    print(f"  Total source_health rows : {len(all_keys)}")
    print(f"  Mapped to a module       : {len(mapped_keys)}")
    print(f"  UNMAPPED (gap)           : {len(unmapped_keys)}")
    if unmapped_keys:
        print("\n  ⚠ UNMAPPED SOURCE KEYS (excluded from scheduling):")
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
# Live scheduler
# ---------------------------------------------------------------------------

def _start_scheduler() -> None:
    """Start the durable BlockingScheduler. Blocks until SIGINT/SIGTERM."""
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.schedulers.blocking import BlockingScheduler

    jobstores = {
        "default": SQLAlchemyJobStore(url=DB_URL),
    }
    scheduler = BlockingScheduler(jobstores=jobstores, timezone="UTC")

    # Replace any stale job definition with the current one on each start.
    # This ensures cadence changes (TICK_INTERVAL_MINUTES) take effect on restart
    # without manual DB cleanup.
    job_id = "heartbeat_tick"
    scheduler.add_job(
        heartbeat_tick,
        trigger="interval",
        minutes=TICK_INTERVAL_MINUTES,
        id=job_id,
        name="cardeep heartbeat tick",
        replace_existing=True,
        max_instances=1,   # enforce single-producer: never two ticks overlapping
        coalesce=True,     # if the scheduler was down for multiple ticks, fire once
        misfire_grace_time=300,  # allow 5 min of slippage before skipping a misfired tick
    )

    log.info(
        "Scheduler started — heartbeat every %d min — jobstore: %s",
        TICK_INTERVAL_MINUTES, DB_URL,
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
    args = parser.parse_args()

    if args.dry_run:
        _dry_run()
        return

    _start_scheduler()


if __name__ == "__main__":
    main()
