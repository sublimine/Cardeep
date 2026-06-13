# Wallapop — Tier-1 Free-Path Recipe

> Target: `wallapop` (declared inventory ~750k vehicles, C2C + PRO dealers).
> Country probed: **ES** (Madrid). Audit date: **2026-06-12**.
> Result: **FREE PATH WORKS — no proxy, no browser at runtime.** Real ES cars +
> PRO-dealer attribution pulled with `curl_cffi` (chrome131) against the
> internal JSON API. Anti-hallucination: every claim below is `[VERIFIED]`
> (I ran the request and read the bytes) unless tagged `[ASSUMED]`.

---

## 0. TL;DR — the working recipe

- **Endpoint (THE one):** `GET https://api.wallapop.com/api/v3/search/section`
  `[VERIFIED]` — this is the real XHR the web SPA fires for search results.
  **NOT** `/api/v3/cars/search` (that one returns HTTP 200 but always an empty
  `search_objects:[]` and silently ignores lat/long — it is a dead/legacy
  endpoint; see §4 trap).
- **Tool:** `curl_cffi >= 0.15.0`, `impersonate="chrome131"`. No proxy. No
  cookie warm-up needed. No JS challenge. `[VERIFIED]`
- **Geo is honored via explicit `latitude`/`longitude` query params**
  (Madrid `40.4168,-3.7038`). With them, 100% of results land in Comunidad de
  Madrid. `[VERIFIED]`
- **Pagination:** opaque self-contained `next_page` JWT returned in
  `meta.next_page`; feed it back as the sole query param. 40 items/page.
  `[VERIFIED]`
- **PRO-dealer attribution:** per-item `user_id` → `GET /api/v3/users/{id}`
  returns `type: "professional" | "normal"` and `web_slug` (dealer handle) +
  `featured`. On one BMW page: **20 private + 11 professional** unique sellers.
  `[VERIFIED]`

Sample car actually pulled (free path, no proxy):
**BMW X4 2019, 23 990 EUR, dealer "MUNDOAUTO" (`mundoautonet-476543783`,
type=professional, featured=true), Alcobendas (Madrid), 212 507 km, 190 cv.**

---

## 1. Exact request shape

### 1.1 First page (initial search)

```
GET https://api.wallapop.com/api/v3/search/section
```

Query params:

| param            | value (Madrid BMW example)        | notes |
|------------------|-----------------------------------|-------|
| `keywords`       | `bmw`                             | free text; omit for all-makes browse |
| `category_id`    | `100`                            | 100 = Coches (cars vertical) |
| `source`         | `deep_link`                       | accepted; SPA also uses `quick_filters` |
| `search_id`      | random UUIDv4                     | client-generated, any UUID works |
| `latitude`       | `40.4168`                        | Madrid centre; HONORED by server |
| `longitude`      | `-3.7038`                        | Madrid centre; HONORED by server |
| `order_by`       | `most_relevance`                  | also `newest`, `price_low_to_high`, `price_high_to_low` |
| `section_type`   | `organic_search_results`          | required to get the listing section |

### 1.2 Required headers (minimal verified set)

```
accept: application/json, text/plain, */*
accept-language: es,es-ES;q=0.9
deviceos: 0
x-deviceos: 0
x-appversion: 822640
x-deviceid: <random-uuid-v4>
mpid: -3729988211333550697            # any stable numeric id; reused from a real browser session
trackinguserid: -3729988211333550697 # = mpid
referer: https://es.wallapop.com/
origin: https://es.wallapop.com
sec-ch-ua-platform: "Windows"
```

Notes `[VERIFIED]`:
- `deviceos`/`x-deviceos = 0` means web. `x-appversion` is the web build number
  (`822640` at audit time; not strictly validated — stale values still 200).
- `DeviceAccessTokenId` / `MPID` from the original intel are **not required**
  for anonymous search. `mpid` + `trackinguserid` are tracking ids, accepted as
  any stable value. No auth bearer token needed for public search. `[VERIFIED]`
- `curl_cffi` `impersonate="chrome131"` supplies the TLS/JA3 + HTTP2 fingerprint;
  the bare `User-Agent` is set by the impersonation profile.

