# coches.com — FAST Data-Layer Recipe (92,326 cars, 20/req, make-partitioned)

Status: **FASTER UNCAPPED SURFACE FOUND (~20× speedup).** The same SSR
`__NEXT_DATA__` the connector already parses is served on the **SRP listing
page**, not just the PDP — and there it carries **20 full cars per request**
(the complete `classified` shape, dealer + imageList included), vs **1 car per
request** for the current per-PDP connector.
Platform: coches.com (Carossa / Grupo coches.com — independent, Imperva/Incapsula).
Declared inventory (VO): **92,326** (`classifieds.total`, live 2026-06-12; matches the
sitemap's 92,259, +live drift).
Verified LIVE: 2026-06-12 (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy, no browser).

---

## TL;DR — the fast surface

The VO SRP `https://www.coches.com/coches-segunda-mano/{slug}.htm?page=N` is a
Next.js page. Its `__NEXT_DATA__` blob carries
`props.pageProps.classifieds.classifiedList` = **20 fully-populated cars** plus
`classifieds.total`. Same transport as the current PDP recipe (curl_cffi
chrome131, `r.content.decode("utf-8")`), same parse path family — but **20 cars
per HTTP GET instead of 1**.

One hard limit at the data layer: **deep pagination is capped at page 500
(= the 10,000th result)** — a classic Elasticsearch `max_result_window=10000`.
`page=501` → **403** (2,588-byte Imperva block). The unfiltered SRP therefore
reaches only 10,000 of 92,326 (10.8%).

**The fix (MECE partition):** drain **per make**. The page-1 unfiltered SRP
serves `seoData[key="all-makes"]` = **all 93 makes with exact counts**, and
**their counts sum to exactly 92,326 = `classifieds.total`** (every car has
exactly one make → clean, complete partition). **No make is ≥ 10,000**
(max = PEUGEOT 8,345), so every make pages fully within the 10k cap. Per-make
URL = `/coches-segunda-mano/{make-slug}.htm?page=N`.

```
GET https://www.coches.com/coches-segunda-mano/coches-ocasion.htm            # page 1: all-makes list + counts
GET https://www.coches.com/coches-segunda-mano/{make-slug}.htm?page={1..ceil(count/20)}
   -> __NEXT_DATA__ -> props.pageProps.classifieds.classifiedList[20]  (+ .total)
```

Total cost for full inventory: `sum_over_makes(ceil(count/20))` ≈
**~4,620 requests** (92,326 / 20), vs the current **~92,259 PDP GETs**.
**~20× fewer requests, same governor, same UTF-8 decode, same parse.**

---

## Why this is the win (proven LIVE)

| Probe (LIVE 2026-06-12) | Result |
|---|---|
| SRP page 1 `__NEXT_DATA__` | `classifieds.classifiedList` = **20 cars**, `classifieds.total` = **92,326** |
| SRP page 2, page 100 | 200, 20 cards each, **0 overlap** with prior page |
| SRP page 500 (paced, fresh warm session) | 200, 20 cards (= 10,000th car) |
| SRP page **501** | **403** (2,588-byte Imperva block) — bisected: last-OK=500, first-blocked=501 |
| `seoData.all-makes` (93 makes) | **Σ counts = 92,326 = classifieds.total** (exact); **0 makes ≥ 10k** (max PEUGEOT 8,345) |
| `peugeot.htm?page=410` (~8,200th) | 200, 20 cards — **deep paging works inside a make** (cap is per-resultset) |
| `mercedes.htm?page=410` | 200, 20 cards |
| Full drain `ferrari.htm` (small make) | **22 distinct ids harvested == declared total 22**, 2 data pages + empty terminator |

The cap is on the **size of one result set** (10k), not on the platform, so
partitioning the platform into <10k slices unlocks 100%. Make is the cleanest
such partition because the platform itself publishes the per-make counts and
they reconcile to the total to the unit.

---

## Winning request shape (the recipe)

### Engine (identical to the existing coches.com PDP recipe)
- Tool: `curl_cffi` (0.15.0), `impersonate="chrome131"`. No proxy. No cookie warm-up
  required for read (Imperva mints `incap_ses_*` on the fly; not replayed).
- Python: `C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.
- Headers (sufficient set — verified):
  ```
  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
  Accept-Language: es-ES,es;q=0.9,en;q=0.8
  Referer: https://www.coches.com/coches-segunda-mano/
  ```
- **Encoding (load-bearing):** decode `r.content.decode("utf-8")` — NOT `r.text`
  (curl_cffi mis-guesses the charset and mojibakes accents). Same as PDP recipe.

### Extraction
1. `__NEXT_DATA__` regex: `<script id="__NEXT_DATA__" type="application/json">(.*?)</script>`.
2. JSON-parse → `props.pageProps`.
3. Card list: `pageProps.classifieds.classifiedList` (array of 20).
4. Result-set total: `pageProps.classifieds.total`.
5. Make catalogue (page-1 unfiltered SRP only):
   `pageProps.seoData` → block `key=="all-makes"` → `list[]` of `{text, count}`.
   (Sibling block `key=="all-provinces"` exists but province totals exceed 10k —
   e.g. Madrid 53,512, Barcelona 47,791 — so **province is NOT a valid partition**;
   make is.)

### Per-card field map — `classifieds.classifiedList[i]`
The SRP card is a **superset** of the PDP `classified` blob (it adds `imageList`,
`showroomList`, `financing`, `measures` inline). The fields the connector needs:

```
id              <- id              # the stable VO UUID (== PDP classified id; dynx_itemid)
listing_ref     <- visibleId       # == ?id= in the PDP URL ; the public short id
make            <- make.name
model           <- model.name
version         <- version.name (+ version.providerId)
body            <- body.name
year            <- registration.year   (registration.{month,plate,vin})
km              <- mileage.amount  (mileage.unit)
price           <- price.amount    (price.currency)
price_offer     <- priceOffer.amount    # precio contado / financed headline (drop signal when < price)
fuel            <- fuel.name        # UTF-8: "Diésel", "Híbrido Gasolina", ...
transmission    <- transmission.name  # "Manual" / "Automática"
color           <- color.{original,name,id}
power_cv        <- engine.powerCv
pollution_tag   <- pollutionTag     # "C", "ECO", "0", "B"
province        <- currentProvince.{id,name}   # id == INE 2-digit province code
photo_url       <- "https://images.coches.com/_ccom_/" + imageList[0].name   (or the ready `image` field)
image_count     <- imageListLength
created_at      <- createdAt ; updated_at <- updatedAt
phone           <- phone
is_km0/is_stock <- isKm0 / isStock ; category <- category

# DEALER (selling entity) — classifiedList[i].dealer  (same shape as PDP)
dealer_name     <- dealer.name
dealer_uuid     <- dealer.uuid           (== dealerId)
dealer_crm_id   <- dealer.crmId          # stable coches.com dealer key, e.g. "D1295"
dealer_type     <- dealer.type           # AUTHORIZED | ...
dealer_showrooms <- showroomList[] {uuid, phone, province{id,name}, city}  # per-POS geo
```

PDP deep-link (for `vehicle.deep_link`, identical to the sitemap `<loc>`):
`https://www.coches.com/coches-segunda-mano/{slug}.htm?id={visibleId}`. The card
does not ship the SEO slug, but the connector already keys on `(dealer, deep_link)`;
the canonical deep link can be rebuilt from `visibleId` + the make/model/version
slug, or `id`/`visibleId` used directly as the listing_ref (the PDP recipe already
stores `visibleId` as `vin_ref`/`listing_ref`).

---

## Harvest recipe (reproducible)

```
1. Session: curl_cffi, impersonate="chrome131". (Optional: GET https://www.coches.com/ once to warm.)
2. GET /coches-segunda-mano/coches-ocasion.htm   (page 1, unfiltered)
     -> read classifieds.total (sanity vs sitemap ~92,259)
     -> read seoData[all-makes] -> [(make_text, count), ...]   (93 makes; Σ count == total)
3. For each make M with slug s(M) and count c(M):     # every c(M) < 10,000 (verified)
     pages = ceil(c(M) / 20)
     For page in 1..pages:
        GET /coches-segunda-mano/{s(M)}.htm  (page==1)  |  ...?page={page}
        parse __NEXT_DATA__ -> classifieds.classifiedList[<=20]
        emit each card (vehicle + dealer + platform_listing edge), dedup on id
4. Dedup on classifiedList[i].id across the whole run (a car can appear under one
   make only; cross-make dups ≈ 0, intra-run live drift < 1% — dedup absorbs it).
5. Reconcile: Σ distinct ids ≈ 92,326 (moves with live market).
```

Make-slug derivation (VERIFIED across all 93 makes live 2026-06-12): ASCII-fold
(NFKD strip accents) → lowercase → drop `&` and `.` → spaces to `-` → collapse
repeated `-`. This resolves **92/93 makes** directly to `total == count`; the one
edge is `LYNK & CO` → `lynk-co` (the `&` drops and the double space collapses) —
covered by the "collapse repeated `-`" + "drop `&`" steps. Examples:
`ALFA ROMEO`→`alfa-romeo`, `ASTON MARTIN`→`aston-martin`, `MINI`→`mini`,
`LAND ROVER`→`land-rover`, `LYNK & CO`→`lynk-co`. (Note: naive `DS`→`ds.htm`
worked; `ds-automobiles.htm` 404s — use the make `text` exactly as published, not
an expanded name.) Belt-and-braces: after slugging, fetch page 1 and assert
`classifieds.total == seoData count` before draining the partition; on mismatch,
fall back to scraping the canonical make anchor from the page-1 SRP
(`/coches-segunda-mano/{slug}.htm`, filtered to entries whose page-1 total equals
the make count — this excludes the province `coches-ocasion-en-{prov}` and
SEO `coches-baratos`/`coches-familiares-*` anchors that share the path prefix).

Pace through the **existing per-host governor** (same token bucket the PDP drain
uses); ~0.6–0.9 s/req held a single IP fine. Watch for the wall: a run of 403s
(2,588-byte Imperva block) = escalation → reserve vectors #5/#6 (camoufox homepage
warm-up to mint `incap_ses_*`, export cookie to curl_cffi).

