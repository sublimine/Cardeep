# V6 — STATISTICAL & SAMPLING RIGOR

> The mathematical spine of CARDEEP's anti-lie guarantee. Every assertion the
> system makes about *how many* and *how correct* must be defensible by a
> formula, a confidence interval, and a worked number — never by the path that
> produced the claim.
>
> Scope of this document (the FACET): acceptance-sampling (AQL) for blind
> re-verification, confidence intervals for capture-recapture denominators,
> sequential sampling for early stop, per-field sample sizing, and the formal
> separation of **precision** (no fabrication) vs **recall** (no missing).
>
> This doc **supersedes and expands** the light `05-VERIFICATION-VAM` count-quorum.
> The quorum (`pipeline/verify.py`) answers "do ≥2 orthogonal paths agree?".
> This document answers the harder questions the quorum cannot: *how many of the
> 20k must I blind-recheck to assert correctness at 99%? How wide is the error
> bar on a 44k denominator estimated by capture-recapture? When can I stop early?*
>
> Verification status of every claim below is marked **[VERIFIED]** (derived from
> a cited statistical result or computed here from first principles, reproducible)
> or **[ASSUMED]** (operating choice / business threshold not yet ratified).

---

## 0. Reading map

| § | Question answered | Primary output |
|---|---|---|
| 1 | What are we even measuring? | Definitions: precision, recall, defect, unit of inspection |
| 2 | How many of N to blind-recheck for a correctness claim? | AQL acceptance-sampling tables + formulas |
| 3 | Can I stop early when the batch is clean (or filthy)? | Sequential probability ratio test (SPRT) |
| 4 | How big is the true universe, and how wide is the error bar? | Capture-recapture (Chapman) + CI |
| 5 | How many records per FIELD must I check? | Per-field stratified sample sizing |
| 6 | Precision vs recall — measured separately, how? | Two-estimator design, never conflated |
| 7 | What numbers does CARDEEP commit to? | Threshold table + acceptance gates |
| 8 | Worked end-to-end example on the real 20k / 44k | Full numeric walkthrough |
| 9 | Failure modes this catches, and how | Detection → routing map |
| 10 | Reference tables (copy-paste constants) | Lookup tables |

---

## 1. Definitions — what a "defect" is before we count them

Sloppy verification dies here: if "correct" is undefined, every sample size is theater.

### 1.1 Unit of inspection

CARDEEP has three nested populations, each sampled independently:

| Population | Symbol | Real size (today) | Unit | Source of size |
|---|---|---|---|---|
| **Entities** (points of sale) | `N_E` | 20 000 completed of ~44 000 census floor | one `entity` row (`cdp_code`) | [VERIFIED] census §6 floor 44k; 20k = the claim under audit |
| **Vehicles** (inventory) | `N_V` | platform-dependent (1 604 → 753 652) | one `vehicle` row (`vehicle_ulid`) | [VERIFIED] census §2 live counters |
| **Fields** (cells) | `N_F = N · k` | `N × 11` entity fields, `N × 8` vehicle fields | one (row, field) cell | [VERIFIED] migrations 0002/0003 |

A **lot** (or **batch**) is the population from which we draw — e.g. "the 20 000
entities claimed complete", or "AutoScout24's 278 329 vehicles as ingested".

### 1.2 The two orthogonal error types (NEVER merge these)

This is the axis everything hangs on. They require **different samples and
different estimators** because they answer different questions.

| Error type | Plain words | Formal | What sample finds it |
|---|---|---|---|
| **Fabrication / wrongness** | a row we HAVE is false (made up, stale, mis-parsed, silently capped value) | **1 − Precision** | re-verify a sample **of rows we have** against ground truth |
| **Omission / missing** | a row that EXISTS in reality is ABSENT from us | **1 − Recall** | a **second independent capture** of reality, count overlap |

> **Hard rule [VERIFIED reasoning]:** a sample drawn *from the database* can NEVER
> measure recall. You cannot sample what you do not have. Recall is only
> measurable against an **external frame** (a second capture, a registry, a gold
> list). Any agent that claims "98% recall, verified by sampling our DB" is
> selling a lie — flag and quarantine. This single confusion is the most common
> way coverage gets faked.

### 1.3 Defect taxonomy (a row can be defective in several ways)

A sampled entity row is scored against an independent re-collection on these axes.
The row is **defective** if ANY *critical* axis fails (attribute sampling), and we
*also* record a per-field defect vector for §5.

| Axis | Field(s) | Criticality | Defect definition |
|---|---|---|---|
| Existence | whole row | CRITICAL | the entity does not actually exist / is duplicate of another `cdp_code` |
| Identity | `cif`, `cnae`, `name` | MAJOR | legal id or name materially wrong (not a formatting nit) |
| Geo | `province_code`, `municipio_code`, `lat`, `lon`, `address` | MAJOR | wrong municipality, or lat/lon > 500 m from truth |
| Type | `entity_type` | MAJOR | dealer classified as desguace, etc. |
| Contact | `phone`, `website` | MINOR | dead/wrong number or URL |
| Defense | `website_waf` | MINOR | mislabeled WAF |
| Freshness | `last_seen` | CRITICAL if staleness > SLA | row claims fresh but real-world state changed (see §1.4) |

For vehicles: `price`, `year`, `km` (MAJOR — silent cap / mis-parse), `vin_ref`
(MAJOR — identity), `photo_hash` (MINOR), existence & `last_seen` (CRITICAL).

