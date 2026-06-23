# Vehicle Canonicalization — Resolve the *same physical car* across every Spanish online listing, at zero false merges.

> This domain owns the deduplication of physical vehicles across the multiple online listings and platforms that advertise them. A single car for sale by one dealer can surface as 2–11 listings (the dealer's own site, plus syndication to coches.net, milanuncios, wallapop, autoScout-style aggregators). If the census counts each listing as a distinct car, the national inventory is inflated; if it over-merges, two genuinely distinct units collapse into one and the count is understated. This domain produces the *canonical* identity overlay — a non-destructive union-find clustering that says "these N listings are the same physical unit, this one is primary" — which directly feeds the dealer-identity resolver (a dealer's fingerprint is the Jaccard set of its canonical cars) and the served national inventory count. Its binding doctrine: **over-merge is forbidden and must stay strictly below under-merge**; a knowingly inflated counter is either deduped by a strong key or served with its measured `±dup_ci` bound. Scope is strictly the DIGITAL footprint: only listings that exist online are in play.

## Current state (verified)

All figures verified against the live DB (`postgres://cardeep@localhost:5433/cardeep`) and the source files cited; date 2026-06-23, branch `main` @ `81de58e`.

**The three non-destructive layers (verified in code):**

1. **Listing layer** (`vehicle`, `migrations/0003_vehicles_events.sql`): one row per `(entity_ulid, deep_link)` unique pair. Ingested via `BULK_INSERT_VEHICLES … ON CONFLICT DO NOTHING` (`pipeline/platform/_core/sql.py`) — no collapse on write. **2,377,080 rows** total; **2,257,054 available**; **120,026 gone**. `vehicle_event` append-only history = **2,761,820 rows**.
2. **Platform-edge layer** (`platform_listing`, `migrations/0009_platform_listing.sql`): `vehicle ↔ platform` edges = **2,176,386**. Carries a `listing_fingerprint` column intended for pHash+attribute dedup but **populated on only 15,617 / 2,176,386 = 0.7%** — effectively unused.
3. **Cluster overlay** (`vehicle_cluster` / `vehicle_cluster_run`, `migrations/0023_vehicle_cluster.sql`): deterministic union-find run `vehicle-identity-det-v1`, served via `v_canonical_vehicle` (latest `vam_verified=TRUE` run). Covers **2,262,673** available vehicles, yields **1,939,474 canonicals**, collapses **323,199 duplicates (14.3% collapse rate)**. Signal breakdown: photo_url only 335,843 listings; firma only 176,519; both 80,851; singletons (`match_signal='none'`) 1,669,460.

**The resolver (`pipeline/identity/cluster_vehicles.py`, verified line-by-line):**
- Signal A = identical normalized `photo_url` (query-stripped, resize-suffix-stripped, lowercased). Sufficient alone.
- Signal B = exact `(make, model, year, km)` + price within ±2% + same `province_code` + **different** `entity_ulid` + identical normalized title.
- Anti-FP guards (all present): never cross-province; same-entity pairs never firma-merged; km=0/NULL blocked unless shared 17-char VIN; photo high-collision guard at `PHOTO_HIGH_COLLISION_K=12` (excludes catalogue/placeholder URLs); cross-generation photo guard (`>2` model-years or `>50,000` km span). Canonical = earliest `first_seen`, tiebreak ULID asc. Anti-FP checks 1–4 run in-process (no cross-province cluster, no cluster >20, full coverage, singletons clean).
- The run is written `vam_verified=FALSE` (hardcoded in `_write_to_pg`); a separate Director gate flips it `TRUE`. The current served run was gated TRUE by that mechanism (gate pattern verified in `scripts/gate_particular_dedup.py`: `--apply`/`--revert`, records a two-independent-path `verification_verdict`, reversible).

**Real row-collapse (`scripts/cross_platform_dedup_watermark.py`, verified):** the only lawful destructive merge today is **VIN-exact (17-char)** — only **18 groups** in the whole DB, immaterial. It is applied reversibly (full before-state JSON in `.backups/`) + idempotently. The script's binding doctrine (verified docstring): strong key = `VIN exact OR (pHash Hamming ≤ 6 AND make,model,year,km-band equal)`.

