# Recipe — motor.es (ES) · OPEN · FREE PATH PROVEN

**Status:** ✅ HARVESTABLE FREE — no proxy, no browser, no solver. Pulled real
cars with full dealer attribution via curl_cffi alone (verified live 2026-06-12).

**Declared inventory:** ~50,938 used cars (`total` field, live counter on
`get-data-ajax`; page `<title>` said "50.769" same sweep — counter is live).

**Owner:** Motor Internet S.L. (taxID B73634099, Lorca/Murcia). Editorial site +
classifieds aggregator. Stack: Cloudflare (permissive) over a PHP backend (PHPSESSID,
server-side rendered HTML). NOT Next.js — no `__NEXT_DATA__`; data is in SSR HTML
cards + JSON-LD on PDPs + an internal JSON AJAX endpoint.

---

## TL;DR — the working recipe

Two FREE surfaces, both 200 to `curl_cffi` impersonate=chrome131, no warm-up needed
beyond one GET to mint `PHPSESSID`:

1. **Enumerate** the full census by draining the SSR listing page with `?pagina=N`:
   `https://www.motor.es/segunda-mano/coches/?pagina=N`  → **22 cards/page**, zero
   overlap between pages, ~2316 pages for 50,938 cars. Each card carries `data-id`
   and a base64 `data-goto` that decodes to the canonical PDP URL.
2. **Enrich** each car from its PDP `https://www.motor.es/segunda-mano/anuncio/{id}/`
   → JSON-LD `@type:Car` (price, fuel, model, brand, km, **offers.seller.name = the
   selling dealer**) + a dealer profile link `/concesionarios/{provincia}/{slug}/`.

A lighter JSON endpoint (`get-data-ajax`) exists but only serves the first 10
(featured/scroll-seed); it is NOT the paginator. Use `?pagina=N` HTML for the census.

---

## Engine / access

- **Engine:** `curl_cffi` Session, `impersonate="chrome131"`. (Project `FetchEngine`
  in `pipeline/engine/fetch.py` is exactly this — reuse it.)
- **is_tier1:** false. OPEN. Cloudflare returns `server: cloudflare`, `cf-ray:*-ZRH`,
  HTTP 200 on first hit. No managed challenge, no JS challenge, no cookie warm-up
  required (a plain GET already mints PHPSESSID; not even needed for the HTML drain).
- **Anthropic/stdlib UA:** untested here, but project convention (AS24) is Chrome UA
  over Chrome TLS. Keep impersonate on.
- **Rate (verified):** 6 listing pages in 1.3 s, all 200, 22 cards each, no 429, no
  challenge. Cloudflare permissive. Still apply the engine's polite 0.7–1.4 s jitter
  for a multi-thousand-page drain; this was a burst probe, not a sustained load test.

## robots.txt (verified 2026-06-12) — what is and isn't allowed

```
Disallow: /vercoche/*                  <- the LEGACY/walled PDP path (do NOT use)
Disallow: /*/set-navegacion-session/   <- session-state writer (not needed; see below)
Disallow: /api/*
Disallow: /vercoche/getNavegacionFicha
... (formula-1, noticias, procesos, cdn-cgi, acceso-usuarios)
```

CRITICAL: the intel's "`/vercoche/` PDP robots-disallowed" is correct but that is the
**old route**. The live canonical PDP is **`/segunda-mano/anuncio/{id}/`** and is
**NOT disallowed**. The listing `/segunda-mano/coches/` and its `get-data-ajax/` are
also not disallowed. So the entire harvest path is robots-clean.

---

## SURFACE A — listing enumerator (the census driver)

**Request**
```
GET https://www.motor.es/segunda-mano/coches/            (page 1)
GET https://www.motor.es/segunda-mano/coches/?pagina=N   (page N, N>=2)
Headers: Referer: https://www.motor.es/segunda-mano/coches/
Impersonate: chrome131
```
- 22 `<article class="elemento-segunda-mano">` cards per page. Verified pages 1/2/3/4/5/6
  each returned 22 cards with **zero id overlap** (66 unique across first 3 pages).
- 50,938 / 22 ≈ **2,316 pages** to drain the full census.