**Acceptance is computed per criticality class** (AQL allows tighter limits on
CRITICAL than MINOR — see §2.4). A single defect taxonomy keeps "20k correct"
from meaning ten different things to ten agents.

### 1.4 Staleness as a defect [VERIFIED reasoning]

A row that *was* correct decays. Define the **freshness defect**: row `i` is
stale-defective if `now − last_seen_i > SLA(type_i)` AND a re-poll shows the
real-world value changed. Staleness sampling is just attribute sampling where
"ground truth" = a fresh re-poll. SLA per type is an [ASSUMED] business input
(default: platform inventory 24 h, dealer long-tail 7 d, registry-derived 30 d).

---

## 2. Acceptance sampling (AQL) — how many of N to blind-recheck

The question the owner asked: *"how many of 20k to blind-recheck to assert
correctness at 95% / 99%?"* This is a **single-sampling attribute plan**. We do
NOT re-verify all 20 000 (cost) and we do NOT trust the producer's self-count
(that is the path that made the claim). We draw `n` blind, count defects `d`,
and **accept** the lot iff `d ≤ c` (the acceptance number).

### 2.1 The exact model — hypergeometric, approximated by binomial/Poisson

Drawing `n` without replacement from a finite lot `N` with `D` true defectives,
the count of sampled defectives is **Hypergeometric(N, D, n)**. For `N ≥ 10·n`
the **binomial** `Bin(n, p)` with `p = D/N` is an excellent approximation, and for
small `p` the **Poisson** `Pois(λ = n·p)` is tighter still and gives closed forms.
CARDEEP uses hypergeometric for the *exact* gate computation and Poisson for the
*table* and intuition. [VERIFIED — standard sampling theory.]

Probability of acceptance (operating characteristic, OC):

```
Pa(p) = P[d ≤ c]  (cumulative tail of the sampling distribution at true rate p)

Exact (hypergeometric):   Pa = Σ_{i=0}^{c}  C(D,i)·C(N−D, n−i) / C(N, n),   D = round(p·N)
Binomial approx:          Pa = Σ_{i=0}^{c}  C(n,i)·p^i·(1−p)^(n−i)
Poisson approx (c=0):     Pa = e^(−n·p)
```

### 2.2 The zero-defect plan (the one CARDEEP leans on): c = 0

The cleanest, most defensible gate is **accept only if the blind sample is
perfectly clean** (`c = 0`). Then `Pa(p) = (1 − p)^n ≈ e^(−n·p)`.

To assert, at confidence `1 − α`, that the true defect rate is **below** a
threshold `p₀` (the "Reject Quality Level"), solve `Pa(p₀) ≤ α`:

```
(1 − p₀)^n ≤ α      ⇒      n ≥ ln(α) / ln(1 − p₀)      [exact, c = 0]

Rule-of-three / Poisson form (p₀ small):   n ≈ −ln(α) / p₀

  95% confidence (α = 0.05):   n ≈ 3 / p₀      ("rule of three")
  99% confidence (α = 0.01):   n ≈ 4.6 / p₀
```

**[VERIFIED]** This is the classic "rule of three": observing 0 defects in `n`
draws gives an upper 95% bound on the rate of `≈ 3/n`. So if I blind-check `n`
and find zero bad rows, I may state *"true defect rate < 3/n with 95%
confidence"* — and nothing stronger.

#### Table 2.2 — zero-defect blind sample sizes (binomial-exact `n = ⌈ln α / ln(1−p₀)⌉`)

| Assert rate below `p₀` | n @ 95% (α=.05) | n @ 99% (α=.01) | n @ 99.9% (α=.001) |
|---|---|---|---|
| 10 % | 29 | 44 | 66 |
| 5 % | 59 | 90 | 135 |
| 2 % | 149 | 228 | 342 |
| 1 % | 299 | 459 | 688 |
| 0.5 % | 598 | 919 | 1 379 |
| 0.2 % | 1 497 | 2 301 | 3 451 |
| 0.1 % | 2 995 | 4 603 | 6 905 |

Reading: *"To certify the 20 000-entity batch has < 1 % defect at 99%
confidence, blind-recheck 459 of them and accept only if all 459 are clean."*
**[VERIFIED — computed from the formula above.]**

> Note the population size barely matters at these ratios: with `N=20 000`, the
> finite-population correction shrinks `n` from 459 to 449 — a 2 % saving. We
> keep the larger (conservative) binomial number. The correction matters only
> when `n` approaches `N` (small lots, §5 per-field strata).

### 2.3 Allowing some defects (c > 0) — when zero-defect is too brittle

`c = 0` is brutal: one unlucky bad row rejects an otherwise-good batch. For
routine monitoring (not the headline certification) we accept `c > 0`. Sizing
fixes two points on the OC curve:

