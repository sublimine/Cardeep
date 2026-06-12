# toyota_lexus (Toyota Plus + Lexus Select ES) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** A single internal JSON API (the **USC — Used
Stock Cars — Web Components** backend, shared by Toyota Europe across all its
markets) flat-enumerates 100% of the Spanish certified-used inventory of BOTH the
Toyota network ("Toyota Plus" / Toyota Approved Used) and the Lexus network
("Lexus Select"), with NO relevance cap and NO depth cap.

Platforms (the two official OEM-VO front-ends, ONE backend):
- **toyota.es** `/coches-segunda-mano` — "Toyota Ocasión" / Toyota Plus.
- **lexusauto.es** `/lexus-seminuevos` — "Lexus Select" seminuevos certificados.

Both SPAs embed the same `usc-webcomponents.toyota-europe.com` web component and
call the same `POST /v1/api/usedcars/results/es/es` endpoint, differing only by the
`?brand=` query param (`toyota` vs `lexus`). This is the SECOND-after-spoticar
member family pattern: one manufacturer-owned portal group publishing the certified
inventory of its own dealer network. It joins `source_group='oem_vo_portal'`,
`family='toyota_lexus_vo'`.

WAF posture: **t0_open.** The API sits behind AWS CloudFront (`x-amz-cf-id`) but
has **NO bot-blocking WAF** — it serves HTTP 200 `application/json` to *plain
urllib* (no fingerprint needed). We still drive it with `curl_cffi
impersonate="chrome131"` for engine-coherence with the rest of the fleet, but the
surface is genuinely open. €0, no proxy, no browser, no auth, no cookie warm-up.

Declared total: ~the two networks combined. Live ES public stock `[VERIFIED]`:
- **Toyota network: 3,274** (`totalResultCount`, `?brand=toyota`, no filter).
  Of these, `usedCarBrand=38`(Toyota)=3,213 + a long tail of trade-ins of other
  makes the Toyota dealers also sell (Kia/VW/etc., 1–7 each).
- **Lexus network: 562–584** (`totalResultCount`, `?brand=lexus`; `usedCarBrand=22`).
  Small live jitter run-to-run.
- **Combined ≈ 3,840.**

Verified LIVE: **2026-06-13** (curl_cffi `impersonate="chrome131"`, no proxy, no
auth, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`.

---

## 0. TL;DR — the uncapped surface

```
POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}
Content-Type: application/json

