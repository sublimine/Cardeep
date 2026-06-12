# oem_ford (Ford Selección ES) — data-layer recipe

**Brand:** Ford · **Programme:** *Ford Selección* (Approved-Used / Ford Store VO)
**Portal:** `https://secure.ford.es/compra/explora/vehiculos-de-ocasion/turismos`
**Group:** `oem_vo_portal` · **Family:** `ford_vo` · **Role:** `platform` · **Kind:** `oem_vo_portal`
**Defense tier:** `t1_soft` · **is_tier1:** TRUE · **WAF:** akamai
**Connector:** `pipeline/platform/oem_ford_wholesale.py`
**Platform cdp_code:** `CDP-ES-00-ZB6C77HC`
**Verified live:** 2026-06-13

The FIFTH member of the OEM-VO portal group (after renew / Das WeltAuto / spoticar /
toyota_lexus). The manufacturer-owned certified-used portal for Ford in Spain. Mirrors the
proven `spoticar_wholesale` / `oem_toyota_lexus_wholesale` template exactly (dual-membership,
bulk cage, governor/health/VAM wiring).

## TL;DR

```
POST https://www.servicescache.ford.com/api/eUsed/v1/searchVehicles
Headers:
  Accept: application/json, text/plain, */*
  Content-Type: application/json;charset=UTF-8
  Referer: https://secure.ford.es/
  Origin:  https://secure.ford.es
  x-eusl-consumer: b-gux_approved_used-prod
  x-eusl-k: base64("{epoch_millis}:{16-byte-hex-nonce}")    # regenerated per request
Body (national geo-radius, all ranges unbounded):
  {"locale":"es_ES","vehicleCategory":"10","distance":"2500",
   "longLatCoordinates":"-3.70,40.0",
   "price":{"minPrice":"0","maxPrice":"9999999"},
   "enginePower":{"min":"0","max":"99999"},
   "ageOfVehicle":{"min":"0","max":"99"},
   "mileage":{"min":"0","max":"9999999"},
   "resultOrder":{"orderBy":"Price","sortOrder":"Ascending"},
   "pagination":{"maxRecords":20000,"startingRecord":0}}
=> data.VehicleInventoryList.{totalMatches, VehicleInventoryItem:[...]}
```

One national request drains the **entire** Ford Selección ES public stock:
**543 cars · 31 official dealers · 0 missing dealer/postcode/geo** (verified live).

## Access — the eUSL soft gate

The eUsed API sits behind **Akamai** (`akamai-grn` header present; plain curl → HTTP 401
`"Request is not Originated from valid Source"`). Two layers must be satisfied:

1. **Akamai source check** — pass `Referer: https://secure.ford.es/` (+ `Origin`). Without it:
   401 *"Request is not Originated from valid Source"*.
2. **eUSL consumer gate** — two computed headers. Without them (but with Referer): 401
   *"Consumer is not Authorized"*.

Both headers are **client-side reproducible** (reverse-engineered from
`secure.ford.es/etc/designs/guxfoe/clientlibs/guxfoe-approved-used/dist/guxfoeApprovedUsed.js`
v5.35.0, `generateToken`):

```js
consumers = "b-" + applicationName + "-" + env       // "b-gux_approved_used-prod"
token     = btoa(Date.now() + ":" + nonce)           // nonce = 16 random bytes, hex (32 chars)
headers   = { "x-eusl-consumer": consumers, "x-eusl-k": token }
```

- `applicationName` = the SPA's hard-coded `bslHeaderValue` for the search service:
  **`gux_approved_used`** (`getVehicleData → handleBslCall({bslHeaderValue:"gux_approved_used"})`).
- `env` is derived from the page host — `secure.ford.es` / `www.ford.es` map to the prod host
  list → **`prod`**.
- `x-eusl-k` **must be fresh per request** (timestamp + nonce); replay is rejected.

No proxy, no browser, no cookie, no auth login, €0. Public API behind Akamai → `is_tier1=TRUE`;
the gate is soft + reproducible with no JS challenge → `defense_tier=t1_soft`.
Engine: `curl_cffi` `impersonate=chrome131`.

## Enumeration — single national geo-radius query

- The request is a **geo-radius** search: `longLatCoordinates="{lng},{lat}"` + `distance` (km).
- **`longLatCoordinates` is `lng,lat`** (NOT `lat,lng`) — wrong order returns 0 matches.
- **The radius is NOT capped.** From the centre of Spain (`-3.70,40.0`):
  - `distance ≤ 1500 km` → 482 cars (peninsula only)
  - `distance ≥ 2000 km` → **543 cars** (peninsula + Canaries; saturates)
  We use `distance=2500 km` to guarantee national coverage.
