# CARDEEP — 10 · The Verification Stack (VAM → Deep Ledger → Gestionador → Inquisition)

> **CARDEEP NEVER SELLS A LIE.** This document is the A-Z of the verification machinery:
> the four layers that decide whether a number CARDEEP holds may be served as *verified*.
> It supersedes the light `05-VERIFICATION-VAM` for everything above the count-quorum.
>
> Discipline: every artifact named here was read in the live repo/DB. `[VERIFICADO]` = read
> the source; `[ASUMIDO]` is labelled. The runbook (`RUNBOOK.md`) documents the *harvest* side
> (which connectors are VAM-validated and serve today); THIS document documents the *verifier*
> side (the machinery that judges them). They are complementary, not duplicates.

---

## 0. Why four layers

A single count-quorum ("do ≥2 paths agree on a number?") is necessary but not sufficient: it
cannot catch a lie every path shares (a silent cap all counters inherit, a stale snapshot all
paths read, a fabricated field no path re-fetches, a "100%" with no denominator). Each layer
below closes a class of blind spot the layer under it cannot see. All four are **€0** (DB +
pure compute); the only harvest-gated piece is the live re-fetch lens (§4, Lens C).

```
L1  VAM (0004)            producer-side optimistic count-quorum  — the fast pre-check
L2  Deep Ledger (0026)    DB-enforced quorum + audit hash-chain + denominator + TTL (δ)
L3  Gestionador (0031)    anomaly detection + state machine + routing (the "manager")
L4  Inquisition (0032)    adversarial verifier chain: default-REFUTED, orthogonal lenses
```

A claim flows: VAM marks it optimistically → the Deep Ledger persists it under a DB invariant →
the Inquisition re-prosecutes it adversarially → a non-clean verdict is routed by the
Gestionador to fix / research / quarantine / escalate. The Inquisition verdict is the ruling;
the VAM verdict is only an opinion.

---

## 1. Layer 1 — VAM (`migrations/0004`, `pipeline/verify.py`) [VERIFICADO]

The original count-quorum. `record_count_verdict(conn, subject_type, subject_key, claim, paths,
tolerance, claim_kind, expires_in)` is the **sole writer** of `verification_verdict` (every
connector + `discover.py` + scripts call it; it is the only direct INSERT). Rule: TRUSTWORTHY
when the modal value is supported by ≥2 paths, no rival reaches ≥2, and the primary/landed value
agrees — else REFUTED/UNVERIFIED. Posture: **optimistic**.

It remains the cheap producer-side pre-check. Everything it marks TRUSTWORTHY is re-prosecuted by
the Inquisition (§4) before that value is served as verified. See `RUNBOOK.md` §8 for the 45
connector verdicts this layer produced.

---

## 2. Layer 2 — Deep Ledger (`migrations/0026_verification_deep.sql`) [VERIFICADO]

Hardens the VAM verdict into a tamper-evident, DB-enforced ledger. Additive to `verification_verdict`:

- **DB-enforced quorum** — `chk_trustworthy_needs_quorum`: a TRUSTWORTHY verdict requires
  `quorum_n ≥ 2 ∧ family_n ≥ 2 ∧ origin_n ≥ 2`, where the three columns are `GENERATED ALWAYS …
  STORED` from `independent_values` / `verifier_paths` (functions `cdp_modal_cluster`,
  `cdp_distinct_families`, `cdp_distinct_origins`). The constraint is `NOT VALID` — it
  grandfathers the ~1039 legacy seals (B1/β/B7 wrote `verifier_paths` as strings/NULL) without
  re-validating them, while every NEW TRUSTWORTHY must satisfy it. A lie cannot be written.
- **Audit hash-chain** — `verdict_audit` (append-only; UPDATE/DELETE raise via
  `cdp_audit_immutable`). Trigger `cdp_audit_append` chains `chain_hash = sha256(prev || payload)`
  over subject/claim/verdict/values/quorum_n/family_n. NOTE: it does **not** hash `expires_at` or
  `superseded_by` — so the cadence (§2.1) can set them without breaking the chain.
- **Denominator** — `denominator_estimate` (Chapman/Chao2: n1/n2/m2 → point_est + CI). The basis
  for any "X% coverage" claim; an Inquisition coverage verdict cites the exact row it used.
- **Read-only role** — `cardeep_inquisitor` (`GRANT SELECT` only): the verifier physically cannot
  write the rows it judges (independence by construction).

### 2.1 The cadence (δ — `pipeline/verify_ttl.py` + `pipeline/ops/inquisition_schedule.py`) [VERIFICADO]

