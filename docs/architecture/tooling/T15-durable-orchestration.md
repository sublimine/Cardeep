# T15 — Durable Scheduling / Orchestration: Live 2026 Tooling Audit

> **Domain:** The permanent scheduler + durable-orchestration layer that drives CARDEEP's
> control plane — the heartbeat that emits cadenced jobs (continuous/hourly/daily/weekly
> sweeps, recipe re-hunts, Inquisition audits, BORRAR eviction) and the durable-execution
> substrate that keeps long-running scrape/ingest/verify chains crash-safe, retried,
> recoverable, and observable as a pipeline DAG. Candidates assessed: **APScheduler,
> Temporal, Prefect, Dagster, Windmill** — plus two 2026 dark-horses surfaced during the
> audit (**DBOS Transact, Restate**) that are materially better fits than two of the
> named five.
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I fetched
> the repo / PyPI / release page this session, URL cited) or **[ASSUMED]** (inferred, not
> opened). No corpses are recommended; dead/stalled artifacts are flagged explicitly.
>
> **Recency bar:** a library with no *stable* release in ~12 months is *suspect*; no commit
> in ~12 months is *dead for our purposes*. Stated explicitly per tool. A pre-release that
> has not graduated to stable in 14 months is treated as **not production-eligible**.

---

## 0. The CARDEEP-specific problem (why "best orchestrator" is the wrong question)

The incumbent is **already designed** and it is **not** a third-party orchestrator. Read this
session: `docs/architecture/04-ORCHESTRATION.md` **[VERIFIED]**. CARDEEP's control plane is a
**hand-built durable substrate** that already owns the hard parts of orchestration:

