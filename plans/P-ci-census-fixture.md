# Plan — CI synthetic census fixture (FASE 1, recover the census-dependent test block)

> Verified scoping from workflow w79zq4bpo (6 read-only agents, line-by-line). The CI `db-tests` job
> runs against an ephemeral, migrated, geo-seeded Postgres with NO census. A single idempotent CI seed
> script recovers ~95-115 tests across ~10 files + parts of 3. Magnitude-floor tests stay local-only.
>
> METHOD: build incrementally, batch by batch. CI is the ONLY faithful verifier (local tests hardcode
> :5433 = live dev DB, so local runs give FALSE greens). For each batch: extend the seed → remove that
> batch from tests/ci_local_only.txt → push → confirm CI db-tests green → next batch. Never assume.
> Experiments use ephemeral docker :5434 (NEVER :5433).

## Seed script: scripts/seed_ci_fixture.py (NEW, idempotent, additive, ON CONFLICT DO NOTHING)
Runs in the db-tests CI job AFTER `migrate up` + geo-seed. Inserts a small synthetic census. All
entity_ulid must match `^[0-9A-HJKMNP-TV-Z]{26}$` (Crockford-26); cdp_code per the tests' constants.

## OLA 1 — generic/mechanical (~62 tests, low fragility) — DO FIRST
- test_evict: 1 generic entity (province_code='28').
- test_entity_muni_province_invariant: 1 entity (muni='28079', prov='28').
- test_emit_gone_events: 1 entity + 1 entity_source + 1 vehicle(available, price>0).
- test_reconcile_gone_coverage: self-seeds in txn+rollback (verify it just needs schema).
- test_servable_status_filter (mechanical 3): 1 servable vehicle + 1 servable dealer.
- test_dedup_invariants (DB ~9): EXACTLY 1 canonical_dedup_run vam_verified=TRUE + small components.
- test_api_seal + test_province_seal_view: denominator_estimate(venta, 52 prov) via
  scripts/load_denominator_provincia.py (in-repo CSV) + ~52 venta entities w/ available vehicle +
  52 desguace entities w/ entity_source('dgt_cat'). v_dealer_resolved COALESCEs to self (migr 0028) →
  no dedup run needed for self-canonical counting.
- test_api_exhaustiveness: 1 synthetic exhaustiveness build_run_id (grand-national NULL/NULL + 4
  segments). Only asserts coverage_lower<=point<=1 and sealed⇒cov_lower>=threshold.

## OLA 2 — exact-cdp-code coupled (~33 tests, higher fragility) — DO AFTER OLA 1
- test_api_pagination: cdp PLATFORM='CDP-ES-00-EMRH0TWQ', DEALER='CDP-ES-28-27JX9YZC', >=20 vehicles
  + >=20 vehicle_event on dealer, >=11 platform_listing on platform, >=20 entities prov 28.
- test_api_canonical: cluster ALIAS='CDP-ES-50-N675XHMM' → CANONICAL='CDP-ES-50-8SX3KPR5' (n_members=2)
  via a vam_verified entity_cluster_run + 2 entity_cluster rows.
- test_api_ratelimit_cache (Section B): >=10 dealers prov 28 + 1 dealer-with-stock (exact code).

## STAY LOCAL-ONLY (honest magnitude floors — a small fixture cannot fake them)
- test_dedup_integrity.py — line 88 assert 30_000<=canon<=60_000 (real ~40k B1 canonical dealers).
- test_api_gaps.py — dealers<raw_non_particular, unique<raw (real vehicle aliases), within>global_only
  cross-dealer car, cluster 5→1 '07-AVYXV1NM'; + GAP-2 uses `docker exec cardeep-pg` (absent in CI).
- test_country_coexistence.py::test_es_entity_count_at_or_above_baseline — line 81 >=431215 (real census).
- test_km_enrichment.py TestKmCollectionLive (3) — real per-source KM distributions.
- test_inquisition_lenses_db.py Lens D test_coverage_desguace_dgt_cat_1292 — EXACTLY 1292 desguace rows.
- test_dealerprobe_concurrent / fetch_cascade / fingerprints / inquisition_engines/lenses/prosecutor /
  quorum / engine_license — network/external-engine; test_virtual_display — needs xvfb env.

## STATUS
- [x] OLA 1 batch A — DONE 2026-06-23 (commit 8bd745c): seed_ci_fixture.py (25 dealers prov28 + source +
      25 vehicles) recovered evict / emit_gone / entity_muni_province / reconcile. db-tests 790->830, no
      regression to the 790. servable-mechanical deferred to batch B.
- [ ] OLA 1 batch B (dedup_invariants served-run + components; servable_status_filter mechanical)
- [ ] OLA 1 batch C (seal + province_seal + exhaustiveness + denominator loader)
- [ ] OLA 2 (pagination + canonical + ratelimit-cache; exact cdp_codes + volume in prov 28 — seed already
      has 25 dealers prov28, extend with the exact cdp_code constants)
