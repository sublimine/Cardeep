# CARDEEP — 05 · The Verification Architecture (VAM, Inquisition, Capture-Recapture, Publish-Gate)

> **Pillar document.** Cardeep's mandate ends with one non-negotiable clause: *a LIVE,
> VERIFIED database*. This doc is the **judge of "verified"**. It distrusts every number
> the system produces — including its own — and confirms each claim by a path **different
> from the one that produced it**. Its prime directive: **better confess a gap than serve a
> lie.** Nothing reaches the API unless it has survived a quorum of orthogonal verification.
>
> It governs four machines and one gate:
> 1. **VAM** — multi-path adversarial verification: a quorum of ≥2 orthogonal paths per
>    claim, the **landed-count invariant** (the count that actually lives in the DB must
>    agree — ingestion loss is never masked), and **per-field live verification**
>    (price-trap, year-band, km-band).
> 2. **The Inquisition** — a **separate adversarial verifier chain**: one agent asserts a
>    fact, another, with no access to the first's method, tries to **refute** it. Verdict by
>    confrontation, not by self-report.
> 3. **Capture-Recapture (Chapman)** — the estimator of the **true denominator** of Spanish
>    car points-of-sale, by crossing orthogonal censuses (Páginas Amarillas, registral
>    CNAE-45, OSM/FSQ, DGT). Tells us what 100% *is*, so "coverage" is a real fraction.
> 4. **The Publish-Gate** — the rule that **nothing not TRUSTWORTHY is served**. The API's
>    materialized truth is exactly the set of claims that passed VAM + Inquisition.
>
> **Builds on what exists, supersedes nothing it cannot replace.** The substrate is already
> in the repo and **[VERIFIED]** alive: `migrations/0004_verification_health.sql`
> (`verification_verdict`, `source_health`, `alert`), `pipeline/verify.py`
> (`record_count_verdict`, the quorum rule + landed-count invariant already coded),
> `pipeline/discover.py` and `pipeline/ingest.py` (both already close with a VAM gate),
> `entity_source` (the capture-recapture substrate — one entity, N orthogonal attestations).
> This doc takes that seed to its full, rigorous form.
>
> **Anchor reality (read before designing):** `docs/research/SOURCES_ES.md §6` (the
> denominator triangulation), `docs/architecture/01-ENTITY-ONTOLOGY.md` (what counts as an
> entity; the dedup `cdp_code`), `docs/architecture/02-SCRAPING-ENGINE.md §7` (the
> pagination-VAM reconcile gate it feeds), `docs/architecture/00-TIER1-REGISTRY.md`
> (per-platform declared counters, the price/year traps), `docs/ORQUESTACION.md`
> (WF-INQUISITION, the cost doctrine).
>
> **Marking discipline.** Every claim is **[VERIFIED]** (read from repo / DB / live this
> session) or **[ASSUMED]** (inferred, not opened). No placeholders, no stubs.

---

## 0. The threat model — every way a number can lie

Verification is only as good as its enumeration of failure modes. This is the exhaustive
list of how a Cardeep number can be **wrong while looking right**, each mapped to the
machine that catches it. Designing the verifier without this list is designing against an
imagined adversary.

| # | Lie | Concrete Cardeep instance | Caught by |
|--:|---|---|---|
| L1 | **Fetched ≠ landed** (silent ingestion loss) | `db_ingested < fetched` from a `cdp_code` collision or a skipped row, masked because `fetched == declared` | VAM landed-count invariant (§2.3) — already coded `[VERIFIED, verify.py:41]` |
| L2 | **Source counter over/under-counts** | AS24 `numberOfResults` counts duplicate live-set rows; a dealer counter inflates | VAM quorum: a lone divergent path can't refute when ≥2 independent paths agree (§2.2) `[VERIFIED, verify.py:34-43]` |
| L3 | **Pagination cap truncates** | `while page<=max_pages` stops at the cap; a 3000-car dealer reads as ~1000 | Pagination-VAM `Σ leaf-distinct == declared` (§2.5, feeds SCRAPING-ENGINE §7) |
| L4 | **Field parsed wrong but plausible** | `mileageInKm` `{raw,formatted}` unwrap bug → `km=6,594,865,948` `[VERIFIED, PROGRESO F3 cause #2]`; price off by ×1000 | Per-field live verification: km-band, price-trap (§3) |
| L5 | **Stale data served as live** | a dealer 404s; the engine keeps serving last snapshot as `available` | Liveness/freshness check (§3.4) + source_health (§5) |
| L6 | **Type/identity drift** | AS24 "profesional" mis-typed `concesionario_oficial` when it's a `rent_a_car_vo` `[VERIFIED, ONTOLOGY failure #1]`; two slugs → one `cdp_code` collapse | Identity-VAM (§4.6) + Inquisition type-refutation |
| L7 | **Denominator unknown** | "12,862 entities" with no idea if that's 30% or 90% of Spain | Capture-Recapture Chapman (§6) |
| L8 | **Self-confirmation** | the agent that scraped a number also "verifies" it → circular | The Inquisition: refuter has no access to the asserter's path (§5) |
| L9 | **Counter drift mistaken for error** (false alarm) | AS24 278,329 today vs 278,163 yesterday is *normal* drift, not a break | Drift-tolerant bands + trend, not point equality (§3.3, §7) |
| L10 | **A platform breaks silently** | coches.com Imperva flips to active; harvest returns 0; DB still shows yesterday's stock | source_health watchdog + exact-origin alert + publish-gate demotion (§5, §8) |
| L11 | **Photo/VIN dedup miss** | same physical car on AS24 + coches.net counted twice across platforms | photo_hash quorum (§4.4, single-seller v1 per ONTOLOGY §4.2) |
| L12 | **Verifier itself rots** | the golden sample ages; bands drift; the verifier passes garbage | Verifier meta-audit (§9): the Inquisition audits the auditor |

The rest of this document is the construction that closes every row of this table.

---

## 1. Doctrine (the five laws of Cardeep verification)

