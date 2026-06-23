# Extraccion / Scraping — Capture, diff, and freshness-track the complete Spanish digital vehicle footprint, continuously, at EUR0

> This domain owns the **fetch + extract + delta** layer of CARDEEP: the tiered HTTP/browser engine (`pipeline/engine/`), the 42 source connectors (`pipeline/platform/`, 38 `*_wholesale.py` + 4 `*_facet.py`), the resilience stack (fingerprint rotation, ban detection, per-host governor, free-proxy pool, clearance cache, source fallback), the recipe harness (recipe-first / sample-verify-delete per dealer), and the delta engine (`pipeline/delta.py`). Its mandate is the **digital footprint only**: anything a dealer/marketplace publishes on the web is fair game to find, fetch, parse, and re-check; anything with no web presence is out of scope by Owner decree. It feeds normalized vehicle records and change events to `identity`, `vehicle`, and `serving`. It matters because the census *is* what this layer captures — without continuous, resilient, ban-resistant extraction there is no living inventory.

## Current state (verified)

All figures below were verified by reading the repo at `C:\Users\elias\projects\cardeep` on 2026-06-23 unless marked [RECON-DB] (from the supplied DB recon, not re-queried here).

- **Engine present and complete** [VERIFIED]: `pipeline/engine/` contains `fetch.py` (tiered, `_TIER1_ENGINE = "camoufox"` default at line 57, `fetch_text(url, *, tier=0, ...)` at line 399), `ban_detector.py`, `fingerprints.py`, `governor.py`, `proxies.py`, `free_proxies.py` (`fetch_candidates`, `health_check`, `harvest_alive`, `refresh_pool_urls`), `clearance_cache.py`, `source_fallback.py`, `ratelimit_pg.py`, and `tier1/`.
- **Connector count** [VERIFIED]: exactly **38** `*_wholesale.py` + **4** `*_facet.py` in `pipeline/platform/`.
- **Delta engine exists but is NOT wired into wholesale** [VERIFIED]: `pipeline/delta.py` defines `diff_vehicle(old, new)` (line 290, returns `PRICE_CHANGE`/`KM_CHANGE`/`PHOTO_CHANGE` event dicts, no DB I/O) and `reconcile_gone(...)` (line 146). **`grep -l "diff_vehicle" pipeline/platform/*_wholesale.py` returns 0 files**; `grep -rl` across all of `pipeline/platform/` returns nothing. The docstring at delta.py line ~316 explicitly notes the old asymmetric guard "silently dropped that transition across all 26 wholesale connectors" — the helper is hardened but uncalled. [RECON-DB] the 176,018 `PRICE_CHANGE` + 15,042 `KM_CHANGE` rows come exclusively from the AS24 ingest branch (`pipeline/ingest.py`).
- **`g5_check.py` does not exist** [VERIFIED]: `find . -name "*g5*"` returns nothing. [RECON-DB] all 37,657 `entity_completion` rows have `g5_delta=False`.
- **`complete.py` hardcodes ES** [VERIFIED]: lines 305 and 309 of `pipeline/complete.py` glob `countries / "ES"` literally — blocks multi-country gate evaluation.
- **Recipe harness present** [VERIFIED]: `pipeline/recipe_harness.py` implements sample-verify-delete with `Sample`, `Extractor` Protocol, `sample_paths`, `decide_status` (zero-parse-loss + VAM gate). [RECON-DB] 61 YAMLs on disk, 537 entities with `recipe_version`.
- **Sources** [RECON-DB]: 56 in `source_health` (50 healthy, 5 degraded — `autocasion_wholesale`, `wallapop_wholesale`, `miclasico_wholesale`, `family_unreachable`, `family_framework_webbuilder` — 1 unknown `dork_municipal`). 2,257,054 available vehicles; 1,177,851 (52%) seen in 24h; 1,607,468 (71%) seen in 7d. Top volume: wallapop 735k, milanuncios 447k, as24_wholesale 309k, coches_net 271k, as24 222k.
- **Proxies** [RECON-DB + VERIFIED]: `CARDEEP_PROXIES` unset in prod; `proxies.py` pool empty; only `free_proxies.py` active.
- **Scheduler not running as daemon** [RECON-DB]: `scheduler_lease` empty; `pipeline/ops/scheduler.py` (`heartbeat_tick` every 15min, `silence_watchdog` hourly) is not held by a persistent process.
- **Docker** [VERIFIED]: `docker-compose.yml` maps host `127.0.0.1:5433 -> container 5432` as a *prod-faithful* reproduction of `cardeep-pg` (comment lines 3, 24). The doctrine `:5434` dry-run target is a **separate ephemeral container**, never the `:5433` faithful one.

