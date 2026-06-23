# E2E Per-Stage Operational Runbook

> The per-sales-point lifecycle, one stage at a time:
> **DISCOVER → SCRAPE → RECIPE → IDENTITY → API → DELTA**.
>
> For every stage: what module/command runs it, its cadence and scheduler, how to
> verify it worked (exact query / curl), how to troubleshoot the common failures
> (breakers, gates, VAM REFUTED, silence watchdog), and the health signals.
>
> Every command, query, threshold, and number below is grounded in the real code
> and the live PostgreSQL backbone. Verified `2026-06-23`. Where a number is a live
> snapshot it is labelled `[live YYYY-MM-DD]`; re-run the query to get the current value.

---

## 0. Conventions, connection, and where things live

**Live PG DSN** (psql is not on PATH — query with a Python + asyncpg heredoc):

```bash
export CARDEEP_DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
```

Run any verification query in this doc with this wrapper (POSIX sh / Git Bash):

```bash
python - <<'PY'
import asyncio, asyncpg, os
DSN = os.environ.get("CARDEEP_DSN","postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
async def main():
    c = await asyncpg.connect(DSN)
    print(await c.fetch("SELECT 1"))   # replace with the query
    await c.close()
asyncio.run(main())
PY
```

The scheduler reads two DSN forms from the env (defaults shown):

| Env var | Form | Default | Used by |
|---|---|---|---|
| `CARDEEP_DB_URL` | SQLAlchemy URL | `postgresql+psycopg2://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep` | APScheduler `SQLAlchemyJobStore` (`scheduler.py:57`) |
| `CARDEEP_DSN` | psycopg2 keyword DSN | `host=127.0.0.1 port=5433 dbname=cardeep user=cardeep password=cardeep_dev_only` | scheduler's own sync queries (`scheduler.py:62`) |
| `CARDEEP_ASYNCPG_DSN` | `postgresql://…` URL | `postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep` | asyncpg cadence jobs (`scheduler.py:68`) |

**Country parametrization (FASE 0).** The census is parametrized by `country_code`
(default `'ES'`). The code prefix is minted in exactly one place —
`mint_code(province_code, digest, country_code='ES')` at `services/api/codes.py:44`
→ `CDP-{country}-{province}-{8×base32}`. Filesystem roots derive from the country in
`pipeline/paths.py` (`recipe_root`/`data_root`/`census_dir`, all default `ES`). The
country segment of a `cdp_code` is parsed back with `country_of_cdp()`
(`pipeline/paths.py:55`). Migration `migrations/0052_country.sql` added
`country_code CHAR(2) DEFAULT 'ES'` + composite `UNIQUE (country_code, code)` to
`geo_province / geo_comarca / geo_municipality / entity`. **To onboard a second
country, see `docs/runbook/05-HARVEST-EXECUTION-PLAN.md` and the switchover doc — the
PK swap to `(country_code, code)`, the geo CHECK relaxation, and country-specific
sources are the deferred work; this runbook is the ES operating manual.**

**Live system snapshot** `[live 2026-06-23]` (re-run the per-stage queries for current values):

| Table | Count | Query |
|---|---|---|
| `entity` total | **431 212** | `SELECT count(*) FROM entity` |
| `entity` active | 419 890 | `… WHERE status='active'` |
| `entity` non-particular | 91 412 | `… WHERE kind<>'particular'` |
| `vehicle` total | 2 312 301 | `SELECT count(*) FROM vehicle` |
| `vehicle` available | 2 207 346 | `… WHERE status='available'` |
| `vehicle` gone | 104 955 | `… WHERE status='gone'` |
| `vehicle_event` | 2 613 139 | `SELECT count(*) FROM vehicle_event` |
| `source_health` rows | 56 | `SELECT count(*) FROM source_health` |
| `verification_verdict` active | 720 (613 TRUSTWORTHY / 64 REFUTED / 43 UNVERIFIED) | `… WHERE superseded_by IS NULL` |
| `alert` open | 53 | `… WHERE resolved_at IS NULL` |

> **Doc-drift note:** the older `SYSTEM-A-Z` said `419k` entities; the live `entity`
> total is **431 212** (active subset is 419 890). Always trust the live query over a
> pinned number — coverage scale changes with every discovery wave.

---

## STAGE 1 — DISCOVER

Mint immutable sales-point identities (`cdp_code`) and grow the census. Discovery is
**incremental/recurrent, not one-shot** — it is the 6th axis of the plan.

### Module / command

- **Per-source one-shot:** `python -m pipeline.discover <source_key>`
  (`pipeline/discover.py`). Runs a `SourceAdapter`, geo-resolves each entity to INE
  province/municipality codes, mints `cdp_code` via `cdp_code(...)`
  (`pipeline/discover.py:91`), upserts `entity` + `entity_source` idempotently
  (`ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()`, `discover.py:100`), and
  closes with a VAM count-quorum gate (`record_count_verdict`, `discover.py:159`).
  Adapters registered in `ADAPTERS` (`discover.py:48`): `dgt_cat`, `osm`, `overture`,
  `borme_cnae`, `axesor_cnae`, `graph_recursive`, `dork_municipal`,
  `collapse_invisible`, `paginas_amarillas`, the OEM dealer locators, the association
  scrapers, and the `*_census` adapters.
