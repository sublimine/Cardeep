# T14 — API Framework + Async Data Layer: Live 2026 Tooling Audit

> **Domain:** The HTTP serving layer for CARDEEP — the framework that exposes
> per-entity inventory, per-platform inventory, and live delta over the PostgreSQL
> backbone; the async PostgreSQL driver beneath it (raw `asyncpg` vs SQLAlchemy 2.0
> vs Rust-native); the ASGI/RSGI server in front (uvicorn vs Granian); and the
> pagination + caching primitives needed to serve these surfaces at scale.
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I
> fetched its PyPI / GitHub / benchmark page this session, URL cited) or
> **[ASSUMED]** (inferred, not opened). No corpses are recommended.
>
> **Recency bar:** a library with no release in ~12 months is *suspect*; no commit
> in ~12 months is *dead for our purposes*. Stated explicitly per tool. Today's
> reference clock for "months since release" is **2026-06**.

---

## 0. The incumbent — what CARDEEP actually runs today

Read this session **[VERIFIED]**:

- **`services/api/main.py`** — `FastAPI(title="Cardeep API", version="0.1.0", lifespan=...)`,
  served by `uvicorn`. Data access is **raw `asyncpg`** via a single shared pool
  (`asyncpg.create_pool(DSN, min_size=1, max_size=8)`) created in an
  `@asynccontextmanager lifespan`. **No SQLAlchemy, no ORM.**
- **Envelope:** every handler returns `JSONResponse({"ok", "data", "error", "meta"})`
  through tiny `ok()` / `err()` helpers. This is a deliberate, consistent contract.
- **Endpoints today:** `/health`, `/entities/{cdp_code}`,
  `/entities/{cdp_code}/inventory`, `/entities/{cdp_code}/delta?since=`,
  `/geo/{province_code}/entities`.
- **`requirements.txt` [VERIFIED]** pins exactly: `asyncpg>=0.29,<0.31`,
  `fastapi>=0.110`, `uvicorn[standard]>=0.29`, `openpyxl>=3.1`.

Load-bearing observations for the pick:

1. **No pagination anywhere.** `/inventory` does `ORDER BY first_seen DESC` with **no
   LIMIT**; `/delta` without `since` is capped at a hard `LIMIT 500`. At 333k+
   vehicles and growing, an unbounded inventory fetch for a large dealer is a latency
   and memory hazard. **This is the real scaling gap — not the framework.**
2. **No caching layer.** Every request hits Postgres. Inventory and province
   listings are read-heavy and highly cacheable (ETag off `last_seen`/`max(observed_at)`).
3. **Hand-rolled serialization.** Each handler manually stringifies `datetime` and
   floats `Decimal`. This is exactly the boilerplate a typed framework (msgspec-based)
   removes — but it also means **there is no Pydantic dependency to "lose"** by moving.
4. **Tiny surface.** 5 endpoints, GET-only, one envelope. A framework migration here
   is cheap *mechanically* but earns little unless it fixes (1) and (2).

So the question is not "is FastAPI fashionable" — it is: **does any 2026 alternative
fix the pagination/caching/serialization gaps materially better than hardening the
incumbent?** The honest answer below is **no, not enough to justify a rewrite** — but
the *driver* and the *server* choices are worth revisiting, and the missing
pagination/caching libraries are a real greenfield pick.

---

## 1. Verdict up front

