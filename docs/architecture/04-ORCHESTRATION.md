# CARDEEP — 04 · The Orchestration & Control Plane

> **Pillar doc.** The permanent machine that drives Cardeep: how every car
> point-of-sale in Spain gets discovered, drained of its full stock, verified by an
> independent path, geo-placed, code-stamped, served live with delta, and kept alive
> when a source breaks — **without artisanal per-source work and without the engine
> ever falling.** This is the control plane: the systems (`S-*`), the two execution
> planes (deterministic Python vs intelligence fleets), the job/queue substrate
> (Redis Streams, at-least-once, idempotent by `cdp_code`), the worker-fleet model,
> the **rate-governor** that is the true bottleneck, the anti-collision contract, the
> cost-router (local vs cloud, model tier per task), and the scheduler.
>
> **Supersedes** the first-pass orchestration in `docs/ORQUESTACION.md` and the
> workflow sketch in `docs/workflows/README.md`. It is the operational spine that
> *invokes* the fetch engine of `02-SCRAPING-ENGINE.md`, writes the entities/kinds of
> `01-ENTITY-ONTOLOGY.md`, attacks the platforms of `00-TIER1-REGISTRY.md`, and
> lands everything in the data layer of `docs/ARCHITECTURE.md` (`migrations/0001-0004`).
>
> **Marking discipline.** Every claim is **[VERIFIED]** (read from repo/DB/live this
> session) or **[ASSUMED]** (design intent, inferred, to be proven on build). No
> placeholders, no stubs, no TODOs. Code and identifiers in English.
>
> **Anchor reality, read before designing** (all read this session):
> `pipeline/discover.py`, `pipeline/ingest.py`, `pipeline/verify.py`,
> `pipeline/harvest_dealer.py`, `pipeline/ids.py`, `services/api/codes.py`,
> `migrations/0004_verification_health.sql`, `PROGRESO.md`, `CLAUDE.md`.

---

## 0. The wall this plane exists to break

The live system already works as a **set of scripts**. As of 2026-06-12 the running
DB holds **12.814 entities** (garaje 7200 · compraventa 2753 · concesionario_oficial
1569 · desguace 1292) and **~22.300 vehicles** across **212 harvested dealers**, every
count carrying a VAM verdict. `[VERIFIED, PROGRESO.md]` That is real and it is a floor
to build on — but it was produced by **hand-launched runs** (`python -m pipeline.discover`,
`python -m pipeline.harvest_dealer <slug>`, ad-hoc batch workers). `[VERIFIED:
discover.py / harvest_dealer.py are `__main__` CLIs]` Two failures of that mode are
already in the log and are exactly what this plane removes:

1. **The harvest is the bottleneck, and it is uncontrolled.** "138 dealers cayeron por
   throttling de AS24 bajo carga 4×" — four naïve parallel workers against one source
   tripped its rate limiter and lost 138 dealers. `[VERIFIED, PROGRESO.md]` The
   conclusion is written in the log itself: *"La cosecha es el cuello (rate-limit de
   fuente), no el sistema."* The plane's first job is a **per-source rate-governor**:
   parallelism is scaled **across sources**, never **within** one past its safe rate.

2. **No permanent loop, no self-repair, no scheduler.** `S-HEALTH` exists only as
   tables (`source_health`, `alert`) — "F7 (tabla lista)". `[VERIFIED,
   migrations/0004 + ORQUESTACION.md]` Nothing writes them on a cadence, nothing
   re-runs a `GONE`-spiking source, nothing fires the exact-origin alert the mandate
   demands. A script that must be re-launched by a human is not *"Cardeep no se cae."*

The control plane converts the proven scripts into **idempotent jobs on a durable
queue**, driven by a **scheduler**, executed by **fleets governed per-source**,
guarded by a **health watchdog with auto-repair**, and **cost-routed** so the massive
cheap work never touches a paid model and the expensive intelligence only decides.

---

## 1. Doctrine (the seven laws of the control plane)

Priority order; on conflict, lower number wins.

1. **TWO PLANES, ONE TRUTH (`main` + PostgreSQL).** The *deterministic plane* (Python
   `pipeline/`, local LLM via Ollama) does everything massive and cheap: discover,
   scrape, parse, classify, dedup, geo-resolve, ingest, verify-by-count. The
   *intelligence plane* (agent fleets) does only what needs a brain: hunt Tier-1
   recipes, disambiguate hard identity, run adversarial verification. Cost follows
   capability, never the reverse. `[VERIFIED mandate, CLAUDE.md "modelos LLM locales
   para lo masivo … la inteligencia cara, solo para decidir"]`

2. **THE GOVERNOR OUTRANKS THE FLEET.** No job runs against a source faster than that
   source's measured safe rate. Concurrency is a **per-source** token budget, not a
   global worker count. A thousand idle workers waiting on one governed source is
   correct; one extra request that earns a 429 is a bug. (§5 is the whole mechanism;
   §0.1 is the scar that proves it.)

3. **IDEMPOTENT BY `cdp_code` / stable id — re-running NEVER duplicates.** Every job is
   safe to deliver at-least-once. Entity upserts are `ON CONFLICT (cdp_code) DO UPDATE`;
   inventory reconciles by `(entity_ulid, deep_link)`; the delta engine emits events
   only on real mutation. `[VERIFIED: discover.py:67-73, ingest.py:48-60, ingest.py
   delta loop]` This is what makes a durable queue with retries safe.

4. **ANTI-COLLISION BY CONSTRUCTION.** Parallel producers never write the same surface.
   Recipe-building writes one file per source (`pipeline/sources/<key>.py` /
   `countries/ES/recipes/<key>.yaml`); **all DB writes funnel through the ingest
   worker family keyed by `cdp_code`**, so two workers touching the same entity
   serialize on the row, never race. `[VERIFIED: the upsert pattern already serializes
   on the unique `cdp_code`]` (§6.)

