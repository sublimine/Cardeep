# coches.net — Segment Census (READ-ONLY audit)

> **Mandate.** CARDEEP doctrine: *"todo su inventario de coches"* = EVERY segment a
> platform exposes (usados/ocasión, NUEVOS, km0/seminuevos, renting/suscripción), not
> only the used pool. This file enumerates every inventory segment coches.net publishes,
> its PUBLISHED count, the URL/param that selects it, and whether the EXISTING connector
> (`pipeline/platform/coches_net_wholesale.py`) covers it.
>
> **Scope of this audit.** READ-ONLY. No harvest, no connector run, no DB write. Probed
> live with `curl_cffi chrome131` (a handful of GETs/POSTs) + WebSearch corroboration on
> 2026-06-13. Marking discipline: every count is **[VERIFIED]** (read live this session)
> or **[ASSUMED]** (inferred / vendor-stated, not re-derived).

---

## 0. TL;DR — the gap

The connector drains **100% of the USED (ocasión/segunda-mano) segment and 0% of every
other segment.** coches.net's open JSON gateway `POST web.gw.coches.net/search` is
**hardwired to the used-cars index** — it returns the same ~272.7k "Ocasión" set no
matter what filter is sent (`categoryId`, `offerTypeId`, `sellerTypeId`, `isCertified`,
`km`, `year`, `subscriptionVehicleState` are ALL ignored on this endpoint `[VERIFIED]`).
NEW, KM0/seminuevos and RENTING are **separate products on separate backends** that the
`/search` gateway does NOT serve, and for which no sibling open endpoint was found.

| Segment | Selector (web) | Published | Connector covers? |
|---|---|--:|:--:|
| **Used (ocasión / segunda-mano)** | `/segunda-mano/`, gateway `/search` | **272,720** `[VERIFIED live]` | ✅ YES (DB: 272,903 edges) |
| **New (coches nuevos)** | `/nuevo/` | ~6,089 `[VERIFIED via SRP/WebSearch]` | ❌ NO |
| **Km0 + seminuevos** | `/km-0/` | ~3,107 `[VERIFIED via SRP/WebSearch]` | ❌ NO |
| **New+Km0 combined surface** | `/nuevo/km-0/` | ~6,210 `[VERIFIED via SRP/WebSearch]` | ❌ NO |
| **Renting / suscripción** | `/renting/` | ~808 `[VERIFIED via SRP/WebSearch]` | ❌ NO |

**Honest true-100% per platform = used 272,720 + new/km0/renting ≈ 9–10k more.** The
used pool is by far the giant; the missing segments are ~3–4% of the platform by count,
but they are a *distinct kind of inventory* (dealer new-car catalog + renting) the mandate
explicitly requires.

---

## 1. robots.txt + sitemap (probe result)

- **robots.txt** `[VERIFIED]` — single sitemap index declared:
  `https://www.coches.net/servicios/sitemaps/sitemap-index.xml`.
  Disallows legacy `.aspx` search params (`?MakeId=`, `?MinPrice=`, `pg=7..69`), `/Detail/`,
  `/ws/`. **Allows** `/concesionarios/`, `/segunda-mano-garantia?certification=true`,
  `/fichas_tecnicas/comparador/`, `/seguros/`. No explicit disallow on `/nuevo/`, `/km-0/`,
  `/renting/` (they are crawlable product surfaces).
- **Sitemap index** `[VERIFIED]` — **Imperva-walled (HTTP 403)** to `curl_cffi` and
  WebFetch (405). The child sitemaps could not be enumerated without a browser/sensor.
  This is a **declared gap** for sitemap-based per-segment enumeration: the segment counts
  below come from the SRP product surfaces + the live gateway, NOT from the sitemap.
- The public HTML SRPs (`/nuevo/`, `/km-0/`, `/renting/`) return **HTTP 405 / Imperva
  interstitial** to `curl_cffi` GET `[VERIFIED]` — the published counts were read from the
  page titles/meta surfaced via WebSearch and the saved `data/___INITIAL_PROPS.json`.

