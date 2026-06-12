# subastas (car AUCTION / remarketing) — data-layer recipe

**Group:** `subastas` (B2B/B2C car auctions & remarketing) · **source_group:** `official_registry`
**Public member connected:** **Ayvens Carmarket** (ALD Automotive remarketing)
**Portal:** `https://carmarket.ayvens.com/es-es/lots`
**Family:** `ayvens_carmarket` · **Role:** `platform` (sellers `registry`) · **Kind:** `plataforma` (sellers `subasta`)
**Defense tier:** `t0_open` · **is_tier1:** FALSE · **WAF:** none
**Connector:** `pipeline/platform/group_subastas_wholesale.py`
**Platform cdp_code:** `CDP-ES-00-H1VCV020`
**Verified live:** 2026-06-13

The `subastas` group is the auction / remarketing surface — a SEPARATE source group from the Tier-1
marketplaces, the generalist classifieds and the OEM-VO portals. A remarketer runs timed **sales**
(auctions / tenders) of fleet & leasing returns. Of the five ES operators named in the mandate
(Autorola, BCA España, Ayvens/ALD, Allane, Aucto), **only Ayvens Carmarket exposes public car stock**;
the other four are gated (documented below). The connector mirrors the proven
`coches_net_wholesale` / `oem_audi_wholesale` template exactly (dual-membership, bulk cage,
governor/health/VAM wiring) — the auction group flows through the ONE architecture, not a fork of it.

## TL;DR

```
GET https://carmarket.ayvens.com/es-es/lots
Headers:
  Accept: text/html,application/xhtml+xml,...
  Accept-Language: es-ES,es;q=0.9
  Referer: https://carmarket.ayvens.com/
=> 200 text/html (~350-470 KB SSR). Parse:
   <script id="ng-state" type="application/json">{ ... "apollo.state": { ... } }</script>
   apollo.state holds:
     LotWithSaleEvent:<id>  -> the CAR  (make, model, version, mileage, fuelType,
                               transmissionType, firstRegistrationDate, fixedPrice, currency,
                               mainImageUrl, images[], saleEventCountry, saleEventId, saleEvent{...})
     SaleEventWithLots:<id> -> the SALE (id, country, name, description, reference, type, state,
                               lotsCount, currency, start/endDateTimeUtc, highlights[])
```

One SSR render embeds the lots of the currently-**opened** sale events. ES-filter on
`saleEventCountry == 'es'`; the seller is the **sale event** (the auction). Live proof: **72 lots /
24 sale events embedded; 27 ES lots across 2 ES sales caged** (declared lotsCount sum = 470).

## Access — open SSR, walled GraphQL

Ayvens Carmarket is an **Angular Universal SSR** app. Two surfaces:

1. **SSR `ng-state` (PUBLIC, key-free)** — the server renders the live Apollo client cache into a
   `<script id="ng-state" type="application/json">` block. A plain `curl_cffi` chrome131 GET returns
   it (HTTP 200, no WAF challenge, no proxy/browser/cookie warm-up). **This is the data surface.**
2. **GraphQL gateway `api-carmarket.ayvens.com/graphql` (WALLED)** — the first-party HotChocolate
   gateway that produced the cache. It is fronted by **Azure API Management** requiring an
   `Ocp-Apim-Subscription-Key`. The key is held **server-side** (the SSR/BFF proxies the client's
   same-origin relative `graphql` POST with it); it is **NOT** in the client bundle. Verified:
   - `GET api-carmarket.ayvens.com/{configurations,featureflags,localizations/es-es}` → **401**
     `"Access denied due to missing subscription key."`
   - `POST api-carmarket.ayvens.com/graphql` (and `/lots/graphql`, `/api/graphql`, …) → **404/401**.
   - Same-origin `POST carmarket.ayvens.com/{es-es/,}graphql` → the Angular SPA HTML shell (catch-all
     route; no public proxy).

   ⇒ The keyed GraphQL is a **gated** path (credential/spend). Not faked, not bypassed. The SSR
   surface is the honest public ceiling.

## Data model — the SELLING POINT is the SALE EVENT

An auction lot has **no per-lot dealer and no per-lot province** on this surface — it belongs to a
national remarketing **SALE**. So each car is attributed to its real selling point, the auction sale:

```
Ayvens Carmarket (the remarketing platform) -> entity kind='plataforma'  (+ platform_meta)  [PLATFORM]
each SALE EVENT (the ES auction/tender sale) -> entity kind='subasta'    (national)         [SELLER]
each LOT (car)                               -> vehicle OWNED BY its sale event (entity_ulid=sale)
the lot ON the platform                      -> platform_listing edge (platform_entity <-> vehicle)
```

Ownership is singular (the sale event); platform membership is plural (the edge). The same physical car
could carry an Ayvens edge AND another platform's edge without changing its owning sale.

- **Sale-event seller cdp_code:** national prefix `00` + canonical key
  `name:'ayvenscarmarketsubasta{reference|id}'|p00` + `address=ayvenssale:{saleEventId}`. Province
  stored **NULL** on the entity (`00` is not a `geo_province` FK; it lives only in the cdp_code string,
  exactly like the platform entity). `source_ref` = `saleEventId`. `role='registry'`, `sells_cars=TRUE`.

