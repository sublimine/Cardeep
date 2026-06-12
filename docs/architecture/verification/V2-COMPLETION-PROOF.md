# V2 — COMPLETION PROOF (the deep validator)

> **Owner question this answers, literally:** *"An agent says 20 000 entities are
> completed end-to-end. Who validates it — and how do we know it isn't a lie?"*
>
> **Answer in one line:** No agent's word counts. An entity is `COMPLETED` only when an
> **independent** validator re-derives every stage of its lifecycle by paths that did
> **not** produce the original data, and the claim "20 000 are completed" is only asserted
> at the **confidence a blind re-scrape sample statistically supports** — never higher.
>
> This document supersedes and expands the light `05-VERIFICATION-VAM` sketch. Where that
> doc treats VAM as a count-quorum feature, this one defines the **binary per-entity
> completion gate**, the **verdict ledger**, the **"completed" definition**, and the
> **aggregate acceptance-sampling proof**. Verification is the product, not a feature.

**Provenance of every claim below** — `[VERIFIED]` = read in the live repo today;
`[ASSUMED]` = design decision not yet in code (marked so it is never sold as built).

| Artifact grounded against | Path | Status |
|---|---|---|
| `entity` / `vehicle` / `vehicle_event` schema | `migrations/0002_entities.sql`, `0003_vehicles_events.sql` | [VERIFIED] |
| `verification_verdict` / `source_health` / `alert` | `migrations/0004_verification_health.sql` | [VERIFIED] |
| Count-quorum + db-landed authority rule | `pipeline/verify.py` `record_count_verdict()` | [VERIFIED] |
| Delta engine + 3-path reconcile | `pipeline/ingest.py` `ingest_dealer()` | [VERIFIED] |
| Harvest drain + `declared_count` = `numberOfResults` | `pipeline/sources/autoscout24.py` `harvest_dealer()` | [VERIFIED] |
| Recipe write path `countries/ES/recipes/<cdp>.yaml` | `pipeline/recipe.py` `write_recipe()` | [VERIFIED] |
| Serving endpoints `/entities/{cdp}` `/inventory` `/delta` | `services/api/main.py` | [VERIFIED] |
| `cdp_code` immutable identity (domain>cif>name+muni) | `services/api/codes.py` | [VERIFIED] |
| Per-entity `entity_completion` ledger table | this doc → `migrations/0005_completion.sql` | [ASSUMED] (proposed) |
| Acceptance-sampling re-scrape validator | this doc → `pipeline/complete.py` | [ASSUMED] (proposed) |

---

## 0. Threat model — the six lies this validator must catch

A "completed" claim can be a lie in exactly six ways. The gate is engineered so each lie
is **structurally impossible to pass**, not merely "checked for".

| # | Lie | Concrete failure it masks | Caught by |
|---|---|---|---|
| L1 | **Inflated count** | "120 cars" served when source had 87 | §3.B db-landed authority + §3.E live-serve recount |
| L2 | **Silent cap** | harvester stopped at page 5/9; 100/180 cars | §3.A harvest-drain proof (last page explicit, not timeout) |
| L3 | **Silently-dropped field** | price/km/deep_link null on landing; row "exists" but is hollow | §3.B field-integrity floor + §4 blind field-compare |
| L4 | **Staleness** | data 40 days old re-served as "live" | §3.F freshness watermark on every gate read |
| L5 | **Fabrication** | row in DB that does not exist at source | §4 blind re-scrape orphan check (set difference) |
| L6 | **Coverage gap** | "20k done" but the 20k are the *easy* ones; tier-1 / hard provinces silently absent | §5.5 stratified sampling + §6 coverage denominator |

> **Design law:** the validator reads only **DB-landed, API-served** state and a **fresh
> independent re-scrape**. It is forbidden to trust the harvest log, the agent's report,
> or any in-memory count produced by the same run that did the work. The path that
> produced a number can never be the path that validates it.

---

## 1. The completion gate — binary, five sequential sub-gates

An entity transitions `…→ COMPLETED` **iff all five sub-gates return `PASS`**. The gate is
a logical **AND of binary predicates** — there is no weighted score, no "90% complete". A
single `FAIL` makes the entity `INCOMPLETE` with an exact failing-stage origin written to
`alert`. This is the per-entity equivalent of the mandate's "nadie vuelve a base a medias".

