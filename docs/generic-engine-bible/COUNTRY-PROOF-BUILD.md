# Country-Proof Build (motor genérico) · rama `feature/country-proof-build`
> Doc de entrega + resume anchor. Última: 2026-06-27. **Core cerrado + endurecido por red-team adversarial (loop-until-dry, en curso).**
> **Aislamiento inviolable:** todo construido/probado en `:5434` (dry-run) + esta rama. **`:5433` (prod viva) jamás tocado.** `main` intacto, sin push. Cada estado = verificado por MÍ re-corriendo los goldens.

## Objetivo
Cerrar la country-blindness del motor → **país nuevo = otra ejecución** (cero false-merge transfronterizo, servido+sellado por país). España preservada: `default 'ES'` ⇒ **byte-idéntico** para el tenant único.

## Lo construido (26 commits, `54d691f..HEAD`) — todo VERIFICADO por mí
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

## Red-team adversarial (loop-until-dry — nada sellado sin intento de romperlo)
- **Round 1** cazó 5 misses reales (no en docs): overlays dedup L3/L4 (`build_residual_namemuni`/`build_particular` — false-merge SERVIDO silencioso), CHECKs `^CDP-ES-` de evict (`0033`), VIN cross-platform sin país, `populate_completion` G1-mirror. Arreglados (`ae1ea25`,`eef9228`,`aa00dd0`, populate; `0062`).
- **Round 2** verificó los 5 + cazó 2: G1 ancho-provincia `{2}`→`{2,8}` (`complete.py`+`populate_completion`, espejo geo VARCHAR(8)/`0062`; + corregí 3 goldens que fosilizaban el `{2}`) y trigger `entity_set_comarca` sin país (`0063`). Arreglados (`4f49137`, `0063`).
- **Round 3** en curso. Cada fix con golden RED→GREEN + cableado al gate.

## Estado verificado (último barrido propio)
- **Gate: `160 passed / 0 skip / 0 fail`** — **19 goldens** del job `country-proof-invariant` en `:5434` (head `0063`), floor 155.
- Migraciones aditivas (`0057`-`0063`, 7): guard · servable país · ancho geo · seal país · ancho analítico · cdp CHECK genérico · trigger comarca. **Byte-idénticas ES.** Prod `:5433` sigue `0055`, intacta.
- Dep declarada: `anyascii==0.3.3` (ISC, €0).

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
**(1)** aplicar `0057→0063` a `:5433` (ADITIVAS, byte-idénticas ES) **ANTES** que el código · **(2)** merge `feature/country-proof-build` → `main` · **(3)** re-correr el clustering servido en `:5433` · **(4)** job CI `country-proof-invariant` (19 goldens) + Ferrari verdes. **NO ejecutar sin "cutover" del owner.**

## OPEN — deuda DECLARADA (fase onboarding país-#2; NO core de merge, NO atajos)
- Matriz MSE exhaustividad ciega (`capture.py`/`discovery_capture`/`splink_merge`), `geo_province.ccaa_code`/`geo_comarca.ine_code CHAR(2)`, `ingest.py` gate `01..52`, `product_stats`/`/stats` sin país, `_measure_bound` ES_national, señales degradadas país-2 (NULL-seguras). Documentado en la biblia; se cierra al onboardar el país #2.
- `test_province_seal_view`/`test_api_*`: census-dependientes → corren en `db-tests` CI (:5433 efímero) + Ferrari. Cubiertos.
- OPEN-D `cluster_dealers:816-918`: auto-auditoría ES (Megar/Vegar) → N/A no-ES, benigno.

## Resume
1. Re-corre el gate: `CARDEEP_DSN=…:5434 pytest` los **19 ficheros** del job `country-proof-invariant` (`ci.yml`) → 160 passed.
2. El CORE merge/serving/esquema/normalización country-proof está cerrado+gateado+red-teameado. Pendiente: round-N del red-team hasta converger, el **cutover** (owner), y la deuda país-#2. **`:5433` jamás se toca.**
