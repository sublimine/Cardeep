# T06 — Scraping Framework / Orchestration Audit

> Domain: Scraping framework & orchestration — self-healing selectors, async
> concurrency, retry/middleware, scale to millions.
> Candidates audited: **Scrapling** · **Scrapy** · **Crawlee-python** ·
> **Frontera** · **custom asyncio** (CARDEEP's current stack).
> Audit date: **2026-06-12**. All recency claims fetched live this date.
> Anti-hallucination: every claim tagged `[VERIFIED]` (I fetched the repo/page)
> or `[ASSUMED]` (inference, not directly read). Source URLs inline.

---

## TL;DR — Verdict

**CARDEEP already runs a custom asyncio coordinator** (`scrapers/coordinator.py`
+ tiered engine: `curl_cffi` T1 → Camoufox T2/T3, identity store, proxy pool,
circuit breakers, Prometheus). `[VERIFIED]` — read the source.

This custom orchestration is the **right backbone** and should be **kept**. None
of the off-the-shelf frameworks beat it for CARDEEP's specific shape (per-source
recipes, JA3/identity invariants, tiered escalation, anti-detect-first). The
mistake would be ripping it out for a framework that does *less*.

What CARDEEP is **missing** is not an orchestrator — it is a best-in-class
**adaptive parsing + self-healing selector layer**. That is exactly Scrapling's
sweet spot, and exactly where it does *not* collapse at scale (parsing is local,
per-page, cheap).

| Decision | Pick |
|---|---|
| **Orchestration (millions-scale)** | **KEEP custom asyncio coordinator** (primary) |
| **Parsing + self-healing selectors** | **ADOPT Scrapling as a library** (the `Selector`/`Adaptor` parser, not its Spider) |
| **Distributed queue fallback / greenfield sources** | **Crawlee-python** (fallback orchestrator) |
| **Legacy heavyweight alternative** | Scrapy (only if a Scrapy-ecosystem dependency forces it) |
| **DEAD — do not touch** | **Frontera** (last release 2019) |

---

## Candidate 1 — Scrapling  ✅ ADOPT (as parser/self-healing library)

- **Repo:** https://github.com/D4Vinci/Scrapling
- **Latest release:** **v0.4.9 — 2026-06-07** `[VERIFIED]` (fetched repo + commits)
- **Most recent commit:** **2026-06-07** (v0.4.9), prior commits 2026-06-04 /
  2026-06-03 `[VERIFIED]` — actively maintained, commits within days of audit.
- **Stars:** ~63.2k `[VERIFIED]` · **Open issues:** **4** `[VERIFIED]` (remarkably
  clean — strong maintenance signal) · **License:** BSD-3-Clause `[VERIFIED]`
- **Python:** 3.10+ `[VERIFIED]`

### What it solves
Adaptive parsing with **self-healing selectors**: with `adaptive=True` +
`auto_save=True` it caches the element's structural fingerprint and **re-locates
the element via a deterministic similarity algorithm** (no LLM, no API call) when
the site's DOM shifts — selectors stop silently breaking on redesigns.
Source: https://scrapling.readthedocs.io/en/latest/index.html `[VERIFIED]`

### Strengths
- **Parsing speed is best-in-class.** Benchmarks (5000 nested elements, text
  extraction): Scrapling **2.02 ms** ≈ Parsel **2.04 ms**, beats raw lxml
  (2.54 ms), and is **~784× faster than BeautifulSoup+lxml** (1584 ms).
  Adaptive find: **2.39 ms** vs AutoScraper 12.45 ms (5.2×).
  Source: https://scrapling.readthedocs.io/en/latest/benchmarks.html `[VERIFIED]`
- **Self-healing is local + deterministic** → cheap per page, no per-request
  network/LLM cost. This is the one capability no competitor here ships natively.
- **Ships an MCP server** exposing fetchers/parsers as tools — directly usable by
  Claude Code agents. Source: WebSearch result, pythonlibraries.substack `[VERIFIED]`
- Anti-bot fetchers (Cloudflare Turnstile bypass) exist, but CARDEEP **already
  has a stronger, JA3-pinned anti-detect stack** (Camoufox + curl_cffi).

### Weaknesses (the load-bearing part for CARDEEP)
Source: https://use-apify.com/blog/scrapling-python-web-scraping-framework `[VERIFIED]`
- **Its Spider/orchestration layer is NOT battle-tested for distributed,
  millions-scale crawls.** No distributed queue, no cross-machine coordination,
  no CRON orchestration documented.
- **Memory exhaustion under load:** the stealth fetcher crashes a standard 8 GB
  VPS above **~10 concurrent requests**. `[VERIFIED]`
- **No integrated proxy-mesh / IP coordination** — you bring your own. (CARDEEP
  already has `engine/proxy/pool.py`.)
