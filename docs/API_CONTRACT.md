# CARDEEP API CONTRACT — sealed, replicable surface

> Part of the **Replication Bible**. This is the contract another country's
> Cardeep API **must honor byte-for-byte**. Every endpoint, parameter, envelope
> field, schema column, and delta rule below was read from the live code in
> `services/api/` and verified by curling the running server at
> `http://localhost:8090` and querying the live PostgreSQL
> (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`) on **2026-06-23**.
>
> Marking convention: `[VERIFIED]` = read from code AND/OR confirmed against a
> live response/query. `[ASUMIDO]` = inferred, not directly observed. There are
> no `[ASUMIDO]` claims about wire shape in this doc — every response shape shown
> is a real captured body.
>
> The product: a **LIVE census of 100% of a country's DIGITAL car sales points
> (dealers) + their inventory**, served over this API with a queryable **delta**
> (altas / bajas / Δprice / Δkm / Δphoto). Lifecycle: DISCOVER → SCRAPE → RECIPE
> → API → DELTA.

---

## 0. Live ground truth (verified 2026-06-23, cosecha ACTIVA)

Re-run this before trusting any cited number; the harvest appends continuously
(last vehicle `last_seen` was `2026-06-23 01:30:10Z` at capture time), so totals
drift upward minute to minute. **Counts here are live, never pinned in code** —
`/stats` computes them with `COUNT(*)` per request (see §4.13).

```bash
cd /path/to/cardeep
python - <<'PY'
import asyncio, asyncpg, json
DSN='postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep'
async def m():
    c=await asyncpg.connect(DSN)
    print('entity_total              ', await c.fetchval("SELECT count(*) FROM entity"))
    print('entity_non_particular     ', await c.fetchval("SELECT count(*) FROM entity WHERE kind<>'particular'"))
    print('dealers_resolved (stats)  ', await c.fetchval("""SELECT count(DISTINCT vdr.resolved_cdp_code)
        FROM v_dealer_resolved vdr JOIN entity e ON e.entity_ulid=vdr.entity_ulid WHERE e.kind<>'particular'"""))
    print('vehicle_total             ', await c.fetchval("SELECT count(*) FROM vehicle"))
    print('vehicle_available         ', await c.fetchval("SELECT count(*) FROM vehicle WHERE status='available'"))
    print('vehicles_unique_available ', await c.fetchval("""SELECT count(*) FROM v_canonical_vehicle vc
        JOIN servable_vehicle v ON v.vehicle_ulid=vc.vehicle_ulid
        WHERE vc.vehicle_ulid=vc.canonical_vehicle_ulid AND v.status='available'"""))
    print('events_total              ', await c.fetchval("SELECT count(*) FROM vehicle_event"))
    print('events_by_type            ', [dict(r) for r in await c.fetch(
        "SELECT event_type,count(*) FROM vehicle_event GROUP BY event_type ORDER BY 2 DESC")])
    await c.close()
asyncio.run(m())
PY
```

Captured baseline (2026-06-23 ~01:30Z) `[VERIFIED]`:

| Metric | Live value | Source |
|---|---|---|
| `entity` total | **431,212** | direct `COUNT(*)` |
| `entity` non-particular | **91,412** | `kind <> 'particular'` |
| dealers (the `/stats.dealers` formula) | **54,570** | `v_dealer_resolved` ∪ `entity`, non-particular |
| `vehicle` total | **2,312,312** | direct `COUNT(*)` |
| `vehicle` available | **2,207,357** | `status='available'` |
| vehicles unique available (`/stats`) | **1,853,644** | canonical-only + available |
| `vehicle_event` total | **2,613,258** | direct `COUNT(*)` |
| provinces / comarcas / municipalities | **52 / 323 / 8,132** | geo backbone |
| country breakdown | **ES: 431,212** (single tenant) | `GROUP BY country_code` |

`vehicle_event` by type `[VERIFIED]`: `NEW 2,313,354` · `PRICE_CHANGE 125,287`
· `GONE 109,153` · `PHOTO_CHANGE 54,506` · `KM_CHANGE 10,958`.

> **Drift note (anti-hallucination).** `/stats` and `/geo/completeness` returned
> slightly higher figures than the direct queries above during the same session
> (e.g. `/stats.events` = 2,613,437 vs direct 2,613,258; `/geo/completeness
> .vehicles.total` = 2,312,444 vs direct 2,312,312). That is **not a bug** — it is
> the live harvest appending rows between the two reads. The earlier audit's
> "419k vs 431k entity" mismatch is **resolved**: live entity is 431,212 (the
> `0052_country.sql` header's `431,211` was the count at migration-write time;
> it grows with discovery). Treat all coverage numbers as a moving target read
> live, never as constants.

---

## 1. Service shape

| Property | Value | Source |
|---|---|---|
| Framework | FastAPI `0.2.0`, title `Cardeep API` | `main.py:93` |
| Run | `uvicorn services.api.main:app --host 127.0.0.1 --port 8090` | `main.py:6,134` |
| DB pool | asyncpg, `min_size=1 max_size=8`, opened on lifespan startup | `main.py:86` |
| DSN | env `CARDEEP_DSN`, default `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep` | `deps.py:15` |
| Routers | `ops`, `entities`, `geo`, `vehicles`, `platforms` | `main.py:125-129` |
| Methods served | **GET and OPTIONS only** (CORS allow-methods) | `main.py:121` |
| OpenAPI | `GET /openapi.json` (FastAPI default; **unauthenticated**) | live `[VERIFIED]` |

There are **no** POST/PUT/PATCH/DELETE routes. The API is strictly read-only;
all mutation happens in the ingest pipeline, never over HTTP.

---

## 2. Response envelope (universal)

Every response — success, error, 404, 400, 401, 429 — uses the **same envelope**.
Defined once in `deps.py:38-43`.

```jsonc
{
  "ok":    true | false,      // boolean success flag
  "data":  <payload> | null,  // null on every error
  "error": null | "message",  // human string on error, null on success
  "meta":  null | { ... }     // pagination / cache / counts; null when absent
}
```

- Success helper `ok(data, **meta)` → `{ok:true, data, error:null, meta: meta or null}`.
  When no `meta` kwargs are passed, `meta` is `null` (e.g. `/entities/{cdp}`,
  `/vehicles/{ulid}`, `/entities/{cdp}/canonical`) `[VERIFIED]`.
- Error helper `err(message, status=404)` → `{ok:false, data:null, error:message, meta:null}`
  with the given HTTP status `[VERIFIED]` (404 body confirmed live).

**Contract for a replicating country: this envelope is invariant.** Do not add
top-level keys; carry everything extra inside `data` or `meta`.

### 2.1 `meta` sub-fields

| Field | Where | Meaning |
|---|---|---|
| `page` | paginated endpoints | echoed 1-based page |
| `size` | paginated endpoints | echoed page size |
| `returned` | paginated endpoints | rows in this page (`len(data)`) |
| `has_more` | paginated endpoints | `true` iff `returned == size` (see §3) |
| `cache` | cacheable GETs | `"hit"` \| `"miss"` (see §6) |
| `count` | `/sources`, `/vehicles/{ulid}/platforms` | total items in `data` (un-paginated) |
| `province`, `municipality`, `platform`, `cdp_code`, `vehicle_ulid`, `retry_after`, `detail` | various | endpoint-specific echoes |

---

## 3. Pagination contract

Applied to every endpoint that can return unbounded rows
(`main.py:8-19`).

| Param | Type | Default | Bounds | Source |
|---|---|---|---|---|
| `page` | int | `1` | `>= 1` | `Query(default=1, ge=1)` |
| `size` | int | `50` | `1..200` (FastAPI 422 outside range) | `Query(default=50, ge=1, le=200)` |

- `offset = (page - 1) * size`; `LIMIT size OFFSET offset`.
- **`has_more` is heuristic, not a full count.** It is `true` when the DB
  returned exactly `size` rows (there *may* be a next page). A `COUNT(*)` is
  **deliberately avoided** on 500k+ row tables (`main.py:16-19`). A replicating
  country must keep this contract: do not promise an exact total on big tables.
- Endpoints with this contract: `/entities/{cdp}/inventory`,
  `/entities/{cdp}/delta`, `/vehicles/{ulid}/history`, `/platforms/{cdp}/inventory`,
  `/geo/{prov}/entities`, `/geo/{prov}/municipalities/{muni}/entities`, `/alerts`.
- **Un-paginated** (return the full set, `meta.count`): `/sources`,
  `/vehicles/{ulid}/platforms`. Fixed-shape (no pagination): `/health`, `/stats`,
  `/geo/completeness`, `/geo/seal`, `/entities/{cdp}`, `/entities/{cdp}/canonical`,
  `/vehicles/{ulid}`, `/geo/{prov}/tree`.

---

## 4. Endpoint catalogue

Live path list from `GET /openapi.json` `[VERIFIED]` (17 routes at the original
2026-06-23 seal). **Stale as a total** — the surface has grown since via
parallel pillar work not yet folded into this count (AUTH-0's `/auth/*` router,
02-history-reports' `/vehicles/{ulid}/lifetime` below); re-run the
`GET /openapi.json` count before quoting a total. Every data endpoint depends on
`require_api_key` (§5) and carries a rate-limit decorator (§7). Cache
eligibility is §6.

> **Live divergence (must replicate consciously).** `/geo/seal` is in code
> (`geo.py:92`) AND live. `/geo/exhaustiveness` is in code (`geo.py:147`) but the
> **running process returns 404** for it — the deployed binary predates that
> route. It is documented in §4.16 as the contract a fresh deploy must serve; a
> replicating country that ships current code WILL expose it. Restart the service
> to pick it up.

### 4.1 `GET /health` — liveness probe (UNAUTHENTICATED)

`ops.py:25`. The **only** unauthenticated data-bearing endpoint, by contract
(`deps.py:26`, `main.py:34`). One `SELECT 1` round-trip → real liveness.

Exposes **no product counts** (coverage scale is a competitive signal; it was
moved to `/stats` behind auth — audit P2/P1).

Live `[VERIFIED]`:
```json
{"ok":true,"data":{"status":"live","db":"ok"},"error":null,"meta":null}
```
Degraded: `status:"degraded"`, `db:"down"` if the `SELECT 1` throws. Rate limit
`RATE_HEALTH` = 300/min (`ratelimit.py:86`).

### 4.2 `GET /stats` — sealed product counts (AUTHENTICATED)

`ops.py:47`. Five live `COUNT(*)`; **competitive coverage signal, authed**.
Cached (§6) and rate-limited `RATE_EXPENSIVE`. **Slow on a cold cache**: measured
~**80s** wall time live (`time_total=79.6s`) over the 2.3M-row tables, then served
from the 60s cache. A replicating country should keep the cache and may add a
materialized snapshot if the table grows.

Live `[VERIFIED]`:
```json
{"ok":true,"data":{"counts":{
  "dealers":54570,
  "vehicles_unique_available":1853644,
  "events":2613437,
  "provinces":52,
  "municipalities":8132}},
 "error":null,"meta":{"cache":"miss"}}
```
Count definitions (`ops.py:57-95`):
- `dealers` — `COUNT(DISTINCT v_dealer_resolved.resolved_cdp_code)` joined to
  `entity` filtered `kind <> 'particular'`. **Computed live, never hardcoded**
  (a stale `40 016` literal was the audit Q10 doc-drift).
- `vehicles_unique_available` — `v_canonical_vehicle` canonical-only
  (`vehicle_ulid = canonical_vehicle_ulid`) ∧ `status='available'`. One row per
  physical car (drops cross-entity aliases).
- `events` — total `vehicle_event` rows (unfiltered, full history).
- `provinces` / `municipalities` — geo backbone row counts.

### 4.3 `GET /entities/{cdp_code}` — canonical entity + aggregated cluster stock

`entities.py:53`. Resolves `cdp_code` → canonical cluster (§8), returns the
**canonical** entity row (full `entity` schema, §9.1) augmented with:

| Added field | Meaning | Source |
|---|---|---|
| `available_inventory` | distinct available canonical cars across ALL cluster members | `entities.py:73` |
| `canonical_cdp_code` | the cluster's canonical code | `entities.py:84` |
| `n_aliases` | `len(members) - 1` | `entities.py:85` |
| `queried_cdp_code` | the code the caller asked for | `entities.py:86` |

`available_inventory` uses `LEFT JOIN v_canonical_vehicle … COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid)`
so a car not yet in any cluster run still counts (an INNER JOIN dropped them,
reporting 0 stock for live dealers — `entities.py:70-72`).

Live `[VERIFIED]` (trimmed): `kind:"compraventa"`, `status:"active"`,
`country_code:"ES"`, `available_inventory:20`, `n_aliases:0`. 404 → `err`.

### 4.4 `GET /entities/{cdp_code}/canonical` — cluster membership

`entities.py:30`. Identity-only resolution.

Live `[VERIFIED]`:
```json
{"ok":true,"data":{"input_cdp_code":"CDP-ES-00-09VQ5R5R",
  "canonical_cdp_code":"CDP-ES-00-09VQ5R5R","is_canonical":true,
  "members":["CDP-ES-00-09VQ5R5R"],"n_members":1},"error":null,"meta":null}
```
404 (`err`) when the code is unknown.

### 4.5 `GET /entities/{cdp_code}/inventory` — available canonical stock (cluster-wide)

`entities.py:94`. **The heaviest endpoint.** Paginated; cached; `RATE_EXPENSIVE`.

Dedup contract (`entities.py:105-115`, sealed product surface `main.py:23-27`):
`DISTINCT ON (COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid))` across all
cluster member entities, `status='available'`.
- **Collapses** the dealer's own cross-platform duplicates (same physical car on
  two of its platforms → one).
- **Keeps** cars whose *global* canonical belongs to another dealer (this dealer
  genuinely lists them) — the global canonical-only filter would wrongly drop
  ~102,449 cross-dealer cars.

Per-row schema = the inventory vehicle shape (§9.3). Live `[VERIFIED]` (size=1)
returned one full row with `make/model/year/km/price/currency/fuel/transmission/
photo_url/status/first_seen/last_seen/deep_link/title` and
`meta:{page,size,returned,has_more,cache}`.

### 4.6 `GET /entities/{cdp_code}/delta` — **vehicle events for the FULL cluster**

`entities.py:170`. **The delta endpoint — the heart of the live census.**
Paginated; not cached; `RATE_DEFAULT`. Optional `since` (ISO-8601; `Z` accepted).

Query (`entities.py:204-230`): `vehicle_event WHERE entity_ulid = ANY(cluster
member_ulids) [AND observed_at >= since] ORDER BY observed_at DESC, event_type`.
Cluster-aware (GAP-4): events from **all** cluster members merged.

Per-event row: `event_type`, `old_value`, `new_value`, `observed_at`,
`entity_ulid`. **Note the wire shape: `old_value`/`new_value` are JSON-encoded
*strings*, not nested objects** (asyncpg returns the JSONB column as a text
string and it is passed through verbatim) `[VERIFIED]`:
```json
{"event_type":"NEW","old_value":null,
 "new_value":"{\"price\": 29900.0, \"title\": \"CUPRA Formentor 1.5 eTSI\", \"platform\": \"Motorflash\"}",
 "observed_at":"2026-06-13 20:38:05.998572+00:00",
 "entity_ulid":"01KV1B8DZ3XB8QDDA89FVCKB25"}
```
Bad `since` → 400 `err("invalid since format …; use ISO-8601 …")`
(`entities.py:194`). Unknown cdp → 404. **See §10 for the full delta semantics
this endpoint exposes.**

### 4.7 `GET /vehicles/{vehicle_ulid}` — single vehicle detail

`vehicles.py:70`. Not cached; `RATE_DEFAULT`. Resolves the alias dimension:
exposes `is_canonical` and `canonical_vehicle_ulid` (falls back to self) so a
caller hitting a non-canonical alias can redirect (`vehicles.py:102-104`).

Live `[VERIFIED]` (trimmed): full `make/model/year/km/price/currency/fuel/
transmission/photo_url/deep_link/title/status/first_seen/last_seen` +
`is_canonical:true`, `canonical_vehicle_ulid:"…"`. `price` cast to `float|null`.
404 → `err`.

### 4.8 `GET /vehicles/{vehicle_ulid}/history` — **full event timeline for one car**

`vehicles.py:24`. Paginated; **oldest first** (`ORDER BY observed_at ASC`) so a
consumer can **replay** the lifecycle. History is served even for a
non-canonical alias (`vehicles.py:34-38`): aliasing is an entity-level concept,
not an erasure of timeline.

Per-row: `event_type`, `old_value`, `new_value`, `observed_at` (no `entity_ulid`
here, unlike `/delta`). Live `[VERIFIED]` shows the real lifecycle of one car:
```json
[{"event_type":"NEW","old_value":null,"new_value":"{\"price\": 36090.0, \"title\": \"Audi Q3 35 TDI Black line\"}","observed_at":"2026-06-12 13:02:13.409797+00:00"},
 {"event_type":"PRICE_CHANGE","old_value":"{\"price\": 36090.0}","new_value":"{\"price\": 35817.0}","observed_at":"2026-06-12 13:55:10.766111+00:00"},
 {"event_type":"PHOTO_CHANGE","old_value":"{\"photo\": \"…9fe10cae….webp\"}","new_value":"{\"photo\": \"…cc37aa09….webp\"}","observed_at":"2026-06-12 13:55:10.786387+00:00"}]
```
`meta` carries `vehicle_ulid` plus pagination. 404 when the ulid is absent from
`vehicle`.

### 4.8b `GET /vehicles/{vehicle_ulid}/lifetime` — **"Vida en mercado"** (02-history-reports F2)

`vehicles.py` (appended after `/history`). Un-paginated (`meta.count` = episode
count); not cached (measured p95 ≈241ms for a single-episode vehicle over 20
live requests — under the threshold that would justify caching per this
pillar's own F2 close-out rule: "la decisión de cachear se toma con medición,
no antes"); `RATE_DEFAULT`. 404 when the ulid is absent from `vehicle`; served
for non-canonical aliases too (same contract as `/history` above — aliasing is
entity-level dedup, not an erasure of this vehicle's own lifetime).

Walks `v_vehicle_lifetime` (migrations/0075, the F1 overlay — **only the most
recent `lifetime_link_run` with `vam_verified=TRUE` is ever read**; today no
run has been gated TRUE, see plans/cardeep-omni/02-history-reports.md §11, so
this view serves 0 rows and every vehicle degrades honestly to
`chain_verified:false`) outward from `vehicle_ulid` in both directions via a
bounded recursive CTE, then computes the C1-C10 aggregates from
`services/api/lifetime_aggregates.py` (pure functions, zero DB imports, 26 unit
tests) over each chain member's own `vehicle_event` rows.

Response shape — `data`:
```jsonc
{
  "vehicle_ulid": "…",
  "chain_verified": false,               // true only once an F1 run is vam_verified
  "episodes": [                          // 1 today whenever chain_verified=false
    {
      "vehicle_ulid": "…", "entity_ulid": "…",
      "c1_days": 34, "c1_suppressed": false, "c1_suppression_reason": null,
      "c3_price_drops": 0, "c3_price_increases": 1, "c4_pct_drop": -0.68,
      "c8a_km_retreats": [],             // [{old_km,new_km,delta,observed_at}] when >1000km
      "make": "SEAT", "model": "Arona", "year": 2023,
      "price": 13773.0, "km": 69695, "status": "available",
      "first_seen": "…", "last_seen": "…",
      "dealer_cdp_code": "CDP-ES-28-…", "dealer_name": "…"
    }
  ],
  "links": [],                            // F1's lifetime_link edges in this chain
  "aggregates": {                         // C2/C6/C7/C8b — null/false/[] whenever chain_verified=false
    "chain_verified": false, "c2_total_days": null,
    "c6_dealer_count": null, "c7_episode_count": 1, "c7_rebotado": false,
    "c8b_km_retreats": []                 // reuses F1's per-edge evidence.km_retreat_flagged verbatim
  },
  "semaforo": { "label": "sin_senales", "triggers": [] },  // C9, taxative closed list
  "freshness": "visto hace 20 días"       // C10
}
```
Live `[VERIFIED]` against a real vehicle (`curl http://127.0.0.1:8090/vehicles/{ulid}/lifetime`),
2026-07-18: byte-correct UTF-8 (verified with a binary-safe `-o file` capture —
a terminal-codepage mojibake red herring was ruled out, not a wire-format bug).

**C1 dual-path suppression** (§7 of the pillar letter): C1 compares
`vehicle.first_seen`/`last_seen` against the `NEW`/`GONE` event timestamps; a
divergence > 24h suppresses `c1_days` (`c1_suppressed:true`, with a named
`c1_suppression_reason`) rather than serving a number only one path agrees on.

**Non-canonical alias / no-chain parity test**: `tests/test_api_lifetime.py`
covers 404, envelope shape, alias service, a vehicle with no verified chain
(the v1 default for every vehicle today), and skips (never fails) the
verified-chain assertion while no run is gated TRUE — an honest skip, not a
silenced failure.

### 4.9 `GET /vehicles/{vehicle_ulid}/platforms` — platforms a car is listed on

`platforms.py:88`. Un-paginated (`meta.count`); not cached; `RATE_DEFAULT`.
Returns `{vehicle:{…, owning_dealer:{cdp_code,name,kind}}, platforms:[…]}`. Each
platform: `cdp_code, trade_name, website, is_tier1, listing_ref, listing_url,
platform_price(float|null), status, first_seen, last_seen`.

Live `[VERIFIED]`: a car owned by `AUTOHERO BARCELONA` with `platforms:[]`,
`meta:{count:0}` (this car is on no separate platform; its dealer harvested it
direct). 404 when the ulid is absent.

### 4.10 `GET /platforms/{cdp_code}/inventory` — cars on a platform, with dealer attribution

`platforms.py:25`. Paginated; cached; `RATE_EXPENSIVE` (Wallapop/milanuncios have
500k+ listed rows). **Guards entity kind**: 400 `err` if the cdp is not
`kind='plataforma'` (`platforms.py:49`).

Joins `platform_listing` → `servable_vehicle` → owning `entity`, filtered
`pl.status='listed' AND v.status='available'`. Per-row mixes listing + vehicle +
selling-dealer attribution: `listing_ref, listing_url, platform_price(float),
listing_status, listed_first_seen, listed_last_seen, vehicle_ulid, make, model,
year, km, price(float), currency, fuel, transmission, photo_url, vehicle_status,
dealer_cdp_code, dealer_name, dealer_province, dealer_municipality, dealer_kind`.

Live `[VERIFIED]` for `milanuncios`: a SEAT listed by a `particular` dealer in
province 52, `platform_price:4250.0`, `meta:{…,platform:"milanuncios",cdp_code,cache}`.

### 4.11 `GET /geo/{province_code}/entities` — active non-particular dealers in a province

`geo.py:229`. Paginated; cached; `RATE_DEFAULT`. **Curated map filter** (GAP-1):
`WHERE status='active' AND kind <> 'particular'`, then `DISTINCT ON
(v_dealer_resolved.resolved_cdp_code)` so each real dealer appears **once** (was
serving raw rows → "QUADIS Autolica ×520"; audit 2026-06-16 F-A, `geo.py:255-258`).

Per-row: `cdp_code` (the canonical), `kind, trade_name, legal_name,
municipality_code, is_tier1, status`. Live `[VERIFIED]` (Barcelona, size=1):
one `compraventa`, `meta:{…,province:"08",cache}`.

### 4.12 `GET /geo/{province_code}/municipalities/{muni_code}/entities`

`geo.py:291`. Same active/non-particular filter scoped to `municipality_code`, so
callers drill country → province → municipality without the full province dump.
Paginated; cached; `RATE_DEFAULT`. `meta` adds `province`, `municipality`.

### 4.13 `GET /geo/{province_code}/tree` — inventory tree país→PROVINCIA→COMARCA→ciudad

`geo.py:350`. Cached; `RATE_EXPENSIVE` (GROUP BY over 50k+ rows). 404 `err` for
an unknown province. Returns `{province:{code,name,ccaa_code,ccaa_name},
comarcas:[{comarca_id,ine_code,name,entities,municipalities:[{municipality_code,
name,entities, <per-kind counts>}]}], entities_geo_clean,
entities_province_only_no_municipality}`. Per-kind counts:
`compraventa, oficial, desguace, plataforma, garaje, subasta, oem_vo_portal,
importador, rent_a_car_vo`. Scoped to `kind <> 'particular' AND status='active'`
(audit P2 E-geo-tree, `geo.py:388,409-414`).

Live `[VERIFIED]` Barcelona: `ccaa_name:"Cataluña"`, real comarca/municipality
breakdown.

### 4.14 `GET /geo/completeness` — national geo-coverage report

`geo.py:32`. Cached; `RATE_EXPENSIVE` (7 sequential `COUNT(*)`). DEALER-scoped
(`kind <> 'particular'` — particulares are platform-attributed C2C, not geo-located
POS, `geo.py:48-54`).

Live `[VERIFIED]`:
```json
{"geo_grid":{"provinces":52,"comarcas":323,"municipalities":8132,"municipalities_with_comarca":8130},
 "entities":{"scope":"dealers (kind<>particular)","total":91412,
   "full_prov_comarca_muni":78416,"municipality_no_comarca_ceuta_melilla":135,
   "province_only":11771,"no_geo":1090,"full_pct":85.78},
 "vehicles":{"total":2312444,"full_prov_comarca_muni":1793201,"full_pct":77.55}}
```

### 4.15 `GET /geo/seal` — per-province SU-SEAL by segment

`geo.py:92`. Cached; `RATE_EXPENSIVE`. Backed by live view `v_province_seal`
(migrations 0042+0043). Two segments:
- **`venta`** — served canonical dealers ÷ DIRCE CNAE-451 registral ceiling.
  Verdict `SELLADO >=85% / PARCIAL 50-85% / GAP <50%`.
- **`desguace`** — scrapyards found ÷ DGT census (discovery; `SELLADO` when
  found ≥ census).

Returns `{segments:{<seg>:{method, national:{numerator,denominator,coverage_pct},
distribution:{<verdict>:n}, provinces:[{province_code,denominator,numerator,
coverage_pct,verdict}]}}}`. Live `[VERIFIED]`: `desguace` national
`numerator:2785 denominator:1292 coverage_pct:215.6` (found exceeds census), all
52 provinces `SELLADO`.

### 4.16 `GET /geo/exhaustiveness` — national coverage CERTIFICATE (in code; redeploy to serve)

`geo.py:147`. **In current code, NOT in the running process (live → 404)**
`[VERIFIED]`. A fresh deploy serves it. Backed by `v_exhaustiveness_seal`:
capture-recapture / MSE statistical lower bound on completeness from k orthogonal
discovery lists (Chapman / stratified). Returns
`{certificate:"national_exhaustiveness_mse", method, build_run_id, generated_at,
national:{k_lists,n_obs,n_hat,ci_low,ci_high,coverage_point,coverage_lower,method,
confidence,seal_threshold,sealed}, by_segment:{<seg>:{national,provinces:[…]}}}`.
Honest by construction: a thin stratum reports `coverage_lower` near 0 and
`sealed:false`, never a fabricated 100%.

### 4.17 `GET /alerts` — active unresolved alerts

`ops.py:105`. Paginated; **not cached** (state changes any time); `RATE_DEFAULT`.
`WHERE resolved_at IS NULL`, ordered `critical → warning → info` then newest.
Per-row: `id, origin, severity, message, payload, created_at`.

Live `[VERIFIED]`: critical source-silence alerts (e.g.
`motor_es_wholesale:silence` "source silent 177.2h, expected every 24h", with a
JSON `payload`).

### 4.18 `GET /sources` — source-health overview

`ops.py:159`. Un-paginated (`meta.count`); **not cached**; `RATE_DEFAULT`.
Ordered `down → degraded → unknown → ok` then `consecutive_fails DESC`. Per-row:
`source_key, status, consecutive_fails, last_ok, last_fail, is_tier1`. Live
`[VERIFIED]`: `degraded` sources with timestamps.

### 4.19 `GET /engine/status` — motor status (00-marketplace-engine.md F5/F6)

`ops.py` (F5). **Not cached** — this endpoint IS the near-real-time trust signal
the carta's §7 two-path verification discipline exists to serve. `RATE_DEFAULT`.

- `badge`: `LATIENDO` (age<30min) / `DEGRADADO` (age<24h) / `PARADO` (>=24h or
  no lease row) — computed in SQL (`EXTRACT(EPOCH FROM now()-last_heartbeat)`)
  against `scheduler_lease` so the boundary is never skewed by API-host vs
  DB-host clock drift.
- `lease`: `holder, pid, started_at, last_heartbeat, age_seconds` of the harvest
  scheduler's singleton advisory lock (`scheduler_lease`, migration 0054).
- `jobs`: every `apscheduler_jobs` row (`id, next_run_time` ISO) — the §7 vía-B
  signal (poll twice ≥15min apart and confirm `next_run_time` actually
  advanced, independent of `scheduler_lease`).
- `replay_progress`: `sources_total` (all of `source_health`) and
  `sources_harvested_since_holder_started` (`last_ok >= lease.started_at`) —
  an honest APPROXIMATION of cold-start replay, not the exact "fuentes DUE al
  arrancar" the carta's §4 names (that denominator is not captured
  retroactively); the `note` field says so explicitly.
- `uptime`: `{"30d": ..., "90d": ...}` (F6) computed from `engine_heartbeat_log`
  (migration 0085, INSERT-only, one row per ~2-min heartbeat). Each window:
  `requested_days, full_window_available, observed_from, observed_to,
  bucket_minutes (15), buckets_total, buckets_with_beat, uptime_pct`.
  `full_window_available=false` and a short `observed_from`↔`observed_to` span
  is the HONEST answer before the ledger has 30/90 days of real history — a
  fresh deployment never reports a fabricated 0%/100%
  (`pipeline/ops/engine_uptime.py`'s anti-alucinación guard).

Live `[VERIFIED]` 2026-07-18: `badge=LATIENDO`, `lease.holder=harvest`,
`replay_progress` `39/56` sources harvested since the current holder's
`started_at`, `uptime.30d.uptime_pct=100.0` (buckets_total=1 — the ledger had
just started; see the carta §9 F6 for the destructive-test evidence of a real
provoked outage reflected in this same field).

---

## 5. Authentication — `CARDEEP_API_KEY`

`deps.py:29-35`. **Backward-compatible, env-gated, read per request:**

| `CARDEEP_API_KEY` env | Behavior |
|---|---|
| **unset** | **public mode** — all callers pass; `X-API-Key` ignored |
| **set** | **protected mode** — every data endpoint requires header `X-API-Key: <value>` |

- Mismatch / missing header in protected mode → **HTTP 401**,
  `detail:"Invalid or missing API key"` (FastAPI `HTTPException`; note this is the
  raw FastAPI error shape, not the project envelope — `deps.py:35`).
- Applied via `Depends(require_api_key)` on **all data endpoints**;
  **NOT** on `/health` (`deps.py:26`, `main.py:34`) so liveness probes always pass.
- Read from `os.environ` **per request**, so toggling the key takes effect with
  no restart (`deps.py:31`).
- `/openapi.json` is **unauthenticated** (FastAPI built-in).
- The server is currently in **public mode** (no key set): a request with a
  bogus `X-API-Key` still returns 200 `[VERIFIED]`.

**Replication note:** single shared key only. The response cache key has **no
tenant dimension** (`cache.py:79-86`); introducing per-tenant keys WITHOUT adding
the key to the cache key would let tenant A read tenant B's cached body. Multi-
tenant auth MUST extend `_cache_key`.

---

## 6. Response caching — in-memory TTL

`cache.py`. `cachetools.TTLCache`, in-process (no Redis, €0).

- **Key** = `METHOD:PATH?sorted-query-string` (`cache.py:79-94`). Deterministic
  regardless of client param order. **No auth/tenant dimension** (see §5).
- **TTL** = `CACHE_TTL_SECONDS = 60`; **max** = `CACHE_MAXSIZE = 512` (LRU evict)
  (`cache.py:49-53`).
- **Eligible prefixes**: `/geo/`, `/entities/`, `/platforms/` (`cache.py:57-62`).
  `/stats` is cached via the same helpers (it calls `try_cache_get`/`cache_set`
  directly despite the prefix list; `ops.py:70,98`).
- **Never cached**: `/health`, `/alerts`, `/sources` (`cache.py:66-70`), plus
  all error responses (`cache_set` only stores `ok:true` 2xx, `cache.py:149-151`).
- **Observability**: every cacheable response carries `meta.cache = "hit" | "miss"`
  `[VERIFIED]` (`cache.py:127-131,159-164`). GETs only (`cache.py:99`).
- Single-worker safety only: `TTLCache` is not thread-safe; the contract assumes
  single-process uvicorn. Multi-process → promote to shared/Redis cache
  (`cache.py:17-24`).

---

## 7. Rate limiting — slowapi, in-memory

`ratelimit.py`. `slowapi.Limiter`, key = client IP (`get_remote_address`),
storage `memory://` (`ratelimit.py:93-102`).

| Tier | Limit | Endpoints |
|---|---|---|
| `RATE_DEFAULT` | **120/minute** | entity/canonical/delta, vehicle/history/platforms, geo entities/muni, alerts, sources |
| `RATE_EXPENSIVE` | **30/minute** | inventory, platform-inventory, geo tree/completeness/seal/exhaustiveness, stats |
| `RATE_HEALTH` | **300/minute** | health |

- Gate: env `CARDEEP_API_RATELIMIT_ENABLED` (default `"1"`). `"0"` → all limits
  become a no-op `9999/second` (`ratelimit.py:72-87`).
- **Read ONCE at import**, baked into the limiter. Toggling the env or changing a
  limit in a running process has **no effect** — requires restart (`ratelimit.py:68-71`).
- Exceeded → **HTTP 429** in the project envelope (`ratelimit.py:109-136`):
  ```json
  {"ok":false,"data":null,"error":"rate_limit_exceeded",
   "meta":{"detail":"<slowapi message>","retry_after":<int|null>}}
  ```
  `Retry-After` header preserved when present.

---

## 8. Cluster resolution (entity identity)

`deps.py:73-122`. A `cdp_code` resolves to its **canonical cluster** via
`v_dealer_resolved` (transitive VAM-verified clusters), falling back to the
entity's own ulid for non-clustered entities. `ClusterInfo` carries
`canonical_cdp_code`, `canonical_ulid`, `member_ulids[]`, `member_cdp_codes[]`.

Consequence for the contract: `/entities/{cdp}`, `/entities/{cdp}/canonical`,
`/entities/{cdp}/inventory`, `/entities/{cdp}/delta` are **all cluster-aware** —
ask for any member and you get the canonical entity, the whole cluster's stock,
and the whole cluster's event stream. `resolve_cluster` returning `None` → 404.

**Curated vs raw divergence (intentional, `main.py:28-33`):** per-dealer
`/entities/{cdp}/inventory` and `/platforms/{cdp}/inventory` **do NOT** apply the
entity-status filter — a directly requested dealer's full stock is served
regardless of verification status ("sacarle TODO su stock"). The `/geo/*` map is
the curated surface (`status='active' AND kind <> 'particular'`).

---

## 9. Schemas (country-agnostic field map)

### 9.1 `entity` (the dealer / platform / particular record)

Full live column list (`information_schema`, `[VERIFIED]`). **Country-agnostic
unless noted.** ES-specific fields are flagged — a replicating country reuses the
same columns with its own values.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| `entity_ulid` | text | NO | — | PK, 26-char Crockford ULID |
| `cdp_code` | text | NO | — | UNIQUE; `CDP-{CC}-{prov2}-{8 base32}` (§11) |
| `country_code` | char(2) | NO | `'ES'` | **the country dimension** (migration 0052) |
| `kind` | enum `entity_kind` | NO | — | see §9.2 |
| `legal_name`, `trade_name` | text | YES | — | |
| `cif` | text | YES | — | **ES tax id**; rename concept per country (§11) |
| `cnae` | text | YES | — | **ES economic-activity code** (CNAE-451 used by seal) |
| `province_code` | char | YES | — | FK geo_province (**ES INE 01-52**) |
| `municipality_code` | char | YES | — | FK geo_municipality (**ES INE 5-digit**) |
| `comarca_id` | bigint | YES | — | FK geo_comarca |
| `address`, `postcode` | text | YES | — | |
| `lat`, `lon` | double | YES | — | plain doubles, no PostGIS |
| `phone`, `email`, `website` | text | YES | — | |
| `website_waf` | enum `waf_kind` | YES | `'none'` | bot-defense fingerprint |
| `is_tier1` | bool | NO | `false` | priority source flag |
| `status` | enum `entity_status` | NO | `'unverified'` | `active` after VAM verify |
| `recipe_version` | int | YES | — | per-dealer recipe version |
| `first_discovered_source` | text | YES | — | source key that first found it |
| `created_at`, `last_seen` | timestamptz | NO | `now()` | |
| `org_id` | text | YES | — | chain vs branch FK |
| `sells_cars` | bool | YES | — | NULL=unknown, FALSE=pure taller |
| `kind_source` | enum `kind_source` | NO | `'manual'` | which rung decided `kind` |
| `geocode_source`, `geocode_precision` | text | YES | — | geo provenance/quality |
| `defense_detail` | jsonb | YES | — | raw bot-defense fingerprint |
| `closed_at`, `close_reason` | — | YES | — | soft-close (closure is a state) |
| `canonical_key` | text | YES | — | exact pre-image `cdp_code` hashed (audit) |
| `attest_count` | int | NO | `1` | # orthogonal sources |
| `defense_tier`, `source_group`, `role` | enums | YES | — | classification facets |
| `evicted_at` | timestamptz | YES | — | |

API never returns `created_at`/`last_seen` as raw timestamptz — they are
`str()`-cast (`entities.py:81-82`).

### 9.2 `entity_kind` enum (live distribution `[VERIFIED]`)

`particular 339,800` · `compraventa 76,076` · `garaje 10,021` · `desguace 2,785`
· `concesionario_oficial 2,300` · `subasta 177` · `plataforma 18` ·
`oem_vo_portal 14` · `importador 11` · `rent_a_car_vo 6` · `cadena 4`.

`particular` = C2C private sellers (excluded from the curated geo map and dealer
counts). The other kinds are the digital sales points the census certifies.

### 9.3 `vehicle` (inventory) — `migrations/0003_vehicles_events.sql`

| Column | Type | Notes |
|---|---|---|
| `vehicle_ulid` | text PK | |
| `entity_ulid` | text FK → entity, ON DELETE CASCADE | owning dealer |
| `deep_link` | text NOT NULL | per-vehicle URL; `UNIQUE(entity_ulid, deep_link)` |
| `title, make, model` | text | `make` canonicalized at ingest (`normalize_make`) |
| `year` | int | sanitized 1900..next-model-year |
| `km` | int | sanitized 0..1.5M |
| `price` | numeric(12,2) | API casts to `float|null`; sanitized 0<p<=10M |
| `currency` | char(3) NOT NULL **default `'EUR'`** | **country-agnostic field, ES default** |
| `fuel, transmission` | text | |
| `photo_url` | text | |
| `photo_hash` | text | perceptual hash for Δphoto (§10) |
| `vin_ref` | text | |
| `recipe_version` | int | |
| `status` | text NOT NULL default `'available'` | CHECK in (`available`,`gone`) |
| `first_seen, last_seen` | timestamptz NOT NULL default `now()` | API `str()`-casts both |

### 9.4 `v_canonical_vehicle` — the vehicle dedup view

Maps `vehicle_ulid → canonical_vehicle_ulid`. A vehicle is canonical when
`vehicle_ulid = canonical_vehicle_ulid`. Used everywhere to collapse cross-dealer
/ cross-platform duplicates of the same physical car. `is_canonical` on
`/vehicles/{ulid}` and the inventory `DISTINCT ON` both derive from it.

### 9.5 Seal views

`v_province_seal` (`/geo/seal`) and `v_exhaustiveness_seal`
(`/geo/exhaustiveness`) — recomputed from the live harvest, so the seal always
reflects current coverage. The replicating country supplies its own registral
ceiling (Spain: DIRCE CNAE-451) and official census (Spain: DGT desguaces).

---

## 10. DELTA SEMANTICS — the contract another country MUST honor

The delta is the product's differentiator: a **queryable, append-only timeline**
of every change to every car. Emitted by the ingest pipeline
(`pipeline/ingest.py`, `pipeline/delta.py`), served by `/entities/{cdp}/delta`
(per dealer-cluster) and `/vehicles/{ulid}/history` (per car).

### 10.1 `vehicle_event` — the immutable timeline (`migrations/0003`)

```
event_ulid   TEXT PK
vehicle_ulid TEXT FK → vehicle  (CASCADE)
entity_ulid  TEXT FK → entity   (CASCADE)
event_type   TEXT CHECK IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE')
old_value    JSONB    -- snapshot before the change (null for NEW)
new_value    JSONB    -- value after the change   (null for GONE)
observed_at  TIMESTAMPTZ DEFAULT now()
```
**Append-only by mandate — never UPDATEd or DELETEd** (migration comment line
"NEVER updated or deleted — the full timeline"). Guarded by append-only row
guards (migrations 0034/0035). **No UNIQUE on `(vehicle_ulid, event_type)`** —
duplicate prevention for GONE is enforced in code (§10.3).

### 10.2 The five event types (live counts §0)

| `event_type` | When | `old_value` | `new_value` | Emitter |
|---|---|---|---|---|
| **`NEW`** (alta) | first time a car is seen | `null` | `{"price":<f|null>,"title":…[,"platform":…]}` | `ingest.py:102` / connectors |
| **`PRICE_CHANGE`** (Δprice) | sanitized price differs OR null→valid fill | `{"price":<f|null>}` | `{"price":<f>}` | `delta.diff_vehicle:319` |
| **`KM_CHANGE`** (Δkm) | sanitized km differs OR null→valid fill | `{"km":<i|null>}` | `{"km":<i>}` | `delta.diff_vehicle:329` |
| **`PHOTO_CHANGE`** (Δphoto) | perceptual-hash Hamming > threshold, else url string differs | `{"photo":…[,"phash":…]}` | `{"photo":…[,"phash":…]}` | `delta.diff_vehicle:346-358` |
| **`GONE`** (baja) | available car not re-seen in a complete harvest | `{"price":<f|null>}` | `null` | `delta.reconcile_gone` / `emit_gone_events` |

**Rules a replicating country must preserve:**
- **No false positives.** `diff_vehicle` returns `[]` when nothing changed
  (`delta.py:308`). Junk is nulled at the boundary (`sanitize_price/km`): a junk
  scrape (≤0 / >10M price, km>1.5M) → `None` → **no event** (`delta.py:318,328`).
- **Null→valid promotion fires an event.** A car first listed without a price/km
  that later gets one emits `PRICE_CHANGE`/`KM_CHANGE` (`old_value.price=null`)
  — the old asymmetric guard silently dropped this across all 26 connectors
  (`delta.py:314-319`).
- **Δphoto is content-aware.** With perceptual hashes on both sides it compares
  64-bit pHash by Hamming distance (catches re-photo on same URL; ignores a CDN
  URL rotation of an unchanged image). Falls back to URL string compare when
  either side lacks a pHash — backward compatible (`delta.py:336-358`).
- **Re-seen unchanged cars are NOT touched** — only `last_seen` refreshes; no
  dead tuples, no event (`ingest.py:8` doctrine; `emit_change_deltas` only writes
  rows that changed, `delta.py:402-403`).
- **`emit_change_deltas`** is the shared, connector-agnostic landing-time emitter
  so PRICE/KM/PHOTO semantics are identical and tested once (`delta.py:388`).

### 10.3 GONE reconciliation (the baja contract) — `delta.reconcile_gone`

A car goes `gone` when it was `available` and **not re-seen** in the latest
harvest (`last_seen < run_started_at`). This is the riskiest operation (a broken
harvest could wipe an inventory), so it is **heavily gated** (`delta.py:146-283`):

1. **Source-scoped** — only vehicles with an `entity_source` row for
   `source_key`. No cross-source contamination (`_FIND_STALE`, `delta.py:77-84`).
2. **Coverage gate** — when `min_coverage` is passed, `reconcile_gone` reads
   `source_coverage` and **refuses to retire** unless `coverage_pct >= floor`
   and verdict is not `REFUTED`. No verdict → skip. "Better a hole than a lie."
   (`delta.py:183-201`).
3. **Gone-fraction cap** — for inventories ≥ `MIN_INVENTORY_FOR_GUARD` (20),
   if retiring would exceed `max_gone_fraction` (default **0.50**) of available
   stock, the sweep **ABORTS** touching nothing (almost certainly a partial run,
   not real churn) (`delta.py:227-238`).
4. **Idempotent** — already-`gone` rows are skipped by the `status='available'`
   guard on the UPDATE; an `UPDATE 0` (race / re-run) skips the event so the
   timeline never gets a duplicate GONE (`delta.py:259-266`).
5. **Atomic** — the whole sweep is ONE transaction: a crash mid-loop never
   leaves a half-retired inventory (`delta.py:240-245`).
6. **Event on retire** — each retire flips `vehicle.status='gone'` AND inserts a
   `GONE` event with `old_value={"price":…}`, `new_value=null` (`delta.py:264-274`).

`emit_gone_events` (`delta.py:110-143`) covers connectors that retire by their
own platform-edge set (group_subastas, localizavo) rather than by `last_seen`:
same one-GONE-per-vehicle contract, idempotent via an existence check (it fixed
audit P4: 1,823 silent bajas with no GONE event).

### 10.4 History queryability (the read contract)

- **Per vehicle:** `GET /vehicles/{ulid}/history` — full timeline, **oldest
  first**, paginated, served even for non-canonical aliases (the alias's
  `vehicle_ulid` is a real row in `vehicle_event`) (`vehicles.py:24-67`).
- **Per dealer (cluster):** `GET /entities/{cdp}/delta` — all events for all
  cluster members, **newest first**, `since` filter, paginated
  (`entities.py:170-238`).
- **Both** expose `event_type, old_value, new_value, observed_at`
  (`/delta` adds `entity_ulid`). `old_value`/`new_value` are JSON **strings** on
  the wire (§4.6). A consumer replays a car's life by reading `/history` ASC and
  applying each `new_value`; reconciles a dealer's churn by polling `/delta?since=`.

---

## 11. Country-agnostic vs ES-specific (replication map)

What is already parametrized (FASE-0, verified in code):
- **`cdp_code` country segment** — `mint_code(province_code, digest,
  country_code='ES')` is the ONE home of the `CDP-{CC}-` literal
  (`services/api/codes.py:44-53`). `country_code` enters ONLY the human-facing
  prefix; it is deliberately **kept OUT of `canonical_key`'s pre-image**
  (`codes.py:56-66`) so threading a country can never re-key an existing entity.
- **Filesystem roots** — `recipe_root/recipes_flat_dir/data_root/census_dir`
  default to `ES` (`pipeline/paths.py`); `country_of_cdp` derives the country
  from a `cdp_code`'s `CDP-XX-` segment with no DB lookup.
- **`entity.country_code` + geo `country_code`** — `CHAR(2) DEFAULT 'ES'` on
  `geo_province/geo_comarca/geo_municipality/entity`, plus composite
  `UNIQUE(country_code, code)` on province/municipality (migration
  `0052_country.sql`). Live: single tenant `ES` (431,212 rows).

What is **ES-specific** and must be supplied per country:
- Tax id concept: `entity.cif` (Spain CIF) — semantics differ per jurisdiction.
- `entity.cnae` and the seal's **DIRCE CNAE-451** registral ceiling (`/geo/seal`
  `venta` segment) — each country has its own registry/economic-activity code.
- **DGT desguace census** (`/geo/seal` `desguace` denominator) — country-specific.
- Geo codes: `province_code` (ES INE 01-52), `municipality_code` (ES INE 5-digit),
  and the ES CHECKs `municipality_province_prefix` and `chk_entity_muni_province`
  (`left(code,2)=province_code`) — a country whose codes are not `<prov2><muni3>`
  must relax these at onboarding.
- `vehicle.currency` default `'EUR'`.

**Deferred switchover work** (PK swap to `(country_code, code)`, geo CHECK
relaxation, country-specific sources, `country_code` on `denominator_estimate`/
`organization`) is the executable checklist in `docs/COUNTRY-SWITCHOVER.md` — not
duplicated here.

---

## 12. CORS

`main.py:114-123`. Origins from `CARDEEP_CORS_ORIGINS` (comma-separated; default
the Vite dev/preview ports `5173`/`4173` on localhost + 127.0.0.1). Allow-methods
`GET, OPTIONS`; allow-headers `X-API-Key, Content-Type`. Preflight `[VERIFIED]`:
`OPTIONS /stats` with `Origin: http://localhost:5173` → 200 with
`access-control-allow-origin`, `access-control-allow-methods: GET, OPTIONS`,
`access-control-allow-headers` echoing `X-API-Key`, `access-control-max-age: 600`.

---

## 13. Error-status contract (summary)

| Status | When | Body |
|---|---|---|
| 200 | success | `{ok:true, data, error:null, meta}` |
| 400 | bad `since` (delta), wrong-kind cdp on `/platforms/{cdp}/inventory` | envelope `ok:false` via `err(…, 400)` |
| 401 | protected mode + bad/missing `X-API-Key` | FastAPI `{"detail":"Invalid or missing API key"}` (**not the envelope**) |
| 404 | unknown cdp / vehicle / province; unmapped route (e.g. `/`, live `/geo/exhaustiveness`) | `err(…)` envelope for handled cases; FastAPI `{"detail":"Not Found"}` for unmapped paths |
| 422 | `page`/`size`/path validation failure | FastAPI validation error (not the envelope) |
| 429 | rate limit exceeded | envelope `error:"rate_limit_exceeded"`, `meta.detail/retry_after` |

> The envelope is honored by **handler-level** errors (`err()`, the 429 handler).
> FastAPI **framework-level** errors (401 `HTTPException`, 422 validation, 404 for
> unmapped routes) use FastAPI's `{"detail":…}` shape. A replicating country that
> wants a uniform envelope on those too must register `exception_handler`s for
> `HTTPException` and `RequestValidationError` — current code does not.
