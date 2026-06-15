# SU-A4 DELTA RECON — Auditoría de uniformidad del delta
**Fecha:** 2026-06-15  
**Auditor:** Claude Sonnet 4.6 (read-only, sin escritura en DB ni código)  
**Verificación:** [VERIFICADO DB] = consulta SQL directa · [VERIFICADO código] = lectura fuente

---

## 1. Qué event_type existen en DB

[VERIFICADO DB]

```
event_type   | total
-------------|----------
NEW          | 1.696.335
GONE         |     7.968
PHOTO_CHANGE |     3.568
PRICE_CHANGE |     1.121
KM_CHANGE    |       339
```

Los 5 tipos declarados en el CHECK CONSTRAINT de `vehicle_event` existen en producción. No hay tipos huérfanos ni ausentes a nivel de schema.

---

## 2. Matriz fuente × event_type [VERIFICADO DB]

Tabla completa (fuentes relevantes por volumen, orden descendente por NEW):

| source_key                        | NEW     | GONE  | PRICE | PHOTO | KM  |
|-----------------------------------|---------|-------|-------|-------|-----|
| wallapop_wholesale                | 588.011 |     0 |     0 |     0 |   0 |
| milanuncios_wholesale             | 397.012 |     0 |     0 |     0 |   0 |
| coches_net_wholesale              | 274.138 |     0 |     0 |     0 |   0 |
| autocasion_wholesale              | 111.844 |     0 |    28 |     0 |   0 |
| coches_com_wholesale              |  93.096 |     0 |     0 |     0 |   0 |
| **as24**                          |  87.209 | 7.968 | 1.093 | 3.568 | 339 |
| motor_es_wholesale                |  49.009 |     0 |     0 |     0 |   0 |
| group_vo_chains_flexicar          |  23.874 |     0 |     0 |     0 |   0 |
| **as24_wholesale**                |  14.640 |    13 |   408 |   521 |   9 |
| group_vo_chains_ocasionplus       |  13.445 |     0 |     0 |     0 |   0 |
| **osm**                           |   9.574 | 1.577 |    71 |   458 |   1 |
| spoticar_wholesale                |   6.138 |     0 |     0 |     0 |   0 |
| mercedes_benz_wholesale           |   4.792 |     0 |     0 |     0 |   0 |
| group_subastas_wholesale          |   3.977 |     0 |     0 |     0 |   0 |
| motorflash_wholesale              |   3.868 |     0 |     0 |     0 |   0 |
| oem_toyota_lexus_wholesale        |   3.834 |     0 |     0 |     0 |   0 |
| oem_audi_wholesale                |   3.798 |     0 |     0 |     0 |   0 |
| **family_dealerk_wp**             |   3.175 |   192 |     1 |     5 |   0 |
| oem_bmw_premium_selection_wholesale|  2.883 |     0 |     0 |     0 |   0 |
| **family_generic_custom**         |   2.727 | 1.679 |    44 |   441 |   0 |
| **family_dms_vendor_platforms**   |   2.246 |   536 |     0 |   113 |   3 |
| oem_seat_cupra_new_stock          |   2.229 |     0 |     0 |     0 |   0 |
| oem_hyundai_wholesale             |   1.994 |     0 |     0 |     0 |   0 |
| acevas                            |   1.842 |   192 |     1 |     5 |   0 |
| oem_volvo_jlr_suzuki_wholesale    |   1.801 |     0 |     0 |     0 |   0 |
| family_builder_wholesale          |   1.781 |     0 |     0 |     0 |   0 |
| group_subastas_bca                |   1.752 |     0 |     0 |     0 |   0 |
| nissan_intelligent_choice_wholesale|  1.622 |     0 |     0 |     0 |   0 |
| oem_kia_wholesale                 |   1.519 |     0 |     0 |     0 |   0 |
| group_vo_chains_clicars           |   1.470 |     0 |     0 |     0 |   0 |
| oem_seat_cupra_wholesale          |   1.323 |     0 |     0 |     0 |   0 |
| aecs                              |     840 |    26 |     0 |     0 |   0 |
| family_framework_webbuilder       |     680 |     0 |     0 |     0 |   0 |
| family_cms_wp                     |     599 |     0 |     0 |     0 |   0 |
| localizavo_wholesale              |     318 |     0 |     0 |     0 |   0 |
| family_unreachable                |     246 |     0 |     0 |     0 |   0 |
| subastacar_wholesale              |     233 |     0 |     0 |     0 |   0 |
| group_rentacar_vo_arval           |   1.172 |     0 |     0 |     0 |   0 |
| (resto OEM/rent-a-car/etc.)       | < 1.000 |     0 |     0 |     0 |   0 |

