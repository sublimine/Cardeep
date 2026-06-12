# CARDEEP — Architecture Overview

> **The system at a glance.** CARDEEP is a live, verified database holding 100% of
> Spain's car points-of-sale — from the giant marketplace to the lost mountain garage —
> with all their inventory in real time, served by an API with full delta (additions,
> removals, price/photo changes, complete history), every dealer uniquely coded and
> ordered country → province → comarca → city, every recipe saved, every source
> self-healing, and the hard-defense Tier-1 platforms separated absolutely from the rest.
>
> **This document is the map.** It states the system in one screen, shows how the pillars
> fit, names the permanent systems, draws the two execution planes, fixes the Tier-1 /
> long-tail boundary, and renders the whole machine as one text diagram. It is the entry
> point to the architecture corpus; the executable plan that builds it is
> [`docs/MASTER_PLAN.md`](../MASTER_PLAN.md).
>
> **This corpus SUPERSEDES the first-pass** `docs/ARCHITECTURE.md` (data-layer sketch),
> `docs/ORQUESTACION.md` (orchestration sketch), and `docs/workflows/README.md` (atom-level
> F3 design). Those remain readable for migration history; where they disagree with a pillar,
> the pillar governs.
>
> **Marking discipline (inherited from every pillar):** every load-bearing fact is
> `[VERIFIED]` (read from repo/DB/live this session) or `[ASSUMED]` (design judgment). No
> placeholders.

---

## 0. The mandate, in one paragraph

A LIVE, VERIFIED database holding, structured to the last atom, **100% of Spain's car
points-of-sale**: official dealerships, used-car traders, garages, scrapyards, rent-a-car
selling ex-fleet, auctions, importers, the OEM used-vehicle portals, **and the giant
marketplaces themselves**. For EACH entity: find it, extract ALL its stock, serve it in a
live API with full delta and complete history, recipe saved, ordered by
country/province/comarca/city with a unique code per dealer. If a source fails, an alert
fires with the EXACT origin, it self-repairs, and CARDEEP never falls. Tier-1
(hard-defense platforms) separated ABSOLUTELY from the rest. Cheap/massive work uses local
LLMs; expensive intelligence only decides. Everything to GitHub `main`, documented.

---

## 1. The system on one screen

```
                              ┌───────────────────────────────────────────┐
   181-source census ───────▶ │  DISCOVER  (S-DISCOVER)                    │  finds entities
   (docs/research/SOURCES_ES) │  source adapters → entity + cdp_code + geo │  → denominator
                              └─────────────────────┬─────────────────────┘
                                                    │  (one immutable cdp_code per POS)
   00-TIER1-REGISTRY ───────▶ ┌─────────────────────▼─────────────────────┐
   (platforms + walls)        │  HARVEST  (S-INVENTORY)                    │  extracts stock
   02-SCRAPING-ENGINE ──────▶ │  tiered fetch (T0 curl_cffi→T1 stealth→T2  │  → numerator
   (the fetch engine)         │  spend) · data-layer surface · facet-drain │
                              └─────────────────────┬─────────────────────┘
                                                    │  raw crude → recipe (the durable asset)
   03-DATA-MODEL ───────────▶ ┌─────────────────────▼─────────────────────┐
   (PostgreSQL 16 backbone)   │  INGEST  (delta engine)                    │  NEW/GONE/Δprice/
                              │  INSERT-new + close-gone, append-only log  │  Δphoto/Δkm + history
                              └─────────────────────┬─────────────────────┘
                                                    │  every count gets a verdict
   05-VERIFICATION-VAM ─────▶ ┌─────────────────────▼─────────────────────┐
   + V1..V6 (deep validator)  │  VERIFY  (VAM → Inquisition → Publish-Gate)│  nothing TRUSTWORTHY
                              │  ≥2 orthogonal paths · landed-count primary│  without quorum;
                              │  · capture-recapture denominator · gate    │  confess the gap
                              └─────────────────────┬─────────────────────┘
                                                    │  only TRUSTWORTHY is served
   06-RESILIENCE-OPS ───────▶ ┌─────────────────────▼─────────────────────┐
   (watchdog + self-repair)   │  SERVE  (S-API, FastAPI + asyncpg)         │  live + delta + geo
                              │  /entities /platforms /orgs /geo /delta    │  + verification meta
                              └─────────────────────┬─────────────────────┘
                                                    │  source fails → exact-origin alert →
   04-ORCHESTRATION ────────▶   S-HEALTH watchdog → auto-repair ladder → park-with-exact-wall
   (the control plane)          (rate-governor is THE bottleneck; the API never falls)

   07-COVERAGE-STRATEGY  =  the order this whole machine runs in (€0 first, platforms wholesale,
                            capture-recapture closes the denominator, 52/52 provinces sealed)
   08-REPO-ORGANIZATION  =  where every artifact lives on disk (geo tree + Tier-1 separated world)
   T08-local-llm         =  the engine that powers the cheap/massive classify·parse·dedup stage
```

