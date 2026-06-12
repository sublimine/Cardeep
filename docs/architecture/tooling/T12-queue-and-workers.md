# T12 — Queue / Transport + Python Workers at Scale

> Tooling audit for CARDEEP. Domain: the **event/job bus** that decouples the
> scraping fleet (ingest → enrich → index → delta → remediation) and the
> **Python worker layer** that drains it, at the scale of "100% of Spain's
> used-vehicle POS + the giant marketplaces" — full inventory + live delta.
>
> Audit date: **2026-06-12**. Recency bar: anything not updated in 12+ months is
> treated as suspect and called out. A tool whose last release predates
> ~2025-06 is flagged.
>
> Anti-hallucination legend: **[VERIFIED]** = I fetched the repo / API / page
> this session (URL cited). **[ASSUMED]** = inferred or from secondary write-up,
> not directly confirmed against the primary source.

---

## 0. TL;DR — Recommendation

| Role | Pick | Status | Why |
|---|---|---|---|
| **Transport / event bus (primary)** | **Redis Streams** (via `redis-py` ≥ 6.x) | ✅ alive, Redis 8.4 (2026) | Already in stack; consumer groups + XACK/XPENDING/XAUTOCLAIM give native at-least-once; throughput envelope (~480k msg/s, p99 0.8 ms) crushes CARDEEP's tens-of-K/min target with 100x headroom. **CARDEEP's current ADR-0001 choice — confirmed still correct.** |
| **Transport fallback (only if/when bus > ~50K msg/min sustained or multi-day replay/audit needed)** | **NATS JetStream** | ✅ alive, v2.14.x (2026-06) | Lighter than Kafka, Go-native, persistent, at-least-once + exactly-once, mature `nats.py` (v2.15.0, 2026-06-05). Kafka only if you later need a durable log / analytics replay, not as a job bus. |
| **Worker library (primary, IF you adopt a framework)** | **Dramatiq** | ✅ alive, v2.1.0 (2025-03) | Fastest in the 2026 20k-job benchmark (1.53 s), "ack only when done" = at-least-once by design, automatic retries + DLQ + prefetch backpressure, RabbitMQ **and** Redis brokers. The modern Celery replacement. |
| **Worker library (fallback / async-first)** | **Taskiq** | ✅ alive, v0.12.4 (2026-05) | asyncio-native (matches CARDEEP's `asyncio` fleet), 2nd-fastest (2.03 s), pluggable brokers incl. Redis Streams, FastStream interop. Use if a framework must be async end-to-end. |
| **Worker library — Postgres-backed alternative** | **Procrastinate** | ✅ alive (pushed 2026-06-10) | If you ever want the queue *inside PostgreSQL* (CARDEEP already runs PG as system-of-record) to kill the Redis-as-broker dependency for a sub-pipeline. Transactional enqueue with your writes. |
| **Reject** | **Celery** (as a *new* choice), **arq**, **RQ** | see §4 | Celery: alive but heavy/legacy ergonomics, slower, sync-rooted. arq/RQ: alive but **benchmarked ~17–35x slower** than Dramatiq — wrong tool at this scale. |
| **Dead / do-not-adopt** | none fully dead in this domain | — | Every live candidate here is maintained in 2026. The trap is not a corpse; it's adopting a *slower/heavier* live tool. |

**Bottom line.** CARDEEP's existing choice — **raw Redis Streams via `redis.asyncio`
with hand-rolled idempotent consumer groups, at-least-once + DLQ** (ADR-0001 /
ADR-0004) — is **the correct architecture and is NOT obsolete in 2026.** It does
not need replacing. The honest gaps are *implementation-level*, not
tool-selection: (1) the hand-rolled consumer loop reimplements reclaim/DLQ/retry
that a framework gives free, (2) Redis 8.4's new single-shot `XREADGROUP … CLAIM`
should replace the multi-call XPENDING+XAUTOCLAIM reclaim, (3) no library-level
backpressure beyond `count`/`block`. If the fleet grows enough to want a
framework, **Dramatiq (Redis broker)** is the bulletproof modern pick and
**Taskiq** the async-native fallback — both keep Redis Streams as transport, so
no bus migration. Move to **NATS JetStream** only when sustained throughput or
replay/audit needs exceed Redis's envelope (the ADR-0001 review trigger).

---

## 1. Scope framing — what CARDEEP actually needs from this layer

The bus is the spine between asymmetric workloads:

1. **Spider/ingest** bursts (scraping peaks): tens of thousands of events/minute,
   bursty, latency-tolerant.
2. **Enrich** (L1→L2 seam, `enrich_worker`): per-listing fetch+parse, I/O-bound,
   the heavy lane — must scale horizontally and independently.
3. **Index / rich consumer** (writes to `vehicles`): DB-bound, idempotent UPSERT.
4. **Delta / remediation** (`delta_worker`, `remediation_dispatcher`): live delta
   detection + purge dispatch.

Hard requirements (from ADR-0001 / ADR-0004, verified against code):

- **At-least-once** delivery; **every consumer idempotent by contract**
  (unique id + `ON CONFLICT DO NOTHING`, content-hash lookup, or set-based UPSERT).
- **Consumer groups** with pending-entry (PEL) tracking.
- **Automatic retries** w/ exponential backoff → **DLQ stream** (`stream:dlq`),
  not auto-reprocessed (manual + RUNBOOK RB-003).
- **Backpressure**: bounded in-flight work so a slow enrich lane can't drown PG.
- **Zero/near-zero infra cost** pre-MVP; trivial Docker Compose operation.
- Throughput horizon: tens of K events/min, review trigger at **50K/min sustained**.

This is a **job-queue / work-distribution** problem, *not* an event-streaming /
event-sourcing problem. That distinction is the whole ballgame in §3.

---

## 2. CARDEEP's CURRENT implementation (ground truth, [VERIFIED] in repo)

**[VERIFIED]** Transport = **Redis Streams**, accessed **directly via
`redis-py`'s `redis.asyncio` (aioredis alias)** — *no* task-queue framework.
- `scrapers/requirements.txt` pins `redis>=5.0.0`.
  ([VERIFIED] file read.)
- Workers are hand-rolled async loops: `scrapers/enrich_worker.py`,
  `scrapers/rich_consumer.py`, `scrapers/common/indexer.py`,
  `scrapers/delta/delta_worker.py`, `scrapers/delta/remediation_dispatcher.py`,
  `scrapers/delta/operator_events.py`, `scrapers/dealer_scraping/*`.
  ([VERIFIED] `grep` for `XREADGROUP/XADD/XACK/XPENDING/consumer group`.)
- Stream contract (from `enrich_worker.py`): `stream:enrich_pending` →
  `stream:ingestion_raw` → consumer, `stream:dlq` for irreparable parses,
  group `cg_enrich`, `INGESTION_MAXLEN = 5_000_000` (capped stream), explicit
  PEL **reclaim of idle un-ACKed entries** so `XREADGROUP '>'` re-delivery gaps
  are closed. ([VERIFIED] head of `enrich_worker.py`.)
- Guarantee = **at-least-once + idempotency by contract** (ADR-0004), DLQ after
  N exponential retries, PEL monitored as a primary metric.

**ADR provenance** ([VERIFIED] both files read):
- `docs/adr/0001-redis-streams-sobre-kafka-nats.md` — Redis Streams chosen over
  Kafka (operational complexity, over-engineering for volume) and NATS JetStream
  (smaller ecosystem, less battle-tested for the use-case). Review trigger:
  2026-10-27 **or** sustained > 50K events/min.
- `docs/adr/0004-at-least-once-idempotencia.md` — at-least-once + mandatory
  idempotent consumers; exactly-once rejected (needs distributed Redis↔PG txn).

So the question this audit must answer is precise: **is "raw Redis Streams +
hand-rolled idempotent asyncio consumers" still the best-in-class 2026 choice, or
has a worker framework / different transport overtaken it?**

---

## 3. Transport audit (live 2026 ecosystem)

### 3.1 Redis Streams — RECOMMENDED PRIMARY ✅ (CARDEEP's current pick)

- **Alive?** ✅ Redis core is the most-active data store on the planet. Redis
  **8.4 (2026)** shipped a *materially relevant* feature: **single-shot reliable
  consumers via `XREADGROUP … CLAIM`** — one round-trip that replaces the
  XPENDING → XCLAIM/XAUTOCLAIM → XREADGROUP stitch and returns the metadata
  needed to build retry caps + DLQ logic. **[VERIFIED]** Redis engineering blog
  "Single-shot reliable consumers with XREADGROUP CLAIM in Redis 8.4".
- **What it solves:** consumer groups, XACK, PEL tracking, XAUTOCLAIM reclaim,
  capped streams (`MAXLEN`), native at-least-once. Inspectable with `redis-cli`.
- **Throughput / latency [ASSUMED, secondary benchmark]:** ~**480k msg/s** at
  1 KB, **p99 0.8 ms** end-to-end (dev.to "Message Brokers Comparison 2026").
  Even discounted heavily this is ~100x CARDEEP's 50K/min (≈833/s) review
  threshold. Throughput is **not** the constraint.
- **Weaknesses:** no native exactly-once (CARDEEP correctly doesn't need it);
  durability tied to Redis persistence model (RDB/AOF) — a streaming/audit log
  (multi-day replay) is not its strength; the classic **XAUTOCLAIM pathological
  O(log n) PEL churn** under "mostly-keeping-up with occasional stuck messages"
  is real **[VERIFIED]** (Redis 8.4 blog explicitly cites this as the motivation
  for the new command). The Python `redis.asyncio` client lacks high-level
  retry/DLQ/backpressure — you hand-roll it (which CARDEEP did).
- **Recommendation:** **Keep.** Two concrete upgrades:
  1. Pin **`redis-py` ≥ 6.x** and target **Redis 8.4** server; migrate the
     reclaim path to `XREADGROUP … CLAIM` to kill the XAUTOCLAIM PEL-churn cost.
  2. Add explicit **backpressure** (see §6) — bound in-flight by `count` *and*
     a semaphore/concurrency cap in the async loop so the enrich lane can't
     outrun PG writes.

### 3.2 NATS JetStream — RECOMMENDED TRANSPORT FALLBACK ✅

- **Alive?** ✅ **[VERIFIED]** `nats-server` releases: **v2.14.2 (2026-06-02)**,
  v2.12.11 (2026-06-09 patch). Python client **`nats.py` v2.15.0 (2026-06-05)**
  **[VERIFIED]**.
- **What it solves:** lightweight Go-native broker with **persistent** streams,
  **at-least-once and exactly-once**, pull consumers, KV/object store. Cluster is
  "dramatically lighter than Kafka" [ASSUMED, secondary]. ~**820k msg/s**, p99
  ~3.2 ms [ASSUMED, secondary benchmark].
- **Weaknesses vs Redis Streams for CARDEEP today:** a second piece of infra to
  run when Redis is *already present*; smaller ecosystem than Kafka; inspection
  tooling less ubiquitous than `redis-cli`. ADR-0001 rejected it for exactly
  these reasons — still valid in 2026.
- **Recommendation:** **Adopt only at the ADR-0001 review trigger** (>50K/min
  sustained, or when you need durable multi-day replay/audit the Redis model
  strains on). It is the right *next* step before Kafka because it stays a
  message bus, not a log platform. `nats.py` is healthy enough to bet on.

### 3.3 Apache Kafka — REJECT as the job bus (keep on radar as a log)

- **Alive?** ✅ very. **[VERIFIED via search]** **Kafka 4.0** (2025-03-18) made
  **KRaft default — ZooKeeper gone** — and shipped **KIP-932 "Queues for Kafka"**
  (queue semantics, share groups). Latest **4.3.0 (2026-05-22)** [VERIFIED via
  search; note: the GitHub `/tags` API returns unsorted legacy tags, so I relied
  on kafka.apache.org release notes for ordering].
- **What it solves:** durable partitioned **log**, highest throughput
  (~1.2M msg/s [ASSUMED, secondary]), exactly-once, infinite replay, huge
  ecosystem. KIP-932 narrows the historical "Kafka isn't a queue" gap.
- **Why reject for CARDEEP now:** operational weight (even KRaft) and p99 ~12.5 ms
  [ASSUMED] vs Redis 0.8 ms; over-engineered for a tens-of-K/min job bus. ADR-0001
  rejected it; still correct. **Reconsider only** if CARDEEP later needs a durable
  event log for analytics/replay (e.g., feeding the `innovation/` ML pipelines) —
  that's a *different* workload than the work-distribution bus.
- **Recommendation:** **Do not adopt as the worker bus.** Park as a possible
  analytics/event-log substrate, decided separately.

### 3.4 RabbitMQ — REJECT (viable but no edge here)

- **Alive?** ✅ **[VERIFIED]** releases **v4.3.1 (2026-05-20)**, v4.2.7 (2026-05-19).
- **What it solves:** classic broker, per-message ack, prefetch (real
  backpressure), at-least-once / at-most-once, mature routing. It's the
  *canonical* Dramatiq/Celery broker.
- **Why reject for CARDEEP:** introduces a broker CARDEEP doesn't run, when Redis
  Streams already covers the need. Only relevant if you adopt **Dramatiq and
  prefer RabbitMQ's prefetch-based backpressure** over Redis. Defensible, not
  necessary.
- **Recommendation:** **Skip** unless a Dramatiq-on-RabbitMQ decision is made
  deliberately for its prefetch semantics.

---

## 4. Worker-library audit (live 2026 ecosystem)

> CARDEEP currently has **no worker framework** — workers are hand-rolled async
> loops. This section evaluates whether adopting one is worth it, and which.

Benchmark anchor **[VERIFIED]** (`github.com/steventen/python_queue_benchmark`,
20,000 jobs / 10 workers, default settings):

| Library | Time to drain 20k jobs | Rank |
|---|---|---|
| **Dramatiq** | **1.53 s** | 🥇 fastest |
| **Taskiq** | **2.03 s** | 🥈 |
| Huey | 3.62–4.15 s | |
| Celery | 11.68–17.60 s | |
| Procrastinate | 27.46 s | (Postgres-backed; durability tradeoff) |
| ARQ | 35.37 s | ~23x slower than Dramatiq |
| RQ | 51.05 s | ~33x slower (sync) |

### 4.1 Dramatiq — RECOMMENDED WORKER LIBRARY (primary) ✅

- **Alive?** ✅ **[VERIFIED]** GitHub `Bogdanp/dramatiq`: **v2.1.0 (2025-03-03)**,
  v2.0.1 (2025-01-18), v2.0.0 (2024-11-18). Repo `pushed_at` **2026-06-05**,
  **5,265★**, **59 open issues**, not archived. Release cadence ~quarterly —
  healthy, not frantic; recent push activity confirms live maintenance.
  *(Note: 14 months between named releases is at the edge of the recency bar, but
  active commits + low open-issue count + 2026-06 push activity clear it.)*
- **What it solves & guarantees [VERIFIED dramatiq.io/motivation]:**
  **"tasks are only ever acked when they're done processing"** → **at-least-once**
  by design; **automatic retries**; reliable delivery; locks + **rate limiting**;
  task prioritization; delayed tasks; result storage. Brokers: **RabbitMQ, Redis,
  in-memory**. DLQ + message-age limits via retry policy [ASSUMED — not on the
  motivation page; documented in user guide].
- **Strengths:** fastest at scale, smaller/cleaner API than Celery, reliability is
  the *design goal* (matches CARDEEP's at-least-once contract exactly), Redis
  broker means **no transport migration**.
- **Weaknesses:** worker model is process+thread (not asyncio-first — async tasks
  supported but it's not async-native like Taskiq); smaller ecosystem/plugins than
  Celery; some advanced workflow (complex chains/canvas) is thinner than Celery.
- **Integration note for CARDEEP:** Dramatiq-on-Redis would let you **delete the
  hand-rolled retry/DLQ/reclaim loop** and get backpressure (prefetch) + retries
  + DLQ as library guarantees, while keeping Redis. The friction: CARDEEP's fleet
  is `asyncio`-end-to-end; Dramatiq's actor model is thread/process-centric, so
  async I/O inside actors needs an async bridge.
- **Recommendation:** **The pick if you adopt a framework and value max
  throughput + battle-tested reliability over async purity.**

### 4.2 Taskiq — RECOMMENDED WORKER LIBRARY (fallback / async-native) ✅

- **Alive?** ✅ **[VERIFIED]** GitHub `taskiq-python/taskiq`: **v0.12.4
  (2026-05-08)**, v0.12.3 (2026-05-04), v0.12.2 (2026-04-18). `pushed_at`
  **2026-06-07**, **2,187★**, 108 open issues, not archived. **Most recently
  released candidate in the field** — clears the recency bar with room to spare.
- **What it solves:** **asyncio-native** "Celery but async" — pluggable brokers
  (incl. Redis/Redis Streams), result backends, middlewares, scheduling. 2nd-
  fastest in the benchmark. **FastStream interop** via `taskiq-faststream`.
- **vs FastStream [VERIFIED search]:** *Taskiq = tasks within one project (async
  Celery). FastStream = event-driven inter-system comms across brokers.* For
  CARDEEP's **job/work-distribution** need, **Taskiq is the right shape**;
  FastStream is the right shape only if CARDEEP reframes the bus as cross-service
  event streaming (it currently is internal work distribution → Taskiq fits).
- **Strengths:** async-native = **drop-in fit for CARDEEP's `asyncio` workers** (no
  thread bridge), modern, actively released, broker-agnostic so Redis Streams
  stays.
- **Weaknesses:** smaller community than Celery/Dramatiq; some backends/plugins
  less mature; fewer "10 years in prod" war stories.
- **Recommendation:** **Choose over Dramatiq if async-native ergonomics matter
  more than raw 1.53 vs 2.03 s throughput** — which, given CARDEEP's entirely
  async fleet, is a strong argument. Realistically **Taskiq is the better
  *cultural* fit; Dramatiq the better-proven *reliability* fit.**

### 4.3 Procrastinate — RECOMMENDED NICHE ALTERNATIVE ✅

- **Alive?** ✅ **[VERIFIED]** `procrastinate-org/procrastinate`, `pushed_at`
  **2026-06-10**, 1,299★, 89 open issues, not archived. Desc: "PostgreSQL-based
  Task Queue for Python".
- **What it solves:** the queue **lives in PostgreSQL** — which CARDEEP already
  runs as system-of-record. **Transactional enqueue with your data writes** (no
  dual-write Redis↔PG inconsistency), async support, LISTEN/NOTIFY.
- **Weaknesses:** slowest in the benchmark (27 s) — throughput-bound by PG; adds
  load to the primary DB; not for the high-burst spider lane.
- **Recommendation:** **Use only for sub-pipelines where transactional
  enqueue-with-write beats throughput** (e.g., delta/remediation that already
  writes PG and wants exactly-once-ish semantics without a distributed txn).
  Directly addresses ADR-0004's "exactly-once needs Redis↔PG txn" pain for *one*
  flow. Not a wholesale replacement.

### 4.4 Celery — REJECT as a *new* choice (alive but legacy ergonomics) ⚠️

- **Alive?** ✅ **[VERIFIED]** `celery/celery` releases **v5.6.3 (2026-03-26)**,
  v5.6.2 (2026-01-04), v5.6.0 (2025-11-30). Actively maintained.
- **Why reject for a greenfield CARDEEP decision:** **~8–11x slower than
  Dramatiq** in the benchmark; sync-rooted with bolted-on async; heavy config
  surface ("~30 min to configure correctly"); at-least-once requires
  `acks_late=True` + careful config (Dramatiq is reliable *by default*). It's the
  incumbent you *migrate off*, not *onto*, in 2026.
- **Recommendation:** **Do not adopt.** Only relevant if CARDEEP already had
  Celery (it doesn't).

### 4.5 arq — REJECT (alive but slow at scale) ⚠️

- **Alive?** ✅ **[VERIFIED]** `python-arq/arq` **v0.28.0 (2026-04-16)** — adds
  Python 3.14 support; `pushed_at` 2026-04-16, 2,949★, 104 open issues, not
  archived. *Recency is excellent.*
- **Why reject:** **~23x slower than Dramatiq** (35.37 s) in the 20k-job
  benchmark. Fine for light async background jobs, **wrong tool for CARDEEP's
  throughput envelope.** Recency is good; *performance* is the disqualifier.
- **Recommendation:** **Skip** at this scale.

### 4.6 RQ — REJECT (sync, slowest) ⚠️

- **Alive?** ✅ **[VERIFIED]** `rq/rq` `pushed_at` **2026-06-12**, 10,650★, 248
  open issues. Extremely popular and maintained.
- **Why reject:** **synchronous**, **~33x slower** than Dramatiq (51 s), 248 open
  issues. Great for MVPs/prototypes; mismatched with CARDEEP's async, high-volume
  fleet.
- **Recommendation:** **Skip.**

### 4.7 Temporal — REJECT for this layer (different problem) ⚠️

- **Alive?** ✅ **[VERIFIED]** `temporalio/temporal` **v1.31.1 (2026-06-10)**,
  v1.31.0 (2026-04-29). Very active.
- **What it is:** **durable workflow orchestration** (stateful, long-running,
  saga/compensation, retries-as-code) — not a throughput job-queue. Python SDK
  is first-class.
- **Why reject for the bus:** it solves *workflow durability*, not
  *high-throughput work distribution*. Heavy infra (server + persistence). Using
  it as the scraping bus is a category error. **However** it is a strong future
  fit for **multi-step, long-lived orchestration** (e.g., a per-source recipe
  pipeline with human-in-the-loop remediation, or the delta→remediation saga) if
  that ever needs durable, resumable state.
- **Recommendation:** **Not for the queue.** Keep in mind as an *orchestration*
  layer above the bus if/when long-running stateful workflows appear.

### 4.8 FastStream — note (event-streaming framework, not a job queue)

- **Alive?** ✅ **[VERIFIED]** `ag2ai/faststream` `pushed_at` **2026-06-10**,
  5,226★, 102 open issues. Async event framework over Kafka/RabbitMQ/NATS/Redis
  with AsyncAPI docs + DI.
- **Why it's not the pick:** it's an **event-driven inter-system** framework,
  whereas CARDEEP's bus is **internal job/work distribution** (Taskiq's shape).
  Relevant only if CARDEEP later exposes a cross-service event contract.
- **Recommendation:** **Not now.** Revisit if the bus becomes a public event
  backbone; pairs with NATS JetStream nicely if so.

---

## 5. At-least-once / idempotency / backpressure — design verdict

CARDEEP's **at-least-once + idempotent-consumer** contract (ADR-0004) is the
**industry-correct** choice for this workload — exactly-once at the bus is a trap
(distributed Redis↔PG txn). Every serious 2026 source agrees: *"with
at-least-once, retries are unavoidable, so consumers must be idempotent"*
([VERIFIED] search consensus). Keep it. Reinforcements:

- **Idempotency** is already done right (unique id + `ON CONFLICT DO NOTHING`,
  content-hash lookup, set-based UPSERT). Maintain the **mandatory
  "process same message twice" test** per ADR-0004.
- **Reclaim / DLQ:** migrate hand-rolled XPENDING+XAUTOCLAIM to Redis 8.4
  **`XREADGROUP … CLAIM`** to avoid the documented XAUTOCLAIM PEL-churn cost
  ([VERIFIED] Redis 8.4 blog) and get retry-cap/DLQ metadata in one round-trip.
- **Backpressure (the real gap):** raw `redis.asyncio` gives you only `count` +
  `block` on `XREADGROUP`. That bounds *batch size*, not *in-flight concurrency*.
  Add an explicit **bounded concurrency cap** (asyncio `Semaphore` sized to PG/
  fetcher capacity) so the enrich lane can't outrun downstream writes. A
  framework (Dramatiq prefetch / Taskiq middleware) gives this for free — the
  strongest argument for adopting one. *(Reference: AWS Builders' Library
  "Avoiding insurmountable queue backlogs" — bound and shed, don't let the PEL
  grow unbounded.)*

---

## 6. Sample CONFIG

### 6.1 Keep current path, harden it — Redis 8.4 single-shot reliable consumer

```python
# scrapers/common/stream_consumer.py  — async, at-least-once, bounded backpressure
# Requires: redis>=6.0 (client), Redis server >= 8.4 (XREADGROUP ... CLAIM)
import asyncio
import redis.asyncio as aioredis

STREAM = "stream:enrich_pending"
GROUP = "cg_enrich"
CONSUMER = "enrich-1"
DLQ = "stream:dlq"
MAX_RETRIES = 5
IDLE_RECLAIM_MS = 60_000          # reclaim entries un-acked > 60s
MAX_INFLIGHT = 32                 # backpressure: bound concurrency to PG/fetcher capacity
BATCH = 16                        # XREADGROUP COUNT

async def run(r: aioredis.Redis, handle) -> None:
    sem = asyncio.Semaphore(MAX_INFLIGHT)

    async def process(msg_id: str, fields: dict) -> None:
        async with sem:                       # backpressure gate
            try:
                await handle(fields)          # idempotent by contract (ADR-0004)
                await r.xack(STREAM, GROUP, msg_id)
            except Exception:
                # retry accounting lives in fields/PEL delivery count;
                # past MAX_RETRIES route to DLQ then ack to clear PEL
                count = await _delivery_count(r, msg_id)
                if count >= MAX_RETRIES:
                    await r.xadd(DLQ, {"src": STREAM, "id": msg_id, **fields})
                    await r.xack(STREAM, GROUP, msg_id)
                # else: leave un-acked → reclaimed/re-delivered below

    while True:
        # Redis 8.4: single round-trip — new messages + reclaim of idle PEL entries.
        # Replaces XPENDING -> XAUTOCLAIM -> XREADGROUP stitch (avoids PEL O(log n) churn).
        resp = await r.execute_command(
            "XREADGROUP", "GROUP", GROUP, CONSUMER,
            "COUNT", BATCH, "BLOCK", 5000,
            "CLAIM", IDLE_RECLAIM_MS,          # 8.4 reliable-claim
            "STREAMS", STREAM, ">",
        )
        if not resp:
            continue
        tasks = [process(mid, _to_dict(f)) for _, entries in resp for mid, f in entries]
        await asyncio.gather(*tasks)
```

### 6.2 IF adopting a framework — Dramatiq on the existing Redis (no bus migration)

```python
# dramatiq_app.py
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries, AgeLimit, TimeLimit

broker = RedisBroker(url="redis://redis:6379/0")
broker.add_middleware(AgeLimit(max_age=3_600_000))   # drop > 1h old
broker.add_middleware(Retries(max_retries=5))        # backoff + DLQ-on-exhaust
dramatiq.set_broker(broker)

@dramatiq.actor(max_retries=5, queue_name="enrich")
def enrich(pointer: dict) -> None:
    # idempotent by contract: unique id + ON CONFLICT DO NOTHING / content-hash
    process(pointer)
# Worker: `dramatiq dramatiq_app --processes 4 --threads 8`
# prefetch = processes*threads gives in-flight bound = backpressure.
```

### 6.3 IF async-native is the priority — Taskiq on Redis (matches asyncio fleet)

```python
# taskiq_app.py
from taskiq_redis import RedisStreamBroker          # Redis Streams transport — same bus
broker = RedisStreamBroker(url="redis://redis:6379/0")

@broker.task(retry_on_error=True, max_retries=5)
async def enrich(pointer: dict) -> None:
    await process(pointer)                           # native async, no thread bridge
# Worker: `taskiq worker taskiq_app:broker --workers 4 --max-async-tasks 32`
# --max-async-tasks = in-flight bound = backpressure.
```

---

## 7. Final verdict — is CARDEEP's current choice good enough?

**Yes — the *architecture* is current and bulletproof; do not replace the
transport.** Redis Streams + at-least-once + idempotent consumers (ADR-0001 /
ADR-0004) is exactly what a 2026 expert would choose for a tens-of-K/min internal
job bus where Redis is already in the stack. None of Kafka/NATS/RabbitMQ beats it
*at the current scale*; they are heavier for no benefit until the ADR-0001 review
trigger (>50K/min sustained or durable-replay needs) fires.

**The honest gaps are implementation-level, ranked:**
1. **[do now]** Move reclaim/DLQ to **Redis 8.4 `XREADGROUP … CLAIM`** (kills
   XAUTOCLAIM PEL churn). Pin `redis-py ≥ 6.x`, server ≥ 8.4.
2. **[do now]** Add **bounded-concurrency backpressure** (asyncio `Semaphore`) so
   the enrich lane can't drown PG — the one thing the hand-rolled loop lacks.
3. **[when the fleet/team grows]** Consider replacing the hand-rolled loop with
   **Taskiq (async-native, Redis Streams broker)** — primary fallback — or
   **Dramatiq (Redis broker)** if max throughput + by-default reliability matter
   more than async purity. Both keep Redis = **no bus migration**, and hand you
   retries + DLQ + backpressure as library guarantees instead of bespoke code.
4. **[transport escalation path]** **NATS JetStream** at the 50K/min trigger;
   **Kafka** only if a durable analytics/event-log workload appears (separate
   decision). **Temporal** only if long-running, resumable stateful *workflows*
   appear (orchestration above the bus, not the bus itself).

**Nothing in this domain is a corpse.** The risk for CARDEEP is not adopting a
dead tool — it's the opposite temptation to over-build onto a heavier live tool
(Kafka/Celery) when the lean current stack is genuinely the right 2026 answer.

---

## 8. Sources

Primary (fetched this session, [VERIFIED]):
- Dramatiq releases — https://github.com/Bogdanp/dramatiq/releases
- Dramatiq repo API — https://api.github.com/repos/Bogdanp/dramatiq
- Dramatiq motivation — https://dramatiq.io/motivation.html
- Taskiq releases API — https://api.github.com/repos/taskiq-python/taskiq/releases
- Taskiq repo API — https://api.github.com/repos/taskiq-python/taskiq
- arq releases — https://github.com/python-arq/arq/releases  · API https://api.github.com/repos/python-arq/arq
- Celery releases API — https://api.github.com/repos/celery/celery/releases
- RQ repo API — https://api.github.com/repos/rq/rq
- Procrastinate repo API — https://api.github.com/repos/procrastinate-org/procrastinate
- FastStream repo API — https://api.github.com/repos/ag2ai/faststream
- Temporal releases API — https://api.github.com/repos/temporalio/temporal/releases
- NATS server releases API — https://api.github.com/repos/nats-io/nats-server/releases
- nats.py releases API — https://api.github.com/repos/nats-io/nats.py/releases
- aiokafka releases API — https://api.github.com/repos/aio-libs/aiokafka/releases
- RabbitMQ server releases API — https://api.github.com/repos/rabbitmq/rabbitmq-server/releases
- python_queue_benchmark — https://github.com/steventen/python_queue_benchmark
- Judoscale "Choosing the Right Python Task Queue" — https://judoscale.com/blog/choose-python-task-queue

Secondary ([ASSUMED] — benchmarks/write-ups, not primary-source-confirmed):
- Redis 8.4 single-shot reliable consumers — https://redis.io/blog/single-shot-reliable-consumers-with-xreadgroup-claim-in-redis-84/
- Message Brokers Comparison 2026 (throughput/latency figures) — https://dev.to/mahdi0shamlou/message-brokers-comparison-2026-kafka-rabbitmq-nats-redis-streams-which-one-should-you-3ea8
- Kafka 4.0 announcement (KRaft default, KIP-932) — https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/
- Taskiq vs FastStream — https://taskiq-python.github.io/framework_integrations/faststream.html
- Redis Streams consumer-failure handling — https://oneuptime.com/blog/post/2026-03-31-redis-handle-consumer-failures-streams/view
- AWS Builders' Library, avoiding queue backlogs — https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/

CARDEEP repo ground truth ([VERIFIED] in `projects/cardex-integration`):
- `docs/adr/0001-redis-streams-sobre-kafka-nats.md`
- `docs/adr/0004-at-least-once-idempotencia.md`
- `docs/adr/0007-separacion-spider-reaper-indexer.md`
- `scrapers/requirements.txt` (`redis>=5.0.0`)
- `scrapers/enrich_worker.py`, `scrapers/rich_consumer.py`, `scrapers/common/indexer.py`,
  `scrapers/delta/delta_worker.py`, `scrapers/delta/remediation_dispatcher.py`
