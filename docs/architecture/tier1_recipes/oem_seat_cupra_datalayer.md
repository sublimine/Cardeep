# seat_cupra (CUPRA Approved ES) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** A single internal JSON API (the **SEAT/CUPRA
"VTP" — Vehicle Trading Platform — REST service**, tenant `cuesgwb` =
CUPRA-ES-Gebrauchtwagen) flat-enumerates 100% of the Spanish certified-used
("CUPRA Approved") inventory of the official CUPRA dealer network, with NO
relevance cap and NO depth cap.

## Brand-front split (why this is SEPARATE from Das WeltAuto)

The `seat_cupra` brand front resolves into TWO distinct surfaces; they are handled
by two different connectors and there is **no double-coverage**:

- **SEAT half → ALREADY COVERED by Das WeltAuto.** SEAT's own used-car portal
  "SEAT Ocasión" (`www.seat.es`) **redirects into Das WeltAuto**
  (`www.dasweltauto.es/esp/seat` — page title "SEAT de Ocasión y Segunda Mano |
  SEAT"). SEAT certified-used IS Das WeltAuto. It is harvested by
  `pipeline.platform.dasweltauto_wholesale` (`family='vw_group'`). We do NOT
  re-harvest it here. `[VERIFIED]` (search-result title + Das WeltAuto docstring
  enumerating "Volkswagen + SEAT + Škoda + CUPRA + Audi").
- **CUPRA half → THIS connector (distinct first-party portal).** CUPRA runs its
  OWN "CUPRA Approved" certified-used surface on `cupra.com`
  (`/es-es/localizador-stock?t_cartype=used`), backed by a DISTINCT internal API
  (the VTP `cuesgwb` tenant). That surface serves **100% `manuf=CUPRA`** cars —
  SEAT is NOT mixed in. A genuinely separate OEM-VO portal. `[VERIFIED]` (288-car
  sample across 3 pages = 100% CUPRA).

It joins `source_group='oem_vo_portal'`, `role='platform'`, `kind='oem_vo_portal'`,
`family='seat_cupra_vo'`, the FIFTH member of the OEM-VO group (after renew,
spoticar, Das WeltAuto, toyota_lexus).

## The surface

Platform front-end: `www.cupra.com/es-es/localizador-stock?t_cartype=used`
("CUPRA Approved" / "coches de ocasión certificados"). A Web-Components SPA
(`x-pattern=cuprawebfe`) that calls ONE internal JSON API:

```
GET https://vtpapi.seat.com/restapi/v1/cuesgwb/search/car
```

Pagination and sort ride in **REQUEST HEADERS**, not query params:

| header | value | meaning |
|---|---|---|
| `x-pattern` | `cuprawebfe` | CUPRA web front-end tenant (required by the edge gate) |
| `x-page` | `N` | 1-based page index |
| `x-page-items` | `96` | page size — default SPA sends 12; **API HONOURS ≥96** `[VERIFIED]` |
| `x-sort` | `DATE_OFFER` | sort field (SPA default; STABLE for a full crawl) |
| `x-sort-direction` | `DESC` | sort direction |

No query string is needed for the full used set. No body. No proxy, no browser, no
cookie warm-up, no auth, €0.

## WAF posture: **t1_soft** (TLS-fingerprint edge gate)

- Plain `urllib` (default TLS) → **HTTP 403 Forbidden** at the edge.
- `curl_cffi impersonate="chrome131"` → **HTTP 200 `application/json`**.

`[VERIFIED]` both directions live. The host fronts with a Traefik ingress
(`traefik-ing` cookie) + a Java backend (`JSESSIONID`); no recognizable commercial
WAF header (no Cloudflare/Akamai/Imperva signature) → `website_waf='other'`. The
gate fingerprints the TLS/JA3, so a real Chrome fingerprint passes cleanly with no
JS challenge → `defense_tier='t1_soft'`, `is_tier1=TRUE`. No cookie warm-up needed
(the bare GET succeeds cold).

## Denominator (authoritative total)

The total lives in a **RESPONSE HEADER**, not the JSON body:

```
x-result-number: 1323
```

`[VERIFIED]` it equals the `criteria.search.criterias[t_drive].possibleItems.number`
facet sum (1156 + 85 + 82 = 1323). The `t_drive` facet is the reliable cross-check
(every car has a drive; the `t_color` facet undercounts because some cars lack a
colour code).

Live ES public CUPRA Approved stock `[VERIFIED]` **2026-06-13: 1,323 cars.** Small,
FLAT index → full drain = `ceil(1323/96) = 14` pages, in reach in a single run.

## Response shape

```
{
  "criteria":     { "key":"criteria", "search": { "criterias": [ {criteria, possibleItems:[{key, number}]} ... ] } },
  "results":      { "result": { "cars": [ { "key", "href", "car": {...} } x12-96 ] } },
  "combinations": { ... }                       // facet combination metadata (unused)
}
```

Boundary behaviour `[VERIFIED]`: page `ceil(total/size)` returns the trailing
remainder; the next page returns NO `cars` key (empty). The drain stops on the first
empty page; `x-result-number` is the hard bound.

## Field map (per `results.result.cars[].car`)

| field | source path |
|---|---|
| `listing_ref` / dedup key | `car.carid` (e.g. `ESP0A211115431200` — stable, clean) |
| `deep_link` | constructed `https://www.cupra.com/es-es/localizador-stock/coche/{carid}` (no url in payload) |
| `make` | `car.items[key='manuf'].value` (always `CUPRA`) |
| `model` | `car.items[key='model'].value` |
| `title` | `car.items[key='localCarTitle'].value` (fallback `cartitle`) |
| `year` | `car.items[key='modelyear'].value` (fallback `initialreg`[:4]) |
| `km` | `car.items[key='mileage'].value` — Spanish-formatted `"38.621"` → strip thousands dots → `38621` |
| `price` | `car.items[key='prices'].values[key='sale'].raw_value` (EUR, clean float) |
| `fuel` | `car.hypermediatechdata..data[key='fuel'].techData.values[0].key` → Spanish label (fixed map) |
| `transmission` | `car.items[key='gear'].value` (`Cambio automático DSG` / `Cambio manual`) |
| `photo` | `car.images[].imageGroup.images[].image.href` (first absolute http(s); hosted on `vtpimages.audi.com`) |
| `vin` | **NOT PRESENT** on the search surface → `NULL` (would require a PDP fetch; not worth it) |
| `dealer` | `car.hypermediadealer.dealer { key, items{city,name,phone,zip,street,position{latitude,longitude}} }` |

Fuel vocabulary (techdata `fuel` KEY → Spanish label, fixed verified map):
`PETROL`/`PURE_PETROL`→Gasolina, `DEPLETING_PETROL`→Híbrido (MHEV),
`SUSTAINING_PETROL`→Híbrido enchufable (PHEV), `DIESEL`/`PURE_DIESEL`→Diésel,
`PURE_ELECTRICAL`/`ELECTRICAL`→Eléctrico.

## Geo anchor (zip-first, the renew/toyota_lexus model)

Each dealer carries BOTH a `zip` (`08040`) and a `position{latitude,longitude}`
(`41.33674, 2.13062`) — `[VERIFIED]` 288/288 dealers carry both. Province =
`zip[:2]` (INE province, authoritative); lat/lng → `ProvinceGeocoder.nearest_province`
fallback when the zip is missing/malformed. Municipality best-effort from the city
literal. `dealer.key` (e.g. `ESP0A211`) is the stable per-dealer id and `source_ref`.

## Encoding

**CLEAN UTF-8 — no mojibake on this surface** (unlike spoticar/toyota_lexus). The
accented bytes are genuine UTF-8 (`automático` = `c3 a1`, `Híbrido`, `A Coruña` all
decode correctly via `resp.content.decode("utf-8")`). `_fix()` is kept only as a
defensive no-op guard (a latin-1 round-trip that returns already-correct UTF-8
unchanged), for field-pipeline parity with the sibling connectors. `[VERIFIED]`
byte-level: `Híbrido` stored as `b'H\xc3\xadbrido'` (í = U+00ED).

## Multi-axis classification (migrations/0016)

```
defense_tier = 't1_soft'        (403 to plain urllib; 200 to chrome131; no JS challenge)
source_group = 'oem_vo_portal'  (fifth member of the group renew opened)
role         = 'platform'
kind         = 'oem_vo_portal'  (platform entity ontology kind)
is_tier1     = TRUE             (edge gate fronts the public API)
family       = 'seat_cupra_vo'
website_waf  = 'other'          (Traefik-fronted TLS gate; no commercial WAF signature)
```

## E2E proof (full drain, live, 2026-06-13)

`python -m pipeline.platform.oem_seat_cupra_wholesale --pages 14 --concurrency 4`

| metric | value |
|---|---|
| declared full (x-result-number) | 1,323 |
| pages fetched | 14 |
| cars caged | **1,323** (1,323 new) |
| distinct official CUPRA dealers | **87** |
| platform_listing edges | 1,323 |
| no-dealer / geo / dup / private skipped | 0 / 0 / 0 / 0 |
| NEW delta events | 1,323 |
| VAM verdict | **TRUSTWORTHY** (harvested_cageable = db_edges = db_join_vehicles = 1,323) |
| data completeness | price/year/km/fuel/transmission/photo = 1,323/1,323 (100%) |
| price range | €19,990 – €58,900 (avg €32,916) |
| health / breaker | healthy / closed |
| idempotency re-run | 0 new cars, 0 edges, 0 events, 87 owners unchanged |

Verified LIVE: **2026-06-13** (curl_cffi `impersonate="chrome131"`, no proxy, no
auth, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read, or DB
> row read) unless tagged `[ASSUMED]`.
