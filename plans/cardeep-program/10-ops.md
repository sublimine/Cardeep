# Operacion / Observabilidad — Keep the whole digital census harvesting, fresh, and honestly observable at EUR0

> This domain owns the heartbeat of CARDEEP: the two single-producer schedulers (harvest + discovery) that drive every connector, the source-health/circuit-breaker/alert layer that decides what is fresh vs. silent vs. broken, the lease-based liveness proof, and the CI gate that classifies the codebase faithfully. It exists so that the national digital footprint census never silently rots: if a point-of-sale source stops being harvested, or a connector starts failing, or data goes stale, an accurate alert fires once and auto-resolves on recovery — and an operator (human or agent) can prove the system is alive without guessing. Everything here is EUR0, self-hosted, and additive over the live `cardeep-pg` on `:5433`.

## Current state (verified)

All figures below were read directly from source in `C:\Users\elias\projects\cardeep` (branch `main`) on 2026-06-23. Where the recon brief asserted a value I confirmed it against the file; I do not restate DB-row counts I could not re-query here, and I flag them as recon-sourced.

**Schedulers (verified by reading source):**
- `pipeline/ops/scheduler.py` — harvest `BlockingScheduler` (APScheduler 3.x, `SQLAlchemyJobStore` on `cardeep-pg`). Host-singleton advisory lock `_SCHEDULER_SINGLETON_LOCK = 0x43415244` (= 1128354372, ASCII `CARD`) at line 913. Jobs registered via `scheduler.add_job`: `heartbeat_tick` (15 min), `silence_watchdog` (1 h), plus inquisition cadence/prosecute, gestionador, canonical-key backfill, product-stats refresh, and `lease_heartbeat` (2 min). `REGISTRY` built at line 330. Modes: `--dry-run` (print DUE sources), `--check-silence` (read-only). [VERIFIED]
- `pipeline/discover_schedule.py` — independent discovery scheduler. Lock `_LOCK_KEY = 0x43415244 + 1` (= 1128354373) at line 50. `DISCOVERY_REGISTRY` (line 65): `borme_cnae` 24 h, `collapse_invisible` 168 h, `overture` 720 h, `graph_recursive` 720 h, `dork_municipal` 2160 h. `dork_municipal` is gated on `CARDEEP_SEARXNG_URL` (DuckDuckGo HTML fallback only). [VERIFIED]

**Health / alert core (verified):**
- `pipeline/ops/health.py` — `record_run` (writes `harvest_run` + `source_health` + `source_breaker`), `fire_alert` (dedup by exact origin, line 295), `resolve_alerts` (line 327), `build_origin` (line 289) producing `<source_key>:<phase>[:<cdp_code>]`. On success `record_run` calls `resolve_alerts` with origin `build_origin(source_key, phase)` where phase is `scrape` (line 169-173). [VERIFIED]
- `pipeline/ops/silence_watchdog.py` — `find_silent_sources` (SQL, sources silent > 2× interval), `fire_silence_alert_sync` builds origin `<source>:silence` (line 127), dedups by UPDATE-or-INSERT. `run_silence_watchdog` only fires/updates — **it has NO resolve path**. [VERIFIED]
- `pipeline/ops/lock_heartbeat.py` — `scheduler_lease` table, TTL = 6 min (3× the 2-min heartbeat), `acquire_with_stale_retry`, fully best-effort/inert if migration `0054_scheduler_heartbeat.sql` is absent (it never creates the table). [VERIFIED]
- `migrations/0054_scheduler_heartbeat.sql` exists. [VERIFIED]

**CONFIRMED BUG (the central defect this domain must fix):** silence alerts live on origin `<source>:silence`; `record_run` resolves `<source>:scrape`. They never intersect, so a recovered source's silence alert stays open forever. Recon reports 7 such zombie silence alerts (`last_ok > alert.created_at`, still open). This is verified at the code level (two distinct origins, no cross-resolve) even without re-querying the DB. [VERIFIED — code path; recon-sourced — row count 7]