- **`pagination.maxRecords` is honoured well past the SPA's 144.** `maxRecords=20000` returns
  **all 543** cars in ONE response — FLAT, no relevance cap, no depth wall. `startingRecord` is a
  ROW cursor kept for safety; the run stops on the first empty `VehicleInventoryItem`.
- `vehicleCategory="10"` = *Personal* (turismos) per `/searchOptions`; the SPA encodes it as
  `"10:Personal"` and sends `split(":")[0]`.
- Dedup key: `Vehicle.Identity.ID`.

**Denominator:** `data.VehicleInventoryList.totalMatches` (543) == distinct `Vehicle.Identity.ID`
== Σ per-car dealer attribution.

## Field map (per `VehicleInventoryItem`)

| Field | Path |
|---|---|
| listing_ref / dedup | `Vehicle.Identity.ID` |
| deep_link | `secure.ford.es/.../results#vehicleDetails/{Vehicle.Identity.ID}/{VendorCode}` |
| make | `Vehicle.Brand.ShortDescription` (FORD) |
| model | `Vehicle.Model.ShortDescription` |
| variant | `Vehicle.Variant.ShortDescription` |
| year | `Vehicle.History.YearOfProduction` (fallback `DateOfRegistration` year) |
| km | `Vehicle.CurrentCondition.CurrentOdometerReading.value` |
| price | `VendorInformation.Price.value` (EUR; `VATIncIndicator` notes VAT inclusion) |
| fuel | `Vehicle.Configuration.FuelType.ShortDescription` |
| transmission | `Vehicle.Configuration.TransmissionType.ShortDescription` |
| photo | `Vehicle.Configuration.Appearance.ImageRef[0].value` (cdn.dealerk.es) |
| **dealer id** | `VendorInformation.VendorCode` |
| dealer name | `VendorInformation.VendorName` |
| dealer postcode | `…Address.PostCode.Identifier[0].value` → `[:2]` = INE province (authoritative) |
| dealer city | `…Address.Locality.NameElement[0].value` |
| dealer lat/lon | `…Address.LocationByCoordinates.Latitude/Longitude.DegreesMeasure` (geocode fallback) |
| VIN | **none** — only `Vehicle.Identity.RegistrationNumber` (matrícula) → `vin_ref` stays NULL |

## Geo anchor

Postcode-first (the renew/toyota model): `PostCode.Identifier[0].value[:2]` = INE province
(validated `01`–`52`). Fallback: `LocationByCoordinates` lat/lon → `ProvinceGeocoder.nearest_province`.
Municipality: `Locality.NameElement` → `GeoResolver.municipality_code`. Verified: **0** cars
missing postcode or coords across the full national set (23 provinces represented).

## Caveats

- **`longLatCoordinates` order is `lng,lat`** — the single most common mistake; wrong order → 0 hits.
- **Radius not capped** — one wide-radius query enumerates the whole country.
- **`maxRecords` honoured past 144** — 20000 drains the full stock in one POST.
- **Clean UTF-8** over the wire (`GARANTÍA`, `táctil`, `Híbrido` arrive intact) — **no** latin-1
  `_fix()` round-trip (unlike spoticar). Any `�` in a Windows console is a display codepage
  artefact, not stored data (DB bytes verified: `Diésel` = `\xc3\xa9`).
- **No per-car VIN** — only the matrícula; `vin_ref` is NULL by design.
- **`x-eusl-k` freshness** — regenerate the timestamp+nonce per request.
- **No private sellers** — OEM certified-used portal; every car belongs to a Ford official dealer.

## Multi-axis classification (migrations/0016)

```
defense_tier = t1_soft          source_group = oem_vo_portal
role         = platform         kind         = oem_vo_portal
is_tier1     = TRUE             family       = ford_vo
data_surface = internal_api     waf          = akamai
```

## E2E proof (2026-06-13, single `--pages 1` national request)

```
items seen            : 543        dealers attributed : 31 distinct
cars caged            : 543 (543 new)
platform_listing edges: 543 created (db total = 543)
NEW delta events      : 543        VINs captured : 0 (none on surface — expected)
no-dealer/geo skipped : 0 / 0      dup ids collapsed : 0
VAM count quorum      : harvested_cageable=543 == db_edges=543 == db_join_vehicles=543
VAM verdict           : TRUSTWORTHY
health                : healthy / breaker closed
```

Idempotent re-run: **0 new cars, 0 new edges, 0 new dealers, 0 NEW events**; db total stays 543;
VAM verdict TRUSTWORTHY. ON CONFLICT path verified.

## Run

```
python -m pipeline.platform.oem_ford_wholesale --pages 1
# --limit N narrows to ~N cars; --concurrency widens the request window (host bucket is the limiter)
```
