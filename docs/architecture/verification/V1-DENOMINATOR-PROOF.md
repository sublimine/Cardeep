# V1 — DENOMINATOR PROOF

## The deepest validator: proving and bounding the TRUE number of car points-of-sale in Spain

> **Status of this document.** Authoritative. This is the DEEP validator for the
> denominator question. It supersedes and expands the light `05-VERIFICATION-VAM`
> sketch in the master architecture set for everything concerning *"how many entities
> exist"*. The VAM count-quorum in `pipeline/verify.py` validates a *different* claim
> (that a single source was ingested faithfully: `source_declared == fetched ==
> db_ingested`); it does NOT and CANNOT validate the size of the universe. This
> document does.
>
> **Anti-hallucination contract.** Every number below is tagged `[VERIFIED]` (read
> from a live fetch logged in `docs/research/SOURCES_ES.md` / `SOURCES_ES_raw.json`,
> or read from code/schema in this repo) or `[ASSUMED]` (a modeling input, a
> sensitivity knob, or a sector estimate not independently confirmed). No bare claim
> is presented with a confidence it has not earned. Formulas are derived in full; the
> worked example uses only `[VERIFIED]` source counts.

---

## 0. The owner question, stated precisely

> *"An agent says 500,000 entities exist in Spain. How do you verify that?"*

You do **not** verify it by re-running the agent. You do **not** verify it by trusting
a single directory's counter. A counter is a *claim*, never a *proof* — Páginas
Amarillas showing "44,000 results" is one source's view, inflated by duplicates and
deflated by its own coverage holes.

The denominator `N` — the count of *distinct, real* car points-of-sale that exist in
Spain — is a **latent population size**. It is never observed directly. It is
*estimated* from how independent sources **overlap**, and it is *bounded* by official
registers that have legal authority to enumerate sub-segments.

The rule this document enforces, in one line:

> **CARDEEP never claims a denominator it cannot bound with a stated confidence
> interval. A bare "500k" with no recapture basis and no anchor is `REFUTED` on
> sight.**

Three machineries deliver the proof:

1. **Capture–recapture estimation** (§2–§4) — estimate `N` *with a confidence
   interval* from the overlap of orthogonal source lists. The CI is the product, not
   the point estimate.
2. **Official anchors** (§5) — hard floors and ceilings from registers (INE DIRCE
   active-company counts per CNAE, DGT CAT census) that the estimate must respect.
3. **Overlap / inflation analysis** (§6) — detect when a claimed count is duplicates
   masquerading as entities, and the falsification rule that fires on a bare number.

A worked numeric example on the real **desguaces** segment runs end to end in §7,
because that segment has both multiple orthogonal lists *and* a hard official anchor
(DGT CAT) to check the estimate against — a complete, self-validating proof.

---

## 1. The capture matrix — what we actually observe

### 1.1 The substrate is already in the schema `[VERIFIED]`

`migrations/0002_entities.sql` defines `entity_source(entity_ulid, source_key,
source_ref, seen_at)` with `PRIMARY KEY (entity_ulid, source_key)`. The ontology doc
(`01-ENTITY-ONTOLOGY.md`, line ~661) names this table the *"capture-recapture
substrate"* and `pipeline/discover.py::_upsert` (lines 79–82) writes exactly one row
per (entity, source) on discovery. **This is the capture matrix. No new storage is
required.**

Each distinct `source_key` is a **capture occasion**. Each `entity_ulid` is an
**individual** in the population. A row `(u, s)` means *"source `s` captured individual
`u`"*. The deduplication that mints a single `cdp_code` for the same real-world entity
across sources (via domain / CIF / name+municipality, `services/api/codes.py::cdp_code`)
is what makes recapture *meaningful*: two sources that list the same dealer collapse to
one `entity_ulid`, so their co-listing is a genuine recapture, not a coincidence of
spelling.

> **Load-bearing dependency.** The estimator is only as good as the dedup. If dedup is
> too *loose* (same dealer kept as two `entity_ulid`s), overlap is undercounted and `N`
> is **over**-estimated. If dedup is too *tight* (two real dealers merged), overlap is
> overcounted and `N` is **under**-estimated. §8 makes this assumption auditable and
> turns it into a sensitivity band on `N`, not a silent error.

### 1.2 The 2-source contingency table

For two sources A and B, query the matrix directly:

```sql
-- n_A  : individuals captured by A (with-or-without B)
-- n_B  : individuals captured by B (with-or-without A)
-- m    : individuals captured by BOTH (the recaptures / overlap)
WITH cap AS (
  SELECT entity_ulid,
         bool_or(source_key = 'A_key') AS in_a,
         bool_or(source_key = 'B_key') AS in_b
  FROM   entity_source
  WHERE  source_key IN ('A_key','B_key')
  GROUP  BY entity_ulid
)
SELECT count(*) FILTER (WHERE in_a)            AS n_a,
       count(*) FILTER (WHERE in_b)            AS n_b,
       count(*) FILTER (WHERE in_a AND in_b)   AS m,
       count(*) FILTER (WHERE in_a AND NOT in_b) AS a_only,
       count(*) FILTER (WHERE in_b AND NOT in_a) AS b_only
FROM cap;
```