**CI (verified by reading `.github/workflows/ci.yml`):** 5 jobs — `bring-up-smoke` (install·import·migrate·collect-only), `db-tests` (self-seeding suite on ephemeral migrated Postgres, ignores files in `tests/ci_local_only.txt`, runs `pytest -m "not unit"`), `frontend-build` (`tsc -b && vite build`), `secret-scan` (gitleaks OSS container, `.gitleaks.toml`), and a separate `unit-tests` (`pytest -m unit`, DB-free). [VERIFIED]

**Docker / port convention (verified):** `docker-compose.yml` runs `postgres:16` as `cardeep-pg`, bound `127.0.0.1:5433:5432` — this is the **live served DB**. The experiment convention is documented in `plans/P-ci-census-fixture.md` and `plans/P-census-data-quality.md`: ephemeral docker on `:5434`, NEVER `:5433` without dry-run → golden → Ferrari → CI. [VERIFIED]

**Recon-sourced runtime metrics (could not re-query live DB here; carried from recon brief):** 56 `source_health` rows (50 healthy, 5 degraded, 1 unknown=`dork_municipal`); 0 open circuit breakers; 29 `harvest_run` in last 24 h (22 ok / 7 fail, ~667k rows ok); 53 open alerts (17 coverage, 8 silence, 3 critical); 7 zombie silence alerts; `scheduler_lease` 0 rows (heartbeat not yet written / scheduler not currently running); 6 active `apscheduler_jobs`; 1 unmapped key `as24_facet`; 42 `repair_attempt` (39 ok). [ASUMIDO — recon brief, not re-verified against DB in this session]

## Next-level objective

Reach a state where **every observable defect surfaces exactly once, accurately, and self-clears on recovery**, and where **liveness is provable, not inferred** — measurably:

1. **Zero zombie alerts:** open silence alerts for sources whose `last_ok > alert.created_at` = **0** at all times (currently 7). Closing the silence/scrape origin gap is the linchpin.
2. **Provable liveness:** `scheduler_lease` always has a fresh row (`last_heartbeat` within TTL) whenever a scheduler process is alive; a single `ops health` command answers "is the census breathing?" in < 2 s with a non-zero exit on staleness (currently 0 lease rows → unanswerable).
3. **No silent registry drift:** every `source_health` key maps to either `REGISTRY` or `DISCOVERY_REGISTRY`; unmapped keys (currently `as24_facet`) are either mapped or explicitly allow-listed with a documented reason — enforced by a CI test, so drift can never reappear.
4. **Honest freshness SLA per source:** each source carries a freshness target; staleness beyond 2× interval produces exactly one alert that auto-resolves, and an operator dashboard renders the full fleet's health from `source_health` alone with zero new infra.

This beats any human operator because the loop is continuous, dedup-correct, and self-resolving — no human watches 56 sources every hour, and no human reliably closes recovered alerts.

## Chosen technology (EUR0)

The current stack (APScheduler + Postgres tables) is already correct, single-producer, and crash-safe — **the right move is to harden and instrument it, not to swap orchestrators.** Adopting Dagster/Prefect/Airflow would be a rewrite that discards the verified advisory-lock singleton design and the `source_health` contract for no census benefit; that violates KISS/YAGNI. Research candidates are adopted only as **thin, additive, optional layers**:

| Need | Chosen tech | Why (vs. alternatives) | Source / URL | Integration effort |
|---|---|---|---|---|
| Keep orchestration | **APScheduler 3.x (in-repo, unchanged)** | Already single-producer, advisory-lock-guarded, crash-safe via `SQLAlchemyJobStore`. A full orchestrator rewrite (Dagster/Prefect) buys nothing here and risks the AS24 "two governors" scar the code explicitly avoids. | existing repo | none (retain) |
| Freshness-as-data SLA | **`source_health.harvest_interval_hours` + a typed freshness view** (in-repo SQL) | dbt source-freshness is the canonical pattern, but the repo is not dbt-centric; replicating its `error_after`/`warn_after` semantics as a Postgres view over `source_health` is EUR0, zero new dependency, and reuses the live table. | dbt pattern: https://github.com/dbt-labs/dbt-core | low (one migration + view) |
| Operator dashboard | **Single self-contained HTML/SQL health page served from existing `web/` + a read-only `ops health` CLI** | Grafana/Prometheus are excellent but add a daemon, scrape config, and a second datastore for 56 rows — overkill at this scale and against EUR0-minimal-infra. The truth already lives in `source_health`/`alert`/`harvest_run`; render it directly. Prometheus stays a **documented future option** if fleet size grows 100×. | Grafana: https://github.com/grafana/grafana (deferred) | low (one read-only view + page) |
| CI faithfulness | **Existing GitHub Actions + gitleaks OSS** (unchanged), extended with a registry-drift test | Already EUR0 and faithful; only add one pytest that asserts registry/health-key parity. | existing `.github/workflows/ci.yml` | trivial |

