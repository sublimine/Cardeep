# RECON SU-A3 — Estado de exhaustividad del scrapeo (B9 coverage gate)

> Auditor: agente de reconocimiento (Sonnet)
> Fecha: 2026-06-15
> DB: `cardeep-pg` :5433 · fuente real
> Metodología: [VERIFICADO DB] = query directa · [VERIFICADO código] = lectura de fichero real · [ASUMIDO] = inferencia declarada
> Propósito: insumo para el Director (Opus) que planifica SU-A3.

---

## 1. ¿Qué es el B9 coverage gate? [VERIFICADO código + DB]

**Implementación:** `pipeline/ops/coverage_verify.py` · `pipeline/ops/health.py` (l. 239-252)

El gate B9 es un mecanismo post-harvest que se dispara **automáticamente** cuando un conector llama a `record_run(..., declared_total=N)` con un valor no-None después de una corrida exitosa (`ok=True`). Flujo:

```
record_run(ok=True, declared_total=N)
  └─► verify_coverage(conn, source_key, declared_total=N, ...)
        Path A: captured_db = COUNT(vehicle WHERE status='available' JOIN entity_source WHERE source_key=K)
        Path B: db_edges  = COUNT(platform_listing WHERE platform_entity_ulid=P)  [si se pasa platform_ulid]
        Veredicto: record_count_verdict(paths={captured_db, declared_total}, tolerance=0.30)
        UPSERT source_coverage (declared, captured, db_edges, coverage_pct, verdict)
        Alerta: si coverage_pct < 0.85 → fire 'under' · si > 1.15 → fire 'over'
```

**El gate NO corre scraping adicional: €0.** Solo lee la DB y calcula ratios.

**Definición de `Σleaf==declared`** en este sistema:
- `declared_total` = lo que la fuente DECLARA en su primera página (totalHits / numberOfResults / equivalente)
- `captured_db` = vehículos distintos en DB atribuibles a esa fuente
- Gate TRUSTWORTHY si `0.85 ≤ captured_db/declared_total ≤ 1.15`
- REFUTED si diverge por encima o por debajo de esos umbrales

**¿Existe implementación?** Sí, está construida, testeada e integrada en `pipeline/ops/` y conectores Tier-1 principales. [VERIFICADO código]

---

## 2. Las 47 fuentes — estado exhaustivo [VERIFICADO DB]

Hay exactamente **47 filas en `source_health`** (confirmado con query). La tabla `source_coverage` tiene 4 filas (las únicas con gate B9 corrido).

### 2.1 Cuáles conectores están instrumentados para B9 [VERIFICADO código]

Solo 5 módulos de platform pasan `declared_total` a `record_run` (condición necesaria para que el gate B9 se dispare):

| Módulo | source_key | B9 Instrumentado |
|--------|-----------|-----------------|
| `autoscout24_wholesale.py` | `as24_wholesale` | SÍ |
| `autocasion_wholesale.py` | `autocasion_wholesale` | SÍ |
| `coches_net_wholesale.py` | `coches_net_wholesale` | SÍ |
| `milanuncios_wholesale.py` | `milanuncios_wholesale` | SÍ |
| `wallapop_wholesale.py` | `wallapop_wholesale` | SÍ |

Los 42 conectores restantes llaman `record_run()` sin `declared_total`. El gate no corre para ellos — no crashea, simplemente no produce fila en `source_coverage`.

### 2.2 Tabla de las 47 fuentes — estado de exhaustividad

