# Feature Design — `price_trap` v2 (model-aware cohort price-anomaly detector)

**Review verdict:** NEEDS-REVISION → **revisions folded in below; now SHIPPABLE** behind the prescribed one-run dry-run review.
**Effort:** M
**Files:** `pipeline/gestionador/detect.py`, `pipeline/gestionador/run.py` (NEW), `pipeline/ops/scheduler.py`, `tests/test_gestionador.py`, `services/api/servable_vehicle` view (zero/tiny bucket — see §Zero-price).
**Migration:** none required for correctness (index dropped per review — see §Data-migration).

---

## 1. Summary & finding closed

Rewrite the DORMANT `detect_price_trap` (`pipeline/gestionador/detect.py:748`, currently emits **0** gestion_items) into a **model-aware, two-sided robust-z price-anomaly detector**. It closes the price-junk half of audit findings **A-junk-sentinel-prices** (the >1M€ monsters: e.g. €10M Nissan Qashqai, €8.5M SEAT Ibiza — both VERIFIED present) and **A-km-year-outliers-adjacent price junk**, plus the **under-100€ available** bucket (11,741 rows, VERIFIED in scope), WITHOUT nulling legit cheap or luxury stock (**Law I**).

**The statistic** is robust z on `ln(price)` per cohort using median + MAD (`1.4826·MAD`), cohort = `(make,model,year)` (Tier-A) with a `(make,year)` fallback (Tier-B) for the ~403k priced-available rows that have make+year but NULL model. MAD (not stddev) because a single 9M outlier inflates stddev and masks its siblings; MAD has ~50% breakdown so junk cannot move the scale.

**Surfacing is QUARANTINE-only** via `gestion_item` — never NULL, never DELETE. The existing `servable_vehicle` view already excludes any vehicle with an open quarantining vehicle-keyed item, so a flag auto-hides the car from served inventory with ZERO write to `vehicle.price`, fully reversible (close the item → car reappears). Release is proof-gated (route.py:243 + trigger 0036 require a TRUSTWORTHY quorum_n≥2 verdict).

### What the review corrected (folded in, not appended)
- **Current state is NOT QUARANTINE-ready.** [VERIFIED] the live detector uses `lane="RESEARCH"` (detect.py ~:818) and a flat kind-median + `[49,999]` monthly band; this rewrite switches the lane to `QUARANTINE` and the statistic to cohort robust-z.
- **Blast radius restated under the rule AS WRITTEN (incl. the 150k floor):** ~**250–300 high + ~17–19k low** (Tier-A low + Tier-B fallback), NOT the plan's original "3,709 high / 19,063 low". The "3,709" figure was computed WITHOUT the 150k floor; the floor kills ~3,046 of those. The corrected high count is ~254 (Tier-A, with floor). See §Acceptance.
- **Performance is ~30s, not <5s.** The covering index is **DROPPED** — the planner seq-scans 1.27M rows regardless (the cohort statistic must read `price+ln(price)` for every priced-available row). 30s is fine for a daily €0 job. See §Performance.
- **Zero-price finding is OUT of this detector's scope** (its `price>0` filter cannot see them; live `price<=0 AND available` = **0 rows** today anyway). Handled separately by a `servable_vehicle` view price-floor predicate. See §Zero-price.
- **`PRICE_TRAP_MAD_FLOOR` raised 1e-6 → 0.05** to neutralize near-degenerate (tight) cohorts that otherwise produce astronomical z for legit cars (Opel Crossland X 2024 z=391, Tesla Model S z=217 — both legit, only the 150k floor accidentally saved the HIGH side; the LOW side was unguarded).
- **Counts refreshed to live reality:** ~8,590 Tier-A cohorts n≥15 (not 11,519); ~403,318 missing-model rows; suite is ~840 tests / `test_gestionador.py` is 744 lines (not "139-test bar").

---

## 2. Files & lines touched