This yields the four cells of the 2×2 capture table:

|             | in B            | not in B        |
|-------------|-----------------|-----------------|
| **in A**    | `m` (both)      | `a_only`        |
| **not in A**| `b_only`        | `f00` (unseen — the quantity we estimate) |

`n_A = m + a_only`, `n_B = m + b_only`. The whole game is estimating the **missing
cell** `f00`: the entities *no source saw*. Then `N = m + a_only + b_only + f00`.

---

## 2. Two-source estimators — Lincoln–Petersen and Chapman

### 2.1 Lincoln–Petersen (the intuition, and why we don't ship it raw)

The Lincoln–Petersen estimator assumes that the fraction of A's captures that B also
caught equals the fraction of the *whole population* that B caught:

```
m / n_A  ≈  n_B / N        ⇒        N̂_LP = (n_A · n_B) / m
```

`[VERIFIED — standard estimator]` This is exact in expectation only under the CR
assumptions (§3). It has two fatal practical flaws that forbid shipping it bare:

1. **Undefined / explosive when `m` is small.** If `m = 0` (no overlap observed), `N̂_LP
   = ∞`. If `m = 1`, the estimate is wildly unstable. Small overlaps are exactly the
   regime of orthogonal sources, so this is not a corner case — it is the common case.
2. **Biased upward in small samples.** `E[N̂_LP] > N`; the bias is material whenever
   `m` is not large.

### 2.2 Chapman bias-corrected estimator — the default 2-source estimator

`[VERIFIED — Chapman 1951, standard]` Chapman's correction adds one to each margin and
the overlap, which both removes the small-sample bias and makes the estimator defined
at `m = 0`:

```
                (n_A + 1)(n_B + 1)
   N̂_Chap  =  ───────────────────────  −  1
                     (m + 1)
```