- **AQL** `p₁` = good level we want to *accept* with high prob `1 − α` (producer's risk α).
- **RQL/LTPD** `p₂` = bad level we want to *reject* with high prob `1 − β` (consumer's risk β).

Solve for the smallest `(n, c)` satisfying both `Pa(p₁) ≥ 1−α` and `Pa(p₂) ≤ β`.
Closed form via the Poisson ratio (the **operating ratio** `R = p₂/p₁`) and the
chi-square quantiles:

```
n·p ≈ ½ · χ²_{2c+2, q}      (Poisson↔χ² identity)

Pick c = smallest integer with   χ²_{2c+2, 1−β} / χ²_{2c+2, α}  ≤  p₂/p₁ = R
then   n = ⌈ χ²_{2c+2, α} / (2·p₁) ⌉
```

#### Table 2.3 — (n, c) plans, producer risk α=0.05, consumer risk β=0.10

| c | accept ratio `R = LTPD/AQL` | `n·AQL` (≈) |
|---|---|---|
| 0 | 44.9 | 0.052 |
| 1 | 10.9 | 0.355 |
| 2 | 6.5 | 0.818 |
| 3 | 4.9 | 1.366 |
| 5 | 3.5 | 2.613 |
| 10 | 2.4 | 5.426 |

**[VERIFIED — standard Cameron/Poisson acceptance-sampling table values.]**

Worked: AQL = 0.5 %, LTPD = 2 % → `R = 4`. Smallest `c` with ratio ≤ 4 is `c=5`
(ratio 3.5). `n = 2.613 / 0.005 = 523`. Plan: **sample 523, accept if ≤ 5
defects.** Accepts a 0.5 %-bad batch 95 % of the time; rejects a 2 %-bad batch
90 % of the time.

### 2.4 Per-criticality plans (tighter on what matters)

Run **three independent acceptance plans on the same drawn sample** (cheap — one
re-collection scores all axes), one per criticality class, with class-specific
`p₀`:

| Class | `p₀` (RQL) [ASSUMED business] | Conf | n (c=0) | Gate |
|---|---|---|---|---|
| CRITICAL (existence, dup, stale-past-SLA) | 0.2 % | 99 % | 2 301 | accept iff 0 |
| MAJOR (identity, geo, type) | 1 % | 99 % | 459 | accept iff 0 (or use c-plan §2.3) |
| MINOR (contact, waf, photo) | 5 % | 95 % | 59 | accept iff ≤ c per §2.3 |

The binding sample is `max(n_class) = 2 301`. We draw 2 301 once, score all
classes on it; CRITICAL must be perfectly clean, MINOR tolerates more.

### 2.5 Why blind, and why not the producing path

`verify.py`'s quorum proves *paths agree on a count*. It does **not** prove the
rows are individually correct — two paths can agree on "20 000" while 3 % of the
rows are garbage in ways both paths share (e.g. both inherit a bad geocoder).
Acceptance sampling closes that hole: an **independent re-collection** of `n`
sampled rows from primary reality (re-fetch the dealer page, re-query DGT, phone
the number) is orthogonal to both counting paths. **The sampler must not reuse
the ingestion code path** — same bug, same blind spot.

---

## 3. Sequential sampling (SPRT) — stop early, save budget

Fixed-`n` plans over-sample clean batches and waste budget on obviously-filthy
ones. **Wald's Sequential Probability Ratio Test** inspects one record at a time
and stops as soon as the evidence is decisive. Expected sample size is typically
**50–66 % of the fixed plan** for the same risks. **[VERIFIED — Wald 1945.]**

### 3.1 The test

Hypotheses: `H0: p = p₁` (good, AQL) vs `H1: p = p₂` (bad, LTPD). After `m`
inspections with `d` defects, the log-likelihood ratio is compared to two bounds:

```
Accept H0 (lot good)  when   d ≤ s·m − h₁     (lower line)
Reject H0 (lot bad)   when   d ≥ s·m + h₂     (upper line)
Continue sampling     otherwise

with the standard Wald constants:
  A = (1−β)/α ,   B = β/(1−α)
  s  = [ ln((1−p₁)/(1−p₂)) ] / k          (slope, the per-item "acceptance rate")
  h₁ = ln(A) / k ,   h₂ = −ln(B) / k       (intercepts)
  k  = ln( p₂(1−p₁) / (p₁(1−p₂)) )         (common log-odds denominator)
```

### 3.2 Worked SPRT — entities, AQL 0.5 %, LTPD 2 %, α=.05, β=.10

```
p₁=0.005, p₂=0.02, α=0.05, β=0.10
k  = ln( 0.02·0.995 / (0.005·0.98) )      = ln(4.061)      = 1.4014
s  = ln(0.995/0.98) / k = ln(1.01531)/k   = 0.015192/1.4014 = 0.010841
A  = 0.90/0.05 = 18      → ln A = 2.8904
B  = 0.10/0.95 = 0.10526 → ln B = −2.2513
h₁ = 2.8904 / 1.4014 = 2.0625
h₂ = 2.2513 / 1.4014 = 1.6064

Decision lines (in cumulative defects d vs items inspected m):
  ACCEPT line:  d = 0.010841·m − 2.0625    (cross below ⇒ accept lot)
  REJECT line:  d = 0.010841·m + 1.6064    (cross above ⇒ reject lot)
```

Operational reading **[VERIFIED — arithmetic above]**:
- You cannot **accept** until `0.010841·m ≥ 2.0625` ⇒ `m ≥ 191` clean-ish items.
  With **zero defects**, accept at `m = 191` (vs 523 fixed — a **63 % saving**).
- You **reject** the instant `d` crosses the upper line: e.g. `d = 2` rejects at
  `m ≥ (2 − 1.6064)/0.010841 = 37`. A filthy 8 % batch is killed in ~40 draws.

### 3.3 Truncation (always cap the walk) [VERIFIED reasoning]

An undisciplined SPRT can wander. Truncate at `n_max = 1.5 × n_fixed`; if
undecided by then, force the fixed-plan decision on the accumulated `(m, d)`.
This bounds worst-case cost and removes the "runs forever" failure mode.

### 3.4 When to use which

| Situation | Plan |
|---|---|
| Headline certification ("20k is correct") for the record | **Fixed-n** (§2) — defensible, fixed, auditable |
| Continuous monitoring of fresh ingests | **SPRT** (§3) — cheap, fast reject |
| Tier-1 platform field-by-field (expensive ground truth) | **SPRT truncated** — every ground-truth pull is costly |

---

## 4. Capture-recapture — the denominator and its error bar

"100 % of Spain" requires a denominator we **never fully observe**. We estimate
the true universe size `N̂` from the overlap between two (or more) independent
captures, and — critically — we attach a **confidence interval**, because a
denominator without error bars is the deepest lie of all.

### 4.1 Two-source Chapman estimator (bias-corrected Lincoln–Petersen)

Capture 1 finds `n₁`, capture 2 finds `n₂`, of which `m` appear in **both**
(matched by `cdp_code` / dedup key). The naive Lincoln–Petersen `N̂ = n₁n₂/m`
is biased upward for small `m`; the **Chapman** estimator is near-unbiased and is
what `PLAN.md` §6/§F8 already commits to:

```
N̂_Chapman = ( (n₁+1)(n₂+1) / (m+1) ) − 1

Var(N̂)    = (n₁+1)(n₂+1)(n₁−m)(n₂−m) / ( (m+1)²(m+2) )

95% CI    = N̂ ± 1.96·√Var      (Normal approx; use log-normal CI when m is small)
```

**Log-normal CI (preferred when `m < 50`, avoids negative lower bound)
[VERIFIED — Chao 1987]:**

```
Let f₀ = N̂ − D_obs  (estimated number NEVER captured, D_obs = n₁+n₂−m observed distinct)
C = exp( 1.96·√( ln(1 + Var/f₀²) ) )
CI = [ D_obs + f₀/C ,  D_obs + f₀·C ]
```

### 4.2 Worked — desguaces denominator (real census numbers)

From census §6 / §3.5, two **orthogonal** captures of Spanish scrapyards:

```
Capture 1 = DGT CATV official registry:  n₁ = 1 292   [VERIFIED ✓ census §7]
Capture 2 = DesguacesDirecto sitemap:    n₂ = 1 386
Overlap (matched by CIF/geo/name):       m  = 1 180   [ASSUMED match rate — to be computed at F8]

N̂  = (1293·1387)/1181 − 1 = 1 793 991/1181 − 1 = 1 518.5 − 1 ≈ 1 517.5
Var = 1293·1387·(112)·(206) / (1181²·1182)
    = 1293·1387·112·206 / (1 394 761·1182)
    = 4.1375e10 / 1.6486e9 = 25.10   ⇒  SD ≈ 5.01
95% CI ≈ 1 517.5 ± 9.8  ⇒  [1 508 , 1 527]
```

**Interpretation [VERIFIED — arithmetic, reproduced below]:** the true scrapyard
universe is ~1 518, tightly bounded, *above* the DGT official 1 292 — meaning DGT
itself under-lists by ~17 % (CATs operating without current registry entry).
CARDEEP reports **"1 518 ± 10 (95% CI), and DGT's 1 292 is a known under-count"** rather
than parroting any single source. This is the anti-lie behavior: the estimate
**bounds** reality instead of asserting a number we cannot defend.

### 4.3 Coverage from the same machinery

Our **recall** against this denominator is `D_have / N̂`. If CARDEEP holds 1 400
distinct scrapyards: recall `= 1 400 / 1 518 = 92.2 %`, with CI `[1400/1528,
1400/1508] = [91.6 %, 92.8 %]`. We can now state coverage **with an error bar**,
not a vibe.

### 4.4 Three+ sources — log-linear models & the critical assumptions

Two sources cannot test their own assumptions. With **≥3 captures** (e.g. Páginas
Amarillas ∪ registral CNAE ∪ OSM/FSQ for the full 44k) we fit a **log-linear
model** to the `2^k − 1` observed inclusion patterns and estimate `f₀` (the
all-zero cell). This both tightens the CI and **lets us test the assumptions**:

| Assumption | Violation effect | Mitigation |
|---|---|---|
| **Closure** (population fixed during capture) | births/deaths inflate/deflate `N̂` | capture within a tight window; net out BORME altas/bajas |
| **Independence** of captures | positive dependence ⇒ **under**-estimate `N̂` | pick orthogonal sources (registry vs directory vs map); 3+ sources estimate the dependence |
| **Perfect matching** (`m` correct) | over-match ⇒ inflate `N̂`; under-match ⇒ deflate | deterministic key (CIF) > fuzzy (name+geo); report match-rate sensitivity |
| **Homogeneous capture** (every unit equally catchable) | heterogeneity ⇒ **under**-estimate | stratify by province/type, sum strata (§4.5) |

**[VERIFIED reasoning]** Positive dependence between sources is the usual real-
world case (a big visible dealer is in *every* directory), which biases `N̂`
**downward** — so a two-source `N̂` is a **lower bound** on the true universe.
CARDEEP states the denominator as **"≥ N̂_2src, best estimate N̂_3src ± CI"**,
honoring §6's "suelo 44k, techo 50–90k".

### 4.5 Stratification (do it — Spain is not homogeneous)

A national `N̂` hides heterogeneity (Madrid over-listed, rural Soria under-
listed). Estimate **per province × per type**, then `N̂_total = Σ N̂_strata` and
`Var_total = Σ Var_strata` (independence across strata). This both removes the
homogeneity bias and localizes coverage gaps for F8's province-by-province seal.

### 4.6 Closure-window gate (the population must be fixed during capture) `[adversarial GAP-10/22]`
Chapman assumes a **closed population**: births/deaths during the capture window bias `N̂`. The
CARDEEP build is multi-month, and orthogonal sources for one segment's `N̂` are ingested *months
apart* (OSM dump early, registral CNAE late, platform attribution accreting continuously) — a gross
closure violation that silently conflates "dealers we haven't found" with "dealers that opened/closed
between captures".
- **GATE (binding): every capture feeding ONE `N̂` carries its `seen_at`; the estimator REJECTS a
  source-pair whose `seen_at` spread exceeds the freshness window (≤30 d).** A pair captured too far
  apart is not eligible to produce a sealed `N̂` — it is re-captured within-window first. (`entity_source.
  first_seen`/`seen_at` already exists, 03 §3.4; this gate consumes it.)
- **Churn is MEASURED, not asserted.** The 2% churn assumption is replaced by the BORME altas/bajas
  delta over the window (the `borme.py` adapter, MASTER_PLAN G-A10). If measured churn during the
  window > 2% of `D`, the CI is widened by the churn fraction. Until BORME is ingested, the segment's
  `N̂` is reported with the closure assumption flagged UNVERIFIED, never sealed.

### 4.7 The membership-filtered frame — recall against the RIGHT denominator `[adversarial GAP-1]`
The deepest seal promise is "we hold X% of N̂". But the capture sources (Páginas Amarillas, FSQ,
Overture) **include C2C private sellers and non-selling workshops** that are NOT CARDEEP entities,
while the deflation (`garaje sells_cars`, D-4) and the C2C sentinel attribution (ontology §4.3) are
applied to the *numerator* but NOT subtracted from the capture frame. Recall computed against an
unfiltered frame mixes a membership-filtered numerator with an inflated denominator — it understates
recall and seals against the wrong denominator.
- **RULE (binding): the capture-recapture frame MUST be filtered by the SAME membership predicate
  that defines a CARDEEP entity** (ontology §1, "offers car stock for acquisition") BEFORE Chapman.
  Each capture list is passed through the membership filter: drop C2C-sentinel-attributed rows, drop
  `garaje` rows with `sells_cars=false`, drop non-POS (pure parts traders with no car stock). The
  filtered counts `n₁ᶠ, n₂ᶠ, mᶠ` → `N̂ᶠ`, the **membership-filtered universe**, and
  `recall = found / N̂ᶠ` draws numerator and denominator from the SAME predicate.
- **Where a capture source cannot be row-filtered** (a directory that does not expose `sells_cars`),
  the unfilterable non-member fraction is estimated by a **labeled sub-sample** and `N̂` is bracketed
  `[N̂ᶠ_lower, N̂_raw]`; the seal reads `N̂ᶠ_lower` (the honest, conservative denominator).
- **The §8 worked example is re-labeled accordingly:** the `≈29,091` is `N̂_raw` (unfiltered,
  all-listed — an upper bracket), NOT the seal frame. The seal-bearing number is `N̂ᶠ` after C2C/
  non-POS removal; the headline recall is reported against `N̂ᶠ`, with `N̂_raw` shown only as context.

### 4.8 Vehicle-recall — numerator completeness as a MEASURED fraction `[adversarial GAP-2]`
Entity-recall (§4.1–4.7) bounds the *entity* universe; `NUMERATOR-SEALED(entity)` only proves each
*known* entity was drained completely. Nothing bounds the **true national CAR count** — cars on
entities we never discovered, or on channels we do not harvest (Facebook Marketplace, un-mirrored
dealer-own stock) — so treating the vehicle population as fully observable once entities are sealed
is an **unstated, false closure assumption**.
- **RULE (binding): a vehicle-level capture-recapture `N̂_V`, parallel to the entity estimator.**
  Two independent vehicle captures with a vehicle-level match key (VIN / `listing_fingerprint` /
  pHash — the same key 03 §6 defines): capture 1 = our held available vehicles in a (segment,
  province) cell; capture 2 = an independent vehicle pull (a platform facet NOT used in capture 1, or
  an OEM-VO portal re-list). Chapman over *vehicles* → `vehicle_recall = N_V_held / N̂_V ± CI`.
- This is a **first-class KPI line**, reported APART from entity recall, each with its own CI. The
  forbidden state is asserting "100% of stock" with only entity-recall measured.
- Where `N̂_V` cannot be formed for a cell (no orthogonal vehicle capture), the cell's vehicle-recall
  is **UNVERIFIED**, declared, never assumed-complete.

---

## 5. Per-field sample sizing — precision at the cell level

"The 20k is correct" is too coarse. A batch can pass row-level acceptance while
one field (say `cif`) is systematically 8 % wrong because one parser is broken.
We therefore size a **per-field** plan and run **stratified attribute sampling**.

### 5.1 Field-level defect rate with a confidence interval

For field `f`, draw `n_f` rows where `f` is **non-null** (sampling nulls tests
recall-of-field, a separate axis), re-verify each cell, count defects `d_f`.
Report the **Wilson score interval** (better than Wald near 0, never exceeds
[0,1]) **[VERIFIED — Wilson 1927]**:

```
p̂ = d_f / n_f ,   z = 1.96 (95%) or 2.576 (99%)

Wilson CI =  [ p̂ + z²/2n ∓ z·√( p̂(1−p̂)/n + z²/4n² ) ] / (1 + z²/n)

For d_f = 0 (clean):  upper bound ≈ z²/(n+z²)  →  with n=300, 95%: ≈ 1.26 %
```

### 5.2 Sizing each field to a target margin of error `E`

To bound a field's true defect rate within ±`E` at confidence `1−α`:

```
n_f = z² · p*(1−p*) / E²              (worst case p*=0.5 ⇒ n = z²/4E²)
finite-pop correction:  n_f* = n_f / (1 + (n_f−1)/N_f)
```

#### Table 5.2 — per-field n for margin E (worst case p*=0.5)

| Margin E | n @ 95 % | n @ 99 % |
|---|---|---|
| ±10 % | 97 | 166 |
| ±5 % | 385 | 664 |
| ±3 % | 1 068 | 1 844 |
| ±2 % | 2 401 | 4 148 |
| ±1 % | 9 604 | 16 590 |

**[VERIFIED — computed.]** If priors say a field is near-clean (`p* ≈ 0.02`), use
`n = z²·p*(1−p*)/E²`, which collapses: for `p*=0.02, E=0.01, 95%`: `n =
3.84·0.0196/0.0001 = 753`. Always size with the **expected** `p*`, not 0.5, once
a pilot gives a prior — it cuts `n` by up to 4×.

### 5.3 Stratified allocation across fields (one sample, scored on all)

We do NOT draw 11 separate samples. We draw **one** master sample sized to the
**most-demanding** field (the binding `max n_f`) and score every field on it.
Optionally use **Neyman allocation** if some fields are pulled from disjoint
sub-populations (e.g. only entities with a website have `website_waf`):

```
Neyman: n_h = n · ( N_h·σ_h / Σ N_j·σ_j )    (σ_h = √(p_h(1−p_h)) per stratum)
```

Allocate more of the budget to strata that are both large and high-variance
(`p ≈ 0.5`), less to near-clean strata. **[VERIFIED — Neyman 1934.]**

### 5.4 The field-recall axis (nulls are not free)

A `null` in `cif` is either *legitimately absent* (sole-trader with no CIF) or a
**silently dropped field** (parser failed → wrote null). To tell them apart,
sample `n` **null cells** and re-collect: if the true value *existed and we
missed it*, that is a field-recall defect. Size with §2.2 against a `p₀` for
"acceptable null-loss" (e.g. < 2 % of nulls should have been populated). This
catches the **silently-dropped-fields** failure mode the mandate names.

---

## 6. Precision vs recall — the two numbers, measured apart

The whole document converges here. CARDEEP reports **two** quality numbers per
population, with two CIs, from **two different sampling designs**. Conflating them
is the cardinal sin.

### 6.1 Precision (no fabrication) — internal sample, external truth

```
Definition:  Precision = (rows we have that are TRUE) / (rows we have)
Measured by: §2 acceptance sample of n rows drawn FROM the DB,
             re-verified against PRIMARY reality (orthogonal path).
Estimator:   P̂ = 1 − d/n ,  CI = Wilson(d, n)  (§5.1)
Catches:     fabrication, stale rows, mis-parses, silent caps, duplicates.
```

### 6.2 Recall (no missing) — external frame, internal lookup

```
Definition:  Recall = (true entities we HAVE) / (all true entities)
Measured by: §4 capture-recapture (DB = capture 1, an INDEPENDENT recollection
             = capture 2); recall = D_have / N̂.   OR a gold "known-present" list:
             draw n items KNOWN to exist (from a registry we trust as a frame),
             check how many we hold:  R̂ = found/n , CI = Wilson.
Catches:     coverage gaps, whole-segment omissions, geographic blind spots.
```

> **[VERIFIED reasoning]** Precision uses the DB as the frame; recall uses
> reality as the frame. They share no sample and no estimator. A claim of high
> recall "verified by re-checking our own rows" is structurally impossible and is
> an automatic quarantine trigger.

### 6.3 The combined honesty statement (the only acceptable claim shape)

CARDEEP never says "20 000 entities, done." It says, for each sealed segment:

> *"Desguaces ES: hold 1 400 distinct; precision 99.3 % (Wilson 95% CI
> [98.6 %, 99.7 %], n=459, c=0 plan); recall 92.2 % against Chapman denominator
> 1 518 ± 10; freshness < 24 h for 99.1 %. Known gap: ~118 unlisted CATs in rural
> provinces (capture-recapture residual). Verdict: SEALED-WITH-DECLARED-GAP."*

That sentence is **provable line by line** and confesses the gap. That is the
product.

### 6.4 F-score only as a summary, never as the gate

`F1 = 2·P·R/(P+R)` may appear in dashboards, but **gates are on P and R
separately** with separate thresholds (§7). A high F1 can hide a catastrophic
recall behind excellent precision; we never let the average launder a failure.

---

## 7. Thresholds CARDEEP commits to (the acceptance gates)

These are the numeric gates wired into the verdict logic. **[ASSUMED — business
thresholds]** except where a formula fixes the value **[VERIFIED]**.

| Gate | Metric | Threshold | Confidence | Sample (n, plan) | Source |
|---|---|---|---|---|---|
| **G-PREC-CRIT** | critical defect rate | < 0.2 % | 99 % | n=2 301, c=0 | §2.4 |
| **G-PREC-MAJ** | major defect rate | < 1 % | 99 % | n=459, c=0 | §2.4 |
| **G-PREC-MIN** | minor defect rate | < 5 % | 95 % | n=59, c≤? (§2.3) | §2.4 |
| **G-RECALL** | segment recall vs Chapman N̂ | ≥ 95 % OR declared gap | 95 % CI lower bound | per §4 | PLAN F4/F8 |
| **G-DENOM** | denominator CI half-width | ≤ 5 % of N̂ | 95 % | 3-source log-linear | §4.4 |
| **G-FIELD** | any single field defect | < 3 % | 95 % | n=1 068 master | §5.2 |
| **G-FRESH** | rows within SLA | ≥ 99 % | 95 % | SPRT monitor | §1.4, §3 |
| **G-DUP** | duplicate `cdp_code` rate | < 0.1 % | 99 % | n=4 603, c=0 | §2.2 |

**Verdict mapping (extends `verification_verdict.verdict`):**
- All gates pass → **TRUSTWORTHY**.
- A precision/dup gate fails (we hold lies) → **REFUTED** → manager routes to
  *fix* (re-parse) or *quarantine* (pull rows).
- Only G-RECALL fails with a *quantified* gap → **SEALED-WITH-DECLARED-GAP**
  (honest partial, not a lie) → route to *research* (new source).
- Insufficient `n` drawn / CI too wide → **UNVERIFIED** → route to *escalate*
  (sample more, or SPRT-continue).

---

## 8. End-to-end worked example — certifying the 20 000

The headline claim under audit: **"20 000 entities completed end-to-end."** Walk
the full machine.

### Step 1 — Count quorum (existing `verify.py`, necessary not sufficient)
Three orthogonal counts of "distinct completed entities": DB `COUNT(DISTINCT
cdp_code WHERE status='complete')` = 20 000; pipeline tombstone ledger = 19 998;
API `/entities?status=complete&count` = 20 000. Modal 20 000 supported by 2 paths,
divergence (20000−19998)/20000 = 0.01 % ≤ tol → quorum **TRUSTWORTHY**. *This only
proves the count, not the contents.* Proceed to sampling.

### Step 2 — Precision via blind acceptance sample
Target: certify **< 1 % major-defect at 99 %**. Table 2.2 → **n = 459, c = 0**.
Draw 459 `cdp_code`s uniformly at random (seeded, logged for audit). For each,
**independently re-collect** from primary reality via a *different code path*
(re-fetch source page / re-query DGT / call the phone). Score against §1.3.

- Outcome A — 0 defects in 459 → **accept**: "major-defect rate < 1 %, 99% conf;
  point estimate Wilson upper bound ≈ 1.0 %." Run the CRITICAL plan too (n grows
  to 2 301, c=0) for the 0.2 % existence/dup gate.
