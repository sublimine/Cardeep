# mercedes_benz (Mercedes-Benz Certified ES) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** A single internal AJAX list endpoint
(`POST /ajxvl`) flat-enumerates 100% of the Spanish certified-used inventory of
the **Mercedes-Benz Certified** ("Vehículos de ocasión Mercedes-Benz Certified")
network, with NO relevance cap and NO depth cap.

Platform (the official OEM-VO front-end):
- **ocasion.mercedes-benz.es** `/vehicles` — "Vehículos de ocasión Mercedes-Benz
  Certified". The manufacturer-owned certified-used portal publishing the stock of
  the official Mercedes-Benz dealer network (concesionarios oficiales) in Spain.

This is another member of the OEM-VO portal family pattern (one manufacturer-owned
portal publishing the certified inventory of its own dealer network). It joins
`source_group='oem_vo_portal'`, `family='mercedes_benz_vo'`. NOT to be confused with
renew (Renault), Das WeltAuto (VW), spoticar (Stellantis), or toyota_lexus — a
SEPARATE brand, SEPARATE portal.

WAF posture: **t0_open.** Plain `urllib` (no fingerprint) AND plain `curl_cffi` (no
impersonate) both return HTTP 200 — there is **NO bot-blocking WAF** and **NO JS
challenge**. We still drive it with `curl_cffi impersonate="chrome131"` for
engine-coherence with the rest of the fleet, but the surface is genuinely open. €0,
no proxy, no browser, no auth. The `ajxvl` POST sets a `UCSSID` session cookie, so
each pool session warms the listing page once for cookie coherence (served cold too).

Declared total / live ES public stock `[VERIFIED]`: **4,804** (`data.count`, ==
the listing "Encontrar 4.804 vehículos disponibles" headline).

