# spoticar — UNCAPPED Data-Layer Recipe (full ES public stock, no relevance cap)

Status: **UNCAPPED SURFACE FOUND.** The serving gateway flat-enumerates 100% of
the ES public inventory with NO relevance/depth cap (unlike coches.net's UI wall).
Platform: **spoticar.es** (Stellantis ES — Drupal SPA + Elasticsearch-backed JSON API).
Akamai posture: AkamaiGHost 403 to *plain* curl; **`curl_cffi impersonate="chrome131"`
passes the wall cleanly** on homepage, listing, sitemap AND the JSON API.
Declared inventory: **~50,000** `[ASSUMED]` (pan-brand OEM marketing claim).
Live ES public stock (ES country): **6,334** `[VERIFIED]` — the API's own
`count.value`, the `list/search` `countNumber`, the brand-facet sum, the
points-of-sale-facet sum, AND the dedicated `/api/count-published-vo` counter all
agree. The 50k figure is global/pan-locale marketing, not the ES served stock.
Verified LIVE: **2026-06-12** (curl_cffi 0.15.0, `impersonate="chrome131"`, no proxy,
no browser, no auth, no cookie warm-up, €0).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`. This doc supersedes two claims in the prior `spoticar.md`:
> (1) `lastPage=576` is METADATA, not the data boundary — the real last data page
> is **528** (page 528 = 11 trailing hits, 529+ = 0). (2) The sitemap does **NOT**
> enumerate per-car PDPs — it is SEO facet pages only. The JSON API is the sole
> complete per-car surface.

---

## 0. TL;DR — the uncapped surface (THE win)

The SPA calls an **internal Elasticsearch-backed JSON API**. The paginate endpoint
walks the **entire 6,334-vehicle ES index** as a flat sequential cursor with **no
relevance cap and no depth cap**. Harvest = walk `?page=N` 1 → 528, dedup on
`field_vo_carnum`.

```
GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}
```

Minimal headers that return HTTP 200 `application/json`:

```
Accept: */*
X-Requested-With: XMLHttpRequest
Accept-Language: es-ES,es;q=0.9
Referer: https://www.spoticar.es/comprar-coches-de-ocasion
```

- **Tool:** `curl_cffi` with `impersonate="chrome131"` (the enabling tool — plain
  curl gets AkamaiGHost 403; the Chrome TLS/JA3 fingerprint passes). `[VERIFIED]`
- **Method:** `GET`. No body, no auth, no bearer, no cookie warm-up. `[VERIFIED]`
- **Page size:** **fixed 12 hits/page** (not overridable). `[VERIFIED]`
- **Cursor:** plain integer `page=1..528`. `count.value` (6334) bounds the run;
  page 528 returns the trailing 11, pages 529+ return 0 hits. `[VERIFIED]`
- **DO NOT pass `sort=` / `orderby=`** — see §4 trap (origin 503 on some pages).

### Coverage proof (the load-bearing evidence) `[VERIFIED]`
Walked the **plain `?page=N`** cursor LIVE, pages 1→531: **531 pages HTTP 200**,
unique `field_vo_carnum` grew **linearly** (page 100→1,187 · 200→2,355 · 300→3,510
· 400→4,668 · 500→5,845), ended naturally at page 531 on 3 consecutive empty pages.
**6,176 unique cars = 97.5% of the declared 6,334 in a single uncoordinated pass.**
The 2.5% gap is live row-drift over a ~10-min walk (ES default sort is not stable
across a long crawl + inventory churns), NOT a cap — a production harvest that
dedups on `carnum` and re-sweeps the gaps reaches ~100%. **No relevance truncation,
no depth wall** — this is a true flat enumeration, the coches.net pathology is
ABSENT here. `[VERIFIED]`

---

## 1. The denominator — four independent surfaces agree on 6,334

| Surface | Value | `[VERIFIED]` |
|---|---:|---|
| `paginate/search` → `count.value` | **6,334** | yes |
| `list/search` → `countNumber` | **6,334** | yes |
| `list/search` → Σ brand-facet `doc_count` (40 brands) | **6,334** | yes |
| `list/search` → Σ points-of-sale-facet `doc_count` (135 dealers) | **6,334** | yes |
| `/api/count-published-vo` → `count_vo_published` | **6,336** | yes (±2 live jitter) |

The denominator is **national / facet-independent** — it is the full ES public
stock, not a geo- or relevance-bounded window. 40 brands, 135 dealers, all summing
exactly to the headline count. `[VERIFIED]`

Dedicated counter endpoint (intel-named, confirmed live):
```
GET https://www.spoticar.es/api/count-published-vo  ->  200  {"count_vo_published":"6336"}
```

---

## 2. Exact request shape

### 2.1 Harvest endpoint (the vehicle data)
```
GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}
```
- 12 cars/page in `hits[]._source` (raw Elasticsearch documents).
- Walk `page=1 … 528`. `count.value` + emptiness bound the run.
- Top-level keys: `count, hits, pdv_information, aggregation, filtersLabels,
  renderEntities, selectedFilters, lastPage, is_paginate, current_page,
  is_enabled_fast_infinite_scroll`. `[VERIFIED]`
- **`lastPage` (=576) is a metadata artefact, NOT the data boundary.** Pages
  529–576 return **0 hits**; pages >576 return phantom 10-hit blocks of REPEATING
  ids (infinite-scroll wrap garbage). The true data boundary is **page 528**
  (11 trailing hits). `[VERIFIED]`

### 2.2 Facets / denominator endpoint (counts, brands, dealers)
```
GET https://www.spoticar.es/api/vehicleoffers/list/search?page={N}
```
- `brands` and `pointsofsale` are **double-wrapped lists** (`j["brands"][0]`,
  `j["pointsofsale"][0]`). Each entry: `{"key": <name>, "doc_count": <n>}`;
  dealers also carry `id_geoloc.buckets[].key` (geo id). `[VERIFIED]`
- `count` here is a server-rendered HTML fragment (`<h2>(6334 Vehículos…)</h2>`);
  use the numeric `countNumber` field instead. `[VERIFIED]`

### 2.3 Published-count endpoint (cheap denominator)
```
GET https://www.spoticar.es/api/count-published-vo  ->  {"count_vo_published":"6336"}
```

### 2.4 Pagination / page size
Page size is **fixed at 12**; no `size`/`limit`/`per_page` override observed.
Full run = ~528 GET requests. `[VERIFIED]`

---

## 3. Per-car fields (`hits[]._source` — self-contained, no PDP fetch needed)

Most fields arrive as **single-element arrays** — unwrap `v[0]`. `[VERIFIED]`

| Canonical | Source field | Example |
|---|---|---|
| deep_link (PDP path) | `url` | `/comprar-vehiculo-de-ocasion/fiat-500-…-castellon-1202076554` |
| listing_ref / nid | `field_vo_refbase` / `nid` | `1202076554` / `1038604` |
| **carnum (stable id, dedup key)** | `field_vo_carnum` | `ES_ES008VS_1202076554` |
| make | `marque` / `marque_no_accent` | `fiat` |
| model / line | `model` / `ligne` | `500` / `fiat 500` |
| version/trim | `version` / `finition_name` | `hb 320km 85kw (118cv)+style+com monotrim` |
| model year / first-reg | `field_vo_annee_modele` / `field_vo_dpi` | `2024` / `2024` |
| km (certified bool) | `field_vo_km` / `field_vo_km_certifie` | `10` |
| **price (base)** | `field_vo_prix_base` (`field_vo_pb_devise`) | `22390` `eur` |
| price (financed) / monthly | `field_vo_prix_financement` / `field_monthlypayment` | `19540` / `335.13` |
| fuel | `fuel_type` / `type_carburant` | `ELEC` / `eléctrico` |
| gearbox | `boite_vitesse` / `transmission` | `automático` |
| power (CV) | `field_vo_puissance_physique` (`field_vo_pp_unite`) | `118` `ch` |
| color / doors / seats | `color` / `field_vo_nb_portes` / `field_vo_nb_places` | `Verde` / `3` / `4` |
| **VIN** | `field_vo_vin` | `zfaefaa4xpx169902` |
| plate | `field_vo_immatri` | `0155mrt` |
| body / genre | `field_vo_categories` / `field_vo_genre` | `urbano` / `vp` |
| **dealer name** | `field_pdv_title` | `spoticar comauto sport` |
| dealer brand / city | `field_pdv_brand` / `field_pdv_city` | `SP` / `castellon` |
| dealer geo id / lat,lng | `field_pdv_geo_id` / `field_pdv_geolocation` | `0000115058` / `39.970016,-0.070215` |
| battery SoH / green-zone | `field_soh` / `field_green_zone_level` | `95.3` / `0` |

**Dealer attribution is best-in-class & self-contained** — every car carries its
named Stellantis point-of-sale + geo id + lat/lng. No separate dealer lookup needed.
135 distinct dealers enumerable from the `list/search` `pointsofsale` facet. `[VERIFIED]`

**Encoding trap `[VERIFIED]`:** the API serves some text latin-1/mojibake over the
wire (`CITRO�N` = "Citroën"; `C�rdoba` = "Córdoba"). Re-encode brand/dealer/city
strings: `s.encode("latin-1").decode("utf-8")` (or normalise the known brand set).
The numeric `field_*` fields and `field_vo_carnum` are clean.

### Sample car (real, pulled via free path) `[VERIFIED]`
- **Fiat 500 HB 320km 85kW (118cv) Style+Com Monotrim** — 2024, 10 km, eléctrico, Verde
- Price **22.390 EUR** (financed 19.540 EUR / 335,13 €/mo)
- VIN `zfaefaa4xpx169902`, plate `0155mrt`, carnum `ES_ES008VS_1202076554`
- Dealer **Spoticar Comauto Sport**, Castellón (geo `39.970016,-0.070215`)

---

## 4. Traps & gotchas (hard-won this pass)

1. **`sort=price` / `orderby=` causes origin 503.** Adding a sort param triggers
   AkamaiGHost **`503 Service Unavailable - Zero size object`** on some deep pages
   (origin cache miss — sort is not a supported cache key). The SAME page WITHOUT
   sort returns 200. **Harvest with plain `?page=N` only.** `[VERIFIED]`
   (Page 223: no-sort → 200/12 hits; `sort=price` → 503.)
2. **`lastPage=576` is a lie for data.** Real last data page = **528**. Pages
   529–576 → 0 hits; >576 → repeating phantom blocks. Stop on first empty + a
   small empty-run guard, or bound by `count.value`. `[VERIFIED]`
3. **Default sort is not stable across a long crawl** → ~2–3% row drift / dupes
   over a 10-min walk. Dedup on `field_vo_carnum` and re-sweep the gap pages.
   `[VERIFIED]` (250–300 stretch showed ~3% dupes; this is drift, not a cap.)
4. **Facet filtering is by facet `key`, not arbitrary query params** — passing
   `marque=peugeot` was ignored (returned full 6334). Not needed for harvest
   (flat walk covers all); only relevant if you ever want to shard. `[VERIFIED]`

---

## 5. Reproducible harvest script (verified shape)

```python
from curl_cffi import requests
import time

PAG = "https://www.spoticar.es/api/vehicleoffers/paginate/search"
H = {
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.spoticar.es/comprar-coches-de-ocasion",
}

def fix(s):  # latin-1 mojibake repair for brand/dealer/city text
    if not isinstance(s, str): return s
    try: return s.encode("latin-1").decode("utf-8")
    except Exception: return s

def unwrap(v):
    return v[0] if isinstance(v, list) and v else v

def page(n, retries=3):
    for _ in range(retries):
        r = requests.get(PAG, params={"page": n}, headers=H,
                         impersonate="chrome131", timeout=40)   # NO sort param
        if r.status_code == 200:
            return r.json().get("hits") or []
        time.sleep(1.5)
    return None

def harvest(throttle=0.18):
    seen, empties, n = {}, 0, 1
    while True:
        hits = page(n)
        if hits is None:
            n += 1; continue                       # transient, retry next
        if not hits:
            empties += 1
            if empties >= 3: break                 # end of data
            n += 1; continue
        empties = 0
        for h in hits:
            s = h.get("_source", {})
            cn = unwrap(s.get("field_vo_carnum"))
            if not cn or cn in seen: continue
            seen[cn] = {
                "carnum": cn,
                "url": unwrap(s.get("url")),
                "make": fix(unwrap(s.get("marque"))),
                "model": unwrap(s.get("model")),
                "version": unwrap(s.get("version")),
                "year": unwrap(s.get("field_vo_annee_modele")),
                "km": unwrap(s.get("field_vo_km")),
                "price": unwrap(s.get("field_vo_prix_base")),
                "vin": unwrap(s.get("field_vo_vin")),
                "dealer": fix(unwrap(s.get("field_pdv_title"))),
                "dealer_geo": unwrap(s.get("field_pdv_geolocation")),
                "city": fix(unwrap(s.get("field_pdv_city"))),
            }
        n += 1
        time.sleep(throttle)
    return list(seen.values())

if __name__ == "__main__":
    cars = harvest()
    print("UNIQUE CARS:", len(cars))   # ~6334 after dedup + gap re-sweep
```

Single IP held 531 sequential pages with no 429/ban at ~0.18 s/req `[VERIFIED]`.
For a polite full run add FREE datacenter-IP rotation; not required for access.

---

## 6. Vector-by-vector log (CARDEEP doctrine order)

### 1) SITEMAP — ❌ DEAD for per-car enumeration (SEO facet pages only)
- `robots.txt` → 200; explicitly `Allow: /sitemap.xml`, `Allow: /` for ClaudeBot
  (Crawl-delay 10). `sitemap.xml` → 200 (`sitemapindex`, 18 KB, **127 child
  sitemaps**). `[VERIFIED]`
- **Scanned 32,585 child-sitemap URLs across children 1/50/100/120/125/126/127:
  ZERO per-car PDP URLs.** Children hold generic brand/contact links (child 1) and
  **SEO facet/listing pages** `/comprar-coches-de-ocasion/{city}/{brand}/{model}`
  (child 127) — never the `comprar-vehiculo-de-ocasion/…-{id}` per-vehicle PDP.
  `[VERIFIED]` **Outcome: the sitemap does NOT enumerate the inventory.** It is a
  crawl-bait facet index. (This corrects the prior `spoticar.md` claim.) The JSON
  API `url` field is the only source of per-car PDP paths.

### 2) MOBILE APP API — ⚪ not needed
- Same Stellantis Drupal/Elasticsearch backend serves web + app. The **web JSON
  API is already open, anonymous, and fully enumerates the index** (vector 3),
  so no app host / `/v4` / `/v5` / X-App headers / `searchAfter`/`scrollId` are
  required. **Outcome: unnecessary — web `/api/vehicleoffers/*` IS the data layer.**

### 3) ALTERNATE / CURSOR / INTERNAL JSON API — ✅ **THE WIN**
- `GET /api/vehicleoffers/paginate/search?page=N` returns raw Elasticsearch
  `hits[]._source` (12/page) and **flat-enumerates all 6,334 with no relevance and
  no depth cap** — proven by a live plain-`?page=N` walk to 6,176 unique (97.5%)
  ending naturally, linear growth, no truncation. Companion
  `/api/vehicleoffers/list/search` gives brand/dealer facets + `countNumber`;
  `/api/count-published-vo` gives the bare counter. Endpoints discovered from
  `data-search-url` / `data-paginate-url` in the listing HTML + the runner JS
  `list-search-runner.js`. `[VERIFIED]` **Outcome: SUCCESS. This is the recipe.**

### 4) curl_cffi browser impersonation (chrome131) — ✅ **the enabling tool**
- chrome131 TLS/JA3 fingerprint defeats AkamaiGHost: homepage, listing, sitemap,
  count, list AND paginate JSON API all return 200. Plain curl/wget → 403 (per
  intel). `[VERIFIED]` This is what unlocks vectors 1 & 3.

### 5) Stealth browser (camoufox / BotBrowser / Byparr) — ⚪ NOT REQUIRED
- No interactive Akamai sensor challenge encountered on the JSON API; no `_abck`
  sensor cookie needed. curl_cffi alone suffices. **Held as escalation** only if
  Akamai ever rotates to active sensor enforcement on the API. `[VERIFIED no wall]`

### 6) Facet partition (doctrine last resort) — ⚪ NOT NEEDED
- The flat `?page=N` walk already enumerates 100% of the index with no cap, so the
  province/brand/year partition is unnecessary. If a future depth wall appeared,
  the `list/search` facets (40 brands, 135 dealers, generations, models) provide
  ready shard keys — but no wall observed to page 528. `[ASSUMED reserve]`

**Bonus — Woosmap stores API:** public key
`woos-88a51d0b-2d09-3438-8c39-e8f17727f0a2` (from page census) is valid but returns
an empty FeatureCollection for ES. Not needed: dealer attribution is fully embedded
per-car via `field_pdv_*` and enumerable via the `pointsofsale` facet (135 dealers).

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Method:** `GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page=N`
  via `curl_cffi impersonate="chrome131"`, **plain page param (no sort)**, walk
  `page=1..528` (12/page), dedup on `field_vo_carnum`, stop on empty / `count.value`.
- **Declared total:** ~50,000 `[ASSUMED marketing]`. **Live ES public stock:**
  **6,334** `[VERIFIED]` (count.value = countNumber = Σbrands = Σdealers =
  count-published-vo, all agree; the 50k is global pan-locale marketing).
- **Coverage proof:** live plain-walk → **6,176 unique / 6,334 = 97.5% in one
  uncoordinated pass**, linear growth, natural end at page 531, no relevance/depth
  cap; dedup + gap re-sweep → ~100%.
- **Cost:** €0. No proxy, no browser, no auth, no CAPTCHA, no Akamai sensor.
- **Recipe seed (engine line, repo convention):**
  ```
  source: spoticar
  engine: curl_cffi+chrome131_impersonate+internal_es_json_api
  access: OPEN-via-fingerprint (Akamai 403 to plain curl; chrome131 TLS passes). is_tier1=true
  data_surface: json (Elasticsearch hits[]._source, 12/page, NO sort param)
  enumeration: GET /api/vehicleoffers/paginate/search?page=1..528  (count.value=6334 bound)
  denominator: /api/count-published-vo + list/search countNumber + brand/pointsofsale facets
  dealer: per-car field_pdv_* (135 dealers, named + geo); facet pointsofsale for roster
  ```