Priority order; on conflict, lower number wins. These are the verification specialization of
the sovereign mandate ("verify EVERYTHING, distrust every number, confirm by a different
path, confess a gap before selling a lie").

1. **ORTHOGONALITY OR IT DOESN'T COUNT.** A claim is verified only by a path that does **not
   share the failure mode** of the path that produced it. Re-reading the same JSON twice is
   one path, not two. The asserting scraper and the verifying probe must be able to fail
   *independently* (different surface, different parser, different network, ideally different
   agent). Two correlated paths are one path wearing a disguise.

2. **THE LANDED COUNT IS THE ONLY COUNT THAT MATTERS.** "Fetched 78" is a claim about the
   wire; "78 rows queryable in `vehicle`" is a claim about the truth we serve. The verifier's
   primary path is **always** the post-ingest DB count. `fetched == declared` can never, by
   itself, read TRUSTWORTHY — it would mask ingestion loss (L1). Already enforced
   `[VERIFIED, verify.py:38-43]`; this doc generalizes it to every subject type.

3. **CONFESS THE GAP, NEVER PAINT IT.** `UNVERIFIED` and `REFUTED` are first-class, valuable
   outcomes — they route an entity *out* of the served set and *into* an exact-origin alert.
   A fabricated TRUSTWORTHY is the one unforgivable failure (the CLAUDE.md §antialucinación
   line, mechanized). The verifier is rewarded for finding gaps, never for hiding them.

4. **THE VERIFIER IS ADVERSARIAL, NOT COOPERATIVE.** Verification is not a checksum the
   producer runs on itself; it is a **prosecution**. The default posture is *guilty until a
   refutation attempt fails*. The Inquisition (§5) institutionalizes this: a separate chain
   whose explicit job is to **break** each claim. A claim survives by resisting refutation,
   not by asserting itself.

5. **CHEAP DETERMINISTIC VERIFY EVERYWHERE; EXPENSIVE ADVERSARIAL VERIFY ON WHAT MATTERS.**
   Per the cost doctrine `[VERIFIED, ORQUESTACION.md]`: the count-quorum, band checks, and
   landed-count invariant are **deterministic Python** (`pipeline/verify.py`, runs on every
   ingest, €0, linear). The **Inquisition** (agent-driven adversarial re-derivation) is
   **expensive intelligence** spent only where the stakes justify it: Tier-1 platform
   counters, the denominator estimate, type-resolution disputes, and any REFUTED escalation.
   Verifying everything cheaply is the floor; prosecuting the load-bearing claims is the ceiling.

---

## 2. VAM — the multi-path adversarial quorum

VAM (Verificación Adversarial Multi-vía) is the deterministic engine. It answers one
question for any *quantitative* claim: **do ≥2 orthogonal paths agree, including the path
that represents what actually landed?** Verdict ∈ `{TRUSTWORTHY, REFUTED, UNVERIFIED}`,
persisted to `verification_verdict` `[VERIFIED, migrations/0004]`.

### 2.1 The subject taxonomy (what VAM judges)

Every verifiable claim is a `(subject_type, subject_key, claim)` triple. The current code
emits two subject types `[VERIFIED]`; this doc defines the full set the system must cover.

| `subject_type` | `subject_key` | The claim | Orthogonal paths (the quorum) |
|---|---|---|---|
| `source` | `source_key` (e.g. `dgt_cat`) | "entities discovered == declared" | `db_ingested` · `fetched` · `source_declared` `[VERIFIED, discover.py:115]` |
| `entity_inventory` | `cdp_code` | "available stock == source-declared count" | `db_available` · `harvested` · `source_declared` `[VERIFIED, ingest.py:113]` |
| `entity_field` | `cdp_code` | "this entity's geo/CIF/type is correct" | registral CNAE · OEM locator · geo round-trip (§4) |
| `vehicle_field` | `vehicle_ulid` | "price/km/year are real, not a parse artifact" | band check · cross-listing · re-fetch (§3) |
| `count` (segment) | segment label (e.g. `desguace_ES`) | "this segment's national total == X" | DGT census · directory · capture-recapture (§6) |
| `denominator` | `auto_pos_ES` | "true total POS in Spain == N̂ ± CI" | Chapman over PA × CNAE × OSM × DGT (§6) |
| `platform_listing` | `(vehicle, platform)` | "same physical car, not a double-count" | photo_hash · VIN · seller-attribution tuple (§4.4) |
| `delta` | `cdp_code` | "this PRICE/GONE event is real, not churn" | re-fetch confirmation · stable-sort dedup (§7) |

### 2.2 The quorum rule (formal, as coded and extended)

The rule already in `verify.py` `[VERIFIED]`, stated formally and generalized:

Given paths `P = {p₁:v₁, …, pₙ:vₙ}` (path → value), with the **primary path** `p₁` = the
landed truth (DB count) by convention:

```
if |{pᵢ : vᵢ ≠ null}| < 2:                    → UNVERIFIED   (no quorum possible)
else:
    let mode      = the value supported by the most paths
    let mode_n    = how many paths support it
    let rivals    = {v ≠ mode : ≥2 paths support v}     (a competing super-claim)
    let primary_agrees = (≥2 paths, including p₁, share p₁'s value)
    let divergence = (max(v) − min(v)) / max(v)

    if mode_n ≥ 2 and rivals = ∅ and primary_agrees:   → TRUSTWORTHY  (clean majority, landed)
    elif divergence ≤ tolerance:                        → TRUSTWORTHY  (all within drift band)
    else:                                               → REFUTED      (real disagreement)
```

Three properties make this a *real* verifier and not a rubber stamp:

- **A lone over-counting path cannot refute** (L2). If `db_available=78`, `harvested=78`, and
  a noisy `source_declared=81`, the two independent paths agreeing at 78 win; the source
  counter is recorded as divergent but does not poison the verdict. This is exactly the
  AS24-duplicate-counter case the pilot hit `[VERIFIED, PROGRESO F3]`.
- **`primary_agrees` is the landed-count invariant** (§2.3, law #2): the DB count *must* be
  one of the ≥2 agreeing paths. A `fetched=declared` pair that the DB silently failed to land
  is **REFUTED**, never TRUSTWORTHY. This was the hardening the owner forced
  `[VERIFIED, PROGRESO "VAM endurecido"]`.
- **`rivals` detects a split.** If two paths say 100 and two say 130, there is no clean
  majority → REFUTED, not a coin-flip. Orthogonal disagreement at scale is a *finding*, not
  noise to be averaged away.

### 2.3 The landed-count invariant (L1 — the heart of "never mask ingestion loss")

The mandate's deepest verification clause: *the actually-landed db count MUST agree.* This is
not a nicety; it is the difference between a database that *claims* completeness and one that
*has* it. Mechanized as the **`primary_path` convention**: every `record_count_verdict` call
passes the DB count as a path, and the verdict logic requires it to be in the agreeing set.

Generalized rule for **every** ingest path, codified as the verifier's contract:

```
INVARIANT (landed): for every ingest of a slice S,
    db_count(S, after)  −  db_count(S, before)   ==   |distinct(harvested(S))|   −   |gone(S)|
    AND  db_count(S, after)  ==  one of the ≥2 quorum-agreeing paths
otherwise  →  REFUTED  +  alert(origin=source_key, severity=critical, message="ingestion loss")
```

Worked instance from the live system `[VERIFIED]`: `ingest.py` reconciles harvest↔DB
(NEW/GONE/PRICE/PHOTO/KM), then queries `SELECT count(*) … status='available'` and feeds that
DB count as `db_available` into the quorum — so a row that failed to insert (FK violation,
collision) drops the DB count below `harvested` and trips REFUTED. The province-range guard
(`01 ≤ province ≤ 52`, `ingest.py:41`) and the AS24 postcode-89 FK fix `[VERIFIED, PROGRESO]`
are the *honest-skip* counterpart: a row that *cannot* land is excluded transparently
(`excluded_out_of_scope`, `discover.py:90`) and removed from the gate's denominator, never
silently dropped into a false pass.

### 2.4 Tolerance bands — drift is not error (L9)

A naïve `==` verifier alarms on every counter tick and is therefore useless on live data. VAM
uses **per-subject-type tolerance**:

| Subject | Tolerance | Rationale |
|---|---|---|
| `source` (registries: DGT, OEM locators) | `0.0` (exact) | A legal/registral census is a fixed set; any drift is a real bug `[VERIFIED: DGT 1292=1292=1292, Kia 241=241]` |
| `entity_inventory` (a dealer's stock) | `0.0` within a single harvest; drift band across harvests | Within one snapshot the three paths describe the *same* fetch; across time the live set moves |
| `count` / platform counters | live-drift band (default **2%**, per-platform tunable) | AS24 +166 / coches.net +219 day-over-day are normal `[VERIFIED, SOURCES_ES §7]`; the band must admit them and still catch a 30% collapse |
| `denominator` | confidence interval, not a point | Capture-recapture yields N̂ ± CI; "agreement" = overlapping intervals (§6) |

The band is **asymmetric-aware**: a counter *dropping* 30% overnight is a far stronger break
signal than rising 30% (new stock is normal; vanished stock is a wall). The drift detector
(§7) carries a per-source EWMA baseline and flags **velocity**, not just level.

### 2.5 Pagination-VAM (L3) — the reconcile gate that feeds the scraping engine

The scraping engine partitions a query space by facets until each leaf fits under the
pagination cap, then unions `[VERIFIED, 02-SCRAPING-ENGINE §7]`. VAM is the **acceptance gate**
on that union:

```
Σ (distinct listing-ids across all leaves)   ==   declared_count(slice)    (within band)
```

If the union of facet-partitioned leaves does not reconcile to the slice's own declared count,
the slice is `UNVERIFIED` and re-partitioned — **a dealer larger than the page cap can never
silently truncate to the cap** (the L3 failure the old `while page<=max_pages` loop had
`[VERIFIED, autoscout24.py:283-308]`). This is the same `record_count_verdict` machine, with
paths `{distinct_union, declared, db_landed}`. The scraping pillar produces the partitions;
this pillar judges whether they sum to the truth.

### 2.6 Orthogonality enforcement (law #1, mechanized)

The verifier must **prove** its paths are orthogonal, or the quorum is theater. Each path
carries a `path_class` tag; the quorum requires **≥2 distinct classes**:

```
path_class ∈ { db_landed, source_counter, independent_refetch, registral, geo_roundtrip,
               cross_listing, photo_hash, census_external, capture_recapture }
```

Rule: `db_landed` + `source_counter` from the **same fetch** are *not* orthogonal (both die if
the fetch is wrong) → they count as **one** class for quorum purposes; a genuine second class
(an `independent_refetch` via a different surface, or a `cross_listing` on another platform, or
a `registral` CIF match) is required for TRUSTWORTHY on high-stakes subjects. This upgrades the
current 3-path-but-same-fetch quorum to a **provably-orthogonal** quorum for Tier-1 and
denominator claims, while keeping the cheap same-fetch quorum for the long-tail (cost doctrine).

> **Schema delta (additive, sibling-migration's job):** `verification_verdict` gains
> `path_classes JSONB` (the class of each path) and `quorum_classes INT` (distinct classes
> that agreed). The existing `verifier_paths`/`independent_values` JSONB columns already
> carry the raw paths `[VERIFIED, migrations/0004]`; this adds the orthogonality proof on top,
> no destructive change.

---

## 3. Per-field live verification — the price-trap, year-band, km-band (L4, L5)

Count quorum proves *how many*; it says nothing about whether each row's **fields** are real.
A dealer can have exactly 78 cars, all counted correctly, every one with a price that is a
parse artifact. Per-field verification is the second axis of VAM — **per record, per field,
against bands and against a re-fetch.**

### 3.1 The trap catalog (the bands, grounded in real Spanish car data + real bugs)

Each field has a **plausibility band** (rejects the impossible) and a **trap rule** (catches
the *plausible-but-wrong* — the dangerous class, L4). Bands are validated against the live DB
distribution, not invented.

| Field | Plausibility band | Trap rule (the subtle lie) | Grounded in |
|---|---|---|---|
| `price` | €300 – €500,000 (retail VO) | **×1000 / ÷1000 trap:** a Porsche at €89 or €89,010,000 — same digits, wrong scale. Flag if `price` is off the make/model/year median by >1 order of magnitude | Porsche Taycan €89,010 verified correct `[VERIFIED, PROGRESO F3]`; the inverse is the trap |
| `km` | 0 – 500,000 | **digit-doubling trap:** `{raw,formatted}` unwrap bug yielded `km=6,594,865,948` `[VERIFIED, PROGRESO F3 cause #2]` → reject `km > 5,000,000` (recipe `bounds` `[VERIFIED, 02-SCRAPING-ENGINE §9.1]`) AND flag `km` inconsistent with `year` |
| `year` | 1900 – (current+1) | **year-band vs km coherence:** a 2024 car with 280,000 km, or a 1998 car at €60,000, is a parse swap or a fraud listing → cross-check `year × km × price` jointly | recipe `bounds: year [1900,2100]` `[VERIFIED]`; tightened to (current+1) here |
| `make`/`model` | in the canonical make/model dictionary | **null-model trap:** make present, model null at >threshold rate → field-map broke (selector drift) | recipe `validation.required` `[VERIFIED]` |
| `photo_url` | resolvable, image content-type | **dead-image trap:** 404 / placeholder / hash-of-known-placeholder → listing is stale or fabricated | photo_hash column exists `[VERIFIED, migrations/0003]` |
| `deep_link` | resolvable PDP, 200 | **stale-link trap (L5):** link 404s but row still `available` → must flip to `gone` | the GONE delta semantics `[VERIFIED, ingest.py:104-109]` |

### 3.2 The year-band / price-trap as a joint plausibility model

The strongest per-field check is **not** per-field — it is the **joint** distribution. A used
car's `(make, model, year, km, price)` live on a known manifold: a 2015 Golf with 90k km sells
for €9–14k, not €90k or €900. The verifier maintains, per `(make, model, year-band)`, a
**price interquartile range** and a **km interquartile range** computed from the live DB
itself (self-calibrating, no external feed). A row outside the IQR by a tunable factor is not
auto-rejected (real bargains and lemons exist) — it is **flagged for re-fetch** (§3.3). The
**×1000 price trap** and the **digit-doubled km trap** are precisely the points that land
orders of magnitude outside the IQR, so this one model catches both real bugs the system
already hit, *structurally*, before they reach the API.

> This is the cost doctrine applied to fields: the IQR model is **deterministic** (computed by
> a SQL window over `vehicle`, €0); only rows it flags get the **expensive** re-fetch or
> LLM-classifier adjudication.

### 3.3 The orthogonal re-fetch (the second path for fields)

A flagged field is verified by **re-fetching the single PDP through a different surface than
the bulk harvest used** (law #1 orthogonality): if the dealer was drained via `__NEXT_DATA__`
on the SRP, the re-fetch reads the **PDP JSON-LD** (a different parser over a different
artifact). Agreement → the outlier is real (a genuine bargain), promote to TRUSTWORTHY.
Disagreement → the bulk parse is wrong → REFUTED + `alert(origin=source_key, field=…,
observed=…, expected_band=…)` + recipe drift signal (§7). This is the per-field analogue of the
count quorum: **two orthogonal reads of the same fact.**

### 3.4 Liveness / freshness (L5) — "served" must mean "still true"

A row is only honestly `available` if it was **confirmed present in the most recent successful
harvest**. The freshness invariant:

```
vehicle.status='available'  ⇒  vehicle.last_seen ≥ entity.last_successful_harvest
```

A row whose `last_seen` predates the entity's latest good harvest but was **not** marked
`gone` is a **liveness leak** (the harvest succeeded but the reconcile missed it). The verifier
sweeps this nightly per entity; a leak trips an alert and forces a reconcile. This closes the
"stale-served-as-live" hole that a pure count quorum cannot see (the counts can match while
*which* rows are stale).

> **Schema note:** `entity.last_seen` exists `[VERIFIED, migrations/0002]`; this invariant
> wants a distinct `entity.last_successful_harvest TIMESTAMPTZ` (additive) so "we touched the
> row" (`last_seen`) and "we successfully drained the source" (`last_successful_harvest`) are
> not conflated. A source that 403s must **not** advance `last_successful_harvest` — otherwise
> a wall reads as "fresh empty stock" (the L10 silent-break, the most dangerous of all).

---

## 4. Entity & identity verification (L6) — the type, the geo, the dedup

The inventory can be perfect while the **entity** is wrong: mis-typed, mis-located, or
collapsed with another. Identity-VAM verifies the node before its stock.

### 4.1 Type-resolution verdict (the failure-#1 catch, mechanized)

`01-ENTITY-ONTOLOGY.md §6.5` defines the type-resolution **precedence** (registral CNAE > OEM
locator > legal census > curated brand-list > LLM classifier > platform label) and the
`entity.kind_source` column recording which rung decided. The verifier's job: **assert the
precedence was respected, and that a higher rung never lost to a lower one.**

```
VERDICT(entity_type):  TRUSTWORTHY  iff  kind_source = the HIGHEST-precedence signal available
                                          for this entity, AND no orthogonal signal contradicts.
                       REFUTED      iff  a higher-precedence signal disagrees with the stored kind
                                          (e.g. platform said concesionario_oficial, but the curated
                                           rent-a-car brand-list matches → must be rent_a_car_vo).
```

This is the OK-Mobility-mis-typed-as-concesionario case `[VERIFIED, ONTOLOGY failure #1 + D-6]`,
turned into a standing verifier: any entity whose `kind` rests on `platform_label` while a
higher rung is *available but unused* is REFUTED and re-typed — deterministically, no phantom
delta, just a type correction (`01-ENTITY-ONTOLOGY §6.5`).

### 4.2 Geo round-trip verification

An entity's geo is verified by a **closed loop**: `(province_code, municipality_code)` →
INE name → re-resolve name → must return the **same** code. The INE invariant
`province_code == municipality_code[:2]` `[VERIFIED, ARCHITECTURE.md]` is asserted on every
entity. A `cdp_code` whose embedded province (`CDP-ES-{prov}-…`) disagrees with
`entity.province_code` is a **minting bug** → REFUTED. This catches the DGT `COD_INE`
misalignment the pilot already found (`COD_INE` said 19→Madrid when 19 is Guadalajara
`[VERIFIED, PROGRESO F3 cause #1]`) — the verifier would have flagged it instead of a human.

### 4.3 Dedup / collision verification (the `cdp_code` audit)

The whole pillar rests on `cdp_code` uniqueness-and-non-collapse. Two failure directions, both
verified:

- **Under-merge (duplicate entity):** two `cdp_code`s that are the same real POS (name+geo
  near-match across `entity_alias`) → flagged for alias-merge. The `entity_alias` table is the
  substrate `[VERIFIED, migrations/0002]`.
- **Over-merge (collapse):** N real branches collapsed into one `cdp_code` — the Hyundai
  175→48 collapse the system already hit `[VERIFIED, PROGRESO]` when a portal *path* was used
  as a domain identity. The verifier asserts the `canonical_key` invariant: a **path-bearing
  URL is never an identity** `[VERIFIED, codes.py:42-47]`, and the multi-branch-brand rule
  (`D-12`: rent-a-car / chain brands key on name+muni+address, not bare domain
  `[VERIFIED, ONTOLOGY §6.3]`). An org with N known branches but <N `cdp_code`s is REFUTED.

### 4.4 Cross-platform vehicle identity (L11) — the photo_hash quorum

The same physical car on AS24 *and* coches.net must be **one** `vehicle` with two
`platform_listing` edges, not two cars (`01-ENTITY-ONTOLOGY §4.2`). v1 scope = **within a
single seller's stock** (cheap, high precision). The match-key quorum, in priority:

```
VIN (rare, authoritative)  >  photo_hash equality (the strongest practical signal —
                              the same dealer uploads the same photos everywhere
                              [VERIFIED, ONTOLOGY §4.2])  >  (make,model,year,km,price-band) tuple
```

`photo_hash` (pHash) already lives in `vehicle` `[VERIFIED, migrations/0003]`. The verifier
treats a cross-listing photo_hash match as a **second orthogonal path** confirming the
vehicle's identity (and de-duplicating the platform double-count). Cross-*seller* identity is
explicitly **out of v1 scope** (over-merge risk, `[VERIFIED, ONTOLOGY §4.2 / residual #4]`) —
confessed, not faked.

### 4.5 C2C and platform-sentinel verification

Private-seller (wallapop/milanuncios) listings have a platform membership but **no real dealer**
(`01-ONTOLOGY §4.3`). The verifier asserts the **ownership invariant** holds without fabricating
dealers: every `vehicle` has exactly one owner, C2C cars owned by the per-platform
`c2c_private` sentinel entity. A C2C car attributed to a *real* `cdp_code` (a fabricated dealer)
is REFUTED — the denominator counts **real** points of sale, never phantoms.

### 4.6 Platform-as-entity self-consistency

A `kind=plataforma` entity (AS24, coches.net) must (a) carry the `00` province sentinel
(`CDP-ES-00-…`, `D-13` `[VERIFIED, ONTOLOGY §6.3]`), (b) own **no** vehicles directly (its
inventory is the union of `platform_listing` edges, not ownership, `D-10`), and (c) have its
declared counter reconcile to the count of edges pointing at it (within drift band). A platform
that *owns* vehicles, or whose edge-count diverges from its counter beyond the band, is REFUTED.

---

## 5. The Inquisition — the separate adversarial verifier chain (L8)

VAM (§2–4) is deterministic and runs *inside* the pipeline. The **Inquisition** is the
**second, physically separate** verification chain — the institutional embodiment of law #4
and the mandate's *"one agent asserts, another refutes."* It exists because **a system cannot
be the sole judge of its own truth**: the agent that scraped a number shares every blind spot
of its own method. The Inquisition imports an **independent adversary** with a different method
and a mandate to **break** the claim.

### 5.1 The assert/refute protocol (structural separation)

```
        ┌──────────────────────────────────────────────────────────────────┐
        │  CLAIM under prosecution  (a TRUSTWORTHY VAM verdict, or a number  │
        │  the pipeline wants to publish: a count, a denominator, a type)    │
        └───────────────┬──────────────────────────────────────────────────┘
                        │
        ┌───────────────▼────────────┐        ┌──────────────────────────────┐
        │  ASSERTER (agent A)         │        │  REFUTER (agent B)            │
        │  states the fact + its      │  ╳───  │  has NO access to A's path;   │
        │  EXACT method/path          │  no    │  must re-derive by an         │
        │  (e.g. "AS24 = 278,329 via  │  shared│  ORTHOGONAL path and try to   │
        │   numberOfResults")         │  method│  PROVE A WRONG                │
        └───────────────┬────────────┘        └───────────────┬──────────────┘
                        │                                      │
                        └──────────────┬───────────────────────┘
                                       ▼
                         ┌──────────────────────────────┐
                         │  CONFRONTATION                │
                         │  agree (within band) → UPHELD │ → verification_verdict
                         │  disagree → CONTESTED         │ → alert + escalate (§5.3)
                         │  B can't derive → INCONCLUSIVE│ → stays UNVERIFIED (not served)
                         └──────────────────────────────┘
```

The **hard separation** is the whole point and mirrors the Tier-1 separation doctrine
(`ARCHITECTURE.md §Separación Tier-1`): the refuter is a *different agent run* with *no sight*
of the asserter's tool, surface, or intermediate output — only the bare claim. If the refuter
could see "I used `numberOfResults`," it would re-walk the same trap. Orthogonality is enforced
by **information starvation**, not by good intentions.

### 5.2 What the Inquisition prosecutes (scope — expensive intelligence, spent well)

Per the cost doctrine, the Inquisition does **not** re-verify every long-tail row (VAM already
did, cheaply). It prosecutes the **load-bearing, expensive-to-be-wrong** claims:

1. **Tier-1 platform counters** — wallapop ~750k, milanuncios ~667k, coches.net 248,648
   `[VERIFIED, 00-TIER1-REGISTRY §1]`. A wrong giant counter mis-sizes the whole mission. The
   refuter re-derives by a different surface (e.g. asserter used the SRP counter; refuter sums
   the facet-partition leaves, or hits the internal API total).
2. **The denominator estimate** (§6) — the single most consequential number in Cardeep
   ("are we at 30% or 90% of Spain?"). Prosecuted every time it's recomputed.
3. **Type-resolution disputes** (§4.1) where rungs disagree — the asserter claims
   `concesionario_oficial`, the refuter checks the rent-a-car brand-list and FACONAUTO.
4. **Every REFUTED verdict** before it becomes a public alert — to distinguish a true break
   (L10) from a verifier false-positive (L9), so the on-call origin alert is never noise.
5. **The Director's own re-derivation** — already practiced manually `[VERIFIED, SOURCES_ES §7:
   "5/5 confirmadas" via independent curl]`. The Inquisition **automates and persists** that
   discipline as `WF-INQUISITION` `[VERIFIED, ORQUESTACION.md]`.

### 5.3 Verdict, persistence, escalation

The confrontation result is written to `verification_verdict` with `subject_type` prefixed
`inquisition:` and the refuter's independent value in `independent_values` — so the audit trail
shows **both** the asserted and the refuting path, forever. A `CONTESTED` confrontation:

- fires `alert(origin=exact subject_key, severity=critical, message="Inquisition contested:
  asserter=X via P_a, refuter=Y via P_b")` — the **exact origin** the mandate demands;
- demotes the subject **out of the served set** (publish-gate, §8) until adjudicated;
- escalates to a **third-path tiebreak** (a Director re-derivation or a registral cross-check)
  — never an average of two disagreeing numbers (law #2: a wrong landed count is not "half
  right").

### 5.4 Anti-collusion (keeping the chain honest)

The Inquisition's value collapses if asserter and refuter quietly share state. Guards
(extending the anti-collision contract `[VERIFIED, ORQUESTACION.md §contrato]`):

- Refuter receives **only** `(subject_type, subject_key, claim, asserted_value)` — never the
  asserter's `verifier_paths`, tool, or raw crude.
- Refuter must declare its **own** `path_class`; the confrontation is **void** (→ INCONCLUSIVE,
  stays unserved) if it collides with the asserter's class (law #1).
- The refuter agent runs from a **clean context** (no shared scratch files); its only inputs
  are the claim and the live world. This is why the Inquisition is a *separate workflow*, not a
  function call inside the producing one.

---

## 6. Capture-Recapture (Chapman) — estimating the TRUE denominator (L7)

Coverage is meaningless without a denominator. "12,862 entities" `[VERIFIED, live DB]` is a
number with no scale: it could be a third of Spain or nearly all of it. Capture-recapture
turns the orthogonal censuses we already have into a **statistical estimate of the total**,
with a confidence interval — so "we are at X% of Spain" becomes a *measured*, defensible claim.

### 6.1 The method (why it fits Cardeep exactly)

Two independent samples of the same population, with a known overlap, estimate the unseen.
Classic Lincoln–Petersen, with the **Chapman bias-correction** (mandatory for the moderate
sample sizes here — the raw estimator is biased upward for small overlaps):

```
              (n₁ + 1)(n₂ + 1)
   N̂_Chapman = ───────────────── − 1
                  (m + 1)

   n₁ = entities in source 1   n₂ = entities in source 2   m = entities in BOTH (the overlap)

   Var(N̂) = (n₁+1)(n₂+1)(n₁−m)(n₂−m) / [(m+1)²(m+2)]      → 95% CI = N̂ ± 1.96·√Var
```

Cardeep already has the **perfect substrate** for `m`: `entity_source` records, for each
`cdp_code`, **every** source that attested it `[VERIFIED, migrations/0002; discover.py:79-82]`.
The overlap `m` between any two sources is a single SQL query — **no new data collection is
needed to compute the denominator**, only to read the attestations already stored. This is the
"capture-recapture substrate" the orchestration doc names `[VERIFIED, ORQUESTACION §contrato 3]`.

```sql
-- overlap m between source A and source B, by segment (illustrative)
SELECT count(*) FROM (
  SELECT entity_ulid FROM entity_source WHERE source_key = 'paginasamarillas'
  INTERSECT
  SELECT entity_ulid FROM entity_source WHERE source_key = 'osm'
) AS both;
```

### 6.2 The orthogonal source pairs (grounded in the census triangulation §6)

The estimate is only valid if the two samples are **independent** (one source's inclusion
doesn't cause the other's). Cardeep's sources are genuinely orthogonal in their sampling
mechanism — that's the whole strength of the census `[VERIFIED, SOURCES_ES §6]`:

| Pair | Source 1 (mechanism) | Source 2 (mechanism) | Independence rationale |
|---|---|---|---|
| **Total POS** | Páginas Amarillas ~44k (commercial directory, self-listing) | OSM/FSQ (volunteer/geo mapping) | A business self-lists in PA for ads; OSM maps it for geography — uncorrelated inclusion |
| **Registral cross** | CNAE-45 registral (legal obligation: 4511/4519/4520) | PA (commercial) | Legal registration vs commercial advertising — orthogonal |
| **Desguace (anchor)** | DGT CAT census 1,292 (legal, authoritative) | DesguacesDirecto 1,386 / AEDRA 615 (trade directories) | Legal census vs trade membership — and DGT is the *known truth*, so this pair **calibrates the method** (N̂ must land near 1,300) |
| **Concesionario** | FACONAUTO 2,018 (association) | Σ OEM locators (manufacturer truth) | Association membership vs OEM franchise list — orthogonal |

### 6.3 Calibration on a known-truth segment (the method's own verification)

The denominator estimator must itself be verified (L12). The **desguace segment is the test
fixture**: its true total is *known* (DGT = 1,292, exact `[VERIFIED]`). Running Chapman over
(DGT × DesguacesDirecto) **must** produce N̂ ≈ 1,300 with the true value inside the CI. If it
doesn't, the independence assumption is violated for that pair and the method is unsafe to
extrapolate to the unknowable segments (garajes, compraventas). **A capture-recapture estimate
is only trusted after it reproduces the one segment whose answer we already know.** This is the
Inquisition prosecuting the estimator with a fact it cannot dodge.

### 6.4 Multi-source closure & the honest CI

Two sources give one estimate; Cardeep has **many** (PA, OSM, FSQ, DGT, CNAE, OEM locators,
chains). The full closure uses **k-source capture-recapture** (a log-linear / Schnabel census
over all attestation patterns in `entity_source`), which tightens the CI and models
source-dependence explicitly. v1 ships the **pairwise Chapman matrix** (every source pair → an
N̂, cross-checked for agreement); v2 fits the log-linear model. The deliverable is **never a
single magic number** but **N̂ ± CI**, with the census's honest framing preserved: floor **~44k
verified** (PA, a hard lower bound — you can't be below what you've literally counted), ceiling
**~50–90k** `[VERIFIED, SOURCES_ES §6]`. Coverage is then reported as
`served_entities / N̂` with its own interval — a *confessed* range, never a false precision.

### 6.5 What capture-recapture does NOT claim (honest residue)

- It estimates the population **reachable by the sampling sources**; truly invisible POS (a
  garage in no directory, no map, no registry, with zero web presence) are outside any sample
  and outside the estimate. The estimate's CI does **not** cover them — stated, not hidden.
- The **`sells_cars` filter** (`D-4`, the 30k unfiltered talleres `[VERIFIED, ONTOLOGY §2.4`])
  must be applied *before* the garaje denominator, or N̂ inflates by non-selling workshops. The
  denominator is over the **entity** population (§1 membership predicate), not the directory
  population.
- Independence is an **assumption, audited** (§6.3 calibration), never asserted. A pair that
  fails calibration is dropped from the estimate with a logged reason.

---

## 7. Drift detection & self-healing wiring (L9, L10, L12)

The verifier must run forever without a human watching, distinguishing a **real break** from
**normal drift**, and firing an alert with the **exact origin** when (and only when) something
is actually wrong. This wires the verification verdicts into the existing `source_health` /
`alert` tables `[VERIFIED, migrations/0004]` — currently empty (`0` rows `[VERIFIED, live DB]`),
the gap this design closes.

### 7.1 The per-source baseline & velocity check

Each source carries an **EWMA baseline** of its declared count and its field-null rates
(persisted; the recipe's golden sample is the seed `[VERIFIED, 02-SCRAPING-ENGINE §9.3]`). On
each harvest the verifier compares **velocity**, not level:

```
break signal  iff  |Δcount| / baseline  >  drift_band      (default 2%, per-source)
                   OR  field_null_rate  >  golden_null_rate + drift_alert_threshold  (0.15 [VERIFIED])
                   OR  declared count drops ≥ 30% (asymmetric: vanished stock = wall, §2.4)
                   OR  harvest returned 0 while last_successful_harvest had >0  (L10 silent break)
```

### 7.2 The exact-origin alert (the mandate's "alerta con el origen exacto")

A break writes one `alert` row with the **precise** origin — `source_key`, and where relevant
`field`, `cdp_code`, `phase`, observed-vs-expected `[VERIFIED, alert.payload JSONB exists]` —
and updates `source_health` (`consecutive_fails++`, `status → degraded|down`). This is wired so
the on-call sees **"as24 / field=km / observed-null-rate 0.4 vs golden 0.05 / recipe drift"**,
not "something broke." The `alert.origin` column is exactly this `[VERIFIED, migrations/0004:36]`.

### 7.3 Self-repair loop (closing F7)

```
break → alert(exact origin) → source_health.status=degraded
   → router escalates tier (02-SCRAPING-ENGINE §9.4) OR re-hunts the recipe (drift)
   → next harvest verifies → if VAM TRUSTWORTHY again: source_health.status=healthy,
                                                        alert.resolved_at=now()
   → if still REFUTED after N retries: status=down, escalate to Inquisition + human
```

Cardeep "never falls" not because sources never break — they will — but because a break is
**detected, attributed to its exact origin, and self-repaired or escalated**, while the
publish-gate (§8) protects the served truth in the meantime. The repair is bounded: a source
`down` past its retry budget is **parked** with the exact wall (the Tier-1 `state/tier1-blocked`
pattern `[VERIFIED, 02-SCRAPING-ENGINE §2]`), never silently retried into a spend or a fake.

### 7.4 The verifier audits the verifier (L12)

The most insidious failure is a **rotted verifier** that passes garbage. Guards:

- The **golden-sample drift detector** is itself checked: if a recipe's golden sample is older
  than its cadence, the verifier flags *itself* (the band may be stale).
- The **denominator calibration** (§6.3) re-runs on the known-truth desguace segment every
  cycle; a calibration miss alarms the *method*, not the data.
- The **Inquisition periodically prosecutes a TRUSTWORTHY claim chosen at random** — a verified
  number that *should* survive re-derivation. If it doesn't, the verifier (not the world)
  changed, and that is a critical meta-alert. The auditor is audited.

---

## 8. The Publish-Gate — nothing not TRUSTWORTHY is served (L all)

The gate is where verification becomes **consequence**. The mandate: *"a LIVE, VERIFIED
database"* — the API serves **only** what passed. Verification that doesn't gate publication is
decoration.

### 8.1 The rule

```
A fact is SERVED by the API   ⇔   its latest verification_verdict = TRUSTWORTHY
                                   AND it is not currently CONTESTED by the Inquisition
                                   AND its source_health.status ∈ {healthy, degraded}   (not down)
                                   AND it satisfies the freshness invariant (§3.4)
```

Applied per granularity:

| Granularity | Gate |
|---|---|
| **Entity** | served iff its identity-VAM (§4) is TRUSTWORTHY (type, geo, dedup all pass) |
| **Inventory count** | served iff `entity_inventory` quorum TRUSTWORTHY (landed == ≥2 paths) |
| **Individual vehicle/field** | served iff per-field verification passed; a REFUTED field is **withheld or flagged**, never shown as fact |
| **Segment / denominator** | published with its verdict **and CI**; an UNVERIFIED segment is shown as "estimate, unverified," never as truth |
| **Delta event** | served iff confirmed real (not pagination churn, §2.5) |

### 8.2 Three served states, never a binary lie

A pure served/not-served binary would force the system to *drop* honest-but-unconfirmed data —
itself a kind of lie (hiding what we found). Instead, every served object carries its
**verification state**, surfaced in the API envelope `meta` `[VERIFIED, main.py:34 envelope
{ok,data,error,meta}]`:

```json
{ "ok": true,
  "data": { "...": "..." },
  "meta": { "verification": "TRUSTWORTHY",        // or UNVERIFIED / CONTESTED
            "quorum_classes": 2,
            "verified_at": "2026-06-12T...",
            "denominator_coverage": { "served": 12862, "estimate": 51000, "ci": [44000, 90000] } } }
```

- **TRUSTWORTHY** → served as fact.
- **UNVERIFIED** → served **only** behind an explicit `?include_unverified=1` flag, always
  labeled — the consumer can never mistake it for confirmed truth.
- **CONTESTED / REFUTED** → **withheld** from the default response; available only on the
  diagnostics endpoint, with the exact origin. A contested number is **never** served as fact.

This realizes law #3 at the API boundary: we **confess** the gap (we show the unverified count
exists, labeled) rather than either faking it TRUSTWORTHY or pretending it doesn't exist.

### 8.3 Gate wiring (additive, on the existing API)

The current API serves raw DB rows `[VERIFIED, main.py]`. The gate adds a verification join:
each served entity/inventory/delta response is filtered/annotated by its latest
`verification_verdict` (and, for counts, the live `denominator` estimate). New diagnostics
endpoints expose the machinery for operators:

```
GET /verification/{cdp_code}        → the entity's verdicts (type, geo, inventory, fields)
GET /verification/denominator       → N̂ ± CI per segment + coverage %
GET /alerts?unresolved=1            → exact-origin breaks (source_health + alert join)
GET /inquisition/{subject_key}      → assert vs refute trail for a prosecuted claim
```

No destructive change to the live endpoints; the gate is a **filter + meta annotation** over
the truth the pipeline already lands, plus read-only diagnostics over the verdict tables that
already exist `[VERIFIED, migrations/0004]`.

---

## 9. The contract this pillar hands the other pillars

Stated as obligations, so the system converges (the verifier is cross-cutting — it touches
every pillar):

1. **To the scraping engine (`02`):** every harvest MUST emit the three count paths
   (`db_landed`, `harvested`, `source_declared`) and MUST partition-then-reconcile (§2.5)
   before the slice is accepted. The recipe `validation` gate (bounds, required) is the
   per-field verifier's first line `[VERIFIED, 02 §9.1]`. A harvest that 403s MUST NOT advance
   `last_successful_harvest` (§3.4) — the single most important wiring to prevent L10.
2. **To the entity ontology (`01`):** `entity.kind_source` MUST be populated so type-VAM (§4.1)
   can assert precedence; the `platform_listing` edge and `c2c_private` sentinel MUST exist so
   ownership/identity invariants (§4.4–4.6) are checkable. These are the ontology's own schema
   deltas `[VERIFIED, 01 §6.4]`.
3. **To the Tier-1 registry (`00`):** every Tier-1 platform's declared counter is an Inquisition
   prosecution target (§5.2); the registry's per-platform price/year/km characteristics seed
   the trap bands (§3.1).
4. **To the migration pillar:** the additive schema deltas this doc needs —
   `verification_verdict.path_classes`/`quorum_classes` (§2.6),
   `entity.last_successful_harvest` (§3.4), and the `denominator` verdict subject (§6) — are
   small, additive, reversible, and consistent with the existing `0004` design `[VERIFIED]`.
5. **To orchestration (`ORQUESTACION`):** `WF-INQUISITION` is the separate adversarial chain
   specified in §5; it runs to a cadence and on every REFUTED, with information-starved refuters.

---

## 10. Honest residue (no makeup)

1. **The Inquisition is agent-driven and therefore costs.** It is scoped (§5.2) to load-bearing
   claims by the cost doctrine, but a genuinely thorough prosecution of *every* Tier-1 counter
   on *every* harvest is not free. v1 prosecutes on a cadence + on REFUTED; continuous
   prosecution of all giants is a spend-gated v2.
2. **Capture-recapture independence is an assumption, audited not proven.** §6.3 calibrates it
   on the desguace known-truth; a segment whose sources are secretly correlated (e.g. one
   directory scraped another) will bias N̂. The calibration catches gross violations; subtle
   correlation is a confessed limit, mitigated by the multi-pair cross-check (§6.4).
3. **Cross-seller vehicle dedup is out of v1** (§4.4) — the photo_hash quorum is single-seller
   only; a car genuinely listed by two *different* dealers is two real listings and is **not**
   merged (over-merge risk). The platform double-count within one seller is caught; across
   sellers it is accepted as a known, bounded over-count.
4. **The freshness invariant needs `last_successful_harvest`** (§3.4), not yet in the schema —
   until it lands, "fresh" leans on `entity.last_seen`, which conflates "row touched" with
   "source successfully drained." Stated as the top-priority additive delta.
5. **`source_health` and `alert` are empty today** (`0` rows `[VERIFIED, live DB]`). The
   watchdog (§7) is *designed and wired in spec* but **not yet running** — F7 in the battle
   order `[VERIFIED, ORQUESTACION §6]`. This doc is its blueprint; the tables and the alert
   origin column already exist `[VERIFIED, migrations/0004]`, so it is wiring, not new
   foundation.
6. **The denominator is a range, forever.** Truly invisible POS (no directory, no map, no
   registry) are outside every sample (§6.5). Cardeep's coverage claim is honestly
   `served / N̂ ∈ [floor, ceiling]`, never a single triumphant percentage. The mandate is
   served by *confessing* that bound, which is exactly law #3.

---

## 11. Summary — the verification architecture in one screen

| Machine | Catches | Mechanism | Substrate (exists / delta) |
|---|---|---|---|
| **VAM quorum** | wrong counts, ingestion loss (L1,L2,L3) | ≥2 orthogonal paths, landed-count primary, drift bands | `verify.py` + `verification_verdict` `[VERIFIED]` |
| **Per-field VAM** | parse artifacts, stale rows (L4,L5) | price-trap / km-band / year-coherence IQR + orthogonal re-fetch | recipe `validation` `[VERIFIED]`; +IQR model |
| **Identity-VAM** | mis-type, collapse, double-count (L6,L11) | type-precedence assert, geo round-trip, `cdp_code` audit, photo_hash quorum | `codes.py` + `entity_alias` + `platform_listing` `[V / delta]` |
| **The Inquisition** | self-confirmation (L8) | separate chain, info-starved refuter, assert-vs-refute confrontation | `WF-INQUISITION` `[VERIFIED, ORQUESTACION]` |
| **Capture-Recapture** | unknown denominator (L7) | Chapman over `entity_source` attestations, calibrated on DGT truth | `entity_source` `[VERIFIED]` |
| **Drift / self-heal** | silent breaks, false alarms, rotted verifier (L9,L10,L12) | EWMA velocity, exact-origin alert, repair loop, verifier-audits-verifier | `source_health` + `alert` `[VERIFIED tables, F7 wiring]` |
| **Publish-Gate** | serving any lie (all) | TRUSTWORTHY-only served, 3 states (trustworthy/unverified/contested), labeled `meta` | `main.py` envelope `[VERIFIED]` + verdict join |

The architecture honors the mandate to the atom: it **verifies everything** (VAM on every
ingest), **distrusts every number** (adversarial posture, law #4), **confirms by a different
path** (orthogonality, law #1, mechanized by path-class and information-starved refuters),
**never masks ingestion loss** (landed-count invariant, law #2), **knows what 100% is**
(capture-recapture), **fires an exact-origin alert and self-repairs** when a source breaks
(§7), **separates the adversarial chain absolutely** (the Inquisition, §5), and **serves only
the trustworthy** while **confessing every gap** (the publish-gate, §8, law #3). Better a
confessed gap than a sold lie — built, not asserted.
