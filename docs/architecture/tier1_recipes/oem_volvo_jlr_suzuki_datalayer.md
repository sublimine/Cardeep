# oem_volvo_jlr_suzuki — data-layer recipe (Volvo Selekt + Jaguar/Land Rover Approved + Suzuki)

Verified live 2026-06-13. The `volvo_jlr_suzuki` front of the `oem_vo_portal` source_group —
the manufacturer-owned certified-used (VO) portals for Volvo (**Selekt**), Jaguar + Land Rover
(**Approved**) and Suzuki, in Spain. Siblings of renew / spoticar / toyota_lexus under the ONE
architecture, on the new `volvo_jlr_suzuki_vo` family axis.

This front spans **two distinct vendor platforms** behind one connector. Both are clean, uncapped,
internal JSON surfaces — no proxy, no browser at harvest time, no €, just a Chrome TLS fingerprint
(curl_cffi chrome131). Each car carries its selling **official dealer** (concesionario oficial)
embedded per-record — no PDP fetch needed.

| Brand surface | Vendor platform | Surface | Declared (live) |
|---|---|---|---|
| **Volvo Selekt** (`selekt.volvocars.es`) | Codeweavers storefront | `POST services.codeweavers.net/api/vehicles/search-with-facets` | **1,311** |
| **Land Rover Approved** (`approved.es.landrover.com`) | GForces NetDirector AVL | `POST production-api.search-api.netdirector.auto/api/vehicle-search` (GraphQL) | **399** |
| **Jaguar Approved** (`approved.es.jaguar.com`) | GForces NetDirector AVL (same API) | same endpoint, different `companyHash` | **35** |
| Suzuki (`auto.suzuki.es/vehiculos-ocasion`) | redsuzuki.es federated dealer subsites | per-dealer server-rendered HTML (30 subsites) | recon'd, NOT a clean surface — DEFERRED |

Front total of the connected surfaces = **1,745** cars across **2 platforms / 3 brands**.

---

## TL;DR — the two working requests

### A) Volvo Selekt — Codeweavers `search-with-facets`

Codeweavers "Digital Retail Store" SPA. The store identity is injected into the index HTML as a
base64-then-URL-encoded `<meta name="cw-application-configuration">` blob carrying the tenant
`Reference` and `ApiKey`. Auth is a **guest customer token** minted from the ApiKey, then sent as
`x-cw-customertoken` on every call (no Bearer, no cookie warm-up). NO bot WAF.

```
# 0. (static identity — extracted from the index HTML once; constants in the connector)
   Reference = 9d888d9b-7428-4e3c-9763-621c6311e3f2     # cw-application-configuration.Reference
   ApiKey    = n1WG1lPrjpggL45z6p                        # cw-application-configuration.Authentication.ApiKey
   OrgRef    = 55388                                     # CodeweaversReference (init body OrganisationIdentifier)

# 1. mint guest token
POST https://services.codeweavers.net/api/guest/initialise/proposal
  headers: x-cw-digitalretailstorereference: <Reference>, x-cw-applicationname: Storefront,
           x-cw-applicationinstanceid: <uuid>, x-cw-anti-cache: <uuid>, x-cw-accept-language: es-es
  body:    {"ApiKey":"<ApiKey>","OrganisationIdentifier":{"Type":"CodeweaversReference","Value":"55388"}}
  -> 200 {"UserToken":"<guid>", ...}     # UserToken == the customer token

# 2. count (denominator)
POST https://services.codeweavers.net/api/vehicles/search/count
  headers: + x-cw-customertoken: <UserToken>
  body:    {"Filters":{"Vehicle":{}}}
  -> 200 {"VehiclesSearched":1311,"TotalResults":1311}

# 3. paginate (FLAT)
POST https://services.codeweavers.net/api/vehicles/search-with-facets
  body:    {"Filters":{"Vehicle":{}},"ResultsPerPage":100,"Page":N}
  -> 200 {"Results":[{"Vehicle":{...},"Retailer":{...}}], "TotalResults":1311, "TotalPages":14, "CurrentPage":N}
```

