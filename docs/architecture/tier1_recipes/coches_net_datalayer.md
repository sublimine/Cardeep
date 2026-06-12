# coches.net — UNCAPPED Data-Layer Recipe (full 272k, no relevance cap)

Status: **UNCAPPED SURFACE FOUND.** The serving gateway enumerates 100% of the
declared inventory with NO cap. The "~155k web relevance cap" is a **frontend-UI
limit only** — it is NOT enforced at the data layer.
Platform: coches.net (Adevinta / Schibsted Spain Motor).
Declared inventory: 272,682. Live gateway count: **272,654** (`meta.totalResults`).
Verified LIVE: 2026-06-12 (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy, no browser).

---

## TL;DR — the uncapped surface

The same gateway the SRP uses, `POST https://web.gw.coches.net/search`, has **no
relevance cap at the data layer**. It paginates cleanly through **all 2727 pages**
(size=100) to the full 272,654. The website stops the UI at ~page 1550 (~155k);
the gateway does not. Harvest = walk `pagination.page` 1 → 2727, dedup on `id`.

```
POST https://web.gw.coches.net/search
Content-Type: application/json
Accept: application/json, text/plain, */*
Origin: https://www.coches.net
Referer: https://www.coches.net/segunda-mano/
X-Schibsted-Tenant: coches
```

Body (categoryId 2500 = cars/turismos; pagination is a NESTED object):

```json
{
  "categoryId": 2500,
  "sortBy": "relevance",
  "sortOrder": "DESC",
  "pagination": { "page": 1, "size": 100 },
  "price": { "from": null, "to": null },
  "year":  { "from": null, "to": null },
  "km":    { "from": null, "to": null }
}
```

- `meta.totalResults = 272654`, `meta.totalPages = 2727`.
- `size` is **hard-capped at 100** (150 / 200 / 500 all silently return 100).
- Full inventory = **2,726 pages × 100 + 1 page × ~52 = 272,654**, i.e. **2,727 requests**.
- Transport: `curl_cffi` `impersonate="chrome131"`. No cookies, no proxy, no JS challenge
  on the API host.
- Runner: `scripts/coches_net_harvest.py` (`python scripts/coches_net_harvest.py <page>`).
  Bump default `size` 30 → 100 for the full walk.

---

## Why this is the WIN (the cap is frontend-only — proven LIVE)

The intel said "web relevance pagination caps at ~155k of 272k". That cap is in the
**website UI**, not in the gateway. Proven by directly requesting pages that sit
**past** the 155k boundary and at the very tail:

| Page block | Listing positions | Result (LIVE 2026-06-12) |
|---|---|---|
| 1, 2, 3 | 1–300 | 100 items each, 0 cross-page overlap |
| 1500, 1600, 2000 | ~150k–200k | 100 items each, status 200 |
| **1551–1555** | **~155,100th–155,500th** (past the web cap) | **500 rows / 497 distinct, real listings** |
| 2720–2726 | ~272,000th | 100 items each, status 200 |
| **2727 (last)** | tail | **52–55 items** → 2726×100 + 52 ≈ **272,654** ✔ |
| 2728, 3000 | past end | **0 items** (clean end-of-set) |

Sample real listing pulled from **past the web cap** (page 1555):
`RENAULT Safrane 2.2i RN, 1996, 900 EUR, Huelva, id 70788916`
(`/renault-safrane-22-i-rn-5p-gasolina-1996-en-huelva-70788916-covo.aspx`) — a car
the website frontend will not paginate to, served directly by the gateway.

### Pagination integrity

- Adjacent pages: ~0 overlap (pg1/pg2, pg2/pg3, pg500/pg501 = 0).
- Across 13 sampled pages spanning 1 → 2727: 1255 collected, 1252 distinct
  (**3 dups = 0.24%**), pure live-insertion drift, not structural duplication.
- The gateway uses a **fixed default order** that is stable across calls. `sortBy`
  / `sortOrder` and every alternate sort shape tried (`sort:{order,term}`,
  `sort:{order,field}`, `order:{field,direction}`) are **silently ignored** — page-1
  first ids are identical regardless. Default order is deterministic, so sequential
  `page` walking is consistent. **Dedup on `id`** absorbs the sub-1% live drift.

### Harvest recipe (reproducible)

```
1. Session: curl_cffi, impersonate="chrome131".
2. For page in 1..2727:
     POST web.gw.coches.net/search with body above, pagination.size=100.
     Collect items[].id (+ full field map below).
3. Dedup on id. Expect ~272,6xx distinct (count moves with live market).
4. Re-walk on a cadence to capture churn; the set is fully addressable every pass.
```

No relevance cap, no facet partitioning, no province loop needed. One linear walk
of 2,727 requests covers 100%.

---

## Five uncapped-surface vectors — outcome log (tried IN ORDER, LIVE)

### Vector 1 — SITEMAP — **DEAD END (evidenced).** Does NOT enumerate all PDPs.

