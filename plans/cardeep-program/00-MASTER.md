# CARDEEP — Institutional Program (A->Z)

> **North-star:** index, order, and locate the complete *digital footprint* of every car sale point in Spain — a national census so exhaustive, fresh, and provably honest that no human or AI could replicate it in years. **Scope is digital footprint only:** if it is not present online it is not in the inventory denominator; we find, extract, canonicalize, locate, certify, and serve everything that *is* online, for absolutely everyone, at **EUR0**. Each of the ten domains below is an individual institutional project with its own plan file, owner, and acceptance gate.

## The 10 domains (A->Z map)

| Domain | Mission | Next-level headline | Plan file |
|--------|---------|---------------------|-----------|
| **A. Discovery / Universe** | Find EVERY car sale point with a digital footprint in Spain (the denominator) and PROVE exhaustiveness. | Seal the national non-particular denominator to >=95% `coverage_lower` by closing the orthogonal-list gaps (DORK, REG/Axesor, Páginas Amarillas) and routing all 25 adapters through the audited `harvest_run` gate. | `01-discovery.md` |
| **B. Extraction / Scraping** | Extract each footprint's inventory at scale, fresh and resilient. | Wire the existing delta engine into all 38 wholesale connectors and stand the scheduler up as a persistent daemon so every digital footprint is captured, diffed, and freshness-tracked continuously at EUR0. | `02-extraction.md` |
| **C. Identity Resolution (entity)** | One real-world sale point = one canonical entity, without over-merging. | Serve a single transitive-closure dealer identity that fuses every VAM-verified merge edge-set (B1, deep-link, particular, beta-fingerprint, cross-source) behind one zero-false-positive code-unique-per-dealer contract. | `03-identity.md` |
| **D. Vehicle Canonicalization** | One physical car = one canonical vehicle across all listings and sources. | Lift cross-platform "same physical car" collapse from a single string/exact-attribute overlay to a pHash-backed strong-key resolver that closes the measured ~131.8K fuzzy over-count without a single false merge. | `04-vehicle.md` |
| **E. Geolocation** | Locate every entity and every car precisely (province/municipality/coordinates). | Drive non-particular municipality completeness from 85.79% toward the data-blocked floor (~90%) and add a CartoCiudad/Nominatim self-hosted fallback so every digitally-present entity with any geo signal is located, EUR0. | `05-geo.md` |
| **F. Data Quality & Truth** | Honest census: count what *is* (real sale points), never inflate; sanitation and data contracts. | Make every served number provably true: one canonical "sale point" definition, contract-gated ingestion, and continuous anomaly detection at EUR0. | `06-quality.md` |
| **G. Serving / API** | Serve the live census — fast, authenticated — as the single source of truth. | Turn the FastAPI census surface into a sub-50ms, fuzzy-searchable, materialized-view-backed serving layer that no human or competitor can match — at EUR0. | `07-serving.md` |
| **H. Product / Frontend** | A portal that orders and makes explorable the digital footprint of absolutely everyone. | Turn the census into a navigable national product: a real global vehicle/dealer search and a live 3D coverage map that proves "everyone, everywhere" at a glance. | `08-product.md` |
| **I. Trust & Certification** | Prove verifiably that the census is complete and honest (the seal). | Lift national MSE certified lower-bound coverage from 37.72% toward >=80% by widening orthogonal capture lists and tightening overlap, and make every seal byte cryptographically reproducible with provenance. | `09-trust.md` |
| **J. Ops / Observability** | Harvest continuously, watch freshness and health, with CI that classifies faithfully. | Make the census self-operating and self-healing: every silent or failing source surfaces one accurate, auto-resolving alert, and a single observable scheduler proves liveness so no point-of-sale silently rots undetected. | `10-ops.md` |

## Dependency graph & sequencing