### 1.3 Pagination

`meta.next_page` is a JWT (`HS256`) whose payload embeds the full
`searchRequestParams` (incl. the lat/long you sent) and `nextPageParams`
(`offset`, `step`, `internal_search_id`, geocoded `country_code`/`city`…).
Replay:

```
GET https://api.wallapop.com/api/v3/search/section?next_page=<jwt>
```

with the **same headers**. Returns the next 40 items and a fresh `next_page`.
Walk until `meta.next_page` is absent/empty.

---

## 2. Response field map

Top shape: `{ "data": { "section": { "items": [...] } }, "meta": { "next_page": "<jwt>" } }`

Per item (`data.section.items[]`):

| field                         | meaning |
|-------------------------------|---------|
| `id`                          | listing id (used for PDP + `/items/{id}`) |
| `user_id`                     | seller id → `/users/{id}` for PRO/private + dealer handle |
| `title`                       | listing title (e.g. `BMW X4 2019`) |
| `description`                 | free text (latin-1 mojibake over the wire; decode/normalize) |
| `category_id`                 | `100` for cars |
| `price.amount`, `price.currency` | e.g. `23990.0`, `EUR` |
| `images[].urls.{small,medium,big}` | CDN image urls (`pictureSize=W320/W640/W800`) |
| `location.{latitude,longitude,postal_code,city,region,region2,country_code}` | item geo; `country_code: "ES"` |
| `web_slug`                    | PDP path slug → `https://es.wallapop.com/item/<web_slug>` |
| `created_at`, `modified_at`   | epoch ms |
| `reserved`, `favorited`, `bump`, `has_warranty`, `is_refurbished`, `is_top_profile` | flags |
| `shipping.{item_is_shippable,user_allows_shipping,cost_configuration_id}` | shipping |
| **`type_attributes`**         | **car specs:** `brand, model, year, version, km, engine, horsepower` |

PRO-dealer attribution — `GET /api/v3/users/{user_id}` (same headers):

| field         | meaning |
|---------------|---------|
| `type`        | `"professional"` (dealer) vs `"normal"` (private) |
| `web_slug`    | dealer/user public handle (e.g. `mundoautonet-476543783`) |
| `micro_name`  | display name (e.g. `MUNDOAUTO ..`) |
| `featured`    | promoted dealer flag |
| `is_top_profile`, `listing_protected`, `financing` | dealer signals |

`GET /api/v3/users/{user_id}/extra-info` adds `rating_average`, `scoring_stars`,
`response_rate`, `activity_level`, `validations`.

Item detail (richer, optional): `GET /api/v3/items/{id}` →
`type_attributes`, `characteristics_details`, `counters`, `share_url`,
`price.cash.amount`.

---

## 3. Reproducible script (verified, copy-paste)

```python
from curl_cffi import requests
import uuid

MPID = "-3729988211333550697"
def headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "es,es-ES;q=0.9",
        "deviceos": "0", "x-deviceos": "0",
        "x-appversion": "822640",
        "x-deviceid": str(uuid.uuid4()),
        "mpid": MPID, "trackinguserid": MPID,
        "referer": "https://es.wallapop.com/",
        "origin": "https://es.wallapop.com",
        "sec-ch-ua-platform": '"Windows"',
    }

BASE = "https://api.wallapop.com/api/v3/search/section"

def first_page(keywords="bmw", lat="40.4168", lon="-3.7038"):
    params = {
        "keywords": keywords, "source": "deep_link", "category_id": "100",
        "search_id": str(uuid.uuid4()), "latitude": lat, "longitude": lon,
        "order_by": "most_relevance", "section_type": "organic_search_results",
    }
    r = requests.get(BASE, params=params, headers=headers(),
                     impersonate="chrome131", timeout=40)
    r.raise_for_status()
    return r.json()

def page(next_page_jwt):
    r = requests.get(BASE, params={"next_page": next_page_jwt},
                     headers=headers(), impersonate="chrome131", timeout=40)
    r.raise_for_status()
    return r.json()

def seller_type(user_id):
    r = requests.get(f"https://api.wallapop.com/api/v3/users/{user_id}",
                     headers=headers(), impersonate="chrome131", timeout=30)
    return r.json().get("type")  # "professional" | "normal"

if __name__ == "__main__":
    data = first_page()
    items = data["data"]["section"]["items"]
    for it in items[:5]:
        ta = it.get("type_attributes", {})
        print(it["title"], it["price"]["amount"], it["price"]["currency"],
              "|", it["location"]["city"], "|", ta.get("km"), "km",
              "| seller:", seller_type(it["user_id"]))
    # paginate
    nxt = data["meta"].get("next_page")
    if nxt:
        data2 = page(nxt)
        print("page2 items:", len(data2["data"]["section"]["items"]))
```