| File:lines | Change |
|---|---|
| `detect.py:87-100` (PRICE_TRAP_* block) | REPLACE. Keep `PRICE_TRAP_FLOOR` (low-side absolute co-guard). ADD: `PRICE_TRAP_COHORT_Z=6.0`, `PRICE_TRAP_COHORT_MIN_A=15`, `PRICE_TRAP_COHORT_MIN_B=30`, `PRICE_TRAP_LOW_MEDIAN_FRAC=0.25`, **`PRICE_TRAP_MAD_FLOOR=0.05`** (was 1e-6 — see §MAD-floor), `PRICE_TRAP_HIGH_ABS_FLOOR=150000.0`, `PRICE_TRAP_MAX_ROWS=5000`. |
| `detect.py:748-824` (`detect_price_trap` body) | REWRITE. Replace kind-median + flat-floor + monthly-band with the cohort CTE (§3). Emit `AnomalyResult(detector='price_trap', subject_type='vehicle', subject_key=vehicle_ulid, lane='QUARANTINE', quarantines=True, severity=...)`. `dedupe_key=f'price_trap|{vid}|{bucket}'`. Pure async DB-only (zero cost). |
| `detect.py:9-21` (status docstring) | Update line ~17: `price_trap` stays LIVE, now cohort-aware two-sided QUARANTINE (was RESEARCH). |
| `pipeline/gestionador/run.py` | **NEW** (does not exist; [VERIFIED] gestionador/ holds only `__init__.py`, `detect.py`, `route.py`). Thin async entrypoint: connect → `detect_price_trap(conn)` → `route.route_anomalies(...)` → close. Exposes `run_price_trap(conn)` + `__main__` CLI. |
| `scheduler.py` (new job fn near `inquisition_cadence_job`; add_job block) | ADD `gestionador_detect_job` on a daily IntervalTrigger calling `run.run_price_trap`. €0 (DB reads + gestion_item upserts). Never raises (log+exit), mirroring `inquisition_cadence_job`. [VERIFIED] scheduler currently has 3 jobs; no gestionador job exists. |
| `services/api` `servable_vehicle` view (migration) | ADD a `price > 0` (or `price >= <floor>`) predicate so the structurally-invisible zero/sub-floor bucket is hidden at the view, per audit:250. See §Zero-price. |
| `tests/test_gestionador.py` | ADD cohort tests (§Verification step 2), incl. the new **tight-cohort-legit-car-not-flagged** regression test (both sides). |

---

## 3. Atom-level approach

**STATISTIC.** Per cohort: `med_lp = median(ln price)`; `mad_lp = median(|ln price − med_lp|)`; `robust_z = (ln price − med_lp)/(1.4826·mad_lp)`. [VERIFIED on live DB]: Audi A4 2008 cohort n=617, med_lp=8.839, mad_lp=0.1911 → 9M junk z=+25.32, legit 16.4k top z=+3.06; SEAT Ibiza 2018 n=649 → 49€ z=−24.73; Ferrari Purosangue 2025 n=26 → 760K z=+2.15 (safe).

**COHORT + MIN-SIZE GUARD.** Tier-A key `make|model|year`, fire only if `n>=15`. Tier-B fallback (make+year present, model NULL) key `make||year`, fire only if `n>=30`. Rows below the guard or with NULL make/year are NOT evaluated (conservative, no false positive). [VERIFIED] ~8,590 Tier-A cohorts n≥15 covering ~1.165M rows; ~403,318 missing-model rows feed the Tier-B fallback.