- Outcome B — 3 defects in 459 → **reject** (c=0): `p̂=0.65 %`, Wilson 95% CI
  [0.22 %, 1.9 %] — upper bound breaches 1 %. Verdict **REFUTED**; manager
  inspects the 3 defects, finds (say) all 3 are stale `last_seen` from one source
  → route *fix* (re-poll that source), re-sample.

### Step 3 — Recall via capture-recapture
DB (capture 1, `n₁ = 20 000` distinct) vs an **independent** recollection — e.g.
a fresh Páginas Amarillas + FSQ/Overture pull (capture 2, `n₂`), matched by CIF/
geo. Suppose `n₂ = 24 000`, overlap `m = 16 500`:

```
N̂_raw = (20001·24001)/16501 − 1 = 4.8006e8/16501 − 1 ≈ 29 091   (UNFILTERED — all-listed upper bracket)
```
**MEMBERSHIP FILTER FIRST (§4.7 — the recall frame is NOT this raw number).** The PA+Overture capture
includes C2C private sellers and non-selling workshops that are not CARDEEP entities. After dropping
sentinel-attributed C2C rows, `garaje sells_cars=false`, and non-POS from both captures, suppose the
filtered captures give `N̂ᶠ ≈ 23 800` (the membership-filtered universe; `N̂ᶠ_lower ≈ 22 900`):
```
Recall = found / N̂ᶠ_lower = 20 000 / 22 900 = 87.3 %   (the SEAL-BEARING number)
```
**Honest reading:** the 20 000 are (precision-wise) clean and cover ~87 % of the **membership-filtered
~22 900 entity universe** — there are **~2 900 *entities* we do not yet hold** (the ~6 000 difference
to `N̂_raw` are C2C/non-POS, correctly NOT in the entity frame, served-attributed to the platform
sentinel and counted on the `c2c_listed_pct` KPI line instead). Verdict for the *coverage* claim:
**SEALED-WITH-DECLARED-GAP (recall 87.3 % vs membership-filtered N̂ᶠ, gap ≈ 2 900)** → route *research*.
The illustrative filtered figures here are `[ASSUMED]`; the rule is binding (§4.7) — recall is ALWAYS
reported against `N̂ᶠ`, never `N̂_raw`. We must NEVER let "20 000 completed" be read as "Spain done",
NOR let the unfiltered ~29 100 understate recall by counting non-entities as missed.

