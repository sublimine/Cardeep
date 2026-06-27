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
- [ ] **360-A · Adversarial multi-país real** — goldens FR (Córcega `2A/2B`, DOM `971-976`), IT (ISTAT con muni >99 → ¿rompe `left(muni,2)=province`?), PT, y un caso no-UE/no-latino. Cada quirk verificado, no inventado.
- [ ] **360-B · Seal endpoints** — `/geo/seal` + `/geo/exhaustiveness` + vistas-certificado con dimensión país (OPEN declarado de #5).
- [ ] **360-C · Perf/escala** — `country_code` en block-keys + predicados no degradan a 2M+ filas (EXPLAIN + índices, migración aditiva).
- [ ] **360-D · CI** — suite country-isolation cableada al CI (`:5434` efímero) → regresión cross-país imposible para siempre.
- [ ] **360-E · Docs/provenance** — `BLOCKING_RULES`, `RESOLVER_VERSION`, `COUNTRY-PROOF-INVARIANT.md` actualizados al estado real.

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
Orden de despliegue: **migraciones (`0057`+`0058`+…) ANTES que el código** (el código referencia `country_code`) · merge a `main` · re-correr el clustering servido en `:5433` · Ferrari + CI verdes. **NO ejecutar sin la palabra "cutover" del owner.**

## Resume (un yo futuro / hands-off lee esto y ejecuta)
1. Lee este PLAN + re-corre los 33 goldens (`CARDEEP_DSN=…:5434`).
2. Mira los `[ ]` de 360º → lanza el siguiente proyecto (1 a la vez, aislado en `:5434` + rama, verificado por mí antes de marcar `[x]`).
3. Verifica multi-vía en disco/DB antes de declarar nada. **`:5433` jamás se toca.**
