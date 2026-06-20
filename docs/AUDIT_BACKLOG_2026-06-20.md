# CARDEEP Blueprint Gap Backlog — Autonomous TDD Loop (€0, reversible/cycle)

Filter applied: `eur0_reversible_now=true` AND `gated==""`. Deduped across P01–P14. Ranked by impact/effort, favoring honesty/correctness holes (anti-maquillaje, VAM) and built-but-dead wiring.

---

## TOP 8 (execute in order)

### Rank 1 — P14: Eradicate hardcoded dev credentials (`cardeep_dev_only`)
- **Why it matters:** Hardcoded DSN secrets across 11+ files = a CRITICAL security hole that ships prod with a dev password; fail-fast in prod is pure correctness.
- **RED test:** `tests/test_no_hardcoded_dsn.py` — `CARDEEP_ENV=prod` + no `CARDEEP_DSN` set → `import pipeline.discover_schedule` must raise `RuntimeError`; plus a repo-grep assertion that `cardeep_dev_only` appears ONLY in `.env.example`.

### Rank 2 — P06-S1: `canonical_key` does not validate CIF/NIF nor normalize phone
- **Why it matters:** Identity is minted over corrupt CIFs → denominator inflation; the validated primitives (`canonical_tax_id`, `phone_match_key`) already exist but are dead — pure wire-up of an anti-maquillaje hole. (Note: full historical re-key is the GATED twin; the *generator* fix on new keys is reversible.)
- **RED test:** `tests/test_canonical_key_validates.py` — feed an invalid CIF → assert `canonical_key()` does NOT emit `cif:<garbage>` but falls back to name+muni; feed a valid phone → assert it routes through `phone_match_key()` normalization.

### Rank 3 — P03-S1: `record_run` ignores ban/challenge verdict (breaker blind to semantic bans)
- **Why it matters:** `ban_detector.Verdict` is computed in `fetch.py` but never reaches the breaker → fleet keeps hammering a banned host on HTTP 200. Built-but-dead signal; correctness + antidetección.
- **RED test:** `tests/test_breaker_reacts_to_verdict.py` — call `record_run(http_status=200, verdict=Verdict.BANNED)` N times → assert breaker opens independent of `http_status`.

### Rank 4 — P02-S1: Load DIRCE CNAE-451 external census (triangulation anchor)
- **Why it matters:** Without the official anchor, triangulation returns `pending` and the national seal can never gate honestly; it is the denominator ground-truth for the whole exhaustiveness claim.
- **RED test:** `tests/test_exhaustiveness_triangulation_loaded.py` — after dropping `countries/ES/census/dirce_cnae451.csv`, assert `triangulation.status()` contains `'loaded'` and reports ≥52 anchors.

### Rank 5 — P05-S6: Break facet→wholesale coupling + pluggy registration
- **Why it matters:** Facets import from `*_wholesale` (4 hits) and scheduler hardcodes a `SourceEntry` dict — exactly the coupling that let the S0 arity bug ship. Reversible refactor toward contract-enforced discovery.
- **RED test:** `tests/test_no_wholesale_imports_in_facets.py` — AST/grep assertion that `from *wholesale import` count == 0 in facet/segment modules; plus a pluggy-registry discovery test asserting each connector is found via hookimpl, not the dict.

### Rank 6 — P08-S5a: Universalize `reconcile_gone` (only ~3/63 source_keys emit GONE)
- **Why it matters:** Most sources are de-facto append-only → dead stock never marked GONE = silent freshness lie. The coverage-gate exists but is never armed; wiring closes a VAM honesty hole.
- **RED test:** `tests/test_reconcile_gone_universal.py` — for each registered wholesale/platform connector, assert it calls `reconcile_gone` post-ingest with a non-None `min_coverage`; and that the coverage-gate ABORTS GONE emission when `coverage < floor`.