{
  "uscEnv": "production",
  "filters": [],                    // empty = whole network; or [{"filterId":"usedCarBrand","valueIds":["38"]}]
  "filterContext": "used",
  "offset": 0,                      // pagination cursor (rows, not pages)
  "resultCount": 50,                // page size (configurable; 11 is the SPA default, ≥100 works)
  "sortOrder": "published",
  "distributorCode": "9424M",       // ES distributor; same for both brands
  "hasContentBlock": false
}
```

- **Tool:** `curl_cffi impersonate="chrome131"` for fleet coherence. (Plain urllib
  also returns 200 — the API is t0_open, no WAF.) `[VERIFIED]`
- **Method:** `POST` JSON body. No auth, no bearer, no cookie warm-up. `[VERIFIED]`
- **Page size:** `resultCount` in the body governs it. The SPA sends 11; the API
  honours 24/48/100 cleanly. `[VERIFIED]`
- **Cursor:** `offset` (ROW offset, not page index). Walk `offset = 0, N, 2N, …`
  until `offset >= totalResultCount` or an empty `results[]`. `[VERIFIED]`
- **Denominator:** `totalResultCount` (top-level). Also `totalPageCount` (=
  ceil(total / resultCount)). `[VERIFIED]`
- **Dedup key:** `results[].id` (per-car UUID, stable + globally unique). `[VERIFIED]`

### Coverage proof `[VERIFIED]`
`brand=toyota` no-filter → `totalResultCount=3274`; `brand=lexus` → `562–584`.
Both brand-facet sums (`aggregations.usedCarBrand`) reconcile to the headline
count (Toyota: 38→3213 + tail = 3274). Walking `offset` enumerates the index flat
with linear growth and no truncation — the coches.net relevance-wall pathology is
ABSENT. A re-sweep dedup on `id` reaches ~100%.

---

## 1. The denominator

| Surface | Toyota | Lexus | `[VERIFIED]` |
|---|---:|---:|---|
| `results` → `totalResultCount` (no filter) | 3,274 | 562–584 | yes |
| `aggregations.usedCarBrand` Σ doc_count | 3,274 | 562 | yes |
| brand-specific bucket (`38`=Toyota / `22`=Lexus) | 3,213 | 562 | yes |

The denominator is national / facet-independent (the full ES served stock per
network). The Toyota network count includes trade-ins of other makes; the
brand-38 bucket is the pure-Toyota subset. We cage the WHOLE network stock
(every car the dealers sell), so `totalResultCount` is the slice denominator.

---

## 2. Exact request shape

### 2.1 Harvest endpoint (the vehicle data)
```
POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={brand}
```
Top-level response keys: `errorLogs, results, totalPageCount, aggregations,
totalResultCount, esQuery`. `results[]` carries the raw per-car documents (page
size = body `resultCount`). `[VERIFIED]`

### 2.2 Pagination
`offset` is a ROW offset. `offset += resultCount` each page; stop on
`offset >= totalResultCount` OR empty `results[]`. `[VERIFIED]`

### 2.3 Discovery provenance
The endpoint + body were captured LIVE from the `lexusauto.es/lexus-seminuevos`
SPA via the network panel (`POST .../usedcars/results/es/es?brand=lexus`, body
carrying `filters:[{usedCarBrand:["22"]}]`, `distributorCode:"9424M"`). The
`toyota.es` SPA issues the identical POST with `?brand=toyota`. `[VERIFIED]`

---

## 3. Per-car fields (`results[]` — self-contained, NO PDP fetch needed)

| Canonical | Source field | Example |
|---|---|---|
| **id (stable, dedup key + deep_link tail)** | `id` (UUID) | `728b1fb5-2281-4184-98de-06d2fb7c0b3f` |
| **VIN** | `vin` | `YARKBAC3300013464` |
| plate | `licensePlate` | `1085LWX` |
| **price (incl VAT)** | `price.sellingPriceInclVAT` | `20800` |
| km | `mileage.value` | `59752` |
| year | `product.modelYear` (fallback `history.registrationDate[:4]`) | `2023` |
| make | `product.brand.description` | `Toyota` / `Lexus` |
| model | `product.model.description` | `Yaris` / `UX` |
| version/trim | `product.versionName` | `5P Style 120H e-CVT` |
| fuel | `product.engine.marketingFuelType.description` (`displayFuelType`) | `Híbrido` |
| transmission | `product.transmission.transmissionType.description` | `Automático` |
| photo | `images[0].url` (protocol-relative `//…`) | `//used-car-publisher…JPEG` |
| body / doors / seats | `product.bodyType` / `product.doors` / `product.seats` | `5P` / `5` / `5` |
| UC program | `ucProgram.description` | `Toyota Approved Used` |
| **dealer id** | `dealer.id` (== `dealerId`) | `00CD0-E9EAD-16789-E8800-01260-3` |
| **dealer name** | `dealer.name` | `Compostela Móvil, S.A.U. …` |
| dealer city / zip / region | `dealer.address.{city,zip,region}` | `Teo (Santiago)` / `15866` / `LA CORUÑA` |
| dealer lat/lon | `dealer.geoLocation.{lat,lon}` | `42.838333,-8.582776` |
| dealer website / phone / email | `dealer.{website,phoneNumber,email}` | toyota.es/instalaciones/… |

**Dealer attribution is best-in-class & fully embedded** — every car carries its
named official dealer (concesionario oficial) with id, full postal address, zip,
geo, website, phone. No separate lookup.

**Geo anchor:** `dealer.address.zip` (postcode) → province = first 2 digits (INE).
This is the primary, authoritative anchor (better than spoticar, which had no
zip). Fallback: `dealer.geoLocation.lat/lon` → `ProvinceGeocoder.nearest_province`.

**Encoding trap `[VERIFIED]`:** human-text fields are latin-1 mojibake over the
wire (`Gris �gata`="Gris ágata", `LA CORU�A`="LA CORUÑA", `Autom�tico`,
`H�brido`). Repair every text field: `s.encode("latin-1").decode("utf-8")`.
Numeric/id fields (`id`, `vin`, `price`, `mileage`) are clean.

