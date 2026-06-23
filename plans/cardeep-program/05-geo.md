# Geolocalizacion — Locate every digitally-present entity on the INE administrative mesh, to the limit of its online geo signal, at EUR0.

> This domain owns the spatial truth of the census: the INE administrative backbone (province / comarca / municipality + centroids), the resolution chain that turns a name, a coordinate, or a postcode into an authoritative INE municipality code, the backfill that closes the gap on already-harvested entities, and the API/frontend surfaces that expose geographic completeness. It does NOT decide which entities exist (discovery) nor whether their address text is real (extraction); it takes whatever geo signal an entity carries and pins it to the canonical mesh, honestly leaving a hole when no signal exists ("mejor un hueco que una mentira"). It matters because the census is worthless if you cannot answer "where" — every coverage seal, every province tree, every map polygon depends on this layer being correct and exhaustive.

## Current state (verified)

All figures below were re-verified against code in `C:\Users\elias\projects\cardeep` on 2026-06-23 and against the live DB on `cardeep-pg` (:5433) per the recon brief.

**Backbone (authoritative, complete):**
- `geo_province` = 52, `geo_comarca` = 323, `geo_municipality` = 8132 — `SELECT count(*)`.
- `geo_municipality` with centroid lat/lon = 8117 (99.8%); only 15 lack coordinates. Source: `municipios_centroides.csv` (PopulateTools/ine-places, MIT), seeded by `scripts/seed_geo_centroides.py` which corrects the upstream lat/lon column swap (verified comment in file).
- Only 2 municipalities lack `comarca_id` (Ceuta + Melilla, which have no INE comarca). Comarca is auto-assigned by PG trigger `trg_entity_set_comarca` → `entity_set_comarca()` defined in `migrations/0018_comarca.sql` (verified: `AFTER INSERT OR UPDATE ... FOR EACH ROW`).