Honest gaps: (1) delta is dead code for 38/42 connectors — 52% of the catalog never emits price/km/photo change events; (2) no daemon means harvesting is manual/intermittent; (3) freshness is decaying (only 52% seen in 24h); (4) G5 (delta-coverage gate) is unimplemented; (5) `complete.py` cannot run for any country but ES; (6) only 2 of 34 measured sources are TRUSTWORTHY (a `trust`/`quality` concern this domain feeds but does not own).

## Next-level objective

**Every connector emits delta events, and the fleet runs unattended.** Concretely, measurable:

1. **Delta coverage = 42/42 connectors** import and call `diff_vehicle` + `reconcile_gone` (verifiable by grep count), up from 4/42.
2. **`PRICE_CHANGE`/`KM_CHANGE`/`PHOTO_CHANGE` events originate from ≥ 20 distinct `source_key`s** within 14 days of rollout (today: effectively 1 — AS24), proving the wiring is live, not just present.
3. **24h freshness ≥ 80%** of available vehicles (today 52%) sustained for 7 consecutive days, driven by a persistent scheduler daemon holding `scheduler_lease`.
4. **G5 gate operational**: `pipeline/g5_check.py` exists and sets `entity_completion.g5_delta=True` for entities with ≥ 2 observed harvests and at least one delta-eligible re-check (today 0/37,657).
5. **Zero new EUR spend**: engine stays on `curl_cffi` Tier-0 + `camoufox` Tier-1 + free-proxy pool; residential proxies remain a `trust`/`ops` PENDING-CREDENTIAL gate that never blocks this domain.

This passes any human/IA bar because it is *continuous, self-healing, full-catalog change-detection over the entire national digital footprint* — not a one-shot scrape.

## Chosen technology (EUR0)

The engine is already best-in-class for 2026; the plan **keeps and hardens** it rather than rewriting. Selections, with rationale and source:

| Need | Tool | Why (vs alternatives) | Source | Integration effort |
|---|---|---|---|---|
| Tier-0 HTTP (TLS/JA3/JA4/HTTP2 impersonation) | **curl_cffi** (in use, `fetch.py`) | 26/31 on the 2026 adversarial bench, 0 extra deploys, drop-in `requests` API; already the Tier-0 default | github.com/lexiforest/curl_cffi (MIT) | **Zero** — already wired |
| Tier-0 high-throughput fallback | **primp** (Rust `rquest` binding) | Separates browser vs OS fingerprint (UA↔Client-Hints↔TLS cross-check resistance); 5.2x faster sync; lower RAM for fan-out workers | github.com/deedy5/primp (MIT) | Low — add as a `fetch.py` Tier-0 alternate engine behind a flag |
| Tier-1 browser (default) | **Camoufox** (in use) | Firefox C++ patches (not JS-bypassable), 25/31 bench, BrowserForge device realism; MPL-2.0 keeps us license-clean | github.com/daijro/camoufox (MPL-2.0) | **Zero** — `_TIER1_ENGINE = "camoufox"` |
| Tier-1 hardest targets (opt-in) | **nodriver** (in use, opt-in) | Only tool with 0 blocks on the 2026 bench (28/31); direct CDP, no automation handshake. AGPL → opt-in only, never default | github.com/ultrafunkamsterdam/nodriver (MIT) | **Zero** — opt-in present |
| Structured-data extraction | **extruct** | Captures schema.org/Vehicle JSON-LD, Microdata, RDFa, OpenGraph in one call → VIN/price/km layout-immune; natural fallback to CSS | github.com/scrapinghub/extruct (BSD-3) | Low — add to `recipe_extractors.py` as first-pass extractor |
| Layout-immune extraction for messy dealers | **crawl4ai + Ollama (local)** | LLM-as-selector via Pydantic schema; EUR0 on local CPU/GPU; for the long tail of bespoke dealer sites where CSS selectors rot | github.com/unclecode/crawl4ai (Apache-2.0) | Medium — optional Tier-2 extractor, gated behind a feature flag; **deferred to a later PR**, not on the critical path |
| Distributed scaling (future) | **scrapy-redis + scrapy-impersonate** | Only if single-producer APScheduler becomes the bottleneck; shared Redis queue + per-worker fingerprint. **Not adopted now** — current scheduler is sufficient and adding Redis is non-additive | github.com/rmax/scrapy-redis (BSD), github.com/jxlil/scrapy-impersonate (MIT) | Out of scope this cycle |

