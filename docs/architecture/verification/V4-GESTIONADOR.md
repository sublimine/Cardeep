# V4 — EL GESTIONADOR · Lie & Gap Detection Manager

> Facet of the CARDEEP Supreme Validator. Siblings: V1-DENOMINATOR-PROOF,
> V2-COMPLETION-PROOF, V3-INQUISITION, V5-LEDGER-API, V6-STATISTICAL-RIGOR.
> This document supersedes and expands the light `05-VERIFICATION-VAM` in the
> master architecture set for the management/routing layer.
>
> **Creed:** CARDEEP never serves a lie. A number is not "good" because it was
> produced; it is good only when an *independent* path fails to refute it. The
> Gestionador is the organ that **continuously hunts for the lie**, turns each
> suspicion into a tracked managed item, and **routes it to closure**. Nothing
> serves while quarantined.

Anti-hallucination contract for this doc: every reference to a table, column,
field, file, or live number is marked `[VERIFIED]` (read from the repo) or
`[ASSUMED]` (design proposal not yet in code). Detectors that require a new
column/table are flagged `NEEDS-MIGRATION` and the exact DDL delta is given so
V5-LEDGER-API can absorb it.

---

## 0. Position in the validator

```
  PRODUCERS                 V3 INQUISITION              V4 GESTIONADOR
  (pipeline/*)              (independent re-derivation)  (this doc)
  ─────────                 ────────────────────────     ──────────────
  discover  ┐                                            DETECTORS scan the
  harvest   ├─► writes ──►  re-derives claims by      ►  ledger + live DB +
  ingest    │   facts &     orthogonal paths,            recipe baselines, emit
  recipe    │   verdicts    emits TRUSTWORTHY/REFUTED    MANAGED ITEMS, ROUTE each
  api       ┘                                            to AUTO_FIX / RESEARCH /
                                                         QUARANTINE / ESCALATE,
                                                         track to closure, and
                                                         gate the publish surface.
```

The Inquisition (V3) answers *"is this single claim reproducible?"*. The
Gestionador answers *"across the whole live DB, where is a lie or a gap forming,
who fixes it, and may we keep serving while it is open?"*. V3 is a verifier; V4
is a **manager with a state machine and an SLA**.

Division of labour, sharp:
- **V3 produces verdicts** on demand for a named claim.
- **V4 runs detectors on a schedule** over the entire corpus, **opens items**,
  **routes**, **gates serving**, and **closes**. When a detector needs a fresh
  independent recount to decide, it *calls V3* as a subroutine — V4 never
  re-uses the producer's own path to confirm.

---

## 1. Ground truth this design binds to `[VERIFIED]`

Read from the repo on 2026-06-12:

**Live corpus state** (`PROGRESO.md`):
- `[VERIFIED]` 12,814 entities (garaje 7,200 · compraventa 2,753 ·
  concesionario_oficial 1,569 · desguace 1,292), 22,300 serviceable vehicles,
  24,329 delta events, 212 dealers with inventory, 52/52 provinces, 10 sources.

**Denominator anchors** (`docs/research/SOURCES_ES.md` §6) — the per-segment
estimates the coverage-gap detector consumes:
- `[VERIFIED]` Desguaces/CAT: DGT official **1,292** (hard, exact registry).
- `[VERIFIED]` Concesionarios oficiales: FACONAUTO **2,018** franquiciados;
  Páginas Amarillas **11,202** incl. multimarca.
- `[VERIFIED]` Compraventas: PA floor **1,662**.
- `[VERIFIED]` Talleres/garajes: PA **29,955** / CETRAA ~20,000.
- `[VERIFIED]` TOTAL auto POS: floor **~44,000** (PA), ceiling **~50–90k**
  `[ASSUMED in census]` (registral CNAE 45 + Places).

**Schema the detectors read/write** (`migrations/0002..0004`):
- `[VERIFIED]` `entity(entity_ulid, cdp_code, kind, province_code,
  municipality_code, website, status, recipe_version, last_seen, …)`.
- `[VERIFIED]` `vehicle(vehicle_ulid, entity_ulid, deep_link, price NUMERIC(12,2),
  km INT, year INT, photo_url, status IN ('available','gone'), first_seen,
  last_seen, …)`, `UNIQUE(entity_ulid, deep_link)`.
- `[VERIFIED]` `vehicle_event(event_type IN
  ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE'), old_value, new_value,
  observed_at)` — append-only.
- `[VERIFIED]` `verification_verdict(subject_type, subject_key, claim,
  primary_value, primary_path, verifier_paths, independent_values, divergence,
  verdict IN ('TRUSTWORTHY','REFUTED','UNVERIFIED'), evidence, created_at)`.
- `[VERIFIED]` `source_health(source_key, last_ok, last_fail, consecutive_fails,
  status IN ('healthy','degraded','down','unknown'))`.
- `[VERIFIED]` `alert(origin, severity IN ('info','warning','critical'), message,
  payload, resolved_at)` — exact-origin alerts with unresolved partial index.

**Producer invariants the detectors exploit** (`pipeline/`):
- `[VERIFIED]` `ingest.py` already closes each dealer with a count quorum over
  `{db_available, harvested, source_declared}` and the **db-landed authority
  rule** (`verify.py`: the primary/landed path must agree with ≥1 other path or
  the verdict is `REFUTED`). The Gestionador's count-inflation detector *reuses
  this triplet as stored evidence* rather than re-inventing it.
- `[VERIFIED]` `autoscout24.py` carries `declared_count`, `pages_drained`,
  `raw_count` (pre-dedup) and `len(vehicles)` (post-dedup) — the exact signals
  the silent-cap detector needs (`max_pages=50`, `size=20` → a hard 1,000-row
  page ceiling).
- `[VERIFIED]` `autoscout24.py` bounds `km` to `(0, 5_000_000]` and `year` to
  `[1900, 2100]` and drops out-of-band values to NULL — meaning fabrication that
  slips through is **silently nulled**, which is itself a field-loss signal the
  Gestionador must see (a spike in NULL km is not "clean data", it is a parser
  swallowing garbage).
