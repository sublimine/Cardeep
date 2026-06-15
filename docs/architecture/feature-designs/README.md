# Feature Designs — Phase 2 backlog (vetted)

Vetted, review-folded designs for the four features from `docs/recon/AUDIT_2026-06-15_PHASE2.md`.
Each design has been adversarially reviewed; every reviewer gap/missed-risk is folded **into** the
plan (not appended). All four carry a `NEEDS-REVISION` verdict that becomes shippable after the
revisions captured in each file. Live-DB facts re-verified 2026-06-15.

| # | Feature | Closes | Effort | Verdict (post-revision) | Biggest residual risk |
|---|---------|--------|--------|--------------------------|------------------------|
| 1 | [scheduler_source_expansion](scheduler_source_expansion.md) | C-cochesnet-segments-unscheduled, C-as24-unscheduled | **S** | SHIP (sentinel fix) | silence_watchdog false WARNING on the seed — neutralized by sentinel `last_fail` |
| 2 | [canonical_key](canonical_key.md) | B-canonical-key-column-empty | **L** | PROCEED | mutable muni/name → dealer backfill yield unknown (gate keeps it SAFE; under-fill self-heals) |
| 3 | [inquisition_wiring](inquisition_wiring.md) | D-inquisition-never-ran | **M** | PROCEED (corrected emitter) | €0 flood of un-self-resolvable escalations — emission default OFF + bounded |
| 4 | [price_trap](price_trap.md) | A-junk-sentinel-prices, A-km-year price junk, under-100€ | **M** | SHIPPABLE behind dry-run gate | Law-I: it actively HIDES served stock; removing the 150k floor would quarantine ~3,046 legit cars |

---

## Ranking by value / risk

**Value** = audit findings closed × operational lift. **Risk** = blast radius on served data + regression class.

1. **scheduler_source_expansion — HIGHEST value/risk.** Effort **S**, closes **two CRITICAL** findings, and revives ~10.5k coches.net segment listings + the AS24 platform surface from *never refreshing* to in-cadence with auto-repair. The only real risk (a transient false silence alert) is fully neutralized at €0 by a sentinel `last_fail` seed. Additive — touches no served data. **Do this first.**

2. **canonical_key — high value, near-zero risk (despite L effort).** Closes a CRITICAL audit finding and unlocks dedup/collision auditability + the cross-province-split signal. The **self-verifying re-hash gate makes a wrong key impossible** — the only failure mode is under-fill, which self-heals on the INSERT path. Wide edit surface (35 connectors) but mechanical, and the MVCC concern is removed by writing the column only on INSERT (never ON CONFLICT). Pure audit metadata, no served-view impact.

3. **inquisition_wiring — medium value now, high later; safe.** Closes the D-finding (the engine has never adjudicated a live claim) and corrects the meaning-corruption emit bug. But at €0 the yield is LOW (every first-pass claim → honest `REFUTED:NO_INDEPENDENT_PATH`), so the *immediate* lift is "drain seeded claims + a correct, idempotent, opt-in emitter". Fully safe (default OFF, writes only inquisition_*/gestion_*/alert, never served data). The same wiring becomes high-value the moment Lens B raw-store or Lens C live-refetch lands — no further code change.

4. **price_trap — real value, HIGHEST risk; gated.** The only feature that **actively hides served stock** (quarantine), so it carries the highest regression class (Law I — "sacarle TODO su stock"). The core statistic is sound and verified, but the corrected blast radius (~250–300 high + ~17–19k low under the 150k floor + `MAD_FLOOR=0.05`) and the "do not remove the floor" time-bomb mean it must ship **behind a one-run dry-run human review** before the cadence job is enabled. Highest care, lowest position.

---

## Recommended execution order

```
1. scheduler_source_expansion   (S, additive, 2 CRITICALs)   — ship first, immediate lift, lowest risk
2. canonical_key                (L, gated-safe, 1 CRITICAL)   — high value, wrong-write impossible; run in parallel with #1 if capacity allows (disjoint files)
3. inquisition_wiring           (M, safe, default OFF)        — wire the bridge now; flip emission ON only after Lens B/C
4. price_trap                   (M, gated, served-surface)    — last: build + dry-run review + then enable cadence
```

Rationale for the order beyond value/risk:
- **#1 and #2 are file-disjoint** (scheduler/connectors-health vs codes.py/INSERT-cols + backfill) and both additive/gated-safe, so they can land in parallel. #1 first because it's S-effort and unblocks live cadence.
- **#3 before #4** because inquisition is safe-by-default (no served writes) and its corrected emitter removes a latent meaning-corruption bug, whereas #4 touches the served surface and needs a human dry-run gate — best done last when the cheaper, safer wins are banked.
- All four share the migration slot **0039**; only **one** can take it. If shipping in this order, assign **0039 = scheduler seed**, then renumber the others sequentially (canonical_key backfill → next; price_trap optional servable-view guard → next). Confirm the next free number with `python -m scripts.migrate verify` before each (newest applied is **0038**).

---

## Cross-cutting notes verified on the live DB (2026-06-15)

- Newest applied migration = **0038**. The four designs collectively want **0039**; only one may claim it — sequence per the order above.
- `entity.canonical_key` is **100% NULL** (391,944 rows; filled=0). `inquisition_verdict` live tuples = **0** (never adjudicated). Both confirm the findings are still open.
- No design introduces a new `source_key` except via the **seeded** `coches_net_segments`/`as24_wholesale` rows in #1 (the autocasion-orphan lesson is honored: seed `source_health` + register in `REGISTRY` together).
- No design writes served data destructively: #1 is additive cadence rows; #2 is audit-only metadata on INSERT; #3 writes only inquisition_*/gestion_*/alert; #4 only opens reversible quarantine items (never NULLs `vehicle.price`).
- The scheduler is **not yet deployed as a service** (`apscheduler_jobs` absent in prod, F-scheduler-never-deployed) — #1, #3, and #4's cadence jobs are inert until that separate work lands, but each is exercisable directly via its smoke command.
