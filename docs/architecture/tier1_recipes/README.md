# Tier-1 Free-Assault — Results Synthesis

> **Verdict in one line:** all **7** probed giant ES platforms are **harvestable on a
> 100% FREE path** today — €0, no paid residential proxy, no CAPTCHA-solver spend. Six
> fall to plain `curl_cffi` (Chrome TLS impersonation); one (milanuncios) needs a free
> stealth browser (camoufox). **Zero platforms are genuinely walled.**
>
> Sweep date: **2026-06-12**. Country probed: **ES**. Every recipe below is `[VERIFIED]`
> (request fired, bytes read, real car + dealer pulled) — never `[ASSUMED]`. The full
> per-platform dossiers (8-vector logs, field maps, traps, scripts) live alongside this
> file: [`wallapop.md`](wallapop.md) · [`coches_net.md`](coches_net.md) ·
> [`coches_com.md`](coches_com.md) · [`autocasion.md`](autocasion.md) ·
> [`spoticar.md`](spoticar.md) · [`motor_es.md`](motor_es.md) ·
> [`milanuncios.md`](milanuncios.md).

---

## 0. What "free assault" means here

The owner-mandated discipline: before declaring any platform "needs spend", exhaust the
**8 free vectors** with evidence — (1) internal/open JSON or GraphQL API, (2) mobile-app
API, (3) sitemap of PDPs + JSON-LD/`__NEXT_DATA__`, (4) `curl_cffi` Chrome TLS
impersonation, (5) free stealth browser (camoufox/patchright/nodriver), (6)
BotBrowser/Byparr/FlareSolverr, (7) **free** datacenter-proxy rotation
(requests-ip-rotator/cloudproxy), (8) header/cookie/referer warm-up.

A platform is listed as **"needs spend"** ONLY if its dossier shows all free vectors
tried and failed. **No platform reached that bar.** In every case a primary free vector
(1, 3, or 5) won; vectors 2/6/7/8 were generally not even needed and are recorded in the
dossiers as *unnecessary* (no wall hit), not as dead ends.

---

## 1. Ranked results table

Ranked by **harvest ease** (cleanest free path first → hardest). "Tool tier" maps to
`02-SCRAPING-ENGINE.md`: **T0** = `curl_cffi` only, **T1** = free stealth browser.