**MAD-FLOOR (the safety fix).** Skip cohorts with `mad_lp < PRICE_TRAP_MAD_FLOOR` where **`PRICE_TRAP_MAD_FLOOR=0.05`** (≈5% log-price spread). [VERIFIED regression class] at 1e-6, tight cohorts collapse the z denominator and explode z for legit cars: Opel Crossland X 2024 @20,475 vs median 17,999 (a normal 14% premium) → z=391; Tesla Model S 2016 → z=217; Renault Megane E-Tech 2022 → z=198. The 150k abs-floor accidentally masks these on the HIGH side; the LOW side was UNGUARDED. Raising the floor to 0.05 makes near-degenerate cohorts skipped (not amplified) on **both** sides. (Degenerate single-price cohorts are handled by the fabrication degenerate-distribution detector, not here.)

**TWO-SIDED RULE + LAW I.**
- **HIGH:** `robust_z >= +6 AND price >= PRICE_TRAP_HIGH_ABS_FLOOR(150000)`. The abs-floor guarantees a tight mainstream cohort can never push a normal-priced car over the line on spread alone. Severity `critical`, quarantines. [VERIFIED] this catches the real monsters (>1M€ junk) and yields ~254 Tier-A flags — NOT 3,709 (that number omitted the floor).
- **LOW:** `robust_z <= -6 AND price < 0.25·cohort_median_price` (deposit/finance/placeholder shape). The `0.25·median` gate is the Law I protector — [VERIFIED] a Renault Clio 2005 cohort (median 2,200€, gate 550€): 1–13€ rows flag, but a 600€+ runner survives even at negative z. Severity `critical` if `price <= PRICE_TRAP_FLOOR[kind]` (deposit) else `warning`. Quarantines.
- **Luxury safe-by-construction:** high-median cohorts keep legit members at small |z| (760K Purosangue z=2.15), and the HIGH abs-floor is moot because they are not cohort-outliers.

**SURFACING — QUARANTINE only.** Emit via `route.route_anomalies` with `quarantines=True, subject_type='vehicle', subject_key=vehicle_ulid`. [VERIFIED] `servable_vehicle = SELECT ... FROM vehicle v WHERE NOT EXISTS (SELECT 1 FROM gestion_item g WHERE g.quarantines AND g.closed_at IS NULL AND g.subject_type='vehicle' AND g.subject_key=v.vehicle_ulid)`. So an open quarantining item auto-hides the row with ZERO write to `vehicle.price`. Idempotent: `dedupe_key=price_trap|{vid}|{daily_bucket}`; `ON CONFLICT` updates measured/severity only (route.py:115-143). `vehicle_ulid` is text so subject_key matching works.

**EFFICIENT QUERY SHAPE.** Final SQL: (1) base CTE filtered `status='available' AND price>0`; (2) `med` CTE = one GROUP BY cohort computing count, `median(lp)`, `median(price)` with `HAVING count(*) >= $min` (drops most cohorts early); (3) `mad` CTE joins base back to surviving cohorts only and computes `median(|lp−med_lp|)`, filtering `mad_lp >= $mad_floor`; (4) final SELECT applies the two-sided rule, `ORDER BY abs(z) DESC LIMIT $max_rows(5000)`. **Param-bind all constants** (`$1..$n`) — no f-string value interpolation. The whole pass is ~30s (seq scan + 3 percentile sorts) — acceptable for a daily €0 job.

---

## 4. Performance (corrected)

[VERIFIED by reviewer on live DB] **~30s** (33s without index; the EXACT proposed covering index + ANALYZE → 30.3s, planner chose Seq Scan on vehicle 1,272,132 rows and IGNORED the index). Reason: the cohort statistic must read `price+ln(price)` for EVERY priced-available row (double scan + 3 `percentile_cont` sorts); a covering index over ~all of the filtered table gives the planner no win over a seq scan.

**Decision:** **DROP the covering index** (`idx_vehicle_price_cohort`). It ships a blocking `CREATE INDEX` on 1.7M rows that the planner won't use. There is no other access path that benefits it for this workload. 30s is fine: this is a daily €0 cadence job (DB reads only), NOT in the ingest hot path.