### Rank 7 — P07-S3 / P06-S2 / P11-S7 (DEDUP): promote `entity.cdp_code` UNIQUE INDEX → UNIQUE CONSTRAINT
- **Why it matters:** Three points filed the same gap. INDEX is not FK-able, blocking `resolved_cdp_code` FKs; data already verified 0 duplicates, so the additive migration is low-risk and unblocks identity FK integrity. (The *prod apply* is the gated step; authoring the guarded, idempotent migration is reversible.)
- **RED test:** `tests/test_cdp_code_constraint.py` — apply migration on ephemeral DB → query `information_schema.table_constraints` returns `UNIQUE` for `uq_entity_cdp_code_*`; pre-flight duplicate guard RAISEs if any dup injected.

### Rank 8 — P12-S1: Backend `/facets/{scope}` global facets endpoint
- **Why it matters:** Frontend filters only the loaded page → counts lie vs national reality; this endpoint is the correctness anchor (count must match `/geo/seal` numerator) and unblocks the whole P12 facet refactor.
- **RED test:** `tests/test_api_facets_scope.py` — `GET /facets/venta?prov=28` → `meta.count` equals the Madrid numerator from `/geo/seal`; envelope `{ok,data,error,meta}` shape asserted.

---

## REMAINING ELIGIBLE (rank 9+, terse)

Ranked impact/effort within tier.

**Anti-maquillaje / correctness, small:**
9. P14-S2 dedup note — covered by Rank 1.
10. P09-S5(b): persist PrecisionGate fields from prosecutor → `inquisition_verdict` (S, wiring already-built quorum fields). *Eligible.*
11. P13.1: `conftest.py` + `pyproject.toml` (markers, cov source) — unblocks the whole test loop. **Consider promoting near top** if the loop can't run cov without it.
12. P13.9 / P9: instrument scheduler ban-rate/silence Prometheus counters (S).
13. P03-S6 README zendriver AGPL note (S, LOW) — honesty doc fix.

**Schema/migration authoring (reversible authoring; prod apply gated):**
14. P02 migration 0051: add `method_quorum/completeness_pct/finite_cap/open_pop_flag/triangulation_verdict` columns (S, nullable additive).
15. P08-S4: additive `TEXT_CHANGE` event_type + `title_hash/desc_hash` + diff branch (M).
16. P07-S1/S2 backfill+atomic-swap pre-flight guard authoring (M).

**Engines/interpreters (medium build, no install needed beyond BSD libs):**
17. P04 design-doc: field_map execution model (M, document-first — blocks S2/S3).
18. P04-S2 `extract/structured.py` (extruct) + P04-S3 `extract/selectors.py` (parsel) + P04-S4 rewrite `replay()` to interpreter. *Cluster; do after Rank 17. Removes the admitted "interpreter NOT claimed" gap.*
19. P04-S6 `extract/heal.py` (Anansi 4 strategies) — after S2/S4.
20. P01 cluster: `_dealer_confirm.py` (S1) → `wallapop_census.py` (S4) → `fsq_places.py` (S5) → wire S6 registry + lists.py taxonomy. *All €0/reversible; dedups the "JSON-LD parsing duplicated" gap into S1.*
21. P05-S4 `_core/ingest_engine.py` unified `_ingest_window` (L) + P05-S5 COPY path + P05-S7 contract-test CI gate.
22. P02-S2 `estimators_finite.py` (Doerfler cap) + P02-S5 quorum validator + P02-S7 resolved-vs-splink reconciliation + P02 CLI flags + 7 test files.
23. P06-S3 `identity_authority` table (lineage) + P06 beta-run publish decision.
24. P09-S3 Lens F reconcile (ABSTAIN cost-zero path) + P09-S7 ODCS `contract.py` + Lens/S6/S7 tests.
25. P10-S1 `scheduler_heartbeat` + `liveness_beat` + watchdog wiring + P10 systemd units + P10-S4 OTel/Prometheus.
26. P11 cluster: S6 cursor/keyset pagination, S2 `/coverage/map`, S5 SSE delta stream, S8 BFF (kill `VITE_API_KEY` from bundle — security), S9 Schemathesis CI.
27. P12 cluster: S2 facets frontend (DuckDB-WASM/TanStack), split map+list `/explore`, price-outlier sanity (`price_sanity.py`).
28. P13: seed.sql fixture, behavioral-suite CI job (+pytest-cov/diff-cover), Dockerfile multi-stage, LiteLLM config, Grafana dashboards.
29. P14: LICENSE + SBOM/license-gate CI + `test_arch_no_agpl_in_api.py`; PRIVACY/LIA/tos_ledger docs + opt-out entity columns + `test_optout_excludes_entity.py`.
30. P10-S2: E2E test that `gestionador_detect_all_job` opens real `gestion_items` (LOW — detectors already live; just prove CI runs it).

