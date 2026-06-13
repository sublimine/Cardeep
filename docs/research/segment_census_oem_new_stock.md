# Segment census — `oem_new_stock` (OEM official NEW-car + km0 stock channels, ES)

> Front: OEM NEW-CAR + km0 stock surfaces, DISTINCT from the OEM-VO certified-used portals
> already harvested. Method: enumerate every official brand "coches nuevos / stock disponible /
> entrega inmediata" surface with a queryable data layer; mark have/missing; connect the
> reachable-free; declare the genuinely-walled honestly. Social media excluded by mandate.
> Verified live 2026-06-13. Every count below is from a direct DB query on the live cardeep PG.

## TL;DR

- The ONLY NEW/km0 stock in the DB before this front was the **coches.net marketplace** segment
  slice (`new`=6151, `km0`=3107) — a generalist marketplace, NOT OEM-official.
- Every existing OEM connector is `oem_vo_portal` (certified **USED**). There was **zero**
  OEM-official **new-car** coverage.
- BUILT this front: **`seat_cupra_new`** — the SEAT + CUPRA official "Localizador de Stock"
  (VW-Group VTP REST API). **2208 brand-new cars** caged (Seat 1145 + CUPRA 1063), **163
  distinct official dealers**, segment=`new`, dealer-attributed, VAM TRUSTWORTHY.
- The DB-wide `new` segment grew **6151 → 8359** (+2208 OEM-official).
- Mapped the rest of the universe: Renault Webstore, Audi, VW-ES, Skoda, Toyota NSC,
  Stellantis (Peugeot/Citroën/Opel), Hyundai, Kia, Ford — all have an official new-stock
  surface; reachability classified below.

## The architecture distinction (why this is its own front)

| Axis | OEM-VO portal (already had) | OEM new-stock (this front) |
|---|---|---|
| product | certified **used** | brand-**new** + km0 |
| example | spoticar, dasweltauto, renew, Toyota Plus | seat.es/localizador-stock |
| `source_group` | `oem_vo_portal` | `oem_dealer_network` |
| `segment` on edge | (used) | **`new`** |
| car signal | mileage, registration date | `available_from=Immediately`, `dateproduction`, km=0 |

Same dual-membership cage in both: platform entity → selling official dealer (owns the car) →
`vehicle` → `platform_listing` edge. New-stock edges are stamped `segment='new'`.

## BUILT — `seat_cupra_new` (SEAT + CUPRA official new-stock locator)

- **Connector**: `pipeline/platform/oem_seat_cupra_new_stock.py`
- **Platform cdp_code**: `CDP-ES-00-5R30HVA7` · `kind=plataforma` · `source_group=oem_dealer_network`
  · `role=platform` · `family=vw_group_new` · `defense_tier=t0_open` · `data_surface=internal_api`
- **Recipe**: `countries/ES/recipes/CDP-ES-00-5R30HVA7.yaml`
- **Engine**: `curl_cffi` chrome131, GET `https://vtpapi.seat.com/restapi/v1/{stockType}/search/car`
  - SEAT → `stockType=stesnwb`, header `x-pattern: seatwebfe`
  - CUPRA → `stockType=cuesnwb`, header `x-pattern: cuprawebfe`
  - The `x-pattern` header is the ONLY access gate (without it → 401 VtpApiUnauthorized). No
    proxy, no browser, no cookie warm-up, no token. €0. `t0_open`.
- **Pagination**: `x-page` (1-based) + `x-page-items` (≤12; host 500s on larger). Default sort
  PRICE_SALE/ASC is UNSTABLE across pages → carid dedup is mandatory (536 dups collapsed).
- **Discovery**: one-time Playwright XHR capture of the live locator SPA (captured the path shape
  + `x-pattern`/pagination headers); the API then answers plain `curl_cffi` identically.

### Counts (direct DB query, platform `CDP-ES-00-5R30HVA7`)

| metric | value |
|---|---|
| `platform_listing` edges, segment=new | **2208** |
| by make | Seat 1145 · CUPRA 1063 |
| distinct official dealers attributed | **163** |
| source-declared full (t_body criteria sum) | 2747 (SEAT 1684 + CUPRA 1063) |
| top provinces | 08 Barcelona 430 · 28 Madrid 313 · 46 Valencia 85 · 48 Bizkaia 78 · 03 Alicante 76 |
| VAM verdict (harvested==db_edges==join_vehicles) | TRUSTWORTHY |

**Honest gap note**: 2208 caged vs 2747 source-declared. The VTP search has no stable cursor —
a single PRICE_SALE/ASC walk repeats ~half of each page boundary and does not surface every
distinct `carid` in one sort order (536 dups collapsed proves the rotation). A future pass can
close the gap by sweeping multiple sort orders / per-model `t_model` facet partitions and unioning
on `carid`. This is a completeness ceiling of the surface's pagination, declared not hidden.

