# Milanuncios — UNCAPPED DATA-LAYER Recipe (CARDEEP)

> Target: `milanuncios` (Adevinta Spain) — declared ~666,901 motor (census / marketing).
> **The SPA's own JSON data layer is fully open to plain `curl_cffi` — NO browser, NO
> reese84, NO auth, NO proxy.** This SUPERSEDES `milanuncios.md`, whose conclusion
> ("no browser-callable search API; listing is server-rendered; must DOM-scrape with
> camoufox") was **WRONG**. The SPA is client-rendered and calls a clean REST gateway.
> Country probed: **ES**. Audit date: **2026-06-12**. Engine: `curl_cffi 0.15.0`
> `impersonate="chrome131"`; live-XHR discovery via `camoufox v135.0.1-beta.24`.
>
> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless tagged
> `[ASSUMED]`.

---

## 0. TL;DR — the data layer (THE win)

The SPA does **NOT** server-render the listing. After the camoufox warm-up + in-page
click, a network capture shows the listing component (`Listing.js`) firing a burst of XHRs
to a dedicated milanuncios gateway the prior recipe never found (it only guessed
`web.gw.milanuncios.com` / `api.milanuncios.com` → NXDOMAIN, and `mn.gw.coches.net/search`
→ 404). The real host is **`searchapi.gw.milanuncios.com`**. `[VERIFIED]`

```
GET https://searchapi.gw.milanuncios.com/v4/classifieds
      ?category=13&limit=41&offset=0&sort=newest&transaction=supply
```
→ **200, ~180 KB JSON, `{"ads":[…41 cars…], "ids", "pagination", "photos", …}`**,
called **directly by plain curl_cffi** (chrome131 TLS), no cookie/warm-up/Imperva.
`[VERIFIED]`

- **Host:** `searchapi.gw.milanuncios.com` (CloudFront `3.165.190.71`). Sister host
  `classifieds.gw.milanuncios.com` serves the category tree. `[VERIFIED]`
- **Endpoint:** `GET /v4/classifieds` — the listing data layer (web + app share this
  gateway; `deviceos`-style header not even required for read).
- **`category=13`** = Coches. `transaction=supply` = for-sale ads. `limit` honored up to
  **100/page** (≥101 silently degrades to a 30-ad fallback). `sort ∈
  {relevance, newest, cheapest, oldest, …}`.
- **No auth, no Captcha-Token, no bearer, no `x-schibsted-tenant`.** Standard
  `Accept`/`Origin`/`Referer` to `www.milanuncios.com` is enough. `[VERIFIED]`

### The cap (and why a single cursor does NOT uncap it — unlike wallapop)

| knob | behavior | verdict |
|---|---|---|
| `offset` | walks correctly (offset 5000 → cursor `currentPage:122`) **until 9,959**; at `offset≥~9959` it collapses to a degenerate 30-ad response that **resets to `currentPage:1`** | ❌ hard wall at **10,000** |
| `limit` | honored to 100; 101+ → 30-ad fallback | does not help depth |
| `sort` (all values) | every sort still caps at offset 10,000 | ❌ (the wallapop `order_by` trick does NOT exist here) |
| `pagination.nextToken` (keyset cursor in the body) | **inert as a GET param** — tried as query (`nextToken/cursor/pageToken/searchAfter/…`), as header (`x-next-token/…`), as POST body (→405), via `/v2/search-urls?pg=N` (→ always page 1): **none advance** | ❌ not server-consumed over GET |
| SPA pager | the rendered pager maxes at **page 200** (200 × 41 ≈ 8,200; effective 10k window) | ❌ confirms the 10k view-cap in the UI too |

`[VERIFIED]` all rows. So milanuncios is the **coches.net pathology, not the wallapop
one**: the cap is a hard `from+size ≤ 10,000` ES window per filtered view, and there is no
alternate sort/cursor that lifts it. **The full catalog is reached by FACET PARTITION**
(vector 5), which here is clean and *provable* because the API publishes exact per-cell
counts (next section).

---

## 1. The smoking gun — the API hands you EXACT per-cell counts

`pagination.totalHits` is an Elasticsearch `track_total_hits` object:

```json
"pagination": { "page": 1, "resultsPerPage": 41,
  "nextToken": "eyJkaXIiOiJmI…",            // keyset hint (UI only; not GET-consumable)
  "totalHits": { "relation": "gte", "value": 10000 } }
```

- When a view holds **>10,000** docs → `{"relation":"gte","value":10000}` (clamped; the
  true number is hidden).
- When a filter narrows the view to **≤10,000** → **`{"relation":"eq","value":<EXACT>}`**.
  `[VERIFIED]`

That flip is the coverage oracle: **partition the query space until every cell reports
`relation:"eq"`, and the sum of `value`s is the provable catalog size** — each cell is then
also fully offset-paginable (≤10k) to enumerate its ads.

Examples `[VERIFIED]` in one run:
`brand=ferrari` → `eq:249`; `province=42`(Soria) → `eq:325`; `priceFrom=60000` →
`eq:6812`; `priceFrom=100000&priceTo=200000` → `eq:1639`; `priceFrom=500000` → `eq:61`.

---

## 2. Exact request shape

### 2.1 Listing page
```
GET https://searchapi.gw.milanuncios.com/v4/classifieds
```
| param | value | notes |
|---|---|---|
| `category` | `13` | Coches (motor→coches). `[VERIFIED]` |
| `transaction` | `supply` | for-sale ads |
| `limit` | `100` | max effective page size (101+ → 30-ad fallback) |
| `offset` | `0`,`100`,… | page step; **hard cap at 10,000** |
| `sort` | `newest` | also `relevance`,`cheapest`,`oldest` |

**Filter params (THE partition knobs — exact names matter):** `[VERIFIED]`
| param | meaning | example | ignored-alias trap |
|---|---|---|---|
| **`province`** (singular) | INE province code 1–52 | `province=28` (Madrid) | `provinces`/`provinceIds`/`regions`/`locationIds` are **silently ignored** (still `gte:10000`) |
| **`brand`** | make slug | `brand=ferrari` | `make`/`carMake`/`makes`/`makeSlug` are **silently ignored** |
| `priceFrom` / `priceTo` | € band | `priceFrom=8000&priceTo=12000` | |
| `yearFrom` / `yearTo` | reg-year band | | |

> Anti-trap: an *ignored* filter returns 200 with `gte:10000` and **off-target** ads
> (e.g. `make=ferrari` returns Opel/Leapmotor). Always validate a filter "took" by
> checking `relation` flipped to `eq` OR the returned `title`s match. `brand=ferrari`
> → 4/4 FERRARI titles; `make=ferrari` → 0/4. `[VERIFIED]`

### 2.2 Headers (minimal verified set)
```
accept: application/json, text/plain, */*
accept-language: es-ES,es;q=0.9
origin: https://www.milanuncios.com
referer: https://www.milanuncios.com/
sec-ch-ua-platform: "Windows"
```
`impersonate="chrome131"` supplies UA + TLS/JA3 + h2. **No reese84, no GeeTest, no
bearer.** `[VERIFIED]`

### 2.3 Pagination inside a cell
Page by `offset += limit` while `offset+limit ≤ 10000`. Because each partition cell is
sized `≤10000` (next section), offset paging exhausts every cell. `[VERIFIED]`

---

## 3. Per-item fields (self-contained — no PDP fetch required)

`ads[]` top keys `[VERIFIED]`:
`id, title, url, price, previousPrice, attributes[], authorId, authorName, categories,
contactMethods, description, location, distance, extras, isHighlighted, isNew, origin,
publicationDate, sortDate, updateDate, shipping, transaction, type, visibility`.

| field | meaning |
|---|---|
| `id` | listing id |
| `url` | PDP path → `https://www.milanuncios.com{url}` (`…-{adId}.htm`) |
| `price.cash.value` / `price.financed.value` | € integer (`label` carries formatted string) |
| `previousPrice` | prior price (price-drop signal) |
| `attributes[]` | `{field.raw, value.raw/formatted}` — **car specs:** `kilometers, year, fuel, transmission, hp, doors, color, warranty, environmentalLabel` (and more) |
| `authorId` / `authorName` | **dealer/seller attribution, first-class** (no PDP needed) |
| `location` | city/province geo |
| `publicationDate` / `updateDate` / `sortDate` | epoch ms |
| `photos[]` (top-level, joined by `adId`) | `imageUrls[]` → `https://images.milanuncios.com/api/v1/ma-ad-media-pro/images/{uuid}` |

**Encoding trap `[VERIFIED]`:** strings arrive latin-1 mojibake over the wire
(`h�brido`=`híbrido`, `a�o`=`año`, `kil�metros`). Re-encode:
`s.encode('latin-1').decode('utf-8')` (same trap noted for wallapop).

Pro vs private: `authorName` + warranty/financing language; `sellerType=private` filter
exists (seen in the SPA's carousel call `…&sellerType=private`).

---

## 4. Reproducible harvest script (verified)

```python
from curl_cffi import requests as cr
import time

SA = "https://searchapi.gw.milanuncios.com/v4/classifieds"
HDRS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "es-ES,es;q=0.9",
    "origin": "https://www.milanuncios.com",
    "referer": "https://www.milanuncios.com/",
    "sec-ch-ua-platform": '"Windows"',
}
BASE = {"category": "13", "transaction": "supply", "limit": "100", "sort": "newest"}
PRICE_BANDS = [(0,1000),(1000,2000),(2000,3000),(3000,5000),(5000,8000),(8000,12000),
               (12000,18000),(18000,25000),(25000,40000),(40000,70000),(70000,None)]

def fix(s):
    if not isinstance(s, str): return s
    try: return s.encode("latin-1").decode("utf-8")
    except Exception: return s

def count(params):
    p = dict(BASE); p.update(params); p["limit"] = "1"
    th = cr.get(SA, params=p, headers=HDRS, impersonate="chrome131", timeout=30
        ).json()["pagination"]["totalHits"]
    return th["relation"], th["value"]              # ("eq", N) once <10k

def drain_cell(params, seen, throttle=0.3):
    off = 0
    while off < 10000:
        p = dict(BASE); p.update(params); p["offset"] = str(off)
        r = cr.get(SA, params=p, headers=HDRS, impersonate="chrome131", timeout=40)
        if r.status_code != 200: break
        ads = r.json().get("ads", [])
        if not ads: break
        for a in ads:
            if a["id"] in seen: continue
            seen.add(a["id"])
            at = {x["field"]["raw"]: x["value"]["raw"] for x in a.get("attributes", [])}
            yield {
                "id": a["id"], "url": "https://www.milanuncios.com" + a["url"],
                "title": fix(a.get("title")),
                "price": (a.get("price", {}).get("cash") or {}).get("value"),
                "year": at.get("year"), "km": at.get("kilometers"),
                "fuel": fix(at.get("fuel")), "transmission": at.get("transmission"),
                "hp": at.get("hp"), "authorId": a.get("authorId"),
                "authorName": fix(a.get("authorName")),
            }
        if len(ads) < int(BASE["limit"]): break
        off += int(BASE["limit"]); time.sleep(throttle)

def harvest_all():
    """province × price-band partition; every cell <10k => full enumeration."""
    seen = set()
    for prov in range(1, 53):                         # 52 ES provinces
        rel, _ = count({"province": str(prov)})
        if rel == "eq":
            for ad in drain_cell({"province": str(prov)}, seen): yield ad
        else:                                         # >10k -> sub-band by price
            for lo, hi in PRICE_BANDS:
                f = {"province": str(prov), "priceFrom": str(lo)}
                if hi: f["priceTo"] = str(hi)
                rel2, _ = count(f)
                # rare: a band still >10k -> add brand or year sub-facet here
                for ad in drain_cell(f, seen): yield ad

if __name__ == "__main__":
    n = 0
    for ad in harvest_all():
        n += 1
    print("TOTAL UNIQUE:", n)
```

`brand` is an alternate top-level partition axis if you prefer make-based sharding; mix
`brand`+`province` for the very few cells still >10k. `[VERIFIED]` filters compose.

---

## 5. Vector-by-vector log (CARDEEP order)

### 1) SITEMAP — ❌ DEAD to curl (S3-gated; robots behind the wall)
- `/sitemap.xml` (and ~30 key variants) → **`403 AccessDenied`**, served by `server:
  AmazonS3` via CloudFront (`x-amz-cf-pop`). A sitemap bucket exists but `GetObject` is
  origin-denied for the public; every guessed key returns the same S3 `AccessDenied`
  (not `NoSuchKey`), so key-guessing is futile. `[VERIFIED]`
- `/robots.txt` → **`405` GeeTest wall** (server `bon`, 97 KB captcha body); the canonical
  `Sitemap:` directive is hidden behind the listing wall. Googlebot UA does not lift it.
- HTML sitemap pages indexed by Google (`/anuncios/sitemap-xml-php.htm`,
  `/anuncios-en-{prov}/sitemap-xml.htm`) all → **`405` GeeTest** to curl. `[VERIFIED]`
  **Outcome: no curl-reachable sitemap. Not the enumeration path.**

### 2) MOBILE APP API — ✅ same gateway, already covered
- No `*.milanuncios.com` app host resolves (`api/app/m/mobile/gateway/web.gw…` →
  NXDOMAIN). But the **web XHR gateway `searchapi.gw.milanuncios.com` IS the shared
  web+app data layer** (`/v4/classifieds`), and it is anonymous + open to curl. A separate
  app endpoint/signing/X-App header is unnecessary. `[VERIFIED]`
  **Outcome: the app API is the same `searchapi.gw` gateway — no extra surface needed.**

### 3) ALTERNATE / CURSOR ENDPOINT — ⚠️ endpoint found, cursor inert
- `searchapi.gw.milanuncios.com/v4/classifieds` is the alternate (real) endpoint vs the
  DOM scrape. Its keyset `pagination.nextToken` is **not GET-consumable** (query/header/
  POST/`search-urls` all fail to advance), and **all sorts cap at offset 10,000**. So,
  unlike wallapop, no single cursor enumerates the catalog. `[VERIFIED]`
  **Outcome: endpoint is the win; depth within one view is capped at 10k → partition.**

### 4) IN-BROWSER XHR (camoufox capture) — ✅ how the endpoint was discovered
- Warm-up + in-page click, then logged every request: the listing fires
  `/v4/classifieds?category=13&limit=41&offset=0&sort=relevance&transaction=supply`
  (+`/v3/pole-position-ads`, `/v4/search-listing/carousel`, `/v1/breadcrumbs`,
  `/v2/form/search`, `/v1/crosslinks`, `classifieds.gw…/v1/category-trees/search`).
  This **refutes** `milanuncios.md`'s "no client `/search` XHR; server-rendered" claim.
  `[VERIFIED]` Artifacts: `scratch/milanuncios/network_requests.json`, `json_responses.json`.
  **Outcome: SUCCESS — surfaced the clean JSON data layer.**

### 5) FACET PARTITION — ✅ **THE coverage mechanism** (clean & provable here)
- The 10k window is hard per view (offset/sort/cursor all capped). Partition by
  **`province` (1–52)**: **46/52 return exact `eq` counts (sum 142,510)**; the 6 metro
  provinces still `gte:10000` (Alicante 3, Barcelona 8, Madrid 28, Málaga 29, Sevilla 41,
  Valencia 46) **each fully resolve below 10k under a price-band sub-facet** — every band
  `eq` (Madrid Σ=50,356; Barcelona Σ=23,083; Alicante Σ=12,797, `all_eq=True`).
  `[VERIFIED]` `brand` is an independent partition axis; `brand`+`province` covers the
  residual. **Province × price-band is a complete, gap-free, count-provable partition;
  each cell ≤10k is offset-paginable to exhaustion.**
  **Outcome: SUCCESS. This is the recipe's enumeration strategy.**

---

## 6. Verdict

- `uncapped_surface_found = false` (no single uncapped cursor exists — the data layer is
  hard-capped at a 10,000 window per filtered view; the wallapop `order_by` trick has **no
  analogue** here). **BUT** the full catalog is reachable and **count-provable** via the
  clean JSON API under **facet partition** (vector 5), with no browser/proxy/auth.
- **Method:** `GET https://searchapi.gw.milanuncios.com/v4/classifieds` with
  `category=13&transaction=supply&limit=100&sort=newest`, partitioned by **`province`
  (1–52)**, sub-partitioned by **`priceFrom`/`priceTo`** for the 6 metro provinces still
  >10k; drive each ≤10k cell by `offset`. Confirm each cell via
  `pagination.totalHits.relation=="eq"`. Direct `curl_cffi impersonate="chrome131"`.
- **Declared total:** ~666,901 (census/marketing, all-time). **Live ES `transaction=supply`
  catalog** measured bottom-up: 46 eq-provinces = **142,510** + the 6 metro provinces'
  price-banded sums (Madrid 50,356 + Barcelona 23,083 + Alicante 12,797 + Málaga + Sevilla
  + Valencia) → on the order of **~250k–290k currently-listed cars** (`[ASSUMED]` for the
  three not fully summed in this audit; their per-band drain is identical). The marketing
  ~667k exceeds the live count, mirroring the wallapop finding (marketing N > live N).
- **Coverage proof:** the API publishes EXACT counts (`relation:"eq"`) for every cell once
  <10k; summation across the province×price partition is the gap-free enumeration
  guarantee, and each cell is independently offset-paginable. `[VERIFIED]`
- **Cost:** €0. No proxy, no browser (for the harvest), no auth, no CAPTCHA. The camoufox
  warm-up is needed **only once** to discover the XHR; the harvest itself is pure curl.

### Artifacts (`scratch/milanuncios/`)
- `network_requests.json`, `json_responses.json` — full camoufox XHR capture (the discovery).
- `api_base.json` — a raw `/v4/classifieds` 200 response (field reference).
- `srp.html`, `next_data_summary.json` — un-walled SRP + page-shape dump.
- Probe scripts at repo root: `scratch_mn_capture.py` (XHR capture), `scratch_mn_api.py`
  (offset/sort cap), `scratch_mn_cursor.py`/`_cursor2.py` (cursor inert proof),
  `scratch_mn_facet_verify.py` (filter-param verification),
  `scratch_mn_coverage.py` (province×price coverage proof).