| Layer | Pick | Status | Why |
|---|---|---|---|
| **Web framework** | **FastAPI** (keep) | ✅ **alive** (0.136.3, 2026-05-23) | Already in use, healthiest ecosystem, the gap to Litestar vanishes under DB-bound load. Migration earns little on a 5-endpoint GET API |
| **Framework — modern challenger** | **Litestar 2.24** | ✅ **alive** (2.24.0, 2026-06-11) | Genuinely faster (msgspec native), batteries-included, *better* DTO/pagination/cache stories. The pick **only if** a from-scratch rewrite or a perf-critical fan-out service is on the table |
| **Framework — reject for this role** | **Robyn** | 🟡 alive but unfit (0.85.0, 2026-04-29) | Fast Rust runtime, but **no first-class async Postgres/ORM, no pagination, thinner prod story**. Wrong tool for a DB-bound data API |
| **ASGI/RSGI server** | **Granian** (adopt) ▸ uvicorn (fallback) | ✅ **alive** (2.7.6, 2026-06-10) | Rust/Tokio, higher + more *consistent* tail latency, ASGI-drop-in for FastAPI, RSGI if we ever go native. Lowest-risk real upgrade available today |
| **Async PG driver** | **asyncpg** (keep) | ✅ **alive** (0.31.0, 2025-11-24) | Fastest mature pure-async driver, already in use, py3.13/3.14 wheels incl. free-threaded. **Bump pin to allow 0.31** |
| **ORM / query layer** | **SQLAlchemy 2.0 (asyncio) — optional, scoped** | ✅ **alive** (2.0.50, 2026-05-24) | Adopt *only* if/when query complexity (joins across entity/vehicle/event/platform) outgrows hand SQL. Not needed for today's 5 endpoints |
| **PG driver — Rust challenger** | **psqlpy** | 🟡 **young** (0.12.0, 2026-05-22) | Rust/tokio-postgres, fast, real 2026 cadence — but **356★, 12 open issues, pre-1.0**. Watch, don't bet the serving path on it yet |
| **Pagination** | **fastapi-pagination** | ✅ **alive** (0.15.14, 2026-05-30) | Cursor + page strategies, async SQLAlchemy/raw support. Fixes the unbounded-inventory gap |
| **Caching** | **fastapi-cache2-fork** ▸ Redis (`redis.asyncio`) | ✅ **alive** (2.3.0, 2026-01-28) | The **maintained, msgspec-based** fork. The original `fastapi-cache2` is **stale** (see below) |
| **Caching — DO NOT adopt original** | `fastapi-cache2` | 🟡 **stale** (0.2.2, 2024-07-24) | ~23 months no release. Use the fork or roll ETag + `redis.asyncio` directly |
| **Caching — borderline** | `aiocache` | 🟡 **slowing** (0.12.3, 2024-09-25) | ~21 months no release. Works, multi-backend, but cadence stalled. Prefer `redis.asyncio` directly |

**Bottom line:** **CARDEEP's current choice (FastAPI + uvicorn + raw asyncpg) is good
enough and should stay** — it is not a corpse, the ecosystem is the healthiest of any
Python web stack, and on a DB-bound API the synthetic edge of the challengers
evaporates. The **three concrete, low-risk upgrades** that actually move the needle are
(a) **swap uvicorn → Granian** for tail-latency + throughput at near-zero code cost,
(b) **add `fastapi-pagination`** to kill the unbounded `/inventory` query, and
(c) **add `fastapi-cache2-fork` + `redis.asyncio` + ETags** for read-heavy surfaces.
**Litestar is the fallback/alternative** and the right call *only* on a clean-slate
rewrite or a dedicated high-fan-out service. **Robyn is rejected** for this role.

---

## 2. Web framework — the headline decision

### 2.1 FastAPI — **RECOMMENDED (keep)** ✅

- **PyPI:** https://pypi.org/project/fastapi/ — **[VERIFIED]** latest **0.136.3, released
  2026-05-23**. Recent cadence: 0.136.1 (2026-04-23), 0.136.0 / 0.135.4 (2026-04-16),
  0.135.3 (2026-04-01). **Python >=3.10** (3.10–3.14).
- **Alive?** Emphatically. Multiple releases in 2026, by far the largest plugin/middleware
  ecosystem of any async Python framework **[VERIFIED via PyPI cadence + ecosystem search]**.

**What it solves.** ASGI app + dependency injection + automatic OpenAPI + Pydantic-based
(de)serialization. CARDEEP uses almost none of the Pydantic machinery — it hand-builds
`JSONResponse` envelopes — so FastAPI is effectively acting as a thin router here.

**Strengths.**
- Already integrated; zero migration risk.
- Best-in-class ecosystem: `fastapi-pagination`, `fastapi-cache2-fork`,
  `slowapi` (rate-limit), auth middlewares — all the T14 sub-pieces have a FastAPI plug.