**Per-card extraction (regex on the SSR HTML)**
```python
CARD = re.compile(r'data-goto="([^"]+)"\s+data-id="(\d+)"\s+title="([^"]*)"')
# data-id   -> motor.es native listing id (e.g. 23601273)
# data-goto -> base64(PDP url): base64.b64decode(goto) -> /segunda-mano/anuncio/{id}/
# title     -> full vehicle name (HTML-entity encoded: unescape &amp; -> &)
```
Card also embeds the eco label (`eco-img .../etiquetas/{c|b|0|eco}.svg`) and the
photo gallery (`miniaturas-data` value = JSON array of image URLs).

## SURFACE B — internal JSON AJAX (rich, but first-10 only)

**Request**
```
GET https://www.motor.es/segunda-mano/coches/get-data-ajax/
Headers:
  X-Requested-With: XMLHttpRequest
  Referer: https://www.motor.es/segunda-mano/coches/
  Accept: application/json, text/javascript, */*; q=0.01
```
Returns `application/json`:
```json
{"ok":true,"data":{"pagina":"1","size":10,"total":50938,"hits":[ ... 10 ... ]},
 "expires":..., "session_navigation":{...}, "guarda_busqueda_block":...}
```
- **Use it for:** the live `total` (denominator proof) and rich machine-readable
  fields on the seed-10 without an HTML parse.
- **Do NOT use it for pagination.** It ignores `?pagina=`, `?page=`, `?p=`, POST body,
  and path variants (`/pagina-2/get-data-ajax/` → 404) — always returns page 1, size 10.
- `set-navegacion-session/` accepts `{listado_referrer, pagina}` and returns
  `status:ok`, BUT it only records "where the user was" (back-button memory); it does
  NOT change what `get-data-ajax` then serves, and it is robots-disallowed. Ignore it.

**`hits[]` field map (richer than card HTML)**
```
id                       -> native listing id
nombre                   -> title
marca {nombre,url}       -> make + slug
modelo {nombre,url}      -> model + slug
matriculacion {anno,mes} -> registration year/month
kilometros               -> mileage (int)
potencia                 -> hp (int)
combustible              -> fuel ("Diesel"/"Gasolina"/...)
eco                      -> DGT eco label ("c","b","0","eco")
precio {base,venta,descuento,iva}  -> price (venta = sale price, EUR)
financiacion {precio,cuota}        -> monthly quote
url                      -> canonical PDP /segunda-mano/anuncio/{id}/
imagen, fotos[], fotos_opt[]       -> gallery (fotos_opt = CDN-resized)
vendedor {id, poblacion, provincia, url_provincia, telefono{movil,fijo}}  -> SELLER
renting, stock, origen, ficha_externa, id_tipo
```
`vendedor.id` (e.g. 1103605) is the dealer's native id; `provincia`+`url_provincia`
+ `poblacion` + phone give location attribution without touching the PDP.

## SURFACE C — PDP enrichment + dealer attribution

**Request**
```
GET https://www.motor.es/segunda-mano/anuncio/{id}/
Impersonate: chrome131   (200, ~116 KB, robots-clean)
```
Two JSON-LD blocks:
- `<script type="application/ld+json">` **[0] = `@type:Car`** — the vehicle:
```
name                                  -> title
brand.name                            -> make
model                                 -> model
fuelType                              -> fuel
itemCondition                         -> UsedCondition
mileageFromOdometer.value (KMT)       -> km
vehicleIdentificationNumber           -> VIN  ⚠ SEE CAVEAT
offers.price + offers.priceCurrency   -> price EUR
offers.availability                   -> InStock
offers.seller.name                    -> **SELLING DEALER NAME**  (attribution)
description                           -> free text (often names dealer + address)
```
- [1] = `@type:Organization` is the **publisher (Motor.es itself)**, NOT the dealer —
  do not mistake it for the seller. The dealer is `offers.seller.name`.

**Dealer profile link** (also on PDP, scrape with):
```python
re.findall(r'/concesionarios/[a-z0-9-]+/[a-z0-9-]+/', body)
# e.g. /concesionarios/tenerife/bonocasion/  -> {provincia}/{dealer-slug}
```
This is the per-dealer page (enumerable for a dealer registry + dual-membership edge:
vehicle.entity = selling dealer; platform_listing edge = motor.es <-> vehicle).

⚠ **VIN CAVEAT:** the JSON-LD `vehicleIdentificationNumber` returned the SAME value
(`1G6DP5ED5B7244892`) on two different cars (a Peugeot Rifter and a Lamborghini Urus).
It is a placeholder/static dummy, NOT a real per-car VIN. Treat VIN as UNRELIABLE on
motor.es; use `id` (native listing id) + PDP url as the stable vehicle key. The
`vendedor.id` from Surface B is the dealer key.