## Field map (LotWithSaleEvent)

| Cardeep field | Source |
|---|---|
| `deep_link` | `https://carmarket.ayvens.com/es-es/lot/{id}` |
| `listing_ref` | `id` (stable lot id + dedup key) |
| `make` / `model` | `make` / `model` (UPPERCASE on source → title-cased) |
| `version` | `version` |
| `year` | `firstRegistrationDate` (`YYYY-MM-DD` → `YYYY`) |
| `km` | `mileage` |
| `price` | `fixedPrice` (tender/direct-buy only; **pure-auction lots have NO public price → NULL**) |
| `fuel` | `fuelType` (`diesel`/`petrol`/… → Spanish label) |
| `transmission` | `transmissionType` (`manual`/`automatic` → `Manual`/`Automático`) |
| `photo_url` | `mainImageUrl` (`{size}` → `800x600`); fallback `images[0]` |
| seller (sale) | `saleEventId` → `SaleEventWithLots {name, reference, type, description, lotsCount, country}` |
| ES filter | `saleEventCountry == 'es'` |

## Enumeration & denominator

- **Enumeration:** the SSR render embeds the lots of the currently-**opened** sale events (a live
  snapshot). Dedup on lot `id`. There is **no key-free pagination** beyond the SSR embed — a full
  per-sale drain (each sale's `lotsCount` is in the hundreds) needs the APIM-keyed GraphQL (gated).
- **Denominator (honest):** sum of the ES sales' declared `SaleEventWithLots.lotsCount`. The public
  slice is the SSR-embedded subset, recorded for the VAM slice arithmetic. Live: declared **470**,
  public slice **27**.

## Gated members — documented honestly

| Operator | Surface | Verdict |
|---|---|---|
| **Autorola** (`autorola.es`) | Angular SPA shell from S3; lots/auctions API relative-pathed against a runtime base; bidding requires dealer **approval** (`become_approved_to_bid`). Public site shows only aggregate auction COUNTS (e.g. "9841 Vehículos ofrecidos"), never per-lot stock. | **GATED** |
| **BCA España** (`bca.com` / `es.bca-europe.com`) | B2B only — *"solo los profesionales del automóvil pueden participar … solo las empresas de automoción pueden comprar"*. Sale calendar renders but lots are behind a buyer login. | **GATED** |
| **Allane** (`allane.de` / Sixt Leasing) | DE-centric leasing remarketer; no public ES car-stock surface reachable. | **GATED** |
| **Aucto** (`aucto.es`) | Connection refused / not reachable from here. | **GATED (unreachable)** |
| **Ayvens Carmarket** (`carmarket.ayvens.com`) | PUBLIC SSR `apollo.state` — the one auction operator exposing public ES lots. | **CONNECTED** |

## Multi-axis classification (migrations/0016)

```
platform entity : kind=plataforma · source_group=official_registry · role=platform
                  defense_tier=t0_open · is_tier1=FALSE · waf=none · family=ayvens_carmarket
                  province_code=NULL (sentinel 00 in cdp_code only)
                  platform_meta.data_surface=internal_api (surface_intent=ssr_apollo_transfer_state)
sale-event sellers: kind=subasta · source_group=official_registry · role=registry · province NULL · sells_cars=TRUE
```

> **source_group note:** there is no dedicated `auction` value in the `source_group` enum. Per the
> mandate, `official_registry` is the nearest enum and is used for both the platform and its
> sale-event sellers, with `family=ayvens_carmarket` and `kind=subasta` carrying the auction
> semantics on the ontology and family axes.

## Governor

`carmarket.ayvens.com` is registered in the **STEALTH** rate class (`rate=1.0 req/s, burst=3,
min_spacing=0.8s`) — an SSR HTML surface paced conservatively below an unmeasured ceiling
(like `dasweltauto`/`coches.com`). Serves cleanly to chrome131 today; the breaker is the safety net.

## Live proof (2026-06-13)

```
platform cdp_code     : CDP-ES-00-H1VCV020
ES sales seen         : 2          (saleEventId 43439 ref 148979 'ESP - SUBASTA - 4035';
                                    saleEventId 43445 ref 148986 'ESP - SUBASTA - 4036' tender)
items seen            : 72   non-ES skipped: 45
ES lots               : 27   (0 with a public price — auction lots are bid-based)
sale-event sellers    : 2 distinct (2 new)
cars caged            : 27 (27 new) · edges: 27 · NEW delta events: 27
VAM quorum            : harvested_cageable=27 == db_edges=27 == db_join_vehicles=27  -> TRUSTWORTHY
health/breaker        : healthy / closed
idempotent re-run     : caged 27 (0 new) · 0 edges · 0 events · db total 27 -> TRUSTWORTHY
```

E2E verified independently in `cardeep-pg :5433`: platform entity + platform_meta, 2 `subasta`
sellers (province NULL, source_ref = saleEventId, role=registry), 27 `platform_listing` edges = 27
join-reachable vehicles owned by the sale events, 27 NEW `vehicle_event` rows, each car attributed to
its selling auction sale (e.g. *Alfa Romeo Stelvio 2022 → subasta 148979*; *Audi A3 2023 → subasta
148986*).