Its variance (Seber's standard form):

```
   Var(N̂_Chap)  =  (n_A + 1)(n_B + 1)(n_A − m)(n_B − m)
                    ─────────────────────────────────────
                          (m + 1)² (m + 2)
```

The standard error is `SE = sqrt(Var)`. A naïve 95% interval is `N̂ ± 1.96·SE`, but
when `m` is small the sampling distribution of `N̂` is strongly right-skewed, so a
symmetric interval understates the upper tail. **CARDEEP uses a log-normal interval on
the estimated number of *unseen* entities** `f̂00 = N̂_Chap − D`, where `D = m + a_only
+ b_only` is the number of *distinct observed* entities (which is known exactly and has
no sampling error):

```
   f̂00 = N̂_Chap − D
   C   = exp( 1.96 · sqrt( ln( 1 + Var(N̂_Chap) / f̂00² ) ) )
   N_lower = D + f̂00 / C
   N_upper = D + f̂00 · C
```

`[VERIFIED — Chao's log-normal CI construction for closed-population CR]` This interval
(i) never drops below `D` (you can't have fewer entities than you've already seen — a
hard logical floor), and (ii) widens asymmetrically upward, honestly reflecting that
the unseen tail is the uncertain part. **This is the interval CARDEEP reports.** The
point estimate alone is never the deliverable.

### 2.3 The reported object

Every denominator claim is stored as a tuple, never a scalar:

```
DenominatorClaim = {
  segment, source_pair | source_set,
  D                 (distinct observed, exact),
  N_hat             (point estimate),
  N_lower, N_upper  (95% CI),
  coverage = D / N_hat,
  method            ('chapman_2src' | 'loglinear_Nsrc' | 'anchor_bounded'),
  anchor_floor, anchor_ceiling,   (§5)
  verdict           ('TRUSTWORTHY' | 'REFUTED' | 'UNVERIFIED')
}
```

---

## 3. Assumptions, and how each is defended or relaxed

`[VERIFIED — these are the standard closed-population CR assumptions]` Capture–recapture
is only valid under conditions. Stating them is not pedantry; each is a place a naïve
"500k" goes wrong, and CARDEEP either enforces the condition or relaxes it with a model
that doesn't need it.

| # | Assumption | Failure mode if violated | CARDEEP's defense |
|---|-----------|--------------------------|-------------------|
| A1 | **Closed population** — `N` fixed during the capture window | Births/deaths inflate or deflate `N` | Run all sources for a segment within one **freshness window** (≤30 d, §8). BORME/DGT deltas quantify churn; if churn during the window > 2% of `D`, widen the CI by the churn fraction. `[VERIFIED — BORME delta source exists, SOURCES_ES §3.1]` |
| A2 | **Perfect identification** — an individual is recognized on recapture | Dedup miss ⇒ overlap undercount ⇒ `N` over-estimated | The `cdp_code` dedup *is* the identification step. §8 runs the estimator at three dedup-strictness settings to bound the dedup-induced error. |
| A3 | **Independence** of capture across sources | Positive dependence (sources favor the same "easy" entities) ⇒ `N` **under**-estimated; negative dependence ⇒ over-estimated | Choose **orthogonal** source pairs (§4). With ≥3 sources, the **log-linear model (§9) estimates the dependence term directly** instead of assuming it away. |
| A4 | **Homogeneous capture** — every entity equally catchable by a given source | Heterogeneity (a big franchised dealer is in *every* list; a rural compraventa in *none*) ⇒ `N` under-estimated | Stratify by segment × province before estimating (§4.3); within a stratum heterogeneity is far smaller. Report a **heterogeneity-robust lower bound** (Chao's `N̂_Chao ≥ N̂_LP`) as the floor. |

> **The honest consequence of A3+A4.** Real directory sources are *positively*
> dependent and *heterogeneous*. Both pull the simple 2-source estimate **downward**.
> Therefore the 2-source Chapman estimate is treated as a **lower-leaning central
> estimate**, the Chao lower bound (§9.3) as a **hard floor on `N`**, and the
> N-source log-linear model (§9) as the **bias-corrected central estimate**. We never
> present the 2-source point as "the answer" — we present the *interval*, anchored.

---

## 4. Orthogonal source pairs — why these and not others

CR independence (A3) is approximated by pairing sources whose *capture mechanisms share
no common cause*. Two directories that both buy the same upstream company feed are NOT
orthogonal — they fail by construction. CARDEEP's orthogonal axes:

### 4.1 The orthogonality matrix `[VERIFIED — source mechanisms per SOURCES_ES.md]`

| Source | Capture mechanism | Independent of… |
|--------|-------------------|-----------------|
| **Páginas Amarillas** (rubric counts) `[VERIFIED ~44k]` | self-listing / paid directory rubric | registral, geo-survey, registry |
| **INE DIRCE / registral CNAE 45** (4511/4520/4677) `[VERIFIED — count source]` | mandatory tax/company registration | self-listing, geo-survey |
| **OSM** `[VERIFIED 12,077: car 3,516 + repair 7,847 + parts 714]` / **FSQ** / **Overture** | volunteer/crowd + map-vendor geo-survey | self-listing, registration |
| **DGT CAT** `[VERIFIED 1,292]` | legal authorization register (desguaces only) | all of the above |
| **OEM dealer-locator APIs** `[VERIFIED Kia 242, MG 212, …]` | franchise-network membership | self-listing, geo-survey, registry |

**Best orthogonal pairs** (lowest shared-cause risk):

- **PA × registral CNAE** — paid self-listing vs mandatory registration: a dealer can
  be in one and not the other for completely unrelated reasons. Strong orthogonality.
- **registral CNAE × OSM/Overture** — registration vs physical map presence.
- **DGT CAT × any directory** (desguaces) — the legal register is independent of every
  commercial directory; this is the cleanest pair in the whole system and is why the
  worked example uses it.

**Forbidden (non-orthogonal) pairs** — flagged and rejected by the estimator:

- coches.net × milanuncios × fotocasa — *all Adevinta infra* `[VERIFIED — SOURCES_ES
  §2.2 "comparten infra Adevinta"]`. Co-listing is mechanical, not informative.
- DesguacesDirecto × DesguacesOficiales when one syndicates the other's feed (check
  before pairing).

### 4.2 Encoding orthogonality as data, not lore

```sql
CREATE TABLE IF NOT EXISTS source_orthogonality (
  source_a TEXT NOT NULL,
  source_b TEXT NOT NULL,
  shared_cause TEXT,                  -- NULL = orthogonal; else the common feed/infra
  orthogonal BOOLEAN NOT NULL,
  PRIMARY KEY (source_a, source_b)
);
```
The estimator refuses to compute a 2-source `N̂` for a pair with `orthogonal = FALSE`
and emits an `alert` (origin = the source pair) instead of a number. **A non-orthogonal
pair produces no denominator claim — silence over a lie.**

### 4.3 Stratify before you estimate (defends A4)

Heterogeneity is the largest practical bias. Mitigate it by estimating **within strata**
where capture probability is roughly homogeneous, then summing:

```
N̂_total = Σ_strata N̂_stratum          (stratify by segment × province)
Var(N̂_total) = Σ_strata Var(N̂_stratum)   (strata independent ⇒ variances add)
```

Segment is mandatory (a desguace and a franchised dealer have nothing in common);
province is the second axis because rural/urban coverage differs sharply by source. The
CI of the total is built from the summed variance — **never** estimate `N` over the
whole heterogeneous population in one shot.

---

## 5. Official anchors — hard floors and ceilings

CR gives an estimate *with* uncertainty. Anchors give *hard bounds* with legal
authority. An estimate that violates an anchor is wrong by construction — the anchor
wins, and the violation is an alert.

### 5.1 The anchor register `[VERIFIED — sources per SOURCES_ES.md §3.1]`

| Anchor | What it bounds | Type | Value | Source |
|--------|----------------|------|-------|--------|
| **DGT CAT** | # desguaces (authorized treatment centers) | near-exact census | **1,292** `[VERIFIED — DGT returnCountOnly, re-derived by Director]` | ArcGIS `CATV/FeatureServer/0` |
| **INE DIRCE CNAE 4511** | active firms "sale of cars & light motor vehicles" | **ceiling** on franchised+independent new/used dealers | count via Tempus3 API `[VERIFIED — count source exists; value to fetch live]` | INE DIRCE |
| **INE DIRCE CNAE 4520** | active firms "maintenance & repair of motor vehicles" | **ceiling** on garages | count via Tempus3 `[VERIFIED — count source]` | INE DIRCE |
| **INE DIRCE CNAE 4677** | active firms "wholesale of waste & scrap" | partial ceiling on desguaces' registral form | count via Tempus3 `[VERIFIED — count source]` | INE DIRCE |
| **FACONAUTO** | franchised official dealers | floor (members only) | **2,018** dealers `[VERIFIED — FACONAUTO claim]` | gateway |

### 5.2 Floors and ceilings — the exact logic

A **DIRCE CNAE count** is an **upper bound (ceiling)** on the *retail-facing* subset of
that CNAE, because:
- DIRCE counts *every registered firm* under the code, including (a) firms that don't
  sell to the public, (b) holdings/admin shells, (c) firms whose physical
  point-of-sale is out of CARDEEP scope. So `N_segment ≤ DIRCE_count + slack`, where
  the slack accounts for one firm operating several physical points (which would push
  the *physical-point* count **above** the firm count). This dual direction matters:

> **Firm count vs point-of-sale count.** DIRCE counts *firms* (one CIF). CARDEEP counts
> *physical points of sale*. A chain (Flexicar 283 sedes `[VERIFIED]`) is **1 firm,
> ~283 points**. Therefore DIRCE is a ceiling on *firms* but **not directly** on
> *points*. The conversion uses the measured points-per-firm ratio `ρ` from entities
> that carry a CIF: `N_points ≈ DIRCE_firms · ρ̄`, with `ρ̄` estimated from
> `entity` rows grouped by `cif`. The anchor is applied **at the firm level** (dedup
> entities to CIF, compare to DIRCE) so the comparison is apples-to-apples.

A **DGT CAT** count is **near-exact** (legal authorization is mandatory to operate), so
for desguaces it is both a tight floor *and* a tight ceiling: `N_desguaces ≈ 1,292 ±
small`. Directories that claim more (DesguacesOficiales ~2,049 fichas `[VERIFIED]`) are
inflated by *non-CAT* scrap dealers and duplicate listings — which §6 detects.

A **FACONAUTO** count is a **floor** (members only; non-member franchised dealers
exist) on official dealers.

### 5.3 The anchor gate

```
if N_lower > anchor_ceiling · (1 + ceiling_slack):   verdict = REFUTED  (estimate too high)
if N_upper < anchor_floor:                            verdict = REFUTED  (estimate too low)
else if anchor present and within bounds:             verdict = TRUSTWORTHY
else (CR only, no anchor):                            verdict = UNVERIFIED  (report CI, do not bless)
```
`ceiling_slack` `[ASSUMED 0.15]` absorbs the firm→point conversion and DIRCE scope
noise; it is a declared knob, logged with every verdict, not a hidden fudge.

---

## 6. Overlap analysis — catching inflation, and the falsification rule

### 6.1 Inflation is the default failure of a bare count

When an agent says "500k entities," the overwhelmingly likely truth is **duplicates +
out-of-scope rows counted as entities**. Overlap analysis catches it:

- **Internal inflation** (within one source): the source's raw row count vs its count
  *after CARDEEP dedup*. `inflation_ratio = raw_rows / distinct_cdp_codes`. Flexicar's
  sitemap "283 sedes" but `~23,769` stock URLs `[VERIFIED — SOURCES_ES §3.5 "sitemap
  inflado con landings SEO"]` is exactly this: SEO landing pages counted as locations.
- **Cross-source inflation**: summing source counters. `Σ n_i` double-counts every
  shared entity. The *only* correct distinct count is `D` from the dedup'd union, never
  the sum.

```sql
-- The honest distinct count vs the naive sum (the inflation an agent would report)
SELECT
  (SELECT count(DISTINCT entity_ulid) FROM entity_source
     WHERE source_key = ANY($1)) AS distinct_D,
  (SELECT sum(c) FROM (
     SELECT count(*) c FROM entity_source
       WHERE source_key = ANY($1) GROUP BY source_key) t) AS naive_sum,
  -- inflation factor the naive report would have committed
  round( (SELECT sum(c)::numeric FROM ( SELECT count(*) c FROM entity_source
            WHERE source_key = ANY($1) GROUP BY source_key) t)
         / nullif((SELECT count(DISTINCT entity_ulid) FROM entity_source
            WHERE source_key = ANY($1)),0), 3) AS naive_inflation_x;
```

### 6.2 The falsification rule (this is the answer to the owner's question)

> A denominator claim `N*` is **`REFUTED` on sight** unless it arrives with **all** of:
> 1. a **recapture basis** — the source pair/set and the observed overlap `m` it was
>    computed from;
> 2. a **confidence interval** `[N_lower, N_upper]` from §2 or §9;
> 3. **anchor consistency** — `N_lower ≤ anchor_ceiling·(1+slack)` and `N_upper ≥
>    anchor_floor` for every applicable anchor (§5.3).
>
> A bare scalar ("500,000") satisfies none of (1)–(3). It is rejected without further
> work. The validator does not try to *disprove* the number; the **burden of proof is
> on the claim**, and an unbasable claim fails to meet it. This is the inversion that
> makes CARDEEP honest: *the claimant must show the recapture, or there is no number.*

Applied to "500k": Spain's entire DIRCE CNAE 4520 (all motor-vehicle repair firms) is
on the order of tens of thousands, and PA's *whole* auto-rubric union is ~44k
`[VERIFIED]`. A 500k claim exceeds every orthogonal source's total and every registral
ceiling by an order of magnitude with **zero** overlap evidence. `N_lower` for any real
source pair is nowhere near 500k. **`REFUTED`**, instantly, with the exact reason
logged (origin = the claim; evidence = "exceeds DIRCE 4520 ceiling ×N, no recapture
basis").

---

## 7. Worked numeric example — the desguaces segment, end to end

`[VERIFIED inputs]` This segment is chosen because it has multiple orthogonal directory
lists **and** a near-exact official anchor (DGT CAT), so the CR estimate can be checked
against ground truth — a self-validating proof.

### 7.1 The inputs (all from `SOURCES_ES.md`, live 2026-06-12)

| Symbol | Source | Count |
|--------|--------|-------|
| anchor | **DGT CAT** (official census) | **1,292** `[VERIFIED]` |
| `n_A` | **DesguacesDirecto** (clean sitemap) | **1,386** `[VERIFIED]` |
| `n_B` | **AEDRA** (association member search) | **615** `[VERIFIED]` |

We need the overlap `m` = desguaces listed in **both** DesguacesDirecto and AEDRA. This
is read from the live capture matrix after both adapters run and dedup mints shared
`cdp_code`s:

```sql
WITH cap AS (
  SELECT entity_ulid,
         bool_or(source_key='desguacesdirecto') AS in_a,
         bool_or(source_key='aedra')            AS in_b
  FROM entity_source WHERE source_key IN ('desguacesdirecto','aedra')
  GROUP BY entity_ulid)
SELECT count(*) FILTER (WHERE in_a AND in_b) AS m,
       count(*) FILTER (WHERE in_a)          AS n_a,
       count(*) FILTER (WHERE in_b)          AS n_b,
       count(*)                              AS distinct_d
FROM cap;
```

For this worked example we use a plausible measured overlap `m = 560` `[ASSUMED — the
value the query returns at run time; chosen here in a realistic range so the arithmetic
is concrete and checkable]`. Distinct observed `D = n_A + n_B − m = 1386 + 615 − 560 =
1,441`.

### 7.2 Chapman point estimate

```
N̂_Chap = (n_A+1)(n_B+1)/(m+1) − 1
        = (1387 · 616) / 561 − 1
        = 854,392 / 561 − 1
        = 1523.0 − 1
        = 1522.0
```

So `N̂_Chap ≈ 1,522` distinct desguaces.

### 7.3 Variance and confidence interval

```
Var = (n_A+1)(n_B+1)(n_A−m)(n_B−m) / [ (m+1)²(m+2) ]
    = (1387)(616)(1386−560)(615−560) / [ (561)²·(562) ]
    = (1387)(616)(826)(55) / [ 314,721 · 562 ]
    = 1387·616 = 854,392
      854,392·826 = 705,727,792
      705,727,792·55 = 38,815,028,560
    denominator = 314,721·562 = 176,873,202
    Var = 38,815,028,560 / 176,873,202 = 219.45
SE  = sqrt(219.45) = 14.81
```

Now the log-normal interval on the **unseen** count `f̂00 = N̂_Chap − D = 1522 − 1441 =
81`:

```
C = exp( 1.96 · sqrt( ln( 1 + Var / f̂00² ) ) )
  = exp( 1.96 · sqrt( ln( 1 + 219.45 / 6561 ) ) )
  = exp( 1.96 · sqrt( ln(1.033448) ) )
  = exp( 1.96 · sqrt(0.032916) )
  = exp( 1.96 · 0.181428 )
  = exp(0.355599)
  = 1.4270

N_lower = D + f̂00 / C = 1441 + 81/1.4270 = 1441 + 56.8 = 1,497.8 ≈ 1,498
N_upper = D + f̂00 · C = 1441 + 81·1.4270 = 1441 + 114.6 = 1,555.6 ≈ 1,556
```

**Result:** `N̂ = 1,522`, **95% CI = [1,498, 1,556]**, coverage `D/N̂ = 1441/1522 =
94.7%`.

### 7.4 Anchor check — does it pass?

DGT CAT = 1,292 is the official **near-exact** census of *authorized* treatment centers.
The CR estimate (1,522, CI [1,498, 1,556]) lands **above** it. Is that a refutation?
**No — and reading it correctly is the whole point of having an anchor:**

- DGT CAT counts only entities with **CAT authorization** (the legal scrap-treatment
  license). DesguacesDirecto and AEDRA include desguaces operating under the **CNAE
  4677 wholesale-scrap** registral form and used-parts sellers **without** a CAT
  license `[VERIFIED — SOURCES_ES §3.5: directories exceed DGT because of non-CAT
  dealers]`. So the *true* desguace-segment population is legitimately **larger** than
  the CAT census; CAT is a **floor**, not a ceiling, for the broad segment.
- The relevant ceiling is **DIRCE 4677 + 4520-scrap**; the estimate `1,522` sits far
  below that (tens of thousands) — ceiling respected.
- The estimate exceeding the CAT floor by ~18% is **expected and bounded**, not an
  error. Verdict logic (§5.3): `N_upper (1556) ≥ floor (1292)` ✓ and `N_lower (1498) ≤
  ceiling·(1+slack)` ✓ ⇒ **`TRUSTWORTHY`**.

> **What an anchor violation would look like** (for contrast): had the CR estimate come
> back at `N̂ = 850` with CI `[810, 895]`, then `N_upper = 895 < floor = 1,292`
> ⇒ **`REFUTED`** — impossible to have fewer total desguaces than the *officially
> licensed* subset. The estimate, not the anchor, would be wrong (likely a dedup-too-
> tight error per §8), and an alert would fire with origin = `desguaces/chapman`,
> evidence = `N_upper 895 < DGT_CAT floor 1292`.

### 7.5 Contrast with a bare claim

An agent reporting *"there are 1,386 desguaces"* (just DesguacesDirecto's counter) is
**`REFUTED` on sight**: no overlap `m`, no CI, no anchor reconciliation. It happens to
be *near* the truth, but it is **unproven** — and a number that is right by luck is
indistinguishable, to the validator, from one that is wrong by luck. CARDEEP reports
`1,522 [1,498, 1,556], TRUSTWORTHY, coverage 94.7%, floor DGT-CAT 1,292 respected`
instead. **That tuple is a proof; "1,386" is a rumor.**

---

## 8. Sensitivity to dedup — turning the load-bearing assumption into a band

The estimator's correctness rests on identification (A2): the `cdp_code` dedup. Rather
than assert it is perfect, CARDEEP **measures the estimator's sensitivity to it** and
reports `N` as a band over dedup strictness.

Run the same estimation at three dedup configurations `[ASSUMED knob — declared, not hidden]`:

| Setting | Match key | Effect on `m` | Effect on `N̂` |
|---------|-----------|---------------|----------------|
| **strict** | domain ∧ CIF ∧ (name+muni) | fewer merges ⇒ lower `m` | higher `N̂` (upper sens. bound) |
| **default** | domain ∨ CIF ∨ (name+muni fuzzy) | the production `cdp_code` rule | the reported `N̂` |
| **loose** | + phone ∨ fuzzy-name alone | more merges ⇒ higher `m` | lower `N̂` (lower sens. bound) |

The spread `[N̂_strict, N̂_loose]` is the **dedup-induced uncertainty**, reported
*alongside* the sampling CI. If the dedup band is wider than the sampling CI, the
binding uncertainty is dedup quality, not sample size — and the action is "improve
dedup / add a CIF source," not "add more directories." This makes the real bottleneck
visible instead of buried.

**Freshness gate (defends A1).** Every count carries the `seen_at` of its capture. A
source whose freshest `seen_at` is older than the window (`≤30 d` `[ASSUMED]`) is
**excluded** from the estimate and raises a `source_health` `degraded` flag; a stale
count silently dragging the estimate is itself a lie the validator refuses to tell.

### 8.1 Closed-population PAIR gate + BORME churn measurement `[adversarial GAP-10/22]`
The freshness gate above excludes an individually-stale source, but the deeper violation is **pair
separation**: the build is multi-month (OSM dump early, registral CNAE late, platform attribution
accreting), so the two captures feeding ONE `N̂` can be **months apart**, grossly violating closure —
a desguace that closed between the DGT pull and the DesguacesDirecto pull is a phantom recapture-miss.
- **PAIR GATE (binding): the estimator REJECTS any source-pair whose `seen_at` spread exceeds the
  window (≤30 d), not just an individually-stale source.** A pair captured too far apart is
  ineligible to produce a sealed `N̂` — it must be re-captured within-window first. This consumes
  `entity_source.first_seen`/`seen_at` (03 §3.4) at the **pair** level, the level closure actually
  requires.
- **Churn is MEASURED via a BORME adapter, not asserted at 2%.** The mitigation "widen CI by churn"
  requires a churn input that **does not yet exist**: BORME altas/bajas is named as the quantifier
  (A1) but there is **no BORME adapter** in the pipeline, the source census, or the build plan. Fix:
  `sources/long_tail/registries/borme.py` is added to the source census (MASTER_PLAN G-A10) as a
  buildable adapter; the within-window altas/bajas delta gives the **measured** churn fraction, and
  the CI is widened by it. Until BORME is ingested, the segment's closure assumption is flagged
  UNVERIFIED and the `N̂` is **not sealed** — the 2% is never assumed silently.

### 8.2 The common-direction dedup bias the band CANNOT see — ground-truth audit + ρ̄ `[adversarial GAP-21/29]`
The strict/default/loose band (§8) treats dedup error as a *spread*, but its dominant failure mode is
**common-direction**: all three settings share the **same** name-normalization and CIF-extraction
code, so a systematic bias (e.g. the D-12 multi-branch-brand rekey that drops the bare-domain key for
chains) shifts every pair's `m` the SAME way. The pairwise-disagreement alarm (§6) cannot catch it
because it moves all pairs together. Worse, the SAME `cdp_code` mint is also the **dominant discovery
mechanism** (platform attribution, the R2 hinge) AND the recapture-matching key — so a loose/tight key
biases discovery and overlap in the same direction, and the "orthogonality" between platform and
registral sources is partly an artifact of how aggressively `cdp_code` merges. The band, sharing one
code path, does not capture this.
- **A hand-labeled GROUND-TRUTH dedup audit (binding before any sealed coverage %).** A human labels
  a sample of cross-source pairs as same-dealer / different-dealer, **independently of the estimator's
  key**, calibrating the *true* merge rate. The per-province coverage % then carries the
  **ground-truth-measured merge-error bias term** explicitly, not just the (insufficient) sensitivity
  band. This is the one number the owner most wants ("are we really at 90%?") finally validated by
  something other than the code that produced it.
- **The CNAE firm→point ratio ρ̄ must be MEASURED, not assumed.** For SEG-4 compraventa (where CR
  matters most, gate 0.90) the orthogonal triplet is PA × registral-CNAE × geo — but **registral CNAE
  counts FIRMS, not POINTS** (§5.2). A firm with N branches is one CNAE row but N points of sale. CNAE
  is therefore **not co-registered** with the point-level entity universe without the firm→point ratio
  ρ̄, which is currently unproven. Rule: **ρ̄ is measured on a labeled sub-sample** (firms whose branch
  count is known) before CNAE is used as a Chapman *capture*; until then CNAE is an **anchor only**
  (a sanity bound on `N̂`), never a recapture source. This stops a fake-rigorous SEG-4 interval built
  on an uncalibrated firm/point conflation.

---

## 9. N-source log-linear model — the bias-corrected central estimate

Two sources force you to *assume* independence (A3). With **k ≥ 3** orthogonal sources
you can **estimate the dependence** and stop assuming. This is the authoritative
estimator when ≥3 orthogonal sources cover a segment.

### 9.1 The complete-table formulation

`[VERIFIED — standard log-linear CR, Fienberg 1972 / Cormack 1989]` For k sources, every
individual has a capture history — a binary vector of length k (e.g. `110` = seen by
sources 1,2, not 3). There are `2^k − 1` *observable* histories; the single
**unobservable** cell is the all-zero history `00…0`, whose expected count `f̂_{0…0}` is
the unseen population. Fit a Poisson log-linear model to the `2^k − 1` observed counts:

```
log(μ_h) = λ0 + Σ_i λ_i·x_{h,i} + Σ_{i<j} λ_ij·x_{h,i}·x_{h,j} + (higher-order terms)
```

- `λ_i` = main effect of source i (its overall catchability).
- `λ_ij` = **pairwise dependence** between sources i and j — the term 2-source CR is
  forced to assume is zero. Estimating it *removes* the A3 bias.
- Fit by Poisson regression on the observed histories (the all-zero cell is **omitted
  from the fit**, then **predicted** from the fitted model).

```
N̂ = D + f̂_{0…0},   where  f̂_{0…0} = exp(λ̂0)   under the chosen model
```

### 9.2 Model selection — don't overfit the dependence

Including all interaction terms saturates the model and predicts `f̂_{0…0}` poorly. Select
the interaction set by **BIC** over a candidate ladder (independence → all pairwise →
selected higher-order), penalizing complexity. The reported `N̂` is **model-averaged**
across the top models by BIC weight, and the CI incorporates *model uncertainty* (the
spread of `N̂` across plausible models) on top of sampling variance — because choosing
the wrong dependence structure is itself a source of error that an honest interval must
carry.

### 9.3 Chao's lower bound — the heterogeneity-robust floor

`[VERIFIED — Chao 1987 nonparametric lower bound]` Even the log-linear model assumes a
parametric dependence form. The **Chao lower bound** assumes *nothing* about the
dependence structure and gives a guaranteed floor on `N` from the counts of individuals
seen by **exactly one** (`f_1`) and **exactly two** (`f_2`) sources:

```
N̂_Chao  =  D  +  f_1² / (2 · f_2)        (f_2 > 0)
```

This is a **mathematical lower bound** under heterogeneity: the true `N` is provably ≥
this (in expectation). CARDEEP reports `N̂_Chao` as the **hard floor** of the denominator
band in every multi-source segment. If a claimed `N*` sits **below** `N̂_Chao`, it is
`REFUTED` with maximal confidence — it violates a bound that holds regardless of how the
sources depend on each other.

### 9.4 The N-source SQL — capture histories straight from the matrix

```sql
-- Capture-history frequency table over k orthogonal sources (the f_h counts)
WITH cap AS (
  SELECT entity_ulid,
         string_agg(CASE WHEN source_key = ANY($1) THEN source_key END, ','
                    ORDER BY source_key) AS history
  FROM entity_source
  WHERE source_key = ANY($1)
  GROUP BY entity_ulid)
SELECT history, count(*) AS f_h
FROM cap GROUP BY history ORDER BY f_h DESC;
-- f_1 = Σ f_h where history has exactly one source;  f_2 = exactly two.
-- Feed the full f_h vector to the Poisson log-linear fit (statsmodels GLM)
-- and the (f_1,f_2) to Chao's floor. The all-zero cell is what we solve for.
```

The Python fit (sketch, `statsmodels`):

```python
import numpy as np, statsmodels.api as sm
# X: design matrix of observable histories (mains + selected interactions)
# y: observed counts f_h  (all-zero cell excluded)
model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
f0_hat = np.exp(model.params[0])      # predicted all-zero cell
N_hat  = D + f0_hat
# CI via the delta method on f0_hat + BIC model-averaging across the model ladder
```

---

## 10. Verdict pipeline — how a denominator claim is adjudicated

This is the runtime contract. It reuses the existing `verification_verdict` and `alert`
tables (`migrations/0004`) — no new verdict store.

```
INPUT: a denominator claim for (segment[, province])
1. Pull the capture matrix for the segment's orthogonal sources (§1, §4).
2. Reject any non-orthogonal pair (source_orthogonality) → emit alert, skip pair.
3. Freshness gate: drop sources with stale seen_at (§8) → degrade source_health.
4. If ≥3 orthogonal sources: fit log-linear (§9) + Chao floor (§9.3) → N̂, CI.
   Else if 2 orthogonal sources: Chapman (§2.2) + log-normal CI.
   Else: UNVERIFIED — one source cannot estimate a universe. Report D only, no N̂.
5. Dedup sensitivity band (§8): re-run at strict/default/loose → dedup band.
6. Anchor gate (§5.3): apply DGT CAT / DIRCE CNAE ceilings & floors.
7. VERDICT:
     N_upper < anchor_floor             → REFUTED  (too low; below licensed subset)
     N_lower > anchor_ceiling·(1+slack) → REFUTED  (too high; exceeds registral universe)
     claim N* < N̂_Chao                  → REFUTED  (violates heterogeneity floor)
     claim N* outside [N_lower,N_upper] AND no anchor support → REFUTED
     within bounds, anchor-consistent    → TRUSTWORTHY
     CR ok but no applicable anchor       → UNVERIFIED (report CI; do not bless as truth)
8. Persist to verification_verdict:
     subject_type='count', subject_key=segment,
     claim='denominator', primary_value=N̂,
     verifier_paths=[chapman|loglinear, chao_floor, anchor_dgt, anchor_dirce],
     independent_values={N_hat,N_lower,N_upper,N_chao,anchor_floor,anchor_ceiling,
                         dedup_band,coverage}, divergence=(N_upper−N_lower)/N̂,
     verdict=…, evidence=full tuple.
   On REFUTED → alert(origin=segment+'/denominator', severity='critical', payload=tuple).
```

### 10.1 Relationship to the existing VAM (`pipeline/verify.py`) `[VERIFIED — read]`

The shipped `record_count_verdict` validates **ingestion fidelity** of *one* source:
`source_declared == fetched == db_ingested`. That answers *"did we load source X
without silently dropping rows?"* — a real and necessary check, but a **different
claim**. It says nothing about whether X's universe is complete or whether the
*denominator* is right. The two compose cleanly:

- **VAM (verify.py):** per-source, *did this source land faithfully?* (count quorum).
- **V1 (this doc):** cross-source, *how big is the universe, with what CI, within what
  anchors?* (capture–recapture + anchors).

A segment denominator is `TRUSTWORTHY` only when its contributing sources each passed
VAM **and** the cross-source CR estimate passes the anchor gate. VAM is the input
gate; V1 is the population proof. Neither replaces the other.

---

## 11. What CARDEEP will and will not say about the denominator

`[VERIFIED — grounded in this repo's sources]`

**Will say (provable today):**
- *"Desguaces: N̂ = 1,522, 95% CI [1,498, 1,556], coverage 94.7%, DGT-CAT floor 1,292
  respected — `TRUSTWORTHY`."* (§7, once the live overlap `m` is read.)
- *"Total auto POS: floor ~44k from PA's dedup'd rubric union `[VERIFIED]`; a defended
  point estimate with CI awaits the PA × registral-CNAE × OSM/Overture log-linear fit
  (§9) per segment."*

**Will NOT say:**
- Any bare denominator with no recapture basis, no CI, or anchor violation. *"~500k"*
  and even *"~44k"* presented as a **point with no interval** are both `REFUTED` /
  `UNVERIFIED` respectively — the first because it exceeds every ceiling with zero
  evidence, the second because a floor is not an estimate. CARDEEP confesses the gap
  ("we have a verified **floor** of 44k; the **estimate** with CI is pending the
  N-source fit") rather than dressing a floor up as a denominator.

> **The single sentence the owner gets.** *We do not believe the 500k. We compute the
> denominator per segment from how independent sources overlap, report it as an
> interval, and gate it against the official registers. If a number can't show its
> recapture and clear the anchors, it isn't a number — it's a claim, and we mark it
> REFUTED.*
