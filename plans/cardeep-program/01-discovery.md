# Descubrimiento / Universo — Find, index, order and locate every car point-of-sale in Spain that has a digital footprint, then prove the census is exhaustive.

> This domain owns the **left edge of the CARDEEP pipeline**: the set of source adapters and the continuous scheduler that ingest *entities* (car dealers, used-car traders, garages, scrapyards, OEM VO networks, chains, platforms) into the `entity`/`entity_source` tables, plus the Mark-Recapture (MSE) exhaustiveness framework that *proves* how much of the real Spanish universe we have captured. It does not extract vehicles or prices (that is `extraction`), it does not resolve duplicate identities (that is `identity`), and it does not serve data to the API (that is `serving`). It matters because every downstream number is meaningless without a defensible denominator: the census is only "national 100% digital footprint" if Discovery can show, per province × segment, that captured ≈ estimated-true. Scope is fixed by the owner: **digital footprint only** — a workshop with no web presence has no extractable inventory and is explicitly out of scope; our job is to find, index, order and locate everything that *does* exist online, for absolutely everyone. Budget is strict **€0**.

---

## Current state (verified)

All figures below were read directly from the repo at `C:\Users\elias\projects\cardeep` (branch `main`) and from the recon DB snapshot. Source path or query is given for each. Items I could not re-run against the live DB in this session are marked `[RECON]` (taken from the orchestrator-supplied recon, which queried the live `:5433` DB).

### Ingestion surface (verified by reading source)
- **25 adapters** registered in `ADAPTERS` dict — `pipeline/discover.py` lines 48–74. Verified the full key list: `dgt_cat, oem_kia, oem_mg, oem_byd, oem_skoda, oem_dacia, oem_hyundai, oem_mercedes, oem_seat, osm, aedra, acevas, aecs, autocasion_census, motor_es_census, ocasionplus_census, flexicar_census, overture, dork_municipal, borme_cnae, axesor_cnae, graph_recursive, paginas_amarillas, autoscout24_census, collapse_invisible`.
- **5 scheduled vectors** in `DISCOVERY_REGISTRY` — `pipeline/discover_schedule.py` lines 65–84: `borme_cnae` (24h, orthogonal), `collapse_invisible` (168h, non-orthogonal), `overture` (720h, orthogonal), `graph_recursive` (720h, non-orthogonal), `dork_municipal` (2160h, orthogonal, **gated** on `CARDEEP_SEARXNG_URL` — the scheduler will *not* auto-run dork without a quota-free SearXNG endpoint, to avoid a DDG ban).
- **Contract** `DiscoveredEntity` — `pipeline/sources/base.py` lines 7–25: 18 fields incl. `kind, source_key, source_ref, cif, cnae, province_name, municipality_name, lat, lon, website`. `SourceAdapter` exposes `fetch()` + `declared_count()` (the latter feeds the VAM quorum).
- **VAM gate**: `_upsert` in `discover.py` geo-resolves province/municipality to INE codes (province → municipality → unambiguous-city fallback → lat/lon nearest-province fallback), mints `cdp_code`, and atomically upserts `entity` + `entity_source`. The triple-quorum verdict (declared == fetched == DB) is recorded via `record_count_verdict` (`pipeline/verify.py`).
- **DSN default is `:5433`** — `discover.py` line 46: `postgres://cardeep:...@localhost:5433/cardeep`. This is the **live** port. `docker-compose.yml` line 24 maps `127.0.0.1:5433:5432`. There is **no `:5434` dry-run service in compose yet** — it must be added as an ephemeral container (see Phase 0).

### Coverage / denominator (`[RECON]`, queried against live `:5433`)
- `entity` total: **450,619**; `status='active'`: **439,297**.
- Active **non-particular** (PoS candidates): **80,146**.
- Active non-particular with a confirmed **website** (true digital footprint): **11,428**.
- Active non-particular seen **only** via a non-orthogonal MKT signal (no orthogonal evidence): **54,339** — these are the weakest captures.
- Active with `province_code` NULL: **1,091**; with `municipality_code` NULL but province known: **48,777**. Province coverage: **52/52** provinces present.