### Sample car (real, pulled via free path) `[VERIFIED]`
- **Toyota Yaris 5P Style 120H e-CVT** — 2023, 59,752 km, Híbrido Gasolina, Automático
- Price **20.800 EUR**, VIN `YARKBAC3300013464`, plate `1085LWX`
- Dealer **Compostela Móvil, S.A.U.** (Teo / Santiago de Compostela, zip 15866,
  La Coruña), geo 42.838333,-8.582776
- id `728b1fb5-2281-4184-98de-06d2fb7c0b3f`

---

## 4. Deep-link (PDP) construction

The `results[]` record carries NO PDP URL field. The SPA builds the PDP path from
the record:

```
{portal_base}/{portal_path}/pdp.{brand}-{model}-{modelYear}-{bodyslug}-{transmission}-{fuel}-{id}
```
- Toyota base: `https://www.toyota.es/coches-segunda-mano`
- Lexus base: `https://www.lexusauto.es/lexus-seminuevos`
- e.g. (Lexus, captured live):
  `…/lexus-seminuevos/pdp.lexus-ux-2025-suv-automatico-hibrido-fa76e244-9630-4762-8748-5bacc6c0da46`

The terminal UUID (`id`) is the load-bearing key; the leading slug is SEO
decoration. We build the canonical PDP path with a normalized slug + the id so the
deep_link is stable, unique, and resolvable. `[VERIFIED pattern]`

---

## 5. Traps & gotchas

1. **`resultCount` in the body is the page size, NOT a sanity echo.** The SPA's 11
   is just its viewport batch; the API honours larger values. `[VERIFIED]`
2. **`offset` is a ROW offset, not a page index.** `offset += resultCount`.
   `[VERIFIED]`
3. **`brand=toyota` returns the whole network** including non-Toyota trade-ins
   (filter `usedCarBrand=38` for pure Toyota; we cage the whole network — every
   car the official dealers sell is in scope). `[VERIFIED]`
4. **No PDP url in the payload** — construct it (§4). `[VERIFIED]`
5. **latin-1 mojibake on ALL human-text** — repair per field (§3). `[VERIFIED]`
6. **t0_open** — plain curl works; chrome131 used only for fleet coherence.
   `[VERIFIED]`

---

## 6. Vector-by-vector log (CARDEEP doctrine order)

### 1) SITEMAP — ⚪ not pursued (internal API already flat-enumerates 100%)
### 2) MOBILE APP API — ⚪ not needed — the web USC JSON API is open + complete.
### 3) ALTERNATE / INTERNAL JSON API — ✅ **THE WIN**
`POST /v1/api/usedcars/results/es/es?brand={brand}` returns raw per-car documents,
flat-enumerates the whole network via `offset`, with `totalResultCount` as the
denominator and per-car embedded dealer. Discovered via the live SPA network
panel (Playwright capture of the lexusauto.es seminuevos page). `[VERIFIED]`
### 4) curl_cffi chrome131 — ✅ used for coherence (NOT required — API is open).
### 5) Stealth browser — ⚪ NOT REQUIRED (no WAF challenge).
### 6) Facet partition — ⚪ NOT NEEDED (flat offset walk enumerates 100%). The
`usedCarBrand` / model / dealer aggregations are ready shard keys if a depth wall
ever appeared, but none observed.

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Method:** `POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}`
  via `curl_cffi impersonate="chrome131"`, JSON body (`filters:[]`,
  `filterContext:"used"`, `distributorCode:"9424M"`), walk `offset` by `resultCount`,
  dedup on `results[].id`, stop on `offset >= totalResultCount` / empty.
- **Live ES public stock:** Toyota **3,274** + Lexus **562–584** ≈ **3,840** `[VERIFIED]`.
- **Cost:** €0. No proxy, no browser, no auth, no CAPTCHA, no WAF.
- **Recipe seed:**
  ```
  source: toyota_lexus
  engine: curl_cffi+chrome131_impersonate+usc_internal_json_api(POST)
  access: OPEN (t0_open; CloudFront, no WAF; serves to plain curl). is_tier1=false
  data_surface: internal_api (USC results[], page size=resultCount, offset cursor)
  enumeration: POST /v1/api/usedcars/results/es/es?brand={brand}  offset=0..totalResultCount
  denominator: totalResultCount  (==Σ aggregations.usedCarBrand)
  dealer: per-car dealer{} (id, name, address+zip, geo, website, phone)
  geo: dealer.address.zip[:2]=INE province (primary); geoLocation.lat/lon (fallback)
  ```