- **Continuous orchestrator:** `python -m pipeline.discover_schedule`
  (`pipeline/discover_schedule.py`). A **separate producer** from the harvest
  scheduler — its own advisory lock (`_LOCK_KEY = 0x43415244 + 1`,
  `discover_schedule.py:50`) so it never touches the harvest registry or host lock.

### Cadence / scheduler

`discover_schedule.py` registers 5 vectors in `DISCOVERY_REGISTRY`
(`discover_schedule.py:65`), due-tracked via `source_health` (the same table the
silence watchdog reads):

| Vector / source_key | Cadence | Orthogonal | Auto-run gate |
|---|---|---|---|
| `borme_cnae` | 24h | yes (MSE list) | — |
| `collapse_invisible` | 168h | no (re-collapse) | — |
| `overture` | 720h | yes | — |
| `graph_recursive` | 720h | no | — |
| `dork_municipal` | 2160h | yes | **GATED**: requires `CARDEEP_SEARXNG_URL` (`requires_env`, `discover_schedule.py:83`) |

Commands:

```bash
python -m pipeline.discover_schedule --seed       # register/refresh cadence rows in source_health
python -m pipeline.discover_schedule --dry-run    # show cadences + which vectors are DUE (also default)
python -m pipeline.discover_schedule --once VEC   # run one vector now (bypasses due + the auto-run gate)
python -m pipeline.discover_schedule --tick       # run all DUE vectors once (cron-friendly)
python -m pipeline.discover_schedule --serve      # blocking APScheduler, tick every 60 min (own advisory lock)
```

Tick interval `CARDEEP_DISCOVERY_TICK_MIN` (default 60 min); subprocess wall
`CARDEEP_DISCOVERY_TIMEOUT` (default 21 600 s = 6h). Recipe-first sampling defaults
keep a local tick cheap (`CARDEEP_BORME_DAYS=1`, `CARDEEP_GRAPH_LIMIT=200`); the
national VPS sweep overrides them via env.

### Verify it worked

```bash
# DUE state + gated vectors, read-only:
python -m pipeline.discover_schedule --dry-run
```

```sql
-- discovery cadence rows + last success (live: borme/collapse/graph/overture healthy; dork unknown=never run)
SELECT source_key, status, harvest_interval_hours, last_ok, last_fail, consecutive_fails
FROM source_health
WHERE source_key IN ('borme_cnae','collapse_invisible','overture','graph_recursive','dork_municipal')
ORDER BY source_key;

-- the per-run audit row (discovery writes harvest_run too — discover_schedule.py:137):
SELECT source_key, finished_at, ok, rows, error FROM harvest_run
WHERE source_key IN ('borme_cnae','overture','graph_recursive','collapse_invisible')
ORDER BY finished_at DESC LIMIT 10;

-- newly minted entities today:
SELECT first_discovered_source, count(*) FROM entity
WHERE last_seen > now() - interval '24 hours' GROUP BY 1 ORDER BY 2 DESC;
```

A one-shot `pipeline.discover` prints `new=… in_db=… skipped_no_province=… municipality_resolved=…/…`
and a `VAM verdict: TRUSTWORTHY|UNVERIFIED|REFUTED` line.

### Health signals

- `source_health` row per vector exists and `last_ok` is within its cadence.
- The per-run quorum compares `{db_ingested, fetched, source_declared}` with
  `tolerance=0.0` (`discover.py:159`). `db_ingested` is scoped to this run
  (`seen_at >= run_start`, `discover.py:152`) — **a cumulative count would falsely
  certify** after the first full run; per-run scoping keeps the quorum honest about
  ingestion vs fetch.

### Troubleshoot common failures

- **`skipped_no_province=N` > 0:** an entity could not be geo-resolved to a province,
  so no province-scoped code could be minted (it is skipped honestly,
  `discover.py:90`). Each is traced as `SKIP no_province: name=… province_name=… municipality=…`
  (`discover.py:144`). Fix the adapter's geo fields or add an unambiguous city/postcode.
- **`dork_municipal` never runs (status `unknown`):** **expected** — it is GATED. An
  unbounded scheduled DDG sweep (~40k requests) risks a ban; the daemon refuses to
  auto-run it without `CARDEEP_SEARXNG_URL` (`_gated`, `discover_schedule.py:120`).
  Run it manually with `--once dork_municipal` (operator intent bypasses the gate) or
  set a quota-free SearXNG endpoint.
- **Breaker open:** a discovery vector with `consecutive_fails >= 3` is excluded from
  `_due` (`discover_schedule.py:110`). It fails its own way via `_record` which sets
  `status='down'` at the 3rd consecutive fail (`discover_schedule.py:157`).
- **VAM `REFUTED` at discover:** the three paths disagree beyond tolerance — the
  adapter dropped entities (geo-skip) or the source's declared count is wrong. Read
  the `SKIP` traces, then `pipeline.verify` semantics (Stage 5 below).

---

## STAGE 2 — SCRAPE (harvest inventory)

Drain a sales-point's live inventory into `vehicle` / `platform_listing`, instrumented
end-to-end by S-HEALTH (`record_run` / `is_open` / `auto_repair`).

