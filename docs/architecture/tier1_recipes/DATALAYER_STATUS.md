# CARDEEP Data-Layer Status — Tier-1 Giants

> **One line:** Seven ES giants have a **proven, €0 data-layer surface** that
> enumerates 100% of live inventory. Five (coches.net, wallapop, autocasion,
> spoticar, coches.com) have an uncapped surface; two (milanuncios, motor.es) have
> **no single uncapped surface** and close via a count-provable facet partition. All
> figures below are `[VERIFIED]` live on **2026-06-12** (`curl_cffi 0.15.0`,
> `impersonate="chrome131"`, no proxy, no browser, no auth).
>
> This file is the synthesis index. Full reproducible recipes live in the
> per-giant dossiers: [`coches_net_datalayer.md`](./coches_net_datalayer.md),
> [`wallapop_datalayer.md`](./wallapop_datalayer.md),
> [`autocasion_datalayer.md`](./autocasion_datalayer.md),
> [`spoticar_datalayer.md`](./spoticar_datalayer.md),
> [`coches_com_datalayer.md`](./coches_com_datalayer.md),
> [`milanuncios_datalayer.md`](./milanuncios_datalayer.md),
> [`motor_es_datalayer.md`](./motor_es_datalayer.md).

---

## Status board

| Giant | Verdict | Uncapped surface | Enumerates | Cap defeated |
|---|---|---|---|---|
| **coches.net** | ✅ **UNCAPPED** | `POST web.gw.coches.net/search`, linear `pagination.page` walk | **272,654** (`meta.totalResults`) | ~155k web-UI relevance cap is **frontend-only**; gateway has no cap |
| **wallapop** | ✅ **UNCAPPED** | `GET api.wallapop.com/api/v3/search/section`, `category_id=100` + `order_by=newest` cursor | **651,340** ES cars (server `remaining_documents`) | relevance/distance caps live in `order_by`; `newest` is flat |
| **autocasion** | ✅ **UNCAPPED** (via partition) | URL-path facet partition over SSR (`/coches-segunda-mano/{make}-ocasion`) | **≈123,512** (Σ make-slice `<title>` = 123,530) | ES `max_result_window=10000` bypassed — no slice exceeds 10k |
| **spoticar** | ✅ **UNCAPPED** (flat walk) | `GET spoticar.es/api/vehicleoffers/paginate/search?page=N` via `curl_cffi chrome131` | **6,334** ES public stock (`count.value`) | no relevance/depth cap — true flat ES-index enumeration |
| **coches.com** | ✅ **UNCAPPED** (fast, via make partition) | SRP `__NEXT_DATA__` `classifieds.classifiedList` (20 cars/req), per-make | **92,326** (`classifieds.total`) | 10k deep-page cap defeated by MECE make partition (max make 8,345) |
| **milanuncios** | ⛔ **CAPPED** → partition is the method | `GET searchapi.gw.milanuncios.com/v4/classifieds`, `province × price-band` partition | declared ~666,901 / live ~250k–290k | 10k ES window per view; no single cursor lifts it — partition closes it |
| **motor.es** | ⛔ **CAPPED** → partition is the method | `make → model` path-facet partition over SSR `?pagina=N` | **50,932** (`get-data-ajax` `data.total`) | 50-page (~1,150-row) cap per facet; no cursor/app/sitemap — partition closes it |

The first five (coches.net, wallapop, autocasion, spoticar, coches.com):
`uncapped_surface_found = true`. milanuncios + motor.es have **no single uncapped
surface** — their closure is a count-provable facet partition. None of the seven
requires a proxy, browser, CAPTCHA solve, or authentication for the harvest.

---

## coches.net — UNCAPPED, single linear walk

**Surface:** `POST https://web.gw.coches.net/search` (the same Adevinta/Schibsted
gateway the SRP uses).

- Headers: `Content-Type: application/json`, `Origin: https://www.coches.net`,
  `Referer: https://www.coches.net/segunda-mano/`, `X-Schibsted-Tenant: coches`.
- Body: `categoryId: 2500` (cars), `pagination` is a **nested object**
  `{ page, size }`. `size` is **hard-capped at 100** (150/200/500 silently → 100).