- `[VERIFIED]` `ingest.py` skips entities whose province is outside `01..52`
  (bad postcode guard) and OEM adapters filter out-of-scope (Andorra `AD500`) —
  these honest skips must be *counted as coverage debt*, not lost silently.

**Failure modes the team has already hit** (`PROGRESO.md`) — the detector suite
is calibrated to catch *these specific lies*, because they really happened:
1. `[VERIFIED]` cdp_code collapse: 175 Hyundai dealers → 48 codes (domain key
   reduced portal URLs with paths to one host). → **distinct-row-collapse**.
2. `[VERIFIED]` `_to_int(str(dict))` doubled digits → km = 6,594,865,948. →
   **impossible-value fabrication signature**.
3. `[VERIFIED]` AS24 unstable pagination fabricated a duplicate (78 raw → 77). →
   **pagination-instability / silent-cap family**.
4. `[VERIFIED]` OSM long-tail: 7,676 of 10,809 POIs dropped for missing province
   before the geocoder recovered them. → **silent-drop / coverage-gap**.
5. `[VERIFIED]` VAM quorum once masked ingestion loss (fetched=declared hid
   db<fetched). → **count-inflation with landed-authority**.

---

## 2. The managed item — the unit the Gestionador manages

Every detection becomes exactly one **managed item** (`gestion_item`). It is the
ticket: born from a detector firing, carrying its evidence, routed to a lane,
tracked through a state machine, closed only when an independent recheck passes.

`NEEDS-MIGRATION` — proposed DDL (handed to V5 for the canonical ledger):

```sql
-- 0005_gestionador.sql  (additive, reversible)
CREATE TABLE IF NOT EXISTS gestion_item (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    detector      TEXT NOT NULL,        -- 'count_inflation'|'silent_cap'|'field_loss'|'staleness'|
                                        -- 'fabrication'|'coverage_gap'|'price_trap'|
                                        -- 'geo_resolution_drift'|'classifier_drift' (§3)
    subject_type  TEXT NOT NULL,        -- 'entity' | 'source' | 'segment' | 'field' | 'geo' | 'model'
    subject_key   TEXT NOT NULL,        -- cdp_code | source_key | 'garaje@28' | ...
    severity      TEXT NOT NULL CHECK (severity IN ('info','warning','critical')),
    score         DOUBLE PRECISION,     -- detector-normalized 0..1 anomaly score
    measured      JSONB NOT NULL,       -- the numbers that fired the detector
    baseline      JSONB,                -- the expectation it diverged from
    lane          TEXT NOT NULL CHECK (lane IN
                    ('AUTO_FIX','RESEARCH','QUARANTINE','ESCALATE_GASTO','ESCALATE_OWNER')),
    state         TEXT NOT NULL DEFAULT 'OPEN' CHECK (state IN
                    ('OPEN','ROUTED','IN_PROGRESS','REVERIFYING','RESOLVED',
                     'QUARANTINED','ESCALATED','WONT_FIX','REOPENED')),
    quarantines   BOOLEAN NOT NULL DEFAULT FALSE,  -- does serving stop for subject?
    verdict_id    BIGINT REFERENCES verification_verdict(id),  -- the proof of closure
    opened_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    sla_due       TIMESTAMPTZ,          -- opened_at + lane SLA
    closed_at     TIMESTAMPTZ,
    closed_reason TEXT,
    dedupe_key    TEXT NOT NULL,        -- detector|subject_key|bucket → idempotency
    UNIQUE (dedupe_key)                 -- one open item per (detector, subject, window)
);
CREATE INDEX IF NOT EXISTS idx_gestion_open  ON gestion_item (state) WHERE closed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_gestion_quar   ON gestion_item (subject_type, subject_key) WHERE quarantines AND closed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_gestion_sladue ON gestion_item (sla_due) WHERE closed_at IS NULL;

CREATE TABLE IF NOT EXISTS gestion_transition (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id     BIGINT NOT NULL REFERENCES gestion_item(id) ON DELETE CASCADE,
    from_state  TEXT, to_state TEXT NOT NULL,
    actor       TEXT NOT NULL,          -- 'detector' | 'gestionador' | 'auto_fix:<job>' | 'owner'
    note        TEXT, payload JSONB,
    at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Rollback: DROP TABLE gestion_transition; DROP TABLE gestion_item;
```

The **`dedupe_key`** is load-bearing: a detector that fires every scan must not
spawn 50 tickets for the same subject. Key = `detector | subject_key |
time_bucket` (bucket = ISO date for daily detectors, ISO week for slow ones).
Re-firing an already-open item only **appends a transition** and refreshes
`measured`; it never opens a duplicate.

The **`quarantines`** boolean is the teeth: when `TRUE` and the item is open, the
publish gate (V5) must exclude the subject from every served surface. This is
how "nothing serves while quarantined" is mechanically enforced rather than
promised.

---

## 3. THE DETECTORS

Each detector is specified as: **signal** (what it reads), **statistic**
(the formula), **threshold** (when it fires, with the rationale for the number),
**severity & lane** (default routing), **worked numeric example** (on real
CARDEEP numbers), and **false-positive guard** (what would make it cry wolf and
how it is silenced). Thresholds are stated as constants so they live in config,
never magic-numbered in code.

Notation:
- `D` = source-**D**eclared count (e.g. AS24 `numberOfResults`).
- `H` = **H**arvested distinct rows post-dedup (`len(harvest.vehicles)`).
- `L` = **L**anded rows in DB (`count(*) … status='available'`).
- `R` = **R**aw rows pre-dedup (`harvest.raw_count`).
- Tolerances are **two-sided relative** unless stated:
  `rel(a,b) = |a − b| / max(a, b, 1)`.

---

### 3.1 — `count_inflation` · source-declared vs db-landed divergence

The flagship. A source brags N; the DB landed M; if `M ≪ N` we are either
**missing inventory** (gap) or **the brag was a lie** (inflation). Either way the
served count would be a lie if we published M while implying N.

**Signal.** The stored quorum triplet `{D, H, L}` already written by
`ingest.py` into `verification_verdict.independent_values` `[VERIFIED]`. The
detector reads the latest verdict per `subject_key` (entity inventory) — *it does
not re-harvest*; it audits the recorded evidence and, on suspicion, calls V3 for
an independent re-count.

