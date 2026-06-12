# hyundai (Hyundai Promise / Hyundai Ocasión ES) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** A single internal JSON endpoint on the
official Hyundai España certified-used portal (`www.hyundai.es/seminuevos`, a
custom **OpenCart** storefront) flat-enumerates **100%** of the Spanish
certified-used Hyundai inventory ("Hyundai Promise" / "Hyundai Ocasión") in ONE
response, with NO pagination, NO relevance cap, and NO depth cap. A SECOND
internal JSON endpoint (the concesionarios installations API) supplies the dealer
geo the car list lacks.

Platform (the official OEM-VO front-end):
- **www.hyundai.es/seminuevos** — "Hyundai Ocasión" / the "Hyundai Promise"
  certified-used programme. A single brand-owner publishing the certified-used
  inventory of its own official dealer network (concesionarios oficiales). It
  joins `source_group='oem_vo_portal'`, `family='hyundai_vo'` — the FOURTH member
  of the OEM-VO group after renew / spoticar / toyota_lexus.

WAF posture: **t1_soft.** The host sits behind **AWS CloudFront** which 403s a
stripped (non-browser-fingerprint) request ("Error from cloudfront") but serves
HTTP 200 `application/json` cleanly to `curl_cffi impersonate="chrome131"`. No JS
challenge, no proxy, no browser, no cookie warm-up, no auth, €0. The public site
is WAF-fronted → `is_tier1=TRUE`; the JSON serves to curl_cffi → `t1_soft`.

Declared total / live ES public stock `[VERIFIED]`: **2,036 cars** (the length of
the `vehiculos` list in a single `listado` response). **155** official dealer
installations in the directory; **63** of them have live certified-used stock.