- **Enumeration:** walk `pagination.page` **1 → 2727** at `size=100`, dedup on `id`.
  `meta.totalResults = 272,654`, `meta.totalPages = 2727` → **2,727 requests = 100%**.
- **Cap is frontend-only (proven LIVE):** directly requested page blocks *past* the
  ~155k web boundary (pages 1551–1555 → 500 rows / 497 distinct real listings) and at
  the tail (page 2727 → 52 items; page 2728/3000 → 0, clean end-of-set). Sample pulled
  from past the web cap: `RENAULT Safrane 2.2i RN, 1996, 900 EUR, Huelva, id 70788916`.
- **Integrity:** adjacent-page overlap ≈ 0; across 13 pages spanning 1→2727, 3 dups in
  1255 (0.24%) = live-insertion drift, absorbed by `id` dedup. Sort params are silently
  ignored; default order is deterministic → sequential walk is consistent.
- **Residual:** none for enumeration. The ~0.24% live drift is dedup'd. Sitemap is a
  dead end (rolling ~8k freshness window, not a full index) but **not needed** — the
  gateway alone reaches 100%.

Full recipe + field map: [`coches_net_datalayer.md`](./coches_net_datalayer.md).

---

## wallapop — UNCAPPED, sort-knob cursor

**Surface:** `GET https://api.wallapop.com/api/v3/search/section` (shared web+app
gateway, anonymous).

- Params: `category_id=100` (cars) + **`order_by=newest`** +
  `section_type=organic_search_results`. **Omit `keywords`** (that scopes to a query).
- Headers: `referer`/`origin` = `https://es.wallapop.com`, `deviceos: 0`,
  `x-appversion: 822640`, random `x-deviceid` UUID. No auth bearer, no cookie warm-up.
- **The cap was never the endpoint — it is `order_by`:**

  | `order_by` | server `remaining_documents` | verdict |
  |---|--:|---|
  | `most_relevance` | 53,467 | ❌ relevance wall |
  | `closest` | 59,324 | ❌ distance-bounded |
  | **`newest`** | **651,329** | ✅ full catalog |
  | `price_low_to_high` / `price_high_to_low` | 651,340 | ✅ full catalog |

- **Enumeration:** paginate the opaque `meta.next_page` JWT cursor (40 items/page,
  fixed — every size override is ignored) until `pointers.ORGANIC.remaining_documents`
  → 0. ~16,300 pages for the full catalog.
- **Smoking gun:** the `next_page` JWT (HS256, read-only, no secret) carries
  `remaining_documents`, which **decrements by exactly the page size each step** —
  the API itself publishes the full-catalog guarantee.
- **Coverage proof:** walked `newest` to offset 64,000 → 63,023 unique ids, **0
  duplicates**, `remaining` decrementing linearly and exactly (651,340 → 587,380 =
  exactly 64,000 consumed), `has_next` still true — >10k past both caps.
- **Denominator is geo-independent:** Madrid/Barcelona/Sevilla/A Coruña/Canarias all
  report `remaining ≈ 651,329` (±live jitter); lat/long only affects ordering.
- **Residual:** (1) the **declared ~750k** marketing figure vs **live 651,340** server
  count — the marketing number includes non-current/other-locale listings; 651,340 is
  the honest live ES-cars denominator. (2) `type_attributes.engine` arrives latin-1
  mojibake (`Di�sel`) → re-encode `s.encode('latin-1').decode('utf-8')`. (3) Single-IP
  held 1,600 pages clean; full ~16,300-page run **may** need free DC-IP rotation if 429
  appears `[ASSUMED]` — not observed in audit.

Full recipe + field map: [`wallapop_datalayer.md`](./wallapop_datalayer.md).

---

## autocasion — UNCAPPED via URL-path facet partition

**Surface:** URL-path facet partition over the server-rendered SRP
(`GET https://www.autocasion.com/coches-segunda-mano/{make}-ocasion`). Platform:
autocasion.com (Grupo Luike / Vocento), dealer-focused ES classifieds.