Decision: **the critical path uses only tools already in the repo.** `extruct` and `primp` are additive low-risk wins; `crawl4ai`/`ScrapeGraphAI` and the Scrapy-Redis fleet are explicitly deferred (YAGNI until a measured bottleneck appears).

## Target architecture

```
                 scheduler.py (DAEMON, holds scheduler_lease)
                 heartbeat_tick (15m) -> select due sources -> subprocess per source
                          |                                  silence_watchdog (1h)
                          v
   ┌──────────────────────────────────────────────────────────────┐
   │  Connector (pipeline/platform/<src>_wholesale.py)              │
   │   enumerate() -> ingest()                                      │
   │     for each scraped record:                                   │
   │       old = vehicle snapshot (price, km, photo_url) from DB    │
   │       events = delta.diff_vehicle(old, new)   <-- NEW WIRING   │
   │       persist events to vehicle_event                          │
   │     reconcile_gone(declared, harvested)        <-- NEW WIRING  │
   └──────────────────────────────────────────────────────────────┘
                          |  uses
                          v
   engine/fetch.py  ── Tier-0 curl_cffi (primp alt) ─┐
        |             ── Tier-1 camoufox / nodriver  │
        | governor.py (per-host token bucket, ratelimit_pg backend)
        | fingerprints.py (rotate-on-ban)  ban_detector.py (OK/CHALLENGE/BANNED/NOT_FOUND)
        | free_proxies.py (pool) | clearance_cache.py | source_fallback.py
                          |
                          v
   recipe_harness.py (per-dealer sample-verify-delete) -> recipe.yaml under countries/<CC>/recipes/
                          |
                          v
   g5_check.py (NEW) -> entity_completion.g5_delta = True when delta-eligible re-check observed
                          |
                          v
   complete.py (G1-G5, country-parametrized) -> hands off to identity / vehicle / serving
```

Data flow contract: connectors write to `vehicle` (upsert) and `vehicle_event` (append-only delta). `diff_vehicle` is pure (no DB I/O) — connectors own persistence. `reconcile_gone` keeps the existing GONE guard (`harvested >= declared*0.95`). All writes are **additive** to `vehicle_event`; no destructive change to served `vehicle` rows beyond the existing upsert path.

## Execution phases

Each phase is ~1 PR, additive, reversible. **Data-touching verification runs against a throwaway `:5434` dry-run container, never `:5433`** until golden + Ferrari + CI are green per doctrine.

### Phase 0 — Dry-run harness + baseline (no production writes)

**Cold-start context:** Repo root `C:\Users\elias\projects\cardeep`. `docker-compose.yml` maps `:5433` to a prod-faithful PG; you must stand up a *separate* ephemeral PG on `:5434` for all delta experiments. The delta helper (`pipeline/delta.py:290`) is correct but unused by wholesale connectors (grep returns 0).

**Tasks:**
1. Add `docker-compose.dryrun.yml` defining a `cardeep-pg-dryrun` service on host `127.0.0.1:5434:5432`, seeded from the census fixture (reuse `scripts/seed_ci_fixture.py` if present; else snapshot a 10k-vehicle subset).
2. Write `tests/test_delta_wiring.py` (RED): asserts that for a representative connector, scraping a record whose price differs from the DB snapshot produces a `PRICE_CHANGE` row in `vehicle_event`. This test MUST fail today.
3. Capture baseline metrics into `plans/extraction/baseline.json`: per-`source_key` count of `vehicle_event` rows by `event_type`, and 24h/7d freshness percentages.

**Verification:**
```bash
cd /c/Users/elias/projects/cardeep
docker compose -f docker-compose.dryrun.yml up -d        # :5434 only
python -m pytest tests/test_delta_wiring.py -q            # expect RED (fail)
grep -rl "diff_vehicle" pipeline/platform/                # expect: (empty)
```
**Exit criteria:** `:5434` up and seeded; failing wiring test committed; baseline.json written.
**Rollback:** `docker compose -f docker-compose.dryrun.yml down -v`; delete test + json. No prod artifacts touched.

### Phase 1 — Wire delta into a pilot cohort (5 highest-volume connectors)

**Cold-start context:** `diff_vehicle(old: dict, new) -> list[event dict]` expects `old` with optional keys `price`/`km`/`photo_url`; `new` is the scraped dataclass. It is pure. Pilot the 5 top-volume sources: wallapop, milanuncios, as24_wholesale (already partially via ingest — verify no double-count), coches_net, coches_com.