- 1,311 cars / 100 per page = **14 pages** (page 14 = 11 trailing). `ResultsPerPage` honoured up to
  >=400. `Page`+`ResultsPerPage` are the pagination keys (NOT `PageSize`). `Filters.Vehicle` is a
  required object; `{}` = no filter = whole stock.
- **IDENTITY TRAP — Reference is NOT a durable key (verified live):** the endpoint SAMPLES +
  RESHUFFLES its result set per request. Two full 14-page crawls share **0 common `Vehicle.Reference`**
  (an ephemeral per-listing/per-session token) but **~95% common VIN / ExternalVehicleId**. The
  `SortOrder` param is ignored. So Reference MUST NOT key the deep_link/dedup — it would make every
  run add "new" cars and never converge. The durable key is the **stock identity**:
  `Physical.ExternalVehicleId` (MDX-xxxx, always present) preferred, `Physical.Vin` fallback. Key the
  deep_link and listing_ref on THAT; within one crawl the union of pages is the complete 1,311-car
  snapshot; across runs the set drifts slightly (the live inventory is larger than any one 1,311
  sample) but the same car (same stock id) maps to the same deep_link -> idempotent.
- Field map (`Results[].Vehicle`):
  - `Physical.ExternalVehicleId` (fallback `Physical.Vin`) — DURABLE stock id = listing_ref + dedup
    key + deep_link path. (`Reference` is the rotating per-session listing token — DO NOT use as key.)
  - `Specification.Manufacturer` / `.Model` / `.Variant` — make / model / version (always Volvo).
  - `Specification.ModelYear` — year. `Physical.Mileage` — km. `Physical.OnTheRoadPrice` — price (EUR).
  - `Physical.Vin` — REAL per-car VIN (gold for cross-source dedup).
  - `Marketing.Features[Label=Fuel].DisplayValue` — Spanish fuel ("Mild hybrid gasolina"); preferred
    over `Specification.FuelType` (English). `Marketing.Features[Label=Transmission].DisplayValue` —
    Spanish gearbox ("Automática").
  - `Images[0].Url` — first hosted image (absolute https on picserver.*.mdxprod.io).
  - dealer: `Results[].Retailer` { `Reference` (stable dealer id), `Name`, `Address.Postcode`
    (first 2 = INE province), `Address.TownCity`, `Address.Location.{Latitude,Longitude}`, `Website` }.
- Encoding trap: human text is latin-1 mojibake over the wire (`Autom�tica`, `el�ctrico`); repair
  with `s.encode('latin-1').decode('utf-8')`. Numeric fields, Reference and Vin are clean.
- deep_link: SPA route `https://selekt.volvocars.es/es-ES/store/used-cars/<slug>/<Reference>` — the
  terminal Reference UUID is the load-bearing key; the leading slug is SEO decoration.

### B) Jaguar + Land Rover Approved — NetDirector AVL `vehicle-search` (GraphQL)

A `<jlr-global-avl>` web component (GForces NetDirector AVL) POSTs a GraphQL query to a regional
search-api. Auth is a static `Authorization` client token + a `uuid` query param (both shared by the
two JLR brands). The brand is selected by `manufacturer` + `companyHash` in the query searchParams.
NO bot WAF on the search-api (serves to curl_cffi with the token).

