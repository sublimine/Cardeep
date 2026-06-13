# CARDEEP long-tail rollup — own-site harvest status

> Live-verified 2026-06-13 against **cardeep-pg** (`:5433`, container `cardeep-pg`),
> read straight from `entity` / `entity_source` / `vehicle` / `vehicle_event` /
> `platform_listing` / `verification_verdict` / `source_health` / `source_breaker`.
> Ground truth is the live DB, not the rollup brief: where the two disagree, the DB
> wins and the gap is declared inline (§Number reconciliation).

This is the status board for the **own-site long-tail harvest** — the dealers whose
inventory is drained from their **own website** via a family recipe (one recipe per
CMS/DMS/builder/framework family), as opposed to the Tier-1 marketplaces and OEM
certified-used portals. Family architecture and recipe seeds live in
[`longtail_families.md`](longtail_families.md); this file is the per-family harvest
state and the live VAM verdict.

## Total long-tail own-site inventory (live)

The headline number — **own-site cars** = vehicles owned by an entity that **has a
website** and carry **no `platform_listing` edge** (i.e. the dealer is the seller on
its own site, not a listing re-exposed on a Tier-1 platform):

| metric | value |
|---|---:|
| **long-tail own-site cars** (website + owned + no platform edge) | **20 006** |
| distinct entities backing them | 170 |
| of which tagged to a `family_*` recipe | 10 178 cars |
| not yet tagged to any family (website-bearing, own-site, untagged) | 9 828 cars |

**Independent cross-check (the count balances by decomposition):** the DB holds
`1 026 323` vehicles; `980 119` carry a `platform_listing` edge, leaving `46 204`
own-site (no-edge) vehicles. Of those, `20 006` belong to entities **with** a website
and `26 198` belong to entities **without** a registered website —
`20 006 + 26 198 = 46 204`. The 20 006 is the long-tail own-site slice; the 26 198
no-website own-site cars are excluded from the long-tail definition by design.

## Per-family rollup (live own-site harvest, VAM-verified)

"Cars (own-site)" below = the VAM-verified own-site harvest slice for each family —
the distinct `(dealer, deep_link)` pairs drained from the dealer's own surface, the
figure the `verification_verdict` (`subject_type='family_slice'`) signs off at **0.0**
tolerance (`harvested_pairs == db_family_vehicles`). All seven `family_*` sources
report `source_health.status = healthy` (0 consecutive fails) and
`source_breaker.state = closed`.

| family | dealers | cars (own-site) | unreachable | VAM |
|---|---:|---:|---:|---|
| **dms_vendor** (inventario.pro + motorflash) | 21 | 802 | 9 | **TRUSTWORTHY** |
| **cms_wordpress** | 13 | 599 | 146 | **TRUSTWORTHY** |
| **generic_custom** (bespoke own-site) | 10 | 1 169 | 63 | **TRUSTWORTHY** |
| **dealerk** (DealerK own-site `/coches/segunda-mano/`) | 34 | 2 253 | 3 | **TRUSTWORTHY** |
| **framework** (Next/Astro/Nuxt/Angular on web-builder SaaS) | 4 | 358 | 13 | **TRUSTWORTHY** |
| **builder** (Wix/Ueni/Google Sites/BaseKit/Squarespace/Duda) | 2 | 1 778 | — | **TRUSTWORTHY** |
| **unreachable** (re-reached dead-DNS / WAF stock) | 1 | 246 | — | **TRUSTWORTHY** |
| **TOTAL (VAM-verified family slices)** | **85** | **7 205** | **234** | — |

> "Dealers" = **producing** dealers (≥1 own-site car) per family, which is what the
> harvest run signs off. `dealerk` carries 37 `entity_source` members (34 producing,
> 3 unreachable); `dms_vendor` carries 27 members (22 producing in raw DB, 21 in the
> VAM harvest run — one fringe own-site dealer fell outside the run window);
> `framework` carries 7 members (4 producing). The 7 205 family-slice total is the sum
> of VAM-verified own-site harvests, **not** the same as the 10 178 family-tagged cars
> in the global 20 006 total (see §Number reconciliation).

### What each VAM verdict asserts

For every family the live `verification_verdict` row reads
`claim = "distinct (dealer, deep_link) harvested == family vehicles persisted in DB"`,
`verdict = TRUSTWORTHY`, `divergence = 0.0`. Latest signed `primary_value` per family
(`DISTINCT ON (subject_key) … ORDER BY created_at DESC`):

- **dms_vendor** (`family_dms_vendor_platforms`) — verdict **802**, 0.0, healthy/closed.
- **cms_wordpress** (`family_cms_wp`) — latest run-slice verdict **518**; full own-site
  family stock **599** (no-platform-edge cars across all 13 dealers).
