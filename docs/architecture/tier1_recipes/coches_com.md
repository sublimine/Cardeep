# Tier-1 recipe — coches.com (Carossa / Grupo coches.com)

> Status: **HARVESTABLE FREE** — proven live 2026-06-12 with curl_cffi chrome131, **zero proxy**.
> Defense: Imperva/Incapsula active behind CloudFront (`x-cdn: Imperva`) but **serving
> sitemaps + PDPs + `__NEXT_DATA__` to a plain Chrome impersonation today**. Decaying-open
> window — harvest before Imperva escalates to active JS challenge.

## Verdict
- `harvestable_free = true`
- Declared inventory ~200,388 (live SRP counter). VO sitemap exposes **~100,000 PDP URLs**
  (4 shards × 25,000) directly, each with selling-dealer attribution in `__NEXT_DATA__`.
- Winning vectors: **#3 (sitemap walk) + #4 (curl_cffi chrome131)**. No stealth browser, no
  proxy, no CAPTCHA solve required.

## Winning request shape (the recipe)

### Engine
- Tool: `curl_cffi` (v0.15.0), `impersonate="chrome131"`.
- Python: `C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.
- **No proxy. No cookies needed** (Imperva mints `incap_ses_*`/`visid_incap_*` on the fly;
  not required to be replayed for read access today).

### Headers (sufficient set — verified)
```
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: es-ES,es;q=0.9,en;q=0.8
Referer: https://www.coches.com/coches-segunda-mano/        # PDP only; harmless on sitemaps
```
chrome131 impersonation supplies UA + the rest of the Chrome TLS/JA3 + h2 fingerprint.

### Encoding (load-bearing)
Response body is **valid UTF-8**. Decode with `r.content.decode("utf-8")` — do **not** rely on
`r.text` (curl_cffi may infer the wrong charset and produce mojibake on accents). Strict UTF-8
decode is clean (`Híbrido Gasolina`, `Automática`, `Málaga`).

## Enumeration (sitemap walk — vector #3)

```
GET https://www.coches.com/sitemap.xml                       -> 200, sitemapindex
  -> https://www.coches.com/sitemap/vo.xml                   -> 200, sitemapindex (VO branch)
     -> https://www.coches.com/sitemap/coches/Todo-VO-0.xml  -> 200, 25,000 <loc> PDP URLs
     -> https://www.coches.com/sitemap/coches/Todo-VO-1.xml  -> 200, 25,000
     -> https://www.coches.com/sitemap/coches/Todo-VO-2.xml  -> 200, (~25,000)
     -> https://www.coches.com/sitemap/coches/Todo-VO-3.xml  -> 200, (~25,000)
```
Sibling branches off `sitemap.xml`: `vn.xml` (new cars), `renting.xml`, `vo/site_search.xml`,
`site_landing.xml`. PDP `<loc>` shape:
`https://www.coches.com/coches-segunda-mano/{slug}.htm?id={visibleId}`
The `?id=` value == `classified.visibleId`. Parse `<loc>` with a simple regex; each Todo-VO
shard is ~6 MB XML.

## PDP fetch + extraction (vector #4)

```
GET https://www.coches.com/coches-segunda-mano/{slug}.htm?id={visibleId}   -> 200 (~180 KB HTML)
```
Two usable surfaces in every PDP, both live:

1. **`__NEXT_DATA__` (PRIMARY — has dealer attribution).** Extract:
   `<script id="__NEXT_DATA__" type="application/json">…</script>`
   Path: `props.pageProps.data.classified`.
2. **JSON-LD (secondary — car only, no seller).** Two `application/ld+json` blocks:
   `Product/Offer/Car/Place` (price, brand, model, mileage, place) and `BreadcrumbList`
   (gives municipality, e.g. "Arganda del Rey"). LD `offers[0].seller` is `null` — use
   `__NEXT_DATA__` for the dealer.

### Field map — `props.pageProps.data.classified`
```
listing_ref     <- visibleId            # == ?id= in URL ; also externalId (provider ref)
make            <- make.name
model           <- model.name
version         <- version.name (+ version.providerId)
year            <- registration.year
month           <- registration.month
plate           <- registration.plate
vin             <- registration.vin     # often null
km              <- mileage.amount  (unit mileage.unit)
price           <- price.amount  (price.currency)        # list price
price_offer     <- priceOffer.amount    # "precio contado"/financed offer (lower)
fuel            <- fuel.name             # UTF-8: "Híbrido Gasolina", "Diésel", "Gasolina"
transmission    <- transmission.name     # "Automática" / "Manual"
color           <- color.original (color.name normalized)
body            <- body.name
province        <- currentProvince.{id,name}   # id == INE 2-digit province code (e.g. 28 Madrid)
is_km0          <- isKm0
is_stock        <- isStock
image_list      <- imageList[]
description      <- description
created_at      <- createdAt ; updated_at <- updatedAt

# DEALER (selling entity) — classified.dealer
dealer_name     <- dealer.name
dealer_uuid     <- dealer.uuid
dealer_crm_id   <- dealer.crmId          # stable internal dealer id, e.g. "D1295"
dealer_type     <- dealer.type           # AUTHORIZED | (others)
dealer_tax_id   <- dealer.taxIdNumber    # CIF/NIF when present (often "")
dealer_emails   <- dealer.emailList[]    # often []
dealer_extra    <- dealer.{multiprovince,isCpl,isFordSelection,showroomList}
```
Note: `classified.externalDealerId` + `classified.feeder` identify the upstream feed; `crmId`
is the coches.com-canonical dealer key for dedup/attribution.

