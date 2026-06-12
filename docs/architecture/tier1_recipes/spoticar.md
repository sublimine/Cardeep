# Tier-1 Recipe — Spoticar.es (Stellantis ES)

> Status: **CRACKED via FREE path (Vector 1 — internal JSON API).** No proxy, no
> browser, no cookies, no spend. `curl_cffi impersonate=chrome131` alone returns
> HTTP 200 with the raw Elasticsearch car index.
> Verified 2026-06-12.

## TL;DR

Spoticar's public-listing SPA (Drupal) calls an **internal Elasticsearch-backed
JSON API**. Both endpoints answer **HTTP 200 to `curl_cffi impersonate=chrome131`
with no session, no Akamai sensor, no proxy**. The registry's "AkamaiGHost 403"
intel is true only for *plain* curl/wget; a Chrome TLS fingerprint passes the wall
cleanly on homepage, listing, sitemap **and the JSON API**.

- **Declared inventory:** ~50,000 `[A]` (OEM marketing claim).
- **Real public ES index (ES country):** **6,334 vehicles** `[VERIFIED]`
  (`count.value` returned by the API itself). The 50k claim is pan-brand/global
  marketing, not the ES public stock.
- **Harvest cost:** ~528 GET requests (12 cars/page) to pull the entire ES index.

## Working request (the harvest workhorse)

```
GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}
```

Headers (minimal set that works):

```
Accept: */*
X-Requested-With: XMLHttpRequest
Accept-Language: es-ES,es;q=0.9
Referer: https://www.spoticar.es/comprar-coches-de-ocasion
```

- **Tool:** `curl_cffi` with `impersonate="chrome131"` (installed, v0.15.0).
- **Method:** `GET`. No body. No auth. No cookie warm-up required.
- **Pagination:** `page=1` … `page=528` covers the full 6,334-vehicle index
  (12 hits/page; page 528 returns the trailing 11, page 529 returns 0 hits).
  `count.value` + `lastPage` in the response bound the run.
- **Response:** `application/json`. The car records live in `hits[]._source`
  (raw Elasticsearch documents — every field below is present per car).

### Companion endpoint (facets / counts, optional)

```
GET https://www.spoticar.es/api/vehicleoffers/list/search?page={N}
```

Returns aggregations only: `brands[]` (brand → doc_count), `models`,
`generations`, `pointsofsale`, `count`, `filters`, `lastPage`, `seoText`,
plus a server-rendered `renderEntities` HTML fragment. Use it for the
brand/dealer denominator and facet enumeration; use `paginate/search` for the
actual vehicle data.

## How it was found (provenance, fully reproducible)

1. `GET /comprar-coches-de-ocasion` (curl_cffi chrome131) → HTTP 200 HTML.
2. HTML exposes the endpoints inline on the search container:
   ```html
   <div id="search-list"
        data-search-url="https://www.spoticar.es/api/vehicleoffers/list/search"
        data-paginate-url="https://www.spoticar.es/api/vehicleoffers/paginate/search">
   ```
   and the live count `(6334 Vehículos de segunda mano)`.
3. Runner JS `/modules/custom/psa_search/dist/js/new_spoticar/list-search-runner.js`
   confirms the call shape:
   ```js
   $.ajax({ method: "GET", url: SearchVars.api_call, data: {...} })
   // api_call = generateSearchQuery(search_url)  ->  `${url}?page=${page}&...`
   ```
   `generateSearchQuery` appends `page=N` plus optional contextual/UTM/filter
   params. The minimal viable call is just `?page=N`.
4. Direct probe of both endpoints with curl_cffi → HTTP 200 `application/json`.

## Field map (`hits[]._source`, per car) `[VERIFIED]`

Most fields arrive as single-element arrays — unwrap `v[0]`.

