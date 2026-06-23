# Confianza y Certificacion — Turn CARDEEP's coverage claims into court-grade, reproducible statistical proof that no human or institution can match.

> This domain OWNS the question "how complete is the census, and can you prove it?". It runs two parallel, live, queryable certification mechanisms over the Spanish digital point-of-sale census: the **registral seal** (`v_province_seal`, served at `/geo/seal`) which contrasts the deduplicated served numerator against the DIRCE CNAE-451 / DGT ceilings per province×segment, and the **statistical exhaustiveness seal** (`v_exhaustiveness_seal`, served at `/geo/exhaustiveness`) which runs multi-list capture-recapture (Chapman / Fienberg log-linear with BIC interaction selection / dependence-robust partial-identification bound, plus an R cross-check via `Rcapture`/`LCMCR`) to estimate the *unseen* universe and certify a conservative lower-bound coverage. It is the domain that converts CARDEEP from "we found a lot of dealers" into "we have proven, with a 95% CI and an independent external anchor, that we have captured X% of everything that exists online". Every figure it publishes carries the anti-maquillaje doctrine baked into code: only strata whose overlap *pins N down* enter the certified denominator; everything else is reported as observed-floor-only, never inflated to 100%.

## Current state (verified)

All figures below were verified by reading the live source under `C:\Users\elias\projects\cardeep` on 2026-06-23, not assumed.

**Registral seal (`v_province_seal`, `migrations/0042_province_seal_view.sql` + `0043_province_seal_desguace.sql`, served live at `/geo/seal`):**
- VENTA segment: **14/52 provinces SEALED (>=85%), 32 PARCIAL (50-85%), 6 GAP (<50%)** — GAP codes 05, 16, 21, 35, 51, 52. Source: `SELECT verdict, count(*) FROM v_province_seal WHERE segment='venta' GROUP BY verdict`.
- National VENTA coverage (served canonical / DIRCE-451): **80.6% = 18,318 / 22,720**. Source: `SELECT sum(numerator), sum(denominator) FROM v_province_seal WHERE segment='venta'`.
- DESGUACE segment: **52/52 SEALED (215.6% = 2,785 / 1,292 DGT census)**. Source: same query, `segment='desguace'`.
- The view is recomputed live on every read (GROUP BY over `entity` + dedup join), `RATE_EXPENSIVE` + cached, authenticated. The frontend (`web/src/lib/seal.ts`) consumes it in real time with no static snapshot (verified: `services/api/routers/geo.py` line 92-114, `geo_seal` reads `FROM v_province_seal ORDER BY segment, province_code`).

**Statistical exhaustiveness seal (MSE) — the harder, more honest mechanism:**
- Active build: **`fase9-audit-20260623`** (2026-06-23T05:19:19Z). `v_exhaustiveness_seal` always points to the most recent build by `created_at DESC` (verified: `migrations/0048_discovery_capture.sql` lines 82-106).
- National N̂ (stratified sum) = **15,560, CI95 [13,509, 17,611]**; certified lower-bound coverage = **37.72%**; national sealed at 0.95 = **FALSE**.
- Only **12/208 strata sealed** (all small province×segment strata with total overlap — desguace/concesionario in low-density provinces). The dominant **compraventa segment averages ~12% lower-bound coverage**: the estimator correctly detects the real universe is far larger than what orthogonal lists have jointly observed.
- National MSE numerator (identified, MKT excluded) = **6,642 entities**.

