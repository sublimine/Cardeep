# Plan — Census data-quality overhaul (owner-flagged: inflated "puntos de venta")

> From the deep data-quality audit (workflow wqvzjds77, 5 agents, all vs live DB 2026-06-23). The owner
> caught the served census inflating sales points. Root: NO single "sales point" concept — three surfaces
> use three scopes; particulares (platform listings), desguaces (parts), and empty shells are all counted.
> Method: ONE canonical `v_servable_dealer` view consumed everywhere; every served-data change via
> dry-run (:5434) → golden cdp byte-identity → Ferrari → CI. Backend fixes activate on the API restart
> (the running uvicorn is a stale build). NEVER touch :5433 without dry-run.

## Honest count cascade (verified live)
- 54.587 = non-particular resolved-distinct — CURRENT headline, INFLATED (~2.9x).
- 52.405 = ex-desguace.
- 42.603 = ex-desguace + ex-garaje, ACTIVE representative — the real DIRECTORY of car sales points.
- 19.144 = any non-particular kind WITH ≥1 servable car — ACTIVE sales points (with live inventory).
- 18.994 = compraventa+oficial WITH inventory (the seal's own venta numerator ≈ 18.298).
- Vehicles: 1.841.679 served includes 510.649 PARTICULAR (C2C) cars; dealer stock = 1.331.030.
- 35.443 (64.9%) of the 54.587 have ZERO servable inventory (22.937 also have no website = no footprint).

## Issues (severity)
- [DONE e2f19a2] CRITICAL: /stats.dealers honest = non-particular ∧ non-desguace ∧ has-inventory (19.144).
- CRITICAL: three surfaces, three scopes (stats 54.587 / geo excludes unverified / seal 18.298) — unify.
- HIGH: duplicates — 4.485 deep_links under >1 resolved dealer (3.729 join ≥2 sales points). ROOT: B1
  (dealer-identity-det-v1) requires SAME municipality_code; 81% of dup groups span different municipios
  with the SAME name. Fix: re-run cross_source_dedup (pipeline/identity/cross_source_dedup.py, currently
  vam_verified=FALSE/inert) + a cross-muni edge (same norm name + phone-suffix-9 OR own website host OR
  shared deep_link). Audit its merges against the over-merge guards (test_dedup_invariants) before gating.
- HIGH: empty padding — 35.443 zero-inventory entities served as dealers.
- HIGH: vehicles conflation — "coches verificados" 1.84M includes 510k particular; dealer stock 1.33M.
- MEDIUM: price sentinels in servable_vehicle — 22.5k junk (<300 EUR, all-9s 9999/99999, price=1, 26.7k NULL).
- MEDIUM: seal desguace segment seals non-sales-points (2.785 incl unverified vs DGT 1.292).
- MEDIUM: geo — 56.766 (62%) non-particular served entities have no lat/lon; 12.862 no municipality.
- LOW: vehicle field hygiene (37.136 no year, 56 future, 100.423 no km, 287 km>1M, 685 'despiece' titles).
- LOW: sells_cars useless as scope (true for the 354k particulares); CIF populated in 1 entity; closed/evicted never populated.

## Prioritized fix plan (all €0)
1. [ ] Migration: `v_servable_dealer` = FROM servable_entity WHERE status='active' AND kind NOT IN
       ('particular','desguace') AND (kind<>'garaje' OR EXISTS servable_vehicle). The ONE source of truth.
2. [~] stats.py read from it; expose dealers_with_inventory (19.144) + dealer_directory (42.603). (dealers
       count already honest in e2f19a2; migrate to the view + add the directory field.)
3. [ ] Unify geo.py (/geo/{prov}/entities, /municipalities, /tree, full_pct) + v_province_seal on
       v_servable_dealer; move the desguace segment to a `v_discovery_seal` labelled discovery-only.
4. [ ] Frontend: "puntos de venta" → honest field; "coches verificados" → dealer stock (1.33M) or labelled.
       (NOTE: a separate frontend redesign WIP is in the working tree — coordinate, do not clobber.)
5. [ ] Duplicates: re-run cross_source_dedup nationally + cross-muni edge; verify vs test_dedup_invariants
       over-merge guards; gate vam_verified only when 0 cross-kind + caps respected.
6. [ ] Harden servable_vehicle (additive migration): owner-kind whitelist (drops 540k particular cars
       from census inventory), price floor (NULL OR >=~300), exclude all-9s sentinels + price=1.
7. [ ] Vehicle field sanitation: clamp year to [1950, year+1], km to [0,1e6]; require province_code to serve.
8. [ ] Signal hygiene: stop using sells_cars for scope; B1 phone edge → phone_es.phone_match_key; probe
       why closed/evicted are never populated (business-closure detection).

## STATUS
- [x] Step 2 (partial) — /stats.dealers honest definition (e2f19a2, CI green; activates on API restart).
- [ ] Steps 1,3-8 — sequenced; each served-data change dry-run+golden+Ferrari+CI.