- Huge hiring/knowledge surface; least operational surprise.

**Weaknesses.**
- Pydantic-v2 serialization is the slowest part of the stack vs msgspec — but **CARDEEP
  bypasses it** with manual `JSONResponse`, so this weakness barely applies today.
- No built-in pagination or cache (must add libraries — see §5, §6).

**Recommendation.** **Keep.** The migration cost-to-benefit on a 5-endpoint GET API is
negative. Spend the effort on Granian + pagination + caching instead.

### 2.2 Litestar — **RECOMMENDED FALLBACK / rewrite-only pick** ✅

- **PyPI:** https://pypi.org/project/litestar/ — **[VERIFIED]** latest **2.24.0, released
  2026-06-11** (i.e. *yesterday*). Cadence: 2.23.0 (2026-05-29), 2.22.0 (2026-05-20),
  2.21.1 (2026-03-07). **Python >=3.8,<4.0** (3.8–3.14).
- **GitHub:** https://github.com/litestar-org/litestar — **[VERIFIED]** **8.3k★**, **216 open
  issues**, ~3,442 commits, "5 - Production/Stable", 300+ contributors, multi-maintainer
  team (Hirschfeld, Schutt, Fincher, Mikhailov, …). Healthy bus factor.
- **Alive?** Yes — one of the most active Python web frameworks in 2026.

**What it solves.** A batteries-included ASGI framework that uses **msgspec** natively for
(de)serialization instead of Pydantic, plus first-party DTOs, an offset/cursor
**pagination** abstraction, a **response-cache** store, plugins (incl. SQLAlchemy/Advanced
Alchemy), and DI. It bundles much of what FastAPI needs add-ons for.

**Performance — verified, with honest framing.**
- msgspec is **~10–20× faster than Pydantic v2** for (de)serialization, ~24× on nested
  structures, ~6× on simple ones **[VERIFIED — byteiota 2026 analysis]**
  (https://byteiota.com/litestar-vs-fastapi-python-speed-test-2026-analysis/).
- Migration reports cite **40–120% throughput gains** moving FastAPI→Litestar **[VERIFIED,
  same source]**.
- **The caveat that matters [VERIFIED — Better Stack + tanrax benchmark repo]:** *"Litestar
  wins synthetic charts; FastAPI wins almost every real production decision; the difference
  rarely shows up in user-facing latency… under realistic database-paginated workloads the
  gap narrows to within network and database variance."* CARDEEP requests **all block on
  Postgres** → the serialization edge is largely masked.

**Strengths.** Faster ceiling; cleaner built-in pagination/cache/DTO; msgspec means no
manual `datetime`/`Decimal` stringifying; strong, multi-maintainer project.

**Weaknesses.** Smaller ecosystem than FastAPI; a full rewrite of the router + envelope
contract; the perf win is mostly invisible on a DB-bound API.

**Recommendation.** **Fallback / future.** Pick Litestar **only** if (a) we green-field a
new high-throughput service (e.g. a public fan-out inventory feed that serializes large
JSON arrays hot), or (b) we decide to rebuild the API from scratch anyway. For the current
service, the ROI does not clear the migration bar.

### 2.3 Robyn — **REJECT for this role** 🟡 (alive, but unfit)

- **GitHub:** https://github.com/sparckles/Robyn — **[VERIFIED]** **7.3k★**, **123 open
  issues**, ~804 commits. **PyPI/releases [VERIFIED]:** **0.85.0 (2026-04-29)**, 0.84.0
  (2026-04-26), 0.83.0 (2026-03-28). **Python >=3.10.** Actively developed.
- **Alive?** Yes — frequent 2026 releases, Rust (Tokio) runtime, multi-core, auto-OpenAPI,
  DI, WebSockets, even MCP support.

**Why it's the wrong tool here [VERIFIED — repo docs do not surface any first-class async
Postgres / ORM / pagination story].** CARDEEP is a **database-bound** read API. Robyn's
value proposition is a fast HTTP runtime, but it provides **no first-class async Postgres
integration, no ORM, no pagination framework**, and a thinner production-deployment story
than FastAPI/Litestar. You would re-implement everything CARDEEP already gets for free,
and the Rust-runtime speed is irrelevant when every handler awaits a SQL round-trip.

