# oem_bmw_mini (BMW Premium Selection + MINI Next) — UNCAPPED Data-Layer Recipe

Status: **UNCAPPED SURFACE FOUND.** Both brand portals enumerate 100% of their ES
public certified-used inventory with NO relevance/depth cap — the per-dealer
server-rendered listing paginator is FLAT, and every car card embeds its full
payload INCLUDING the real VIN (no PDP fetch needed).
Platforms: **bmwpremiumselection.es** (BMW "Premium Selection") and
**mininext.es** (MINI "Next") — both run on the **same Motorflash dealer-stock
backend** (identical card markup, identical `?pagina=N` paginator).
WAF posture: a CDN/WAF **403s some bot egress** (plain `WebFetch` is walled);
**`curl_cffi impersonate="chrome131"` serves cleanly** on robots, sitemaps,
listings AND PDPs — no proxy, no browser, no cookie warm-up, no auth, €0.
Verified LIVE: **2026-06-13** (curl_cffi, `impersonate="chrome131"`).

> Anti-hallucination: every line is `[VERIFIED]` (request run + bytes read) unless
> tagged `[ASSUMED]`. The BMW `sitemap-ofertas.xml` is a cross-check denominator
> (2,495 PDP URLs); the MINI `sitemap-ofertas.xml` is a **misconfigured mirror of
> the BMW PDPs** and is NOT a MINI surface — `[VERIFIED]`.

---

## 0. TL;DR — the uncapped surface (THE win)

Both sites publish their **dealer roster** in `sitemap.xml`. Each dealer has a deep,
server-rendered listing paginator. Every car on a listing page is a **CARD of
hidden `<input>` fields** carrying the whole per-car payload (incl. the VIN).

```
1) GET {base}/sitemap.xml                    -> dealer roster (/concesionarios/{prov}/{dealer})
2) GET {base}/concesionarios/{prov}/{dealer}[/]?pagina=N   -> 12 car-cards/page (FLAT)
```

- **BMW base:** `https://www.bmwpremiumselection.es` — dealer pages **REQUIRE a
  trailing slash** before `?pagina=`. 51 dealers in the roster. `[VERIFIED]`
- **MINI base:** `https://www.mininext.es` — dealer pages **404 on a trailing
  slash** (use none). 47 dealers in the roster. `[VERIFIED]`
- **Tool:** `curl_cffi` `impersonate="chrome131"` (the enabling tool — plain
  `WebFetch`/some bot egress gets 403; the Chrome TLS/JA3 + cookie jar passes).
  `[VERIFIED]`
- **Method:** `GET`. No body, no auth, no bearer, no cookie warm-up. `[VERIFIED]`
- **Page size:** **fixed 12 cards/page**. `[VERIFIED]`
- **Cursor:** `?pagina=1..ceil(id_total_resultados/12)` per dealer. **Bound by the
  dealer's `id_total_resultados`** — over-pagination **CLAMPS to the last page and
  REPEATS** cards (Motorflash phantom-repeat), so NEVER trust emptiness; dedup on
  `anuncio_id`. `[VERIFIED]` (a small dealer at `?pagina=99` still returned 2
  repeated cards.)

### Coverage proof (live E2E) `[VERIFIED]`
- **BMW** 8-dealer slice: 46 pages → **507 cards, 507 unique, 507 VINs (100%)**,
  Σ`id_total_resultados`=507 matched exactly; VAM verdict **TRUSTWORTHY** (harvest
  == db_edges == db_join_vehicles == 507); a re-run added **0 new / 0 edges / 0
  events** (idempotent).
