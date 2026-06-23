# Servicio / API — the single live, sealed, sub-50ms surface that serves the entire Spanish digital car-sales-point census

> This domain owns the FastAPI application (`services/api/`, port 8090) that is the **only** way any consumer (frontend, partner, auditor) reads the living national census. It owns the read contract: the `{ok,data,error,meta}` envelope, authentication, rate-limiting, caching, pagination, the precompute layer that makes coverage counts O(1), and — going forward — fuzzy entity search and a hierarchical geographic browse path. It does NOT own how data is discovered, identified, geo-coded, or quality-gated; it owns how that finished truth is **served, fast, sealed, and honest**. Its mandate is digital-footprint only: it serves what exists online about every sales point, indexed and located, faster and more completely than any human or rival could assemble.

## Current state (verified)

All figures verified by reading source in `C:\Users\elias\projects\cardeep` (live repo, remote `github.com/sublimine/Cardeep.git`, HEAD `81de58e` 2026-06-23) and the RECON DB snapshot.

**Application shape**
- FastAPI `0.2.0`, asyncpg, uvicorn single-worker, port 8090. Entry: `services/api/main.py`. [VERIFIED]
- Pool: `asyncpg.create_pool(DSN, min_size=1, max_size=8, init=_init_connection)` — `main.py:107`. The init codec deserializes `jsonb`/`json` to Python objects (fixes `vehicle_event.old_value/new_value` rendering). [VERIFIED]
- **18 GET endpoints** (RECON said 19; recount of `@router.get` = ops 4, entities 4, geo 6, vehicles 2, platforms 2 = **18**). All GET-only; CORS `allow_methods=["GET","OPTIONS"]`, origins default to localhost Vite 5173/4173, env-overridable via `CARDEEP_CORS_ORIGINS`. [VERIFIED]
- Routers: `ops.py` (`/health` unauth, `/stats` authed, `/alerts`, `/sources`), `entities.py` (`/canonical`, `/{cdp}`, `/{cdp}/inventory`, `/{cdp}/delta`), `geo.py` (`/completeness`, `/seal`, `/exhaustiveness`, `/{prov}/entities`, `/{prov}/municipalities/{m}/entities`, `/{prov}/tree`), `vehicles.py` (`/{ulid}`, `/{ulid}/history`), `platforms.py` (`/{cdp}/inventory`, `/{ulid}/platforms`). [VERIFIED]

