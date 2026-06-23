# Calidad y Verdad del Dato — One canonical truth for every served census number

> This domain owns the *correctness contract* of the CARDEEP census: the single, defensible definition of what counts as a "sale point" (punto de venta de coches), the validation gates that stop corrupt data from reaching served views, and the continuous detection of silent data rot (stale scrapers, sentinel prices, ghost shells, deduplication leakage). It does not discover, extract, geocode, or resolve identity — it *audits and certifies* the output of those domains and is the final arbiter of which numbers the product is allowed to publish. It matters because a census whose headline number swung from 54,607 to 19,144 has already proven that an undisciplined definition is the difference between a credible national registry and noise. Scope is strictly DIGITAL footprint: we certify what exists online; absence of a web platform is correctly modeled as "not in scope", never as a quality defect.

## Current state (verified)

All figures below are from the RECON payload, each tagged with the direct DB query that produced it. They are a point-in-time snapshot (2026-06-23) and must be re-measured before any phase (see verification commands).

**Census magnitude**
- `entity` total (all kinds): **450,619** — `SELECT count(*) FROM entity`
- `particular` (C2C platform listings): **359,151** — `WHERE kind='particular'`
- non-particular: **91,468** — `WHERE kind<>'particular'`
- kind breakdown: compraventa=76,132 · garaje=10,021 · desguace=2,785 · concesionario_oficial=2,300 · subasta=177 · plataforma=18 · oem_vo_portal=14 · importador=11 · rent_a_car_vo=6 · cadena=4
- `servable_vehicle` total: **2,257,001**; `vehicle_event` total: **2,761,820**

**The headline number and its three competing scopes (the core problem)**
- `/stats.dealers` live query: **19,164** — `v_dealer_resolved JOIN entity WHERE kind NOT IN (particular,desguace) AND EXISTS servable_vehicle`
- `product_stats.dealers` precompute (2026-06-23 12:33 UTC): **19,144** — `SELECT dealers FROM product_stats WHERE id=1`
- Historical inflated figure (no inventory/desguace filter): **54,607** — `COUNT(DISTINCT resolved_cdp_code) WHERE kind NOT IN ('particular')`
- Empty shells (non-part, non-desguace, **no inventory**): **37,136** — these are the gap between 54,607 and the served number
- `geo.completeness` uses `entity WHERE kind<>'particular'` (a *fourth*, different scope); `v_province_seal` "venta" segment uses compraventa+oficial-with-inventory vs DIRCE-451 (a *fifth* scope). **Five endpoints, five different denominators.**

**The unapplied canonical fix**
- `migrations/0056_v_servable_dealer.sql` exists on disk — defines the single canonical "sale point" view (active, non-particular, non-desguace, garage only when it has inventory). **NOT APPLIED**: `v_servable_dealer` does not exist in the DB, and `stats.py` does not reference it.
- Unification plan documented in `plans/P-census-data-quality.md`.

**Data-integrity defects (verified)**
- CIF populated in **1 of 450,619** entities — the only legal identity anchor is essentially empty.
- `status='closed'`: **0** rows; `status='evicted'`: **0** rows — lifecycle states defined but never populated; `servable_entity`'s `status NOT IN (evicted,closed)` filter is inert.
- `sells_cars=TRUE` on **all 359,151** particulares → signal useless as a scope filter; `sells_cars` NULL on 24,310/76,132 compraventa (31.9%).
- Geo gaps on non-particular: no lat/lon **56,786 (62.1%)**, no municipality_code **12,867 (14.1%)**, no province_code **1,090 (1.2%)**.
- Vehicle price sentinels in `servable_vehicle`: NULL **26,743** · `<300` **22,539** · `=1` **1,207** · all-9s (9999/99999/999999) **3,754**. The view's `price<=0` floor lets every one of these through.
- Vehicle field gaps: no year **37,136** · year>2027 **56** · no km **100,418** · km>1,000,000 **290**.
- `servable_vehicle.status='available'` is **100%** (2,257,001) — the field is never filtered, so `product_stats.vehicles_unique_available=1,841,679` comes from a different (dedup) path, not a status filter.
- `cross-source-dedup-v1` run produced 688 merges but `vam_verified=FALSE` → **inert**, not consumed by `v_dealer_resolved`.

**Honest verdict:** the served number is *defensible* (19,144) but **fragile and un-unified**. The canonical view that would lock it in is written but not deployed. There is no automated gate preventing the next scraper change from re-inflating it, no contract catching sentinel prices, and no monitor catching a stale source.

## Next-level objective

