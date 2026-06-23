"""Continuous DISCOVERY orchestration — the 6th axis of the plan (§1.4): discovery is
incremental/recurrent, not one-shot.

This is the discovery counterpart of pipeline/ops/scheduler.py (which schedules *harvest*).
It is a separate, self-contained producer so it never touches the harvest scheduler's
registry or its host advisory lock. Each discovery vector (V2–V6) is wired with its own
cadence and recipe-first sampling knobs, ready for the national VPS sweep yet verifiable
locally (--dry-run / --once).

Cadences (plano §1.4):
  borme_cnae        24h   — daily, to catch the delta of registral altas/bajas
  collapse_invisible 168h — weekly, re-collapse after each discovery wave
  overture          720h  — monthly, tracks Overture's monthly release
  graph_recursive   720h  — monthly, re-walk corporate graphs
  dork_municipal    2160h — quarterly, full 8.132-municipality sweep is expensive

Due-tracking reuses `source_health` (the same table the harvest silence-watchdog reads),
via a direct, €0 upsert — NOT pipeline.ops.health.record_run, whose success path triggers
harvest-only side effects (reconcile_gone / coverage gate) that are meaningless for a
discovery source that owns no vehicles. The rows still surface in the existing
--check-silence watchdog and dry-run gap report.

Usage:
  python -m pipeline.discover_schedule --seed       # register cadence rows in source_health
  python -m pipeline.discover_schedule --dry-run    # show cadences + which vectors are DUE
  python -m pipeline.discover_schedule --once VEC   # run one vector now (ignores due)
  python -m pipeline.discover_schedule --tick       # run all DUE vectors once (cron-friendly)
  python -m pipeline.discover_schedule --serve      # blocking APScheduler (own advisory lock)
"""
from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

import asyncpg

_ASYNCPG_DSN = os.environ.get(
    "CARDEEP_ASYNCPG_DSN",
    os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"),
)

TICK_INTERVAL_MINUTES = int(os.environ.get("CARDEEP_DISCOVERY_TICK_MIN", "60"))
SUBPROCESS_TIMEOUT_SEC = int(os.environ.get("CARDEEP_DISCOVERY_TIMEOUT", "21600"))  # 6h
BREAKER_TRIP_AT = 3
_LOCK_KEY = 0x43415244 + 1  # 'CARD'+1 — distinct from the harvest scheduler's singleton lock


@dataclass(frozen=True)
class DiscoveryJob:
    source_key: str
    vector: str                      # argument to `python -m pipeline.discover <vector>`
    cadence_hours: int
    orthogonal: bool                 # is this an MSE list (lists.py) or a dependent/resolution vector
    env: dict[str, str] = field(default_factory=dict)  # recipe-first sampling defaults (env-overridable)
    requires_env: tuple[str, ...] = ()  # scheduler GATES auto-run if any of these env vars is absent


# The 5 discovery vectors V2–V6. env values are conservative recipe-first defaults so a local
# tick is cheap; the national VPS sweep overrides them via real env (e.g. unset the limits).
DISCOVERY_REGISTRY: dict[str, DiscoveryJob] = {
    "borme_cnae": DiscoveryJob(
        "borme_cnae", "borme_cnae", cadence_hours=24, orthogonal=True,
        env={"CARDEEP_BORME_DAYS": os.environ.get("CARDEEP_BORME_DAYS", "1")}),
    "collapse_invisible": DiscoveryJob(
        "collapse_invisible", "collapse_invisible", cadence_hours=168, orthogonal=False,
        env={}),
    "overture": DiscoveryJob(
        "overture", "overture", cadence_hours=720, orthogonal=True, env={}),
    "graph_recursive": DiscoveryJob(
        "graph_recursive", "graph_recursive", cadence_hours=720, orthogonal=False,
        env={"CARDEEP_GRAPH_LIMIT": os.environ.get("CARDEEP_GRAPH_LIMIT", "200")}),
    "dork_municipal": DiscoveryJob(
        "dork_municipal", "dork_municipal", cadence_hours=2160, orthogonal=True,
        env={k: os.environ[k] for k in ("CARDEEP_SEARXNG_URL",) if k in os.environ},
        # GATE: the adapter's DuckDuckGo fallback is fine for a bounded manual `--once` run
        # (CARDEEP_DORK_LIMIT), but an unbounded national scheduled sweep hammers DDG and risks a
        # ban. The scheduler will not AUTO-run dork without a quota-free SearXNG endpoint.
        requires_env=("CARDEEP_SEARXNG_URL",)),
}


async def _seed(conn: asyncpg.Connection) -> int:
    """Register/refresh a source_health cadence row per discovery vector (idempotent, €0)."""
    n = 0
    for job in DISCOVERY_REGISTRY.values():
        await conn.execute(
            """INSERT INTO source_health (source_key, harvest_interval_hours, status)
               VALUES ($1, $2, 'unknown')
               ON CONFLICT (source_key) DO UPDATE
                 SET harvest_interval_hours = EXCLUDED.harvest_interval_hours""",
            job.source_key, job.cadence_hours)
        n += 1
    return n