```
G1 DISCOVERED   entity row exists, geo-resolved, immutable cdp_code minted
      │  (entity.province_code NOT NULL ∧ cdp_code matches CDP-ES-NN-######## ∧ lat/lon present-or-justified)
      ▼
G2 HARVESTED    inventory drained COMPLETE, reconciled by ≥2 orthogonal paths
      │  (db-landed == harvested == source-declared, db-landed is authority; OR justified Δ within tol)
      ▼
G3 RECIPE       recipe.yaml written AND git-committed at a real SHA (re-scrape asset exists)
      │  (countries/ES/recipes/<cdp>.yaml tracked ∧ HEAD reachable ∧ entity.recipe_version set)
      ▼
G4 SERVED       live GET actually returns the inventory over the API
      │  (HTTP 200 ∧ /inventory count == DB available count ∧ envelope ok:true)
      ▼
G5 DELTA        a second harvest produces correct, well-typed events (delta engine proven live)
      │  (re-harvest → vehicle_event rows are internally consistent: GONE⊆prev, NEW∩prev=∅, Δ typed)
      ▼
   COMPLETED  → write entity_completion verdict TRUSTWORTHY, ledger row, completed_at watermark
```

Each sub-gate writes its own `verification_verdict` row (`subject_type='entity_stage'`,
`subject_key=<cdp_code>::G#`) so the **why** of any failure is forensically reconstructable
months later — not a boolean lost in a log.

---

## 2. The "COMPLETED" definition (normative, copy-pasteable)