**Engine maturity (verified by reading code — far more advanced than a greenfield):**
- `pipeline/exhaustiveness/estimators.py`: pure-Python, zero-DB, textbook-tested. Implements Chapman + Seber-variance + non-parametric bootstrap CI (2-list floor), Fienberg log-linear Poisson-GLM MSE with greedy BIC pairwise-interaction selection + delta-method CI (K>=3), and `dependence_robust_bound` (partial-identification ceiling over the model class). `IDENT_CAP=5.0` enforces that a stratum is only "identified" if N̂ <= 5×n_obs (coverage floor >= 20%); below that it is flagged unidentified and **excluded from the certified denominator** (anti-maquillaje in code, `_mark_identified`).
- `pipeline/exhaustiveness/seal.py`: stratified roll-up that splits CERTIFIED (identified strata, real N̂) from UNCERTIFIED (denominator unknown — **NOT** folded in as covered). Seals on `coverage_lower = n_obs / ci_high`, never on the point estimate.
- `pipeline/exhaustiveness/splink_merge.py` (§V6): **Splink IS already integrated** — Fellegi-Sunter probabilistic linkage on name/municipality/phone/website (DuckDB backend), UNION-ed with the deterministic `v_dealer_resolved` so the capture unit is never *finer* than resolved (which would lower overlap). Writes `discovery_splink_cluster` (migration `0049`), consumed by `capture.build(unit="splink")`. Optional dependency: falls back to deterministic resolved unit if `splink` is absent (it is NOT declared in `requirements.txt` — verified).
- `pipeline/exhaustiveness/estimators_r.py` + `r/mse.R`: R bridge to `Rcapture::closedpMS.t` (BIC log-linear) + `LCMCR` (Bayesian latent), invoked only when `r_crosscheck=True` and K>=3; result attached to stratum diagnostics.
- `pipeline/exhaustiveness/triangulation.py`: external-census seam, wired. Loads `countries/ES/census/dirce_cnae451.csv` (verified present, 2,901 bytes), contrasts N̂ vs n_external, verdict `consistent` iff 0.7 <= ratio <= 1.4. Returns `{}` (graceful "pending") if CSV absent — no fabricated figures.
- `pipeline/exhaustiveness/cli.py`: end-to-end runner `python -m pipeline.exhaustiveness.cli run --run-id X --threshold 0.95 --unit splink`.
- Tests: `tests/test_province_seal_view.py`, `test_exhaustiveness.py`, `test_api_seal.py`, `test_api_exhaustiveness.py` (estimators validated against textbook values).

**Reproducibility / provenance gap (verified ABSENT):** No `dvc.yaml`/`.dvc`, no OpenLineage/Marquez instrumentation, no Great Expectations suite anywhere in the repo (`grep -rl "great_expectations|openlineage|marquez"` → empty). The seal is currently an *assertion backed by re-runnable code*, not a *cryptographically reproducible, lineage-traced artifact*. This is the single largest credibility gap.

**Serving / safety convention (verified, load-bearing):** `:5433` = the **live served census** (`postgres://cardeep@localhost:5433/cardeep`, postgres:16, REPEATABLE READ, ingesting live — NEVER mutate without dry-run + golden + Ferrari + CI). `:5434` = the **ephemeral dry-run docker** for verification (migrate-from-zero, no live data). The `PROGRESO.md` record documents a real incident where tests hardcoding `:5433` passed falsely against live data — all verification of served-data changes MUST run against a fresh `:5434`.

## Next-level objective

Take this domain from "an honest 37.72% certified national lower-bound on compraventa-dominated strata" to **a certified national lower-bound coverage >= 80% across all segments, with every published figure carrying (a) a 95% CI, (b) an agreeing independent external anchor (DIRCE/DGT/FACONAUTO), and (c) a content-addressed, lineage-traced provenance record that any third party can re-execute byte-for-byte to reproduce the exact seal.** Concretely and measurably:

1. **Identification rate:** lift sealed strata from **12/208 → >=120/208**, by (a) adding >=2 net new orthogonal capture lists for the compraventa segment and (b) recovering split overlaps via Splink so sparse-overlap strata become identified. Target: compraventa lower-bound coverage **12% → >=70%**.
2. **Certified national lower-bound coverage:** **37.72% → >=80%**, with national `sealed=TRUE` at threshold 0.90 (and reported at 0.95).
3. **External agreement:** every certified national/segment N̂ has a triangulation verdict of `consistent` (0.7 <= N̂/n_external <= 1.4) against the loaded DIRCE/DGT/FACONAUTO anchors — currently the concesionario national stratum has `external_ref=5,358 FACONAUTO` but `coverage_lower=0.0` because no national concesionario stratum is identified; close that.
4. **Reproducibility:** 100% of published seal figures are emitted with a DVC-locked, OpenLineage-traced provenance bundle whose inputs/outputs are SHA-256 content-addressed; `dvc repro` reproduces the active build's `exhaustiveness_estimate` rows bit-identically.