### Module / command

Two execution shapes:

1. **Wholesale / platform connectors** (`pipeline/platform/*.py`, **47 modules**,
   **44 wired to `record_run` + `is_open`**). Each is launched as
   `python -m pipeline.platform.<module> [args]`. Pattern (grounded in
   `coches_net_facet.py`):
   - `if await is_open(conn, SOURCE_KEY): skip` — breaker guard **before** any fetch
     (`coches_net_facet.py:331`). Graceful degradation: the API keeps serving the last
     snapshot ("no se cae").
   - drain → write recipe → VAM `record_count_verdict` →
     `record_run(conn, SOURCE_KEY, ok=…, rows=…, declared_total=…, captured_distinct=…, platform_ulid=…)`
     (`coches_net_facet.py:445`). The connector — **not the scheduler** — owns its
     `record_run`.
   - on `not run_ok`: `auto_repair(...)` classifies the failure and fires the
     exact-origin alert (`coches_net_facet.py:453`).

2. **Per-dealer E2E orchestrator** (AutoScout24 path):
   `python -m pipeline.harvest_dealer <as24_dealer_slug>` (`pipeline/harvest_dealer.py`).
   Chains SCRAPE → INGEST+delta+VAM → RECIPE for one dealer. Uses **per-dealer
   `fire_alert`** (not `record_run`) so a single bad dealer never trips the whole-source
   breaker / GONE sweep (`harvest_dealer.py:34`). `scale_as24.py` (the per-dealer
   driver) stays **operator-run, intentionally NOT scheduled** (the AS24 ban scar).

### Cadence / scheduler

The durable single-producer scheduler: `python -m pipeline.ops.scheduler`
(`pipeline/ops/scheduler.py`). APScheduler 3.x `BlockingScheduler` +
`SQLAlchemyJobStore` (crash-safe; jobs survive a process death).

- **`heartbeat_tick`** every **15 min** (`TICK_INTERVAL_MINUTES`, `scheduler.py:76`).
  Single-producer, series: runs due connectors **one at a time** (`max_instances=1`,
  `coalesce=True`, `misfire_grace_time=300`, `scheduler.py:847`). Never two subprocesses
  in flight — avoids the AS24 two-governor scar and does not saturate the 16 GB box.
- **DUE selection** (`_due_sources`, `scheduler.py:309`): `source_health` rows where
  `now() - COALESCE(last_ok, last_fail, '1970-01-01') >= harvest_interval_hours * interval '1 hour'`,
  ordered most-overdue first. Rows with `consecutive_fails >= 3` (`BREAKER_TRIP_AT`)
  are skipped with a logged reason (`scheduler.py:342`).
- **Host singleton:** a session-level pg advisory lock `0x43415244` ('CARD') prevents a
  **second** scheduler process from doubling the host's aggregate rate
  (`scheduler.py:826`). It fails fast if another holds it.
- **Cadence tiers** (set per source in `source_health.harvest_interval_hours`,
  seeded by migrations): Tier-1 marketplaces **24h** (`autocasion_wholesale`,
  `coches_com_wholesale`, `coches_net_wholesale`, `milanuncios_wholesale`,
  `motor_es_wholesale`, `wallapop_wholesale` — the 6 `is_tier1` rows), OEM/groups/
  subastas **168h**, own-site `dealerprobe_ownsite` **24h** (`--from-db --limit 500`,
  host-distributed, ban-free), families **720h**.
- **Subprocess wall:** `CARDEEP_SUBPROCESS_TIMEOUT` (default **14 400 s = 4h**,
  `scheduler.py:104`). All children get `PYTHONIOENCODING=utf-8` (the B3.3 cp1252 crash
  fix, `scheduler.py:390`).
- **Crash safety net:** if a connector exits non-zero **without** writing a
  `harvest_run` (timeout SIGKILL / failed launch), `_record_crash_if_unrecorded`
  records the failure itself — but **only** if no new `harvest_run` row appeared this
  cycle vs the pre-launch high-water (`scheduler.py:435`), so a connector that recorded
  its own outcome is never double-counted.

Inspect / dry-run (no subprocess launched, safe anytime):

```bash
python -m pipeline.ops.scheduler --dry-run        # DUE sources + the exact argv each would run + gap report
python -m pipeline.ops.scheduler --check-silence  # read-only silent-source list (no alerts fired)
python -m pipeline.ops.scheduler                  # start the live blocking scheduler
```

### Verify it worked

```sql
-- last harvest per source + freshness:
SELECT source_key, status, consecutive_fails, last_ok, last_fail, is_tier1, harvest_interval_hours
FROM source_health ORDER BY
  CASE status WHEN 'down' THEN 0 WHEN 'degraded' THEN 1 WHEN 'unknown' THEN 2 ELSE 3 END,
  consecutive_fails DESC;

-- the audit trail (the evidence the 138-dealer scar lacked):
SELECT source_key, finished_at, ok, rows, error, http_status FROM harvest_run
ORDER BY finished_at DESC LIMIT 20;

-- last-24h success/fail tally:
SELECT ok, count(*) FROM harvest_run WHERE finished_at > now()-interval '24 hours' GROUP BY ok;
```

Via the API (monitoring):