**Decision:** retain APScheduler; add freshness/observability as additive Postgres views and a CLI; defer Prometheus/Grafana behind a documented scaling trigger. This honors EUR0, additivity, and the verified architecture.

## Target architecture

```
                         ┌─────────────────────────────────────────────┐
                         │  cardeep-pg  (postgres:16, :5433, LIVE)       │
                         │                                               │
  harvest scheduler ───▶ │  source_health ◀── record_run (health.py)     │
  (lock 1128354372)      │  source_breaker ◀──┘                          │
   heartbeat_tick 15m    │  harvest_run   (audit trail)                  │
   silence_watchdog 1h   │  alert  (dedup by origin <src>:<phase>)       │
   lease_heartbeat 2m ──▶│  scheduler_lease (TTL 6m, liveness proof)     │
                         │  v_source_freshness  (NEW: SLA view)          │
  discovery scheduler ──▶│  apscheduler_jobs (persisted jobs)            │
  (lock 1128354373)      └───────────────────────────────────────────────┘
                                   │                         │
                                   ▼                         ▼
                       ops health CLI (read-only)   web/ health page (read-only)
                       exit!=0 on stale lease /      renders fleet status from
                       open critical alerts          source_health + alert
```

- **Alert lifecycle (fixed):** a source going silent → `silence_watchdog` fires one `<src>:silence` alert. On the next successful `record_run`, the watchdog's resolve path (NEW) closes any open `<src>:silence` whose `last_ok` is now newer than the alert — so silence and scrape origins reconcile.
- **Liveness:** `lease_heartbeat` writes `scheduler_lease` every 2 min; `ops health` treats a lease older than TTL as "scheduler dead" and exits non-zero.
- **Freshness SLA:** `v_source_freshness` exposes per-source `seconds_since_last_ok`, `interval_seconds`, and a derived `state` (fresh / warn / stale) for dashboard + CI.
- **Data safety:** every change is additive (new view, new resolve query, new CLI, new test). No existing served column is altered. All experiments run on ephemeral docker `:5434`.

## Execution phases

Each phase is ~1 PR, additive, reversible. Branch from `main` as `feature/ops-<phase>`. Cold-start context is included so a fresh agent needs no prior memory.

### Phase 1 — Close the silence/scrape origin gap (the zombie-alert bug)

**Cold-start context:** `pipeline/ops/silence_watchdog.py` fires alerts on origin `<src>:silence`; `pipeline/ops/health.py::record_run` resolves `<src>:scrape` (line 169-173). They never meet, so recovered sources keep open silence alerts (recon: 7 zombies). `run_silence_watchdog` (line ~174) currently only fires/updates.

**Tasks:**
1. Add `resolve_recovered_silence_alerts(conn)` in `silence_watchdog.py`: `UPDATE alert SET resolved_at=now() WHERE origin LIKE '%:silence' AND resolved_at IS NULL AND EXISTS (SELECT 1 FROM source_health sh WHERE sh.source_key = split_part(alert.origin,':',1) AND sh.last_ok > alert.created_at)`. Return count.
2. Call it at the start of `run_silence_watchdog` (resolve recovered before detecting new silence), so each hourly cycle self-heals.
3. Add unit test `tests/test_silence_resolve.py` (mark `unit`): seed a `source_health` row with `last_ok = now()`, an open `<src>:silence` alert with `created_at = now() - 1h`, assert it closes; and a still-silent source's alert stays open.