## Verified sample cars (pulled live 2026-06-12, free path, no proxy)

| make/model/version | price | km | year | province | dealer (type/crmId) |
|---|---|---|---|---|---|
| TOYOTA C-HR 125H Active | 16,490 EUR (offer 14,990) | 154,300 | 2021 | Madrid (28) | **Subastacar** (AUTHORIZED/D1295) |
| FORD Focus 1.0 Ecoboost MHEV ST-Line 155 Aut. | 18,500 EUR | 58,495 | 2024 | Sevilla | Automares Peugeot Sevilla (AUTHORIZED/D148) |
| MERCEDES Clase E E Estate 220 BT 9G-Tronic | 24,990 EUR | 91,541 | 2018 | Madrid | OcasionPlus (AUTHORIZED/D1166) |
| HYUNDAI Tucson 1.6 TGDI Klass 4x2 | 19,090 EUR | 95,300 | 2023 | Madrid | Flexicar (AUTHORIZED/D4706) |
| BMW X2 sDrive 18iA | 23,590 EUR | 52,946 | 2022 | Madrid | HR Motor (AUTHORIZED/D561) |

Primary sample (for harness): **TOYOTA C-HR 125H Active — 16,490 EUR — Subastacar (Madrid)**.
URL: `https://www.coches.com/coches-segunda-mano/ocasion-toyota-c-hr-122-125h-active.htm?id=jLhWqHiKv65W`

## Harvest plan
1. Walk `sitemap.xml -> vo.xml -> Todo-VO-{0..3}.xml`, collect ~100k `(visibleId, url)`.
   (Add `vn.xml` branch for VN/Km0 stock if in scope.)
2. Fetch PDPs with the engine above, throttle ~0.6–0.9 s/req (single IP held today).
3. Extract `classified` from `__NEXT_DATA__`; emit vehicle + dealer edge (dealer.crmId as the
   selling-entity key). Cross-check price/place against JSON-LD Product/Offer block.
4. **Watch for the wall:** first sign of escalation = PDP returns an Imperva interstitial
   (`Request unsuccessful. Incapsula incident ID`, JS-redirect `_Incapsula_Resource`, or 403).
   On that signal, escalate to vector #5/#6 (camoufox/nodriver homepage warm-up to mint a
   benign `incap_ses_*` cookie, then replay) — not needed today.

## Per-vector log (8 free vectors)

1. **Internal/open JSON or GraphQL API** — Not needed. `__NEXT_DATA__` SSR blob on the PDP
   already carries the full structured `classified` (vehicle + dealer) JSON inline. Dedicated
   XHR/GraphQL search API not pursued because the SSR surface is complete and cheaper.
   **Outcome: not required (SSR JSON sufficient).**
2. **Mobile app API** — Not attempted. Web SSR surface already yields full car+dealer for free;
   no defensive wall to route around. **Outcome: unnecessary.**
3. **Sitemap of PDPs** — **WORKS.** `sitemap.xml`→`vo.xml`→`Todo-VO-{0..3}.xml` all HTTP 200;
   ~100k PDP `?id=` URLs enumerated. **Outcome: SUCCESS (enumeration vector).**
4. **curl_cffi chrome131** — **WORKS.** SRP/PDP/sitemaps all 200 to chrome131 impersonation,
   no proxy, no cookie replay; `__NEXT_DATA__` + JSON-LD parse clean; 5/5 PDPs from a second
   shard returned full vehicle + dealer. **Outcome: SUCCESS (fetch vector). PRIMARY RECIPE.**
5. **Stealth browser (camoufox/patchright/nodriver/SeleniumBase UC)** — Not needed today
   (curl path 200s). Documented as the escalation path if Imperva flips to active challenge:
   homepage warm-up to mint `incap_ses_*`, export cookies to curl_cffi. **Outcome: held in reserve.**
6. **BotBrowser/Byparr/FlareSolverr-successors** — Not needed (no Akamai/Kasada/Cloudflare
   interactive challenge encountered; Imperva passive today). **Outcome: held in reserve.**
7. **Free datacenter proxy rotation (requests-ip-rotator/cloudproxy)** — Not needed; single IP
   served ~7 sequential PDPs + 6 sitemaps with zero rate-limit/ban. Reserve for when per-IP
   rate walls appear during full ~100k harvest. **Outcome: held in reserve.**
8. **Header/cookie/referer warm-up + TLS variation** — Minimal set already sufficient (Accept,
   Accept-Language, Referer). No warm-up sequence required. **Outcome: unnecessary today.**

**Conclusion:** Free path confirmed at vectors #3+#4. Vectors #5–#8 are escalation reserves,
explicitly unneeded for the current decaying-open window. €0, no proxy, real cars + dealer
attribution pulled live.