```bash
curl -s http://127.0.0.1:8090/sources        # source_health, degraded/down first (authed if CARDEEP_API_KEY set)
```

`[live 2026-06-23]` 51 healthy / 4 degraded / 0 down / 1 unknown; 0 sources with
`consecutive_fails >= 3`; all 6 tier-1 present (motor_es degraded).

### Health signals + state machine

`record_run` (`pipeline/ops/health.py:84`) is **the single writer** of
`source_health` + `source_breaker`, under a `FOR UPDATE` row lock (no lost-update on
`consecutive_fails`). Hysteresis (`health.py:48`): 1 fail → `degraded`, 3 consecutive
→ `down`; one clean run resets to `healthy`. Breaker trips OPEN at
`BREAKER_TRIP_AT = 3` with an **exponential cool-down**
(`min(900 * 2^depth, 86400)` s, `health.py:225`). `is_open` returns True while OPEN +
within cooldown; once cooldown elapses it flips OPEN→`half_open` to let exactly one
probe through (`health.py:443`).

### Troubleshoot common failures

- **Breaker OPEN (source skipped):** check `source_breaker.state` / `cooldown_until`.
  ```sql
  SELECT source_key, state, consecutive_fails, opened_at, cooldown_until
  FROM source_breaker WHERE state <> 'closed';
  ```
  Wait for the cooldown (auto half-open probe) or, after fixing the root cause, force
  recovery by letting one good run reset it. **Do not** hammer — the open breaker is the
  AS24-scar protection.
- **VAM `REFUTED` (run marked not-ok):** the connector sets `run_ok=False` when
  `verdict == 'REFUTED'` and records `error="VAM verdict REFUTED"`
  (`coches_net_facet.py:443`). Means the orthogonal paths
  (`db_edges` / `db_join_vehicles` / `harvested_cageable`) disagree beyond tolerance —
  silent ingest loss or a parse drift. Inspect the latest verdict (Stage 5) and the raw
  dump.
- **Coverage gate alerts** (`source_coverage` via `verify_coverage`,
  `pipeline/ops/coverage_verify.py`): floor `_DEFAULT_FLOOR = 0.85`, ceiling
  `_COVERAGE_CEILING = 1.15`.
  - `coverage_pct < 0.85` → REFUTED + `auto_repair(source_key, 'low_coverage')`
    (`coverage_verify.py:304`) → partial drain; re-run the source.
  - `coverage_pct > 1.15` → **UNVERIFIED, not REFUTED** (over-coverage is unmeasurable
    without a full-index probe, not necessarily wrong, `coverage_verify.py:236`). These
    are benign WARNINGs (e.g. `[live]` `coches_com_wholesale coverage ABOVE ceiling …
    9092%` from multi-segment counting); REFUTED-on-over-coverage would wrongly block
    `reconcile_gone`.
- **`auto_repair` action classes** (`classify_failure`, `health.py:340`): 403/blocked/
  captcha → `refingerprint` (or `escalate_tier` for Akamai/DataDome/PerimeterX);
  429/rate-limit/ban → `quarantine`; null/drift/parse → `re_receta`; unknown →
  `escalate_owner`. `quarantine` + `escalate_owner` are fully effective at €0; the
  spend-bearing rungs are scaffolded behind the P10 gate (recorded `succeeded=FALSE`,
  alert fired, marked pending — **never faked as done**, `health.py:419`).
  ```sql
  SELECT source_key, detected_reason, action, succeeded, created_at
  FROM repair_attempt ORDER BY created_at DESC LIMIT 20;
  ```
- **Silent source (`--check-silence`):** see Stage 6 (watchdog).

---

## STAGE 3 — RECIPE

Persist the durable, versioned extraction recipe per sales-point/platform — the asset
that lets Cardeep re-scrape **without** re-storing the raw crude.

### Module / command

`write_recipe(cdp_code, recipe=None)` (`pipeline/recipe.py:43`). Called automatically
inside each connector after a clean drain (e.g. `coches_net_facet.py:414`) and by
`harvest_dealer.py:76`. Recipes are YAML under
`countries/<country>/recipes/<cdp_code>.yaml`; the country is derived from the
`cdp_code` via `country_of_cdp()` → `recipes_flat_dir()` (`recipe.py:69`). For ES, that
is `countries/ES/recipes/`.

Records: `version`, `source`, `engine`, `access`, `enumeration`, `field_map`
(`AS24_RECIPE`, `recipe.py:20` is the structured default).

### Cadence / scheduler

Not independently scheduled — **co-runs with SCRAPE** (Stage 2). A recipe is
(re)written every successful harvest of that dealer/platform. The recipe is the
**committed** asset; the raw harvest dump (`data/<country>/<slug>/raw/harvest.json`,
`harvest_dealer.py:61`) is ephemeral and gitignored.

### Verify it worked

```bash
ls countries/ES/recipes/ | wc -l          # recipe YAMLs on disk  [live 2026-06-23: 60]
cat countries/ES/recipes/CDP-ES-00-3N995HG6.yaml   # inspect one (a recipe that exists on disk)
```

The connector prints `recipe written: <path>` / `[recipe] <relpath>` on success.

### Health signals