**Tasks:**
1. In each pilot `*_wholesale.py` `ingest` path: fetch the current `vehicle` snapshot, call `diff_vehicle(old, new)`, persist returned events to `vehicle_event` (append-only), and call `reconcile_gone` with declared/harvested counts.
2. Guard against AS24 double-emission: if a connector already emits via the ingest branch, route through one path only (add an idempotency check keyed on `(vehicle_id, event_type, new_value, harvest_run_id)`).
3. Make `tests/test_delta_wiring.py` pass (GREEN) for the pilot connectors; add per-connector unit tests asserting no false-positive events on unchanged records (delta.py guarantees `[]` when nothing changed).

**Verification (dry-run only):**
```bash
python -m pytest tests/test_delta_wiring.py tests/test_delta_no_false_positive.py -q   # GREEN
grep -l "diff_vehicle" pipeline/platform/*_wholesale.py | wc -l                         # expect >= 5
# run pilot connectors against :5434, then:
psql "host=127.0.0.1 port=5434 ..." -c "SELECT source_key, event_type, count(*) FROM vehicle_event GROUP BY 1,2 ORDER BY 1;"
# expect >= 4 NEW distinct source_keys emitting events
```
**Exit criteria:** 5 connectors wired; tests GREEN; ≥ 4 new source_keys emit deltas in `:5434`; no false positives on unchanged rows; no double-count vs AS24.
**Rollback:** `git revert` the PR — connectors fall back to no-delta behavior (the prior production state); `vehicle_event` is append-only so dry-run rows are discarded with the `:5434` container.

### Phase 2 — Roll delta out to the remaining 33 connectors

**Cold-start context:** Phase 1 established the exact wiring pattern. Replicate it across the other 33 `*_wholesale.py` + 4 `*_facet.py`. Extract the wiring into a shared helper (`pipeline/platform/_delta_mixin.py`) to keep DRY and avoid 38 copies.

**Tasks:**
1. Add `pipeline/platform/_delta_mixin.py`: a single function `emit_deltas(conn, vehicle_id, old_snapshot, new_record, harvest_run_id)` that wraps `diff_vehicle` + idempotent persistence.
2. Call it from every connector's ingest path. Use `extruct` (BSD) as the first-pass extractor in `recipe_extractors.py` for any connector whose target exposes schema.org/Vehicle, to make `new_record` field capture layout-immune.
3. Add a guard test `tests/test_all_connectors_wire_delta.py` that greps the platform dir and asserts the count of connectors importing the mixin == 42.

**Verification:**
```bash
python -m pytest tests/test_all_connectors_wire_delta.py -q       # GREEN
grep -rl "_delta_mixin\|diff_vehicle" pipeline/platform/*.py | wc -l   # expect 42
# golden diff + Ferrari suite (per doctrine, before any :5433 touch)
python -m pytest tests/ -q                                         # full local suite green
```
**Exit criteria:** 42/42 connectors wired; full local suite + golden + Ferrari green; CI (unit/collect/frontend/secret) green. Only then is promotion to `:5433` permitted.
**Rollback:** `git revert`; the mixin import is additive so reverting restores the no-delta path connector-by-connector if needed.

### Phase 3 — Implement G5 delta-coverage gate + de-hardcode complete.py

**Cold-start context:** `complete.py` evaluates G1–G4 today; G5 is deferred and `entity_completion.g5_delta` is universally `False`. `complete.py` lines 305/309 hardcode `"ES"`, blocking country #2.

**Tasks:**
1. Create `pipeline/g5_check.py`: for an entity, return `True` when it has ≥ 2 distinct `harvest_run` observations AND at least one delta-eligible re-check (a second fetch of the same vehicle where price/km/photo could have been diffed). Pure function + a DB-backed setter.
2. Integrate G5 into `complete.py`'s gate evaluation and set `entity_completion.g5_delta` accordingly.
3. Parametrize the country: replace the two literal `"ES"` globs (lines 305, 309) with a `country_code` argument threaded from the caller; default `"ES"` to preserve current behavior, but accept any CC.

**Verification:**
```bash
python -m pytest tests/test_g5_check.py tests/test_complete_country_param.py -q   # GREEN
grep -n "\"ES\"\|'ES'" pipeline/complete.py    # expect: no hardcoded literals in the recipe-glob paths
# dry-run on :5434:
psql "...port=5434..." -c "SELECT count(*) FILTER (WHERE g5_delta) FROM entity_completion;"   # expect > 0
```
**Exit criteria:** `g5_check.py` exists; G5 wired into `complete.py`; ES literals removed from glob paths (country-parametrized, ES default preserved); some entities flip `g5_delta=True` in `:5434`; full suite green.
**Rollback:** `git revert`; G5 reverts to deferred, `complete.py` falls back to G1–G4 with ES default.

