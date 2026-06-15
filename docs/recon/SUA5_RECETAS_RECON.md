# SU-A5 — Auditoría de Recetas: Modelo, Cobertura y Gaps
**Fecha:** 2026-06-15  
**Auditor:** Agente de reconocimiento (read-only)  
**Verdad:** código + DB verificados. Sin suposiciones.

---

## 1. El Modelo de Recetas [VERIFICADO]

### 1a. Qué es una receta

Un archivo YAML bajo `countries/ES/recipes/<cdp_code>.yaml`.  
Encabezado canónico: `# Cardeep extraction recipe — <cdp_code> / # Reusable; re-scrape without raw crude.`

**Captura los siguientes campos:**

| Campo | Descripción | Ejemplo |
|---|---|---|
| `version` | Versión de esquema (siempre 1 hoy) | `1` |
| `source` | Identificador de la fuente/portal | `seat_cupra`, `autoscout24`, `carplus.es` |
| `scope` | Tipo de stock y tecnología de la página | `platform-wholesale (OEM SPA + VTP JSON API)` |
| `engine` | Motor de extracción y fingerprint | `curl_cffi+chrome131_impersonate+vtp_internal_json_api` |
| `access` | Tipo de defensa + credenciales requeridas | `OPEN-via-fingerprint / t1_soft / €0` |
| `data_surface` | Superficie de datos | `internal_api`, `json_ld`, `ssr_html` |
| `endpoint` | URL de la SRP / API con parámetros de paginación | `GET https://vtpapi.seat.com/restapi/...` |
| `enumeration` | Estrategia de paginación completa | `page=1..ceil(total/96)` + condición de fin |
| `denominator` | Cómo verificar el total declarado (VAM) | `x-result-number (response header)` |
| `field_map` | Mapeo campo→path en el payload | `deep_link`, `vin`, `make`, `model`, `year`, `km`, `price`, `fuel`, `transmission`, `photo`, `dealer`, `location` |
| `platform_entity` | Metadatos de la entidad-plataforma en DB | `kind=oem_vo_portal, province_code=NULL, is_tier1=TRUE, defense_tier=t1_soft` |
| `caveats` | Trampas conocidas específicas del portal | codificación, paginación irregular, VIN ausente, etc. |

**Una receta completa es suficiente para re-scrapear sin tocar el código raw**: contiene el endpoint, la estrategia de paginación, el mapeo de campos y las trampas conocidas.

### 1b. Tipos de receta

Existen **dos niveles** de receta:

**Nivel A — Receta per-conector (35 YAML, sentinel province_code=00):**
- Una receta por plataforma/conector (milanuncios, wallapop, coches.net, CUPRA, Mercedes, Flexicar, etc.).
- El cdp_code de estos YAML tiene province_code `00` (sentinel: la plataforma no tiene provincia propia).
- Ejemplos verificados: `CDP-ES-00-3N995HG6.yaml` (CUPRA seat_cupra), `CDP-ES-00-4YVMXZ3T.yaml` (Carplus chain), `CDP-ES-00-58C3W3P9.yaml` (RACC).
- **Estas recetas cubren a todos los dealers descubiertos a través de ese conector.**

**Nivel B — Receta per-dealer individual (550 YAML, province_code real):**
- Una receta por dealer específico, identificado con su cdp_code completo (e.g., `CDP-ES-01-02E10MVS.yaml`).
- **Verificado**: los 550 son recetas AS24 genéricas (contenido idéntico: `source: autoscout24, engine: http+next_data`). La función `write_recipe()` en `pipeline/recipe.py` escribe siempre `AS24_RECIPE` por defecto.
- No hay recetas per-dealer own-site individuales (cada sitio bespoke necesitaría su propio endpoint/parser — eso no existe aún para la long-tail).

### 1c. Cómo se escriben

**`pipeline/recipe.py`** — función `write_recipe(cdp_code, recipe=None)`:
- Escribe `countries/ES/recipes/<cdp_code>.yaml`.
- Si no se pasa `recipe`, usa `AS24_RECIPE` (la plantilla genérica AS24).
- Se invoca en **`pipeline/harvest_dealer.py`** en la FASE 3 del E2E (post-ingest).
- Las recetas de conectores (sentinel-00) se escriben manualmente o por scripts dedicados de cada conector.

---

## 2. Cobertura de Recetas [VERIFICADO con números DB]

### 2a. Universo de referencia