**Verification:**
```
# ephemeral, never :5433
docker run -d --rm --name cardeep-ops54 -e POSTGRES_PASSWORD=x -p 127.0.0.1:5434:5432 postgres:16
CARDEEP_DSN="host=127.0.0.1 port=5434 ..." python -m pytest tests/test_silence_resolve.py -q
python -m pytest -m unit -q   # full unit suite green
```
Dry-run readback against live (read-only): `python -m pipeline.ops.scheduler --check-silence` and a manual `SELECT count(*) FROM alert WHERE origin LIKE '%:silence' AND resolved_at IS NULL AND EXISTS(...)` should show the path; do NOT write to `:5433` until CI green.

**Exit criteria:** new test passes on `:5434`; full unit suite green; CI `db-tests` green; the zombie-resolve query returns the recovered set. **Rollback:** revert the PR — the resolve call is purely additive; removing it restores prior behavior with zero schema change.

### Phase 2 — Provable liveness: backfill the scheduler lease and add `ops health`

**Cold-start context:** `scheduler_lease` (migration `0054`) exists but recon shows 0 rows — the heartbeat hasn't written, so liveness is unprovable. `lock_heartbeat.py` provides `record_heartbeat`, `is_lease_stale`, TTL=6 min, all best-effort.

**Tasks:**
1. Verify migration `0054_scheduler_heartbeat.sql` is applied on live (`python -m <migrate-verify>` per CI step `Migrate verify`). If unapplied, that is the root cause of 0 rows — apply it (additive `CREATE TABLE IF NOT EXISTS`).
2. Confirm `lease_heartbeat` job is registered (line 1032-1037 of `scheduler.py`) and that `_lease_heartbeat_job` writes via a separate connection (it must not share the advisory-lock session). Already coded; this phase ensures it actually runs by validating on a supervised restart.
3. Add a read-only `python -m pipeline.ops.scheduler --health` (or new `pipeline/ops/health_cli.py`) that: reads `scheduler_lease` for both lock keys (1128354372, 1128354373), reports age vs TTL, counts open critical alerts, and exits non-zero if any lease is stale or a critical alert is open. No writes.

**Verification:**
```
python -m pipeline.ops.scheduler --health   # exits 0 when fresh, !=0 when stale
# integration on :5434: start scheduler briefly, confirm a scheduler_lease row appears
```
**Exit criteria:** `scheduler_lease` has a fresh row per running daemon; `--health` returns correct exit codes (tested both fresh and forced-stale on `:5434`); unit test for `is_lease_stale` boundary. **Rollback:** the CLI is read-only and additive; revert removes it. The lease write was already best-effort and inert without `0054`, so no destructive surface.

### Phase 3 — Eliminate registry drift and lock it with a CI test

**Cold-start context:** recon shows 1 `source_health` key (`as24_facet`) unmapped from `REGISTRY` + `DISCOVERY_REGISTRY`. `scheduler.py` has a comment (line 332-335) acknowledging keys that record_run but aren't in `REGISTRY` (the AS24 0039 cadence writer). Drift means a source could be tracked in health but never scheduled — a silent gap.

**Tasks:**
1. Add an explicit `ALLOWLISTED_HEALTH_KEYS` set in `scheduler.py` (or a sibling module) documenting each key that legitimately exists in `source_health` without a `REGISTRY`/`DISCOVERY_REGISTRY` entry, with a one-line reason (e.g. `as24_facet` → AS24 facet writer scheduled at 0039 168h cadence).
2. Add `tests/test_registry_parity.py` (mark `db` so it runs in `db-tests`): assert every `source_health.source_key` is in `REGISTRY ∪ DISCOVERY_REGISTRY ∪ ALLOWLISTED_HEALTH_KEYS`. Fails CI on new drift.

**Verification:**
```
CARDEEP_DSN=":5434" python -m pytest tests/test_registry_parity.py -q
python -m pipeline.ops.scheduler --dry-run   # prints DUE; confirm as24_facet handled
```
**Exit criteria:** parity test green on `:5434` with the allow-list; CI `db-tests` green. **Rollback:** revert PR; the allow-list and test are additive, no runtime behavior changes.

