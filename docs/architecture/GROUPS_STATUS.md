# CARDEEP "Los Demás Grupos" — Status Rollup

> **One line:** beyond the Tier-1 marketplaces, the OWNER's mandate "los demás con
> su sistema" is now proven on TWO fronts — **OEM-VO portals** (renew + Das WeltAuto)
> and the **long-tail own-site CMS/DMS families** (DealerK/MotorK family recipe +
> the full live own-site classification). Every connector here flows through the ONE
> architecture (`pipeline/platform/*_wholesale.py`: governor choke point, GeoResolver,
> dual-membership, VAM), not a fork of it. All figures `[VERIFIED]` against the live
> DB (`cardeep-pg`, `:5433`, db `cardeep`) and the connector source on **2026-06-12**.

---

## The two non-marketplace fronts

These are the `source_group`s that are NOT `marketplace_motor` / `marketplace_generalist`
(those live in `tier1_recipes/CONNECTORS_STATUS.md`). The taxonomy is the four-axis
model of `09-TIERING-GROUPS.md` (migration 0016): `defense_tier × source_group × role × kind`.

| Front | `source_group` | Connector(s) | Recipe shape |
|---|---|---|---|
| **OEM-VO portals** | `oem_vo_portal` | `renew_wholesale.py`, `dasweltauto_wholesale.py` | platform-as-entity + dual-membership (mirror `coches_net_wholesale.py`) |
| **Long-tail own-sites** | `long_tail_web` | `family_dealerk_wholesale.py` (+ live classification) | CMS/DMS-family fingerprint → ONE shared recipe/parser → N dealers' own-sites |

---

## Front 1 — OEM-VO portals (`source_group='oem_vo_portal'`)

A single brand-owner publishing the certified-used inventory of its OWN dealer
network — not a marketplace, not generalist classifieds. The NEW group `renew`
opened; `dasweltauto` proved a second portal flows through the same architecture.

| Portal | Cars (verified slice) | Surface / recipe | `defense_tier` | `family` |
|---|--:|---|---|---|
| **renew** (Renault Group: Renault + Dacia + Refactory) | **918** | `GET es.renew.auto/vehiculos.data?<es_facets>&page=N` — React-Router single-fetch JSON loader; RAW Elasticsearch facet params; 23 cars/page; per-vehicle real VIN; `vehicleExhibitionSite` = selling dealer (strong attribution) | `t0_open` | `renault_group` |
| **dasweltauto** (VW Group: VW + SEAT + Škoda + CUPRA + Audi) | **552** | `curl_cffi` chrome131 `GET` against `www.dasweltauto.es` per-province routes (`/esp/coches-de-segunda-mano-en-{provincia}?pagina=N`) — AEM SSR HTML; per-card `data-configuration` JSON (the car) + `data-partner` JSON (the dealer, geo via ZIP) | `t1_soft` | `vw_group` |

Notes that matter:
- **renew** — `t0_open`: the `.data` loader serves clean JSON to a Chrome TLS
  fingerprint, no WAF challenge, no browser/proxy/cookie warm-up. `page` is a stable
  paginator (zero cross-page id overlap verified). Portal declares ~5,739 cars
  unfiltered (the census denominator); 918 is the proof slice, not the full drain.
- **dasweltauto** — `t1_soft`: the public origin 403s a naïve fetch (soft TLS/UA
  wall) but serves cleanly to chrome131 impersonation — no JS challenge.
  Enumeration is **per-province**, not one national paginator; the national route
  ignores `?pagina`. Last page CLAMP-REPEATS, so the stop signal is "a page adds
  zero NEW VehicleIds", not "a page is empty" — handled by the bulk-cage cross-page
  dedup. Portal advertises >8,000 nationally; 552 is the capped proof slice.

Both classify identically except `defense_tier`/`family`: `source_group='oem_vo_portal'`,
`role='platform'`, `kind='oem_vo_portal'`. Ownership is singular (the exhibition-site /
selling dealer); platform membership is plural (`platform_listing` edge). The same
physical car can carry BOTH an OEM-VO edge and a `coches.net` edge without changing its
owning dealer.

---

## Front 2 — Long-tail own-sites (`source_group='long_tail_web'`)

The inventory that exists ONLY on each dealer's own `www.<dealer>.es` — no Tier-1
marketplace feed. Harvesting one recipe per site does not scale; the multiplier is
the **CMS/DMS family**: group dealers by the platform their website runs on, write
ONE recipe per family, drain N dealers.

### 2a — Live own-site classification (the population map)

