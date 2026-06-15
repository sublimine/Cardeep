# Feature Design — Wire the Inquisition engine into the live flow

**Review verdict:** NEEDS-REVISION → **revisions folded in below; PROCEED after the corrected emitter.**
**Effort:** M
**Files:** `pipeline/inquisition/prosecutor.py`, `pipeline/ops/scheduler.py`, `tests/test_inquisition_emit.py` (NEW), `tests/test_scheduler_jobs.py`, `docs/workflows/verification/WF-INQUISITION.md`, `docs/SUPERPLAN.md`, `PROGRESO.md`.
**Migration:** none (pure code wiring on the existing 0032 inquisition tables; newest applied is 0038).

---

## 1. Summary & finding closed

Closes **D-inquisition-never-ran** (`AUDIT_2026-06-15_PHASE2.md:286-291`): the Inquisition engine (prosecutor, quorum, lenses, router) is built and passes its tests but has **NEVER adjudicated a live claim** — [VERIFIED] `inquisition_verdict` live tuples = **0**; `prosecute_pending`/`prosecute_claim` have NO live caller (only prosecutor.py + tests). The scheduler runs only `schedule_reverification` (cadence δ), never the prosecutor.

This feature builds the missing live bridge correctly: **(1)** a CORRECTED, idempotent, opt-in claim emitter that re-keys VAM inventory verdicts to inquisition `subject_type='inventory'` / `subject_key='inventory:<entity_ulid>'` so Lens A measures the REAL available count; **(2)** a scheduler prosecution job calling `prosecute_pending(limit)` in a 6h cadence. It writes ONLY `inquisition_*` + `gestion_item`/`gestion_transition`/`alert` (the router's already-live targets); it NEVER touches `vehicle`/`entity`/`verification_verdict` served data.

**The €0 honesty gate (why emission is opt-in/bounded, not on-by-default):** at €0 the Inquisition cannot certify ANY first-pass claim TRUSTWORTHY — Lens B (raw store) ABSTAINs, Lens C (live refetch) ABSTAINs (harvest-gated), Lens E inventory ABSTAINs without a seeded prior hash, leaving only Lens A asserting → `indep_score=0<2` → quorum Rule 2 → `REFUTED:NO_INDEPENDENT_PATH` → `ESCALATE_OWNER` gestion_item. So mass emission today is HONEST but produces a flood of un-self-resolvable escalations. Emission therefore ships **default OFF** (`CARDEEP_INQUISITION_EMIT` unset/0 = prosecute-only) and bounded; prosecution is safe-to-run-but-low-yield until Lens B raw-store or Lens C live-refetch lands.

### What the review corrected (folded in, not appended)
- **The existing `emit_claim_from_verdict` signature is positional:** `async def emit_claim_from_verdict(conn, verification_verdict_row: asyncpg.Record)` (prosecutor.py ~:400). It reads `.get("subject_type"/"subject_key"/"primary_value"/"primary_path")`. The rewrite preserves this positional shape (the batch emitter passes the row).
- **Per-subject-type entity_ulid resolution (the key fix):** `entity_inventory` → `SELECT entity_ulid FROM entity WHERE cdp_code=$1` ([VERIFIED] **537/537** resolvable); `generic_dealer_site_inventory` → **subject_key IS ALREADY the entity_ulid** ([VERIFIED] **17/17** match `entity.entity_ulid`), use it directly (optionally `SELECT 1 FROM entity WHERE entity_ulid=$1` to drop orphans). Both → `subject_type='inventory'`, `subject_key='inventory:'||entity_ulid`. The original plan resolved only via cdp_code, which would have silently dropped all generic_dealer rows.
- **Remove `coverage`/`source_coverage` from emitter scope.** [VERIFIED] no €0 lens can measure a `source_key`-shaped coverage subject (`source_coverage` rows include `subject_key='as24_wholesale'` etc.). Document them as SKIP-by-design; do NOT list them as handled.
- **Corrected emittable scope:** [VERIFIED live] active `verification_verdict` (`superseded_by IS NULL`) emittable rows = **15 `entity_inventory` REFUTED + 12 `generic_dealer_site_inventory` REFUTED + 1 `denominator` REFUTED ≈ 28 rows** (plus 5 `source_coverage` REFUTED that are SKIP-by-design). **Zero emittable UNVERIFIED** of the inventory/denominator types. The original plan's "66 active rows (43 REFUTED + 23 UNVERIFIED)" counted unrelated subject_types. Fix the dry-run criterion accordingly — `platform_slice` is NOT in the emittable SELECT.
- **Lens-E "cycle-2 corroborates" claim DOWNGRADED:** Lens E ABSTAINs until a hash-seeding writer lands (out of scope). Do not claim a second prosecution cycle starts corroborating €0.
- **Drop the load-bearing emphasis on per-claim `tolerance`:** the lens uses `regime_for` internally; tolerance is not the gating mechanism.
- **Dedupe namespace (no collision):** after re-key, the ESCALATE_OWNER `dedupe_key` = `inquisition:inventory:inventory:<ulid>` (router.py:180) — DISTINCT from any VAM gestion_item. [VERIFIED] zero existing `gestion_item` with `subject_type='inventory'`, so no collision before enabling emission.

---

## 2. Files & lines touched

| File:lines | Change |
|---|---|
| `prosecutor.py:~400-481` (`emit_claim_from_verdict`) | REWRITE body (keep positional signature). Fix subject mapping (§3 STEP 1); add idempotency guard (§3 STEP 2). Return `claim_id` or `None` (skip). |
| `prosecutor.py` (new fn) | **NEW** `async def emit_claims_from_verdicts(conn, *, limit=200, include_trustworthy=False) -> dict`: batch emitter the scheduler calls (§3 STEP 3). |
| `scheduler.py:~80-87` (constants) | ADD `INQUISITION_PROSECUTE_CADENCE_HOURS=6`, `INQUISITION_PROSECUTE_BATCH=int(os.environ.get('CARDEEP_INQUISITION_PROSECUTE_BATCH',200))`, `INQUISITION_EMIT_BATCH=int(os.environ.get('CARDEEP_INQUISITION_EMIT_BATCH',200))`. |
| `scheduler.py:~442-470` (new job fn) | **NEW** `inquisition_prosecute_job()` mirroring `inquisition_cadence_job` (§3 STEP 4). |
| `scheduler.py:~664-674` (add_job block) | ADD `add_job(inquisition_prosecute_job, trigger='interval', hours=..., id='inquisition_prosecute', name=..., replace_existing=True, max_instances=1, coalesce=True, misfire_grace_time=600)`. |
| `scheduler.py:~676-680` (startup log) | UPDATE to mention the prosecute job. |
| `tests/test_inquisition_emit.py` | **NEW** (§Verification step 1). |
| `tests/test_scheduler_jobs.py` | ADD job-registration + smoke assertions. |
| `WF-INQUISITION.md:11-18,163-178` / `SUPERPLAN.md` / `PROGRESO.md` | Update Disparador/Estado: prosecute now has a live caller; emit corrected+idempotent+opt-in; record the €0 ceiling. |

---

## 3. Atom-level approach

**STEP 1 — Fix `emit_claim_from_verdict`.** Current code (VERIFIED) maps `_vam_to_inq_subject = {entity_inventory:'count', coverage:'coverage', freshness:'count', field_fill:'entity_field', existence:'entity_field', denominator:'denominator'}` and writes `subject_key=vam_subject_key` verbatim (a cdp_code), defaulting unknowns to `'count'`. The trap: inquisition `'count' + cdp_code` → Lens A `_a_count` else-branch → `SELECT count(*) FROM entity WHERE province_code='CDP-ES-46-...'` → 0 → `REFUTE_SOFT` against a healthy inventory (meaning-corruption, the autocasion-orphan class).

REPLACE the mapping and key construction (branch on VAM `subject_type`):
- `entity_inventory` → resolve `entity_ulid = SELECT entity_ulid FROM entity WHERE cdp_code=$1` ([VERIFIED 537/537]). If unresolved → `return None` (SKIP).
- `generic_dealer_site_inventory` → `entity_ulid = vam_subject_key` directly ([VERIFIED 17/17 already an entity_ulid]); optionally validate `SELECT 1 FROM entity WHERE entity_ulid=$1`, else SKIP.
- Both of the above → inquisition `subject_type='inventory'`, `subject_key='inventory:'||entity_ulid`. This makes Lens A `_a_inventory` run `COUNT(*) FILTER (WHERE price IS NOT NULL) ... WHERE entity_ulid=$1 AND status='available'` (the REAL measure) and activates Lens E on `inventory:<entity_ulid>`.
- `denominator` → `'denominator'` with the existing key shape (Lens A `_a_denominator` parses `denominator:<segment>[:<prov>]`).
- `coverage` / `source_coverage` → **`return None` (SKIP-by-design)**: no €0 lens measures a source_key-shaped coverage subject.
- everything else (`platform_slice`, `family_slice`, `source`, `global_count`, `freshness`, `field_fill`, `existence`, …) → **`return None`**. DO NOT coerce to `'count'` (the original bug class).

`asserted_value = primary_value` (canonical int string from verify.py); `producer_state = {source:primary_path, tool:'vam_count_quorum', snapshot_id:'vam_snap', code_path:'pipeline/verify.py'}` (unchanged); `evidence_uri=NULL`. INSERT unchanged EXCEPT it now passes through the idempotency guard.

**STEP 2 — Idempotency guard** (inside `emit_claim_from_verdict`, before INSERT). [VERIFIED] no UNIQUE on `inquisition_claim(subject_type,subject_key)` (only `claim_id` PK + 2 CHECKs); `claim_id` is a fresh ULID per call → re-emit every 6h would stack duplicates. The btree `idx_claim_subject(subject_type,subject_key)` exists (0032) so this lookup is indexed:
```python
exists = await conn.fetchval(
    "SELECT 1 FROM inquisition_claim WHERE subject_type=$1 AND subject_key=$2 "
    "AND status IN ('PENDING','PROSECUTING') LIMIT 1",
    inq_subject_type, subject_key)
if exists:
    return None  # an open claim already covers this subject
```
(A DECIDED claim for the same subject is allowed to re-emit on the next TTL cycle — the intended re-prosecution.)

**STEP 3 — Batch emitter** `emit_claims_from_verdicts(conn, *, limit=200, include_trustworthy=False)`. One `conn.transaction()`. Query (emittable types ONLY — coverage excluded):
```sql
SELECT vv.id, vv.subject_type, vv.subject_key, vv.primary_value, vv.primary_path,
       vv.claim_kind, vv.verdict
  FROM verification_verdict vv
 WHERE vv.superseded_by IS NULL
   AND vv.subject_type IN ('entity_inventory','generic_dealer_site_inventory','denominator')
   AND (vv.verdict IN ('REFUTED','UNVERIFIED')
        OR ($1::boolean AND vv.verdict='TRUSTWORTHY'))
 ORDER BY vv.created_at DESC
 LIMIT $2
```
For each row call `emit_claim_from_verdict` (which SKIPs unresolvable/unsupported and dedupes). Tally `{scanned, emitted, skipped_existing, skipped_unsupported}`. `include_trustworthy=False` default: re-prosecuting a TRUSTWORTHY at €0 can only downgrade it to `REFUTED:NO_INDEPENDENT_PATH`, so it is gated.

**STEP 4 — Scheduler prosecute job** (`scheduler.py`), modeled on `inquisition_cadence_job`: build `_run()` coroutine; `asyncpg.connect(_ASYNCPG_DSN)`; in `_run`: `if os.environ.get('CARDEEP_INQUISITION_EMIT')=='1': await emit_claims_from_verdicts(conn, limit=INQUISITION_EMIT_BATCH)`; then **ALWAYS** `await prosecute_pending(conn, limit=INQUISITION_PROSECUTE_BATCH)`; log summary; wrap `asyncio.run` in try/except logging only (never raise). Register `id='inquisition_prosecute'`, `hours=6`, `max_instances=1`, `coalesce=True`. Single-producer + host advisory lock (scheduler.py:613-624) guarantee no double-run. (Offset note: both inquisition jobs run on 6h but are distinct ids; consider prosecute at +30min — DB-only, no host-hammer.)

**STEP 5 — The 4 questions.**
- **TRIGGER:** a scheduler job (NOT inline in harvest). Source = active VAM verdict rows (REFUTED/UNVERIFIED of the 3 emittable types). Inline delta-event emission is DEFERRED (delta.diff_vehicle not wired into connectors; Lens E delta-fraud needs a prior hash anyway).
- **CADENCE:** 6h (matches the doc "cadencia δ"). Prosecute-only is the default tick; emission opt-in.
- **IDEMPOTENCY (3 layers):** (1) emit-side NOT-EXISTS guard on open claims (Step 2); (2) `prosecute_pending` selects `status='PENDING'` and the PENDING→PROSECUTING UPDATE is the row-lock serializer (prosecutor.py:160-167); (3) router `open_or_refresh` dedupe_key UNIQUE = one open gestion_item per subject (route.py:124).
- **WRITES-ONLY-INQUISITION_* invariant:** `prosecute_claim` INSERTs `inquisition_skeptic` + `inquisition_verdict`, UPDATEs only `inquisition_claim.status`, and via the router UPSERTs `gestion_item` + INSERTs `gestion_transition` + (critical routes) `alert`. It NEVER writes `vehicle`/`entity`/`platform_listing`/`verification_verdict`. [VERIFIED] the router does NOT write `verification_verdict.superseded_by` (only verify.py:185 does) — prosecution cannot corrupt served "latest verdict" semantics.

**STEP 6 — SAFE NOW vs HARVEST-GATED.**
- **SAFE NOW (€0):** `prosecute_pending` in cadence (drains seeded claims; honest `REFUTED:NO_INDEPENDENT_PATH` → ESCALATE_OWNER; no served writes). The corrected idempotent emitter. Lens A (SQL re-query), Lens D (cross-source).
- **HARVEST-GATED (default OFF):** mass emission (`CARDEEP_INQUISITION_EMIT` unset); Lens B raw-recount (`_RAW_STORE_AVAILABLE=False`); Lens C live-refetch (separate egress/JA3); TRUSTWORTHY re-prosecution; **Lens E inventory corroboration (needs a hash-seeding writer — out of scope, ABSTAINs until then).** When Lens B/C lands, flip `CARDEEP_INQUISITION_EMIT=1`; same wiring yields real adjudications with no further code change.

---

## 4. Verification commands & acceptance criteria

DB via `docker exec -e PGPASSWORD=cardeep_dev_only cardeep-pg psql -U cardeep -d cardeep -c "SQL"`.

1. **Unit/integration:** `python -m pytest tests/test_inquisition_emit.py tests/test_inquisition_prosecutor.py -v` → all pass. New emit tests: (a) re-key — seed a dealer+vehicles, emit an `entity_inventory` verdict, prosecute, assert Lens A `measured_value == real available count` (NOT 0); (b) idempotency — double-emit → exactly 1 PENDING claim; (c) skip — an unsupported subject_type (e.g. `platform_slice`) → zero claims, no exception; (d) e2e — emit→prosecute → `REFUTED:NO_INDEPENDENT_PATH` + an `ESCALATE_OWNER` gestion_item. (Reviewer reproduced the re-key: Lens A measured the real count **8**, not 0; verdict `REFUTED:NO_INDEPENDENT_PATH`; gestion_item opened.)
2. **Scheduler smoke (live DB, emission OFF):** `CARDEEP_INQUISITION_EMIT` unset; `python -c "from pipeline.ops.scheduler import inquisition_prosecute_job; inquisition_prosecute_job()"` → logs a summary, does NOT raise, exit 0.
3. **Emit dry-run (live DB, rolled back):** connect, `BEGIN`, `emit_claims_from_verdicts(conn, limit=5)`, print summary, `ROLLBACK`. **ACCEPTANCE:** every emitted claim has `subject_type IN ('inventory','denominator')` with `subject_key` matching the lens-required prefix; `skipped_unsupported>0`; **NO `platform_slice`/`coverage` rows appear** (they're not in the SELECT / are SKIPped).
4. **Full emit+prosecute cycle (rolled back):** `BEGIN; emit_claims_from_verdicts(limit=20); prosecute_pending(limit=20);` then group `inquisition_verdict` and `inquisition_skeptic`; `ROLLBACK`. **ACCEPTANCE:** Lens A rows carry real measured counts; verdicts are `REFUTED:NO_INDEPENDENT_PATH` (never a fabricated TRUSTWORTHY — the DB CHECK `trustworthy_needs_independence` would block that anyway).
5. **Duplicate-claim regression:** run `emit_claims_from_verdicts` twice in the same committed state on a scratch subject (rolled-back tx) → `SELECT subject_type,subject_key,count(*) ... WHERE status IN ('PENDING','PROSECUTING') GROUP BY 1,2 HAVING count(*)>1` returns 0 rows.
6. **Served-data non-corruption:** before/after a prosecute cycle (rolled back), assert byte-identical: `count(*) FROM vehicle`; `count(*) FROM entity`; `id,verdict,superseded_by FROM verification_verdict WHERE superseded_by IS NULL ORDER BY id`.
7. **Dry-run scheduler registration:** `python -m pipeline.ops.scheduler --dry-run` still prints normally.

**ACCEPTANCE (all hold):** (a) job registered `id='inquisition_prosecute'`, 6h, `max_instances=1`, coalesce; (b) prosecuted `entity_inventory` claim's Lens A measures the real count, not province-count 0; (c) double-emit = 1 open claim; (d) unsupported subject_types skipped silently; (e) €0 verdicts land as `REFUTED:NO_INDEPENDENT_PATH`, never fabricated TRUSTWORTHY; (f) `vehicle`/`entity`/served `verification_verdict` untouched; (g) emission default OFF.

---

## 5. Risks (incl. reviewer's missed/confirmed risks)

1. **FLOOD / alert-and-never-recover (central):** at €0 every first-pass claim → `REFUTED:NO_INDEPENDENT_PATH` → `ESCALATE_OWNER` (no SLA, awaits human). Mass emission now would open hundreds of un-self-resolvable escalations. Mitigation: emission default OFF; batch-capped (200); scope = REFUTED/UNVERIFIED actives of the 3 emittable types (~28 rows), not the 522 active TRUSTWORTHY `entity_inventory`. Prosecute-only default just drains whatever is already PENDING (zero today).
2. **MEANING-CORRUPTION via mis-keying (the existing bug):** `entity_inventory→count+cdp_code` makes Lens A count provinces (→0) and falsely REFUTE a healthy inventory. Fixed by re-key to `inventory:<entity_ulid>` (537/537 + 17/17 generic) and SKIP for unsupported shapes. The emit test asserts `measured!=0`.
3. **DUPLICATE-CLAIM ACCUMULATION:** fresh-ULID `claim_id`, no UNIQUE → without the guard every 6h stacks duplicates. Mitigation: emit-side open-claim guard (Step 2) + regression test #5.
4. **AS24 touchpoint (reviewer's miss — but harmless):** `source_coverage` rows include `subject_key='as24_wholesale'`. Emitting/prosecuting it is pure DB (Lens C makes ZERO network calls; A/D/E are SQL/hash), so the AS24-ban scar is nil here. We SKIP coverage anyway (§3 STEP 1), so AS24 is never even emitted. The original plan reached "no AS24 risk" for the wrong reason (it never noticed AS24 is a prosecutable subject).
5. **Dedupe namespace (reviewer's confirm):** post-re-key dedupe_key = `inquisition:inventory:inventory:<ulid>`, DISTINCT from VAM gestion_items; [VERIFIED] zero existing `subject_type='inventory'` gestion_items → no collision. Re-confirm before enabling emission.
6. **alert-table noise:** €0 outcomes are `NO_INDEPENDENT_PATH`=warning (no alert), so dormant today. Once Lens C/B land and produce hard refutes, alert volume rises (intended product behavior, dedup-aware). Monitor, not a blocker.
7. **Two 6h DB jobs on one host (AS24-scar adjacency):** both DB-only, `max_instances=1`, host advisory lock prevents a 2nd process. Optionally offset prosecute +30min. NOT the AS24 ban risk (that was concurrent HTTP governors).
8. **Transaction size:** `prosecute_pending` iterates; each `prosecute_claim` opens its own small `conn.transaction()` (no long-lock). `emit_claims_from_verdicts` is one INSERT-only + indexed-lookup batch, capped 200. No big-table `NOT IN` (indexed equality + LEFT JOIN on `entity.cdp_code`).
9. **Scheduler never deployed (pre-existing, F-scheduler-never-deployed):** `apscheduler_jobs` absent in prod — this job, like the other three, only ticks once the scheduler runs as a supervised service. Not introduced here; the job is exercisable directly via smoke #2.
10. **Served-data safety (reviewer CONFIRMED):** prosecute writes only `inquisition_*`/`gestion_*`/`alert`; never `vehicle`/`entity`/`verification_verdict`; router does not write `superseded_by`. Hot-path ingest untouched. Correct, not a gap.

---

## 6. Rollback

- **Disable cadence:** remove the `inquisition_prosecute` add_job block (or set the interval astronomically high). Emission is already default OFF.
- **Seeded claims:** `UPDATE inquisition_claim SET status='DECIDED' WHERE status IN ('PENDING','PROSECUTING') AND <test/scratch predicate>;` (or let them prosecute to the honest €0 verdict). No served data is affected by leaving them.
- **Emitter:** git-revert the `prosecutor.py` rewrite; the engine returns to "no live caller" (zero adjudications), the prior safe state.
- **OPTIONAL future hardening (NOT in scope):** `CREATE UNIQUE INDEX uq_claim_open_subject ON inquisition_claim(subject_type,subject_key) WHERE status IN ('PENDING','PROSECUTING');` — defer until emission is enabled (post Lens B/C) to avoid constraining manual-seed/test paths; a DECIDED claim MUST stay re-emittable, so a plain UNIQUE(subject_type,subject_key) would be wrong.
