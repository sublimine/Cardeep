# TOOLING — CARDEEP Master Bill of Materials

> **What this is.** The single, authoritative Bill of Materials (BOM) for the
> CARDEEP stack: for every micro and macro task of the system — second-hand
> vehicle scraping + indexing across 100% of Spain's points-of-sale and the giant
> marketplaces, with full inventory + live delta + per-source recipe + verified
> API — this document names **the chosen tool, its pinned version, why it beats
> the alternatives, and a config snippet**. It is the synthesis of the sixteen
> domain audits `T01`–`T16` in this directory; each row links back to the audit
> that proves it.
>
> **Audit date of the underlying research:** 2026-06-12. Every version/recency
> claim is traceable to its `T**` source doc, where it is tagged `[VERIFIED]`
> (repo/PyPI/release fetched) or `[ASSUMED]` (inferred). This master doc does not
> re-fetch; it **trusts and indexes** the per-domain audits and is the binding
> selection layer above them.
>
> **Reading order.** §1 the verdict table (the BOM). §2 the per-domain detail with
> config snippets. §3 **Upgrades vs current code** — the concrete deltas against
> what CARDEEP runs today. §4 dead tools banned on sight. §5 adoption phasing.
> §6 source index.

---

## 0. The doctrine that governs every pick

Six rules, distilled from the sixteen audits, that explain *why* the BOM looks
the way it does — and that any future tool swap must still satisfy:

1. **Current-floor or it's a liability.** "Alive" is necessary but insufficient.
   The 2026 bar for the scraping tier is **current-Chrome floor + post-quantum
   X25519MLKEM768 key share + HTTP/2 frame fidelity**; for everything else it is a
   release inside ~12 months *and* a maintained data/model corpus. A stale pin on a
   live tool ages silently (T01 §1, T05 §7.1).
2. **Render to unlock, drain on Tier-0.** Browsers are expensive and a fingerprint
   surface. Use the stealth browser only to defeat a JS/sensor challenge, capture
   the warmed cookie + the page's own internal API call, then replay with
   `curl_cffi` (T02 §5, T01 §3.1).
3. **Deterministic-first, probabilistic/LLM-fallback.** Parser+regex over
   structured islands, deterministic keys (domain/CIF), exact joins — these are the
   default and cover the overwhelming majority of the surface. The LLM and
   probabilistic linkage are the *long tail*, gated by cost (T07 §3, T08 §1, T09 §0).
4. **Keep PostgreSQL the system of record; escalate OLAP in-process before
   out-of-process.** Native partitioned PG handles OLTP+OLAP at CARDEEP's scale;
   the escalation order is `native PG → pg_duckdb (in-process) → ClickHouse (CDC
   serving layer)`, each behind a *written-down, measured* trigger (T13 §5).
5. **Augment the in-house control plane; never let a framework evict it.** The
   custom asyncio coordinator + Redis-Streams bus + per-source rate-governor are
   bespoke to CARDEEP's scars and beat every off-the-shelf orchestrator for *this*
   shape. Adopt libraries that feed them (Scrapling parser, APScheduler emitter,
   structlog), not frameworks that replace them (T06, T12, T15).
6. **Cheapest correct response; spend behind a gate.** Paid solvers, residential
   GB, ClickHouse clusters, Sentry-self-hosted, LGTM — all are reserve/last-resort
   tiers authorized by the lead, not fleet baseline (T03, T04, T13, T16).

CARDEEP's current `requirements.txt` (canonical `projects/cardeep`, verified
2026-06-12) is intentionally thin — `asyncpg`, `fastapi`, `uvicorn[standard]`,
`openpyxl`, plus a **commented** scraping arsenal (`scrapling>=0.4.9`,
`camoufox[geoip]`, `curl_cffi>=0.15.1`, `browserforge`). The BOM below is what that
arsenal block, and the rest of the stack, should become.

---

## 1. The Bill of Materials (master table)

Legend: **PICK** = primary; **FB** = fallback/secondary; **GATED** = adopt only at
a written trigger; **DEAD** = banned (see §4). Versions are the pinned floor.