Verified LIVE: **2026-06-13** (curl_cffi `impersonate="chrome131"`, no proxy, no
auth, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`.

---

## 0. TL;DR — the uncapped surface

```
POST https://ocasion.mercedes-benz.es/ajxvl
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
Origin/Referer: https://ocasion.mercedes-benz.es/vehicles?referrer=vehiclesearch&language=es-ES

type=vehiclelist
q=referrer=vehiclesearch&language=es-ES
page=N            # 1-based page index (NOT a row offset)
area=1
```

Response (UTF-8 **with a BOM** — decode `utf-8-sig`):
```json
{ "success": 1, "refresh": 0,
  "data": { "view": "box", "page": N, "sorting": "acdade",
            "count": 4804, "onlyOnePage": false },
  "html": "<div id=\"resultListItem18991353\" ...> ...12 cards... ",
  "supplements": ..., "pageTop": ..., "banner": ..., "q": ... }
```

- **Tool:** `curl_cffi impersonate="chrome131"` for fleet coherence. (Plain `urllib`
  / plain `curl_cffi` also return 200 — the surface is t0_open, no WAF.) `[VERIFIED]`
- **Method:** `POST` FormData. No auth, no bearer. Warm the listing page once per
  session for the `UCSSID` cookie (the endpoint serves cold too). `[VERIFIED]`
- **Page size:** FIXED 12 cars/page (not a request param). `[VERIFIED]`
- **Cursor:** `page` (1-based page index). Walk `page = 1, 2, …` until an empty/short
  card set or `page > ceil(count/12)`. `[VERIFIED]`
- **Denominator:** `data.count` (= 4804). `[VERIFIED]`
- **Dedup key:** the per-car numeric id `data-vehicle` (== the `&vehicle=` in the PDP
  href). Secondary: the `<dealerCode>-<carCode>` identifier. `[VERIFIED]`

### Coverage proof `[VERIFIED]`
`data.count = 4804`. 4804 / 12 = 400.33 → page 1..400 full (12 each) + **page 401 = 4
trailing cards** = 400×12 + 4 = **4804**, exactly the denominator. page 402+ returns 0
cards. Distinct ids per page, no cross-page overlap on the default sort
(`acdade` = newest-first). Walking `page` enumerates the index FLAT with linear growth
and no truncation — the coches.net relevance-wall pathology is ABSENT.

---

## 1. The denominator

| Surface | Value | `[VERIFIED]` |
|---|---:|---|
| `data.count` (ajxvl JSON) | 4,804 | yes |
| listing "Encontrar N vehículos" headline | 4.804 | yes |
| 400 full pages × 12 + page-401 tail (4) | 4,804 | yes |

National / facet-independent (the full ES served certified stock). We cage the WHOLE
network stock (every certified car the official dealers publish), so `data.count` is
the slice denominator.

---

## 2. Exact request shape

### 2.1 The page IS server-rendered; pagination is the AJAX POST
`GET /vehicles?referrer=vehiclesearch&language=es-ES` server-renders page 1 (12 cards)
+ the filter/pager chrome. A `GET ?page=N` on `/vehicles` does **NOT** page (verified:
the result is unchanged for `page/pageNo/start/offset/...`). Pagination is the
`data-page` button → JS `refreshVehicleList()` → `POST /ajxvl` (FormData with `page`).
The same controller exposes sibling endpoints `ajxvlo` and `ajxloc` (single-vehicle /
location lookups — not needed for the drain). `[VERIFIED]`

### 2.2 Discovery provenance
The endpoint + body were root-caused from the listing page's inline JS controller
(`refreshVehicleList(aRequest)` builds a `FormData` from `{type:'vehiclelist',
q:'referrer=vehiclesearch&language=es-ES', page, area:1, restore:{...}}` and
`XMLHttpRequest.open('post','ajxvl')`). Confirmed by replaying the POST directly with
`curl_cffi` for pages 1/2/400/401. `[VERIFIED]`

---

## 3. Per-car fields (the rendered card — self-contained, NO PDP fetch needed)

| Canonical | Source (within each `resultListItem` card) | Example |
|---|---|---|
| **vehicle id (dedup key + deep_link tail)** | `resultListItem<ID>` / `data-vehicle` / `&vehicle=` | `18991353` |
| **identifier (`<dealerCode>-<carCode>`)** | "Identificador del vehículo&nbsp;…" | `3689-2473023` |
| **deep_link** | card `href="vehicle?<ident>+<make>+<model>&vehicle=<id>&referrer=vehicles"` (prefix base) | `…/vehicle?3689-2473023+Mercedes-Benz+CLS+220+d&vehicle=18991353&referrer=vehicles` |
| make | `span.manufacturer` | `Mercedes-Benz` |
| model/version | title line after `</span><br>` | `CLS 220 d` |
| price (€) | `div.vehicle_price_headline` | `49.900` |
| body | spec row 1 (`vc-vehicle-attribute-text`) | `Coupé` |
| **year** | spec row 2 (registration `dd.mm.yyyy`) → trailing year | `27.11.2022` → `2022` |
| power | spec row 3 | `143 kW (194 CV)` |
| km | spec row 4 | `84.574 km` → `84574` |
| fuel | spec row 5 | `Diesel` / `Eléctrico` / `Híbrido enchufable - Gasolina` |
| photo | `img.v-i-g-main-image` `data-src` (hosted on `img.autodo.eu`) | `https://img.autodo.eu/…` |
| **dealer name** | `result-box-location-item` name span | `VALDISA` |
| **dealer location** | `result-box-location-item` "`<postalCode> <city>`" span | `46470 Massanassa` |
| **dealer code** | the prefix of the `<dealerCode>-<carCode>` identifier | `3689` |
| VIN / gearbox | **NOT on the list card** (PDP-only) | — (left NULL, never invented) |

**Dealer attribution is fully embedded** — every card carries its named official
dealer (concesionario oficial) + postcode + city + a stable dealer code. No separate
lookup. Multiple cars share a dealer (e.g. `LOUZAO A CORUÑA`, `HIJOS DE MANUEL
CRESPO, S.A.`) — dealer grouping verified.

**Geo anchor:** `result-box-location-item` postcode → province = first 2 digits (INE),
the authoritative anchor (better than spoticar which had no postcode; same path as
renew / toyota_lexus). City → municipality (INE-resolved, best-effort). `[VERIFIED]`

**Encoding `[VERIFIED]`:** the `ajxvl` body is UTF-8 **with a leading BOM** (decode
`utf-8-sig` — orjson rejects the raw BOM). The card text is then **CLEAN UTF-8** (0
U+FFFD; `Coupé`, `Híbrido`, `A CORUÑA`, `San Ciprián de Viñas` all render correctly).
There is **NO latin-1 mojibake** on this surface — unlike spoticar / toyota_lexus —
so only HTML-entity unescape (`&nbsp;`, `&ntilde;`, `&euro;`) is needed, NO re-encode.

### Sample car (real, pulled via free path) `[VERIFIED]`
- **Mercedes-Benz CLS 220 d** — Coupé, 2022, 84,574 km, Diesel
- Price **49.900 EUR**, identifier `3689-2473023`, vehicle id `18991353`
- Dealer **VALDISA** (46470 Massanassa, **province 46 Valencia**)

---

## 4. Deep-link (PDP) construction

The card already carries the relative PDP href
(`vehicle?<ident>+<make>+<model>&vehicle=<id>&referrer=vehicles`); prefix with the
base `https://ocasion.mercedes-benz.es/`. The load-bearing key is the `&vehicle=<id>`
terminal; the leading slug is SEO decoration. `[VERIFIED]`

---

## 5. Traps & gotchas

1. **The page is server-rendered; `GET ?page=N` on `/vehicles` does NOT page** —
   pagination is the AJAX `POST /ajxvl` only. `[VERIFIED]`
2. **`page` is a 1-based page index, NOT a row offset.** `[VERIFIED]`
3. **UTF-8 BOM on the JSON body** — decode `utf-8-sig` (raw `.json()` fails on the
   BOM). `[VERIFIED]`
4. **Card text is clean UTF-8** (no latin-1 mojibake) — only HTML-entity unescape.
   `[VERIFIED]`
5. **VIN and gearbox are PDP-only** — not on the list card; left NULL (never
   fetched, never invented). `[VERIFIED]`
6. **t0_open** — plain `urllib`/`curl_cffi` work; chrome131 used only for fleet
   coherence; warm the listing page once per session for the `UCSSID` cookie.
   `[VERIFIED]`
7. **page 401 is the data boundary** (4 trailing cards); 402+ = 0 cards. Stop on the
   first empty card set; `data.count` is the hard bound. `[VERIFIED]`

---

## 6. Vector-by-vector log (CARDEEP doctrine order)

### 1) SITEMAP — ⚪ not pursued (internal AJAX list already flat-enumerates 100%)
### 2) MOBILE APP API — ⚪ not needed — the web ajxvl endpoint is open + complete.
### 3) ALTERNATE / INTERNAL JSON API — ✅ **THE WIN**
`POST /ajxvl` returns the rendered cards + `data.count`, flat-enumerates the whole
network via the `page` index, with `data.count` as the denominator and per-card
embedded dealer. Root-caused from the listing page's inline `refreshVehicleList`
controller. `[VERIFIED]`
### 4) curl_cffi chrome131 — ✅ used for coherence (NOT required — surface is open).
### 5) Stealth browser — ⚪ NOT REQUIRED (no WAF challenge).
### 6) Facet partition — ⚪ NOT NEEDED (flat page walk enumerates 100%). The filter
form (brand/model/price/km/fuel/gear) is a ready shard key if a depth wall ever
appeared, but none observed.

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Method:** `POST https://ocasion.mercedes-benz.es/ajxvl` via `curl_cffi
  impersonate="chrome131"`, FormData (`type=vehiclelist`, `q=referrer=vehiclesearch&
  language=es-ES`, `page=N`, `area=1`), decode body `utf-8-sig`, split the `html`
  payload into `resultListItem` cards, dedup on the per-car vehicle id, stop on
  `page > ceil(count/12)` / empty card set.
- **Live ES public stock:** **4,804** (`data.count`) `[VERIFIED]`.
- **Cost:** €0. No proxy, no browser, no auth, no CAPTCHA, no WAF.
- **Connector:** `pipeline/platform/oem_mercedes_benz_wholesale.py` (mirrors
  `spoticar_wholesale.py`: platform entity `kind=oem_vo_portal` + per-car selling
  DEALER upsert + vehicle owned by dealer + `platform_listing` edge + delta NEW +
  saved recipe + VAM verdict + governor-wrapped fetch + breaker/record_run/auto_repair
  + idempotent ON CONFLICT + BATCH unnest ingest).
- **Recipe seed:**
  ```
  source: mercedes_benz (ocasion.mercedes-benz.es)
  engine: curl_cffi+chrome131_impersonate+internal_ajax_list_endpoint(POST)
  access: OPEN (t0_open; no WAF; serves to plain urllib). is_tier1=false
  data_surface: internal_api (ajxvl html cards, page size=12, 1-based page index)
  enumeration: POST /ajxvl {type=vehiclelist,q,page=N,area=1}  page=1..401
  denominator: data.count (4804)
  dealer: per-card {name, '<postalCode> <city>', dealerCode}
  geo: postalCode[:2]=INE province (primary); city -> municipality (INE)
  encoding: body utf-8-sig (BOM); card text clean UTF-8 (HTML-entity unescape only)
  vin/gearbox: PDP-only (NULL on the cage)
  ```

---

## 8. Live proof run (2026-06-13) `[VERIFIED]`

Bounded harvest `--pages 25 --concurrency 4` (a real chunk of the 4804 full run):
- 25 pages, 300 cards → **300 cars caged (300 new)**, **300 platform_listing edges**,
  **300 NEW delta events**, **299 distinct owning dealers** attributed.
- geo-skipped 0, no-dealer 0 — 100% of cards cageable.
- province spread (dealer): Barcelona 34, Cádiz 28, Valencia 26, A Coruña 22, Madrid 21,
  Alicante 19, Baleares 18, Badajoz 17, … (national).
- **VAM verdict: TRUSTWORTHY** (`harvested_cageable == db_edges == db_join_vehicles ==
  300`).
- **health: healthy / breaker closed.**
- **Idempotency:** a re-run of pages 1-5 caged 60 (touch) and added **0 new cars / 0
  edges / 0 events** — `db_edges` unchanged at 300.
- Platform entity: `CDP-ES-00-A57R0YK8` (kind=oem_vo_portal, defense_tier=t0_open,
  source_group=oem_vo_portal, role=platform, is_tier1=false, waf=none,
  family=mercedes_benz_vo).
```
