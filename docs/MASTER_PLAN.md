# CARDEEP — MASTER PLAN (A → Z, executable)

> **The single executable plan.** It converts the nine architecture pillars
> (`docs/architecture/00`–`08`), the six verification sub-pillars (`verification/V1`–`V6`),
> and the local-LLM tooling doc (`tooling/T08`) into one ordered, dependency-aware, binary-gated
> build sequence — from today's live floor (12,862 entities / 39k vehicles / 4 kinds / 0 Tier-1)
> to a sealed, honest **100% of Spain**.
>
> It owns four things the pillars individually do not: (1) the **reconciliation** of every
> contradiction between pillars, decided here once; (2) the **dependency-ordered phase plan**
> with a verifiable predicate per gate; (3) the **cost gates** — exactly what needs owner spend;
> (4) the **definition of 100% done**, refutable per segment × province.
>
> **This SUPERSEDES** the F-phase table in `PLAN.md` and the ROI order in `ORQUESTACION.md` —
> it absorbs both and makes every gate a predicate over the live DB / `verification_verdict`.
>
> **Marking discipline:** every fact is `[VERIFIED]` (read from repo/DB this session) or
> `[ASSUMED]` (design judgment). No placeholders. Companion: `docs/architecture/README.md`
> (the overview).

---

## 0. Ground truth this plan is pinned to `[VERIFIED 2026-06-12]`

| Fact | Value | Evidence |
|---|---|---|
| Engine | PostgreSQL **16.14**, Docker `cardeep-pg :5433`; `btree_gin`/`pg_trgm`/`pgcrypto` available; **PostGIS not** | live DB |
| Live rows | entity **12,862** · vehicle **39,068** · vehicle_event **41,165** · distinct kinds **4** | direct count |
| Kinds present | garaje 7200 · compraventa 2753 · concesionario_oficial 1617 · desguace 1292 | direct count |
| Recipes | **262** flat YAML at `countries/ES/recipes/CDP-ES-{NN}-{b32}.yaml`, all `source: autoscout24` | `ls` |
| Migrations live | `0001_geo` `0002_entities` `0003_vehicles_events` `0004_verification_health` (additive/reversible) | repo |
| Code live | `pipeline/{discover,ingest,verify,geo,geocode,recipe,harvest_dealer,ids}.py`, `pipeline/sources/{base,dgt_cat,osm,autoscout24,oem_*×8}.py`, `services/api/{main,codes}.py`, `scripts/{migrate,load_geo,seed_pilot,scale_as24,as24_*}.py` | repo |
| The scar | **138 AS24 dealers lost to throttling under 4× parallel load** | `PROGRESO.md` |
| Empty-but-defined | `is_tier1`=0 · platform entities=0 · `geo_comarca`=0 rows · `source_health`/`alert`=0 rows | live DB |

This plan is **additive evolution** of that floor: the 12,862 entities / 39k vehicles / 41k
events are preserved by in-place migration, never recreated.

---

## 1. CONTRADICTIONS BETWEEN PILLARS — reconciled here, once

The corpus was written by parallel agents; several pillars independently claim the same
artifact for different purposes. Each conflict is resolved below with a binding decision. **These
decisions govern; where a pillar disagrees, this section wins.**

### C-1 · The `migrations/0005` collision (FIVE docs claim it) — **the biggest conflict**
- **03-DATA-MODEL** uses `0005` for ENUM types + infra; data model owns `0005`–`0012`.
- **06-RESILIENCE-OPS** writes `0005_resilience_ops.sql` (breaker/harvest_run/repair tables).
- **V2-COMPLETION** writes `0005_completion.sql` (`entity_completion`).
- **V3-INQUISITION** writes `0005_inquisition.sql` (claim/skeptic/verdict tables).
- **V4/V5** write `0005_gestionador.sql` / `0005_verification_deep.sql` (deep ledger, audit chain).
- **DECISION (binding):** migration numbers are a **single global monotonic sequence**, never
  reused. The numbers in the verification/resilience pillars are *placeholders meaning "the next
  free number"*, not literal `0005`. The **canonical migration order is the 03-DATA-MODEL
  sequence `0005`–`0012`** (it owns the schema spine), and the operational/verification deltas
  append **after** it. Authoritative renumbering:

  | Migration | Owner pillar | Content |
  |---|---|---|
  | `0005` | 03 | ENUM types + extensions + shared `cardeep_block_mutation` trigger |
  | `0006` | 03 | entity evolve (enum swap + ontology cols + `platform_meta`) |
  | `0007` | 03 | organization + `entity.org_id` FK + `entity_source.first_seen` |
  | `0008` | 03 | vehicle → LIST(province) partitioned + `vehicle_spec` |
  | `0009` | 03 | `platform_listing` edge + `listing_fingerprint` |
  | `0010` | 03 | `auction_lot` (defined, v2 harvest) |
  | `0011` | 03 | `vehicle_event` → RANGE(month) partitioned + immutability trigger |
  | `0012` | 03 | rollup views (stats, freshness) + resilience-layer additions |
  | `0013` | 06 | `source_breaker` + `harvest_run` + `repair_attempt` + `source_health.{is_tier1,tuning}` |
  | `0014` | V5 (absorbs V2/V3/V4) | the **deep verification ledger** (see C-2) |
  | `0015` | V2 | `entity_completion` ledger |
  | `0099` | 03 | optional PostGIS (`geography` + GiST), extension-gated, only if installed |

  Every migration keeps the project's `IF NOT EXISTS` + inline `-- Rollback:` + ledger discipline.

### C-2 · The verification fork: ONE light pillar (05) vs SIX deep sub-pillars (V1–V6)
Pillars 05 and V1–V6 are **one system at two depths**, and every V-doc says it "supersedes and
expands the light 05-VERIFICATION-VAM." But they diverge on concrete schema. Reconciliation:
- **05 is the FRAME** (threat model, the four machines, the publish-gate, the doctrine). It is
  the canonical *architecture* of verification and is **not** superseded as architecture.
- **V1–V6 are the MECHANISMS** (exact estimators, sample sizes, DB-enforced quorum, audit chain,
  precision/recall split). They are the canonical *implementation*.
- **DECISION:** build the **05 frame first** (cheap inline VAM, already live in `verify.py`), then
  layer the V-mechanisms as the deep validator. The deep ledger of **V5 is the canonical schema**
  (it is the most complete and DB-enforces the quorum); V2/V3/V4 tables **append to V5's `0014`**,
  not compete with it. Specifically:
  - V5's `verification_verdict` superset (generated `quorum_n`/`family_n` + `chk_trustworthy_needs_quorum`
    CHECK + hash-chained `verdict_audit`) is the canonical ledger.
  - V3's `inquisition_claim`/`inquisition_skeptic`/`inquisition_verdict` + the read-only
    `cardeep_inquisitor` role are the canonical adversarial layer, **added in `0014`**.
  - V4's `gestion_item`/`gestion_transition` (the detector/manager) and V2's `entity_completion`
    are added in `0014`/`0015`.

### C-3 · The verdict enum disagreement
- **04-DATA-MODEL / 0004 live**: `verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED')` `[VERIFIED]`.
- **V5**: adds `'QUARANTINED'` (4 values).
- **V3**: uses `{TRUSTWORTHY, REFUTED, INCONCLUSIVE, QUARANTINED}` for its *separate*
  `inquisition_verdict` table.
- **V6**: adds `'SEALED-WITH-DECLARED-GAP'` as a coverage outcome.
- **DECISION:** the core `verification_verdict.verdict` is widened to the **4-value set
  `{TRUSTWORTHY, REFUTED, UNVERIFIED, QUARANTINED}`** in `0014` (V5's set; additive CHECK widen,
  reversible). `INCONCLUSIVE` lives **only** on the separate `inquisition_verdict` table (it is an
  Inquisition-internal state). `SEALED-WITH-DECLARED-GAP` is a **coverage KPI label**, not a
  verdict enum value — it is computed from `(coverage ≥ gate OR declared-caused-gap)` and stored
  as a coverage `verification_verdict` row plus the gap cause in `evidence`. No enum churn for it.

