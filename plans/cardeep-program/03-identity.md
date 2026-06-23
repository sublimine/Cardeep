# Resolucion de Identidad (entidad) — One verified code per real Spanish sales point, never two for one and never one for two

> This domain owns the question "who is this seller, really?". It collapses the raw `entity` rows harvested from every digital platform (each platform mints its own listing of the same dealer) into exactly one canonical identity per real-world sales point, and exposes that mapping through the single authoritative view `v_dealer_resolved` consumed by `resolve_cluster` and every entity/inventory/geo endpoint. It matters because the census product promise is "codigo unico por dealer": over-merge fuses distinct dealers into one (corrupting `/entities`, `/inventory`, `/geo`); under-merge inflates the count with duplicates. This domain is the arbiter of both failure directions, and it must do so at EUR0 with zero-false-positive certification.

## Current state (verified)

All figures below were read from real code/tests in `C:/Users/elias/projects/cardeep` on 2026-06-23, not assumed.

**Served chain (authoritative).** `migrations/0028_dealer_resolved.sql` defines `v_dealer_resolved` as a two-layer COALESCE composition: Layer 1 = B1 (`v_canonical`, run `dealer-identity-det-v1`), Layer 2 = `canonical_dedup` from the single most-recent `vam_verified=TRUE` run (`ORDER BY run_id DESC LIMIT 1`). [VERIFIED — read the SQL]. `docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md` (ADR 11, 2026-06-15) declares this the authoritative resolver and `v_resolved_dealer` (beta) as BETA DEFERRED with 0 consumers. [VERIFIED]

**Layer 1 — B1 `dealer-identity-det-v1`** (`pipeline/identity/cluster_dealers.py`): deterministic union-find with 4 edge types (name+muni, phone+muni, website+muni, Levenshtein<=2+muni in blocks <=500). Run 2026-06-22T22:42 UTC. 91,319 entities in / 58,520 clusters out / 32,799 merges. [from recon metrics; the script + run are VERIFIED to exist]

