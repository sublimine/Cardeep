# Autocasion — free-harvest recipe & 8-vector dossier

> **Platform:** autocasion.com (Grupo Luike / Vocento). Dealer-focused ES classifieds.
> **Declared inventory:** ~122k. **Live counter this sweep (2026-06-12):** GraphQL
> `search.paginatedAds.total = 115,179`. **Verdict:** OPEN — fully harvestable FREE
> (curl_cffi, Chrome131 impersonation, €0 proxies, no auth, no browser, no captcha).
> Cloudflare is permissive (`server: cloudflare`, `cf-cache-status: DYNAMIC`, no JS
> challenge to a Chrome TLS fingerprint).
>
> Every claim below is `[VERIFIED]` — fetched live with the project python
> (`C:/Users/elias/AppData/Local/Programs/Python/Python311/python`) + `curl_cffi 0.15.0`,
> 2026-06-12. No `[ASSUMED]` in the working recipe.

---

## TL;DR — the working free path

Three independent free surfaces, all live, no proxy/auth/browser:

1. **GraphQL `ad(adId:N)`** at `https://gql.autocasion.com/graphql/` — returns the
   FULL structured car (make/model/year/price/km/fuel/transmission/province/url) for
   any ad id, **no auth, no token**. (Dealer/`advertiser` is null on this resolver.)
2. **GraphQL `search`** — returns the correct `total`/`pages` (the live counter +
   enumeration math) but the `ads[]` list resolves to `[null,...]` (list resolver is
   gated; per-ad resolver is NOT). Use it for the **counter + page math only**.
3. **PDP JSON-LD** — every detail page embeds one `application/ld+json` `Product`
   block whose `offers.offeredBy` is the **`AutoDealer`** (name, `@id` dealer page,
   telephone, full `PostalAddress`) and whose `offers.itemOffered` is the full `Car`.
   **This is the dealer-attribution surface.**

**Canonical enumeration** = the SSR results page `/coches-ocasion?page=N`
(N = 1..4800, ~24–26 cards/page, clamps past the end). Each card carries a
`-ref{ID}` PDP link. Drain the pages → harvest `(url, id)` → hydrate via GraphQL
`ad()` and/or parse the PDP JSON-LD for the dealer.

---

## The recipe (reproducible)

**Engine:** `pipeline/engine/fetch.py` (`FetchEngine`, `curl_cffi` `impersonate="chrome131"`),
one session = one fingerprint = one cookie jar for the whole drain.

**Headers (HTML/SSR + PDP):**
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept-Language: es-ES,es;q=0.9,en;q=0.8
```

**Headers (GraphQL POST):** as above plus
```
Accept: application/json
Content-Type: application/json
Origin: https://www.autocasion.com
Referer: https://www.autocasion.com/coches-segunda-mano
```

### Step 1 — counter + page math (GraphQL `search`)
```
POST https://gql.autocasion.com/graphql/
{"query":"query S($p:[SearchParamInput],$page:Int,$ipp:Int){search(params:$p,page:$page,itemsPerPage:$ipp){paginatedAds{total pages itemsPerPage}}}",
 "variables":{"p":[],"page":1,"ipp":24}}
```
→ `total=115179`, `pages=4800` @ itemsPerPage=24. (Sets the drain size; `ads[]` here is null — do not rely on it.)

### Step 2 — enumerate ad URLs/IDs (SSR results pages)
```
GET https://www.autocasion.com/coches-ocasion?page={1..4800}
```
Extract PDP links + ids:
```
href="(/coches-[^"]*-ref(\d+))"
```
~24–26 PDP refs per page. Pages past the last clamp to the final page (page=4800==4801),
so stop when the id-set stops changing (id-dedup across pages, not page position — the
live-set-shifts hazard of `02-SCRAPING-ENGINE.md §0`).

### Step 3a — hydrate the car (GraphQL `ad`, cheapest, structured)
```
POST https://gql.autocasion.com/graphql/
{"query":"{ ad(adId:19038696){ id title price finalPrice kilometers year month km0 certificated url slug fuel{name} transmission{name} brand{name} family{name} province{name} } }"}
```
→ full car. **`advertiser` is null on this resolver** — get the dealer from Step 3b.

### Step 3b — dealer attribution (PDP JSON-LD)
```
GET https://www.autocasion.com{pdp_url}
```
Parse the single `application/ld+json` block:
```
offers.price / offers.priceCurrency                → price
offers.offeredBy.@type   == "AutoDealer"
offers.offeredBy.name                              → dealer name
offers.offeredBy.@id     (/profesional/{slug})     → dealer entity page
offers.offeredBy.telephone                         → dealer phone
offers.offeredBy.address.{streetAddress,addressLocality,postalCode,addressCountry}
offers.itemOffered.@type == "Car"  {manufacturer, model, productionDate(year),
                                    vehicleTransmission, numberOfDoors,
                                    mileageFromOdometer.value(km), vehicleEngine, identifier}