async def _due(conn: asyncpg.Connection) -> list[str]:
    """Discovery source_keys whose cadence has elapsed (and breaker not tripped)."""
    rows = await conn.fetch(
        """SELECT source_key, harvest_interval_hours, last_ok, last_fail, consecutive_fails
           FROM source_health WHERE source_key = ANY($1::text[])""",
        list(DISCOVERY_REGISTRY))
    due: list[tuple[float, str]] = []
    now = datetime.now(timezone.utc)
    for r in rows:
        if (r["consecutive_fails"] or 0) >= BREAKER_TRIP_AT:
            continue
        last = r["last_ok"] or r["last_fail"]
        overdue_h = float("inf") if last is None else (now - last).total_seconds() / 3600.0
        if overdue_h >= (r["harvest_interval_hours"] or 0):
            due.append((overdue_h, r["source_key"]))
    due.sort(reverse=True)  # most overdue first
    return [k for _o, k in due]


def _gated(job: DiscoveryJob) -> str | None:
    """Return the first required env var that is ABSENT (gating the vector from AUTO-run), or None.

    Why: dork_municipal requires SearXNG. Its DuckDuckGo HTML fallback produces results for a bounded
    manual `--once` run, but an unbounded national scheduled sweep (8.132 municipalities x 5 templates
    ~= 40k requests) hammers DDG and risks a ban — so the daemon refuses to auto-run it without a
    quota-free SearXNG endpoint. An explicit `--once <vector>` overrides the gate (operator intent)."""
    for var in job.requires_env:
        if not os.environ.get(var):
            return var
    return None


async def _record(conn: asyncpg.Connection, source_key: str, *, ok: bool, rows: int | None,
                  cadence_hours: int, error: str | None = None) -> None:
    """€0 source_health upsert for a discovery run (no harvest side-effects). Also writes a
    harvest_run audit row so the run is visible in the same audit trail as harvest."""
    await conn.execute(
        "INSERT INTO harvest_run (source_key, finished_at, ok, rows, error) "
        "VALUES ($1, now(), $2, $3, $4)", source_key, ok, rows, error)
    if ok:
        await conn.execute(
            """INSERT INTO source_health (source_key, last_ok, consecutive_fails, status,
                   harvest_interval_hours)
               VALUES ($1, now(), 0, 'healthy', $2)
               ON CONFLICT (source_key) DO UPDATE
                 SET last_ok = now(), consecutive_fails = 0, status = 'healthy',
                     harvest_interval_hours = EXCLUDED.harvest_interval_hours""",
            source_key, cadence_hours)
    else:
        await conn.execute(
            """INSERT INTO source_health (source_key, last_fail, consecutive_fails, status,
                   harvest_interval_hours)
               VALUES ($1, now(), 1, 'degraded', $2)
               ON CONFLICT (source_key) DO UPDATE
                 SET last_fail = now(),
                     consecutive_fails = source_health.consecutive_fails + 1,
                     status = CASE WHEN source_health.consecutive_fails + 1 >= 3
                                   THEN 'down' ELSE 'degraded' END,
                     harvest_interval_hours = EXCLUDED.harvest_interval_hours""",
            source_key, cadence_hours)