**Statistic.** Three divergences, because the *shape* of the gap names the
culprit:
```
g_DH = rel(D, H)   -- declared vs harvested : a SCRAPE gap (pagination/throttle)
g_HL = rel(H, L)   -- harvested vs landed   : an INGEST gap (collisions/FK skips)
g_DL = rel(D, L)   -- declared vs landed    : the SERVED lie (end-to-end)
```

**Threshold.**
- `g_DL > τ_count` fires. **τ_count = 0.02** (2%). Rationale `[VERIFIED]`: the
  Director's own curl re-derivations drifted +166/278,329 = **0.06%** and
  +219/249,139 = **0.09%** on live marketplace counters (`SOURCES_ES.md` §7) —
  legitimate counter drift between two reads is sub-0.1%. 2% leaves 20× headroom
  over honest drift while catching any real truncation, which is almost always
  ≥ a full page (5–20%).
- **Hard sub-rule (no tolerance):** if `g_HL > 0` *at all* → `critical`. Landed <
  harvested means rows we *parsed* never reached the DB (silent FK skip, ON
  CONFLICT collapse). This is the exact lie `verify.py`'s landed-authority rule
  exists to kill `[VERIFIED]`; the Gestionador escalates it to a managed item so
  it is *tracked*, not just verdict'd.

**Direction matters.** `D > L` (under-landed) = **coverage gap** → lane
`RESEARCH`/`AUTO_FIX`. `D < L` (over-landed, DB has more than the source admits)
= **stale ghosts** (rows the source dropped that we never marked `gone`) →
different remedy (force a GONE reconciliation), still `count_inflation` family
but `sub='ghost_surplus'`.

**Severity & lane.**
| Condition | Severity | Lane |
|---|---|---|
| `g_HL > 0` (ingest loss) | critical | AUTO_FIX (re-ingest; bug if persists) |
| `g_DL > 0.20` (≥1 full page lost) | critical | QUARANTINE + RESEARCH |
| `0.02 < g_DL ≤ 0.20` | warning | RESEARCH |
| ghost surplus `L>D` by >2% | warning | AUTO_FIX (run GONE reconcile) |

**Worked example.** OK MOBILITY VALENCIA AIRPORT `[VERIFIED]`: D=78, H=78,
L=78. `g_DL = 0/78 = 0 ≤ 0.02` → **no item**. Correct.
Counter-example (the masked-loss bug that really happened `[VERIFIED]`): suppose
D=78, H=78 but L=73 (5 rows hit a dedup collision). `g_DH=0`, `g_HL = 5/78 =
0.064 > 0` → **critical `count_inflation` item, lane AUTO_FIX**, `quarantines`
the entity until L=H again. The old quorum (D=H) would have read TRUSTWORTHY; the
Gestionador refuses.

**False-positive guard.** Honest, declared scope-filters are not inflation:
`ingest.py` legitimately skips Andorra and out-of-range provinces. The detector
subtracts a recorded `excluded_in_scope` count from `D` before computing
`g_DL` (i.e. compares against the *in-scope declared* denominator). If the skip
was not recorded, the item still opens but routes to `RESEARCH` with note
"declared includes possibly-out-of-scope rows — confirm".

---

### 3.2 — `silent_cap` · top-N truncation / pagination ceiling hit

The cruelest lie: a harvest that *looks complete* because the loop ended cleanly,
but ended because it hit a cap, not because it drained the source.

**Signal `[VERIFIED]`.** `harvest_dealer(slug, max_pages=50)` with `size=20`
pages. Caps that can silently truncate:
- **page-budget cap:** `pages_drained == max_pages` AND `len(vehicles) <
  declared_count`.
- **provider hard ceiling:** AS24 `/lst` deep-paging caps near ~1,000 results;
  any single-source request returning exactly a round ceiling (1,000; 20×50) with
  more declared is suspect.
- **early-stop on stable-sort exhaustion:** the loop also breaks when
  `new_on_page == 0`. If that break fires with `len(vehicles) < D − τ`, the
  source stopped serving new rows before the declared count — a soft cap.

**Statistic.**
```
cap_hit       = (pages_drained == MAX_PAGES) and (H < D)
ceiling_hit   = (H in {500,1000,2000,5000}) and (D > H)   -- round-number ceilings
early_starve  = (new_on_page==0 reached) and (D - H) > max(τ_count*D, 1)
```

**Threshold.** Any of the three true → fire. `MAX_PAGES`, `size`, and the
round-ceiling set are config constants `[ASSUMED config, derived from
[VERIFIED] code constants]`. The round-ceiling set is provider-specific and
learned: the detector records, per source, the largest `H` ever seen with
`D>H`; a recurring plateau at the same `H` across many entities **is** the cap.

**Severity & lane.** `critical` always (a cap silently understates inventory =
a served lie). Lane:
- page-budget cap → `AUTO_FIX` (raise `max_pages`, re-harvest; the fix is
  mechanical and reversible).
- provider hard ceiling → `RESEARCH` (needs a recipe change: facet the query by
  make/price band to slice under the ceiling — exactly the V1/V2 slicing idea).

**Worked example.** A mega-dealer with D=1,840 stock. Harvest drains
`pages_drained=50`, `H = 50×20 = 1,000`. `cap_hit = (50==50) and (1000<1840) =
TRUE`. Item opens `critical`, `AUTO_FIX` bumps `max_pages` → re-harvest yields
H≈1,840 → `g_DL→0` → item closes after V3 re-count. Without this detector the
DB would forever serve "1,000 cars" for a 1,840-car dealer and call it complete.

**False-positive guard.** A dealer whose true stock *is* exactly 1,000 must not
loop forever. The discriminator is `D`: cap detection requires `D > H`. If the
source declares ≤ H, there is no cap — the loop ended because it drained. The
pagination-instability dupe (78 raw→77 `[VERIFIED]`) is **not** a cap (H<R but
H≈D); it routes to `field_loss`/dedup-health, not here.

---

### 3.3 — `field_loss` · null-rate spike vs recipe baseline

