# Gap-closure working plan (adversarial review)

All 35 gaps verified against source this session. Every one is REAL and accurately
described. Fixes land as binding decisions in MASTER_PLAN §1 (the reconciliation
authority) + targeted new sections in the source pillar. Cross-cutting reconciliations
go to MASTER_PLAN; localized methods/rules go to the owning doc.

## Routing of fixes
- GAP-1  membership-filtered recall frame      → V6 (new §4.x) + MASTER_PLAN G-A1
- GAP-2  vehicle-recall estimator              → V6 (new §) + MASTER_PLAN G-A2
- GAP-3  cross-seller over-count CI bound       → 03 §6 + V6 + MASTER_PLAN G-A3
- GAP-4  VN/km0 inventory shape + declared gap → 01 §2.1 + MASTER_PLAN seal §6 G-A4
- GAP-5  freshness SLA reconciliation (4-way)  → MASTER_PLAN C-11 (binding table)
- GAP-6  comarca seal + geo-drift detector     → V4 (new detector) + MASTER_PLAN
- GAP-7/25 classifier accuracy gold-set gate   → T08 (new §) + MASTER_PLAN P3 gate
- GAP-8  C2C volume KPI line                    → 07 KPI + MASTER_PLAN §6.3
- GAP-9  inquisitor role + egress migration/gate→ MASTER_PLAN C-2/P5/P11 + V3 note
- GAP-10 BORME adapter + closed-pop window gate → MASTER_PLAN source census + V1 gate
- GAP-11 agente_oficial numerator seal rule    → 01 §2.2 + MASTER_PLAN seal
- GAP-12 global spend ceiling + auth state mach→ MASTER_PLAN §5 + 04
- GAP-13 SEG-3/7 enumeration honesty           → 07 §6.1 gate + MASTER_PLAN
- GAP-14 event idempotency (single txn + key)  → 04 §4 + 03 + MASTER_PLAN invariant
- GAP-15 Ceuta/Melilla declared structural gap → MASTER_PLAN seal §6 + 03
- GAP-16 P0.5 spike phase                       → MASTER_PLAN phase plan
- GAP-17 PQ ClientHello cross-session identity → 02/T05 + MASTER_PLAN
- GAP-18 walled-API spike before €0 cost gate  → MASTER_PLAN P0.5 / cost gates
- GAP-19 per-request sensor cost model         → 02 + MASTER_PLAN cost gates
- GAP-20 stealth-engine reconciliation         → MASTER_PLAN C-12
- GAP-21/29 ground-truth dedup audit           → V1 (new §) + MASTER_PLAN
- GAP-22 closure window discipline (dup of 10) → folded into GAP-10 fix
- GAP-23 legal/GDPR/sui-generis threat surface → MASTER_PLAN (new §) + 07
- GAP-24 AIMD behavioral vs volumetric pacing  → 06 + MASTER_PLAN
- GAP-26 cross-platform same-car resolver       → 03 §6 (algorithm) + MASTER_PLAN G-A3
- GAP-27 ownership-first vs platform-first order→ MASTER_PLAN C-13 + 03/07
- GAP-28 C2C '00' sub-partition                → 03 §4 + MASTER_PLAN
- GAP-30 family_n origin DB enforcement        → V5 §3.1 + MASTER_PLAN
- GAP-31 0008 swap preflight + zero-downtime   → 03 §4.1 + MASTER_PLAN P0 gate
- GAP-32 Tier-1 data-axis + recipe-family      → 08 + MASTER_PLAN invariant #5
- GAP-33 v_latest_verdict materialization      → V5 §3.4 + MASTER_PLAN invariant #7
- GAP-34 scale/partition skew honesty          → 03 §9.7 residual + MASTER_PLAN
- GAP-35 eviction vs replay reconciliation     → V5 §7 + 08 + MASTER_PLAN

## Deliberately deferred (with reason) — none deferred as "not real".
Implementation-scoped items (writing the BORME adapter code, the actual gold-set
labels, the load test EXPLAIN) are deferred to their phase — the DOC gap (the missing
decision/section/gate) is what this task closes. Recorded in the "Gaps closed" section.