### 1.1 Scraping / acquisition plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| A1 | No-browser HTTP w/ TLS/JA3/JA4 + PQ impersonation | **curl_cffi** (PICK) | `>=0.15.0,<0.16` | Only client that is current-Chrome floor (chrome146) **+** PQ-correct engine (X25519MLKEM768) **+** HTTP/2 **and** HTTP/3 **+** real `AsyncSession`. Already the standard | T01 |
| A2 | High-throughput sweep client | **rnet / wreq-python** (FB) | `==0.12.0` | Rust/PyO3 over BoringSSL → PQ-correct by construction, faster req/s. No HTTP/3, single-maintainer w/ rename churn → pin exact, throughput tier only | T01 |
| A3 | Stealth-browser control plane (Tier-1 render) | **patchright** via Scrapling `StealthyFetcher` (PICK) | `patchright>=1.60.0` | Undetected Playwright drop-in, monthly releases, 5 open issues; reached for free through the wrapper | T02 |
| A4 | Stealth wrapper + adaptive selectors | **Scrapling** (KEEP) | `>=0.4.9` | Best-maintained tool in the whole audit; gives patchright + self-healing selectors + capture ergonomics in one dep | T02, T06 |
| A5 | Pure-CDP escalation engine | **nodriver** (FB) ▸ **zendriver** (ALT) | `nodriver` (pin commit) / `zendriver>=0.15.3` | Wins the Cloudflare-Turnstile/Google cases patchright is gated on (28/0 blocked of 31). zendriver = pinnable-semver twin | T02 |
| A6 | Interactive-case escape hatch | **SeleniumBase** (ESCAPE) | `>=4.49.10` | Best-in-class Turnstile-click + xvfb tooling for awkward interactive flows | T02 |
| A7 | Tier-2 render of last resort | **BotBrowser** (KEEP, spend-gated) | `149.0.7827.59` | Deepest anti-bot reach (Akamai/Kasada/DataDome-sensor); freemium binary, last resort only | T02 |
| A8 | Firefox-only niche render | **cloverlabs-camoufox** (SECONDARY) | maintained fork | Firefox C++ fingerprint surface for targets that punish Chromium; **never stock `camoufox` 0.4.11 (stale)** | T02, T05 |
| A9 | CF interactive-challenge proxy | **Byparr** (PICK) ▸ **FlareSolverr** (FB) | `byparr 2.1.0` / `flaresolverr 3.5.0` | Byparr = Camoufox+FastAPI, reuses approved engine; FlareSolverr uses CI-blocked undetected-chromedriver → compat net only | T03 |
| A10 | Headless-native cf_clearance minter | **sarperavci/CloudflareBypassForScraping** (ALT) | container ~Apr 2026 | DrissionPage request-mirroring → `cf_clearance` + TLS-matched session handed to curl_cffi | T03 |
| A11 | Paid captcha solver (primary) | **CapSolver** (KEEP) | API | 2026 CF-ranking leader, AI-only, ~$1.2/1k Turnstile, ~99.15% claimed | T03 |
| A12 | Paid captcha solver (#2 hedge) | **CapMonster Cloud** (ADD) | API | Cheapest AI-only at volume, broadest type list (Amazon WAF/Yidun/Tencent); replaces NopeCHA | T03 |
| A13 | Free OSS Turnstile solver | **Theyka/Turnstile-Solver** (OSS) | `828★, patchright` | $0 backend behind Solver Layer; hobby-grade → CapSolver auto-fallback | T03 |
| A14 | Portal WAF/captcha classifier | **scrapfly/Antibot-Detector** (TOOL) | `v2.6` | Manifest-V3 extension; classifies CF/Akamai/DataDome/PX during W2 recipe authoring | T03 |
| A15 | Self-test leak oracle | **FingerprintJS BotD** + **CreepJS** (GATE) | `botd 2.0.0` | Assert zero leaks before promoting an identity to PREMIUM (trust ≥ 7.0) | T03 |

### 1.2 Identity / proxy plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| B1 | Primary ES residential proxy | **Decodo** (ex-Smartproxy) (PICK) | subscription | Best price/quality, 736k ES IPs, `country-es`, sticky 30m/24h, maintained SDK | T04 |
| B2 | Fallback / non-expiring GB | **IPRoyal** (FB) | subscription | Deepest ES pool (2.05M), sticky to 7 days, non-expiring GB for bursty re-index | T04 |
| B3 | Cheap bulk lane (soft long-tail) | **Evomi Core** (BULK) | `$0.49/GB` | Cheapest credible ES residential; Swiss/EU GDPR-friendly, sticky 24h | T04 |
| B4 | Self-hosted routing control plane | **proxy.py** (CONTROL) | `pushed 2026-05-18` | Per-domain provider routing + ban-driven session recycling; replaces the dead Scrapoxy | T04 |
| B5 | Free datacenter fronting lanes | **requests-ip-rotator** + **cloudproxy** (CHEAP) | latest | Zero-cost DC IPs for trivially-open targets, spares paid GB | T04 |
| B6 | Break-glass per-success unlock | **Bright Data Web Unlocker / Oxylabs** (RESERVE) | pay-per-success | The 2–3 hardest ES marketplaces only; never fleet baseline | T04 |
| B7 | Fingerprint value generator (UA/Sec-CH-UA/navigator/WebGL/fonts) | **browserforge** (PICK) | `+ apify-fingerprint-datapoints` pinned | Jointly-sampled coherent values; recency lives in the **monthly datapoints corpus** (pin it) | T05 |
| B8 | Fingerprint injector (Layer-3) | **camoufox** (PICK, verify-applied) | `v150.x` (cloverlabs fork) | Writes values into Firefox C++ APIs w/o JS-patch leaks; read back & assert post-launch | T05 |
| B9 | Node-side fingerprint fallback | **apify/fingerprint-suite** (FB-A) | `v2.1.83` | browserforge's upstream; only if Node enters the stack | T05 |

> **JA3/JA4 ownership (explicit):** no fingerprint *generator* rotates JA3/JA4 —
> that is a property of the TLS stack. It is owned by **curl_cffi `impersonate`**
> (A1). browserforge's only obligation is `UA-major == Sec-CH-UA-major ==
> curl_cffi-impersonate-major == injected-navigator-major`, asserted at session
> open, fail-closed (T05 §4).

### 1.3 Parsing / extraction / intelligence plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| C1 | Scraping orchestration (millions-scale) | **Custom asyncio coordinator** (KEEP) | in-house | Beats every framework for the anti-detect/JA3/tiered/identity model | T06 |
| C2 | Parsing + self-healing selectors | **Scrapling** `Adaptor`/`Selector` (LIB) | `>=0.4.9` | Deterministic local self-heal on DOM drift; ~2 ms/page; use the parser, NOT its Spider | T06 |
| C3 | Fallback orchestrator (new low-anti-bot sources) | **Crawlee-python** (FB) | `>=1.7.2` | Batteries-included async crawler; `SqlStorageClient` for multi-worker dedup | T06 |
| C4 | Fleet HTML parser | **selectolax** (lexbor backend) (PICK) | `==0.4.10` | Fastest mainstream parser (~5–30× BS4); lowest memory; **lexbor backend only** | T07 |
| C5 | XPath fallback parser | **lxml** (FB) | `>=6.0.1` | Where XPath axis traversal is needed; require ≥6.0.1 for XXE fix | T07 |
| C6 | Ergonomic unified CSS/XPath/JSON parser | **parsel** (ALT) | `1.11.0` | CSS+XPath+jmespath in one Selector for `__NEXT_DATA__`/`__NUXT__` blobs | T07 |
| C7 | Microdata + RDFa + all-syntax extraction | **extruct** (PINNED) | `==0.18.0` | Only purpose-built all-syntax extractor; pin (cadence slowed, not dead) | T07 |
| C8 | Long-tail LLM extraction API | **instructor** (PICK) | `>=1.15.1` | Pydantic-validated extraction; reuses CARDEEP's Pydantic models | T07 |
| C9 | Token-constrained decoding engine | **outlines** (PICK) | `>=1.3.0` | Hard schema guarantee via vLLM/llama.cpp; for huge hot reused schemas | T07, T08 |
| C10 | Local LLM batch engine (GPU) | **vLLM** (PICK) | `>=0.22,<0.23` | ~10× aggregate throughput vs Ollama at 32 concurrent; native `guided_json` (xgrammar) | T08 |
| C11 | Local LLM CPU/low-VRAM engine | **llama.cpp** (`llama-server`) (FB) | build `b9611+` | Single-stream king, CPU-only, GBNF constrained decoding; the real substrate under Ollama | T08 |
| C12 | Recommended extraction model | **Qwen3.5-4B-Instruct** (PICK) | Apache-2.0, 2026-03 | 262K ctx, 201 langs incl. ES, native tool-calling; throughput sweet spot | T08 |
| C13 | Fallback / edge model | **Gemma-4-E4B-it** (FB) | Apache-2.0, 2026-03 | 128K ctx, 140+ langs, Per-Layer-Embeddings for low-RAM CPU path | T08 |
| C14 | LLM dev/iteration front-end | **Ollama** (DEMOTE) | `v0.30.7` | Keep for dev DX only; ~12× slower aggregate — never the prod batch engine | T08 |
| C15 | Structured-output enforcement | **xgrammar** (default) ▸ **GBNF** (llama.cpp) | bundled | vLLM 2026 default; always temperature=0, schema-constrained at the decoder | T08 |
| C16 | Batch-engine watch/A-B candidate | **SGLang** (WATCH) | `v0.5.12+` | RadixAttention prefix-cache fits shared-schema fan-out; benchmark vs vLLM before lock | T08 |

### 1.4 Entity resolution / geo plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| D1 | Deterministic hard-key dedup | **`cdp_code`** (KEEP) | in-house | Domain/CIF/exact-normalized hard links stay deterministic — do not replace | T09 |
| D2 | Probabilistic record linkage / clustering | **Splink 4** (PICK) | `>=4.0.16,<5` | Unsupervised Fellegi-Sunter on DuckDB, no labels, 7M recs/2min, MoJ-maintained | T09 |
| D3 | Fuzzy string comparator | **RapidFuzz** (PICK) | `>=3.14,<4` | Fastest in class (C++ core); standard over legacy fuzzywuzzy/thefuzz | T09 |
| D4 | Phonetic blocking keys | **jellyfish** (PICK) | `>=1.2,<2` | Metaphone/Match-Rating (Rust core); complements RapidFuzz | T09 |
| D5 | Address parse + normalize | **libpostal** via **pypostal-multiarch** (PICK) | `pypostal-multiarch 1.0.3` | Only credible OSS multilingual parser; Senzing-revived (model v1.2.0); prebuilt Linux/ARM wheels | T09, T10 |
| D6 | Embedding blocking (scale tier) | **model2vec** (GATED ~100k) ▸ **sentence-transformers** (FB) | `model2vec>=0.8,<1` | Static embeddings ~500× faster, CPU-only; ST only for accuracy tier | T09 |
| D7 | Forward+reverse geocoder | **Nominatim** embedded via **nominatim-api** (PICK) | `5.3.2` | Best structured reverse; run in-process against a Spain extract, no HTTP service | T10 |
| D8 | Typo-tolerant fuzzy forward geocode | **Photon** (FB) | `1.2.0` | Tolerant free-text matching for sloppy listing locations (Spain-only import) | T10 |
| D9 | Authoritative INE province/municipio | **Shapely 2.x + GeoPandas STRtree** vs IGN-CNIG/INE polygons (PICK) | `shapely>=2.1` | Offline point-in-polygon → canonical INE codes; backfills whole corpus | T10 |
| D10 | Spatial bucketing | **Uber H3** (KEEP) | `h3-py 4.x` | 73–77% faster than PostGIS for coarse proximity; genuinely modern | T10 |
| D11 | Metric KNN (true distance) | **cube + earthdistance** (ADD) | PG contrib | One-line migration, true `<@>` KNN, no PostGIS dependency; defer PostGIS | T10 |
| D12 | Perceptual image hash (photo-delta/fraud) | **ajdnik/imghash** (PDQ, pure Go) (PICK) | `v2.5.2` | PDQ 256-bit ≫ 64-bit pHash on robustness, pure Go no-cgo, maintained 2026-06 | T11 |
| D13 | PDQ canonical oracle / scale-out index | **python-threatexchange** + **pdqhash** (FB) | `threatexchange 1.2.16` | Bit-for-bit PDQ oracle + FAISS index for hundreds-of-millions matching | T11 |
| D14 | Embedding 2nd-stage re-rank (flagged pairs) | **DinoHash** ▸ CLIP/SigLIP (NARROW) | `ICML 2025` | Recovers crop/watermark/overlay recall PDQ misses; flagged pairs only | T11 |
| D15 | Offline corpus dedup + threshold tuning | **imagededup** (idealo) (TOOL) | `5.6k★` | Seeds the duplicate index, tunes PDQ threshold against the real corpus | T11 |

### 1.5 Platform / serving plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| E1 | Job/event transport (primary) | **Redis Streams** via **redis-py** (KEEP) | `redis-py>=6.x`, server `Redis 8.4` | Consumer groups + at-least-once; ~100× headroom over the 50k/min trigger; migrate reclaim to `XREADGROUP … CLAIM` | T12 |
| E2 | Transport fallback (>50k/min or replay) | **NATS JetStream** (GATED) | `nats-server v2.14.x`, `nats.py 2.15.0` | Light Go-native durable bus; adopt only at the ADR-0001 trigger | T12 |
| E3 | Worker library (if a framework is adopted) | **Dramatiq** (Redis broker) (PICK) | `v2.1.0` | Fastest (1.53s/20k), at-least-once by design, retries+DLQ+prefetch free, no bus migration | T12 |
| E4 | Worker library (async-native) | **Taskiq** (Redis Streams broker) (FB) | `v0.12.4` | asyncio-native (matches the fleet), 2nd-fastest, broker-agnostic | T12 |
| E5 | Transactional enqueue-with-write | **Procrastinate** (PostgreSQL) (NICHE) | `pushed 2026-06` | Queue inside PG for delta/remediation sub-pipelines that already write PG | T12 |
| E6 | Backpressure on the consumer loop | **asyncio Semaphore** bound (ADD) | in-house | The one real gap: bound in-flight to PG/fetcher capacity | T12 |
| E7 | Core OLTP+OLAP engine | **PostgreSQL 18** (upgrade target; 17 interim) (PICK) | `18.4` | AIO ~3× scans/VACUUM, skip-scan, better partition pruning, retained planner stats | T13 |
| E8 | Partition lifecycle automation | **pg_partman + pg_cron** (ADD) | `partman>=5.4.3`, `cron>=1.6.7` | Premake + 24-mo detach-retention for `vehicle_event`; replaces hand-rolled cron. Avoid partman 5.4.2 | T13 |
| E9 | Fuzzy/faceted search spine | **pg_trgm + btree_gin** (KEEP) | in-core | In-DB trigram search; no external engine justified for single-country names | T13 |
| E10 | Geo geometry (future) | **PostGIS 3.6** (GATED) | `3.6.3` | Only when radius/density geo needed (`0099` migration); not v1 | T13 |
| E11 | OLAP accelerant (in-process) | **pg_duckdb** (GATED) | `>=1.1.1` | DuckDB vectorized engine over same tables, no second datastore — first OLAP escalation | T13 |
| E12 | OLAP serving layer (scale) | **ClickHouse** via PeerDB→ClickPipes CDC (GATED) | `26.4.4` | Read-only CDC-fed serving layer at >500GB/hundreds-concurrency; never OLTP | T13 |
| E13 | API framework | **FastAPI** (KEEP) | `>=0.110` (latest 0.136.3) | Incumbent, healthiest ecosystem; perf gap vanishes under DB-bound load | T14 |
| E14 | Production ASGI server | **Granian** (ADOPT) ▸ uvicorn (FB) | `granian>=2.7` | Rust/Tokio, tighter tail latency (~2.8× vs uvicorn ~6.8×), HTTP/2, drop-in. Highest-ROI low-risk upgrade | T14 |
| E15 | Async PG driver | **asyncpg** (KEEP, bump pin) | `>=0.30,<0.32` | Fastest mature async driver; unlock 0.31 (py3.13/3.14 + free-threaded wheels) | T14 |
| E16 | Pagination | **fastapi-pagination** or hand-rolled keyset (ADD) | `>=0.15.14` | Kills the unbounded `/inventory` query — the real scaling defect | T14 |
| E17 | Read caching | **fastapi-cache2-fork** + `redis.asyncio` + ETag (ADD) | `>=2.3.0` | Maintained msgspec fork (NOT the stale original); offloads read-heavy surfaces | T14 |
| E18 | ORM / query layer | **SQLAlchemy 2.0** async Core (OPTIONAL) | `2.0.50` | Only when multi-join per-platform aggregations or migrations demand it | T14 |
| E19 | Framework rewrite-only challenger | **Litestar** (FB) | `2.24.0` | msgspec-native; pick only for a green-field high-fan-out service | T14 |

### 1.6 Control / observability plane

| # | Task | Tool (role) | Version pin | Why it beats alternatives | Audit |
|---|------|-------------|-------------|---------------------------|-------|
| F1 | Durable cadence emitter (scheduler) | **APScheduler 3.11** on PG `SQLAlchemyJobStore` (PICK) | `>=3.11,<4` | Smallest correct tool: durable schedules, misfire grace, single-producer; emits onto Redis Streams. **Never 4.0.0a\*** | T15 |
| F2 | Scheduler fallback (UI/automations) | **Prefect 3.7** schedule-only (FB) | `3.7.4` | Run-history UI + event automations when later justified; still emits onto streams | T15 |
| F3 | Per-step durable execution (future) | **DBOS Transact** (OPTIONAL) | `2.23.0` | Postgres-journaled checkpoint/resume inside a worker, zero new infra | T15 |
| F4 | Structured logging (keystone) | **structlog** (PICK) | `>=26.1,<27` | Carries the same `(source_key, phase, signal)` tuple as the alert table; contextvars pipeline feeds the log→alert tee | T16 |
| F5 | In-proc metrics exposition | **prometheus-client** + **prometheus-fastapi-instrumentator** (ADD) | `>=0.25` / `>=8` | Cheap pull-based `/metrics` for the operator dashboard, no always-on agent | T16 |
| F6 | Telemetry wire format (anti-lock-in) | **OpenTelemetry SDK** + FastAPI instr. (GATED) | `sdk>=1.42,<2` | Vendor-neutral OTLP so the backend is swappable; adopt when a backend lands | T16 |
| F7 | Code-level exception capture | **GlitchTip** + **sentry-sdk** (ADD) | `glitchtip v6.1.8`, `sentry-sdk>=2.62,<3` | Self-hosted, light, Sentry-API-compatible; catches Python tracebacks the alert table can't hold | T16 |
| F8 | Single-pane telemetry backend (if UI wanted) | **SigNoz** (GATED) | `v0.128.0` | OTel-native, ClickHouse one-store; lower op-overhead than LGTM on one node | T16 |
| F9 | Metrics-only lighter backend | **VictoriaMetrics** (ALT) | `v1.145.0` | Drop-in Prometheus replacement if footprint matters and no logs/traces UI needed | T16 |
| F10 | Exact-origin alert channel | **DB-native alerter** (`alert` table, `origin NOT NULL`, `(origin,signal)` dedup) + **PushNotification** (KEEP) | in-house | Typed, attributed, self-repair-aware alerts richer than a metric threshold; augment, do not replace | T16 |

---

## 2. Per-domain detail + config snippets

Only the load-bearing config is reproduced here; the full rationale, candidate
matrices, dead-tool flags, and source URLs live in each `T**` audit.

### 2.1 HTTP / TLS impersonation (A1–A2 · T01)

`curl_cffi` stays primary. The two corrections are **hardening, not a swap**: pin
to a stable floor (the current `>=0.15.1` is a *beta* string) and name an explicit
PQ-correct Chrome target so a downgrade can't silently drop onto a pre-PQ profile.

```python
# pipeline/fetch/tls.py — PQ-aware floor, session-level JA3 only
from curl_cffi.requests import AsyncSession

_MIN_CHROME_PQ = 142   # >= chrome142 sends X25519MLKEM768; refuse to start below this
def make_session(identity) -> AsyncSession:
    return AsyncSession(
        impersonate="chrome",   # alias -> latest available (>=146 today); session-level ONLY
        http_version=3,         # QUIC / HTTP-3
        proxies={"https": identity.proxy_ip, "http": identity.proxy_ip} if identity.proxy_ip else None,
    )
```
```text
# requirements.txt
curl_cffi>=0.15.0,<0.16        # stable floor, PQ-correct engine (chrome146/ff147/safari260)
rnet==0.12.0                   # FALLBACK throughput tier — pin exact (rename-churn risk)
```
Add a **live PQ self-check** to CI/health: hit a TLS-inspect reflector and assert
NamedGroup `0x11ec` (X25519MLKEM768) is present in the ClientHello.

### 2.2 Stealth browsers + anti-bot (A3–A15 · T02, T03)

Two-engine, CDP-first Tier-1: patchright primary (via Scrapling), nodriver/zendriver
escalation, BotBrowser last resort, camoufox demoted to Firefox-only.

```text
# requirements.txt — Tier-1 stealth block
scrapling>=0.4.9             # wrapper: StealthyFetcher(patchright) + adaptive selectors
patchright>=1.60.0           # PRIMARY control plane (undetected Playwright, channel=chrome)
nodriver                     # FALLBACK control plane (pure-CDP) — pin a commit (no tags)
# zendriver>=0.15.3          # ALT fallback: pinnable semver, same CDP class
# seleniumbase>=4.49.10      # ESCAPE HATCH: CDP Mode + Turnstile-click + xvfb
# cloverlabs-camoufox        # SECONDARY (Firefox-only) — NOT stock camoufox 0.4.11 (stale)
```
```yaml
# configs/antibot/solver_layer.yaml — Solver Abstraction Layer (cheapest-first)
solver_layer:
  selection_order: [oss_turnstile, capsolver, capmonster]   # OSS → paid; lead authorizes spend
  backends:
    oss_turnstile: { repo: Theyka/Turnstile-Solver, engine: camoufox, liveness_recheck_days: 7 }
    capsolver:     { api_key_env: CAPSOLVER_API_KEY }        # KEEP — primary paid
    capmonster:    { api_key_env: CAPMONSTER_API_KEY }       # ADD  — #2 (replaces NopeCHA)
cf_challenge_proxy:
  primary:  { tool: byparr,       endpoint: "http://127.0.0.1:8191/v1", per_request_proxy: true }
  fallback: { tool: flaresolverr, endpoint: "http://127.0.0.1:8192/v1" }   # compat net (UC engine)
# HARD RULE: DataDome / PerimeterX portals NEVER route to a solver as primary unblock —
#   that is a T04 proxy/fingerprint/behavioral decision, not a T03 solver decision.
```

### 2.3 Proxy fleet (B1–B6 · T04)

Provider-side rotation + `proxy.py` control plane. **Scrapoxy is dead** — do not build
on it. Rotation = session-ID cycling in the username; the provider rotates the egress IP.

```text
scrapers ──► [proxy.py control plane] routes by target difficulty:
  ├─► Evomi Core (ES, $0.49/GB)   → long-tail soft dealer sites (cheap GB)
  ├─► Decodo residential (ES)     → hard marketplaces (sticky 30m, session IDs)   ← PRIMARY
  ├─► IPRoyal (ES, non-expiring)  → overflow / burst lanes
  └─► cloudproxy / req-ip-rotator → free DC lane for trivial targets
# Decodo gate: user-<USER>-country-es-session-<ID>-sessionduration-30 @ gate.decodo.com:7000
# Bright Data Web Unlocker / Oxylabs = RESERVE (pay-per-success, 2–3 hardest sites only)
```

### 2.4 Fingerprint coherence (B7–B9 · T05)

```python
# Pin the DATA, not just the package — recency lives in the datapoints corpus.
# requirements.txt:
#   browserforge
#   apify-fingerprint-datapoints   # PIN EXPLICITLY; refresh on the ~6-week Chrome cadence
fp = FingerprintGenerator().generate()      # coherent UA/navigator/WebGL/fonts (jointly sampled)
# T0: fp headers → curl_cffi request.   T1: SAME fp object → camoufox injector.
# After camoufox launch: READ BACK the applied fingerprint and assert it still matches
# the session identity (fail-closed) — camoufox drops some fields when its data lags.
```

### 2.5 Parsing + extraction (C1–C9 · T06, T07)

```text
# requirements.txt — parsing
selectolax==0.4.10          # lexbor backend; fleet HTML parser
extruct==0.18.0             # microdata + RDFa + all-syntax; PINNED (cadence slowed)
# parsel==1.11.0            # OPTIONAL unified CSS/XPath/jmespath alt
# lxml>=6.0.1               # only if XPath needed (>=6.0.1 = XXE fix)
instructor>=1.15.1          # long-tail LLM extraction API (Pydantic-validated)
outlines>=1.3.0             # token-constrained decoding (vLLM/llama.cpp)
```
```python
# Replace the brittle regex _RE_LD_BLOCK find + "}{"→"},{" hack with a real parser.
from selectolax.lexbor import LexborHTMLParser
import json
def extract_jsonld_blocks(html: str) -> list:
    tree = LexborHTMLParser(html)
    out = []
    for node in tree.css('script[type="application/ld+json"]'):
        body = (node.text() or "").strip()
        if not body: continue
        try: out.append(json.loads(body))     # per-block; no sibling-merge corruption
        except json.JSONDecodeError: continue  # skip malformed, keep the rest
    return out
# Scrapling as a pure parser (self-healing selectors), fed by CARDEEP's own fetchers:
from scrapling.parser import Adaptor
page = Adaptor(html, url=url, adaptive=True, auto_save=True)   # fingerprint store on a DURABLE shared volume
```

### 2.6 Local LLM (C10–C16 · T08)

```bash
# Production batch (GPU): vLLM + Qwen3.5-4B + xgrammar guided_json
pip install "vllm>=0.22,<0.23"
vllm serve Qwen/Qwen3.5-4B-Instruct --port 8000 --max-model-len 32768 \
  --gpu-memory-utilization 0.90 --enable-prefix-caching \
  --guided-decoding-backend xgrammar --enable-auto-tool-choice --tool-call-parser hermes
# Fallback (CPU/low-VRAM): llama.cpp + Gemma-4-E4B Q4_K_M + GBNF
./llama-server -hf google/gemma-4-E4B-it-GGUF:Q4_K_M --port 8001 --ctx-size 8192 --parallel 4 --jinja
```
```python
# Every classify/parse call schema-constrained at the decoder, temperature=0.
resp = client.chat.completions.create(
    model="Qwen/Qwen3.5-4B-Instruct", messages=[...],
    extra_body={"guided_json": DEALER_SCHEMA}, temperature=0, max_tokens=64)
# Model recency MANDATE: Qwen3.5 / Gemma 4 — NEVER Qwen3 / Gemma 3 / Phi-4 / Llama 3.x (last-gen).
```

### 2.7 Dedup / entity resolution (D1–D6 · T09)

```text
# Linux pipeline container
splink>=4.0.16,<5
rapidfuzz>=3.14,<4
jellyfish>=1.2,<2
postal>=1.1            # native libpostal required (use pypostal-multiarch wheels)
model2vec>=0.8,<1      # embedding blocking, scale tier (~100k+)
# sentence-transformers>=5.5  # accuracy-tier fallback, GPU optional
```
Architecture = **deterministic-first** (`cdp_code` hard-keys domain/CIF) →
**Splink** unsupervised Fellegi-Sunter only over the residual no-shared-key records,
blocked by `province_code` + phonetic name keys; `cluster_id` → owns `cdp_code`; a
second org-grain Splink model feeds `org_code` (branch↔chain). pypostal normalizes
the address arm *before* keying.

### 2.8 Geocoding (D7–D11 · T10)

```python
# pip install pypostal-multiarch==1.0.3 nominatim-api==5.3.2 shapely>=2.1 geopandas pyproj
# 1) libpostal parse → postcode[:2] = deterministic province hint
# 2) Nominatim 5.3.2 embedded in-process (no HTTP service) against a Spain extract
# 3) Photon 1.2.0 fallback for typo-tolerant free-text
# 4) Shapely STRtree PiP vs IGN-CNIG/INE polygons → AUTHORITATIVE INE codes (backfill corpus)
```
```sql
-- Metric KNN without PostGIS: cube + earthdistance (one-line migration). Keep H3 as the coarse index.
CREATE EXTENSION IF NOT EXISTS cube;  CREATE EXTENSION IF NOT EXISTS earthdistance;
CREATE INDEX idx_vehicles_earth ON vehicles USING gist (ll_to_earth(lat::float8, lng::float8));
```

### 2.9 Perceptual hashing (D12–D15 · T11)

```go
// Replace goimagehash (frozen 2022/2024) with ajdnik/imghash PDQ — pure Go, no cgo.
import "github.com/ajdnik/imghash/v2"
var pdq = imghash.NewPDQ()           // 256-bit PDQ ≫ 64-bit pHash on crop/watermark/overlay
const pdqDuplicateMax = 16           // strict "same photo" fraud band (paper match band ≤30/256)
// Keep V16's store/index/warning logic; widen threshold from Hamming≤4/64 to PDQ ≤16/256.
// 2nd stage: DinoHash/CLIP re-rank only on PDQ-flagged uncertain pairs (cost-bounded).
```

### 2.10 Queue + workers (E1–E6 · T12)

```python
# KEEP Redis Streams. Two upgrades: (1) Redis 8.4 single-shot reclaim, (2) bounded backpressure.
MAX_INFLIGHT = 32                     # bound in-flight to PG/fetcher capacity (the real gap)
sem = asyncio.Semaphore(MAX_INFLIGHT)
# Redis 8.4: single round-trip new+reclaim, replaces XPENDING→XAUTOCLAIM→XREADGROUP (PEL churn):
resp = await r.execute_command("XREADGROUP","GROUP",GROUP,CONSUMER,"COUNT",16,"BLOCK",5000,
                               "CLAIM",60_000,"STREAMS",STREAM,">")
# IF a framework is later adopted (no bus migration): Dramatiq (Redis broker) or Taskiq (async-native).
```

### 2.11 Datastore (E7–E12 · T13)

```dockerfile
FROM postgres:18
RUN apt-get update && apt-get install -y --no-install-recommends \
      postgresql-18-partman postgresql-18-cron && rm -rf /var/lib/apt/lists/*
# in-core: pg_trgm, btree_gin, pgcrypto.  shared_preload_libraries='pg_cron'; cron.database_name='cardeep'
# enable_partitionwise_join/aggregate = on  (off by default — real win for /stats & grid)
# pg_duckdb / postgis / clickhouse: added ONLY at their documented triggers — NOT now.
```
```sql
-- pg_partman manages the ROLLING vehicle_event time dimension (province-LIST partitions are static, leave as DDL):
SELECT partman.create_parent('public.vehicle_event','observed_at','native','1 month', p_premake=>4);
UPDATE partman.part_config SET retention='24 months', retention_keep_table=true
 WHERE parent_table='public.vehicle_event';
```
Escalation order (each behind a measured trigger): **native PG → pg_duckdb
(in-process) → ClickHouse via PeerDB→ClickPipes CDC**. TimescaleDB rejected for the
core (overlaps native partitioning + non-OSI TSL). Citus is the documented far-future
single-node-write-wall exit ramp.

### 2.12 API serving (E13–E19 · T14)

```text
# requirements.txt deltas
asyncpg>=0.30,<0.32            # BUMP from >=0.29,<0.31 → unlock 0.31 (py3.13/3.14 free-threaded)
granian>=2.7                   # ADOPT prod ASGI server (uvicorn stays dev/fallback)
fastapi-pagination>=0.15.14    # OR hand-roll keyset on asyncpg — kill the unbounded /inventory query
fastapi-cache2-fork>=2.3.0     # maintained msgspec fork (NOT stale fastapi-cache2) + redis.asyncio + ETag
```
```bash
# Same FastAPI ASGI app, Rust runtime — process-launch change, not a refactor:
granian --interface asgi services.api.main:app --host 0.0.0.0 --port 8090 --workers 4 --http auto
```

### 2.13 Orchestration scheduler (F1–F3 · T15)

```python
# pipeline/scheduler.py — durable cadence emitter (replaces the bare asyncio.sleep loop)
# pip: APScheduler>=3.11,<4   (NEVER 4.0.0a* — stalled alpha, "do NOT use in production")
scheduler = AsyncIOScheduler(
    jobstores={"default": SQLAlchemyJobStore(url="postgresql+psycopg://cardeep:***@localhost:5433/cardeep",
                                             tablename="apscheduler_jobs")},
    job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 900},  # single-producer, crash-safe
    timezone="Europe/Madrid")
# Each job's ONLY action: XADD a job envelope onto a Redis Stream; the per-source governor paces execution.
```

### 2.14 Observability (F4–F10 · T16)

```text
# requirements.txt — now-tier
structlog>=26.1,<27                     # keystone: same (source_key,phase,signal) tuple as the alert table
prometheus-client>=0.25,<0.26
prometheus-fastapi-instrumentator>=8,<9
sentry-sdk>=2.62,<3                      # client; DSN → self-hosted GlitchTip
# opentelemetry-sdk>=1.42,<2             # adopt when a backend (SigNoz) is stood up
```
Keep the **DB-native exact-origin alerter** (doc 06 §3: `alert` table, `origin NOT
NULL`, `(origin,signal)` dedup, auto-resolve) + `PushNotification` escalation —
**augment, do not replace**. structlog's terminal processor tees a `HARD_FAIL`
log event into an `alert` row (one vocabulary, one code path). Reject the full LGTM
stack (three stateful systems on one node) and Sentry-self-hosted (~16GB RAM).

---

## 3. Upgrades vs current code

What CARDEEP runs today vs what the BOM mandates. Ordered by ROI / risk. The
canonical `requirements.txt` (verified 2026-06-12) has only `asyncpg>=0.29,<0.31`,
`fastapi>=0.110`, `uvicorn[standard]>=0.29`, `openpyxl` live, with the scraping
arsenal **commented out**.

### 3.1 Already partially used — fix the pins / wiring

| Current state | Required change | Why | Audit |
|---|---|---|---|
| `curl_cffi>=0.15.1` (commented; **beta string** — 0.15.1 only exists as betas) | `curl_cffi>=0.15.0,<0.16` + explicit PQ-correct chrome floor (`>=chrome142`) + live PQ ClientHello check in CI | Tracking a beta in requirements is a latent footgun; a stale alias can silently drop below the X25519MLKEM768 line | T01 |
| `scrapling>=0.4.9` (commented) | Promote to live; use `Adaptor`/`StealthyFetcher` (patchright-backed), **NOT** its Spider; persist fingerprint store on a **durable shared volume** | Scrapling is the best-maintained tool in the audit; ephemeral-fs wipes the self-heal store on cold start | T02, T06 |
| `camoufox[geoip]` (commented) — described elsewhere as the "camoufox-driven StealthyFetcher" engine | Drop as the Tier-1 *default*; Scrapling swapped to **patchright** at v0.3.13. Pin `patchright>=1.60.0` + `nodriver` (escalation). If camoufox kept → `cloverlabs-camoufox` fork, Firefox-only niche | Stock `camoufox` pip is 16-mo stale (0.4.11, 2025-01); the doc describes a backend its own wrapper abandoned | T02, T05 |
| `browserforge` (commented) | Keep, but **pin `apify-fingerprint-datapoints` explicitly** and add it to the ~6-week Chrome-cadence refresh; read back & assert the camoufox-applied fingerprint, fail-closed | browserforge's recency lives in the monthly datapoints corpus, not its own commits; a stale datapoints pin ages every UA | T05 |
| `asyncpg>=0.29,<0.31` (live) | Bump to `asyncpg>=0.30,<0.32` | The current pin **excludes 0.31.0** (2025-11-24) with py3.13/3.14 + free-threaded wheels | T14 |
| `uvicorn[standard]>=0.29` (live, prod server) | Add `granian>=2.7` as the **production** server; keep uvicorn as dev/fallback | Rust/Tokio, ~2.8× avg-to-max latency vs uvicorn's ~6.8×, HTTP/2; same ASGI app, launch-line change. Highest-ROI low-risk win | T14 |

### 3.2 Plain stdlib / hand-rolled patterns that must die or harden

| Current pattern | Replacement | Why | Audit |
|---|---|---|---|
| **Plain `urllib`/`httpx`/`aiohttp`/`requests` pointed at WAF-guarded portals** | `curl_cffi` (A1) for anything behind a CDN; relegate plain clients to **trusted-host tier only** (open sitemaps, OEM JSON, internal APIs) | Default Python/OpenSSL ClientHello has no browser JA3/JA4 → filtered on TLS *before* the first HTTP byte by any modern WAF. **plain urllib must die on guarded targets** | T01 §3.6 |
| **Regex `_RE_LD_BLOCK` + `}{`→`},{` JSON-LD hack** | `selectolax` lexbor: extract `<script type="application/ld+json">` bodies, `json.loads` each independently; keep `_walk_ld` | The string-rewrite **corrupts valid adjacent JSON-LD objects** and drops silently — the single most fragile line in extraction | T07 §2.2 |
| **Regex "microdata" extraction** | `extruct==0.18.0` (or a selectolax tree walk) | `itemscope`/`itemprop` is nested DOM scope resolution; regex cannot track scope boundaries | T07 §2.1 |
| **Hand-rolled `XPENDING`→`XAUTOCLAIM`→`XREADGROUP` reclaim loop** | Redis 8.4 single-shot `XREADGROUP … CLAIM` (pin `redis-py>=6.x`, server ≥8.4) | Kills the documented XAUTOCLAIM PEL O(log n) churn; retry-cap + DLQ metadata in one round-trip | T12 §3.1 |
| **Consumer loop with only `count`/`block` (no in-flight bound)** | Add an `asyncio.Semaphore` backpressure gate sized to PG/fetcher capacity | The one real gap: the enrich lane can currently outrun PG writes | T12 §5 |
| **Hand-rolled monthly-cron partition creation (`§8.3`)** | `pg_partman>=5.4.3` + `pg_cron>=1.6.7` (premake + 24-mo detach-retention) | Battle-tested; premake gives slack so a missed run doesn't dump rows into `default` | T13 §3 |
| **Bare `asyncio.sleep` / cron emitter as the scheduler** | `APScheduler>=3.11,<4` on a persistent PG `SQLAlchemyJobStore` | A bare loop fails crash-safety (a crash between ticks silently loses a cadence) and single-producer (a restart can double-fire) | T15 §9 |
| **`print(...)` to stdout for operational signal (the §0 incident)** | `structlog>=26.1,<27` carrying the exact-origin tuple; tee `HARD_FAIL` events into the `alert` row | Unstructured prints are the blind spot; structured logs share one vocabulary with the alerter | T16 §2.1 |
| **Unbounded `/inventory` `ORDER BY first_seen DESC` (no LIMIT)** | Keyset/cursor pagination (`fastapi-pagination>=0.15.14` or hand-rolled on asyncpg) | At 333k+ vehicles an unbounded fetch for a large dealer is a latency/memory hazard — the real API scaling defect | T14 §5 |
| **Every request hits Postgres (no cache)** | ETag (off `last_seen`/`max(observed_at)`) + `redis.asyncio` + `fastapi-cache2-fork>=2.3.0` | Inventory/province listings are read-heavy and highly cacheable | T14 §6 |
| **`goimagehash` 64-bit pHash @ Hamming≤4 (V16, frozen 2022/2024)** | `ajdnik/imghash` v2.5.2 PDQ (256-bit, pure Go, no cgo); retune threshold ≤16/256 | Frozen single-algorithm library; brittle to the crop/watermark/overlay tricks dealers use | T11 |
| **No geocoder / no INE province assignment (free-text addresses fall on the floor)** | libpostal (pypostal-multiarch) + embedded Nominatim 5.3.2 + Shapely STRtree vs INE polygons | The 100%-of-Spain mandate gap: sources giving only free-text addresses land `lat=lng=NULL`, untrusted region | T10 |
| **No cross-source entity resolution (only deterministic `cdp_code`)** | Add Splink 4 + RapidFuzz + jellyfish + pypostal, deterministic-first | Same dealer under different names across AS24/OEM/Coches.net mints multiple codes → violates "one code per dealer" | T09 |

### 3.3 Engine-grade upgrades (infra)

| Current | Target | Why | Audit |
|---|---|---|---|
| PostgreSQL 16.14 | **PostgreSQL 18** (17 conservative interim) | AIO ~3× scans/VACUUM, skip-scan on composite indexes, better partition pruning/joins, retained planner stats de-risk the upgrade itself | T13 |
| Ollama (dev default, no model pinned) for the massive batch stage | **vLLM 0.22.x + Qwen3.5-4B + xgrammar** for prod batch; demote Ollama to dev front-end | Ollama is ~12× slower aggregate at 32 concurrent — caps throughput on the *masivo y barato* layer | T08 |
| Redis Streams (correct, KEEP) on older server | Redis **8.4** server + `redis-py>=6.x` | Unlocks single-shot reliable consumers; the *architecture* is already right | T12 |

---

## 4. DEAD / banned on sight (do not adopt — corpses flagged by the audits)

| Tool | Status | Replacement | Audit |
|---|---|---|---|
| **hrequests** | DEAD — no PyPI release 12+ mo; wraps tls-client. Rip out if imported | curl_cffi / rnet | T01, T05 |
| **rebrowser-patches** | DEAD-for-purpose — last release 2025-05 (~13mo), benchmark-equal to vanilla | patchright (subsumes its one trick) | T02 |
| **undetected-chromedriver / playwright-stealth / puppeteer-stealth / fake-useragent** | CI-BLOCKED + outdated | patchright / nodriver / Camoufox driver-level | T02, T03 |
| **2Captcha** as a pinned dependency | CI-BLOCKED (human-assisted, slow) | CapSolver / CapMonster (AI-only) | T03 |
| **Scrapoxy** | DEAD — discontinued 2026 after 11 yr (don't be fooled by the deprecation-commit timestamp) | provider-side rotation + proxy.py | T04 |
| **ProxyBroker** | DEAD — last push 2024-03 | — (provider gateways rotate) | T04 |
| **fakebrowser** | DEAD — archived 2025-03, repo 404 | browserforge + camoufox | T05 |
| **FraudFox** | DEAD — deadpooled 2026 | — | T05 |
| **Frontera** | DEAD — last release 2019 (Python-2-era) | Redis/Postgres priority queue inside the coordinator | T06 |
| **recordlinkage** | DEAD — ~3yr no release/commit, Py≤3.11 | Splink 4 | T09 |
| **SSCD** | DEAD — archived 2022-08 | DinoHash | T11 |
| **MTRNord/pdqhash-go**, **blockhash-python** | DEAD/stale | ajdnik/imghash (PDQ + blockhash in pure Go) | T11 |
| **goimagehash** (current V16 hasher) | FROZEN — no release since 2022, no PDQ | ajdnik/imghash | T11 |
| **APScheduler 4.0.0a\*** | STALLED ALPHA — "do NOT use in production" | APScheduler 3.11 | T15 |
| **fastapi-cache2** (original) | STALE — 0.2.2 / 2024-07 (~23mo) | fastapi-cache2-fork | T14 |
| **aiocache** | BORDERLINE-STALE — 0.12.3 / 2024-09 | `redis.asyncio` directly | T14 |

**Demoted (alive but wrong-sized/shape, not death):** TimescaleDB (overlaps native
partitioning + non-OSI TSL), Sentry self-hosted (~16GB RAM), full LGTM stack (3
stateful systems on one node), loguru (18mo no release), Dagster/Windmill/Temporal
(would evict the in-house control plane), Scrapy (no gain over the custom coordinator),
Robyn (no async-PG/pagination story), psqlpy (pre-1.0 on the hot path), pg_mooncake
(sub-v1, branch quiet since 2025-10).

---

## 5. Adoption phasing (spend- and risk-aware)

1. **Now, zero-risk pin hygiene:** bump `asyncpg` pin; promote `curl_cffi>=0.15.0,<0.16`
   with PQ floor; adopt **Granian** (prod); add **structlog** + **prometheus-client**;
   add the **asyncio.Semaphore backpressure** gate; swap the JSON-LD regex for selectolax.
2. **Now, mandate-closing:** add **pagination** + **ETag/redis caching** to the API;
   migrate Redis reclaim to **8.4 `XREADGROUP … CLAIM`**; replace the bare scheduler loop
   with **APScheduler 3.11**; swap V16 hasher to **ajdnik/imghash PDQ**.
3. **Scheduled infra:** **PostgreSQL 18** upgrade (gate on extension PG18 builds +
   asyncpg smoke test) with **pg_partman + pg_cron**; stand up the **geocoding** stack
   (libpostal + embedded Nominatim + Shapely INE PiP) and backfill the corpus; bring up
   the **entity-resolution** container (Splink + RapidFuzz + jellyfish + pypostal).
4. **When the batch LLM stage goes live:** **vLLM + Qwen3.5-4B + xgrammar** (GPU host),
   **llama.cpp + Gemma-4-E4B** (CPU fallback); demote Ollama to dev.
5. **Spend-gated / break-glass:** **Decodo** primary residential + **IPRoyal** fallback +
   **Evomi** bulk; **CapSolver** + **CapMonster**; reserve **Bright Data Web Unlocker** for
   the 2–3 hardest ES marketplaces; **BotBrowser** for Akamai/Kasada render of last resort.
6. **Gated by a written, measured trigger only:** **pg_duckdb** (native aggregation
   strains) → **ClickHouse** CDC serving layer (>500GB / hundreds-concurrency / SLA miss);
   **NATS JetStream** (>50k msg/min sustained); **SigNoz/VictoriaMetrics** (real telemetry
   UI wanted); **PostGIS** (radius/density geo); **GlitchTip** (code-exception capture);
   **DBOS Transact** (per-step resume becomes a measured cost).

---

## 6. Source index — the sixteen domain audits

Each row of §1 traces to one of these. Read the audit for the full candidate matrix,
recency evidence (`[VERIFIED]`/`[ASSUMED]`), dead-tool flags, and source URLs.

| Doc | Domain | Lives in repo |
|---|---|---|
| `T01-tls-http-clients.md` | No-browser HTTP w/ TLS/JA3/JA4 + PQ impersonation | cardex-integration |
| `T02-stealth-browsers.md` | Stealth / undetected browsers (Tier-1 render) | cardeep |
| `T03-antibot-and-captcha.md` | Anti-bot challenge solving + captcha + detection | cardex-integration |
| `T04-proxy-fleet.md` | Proxy providers + rotation (Spain residential/mobile) | cardex-integration |
| `T05-fingerprint-generation.md` | Browser/header/TLS fingerprint coherence | cardeep |
| `T06-scraping-framework.md` | Scraping framework / orchestration | CARDEX |
| `T07-parsing-extraction.md` | HTML/JSON parsing + extraction + LLM boundary | CARDEX |
| `T08-local-llm.md` | Local LLM engine + small structured-extraction model | cardeep |
| `T09-dedup-entity-resolution.md` | Dedup / entity resolution / address normalization | cardeep |
| `T10-geocoding-address.md` | Geocoding + address parsing (Spain) | cardex |
| `T11-perceptual-hash.md` | Perceptual image hashing / photo-delta fraud | CARDEX |
| `T12-queue-and-workers.md` | Job queue/transport + Python workers at scale | cardex-integration |
| `T13-datastore.md` | Datastore (Postgres 16/17/18, partitioning, OLAP) | cardeep |
| `T14-api-framework.md` | API framework + async data layer | cardeep |
| `T15-durable-orchestration.md` | Durable scheduling / orchestration | cardeep |
| `T16-observability.md` | Observability + alerting | cardeep |

> The audit files are distributed across the four CARDEEP/CARDEX working trees
> (canonical CARDEEP = `github.com/sublimine/Cardeep`, `projects/cardeep`). This
> master `TOOLING.md` is written to the canonical repo's
> `docs/architecture/tooling/`; consolidating the `T**` files into the same tree is
> a recommended housekeeping follow-up.

---

*Bill of Materials compiled 2026-06-12 from audits T01–T16. Every version pin and
recency claim is the responsibility of its source audit; this document is the binding
selection layer above them. No placeholders, no corpses recommended.*