> An entity `E` with code `C = E.cdp_code` is **`COMPLETED` at instant `t`** if and only if
> **all** of the following hold, each independently re-derived:
>
> 1. **(G1 Identity)** `entity` has exactly one row for `C`; `province_code ∈ {01..52}`;
>    `C` matches `^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$`; and either `(lat,lon)` are
>    set **or** the entity is flagged `geo_partial` with a logged reason. *(L6-resistant: a
>    code can't be minted without a province — verified in `cdp_code()` / `discover._upsert`.)*
> 2. **(G2 Inventory complete)** Let `S` = source-declared count, `H` = harvested distinct
>    deep_links, `D` = DB-landed `available` rows. **Quorum:** `D == H` **and** (`D == S`
>    **or** the residual `|S−D|` is explained by a logged dedup/closed reason). `D` is the
>    **authority** — see §3.B. No field-integrity violation (§3.B floor) on any landed row.
> 3. **(G3 Recipe durable)** `countries/ES/recipes/<C>.yaml` exists, is **git-tracked at a
>    commit reachable from HEAD**, parses as a valid recipe, and `entity.recipe_version`
>    equals the recipe's `version`. *(The recipe is the asset that lets us re-scrape without
>    the raw crude — `recipe.py` docstring. If it isn't committed, the entity is **not** done.)*
> 4. **(G4 Served)** `GET /entities/{C}/inventory` returns HTTP 200, `ok:true`, and
>    `meta.count` (or `len(data)`) **equals** `D`. `GET /entities/{C}` returns
>    `available_inventory == D`. *(A row no API can serve does not exist to a customer.)*
> 5. **(G5 Delta proven)** A **second** harvest of `C` ingests through the live delta engine
>    and the resulting `vehicle_event` rows are **type-consistent** (§3.G): every `GONE`
>    references a vehicle that was `available` before; every `NEW` deep_link was absent
>    before; every `PRICE_CHANGE/KM_CHANGE/PHOTO_CHANGE` has `old≠new` of the right type.
> 6. **(Freshness)** `now() − E.last_harvest_at ≤ SLA_E` for the entity's tier SLA (§3.F).
>
> The conjunction is recorded as one `entity_completion` ledger row with
> `verdict='TRUSTWORTHY'` and `completed_at=t`. **Absent that row, the entity is not
> completed, regardless of any agent's claim.**

---

## 3. Sub-gate mechanics, formulas, thresholds

### 3.A — G2 step 1: harvest-drain completeness (kills L2 silent cap)

The harvester (`autoscout24.harvest_dealer`) stops on one of three conditions: declared
count reached, a page added zero new links, or `max_pages`. Only the **first two** are
honest terminations. The drain proof:

```
drained_ok  ⟺  ( H ≥ S )                              # collected at least what source declared
            ∨  ( last_page_new == 0 ∧ pages_drained < max_pages )   # natural exhaustion
last_page_explicit ⟺ pages_drained < max_pages         # we did NOT bottom out on the cap
```

**Threshold:** if `pages_drained == max_pages` **and** `H < S`, the drain is **capped, not
complete** → G2 `FAIL`, origin `=<C>::G2::CAP`, severity `warning`. *(`max_pages=50` default
[VERIFIED]; the cap existing is fine — silently passing a capped harvest as "complete" is the lie.)*

### 3.B — G2 step 2: three-path count reconciliation + **db-landed authority** (kills L1, L3)

This reuses the live quorum in `ingest_dealer` (the three paths `db_available`,
`harvested`, `source_declared` are already computed [VERIFIED]) and `record_count_verdict`'s
**db-landed authority rule** [VERIFIED]: the primary path (what actually landed) MUST agree
with ≥1 other path, else a fetched/declared pair could mask ingestion loss.

```
S = harvest.declared_count          # source-declared (numberOfResults)   — orthogonal path 1
H = len(harvest.vehicles)           # harvested distinct deep_links        — orthogonal path 2
D = COUNT(vehicle WHERE entity=E AND status='available')   # DB-landed    — AUTHORITY path 3

verdict(G2) = TRUSTWORTHY ⟺  (D == H == S)
                          ∨  (D == H ∧ |S − D| ≤ τ_count·max(S,D) ∧ residual_is_logged)
```

**Why D is authority, not S:** `S` is the source's marketing counter and over-counts
duplicates, cross-posts, and reserved units; `H` can include links the parser saw but that
collided on the `UNIQUE(entity_ulid, deep_link)` constraint at insert time. Only `D` is what
a customer can actually retrieve. **Ingestion loss must never read as TRUSTWORTHY** — so if
`H > D` (rows fetched but not landed), G2 `FAIL` *even if* `H == S`. This is exactly the
`primary_agrees` guard in `verify.py:41` raised to a hard gate.

**Field-integrity floor (kills L3 hollow rows):** a landed `available` row counts toward `D`
**only if** its load-bearing fields are non-null:

```
row_valid ⟺ deep_link IS NOT NULL          # identity / re-fetch key (UNIQUE, NOT NULL [VERIFIED])
          ∧ (price IS NOT NULL ∨ price_absent_is_justified)   # "consultar precio" is a real state
          ∧ recipe_version IS NOT NULL       # provenance: which recipe produced it
D_valid = COUNT(available rows WHERE row_valid)
field_integrity_ratio = D_valid / D
```

**Threshold:** `field_integrity_ratio ≥ 0.98` (`τ_field`). Below → G2 `FAIL`, origin
`=<C>::G2::HOLLOW`. The 2% slack absorbs legitimately-null optional fields (e.g. VIN), never
the load-bearing trio. **`τ_count` default = 0.0** (exact match) for entities below 500 cars;
relaxes to `0.01` only above 2 000 cars where source counters legitimately drift intra-crawl,
and only with a logged residual reason.

### 3.C — G1: identity & geo (kills part of L6)

```
identity_ok ⟺ EXISTS(entity WHERE cdp_code=C)
            ∧ regex(C, '^CDP-ES-(0[1-9]|[1-4][0-9]|5[0-2])-[0-9A-HJKMNP-TV-Z]{8}$')
            ∧ province_code BETWEEN '01' AND '52'
            ∧ (lat IS NOT NULL ∧ lon IS NOT NULL  ∨  status_flag='geo_partial' WITH reason)
```

The `cdp_code` format is `CDP-ES-{province2}-{8×Crockford-base32}` [VERIFIED in `codes.py`];
the alphabet excludes `I,L,O,U` so the regex class is `[0-9A-HJKMNP-TV-Z]`. A code that does
not parse means a mint bug → `REFUTED`, not merely `INCOMPLETE`.

### 3.D — G3: recipe durability (kills "re-scrapable" hand-waving)

```
recipe_ok ⟺ Test-Path(countries/ES/recipes/<C>.yaml)
          ∧ git_tracked(<path>)                                   # not just on disk
          ∧ git_reachable_from_HEAD(blob_of(<path>))              # committed, not staged
          ∧ parse_yaml(<path>).version == entity.recipe_version   # the served rows came from THIS recipe
```

Disk-only is the trap: `write_recipe` writes the file [VERIFIED], but until it is committed
the asset is ephemeral and the entity is **not** durable. The gate shells
`git ls-files --error-unmatch <path>` and `git cat-file -e HEAD:<path>` — a non-zero exit is
G3 `FAIL`, origin `=<C>::G3::UNCOMMITTED`.

### 3.E — G4: live serve recount (kills L1 at the edge)

The validator issues real HTTP against the running API (`services/api/main.py`), not a DB
query, because **the customer's truth is the API response**, and the API could under/over-serve
relative to the table (pagination bug, stale pool, filter drift):

```
GET /entities/{C}/inventory  →  200 ∧ body.ok==true ∧ len(body.data)==D ∧ body.meta.count==D
GET /entities/{C}            →  200 ∧ body.data.available_inventory==D
served_ok ⟺ both hold
```

Mismatch between **served count** and **DB `D`** is its own detection (`SERVE_DRIFT`) routed
to fix, distinct from a harvest problem. *(Endpoints + envelope + `available_inventory` field
all [VERIFIED] in `main.py`.)*

### 3.F — Freshness watermark (kills L4 staleness)

Every gate read stamps and checks an entity-tier SLA. Staleness is a **completion-invalidating**
event: a once-completed entity silently *decays* to `STALE` and must re-prove G2/G4/G5.

| Entity tier | `SLA` (max age before STALE) | Rationale |
|---|---|---|
| Tier-1 platform / high-churn dealer | 24 h | inventory turns daily |
| Standard concesionario / compraventa | 7 d | weekly listing cadence |
| Long-tail garaje / desguace | 30 d | low churn |

```
fresh ⟺ (now() − E.last_harvest_at) ≤ SLA(tier(E))
STALE if ¬fresh → completion verdict downgraded to UNVERIFIED, re-queue G2.
```

### 3.G — G5: delta correctness (proves the live delta is real, not cosmetic)

A second harvest must produce **type-consistent** events through the existing engine
(`ingest_dealer` emits NEW/GONE/PRICE/PHOTO/KM with `old_value`/`new_value` JSONB [VERIFIED]).
Correctness predicates over the events of the second run:

```
∀ ev∈events:
  ev.type=='GONE'          ⇒ ev.vehicle was status='available' before run ∧ now 'gone'
  ev.type=='NEW'           ⇒ ev.deep_link ∉ prev_links ∧ now ∈ vehicle (available)
  ev.type=='PRICE_CHANGE'  ⇒ old.price ≠ new.price ∧ both numeric
  ev.type=='KM_CHANGE'     ⇒ old.km   ≠ new.km     ∧ new.km ≥ old.km   (odometers don't decrease)
  ev.type=='PHOTO_CHANGE'  ⇒ old.photo ≠ new.photo
conservation: D_after == D_before + #NEW − #GONE        # the count identity must close
```

A `KM_CHANGE` where `new.km < old.km` is a **fabrication/parse signal** (L5), not a normal
delta → G5 `FAIL`, origin `=<C>::G5::ODO_REVERSE`. The **conservation identity** is the
strongest single check: if landed-available count doesn't equal previous ± events, the delta
engine silently dropped or invented a row.

---

## 4. The blind re-scrape (the heart — kills L5 fabrication + L3 at row level)

For the entities the aggregate sample selects (§5), the validator does **not** look at the
stored data first. It performs a **cold, independent re-harvest** using the **committed
recipe** (proving the recipe asset actually works), then field-compares:

```
fresh   = re_harvest(C)                       # independent path, recipe-driven, no DB peek
stored  = GET /entities/{C}/inventory         # what we claim
fresh_links  = { v.deep_link for v in fresh }
stored_links = { r.deep_link for r in stored }

orphans   = stored_links − fresh_links        # we serve it, source doesn't have it  → FABRICATION (L5)
missing   = fresh_links − stored_links        # source has it, we don't serve it      → COVERAGE GAP (L6)
matched   = stored_links ∩ fresh_links

# per-matched-row field agreement on load-bearing fields:
field_mismatch(r) = (r.price≠fresh.price) ∨ (r.km≠fresh.km) ∨ (r.make≠fresh.make) ∨ (r.model≠fresh.model)
```

Per-entity **field error rate** and **set errors**:

```
e_set(C)   = (|orphans| + |missing|) / |fresh_links|         # listing-level error
e_field(C) = #{ r∈matched : field_mismatch(r) } / |matched|  # field-level error
entity_defect(C) ⟺ e_set(C) > θ_set  ∨  e_field(C) > θ_field
```

**Thresholds:** `θ_set = 0.02` (≤2 % listing drift tolerated — real churn between the
original harvest and the re-scrape window), `θ_field = 0.01` (≤1 % field drift). A re-scrape
is only valid if performed within the entity's SLA window of the original; otherwise observed
drift is legitimate churn, not a defect, and the entity is re-sampled (never counted as a
pass *or* a fail on stale comparison — that would itself be a lie). **Orphans are weighted
2×** in routing because fabrication (serving phantom inventory) is the worst lie CARDEEP can
tell.

---

## 5. The aggregate proof — "20 000 completed" by acceptance sampling

Per-entity gates make each entity's completion *checkable*; they do not, on their own, let us
**assert the population claim cheaply**. Re-scraping all 20 000 to validate 20 000 is circular
(same cost as building it) and still doesn't bound the ones you didn't blind-check. So the
population claim is proven by **statistical acceptance sampling**: blind-re-scrape a
random sample, and **assert "20 000 are completed" only at the confidence the sample
supports** — never the bare count.

### 5.1 What we are estimating

Let `N` = claimed-completed population (e.g. `N = 20 000`). Let `p` = the **true defective
fraction** (entities that would FAIL §4 blind re-scrape if checked). We want, with confidence
`1−α`, an **upper bound** `p_U` on `p`. The claim is reframed honestly:

> *"≥ `N·(1 − p_U)` of the `N` claimed entities are completed to spec, at `100·(1−α)%`
> confidence."* — e.g. "≥ 19 600 of 20 000 are verified complete at 95 % confidence,"
> not the unprovable "all 20 000 are done."

### 5.2 Sample size — attribute sampling (binomial / hypergeometric)

For a yes/no defect on each sampled entity, the worst-case (most conservative, `p=0.5`)
sample size for absolute precision `±m` at confidence `1−α`:

```
n0 = z²·p(1−p) / m²            with p=0.5 (max variance), z = z_{1−α/2}
n  = n0 / (1 + (n0−1)/N)       finite-population correction (hypergeometric)
```

**Worked numbers (N = 20 000):**

| Goal | z (α) | m | `n0` | `n` (FPC) |
|---|---|---|---|---|
| 95 % conf, ±3 % | 1.960 | 0.03 | 1067.1 | **1014** |
| 95 % conf, ±2 % | 1.960 | 0.02 | 2401.0 | **2144** |
| 99 % conf, ±2.5 % | 2.576 | 0.025 | 2654.3 | **2344** |

*(Compute check, 95 %/±3 %: `n0 = 1.96²·0.25/0.03² = 3.8416·0.25/0.0009 = 0.9604/0.0009 =
1067.1`; `n = 1067.1/(1+1066.1/20000) = 1067.1/1.0533 = 1013.1 → 1014`.)*

So **~1 000 blind re-scrapes** bound the defect rate of a 20 000-claim to ±3 % at 95 %.
That is the price of honesty for this claim, and it is ~5 % of the build cost — not circular.

### 5.3 The accept/reject decision (LQAS — the actual gate)

We don't just estimate `p`; we **accept or reject the 20 000 claim** with a defined quality
floor. Lot Quality Assurance Sampling: choose `(n, c)` = sample size, max allowed defects.
Accept the lot iff observed defects `d ≤ c`.

- **AQL** (acceptable quality, accept with high prob): `p₁ = 1 %` defective.
- **RQL/LTPD** (reject with high prob): `p₂ = 5 %` defective.
- Producer's risk `α = 0.05` (reject a good lot), consumer's risk `β = 0.10` (accept a bad lot).

A standard plan meeting these is **`n = 132, c = 3`** (binomial):

```
P_accept(p) = Σ_{d=0}^{c} C(n,d) p^d (1−p)^{n−d}
P_accept(0.01) = Σ_{d=0}^{3} C(132,d)·0.01^d·0.99^{132−d} ≈ 0.9557  (≥ 1−α ✓ good lot accepted)
P_accept(0.05) = Σ_{d=0}^{3} C(132,d)·0.05^d·0.95^{132−d} ≈ 0.0992  (≤ β   ✓ bad lot rejected)
```

*(λ-approx for the RQL point: `np₂ = 6.6`; Poisson `P(d≤3 | 6.6) = e^{-6.6}(1+6.6+21.78+47.9)
≈ 0.00136·77.3 ≈ 0.105`; exact binomial = 0.0992 — both ≤ β=0.10. The plan holds, with the
exact binomial sitting just under the 0.10 consumer-risk ceiling.)*

> **Operational rule:** blind re-scrape **132** random claimed-completed entities. If **≤3**
> fail §4, **accept** the claim "20 000 completed at AQL 1 %". If **≥4** fail, **reject** —
> the 20 000 claim is a lie at the 5 % quality floor; the manager (§7) quarantines the lot
> and the count reverts to only the per-entity-`TRUSTWORTHY` subset.

`n=132` is cheaper than the `±3 %` estimator (`n=1014`) because LQAS answers the **binary
accept/reject** question, not a precise point estimate. Run the **132-plan as the gate**;
run the **1014-sample only when you also need to publish a numeric coverage figure**.

### 5.4 Confidence-bounded count (what we are allowed to publish)

After observing `d` defects in `n`, the one-sided upper bound on `p` (Clopper–Pearson exact,
the honest bound for small `d`):

```
p_U = BetaInv(1−α; d+1, n−d)
```

**Worked (n=132, d=3, α=0.05):** `p_U = BetaInv(0.95; 4, 129) ≈ 0.0577`. Therefore the only
claim we may publish is:

> *"At 95 % confidence, ≤ 5.77 % of the 20 000 are defective ⇒ **≥ 18 845 are verified
> complete.**"*

If `d=0` in `n=132`: `p_U = 1−(α)^{1/n} = 1−0.05^{1/132} = 1−e^{ln0.05/132} = 1−e^{−0.0227}
= 0.0224` ⇒ "≥ 19 552 verified complete at 95 %." **We never write "20 000 done"** — we write
the bound the evidence earns. That is CARDEEP refusing to sell a lie.

### 5.5 Stratified sampling (kills L6 — the "easy ones" lie)

A simple random sample can still hide a coverage gap if defects concentrate in a hard stratum
(tier-1 platforms, anti-bot provinces, desguaces). So the sample is **stratified** and each
stratum gets an LQAS sub-plan; the lot is accepted only if **every stratum** passes:

| Stratum | Why it's a distinct risk | Min sub-sample |
|---|---|---|
| `is_tier1=TRUE` platforms | hard defense, recipe most likely to rot | 100 % if `N_tier1 ≤ 30`, else LQAS n=80,c=2 |
| Hard-WAF dealers (`website_waf ∈ datadome/akamai/perimeterx`) | re-scrape most likely to fail | proportional, min 50 |
| Low-churn (`desguace`,`garaje`) | staleness hides here (L4) | proportional, min 50 |
| Bulk standard (`concesionario`,`compraventa`) | the "easy" majority | remainder of n |

Allocation is **Neyman** (more sample where variance/defect-risk is higher):
`n_h = n · (N_h·S_h) / Σ_k (N_k·S_k)`, with `S_h` the stratum's prior defect std-dev.
**Acceptance is an AND across strata** — passing the bulk while tier-1 fails does **not**
accept the 20 000. This is the structural defense against "we did the 20k, just not the
hard 20k."

---

## 6. The completion ledger (the per-entity verdict store) [ASSUMED — proposed migration]

The existing `verification_verdict` table [VERIFIED] stores generic count quorums; the
**completion** state needs its own authoritative, queryable ledger so the API and the
manager can answer "is C done?" in O(1) and so "20 000 completed" is a **`COUNT(*)` against
ground truth**, not an agent's assertion.

```sql
-- migrations/0005_completion.sql  (additive, idempotent, reversible)  [ASSUMED]
CREATE TABLE IF NOT EXISTS entity_completion (
    cdp_code        TEXT PRIMARY KEY REFERENCES entity(cdp_code) ON DELETE CASCADE,
    g1_identity     BOOLEAN NOT NULL DEFAULT FALSE,
    g2_inventory    BOOLEAN NOT NULL DEFAULT FALSE,
    g3_recipe       BOOLEAN NOT NULL DEFAULT FALSE,
    g4_served       BOOLEAN NOT NULL DEFAULT FALSE,
    g5_delta        BOOLEAN NOT NULL DEFAULT FALSE,
    -- evidence
    s_declared      INT, h_harvested INT, d_landed INT, d_valid INT,
    field_integrity DOUBLE PRECISION,                 -- D_valid/D
    recipe_sha      TEXT,                              -- the commit proving G3
    served_count    INT,                               -- live API recount (G4)
    last_harvest_at TIMESTAMPTZ,                        -- freshness watermark
    sla_seconds     INT NOT NULL,                       -- tier SLA
    verdict         TEXT NOT NULL DEFAULT 'INCOMPLETE'
        CHECK (verdict IN ('COMPLETED','INCOMPLETE','STALE','REFUTED','QUARANTINED')),
    -- aggregate-proof linkage: was this entity in a blind-sample, and did it pass?
    last_blind_at   TIMESTAMPTZ,
    last_blind_pass BOOLEAN,
    e_set           DOUBLE PRECISION,                  -- §4 listing error
    e_field         DOUBLE PRECISION,                  -- §4 field error
    completed_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_completion_verdict ON entity_completion (verdict);
CREATE INDEX IF NOT EXISTS idx_completion_stale   ON entity_completion (last_harvest_at);

-- The ONLY trustworthy answer to "how many are completed":
--   SELECT count(*) FROM entity_completion WHERE verdict='COMPLETED'
--       AND now() - last_harvest_at <= make_interval(secs => sla_seconds);
-- Rollback: DROP TABLE IF EXISTS entity_completion;
```

**Invariant (DB-enforceable trigger):** `verdict='COMPLETED'` ⇒ `g1∧g2∧g3∧g4∧g5 = TRUE`
AND `completed_at IS NOT NULL`. The gate cannot write COMPLETED with any sub-gate false — the
binary AND is enforced at the storage layer, so even a buggy validator can't fabricate a
completion. Each gate flip also writes a `verification_verdict` audit row (`subject_type=
'entity_stage'`) for the forensic trail.

---

## 7. Routing every detection (fix / research / quarantine / escalate)

Every `FAIL` carries an exact origin (`<cdp_code>::G#::REASON`) written to `alert` [VERIFIED
table] and is routed by a deterministic manager:

| Detection (origin code) | Lie | Route | Action |
|---|---|---|---|
| `G2::CAP` (capped harvest) | L2 | **fix** | raise `max_pages`, re-harvest; recipe pagination bug → research |
| `G2::HOLLOW` (field_integrity<0.98) | L3 | **fix** | recipe field-map drift → re-derive recipe, re-ingest |
| `G2` count `H>D` (ingestion loss) | L1 | **fix** | dedup/constraint collision → reconcile, re-ingest |
| `G2` count `S≫H` unexplained | L1/L2 | **research** | source counter vs reality → human/agent investigates |
| `G3::UNCOMMITTED` | — | **fix** | `git add/commit` the recipe; block completion until SHA exists |
| `G4::SERVE_DRIFT` | L1 | **fix** | API/pool/filter bug — DB right, serve wrong |
| `G5::ODO_REVERSE` / orphans in §4 | L5 | **quarantine** | fabrication signal → freeze entity, no serve, escalate |
| §4 stratum reject (tier-1) | L6 | **escalate** | recipe rot on hard defense → senior + recipe-hunt workflow |
| `STALE` (freshness) | L4 | **fix** | re-queue G2/G4/G5; downgrade verdict to UNVERIFIED meanwhile |
| LQAS lot **reject** (d>c) | all | **escalate + quarantine lot** | revert count to per-entity-TRUSTWORTHY subset only |

**Quarantine** is non-negotiable for fabrication (L5): a quarantined entity is removed from
the served count and from any "completed" total until a human clears it. Better to confess the
gap than serve the phantom.

---

## 8. End-to-end worked example (one entity, then the 20 000)

**Entity** `C = CDP-ES-28-7Q2K9ABX` (a Pinto/Madrid concesionario):

| Gate | Observation | Predicate | Result |
|---|---|---|---|
| G1 | row exists, prov `28`, code parses, lat/lon set | identity_ok | **PASS** |
| G2 | `S=84, H=84, D=84, D_valid=83` → fi=0.988≥0.98; D==H==S | quorum ∧ floor | **PASS** |
| G3 | `recipes/CDP-ES-28-7Q2K9ABX.yaml` at HEAD SHA `a1b9…`; recipe_version=1==entity.recipe_version | recipe_ok | **PASS** |
| G4 | `GET /inventory` → 200, ok:true, len=84==D; `/entities` available_inventory=84 | served_ok | **PASS** |
| G5 | 2nd harvest: 2 NEW, 1 GONE, 1 PRICE_CHANGE; `84+2−1=85==D_after`; odo monotone | delta correct | **PASS** |
| Fresh | `last_harvest_at` 6 h ago, tier SLA 7 d | fresh | **PASS** |
| → | write `entity_completion … verdict='COMPLETED', completed_at=now()` | | **COMPLETED** |

**The population:** agent claims `N=20 000`. Validator runs the **132-entity LQAS plan**
(stratified: tier-1 100 %, hard-WAF ≥50, low-churn ≥50, bulk remainder), each via §4 blind
re-scrape. Observed: `d=2` defects (one `G2::HOLLOW`, one `missing>θ_set`), both in bulk
stratum, tier-1 stratum **0/all**. `d=2 ≤ c=3` ⇒ **lot ACCEPTED**. Published claim, from the
Clopper–Pearson bound `p_U=BetaInv(0.95;3,130)≈0.0469`:

> **"≥ 19 062 of 20 000 entities verified complete to spec at 95 % confidence; tier-1 stratum
> 100 % clean; 2 defects routed to fix."**

The ~938-entity gap is **confessed, not hidden**. That sentence is the entire point of
CARDEEP: a number nobody can refute, with the gap stated out loud.

---

## 9. Implementation surface (what `[ASSUMED]` work this doc commissions)

| Component | Path | Builds on (VERIFIED) |
|---|---|---|
| Completion ledger migration | `migrations/0005_completion.sql` | `entity`, `verification_verdict` |
| Per-entity gate runner | `pipeline/complete.py :: complete_entity(C)` | `ingest_dealer`, `record_count_verdict`, `write_recipe` |
| Live-serve recount client | reuses `services/api/main.py` endpoints | `/entities/{C}`, `/inventory` |
| Blind re-scrape comparator | `pipeline/blind.py :: blind_compare(C)` | `autoscout24.harvest_dealer`, committed recipe |
| Aggregate acceptance sampler | `pipeline/accept.py :: accept_lot(N, plan)` | `entity_completion`, stratify by `is_tier1`/`website_waf`/`kind` |
| Routing manager | `pipeline/route.py` | `alert`, `source_health` |

> Anti-stub discipline (mandate §Anti-atajo): these files do **not** exist yet and are **not**
> claimed as built — they are the commissioned surface this validator defines. The formulas,
> thresholds, and ledger schema above are complete and implementable as written; nothing here
> is a placeholder.

---

## 10. Symbols & thresholds (single reference table)

| Symbol | Meaning | Default |
|---|---|---|
| `S` | source-declared count (`numberOfResults`) | — |
| `H` | harvested distinct deep_links | — |
| `D` | DB-landed `available` rows (**authority**) | — |
| `D_valid` | landed rows passing field-integrity floor | — |
| `τ_count` | count-quorum tolerance | 0.0 (≤500 cars), 0.01 (>2000) |
| `τ_field` / field_integrity floor | min `D_valid/D` | 0.98 |
| `θ_set` | per-entity listing-error tolerance (§4) | 0.02 |
| `θ_field` | per-entity field-error tolerance (§4) | 0.01 |
| `SLA` | max age before STALE | 24 h / 7 d / 30 d by tier |
| `α` | confidence level complement | 0.05 (95 %) |
| `m` | sampling absolute precision | 0.03 |
| `p₁` AQL / `p₂` RQL | accept / reject quality | 1 % / 5 % |
| `(n,c)` | LQAS plan (sample, max defects) | (132, 3) |
| `n` estimator | ±3 %/95 % sample w/ FPC over N=20 000 | 1014 |
| `p_U` | Clopper–Pearson one-sided upper bound | reported per run |
```
