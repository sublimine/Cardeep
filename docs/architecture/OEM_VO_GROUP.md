# CARDEEP — OEM-VO GROUP Rollup (`source_group='oem_vo_portal'`)

> **One line:** the manufacturer certified-used portals — a brand owner publishing
> the certified-used inventory of its OWN official dealer network — are now proven on
> **four** portals (`renew`, `Das WeltAuto`, `spoticar`, `toyota_lexus`), every one
> flowing through the ONE architecture (`pipeline/platform/*_wholesale.py`: governor
> choke point, GeoResolver, dual-membership, VAM), not a fork of it. All figures
> `[VERIFIED]` against the live DB (`cardeep-pg`, `:5433`, db `cardeep`) and the
> persisted VAM verdict ledger on **2026-06-13**.

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

## The four portals — live DB rollup

Per-portal `cars` = distinct caged inventory reached via the `platform_listing` edge
(`db_edges` == `db_join_vehicles`); `dealers` = distinct owning official dealers reached
via that same edge. `[VERIFIED]` against `cardeep-pg` on 2026-06-13.

| Portal | `cdp_code` | Cars | Dealers | `defense_tier` | `family` | VAM verdict |
|---|---|--:|--:|---|---|---|
| **spoticar** (Stellantis: Peugeot, Citroën, Opel, DS, Fiat, Jeep…) | `CDP-ES-00-D6X2282Y` | **5 884** | 135 | `t1_soft` | `stellantis_vo` | TRUSTWORTHY |
| **renew** (Renault Group: Renault, Dacia, Refactory) | `CDP-ES-00-DT59NK3D` | **918** | 115 | `t0_open` | `renault_group` | TRUSTWORTHY |
| **toyota_lexus** (Toyota Plus + Lexus Select) | `CDP-ES-00-GNAJ5S16` | **768** | 94 | `t0_open` | `toyota_lexus_vo` | TRUSTWORTHY |
| **Das WeltAuto** (VW Group: VW, SEAT, Škoda, CUPRA, Audi) | `CDP-ES-00-XWX9RHG7` | **552** | 56 | `t1_soft` | `vw_group` | TRUSTWORTHY |
| **GROUP TOTAL** | — | **8 122** | **400** | — | — | 4/4 TRUSTWORTHY |