The bar: no national statistics office or commercial data vendor publishes a per-stratum capture-recapture seal with a partial-identification honesty floor, an external anchor, AND a one-command reproducible provenance bundle. That combination is the moat.

## Chosen technology (EUR0)

All EUR0, all reversible, chosen against the verified current state (not greenfield — several research candidates are already in the codebase).

| Tool | Why (vs current state) | Source / URL | Integration effort |
|---|---|---|---|
| **Splink (MoJ UK)** — *already integrated* | Probabilistic Fellegi-Sunter linkage recovers cross-source overlaps the deterministic dedup splits → tightens N̂ CI and turns unidentified strata identified. `splink_merge.py` + `0049` exist; gap is it is NOT in `requirements.txt` and not run in the default build. | https://github.com/moj-analytical-services/splink (MIT, 2.2k★, daily-active) | LOW — declare `splink` + `duckdb` + `pandas` in `requirements.txt`, make `--unit splink` the default build path, verify on `:5434`. |
| **Rcapture + dga + SparseMSE (R/CRAN)** — *partially wired* | `estimators_r.py` already bridges `Rcapture`/`LCMCR`. Add `dga` (Bayesian model averaging → full posterior of N, not just point+CI) and `SparseMSE` (handles zero-intersection cells that break Lincoln-Petersen) for the sparse compraventa strata. Gold standard used by US Census / UK ONS / HRDAG. | https://cran.r-project.org/package=Rcapture / package=dga / package=SparseMSE (GPL) | MEDIUM — extend `r/mse.R`, gate behind `r_crosscheck=True`, attach posterior to diagnostics. Pure cross-check, never the primary certified figure. |
| **DVC (Data Version Control)** — *ABSENT, highest-value add* | Converts the seal from re-runnable code into a `dvc repro`-reproducible artifact with SHA-256 hashes committed to Git. Reproducibility is a *necessary condition* for the seal's epistemic value. | https://github.com/iterative/dvc (Apache-2.0, 15.7k★) | MEDIUM — author `dvc.yaml` DAG (capture → estimate → seal), local cache only (no remote, EUR0). |
| **OpenLineage + Marquez** — *ABSENT* | Standardised lineage events (RunEvent/DatasetEvent) so each seal records *which inputs, which code version, which hashes, at what UTC time* produced it. Industry standard, self-hostable, no cloud. | https://github.com/OpenLineage/OpenLineage + https://github.com/MarquezProject/marquez (Apache-2.0) | MEDIUM — emit OpenLineage events from `cli.py`; Marquez runs in local docker for inspection (optional, dev-only). |
| **Great Expectations** — *ABSENT* | Turns the seal's invariants (52 provinces present, no over-counting, `coverage_lower = n_obs/ci_high`, MKT excluded, every certified stratum identified) into declarative PASS/FAIL assertions with an immutable, timestamped HTML Data Doc as audit evidence. | https://github.com/great-expectations/great_expectations (Apache-2.0, 11.6k★) | LOW-MEDIUM — one expectation suite over `exhaustiveness_estimate` + `v_province_seal`, run in CI. |
| **iNEXT (Anne Chao, R/CRAN)** — optional cross-check | Coverage-based rarefaction/extrapolation (Chao1 on singletons/doubletons) as a *third* independent estimate of total richness, sanity-checking the log-linear N̂. Same family the US Census uses for undercoverage. | https://github.com/AnneChao/iNEXT (CRAN, MEE 2016) | LOW — add to `r/mse.R` as a diagnostic-only cross-check. |