```
POST https://production-api.search-api.netdirector.auto/api/vehicle-search?uuid=5942c2c0-6601-11eb-b21b-b1ad5fa81f89
  headers: Authorization: 4d598000-5b04-11eb-ab95-ab946a2c7e0d, Content-Type: application/json,
           Origin/Referer: https://approved.es.<brand>.com
  body:    {"query":"query { getCount (searchParams: SP) getAll (searchParams: SP, pagination:
            {currentPage: N, pageSize: 400}, sortParams: [{fieldName: currentPrice, direction: asc}]) FIELDS }"}
           where SP   = {companyHash: ["<hash>"], manufacturer: "<Manufacturer>", condition: "used"}
                 Land Rover: companyHash 1c0df99311526c1ec3af03a70a6da4e2eaa801a2, manufacturer "Land Rover"
                 Jaguar    : companyHash c2b4772858deec1ccea04ea99556cb37b5bd68ab, manufacturer "Jaguar"
  -> 200 {"data":{"getCount":399,"getAll":[{...}]}}
```

- `getCount` is the denominator; `getAll` returns the page. `pageSize` honoured up to >=400 — the set
  is small and FLAT, so ONE page per brand drains it (LR 399, Jaguar 35).
- Field map (`data.getAll[]`):
  - `id` / `identifiers.stockId` — stable car id = listing_ref + dedup key.
  - `manufacturer` / `model` / `variant` — make / model / version.
  - `productionYear` (fallback `registration.year`) — year. `odometer.value` — km (unit km).
  - `price.current` (fallback `.base`) — price (EUR). `vin` (fallback `registration.number`) — VIN.
  - `fuel.type` (Spanish) — fuel. `transmission.type` (Spanish) — gearbox. `mainImage` — first image
    (protocol-relative `//s3-...` -> promote to https).
  - dealer: `location` { `hash` (stable dealer id), `name`, `details.address` { `postcode`
    (first 2 = INE province), `city`, `county`, `line1` } }. There is NO lat/lng on this surface —
    province comes from the postcode only (the renew model), municipality from the city literal.
- Encoding trap: `description` and human text carry latin-1 mojibake (`Informaci�n`, `Di�sel`);
  repair with the same `_fix`. `vin`, `id`, numbers are clean.
- deep_link: PDP path `https://approved.es.<brand>.com/used/<id>` (the AVL detail route keyed by id).

---

## Multi-axis classification (migrations/0016)

```
defense_tier = 't1_soft'           # Volvo Selekt index sits behind Akamai-class fronting; the JSON
                                   # APIs serve to curl_cffi with no JS challenge. (JLR search-api is
                                   # token-gated but open to curl_cffi -> still t1_soft for the front.)
source_group = 'oem_vo_portal'     # the group renew opened; this is its volvo/jlr/suzuki front.
role         = 'platform'
kind         = 'oem_vo_portal'     # the platform ENTITY's ontology kind.
is_tier1     = TRUE                # public sites front behind tier-1 CDNs/WAFs.
family       = 'volvo_jlr_suzuki_vo'
```

## Dual-membership (the ONE architecture)

```
volvo_jlr_suzuki (the OEM-VO portal) -> entity, kind='oem_vo_portal' (+ platform_meta)   [PLATFORM]
each SELLING official dealer          -> entity, kind='compraventa'   (geo-resolved)
each CAR                              -> vehicle, OWNED BY its dealer (entity_ulid=dealer)
the car ON the portal                -> platform_listing edge (platform_entity <-> vehicle)
```

Ownership is singular (the selling concesionario oficial); platform membership is plural (the edge).
There are NO private sellers on these portals.

## Suzuki — why DEFERRED

`auto.suzuki.es/vehiculos-ocasion` is a **directory of 30 dealer subsites** on the `redsuzuki.es`
platform (`<dealer>.redsuzuki.es/vehiculos-ocasion-suzuki`), each server-rendering ~10-11 cars in
HTML with no central JSON API and no per-subsite clean data surface. That is a per-dealer HTML scrape
(a facet/long-tail workaround), not a clean uncapped data-layer surface, so per the "exhaust uncapped
surfaces; connect as many as expose a clean surface" mandate it is recon'd and DEFERRED, not forced
through this OEM-VO connector. Its 30 dealer subsites are enumerated above for a future long-tail pass.

## Run

```
python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20
```