### Exhaustiveness framework (verified: code read; row counts `[RECON]`)
- Schema `migrations/0048_discovery_capture.sql`: `discovery_list`, `discovery_capture`, `exhaustiveness_estimate`, view `v_exhaustiveness_seal`. Row counts `[RECON]`: `discovery_capture` **910,153**, `exhaustiveness_estimate` **2,934**.
- Taxonomy `pipeline/exhaustiveness/lists.py`: **7 orthogonal lists** — `ORTHOGONAL_LISTS = ("GEO","CENSUS","DGT","ASSOC","OEM","DORK","REG")` (line 49). `MKT`, `GRAPH`, `COLLAPSE` are deliberately **excluded** from the MSE (non-independent / resolution-only).
- Sealing `pipeline/exhaustiveness/seal.py`: `DEFAULT_THRESHOLD = 0.95` (line 27). A stratum (province × segment) is SEALED iff `coverage_lower (= n_obs / ci_high) >= threshold`. Estimators: Chapman / Chao2 / Jackknife (`estimators.py`).
- DIRCE anchor `countries/ES/census/dirce_cnae451.csv`: **161 lines** (160 data rows), columns `province_code,segment,n_external`. Loaded by `triangulation.py` *only if the file exists*; **not wired into the active seal path** yet.
- Last build `'fase9-audit-20260623'` `[RECON]`: national `N_hat ≈ 15,560` non-particular, **coverage_lower 37.7% (unsealed)**, **12 of 208 strata sealed** (all small provinces, low-volume segments).

### Honest gaps (verified)
1. **21 of 25 adapters have never passed through `harvest_run`** `[RECON]` — only `overture, borme_cnae, collapse_invisible, graph_recursive` have audit rows. The other 21 have `entity_source` rows but no audited provenance, so their captures are not trustworthy inputs to the MSE.
2. **`dork_municipal` (DORK list) has never run** — `source_health.status='unknown'`, no `harvest_run`, gated on `CARDEEP_SEARXNG_URL`. DORK is one of the 7 orthogonal lists, so its absence inflates `N_hat` uncertainty and blocks sealing of urban/high-volume strata.
3. **`axesor_cnae` (REG-CIF) effectively dormant** `[RECON]`: 1 `entity_source` row, no `source_health`, no `harvest_run`. BORME alone (altas-only, no CIF) is a thin REG list.
4. **`paginas_amarillas` is in `ADAPTERS` but absent from `DISCOVERY_REGISTRY`** — it never runs on a cadence (verified: not in the 5-vector registry).
5. **DIRCE triangulation not active** — the external anchor exists but does not constrain `N_hat`, so estimates are unbounded above.
6. **48,777 active entities lack a municipality code** — they cannot be placed in a province × segment stratum at municipal granularity, degrading stratified sealing (a `geo` dependency).

---

## Next-level objective

**Make the census provably exhaustive and route every capture through the audited gate.** Concretely, three measurable targets:

1. **National `coverage_lower` of non-particular entities ≥ 0.95 (sealed)**, up from 37.7%, with the seal computed from **7 live orthogonal lists** (today only 5 of the 7 produce audited captures — DORK and a CIF-grade REG are missing).
2. **Strata sealed ≥ 95% of the 208 (province × segment) strata**, up from 12/208, with DIRCE triangulation actively bounding `N_hat` so no stratum is sealed on an under-estimated denominator.
3. **100% of orthogonal-list captures audited** — every adapter that feeds an MSE list (`GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG`) records a `harvest_run` row with a VAM verdict, eliminating the 21-unaudited-adapter blind spot for the lists that matter to sealing.

This is the level no human team reaches: a continuously re-estimated, externally-anchored, capture-recapture-proven national census where exhaustiveness is a number you can defend per stratum, not a claim.

---

## Chosen technology (€0)

From the research, all open-source / public-data, all integrable into the existing adapter contract:

| Tech | Why chosen | Source / URL | Integration effort |
|---|---|---|---|
| **SearXNG (self-hosted Docker)** | Unblocks the DORK orthogonal list **quota-free** — the scheduler already gates `dork_municipal` on `CARDEEP_SEARXNG_URL`. Self-hosting removes the DDG-ban risk that keeps DORK dormant. | github.com/searxng/searxng (Docker image) | Low — add a compose service, set the env var; adapter already exists. |
| **osmium-tool (`osmium tags-filter`)** | Reproducible **offline** GEO denominator from Geofabrik `spain-latest.osm.pbf`; 10–100× faster than Overpass, no rate-limit. Hardens the existing `osm` adapter into a CI-reproducible source. | github.com/osmcode/osmium-tool ; download.geofabrik.de/europe/spain.html | Medium — new offline path feeding the existing `osm` adapter format. |
| **Overture Maps Places via DuckDB** | Already wired (`overture` adapter, audited). Confirms the GEO list cross-source for capture-recapture independence checks. | github.com/OvertureMaps/overturemaps-py | None (in place) — only verify query bbox = ES. |
| **bormeparser + OpenBORME (CNAE 4511/4519/4520)** | Strengthens the **REG** list with the legal universe of automotive incorporations; complements `axesor_cnae` (which adds CIF + exact CNAE). | github.com/PabloCastellano/bormeparser ; openborme.es | Low — `borme_cnae` exists; widen CNAE coverage + revive `axesor_cnae`. |
| **INE DIRCE (datos.gob.es API 4721)** | The **external statistical anchor** for triangulation — caps `N_hat` per province × CNAE so no stratum seals on a runaway estimate. The seam (`triangulation.py`) and a 160-row CSV already exist; refresh + wire it in. | datos.gob.es/.../ea0010587 (API id 4721) | Low — refresh CSV, pass through `seal.compute()`. |
| **Common Crawl CDX (`cdx_toolkit`)** | Optional long-tail discovery of dealer-owned `.es` domains absent from every structured source — pure capture-recapture upside (new list candidate). | github.com/commoncrawl/cdx_toolkit (S3 us-east-1, egress-free) | Medium — new adapter; defer to a later phase. |
| **Nominatim (self-hosted Docker)** | Geocodes BORME/Axesor postal addresses (no coords) to lat/lon so REG captures get a province/municipality and enter a stratum — directly attacks the 48,777 NULL-municipality gap. Public instance is 1 req/s (unusable at scale). | github.com/osm-search/Nominatim | Medium — Docker + ES extract; consumed by `geo` domain (dependency). |

Everything above is €0: public data (BORME/INE/Geofabrik/Overture/Common Crawl) or self-hosted OSS (SearXNG/Nominatim). No paid API, no per-call cost.

---

## Target architecture

```
                         ┌─────────────────────────── ORTHOGONAL LISTS (MSE) ──────────────────────────┐
  Geofabrik PBF ─osmium─▶ osm ─┐                                                                        │
  Overture S3 ──DuckDB──▶ overture ─┤ GEO    autocasion ─▶ CENSUS   dgt_cat ─▶ DGT   aedra/acevas/aecs ─▶ ASSOC
  OEM locators ─────────▶ oem_* ─────────────────────────────────────────────────────────────────────▶ OEM
  SearXNG (self-host) ──▶ dork_municipal ─────────────────────────────────────────────────────────────▶ DORK
  BORME API + Axesor ───▶ borme_cnae / axesor_cnae ───────────────────────────────────────────────────▶ REG
                         └──────────────────────────────────────────────────────────────────────────────┘
  marketplaces ─▶ *_census ─▶ MKT (non-orthogonal)   graph_recursive ─▶ GRAPH (dependent)   collapse_invisible ─▶ COLLAPSE (resolution)

  every fetch() ─▶ VAM gate (declared==fetched==DB) ─▶ harvest_run row ─▶ entity + entity_source (cdp_code minted)
                                       │
                                       ▼
        discovery_capture  ◀── capture.py reads entity_source provenance per orthogonal list
                                       │
        DIRCE (INE) ──anchor──▶ triangulation.py ──▶ seal.py (Chapman/Chao2/Jackknife per province×segment)
                                       │                         coverage_lower >= 0.95 ?
                                       ▼
        exhaustiveness_estimate  +  v_exhaustiveness_seal  ─▶ national denominator, per-stratum SEAL verdict
```

**Data flow:** adapters normalize to `DiscoveredEntity` → VAM gate → audited `harvest_run` + idempotent `entity`/`entity_source` upsert (cdp_code minted, geo-resolved to INE) → `discovery_capture` records which orthogonal list saw each entity → estimators compute `N_hat` per stratum, bounded by the DIRCE anchor → seal verdict persisted. All writes to served data are **additive** and idempotent (ON CONFLICT upserts), so re-runs are safe.

---

## Execution phases

> **Hard rule for every phase that touches served data:** dry-run on a throwaway Docker Postgres at **`:5434`**, never `:5433`. Promotion to `:5433` requires: dry-run pass **+** golden snapshot diff **+** Ferrari suite green **+** CI green. `:5433` is the live census DB.

