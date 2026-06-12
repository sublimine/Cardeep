# Long-tail CMS/DMS family map — the own-site harvest multiplier

> Re-verified live 2026-06-13 against cardeep-pg (`:5433`). Read-only market research
> over public dealer homepages (curl_cffi `impersonate=chrome131`, no proxy/browser).
> Evidence artifacts: `docs/_longtail_probe_list.json` (domain list),
> `docs/_longtail_fingerprints.json` (per-domain fingerprint), built by
> `scripts/longtail_fingerprint.py` + `scripts/longtail_refine.py`;
> `docs/_longtail_live_hosts.json` (current DB own-site hosts) +
> `docs/_longtail_family_ranking.json` (ranking re-aggregated over the live set).

## What this front is

Beyond the Tier-1 marketplaces (coches.net, AS24, wallapop, autocasion, motor.es —
each its own `pipeline/platform/*_wholesale.py` connector) and the OEM
certified-used portals, the inventory's long tail lives on each dealer's **own
website**. Harvesting thousands of own-sites one recipe at a time does not scale.
The multiplier is **CMS/DMS family**: group dealers by the platform their website
runs on, then write **ONE recipe per family** — every dealer on that platform
exposes its stock the same way, so one parser drains many dealers.

This document is that family map: which families cover the most dealers, and the
inventory-listing recipe seed for the top families.

## The own-site population (verified against the live DB)

The live `entity` table now holds **90,035** entities (grew from 22,671 as
discovery expanded; the `particular` kind dominates). Website coverage by kind
(`SELECT kind, count(*), count(website) ... GROUP BY kind`, 2026-06-13):

| kind | entities | with website |
|---|---:|---:|
| particular | 60,809 | 0 |
| compraventa | 19,059 | 458 |
| garaje | 7,248 | 797 |
| concesionario_oficial | 1,617 | 407 |
| desguace | 1,292 | 0 |
| plataforma | 7 | 7 |
| oem_vo_portal | 3 | 3 |

**865** car-selling entities (`compraventa` + `concesionario_oficial`) carry a
website — stable vs the prior pass. After removing OEM-portal / Tier-1-aggregator
hosts (`hyundai.es`=180, `concesionarios.seat`=109, `redoficial.citroen.es`=13,
`kia.com`=8, `tesla.com`=5, `ocasionplus.*`=14, `flexicar.es`=7, brand subdomains
`*.concesionariobmw.es`, `byd.blendio.es`, `audi.safamotor.com`, ... — those belong
to the **OEM-portal connector** front, not the long tail), what remains is the
genuine own-site long tail (re-aggregated 2026-06-13):

- **413** own-site entity rows
- **369** distinct registrable own-site domains (the unit a recipe targets)

> Boundary rule (verified): a brand token in a dealer's **own registered domain**
> (`citroencuenca.com`, `bmwautomotor.com`, `garciapeugeot.com`) stays long-tail;
> a brand token as an **OEM-infrastructure subdomain** (`redoficial.citroen.es`,
> `*.concesionariobmw.es`, `audi.safamotor.com`) is OEM-portal, excluded.

> OEM portals are NOT long-tail. `hyundai.es/concesionarios/<slug>`,
> `concesionarios.seat/...`, `redoficial.opel.es/<slug>`, brand subdomains
> (`armentia.toyota.es`) are OEM certified-used network pages — one connector per
> OEM brand (mirror `coches_net_wholesale.py`: platform-as-entity + dual-membership),
> covering ~330 entities in the head. This doc covers the 398-domain tail behind them.

## Family ranking (the multiplier map)

Each of the 369 live own-site domains carries a fetched fingerprint (366 reused from
the prior probe pass + 3 newly fetched builders). Coverage at **domain level** (one
recipe per domain) and at **entity-row level** (dealers served), re-aggregated
2026-06-13 over the live DB own-site set:

| family | domains | entities served | share of domains |
|---|---:|---:|---:|
| **cms** (WordPress-dominated) | 157 | 179 | 42.5% |
| unreachable | 86 | 91 | 23.3% |
| generic / custom | 73 | 83 | 19.8% |
| **dms** (vendor platforms) | 28 | 33 | 7.6% |
| framework (Next/Astro/Nuxt/Angular) | 17 | 18 | 4.6% |
| builder (Wix/Ueni/Google Sites/...) | 8 | 9 | 2.2% |

**283 / 369** domains are reachable; 86 unreachable (dead DNS + hard WAF/403/timeout
— genuinely offline or fully bot-walled, not a probe defect).

### Subfamily breakdown

| subfamily | domains | entities served |
|---|---:|---:|
| **cms/wordpress** (plain theme) | 143 | 164 |
| generic/custom | 66 | 76 |
| **dms/inventario_pro** | 15 | 19 |
| **dms/motorflash** | 11 | 12 |
| framework/nextjs | 9 | 9 |
| framework/astro | 5 | 5 |
| cms/wordpress + automotive plugin (motors/car_dealer/wp_auto_listing) | ~7 | ~7 |
| cms/prestashop | 2 | 2 |
| cms/drupal | 2 | 2 |
| dms/automanager | 2 | 2 |
| framework/angular | 2 | 2 |
| builder/basekit, builder/ueni | 2 each | 2 each |
| builder/wix, builder/google_sites, generic/iridio, generic/zoho, framework/nuxt | 1–2 each | — |

## #1 family — WordPress (152 domains, the clear winner)

WordPress is the dominant long-tail platform: **152 domains (~54% of reachable,
serving 164 dealers)** — 143 plain + ~7 carrying a named automotive plugin. Most run
a **custom theme, not a standard plugin** (no `stm_motors` / `car-dealer` marker), so
there is no single plugin API to hit. The recipe seed is therefore a **two-stage HTML
recipe**, not an API call:

1. **Listing-path discovery.** WordPress dealer sites converge on a small set of
   inventory entry slugs. Verified live across the family's discovered
   `inventory_paths` (frequency of hits): **`/coches` (229)**, `/vehiculos` (49),
   `/catalogo` (17), `/ocasion` (17), `/vehiculos-ocasion` (14), `/stock` (12),
   `/km0` (9), `/seminuevos` (9), `/coches-segunda-mano` (7), `/coches-ocasion` (7).
   A recipe probes this ranked slug list per site to find the listing index (then
   follows pagination `?pag=N` / `/page/N/`).
2. **Card parse.** Inventory cards are server-rendered `<article>`/`<div class="...car...">`
   blocks → make/model/price(`€`)/km/year/detail-link. The ~10 plugin sites
   (`motors_plugin`, `car_dealer_wp`, `wp_auto_listing`) expose a stricter, even
   more uniform card markup and can share a tighter sub-recipe.

WordPress is high-coverage but **medium-leverage per recipe** (theme variance means
the card selector needs a small per-site adaptation layer). It is the volume play.

## Top DMS family — inventario.pro (the highest-leverage recipe seed)

The cleanest multiplier is the DMS vendor **inventario.pro** — a Spanish dealer
website + stock platform. **15 own-site dealers** run it, and they share a
**byte-identical URL template and server-rendered HTML** (no JS rendering needed):

- Listing index: **`/coches`** (also `/coches-ocasion`, `/coches-nuevos`, `/vehiculos`)
- Detail link template: **`/coches/<make>/<model>/<numeric_id>`**
  (e.g. `/coches/citroen/c3/3549357`, `/coches/cupra/formentor/3462581`)
- Price rendered as text `<n> €`; vehicle id is the trailing numeric segment
  (stable native listing_ref).
- The `www.inventario.pro/` asset host appears in every page — the family fingerprint.

Because the template is uniform, **ONE recipe drains all 15 dealers** with zero
per-site adaptation. This is the model long-tail recipe.

> **Live re-check 2026-06-13:** 6/6 sampled inventario.pro dealers (canaauto.es,
> carsandbikes.es, masmotorcantabria.net, mobilitycentro.com, ftome.com,
> autosocasionalminares.com) return HTTP 200 on `/coches`, carry the `inventario.pro`
> asset fingerprint, expose `/coches/<make>/<model>/<id>` detail links, and render
> prices server-side. The seed is buildable today, no JS rendering needed.