| # | source_key | Tier-1 | Status | Runs | Vehicles DB | B9 Corrido | declared | captured_db | coverage_pct | Veredicto | Drain |
|---|-----------|--------|--------|------|-------------|-----------|---------|------------|-------------|-----------|-------|
| 1 | `coches_net_wholesale` | SÍ | healthy | 19 | 274.138 | **SÍ** | 272.000 | 274.138 | 100,8% | **TRUSTWORTHY** | COMPLETO |
| 2 | `wallapop_wholesale` | SÍ | healthy | 12 | 588.011 | **SÍ** | 651.000 | 588.011 | 90,3% | **TRUSTWORTHY** | ~90% (gap ~67k+legacy) |
| 3 | `milanuncios_wholesale` | SÍ | healthy | 10 | 397.012 | **SÍ** | 110.000 | 397.012 | 360,9% | **REFUTED** | INFLADO (over-coverage) |
| 4 | `autocasion_wholesale` | SÍ | degraded | 10 | 111.844 | SÍ pero sin gate* | — | — | — | — | PARCIAL (último run falló timeout) |
| 5 | `motor_es_wholesale` | SÍ | degraded | 7 | 49.009 | NO | — | — | — | — | PARCIAL (degraded, último run falló) |
| 6 | `coches_com_wholesale` | SÍ | healthy | 16 | 92.088 | NO** | — | — | — | — | ¿COMPLETO? (sin gate) |
| 7 | `as24_wholesale` | NO*** | (no en SH) | — | 14.640 | **SÍ** | 65.000 | 14.640 | 22,5% | **REFUTED** | PROOF SLICE (no drain real) |
| 8 | `family_dms_vendor_platforms` | NO | healthy | 9 | 2.034 | NO | — | — | — | — | sin gate |
| 9 | `family_cms_wp` | NO | healthy | 8 | 599 | NO | — | — | — | — | sin gate |
| 10 | `family_dealerk_wp` | NO | healthy | 7 | 2.983 | NO | — | — | — | — | sin gate |
| 11 | `oem_volvo_jlr_suzuki_wholesale` | NO | healthy | 7 | 1.801 | NO | — | — | — | — | sin gate |
| 12 | `family_generic_custom` | NO | healthy | 6 | 1.640 | NO | — | — | — | — | sin gate |
| 13 | `group_subastas_wholesale` | NO | healthy | 6 | 3.977 | NO | — | — | — | — | sin gate |
| 14 | `oem_kia_wholesale` | NO | healthy | 6 | 1.519 | NO | — | — | — | — | sin gate |
| 15 | `oem_hyundai_wholesale` | NO | healthy | 5 | 1.994 | NO | — | — | — | — | sin gate |
| 16 | `spoticar_wholesale` | NO | healthy | 5 | 6.138 | NO | — | — | — | — | sin gate |
| 17 | `family_builder_wholesale` | NO | healthy | 4 | 1.781 | NO | — | — | — | — | sin gate |
| 18 | `group_vo_chains_flexicar` | NO | healthy | 4 | 23.874 | NO | — | — | — | — | sin gate |
| 19 | `oem_bmw_premium_selection_wholesale` | NO | healthy | 4 | 2.883 | NO | — | — | — | — | sin gate |
| 20 | `oem_toyota_lexus_wholesale` | NO | healthy | 4 | 3.834 | NO | — | — | — | — | sin gate |
| 21 | `group_rentacar_vo_okmobility` | NO | healthy | 3 | 169 | NO | — | — | — | — | sin gate |
| 22 | `mercedes_benz_wholesale` | NO | healthy | 3 | 4.792 | NO | — | — | — | — | sin gate |
| 23 | `nissan_intelligent_choice_wholesale` | NO | healthy | 3 | 1.622 | NO | — | — | — | — | sin gate |
| 24 | `oem_audi_wholesale` | NO | healthy | 3 | 3.798 | NO | — | — | — | — | sin gate |
| 25 | `oem_mini_next_wholesale` | NO | healthy | 3 | 772 | NO | — | — | — | — | sin gate |
| 26 | `oem_seat_cupra_new_stock` | NO | healthy | 3 | 2.229 | NO | — | — | — | — | sin gate |
| 27 | `oem_seat_cupra_wholesale` | NO | healthy | 3 | 1.323 | NO | — | — | — | — | sin gate |
| 28 | `racc_ocasion_wholesale` | NO | healthy | 3 | 96 | NO | — | — | — | — | sin gate |
| 29 | `carandclassic_wholesale` | NO | healthy | 2 | 585 | NO | — | — | — | — | sin gate |
| 30 | `dasweltauto_wholesale` | NO | healthy | 2 | 552 | NO | — | — | — | — | sin gate |
| 31 | `faciliteacoches_wholesale` | NO | healthy | 2 | 788 | NO | — | — | — | — | sin gate |
| 32 | `family_framework_webbuilder` | NO | healthy | 2 | 680 | NO | — | — | — | — | sin gate |
| 33 | `family_unreachable` | NO | healthy | 2 | 246 | NO | — | — | — | — | sin gate |
| 34 | `group_importador_modrive` | NO | healthy | 2 | 19 | NO | — | — | — | — | sin gate |
| 35 | `group_rentacar_vo_athlon` | NO | healthy | 2 | 52 | NO | — | — | — | — | sin gate |
| 36 | `group_rentacar_vo_centauro` | NO | healthy | 2 | 28 | NO | — | — | — | — | sin gate |
| 37 | `group_rentacar_vo_recordgo` | NO | healthy | 2 | 18 | NO | — | — | — | — | sin gate |
| 38 | `group_vo_chains_carplus` | NO | healthy | 2 | 412 | NO | — | — | — | — | sin gate |
| 39 | `group_vo_chains_clicars` | NO | healthy | 2 | 1.470 | NO | — | — | — | — | sin gate |
| 40 | `group_vo_chains_ocasionplus` | NO | degraded | 2 | 13.445 | NO | — | — | — | — | PARCIAL (1 fallo) |
| 41 | `localizavo_wholesale` | NO | healthy | 2 | 318 | NO | — | — | — | — | sin gate |
| 42 | `motorflash_wholesale` | NO | healthy | 2 | 3.868 | NO | — | — | — | — | sin gate |
| 43 | `oem_ford_wholesale` | NO | healthy | 2 | 543 | NO | — | — | — | — | sin gate |
| 44 | `renew_wholesale` | NO | healthy | 2 | 918 | NO | — | — | — | — | sin gate |
| 45 | `group_rentacar_vo_arval` | NO | healthy | 1 | 1.172 | NO | — | — | — | — | sin gate |
| 46 | `group_rentacar_vo_northgate` | NO | healthy | 1 | 108 | NO | — | — | — | — | sin gate |
| 47 | `miclasico_wholesale` | NO | healthy | 1 | 959 | NO | — | — | — | — | sin gate |
| 48 | `subastacar_wholesale` | NO | healthy | 1 | 233 | NO | — | — | — | — | sin gate |