Rationale for routing: Splink + DVC + Great Expectations are the priority because Splink directly attacks the 12% compraventa identification gap and DVC+GX close the absent-reproducibility gap. Rcapture/dga/SparseMSE/iNEXT are cross-checks that harden trust but do not move coverage on their own.

## Target architecture

**Components and data flow:**

```
                            ORTHOGONAL LISTS (lists.py taxonomy)
   GEO(OSM/Overture/geo_sweep) · CENSUS(autocasion) · DGT · ASSOC(AEDRA/AECS)
   OEM · DORK(municipal) · REG(BORME)   [MKT/GRAPH/COLLAPSE excluded — dependent]
                                   │
                                   ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ capture.build(unit="splink")                                   │
   │   v_dealer_resolved ∪ discovery_splink_cluster  → capture unit │  ← Splink (default)
   │   → discovery_capture (resolved_ulid × list_key, per stratum)  │
   └──────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ estimators.estimate_stratum (per province×segment)            │
   │   K>=3 → loglinear_mse (BIC) widened by dependence_robust_bound│
   │   K==2 → chapman bootstrap (floor)                             │
   │   K<2  → observed-only, confidence=none, identified=False      │
   │   _mark_identified: N̂ <= IDENT_CAP·n_obs else uncertified     │
   │   [optional] estimators_r: Rcapture/dga/LCMCR/iNEXT crosscheck │
   └──────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ seal.compute → stratified roll-up                             │
   │   CERTIFIED = Σ N̂ over identified strata (variances add)      │
   │   UNCERTIFIED reported separately (denom unknown, NOT covered) │
   │   triangulation vs dirce_cnae451.csv → consistent/high/low    │
   │   persist → exhaustiveness_estimate (build_run_id)            │
   └──────────────────────────────────────────────────────────────┘
                                   │
            ┌──────────────────────┼───────────────────────┐
            ▼                      ▼                       ▼
   v_exhaustiveness_seal   Great Expectations      DVC lock + OpenLineage
   (latest build)          (invariant PASS/FAIL    (SHA-256 provenance
            │               + HTML Data Doc)        bundle, `dvc repro`)
            ▼
   /geo/exhaustiveness  +  /geo/seal   (RATE_EXPENSIVE, cached, authed)
            ▼
   web/src/lib/seal.ts (live, no static snapshot)
```

**Data contracts (formalised as GX expectations):** every certified row in `exhaustiveness_estimate` MUST satisfy `coverage_lower = n_obs / ci_high`; `sealed` iff `identified AND coverage_lower >= threshold`; the national row (`province_code IS NULL AND segment IS NULL`) MUST equal the stratified sum of identified strata; MKT excluded from the orthogonal set; exactly 52 provinces × active segments represented; no numerator exceeds its registral ceiling without an explicit over-coverage flag (desguace 215.6% is a known, documented legitimate case).

## Execution phases

Each phase is ~1 PR, additive + reversible, verified against ephemeral `:5434` before any touch to served data. **The MSE persistence writes to `exhaustiveness_estimate` keyed by a NEW `build_run_id`** — it never mutates the active build, so it is additive by construction (the live view points at the latest by `created_at`; a bad build is reverted by deleting its rows, restoring the prior latest).

### Phase 1 — Make Splink the default capture unit (attack the identification gap)

**Cold-start context:** Splink is fully implemented in `pipeline/exhaustiveness/splink_merge.py` and its table exists (`migrations/0049_discovery_splink_cluster.sql`), but `splink`/`duckdb`/`pandas` are NOT in `requirements.txt` (verified) so `splink_available()` returns False in CI and the build silently falls back to the deterministic resolved unit, which leaves cross-source duplicates split → low overlap → sparse strata flagged unidentified. Capture supports `unit="splink"` already (verified in `splink_merge.py` docstring + `capture.build(unit=...)`).

