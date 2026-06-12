# CARDEEP — 07 · Coverage Strategy & Executable Roadmap to 100% of Spain

> **Pillar document.** The A-to-Z phased plan with **binary gates** that closes
> *every* segment (platforms, OEM networks, long-tail retail, garages, desguaces,
> rent-a-car, auctions, importers) and *every* geography (province by province) of
> Spain's car points-of-sale to a defined, honest **100% sealed**. It defines:
> the **denominator-closure method** (capture-recapture / Chapman), the **cost
> gates** (what needs owner spend), the **ROI order** (zero-cost open first, then
> gated), the **rate-limit-aware sequence** (the true bottleneck), and the
> **per-segment / per-province KPIs** with a refutable definition of "done".
>
> This doc is the *coverage* layer. It sits on top of, and routes work into, the
> other pillars — it invents no new schema, no new engine, no new ontology; it
> **orchestrates** them toward the mandate's denominator. Read first (anchors):
> - `docs/research/SOURCES_ES.md` + `SOURCES_ES_raw.json` — the 181-source census
>   (the *supply* of discovery sources and their verified volumes/defenses).
> - `docs/architecture/00-TIER1-REGISTRY.md` — the platform universe (the *numerator*
>   supply: where inventory is harvested wholesale).
> - `docs/architecture/01-ENTITY-ONTOLOGY.md` — the *denominator* taxonomy (what we
>   are counting and how each type is discovered) + the `cdp_code` identity model
>   that makes capture-recapture possible.
> - `docs/architecture/02-SCRAPING-ENGINE.md` — the fetch engine + per-defense tiers
>   that this strategy's cost gates spend against.
> - `docs/ARCHITECTURE.md` — the data layer (`entity`, `entity_source`, `vehicle`,
>   `verification_verdict`, `source_health`) this strategy reads and writes.
> - `docs/ORQUESTACION.md` + `PLAN.md` — the F0–F8 phase frame this doc makes
>   executable, and the cost doctrine ("masivo+barato → determinista/local;
>   inteligencia cara → solo decide").
>
> **Anchor reality, live-verified this session [VERIFIED against the running DB,
> 2026-06-12]:** 12,862 entities (garaje 7200 · compraventa 2753 ·
> concesionario_oficial 1617 · desguace 1292), 39,068 vehicles, **262 dealers with
> harvested stock**, 41,165 delta events, 262 committed recipes, 52/52 provinces
> touched, **0 `is_tier1` entities**, **0 `geo_comarca` rows loaded** (the comarca
> grid the mandate demands is an *empty table* today — flagged as a real gap, §9).
>
> Marking discipline: every claim is **[VERIFIED]** (read from repo/DB/census this
> session) or **[ASSUMED]** (inferred, not re-derived). No placeholders, no stubs.

---

## 0. The thesis in one paragraph

100% is not a number you reach by scraping harder; it is a **denominator you close
and then cover**. Cardeep closes the denominator by *capture-recapture over
orthogonal discovery sources* (the same dealer seen by OSM **and** Páginas Amarillas
**and** AutoScout24 lets you *estimate the dealers no source has seen yet*), and
covers the numerator by *harvesting inventory wholesale through platforms first*
(one AutoScout24 recipe attributes 278k cars to thousands of dealers at €0) and
*own-site harvest by CMS/DMS family second*. The work is sequenced not by appetite
but by the **one real bottleneck — source rate-limits** (PROGRESO already proved
"138 dealers fell to AS24 throttling under 4× load" `[VERIFIED]`). Every segment and
every province has a **binary gate** and an **honest KPI**: a province is *sealed*
when its capture-recapture coverage estimate clears a threshold **or** the residual
is a declared, caused gap (no web / no online stock / spend-gated wall) — never a
silent shortfall. Zero-cost open sources are drained to exhaustion before a single
euro of residential-proxy spend is authorized.

---

## 1. The two closure problems (denominator vs numerator), stated precisely

The mandate is "100% of Spain's car points-of-sale **and** all their stock." That is
**two** closure problems with **two** different methods and **two** different KPIs.

| | **DENOMINATOR closure** | **NUMERATOR closure** |
|---|---|---|
| Question | Have we found *every entity*? | Have we extracted *every car* of each found entity? |
| Unit | `entity` (the point of sale) | `vehicle` per `entity` |
| Method | capture-recapture over orthogonal sources (§3) | per-entity exhaustive harvest via recipe (§4 of `02-SCRAPING-ENGINE.md`) |
| "Done" test | `coverage = found / estimated-true ≥ gate`, residual caused | `Σ harvested == declared count` per entity (VAM count-quorum, §4.2) |
| Failure mode | **silent under-count** (a dealer no source lists) | **silent under-drain** (pagination cap hides stock) |
| Live state | 12,862 found vs ~44k floor / 50–90k ceiling `[VERIFIED census §6]` | 262/12,862 entities harvested `[VERIFIED DB]` — numerator barely begun |

**The strategic asymmetry that orders everything:** the denominator is closed by
*cheap, broad, orthogonal discovery* (registries, directories, OEM APIs, OSM — most
€0). The numerator is closed by *expensive, deep, per-entity harvest*. But the
numerator has a **shortcut the denominator lacks**: a handful of **platforms**
(AutoScout24, coches.net, wallapop…) each carry the stock of *thousands* of entities,
dealer-attributed. So the optimal play is: **harvest platforms wholesale (closes most
of the numerator AND discovers entities as a side-effect), then close the denominator
residual with cheap discovery, then mop up the numerator long-tail by own-site
family-recipe.** This is why "platforms wholesale first" is the ROI spine (§5).

---

## 2. The segment map — every segment, its denominator source-of-truth, its closure path

Eleven entity kinds (`01-ENTITY-ONTOLOGY.md §2`) collapse into **seven coverage
segments** by *how they are closed* (same closure method = same segment). For each:
the **denominator truth** (the count we measure coverage against), the **primary +
orthogonal discovery sources** (for capture-recapture), the **numerator harvest
surface**, the **cost class**, and the **binary seal gate**.

> Denominator floors below are the **verified** census numbers (`SOURCES_ES.md §6`,
> re-confirmed this session); ceilings are the registral/Places upper bounds. The
> *true* denominator per segment is the capture-recapture estimate (§3), which lives
> between floor and ceiling and is re-estimated as sources are added.

### SEG-1 · Desguaces (CAT scrapyards) — `desguace`
- **Denominator truth.** DGT CAT FeatureServer = **1,292** `[VERIFIED exact, census §7
  + DB]`. This is a *legal census* — the rare segment where the true denominator is
  **known exactly**, not estimated. Coverage is therefore `found/1292`, not a CR estimate.
- **Discovery sources (orthogonal).** Primary: DGT CAT (truth). Cross-check / enrich:
  DesguacesDirecto 1,386, DesguacesOficiales ~2,049, AEDRA 615, SIGRAUTO 595+25,
  Opisto 449, AETRAC (Cataluña) 107–130 `[VERIFIED census §3.5]`.
- **Numerator surface.** Whole-car stock (v1) on own-web / car aggregators; parts on
  Opisto/Ovoko (v2, deferred per ontology §8). Most desguaces sell *few or zero* whole
  cars online — a legitimate **zero-inventory** state.
- **Cost class.** €0 (DGT is an open ArcGIS dump).
- **Seal gate (BINARY).** `entity` count for `kind=desguace, status=active` **== 1292**
  (already met `[VERIFIED]`) **AND** every directory desguace beyond the 1,292 ingested
  as `status=unverified` until CIF/geo-matched (ontology D-5), **AND** whole-car
  inventory attempted for the subset with an online stock signal. **State: denominator
  100% SEALED `[VERIFIED]`; numerator deferred (whole-car harvest not yet run).**

### SEG-2 · Official dealer networks — `concesionario_oficial` + `agente_oficial` + `oem_vo_portal`
- **Denominator truth.** FACONAUTO **2,018 franchised + 3,642 agentes** `[VERIFIED
  census §3.2]`. The franchised universe is **small and almost fully enumerable from
  OEM locator APIs** — this is the segment with the best free-discovery leverage.
- **Discovery sources (orthogonal).** OEM dealer-locator **JSON APIs without auth**
  (the gold): Kia 242, MG 212, BYD 106 `[VERIFIED]`; OEM network sitemaps: SEAT 166
  subsites, Skoda 215, Toyota 98 groups, Dacia ~150–200, Peugeot 275 `[VERIFIED census
  §3.3]`. Associations: FACONAUTO gateway, AMDA Madrid 147, Gremi BCN 693. Cross-confirm:
  PA "concesionarios" 11,202 (incl. multimarca noise), CNAE 4511. Live: 9 OEM adapters
  already built (kia/mg/byd/skoda/dacia/hyundai/mercedes/seat) `[VERIFIED DB
  entity_source: oem_* sources present]`.
- **Numerator surface.** VO (used) stock via **OEM VO portals** (renew ES-facet API,
  Das WeltAuto BFF, Spoticar Akamai, MB/BMW/Hyundai central) — dealer-attributed, so
  one portal harvest = N dealers' VO stock (the dual-membership of ontology §4).
- **Cost class.** Discovery €0 (OEM JSON). Numerator: renew/MB/BMW/Hyundai OPEN (€0);
  Spoticar Akamai = Tier-2 spend-gated (SEG-7).
- **Seal gate (BINARY).** Every OEM brand operating in ES has its locator ingested
  (per-OEM count VAM-verified vs the brand's own counter) **AND** the `agente_oficial`
  split applied (ontology D-3) **AND** each OEM-VO-portal harvested or its wall
  declared. Per-brand sub-gate: `db_count == locator_count` (the Kia precedent: 241 ES,
  1 Andorra excluded transparently `[VERIFIED PROGRESO]`).

### SEG-3 · Platforms / aggregators (OPEN) — `plataforma` (open sub-kind)
- **Denominator truth.** A *fixed, enumerable list* — there are ~15–20 platforms, not
  thousands. The denominator is "every platform in `00-TIER1-REGISTRY.md §1` with
  `is_tier1=false`." Closure = each becomes one `entity` row (`kind=plataforma`,
  province sentinel `00`, ontology D-13) with a committed recipe.
- **Discovery sources.** The registry itself (`00-TIER1-REGISTRY.md`). No CR needed —
  the universe is hand-enumerable and verified.
- **Numerator surface (the prize).** Each platform's data-layer surface: AS24
  `__NEXT_DATA__` (278k), autocasion GraphQL (123k), coches.com sitemap+`__NEXT_DATA__`
  (200k, decaying-open), motor.es listings (51k), Flexicar/OcasiónPlus/Autohero/Clicars/
  Crestanevada JSON-LD, renew ES-facet, Das WeltAuto/MB/BMW central. **Sum of OPEN
  free-now ≈ 700k+ listings drainable today with curl_cffi, €0 `[VERIFIED registry
  §1.1]`.** This single segment closes most of the national numerator.
- **Cost class.** €0 (Tier-0 curl_cffi). The highest-value-per-euro work in the project.
- **Seal gate (BINARY).** Each OPEN platform: (a) `entity` row minted, (b) recipe
  committed to `countries/ES/recipes/`, (c) full inventory drained via facet-partition
  (§4 below) with `Σ leaf-distinct == declared counter` (pagination VAM, scraping-engine
  §7), (d) every listing's selling dealer resolved to an `entity` + `platform_listing`
  edge (dual membership). **The dealer-attribution side-effect of this segment feeds
  SEG-4/5 discovery for free.**

### SEG-4 · Independent used-car trade — `compraventa` + `importador` + chains (`organization`)
- **Denominator truth.** PA "compraventa" **1,662** is the *floor*; true count is much
  larger (the long-tail is defined by platform presence, not directory listing).
  **CR estimate (§3) is the real denominator here** — this is the segment where
  capture-recapture matters most. Chains roll up via `organization` (Flexicar 175+,
  OcasiónPlus ~120, AUTO1/Clicars/Autohero, Crestanevada 32 `[VERIFIED]`).
- **Discovery sources (orthogonal — the CR substrate).** PA 1,662; OSM `shop=car`
  3,516; FSQ OS Places + Overture (permissive-license geo); **platform dealer-attribution
  (AS24 + coches.net + autocasion — the richest)**; registral CNAE 4519/4520; chain
  sitemaps. The orthogonality (a directory source vs a platform source vs a geo dump)
  is what makes the Chapman estimator valid (§3).
- **Numerator surface.** Heavily on aggregator platforms (so SEG-3 harvest *already
  captures most of it*) + own-web (CMS/DMS family recipe, §4).
- **Cost class.** €0 (open platforms + geo dumps + registries).
- **Seal gate (BINARY, per province).** CR coverage estimate ≥ gate (§6) **AND** every
  chain's branches enumerated under one `org_id` **AND** importadores resolved by
  classifier over already-ingested sellers (last-priority, ontology D-8).

### SEG-5 · Garages that sell — `garaje` (with `sells_cars` gate)
- **Denominator truth.** **The hardest and most over-collected segment.** CCAA workshop
  registries over-collect *every* workshop: RASIC 12,155, CyL ~6,714, CETRAA ~20,000,
  PA "talleres" 29,955, OSM `shop=car_repair` 7,847 `[VERIFIED census §3.4]`. The live DB
  has **7,200 garaje rows seeded from OSM with NO sells-cars filter** `[VERIFIED DB +
  ontology §2.4]` — the denominator is **inflated**. The *true* denominator is the
  **selling subset**, gated by `entity.sells_cars=true` (ontology D-4), which is **not
  yet populated**. So SEG-5's first job is **deflation, not inflation**: apply the
  sale-signal filter before measuring coverage.
- **Discovery sources.** CCAA registries (RASIC Socrata, CyL CSV, CETRAA gateway), PA,
  OSM — all over-collect. Sale-signal sources: presence on AS24/wallapop/milanuncios as a
  seller, "venta"/"compra-venta" on own site (classifier job).
- **Numerator surface.** Sparse — a few aggregator listings; many have zero online stock
  (a legitimate catalogued-not-harvested state, ontology §2.4).
- **Cost class.** €0 discovery; classifier = local LLM (ORQUESTACION cost doctrine).
- **Seal gate (BINARY).** `sells_cars` resolved for every `garaje` row (the gate that
  separates entity from non-entity geo-anchor) **AND** the selling subset's CR coverage
  ≥ gate. **Honest KPI: report the deflation** (7,200 → N selling) as a *correction*, not
  a loss — the mandate counts *points of sale*, and a pure workshop is not one.

### SEG-6 · Rent-a-car ex-fleet + auctions — `rent_a_car_vo` + `subasta`
- **Denominator truth.** **Curated lists, no census source.** Rent-a-car: ~10–15 brands
  (OK Mobility, Centauro, Record Go, Goldcar, Europcar Selección, Sixt, Enterprise…
  `[VERIFIED live, ontology §2.6]`). Auctions: BCA (4 physical centres), Autorola, Adesa
  `[VERIFIED, ontology §2.7]`. Small, hand-enumerable denominators.
- **Discovery sources.** Curated brand/operator allow-list (the *only* reliable type
  resolver — platforms mis-label OK Mobility as a concesionario, ontology D-6) +
  aggregator seller-name matching.
- **Numerator surface.** Rent-a-car: brand VO portal (own web) + aggregator brand
  profile. Auctions: time-boxed `auction_lot` overlay (v2 harvest; v1 = operators +
  centres as denominator, ontology D-7).
- **Cost class.** Rent-a-car €0 (open brand portals + curated list). Auctions: catalog
  pages partially open (Ayvens); full lot/bid data behind B2B login (credentials-gated,
  not spend-gated — a *different* gate, §7.3).
- **Seal gate (BINARY).** Every brand/operator on the curated list minted as an entity
  with correct `kind` (allow-list override applied) **AND** rent-a-car VO portals
  harvested **AND** auction operators + physical centres catalogued (lot-harvest deferred
  to v2 with declared scope).

### SEG-7 · Platforms (TIER-1, hard defense) — `plataforma` (`is_tier1=true`) + `oem_vo_hard`
- **Denominator truth.** Enumerable list (`00-TIER1-REGISTRY.md §1`, `is_tier1=true`):
  Wallapop ~750k, Milanuncios ~667k, coches.net 249k, coches.com 200k (decaying-open),
  Spoticar ~50k, + auction B2B (BCA/Autorola/CarNext/Ayvens). **Physically separated**
  into `countries/ES/_tier1/` — never shares recipe/raw/operation (mandate + ontology D-2).
- **Discovery sources.** The registry. Recipe-hunt is by **agent fleet** (WF-TIER1-HUNT),
  not deterministic — expensive intelligence (cost doctrine).
- **Numerator surface.** Internal APIs behind walls: wallapop `cars/search` v3 (app
  headers), Adevinta `advgo.net/search` POST (one recipe for coches.net + milanuncios +
  fotocasa + segundamano), Spoticar Akamai stock XHR.
- **Cost class.** **THE spend gate.** Residential ES proxies (Decodo) + sensor generation
  (Hyper Solutions) for Akamai/Imperva/PerimeterX; GeeTest solver for milanuncios; B2B
  credentials for auctions. **No Tier-2 component runs without owner per-source spend
  authorization** (scraping-engine §2 hard rule).
- **Seal gate (BINARY, per platform).** Reproducible recipe committed to `_tier1/` **OR**
  the *exact wall* declared in `state/tier1-blocked.json` (e.g. "Akamai `_abck`,
  sensor_data v3, ES residential required") — a parked wall with an exact cause **is a
  valid sealed state** (a declared gap, not a silent failure).

### Segment denominator board (the coverage scoreboard)

| Seg | Kinds | Denom. truth | Floor / ceiling | Found (live) | Cost class | Numerator shortcut |
|---|---|---|---|--:|---|---|
| SEG-1 | desguace | DGT CAT (exact) | 1,292 (exact) | **1,292 ✅** | €0 | own-web/parts(v2) |
| SEG-2 | conces_of + agente + oem_vo | FACONAUTO + OEM APIs | 2,018+3,642 / ~11k | 1,617 `[partial]` | €0 disc | OEM VO portals |
| SEG-3 | plataforma (open) | registry list | ~15 platforms | **0 entities ❌** | €0 | **IS the shortcut (700k)** |
| SEG-4 | compraventa + importador + orgs | **CR estimate** | 1,662 / long-tail | 2,753 `[partial]` | €0 | SEG-3 attribution |
| SEG-5 | garaje (sells_cars) | selling subset (CR) | ~30k over-collected → N | 7,200 `[inflated]` | €0 | sparse |
| SEG-6 | rent_a_car_vo + subasta | curated lists | ~15 + ~5 ops | **0 ❌** | €0/creds | brand portals / lots(v2) |
| SEG-7 | plataforma tier1 + oem_vo_hard | registry list | ~8 platforms | **0 ❌** | **SPEND** | internal APIs |

The board is the project's single coverage truth-table; every phase gate (§8) moves a
cell. Note the live reality it exposes: **the numerator giant (SEG-3) has zero entity
rows** — platforms are harvested *as a source* (262 dealers via `as24` provenance
`[VERIFIED]`) but the platform itself is not yet a first-class entity. Closing SEG-3 is
the highest-leverage open move.

---

## 3. Denominator closure — capture-recapture (Chapman), mechanized

The mandate's denominator ("100% of points of sale") is **unknowable a priori** — no
single source lists every dealer. Capture-recapture estimates the *unseen* population
from the *overlap* between independent sources, turning "how many are we missing?" from
a guess into a computed interval with a confidence band. This is the method `census §6`
names and `PLAN.md F8` defers to; here it is made executable.

### 3.1 The estimator (two-source Chapman, then k-source)

For two **independent** sources A and B over the same universe:
- `n_A` = entities seen by A, `n_B` = seen by B, `m` = seen by **both** (matched by
  `cdp_code` — the deterministic identity that makes "both" computable, ontology §6.2).
- **Chapman estimator** (bias-corrected Lincoln-Petersen):
  `N̂ = ((n_A + 1)(n_B + 1) / (m + 1)) − 1`
- **Variance / 95% CI** via the Chapman variance formula → report `N̂ ± 1.96·SE`.
- **Coverage of A∪B** = `(n_A + n_B − m) / N̂`.

The substrate **already exists and is populated**: `entity_source` records, per entity,
*which sources attested it* (`UNIQUE(entity_ulid, source_key)`) `[VERIFIED ARCHITECTURE
+ DB: osm 9956, dgt_cat 1292, oem_* …]`. `m` for any source pair is a single SQL join.
**No new infrastructure** — capture-recapture is a *query over `entity_source`*, run
per segment and per province.

### 3.2 Why orthogonality is the load-bearing assumption (and how we defend it)

Chapman assumes sources are **independent** (seeing a dealer in A doesn't change its
odds of being in B). Cardeep's source families are *deliberately orthogonal by
mechanism*:
- **Registral** (DGT, BORME, CNAE) — sees an entity because it *exists legally*.
- **Geo directories** (OSM, FSQ, Overture, PA) — sees it because it has a *physical
  location someone mapped*.
- **Platform attribution** (AS24, coches.net) — sees it because it *advertises stock*.
- **OEM locators** — sees it because it *holds a franchise*.

These capture-mechanisms are nearly independent (a dealer's legal registration is
uncorrelated with whether a hobbyist mapped it on OSM). **Violations we actively
guard:** two *directory* sources (PA + another yellow-pages clone) are **not**
orthogonal (both copy the same phone-book) → never paired in an estimate; the §3.3
multi-source model handles correlated sources by stratification. The estimator is run
**only on mechanism-orthogonal pairs/strata**, and the chosen pairs are recorded with
the estimate so the assumption is auditable.

### 3.3 k-source closure (the real model) and the per-province grid

Two sources give one estimate; Cardeep has *many*. The production method:
1. **Per segment × per province**, build the source-incidence matrix from `entity_source`
   (rows = entities, cols = orthogonal source families, cells = seen/not-seen).
2. Estimate `N̂` via **multiple orthogonal pairs** and reconcile (a sample-coverage /
   log-linear estimator over the incidence matrix is the v2 upgrade; v1 = the median of
   pairwise Chapman estimates over orthogonal pairs, with the spread as an uncertainty
   signal). Disagreement between pairs **is itself the alarm** that an orthogonality
   assumption is violated → investigate before trusting `N̂`.
3. **Coverage** = `found_in_province / N̂_province`. This is the per-province KPI (§6).
4. **Re-estimate on every new source ingest** — adding Overture to a province with only
   OSM+PA *shrinks the unseen estimate*; the denominator is a *living estimate that
   tightens as sources accumulate*, never a frozen guess.

### 3.4 The closure persistence (where the estimate lives)

Each estimate is written as a `verification_verdict` row (the VAM judge already in the
schema `[VERIFIED migrations/0004]`): `subject_type='coverage'`,
`subject_key='{segment}:{province}'`, `claim='denominator_coverage'`,
`primary_value=N̂`, `independent_values=[pairwise estimates]`, `divergence=spread`,
`verdict ∈ {TRUSTWORTHY|UNVERIFIED}`. So the coverage scoreboard is **queryable from the
same table that judges every other count** — one verification substrate, no parallel
truth. A province's seal gate (§6) reads exactly these rows.

---

## 4. Numerator closure — wholesale-first, then own-site by family

The numerator (every car of every entity) is closed in **three waves**, ordered by
cars-captured-per-unit-effort. Each wave's *mechanics* live in `02-SCRAPING-ENGINE.md`
(facet-partition §7, recipe system §9); here is the *coverage logic* of when each runs.

### Wave A — Platform wholesale (closes ~80% of the numerator at €0)

Harvest the OPEN platforms (SEG-3) by their data-layer surface. One AS24 recipe
attributes 278k cars to thousands of dealers; coches.com adds 200k; autocasion 123k.
**Because a platform lists the *same physical cars* many dealers also show on their own
sites, draining the platforms first captures the bulk of the national stock before a
single own-site is touched.** Dual-membership (`platform_listing` edge, ontology §4)
records *which* platform each car came from, so cross-platform dedup (by seller +
photo-hash, ontology §4.2) yields the *union* (real stock), not the sum.

- **Coverage accounting.** A dealer is "numerator-covered via platform" when its
  platform-attributed stock count is VAM-stable across two consecutive harvests (no
  churn beyond live drift). This is *most* compraventas and many concesionarios for free.
- **Rate-limit reality.** Platform harvest is the **bottleneck** (§7). One platform =
  one host = one rate-limit budget; you cannot parallelize *within* a platform past its
  throttle (PROGRESO: AS24 4× load → 138 dealers lost `[VERIFIED]`). You parallelize
  *across* platforms (AS24 ∥ coches.com ∥ autocasion ∥ renew — different hosts).

### Wave B — OEM VO portals (closes the official-network numerator at €0)

renew (ES-facet API), Das WeltAuto (BFF), MB/BMW/Hyundai central. Each portal =
dealer-attributed VO stock for a whole brand network. Closes SEG-2's numerator and
*discovers* the participating dealers as a side-effect (the "free network census",
census finding #2).

### Wave C — Own-site by CMS/DMS family (closes the residual long-tail)

The entities **not** fully covered by Waves A/B — those with own-site stock not mirrored
on any platform. The lever (census §9, scraping-engine §9.2): **classify dealer websites
by CMS/DMS family → one recipe per family parameterized per dealer.** Dealers on the same
DMS (e.g. Motorflash microsites) share *one* recipe template draining *thousands* of
sites. This is where the long-tail "lost mountain garage" with its own little website is
closed — cheaply, by family, not artisanally per site.

- **Coverage accounting.** A dealer is "numerator-covered via own-site" when its own-site
  harvest VAMs stable AND its delta vs its platform-attributed stock is reconciled (own
  stock ⊇ platform stock, modulo timing). Many garajes (SEG-5) have **no** own-site stock
  → a legitimate **zero-inventory sealed** state (catalogued, not harvested).

### 4.1 The numerator seal per entity (binary)

An entity is **numerator-sealed** when **one** of:
1. Its full stock is harvested and VAM-stable (`Σ harvested == declared`, count-quorum), OR
2. It is verified to have **no online stock** (no platform presence + no own-site feed) —
   a *caused zero*, recorded as `verification_verdict(verdict=TRUSTWORTHY, claim='no_online_stock')`, OR
3. Its only stock is behind a **declared spend/credentials wall** (SEG-7) — parked with
   the exact wall.

All three are *honest sealed states*. The forbidden state is **unknown** (not harvested,
no verdict) — that is an open cell, never reported as covered.

---

## 5. ROI order — the zero-cost-first attack sequence

The cost doctrine (`ORQUESTACION` + scraping-engine §2: "cheapest tier that works",
"masivo+barato → determinista") dictates a strict order: **exhaust every €0 source before
authorizing one euro of spend.** The sequence below is the ROI-ranked attack plan; each
rung is gated (you don't open rung N+1's spend while rung N has €0 work left).

| Rung | Work | Cost | Why this order | Closes |
|--:|---|---|---|---|
| **R0** | Desguaces (DGT) | €0 | exact denominator, already done | SEG-1 ✅ |
| **R1** | OEM locator APIs (all brands) | €0 | tiny enumerable universe, JSON no-auth | SEG-2 denom |
| **R2** | **Platforms OPEN — AS24 → coches.com → autocasion → motor.es** | €0 | **700k cars + dealer attribution in ~4 recipes** — the single highest-ROI move | SEG-3 + most of SEG-4 numerator |
| **R3** | OEM VO portals (renew/DasWeltAuto/MB/BMW/Hyundai) + chains (Flexicar/OcasiónPlus/Autohero/Clicars) | €0 | dealer-attributed network stock; Motorflash early as dealer-discovery multiplier | SEG-2 numer + SEG-4 chains |
| **R4** | Long-tail geo discovery (OSM ∪ FSQ ∪ Overture ∪ PA ∪ CCAA registries) + CR estimate | €0 | closes the SEG-4/SEG-5 *denominator*; permissive-license geo replaces Places (legal) | SEG-4/5 denom |
| **R5** | Own-site harvest by CMS/DMS family | €0 (CPU) | the long-tail numerator residual, one recipe per family | SEG-4/5 numer |
| **R6** | `sells_cars` deflation + classifier typing (garaje/importador) | €0 (local LLM) | corrects the inflated denominator; resolves thin types | SEG-5 + importador |
| **R7** | Rent-a-car curated brands + auction operators (catalog) | €0 / creds | curated lists; auctions = catalog now, lots v2 | SEG-6 |
| **R8** | **TIER-1 walled — Adevinta family (advgo API) → Wallapop (app headers) → Akamai/CF (spend)** | **SPEND** | only after €0 exhausted; one Adevinta recipe = 4 platforms | SEG-7 |

**The hinge is R2.** Everything before it is cheap setup; R2 captures the inventory mass
*and* discovers the dealer long-tail as a free side-effect, which makes R4's denominator
estimate dramatically tighter. R8 (spend) is **last** and **per-source authorized** —
the owner sees the exact wall and the exact cost (`state/spend-ledger.json`, scraping-engine
§5) before a euro moves.

### 5.1 Cost gates — exactly what needs owner spend (and what does not)

| Needs spend? | Item | Trigger | Est. cost basis `[VERIFIED scraping-engine §2]` |
|:--:|---|---|---|
| **NO** | Everything in R0–R7 | open/permissive sources, curl_cffi, local LLM | €0 |
| **NO** | Tier-1 *whose internal API is open* | wallapop `cars/search` (header-gated, not paid), advgo POST (token via 1 browser hit) | €0 if no residential needed |
| **YES** | Residential ES proxies (Decodo) | geo-sensitive walls (milanuncios "fuera de ES dispara muro"), IP-reputation walls | ~$2–8.50/GB |
| **YES** | Sensor generation (Hyper Solutions) | Akamai `_abck` (Spoticar), Imperva hardened (coches.com if it flips), PerimeterX | per-call metered |
| **YES** | CAPTCHA/token solvers (2Captcha/CapSolver) | GeeTest (milanuncios), interactive DataDome/Turnstile | per-solve |
| **CREDS** | B2B accounts (not money, but authorization) | BCA/Autorola/Ayvens full lot data | dealer account provisioning |

The spend gate is **per-source**: authorizing Spoticar's Akamai sensor does not authorize
milanuncios' GeeTest. Each parks in `state/tier1-blocked.json` with its exact wall until
its own authorization lands (scraping-engine §2 hard rule).

---

## 6. The "100% sealed" definition and the honest KPIs

"100%" is defined **refutably**, per segment and per province, so it can never be
quietly faked. Two coverage dimensions (denominator, numerator), each with a binary seal.

### 6.1 Per-province seal (the mandate's "province by province")

A province `P` is **DENOMINATOR-SEALED** when, for **every** segment present in `P`:
```
coverage(seg, P) = found(seg, P) / N̂(seg, P)  ≥  GATE(seg)
   OR  the shortfall (N̂ − found) is a DECLARED, CAUSED gap
       (source-with-no-province-data | spend-gated-wall | known-empty-segment)
```
with `N̂` the capture-recapture estimate (§3) carrying a `verification_verdict` of
`TRUSTWORTHY` (its orthogonal pairs agreed). `GATE(seg)` is segment-specific because
segments have different closability:

| Segment | `GATE` | Rationale |
|---|--:|---|
| SEG-1 desguace | **1.00** (exact) | legal census = exact denominator, no estimate |
| SEG-2 official | **0.98** | OEM locators are near-complete; 2% = locator drift |
| SEG-3/7 platforms | **1.00** (enumerated) | hand-enumerable list, not estimated |
| SEG-4 compraventa | **0.90** | long-tail; 90% of CR estimate is the honest ceiling of free discovery |
| SEG-5 garaje | **0.85** (of selling subset) | hardest to enumerate; gate is on the `sells_cars` subset, not raw workshops |
| SEG-6 rentacar/subasta | **1.00** (curated) | curated lists are complete by construction |

A province is **NUMERATOR-SEALED** when every numerator-relevant entity in it is
numerator-sealed (§4.1: harvested-stable OR caused-zero OR declared-wall).

A province is **SEALED** = denominator-sealed AND numerator-sealed. **Spain is sealed
when 52/52 provinces are sealed** (the mandate's "50/50 provinces or declared gap"
`[VERIFIED PLAN F8]` — corrected to **52**, the real INE province count `[VERIFIED DB:
52 provinces]`).

### 6.2 The honest KPI panel (per segment × per province, queryable)

Reported numbers, each with its derivation so none is a vanity metric:
- **`found`** — `entity` rows for the segment in the province `[from DB]`.
- **`N̂` + 95% CI** — capture-recapture estimate `[from verification_verdict]`.
- **`coverage` = found/N̂** — the headline, with its CI band.
- **`numerator_sealed_pct`** — fraction of entities with a numerator verdict (any of the
  three honest states), NOT just harvested — a caused-zero counts as sealed.
- **`harvested_pct`** — fraction actually drained (the *subset* of sealed that has stock).
- **`declared_gap`** — the residual, *itemized by cause* (no-province-data, spend-wall,
  empty-segment). **A gap with a cause is honest; a gap without one is a bug.**
- **`vam_status`** — the segment-province's `verification_verdict` verdict.

The panel's iron rule (from `PLAN` operating rules + the doctrine): **report the gap, not
a rounded-up coverage.** SEG-5's deflation (7,200 → N selling garajes) is reported as a
*correction with cause*, never hidden as a loss. A REFUTED VAM blocks the seal — exactly
as PROGRESO already practices ("OSM long-tail VAM REFUTED honesto" `[VERIFIED]`).

### 6.3 What "100%" honestly is (and is not)

- **IS:** every *findable* point of sale found (CR coverage ≥ gate), every *harvestable*
  car harvested (VAM-stable), every residual *declared with an exact cause*.
- **IS NOT:** a claim that literally zero dealers in Spain are unknown (unprovable) or
  that C2C private sellers are enumerated (out of scope, attributed to platform sentinel,
  ontology §4.3). The honesty is in the **caused residual**, not in a fabricated 100.00%.

---

## 7. Sequencing for the real bottleneck — source rate-limits

The bottleneck is **not** compute, code, or denominator size — it is **how fast each
source lets us pull before it throttles**. PROGRESO proved it twice: "138 dealers fell to
AS24 throttling under 4× load" and "harvest is the bottleneck (source rate-limit), not the
system — scale by number of sources in parallel" `[VERIFIED]`. The sequence respects this.

### 7.1 The parallelism law: across hosts, never within a host past throttle

- **One source = one host = one rate budget.** Concurrency is a *per-source tuned knob*
  (scraping-engine §6: "concurrency is a tuned per-source knob, not a global max"), set
  below the throttle threshold, with token-bucket pacing + jitter.
- **Throughput scales by adding *orthogonal hosts*, not by hammering one.** AS24 ∥
  coches.com ∥ autocasion ∥ renew ∥ OSM-dump run fully parallel (5 different
  infrastructures, 5 independent budgets). This is why R2+R3 platforms are attacked
  *concurrently across platforms* but *serially-paced within* each.
- **Tier-1 residential egress lifts the per-host ceiling** (more IPs = more parallel
  budget) — but only behind the spend gate (§5.1).

### 7.2 The realistic critical path (effort-ordered, not calendar-promised)

The doctrine forbids time-as-a-metric ("la velocidad no es métrica"). The path is
ordered by *dependency and throttle*, not dated:
```
R0/R1 (instant, done/near-done: DGT + OEM locators — small, fast, no throttle)
  └─► R2 platforms OPEN  ── THROTTLE-BOUND, longest single stretch ──┐
        (AS24 278k + coches.com 200k + autocasion 123k, paced per-host)
        run R3 OEM-VO + chains CONCURRENTLY (different hosts) ───────┤
  └─► R4 geo-discovery (dump-based: OSM/FSQ/Overture = bulk, fast; PA/CCAA = paced)
        → first CR estimates land → denominator tightens ───────────┤
  └─► R5 own-site family harvest (parallel across CMS families, paced per-domain)
  └─► R6 deflation + classifier (local, compute-bound not throttle-bound — fast)
  └─► R7 rent-a-car/auction catalog (small, paced)
  └─► R8 Tier-1 (spend-gated; Adevinta one recipe → wallapop → Akamai last)
```
R2 is the long pole; everything that can run beside it (R3 concurrent hosts, R4 dumps,
R6 local compute) is parallelized to hide its latency. R8 waits for both €0 exhaustion
and owner authorization.

### 7.3 The two non-money gates (don't confuse with spend)

- **Robots / ToS gates** — motor.es `/vercoche/*` robots-disallowed (harvest listings
  only, scraping-engine §O.3); Google Places ToS forbids indexing (use FSQ/Overture
  instead, census refutation #4); Facebook Marketplace no public surface (out of scope,
  registry §3.7). These are **respected, not spent past** — a declared scope boundary.
- **Credentials gates** — BCA/Autorola/Ayvens full lot data needs a B2B dealer account
  (authorization, not euros). Parked as `needs B2B credentials`, distinct from spend.

---

## 8. The executable roadmap — phases with binary gates

This maps the ROI rungs (§5) onto the F-phase frame (`PLAN.md`), making each gate a
*verifiable predicate over the DB / verification_verdict*, not a vibe. Phases F0–F3 are
**done** `[VERIFIED PROGRESO]`; the table below is the forward plan with corrected,
binary gates.

| Phase | Rung(s) | Scope | **BINARY GATE (verifiable predicate)** | Cost |
|---|---|---|---|---|
| **F3.5 PLATFORM-AS-ENTITY** | R2 setup | Mint every OPEN platform as `kind=plataforma` entity (prov `00`); add `platform_listing` edge + `organization` layer per ontology §6.4 (a)(b)(c) | `SELECT count(*) FROM entity WHERE kind='plataforma'` ≥ 15 AND `platform_listing` table exists AND migration applied+rolled-back+re-applied clean | €0 |
| **F4a PLATFORM WHOLESALE** | R2 | Drain AS24 → coches.com → autocasion → motor.es; dual-membership recorded | Per platform: recipe committed + `Σ leaf-distinct == declared` (pagination VAM TRUSTWORTHY) + every listing's dealer resolved to entity | €0 |
| **F4b OEM-VO + CHAINS** | R3 | renew/DasWeltAuto/MB/BMW/Hyundai + Flexicar/OcasiónPlus/Autohero/Clicars; Motorflash dealer-discovery | Per source: harvest VAM-stable + chain branches under one `org_id` + per-brand dealer census reconciled | €0 |
| **F4c LONG-TAIL DENOMINATOR** | R4 | OSM ∪ FSQ ∪ Overture ∪ PA ∪ CCAA registries ingested; **first CR estimates** | Each new source ingested with provenance; CR `N̂` computed per segment×province with TRUSTWORTHY verdict (orthogonal pairs agree) | €0 |
| **F4d OWN-SITE FAMILY** | R5 | CMS/DMS classification → family recipes → residual own-site harvest | ≥1 province: numerator_sealed_pct ≥ gate (every entity harvested OR caused-zero OR declared-wall) | €0 |
| **F4e DEFLATE + TYPE** | R6 | `sells_cars` resolved for all garaje; classifier types importador/garaje-sells | `sells_cars IS NOT NULL` for 100% of `kind=garaje` AND deflation reported with cause | €0 |
| **F6 DELTA AT SCALE** | (cross) | delta engine proven on platform + own-site (already proven per-dealer) | Δ re-derived on a platform harvest + an own-site harvest with evidence | €0 |
| **F7 RESILIENCE** | (cross) | S-HEALTH: injected source failure → exact-origin alert → auto-repair | Inject a source fault → correct `alert` row with exact origin + auto re-route, no system fall | €0 |
| **F5 TIER-1** | R8 | Adevinta recipe (advgo) → wallapop → Akamai/CF, in `_tier1/` separated | Per platform: reproducible recipe in `_tier1/` + 2-way count + blind-sample field VAM, OR exact wall parked in `tier1-blocked.json` | **SPEND/creds** |
| **F8 SEAL 52/52** | all | per-province seal scoreboard; capture-recapture closure; honest report | 52/52 provinces SEALED (denom ≥ gate + numer sealed) OR declared caused gap per cell | €0 |

> F4a–F4e and F6/F7 run **concurrently where hosts differ** (§7.1); F5 (spend) is gated
> last; F8 is the rolling scoreboard that *closes* as the others land — a province seals
> the moment its cells clear, not in a big-bang at the end.

### 8.1 The immediate next move (grounded in the live gap)

The live DB has **0 platform entities** despite harvesting 262 dealers *through* AS24
`[VERIFIED]`. The single highest-leverage next action is **F3.5 → F4a**: make platforms
first-class entities and drain them wholesale. This converts the existing 262-dealer,
39k-vehicle proof into the 700k-listing national numerator at €0, and its
dealer-attribution side-effect tightens every province's denominator estimate (R4) for
free. Everything else (F4c discovery, F5 spend) is *downstream* of this move's leverage.

---

## 9. Honest residuals & confessed gaps (no makeup)

1. **`geo_comarca` is empty `[VERIFIED DB: 0 rows]`.** The mandate's grid is
   "province→**comarca**→city"; comarcas are loaded as a table but **zero rows**. The
   per-province seal (§6) is computable today; the **per-comarca** stratum the mandate
   names is **not** until the comarca grid is populated (INE/CCAA comarcal source).
   Stated, not hidden — this is a denominator-grid gap, not a coverage lie.
2. **Capture-recapture orthogonality is an assumption, not a proof.** §3.2 defends it by
   mechanism and guards correlated pairs, but a hidden correlation (two "independent"
   sources both sourced from a common upstream) would bias `N̂`. The mitigation —
   pairwise-estimate disagreement as an alarm — *detects* but does not *prevent* it. The
   estimate is honest-with-uncertainty, never presented as exact (except SEG-1 where the
   denominator is a legal census).
3. **SEG-5 (garaje) denominator is currently inflated and not yet deflated.** 7,200 rows,
   `sells_cars` unpopulated. Until R6 runs, SEG-5 coverage is *uncomputable* honestly
   (you cannot measure coverage of an undefined denominator). Flagged; the gate (F4e)
   blocks SEG-5 seal until deflation lands.
4. **Numerator is ~2% started.** 262/12,862 entities harvested `[VERIFIED]`. The strategy
   is sound and proven per-dealer (OK Mobility 78 cars, VAM TRUSTWORTHY `[VERIFIED]`), but
   the wholesale waves (A/B/C) are *designed here, not yet executed* — this is a roadmap,
   and the roadmap says so.
5. **Tier-1 totals are mostly `[ASSUMED]`** (Spoticar ~50k, wallapop ~750k vendor-claimed)
   — re-derived only when the spend-gated recipe lands. Coverage of SEG-7 is therefore
   estimated-against-an-estimate until then; reported as such.
6. **Auction lot harvest (v2) and desguace parts (v2) are out of v1 numerator scope**
   (ontology §8). v1 seals their *denominator* (operators/centres/CATs) and defers their
   *numerator* with declared scope — a deliberate boundary, not an omission.
7. **C2C private-seller volume (wallapop ~750k incl. private) is attributed to the
   platform sentinel, not enumerated as dealers** (ontology §4.3). Whether to fully
   enumerate private sellers is an **owner call**; the denominator counts *real points of
   sale*, so C2C is inventory-served, not a denominator gap.

---

## 10. Summary — the coverage strategy in one screen

- **Two closures, two methods:** denominator by **capture-recapture over orthogonal
  sources** (§3, computable today from `entity_source`); numerator by **wholesale-first
  harvest** (platforms → OEM-VO → own-site family, §4).
- **Seven segments**, each with a denominator truth, orthogonal discovery sources, a
  numerator shortcut, a cost class, and a **binary seal gate** (§2 board).
- **ROI order, €0 first** (§5): R0 desguaces → R1 OEM locators → **R2 OPEN platforms (the
  700k hinge)** → R3 OEM-VO/chains → R4 geo-discovery+CR → R5 own-site family → R6
  deflate/type → R7 rent-a-car/auction → **R8 Tier-1 (spend, last, per-source authorized)**.
- **Cost gates named exactly** (§5.1): everything €0 except residential proxies + sensor
  gen + solvers for the hard Tier-1 walls, each per-source spend-authorized; B2B
  credentials a distinct non-money gate.
- **Bottleneck = source rate-limit** (§7): parallelize across hosts, pace within each
  host below throttle; R2 is the long pole, everything beside it runs concurrent.
- **"100% sealed" is refutable** (§6): per segment×province, `coverage ≥ segment-gate` OR
  a **declared caused gap**; Spain sealed at 52/52 provinces; honest KPI panel reports the
  *caused residual*, never a rounded-up number.
- **Immediate move** (§8.1): mint platforms as entities + drain wholesale — converts the
  live 262-dealer proof into the national numerator and tightens every denominator
  estimate, at €0.

Every gate in this doc is a predicate over the live DB or `verification_verdict`; every
number is `[VERIFIED]` against the census/registry/DB or marked `[ASSUMED]`; every
residual is confessed with its cause. This is the executable path from 12,862 entities /
39,068 cars to a sealed, honest 100% of Spain.
