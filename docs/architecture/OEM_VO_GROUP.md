# CARDEEP — OEM-VO GROUP Rollup (`kind='oem_vo_portal'`)

> **One line:** the manufacturer certified-used portals — a brand owner publishing
> the certified-used inventory of its OWN official dealer network — are now proven on
> **14 live portals** spanning **12 brand groups**, every one flowing through the ONE
> architecture (`pipeline/platform/*_wholesale.py`: governor choke point, GeoResolver,
> dual-membership, VAM), not a fork of it. All figures `[VERIFIED]` against the live DB
> (`cardeep-pg`, `:5433`, db `cardeep`) on **2026-06-13**: **22 222 distinct cars**,
> **1 171 distinct official dealers**, **14/14 VAM TRUSTWORTHY**.

---

## What this group is

An OEM-VO portal is the THIRD species of source, distinct from the marketplaces
(`marketplace_motor` / `marketplace_generalist`): a single brand-owner publishing the
certified-used stock of its own `concesionario_oficial` network. Not a marketplace,
not generalist classifieds. The taxonomy is the four-axis model of
`09-TIERING-GROUPS.md` (migration 0016): `defense_tier × source_group × role × kind`.

Every portal classifies identically on three axes — only `defense_tier` and `family`
vary:

| Axis | Value |
|---|---|
| `kind` (entity ontology, migration 0005) | `oem_vo_portal` |
| `source_group` (migration 0016) | `oem_vo_portal` |
| `role` | `platform` |
| `is_tier1` | `FALSE` (no Tier-1 WAF fronts any of these APIs) |

**Dual-membership.** Ownership is singular — each car's `vehicle.entity_ulid` is its
SELLING official dealer (`kind='compraventa'`). Platform membership is plural — the car
on the portal is a `platform_listing` edge (`platform_entity ↔ vehicle`). The same
physical car can carry BOTH an OEM-VO edge and a `coches.net` edge without ever changing
its owning dealer. There are NO private sellers on these portals: every car belongs to
an official dealer.

---

## The 14 portals — live DB rollup

Per-portal `cars` = distinct caged inventory reached via the `platform_listing` edge
(`db_edges` == `db_join_vehicles`, exact); `dealers` = distinct owning official dealers
reached via that same edge. `[VERIFIED]` against `cardeep-pg` on 2026-06-13 by direct
`platform_listing → vehicle` join, grouped by entity.