| # | Platform (operator) | Free now? | Tool tier | Working recipe (endpoint / method) | Data surface | Dealer attribution | Sample car pulled (free, 2026-06-12) |
|--:|---|:---:|:---:|---|---|---|---|
| 1 | **spoticar** (Stellantis ES, Drupal) | ✅ FREE | T0 `curl_cffi` chrome131 | `GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={1..528}` | Internal **Elasticsearch** JSON (`hits[]._source`), **VIN present** | per-car `field_pdv_title` + geo id + lat/lng (best-in-class) | Fiat 500 HB 85kW Style — 22.390 € — *Spoticar Comauto Sport*, Castellón (VIN `zfaefaa4xpx169902`) |
| 2 | **coches_net** (Adevinta/Schibsted) | ✅ FREE | T0 `curl_cffi` chrome131 | `POST https://web.gw.coches.net/search` — **no trailing slash**, `categoryId:2500`, **nested** `pagination:{page,size}` | JSON `{items[], meta{totalPages,totalResults}}`, 272,706 live | first-class `seller{name,isProfessional,contractId,ratings}` | TESLA Model S — 29.900 € — *Movilcar* (contract 77152), Madrid |
| 3 | **autocasion** (Grupo Luike / Vocento) | ✅ FREE | T0 `curl_cffi` chrome131 | GraphQL `POST https://gql.autocasion.com/graphql/` `ad(adId:N)` (open, no auth) + PDP JSON-LD for dealer; enumerate via SSR `/coches-ocasion?page=N` | GraphQL `Ad` + PDP JSON-LD `Product`, 115,179 live | PDP JSON-LD `offers.offeredBy` = **`AutoDealer`** (name/@id/phone/address) | CITROEN C4 1.4i Collection 2006 — 5.500 € — *TADER CARS* (tel 966678599), Elche 03293 |
| 4 | **motor_es** (Motor Internet S.L.) | ✅ FREE | T0 `curl_cffi` chrome131 | `GET https://www.motor.es/segunda-mano/coches/?pagina=N` (22 cards/pg, SSR) → PDP `/segunda-mano/anuncio/{id}/` JSON-LD | SSR HTML cards + PDP JSON-LD `@type:Car`; `get-data-ajax` gives live `total=50,938` (first-10 only) | PDP JSON-LD `offers.seller.name` + `/concesionarios/{prov}/{slug}/` | Peugeot Rifter Allure BlueHDi 130 — 21.990 € — *BONOCASION*, Sta. Cruz de Tenerife |
| 5 | **coches_com** (Carossa / Grupo coches.com) | ✅ FREE | T0 `curl_cffi` chrome131 | Sitemap walk `sitemap.xml → vo.xml → Todo-VO-{0..3}.xml` (~100k PDPs) → PDP `__NEXT_DATA__` | SSR `__NEXT_DATA__` `props.pageProps.data.classified` + JSON-LD; ~200k declared | `classified.dealer` (`name`/`uuid`/`crmId`/`type`/`taxIdNumber`) | TOYOTA C-HR 125H Active — 16.490 € (oferta 14.990) — *Subastacar* (AUTHORIZED/D1295), Madrid |
| 6 | **wallapop** (Wallapop C2C+PRO) | ✅ FREE | T0 `curl_cffi` chrome131 | `GET https://api.wallapop.com/api/v3/search/section` (geo via `latitude`/`longitude`; JWT `next_page`) | Internal JSON `data.section.items[]` (`type_attributes` = car specs), ~750k declared | `user_id` → `GET /api/v3/users/{id}` → `type:professional` + `web_slug` | BMW X4 2019 — 23.990 € — dealer *MUNDOAUTO* (professional, featured), Alcobendas (Madrid) |
| 7 | **milanuncios** (Adevinta Spain) | ✅ FREE | **T1** stealth (camoufox) | **camoufox** warm-up on `/` (mints `reese84`) → **in-page SPA click** into `coches-de-segunda-mano` → scroll → scrape `article.ma-AdCardV2` DOM | Server-rendered SRP DOM (no replayable JSON API); ~667k census, **10k/view display cap** | dealer name in card blurb + warranty/financing signal; clean `seller` on PDP (open via in-page click) | PORSCHE Macan S Diesel 2015 — 34.500 € — dealer *VOJJCARS*, Mejorada del Campo (Madrid) |

**Legend.** *Free now?* ✅ = real cars + dealer pulled at €0 this sweep. *Tool tier* is the
**minimum** engine that works; all T0 platforms also work from a stealth browser but don't
need one.

---

## 2. The recipes, expanded (copy-ready)

### 2.1 spoticar — internal Elasticsearch JSON API (cleanest win)
```
GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}
Headers: Accept: */*  ·  X-Requested-With: XMLHttpRequest
         Accept-Language: es-ES,es;q=0.9
         Referer: https://www.spoticar.es/comprar-coches-de-ocasion
Tool: curl_cffi impersonate="chrome131"  ·  no proxy, no cookie, no auth
Enumerate: page=1..528 (12 cars/pg; count.value=6,334 ES public stock bounds the run)
Data: hits[]._source (raw ES docs; unwrap single-element arrays v[0]); VIN in field_vo_vin
Dealer: field_pdv_title + field_pdv_geo_id + field_pdv_geolocation (per car)
```
Note: AkamaiGHost 403s *plain* curl; the **chrome131 TLS fingerprint passes** the wall.
Registry "spend-gated hardest wall" verdict is **refuted** for ES public stock.

### 2.2 coches_net — Adevinta search gateway (canonical Adevinta recipe)
```
POST https://web.gw.coches.net/search           # NO trailing slash (the /search/ variant 404s)
Headers: Content-Type: application/json  ·  Accept: application/json,text/plain,*/*
         X-Schibsted-Tenant: coches             # the only load-bearing custom header
         Origin: https://www.coches.net  ·  Referer: https://www.coches.net/segunda-mano/
Body: {"categoryId":2500,"sortBy":"relevance","sortOrder":"DESC",
       "pagination":{"page":N,"size":100},      # pagination MUST be nested; top-level "page" is ignored
       "price":{"from":null,"to":null},"year":{...},"km":{...}}
Tool: curl_cffi impersonate="chrome131"  ·  no proxy, no cookie
Scale: ~2,728 requests @ size=100 for 272,706 cars.
```
Trap: the intel host `ms-mt--api-web.spain.advgo.net/search` is a **dead internal SSR
origin** (CloudFront 502, DNS unresolvable). The live public gateway is `web.gw.coches.net`.
The same gateway is **tenant-gated to `coches`** → 403 for every milanuncios tenant string.