### C-4 · The freshness column name
- **05-VERIFICATION-VAM §3.4** wants `entity.last_successful_harvest` (distinct from `last_seen`).
- **V2/V5/V6** reference `last_harvest_at` and a per-verdict `expires_at`.
- **DECISION:** add **`entity.last_successful_harvest TIMESTAMPTZ`** (05's name — it is the precise
  one: "we successfully drained the source" vs "we touched the row") in `0012`, AND
  **`verification_verdict.expires_at`** (V5's per-verdict SLA) in `0014`. They are
  complementary, not duplicates: the column tracks source-drain success; the verdict expiry
  closes the publish-gate on stale verdicts. A 403 must **not** advance `last_successful_harvest`
  (the L10 silent-break guard).

### C-5 · Tier-1 recipe home: `countries/ES/_tier1/` vs `platforms/_tier1/`
- **ARCHITECTURE.md / 02-SCRAPING-ENGINE §9 / 03 / 04** all name `countries/ES/_tier1/<key>.yaml`.
- **08-REPO-ORGANIZATION §0.2** *deliberately relocates* it to `platforms/_tier1/<name>/` (a
  top-level peer of `sources/`), arguing top-level separation is stronger than a subfolder.
- **DECISION:** **08 governs** (it is the repo-organization authority and gives an explicit,
  reasoned override). Tier-1 code+recipe bundles live at **`platforms/_tier1/<name>/`**; the
  served catalog node stays at `countries/ES/_platforms/<cdp_code>/`. The earlier-pillar
  `countries/ES/_tier1/` path is **retired**; any sibling-doc reference to it resolves to
  `platforms/_tier1/`.

### C-6 · The `kind` enum vocabulary (ontology 11 vs classifier 6 vs schema legacy 6)
- **01-ENTITY-ONTOLOGY** defines **11** kinds + `cadena`(deprecated) + `organization`(relation).
- **T08 sample schema** shows a **6**-value classifier enum (`concesionario`/`compraventa`/`garaje`/
  `desguace`/`importador`/`plataforma`).
- **Live schema** has the legacy 6-value CHECK (4 kinds actually used).
- **DECISION:** the **canonical `entity_kind` ENUM is the 11-kind ontology set** (01 §6.4 / 03 §2),
  added in `0006`. The T08 classifier's 6 values are an **input simplification** — the local LLM
  emits a coarse kind which the **type-resolution precedence ladder** (01 §6.5) then refines using
  registral/locator/brandlist signals before it becomes the authoritative `entity.kind`. The
  classifier never writes `kind` directly; it writes a *candidate* with `kind_source='classifier'`,
  the lowest-but-one precedence rung. No conflict once the ladder is in place.

### C-7 · Denominator: which estimator is canonical?
- **05 §6** and **V3 §6**: two-source Chapman + variance.
- **V1**: Chapman *and* the **N-source log-linear** model + Chao lower bound + official anchors,
  with the explicit rule "≥3 orthogonal sources before any 100% claim is eligible."
- **V6**: Chapman + log-normal CI + stratification + the precision/recall split.
- **DECISION:** **V1 is the canonical denominator authority** (deepest, anchored, with the
  falsification rule). v1 ships the **pairwise Chapman matrix** (computable today from
  `entity_source`); v2 fits the **log-linear model**. The Chao lower bound and the DGT/DIRCE
  anchors are **mandatory** gates on every estimate. 05/V3/V6 Chapman formulas are consistent with
  V1 and remain as the inline/illustrative form.

### C-8 · The completion-claim count (12,862 vs 12,814 vs 20,000)
Different docs cite slightly different live counts (12,862 in 01/03/05/07; 12,814 in 04/V4/V5;
20,000 as a *hypothetical* claim in V2/V6). **DECISION:** these are **snapshots at different
minutes of the same session** (the harvest was running) plus one *illustrative* claim. The
**canonical live count for planning is `SELECT count(*) FROM entity` at build time** — never a
doc constant. V2/V6's "20,000" is explicitly a worked-example placeholder for the acceptance-
sampling math, not a live figure. No reconciliation needed beyond "trust the DB, not the prose."

### C-9 · Local LLM engine: Ollama (doctrine) vs vLLM (T08)
- **ORQUESTACION / 04 §3** name **Ollama**.
- **T08** recommends **demoting Ollama to dev** and running the batch fleet on **vLLM + Qwen3.5-4B**.
- **DECISION:** **T08 governs the engine choice** (it is the tooling authority, live-benchmarked).
  Ollama stays the **dev/single-stream front-end**; the production classify/parse/dedup fleet runs
  **vLLM + Qwen3.5-4B + `guided_json`(xgrammar)**, llama.cpp+Gemma-4 as the CPU fallback. The 04
  cost-router contract (`classify_kind`, `canonical_name`, temperature 0, JSON-schema, confidence
  threshold) is **engine-agnostic** and unchanged.

### C-10 · `pipeline/` package vs `engine/`+`sources/` rename
- **04 / workflows** build into `pipeline/`.
- **08 §10** renames `pipeline/` → `engine/` (generic core) + `sources/` (long-tail adapters) +
  `platforms/` (Tier-1).
- **DECISION:** **08 governs the final tree**, but the rename is a **late, mechanical, reversible
  step** (it is pure `git mv` + import rewrite, no logic change). Build *into the current
  `pipeline/` layout through the functional phases*, then execute the 08 reshape as one reviewable
  `refactor(repo)` commit (phase **P9**). This avoids churning every import on every early commit
  while still reaching the canonical tree.

### C-11 · The freshness-SLA taxonomy — FOUR incompatible definitions, reconciled here `[adversarial GAP-5]`
Four pillars independently define freshness TTLs over **different keys**, assigning *different*
TTLs to the same physical row, and the publish-gate (V5 `expires_at`) fights the staleness
detector (V4): a compraventa inventory row is "7d dealer" (V2/V6), "24h entity_inventory" (V5),
and "3d compraventa" (V4) at once. V5 would close the gate at 24h while V4 only opens a staleness
item at 3d — one organ withholds-as-stale what another calls fresh.
- **DECISION (binding): there is ONE freshness axis, keyed by `(subject_type, segment)`, and it is
  the V5 `expires_at` column.** All four taxonomies collapse onto this single matrix. The
  *publish-gate* (V5 expiry) and the *staleness detector* (V4) read the **same** TTL — V4's
  warning threshold is `expires_at` itself (`staleness_ratio = age/TTL > 1.0` ⇔ `now() > expires_at`),
  so the gate and the detector can never disagree. V2/V6 narratives are the human-readable form of
  the same numbers. **Canonical TTL matrix** (supersedes V2 §3.4, V5 §4.4, V6 §1.4, V4 §3.4):

  | subject_type / claim | segment refinement | TTL (`Δ`) | publish-gate == V4 detector |
  |---|---|---|---|
  | `entity_inventory` | Tier-1 marketplace counter | **24 h** | yes |
  | `entity_inventory` | compraventa / official dealer VO | **72 h** (3 d) | yes |
  | `entity_inventory` | garaje (selling subset) | **7 d** | yes |
  | `entity_inventory` | desguace / long-tail static | **30 d** | yes |
  | `platform` (Tier-1 served counter) | — | **24 h** | yes |
  | `source` (discovery count) | — | **30 d** | yes |
  | `entity` (existence) | — | **90 d** | yes |
  | `denominator` (capture-recapture N̂) | — | **180 d** | yes |

  The previous V5 "entity_inventory = 24h flat" is **refined by segment** here (a desguace's stock
  does not drift daily; a Tier-1 counter does). `ingest.py` stamps `expires_at = created_at +
  TTL(subject_type, segment)` at verdict write; V4's staleness lane is wired to the **same**
  function. No row carries two TTLs. (Closes GAP-5.)

### C-12 · The stealth-engine disagreement — T02 vs T05 vs 02, reconciled here `[adversarial GAP-20]`
The contradiction-reconciliation section never settled which browser injector is canonical, and the
docs disagree: **02 §2/§6/§11** and **T05** endorse **camoufox** as the primary injector; **T02**
demotes it (Scrapling swapped to **patchright** at v0.3.13; the camoufox pip wrapper is ~16 mo
stale, maintainer on medical hiatus); **nodriver** (the recommended pure-CDP fallback) ships **no
tagged releases** — a supply-chain risk for a "pinned, reproducible, everything-to-main" doctrine.
- **DECISION (binding): T02 governs the stealth engine** (it is the live-benchmarked tooling
  authority and supersedes the earlier prose). The canonical injector stack is:
  1. **Primary browser injector: `patchright` (the Scrapling ≥0.3.13 default).** It is actively
     maintained and is what Scrapling actually drives today.
  2. **camoufox is demoted to an *optional, pinned, vendored* injector** used only where a probe
     proves patchright is fingerprintable on a specific target; it is never an unpinned dependency.
  3. **nodriver (pure CDP) is allowed ONLY vendored at a pinned commit** (`pip install
     git+…@<sha>`), recorded in `requirements.txt` with the SHA — never `@main`. A CI check
     forbids any unpinned VCS dependency.
  The 02/T05 references to "camoufox-driven StealthyFetcher" are **retired**; any sibling-doc
  reference resolves to "patchright-driven StealthyFetcher". The engine layer is injector-agnostic
  behind `engine/fetch/tiers/` so the swap is a one-file change. (Closes GAP-20.)

### C-13 · Ownership-first vs platform-wholesale-first — the harvest-order contradiction `[adversarial GAP-27]`
**07 §4 Wave A** drains platforms FIRST and *discovers* selling dealers as a side-effect; but
**invariant #2 + 03 §4.1** require every `vehicle` to be OWNED by a resolved selling entity
(`entity_ulid` → a dealer, never a platform) at INSERT time, with `province_code` copied from that
owner. At first-platform-drain the dealer is often not yet an entity — so either the car cannot be
inserted (serializing the "parallel wholesale" 07 claims) or it is inserted under a placeholder
owner (violating the ownership invariant and the province-partition key).
- **DECISION (binding): a two-phase "stage-then-resolve" ingest, never a placeholder owner.**
  1. A platform drain writes each raw listing to a **`listing_staging`** table (additive, in
     `0009`), keyed by `(platform_entity_ulid, listing_ref)`, carrying the *unresolved* seller
     signal (seller name/url/phone/geo as scraped) and the full payload. **No `vehicle` row, no
     province partition, no ownership invariant** applies to staging — it is pre-entity.
  2. A **`cdp:resolve_seller`** job mints/links the selling entity (dedup by `cdp_code`, geocode →
     province) — the discover-as-side-effect, now an explicit, idempotent step.
  3. Only **after** the seller is a resolved, geocoded entity does the **promote** step INSERT the
     `vehicle` (owner = that entity, `province_code` = its province) + the `platform_listing` edge,
     and emit NEW. Staging rows whose seller cannot yet be resolved sit in staging (visible,
     counted as "pending-attribution"), never as fabricated dealers and never as platform-owned cars.
  This keeps wholesale **parallel** (staging is lock-free and province-free) while the ownership
  invariant holds at every `vehicle` INSERT. The P7a gate predicate adds: *zero `vehicle` rows
  owned by a `kind=plataforma` entity; staging-pending count published as a declared residual.*
  (Closes GAP-27.)

### C-14 · Membership-filtered denominator frame — the recall/denominator paradox `[adversarial GAP-1]`
The seal promise is "we hold X% of N̂", but the Chapman N̂ (V6 §8) is computed over capture sources
(Páginas Amarillas + FSQ/Overture) that **include C2C private sellers and non-selling workshops**,
while the deflation (garaje `sells_cars`, D-4) and the C2C sentinel attribution (ontology §4.3) are
applied to the *numerator/served set* but NOT subtracted from the capture-recapture *frame* before
recall is computed. So `recall = found / N̂` mixes a membership-filtered numerator against an
unfiltered denominator — recall is understated (frame inflated by non-entities) and GATE(seg) is
measured against a different denominator than V1 produces.
- **DECISION (binding): the capture-recapture frame MUST be filtered by the SAME membership
  predicate that defines a CARDEEP entity** (ontology §1, "offers car stock for acquisition")
  before N̂ is computed. Concretely (the rule V6's new §4.7 implements):
  - Every capture list (`n₁`, `n₂`, `m`) is passed through the **membership filter** first:
    drop rows that resolve to a C2C private seller (sentinel-attributed), drop `garaje` rows with
    `sells_cars=false`, drop rows that resolve to a non-POS (pure parts trader with no car stock).
    The filtered counts `n₁ᶠ, n₂ᶠ, mᶠ` feed Chapman → `N̂ᶠ`, the **membership-filtered universe**.
  - `recall = found / N̂ᶠ`, where `found` and `N̂ᶠ` are now drawn from the **same** predicate. The
    seal gate `GATE(seg)` reads `N̂ᶠ`. Where a capture source cannot be membership-filtered at the
    row level (a directory that does not expose `sells_cars`), the **unfilterable fraction is
    estimated by a labeled sub-sample** and N̂ is bracketed `[N̂ᶠ_lower, N̂_raw]`, with the seal
    computed against `N̂ᶠ_lower` (the honest, conservative denominator).
  - V6 §8's worked "68.8% of 29,091" is **re-labeled**: 29,091 is `N̂_raw` (unfiltered, an upper
    bracket); the seal-bearing number is `N̂ᶠ` after C2C/non-POS removal. The headline recall is
    reported against `N̂ᶠ`, with `N̂_raw` shown as the "all-listed" context, never as the seal frame.
  (Closes GAP-1. Implemented in V6 new §4.7 and reflected in the seal predicate §6.2.)

### C-15 · Numerator completeness as a *measured* fraction (vehicle-recall) `[adversarial GAP-2]`
Every coverage mechanism closes the **entity** denominator; `NUMERATOR-SEALED(entity)` only proves
each *known* entity was drained completely. Nothing bounds the **true national CAR count** the way
Chapman bounds the entity count — cars on entities we never discovered, or on channels we do not
harvest (Facebook Marketplace, un-mirrored dealer-own stock), are an **unstated, false closure
assumption** (the vehicle population is treated as fully observable once entities are sealed).
- **DECISION (binding): introduce a vehicle-level capture-recapture estimator, `N̂_V`, parallel to
  the entity estimator.** Two independent vehicle captures with a vehicle-level match key
  (`listing_fingerprint` / VIN / pHash, the same key 03 §6 already defines) → Chapman over
  *vehicles*: capture 1 = our held available vehicles in a (segment, province) cell; capture 2 = an
  independent vehicle pull (a platform facet not used in capture 1, or an OEM-VO portal re-list).
  `vehicle_recall = N_V_held / N̂_V ± CI`. This is a **first-class KPI line**, reported apart from
  entity recall, each with its own CI. The forbidden state is asserting "100% of stock" with only
  entity-recall measured. Where `N̂_V` cannot be formed for a cell (no orthogonal vehicle capture),
  the cell's vehicle-recall is **UNVERIFIED**, declared, never assumed-complete. (Closes GAP-2.
  Implemented in V6 new §4.8; surfaced in the KPI panel §6.3.)

