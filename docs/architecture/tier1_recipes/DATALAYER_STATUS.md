# CARDEEP Data-Layer Status — Tier-1 Giants

> **One line:** Three ES giants (coches.net, wallapop, autocasion) have a **proven,
> €0, no-cap data-layer surface** that enumerates 100% of declared inventory. All
> figures below are `[VERIFIED]` live on **2026-06-12** (`curl_cffi 0.15.0`,
> `impersonate="chrome131"`, no proxy, no browser, no auth).
>
> This file is the synthesis index. Full reproducible recipes live in the
> per-giant dossiers: [`coches_net_datalayer.md`](./coches_net_datalayer.md),
> [`wallapop_datalayer.md`](./wallapop_datalayer.md),
> [`autocasion_datalayer.md`](./autocasion_datalayer.md).

---

## Status board

| Giant | Verdict | Uncapped surface | Enumerates | Cap defeated |
|---|---|---|---|---|
| **coches.net** | ✅ **UNCAPPED** | `POST web.gw.coches.net/search`, linear `pagination.page` walk | **272,654** (`meta.totalResults`) | ~155k web-UI relevance cap is **frontend-only**; gateway has no cap |
| **wallapop** | ✅ **UNCAPPED** | `GET api.wallapop.com/api/v3/search/section`, `category_id=100` + `order_by=newest` cursor | **651,340** ES cars (server `remaining_documents`) | relevance/distance caps live in `order_by`; `newest` is flat |
| **autocasion** | ✅ **UNCAPPED** (via partition) | URL-path facet partition over SSR (`/coches-segunda-mano/{make}-ocasion`) | **≈123,512** (Σ make-slice `<title>` = 123,530) | ES `max_result_window=10000` bypassed — no slice exceeds 10k |

All three: `uncapped_surface_found = true`. None requires a proxy, browser,
CAPTCHA solve, or authentication.

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

## Bottom line

| Giant | Uncapped? | Honest residual |
|---|---|---|
| coches.net | ✅ 100% via single linear gateway walk | none (0.24% live drift dedup'd) |
| wallapop | ✅ 100% via `newest` cursor | declared-vs-live denominator (750k mktg vs 651,340 live); mojibake fix; possible IP rotation at full scale |
| autocasion | ✅ 100% via facet partition (relevance surface stays capped at 10k) | two denominators ~7% apart; future-make 3rd-axis split held in reserve |

*Source of truth: the three per-giant `*_datalayer.md` dossiers. All claims
`[VERIFIED]` live 2026-06-12. Generated 2026-06-12.*