### 2.3 autocasion — open GraphQL (per-ad) + PDP JSON-LD (dealer)
```
# counter/page math (search list resolver is gated → ads[] = [null,...]; use total/pages only)
POST https://gql.autocasion.com/graphql/  → search(...){paginatedAds{total pages}} = 115,179 / 4,800
# per-ad hydrate (OPEN, no auth):
POST https://gql.autocasion.com/graphql/  → { ad(adId:N){ ...car... } }      # advertiser is null here
# dealer attribution (public): GET the PDP, parse application/ld+json
GET https://www.autocasion.com/coches-ocasion?page={1..4800}   # enumerate -ref{ID} links
GET https://www.autocasion.com{pdp_url}  → ld.offers.offeredBy (AutoDealer name/@id/phone/address)
Tool: curl_cffi impersonate="chrome131"  ·  Cloudflare permissive (DYNAMIC, no challenge)
```
GraphQL introspection is fully open. Dealer (`advertiser`) is login-gated on GraphQL → take
it from the **public PDP JSON-LD `offeredBy`** instead.

### 2.4 motor_es — SSR census driver + PDP JSON-LD
```
GET https://www.motor.es/segunda-mano/coches/?pagina={N}     # 22 cards/pg, zero overlap, ~2,316 pages
   parse: data-goto (base64→PDP url) · data-id · title
GET https://www.motor.es/segunda-mano/anuncio/{id}/          # PDP JSON-LD[0] @type:Car
   price=offers.price · dealer=offers.seller.name · + /concesionarios/{prov}/{slug}/ link
Live total: GET .../get-data-ajax/ (X-Requested-With:XMLHttpRequest) → total=50,938 (seed-10 only, NOT a paginator)
Tool: curl_cffi impersonate="chrome131"  ·  Cloudflare permissive; one GET mints PHPSESSID
```
Canonical PDP is `/segunda-mano/anuncio/{id}/` (robots-clean); the **legacy `/vercoche/`
path is robots-disallowed** — do not use it. **VIN is a static dummy** (same value across
different cars) — key on native `id`, not VIN.

### 2.5 coches_com — sitemap walk + `__NEXT_DATA__`
```
GET https://www.coches.com/sitemap.xml → /sitemap/vo.xml → /sitemap/coches/Todo-VO-{0..3}.xml
   ~100k PDP <loc>:  /coches-segunda-mano/{slug}.htm?id={visibleId}
GET {pdp_url}  → <script id="__NEXT_DATA__">  props.pageProps.data.classified
   dealer = classified.dealer{name,uuid,crmId,type,taxIdNumber}   # crmId = canonical dealer key
Encoding: decode r.content.decode("utf-8") (do NOT trust r.text → mojibake on accents)
Tool: curl_cffi impersonate="chrome131"  ·  no proxy, no cookie replay
```
Imperva/Incapsula sits behind CloudFront but is **passive today** — serving sitemaps + PDPs +
`__NEXT_DATA__` to plain chrome131. **Decaying-open window**: watch for an Incapsula
interstitial / 403; escalate to camoufox warm-up only if it flips to active challenge.

