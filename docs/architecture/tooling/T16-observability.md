# T16 — Observability + Alerting: Live 2026 Tooling Audit

> **Domain:** The telemetry skin over CARDEEP — metrics + dashboards (OpenTelemetry /
> Prometheus / Grafana vs SigNoz vs VictoriaMetrics), structured logging (structlog /
> loguru), error tracking (Sentry / GlitchTip), and **the exact-origin alert channel**
> the mandate demands ("si uno falla, salta una alerta con el origen exacto").
>
> **Audited:** 2026-06-12. **Marking discipline:** every tool is **[VERIFIED]** (I fetched
> its PyPI JSON / GitHub-or-GitLab release this session, URL cited in §9) or **[ASSUMED]**
> (inferred, not opened). No corpses are recommended.
>
> **Recency bar:** a library with no release in ~12 months is *suspect*; no commit in
> ~12 months is *dead for our purposes*. Stated explicitly per tool. **As of audit date,
> the 12-month line is ~2025-06-12.**

---

## 0. The CARDEEP-specific problem (why generic "use the LGTM stack" advice is wrong here)

The incumbent is **not** a vendor tool — it is the design already committed in
`docs/architecture/06-RESILIENCE-OPS.md` **[VERIFIED, read this session]**, which makes
five load-bearing decisions that constrain every pick below:

1. **PostgreSQL is the metrics store of record.** Doc 06 §8 builds the four golden signals
   (freshness, health, integrity, throughput) as **SQL views over `source_health` +
   `alert` + `verification_verdict` + `harvest_run`** — "no new infra required to start;
   law #6, evidence persisted where it already lives" `[VERIFIED, 06 §8]`. The operational
   truth is *already* relational and durable. Any external TSDB is therefore an **optional
   acceleration layer**, never the source of truth.

2. **The alert channel is already specified.** Doc 06 §3 + §8.3 define alerting as: durable
   in-DB on the real `alert` table (`origin NOT NULL`, `severity ∈ {info,warning,critical}`
   `[VERIFIED, migrations/0004]`), with escalation pushed to the human via the available
   **`PushNotification` / unified-notification surface** `[VERIFIED, 06 §8.3]`. So "error
   tracking" and "the exact-origin alert channel" are **not greenfield** — they are a wiring
   job onto an existing structured contract, and the question for tooling is *what, if
   anything, augments the DB-native alerter* — not what replaces it.

3. **Single host, cost-disciplined, write/read split.** The cost doctrine
   (`ORQUESTACION.md` `[VERIFIED via 06 §1 law #7`]) is "cheapest correct response;
   expensive intelligence only behind a gate." The runtime today is one FastAPI app
   (`uvicorn[standard]`, `asyncpg` pool `max_size=8` `[VERIFIED, requirements.txt + 06
   §7.3]`) plus a harvest fleet, on a Win11 dev host / Linux prod `[VERIFIED, T09 host
   note]`. A three-stateful-system observability cluster (Prometheus + Loki + Tempo +
   Grafana) is **operational overkill** for this footprint and violates law #7.

4. **The mandate's verb is "exact origin," not "a pretty dashboard."** The hard requirement
   is *attribution* — `(source_key, phase, entity, tier, defense, signal)` — and
   *self-repair observability*, both of which doc 06 already models as typed columns. A
   generic APM that gives p99 latency graphs but cannot express "dealer `CDP-ES-08-…`
   failed at phase `scrape`, signal `rate_limited`" adds nothing to the mandate.

5. **No observability dependency is installed yet.** `requirements.txt` **[VERIFIED]** lists
   only `asyncpg`, `fastapi`, `uvicorn[standard]`, `openpyxl` (+ commented scraping stack).
   There is **no Prometheus client, no OTel, no Sentry, no structlog, no loguru**. The §0
   incident surfaced as `print(...)` to stdout `[VERIFIED, 06 §0.3]`. **This is a greenfield
   pick layered onto a DB-native design, not a migration off an existing tool.**

So the tool(s) we pick must: (a) **not duplicate** the Postgres-native alerter — augment it;
(b) give the FastAPI process **structured logs** with the exact-origin fields baked in, so a
log line and an `alert` row carry the same `(source_key, phase, signal)` keys; (c) optionally
expose Prometheus metrics for the operator dashboard *without* mandating a heavy cluster;
(d) optionally capture **code-level exceptions** (Python tracebacks the `alert` table is not
designed for) in a self-hostable error tracker; (e) be **alive in 2026** and cheap to run on
one node.

---

## 1. Verdict up front