Queried live against cardeep-pg (`:5433`) for entities `WHERE website IS NOT NULL`
over the **22,671**-row `entity` table. After removing OEM-portal / Tier-1-aggregator
domains, the genuine own-site long tail is **461 entity rows across 398 distinct
registrable domains** (the unit a recipe targets). Family ranking (per `longtail_families.md`):

| family | domains | entities served |
|---|--:|--:|
| **cms** (WordPress-dominated) | 165 | 194 |
| unreachable (dead DNS / hard WAF) | 92 | 104 |
| generic / custom | 83 | 98 |
| **dms** (vendor platforms: inventario.pro, Motorflash, …) | 31 | 36 |
| framework (Next/Astro/Nuxt/Angular) | 19 | 20 |
| builder (Wix/Ueni/Squarespace/…) | 8 | 9 |

Evidence: `docs/_longtail_probe_list.json`, `docs/_longtail_fingerprints.json`,
built by `scripts/longtail_fingerprint.py` + `scripts/longtail_refine.py`.

### 2b — Family harvest PROVEN (DealerK / MotorK CMS family)

The **DealerK (MotorK) WordPress** family is the first long-tail family wired end to
end via `pipeline/platform/family_dealerk_wholesale.py` — a CMS-family fingerprint +
ONE shared recipe/parser draining **165** family domains' own-sites.

| Item | Value |
|---|---|
| Family domains harvested by one recipe | **165** |
| Fingerprint | WordPress + Elementor + "tucoche" plugin; assets from `*.dealerk.com/<tenant>/uploads/sites/<N>/` + photos from `cdn.dealerk.es/dealer/datafiles/vehicle/...` |
| Listing surface | `/coches/segunda-mano/` (also `/seminuevos/`, `/coches/`), paginated `?page=N` |
| Parser | identical `vcard-*` card markup across every member → ONE parser reads them all |
| Ownership model | singular & direct — dealer (`kind='compraventa'`) owns its cars (`entity_ulid=dealer`); **NO `platform_listing` edge** (own site is the PRIMARY source, not a third-party marketplace) |

Because the markup is byte-identical across members, ONE recipe + ONE parser harvests
N dealers — the multiplier the mandate demands, lifted from the per-dealer recipe model
(`pipeline.harvest_dealer`) to a family. Run:
`python -m pipeline.platform.family_dealerk_wholesale --from-db --limit 5`.

---

## Rollup table (all four results)

| # | Result | Count | Method / recipe (verified) |
|---|---|--:|---|
| 1 | `oem_vo_portal` — **renew** | **918** | `GET es.renew.auto/vehiculos.data?<es_facets>&page=N` — React-Router single-fetch JSON loader (`t0_open`) |
| 2 | `oem_vo_portal` — **dasweltauto** | **552** | `curl_cffi` chrome131 `GET` against `www.dasweltauto.es` per-province routes (`t1_soft`) |
| 3 | Long-tail CMS-family classification (own-sites) | **22,671** | Queried live cardeep-pg (`:5433`) for entities `WHERE website IS NOT NULL` over the full `entity` table → 461 own-site rows / 398 domains / family ranking |
| 4 | Long-tail family harvest (DealerK WordPress / MotorK CMS family) | **165** | CMS-family fingerprint + one shared recipe/parser → N dealers' own-sites |

---

## What remains

1. **Drain the OEM-VO portals fully** — both counts (918 / 552) are honest PROOF
   SLICES under `MAX_PAGES` / `MAX_PROVINCES` caps, not the full census (renew
   declares ~5,739; Das WeltAuto >8,000 advertised). Run the governed full harvest.
2. **Add the remaining OEM-VO portals** — `oem_vo_portal` is proven on 2 brand groups
   (Renault, VW); Spoticar (Stellantis, `t3_hard_sensor`) and MB Certified remain.
3. **Build the next long-tail families by leverage** — `inventario.pro` (1 recipe →
   15+ dealers, uniform SSR `/coches/<make>/<model>/<id>`) and `motorflash` (1 recipe
   → 13 dealers via shared embed) are the highest-ROI seeds after DealerK.
4. **Run VAM on the new connectors** — clear the VAM verdict for renew, dasweltauto,
   and family_dealerk before declaring any TRUSTWORTHY.

---

*Source of truth: live DB `cardeep-pg` (`:5433`) + `pipeline/platform/{renew,dasweltauto,family_dealerk}_wholesale.py` + `docs/architecture/longtail_families.md`. Generated 2026-06-12.*