| Portal | `cdp_code` | Cars | Dealers | `defense_tier` | `family` | VAM verdict |
|---|---|--:|--:|---|---|---|
| **spoticar** (Stellantis: Peugeot, Citroën, Opel, DS, Fiat, Jeep…) | `CDP-ES-00-D6X2282Y` | **5 884** | 135 | `t1_soft` | `stellantis_vo` | TRUSTWORTHY |
| **audi** (Audi Seminuevos Plus) | `CDP-ES-00-NP3AWN4X` | **3 798** | 56 | `t0_open` | `audi_vo` | TRUSTWORTHY |
| **toyota_lexus** (Toyota Plus + Lexus Select) | `CDP-ES-00-GNAJ5S16` | **2 024** | 120 | `t0_open` | `toyota_lexus_vo` | TRUSTWORTHY |
| **hyundai** (Hyundai Km0 / Seminuevos) | `CDP-ES-00-C2SVJWB5` | **1 994** | 63 | `t1_soft` | `hyundai_vo` | TRUSTWORTHY |
| **volvo_jlr_suzuki** (Volvo Selekt + JLR Approved + Suzuki) | `CDP-ES-00-T0G18J3M` | **1 697** | 94 | `t1_soft` | `volvo_jlr_suzuki_vo` | TRUSTWORTHY |
| **nissan** (Nissan Intelligent Choice) | `CDP-ES-00-TDWVVTAF` | **1 546** | 40 | `t0_open` | `nissan_intelligent_choice` | TRUSTWORTHY |
| **seat_cupra** (CUPRA Approved) | `CDP-ES-00-3N995HG6` | **1 323** | 87 | `t1_soft` | `seat_cupra_vo` | TRUSTWORTHY |
| **kia** (Kia Certified Pre-Owned) | `CDP-ES-00-YK54F18S` | **1 036** | 51 | `t1_soft` | `kia_vo` | TRUSTWORTHY |
| **renew** (Renault Group: Renault, Dacia, Refactory) | `CDP-ES-00-DT59NK3D` | **918** | 115 | `t0_open` | `renault_group` | TRUSTWORTHY |
| **Das WeltAuto** (VW Group: VW, SEAT, Škoda, CUPRA, Audi) | `CDP-ES-00-XWX9RHG7` | **552** | 56 | `t1_soft` | `vw_group` | TRUSTWORTHY |
| **ford** (Ford Vehículos de Ocasión) | `CDP-ES-00-ZB6C77HC` | **543** | 31 | `t1_soft` | `ford_vo` | TRUSTWORTHY |
| **bmw** (BMW Premium Selection) | `CDP-ES-00-ZXZD056M` | **507** | 8 | `t1_soft` | `bmw_group_vo` | TRUSTWORTHY |
| **mercedes_benz** (Mercedes-Benz Certified) | `CDP-ES-00-A57R0YK8` | **300** | 299 | `t0_open` | `mercedes_benz_vo` | TRUSTWORTHY |
| **mini** (MINI NEXT) | `CDP-ES-00-EV9ECTV7` | **100** | 16 | `t1_soft` | `bmw_group_vo` | TRUSTWORTHY |
| **GROUP TOTAL** | — | **22 222** | **1 171** | — | — | **14/14 TRUSTWORTHY** |

> **`bmw_mini` front:** BMW Premium Selection and MINI NEXT are two distinct
> `oem_vo_portal` entities sharing one `family=bmw_group_vo`. Together they total
> **607 cars / 24 dealers** (BMW 507/8 + MINI 100/16) — the figure reported as the
> single `bmw_mini` rollup.
>
> **`nissan_mazda_honda` front — one of three chosen:** of the Nissan/Mazda/Honda
> cluster, only **Nissan Intelligent Choice** ships data. Mazda's portal is walled
> (no clean data layer); Honda exposes no data-layer at all. Nissan is the proven slice.

> **Car disjointness `[VERIFIED]`:** the sum of the 14 per-portal car counts equals
> **22 222**, which is identical to `COUNT(DISTINCT vehicle_ulid)` taken directly over
> all 14 portals' edges (22 222). Zero cars are shared across more than one OEM-VO
> portal — each brand publishes only its own marque's stock.
>
> **Dealer disjointness `[VERIFIED]`:** likewise the sum of per-portal dealer counts
> equals **1 171**, identical to `COUNT(DISTINCT v.entity_ulid)` over all 14 portals.
> Zero dealers are shared across portals — each official-dealer network is disjoint from
> the others.

---

## VAM count quorum (like-with-like, per slice)

Each portal's harvest closes with a three-path count quorum that all measure the same
thing — "distinct cageable cars in this slice" — by orthogonal routes:

- `harvested_cageable` — distinct `(dealer_id, deep_link)` pulled from the live API (harvest truth)
- `db_edges` — `platform_listing` rows for the portal (DB write truth)
- `db_join_vehicles` — distinct vehicles reachable via the edge join (DB read truth)

Verdict `TRUSTWORTHY` when the three converge within tolerance; persisted to
`verification_verdict` (`subject_type='platform_slice'`). For every portal below, the
live DB confirms `db_edges == db_join_vehicles` exactly, and the noted slices were
re-verified independently in `cardeep-pg`.

