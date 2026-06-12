# CARDEEP — 08 · Repository & Organization Architecture

> **Pillar document.** The physical shape of the whole system on disk and in git:
> the complete folder tree, the **absolute** Tier-1 vs long-tail separation (separate
> code trees, recipes, raw stores, operation, and even alerting), the naming
> conventions that make every artifact addressable to the last atom, the
> config-as-registry pattern that drives the harvesters, the versioned-vs-gitignored
> boundary, and the GitHub classification of every path. This is the skeleton the
> other pillars hang flesh on; it owns no scraping logic, no SQL, no taxonomy — it
> owns **where everything lives and why nothing collides**.
>
> **Supersedes** the partial layout sketches in `docs/workflows/README.md §"Arquitectura
> de capas"` (which shows only `pipeline/`), `docs/ARCHITECTURE.md §"Separación Tier-1"`
> (which states the separation but not the tree), and `docs/architecture/02-SCRAPING-ENGINE.md §9`
> (which names `countries/ES/recipes/<key>.yaml` and `countries/ES/_tier1/<key>.yaml`
> without the geo hierarchy). It reconciles all three into one canonical tree and gives
> the **deterministic migration** from the current flat reality to it.
>
> **Anchor reality (read before trusting any path here):** the on-disk repo as of
> 2026-06-12 — verified directly this session, not assumed. Every "current state" claim
> is `[VERIFIED]` (read from the filesystem / git / a source file this session) or
> `[ASSUMED]` (a forward design decision not yet on disk). No placeholders, no stubs.

---

## 0. Ground truth on disk RIGHT NOW (the reality this doc reorganizes)

Before designing the target, the exact current tree, `[VERIFIED]` this session
(`ls`, `git status`, `find`):

```
cardeep/
├── CLAUDE.md  PLAN.md  PROGRESO.md  README.md         # governance + living log (versioned)
├── .env.example  .gitignore  requirements.txt
├── .wf/                          # master_arch.js, validator_supremo.js (planning workflows)
├── countries/ES/recipes/         # 262 FLAT yaml files: CDP-ES-{NN}-{b32}.yaml  [VERIFIED count=262]
├── data/                         # GITIGNORED raw harvests (data/ES/<slug>/raw/, data/geo, data/probe)
├── docs/
│   ├── ARCHITECTURE.md  ORQUESTACION.md                # F2 first-pass (this doc supersedes layout bits)
│   ├── architecture/                                   # the Recon pillars (THIS file joins them)
│   │   ├── 00-TIER1-REGISTRY.md  01-ENTITY-ONTOLOGY.md  02-SCRAPING-ENGINE.md
│   │   └── verification/                               # (empty placeholder dir, present)
│   ├── research/   SOURCES_ES.md  SOURCES_ES_raw.json  # F1 census = ground truth (versioned)
│   └── workflows/  README.md                           # atom-level E2E phase design
├── migrations/   0001_geo.sql … 0004_verification_health.sql   # PG16, additive/reversible
├── pipeline/                     # deterministic production code (the cheap plane)
│   ├── __init__.py  discover.py  geo.py  geocode.py  harvest_dealer.py
│   ├── ids.py  ingest.py  recipe.py  verify.py
│   └── sources/   base.py dgt_cat.py osm.py autoscout24.py oem_{kia,mg,byd,skoda,dacia,hyundai,mercedes,seat}.py
├── scripts/      migrate.py load_geo.py seed_pilot.py scale_as24.py as24_{discover_dealers,harvest_batch}.py
└── services/
    ├── __init__.py
    └── api/      __init__.py  main.py  codes.py        # FastAPI + the cdp_code generator
```

Three facts this layout gets **wrong** against the mandate, each `[VERIFIED]` and each
fixed below:

1. **No geo hierarchy.** Recipes are a single flat folder of 262 files
   (`countries/ES/recipes/CDP-ES-28-12M7VRB0.yaml` …) `[VERIFIED]`. The mandate demands
   `país/provincia/comarca/ciudad/dealers/<cdp_code>/` ("ordenado por país/provincia/
   ciudad", CLAUDE.md). The province *is already embedded in every filename* (the `{NN}`
   segment of the `cdp_code`), so the geo tree is reconstructable deterministically (§5,
   §11).
2. **No Tier-1 tree exists yet, and the sibling docs name a different path.**
   `docs/ARCHITECTURE.md §"Separación Tier-1"` and `02-SCRAPING-ENGINE.md §9` both name the
   Tier-1 home as `countries/ES/_tier1/<key>.yaml` `[VERIFIED]` — but **no such directory is
   on disk** `[VERIFIED: find countries -type d → only countries/ES/recipes]`. This pillar
   **deliberately relocates the Tier-1 home to `platforms/_tier1/<name>/`** (a top-level
   peer of `sources/`, not a subfolder of the geo catalog), because separation-by-top-level
   is stronger than separation-by-subfolder (§3.2): a Tier-1 tree buried inside `countries/`
   sits one `rm`/glob slip away from the long-tail geo tree, whereas a top-level
   `platforms/` is its own world. The `entity.is_tier1` boolean and the served-catalog home
   are unchanged (Tier-1 platforms are still served from `countries/ES/_platforms/`, §3.1);
   only the **code+recipe bundle** moves to `platforms/_tier1/`. This is the one place this
   pillar overrides a path named by a sibling doc, and it does so explicitly, with reason —
   not silently. §3 builds it.
3. **No registry config.** The harvesters are driven by hardcoded knowledge inside
   `pipeline/sources/*.py` (e.g. `autoscout24.py`'s `_UA`, endpoints) `[VERIFIED]`, not by
   a versioned `config/registries/*.json`. The mandate's "config-as-registry" (platforms
   table drives the engine) does not exist as a file. §6 creates it.

This document is the contract that converges the repo to a tree where all three are
structurally correct and **cannot regress** (the separation is enforced by path, by
.gitignore, by a CI guard, and by the alert origin namespace — §3.4, §9.4).

---

## 1. The seven design laws (every path decision obeys these)

In priority order; when they conflict, the lower number wins.

1. **TIER-1 IS A SEPARATE WORLD, NOT A SUBFOLDER WITH A FLAG.** The hard-defense
   platforms (`00-TIER1-REGISTRY.md`) share **nothing** physical with the long-tail:
   not the recipe tree, not the raw store, not the runner, not the spend ledger, not even
   the alert origin prefix. A reader (or a CI rule, or an `rm -rf` mistake) operating on
   the long-tail tree can never touch Tier-1 and vice-versa. The boolean `entity.is_tier1`
   is the *data* expression of this; the **directory boundary is the operational
   expression**, and it is the stronger of the two (a flag can be mis-set; a path cannot
   be accidentally crossed). (§3)