5. **VERIFY BY AN ORTHOGONAL PATH, ALWAYS.** No count is trusted because the job that
   produced it said so. Every consequential number re-derives through ≥2 independent
   paths and lands a `verification_verdict`; the *primary* path (what actually hit the
   DB) must agree, or the verdict is `REFUTED`. `[VERIFIED: verify.py quorum +
   primary_agrees rule]` The Inquisition (§9) is a *separate* fleet that re-derives
   counts by a method the producer never used.

6. **SELF-HEAL OR ESCALATE — NEVER SILENTLY DRIFT.** A source that fails, drifts
   (field-null spike, count collapse, `GONE` storm), or hits a new wall files an
   `alert` with the **exact origin** (`source_key` / `cdp_code` / phase), updates
   `source_health`, and triggers an automatic repair attempt (re-route tier, re-hunt
   recipe, back off and retry). Only an unrepairable wall parks the source for the
   owner — and it parks with the *exact* wall named, never faked. `[VERIFIED mandate
   "salta una alerta con el origen exacto, se auto-repara"]` (§8.)

7. **EVERYTHING TO `main`, EVERYTHING REPRODUCIBLE.** Recipes, schedules, governor
   profiles, spend ledger, and run state are committed or persisted; the raw crude is
   ephemeral (gitignored `data/`) and reconstructable from the recipe. State lives on
   disk/DB, never only in a worker's memory. `[VERIFIED mandate "todo a GitHub (main)
   … nada se pierda y cualquiera pueda retomarlo"; harvest_dealer.py dumps raw to
   gitignored `data/`]`

---

## 2. The two planes and where each system lives

```
┌───────────────────────────── CONTROL PLANE (this doc) ──────────────────────────────┐
│                                                                                      │
│  SCHEDULER (§10)  ──emits jobs──▶  REDIS STREAMS (§4)  ──consumed by──▶  FLEETS (§7)  │
│      cadences          DISCOVER · HARVEST · RECIPE · INGEST · VERIFY · HEAL · GEO     │
│         │                    │  every job idempotent by cdp_code / stable id   │      │
│         │                    ▼                                                 ▼      │
│         │            RATE-GOVERNOR (§5) ◀──one token bucket per source────── workers  │
│         │              (THE bottleneck; gates every outbound fetch)                   │
│         ▼                                                                             │
│   COST-ROUTER (§3) — decides per task: deterministic | local-LLM | cloud-agent       │
│                                                                                      │
├──────────────── DETERMINISTIC PLANE ────────────┬──────── INTELLIGENCE PLANE ────────┤
│  pipeline/ (Python) + Ollama (local LLM)         │  agent fleets (Workflow tool)      │
│   • S-DISCOVER  source adapters → entities        │   • WF-TIER1-HUNT  recipe-cazadores│
│   • S-INVENTORY harvest → recipe → ingest(delta)  │   • WF-INQUISITION adversarial VAM │
│   • S-VERIFY    count quorum (VAM)                │   • WF-IDENTITY    hard dedup calls │
│   • S-GEO       INE name→code backbone            │  (cara; SOLO decide y caza)        │
│   • S-CODE      cdp_code immutable mint           │                                    │
│   • S-HEALTH    watchdog + auto-repair            │                                    │
│  (barato; €0; escala lineal)                      │                                    │
└──────────────────────────────────┬───────────────┴────────────────────────────────────┘
                                    ▼
                  PostgreSQL cardeep-pg :5433  +  FastAPI live API (S-API)
                  (entity · vehicle · vehicle_event · verification_verdict ·
                   source_health · alert — migrations 0001-0004, VERIFIED)
```

**Plane assignment is the cost contract (law #1 + §3).** A task lands in the
deterministic plane unless it provably needs a brain. The intelligence plane is
invoked *only* by two triggers: (a) a Tier-1 source whose data-layer recipe is unknown
(`WF-TIER1-HUNT`), and (b) a consequential count that must be refuted by a fresh
independent method (`WF-INQUISITION`). Everything else — including parsing, classifying
`kind`, and deduping — runs deterministic + Ollama at €0.

---

## 3. The cost-router (local vs cloud, model tier per task)

The router decides, **per unit of work**, the cheapest executor that can do it
correctly. It is the mechanization of the mandate's spend doctrine.

### 3.1 Routing table (task → executor → why)

| Task | Executor | Model / engine | Cost | Rationale |
|---|---|---|---|---|
| Fetch a JSON/sitemap/SSR surface | deterministic | `curl_cffi` (Tier-0) | €0 | §02 law: data layer, no brain needed |
| Parse a typed field-map | deterministic | recipe JSON-path | €0 | structure is deterministic |
| Classify entity `kind` (concesionario / compraventa / garaje / desguace / rent-a-car) | local-LLM | **Ollama** (e.g. `qwen2.5:7b`/`llama3.1:8b`) | €0 | fixes the `ingest.py:52` mis-typing bug `[VERIFIED, 01-ENTITY-ONTOLOGY §0.1]`; massive + cheap → local |
| Dedup / canonicalize a noisy name vs alias set | local-LLM | Ollama | €0 | massive, fuzzy, no external truth |
| Geo-resolve name→INE code | deterministic | `GeoResolver` | €0 | exact dictionary lookup `[VERIFIED, geo.py]` |
| Mint `cdp_code` | deterministic | `codes.py` | €0 | pure function `[VERIFIED]` |
| Count-quorum VAM | deterministic | `verify.py` | €0 | arithmetic `[VERIFIED]` |
| **Hunt a Tier-1 data-layer recipe** (hard wall) | **cloud-agent** | Opus-class fleet | €€ | needs reasoning + tool exploration; one giant per agent |
| **Adversarial re-derivation** of a key count | **cloud-agent** | Sonnet/Opus | €€ | independence requires a fresh method |
| Hard identity call (is branch X the same firm as Y?) | **cloud-agent** | Sonnet | € | only when deterministic dedup is ambiguous |

### 3.2 Escalation ladder (cheap first, evidence to climb)

```
deterministic  ──can't (fuzzy/semantic)──▶  local-LLM (Ollama)  ──can't (needs
   reasoning + live tool exploration + a real wall)──▶  cloud-agent (spend-gated)