---

## Parallelization (the second lever)

The 92k is now ~4,620 GETs partitioned into **93 independent make streams**. These
are embarrassingly parallel: run K make-workers concurrently (each its own
curl_cffi session/cookie jar), all funneled through the **one per-host governor**
so the host bucket still paces the aggregate. The current connector's
single-threaded per-PDP loop becomes K parallel make-drains under one rate budget —
wall-clock drops by ~min(K, governor_ceiling) on top of the 20× per-request win.

---

## The JSON API (`api-coches.pro.pvt.coches.com`) — mapped, NOT the bulk path

Live network capture of the PDP showed the SPA's real backend:
`https://api-coches.pro.pvt.coches.com/v1/...`, gated by header **`X-App: coches.com`**
(found in `_app-*.js`; without it → `412 {"reason":"invalid.app"}`).

- Working unauthenticated-on-load calls observed: `/v1/classified/dealer/{uuid}?limit=6`,
  `/v1/used-car/{uuid}/similar?limit=6`, `/v1/version/{token}/equipments`.
- **But there is NO open bulk VO search on it.** With `X-App` set, the listing/detail
  routes (`/v1/classified`, `/v1/used-car/{id}`, `/v1/classified/search`,
  `/v1/used-car/search`, `/v1/used-car/list`) all return **`401 missing.token`** —
  they require a **Bearer token**.