Notas:
- `*` autocasion: el módulo pasa `declared_total=stats.get("declared_full")` pero el último run falló por timeout con 111.619 filas. El gate no se ha disparado porque ok=False. No hay fila en source_coverage.
- `**` coches_com: tiene `declared_total_observed` hardcoded en comentario (92.312) pero el `record_run()` al final NO pasa `declared_total`. No instrumentado para el gate.
- `***` as24_wholesale no aparece en `source_health` (47 rows NO lo incluyen); sí aparece en `source_coverage` y `entity_source`. Tiene run en `harvest_run` si — hubo al menos una corrida que disparó el gate.

---

## 3. El issue AS24/milanuncios REFUTED [VERIFICADO código + DB]

### 3.1 AS24 REFUTED — causa raíz

**Estado actual:** REFUTED · declared=65.000 · captured_db=14.640 · coverage=22,5%

**Causa raíz confirmada:** `autoscout24_wholesale.py` opera en modo **PROOF SLICE** con `DEFAULT_MAX_PAGES = 12`. Eso implica `~12 × 20 = ~240 listados por run` — no un drain real. Los 14.640 en DB son acumulación de múltiples proof-slices pasados, pero frente a los 278k (~65k filtrado ES) que AS24 declara, la ratio queda en 22,5% → REFUTED.

**El código lo documenta explícitamente** (autoscout24_wholesale.py l.15):
> "PROOF SLICE, NOT THE FULL HARVEST. AS24 declares ~278k results; draining all of it [...] is a P1 governor task."