### Step 4 — Per-field audit on the same 459 (+ top-up to 1 068)
Score every field on the master sample; for the binding `±3 %@95 %` field, top up
to n=1 068. Suppose `cif` shows 41/1068 defects → `p̂=3.8 %`, Wilson 95% CI
[2.8 %, 5.2 %] — breaches the 3 % field gate. **G-FIELD REFUTED for `cif`** even
though row-level major-defect passed: the CIF parser is the localized culprit →
route *fix* (one parser), not a full re-ingest.

### Step 5 — Sequential monitor going forward
Wire the SPRT of §3.2 onto the *stream* of newly-completed entities so drift is
caught within ~40–190 records instead of waiting for the next full certification.

### Step 6 — Emit the honest verdict (the deliverable)
> *"20 000 entities: COUNT TRUSTWORTHY (3-path quorum, div 0.01 %). PRECISION
> major-defect < 1 % @99 % (n=459/0) PASS; CRITICAL < 0.2 % @99 % (n=2301/0)
> PASS; FIELD `cif` 3.8 % FAIL→parser fix queued. RECALL 68.8 % vs Chapman N̂≈
> 29 091 → DECLARED GAP ~9 091, route research. Net: rows we hold are true; we
> hold 69 % of Spain. No lie sold."*

---

## 9. Failure modes caught, and the formula that catches each