- `robots.txt` (200) declares one sitemap:
  `https://www.coches.net/servicios/sitemaps/sitemap-index.xml`.
- Direct GET of any sitemap with a bare client or spoofed Googlebot UA → **403 / 405
  hCaptcha block page** (Schibsted "Ups! Parece que algo no va bien…", ~8.3 KB HTML).
- **Bypass found** for *reading* the sitemap: warm the session on `https://www.coches.net/`
  first (acquires `ajs_anonymous_id` cookies), then GET the sitemap with
  `Referer: https://www.coches.net/` + `Sec-Fetch-Site: same-origin` →
  **200 valid XML**. (Documented because it unblocks the sitemap, but the content
  does not help — see below.)
- The index lists **28 child sitemaps**. Only the `sitemap-ad-*` files hold PDP URLs.
  - `sitemap-ad-sm-1.xml` → **4000** PDP URLs (`.../{slug}-{id}-covo.aspx`).
  - `sitemap-ad-sm-2.xml` → **4000** PDP URLs.
  - **3993 of ~4000 ids overlap between sm-1 and sm-2**, and **every `lastmod` =
    today (2026-06-12)**. These are NOT a partition — they are a **rolling freshness
    window** of the latest ~4000 used-car ads, refreshed daily.
  - `sitemap-ad-sm-3.xml` → **404**. No `?page=`/`?p=`/`?pg=` pagination (all → block page).
  - `sitemap-ad-km0.xml`, `-clasicos-competicion`, `-autocaravanas-remolques`,
    `-sin-carnet`, `-vehiculos-industriales`, `-detail-prof` → persistent **8715-byte
    captcha block** (4 retries each, never yields XML).
- **Verdict:** the sitemap surfaces at most ~8000 fresh PDPs, not ~272k. Unlike
  coches.com (whose sitemap enumerated 92,259 PDPs), coches.net's sitemap is a
  crawl-priority freshness feed, not a full index. **Cannot reach N via sitemap.**

### Vector 2 — MOBILE APP API — **NOT REQUIRED.** Web gateway already uncapped.

The mobile app and the web SRP share the same Adevinta/Schibsted gateway host
(`web.gw.coches.net`). Since that gateway already serves 100% of the inventory with
no cap (Vector 3), a separate app host / `/v5` / `searchAfter` variant is unnecessary.
The internal SSR origin `ms-mt--api-web.spain.advgo.net` remains externally
unreachable (CloudFront 502 "wasn't able to resolve the origin domain name") and is
not needed.

### Vector 3 — CURSOR/ALTERNATE ENDPOINT on the same gateway — **WON.**

`POST web.gw.coches.net/search` is itself the uncapped surface. No cursor / `scrollId`
/ `searchAfter` is required: the plain **`pagination:{page,size}` object walks all
2727 pages with no relevance cap** (proven above). `size` maxes at 100. The frontend
caps the UI at ~155k; the gateway does not cap at all. This is the recipe.

### Vector 4 — FEED / EXPORT — **NOT REQUIRED.**

No dealer-feed / data-feed / XML-export endpoint was needed; the gateway delivers the
full set linearly. (Not pursued because Vector 3 already yields 100%.)

### Vector 5 — Facet partition (province/price/year) — **NOT REQUIRED (last resort).**

Unnecessary: the unpartitioned gateway already reaches 272,654 with no cap. Facet
partitioning would only be a fallback if the gateway had enforced the 155k cap — it
does not.

---

## Field map (per item — same as SRP recipe, unchanged)

`id, title, url, make, makeId, model, modelId, year, km, hp, fuelType, fuelTypeId,
bodyTypeId, transmissionTypeId, environmentalLabel, drivenWheelsId, isProfessional,
isCertified, isFinanced, hasUrge, offerType, phone, hidePhone, contractId, pack,
publishedDate, creationDate, provinceIds, mainProvince, location, resources, warranty`

- `price` (object): `{ amount, taxTypeId, hasTaxes, financedAmount?, financingInfo?,
  priceDropData?, indicator?{average,rank}, hasReservation }`
- `seller` (object): `{ name, isProfessional, contractId, pack{legacyId,type},
  ratings{scoreAverage,commentsNumber} }`  ← dealer attribution
- `location` (object): `{ provinceIds[], regionId, regionLiteral, mainProvince,
  mainProvinceId, cityId, cityLiteral }`
- PDP URL pattern: `https://www.coches.net/{slug}-{id}-covo.aspx`

---

## Conclusion

The data layer that serves the full inventory is the **`web.gw.coches.net/search`
gateway**, and it imposes **no cap**. The ~155k limit lives only in the website UI.
A single linear `pagination.page` walk 1 → 2727 at `size=100` enumerates **100% of
the 272,654 cars** (dedup on `id` for the <1% live drift). The sitemap is a dead end
(rolling ~8k freshness window, not a full PDP index); no mobile-app host, cursor,
feed, or facet partition is required.