**¿Está resuelto?** NO. El módulo AS24 wholesale está diseñado intencionalmente para proof-slice, no para drain completo. La alerta activa (`as24_wholesale:coverage`) es correcta. El drain real de AS24 requiere `max_pages` grande (equivalente a 278k/20 ≈ 13.900 páginas) bajo governor P1, que no se ha ejecutado.

### 3.2 Milanuncios REFUTED — causa raíz

**Estado actual:** REFUTED · declared=110.000 · captured_db=397.012 · coverage=360,9%

**Causa raíz:** `_COVERAGE_CEILING = 1.15` en `coverage_verify.py`. El módulo milanuncios pasa `declared_total = stats.get("coverage_sum") or stats.get("declared_full")`, que es el totalHits de la primera partición o la suma de particiones. Milanuncios usa paginación province×price-band; el `declared_total` que se pasa (110.000) es solo una **muestra del primer shard**, mientras que la DB ya acumula corridas anteriores de multiples shards = 397.012 total.

**Historial de veredictos:** La primera vez (la misma noche) se emitió TRUSTWORTHY porque `db_edges` (397k) y `captured_db` (397k) convergían. Luego se ajustó la lógica para no usar `db_edges` como path de coverage (era un echo de sí misma), y ahora con solo `captured_db` vs `declared` (110k) la divergencia es real y REFUTED.

**¿Está resuelto?** NO. El problema fundamental es que `declared_total` para milanuncios está mal medido: debería ser la suma de todos los partition-totalHits de la corrida completa (agregado real del inventario ES), no el primero que se lee. El 110k declarado es un undercount severo del total real.

---

## 4. Estado de inventario por fuente — señales de drain incompleto [VERIFICADO DB]

### 4.1 Fuentes con señal clara de drain incompleto

| Fuente | Evidencia de incompleto |
|--------|------------------------|
| `as24_wholesale` | 14.640/65.000 = 22,5% · REFUTED · proof-slice por diseño |
| `wallapop_wholesale` | 588k/651k = 90,3% · gap ~67k + 22.900 legacy buckets no migrados |
| `milanuncios_wholesale` | declared bajo (110k) pero DB = 397k; drain puede ser completo, gate está roto por declared_total mal calculado |
| `autocasion_wholesale` | 111.844 en DB pero último run falló timeout después de 111.619 rows; drain interrumpido |
| `motor_es_wholesale` | 49.009 pero degraded + fallo reciente (404 en pág 51 = paginación cortada) |
| `group_vo_chains_ocasionplus` | 13.445 pero status degraded, 1 fallo reciente |

### 4.2 Fuentes con drain aparentemente completo pero sin gate

42 fuentes han corrido con éxito y producen inventario, pero no tienen `declared_total` instrumentado → no hay evidencia formal de exhaustividad. No se puede decir si están completas o truncadas.

### 4.3 Fuentes con inventario sorprendentemente bajo (posible drain incompleto no detectado)

| Fuente | Vehicles | Señal |
|--------|----------|-------|
| `group_importador_modrive` | 19 | Solo 2 runs; volumen real no conocido |
| `group_rentacar_vo_recordgo` | 18 | Solo 2 runs |
| `group_rentacar_vo_centauro` | 28 | Solo 2 runs |
| `oem_byd` | 32 | Solo aparece en entity_source, no en source_health |
| `localizavo_wholesale` | 318 | 2 runs |

---

## 5. Recetas / runbook [VERIFICADO filesystem]

- **`countries/ES/recipes/`**: 585 archivos YAML (recetas por dealer con cdp_code).
- Estas son recetas individuales por dealer, no por fuente.
- **Runbook de fuente**: existe `docs/RUNBOOK.md` y `docs/architecture/` con docs específicos por fuente para Tier-1 (wallapop.md, segment_gaps.md, tier1_recipes/).
- **Sin runbook de gate B9 por fuente**: no existe un archivo que documente `declared_total` esperado por cada una de las 47 fuentes. El gate se recalibra automáticamente en cada run si el conector está instrumentado.

---

## 6. Gap concreto hacia "47/47 gateadas con Σleaf==declared o causa" [VERIFICADO]

### Resumen del gap