---

## Proof — real cars pulled FREE (verified live 2026-06-12)

| field | car 1 | car 2 |
|---|---|---|
| id | 23601273 | (page 2 card 0) |
| make/model | Peugeot Rifter Allure BlueHDi 130 | Lamborghini Urus Performante 666CV |
| price | **21.990 EUR** | **495.000 EUR** |
| km | 116.492 | 1.500 |
| fuel | Diesel | (per PDP) |
| dealer (offers.seller.name) | **BONOCASION** | **TREND CARS \| Tu concesionario MULTIMARCA** |
| dealer profile | /concesionarios/tenerife/bonocasion/ | (per PDP) |
| location (Surface B vendedor) | Santa Cruz de Tenerife / Tenerife / tel 609018208 | — |

SAMPLE CAR: **Peugeot Rifter Allure BlueHDi 130 — 21.990 EUR — dealer BONOCASION
(Santa Cruz de Tenerife)**, PDP https://www.motor.es/segunda-mano/anuncio/23601273/

---

## Recommended harvest algorithm

```
1. seed = GET get-data-ajax  -> read total (denominator), capture seed-10 rich JSON.
2. for N in 1..ceil(total/22):
     GET /segunda-mano/coches/?pagina=N  (engine polite jitter 0.7-1.4s)
     parse 22 cards -> {id, pdp, title}; dedup by id (sort is age-desc but stable
     enough across a fast drain; dedup defends against churn at the head).
3. for each unique id:
     GET /segunda-mano/anuncio/{id}/ -> JSON-LD[0] Car (price, make, model, km, fuel,
     offers.seller.name) + /concesionarios/{prov}/{slug}/ dealer link.
   (Optional cheaper path: for the seed-10 and any card you can match, Surface B JSON
    already has price+vendedor without a PDP hit; PDP needed for seller.name on the rest.)
4. attribution: vehicle.entity = dealer (offers.seller.name + /concesionarios/ slug +
   vendedor.id/provincia/telefono); platform edge motor.es <-> vehicle.
```

## Field stability / churn

- listing sort = newest-first; head of list rotates as cars are added/sold. Dedup by
  `id` across the whole drain. `publicado` (unix ts) on Surface B lets you watermark.
- `total` is a live counter; expect small drift between the count read and drain end.

---

## Vectors tried (8) — outcome log

1. **Internal/open JSON/GraphQL API** — ✅ FOUND `get-data-ajax` (200 application/json,
   total+hits). Rich but first-10 only; not a paginator. Used for denominator + seed.
   The real census paginator is the SSR HTML `?pagina=N` (Surface A). No GraphQL.
2. **Mobile app API** — NOT NEEDED. Web free path fully sufficient (full census +
   price + dealer). Not probed; documented as unnecessary, not as a wall.
3. **Sitemap of PDPs + JSON-LD/__NEXT_DATA__** — ✅ PDP JSON-LD `@type:Car` is the
   enrichment surface (price, dealer via offers.seller.name). No `__NEXT_DATA__` (PHP
   site, not Next). `sitemap_vo.xml` has category URLs per intel; not needed since the
   `?pagina=N` listing already enumerates every id.
4. **curl_cffi browser impersonation (chrome131)** — ✅ THE CARRIER. Every 200 above
   came through plain curl_cffi impersonate=chrome131, no proxy. Cloudflare permissive.
5. **Stealth browser (camoufox/patchright/nodriver/SeleniumBase)** — NOT NEEDED. No JS
   challenge, no DataDome, no cookie wall. curl alone suffices. Not invoked.
6. **BotBrowser/Byparr/FlareSolverr** — NOT NEEDED (no Akamai/Kasada/CF-interactive).
7. **FREE datacenter proxy rotation (requests-ip-rotator/cloudproxy)** — NOT NEEDED.
   6-page burst in 1.3 s with zero 429/challenge from a single IP. Apply engine polite
   jitter for the full 2,316-page drain; revisit only if a sustained drain trips a wall.
8. **Header/cookie/referer warm-up + TLS variation** — minimal applied: one GET mints
   PHPSESSID; Referer set to the listing root on AJAX/paginated GETs. No TLS variation
   needed. Sufficient.

**Conclusion:** FREE path PROVEN on vectors 1+3+4. Vectors 2,5,6,7,8 not required —
documented as unnecessary (no wall hit), not as dead ends.