1. **The durable queue exists.** §4 specifies **Redis Streams** with consumer groups,
   per-message `XACK`, the Pending Entries List (PEL), and `XAUTOCLAIM` crash recovery —
   i.e. at-least-once delivery + crash redelivery is **already the design**, justified by
   the fact that every job is **idempotent by `cdp_code`** (law #3). **[VERIFIED, 04 §4.1-4.4]**
2. **Retries / backoff / dead-letter exist.** §4.4 specifies exponential backoff + jitter,
   `not_before` deferred re-enqueue, `max_attempts`, poison-job routing to `cdp:heal`, and a
   `cdp:dead` dead-letter stream. **[VERIFIED, 04 §4.4]**
3. **The real bottleneck is governed, not scheduled.** §5 — the **per-source rate-governor**
   (Redis token-bucket / GCRA + AIMD) is THE throughput lever; "worker count is not the
   throughput lever — the governor is" (§7.2). Throughput scales by *number of sources in
   parallel*, born of the **4× AS24 throttling scar** that lost 138 dealers. **[VERIFIED, 04 §5, §7.2, §0.1]**
4. **Self-heal + observability exist as design.** §8 (`source_health` heartbeat, drift
   detectors, `cdp:heal` auto-repair tree, exact-origin `alert`) and §9 (inline VAM +
   Inquisition). **[VERIFIED, 04 §8-9]**
5. **The scheduler is the ONLY thin spot.** §10 says the scheduler is *"a `cron`-driven or
   `asyncio`-loop emitter"* — **the single producer of scheduled jobs** that writes cadences
   onto the streams. §13 build-order item 6 is literally `pipeline/scheduler.py` (to build).
   **[VERIFIED, 04 §10, §13]**

**The decisive consequence.** CARDEEP does **not** have an empty orchestration slot to fill with
a heavyweight durable-execution engine. It has a **fully specified Redis-Streams control plane**
plus **one unbuilt component**: a *crash-safe, persistent cadence emitter*. Dropping in Temporal
or Dagster would mean **ripping out and duplicating** the governor, the streams, the idempotency
model, the heal loop, and the VAM — all already designed against the live system's scars. That is
not an upgrade; it is a rewrite that throws away the one subsystem (the per-source governor) that
no general orchestrator ships.

So the pick must satisfy a **narrow, sharp** requirement, not "which orchestrator wins 2026":

- **(R1) Durable, crash-safe scheduling.** If the emitter process dies between ticks, a missed
  daily sweep must not be silently lost — schedules persist and misfires are handled (coalesce /
  grace window), backed by a store CARDEEP already runs (Postgres `:5433` or the dedicated Redis).
- **(R2) Single-producer guarantee.** Cadences must **never double-fire** (04 §10) even across a
  restart or a future second instance → needs a persistent, lock-protected job store, not a bare
  in-memory `asyncio.sleep` loop.
- **(R3) Zero new heavy infrastructure.** No Cassandra, no Elasticsearch, no separate cluster of
  services. Runs on a laptop / single node next to `pipeline/`, in-process Python.
- **(R4) Does NOT fight the existing substrate.** It *emits onto* Redis Streams; it does not try
  to own execution, retries, or rate-limiting — those are already better-solved in-house for this
  exact domain (the governor).
- **(R5) Alive in 2026**, Python-native, MIT/BSD/Apache-licensed.

A second, *optional* tier of the audit asks: **if** CARDEEP ever wants per-step durable execution
*inside* a worker (checkpoint-and-resume of a multi-step dealer E2E without re-running completed
steps), which 2026 engine fits **without** abandoning Redis Streams + the governor? That tier has
a different winner (see §7).

---

## 1. Verdict up front

| Layer | Pick | Status | Why (one line) |
|---|---|---|---|
| **Scheduler / cadence emitter (R1-R5, the actual gap)** | **APScheduler 3.11** (persistent `SQLAlchemyJobStore` on the existing Postgres) | ✅ **alive** (3.11.2, 2025-12-22) | Smallest correct tool: durable schedules, misfire grace + coalesce, single-producer via the DB job store, in-process, zero new infra, emits onto Redis Streams. Does exactly R1-R5 and nothing it would fight. |
| **Fallback scheduler (if a richer trigger model / UI is later wanted)** | **Prefect 3.7** (self-hosted server, schedule-only use) | ✅ **alive** (3.7.4, 2026-06-05) | Python-first, durable scheduling + retries + a real run-history UI; can be adopted *incrementally* as the cadence layer without forcing the streams out. Heavier than APScheduler; justified only if observability/UI demand grows. |
| **Optional per-step durable execution INSIDE a worker (future tier)** | **DBOS Transact** (Postgres-backed, in-process) | ✅ **alive** (2.23.0, 2026-06-01) | Ultra-light durable execution on the **Postgres CARDEEP already runs** — `@DBOS.workflow`/`@DBOS.step` checkpoints to PG, auto-resumes from the last completed step. Zero new infra; coexists with Redis Streams + governor. The modern answer to "durable execution" without a Temporal cluster. |
| **Heavy durable-execution engine (only if multi-language, signals, human-in-loop at scale)** | **Temporal** (self-hosted) | ✅ **alive** (Python SDK 1.28.0, 2026-06-04) | Best-in-class durability/timer/signal/retry model and the 2026 "Leader" for durable execution — but its determinism constraints and PG+(Cassandra/ES) cluster overhead are a poor fit for CARDEEP's async-scraper code and single-node target. Documented, not recommended now. |
| ~~Full data orchestrator as the spine~~ | **Dagster** | ✅ alive but **wrong shape** | Asset/lineage-centric DAG runner; great for dbt/modern-data-stack, "weak for long-running app orchestration" (2026 quadrant). Would duplicate the streams/governor. Rejected for CARDEEP's role. |
| ~~Script-runner platform as the spine~~ | **Windmill** | ✅ alive but **wrong shape** | Code-first internal-tools / script platform (Rust, fast), excellent UI/secrets — but "more tool than full orchestrator," operator-oriented, and would own execution. Rejected as the spine; not the gap CARDEEP has. |
| ⚠️ **DEAD-FOR-PROD pre-release** | **APScheduler 4.0** | ⚠️ **alpha, stalled** | 4.0.0a6 (2025-04-27) — **14 months** with no graduation to stable; README: *"do NOT use this release in production!"* Use **3.11**, not 4.0. |

**Bottom line:** CARDEEP's current choice (a hand-rolled "`cron`/`asyncio`-loop emitter", 04 §10)
is **directionally right but under-specified on durability** — a bare `asyncio.sleep` loop fails
R1/R2 (a crash loses the schedule; a restart can double-fire). **Replace the hand-rolled emitter
with APScheduler 3.11 on a persistent Postgres job store.** Everything else in 04 (streams,
governor, heal, VAM) stays. Do **not** adopt Temporal/Dagster/Windmill as the spine.

---

## 2. APScheduler — the right-sized pick (and the 4.0 trap)

**Repo:** https://github.com/agronholm/apscheduler · **PyPI:** https://pypi.org/project/APScheduler/

### 2.1 Alive-or-dead

- **3.11.2 — released 2025-12-22.** **[VERIFIED, PyPI]** Stable line is **actively maintained**
  (3.11.0 2024-11, 3.11.1 2025-10-31, 3.11.2 2025-12-22). **7.5k stars**, 1,324 commits.
  **[VERIFIED, GitHub repo page]** ✅ **ALIVE.**
- **4.0.0a6 — released 2025-04-27 — alpha, ~14 months stale, NOT production-eligible.**
  **[VERIFIED, PyPI + GitHub releases]** The README carries an explicit warning: *"The v4.0 series
  is provided as a **pre-release** and may change in a backwards incompatible fashion without any
  migration pathway, so do NOT use this release in production!"* **[VERIFIED, GitHub README]**
  4.0 is a ground-up rewrite (data stores + event brokers for multi-scheduler coordination,
  tracked since 2020 in issue #465) that has **not shipped a stable in 14 months**. ⚠️ **TREAT 4.0
  AS A TRAP** — pin `APScheduler>=3.11,<4`.

### 2.2 What it solves for CARDEEP (maps to R1-R5)

- **R1 durable schedules + misfire handling.** Persistent job stores (SQLAlchemy → Postgres,
  Redis, MongoDB) survive restart; `misfire_grace_time` + `coalesce` decide what happens to a tick
  missed during downtime (run-once-late vs skip), and `max_instances` prevents overlap.
  **[VERIFIED, repo: "PostgreSQL, MySQL and derivatives, SQLite, MongoDB" persistent stores]**
- **R2 single-producer.** The persistent job store is the single source of schedule truth; a
  `BackgroundScheduler`/`AsyncIOScheduler` reading it won't re-create already-stored jobs (stable
  `job_id` + `replace_existing`), and the store row is the coordination point against a second
  instance — exactly 04 §10's "single producer, never double-fire."
- **R3 zero new infra.** Pure Python, in-process, store on the **already-present** `cardeep-pg
  :5433`. No broker, no cluster.
- **R4 doesn't fight the substrate.** APScheduler's *job function is one line*: `XADD` onto the
  right Redis Stream. It schedules; the streams + governor + workers (04 §4-7) execute. Perfect
  separation — it fills the gap and touches nothing else.
- **R5 alive, BSD-like (MIT) license, Python 3.8-3.13.** **[VERIFIED, PyPI classifiers]**

### 2.3 Weaknesses (honest)

- **No built-in run-history UI / DAG view.** Observability of the *pipeline DAG* is **not**
  APScheduler's job — and it doesn't need to be: CARDEEP's DAG observability lives in
  `source_health`, `alert`, `verification_verdict`, `vehicle_event`, and the streams' PEL
  (04 §8-9). APScheduler only needs to prove *"the cadence fired on time."* If a schedule UI is
  later wanted, that is the trigger to consider the Prefect fallback (§3), not a reason to reject
  APScheduler now.
- **3.x ≠ 4.x multi-scheduler HA.** 3.x is single-scheduler-with-persistent-store, not a
  multi-active-scheduler cluster. **This is fine** — 04 §10 explicitly wants a *single* producer.
  HA here = "restart recovers from the store," which 3.x's persistent job store gives. Do not buy
  4.0's unfinished multi-scheduler complexity to solve a problem CARDEEP doesn't have.

### 2.4 Integration notes + sample CONFIG

Add to `pipeline/scheduler.py` (the 04 §13 build-order item 6). The scheduler's **only** action
per cadence is to `XADD` a job envelope (04 §4.3) onto a stream; the governor paces execution.

```python
# pipeline/scheduler.py — durable cadence emitter (replaces the hand-rolled asyncio loop)
# pip: APScheduler>=3.11,<4   (NEVER 4.0.0a* in prod)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

# Durable store on the Postgres CARDEEP already runs (cardeep-pg :5433).
# A dedicated schema keeps APScheduler tables out of the product schema.
jobstores = {
    "default": SQLAlchemyJobStore(
        url="postgresql+psycopg://cardeep:***@localhost:5433/cardeep",
        tablename="apscheduler_jobs",  # lives in its own table; never touches entity/vehicle
    )
}
job_defaults = {
    "coalesce": True,          # a tick missed during downtime fires ONCE on recovery, not N times
    "max_instances": 1,        # single-producer guarantee (04 §10) — no overlapping cadence runs
    "misfire_grace_time": 900, # a daily sweep missed by <15 min still fires; older = skipped (logged)
}
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors={"default": AsyncIOExecutor()},
    job_defaults=job_defaults,
    timezone="Europe/Madrid",  # cadence intent is Spain-local (04 mandate "tiempo real")
)

# Cadences from 04 §10.1 — each job ONLY enqueues onto a stream; the governor paces it.
def register_cadences(emit) -> None:
    # emit(stream, payload) = XADD onto Redis Streams (pipeline/queue/streams.py, 04 §4)
    scheduler.add_job(emit, "interval", seconds=30, args=("cdp:harvest", {"mode": "backlog_refill"}),
                      id="continuous-harvest-refill", replace_existing=True)
    scheduler.add_job(emit, "cron", minute=0, args=("cdp:harvest", {"cohort": "flagship_hourly"}),
                      id="hourly-flagship-harvest", replace_existing=True)
    scheduler.add_job(emit, "cron", hour=3, minute=0, args=("cdp:harvest", {"cohort": "all_active"}),
                      id="daily-full-sweep", replace_existing=True)
    scheduler.add_job(emit, "cron", hour=4, minute=0, args=("cdp:discover", {"cohort": "fast_sources"}),
                      id="daily-discover-fast", replace_existing=True)
    scheduler.add_job(emit, "cron", day_of_week="sun", hour=2, args=("cdp:discover", {"cohort": "all"}),
                      id="weekly-discover-full", replace_existing=True)
    scheduler.add_job(emit, "cron", day_of_week="sun", hour=5, args=("cdp:inquisition", {"scope": "top_n+unverified"}),
                      id="weekly-inquisition", replace_existing=True)
    scheduler.add_job(emit, "cron", hour=6, minute=30, args=("cdp:evict", {"policy": "lru_above_hwm"}),
                      id="daily-borrar-eviction", replace_existing=True)  # BORRAR (04 §10.3)
```

`replace_existing=True` + stable `id=` makes startup **idempotent**: the persistent store is the
schedule truth, restart re-attaches, no duplicate jobs (R2). Event-driven cadences (`cdp:heal` on
degraded health, `cdp:recipe.hunt` on drift — 04 §10.1) are **not** APScheduler's job; they are
fired by the watchdog (04 §8), correctly.

---

## 3. Prefect 3 — the fallback (richer triggers + UI, when justified)

**Compare page:** https://www.prefect.io/compare/dagster · **PyPI:** https://pypi.org/project/prefect/

### 3.1 Alive-or-dead

- **3.7.4 — released 2026-06-05.** **[VERIFIED, PyPI]** Extremely active: 3.7.0 (2026-05-06) →
  3.7.4 (2026-06-05), ~weekly cadence. ✅ **ALIVE** and a 2026 market-quadrant **Leader** for
  Python-first orchestration. **[VERIFIED, npow March-2026 quadrant]**

### 3.2 What it adds over APScheduler

- **Durable scheduling + native retries + a real run-history/observability UI** (self-hosted
  Prefect server, Postgres-backed). **[VERIFIED, prefect.io GA post + npow quadrant]**
- **Prefect 3.0 transactional semantics**: every task runs in a transaction governing result
  persistence, enabling "return your workspace to a desired point in the past" on failure — i.e. a
  lightweight durability/idempotency model. **[VERIFIED, prefect.io "Transactional ML Pipelines"]**
- **Hybrid architecture**: workers poll via outbound-only connections; code/data/compute stay in
  your environment — friendly to a self-hosted, single-node CARDEEP. **[VERIFIED, prefect/dagster compare]**

### 3.3 Why it's the *fallback*, not the pick

- **Heavier than the gap requires.** It brings a server + DB-backed control plane CARDEEP would run
  *in addition to* its Redis Streams substrate — two control planes where 04 designed one. As a
  **schedule-only** adoption (Prefect emits onto the streams, exactly like the APScheduler job) it
  is reasonable; as a full execution engine it would duplicate the governor/streams (R4 violation).
- **Adopt incrementally, only on a real trigger:** if CARDEEP later needs a *visual* schedule/run
  history, event-driven automations, or non-developer schedule editing, lift the cadence layer from
  APScheduler to Prefect **without** moving execution off Redis Streams. Until then, APScheduler is
  less to operate.

### 3.4 Sample CONFIG (schedule-only adoption)

```python
# Prefect as a schedule-only emitter — the flow body just XADDs, like the APScheduler job.
from prefect import flow
from prefect.client.schemas.schedules import CronSchedule

@flow(retries=2, retry_delay_seconds=30, log_prints=True)
def emit_cadence(stream: str, payload: dict):
    xadd(stream, payload)   # pipeline/queue/streams.py — governor still paces execution (04 §5)

emit_cadence.serve(
    name="daily-full-sweep",
    schedule=CronSchedule(cron="0 3 * * *", timezone="Europe/Madrid"),
    parameters={"stream": "cdp:harvest", "payload": {"cohort": "all_active"}},
)
# Self-hosted server: `prefect server start` (Postgres-backed) for the run-history UI.
# Execution still lives in Redis Streams + the governor; Prefect only owns the cadence + its UI.
```

---

## 4. Temporal — the heavy durable engine (documented, NOT recommended now)

**Repo:** https://github.com/temporalio/sdk-python · **Docs:** https://docs.temporal.io/develop/python

### 4.1 Alive-or-dead

- **Python SDK 1.28.0 — released 2026-06-04.** **[VERIFIED, GitHub releases]** Intensely active
  (1.25.1/1.26.1 2026-05-18 → 1.28.0 2026-06-04). At Replay 2026: Serverless Workers, Standalone
  Activities, Workflow Streams, Nexus GA. **[VERIFIED, temporal.io Replay-2026 post]** 2026
  market-quadrant **Leader** for durable execution. ✅ **ALIVE** and best-in-class.

### 4.2 Why it is *the wrong fit for CARDEEP right now* (despite being the category leader)

- **Determinism constraints clash with the scraper code.** Temporal workflows must be
  deterministic: *"no `set` iteration, threading, no randomness, no external calls to processes, no
  network IO… networking, subprocesses, and disk I/O [disabled]"* inside workflows — all I/O must be
  shoved into Activities. **[VERIFIED, sdk-python repo]** CARDEEP's logic is *fundamentally* network
  I/O against governed sources; modeling it in Temporal means wrapping nearly everything as
  Activities and re-expressing the **per-source governor** (which has no Temporal equivalent) on top
  — large rewrite, little gained over the already-designed Redis-Streams + governor model.
- **Cluster operational overhead breaks R3.** Self-hosted Temporal is *"not a single process… a
  persistent database and a cluster of multiple processes,"* needing PostgreSQL **plus** typically
  Elasticsearch for visibility, and Cassandra for scale; *"PostgreSQL is not ideal for
  medium-to-large-scale systems."* **[VERIFIED, self-hosted complexity search + Temporal docs]**
  That is a heavy multi-service cluster on a single-node target — exactly the overhead 04 §4.1
  avoided by choosing Redis Streams already in the stack.
- **Smallest community signal of the named set on the SDK repo** (1.1k stars on `sdk-python`,
  **[VERIFIED]**) — not a death flag (Temporal's mass is in Go/the server), but it underlines that
  for a Python single-node scraper this is the wrong center of gravity.

**When Temporal *would* win:** multi-language workflows, long human-in-the-loop approvals at scale,
rich signals/queries, or a many-node cluster — none of which is CARDEEP's current shape. Keep it on
the shelf, documented; do not adopt it as the spine.

---

## 5. Dagster — alive, wrong shape (rejected as spine)

**Compare:** https://dagster.io/vs/dagster-vs-prefect · **PyPI:** https://pypi.org/project/dagster/

- **1.13.9 — released 2026-06-11.** **[VERIFIED, PyPI]** ~weekly releases through H1-2026,
  "Production/Stable," Apache-2.0. ✅ **ALIVE.**
- **Wrong shape for CARDEEP's role.** Dagster is **asset/lineage-centric**: you structure code as a
  software-defined **asset graph** with IO managers handling reads/writes. **[VERIFIED, prefect/dagster
  compare]** The 2026 quadrant places it as a **Challenger** strong on dbt/modern-data-stack and
  data-lineage, but *"weak for long-running app orchestration."* **[VERIFIED, npow quadrant]**
- **Cost signal.** Effective 2026-05-01, Dagster+ Solo/Starter dropped credits — every credit
  billed from $0.035-0.040. **[VERIFIED, prefect/dagster 2026 comparison]** (OSS self-host is free;
  noted for completeness.)
- **Verdict:** would force CARDEEP's scrape→ingest→verify chains into an asset-materialization model
  and **duplicate** the Redis-Streams substrate + governor. Excellent tool, **rejected** for this
  role. Not the gap CARDEEP has.

---

## 6. Windmill — alive, wrong shape (rejected as spine)

**Repo:** https://github.com/windmill-labs/windmill

- **v1.723.0 — released 2026-06-11** (two releases the same day; extremely high cadence).
  **[VERIFIED, GitHub releases]** ~16k stars, Rust backend / Svelte frontend, used by 3,000+ orgs.
  **[VERIFIED, repo + search]** ✅ **ALIVE** and fast-moving.
- **What it is:** a **code-first internal-tools / script platform** — scripts→webhooks/workflows/UIs,
  cron + visual cron builder, flows with branching/loops/retries, first-class secrets, full web IDE.
  Self-hosts on Postgres in minutes. Genuinely strong at operator/analyst-facing automation.
- **Wrong shape for the spine.** 2026 quadrant: **Niche Player** — *"script runner with growing
  workflow capabilities; more tool than full orchestrator… least suitable for complex distributed
  patterns."* **[VERIFIED, npow quadrant + pkgpulse 2026]** It wants to **own execution and the UI**;
  CARDEEP's execution is already owned by governed Python workers on Redis Streams. Adopting Windmill
  as the spine means re-homing the workers into Windmill's runtime and losing the per-source governor.
- **Verdict:** great product, **rejected** as CARDEEP's orchestrator. (If a non-developer ever needs
  a UI to toggle/inspect schedules, Windmill or Prefect's UI are the options to revisit — UI is not a
  current requirement.)

---

## 7. Optional future tier — per-step durable execution *inside* a worker

This tier answers a **different** question than the scheduler gap: *if* a single dealer's E2E
(DISCOVER→HARVEST→RECIPE→INGEST→VERIFY, 04 §11) should **checkpoint-and-resume** so a crash mid-chain
doesn't re-run already-completed steps (beyond what at-least-once + `cdp_code` idempotency already
give for free), which 2026 engine fits **without** abandoning Redis Streams + the governor?

