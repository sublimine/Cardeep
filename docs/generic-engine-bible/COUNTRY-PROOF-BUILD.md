# PLAN — Country-Proof Build (motor genérico) · rama `feature/country-proof-build`
> Estado vivo + resume anchor. HANDS-OFF, no parar. Última: 2026-06-27.
> **Aislamiento inviolable:** TODO en `:5434` (dry-run) + esta rama. **PROHIBIDO `:5433`** (prod viva) — ni read-only. `main` intacto, sin push.

## Objetivo
Cerrar la country-blindness del motor → **país nuevo = otra ejecución** (cero false-merge transfronterizo, servido por país). España preservada: `default 'ES'` ⇒ byte-idéntico para el tenant único actual.

## Base — 5 vectores CERRADOS y VERIFICADOS por mí (re-corro los goldens, no me fío del label del agente)
| # | Vector | Fix | Commit | Verif. (re-run propio) |
|---|---|---|---|---|
| 1 | dealer false-merge | `country_code` en las 4 block-keys de `cluster_dealers` | `61768a7` | 4 passed |
| 2 | vehículo Signal A+B | país vía JOIN a `entity` + guard pre-write bloqueante | `be77797` | 78 passed |
| 3 | dedup `deep_link` + `cross_source` | `(country_code, key)` | `795c6c9` | 26 passed |
| 4 | β resolver + guard SQL | `country_set` en CUF + mig `0057` `v_country_proof_violations` | `f198213` | 99 passed |
| 5 | serving mint+geo+queries | regex `^CDP-[A-Z]{2}-` + predicado país + mig `0058` + meta-test | `6cc01d8` | 33 passed |

Goldens country-isolation: **33 verdes** en `:5434` (head `0058`). Regresión: `unit` 474 passed. Prod `:5433` intacta (`0055`, sin `0058`).

## 360º — cada vector elevado a proyecto institucional (EN CURSO, 1 a la vez, verificado)
- [x] **360-A · Adversarial multi-país real** (`052fa8f`, 84 passed) — FR/IT/PT/GR con gramática real. Cazó+arregló: regex mint `[0-9A-Z]{2}`, G1 country-scoped. Cazó 3 bugs de esquema → F1/F2/OPEN.
- [x] **F1 · Ancho geo VARCHAR** (`e910cd4`, 86 passed) — `geo_province CHAR(2)→VARCHAR(8)` + `geo_municipality CHAR(5)→VARCHAR(16)` + cadena FK (mig `0059`). FR DOM `971` / IT ISTAT `058091` entran. ES byte-idéntico.
- [ ] **F2 · Normalización no-latina** (OPEN-C) — `norm_name` borra griego/cirílico → señal muerta. Transliterar en `cluster_dealers`/`cross_source_dedup`/`cluster_vehicles`. ES byte-idéntico.
- [ ] **360-B · Seal endpoints** — `/geo/seal` + `/geo/exhaustiveness` + vistas-certificado con dimensión país (OPEN de #5).
- [ ] **360-C · Perf/escala** — `country_code` en block-keys + predicados no degradan a 2M+ filas (EXPLAIN + índices).
- [ ] **360-D · CI** — suite country-isolation cableada al CI (`:5434` efímero) → regresión cross-país imposible.
- [ ] **360-E · Docs/provenance** — `BLOCKING_RULES`, `RESOLVER_VERSION`, `COUNTRY-PROOF-INVARIANT.md` actualizados.

### OPEN menores tracked (no se pierden — cada uno su mini-proyecto)
- Tests geo antiguos hard-pinned a `:5433` (`test_geo_reverse/fuzzy/upsert_backfill`, `test_country_coexistence`) → retrofit a `CARDEEP_DSN` + seed `:5434`.
- `discovery_capture.province_code` / `exhaustiveness_estimate.province_code` `CHAR(2)` sin ensanchar (estrato analítico, sin FK) → pasada de ancho analítico.
- OPEN-D: `cluster_dealers.py:816-950` auditoría ES-hardcoded (diagnóstico, no core).

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
Orden de despliegue: **migraciones (`0057`+`0058`+…) ANTES que el código** (el código referencia `country_code`) · merge a `main` · re-correr el clustering servido en `:5433` · Ferrari + CI verdes. **NO ejecutar sin la palabra "cutover" del owner.**

## Resume (un yo futuro / hands-off lee esto y ejecuta)
1. Lee este PLAN + re-corre los 33 goldens (`CARDEEP_DSN=…:5434`).
2. Mira los `[ ]` de 360º → lanza el siguiente proyecto (1 a la vez, aislado en `:5434` + rama, verificado por mí antes de marcar `[x]`).
3. Verifica multi-vía en disco/DB antes de declarar nada. **`:5433` jamás se toca.**