---

## 2. The nine pillars and how they fit

The architecture is nine pillars on three axes — **what exists** (recon), **how it is built**
(machine), and **how it is run/proven** (operation/coverage) — plus deep sub-pillars under
verification and tooling.

| # | Pillar | Axis | Owns | Hands the next pillar |
|---|---|---|---|---|
| **00** | [Tier-1 Platform Registry](00-TIER1-REGISTRY.md) | recon | the definitive live-verified registry of every car platform serving Spain (23 platforms + 4 B2B/auction), each with defense stack, data-layer surface, attribution, free-vs-spend verdict | *what to attack and in what order* → 02, 04, 07 |
| **01** | [Entity Ontology](01-ENTITY-ONTOLOGY.md) | recon | the 11 entity kinds with hard boundaries, the platform-as-entity + dual-membership model, the `cdp_code` identity/dedup model, chain-vs-branch fix | *the taxonomy + identity contract* → 03 |
| **02** | [Scraping Engine](02-SCRAPING-ENGINE.md) | machine | the 3-tier fetch ladder (curl_cffi → Scrapling/patchright → Decodo+Hyper sensors), per-defense routing, the versioned recipe system, self-healing | *the fetch engine the governor wraps* → 04, 06 |
| **03** | [Data Model](03-DATA-MODEL.md) | machine | the PostgreSQL 16 schema (entity graph + org layer + platform_listing edge + partitioned vehicle/event tables + auction overlay), migrations 0005–0012, the API contract | *the storage every module writes to* → all |
| **04** | [Orchestration](04-ORCHESTRATION.md) | machine | the control plane: two planes, Redis-Streams job substrate, the per-source **rate-governor** (the true bottleneck), anti-collision, cost-router, scheduler | *the spine that invokes 02 + writes 01 + lands in 03* |
| **05** | [Verification (VAM)](05-VERIFICATION-VAM.md) | operation | the threat model (12 ways a number lies), VAM quorum, the Inquisition, capture-recapture denominator, the publish-gate | *nothing serves unless TRUSTWORTHY* → V1..V6 deepen this |
| **06** | [Resilience & Ops](06-RESILIENCE-OPS.md) | operation | the watchdog, exact-origin alerting, recipe-drift detection, circuit breakers, auto-repair ladder, graceful degradation | *"a source fails → alert → self-repair → never falls"* |
| **07** | [Coverage Strategy](07-COVERAGE-STRATEGY.md) | operation | the A-to-Z roadmap to 100%: 7 segments, denominator-by-capture-recapture, numerator-wholesale-first, ROI order R0–R8, per-province seal gates | *the executable order the whole machine runs in* |
| **08** | [Repo Organization](08-REPO-ORGANIZATION.md) | machine | the on-disk tree, the absolute Tier-1/long-tail separation, config-as-registry, the geo-hierarchical per-entity bundle, the flat→geo migration | *where every artifact lives and why nothing collides* |

**Deep sub-pillars** (under `verification/` and `tooling/`) take individual concerns to
maximum rigor and explicitly extend pillar 05 and the cost doctrine:

| Doc | Deepens | Core contribution |
|---|---|---|
| [V1 — Denominator Proof](verification/V1-DENOMINATOR-PROOF.md) | 05 §6 | Chapman + log-linear capture-recapture **with confidence intervals**, official anchors (DGT/DIRCE) as hard floors/ceilings, the falsification rule that REFUTES a bare denominator |
| [V2 — Completion Proof](verification/V2-COMPLETION-PROOF.md) | 05 §8 | the binary 5-gate per-entity `COMPLETED` definition + **acceptance-sampling** (LQAS) proof of a population "20k done" claim |
| [V3 — Inquisition](verification/V3-INQUISITION.md) | 05 §5 | the formal adversarial chain: default-REFUTED, producer-exclusion, the numeric independence gate `INDEP≥2`, five orthogonal lenses |
| [V4 — Gestionador](verification/V4-GESTIONADOR.md) | 05 §7–8 + 06 | the lie/gap **detection manager**: 7 detectors, the managed-item state machine, the quarantine⇄publish gate |
| [V5 — Ledger/API](verification/V5-LEDGER-API.md) | 05 §8 + 03 §7 | the **DB-enforced quorum** (generated `quorum_n`/`family_n` + CHECK), hash-chained audit trail, publish-gate as a bound view, verification API |
| [V6 — Statistical Rigor](verification/V6-STATISTICAL-RIGOR.md) | 05 §3,§6 | the math spine: AQL sample sizing, SPRT early-stop, Wilson/Chapman CIs, **precision-vs-recall measured apart** |
| [T08 — Local LLM](tooling/T08-local-llm.md) | 04 §3 | the cheap/massive engine pick: **vLLM + Qwen3.5-4B** (batch) / llama.cpp+Gemma-4 (CPU) / Ollama (dev), `guided_json` schema-constrained |

> **One reconciliation the reader must know up front:** pillars 05 and V1–V6 are **one
> verification system at two depths**, not two systems. 05 is the architecture (threat model,
> the four machines, the gate); V1–V6 are the rigorous mechanisms (the exact estimators,
> sample sizes, DB-enforced quorum, audit chain). They agree on the soul ("never serve a lie,
> confess the gap, verify by an orthogonal path") and on the substrate (`verification_verdict`,
> `entity_source`, `alert`, `source_health`). Where they differ in detail — the verdict enum,
> the migration number, the freshness column — the [MASTER_PLAN](../MASTER_PLAN.md) §"Contradictions"
> reconciles each explicitly. The deep docs govern the *mechanism*; pillar 05 governs the *frame*.

---

## 3. The permanent systems (S-*)

CARDEEP is not a script that is run; it is a set of permanent systems that run themselves.
Each maps to a pillar and to live or to-be-built code.

| System | What it does | Pillar | Live state `[VERIFIED]` |
|---|---|---|---|
| **S-GEO** | INE backbone: 52 provinces / ~8.1k municipalities + name→code resolution | 03 | ✅ working (`pipeline/geo.py`, `migrations/0001`) |
| **S-CODE** | `cdp_code` immutable deterministic mint (domain>cif>name+muni+addr); the universal key | 01, 03, 08 | ✅ working (`services/api/codes.py`) |
| **S-DISCOVER** | source adapters → entities + multi-source provenance + inline VAM | 01, 04 | ✅ working (`pipeline/discover.py`; DGT + 8 OEM + OSM + AS24) |
| **S-INVENTORY** | harvest → recipe → ingest with the delta engine | 02, 03, 04 | ✅ working per-dealer (`pipeline/ingest.py`, AS24); ~22–39k vehicles, 212–262 dealers |
| **S-VERIFY / VAM** | count-quorum; nothing TRUSTWORTHY without ≥2 orthogonal paths + landed-count primary | 05, V1–V6 | ✅ inline (`pipeline/verify.py`); deep validator + Inquisition = to build |
| **S-API** | serves entity / inventory / delta / geo / platform / org (consistent `{ok,data,error,meta}`) | 03, 06 | ✅ skeleton (`services/api/main.py`); full F6 contract = to build |
| **S-HEALTH** | per-source watchdog + exact-origin alert + auto-repair ladder + circuit breakers | 04, 06 | ⏳ tables live (`migrations/0004`); nothing writes them yet — F7 |
| **S-TIER1** | hard-defense platforms, code/recipe/raw/operation **separated absolutely** | 00, 02, 08 | ⏳ in recipe-hunt; **0 Tier-1 entities live** — F5 |

