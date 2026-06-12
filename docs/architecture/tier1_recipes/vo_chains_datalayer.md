# vo_chains — Data-Layer Recipe (national used-car CHAINS, own-site stock)

Status: **TWO OPEN SURFACES FOUND.** Both members serve 100% of their own stock through
an unwalled first-party data layer (no proxy, no browser, no cookie warm-up, €0).
Group: **`source_group='chain'`** — big national used-car chains liquidating their own
large stock through their own storefront. Each chain is a `kind='cadena'` platform entity;
each car attributes to its **real selling point** (a physical branch where the surface
exposes one, else the chain company itself).
Connector: `pipeline/platform/group_vo_chains_wholesale.py`.
Verified LIVE: **2026-06-13** (`curl_cffi` `impersonate="chrome131"`, no proxy, no browser).

> Anti-hallucination: every field below was inspected on a live response, not assumed.
> Counts move with the live market.

---

## Members & owner models (why two caging shapes, one architecture)

| Member | Surface | Declared stock | Owner model | Selling point caged |
|---|---|---|---|---|
| **Flexicar** | OPEN JSON REST API | **23,874** (`total`) | per-branch | each of 186 physical **compraventa** branches |
| **OcasionPlus** | SSR schema.org JSON-LD `ItemList` | **14,052** (`offerCount`) | chain-as-owner | the **chain company** (per-car branch not on this surface) |

Both flow through the ONE proven architecture (governor choke point, `GeoResolver`,
idempotent `ON CONFLICT` BULK unnest ingest, NEW-delta events, VAM count quorum, S-HEALTH
breaker) — mirroring `coches_net_wholesale` (per-branch owner) and
`group_rentacar_vo_wholesale` (chain-as-owner). The dual owner model lives in one file:
`owner_model='branch'` routes a car to its geo-resolved branch; `owner_model='chain'`
cages it under the chain entity directly.

Chain platform entity (both): `kind='cadena'`, `source_group='chain'`, `role='chain'`,
`is_tier1=FALSE`, `defense_tier='t0_open'`, `province_code=NULL` (national; `00` in the
cdp_code only). `platform_listing` edge = chain ⟷ vehicle for every car (the dual-membership
signal a marketplace car carries; the same physical car could also carry an AS24/coches.net
edge without changing its owner).

---

## MEMBER 1 — FLEXICAR (the cleanest surface in the group)

### TL;DR — the open JSON gateway

`services.flexicar.es/api/v1/vehicles` is Flexicar's **OPEN first-party REST/JSON gateway**
(the SPA backend behind `www.flexicar.es`). Unwalled to a Chrome TLS fingerprint — no proxy,
no cookie, no JS challenge. Harvest = walk `?page=N&size=24` 1 → `pages`.

```
GET https://services.flexicar.es/api/v1/vehicles?page=1&size=24
Accept: application/json
Origin: https://www.flexicar.es
Referer: https://www.flexicar.es/
```

Response (verified live):

```json
{ "hasNext": true, "page": 1, "pages": 995, "size": 24, "total": 23874,
  "lowPrice": 5490, "highPrice": 174990, "results": [ { ... } ] }
```

- `total = 23874`, `pages = 995` (live 2026-06-13).
- **`size` is HARD-capped at 24** — `size>24` → **HTTP 400** `"size must not be greater than 24"`
  (verified at 36/48/60/100). The drain is request-bound: full set = **995 requests**.
- Default order is stable across calls; sequential `page` walking is consistent. Dedup on
  `result.id` absorbs any live-insertion drift.
- `province` and `carDealership` query filters also work (e.g. `province=coruna` → 543,
  `carDealership=a-coruna-parque-de-viono` → 97) — useful for a per-branch verification pass,
  not required for the linear drain (each car already carries its branch).

### Branch attribution (the per-branch owner model)

Each `result` carries **`carDealershipSlug`** — the branch that sells it. The full
**186-branch directory** lives in the SSR `__NEXT_DATA__` of the listing page (NOT the API):

```
GET https://www.flexicar.es/coches-segunda-mano/
  -> <script id="__NEXT_DATA__"> .props.pageProps.dealerships[]
     each = { value(=slug), name, province, provinceSlug, zipCode, location, latitude, longitude }
```

Geo per branch: the branch `zipCode`'s first two digits **ARE the INE province code**
(`15008` → `15` A Coruña), and `location` resolves the municipality through `GeoResolver`.
Load the directory once at run start; map every car's `carDealershipSlug` → branch →
`cdp_code` (`name + municipality + address='branch:<slug>'`, so two branches sharing a name
in one town stay distinct). A car referencing an unknown/un-geocoded branch is caged under
the chain entity (national) rather than dropped — never fabricate a branch.

### Field map (per `result`)

```
id            -> listing_ref (Flexicar native stock id)
slug          -> deep_link = https://www.flexicar.es/coches-segunda-mano/{slug}
brand         -> make
model         -> model
version       -> (folded into title)
year          -> year
km            -> km
price         -> price
previousPrice -> prev_price  (price-drop delta — gold for the NEW event)
fuel          -> fuel (clean ES label: Gasolina/Diésel/Híbrido/...)
transmission  -> transmission (Manual/Automático)
image / images[0] -> photo_url
carDealershipSlug -> selling branch (-> dealerships[value=slug] -> geo)
```