```

Each rung is tried before the next, and a climb must be *justified by a typed signal*,
never by default. Mirrors the fetch ladder of `02-SCRAPING-ENGINE.md §1 law 2` (cheapest
tier that works) — the cost-router is that doctrine applied to *cognition*, the
rate-governor applies it to *throughput*, and the fetch router applies it to *transport*.
Three routers, one principle: **spend the minimum that is correct.**

### 3.3 Local-LLM service contract

Ollama runs as a local sidecar (HTTP `:11434`). The deterministic plane calls it
through one narrow client (`pipeline/llm/local.py`, to build) with a **strict JSON
schema** per task and a **deterministic fallback** when the model is unsure:

```python
class LocalLLM(Protocol):
    def classify_kind(self, entity: EntityFeatures) -> KindVerdict: ...   # → {kind, confidence}
    def canonical_name(self, raw: str, aliases: list[str]) -> NameVerdict: ...
# Contract: temperature 0, JSON-mode, schema-validated. confidence < THRESHOLD
# (e.g. 0.7) → keep the deterministic guess + flag for the Inquisition, never block.
```

**Cost ledger (shared with §02 spend gate).** Every cloud-agent invocation and every
Tier-2 fetch writes `{task, executor, units, est_cost, ts}` to `state/spend-ledger.json`.
A per-front budget cap trips an `alert` before overspend. Local-LLM and deterministic
work cost €0 and are not metered for spend (only for latency/governor accounting).

---

## 4. Job & queue model (Redis Streams, at-least-once, idempotent)

### 4.1 Why Redis Streams (not a list, not Celery, not Kafka)

- **Durable, replayable log with consumer groups + per-message ACK.** `XADD` appends;
  `XREADGROUP` delivers to exactly one consumer in a group; `XACK` confirms; unacked
  messages sit in the **Pending Entries List (PEL)** and are reclaimed by `XAUTOCLAIM`
  after a crash. This gives **at-least-once delivery with crash recovery** out of the
  box. `[VERIFIED: Redis Streams semantics — consumer groups, PEL, XAUTOCLAIM]`
- **At-least-once is *safe here* because every job is idempotent by `cdp_code`/stable
  id (law #3).** A redelivered DISCOVER or HARVEST re-runs to the same DB state; the
  delta engine emits no spurious events on a re-run (proven: "re-run new=0, gone=0, 78
  unchanged" `[VERIFIED, PROGRESO.md F3]`). We therefore do **not** need exactly-once.
- **Already in the stack.** CARDEX (sibling project) runs PostgreSQL+Redis; Redis is a
  known, operated dependency for this owner. `[VERIFIED, MEMORY/cardex-pipeline]`
  Cardeep gets its **own** Redis instance (separate port/namespace), never shared.
- **Lighter than Kafka, more durable than a Redis list / pub-sub**, and it keeps the
  whole transport inside one already-present service. YAGNI says no broker cluster
  until a stream's throughput proves it needs one.

### 4.2 The streams (one per job kind)

| Stream | Producer | Consumer group | Payload (idempotency key) |
|---|---|---|---|
| `cdp:discover` | scheduler | `discover-workers` | `{source_key}` |
| `cdp:harvest` | scheduler / discover | `harvest-workers` | `{source_key, dealer_ref}` → `cdp_code` |
| `cdp:recipe.hunt` | router (Tier-1) | `recipe-fleet` (agents) | `{source_key}` |
| `cdp:ingest` | harvest workers | `ingest-workers` | `{cdp_code, harvest_ref}` |
| `cdp:verify` | ingest / scheduler | `verify-workers` | `{subject_type, subject_key}` |
| `cdp:inquisition` | scheduler / health | `inquisition-fleet` (agents) | `{subject_key, claim}` |
| `cdp:geo.backfill` | ingest (province-miss) | `geo-workers` | `{entity_ulid}` |
| `cdp:heal` | health watchdog | `heal-workers` | `{source_key, fault}` |

Discover and ingest are **split** (they are split today: `discover.py` for entities,
`ingest.py` for inventory `[VERIFIED]`). Harvest produces a raw artifact ref; ingest
consumes it and owns *all* DB writes for an entity — the anti-collision funnel (§6).

### 4.3 Job envelope (canonical schema)

```json
{
  "job_id": "01J...ULID",          // ULID, time-ordered (pipeline/ids.py, VERIFIED)
  "kind": "harvest",
  "idempotency_key": "as24:ok-mobility-valencia-airport",
  "cdp_code": null,                 // filled once known; the cross-plane join key
  "source_key": "as24",
  "payload": { "dealer_ref": "ok-mobility-valencia-airport" },
  "attempt": 1,
  "max_attempts": 5,
  "not_before": "2026-06-12T15:20:00Z",  // governor/backoff release time
  "trace_id": "01J...ULID",         // links all jobs of one logical unit (dealer E2E)
  "enqueued_at": "2026-06-12T15:19:50Z"
}
```

`job_id` and `trace_id` reuse the existing ULID minter (`pipeline/ids.py` `[VERIFIED]`)
— time-ordered, so the stream and the trace are naturally chronological.

### 4.4 Delivery lifecycle (at-least-once with bounded retry)

```
XADD cdp:harvest → worker XREADGROUP (claims, enters PEL)
   → governor.acquire(source_key)               # may block; THE throttle (§5)
   → run job (idempotent)
       success → XACK  (leaves PEL)             # done, exactly-once *effect* by idempotency
       transient fail (504, 429, timeout)
            → attempt<max → XADD with not_before=now+backoff(attempt) ; XACK original
            → attempt==max → route to cdp:heal + alert(origin=source_key) ; XACK
       crash before ACK → message stuck in PEL
            → reaper XAUTOCLAIM after idle_timeout → redelivered (safe: idempotent)