- **The cap is real and bashing it fails:** GraphQL `search` and the SSR pages share one
  Elasticsearch backend with `index.max_result_window = 10000`. Any request with
  `from + size > 10000` → `500 "Result window is too large… See the scroll api"`. Open
  schema introspection confirms **no `scroll`, `searchAfter`, `cursor`, `*Connection`,
  `edges`/`pageInfo`, `offset`, `feed`, or `export`** resolver exists — pagination is
  pure offset, same 10k wall. So the relevance surface **cannot** reach 100%.
- **The bypass (the win):** partition by URL-path facet so **no slice exceeds 10k**.
  - Enumerate keys: GraphQL `brands(type:CAR)` → 184 make slugs (114 with stock).
  - Size each slice from the SSR facet `<title>` counter (no GraphQL):
    `<title>N.NNN {Make} de segunda mano…`.
  - Only **MERCEDES-BENZ (10,944)** exceeds 10k → split by province
    (`/{make}-ocasion/{province}`, all 50 slices < 10k).
  - Drain each slice `?page=1..⌈N/26⌉` (~26 PDP `-ref{ID}` cards/page) until a page
    returns 0 refs / "no hemos encontrado". Dedup ref-ids across pages and slices.
- **No relevance cap inside a slice** (proven): VW 8,589-slice flows cleanly through
  page 332, ends ~page 384. The 10k wall is **never hit** because each slice < 10k.
- **Coverage math:** Σ per-make `<title>` totals (114 makes) = **123,530** ≈ SRP
  declared **123,512** (~0.01% facet-overlap noise). GraphQL
  `search.paginatedAds.total` = 115,179 (search-index surface, ~7% lower — both real).
- **Hydration (already proven in `autocasion.md`):** car via GraphQL `ad(adId:{ID})`
  (OPEN, no auth); dealer via PDP JSON-LD `offers.offeredBy = AutoDealer`.
- **Residual / honest caveats:**
  - **Two live denominators, ~7% drift:** SRP `<title>` = 123,512 vs GraphQL `total` =
    115,179. Both real; re-derive at harvest (counter drifts daily).
  - **Future make >10k that one province can't split** (none today): add a third axis
    (make×province×fuel or make×year) — the sitemap `coches-segunda-mano.xml` (30,386
    facet slugs) already enumerates all three axes, so the partition extends cleanly.
  - **GraphQL `search.ads[]` is `[null,…]`** (list resolver gated) AND 10k-capped → use
    it only for the live counter, never for enumeration; per-ad `ad(adId)` is uncapped.
  - **robots.txt:** use path-segment facets (`/{make}-ocasion/{province}`), NOT
    query-param filters (`?marca=&provincia=`, which are disallowed). No 429/403 across
    the full probe from one residential IP.

Full recipe + field map: [`autocasion_datalayer.md`](./autocasion_datalayer.md).

---

## spoticar — UNCAPPED, flat ES-index walk (curl_cffi chrome131 is the key)

**Surface:** `GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page=N` —
the Drupal SPA's internal Elasticsearch-backed JSON API. Platform: **spoticar.es**
(Stellantis ES). **AkamaiGHost 403s plain curl; `curl_cffi impersonate="chrome131"`
passes the wall** (Chrome TLS/JA3 fingerprint) on homepage, listing, sitemap AND the API.

- **The enabling tool IS the win:** no single trick on the endpoint — the endpoint is
  open and flat once the chrome131 fingerprint clears Akamai. No proxy, no browser, no
  auth, no cookie warm-up, €0.
- Headers (minimal, → 200 `application/json`): `Accept: */*`,
  `X-Requested-With: XMLHttpRequest`, `Accept-Language: es-ES,es;q=0.9`,
  `Referer: https://www.spoticar.es/comprar-coches-de-ocasion`.
- **Enumeration:** fixed **12 hits/page** (not overridable); walk `page=1 → 528`, dedup
  on `field_vo_carnum`. `count.value` (6,334) bounds the run; page 528 = 11 trailing
  hits, 529+ = 0.
