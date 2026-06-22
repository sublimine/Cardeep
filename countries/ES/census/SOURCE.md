# External triangulation anchor — Spain (ES)

> Provenance for `dirce_cnae451.csv`, the independent census the exhaustiveness
> seal contrasts against N̂ (`pipeline/exhaustiveness/triangulation.py`).
> Generated 2026-06-22. €0 sources only. No fabricated figures.

The seal joins this anchor on `(province_code, segment)` where
`segment ∈ {compraventa, concesionario, desguace, otros}`
(see `pipeline/exhaustiveness/capture.py::_SEGMENT`). The CSV header is
`province_code,segment,n_external`; a blank `province_code` and/or `segment`
encodes a national / all-segment anchor (the `(None, …)` keys consumed by
`seal.compute`).

## What is measured vs estimated

Each row is tagged with one of:

- **[MEDIDO]** — a direct external count, no apportionment.
- **[ESTIMADO DECLARADO]** — an honest apportionment of a real national figure
  to provinces via a published ratio/share. The national total is real; the
  per-province split is modelled and declared as such here. **Never** presented
  as a measured province figure.

| segment        | basis                                              | tag                  |
|----------------|----------------------------------------------------|----------------------|
| `compraventa`  | CNAE 451 (apportioned) minus concesionario         | [ESTIMADO DECLARADO] |
| `concesionario`| FACONAUTO installations apportioned by population  | [ESTIMADO DECLARADO] |
| `desguace`     | DGT CAT authorised-centre register, per province   | [MEDIDO]             |
| `otros`        | **no honest €0 census found → no anchor emitted**  | (omitted)            |

`otros` (garaje/subasta/importador/cadena/rent-a-car/oem-vo) has no independent
public census at province granularity, so **no row is written** for it. The
seam reports `no_anchor` for those strata rather than inventing a number.

## Sources (all €0, official)

### CNAE 451 — venta de vehículos de motor (compraventa + concesionario universe)

- **INE DIRCE 2025** (locales activos a 2025-01-01). Division-45 locales per
  province come from `data/official/denominador_cnae45_provincia_2024.csv`,
  derived from INE DIRCE **table 301** (Locales por provincia, actividad CNAE
  2009, estrato de asalariados):
  `https://www.ine.es/jaxiT3/Tabla.htm?t=301&L=0`
  (CSV mirror `data/official/dirce_301_locales_provincia_cnae2009.csv`).
  National division-45 = **88,621** locales. [VERIFICADO CSV]
- Group **451** (venta de vehículos de motor) is published only down to **CCAA**,
  never to province — this is an **INE structural limitation**, not ours
  (confirmed in `docs/recon/B6_venta_sello.md §1.3`). National group-451 2025 =
  **23,085** locales, from INE DIRCE **table 294** (Locales por CCAA, actividad
  CNAE 2009, grupos): `https://www.ine.es/jaxiT3/Tabla.htm?t=294&L=0`
  (CSV mirror `data/official/dirce_294_locales_ccaa_grupos_cnae.csv`,
  row `451 Venta de vehículos de motor / Total Nacional / Total / 2025`).
  [VERIFICADO CSV]

  **Cross-check of the national 45 decomposition (table 294, period 2025):**
  451 = 23,085 · 452 (talleres) = 50,294 · 453 (repuestos) = 11,494 ·
  454 (motos) = 3,748. Sum = **88,621 = division 45**. [VERIFICADO]

- **[ESTIMADO DECLARADO] apportionment ratio:**
  `ratio_451/45 = 23,085 / 88,621 = 0.2605` (national).
  `venta_prov = round( cnae45_locales_prov × 0.2605 )`.
  This is the exact method already verified and persisted by
  `scripts/load_denominator_provincia.py` and documented in
  `docs/recon/B6_venta_sello.md §1.4` and `docs/recon/B6_SELLO_52.md §0.4`.
  **Declared bias:** the ratio is applied uniformly across provinces, so a
  province with an atypical talleres/venta mix deviates; group 451 also includes
  CNAE 4519 (heavy/other vehicles), inflating the ceiling in provinces with much
  industrial-vehicle trade. Direction: the per-province `compraventa`+`concesionario`
  anchor is a **registral ceiling**, not a tight point estimate.

