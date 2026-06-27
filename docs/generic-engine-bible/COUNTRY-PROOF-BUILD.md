# Country-Proof Build (motor genérico) · rama `feature/country-proof-build`
> Doc de entrega + resume anchor. Última: 2026-06-28. **Invariante COUNTRY-PROOF del censo servido: CERRADO y ADVERSARIALMENTE SELLADO.**
> **Aislamiento inviolable:** todo construido/probado en `:5434` (dry-run) + esta rama. **`:5433` (prod viva) jamás tocado.** `main` intacto, sin push. Cada estado verificado por MÍ re-corriendo los goldens.

## Objetivo — ACHIEVED
Cerrar la country-blindness del motor → **país nuevo = otra ejecución** (cero false-merge transfronterizo, servido+sellado por país). España preservada: `default 'ES'` ⇒ **byte-idéntico** para el tenant único. El red-team independiente confirmó el cierre.

## El build (34 commits, `54d691f..HEAD`) — todo VERIFICADO por mí
**A · 5 vectores de corrupción (false-merge):** dealer 4 block-keys (`61768a7`) · vehículo Signal A+B + guard (`be77797`) · dedup deep_link+cross_source (`795c6c9`) · β resolver + guard SQL `0057` (`f198213`) · serving mint+geo+queries `0058`+meta-test (`6cc01d8`).
**B · Endurecimiento 360º:** adversarial real FR/IT/PT/GR (`052fa8f`) · ancho geo `VARCHAR` `0059` (`e910cd4`) · transliteración no-latina nombres `9a5559b` + títulos `76ff899` (`anyascii` ISC €0) · seal+exhaustividad por país `0060` (`20e56a3`) · ancho analítico `0061` (`555eb60`) · perf auditado (neutral, índice existe) · retrofit tests · exhaustividad pipeline country-aware (`b36224a`) · CI gate (`7b2b0cd`).
**C · Campaña RED-TEAM adversarial (loop-until-dry — 11 misses + 2 residuales, TODOS cerrados):**
- R1 (5): overlays dedup L3/L4 (`ae1ea25`), CHECKs `^CDP-ES-` evict `0062` (`eef9228`), VIN cross-platform (`aa00dd0`), populate G1-mirror.
- R2 (2): G1 ancho-provincia `{2}→{2,8}` (`4f49137`), trigger comarca `0063`.
- R3 (3): associations/PA dedup (`f88697f`), seed centroides + denominator (`355673f`).
- Barrido EXHAUSTIVO (1): `backfill_comarca` (último writer). + self-verify `backfill_municipality_geo`.
- R-final (confirmación): **CONVERGIDO — SELLO OK** + 2 residuales LOW cerrados: geocoder + `gestion_item` monitoring `0064` (`18b4928`).

## Estado verificado (sello)
- **Gate: `178 passed / 0 skip / 0 fail`** — **25 goldens** del job `country-proof-invariant` en `:5434` (head `0064`), floor 173.
- Migraciones aditivas (`0057`-`0064`, 8). **Byte-idénticas ES.** Prod `:5433` sigue `0055`, intacta.
- Dep: `anyascii==0.3.3` (ISC, €0).
- **Veredicto red-team:** el universo entero de writers (≈40 connectors + 8 capas de fusión + geo/serving/monitoring) está country-scoped por identidad cdp/ULID, clave con país, o FK compuesto fail-closed — verificado línea-a-línea, no asumido.

## Cutover — ÚNICO gate del owner (irreversible, prod viva)
**(1)** aplicar `0057→0064` a `:5433` (ADITIVAS, byte-idénticas ES) **ANTES** que el código · **(2)** merge `feature/country-proof-build` → `main` · **(3)** re-correr el clustering servido en `:5433` · **(4)** job CI `country-proof-invariant` (25 goldens) + Ferrari verdes. **NO ejecutar sin "cutover" del owner.**

## OPEN — deuda DECLARADA (fase onboarding país-#2; NO core servido, NO atajos)
Matriz MSE exhaustividad (`capture.py`/`splink_merge`/`discovery_capture`), `geo_province.ccaa_code`/`geo_comarca.ine_code CHAR(2)`, `ingest.py` gate `01..52`, write-site default-ES de scrapers, `product_stats`/`/stats`, `canonical_key_backfill` (NULL-seguro), `phone_es`, `price_sanity` EUR. Documentado en la biblia; se cierra al onboardar el país #2. Test infra: `test_api_*`/`test_gestionador` hard-pinned a `:5433` → migrar a `CARDEEP_DSN`.

## Resume
1. Re-corre el gate: `CARDEEP_DSN=…:5434 pytest` los **25 ficheros** del job `country-proof-invariant` (`ci.yml`) → 178 passed.
2. El invariante COUNTRY-PROOF del censo servido está **cerrado, gateado y adversarialmente sellado**. Pendiente: el **cutover** (owner) y la deuda país-#2. **`:5433` jamás se toca.**