**The blocking signal gaps (the reason this domain is not finished):**
- `photo_hash` (perceptual pHash) populated on **0 / 2,257,054 = 0%** of available vehicles → the pHash arm of the strong key **cannot run today**.
- Real 17-char `vin_ref` on **32,803 / 2,257,054 = 1.5%** → VIN arm is near-empty.
- `null_model` on **530,065 / 2,257,054 = 23.5%** and `null_km` on 100,419 (4.5%) → Signal B is structurally blind on a quarter of stock.
- `photo_url` present on 2,120,717 / 2,257,054 = 94% — Signal A has wide coverage but is string-exact only.
- **Measured residual cross-platform over-count: ~131.8K excess rows** at the strictest exact-km+exact-price floor (VAM: SQL `GROUP BY` 131,773 ≈ Python 131,895, agree within 0.09% — verified in the watermark script docstring). This is the prize: it is *not* a strong key (no pHash) so doctrine forbids auto-merging it today; it is currently MEASURE-ONLY.

**Already-built but dormant asset (verified):** `pipeline/delta_photo.py` (P08-S1) implements the canonical DCT pHash (imagehash-equivalent, `hash_size=8`, 64-bit) on **PIL + numpy + scipy only — no TensorFlow, no new dependency, EUR0 by construction**. Network fetch is injected (governor-wrapped, egress-gated). The mass backfill over the fleet is labelled **P08-S3, explicitly gated on a free egress route**; the diff rewrite to use pHash is P08-S2.

**C2C scope (verified):** 545,619 available vehicles belong to `kind='particular'` entities. They are excluded from the *dealer* cluster but DO enter `vehicle_cluster` B7 with identical guards — correct, since a private car can still be cross-listed.

## Next-level objective

**Activate the pHash strong key and close the measured ~131.8K fuzzy over-count to a served, falling, bounded number — without a single false merge — taking the collapse rate from 14.3% to a verified, photo-content-backed figure, and replacing every "served with ±dup_ci" inflation with either a strong-key collapse or a tightened, monitored bound.**

Concretely measurable exit:
1. `photo_hash` populated on **≥90%** of available vehicles that have a fetchable `photo_url`, via an EUR0 egress route.
2. A new resolver run (`vehicle-identity-phash-v1`) whose Signal A is upgraded from string-exact `photo_url` to **pHash Hamming ≤ 6 + attribute corroboration**, recovering the URL-rotation duplicates string-match misses, while the cross-generation/high-collision guards keep false-merge at zero.
3. The residual fuzzy over-count served by the API drops from `~131.8K ±` to a strong-key-resolved figure, with the *remaining* residual still served as a measured `±dup_ci` (never silently inflated).
4. Zero regressions: `v_canonical_vehicle`, `servable_vehicle` (2,257,001), `v_servable_dealer` counts move only in the dedup direction, fully explained, fully reversible.

## Chosen technology (EUR0)

| Need | Tool | Why this one | Source | Integration effort |
|---|---|---|---|---|
| Perceptual image hash (pixel-level dup detection) | **Already in-repo: `pipeline/delta_photo.py` DCT pHash** (imagehash-equivalent) | It is the canonical `imagehash.phash` algorithm, implemented on PIL+numpy+scipy with **zero new dependency** and zero license cost. We do NOT add `imagededup` (pulls TensorFlow, heavy) or even the `imagehash` pip package — the repo already has the exact 64-bit DCT hash. Validate ours bit-for-bit against `imagehash` once, then never depend on it. | In-repo; reference `https://github.com/JohannesBuchner/imagehash` for the equivalence oracle | LOW — code exists; needs a backfill driver + an indexable storage decision |
| Indexed Hamming-distance neighbor search over 64-bit hashes at 2.2M scale | **Postgres `bit(64)` + BK-tree blocking in Python**, OR `pgvector` Hamming on a `bit(64)` column | Hamming-≤6 neighbor search is the blocking bottleneck. `pgvector` (already a Postgres-native extension, no external vector service) supports binary Hamming distance and HNSW; it lives in the SAME Postgres so no new infra. If extension install is blocked, a pure-Python BK-tree over the hash set is EUR0 and offline. We pick whichever the `quality`/`ops` domains can install at EUR0; default to in-process BK-tree (zero infra risk). | `https://github.com/pgvector/pgvector` (PostgreSQL License) | MEDIUM — extension install is an `ops` dependency; BK-tree fallback is LOW |
| Fast fuzzy string compare for title/make/model corroboration | **RapidFuzz** (MIT, 2–100× FuzzyWuzzy, C++ core) | Already the right tool for normalizing `make`/`model`/`title` equivalence as a *corroborating* (never sole) signal. MIT vs FuzzyWuzzy's GPL. The repo's `rapidfuzz` usage is already established in the identity pipeline (recon noted a prior undeclared-dep bug — declare it). | `https://github.com/rapidfuzz/RapidFuzz` (MIT) | LOW — likely already a transitive dep; pin it explicitly |
| (Deferred, NOT adopted now) Semantic/embedding dedup | open_clip + FAISS/pgvector | Rejected for this phase: CLIP embeddings need model download + CPU inference budget, and pHash + attribute corroboration already covers "same photo, re-encoded/cropped/watermarked". Embeddings are a *future* recall-extension only if pHash leaves material residual. YAGNI now. | n/a | n/a |