2. **GEO IS THE PRIMARY ORGANIZING AXIS FOR THE LONG-TAIL.** Every long-tail entity
   artifact lives at its deterministic geo address `ES/<province>/<comarca>/<city>/dealers/
   <cdp_code>/`. The address is derived, never typed — `province` and the `cdp_code` come
   straight from the existing `codes.py`; `comarca`/`city` from the INE geo backbone
   (`migrations/0001`). Geo-less entities (national platforms, un-geocoded long-tail) have
   a defined sentinel home, never a lost file. (§4, §5)

3. **THE `cdp_code` IS THE UNIVERSAL FILESYSTEM PRIMARY KEY.** The same immutable code
   that keys `entity` in PG (`codes.py`, `CDP-ES-{prov}-{b32}`) is the directory name of
   that entity's artifact bundle. One entity ⇒ one code ⇒ one directory, everywhere,
   forever. Re-discovery never mints a second folder (the code is deterministic, §3.3 of
   the ontology). This makes "find the folder for entity X" a pure function of X's code.
   (§4.2)

4. **CONFIG IS A VERSIONED REGISTRY, CODE IS A GENERIC ENGINE.** What to harvest, with
   which defense, at which tier, lives in declarative JSON/YAML registries under
   `config/registries/` (versioned, reviewable, diffable). The Python engine reads the
   registry; it never hardcodes a platform, a count, or an endpoint. Adding a platform is
   a registry edit + a recipe, not a code change. (§6)

5. **RAW CRUDE IS EPHEMERAL AND GITIGNORED; THE RECIPE IS THE DURABLE ASSET.** The
   harvested HTML/JSON crude lives under `data/` (gitignored, evicted by capacity,
   `evict.py` + tombstone). The *recipe* that reproduces it without the crude is versioned
   in git `main`. Losing `data/` loses nothing recoverable; losing a recipe loses work.
   The two are physically separated so an eviction sweep can never touch a recipe. (§7, §8)

6. **MANY SMALL, COHESIVE, DEEP-ADDRESSED FILES > FEW BROAD ONES.** Per the global coding
   doctrine (200–400 lines typical, 800 max). The engine splits into `pipeline/fetch/`,
   `pipeline/sources/`, `pipeline/recipe/`, etc.; one source = one adapter file; one
   entity = one recipe file; one registry concern = one JSON. Nothing is a god-module. (§2)

7. **EVERY PATH HAS A DECLARED GIT DISPOSITION.** Each top-level path is exactly one of:
   **versioned** (committed to `main` — the durable asset), **gitignored-ephemeral**
   (`data/`, `state/` — regenerable/volatile), or **gitignored-secret** (`.env`). There is
   no fourth category and no undeclared path. The `.gitignore` is the machine-checkable
   statement of this law. (§9)

---

## 2. The target top-level tree (canonical)

The full repository after this pillar lands. **Versioned** unless tagged
`[GITIGNORED]`. New-vs-existing is marked: `[EXISTS]` is on disk now `[VERIFIED]`;
`[NEW]` is introduced by this design.

```
cardeep/
│
├── README.md  CLAUDE.md  PLAN.md  PROGRESO.md           [EXISTS]  governance + living log
├── .gitignore  .env.example  requirements.txt           [EXISTS]
├── pyproject.toml                                        [NEW]     packaging + tool config (ruff/pytest)
│
├── engine/                                               [NEW]     ← generic, source-agnostic core
│   │                                                               (the reusable machine; knows no platform)
│   ├── fetch/            session.py router.py tiers/ solvers.py    tiered fetch (02-SCRAPING-ENGINE §2-§8)
│   ├── recipe/           schema.py loader.py heal.py runner.py     recipe parse/validate/self-heal (§9)
│   ├── extract/          jsonpath.py jsonld.py sitemap.py next_data.py   data-layer extractors (law #1)
│   ├── delta/            engine.py events.py                       NEW/GONE/PRICE/PHOTO/KM (migrations/0003)
│   ├── geo/              resolve.py geocode.py                     INE name→code + lat/lon→province
│   ├── identity/         codes.py canonical.py                     cdp_code (moved from services/api, §10)
│   ├── verify/           vam.py quorum.py                          VAM count-quorum (was pipeline/verify.py)
│   └── health/           watchdog.py alerts.py                     source_health + alert origin (S-HEALTH)
│
├── sources/                                              [NEW]     ← LONG-TAIL discovery + harvest adapters
│   │                                                               (OPEN world only; never a Tier-1 platform)
│   ├── long_tail/
│   │   ├── registries/   dgt_cat.py aedra.py paginas_amarillas.py  legal/registral/directory discovery
│   │   ├── osm/          osm.py overture.py foursquare.py          geo POI discovery
│   │   ├── oem/          kia.py mg.py byd.py skoda.py dacia.py …    OEM locator JSON (concesionario discovery)
│   │   ├── oem_vo/       renew.py das_weltauto.py mb_certified.py  OEM VO portals (OPEN, §O of registry)
│   │   ├── aggregators/  autoscout24.py autocasion.py cochescom.py motorflash.py   OPEN platforms
│   │   └── chains/       flexicar.py ocasionplus.py clicars.py     single-seller chains (mono-sitemap)
│   └── base.py                                                     SourceAdapter contract (moved, §10)
│
├── platforms/                                            [NEW]     ← TIER-1 ONLY. Separate world (law #1)
│   └── _tier1/                                                     the leading underscore sorts it apart
│       ├── README.md                                              what Tier-1 is + the separation contract
│       ├── _shared/adevinta/ recipe.yaml  client.py               SHARED advgo.net recipe (GAP-32) — imported by the 4 Adevinta platforms
│       ├── wallapop/        adapter.py  recipe.yaml  fixtures/    api/v3/cars/search + app headers
│       ├── milanuncios/     adapter.py  recipe.yaml  fixtures/    imports _shared/adevinta + GeeTest
│       ├── coches_net/      adapter.py  recipe.yaml  fixtures/    imports _shared/adevinta (the Adevinta recipe)
│       ├── coches_com/      adapter.py  recipe.yaml  fixtures/    Imperva decaying-open
│       ├── spoticar/        adapter.py  recipe.yaml  fixtures/    Akamai (spend-gated)
│       ├── ayvens_carmarket/ adapter.py recipe.yaml  fixtures/    B2B auction catalog
│       ├── bca/             adapter.py  recipe.yaml  fixtures/    Cloudflare + B2B login
│       ├── autorola/        adapter.py  recipe.yaml  fixtures/    B2B login-gated
│       └── carnext/         adapter.py  recipe.yaml  fixtures/    Cloudflare (low ES priority)
│
├── countries/                                            [EXISTS, RESHAPED]  ← the served GEO catalog
│   └── ES/
│       ├── _platforms/                                  [NEW]     national platform entities (province 00)
│       │   └── <cdp_code>/   config.yaml recipe.ref manifest.json     e.g. CDP-ES-00-{hash(as24 domain)}
│       ├── _orgs/                                       [NEW]     organization roots (chains/groups/oem)
│       │   └── <org_code>/   org.yaml                              Flexicar, AUTO1, Kia España … (§ ontology 2.12)
│       └── <province>/                                  [RESHAPED] e.g. 28-madrid/ 08-barcelona/ … (52)
│           └── <comarca>/                                          e.g. area-metropolitana-de-madrid/
│               └── <city>/                                         e.g. madrid/ pinto/ …
│                   └── dealers/
│                       └── <cdp_code>/                  [NEW shape] e.g. CDP-ES-28-12M7VRB0/
│                           ├── config.yaml                          entity descriptor (geo, kind, org, urls)
│                           ├── recipe.yaml                          harvest recipe (was the flat file, §11)
│                           ├── manifest.json                        last harvest proof (count, hash, ts, VAM)
│                           └── tombstone.json                       eviction proof of life (when raw evicted)
│
├── migrations/          0001_geo.sql … 000N_*.sql        [EXISTS]  PG16 schema (additive/reversible)
├── services/
│   └── api/             main.py  routers/  schemas/      [EXISTS, GROWN]  FastAPI live API (codes.py → engine)
│
├── ops/                                                  [NEW]     operation: how the system is run/observed
│   ├── runners/         discover_loop.py harvest_loop.py tier1_run.py   the loops (cheap vs Tier-1 separate)
│   ├── orchestration/   discovery_fleet.md tier1_hunt.md inquisition.md  WF-* playbooks (from ORQUESTACION)
│   ├── migrate.py  load_geo.py                           [MOVED]   schema + geo loaders (from scripts/)
│   └── dashboards/      health.sql coverage.sql                    operator queries (denominator, deltas)
│
├── config/                                               [NEW]     config-as-registry (law #4)
│   └── registries/
│       ├── platforms_es.json                                       Tier-1 + OPEN platform registry (§6.1)
│       ├── sources_es.json                                         long-tail source registry (§6.2)
│       ├── oem_brands_es.json                                      OEM locator endpoints + org roots
│       ├── chains_es.json                                          chain → branch/sitemap map
│       ├── rentacar_brands_es.json                                 rent_a_car_vo allow-list (ontology D-6)
│       ├── auction_operators_es.json                               subasta operator list
│       ├── cms_families_es.json                                    CMS/DMS family → recipe template (§6.3)
│       └── defense_routing.json                                    defense → tier floor (02-ENGINE §3)
│
├── state/                                                [GITIGNORED]  volatile run state (§9.2)
│   ├── capacity-ledger.json  spend-ledger.json  run/  tier1-blocked.json
│
├── data/                                                 [GITIGNORED]  ephemeral raw crude (§7)
│   └── ES/<cdp_code>/raw/                                            evicted by capacity
│
├── docs/
│   ├── architecture/    00…02 + 08-REPO-ORGANIZATION.md  [EXISTS]  the pillars (this file)
│   ├── research/        SOURCES_ES.md  *_raw.json        [EXISTS]  F1 census
│   └── ARCHITECTURE.md  ORQUESTACION.md  workflows/      [EXISTS]
│
└── tests/                                                [NEW]     mirror of engine/ + fixtures (§9.5)
```