The original plan's acceptance criterion "Execution Time < 5s" is **DELETED**. New criterion: Execution Time < 60s (typically ~30s).

---

## 5. Zero-price bucket (out of detector scope — handled at the view)

The audit's headline **A-zero-and-tiny-prices** finding (2,678 @ 0€ in the audit) is NOT addressed by this detector: (a) live DB shows `price<=0 AND status='available'` = **0 rows** today (VERIFIED), and (b) the detector's base CTE filters `price>0` (and `ln(0)` is undefined), so zero/negative prices are **structurally invisible** to it. Per the audit's own suggestion (`docs/recon/AUDIT_2026-06-15_PHASE2.md:250`), the zero/sub-floor bucket is handled by a **price-floor predicate in the `servable_vehicle` view** (e.g. `AND v.price > 0`), which is migration-only and independent of this detector. The under-100€ bucket (11,741 rows) IS in scope via the LOW side. Do NOT claim this detector closes the zero-price finding.

---

## 6. Data-migration & backfill (exact SQL)

**No row backfill of vehicle data. The covering index is DROPPED (planner won't use it).** The only schema touch is the optional `servable_vehicle` view price-floor predicate for the zero/tiny bucket (§5), shipped as the next migration after 0038:

```sql
-- migrations/00NN_servable_price_floor.sql  (one transaction; migrate.py strip_rollback format)
-- Hide zero/non-positive priced rows at the served surface (audit A-zero-and-tiny-prices).
-- The price_trap detector cannot see price<=0 (its base CTE is price>0); this is the
-- complementary view-level guard suggested at AUDIT_2026-06-15_PHASE2.md:250.
CREATE OR REPLACE VIEW servable_vehicle AS
  SELECT v.*
    FROM vehicle v
   WHERE v.status = 'available'
     AND v.price IS NOT NULL
     AND v.price > 0                         -- NEW zero/tiny guard
     AND NOT EXISTS (
       SELECT 1 FROM gestion_item g
        WHERE g.quarantines AND g.closed_at IS NULL
          AND g.subject_type = 'vehicle' AND g.subject_key = v.vehicle_ulid);
-- Rollback:
-- CREATE OR REPLACE VIEW servable_vehicle AS <prior definition without the price>0 line>;
```
> NOTE: copy the EXACT prior `servable_vehicle` definition before editing so the rollback is byte-faithful and no served column drifts. If the price>0 guard is judged out of scope for this feature, omit this migration entirely — the detector ships with no migration at all.

**Flags backfill:** none needed. The detector, on first cadence run, INSERTs the ~250–300 high + ~17–19k low flags idempotently. For immediate effect run `python -m pipeline.gestionador.run` once after deploy, **gated behind the one-run dry-run review** (§Risks #1).

---

## 7. Verification commands & acceptance criteria

1. **Unit** (`pytest tests/test_gestionador.py -k price_trap -q`):
   - high-junk row (cohort-implausible, `price>=150k`) → `AnomalyResult side='high' quarantines=True`;
   - legit-luxury row (large cohort, near-median) → none;
   - low-deposit row (`z<=-6 AND price<0.25*median`) → `side='low' quarantines=True`;
   - legit-cheap row above `0.25*median` → none;
   - cohort `n<15` → none;
   - **tight-cohort legit car (small absolute deviation, `price<150k`, `mad_lp<0.05`) → NOT flagged on EITHER side** (the MAD-floor regression test);
   - same input twice → identical `dedupe_key` (idempotent). Keep the suite green (~840 tests).
2. **Dry-run vs live DB (no writes):** add a count to `dry_run_all`; **ACCEPTANCE: high ≈ 250–300, low ≈ 17–19k** (Tier-A low + Tier-B fallback) under the rule AS WRITTEN incl. the 150k floor and `MAD_FLOOR=0.05`. (NOT the old 3,709/19,063.)
3. **Law I regression queries:** (a) Ferrari Purosangue 2025 760K `robust_z=2.15 < 6` → absent; (b) no flagged LOW row has `price >= 0.25*cohort_median`, no flagged HIGH row has `price < 150000`; (c) after a run: `count(available with open quarantining price_trap item) == count of those items`; `count(vehicle WHERE price IS NULL)` unchanged (we never NULL).
4. **Surfacing proof:** pick one flagged `vehicle_ulid` → present in `vehicle`, ABSENT from `servable_vehicle`, `vehicle.price` unchanged.
5. **Idempotency (intra-day):** run the runner twice in the same UTC day → `count(gestion_item WHERE detector='price_trap')` stable.
6. **Cross-day non-idempotency (explicit):** a still-anomalous car opens a NEW item per calendar day (`dedupe_key` includes `daily_bucket`); yesterday's stays open until its 48h QUARANTINE SLA (route.py LANE_SLA). So `gestion_item` for `price_trap` accumulates up to ~2 days of overlap per persistently-bad car. This is acceptable and documented — NOT a defect.
7. **Performance:** EXPLAIN ANALYZE the detector SQL → Execution Time < 60s (~30s typical). No index dependency.

---

## 8. Risks (incl. reviewer's missed risks)

1. **REGRESSION-CLASS (servable surface):** quarantining hides cars from served inventory. Mitigation: `|z|>=6`, HIGH abs-floor 150k, LOW 0.25·median gate, `MAD_FLOOR=0.05`, `LIMIT 5000/run`. Blast radius ~1.35% and every inspected sample was real junk. **Ship behind a one-run dry-run review of the flagged set before enabling the cadence job.**
2. **REGRESSION-CLASS / Law-I time-bomb (reviewer's PRIMARY miss):** the original plan's acceptance number (3,709 high) silently assumed NO 150k floor. An engineer "fixing" the dry-run mismatch by removing the floor would quarantine ~3,046+ legit mainstream cars (Opel/Tesla/Megane) → shrink served stock → direct "sacarle TODO su stock" violation. Mitigation: the acceptance number here is restated UNDER the floor (~254 high); the floor is load-bearing and must NOT be removed; the MAD-floor test guards the same pathology.
3. **REGRESSION-CLASS (near-degenerate-MAD amplification):** neutralized by `MAD_FLOOR=0.05` on both sides + the tight-cohort regression test.
4. **Law I (nulling legit data):** the detector NEVER writes `vehicle.price` and NEVER deletes; only a reversible quarantine item. Release is proof-gated (route.py:243 + trigger 0036, TRUSTWORTHY quorum_n≥2). Wrongly-quarantined car recovers by closing the item (rollback SQL below).
5. **Cohort mislabeling from upstream parse junk:** ~rows with make+model NULL are NOT evaluated; Tier-B fires only at n>=30. A polluted cohort's median is bounded by MAD's 50% breakdown + the abs-floors.
6. **High side oversold 14×:** the genuine value is ~254 high (the real >1M€ monsters ARE caught); reviewers must not under-scrutinize the value/risk boundary thinking it's 3,709.
7. **No scheduler/source_health/AS24 regression:** this adds a NEW job id (`gestionador_detect_job`); it does NOT touch SourceEntry, `_due_sources`, `source_health`, or any connector `source_key` (avoids the autocasion-orphan and AS24 scars). Additive, never raises.

---

## 9. Rollback

- **Flags:** `UPDATE gestion_item SET state='WONT_FIX', closed_at=now(), closed_reason='rollback price_trap v2' WHERE detector='price_trap' AND closed_at IS NULL;` (reversible — re-shows quarantined cars).
- **Detector:** revert `detect.py` to the RESEARCH-lane flat-floor version (git revert the rewrite commit).
- **Scheduler job:** remove the `gestionador_detect_job` add_job block.
- **View (if shipped):** restore the prior `servable_vehicle` definition (byte-faithful copy taken before edit).