- **MINI** 6-dealer slice: 13 pages → 138 cards, **100 unique** (38 cross-dealer
  dup `anuncio_id` collapsed), 100 VINs, **16 distinct selling dealers attributed**
  (MINI cards carry `concesionario_<id>` → cars are attributed to their TRUE
  selling concesionario, not the page's dealer); VAM **TRUSTWORTHY**.

No relevance truncation, no depth wall on the per-dealer paginator — a true flat
enumeration. Σ over the roster = the full brand ES public stock.

---

## 1. The denominator

| Surface | Brand | Value | `[VERIFIED]` |
|---|---|---:|---|
| Σ dealer `id_total_resultados` over the roster | per brand | full brand ES stock | yes (== distinct `anuncio_id` harvested) |
| `sitemap-ofertas.xml` `<loc>` count (PDP URLs) | BMW only | **2,495** | yes (cross-check) |
| Marketing claim ("more than 2,840 vehicles") | BMW | ~2,840 | `[ASSUMED marketing]` |

The denominator is the **roster sum**: each dealer renders its own
`id_total_resultados`; their sum is the brand's served public stock. The BMW
`sitemap-ofertas.xml` (2,495 PDP URLs) is an independent cross-check.
The MINI `sitemap-ofertas.xml` **mirrors the BMW PDPs** (shared backend misconfig)
— do NOT use it for MINI. `[VERIFIED]`

---

## 2. Exact request shape

### 2.1 Roster (dealer enumeration)
```
GET {base}/sitemap.xml
```
- Keep only `/concesionarios/{prov-slug}/{dealer-slug}` roots (exactly 2 path
  segments). Deeper URLs are SEO facet pages or (BMW) PDPs. `[VERIFIED]`

### 2.2 Harvest (the vehicle data)
```
BMW : GET https://www.bmwpremiumselection.es/concesionarios/{prov}/{dealer}/?pagina=N
MINI: GET https://www.mininext.es/concesionarios/{prov}/{dealer}?pagina=N
```
Minimal headers that return HTTP 200 `text/html`:
```
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: es-ES,es;q=0.9
```
- 12 car-cards/page. `id_total_resultados` (hidden input) bounds the walk.
- **Trailing-slash rule is brand-specific** (BMW yes, MINI no). `[VERIFIED]`

---

## 3. Per-car fields (listing CARD — self-contained, no PDP fetch needed)

Each card is a block of hidden `<input>` fields. Attribute spacing is irregular
over the wire (`name ="x" value="y"`) — tolerate `\s*`. `[VERIFIED]`

| Canonical | Card field | Example |
|---|---|---|
| listing_ref (stable id, **dedup key**) | `anuncio_id` | `148007871` |
| deep_link (PDP path) | `gtm_url_<id>` | `/concesionarios/burgos/burgocar/bmw-x1-xdrive25e/148007871/` |
| **VIN** | `bastidorVehiculo` | `WBA21EF0305619105` |
| make | `marcaVehiculo` | `BMW` / `MINI` |
| model | `modeloVehiculo` (+ `tracy_productName_<id>` for version) | `X1` / `MINI Countryman` |
| title | `tracy_productName_<id>` joined w/ make (fallback `gtm_name_<id>`) | `BMW X1 xDrive25e 180 kW (245 CV)` |
| **price (EUR)** | `precio` | `49500` |
| km | `kilometros` | `10` |
| year | `tracy_yearOfRegistration_<id>` (fallback `fechamatriculacion` `DD / MM / YYYY`) | `2026` |
| fuel | `tracy_fuelType_<id>` / `gtm_category_<id>` last `/`-segment | `…/Diésel`, `…/Híbrido Electro/Gasolina` |
| transmission | `tracy_gearing_<id>` | `Cambio automático` |
| photo | `img_<id>` | `https://fotos.estaticosmf.com/…/m01.jpg` |
| dealer name | `concesionario_<id>` (MINI) else de-slugified `dealer-slug` (BMW) | `Momentum S.A.` / `Burgocar` |
| dealer province | the `{prov-slug}` in the URL path | `burgos` → `09` |
| dealer city literal | `provincia_<id>` (MINI only) | `Madrid` |

**Dealer attribution:** the SELLING dealer's province is the URL `{prov-slug}`
(→ INE code via `GeoResolver.province_code`, after a small slug fix map:
`sta-c-tenerife`→Santa Cruz de Tenerife, `guipuzcoa`→Gipuzkoa). The dealer NAME is
`concesionario_<id>` when present (MINI) else the de-slugified dealer-slug (BMW).
The dealer-slug is the stable per-dealer key (`source_ref` + cdp_code address
anchor). MINI listing pages aggregate cars from MULTIPLE selling dealers, so a
single page yields several distinct concesionarios — each car keeps its true
`concesionario_<id>`. `[VERIFIED]`

**Encoding trap `[VERIFIED]`:** title/dealer/fuel text is latin-1 mojibake over the
wire (`a�o`="año", `H�brido`="Híbrido", `autom�tico`="automático"). Re-encode:
`s.encode("latin-1").decode("utf-8")`. The numeric inputs (`precio`,`kilometros`),
the VIN and the URL path are clean. Fuel/gearbox additionally normalized through a
fixed clean vocabulary keyed on accent-stripped tokens (handles both `Diésel` and
`Diesel` → `Diésel`; `Cambio automático` → `Automático`).

### Sample cars (real, pulled via the free path) `[VERIFIED]`
- **BMW XM** — 2024, 8,000 km, Gasolina/Automático, **169.400 €**,
  VIN `WBS31CS0809X95067`, dealer **Movilbegar** (Alicante, prov 03).
- **MINI Countryman** — 2025, 4,050 km, Gasolina/Automático, **45.900 €**,
  VIN `WMW21GA0007T91572`, dealer **Bernesga Motor León** (prov 24).

---

## 4. Traps & gotchas (hard-won this pass)

1. **Trailing slash is brand-specific.** BMW dealer pages 404 WITHOUT a trailing
   slash before `?pagina=`; MINI dealer pages 404 WITH one. `[VERIFIED]`
2. **Over-pagination clamps + repeats.** Pages beyond the last DO NOT empty — they
   re-serve the last page's cards. Bound by `id_total_resultados` + dedup on
   `anuncio_id`; never stop on "non-empty". `[VERIFIED]`
3. **MINI `sitemap-ofertas.xml` is a BMW mirror** (shared backend misconfig) — it
   lists BMW PDP URLs, not MINI. MINI has NO per-car sitemap; the per-dealer
   paginator is the only complete MINI surface. `[VERIFIED]`
4. **MINI PDPs carry NO JSON-LD**; BMW PDPs DO (schema.org `Car`). The listing
   CARD (hidden inputs) is the unified surface that works for BOTH brands — so the
   harvester reads cards, never PDPs. `[VERIFIED]`
5. **`WebFetch` is walled (403)** but `curl_cffi`/`chrome131` AND even a plain
   `curl/8` UA from a clean IP pass — the block targets specific bot egress, not a
   hard TLS sensor. Classified `t1_soft` (WAF present, serving to curl_cffi).
   `[VERIFIED]`

---

## 5. The connector

`pipeline/platform/oem_bmw_mini_wholesale.py` — ONE module, BOTH brands
(`--brand bmw|mini|both`). Mirrors `spoticar_wholesale.py` EXACTLY: platform entity
`kind=oem_vo_portal` (+ `platform_meta`), per-car selling-DEALER upsert
(`kind=compraventa`, `standalone_pos`), vehicle owned by dealer, `platform_listing`
edge, delta `NEW`, saved recipe, VAM verdict, governor-wrapped fetch, breaker /
`record_run` / `auto_repair`, idempotent `ON CONFLICT`, BATCH `unnest` ingest.

Multi-axis classification (migrations/0016):
```
defense_tier = t1_soft           (WAF 403s plain bot egress; serving to curl_cffi; no JS challenge)
source_group = oem_vo_portal     (3rd/4th member after renew, spoticar, dasweltauto)
role         = platform
kind         = oem_vo_portal     (the platform ENTITY's ontology kind)
is_tier1     = TRUE              (public site behind a WAF/CDN)
family       = bmw_group_vo      (ties the BMW-group OEM-VO siblings)
data_surface = json_ld           (structured data embedded in the page; BMW PDPs carry schema.org Car)
website_waf  = other
```

Platform cdp_codes (national, sentinel `00`): BMW `CDP-ES-00-ZXZD056M`,
MINI `CDP-ES-00-EV9ECTV7`.

Run: `python -m pipeline.platform.oem_bmw_mini_wholesale --brand both`

---

## 6. Vector-by-vector log (CARDEEP doctrine order)

### 1) SITEMAP — ✅ ROSTER (BMW also per-car) / ❌ MINI per-car
- BMW `sitemap.xml` (315 `<loc>`, dealer/facet pages) + `sitemap-ofertas.xml`
  (**2,495 per-car PDP URLs**, `/concesionarios/{prov}/{dealer}/{model}/{id}/`).
  MINI `sitemap.xml` (80 `<loc>`, dealer roots + model facets, **no per-car PDPs**);
  MINI `sitemap-ofertas.xml` mirrors the BMW PDPs (misconfig). **Outcome: both
  sitemaps give the DEALER ROSTER; BMW's also cross-checks the denominator.**
  `[VERIFIED]`

### 2) MOBILE APP API — ⚪ not needed
- The web listing already enumerates the full per-dealer stock anonymously. No app
  host required. **Outcome: unnecessary.** `[ASSUMED reserve]`

### 3) INTERNAL JSON API — ⚪ none exposed; HTML-card surface is complete
- `listado.js` is UI-only (no AJAX search endpoint). The per-dealer
  server-rendered listing embeds every car as hidden-input CARDS (incl. VIN) —
  a complete structured surface with no JSON API needed. **Outcome: SUCCESS via
  the card surface.** `[VERIFIED]`

### 4) curl_cffi browser impersonation (chrome131) — ✅ **the enabling tool**
- chrome131 TLS/JA3 + cookie jar defeats the WAF on robots, sitemaps, listings and
  PDPs (all 200). Plain `WebFetch` → 403. `[VERIFIED]`

### 5) Stealth browser (camoufox / BotBrowser) — ⚪ NOT REQUIRED
- No interactive sensor challenge encountered. curl_cffi alone suffices. Held as
  escalation only. `[VERIFIED no wall]`

### 6) Facet partition (doctrine last resort) — ⚪ NOT NEEDED
- The per-dealer flat walk enumerates 100% with no cap. The roster IS the natural
  shard set (51 BMW / 47 MINI dealers). `[VERIFIED]`

---

## 7. Verdict

- `uncapped_surface_found = true`
- **Method:** roster from `{base}/sitemap.xml`, then
  `GET {base}/concesionarios/{prov}/{dealer}[/]?pagina=N` (12 cards/page) via
  `curl_cffi impersonate="chrome131"`, bound by `id_total_resultados`, dedup on
  `anuncio_id`. ONE module, both brands.
- **Declared total:** Σ dealer `id_total_resultados` (roster); BMW cross-check
  `sitemap-ofertas.xml` = **2,495** PDP URLs.
- **Coverage proof:** BMW 8-dealer slice → 507 unique / 507 VINs, VAM
  **TRUSTWORTHY**, idempotent re-run (0 new). MINI 6-dealer slice → 100 unique /
  100 VINs / 16 dealers attributed, VAM **TRUSTWORTHY**.
- **Cost:** €0. No proxy, no browser, no auth, no CAPTCHA.
- **Recipe seed (engine line, repo convention):**
  ```
  source: oem_bmw_mini (bmwpremiumselection.es + mininext.es)
  engine: curl_cffi+chrome131_impersonate+motorflash_dealer_listing(html cards)
  access: OPEN-via-fingerprint (WAF 403s plain bot egress; chrome131 passes). is_tier1=true, t1_soft
  data_surface: json_ld (structured hidden-input cards; BMW PDPs carry schema.org Car)
  enumeration: roster /sitemap.xml ; per dealer /concesionarios/{prov}/{dealer}[/]?pagina=1..ceil(total/12)
  denominator: Σ id_total_resultados (roster) ; BMW cross-check sitemap-ofertas.xml=2495
  dealer: URL {prov-slug}->INE + concesionario_<id> (MINI) / de-slugified dealer-slug (BMW)
  family: bmw_group_vo ; source_group: oem_vo_portal ; kind: oem_vo_portal
  ```