**Layer 2 — `canonical_dedup` chain** (3 runs, all `vam_verified=TRUE`):
- `canonical-dedup-deeplink-v1` (`scripts/build_canonical_dedup.py`): fuses B1 canonicals sharing a `deep_link` (union-find, anti-hub K=3, `AND e.kind <> 'particular'` at line ~191 to kill the 113k mega-cluster). 58,520 in / 4,043 merges / 54,488 deduped. [VERIFIED script + recon]
- `particular-canonkey-v1` (`scripts/build_particular_dedup.py` + `scripts/gate_particular_dedup.py`): collapses province-split particulars by definitive collision-free `canonical_key` (the platform's own seller id, re-hash-gated). 706 humans collapsed, verdict 1423, reversible via `--revert`. [VERIFIED ADR 11 §Update]
- `residual-namemuni-v1` (`scripts/build_residual_namemuni_dedup.py`): 19 straggler name+muni groups; **this is the run `v_dealer_resolved` currently serves** (newest run_id). [VERIFIED]

**Served counts.** `v_dealer_resolved` resolves the full ~368K entity universe; the dealer subset is 40,016 distinct B1 dealers after dedup (verdict 1121, `0028` header). [VERIFIED — read header]. API-served dealers (`product_stats`, `kind NOT IN (particular,desguace)` AND has servable_vehicle) = 19,144 (2026-06-23T12:33). [from recon]. Distinct non-particular dealers via `v_dealer_resolved` = 54,607. [from recon]

**Over-merge guard (the regression net).** `tests/test_dedup_invariants.py` asserts against the live served run on `postgresql://...@127.0.0.1:5433/cardeep`: 0 cross-kind (particular+dealer) components, max component_size <= 30 (real=22, the LOUZAO B1-split), max distinct normalized trade-names <= 12 (real=8), canonical = richest member within a +50-car gross drift tolerance, and served dealer count == an independent overlay recompute (relational, never a frozen constant). It also has a DB-free unit test pinning the caps between the known real maxima and the 52-member mega-cluster regime, plus a chain-coarsening invariant (a deep-link merge is never UNDONE by a later layer). [VERIFIED — read all 467 lines]

**Beta (DEFERRED, 0 consumers).** `entity_resolution` run `entity-resolution-fingerprint-v1` (`pipeline/identity/resolve_entities.py`): inventory-fingerprint Jaccard (`JACCARD_THETA=0.30` line 105) over B7 `canonical_vehicle_ulid`, reinforced by phone/website, with `ConstrainedUnionFind` (line 299) enforcing chain guard (same non-null `org_id` never merges), city-INE guard, centralita guard (`MAX_PHONE_COLLISION_K=3` line 116), cross-province-requires-fingerprint. 59,506 in / 38,555 dealers / 20,951 merges; `vam_verified=TRUE` but ~388 net-new vs served. ADR 11 defers it: composing it is a union-find transitive-closure rebuild of the CORE view for ~1% gain. [VERIFIED — read the constants + ADR rationale]

**Cross-source (NOT certified).** `cross-source-dedup-v1` (`pipeline/identity/cross_source_dedup.py`): OSM x digital dedup via phone+muni / website+muni / exact-name+muni. 688 merges, `vam_verified=FALSE`. ~13 genuine net-new dealers. [VERIFIED — recon + ADR]

**Phone authority.** `pipeline/identity/phone_es.py` is the single E.164 Spanish validator (9 digits, leading 6/7/8/9, strips +34/0034); EUR0 stdlib replacement for phonenumbers. `cross_source_dedup.py` consumes it; `resolve_entities.py` still has a legacy `_normalize_phone` that does NOT use this authority (known dual-authority debt). [VERIFIED — read phone_es.py + grep]

**Honest gaps:** (1) two known cross-kind super-canonical groups exist in the served run (a particular sharing a deep_link with a dealer) flagged for kind re-classification, NOT corrupted (ADR 11 edge case). (2) `resolve_entities.py` does not use the `phone_es` authority. (3) beta + cross-source carry real net-new merges that are computed but unserved.

## Next-level objective

Deliver **one unified union-find transitive closure over ALL VAM-verified merge edge-sets** (`{B1, canonical_dedup chain, entity_resolution-fingerprint, certified-subset of cross-source}`) serving through `v_dealer_resolved`, so that every evidence-definitive merge currently computed-but-deferred becomes served WITHOUT reintroducing a single false-positive. Measurable exit: served non-particular dealer count drops by the certified net-new merges (target: absorb the ~388 beta + ~13 cross-source genuine merges, net ~ -400 vs the 54,607 baseline), `test_dedup_invariants.py` stays green (0 cross-kind, max component <= 30), a new `er-evaluation` entity-centric cluster-precision report shows >= 0.99 precision on a 300-pair gold set, and `resolve_cluster` + `/stats` + `/entities` regress clean. The bar: a record-linkage system whose every served merge is backed by either a collision-free hard key or an EM-scored probabilistic match above a human-audited threshold — beyond what a manual analyst could certify at this scale.

## Chosen technology (EUR0)

| Tool | Role here | Why chosen over alternatives | Source | Integration effort |
|---|---|---|---|---|
| **Splink v4** (MIT) | EM-scored probabilistic re-scoring of the deferred edges (beta fingerprint + cross-source) before certification; its integrated graph metrics (density, bridges, centralization) audit each candidate super-canonical for over-merge. | Only tool with built-in cluster graph-metrics to detect over-merge with no extra code; term-frequency adjustment is exactly right for frequent dealer name tokens ("Motor", "Automoviles"); DuckDB backend handles ~400K entities in minutes at EUR0; production-proven (ABS, Harvard). | https://github.com/moj-analytical-services/splink | Medium: add as a dev/validation dependency; feed it the candidate pair table exported from `entity_resolution`/`cross-source-dedup-v1`; consume its match_probability to filter the certified subset. Does NOT replace the served union-find — it is the certification oracle. |
| **er-evaluation** (MIT) | Entity-centric cluster precision/recall/F with sampling-bias correction over a gold set, to prove the closure does not over-merge. | Pairwise metrics over-weight large clusters and mask exactly the over-merge this domain fears; entity-centric metrics measure "how many real dealers are correctly resolved". | https://github.com/Valires/er-evaluation | Low: pip dev dependency; build a 300-pair gold set from manual dealer verification; run as a CI report step. |
| **rapidfuzz** (MIT, already in tree per recon) | Deterministic Levenshtein/Jaro-Winkler for B1 fuzzy edges and Splink comparison columns. | Already a declared dependency after the Fase-1 fix; battle-tested C++ speed; no new install gate. | https://github.com/rapidfuzz/RapidFuzz | None (present). |
| **leidenalg + igraph** (GPL/ optional) | OPTIONAL fallback community detection if naive connected-components over the merged edge graph produces over-large components; Leiden guarantees well-connected communities. | Only needed if the union-find closure yields components above the size cap; keeps clusters well-connected vs Louvain. | https://github.com/vtraag/leidenalg | Low, deferred: only wire in if Phase 3 shows oversized components. |

Rejected for this domain: `dedupe`/`Zingg`/`Ditto`/`pyJedAI`/`LinkTransformer` require labelled training, Spark, or embedding model downloads (heavier, and the served merges must be hard-key or auditable-EM, not black-box). They are noted as future options for blocking/recall expansion only.

## Target architecture

**Principle (from ADR 11, preserved):** serve a merge ONLY when it is BOTH evidence-definitive AND the composition is safe. The current served chain is additive (2-layer COALESCE) because every layer is built on B1's cdp_code space. The next-level objective requires composing edge-sets that are NOT built on B1 (fingerprint, cross-source), which mandates a single transitive-closure resolver — the central new component.

```
                    ┌──────────────────────────────────────────────┐
   entity (raw) ───▶│  EDGE PRODUCERS (unchanged, each writes its    │
                    │  own run table, vam_verified flag)             │
                    │  • cluster_dealers.py      → entity_cluster B1 │
                    │  • build_canonical_dedup   → canonical_dedup   │
                    │  • build_particular_dedup  → canonical_dedup   │
                    │  • build_residual_namemuni → canonical_dedup   │
                    │  • resolve_entities.py     → entity_resolution │
                    │  • cross_source_dedup.py   → entity_cluster    │
                    └───────────────────┬──────────────────────────┘
                                        │ all VAM-verified edges
                                        ▼
              ┌─────────────────────────────────────────────┐
              │  NEW: closure builder (scripts/build_identity│
              │  _closure.py) — union-find over the UNION of │
              │  every vam_verified edge-set; canonical pick =│
              │  most-available member (tie cdp asc); writes  │
              │  identity_closure_run + identity_closure      │
              │  (new overlay table, additive, reversible).   │
              │  Splink re-scores beta+cross-source candidates │
              │  BEFORE they enter the union (certification).  │
              └───────────────────┬──────────────────────────┘
                                  │
                                  ▼
              v_dealer_resolved  (rewritten to read the closure
              run when present, else fall back to the 2-layer
              COALESCE — backward compatible)
                                  │
                                  ▼
              resolve_cluster (deps.py) → /entities /inventory
              /geo /stats   (consumers UNCHANGED)
```

Data: the closure overlay is a new additive table keyed by `(run_id, entity_ulid → super_canonical_cdp_code, is_representative, edge_provenance)`. `edge_provenance` records which producer justified each membership (B1/deeplink/particular/fingerprint/crosssource) — required for audit and selective rollback. Flow: producers run unchanged → closure builder unions verified edges → Splink+er-evaluation certify → gate flips `vam_verified=TRUE` on the closure run → `v_dealer_resolved` picks it up.

## Execution phases

Each phase is ~1 PR. The hard rule (verified convention): **all data-mutating validation runs on the ephemeral docker Postgres `:5434` (NEVER `:5433` without dry-run + golden cdp byte-identity + Ferrari + CI green first).** The live served DB is `:5433`. Every overlay write is additive; rollback drops the new run/view only.

### Phase 0 — Unify the phone authority (debt paydown, isolated)
- **Cold-start context:** `resolve_entities.py` has a legacy `_normalize_phone` that takes the last 9 digits blindly; `phone_es.py` is the validated authority. This is a latent false-merge source. No served data changes (beta is unserved).
- **Tasks:** replace `resolve_entities._normalize_phone` body with a call to `pipeline.identity.phone_es.phone_match_key`; delete the dead helper; add a unit test asserting an 11-digit extension yields `None` not a false key.
- **Verify:** `pytest tests/test_phone_es.py tests/ -k phone -q`; grep confirms only one phone authority remains: `grep -rn "_normalize_phone" pipeline/identity/`.
- **Exit:** single phone authority; all phone tests green; beta re-run (on :5434) produces <= the prior merge count (never more).
- **Rollback:** revert the file; no DB state touched.

### Phase 1 — Gold set + er-evaluation harness (measurement before mutation)
- **Cold-start context:** there is no entity-centric precision number today, only structural guards. We cannot certify a closure without a ground-truth gold set.
- **Tasks:** build `tests/fixtures/identity_gold.jsonl` of 300 manually-verified dealer pairs (match / non-match) sampled across the hard cases (chains, province-splits, cross-source, fingerprint-only); add `scripts/eval_identity.py` that loads the served run + a candidate run and prints `er-evaluation` cluster precision/recall/F.
- **Verify:** `python scripts/eval_identity.py --run residual-namemuni-v1` prints precision on the gold set; against the served run, precision must be >= 0.99 (it is already conservative).
- **Exit:** reproducible entity-centric metric; baseline number recorded in `PROGRESO.md`.
- **Rollback:** delete the fixture + script; nothing served.

### Phase 2 — Splink certification of the deferred edges (no serving yet)
- **Cold-start context:** beta (`entity_resolution`, ~388 net-new) and cross-source (`cross-source-dedup-v1`, ~13 genuine, vam_verified=FALSE) hold computed-but-unserved merges. Per ADR 11, each must be certified per-merge before serving.
- **Tasks:** add `scripts/certify_edges.py` exporting beta + cross-source candidate pairs to a DuckDB-backed Splink model (EM, term-frequency on name tokens, comparison columns: name jaro-winkler, phone exact via `phone_es`, website exact, geo muni); output a `certified_edges` table = pairs with `match_probability >= 0.95` AND backed by a hard key (phone/website) OR fingerprint Jaccard >= 0.30. Reject the rest with a logged reason.
- **Verify:** on :5434, `python scripts/certify_edges.py --dry-run`; cross-check certified count against ADR 11's hard-ID subsets (~13 cross-source genuine, beta hard-ID subset); Splink graph-metrics report shows no candidate component with bridge/density anomaly.
- **Exit:** a `certified_edges` set whose every member is hard-key-backed or high-EM; rejected pairs logged with reason; zero certified pair crosses a `kind='particular'` ↔ dealer boundary.
- **Rollback:** drop `certified_edges`; producers and served view untouched.

### Phase 3 — Closure builder + new overlay (built INERT)
- **Cold-start context:** the served view is a 2-layer COALESCE; composing fingerprint/cross-source edges (not built on B1) requires a transitive closure, not a 3rd COALESCE (ADR 11 §rationale).
- **Tasks:** add `migrations/00XX_identity_closure.sql` (table `identity_closure_run` + `identity_closure` with `edge_provenance`); add `scripts/build_identity_closure.py` doing union-find over the UNION of {B1 edges, canonical_dedup served chain, certified_edges from Phase 2}; canonical pick = most-available member (tie-break cdp asc), identical to the existing build scripts; write the run with `vam_verified=FALSE` (inert).
- **Verify (all on :5434 ephemeral):** 0 cycles; every member resolves to exactly one canonical; `python scripts/eval_identity.py --run identity-closure-v1` precision >= 0.99 on the gold set; max component_size <= 30; 0 cross-kind components; chain-coarsening holds (no served deep-link merge undone). Run the FULL `test_dedup_invariants.py` against the :5434 instance pointed at the candidate run.
- **Exit:** inert closure run exists; all invariants pass on ephemeral; net-new merge count matches the certified set (~400); golden cdp byte-identity check shows dealer cdp_codes unchanged for already-merged dealers.
- **Rollback:** the run is inert (`vam_verified=FALSE`), invisible to the view; drop the run row to fully remove.

### Phase 4 — Switch v_dealer_resolved to closure-aware + gate (the only serving change)
- **Cold-start context:** the closure run is verified-inert. The view must read it WITHOUT breaking the fallback for environments where the closure run is absent.
- **Tasks:** `CREATE OR REPLACE VIEW v_dealer_resolved` to prefer the latest `vam_verified=TRUE identity_closure_run` when present, else fall back to the existing 2-layer COALESCE (backward compatible, same output columns); add `scripts/gate_identity_closure.py` with `--gate` / `--revert` mirroring `gate_particular_dedup.py`.
- **Verify:** on :5434 first — `v_dealer_resolved` output column contract identical; `resolve_cluster` resolves every entity_ulid; `/stats` dealer count == independent recompute; full Ferrari + CI (`db-tests` job, the 830 DB-backed + 465 unit) green. Only after green: dry-run on a :5433 read-replica snapshot; then gate live with a TRUSTWORTHY verdict (two independent count paths agreeing, as particular-split did).
- **Exit:** `v_dealer_resolved` serves the closure; `test_dedup_invariants.py` green against live :5433; served non-particular dealer count drops by exactly the certified net-new merges; `/entities`/`/inventory`/`/geo` regress clean.
- **Rollback:** `python scripts/gate_identity_closure.py --revert` flips `vam_verified=FALSE`; the view's COALESCE fallback instantly restores the prior served chain. Reversible in one command.

### Phase 5 — Cross-kind reclassification follow-up (close the known gap)
- **Cold-start context:** ADR 11 records 2 served cross-kind super-canonical groups (a particular sharing a deep_link with a dealer) flagged for kind review.
- **Tasks:** add a quality probe that surfaces these 2 groups; manually verify whether the `kind='particular'` member is a misclassified dealer; if so, correct `entity.kind` (additive, via the standard kind-correction path) so the cross-kind guard reflects truth rather than masking it.
- **Verify:** after correction, re-run `test_no_cross_kind_particular_dealer_component` — it must still pass for legitimate reasons (the member is no longer a particular), not be suppressed.
- **Exit:** 0 cross-kind groups for the RIGHT reason; the guard's `live=0` is honest.
- **Rollback:** kind corrections are per-row and reversible; revert the specific `entity.kind` updates.

## Risks & mitigations

- **Over-merge from the closure (CRITICAL).** A transitive closure can chain distinct dealers through a shared weak signal (the original 113k incident). Mitigation: the union only ingests CERTIFIED edges (Phase 2 hard-key/EM gate); `test_dedup_invariants.py` (max component 30, max names 12, 0 cross-kind) runs on the candidate run on :5434 BEFORE any gate; er-evaluation precision gate >= 0.99.
- **Core-view rebuild breaks every consumer.** `v_dealer_resolved` feeds all of `resolve_cluster`/`/entities`/`/inventory`/`/geo`/`/stats`. Mitigation: identical output-column contract; backward-compatible COALESCE fallback; full Ferrari + CI + golden cdp byte-identity before the gate; one-command `--revert`.
- **Splink as a new dependency (EUR0 discipline).** Mitigation: Splink is a dev/validation-only dependency (certification oracle), NOT a runtime serving dependency; the served path remains pure SQL + deterministic union-find. MIT, DuckDB backend, no paid service.
- **Gold-set bias.** A 300-pair set can miss a failure mode. Mitigation: stratified sampling across the hard cases (chains, province-split, cross-source, fingerprint-only); er-evaluation's sampling-bias correction; the structural guards remain as a second independent net.
- **Modest value, real risk (ADR 11's own caution).** Net-new is ~400 of ~54K (<1%). Mitigation: this is framed as a completeness gain done "una vez impecable, sin prisa" with full regression; if Phase 2 certification yields fewer hard-key-backed merges than expected, serve only those and keep the rest deferred — never lower the certification bar to hit a count.

## Success metrics

- **Served correctness:** `test_dedup_invariants.py` green on live :5433 (0 cross-kind, max component <= 30, max distinct names <= 8 real / 12 cap, canonical=richest within +50 drift, served count == independent recompute).
- **Entity-centric precision:** er-evaluation cluster precision >= 0.99 on the 300-pair gold set for the served closure run.
- **Net-new served merges:** beta hard-ID subset + ~13 cross-source genuine merges served; served non-particular dealer count decreases by exactly the certified count (no silent extra merges).
- **Zero false-positive contract:** 100% of newly-served merges backed by a hard key (phone via `phone_es` / website / canonical_key) OR Splink match_probability >= 0.95 with fingerprint corroboration; every rejected pair logged with a reason.
- **Single authority:** one phone authority (`phone_es`), one served resolver (`v_dealer_resolved`), one closure overlay; `v_resolved_dealer` and uncertified runs remain non-served.
- **Reversibility:** every phase rolls back in one command; the closure gate's `--revert` restores the prior served chain with the view's COALESCE fallback.