- The token is an **anonymous JWT** minted by `PUT /v1/user/anonymous`, which
  **requires `fingerprint` + `type` body params** (`400 Missing parameter -
  fingerprint,type`) — a device-fingerprint gate, refreshed via `/v1/refresh-token`.
- The PDP Next.js bundle only knows the **VN (new-car) search** route
  (`/v1/classified/vn/search?page=`); the **VO (used-car) search is NOT a public
  JSON route** — the VO SRP is server-rendered (`getServerSideProps`), so its data
  comes back **inside `__NEXT_DATA__`**, and the `_next/data/{buildId}/...json`
  twin **404s** (no static-props JSON for an SSR page).

**Conclusion:** the JSON API exists and is reachable, but its bulk VO surface is
token-walled behind a fingerprint mint — strictly more friction than the SSR
`__NEXT_DATA__`, which is already complete and **20 cars/req for free**. The
`X-App`/token map is documented here as the escalation reserve if the SSR surface
is ever removed.

---

## Five uncapped-surface vectors — outcome log (tried IN ORDER, LIVE)

### Vector 1 — SITEMAP — already the connector's enumerator (kept).
`sitemap.xml → vo.xml → Todo-VO-{0..3}.xml` = 92,259 PDP URLs. It enumerates the set
but is **1 car per PDP GET** — that is the slowness this recipe replaces. Still the
ground-truth count cross-check.