- **Round-trip self-check (R2):** `write_recipe` re-parses the YAML it is about to
  persist and raises if it does not round-trip — a serialization defect fails at
  **write** time, not silently at read time (`recipe.py:76`). This fixed the
  hand-rolled-dumper bug where any value containing `': '` produced unparseable YAML
  that corrupted the dealer's only durable asset.
- **Clobber visibility (R3):** overwriting an existing recipe with a **semantically
  different** one logs a WARNING (the silent last-writer-wins clobber, `recipe.py:88`).

### Troubleshoot common failures

- **`recipe must be a non-empty dict`:** the caller passed a bad recipe object
  (`recipe.py:60`) — fix the connector's recipe build.
- **`recipe did not round-trip through YAML`:** a value broke serialization; the write
  is **refused** (no corrupt file). Inspect the offending `field_map` value.
- **`already holds a DIFFERENT recipe — overwriting (possible clobber)`** in the logs:
  two modules write the same `cdp_code` with diverging recipes (the historic coches.net
  `_tier1` clobber). Decide which connector owns the recipe for that code.
- **Missing recipe for a live dealer:** the dealer was discovered but never harvested
  clean. Run its connector / `harvest_dealer <slug>` and confirm a clean (non-REFUTED)
  drain.

---

## STAGE 4 — IDENTITY (cluster + canonical key)

Collapse cross-source duplicate sales-points into one canonical cluster, collapse a
dealer's cross-platform duplicate cars, and keep the audit pre-image (`canonical_key`)
filled.

### Module / command

- **Dealer clustering:** `python -m pipeline.identity.cluster_dealers`
  (`pipeline/identity/cluster_dealers.py`) → feeds `v_dealer_resolved` (the
  transitive, VAM-verified dealer cluster view the API resolves against,
  `services/api/deps.py:79`).
- **Vehicle clustering / cross-source dedup:**
  `python -m pipeline.identity.cluster_vehicles` and
  `python -m pipeline.identity.cross_source_dedup` → feed `v_canonical_vehicle`
  (`vehicle_ulid` → `canonical_vehicle_ulid`).
- **Entity resolution:** `python -m pipeline.identity.resolve_entities`.
- **canonical_key forward-coverage:**
  `python -m pipeline.identity.canonical_key_backfill`
  (`backfill_canonical_keys(conn, apply=True)`).

The hot-path dedup key (`cdp_code`) is **always set at insert** (Stage 1);
`canonical_key` is the AUDIT pre-image (`particular:wallapop:{id}` / `domain:ford.es` /
`name:{norm}|{muni}`, `services/api/codes.py:56`), inserted NULL on new rows and lazily
filled.

### Cadence / scheduler

- **Cluster runs are operator-run** — `cluster_dealers` / `cluster_vehicles` /
  `cross_source_dedup` / `resolve_entities` are **NOT** in
  `pipeline/ops/scheduler.py` (verified: no reference). Re-cluster after a discovery
  wave or a large harvest, on demand.
- **`canonical_key_backfill` IS scheduled:** `canonical_key_backfill_job`
  every **24h** (`CANONICAL_KEY_BACKFILL_CADENCE_HOURS`, `scheduler.py:97`; job
  `scheduler.py:926`). Self-verifying: it writes a key **only** when its recompute
  re-hashes to the row's stored `cdp_code` (a wrong key cannot be written) — €0,
  MVCC-clean (NULL→value only). Logs `canonical_key_backfill: <summary>`.

### Verify it worked

```sql
-- canonical_key coverage (forward-fill target = entity rows still NULL):
SELECT count(*) FILTER (WHERE canonical_key IS NULL)  AS still_null,
       count(*) FILTER (WHERE canonical_key IS NOT NULL) AS filled,
       count(*) AS total
FROM entity;

-- dealer clusters with >1 member (alias collapse working):
SELECT count(*) FROM (
  SELECT resolved_ulid FROM v_dealer_resolved GROUP BY resolved_ulid HAVING count(*) > 1
) t;

-- canonical vehicle collapse (canonical-only available; live ~1.85M of 2.21M available):
SELECT count(*) FROM v_canonical_vehicle vc
JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid AND v.status='available';
```

Via API: `/entities/{cdp}/canonical` returns `canonical_cdp_code`, `is_canonical`,
`members[]`, `n_members` (`services/api/routers/entities.py:30`).

```bash
curl -s http://127.0.0.1:8090/entities/CDP-ES-08-CPH3HKAH/canonical
```

### Health signals

- `v_dealer_resolved` resolves every requested `cdp_code` to a canonical (the API
  `resolve_cluster` falls back to the entity's own ulid for non-clustered entities,
  `deps.py:90`).
- `v_canonical_vehicle` available-canonical count `[live ~1 853 644]` < raw available
  `[2 207 346]` — the gap is the collapsed cross-platform/cross-dealer duplicates.

### Troubleshoot common failures

- **`/entities/{cdp}` reports 0 stock for a live dealer:** a vehicle not yet in a
  cluster run is absent from `v_canonical_vehicle`; the API LEFT-JOINs and
  `COALESCE`s to the vehicle's own ulid so it is still counted (`entities.py:73`). If a
  dealer shows 0, run `cluster_vehicles` or confirm the harvest actually landed rows.