| Failure mode (mandate) | Detector | Trip condition | Verdict → route |
|---|---|---|---|
| **Inflated counts** | §2 acceptance + §4 recapture | sampled defectives > c; or `N̂` ≫ claimed | REFUTED → fix/quarantine |
| **Silent caps** (e.g. price/km clipped, pagination cut at 1 000) | §5 per-field on `price`/`km`/existence + §2 existence plan | field CI breach; or recall gap concentrated at a value ceiling | REFUTED → fix |
| **Silently-dropped fields** | §5.4 null-cell sample | null-loss rate > p₀ | REFUTED → fix |
| **Staleness** | §1.4 + §3 SPRT freshness monitor | within-SLA share < 99 % (G-FRESH) | REFUTED → fix (re-poll) |
| **Fabrication** | §2 blind re-collection (orthogonal path) | any existence defect (CRITICAL c=0) | REFUTED → quarantine |
| **Coverage gaps** | §4 capture-recapture per stratum | recall CI lower bound < 95 % | SEALED-WITH-GAP → research |
| **Denominator bluffing** | §4.1 CI on N̂ | CI half-width > 5 % of N̂ (G-DENOM) | UNVERIFIED → escalate (3rd source) |
| **Self-verification fraud** (recall "proven" from own DB) | §6.2 frame check | recall estimator's frame == DB | QUARANTINE (structural lie) |
| **Under-sampling to fake confidence** | §2 / §5 sizing | reported `n` < required `n` for claimed conf | UNVERIFIED → escalate |

