# T13 — Datastore: Live 2026 Tooling Audit

> **Domain:** The storage substrate for CARDEEP at scale — tens of millions of
> `vehicle` rows + an append-only `vehicle_event` delta log + a geo backbone, served
> as a hybrid OLTP (per-entity/per-platform/PDP reads, ingest writes) **and** OLAP
> (delta-since firehose, geo-grid aggregation, `/stats` rollups) workload. The
> decision space: **PostgreSQL 16/17/18 + declarative partitioning + pg_trgm + PostGIS
> + (TimescaleDB?)** versus **ClickHouse** for the analytics/delta layer; and whether
> a hybrid OLTP+OLAP split is warranted at all. Plus the index/partition strategy and
> the maintenance/automation extensions (pg_partman, pg_cron) and the
> analytics-in-Postgres engines (pg_duckdb, pg_mooncake).
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I
> fetched the repo / release page / GitHub API this session, URL + value cited) or
> **[ASSUMED]** (inferred, design judgment). No corpses are recommended.
>
> **Recency bar:** a tool with no *release* in ~12 months is *suspect*; no *commit* in
> ~12 months is *dead for our purposes*. Stated explicitly per tool — and where a tool
> has a stale **tag** but a live **default branch**, that distinction is called out
> rather than hidden (it changes the verdict).

---

## 0. The CARDEEP-specific reality (why generic "ClickHouse is faster" benchmarks lie)

The incumbent is **not** a candidate to be graded against alternatives in the abstract —
it is a *live, running* PostgreSQL 16.14 instance with a designed schema. Ground truth,
read this session from `docs/architecture/03-DATA-MODEL.md` and the live DB probes it
records **[VERIFIED, repo-local]**:

| Fact | Value | Consequence for this audit |
|---|---|---|
| Engine | **PostgreSQL 16.14** (Debian, Docker `cardeep-pg`, `127.0.0.1:5433`) | The pick is "evolve this", not "greenfield" |
| Extensions **available** | `btree_gin`, `pg_trgm`, `pgcrypto`, `uuid-ossp` | pg_trgm is the fuzzy-search spine; **PostGIS is NOT in the image** |
| Extensions **installed** | only `plpgsql` (+ planned `pg_trgm`, `btree_gin`, `pgcrypto` in `0005`) | every extension we recommend must be *added to the image*, not assumed present |
| **PostGIS NOT available** | absent from `pg_available_extensions` | geo today = lat/lon `double precision` + bbox btree + Haversine; PostGIS is a *future gated add* (`0099`), not a dependency |
| Snapshot partitioning | `vehicle` **`PARTITION BY LIST (province_code)`** (~53 parts) | geo-first access pattern; province-local queries prune to one partition |
| Log partitioning | `vehicle_event` **`PARTITION BY RANGE (observed_at)` monthly** | the delta/OLAP-shaped table; "delta since yesterday" touches 1–2 partitions |
| Live volume (2026-06-12) | entity 12.862 · vehicle 39.068 · vehicle_event 41.165 | **today the whole DB is < 1 GB** — orders of magnitude below any "you need ClickHouse" threshold |
| Target volume | tens of millions of vehicles + full delta history forever | the design must *scale to* that, not be load-tested there yet |
| Driver | **asyncpg** (FastAPI) | any datastore swap means re-plumbing the driver layer — a real cost |
| Mutation doctrine | INSERT-new/close-gone; UPDATE only mutated field +event; append-only log | classic **OLTP write pattern** with an **OLAP read tail** → the textbook hybrid case |

**The load-bearing point:** CARDEEP's analytics surface (delta firehose, geo-grid,
`/stats`) is real, but it is **bounded** — it aggregates over a single country's vehicle
census, partitioned by province and month, with indexes sized to the exact hot paths
(`03-DATA-MODEL.md §4.1, §5.1`). The ClickHouse decision guide's own threshold for "you
need a columnar OLAP engine" is **>500 GB active data and hundreds of concurrent
analytical queries** **[VERIFIED]** (clickhouse.com/resources/.../how-to-choose...-2026).
CARDEEP is ~3 orders of magnitude under that today and, even at tens of millions of rows
with full history, the *hot* serving set (current `available` inventory + recent delta)
stays well within PostgreSQL's competent range when partitioned and indexed as designed.

So the question is **not** "PostgreSQL or ClickHouse" — it is "is single-node partitioned
PostgreSQL 17/18 the bulletproof substrate, and at what concrete trigger does a ClickHouse
*serving layer* (not replacement) earn its operational cost?"

---

## 1. Verdict up front