### Concesionario oficial — FACONAUTO

- **FACONAUTO** (Federación de Asociaciones de Concesionarios de la Automoción),
  national network: **5,358** installations used as the concesionario universe,
  consistent with `scripts/calc_spain_sealed.py` (`FACONAUTO_TOTAL = 5358`,
  tagged `[ESTIMADO DECLARADO: instalaciones FACONAUTO 2024]`) and
  `docs/recon/B6_SELLO_52.md §6`. Association membership is a different mechanism
  from OEM franchise lists, which is exactly what makes it a valid triangulation
  anchor (`docs/architecture/05-VERIFICATION-VAM.md §line 543`).
- **[ESTIMADO DECLARADO] apportionment:** FACONAUTO publishes the national figure,
  not a province table, so it is split by INE resident population share:
  `concesionario_prov = round( 5358 × pop_prov / pop_national )`.
  Population per province from INE (the `pop_ine` table in
  `scripts/calc_spain_sealed.py`; national = 47,870,758). **Declared bias:**
  concesionario density is not strictly proportional to population (capital and
  industrial provinces over-index); this is a modelled split, declared.

### Compraventa (independent used-car sales)

- **[ESTIMADO DECLARADO] derived:**
  `compraventa_prov = max(0, venta_prov − concesionario_prov)`.
  CNAE 451 covers the whole car-sales universe (independent compraventa +
  official concesionario); DIRCE does not split it. Subtracting the FACONAUTO
  concesionario estimate isolates the independent-dealer remainder. By
  construction `compraventa + concesionario = venta (CNAE 451 ceiling)`
  per province, so the decomposition is internally consistent and no province
  required clamping (all `venta_prov ≥ concesionario_prov`).

### Desguace — DGT CAT register  [MEDIDO]

- **DGT CAT** (Centros Autorizados de Tratamiento de vehículos al final de su
  vida útil) — the legal register of authorised scrappage centres. National
  count **1,292**, broken down per province directly, no apportionment.
- Source of the per-province split: the DGT CAT census materialised in the
  CARDEEP DB as `entity.source_group = 'desguace_network'`, which sums to exactly
  1,292 and is verified province-by-province in `docs/recon/B6_SELLO_52.md §3`
  and `docs/recon/B5_COVERAGE_RECON.md`. Re-confirmed 2026-06-22 by aggregated
  query (`SELECT province_code, COUNT(*) FROM entity WHERE kind='desguace' AND
  source_group='desguace_network' GROUP BY province_code` → 52 rows, sum 1,292).
  Public cross-reference: SIGRAUTO authorised-centre directory
  `https://www.sigrauto.com/donde-puedo-entregar-mi-vehiculo`.
  This is a **measured** anchor.

## National anchors

| key                         | value  | meaning                                              |
|-----------------------------|--------|------------------------------------------------------|
| `(,compraventa)`            | 17,362 | Σ per-province compraventa (= 23,085−5,358, rounded) |
| `(,concesionario)`          | 5,358  | exact national FACONAUTO                              |
| `(,desguace)`               | 1,292  | exact national DGT CAT                                |
| `(,)` all-segment           | 24,377 | CNAE 451 (23,085) + DGT CAT (1,292) registral ceiling |

The all-segment national anchor `(None, None)` deliberately **excludes `otros`**
(no census exists for it). It is therefore a ceiling over the three census-backed
segments, not over the full N̂ which also sums `otros` strata; the seal's
`triangulate(n_hat_sum, ext)` verdict against this anchor must be read with that
scope in mind. Per-segment national rows are provided so a scoped comparison is
possible.

## Refresh procedure

To regenerate when DIRCE/FACONAUTO/DGT figures update:
1. Update division-45 per province in
   `data/official/denominador_cnae45_provincia_2024.csv` from INE table 301.
2. Update national 451 and 45 from INE table 294 (latest period) → recompute the
   ratio.
3. Update `FACONAUTO_TOTAL` and `pop_ine` if changed.
4. Re-run the aggregated DGT CAT query for the per-province desguace counts.
5. Rebuild `dirce_cnae451.csv` (same formulas above) and re-run
   `tests/test_exhaustiveness_triangulation_loaded.py`.
