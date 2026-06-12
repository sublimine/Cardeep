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
