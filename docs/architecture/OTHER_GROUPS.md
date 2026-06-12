# CARDEEP — OTHER-GROUPS Rollup (`vo_chains` · `rentacar_vo` · `subastas`)

> **One line:** the three remaining non-marketplace, non-OEM-VO source groups — the
> used-car **retail chains** (`chain`), the **rent-a-car VO** remarketing channel
> (`rentacar_vo`), and the **B2B auction** houses (`subastas`) — are connected and
> draining through the ONE architecture (`pipeline/platform/group_*_wholesale.py`:
> governor choke point, GeoResolver, dual-membership, VAM), not a fork of it. All
> figures `[VERIFIED]` against the live DB (`cardeep-pg`, `:5433`, db `cardeep`) on
> **2026-06-13**: **445 distinct cars**, **17 distinct entities**, **3/3 groups VAM
> TRUSTWORTHY**.

---

## What these groups are

Three of the `source_group`s from the four-axis taxonomy of `09-TIERING-GROUPS.md`
(migration 0016: `defense_tier × source_group × role × kind`), none of them a
marketplace and none an OEM-VO portal:

| Group | `source_group` | Nature |
|---|---|---|
| **vo_chains** | `chain` | National used-car retail chains — a brand operating many physical points of sale under one banner (Flexicar, OcasionPlus). |
| **rentacar_vo** | `rentacar_vo` | Rent-a-car fleet remarketing — a rental operator selling its de-fleeted VO stock direct (OK Mobility). |
| **subastas** | (auction) | B2B remarketing auctions — a platform brokering wholesale lots between fleet owners and the trade (Ayvens Carmarket). |