The mandate's two hardest promises live here: **"the source fails → alert with exact origin →
self-repairs → CARDEEP never falls"** is S-HEALTH (pillar 06), and **"100% of the points of
sale"** is the denominator that S-VERIFY closes by capture-recapture (V1).

---

## 4. The two planes (cost doctrine, mechanized)

> *Massive and cheap → deterministic or local LLM. Expensive intelligence → only to decide and
> hunt.* (`ORQUESTACION.md`, `CLAUDE.md` — the mandate's spend doctrine.) Three routers, one
> principle: **spend the minimum that is correct** — the fetch router on *transport*, the
> rate-governor on *throughput*, the cost-router on *cognition*.

```
┌──────────────── DETERMINISTIC PLANE (€0, scales linearly) ──────┬──── INTELLIGENCE PLANE (€€, decides) ────┐
│  pipeline/ Python  +  local LLM (vLLM/Qwen3.5-4B, T08)           │  agent fleets (the Workflow tool)        │
│   • discover · scrape · parse · classify-kind · dedup · geo      │   • WF-TIER1-HUNT  (one agent per giant; │
│   • ingest (delta) · verify (count-quorum VAM)                   │      hunt the data-layer recipe or       │
│   • the rate-governor, the watchdog, the scheduler              │      report the exact wall that needs    │
│  ↳ everything massive: ~90% of all work, €0                      │      spend)                               │
│                                                                 │   • WF-INQUISITION (adversarial          │
│                                                                 │      re-derivation; refuter info-starved)│
│                                                                 │   • hard identity disambiguation         │
└───────────────────────────────┬─────────────────────────────────┴───────────────────┬──────────────────────┘
                                 ▼                                                      ▼
                    PostgreSQL cardeep-pg :5433  ◀────────────────────  FastAPI live API (S-API)
                    (entity · org · vehicle · platform_listing · vehicle_event ·
                     verification_verdict · source_health · alert — migrations 0001→00NN)
```

The intelligence plane is invoked by **exactly two triggers**: (a) a Tier-1 source whose
data-layer recipe is unknown (`WF-TIER1-HUNT`), and (b) a consequential count that must be
refuted by a fresh independent method (`WF-INQUISITION`). Everything else — including parsing,
classifying `kind` (the fix for the `ingest.py:52` mis-typing bug), and deduping — runs
deterministic + local-LLM at €0. Every cloud-agent invocation and every Tier-2 fetch writes
to `state/spend-ledger.json`; a per-front budget cap trips an alert before overspend.

---

## 5. The absolute Tier-1 / long-tail separation

The owner's repeated, explicit demand: the hard-defense platforms share **nothing** with the
rest. Separation is enforced on **six independent axes** (pillar 08 §3) so the failure of any
one does not collapse it.

| Concern | LONG-TAIL world (OPEN) | TIER-1 world (hard defense) |
|---|---|---|
| **Adapter code** | `sources/long_tail/**` | `platforms/_tier1/<name>/adapter.py` |
| **Recipe store** | `countries/ES/<prov>/.../dealers/<code>/recipe.yaml` (+ `_platforms/` for OPEN platforms) | `platforms/_tier1/<name>/recipe.yaml` (co-located bundle) |
| **Raw crude** | `data/ES/<code>/raw/` | `data/_tier1/<name>/raw/` (separate subtree) |
| **Runner / loop** | `ops/runners/{discover,harvest}_loop.py` (cheap, €0) | `ops/runners/tier1_run.py` (gated, may spend) |
| **Registry** | `config/registries/sources_es.json` | `config/registries/platforms_es.json` (`tier1:true` rows) |
| **Spend / block ledger** | n/a (€0 by definition) | `state/spend-ledger.json`, `state/tier1-blocked.json` |
| **Alert origin prefix** | `origin = "longtail:<source_key>"` | `origin = "tier1:<platform>"` |
| **DB flag** | `entity.is_tier1 = false` | `entity.is_tier1 = true` |

A subtlety the naive split gets wrong (08 §3.1): **Tier-1-ness is a *defense* axis,
platform-ness is an *entity-kind* axis.** A 700k-listing OPEN platform (AutoScout24) is a
first-class `kind=plataforma` entity served under `countries/ES/_platforms/`, but its **code
lives in `sources/long_tail/aggregators/`** and it runs on the cheap loop — because it has no
wall. A 50k OEM portal behind Akamai (Spoticar) is `is_tier1=true`, lives in
`platforms/_tier1/`, and runs only on the gated runner. **The served catalog is geo/kind-shaped;
the code tree is defense-shaped.** A CI structural guard (08 §3.4, 09 §9.4) makes the boundary a
tested invariant, not a convention.

---

## 6. The model decisions that make the mandate expressible

Three structural failures in the first-pass system are fixed by three model decisions (pillars
01 + 03):

1. **Mis-typing at ingest** (`ingest.py:52` hardcodes `kind='concesionario_oficial'` for every
   AS24 dealer) → the **11-kind ontology** + a **type-resolution precedence ladder** (registral >
   OEM-locator > legal-census > curated-brandlist > LLM-classifier > platform-label-advisory) +
   `entity.kind_source` recording which rung decided.
2. **No platform as an entity, no "same car ∈ platform AND dealer"** → the platform is **both a
   first-class entity** (`kind ∈ {plataforma, oem_vo_portal}`) **and a channel**: a vehicle is
   *owned* by exactly one selling entity, and has **0..M platform memberships** via the
   `platform_listing` edge. This is the single most important modeling decision — it makes dual
   membership expressible.
3. **Chains vs branches conflated** (`cadena` was a leaf kind) → an **`organization` layer** +
   `entity.org_id` FK; each branch keeps its true leaf kind AND points to its chain, so
   "Flexicar's national stock" and "how many points of sale does AUTO1 operate" become one
   indexed predicate.

The identity spine under all three: **one immutable `cdp_code` per real point of sale**,
deterministic over canonical identity (bare-domain > CIF > name+municipality+address), so
re-discovery by any source converges to one code — and the same code is the directory name of
that entity's on-disk bundle (08), the partition-aware DB key (03), and the idempotency key of
every job (04).

---

## 7. Live ground truth (the floor this builds on)

`[VERIFIED 2026-06-12 against the running DB / repo]`:

- **PostgreSQL 16.14** in Docker (`cardeep-pg :5433`); extensions `btree_gin`/`pg_trgm`/`pgcrypto`
  available, **PostGIS not** (geo uses lat/lon bbox + Haversine).
- **~12,862 entities** (garaje 7200 · compraventa 2753 · concesionario_oficial 1617 · desguace
  1292) — **4 kinds only**, the ontology's 11 kinds + platform + org rows are the backlog.
- **~39,068 vehicles**, ~41,165 delta events, **262 recipes** (all AS24, flat at
  `countries/ES/recipes/`), 52/52 provinces touched.
- **0 `is_tier1` entities, 0 platform entities, 0 `geo_comarca` rows, 0 `source_health`/`alert`
  rows** — the four biggest open gaps (Tier-1, platform-as-entity, the comarca grid, the live
  watchdog).
- Migrations `0001`–`0004` live and additive/reversible; the documented scar: **138 AS24 dealers
  lost to throttling under 4× parallel load** — the reason the rate-governor (04 §5, 06 §7) is the
  centerpiece, not a worker count.

The architecture is **additive evolution of this live floor**, never a destructive recreate: the
12,862 entities, 39k vehicles, and 41k events are preserved by in-place migration.

---

## 8. How to read the corpus

1. **Start here** (this file) for the shape.
2. Read [`MASTER_PLAN.md`](../MASTER_PLAN.md) for the executable A-to-Z plan with binary gates,
   the build sequence, the cost gates, the reconciled contradictions, and the definition of
   100% done.
3. Drill into a pillar (00–08) when you build that subsystem; into V1–V6 / T08 when you build the
   deep validator or the local-LLM layer.
4. The first-pass `ARCHITECTURE.md` / `ORQUESTACION.md` / `workflows/README.md` are **superseded**
   — read them only for migration history.

> **The promise this architecture keeps:** every kind of point of sale defined to the last atom,
> the platform a first-class entity, the same car a member of both its platform and its dealer,
> chains and branches distinguished, a denominator that is a *measured* fraction not a guess,
> Tier-1 separated absolutely, an identity that survives cross-source overlap, a verifier that
> confesses every gap rather than serve a single lie, and a control plane where a broken source
> fires an exact-origin alert, self-repairs, and the API never falls.