| Métrica | Número |
|---|---|
| Total entidades en DB | 390.621 |
| Particulares (kind=particular) | 329.070 |
| **Dealers (todos los kinds excepto particular)** | **61.551** |
| **Dealers SERVIDOS** (con ≥1 vehículo `status='available'`) | **37.657** |
| Total vehículos disponibles | 1.689.243 |

### 2b. Los 585 YAML — qué son realmente

| Tipo | Cuenta | Descripción |
|---|---|---|
| **Sentinel-00 (plataformas/conectores)** | **35** | Recetas de los conectores wholesale y OEM: milanuncios, wallapop, coches.net, autocasion, coches.com, motor.es, motorflash, miclasico, faciliteacoches, car&classic, autoscout24, cupra, mercedes, hyundai, kia, audi, bmw, dasweltauto, ford, mini_next, nissan, renew, seat_cupra, spoticar, toyota_lexus, volvo_jlr_suzuki, ayvens, bca, localizavo, subastacar, racc, flexicar, carplus, clicars, ocasionplus (+ modrive) |
| **Per-dealer AS24** | **550** | Recetas individuales generadas automáticamente por `harvest_dealer.py` para cada dealer scrapeado vía AutoScout24. Contenido: plantilla AS24 genérica (todos iguales) |
| **Total** | **585** | |

### 2c. Cobertura entre los 37.657 dealers SERVIDOS

| Bucket | Dealers servidos | Vehículos disponibles | Descripción |
|---|---|---|---|
| **A: recipe_individual AS24** | **537** (1,4%) | **81.118** (4,8%) | Recipe YAML per-dealer + `recipe_version=1` en DB. Solo AS24. |
| **B1: sentinel-00 en DB** (plataforma-propia con YAML) | **310** (0,8%) | — | Entidades-plataforma (kind=plataforma/oem_vo_portal) que SON el conector. El YAML del conector ES su receta. |
| **B2: cubierto por conector wholesale** | **36.718** (97,5%) | **1.102.263** (65,3%) | Dealers descubiertos e inventariados VIA un conector wholesale. La receta del conector los cubre. Sin recipe individual. |
| **D: directorio sin recipe scraping** | **88** (0,2%) | **10.976** (0,6%) | Dealers de fuentes de directorio (osm, acevas, aecs, aedra, geo_sweep). Sus vehículos vienen de OTRO conector que los comparte. No tienen recipe de scraping propia. |
| **Total** | **37.657** | **~1.195.357** (aprox.) | |

> Nota: los totales de vehículos por bucket suman menos que 1.689.243 porque los particulares (~490k) no aparecen aquí y hay overlaps de clustering.

### 2d. Desglose por kind para los 37.657 servidos

| kind | Dealers con inventario |
|---|---|
| compraventa | 37.535 |
| concesionario_oficial | ~190 |
| garaje | ~19 |
| subasta | ~97 |
| importador / rent_a_car_vo | ~16 |

### 2e. Dealers con website propio

De los 37.657 dealers servidos: solo **329** tienen `website` en DB (0,87%).  
De esos 329: la mayoría está cubierta por conectores wholesale. Muy pocos necesitan recipe per-site.

---

## 3. Completitud E2E por Fase [VERIFICADO]

El prompt fundacional exige el E2E por dealer: **descubrir → scrapear → receta → API → borrar**.  
El PLAN.md (F3 WORKFLOWS ÁTOMO) lo confirma explícitamente.

| Fase | Artefacto | Estado |
|---|---|---|
| **1. DESCUBRIR** | `pipeline/discover.py` + `pipeline/sources/*.py` | EXISTE. 10 source adapters (dgt_cat, osm, oem_kia, oem_mg, oem_byd, oem_skoda, oem_dacia, oem_hyundai, oem_mercedes, oem_seat). Upserta entity + entity_source + VAM gate. |
| **2. SCRAPEAR** | `pipeline/harvest_dealer.py` + `pipeline/platform/*.py` | EXISTE. AS24 per-dealer via `sources/autoscout24.py`. ~45 módulos wholesale en `platform/`. |
| **3. RECETA** | `pipeline/recipe.py` → `countries/ES/recipes/<cdp>.yaml` | EXISTE pero **parcial**: solo escribe AS24_RECIPE genérica. No hay auto-generación de recetas per-conector ni per-own-site. Los YAML sentinel-00 se han escrito manualmente. |
| **4. API** | `services/api/` (FastAPI) + endpoints `/entities/{cdp_code}`, `/vehicles/`, `/geo/` | EXISTE. Sirve entidades, inventario, delta, cluster canonical. |
| **5. BORRAR (GONE)** | `pipeline/ingest.py` → `should_emit_gone()` + `pipeline/delta_guard.py` | EXISTE. Guard al 95% del declared count. Status=gone + vehicle_event. |

