# Nissan Intelligent Choice (front: nissan_mazda_honda) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** The serving GraphQL flat-enumerates 100% of the
ES public Nissan certified-used inventory with NO relevance/depth cap.
Front: **nissan_mazda_honda** (Nissan Intelligent Choice + Mazda Selected + Honda Approved).
Chosen platform: **ocasion.nissan.es** (Nissan Iberia — Next.js SSR + AWS AppSync GraphQL).
Mazda/Honda **NOT connected** (no clean data surface — see §6).
Defense posture: **no WAF** on the API. `curl_cffi impersonate="chrome131"` serves the
public token endpoint and the AppSync GraphQL directly; **plain x-api-key is Unauthorized —
a Cognito idToken (minted from a public, unauthenticated endpoint) is required.**
Live ES public stock: **1,546** `[VERIFIED]` — the API's own `metaData.totalCount`,
which equals `metaData.totalPages × pageSize` arithmetic (104 pages × 15, page 104 = 1
trailing car) AND the exact count caged + edged + VIN'd in the live DB (VAM TRUSTWORTHY).
Verified LIVE: **2026-06-13** (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy,
no browser, no login, no cookie warm-up, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read, or DB row
> read) unless tagged `[ASSUMED]`.

---

## 0. TL;DR — the uncapped surface (THE win)

The Next.js SSR site calls an **AWS AppSync GraphQL API**. The `GetUsedCarsInventoryData`
operation walks the **entire 1,546-vehicle ES index** as a flat page cursor with **no
relevance cap and no depth cap**. Each vehicle is fully specced and carries a **REAL
per-car VIN** + an embedded selling dealer. A companion `getDealersData` operation on the
same endpoint returns the whole 180-dealer roster with postCode + lat/lng for geo.

```
# 1) mint a fresh Cognito idToken (public, no auth):
GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token
    ?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm
    -> 200 {"idToken":"<JWT, ~1169 chars>"}

# 2) page the inventory (AppSync GraphQL, Authorization: <idToken>):
POST https://gq-eu-prod.nissanpace.com/graphql
     query GetUsedCarsInventoryData(marketConfig, usedCarsInventoryInputData{pageNumber:N, ...})
```

- **Tool:** `curl_cffi` with `impersonate="chrome131"`. No WAF challenge on either host
  (no Akamai/Cloudflare); the Chrome JA3 is sufficient. `[VERIFIED]`
- **Auth:** AppSync authorizes on the **Cognito `idToken`** in the `Authorization` header
  (bare or `Bearer ` prefix both work). The page's `graphqlkey="da2-…"` **x-api-key alone
  returns `Unauthorized`** — do NOT use it. Mint a fresh idToken per run. `[VERIFIED]`
- **Method:** `POST` JSON body `{query, variables}`. `[VERIFIED]`
- **Page size:** **fixed 15 cars/page** (server-side; `usedCarsInventoryInputData` has no
  pageSize override). `[VERIFIED]`
- **Cursor:** `usedCarsInventoryInputData.pageNumber = 1..104`. `metaData.totalCount`
  (1546) bounds the run; page 104 returns the trailing 1, page 105+ returns 0 vehicles.
  `[VERIFIED]`

### Coverage proof (the load-bearing evidence) `[VERIFIED]`
Ran the FULL governed drain LIVE, pages 1→104: **104 pages, 1,546 vehicles, 0 cross-page
dupes, 0 geo-skips, 0 no-dealer-skips.** Caged into cardeep-pg: **1,546 vehicles, 1,546
platform_listing edges, 1,546 VINs, 1,546 NEW delta events.** VAM count quorum
(harvested_cageable == db_edges == db_join_vehicles == 1546) → **TRUSTWORTHY**; breaker
**closed**, health **healthy**. This is the complete flat ES public stock in one pass — no
relevance truncation, no depth wall. `[VERIFIED]`

---

## 1. The denominator — `metaData.totalCount` = 1,546

| Surface | Value | `[VERIFIED]` |
|---|---:|---|
| `getUsedCarsInventoryData.metaData.totalCount` | **1,546** | yes |
| `metaData.totalPages` × `pageSize` (104 × 15, last page = 1) | **1,546** | yes |
| live DB platform_listing edges (full drain) | **1,546** | yes |
| live DB distinct VINs caged | **1,546** | yes |