### Vector 2 — MOBILE APP API — **NOT REQUIRED.**
The web `api-coches.pro.pvt.coches.com` is the shared backend; no separate app host /
`/v4` / `/v5` / `searchAfter`/`scrollId` variant was needed. The web VO surface
(`__NEXT_DATA__` SRP) already serves the full set in 20-car pages. The pvt API's VO
bulk route is token-walled (above), so even the app path would hit the same JWT gate.

### Vector 3 — ALTERNATE/CURSOR endpoint / SRP-as-JSON — **WON (the SRP `__NEXT_DATA__`).**
The SRP `__NEXT_DATA__` is the bulk surface: 20 cars/page, clean `?page=N`,
`classifieds.total`. No cursor/`scrollId` needed; `?page=N` walks each make
partition end-to-end (ferrari drained 22/22 exactly). The `_next/data` JSON twin
404s (SSR page), so HTML-`__NEXT_DATA__` is the carrier — same parse the connector
already does, just at SRP granularity.

### Vector 4 — Browser-walled in-browser XHR — **mapped, not the path.**
Captured live via Playwright: header `X-App: coches.com` + anonymous-JWT (fingerprint
gate). VO bulk is `401 missing.token`; not worth the fingerprint reversal when SSR is
open and complete. Held as escalation reserve.

### Vector 5 — Facet partition — **REQUIRED here, and it is CLEAN.**
Unlike coches.net (gateway had no cap → no partition needed), coches.com enforces a
**10,000-result deep-pagination cap**. The platform-published **make facet** is a
MECE partition whose counts sum to the exact total (92,326) with **no slice ≥ 10k**,
so a per-make walk reaches 100% at 20 cars/req. This is the documented last-resort
vector — used here because the data layer genuinely caps the result set, not the UI.

---

## Conclusion

Same 92k, **~20× faster**: drain the VO SRP `__NEXT_DATA__`
(`classifieds.classifiedList`, 20 full cars/req) **per make**
(`/coches-segunda-mano/{make}.htm?page=N`), using the page-1 `seoData.all-makes`
counts (Σ = 92,326, every make < 10k) to size each partition under the
10,000-result deep-page cap. Dedup on `id`. ~4,620 requests replace ~92,259 PDP
GETs; the 93 make streams are independently parallelizable under the one per-host
governor. The pvt JSON API (`X-App: coches.com` + anonymous JWT) is mapped as the
escalation reserve; its VO bulk route is token-walled and therefore slower to use
than the open SSR surface.