| Categoría | N fuentes | Estado |
|-----------|-----------|--------|
| TRUSTWORTHY (gate pasado) | 2 | coches_net, wallapop |
| REFUTED (gate corrido, fallo conocido) | 2 | milanuncios, as24 |
| Instrumentadas pero gate no disparado (ok=False o declared=None) | 1 | autocasion |
| **No instrumentadas (no pasan declared_total)** | **42** | todos los demás |
| **TOTAL** | **47** | — |

**Gap real:** 45 fuentes sin veredicto de coverage. De esas 45:
- 1 (autocasion) tiene el código para instrumentarse pero su run falló antes de llegar al gate.
- 42 no tienen `declared_total` en su `record_run` → el gate **nunca correrá** para ellas sin modificar código.
- 1 (coches_com) tiene `declared_total_observed` hardcoded pero no lo pasa a `record_run`.
- 1 (motor_es) está degraded, tiene código para `_declared_total()` pero sin integración B9.

### Para llegar a 47/47:
1. **Instrumentar** los 42 conectores no-B9 con `declared_total` en su `record_run` (modificación de código).
2. **Correr una corrida exitosa** de cada fuente (para activar el gate).
3. **Resolver los 2 REFUTEDs**:
   - AS24: lanzar drain real (max_pages alto, P1 governor, ~13.900 páginas).
   - Milanuncios: corregir cálculo de `declared_total` (usar suma de todos los partition-totalHits, no el primero).

---

## 7. €0-verificable ahora vs requiere correr scrapers

### €0 verificable sin correr scrapers

- **Estado de 42 fuentes "sin gate"**: se puede calcular su coverage estimado offline comparando vehicle count en DB vs una estimación manual del declared por cada fuente. No requiere scraping.
- **Corrección declared_total de milanuncios**: solo cambio de código en `milanuncios_wholesale.py` → acumular `coverage_sum` de todos los partitions antes de llamar record_run.
- **Instrumentar coches_com**: pasar `declared_total=stats.get("declared_full")` en su `record_run` final (1 línea de código).

### Requiere correr scrapers (tiempo + recursos)

| Tarea | Coste estimado |
|-------|---------------|
| AS24 drain completo | 13.900 páginas × governor = varias horas de scraping, sin proxy ES (curl_cffi) |
| Wallapop completar 90%→100% | keyword×centroid sweep + legacy bucket migration = pocas horas |
| Autocasion re-run exitoso | 1 run sin timeout = ~2-3 horas (tiene 135k+ listings) |
| Motor.es fix + re-run | Fix el 404 (paginación rota pg51) + re-run = 1-2 horas |
| 42 fuentes no-instrumentadas: 1 run cada una | Ya tienen runs recientes; solo falta código para captured_total |

---

## 8. Riesgos y dudas honestas

1. **`as24_wholesale` no aparece en `source_health`** (47 rows, no está). Sí aparece en `entity_source` y `source_coverage` y `harvest_run`. [ASUMIDO: fue registrado por su primer run pero la fila en `source_health` no se insertó por la lógica UPSERT, o hay una discrepancia de source_key entre el run y el health check]. Esta discrepancia necesita ser investigada.

2. **42 fuentes sin denominador oficial conocido**: para la mayoría (OEM locators, group chains, rent-a-car) el `declared_total` real es fácil de obtener de la primera página del scraper. Para las `family_*` (multi-dealer) el concepto de `declared_total` es más complejo: cada dealer tiene su propio total y la fuente agrega N dealers. El gate B9 funciona por fuente agregada, no por dealer individual.

3. **Coverage por fuente ≠ exhaustividad global**: wallapop TRUSTWORTHY al 90,3% significa que el scraper drena el 90% del declarado por wallapop. Pero wallapop puede no declarar el 100% de su inventario (cursores saturan en ~224k de un total real mayor). La exhaustividad absoluta requiere drain completo a nivel cursor, no solo ratio declared.

4. **milanuncios declared_total está roto**: el veredicto REFUTED es un artefacto de cómo se calcula declared_total, no necesariamente de falta de inventario. El inventario puede estar completo; el gate está midiendo mal. Requiere auditoría adicional del `coverage_sum` real.