Reach a state where **every published number is the output of exactly one canonical, version-controlled definition, validated by an automated contract that fails CI before bad data is served, and continuously monitored for drift** — a degree of auditable correctness no manual census operation (human or AI) can match over time. Measurable targets:

1. **One definition, zero divergence.** `stats.dealers`, `geo.completeness` numerator, and `v_province_seal` "venta" numerator all resolve through `v_servable_dealer`. Cross-endpoint divergence = **0** (currently 5 scopes; live-vs-precompute already off by 20).
2. **Contract gate live.** 100% of ingested vehicle/entity rows pass a declarative data contract in CI; a deliberately corrupt fixture (sentinel price, year 3000, duplicate cdp_code) **fails the build**.
3. **Sentinel/clamp enforcement.** Served vehicles with non-credible price/year/km drop from the implicit "available" set; report exact count reclassified (baseline candidates: 1,207 price=1 + 3,754 all-9s + 56 future-year + 290 impossible-km = **5,307+** rows).
4. **Drift detection.** Daily anomaly check on per-source ingest volume and freshness, with a baseline-relative alert (no manual thresholds) wired into the existing `/alerts` endpoint.
5. **Lifecycle truth.** `closed`/`evicted` populated from real eviction signals (gone-detection), moving these from 0 to a non-zero, audited count — so the census reflects *current* reality, not cumulative-ever.

## Chosen technology (EUR0)

All selections are OSS, self-hostable, zero recurring cost, and chosen to layer onto the existing Postgres + Python stack without new infrastructure.

| Tool | Role in this domain | Why chosen over alternatives | Source / URL | Integration effort |
|---|---|---|---|---|
| **Pandera** (MIT) | In-process schema validation of the vehicle/entity DataFrames *at ingest time*, before rows reach Postgres. `DataFrameModel` declares year∈[1885,2026], km∈[0,2_000_000], price credibility, cdp_code uniqueness, URL regex. `@pa.check_types` guards pipeline functions. | CARDEEP data lives as DataFrames in the incremental scraper/enrichment path; Pandera validates *there*, at the boundary, cheapest place to fail fast. Typed, mypy-checkable, reused across ingest + unit tests. GX is heavier and DataFrame-second. | https://github.com/unionai-oss/pandera | Low — 1 schema module per record type; decorate existing ingest fns. |
| **dbt Core + dbt-expectations + dbt-utils** (Apache 2.0) | SQL-layer tests *closest to the served data*: `unique(cdp_code)`, `not_null`, `accepted_values(kind)`, `expect_column_values_to_be_between` for price/km/year clamps, `relationships` (every servable_vehicle → existing entity). Runs against the live Postgres in CI and locally. | The served truth is SQL views in Postgres. dbt tests are the canonical industrial pattern for "no bad row reaches the model". dbt-expectations (1,227 stars) adds the GX-style range/regex assertions in YAML. Pairs with the existing migration discipline. | https://github.com/calogica/dbt-expectations | Medium — model the existing views as dbt sources; no transformation rewrite needed (tests-only adoption). |
| **Soda Core + SodaCL** (Apache 2.0, engine local) | Operational, human-legible quality contracts run on a schedule against Postgres: `duplicate_count(cdp_code)=0`, `missing_percent(url)<5`, `freshness(updated_at)<24h`, per-source `row_count` anomaly. Output feeds `/alerts`. | SodaCL is the most readable DSL for *operational* checks (freshness, volume) that aren't naturally dbt model tests, and runs as a local process — Soda Cloud (paid) is not required. | https://github.com/sodadata/soda-core | Low-Medium — YAML checks + one cron invocation writing results to a table. |
| **PyOD** (BSD) | Unsupervised outlier detection over the vehicle distribution: dealers with anomalously low mean price (scam/agregador), impossible km/price combos, volume-outlier "dealers" that are disguised aggregators. Backend-agnostic over a DataFrame. | Learns the *real Spanish market distribution* instead of hand-coded thresholds; catches the long tail of corruption that fixed clamps miss. 46M+ downloads, mature. | https://github.com/yzhao062/pyod | Medium — offline batch job scoring servable_vehicle; flagged rows feed a quarantine review queue. |
| **datacontract-cli + ODCS** (Apache 2.0) | Formal per-source contract (e.g. "AutoScout delivers url+price+km in these ranges, this freshness, non-null cdp_code"). CI fails when a source's HTML change breaks the contract *before* corrupt rows land. | Turns the "scraper silently emits garbage" failure mode into a CI block. Exports to dbt models / SQL DDL so contract and tests stay in sync. ODCS 3.1 is the emerging standard. | https://github.com/datacontract/datacontract-cli | Medium — one contract file per active source; wire into existing CI. |