The domains form a directed graph. Edges below read **"X depends on Y"** (Y must produce signal before X can reach its next-level headline). Cycles exist by design — the census is a closed loop where serving and quality feed back into discovery and identity — so sequencing is expressed as *waves* of dominant flow, not a strict topological order.

**Edge semantics (clarified post-review):** an edge `X ← Y` means X *reads signal from Y's **current** surface*, not that Y must be fully built before X starts. Serving, Quality and Ops already **exist** at baseline (the live FastAPI/DB surface, the `product_stats` path, the running schedulers), so an upstream domain consuming them (e.g. `Identity ← Serving`) is runtime data-flow, **not** a build cycle. Build order is the wave order below; each domain's *next-level* work layers on top of the existing surfaces. See **Post-review reconciliation** for the full resolution.

```
                 ┌─────────────────────────────────────────────┐
                 │                                             │
   A. Discovery ─┼──► B. Extraction ─► C. Identity ─► D. Vehicle │
        ▲        │         │              │             │       │
        │        │         ▼              ▼             ▼       │
        │        └──► E. Geo ◄──── F. Quality ◄─────────┘       │
        │                  │           │                        │
        │                  ▼           ▼                        │
        │              G. Serving ◄────┘                        │
        │                  │                                    │
        │     ┌────────────┼───────────────┐                    │
        │     ▼            ▼               ▼                     │
        └── I. Trust   H. Product      J. Ops ───────────────────┘
```

**Declared dependencies (per domain):**

- **A. Discovery** ← geo, identity, quality, extraction, trust, ops
- **B. Extraction** ← discovery, identity, vehicle, geo, quality, ops
- **C. Identity** ← extraction, vehicle, geo, quality, serving
- **D. Vehicle** ← extraction, identity, geo, quality, serving, discovery
- **E. Geo** ← extraction, identity, quality, serving
- **F. Quality** ← identity, vehicle, geo, serving, discovery, extraction
- **G. Serving** ← identity, vehicle, geo, quality, trust, discovery, ops
- **H. Product** ← serving, geo, vehicle, identity, quality, trust
- **I. Trust** ← discovery, identity, quality, serving, geo
- **J. Ops** ← discovery, extraction, quality, serving

**Execution waves (dominant flow, derived from the graph):**

1. **Wave 0 — Foundation (parallel):** A. Discovery and B. Extraction. These produce the raw denominator and the raw inventory; everything downstream is empty without them. Run their independent sub-streams in parallel (discovery list-building vs. connector wiring).
2. **Wave 1 — Canonicalization (parallel after Wave 0 has signal):** C. Identity and D. Vehicle. Identity collapses entities; Vehicle collapses physical cars. They share inputs (extraction) and cross-reference each other, so they advance in lockstep with frequent reconciliation.
3. **Wave 2 — Placement & Truth (parallel):** E. Geo and F. Quality. Geo locates the canonical entities; Quality contracts and audits every served number. Both consume Identity/Vehicle output and both feed Serving.
4. **Wave 3 — Serving:** G. Serving. The single source of truth materializes only once Identity, Vehicle, Geo, and Quality are stable enough to back a sub-50ms surface.
5. **Wave 4 — Proof & Surface (parallel):** I. Trust, H. Product, and J. Ops. Trust certifies coverage off the served census; Product makes it explorable; Ops keeps the whole loop self-healing. These run concurrently and feed their signal *back* into Wave 0 (Trust widens Discovery lists; Ops surfaces dead sources to Extraction), closing the loop.

**Always-on cross-cutting:** J. Ops and F. Quality are not one-shot waves — they run continuously across every other domain from the first served change onward.

## Orchestration hierarchy

```
                 CEO-Orchestrator (Program Director)
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  Domain Owner A      Domain Owner B   ...  Domain Owner J
   (per plan file)    (per plan file)        (per plan file)
        │                   │                   │
   build agents        build agents        build agents
   (parallel, file-     (parallel)          (parallel)
    scoped, return
    git diff)
        │                   │                   │
        └───────► Adversarial Verification ◄─────┘
                  (co-equal, independent)
```

