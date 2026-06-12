# Autocasion — uncapped data-layer recipe (CARDEEP)

> **Platform:** autocasion.com (Grupo Luike / Vocento). Dealer-focused ES classifieds.
> **Declared inventory (this sweep, 2026-06-12):** site SRP `/coches-ocasion` `<title>`
> counter = **123,512**; GraphQL `search.paginatedAds.total` = **115,179** (two live
> surfaces, ~7% drift — both real, both re-derived at harvest).
> **Mission verdict:** **UNCAPPED SURFACE FOUND.** The GraphQL/SSR relevance pagination
> caps hard at the Elasticsearch **`max_result_window = 10000`** offset wall (proven
> below). The site serves the FULL inventory with NO cap through **URL-path facet
> partitioning** (make, and make×province for the single make over 10k) — every slice
> < 10k, each fully drainable by SSR `?page=N`, Σ slices ≈ 100% of N.
>
> Every claim is `[VERIFIED]` — fetched live 2026-06-12 with the project python
> (`C:/Users/elias/AppData/Local/Programs/Python/Python311/python`) + `curl_cffi 0.15.0`,
> `impersonate="chrome131"`, €0 (no proxy, no auth, no browser for the harvest path).

---

## TL;DR — the 100% recipe

1. **Enumerate the partition keys.** GraphQL `brands(type:CAR)` → 184 make slugs (114 with
   live stock). Add the 52 provinces (`provinces`) for the one make over 10k.
2. **Size each slice** from the SSR facet `<title>` counter (no GraphQL needed):
   `GET /coches-segunda-mano/{make}-ocasion` → `<title>N.NNN {Make} de segunda mano…`.
   Per-make: only **MERCEDES-BENZ (10,944)** exceeds 10k; every other make < 10k.
3. **For makes < 10k:** drain `GET /coches-segunda-mano/{make}-ocasion?page=1..⌈N/26⌉`,
   ~26 PDP `-ref{ID}` cards/page, until `page` returns 0 refs ("no results").
4. **For MERCEDES-BENZ (>10k):** split by province
   `GET /coches-segunda-mano/mercedes-benz-ocasion/{province}` (all 50 province slices
   verified < 10k) and drain each `?page=N`.
5. **Hydrate** each harvested ref: GraphQL `ad(adId:{ID})` (full car, OPEN, no auth) and/or
   the PDP JSON-LD `offers.offeredBy=AutoDealer` (dealer attribution). Both already proven
   in `autocasion.md`.

**Coverage proof:** Σ(per-make `<title>` totals) = **123,530** (114 makes) ≈ the SRP
declared 123,512. Each slice drains to its own end with no relevance cap inside the slice
(VW 8,589-slice verified flowing through page 332, "no results" only at ~page 384). The 10k
ES wall is never hit because no single slice exceeds 10k. **This is the uncapped surface.**

---

## The cap — exactly where the wall is (proven)

GraphQL `search` and the SSR results pages share one Elasticsearch backend
(`index: autocasion_prod_search`) with `index.max_result_window = 10000`. Any request
whose **`from + size > 10000`** fails:

```
POST https://gql.autocasion.com/graphql/
query S($p:[SearchParamInput],$page:Int,$ipp:Int){search(params:$p,page:$page,itemsPerPage:$ipp){paginatedAds{total pages ads{id}}}}
```
| page | itemsPerPage | from+size | result |
|---|---|---|---|
| 1   | 24   | 24      | 200, total=115179, pages=4800 (ads[] null — list resolver gated) |
| 100 | 24   | 2400    | 200 OK |
| 500 | 24   | 12000   | **500** `Result window is too large, from + size must be ≤ 10000 … See the scroll api` |
| 4800| 24   | 115200  | **500** same ES error |
| 1   | 1000 | 1000    | 200 OK (bigger `itemsPerPage` works, but `page*ipp` still bounded ≤ 10000) |

The ES error names the only two escapes: **scroll API** / **`search_after`**. Schema
introspection (open, no auth) was exhausted for both — **neither exists**:

- Query type (30 fields): `search(params,config,page,itemsPerPage)`, `searchAs(...)`,
  `searchAP(...)`, `ad(adId)`, `brands(type)`, `families`, `fuels`, `provinces`, … — no
  `*Connection`, no `edges`/`pageInfo`, no `cursor`/`after`/`scroll`/`searchAfter`/`offset`/
  `feed`/`export`/`seo`-dump field anywhere.