**Deferred (documented, not adopted now):** Splink/dedupe (record linkage) and OpenMetadata (catalog) belong to the `identity` and `ops` domains respectively. Great Expectations is intentionally **not** chosen — Pandera (DataFrame) + dbt-expectations (SQL) cover the same surface with less boilerplate and zero new runtime service. Elementary OSS is a strong future add for dbt-native anomaly observability once dbt is in place (Phase 4 candidate, deferred to keep PRs small).

## Target architecture

**Principle: one definition, three enforcement layers, additive and reversible.**

```
                 ┌─────────────────────────────────────────────────────┐
   SOURCES ──►   │ LAYER 1 — INGEST GATE (Pandera + datacontract-cli)    │
 (discovery/     │ Validate DataFrame at boundary. Reject/quarantine     │
  extraction)    │ rows failing schema. Contract breaks fail CI.         │
                 └───────────────────────────┬─────────────────────────┘
                                              ▼ (clean rows only)
                 ┌─────────────────────────────────────────────────────┐
   POSTGRES ──►  │ LAYER 2 — CANONICAL DEFINITION (SQL views)            │
                 │  v_servable_dealer  ◄── THE single sale-point view    │
                 │  servable_vehicle   ◄── price/year/km clamps applied  │
                 │  servable_entity    ◄── closed/evicted now populated  │
                 │  consumed identically by stats.py / geo.py / seal     │
                 └───────────────────────────┬─────────────────────────┘
                                              ▼
                 ┌─────────────────────────────────────────────────────┐
   CI + CRON ──► │ LAYER 3 — CERTIFICATION (dbt tests + Soda + PyOD)     │
                 │  dbt test: uniqueness/clamps/relationships (CI gate)  │
                 │  Soda: freshness/volume/dup (cron → /alerts)          │
                 │  PyOD: distribution outliers → quarantine review      │
                 └─────────────────────────────────────────────────────┘
```

**Data objects (additive):**
- `v_servable_dealer` (from migration 0056, applied) — the sole sale-point denominator.
- New columns on `servable_vehicle` view: tightened price/year/km predicates (additive view rewrite, old view kept as `v_servable_vehicle_legacy` for one cycle).
- New `data_quality_run` table (single source for Soda/dbt result history, mirrors `product_stats` single-row-cache pattern).
- New `vehicle_quarantine` table (PyOD/contract-flagged rows held out of served views, reviewable, reversible).
- `entity.status` populated `closed`/`evicted` from gone-detection signals (depends on `vehicle` domain emitting gone events).

**Safety contract for served data:** every change touching a served view is developed and validated in **docker Postgres `:5434` (dry-run)**. Promotion to `:5433` (live) requires dry-run + golden-output diff + Ferrari suite + CI all green. No exceptions.

## Execution phases

Each phase is ~1 PR, additive, reversible, with cold-start context.

---

### Phase 0 — Re-baseline and freeze the truth (no schema change)

**Cold-start context:** A future agent has no guarantee the figures above still hold. Before changing anything, re-measure and snapshot the five scopes so divergence is quantified, not assumed.

**Tasks:**
1. Run the five denominator queries (stats, product_stats, geo.completeness, v_province_seal venta, raw kind<>particular) against `:5433` read-only.
2. Persist results to `plans/quality-baseline-<date>.json`.
3. Diff against the recon snapshot; record any drift.
4. Confirm `v_servable_dealer` still absent: `\d v_servable_dealer`.

**Verification:**
```bash
psql $LIVE_RO -c "SELECT 'stats' s, count(DISTINCT resolved_cdp_code) n FROM v_dealer_resolved jdr JOIN entity e USING(...) WHERE e.kind NOT IN ('particular','desguace') AND EXISTS(...)"
psql $LIVE_RO -c "SELECT dealers FROM product_stats WHERE id=1"
psql $LIVE_RO -c "\d v_servable_dealer"   # must error: relation does not exist
```
**Exit criteria:** baseline JSON committed; the 5 scopes and their numeric divergence are written down.
**Rollback:** none (read-only).

---

### Phase 1 — Apply the canonical view in dry-run and prove equivalence

**Cold-start context:** `migrations/0056_v_servable_dealer.sql` defines the single sale-point view but is unapplied. We must prove it reproduces 19,144 ± explained delta before it touches live.

**Tasks:**
1. Spin up docker Postgres `:5434`, load a representative dump/fixture.
2. Apply `0056_v_servable_dealer.sql` on `:5434`.
3. Query `v_servable_dealer` count; compare to the Phase-0 stats baseline. Explain any delta line-by-line (expected sources: garage-with-inventory rule, dedup collapse).
4. Write a golden-output test asserting the count and the row-set hash.

