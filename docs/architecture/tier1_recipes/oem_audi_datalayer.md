# Audi Selection :plus — UNCAPPED Data-Layer Recipe (full ES Audi used stock, no relevance cap)

Status: **UNCAPPED, FULLY-OPEN SURFACE FOUND.** The serving gateway flat-enumerates
100% of the ES Audi certified-used inventory with NO relevance/depth cap, behind NO
WAF, gated only by a public static API token.
Platform: **audi.es** "Audi Selection :plus" (the brand's own single-brand OEM-VO portal),
served by Audi's GLOBAL **SCS — Stock Car Search** JSON gateway at **scs.audi.de**.
Defense posture: **t0_open** — even *plain `python-urllib`* (no TLS impersonation) gets
HTTP 200; there is no `server`/`cf-ray`/WAF header. The ONLY gate is a public static
`token` header (`FJ54W6H`, the page's envConfig `scs.apiKey`); without it the API
returns `401 Token is missing or invalid`.
Declared ES Audi used stock: **3,798** `[VERIFIED]` — the API's own `totalCount`, echoed
by the SCS response header and equal to the sum of the carline-facet counts.
Verified LIVE: **2026-06-13** (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy,
no browser, no auth, no cookie warm-up, €0). Full drain run end-to-end: 3,798/3,798
cars caged, VAM verdict **TRUSTWORTHY**, 56 official Audi dealers attributed.

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`. The connector is `pipeline/platform/oem_audi_wholesale.py`,
> mirroring the proven `spoticar_wholesale.py` OEM-VO template exactly.

> **VW-Group note.** Audi is part of the VW Group, whose generic multi-brand
> certified-used portal **Das WeltAuto** already lives in the cage (family `vw_group`).
> THIS is a SEPARATE surface: Audi's OWN single-brand "Selection :plus" portal, with its
> own dealer network and its own clean JSON data layer (Das WeltAuto = AEM HTML SSR by
> province slug; Audi Selection :plus = first-party SCS JSON gateway). Family `audi_vo`.

---

## 0. TL;DR — the uncapped surface (THE win)

The OneAudi/NEMO (AEM) SPA's VTP (Vehicle Trading Platform) feature-app calls Audi's
**global SCS Stock Car Search JSON API**. The `search/filter` endpoint walks the **entire
3,798-vehicle ES Audi-used index** as a flat `from`/`size` cursor with **no relevance cap
and no depth cap**. Harvest = walk `from=0,96,192,…` with `size=96`, dedup on `carId`.

```
GET https://scs.audi.de/api/v2/search/filter/esuc/es?from={N}&size=96&sort=prices.retail:asc
```

- **Market / language:** `esuc` (ES **U**sed **C**ars) / `es`. `[VERIFIED]`
- **Tool:** `curl_cffi` with `impersonate="chrome131"` (NOT required for access — plain
  urllib also gets 200 — but used for consistency with the rest of the fleet). `[VERIFIED]`
- **Method:** `GET`. No body. **REQUIRED header: `token: FJ54W6H`** (public static api
  key from the page's `envConfig.scs.apiKey`; 401 without it). No cookie warm-up. `[VERIFIED]`
- **Page size:** `size` honored up to **100** (verified 24/48/96/100 all returned in
  full). We harvest at **`size=96`** → the 3,798-car index in **~40 requests**. `[VERIFIED]`
- **Cursor:** integer `from` offset. `totalCount` (3798) bounds the run; the last data
  page is `from=3744` (54 trailing cars); **`from>=totalCount` returns `HTTP 400`** — the
  clean data boundary the connector treats as a normal stop. `[VERIFIED]`
- **Sort:** `prices.retail:asc` (the live buscador's default). `[VERIFIED]`

Minimal headers that return HTTP 200 `application/json;charset=UTF-8`:

```
Accept: application/json
token: FJ54W6H
Referer: https://www.audi.es/
Origin: https://www.audi.es
```

### Coverage proof (the load-bearing evidence) `[VERIFIED]`
Walked `from=0..3744` (size=96) LIVE in a single full drain: **40 pages HTTP 200**,
**3,798 unique `carId`** caged (0 cross-page dupes, 0 dealer-parse skips, 0 geo skips),
`from=3840` returned `HTTP 400` (past `totalCount`) → boundary reached. **3,798 cars =
100% of the declared `totalCount` in one pass.** No relevance truncation, no depth wall.
A re-run added **0** new cars / 0 edges / 0 events (idempotent ON CONFLICT). `[VERIFIED]`

---

## 1. The surface discovery trail

1. `audi.es/es/buscador-de-stock-de-ocasion` (the "Audi Selection :plus" buscador) is a
   OneAudi/NEMO AEM SPA. The page HTML embeds the VTP feature-app config (`fa-vtp-plp`,
   `fa-vtp-configuration`) and an `envConfig.scs` block with
   `baseUrl: https://scs.audi.de/api/`, `defaultApiVersion: v1`, `apiKey: FJ54W6H`. `[VERIFIED]`
2. Driving the live page (Playwright) shows the PLP app issuing the real XHR:
   `GET scs.audi.de/api/v2/search/filter/esuc/es?size=12&sort=prices.retail:asc` with the
   `apiKey` carried as a **`token` HEADER** (not a query param), CORS
   `access-control-allow-origin: *`. `[VERIFIED]`
3. Direct probe confirms market `esuc`/lang `es`, `from`/`size` pagination, `totalCount`,
   and the `vehicleBasic[]` car array with a fully embedded per-car `dealer` object. `[VERIFIED]`

---

## 2. Response shape & field map (the `vehicleBasic[]` car)

Top-level keys: `totalCount`, `vehicleBasic[]` (the cars, `size` per page), `groups`
(filter facets — `groups.carline` counts sum to `totalCount`), `header` (echoes
`from`/`size`/`market`/`sort`), `items` (facet counts, NOT cars — do not parse as cars).

| Cardeep field   | SCS path                                                              |
|-----------------|-----------------------------------------------------------------------|
| `deep_link`     | `weblink` (absolute `entry.audi.com` PDP URL)                         |
| `listing_ref`   | `carId` (e.g. `ESP05346128322740`; stable id + dedup key)            |
| `vin`           | NOT exposed on the listing surface → `NULL`                           |
| `make`          | constant `"Audi"` (`brand.code='aa'`; single-brand portal)           |
| `model`         | `symbolicCarline.description` (leading `"Audi "` stripped); fallback `model.description` |
| `version`       | `trimline.description`                                                 |
| `year`          | `modelYear`                                                           |
| `km`            | `used.mileage`                                                       |
| `price`         | `typedPrices[type=retail].amount` (fallback `type=regular`); EUR     |
| `fuel`          | `fuel.code` D/B/H/E → Diésel/Gasolina/Híbrido/Eléctrico (see §3)      |
| `transmission`  | `gearType.code` gear-type.automatic/manual → Automático/Manual (see §3) |
| `photo_url`     | `used.pictureUrls[0]` (fallback `pictures[0].url`, skip `type=fallback`) |
| **dealer**      | `dealer{ id, name, city, street, zipCode, geoLocation{lat,lon} }`     |
| dealer province | `dealer.zipCode[:2]` = INE province (authoritative); `geoLocation` lat/lon → ProvinceGeocoder as fallback |
| dealer muni     | `dealer.city` → INE municipality (best-effort)                       |
| dealer id       | `dealer.id` (stable Audi dealer no., e.g. `05346`) — source_ref + cdp_code anchor |

Every car is `type='U'` (used) and `businessModel.code='dealer_stock'` — an OEM
certified-used portal, **NO private sellers**. Field completeness across the full 3,798:
price/year/km/fuel/transmission/photo/dealer-id/zipCode = **100%, zero nulls**. `[VERIFIED]`

---

## 3. Traps & gotchas

- **`token` header is REQUIRED** (401 without it). It is a **public static api key**
  embedded verbatim in the page, NOT a secret/credential. `[VERIFIED]`
- **`from>=totalCount` → HTTP 400** (`"400 - Bad Request"`), not an empty 200. The
  connector treats a 400 *at/after the expected tail* (`from >= totalCount`) as the clean
  data boundary; any other non-200 is a real failure the breaker catches. `[VERIFIED]`
- **`items[]` is filter-facet counts, NOT cars.** The cars are in `vehicleBasic[]`. Parsing
  `items` as cars would cage facet rows. `[VERIFIED]`
- **`gearBox` ≠ transmission.** `gearBox` is the gear *ratios* ("5 vel.", "7 vel."); the
  Manual/Automático axis is **`gearType`**. Use `gearType`. `[VERIFIED]`
- **Encoding — NO corruption (display artifact only).** SCS serves valid UTF-8
  (`content-type: application/json;charset=UTF-8`); accented values store as clean
  codepoints (`Diésel`=U+00E9, `Málaga`=U+00E1, `Alcorcón`=U+00F3). A Windows cp1252
  console renders these as `�` in stdout, but the DB bytes are correct (verified:
  **0 rows with U+FFFD** in the caged 3,798). The connector additionally prefers the
  accent-free **`*.code`** companion mapped to a fixed Spanish label for fuel/transmission —
  a robustness measure (immune to any future source encoding drift), identical to the
  spoticar fix. `[VERIFIED]`
- **VIN absent on the listing surface** → `vin_ref` is NULL for all cars (expected). `[VERIFIED]`
- **Municipality ~89%** (50/56 dealers): the misses are INE-index gaps on compound city
  names (e.g. "Perillo – Oleiros"), NOT encoding — `zipCode[:2]` province is **100%**. `[VERIFIED]`

---

## 4. Classification (migrations/0016)

```
defense_tier = 't0_open'         # fully open; plain urllib gets 200; only a public token header
source_group = 'oem_vo_portal'   # the group renew opened
role         = 'platform'
kind         = 'oem_vo_portal'   # the platform entity's ontology kind (migrations/0005)
is_tier1     = FALSE             # no WAF fronts the SCS gateway
website_waf  = 'none'
family       = 'audi_vo'         # Audi's single-brand OEM-VO surface (sibling-by-group to vw_group)
data_surface = 'internal_api'
```

Governor: `scs.audi.de` registered in the **JSON_API rate class** (a first-party gateway
built to serve the whole brand user base across markets — like renew/coches.net), 12 req/s
steady, burst 24, min-spacing 0.03 s + jitter. The per-host token bucket is the aggregate limiter.

---

## 5. Dual-membership wiring (the cage)

```
audi (the OEM-VO portal)  -> entity kind='oem_vo_portal' (+ platform_meta)   [THE PLATFORM]
                             cdp_code CDP-ES-00-NP3AWN4X  (domain:audi.es, province 00=national)
each SELLING DEALER        -> entity kind='compraventa'   (geo via zipCode[:2]; standalone_pos)
each CAR                   -> vehicle OWNED BY its dealer  (entity_ulid = dealer)
the car ON the portal      -> platform_listing edge        (platform_entity <-> vehicle)
NEW car                    -> vehicle_event 'NEW'          (delta)
```

Ownership is singular (the selling Audi concesionario oficial); platform membership is
plural (the edge). The same physical car can carry BOTH an audi edge and a coches.net edge
without changing its owning dealer.

---

## 6. Run

```
python -m pipeline.platform.oem_audi_wholesale --pages 45            # full ES Audi used stock (~40 data pages)
python -m pipeline.platform.oem_audi_wholesale --pages 3             # proof slice (288 cars)
python -m pipeline.platform.oem_audi_wholesale --limit 500           # target ~500 cars (page-count derived)
```

### Verified full-drain result (2026-06-13) `[VERIFIED]`
```
declared full (totalCount) : 3798
pages fetched              : 40 (size=96), HTTP-400 boundary at from=3840
cars caged                 : 3798   (100% of declared)
dealers attributed         : 56 distinct official Audi dealers
data completeness          : price/year/km/fuel/transmission/photo = 100%
VAM count quorum           : harvested_cageable=3798 == db_edges=3798 == db_join_vehicles=3798
VAM verdict                : TRUSTWORTHY (divergence 0.0)
health / breaker           : healthy / closed
idempotent re-run          : 0 new cars / 0 edges / 0 events
```