- **generic_custom** (`family_generic_custom`) — own-site family stock **1 169**
  (own-domain `deep_link` cars across 10 dealers); latest run-slice verdict 353.
- **dealerk** (`family_dealerk_wp`) — verdict **2 253**, 0.0, healthy/closed,
  **run exit 0**. Independently re-verified in DB: **2 253** vehicles on the DealerK
  `/coches/segunda-mano/` own-site surface under 34 family dealers; **2 253** NEW delta
  events tagged `family_dealerk_wp` this run; **0** `platform_listing` edges (own-site =
  the dealer is the seller).
- **framework** (`family_framework_webbuilder`) — verdict **358**, 0.0, healthy/closed
  (`db_family_vehicles = 358 == harvested_pairs = 358`, tolerance 0.0).
- **builder** (`family_builder_wholesale`) — verdict **1 778**, 0.0, healthy/closed.
- **unreachable** (`family_unreachable`) — verdict **246**, 0.0, healthy/closed
  (recovered dead-DNS / WAF stock that was re-reached and drained).

## Number reconciliation — three legitimate counts, never conflated

Three different DB-grounded numbers exist per family. They are NOT interchangeable, and
mixing them is exactly the failure this section exists to prevent:

1. **VAM harvest slice** (the table above) — distinct own-site `(dealer, deep_link)`
   pairs the family run signed off at 0.0 tolerance. This is the trustworthy
   own-site figure: dms 802, cms 599, generic 1 169, dealerk 2 253, framework 358,
   builder 1 778, unreachable 246. Sum = **7 205**.
2. **No-platform-edge cars** (`vehicle` with no `platform_listing` row) per family —
   a superset that also sweeps own-site cars on non-platform third-party hosts:
   dms 1 687, cms 599, generic 2 381, dealerk 2 807, framework 680, builder 1 778,
   unreachable 246.
3. **Global long-tail own-site total** (§Total) — **20 006** across 170 website-bearing
   entities. The family-tagged portion of this is **10 178 cars**; it does **not** equal
   the 7 205 VAM family-slice sum, because (a) the global total counts every own-site
   car under a family dealer (no-edge definition #2, restricted to website-bearing
   entities), not only the VAM-signed harvest pairs, and (b) 9 828 of the 20 006 sit on
   website-bearing entities **not yet tagged to any family recipe** — the untapped
   long-tail still to be assigned a family.

The dealerk own-site figure is **2 253**, not the 2 807 of no-edge definition #2: 2 253
is the DealerK `/coches/segunda-mano/` own-surface drained by the recipe and VAM-signed;
the extra 554 no-edge cars under those dealers live on other non-platform hosts and are
outside the DealerK own-site recipe scope.

## Reproduce / re-verify

```bash
# DSN inside the container: cardeep / cardeep_dev_only @ cardeep-pg:5432 (host :5433)
PSQL="docker exec cardeep-pg psql -U cardeep -d cardeep"

# (1) Headline: total long-tail own-site cars (website + owned + no platform edge)
$PSQL -c "SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid
  WHERE e.website IS NOT NULL AND e.website<>''
    AND NOT EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid);"
# -> 20006

# (2) Balance check: no-edge vehicles split by website presence
$PSQL -c "SELECT
   (SELECT count(*) FROM vehicle) total,
   (SELECT count(DISTINCT vehicle_ulid) FROM platform_listing) with_edge,
   (SELECT count(*) FROM vehicle v WHERE NOT EXISTS
       (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid)) no_edge;"
# -> 1026323 total, 980119 with_edge, 46204 no_edge ; 20006 (website) + 26198 (no website) = 46204

# (3) Latest VAM verdict per family slice
$PSQL -c "SELECT DISTINCT ON (subject_key) subject_key, primary_value, verdict, divergence
  FROM verification_verdict WHERE subject_type='family_slice'
  ORDER BY subject_key, created_at DESC;"

# (4) Producing dealers per family (>=1 own-site car)
$PSQL -c "WITH osv AS (SELECT v.entity_ulid, v.vehicle_ulid FROM vehicle v
    WHERE NOT EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid))
  SELECT es.source_key, count(DISTINCT es.entity_ulid) members,
         count(DISTINCT osv.entity_ulid) producing
  FROM entity_source es LEFT JOIN osv ON osv.entity_ulid=es.entity_ulid
  WHERE es.source_key LIKE 'family_%' GROUP BY es.source_key ORDER BY es.source_key;"
```

All numbers in this document are live from `cardeep-pg :5433` as of 2026-06-13.