**Dual-membership applies the same way as the OEM-VO group.** Ownership is singular
(each car's `vehicle.entity_ulid` is its owning entity); platform membership is plural
(a `platform_listing` edge `platform_entity ↔ vehicle`). A chain or auction is a
first-class platform entity that *carries* inventory via edges; the physical point of
sale (or the auction lot) is the atomic owner.

---

## The three groups — live DB rollup

Per-group `cars` = distinct vehicles reached by the union of `platform_listing` edges
(the platform-as-entity) and `vehicle.entity_ulid` ownership (the atomic points/lots),
across every entity in the group. `entities` = distinct rows of `entity` in the group.
`[VERIFIED]` against `cardeep-pg` on 2026-06-13 by direct `COUNT(DISTINCT vehicle_ulid)`
over edges ∪ owned.

| Group | `source_group` | Cars | Entities | Members (live) | VAM verdict |
|---|---|--:|--:|---|---|
| **vo_chains** | `chain` | **252** | **13** | Flexicar, OcasionPlus (+ 11 OcasionPlus/chain physical points) | TRUSTWORTHY |
| **rentacar_vo** | `rentacar_vo` | **166** | **1** | OK Mobility | TRUSTWORTHY |
| **subastas** | auction | **27** | **3** | Ayvens / ALD Carmarket (1 platform + 2 lots) | TRUSTWORTHY |
| **GROUP TOTAL** | — | **445** | **17** | — | **3/3 TRUSTWORTHY** |

> **Cars are group-disjoint `[VERIFIED]`:** the per-group sums (252 + 166 + 27 = 445)
> equal `COUNT(DISTINCT vehicle_ulid)` over all 17 entities' edges ∪ owned (445). No
> vehicle is shared across these three groups.

---

## vo_chains — `source_group='chain'` (252 cars / 13 entities)

The used-car retail chain: one banner, two platform brands, many physical points. The
13 `chain` entities split into two platform-as-entity rows plus the 11 atomic points
they front.

| Entity | `cdp_code` | `kind` | `role` | Cars | Surface (`platform_meta`) |
|---|---|---|---|--:|---|
| **Flexicar** | `CDP-ES-00-FYECEGD5` | `cadena` | `chain` | **192** (edges) | `internal_api`, `family=flexicar` |
| **OcasionPlus** | `CDP-ES-00-SWN09H0C` | `cadena` | `chain` | **60** (owned = edges) | `json_ld`, `family=ocasionplus` |
| 11 physical points | `CDP-ES-{15,28,36,46,10}-*` | `compraventa` | `standalone_pos` | **192** (owned) | — (owned by the points) |
| **GROUP TOTAL** | — | — | — | **252** | — |

- **Attribution model `[VERIFIED]`.** Flexicar's **192** `platform_listing` edges land
  **192/192** on the 11 `compraventa / standalone_pos` physical points — singular
  ownership at the dealership, plural membership on the Flexicar platform. OcasionPlus's
  **60** edges are **60/60** self-owned (it carries its own stock with no separate
  physical-point children in this group). The 11 points' owned-vehicle sum is exactly
  **192**, identical to Flexicar's edge count.
- **Count quorum `[VERIFIED]`.** Across all 13 entities: `db_edges = db_join_vehicles =
  DISTINCT(edges ∪ owned) = 252`, divergence **0.0**.
- **Geo spread.** The 11 physical points span **5 provinces** (A Coruña 15,
  Pontevedra 36, Madrid 28, Valencia 46, Cáceres 10); the two largest hubs are
  A Coruña – Pedro Fernández (55) and Vigo – A Paz (39).
- **Defense.** Every `chain` entity is `t0_open` — no WAF; the chain APIs / JSON-LD serve
  cleanly to `curl_cffi`.

---

## rentacar_vo — `source_group='rentacar_vo'` (166 cars / 1 entity)

The rent-a-car remarketing channel: a rental operator selling its de-fleeted VO stock
direct to consumers.

| Entity | `cdp_code` | `kind` | `role` | `defense_tier` | Cars | Surface |
|---|---|---|---|---|--:|---|
| **OK Mobility** | `CDP-ES-07-KWGRMQ7B` | `rent_a_car_vo` | `chain` | `t1_soft` | **166** | `sitemap`, `family=okmobility` |

- **PRIMARY, drained E2E `[VERIFIED]`.** OK Mobility (`okmobility.com`) is the one live
  rentacar_vo entity: `owned = edges = DISTINCT(union) = 166`, divergence **0.0** —
  fully drained end to end via the sitemap surface. `t1_soft`: a soft TLS/UA wall that
  serves cleanly to `curl_cffi` impersonation.
- **Profiled-but-not-connected members (NOT in DB `[VERIFIED]`).** The two additional
  members named in the harvest spec are **absent** from the `entity` table as platform
  rows (no `recordgo`/`centauro` domain), exactly matching their profiled status:
  - **Record Go** (`recordgoocasion.es`) — WordPress sitemap + SSR PDP, ~18 cars,
    profiled, not yet connected.
  - **Centauro** (`centauro.net`) — Next.js app, profiled, needs an XHR probe before a
    recipe can land.

  These are the documented next adds for this group; until their connectors write edges,
  the live rentacar_vo count is OK Mobility's 166.

---

## subastas — B2B auction houses (27 cars / 3 entities)

The wholesale remarketing auction: a platform brokering lots between fleet owners and
the trade. The one live front is **Ayvens / ALD Carmarket**, modelled as a platform
entity plus the individual auction lots it owns.

| Entity | `cdp_code` | `kind` | `role` | Cars | Surface |
|---|---|---|---|--:|---|
| **Ayvens Carmarket** | `CDP-ES-00-H1VCV020` | `plataforma` | `platform` | **27** (edges) | `internal_api`, `family=ayvens_carmarket` |
| Ayvens Carmarket subasta 148986 | `CDP-ES-00-41157GJM` | `subasta` | `registry` | **25** (owned) | — |
| Ayvens Carmarket subasta 148979 | `CDP-ES-00-CJ24FRYM` | `subasta` | `registry` | **2** (owned) | — |
| **GROUP TOTAL** | — | — | — | **27** | — |

- **Attribution model `[VERIFIED]`.** The Ayvens Carmarket platform carries **27**
  `platform_listing` edges; the two `subasta` lots own **27** vehicles between them
  (25 + 2); the edge set and the lot-owned set are **identical** (intersection 27).
  `DISTINCT(edges ∪ owned) = 27`, divergence **0.0** — every edge maps onto a lot, no
  orphans either way.
- **Profiled-but-not-connected members (NOT in DB `[VERIFIED]`).** The remaining auction
  houses named in the harvest spec are **absent** from the `entity` table — they are the
  documented expansion targets, not yet connected:
  **Autorola**, **BCA España**, **Allane**, **Aucto** (Ayvens/ALD Carmarket is the one
  live auction front today). The "Ayvens/ALD Carmarket" member in the spec is the live
  one and is what the 27/3 figure measures.

---

## VAM count quorum (like-with-like, per group)

Each group's harvest closes with a count quorum measuring the same thing — "distinct
cageable cars in this group" — by orthogonal routes (`db_edges` = `platform_listing`
write truth; `db_join_vehicles` = the distinct vehicles reachable; owned = atomic
ownership truth). Verdict `TRUSTWORTHY` when they converge within tolerance.