A verdict is a snapshot of a moment; data drifts. The cadence gives operational verdicts a TTL:

- `verify_ttl.ttl_for(claim_kind)` → `timedelta` (count 7d, freshness 1d, coverage/field_fill 14d,
  existence/denominator 30d; unknown → count default, never NULL). `record_count_verdict` sets
  `expires_at = now() + ttl` on NEW verdicts. **Grandfathered seals keep `expires_at = NULL`
  (eternal)** — they re-verify on re-harvest, not by wall-clock (a backfill would flood the queue
  with re-verifications that cannot run at €0).
- `inquisition_schedule.find_expired` (`expires_at < now() ∧ superseded_by IS NULL`, uses
  `idx_verdict_expiry`) → `schedule_reverification` opens a `stale_verdict` gestion_item in the
  RESEARCH lane via the Gestionador (§3). **€0** (reads + upserts; it QUEUES re-verification, never
  runs harvest). CLI: `python -m pipeline.ops.inquisition_schedule`. Idempotent by dedupe_key.

---

## 3. Layer 3 — Gestionador V4 (`migrations/0031_gestion.sql`, `pipeline/gestionador/`) [VERIFICADO]

The "manager": it detects anomalies, opens managed items, and routes them through a state machine.

- **Tables** — `gestion_item` (dedupe_key UNIQUE; INSERT … ON CONFLICT DO UPDATE = MVCC-safe
  UPSERT) + `gestion_transition` (append-only).
- **State machine** (`route.py`) — `OPEN → ROUTED → IN_PROGRESS → REVERIFYING →
  RESOLVED/QUARANTINED/ESCALATED/WONT_FIX/REOPENED`. **RESOLVED requires a `verdict_id`** ("no
  independent recheck → no close"). Lanes: AUTO_FIX / RESEARCH / QUARANTINE / ESCALATE_GASTO /
  ESCALATE_OWNER (each with an SLA).
- **7 €0 detectors** (`detect.py`) — count_inflation, silent_cap, field_loss, staleness,
  fabrication, coverage_gap, price_trap — + 2 declared stubs (geo-drift, classifier-drift =
  golden-set/scraping, out of €0). A demo dry-run over the live DB surfaced 1,610 real anomalies.
- Tests: `tests/test_gestionador.py` (56, incl. 2 real-DB integration tests that bind
  `open_or_refresh` through real asyncpg — the mocked unit tests once hid a shipped crash where
  `str(timedelta)` was passed as an INTERVAL parameter; the real-DB tests guard that class now).

The Inquisition's Manager Router (§4) and the cadence (§2.1) both open their items through this
layer — there is one queue, not three.

---

## 4. Layer 4 — V3 The Inquisition (`migrations/0032_inquisition.sql`, `pipeline/inquisition/`)

The adversarial verifier chain. Spec: `docs/architecture/verification/V3-INQUISITION.md` (3 laws,
5 lenses, independence gate §4, quorum §5, manager router §7, denominator §6). Built in four
blocks, all €0, all gated against the live DB.

### 4.1 ε1 — Schema + DB invariant [VERIFICADO]
`inquisition_claim` (the §2.1 envelope; producer_state JSONB carries Law II's 4 dimensions;
indexed PENDING work-queue) · `inquisition_skeptic` (per-skeptic audit; lens + indep_distance) ·
`inquisition_verdict` with **`trustworthy_needs_independence`**: `verdict <> 'TRUSTWORTHY' OR
(indep_score ≥ 2 ∧ assert_n ≥ 2 ∧ refute_hard_n = 0)`. Laws II+III become a database invariant —
a TRUSTWORTHY lie cannot be persisted even by a buggy prosecutor. FK `denom_estimate_id →
denominator_estimate(id)` makes a coverage verdict auditable.

### 4.2 ε2 — The engines (pure, `independence.py` + `quorum.py`) [VERIFICADO]
- **Independence (§4)** — `indep_distance(a,b)` = differing dims (0..4); `admit` = D(s,P) ≥ 2;
  `indep_score` = min over asserting pairs. Director decision (sealed): INDEP over ALL asserting
  skeptics (the strict reading) when §4 is internally ambiguous — the strict reading can only
  over-refute, never manufacture a false TRUSTWORTHY (Law I).
- **Quorum (§5.4)** — `decide(...)` implements the 6-step rule exactly, with the §5.5 false-veto
  guard (a deterministic hard refute vetoes alone; a lone non-deterministic one does not; two
  independent ones do). Tolerance EXACT vs DRIFT (`max(τ_rel·v, τ_abs)`, τ_rel=0.005, τ_abs=50).
  `QuorumResult` maps 1:1 onto `inquisition_verdict`. Every spec worked example reproduces.

### 4.3 ε3 — The five orthogonal lenses (`lenses.py`, `_lens_a.py`, `_lens_d.py`) [VERIFICADO]
Each lens measures the claim's true value by an orthogonal path and returns a Skeptic (StateTuple
D≥2 from the producer). Routed per the §3.6 matrix by `run_applicable_lenses`.