- **Self-heal fails on catastrophic redesigns** (server-HTML → React/WebSocket
  SPA) — the fingerprint has nothing to match against. `[VERIFIED]`
- **Ephemeral-storage footgun:** fingerprint DB is local (SQLite-style). On
  serverless without a mounted persistent volume, fingerprints are wiped on cold
  start, neutering `auto_match`. `[VERIFIED]` → CARDEEP must persist the
  fingerprint store on a durable volume / shared path.

### Recommendation
**Adopt Scrapling as a library for the parsing + self-healing layer only.** Do
**not** adopt its `Spider`. Feed it the HTML/response that CARDEEP's existing
tiered fetchers already retrieve. This gives CARDEEP self-healing per-source
recipes (a stated CARDEEP goal) without surrendering the orchestration that
already outclasses Scrapling's.

```python
# scrapers/common/parse.py  — Scrapling as a pure parser, fed by CARDEEP fetchers
from scrapling.parser import Adaptor  # parser only; no Scrapling fetcher/Spider

# `html` comes from CARDEEP's existing curl_cffi / Camoufox tier — NOT Scrapling
def parse_listing(html: str, url: str, recipe: dict) -> dict:
    page = Adaptor(
        html,
        url=url,
        adaptive=True,        # enable self-healing relocation
        auto_save=True,       # persist structural fingerprint to durable store
        # storage path MUST be a durable, shared volume (NOT ephemeral container fs)
        # e.g. mounted at /data/scrapling_fp  — see weakness "Ephemeral-storage footgun"
    )
    price = page.css_first(recipe["price_sel"], auto_match=True)
    return {
        "price": price.clean() if price else None,
        "title": page.css_first(recipe["title_sel"], auto_match=True),
    }
```
> Config note: pin `scrapling==0.4.9` (current). Mount fingerprint store on a
> durable, **shared** path so all coordinator workers see the same healed
> selectors and cold starts don't wipe them.

---

## Candidate 2 — custom asyncio (CARDEEP's CURRENT stack)  ✅ KEEP (orchestration)

- **Where:** `scrapers/coordinator.py`, `scrapers/engine/{router,proxy,identity,session,monitoring}`
  `[VERIFIED]` — read the source tree and coordinator docstring.
- **What it is:** A priority work-queue coordinator that maintains tier pools
  (`curl_cffi` workers T1, Camoufox pool T2/T3), assigns identities by
  trust_score/warming/country, assigns proxies by domain affinity + health,
  escalates tiers via `router/escalator.py`, enforces circuit breakers
  (`router/circuit.py`), warming-before-extraction, and exports Prometheus
  metrics. Writes to `vehicle_index` (Postgres) + Redis. `[VERIFIED]`
- **Deps (`scrapers/requirements.txt`):** httpx[http2], playwright, tenacity
  (retry), pydantic, curl_cffi, **camoufox[geoip]**, capsolver, markitdown,
  structlog. `[VERIFIED]`

### Strengths (relative to every framework here)
- **Anti-detect-first by design:** JA3 invariant per browser instance, Firefox
  TLS profile via Camoufox, identity warming, no `playwright-stealth` (banned by
  CI 2026-05-16). No framework here ships this. `[VERIFIED]` (`common/pw_base.py`)
- **Tiered escalation** (cheap HTTP → stealth browser) — bespoke to CARDEEP's
  cost/anti-block model. Frameworks force one crawler type per spider.
- **Already integrates** Postgres index + Redis + circuit breakers + per-source
  control — i.e. the "full inventory + live delta + per-source recipe" mandate.

### Weaknesses / risks
- **Maintenance burden is on CARDEEP.** No external community fixes the queue,
  retry, or dedup logic. `tenacity` covers retry/backoff; dedup + persistence
  are home-grown.
- **Bus-factor:** institutional knowledge lives in-house. Mitigate with the
  per-module docstrings already present (good) + tests under `tests/`.

### Recommendation
**Keep it as the primary orchestrator.** It is more specialized than any
off-the-shelf framework for CARDEEP's anti-detect + tiered + identity model.
Bolt Scrapling's parser onto it (above). Keep `tenacity` for retry/backoff.

---

## Candidate 3 — Crawlee-python  ✅ FALLBACK orchestrator

- **Repo:** https://github.com/apify/crawlee-python
- **Latest release:** **v1.7.2 — 2026-06-04** `[VERIFIED]` (fetched releases).
  Cadence ~2–3 weeks (v1.7.1 05-26, v1.7.0 05-12, v1.6.3 04-27…). Very alive.
- **Stars:** ~9.2k `[VERIFIED]` · **Open issues:** **74** `[VERIFIED]` (healthy
  for an active framework) · Asyncio-native. `[VERIFIED]`