- **A dealer's duplicate cars not collapsing:** run `cross_source_dedup` /
  `cluster_vehicles`; verify the `v_canonical_vehicle` mapping exists for those
  `vehicle_ulid`s.
- **Two physical dealers merged into one (over-clustering) or one split into two
  (under-clustering):** inspect the cluster inputs in `cluster_dealers.py`; identity is
  keyed by `canonical_key` priority `particular > domain(bare host) > CIF >
  name|municipality|address` (`codes.py:56`). A path-bearing OEM portal URL is
  deliberately **not** an identity (distinct branches stay distinct, `codes.py:84`).
- **`canonical_key` stuck NULL:** the backfill only writes on a re-hash match; if a row
  stays NULL its stored `cdp_code` does not re-derive from current fields (data drift) —
  investigate, do not force-write.

---

## STAGE 5 — API (serve) + VAM verification

Serve per-sales-point inventory, identity, stats, alerts, and source health over the
PostgreSQL backbone with a consistent envelope. VAM (`verify.py`) is the verification
spine that gates what is allowed to read as TRUSTWORTHY.

### Module / command

`services/api/main.py` (FastAPI). Run:

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8090
```

Connection pool `min_size=1, max_size=8` (`main.py:86`). Routers:
`ops` (`/health`, `/stats`, `/alerts`, `/sources`), `entities`, `geo`, `vehicles`,
`platforms` (`main.py:125`).

Envelope (every response, `deps.py:38`): `{ok, data, error, meta}`.

Auth (`require_api_key`, `deps.py:29`): if `CARDEEP_API_KEY` is **set**, data
endpoints require header `X-API-Key`; `/health` is always unauthenticated. If unset,
public mode.

Rate limiting (slowapi, in-memory, `services/api/ratelimit.py`): default 120/min,
expensive endpoints 30/min; disable for test runs with
`CARDEEP_API_RATELIMIT_ENABLED=0`. Caching (cachetools TTLCache) on stable reads;
`meta.cache = hit|miss`.

### Cadence / scheduler

Long-running service (always-on). Not scheduled — it is the read surface; harvest/
discover/identity feed it.

### Verify it worked

```bash
# liveness (unauthenticated; runs SELECT 1 — real DB reachability, not just process-up):
curl -s http://127.0.0.1:8090/health
# -> {"ok":true,"data":{"status":"live","db":"ok"},"error":null,"meta":null}   [verified live]

# sealed product counts (AUTHED — coverage scale is a competitive signal):
curl -s -H "X-API-Key: $CARDEEP_API_KEY" http://127.0.0.1:8090/stats
#   dealers (v_dealer_resolved, kind<>'particular'), vehicles_unique_available
#   (canonical-only available), events, provinces, municipalities  (ops.py:74)

# per-dealer inventory (canonical-deduped within cluster; cached 60s; 30/min):
curl -s http://127.0.0.1:8090/entities/CDP-ES-08-CPH3HKAH/inventory?page=1&size=50

# operational monitoring:
curl -s http://127.0.0.1:8090/alerts        # open alerts, critical->warning->info  (ops.py:105)
curl -s http://127.0.0.1:8090/sources       # source_health, sickest first         (ops.py:159)
```

### VAM — the verification spine

`record_count_verdict(...)` (`pipeline/verify.py:53`) persists a
`verification_verdict` row. Quorum: **TRUSTWORTHY** only when ≥2 orthogonal paths
agree **exactly** AND span ≥2 distinct families AND ≥2 origins
(`has_independence`, `verify.py:119`) AND the primary path (what actually landed)
agrees (`primary_agrees`, `verify.py:136`) AND a modal-zero is observation-backed
(`zero_certifiable`, `verify.py:155`). Otherwise:
- values do not disagree but cannot be quorum-certified → **UNVERIFIED** (never
  REFUTED) — e.g. soft drift within tolerance, or same-family clustering.
- values disagree beyond tolerance → **REFUTED**.

Path families (`_path_family`, `verify.py:31`): `db`, `http`, `source`, `registral`,
`other` (unknown collapses to `other` so unproven orthogonality never grants quorum).

The newest verdict for a `(subject_type, subject_key, claim)` supersedes prior actives
(`superseded_by`, `verify.py:205`) — read-side filters use `superseded_by IS NULL`.

```sql
-- active verdict mix (live: 720 active = 613 TRUSTWORTHY / 64 REFUTED / 43 UNVERIFIED):
SELECT verdict, count(*) FROM verification_verdict WHERE superseded_by IS NULL GROUP BY verdict;