**Verification:**
```bash
docker compose -f infra/dryrun.yml up -d   # :5434
psql $DRYRUN -f migrations/0056_v_servable_dealer.sql
psql $DRYRUN -c "SELECT count(*) FROM v_servable_dealer"   # ≈ baseline dealers
pytest tests/golden/test_servable_dealer.py
```
**Exit criteria:** `v_servable_dealer` count on `:5434` matches baseline within an explained delta; golden test green. **No `:5433` change yet.**
**Rollback:** drop the docker volume; live untouched.

---

### Phase 2 — Repoint stats/geo/seal to the canonical view (dry-run → live)

**Cold-start context:** stats.py, geo.py and the seal views each compute their own denominator. After Phase 1 proves `v_servable_dealer` is correct, all three must consume it so divergence → 0.

**Tasks:**
1. Edit `services/api/stats.py` dealers query → `SELECT count(*) FROM v_servable_dealer`.
2. Edit `geo.py` completeness numerator and `/geo/{prov}/entities` dedup path → `v_servable_dealer`.
3. Update `v_province_seal` venta numerator (new migration) → reference `v_servable_dealer`.
4. Regenerate `product_stats` precompute from the same view (eliminates the 19,164-vs-19,144 live/cache gap).
5. Run full golden + Ferrari suite on `:5434`.

**Verification:**
```bash
pytest tests/golden tests/ferrari -q       # all green on :5434
psql $DRYRUN -c "SELECT (SELECT count(*) FROM v_servable_dealer) = (SELECT dealers FROM product_stats WHERE id=1) AS unified"
# expect: unified = t
```
**Exit criteria (live promotion):** dry-run green + golden diff explained + Ferrari + CI green → apply migration to `:5433`; cross-endpoint divergence measured = 0.
**Rollback:** views are additive; revert API queries to prior commit and `DROP VIEW v_servable_dealer` (legacy queries still function).

---

### Phase 3 — Ingest contract gate (Pandera + datacontract-cli)

**Cold-start context:** Nothing currently stops a scraper change from emitting sentinel prices or duplicate cdp_codes. Add a fail-fast gate at the DataFrame boundary plus a per-source contract enforced in CI.

**Tasks:**
1. Create `pipeline/quality/schemas.py`: `VehicleModel` (year 1885–current, km 0–2_000_000, price credibility band, cdp_code unique, url regex) and `EntityModel` (kind ∈ accepted set, province_code format).
2. Decorate ingest functions with `@pa.check_types`; failing rows routed to `vehicle_quarantine` (not dropped silently).
3. Author `contracts/<source>.odcs.yaml` for each active source; wire `datacontract test` into CI.
4. Add a deliberately corrupt fixture (`price=1`, `year=3000`, dup cdp_code) and assert CI **fails** on it.

**Verification:**
```bash
pytest pipeline/quality/tests -q
datacontract test contracts/autoscout.odcs.yaml
pytest tests/contract/test_corrupt_fixture.py  # asserts non-zero exit on bad data
```
**Exit criteria:** corrupt fixture fails the build; clean fixture passes; quarantine table receives rejected rows.
**Rollback:** feature-flag the gate (`QUALITY_GATE=off`) → ingest behaves as today.

---

### Phase 4 — Vehicle clamps + sentinel reclassification (dry-run → live)

**Cold-start context:** `servable_vehicle` admits 1,207 price=1, 3,754 all-9s, 56 future-year, 290 impossible-km rows. Tighten the view so non-credible vehicles leave the served set; report the exact reclassified count.

**Tasks:**
1. Rewrite `servable_vehicle` (new migration) with credible-band predicates; keep `v_servable_vehicle_legacy`.
2. Add dbt-expectations YAML tests (`expect_column_values_to_be_between`) mirroring the SQL clamps.
3. On `:5434`, measure rows reclassified per defect class; persist to baseline.
4. Recompute `product_stats.vehicles_unique_available`; confirm direction (should drop by the reclassified count).

**Verification:**
```bash
psql $DRYRUN -c "SELECT count(*) FROM v_servable_vehicle_legacy" 
psql $DRYRUN -c "SELECT count(*) FROM servable_vehicle"   # lower by reclassified count
dbt test --select servable_vehicle
pytest tests/golden tests/ferrari -q
```
**Exit criteria:** reclassified count ≥ 5,307 and itemized by class; dbt clamp tests green; Ferrari green. Promote to `:5433` only on full green.
**Rollback:** `DROP VIEW servable_vehicle; ALTER VIEW v_servable_vehicle_legacy RENAME TO servable_vehicle`.

