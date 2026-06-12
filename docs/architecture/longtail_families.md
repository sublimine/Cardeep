# Long-tail CMS/DMS family map — the own-site harvest multiplier

> Verified live 2026-06-12 against cardeep-pg (`:5433`). Read-only market research
> over public dealer homepages (curl_cffi, Chrome TLS fingerprint, no proxy/browser).
> Evidence artifacts: `docs/_longtail_probe_list.json` (domain list),
> `docs/_longtail_fingerprints.json` (per-domain fingerprint), built by
> `scripts/longtail_fingerprint.py` + `scripts/longtail_refine.py`.

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

The live `entity` table holds **22,671** entities. Website coverage by kind
(`SELECT kind, count(*), count(website) ... GROUP BY kind`):

| kind | entities | with website |
|---|---:|---:|
| compraventa | 12,507 | 458 |
| garaje | 7,249 | 797 |
| concesionario_oficial | 1,617 | 407 |
| desguace | 1,292 | 0 |
| plataforma | 6 | 6 |

**865** car-selling entities (`compraventa` + `concesionario_oficial`) carry a
website. After removing OEM-portal / Tier-1-aggregator domains (`hyundai.es`=180,
`concesionarios.seat`=109, `toyota.es`=22, `citroen.es`=13, `kia.com`, `tesla.com`,
`renault.es`, `flexicar.es`, `ocasionplus.*`, `coches.net`, ... — those belong to
the **OEM-portal connector** front, not the long tail), what remains is the
genuine own-site long tail:

- **461** own-site entity rows
- **398** distinct registrable own-site domains (the unit a recipe targets)

> OEM portals are NOT long-tail. `hyundai.es/concesionarios/<slug>`,
> `concesionarios.seat/...`, `redoficial.opel.es/<slug>`, brand subdomains
> (`armentia.toyota.es`) are OEM certified-used network pages — one connector per
> OEM brand (mirror `coches_net_wholesale.py`: platform-as-entity + dual-membership),
> covering ~330 entities in the head. This doc covers the 398-domain tail behind them.

## Family ranking (the multiplier map)

Each of the 398 distinct own-site domains was fetched and classified by website
platform. Coverage at **domain level** (one recipe per domain) and at **entity-row
level** (dealers served), verified against the DB:

| family | domains | entities served | share of domains |
|---|---:|---:|---:|
| **cms** (WordPress-dominated) | 165 | 194 | 41.5% |
| unreachable | 92 | 104 | 23.1% |
| generic / custom | 83 | 98 | 20.9% |
| **dms** (vendor platforms) | 31 | 36 | 7.8% |
| framework (Next/Astro/Nuxt/Angular) | 19 | 20 | 4.8% |
| builder (Wix/Ueni/Squarespace/...) | 8 | 9 | 2.0% |

**306 / 398** domains were reachable (92 unreachable after a verify-off + browser-
header retry pass: 40 dead DNS, the rest hard WAF/403/timeout — genuinely offline or
fully bot-walled, not a probe defect).

### Subfamily breakdown (reachable)

| subfamily | domains |
|---|---:|
| **cms/wordpress** (plain theme) | 149 |
| generic/custom | 76 |
| **dms/inventario_pro** | 15 |
| **dms/motorflash** | 13 |
| framework/nextjs | 10 |
| framework/astro | 6 |
| cms/wordpress+motors_plugin (+listing) | ~9 (across plugin combos) |
| cms/prestashop | 3 |
| builder/ueni | 2 |
| dms/automanager | 2 |
| cms/drupal, builder/wix, builder/basekit | 2 each |
| framework/angular, framework/nuxt, dms/sumauto, ... | 1–2 each |

## #1 family — WordPress (159 domains, the clear winner)

WordPress is the dominant long-tail platform: **149 plain + ~10 with a named
automotive plugin = ~159 domains (~53% of reachable)**. Most run a **custom theme,
not a standard plugin** (149 show no `stm_motors` / `car-dealer` marker), so there
is no single plugin API to hit. The recipe seed is therefore a **two-stage HTML
recipe**, not an API call:

1. **Listing-path discovery.** WordPress dealer sites converge on a small set of
   inventory entry slugs (observed across the family's homepage anchors):
   `/coches`, `/vehiculos-ocasion`, `/seminuevos`, `/km0`, `/catalogo`,
   `/coches-ocasion`, `/vehiculos-nuevos`. A recipe probes this slug list per site
   to find the listing index (then follows pagination `?pag=N` / `/page/N/`).
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

Because the template is uniform, **ONE recipe drains all 15+ dealers** with zero
per-site adaptation. This is the model long-tail recipe.

**inventario.pro dealers (verified):** masmotorcantabria.net, eveauto.es,
autosniser.es, integralmotion.es, iluscar.com, mobilitycentro.com, ftome.com,
garciautodelvalles.com, canaauto.es, automovilesgabilondo.com,
autosocasionalminares.com, carmotors99.com, carsandbikes.es, tuokasion.es,
bellamachina.es. (2 more — grupogamboa.com, setienherra.es — share the template but
returned cert errors; likely same family.)

## Second DMS family — Motorflash (13 domains)

**motorflash** is the other significant vendor family (13 own-sites embed the
Motorflash stock widget/iframe). Stock is delivered through a Motorflash-hosted
component, so the recipe targets the **Motorflash embed endpoint** rather than the
host page's own HTML — one recipe per the Motorflash surface covers all 13.
Examples: grupmibec.com, jarmauto.es, mundiauto.com.

## Recommended recipe build order (by leverage)

1. **inventario.pro** — 1 recipe → 15+ dealers, uniform `/coches/<make>/<model>/<id>`
   SSR template. Highest ROI; build first. Maps onto the per-dealer recipe model
   (`pipeline/discover` → `pipeline/recipe` → `pipeline/ingest`) with a single shared
   parser keyed on the `inventario.pro` fingerprint.
2. **motorflash** — 1 recipe → 13 dealers via the shared Motorflash embed surface.
3. **WordPress generic** — the volume recipe: slug-probe + card parser with a thin
   per-site selector override. ~159 dealers; build the discovery+card skeleton once,
   accept a small adaptation tail.
4. **WordPress + automotive plugin** (motors/car-dealer/auto-listing) — tighter
   sub-recipe off the WP skeleton; ~10 dealers with very uniform markup.
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
python scripts/longtail_fingerprint.py   # probe 398 domains -> _longtail_fingerprints.json
python scripts/longtail_refine.py        # recover unreachables + expanded signatures
```
Numbers above are queried live from `entity` (cardeep-pg `:5433`); re-run the DB
aggregation in `scripts/` against `CARDEEP_DSN` to re-verify.