A recipe silently stops extracting a field (site markup changed, a selector
rotted). The rows still land, the counts still reconcile, but `price` or `year`
quietly becomes NULL across the board. Counts say "complete"; the data is gutted.

**Signal.** Per `(source_key, recipe_version, field)` baseline null-rate vs the
current harvest's null-rate, for the high-value fields: `price, year, km,
photo_url, make, model, province_code, municipality_code`. The recipe (`recipe.py`
field_map `[VERIFIED]`) *names exactly these fields*, so the baseline set is the
recipe's field_map keys — no guessing.

**Statistic.** Baseline `p0 = ` historical null-rate for the field at this
recipe_version (a stored rolling estimate). Current `p1 = nulls/N` in the new
harvest of size `N`. Use a **two-proportion z-test** (one-sided, null-rate
*increased*):
```
p_pool = (x0 + x1) / (n0 + n1)
z      = (p1 − p0) / sqrt( p_pool*(1−p_pool) * (1/n0 + 1/n1) )
fire when z > z_crit  (z_crit = 3.0  ⇒ ~0.13% one-sided false-alarm)
```
A z-test, not a flat threshold, because a jump from 1%→3% null on N=2,000 is
real signal, while 0%→8% on N=12 rows is noise — the test scales the alarm to
the sample size automatically.

**Threshold.** `z_crit = 3.0` **and** an absolute floor `p1 − p0 ≥ 0.05`
(ignore statistically-significant-but-trivial 0.5% drifts). Both must hold. For
**hard-required fields** (`price` on a `compraventa`/dealer, `province_code` on
any entity) a stricter rule: `p1 > 0.30` fires `critical` regardless of z,
because a marketplace listing with no price is structurally a lie.

**Severity & lane.**
| Field class | Spike | Severity | Lane |
|---|---|---|---|
| core (price, year, km) | z>3 & Δ≥5% | warning | RESEARCH (recipe likely rotted) |
| identity (province, make) | any spike to >30% | critical | QUARANTINE + RESEARCH |
| photo_url | z>3 & Δ≥10% | info | AUTO_FIX (re-fetch images) |

**Worked example.** AS24 dealer, recipe_version=1, historical `price` null-rate
p0 = 0.012 over n0 = 22,300 landed vehicles `[VERIFIED corpus size]`. A markup
change makes the new harvest of N=140 cars return p1 = 0.46 (64 nulls).
`p_pool = (267 + 64)/(22300+140) = 0.01475`;
`z = (0.46−0.012)/sqrt(0.01475·0.98525·(1/22300+1/140)) =
0.448 / sqrt(0.014537·0.007194) = 0.448 / 0.010225 ≈ 43.8 ≫ 3` and `Δ=0.448 ≥
0.05`. **critical-by-class `field_loss` on `price`** → QUARANTINE the dealer +
RESEARCH the recipe. The `[VERIFIED]` km-doubling bug is the mirror image: there
the parser produced *garbage that got nulled by the (0,5M] bound* — same
detector catches the resulting null spike even when the root cause is a parser,
not a missing selector.

**False-positive guard.** Genuinely price-less segments (some desguaces list
parts, not priced cars) have a high *legitimate* baseline null-rate. The test
compares against the **segment-and-source-specific** `p0`, not a global one, so a
desguace's natural 90% car-price-null does not trip when it stays at 90%.

---

### 3.4 — `staleness` · last_seen drift past TTL

A live DB that stops refreshing is a graveyard wearing a "live" badge. If an
entity hasn't been re-harvested past its TTL, its inventory and prices are stale
and serving them is a (time-)lie.

**Signal `[VERIFIED]`.** `entity.last_seen`, `vehicle.last_seen`,
`source_health.last_ok`. Append-only `vehicle_event.observed_at` gives the true
last delta.

**Statistic.** Per subject, `age = now() − last_seen`. TTL is **segment-tiered**
because a marketplace churns daily while a desguace registry barely moves:
```
TTL_inventory[segment]:  compraventa/dealer = 3 d ·  garaje = 7 d ·
                         desguace = 30 d  ·  Tier-1 marketplace = 1 d
TTL_entity (existence):  90 d for all (re-confirm the POS still exists)
staleness_ratio = age / TTL    → fire when > 1.0
```

**Threshold.** `staleness_ratio > 1.0` → warning; `> 3.0` → critical
(`quarantines` inventory: stop serving a price 3 TTLs old). The ratio (not raw
age) lets one config knob per segment drive everything and makes the dashboard a
single comparable number across segments.

**Severity & lane.**
| ratio | Severity | Lane |
|---|---|---|
| 1–3 | warning | AUTO_FIX (enqueue re-harvest) |
| > 3 | critical | QUARANTINE inventory + AUTO_FIX |
| entity age > 90d | warning | RESEARCH (does the POS still exist?) |

**Worked example.** A compraventa harvested 2026-06-01, today 2026-06-12 →
`age = 11 d`, `TTL = 3 d`, `ratio = 3.67 > 3` → **critical**: its 22-car
inventory is frozen for 11 days; QUARANTINE it from `/inventory` and AUTO_FIX
enqueues a re-harvest. Once re-harvested and the count reconciles, `last_seen`
resets, `ratio → 0`, item closes.

**False-positive guard.** A source that is *globally down* (its `source_health`
= `down`) must not spawn 2,000 per-entity staleness items — that is noise. The
detector **rolls up**: if `>50%` of a source's entities are stale
simultaneously, it suppresses the per-entity items and opens **one**
`source`-level staleness item routed to `ESCALATE_GASTO`/`RESEARCH` (the source
needs a defense/budget fix), with the per-entity ages attached as evidence.

---

### 3.5 — `fabrication` · impossible / out-of-band / collapsed values

The detector of invented data: values that *cannot be real*, or many distinct
real things crushed into one row. This is where the km-doubling and cdp_code
collapse bugs live.

**Signal.** Distribution + range checks over `vehicle.{price, year, km}`,
`entity.cdp_code` cardinality vs source row cardinality, and per-entity row
fan-in.

**Sub-detectors & thresholds.**

**(a) Out-of-band hard bounds** (a row outside is fabricated/parse-garbage):
```
price : (0, 5_000_000] EUR          -- a 5M€ ceiling; hypercars exist, 6M€ glitch
year  : [1900, this_year + 1]       -- next year for pre-reg; 2100 is a parse bug
km    : [0, 1_000_000]              -- tightened from the code's 5M sanity cap;
                                       a >1M km retail car is ~always a digit bug