### Phase 0 — Dry-run harness on `:5434` (safety foundation)
- **Cold-start context:** The repo has only a `:5433` Postgres in `docker-compose.yml` (line 24). The dry-run discipline referenced throughout CARDEEP needs a second, ephemeral DB on `:5434` seeded from the live schema. There is no such service today (verified).
- **Tasks:** Add a `cardeep-pg-dryrun` compose service (or `docker-compose.dryrun.yml`) mapping `127.0.0.1:5434:5432`, same `postgres:16` image; a `scripts/seed_dryrun.sh` that applies all `migrations/*.sql` and loads a small geo + census fixture (reuse `scripts/seed_ci_fixture.py` if present); document `CARDEEP_DSN=postgres://...@localhost:5434/cardeep` as the dry-run DSN.
- **Verify:** `docker compose -f docker-compose.dryrun.yml up -d && CARDEEP_DSN=...5434... python -c "import asyncpg,asyncio; ..."` connects; `psql -p 5434 -c '\dt'` lists `entity, entity_source, discovery_capture, exhaustiveness_estimate`.
- **Exit:** A documented one-command dry-run DB on `:5434` independent of `:5433`.
- **Rollback:** `docker compose -f docker-compose.dryrun.yml down -v`; delete the compose file. Nothing touches `:5433`.

### Phase 1 — Route all orthogonal adapters through the audited `harvest_run` gate
- **Cold-start context:** 21/25 adapters have `entity_source` rows but no `harvest_run` audit (`[RECON]`). The MSE only trusts audited captures. Priority is the adapters feeding the 7 orthogonal lists: `osm, overture, autocasion_census, dgt_cat, aedra, acevas, aecs, oem_*, dork_municipal, borme_cnae, axesor_cnae` (DORK/REG handled in Phases 2–3).
- **Tasks:** For each orthogonal adapter not yet audited, run a bounded `python -m pipeline.discover <vector>` against `:5434`, confirm `record_count_verdict` writes a `harvest_run` row with the VAM verdict, and add the adapter to `DISCOVERY_REGISTRY` with a conservative cadence + recipe-first env limits (mirror the existing 5 entries). Add a unit test asserting every orthogonal `source_key` has a `harvest_run` row after a dry-run tick.
- **Verify:** `CARDEEP_DSN=...5434... python -m pipeline.discover osm --once` then `psql -p 5434 -c "SELECT source_key,verdict FROM harvest_run ORDER BY created_at DESC LIMIT 20"`; `pytest tests/ -k harvest_audit`.
- **Exit:** Every orthogonal-list adapter produces an audited `harvest_run` row on a dry-run tick; registry covers all 7 lists.
- **Rollback:** Revert `DISCOVERY_REGISTRY` additions; dry-run rows live only on `:5434`.

### Phase 2 — Activate the DORK orthogonal list via self-hosted SearXNG
- **Cold-start context:** `dork_municipal` (DORK, one of 7 orthogonal lists) is gated on `CARDEEP_SEARXNG_URL` (`discover_schedule.py` lines 78–84) and has never run (`source_health.status='unknown'`). DORK captures dealer-**owned** domains across the 8,132 INE municipalities — exactly the digital-footprint long tail in scope.
- **Tasks:** Add a `searxng` Docker service (€0, quota-free); set `CARDEEP_SEARXNG_URL`; run `python -m pipeline.discover dork_municipal --once` bounded by `CARDEEP_DORK_LIMIT` against `:5434`; confirm audited capture + `discovery_capture` rows tagged DORK; tune cadence in the registry.
- **Verify:** `curl $CARDEEP_SEARXNG_URL/search?q=test&format=json` returns JSON; after dry-run, `psql -p 5434 -c "SELECT count(*) FROM discovery_capture dc JOIN discovery_list dl USING(list_id) WHERE dl.bucket='DORK'"` > 0.
- **Exit:** DORK produces audited orthogonal captures on `:5434`; ready for promotion.
- **Rollback:** Unset `CARDEEP_SEARXNG_URL` (scheduler auto-skips dork — the gate is designed for exactly this); remove the compose service.

### Phase 3 — Strengthen the REG list (BORME CNAE breadth + revive Axesor CIF)
- **Cold-start context:** REG today is BORME-only (altas, no CIF). `axesor_cnae` exists but is dormant (1 `entity_source` row, no audit). A thin REG list weakens one of 7 orthogonal pillars.
- **Tasks:** Widen `borme_cnae` CNAE coverage to 4511/4519/4520; bring `axesor_cnae` to audited parity (province→muni→ficha walk, CIF + exact CNAE) on `:5434`; geocode REG postal addresses via the `geo`-owned Nominatim so REG entities land in a stratum (depends on `geo`).
- **Verify:** dry-run both vectors on `:5434`; `psql -p 5434 -c "SELECT count(*) FILTER (WHERE cif IS NOT NULL) FROM entity_source WHERE source_key='axesor_cnae'"` > 0; REG capture rows present.
- **Exit:** REG list backed by both BORME (breadth) and Axesor (CIF depth), both audited.
- **Rollback:** Revert CNAE widening; Axesor reverts to dormant. No `:5433` impact.