brand.name                                         → make (fallback)
name                                               → full title
image[0]                                           → photo
```
One PDP fetch yields BOTH the full car AND the full dealer — so Step 3a (GraphQL) is
optional; the PDP alone is a complete record. Use GraphQL `ad()` when you want car
fields without the per-PDP fetch (e.g. fast counter/price refresh), and the PDP when
you need the dealer.

### Field map (canonical, GraphQL `Ad` + PDP JSON-LD)
```
listing_ref     : ad.id  |  ld.offers.itemOffered.identifier   (autocasion native id; == -ref{ID})
deep_link       : "https://www.autocasion.com" + ad.url
make            : ad.brand.name  |  ld.offers.itemOffered.manufacturer
model           : ad.family.name |  ld.offers.itemOffered.model
title           : ad.title       |  ld.name
year            : ad.year        |  ld.offers.itemOffered.productionDate
km              : ad.kilometers  |  ld.offers.itemOffered.mileageFromOdometer.value
price           : ad.price       |  ld.offers.price            (EUR; ld.offers.priceCurrency)
fuel            : ad.fuel.name
transmission    : ad.transmission.name | ld.offers.itemOffered.vehicleTransmission
province        : ad.province.name
photo_url       : ad.image.url   |  ld.image[0]
km0             : ad.km0
certificated    : ad.certificated
dealer          : ld.offers.offeredBy {name, @id(/profesional/slug), telephone,
                  @type=AutoDealer, address{streetAddress, addressLocality, postalCode, addressCountry=ES}}
```

---

## Proof — real cars actually pulled (FREE path, 2026-06-12)

Full chain (SSR enumerate → GraphQL `ad()` hydrate → PDP JSON-LD dealer):

| make/model | year | price | km | fuel/trans | province | dealer (AutoDealer) | city CP |
|---|---|---|---|---|---|---|---|
| MERCEDES-BENZ Clase CLA 220d | 2021 | 33.490 € | 85.516 | — | Madrid | **AUTOS MADRID MÓSTOLES** | Móstoles 28933, Calle Alquimia 2 |
| MERCEDES-BENZ Clase SL AMG 43 | 2023 | 109.990 € | 1.900 | Automático | — | **PALACIOCASIÓN** (`/profesional/palaciocasion`) | Lugones 33420, Avd. de Gijón 21 |
| CITROEN C4 1.4i 16v Collection | 2006 | 5.500 € | 60.000 | Gasolina/Manual | Alicante | **TADER CARS** (`/profesional/taderautomocion-1526747`) tel 966678599 | Elche 03293 |
| AUDI A3 1.4 TFSI Sport Edition | 2017 | 21.850 € | 125.000 | Manual | — | **MORALAUTO** (`/profesional/moralauto-1315165`) tel 958590820 | La Zubia 18140 |
| PEUGEOT 508 1.5 BlueHDi Allure | 2019 | 16.950 € | 88.649 | Manual | — | **AUTOS MORALES ESURY** tel 609412136 | Ayamonte 21400 |
| FORD Mustang Mach-E RWD | 2020 | 23.950 € | 76.668 | Eléctrico/Automático | Madrid | (GraphQL-only pull; dealer via PDP) | — |
| LAMBORGHINI Urus SE | 2025 | 350.000 € | 6.500 | Híbrido Enchufable/Aut. | Málaga | (km0) | — |

**Sample car (one, fully attributed):** CITROEN C4 1.4i 16v Collection, 2006, 5.500 €,
60.000 km — dealer **TADER CARS** (AutoDealer, tel 966678599, Avda. de l'Alcalde Ramón
Pastor 6, ELCHE 03293), PDP
`https://www.autocasion.com/coches-segunda-mano/citroen-c4-ocasion/c4-1-4i-16v-collection-ref19869721`.

---

## GraphQL schema (introspectable — no auth)

`https://gql.autocasion.com/graphql/` is a Symfony `overblog/graphql-bundle` endpoint.
Introspection is **fully open** (`{__schema{...}}` → 200). Key surface:

- `search(params:[SearchParamInput], config:[SearchFilterElementConfigInput], page:Int, itemsPerPage:Int): Search`
  - `Search.paginatedAds: PaginationAds {page, pages, itemsPerPage, total, hasNext, hasPrevious, ads:[Ad]}`
  - `SearchParamInput { key:String!, value:String! }` (simple k/v filter pairs)
  - **Gate:** `paginatedAds.total/pages` resolve correctly; `ads[]` returns `[null,...]`
    (list-level Ad resolver is gated). Use `search` for counter/page math only.
- `ad(adId:Int): Ad` — **OPEN**, returns the full car for any id. `advertiser` field null.
- `Ad { id, title, name, price, finalPrice, dealPrice, kilometers, year, month, plate,
   url, slug, km0, demo, certificated, automatic, horsePower, doors, monthsGuarantee,
   fuel{name}, transmission{name}, brand{id,name,slug}, family{id,name,slug},
   province{id,name,slug}, image{url,...}, gallery{...}, advertiser{id,name,isAS24,...}(null), ... }`