| Layer | Pick | Status | Why |
|---|---|---|---|
| **Core OLTP + OLAP engine** | **PostgreSQL 18** (upgrade target; **17** the conservative interim) | ✅ **alive** (18.4, 2026-05-14) | AIO subsystem (up to 3× read throughput), skip-scan, improved partition pruning/joins, retained planner stats across major upgrade — directly helps CARDEEP's partition-scan + delta workload. **The incumbent, and it is the right pick.** |
| **Partition automation** | **pg_partman + pg_cron** | ✅ **alive** (partman 5.4.3 2026-03-05; cron 1.6.7 2025-09-04, pushed 2026-04-21) | Replaces the hand-rolled "monthly cron creates next `vehicle_event` partition" job (`03-DATA-MODEL.md §8.3`) with a battle-tested, declarative-partitioning-native extension. **The one concrete add to the current design.** |
| **Fuzzy name/alias search** | **pg_trgm (built-in)** | ✅ **alive** (ships with PG18) | Already the design's choice (`gin_trgm_ops` on `trade_name`/`legal_name`/`description`). No change. Bulletproof, in-core. |
| **Geo (current)** | **lat/lon + composite btree + Haversine** (no extension) | ✅ **alive** | Correct for national-zoom grid at current density; PostGIS not in the image. Keep. |
| **Geo (future, gated)** | **PostGIS 3.6** | ✅ **alive** (3.6.3, May 2026; PG14–18) | The clean drop-in *if/when* rooftop-density clustering or true `ST_DWithin` "near me" is needed. `0099_postgis_geo.sql`, additive. **Not needed for v1.** |
| **Time-series / columnar-in-PG** | **TimescaleDB** | 🟡 **alive but rejected for the core** (2.27.2, 2026-06-02; PG18 support since 2.23) | Excellent engine, but its hypertable model competes with CARDEEP's *already-chosen* province-LIST + month-RANGE native partitioning, adds a heavy extension + a non-OSI license (TSL), and buys little the native scheme doesn't. **Fallback only**, for the event log, if native partition maintenance ever proves insufficient. |
| **Analytics-in-PG (OLAP accel)** | **pg_duckdb** | ✅ **alive** (1.1.1, 2025-12-18; last commit 2026-03-16) | If `/stats` / grid aggregations ever get heavy, pg_duckdb runs DuckDB's vectorized engine *inside* Postgres over the same tables — OLAP speed without a second datastore or CDC. **The preferred scale-tier accelerant** before reaching for ClickHouse. |
| **Lakehouse columnstore mirror** | **pg_mooncake** | 🟡 **early-stage, watch** (tag v0.1.3; last commit 2025-10-26 "Support Postgres 18") | Iceberg columnstore mirror of PG tables, now a *subextension of pg_duckdb*. Promising but sub-v1 and the default branch has not moved since 2025-10. **Not for v1; re-evaluate when it tags v0.2/1.0.** |
| **Dedicated OLAP serving engine** | **ClickHouse** | ✅ **alive** (26.4.4, 2026-06-08, monthly CalVer) | World-class columnar OLAP. But it is a *second datastore* with its own ops, and CARDEEP is far below its break-even scale. **Scale-tier fallback as a read-only serving layer fed by CDC (PeerDB→ClickPipes)**, switched on only at a concrete volume/concurrency trigger — never as the OLTP store. |
| **Horizontal scale-out** | **Citus** | ✅ **alive** (14.0, 2026-02-17; PG18.1) | Distributed PostgreSQL. Real and maintained, but CARDEEP is single-node-sized for the foreseeable future. **Documented exit ramp**, not a v1 dependency. |

**Bottom line.** The current CARDEEP choice — **single-node, partitioned PostgreSQL 16**
— is **correct and good enough**, and the only change it *needs* is to **upgrade to
PostgreSQL 18** (for AIO + partition-pruning/skip-scan wins and the cross-upgrade planner
stats), and to **adopt pg_partman + pg_cron** so partition lifecycle is automated by a
proven extension instead of a hand-rolled cron. Everything heavier — TimescaleDB,
pg_mooncake, ClickHouse, Citus — is **deferred behind a concrete trigger**, because
adopting any of them now would add operational mass the workload does not yet justify
(YAGNI). The hybrid OLTP+OLAP need is **real but satisfiable inside Postgres** at
CARDEEP's scale; the moment it isn't, the bulletproof escalation order is
**pg_duckdb (in-process) → ClickHouse serving layer via PeerDB CDC (out-of-process)**,
in that order.

---

## 2. The core engine — PostgreSQL

### 2.1 PostgreSQL 18 — **RECOMMENDED (upgrade target)** ✅