```
The producer already nulls `km>5M` / `year∉[1900,2100]` `[VERIFIED]`. The
fabrication detector therefore *also watches the NULL it created* (cross-links to
`field_loss`) AND independently re-checks the **landed** rows in case a future
recipe forgets the bound. Any landed row out-of-band → `critical`,
`QUARANTINE` the row, `AUTO_FIX` (re-parse) → if it recurs, bug → `RESEARCH`.

**(b) Distinct-row-collapse** — the Hyundai 175→48 lie `[VERIFIED]`:
```
collapse_ratio = source_distinct_refs / db_distinct_codes
fire when collapse_ratio > κ   (κ = 1.10  ⇒ >10% of distinct sources fused)
```
For Hyundai: `175/48 = 3.65 ≫ 1.10` → **critical** `fabrication
(distinct_collapse)`. This is precisely the bug the cdp_code domain-vs-path fix
solved; the detector guarantees a *regression* of that fix is caught the next
day, not a month later by the owner. Lane: `RESEARCH` (it's an identity-key
design fault, never auto-fixable blindly — a wrong auto-merge/split corrupts the
immutable code).

**(c) Degenerate-distribution signature** — fabrication often shows as
unnatural uniformity (all prices identical, all years one value). Per entity with
≥ `n_min=20` cars, compute coefficient of variation `cv = σ/μ` of price; `cv <
0.01` (prices essentially identical) → `warning` `fabrication(degenerate)` →
RESEARCH. Benford's-law first-digit check on price across a *source* (≥500 rows)
is the population-scale version: `χ²` of observed first-digit dist vs Benford;
`χ² > 20.09` (8 dof, p<0.01) → warning, source-level RESEARCH item.

**Worked example (a).** The km-doubling bug `[VERIFIED]`: a row lands km =
6,594,865,948. `> 1,000,000` → **critical** out-of-band; QUARANTINE row, AUTO_FIX
re-parse. (In reality the `_raw()` fix prevents it; the detector is the
regression net.)

**Worked example (b).** New OEM adapter ships, puts portal-path URLs as website
again. 212 MG dealers `[VERIFIED]` collapse to 60 codes. `collapse_ratio =
212/60 = 3.53 > 1.10` → critical, RESEARCH, dealer codes quarantined from serving
until the key is fixed and codes re-expand.

**False-positive guard.** Legitimate multi-source dedup *should* reduce distinct
refs (same dealer attested by AS24 + OSM = 2 refs → 1 code, ratio 2.0). The
detector therefore measures collapse **within a single source's distinct
business identities**, not across sources, and excludes the
`entity_source`-driven cross-source merges (those are *wanted*).

---

### 3.6 — `coverage_gap` · denominator estimate − covered, per segment × province

The gap detector for the *universe*, not a single entity. It is the bridge to
V1-DENOMINATOR-PROOF: V1 produces the bounded estimate `Û ± CI`; the Gestionador
turns "we cover C of Û" into managed, prioritized RESEARCH work and forbids ever
claiming "100% of Spain" while a segment×province cell is empty.

**Signal.** `covered[seg][prov] = count(entity WHERE kind=seg AND
province_code=prov AND status='active')` vs the V1 estimate
`Û[seg][prov]` (or, where V1 has no provincial split, the national anchor
allocated by a province weight — e.g. registered-vehicle share).

**Statistic.**
```
coverage[seg][prov]   = covered / Û_lo          -- conservative: use CI LOWER bound
                                                   so we never overclaim coverage
gap[seg][prov]        = max(0, Û_lo − covered)
relgap                = gap / Û_lo
```
Using `Û_lo` (the *lower* confidence bound) is the anti-lie choice: it makes
coverage look *worse*, never better. Claiming 100% requires `covered ≥ Û_hi`.

**Threshold.** Per cell: `relgap > 0.10` → an `info` gap item (research debt);
`relgap > 0.40` → `warning`; a **hard anchor breach** `covered < anchor_floor`
(e.g. desguace covered < 1,292 DGT, or oficial < FACONAUTO 2,018) → `critical`,
because we *know* the floor exactly and are demonstrably below it.

**Severity & lane.** All `coverage_gap` items route to `RESEARCH` (find more
sources / build an adapter for the missing cell) — never AUTO_FIX (you cannot
auto-fix not having the data). The largest `gap` cells are the prioritized
backlog; the dashboard sorts by absolute `gap` (biggest wins first).

**Worked example.** Desguace segment `[VERIFIED]`: covered = 1,292, anchor floor
= DGT 1,292. `covered ≥ floor` and `Û_hi ≈ 1,300` → coverage ≈ 0.994, `relgap ≈
0.006 < 0.10` → **no item**: this segment is honestly ~complete and may be
served as "≈100% of the official registry". By contrast garaje `[VERIFIED]`:
covered = 7,200, anchor PA 29,955. `coverage = 7,200/29,955 = 0.240`, `relgap =
0.76 > 0.40` → **warning** coverage_gap, RESEARCH. **Crucially**: this is the
detector that *forbids the "100% of Spain" lie* — with garaje at 24% covered, any
agent claiming "Spain complete" produces a `coverage_gap` contradiction the
Gestionador surfaces.

**False-positive guard.** A segment whose true universe is genuinely small but
PA over-rubricates (PA's 11,202 "concesionarios" includes multimarca double-
counts vs FACONAUTO's 2,018 franchised `[VERIFIED]`). The detector uses the
**most-defensible anchor per segment** (registry > capture-recapture >
directory-rubric) and, where two anchors disagree by >2×, opens a *separate*
`RESEARCH` item "reconcile denominator anchors" rather than treating the inflated
rubric as the target — i.e. it refuses to chase a denominator that is itself a
lie.

---

### 3.7 — `price_trap` · finance/monthly rate sold as the price

Marketplaces show "199 €/month" far larger than the cash price. A naive parser
stores 199 as `price`. The DB then "lies" that a 24,000 € car costs 199 €. This
is a fabrication sub-species important enough to be its own detector because its
signature is specific and its blast radius (price = the headline field) is huge.

**Signal.** `vehicle.price` distribution per segment + per listing
cross-checks. A finance rate is detectable by **range** and **co-occurrence**.

**Statistic.**
```
implausible_low = price < FLOOR_PRICE[segment]      -- e.g. car < 300 € is not a price
ratio_outlier   = price < 0.05 * median(price | same make,model,year cohort)
text_signal     = listing text/url contains /mes, /month, "cuota", "desde"
                  while the stored number ≈ a monthly band (50–900)