### 7.1 DBOS Transact — the modern, infra-free answer ✅

**PyPI:** https://pypi.org/project/dbos/

- **2.23.0 — released 2026-06-01.** **[VERIFIED, PyPI]** *"Ultra-lightweight durable execution in
  Python"* — annotate functions with `@DBOS.workflow()` / `@DBOS.step()`; state is checkpointed to
  **PostgreSQL** and **auto-resumes from the last completed step** after a crash. Durable workflows,
  queues, scheduling, events — **backed by Postgres, no separate infrastructure**, Python 3.10+,
  MIT, maintained by DBOS, Inc. **[VERIFIED, PyPI]** ✅ **ALIVE.**
- **Why it fits CARDEEP and Temporal doesn't (for this tier):** it runs **in-process** on the
  **Postgres CARDEEP already runs** (`cardeep-pg :5433`) — **zero new infra (R3)** — and imposes no
  Temporal-style determinism cluster. It coexists with Redis Streams: a worker can wrap its multi-step
  handler in `@DBOS.workflow` for free checkpoint/resume while the streams still deliver the job and
  the governor still paces the fetch.
- **2026 positioning:** named alongside Temporal and Prefect in durable-workflow-engine comparisons
  as the lightweight Postgres-native option. **[VERIFIED, dev.to durable-engines comparison + search]**

