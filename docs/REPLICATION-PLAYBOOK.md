# CARDEEP — Replication Playbook (A → Z master manual)

> **What this is.** The operational A→Z manual to (PART A) run the Spain (`ES`)
> census end-to-end exactly as it runs today, and (PART B) stand up **country #2**
> at 100% using the FASE-0 `country_code` mechanism that just landed on `main`
> (commit `8866720`, "feat(replication): FASE 0 — country-parametrize cdp/paths +
> additive country_code migration").
>
> **Grounding discipline.** Every count, path, and command below was read from the
> real code or proven against the **live PG** (`postgres://cardeep:…@localhost:5433/
> cardeep`) on **2026-06-23**. Each load-bearing claim is `[VERIFIED]` (read/queried
> this session) or `[ASSUMED]` (forward design — no second country has run yet).
> File citations are `path:line`. **This doc supersedes the stale figures** in
> `docs/architecture/REPLICATION-GUIDE.md` (which still says "419,563 entities, no
> `country_code` column" — both pre-FASE-0 and now wrong; see the drift note below).
>
> **Live ground truth (queried 2026-06-23 against :5433) `[VERIFIED]`:**
>
> | Metric | Live value | Query |
> |---|---|---|
> | `entity` total | **431,212** | `select count(*) from entity` |
> | `entity` with `country_code='ES'` | **431,212** (100%) | `… where country_code='ES'` |
> | `entity` with `cdp_code LIKE 'CDP-ES-%'` | **431,212** (100%) | `… where cdp_code like 'CDP-ES-%'` |
> | `entity` non-`ES` country | **0** | `… where country_code<>'ES'` |
> | non-`particular` entities | **91,412** | `… where kind <> 'particular'` |
> | `geo_province` | **52** (all `ES`) | `select count(*) from geo_province` |
> | `geo_comarca` | **323** | `select count(*) from geo_comarca` |
> | `geo_municipality` | **8,132** | `select count(*) from geo_municipality` |
> | `vehicle` | **2,312,292** | `select count(*) from vehicle` |
> | `vehicle_event` | **2,613,131** | `select count(*) from vehicle_event` |
> | `servable_vehicle` (view) | **2,207,293** | `select count(*) from servable_vehicle` |
> | `servable_entity` (view) | **431,212** | `select count(*) from servable_entity` |
> | `source_health` rows | **56** | `select count(*) from source_health` |
> | entities seen in last 24h (cosecha activa) | **30,263** | `… where last_seen >= now()-interval '24 hours'` |
> | max `last_seen` | **2026-06-23 01:28Z** | `select max(last_seen) from entity` |
>
> **Drift note `[VERIFIED]`.** `REPLICATION-GUIDE.md:18` claims 419,563 entities and
> "no `country_code` column anywhere". Both are false today: the live entity count is
> **431,212** and `country_code` exists on `entity/geo_province/geo_comarca/
> geo_municipality` (migration `0052_country`, applied `2026-06-23 01:25:04Z`,
> ledger row `version='0052'`). The `0052_country.sql:21` header itself says 431,211
> (off by 1 — one entity arrived between writing the migration and now). When PART B
> figures and the GUIDE disagree, **this playbook + a live query win.**

---

# PART A — How Spain is done, end-to-end

The system is a five-stage lifecycle: **DISCOVER → SCRAPE → RECIPE → API → DELTA**,
wrapped by two daemons (discovery scheduler, harvest scheduler) and certified by a
seal/MSE. Each stage below lists its real module, the exact command to run it, and a
live verification query.

```
        ┌─ pipeline.discover_schedule (V2–V6, own advisory lock 0x43415245) ─┐
DISCOVER│  vector → SourceAdapter → DiscoveredEntity → cdp_code mint → entity│
        └───────────────────────────────────────────────────────────────────┘
        ┌─ pipeline.ops.scheduler (heartbeat 15min, advisory lock 0x43415244) ┐
SCRAPE  │  source_health DUE → connector subprocess → vehicle rows + events  │
        └───────────────────────────────────────────────────────────────────┘
RECIPE  │  pipeline.recipe_harness  EXTRACT(k≈3-5)→PERSIST→VERIFY(VAM)→DELETE │
IDENTITY│  cdp_code mint (B1) → cross_source_dedup → cluster (super-canonical)│
API     │  services.api.main  FastAPI envelope: /entities /vehicles /geo /ops│
DELTA   │  /entities/{cdp}/delta?since=  ← vehicle_event (NEW/PRICE/GONE)     │
SEAL    │  v_province_seal (venta) + v_exhaustiveness_seal (MSE capture-recap)│
```

## A.0 — Environment + DB bring-up `[VERIFIED]`

The DSN used everywhere defaults to `postgres://cardeep:cardeep_dev_only@localhost:
5433/cardeep` (`scripts/migrate.py:24`, `pipeline/discover.py:46`). `psql` is **not**
on PATH on this host — query via a Python + asyncpg heredoc (every verification
query in this doc uses that form).

```bash
cd /c/Users/elias/projects/cardeep
docker compose up -d                 # brings up cardeep-pg on :5433 (docker-compose.yml)
python -m scripts.migrate up         # apply all pending migrations (idempotent)
python -m scripts.migrate status     # ledger; last applied today = 0052_country
python -m scripts.migrate verify     # CI drift gate: file sha256 vs ledger (exit 1 on drift)
```

`scripts/migrate.py:104-128` applies each numbered `migrations/NNNN_*.sql` inside one
transaction, records `(version, filename, sha256)` in `schema_migrations`, strips the
trailing `-- Rollback:` block via `strip_rollback()` (`migrate.py:47-65`), and
`$$`-aware splits statements (`split_statements()`, `migrate.py:68-101`). **Verify
the schema head:**

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print(await c.fetch("select version,filename,applied_at from schema_migrations order by version desc limit 3"))
    await c.close()
asyncio.run(m())
PY
# expect 0052_country / 0051_dealerprobe_cadence / 0050_precision_gate
```

## A.1 — DISCOVER (FASE 1): the 6 discovery vectors + the discovery daemon

**Module:** `pipeline/discover.py` (one-shot per vector) and
`pipeline/discover_schedule.py` (the recurrent daemon — "the 6th axis of the plan",
`discover_schedule.py:1`).

### The vectors `[VERIFIED]`

`pipeline/discover.py:48-74` registers **25 source adapters** in `ADAPTERS`. They
realize the discovery vectors of the plan:

- **V1 — registral / authoritative baseline:** `dgt_cat` (DGT CAT census),
  `borme_cnae` (BORME registral altas/bajas filtered by CNAE),
  `axesor_cnae`, the associations (`aedra`, `acevas`, `aecs`),
  `paginas_amarillas`. The DGT/registral list is the V1 backbone.
- **V2 — geo POI grid:** `osm`, `overture` (Overture Maps monthly release).
- **V3 — dork / web-grep:** `dork_municipal` (per-municipality search-engine sweep).
- **V4 — OEM locators:** `oem_kia/mg/byd/skoda/dacia/hyundai/mercedes/seat`.
- **V5 — marketplace seller-census:** `autocasion_census`, `motor_es_census`,
  `ocasionplus_census`, `flexicar_census`, `autoscout24_census` (seller as a
  first-class entity, not a by-product of inventory).
- **V6 — graph / collapse:** `graph_recursive` (re-walk corporate graphs),
  `collapse_invisible` (re-collapse dealers that hide behind aggregator pages).

Each adapter implements the **country-agnostic `SourceAdapter` contract**
(`pipeline/sources/base.py:30-42`): `fetch() -> list[DiscoveredEntity]` and
`declared_count() -> int | None` (the source's own asserted total, for the VAM gate).
A `DiscoveredEntity` carries raw `province_name`/`municipality_name` (resolved to INE
codes at ingest), never pre-resolved codes (`base.py:8-26`).

### What `discover.py` does per entity `[VERIFIED discover.py:77-114]`

1. **Geo-resolve:** `GeoResolver.province_code(name)` → `municipality_code(prov,name)`;
   fallbacks: unambiguous global city name, then lat/lon → nearest labeled province
   (`discover.py:81-90`). **No province ⇒ skip honestly** (cannot mint a
   province-scoped code), printed as `SKIP no_province:` (`discover.py:88-90,144-146`).
2. **Mint the immutable `cdp_code` (B1 identity):** `cdp_code(province_code=prov,
   domain=…, cif=…, name=…, municipality_code=muni, address=…)` (`discover.py:91-93`).
3. **Idempotent upsert:** `INSERT … ON CONFLICT (cdp_code) DO UPDATE SET last_seen=
   now() RETURNING entity_ulid, (xmax=0) AS inserted` (`discover.py:95-104`) — so
   re-discovering the same entity through a different source updates `last_seen`, never
   double-inserts.
4. **Provenance:** upsert `entity_source (entity_ulid, source_key, source_ref)`
   (`discover.py:109-113`).
5. **VAM count quorum gate:** `record_count_verdict(... paths={db_ingested, fetched,
   source_declared}, tolerance=0.0)` (`discover.py:159-164`) — the run closes
   TRUSTWORTHY only when `declared == fetched == in_db` (the in_db count is scoped to
   THIS run via `seen_at >= run_start`, `discover.py:152-154`, so a later geo-skip
   cannot emit a false TRUSTWORTHY).

### Commands `[VERIFIED]`

```bash
python -m pipeline.discover dgt_cat            # V1 registral baseline, one-shot
python -m pipeline.discover overture           # V2 geo POI
python -m pipeline.discover borme_cnae         # V1 registral delta
# daemon (the recurrent 6th axis):
python -m pipeline.discover_schedule --dry-run # show cadences + which vectors are DUE
python -m pipeline.discover_schedule --seed    # register cadence rows in source_health
python -m pipeline.discover_schedule --tick    # run all DUE vectors once (cron-friendly)
python -m pipeline.discover_schedule --once overture   # force one vector (bypasses DUE + gate)
python -m pipeline.discover_schedule --serve   # blocking APScheduler loop, own advisory lock
```

### The discovery daemon internals `[VERIFIED discover_schedule.py]`

- **5 registered vectors** in `DISCOVERY_REGISTRY` (`discover_schedule.py:65-84`) with
  per-vector cadence: `borme_cnae` 24h, `collapse_invisible` 168h, `overture` 720h,
  `graph_recursive` 720h, `dork_municipal` 2160h (`discover_schedule.py:10-16`).
- **Due-tracking reuses `source_health`** via a €0 upsert — NOT `record_run` (whose
  success path triggers harvest-only side effects meaningless for a discovery source
  that owns no vehicles, `discover_schedule.py:16-21,133-160`).
- **Separate advisory lock** `0x43415244 + 1` (`discover_schedule.py:50`) so it never
  fights the harvest scheduler's singleton lock.
- **Circuit breaker:** a vector with `consecutive_fails >= 3` is skipped
  (`discover_schedule.py:49,110`).
- **AUTO-run gate:** `dork_municipal` requires `CARDEEP_SEARXNG_URL`
  (`requires_env`, `discover_schedule.py:77-83`); without it the daemon GATES it
  (an unbounded national DDG sweep ~40k requests risks a ban). `--once` bypasses the
  gate (operator intent, `discover_schedule.py:120-130,194-198`).

**Verify discovery health:**

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print(await c.fetch("""select source_key,status,last_ok,consecutive_fails
        from source_health where source_key in
        ('borme_cnae','overture','graph_recursive','collapse_invisible','dork_municipal')
        order by source_key"""))
    await c.close()
asyncio.run(m())
PY
```

## A.2 — SCRAPE (FASE 2): the harvest scheduler + connectors

**Module:** `pipeline/ops/scheduler.py` — a **durable, single-producer, in-series**
APScheduler `BlockingScheduler` with a `SQLAlchemyJobStore` persisted to cardeep-pg
(`scheduler.py:1-25,815-857`). Crash-safe: the job survives process death and resumes.

### Why single-producer `[VERIFIED scheduler.py:6-13,820-837]`

One `heartbeat_tick` fires every **15 min** (`TICK_INTERVAL_MINUTES=15`,
`scheduler.py:76`) and runs due connectors **one at a time** — never more than one
subprocess in flight. A **session-level pg advisory lock** `0x43415244` (ASCII
`'CARD'`) prevents a *second* scheduler process on the host (the "AS24 scar": two
governors on one host once 4×-hammered and lost 138 dealers, `scheduler.py:820-826`).

### Source selection (DUE) `[VERIFIED scheduler.py:309-349]`

```sql
SELECT source_key, harvest_interval_hours, last_ok, last_fail, consecutive_fails
FROM source_health
WHERE now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
      >= harvest_interval_hours * interval '1 hour'
ORDER BY now() - COALESCE(last_ok, last_fail, '1970-01-01') DESC   -- most overdue first
```
Sources with `consecutive_fails >= 3` (`BREAKER_TRIP_AT`, `scheduler.py:100,342-347`)
are skipped. Each DUE source maps to a `SourceEntry(source_key, module, extra_args)`
in `REGISTRY` (`scheduler.py:131-295`) and is launched as
`python -m <module> [args]` with `PYTHONIOENCODING=utf-8` (the B3.3 Windows-cp1252
fix, `scheduler.py:390`). **The connector writes its own `record_run`; the scheduler
does NOT** — except the crash safety-net `_record_crash_if_unrecorded`
(`scheduler.py:435-477`), which records a failure only when no new `harvest_run` row
appeared this cycle (idempotent vs the pre-launch high-water id).

### Tiers `[VERIFIED scheduler.py:137-289]`

- **Tier-1 (24h):** `autocasion_wholesale`, `coches_com_wholesale`,
  `coches_net_wholesale`, `coches_net_segments`, `milanuncios_wholesale`,
  `motor_es_wholesale`, `wallapop_wholesale` — each runs the **canonical complete
  harvester** (the source_key equals the `*_SOURCE_KEY` the connector writes, so
  health/breaker/`harvest_run` continuity holds).
- **OEM / groups / subastas (168h):** `as24_wholesale` (ban-safe 168h cadence, the
  AS24 record_run writer — NOT the per-dealer `scale_as24.py`), the
  `group_rentacar_vo_*` (6), `group_vo_chains_*` (4), `oem_*` networks, etc.
- **Own-site €0 drain:** `dealerprobe_ownsite` with `--from-db --limit 500`
  (`scheduler.py:269-271`) — host-distributed, ban-free, drains the dealers-with-website
  backlog idempotently.
- **Families (720h):** `family_cms_wp`, `family_dealerk_wp`, `family_generic_custom`,
  `family_unreachable`, etc.

### Co-resident cadence jobs on the same scheduler `[VERIFIED scheduler.py:859-936]`

- `silence_watchdog` (hourly): one dedup-aware alert per source silent >2× its
  interval (`scheduler.py:527-549,862-872`).
- `inquisition_cadence` (6h) + `inquisition_prosecute` (6h, +30min stagger):
  re-verify expired verdicts and adjudicate PENDING claims (`scheduler.py:874-906`).
- `gestionador_detect` (24h): QUARANTINE-only cohort price-anomaly detector
  (`scheduler.py:908-921`).
- `canonical_key_backfill` (24h): self-verifying fill of `entity.canonical_key`
  (the audit pre-image of `cdp_code`) for new rows (`scheduler.py:923-936`).

### Commands `[VERIFIED]`

```bash
python -m pipeline.ops.scheduler --dry-run        # which sources are DUE + the exact argv, no run
python -m pipeline.ops.scheduler --check-silence  # read-only: sources silent > 2× interval
python -m pipeline.ops.scheduler                  # start the live scheduler (blocking, acquires lock)
# run a single connector by hand (what the scheduler would launch):
python -m pipeline.platform.coches_net_facet
python -m pipeline.platform.dealerprobe_wholesale --from-db --limit 500
```

**Verify the harvest pulse:**

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("recent harvest_run:", await c.fetch(
      "select source_key,ok,rows,finished_at from harvest_run order by finished_at desc limit 8"))
    await c.close()
asyncio.run(m())
PY
```

## A.3 — RECIPE (FASE 3): the recipe-first harness

**Module:** `pipeline/recipe_harness.py` (the canonical cycle) +
`pipeline/recipe.py` (`write_recipe`) + `pipeline/recipe_schema.py` (the `Recipe`
dataclass).

The harness inverts the post-hoc order into the mandated cycle
(`recipe_harness.py:5-27`):

```
EXTRACT SAMPLE (k≈3-5) → PERSIST RECIPE → VERIFY (VAM) → DELETE SAMPLE
                              ^ if VERIFY refutes → mark FAILED with reason ^
```

- **recipe-first** — the recipe (config YAML) is the durable asset, so a dealer can
  be re-scraped without keeping raw crude.
- **sample-verify-delete** — only `k` cars are pulled; the raw sample is wiped at the
  end (never fills disk, `recipe_harness.py:10-13`).
- **VAM** — verification reuses `pipeline.verify.record_count_verdict`, never a
  hand-rolled check (`recipe_harness.py:14-15`).
- **no silent failure** — a recipe is `VERIFIED` or `FAILED` with a reason
  (`recipe_schema.STATUS_VERIFIED`/`STATUS_FAILED`).

**Recipe persistence is now country-parametrized `[VERIFIED recipe.py:15,43-69]`:**
`write_recipe(cdp_code)` derives the country from the code and writes to
`recipes_flat_dir(country_of_cdp(cdp_code), root=ROOT)` →
`countries/<country>/recipes/<cdp_code>.yaml`. For every ES code
`country_of_cdp` returns `'ES'`, so the path is byte-identical to the historical
`countries/ES/recipes/` (`recipe.py:66`). Raw crude likewise lands in
`data_root("ES", root=ROOT)/slug/raw` (`harvest_dealer.py:21,59-61`).

> **Honest residual `[VERIFIED plans/P04.md:11]`:** two recipe systems coexist —
> the v2/v3 `Recipe` schema (executable field-map, the harness) and the legacy
> `write_recipe()` v1 dict used by the production connector fleet. Most of the
> on-disk corpus is still `version: 1` legacy. The harness is the target spine; the
> connectors are the current reality. Treat the field-map-driven replay as
> partially-landed, not universal.

## A.4 — IDENTITY / DEDUP: B1 → super-canonical chain

**Modules:** `services/api/codes.py` (B1 mint), `pipeline/identity/*`
(`cross_source_dedup.py`, `cluster_dealers.py`, `resolve_entities.py`,
`canonical_key_backfill.py`).

- **B1 — the immutable mint (`services/api/codes.py`).** `canonical_key()`
  (`codes.py:56-97`) returns the dedup pre-image by priority:
  `particular:{platform}:{sellerId}` > `domain:{host}` (bare host only — a
  path-bearing OEM portal URL is NOT an identity, `codes.py:84-87`) > `cif:{CIF}` >
  `name:{norm}|{muni}[|addr]` > `name:{norm}|p{prov}[|addr]`. `cdp_code` =
  `mint_code(province_code, sha256(key), country_code)` =
  `CDP-{country}-{province}-{8×Crockford-base32}` (`codes.py:44-53`). Same identity
  through a different source → same code → the `ON CONFLICT (cdp_code)` upsert dedups
  at write time.
- **Super-canonical cluster.** Beyond the B1 write-time dedup, `pipeline/identity/
  cluster_dealers.py` + `cross_source_dedup.py` group multiple `cdp_code` entities
  that are the same physical dealer into a resolved cluster. The API resolves a
  requested `cdp_code` to its **whole cluster** (`v_dealer_resolved`,
  `resolve_cluster`) so served counts and `/delta` cover all member ULIDs (see A.6).
- **`canonical_key` forward-coverage.** The mint's pre-image is stored on
  `entity.canonical_key` for audit; new rows insert it NULL and the daily
  `canonical_key_backfill` job fills it self-verifyingly (writes only when the
  recompute re-hashes to the stored `cdp_code`, `scheduler.py:654-683`).

**Why the seal numerator must dedup `[VERIFIED 0042_province_seal_view.sql:9-13]`:**
counting `entity_ulid` directly over-counts ~2× (164.9% national vs the correct
79.4%); the seal numerator uses `COUNT(DISTINCT COALESCE(vdr.resolved_ulid,
e.entity_ulid))`.

## A.5 — API: the FastAPI envelope

**Module:** `services/api/main.py` + `services/api/routers/{entities,vehicles,geo,
platforms,ops}.py` `[VERIFIED]`. Consistent envelope (`ok`/`err`, pagination,
api-key + rate-limit). Key endpoints:

```
GET /entities/{cdp_code}                  # entity + resolved cluster
GET /entities/{cdp_code}/inventory        # available vehicles for the cluster
GET /entities/{cdp_code}/delta?since=…    # vehicle events (see A.6)
GET /vehicles/{id}/history                # full NEW→PRICE_CHANGE→GONE history
GET /geo …                                # province → municipality hierarchy
GET /ops …                               # health / seal surfaces
```

Run it:

```bash
uvicorn services.api.main:app --port 8000   # see services/api/main.py for the app
```

## A.6 — DELTA: NEW / PRICE / GONE lifecycle

**Module:** `services/api/routers/entities.py:170-237` (`/entities/{cdp}/delta`) +
`services/api/routers/vehicles.py:33` (full history).

- `/delta` is **cluster-aware**: it queries `vehicle_event WHERE entity_ulid =
  ANY(cluster.member_ulids)` (GAP-4 fix, `entities.py:182-184,203-230`), so events
  from every cluster member are merged, ordered `observed_at DESC`.
- `?since=<ISO-8601>` filters to events after a timestamp (`entities.py:189-216`);
  invalid format → HTTP 400 with a clear message (`entities.py:193-197`). Paginated
  `page`/`size` (1-200). Not cached (event stream is time-sensitive,
  `entities.py:9-10`).
- The event log (`vehicle_event`, **2,613,131 rows** `[VERIFIED]`) is the append-only
  source of NEW / PRICE_CHANGE / GONE deltas produced by `pipeline/ingest.py` +
  `pipeline/delta*.py` on each harvest.

**Verify delta is live:**

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("events by type (24h):", await c.fetch(
      "select event_type,count(*) n from vehicle_event where observed_at>=now()-interval '24 hours' group by event_type order by n desc"))
    await c.close()
asyncio.run(m())
PY
```

## A.7 — SEAL + MSE: the two certifications

Two complementary seals, both **live views** (no stale snapshots):

### Venta seal — `v_province_seal` `[VERIFIED 0042_province_seal_view.sql + live query]`

Per-province coverage = canonical served dealers (numerator) ÷ DIRCE CNAE-451
registral ceiling (denominator, loaded by `scripts/load_denominator_provincia.py`
into `denominator_estimate`). Verdict: **SELLADO ≥85%, PARCIAL 50–85%, GAP <50%**.
Numerator = `COUNT(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid))` over
`compraventa + concesionario_oficial` with ≥1 `available` vehicle.

**Live (2026-06-23) `[VERIFIED]`:** national **venta** coverage = **80.5%**
(numerator 18,298 ÷ denominator 22,720). The view holds **two segments** —
`venta` (52 rows) and `desguace` (52 rows), 104 rows total — so **always scope by
`segment`**. Venta per-province verdicts: **14 SELLADO, 31 PARCIAL, 7 GAP** (52
provinces). The `desguace` segment is all **52 SELLADO** (national 2,785 ÷ 1,292 =
215.6%, found exceeds the DGT census). These are moving targets read live, not
constants — re-run the query.

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("venta by verdict:", await c.fetch("select verdict,count(*) n,sum(numerator) num,sum(denominator) den from v_province_seal where segment='venta' group by verdict order by n desc"))
    print("venta national:", await c.fetchrow("select sum(numerator) num,sum(denominator) den from v_province_seal where segment='venta'"))
    print("desguace by verdict:", await c.fetch("select verdict,count(*) n from v_province_seal where segment='desguace' group by verdict"))
    await c.close()
asyncio.run(m())
PY
```

### MSE statistical seal — `v_exhaustiveness_seal` + `pipeline/exhaustiveness/seal.py`

Capture-recapture (Chapman / log-linear MSE). A stratum SEALS at threshold X iff
`coverage_lower = n_obs / ci_high >= X` (default **0.95**); the point estimate never
certifies (`seal.py:1-11,27,39-47`). National roll-up is the **sum of per-stratum N̂**
over **identified** strata only (uncertified strata are reported separately, not
folded in as 100% — anti-maquillaje, `seal.py:84-90`). The external census anchor is
loaded from `countries/ES/census/` via `triangulation.load_external_census()`
(`seal.py:68-69`, `triangulation.py:24-50`); absent anchor → `no_anchor` (graceful).

```bash
python -m pipeline.exhaustiveness.cli       # compute/seal (see exhaustiveness/cli.py)
```

> **Honest residual `[VERIFIED docs/SPAIN_SEALED.md]`:** `compraventa` reads ~10% in
> the MSE not because of under-coverage but because the orthogonal discovery lists do
> not overlap enough to *statistically bound* a population larger than the registral
> ceiling — a limit of identifiability, not of real coverage. The venta seal (80.5%)
> and the MSE seal answer different questions; report both.

---

# PART B — How to stand up COUNTRY #2 (`XX`) at 100%

FASE 0 (commit `8866720`) made the country a parameter. PART B is the **exact ordered
sequence** to onboard `XX`, with the gate and rollback at each step. The principle:
`ES` paths/codes are **byte-identical** to pre-FASE-0 (proven by golden tests + the
431,212 ES rows all still `CDP-ES-*`); a second country is onboarded by passing a
different `country_code` and cloning the ES-specific surface.

## B.0 — What FASE 0 already delivered (the mechanism) `[VERIFIED]`

| Mechanism | Where | Status |
|---|---|---|
| `cdp_code` country prefix is a parameter | `services/api/codes.py:44-53` — `mint_code(province_code, digest, country_code="ES")` → `CDP-{country}-…`; the literal lives in ONE place | `[VERIFIED]` landed |
| `country_code` deliberately **out** of the dedup pre-image | `codes.py:62-65` — `canonical_key()` ignores `country_code` so threading it cannot re-key any entity | `[VERIFIED]` |
| Path helpers | `pipeline/paths.py` — `recipe_root/recipes_flat_dir/data_root/census_dir(country_code="ES")` + `country_of_cdp(cdp)` parses `CDP-XX-` | `[VERIFIED]` landed |
| Path helpers wired into call sites | `recipe.py:15,69`, `harvest_dealer.py:21,61`, `triangulation.py:24,32,50` | `[VERIFIED]` |
| Additive `country_code` column | `migrations/0052_country.sql` — `CHAR(2) NOT NULL DEFAULT 'ES'` on `geo_province/geo_comarca/geo_municipality/entity`; backfills every existing row `ES` | `[VERIFIED]` applied 2026-06-23 01:25Z |
| Composite UNIQUE `(country_code, code)` | `0052_country.sql:61-77` — `uq_geo_province_country_code`, `uq_geo_municipality_country_code` (the surface for the future PK swap) | `[VERIFIED]` present in `pg_constraint` |
| Country-scoped indexes | `0052_country.sql:80-81` — `idx_entity_country`, `idx_geo_municipality_country` | `[VERIFIED]` |

**Verify FASE 0 is intact before starting:**

```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("cc cols:", [r['table_name'] for r in await c.fetch(
      "select table_name from information_schema.columns where column_name='country_code' order by 1")])
    print("uniques:", [r['conname'] for r in await c.fetch(
      "select conname from pg_constraint where conname like 'uq_geo_%country%' order by 1")])
    print("all ES:", await c.fetchval("select count(*)=count(*) filter (where country_code='ES') from entity"))
    await c.close()
asyncio.run(m())
PY
# expect: cc cols [entity,geo_comarca,geo_municipality,geo_province]; both uniques; all ES True
```

## B.1 — STEP 1: the country-onboarding migration (the one FK-breaking change)

`0052_country.sql:24-41` **deferred** the FK-breaking changes by design — they are
unnecessary while every row is `ES` and must be a separate, reviewed migration done
**before any second country's data loads** (while ES is still the sole tenant, so the
rewrite is trivial). Author this as `migrations/0053_country_onboarding.sql`.

It must do four things (the deferred list, `0052_country.sql:29-41`):

1. **(a) PK swap to `(country_code, code)`** for `geo_province` and
   `geo_municipality`. The composite UNIQUEs from `0052` make this mechanical:
   `ALTER TABLE … DROP CONSTRAINT geo_province_pkey, ADD PRIMARY KEY (country_code,
   code)` — and **composite-rewrite all 7 referencing FKs** (`entity.province_code`,
   `geo_comarca.province_code`, `geo_municipality.province_code`,
   `denominator_estimate.province_code`, `organization.hq_province_code`,
   `entity.municipality_code` → must carry `country_code` too). Today `28` is a bare
   PK so two countries would collide; this is **the single not-purely-additive step**
   (`0052_country.sql:29-33`, GUIDE §8.1). `[VERIFIED]` the 7 FKs in
   `0052_country.sql:9-17`.
2. **(b)** add `country_code` to `denominator_estimate` and `organization` and
   rewrite their FKs (`0052_country.sql:34`).
3. **(c) relax the ES-specific CHECKs** — both are live `[VERIFIED]`:
   `geo_municipality` `municipality_province_prefix` = `CHECK (left(code,2)=
   province_code)` and `entity` `chk_entity_muni_province` (same prefix invariant).
   These encode INE's `<prov2><muni3>` scheme. A country whose municipality codes are
   not that shape must make these **per-country** (e.g. drop the global CHECK and
   enforce width/prefix in `load_geo_xx.py`, or gate the CHECK on
   `country_code='ES'`) — `0052_country.sql:34-37`.
4. **(e)** if needed, extend `geo_comarca` to a `(country_code, province_code, name)`
   surface (it has no `code` column; PK is `id`, `0052_country.sql:38-41`).

> **Decision — `vehicle` gets NO `country_code` (YAGNI) `[VERIFIED 0052_country.sql:37-38`:**
> `vehicle.country` is derivable via `vehicle.entity_ulid → entity.country_code`;
> the geo backbone + `entity` are the single source of the country dimension.
> A 2.3M-row (`vehicle`, **2,312,292** live) rewrite is deliberately avoided.

**Gate (before applying 0053):** snapshot the FK set and ES counts.
```bash
python -m scripts.migrate status     # confirm 0052 applied, 0053 pending
pg_dump -s -h 127.0.0.1 -p 5433 -U cardeep cardeep > /tmp/schema_pre_0053.sql  # schema-only snapshot
```
**Apply + verify:**
```bash
python -m scripts.migrate up
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("province PK:", await c.fetchval("""select pg_get_constraintdef(oid) from pg_constraint
      where conrelid='geo_province'::regclass and contype='p'"""))
    print("ES still all here:", await c.fetchval("select count(*) from entity where country_code='ES'"))  # must stay 431,212+
    await c.close()
asyncio.run(m())
PY
```
**Rollback:** every migration carries a commented `-- Rollback:` block
(`0052_country.sql:83-91` is the template); the runner strips it on apply
(`migrate.py:47-65`). For 0053 the rollback re-swaps the PK back to `(code)` and
re-adds the CHECKs. Because no `XX` data exists yet, rollback is safe.

**Acceptance gate B.1:** `migrate verify` exit 0; ES entity count unchanged
(≥431,212); ES golden `cdp_code` test green; all 7 FKs resolve against the new
composite PK.

## B.2 — STEP 2: geo backbone for `XX`

ES analogue: `scripts/load_geo.py` `[VERIFIED]` — 52 hard-coded `PROVINCES` + 19
`CCAA`, municipalities from INE `diccionario_ine.xlsx`, INSERT-only
`ON CONFLICT DO NOTHING` (`load_geo.py:1-45`).

1. Source `XX`'s official admin grid: **L1** (province/région/Land), **L2**
   (municipality/commune/comune), optional **L3** (comarca analogue).
2. Write `scripts/load_geo_xx.py` (clone of `load_geo.py`) inserting rows with
   `country_code='XX'`. Adapt code widths + the prefix invariant to `XX`'s scheme
   (relaxed in B.1 step c). `ccaa_code/ccaa_name` are ES-only → NULL or `XX`'s own L1
   division.
3. Geo **hierarchy depth — 2-level (ES) vs 3-level (DE/FR) `[VERIFIED/ASSUMED]`:**
   ES is 2-level (province → municipality; `geo_comarca` exists with 323 rows but the
   API `/geo` assumes province → municipality, GUIDE §8.2 `[ASSUMED]`). For a 3-level
   country (DE Land→Kreis→Gemeinde, FR région→département→commune) the `geo_comarca`
   slot absorbs the L2-vs-L3 distinction, but the `/geo` router needs a third path
   segment for full fidelity — **flag and design before serving 3-level geo** (this is
   an open API change, not yet built, GUIDE §8.2).

**Acceptance gate B.2:**
```bash
python -m scripts.load_geo_xx
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("XX provinces:", await c.fetchval("select count(*) from geo_province where country_code='XX'"))
    print("XX munis:", await c.fetchval("select count(*) from geo_municipality where country_code='XX'"))
    print("ES untouched:", await c.fetchval("select count(*) from geo_province where country_code='ES'"))  # must be 52
    await c.close()
asyncio.run(m())
PY
```
Gate passes when `XX` province/municipality counts equal the official counts and ES
stays at 52/8,132. **Rollback:** `DELETE FROM geo_municipality WHERE
country_code='XX'; DELETE FROM geo_province WHERE country_code='XX';` (no ES row is
touched — INSERT-only loader).

## B.3 — STEP 3: census / denominator anchor (optional at start)

ES analogue: `countries/ES/census/dirce_cnae451.csv` (`province_code,segment,
n_external`) + `SOURCE.md` provenance. The seam is country-parametrized
(`triangulation.py:50` resolves `census_dir(country_code)/dirce_cnae451.csv`) and
returns `{}` / `no_anchor` when absent `[VERIFIED]`.

1. `countries/XX/census/SOURCE.md` documenting the chosen €0 official anchor (DGT/
   DIRCE for ES → KBA/Destatis for DE, SIV/ANFIA for IT) and which figures are
   MEDIDO vs ESTIMADO-DECLARADO.
2. Drop `countries/XX/census/dirce_cnae451.csv` with the same schema.
3. Re-tune `_SEGMENT` in `pipeline/exhaustiveness/capture.py` only if `XX`'s anchor
   uses strata other than {compraventa, concesionario, desguace, otros}.

**Gate:** `census_dir("XX")` exists and `triangulation.load_external_census("XX")`
returns the parsed dict (or, intentionally, `no_anchor` if you start without it — a
country runs from day one with no anchor). **Rollback:** delete the CSV; the seam
degrades to `no_anchor`.

## B.4 — STEP 4: source + platform adapters (the bulk of the work)

This is irreducibly per-country `[VERIFIED GUIDE §8.4]` — there is no auto-generation;
the framework replicates, the adapter *content* is fresh.

1. **Discovery sources** — for each, write `pipeline/sources/<src>.py` implementing
   `SourceAdapter` (`pipeline/sources/base.py:30-42`): `fetch()` yields
   `DiscoveredEntity` (raw `province_name`/`municipality_name`) and `declared_count()`
   for the VAM quorum. Register it in `pipeline/discover.py:48` `ADAPTERS`.
2. **Platforms** — write `pipeline/platform/<plat>_wholesale.py` (the connector that
   writes `record_run`), register its `source_key` → `SourceEntry` in
   `pipeline/ops/scheduler.py:131` `REGISTRY`, and seed its `source_health` cadence
   row.
3. **Recurrent discovery** — add the new vectors to
   `pipeline/discover_schedule.py:65` `DISCOVERY_REGISTRY` with cadence +
   orthogonality + any `requires_env` gate.
4. **Tier classification** — Tier-1 bundles → `countries/XX/_tier1/`, OPEN platforms
   → `countries/XX/_platforms/<group>/` (clone the `countries/ES/` shape, GUIDE §3).

**Gate:** `python -m pipeline.discover <xx_src>` closes with a TRUSTWORTHY VAM verdict
(`declared==fetched==in_db`, `discover.py:159-164`); the platform appears in
`python -m pipeline.ops.scheduler --dry-run` as WOULD RUN (mapped, not in the gap
report). **Rollback:** remove the adapter from `ADAPTERS`/`REGISTRY` and
`DELETE FROM entity WHERE country_code='XX' AND first_discovered_source='<xx_src>'`.

## B.5 — STEP 5: identity locals + market calibration

1. **Phone:** clone `pipeline/identity/phone_es.py` → `phone_xx.py` (the only
   country-tied identity helper, GUIDE §6) for `XX`'s numbering plan; wire behind a
   country switch in `cross_source_dedup`/`resolve_entities`.
2. **Registral id:** ES uses `entity.cif`; `XX` may use a different VAT/registry id.
   Reuse `entity.cif` if generic enough, or add `entity.reg_id` `[ASSUMED]`.
3. **Price gate:** re-calibrate `pipeline/price_sanity.py` for `XX`'s currency/market
   (ES: EUR, €5M ceiling `[VERIFIED]`). EUR countries may carry the ceiling over;
   non-EUR replace currency + bounds.

**Gate:** unit tests for `phone_xx.py`; a deliberately out-of-range `XX` price is
QUARANTINE-flagged, not served.

## B.6 — STEP 6: pilot harvest end-to-end

Harvest one `XX` dealer through the full lifecycle and verify all artifacts land in
the `XX` partition (the §A path helpers route by country automatically once the code
is `CDP-XX-*`):

```bash
python -m pipeline.discover <xx_src>            # mint a CDP-XX-* entity
python -m pipeline.ops.scheduler --dry-run      # confirm the XX platform is DUE + mapped
# (run the connector; harvest writes vehicle rows + events, recipe to countries/XX/, raw to data/XX/)
```
**Acceptance gate B.6 `[ASSUMED, mirrors A.1–A.6]`:**
```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    print("CDP-XX entities:", await c.fetchval("select count(*) from entity where cdp_code like 'CDP-XX-%'"))
    print("XX vehicles:", await c.fetchval("""select count(*) from vehicle v join entity e on e.entity_ulid=v.entity_ulid
        where e.country_code='XX'"""))
    await c.close()
asyncio.run(m())
PY
```
Confirm: raw in `data/XX/`, recipe in `countries/XX/recipes/`, entity in DB with
`country_code='XX'` + a `CDP-XX-*` code, and `/entities/{cdp}/inventory` +
`/entities/{cdp}/delta` serve it.

## B.7 — STEP 7: coverage seal for `XX`

Run the same two seals (A.7) scoped to `XX`:
- **Venta seal:** `v_province_seal` already groups by `province_code`; with the
  composite geo PK (B.1) and `XX` denominators loaded, it yields `XX` per-province
  verdicts. Drop `XX` registral ceilings via `scripts/load_denominator_provincia.py`.
- **MSE seal:** `python -m pipeline.exhaustiveness.cli` reuses the capture-recapture
  math unchanged; it contrasts against the B.3 anchor (or `no_anchor`).

## B.8 — Acceptance criteria: "country `XX` replicated at 100%"

Mirrors `REPLICATION-GUIDE.md:400-413` (§9), made executable. `XX` is replicated when
**all** hold for every province of `XX`:

1. **Geo backbone loaded** — `geo_province`/`geo_municipality` rows with
   `country_code='XX'`, counts matching the official admin grid (B.2 gate).
2. **≥1 discovery source + ≥1 platform adapter live**, producing `CDP-XX-*` entities
   with provenance (`entity_source`), each run closing a TRUSTWORTHY VAM verdict.
3. **A pilot dealer harvested end-to-end** — raw `data/XX/`, recipe
   `countries/XX/recipes/`, served by `/entities/{cdp}/inventory` (B.6 gate).
4. **Delta live** — `/entities/{cdp}/delta?since=…` returns `XX` vehicle events
   (NEW/PRICE_CHANGE/GONE) from `vehicle_event`.
5. **Coverage% + seal** — capture-recapture N̂ computed; venta seal `coverage_pct`
   per `XX` province with the SELLADO ≥85% / PARCIAL / GAP verdict; ≥1 `XX` province
   SELLADO; MSE `coverage_lower ≥ 0.95` for ≥1 identified stratum (or `no_anchor`
   honestly reported).
6. **Zero ES regression** — the FASE-0 + 0053 changes are backward-compatible:
   `migrate verify` exit 0, the ES golden `cdp_code` test green, and ES rows
   untouched (`select count(*) from entity where country_code='ES'` ≥ **431,212**,
   all still `CDP-ES-*`).

**Single roll-up check `[the 100% gate]`:**
```bash
python - <<'PY'
import asyncio, asyncpg
async def m():
    c=await asyncpg.connect("postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep")
    es = await c.fetchval("select count(*) from entity where country_code='ES'")
    es_ok = es>=431212 and es==await c.fetchval("select count(*) from entity where cdp_code like 'CDP-ES-%'")
    xx = await c.fetchval("select count(*) from entity where country_code='XX'")
    sealed = await c.fetchval("select count(*) from v_province_seal where verdict='SELLADO'")  # XX needs province scoping in 0053
    print(f"ES regression-free: {es_ok} (es={es})  |  XX entities: {xx}  |  SELLADO segments: {sealed}")
    await c.close()
asyncio.run(m())
PY
```

---

## Appendix — module map (cited, `[VERIFIED]`)

| Stage | Module | Command |
|---|---|---|
| Migrate | `scripts/migrate.py` | `python -m scripts.migrate up\|status\|verify\|repair` |
| Geo load | `scripts/load_geo.py` | `python -m scripts.load_geo` |
| Denominator | `scripts/load_denominator_provincia.py` | (loads `denominator_estimate`) |
| Discover (one-shot) | `pipeline/discover.py` (25 adapters, `:48-74`) | `python -m pipeline.discover <vector>` |
| Discover (daemon) | `pipeline/discover_schedule.py` (5 vectors, `:65-84`) | `--dry-run\|--seed\|--tick\|--once V\|--serve` |
| Source contract | `pipeline/sources/base.py:30-42` | (clone per source) |
| Harvest scheduler | `pipeline/ops/scheduler.py` (REGISTRY `:131-295`) | `--dry-run\|--check-silence\|(blocking)` |
| Recipe harness | `pipeline/recipe_harness.py` | (EXTRACT→PERSIST→VERIFY→DELETE) |
| Recipe persist | `pipeline/recipe.py:43-69` | `write_recipe(cdp_code)` |
| Identity mint | `services/api/codes.py:44-130` | `cdp_code(...)` / `mint_code(...)` |
| Dedup/cluster | `pipeline/identity/{cross_source_dedup,cluster_dealers,resolve_entities}.py` | — |
| Paths | `pipeline/paths.py` | `recipe_root/data_root/census_dir(country_code)` |
| API | `services/api/main.py` + `routers/*` | `uvicorn services.api.main:app` |
| Delta | `services/api/routers/entities.py:170-237` | `GET /entities/{cdp}/delta?since=` |
| Venta seal | `migrations/0042_province_seal_view.sql` → `v_province_seal` | (live view) |
| MSE seal | `pipeline/exhaustiveness/seal.py` + `v_exhaustiveness_seal` | `python -m pipeline.exhaustiveness.cli` |
| Country migration (FASE 0) | `migrations/0052_country.sql` | applied 2026-06-23 |
| Country onboarding (B.1) | `migrations/0053_country_onboarding.sql` `[to author]` | the deferred PK swap |