fire when implausible_low OR (ratio_outlier AND in monthly band [49,999])
```

**Threshold.** `FLOOR_PRICE`: car/dealer/compraventa = **300 €**; parts at a
desguace exempt. Monthly band `[49, 999]` (typical car finance installments).
The cohort-median outlier (`<5%` of peers) catches the trap even when the
absolute value is plausible-looking (e.g. 299 €/mo).

**Severity & lane.** `critical` (price is the field users trust most), `lane =
RESEARCH` (recipe must distinguish `prices.public.priceRaw` from a finance node —
`autoscout24.py` already prefers `prices.public`/`dealer` over the monthly field
`[VERIFIED]`, so this detector is the regression net for recipes that lack that
discipline). Affected rows `QUARANTINE` from price-bearing surfaces until
re-parsed.

**Worked example.** A coches.net-style harvest lands 4 cars at 149, 175, 199,
210 € among a cohort whose median is 18,900 €. Each is `< 0.05·18,900 = 945`
and in `[49,999]` → **critical `price_trap`** on those rows; QUARANTINE +
RESEARCH the recipe's price node. The OK Mobility Porsche Taycan at 89,010 €
`[VERIFIED]` is far above floor and ≈ cohort median → no item.

**False-positive guard.** Genuinely cheap items (a 250 € scooter, a desguace
part) are exempted by segment floor + cohort comparison: a 250 € listing whose
cohort median is also ~300 € is not an outlier and does not fire.

---

### 3.8 — `geo_resolution_drift` · sentinel-placement rate regression `[adversarial GAP-6]`
The geo placement function (08 §5.1) sends entities it cannot resolve to `_sin-comarca` /
`_sin-municipio` sentinel dirs. A geocoder regression that suddenly routes (say) 50% of new entities
to `_sin-municipio` is a **silent coverage-QUALITY collapse** — the entities still exist, still
count, but the mandate's `province→comarca→city` grid quietly hollows out, and NO existing V4
detector watches it (staleness/fabrication/field_loss are blind to geo precision).
- **Fires when** the rolling sentinel-placement rate `sentinel_placed / total_placed` over a window
  exceeds **2× its trailing baseline** OR breaches an absolute ceiling (`[ASSUMED]` >15% of newly
  placed entities). Severity warning→critical with the magnitude; lane **RESEARCH** (a geocoder/
  gazetteer fix), never quarantine (the entities are real). This makes geo precision a monitored
  quality dimension — the VAM axis it previously lacked.

### 3.9 — `classifier_drift` · LLM kind-label accuracy regression `[adversarial GAP-7/25]`
The local-LLM classifier writes `kind` (the seal-segment selector) and `canonical_name` (feeds
`cdp_code`), and for entities with no higher-precedence signal it is the sole authority — yet its
accuracy was previously watched by NOTHING (the corpus watches SCRAPER recipe drift, never LLM
classifier drift).
- **Fires when** the nightly golden-set regression (T08 §5.1) scores the model **below its per-kind
  precision/recall floor** (≥0.95 where the classifier is sole authority). Severity critical; lane
  **RESEARCH/AUTO_FIX**; **side-effect: freeze `kind_source='classifier'` writes** until the model
  re-clears the floor (model/quant/prompt drift is contained, not served). Cross-links to
  `field_loss` when the drift manifests as a specific field. A silently-degraded model mis-typing
  long-tail entities — which would silently corrupt segment denominators and thus every coverage % —
  is now caught by a detector instead of being invisible.

### 3.10 — Detector summary matrix

| # | detector | fires when | default severity | default lane | quarantines? |
|---|---|---|---|---|---|
| 3.1 | `count_inflation` | `g_DL>0.02` or `g_HL>0` | warning→critical | RESEARCH/AUTO_FIX | if `g_DL>0.20` |
| 3.2 | `silent_cap` | page/ceiling/starve hit & `H<D` | critical | AUTO_FIX/RESEARCH | yes |
| 3.3 | `field_loss` | `z>3 & Δp≥0.05` (class-tiered) | info→critical | AUTO_FIX/RESEARCH | identity-field: yes |
| 3.4 | `staleness` | `age/TTL>1` (segment TTL, MASTER_PLAN C-11) | warning→critical | AUTO_FIX | if ratio>3 |
| 3.5 | `fabrication` | out-of-band / collapse>1.10 / degenerate | warning→critical | RESEARCH/AUTO_FIX | yes |
| 3.6 | `coverage_gap` | `relgap>0.10` / anchor breach | info→critical | RESEARCH | no (it's a gap, not a lie-in-DB) |
| 3.7 | `price_trap` | implausible-low / monthly band | critical | RESEARCH | yes |
| 3.8 | `geo_resolution_drift` | sentinel-rate > 2× baseline / >15% | warning→critical | RESEARCH | no (entities are real) |
| 3.9 | `classifier_drift` | golden-set below per-kind floor | critical | RESEARCH/AUTO_FIX | no — freezes classifier writes |

Note the asymmetry: `coverage_gap`, `geo_resolution_drift`, and `classifier_drift` never quarantine,
because a *missing/mis-placed/mis-typed* entity isn't a lie *being served as a number* — they gate
quality and freeze a producer instead. Every other detector can quarantine, because it found a lie
*being served*. **The §3.4 `staleness` TTL is the SINGLE TTL matrix of MASTER_PLAN C-11** — the same
`expires_at` the V5 publish-gate reads, so the gate and this detector can never disagree (GAP-5).

---

## 4. THE ROUTING STATE MACHINE

Detection is worthless without disposition. Each managed item flows through one
deterministic state machine. Lanes are *where* it goes; states are *how far*
it's gotten.

### 4.1 Lanes (the five destinies)

| Lane | Meaning | Who acts | Reversible? | Example trigger |
|---|---|---|---|---|
| **AUTO_FIX** | Mechanical, reversible remedy the system applies itself | a deterministic job | yes | re-harvest (cap), re-ingest (g_HL>0), bump max_pages, re-fetch photos |
| **RESEARCH** | Needs investigation / new adapter / recipe change | research agent (V3-style) | n/a | recipe rotted, new source for a coverage cell, denominator anchor conflict |
| **QUARANTINE** | Stop serving the subject *now*; remedy is pending | gate (immediate) + then AUTO_FIX/RESEARCH | yes | any served lie (silent_cap, price_trap, identity field_loss) |
| **ESCALATE_GASTO** | Remedy needs spend (proxies, residential IPs, a paid API, captcha budget) | owner-approved budget | — | a Tier-1 source is `down` from defense; harvesting needs paid infra |
| **ESCALATE_OWNER** | Ambiguous/irreversible/scope/legal decision | the owner | — | Google Places ToS risk `[VERIFIED]`; "is this homonym one chain or many?" `[VERIFIED]`; denominator method choice |

**Routing function** (deterministic, auditable):
```
route(item):
    if item.detector == 'coverage_gap':            return RESEARCH
    if served_lie(item):                            QUARANTINE  (then sub-route)
    if mechanical_and_reversible(item):             return AUTO_FIX
    if needs_spend(item):                           return ESCALATE_GASTO
    if irreversible_or_legal_or_scope(item):        return ESCALATE_OWNER
    return RESEARCH                                  # default: investigate, never guess