- **CEO-Orchestrator (Program Director):** owns the master, the dependency graph, and wave sequencing. Never works in solitary on anything orchestratable; dispatches parallel forces and never waits passively — when one front is blocked, another is launched. Decomposes every order into a verifiable checklist before acting.
- **Domain Owners (A→Z):** one accountable owner per plan file. Each owner drives their domain's next-level headline to its acceptance gate and reports per-criterion status — never "done" without proof.
- **Build agents:** dispatched in parallel, each *owns one file*, runs against the repo, and returns a `git diff` integrated in series (worktree isolation is unavailable from the protected cwd — agents `cd` into the repo and hand back diffs).
- **Adversarial verification (co-equal):** verification is a first-class, independent role, not a rubber stamp. Every served change faces an adversarial reviewer with equal authority to block. Anti-hallucination is absolute: each claim is `[VERIFIED]` (read from source) or `[ASSUMED]`; numbers come from the live system, never from memory.

## Operating cadence & gates

**Per-change loop (every served change, no exception):**

1. **Additive + reversible only.** Change must be revertible more cheaply than it is to interrupt. Irreversible or high-cost actions stop at the gate (below).
2. **Dry-run on `:5434`** before anything touches the served surface — validate against the shadow/dry-run database first.
3. **Golden + Ferrari + CI green** for every change that reaches serving: golden fixtures, the Ferrari local suite, and CI (unit / collect / frontend / secret) must all pass. A red gate is a stop.
4. **Adversarial verification** signs off independently (co-equal authority).
5. **Integrate the diff in series**, re-run the gate, move to the next piece. One block closed before the next is opened.

**Cadence:** construction *chains* pieces turn by turn (component → GREEN → commit → CI → next piece — no idle sleeping). Draining is event-driven (driven by background-drain notifications) with a long heartbeat (~1200–1800s), never a 60s busy-poll.

**Owner gates — PENDING-OWNER, never blocking:**

| Gate | Rule |
|------|------|
| **Spend (EUR > 0)** | The program runs at EUR0. Any spend route is researched, a free alternative is exhausted first, and if none exists the item parks as **PENDING-OWNER**. Spend never auto-proceeds. |
| **Production write** | Push to prod / serving-of-record requires explicit owner instruction; parks as **PENDING-OWNER**. |
| **Legal** | Anything with legal exposure parks as **PENDING-OWNER**. |

Gates **do not stop the loop.** When the reversible work is exhausted, the orchestrator re-syncs, builds staged work, hardens, and re-scans — the gated residual stays explicitly **PENDING-OWNER**. It is forbidden to declare 100% complete while a gated residual is open: the honest state is "100% of reversible work done, N items PENDING-OWNER."

## Post-review reconciliation (adversarial gate)

> The program passed independent adversarial review as **APPROVED_WITH_MINOR** (0 critical; anti-hallucination **PASS** — all load-bearing claims verified against HEAD `81de58e`: the 25-adapter list, connector counts, migrations, `v_canonical_*` views; digital-footprint scope and **EUR0** discipline **COMPLIANT**). The three HIGH findings and the real coverage gaps are resolved here at program level; the ten domain plans stand as written.