### Phase 4 — Stand the scheduler up as a persistent daemon (freshness)

**Cold-start context:** `scheduler_lease` is empty; `pipeline/ops/scheduler.py` (`heartbeat_tick` 15m, `silence_watchdog` 1h, jobs in `apscheduler_jobs`) is not held by a long-lived process. 24h freshness is 52%; target ≥ 80%.

**Tasks:**
1. Add a supervised launcher (`ops/run_scheduler.sh` or a systemd/NSSM unit appropriate to the host) that acquires `scheduler_lease`, runs the APScheduler producer as a daemon, and restarts on crash.
2. Add lease-liveness telemetry to `pipeline/ops/health.py` (a `scheduler_alive` heartbeat row) so `ops`/`quality` can alarm if the lease goes stale. **This is the `ops` dependency** — daemon supervision policy is co-owned with `ops`.
3. Tune `harvest_interval_hours` for the top-volume sources downward where ban-budget allows (governor already throttles), to lift 24h freshness.

**Verification:**
```bash
# start daemon (dry-run target first), then:
psql "...port=5434..." -c "SELECT holder, acquired_at FROM scheduler_lease;"   # non-empty, fresh
# after >= 24h of running:
psql -c "SELECT 100.0*count(*) FILTER (WHERE last_seen >= now()-interval '1 day')/count(*) FROM vehicle WHERE status='available';"   # trend toward >= 80
```
**Exit criteria:** daemon holds a fresh `scheduler_lease`; `scheduler_alive` heartbeat visible to health; 24h freshness trending up over a 7-day window toward ≥ 80%.
**Rollback:** stop the daemon / release the lease; system returns to manual/intermittent harvesting (prior state). No data change to revert.

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Delta wiring double-counts vs AS24 ingest branch → inflated `vehicle_event` | HIGH | Idempotency key `(vehicle_id, event_type, new_value, harvest_run_id)`; Phase 1 explicitly audits AS24 path before wiring; dry-run count comparison vs baseline.json |
| Promoting delta to `:5433` corrupts served history | CRITICAL | Append-only `vehicle_event`; full golden + Ferrari + CI gate before any `:5433` write; `:5434` dry-run is mandatory and prod DB is never exposed publicly (compose binds 127.0.0.1) |
| Mass ban as harvest frequency rises (Phase 4) | HIGH | Governor token-bucket + `ban_detector` semantic verdicts + fingerprint rotate-on-ban + `clearance_cache` + `source_fallback`; raise frequency per-source incrementally, watch `source_breaker` |
| Residential proxies unavailable (EUR0 constraint) | MEDIUM | Free-proxy pool (`free_proxies.py`) + Tier-1 browser clearance; residential proxies stay a PENDING-CREDENTIAL `trust`/`ops` gate that never blocks this domain |
| `complete.py` country de-hardcode regresses ES | MEDIUM | `country_code` defaults to `"ES"`; dedicated regression test `test_complete_country_param.py` asserts ES behavior unchanged |
| AGPL contamination via nodriver | LOW | nodriver stays strictly opt-in (never default `_TIER1_ENGINE`); camoufox (MPL-2.0) is the default Tier-1 |
| crawl4ai/Ollama scope creep | LOW | Explicitly deferred; not on critical path; feature-flagged if introduced |

## Success metrics

| Metric | Baseline (verified/RECON) | Target | How measured |
|---|---|---|---|
| Connectors emitting delta | 4/42 (effectively 1: AS24) | **42/42** | `grep -rl "_delta_mixin\|diff_vehicle" pipeline/platform/*.py \| wc -l` |
| Distinct source_keys with delta events | ~1 | **≥ 20 within 14d** | `SELECT count(DISTINCT source_key) FROM vehicle_event` (rolling 14d) |
| 24h freshness | 52% (1,177,851 / 2,257,054) | **≥ 80% sustained 7d** | `count FILTER (last_seen >= now()-'1 day') / total available` |
| `entity_completion.g5_delta=True` | 0 / 37,657 | **> 0, growing** | `SELECT count(*) FILTER (WHERE g5_delta) FROM entity_completion` |
| Scheduler lease held | empty | **fresh, continuous** | `SELECT acquired_at FROM scheduler_lease` + `scheduler_alive` heartbeat |
| Degraded sources | 5 | **≤ 2** | `SELECT count(*) FROM source_health WHERE status='degraded'` |
| New EUR spend | EUR0 | **EUR0** | engine stays curl_cffi + camoufox + free proxies; no paid service wired |