**Auth / limits / cache**
- `require_api_key` (`deps.py:32`): dev/test (no `CARDEEP_ENV`) → public; prod without `CARDEEP_API_KEY` → fail-closed 503; key set → `X-API-Key` enforced. Applied to all data endpoints; NOT `/health`. [VERIFIED]
- Rate-limit (`ratelimit.py`): slowapi `memory://`, per-IP. `RATE_HEALTH=300/min`, `RATE_DEFAULT=120/min`, `RATE_EXPENSIVE=30/min`. **Limits are read once at import** (documented audit note `E-ratelimit`): toggling `CARDEEP_API_RATELIMIT_ENABLED` needs a process restart. Custom 429 returns the project envelope. [VERIFIED]
- Cache (`cache.py`): `cachetools.TTLCache(maxsize=512, ttl=60)`, in-process. Cacheable prefixes: `/geo/`, `/entities/`, `/platforms/`. Excluded: `/health`, `/alerts`, `/sources`. **`/stats` is NOT covered by this cache** (path doesn't match a prefix); it has its own precompute path. Cache key has **no auth/tenant dimension** (documented audit note `E-cache-key`) — safe only under one shared key. [VERIFIED]

**The /stats precompute — RECON CORRECTION**
- RECON claims `scripts/refresh_product_stats.py` is "NOT registered in apscheduler_jobs (manual only)". **This is false.** It IS registered: `pipeline/ops/scheduler.py:854` `_refresh_product_stats_job()` and `:1049` `scheduler.add_job(..., id="product_stats_refresh", ...)`, cadence `CARDEEP_STATS_REFRESH_MIN` default **30 min** (`scheduler.py:851`). It is best-effort (a failed refresh never kills the scheduler; `/stats` falls back to live `compute_counts`). The last `computed_at` 2026-06-23T12:33:47Z is consistent with scheduled refresh, not manual. [VERIFIED — corrects RECON]
- `/stats` (`ops.py:49`): reads `product_stats WHERE id=1` (O(1)); on `UndefinedTableError` falls back to `compute_counts` (the ~83s path). `stats.py` is the single source of the 5 queries, FastAPI-free so the scheduler/script imports it cheaply. [VERIFIED]

**Search / geo infrastructure already present but UNUSED by the API**
- `pg_trgm` + `btree_gin` extensions installed (`migrations/0005`). GIN trigram indexes EXIST: `idx_entity_tradename_trgm` and `idx_entity_legalname_trgm` on `entity` (`migrations/0006:62-63`), `idx_org_name_trgm` on `organization` (`migrations/0007:18`). **No `/search` endpoint exposes them** (`grep` for search in routers = empty). This is the single largest leverage gap. [VERIFIED]
- **No PostGIS, no lat/lon/geometry columns** anywhere (`grep latitude|longitude|geom|ST_` in migrations = empty; `entity` has only `province_code`/`municipality_code`/`comarca_id`). Geography is administrative-code based, not coordinate-based. Map/tile candidates from RESEARCH (Martin, PostGIS GiST) are **not applicable without an upstream geocoding decision in the `geo` domain** — out of scope here until coordinates exist. [VERIFIED]
- No materialized views; `product_stats` is a hand-rolled single-row table (`migrations/0055`); `v_province_seal`, `v_exhaustiveness_seal`, `v_dealer_resolved`, `v_canonical_vehicle`, `servable_entity`, `servable_vehicle` are plain (non-materialized) views. `migrations/0056_v_servable_dealer.sql` adds `v_servable_dealer` as the single canonical "sales point" definition (directory ~36.3k / with-inventory ~18.3k) but stats.py/geo.py do not yet all read from it. [VERIFIED]
- Latest migration: `0056`. [VERIFIED]

**Scale served (RECON DB snapshot, accepted as [ASUMIDO] — not re-queried live)**
- dealers (product_stats) 19,144 · vehicles_unique_available 1,841,679 · servable_vehicle 2,257,001 · platform_listing 2,176,386 · servable_entity 450,619 · vehicle_event 2,761,820 · provinces 52 · municipalities 8,132 · active alerts 53 · source_health healthy 50 / degraded 5 / unknown 1.

**Tests:** 7 API test files (`tests/test_api_*.py`): auth, canonical, exhaustiveness, gaps, pagination, ratelimit_cache, seal. [VERIFIED file list]

**Dependencies (`requirements.txt`):** `asyncpg>=0.29,<0.31`, `fastapi>=0.110`, `uvicorn[standard]>=0.29`, `slowapi>=0.1.9`, `cachetools>=5.3,<6`. [VERIFIED]

**Dev/dry-run ports:** default DSN `:5433` (dev `cardeep-pg`). `docker-compose.yml` reproduces `:5433` (localhost-only). **Any data-affecting validation in this plan runs against a throwaway `:5434` container, never `:5433` without dry-run+golden+Ferrari+CI.** [VERIFIED compose]

## Next-level objective

Make the API the surface that proves CARDEEP has no peer: **every one of the 450k+ entities findable by typo-tolerant name search in <50ms p95**, **every coverage number served in <10ms from a precomputed layer that the consumer can trust by reading its `computed_at`**, **a clean country→province→municipality→dealer→inventory browse path with no dead ends**, and **a self-describing, versioned, machine-readable contract** so a partner or auditor can consume the whole census without a human in the loop. Concretely and measurably:
1. `/search?q=` over entity names: typo-tolerant (`Renaul`→`Renault`), p95 < 50ms, backed by the **already-installed** trigram indexes (EUR0, zero new infra).
2. `/stats` and `/geo/completeness` p95 < 10ms (precompute already half-built; finish + harden + observability).
3. Keyset (cursor) pagination on the unbounded endpoints so deep pages stay O(log n) instead of OFFSET O(n).
4. A published, versioned OpenAPI contract + ETag/`304` conditional GET so consumers cache correctly and never re-download unchanged coverage.

## Chosen technology (EUR0)

Every choice is already in-tree or a single pure-Python dependency. No new service, no Redis, no Meilisearch, no tile server — those from RESEARCH are **deliberately rejected for this phase** because the leverage is already on disk and adding a daemon violates the EUR0/zero-infra posture for a single-host deployment.

| Need | Chosen | Why (vs RESEARCH alternative) | Source / in-tree proof | Integration effort |
|---|---|---|---|---|
| Fuzzy entity search | **PostgreSQL `pg_trgm` GIN** (`%` similarity / `word_similarity`) | RESEARCH proposed Meilisearch (58k★) — rejected: it's a second daemon + index sync + RAM/disk for 450k rows when the **GIN trigram indexes already exist** (`migrations/0006:62`). pg_trgm gives `Renaul→Renault` typo tolerance natively; zero new infra; one new endpoint. | `migrations/0005:6`, `0006:62-63`; https://www.postgresql.org/docs/current/pgtrgm.html | Low — 1 endpoint + tuning `pg_trgm.similarity_threshold`, possibly 1 additive migration for a combined `coalesce(trade_name,legal_name)` index. |
| Coverage precompute | **Single-row `product_stats` table + scheduled refresh** (already live) + extend to `geo/completeness` | RESEARCH proposed `MATERIALIZED VIEW … REFRESH CONCURRENTLY`. Viable and EUR0, but `product_stats` pattern is already proven and the scheduler hook already exists. Adopt MV **only** for `/geo/completeness` (7 sequential COUNTs) where a `REFRESH CONCURRENTLY` MV is cleaner than another bespoke table. | `migrations/0055`, `scheduler.py:1049`; https://www.postgresql.org/docs/current/rules-materializedviews.html | Low — 1 MV migration + 1 scheduler job reusing the existing `_refresh_*_job` pattern. |
| Deep pagination | **Keyset/cursor pagination** (native SQL, no dep) | RESEARCH endorses keyset over OFFSET. Endpoints already over-fetch `size+1` (`page_slice`, `deps.py:60`) so the contract is half-keyset already; finish it with `WHERE (sort_key, ulid) > (cursor)`. | `deps.py:60`; standard SQL | Medium — additive `cursor` param alongside existing `page`/`size` (backward-compatible). |
| HTTP caching | **ETag + `If-None-Match` → 304** (Starlette/FastAPI native) | RESEARCH proposed `fastapi-cache2`+Valkey. Rejected: another daemon. ETag is computed from the body we already build; 304 saves bandwidth with zero infra and composes with the existing in-process TTLCache. | FastAPI/Starlette `Response`/`Request.headers`; RFC 7232 | Low — 1 small helper in `cache.py`. |
| Contract publication | **FastAPI built-in OpenAPI** + explicit `summary`/`response_model` + `/docs` gating | Already emitted by FastAPI; just enrich + version it. | FastAPI native (`/openapi.json`) | Low. |

Rejected for this phase (documented so a cold-start agent doesn't re-litigate): Meilisearch/Typesense, Valkey/Redis, Martin tile server, MapLibre, PgBouncer (single-worker + pool max 8 doesn't yet need it; revisit if multi-worker). PostGIS is **blocked on the `geo` domain** producing coordinates — not a serving decision.

## Target architecture

```
                         consumers (web frontend, partners, auditors)
                                        │  X-API-Key, If-None-Match
                                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  FastAPI :8090  (single uvicorn worker)                    │
        │   middleware: CORS(GET,OPTIONS) → SlowAPI(memory://)       │
        │   per-request: require_api_key  → ETag/304 → TTLCache(60s) │
        │   routers: ops · entities · geo · vehicles · platforms ·   │
        │            **search (NEW)**                                │
        └───────────────┬────────────────────────────────────────────┘
                        │ asyncpg pool (min1,max8, jsonb codec)
                        ▼
        ┌──────────────────────────────────────────────────────────┐
        │  PostgreSQL :5433 (prod-equivalent)                        │
        │   read views: servable_entity/_vehicle, v_dealer_resolved, │
        │               v_canonical_vehicle, v_servable_dealer,      │
        │               v_province_seal, v_exhaustiveness_seal       │
        │   precompute: product_stats (table) + **mv_geo_completeness│
        │               (NEW MV, REFRESH CONCURRENTLY)**             │
        │   search idx: idx_entity_tradename_trgm / legalname_trgm   │
        │               (+ NEW combined-name GIN if needed)          │
        └───────────────▲────────────────────────────────────────────┘
                        │ off-request cadence (best-effort, never blocks readers)
        ┌───────────────┴────────────────────────────────────────────┐
        │  apscheduler (pipeline/ops/scheduler.py, single-producer)   │
        │   product_stats_refresh (30m) · **mv_geo_refresh (30m NEW)**│
        └────────────────────────────────────────────────────────────┘
```

Data-flow contract (unchanged where it works): every response is `{ok,data,error,meta}`; `meta.cache∈{hit,miss}`; paginated `meta` carries `{page,size,returned,has_more}` and (new) `{cursor,next_cursor}`; precomputed responses carry `computed_at` + `source∈{precomputed,live}`.

## Execution phases

Each phase ≈ 1 PR, additive and reversible, branched from `main` as `feature/<descriptor>`. Tests run with `CARDEEP_API_RATELIMIT_ENABLED=0`. Data-affecting SQL is validated on a **throwaway `:5434` docker container** (`docker run --rm -e POSTGRES_... -p 127.0.0.1:5434:5432 postgres:16`), migrations applied there, never on `:5433` without the full golden+Ferrari+CI gate.

---

### Phase 1 — `/search` endpoint over the existing trigram indexes

**Cold-start context.** The DB already has `pg_trgm` + GIN indexes on `entity.trade_name` and `entity.legal_name` (`migrations/0006:62-63`) but no endpoint uses them. This phase exposes typo-tolerant entity search — the single highest-leverage, lowest-cost win. New router file `services/api/routers/search.py`, registered in `main.py` after `platforms`.

**Tasks.**
1. Create `services/api/routers/search.py` with `GET /search` accepting `q: str (min_length 2)`, `province: str|None`, `kind: str|None`, `page`/`size`. Query `v_servable_dealer` joined to `entity`, ranking by `GREATEST(word_similarity(q, trade_name), word_similarity(q, legal_name))`, filtered `WHERE (trade_name %% q OR legal_name %% q)` to hit the GIN index, `ORDER BY rank DESC, resolved_cdp_code`, `DISTINCT ON (resolved_cdp_code)`. Return canonical cdp only (consistent with `/geo/{prov}/entities`).
2. Decorate `@limiter.limit(RATE_EXPENSIVE)` (trigram scan is heavy) and route through the existing TTLCache by adding `/search` is **not** auto-cacheable today — extend `CACHEABLE_PATH_PREFIXES` in `cache.py` with `"/search"` (additive, documented).
3. Set `pg_trgm.similarity_threshold` per-session via `SET LOCAL` (or use explicit `word_similarity` threshold in WHERE) so tuning is in-code, not global server config.
4. Register router in `main.py`; add `summary=`/docstring; `Depends(require_api_key)`.
5. Tests: new `tests/test_api_search.py` — exact match, typo (`Renaul`), province filter, empty `q` 422, pagination, cache hit/miss, envelope shape. Seed minimal fixture rows on `:5434`.

**Verification.**
```bash
# throwaway DB, apply schema, seed, run targeted tests
CARDEEP_API_RATELIMIT_ENABLED=0 CARDEEP_DSN=postgres://...:5434/... \
  python -m pytest tests/test_api_search.py -q
# live smoke (read-only) against :5433
curl -s 'http://127.0.0.1:8090/search?q=Renaul&size=5' | python -m json.tool | head
# index is actually used (no seq scan on 450k rows):
psql -p 5434 -c "EXPLAIN (ANALYZE,BUFFERS) SELECT ... WHERE trade_name %% 'renaul' ..."  # expect Bitmap Index Scan on idx_entity_tradename_trgm
```
**Exit criteria.** `/search?q=Renaul` returns Renault dealers; `EXPLAIN` shows the GIN index (no seq scan); p95 < 50ms on the seeded set; new tests green; existing 7 API test files still green; envelope `{ok,data,error,meta}` with `meta.cache` and pagination intact.

**Rollback.** Pure addition: revert the commit (delete `search.py`, unregister in `main.py`, revert `cache.py` prefix line). No schema change, nothing to undo in DB.

---

### Phase 2 — Materialize `/geo/completeness` + honest `computed_at`

**Cold-start context.** `/geo/completeness` (`geo.py:32`) runs **7 sequential COUNT(*)** over full `entity`+`vehicle` tables on every cache miss. Make it O(1) like `/stats`, using a `REFRESH CONCURRENTLY` materialized view fed by the existing scheduler pattern (`_refresh_product_stats_job`, `scheduler.py:854`).

**Tasks.**
1. Migration `migrations/0057_mv_geo_completeness.sql`: `CREATE MATERIALIZED VIEW mv_geo_completeness AS <the 7 counts as one row>` + `CREATE UNIQUE INDEX` on a constant key (required for `REFRESH CONCURRENTLY`). Include `computed_at timestamptz` via a wrapping table or a `now()`-stamped refresh function. (If MV cannot carry `now()` cleanly, mirror the `product_stats` single-row-table pattern instead — decide on `:5434` by trying both.)
2. `geo.py` `geo_completeness`: read the MV/table first (O(1)), fall back to the live 7-count path on `UndefinedTableError` (symmetry with `/stats`), add `source` + `computed_at` to `meta`.
3. Scheduler: add `mv_geo_refresh` job mirroring `product_stats_refresh` (same cadence env var or a new `CARDEEP_GEO_REFRESH_MIN`, default 30), best-effort, never blocks.
4. Tests: extend `tests/test_api_gaps.py` (or new `test_api_completeness.py`) — precomputed path returns same numbers as live fallback; `source` field present.

**Verification.**
```bash
# on :5434: apply 0057, REFRESH, assert MV row == live 7-count result
psql -p 5434 -f migrations/0057_mv_geo_completeness.sql
psql -p 5434 -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_geo_completeness;"
CARDEEP_DSN=...:5434 python -m pytest tests/test_api_completeness.py -q
curl -s http://127.0.0.1:8090/geo/completeness | python -c "import sys,json;d=json.load(sys.stdin);print(d['meta'])"  # expect source+computed_at
```
**Exit criteria.** Precomputed `/geo/completeness` numbers byte-match the live fallback; p95 < 10ms warm; `source`/`computed_at` exposed; scheduler job registered and logging a success line; migration reversible (`DROP MATERIALIZED VIEW IF EXISTS`).

**Rollback.** Revert handler to live-only path (commit revert) and `DROP MATERIALIZED VIEW mv_geo_completeness;` on the target DB (down-migration shipped in the same PR). No served-row data is mutated — only a derived cache is dropped.

---

### Phase 3 — ETag / conditional GET (304) on cached read endpoints

**Cold-start context.** Consumers re-download identical coverage payloads every TTL window. Add `ETag` (hash of body) + honor `If-None-Match` → `304 Not Modified` with empty body. Composes with the in-process TTLCache (`cache.py`), zero new infra.

**Tasks.**
1. In `cache.py`, compute `etag = '"' + sha256(canonical_json(payload)).hexdigest()[:32] + '"'` when storing/serving cacheable responses; set the `ETag` response header.
2. New helper `conditional_304(request, etag) -> JSONResponse|None`: if `request.headers.get('if-none-match') == etag`, return `JSONResponse(status_code=304, content=None)` with the `ETag` header and no body.
3. Wire into the cacheable read paths (the `try_cache_get`/`cache_set` flow) so it's automatic for `/geo/`, `/entities/`, `/platforms/`, `/search` — no per-router changes.
4. Tests: extend `tests/test_api_ratelimit_cache.py` — first GET returns 200 + `ETag`; second GET with `If-None-Match` returns 304 + empty body + same `ETag`; a TTL-expired/changed body returns a new `ETag` + 200.

**Verification.**
```bash
CARDEEP_API_RATELIMIT_ENABLED=0 python -m pytest tests/test_api_ratelimit_cache.py -q
etag=$(curl -s -D- -o/dev/null http://127.0.0.1:8090/geo/completeness | tr -d '\r' | awk -F': ' '/^ETag/{print $2}')
curl -s -o/dev/null -w '%{http_code}\n' -H "If-None-Match: $etag" http://127.0.0.1:8090/geo/completeness  # expect 304
```
**Exit criteria.** Matching `If-None-Match` → 304 empty body; non-matching → 200 + fresh body; `ETag` stable across identical payloads; all existing tests green; envelope unchanged on 200 responses.

**Rollback.** Revert the `cache.py` commit; endpoints fall back to always-200. No schema, no data.

---

### Phase 4 — Keyset (cursor) pagination on unbounded endpoints

**Cold-start context.** `/entities/{cdp}/inventory`, `/entities/{cdp}/delta`, `/geo/{prov}/entities`, `/alerts` use `LIMIT size+1 OFFSET (page-1)*size` (`page_slice`, `deps.py:60`). Deep pages are O(n). Add an **additive** `cursor` param (opaque base64 of the last row's sort key) that, when present, replaces OFFSET with `WHERE (sort_key, tiebreak_ulid) > cursor`. `page`/`size` stay valid for backward compatibility.

**Tasks.**
1. Add `encode_cursor`/`decode_cursor` helpers in `deps.py` (base64 JSON of the ordered sort tuple). Validate/strict-fail malformed cursors with 400 (system-boundary input validation).
2. For each target endpoint: if `cursor` present, build the keyset `WHERE` from the existing `ORDER BY` columns (already deterministic with a ulid tiebreak); else keep OFFSET. Emit `meta.next_cursor` (null on last page).
3. Confirm composite indexes back each `ORDER BY`; if a deep-page `EXPLAIN` on `:5434` shows a sort/seq-scan, ship an additive `migrations/0058_*` index (reversible `DROP INDEX`).
4. Tests: extend `tests/test_api_pagination.py` — cursor walk returns the same rows in the same order as page-walk, no overlap/gap, `next_cursor` null on final page, malformed cursor → 400.

**Verification.**
```bash
CARDEEP_API_RATELIMIT_ENABLED=0 CARDEEP_DSN=...:5434 python -m pytest tests/test_api_pagination.py -q
# deep page stays index-driven:
psql -p 5434 -c "EXPLAIN (ANALYZE) SELECT ... WHERE (first_seen,vehicle_ulid) < (...) ORDER BY ... LIMIT 50"  # no full sort of 500k rows
```
**Exit criteria.** Cursor pagination yields identical, gap-free ordering vs page pagination; `EXPLAIN` on a deep cursor page shows index range scan, not a full sort; malformed cursor → 400; `page`/`size` callers unaffected (backward-compatible); all pagination tests green.

**Rollback.** `cursor` is additive; reverting the commit removes the param and restores pure OFFSET behavior. Any added index has a `DROP INDEX` down-migration; dropping it only loses speed, not data.

---

### Phase 5 — Contract hardening: versioned OpenAPI, response models, `/docs` gating, security headers

**Cold-start context.** FastAPI already emits `/openapi.json` but endpoints lack explicit `summary`/`response_model`, and there are no standard security response headers. This makes the surface self-describing for partners/auditors and closes web-security gaps (CSP/HSTS/nosniff) per the project's `web/security.md`.

**Tasks.**
1. Add `summary=` and a typed `EnvelopeModel`/per-endpoint `response_model` (Pydantic) so `/openapi.json` documents the real shape; bump `app.version` and embed it in `meta.api_version` on every response (one place: the `ok()`/`err()` helpers in `deps.py`).
2. Add a small middleware setting `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: DENY`, and (prod) `Strict-Transport-Security`; gate `/docs` + `/redoc` + `/openapi.json` behind `require_api_key` (or disable in prod via `CARDEEP_ENV`) — coverage scale is a competitive signal.
3. Tests: new `tests/test_api_contract.py` — `/openapi.json` lists 19 paths (18 + `/search`); every data response carries `meta.api_version`; security headers present; `/docs` requires auth in prod mode.

**Verification.**
```bash
CARDEEP_API_RATELIMIT_ENABLED=0 python -m pytest tests/test_api_contract.py -q
curl -s http://127.0.0.1:8090/openapi.json | python -c "import sys,json;print(len(json.load(sys.stdin)['paths']))"  # expect 19
curl -s -D- -o/dev/null http://127.0.0.1:8090/geo/completeness | grep -i 'x-content-type-options'
```
**Exit criteria.** `/openapi.json` enumerates all 19 endpoints with summaries + envelope schema; `meta.api_version` on every response; security headers present; `/docs` gated in prod; all prior tests green (no envelope regression).

**Rollback.** Revert the commit; FastAPI returns to default OpenAPI and no extra headers. No data, no schema.

---

### Phase 6 — Full-suite regression + honest sealing audit (no new feature)

**Cold-start context.** Auditor pass over phases 1–5 before declaring the domain advanced. No new feature; this is the §Auditoría final gate.

**Tasks.**
1. Run the entire API test suite (`tests/test_api_*.py` + new) with rate-limit off, then a focused run with `CARDEEP_API_RATELIMIT_ENABLED=1` to confirm 429 envelopes still fire.
2. Adversarial checks: cache key still has no tenant dimension (document it stays single-key, or add tenant dimension if multi-key is now in scope per `trust` domain); confirm `/search` cannot leak `particular` listings (kind filter); confirm precompute fallbacks return EXACT counts not stale silent values.
3. p95 latency capture for `/search`, `/stats`, `/geo/completeness` against `:5434` seeded with realistic row counts; record numbers honestly in the PR body (no maquillaje — if a target is missed, state it).

**Verification.**
```bash
CARDEEP_API_RATELIMIT_ENABLED=0 python -m pytest tests/test_api_*.py -q
CARDEEP_API_RATELIMIT_ENABLED=1 python -m pytest tests/test_api_ratelimit_cache.py -q
```
**Exit criteria.** Full API suite green both modes; measured p95 reported for the three target endpoints with pass/fail against the objective thresholds stated honestly; zero regressions in envelope/pagination/auth; audit notes (`E-cache-key`, `E-ratelimit`) re-verified and still accurate or updated.

**Rollback.** Audit-only; nothing to roll back. If a regression is found, revert the offending feature PR.

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Trigram `/search` does a seq scan on 450k rows (threshold too low / wrong operator) | HIGH | `EXPLAIN ANALYZE` gate in Phase 1 exit criteria; require Bitmap Index Scan on the GIN index before merge; tune `word_similarity` threshold, not global config. |
| Cache key has no tenant dimension; introducing per-tenant keys later leaks bodies cross-tenant | HIGH (latent) | Documented audit note `E-cache-key` carried forward in Phase 6; any multi-key work (owned by `trust`) MUST extend `_cache_key` in the same PR — called out as a dependency. |
| Rate-limit/cache are in-process; a future multi-worker uvicorn breaks both | MEDIUM | Documented in `ratelimit.py`/`cache.py`; this plan keeps single-worker; if `ops` moves to multi-worker, promote to shared store (revisit PgBouncer/Valkey then, not now). |
| MV `REFRESH CONCURRENTLY` requires a unique index and locks briefly | MEDIUM | Validate on `:5434`; ship the unique index in the same migration; refresh is best-effort off-request (never blocks readers), mirroring the proven `product_stats` job. |
| Precompute serves a silently stale number after a failed refresh | MEDIUM | `computed_at` + `source` already exposed on `/stats`; replicate on `/geo/completeness`; consumers can detect staleness; fallback recomputes live. |
| Keyset cursor and OFFSET disagree on ordering at boundaries | MEDIUM | Phase 4 test asserts cursor-walk == page-walk row-for-row; deterministic `ORDER BY (sort_key, ulid)` tiebreak already present. |
| Touching served data on `:5433` by accident | CRITICAL | Hard rule: all data-affecting SQL on throwaway `:5434`; `:5433` only via dry-run+golden+Ferrari+CI; phases 1/3/5 touch no DB at all. |

## Success metrics

| Metric | Baseline (verified) | Target | How measured |
|---|---|---|---|
| Entity name search exists | none (no `/search`) | `/search?q=` live, typo-tolerant | Phase 1 endpoint + `test_api_search.py` |
| `/search` p95 | n/a | < 50 ms | `EXPLAIN ANALYZE` + load on `:5434` (Phase 6) |
| `/geo/completeness` cost | 7 sequential COUNT(*) per miss | < 10 ms warm, O(1) read | MV + `source=precomputed` (Phase 2/6) |
| `/stats` precompute correctly understood & observable | registered 30m job (RECON wrong) + O(1) read | unchanged + `computed_at` surfaced everywhere | re-verify scheduler line `:1049` |
| Deep-page pagination complexity | OFFSET O(n) | cursor O(log n) | `EXPLAIN` deep cursor page index scan (Phase 4) |
| Bandwidth on unchanged reads | full payload every TTL | `304` on `If-None-Match` | Phase 3 curl/test |
| Contract self-description | implicit OpenAPI, no models | 19 paths, typed envelope, `meta.api_version` | `/openapi.json` path count (Phase 5) |
| Test coverage of the surface | 7 API test files | + search, completeness, contract; all green both rate-limit modes | full `pytest tests/test_api_*.py` (Phase 6) |
| New infra / cost | EUR0, single host, in-process | EUR0 maintained (no Redis/Meili/tile server) | dependency diff = pure-Python only |