**Conclusión E2E**: las 5 fases tienen artefacto de código. El ciclo completo funciona para dealers AS24. Para conectores wholesale el flujo es levemente distinto (no hay harvest_dealer individual, sino un drainer de plataforma completo que GONE-barre por fuente). La fase RECETA es la más incompleta (ver §4).

---

## 4. El Gap Concreto [VERIFICADO]

### 4a. Gap real de recetas

| Categoría | Gap |
|---|---|
| **Conectores wholesale activos SIN YAML** | **Autorola** (cdp `CDP-ES-00-RJ109M0T`) y **BCA España** (`CDP-ES-00-WYJKTP6S`). Ambos en `official_registry`. Tienen módulos Python (`group_subastas_wholesale.py`?) pero sin YAML. |
| **~13 conectores con módulo Python SIN YAML sentinel-00** | `coches_net_segments.py`, `autocasion_facet.py`, `wallapop_facet.py`, `group_importador_wholesale.py`, `group_rentacar_vo_wholesale.py`, `carandclassic_wholesale.py`, `oem_ford_wholesale.py`, `oem_bmw_mini_wholesale.py`, `oem_nissan_mazda_honda_wholesale.py`, etc. Sus entidades plataforma pueden existir en DB pero el YAML de receta no se ha escrito. |
| **550 per-dealer YAML = AS24 genérico** | No son recetas específicas del dealer: son la misma plantilla AS24. Útil para re-scrapear el perfil AS24 del dealer, pero no documenta si ese dealer tiene own-site. |
| **Long-tail own-sites sin recipe individual** | Los ~67 dealers de `family_*` tienen código Python genérico (family_dealerk_wholesale, family_generic_custom) pero ninguno tiene YAML per-dealer propio. Para re-scrapear necesitarías la familia, no una receta individual. |
| **88 dealers directorio** | Sin recipe de scraping de ningún tipo. Sus vehículos provienen de fuentes wholesale cruzadas. No se puede re-scrapear directamente. |

### 4b. Techo estructural vs gap tratable

| Tipo de gap | Naturaleza | Tratable €0 | Requiere trabajo |
|---|---|---|---|
| Conectores wholesale (B2, 36.718 dealers) | Ya cubiertos por receta del conector. La receta del conector ES la forma de re-scraping. **No es un gap real.** | — | — |
| YAML faltante para 2 conectores (Autorola, BCA) | Gap tratable: el código Python existe, falta escribir el YAML. | Generación automática desde `group_subastas_wholesale.py` | Trivial |
| YAML faltante para ~13 conectores activos | Gap de documentación: los módulos existen y funcionan. Los YAML se pueden generar inspeccionando los módulos. | Generación automática o manual | Bajo — 1-2h por conector |
| Own-site long-tail (family_*, generic_custom) | Los 67 dealers tienen familia Python genérica. Para re-scraping basta con el módulo + cdp_code. El YAML per-dealer sería documentación redundante. | — | Bajo si se acepta receta a nivel de familia |
| 88 directorio | No hay surface de scraping propia. Los vehículos vienen de marketplace cruzado (milanuncios, coches.net, as24). Su "receta" es la del marketplace, no la del dealer. **Techo estructural.** | — | No aplica |
| Dealers fuera del radar (sin inventario) | 61.551 - 37.657 = 23.894 dealers conocidos SIN inventario. Pueden tener website pero Cardeep aún no los ha scrapeado. | Requiere recipe-hunting per-site | Alto — Tier-1 hunting + AS24 discovery |

### 4c. Gap numérico de recipe real

- **Dealers SERVIDOS sin recipe ni propia ni de conector**: **88** (bucket D).  
  Sus vehículos provienen de fuentes cruzadas, pero no hay recipe de re-scraping directa. Son 10.976 vehículos (0,65% del total).
- **Dealers NO servidos** (23.894): el problema no es falta de receta — es que aún no han sido scrapeados. Descubrir y crear receta es el trabajo pendiente de expansión (Fase B del SUPERPLAN).

---

## 5. €0-mejorable vs Requiere-trabajo