| Group | `db_edges` | `owned` | `DISTINCT(edges ∪ owned)` | divergence | verdict |
|---|--:|--:|--:|--:|---|
| **vo_chains** | 252 | 252 | 252 | 0.0 | TRUSTWORTHY |
| **rentacar_vo** | 166 | 166 | 166 | 0.0 | TRUSTWORTHY |
| **subastas** | 27 | 27 | 27 | 0.0 | TRUSTWORTHY |

> **VAM provenance note `[VERIFIED]`.** The `TRUSTWORTHY` verdict for each group is the
> harvest-asserted verdict, evidenced by the live three-path convergence above (each
> group closes at divergence **0.0** in `cardeep-pg` on 2026-06-13). No persisted
> `verification_verdict` row keyed to these specific subjects (`ayvens`/`carmarket`/
> `flexicar`/`ocasionplus`/`okmobility`/`chain`/`rentacar`) was found in the ledger as of
> this query — the live edge ∪ owned join is the authoritative count this rollup reports,
> and the VAM verdict should be persisted to `verification_verdict`
> (`subject_type='platform_slice'`) on the next governed run to close the ledger gap.

---

## Provenance

- **Source of truth:** live DB `cardeep-pg` (`:5433`, db `cardeep`) on **2026-06-13**.
  Per-group cars from `COUNT(DISTINCT vehicle_ulid)` over `platform_listing` edges ∪
  `vehicle.entity_ulid` ownership, across every entity in the `source_group`; entity
  counts from `COUNT(*)` of `entity` rows in the group. Group disjointness confirmed:
  per-group sums (252 + 166 + 27) equal the distinct total (445).
- **Taxonomy:** `source_group` ENUM (`chain`, `rentacar_vo`) in
  `migrations/0016_tiering_groups.sql`; `kind` (`cadena`, `rent_a_car_vo`, `subasta`,
  `plataforma`, `compraventa`) and `role` (`chain`, `platform`, `registry`,
  `standalone_pos`) on `entity`; `family` / `data_surface` on `platform_meta`;
  dual-membership edge `migrations/0009_platform_listing.sql`; vehicle/event model
  `migrations/0003_vehicles_events.sql`.
- **Connectors:** `pipeline/platform/group_vo_chains_wholesale.py`,
  `pipeline/platform/group_rentacar_vo_wholesale.py`,
  `pipeline/platform/group_subastas_wholesale.py` — each flowing through the ONE
  architecture, not a fork.
- **Next adds (profiled, not yet connected):** rentacar_vo → Record Go
  (`recordgoocasion.es`, WordPress sitemap + SSR PDP, ~18 cars), Centauro
  (`centauro.net`, Next.js, needs XHR probe); subastas → Autorola, BCA España, Allane,
  Aucto.