- **No relevance/depth cap (proven LIVE):** plain `?page=N` walk → **6,176 unique /
  6,334 = 97.5% in one uncoordinated pass**, linear growth (page 100→1,187 · 300→3,510 ·
  500→5,845), natural end at page 531. The ~2.5% gap is live row-drift over a ~10-min
  walk, NOT a cap; dedup + gap re-sweep → ~100%. The coches.net relevance pathology is
  ABSENT.
- **Denominator — five surfaces agree on 6,334:** `paginate count.value` = `list/search
  countNumber` = Σ brand-facet (40 brands) = Σ points-of-sale facet (135 dealers) =
  `/api/count-published-vo` (6,336, ±2 jitter). The declared ~50,000 is global pan-locale
  OEM marketing, not ES served stock.
- **Dealer attribution is best-in-class & self-contained:** every car carries its named
  Stellantis point-of-sale + geo id + lat/lng (`field_pdv_*`); 135 dealers enumerable
  from the `pointsofsale` facet — no separate dealer fetch.
- **Residual:** (1) `lastPage=576` is a metadata lie — real data boundary is page 528;
  pages 529–576 → 0 hits, >576 → repeating phantom blocks. (2) **Do NOT pass
  `sort=`/`orderby=`** → AkamaiGHost `503 Zero size object` on deep pages (sort not a
  cache key); plain `?page=N` only. (3) latin-1 mojibake on brand/dealer/city text
  (`CITRO�N`) → `s.encode("latin-1").decode("utf-8")`.

Full recipe + field map: [`spoticar_datalayer.md`](./spoticar_datalayer.md).

---

## coches.com — UNCAPPED FAST surface (SRP `__NEXT_DATA__`), MECE make partition

**Surface:** the VO SRP `https://www.coches.com/coches-segunda-mano/{slug}.htm?page=N`
is a Next.js page whose `__NEXT_DATA__` carries
`props.pageProps.classifieds.classifiedList` = **20 fully-populated cars** (dealer +
imageList inline) plus `classifieds.total`. Platform: coches.com (Carossa /
Imperva-Incapsula). Same transport as the existing PDP connector (curl_cffi chrome131,
`r.content.decode("utf-8")`) but **20 cars/req instead of 1 (~20× speedup)**.

- **The fast win:** the SRP (not just the PDP) serves the complete `classified` shape —
  the listing page is the bulk surface. `seoData[key="all-makes"]` on page 1 publishes
  all 93 makes with exact counts.
- **One data-layer cap:** deep pagination capped at **page 500 (= 10,000th result)** —
  classic ES `max_result_window=10000`; `page=501` → **403** (2,588-byte Imperva block).
  Unfiltered SRP reaches only 10,000 / 92,326 (10.8%).
- **The fix (MECE partition):** drain **per make**. `seoData.all-makes` counts **sum to
  exactly 92,326 = `classifieds.total`** (every car has exactly one make → clean,
  complete partition), and **no make ≥ 10,000** (max PEUGEOT 8,345), so every make pages
  fully inside the 10k cap. Per-make URL `/coches-segunda-mano/{make-slug}.htm?page=N`.
- **Cost:** `Σ ceil(count/20)` ≈ **~4,620 requests** for the full 92,326, vs ~92,259 PDP
  GETs. The 93 make streams are embarrassingly parallel under the one per-host governor.
- **Proven LIVE:** SRP page 500 → 200 / page 501 → 403 (bisected); `peugeot.htm?page=410`
  (~8,200th) → 200 (deep paging works inside a make — cap is per-result-set);
  `ferrari.htm` full drain → 22/22 distinct ids == declared total.
- **Residual:** (1) make-slug derivation is ASCII-fold + lowercase + drop `&`/`.` +
  spaces→`-` + collapse repeated `-` (resolves 92/93; edge `LYNK & CO`→`lynk-co`,
  `DS`→`ds.htm` not `ds-automobiles.htm`) — belt-and-braces: assert
  `classifieds.total == seoData count` before draining. (2) **Province is NOT a valid
  partition** (Madrid 53,512, Barcelona 47,791 > 10k) — make is. (3) the pvt JSON API
  (`api-coches.pro.pvt.coches.com`, `X-App: coches.com`) exists but its VO bulk route is
  token-walled behind a fingerprint-minted anonymous JWT → strictly more friction than
  the open SSR `__NEXT_DATA__`; held as escalation reserve.