| Canonical | Source field | Example |
|---|---|---|
| deep_link | `url` | `/comprar-vehiculo-de-ocasion/fiat-500-...-castellon-1202076554` |
| listing_ref | `field_vo_refbase` / `nid` | `1202076554` / `1038604` |
| carnum (stable id) | `field_vo_carnum` | `ES_ES008VS_1202076554` |
| make | `marque` / `marque_no_accent` | `fiat` |
| model | `model` | `500` |
| line | `ligne` | `fiat 500` |
| version/trim | `version` / `finition_name` | `hb 320km 85kw (118cv)+style+com monotrim` |
| year (model) | `field_vo_annee_modele` | `2024` |
| first-reg year | `field_vo_dpi` (+ `field_vo_dpi_timestamp`) | `2024` / `1716933600` |
| km | `field_vo_km` (`field_vo_km_certifie` bool) | `10` |
| **price (base)** | `field_vo_prix_base` (`field_vo_pb_devise`) | `22390` `eur` |
| price (financed) | `field_vo_prix_financement` (`field_vo_pf_devise`) | `19540` `EUR` |
| monthly payment | `field_monthlypayment` | `335.13` |
| fuel | `fuel_type` / `type_carburant` | `ELEC` / `eléctrico` |
| gearbox | `boite_vitesse` / `transmission` | `automático` / `delantera` |
| power (CV) | `field_vo_puissance_physique` (`field_vo_pp_unite`) | `118` `ch` |
| displacement | `field_vo_cylindree` | `0` |
| color | `color` | `Verde` |
| doors / seats | `field_vo_nb_portes` / `field_vo_nb_places` | `3` / `4` |
| **VIN** | `field_vo_vin` | `zfaefaa4xpx169902` |
| plate | `field_vo_immatri` | `0155mrt` |
| body category | `field_vo_categories` / `field_vo_genre` | `urbano` / `vp` |
| equipment | `equipement` | `pintura metalizada ocean green` |
| promotions | `promotion` | `entrega a domicilio`, `ofertas del mes` |
| created (epoch) | `created` | `1774006898` |
| **dealer name** | `field_pdv_title` | `spoticar comauto sport` |
| dealer brand | `field_pdv_brand` | `SP` |
| dealer city | `field_pdv_city` | `castellon` |
| dealer geo id | `field_pdv_geo_id` | `0000115058` |
| dealer geolocation | `field_pdv_geolocation` | `39.970016,-0.070215` |
| contract type | `type_contrat` / `field_vo_duree_contrat` | `spoticar 12m` / `12` |
| battery SoH | `field_soh` | `95.3` |
| green-zone level | `field_green_zone_level` | `0` |

Dealer attribution is **best-in-class and self-contained** — every car carries its
named Stellantis point-of-sale (`field_pdv_title`) plus geo id + lat/lng. The
`paginate/search` response also includes a top-level `pdv_information` block.

## Sample car (real, pulled via free path)

- **Fiat 500 HB 320km 85kW (118cv) Style+Com Monotrim** — 2024, 10 km, electric, Verde
- **Price 22.390 EUR** (financed 19.540 EUR / 335,13 €/mo)
- VIN `zfaefaa4xpx169902`, plate `0155mrt`
- Dealer: **Spoticar Comauto Sport**, Castellón de la Plana (geo 39.970016,-0.070215)
- URL: `/comprar-vehiculo-de-ocasion/fiat-500-hb-320km-85kw-118cvstylecom-monotrim-castellon-de-la-plana-castellon-1202076554`

## Response envelopes (top-level keys)

- `paginate/search`: `count`, `hits`, `pdv_information`, `aggregation`,
  `filtersLabels`, `renderEntities`, `selectedFilters`, `lastPage`,
  `current_page`, `is_paginate`, `is_enabled_fast_infinite_scroll`.
- `list/search`: `brands`, `generations`, `models`, `pointsofsale`, `count`,
  `countNumber`, `filters`, `selectedFilters`, `activeFilters`, `lastPage`,
  `searchTitle`, `metatags`, `seoText`, `renderEntities`, `tags`, …

## Sitemap (Vector 3 — also free, secondary)

`GET https://www.spoticar.es/sitemap.xml` → HTTP 200 (`sitemapindex`, 18 KB),
child sitemaps enumerable. PDP URLs are also fully derivable from the API `url`
field, so the JSON path is strictly superior. Sitemap kept as a cross-check /
discovery fallback.