**Recommendation.** **Do not adopt for the inventory/delta API.** Not a corpse — just the
wrong shape for a DB-heavy data service.

### 2.4 Framework scoreboard

| Framework | Latest / date | ★ | Open iss. | Serializer | Built-in pagination | Built-in cache | Async PG story | Verdict for CARDEEP |
|---|---|---|---|---|---|---|---|---|
| **FastAPI** | 0.136.3 / 2026-05-23 | (huge) | — | Pydantic v2 (bypassed here) | via lib | via lib | excellent (asyncpg/SQLA) | ✅ **keep** |
| **Litestar** | 2.24.0 / 2026-06-11 | 8.3k | 216 | **msgspec** | **built-in** | **built-in** | excellent (Advanced Alchemy) | ✅ fallback / rewrite-only |
| **Robyn** | 0.85.0 / 2026-04-29 | 7.3k | 123 | own | none | none | weak/none | 🟡 reject for this role |

---

## 3. ASGI / RSGI server — the highest-ROI real upgrade

### 3.1 Granian — **RECOMMENDED (adopt)** ✅

- **PyPI:** https://pypi.org/project/granian/ — **[VERIFIED]** latest **2.7.6, released
  2026-06-10**. **Python >=3.10.**
- **GitHub:** https://github.com/emmett-framework/granian — **[VERIFIED via vendor/PyPI]**
  Rust HTTP server (Tokio). **Supports ASGI/3, RSGI, and WSGI; HTTP/1 + HTTP/2; WebSockets.**
  Stated production users include Microsoft, Mozilla, Sentry **[VERIFIED — PyPI/vendor copy]**.
- **Alive?** Yes — June 2026 release, official benchmark suite re-run **2026-04-07** on
  Granian 2.7.3 **[VERIFIED — search of granian benchmarks/vs.md]**.

**What it solves.** A drop-in replacement for `uvicorn` that runs the **same FastAPI ASGI
app** with a Rust I/O core. Optional **RSGI** protocol if we ever move to a Granian-native
framework (Emmett/Litestar-on-RSGI), but **no app change is needed** to benefit on ASGI.