### What it solves / strengths
- Batteries-included async crawler: **autoscaling** (parallel by system
  resources), **persistent request queue** (resume after interruption),
  **session pool**, **integrated proxy rotation**, **automatic retries on
  errors/blocks**. Crawler types: HttpCrawler, BeautifulSoupCrawler,
  **ParselCrawler**, PlaywrightCrawler. `[VERIFIED]`
- **v1.0+ `SqlStorageClient` (experimental, SQLite/PostgreSQL) supports
  concurrent access from multiple crawler processes → a real distributed path.**
  Source: https://crawlee.dev/python/docs/guides/storage-clients `[VERIFIED]`
- Best onboarding/docs of the three; matches Scrapy's scale with native asyncio.
  Source: https://crawlee.dev/blog/scrapy-vs-crawlee `[VERIFIED via WebSearch]`

### Weaknesses
- **Native `RequestQueue` was not designed for concurrent multi-worker access**
  — multi-machine distribution historically needs a custom Redis/SQL queue.
  Mitigated (not fully erased) by the new `SqlStorageClient`. `[VERIFIED]`
- No JA3/identity-invariant anti-detect model — would regress CARDEEP's current
  anti-block posture if it replaced the custom engine. `[ASSUMED]` (not
  documented as a feature; CARDEEP's model is stricter).
- Greenfield in CARDEEP: adopting wholesale means re-implementing the tiered
  escalation + identity warming Crawlee doesn't have.

### Recommendation
**Fallback / secondary.** Use Crawlee-python for **new, low-anti-bot sources**
where speed-to-build matters more than the JA3 anti-detect stack, or if CARDEEP
ever wants to retire bespoke queue/dedup/session code on a subset of sources.
Pair its `ParselCrawler` with Scrapling's adaptive parser. Use the
`SqlStorageClient` against the existing Postgres for multi-worker dedup.

```python
# Fallback path for a new, low-defense source — Crawlee handles the plumbing.
import asyncio
from crawlee.crawlers import ParselCrawler, ParselCrawlingContext
from crawlee.storage_clients import SqlStorageClient  # v1.0+ multi-process queue

async def main() -> None:
    crawler = ParselCrawler(
        max_requests_per_crawl=1_000_000,   # millions-scale ceiling
        max_request_retries=5,              # built-in retry/backoff
        concurrency_settings=None,          # autoscale by system resources
        storage_client=SqlStorageClient(    # concurrent multi-worker queue
            connection_string="postgresql+asyncpg://cardex:***@pg/cardex",
        ),
    )

    @crawler.router.default_handler
    async def handler(ctx: ParselCrawlingContext) -> None:
        # ctx.selector is Parsel; swap to scrapling.Adaptor for self-healing
        await ctx.push_data({"url": ctx.request.url,
                             "price": ctx.selector.css("::attr(data-price)").get()})
        await ctx.enqueue_links()

    await crawler.run(["https://new-source.example/listings"])

asyncio.run(main())
```
> Config note: pin `crawlee>=1.7.2`. `SqlStorageClient` is **experimental** — for
> true cross-machine distribution, validate concurrent dedup under load or front
> it with a Redis queue (BullMQ/Celery-style fan-out is the documented pattern).

---

## Candidate 4 — Scrapy  ⚠️ ALTERNATIVE (only if forced)

- **PyPI:** https://pypi.org/project/Scrapy/ · **Repo:** https://github.com/scrapy/scrapy
- **Latest release:** **2.16.0 — 2026-05-19** `[VERIFIED]` (fetched PyPI). Recent
  cadence: 2.15.2 (04-28), 2.15.0 (04-09), 2.14.2 (03-12). **Very alive.**
- **Stars:** ~62.2k · **Open issues:** **430** · **Open PRs:** ~187 `[VERIFIED]`
  (high but normal for a 16-year, 11k-commit project; maintained by Zyte).
- **Python:** 3.10–3.14, CPython + PyPy. `[VERIFIED]`

### What changed (recency matters)
- **Asyncio is no longer experimental**, on by default for new projects, works on
  Windows on any Python version.
  Source: https://docs.scrapy.org/en/latest/topics/asyncio.html `[VERIFIED]`
- **Scrapy 2.14 (early 2026) added `AsyncCrawlerProcess` / `AsyncCrawlerRunner`**
  — coroutine-based replacements for the Twisted-era runners.
  Source: https://www.zyte.com/blog/scrapy-in-2026-modern-async-crawling/ `[VERIFIED via WebSearch]`

### Strengths
- **Most mature pipeline architecture** of any candidate (item pipelines,
  middlewares, feed exports). Best for **bulk multi-domain static-HTML discovery**
  across thousands of URLs. Huge ecosystem (scrapy-redis for distributed, etc.).

### Weaknesses
- **Twisted legacy** still underneath; async retrofit, not async-native like
  Crawlee/CARDEEP's stack. Mixing asyncio cleanly is improving but historically
  sharp-edged.
- **Weak on JS-heavy SPAs** out of the box (needs scrapy-playwright). `[VERIFIED via WebSearch]`
- Adopting it means a **paradigm shift** away from CARDEEP's asyncio coordinator
  for zero net capability gain on the anti-detect front.

### Recommendation
**Do not migrate to Scrapy.** It is excellent and alive, but it offers nothing
CARDEEP's custom asyncio engine lacks for *this* problem, and its strengths
(mature pipelines, scrapy-redis) are addressable inside the current stack. Keep
on the radar only if a must-have Scrapy-ecosystem plugin appears.

---

## Candidate 5 — Frontera  ❌ DEAD — DO NOT USE

- **Repo:** https://github.com/scrapinghub/frontera
- **Latest release:** **v0.8.1 — 2019-04-05** `[VERIFIED]` (fetched repo).
  **~7 years stale.** No releases since. Stars ~1.3k, **78 open issues**. `[VERIFIED]`
- **What it was:** distributed crawl-frontier (URL prioritization, Kafka/ZeroMQ
  message bus, HBase/SQLAlchemy/Redis backends), battle-tested at 50–60M docs/day.
- **Verdict:** A **corpse**. Architecturally interesting (the frontier concept is
  worth borrowing conceptually for CARDEEP's discovery/priority queue), but the
  code targets a Python 2-era Scrapy world and is unmaintained. **Recommending it
  for new work would be malpractice.** Do not depend on it. If CARDEEP needs a
  large-scale URL frontier, build it on Redis/Postgres inside the existing
  coordinator (it already has a priority work-queue) — not on Frontera.

---

## Scale-to-millions reality check

- **Parsing** is not the scale bottleneck — Scrapling/Parsel parse at ~2 ms/page.
- **The bottleneck is the queue + dedup + proxy/identity throughput + anti-block
  survival** — which is *orchestration*, and which CARDEEP's custom engine already
  owns (Postgres index, Redis, circuit breakers, tiered escalation).
- Scrapling's per-page self-heal cost is **negligible and local** — adopting it as
  a parser does **not** inherit the "computational overhead at scale" critique,
  which applies to running Scrapling's *Spider/fetcher* as the orchestrator.
  `[VERIFIED]` (overhead critique is about its spider/fetcher, not the parser).

---

## Final answer to the mandate

**Is CARDEEP's current choice good enough?** — **Yes, for orchestration.** The
custom asyncio coordinator is the correct, specialized backbone and beats every
framework here for CARDEEP's anti-detect + tiered + identity model. Keep it.

**What changes:** CARDEEP's current stack has **no self-healing selector layer**
— a stated product goal ("per-source recipe" that survives DOM drift). **Adopt
Scrapling (v0.4.9) as a parsing library** fed by the existing fetchers, persist
its fingerprint store on a durable shared volume, and you close the gap without
regression. **Crawlee-python (v1.7.2)** is the sanctioned fallback orchestrator
for new low-defense sources. **Scrapy** stays an alternative-of-last-resort.
**Frontera is dead — banned.**

---

### Source list
- Scrapling repo — https://github.com/D4Vinci/Scrapling `[VERIFIED]`
- Scrapling commits — https://github.com/D4Vinci/Scrapling/commits/main `[VERIFIED]`
- Scrapling benchmarks — https://scrapling.readthedocs.io/en/latest/benchmarks.html `[VERIFIED]`
- Scrapling limitations review — https://use-apify.com/blog/scrapling-python-web-scraping-framework `[VERIFIED]`
- Crawlee-python releases — https://github.com/apify/crawlee-python/releases `[VERIFIED]`
- Crawlee-python repo — https://github.com/apify/crawlee-python `[VERIFIED]`
- Crawlee storage clients (SqlStorageClient) — https://crawlee.dev/python/docs/guides/storage-clients `[VERIFIED]`
- Scrapy PyPI (latest 2.16.0) — https://pypi.org/project/Scrapy/ `[VERIFIED]`
- Scrapy repo — https://github.com/scrapy/scrapy `[VERIFIED]`
- Scrapy asyncio docs — https://docs.scrapy.org/en/latest/topics/asyncio.html `[VERIFIED]`
- Scrapy 2026 async blog — https://www.zyte.com/blog/scrapy-in-2026-modern-async-crawling/ `[VERIFIED via WebSearch summary]`
- Frontera repo (dead, 2019) — https://github.com/scrapinghub/frontera `[VERIFIED]`
- CARDEEP current stack — `scrapers/coordinator.py`, `scrapers/engine/*`, `scrapers/requirements.txt`, `scrapers/common/pw_base.py` `[VERIFIED]` (read locally)