| Acción | Esfuerzo | Impacto |
|---|---|---|
| **Generar YAML para Autorola y BCA** (2 conectores, sentinel-00) | €0, 30 min | Cierra gap de documentación de 2 conectores de subastas activos |
| **Generar YAML para ~13 conectores activos sin YAML** (oem_ford, bmw, nissan, carandclassic, group_importador, group_rentacar_vo, etc.) | €0, 1-2h cada uno, script parsea el módulo Python | Documenta todos los conectores activos. No cambia el scraping (ya funciona). |
| **Marcar `recipe_version` en DB** para entidades cuyo conector tiene YAML | €0, 1 migración SQL | Hace el campo coherente (ahora los 36.718 de B2 tienen NULL). |
| **Recipe-hunting Tier-1** (own-sites de los 23.894 dealers sin inventario) | Alto: fingerprinting, anti-bot, cadencia por site | Expande cobertura. Necesario para completar el mandato "100%". |
| **Generar recetas per-dealer para family_* (67 dealers)** | Bajo: el módulo Python ya funciona; el YAML sería documentación adicional | Mejora la trazabilidad pero no debloquea nada. |

---

## 6. Riesgos y Dudas Honestas

1. **`recipe_version` en DB es un indicador débil.** Solo los 537 AS24 lo tienen (`=1`). Los 36.718 dealers de conectores wholesale tienen `recipe_version=NULL` aunque SÍ están cubiertos por la receta de su conector. El campo no refleja la cobertura real. Recomiendo poblar o deprecar.

2. **Los 550 YAML per-dealer son copias de AS24_RECIPE.** No capturan información específica del dealer (nombre, slug, provincia). Son útiles para saber "este dealer existe en AS24 y se puede re-scrapear", pero no son recetas auténticamente personalizadas. Confundirlos con "receta completa" sería un error.

3. **Los conectores wholesale no tienen YAML sentinel-00 para todos.** Solo 35 de los ~47+ módulos Python tienen su YAML. Los conectores sin YAML funcionan (el código está ahí) pero no tienen documentación persistida de cómo re-scrapearlos.

4. **Los 88 dealers de directorio tienen vehículos por cruce de fuentes, no por scraping directo.** Si mañana se desactivan las fuentes cruzadas (milanuncios, coches.net), esos 88 perderían inventario sin aviso. No hay alerta configurada para esto.

5. **La fase BORRAR (GONE) solo funciona cuando harvested >= declared * 0.95.** En scraping fallido parcial, el GONE no se emite (por diseño, delta_guard.py). Correcto pero implica que un dealer caído silenciosamente puede retener inventario fantasma hasta la próxima corrida completa.

6. **El prompt exige "E2E por dealer" atómico.** `harvest_dealer.py` implementa esto solo para AS24. Para conectores wholesale el E2E no es per-dealer sino per-conector (un sweep arrastra todos los dealers de la plataforma). Esto es correcto arquitecturalmente pero crea asimetría: no existe un comando `python -m pipeline.harvest_dealer <cdp_code>` para un dealer de milanuncios o mercedes.

---

## 7. Resumen Ejecutivo

**Modelo**: La receta es un YAML con endpoint, motor, paginación, field-map y caveats que permite re-scrapear sin código raw. Existen dos niveles: por-conector (35 YAMLs, plataformas) y per-dealer (550 YAMLs, AS24 genérico).

**Cobertura real**:
- 37.657 dealers servidos (con inventario activo).
- **97,5% cubiertos por receta de conector** (B2): no necesitan recipe individual.
- **1,4% con recipe individual AS24** (A): 537 dealers, YAML+DB coherentes.
- **0,2% sin recipe de ningún tipo** (D): 88 dealers de directorio, 10.976 vehículos.

**E2E**: Las 5 fases (DESCUBRIR / SCRAPEAR / RECETA / API / BORRAR) tienen artefacto de código. Completo para AS24. Para wholesale el loop es per-conector, no per-dealer.

**Gap real**:
- Solo 88 dealers servidos sin recipe ni propia ni de conector (techo estructural: vienen de registros, no tienen superficie scraping directa).
- ~13 conectores activos sin YAML de documentación (el scraping funciona, falta el YAML).
- 23.894 dealers conocidos sin inventario = trabajo de expansión pendiente (Tier-1 recipe-hunting).

**€0-mejorable inmediato**: generar YAML para los ~15 conectores activos sin YAML (Autorola, BCA, ford, bmw, nissan, etc.) y poblar `recipe_version` en DB para B2.