**EUR0 discipline:** no managed dedup service, no paid vector DB, no training-data labelling. The egress for the photo backfill (the one real cost vector) is the hard gate — it MUST ride the existing governor-wrapped, free egress route the `extraction`/`ops` domains own; if no free route exists, the backfill stays PENDING-OWNER and the bounded `±dup_ci` serving continues. We never spend to fetch photos.

## Target architecture

```
                          vehicle (2.377M, append-only, never mutated)
                                   │ photo_url (94%), make/model/year/km/price, vin_ref (1.5%)
                                   ▼
      ┌──────────────────────────────────────────────────────────────────┐
      │  PHASE A — photo_hash backfill  (pipeline/delta_photo.py core)     │
      │  governor-wrapped free egress → DCT pHash (PIL+numpy+scipy) →      │
      │  store photo_hash on vehicle (additive column, already exists)     │
      └──────────────────────────────────────────────────────────────────┘
                                   │  photo_hash bit(64) on ≥90% available
                                   ▼
      ┌──────────────────────────────────────────────────────────────────┐
      │  PHASE B — pHash blocking index  (in-process BK-tree | pgvector)   │
      │  candidate pairs with Hamming ≤ 6                                  │
      └──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
      ┌──────────────────────────────────────────────────────────────────┐
      │  PHASE C — resolver vehicle-identity-phash-v1                      │
      │  Signal A' = (Hamming ≤ 6) AND (make,model,year,km-band equal)     │
      │            + ALL existing guards (cross-prov, km=0, cross-gen,     │
      │              high-collision, same-entity firma)                    │
      │  Signal B  = unchanged exact firma                                 │
      │  union-find → vehicle_cluster (vam_verified=FALSE)                 │
      └──────────────────────────────────────────────────────────────────┘
                                   │ Director VAM gate (2 independent paths)
                                   ▼  vam_verified=TRUE  (reversible flip)
      ┌──────────────────────────────────────────────────────────────────┐
      │  v_canonical_vehicle  →  resolve_entities.py (dealer Jaccard)      │
      │                       →  servable_vehicle / v_servable_dealer      │
      │  residual fuzzy not strong-keyed → served WITH ±dup_ci (measured)  │
      └──────────────────────────────────────────────────────────────────┘
```