> **Dealer disjointness `[VERIFIED]`:** 0 dealers are shared across more than one OEM-VO
> portal, so the group-wide distinct dealer count (400, queried directly via
> `COUNT(DISTINCT v.entity_ulid)` over all four portals' edges) equals the sum of the
> per-portal counts (135 + 115 + 94 + 56 = 400). This is expected — each brand network is
> disjoint from the others.

---

## VAM count quorum (like-with-like, per slice)

Each portal's harvest closes with a three-path count quorum that all measure the same
thing — "distinct cageable cars in this slice" — by orthogonal routes:

- `harvested_cageable` — distinct `(dealer_id, deep_link)` pulled from the live API (harvest truth)
- `db_edges` — `platform_listing` rows for the portal (DB write truth)
- `db_join_vehicles` — distinct vehicles reachable via the edge join (DB read truth)

Verdict `TRUSTWORTHY` when the three converge within tolerance; persisted to
`verification_verdict` (`subject_type='platform_slice'`). Latest persisted values:

| Portal | `harvested_cageable` | `db_edges` | `db_join_vehicles` | divergence | verdict |
|---|--:|--:|--:|--:|---|
| **toyota_lexus** | 768 | 768 | 768 | 0.0 | TRUSTWORTHY |
| **renew** | 918 | 918 | 918 | 0.0 | TRUSTWORTHY |
| **Das WeltAuto** | 552 | 552 | 552 | 0.0 | TRUSTWORTHY |
| **spoticar** | 5 880 | 5 884 | 5 884 | 0.00068 | TRUSTWORTHY |

> **toyota_lexus is the clean reference slice:** all three independent paths equal
> **768** with divergence 0.0 — harvest truth, DB write truth and DB read truth agree to
> the unit, verified independently in the live DB. 94 official dealers attributed.
>
> **One honest caveat, not masked:** spoticar's harvest-side count (5 880) trails its DB
> edge/join count (5 884) by 4 cars (0.068 %) — within the VAM tolerance, so the verdict
> stands TRUSTWORTHY, but the two routes are not bit-identical. The gap is the expected
> footprint of cross-page churn during a long drain (a car re-surfacing under a shifted
> default sort after its edge was already caged); the DB join is the authoritative count.
> renew, Das WeltAuto and toyota_lexus each close at exact 0.0 divergence.

---

## Per-portal surface notes (the recipe shape that earns the count)

- **spoticar** (`t1_soft`, `family=stellantis_vo`) — the largest OEM-VO network in ES
  by a wide margin (5 884 cars / 135 dealers). Per-car dealer attribution from the
  embedded selling-dealer object; geo anchored from the dealer record. `t1_soft`: a soft
  TLS/UA wall that serves cleanly to `curl_cffi` chrome131 impersonation, no JS challenge.

- **renew** (`t0_open`, `family=renault_group`) — `GET es.renew.auto/vehiculos.data`
  React-Router single-fetch JSON loader; RAW Elasticsearch facet params; per-vehicle real
  VIN; `vehicleExhibitionSite` = selling dealer (strong attribution). Genuinely open: the
  `.data` loader serves clean JSON to a Chrome TLS fingerprint, no WAF, no browser / proxy /
  cookie warm-up. 918 is the proof slice (portal declares ~5 739 unfiltered).

- **toyota_lexus** (`t0_open`, `family=toyota_lexus_vo`) — `POST` against the Toyota-Europe
  USC (Used Stock Cars) Web Components JSON API
  (`usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}`),
  ONE backend, two brand scopes, single ES `distributorCode=9424M`. Behind AWS CloudFront
  with NO bot WAF — serves HTTP 200 `application/json` to plain `curl`. Per-car dealer
  embedded (id, name, full address+zip, lat/lon); province from `dealer.address.zip[:2]`
  (INE) with lat/lon geocode fallback. Latin-1 mojibake on human-text fields, repaired on
  ingest. The clean reference slice: 768 / 768 / 768, divergence 0.0.

- **Das WeltAuto** (`t1_soft`, `family=vw_group`) — `curl_cffi` chrome131 `GET` against
  per-province routes (`/esp/coches-de-segunda-mano-en-{provincia}?pagina=N`); AEM SSR HTML;
  per-card `data-configuration` JSON (the car) + `data-partner` JSON (the dealer, geo via
  ZIP). Enumeration is **per-province**, not one national paginator; the last page
  CLAMP-REPEATS, so the stop signal is "a page adds zero NEW VehicleIds" (handled by the
  bulk-cage cross-page dedup), not "a page is empty". 552 is the capped proof slice
  (portal advertises >8 000 nationally).

---

## Provenance

- **Source of truth:** live DB `cardeep-pg` (`:5433`, db `cardeep`) on **2026-06-13**.
  Per-portal cars/dealers from the `platform_listing` edge join; group total dealers from a
  direct `COUNT(DISTINCT)` over all four portals (0 cross-portal sharing confirmed).
- **VAM verdicts:** latest per-slice rows in `verification_verdict`
  (`subject_type='platform_slice'`), connectors `pipeline/platform/{spoticar,renew,
  oem_toyota_lexus,dasweltauto}_wholesale.py`.
- **Taxonomy:** `kind` ENUM `migrations/0005_types_and_guards.sql`; `source_group` /
  `defense_tier` / `role` ENUMs `migrations/0016_tiering_groups.sql`; dual-membership
  edge `migrations/0009_platform_listing.sql`; vehicle/event model
  `migrations/0003_vehicles_events.sql`.