```python
# OPTIONAL: free checkpoint/resume for a dealer E2E, on the Postgres already present.
from dbos import DBOS
@DBOS.workflow()
def dealer_e2e(cdp_code: str):
    raw = DBOS.step(harvest)(cdp_code)   # if the process dies after harvest…
    ent = DBOS.step(ingest)(raw)         # …resume here on restart, harvest NOT re-run
    DBOS.step(verify)(ent)               # governor + streams unchanged; PG is the journal
```

### 7.2 Restate — the visionary alternative ⚠️ (lighter ecosystem)

- 2026 quadrant **Visionary**: *"journal-based execution model with the most explicit idempotency and
  compensation semantics… lightweight durable execution without heavy infrastructure."* **[VERIFIED,
  pkgpulse + npow quadrant]** Weaknesses: *"less mature observability than Temporal, smaller
  ecosystem (~3K weekly downloads vs Temporal's 25K)."* **[VERIFIED, pkgpulse 2026]**
- **Verdict:** credible and modern, but DBOS's *Postgres-you-already-run* story is a cleaner fit for
  CARDEEP's single-node + Postgres reality. Keep Restate as the secondary option for this tier.

**Tier status:** **not needed for the MVP.** At-least-once + `cdp_code` idempotency (04 §3) already
makes redelivery safe; per-step resume is an optimization. Adopt DBOS **only** if re-running
completed steps becomes a measured cost. Flagged here so the decision is informed, not reinvented.

---

## 8. Recency ledger (the ruthless table)

| Tool | Latest stable | Date | Stars | Verdict |
|---|---|---|---|---|
| **APScheduler 3.x** | 3.11.2 | **2025-12-22** | 7.5k | ✅ alive — **PICK (scheduler)** |
| APScheduler 4.0 | 4.0.0a6 (alpha) | 2025-04-27 | (same repo) | ⚠️ **stalled pre-release, 14 mo, DO NOT use in prod** |
| **Prefect** | 3.7.4 | **2026-06-05** | — | ✅ alive — **FALLBACK (scheduler+UI)** |
| **Temporal Python SDK** | 1.28.0 | **2026-06-04** | 1.1k (sdk-python) | ✅ alive — documented, **not recommended now** |
| **Dagster** | 1.13.9 | **2026-06-11** | — | ✅ alive — **wrong shape, rejected as spine** |
| **Windmill** | v1.723.0 | **2026-06-11** | ~16k | ✅ alive — **wrong shape, rejected as spine** |
| **DBOS Transact** | 2.23.0 | **2026-06-01** | — | ✅ alive — **optional per-step durability tier** |
| Restate | (recent, 2026) | 2026 | — | ✅ alive — visionary, secondary to DBOS for CARDEEP |

No corpses recommended. The **only** dead-for-prod artifact flagged is **APScheduler 4.0.0a6** (a
stalled alpha) — and the live 3.11 line is the actual pick, so the trap is avoided by pinning.

---

## 9. Is CARDEEP's current choice good enough? — and what replaces it

**Current choice (04 §10):** *"a `cron`-driven or `asyncio`-loop emitter… the single producer of
scheduled jobs."* **[VERIFIED, 04 §10]**

**Verdict: directionally correct, but as a bare `asyncio.sleep` loop it is NOT good enough** — it
fails **R1** (a crash between ticks silently loses a cadence; nothing persists the schedule) and
**R2** (no DB-backed lock → a restart or a second instance can double-fire). A hand-rolled
crash-safe + misfire-correct + single-producer scheduler is exactly the wheel APScheduler already
reinvented and hardened over a decade.

**Replacement (minimal, surgical):** **Adopt APScheduler 3.11 with a persistent `SQLAlchemyJobStore`
on the existing `cardeep-pg :5433`** as `pipeline/scheduler.py` (the 04 §13 build-order item 6). Its
job functions do nothing but `XADD` onto the Redis Streams of 04 §4 — so **every other subsystem of
04 is preserved unchanged**: the governor (§5) still owns throughput, the streams (§4) still own
durable delivery + retries, the heal loop (§8) still owns self-repair, VAM (§9) still owns
verification. The change is **one component swap**, not an orchestration rewrite.

- **Do NOT** replace the spine with Temporal, Dagster, or Windmill — each would **duplicate or
  evict** the Redis-Streams substrate and the per-source governor, which are the parts no general
  orchestrator ships and which were designed against this system's real scars (04 §0.1, §5).
- **Fallback** (only if a visual schedule/run-history UI or event-automations become a real
  requirement): lift the cadence layer to **Prefect 3.7**, schedule-only, still emitting onto the
  streams.
- **Optional future** (only if re-running completed E2E steps becomes a measured cost): wrap worker
  handlers in **DBOS Transact** for Postgres-journaled checkpoint/resume — zero new infra.

This keeps 04's promise — *"Cardeep no se cae"* — true at the one layer that was still a bare loop:
the heartbeat now survives its own crash.

---

## 10. Sources

All fetched this session (2026-06-12) unless marked internal:

- Internal `[VERIFIED]`: `docs/architecture/04-ORCHESTRATION.md` (§4 Redis Streams + at-least-once,
  §5 rate-governor + the 4× AS24 throttling scar, §7.2 governor-is-the-lever, §8 S-HEALTH, §9 VAM,
  §10 scheduler cadences + single-producer, §10.3 BORRAR, §13 build order).
- APScheduler — https://pypi.org/project/APScheduler/ (3.11.2 2025-12-22; 4.0.0a6 2025-04-27 alpha);
  https://github.com/agronholm/apscheduler (7.5k stars, 1,324 commits, README "do NOT use [4.0] in
  production!"); https://github.com/agronholm/apscheduler/releases; issue #465 (4.0 progress tracking,
  open since 2020).