---

## 2. The used-cars gateway is segment-locked (root cause of the gap)

`POST https://web.gw.coches.net/search` (tenant `coches`) is the ONLY open JSON endpoint
found. Probed live 2026-06-13:

- Default body → `meta.totalResults = 272,720` (all `offerType.literal = "Ocasión"`)
  `[VERIFIED]`.
- **Every filter is ignored** on this endpoint (total stays ~272,720 ± live drift)
  `[VERIFIED]`:
  - `categoryId` 1/2/100/1000/2000…3000 → identical 272,720.
  - `offerTypeId` 1..6, `sellerTypeId` 1..3, `isCertified=true`, `hasInstalment=true` →
    identical (even `isCertified` does not drop to the ~143,940 pro-warranty subset the
    SRP FAQ cites, proving the filter is inert here).
  - `km={to:1}`, `year={from:2026}`, `subscriptionVehicleState=new/km0` → identical.
  - Full Adevinta `initialSearch` schema (from `data/___INITIAL_PROPS.json`) with
    `offerTypeId`/`sellerTypeId`/`subscriptionVehicleState` set → still 272,720.
- **Sibling endpoints 404** `[VERIFIED]`: `/newcars/search`, `/new/search`, `/nuevo/search`,
  `/catalog/search`, `/models/search`, `/configurator/search`, `/renting/search`,
  `/subscription/search`, `/km0/search`, `/v1/search`, `/search/new` → all
  `404 "No static resource …"`. The gateway exposes only `/search`.
- **Alternate tenants rejected** `[VERIFIED]`: `coches-new`, `coches-nuevos`,
  `coches-renting`, `motor`, `cochesnet` → `HTTP 400 "Unsupported tenant code"`. Only
  `coches` is valid, and it maps to the used index.

**Conclusion:** the used-cars index and the new/km0/renting catalogs are different
backends. The open `/search` gateway cannot reach NEW/KM0/RENTING under any parameter,
tenant, or sibling path discovered in this audit. Reaching them needs a different recipe
(separate host/endpoint, likely behind Imperva on the SRP, or a `nuevo`/`renting` BFF not
exposed on `web.gw.coches.net`).

---

## 3. Per-segment detail

### SEG · Used — `offer_type=segunda-mano` (a.k.a. ocasión)
- **Selector.** Web `/segunda-mano/`; API `POST web.gw.coches.net/search`, tenant `coches`,
  `categoryId=2500` (the only param the connector sends; the gateway is anyway locked here).
- **Published.** `meta.totalResults = 272,720` live `[VERIFIED 2026-06-13]`.
  (SRP FAQ text in `___INITIAL_PROPS.json` cites 248,648 "publicados" / 249,351
  `initialResults.totalResults` — a snapshot lower bound; the live gateway is the truth.)
- **Internal splits (from SRP FAQ, used pool only) `[VERIFIED text]`:** ~143,940 pro ads,
  ~140,564 with ≥1yr warranty, avg price €19,685, avg year 2020, avg 71,255 km.
- **Connector coverage.** ✅ **YES — full.** `coches_net_wholesale.py` drains this set via
  nested `pagination` (no `sortBy` cap), dual-membership (dealer compraventa + per-province
  `particular` bucket). DB holds **272,903 `platform_listing` edges** `[VERIFIED DB]`
  (≈ live + accumulated cross-run drift). This segment is sealed.

### SEG · New — `coches nuevos`
- **Selector.** Web `/nuevo/`. No open API endpoint found (gateway 404s `/nuevo/search`).
- **Published.** ~**6,089** coches nuevos de concesionarios `[VERIFIED via SRP/WebSearch
  2026-06-13]`. (Province example: Madrid `/nuevo/km-0/madrid/` = 2,255.)
- **Nature.** Dealer new-car catalog (configured by make/model/trim/offer), not per-VIN
  used ads — a structurally different inventory surface.