**Tasks:**
1. Add `splink`, `duckdb`, `pandas` to `requirements.txt` (pinned). Verify `splink_available()` → True.
2. Run `python -m pipeline.exhaustiveness.splink_merge` against a **fresh `:5434`** loaded from a dump of the served schema; record `net_extra_merges_vs_resolved` and `splink_pairs_collapsed`.
3. Run the full seal with `--unit splink --run-id splink-eval-<date>` on `:5434`; compare `n_strata_identified` and `national_certified.coverage_lower` against the resolved-only baseline.
4. If identification improves and triangulation verdict stays `consistent`, make `--unit splink` the default in `cli.py`.

**Verification commands:**
```
docker compose -f docker-compose.yml up -d            # :5433 reproduction → use a :5434 ephemeral clone, NEVER mutate :5433
python -c "from pipeline.exhaustiveness.splink_merge import splink_available; print(splink_available())"
DSN=postgres://cardeep@localhost:5434/cardeep python -m pipeline.exhaustiveness.cli run --run-id splink-eval-$(date +%Y%m%d) --threshold 0.95 --unit splink
pytest tests/test_exhaustiveness.py -q
```

**Exit criteria:** `n_strata_identified` strictly increases vs resolved baseline; no certified stratum's triangulation flips to `n_hat_high`; all estimator unit tests green. **Rollback:** revert `requirements.txt`; delete the `splink-eval-*` rows (`DELETE FROM exhaustiveness_estimate WHERE build_run_id LIKE 'splink-eval-%'`); default reverts to resolved.

### Phase 2 — Add >=2 net new orthogonal lists for compraventa (move coverage, not just identification)

**Cold-start context:** the orthogonal-list taxonomy lives in `pipeline/exhaustiveness/lists.py` (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG; MKT/GRAPH/COLLAPSE excluded for dependence). Coverage on compraventa is ~12% because the existing lists are too correlated / too few to pin the large compraventa universe. New lists must be **independent of existing capture mechanisms** (digital-footprint only, per the EUR0 + digital-only mandate) — e.g. additional municipal DORK strata, a BORME/REG widening, or a new OEM dealer-locator source. **Depends on `discovery` and `identity` to actually produce the new source rows in `entity_source`/`entity`.**

**Tasks:**
1. With the discovery domain, identify >=2 EUR0 digital sources orthogonal to current lists; register them in `lists.py` with the correct taxonomy bucket.
2. Re-run `capture.build` on `:5434` so the new `list_key`s appear in `discovery_capture`.
3. Re-seal; measure compraventa `coverage_lower` lift and national lower-bound.
4. Verify the new lists do NOT introduce dependence that biases N̂ low (BIC interaction selection should absorb correlation; triangulation must stay `consistent`).

**Verification commands:**
```
DSN=postgres://cardeep@localhost:5434/cardeep python -m pipeline.exhaustiveness.cli run --run-id newlists-$(date +%Y%m%d) --unit splink
# inspect per-segment lower bound:
psql postgres://cardeep@localhost:5434/cardeep -c "SELECT segment, coverage_lower, sealed FROM exhaustiveness_estimate WHERE build_run_id='newlists-...' AND province_code IS NULL"
```

**Exit criteria:** compraventa national `coverage_lower` increases materially toward the >=70% target; national triangulation verdict remains `consistent`. **Rollback:** delete the new `list_key`s from `lists.py` and the build's rows; prior build remains the served latest.

### Phase 3 — Bayesian + sparse cross-checks (Rcapture/dga/SparseMSE/iNEXT)

**Cold-start context:** `estimators_r.py` + `r/mse.R` already bridge `Rcapture`/`LCMCR`, invoked only when `r_crosscheck=True` and K>=3 (verified `seal.py` lines 78-81). The remaining sparse-overlap strata (where two lists never co-observe a dealer → zero intersection cell) break the frequentist log-linear fit; `SparseMSE` and `dga` (posterior of N) handle exactly this.

