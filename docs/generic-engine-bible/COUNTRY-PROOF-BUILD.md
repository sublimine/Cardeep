# Country-Proof Build (motor genérico) · rama `feature/country-proof-build`
> Doc de entrega + resume anchor. HANDS-OFF. Última: 2026-06-27.
> **Aislamiento inviolable:** TODO se construyó/probó en `:5434` (dry-run) + esta rama. **`:5433` (prod viva) jamás tocado.** `main` intacto, sin push. Cada `[x]` = verificado por MÍ re-corriendo los goldens (no por el label del agente).

## Objetivo
Cerrar la country-blindness del motor → **país nuevo = otra ejecución** (cero false-merge transfronterizo, servido por país, sellado por país). España preservada: `default 'ES'` ⇒ **byte-idéntico** para el tenant único actual.

## Base — 5 vectores de corrupción CERRADOS y VERIFICADOS
| # | Vector | Fix | Commit |
|---|---|---|---|
| 1 | dealer false-merge | `country_code` en las 4 block-keys de `cluster_dealers` | `61768a7` |
| 2 | vehículo Signal A+B | país vía JOIN a `entity` + guard pre-write bloqueante | `be77797` |
| 3 | dedup `deep_link` + `cross_source` | `(country_code, key)` | `795c6c9` |
| 4 | β resolver + guard SQL | `country_set` en CUF + mig `0057` (`v_country_proof_violations`) | `f198213` |
| 5 | serving mint+geo+queries | regex `^CDP-[A-Z]{2}-` + predicado país + mig `0058` + meta-test | `6cc01d8` |

## 360º — cada vector elevado a proyecto institucional (VERIFICADO)
- [x] **360-A · Adversarial multi-país real** (`052fa8f`) — FR/IT/PT/GR con gramática real. Cazó+arregló: regex mint `[0-9A-Z]{2}`, G1 country-scoped. Y cazó 3 bugs de esquema reales → F1/F2/F3.
- [x] **F1 · Ancho geo VARCHAR** (`e910cd4`) — `geo_province CHAR(2)→VARCHAR(8)` + `geo_municipality CHAR(5)→VARCHAR(16)` + cadena FK (mig `0059`). FR DOM `971` / IT ISTAT `058091` entran.
- [x] **F2 · Normalización no-latina dealer** (`9a5559b`) — `norm_name` transliteraba a vacío (griego/cirílico → señal muerta + sobre-merge por residuo). Unificado en `name_normalize.py` con `anyascii` (ISC, €0). ES byte-idéntico.
- [x] **F3 · Normalización no-latina vehículo** (`76ff899`) — `_normalize_title` (único corroborador de Signal B) tenía el mismo bug → under+over-merge. Reusa el primitivo de F2.
- [x] **360-B · Seal + exhaustividad country-scoped** (`20e56a3`, mig `0060`) — `v_province_seal`/`v_exhaustiveness_seal` + `/geo/seal` + `/geo/exhaustiveness` mezclaban países; ahora con dimensión país.
- [x] **360-D · CI gate** (`7b2b0cd`) — la suite country-isolation (11 ficheros) cableada a `ci.yml` job `country-proof-invariant` contra `:5434`, con guard anti-greenwash (falla si skip/encoge ≥70). **Hallazgo:** en `db-tests` (:5433) los goldens se saltaban = gate fantasma; ahora corre de verdad.

## Estado verificado (último barrido propio)
- **Gate CI (11 ficheros, comando exacto del job): `75 passed`** en `:5434` (head `0060`). Suite ampliada de 13 ficheros: `133 passed, 1 skipped` (el skip es `test_country_coexistence.py` pilot DE no sembrado, no gateado).
- Regresión: `cluster_vehicles` 70, `complete` 52, `resolve_entities` 74, unit ~489 — verdes. ES byte-idéntico probado (nombres/títulos reales + barrido per-carácter).
- **Migraciones aditivas en la rama:** `0057` (guard), `0058` (servable país), `0059` (ancho geo), `0060` (seal país). Aplicadas SOLO a `:5434`. **Prod `:5433` sigue `0055`, intacta.**
- Dependencia nueva declarada: `anyascii==0.3.3` (ISC) en `requirements.txt`.

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
Orden estricto: **(1)** aplicar migraciones `0057→0060` a `:5433` (ADITIVAS, probadas byte-idénticas ES) **ANTES** que el código · **(2)** merge `feature/country-proof-build` → `main` · **(3)** re-correr el clustering servido en `:5433` (los block-keys ahora llevan país) · **(4)** Ferrari + el job CI `country-proof-invariant` verdes. **NO ejecutar sin la palabra "cutover" del owner.**

## Follow-ups OPEN honestos (con causa — país-#2 / infra, NO core de merge; declarados, no atajos)
- **Exhaustividad pipeline** (`pipeline/exhaustiveness/seal.py::_persist`, `report.py`): escriben país solo por DEFAULT 'ES'; cuando el país #2 corra exhaustividad real habrá que setear `country_code` explícito + filtrar la fila nacional. (No-servido hoy.)
- **Ancho analítico:** `discovery_capture.province_code` / `exhaustiveness_estimate.province_code` `CHAR(2)` sin ensanchar (estrato analítico, sin FK). Mini-migración cuando país-#2 tenga provincia >2 chars.
- **Tests geo hard-pinned a `:5433`** (`test_geo_reverse/fuzzy/upsert_backfill`, `test_country_coexistence`, `test_province_seal_view`, `test_api_*`): retrofit a `CARDEEP_DSN`+seed `:5434` para sumarlos al gate. (Infra de test; el gate ya corre los goldens nuevos.)
- **360-C Perf/escala:** auditoría EXPLAIN + índices de soporte de los block-keys country-scoped a 2M+ filas (impacto esperado mínimo: `country_code` es igualdad barata + particiona grupos; confirmar antes/durante cutover).
- **OPEN-D:** `cluster_dealers.py:816-950` auditoría ES-hardcoded (diagnóstico, no core de merge).

## Resume (un yo futuro / hands-off lee esto y ejecuta)
1. Lee este doc + re-corre el gate: `CARDEEP_DSN=…:5434 pytest` los 11 ficheros del job `country-proof-invariant` (en `ci.yml`).
2. El CORE country-proof está cerrado+verificado. Lo pendiente son los follow-ups de arriba (país-#2/infra) y el **cutover** (gate del owner).
3. Verifica multi-vía en disco/DB antes de declarar nada. **`:5433` jamás se toca.**