5. **Fuentes con `status=healthy` pero solo 1-2 runs**: no hay evidencia de que hayan completado un drain exhaustivo. Pueden haber sido ejecutadas parcialmente en el primer run y marcadas healthy por no tener errores.

---

## 9. Tabla resumen ejecutivo (para el Director)

| Dimensión | Estado actual |
|-----------|--------------|
| Gate B9 implementado | SÍ (pipeline/ops/coverage_verify.py) |
| Fuentes con gate corrido exitosamente | 2/47 (4,3%) |
| Fuentes TRUSTWORTHY | 2 (coches_net, wallapop) |
| Fuentes REFUTED | 2 (milanuncios declared_total roto, as24 proof-slice) |
| Fuentes con código B9 pero sin gate corrido | 1 (autocasion, run falló) |
| Fuentes sin instrumentación B9 | 42 (requieren modificación de código) |
| Brecha para 47/47 gateadas | 45 fuentes pendientes |
| Trabajo de código necesario | Instrumentar 42 conectores con declared_total |
| Trabajo de ejecución necesario | Re-run de todas + drain AS24 real |
| AS24 REFUTED resuelto | NO (proof-slice intencional, drain real nunca ejecutado) |
| Milanuncios REFUTED resuelto | NO (declared_total mal calculado en el conector) |
| Coste de instrumentación | €0 (solo código) |
| Coste de drain completo | €0 (scrapers locales) + tiempo de cómputo |

*Generado 2026-06-15. Números de DB [VERIFICADO] con queries directas. Afirmaciones sobre código [VERIFICADO] con lectura de ficheros.*

---

## ADDENDUM DEL DIRECTOR (Opus, 2026-06-15) — diagnóstico profundo del B9

Leí `pipeline/platform/milanuncios_wholesale.py` + `pipeline/ops/coverage_verify.py`. El recon simplificó ("primer shard"); la verdad verificada:

- El conector milanuncios **SÍ pasa `coverage_sum`** (suma de TODAS las particiones province×price-band de ESA corrida-segmento), no el primer shard. La lógica de partición es sólida (FACET province 1..52, sub-shard por banda de precio hasta `eq`<10k, conteo exacto vía `pagination.totalHits.relation`).
- **Raíz del REFUTED = DESAJUSTE DE SCOPE en `verify_coverage` Path A**: `captured_db = count(DISTINCT vehicle available JOIN entity_source source_key='milanuncios_wholesale')` cuenta el ACUMULADO de la DB — todas las corridas, todos los segmentos. El `declared_total` es el `coverage_sum` de UNA corrida-segmento. Comparar 397k (acumulado multi-segmento) vs 110k (un segmento) = 360% espurio. **No es bug de 1 línea.**
- **Segunda causa posible**: `captured_db` filtra `status='available'`; si la detección GONE no marca bajas, se infla con stale-available. Hay que medir frescura (cuántos de los 397k son actuales).

**Decisión de diseño del Director (B9 v2) — para que A3 sea fiable:**
1. El gate debe comparar MISMO SCOPE. Opciones: (a) `declared_total` = total nacional all-segments (el conector suma `coverage_sum` across segments en una corrida full-index antes de `record_run`); (b) `captured_db` scopeado por segmento (requiere segment-tag — más invasivo). Preferida: (a).
2. Single-scope-single-run (coches_net) ya es correcto — no tocar.
3. Multi-segmento/multi-run (milanuncios, wallapop) necesita alineación de scope + verificación de frescura (GONE).
4. **AS24: el REFUTED es CORRECTO** (proof-slice por diseño; drain real pendiente, gated por D1=capacidad PC). Sellar como GAP-DECLARADO hasta el drain.

**Plan SU-A3 reordenado:** (1) B9 v2 scope-alignment + freshness [diseño+código, €0]; (2) instrumentar los 42 [€0 código + 1 run c/u, paced D1]; (3) drains pendientes AS24/wallapop-100%/autocasion/motor.es [paced D1, con evicción por disco 93%].