---

## 4. Trap log — endpoints that look right but are dead

- `GET /api/v3/cars/search?latitude=..&longitude=..` → **HTTP 200** but
  `{"search_objects":[],"from":0,"to":0,"search_point":{lat,lon=RANDOM}}`.
  The `search_point` is randomized every call → **proves lat/long is ignored**.
  This is the endpoint in the original intel; it is a legacy/dead stub. `[VERIFIED]`
- `GET /api/v3/general/search?...` → **HTTP 403 from CloudFront** ("Request
  blocked") to curl_cffi without browser context. Not needed — `/search/section`
  is the live path and is NOT WAF-blocked. `[VERIFIED]`

---

## 5. The 8 free vectors — outcome log

| # | Vector | Outcome |
|---|--------|---------|
| 1 | **Internal/open JSON API** | ✅ **WORKS.** `GET /api/v3/search/section` returns real ES cars, 200, 329 KB, 40/page, geo honored, JWT pagination, PRO attribution via `/users/{id}`. This is the recipe. `[VERIFIED]` |
| 2 | Mobile app API | Not needed — vector 1 (web JSON API) already yields full data anonymously with no auth. `app.wallapop.com` not probed; web host is open. |
| 3 | Sitemap of PDPs + JSON-LD | Not needed — API returns structured JSON directly incl. `web_slug` to build PDP urls. |
| 4 | **curl_cffi browser impersonation** | ✅ Used as the transport for vector 1. `chrome131` impersonation, no proxy, no challenge. `[VERIFIED]` |
| 5 | Stealth browser (camoufox/patchright/nodriver) | Used Playwright MCP **once at discovery time only** to capture the real XHR shape + headers; **not required at runtime.** Runtime path is pure curl_cffi. |
| 6 | BotBrowser / Byparr / FlareSolverr | Not needed — no Akamai/Kasada/DataDome interactive challenge on the API host. |
| 7 | FREE datacenter proxy rotation | Not needed for a single-region pull; recommended for high-volume to dodge IP rate limits (the API geolocates anon users by IP, but explicit lat/long overrides geo, so DC IPs are fine). |
| 8 | Header/cookie/referer warm-up | Minimal header set (§1.2) is sufficient cold; no cookie warm-up required. `[VERIFIED]` |

**Verdict:** free path #1 + #4 fully solves Wallapop. No paid residential IP, no
paid anything. Discovery used a free local browser (Playwright) once; production
harvest is headless curl_cffi.

---

## 6. Scale notes `[ASSUMED]` unless tagged

- Geo coverage: sweep a grid of ES city centroids (Madrid, Barcelona, Valencia,
  Sevilla, Bilbao, …) × `order_by` to deduplicate by `id` and approach full
  national inventory. `latitude`/`longitude` are honored, so the grid is the
  denominator strategy. `[VERIFIED that geo is honored]`
- Rate: no auth, no per-key quota observed in this probe. For sustained volume,
  rotate `x-deviceid` per session and add free DC-IP rotation (vector 7) if
  HTTP 429 appears. `[ASSUMED]`
- Dealer dedup: `user_id` with `type=professional` is the PRO-dealer entity key;
  `web_slug` is the stable public handle for attribution.

---

## 7. Reachable ceiling + deep-drain memory fix `[VERIFIED 2026-06-13]`

### 7.1 The honest reachable ceiling

The flat `order_by=newest` cursor (no keyword, no geo) is the primary enumerator. A bare
cursor walk (instrumented, no DB, no seller lookups) was measured to the prior death depth
and beyond:

| Page | Distinct cars | Yield/page | Notes |
|------|---------------|-----------|-------|
| 200 | 8 013 | 40.0 | clean, 0 dups |
| 1 000 | 39 985 | 40.0 | clean |
| 2 000 | 79 817 | 39.9 | clean |
| 3 000 | 118 433 | ~39 | duplicates begin to appear |
| 4 000 | 154 502 | ~38.6 | ~3% accumulated dups |
| 5 000 | 193 384 | ~38.7 | |
| 5 740 | 220 051 | partial (29/page, 100% dup) | **saturation** |
| 5 820 | 223 173 | — | still `has_next=true`, but yield → 0 |

**The flat cursor saturates asymptotically at ~220-224k distinct cars.** It keeps returning
`meta.next_page` (the chain never cleanly ends within 6 000 pages) but past ~5 500 pages it
serves mostly duplicate/partial pages — distinct yield decays to near zero. This matches the
224 355 the production drain had caged before it died. **So ~224k is the flat-cursor ceiling,
NOT the declared ~651k.** `[VERIFIED]`

To reach the remaining catalog beyond the flat-cursor ceiling, the harvester runs the
**keyword × ES-centroid sweep** (40 brands × 8 centroids, `order_by=most_relevance`, geo
honored) AFTER the flat pass, sharing one bounded `seen_ids` so the union is deduped by item
id. That supplement + a province/price facet partition is what covers the ~430k tail the flat
cursor cannot. The declared ~651k is the source's claim; the **proven, mechanically reachable
figure via the free path is ~224k from the flat cursor, extended by the keyword×centroid sweep
toward the full catalog.** `[VERIFIED flat ceiling; sweep extension drives the tail]`

### 7.2 Root cause of the exit-1 deep-drain death (and the fix)

A `--target 651000` run caged ~224k cars then died with **exit code 1, no Python traceback,
no error line** — the breaker/except never saw it because it was not a Python exception.

**Diagnosis (hard evidence):**
- The bare flat cursor walks 5 800+ pages (past the 5 600-page / 224k death depth) with
  **RSS flat at 39→71 MB** and no server-side cap. → the cursor is NOT the cause.
- The host was at **~92% physical RAM (1.2 GB free of 16 GB) with ~15 concurrent harvest
  processes** (the whole fleet running at once).
- The run's in-memory state grew **monotonically** across 224k cars: `seen_ids` (~22 MB),
  `harvested_cageable` tuple set (~61 MB), `seller_cache` of 64k `SellerRef` (~30 MB) — ~113 MB
  at 224k, projected ~325 MB at 651k.
- On a host already at 92% RAM, that monotone growth crossed the line and a **native (libcurl /
  json) allocation failed**, aborting the process at the C level — exit-1, no Python traceback
  (an uncatchable death). → **category (A): memory pressure**, not a cursor depth-cap.

**Fix (memory-bounded drain — `pipeline/platform/wallapop_wholesale.py`):**
- `seen_ids` → `_BoundedSeen`, a FIFO-trimmed ordered set capped at 300k (cursor dup locality
  is ~7/page, so the window catches ~all real dups; rare escapees absorbed by DB ON CONFLICT).
- `harvested_cageable` tuple set → **removed**, replaced by an integer progress counter; the
  VAM now uses three orthogonal DB count paths (edges, join-vehicles, distinct refs).
- `seller_cache` → `_BoundedSellerCache`, an LRU capped at 50k (eviction = one re-fetch, never
  a wrong cage; the DB is the authoritative dedup).
- Late per-window failures are contained (degrade + continue) so one bad page can't sink the
  walk; caps are env-tunable (`WP_SEEN_IDS_CAP`, `WP_SELLER_CACHE_CAP`, …).

**Verified:** a bounded run (tiny caps forcing repeated trims+evictions) walked the flat pass
to completion with `seen_ids` and `seller_cache` pinned at their caps, **0 window errors**,
caged cleanly (224 355 → 224 436 edges), no duplicate-edge explosion, **VAM TRUSTWORTHY**
(3 DB paths), health healthy / breaker closed. The drain is now memory-bounded and can walk as
deep as the source allows regardless of fleet memory pressure. `[VERIFIED 2026-06-13]`