**H1 — Dependency-edge semantics / no true build cycle.** Edges `X ← Y` denote *runtime data-flow* (X reads Y's current surface), not build precedence. Serving, Quality and Ops **already exist** at baseline, so upstream domains consuming them is not a cycle. **Build order is the five waves**; cross-wave edges into Serving/Quality/Ops mean "consume the existing surface", while their *next-level* work (Wave 3 Serving hardening; continuous Quality/Ops) layers on top. No topological contradiction remains.

**H2 — One canonical coverage metric.** The single national coverage number is the **MSE certified `coverage_lower = n_obs / ci_high`** (`pipeline/exhaustiveness/seal.py`). The three figures the review flagged are distinct, non-competing layers of it:
- **0.95** = the *per-stratum* seal threshold (`DEFAULT_THRESHOLD`; a province×segment must clear it to be SEALED) — Discovery's bar.
- **>=80%** = the *national rollup* target (hard urban/high-volume strata drag the aggregate below any single stratum's bar) — Trust's headline; current **37.72%**.
- **80.6% registral VENTA** = an *external* DIRCE/registral cross-check on the venta segment only — a triangulation anchor, never the headline.
Canonical reporting always names which of the three a number is.

**H3 — Canonical sale-point definition is a hard program gate.** No domain may **serve or seal** a dealer / sale-point count until Quality's single canonical definition — `v_servable_dealer` (`migrations/0056_v_servable_dealer.sql`, the active uncommitted artifact: active ∧ non-particular ∧ non-desguace ∧ garaje-only-with-inventory) — is the one definition every consumer (`stats`, `geo`, the seal) reads. The four historical scopes (19,164 / 19,144 / 54,607 / geo's `kind<>particular`) collapse to this one. **Quality Phase 1 gates Serving, Trust and Product** on this landing.

**Gap — compliance-posture ownership.** Mass-scraping legality (robots/ToS) and PII for the ~359K `particular` C2C seller rows had no owner. Assigned: **Quality** owns PII minimization in the data contracts; **Ops** owns per-source robots/ToS adherence in source-health; **legal sign-off is a PENDING-OWNER gate** (never auto-proceeds).

**Gap — explicit EUR0 prerequisites (Phase-0, not assumptions).**
- Discovery's DORK/REG/Páginas gap-closers require **wiring `axesor_cnae` + `paginas_amarillas` into `DISCOVERY_REGISTRY`** and standing up a **self-hosted SearXNG** (EUR0) for `dork_municipal`; until then those vectors do not fire.
- Trust's LCMCR/`Rcapture` cross-check requires an **R runtime** (free CRAN) declared as an environment prerequisite.

## North-star metrics

"A level unreachable by human or AI for years" expressed in numbers. Values marked *current* are the live baseline; *target* is the next-level bar.

| Dimension | Current (live baseline) | Next-level target |
|-----------|-------------------------|-------------------|
| **Discovery — non-particular denominator** | `coverage_lower` below target | **>=95%** `coverage_lower`, all 25 adapters through the audited `harvest_run` gate |
| **Extraction — connector reach** | delta engine on subset | **38/38** wholesale connectors wired, scheduler as a persistent daemon, continuous freshness tracking |
| **Identity — false merges** | multiple merge edge-sets | **0** false positives, one code-unique-per-dealer transitive-closure contract |
| **Vehicle — fuzzy over-count** | ~131.8K fuzzy over-count | over-count closed via pHash strong-key resolver, **0** false merges |
| **Geo — municipality completeness (non-particular)** | **85.79%** | toward the data-blocked floor **~90%**, self-hosted CartoCiudad/Nominatim fallback |
| **Trust — MSE certified lower-bound coverage** | **37.72%** | toward **>=80%**, every seal byte cryptographically reproducible with provenance |
| **Serving — latency** | FastAPI surface | **<50ms**, fuzzy-searchable, materialized-view-backed |
| **Quality — truth** | partial contracts | one canonical "sale point" definition, contract-gated ingestion, continuous anomaly detection |
| **Product — explorability** | census data | real global vehicle/dealer search + live 3D coverage map proving "everyone, everywhere" |
| **Ops — self-healing** | manual watch | every silent/failing source → one accurate auto-resolving alert; single observable scheduler proves liveness |
| **Cost** | — | **EUR0 sustained** across all of the above |

The bar is met when all ten domains hold their next-level target simultaneously, every served number is `[VERIFIED]` against the live system, and the only open items are explicit **PENDING-OWNER** gates (spend / prod / legal) — never silent gaps.