## Spoticar Direct

Same Stellantis Drupal infra and same Akamai posture. Expect the identical
`/api/vehicleoffers/*` surface on its host; replay this recipe with the Direct
base URL. (Not separately probed in this pass — same wall, same bypass.)

## Recipe seed (engine line, matches repo convention)

```
source: spoticar
engine: curl_cffi+chrome131_impersonate+internal_es_json_api
access: OPEN-via-fingerprint (Akamai 403 to plain curl; chrome131 TLS passes). is_tier1=true (wall present, bypassed free)
data_surface: json (Elasticsearch hits[]._source)
enumeration: GET /api/vehicleoffers/paginate/search?page=1..528  (12/page, count.value bound)
denominator: list/search count + pointsofsale facet; per-car field_pdv_* for dealer
```

---

## 8-VECTOR LOG (owner-mandated)

| # | Vector | Outcome |
|---|---|---|
| 1 | **Internal/open JSON / GraphQL API** | **✅ WIN.** `GET /api/vehicleoffers/paginate/search?page=N` and `/api/vehicleoffers/list/search` both **HTTP 200 `application/json`** to curl_cffi chrome131, no session. Raw Elasticsearch `hits[]._source`, 6,334 cars, full field map incl. VIN + dealer. Endpoints discovered from `data-search-url`/`data-paginate-url` in listing HTML + runner JS. **This is the harvest path.** |
| 2 | Mobile app API | Not needed — vector 1 already yields the full raw ES index over the web host. Same Stellantis backend powers app; not separately probed because the web JSON API is open and complete. |
| 3 | Sitemap of PDPs + JSON-LD/NEXT_DATA | **✅ also open.** `sitemap.xml` → HTTP 200 (`sitemapindex`, 18 KB) to chrome131; child sitemaps enumerable. Redundant with vector 1 (API `url` field gives every PDP), kept as fallback. |
| 4 | curl_cffi browser impersonation (chrome131) | **✅ WIN — this is the enabling tool for vectors 1 & 3.** chrome131 TLS fingerprint defeats AkamaiGHost: homepage/listing/sitemap/JSON-API all 200. Plain curl would 403 (per registry); the fingerprint is what passes. |
| 5 | Stealth browser (camoufox/patchright/nodriver/SeleniumBase) | **Not required.** Reserved as escalation if Akamai ever rotates to active sensor enforcement on the API. curl_cffi suffices today. |
| 6 | BotBrowser / Byparr / FlareSolverr-successors (Akamai sensor) | **Not required.** No interactive Akamai challenge encountered on the JSON API; no sensor cookie needed. Byparr is the documented escalation if the wall hardens. |
| 7 | FREE datacenter proxy rotation (requests-ip-rotator / cloudproxy) | **Not needed for access** (single IP returns 200). Recommended only as polite rate-spreading for the full ~528-page run to avoid IP throttling; FREE (AWS API Gateway), not paid residential. |
| 8 | Header/cookie/referer warm-up; TLS variation; retry windows | **Not needed.** `Referer: …/comprar-coches-de-ocasion` + `X-Requested-With: XMLHttpRequest` included as good-citizen headers; the API returns 200 even without a warm-up cookie sequence. |

**Bonus — Woosmap stores API:** public key `woos-88a51d0b-2d09-3438-8c39-e8f17727f0a2`
(from page census) → `https://api.woosmap.com/stores/search/?key=...` returns
HTTP 200 (key valid) but an **empty FeatureCollection** for ES. Not needed:
dealer attribution is already fully embedded per-car via `field_pdv_*`.

**Verdict:** Spoticar is **harvestable on a 100% free path.** No residential proxy,
no paid Akamai sensor, no spend. Vector 1 (internal ES JSON API) via Vector 4
(curl_cffi chrome131) pulls the entire 6,334-vehicle ES index with full dealer
attribution. The "spend-gated, hardest wall" verdict in the registry is **refuted
for ES public stock** — the wall only stops naked curl, not a fingerprinted client.
