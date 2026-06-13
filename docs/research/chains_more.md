# FRONT: chains_more — remaining big national USED-CAR CHAINS

Mission: connect the remaining large national used-car chains not yet in DB, extending the
proven `group_vo_chains_wholesale.py` architecture (source_group='chain'). Verified live
2026-06-13 via curl_cffi chrome131 + Playwright network capture.

## Already in DB (source_group='chain', kind='cadena') — DO NOT re-add
| Chain | cdp_code | edges (cars) in DB |
|-------|----------|--------------------|
| Flexicar | CDP-ES-00-FYECEGD5 | 23874 |
| OcasionPlus | CDP-ES-00-SWN09H0C | 13445 |

(+ 185 Flexicar branch entities kind='compraventa' under the chain.)

## NEW members added by this front
### 1. Clicars (clicars.com) — chain-as-owner, SSR HTML car cards
- Surface: Next/legacy SSR HTML. `GET https://www.clicars.com/coches-segunda-mano-ocasion?page=N`.
  Cloudflare in front but NO challenge → curl_cffi chrome131 serves 200 cleanly (t0_open).
- Pagination: `?page=N` server-side (page 2 returns different ids vs page 1). 12 cars/SSR page.
  `data-pages="125"`, `data-filter-num-rows="1494"` declares full stock = **1494** (995..2000 are marketing).
- Per-card data (the `<a class="analytics-list-click-car">` block):
  - listing_ref: `data-vehicle-web-id` (native stock id, also the deep-link tail).
  - deep_link: `href` → `/coches-segunda-mano-ocasion/comprar-<slug>-<id>`.
  - make: `data-analytics-vehicle-maker`; model: `data-analytics-vehicle-model`.
  - title/version: `<h2 class="maker"><strong>{make model}</strong><span class="version">{version}</span>`.
  - info span: `{year} | {km}km | {CV}CV | {Manual|Automático}`.
  - fuel: `<span class="fuelName">{Gasolina|Diésel|Híbrido|…}</span>`.
  - price: `data-price-web` (web price, EUR) — also `data-price-web-offer`, `data-amount-without-discount`.
  - photo: `<img class="vehicle-img" src=...>`.
- Owner model: CHAIN-AS-OWNER. The SRP does not attribute a car to a physical branch
  (Clicars is a Madrid-centric online retailer w/ delivery), so the chain entity owns every car.
- The `data.json.gz` (storage.googleapis.com/clicars-storage-prod-public/others/data.json.gz)
  is ONLY facet metadata (makers/fuels/bodies), NOT stock — confirmed via Playwright XHR capture.

### 2. Carplus (carplus.es) — chain-as-owner, SSR JSON-LD Vehicle blocks
- Surface: SSR HTML w/ schema.org JSON-LD. `GET https://www.carplus.es/coches-segunda-mano/?page=N`.
  No WAF, no CF challenge → curl_cffi chrome131 serves cleanly (t0_open).
- Pagination: `?page=N` server-side. 16 Vehicle JSON-LD blocks/page. Walked to boundary:
  pages 1..25 = 16 each, page 26 = 12, page 27+ = 0 → 25×16+12 = **412 cars** (the "1.000" is marketing).
- Per-Vehicle JSON-LD (one standalone `@type:Vehicle` script per car, NOT an ItemList):
  - name (make+model), brand.name (make), model, vehicleTransmission, fuelType,
    productionDate (ISO→year), mileageFromOdometer.value (km),
    offers.price (EUR), offers.url (deep-link), image.
  - listing_ref: deep-link tail = VIN. URL `…/coche/<slug>-<vin>/`; tail before final '/' is the VIN
    (e.g. `zfa3120000jb87370`) → stable native id.
- Owner model: CHAIN-AS-OWNER (the SRP does not attribute per-centro; chain owns every car).

## Investigated and REJECTED (with evidence)
- **Aurgi (aurgi.com)** — NOT a used-car chain. It is an auto-parts / accessories e-commerce +
  workshop chain ("centros-aurgi", batteries, oils, brakes, tyres). No `ocasion`/`coches segunda mano`/
  `vehiculos venta` section exists. 0 JSON-LD vehicle blocks. The task hypothesis was wrong. Excluded.
- **Automóviles Sánchez** — regional SEAT/CUPRA/Volvo OFFICIAL dealer (Zaragoza/Barcelona), tiny used
  stock (~15), already covered by OEM dealer-network / Das WeltAuto connectors. Not a national chain.
- **GpsAutos** — NXDOMAIN (gpsautos.es / gpsautos.com both fail DNS). Dead.
- **Crandon (crandon.es)** — 114-byte stub page, no stock. Not a reachable chain.
- **Mundocar (mundocar.es)** — 2.8KB stub page, no stock. Not a reachable chain.

## HARVEST RESULT (verified in DB by own query, 2026-06-13)
| Member | cdp_code | surface | cars (edges==join==owned) | VAM verdict |
|--------|----------|---------|---------------------------|-------------|
| Clicars | CDP-ES-00-QCMVM26T | next_data (SSR HTML cards) | 1470 | TRUSTWORTHY |
| Carplus | CDP-ES-00-4YVMXZ3T | json_ld (SSR Vehicle blocks) | 412 | TRUSTWORTHY |

- 2 NEW entities (kind=cadena, source_group=chain, role=chain, t0_open). +1882 vehicles.
- Idempotent: Carplus re-run = +0; Clicars re-run = +1 (one new live car, delta event fired correctly).
- Dedup: each chain exists exactly once; cdp_code == deterministic `domain:<host>` code (no phantom dup).
- Clicars declares 1492 but caged 1470 distinct: its SSR pages overlap (799 cross-page dups collapsed);
  every DISTINCT car the surface served is caged — honest gap, not a bug.
- `chain` group now: 4 cadena platforms (Flexicar 23874, OcasionPlus 13445, Clicars 1470, Carplus 412)
  + 185 branch entities. Total cars across all 4 chain platforms = 39201.

## Future candidate (not in scope of this front, noted honestly)
- **Crestanevada (crestanevada.es)** — reachable national chain w/ JSON-LD; a future member under
  this same architecture. Its SRP needs a deeper surface probe (count not declared on the home page).