The denominator is **national** (`queryFilters: make=Nissan`, no geo filter) — the full ES
public certified-used stock, not a geo- or relevance-bounded window. `[VERIFIED]`

---

## 2. Exact request shape

### 2.1 Token mint (public, no auth)
```
GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token
    ?brand=NISSAN&dataSourceType=live&market=ES&client=euecomm
Headers: Accept */*, Origin https://www.ocasion.nissan.es
-> 200 {"idToken":"eyJ…"}   (a Cognito RS256 JWT, ~1169 chars)
```

### 2.2 Inventory (the vehicle data)
```
POST https://gq-eu-prod.nissanpace.com/graphql
Headers: Content-Type application/json, Authorization <idToken>,
         Origin https://www.ocasion.nissan.es, Accept-Language es-ES
Body: { "query": "<GetUsedCarsInventoryData>", "variables": {
  "marketConfig": {"brand":"NISSAN","country":"ES","language":"es",
                   "metadata":{"clientApp":"[WEB]USEDCARS","correlationId":""}},
  "usedCarsInventoryInputData": {
    "usedCarsServletURL":"/content/nissan_prod/es_ES/index/cf-used-cars-ecom.model.json",
    "includeCentralStock":false, "minLatestAchievementPoint":40, "withDiscounts":false,
    "vinListType":"used_cars", "pageNumber":N, "dealerId":"",
    "queryFilters":[{"type":"make","values":["Nissan"]}], "parentFilter":"queryFilters" } } }
```
- `data.getUsedCarsInventoryData.vehicles[]` = 15 fully-specced cars.
- `data.getUsedCarsInventoryData.metaData` = `{totalCount, totalPages, pageIndex, pageSize,
  hasMorePages, nextPageSearchCriteria}`. `[VERIFIED]`
- The full SSR query (with msrpOfferPrice/facets/i18n) was lifted from the site's own chunk
  `index-f3e7293228f0bf0c.js`; the connector ships a **trimmed** query (vehicles{} + metaData{}
  only) — same shape, fewer fields. `[VERIFIED]`

### 2.3 Dealer locator (geo for attribution)
```
POST https://gq-eu-prod.nissanpace.com/graphql   (same endpoint, same auth)
query GetDealers(marketConfig, locationDataInput{lat:40.4,long:-3.7,radius:2000,unit:"K"})
  -> getDealersData[] : 180 dealers, each {id, name, postCode, city, region, stateCode,
                         addressLine1, location{gpsLatitude, gpsLongitude}}
```
- **`getDealersData` requires a non-null location** — a Spain-centre point (40.4,-3.7) with
  a 2000 km radius returns the WHOLE ES roster (180 concesionarios, all with postCode AND
  lat/lng). `[VERIFIED]`
- `getDealersInfoData(marketConfig, dealerId)` resolves a single dealer (same fields). Used
  as a per-id fallback; the bulk roster covers all 41 selling dealers. `[VERIFIED]`

### 2.4 Pagination / page size
Page size is **fixed at 15**. Full run = ~104 inventory POSTs + 1 token GET + 1 roster POST.
`[VERIFIED]`

---

## 3. Per-car fields (`vehicles[]` — self-contained except dealer geo)

| Canonical | Source field | Example |
|---|---|---|
| deep_link (PDP path) | `vehiclesku` (prefixed) | `…/all-vehicles/detail/es_NISSAN_<vin>` |
| **listing_ref / sku (dedup key)** | `vehiclesku` | `es_NISSAN_MQ4IH3WE3X3573338` |
| make / model / version | `make` / `modelName` / `version` | `NISSAN` / `ARIYA` / `Ariya 87kWh Evolve` |
| short version (power) | `shortVersion` | `ELÉCTRICO #### 87 kWh #### 178 KW (242 CV)` |
| model year / first-reg | `modelYear` / `registrationYear` | `2025` / `2025` |
| km | `mileage` (`"91587.0"` → float → int) | `12890` |
| **price (offer)** | `discountedPrice` (fallback `rrpPrice`) | `46250` |
| fuel | `fuelType` | `Gasolina` / `Diésel` / `Eléctrico` / `Híbrido` |
| gearbox | `transmission` | `manual` / `automatico` → Manual/Automático |
| photo | `thumbnailUrl` | `https://media-assets.nissanpace.com/…/small/….webp` |
| **VIN** | `vin` | `MQ4IH3WE3X3573338` |
| certification | `certificationLabel` | `Nissan Certified` |
| **dealer id / name** | `dealer.dealerId` / `dealer.dealerName` | `41020118` / `QUADIS LLANSÀ` |

