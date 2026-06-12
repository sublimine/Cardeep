# Wallapop — Inventory Segment Enumeration (READ-ONLY audit)

> Mission: enumerate EVERY inventory segment wallapop exposes for cars and its
> PUBLISHED count, so we know the true 100% per platform and whether the existing
> connector (`pipeline/platform/wallapop_wholesale.py`) drains all of it — the way
> coches.com was caught draining only VO and missing the vn.xml NEW segment.
>
> Probed LIVE 2026-06-13 with curl_cffi chrome131 against
> `GET https://api.wallapop.com/api/v3/search/section` (no proxy, no auth).
> Every count is the server's own `meta.next_page` JWT
> `pointers.ORGANIC.remaining_documents` (= live catalog denominator behind the
> cursor). `[VERIFIED]` unless tagged `[ASSUMED]`.

---

## 0. TL;DR — the segmentation verdict

**Wallapop has NO new-car (VN) catalog, NO km0 vertical, and NO renting vertical.**
It is a single generalist C2C + PRO classifieds cars vertical (`category_id=100`).
There is no coches.com-style hidden `vn.xml` NEW segment to miss here — the
analogue does not exist. The only real partitions the API exposes are:

| Axis | param | partition counts (live) |
|---|---|---|
| **Seller type** | `seller_type` | professional **345,836** + private **305,323** ≈ 651k total |
| **Mileage** | `min_km` / `max_km` | continuous range filter (km≤100 ≈ 4,937; km≤5,000 ≈ 20,686) |
| **Year** | `min_year` / `max_year` | continuous range filter (≥2025 ≈ 29,936; ≥2026 ≈ 3,350) |
| **Warranty** | `has_warranty` | 289,739 (a dealer/quality signal, not a condition segment) |

**Total live ES cars (category 100): ≈ 651,199** (server `remaining_documents`,
geo-independent; the ~750k marketing figure includes non-current/other-locale).

"New / km0" is **not a hard facet** — it is expressed only as `max_km`/`min_year`
ranges. `condition=new`, `is_new=true`, `car_status=new`, `vehicle_status=new`,
`new=true` are ALL silently ignored (return the full 651,199). `[VERIFIED]`

**Connector coverage: COMPLETE by construction.** The connector's enumeration is
`order_by=newest` over `category_id=100` with NO segment filter, walking the flat
`next_page` cursor across the WHOLE catalog (all sellers, all km/year). Therefore it
covers professional + private + every km/year band in one sweep — it does NOT
exclude a new/km0 segment. The DB currently holds ~81k of 651k cars: that is a
**drain-DEPTH** shortfall (the cursor was not walked to remaining→0), NOT a
segment-exclusion gap. There is no missing selector to add.

---

## 1. Robots / sitemap surface

- `es.wallapop.com/robots.txt` → 200, **NO `Sitemap:` directive**. Bot blocklist +
  `User-agent: *  Allow: /` with `Disallow: /search /login /register /auth/ /app/
  /wallapay /faq ...`. No XML sitemap exists (corroborates
  `wallapop_datalayer.md` §5.1, which probed 20 candidates → all 404 SPA HTML).
  `[VERIFIED]` — the sitemap is NOT a segment-enumeration surface.

---

## 2. Segment-by-segment live probe

All probes: base = `category_id=100 & order_by=newest &
section_type=organic_search_results` at Madrid centroid; read
`remaining_documents`. Baseline (no filter) = **651,199**. `[VERIFIED]`

### 2.1 Seller-type axis — REAL, CLEAN partition
| selector | remaining | note |
|---|---:|---|
| `seller_type=professional` | **345,836** | PRO dealers (compraventa) |
| `seller_type=private` | **305,323** | private individuals (particular) |
| sum | 651,159 | ≈ baseline 651,199 (±live jitter) → clean 2-way split |
| `type_of_seller=...` | ignored (651,199) | wrong param name |
| `is_professional=true` | ignored (651,199) | wrong param name |
| `seller_type=normal` | HTTP 400 | only `professional`/`private` accepted |

→ This is the dealer/new analogue the mission asks about: **wallapop DOES have a
pro-dealer segment (345,836), and the connector already harvests it** (PRO sellers
become `compraventa` entities via `GET /users/{id}` type=professional).

