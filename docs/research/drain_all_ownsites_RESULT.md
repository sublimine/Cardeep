# FRONT: drain_all_ownsites — full reachable own-site roster drain

> Run 2026-06-13 against **cardeep-pg** (`postgres://cardeep@localhost:5433/cardeep`).
> Every number below is DB-verified by my own query (VAM), not read from a brief.

## What was run

Each `family_*_wholesale.py` connector was run across **EVERY reachable member** of
its roster (not just the 3-5 proof dealers). The reachable roster was built from
`docs/_longtail_fingerprints.json` (`reachable==true`), persisted to
`docs/research/_drain_rosters.json`:

| roster fed | domains | connector(s) |
|---|---:|---|
| cms/wordpress (incl. Vehica) | 165 | `family_dealerk_wp` + `family_cms_wp` (each self-gates by fingerprint) |
| generic/custom | 83 | `family_generic_custom` (registry-bound, see note) |
| dms (inventario.pro + motorflash) | 31 | `family_dms_vendor_platforms` |
| framework (Next/Astro/Nuxt/Angular) | 19 | `family_framework_webbuilder` |
| builder (Wix/Ueni/GoogleSites/BaseKit/...) | 11 | `family_builder_wholesale` |
| **total reachable feed** | **309** | |

The 92 `family=unreachable` domains were skipped per
`docs/architecture/UNREACHABLE_STEALTH_RETEST.md` (89 genuinely dead NXDOMAIN/hard-wall,
1 already caged = hrmotor.com, 2 no own-site listing) — confirmed dead by a real
stealth browser, nothing to re-drain.

## Per-family result — full roster (run-slice, VAM-signed at 0.0 divergence)

| family | requested | members confirmed | producing | cars (VAM run-slice) | VAM |
|---|---:|---:|---:|---:|---|
| dealerk | 165 | 43 | 36 | **2 059** | TRUSTWORTHY 0.0 |
| dms_vendor | 31 | 27 | 21 | **799** | TRUSTWORTHY 0.0 |
| generic_custom | 10* | 10 | 10 | **1 029** | TRUSTWORTHY 0.0 |
| framework | 19 | 7 | 4 | **358** | TRUSTWORTHY 0.0 |
| builder | 11 | 6 | 1 | **432** | TRUSTWORTHY 0.0 |
| cms_wordpress | 165 | 13 | 13 | **518** | TRUSTWORTHY 0.0 |
| unreachable | — | 1 | 1 | **246** | TRUSTWORTHY 0.0 |
| **TOTAL** | | **110 attested** | **86** | **5 441** | all 7 TRUSTWORTHY |

\* generic_custom is **registry-bound by design** (per-dealer bespoke recipes — each
custom site has a unique parser). It only harvests its 10 registered recipes; the other
73 reachable generic/custom domains were declared "unknown dealer; skipping" because a
bespoke site needs a hand-written recipe (that is a discovery/recipe-authoring front,
not a roster drain).

## DB-verified family rosters (no-platform-edge superset)

| family | members (entity_source) | own-site cars |
|---|---:|---:|
| dealerk | 43 | 3 169 |
| dms_vendor | 27 | 1 691 |
| generic_custom | 10 | 2 499 |
| framework | 7 | 680 |
| builder | 9 | 1 781 |
| cms_wordpress | 13 | 599 |
| unreachable | 1 | 246 |
| **TOTAL** | **110** | **10 665** |

## Drain delta vs prior proof slice

- **Baseline (start of run):** 103 attested members / 10 178 own-site cars.
- **After full-roster drain:** 110 attested members / 10 665 own-site cars.
- **Net new from this run:** **+7 attested dealers, +487 own-site cars.**
  - dealerk: 37 → 43 members (+6: barrabinoehijos.com, eslauto.es, galcar.com,
    hnosroyo.es, indacar.es, lexusmadrid.es, mintegui.com, pamplonacar.com,
    talleresfernandezlucio.com, uniocasio.cat, vianautomobile.es and others newly
    fingerprint-confirmed; net +362 cars to 3 169).
  - builder: 8 → 9 members (+1; +3 cars).
  - generic +118 cars (csvmotor.com +35 fresh NEW delta), dms +4 cars.
- **1 NEW delta event** observed live this run (fresh inventory).

## The honest ceiling (medium-leverage limit, declared)

The biggest roster (165 cms/wordpress) yielded only **13 producing dealers / 518 cars**:
**138 of 165** reachable WordPress hosts returned *"WordPress, but no known card theme /
no Vehica REST"* — generic custom WP themes whose card markup varies per site and is not
covered by the family parser. This is the predicted medium-leverage WP reality
(`longtail_families.md`): draining them needs a per-site selector layer (a recipe-authoring
front), not the family multiplier. The cms connector drains only Vehica-REST sites and
the recognized card themes (stm_motors, auto_listing, ga-car-card, sc_cars_item).

5 builder members are JS-only (no SSR/JSON-LD) — honest 0, would need a stealth browser.

## Verdict

Full reachable roster drained where a family recipe can reach it. **110 own-site dealers /
10 665 own-site cars** now attested across 7 families (all VAM TRUSTWORTHY at 0.0), up from
the 103 / 10 178 proof baseline. The remaining untapped reachable own-site surface is
**~211 WordPress/generic domains with no recognized card theme** — recipe-authoring work,
not a drain, and flagged here rather than silently dropped.
