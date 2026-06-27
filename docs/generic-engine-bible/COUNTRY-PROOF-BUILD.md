# Country-Proof Build (motor genérico) · rama `feature/country-proof-build`
> Doc de entrega + resume anchor. Última: 2026-06-27. **Reversible 100% cerrado y gateado.**
> **Aislamiento inviolable:** todo construido/probado en `:5434` (dry-run) + esta rama. **`:5433` (prod viva) jamás tocado.** `main` intacto, sin push. Cada estado = verificado por MÍ re-corriendo los goldens.

## Objetivo
Cerrar la country-blindness del motor → **país nuevo = otra ejecución** (cero false-merge transfronterizo, servido+sellado por país). España preservada: `default 'ES'` ⇒ **byte-idéntico** para el tenant único.

## Lo construido (18 commits, `54d691f..66ca648`) — todo VERIFICADO por mí
**Vectores de corrupción (false-merge):**
| # | Vector | Commit |
|---|---|---|
| 1 | dealer — `country_code` en las 4 block-keys | `61768a7` |
| 2 | vehículo Signal A+B — país vía JOIN + guard pre-write | `be77797` |
| 3 | dedup `deep_link` + `cross_source` | `795c6c9` |
| 4 | β resolver + guard SQL (`0057` `v_country_proof_violations`) | `f198213` |
| 5 | serving mint+geo+queries (`0058` + meta-test) | `6cc01d8` |

**Endurecimiento 360º (cada uno un proyecto):**
- **360-A** adversarial real FR/IT/PT/GR (`052fa8f`) — cazó+arregló regex mint + G1, y destapó 3 bugs de esquema reales.
- **F1** ancho geo `CHAR→VARCHAR` + cadena FK (`e910cd4`, `0059`) — FR DOM `971` / IT ISTAT `058091` entran.
- **F2** transliteración nombres dealer no-latinos (`9a5559b`, `anyascii` ISC €0) — eliminó señal-muerta + sobre-merge griego.
- **F3** transliteración títulos vehículo no-latinos (`76ff899`) — `_normalize_title` es el único corroborador de Signal B; arreglado under+over-merge.
- **360-B** seal + exhaustividad por país (`20e56a3`, `0060`).
- **Ancho analítico** `discovery_capture`/`exhaustiveness_estimate` (`555eb60`, `0061`).
- **360-C Perf** — auditado: el `country_code` en block-keys es neutral-a-positivo (particiona bloques más pequeños; constante no-op en mono-tenant) y el filtro servido tiene índice (`idx_entity_country`). **Sin migración de índice.**
- **Retrofit de tests** (`66ca648`) — `test_country_coexistence` aislado a `:5434` + cableado al gate; geo tests honran `CARDEEP_DSN` con skip honesto.

**360-D · CI gate (`7b2b0cd` + `aac3a81` + `66ca648`):** job `country-proof-invariant` corre **13 ficheros / 106 tests** contra `:5434`, con guard anti-greenwash (falla si skip/error/encoge **< floor 101**). Hallazgo: en `db-tests` (:5433) los goldens se saltaban (gate fantasma) → ahora corre de verdad.

## Estado verificado (último barrido propio)
- **Gate: `106 passed / 0 skip / 0 fail`** en `:5434` (head `0061`).
- Migraciones aditivas en la rama: `0057` guard · `0058` servable país · `0059` ancho geo · `0060` seal país · `0061` ancho analítico. **Probadas byte-idénticas ES.** Prod `:5433` sigue `0055`, intacta.
- Dep declarada: `anyascii==0.3.3` (ISC, €0).

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
**(1)** aplicar `0057→0061` a `:5433` (ADITIVAS, probadas byte-idénticas ES) **ANTES** que el código · **(2)** merge `feature/country-proof-build` → `main` · **(3)** re-correr el clustering servido en `:5433` (los block-keys ahora llevan país) · **(4)** job CI `country-proof-invariant` + Ferrari verdes. **NO ejecutar sin la palabra "cutover" del owner.**

## OPEN honestos (con causa — NO core de merge; declarados, no atajos)
- **Exhaustividad pipeline** (`pipeline/exhaustiveness/seal.py`, `report.py`): país por DEFAULT 'ES' hoy; setear explícito cuando el **país-#2** corra exhaustividad real. (Dependiente de que país-#2 exista.)
- **Tests de integración** `test_province_seal_view` / `test_api_*`: atados a `cdp_code` reales del censo vivo → no retrofitteables a `:5434`; **corren en `db-tests` CI (:5433 efímero geo-sembrado) + Ferrari local** (cubiertos, no es hueco).
- **OPEN-D:** `cluster_dealers.py:816-950` auditoría ES-hardcoded — **diagnóstico**, no afecta correctitud de merge multi-país.

## Resume
1. Re-corre el gate: `CARDEEP_DSN=…:5434 pytest` los 13 ficheros del job `country-proof-invariant` (`ci.yml`) → 106 passed.
2. El CORE country-proof está 100% cerrado+gateado. Lo pendiente es el **cutover** (owner) y los OPEN dependientes de país-#2. **`:5433` jamás se toca.**