```

- **Backoff** is exponential + jitter, seeded by the governor's observed health for the
  source (a source already throttling gets a longer base). This generalizes the
  ad-hoc "retry+backoff en fetch_page" that already recovered transient 504s.
  `[VERIFIED, PROGRESO.md]`
- **`not_before`** lets a job be re-enqueued *deferred* without a separate delay queue:
  workers skip-and-requeue (or a single delayed-set in Redis `ZADD score=not_before`
  feeds a promoter) any job whose `not_before` is in the future. This is how a
  governed source's surplus demand parks cheaply.
- **Poison-job guard:** a job that fails `max_attempts` is **never dropped** — it goes
  to `cdp:heal` (auto-repair) and, if unrepairable, to a dead-letter stream
  `cdp:dead` + a `critical` alert. Nothing is lost silently (law #6/#7).

---

## 5. The rate-governor — the real bottleneck, mechanized (law #2)

This is the most important subsystem in the plane. The scar is explicit: **4× naïve
concurrency against AutoScout24 lost 138 dealers to throttling.** `[VERIFIED,
PROGRESO.md]` The governor makes that structurally impossible.

### 5.1 One token bucket per source, shared across all workers

```
                          ┌──────────────── RATE-GOVERNOR (Redis-backed) ───────────────┐
worker A ─acquire(as24)─▶ │  bucket[as24]   rate=R_as24/s  burst=B_as24  concurrency=C   │
worker B ─acquire(as24)─▶ │  bucket[kia]    rate=R_kia/s   ...                           │
worker C ─acquire(coches)▶│  bucket[coches] ...                                          │
                          │  token = Redis atomic (Lua) GCRA/token-bucket per source_key │
                          └──────────────────────────────────────────────────────────────┘