**Dealer geo is NOT in the inventory's dealer object** (only id + name). Resolve via the
`getDealersData` roster: map `dealer.dealerId` → roster `id` → `postCode` (first 2 digits =
INE province, the primary path) + `location.gpsLatitude/Longitude` (ProvinceGeocoder
fallback) + `city` (→ municipality). `[VERIFIED]`

Only **41 distinct dealerIds** sell the 1,546 certified cars (the roster has 180 service
points; certified stock concentrates in big Nissan groups — prov 46/Valencia 421, prov
08/Barcelona 339). This is real concentration, not a parse collapse. `[VERIFIED in DB]`

### Sample car (real, pulled via free path) `[VERIFIED]`
- **NISSAN ARIYA 2025** — 12 890 km, Eléctrico, Automático, 46 250 EUR
- VIN `MQ4IH3WE3X3573338`, sku `es_NISSAN_MQ4IH3WE3X3573338`, `Nissan Certified`
- Dealer **CONCESOL AUTOMOCIÓN**, prov 29 (Málaga), muni 29070

---

## 4. Traps & gotchas (hard-won this pass)

1. **x-api-key is NOT auth.** The page's `graphqlkey="da2-jndnl5ffcrapjpra72jspszdsq"`
   (AppSync API key) returns `errorType: Unauthorized` on `getUsedCarsInventoryData`. The
   real authorizer is the **Cognito `idToken`** — mint it from the public
   `…/public-access-token` endpoint and send it as `Authorization`. `[VERIFIED]`
2. **SSR query params don't paginate.** `?page=2` / `?pageNumber=2` on the SSR
   `/all-vehicles/inventory` URL always re-renders page 1. Pagination is client-side via the
   GraphQL `pageNumber` variable only. `[VERIFIED]`
3. **`getDealersData` rejects a null location** (`Cannot read properties of null (reading
   'lat')`). Pass a Spain-centre point + large radius (2000 km) to enumerate all dealers.
   `[VERIFIED]`
4. **dealerId is NOT a province prefix.** Inventory `dealerId` (e.g. `41020014`) is a Nissan
   internal code — that dealer sits in postcode `08210`/Barcelona. Geo MUST come from the
   roster's `postCode`/`location`, never the id prefix. `[VERIFIED]`
5. **Encoding trap (same as spoticar):** dealer/city text is latin-1 mojibake over the wire
   (`LLANS\xe9` → `LLANSÀ`, `AUTOM\xd3VILES`); fuel labels carry `\xe9`/`\xed`
   (`Di\xe9sel`/`H\xedbrido`). Re-encode human text: `s.encode("latin-1").decode("utf-8")`,
   then normalize the finite fuel/gearbox vocabulary. VIN/dealerId/numeric are clean. The DB
   stores correct UTF-8 (`Diésel`, `Híbrido`, `QUADIS LLANSÁ` — verified at the byte level).
   `[VERIFIED]`
6. **Page 104 = 1 trailing car, 105 = 0.** Stop on the first empty `vehicles[]`;
   `metaData.totalCount` (1546) is the hard bound. `[VERIFIED]`

---

## 5. Connector (built, run, DB-verified)

`pipeline/platform/oem_nissan_mazda_honda_wholesale.py` — mirrors `spoticar_wholesale.py` /
`renew_wholesale.py` EXACTLY (platform entity kind=`oem_vo_portal` + per-car selling DEALER
upsert + vehicle owned by dealer + platform_listing edge + delta NEW + saved recipe + VAM
verdict + governor-wrapped fetch + breaker/record_run/auto_repair + idempotent ON CONFLICT +
BATCH unnest ingest). The only structural deltas vs spoticar:
- POST GraphQL (not GET) with a per-run Cognito token, paginating `pageNumber`.
- A pre-fetched dealer roster (`getDealersData`) maps `dealerId` → postCode/lat-lng/city;
  province = postcode prefix (primary), ProvinceGeocoder lat/lng (fallback).