- **Connector coverage.** ❌ **NO.** Not reachable on the used gateway; needs a separate
  `/nuevo/` recipe.

### SEG · Km0 + seminuevos
- **Selector.** Web `/km-0/`. No open API endpoint found.
- **Published.** ~**3,107** km0/seminuevos general `[VERIFIED via SRP/WebSearch]`.
  Province examples: Madrid `/km-0/madrid/` = 753, Barcelona `/km-0/barcelona/` = 693.
- **Combined new+km0 surface** `/nuevo/km-0/` = ~**6,210** `[VERIFIED]` (coches.net groups
  NEW and KM0 under one product path; avg power 207 CV, avg price €30,783).
- **Connector coverage.** ❌ **NO.**

### SEG · Renting / suscripción
- **Selector.** Web `/renting/`. API field `subscriptionVehicleState` exists in the search
  schema but is inert on the used gateway; no open renting endpoint found.
- **Published.** ~**808** vehicles `[VERIFIED via SRP/WebSearch]` (from €241/month;
  body types Sedan/Estate/Coupe/Minivan/SUV/Convertible/PickUp).
- **Connector coverage.** ❌ **NO.**

---

## 4. True-100% denominator for coches.net (this platform)

```
USED      272,720   ✅ covered (DB 272,903 edges)
NEW       ~6,089    ❌ gap
KM0       ~3,107    ❌ gap   (NEW+KM0 combined surface ~6,210)
RENTING   ~808      ❌ gap
--------------------------------------------------
TRUE TOTAL ≈ 282,700  (used + new + km0 + renting, de-overlap caveat below)
COVERED    272,720..272,903  → ~96.5% of platform by count, 0% of non-used kinds
```

**Overlap caveat `[ASSUMED]`:** `/nuevo/km-0/` (6,210) is a combined surface; adding
`/nuevo/` (6,089) + `/km-0/` (3,107) separately double-counts the km0∩new region. The
honest non-used residual is **~9–10k cars** across new+km0+renting. The exact union needs
the segmented SRPs (Imperva-walled this session) to deduplicate.

---

## 5. Recommended connector extension (NOT executed — audit only)

To close coches.net to true 100% per the mandate, the connector needs **three new
segment recipes**, each a distinct backend from the used gateway:
1. `/nuevo/` new-car catalog (~6,089) — find its BFF/endpoint (Imperva-fronted SRP).
2. `/km-0/` km0+seminuevos (~3,107 / combined ~6,210).
3. `/renting/` subscription (~808) — likely a separate Adevinta renting product.

None is reachable via `web.gw.coches.net/search`. Each is a separate recipe-hunt
(browser/sensor likely required for the Imperva-walled SRP, or a dedicated `nuevo`/
`renting` gateway host not exposed in this probe). Until then, the non-used segments are a
**declared, caused gap** (cause: separate backend, gateway segment-locked to used).

---

## 6. Evidence log (this session, 2026-06-13)

- DB: `platform_listing` edges for `entity.website='coches.net'` = **272,903** `[VERIFIED]`;
  `entity_source.source_key='coches_net_wholesale'` attributes 7,223 entities.
- Live gateway default `totalResults` = **272,720** (all "Ocasión") `[VERIFIED]`.
- Filter inertness on `/search`: `categoryId`/`offerTypeId`/`sellerTypeId`/`isCertified`/
  `km`/`year`/`subscriptionVehicleState` all → 272,720 `[VERIFIED]`.
- Gateway sibling new/renting endpoints → 404; alternate tenants → 400 `[VERIFIED]`.
- robots.txt sitemap index → 403 (Imperva); SRPs `/nuevo//km-0//renting/` → 405 to
  curl_cffi `[VERIFIED]`.
- Published non-used counts (new ~6,089 · km0 ~3,107 · new+km0 ~6,210 · renting ~808)
  `[VERIFIED via SRP page titles + WebSearch]`.