### 2.6 wallapop — internal search API (geo-honored, JWT pagination)
```
GET https://api.wallapop.com/api/v3/search/section
   ?keywords=&category_id=100&latitude=40.4168&longitude=-3.7038
    &order_by=most_relevance&section_type=organic_search_results&search_id={uuid}
Headers: deviceos:0 · x-deviceos:0 · x-appversion:822640 · x-deviceid:{uuid}
         mpid/trackinguserid:{any stable id} · referer/origin: es.wallapop.com
Paginate: feed meta.next_page (a JWT) back as ?next_page=<jwt>; 40 items/pg
Dealer: item.user_id → GET /api/v3/users/{id} → type:"professional" + web_slug
Tool: curl_cffi impersonate="chrome131"  ·  no proxy, no auth bearer
```
Trap: `/api/v3/cars/search` returns 200 but **always empty** and **ignores lat/long** (legacy
dead stub — the endpoint in the original intel). `/api/v3/general/search` is **CloudFront
403**. Only `/api/v3/search/section` is the live, un-walled path.

### 2.7 milanuncios — camoufox warm-session DOM scrape (only T1 platform)
```
1. camoufox(headless=True, os="windows", locale="es-ES", humanize=True)
2. page.goto("https://www.milanuncios.com/", "domcontentloaded"); wait 7s   # mints reese84, passes Imperva
3. click a[href*="coches-de-segunda-mano"]   # IN-PAGE SPA click — a cold goto re-trips the wall
4. mouse.wheel × ~8-15 to lazy-load virtualized cards
5. scrape article.ma-AdCardV2 innerText → make/model/price/year/km/fuel/warranty + a[href*=".htm"] PDP
Scale: shard the query (province/make/price/year band) under the 10k-ad display cap to reach ~667k
```
**Load-bearing trick:** the `reese84` cookie minted on the homepage **plus the in-page
(SPA) referer transition** is what unlocks the SRP. **Cold `page.goto()` of a listing/PDP
re-walls even with valid cookies** — every navigation must be an in-page click. Vanilla
Playwright/Chromium is detected (WALLED); **camoufox is required**. No JSON search API
exists (server-rendered), and the shared `web.gw.coches.net` gateway is tenant-gated → 403
for milanuncios.

---

## 3. Free now (all 7)

`spoticar` · `coches_net` · `autocasion` · `motor_es` · `coches_com` · `wallapop` ·
`milanuncios` — all pulled real cars with dealer attribution at €0 this sweep.

## 4. Genuinely walled (needs spend): **none**

No platform showed all free vectors exhausted-and-failed. The hardest case
(milanuncios, double-walled with Imperva `reese84` + Adevinta GeeTest) was still beaten by
a **free** stealth browser (camoufox) with no proxy and no paid IP — so it counts as FREE,
not walled.

---

## 5. Cross-cutting patterns (for the harvest engine)

1. **`curl_cffi` chrome131 is the universal T0 carrier.** 6 of 7 platforms need nothing
   more. The TLS/JA3 + HTTP2 fingerprint — not residential IP — is what defeats Akamai
   (spoticar) and Imperva-passive (coches_com).
2. **The data is almost never where the intel said.** Live wins came from re-derived hosts
   and surfaces: `web.gw.coches.net` (not the dead advgo SSR origin), wallapop
   `/search/section` (not `/cars/search`), motor.es `/segunda-mano/anuncio/` (not legacy
   `/vercoche/`). Always re-probe; trust bytes over registry strings.
3. **Dealer attribution is first-class on every platform** — `seller{}` (coches_net),
   `AutoDealer offeredBy` (autocasion), `classified.dealer.crmId` (coches_com),
   `field_pdv_title` (spoticar), `offers.seller.name` (motor_es), `/users/{id} type`
   (wallapop), card blurb + PDP `seller` (milanuncios). Selling-entity edges are extractable
   free everywhere.
4. **Two paid-looking moats are actually free-passable today:** Akamai (spoticar) yields to
   a TLS fingerprint; Imperva yields either passively (coches_com, curl-readable now) or to
   a free warm-session stealth browser (milanuncios). Both flagged as **decaying-open** —
   re-verify before each large drain; the camoufox/cookie-warm-up escalation is documented
   in each dossier as the held-in-reserve next tier.
5. **`curl_cffi` charset trap:** decode `r.content.decode("utf-8")` explicitly (coches_com);
   `r.text` mis-infers charset and mojibakes Spanish accents.

> **Marking:** every cell in §1 and every recipe in §2 is `[VERIFIED]` from the linked
> dossier (live request, real bytes, real car + dealer). Scale/rate projections inside the
> dossiers are `[ASSUMED]` and tagged there; the access verdicts are not.