```
`served_lie` = the subject currently appears on an API surface AND the detector
class can produce a wrong served value (everything except `coverage_gap`).
QUARANTINE is **not terminal**: it freezes serving, then the item *also* carries
a sub-lane (AUTO_FIX or RESEARCH) for the actual remedy. Freeze first, fix
second — the freeze is what guarantees no lie is served during the fix.

The default is **RESEARCH, never silent close**. Doctrine: an unexplained
anomaly is investigated, not assumed-benign.

### 4.2 States & transitions

```
            ┌─────────────────────────────────────────────────────────┐
            │                                                         │
  detector  ▼                                                         │
  fires → [OPEN] ──route()──► [ROUTED] ──pickup──► [IN_PROGRESS]      │
            │                    │                       │            │
            │ (quarantines)      │                       ▼            │
            ▼                    │                 remedy applied      │
       [QUARANTINED]◄────────────┘                       │            │
       (serving frozen,                                  ▼            │
        still being worked)                       [REVERIFYING] ──────┤
            ▲                                            │  calls V3   │
            │                                  ┌─────────┴─────────┐  │
            │                          indep. PASS          indep. FAIL
            │                                  │                 │   │
            │                                  ▼                 ▼   │
            └──── reopen if regresses ──── [RESOLVED]        [REOPENED]┘
                                          (unquarantine,     (back to ROUTED,
                                           verdict_id set)    escalate severity)

  ESCALATE_* items: [OPEN]→[ROUTED]→[ESCALATED]  (await owner/budget)
                    on decision → [IN_PROGRESS] or [WONT_FIX]
```

**The closure rule is the spine:** an item may reach `RESOLVED` **only** through
`REVERIFYING`, and `REVERIFYING` **must** be an *independent* recheck — the
Gestionador calls **V3-INQUISITION** (a different path/tool/source than the
producer) and stores the resulting `verification_verdict.id` in
`gestion_item.verdict_id`. **No verdict_id → no RESOLVED.** This is the
mechanical embodiment of "never validated by the path that produced it": closure
literally cannot be written without an independent verdict row.

**Transitions are append-only** (`gestion_transition`), giving an immutable audit
trail: who/what moved the item, when, with what evidence. Nothing is mutated in
place; the history is the proof.

### 4.3 Quarantine ⇄ publish gate (the teeth)

The publish gate (owned by V5, enforced here) is a single predicate every served
read must pass:

```sql
-- a subject is SERVABLE iff no open, quarantining item references it
CREATE OR REPLACE VIEW servable_entity AS
SELECT e.* FROM entity e
WHERE NOT EXISTS (
  SELECT 1 FROM gestion_item g
  WHERE g.quarantines AND g.closed_at IS NULL
    AND g.subject_type='entity' AND g.subject_key = e.cdp_code
);
```
The API `[VERIFIED endpoints: /entities/{cdp_code}, /inventory, /delta,
/geo/{prov}/entities]` reads through `servable_*` views, never the raw tables.
Result: **the instant a detector opens a quarantining item, the subject vanishes
from every served surface**, and **the instant it reaches RESOLVED, it returns** —
with no code path that can serve a quarantined subject. "Nothing serves while
quarantined" is thus a database invariant, not a hope.

A served *count* (e.g. `/health` total) is computed over `servable_*`, so the
public number is always the *defensible* number, automatically excluding
quarantined subjects. We would rather under-report than serve a lie.

### 4.4 SLA, dedup, and escalation pressure

- **SLA per lane** (`sla_due = opened_at + ttl`): AUTO_FIX = 6 h, RESEARCH = 7 d,
  QUARANTINE remedy = 48 h, ESCALATE_* = no auto-SLA (awaits human/budget).
- **Aging escalation:** an item past `sla_due` auto-bumps severity one notch and,
  if QUARANTINE+overdue twice, re-routes to `ESCALATE_OWNER` ("we cannot self-heal
  this — decide"). A lie that won't die gets louder until a human sees it.
- **Dedup:** `dedupe_key` (detector|subject|bucket) keeps one open item per
  recurring condition; re-firing appends a transition and updates `measured`.
- **Storm suppression:** if a single source spawns `> N_storm` (default 200)
  items in one scan, the Gestionador collapses them into one `source`-level item
  (`ESCALATE_GASTO`/`RESEARCH`) with the children referenced — a down source is
  *one* problem, not 2,000 (the §3.4 rollup, generalized).

---

## 5. SCHEDULING — when detectors run

| detector | cadence | scope per run | rationale |
|---|---|---|---|
| `count_inflation` | on every ingest + nightly sweep | the just-ingested entity; full corpus nightly | cheapest at write-time; sweep catches drift |
| `silent_cap` | on every harvest | the harvest in hand | the signal (`pages_drained`) only exists at harvest time |
| `field_loss` | per harvest + nightly per-source | source's recent rows | needs ≥ a batch to be statistically meaningful |
| `staleness` | hourly | rolling scan of `last_seen` | cheap index scan; TTLs are in hours/days |
| `fabrication` | on ingest (bounds) + weekly (distribution) | row-level live; distribution weekly | bounds are O(1); Benford/cv need population |
| `coverage_gap` | nightly + on V1 estimate refresh | all segment×province cells | denominator changes slowly |
| `price_trap` | on ingest | the row | catch before it's ever served |

Write-time detectors (bounds, price_trap, count quorum) are the **first line** —
they prevent a lie from ever landing servable. Sweep detectors are the **safety
net** — they catch drift, rot, and regressions the write-time check couldn't see.

---

## 6. WORKED END-TO-END SCENARIO (the system catching itself)

A regression ships: a new recipe version for AS24 forgets the stable-sort fix.

1. **t0 harvest** of dealer D (D=140 declared). Unstable pagination →
   `raw_count=140`, dedup → `H=132` (8 fabricated dupes dropped), but 3 real
   rows lost across page boundaries → `H` is *missing* 3 reals. Lands `L=132`.
2. **write-time `count_inflation`**: `g_DL = |140−132|/140 = 0.057 > 0.02` →
   item `#811` OPEN, warning, `served_lie=true` → **QUARANTINE** dealer D + sub-
   lane RESEARCH. Dealer D vanishes from `/inventory` immediately (§4.3).