### Phase 4 — Wire DIRCE triangulation into the active seal path
- **Cold-start context:** `triangulation.py` loads `dirce_cnae451.csv` (160 rows, verified) only if present and is **not** constraining the active `seal.compute()`. Without an external upper bound, `N_hat` can run away and seal strata prematurely.
- **Tasks:** Refresh the CSV from INE DIRCE API 4721 (province × CNAE 45xx × segment); pass the anchor through `seal.compute()` so per-stratum `N_hat` is bounded by `n_external`; add a test that a stratum cannot seal when `n_obs < threshold * n_external`.
- **Verify:** rebuild MSE on `:5434` fixture; `pytest tests/ -k triangulation`; inspect `exhaustiveness_estimate` for the anchor column populated.
- **Exit:** No stratum seals on an under-estimate; national `coverage_lower` is anchor-bounded.
- **Rollback:** Revert the `seal.compute()` signature change; CSV refresh is additive (old CSV restorable from git).

### Phase 5 — National sealing build + promotion to `:5433`
- **Cold-start context:** With 7 audited orthogonal lists live (Phases 1–3) and DIRCE anchoring (Phase 4), run the national sealing build to push `coverage_lower` from 37.7% toward ≥95% and strata from 12/208 toward ≥198/208.
- **Tasks:** Full national discover sweep (registry, unbounded env) on `:5434`; run sealing build (`pipeline/exhaustiveness/cli.py`); record per-stratum verdicts; **then** promotion gate to `:5433`: golden snapshot diff + Ferrari suite + CI all green.
- **Verify:** `psql -p 5434 -c "SELECT coverage_lower FROM exhaustiveness_estimate WHERE province_code IS NULL AND segment IS NULL ORDER BY build_run_id DESC LIMIT 1"` ≥ 0.95; sealed-strata count query ≥ 198; Ferrari + CI green before promotion.
- **Exit:** National denominator sealed ≥95% on `:5434`, promoted to `:5433` only after all gates pass.
- **Rollback:** Promotion is additive (new `build_run_id` rows); revert by querying the prior `build_run_id`. No row mutation of served entities.

---

## Risks & mitigations
- **R1 — Non-independent lists inflate seal.** GEO/CENSUS overlap (Overture ingests OSM) breaks capture-recapture independence. *Mitigation:* MKT/GRAPH/COLLAPSE already excluded from `ORTHOGONAL_LISTS`; add an independence check (pairwise capture correlation) before trusting a stratum seal.
- **R2 — DDG ban from unbounded dork.** *Mitigation:* the scheduler gate (`requires_env=("CARDEEP_SEARXNG_URL",)`) already blocks auto-dork without SearXNG; Phase 2 self-hosts SearXNG so the national sweep is quota-free.
- **R3 — 48,777 NULL-municipality entities can't be stratified.** *Mitigation:* Nominatim geocoding in Phase 3 (depends on `geo`); strata with insufficient geo resolution stay UNSEALED rather than seal on partial data.
- **R4 — Accidental write to `:5433`.** *Mitigation:* every phase dry-runs on `:5434`; promotion only via golden+Ferrari+CI gate; `discover.py` DSN default must be overridden by `CARDEEP_DSN` env in all dry-runs (verified default is `:5433`, so the env override is mandatory, not optional).
- **R5 — DIRCE anchor stale (annual cadence).** *Mitigation:* treat `n_external` as a soft upper bound with a documented refresh date; never let a stale anchor *lower* a seal verdict, only cap it.

## Success metrics
- National `coverage_lower` (non-particular) **≥ 0.95 sealed** (from 37.7% unsealed). Query: `exhaustiveness_estimate WHERE province_code IS NULL AND segment IS NULL`.
- **≥ 198/208 strata sealed** (from 12/208).
- **7/7 orthogonal lists produce audited `harvest_run` captures** (today 5/7: DORK and CIF-grade REG missing).
- **0 orthogonal-list adapters without a `harvest_run` row** after a dry-run tick (from 21/25 unaudited overall).
- DIRCE anchor active: **100% of sealed strata respect `n_obs ≤ ci_high` and `N_hat ≤ n_external` bound**.
- **€0 spend** across all phases (verified: all sources public or self-hosted OSS).