```

- **Distributed, atomic, source-scoped.** The bucket lives in Redis (one key per
  `source_key`), refilled by a **GCRA / token-bucket Lua script** run atomically — so
  N workers on M machines share *one* global rate per source. A worker calls
  `governor.acquire(source_key)`; it returns a token (proceed) or a `retry_after`
  (re-enqueue with `not_before`). No worker ever bypasses it: **the governor wraps the
  fetch engine of `02-SCRAPING-ENGINE.md`, every outbound request passes through it.**
- **Per-source, not global.** Parallelism scales by adding *sources*, never by raising
  one source's rate past safe. Draining AS24, Kia portals, coches.com sitemap, and OSM
  *simultaneously* is correct; running 4 AS24 workers flat-out is the banned pattern.
  This is the corrected throughput model the log demands: *"escala por nº de fuentes en
  paralelo."* `[VERIFIED, PROGRESO.md]`

### 5.2 The governed knobs (per source, in the recipe + governor profile)

```yaml
# governor profile, committed: countries/ES/governor/<source_key>.yaml
source_key: as24
rate_per_sec: 1.5            # safe steady request rate (tuned from 429 telemetry)
burst: 5                     # bucket depth
max_concurrency: 2           # in-flight cap per source (the "no 4×" rule, hard)
min_delay_ms: 250            # floor between requests + jitter
backoff_on_429: 4.0         # multiply base backoff when the source throttles
cooldown_on_block_sec: 900   # full pause after a hard block, then probe
sticky_session_ttl_sec: 600  # one fingerprint/session window (§02 law #3 coherence)
```

`max_concurrency` is the hard expression of law #2: **the governor caps in-flight
requests per source below the rate that earned the ban.** AS24's profile is born at
`max_concurrency: 2` precisely because `4×` failed. `[VERIFIED, PROGRESO.md]`

### 5.3 Adaptive governance (AIMD — self-tuning the rate)

The governor is not static; it **learns each source's true ceiling** with an
Additive-Increase / Multiplicative-Decrease loop on observed signals:

```
on success window (no 429/403/challenge for N requests)  → rate += additive_step   (probe up)
on 429 / 403 / soft-challenge                            → rate *= 0.5 ; concurrency-= 1  (back off hard)
on hard block (Akamai/DataDome wall)                     → cooldown_on_block_sec ; alert ; tier-bump
```

This couples directly to `02-SCRAPING-ENGINE.md §8` (a fingerprint-correlated
challenge-rate rise bumps the tier) — a *challenge spike* is both a governor "back off"
signal and a router "escalate tier" signal. The governor writes its current learned
rate back to the profile (committed) so the next campaign starts at the right ceiling,
exactly as the recipe self-tunes its tier (§02 §9.4).

### 5.4 What the governor protects against, concretely

| Threat | Governor mechanism |
|---|---|
| 4× over-concurrency ban (the scar) | `max_concurrency` hard cap per source |
| Thundering herd on schedule tick | tokens shared globally → fleet can't burst past `rate_per_sec` |
| One bad source starving others | per-source buckets are independent; AS24 throttling never slows Kia |
| Source silently tightening its limit | AIMD multiplicative-decrease + 429 telemetry into `source_health` |
| Mid-drain IP/fingerprint rotation flag | `sticky_session_ttl_sec` pins one identity per window (§02 law #3) |

---

## 6. Anti-collision contract (parallel safety, mechanized — law #4)

Three rules make unbounded parallelism safe **by construction**, so no distributed lock
is needed on the hot path:

1. **One writer per surface.**
   - *Recipe/adapter builders* (deterministic inference or `WF-TIER1-HUNT` agents) each
     write **one file**: `pipeline/sources/<key>.py` or
     `countries/ES/recipes/<key>.yaml` (Tier-1: `countries/ES/_tier1/<key>.yaml`,
     physically separated `[VERIFIED, ARCHITECTURE.md §Separación Tier-1]`). They never
     touch the DB or `discover.py`. Two builders cannot collide — different files.
   - *Harvest workers* write **only** the ephemeral raw artifact under
     `data/ES/<key>/<dealer_ref>/raw/` (gitignored, per-dealer path → no shared file).
     `[VERIFIED, harvest_dealer.py:38-42]`

2. **All DB writes funnel through the ingest worker family, keyed by `cdp_code`.** A
   single logical owner per entity: the ingest job for `cdp_code` X is the only writer
   of X's `entity`/`vehicle`/`vehicle_event` rows. Even if two harvests of the same
   dealer arrive (at-least-once redelivery, or two sources attesting one entity), they
   serialize on the unique `cdp_code` row via `ON CONFLICT … DO UPDATE` — Postgres
   row-locking does the mutual exclusion. `[VERIFIED: discover.py:67-73, ingest.py:48-60]`
   No application-level lock required.

3. **Multi-source provenance is additive, never destructive.** The same physical entity
   discovered by N sources = **1 `cdp_code`, N `entity_source` rows**
   (`UNIQUE(entity_ulid, source_key)`, `ON CONFLICT DO UPDATE seen_at`). `[VERIFIED:
   discover.py:79-82]` This is the capture-recapture substrate (§9) **and** the dedup
   guarantee in one structure: re-discovery enriches provenance, it never duplicates.

**Sequencing where order matters.** A dealer's E2E (DISCOVER→HARVEST→RECIPE→INGEST→VERIFY)
is a chain of jobs joined by `trace_id`; each stage enqueues the next on success. The
ingest stage is the **only serialization point** and it is per-`cdp_code`, so distinct
dealers run fully parallel while one dealer's stages stay ordered.

---

## 7. The worker-fleet model

A **fleet** is a consumer group on a stream, sized independently. Fleets are
heterogeneous: deterministic Python workers (the majority) and agent workers (rare,
expensive, spend-gated).

### 7.1 Fleet roster

| Fleet | Plane | Reads stream | Sizing rule | Notes |
|---|---|---|---|---|
| `discover-workers` | deterministic | `cdp:discover` | small (I/O-bound, governed) | runs `pipeline/discover.py` logic per source |
| `harvest-workers` | deterministic | `cdp:harvest` | **bounded by Σ source `max_concurrency`**, not by CPU | the governed fleet; size > sources so workers idle-wait, not over-fetch |
| `ingest-workers` | deterministic | `cdp:ingest` | = DB write capacity (pool size) | the single DB-writer funnel (§6.2) |
| `verify-workers` | deterministic | `cdp:verify` | small | runs `verify.py` quorum |
| `geo-workers` | deterministic | `cdp:geo.backfill` | small | lat/lon→province recovery `[VERIFIED, geocode.py]` |
| `heal-workers` | deterministic | `cdp:heal` | small | the auto-repair loop (§8) |
| `recipe-fleet` | **intelligence** | `cdp:recipe.hunt` | 1 agent per Tier-1 giant; spend-gated | `WF-TIER1-HUNT` |
| `inquisition-fleet` | **intelligence** | `cdp:inquisition` | bursty, scheduled | `WF-INQUISITION` adversarial VAM |

### 7.2 The decisive sizing law

> **Worker count is NOT the throughput lever — the governor is.** Adding harvest workers
> past `Σ_sources max_concurrency` only grows the idle-wait pool; it cannot raise
> per-source rate (the governor forbids it). Throughput grows by **(a) more sources in
> parallel** and **(b) more open data-layer surfaces unlocked by recipes/Tier-1 hunts** —
> never by piling workers on one source. This is the corrected model from the scar.
> `[VERIFIED, PROGRESO.md "escala por nº de fuentes en paralelo + recetas Tier-1"]`

So `harvest-workers` is sized *generously* (cheap idle async tasks) precisely so there
is always a worker ready the instant any source's governor releases a token — maximizing
utilization of the **sum** of safe rates while never exceeding **any** single one.

### 7.3 Worker contract (uniform)

Every deterministic worker is the same loop, which is why the existing scripts port
cleanly:

```python
async def worker(stream, group, consumer):
    while True:
        msg = await xreadgroup(stream, group, consumer, block=5000)   # at-least-once claim
        if not msg: await reaper.xautoclaim(stream, group, consumer); continue  # crash recovery
        job = Job.parse(msg)                                          # schema-validated (§4.3)
        if job.not_before > now(): await defer(job); ack(msg); continue
        token = await governor.acquire(job.source_key)               # THE throttle (§5)
        if token.retry_after: await reenqueue(job, after=token.retry_after); ack(msg); continue
        try:
            await HANDLERS[job.kind](job)        # discover/harvest/ingest/verify — existing code
            await source_health.mark_ok(job.source_key)               # §8 watchdog
            ack(msg)
        except Transient as e:
            await backoff_reenqueue(job, e); ack(msg)
        except Permanent as e:
            await route_to_heal(job, e); alert(origin=job.source_key, sev="warning"); ack(msg)