3. **`silent_cap`** checks: `pages_drained=7 < 50`, not a cap → no item (correct;
   the cause is instability, not truncation).
4. **RESEARCH** (a V3-style agent) re-derives independently: blind re-harvest
   *with* stable sort → 140 distinct. Diagnoses the missing sort. Fix shipped
   (reversible recipe bump). Item → IN_PROGRESS → remedy applied → **REVERIFYING**.
5. **REVERIFYING** calls V3-INQUISITION: independent recount yields D=H=L=140,
   `g_DL=0` → `verification_verdict` row `id=4021` TRUSTWORTHY written.
6. Item `#811` → **RESOLVED**, `verdict_id=4021`, `quarantines` no longer open →
   dealer D **reappears** in `/inventory` serving the *correct* 140.
7. `gestion_transition` holds the full who/when/evidence chain. The owner
   dashboard showed dealer D as "quarantined: count divergence 5.7%" for the
   ~hours it took, never a wrong number.

At no point was a lie served. The divergence the old quorum (which once read
fetched=declared as fine `[VERIFIED]`) would have masked is instead *frozen,
fixed, independently re-proven, and audited*.

---

## 7. HONEST RESIDUE — what this layer does NOT do (no maquillaje)

- **Detectors find suspicion; they don't diagnose root cause.** That's RESEARCH's
  job (and V3's). The Gestionador guarantees *nothing benign is assumed* and
  *nothing is served while open* — it does not itself fix recipes.
- **Thresholds (τ_count=0.02, z_crit=3.0, κ=1.10, TTLs) are calibrated from
  `[VERIFIED]` real drift (sub-0.1% curl drift) and real bugs (175→48 collapse),
  but they are starting constants.** They must live in config and be tuned as the
  false-positive/false-negative log accrues. Shipping them as magic numbers in
  code would itself be an anti-pattern.
- **`coverage_gap` is only as honest as V1's denominator.** If V1's `Û` is wrong,
  the gap is wrong. That's why this detector *consumes V1's CI lower bound* and
  opens an explicit "reconcile anchors" item when sources disagree >2× rather
  than trusting a single rubric (PA's inflated 11,202 vs FACONAUTO 2,018
  `[VERIFIED]`).
- **The publish gate is specified here but enforced in V5.** The `servable_*`
  views and the API reading through them are the contract; V5 owns the DDL and
  the `gestion_item`/`gestion_transition` migration (0005) proposed in §2.
- **Andorra/out-of-scope skips `[VERIFIED]`** are counted as coverage debt, not
  lies — but only if the producer records the skip count. Where it doesn't, the
  detector opens a RESEARCH item rather than silently trusting the declared
  total. Honest gap > silent assumption.

---

## 8. Interfaces to sibling facets (contract surface)

- **← V1-DENOMINATOR-PROOF:** consumes `Û[seg][prov]` with CI bounds; uses
  `Û_lo` for coverage; raises "reconcile anchors" on >2× source disagreement.
- **← V2-COMPLETION-PROOF:** an entity's COMPLETION GATE failing *is* a
  Gestionador trigger (it opens the matching detector item, e.g. a recipe not
  git-committed → a `RESEARCH` item; a sample re-scrape mismatch → `count_inflation`).
- **→/← V3-INQUISITION:** the Gestionador *calls* V3 in `REVERIFYING`; V3's
  verdict is the only thing that can close an item (`verdict_id` FK).
- **→ V5-LEDGER-API:** hands the `0005_gestionador.sql` DDL, the `servable_*`
  publish-gate views, and the dashboard fields (open items by lane/severity,
  quarantined count, SLA breaches, per-segment coverage from §3.6).
- **← V6-STATISTICAL-RIGOR:** the `z`-test (§3.3), χ²/Benford (§3.5), and the
  acceptance-sample sizes that feed `count_inflation`'s sample-based variant come
  from V6; this doc states the *use*, V6 owns the *derivation*.

---

*End V4-GESTIONADOR. The lie is found, ticketed, frozen, fixed, independently
re-proven, and audited — or it is escalated to a human. It is never served.*