> **Naming of the geo levels.** Province dirs are `{NN}-{slug}` (the INE 2-digit code +
> kebab name: `28-madrid`), so they sort numerically and read humanly, and the `{NN}` is
> the *same* code embedded in every `cdp_code` under it (the join is trivial and visible).
> Comarca/city dirs are the INE name kebab-cased (`_normalize` from `codes.py` applied with
> hyphen separators). The leading-underscore dirs (`_platforms`, `_orgs`, `_tier1`) sort
> above the numeric provinces, visually separating the "non-provincial" nodes from the geo
> grid — the same trick `_tier1` uses to stand apart.

---

## 3. The ABSOLUTE Tier-1 / long-tail separation (law #1, fully specified)

This is the heart of the pillar and the owner's explicit, repeated demand
("separándome ABSOLUTAMENTE los Tier-1 y los demás grupos … con lógica y coherencia
total"). Separation is enforced on **six independent axes**, so failure of any one does
not collapse it.

### 3.1 The two worlds, side by side

| Concern | LONG-TAIL world (OPEN) | TIER-1 world (hard defense) |
|---|---|---|
| **Adapter code** | `sources/long_tail/**` | `platforms/_tier1/<name>/adapter.py` |
| **Recipe store** | `countries/ES/<prov>/.../dealers/<code>/recipe.yaml` (+ `_platforms/` for OPEN platforms) | `platforms/_tier1/<name>/recipe.yaml` (co-located with its code) |
| **Raw crude** | `data/ES/<code>/raw/` | `data/_tier1/<name>/raw/` (separate subtree) |
| **Runner / loop** | `ops/runners/{discover,harvest}_loop.py` (cheap, deterministic, €0) | `ops/runners/tier1_run.py` (gated, careful, may spend) |
| **Registry** | `config/registries/sources_es.json` | `config/registries/platforms_es.json` (`tier1:true` rows) |
| **Spend / block ledger** | n/a (€0 by definition) | `state/spend-ledger.json`, `state/tier1-blocked.json` |
| **Alert origin prefix** | `origin = "longtail:<source_key>"` | `origin = "tier1:<platform>"` (§3.4) |
| **Served-entity home** | `countries/ES/<prov>/.../dealers/<code>/` | `countries/ES/_platforms/<code>/` (national, province `00`) |

A few platforms are **OPEN platforms** (AS24, autocasion, coches.com sitemap, motorflash,
the OEM VO portals): they are *platforms* (national, `kind=plataforma`/`oem_vo_portal`,
served under `countries/ES/_platforms/`) but **not Tier-1** (no hard wall), so their
**adapter lives in `sources/long_tail/aggregators|oem_vo/`** and they run on the cheap
loop. Tier-1-ness is the *defense* axis (`00-TIER1-REGISTRY §0`), platform-ness is the
*entity-kind* axis (`01-ENTITY-ONTOLOGY D-2`); the directory split follows **defense**,
because that is what dictates code, cost, and operational care. This is the single
subtlety that a naive "platforms here, dealers there" split gets wrong, and it is
resolved explicitly: **the served catalog is geo/kind-shaped (`_platforms/`), the code
tree is defense-shaped (`sources/` vs `platforms/_tier1/`).**

### 3.2 Why the code tree is `platforms/_tier1/<name>/` (co-located bundle), not flat

Each Tier-1 giant is a *project* — it has bespoke header capture, a fragile recipe, golden
fixtures, and a hunt history. Co-locating `adapter.py + recipe.yaml + fixtures/` per
platform (a self-contained bundle) means one person owns one folder, the recipe sits next
to the code that consumes it, and deleting/quarantining a platform is `rm -rf
platforms/_tier1/<name>/` with zero blast radius. The long-tail, by contrast, is
*templated* (one adapter family drains thousands of dealers, §6.3), so its code is
generic in `sources/long_tail/` and its per-entity recipe is data in the geo tree. The
asymmetry of the two trees mirrors the asymmetry of the two worlds: **Tier-1 is N bespoke
projects; the long-tail is one engine × M config rows.**

### 3.3 The leading underscore is load-bearing

`_tier1`, `_platforms`, `_orgs` all begin with `_` so they **sort above** the
alphanumeric siblings and are visually unmissable as "not a normal geo/source node". This
is a deliberate, cheap, self-documenting signal: anyone listing `platforms/` sees only
`_tier1/`; anyone listing `countries/ES/` sees `_orgs/ _platforms/ 01-… 02-… 28-…` with
the specials grouped at the top. It also makes glob rules trivial (`platforms/_tier1/**`
is the entire Tier-1 code surface in one pattern, used by the CI guard §3.4 and by
`.gitignore` reasoning).

### 3.4 Separation enforced, not merely documented (the four guards)

1. **`.gitignore` partition** — `data/ES/**` and `data/_tier1/**` are independently
   ignored; an eviction sweep is scoped to one subtree and *cannot* reach the other (§9).
2. **Alert-origin namespace** — `health/alerts.py` stamps every `alert.origin` with a
   `tier1:` or `longtail:` prefix, so the operator instantly sees which world fired, and a
   query can isolate Tier-1 incidents (the mandate's "alerta con el origen EXACTO"). The
   two worlds never share an origin string.
3. **Runner isolation** — the cheap loop (`discover_loop.py`, `harvest_loop.py`) imports
   only `sources/long_tail/**` and physically *cannot* trigger a Tier-1 harvest (it has no
   import path to `platforms/_tier1/`). Tier-1 runs only via `tier1_run.py`, which checks
   the spend gate before any `platforms/_tier1/` adapter executes (`02-SCRAPING-ENGINE
   §2 Tier-2 hard rule`).
4. **CI structural guard** (`ops/` + a pre-commit/CI check, `[NEW]`) — a test asserts
   `import sources.*` never resolves a symbol from `platforms._tier1` and vice-versa, and
   that no `countries/ES/<NN>-*/.../dealers/<code>/` recipe carries `tier1: true` (a Tier-1
   recipe in the long-tail tree is a build failure). The boundary is a tested invariant,
   not a convention. (§9.4)

### 3.5 The HONEST scope of "absolute" — three surfaces that cross by construction `[adversarial GAP-32]`
The six axes are all **filesystem / ops** axes. Three surfaces cross the wall by construction, and
pretending otherwise is the dangerous lie. Declared and handled:
1. **The DATABASE is NOT separated — only flagged.** Tier-1 platform entities, their vehicles,
   `platform_listing` edges, and `verification_verdict` rows live in the **SAME tables/partitions** as
   long-tail data (`is_tier1` is a column, not a separate store). An `rm`/glob cannot cross the code
   trees, but a bad **query / migration / `DELETE`** absolutely crosses the data — that is the real
   blast radius, and it is NOT on the six axes. **Guard:** destructive ops on served data are gated by
   the **row-count sanity bound + the GONE-storm quarantine** (06 §… the destructive-delta refusal),
   not by `rm`. Invariant #5 (MASTER_PLAN) is corrected to "separated on disk + ops, NOT in the data".
2. **The Adevinta recipe FAMILY spans multiple Tier-1 platforms.** coches.net is Tier-1, but the SAME
   `advgo.net/search` recipe drains milanuncios + fotocasa + segundamano (00 §1.5). A single shared
   recipe asset means `rm -rf coches_net/` would **orphan the recipe the others import**, contradicting
   "zero blast radius" (§3.2). **Fix:** the shared recipe is extracted to
   **`platforms/_tier1/_shared/adevinta/`**; each platform bundle imports it. Deleting one platform is
   `rm -rf <name>/` **plus a registry edit**, never an orphan; the CI guard (§9.4) additionally checks
   the shared recipe has ≥1 importer (or is removed with its last importer).
3. **OPEN platforms legitimately STRADDLE both worlds.** AS24 is `is_tier1=false` but
   `kind=plataforma`: its adapter lives in long-tail `sources/long_tail/aggregators/` while its served
   entity lives in `countries/ES/_platforms/` (§3.1). This is **by design** and correct. The CI
   guard's invariant is therefore stated precisely: it checks **"no Tier-1-WALLED helper is imported
   by a long-tail or open adapter"** (a checkable, true invariant), NOT the un-checkable "open
   platforms never touch both worlds" (which they must). The earlier "absolute, NOTHING shared"
   framing is refined to this honest, enforceable form.

---

## 4. The per-entity artifact bundle (the atom of organization)

Every served entity — long-tail dealer or national platform — is a **directory named by
its `cdp_code`** containing a fixed, small set of files. This is the "estructura hasta el
último átomo" the mandate demands, made concrete.

### 4.1 The four files (and only these)

```
<cdp_code>/
├── config.yaml      # WHO this entity is — immutable identity + geo + kind + org + source URLs
├── recipe.yaml      # HOW to harvest its stock — the durable, versioned asset (02-ENGINE §9.1)
├── manifest.json    # PROOF of the last harvest — count, content-hash, timestamp, VAM verdict
└── tombstone.json   # PROOF OF LIFE after raw eviction — minimal record the raw existed & was valid
```

- **`config.yaml`** — the entity descriptor, derived from PG `entity` + `entity_source`,
  committed so the catalog is browsable without a DB. Fields: `cdp_code`, `kind`,
  `legal_name`/`trade_name`, `cif`, `cnae`, geo (`province_code`/`municipality_code`/
  `comarca_id`/`address`/`lat`/`lon`), `website`, `website_waf`, `is_tier1`, `org_code`
  (FK to `countries/ES/_orgs/`), `sources` (the `entity_source` attestations), `kind_source`
  (precedence rung, ontology §6.5). **Immutable identity, mutable enrichment** — re-running
  discovery refreshes enrichment, never the `cdp_code`.
- **`recipe.yaml`** — exactly the `02-SCRAPING-ENGINE §9.1` schema (version, defense, tier,
  access surface, field_map, validation, heal, provenance). The single most valuable
  versioned artifact in the repo: it re-creates the stock without the crude.
- **`manifest.json`** — written by `harvest_dealer.py` after each successful harvest:
  `{recipe_version, harvested_at, vehicle_count, batch_hash, vam_verdict,
  raw_path, raw_present: bool}`. It is the audit trail and the input to `evict.py`'s
  "is this safe to evict?" gate (`docs/workflows/README.md §FASE 5`).
- **`tombstone.json`** — written by `evict.py` when the raw is deleted for capacity:
  `{evicted_at, last_vehicle_count, last_batch_hash, recipe_version, reproducible: true}`.
  It is the mandate's "guardamos config y eliminamos por capacidad" — the *proof* the stock
  existed and is re-derivable from `recipe.yaml`, so eviction loses nothing.

> `manifest.json` and `tombstone.json` are **small and versioned** (they are proofs, KB-
> sized); the **raw crude they attest to is gitignored** under `data/`. This is the §5
> boundary in miniature, repeated at every entity.

### 4.2 The directory IS the entity (filesystem = primary index)

Because the directory name is the `cdp_code` and the code is a deterministic function of
canonical identity, the path to any entity's bundle is computable with zero lookups:
`countries/ES/{province_dir}/{comarca}/{city}/dealers/{cdp_code}/`. The province slug is
recoverable from the code's `{NN}`; the comarca/city from the DB or the entity's own
`config.yaml`. A national platform short-circuits to `countries/ES/_platforms/{cdp_code}/`.
This makes git the **secondary index of the database** — browsable, diffable, forkable —
which is precisely the mandate's "todo guardado y documentado … cualquiera pueda
retomarlo".

---

## 5. Geo addressing — deterministic placement of every long-tail entity

The rule that turns a `cdp_code` + DB row into exactly one path, with **no ambiguity and
no orphans**.

### 5.1 The placement function

```
place(entity) -> path
  if entity.is_tier1:            return platforms/_tier1/<platform_name>/        # code+recipe co-located
  if entity.kind in {plataforma, oem_vo_portal} and national:
                                 return countries/ES/_platforms/<cdp_code>/      # province sentinel 00
  if entity.org_id and is_root:  return countries/ES/_orgs/<org_code>/           # the chain/group root
  # normal geo-anchored point of sale:
  prov  = entity.province_code              # always present (INE 2-digit) — 100% resolved [VERIFIED PROGRESO]
  com   = comarca_slug(entity.comarca_id)   # may be NULL → "_sin-comarca"
  city  = municipality_slug(entity.municipality_code)  # may be NULL → "_sin-municipio"
  return countries/ES/<prov>-<prov_slug>/<com>/<city>/dealers/<cdp_code>/
```

### 5.2 The sentinel homes (no file is ever lost)

The data is honest about gaps (`PROGRESO.md`: municipality resolution 85–93%, the rest
ingested with `municipality NULL`, **not discarded**). The tree mirrors that honesty:

| Missing level | Sentinel dir | Why it exists |
|---|---|---|
| `comarca_id` NULL | `<prov>/_sin-comarca/` | comarca is nullable in the schema by design (`migrations/0001`) |
| `municipality_code` NULL | `<prov>/<com>/_sin-municipio/` | the 7–15% un-resolved long-tail (POIs w/o postcode) |
| province present, nothing else | `<prov>/_sin-comarca/_sin-municipio/dealers/<code>/` | province is **always** resolvable (`code[:2]`) |
| national platform/org | `_platforms/` / `_orgs/` (province `00`) | no province by nature (ontology D-13) |

Province is **never** missing — it is the first two digits of the `cdp_code` and the INE
invariant (`province_code = municipality_code[:2]`, `ARCHITECTURE.md`). So the *shallowest*
any entity sits is `<prov>/_sin-comarca/_sin-municipio/dealers/<code>/` — always at least
province-addressed, the mandate's minimum ("por provincia").

### 5.3 Re-geocoding moves the folder deterministically

When the long-tail geocoder (`engine/geo/geocode.py`) later resolves a `NULL` municipality
to a real one, the entity's bundle **moves** from `_sin-municipio/` to the real city dir.
The move is a pure function of the new geo + the unchanged `cdp_code`; a `git mv` preserves
history. The `cdp_code` never changes, so all references (manifest, DB FK, API URL) stay
valid — only the *shelf* changes, never the *identity*. This is why identity (code) and
location (path) are deliberately decoupled (§3 law, §4.2).

---

## 6. Config-as-registry (law #4) — the declarative tables that drive the engine

The engine is generic; the *knowledge* lives in versioned registries under
`config/registries/`. Each is JSON (machine-diffable, validated against a JSON Schema in
`config/schemas/`). The Recon census (`SOURCES_ES.md`) and the Tier-1 registry
(`00-TIER1-REGISTRY.md`) are the *human* source of truth; these JSONs are their
*machine-executable* projection.

### 6.1 `platforms_es.json` — the harvester-driving platform table

The single registry that turns `00-TIER1-REGISTRY.md`'s tables into runnable config. One
row per platform; `tier1` decides which code tree + runner + raw store apply (§3.1).

```jsonc
{
  "schema_version": 1,
  "platforms": [
    {
      "key": "autoscout24",
      "display": "AutoScout24.es",
      "kind": "plataforma",              // ontology kind
      "tier1": false,                    // → sources/long_tail/aggregators/, cheap loop
      "cdp_code": "CDP-ES-00-XXXXXXXX",  // national platform entity (province 00)
      "defense": "none",                 // is-antibot class → tier floor (defense_routing.json)
      "min_tier": 0,
      "surface": "next_data",            // data-layer surface (02-ENGINE law #1)
      "entrypoint": "https://www.autoscout24.es/lst",
      "recipe": "sources/long_tail/aggregators/recipes/autoscout24.yaml",
      "es_inventory_snapshot": 278584,   // 2026-06-12 photo; re-derived at harvest (drift is law)
      "attribution": "dealer",           // JSON-LD Organization+PostalAddress (GOLD)
      "verified_live": "2026-06-12",
      "status": "active"
    },
    {
      "key": "coches_net",
      "display": "coches.net",
      "kind": "plataforma",
      "tier1": true,                     // → platforms/_tier1/coches_net/, gated runner
      "cdp_code": "CDP-ES-00-YYYYYYYY",
      "defense": "adevinta_lambda_edge",
      "min_tier": 1,
      "surface": "json_api",
      "entrypoint": "https://ms-mt--api-web.spain.advgo.net/search",
      "recipe": "platforms/_tier1/coches_net/recipe.yaml",
      "es_inventory_snapshot": 248648,
      "attribution": "dealer",
      "spend_gated": false,              // API answers curl; no residential needed yet
      "shares_recipe_family": "adevinta",// coches.net + milanuncios + fotocasa one family
      "verified_live": "2026-06-12",
      "status": "active"
    }
  ]
}
```

The runner does `for p in platforms_es.json: route(p)` — `tier1` selects the world, `recipe`
points at the bundle, `defense`+`min_tier` feed the router (`02-SCRAPING-ENGINE §3`). Adding
Spoticar is one row (`tier1:true, spend_gated:true, defense:akamai`) + a
`platforms/_tier1/spoticar/` bundle — **zero engine code touched.**

### 6.2 `sources_es.json` — the long-tail discovery registry

One row per discovery source from the census (DGT CAT, AEDRA, Páginas Amarillas, OSM,
OEM locators…). Drives `discover_loop.py`. Fields: `key`, `adapter`
(`sources/long_tail/registries/dgt_cat.py`), `kind_yield` (the `entity.kind` it produces,
e.g. `desguace`), `declared_count` (for VAM), `legal_truth` (bool — DGT CAT is the only
`status=active` desguace truth, ontology D-5), `verified_live`. This is the machine form
of `SOURCES_ES.md` + `ORQUESTACION.md §"Orden de batalla por ROI"`.

### 6.3 `cms_families_es.json` — the family-keyed recipe multiplier

The census's highest-leverage long-tail idea ("clasificar webs por CMS/DMS → receta por
familia", `SOURCES_ES.md §9`, `02-SCRAPING-ENGINE §9.2`): dealers on the same CMS/DMS share
**one** parameterized recipe template. This registry maps a CMS signature → a template
recipe + the per-dealer params it needs.

```jsonc
{
  "families": [
    { "key": "motorflash_microsite",
      "detect": ["powered by Motorflash", "/concesionario/{slug}/coches-segunda-mano/"],
      "template": "config/recipe_templates/motorflash.yaml",
      "params": ["dealer_slug", "dealer_id"],
      "drains_estimated": "thousands of OEM/dealer microsites" }
  ]
}
```

One template + N param rows ⇒ N dealer recipes generated, not hand-written. The generated
per-dealer `recipe.yaml` still lands in each entity's bundle (§4.1) carrying a
`derived_from_family` provenance pointer, so it is self-describing and individually
healable.

### 6.4 The other registries (one concern each, law #6)

| File | Drives | Source of truth |
|---|---|---|
| `oem_brands_es.json` | OEM locator adapters + `_orgs/` OEM roots | census §3.3, ontology §2.1/§2.11 |
| `chains_es.json` | chain mono-sitemap harvest + `_orgs/` chain roots + branch `org_id` | census §3.5, ontology §2.12 |
| `rentacar_brands_es.json` | the `rent_a_car_vo` allow-list that overrides platform seller labels | ontology D-6 |
| `auction_operators_es.json` | `subasta` operators + physical centers | ontology §2.7 |
| `defense_routing.json` | `defense → tier floor` map | `02-SCRAPING-ENGINE §3` `DEFENSE_FLOOR` |

Each is validated on load against `config/schemas/<name>.schema.json`; a malformed registry
fails closed (the engine refuses to start on an invalid table — input validation at the
system boundary, global coding doctrine).

---

## 7. Raw store layout & the eviction boundary (law #5)

```
data/                              [GITIGNORED — entirely]
├── ES/<cdp_code>/raw/             long-tail dealer crude (HTML/JSON snapshots)
│   └── 2026-06-12T.../page-*.json
├── _tier1/<platform>/raw/         Tier-1 crude (SEPARATE subtree, §3.1)
├── geo/                           INE source spreadsheets / geocode caches
└── probe/                         is-antibot probe captures, fingerprint self-tests
```

- **Keyed by `cdp_code`**, mirroring the served bundle — the crude for entity X is always
  `data/ES/<X.cdp_code>/raw/`, a pure function of the code (no slug guessing; the current
  `data/ES/<slug>/raw/` `[VERIFIED]` migrates to code-keyed in §11).
- **Tier-1 crude is a separate subtree** (`data/_tier1/`) so the long-tail eviction sweep
  (LRU over `data/ES/`) never touches Tier-1 crude, and a Tier-1 quarantine never touches
  long-tail crude (§3.1, §3.4 guard #1).
- **Eviction (`evict.py`)** removes `raw/` after the 3 hard gates (`docs/workflows/README.md
  §FASE 5`: VAM TRUSTWORTHY + recipe committed + counts square), writes `tombstone.json`
  into the entity bundle (versioned), and updates `state/capacity-ledger.json` (gitignored).
  **It can never reach `recipe.yaml`/`config.yaml`/`manifest.json`** — those live in
  `countries/` (versioned), a different tree entirely from `data/` (gitignored). The
  physical separation makes "evict crude" structurally incapable of "lose recipe".
- **Eviction PINS the crude that a live TRUSTWORTHY verdict needs to replay `[adversarial GAP-35]`.**
  V5 §7 makes fabrication/staleness detection work by **replaying** a verdict's `evidence_uri →
  data/probe/<blobhash>` artifact — which is exactly what capacity eviction would delete. So
  `evict.py` **MUST skip any blob referenced by `evidence_uri` of a non-expired TRUSTWORTHY verdict**
  (a small, bounded pinned set — only the latest live verdict per subject pins). Reproducibility comes
  in **two distinct flavors that this resolves**: *reproducibility-from-RECIPE* (law #5 — re-run the
  recipe; survives eviction but CANNOT detect a fabricated COUNT, it re-runs the same path that
  produced it) and *reproducibility-from-ARTIFACT* (V5 §7 — replay the pinned blob; the only thing
  that catches a fabricated count). The pinned blob releases the instant its verdict **expires** (then
  replay correctly falls back to a live re-fetch, the spend already acknowledged at P11). The artifact
  survives exactly as long as the verdict it proves.

---

## 8. Versioned vs gitignored — the exhaustive disposition table (law #7)

Every path's git disposition, declared. This is the canonical reference the `.gitignore`
implements.

| Path | Disposition | Rationale |
|---|---|---|
| `engine/**`, `sources/**`, `platforms/**` | **versioned** | the code — durable |
| `countries/ES/**/{config,recipe}.yaml` | **versioned** | identity + the recipe asset (mandate: "recetas guardadas") |
| `countries/ES/**/{manifest,tombstone}.json` | **versioned** | harvest proof + proof-of-life (KB-sized, durable) |
| `config/registries/**`, `config/schemas/**`, `config/recipe_templates/**` | **versioned** | config-as-registry |
| `migrations/**`, `services/**`, `ops/**`, `tests/**`, `docs/**` | **versioned** | schema, API, operation, tests, docs |
| `README/CLAUDE/PLAN/PROGRESO.md`, `pyproject.toml`, `requirements.txt`, `.env.example` | **versioned** | governance + reproducibility |
| `data/**` | **gitignored-ephemeral** | raw crude, evicted by capacity, fully re-derivable from recipe |
| `state/**` | **gitignored-ephemeral** | volatile ledgers (capacity, spend, run, tier1-blocked) |
| `.env`, `.env.*` (except `.env.example`) | **gitignored-secret** | DSN, proxy creds, solver keys — never committed |
| `**/__pycache__/`, `*.pyc`, `.venv/`, `.pytest_cache/`, `node_modules/`, `*.log` | **gitignored-noise** | build/runtime artifacts |

The current `.gitignore` `[VERIFIED]` already ignores `data/`, `.env*` (keeping
`.env.example`), `state/`, `*.log`, caches. The **delta this design adds** is the explicit
`data/_tier1/` reasoning (covered by `data/`) and `state/` sub-files (covered by `state/`)
— so the existing `.gitignore` is already correct for the new tree with no edit required
for the ephemeral/secret classes. The one **addition** to consider: ensure
`countries/ES/**/manifest.json` and `tombstone.json` are **not** caught by any future broad
`*.json` ignore (they must stay versioned) — pin this with a `!countries/**` un-ignore if a
broad rule is ever added. Documented here so it is never accidentally regressed.

---

## 9. GitHub classification & repository hygiene

How the repo presents on GitHub `main` (the mandate's "clasificarlo en GitHub TODO").

### 9.1 Top-level legibility

A visitor landing on the repo root sees, in order: `README.md` (what + status), the
governance trio (`CLAUDE/PLAN/PROGRESO`), then the **eight functional top-levels** each
with a one-line purpose — `engine/` (the machine), `sources/` (long-tail discovery),
`platforms/` (Tier-1, separated), `countries/` (the served geo catalog), `config/` (the
registries), `services/` (the live API), `ops/` (how it runs), `docs/` (the architecture).
The structure *is* the documentation: the separation of concerns is visible from the file
listing alone.

### 9.2 Directory READMEs at the boundaries

Three `README.md` anchors mark the load-bearing boundaries (and only these — no README
sprawl):
- `platforms/_tier1/README.md` — states the separation contract (§3) so no one ever adds a
  long-tail source here.
- `countries/ES/README.md` — explains the geo addressing (§5) + the `_platforms`/`_orgs`
  sentinels so the tree is self-navigating.
- `config/registries/README.md` — the registry catalog (§6) so config edits are guided.

### 9.3 Commit & branch discipline (inherited, restated for this tree)

Conventional Commits (global doctrine). This pillar's work commits under `chore(arch)` /
`refactor(repo)` / `feat(scale)` as appropriate. The big structural move (§11) is a single
reviewable `refactor(repo): geo-hierarchical recipe tree + Tier-1 separation` commit with
the migration script included, so the reshape is auditable and reversible in one revert.

### 9.4 The CI structural guard (the separation as a test)

`tests/structure/test_separation.py` `[NEW]` asserts the invariants of §3, run in CI on
every push:
1. No module under `sources/` imports anything under `platforms._tier1` (and vice-versa).
2. No `recipe.yaml` under `countries/ES/<NN>-*/.../dealers/` has `tier1: true`.
3. No `recipe.yaml` under `platforms/_tier1/` has `tier1: false`.
4. Every `dealers/<code>/` dir name matches `^CDP-ES-\d{2}-[0-9A-HJKMNP-TV-Z]{8}$` (the
   `codes.py` Crockford-base32 alphabet) and its `{NN}` equals the parent province dir's
   `{NN}`.
5. Every `recipe`/`adapter` path referenced in `config/registries/*.json` exists on disk.

A red guard blocks the merge. The owner's "separación absoluta" becomes a machine-checked
property, not a hope.

### 9.5 Tests mirror the engine

`tests/` mirrors `engine/` package-for-package (`tests/engine/fetch/test_router.py` …) plus
`tests/fixtures/` (golden samples referenced by `recipe.yaml heal.reference_sample`) and the
`tests/structure/` guards. Coverage target per global doctrine (80%); the deterministic
engine is the high-value test surface (the Tier-1 adapters are integration-tested against
recorded fixtures, never live, to keep CI hermetic).

---

## 10. Code moves this reorganization forces (grounded, not abstract)

The reshape relocates existing `[VERIFIED]` files into the new tree. Each move is a `git mv`
(history preserved) + an import-path update; **no logic changes in this pillar** (logic is
the other pillars' job).

| Current path `[VERIFIED]` | Target path | Why |
|---|---|---|
| `services/api/codes.py` | `engine/identity/codes.py` | identity is engine-core, not an API detail; the API imports it |
| `pipeline/verify.py` | `engine/verify/vam.py` | VAM is engine-core (used by discover + ingest + Tier-1) |
| `pipeline/geo.py`, `pipeline/geocode.py` | `engine/geo/resolve.py`, `engine/geo/geocode.py` | geo resolution is engine-core |
| `pipeline/ingest.py` (delta parts) | `engine/delta/engine.py` | the delta engine is the crown jewel — promote it |
| `pipeline/recipe.py` | `engine/recipe/` (loader/schema) | recipe handling is engine, recipes are data |
| `pipeline/sources/base.py` | `sources/base.py` | the SourceAdapter contract roots the long-tail tree |
| `pipeline/sources/dgt_cat.py`, `osm.py` | `sources/long_tail/registries/`, `…/osm/` | classify discovery adapters by modality |
| `pipeline/sources/oem_*.py` | `sources/long_tail/oem/` | OEM locator adapters grouped |
| `pipeline/sources/autoscout24.py` | `sources/long_tail/aggregators/autoscout24.py` | OPEN aggregator (not Tier-1) |
| `scripts/migrate.py`, `load_geo.py` | `ops/migrate.py`, `ops/load_geo.py` | operational tooling → `ops/` |
| `scripts/as24_*.py`, `scale_as24.py`, `seed_pilot.py` | `ops/runners/` or deleted post-generalization | one-off scale scripts fold into the loop |
| `countries/ES/recipes/CDP-ES-*.yaml` (262) | `countries/ES/<prov>/<com>/<city>/dealers/<code>/recipe.yaml` | §11 geo migration |

> The `pipeline/` package name retires in favor of `engine/` + `sources/`; the
> `__init__.py` docstring's phase narrative `[VERIFIED]` moves to `engine/README.md`. This
> is a rename + reclassify, executed once, behind the §11 migration script so it is
> mechanical and reversible.

---

## 11. The deterministic migration: flat → geo-hierarchical (executable plan)

The one irreversible-feeling change made safe. Current state `[VERIFIED]`: **262 flat
recipes** at `countries/ES/recipes/CDP-ES-{NN}-{b32}.yaml`, all `source: autoscout24`,
province codes spanning 01–50 (counted this session: 68×`28`, 30×`08`, 30×`29`, 17×`46`,
13×`30`, …). Target: each under its geo path. The migration is a **pure function of data
already present** — the province is in the filename, the rest comes from the DB row.

### 11.1 Algorithm (`ops/migrate_recipes_to_geo.py`, `[NEW]`)

```
for each countries/ES/recipes/<CODE>.yaml:
    prov = CODE[7:9]                                   # the {NN} segment (e.g. "28")
    row  = db.entity_by_cdp_code(CODE)                 # geo + kind + is_tier1 + org_id
    if row.is_tier1:                                   # (none today; future-proof)
        dest = platforms/_tier1/<platform_name>/recipe.yaml
    elif row.kind in {plataforma, oem_vo_portal}:
        dest = countries/ES/_platforms/<CODE>/recipe.yaml
    else:
        prov_dir = f"{prov}-{slug(province_name[prov])}"
        com      = slug(comarca_name(row.comarca_id)) or "_sin-comarca"
        city     = slug(municipality_name(row.municipality_code)) or "_sin-municipio"
        dest = f"countries/ES/{prov_dir}/{com}/{city}/dealers/{CODE}/recipe.yaml"
    git_mv(src, dest)                                  # preserves history
    write(dirname(dest)/config.yaml, entity_descriptor(row))   # §4.1
    # manifest.json/tombstone.json already exist in data/ → relocate proofs alongside
verify: count(recipes after) == 262 ; no file lost ; every dest matches the §9.4 regex
commit: refactor(repo): geo-hierarchical recipe tree + per-entity bundles
```

### 11.2 Why this is safe (reversibility + verification)

- **`git mv`** preserves every recipe's history; a single `git revert` of the migration
  commit restores the flat layout exactly (reversible, per the autonomy doctrine — a
  reversible reshape proceeds without asking; only the *irreversible* needs a gate).
- **Pure function of existing data** — no new facts invented; the placement reads only the
  `cdp_code` (on disk) + the DB row (live). If a `cdp_code` has no DB row (orphan recipe),
  it lands in `countries/ES/_unmatched/<CODE>/` and fires a `longtail:migration` alert —
  honest, never silently dropped (anti-hallucination doctrine).
- **VAM on the move**: `count(after) == count(before) == 262` and every path matches the
  structural regex (§9.4) is the migration's own acceptance gate — the same quorum
  discipline the data pipeline uses, applied to the filesystem reshape.

### 11.3 Forward state (post-migration)

After §11 the repo is at the §2 canonical tree: long-tail recipes geo-addressed in
per-entity bundles, the Tier-1 tree scaffolded (`platforms/_tier1/<name>/` with a README
and the first hunted recipes), `config/registries/` driving the loops, `engine/` holding
the generic machine, `ops/` holding the runners. The 262 AS24 recipes become 262 bundles
under their true provinces/cities; new sources (coches.net Tier-1, OEM VO portals, the
long-tail registries) drop into their declared homes without a single structural decision
left to improvisation — **the organization is now a closed, total, self-enforcing system,
which is exactly what the mandate demanded.**

---

## 12. Honest residuals (no whitewashing)

1. **The geo tree depth (province/comarca/city) inflates path length** for 262→tens of
   thousands of entities. Mitigated by the sentinel dirs (§5.2) keeping depth bounded and by
   the fact that the filesystem is the *secondary* index (PG is primary); browsing is by
   path, querying is by DB. Accepted: the mandate explicitly demands the geo hierarchy.
2. **`comarca` is sparsely populated in INE** (nullable by design, `migrations/0001`); many
   entities will sit under `_sin-comarca/`. This is honest (the data is genuinely
   comarca-less for much of Spain), not a defect — the level exists for the comarcas that
   do resolve.
3. **`config.yaml` duplicates DB fields** (a denormalization: identity lives in both PG and
   git). Deliberate — git must be browsable/forkable without the DB (mandate: "cualquiera
   pueda retomarlo"). The DB is authoritative; `config.yaml` is a committed projection
   regenerated by discovery, never hand-edited.
4. **The `engine/`+`sources/` rename touches every import** in `pipeline/` and `scripts/`
   `[VERIFIED present]`. Real churn, done once behind §11, mechanically, with the import
   rewrite scripted and the test suite as the regression net. Not deferred, not half-done —
   but flagged as the largest mechanical change this pillar implies.
5. **Tier-1 bundles are scaffolded empty** until `WF-TIER1-HUNT` lands each recipe
   (`ORQUESTACION.md`). This doc creates the *homes* (`platforms/_tier1/<name>/` per the
   registry, §3) and the contract; it does not fabricate recipes it has not hunted
   (anti-stub). An empty Tier-1 bundle with only a `README` + `recipe.yaml: {status:
   hunting}` is the honest state, not a placeholder pretending to work.

---

## 13. Summary — the organization in one screen

- **Two worlds, separated absolutely** (law #1): the OPEN long-tail (`sources/` code +
  geo-addressed recipes + `data/ES/` crude + cheap loop) and the hard-defense Tier-1
  (`platforms/_tier1/<name>/` bundles + `data/_tier1/` crude + gated runner), sharing **no**
  code, recipe, raw store, runner, ledger, or alert origin — enforced by path, `.gitignore`,
  runner imports, and a CI guard (§3).
- **Geo is the long-tail axis** (law #2): `countries/ES/<prov>/<com>/<city>/dealers/<code>/`,
  deterministic from the `cdp_code` + INE backbone, with sentinel homes so no file is ever
  lost (§5).
- **The `cdp_code` is the universal filesystem key** (law #3): one entity ⇒ one code ⇒ one
  directory ⇒ four files (`config/recipe/manifest/tombstone`) — the atom of organization
  (§4).
- **Config is a versioned registry** (law #4): `config/registries/*.json` (platforms,
  sources, OEM, chains, rentacar, auctions, CMS families, defense routing) drive a generic
  `engine/`; adding a platform is a registry row + a bundle, never an engine edit (§6).
- **Raw crude is gitignored & evictable; the recipe is the durable git asset** (law #5),
  physically separated so eviction can never lose a recipe (§7, §8).
- **Every path has a declared git disposition** (law #7), and the whole reshape from
  today's flat 262-recipe reality is a single, reversible, VAM-gated migration (§8, §11).

This is the repository as a **closed, total, self-enforcing organization**: every artifact
has exactly one deterministic home, the two worlds cannot bleed into each other, and the
structure itself documents and defends the mandate.