- **Release page:** https://www.postgresql.org/about/news/postgresql-18-released-3142/ —
  **[VERIFIED]** PostgreSQL **18.0 released 2025-09-25**; **18.4 released 2026-05-14**
  (https://www.postgresql.org/docs/release/18.4/) **[VERIFIED via search + release index]**.
  18.x is the current stable line; 16.x (CARDEEP's incumbent) is fully supported until
  **Nov 2028** per the PG support policy **[ASSUMED — standard 5-yr policy, not re-fetched]**.
- **Alive?** ✅ Emphatically — it *is* the reference implementation, quarterly minors,
  active major-version cadence.

**What PG18 buys CARDEEP specifically (not generic hype):**
- **Asynchronous I/O (AIO) subsystem** — up to ~3× faster reads from storage for
  sequential scans, bitmap heap scans, and **VACUUM** **[VERIFIED via release notes/search]**.
  CARDEEP's two heaviest patterns are *exactly* these: the GONE-sweep / freshness scan
  (`idx_vp_status_seen`), the delta-since range scan over `vehicle_event` partitions, and
  VACUUM on the high-churn `status`/`last_seen` columns. AIO is a direct, free win on the
  hot path.
- **Skip-scan on multicolumn B-tree indexes** **[VERIFIED]** — queries that omit an `=`
  on a leading index column can still use the index. CARDEEP has several composite indexes
  (`idx_vp_make_model (make,model,year)`, `idx_entity_kind_prov (kind, province_code)`)
  where a query filtering only on the *second* column previously couldn't use them. Skip-scan
  recovers those.
- **Improved partition pruning + partition-wise join support** **[VERIFIED]** — compounding
  on the design's two partition schemes (province LIST, month RANGE). The geo-grid and
  delta endpoints prune harder.
- **Retained planner statistics across a major-version upgrade** **[VERIFIED]** — the
  16→18 `pg_upgrade` no longer leaves the cluster slow until a full ANALYZE; it reaches
  expected performance immediately. This *materially de-risks the upgrade itself*.
- **`uuidv7()` in core** **[VERIFIED]** — time-ordered UUIDs. CARDEEP deliberately uses
  Crockford ULIDs (`pipeline/ids.py`) and the data-model doc argues *against* switching to
  native `uuid` (`§2`); `uuidv7()` does **not** change that decision (ULIDs are already
  time-sortable and the repo-wide FK rewrite cost is real) — noted only so the option is
  on record, not recommended.

**Honest risk / integration notes.**
- **Extension lag is the real upgrade gate, not core.** Every extension CARDEEP depends on
  must have a PG18 build *before* the upgrade: pg_partman ✅ (PG18-tested), pg_cron ✅
  (1.6.7 tested on PG18), pg_trgm ✅ (in-core), PostGIS ✅ (3.6 supports PG18) — all clear
  **[VERIFIED, see their sections]**. The `wiki.postgresql.org/wiki/PostgreSQL_18_Extension_Bugs`
  page **[VERIFIED via search]** tracks per-extension PG18 issues — check it at upgrade time.
- **PG18 introduced wire protocol 3.2** **[VERIFIED]** — asyncpg negotiates protocol; verify
  the pinned `asyncpg` version speaks to PG18 cleanly before cutover (it defaults to 3.0,
  which PG18 still serves — low risk, but `[ASSUMED]` until tested against the real driver).
- **Conservative interim: PostgreSQL 17.** If the operator wants to skip an `.0`-line major,
  17 (released 2024-09, current 17.x in 2026) already has partition-wise aggregate pushdown
  and the improved pruning that benefit the rollup/grid queries **[VERIFIED via search]**, and
  every extension supports it. 17 is the "no-surprises" interim; 18 is the "best substrate"
  target. **Recommendation: go to 18** unless an extension blocker appears at upgrade time, in
  which case 17 is the safe harbor.

**Sample config — the upgrade + extension manifest (image build):**
```dockerfile
# CARDEEP datastore image — Postgres 18 + the exact extension set the schema needs.
FROM postgres:18
RUN apt-get update && apt-get install -y --no-install-recommends \
      postgresql-18-partman \
      postgresql-18-cron \
   && rm -rf /var/lib/apt/lists/*
# pg_trgm, btree_gin, pgcrypto are in-core (contrib) — no package needed.
# PostGIS deliberately omitted (geo = lat/lon + btree today; add postgresql-18-postgis-3
#   only when 0099_postgis_geo.sql is scheduled).
```
```ini
# postgresql.conf deltas for the CARDEEP workload (append to image config)
shared_preload_libraries = 'pg_cron'           # pg_cron must preload; pg_partman runs in-SQL
cron.database_name       = 'cardeep'
# AIO is on by default in PG18; io_method=worker is the portable default.
io_method                = 'worker'            # 'io_uring' on modern Linux for max AIO benefit
max_worker_processes     = 16                  # cron + partman bgw + parallel query headroom
# partition-friendly planner:
enable_partition_pruning = on                  # default on; assert it
enable_partitionwise_join = on                 # off by default — turn ON for cross-partition joins
enable_partitionwise_aggregate = on            # off by default — turn ON for /stats & grid rollups
```
> `enable_partitionwise_join`/`aggregate` are **off by default** in stock Postgres — turning
> them on is a concrete, verified win for CARDEEP's aggregation endpoints and costs only
> planner time on partitioned queries.

---

## 3. Partition automation — pg_partman + pg_cron

### 3.1 pg_partman — **RECOMMENDED (the one real add)** ✅

- **Repo:** https://github.com/pgpartman/pg_partman — **[VERIFIED]** 2,728★, not archived,
  **last pushed 2026-03-09**.
- **Latest release:** **5.4.3, 2026-03-05** **[VERIFIED via GitHub API]**
  (https://github.com/pgpartman/pg_partman/releases). ⚠️ **Avoid 5.4.2** — it shipped a
  broken extension control file that breaks upgrades from 5.4.1; **5.4.3 fixes it**
  **[VERIFIED via search]**. Pin `>=5.4.3`.
- **Alive?** ✅ Yes — release 2026-03, push 2026-03, PG18-compatible **[VERIFIED via search:
  "Unlogged tables still supported as of PG18… through the template table system"]**.

**What it solves for CARDEEP.** The data-model doc currently specifies a **hand-rolled
maintenance job** (`§8.3`): "a monthly cron creates next month's `vehicle_event_*`
partition… if it misses, rows land in the `default` partition and an alert fires."
pg_partman is the **purpose-built, declarative-partitioning-native** replacement for
exactly that: it auto-creates future child partitions ahead of time (`premake`),
optionally auto-drops/detaches old ones on a **retention policy** (CARDEEP's "cold-event
archival, `DETACH` months older than 24mo" — `§8.3.2`), and runs entirely via
`run_maintenance_proc()` triggered by pg_cron. It works **on top of native declarative
partitioning** (it does not replace it), so CARDEEP's `PARTITION BY RANGE (observed_at)`
stays exactly as designed — pg_partman just manages the children.

**Strengths.** Eliminates the "if the cron misses, rows hit `default`" failure mode (it
premakes ahead, so a missed run has slack); battle-tested (AWS RDS/Aurora, Yugabyte, and
PlanetScale all ship `pg_partman`/`pg_partman_bgw` **[VERIFIED via search]**); native
declarative-partitioning support (not the legacy trigger-based inheritance); retention
automation matches CARDEEP's archival requirement 1:1.

**Weaknesses / honest notes.** (a) Adds an extension to the image (minor). (b) The
`_bgw` background-worker variant needs `shared_preload_libraries` (CARDEEP can instead
drive `run_maintenance_proc()` from **pg_cron**, avoiding a second preload — cleaner).
(c) pg_partman manages **one partition dimension per table** — perfect for the *time-range*
`vehicle_event` log; the **province-LIST** `vehicle` partitions are a *fixed, bounded set*
(52 provinces + sentinels) created once and never rolled, so they **don't need pg_partman
at all** — they're static. So: **use pg_partman for `vehicle_event` (the rolling time
dimension); leave the static province partitions as plain declarative DDL.** This is the
correct division and avoids over-applying the tool.

**Integration notes for CARDEEP.**
1. Keep the native `vehicle_event PARTITION BY RANGE (observed_at)` parent (`§5.1`).
2. Register it with pg_partman for monthly children + 24-month retention.
3. Schedule `run_maintenance_proc()` via pg_cron (no bgw preload needed).
4. Keep the `DEFAULT` partition as the safety net + the existing alert on non-empty default.
5. Replace the bespoke "partition pre-creation" job in `§8.3` with this; keep the
   "denormalization reconcile" job (that's app logic, not partitioning).

**Sample config (`migrations/00XX_partman_events.sql`):**
```sql
CREATE EXTENSION IF NOT EXISTS pg_partman;     -- needs a 'partman' schema by convention
-- vehicle_event is already PARTITION BY RANGE (observed_at) with monthly children (§5.1).
SELECT partman.create_parent(
  p_parent_table    => 'public.vehicle_event',
  p_control         => 'observed_at',          -- the RANGE key
  p_interval        => '1 month',              -- monthly children, matching the design
  p_premake         => 4,                      -- keep 4 future months pre-created (slack vs a missed run)
  p_default_table   => true                    -- retain the DEFAULT safety-net partition
);
-- retention: detach (not drop) months older than 24mo so full history is archivable off-DB.
UPDATE partman.part_config
   SET retention = '24 months',
       retention_keep_table = true,            -- DETACH + keep table → pg_dump to cold storage, then drop
       infinite_time_partitions = true
 WHERE parent_table = 'public.vehicle_event';
-- Rollback: SELECT partman.undo_partition('public.vehicle_event', ...); DROP EXTENSION pg_partman;
```

### 3.2 pg_cron — **RECOMMENDED (scheduler)** ✅

- **Repo:** https://github.com/citusdata/pg_cron — **[VERIFIED]** 3,808★, **last pushed
  2026-04-21**.
- **Latest release:** **1.6.7, 2025-09-04** **[VERIFIED via GitHub API]**. ~9 months since
  the last *tag* but the branch is live (push 2026-04) and it is **PG18-tested**
  (1.6.7 noted on the PG18 Extension Bugs wiki **[VERIFIED via search]**).
- **Alive?** ✅ Yes — Citus-maintained (now Microsoft), the de-facto in-DB scheduler,
  shipped by every major managed Postgres.

**What it solves.** In-database cron. Drives `partman.run_maintenance_proc()`, the nightly
`attest_count`/`branch_count` reconcile (`§8.3.3`), and any `/stats` materialized-view
refresh — all *inside* Postgres, no external scheduler, no app-side timer to forget.
Requires `shared_preload_libraries = 'pg_cron'` and `cron.database_name`.

**Sample config:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
-- monthly partition maintenance (premake + retention), 03:00 on the 1st:
SELECT cron.schedule('partman-maintenance', '0 3 1 * *',
  $$CALL partman.run_maintenance_proc()$$);
-- nightly denormalization reconcile (the §8.3.3 job), 04:00 daily:
SELECT cron.schedule('reconcile-counts', '0 4 * * *',
  $$SELECT cardeep_reconcile_denorm_counts()$$);
```
**Pin:** `pg_cron >= 1.6.7`, `pg_partman >= 5.4.3`.

---

## 4. Fuzzy search & geo — keep what the design already chose

### 4.1 pg_trgm — **RECOMMENDED (no change)** ✅
- **In-core** (PostgreSQL contrib), ships with every version incl. 18. **[VERIFIED — listed
  in CARDEEP's `pg_available_extensions`]**. The design already uses `gin_trgm_ops` GIN
  indexes on `entity.trade_name`, `entity.legal_name`, `organization.name`,
  `vehicle_spec.description` (`§3.1, §3.3, §4.2`). This is the correct, bulletproof,
  in-core choice for the `/search?q=` fuzzy surface. **No external tool competes** for
  in-DB trigram search; the alternative (an external search engine like Elasticsearch /
  Meilisearch / Typesense) is a *separate datastore* and is **not justified** for
  single-country name/alias matching that pg_trgm + the T09 ER stack already cover.
  `btree_gin` (also available) lets a single GIN index combine an enum filter + trigram
  for the faceted `/search` (`kind` + `q`) — already in the design (`§2`). Keep both.

### 4.2 Geo — lat/lon + btree today; PostGIS 3.6 as the gated future add 🟡→✅
- **Current (no extension):** `idx_entity_latlon (lat, lon) WHERE lat IS NOT NULL` partial
  composite btree + bbox prefilter + Haversine refine + zoom-decimal grid bucketing
  (`§7.3`). Correct and PostGIS-free, matching the image reality (**PostGIS NOT available**).
  **[VERIFIED, repo-local design.]** Keep for v1.
- **PostGIS 3.6 — alive, the clean later add.** https://postgis.net — **[VERIFIED via
  search]** **3.6.3 released ~May 2026** (3.6.2 2026-02-06), supports **PostgreSQL 14–18**,
  GEOS ≥3.8, Proj ≥6.1. **Alive?** ✅ Very — quarterly point releases, the unchallenged OSS
  spatial standard. **When it earns its place:** if CARDEEP needs true `ST_DWithin` radius
  "near me", rooftop-density clustering at high zoom, or `ST_SnapToGrid` instead of decimal
  bucketing. Then `0099_postgis_geo.sql` adds a generated `geography(Point,4326)` column +
  GiST index, additive, no core rewrite (`§10.4`). **Not needed for v1**; the bbox+Haversine
  path is adequate at national zoom **[ASSUMED, per design]**. Add `postgresql-18-postgis-3`
  to the image only when that migration is scheduled.

---

## 5. The hybrid OLAP question — three escalating answers

CARDEEP's OLAP-shaped surface = the **delta-since firehose** (`GET /delta`), the
**geo-grid aggregation** (`GET /geo/grid`), and the **`/stats` rollups**. The honest
engineering question is *where* that runs. Three tiers, in escalating cost — adopt the
**lowest** that meets the load, never skip ahead.

### 5.1 Tier 0 — native Postgres (current design) — **THE v1 ANSWER** ✅
Partitioned tables + `enable_partitionwise_aggregate` + materialized rollup views
(`§8.1 migration 0012: rollup views (stats, freshness)`) handle every analytics endpoint
at CARDEEP's current and near-term scale. The delta firehose is a **range scan on a
month-partitioned, `observed_at`-indexed log** — the single most OLAP-friendly shape a
row store can offer, and partition pruning makes "since yesterday" touch one partition.
**[VERIFIED design fit.]** This is good enough and is the recommendation for v1. No new tool.

### 5.2 Tier 1 — pg_duckdb (in-process OLAP) — **PREFERRED SCALE ACCELERANT** ✅
- **Repo:** https://github.com/duckdb/pg_duckdb — **[VERIFIED]** 3,130★, not archived,
  **last pushed 2026-03-16**, 116 open issues. **Latest release v1.1.1, 2025-12-18**
  **[VERIFIED via GitHub API — note: a casual read of the releases page misdates this to
  2024; the API `published_at` is `2025-12-18`].** Backed by **DuckDB Labs + MotherDuck +
  Hydra**.
- **Alive?** ✅ Yes — push 2026-03, release 2025-12, DuckDB-Labs-stewarded.

**What it solves.** Embeds DuckDB's **vectorized, columnar** execution engine *inside*
PostgreSQL. You run analytical SQL (`SELECT … FROM postgres_table` via the `duckdb.*`
functions / `SET duckdb.force_execution`) and DuckDB executes the heavy aggregation over
the *same* Postgres tables (or over Parquet/Iceberg in object storage) — **OLAP speed
without a second datastore, without CDC, without leaving the transaction boundary.** It
ranks top-10 on ClickBench while living in Postgres **[ASSUMED — per pg_mooncake's claim
which uses pg_duckdb; not independently re-benchmarked]**.

**Why it's the right *first* escalation for CARDEEP.** If `/stats` or `/geo/grid` over tens
of millions of rows ever gets slow on the row store, pg_duckdb accelerates *those queries*
with **zero new operational surface** — same DB, same backup, same connection pool, same
asyncpg. It is strictly less disruptive than standing up ClickHouse + a CDC pipeline. It is
the **bridge between "native Postgres is enough" and "we genuinely need a separate OLAP
cluster."**

**Weaknesses / honest notes.** (a) It is an *accelerant*, not a storage engine — it does
not change CARDEEP's storage, it speeds reads. (b) Memory-hungry under big aggregations
(DuckDB buffers); needs `max_memory` tuning. (c) 116 open issues — normal for a fast-moving
3k★ project, triage is active. (d) **[ASSUMED]** the in-Postgres DuckDB path is sufficient
for CARDEEP's aggregation volume before ClickHouse is needed — validate with `EXPLAIN` on
real volume.

**Sample config (only when Tier 0 measurably strains):**
```sql
CREATE EXTENSION IF NOT EXISTS pg_duckdb;       -- needs the duckdb shared lib in the image
SET duckdb.force_execution = true;              -- route this session's heavy aggregations to DuckDB
-- /stats rollup accelerated by DuckDB's vectorized engine over the live partitioned table:
SELECT province_code, kind, count(*) AS n, percentile_cont(0.5) WITHIN GROUP (ORDER BY price)
  FROM vehicle JOIN entity USING (entity_ulid)
 WHERE status = 'available'
 GROUP BY province_code, kind;
```
**Pin:** `pg_duckdb >= 1.1.1`.

### 5.3 Tier 2 — ClickHouse as a read-only serving layer (CDC-fed) — **SCALE FALLBACK** ✅
- **Repo:** https://github.com/ClickHouse/ClickHouse — **[VERIFIED]** 47,963★, **last
  pushed 2026-06-12**. **Latest stable v26.4.4.38, 2026-06-08** (CalVer `Year.Month.Patch`,
  ~monthly minors) **[VERIFIED via GitHub API]**.
- **Alive?** ✅ Among the most active OSS databases on earth.

**What it solves & when it earns its cost.** ClickHouse is the fastest-class columnar OLAP
engine (tops ClickBench) **[VERIFIED — clickhouse.com fastest-OLAP-2026 page]**. For
CARDEEP it is **never the OLTP store** (no real transactions, mutate-in-place is alien to
its merge-tree model — CARDEEP's INSERT-new/UPDATE-mutated-field/append-log doctrine is the
*opposite* of ClickHouse's strengths). Its **only** correct role is a **read-only serving
layer for the analytics surface** *if and only if* the delta firehose / grid / stats grow
past what partitioned Postgres + pg_duckdb can serve at the required latency and
concurrency. ClickHouse's own 2026 decision guide draws that line at **>500 GB active data
+ hundreds of concurrent analytical queries** **[VERIFIED]** — and explicitly recommends
the **augmentation** pattern: "keep Postgres, add ClickHouse as a serving layer," not
replacement **[VERIFIED]**.

**The concrete integration path (verified, low-friction).** **PeerDB → ClickPipes Postgres
CDC.** ClickHouse acquired PeerDB (July 2024) and the **Postgres-CDC connector in ClickPipes
reached GA in May 2025** **[VERIFIED via search]**, now replicating 200+ TB/month from 400+
companies. So the bridge from CARDEEP's Postgres to a ClickHouse serving replica is a
**managed, GA, logical-replication CDC pipeline** — not a bespoke ETL. CARDEEP's
append-only `vehicle_event` log is an *ideal* CDC source (inserts only, no in-place
mutation of history). This makes Tier 2 a **clean, reversible bolt-on**, not an architecture
rewrite.

**The concrete trigger to adopt Tier 2 (write it down so it's not a vibe):**
- delta-firehose / grid p95 latency exceeds the SLA on partitioned PG *after* pg_duckdb, **or**
- sustained analytical concurrency enters the hundreds, **or**
- active analytical dataset crosses ~hundreds of GB.
Until one of those is *measured*, ClickHouse is **deferred** — adopting it now would double
the datastore ops (two engines, CDC lag, schema drift between them) for a workload three
orders of magnitude below its break-even. **[ASSUMED]** none of these triggers is hit at
v1/near-term volume.

**Sample config (the CDC bridge, only at the trigger — ClickPipes-side):**
```sql
-- ClickHouse side: a ReplacingMergeTree mirror of the append-only event log, fed by ClickPipes CDC.
CREATE TABLE vehicle_event_olap (
  event_ulid String, vehicle_ulid String, entity_ulid String,
  province_code FixedString(2), event_type LowCardinality(String),
  old_value String, new_value String, observed_at DateTime64(3)
) ENGINE = ReplacingMergeTree
ORDER BY (province_code, observed_at, event_ulid);   -- columnar, province+time ordered for the firehose/grid
-- Postgres side: wal_level=logical + a publication on vehicle_event; ClickPipes consumes it.
```

### 5.4 TimescaleDB — **REJECTED for the core, narrow fallback** 🟡
- **Repo:** https://github.com/timescale/timescaledb — **[VERIFIED]** 22,880★, not archived,
  **last pushed 2026-06-12**. **Latest v2.27.2, 2026-06-02** **[VERIFIED via GitHub API]**;
  PG18 support since 2.23, PG15–18 supported (PG15 dropping ~June 2026)
  **[VERIFIED via search/tigerdata changelog]**. Vendor rebranded to **Tiger Data**.
- **Alive?** ✅ Very — but **license is TSL (Timescale License), not OSI** (`license:
  "NOASSERTION"` on the repo **[VERIFIED via API]**); the community edition's
  compression/continuous-aggregates are under TSL, not Apache-2. This matters for a
  self-hosted, redistributed CARDEEP image.

**Why rejected for CARDEEP's core.** TimescaleDB's headline features — **hypertables**
(automatic time-based chunking) and **continuous aggregates** — *overlap with what CARDEEP
already built natively*: the `vehicle_event` log is **already** month-range-partitioned by
hand (`§5.1`), and the `/stats` rollups are **already** materialized views (`0012`).
Adopting Timescale would mean **re-homing the event log into a hypertable** (replacing the
hand-tuned, working partition scheme), pulling in a **heavy C extension under a non-OSI
license**, for benefits (auto-chunking, native compression, continuous aggregates) that the
**native partitioning + pg_partman + pg_duckdb** stack already covers with **in-core,
OSI-clean, lower-mass** components. The KISS/YAGNI call is clear: **the native scheme wins**.
**Fallback only** if native partition management + pg_duckdb ever prove insufficient *and*
the TSL license is acceptable *and* the team wants Timescale's columnar compression on the
cold event tail specifically — a narrow, unlikely corner.

### 5.5 pg_mooncake — **WATCH, not v1** 🟡
- **Repo:** https://github.com/Mooncake-Labs/pg_mooncake — **[VERIFIED]** 1,975★, not
  archived, **last pushed 2026-03-31** but **last commit on `main` 2025-10-26** ("Support
  Postgres 18"); **latest tag v0.1.3** (release list shows v0.1.0–v0.1.2; tags include
  v0.1.3) **[VERIFIED via GitHub API + branch/tag listing]**.
- **Alive?** 🟡 **Borderline.** The default branch hasn't advanced since **2025-10-26**
  (~8 months) — inside the 12-month *commit* bar but cooling, and **no v0.2/1.0 tag exists**.
  Sub-v1, explicitly early-stage. In Sept 2025 it **became a subextension of pg_duckdb**.

**What it solves.** A **columnstore mirror** of Postgres tables in **Apache Iceberg** with
sub-second freshness, queryable as normal Postgres tables, analytics accelerated by DuckDB
(via pg_duckdb), and the Iceberg data readable by external engines — a "lakehouse in
Postgres." **[VERIFIED via README/search.]**

**Why watch, not adopt.** Genuinely interesting for a future where CARDEEP wants its delta
log as an open Iceberg lakehouse readable by Spark/Trino/DuckDB without CDC. But it is
**sub-v1, the branch has been quiet since Oct 2025, and its value (Iceberg interop) is a
*nice-to-have* CARDEEP has not asked for**. For pure in-Postgres OLAP acceleration,
**pg_duckdb alone (§5.2) is the more mature, more active path** — pg_mooncake's extra layer
(Iceberg mirror) only pays off for cross-engine lakehouse access. **Re-evaluate when it tags
v0.2/1.0 and the branch reactivates.** Not a v1 dependency.

---

## 6. Horizontal scale-out — Citus (documented exit ramp, not a v1 need)

- **Repo:** https://github.com/citusdata/citus — **[VERIFIED]** 12,559★, not archived,
  **last pushed 2026-06-10**. **Latest v14.0.0, 2026-02-17**, brings **PostgreSQL 18.1
  support** (13.x added PG17) **[VERIFIED via GitHub releases]**. Microsoft-maintained.
- **Alive?** ✅ Yes — the post-acquisition slowdown narrative is **outdated**: v14.0 in
  Feb 2026 with PG18 support and a push 4 days before this audit prove active maintenance.

**What it solves & why deferred.** Citus shards a Postgres table across a cluster (a
coordinator + workers), turning single-node Postgres into a distributed OLTP/HTAP system.
CARDEEP is **single-node-sized for the foreseeable future** (sub-1 GB today; tens of
millions of rows partitioned by province/month is still comfortably single-node on modern
hardware). Sharding adds a coordinator, cross-shard query complexity, and ops mass that the
volume does not justify (**YAGNI**). It is the **documented exit ramp** if CARDEEP ever
(a) outgrows a single node's write throughput or (b) needs to co-locate by province across
nodes — but that is a *much* later, *much* larger-scale concern than the analytics tiers
above. **Not a v1 dependency; on record as the scale-out path if single-node is ever the
wall.**

---

## 7. Is the current CARDEEP choice good enough? — final answer

**Current choice: single-node, partitioned PostgreSQL 16.14. Verdict: YES, good enough —
with two concrete, low-risk improvements.**

1. **Upgrade to PostgreSQL 18** (17 as the conservative interim). Free, direct wins on
   CARDEEP's exact hot paths: AIO (~3× faster scans/VACUUM), skip-scan on the composite
   indexes, better partition pruning/joins, and retained planner stats that de-risk the
   `pg_upgrade` itself. Gate the upgrade on the extension PG18-build check (all clear:
   partman/cron/trgm/postgis ✅) and an asyncpg-vs-PG18 smoke test.
2. **Adopt pg_partman + pg_cron** to automate the `vehicle_event` monthly-partition
   lifecycle (premake + 24-month detach-retention), replacing the hand-rolled cron in
   `§8.3` with a battle-tested extension. Leave the **static province-LIST partitions** as
   plain declarative DDL (they don't roll, so they don't need partman).

**Everything else stays as designed and is correct:**
- **pg_trgm + btree_gin** for fuzzy/faceted search — in-core, bulletproof, keep.
- **lat/lon + composite btree + Haversine** for geo — correct given PostGIS isn't in the
  image; **PostGIS 3.6** is the clean gated add (`0099`) only when radius/density queries
  are actually needed.
- The **hybrid OLTP+OLAP need is real but satisfied inside Postgres** at CARDEEP's scale
  (partitioned tables + `enable_partitionwise_aggregate` + materialized rollups).

**The deferred-behind-a-trigger escalation order (write it down, don't guess):**
- **Tier 1 — pg_duckdb** (in-process vectorized OLAP over the same tables) the *moment*
  native aggregation measurably strains. Lowest cost, no second datastore.
- **Tier 2 — ClickHouse** as a **read-only, CDC-fed serving layer** (via the GA
  **PeerDB→ClickPipes** Postgres CDC) only at a measured trigger (>~hundreds of GB active
  / hundreds of concurrent analytical queries / SLA miss after pg_duckdb). Never the OLTP
  store.
- **Citus** as the single-node-write-wall exit ramp, far later if ever.

**Explicitly rejected / deferred (no corpses, but no premature adoption):**
- **TimescaleDB** — alive (2.27.2) but **rejected for the core**: its hypertable +
  continuous-aggregate value overlaps CARDEEP's *already-built* native month-partitioning +
  materialized rollups, while adding a heavy extension under a **non-OSI (TSL) license**.
  Narrow fallback only.
- **pg_mooncake** — alive but **sub-v1 with a branch quiet since 2025-10** and Iceberg
  interop CARDEEP hasn't asked for; pg_duckdb is the more mature in-PG OLAP path. **Watch**,
  re-evaluate at v0.2/1.0.
- **No dead corpses recommended.** Every tool above has a verified 2026 (or late-2025)
  release/commit; the two with stale *tags* (pg_mooncake v0.1.3, pg_cron 1.6.7) were checked
  at the **branch** level and the distinction stated.

**Image manifest delta (the total concrete change):**
```dockerfile
FROM postgres:18
RUN apt-get update && apt-get install -y --no-install-recommends \
      postgresql-18-partman postgresql-18-cron \
  && rm -rf /var/lib/apt/lists/*
# shared_preload_libraries = 'pg_cron'; cron.database_name = 'cardeep'
# extensions to CREATE: pg_trgm, btree_gin, pgcrypto (already planned in 0005) + pg_partman, pg_cron
# pg_duckdb / postgis / clickhouse: added only at their documented triggers — NOT now.
```

---

## 8. Source ledger (all [VERIFIED] = fetched this session via GitHub API / release page / docs unless noted)

**Core engine**
- PostgreSQL 18 released 2025-09-25: https://www.postgresql.org/about/news/postgresql-18-released-3142/
- PostgreSQL 18.4 (2026-05-14) release notes: https://www.postgresql.org/docs/release/18.4/
- PG18 AIO / skip-scan / partition pruning / retained stats *(release notes + search)*: https://www.postgresql.org/docs/release/18.0/ · https://www.crunchydata.com/blog/get-excited-about-postgres-18
- PG18 Extension Bugs wiki *(via search)*: https://wiki.postgresql.org/wiki/PostgreSQL_18_Extension_Bugs
- PG17 partition pruning / 1B-row latency *(via search)*: https://johal.in/deep-dive-postgresql-17-partitioning-optimize-queries-1b/

**Partition automation**
- pg_partman v5.4.3 (2026-03-05), 2.7k★, pushed 2026-03-09 *(GitHub API)*: https://github.com/pgpartman/pg_partman + https://github.com/pgpartman/pg_partman/releases
- pg_partman 5.4.2 control-file regression / 5.4.3 fix *(via search)*: https://nerdleveltech.com/pg-partman-pg-cron-postgres-18-partition-automation-tutorial
- pg_cron v1.6.7 (2025-09-04), 3.8k★, pushed 2026-04-21, PG18-tested *(GitHub API + search)*: https://github.com/citusdata/pg_cron
- managed-Postgres shipping partman/cron *(via search)*: https://planetscale.com/changelog/postgres-extensions-pg-cron-partman-bgw

**Search & geo**
- pg_trgm in-core *(CARDEEP `pg_available_extensions`, repo-local)*: `docs/architecture/03-DATA-MODEL.md`
- PostGIS 3.6.2/3.6.3 (2026), PG14–18 *(via search)*: https://postgis.net/documentation/getting_started/install_windows/released_versions/ · https://postgis.net/docs/release_notes.html

**Hybrid OLAP**
- pg_duckdb v1.1.1 (2025-12-18, per API `published_at`), 3.1k★, pushed 2026-03-16 *(GitHub API)*: https://github.com/duckdb/pg_duckdb + https://github.com/duckdb/pg_duckdb/releases
- ClickHouse v26.4.4.38 (2026-06-08), 48k★, pushed 2026-06-12 *(GitHub API)*: https://github.com/ClickHouse/ClickHouse/releases
- ClickHouse "choose a DB for real-time analytics 2026" (>500 GB threshold, augmentation pattern): https://clickhouse.com/resources/engineering/how-to-choose-a-database-for-real-time-analytics-in-2026
- ClickHouse fastest-OLAP-2026 (ClickBench): https://clickhouse.com/resources/engineering/fastest-olap-databases
- PeerDB acquisition + ClickPipes Postgres CDC GA (May 2025) *(via search)*: https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database · https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-ga
- TimescaleDB v2.27.2 (2026-06-02), 22.9k★, pushed 2026-06-12, TSL license *(GitHub API)*: https://github.com/timescale/timescaledb
- TimescaleDB 2.22/2.23 PG18 support + PG15 EOL June 2026 *(via search)*: https://www.tigerdata.com/blog/timescaledb-2-22-2-23-90x-faster-distinct-queries-postgres-18-support-configurable-columnstore-indexes-uuidv7 · https://www.tigerdata.com/docs/about/latest/changelog
- pg_mooncake tag v0.1.3, last `main` commit 2025-10-26, 2.0k★, subextension of pg_duckdb *(GitHub API + branches/tags + README)*: https://github.com/Mooncake-Labs/pg_mooncake

**Scale-out**
- Citus v14.0.0 (2026-02-17), PG18.1 support, 12.6k★, pushed 2026-06-10 *(GitHub API + releases)*: https://github.com/citusdata/citus/releases

**CARDEEP incumbent (read this session, repo-local)**
- `docs/architecture/03-DATA-MODEL.md` (PG16.14, no PostGIS, province-LIST + month-RANGE partitioning, pg_trgm GIN, asyncpg, maintenance jobs §8.3, rollup views 0012, PostGIS gated add §10.4)