### C-16 · The Inquisition independence guarantee — physical, gated, with a migration `[adversarial GAP-9]`
V3 §10/§11 declare the read-only `cardeep_inquisitor` role AND the separate network egress as
"design requirements not yet in repo; independence is PROCEDURAL not PHYSICAL until built", yet
P11's gate does not require either to exist, and the DB CHECK enforces `quorum_n`/`family_n` but
nothing enforces that the second family was not produced by the **same process/IP**.
- **DECISION (binding):**
  1. **Migration `0014` creates the role** `cardeep_inquisitor` with `GRANT SELECT` only on the
     served + verdict tables and **no** write grant anywhere — listed explicitly in the `0014`
     migration body, not in prose. P5's gate is extended: *the role exists AND a write attempt by
     it is rejected by the DB* (a proven `INSERT … → permission denied`).
  2. **The separate egress identity is a hard P11 gate, not a procedural note.** Each Lens-C
     live-refetch path records its `egress_id` (proxy pool / network identity) on the verdict; a DB
     CHECK on `inquisition_verdict` requires `egress_id(skeptic) <> egress_id(producer)` for any
     verdict that consumed a live re-fetch. P11 cannot pass until: the role exists, the egress
     CHECK is live, and a synthetic "producer judges itself" attempt is **rejected**.
  3. The independence is therefore **enforced (DB role + egress CHECK)**, not trusted. (Closes GAP-9.)

---

## 1b. Adversarial-review gap closures — decisions index `[adversarial review 2026-06-12]`
The contradictions C-11..C-16 above plus the localized decisions below close the 35-gap adversarial
review. Each gap is fixed by a binding decision here and/or a new section in the owning pillar; the
"Gaps closed" section at the end of this file is the audit index.

- **G-A4 · VN / km0 inventory shape + declared gap (GAP-4).** New-vehicle (VN) and km0/
  pre-registration stock is **out of live-inventory scope** (no reliable public live feed) but is
  now a **declared inventory-shape gap**, not silence. A new `inventory_shape` value `new_vehicle`
  (alongside retail/auction/parts) marks the VN residual. A `concesionario_oficial` is sealed on
  its **VO** numerator with an explicit `declared_gap{cause:'VN-no-live-feed', shape:'new_vehicle'}`
  on the entity; the province seal carries the VN gap **itemized**, never reported as covered.
  **km0/pre-registration cars are VO for our purposes** (web-exposed on coches.com/AS24) — they get
  `kind` unchanged, `inventory_shape='retail'`, `vehicle_spec.km0=true`, and ARE harvested + sealed.
  Only true VN configurator stock is the declared gap. (01 §2.1 edit + seal §6.)
