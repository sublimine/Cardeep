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
import subprocess
import sys
from datetime import datetime, timezone
from typing import NamedTuple

import psycopg2

from pipeline.ops.silence_watchdog import (
    find_silent_sources,
    run_silence_watchdog,
)

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
# asyncpg URL DSN for the WF-INQUISITION cadence job (δ). Distinct from _RAW_DSN
# above, which is the psycopg2 keyword form; asyncpg requires a postgres:// URL.
_ASYNCPG_DSN = os.environ.get(
    "CARDEEP_ASYNCPG_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)

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
        # Audit 2026-06-15 Phase 2: production scheduled the PROOF/capped strategy for EVERY Tier-1
        # platform — autocasion (10k SSR cap), coches.net (~500-car 5-page slice), wallapop (flat
        # ~347k vs 651k), coches.com (16k VO-only), motor.es (10k VO-only). Each entry below now runs
        # the CANONICAL COMPLETE harvester. The source_key is KEPT equal to the *_SOURCE_KEY the
        # connector writes to source_health (facets import their wholesale's SOURCE_KEY), so
        # health/breaker/harvest_run continuity and due-selection matching hold — this also repairs
        # the F-autocasion-orphaned regression (a renamed key orphaned autocasion from scheduling).
        SourceEntry("autocasion_wholesale",   # key=AC_SOURCE_KEY (facet imports it); module=facet
                    "pipeline.platform.autocasion_facet", ["--segment", "all", "--makes", "all"]),
        SourceEntry("coches_com_wholesale",   # no facet module; --all --segment all = full uncapped drain
                    "pipeline.platform.coches_com_wholesale", ["--all", "--segment", "all"]),
        SourceEntry("coches_net_wholesale",   # key=COCHES_SOURCE_KEY (facet imports it); module=facet
                    "pipeline.platform.coches_net_facet", []),
        SourceEntry("coches_net_segments",    # own key (audit C-cochesnet-segments); new/km0/renting, seeded 0039
                    "pipeline.platform.coches_net_segments", []),
        SourceEntry("milanuncios_wholesale",
                    "pipeline.platform.milanuncios_wholesale", []),
        SourceEntry("motor_es_wholesale",     # --full --segment all = full census (vo+vn+renting)
                    "pipeline.platform.motor_es_wholesale", ["--full", "--segment", "all"]),
        SourceEntry("wallapop_wholesale",     # key=WP_SOURCE_KEY (facet imports it); module=facet
                    "pipeline.platform.wallapop_facet", []),

        # ── OEM / groups / subastas (168h) ───────────────────────────────
        # AS24 (audit C-as24-unscheduled): schedule autoscout24_wholesale — it WRITES record_run and is
        # governor-paced. NOT the literal 'as24' per-dealer driver (scale_as24.py), which never writes
        # last_ok -> would be perpetually DUE every 15-min tick = the AS24 ban scar. Ban-safe 168h cadence
        # lives in the 0039 seed row (the connector doesn't pass harvest_interval_hours). This 12-page
        # proof slice closes the cadence/auto-repair gap, NOT full ~278k coverage (that stays operator-run).
        SourceEntry("as24_wholesale",
                    "pipeline.platform.autoscout24_wholesale", []),
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
# (audit P2 C-as24): as24_wholesale is now seeded in source_health (migration 0039) and mapped in
# REGISTRY above — it is the AS24 record_run writer, scheduled at the 0039 168h cadence. The literal
# 'as24' per-dealer driver (scale_as24.py) stays operator-run and is intentionally NOT scheduled.
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

    from pipeline.gestionador.run import run_price_trap

    log.info("=== gestionador_detect (price_trap) START ===")

    async def _run() -> dict:
        conn = await asyncpg.connect(_ASYNCPG_DSN)
        try:
            return await run_price_trap(conn)
        finally:
            await conn.close()

    try:
        summary = asyncio.run(_run())
        log.info("gestionador_detect: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("gestionador_detect: unexpected error: %s", exc)
    log.info("=== gestionador_detect (price_trap) END ===")


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
    print(f"  DB:        {_RAW_DSN}")
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

def _start_scheduler() -> None:
    """Start the durable BlockingScheduler. Blocks until SIGINT/SIGTERM."""
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.schedulers.blocking import BlockingScheduler

    # Single-producer HOST lock (AS24 scar: never two governors on one host — that 4x-hammer lost
    # 138 dealers). max_instances=1 only prevents overlapping ticks WITHIN one process; this
    # session-level pg advisory lock prevents a SECOND scheduler process from doubling the host's
    # aggregate request rate. It fails fast if another scheduler holds it and auto-releases when
    # this connection closes at process exit. _lock_conn is intentionally kept open for the
    # process lifetime — do not close it.
    _SCHEDULER_SINGLETON_LOCK = 0x43415244  # ASCII 'CARD' = 1128415556 — fixed host-singleton key
    _lock_conn = psycopg2.connect(_RAW_DSN)
    _lock_conn.autocommit = True
    _cur = _lock_conn.cursor()
    _cur.execute("SELECT pg_try_advisory_lock(%s)", (_SCHEDULER_SINGLETON_LOCK,))
    if not _cur.fetchone()[0]:
        _lock_conn.close()
        raise SystemExit(
            "another cardeep scheduler already holds the singleton advisory lock "
            f"({_SCHEDULER_SINGLETON_LOCK}); refusing to start a second producer on this host"
        )
    log.info("Acquired singleton scheduler advisory lock %s", _SCHEDULER_SINGLETON_LOCK)

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