**inventario.pro dealers (verified):** masmotorcantabria.net, eveauto.es,
autosniser.es, integralmotion.es, iluscar.com, mobilitycentro.com, ftome.com,
garciautodelvalles.com, canaauto.es, automovilesgabilondo.com,
autosocasionalminares.com, carmotors99.com, carsandbikes.es, tuokasion.es,
bellamachina.es. (2 more — grupogamboa.com, setienherra.es — share the template but
returned cert errors; likely same family.)

## Second DMS family — Motorflash (11 domains)

**motorflash** is the other significant vendor family (11 own-sites embed the
Motorflash stock widget/iframe; the host CMS varies — e.g. movento.es runs Drupal 10
behind the Motorflash widget). Stock is delivered through a Motorflash-hosted
component, so the recipe keys on the **`dms:motorflash` signal** and targets the
Motorflash listing surface rather than the host page's own theme. Verified seed
paths: `/coches`, `/coches-ocasion`, `/coches-nuevos`, `/coches-segunda-mano`,
`/vehiculos-de-ocasion`, with detail template `/ficha-vehiculo-ocasion/<slug>/<id>`
and faceted query params. One recipe per the Motorflash surface covers all 11.
Examples: grupmibec.com, helmantica.es, autoelia.es, movento.es, bmwpremiumselection.es.

## Recommended recipe build order (by leverage)

1. **inventario.pro** — 1 recipe → 15 dealers, uniform `/coches/<make>/<model>/<id>`
   SSR template (live-verified 6/6 on 2026-06-13). Highest ROI; build first. Maps onto
   the per-dealer recipe model (`pipeline/discover` → `pipeline/recipe` → `pipeline/ingest`)
   with a single shared parser keyed on the `inventario.pro` fingerprint.
2. **motorflash** — 1 recipe → 11 dealers via the shared Motorflash listing surface.
3. **WordPress generic** — the volume recipe: ranked slug-probe (`/coches` first) +
   card parser with a thin per-site selector override. ~152 dealers / 164 entities;
   build the discovery+card skeleton once, accept a small adaptation tail.
4. **WordPress + automotive plugin** (motors/car-dealer/auto-listing) — tighter
   sub-recipe off the WP skeleton; ~7 dealers with very uniform markup.
5. Long-tail singletons (prestashop, framework/nextjs+astro custom DMS, builders) —
   lower priority; framework/nextjs sites often expose a JSON API worth probing
   individually before writing HTML recipes.

## Pattern fit

- **OEM portals** → mirror `pipeline/platform/coches_net_wholesale.py` exactly:
  platform-as-entity (`kind='plataforma'`) + dual-membership (vehicle owned by the
  dealer, `platform_listing` edge to the portal) + batch ingest + governor + VAM.
- **Long-tail families** → per-dealer recipe model (`pipeline/discover` +
  `pipeline/recipe` + `pipeline/ingest`), but the recipe is keyed on the **family
  fingerprint** (the `inventario.pro` host, the Motorflash embed, the WP slug+card
  shape) so one recipe is reused across every dealer in the family — the multiplier.

## Reproduce

```
python scripts/longtail_fingerprint.py   # probe domains -> _longtail_fingerprints.json
python scripts/longtail_refine.py        # recover unreachables + expanded signatures
```
The 2026-06-13 re-verification pulled the live own-site host set straight from the DB
(`entity` WHERE website IS NOT NULL AND kind IN ('compraventa','concesionario_oficial'),
minus OEM/Tier-1), reconciled it against `_longtail_fingerprints.json` (366/369 already
classified; 3 builders fetched fresh), and re-aggregated the ranking into
`docs/_longtail_family_ranking.json`. Re-run that DB aggregation against `CARDEEP_DSN`
to re-verify; numbers above are live from `entity` (cardeep-pg `:5433`).