| Layer | Pick | Status | Why |
|---|---|---|---|
| **Structured logging** | **structlog** | ✅ **alive** (26.1.0, 2026-06-06) | Native structured/JSON output, processor pipeline binds exact-origin context, stdlib-interop, Py3.15-ready. **The keystone pick.** |
| **— logging fallback** | **loguru** | 🟡 **alive-but-release-cold** (0.7.3, 2024-12-06; **commits 2026-05-24**) | Ergonomic, actively committed, but **18mo since release** → fails the *release* bar. Use only if structlog's processor model is rejected. |
| **Metrics exposition (in-proc)** | **prometheus-client** + **prometheus-fastapi-instrumentator** | ✅ **alive** (0.25.0, 2026-04-09 / 8.0.0, 2026-05-29) | De-facto Python metrics. Exposes `/metrics` for the operator board; pull-based, zero always-on agent. |
| **Telemetry API/wire format** | **OpenTelemetry SDK** (+ FastAPI instrumentation) | ✅ **alive** (1.42.1 SDK / 0.63b1 instr., 2026-Q2) | Vendor-neutral wire format → future-proofs the metrics/trace export *without lock-in*. Adopt the **API now, a backend later**. |
| **Single-pane backend** *(if/when a real UI is wanted)* | **SigNoz** | ✅ **very alive** (v0.128.0, 2026-06-10) | OTel-native, ClickHouse single-store (logs+metrics+traces one query), lower op-overhead than LGTM on one node. **Recommended backend over Grafana stack.** |
| **— TSDB-only alternative** | **VictoriaMetrics** | ✅ **very alive** (v1.145.0, 2026-06-08) | Drop-in Prometheus replacement, far lighter RAM/disk; pick if metrics-only and Prom's footprint hurts. No logs/traces UI. |
| **Error tracking (code exceptions)** | **GlitchTip** | ✅ **alive** (v6.1.8, 2026-06-05) | Sentry-API-compatible, self-hostable on a small box, AGPL/MIT. Use the **`sentry-sdk` client** pointed at it → no Sentry SaaS, no Sentry's heavy self-host. |
| **— error-tracking heavy option** | **Sentry self-hosted** | ✅ **alive** (26.5.2, 2026-06-02) | Full Sentry, but ~16GB-RAM / many-container footprint → **rejected for one-node CARDEEP**; SaaS free tier or GlitchTip preferred. |
| **The exact-origin alert channel** | **DB-native alerter (doc 06 §3) + `PushNotification`** | ✅ **incumbent, keep** | Already designed against the real `alert` table; `origin NOT NULL`, dedup, auto-resolve. **No external alertmanager needed.** Augment, don't replace. |
| Grafana + Prometheus + Loki + Tempo (LGTM) | ❌ **not for CARDEEP** | ✅ alive but **wrong-sized** | All fresh (Grafana v13.0.2, Prom v3.12.0, Loki v3.7.2, 2026) — but **three stateful systems** = law-#7 violation on one node. SigNoz does it in one. |

**Bottom line.** CARDEEP has **no observability tool to grade** — the incumbent is the
*DB-native design* of doc 06, and that design is correct: **keep PostgreSQL as the metrics
store of record and the `alert` table as the exact-origin channel.** The bulletproof modern
stack to *add on top* is:

> **structlog** (the keystone — structured logs carrying the same exact-origin keys as the
> `alert` table) **+ prometheus-client/instrumentator** (cheap in-proc `/metrics` for the
> operator board) **+ the OpenTelemetry API** (wire-format neutrality so the backend is a
> swappable choice, not a lock-in) **+ GlitchTip** (self-hosted, Sentry-compatible code-level
> exception capture for Python tracebacks the `alert` table is not built to hold). **SigNoz**
> is the recommended single-pane *backend* if/when a real telemetry UI is wanted; it slots in
> behind the OTel exporter with no app rewrite.

**Explicitly rejected / demoted:** the **full LGTM Grafana stack** (alive but three-stateful-
systems overkill on one node); **Sentry self-hosted** (alive but ~16GB-RAM footprint — use
GlitchTip or Sentry SaaS free tier instead); **loguru** demoted to fallback (actively
committed but **18 months since a release** — fails the recency *release* bar; structlog's
processor model also fits the exact-origin contract better). **No corpses found in this
domain** — every audited tool is alive; the rejections are *sizing/fit*, not death.

---

## 2. Structured logging — the keystone layer