- **G-A11 · agente_oficial numerator seal (GAP-11).** The second-largest official population (3,642)
  gets an explicit numerator rule: an `agente_oficial` whose stock is **inherited** (surfaces under
  the parent dealer's profile) is `NUMERATOR-SEALED` as **`caused-inherited`** — its cars are owned
  by and counted against the **parent** entity (never double-counted), and the agente carries a
  `served_via: <parent cdp_code>` pointer. An agente with an **independent feed** is sealed on its
  own numerator like any dealer. An agente with neither is `caused-zero` (verified no independent
  online stock). No agente double-counts the parent; none is left undefined. (01 §2.2 edit + seal §6.)
- **G-A13 · SEG-3/7 enumeration honesty (GAP-13).** The "1.00 enumerated, complete by construction"
  gate for platforms is **internally contradictory** while 00 confesses VGRS unprobed and per-dealer
  OEM subsites un-enumerated. Fix: the platform-seal gate is **1.00 against the *committed* registry
  snapshot**, and the registry carries an explicit `enumeration_status ∈ {complete, open-probe}`
  per platform. A platform in `open-probe` (VGRS, OEM subsite discovery, industriales/furgoneta
  channels) is a **declared discovery gap**, not counted as sealed. SEG-3/7 seals at 1.00 of the
  `complete` set; the `open-probe` set is an itemized residual. Vans/industriales get an explicit
  **scope decision**: `kind=compraventa`/`concesionario` with `inventory_shape='retail'` but a
  `vehicle_class ∈ {car, van, industrial}` tag so the mandate's "cars" headline can be reported
  filtered, with the van/industrial count shown apart. (00 §3 + 07 §6.1 edit.)
- **G-A12 · Global spend ceiling + authorization state machine (GAP-12).** Per-source caps are
  insufficient: there is no aggregate ceiling and no persisted authorization record. Fix in §5
  (cost gates) below: a **global monthly burn cap** with a hard **circuit-breaker that HALTS all
  Tier-2 spend** at the aggregate ceiling, plus a persisted **authorization record** with expiry
  and cost-basis re-authorization.
- **G-A14 · Delta exactly-once-per-mutation (GAP-14).** The snapshot UPDATE and the `vehicle_event`
  INSERT MUST be in **one DB transaction**, and each event carries an **idempotency key**
  `(vehicle_ulid, event_type, source_diff_hash)` with a UNIQUE constraint so redelivery (XAUTOCLAIM)
  cannot double-emit. (04 §4 + 03 edit + invariant #3.)
- **G-A15 · Ceuta/Melilla structural exemption (GAP-15).** INE 52 includes Ceuta(51)/Melilla(52) as
  autonomous cities with a structurally inapplicable comarca grid and near-zero capture-recapture
  sample sizes. Fix: these two cells are a **declared structural exemption** — sealed by a
  **direct-census** rule (hand-enumerable dealer list, no Chapman) since the universe is tiny and
  fully observable, with comarca-stratum marked N/A. `52/52 SEALED` is reachable; the two cells
  carry `seal_method='direct-census'` instead of `capture-recapture`. (seal §6 + 03 edit.)
- **G-A6 · Comarca/city seal + geo-resolution drift detector (GAP-6).** (a) The seal scoreboard is
  province-grained; the comarca/city stratum has no closure method. Fix: comarca/city seals are
  **derived, not independently estimated** — a province seals its comarca grid when every entity in
  the province is geo-placed to comarca+city (sentinel-placement rate below threshold) AND the
  province denominator is sealed; the comarca grid is a *placement-completeness* gate, not a second
  capture-recapture. (b) A new **V4 `geo_resolution_drift` detector** watches the
  `_sin-comarca`/`_sin-municipio` sentinel-placement RATE; a jump (e.g. >2× baseline, or >X% of new
  entities) fires a `geo-drift` item — a geocoder regression is no longer silent. (V4 edit + seal §6.)
- **G-A7 · LLM classifier accuracy floor + drift regression (GAP-7/25).** `kind` (the most
  load-bearing field) and `canonical_name` (feeds `cdp_code` → capture-recapture) are written by an
  unverified local LLM with no accuracy gate. Fix: a **held-out, human-labeled gold set** (≥300
  dealers spanning every kind, sampled across the long-tail) with a **per-kind precision/recall
  floor** (≥0.95 on the kinds where the classifier is the sole authority). P3's gate is extended:
  the classifier must clear the gold-set floor before it writes candidates at scale. A **nightly
  golden-set regression** re-scores the model; a drop below floor (model/quant/prompt drift) fires a
  `classifier_drift` Gestionador item and freezes `kind_source='classifier'` writes until cleared.
  The acceptance-sampling corpus (V6) is extended to cover **classifier accuracy**, not just scraper
  field-fidelity. (T08 new § + V4 detector + P3 gate.)
- **G-A8 · C2C volume as a sized KPI line (GAP-8).** The headline "100% of car points-of-sale"
  silently excludes the single largest pool of cars-for-sale (Wallapop ~750k, mostly C2C private).
  Fix: a **mandatory KPI line** `c2c_listed_pct = C2C-attributed listings / all-listed Spanish cars`,
  shown on the honest-KPI panel so dealer-segment coverage is **never** presented as market coverage.
  The caused-residual doctrine now *sizes* the C2C gap, not just mentions it. (07 KPI + §6.3.)
- **G-A10 · BORME adapter + closed-population window gate (GAP-10/22).** V1 cites BORME altas/bajas
  as the churn-quantifier but **no BORME adapter exists** in the pipeline, source census, or build
  plan — the churn-correction input is missing. Fix: (a) **add `sources/long_tail/registries/
  borme.py`** to the source census as a buildable adapter (BORME open-data JSON/XML, SOURCES_ES §3.1)
  in a new phase slot; (b) the capture-recapture estimator gains a **closure gate**: it **rejects a
  source-pair whose `seen_at` spread exceeds the freshness window (≤30 d)**, and widens the CI by the
  BORME-measured churn fraction (2% is now *measured*, not asserted). No N̂ is sealed from captures
  separated by more than the window. (V1 edit + source census + phase slot.)
- **G-A21/29 · Ground-truth dedup audit (GAP-21/29).** The strict/default/loose dedup band shares
  one name-normalization/CIF code path, so a **common-direction** merge bias shifts every pair the
  same way — invisible to the pairwise-disagreement alarm. Fix: a **hand-labeled dedup ground-truth
  set** (a sample of cross-source pairs labeled same-dealer/different-dealer by a human) calibrates
  the *true* merge rate independently of the estimator; the per-province coverage % carries the
  ground-truth-measured merge error as an explicit bias term, not just the (insufficient) sensitivity
  band. Separately, the **firm→point ratio ρ̄** for registral CNAE (which counts FIRMS not POINTS)
  must be **measured on a labeled sub-sample** before CNAE is used as a co-registered capture; until
  measured, CNAE is an anchor only, not a Chapman capture for SEG-4. (V1 new § + denominator gate.)
- **G-A30 · `family_n` cannot see origin-distinctness (GAP-30).** V5's CHECK enforces ≥2 *families*
  but `family_n` is DISTINCT-family-count only; origin-distinctness is "enforced per-family at write
  time" — i.e. in application code, the layer V5 says cannot be trusted. Fix: add a generated
  **`origin_n = cdp_distinct_origins(verifier_paths)`** column and widen the CHECK to
  `chk_trustworthy_needs_quorum: family_n ≥ 2 AND origin_n ≥ 2`. The DB now enforces two distinct
  origins, not just two family labels; the family label being hand-set no longer back-doors the
  guarantee. (V5 §3.1 edit.)
- **G-A33 · `v_latest_verdict` materialization + freshness-gate availability (GAP-33).** The "never
  falls" API binds every served row to a heavy `DISTINCT ON … ORDER BY created_at DESC` view over the
  whole verdict ledger, and verdict expiry flips `is_publishable` to false with **no write** — so the
  publishable set silently shrinks to near-zero between harvest cycles (data availability collapses
  even though the process stays up). Fix: (a) **materialize `v_latest_verdict`** as a
  `MATERIALIZED VIEW` (or an incrementally-maintained `entity_latest_verdict` table refreshed by the
  ingest/verify path), so the hot read path is an index lookup, not an analytical scan; (b) a
  **continuous re-verification cadence** keyed to the §C-11 TTL matrix keeps the served set fresh —
  the publish-gate withholds individual *stale* rows but the cadence guarantees the served set does
  not collapse wholesale. "Never falls" is now defended for the **data surface**, not just process
  liveness. (V5 §3.4 edit + invariant #7.)
- **G-A35 · Eviction vs replay reconciliation (GAP-35).** V5 §7 makes TRUSTWORTHY verdicts replayable
  from `evidence_uri → data/probe/<blobhash>`, but 08 EVICTS `data/**` by capacity — the blob a
  verdict points at is exactly what eviction deletes, so replay-based fabrication/staleness detection
  is unavailable for €0 on any evicted subject (most of them over time). Fix: (a) **TRUSTWORTHY
  verdicts pin their crude** — an evicted blob backing a *live* TRUSTWORTHY verdict is **forbidden**;
  `evict.py` skips any blob referenced by a non-expired TRUSTWORTHY verdict (a small, bounded pinned
  set, since only the latest verdict per subject is live). (b) Once a verdict **expires**, its crude
  is evict-eligible and replay for that subject correctly requires a live re-fetch (the spend already
  acknowledged for Tier-1). Reproducibility-from-recipe (08 law #5) and reproducibility-from-artifact
  (V5 §7) are now distinct and both honored: the artifact survives exactly as long as the verdict it
  proves. (V5 §7 + 08 edit.)
- **G-A3/26 · Cross-platform same-car resolver + over-count CI (GAP-3/26).** See §C-13 staging model
  AND 03 §6: v1 ships a **cross-seller resolver gated on a STRONG key only** (VIN exact, or pHash
  Hamming ≤ 6 AND make+model+year+km-band match) that **collapses a second-platform sighting into a
  `platform_listing` edge on the existing vehicle instead of a second `vehicle` row**, with a
  conservative threshold so over-merge stays below under-merge. The residual cross-seller over-count
  is **bounded by a measured CI**: a labeled sample estimates the duplication rate, and every served
  platform/national rollup counter carries `±dup_ci`. A counter knowingly inflated by an *unmeasured*
  amount is forbidden (it is exactly the L1/L2 lie); it must be either deduped or carry its measured
  bound. (03 §6 algorithm + V6 vehicle-recall + KPI.)
- **G-A28 · C2C sentinel sub-partitioning (GAP-28).** Routing ~1.4M C2C cars into the single
  `vehicle_p_00` partition defeats the per-province scale strategy and turns `idx_vp_entity_avail`
  into a multi-hundred-thousand-row equality bucket on one synthetic owner. Fix: **`vehicle_p_00` is
  sub-partitioned by `(platform_entity_ulid)` HASH** (8–16 sub-partitions) so each C2C platform's
  inventory and the national-platform cars spread across sub-partitions; the `entity_ulid` index on
  the C2C sentinel becomes per-sub-partition. The C2C sentinel owner is additionally split per
  platform (`c2c_private@wallapop`, `c2c_private@milanuncios`) so HASH(owner) actually distributes.
  (03 §4 edit.)
- **G-A31 · 0008 swap preflight + zero-downtime (GAP-31).** `INSERT … ON CONFLICT DO NOTHING`
  silently drops legacy rows that collide on the new UNIQUE key (count shrinks, P0 gate fails
  unexplained), and the two-step `RENAME` leaves `vehicle` briefly absent (violating "API never
  falls"). Fix: (a) a **pre-flight** that COUNTS legacy duplicate `(entity, deep_link)` under the
  backfilled province and **aborts the migration** if any exist (with the dup list), so no row is
  silently dropped; (b) the swap is wrapped so `vehicle` is **never absent** — use a single
  transaction `ALTER TABLE … RENAME` pair (DDL is transactional in PG; both renames commit
  atomically, so no window where `vehicle` is missing), and the E2E migration gate asserts the API's
  `SELECT FROM vehicle` never errors during the swap. (c) The `COALESCE(province,'00')` backfill is
  flagged: un-geocoded long-tail landing in '00' is now a **declared placement gap**, geocoded by the
  `cdp:geo.backfill` job, not conflated with national platforms permanently. (03 §4.1 + P0 gate.)
- **G-A32 · Tier-1 separation pierced by DB + recipe-family + open-platform straddle (GAP-32).** The
  "six axes" separation is filesystem/ops-only; three surfaces cross by construction: (1) the
  **database** (Tier-1 and long-tail share tables/partitions — `is_tier1` is a column, not a store);
  (2) the **Adevinta recipe family** (one `advgo` recipe drains coches.net + milanuncios + fotocasa +
  segundamano, so `rm -rf coches_net/` orphans the shared recipe); (3) **open-platform code/catalog
  straddle** (AS24 adapter in long-tail, served entity in `_platforms/`). Fix: declare the honest
  scope of invariant #5 — **separation is filesystem+ops, NOT data**. Add (a) a **data-axis guard**:
  destructive ops on served data are gated by a row-count sanity bound + the GONE-storm quarantine
  (06), since a bad `DELETE`/migration is the real cross-tier blast radius, not `rm`; (b) the shared
  Adevinta recipe is **extracted to `platforms/_tier1/_shared/adevinta/`** with each platform
  importing it — deleting one platform is `rm -rf <name>/` and a registry edit, never an orphan; the
  CI guard checks the shared recipe has ≥1 importer or is also removed; (c) the open-platform
  straddle is **documented as legitimate** (open platforms span both worlds by design) and the CI
  guard's scope is corrected to "no Tier-1-walled helper imported by a long-tail or open adapter",
  which is checkable. (08 edit + invariant #5.)
- **G-A24 · AIMD trains the behavioral detector (GAP-24).** The governor's additive-increase-until-
  429 / multiplicative-decrease learns the *volumetric* ceiling — but against a 2026 behavioral ML
  scorer (DataDome/Akamai v4+), methodically ramping-to-trip-then-backing-off-50% **is** the
  automated-probing pattern the model flags. The scar it fixes (138 AS24 dealers) was an **OPEN**
  source with no behavioral WAF. Fix: **two pacing regimes, selected by defense tier.** OPEN sources
  keep AIMD (volumetric optimization is correct there). **Behaviorally-scored Tier-1/walled sources
  use a fixed, randomized, human-shaped pace** (jittered inter-request delays drawn from a
  human-like distribution, no convergence-to-ceiling probing) — the governor never ramp-probes a
  walled host. The doc now distinguishes *rate-limit avoidance* (AIMD) from *behavioral-pattern
  avoidance* (randomized pacing). (06 edit.)
- **G-A17/18/19 · Anti-detection 2026 reality (GAP-17/18/19).** (17) The X25519MLKEM768 PQ key share
  is no longer presence/absence — Akamai made PQ the default (Jan-2026), ~57% of ClientHellos carry
  it (+1,088 bytes), and the discriminator is **byte-exact key-share group order + ClientHello shape
  + cross-session fingerprint STABILITY**. Per-session browserforge rotation (the current design) is
  itself a v4+ flag. Fix: the engine maintains a **stable per-target identity that persists across
  sessions** for walled sources, and the §8 fingerprint self-test is upgraded from "is the key share
  present" to a **byte-for-byte diff of the emitted ClientHello against a reference current-Chrome
  JA4**. (18) Wallapop's signed/rotating request signature and the Adevinta Lambda@Edge token are
  **OPEN QUESTIONS gating ~1.4M of ~2.1M listings**, yet budgeted €0 — they are now **mandatory P0.5
  spike outputs** before the cost gates are trusted. (19) DataDome/Akamai are per-request ML, not
  static tier labels — a minted clearance cookie replayed from a datacenter IP at curl-pace
  **re-scores as bot on the next request**; the mint-then-drain pattern works for cookie-ISSUANCE
  walls (passive CF/Incapsula) but NOT full-sensor walls (Akamai `_abck`, DataDome). Fix: the cost
  model gains a **per-request sensor-regeneration line** for full-sensor walls (a 50k-listing Akamai
  drain is N sensor calls, not one mint) — Tier-2 cost is metered per page, changing the spend
  estimate by orders of magnitude. (02/T05 edit + P0.5 + cost gates.)
- **G-A16 · The engine is unbuilt — P0.5 validation spike (GAP-16).** Every "€0 / curl_cffi suffices"
  claim is a **prediction**, untested: `requirements.txt` has the entire scraping arsenal commented
  out; there is no fetch engine, router, governor, queue, S-HEALTH, or Tier-1 recipe; 0 platform
  entities. The €0 phase ordering is contingent on curl_cffi clearing coches.com Imperva, autocasion
  Cloudflare, Wallapop's signed API, and the Adevinta POST **on the first try**. Fix: a new **phase
  P0.5 "anti-detection validation spike"** (below) stands up `curl_cffi + browserforge + patchright`
  and **re-probes the 5 load-bearing OPEN/decaying + 2 walled-API targets BEFORE committing to the
  €0 ordering.** If coches.com Imperva or autocasion CF have hardened since the 2026-06-12 probe, the
  ROI spine (R2 = 700k free) collapses and spend moves from "last" to "early" — P0.5 surfaces that
  before the plan is committed, not after. (phase plan + cost gates.)
- **G-A23 · Legal/GDPR/sui-generis threat surface (GAP-23).** The corpus respects a few named
  robots/ToS exceptions but never addresses the **systemic** legal surface of a commercial, served,
  monetizable EU scraped database: (a) **GDPR** — dealer and especially C2C private-seller listings
  are personal data of identifiable EU persons; "attributed to the platform sentinel" does not remove
  the exposure of having fetched/stored it; (b) the **EU Database Directive sui-generis right** —
  coches.net/AS24/Adevinta have invested in their databases; wholesale aggregation is the exact
  fact-pattern of EU scraping litigation; (c) **circumventing a technical protection measure**
  (Akamai/sensor walls via paid solvers) has a different legal character than reading open HTML, and
  the anti-detection sophistication is precisely what raises it. Fix: a new MASTER_PLAN **§10 Legal &
  data-protection threat model** that (i) makes **C2C personal data minimization** a rule — C2C is
  stored as **aggregate counts attributed to the platform sentinel, NOT per-listing personal data**
  retained; (ii) records the **sui-generis exposure** per Tier-1 source as a `legal_class` on the
  registry and gates wholesale aggregation of a protected DB behind an explicit owner decision; (iii)
  treats **TPM-circumvention sources** as a distinct `legal_class='tpm-circumvention'` requiring
  owner authorization alongside the spend authorization (it is not merely a cost gate). This is a
  category the threat model omitted entirely; it can void the served-product premise regardless of
  engineering cleanliness. (new §10 + 07 + 00 registry field.)
- **G-A34 · Scale model honesty — partition skew + event-log volume (GAP-34).** The docs alternate
  "tens of millions" with a ~1.1M live numerator + forever gone-history; province `LIST` partitions
  are wildly unbalanced (Madrid/Barcelona + the '00' bucket dwarf rural provinces 10–100×, so `LIST`
  does **not** deliver the per-partition balance that justified it over HASH), and the partition DDL
  (0008/0011) is committed FINAL before any load test, with several decisions (C2C-in-'00', skew)
  knowably-bad today. Fix: (a) the '00' sub-partitioning (G-A28) addresses the worst hot partition;
  (b) the residual (03 §9.7) is **upgraded from "designed-for, not load-tested" to a concrete
  pre-commit obligation**: the skew and event-log volume are estimated *before* 0008/0011 are marked
  final, and the migrations carry a **documented re-partition path** (the LIST→sub-HASH change is
  reversible via a maintenance re-home) so the irreversible-feeling DDL is in fact reversible; (c) the
  scale headline is reconciled — "designed for tens of millions of *lifetime* vehicle rows incl.
  gone-history; ~1–2M *live* at any time" — and stated once, not contradicted. (03 §9.7 + P0 note.)

---

## 2. The phase plan — dependency-ordered, binary-gated

Phases are **P0–P12**. Each gate is a **verifiable predicate over the DB / `verification_verdict`
/ the filesystem**, not a vibe. Phases F0–F3 of the old `PLAN.md` are **done** `[VERIFIED PROGRESO]`;
this plan is the forward build. The dependency arrows are hard — a phase may not start until its
predecessors' gates are green. Phases marked `∥` run concurrently where they touch different hosts
(the rate-limit parallelism law, 07 §7).

| Phase | Name | Depends on | Pillars | **BINARY GATE (verifiable predicate)** | Cost |
|---|---|---|---|---|---|
| **P0** | SCHEMA SPINE | live 0001–0004 | 03 | migrations `0005`–`0012` apply → rollback → re-apply clean; `\dT entity_kind` shows 11 kinds; `platform_listing`/`organization`/`platform_meta` exist; 12,862 entities + 39k vehicles + 41k events **preserved** (count before == after); **0008 swap: legacy-dup pre-flight passes (G-A31), `vehicle` never absent during RENAME, no row silently dropped**; E2E migration pattern green | €0 |
| **P0.5** | ANTI-DETECTION VALIDATION SPIKE `[G-A16/18]` | P0 | 02, T02, 00 | `curl_cffi + browserforge + patchright` stood up; the **5 load-bearing OPEN/decaying targets** (coches.com Imperva, autocasion CF, motor.es, AS24, coches.net) **re-probed live** and each classified OPEN/curl-OK or WALL-hardened with evidence; the **2 walled-API unknowns RESOLVED** — Wallapop `cars/search` signature (static-header vs rotating-signed) and Adevinta `advgo` token (open vs Lambda@Edge-minted) — written to `state/tier1-blocked.json` with the exact verdict; the **ClientHello self-test** diffs emitted bytes against a reference current-Chrome JA4 (not mere PQ presence); **the €0 phase ordering is RE-CONFIRMED or the ROI spine re-sequenced** (if a load-bearing target hardened, spend moves earlier) | €0 (spike) |
| **P1** | GOVERNOR + QUEUE | P0.5 | 04, 06 | Redis Streams up (own instance, AOF on); per-source token-bucket governor with AIMD; `as24` profile born `max_concurrency:2`; a synthetic 4×-load test against a stub source **cannot exceed** the host budget (the scar made structurally impossible); `0013` (breaker/harvest_run/repair) applied | €0 |
| **P2** | WORKER FLEET + HANDLERS | P1 | 04 | existing `discover`/`ingest`/`verify` logic wrapped as idempotent job HANDLERS on the streams; `XAUTOCLAIM` reaper recovers a killed worker; a redelivered job re-runs to the **same** DB state (new=0, gone=0) — idempotency proven | €0 |
| **P3** | COST-ROUTER + LOCAL LLM | P2 | 04, T08 | vLLM+Qwen3.5-4B serving `guided_json`; `classify_kind` writes a *candidate* with `kind_source='classifier'`; the `ingest.py:52` hardcode is **gone** (no row gets `concesionario_oficial` by default); type-resolution ladder resolves a known rent-a-car (OK Mobility) to `rent_a_car_vo`, not `concesionario_oficial`; **the classifier clears the held-out human-labeled gold-set per-kind precision/recall floor (≥0.95 where it is the sole authority) before writing candidates at scale, and the nightly golden-set regression is wired (G-A7)** | €0 |
| **P4** | S-HEALTH WATCHDOG | P2 | 06, 05 | watchdog writes `source_health` on every job outcome; an **injected source fault** produces exactly **one** `alert` row with the exact origin (`<source_key>:<phase>[:<cdp_code>]`) + a circuit-breaker trip + auto-repair attempt; the GONE-storm quarantine refuses a destructive delta exceeding the sanity bound; **the API keeps serving throughout** | €0 |
| **P5** | DEEP VERIFICATION LEDGER | P0, P2 | 05, V1–V6 | `0014` applied: `verification_verdict` superset (generated `quorum_n`/`family_n` + `chk_trustworthy_needs_quorum` CHECK); a TRUSTWORTHY row is **physically unstorable** without ≥2 agreeing values across ≥2 families **AND ≥2 distinct origins** (CHECK widened per G-A30: `family_n ≥ 2 AND origin_n ≥ 2`; proven by a rejected INSERT); hash-chained `verdict_audit` verifies intact; read-only `cardeep_inquisitor` role **exists in `0014` and a write attempt by it is DB-rejected** (G-A16/C-16); **`v_latest_verdict` is materialized** (G-A33, not a hot-path analytical scan); publish-gate views (`v_publishable_entity/inventory`) serve only TRUSTWORTHY+fresh | €0 |
| **P6** | PLATFORM-AS-ENTITY | P0, P2 | 01, 03, 00 | every OPEN platform (00 §1, `is_tier1=false`) minted as `kind=plataforma` entity, province `00`, `platform_meta` row; `SELECT count(*) FROM entity WHERE kind='plataforma'` ≥ 15; the reflexive case proven: one AS24 car owned by a dealer entity + one `platform_listing` edge to AS24 | €0 |
| **P7a** ∥ | PLATFORM WHOLESALE (OPEN) | P3, P5, P6 | 02, 07, 00 | per OPEN platform: curl_cffi recipe committed + full drain via facet-partition with **`Σ leaf-distinct == declared`** (pagination-VAM TRUSTWORTHY) + every listing's selling dealer resolved to an entity + `platform_listing` edge; AS24 → coches.com → autocasion → motor.es drained; ~700k listings landed €0 | €0 |
| **P7b** ∥ | OEM-VO + CHAINS | P3, P5, P6 | 02, 07 | renew/DasWeltAuto/MB/BMW/Hyundai + Flexicar/OcasiónPlus/Autohero/Clicars harvested VAM-stable; chain branches under one `org_id`; per-brand dealer census reconciled; Motorflash used as dealer-discovery multiplier | €0 |
| **P7c** ∥ | LONG-TAIL DENOMINATOR | P5 | 07, V1 | OSM ∪ FSQ ∪ Overture ∪ PA ∪ CCAA registries ingested with provenance; **first capture-recapture estimates** land as coverage `verification_verdict` rows per segment×province; the **DGT-desguace calibration passes** (Chapman over DGT×DesguacesDirecto reproduces N̂≈1.3k with 1,292 in CI) — the method is verified before extrapolation | €0 |
| **P8** | OWN-SITE BY FAMILY + DEFLATE | P3, P7a–c | 02, 07, 01 | CMS/DMS family classification → family recipes → residual own-site harvest; `entity.sells_cars` resolved for **100% of `kind=garaje`** (the deflation reported with cause); ≥1 province: `numerator_sealed_pct ≥ gate` (every entity harvested OR caused-zero OR declared-wall) | €0 |
| **P9** | REPO RESHAPE | P7a–c (recipes exist) | 08 | flat 262 recipes → geo-hierarchical per-entity bundles via the deterministic `git mv` migration; `count(after)==count(before)`; every `dealers/<code>/` matches the Crockford regex with `{NN}` == parent province; `pipeline/`→`engine/`+`sources/`+`platforms/` rename; CI structural guard green (no `sources/`↔`platforms._tier1` import, no Tier-1 recipe in long-tail tree) | €0 |
| **P10** | TIER-1 WALLED | P4, P5, P9 | 00, 02 | per Tier-1 platform: reproducible recipe in `platforms/_tier1/<name>/` + 2-way count + blind-sample field-VAM, **OR** the exact wall parked in `state/tier1-blocked.json` (e.g. "Akamai `_abck`, sensor_data v3, ES residential required"); the Adevinta recipe (advgo) drains coches.net+milanuncios+fotocasa+segundamano; Wallapop app-headers settled | **SPEND / creds** |
| **P11** | INQUISITION + COMPLETION | P5, P7 | V2, V3, V4, V6 | `WF-INQUISITION` runs on a cadence + on every REFUTED with info-starved refuters (INDEP≥2); the V4 detector suite + managed-item state machine live; an entity reaches `COMPLETED` only through the 5 binary gates; an "N completed" claim is published **only at the LQAS-supported confidence** (e.g. "≥18,845 of 20k at 95%"), never the bare count; **Lens-C independence is PHYSICAL not procedural (G-A16/C-16): a "producer judges itself" attempt is rejected, and the `egress_id(skeptic) <> egress_id(producer)` DB CHECK is live** on every live-refetch verdict | €0 (+spend for Lens-C live re-fetch on Tier-1) |
| **P12** | SEAL 52/52 | all | 07, V1, V6 | per-province seal scoreboard live; **52/52 provinces SEALED** (denominator coverage ≥ segment-gate AND numerator sealed) **OR** a declared, caused gap per cell; **denominator N̂ is membership-FILTERED (C-14: C2C/non-POS removed before Chapman); Ceuta/Melilla sealed by direct-census (G-A15); VN/agente residuals itemized (G-A4/A11)**; the KPI panel reports the *caused residual*, never a rounded-up number; **entity-recall AND vehicle-recall (`N̂_V`, C-15) AND `c2c_listed_pct` (G-A8)** reported apart, each with a CI | €0 |

> **Concurrency:** P7a/P7b/P7c run in parallel (different hosts — the rate-limit law). P4
> (health) and P5 (deep ledger) can build alongside P3. P10 (spend) is gated last. P12 is a
> **rolling scoreboard** that closes as the others land — a province seals the moment its cells
> clear, not in a big-bang at the end.

---

## 3. The build sequence (dependency DAG, the order to actually write code)

```
P0 SCHEMA SPINE (0005–0012)
   └─► P1 GOVERNOR + QUEUE (0013) ───────────────────────────────┐
          └─► P2 WORKER FLEET + HANDLERS                          │
                 ├─► P3 COST-ROUTER + LOCAL LLM (fixes ingest:52) │
                 ├─► P4 S-HEALTH WATCHDOG ────────────────────────┤  (06: the "never falls" guarantee)
                 └─► P5 DEEP VERIFICATION LEDGER (0014) ──────────┤  (05+V5: DB-enforced quorum)
                        └─► P6 PLATFORM-AS-ENTITY                  │
                               ├─► P7a PLATFORM WHOLESALE (OPEN) ──┤  ┐ run ∥ (different hosts)
                               ├─► P7b OEM-VO + CHAINS ────────────┤  │
                               └─► P7c LONG-TAIL DENOMINATOR ──────┘  ┘
                                      └─► P8 OWN-SITE FAMILY + DEFLATE
                                             └─► P9 REPO RESHAPE (08, mechanical)
                                                    └─► P10 TIER-1 WALLED (SPEND, last)
                                      ┌──────────────────────────────────┘
                                      └─► P11 INQUISITION + COMPLETION (V2/V3/V4/V6)
                                             └─► P12 SEAL 52/52 (rolling, V1/V6)
```

**The decisive ordering principles** (from the pillars, made operational):
1. **Governor before any scale** (04 §13, 06 §0): the rate-limit is THE bottleneck; nothing
   fetches at scale until the per-host token bucket is the only path to a request. P1 first.
2. **Schema spine before everything that writes** (03 §8): the ontology, org layer, and
   `platform_listing` edge must exist before platform-as-entity (P6) or any platform drain (P7).
3. **Deep ledger before wholesale drain** (05 §8 / V5): so no harvested count is ever served
   un-quorumed; the publish-gate is a bound view from P5 onward.
4. **Platforms wholesale before the long-tail mop-up** (07 §4–5): one AS24 recipe attributes
   278k cars to thousands of dealers and *discovers* them as a side-effect, tightening every
   province's denominator estimate for free. P7 is the hinge.
5. **€0 exhausted before spend** (07 §5): P0–P9 + P11 are all €0; only P10 (Tier-1 walls) spends,
   per-source authorized, last.
6. **The repo reshape is late and mechanical** (08 §11, C-10): build into `pipeline/` through the
   functional phases, reshape once at P9.

---

## 4. The file / folder structure to build (target tree, pillar 08)

Built incrementally; the canonical end-state (after P9). `[NEW]` = introduced; `[EXISTS]` = on disk.

```
cardeep/
├── engine/                  [NEW, P9 from pipeline/]   generic source-agnostic core
│   ├── fetch/   session.py router.py tiers/ solvers.py      tiered fetch (02 §2–8)
│   ├── recipe/  schema.py loader.py heal.py runner.py        recipe parse/validate/self-heal (02 §9)
│   ├── extract/ jsonpath.py jsonld.py sitemap.py next_data.py data-layer extractors (02 law #1)
│   ├── delta/   engine.py events.py                          NEW/GONE/PRICE/PHOTO/KM
│   ├── geo/     resolve.py geocode.py                        INE name→code + lat/lon→province
│   ├── identity/ codes.py canonical.py                       cdp_code (moved from services/api)
│   ├── verify/  vam.py quorum.py inquisition.py denominator.py  VAM + V1–V6 deep validator
│   ├── llm/     local.py                                     vLLM/Qwen client (T08), guided_json
│   └── health/  watchdog.py breaker.py alerts.py repair.py drift.py governor.py   S-HEALTH (06)
├── sources/                 [NEW, P9]    LONG-TAIL discovery + harvest adapters (OPEN only)
│   ├── long_tail/{registries,osm,oem,oem_vo,aggregators,chains}/   classified by modality
│   └── base.py
├── platforms/_tier1/<name>/ [NEW, P10]   TIER-1 ONLY: adapter.py + recipe.yaml + fixtures/  (separate world)
├── countries/ES/            [EXISTS, RESHAPED P9]   the served GEO catalog
│   ├── _platforms/<cdp_code>/   national platform entities (province 00)
│   ├── _orgs/<org_code>/        chain/group/brand roots
│   └── <NN>-<prov>/<comarca>/<city>/dealers/<cdp_code>/{config,recipe}.yaml {manifest,tombstone}.json
├── config/registries/       [NEW, P6/P7]   platforms_es.json sources_es.json oem_brands_es.json
│                                          chains_es.json rentacar_brands_es.json auction_operators_es.json
│                                          cms_families_es.json defense_routing.json   (config-as-registry)
├── migrations/              [EXISTS, GROWN P0/P1/P5]   0001…0015 (+0099 PostGIS optional)
├── services/api/            [EXISTS, GROWN]   FastAPI; routers/ schemas/ + verification API (V5 §8)
├── ops/                     [NEW]   runners/{discover,harvest}_loop.py tier1_run.py · migrate.py · dashboards/
├── state/                   [GITIGNORED]   spend-ledger.json tier1-blocked.json capacity-ledger.json
├── data/                    [GITIGNORED]   ES/<cdp_code>/raw/  +  _tier1/<name>/raw/  (separate subtree)
├── docs/{architecture,research,...}        the pillars + README + this MASTER_PLAN
└── tests/                   [NEW]   mirrors engine/; tests/structure/test_separation.py (CI guard)
```

---

## 5. The cost gates — exactly what needs owner spend

Everything is **€0** except a tightly-scoped Tier-1 wall set, each **per-source authorized**
(07 §5.1, 02 §2 hard rule). The spend gate is checked before any Tier-2 component runs; an
unauthorized wall **parks** with the exact wall named, never silently retried, never faked.

| Needs spend? | Item | Trigger | Basis |
|:--:|---|---|---|
| **NO** | Everything in P0–P9, P11, P12 | open/permissive sources, curl_cffi, local LLM, deterministic | €0 |
| **NO** | Tier-1 whose internal API is open | Wallapop `cars/search` (header-gated), Adevinta advgo POST (token via 1 browser hit) | €0 if no residential needed |
| **YES** | Residential ES proxies (Decodo) | geo-sensitive walls (milanuncios), IP-reputation walls | ~$2–8.50/GB |
| **YES** | Sensor generation (Hyper Solutions) | Akamai `_abck` (Spoticar), Imperva-hardened, PerimeterX | per-call metered |
| **YES** | CAPTCHA/token solvers (2Captcha/CapSolver) | GeeTest (milanuncios), interactive DataDome/Turnstile | per-solve |
| **CREDS** (not money) | B2B accounts | BCA / Autorola / Ayvens full lot data | dealer-account provisioning |

**Two non-money gates** (07 §7.3), respected not spent past: **robots/ToS** (motor.es
`/vercoche/*`, Google Places, Facebook Marketplace — declared scope boundaries) and
**credentials** (B2B auction logins). Every solver/proxy call writes `state/spend-ledger.json`;
a per-source budget cap trips an alert before overspend.

### 5.1 Global spend ceiling + authorization state machine `[G-A12]`
The per-source cap is necessary but **insufficient** — there is no aggregate ceiling and no
persisted authorization record. Added here, binding:
- **Global monthly burn cap.** `state/spend-ledger.json` carries `month_total` and a hard
  `MONTHLY_CEILING`. A **circuit-breaker HALTS all Tier-2 spend** (proxy, sensor, solver) the
  instant `month_total ≥ MONTHLY_CEILING` — not a per-source alert, a fleet-wide stop. Spend
  resumes only on an owner re-authorization that raises the ceiling. This is the CLAUDE.md
  irreversibility-gate mechanized at the aggregate, where money is irreversible.
- **Authorization is a persisted state machine**, not a verbal "owner authorized it":
  `parked → authorized(source, cost_basis, ceiling, expires_at) → consumed → re-auth-required`.
  An authorization record lives in `state/spend-auth.json` with the **cost basis it was granted
  under** (Decodo is $2–8.50/GB, volume-dependent) and an **expiry**. If the realized cost basis
  drifts past the authorized basis (e.g. low volume pushes $2/GB → $8.50/GB), the authorization
  **auto-revokes** and re-parks the source for re-authorization — an authorization at $2/GB never
  silently becomes an $8.50/GB drain.
- **Per-request sensor cost is modeled, not a single mint `[G-A19]`.** For full-sensor walls
  (Akamai `_abck`, DataDome), a minted clearance cookie does NOT make subsequent Tier-0 requests
  human — the cookie replayed from a datacenter IP at curl-pace re-scores as bot on the next
  request. So a walled drain is **N sensor calls metered per page**, not one mint then cheap. The
  cost estimate for any full-sensor Tier-1 drain (e.g. a 50k-listing Spoticar/Akamai drain) is
  computed as `pages × sensor_cost_per_call`, and that figure is the authorization basis — the
  mint-then-drain shortcut applies ONLY to cookie-ISSUANCE walls (passive CF/Incapsula), declared
  per source in the registry's `wall_class ∈ {cookie-issuance, full-sensor}`.

---

## 6. The definition of "100% done" — refutable, per segment × province

100% is **two closures** (07 §1): the **denominator** (found every entity) and the **numerator**
(extracted every car). Each has a binary seal; neither is ever a rounded-up number.

### 6.1 Per-segment seal gates (segment-specific because closability differs, 07 §6.1, V1)
| Segment | Gate | Why |
|---|--:|---|
| SEG-1 desguace | **1.00** (exact) | DGT CAT legal census = exact denominator (1,292), not estimated |
| SEG-2 official | **0.98** | OEM locators near-complete; 2% = locator drift |
| SEG-3/7 platforms | **1.00** (enumerated, `complete` set only — G-A13) | hand-enumerable list; `open-probe` platforms (VGRS, OEM subsites, industriales) are a declared discovery gap, not sealed |
| SEG-4 compraventa | **0.90** | long-tail; 90% of the capture-recapture estimate is the honest ceiling of free discovery |
| SEG-5 garaje | **0.85** (of selling subset) | hardest to enumerate; gate on the `sells_cars=true` subset, not raw workshops |
| SEG-6 rentacar/subasta | **1.00** (curated) | curated lists complete by construction |
| Ceuta/Melilla (51/52) | **direct-census** (G-A15) | autonomous cities; tiny fully-observable universe, comarca grid N/A, hand-enumerable — NOT capture-recapture |

### 6.2 The seal predicate (per province P, per segment) `[updated: C-14/C-15/G-A4/A11/A15]`
```
N̂ᶠ  = MEMBERSHIP-FILTERED capture-recapture estimate (C-14): every capture list passed
       through the ontology-§1 predicate ("offers car stock for acquisition") FIRST —
       C2C-sentinel rows removed, garaje sells_cars=false removed, non-POS removed —
       BEFORE Chapman. found and N̂ᶠ are drawn from the SAME predicate. Seal uses N̂ᶠ_lower.
       (N̂_raw, the unfiltered "all-listed" count, is context only, NEVER the seal frame.)

DENOMINATOR-SEALED(seg,P)  ⇔  coverage(seg,P) = found / N̂ᶠ_lower  ≥  GATE(seg)
                              OR the shortfall is a DECLARED, CAUSED gap
                                 (no-province-data | spend-gated-wall | known-empty-segment
                                  | VN-no-live-feed[official] | open-probe-platform)
                              OR seg∈{SEG-1, Ceuta/Melilla, SEG-6} uses an EXACT/direct census
                                 (no estimate; G-A15)
   with N̂ᶠ carrying a TRUSTWORTHY verification_verdict (orthogonal pairs agreed + DGT
            calibration held + anchors respected + closure-window gate passed, G-A10:
            no capture-pair whose seen_at spread exceeds 30d; CI widened by BORME churn)

NUMERATOR-SEALED(entity)   ⇔  Σ harvested == declared (count-quorum)        -- harvested-stable
                              OR verified no online stock (caused-zero)     -- TRUSTWORTHY, claim='no_online_stock'
                              OR only stock behind a declared spend/creds wall  -- parked, exact wall
                              OR stock inherited from a resolved parent (agente, G-A11)
                                 -- caused-inherited, counted against PARENT, served_via:<parent>
                              OR new-vehicle-only configurator stock (concesionario, G-A4)
                                 -- caused VN-no-live-feed, declared_gap{shape:'new_vehicle'}
       NOTE: an entity's VO numerator can seal while its VN residual is a DECLARED gap —
             the two are reported apart, never the VN absence read as "covered".

VEHICLE-SEALED(seg,P)      ⇔  vehicle_recall = N_V_held / N̂_V  measured with CI (C-15)
                              OR cell vehicle-recall UNVERIFIED (no orthogonal vehicle capture)
       -- numerator completeness is a MEASURED fraction, not the false closure
          "entities sealed ⇒ all cars found".

PROVINCE-SEALED(P)         ⇔  every segment denominator-sealed AND every numerator-relevant entity
                              numerator-sealed AND vehicle-recall measured-or-declared per cell
SPAIN-SEALED               ⇔  52/52 provinces SEALED (Ceuta/Melilla via direct-census)
```
The forbidden state is **unknown** (not harvested, no verdict) — that is an open cell, never
reported as covered. A REFUTED VAM blocks the seal.

### 6.3 The honest KPI panel (V5 §9, V6 §6) — every number with its derivation `[updated]`
- `found` (DB), `N̂ᶠ ± 95% CI` (membership-FILTERED capture-recapture, C-14), `coverage = found/N̂ᶠ`
  with its band. `N̂_raw` shown as "all-listed" context, labeled NOT the seal frame.
- `numerator_sealed_pct` (any honest state — caused-zero/caused-inherited/caused-VN **count as
  sealed**, each itemized).
- `harvested_pct` (the subset actually drained).
- `declared_gap`, **itemized by cause** — a gap with a cause is honest; a gap without one is a bug.
  Causes now include `VN-no-live-feed`, `open-probe-platform`, `agente-inherited`,
  `ceuta-melilla-direct-census`, `vehicle-recall-unverified`.
- **entity-precision** (acceptance-sampling, internal frame) **and** **entity-recall**
  (membership-filtered capture-recapture, external frame) **and `vehicle_recall`** (`N_V_held/N̂_V`,
  C-15) **and `classifier_accuracy`** (per-kind, gold-set, G-A7) reported **apart**, each with a CI
  — never an F1 average that launders a failure.
- **`c2c_listed_pct`** (G-A8): C2C-attributed listings as a fraction of all-listed Spanish cars —
  the single line that stops dealer-segment coverage being read as market coverage.
- **`cross_seller_dup_ci`** (G-A3/26): every served platform/national rollup counter carries its
  measured cross-seller duplication bound; a counter inflated by an *unmeasured* amount is forbidden.
- The deflation (e.g. garaje 7,200 → N selling) reported as a **correction with cause**, never
  hidden as a loss.

> **What 100% honestly IS** (07 §6.3): every *findable* POS found (coverage ≥ gate), every
> *harvestable* car harvested (VAM-stable), every residual *declared with an exact cause*. What it
> is **NOT**: a claim that literally zero dealers in Spain are unknown (unprovable), or that C2C
> private sellers are enumerated (out of scope, attributed to the platform sentinel). The honesty
> is in the **caused residual**, never a fabricated 100.00%.

---

## 7. Cross-cutting invariants (true in every phase, enforced structurally)

1. **Identity is immutable and source-independent** — one `cdp_code` per real POS, deterministic;
   re-discovery converges, never duplicates (01 §6, 03 §1, enforced by `UNIQUE` + deterministic key).
2. **Ownership singular, membership plural** — a vehicle is owned by exactly one selling entity
   (never a platform); platform membership is the `platform_listing` edge (03 §1, the failure-#2 fix).
   A platform drain stages to `listing_staging` and only INSERTs a `vehicle` AFTER its seller is a
   resolved, geocoded entity (C-13) — never a placeholder/platform owner. A second-platform sighting
   of an already-owned car becomes a `platform_listing` edge, not a second `vehicle` row (G-A3/26).
3. **State is a projection of an append-only log** — `vehicle` is the snapshot cache;
   `vehicle_event` is immutable truth (the `cardeep_block_mutation` trigger raises on UPDATE/DELETE).
   The snapshot UPDATE and its `vehicle_event` INSERT are **one DB transaction**, and each event
   carries an idempotency key `(vehicle_ulid, event_type, source_diff_hash)` UNIQUE — so XAUTOCLAIM
   redelivery is exactly-once-per-real-mutation, never a double-emitted or lost delta (G-A14).
4. **Never UPDATE a non-mutated row** — INSERT-new + close-gone; only a mutated field updates +
   emits its event; unchanged → refresh `last_seen` only; history retained forever.
5. **Tier-1 separated on disk + ops, NOT in the data** (G-A32) — the six axes are filesystem/ops;
   Tier-1 and long-tail share tables/partitions (`is_tier1` is a column). The data-axis blast radius
   (a bad `DELETE`/migration) is guarded by the row-count sanity bound + GONE-storm quarantine (06),
   not by `rm`. The shared Adevinta recipe lives at `platforms/_tier1/_shared/adevinta/` (deleting
   one platform never orphans it); open platforms legitimately straddle long-tail code + `_platforms/`
   catalog, and the CI guard checks "no Tier-1-walled helper imported by a long-tail/open adapter".
6. **Verify by an orthogonal path, always** — nothing TRUSTWORTHY without ≥2 paths across ≥2
   families **AND ≥2 distinct origins** (the DB CHECK is widened to `family_n ≥ 2 AND origin_n ≥ 2`,
   G-A30 — origin-distinctness is DB-enforced, not trusted to application code); the DB CHECK (V5)
   makes a TRUSTWORTHY lie unstorable.
7. **The API never falls; the harvester may** — the API serves the DB on a separate pool; a source
   break degrades *freshness*, never *availability* or *integrity* (06 §1, §9). The publish-gate
   reads a **materialized** `v_latest_verdict` (not a hot-path analytical scan), and a continuous
   re-verification cadence (C-11 TTLs) keeps the served set fresh — so the freshness gate withholds
   individual stale rows without the served DATA collapsing wholesale between harvest cycles (G-A33).
8. **Confess the gap, never paint it** — UNVERIFIED/REFUTED/QUARANTINED are first-class, served
   labeled or withheld; a contested number is never served as fact.
9. **Spend the minimum that is correct** — three routers (transport/throughput/cognition), €0
   everywhere except the per-source-authorized Tier-1 walls.
10. **Everything to `main`, reproducible** — recipes/config/schedules/ledgers committed; raw crude
    ephemeral and regenerable from the recipe; state on disk/DB, never only in a worker's memory.

---

## 8. Honest residuals carried from the pillars (no makeup)

1. **`geo_comarca` is empty** (0 rows) — the per-province seal is computable today; the
   per-comarca stratum the mandate names awaits an INE/CCAA comarcal source load. A grid gap, not
   a coverage lie. The comarca/city seal is now a **placement-completeness** gate, not a second
   capture-recapture (G-A6), and a geo-resolution-drift detector watches sentinel-placement rate. (07 §9.1)
2. **Capture-recapture orthogonality is an assumption, audited not proven** — defended by mechanism
   + calibrated on the DGT known-truth; subtle source-correlation is a confessed limit, detected
   (pairwise-disagreement alarm) not prevented. **The common-direction dedup bias** (invisible to the
   disagreement alarm) is now calibrated by a **hand-labeled ground-truth dedup audit** (G-A21/29),
   and the CNAE firm→point ratio ρ̄ is measured before CNAE is used as a Chapman capture. (V1 §3, V6 §4.4)
3. **Auction lots (v2) and desguace parts (v2)** are defined-not-harvested — v1 seals their
   *denominator* (operators/centres/CATs), defers their *numerator* with declared scope. (01 §8, 03 §9)
4. **Cross-seller same-car dedup is now v1-bounded, not deferred-blind** — a STRONG-key cross-seller
   resolver (VIN/pHash≤6) collapses second-platform sightings into edges (G-A3/26), and the residual
   over-count carries a **measured CI** on every served counter; a knowingly-inflated-by-an-unmeasured-
   amount counter is forbidden. (03 §6, V6 vehicle-recall)
5. **Scale is designed-for with a reversible re-partition path, not committed blind** — the worst hot
   partition ('00' C2C) is sub-partitioned by platform HASH (G-A28); province `LIST` skew and
   forever-event-log volume are estimated BEFORE 0008/0011 are final, the LIST→sub-HASH change is
   documented as reversible, and the headline is reconciled to "~1–2M live, tens-of-millions lifetime
   incl. gone-history" (G-A34). Prune plans still need `EXPLAIN` once volume lands. (03 §9.7)
6. **The deep validator (V1–V6), the Inquisition, and S-HEALTH are blueprinted-not-running** — the
   tables/columns the live `0004` provides are the foundation; P4/P5/P11 are the wiring. (05 §10, 06 §0)
7. **Tier-1 totals are mostly `[ASSUMED]`** until the spend-gated recipe lands; SEG-7 coverage is
   estimated-against-an-estimate until then, reported as such. (00 §3, 07 §9.5)

---

## 9. The one-line statement of done

> CARDEEP is done when every *findable* Spanish car point of sale is found and uniquely coded,
> every *harvestable* car is harvested with VAM-stable counts and live delta, the platforms are
> first-class entities with the same car a member of both its platform and its dealer, Tier-1 is
> separated absolutely, a broken source fires an exact-origin alert and self-repairs without the
> API falling, the denominator is a *measured* fraction with a confidence interval (not a guess),
> and **52/52 provinces are SEALED or carry a declared, caused gap** — with the API serving only
> the trustworthy and confessing every residual, **never a single number it cannot prove by a path
> other than the one that made it.**

---

## 10. Legal & data-protection threat model `[adversarial GAP-23 — a category the corpus omitted]`

CARDEEP is a **commercial, served, monetizable database of scraped EU data**. The corpus respected
a few named robots/ToS exceptions but never modeled the *systemic* legal surface — a gap that can
void the served-product premise regardless of engineering cleanliness. This section is a first-class
threat axis, gated like spend.

### 10.1 GDPR — personal data of identifiable EU persons
Dealer listings, and especially **C2C private-seller listings** (Wallapop/Milanuncios), are personal
data of identifiable EU persons. "Attributed to the platform sentinel" removes the *fabricated-dealer*
problem but **not** the GDPR exposure of having fetched/stored that data.
- **RULE (binding): C2C personal-data minimization.** C2C private-seller data is stored as
  **aggregate counts attributed to the platform sentinel, NOT as per-listing personal data retained**.
  We keep the count and the platform attribution; we do not persist the private seller's name, phone,
  or precise location as a served row. This is the data-protection form of the §4.3 sentinel doctrine.
- Dealer (B2B) data is processed on the legitimate-interest basis appropriate to a commercial
  registry; the served surface exposes the business POS, not private individuals.

### 10.2 EU Database Directive — the sui-generis right
coches.net / AS24 / Adevinta have made substantial investment in their databases; **wholesale
aggregation** is the exact fact pattern of Spanish/EU scraping litigation (the Ryanair-style line).
- **RULE: a `legal_class` field on the Tier-1 registry** records each source's sui-generis exposure.
  Wholesale aggregation of a `legal_class='protected-db'` source is gated behind an **explicit owner
  decision**, distinct from the spend gate. We harvest the *facts* (a car exists, its price) which are
  not themselves the protected DB structure, and we never re-publish a competitor's DB wholesale.

### 10.3 Circumventing a technical protection measure (TPM)
Reading open HTML and **defeating a sensor wall (Akamai/DataDome) via paid solvers** have different
legal characters; the anti-detection sophistication (sensor generation, ES residential proxies,
GeeTest solving) is precisely what raises the TPM-circumvention question.
- **RULE: `legal_class='tpm-circumvention'` sources require OWNER AUTHORIZATION, not merely spend
  authorization.** A wall that needs sensor/solver defeat is parked with both its spend basis AND a
  distinct legal authorization flag; it is never auto-resumed by a spend-ceiling raise alone. This is
  the legal arm of the CLAUDE.md irreversibility gate.

### 10.4 The honest position
CARDEEP's defensible posture is **facts not structure, businesses not private persons, open before
walled**. The legal residual is itemized like any other declared gap; a source whose legal class is
unresolved is **open-cell**, never silently harvested into the served product.

---

## 11. Gaps closed — adversarial review audit index `[2026-06-12]`

This section records the disposition of all 35 adversarial-review gaps. Every gap was verified
against source this session; **all 35 are real and accurately described** (none dismissed as
not-a-gap). Each is closed by a binding decision / new section / new gate in the docs below. Where an
item is **deferred**, it is *implementation-scoped* (writing code / labeling a set / running a load
test) — the **doc gap** (the missing decision/method/gate) is closed here; the build is deferred to
its phase, which is the correct disposition for a documentation-architecture task.

### Closed (decision/method/gate added)
| Gap | Title | Closed by |
|---|---|---|
| GAP-1 | Recall/denominator paradox (unfiltered Chapman frame) | C-14; V6 §4.7; seal §6.2; KPI §6.3 |
| GAP-2 | Vehicle-recall has no estimator | C-15; V6 §4.8; seal §6.2 `VEHICLE-SEALED`; KPI §6.3 |
| GAP-3 | Cross-seller over-count served as trustworthy, unbounded | G-A3/26; 03 §6; residual #4; KPI `cross_seller_dup_ci` |
| GAP-4 | VN/km0 out of scope, undeclared | G-A4; 01 §2.1; seal §6.2 `caused VN-no-live-feed` |
| GAP-5 | Four incompatible freshness SLA taxonomies | C-11 (single TTL matrix; gate==detector) |
| GAP-6 | No comarca/city seal + no geo-drift detector | G-A6; V4 `geo_resolution_drift`; residual #1 |
| GAP-7 | LLM classifier has no accuracy floor / drift detector | G-A7; T08 §; V4 `classifier_drift`; P3 gate |
| GAP-8 | C2C volume excluded but never sized | G-A8; KPI `c2c_listed_pct` |
| GAP-9 | Inquisition independence procedural, not gated | C-16; P5 + P11 gates; `0014` role + egress CHECK |
| GAP-10 | No BORME adapter; closed-population not enforced | G-A10; `borme.py` in census; V1 closure-window gate |
| GAP-11 | agente_oficial (3,642) numerator seal undefined | G-A11; 01 §2.2; seal `caused-inherited` |
| GAP-12 | No global spend ceiling / auth state machine | G-A12; §5.1 (ceiling + circuit-breaker + auth record) |
| GAP-13 | SEG-3/7 1.00 on a confessed-incomplete list | G-A13; `enumeration_status`; seal §6.1 |
| GAP-14 | Delta not exactly-once under redelivery | G-A14; invariant #3 (single txn + idempotency key) |
| GAP-15 | Ceuta/Melilla make 52/52 unreachable | G-A15; seal §6.1/§6.2 `direct-census` |
| GAP-16 | Engine unbuilt; €0 untested | G-A16; phase **P0.5** validation spike |
| GAP-17 | PQ ClientHello stale; cross-session identity | G-A17; 02/T05; P0.5 ClientHello byte self-test |
| GAP-18 | Walled APIs unresolved but budgeted €0 | G-A18; P0.5 mandatory spike outputs |
| GAP-19 | Sensor walls per-request; mint-then-drain over-generalized | G-A19; §5.1 per-request sensor cost line |
| GAP-20 | Stealth-engine disagreement (camoufox/patchright/nodriver) | C-12 (T02 governs; patchright primary; pinned VCS) |
| GAP-21 | Dedup circularity; no ground-truth audit | G-A21/29; V1 §; residual #2 |
| GAP-22 | Closed-population violated by multi-month timeline | folded into G-A10 (closure-window gate) |
| GAP-23 | Legal/GDPR/sui-generis/TPM surface omitted | new **§10** legal threat model + `legal_class` |
| GAP-24 | AIMD probing trains the behavioral detector | G-A24; 06 (two pacing regimes by defense tier) |
| GAP-25 | LLM classify/dedup plane unverified (dup of GAP-7) | G-A7 (same gold-set + drift gate) |
| GAP-26 | One-car-one-row unenforceable at ingest | C-13 staging + G-A3/26 resolver; invariant #2 |
| GAP-27 | Ownership-first vs platform-wholesale-first order | C-13 (stage→resolve→promote) |
| GAP-28 | C2C sentinel detonates `vehicle_p_00` | G-A28; 03 §4 ('00' HASH sub-partition + per-platform owner) |
| GAP-29 | Denominator gated on untrusted dedup (dup of GAP-21) | G-A21/29 (same ground-truth audit + ρ̄) |
| GAP-30 | `family_n` cannot see origin-distinctness | G-A30; V5 §3.1 `origin_n`; CHECK widened; invariant #6 |
| GAP-31 | 0008 swap not zero-downtime / preserve-all | G-A31; 03 §4.1 preflight + atomic rename; P0 gate |
| GAP-32 | Tier-1 separation pierced (DB/recipe/straddle) | G-A32; invariant #5; 08 shared-recipe + data-axis guard |
| GAP-33 | `v_latest_verdict` un-materialized; expiry shrinks served set | G-A33; V5 §3.4 materialize + cadence; invariant #7 |
| GAP-34 | Scale numbers inconsistent; partitions undersized | G-A34; residual #5; reversible re-partition path |
| GAP-35 | Eviction deletes the artifact replay needs | G-A35; V5 §7 pin-crude-while-TRUSTWORTHY; 08 evict.py skip |

### Deliberately deferred (implementation-scoped, doc gap closed)
The following are **not open architecture gaps** — the decision/method/gate is now in the docs; the
remaining work is execution and lands in the named phase:
- **BORME adapter code** (`sources/long_tail/registries/borme.py`) — decision + census slot added
  (G-A10); the adapter is written in the long-tail-denominator phase (P7c). *Reason:* writing the
  source code is a build task, not an architecture decision.
- **The human-labeled gold sets** (classifier accuracy G-A7; dedup ground-truth G-A21/29; CNAE ρ̄
  sub-sample) — the gates and floors are specified; the *labeling* is a one-time data task in P3/P7c.
  *Reason:* a doc cannot contain the labels; it can and now does mandate the floor and the regression.
- **The P0.5 spike's actual live re-probe** of the 7 targets — the phase, predicate, and "re-sequence
  if hardened" rule are added; the probe is run at P0.5. *Reason:* the probe is the phase's work; the
  plan's job was to *require* it before the €0 ordering is trusted, which it now does.
- **Load-test `EXPLAIN` of the partition model** (G-A34) — the reversible re-partition path and the
  pre-commit estimation obligation are documented; the EXPLAIN runs once real volume lands. *Reason:*
  it requires production-scale data that does not yet exist.
- **Auction-lot / desguace-parts numerator** (pre-existing residual #3) — unchanged; still v2 scope
  with a sealed denominator. *Reason:* out of v1 by prior design decision, not a review gap.