Verified LIVE: **2026-06-13** (`curl_cffi impersonate="chrome131"`, no proxy, no
auth, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`.

---

## 0. TL;DR — the two uncapped surfaces

### A) The car list (the whole national stock, flat, one GET)
```
GET https://www.hyundai.es/seminuevos/index.php?route=product/vehiculo/listado
Accept: application/json, text/javascript, */*; q=0.01
X-Requested-With: XMLHttpRequest
Referer: https://www.hyundai.es/seminuevos/
```
Response: `{recibido:[], busqueda:{marcas:['91'], price:{...}}, vehiculos:[{...}, …]}`.
`vehiculos[]` carries every car FLAT — 2,036 live, NO pagination, NO offset cursor.
`busqueda.marcas == ['91']` confirms the portal is brand-pure Hyundai. `[VERIFIED]`

### B) The dealer geo (fetched ONCE, joined per car)
```
GET https://www.hyundai.es/concesionarios/index.php?route=api/installation/seminuevos
```
Response: `{status:..., instalaciones:[{...}, …]}` — **155** official installations,
each with `concesionario_id`, `name`, `phone`, `zipcode`, `zone` (province name),
`city`, `lat`, `lon`. This is the dealer-geo source the car list lacks. `[VERIFIED]`

- **Tool:** `curl_cffi impersonate="chrome131"` (REQUIRED — plain/stripped curl
  earns a CloudFront 403). `[VERIFIED]`
- **Method:** `GET` both surfaces. No auth, no bearer, no cookie warm-up. `[VERIFIED]`
- **Pagination:** NONE — the `listado` returns the whole stock in one response. `[VERIFIED]`
- **Denominator:** `len(vehiculos)` (== the portal's declared full stock). `[VERIFIED]`
- **Dedup key:** the **VIN** (`bastidor`) — 100% present, permanent. **NOT** the
  `vehiculo_id` token (it rotates every fetch — see §5.1). `[VERIFIED]`

### Coverage proof `[VERIFIED]`
A single `listado` GET returns `len(vehiculos)=2036`. Re-fetching yields the same
2,036 VINs (the set is stable; only the per-car `vehiculo_id` token rotates).
Walking is unnecessary — the response IS the full index. No relevance wall, no
depth wall. Of 2,036 cars, **1,994** join to an official installation (dealer geo
resolved) and cage; 42 carry a dealer name absent from the installations directory
and are honestly geo-skipped (no FK risk).

---

## 1. The denominator

| Surface | Value | `[VERIFIED]` |
|---|---:|---|
| `listado` → `len(vehiculos)` | 2,036 | yes |
| installations → `len(instalaciones)` | 155 | yes |
| dealers with live stock (post-join, post-geo) | 63 | yes |
| cars caged (joined + geo-resolved) | 1,994 | yes |
| cars no-dealer-skipped (name not in directory) | 42 | yes |

The denominator is national / facet-independent (the full ES served stock). We
cage every car that attributes to a concrete official dealer.

---

## 2. Exact request shape

### 2.1 Harvest endpoint (the vehicle data)
`GET …?route=product/vehiculo/listado` → `{vehiculos:[…]}`. The `vehiculos[]`
items are flat dicts (the per-car field map is §3). NO body, NO params beyond the
route. `[VERIFIED]`

### 2.2 Dealer-geo endpoint (fetched once)
`GET /concesionarios/index.php?route=api/installation/seminuevos` →
`{instalaciones:[…]}`. Indexed by phone (primary) + normalized name (fallback) for
the car→dealer join. `[VERIFIED]`

### 2.3 Discovery provenance
The `listado` route was found by probing the OpenCart `product/vehiculo` module —
the HTML listing cards are server-rendered, but `…/vehiculo/listado` returns the
same stock as raw `application/json` (1.4 MB). The dealer-geo endpoint was lifted
LIVE from the `concesionarios` page's `getInstalaciones()` AJAX call
(`url: ".../api/installation/seminuevos", dataType: 'json'`). `[VERIFIED]`

---

## 3. Per-car fields (`vehiculos[]`) + dealer join

| Canonical | Source | Example |
|---|---|---|
| **VIN (stable dedup key + deep_link anchor)** | `bastidor` | `KMHB15121SW013676` |
| price (incl VAT) | `importe_financiar` (num) / `importe` ('19.900') | `18900` / `19900` |
| km | `kilometraje` ('15.000km') | `15000` |
| year | `matriculacion` ('30-12-2024' → YYYY) | `2024` |
| make | constant `Hyundai` (brand-pure) | `Hyundai` |
| model | `modelo` ('OTROS' → NULL catch-all bucket) | `TUCSON` |
| version/trim | `version` | `1.6 T Maxx` |
| fuel | `combustible` (latin-1 repaired) | `Corriente eléctrica` |
| transmission | `transmision` (latin-1 repaired) | `Directo, sin caja de cambios` |
| photo | `imagen` (absolute S3 url) | `https://hyundai-vo.s3…/…jpg` |
| warranty (months) | `garantia` | `48` |
| **dealer name (join key)** | `concesionario` | `HERCOS MOTOR` |
| **dealer phone (join key)** | `telefono` | `942353742` |
| live PDP token (EPHEMERAL — see §5.1) | `href` → `vehiculo_id` | rotates every fetch |

### Dealer geo (from the installations join), per `instalaciones[]`
| Canonical | Source | Example |
|---|---|---|
| **dealer id (stable)** | `concesionario_id` | `71` |
| dealer name | `name` | `Abello Autotec` |
| dealer phone (join key) | `phone` | `977448333` |
| **zip → INE province (authoritative)** | `zipcode` | `43500` → province `43` |
| province name | `zone` | `Tarragona` |
| city → municipality | `city` | `Tortosa` |
| lat / lon (CORRECT keys) | `lat` / `lon` | `40.7898…` / `0.5228…` |

**Join:** car→installation by **phone** (exact digit match, primary; ~86% of
cars) → **normalized name** (exact, fallback) → **token-subset name** (fallback).
Combined ≈ 96–98% join rate; the rest are dealers genuinely absent from the
directory (geo-skipped). **Geo anchor:** `installation.zipcode[:2]` = INE province
(authoritative, the renew/toyota model); `lat`/`lon` is the `ProvinceGeocoder`
fallback. `[VERIFIED]`

### Sample car (real, pulled via the free path) `[VERIFIED]`
- **Hyundai TUCSON 1.6 T Maxx** — 2024, 15,000 km, Gasolina
- Price **27.490 EUR**, VIN `TMAJC81B1SJ552764`
- Dealer **Cobendai** (Madrid, province 28)

---

## 4. Deep-link (PDP) construction

The detail page is reachable only via the rotating `vehiculo_id` token:
`…?route=product/vehiculo/detalle&vehiculo_id={token}`. Because that token is
EPHEMERAL (§5.1), the **canonical, STABLE deep_link is VIN-anchored**:
```
https://www.hyundai.es/seminuevos/#vin={bastidor}
```
This keeps the `(entity_ulid, deep_link)` vehicle identity permanent so re-runs are
idempotent (verified: a second full drain adds 0 new cars, 0 events). `[VERIFIED]`

---

## 5. Traps & gotchas

1. **`vehiculo_id` token ROTATES every fetch.** `[VERIFIED]` — 0/2036 tokens
   stable across two consecutive `listado` GETs (same VINs, all-new tokens). It is
   an ephemeral per-response session token, NOT a car id. Using it as the dedup
   key re-cages the WHOLE stock as "new" every run. **Dedup + deep_link MUST anchor
   on the VIN (`bastidor`)**, which is 100% present and permanent.
2. **Dealer geo is SPLIT off the car list.** The `listado` carries only dealer
   NAME + phone — no zip/city/geo. Fetch the installations API once and join.
   `[VERIFIED]`
3. **lat/lon swap.** Installations carry a correct `lat`/`lon` pair AND a SWAPPED
   `latitud`/`longitud` pair (the site's own JS compensates:
   `lat: parseFloat(inst['longitud'])`). Read `lat`/`lon` (Spain lat 36..44, lon
   -9..4). `[VERIFIED]`
4. **latin-1 mojibake on ALL human text** (`Corriente el�ctrica`, `autom�tico`,
   `L�Aldea`) — repair per field with `s.encode('latin-1').decode('utf-8')`. VIN,
   numeric and the token are clean. `[VERIFIED]`
5. **`modelo == 'OTROS'`** is the portal's catch-all bucket, not a real model →
   stored as NULL. `[VERIFIED]`
6. **CloudFront 403 to stripped curl** — `impersonate="chrome131"` REQUIRED
   (t1_soft). `[VERIFIED]`
7. **No private sellers** — OEM certified-used portal; every car belongs to an
   official Hyundai dealer. `[VERIFIED]`

---

## 6. Vector-by-vector log (CARDEEP doctrine order)

### 1) SITEMAP — ⚪ not pursued (internal JSON already flat-enumerates 100%)
### 2) MOBILE APP API — ⚪ not needed — the web `listado` JSON is complete + open.
### 3) ALTERNATE / INTERNAL JSON API — ✅ **THE WIN**
`GET …/route=product/vehiculo/listado` returns the WHOLE national stock flat in one
response (`vehiculos[]`, 2036), with `len(vehiculos)` the denominator and the VIN
the dedup key. The dealer geo comes from `GET …/api/installation/seminuevos`
(`instalaciones[]`, 155). Both discovered via the OpenCart module + the
concesionarios page's AJAX call. `[VERIFIED]`
### 4) curl_cffi chrome131 — ✅ **REQUIRED** (stripped curl → CloudFront 403).
### 5) Stealth browser — ⚪ NOT REQUIRED (no JS challenge; chrome131 JA3 passes).
### 6) Facet partition — ⚪ NOT NEEDED (one flat response enumerates 100%).

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Method:** `GET https://www.hyundai.es/seminuevos/index.php?route=product/vehiculo/listado`
  via `curl_cffi impersonate="chrome131"` → `vehiculos[]` (whole national stock,
  one flat response); dealer geo via
  `GET …/concesionarios/index.php?route=api/installation/seminuevos` →
  `instalaciones[]`, joined per car by phone+name; province = `zipcode[:2]`
  (lat/lon fallback); **dedup + deep_link anchored on the VIN** (`bastidor`).
- **Live ES public stock:** **2,036** cars; **1,994** caged (dealer-attributed +
  geo-resolved); **63** dealers with stock / 155 installations. `[VERIFIED]`
- **Cost:** €0. No proxy, no browser, no auth, no CAPTCHA.
- **Idempotency:** re-run adds 0 new cars / 0 events (VIN-anchored). `[VERIFIED]`
- **VAM:** TRUSTWORTHY (harvested_cageable == db_edges == db_join_vehicles ==
  1,994). `[VERIFIED]`
- **Recipe seed:**
  ```
  source: hyundai
  engine: curl_cffi+chrome131_impersonate+internal_opencart_json_api(GET)
  access: OPEN-via-fingerprint (CloudFront 403s stripped curl; chrome131 passes). is_tier1=true, t1_soft
  data_surface: internal_api (listado vehiculos[], single flat response)
  enumeration: GET route=product/vehiculo/listado  -> vehiculos[] (no pagination)
  denominator: len(vehiculos) (2036)
  dealer_geo: GET route=api/installation/seminuevos -> instalaciones[] (155); join by phone+name
  geo: installation.zipcode[:2]=INE province (primary); lat/lon (fallback)
  dedup_key: bastidor (VIN) — NOT the rotating vehiculo_id token
  ```