```

Agent workers (`recipe-fleet`, `inquisition-fleet`) wrap the **Workflow tool** instead
of `HANDLERS`, are **spend-gated** (cost-router §3 + ledger), and write their output to
*files* (recipes) or `verification_verdict` rows (Inquisition) — never racing the DB
writers (§6).

---

## 8. S-HEALTH — watchdog, exact-origin alert, auto-repair (law #6)

Today `source_health`/`alert` are empty tables. `[VERIFIED, migrations/0004 + "F7 tabla
lista"]` This is the loop that fills them and makes *"se auto-repara, y Cardeep no se
cae"* real.

### 8.1 Heartbeat (every job result writes health)

Each worker outcome updates `source_health` for its `source_key`:

```
success → last_ok=now, consecutive_fails=0, status='healthy'
fail    → last_fail=now, consecutive_fails+=1
          status = degraded (>=3) | down (>=10)         # thresholds, tunable
```

This is a direct write to the **existing** schema (`source_health.last_ok / last_fail /
consecutive_fails / status` `[VERIFIED, migrations/0004]`) — no new table needed.

### 8.2 Drift detectors (beyond crash — the silent failures)

A source can return `200 OK` and still be broken. The watchdog runs orthogonal drift
checks and **alerts with the exact origin**:

| Detector | Signal | Origin written to `alert.origin` |
|---|---|---|
| Count collapse | declared/fetched drops >X% vs last run | `source_key` |
| `GONE` storm | a harvest marks an abnormal fraction of a dealer's stock `GONE` | `cdp_code` (the dealer) |
| Field-null spike | required field null-rate > recipe `drift_alert_threshold` | `source_key` + field (§02 §9.3) |
| VAM `REFUTED` | quorum disagreement on a count | `subject_key` |
| Challenge-rate spike | 429/403/challenge fraction rises | `source_key` (also bumps tier, §5.3/§02 §8) |
| Governor cooldown | hard block triggered cooldown | `source_key` |

Every alert row carries `payload` JSON with observed-vs-expected, so the origin is not
just *which* source but *what* drifted — the mandate's *"alerta con el origen exacto."*

### 8.3 The auto-repair decision tree (`cdp:heal` consumer)

```
fault arrives on cdp:heal
   ├─ transient (timeout/504/5xx)          → backoff + re-enqueue original job (bounded)
   ├─ 429 / soft-challenge                 → governor multiplicative-decrease + cooldown, then retry
   ├─ new hard wall (Akamai/DataDome/etc.) → re-classify via is-antibot (§02 §3);
   │                                          tier-bump recipe; if Tier-2 & unauthorized →
   │                                          PARK with exact wall (§8.4), do NOT fake
   ├─ recipe drift (field-null / schema)   → enqueue cdp:recipe.hunt (re-derive recipe N+1);
   │                                          long-tail = deterministic re-infer, Tier-1 = agent
   ├─ GONE storm                            → quarantine the harvest (don't apply the destructive
   │                                          delta), re-harvest once; if confirmed, apply; else alert
   └─ unrepairable after N cycles           → dead-letter + critical alert + park for owner
```

The `GONE`-storm quarantine is a **data-integrity guard**: a source glitch that returns
an empty/partial result would otherwise make the delta engine mark a dealer's entire
real stock `GONE` (false bajas). The watchdog refuses to apply a destructive delta that
exceeds a sanity bound until a second harvest confirms it — protecting the mandate's
"delta correcto" against source flakiness.

### 8.4 Parking (the honest wall)

A source needing Tier-2 without owner spend-authorization is parked in
`state/tier1-blocked.json` with the **exact** wall — *"Akamai `_abck`, sensor_data v3,
Spanish residential IP required"* — never silently retried, never faked. `[VERIFIED
doctrine, 02-SCRAPING-ENGINE.md §2 Tier-2 hard rule]` This is `S-TIER1`'s *"reporta
método reproducible o el muro exacto que exige gasto."*

---

## 9. S-VERIFY & the Inquisition (orthogonal verification, mechanized — law #5)

Two layers, deliberately separated: cheap inline verification on every job, and an
expensive adversarial fleet on the numbers that matter.

### 9.1 Inline VAM (every job, deterministic, €0)

Every DISCOVER and INGEST already closes with `record_count_verdict` — a quorum of ≥2
orthogonal paths, with the **primary path (what landed in the DB) required to agree** or
the verdict is `REFUTED`. `[VERIFIED: discover.py:115-121, ingest.py:113-118, verify.py
primary_agrees rule]` The control plane's contribution: **route a `REFUTED` verdict
straight to `cdp:heal`** (it is a fault, not a log line) and **escalate a chronically
`UNVERIFIED` subject to the Inquisition** (it lacks a second path — go find one).

### 9.2 The Inquisition fleet (`WF-INQUISITION`, adversarial, spend-gated)

A *separate* chain whose sole job is to **refute**. For a consequential claim (a
source's total, a province's entity count, a flagship dealer's inventory) it re-derives
the number through a method the producer **never used**:

| Producer path | Independent Inquisition path |
|---|---|
| AS24 `__NEXT_DATA__` per-dealer drain | AS24 public JSON-LD count + a coches.net cross-listing of the same dealer |
| OEM JSON API dealer list | the OEM's HTML store-locator sitemap, counted independently |
| DGT CATV registry count | AEDRA association directory cross-check `[VERIFIED, ORQUESTACION.md ROI #1]` |
| OSM long-tail province tally | Overture/FSQ POI count for the same province |

The producing agent **asserts**; the Inquisition agent **refutes**. Agreement within
tolerance → the `verification_verdict` is upgraded to `TRUSTWORTHY` with two genuinely
independent paths recorded; disagreement → `REFUTED` + alert + `cdp:heal`. The whole
system uses the **same `verification_verdict` table** (`subject_type/subject_key/claim/
verifier_paths/independent_values/verdict` `[VERIFIED, migrations/0004]`) — the
Inquisition just supplies the second, hostile path.

### 9.3 Capture-recapture (the universe denominator)

Multi-source provenance (`entity_source`, §6.3) is the substrate for estimating the
**true** universe size: entities seen by source A, by source B, and by both → a
Lincoln-Petersen estimate of the unseen tail. This is how the mandate's *"100% de los
puntos de venta"* gets a measurable denominator instead of a guess — the F1 census
floor (~44k) and ceiling (~50-90k) `[VERIFIED, PROGRESO.md F1]` get closed empirically
as sources overlap accumulate. The estimate itself is a `verification_verdict` subject
the Inquisition audits.

---

## 10. The scheduler (cadences that drive the loop)

The scheduler is the heartbeat: it emits jobs on time so the DB stays *live* (the
mandate's "tiempo real"). It is a deterministic process (a `cron`-driven or
`asyncio`-loop emitter) writing to the streams — **the single producer of scheduled
jobs**, so cadences never double-fire.

### 10.1 Cadence table

| Cadence | Job emitted | Rationale |
|---|---|---|
| **Continuous** | refill `cdp:harvest` from the dealer backlog | the perpetual drain; governor paces it |
| **Hourly** | `cdp:harvest` for high-churn flagship dealers/platforms | fresh delta where stock moves fastest |
| **Daily** | full `cdp:harvest` sweep of all active dealers | every dealer's stock re-reconciled daily → daily delta |
| **Daily** | `cdp:discover` for fast-moving sources (platform new-dealer signups) | catch new entities |
| **Weekly** | `cdp:discover` full sweep (all adapters) | universe refresh + capture-recapture update |
| **Weekly** | `cdp:inquisition` on top-N counts + all `UNVERIFIED` subjects | adversarial audit cadence |
| **~6-weekly** | fingerprint/JA4 re-confirm + `IMPERSONATE_TARGET` check | Chrome release-train rotation (§02 §8) |
| **On `source_health` degraded** | `cdp:heal` | event-driven, not time-driven (§8) |
| **On recipe drift** | `cdp:recipe.hunt` | event-driven re-derivation (§8.3) |

### 10.2 Freshness tiers (not every dealer deserves the same cadence)

Dealers are cohorted by **observed churn** (delta-event rate): a flagship platform
reshuffling stock daily harvests daily/hourly; a mountain garage with three cars that
hasn't changed in a month harvests weekly. This concentrates the *governed, scarce*
harvest budget where the delta is real — maximizing "tiempo real" fidelity per request
spent. The churn metric comes free from `vehicle_event` counts per entity. `[VERIFIED:
vehicle_event is the append-only delta log, migrations/0003]`

### 10.3 Eviction (BORRAR — the owner's explicit phase)

The mandate names a `BORRAR` phase: *"eliminamos por capacidad del PC"* — store the
recipe, evict the bulk crude. `[VERIFIED, CLAUDE.md]` The scheduler runs a
**capacity-eviction** job:

- **Recipe is the durable asset; crude is ephemeral.** Raw harvests in `data/`
  (gitignored) are deletable at any time — the recipe regenerates them. `[VERIFIED:
  harvest_dealer.py dumps to gitignored data/]`
- **Eviction policy:** LRU on raw artifacts past a disk high-water mark; the DB
  (entities, vehicles, events, verdicts) is **never** evicted — it is the served
  product. Tombstone (`vehicle.status='gone'`) is logical, not physical: history is
  append-only and never deleted (mandate "historial completo"). `[VERIFIED,
  ARCHITECTURE.md mutation doctrine]`

---

## 11. End-to-end: one dealer through the whole plane (the atom)

The mandate demands *"el END TO END DE CADA DEALER. DESCUBRIR, SCRAPEAR, RECETA, API Y
BORRAR."* `[VERIFIED, CLAUDE.md]` Here is the atom, every stage a governed idempotent
job joined by `trace_id`:

```
[scheduler] ─XADD cdp:discover {source_key=as24}──────────────────────────────────────┐
                                                                                       ▼
[discover-worker]  governor.acquire(as24) → run adapter → upsert entities (cdp_code) ──┐
   for each new/known dealer ─XADD cdp:harvest {source_key=as24, dealer_ref=slug}──────┘
                                                                                       ▼
[harvest-worker]   governor.acquire(as24)  ◀── THE throttle (max_concurrency=2)
   → fetch via §02 engine (Tier-0 curl_cffi, data layer __NEXT_DATA__)
   → facet-partition + stable sort (§02 §7) → raw artifact data/ES/as24/<slug>/raw/
   → classify kind via Ollama (fixes ingest.py:52 mis-typing)  ── §3 cost-router
   ─XADD cdp:ingest {cdp_code, harvest_ref}─────────────────────────────────────────┐
                                                                                     ▼
[ingest-worker]  (sole DB writer for this cdp_code — §6.2)
   → upsert entity + entity_source → delta reconcile (NEW/GONE/PRICE/PHOTO/KM)
   → inline VAM quorum → if REFUTED ─XADD cdp:heal
   ─XADD cdp:recipe {cdp_code}  (persist recipe N to git)  +  ─XADD cdp:verify ───────┐
                                                                                      ▼
[verify-worker / inquisition]  orthogonal re-derivation → verification_verdict
                                                                                      ▼
[S-API]  GET /entities/{cdp_code}/inventory  +  /delta?since=   ◀── served live, VERIFIED contract
                                                                                      ▼
[scheduler BORRAR]  evict raw crude past disk HWM (recipe survives) — DB untouched
```

Every arrow is a durable, idempotent, governed job. A crash anywhere is recovered by
`XAUTOCLAIM`; a redelivery is absorbed by idempotency; a source slow-down is absorbed by
the governor; a break is caught by the watchdog and auto-repaired or honestly parked.
**That is "Cardeep no se cae."**

---

## 12. Mapping S-* systems to this plane (status ledger)

| System | What the plane adds | Status before → after this design |
|---|---|---|
| **S-DISCOVER** | becomes `cdp:discover` jobs + `discover-workers` fleet | working CLI `[VERIFIED]` → scheduled, governed, retried |
| **S-INVENTORY** | `cdp:harvest`→`cdp:ingest` chain; governor; classify-kind via Ollama | working CLI per dealer `[VERIFIED]` → fleet at scale, mis-typing fixed |
| **S-VERIFY / Inquisition** | inline VAM routed on `REFUTED`; `inquisition-fleet` adversarial | inline only `[VERIFIED]` → + separate adversarial chain |
| **S-HEALTH** | heartbeat + drift detectors + `cdp:heal` auto-repair + exact-origin alerts | empty tables `[VERIFIED]` → live watchdog + self-repair |
| **S-GEO** | `cdp:geo.backfill` for province-miss recovery | working `[VERIFIED, geocode.py]` → async backfill stream |
| **S-CODE** | unchanged pure function, used as the idempotency + anti-collision key everywhere | working `[VERIFIED, codes.py]` → load-bearing for the queue |
| **S-TIER1** | `WF-TIER1-HUNT` as `recipe-fleet`; spend-gated; parked walls honest | hunting `[VERIFIED]` → governed, cost-routed, separated tree |
| **S-API** | unchanged contract; reads the DB the plane keeps fresh | skeleton `[VERIFIED]` → fed by the live loop |

---

## 13. Build order (what to implement, in dependency order)

Architecture only; implementation is downstream. The build sequence that respects the
dependencies above:

1. **Governor first** (`pipeline/governor.py`, Redis token bucket + AIMD). Nothing
   should fetch at scale until the bottleneck is mechanized — it is the lesson of the
   scar. Profiles committed under `countries/ES/governor/`.
2. **Queue substrate** (`pipeline/queue/streams.py`): the streams, the job envelope, the
   worker loop (§7.3), `XAUTOCLAIM` reaper, backoff re-enqueue, dead-letter.
3. **Wrap existing handlers** (`discover.py`/`ingest.py`/`verify.py` logic → job
   `HANDLERS`). They already work and are idempotent; the queue just drives them.
4. **Cost-router + Ollama client** (`pipeline/llm/local.py`): classify `kind`, fixing
   the `ingest.py:52` mis-typing at ingest time.
5. **S-HEALTH watchdog** (`pipeline/health.py`): heartbeat writes, drift detectors,
   `cdp:heal` consumer with the §8.3 decision tree.
6. **Scheduler** (`pipeline/scheduler.py`): the cadence table (§10), churn cohorting,
   BORRAR eviction.
7. **Intelligence fleets** (`WF-TIER1-HUNT`, `WF-INQUISITION`) wired to `cdp:recipe.hunt`
   / `cdp:inquisition`, spend-gated through the cost-router + ledger.

Each ships with the project's E2E verification pattern (apply → exercise → prove
idempotency/recovery → VAM) before its gate goes green — the standard already used for
migrations and the discover/ingest verticals. `[VERIFIED, PROGRESO.md]`