---

## MEMBER 2 — OCASIONPLUS (SSR JSON-LD, chain-as-owner)

### TL;DR — the embedded schema.org ItemList

`www.ocasionplus.com` is a Next.js App-Router SSR site (`x-powered-by: Next.js`, **no
Cloudflare/WAF** → `t0_open`). Its public data layer is the **schema.org JSON-LD `ItemList`**
embedded in each search-results render: **20 `Vehicle` objects/page**, each with full
structured data. Harvest = walk `?page=N` 1 → ~703.

```
GET https://www.ocasionplus.com/coches-segunda-mano?page=1
Accept: text/html,application/xhtml+xml,...
Referer: https://www.ocasionplus.com/
```

- `?page=N` paginates **server-side** (verified: distinct car sets per page; `?pagina=N` is
  ignored and returns page 1).
- The page-level `Product` block's `offers` (`AggregateOffer`) declares the full stock:
  **`offerCount = 14052`** (live 2026-06-13). At 20/page that is **~703 pages**.
- Per-branch (`centro`) is **NOT** on this search-results surface, so the chain is the
  singular selling point and owns every car. The PDP (detail page) carries `centro`/`provincia`
  for a future per-branch attribution pass — never fabricated here.

### Field map (per `ItemList.itemListElement[].@type=Vehicle`)

```
offers.url            -> deep_link (per-car PDP)
url tail after last - -> listing_ref (stable native id, e.g. 'togx7qan')
brand.name            -> make
model                 -> model / title
productionDate (ISO)  -> year (YYYY prefix)
mileageFromOdometer.value -> km
offers.price          -> price (EUR)
fuelType              -> fuel
vehicleTransmission   -> transmission (AUTO->Automático / MANUAL->Manual)
image                 -> photo_url
```

---

## Governor pacing (registered)

- `services.flexicar.es` → **JSON_API class** (12 req/s, burst 24): a first-party JSON gateway
  built for the brand's whole user base; size-cap makes it request-bound, so the higher rate
  matters. Unwalled (`t0_open`).
- `www.ocasionplus.com` → **STEALTH class override** (1 req/s, burst 3, min-spacing 0.8 s):
  an SSR HTML surface (not a JSON gateway) with an unmeasured ceiling — paced conservatively
  below it, human-shaped, like `dasweltauto`/`coches.com`. The breaker is the safety net.

---

## LIVE E2E PROOF (2026-06-13, real DB writes, `cardeep-pg:5433`)

Bounded foreground harvest (`--pages 3` both members, then `--pages 8` Flexicar):

| Member | chain cdp_code | cars caged | owners (selling points) | edges | NEW deltas | VAM |
|---|---|---|---|---|---|---|
| Flexicar (8 pages) | `CDP-ES-00-FYECEGD5` | 192 | **11 distinct compraventa branches** | 192 | 192 | **TRUSTWORTHY** |
| OcasionPlus (3 pages) | `CDP-ES-00-SWN09H0C` | 60 | 1 (the chain) | 60 | 60 | **TRUSTWORTHY** |

- Flexicar branch entities created with real geo (e.g. `A Coruña - Parque de Vioño`,
  province `15`, municipality `15030`); each car owned by its branch, `platform_listing`
  edge chain ⟷ vehicle.
- OcasionPlus cars owned by the `OcasionPlus` `kind='cadena'` entity directly.
- **Idempotency proven**: re-running Flexicar pages 1-3 added **0 new cars, 0 edges,
  0 NEW events** (db total unchanged) — `ON CONFLICT` makes a re-harvest a no-op.
- VAM count quorum (three orthogonal like-with-like paths) agreed exactly for both slices:
  `harvested_cageable == db_edges == db_join_vehicles`.
- S-HEALTH: both sources `healthy`, breaker `closed`, `harvest_run` + `source_health` +
  `verification_verdict` rows persisted.

---

## Further members (same group, same architecture)

- **Clicars** (`clicars.com`) — a custom SPA widget (`data-url-vehicles-count=/coches/numero-de-vehiculos`,
  stock loaded via an XHR with a `{makers,models,fuels,bodies,publishedOptions,embeds}` params
  body; ~1,561 cars). `storage.googleapis.com/clicars-storage-prod-public/others/data.json.gz` is
  facet metadata only, NOT stock. The stock XHR endpoint needs a deeper bundle probe before adding.
- **Carplus, Aurgi, GpsAutos, Crandon** — added as further `source_group='chain'` members under
  this same connector once their cleanest stock surface is probed.

---

## Conclusion

Two national used-car chains drain cleanly through unwalled first-party data layers: Flexicar
via an **OPEN JSON REST API** (23,874 cars, per-branch attribution to 186 physical compraventa),
OcasionPlus via **SSR schema.org JSON-LD** (14,052 cars, chain-as-owner). Both cage every car to
its real selling point, mint a `platform_listing` edge, emit NEW deltas, and pass a TRUSTWORTHY
VAM count quorum — all through the ONE proven architecture, no fork per chain.