---

## SHELFWARE RISK (built but no real consumer — wire or delete)

- **P03 `PostgresRateLimiter` / `ratelimit_pg.py`** — exists, `test_governor_distributed.py` passes, but `governor()` is instantiated with `backend=None`; never wired at cosecha startup. Dead until scheduler wires it. *(eligible, Rank-cluster 25.)*
- **P03 ban verdict** — `Verdict` enum computed, never propagated (Rank 3).
- **P06 `canonical_tax_id` + `phone_match_key`** — validated primitives, not called by `codes.py` (Rank 2).
- **P06 `splink_merge.py`** (~250 lines) — feeds MSE denominator only, never identity served; risk of two divergent splink paths. *(served path is GATED-GASTO.)*
- **P08 `delta_photo.py`** — full PDQ/pHash code, never invoked in hot path (backfill GATED-GASTO; the persistence-on-refresh wiring is partly eligible once egress unlocks).
- **P10 9 detectors** — live, but `detect_classifier_drift` / `detect_geo_resolution_drift` are `[]` stubs (GATED); the other 7 run — verify CI actually executes the dry-run test.
- **P02 `splink_merge` resolved/splink dual numbers (46,963 vs 106,864)** — emitted "sueltos" with no reconciliation → maquillaje risk until S7 bridge lands (Rank-cluster 22).
- **P09 `detect.py` stubs returning `[]`** — present in DETECTORS list but inert; flag so they aren't counted as "9 live".

---

## STAGED / OWNER (gated — do NOT enter the €0 loop)

- **GASTO (install/egress/spend):** P02-S3 MSETools+SparseMSE, P02-S4 EconML/DoubleML DR-ML, P02-S6 iNEXT; P04-S5/S8 Ollama mintero+XGrammar; P06-S4 pgvector/model2vec, S5 Splink-identity, S7 photo_hash backfill, S8 LLM-CER; P07-S5 SeaweedFS, S6 CLIP embeddings; P08-S3 1.68M photo egress + CLIP; P09-S3 Lens C re-fetch, S6 NannyML golden_set; P10-S3 rung2 re_receta (Ollama), S5 pyrate PostgresBucket; P11 Redis (S3/S4/S10), Granian; P12-S3/S4/S5/S6 valuation motor + ECharts/deck.gl; P13.6 Terraform/Hetzner; P14-S4 Protego, S6 datacontract-cli, S7 Marquez.
- **IRREVERSIBLE-PROD:** P06-S1 historical cdp_code re-key, S2 cdp constraint *apply*, S6 union-find served cut; P07-S7 PG16→18 upgrade, schema applies on live DB; P02-S8 composite national seal apply; P09-S5 verdict-enum migration apply; P08 PHASH_HAMMING_MAX recalibration (retroactive timeline).
- **LEGAL:** P12 Kaggle dataset license verification (calibration-only).
- **DESIGN-GATE:** P05 `group_rentacar_vo` bespoke-vs-unify decision; P05 schema-drift sentinel.

---

**Loop note:** Start with Rank 11 (P13.1 conftest/pyproject) only if your runner cannot collect coverage — it is the meta-prerequisite for "ship one verified change per cycle." Otherwise begin at Rank 1.