Full recipe + field map: [`coches_com_datalayer.md`](./coches_com_datalayer.md).

---

## milanuncios — CAPPED; province × price-band facet partition is the closure

**Surface:** `GET https://searchapi.gw.milanuncios.com/v4/classifieds` — the SPA's real
JSON gateway (CloudFront), discovered via camoufox XHR capture; the prior `milanuncios.md`
("server-rendered, must DOM-scrape with camoufox") was **WRONG**. The SPA is client-rendered
and calls this clean REST gateway, **open to plain `curl_cffi chrome131` — no reese84, no
GeeTest, no auth, no proxy**. Platform: milanuncios (Adevinta Spain), declared ~666,901.

- Params: `category=13` (Coches), `transaction=supply`, `limit=100` (101+ → 30-ad
  fallback), `sort=newest`. Filter knobs: **`province`** (singular; INE 1–52),
  **`brand`** (make slug), `priceFrom`/`priceTo`, `yearFrom`/`yearTo`.
  ⚠ Plural/alias filters (`provinces`, `make`, `makes`…) are **silently ignored** (return
  `gte:10000` + off-target ads) — validate a filter "took" via `relation==eq` or matching
  titles.
- **No single uncapped cursor (unlike wallapop):** every view is a hard
  `from+size ≤ 10,000` ES window. `offset` walks until ~9,959 then collapses to a
  degenerate page-1 reset; `limit`, all `sort` values, and the body `nextToken` keyset
  (tried as query/header/POST/`search-urls`) **none lift the 10k wall**. This is the
  coches.net pathology, not the wallapop one.
- **The smoking-gun oracle:** `pagination.totalHits` is an ES `track_total_hits` object —
  `{relation:"gte", value:10000}` when a view >10k, but flips to
  **`{relation:"eq", value:<EXACT>}`** the moment a filter narrows it ≤10k. Partition
  until every cell reports `eq`; the sum of `value`s is the provable catalog size, and
  each ≤10k cell is fully offset-paginable.
- **Closure (the method):** partition by **`province` (1–52)** — 46/52 return exact `eq`
  (Σ 142,510); the 6 metro provinces (Madrid/Barcelona/Alicante/Málaga/Sevilla/Valencia)
  still `gte:10000` → sub-partition by **`priceFrom`/`priceTo`** (Madrid Σ=50,356;
  Barcelona Σ=23,083; Alicante Σ=12,797, all-eq). `brand` is an independent axis;
  `brand × province` covers any residual. Province × price-band is a gap-free,
  count-provable partition.
- **Self-contained fields (no PDP):** `ads[]` carries specs (`kilometers, year, fuel,
  transmission, hp, doors, color, environmentalLabel`), `authorId`/`authorName` (dealer
  attribution first-class), price (`cash`/`financed`), and top-level `photos[]` joined by
  `adId`. latin-1 mojibake → `s.encode("latin-1").decode("utf-8")`.
- **Residual:** `uncapped_surface_found = false` — closure is the partition.
  **Declared ~666,901** (census/marketing, all-time) vs **live ~250k–290k** currently
  listed (46 eq-provinces 142,510 + metro price-banded sums; mirrors the wallapop
  marketing-N > live-N finding). Sitemap is S3-`AccessDenied` / robots behind GeeTest —
  not the path; the gateway under partition is.

Full recipe + field map: [`milanuncios_datalayer.md`](./milanuncios_datalayer.md).

---

## motor.es — CAPPED; make → model path-facet partition is the closure

**Surface:** there is **no single uncapped surface**. The unfiltered listing and every
facet share a **hard 50-page UI cap (≤1,150 rows)**; there is no mobile/app API, no PDP
sitemap, and no cursor on the AJAX seed. Closure = a **two-level path-facet partition
(make → model)** where every leaf drains its own ≤50-page window and the leaves are MECE.
Platform: motor.es (Motor Internet S.L.), Cloudflare-permissive PHP/SSR site (NOT
Next.js). Declared ~51,000; live `get-data-ajax` `data.total` = **50,932**.