---

### Phase 5 — Operational drift monitoring (Soda + PyOD → /alerts)

**Cold-start context:** A stale scraper or IP block degrades the census silently. Add freshness/volume/dup checks and distribution-outlier detection feeding the existing `/alerts` endpoint.

**Tasks:**
1. Author SodaCL checks: `freshness(updated_at)<24h` per source, per-source `row_count` anomaly, `duplicate_count(cdp_code)=0`, `missing_percent(url)`.
2. Cron job runs Soda → writes to `data_quality_run`; `ops.py /alerts` surfaces failures.
3. PyOD batch scores `servable_vehicle` distribution (low-mean-price dealers, volume outliers); flagged → `vehicle_quarantine` review queue.
4. Document baselines in `plans/P-census-data-quality.md`.

**Verification:**
```bash
soda scan -d cardeep -c soda/checks.yml
psql $LIVE_RO -c "SELECT * FROM data_quality_run ORDER BY ran_at DESC LIMIT 1"
curl -s localhost:8000/alerts | jq '.[] | select(.source=="quality")'
python pipeline/quality/outliers.py --dry-run
```
**Exit criteria:** a synthetically stale source triggers a `/alerts` entry; PyOD produces a non-empty, reviewable flag set on real data.
**Rollback:** monitoring is read-only/advisory; disable cron. Quarantine is reversible (rows re-promotable).

---

### Phase 6 — Lifecycle truth: populate closed/evicted

**Cold-start context:** `closed`/`evicted` are 0 → the census is cumulative-ever, not current. Depends on the `vehicle` domain emitting gone/eviction signals.

**Tasks:**
1. Define eviction policy (e.g. N consecutive cosechas with 0 inventory + source 404) — document thresholds explicitly.
2. New job sets `entity.status='evicted'/'closed'` from those signals; `servable_entity`'s existing filter then becomes live.
3. Measure entities transitioning out; assert served sale-point count adjusts and is explained.

**Verification:**
```bash
psql $DRYRUN -c "SELECT status, count(*) FROM entity GROUP BY status"  # closed/evicted now > 0
pytest tests/golden tests/ferrari -q
```
**Exit criteria:** non-zero, audited closed/evicted counts on `:5434`; served count change explained; full green before `:5433`.
**Rollback:** `UPDATE entity SET status='active' WHERE status IN ('closed','evicted')` restores prior served set.

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Repointing to `v_servable_dealer` silently shifts the headline number | HIGH | Phase 1 proves equivalence on `:5434` with golden-hash test before any live change; any delta itemized. |
| Clamping vehicles over-prunes legitimate listings (e.g. genuine cheap project cars) | HIGH | PyOD-informed bands learned from real distribution, not arbitrary; quarantine (reversible) instead of delete; report exact reclassified set for review. |
| CIF essentially empty (1/450,619) blocks legal-grade identity assertions | MEDIUM | Do not gate scope on CIF; treat it as enrichment. Identity/dedup is owned by `identity` domain (Splink/dedupe) — this domain only certifies its output. |
| `cross-source-dedup-v1` inert (vam_verified=FALSE) leaks duplicates into counts | MEDIUM | dbt `unique(cdp_code)` test makes any leakage a CI failure; escalate verification to `identity` domain. |
| Soda Cloud / Elementary Cloud paywall creep | LOW | Engine/CLI only; results stored in our own `data_quality_run` table. EUR0 invariant held. |
| Touching served views on `:5433` without full gate | CRITICAL | Hard rule: `:5434` dry-run + golden + Ferrari + CI green required; every view change ships with a legacy fallback view. |

## Success metrics

1. **Scope divergence = 0** across stats / geo.completeness / seal "venta" (from 5 distinct denominators today).
2. **Live = precompute**: `v_servable_dealer` count == `product_stats.dealers` (closes the 19,164 vs 19,144 gap).
3. **Contract gate effective**: corrupt fixture fails CI; ≥1 real source contract enforced.
4. **Sentinels reclassified**: ≥5,307 non-credible vehicles removed from served set, itemized by defect class (price=1, all-9s, future-year, impossible-km).
5. **Drift coverage**: 100% of active sources have a freshness + volume Soda check feeding `/alerts`; a stale source raises an alert within one cron cycle.
6. **Lifecycle truth**: `closed`+`evicted` > 0 and audited; served count reflects *current* reality.
7. **EUR0 held**: no recurring cost across all adopted tools.
8. **Zero regressions**: Ferrari + golden suites green at every live promotion.