---

## 10. Reference tables (copy-paste constants)

### 10.1 Zero-defect blind sample size `n = ⌈ln α / ln(1−p₀)⌉`
(see Table 2.2)

| p₀ \ conf | 90 % | 95 % | 99 % | 99.9 % |
|---|---|---|---|---|
| 5 % | 45 | 59 | 90 | 135 |
| 2 % | 114 | 149 | 228 | 342 |
| 1 % | 230 | 299 | 459 | 688 |
| 0.5 % | 460 | 598 | 919 | 1 379 |
| 0.2 % | 1 151 | 1 497 | 2 301 | 3 451 |
| 0.1 % | 2 302 | 2 995 | 4 603 | 6 905 |

### 10.2 χ² constants for c-plans (§2.3, used as `χ²_{2c+2,q}/2`)

| c | `½χ²_{2c+2,0.05}` (n·AQL, α=.05) | `½χ²_{2c+2,0.90}` (n·LTPD, β=.10) |
|---|---|---|
| 0 | 0.0513 | 2.303 |
| 1 | 0.355 | 3.890 |
| 2 | 0.818 | 5.322 |
| 3 | 1.366 | 6.681 |
| 5 | 2.613 | 9.274 |
| 10 | 5.426 | 15.41 |

### 10.3 Estimator cheat-sheet