**Resolution chain (verified in code):**
- `pipeline/geo.py` `GeoResolver`: name → INE code. Cascade exact → fuzzy (rapidfuzz `WRatio >= 88`, `_FUZZY_CUTOFF = 88`, query-min-len 4, candidate-len guard `max(4, len//3)`) → locality gazetteer from `data/geo/nomenclator_entidades_ine.csv` (~63k locality→municipality pairs, loaded at startup, source inigoflores/ds-codigos-postales-ine-es). All lookups province-scoped, never cross-province. Tuning constants annotated as "validated by B4.1 probe (0 false positives)".
- `pipeline/geocode.py`: `MunicipalityGeocoder` (KNN inverse lat/lon→municipality, `KNN_MAX_DISTANCE_KM = 30.0`, province-scoped, exact haversine on the winner), `ProvinceGeocoder`, and `PostcodeIndex` (postcode→municipality via the same Nomenclátor, ambiguous postcodes return None).
- Backfill: `scripts/geo_backfill.py` (priority 1=KNN, 2=CP; writes `geocode_source` + `geocode_precision`) and `scripts/backfill_municipality_geo.py` (self-validating per audit P2 SU-A6: writes only if resolved code exists in `geo_municipality` AND its prefix matches the entity's `province_code`; **dry-run by default**, `--apply` to write — verified line 100 `apply="--apply" in sys.argv`).

**API surface (verified in `services/api/routers/geo.py`):** `/geo/completeness`, `/geo/seal` (DIRCE/DGT registral ceiling, live view `v_province_seal`), `/geo/exhaustiveness` (MSE capture-recapture, live view `v_exhaustiveness_seal`, honest-by-construction lower bound), `/geo/{province}/tree`, `/geo/{province}/entities`, `/geo/{province}/municipalities/{muni}/entities`. All authenticated and cached.

**Frontend:** `web/src/lib/geo.ts` loads province polygons from TopoJSON with a d3-composite conformal-conic projection of Spain for Three.js.

**Coverage truth (live, non-particular = `kind <> 'particular'`):**
- entity total = 450,619; with lat/lon = 188,606 (41.9%).
- non-particular total = 91,468; without `province_code` = 1,090 (1.19%).
- non-particular full geo (prov+muni+comarca) = **78,466 (85.79%)**.
- non-particular without `municipality_code` (total gap) = **12,867 (14.07%)**.
- of those, with usable geo signal (lat/lon OR postcode) = **3,828** — KNN-resolvable now ~1,110/1,182 (93.9%), CP-resolvable now ~2,210/2,646 (83.5%).
- **data-blocked** (no signal at all: no muni, no lat/lon, no postcode) = **9,039 (9.88%)** — this is the honest floor; nothing in scope recovers these.
- non-particular with municipality but no comarca = 135 (Ceuta 68 + Melilla 67) — structural, not a defect.

**Honest read:** the recoverable gap is the ~3,828 signal-bearing rows. Applying the existing backfill end-to-end should lift 85.79% toward roughly 89–90% (~3,300 recoverable of 3,828). The remaining ~9.9% is a source wall, not a tooling failure.

## Next-level objective

Reach the **data-blocked floor**: every non-particular entity that carries ANY geo signal (coordinate, postcode, or resolvable place name in its harvested address text) is pinned to an authoritative INE municipality, with `geocode_source` + `geocode_precision` recorded and zero false assignments. Concretely:
1. Drive non-particular `municipality_code` completeness from **85.79% → ≥ 89%** by applying the existing self-validating backfill over the 3,828 signal-bearing rows (measurable via `/geo/completeness`).
2. Add a **third recovery lane** — free-text address geocoding via a self-hosted CartoCiudad-first / Nominatim-fallback resolver normalized by libpostal — so entities that today have *only* a raw address string (currently invisible to the KNN/CP backfill) become resolvable. This is what no human or prior pipeline does at this completeness: a four-source resolver (name gazetteer → reverse-KNN → postcode → structured-address geocode) over the entire digital footprint of Spain.
3. Make completeness **provably non-regressing**: a geo-quality assertion in the Ferrari suite that fails if non-particular full-geo % drops, and a golden dataset of known (entity → INE code) pairs.

## Chosen technology (EUR0)

The backbone, fuzzy resolver, KNN, and postcode lanes already exist and are correct — **do not rebuild them**. The net-new capability is structured free-text address geocoding, plus name-variant hardening. Selected from the research, all EUR0:

| Tool | Role here | Why it wins | Source | Integration effort |
|---|---|---|---|---|
| **libpostal + pypostal** | Normalize raw address strings into `{road, house_number, postcode, city, state}` before any geocode call. | 99.45% parse accuracy, fully offline, kills abbreviation/accent drift (Av./Avda./Avenida) that breaks the existing name resolver. MIT. | github.com/openvenues/libpostal, github.com/openvenues/pypostal | Medium — C lib + ~2GB model download once; wrap in a small `pipeline/address_parse.py`. Offline, no runtime network. |
| **CartoCiudad REST (IGN/CNIG)** | Primary structured-address → coordinate + INE code for the ~95% of Spain it covers (Catastro+INE+IGN fused). | Authoritative for Spanish addresses (portal/escalera), the only free source resolving cadastral references; CC-BY 4.0, no key, no quota. | github.com/IDEESpain/Cartociudad, pycartociudad on PyPI | Low–Medium — HTTP client behind `geopy`; rate-limit politely (batch nightly). |
| **Nominatim (self-hosted)** | Fallback geocoder for País Vasco/Navarra (CartoCiudad gap) and for entities CartoCiudad misses. | De-facto self-host standard; Spain Geofabrik extract (~1.4GB) imports in hours on 16–32GB RAM; ODbL/GPL3, no rate limit when self-hosted. | github.com/osm-search/Nominatim | High (one-time infra) — Docker import of ES extract. Deferred to its own phase; falls back to "hole" until ready. |
| **geopy** | Single client abstraction with `RateLimiter` over CartoCiudad (custom URL) + Nominatim, enabling clean fallback ordering. | One interface, no per-backend rewrite; built-in rate limiting. MIT. | github.com/geopy/geopy | Low. |
| **GeoNames ES + pg_trgm** | Harden `GeoResolver` against regional name variants (Gerona→Girona, Lérida→Lleida, Vizcaya→Bizkaia) the current alias table misses. | Authoritative alternate-names dump; pairs with Postgres `pg_trgm.similarity()` already available. CC-BY 4.0. | geonames.org/export | Low–Medium — extend the existing alias/gazetteer load. |

`reverse_geocoder` (KD-tree offline) was evaluated and **rejected**: the existing `MunicipalityGeocoder` already does province-scoped KNN with a defensible 30km guard against INE centroids — adding a second reverse engine would be redundant (DRY) and would not be province-scoped.

## Target architecture

**Resolution chain becomes four lanes, ordered by precision, all province-scoped, all "hole over lie":**

```
harvested entity signal
   ├─ municipality NAME present  → GeoResolver (exact → fuzzy≥88 → Nomenclátor)        [exists]
   ├─ lat/lon present            → MunicipalityGeocoder KNN (≤30km, province-scoped)   [exists]
   ├─ postcode present           → PostcodeIndex (Nomenclátor, ambiguous→None)         [exists]
   └─ raw ADDRESS string only    → AddressGeocoder:                                    [NEW]
                                       libpostal parse
                                       → CartoCiudad (primary)
                                       → Nominatim self-hosted (fallback)
                                       → (lat/lon out) → MunicipalityGeocoder KNN to canonical INE code
   all lanes → self-validation gate (code ∈ geo_municipality ∧ prefix == province_code)
             → write municipality_code (+ geocode_source, geocode_precision)
             → trg_entity_set_comarca fills comarca_id automatically
```

- **Data:** new entity columns are already present (`municipality_code`, `geocode_source`, `geocode_precision`). The address lane reuses them; `geocode_source` gains values `cartociudad` / `nominatim`. No served-column semantics change — purely additive backfill of NULLs.
- **New module `pipeline/address_geocode.py`:** `AddressGeocoder` wrapping libpostal parse + geopy(CartoCiudad, Nominatim) + reuse of `MunicipalityGeocoder` to snap returned coordinates to the canonical INE municipality (never trust the geocoder's own admin label — always re-snap to OUR mesh).
- **New script `scripts/geo_backfill_address.py`:** same self-validation gate and dry-run-by-default contract as `backfill_municipality_geo.py`; only targets rows with a raw address but no lat/lon/postcode/muni.
- **Flow / safety:** all served-data writes go `dry-run (:5434) → golden cdp byte-identity → Ferrari → CI`, never `:5433` directly (verified convention in `plans/P-census-data-quality.md`). Backend changes activate on API restart (running uvicorn is a stale build).

## Execution phases

Each phase is ~1 PR, additive, reversible. The DB on **:5433 is production** and is the faithful target reproduced by `docker-compose.yml`; **:5434 is the dry-run instance** for served-data validation per repo convention.

### Phase 0 — Harvest the recoverable gap with existing tooling (no new code)
- **Cold-start context:** 3,828 non-particular rows have lat/lon or postcode but no `municipality_code`. The self-validating backfill `scripts/backfill_municipality_geo.py` already resolves these correctly but has not been applied end-to-end.
- **Tasks:** (1) bring up a fresh `:5434` from `docker-compose.yml` + migrations + seeds (`load_geo.py`, `seed_geo_centroides.py`). (2) Run `python scripts/backfill_municipality_geo.py` (dry-run) and capture the report. (3) Diff the would-write set against expectation; confirm every write passes the prefix==province_code gate.
- **Verify:** `python scripts/backfill_municipality_geo.py` (no flag) prints N candidates resolved, 0 prefix-mismatch skips unexplained. On :5434 after `--apply`: `SELECT count(*) FROM entity WHERE kind<>'particular' AND municipality_code IS NOT NULL AND comarca_id IS NOT NULL` rises by ~3,300 toward 81,700; `pytest tests/test_geo_upsert_backfill.py` green; golden cdp byte-identity unchanged; Ferrari green; CI green.
- **Exit criteria:** non-particular full-geo % ≥ 89% on :5434, zero false assignments, all gates green. Then apply to :5433 via the normal CI-build/deploy chain (NOT a manual write).
- **Rollback:** writes are NULL→value only; `UPDATE entity SET municipality_code=NULL, geocode_source=NULL, geocode_precision=NULL WHERE geocode_source IN ('knn','postcode') AND <this run's build_run_id>`. Backfill is idempotent.

### Phase 1 — Geo-completeness regression guard (Ferrari + golden)
- **Cold-start context:** no test currently fails if completeness regresses; the seal tests assert dealer counts, not municipality-fill %.
- **Tasks:** (1) build a golden set of ~200 hand-verified `(entity attributes → expected INE code)` pairs covering exact/fuzzy/KNN/CP, stored as a fixture. (2) Add a Ferrari-grade assertion: non-particular full-geo % must be `>=` a checked-in floor (seed 0.858) and the golden set must resolve 100% correctly.
- **Verify:** `pytest tests/test_geo_fuzzy.py tests/test_geo_reverse.py tests/test_geo_upsert_backfill.py` green; new test RED when floor is lowered artificially, GREEN at real data. Requires `cardeep-pg`-shaped DB with centroids seeded (per existing test headers).
- **Exit criteria:** regression test in the Ferrari suite, green, and proven to fail on a forced regression.
- **Rollback:** test-only PR; revert the commit.

### Phase 2 — libpostal normalization + GeoResolver name-variant hardening
- **Cold-start context:** `GeoResolver` has a curated alias table but misses systematic regional variants; raw address strings are not parsed before resolution.
- **Tasks:** (1) add `pipeline/address_parse.py` wrapping pypostal (offline, model downloaded once into repo-ignored cache). (2) Load GeoNames ES alternate names into the resolver's alias index; use existing `pg_trgm` for a final fuzzy tie-break with confidence threshold. (3) Feed parsed `city`/`state` tokens into `GeoResolver` for address-only rows.
- **Verify:** unit tests for parse of `"C/ Gran Vía 28, 3º izq, 28013 Madrid"` and for variant resolution (Gerona→17, Lérida→25, Vizcaya→48); `pytest tests/test_geo_fuzzy.py` extended, green; 0 new false positives on the B4-style probe `scripts/recon/b4_geo_probe.py`.
- **Exit criteria:** variant resolution proven on a fixture set; libpostal available offline; no regression in existing fuzzy tests.
- **Rollback:** new module + additive index load; revert commit. No served-data write in this phase.

### Phase 3 — AddressGeocoder (CartoCiudad primary) + address backfill
- **Cold-start context:** rows with only a raw address string are invisible to KNN/CP. CartoCiudad is the authoritative EUR0 Spanish geocoder.
- **Tasks:** (1) `pipeline/address_geocode.py`: libpostal parse → geopy→CartoCiudad → returned coordinate re-snapped to canonical INE code via `MunicipalityGeocoder` (never trust the geocoder's admin label). (2) `scripts/geo_backfill_address.py`: dry-run default, same self-validation gate, `geocode_source='cartociudad'`, polite batch rate-limiting. (3) Cache resolved (address→code) to avoid re-querying.
- **Verify:** dry-run report on :5434 lists candidates with confidence; manual spot-check of 30 against the live CartoCiudad result; on `--apply` (:5434) full-geo % rises further; golden byte-identity unchanged; Ferrari + CI green.
- **Exit criteria:** address-only recoverable rows resolved with 0 prefix-mismatch writes; completeness gain measured and ≥ Phase 0 result. Apply to :5433 via normal CI/deploy chain.
- **Rollback:** `geocode_source='cartociudad'` writes are isolated and NULL→value; revert by NULLing that source's rows; backfill idempotent.

### Phase 4 — Nominatim self-hosted fallback (País Vasco / Navarra + CartoCiudad misses)
- **Cold-start context:** CartoCiudad excludes País Vasco and Navarra; those addresses currently fall through to "hole".
- **Tasks:** (1) Docker import of the Spain Geofabrik extract into a self-hosted Nominatim (one-time, documented, off the served stack). (2) Wire as geopy fallback after CartoCiudad in `AddressGeocoder`. (3) Re-run `scripts/geo_backfill_address.py` over the still-NULL address rows.
- **Verify:** Nominatim `/status` healthy; fallback resolves a sample of Bilbao/Vitoria/Pamplona addresses, re-snapped to correct INE codes; dry-run→golden→Ferrari→CI green before any :5433 apply.
- **Exit criteria:** Basque/Navarrese address-only rows resolved; completeness at the data-blocked floor (~90% non-particular); remaining gap proven to be the 9.88% no-signal wall.
- **Rollback:** `geocode_source='nominatim'` writes isolated and reversible; Nominatim infra is external to the served stack and can be torn down without affecting data.

## Risks & mitigations
- **False municipality assignment (CRITICAL).** Mitigation: every lane keeps the existing self-validation gate (code ∈ `geo_municipality` ∧ prefix == `province_code`) and always re-snaps external geocoder coordinates to OUR INE centroid mesh; "hole over lie" preserved. Golden set + Ferrari guard catch regressions.
- **Touching served data on :5433 directly.** Mitigation: hard rule — dry-run (:5434) → golden cdp byte-identity → Ferrari → CI → deploy chain. No phase writes :5433 manually.
- **CartoCiudad coverage holes (País Vasco/Navarra).** Mitigation: Nominatim self-hosted fallback (Phase 4); until then those rows stay honest holes, not guesses.
- **libpostal model size / build friction.** Mitigation: one-time ~2GB offline download into an ignored cache; no runtime network; document in the phase.
- **External API politeness / EUR0 integrity.** Mitigation: geopy RateLimiter, nightly batch, persistent (address→code) cache; all sources confirmed free (CartoCiudad CC-BY, Nominatim ODbL self-hosted, GeoNames CC-BY).
- **Over-claiming completeness.** Mitigation: report the 9.88% data-blocked floor explicitly in `/geo/completeness`; never present resolved % as if the wall were recoverable.

## Success metrics
- Non-particular full-geo (prov+muni+comarca) %: **85.79% → ≥ 89%** (Phase 0–3), approaching the **~90% data-blocked floor** (Phase 4). Source: `/geo/completeness`.
- Recoverable signal-bearing rows resolved: ≥ 3,300 of 3,828 (KNN+CP), plus address-only rows newly recovered (Phase 3–4).
- **Zero** false municipality assignments (every write passes the prefix-gate; golden set resolves 100%).
- Ferrari geo-regression assertion present and green; proven to fail on forced regression.
- `geocode_source` distribution observable (`knn` / `postcode` / `cartociudad` / `nominatim`) for full provenance.
- EUR0 maintained: no paid API, no quota breach (verified per source license).