**Performance — verified, honestly framed.**
- Granian posts the **highest RPS** and a **tighter latency distribution** — avg-to-max
  latency gap ≈ **2.8×** vs uvicorn's ≈ **6.8×** **[VERIFIED — hashhackers ASGI comparison]**
  (https://blog.hashhackers.com/blog/granian-uvicorn-asgi/). Consistent tail latency is the
  real win for an SLO-bound API.
- **Caveat [VERIFIED — deployhq 2026 + thenerdnook]:** on a typical CRUD API where each
  request blocks on a DB query, the throughput gap shrinks to **~10%**; the big gains are in
  connection-heavy, low-logic paths. CARDEEP's `/health` and cached reads benefit most.

**Strengths.** Zero app rewrite (ASGI). Better p99 tail latency. HTTP/2. RSGI optionality.
Single binary, good worker/threading model.

**Weaknesses.** Smaller operational track record than uvicorn; fewer SO answers; if
something is weird at 3 a.m., uvicorn is the better-documented fallback.

**Recommendation.** **Adopt as the production server**, keep uvicorn as the dev/fallback
runner. This is the **single best risk-adjusted upgrade** in T14: real, measurable, and
the code change is a process-launch line, not a refactor.

### 3.2 uvicorn — **RECOMMENDED FALLBACK** ✅

- **[VERIFIED]** in `requirements.txt` as `uvicorn[standard]>=0.29`; the most widely
  deployed ASGI server, battle-tested **[VERIFIED — deployhq 2026 guidance]**.
- **Recommendation.** Keep as the default for local dev and as the production fallback if
  Granian ever misbehaves. Per the same 2026 guidance: *"if you have no specific reason to
  push raw req/sec, uvicorn (under Gunicorn for prod) is the safer, lower-operational-cost
  choice."* Granian is the upgrade; uvicorn is the safety net.

---

## 4. Async data layer — driver + (optional) ORM

### 4.1 asyncpg — **RECOMMENDED (keep, bump pin)** ✅

- **PyPI:** https://pypi.org/project/asyncpg/ — **[VERIFIED]** latest **0.31.0, released
  2025-11-24**; prior 0.30.0 (2024-10-20). **Ships cp313 + cp314 wheels incl.
  `cp314-cp314t` (free-threaded)**; min **Python >=3.9**.
- **Alive?** Yes — 0.31.0 is a 2025-Q4 release with explicit 3.13/3.14 support. Slow-but-deliberate
  cadence is normal for a mature driver, **not** a death signal.

**What it solves.** The fastest mature pure-async Postgres driver for Python; binary
protocol, prepared-statement cache, native pooling — exactly what `main.py` already uses.

**Action item [VERIFIED gap].** `requirements.txt` pins `asyncpg>=0.29,<0.31`, which
**excludes 0.31.0**. Bump to `asyncpg>=0.30,<0.32` to pick up the 3.13/3.14 wheels and
latest fixes.

**Recommendation.** **Keep.** No better mature pure-async driver exists. Raw asyncpg + the
`{ok,data,error,meta}` envelope is a perfectly good, low-dependency serving path for this
query shape.

### 4.2 SQLAlchemy 2.0 (asyncio) — **OPTIONAL, scoped** ✅

- **PyPI:** https://pypi.org/project/SQLAlchemy/ — **[VERIFIED]** latest **2.0.50, released
  2026-05-24**; steady patch cadence (2.0.49 2026-04-03, 2.0.48 2026-03-02, …). **2.1.0b2**
  pre-release exists (2026-04-16) → 2.1 in active dev.
- **Alive?** Yes — the canonical Python ORM/Core, async engine over asyncpg is first-class.

**What it solves.** Typed query construction, relationship loading, and migrations (with
Alembic) when SQL gets complex — e.g. joining `entity × vehicle × vehicle_event ×
platform_membership` for per-platform inventory views. Its **async Core** can run over
asyncpg and still hand back rows without forcing the full ORM.

**Recommendation.** **Adopt later, only if needed.** Today's five GET endpoints are simple,
single-table-ish reads where hand SQL is clearer and faster to reason about. Introduce
SQLAlchemy 2.0 **Core (async)** the moment multi-join per-platform aggregations or a
migration discipline are required — not before. Avoid the full ORM identity-map on the hot
read path; use Core or keep asyncpg for those.

### 4.3 psqlpy — **WATCH, do not bet the serving path yet** 🟡

- **GitHub:** https://github.com/psqlpy-python/psqlpy — **[VERIFIED]** latest **0.12.0
  (2026-05-22)**, **356★**, **12 open issues**, 71 releases, ~58% Rust / ~41% Python,
  Python 3.10–3.14.
- **Alive?** Yes, active 2026 cadence — but **pre-1.0 and small adoption**.

**What it solves.** A Rust (tokio-postgres) async Postgres driver positioned as faster +
more type-safe than asyncpg. Promising, genuinely maintained.

**Recommendation.** **Watch-list, not production.** 356★ and a sub-1.0 version on the
*critical data path* of "the greatest scraping/indexing system" is an unjustified risk
while asyncpg (battle-tested, free-threaded-ready) exists. Re-evaluate at ≥1.0 with broader
adoption.

---

## 5. Pagination — fixing the unbounded-inventory gap

### 5.1 fastapi-pagination — **RECOMMENDED** ✅

- **PyPI:** https://pypi.org/project/fastapi-pagination/ — **[VERIFIED]** latest **0.15.14,
  released 2026-05-30**; multiple releases/month through 2025–2026. **Python >=3.10–3.14.**
  Optional extras for `sqlalchemy` / `sqlmodel`. **Cursor-based + page-based** strategies.
- **Alive?** Yes — very active.

**What it solves.** Adds `limit/offset` **and cursor** pagination with a typed response
shape, integrating with async SQLAlchemy and (with a params object) raw queries. Directly
addresses the unbounded `SELECT … ORDER BY first_seen DESC` in `/inventory` and the hard
`LIMIT 500` in `/delta`.

**Integration note.** Keep the `{ok,data,error,meta}` envelope: put page/cursor info in
`meta` (`total`, `cursor`, `limit`) rather than adopting the library's default top-level
shape — wrap its output. For a pure-asyncpg path, **cursor pagination is trivial to keep
hand-rolled** (`WHERE first_seen < $cursor ORDER BY first_seen DESC LIMIT $n`) and may be
preferable to a dependency. **Recommendation: add `fastapi-pagination` if you want a
ready typed abstraction; otherwise hand-roll keyset/cursor pagination on asyncpg — either
fixes the gap. Do not ship unbounded queries.**

---

## 6. Caching — read-heavy inventory + province listings

### 6.1 fastapi-cache2-fork — **RECOMMENDED** ✅ (the maintained fork)

- **PyPI:** https://pypi.org/project/fastapi-cache2-fork/ — **[VERIFIED]** latest **2.3.0,
  released 2026-01-28**; 2.2.2 (2025-11-26), 2.2.1 (2025-07-24), 2.0.0 (2025-04-30).
  Maintained by *Yolley*; **uses msgspec** for JSON encode/decode where possible.
- **Alive?** Yes — active 2025–2026 cadence.

**What it solves.** Decorator-style response caching with **Redis / memcached / in-memory**
backends and **HTTP cache headers (ETag, Cache-Control, conditional If-None-Match)** — the
exact primitives for inventory/province endpoints.

### 6.2 fastapi-cache2 (original) — **DO NOT adopt** 🟡 stale

- **PyPI:** https://pypi.org/project/fastapi-cache2/ — **[VERIFIED]** latest **0.2.2,
  released 2024-07-24** (prior 0.2.1 was 2023-02-15). **~23 months since last release.**
- **Recommendation.** **Avoid.** Use `fastapi-cache2-fork` (the live successor) or roll
  ETag + `redis.asyncio` directly. Not a hard corpse, but past the 12-month suspect bar
  with no successor activity on the original line.

### 6.3 aiocache — **borderline** 🟡

- **PyPI:** https://pypi.org/project/aiocache/ — **[VERIFIED]** latest **0.12.3, released
  2024-09-25**. ~21 months since release. Multi-backend (memory/redis/memcached), async.
- **Recommendation.** Works, but cadence has stalled past the suspect bar. **Prefer
  `redis.asyncio` (a.k.a. `aioredis`) directly** for the shared cache — it is the
  asyncio-native, maintained path **[VERIFIED — 2026 best-practice search]**.

### 6.4 Recommended caching architecture

1. **Protocol layer:** compute **ETag from `last_seen` / `max(observed_at)`** per entity;
   honor `If-None-Match` → `304`. Cheap, correct, and offloads unchanged inventory.
2. **Shared layer:** **Redis via `redis.asyncio`**, keyed on full input (`cdp_code`,
   pagination cursor, `since`). Short TTL first, lengthen with confidence (SLO-aware).
3. **Convenience:** wrap (1)+(2) with **`fastapi-cache2-fork`** if you want decorators
   instead of hand-rolled logic. **[VERIFIED — multi-layer pattern, greeden/uplatz 2026.]**

---

## 7. Is CARDEEP's current choice good enough — and what replaces it?

**Yes — the FastAPI + uvicorn + raw-asyncpg core is good enough and stays.** None of the
challengers is a corpse, but none clears the rewrite bar for a 5-endpoint, DB-bound GET API:
- **Litestar** is faster on paper (msgspec) and has nicer built-ins, but the edge is masked
  by Postgres round-trips and the migration cost is real. → **Fallback / rewrite-only.**
- **Robyn** lacks the async-Postgres/pagination story this service depends on. → **Reject
  for this role.**
- **asyncpg** remains the best mature async driver; **SQLAlchemy 2.0 Core (async)** waits in
  the wings for when joins get complex; **psqlpy** is a watch-list Rust contender, not yet
  trustworthy on the hot path.

**What actually changes (ordered by ROI, all low-risk):**

1. **Swap uvicorn → Granian** in production (keep uvicorn for dev/fallback). Same ASGI app,
   better + more consistent tail latency, HTTP/2, RSGI optionality. *Highest ROI, near-zero
   code.*
2. **Add pagination** to `/inventory` (and lift `/delta`'s hard 500): `fastapi-pagination`
   **or** hand-rolled keyset/cursor on asyncpg. *Closes the only real scaling defect.*
3. **Add caching:** ETag (off `last_seen`/`max(observed_at)`) + `redis.asyncio`, optionally
   via `fastapi-cache2-fork`. *Cuts Postgres load on read-heavy surfaces.*
4. **Bump the asyncpg pin** `>=0.30,<0.32` to allow 0.31.0 (py3.13/3.14 + free-threaded
   wheels).
5. **Defer** SQLAlchemy 2.0 until multi-join per-platform aggregations or migrations demand
   it; **defer** psqlpy until ≥1.0; **do not** migrate to Litestar/Robyn for this service.

**Explicit DEAD / stale flags (do not adopt):**
- `fastapi-cache2` (original) — **stale**, 0.2.2 / 2024-07-24 (~23 mo). Use the fork.
- `aiocache` — **borderline-stale**, 0.12.3 / 2024-09-25 (~21 mo). Prefer `redis.asyncio`.
- **No hard corpse** among the framework/server/driver candidates — all had 2025-Q4–2026
  releases.

---

## 8. Sample config / integration sketches

### 8.1 `requirements.txt` deltas (additive, verified versions)

```text
# --- API serving (T14) ---
fastapi>=0.110                 # keep (latest 0.136.3, 2026-05-23) [VERIFIED]
asyncpg>=0.30,<0.32            # BUMP: was >=0.29,<0.31; unlock 0.31.0 (2025-11-24, py3.13/3.14) [VERIFIED]
uvicorn[standard]>=0.29        # keep as dev/fallback server
granian>=2.7                   # ADOPT: production ASGI server (2.7.6, 2026-06-10) [VERIFIED]

# --- pagination + caching (add as F6 hardens) ---
fastapi-pagination>=0.15.14    # cursor + page (2026-05-30) [VERIFIED]  (or hand-roll keyset on asyncpg)
fastapi-cache2-fork>=2.3.0     # maintained, msgspec (2026-01-28) [VERIFIED]  (NOT fastapi-cache2)
redis>=5                       # redis.asyncio shared cache

# --- defer until needed ---
# SQLAlchemy>=2.0.50           # async Core, only when per-platform joins/migrations demand it [VERIFIED]
# psqlpy>=0.12                  # WATCH-LIST Rust driver, re-evaluate at >=1.0 [VERIFIED]
```

### 8.2 Run under Granian instead of uvicorn (no app change)

```bash
# dev (unchanged): uvicorn services.api.main:app --host 127.0.0.1 --port 8090
# prod: same ASGI app, Rust runtime
granian --interface asgi services.api.main:app \
        --host 0.0.0.0 --port 8090 \
        --workers 4 --runtime-threads 1 \
        --http auto            # negotiate HTTP/2 where available
```

### 8.3 Keyset/cursor pagination on the existing asyncpg path (envelope-preserving)

```python
# /entities/{cdp_code}/inventory?cursor=<iso8601>&limit=50
LIMIT_MAX = 200

@app.get("/entities/{cdp_code}/inventory")
async def get_inventory(cdp_code: str, cursor: str | None = None, limit: int = 50):
    limit = min(max(limit, 1), LIMIT_MAX)
    async with app.state.pool.acquire() as c:
        eulid = await c.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", cdp_code)
        if eulid is None:
            return err(f"entity {cdp_code} not found")
        # keyset on first_seen DESC; cursor is the last-seen first_seen of the prior page
        rows = await c.fetch(
            "SELECT vehicle_ulid, deep_link, title, make, model, year, km, price, currency, "
            "fuel, transmission, photo_url, status, first_seen, last_seen "
            "FROM vehicle "
            "WHERE entity_ulid=$1 AND status='available' "
            "  AND ($2::timestamptz IS NULL OR first_seen < $2::timestamptz) "
            "ORDER BY first_seen DESC LIMIT $3",
            eulid, cursor, limit + 1)
        has_more = len(rows) > limit
        rows = rows[:limit]
        items = [{**dict(r),
                  "price": float(r["price"]) if r["price"] is not None else None,
                  "first_seen": str(r["first_seen"]), "last_seen": str(r["last_seen"])}
                 for r in rows]
        next_cursor = str(rows[-1]["first_seen"]) if has_more and rows else None
        return ok(items, count=len(items), next_cursor=next_cursor, limit=limit)
```

### 8.4 ETag + Redis cache for a hot read (sketch)

```python
import hashlib, redis.asyncio as redis
from fastapi import Request, Response

# app.state.redis = redis.from_url(os.environ["CARDEEP_REDIS"], decode_responses=True)  # in lifespan

async def inventory_etag(c, eulid) -> str:
    # cheap version token: max(last_seen) over the entity's available vehicles
    v = await c.fetchval(
        "SELECT max(last_seen) FROM vehicle WHERE entity_ulid=$1 AND status='available'", eulid)
    return hashlib.sha256(f"{eulid}:{v}".encode()).hexdigest()[:16]

# in handler: compute etag; if request.headers.get('if-none-match') == etag -> Response(status_code=304)
# else set response.headers['ETag'] = etag; cache the JSON body in redis with a short TTL.
```

---

## 9. Source URLs (all fetched / searched this session)

- FastAPI — https://pypi.org/project/fastapi/ **[VERIFIED]**
- Litestar (PyPI) — https://pypi.org/project/litestar/ **[VERIFIED]**
- Litestar (GitHub) — https://github.com/litestar-org/litestar **[VERIFIED]**
- Litestar 2026 benchmark analysis — https://byteiota.com/litestar-vs-fastapi-python-speed-test-2026-analysis/ **[VERIFIED]**
- Litestar vs FastAPI (production framing) — https://betterstack.com/community/guides/scaling-python/litestar-vs-fastapi/ **[VERIFIED via search]**
- Framework benchmark repo (FastAPI/Litestar/Django) — https://github.com/tanrax/python-api-frameworks-benchmark **[VERIFIED via search]**
- Robyn (GitHub) — https://github.com/sparckles/Robyn **[VERIFIED]**
- Robyn (releases) — https://robyn.tech/releases **[VERIFIED via search]**
- Granian (PyPI) — https://pypi.org/project/granian/ **[VERIFIED]**
- Granian vs uvicorn (ASGI comparison) — https://blog.hashhackers.com/blog/granian-uvicorn-asgi/ **[VERIFIED via search]**
- Python app servers 2026 (uvicorn-as-safe-default) — https://www.deployhq.com/blog/python-application-servers-in-2025-from-wsgi-to-modern-asgi-solutions **[VERIFIED via search]**
- asyncpg — https://pypi.org/project/asyncpg/ **[VERIFIED]**
- SQLAlchemy — https://pypi.org/project/SQLAlchemy/ **[VERIFIED]**
- psqlpy — https://github.com/psqlpy-python/psqlpy **[VERIFIED]**
- fastapi-pagination — https://pypi.org/project/fastapi-pagination/ **[VERIFIED]**
- fastapi-cache2 (stale original) — https://pypi.org/project/fastapi-cache2/ **[VERIFIED]**
- fastapi-cache2-fork (maintained) — https://pypi.org/project/fastapi-cache2-fork/ **[VERIFIED]**
- aiocache — https://pypi.org/project/aiocache/ **[VERIFIED]**
- FastAPI caching strategy 2026 — https://blog.greeden.me/en/2026/02/03/fastapi-performance-tuning-caching-strategy-101-... **[VERIFIED via search]**