- Helper resolvers (all OPEN, useful for filter vocab / dealer pages): `brands`, `families`,
  `fuels`, `bodyworks`, `provinces`, `product(id)`, `ratingStats(advertiserId)`,
  `searchAs`, `searchAP`.

> Note: the `advertiser` object IS rich in the schema (name, contract, stock, ratings,
> stockInfo…) but is null on the public `ad()`/`search` resolvers (login-gated). Dealer
> attribution therefore comes from the **PDP JSON-LD `offeredBy`**, which is public.

---

## robots.txt posture (verified)

`User-agent: *` does **NOT** disallow the listing path `/coches-ocasion` or PDPs
`/coches-segunda-mano/…-ref{ID}`. It disallows only specific `/api/*` stat/tracking/partial
endpoints, policy pages, `/movil*`, `/cdn-cgi/`. Two declared sitemaps
(`actualidad/sitemap_index.xml`, `uploads/sitemap.xml`) are **editorial/uploads, not a PDP
sitemap** — so SSR pagination (`/coches-ocasion?page=N`) is the canonical enumeration, not a
sitemap walk. (The blanket `Disallow: /` block applies only to a named bot blacklist —
TurnitinBot, PetalBot, Baiduspider, Yandex, etc. — not to `*`.)

---

## The 8 free vectors — exact outcome each

| # | Vector | Outcome |
|--:|---|---|
| 1 | **Internal/open JSON or GraphQL API** | ✅ **WIN.** `window.__APP_CONTEXT__.endpointGraphql = https://gql.autocasion.com/graphql/`. Introspection OPEN (no auth). `ad(adId:N)` returns full car (200). `search` returns true `total=115179`/`pages` but `ads[]`=`[null,…]` (list resolver gated → use for counter/math). This + PDP JSON-LD is the production recipe. |
| 2 | **Mobile app API** | Not needed. The same `gql.autocasion.com/graphql/` is the app's backend (single GraphQL surface for web+app). The web-origin call already succeeds without device headers, so no separate app host was required. `[NOT NEEDED — vector 1 sufficed]` |
| 3 | **Sitemap of PDPs + JSON-LD** | ⚠ Partial: declared sitemaps are editorial/uploads (no PDP sitemap). BUT **PDP JSON-LD is the win** — every PDP embeds `Product` + `offers.offeredBy=AutoDealer` + `itemOffered=Car` (full dealer + car). Enumeration done via SSR `/coches-ocasion?page=N` (4800 pages × ~24). ✅ for JSON-LD, ✗ for a PDP sitemap. |
| 4 | **curl_cffi browser impersonation (chrome131)** | ✅ **WIN.** Homepage, SRP, results pages, PDPs, robots — all HTTP 200 to `curl_cffi impersonate=chrome131` + Chrome UA. Cloudflare permissive (`cf-cache-status: DYNAMIC`, no challenge). This is the engine for all of vectors 1/3. |
| 5 | **Stealth browser (camoufox/patchright/nodriver/SeleniumBase)** | `[NOT NEEDED]` — no JS challenge, no cookie-minting, no DataDome. curl_cffi alone passes. Would only be a fallback if Cloudflare escalates. |
| 6 | **BotBrowser/Byparr/FlareSolverr (Akamai/Kasada/CF-interactive)** | `[NOT NEEDED]` — no interactive challenge present. |
| 7 | **FREE datacenter proxy rotation (requests-ip-rotator/cloudproxy)** | `[NOT NEEDED]` — no IP-rate/ban wall hit across the probes (counter, schema, results pages, multiple PDPs, all 200 from a single residential IP). Polite-delay engine (`fetch.py` 0.7–1.4s jitter) is enough for the 4800-page drain; rotate only if a 429 wall appears at scale. |
| 8 | **Header/cookie/referer warm-up + TLS variation** | Light warm-up applied (homepage GET to mint `cf` cookies before GraphQL POST; `Origin`/`Referer` set to `www.autocasion.com`). Sufficient. No TLS rotation needed (single chrome131 profile passes). ✅ as a hardening measure, not a requirement. |

**Conclusion:** Vector **1 (GraphQL `ad()`) + Vector 3 (PDP JSON-LD dealer) over Vector 4
(curl_cffi chrome131)** is the complete, reproducible, €0 recipe. Vectors 5–7 unneeded;
8 applied as light hardening. No paid residential IP, no spend, no wall left standing.

## Residual notes
- `search.ads[]` null is a resolver gate, not a wall — fully bypassed by enumerating ids
  from SSR pages and hydrating per-ad. No information lost.
- `advertiser` null on GraphQL → dealer from PDP JSON-LD `offeredBy` (public, complete).
- Counter drift: 115,179 is the 2026-06-12 photo (declared ~122k); re-derive at harvest.
- Scale hygiene: id-dedup across pages (live set shifts), polite jitter; watch for a first
  Cloudflare 403/429 tripwire to escalate to camoufox (vector 5) only if/when it appears.