---

## 14. Open decisions (flagged for the owner, not assumed)

- **Redis deployment.** A dedicated `cardeep-redis` container (separate port from any
  CARDEX Redis) is the [ASSUMED] default, mirroring the dedicated `cardeep-pg :5433`
  separation. Confirm the port and whether persistence (AOF) is required for the
  streams (recommended: yes, so PEL survives a Redis restart).
- **Ollama model pin.** `qwen2.5:7b` / `llama3.1:8b`-class for `classify_kind` is
  [ASSUMED] pending a local benchmark on a labeled dealer sample; the contract (§3.3)
  is model-agnostic.
- **Cloud-agent budget caps** per front (`recipe-fleet`, `inquisition-fleet`) are
  owner-set numbers, not assumed here — the ledger + gate enforce whatever cap is given.
- **Governor starting rates** beyond AS24 (`max_concurrency: 2`, born of the scar
  `[VERIFIED]`) are tuned from each source's first 429-telemetry window via AIMD; the
  committed profiles are seeds, not final.

---

## 15. Sources

- Internal `[VERIFIED]` (read this session): `pipeline/discover.py`,
  `pipeline/ingest.py` (delta engine + `kind` hardcode :52), `pipeline/verify.py`
  (quorum + `primary_agrees`), `pipeline/harvest_dealer.py` (E2E chain + raw dump),
  `pipeline/ids.py` (ULID), `services/api/codes.py` (`cdp_code`),
  `migrations/0004_verification_health.sql` (`source_health`/`alert`/`verification_verdict`),
  `PROGRESO.md` (live counts, the 4× throttling scar, retry/backoff, governor lesson),
  `CLAUDE.md` (mandate: BORRAR, exact-origin alert, local-LLM cost doctrine).
- Companion pillars: `docs/architecture/00-TIER1-REGISTRY.md` (what `recipe-fleet`
  attacks), `01-ENTITY-ONTOLOGY.md` (the `kind` taxonomy the cost-router classifies into,
  the `ingest.py:52` mis-typing bug), `02-SCRAPING-ENGINE.md` (the fetch engine the
  governor wraps and the router escalates), `docs/ARCHITECTURE.md` (the data layer the
  plane keeps live), `docs/ORQUESTACION.md` (superseded first-pass).
- Redis Streams semantics (consumer groups, PEL, `XAUTOCLAIM`, at-least-once) — Redis
  documentation, applied; idempotency-by-`cdp_code` makes exactly-once unnecessary.
```