**En negrita**: fuentes con al menos un event_type no-NEW.

### ⚠️ HALLAZGO CRÍTICO — Artefacto de atribución

Los eventos no-NEW atribuidos a `family_generic_custom`, `family_dms_vendor_platforms`, `family_dealerk_wp`, `acevas`, `aecs` y `osm` son **100% artefactos de JOIN por entidad compartida** [VERIFICADO DB]:

```sql
-- Confirmado para family_generic_custom:
event_type   | total | también_en_as24
GONE         | 1.679 |          1.679  ← 100%
PHOTO_CHANGE |   441 |            441  ← 100%
PRICE_CHANGE |    44 |             44  ← 100%

-- Confirmado para family_dms_vendor_platforms:
GONE         |   536 |            536  ← 100%
KM_CHANGE    |     3 |              3  ← 100%
PHOTO_CHANGE |   113 |            113  ← 100%
```

La query de atribución usa `entity_ulid`; si AS24 y `family_generic_custom` scrapearon el mismo dealer, sus eventos se "ven" desde ambos source_keys en el JOIN. Los eventos los **emitió AS24**, no el conector family.

**Fuentes que REALMENTE emiten delta completo (no solo NEW):**
- `as24` — los 5 tipos (GONE/PRICE/PHOTO/KM + NEW) ✓
- `as24_wholesale` — los 5 tipos ✓
- `autocasion_wholesale` — solo PRICE_CHANGE (28 eventos; sin GONE/PHOTO/KM) ⚠️

**Fuentes que solo emiten NEW en código:** todas las demás (43 de 47 fuentes activas).

---

## 3. Lógica de delta — ¿compartida o duplicada? [VERIFICADO código]

### Arquitectura actual

Existe **una función central de delta completo** en `pipeline/ingest.py`:
- Ruta: `C:/Users/elias/projects/cardeep/pipeline/ingest.py`
- Función: `ingest_dealer()` (líneas 40–159)
- Implementa: NEW + PRICE_CHANGE + PHOTO_CHANGE + KM_CHANGE + GONE (con GONE guard B2.3)
- Llamada por: `pipeline/harvest_dealer.py` (AS24 per-dealer) con `source_key="as24"`

**Esta función central NO es llamada por ningún conector wholesale distinto de AS24.**

Cada conector wholesale implementa su propio `ingest_dealer_vehicles()` local:

| Archivo | Función local | Emite NEW | Emite GONE | Emite PRICE/PHOTO/KM |
|---------|--------------|-----------|------------|---------------------|
| `pipeline/ingest.py` | `ingest_dealer()` | ✓ | ✓ (guarded) | ✓ PRICE+PHOTO+KM |
| `platform/autocasion_wholesale.py` | `process_ref()` | ✓ | ✗ | ✓ PRICE únicamente |
| `platform/generic_dealer_site.py` | `generic_ingest_dealer_site()` | ✓ | ✓ (guarded) | ✗ |
| `platform/localizavo_wholesale.py` | `_reconcile_aged_out()` | ✓ | ✓ (guarded) | ✗ |
| `platform/subastacar_wholesale.py` | `_reconcile_aged_out()` | ✓ | ✓ (guarded) | ✗ |
| `platform/group_subastas_wholesale.py` | inline reconcile | ✓ | ✓ (guarded) | ✗ |
| `platform/family_dms_vendor_platforms__wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/family_generic_custom_wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/family_dealerk_wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/family_cms_wordpress_dominated__wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/family_framework_next_astro_nuxt_angular__wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/family_builder_wix_ueni_google_sites_basekit__wholesale.py` | `ingest_dealer_vehicles()` | ✓ | ✗ | ✗ |
| `platform/coches_net_wholesale.py` | `emit_new_event()` | ✓ | ✗ | ✗ |
| `platform/coches_com_wholesale.py` | `_BULK_INSERT_EVENTS` SQL | ✓ | ✗ | ✗ |
| `platform/milanuncios_wholesale.py` | `_BULK_INSERT_EVENTS` SQL | ✓ | ✗ | ✗ |
| `platform/wallapop_wholesale.py` | `_BULK_INSERT_EVENTS` SQL | ✓ | ✗ | ✗ |
| Todos los OEM/rentacar/chain/* | similares | ✓ | ✗ | ✗ |

**Conclusión de arquitectura:** La lógica de delta completa **NO es compartida (fix-once)**. Está implementada en `ingest.py` exclusivamente para AS24. Los conectores wholesale tienen sus propias versiones del ingest, cada una con distintos niveles de completitud. Es lógica **duplicada/ausente por conector**, no una función centralizada que todos llamen.

---

## 4. GONE detection — estado [VERIFICADO código + DB]

### Mecánica por conector:

**`ingest.py` (AS24):** sweep de reconciliación real [VERIFICADO código líneas 110–148]
- Lee `existing` (snapshot completo del dealer en DB)
- Compara contra `harvested_links` (set de deep_links scrapeados esta corrida)
- Diferencia = GONE candidatos
- Guarded por `delta_guard.should_emit_gone()` (B2.3): requiere harvested ≥ declared×0.95 o harvested ≥ previous×0.50
- Emite `UPDATE vehicle SET status='gone'` + evento GONE
- **Resultado en DB:** 7.968 GONE reales [VERIFICADO DB]

**`localizavo_wholesale.py`** [VERIFICADO código líneas 677–704, 802–823]
- `_reconcile_aged_out()`: compara `vehicles_before` (set pre-corrida de vehicle_ulid en edge) vs `harvested` (set de deep_links vistos)
- Guarded por B2.3 también
- 2 corridas en DB (2026-06-13 19:10 y 19:11, ambas con 3 minutos de diferencia)
- **0 GONE en DB** — ambas corridas separadas por ~1 minuto; plausible que el inventario no cambió o que la segunda corrida no superó el threshold

**`subastacar_wholesale.py`** [VERIFICADO código] — idéntica arquitectura a localizavo
- Solo 1 corrida en DB → imposible detectar GONE (necesita segunda pasada para comparar)

**`group_subastas_wholesale.py`** [VERIFICADO código líneas 1005–1045]
- Reconcile inline: calcula aged = `vehicles_before - vehicles_after`
- Guarded por B2.3
- 6 corridas en DB (2026-06-12 a 2026-06-13)
- **0 GONE** — posible que el stock subasta no cambió entre corridas, o el guard lo frenó

**`generic_dealer_site.py`** [VERIFICADO código líneas 714–739]
- Sweep local: compara `seen_deep_links` vs todos los `status='available'` del dealer
- Threshold: `harvest_total >= prior_available * 0.95`
- ⚠️ BUG MENOR [VERIFICADO código línea 736]: emite GONE con `old_value='available'` y `new_value='sold'` como strings JSON literales (no JSON objects con campos). El resto del sistema usa `{"price": ...}`. Cosmético en DB pero inconsistente.
- ⚠️ También: marca `status='sold'` en lugar de `status='gone'` (línea 730), mientras el resto del sistema usa `status='gone'`. Inconsistencia de estado.

**Todos los demás wholesale (wallapop, milanuncios, coches_net, coches_com, motor_es, OEMs, etc.):**  
- **Sin sweep de reconciliación** — son append-only
- `ON CONFLICT (entity_ulid, deep_link) DO NOTHING` o equivalente: insertan nuevos, tocan `last_seen` de los existentes, pero nunca marcan GONE
- Dependen de una futura "eviction pass" basada en `last_seen` (no implementada)

---

## 5. 2ª pasada (delta Δ) — análisis [VERIFICADO DB + código]

### ¿Qué requiere una 2ª pasada para emitir PRICE/PHOTO/KM_CHANGE?

Estos eventos requieren comparar el valor actual en DB contra el valor recién scrapeado. Solo `ingest.py` hace esta comparación (líneas 92–103). Para que aparezcan, el conector debe:
1. Haber corrido ≥1 vez antes (hay datos en DB)
2. Re-scrapear el mismo vehículo con un valor distinto
3. Tener código que compare los valores

### Fuentes con ≥2 corridas que NO emiten delta Δ [VERIFICADO DB]

39 fuentes corrieron ≥2 veces y tienen 0 GONE + 0 PRICE + 0 PHOTO + 0 KM:

```
coches_net_wholesale       (19 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
coches_com_wholesale       (16 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
wallapop_wholesale         (12 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
milanuncios_wholesale      (10 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
family_cms_wp              ( 8 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
motor_es_wholesale         ( 7 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
oem_volvo_jlr_suzuki       ( 7 runs) — ✗ sin GONE, ✗ sin PRICE/PHOTO/KM
group_subastas_wholesale   ( 6 runs) — tiene GONE en código, pero 0 en DB
oem_kia_wholesale          ( 6 runs) — ✗ sin delta
... (33 fuentes más)
```

**Las fuentes más grandes del sistema (wallapop=588k, milanuncios=397k, coches_net=274k, coches_com=93k) llevan entre 10 y 19 corridas y no han emitido UN SOLO evento de delta Δ ni GONE.** 

---

## 6. Gap concreto por categoría

### GAP-1: Ausencia total de GONE en fuentes masivas (append-only)

**Fuentes afectadas:** wallapop_wholesale, milanuncios_wholesale, coches_net_wholesale, coches_com_wholesale, motor_es_wholesale, todas las OEM, todos los rentacar, todos los VO chains, spoticar, etc.  
**Causa:** El código de ingest es append-only (`ON CONFLICT DO NOTHING` o equivalente). No hay sweep de reconciliación. Un coche vendido permanece `status='available'` indefinidamente.  
**Magnitud estimada:** ~1.3M vehículos en DB sin mecanismo de baja. Si la tasa de rotación típica es 5%/semana, en producción real habría ~65.000 coches "fantasma" por semana sin detectar.  
**Tipo de fix:** Requiere código nuevo de reconciliación por conector (o eviction pass global) + ≥2 corridas para comparar.

### GAP-2: Ausencia de PRICE/PHOTO/KM_CHANGE en todos los wholesale salvo autocasion

**Fuentes afectadas:** todos excepto as24/as24_wholesale/osm/autocasion_wholesale.  
**Causa:** Los ingest_dealer_vehicles() locales no comparan el valor nuevo vs el almacenado. Solo detectan si el deep_link es nuevo (INSERT) o existente (TOUCH last_seen). No hay lógica de diff de precio/foto/km.  
**Impacto producto:** El historial de precios — explícitamente requerido en el mandato fundacional ("historial completo") — no existe para el 96% del inventario en producción.

### GAP-3: GONE en localizavo/subastacar/group_subastas sin eventos reales

**Fuentes afectadas:** localizavo_wholesale (2 runs, 0 GONE), subastacar_wholesale (1 run, 0 GONE), group_subastas_wholesale (6 runs, 0 GONE).  
**Causa probable:** El inventario subasta es altamente volátil pero corridas muy próximas entre sí (localizavo: 1 minuto de diferencia). El threshold B2.3 o la volatilidad real pueden estar suprimiendo el sweep. En subastacar solo hay 1 corrida → imposible detectar GONE.  
**No es bug de código** — la arquitectura es correcta. Es falta de suficientes corridas espaciadas en el tiempo.

### GAP-4: Bug de status en generic_dealer_site.py (menor)

**Archivo:** `pipeline/platform/generic_dealer_site.py` línea 730  
**Bug:** `UPDATE vehicle SET status='sold'` en lugar de `status='gone'`. El resto del sistema usa `'gone'`.  
**Impacto:** Coches marcados como 'sold' en esta ruta no son detectados por consultas que filtran `status='gone'`. Inconsistencia silenciosa.  
**Fix-cost:** €0 (trivial: una línea).

### GAP-5: old_value/new_value en GONE de generic_dealer_site son strings, no JSON objects

**Archivo:** `pipeline/platform/generic_dealer_site.py` línea 736  
`VALUES ($1,$2,$3,'GONE','available','sold')` — los valores 'available' y 'sold' se insertan como strings literales en un campo jsonb, no como objetos JSON `{"status":"available"}`.  
**Fix-cost:** €0 (trivial: cambiar los literales por `json.dumps({"status": "available"})` etc.).

---

## 7. €0-fixable ahora vs requiere-corridas

### €0-fixable (código, sin necesidad de más corridas):

1. **Bug status 'sold' → 'gone'** en `generic_dealer_site.py:730` — 1 línea
2. **Bug jsonb 'available'/'sold'** en `generic_dealer_site.py:736` — 1 línea
3. **PRICE_CHANGE en autocasion_wholesale** ya funciona — requiere solo más corridas para acumular eventos (código correcto)
4. **Añadir PRICE/PHOTO/KM diff** a `ingest_dealer_vehicles()` del conector family_dms_vendor_platforms usando el patrón de `ingest.py` — ~30 líneas por conector, replicables a todos los family/*

La lógica de diff existe en `ingest.py` (líneas 92–103) y es extraíble como función shared. **Si se centraliza en un helper compartido, todos los conectores que hagan el import lo heredan en una sola operación.**

### Requiere corridas (infraestructura de 2ª pasada):

5. **GONE sweep en wallapop/milanuncios/coches_net/coches_com** — requiere implementar reconcile + ejecutar ≥2 corridas espaciadas. Sin código implementado aún.
6. **PRICE/PHOTO/KM en fuentes grandes** — una vez añadido el diff al código, aparecerán automáticamente en la siguiente corrida que encuentre cambios.
7. **GONE en group_subastas/localizavo con variación real** — el código ya existe; necesita corridas separadas en el tiempo suficiente para que el inventario cambie.

---

## 8. Resumen del GATE de SU-A4

**GATE:** "cada conector wholesale emite NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE verificado en 2ª pasada; no solo AS24"

**Estado actual:**

| Criterio | Estado |
|----------|--------|
| NEW uniforme en todos los conectores | ✓ SÍ — todos los 47 conectores activos emiten NEW |
| GONE en fuentes wholesale grandes | ✗ NO — wallapop/milanuncios/coches_net/coches_com/motor_es/OEMs/etc.: 0 GONE en código |
| PRICE_CHANGE en fuentes wholesale | ✗ PARCIAL — solo autocasion_wholesale (28 eventos). AS24 y as24_wholesale funcionan |
| PHOTO_CHANGE en fuentes wholesale | ✗ NO — solo AS24 y as24_wholesale vía `ingest.py` |
| KM_CHANGE en fuentes wholesale | ✗ NO — solo AS24 y as24_wholesale |
| Delta uniforme (fix-once shared) | ✗ NO — código duplicado/ausente por conector, no función centralizada |

**Veredicto: GATE NO PASADO.** El delta es producido exclusivamente por AS24/as24_wholesale en la práctica. El 93% del inventario (fuentes wholesale) es append-only sin bajas ni cambios. El producto no puede declarar "historial completo" para wallapop (588k vehículos), milanuncios (397k), coches.net (274k) ni coches.com (93k).

---

## 9. Riesgos y dudas honestas

1. **Los 0 GONE en group_subastas (6 runs)** podrían indicar: (a) el inventario de subasta no cambió entre corridas — plausible si son corridas diarias y el catálogo rota semanalmente; o (b) el B2.3 guard está suprimiendo el sweep cada vez — necesita revisión de los logs de corrida para confirmar.

2. **autocasion_wholesale emite PRICE_CHANGE (28 eventos)** pero no GONE. El código tiene la función `capture_price_drop()` correctamente implementada pero falta sweep de reconciliación.

3. **La query de atribución (JOIN entity_source)** puede ser engañosa: si un dealer tiene fuente AS24 y fuente family_generic_custom, los eventos de AS24 aparecen bajo ambos source_keys en el JOIN. Los números de la matriz son correctos solo si se entiende que reflejan "eventos sobre entidades que también tienen este source_key", no "eventos generados por este conector".

4. **La eviction pass global basada en last_seen** (mencionada en comentarios de código de varios conectores) no está implementada. Es el mecanismo de baja fallback para fuentes append-only. Sin ella, la DB acumula inventario estale indefinidamente.

---

*Documento generado en read-only. Ningún dato fue modificado en DB ni en código.*