- ⚠ **Correction to `motor_es.md`:** its claimed "unfiltered `?pagina=N` drains all 2,316
  pages" is **FALSE** — `?pagina=50` → 200, `?pagina=51` → **404** (LIVE). A flat drain
  reaches only ~1,150 cars (2.3% of census). The partition is mandatory.
- **Path facets only — query params are ignored:** `?precio_hasta=`, `?anio_desde=` etc.
  return the unfiltered set. Only path facets filter:
  `/segunda-mano/{make}/`, `/{make}/{model}/`, `/{make}/{model}/{province}/` — each has
  its own paginator, its own total, and the **same 50-page cap**.
- **Closure (the method):** read the denominator from `get-data-ajax` `data.total`;
  harvest the make taxonomy from the listing-sidebar HTML (117 one-seg make+province
  slugs). For each make: if total ≤ 1,150 drain the make whole (≤50 pages, 23 cards/page,
  dedup on `data-id`); else split by **model** (`/{make}/{model}/`); if a model leaf is
  still > 1,150, add **province** as a rare 3rd level. make→model is MECE (Cupra sum check:
  models 341 ≈ make 345), so the leaf union = the full 50,932.
- **Vectors that failed (proven LIVE):** sitemap `sitemap_vo.xml` = 2,620 facet locs, **0
  PDPs**; no app host (`api/app/m.motor.es` → DNS-dead); `get-data-ajax` is a frozen 10-row
  seed (every `pagina`/`offset`/`cursor`/`searchAfter` param + POST + path variant ignored;
  `set-navegacion-session` is back-button memory, not a cursor); no GraphQL; the SSR
  `?pagina=N` HTML *is* the data layer (Playwright: page-2 nav fires no listing XHR).
- **Enrichment:** PDP `GET /segunda-mano/anuncio/{id}/` JSON-LD `@type:Car`
  (`offers.price`, `offers.seller.name` = selling dealer). ⚠ `vehicleIdentificationNumber`
  is a static DUMMY — key on `data-id` + PDP url.
- **Residual:** `uncapped_surface_found = false` — closure is the partition; €0, curl_cffi
  chrome131, one warm GET mints `PHPSESSID`, Cloudflare permissive.

Full recipe + field map: [`motor_es_datalayer.md`](./motor_es_datalayer.md).

---

## Bottom line

| Giant | Uncapped? | Honest residual |
|---|---|---|
| coches.net | ✅ 100% via single linear gateway walk | none (0.24% live drift dedup'd) |
| wallapop | ✅ 100% via `newest` cursor | declared-vs-live denominator (750k mktg vs 651,340 live); mojibake fix; possible IP rotation at full scale |
| autocasion | ✅ 100% via facet partition (relevance surface stays capped at 10k) | two denominators ~7% apart; future-make 3rd-axis split held in reserve |
| spoticar | ✅ 100% via flat ES-index `?page=N` walk (curl_cffi chrome131 clears Akamai) | 50k marketing vs 6,334 live ES stock; `lastPage=576` metadata lie (real boundary 528); never send `sort=` (origin 503); mojibake fix |
| coches.com | ✅ 100% via SRP `__NEXT_DATA__`, per-make MECE partition (~20× faster, 20 cars/req) | 10k deep-page cap per result-set forces make partition; slug edge cases (`LYNK & CO`, `DS`); pvt JSON API token-walled (reserve) |
| milanuncios | ⛔ no single uncapped surface — closure = `province × price-band` partition (each cell `eq`-counted ≤10k) | declared ~666,901 vs live ~250k–290k; ignored-alias filter trap; mojibake fix; sitemap S3-gated |
| motor.es | ⛔ no single uncapped surface — closure = `make → model` path-facet partition (MECE, ≤50 pages/leaf) | 50-page (~1,150-row) cap per facet; `motor_es.md` "2,316-page drain" refuted live; dummy VIN; sitemap has 0 PDPs |

*Source of truth: the seven per-giant `*_datalayer.md` dossiers. All claims
`[VERIFIED]` live 2026-06-12. Generated 2026-06-12; spoticar/coches.com/milanuncios/
motor.es appended 2026-06-12.*