### Phase 4 — Freshness-as-data SLA view + read-only operator health page

**Cold-start context:** `source_health` already has `harvest_interval_hours`, `last_ok`, `status`. There is no single view expressing "is this source within SLA?" and no at-a-glance fleet page. The serving DB already feeds `web/`.

**Tasks:**
1. Add migration `00XX_v_source_freshness.sql` (additive `CREATE OR REPLACE VIEW`): per source, `seconds_since_last_ok`, `interval_seconds = harvest_interval_hours*3600`, `state` = fresh (< interval) / warn (< 2×) / stale (≥ 2×), plus `is_tier1`, `consecutive_fails`, `open_alert_count` (join `alert`).
2. Add a read-only endpoint/page in `web/` (or extend the existing ops surface) rendering `v_source_freshness` ordered by worst-first. Reuse existing styling tokens — no orphan style. No write paths.
3. Wire `ops health --json` to emit the same view for scripting.

**Verification:**
```
# apply view on :5434, seed via scripts/seed_ci_fixture.py, query:
psql ":5434" -c "SELECT source_key,state FROM v_source_freshness ORDER BY seconds_since_last_ok DESC LIMIT 10;"
cd web && npm ci && npm run build   # frontend-build job stays green
```
**Exit criteria:** view returns correct `state` classification on seeded `:5434`; `web/` `tsc -b && vite build` green; page renders fleet status read-only. **Rollback:** drop the view (`DROP VIEW IF EXISTS v_source_freshness`) and revert the page — nothing served depends on it.

**Live activation note (all phases):** changes touching served data activate only via the documented gate — dry-run on `:5434` → golden cdp byte-identity → Ferrari → CI green → supervised API/scheduler restart. Never write to `:5433` outside that gate.

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Phase 1 resolve query over-resolves (closes a still-silent source's alert) | HIGH | Condition strictly on `sh.last_ok > alert.created_at`; unit test asserts a still-silent source's alert stays open. Resolve runs before new detection so the same cycle re-fires if still silent. |
| `0054` unapplied on live → lease still 0 rows after Phase 2 | MEDIUM | Phase 2 task 1 explicitly runs `Migrate verify` and applies `0054` (additive, `IF NOT EXISTS`) before validating. |
| Migration drift between `migrations/` and live schema | MEDIUM | CI `bring-up-smoke` already has a `Migrate verify` (no-drift) step; new view migration must pass it. |
| Touching `:5433` by accident | CRITICAL | All experiments on ephemeral `:5434`; DSNs in commands are explicit; activation only via the golden→Ferrari→CI gate. |
| Adding Prometheus/Grafana prematurely (scope creep, infra cost) | MEDIUM | Explicitly deferred behind a documented 100× fleet-growth trigger; current scale (56 sources) is served by Postgres views at EUR0. |
| `as24_facet` allow-list masks a real future gap | LOW | Allow-list requires a one-line documented reason per key; CI parity test forces any new key to be justified, not silently ignored. |

## Success metrics

- **Zombie silence alerts = 0** (sources with `last_ok > created_at` and an open `:silence` alert) — continuously, verified by the Phase 1 resolve query. Baseline: 7.
- **Lease freshness:** `scheduler_lease` row age < TTL (6 min) for every live daemon; `ops health` exit code correct in both fresh and stale states. Baseline: 0 lease rows.
- **Registry drift = 0** enforced by green `test_registry_parity` in CI on every PR. Baseline: 1 unmapped (`as24_facet`).
- **Freshness coverage:** 100% of `source_health` rows classified by `v_source_freshness`; operator page renders worst-first with `frontend-build` green.
- **CI faithfulness preserved:** all 5 jobs (`bring-up-smoke`, `db-tests`, `frontend-build`, `secret-scan`, `unit-tests`) green; new tests added to the appropriate marker (`unit` vs DB-backed) and never to `tests/ci_local_only.txt` unless they genuinely require live census data.
- **Zero regressions to served data:** no served column altered; every change is a new view, query, CLI, test, or read-only page, reversible by `git revert` + `DROP VIEW IF EXISTS`.