- Temporal — https://github.com/temporalio/sdk-python/releases (1.28.0 2026-06-04);
  https://github.com/temporalio/sdk-python (1.1k stars, determinism constraints — no network/disk/threads
  in workflows); https://temporal.io/blog/replay-2026-product-announcements; self-hosted complexity:
  https://medium.com/@mailman966/my-journey-hosting-a-temporal-cluster-237fec22a5ec + Temporal docs
  (PG+Cassandra/Elasticsearch cluster).
- Prefect — https://pypi.org/project/prefect/ (3.7.4 2026-06-05); https://www.prefect.io/compare/dagster
  (hybrid architecture); https://www.prefect.io/blog/prefect-3-generally-available-september-3 +
  https://www.prefect.io/blog/transactional-ml-pipelines-with-prefect-3-0 (3.0 transactional semantics).
- Dagster — https://pypi.org/project/dagster/ (1.13.9 2026-06-11); https://dagster.io/vs/dagster-vs-prefect
  (asset-graph model); 2026 pricing change (Dagster+ credits removed 2026-05-01).
- Windmill — https://github.com/windmill-labs/windmill/releases (v1.723.0 2026-06-11);
  https://www.windmill.dev/ (Rust/Svelte, ~16k stars, 3,000+ orgs).
- DBOS Transact — https://pypi.org/project/dbos/ (2.23.0 2026-06-01; Postgres-backed durable execution,
  no separate infra, MIT, Python 3.10+).
- 2026 landscape — http://npow.github.io/posts/workflow-orchestration-market-quadrant-2026/ (March 2026
  quadrant: Temporal/Prefect/Airflow Leaders, Dagster Challenger, Restate Visionary, Windmill Niche;
  durable-execution vs data-orchestration split); https://www.pkgpulse.com/guides/temporal-vs-restate-vs-windmill-durable-workflow-2026
  (Restate "lightweight durable execution," download/maturity comparison).
```