-- current REFUTED verdicts (what to investigate first):
SELECT subject_type, subject_key, claim, divergence, evidence, created_at
FROM verification_verdict WHERE superseded_by IS NULL AND verdict='REFUTED'
ORDER BY created_at DESC;
```

### Health signals

- `/health` → `status:"live", db:"ok"`. If `db:"down"`, the pool cannot reach PG.
- `/sources` mirrors the harvest scheduler's health; `/alerts` mirrors the live
  fault state.

### Troubleshoot common failures

- **401 Invalid or missing API key:** `CARDEEP_API_KEY` is set server-side; send
  `X-API-Key`. `/health` never needs it.
- **429 (rate limit):** the envelope still wraps it; back off or set
  `CARDEEP_API_RATELIMIT_ENABLED=0` for tests.
- **`entity … not found`:** `resolve_cluster` returned None — the `cdp_code` has no
  `entity` row. Confirm Stage 1 minted it.
- **Stale inventory after a harvest:** `/entities/{cdp}/inventory` is cached
  `CACHE_TTL_SECONDS`; `/delta`, `/alerts`, `/sources`, `/vehicles/*` are **not**
  cached (`entities.py:10`, `ops.py:6`). Wait out the TTL or read `/delta`.
- **`db:"down"`:** check PG on `:5433`, the pool, and `CARDEEP_DSN`.

---

## STAGE 6 — DELTA (lifecycle: NEW / PRICE / KM / PHOTO / GONE)

Emit and serve the per-vehicle change stream — the live pulse of each sales-point's
inventory.

### Module / command

- **Diff + GONE machinery:** `pipeline/delta.py`. `diff_vehicle(old, new)` is a pure
  function returning `PRICE_CHANGE / KM_CHANGE / PHOTO_CHANGE` event dicts (no false
  positives). `reconcile_gone(conn, source_key, run_started_at, *, min_coverage)`
  retires available vehicles **not re-seen** in the latest run — source-scoped,
  idempotent, MVCC-safe.
- **Wiring:** `reconcile_gone` is called by `record_run` **after** coverage is recorded
  (`pipeline/ops/health.py:280`), gated by `_GONE_MIN_COVERAGE = 0.9` (`health.py:40`)
  — GONE only fires when the harvest captured ~all the inventory **and** the verdict is
  not REFUTED, so a partial/failed drain never retires the whole inventory. Boundary
  for "not re-seen" = the connector's explicit harvest-start, else the prior successful
  `last_ok` (`health.py:279`); on the first run (`prior_last_ok` NULL) GONE is skipped.
- **Photo delta:** `pipeline/delta_photo.py`; **guard:** `pipeline/delta_guard.py`.

### Cadence / scheduler

Co-runs with SCRAPE (Stage 2) — every harvest run emits its delta via `record_run`.
No separate scheduler entry; cadence == the source's `harvest_interval_hours`.

### Verify it worked

```sql
-- event stream is appending (live total 2,613,139):
SELECT event_type, count(*) FROM vehicle_event GROUP BY event_type ORDER BY 2 DESC;

-- recent events:
SELECT event_type, count(*) FROM vehicle_event
WHERE observed_at > now()-interval '24 hours' GROUP BY event_type ORDER BY 2 DESC;

-- GONE retirements (live: 104,955 gone of 2,312,301 total):
SELECT status, count(*) FROM vehicle GROUP BY status;
```

Via API (cluster-aware — events from ALL cluster members, `entities.py:170`):

```bash
curl -s "http://127.0.0.1:8090/entities/CDP-ES-08-CPH3HKAH/delta?since=2026-06-01T00:00:00Z&page=1&size=50"
curl -s "http://127.0.0.1:8090/vehicles/<ulid>/history"   # full per-vehicle timeline, oldest first
```

### Health signals

- `vehicle_event` total monotonically increases across harvests.
- `vehicle.status='gone'` grows only after coverage-complete runs.
- `record_run` logs `reconcile_gone[<source>]: <reason>` every run (`health.py:284`) —
  the reason states whether GONE fired or was gated.

### Troubleshoot common failures

- **No GONE events despite stock disappearing:** the source's latest coverage is
  `< 0.9` or REFUTED (gate, `health.py:283`), or the connector omits `run_started_at`
  **and** has no prior `last_ok` (first run). Read `reconcile_gone[…]` in the scheduler
  log; raise coverage / fix the harvest before expecting bajas.
- **Mass false GONE:** would require a coverage-complete run that actually missed
  inventory — the `min_coverage 0.9` gate + the >50% gone-fraction cap in
  `reconcile_gone` are the protection. If you see it, the coverage metric is lying;
  investigate `source_coverage` before trusting the sweep.
- **Delta endpoint empty for a known dealer:** confirm `resolve_cluster` returns the
  cluster and that events exist for `entity_ulid = ANY(member_ulids)` — the query is
  cluster-scoped (`entities.py:206`).
- **Inquisition re-verification backlog (verdict TTL):** verdicts expire
  (`verify_ttl.ttl_for`); the cadence job re-queues them (see below).

---

## Cross-stage: scheduled background jobs (the auto-pilot)

All registered in `_start_scheduler()` (`pipeline/ops/scheduler.py`), one process,
single-producer, host advisory lock `0x43415244`:

| Job | Cadence | What it does | Verify |
|---|---|---|---|
| `heartbeat_tick` | 15 min | run DUE harvest connectors in series (Stage 2) | `--dry-run`; `harvest_run` |
| `silence_watchdog` | 1h | alert sources silent > 2× their interval | `--check-silence`; `/alerts` |
| `inquisition_cadence` | 6h | queue re-verification for verdicts whose TTL lapsed (€0; opens `stale_verdict` gestion_items) | `gestion_item` |
| `inquisition_prosecute` | 6h (+30 min stagger) | adjudicate PENDING claims; at €0 → honest `REFUTED:NO_INDEPENDENT_PATH` → `ESCALATE_OWNER`. New-claim emission opt-in via `CARDEEP_INQUISITION_EMIT=1` | `inquisition_*` tables |
| `gestionador_detect` | 24h | cohort price-anomaly detector, **QUARANTINE-only + reversible** (hides cohort-implausible cars from `servable_vehicle`, never NULLs `vehicle.price`) | `gestion_item` |
| `canonical_key_backfill` | 24h | fill `entity.canonical_key` for new rows, self-verifying (Stage 4) | NULL-count query above |

### Silence watchdog (Stage-2/6 blind-spot cover)

`pipeline/ops/silence_watchdog.py`. A source is **silent** when
`now() - COALESCE(last_ok, last_fail, '1970-01-01') > 2 × harvest_interval_hours`
(`SILENCE_MULTIPLIER = 2`, `silence_watchdog.py:46`). It catches the case S-HEALTH is
blind to: a connector that **never runs** never calls `record_run`, so the breaker
never trips. Tier-1 silence → `critical`, others → `warning`. Dedup-aware: one open
alert per `source_key:silence` origin (UPDATE existing, INSERT new,
`silence_watchdog.py:113`).

```bash
python -m pipeline.ops.scheduler --check-silence    # read-only, fires NO alerts
```

```sql
SELECT origin, severity, message FROM alert
WHERE resolved_at IS NULL AND origin LIKE '%:silence' ORDER BY severity, created_at DESC;
```

`[live 2026-06-23]` examples: `motor_es_wholesale:silence` (critical, silent 177h vs
24h), `coches_com_wholesale:silence` (critical, 168h), `borme_cnae:silence` (warning,
58.8h vs 24h). A silence alert auto-resolves when the source records a good run
(`resolve_alerts` on the matching origin, `health.py:172`). To clear a stale silence:
fix the source and let one clean harvest run.

### Gestionador (quarantine) state

```sql
-- open gestion items (live: 38 open):
SELECT state, count(*) FROM gestion_item WHERE state NOT IN ('closed','resolved') GROUP BY state;
```

**`gestionador_detect` ships behind a one-run dry-run review**
(`docs/architecture/feature-designs/price_trap.md §Risks`,
`scheduler.py:628`): review the flagged set with `python -m pipeline.gestionador.run`
before relying on it in prod. It is inert until the scheduler is deployed.

---

## Gates that stop or pause work (and how to clear them)

| Gate | Where | Trigger | Effect | Clear / override |
|---|---|---|---|---|
| Circuit breaker | `health.py:215` / `scheduler.py:342` | `consecutive_fails >= 3` | source skipped from DUE; `is_open` → True | one clean run resets; or wait the exponential cooldown (auto half-open probe) |
| Coverage floor | `coverage_verify.py:304` | `coverage_pct < 0.85` | REFUTED + `auto_repair('low_coverage')` | re-run for a complete drain |
| Coverage ceiling | `coverage_verify.py:236` | `coverage_pct > 1.15` | **UNVERIFIED** (benign), warning alert | benign; over-counting metric, not a data error |
| VAM REFUTED | `verify.py:166` | paths disagree > tolerance | run not-ok; blocks GONE | fix ingest/parse; re-harvest |
| GONE coverage gate | `health.py:283` | latest coverage < 0.9 or REFUTED | no retirements this run | raise coverage; re-harvest |
| Discovery auto-run gate | `discover_schedule.py:120` | required env absent (`dork_municipal`→`CARDEEP_SEARXNG_URL`) | vector skipped (not run, not failed) | set the env, or `--once <vector>` (operator intent) |
| Host singleton lock | `scheduler.py:826` / `discover_schedule.py:240` | a second scheduler process | refuses to start | stop the other producer |
| P10 spend gate | `health.py:419` | repair action needs spend (`refingerprint`/`escalate_tier`/`re_receta`) | recorded `succeeded=FALSE`, pending, alert fired | authorize spend (out of scope here); honest wall, never faked |
| API auth | `deps.py:29` | `CARDEEP_API_KEY` set | data endpoints need `X-API-Key` | send the header |

---

## Rollback / safety notes

- **Discovery / harvest are idempotent.** `entity` upsert is
  `ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now()` (`discover.py:100`);
  re-running never double-mints. `reconcile_gone` is idempotent (a second call with the
  same boundary is a no-op).
- **Recipes are versioned files** — `git checkout countries/ES/recipes/<cdp>.yaml` to
  revert; the round-trip self-check guarantees no corrupt write lands.
- **Gestionador quarantine is fully reversible** — it opens a hiding `gestion_item`,
  never mutates `vehicle.price`. Close the item to re-show the car.
- **Stopping the scheduler is safe** — APScheduler `SQLAlchemyJobStore` persists jobs;
  on restart `coalesce=True` fires one catch-up tick (no storm). The advisory lock
  auto-releases when the process exits.
- **Never** force-reset a tripped breaker by hammering — the open breaker is the AS24
  138-dealer-scar protection. Fix the root cause; one clean run closes it.
- **Re-clustering (Stage 4) is the one heavyweight manual op** — run it off-peak; it
  rebuilds `v_dealer_resolved` / `v_canonical_vehicle` the API resolves against.