def _run_vector(job: DiscoveryJob) -> tuple[int, int | None]:
    """Launch `python -m pipeline.discover <vector>` with the job's recipe-first env.
    Returns (exit_code, parsed_new_count|None)."""
    cmd = [sys.executable, "-m", "pipeline.discover", job.vector]
    child_env = {**os.environ, "PYTHONIOENCODING": "utf-8", **job.env}
    print(f"[discovery] LAUNCH {job.source_key} -> {' '.join(cmd)} env+={list(job.env)}")
    try:
        res = subprocess.run(cmd, timeout=SUBPROCESS_TIMEOUT_SEC, check=False,
                             env=child_env, capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        print(f"[discovery] TIMEOUT {job.source_key}")
        return -1, None
    sys.stdout.write(res.stdout[-2000:] if res.stdout else "")
    new = None
    for line in (res.stdout or "").splitlines():
        if "] new=" in line:
            try:
                new = int(line.split("] new=")[1].split()[0])
            except (IndexError, ValueError):
                pass
    return res.returncode, new


async def _tick(only: str | None = None) -> dict:
    conn = await asyncpg.connect(_ASYNCPG_DSN)
    try:
        await _seed(conn)
        keys = [only] if only else await _due(conn)
        ran: dict[str, dict] = {}
        for key in keys:
            job = DISCOVERY_REGISTRY[key]
            # AUTO-run gate (an explicit --once VECTOR bypasses it: operator intent).
            gate = None if only else _gated(job)
            if gate:
                print(f"[discovery] GATED {key}: missing {gate} — skipped (not run, not failed)")
                ran[key] = {"gated": gate}
                continue
            rc, new = _run_vector(job)
            await _record(conn, key, ok=(rc == 0), rows=new, cadence_hours=job.cadence_hours,
                          error=None if rc == 0 else f"exit {rc}")
            ran[key] = {"exit": rc, "new": new}
        return {"ran": ran, "due_checked": keys}
    finally:
        await conn.close()


async def _dry_run() -> None:
    conn = await asyncpg.connect(_ASYNCPG_DSN)
    try:
        await _seed(conn)
        due = set(await _due(conn))
        print("=" * 72)
        print("CARDEEP DISCOVERY SCHEDULER — DRY RUN")
        print(f"  tick every {TICK_INTERVAL_MINUTES} min | timeout {SUBPROCESS_TIMEOUT_SEC}s")
        print(f"  {datetime.now(timezone.utc).isoformat()}")
        print("=" * 72)
        for job in sorted(DISCOVERY_REGISTRY.values(), key=lambda j: j.cadence_hours):
            gate = _gated(job)
            mark = "GATE" if gate else ("DUE" if job.source_key in due else "   ")
            ortho = "orthogonal" if job.orthogonal else "non-ortho "
            print(f"  [{mark}] {job.source_key:20s} cadence={job.cadence_hours:>5}h  {ortho}  "
                  f"env={list(job.env)}" + (f"  GATED:needs {gate}" if gate else ""))
        print(f"\n  {len(due)} vector(s) DUE now.")
    finally:
        await conn.close()


def _serve() -> None:
    from apscheduler.schedulers.blocking import BlockingScheduler

    import psycopg2

    from pipeline.ops.lock_heartbeat import (
        check_and_clear_stale_lease,
        heartbeat_interval_minutes,
        record_heartbeat,
    )
    from pipeline.config_guard import require_prod_secrets

    raw = os.environ.get("CARDEEP_DSN_KW",
                         "host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only")
    # FASE-2 ops-hardening: in prod, fail fast if a DSN still carries the dev credential. No-op in
    # dev/test (CARDEEP_ENV unset) — byte-identical behaviour.
    require_prod_secrets((raw, "CARDEEP_DSN_KW"), (_ASYNCPG_DSN, "CARDEEP_ASYNCPG_DSN"))
    lock = psycopg2.connect(raw)
    lock.autocommit = True
    cur = lock.cursor()
    cur.execute("SELECT pg_try_advisory_lock(%s)", (_LOCK_KEY,))
    if not cur.fetchone()[0]:
        # Held: surface a STALE lease (crashed prior holder PG has not reaped) and retry once.
        # pg_try_advisory_lock is the atomic mutex — this can never steal a live lock. Best-effort;
        # inert without migration 0054.
        reacquired = False
        if check_and_clear_stale_lease(lock, _LOCK_KEY):
            cur.execute("SELECT pg_try_advisory_lock(%s)", (_LOCK_KEY,))
            reacquired = bool(cur.fetchone()[0])
        if not reacquired:
            raise SystemExit("another discovery scheduler holds the advisory lock; refusing to start")
    # FASE-2 ops-hardening: claim the observable lease (best-effort; inert without migration 0054).
    record_heartbeat(lock, _LOCK_KEY, holder="discovery")
    sched = BlockingScheduler(timezone="UTC")
    sched.add_job(lambda: asyncio.run(_tick()), trigger="interval",
                  minutes=TICK_INTERVAL_MINUTES, id="discovery_tick",
                  max_instances=1, coalesce=True, misfire_grace_time=600)
    # FASE-2 ops-hardening: keep the lease fresh on the held lock connection (€0, MemoryJobStore so
    # the closure is fine). docs/DEPLOY-DURABLE-DAEMONS.md §4.
    sched.add_job(lambda: record_heartbeat(lock, _LOCK_KEY, holder="discovery"),
                  trigger="interval", minutes=heartbeat_interval_minutes(),
                  id="lease_heartbeat", max_instances=1, coalesce=True, misfire_grace_time=120)
    print(f"[discovery] scheduler started — tick every {TICK_INTERVAL_MINUTES} min")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="discover_schedule")
    ap.add_argument("--seed", action="store_true", help="register cadence rows then exit")
    ap.add_argument("--dry-run", action="store_true", help="show cadences + DUE vectors")
    ap.add_argument("--once", metavar="VECTOR", help="run one vector now (ignores due)")
    ap.add_argument("--tick", action="store_true", help="run all DUE vectors once")
    ap.add_argument("--serve", action="store_true", help="blocking scheduler loop")
    args = ap.parse_args(argv)

    if args.once and args.once not in DISCOVERY_REGISTRY:
        print(f"unknown vector '{args.once}'. available: {list(DISCOVERY_REGISTRY)}")
        return 2
    if args.seed:
        print("seeded:", asyncio.run(_seed_only()))
    elif args.dry_run:
        asyncio.run(_dry_run())
    elif args.once:
        print(asyncio.run(_tick(only=args.once)))
    elif args.tick:
        print(asyncio.run(_tick()))
    elif args.serve:
        _serve()
    else:
        asyncio.run(_dry_run())
    return 0


async def _seed_only() -> int:
    conn = await asyncpg.connect(_ASYNCPG_DSN)
    try:
        return await _seed(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    sys.exit(main())