**Tasks:**
1. Extend `r/mse.R` to call `dga` (Bayesian model averaging, full posterior) and `SparseMSE` for K>=3 sparse strata, plus `iNEXT` Chao1 as a richness sanity check.
2. Attach posterior interval + iNEXT estimate to stratum `diagnostics`; surface in `/geo/exhaustiveness` as a cross-check field (never overrides the primary certified figure).
3. Flag any stratum where the Bayesian posterior and the frequentist CI disagree by >30% for analyst review.

**Verification commands:**
```
Rscript r/mse.R --selftest          # textbook validation of dga/SparseMSE/iNEXT
DSN=...:5434 python -m pipeline.exhaustiveness.cli run --run-id rxcheck-... --unit splink   # with r_crosscheck wired on
pytest tests/test_exhaustiveness.py -q
```

**Exit criteria:** R cross-check runs on all identified K>=3 strata without aborting the build; disagreements are flagged, not hidden. **Rollback:** R cross-check is gated behind `r_crosscheck`; disabling the flag fully reverts (Python path is independent — verified zero-DB/zero-R estimators).

### Phase 4 — Great Expectations: invariants as executable, audited assertions

**Cold-start context:** No GX suite exists (verified absent). The seal's invariants currently live in pytest (`test_province_seal_view.py`, `test_exhaustiveness.py`) but are not emitted as a portable, timestamped audit artifact.

**Tasks:**
1. Author one GX expectation suite over `v_province_seal` and `exhaustiveness_estimate`: 52 provinces present per active segment; `coverage_lower` computed correctly; national row = stratified sum of identified; no MKT in orthogonal set; certified ⇒ identified; numerator <= ceiling except flagged over-coverage.
2. Run it in CI against a fresh-migrated `:5434`; emit the HTML Data Doc as a CI artifact.
3. Fail CI on any CRITICAL expectation breach.

**Verification commands:**
```
great_expectations checkpoint run cardeep_seal     # against :5434
ls great_expectations/uncommitted/data_docs/        # HTML evidence artifact present
```

**Exit criteria:** suite green on the active build; Data Doc generated and attached in CI. **Rollback:** GX is read-only verification — removing the checkpoint step changes no served data.

### Phase 5 — DVC + OpenLineage: byte-reproducible, lineage-traced provenance

**Cold-start context:** No DVC/lineage (verified absent). This is the credibility capstone: a third party must be able to reproduce the exact `exhaustiveness_estimate` rows.

**Tasks:**
1. Author `dvc.yaml` DAG: `capture` → `estimate` → `seal`, with `deps` = input snapshots + code, `outs` = the build's estimate dump (SHA-256 in `dvc.lock`, committed to Git). Local cache only (EUR0, no remote).
2. Instrument `cli.py` to emit OpenLineage RunEvents (inputs, outputs, code git-SHA, UTC timestamp); optional local Marquez for inspection.
3. Add a `--prove` mode that, given a `build_run_id`, re-runs `dvc repro` and asserts the regenerated dump hashes match the stored lock.

**Verification commands:**
```
dvc repro                                            # reproduces the active build on :5434
dvc status                                           # clean = reproducible
python -m pipeline.exhaustiveness.cli prove --run-id <active>   # hash-match assertion
```

**Exit criteria:** `dvc repro` reproduces the active build's estimate dump bit-identically; `dvc status` clean; lineage events emitted. **Rollback:** DVC/lineage are additive metadata over an existing deterministic pipeline (same `run-id` ⇒ idempotent, per `plans/P-recluster-overture-mse.md` line 79) — deleting `dvc.yaml`/lock and the lineage emit changes no served data.

### Phase 6 — Promote the best build to served + close concesionario national anchor

**Cold-start context:** `v_exhaustiveness_seal` serves the latest build by `created_at` (verified). Promotion = inserting a new, better build whose rows become the latest. The concesionario national stratum has `external_ref=5,358 (FACONAUTO)` but `coverage_lower=0.0` because no national concesionario stratum is identified — fixing identification (Phases 1-3) should close this.