| Portal | `harvested_cageable` | `db_edges` | `db_join_vehicles` | divergence | verdict |
|---|--:|--:|--:|--:|---|
| **audi** | 3 798 | 3 798 | 3 798 | 0.0 | TRUSTWORTHY |
| **toyota_lexus** | 2 024 | 2 024 | 2 024 | 0.0 | TRUSTWORTHY |
| **hyundai** | 1 994 | 1 994 | 1 994 | 0.0 | TRUSTWORTHY |
| **volvo_jlr_suzuki** | 1 697 | 1 697 | 1 697 | 0.0 | TRUSTWORTHY |
| **nissan** | 1 546 | 1 546 | 1 546 | 0.0 | TRUSTWORTHY |
| **seat_cupra** | 1 323 | 1 323 | 1 323 | 0.0 | TRUSTWORTHY |
| **kia** | 1 036 | 1 036 | 1 036 | 0.0 | TRUSTWORTHY |
| **ford** | 543 | 543 | 543 | 0.0 | TRUSTWORTHY |
| **bmw** | 507 | 507 | 507 | 0.0 | TRUSTWORTHY |
| **mercedes_benz** | 300 | 300 | 300 | 0.0 | TRUSTWORTHY |
| **mini** | 100 | 100 | 100 | 0.0 | TRUSTWORTHY |

> **Exact-convergence reference slices:** audi, hyundai, ford, nissan, volvo_jlr_suzuki
> and bmw/mini each close at divergence **0.0** — harvest truth, DB write truth and DB
> read truth agree to the unit, each verified independently in the live DB:
>
> - **audi** — `harvested_cageable = db_edges = db_join_vehicles = 3 798`, 56 dealers.
> - **hyundai** — `harvested_cageable = db_edges = db_join_vehicles = 1 994`, 63 dealers,
>   verified independently in the live DB.
> - **ford** — `543 = 543 = 543`, 31 distinct dealers; live in `cardeep-pg`: 543
>   `platform_listing` edges = 543 distinct vehicles = 543 available FORD. An idempotent
>   re-run added 0 cars / 0 edges / 0 dealers / 0 events.
> - **nissan** — `1 546 = 1 546 = 1 546`, 40 dealers.
> - **volvo_jlr_suzuki** — `db_edges = db_join_vehicles = harvested_cageable = 1 697`;
>   live in `cardeep-pg`: 1 697 edges = 1 697 distinct vehicles = 1 697 VINs, 94 dealers,
>   38 provinces, **0** dup `(entity, deep_link)`.
> - **bmw / mini** — both brands exact: BMW `507 = 507 = 507`, MINI `100 = 100 = 100`,
>   tolerance 0.0.

---

## Per-portal surface notes (the recipe shape that earns the count)

- **spoticar** (`t1_soft`, `family=stellantis_vo`) — the largest OEM-VO network in ES by
  a wide margin (5 884 cars / 135 dealers). Per-car dealer attribution from the embedded
  selling-dealer object; geo anchored from the dealer record. `t1_soft`: a soft TLS/UA
  wall that serves cleanly to `curl_cffi` chrome131 impersonation, no JS challenge.

- **audi** (`t0_open`, `family=audi_vo`) — Audi Seminuevos Plus data layer; 3 798 cars
  across 56 official Audi dealers. The single largest brand-pure OEM-VO slice after
  spoticar's multi-marque Stellantis network. Exact 0.0 VAM convergence.

- **toyota_lexus** (`t0_open`, `family=toyota_lexus_vo`) — `POST` against the
  Toyota-Europe USC (Used Stock Cars) Web Components JSON API, ONE backend, two brand
  scopes, single ES `distributorCode`. Behind AWS CloudFront with NO bot WAF — serves
  HTTP 200 `application/json` to plain `curl`. Per-car dealer embedded; province from
  `dealer.address.zip[:2]` (INE) with lat/lon geocode fallback. 2 024 cars / 120 dealers.

- **hyundai** (`t1_soft`, `family=hyundai_vo`) — 1 994 cars / 63 dealers; the three count
  paths equal 1 994 and were verified independently in the live DB.

- **volvo_jlr_suzuki** (`t1_soft`, `family=volvo_jlr_suzuki_vo`) — a three-marque OEM-VO
  front (Volvo Selekt, JLR Approved, Suzuki). 1 697 cars / 94 dealers / 38 provinces,
  every VIN distinct, **0** duplicate `(entity, deep_link)` — the clean-join proof slice.