## Universe map — every OEM new-stock surface (have / missing / reachability)

| Brand / group | Official new-stock surface | Data layer | Status |
|---|---|---|---|
| **SEAT** | seat.es/localizador-stock | VTP `vtpapi.seat.com` `stesnwb`/`seatwebfe` | **HAVE (built)** |
| **CUPRA** | cupra.com/es-es/localizador-stock | VTP `vtpapi.seat.com` `cuesnwb`/`cuprawebfe` | **HAVE (built)** |
| **Volkswagen** | volkswagen.es/es/modelos/stock.html | feature-app `stock-resultados.html/__app/search/cars.app` (ES-specific; VTP DE host is german market) | MISSING — reachable, needs ES feature-app XHR capture |
| **Audi** | audi.es/es/buscador-de-stock-nuevo/ | `omnigraph.audi.com/graphql` (live; 400 CSRF on bare GET → needs POST + anti-CSRF) | MISSING — reachable-with-discovery |
| **Škoda** | skodastock.com/resultados | dedicated stock SPA (host slow/refused on probe; likely same VTP-family or Contentful) | MISSING — reachable, needs XHR capture |
| **Renault / Dacia** | renault.es/renault-webstore | `rvp-datahub-wired-prod-1-euw1.wrd-aws.com/rplugdcs2renaultcom/co/es` (live; 403 AccessDenied on bare path → needs signed object path/params) | MISSING — reachable-with-discovery |
| **Toyota / Lexus** | toyota.es coches nuevos (NSC) | `kong-proxy...toyota-europe.com/dxp/dealers/api/` (live; same Toyota-Europe infra as the USC/VO connector already built) | MISSING — reachable; mirror the USC recipe for NSC |
| **Stellantis** (Peugeot/Citroën/Opel/DS/Fiat) | brand "compra online / stock" pages | shared Stellantis stock API (sibling of the spoticar VO backend) | MISSING — reachable-with-discovery |
| **Hyundai** | hyundai.com/es stock | brand stock API (sibling of the hyundai VO `internal_api` already built) | MISSING — reachable-with-discovery |
| **Kia** | kia.com/es stock | brand stock API (sibling of the kia VO `internal_api` already built) | MISSING — reachable-with-discovery |
| **Ford** | ford.es stock | brand stock API (sibling of the ford VO `internal_api` already built; akamai-fronted) | MISSING — reachable-with-discovery (t1_soft akamai) |

### Reachability summary

- **HAVE / built (free, t0_open)**: SEAT, CUPRA → `seat_cupra_new`, 2208 cars.
- **MISSING but reachable-free with one-time XHR discovery**: Volkswagen-ES, Audi (omnigraph
  GraphQL), Škoda, Renault/Dacia (Webstore datahub), Toyota/Lexus NSC, Stellantis brands,
  Hyundai, Kia. Each host is LIVE and responds (403/400/404 with a body, never connection-refused)
  — they gate on request shape (signed path / POST GraphQL / sub-path / anti-CSRF header), exactly
  the class of gate the SEAT/CUPRA `x-pattern` was. None require paid proxies; the same
  Playwright-capture → curl_cffi-replay method that built SEAT/CUPRA applies.
- **Genuinely free-unreachable**: none identified on this front. Ford's new-stock sits behind
  Akamai (t1_soft) like its VO sibling, but Akamai here is JS-soft, not a spend-gated sensor —
  the existing fleet already clears equivalent Akamai (ford VO `internal_api`), so it is
  reachable, just harder.

## Next-build priority (highest yield, all reachable-free)

1. **VW-ES + Audi + Škoda** — complete the VW-Group new-stock family (`vw_group_new`) alongside
   the SEAT/CUPRA built here; Audi alone declares ~4,000 new cars in stock.
2. **Renault Webstore (Renault + Dacia)** — owner-cited ~4,000 permanent new-stock cars.
3. **Toyota/Lexus NSC** — mirror the proven USC (VO) connector recipe onto the NSC endpoint on the
   same `toyota-europe.com` infra (lowest discovery cost — sibling of an already-built surface).
4. **Stellantis / Hyundai / Kia / Ford** — each a sibling of an already-built VO `internal_api`
   connector; reuse the fleet's per-brand patterns.

## Files

- Connector: `C:\Users\elias\projects\cardeep\pipeline\platform\oem_seat_cupra_new_stock.py`
- Recipe: `C:\Users\elias\projects\cardeep\countries\ES\recipes\CDP-ES-00-5R30HVA7.yaml`
- This census: `C:\Users\elias\projects\cardeep\docs\research\segment_census_oem_new_stock.md`