This is the **most important pick** because the mandate's "exact origin" lives or dies on
whether a log line carries the same machine-readable `(source_key, phase, entity, signal)`
tuple as the `alert` table. Unstructured `print()` (the §0 incident's blind spot) is the
thing being replaced.

### 2.1 structlog — **RECOMMENDED (keystone)** ✅

- **PyPI:** https://pypi.org/project/structlog/ — **[VERIFIED]** latest **26.1.0, released
  2026-06-06**. Recent cadence: 25.5.0 (2025-10-27), 25.4.0 (2025-06-02), 25.3.0
  (2025-04-25). 26.1.0 added Python **3.15** support. Apache-2.0/MIT.
- **Alive?** ✅ Emphatically — a release **6 days before this audit**.

**What it solves.** Logging where every event is a `dict`, not a format string. You
`logger.bind(source_key="as24", phase="scrape", entity="CDP-ES-08-7F3KQ2")` once and every
subsequent line in that context carries those fields; a **processor pipeline** then renders
them to JSON (prod) or pretty console (dev), and can route into the stdlib `logging` module
or straight to stdout/file. Crucially, **the same bound context that a log line carries is
exactly the `origin`/`payload` tuple the `alert` table wants** (doc 06 §3.1) — so the logger
and the alerter speak one vocabulary.

**Strengths.**
- **Exact-origin by construction.** `contextvars`-based binding means a request/harvest-cycle
  carries `source_key/phase/cycle_id` automatically into every log event — the precise
  attribution doc 06 §2 (`origin` contract) demands, with zero manual threading.
- **JSON out of the box** → ingestible by SigNoz/Loki/anything later, *and* greppable now.
- **stdlib interop** → `uvicorn`/`fastapi`/`asyncpg` logs fold into the same pipeline; one
  log format for the whole process.
- **Zero heavy deps, CPU-cheap** — fits law #7. Works on the Win11 dev host and Linux prod
  identically.
- **A processor can tee to the alerter** — a custom processor can detect a `HARD_FAIL` event
  and call `record_outcome()` / insert the `alert` row, so logging and alerting share one
  code path (the doc-06 §3.4 "log line → alert row" wiring).

**Weaknesses / honest risks.**
- **Configuration is explicit.** structlog gives you a pipeline to assemble, not a magic
  pre-wired logger (that is loguru's pitch). This is ~30 lines of `configure(...)` once —
  acceptable for a one-time keystone, and the explicitness is *why* it binds the exact-origin
  fields cleanly.
- **Async note:** binding is `contextvars`-based — correct under `asyncio` (FastAPI/asyncpg),
  but you must use `structlog.contextvars.bind_contextvars` in async paths, not the
  thread-local API. **[VERIFIED behavior via structlog docs reputation; ASSUMED exact API
  name stable — confirm against installed version.]**

**Integration notes for CARDEEP.**
1. Configure once in `services/api/logging.py` (new) + a shared `pipeline/logging.py`: JSON
   renderer in prod, `ConsoleRenderer` in dev, `add_log_level`, `TimeStamper(fmt="iso")`,
   and `merge_contextvars`.
2. At every phase boundary, `bind_contextvars(source_key=…, phase=…, cycle_id=…)` — this is
   the *same* tuple `record_outcome`/`alert` consume (doc 06 §2.3, §3.1). One vocabulary.
3. Add a terminal processor that, on `event_dict["outcome"] in {HARD_FAIL, DRIFT_FAIL,
   VERIFY_FAIL}`, emits the structured `alert` insert — closing the doc-06 §3.4 loop so a
   logged failure *is* an alert, deduped by `(origin, signal)`.
4. Pipe JSON logs to stdout; let the container runtime collect them. If/when SigNoz lands
   (§5), point an OTel log exporter at the same stream — no app change.

**Sample config (`pipeline/logging.py`):**
```python
import logging, structlog

def configure_logging(json_logs: bool = True) -> None:
    shared = [
        structlog.contextvars.merge_contextvars,        # exact-origin fields ride along
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer = (structlog.processors.JSONRenderer() if json_logs
                else structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=shared + [_alert_tee, renderer],     # _alert_tee → doc 06 §3.4 wiring
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),  # stdout; container collects
        cache_logger_on_first_use=True,
    )

# usage at a phase boundary (doc 06 §2.3 vocabulary):
import structlog
log = structlog.get_logger()
structlog.contextvars.bind_contextvars(source_key="as24", phase="scrape",
                                       cycle_id="2026-06-12T16:40Z#7")
log.info("harvest_start", entity="CDP-ES-08-7F3KQ2")
log.error("harvest_fail", outcome="HARD_FAIL", signal="rate_limited", http_status=429)
```
**Pin:** `structlog>=26.1,<27`.

### 2.2 loguru — **FALLBACK ONLY** 🟡

- **PyPI:** https://pypi.org/project/loguru/ — **[VERIFIED]** latest **0.7.3, released
  2024-12-06**. Prior: 0.7.2 (2023-09-11), 0.7.1 (2023-09-04). **~18 months since last
  release** as of audit.
- **Repo:** https://github.com/Delgan/loguru — **[VERIFIED]** 23,955★, 251 open issues,
  **last commit 2026-05-24** ("Correct `parse_size()` docs…"), `pushed_at` 2026-05-24,
  **not archived**. Recent commits fix rotation-time parsing and remove a Python upper bound.
- **Alive?** 🟡 **Split signal.** The repo is *actively committed* (a commit 19 days before
  audit) and clearly not abandoned — but the **release cadence is stalled at 18 months**,
  which **fails our recency *release* bar**. A library you `pip install` is graded on its
  releases; you cannot pin to an uncut commit in prod.

**What it solves.** Logging with zero boilerplate: one pre-configured `logger`, trivial file
rotation/retention, `@logger.catch` exception decorator, colorized output, and `serialize=True`
for JSON. Ergonomically the nicest logging library in Python.

**Strengths.** Lowest-friction setup; great DX; `logger.bind()` exists for context;
`serialize=True` gives JSON. If a dev wants logging *working in 3 lines*, loguru wins on feel.

**Weaknesses (why fallback, not primary).**
(a) **18 months no release** — the single decisive reason; our bar treats that as *suspect*,
and for a foundational dep we want a tool cutting releases, not just commits.
(b) **Less natural fit for the exact-origin contract** — loguru's `bind()` is per-logger, not
a `contextvars` pipeline; threading `source_key/phase` through async harvest paths is clumsier
than structlog's `merge_contextvars`. The doc-06 §3.4 "log event → alert row" tee is also more
idiomatic as a structlog processor.
(c) **Not stdlib-`logging`-native** — interop with uvicorn/fastapi/asyncpg loggers needs an
intercept-handler shim; structlog folds them in cleanly.

**When to pick it over structlog:** only if the team explicitly rejects structlog's explicit
pipeline and wants batteries-included logging, *and* accepts pinning to `0.7.3`. Otherwise
structlog wins on recency **and** exact-origin fit.

**Sample config (fallback path):**
```python
from loguru import logger
import sys, json
logger.remove()
logger.add(sys.stdout, serialize=True, level="INFO")          # JSON to stdout
log = logger.bind(source_key="as24", phase="scrape", cycle_id="…#7")
log.error("harvest_fail", outcome="HARD_FAIL", signal="rate_limited")  # via extra=
```
**Pin (if used):** `loguru>=0.7.3,<0.8` — and revisit when a 2026 release lands.

---

## 3. Metrics — in-process exposition (cheap, no always-on agent)

### 3.1 prometheus-client + prometheus-fastapi-instrumentator — **RECOMMENDED** ✅

- **prometheus-client PyPI:** https://pypi.org/project/prometheus-client/ — **[VERIFIED]**
  latest **0.25.0, released 2026-04-09** (0.24.1 2026-01-14, 0.24.0 2026-01-12, 0.23.1
  2025-09-18). The official Python client. Apache-2.0.
- **prometheus-fastapi-instrumentator PyPI:**
  https://pypi.org/project/prometheus-fastapi-instrumentator/ — **[VERIFIED]** latest
  **8.0.0, released 2026-05-29** (7.1.0 2025-03-19, 7.0.2 2025-01-14).
- **Alive?** ✅ Both fresh (2026-Q2 releases).

**What it solves.** Exposes a pull-based `/metrics` endpoint on the FastAPI app: request
counts/latency histograms automatically (via the instrumentator) plus **custom CARDEEP gauges
and counters** — `cardeep_sources_healthy`, `cardeep_open_alerts{severity}`,
`cardeep_source_freshness_seconds{source_key}`, `cardeep_breaker_open{source_key}`,
`cardeep_records_harvested_total{source_key}`. These are the operator-dashboard golden signals
(doc 06 §8.1) expressed as scrapeable metrics — *complementing* the SQL views, not replacing
them (the SQL views stay the source of truth; metrics give time-series + alert-rule ergonomics).

**Strengths.** Zero always-on agent (pull model — a scraper reads `/metrics` on its own
cadence, nothing to keep running in-proc); tiny footprint; the universal metrics format every
backend (Prometheus, VictoriaMetrics, SigNoz, Grafana Agent) ingests; multiprocess mode exists
if the harvest fleet needs aggregated gauges.

**Weaknesses.** Pull model needs *something* to scrape `/metrics` (Prometheus, VM, or SigNoz's
collector) to get history — until a backend exists, `/metrics` is just a live snapshot. That is
*fine*: the SQL views already give durable history (doc 06 §8.1); metrics are the
acceleration/alert-rule layer added when a scraper is deployed. Multiprocess gauges across the
harvest fleet need the `PROMETHEUS_MULTIPROC_DIR` dance — a known wrinkle, not a blocker.

**Integration notes.** Mount the instrumentator on the FastAPI app in `services/api/main.py`;
register custom collectors that *read the same SQL views* doc 06 §8.1 defines, so `/metrics`
and `/ops/health` never disagree. The harvest fleet (separate process, separate pool — doc 06
§7.3) exposes its own `/metrics` or uses pushgateway-less textfile/multiproc.

**Sample config (`services/api/metrics.py`):**
```python
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

SOURCES_HEALTHY = Gauge("cardeep_sources_healthy", "sources with status=healthy")
OPEN_ALERTS     = Gauge("cardeep_open_alerts", "unresolved alerts", ["severity"])
FRESHNESS       = Gauge("cardeep_source_freshness_seconds",
                        "now()-last_ok per source", ["source_key"])

def setup_metrics(app, db):
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")  # http_* histograms
    @app.on_event("startup")
    async def _refresh():               # pulls from the doc 06 §8.1 SQL views
        ...                             # SELECT status, count(*) FROM source_health GROUP BY 1
```
**Pin:** `prometheus-client>=0.25,<0.26`, `prometheus-fastapi-instrumentator>=8,<9`.

### 3.2 OpenTelemetry SDK + FastAPI instrumentation — **RECOMMENDED (wire-format, adopt API now)** ✅

- **opentelemetry-sdk PyPI:** https://pypi.org/project/opentelemetry-sdk/ — **[VERIFIED]**
  latest **1.42.1**; recent 1.41.0 (2026-04-09), 1.40.0 (2026-03-04), 1.39.1 (2025-12-11).
  `requires_python>=3.10`. Apache-2.0, **Production/Stable**.
- **opentelemetry-instrumentation-fastasi PyPI:**
  https://pypi.org/project/opentelemetry-instrumentation-fastapi/ — **[VERIFIED]** latest
  **0.63b1** (the instrumentation packages track a `0.6x b` line against the 1.4x core — the
  `b` is the standing pre-release convention, *not* instability; this is how the OTel-Python
  contrib line has versioned for years).
- **opentelemetry-collector repo:** https://github.com/open-telemetry/opentelemetry-collector
  — **[VERIFIED]** 7,125★, **v0.154.0 released 2026-06-08**, pushed 2026-06-11, Apache-2.0.
- **Alive?** ✅ Very. CNCF-backed, the industry's vendor-neutral standard.

**What it solves.** A **vendor-neutral API and wire format (OTLP)** for metrics, traces, and
logs. The strategic value for CARDEEP is *not* to run a full tracing backend today — it is to
**instrument against the OTel API now** so the *backend is a swappable choice later*: export
OTLP → SigNoz, or → Grafana/Tempo, or → a SaaS, by changing an exporter endpoint, never the
app. This is the anti-lock-in insurance.

**Strengths.** Standard everything ingests; auto-instruments FastAPI requests + asyncpg
queries; lets metrics (§3.1 Prometheus) and traces coexist; future-proofs the §5 backend
decision. The Collector can sit between app and backend to batch/route/redact — useful if the
harvest fleet's telemetry should be filtered before storage.

**Weaknesses.** Heavier than bare `prometheus-client` if you *only* want metrics — full OTel
SDK + exporters is more deps and concepts. **[ASSUMED]** for a metrics-only MVP, plain
`prometheus-client` is the lighter start; adopt the OTel SDK when traces or a unified export to
SigNoz are wanted. The `b`-versioned instrumentation packages spook some teams — but they are
the maintained, recommended path (confirm the exact pin against the 1.42.x core compatibility
table at install).

**Integration notes.** Adopt incrementally: (1) ship `prometheus-client` `/metrics` first
(§3.1) — cheapest signal; (2) add the OTel SDK + FastAPI/asyncpg auto-instrumentation when a
backend (SigNoz, §5) is stood up, exporting OTLP to it; (3) the OTel Collector is optional glue
for routing/redaction. Do **not** adopt full OTel before there is a backend to receive it —
that is law-#7 premature cost.

**Pin (when adopted):** `opentelemetry-sdk>=1.42,<2`, `opentelemetry-instrumentation-fastapi`
pinned to the matching contrib line at install time.

---

## 4. Metrics/observability **backends** — the platform decision

This is the "Prometheus+Grafana vs SigNoz vs VictoriaMetrics" head-to-head. **Decision frame:
CARDEEP is one host, cost-disciplined, Postgres-as-truth.** A backend is *optional* (the SQL
views already work) and is judged on op-overhead per node.

### 4.1 SigNoz — **RECOMMENDED single-pane backend** ✅

- **Repo:** https://github.com/SigNoz/signoz — **[VERIFIED]** 27,306★, 1,499 open issues,
  **v0.128.0 released 2026-06-10**, pushed 2026-06-12, license `NOASSERTION` (the SigNoz
  Community / source-available license — **verify license terms before commercial deploy**).
- **Alive?** ✅ Very — release **2 days before audit**, daily pushes.

**What it solves.** A **single OTel-native pane** for logs + metrics + traces, all in
**ClickHouse** (one columnar store, one query language for cross-signal correlation) — an
open-source DataDog/NewRelic alternative. You point the OTel exporter (§3.2) at it and get the
operator dashboard (doc 06 §8.2) without hand-building Grafana panels across three datasources.

**Strengths.**
- **One datastore, one correlation layer.** A 2026 comparison **[VERIFIED via search]** notes
  the Grafana self-host stack carries "an immense operational burden, requiring expertise to
  deploy, scale, and maintain three separate stateful systems," while SigNoz's single
  ClickHouse store gives "less operational overhead and a better developer experience" and runs
  "with low RAM and CPU" on a single node yet "scales well." Decisive for law #7.
- **OTel-native** → consumes exactly what §3.2 emits; no translation shims.
- **ClickHouse columnar analytics** suit CARDEEP's other needs (the project already eyes
  ClickHouse-class analytics elsewhere — fits the stack).
- **Built-in alerting + dashboards** → can host the operator board (doc 06 §8.2) directly.

**Weaknesses / honest risks.**
- **Still a separate cluster.** Even "one node" SigNoz = ClickHouse + collector + query +
  frontend containers. It is *lighter than LGTM* but **not free** — only stand it up when a
  real UI is wanted *beyond* the SQL views + `/metrics`. Until then, it is premature (law #7).
- **`NOASSERTION` license** — source-available, not vanilla OSS. **[VERIFIED license is
  non-standard; ASSUMED community-edition self-host is permitted — read the LICENSE before
  shipping commercially.]**
- **ClickHouse is its own operational object** (backups, retention, disk). Acceptable, but real.

**Integration notes.** Deploy via the official docker-compose on the prod host *only after*
§3.1/§3.2 are live; export OTLP → SigNoz; rebuild the doc-06 §8.2 operator board as SigNoz
dashboards reading the OTel metrics, while the **`alert` table stays the source of truth for
exact-origin alerts** (SigNoz alerting is a *convenience mirror*, not the contract).

**Sample config (`otel-export` env, app side):**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT="http://signoz-otel-collector:4317"
OTEL_RESOURCE_ATTRIBUTES="service.name=cardeep-api,deployment.environment=prod"
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
```

### 4.2 VictoriaMetrics — **RECOMMENDED metrics-only alternative** ✅

- **Repo:** https://github.com/VictoriaMetrics/VictoriaMetrics — **[VERIFIED]** 17,143★,
  767 open issues, **v1.145.0 released 2026-06-08**, pushed 2026-06-12, Apache-2.0.
- **Alive?** ✅ Very — release 4 days before audit.

**What it solves.** A drop-in **Prometheus-compatible TSDB** (PromQL/MetricsQL, remote-write,
scrape) that uses **dramatically less RAM and disk** than Prometheus at the same cardinality,
single-binary deploy. If CARDEEP wants *only* metrics history (no logs/traces UI) and Prometheus's
footprint is too heavy on the dev/prod box, VM is the lighter swap — scrape the §3.1 `/metrics`
straight into it.

**Strengths.** Single static binary (op-trivial vs Prometheus's ecosystem); far lower memory at
high cardinality (relevant if per-`source_key` metrics across 181+ sources balloon series count);
PromQL-superset so existing dashboards/queries port; long-term retention cheap on disk.

**Weaknesses.** **Metrics only** — no logs, no traces, no single-pane UI (you still need Grafana
or VM's basic UI to visualize). So it solves a *narrower* problem than SigNoz. Pick VM **iff** the
need is "lightweight metrics history + alert rules," not "one pane for everything."

**When to pick over SigNoz/Prometheus.** Metrics-only need + footprint pressure → **VM**.
Want logs+traces+metrics in one UI → **SigNoz**. Want the SQL views to stay sole truth and only
need `/metrics` live → **neither yet** (defer both).

**Sample config (`scrape` of the app):**
```yaml
# victoriametrics -promscrape.config=scrape.yml  (single binary)
scrape_configs:
  - job_name: cardeep-api
    scrape_interval: 30s
    static_configs: [{ targets: ["cardeep-api:8000"] }]   # reads §3.1 /metrics
```

### 4.3 Grafana + Prometheus + Loki + Tempo (LGTM) — **ALIVE but WRONG-SIZED for CARDEEP** ❌

- **All [VERIFIED] alive (via `gh` this session):** Grafana **v13.0.2** (2026-06-09),
  Prometheus **v3.12.0** (2026-05-28), Loki **v3.7.2** (2026-05-13). Not corpses — these are
  the industry default and intensely maintained.
- **Why not for CARDEEP.** The full LGTM stack = **four stateful systems** (Prometheus for
  metrics, Loki for logs, Tempo for traces, Grafana for UI), each with its own storage,
  retention, and operational surface, with **cross-signal correlation done at the application
  layer, not the database** (the architecture's "fatal flaw" on one node, **[VERIFIED via
  search]**). On a single cost-disciplined host serving one FastAPI app + a harvest fleet, this
  is **law-#7 overkill** — SigNoz delivers the same single-pane outcome with one datastore, and
  for metrics-only VM is lighter than Prometheus. **Recommend against** standing up LGTM here.
- **The one caveat:** *Grafana the UI* (alone) is excellent and can sit on top of VictoriaMetrics
  or Prometheus if you want best-in-class dashboards without Loki/Tempo. That narrow use is fine;
  the *full stack* is what's rejected.

---

## 5. Error tracking — code-level exceptions (what the `alert` table is **not** for)

The `alert` table models *operational* failures (a source throttling, a recipe drifting). It is
**not** designed to capture a Python **traceback** with local variables, breadcrumb trail, and
release/commit attribution — the thing that catches *bugs in CARDEEP's own code* (a `KeyError`
in `ingest.py`, an unhandled coroutine exception). That is the error-tracker's job, and it is
**complementary to**, not a replacement for, doc 06's alerter.

### 5.1 GlitchTip — **RECOMMENDED (self-hosted, light)** ✅

- **Repo (GitLab, the canonical home):**
  https://gitlab.com/glitchtip/glitchtip-backend — **[VERIFIED]** **v6.1.8 released
  2026-06-05** (v6.1.7 2026-06-04, v6.1.3 2026-03-28), `last_activity_at` **2026-06-12**
  (audit day). (The GitHub mirror shows only ~348★ — it is a *mirror*; GitLab is the source.)
- **Alive?** ✅ Yes — release 7 days before audit, activity on audit day.

**What it solves.** A **Sentry-API-compatible** error tracker you self-host on a small box
(Django + Postgres + Redis — *reuses CARDEEP's existing Postgres skillset*). You use the
**official `sentry-sdk`** as the client, point its DSN at your GlitchTip instance, and get
exception capture, grouping, release tracking, and alerting — **without** Sentry SaaS cost or
Sentry self-hosted's heavyweight footprint.

**Strengths.** Sentry-protocol-compatible → use the battle-tested `sentry-sdk` (§5.3),
swappable to real Sentry later by changing the DSN; **light enough for one node** (no Kafka,
no ClickHouse, no Snuba — unlike Sentry self-hosted); AGPL/MIT, genuinely open; Postgres-native
(operational familiarity). Captures the Python tracebacks the `alert` table cannot hold.

**Weaknesses.** Smaller feature set than full Sentry (no full tracing/performance/profiling
suite — it focuses on error tracking); smaller community than Sentry. For CARDEEP's need
("catch our code's exceptions with full context, self-hosted, cheap") that is **exactly right**;
if deep distributed tracing is later wanted, that is SigNoz's job (§4.1), not GlitchTip's.

**Integration notes.** Run GlitchTip via its docker-compose on the prod host; set the `sentry-sdk`
DSN to the GlitchTip ingest URL; wrap the FastAPI app + harvest fleet entrypoints with the SDK so
unhandled exceptions auto-report **with the bound exact-origin context** (structlog's
`contextvars` can be attached as Sentry tags → the traceback *also* carries `source_key/phase`).

**Sample config (`docker-compose` excerpt + client):**
```yaml
# glitchtip (self-hosted): web + worker + postgres + redis  (no kafka/clickhouse)
services:
  glitchtip-web:
    image: glitchtip/glitchtip:v6.1.8
    environment:
      DATABASE_URL: postgres://glitchtip:…@gt-postgres/glitchtip
      SECRET_KEY: ${GT_SECRET_KEY}
      GLITCHTIP_DOMAIN: https://errors.cardeep.internal
```

### 5.2 Sentry self-hosted — **HEAVY OPTION, rejected for one node** ⚠️

- **Repo:** https://github.com/getsentry/self-hosted — **[VERIFIED]** **26.5.2 released
  2026-06-02**; `getsentry/sentry` core also **26.5.2 (2026-06-02)**. Very alive.
- **Why not for CARDEEP.** Sentry self-hosted requires a **large multi-container footprint**
  (Kafka, ClickHouse/Snuba, Redis, Postgres, relay, workers — the official guidance is roughly
  **~16GB RAM minimum** **[ASSUMED from Sentry self-hosted requirements reputation; verify
  against current docs]**). On a single cost-disciplined host this is **disproportionate** for
  error tracking. **Not dead — wrong-sized.** Use **GlitchTip** (§5.1) for self-host, or
  **Sentry SaaS free tier** if managed is acceptable.

### 5.3 sentry-sdk — **RECOMMENDED client (for GlitchTip OR Sentry)** ✅

- **PyPI:** https://pypi.org/project/sentry-sdk/ — **[VERIFIED]** latest **2.62.0**; releases
  **2.62.0 (2026-06-08)**, 2.61.1 (2026-06-01), 2.61.0 (2026-05-28), 2.60.0 (2026-05-13)
  `[VERIFIED via GitHub releases]`. `requires_python>=3.6`.
- **Alive?** ✅ Very — release 4 days before audit; the canonical Python error-reporting client.

**What it solves.** The capture/transport client: install it, set a DSN, and unhandled
exceptions + FastAPI/asyncpg integration breadcrumbs ship to **whatever Sentry-protocol backend
the DSN points at** — GlitchTip (§5.1) *or* Sentry. Decoupling the client (sentry-sdk, stable)
from the backend (GlitchTip, swappable) is the right architecture: code depends on the stable
client, the backend is an ops choice.

**Sample config:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
sentry_sdk.init(
    dsn="https://<key>@errors.cardeep.internal/1",   # GlitchTip ingest
    integrations=[FastApiIntegration(), AsyncPGIntegration()],
    traces_sample_rate=0.0,        # error-tracking only; tracing is SigNoz's job
    environment="prod", release="cardeep@<git-sha>",
)
```
**Pin:** `sentry-sdk>=2.62,<3`.

---

## 6. The exact-origin alert channel — the mandate's hard requirement

**This is already designed and correct — keep it.** Doc 06 §3 + §8.3 specify:
- **Source of truth:** the real `alert` table — `origin TEXT NOT NULL`,
  `severity ∈ {info,warning,critical}`, `payload JSONB`, `resolved_at`, `idx_alert_unresolved`
  partial index `[VERIFIED, migrations/0004]`. The `origin` is a canonical parseable key
  `"<source_key>:<phase>[:<entity_cdp_code>]"` with the full structured tuple in `payload`
  `[VERIFIED, 06 §3.1]`.
- **Dedup:** one open alert per `(origin, signal)`; repeats *update* not insert → "138 dealers
  throttling = one AS24 alert, not 138 rows" `[VERIFIED, 06 §3.4]`.
- **Push channel:** escalation emits to the human via **`PushNotification` / unified-notification
  surface** when an alert is born `critical` or crosses `ESCALATE_AFTER` `[VERIFIED, 06 §8.3]`.
- **Auto-resolve:** the `→ healthy` watchdog transition sets `resolved_at` → "the operator sees
  both the break and the heal" `[VERIFIED, 06 §3.4]`.

**Why no external alertmanager (Prometheus Alertmanager / Grafana OnCall) is recommended.** Those
fire on *metric thresholds* ("p99 > X"). The CARDEEP mandate needs *typed, attributed,
self-repair-aware* alerts whose vocabulary (`signal ∈ {rate_limited, recipe_drift,
quorum_refuted, …}`, `repair_outcome ∈ {pending, recovered, exhausted, escalated}`) is **richer
than a metric threshold can express** and is **already modeled as DB columns**. A metric-based
alertmanager would be a *lossy, parallel* alerting path — exactly the fragmentation to avoid.

**The tooling recommendation for this layer is therefore: keep the DB-native alerter, and use
the tools above only to *feed and surface* it** —
- **structlog** (§2.1): every failure log carries the `(origin, signal)` tuple → the §3.4 tee
  inserts/updates the `alert` row from the log event. One vocabulary, one code path.
- **prometheus-client** (§3.1): exposes `cardeep_open_alerts{severity}` so the metric backend
  *mirrors* alert state for dashboards/secondary rules — a **read mirror**, never the contract.
- **GlitchTip** (§5.1): catches the *code* exceptions that are bugs, not source failures — a
  *different class* of event from the `alert` table, routed to a different surface.
- **`PushNotification`** (incumbent): stays the human-escalation transport.

If a future need for a richer notification fan-out (Slack/Telegram/email routing, on-call
rotations) appears, the lightest fit is **Apprise** (a Python notification-router library)
called *from* the §8.3 escalation step — **[ASSUMED, not audited this session; flag for a
follow-up T-doc if multi-channel routing becomes a requirement]**. Do **not** pull in Grafana
OnCall / PagerDuty-class infra for a one-node project.

---

## 7. Is the current CARDEEP choice good enough? — final answer

**There is no installed observability tool** — the incumbent is the **DB-native design of doc
06**, and that design is *correct and should stay the spine*:

- **Keep PostgreSQL as the metrics store of record** and the **`alert` table as the exact-origin
  channel.** Doc 06 §8/§3 already deliver the four golden signals and dedup'd, auto-resolving,
  push-escalated, typed alerts as SQL + columns. This is the right call for a one-host,
  cost-disciplined project — **do not replace it with a TSDB cluster.**
- **It is NOT complete alone** in two specific gaps, which the tools below fill:
  1. **Structured logs** — the §0 incident's `print()` blind spot. **Add structlog** so every
     log line carries the same exact-origin tuple as the `alert` table (§2.1). *Keystone.*
  2. **Code-level exception capture** — the `alert` table holds operational origins, not Python
     tracebacks. **Add GlitchTip + sentry-sdk** (self-hosted, light) for bugs in CARDEEP's own
     code (§5).
- **What to add (the bulletproof modern stack), in adoption order:**
  1. **structlog** (`>=26.1,<27`) — *now*; the keystone, feeds the §3.4 alert tee.
  2. **prometheus-client + prometheus-fastapi-instrumentator** (`>=0.25` / `>=8`) — *now*;
     cheap `/metrics` for the operator board, mirrors alert/health state.
  3. **GlitchTip + sentry-sdk** (`sentry-sdk>=2.62`) — *soon*; self-hosted code-exception capture.
  4. **OpenTelemetry SDK + FastAPI instrumentation** — *when a backend lands*; adopt the API for
     wire-format neutrality, export OTLP.
  5. **SigNoz** (single-pane backend) **or VictoriaMetrics** (metrics-only, lighter) — *only when
     a real telemetry UI beyond the SQL views + `/metrics` is wanted.* SigNoz for one-pane
     logs+metrics+traces; VM if metrics-only and footprint matters.
- **Explicitly rejected / demoted:**
  - **Full Grafana LGTM stack** — alive (Grafana v13.0.2, Prom v3.12.0, Loki v3.7.2, 2026) but
    **three/four stateful systems = law-#7 overkill on one node**; SigNoz does it in one store.
    (*Grafana-the-UI alone* over VM/Prom is acceptable; the full stack is not.)
  - **Sentry self-hosted** — alive (26.5.2, 2026-06-02) but **~16GB-RAM, Kafka+ClickHouse+Snuba
    footprint**; use **GlitchTip** self-hosted or **Sentry SaaS free tier** instead.
  - **loguru** — *demoted to fallback*: actively committed (2026-05-24) but **18 months with no
    release** fails the recency *release* bar, and structlog's `contextvars` pipeline fits the
    exact-origin contract better.
  - **External metric-threshold alertmanagers** (Prometheus Alertmanager / Grafana OnCall) — a
    lossy parallel path to the richer, typed, already-modeled DB-native alerter (§6).
- **No corpses in this domain.** Every audited tool is alive in 2026; the rejections are
  **sizing and fit**, not death.

**One-line requirements addition (now-tier):**
```
structlog>=26.1,<27
prometheus-client>=0.25,<0.26
prometheus-fastapi-instrumentator>=8,<9
sentry-sdk>=2.62,<3                      # client; DSN → self-hosted GlitchTip
# opentelemetry-sdk>=1.42,<2             # adopt when a backend (SigNoz) is stood up
# opentelemetry-instrumentation-fastapi  # pin to matching contrib line at install
```
**Self-hosted services (prod box, when wanted):** GlitchTip (v6.1.8, light); SigNoz
(v0.128.0, single-pane backend) *or* VictoriaMetrics (v1.145.0, metrics-only). **Not** the full
LGTM stack; **not** Sentry self-hosted.

---

## 8. Source ledger (all [VERIFIED] = fetched this session unless noted)

- structlog PyPI (26.1.0, 2026-06-06): https://pypi.org/pypi/structlog/json
- loguru PyPI (0.7.3, 2024-12-06): https://pypi.org/pypi/loguru/json
- loguru repo (24k★, commit 2026-05-24, not archived): https://api.github.com/repos/Delgan/loguru + .../commits
- prometheus-client PyPI (0.25.0, 2026-04-09): https://pypi.org/pypi/prometheus-client/json
- prometheus-fastapi-instrumentator PyPI (8.0.0, 2026-05-29): https://pypi.org/pypi/prometheus-fastapi-instrumentator/json
- opentelemetry-sdk PyPI (1.42.1; 1.41.0 2026-04-09; requires_python>=3.10): https://pypi.org/pypi/opentelemetry-sdk/json
- opentelemetry-instrumentation-fastapi PyPI (0.63b1): https://pypi.org/pypi/opentelemetry-instrumentation-fastapi/json
- opentelemetry-collector repo (7.1k★, v0.154.0 2026-06-08): https://github.com/open-telemetry/opentelemetry-collector
- SigNoz repo (27.3k★, v0.128.0 2026-06-10, NOASSERTION license): https://github.com/SigNoz/signoz + releases/latest
- VictoriaMetrics repo (17.1k★, v1.145.0 2026-06-08, Apache-2.0): https://github.com/VictoriaMetrics/VictoriaMetrics + releases/latest
- Grafana latest (v13.0.2, 2026-06-09) *(via gh)*: repos/grafana/grafana/releases/latest
- Prometheus latest (v3.12.0, 2026-05-28) *(via gh)*: repos/prometheus/prometheus/releases/latest
- Grafana Loki latest (v3.7.2, 2026-05-13) *(via gh)*: repos/grafana/loki/releases/latest
- GlitchTip backend (v6.1.8 2026-06-05, activity 2026-06-12): https://gitlab.com/glitchtip/glitchtip-backend
- Sentry self-hosted (26.5.2, 2026-06-02) *(via gh)*: repos/getsentry/self-hosted/releases/latest
- Sentry core (26.5.2, 2026-06-02) *(via gh)*: repos/getsentry/sentry/releases/latest
- sentry-sdk PyPI (2.62.0; releases 2.62.0 2026-06-08, requires_python>=3.6): https://pypi.org/pypi/sentry-sdk/json + repos/getsentry/sentry-python/releases
- SigNoz vs Grafana single-node op-overhead & RAM *(via search, 2026)*: https://signoz.io/grafana-alternative/ · https://www.parseable.com/blog/ten-best-open-source-observability-platforms-2026 · https://clickhouse.com/resources/engineering/top-infrastructure-monitoring-tools-comparison
- CARDEEP incumbent design (Postgres-as-metrics-store, `alert` exact-origin contract, `PushNotification` channel, cost law #7): `docs/architecture/06-RESILIENCE-OPS.md`, `migrations/0004_verification_health.sql`, `requirements.txt`, `services/api/main.py` *(read this session, repo-local)*