```
python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104   # full ES stock
python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 5      # proof slice
```

Live full-drain result (2026-06-13): 104 pages, 1,546 cars caged (1,546 new), 1,546 edges,
1,546 VINs, 1,546 NEW events, 41 selling dealers attributed, 180-dealer roster, VAM
**TRUSTWORTHY**, breaker closed. Recipe written to
`countries/ES/recipes/CDP-ES-00-TDWVVTAF.yaml`. `[VERIFIED in DB]`

---

## 6. Vector-by-vector log (the three-brand front)

### NISSAN — ocasion.nissan.es — ✅ **THE WIN (connected)**
- Next.js SSR (`__NEXT_DATA__`) referencing `graphqlurl=gq-eu-prod.nissanpace.com/graphql`.
  AppSync GraphQL flat-enumerates all 1,546 with no cap; public Cognito token mint; full
  dealer geo via `getDealersData`. **Connected, full-drained, DB-verified TRUSTWORTHY.**
  `[VERIFIED]`

### MAZDA — mazdaselected.es — ⛔ **WALLED (not connected)**
- TLS connect **times out** to `curl_cffi impersonate=chrome131` (curl error 28, port 443,
  no response after 21 s). No clean surface reachable from this ingress; would need camoufox
  / a different network path. **Skipped per "pick whichever exposes a clean surface".**
  `[VERIFIED no reach]`

### HONDA — vehiculosdeocasion.honda.es — ⚪ **NO DATA-LAYER (not connected)**
- Server-rendered jQuery site. The `/es/ocasion-honda/buscador/modelos` "buscador" paginates
  by re-GETting the **same HTML URL** (form `action`/`data-url` = the page itself, fragment
  anchor `#result-tools-top`); no `__NEXT`/`__NUXT`/JSON API in the page. Harvesting it would
  be an **HTML/facet scrape**, not a data-layer surface — and the doctrine is "exhaust
  uncapped data-layer surfaces before any facet workaround." Nissan's pristine GraphQL wins.
  **Skipped in favour of Nissan.** `[VERIFIED no JSON surface]`

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Brand connected:** Nissan (Intelligent Choice). Mazda walled, Honda no data-layer.
- **Method:** mint Cognito idToken from the public `…/public-access-token` endpoint, then
  `POST https://gq-eu-prod.nissanpace.com/graphql` `GetUsedCarsInventoryData` via
  `curl_cffi impersonate="chrome131"`, `Authorization: <idToken>`, walk
  `usedCarsInventoryInputData.pageNumber = 1..104` (15/page), dedup on `vehiclesku`, stop on
  empty / `metaData.totalCount`. Dealer geo from `getDealersData` (postCode → INE province;
  lat/lng fallback).
- **Declared total:** **1,546** `[VERIFIED]` (`metaData.totalCount` = pages×size = DB edges =
  DB VINs, all agree).
- **Coverage proof:** full governed drain → **1,546 / 1,546 caged, VAM TRUSTWORTHY**, 0
  dupes, 0 geo-skips, breaker closed.
- **Cost:** €0. No proxy, no browser, no login, no CAPTCHA, no WAF.
- **Recipe seed (engine line, repo convention):**
  ```
  source: nissan_intelligent_choice (ocasion.nissan.es)
  engine: curl_cffi+chrome131_impersonate+aws_appsync_graphql(POST)+public_cognito_token
  access: OPEN-via-fingerprint+public-token (x-api-key Unauthorized; idToken required). is_tier1=false, t0_open
  data_surface: internal_api (AppSync GraphQL, vehicles[] 15/page)
  enumeration: POST /graphql GetUsedCarsInventoryData pageNumber=1..104 (totalCount=1546 bound)
  denominator: metaData.totalCount (1546)
  dealer: inventory dealer{dealerId,dealerName} + getDealersData roster (180; postCode+lat/lng) for geo
  ```