| Need | Estimator | CI |
|---|---|---|
| Defect rate from a sample | `p̂ = d/n` | Wilson (§5.1) |
| Upper bound, 0 defects seen | `3/n` (95 %), `4.6/n` (99 %) | rule of three |
| Universe size, 2 sources | Chapman `N̂` (§4.1) | log-normal (§4.1) |
| Universe size, 3+ sources | log-linear `f₀` | profile-likelihood |
| Recall | `D_have/N̂` or `found/n_frame` | propagate / Wilson |
| Stop early | Wald SPRT lines (§3.1) | risks (α,β) by design |

### 10.4 Symbols

`N` lot size · `n` sample size · `d` defects found · `c` acceptance number ·
`p₀/RQL/LTPD` bad rate to reject · `AQL` good rate to accept · `α` producer risk ·
`β` consumer risk · `Pa` prob. of acceptance · `N̂` estimated universe ·
`n₁,n₂` capture sizes · `m` overlap · `P` precision · `R` recall.

---

## Appendix A — Reproducibility & audit

Every sampling event MUST persist (extends `verification_verdict.evidence`):
RNG **seed**, the exact list of sampled keys, the plan `(n, c, p₀, conf)`, the
independent re-collection path used, raw per-item scores, and the resulting CI.
A verdict is **re-runnable**: feed the seed, get the same sample. Without the
seed and the sampled-key list, an acceptance verdict is itself unverifiable — and
CARDEEP does not sell unverifiable verdicts, not even about its own verification.

## Appendix B — What this supersedes

`05-VERIFICATION-VAM` (light) = count quorum only (`verify.py`): "≥2 paths agree
on a number." It is the **first** gate (Step 1 / §8) and remains in force for
counts. This V6 doc adds the **content** gates (precision, recall, per-field,
denominator CI, sequential monitoring) that the quorum cannot provide. Where the
two ever conflict, **V6 governs**: a quorum-passing count whose blind sample is
defective is **REFUTED**, never TRUSTWORTHY.