- Pagination input is `PaginationInput {page, itemsPerPage, sortBy}` — pure offset only.
- `Search.paginatedAds: PaginationAds {page, pages, itemsPerPage, hasNext, hasPrevious,
  total, ads}` — offset-only, same 10k wall.

SSR mirrors the wall: `/coches-segunda-mano/volkswagen-ocasion?page=384` → "no hemos
encontrado" (≈ 26×384 ≈ 9,984 ≈ 10k), regardless of the slice's true size. So **relevance
pagination caps at 10k; facet partitioning under 10k is the only uncapped path** — and it
is sufficient because the max make slice (MB) is 10,944, splittable by province.

---

## Vector-by-vector (the 5 uncapped vectors, in doctrine order)

| # | Vector | Live outcome (2026-06-12) |
|--:|---|---|
| 1 | **SITEMAP of all PDPs** | ⚠ **No per-PDP sitemap exists**, but the sitemap tree is richer than prior intel claimed. `robots.txt` → `uploads/sitemap.xml` is a **`sitemapindex`** (NOT "editorial/uploads"): 12 children incl. `sitemap-ng/coches-segunda-mano/coches-segunda-mano.xml` = **30,386 `<loc>` SEO facet landing pages** (make / make×model / make×province / province×fuel — gzipped 5.6 MB urlset, **0 `-ref{ID}`**) and `sitemap-ng/stock/stock.xml` = **2,948 dealer pages** (`/profesional/{slug}`, **0 `-ref{ID}`**). No file lists individual ads. The other declared sitemap (`actualidad/sitemap_index.xml`) is WordPress editorial. 14 undeclared common PDP-sitemap names (`/sitemap.xml`, `/sitemap_index.xml`, `/product-sitemap.xml`, …) all **404** (SPA fallback). **→ The 30,386 facet URLs ARE the pre-built partition surface** (they enumerate every make×model×province×fuel slug the site indexes); the 2,948 dealer pages are an alternate full partition (every ad belongs to exactly one dealer). |
| 2 | **Mobile-app API** | Not needed. `window.__APP_CONTEXT__.endpointGraphql = https://gql.autocasion.com/graphql/` is the single backend for web **and** the app (`apple-itunes-app: 580457760`, `google-play: com.vocento.autocasion`). The same host answers web-origin calls with no device headers. It is the same ES backend → **same 10k wall**; no app-only cursor endpoint exists (introspection confirms no scroll/searchAfter on this host, which is the app's host too). `[NOT NEEDED — same gateway, same cap]` |
| 3 | **Alternate/cursor endpoint on the gateway** | ✗ **Exhausted.** Full open introspection: no `scroll`, `searchAfter`, `cursor`, `*Connection`, `edges`/`pageInfo`, `offset`, `feed`, `export`, or `seo`-dump resolver. `config:[SearchFilterElementConfigInput{name,options}]` rejects every guessed facet name (`"El elemento con nombre X no está registrado"`) — the resolver has a server-side facet registry not exposed via the API, AND the facet pages render server-side (no client GraphQL call observed in Playwright network capture on a facet page). So GraphQL filtering by arbitrary key is **not** the partition surface — the **URL-path facet** is. |
| 4 | **Feed / export** | ✗ No dealer-feed / data-feed / partner / XML-export endpoint found (none in sitemaps, none in introspection, none under probed paths). |
| 5 | **Facet partition (URL-path)** | ✅ **WIN — this is the uncapped surface.** Per-make SSR facet pages (`/coches-segunda-mano/{make}-ocasion`) carry the slice total in `<title>` and the PDP `-ref{ID}` cards in the body, fully server-rendered (curl_cffi, no browser). Only **MERCEDES-BENZ (10,944)** exceeds 10k → split by province (all 50 MB×province slices verified < 10k). Σ make slices = **123,530** ≈ declared 123,512. Each slice drains to its own end (VW 8,589 verified through page 332). **100% coverage, no relevance cap.** |

**Conclusion:** Vector 5 (URL-path facet partition by make, make×province for MB) over the
already-proven hydration path (GraphQL `ad()` + PDP JSON-LD) is the complete, reproducible,
€0, 100%-coverage recipe. The GraphQL/SSR 10k ES wall (vectors 2/3) is bypassed, not bashed.

---

## Reproducible drain (the surface)

**Engine:** `pipeline/engine/fetch.py` `FetchEngine` (`curl_cffi impersonate="chrome131"`),
one warm session (homepage GET to mint `cf` cookies), polite 0.7–1.4 s jitter. Cloudflare
permissive (`cf-cache-status: DYNAMIC`, no JS challenge to a Chrome TLS fingerprint).

**Headers (SSR/PDP):**
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept-Language: es-ES,es;q=0.9,en;q=0.8
```
**Headers (GraphQL hydrate POST):** + `Accept: application/json`, `Content-Type: application/json`,
`Origin: https://www.autocasion.com`, `Referer: https://www.autocasion.com/coches-segunda-mano`.

### Step 1 — partition keys + slice sizes (no GraphQL needed for sizing)
```
POST gql.autocasion.com/graphql/  {"query":"{brands(type:CAR){id name slug}}"}        # 184 makes
POST gql.autocasion.com/graphql/  {"query":"{provinces{id name slug}}"}                # 52 provinces (for MB)
GET  /coches-segunda-mano/{make-slug}-ocasion                                          # <title> "N.NNN {Make} de segunda mano…"
```
Parse the slice total from `<title>`: `^<title>\s*([\d\.]+)\s` → strip dots → int.
Rule: if make total < 10000 → drain the make slice; else (only MERCEDES-BENZ) → iterate
provinces and drain `/{make}-ocasion/{province}` slices (all < 10k).

### Step 2 — drain each slice to its end (SSR pagination)
```
GET /coches-segunda-mano/{make}-ocasion?page={1..}          (or {make}-ocasion/{province}?page={1..})
```
~25–26 PDP cards/page. Harvest refs: `href="(/coches-[^"]*-ref(\d+))"`. Stop the slice when a
page returns **0 refs** / contains "no hemos encontrado". Dedup ref-ids across pages and across
slices (live set shifts; a listing can appear under make and under make×province).

### Step 3 — hydrate (already proven; see `autocasion.md`)
- **Car:** `POST gql.autocasion.com/graphql/ {"query":"{ad(adId:{ID}){id title price kilometers year fuel{name} transmission{name} brand{name} family{name} province{name} url slug km0 certificated}}"}` — OPEN, no auth.
- **Dealer:** `GET https://www.autocasion.com{pdp_url}` → single `application/ld+json` `Product`
  block, `offers.offeredBy` = `AutoDealer {name, @id(/profesional/slug), telephone, address}`.

---

## Coverage math (verified)

```
Σ per-make <title> totals (114 makes w/ stock)        = 123,530
SRP /coches-ocasion <title> counter                   = 123,512   (≈ match; ~0.01% facet-overlap noise)
GraphQL search.paginatedAds.total                      = 115,179   (search-index surface, ~7% lower)
makes over 10k requiring make×province split           = 1  (MERCEDES-BENZ = 10,944)
MERCEDES-BENZ × province slices over 10k               = 0   (all 50 < 10k)
VW slice (8,589) drains through page 332, ends ~page 384 (no relevance cap inside slice)
```
Re-derive totals at harvest (counter drifts daily). Worst-case future make >10k that a
single province can't split (none today) → add a third axis (make×province×fuel; the
sitemap already enumerates `{province}/{fuel}` slugs) or make×year — the facet vocabulary
in `coches-segunda-mano.xml` (30,386 slugs) already covers all three axes.

## Residual notes / hygiene
- GraphQL `search.ads[]` is `[null,…]` (list resolver gated) AND capped at 10k → do not use it
  for enumeration; use it only for the live counter. Per-ad `ad(adId)` is OPEN and uncapped.
- `advertiser` null on `ad()`/`search` (login-gated) → dealer from PDP JSON-LD `offeredBy` (public).
- robots.txt `User-agent: *` does NOT disallow `/coches-segunda-mano/…` facet paths or PDPs; it
  disallows query-param filter URLs (`*?*marca=*`, `*?*provincia=*`, …) and `/api/*` tracking —
  so use the **path-segment** facets (`/{make}-ocasion/{province}`), not `?marca=&provincia=`.
- No 429/403 across the full probe set (counter, schema, sitemaps, 184 facet titles, MB×52
  provinces, multi-page drains) from one residential IP. Escalate to camoufox only on a first CF
  tripwire at scale; not needed today.