| Lens | What it measures | €0 status |
|---|---|---|
| **A** re-query | recompute via a different SQL aggregation over the canonical DB | €0 real |
| **D** cross-source | corroborate from a different source already in the DB (dgt_cat, wallapop, denominator) | €0 real (ABSTAIN if no witness) |
| **E** batch-hash | SHA-256 over the canonical set; empty-delta → REFUTE_HARD deterministic | €0 real |
| **B** raw-recount | recount from raw evidence bytes at evidence_uri | ABSTAIN (no raw store yet) — flips on harvest |
| **C** live re-fetch | re-fetch live through a separate network identity (the gold lens, D=4) | **harvest-gated** stub, ZERO network calls |

`measured_value` is a canonical string (`"1292"` not `"1292.0"`) so the quorum's modal Counter
never splits a true quorum.

### 4.4 ε4 — Prosecutor + Manager Router (`prosecutor.py`, `router.py`) [VERIFICADO]
- `prosecute_claim` — **atomic** (whole prosecution in one `conn.transaction()`: poll PENDING →
  `run_applicable_lenses` → persist skeptics → `decide()` → persist verdict → route → DECIDED; on
  failure the claim reverts to PENDING, no PROSECUTING zombie). `prosecute_pending` polls the queue.
  CLI: `python -m pipeline.inquisition.prosecutor`. `emit_claim_from_verdict` is the §9 harvest
  bridge (built, not auto-run).
- **Manager Router (§7)** — a 13-row deterministic table (verdict + reason_code → action / lane /
  quarantines / severity). Opens gestion_items through the Gestionador's `open_or_refresh` and
  writes the existing `alert` table for critical routes — it reuses Layer 3, no new queue.
  silent_cap→AUTO_FIX, fabrication/empty_delta→QUARANTINE, coverage→RESEARCH,
  NO_INDEPENDENT_PATH→ESCALATE_OWNER, …

Tests: `tests/test_inquisition_{schema,engines,lenses,lenses_db,prosecutor}.py` — **139 pass**.

---

## 5. The €0 / harvest boundary (what is built vs what waits)

**Built and €0-complete:** all four layers, end to end, tested. The machinery to detect, judge,
route, and re-verify exists and runs against the live DB today.

**Harvest-gated (honestly deferred, declared):**
- **Lens C** (live re-fetch) — needs scraping + a separate egress identity (different JA3 / IP
  pool). It is the only lens that differs on all four producer dimensions, so at €0 most claims
  reach only 1 independent asserting lens → `REFUTED:NO_INDEPENDENT_PATH`. This is the **honest**
  state, not a gap masked: CARDEEP confesses it cannot yet prove these by an independent path.
- **G5** (the 5th completion gate) — needs a 2nd harvest run to observe delta.
- **Claim emission** — running `emit_claim_from_verdict` over the 1044 VAM verdicts is a
  harvest-phase decision (it would flood the queue with un-runnable re-verifications at €0).

## 6. Declared debt

- Lens A lacks a `delta` sub-handler (ABSTAINs honestly until the event-store / SU-A4 delta lands).
- `entity_field`/`cif` field claims need lenses B/C/D (harvest-gated); A-only yields INDEP<2 →
  REFUTED (honest, never a false TRUSTWORTHY).
- `superseded_by` is respected by the cadence (excludes superseded rows) but not yet written on
  re-verification close — a post-RESOLVED step for the harvest phase.
- The Lens-C egress CHECK (`egress_id(skeptic) <> egress_id(producer)`) is documented in 0032 but
  deferred (nothing live to enforce at €0).

---

> **The promise, made structural.** No load-bearing value is served as *verified* unless ≥2
> mutually-independent lenses asserted it and no un-vetoed hard contradiction exists — enforced as
> a DB invariant. Every refuted claim is routed to an action, never silently dropped. "100%" is
> un-assertable without ≥3 orthogonal sources and a denominator whose CI supports it. CARDEEP
> confesses every gap it cannot close and refuses to serve a single number it cannot prove by a
> path other than the one that made it.