**Data contract (all additive, all reversible):**
- `vehicle.photo_hash` — already exists in schema (`0003`), currently NULL; Phase A only fills it. No new column for the served path.
- New resolver writes a NEW `cluster_run_id='vehicle-identity-phash-v1'`; the existing `vehicle-identity-det-v1` is left untouched. `v_canonical_vehicle` automatically serves the latest `vam_verified=TRUE` run, so the cutover is a single reversible `UPDATE … SET vam_verified` flip.
- The `±dup_ci` bound is recorded to the verification ledger (the watermark script's existing lock mechanism), so the API's served counters always carry a measured bound.

**Hard safety rule (orchestrator mandate):** any step that touches *served* data (a new run feeding `v_canonical_vehicle`, or a row-collapse) is validated FIRST against an ephemeral docker clone on **`:5434`** (NOT the live `:5433`), with golden-count comparison and the full Ferrari/CI suite green, BEFORE the live `:5433` gate flip. The live DB is bound to `127.0.0.1:5433` only.

## Execution phases

> Each phase ≈ one PR. Cold-start context is self-contained. Commands assume repo root `C:\Users\elias\projects\cardeep`, `CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`. A dry-run clone is brought up on `:5434` for any served-data step.

### Phase 0 — Dry-run harness + pHash equivalence oracle (no data change)

**Cold-start context:** Before touching anything served, we need (a) a throwaway `:5434` Postgres clone of the live DB for golden testing, and (b) proof that the in-repo DCT pHash equals the reference `imagehash.phash`, so reviewers trust the strong key.

**Tasks:**
1. Add a `docker-compose.dryrun.yml` service `cardeep-pg-dryrun` (postgres:16, `127.0.0.1:5434:5432`, separate volume) and a `make dryrun-clone` target that `pg_dump` from 5433 → restore into 5434. Document in `docs/runbook/`.
2. Add `tests/test_phash_equivalence.py`: for a fixed set of test images (committed small fixtures), assert `pipeline.delta_photo` pHash == `imagehash.phash` bit-for-bit (install `imagehash` as a **test-only** dep; runtime stays dependency-free).
3. Declare `rapidfuzz` explicitly in the project deps (recon flagged a prior undeclared-dep bug).

**Verification:**
```bash
docker compose -f docker-compose.dryrun.yml up -d cardeep-pg-dryrun
make dryrun-clone
psql postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep -c "SELECT count(*) FROM vehicle;"   # == 2377080
pytest tests/test_phash_equivalence.py -q
```
**Exit criteria:** clone count matches live; equivalence test green; `rapidfuzz` pinned. **Rollback:** `docker compose -f docker-compose.dryrun.yml down -v` (clone is throwaway); revert PR.

### Phase 1 — photo_hash backfill driver (EUR0 egress-gated)

**Cold-start context:** `pipeline/delta_photo.py` already computes the pHash; it has no mass driver. `vehicle.photo_hash` is 0% populated. Egress is the only cost vector and MUST use the existing free, governor-wrapped fetch route owned by `extraction`/`ops`.

**Tasks:**
1. Write `scripts/backfill_photo_hash.py`: iterate `vehicle WHERE status='available' AND photo_url IS NOT NULL AND photo_hash IS NULL`, fetch bytes via the injected governor fetch, compute pHash via `delta_photo`, `UPDATE vehicle SET photo_hash=...`. Idempotent (skips already-hashed), resumable (watermark by `vehicle_ulid`), batched, rate-limited by the egress token bucket. Content-hash cache keyed by image bytes (blake2b) to avoid re-fetching the same CDN image (recall: many listings share one photo).
2. **Egress gate:** if no free egress route is confirmed available, the script runs in `--measure-only` mode (counts fetchable photos, estimates coverage) and the backfill stays **PENDING-OWNER** — it does not block the rest of the plan.
3. Store `photo_hash` as `bit(64)` (or hex `char(16)` if extension-free Hamming is chosen) — additive; decide with `quality`/`ops`.

**Verification (on `:5434` first):**
```bash
CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep \
  python -m scripts.backfill_photo_hash --limit 5000
psql .../5434 -c "SELECT count(*) FILTER (WHERE photo_hash IS NOT NULL) FROM vehicle WHERE status='available';"
python -m scripts.backfill_photo_hash --dry-run --measure-only   # coverage estimate
```
**Exit criteria:** on the 5000-row dry-run sample, ≥90% of fetchable photos hashed, 0 mutations to any column other than `photo_hash`, fully resumable. Full-fleet backfill proceeds only after egress route confirmed free. **Rollback:** `UPDATE vehicle SET photo_hash=NULL` (additive column; reversible); the column itself is pre-existing so nothing is dropped.

### Phase 2 — pHash blocking index + candidate-pair generation

**Cold-start context:** With `photo_hash` populated, we need Hamming-≤6 neighbor pairs at 2.2M scale without O(n²). Default to an in-process BK-tree (EUR0, zero infra); offer pgvector path if `ops` confirms the extension installs free.

**Tasks:**
1. Add `pipeline/identity/phash_blocking.py`: build a BK-tree over all non-null `photo_hash`, emit candidate pairs with Hamming ≤ 6. Pure Python, offline-testable. Unit test on synthetic hash sets (`tests/test_phash_blocking.py`) with known Hamming neighbors.
2. Benchmark on the `:5434` clone; assert wall-clock and pair-count are sane (compare candidate count vs current string-exact photo edges as a recall sanity check — pHash should produce *more* candidate pairs than string-exact, since it catches URL-rotated re-encodes).

**Verification:**
```bash
pytest tests/test_phash_blocking.py -q
CARDEEP_DSN=.../5434 python -m pipeline.identity.phash_blocking --report   # pair count, timing
```
**Exit criteria:** unit tests green; candidate pairs ≥ current Signal-A string-exact pair count; runtime bounded. **Rollback:** revert PR (read-only module, no data touched).

### Phase 3 — resolver `vehicle-identity-phash-v1` (new run, NOT served yet)

**Cold-start context:** `cluster_vehicles.py` is the canonical resolver. We fork its Signal A from string-exact `photo_url` to pHash-Hamming-≤6 **gated by attribute corroboration** (`make,model,year,km-band` equal), keep Signal B and ALL anti-FP guards identical, and write a NEW `cluster_run_id`. Doctrine: a pHash neighbor alone is NOT a strong key — it merges only with make/model/year/km-band corroboration (the watermark docstring's strong-key definition). The run writes `vam_verified=FALSE`.

**Tasks:**
1. Add `pipeline/identity/cluster_vehicles_phash.py` (or a `--signal-mode=phash` flag on the existing module, preserving det-v1): Signal A' = candidate pair from Phase 2 AND `make`/`model`/`year` equal AND `km` within band AND existing cross-generation + high-collision + km=0 guards. Signal B unchanged. `RUN_ID='vehicle-identity-phash-v1'`, `vam_verified=FALSE`.
2. Extend `tests/test_cluster_vehicles.py` with pHash-signal cases: Hamming-≤6 same-car merges; Hamming-≤6 cross-generation does NOT merge; high-collision placeholder pHash excluded; km=0 still guarded.
3. Run on `:5434` clone; capture run stats and the 4 anti-FP checks; diff canonical count vs det-v1's 1,939,474 (expect *lower* canonical count = more collapse, all explained by recovered URL-rotation dups).

**Verification:**
```bash
pytest tests/test_cluster_vehicles.py tests/test_dedup_invariants.py -q
CARDEEP_DSN=.../5434 python -m pipeline.identity.cluster_vehicles_phash
psql .../5434 -c "SELECT n_in,n_clusters,n_merged FROM vehicle_cluster_run WHERE cluster_run_id='vehicle-identity-phash-v1';"
# anti-FP: cross-province=0, no cluster>20, full coverage, singletons clean (printed by the run)
```
**Exit criteria:** all anti-FP checks pass on the clone; collapse increases vs det-v1 with every delta cluster explained; full Ferrari/unit/`test_dedup_invariants` suite green. **Rollback:** `DELETE FROM vehicle_cluster_run WHERE cluster_run_id='vehicle-identity-phash-v1'` (cascades to `vehicle_cluster`); det-v1 remains the served run untouched.

### Phase 4 — Director VAM gate + served cutover (the one served-data flip)

**Cold-start context:** `v_canonical_vehicle` serves the latest `vam_verified=TRUE` run. Flipping the new run TRUE is the cutover; it is a single reversible `UPDATE`. The gate requires two independent verification paths agreeing (pattern from `scripts/gate_particular_dedup.py`) and a `verification_verdict` record.

**Tasks:**
1. Add `scripts/gate_vehicle_phash.py` (`--apply` / `--revert`): verify canonical count by two independent paths (resolver `n_clusters` vs `SELECT count(DISTINCT canonical_vehicle_ulid)` from the live overlay), record a TRUSTWORTHY verdict, flip `vam_verified=TRUE`. Idempotent; `--revert` restores det-v1 instantly.
2. Run the backfill (Phase 1) + resolver (Phase 3) against LIVE `:5433` only after the `:5434` golden run is clean and CI is green. Then gate.
3. Re-measure the residual fuzzy over-count (`cross_platform_dedup_watermark.py --dry-run`): the served `±dup_ci` bound must now be **lower** than ~131.8K (strong-key collapse moved part of it into real merges). Lock the new bound to the ledger.

**Verification:**
```bash
# LIVE, post-backfill+resolver, CI green, 5434 golden clean:
python scripts/gate_vehicle_phash.py --run-id vehicle-identity-phash-v1 --apply
psql .../5433 -c "SELECT count(*) FROM v_canonical_vehicle;"        # serves phash-v1
psql .../5433 -c "SELECT count(*) FROM servable_vehicle;"           # ≈2.257M, moved only by dedup
python -m scripts.cross_platform_dedup_watermark --dry-run         # residual ±dup_ci now < 131.8K
```
**Exit criteria:** served canonical count drops by the explained merge delta; `servable_vehicle` and `v_servable_dealer` change only in the dedup direction with full attribution; residual `±dup_ci` strictly lower and locked to the ledger; downstream `resolve_entities.py` re-run clean. **Rollback (instant, reversible):** `python scripts/gate_vehicle_phash.py --run-id vehicle-identity-phash-v1 --revert` → `v_canonical_vehicle` immediately serves det-v1 again. No row was ever destroyed.

### Phase 5 — Residual bound tightening + monitoring (close the loop)

**Cold-start context:** After the strong-key collapse, a residual fuzzy over-count remains (weak-key pairs with no pHash and no VIN). Doctrine forbids auto-merging it; it must be served bounded and the bound must be *monitored* so it cannot silently re-inflate as new listings arrive.

**Tasks:**
1. Add a scheduled re-measure of the `±dup_ci` bound (re-run the watermark `--dry-run` measure + lock) so every census refresh re-publishes a current bound.
2. Add a guard test (`tests/test_dup_bound_monotone.py`): the served canonical count must never *exceed* the listing count, and the locked `±dup_ci` must be present for every served national counter (no naked inflated counter).
3. Document, in `docs/`, the explicit residual: which over-count is structurally un-mergeable today (no pHash + no VIN + null model/km) and what would unlock it (more VINs from `extraction`, more model coverage from `quality`).

**Verification:**
```bash
pytest tests/test_dup_bound_monotone.py -q
python -m scripts.cross_platform_dedup_watermark --dry-run   # bound re-locked
```
**Exit criteria:** every served counter carries a current `±dup_ci`; monotonicity guard green in CI; residual documented with its unlock dependency. **Rollback:** revert PR (read-only + test additions).

## Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| **No free egress route → photo backfill cannot run** | HIGH (blocks the whole pHash arm) | Backfill ships in `--measure-only` mode; stays PENDING-OWNER without blocking Phases 0/2 scaffolding. The bounded `±dup_ci` serving continues meanwhile — the census is never wrong, only conservatively inflated with a *declared* bound. Egress is an `extraction`/`ops` dependency, not invented here. |
| **pHash over-merge: two distinct same-model cars share a near-identical photo** | CRITICAL (false merge violates doctrine) | pHash is NEVER a sole signal — strong key requires `make,model,year,km-band` equality too; cross-generation guard (>2yr / >50k km) and high-collision-K guard carry over unchanged. Validated on `:5434` golden before any live gate. |
| **Hamming neighbor search blows up at 2.2M** | MEDIUM | Default in-process BK-tree (EUR0, no infra); pgvector only if `ops` confirms free install. Benchmarked in Phase 2 on the clone before resolver runs. |
| **Serving regression on cutover** | HIGH | The cutover is a single reversible `vam_verified` flip; `--revert` restores det-v1 instantly. Golden-count diff on `:5434` + full CI/Ferrari green is a hard precondition. Live `:5433` is never the first target. |
| **In-repo pHash silently diverges from the reference algorithm** | MEDIUM | Phase 0 bit-for-bit equivalence test against `imagehash` (test-only dep) as a permanent oracle. |
| **Null-model 23.5% caps both Signal B and the km-band corroboration** | MEDIUM (recall ceiling) | Declared honestly as the residual's structural cause; depends on `quality` (model enrichment) and `extraction` (VIN harvest) to lift. Not over-claimed. |

## Success metrics

| Metric | Baseline (verified) | Target |
|---|---|---|
| `vehicle.photo_hash` populated (available, fetchable photo) | 0 / 2,257,054 (0%) | ≥ 90% of fetchable |
| Served canonical count (`v_canonical_vehicle`) | 1,939,474 (det-v1) | < 1,939,474, every delta explained by recovered URL-rotation dups |
| Collapse rate | 14.3% (323,199 merged) | > 14.3%, photo-content-backed, 0 false merges |
| Cross-province false-merge clusters | 0 (anti-FP check 1) | 0 (must stay 0) |
| Residual fuzzy over-count served as `±dup_ci` | ~131,800 (measure-only, naked) | strictly lower + locked to ledger + monitored |
| Naked inflated served counters (no `±dup_ci`) | (doctrine violation if any) | 0 — every counter bounded |
| Reversibility of cutover | n/a | 1-command `--revert` restores prior served run |
| Test suite (`test_cluster_vehicles`, `test_dedup_invariants`, new pHash tests) + Ferrari + CI | green on det-v1 | green on phash-v1, 0 regressions |