**Tasks:**
1. After Phases 1-3, run the final build with the chosen unit/lists/threshold against a **fresh `:5434`**, then — only after golden + Ferrari + CI green — apply via the normal deploy chain to `:5433` (never a direct manual write; per `PROGRESO.md` line 1812, migrations are applied by CI fresh-build/deploy, not by hand on live).
2. Verify `/geo/exhaustiveness` and `/geo/seal` return the new build; verify the frontend map updates live.
3. Confirm concesionario national triangulation verdict is `consistent` against FACONAUTO 5,358.

**Verification commands:**
```
# DRY-RUN on :5434 first (mandatory):
DSN=...:5434 python -m pipeline.exhaustiveness.cli run --run-id fase10-<date> --unit splink --threshold 0.95
make golden && make ferrari      # golden + Ferrari gates before any :5433 touch
# served check (read-only):
curl -s localhost:8000/geo/exhaustiveness | jq '.build_run_id, .national_certified.coverage_lower, .national_certified.sealed'
```

**Exit criteria:** served national `coverage_lower >= 0.80`, `sealed=TRUE` at 0.90; concesionario national verdict `consistent`; zero regressions in golden/Ferrari/CI. **Rollback:** delete the new build's rows from `exhaustiveness_estimate` on `:5433` → `v_exhaustiveness_seal` reverts to the prior latest by `created_at` (additive-by-construction, no served-data loss).

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Splink over-merges distinct dealers → N̂ biased low → false-high coverage (maquillaje) | CRITICAL | Splink is UNION-ed with `v_dealer_resolved` so the unit is never finer than resolved (verified `splink_merge.py` lines 198-219); `match_threshold=0.9`; triangulation `n_hat_low` verdict catches under-counting; dry-run on `:5434` and compare against resolved baseline before defaulting. |
| New orthogonal lists are correlated with existing ones → dependence biases N̂ low | HIGH | BIC interaction selection in `loglinear_mse` absorbs pairwise dependence into wider CI (verified); `dependence_robust_bound` provides the honest ceiling; triangulation gate must stay `consistent`. |
| Accidental mutation of the live `:5433` served census | CRITICAL | Hard rule: all verification on ephemeral `:5434`; migrations applied only by CI fresh-build/deploy chain, never manual on `:5433` (per `PROGRESO.md` 1812); golden+Ferrari+CI gate before any served touch. |
| Tests passing falsely by leaking onto live `:5433` (documented past incident) | HIGH | Run the seal/verify suite against a **fresh-migrated `:5434`**; never hardcode `5433` in tests (root-cause of the past false-pass, `PROGRESO.md` 3527-3542). |
| R cross-check unavailable in CI (no R toolchain) | MEDIUM | R path is gated behind `r_crosscheck=True` and K>=3; the pure-Python estimators are the primary certified figure and are zero-R/zero-DB (verified); R is cross-check only. |
| External census drift (DIRCE/DGT/FACONAUTO figures stale) | MEDIUM | `triangulation.status()` reports anchor count + path; CSV is versioned in `countries/ES/census/`; never fabricate anchors (returns `{}` when absent — verified). |

## Success metrics

- **Certified national lower-bound coverage:** 37.72% → **>=80%** (`exhaustiveness_estimate` national row, `coverage_lower`).
- **Sealed strata:** 12/208 → **>=120/208**.
- **Compraventa segment lower-bound:** ~12% → **>=70%**.
- **National `sealed`:** FALSE → **TRUE at threshold 0.90** (reported also at 0.95).
- **External agreement:** 100% of certified national/segment N̂ with triangulation verdict `consistent`; concesionario national verdict `consistent` vs FACONAUTO 5,358.
- **Reproducibility:** `dvc repro` reproduces the active build's `exhaustiveness_estimate` dump **bit-identically**; `dvc status` clean; GX suite green with HTML Data Doc artifact in CI.
- **Zero regressions:** golden + Ferrari + full CI green on every promotion to `:5433`; registral seal VENTA national coverage never decreases below 80.6% and DESGUACE stays 52/52.