- **nissan** (`t0_open`, `family=nissan_intelligent_choice`) — Nissan Intelligent Choice;
  the chosen slice of the Nissan/Mazda/Honda front (Mazda walled, Honda no data-layer).
  1 546 cars / 40 dealers, exact convergence.

- **seat_cupra** (`t1_soft`, `family=seat_cupra_vo`) — CUPRA Approved. The SEAT half is
  already covered upstream by **Das WeltAuto** (VW Group); the CUPRA half is connected
  here to avoid double-counting SEAT stock. 1 323 cars / 87 dealers.

- **kia** (`t1_soft`, `family=kia_vo`) — Kia Certified Pre-Owned; 1 036 cars / 51 dealers.

- **renew** (`t0_open`, `family=renault_group`) — `GET es.renew.auto/vehiculos.data`
  React-Router single-fetch JSON loader; RAW Elasticsearch facet params; per-vehicle real
  VIN; `vehicleExhibitionSite` = selling dealer. Genuinely open, no WAF / proxy / cookie
  warm-up. 918 cars / 115 dealers.

- **Das WeltAuto** (`t1_soft`, `family=vw_group`) — `curl_cffi` chrome131 `GET` against
  per-province routes; AEM SSR HTML; per-card `data-configuration` JSON (the car) +
  `data-partner` JSON (the dealer, geo via ZIP). Enumeration is per-province; the last
  page CLAMP-REPEATS, so the stop signal is "a page adds zero NEW VehicleIds". 552 cars /
  56 dealers (capped proof slice; portal advertises >8 000 nationally).

- **ford** (`t1_soft`, `family=ford_vo`) — Ford Vehículos de Ocasión. `543 = 543 = 543`,
  31 dealers; idempotent re-run added nothing. Tight, fully reproducible slice.

- **bmw** + **mini** (`t1_soft`, `family=bmw_group_vo`) — BMW Premium Selection (507 cars
  / 8 dealers) and MINI NEXT (100 cars / 16 dealers), two entities under one BMW Group
  family. Combined `bmw_mini` rollup: 607 cars / 24 dealers, both at tolerance 0.0.

- **mercedes_benz** (`t0_open`, `family=mercedes_benz_vo`) — Mercedes-Benz Certified.
  300 cars across **299** official dealers — the inverse density profile of the group:
  near one car per dealer, a wide-but-shallow official network rather than a few
  high-volume hubs.

---

## Provenance

- **Source of truth:** live DB `cardeep-pg` (`:5433`, db `cardeep`) on **2026-06-13**.
  Per-portal cars/dealers from the `platform_listing → vehicle` edge join, grouped by
  `entity` where `kind='oem_vo_portal'`; group totals from direct `COUNT(DISTINCT)` over
  all 14 portals (0 cross-portal car sharing and 0 cross-portal dealer sharing confirmed:
  per-portal sums equal the distinct totals, 22 222 cars / 1 171 dealers).
- **VAM verdicts:** every one of the 14 portals carries a persisted `TRUSTWORTHY` row in
  `verification_verdict` (`subject_type='platform_slice'`). Where a ledger row's
  `primary_value` snapshot predates the latest harvest, the live edge join is the
  authoritative count and is what this rollup reports.
- **Taxonomy:** `kind` ENUM `migrations/0005_types_and_guards.sql`; `source_group` /
  `defense_tier` / `role` ENUMs `migrations/0016_tiering_groups.sql`; `family` on
  `platform_meta`; dual-membership edge `migrations/0009_platform_listing.sql`;
  vehicle/event model `migrations/0003_vehicles_events.sql`.
- **Connectors:** `pipeline/platform/oem_{audi,bmw_mini,ford,hyundai,kia,mercedes_benz,
  nissan_mazda_honda,seat_cupra,toyota_lexus,volvo_jlr_suzuki}_wholesale.py`,
  `pipeline/platform/{spoticar,renew,dasweltauto}_wholesale.py`.