### 2.2 Mileage axis — `min_km`/`max_km` (continuous; the only "new/km0" proxy)
| selector | remaining |
|---|---:|
| `max_km=0` | 2,197 |
| `min_km=0 & max_km=0` | 2,194 |
| `max_km=0 & min_year=2024` | 678 (true km0: 0 km + recent reg) |
| `min_km=1 & max_km=100` | 4,647 |
| `max_km=10` | 4,937 |
| `max_km=1000` | 17,223 |
| `max_km=5000` | 20,686 |
| `max_km=20000` | 47,566 |

→ "km0 / nearly-new" ≈ **2,197 at 0 km, ~4,937 at ≤10 km, ~20,686 at ≤5,000 km**.
No discrete km0 vertical — it is a slice of the same catalog the cursor already
walks.

### 2.3 Year axis — `min_year`/`max_year` (continuous)
| selector | remaining |
|---|---:|
| `min_year=2025` | 29,936 |
| `min_year=2026` | 3,350 |

→ "new model-year" ≈ 29,936 (2025+) / 3,350 (2026). A slice, not a segment.

### 2.4 Intersections (sanity)
| selector | remaining |
|---|---:|
| `seller_type=professional & max_km=100` | 3,861 (dealer km0-ish) |
| `seller_type=professional & min_year=2025` | 26,051 (dealer recent) |
| `seller_type=private & max_km=100` | 2,983 (private km0-ish) |

### 2.5 Facets that DO NOT exist (silently ignored → full 651,199)
`condition=new`, `condition=used` (400), `status=new`, `car_condition=new`,
`car_status=new|used`, `vehicle_status=new`, `is_new=true`, `new=true`,
`is_refurbished=true`, `financed=true`, `object_type_ids=100`. `subcategory_ids=`
and `seller_type=normal` → HTTP 400 (param exists but value rejected).

→ **No VN catalog, no km0 vertical, no renting vertical.** The mission's hypothesis
("wallapop has pro dealers → is there a dealer/new segment?") resolves to: the
dealer segment exists (§2.1) and is already covered; a separate NEW segment does
NOT exist on this platform.

### 2.6 Warranty (quality signal, not a segment)
`has_warranty=true` → 289,739. Mostly dealer stock with a warranty flag; overlaps
both seller types. Not an inventory segment, recorded for completeness.

---

## 3. Connector coverage map

`pipeline/platform/wallapop_wholesale.py` enumeration (per code + recipe
`wallapop_datalayer.md`): `category_id=100` + `order_by=newest` +
`section_type=organic_search_results`, **NO seller/km/year filter**, paginate the
flat `next_page` JWT cursor. Every item carries `user_id` → `GET /users/{id}`
splits professional (→ compraventa) vs private (→ per-seller particular).

| Segment | published (live) | connector covers? | how |
|---|---:|---|---|
| Whole cars vertical (cat 100) | **651,199** | YES | flat `order_by=newest` cursor walks the entire catalog |
| Professional / dealer (VO+all) | 345,836 | YES | `users/{id}` type=professional → compraventa entity |
| Private (C2C) | 305,323 | YES | type=normal → per-seller particular entity |
| km0 / 0-km slice | ~2,197 (≤10 km ~4,937) | YES (incidental) | inside the unfiltered cursor; no special handling |
| New model-year (2025+) | ~29,936 | YES (incidental) | inside the unfiltered cursor |
| New-car (VN) catalog | **does not exist** | N/A | wallapop has no VN vertical |
| Renting vertical | **does not exist** | N/A | `subcategory_ids=renting` → 400 |

**Currently in DB:** 81,142 platform_listing edges (compraventa 36,227 +
garaje-legacy 22,900 + particular 22,015). vs 651,199 live = ~12.5% depth. The
shortfall is cursor DEPTH (run target ~8k/chunk, not walked to remaining→0), not a
skipped segment. The 22,900 `garaje` legacy-bucket cars are mid-migration to
per-seller `particular` (connector `cleanup_legacy_buckets`).

---

## 4. Verdict

- `segments_complete = true` (every exposed axis enumerated)
- **No coches.com-style gap exists on wallapop.** There is no separate NEW/VN
  segment, km0 vertical, or renting vertical to miss; the dealer (professional)
  segment exists and is already drained.
- **Real total = 651,199** ES cars (category 100), 2-way seller split
  345,836 PRO / 305,323 private.
- **Gap to close is depth, not coverage:** walk the existing `order_by=newest`
  cursor to `remaining_documents → 0` to reach 100% (≈651k), which the connector's
  enumeration already targets without any new selector.
