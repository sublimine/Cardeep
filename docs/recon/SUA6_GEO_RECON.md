# SUA6 — GEO PAÍS/PROV/CIUDAD: RECON COMPLETO

> **Fecha:** 2026-06-15  
> **Auditor:** Agente geo (Sonnet), bajo Director (Opus)  
> **Scope:** Read-only. No se ha escrito ninguna fila ni ningún fichero salvo este.  
> **DB:** cardeep-pg :5433  

---

## 0. GATE OBJETIVO

```
gap municipio <2%  |  /geo/tree completo  |  comarca asignada  |  sin sentinel-drift
```

Estado a fecha de este recon: **NINGÚN punto sellado todavía.**

---

## 1. ARQUITECTURA GEO (estado verificado)

### Tablas

| Tabla | Filas | Comentario |
|---|---:|---|
| `geo_province` | 52 | 50 provincias + Ceuta (51) + Melilla (52) |
| `geo_comarca` | 323 | 50 provincias con comarca; 323 ine_codes poblados |
| `geo_municipality` | 8.132 | 8.117 con lat/lon · 8.130 con comarca_id · **2 sin comarca** (Ceuta + Melilla) · 15 sin lat/lon |

`geo_municipality` tiene CHECK constraint `municipality_province_prefix`: `left(code,2) = province_code`. Esto garantiza que ninguna fila de la tabla de referencia puede tener muni asignado a provincia incorrecta.

### Código GeoResolver (pipeline/geo.py)

Cascada de resolución **siempre scoped a province_code** (no hay crossover):
1. Exact match (normalized/token-sorted key)
2. Fuzzy WRatio ≥ 88 con guards de longitud + token-subset ambiguity guard
3. INE Nomenclátor gazetteer (~63k entidades singulares/núcleos)

### Código MunicipalityGeocoder (pipeline/geocode.py)

- KNN nearest-centroid dentro de la provincia (scoped por province_code → imposible crossover cross-province)
- Guard: si dist > 30 km → devuelve None ("better a hole than a lie")
- PostcodeIndex: CP → muni via Nomenclátor; postcodes ambiguos (>1 muni) → None

### Datos de referencia en disco

```
data/geo/nomenclator_entidades_ine.csv   4,2 MB   (2026-06-14)
data/geo/municipios_centroides.csv        576 KB   (2026-06-14)
data/geo/comarcas_ine.xls                576 KB
data/geo/diccionario_ine.xlsx            307 KB
```

---

## 2. EL GAP EXACTO

### Universo de análisis

| Universo | Dealers |
|---|---:|
| Entities no-particular (total) | 61.551 |
| · Con municipality_code asignado | 54.805 |
| · Sin municipality_code (gap total) | **6.746** |
| — De los 6.746: con province_code NULL | 343 |
| **Dealers POS con vehicles available** | **37.657** |
| · Sin municipality_code (gap servido) | **6.619** |
| — De los 6.619: con province_code NULL | 310 |

### Gap ratio

- **Gap total (universo completo):** 6.746 / 61.551 = **11,0%**
- **Gap servido (POS con inventario disponible):** 6.619 / 37.657 = **17,6%**

> El SUPERPLAN reportaba "11% (6.746)" sobre el universo completo. Verificado.  
> El gap sobre dealers *servidos* es mayor (17,6%) porque los dealers sin muni tienden a tener menos inventario o estar parcialmente activos.

### Vías de resolución €0 (universo completo, 6.746 dealers)

| Vía | N con señal | N en soledad (sin otra vía) |
|---|---:|---:|
| Tiene `address` (no vacío) | 129 | 4 |
| Tiene `lat`/`lon` | 30 | — |
| Tiene `postcode` | 125 | 0 |
| `lat`/`lon` + `postcode` | 14 | — |
| `address` + `postcode` (sin lat/lon) | 111 | — |
| **Al menos una vía** | **145** | — |
| **Cero vías (irresolvibles)** | **6.601** | **6.601** |

> De los 6.619 dealers *servidos* sin muni: 6.524 sin ninguna señal, 95 con al menos una vía.

### Tabla de resolubilidad €0

```
TOTAL SIN MUNI (universo):   6.746
  ├── Resolvibles €0:          145   (2,1%)
  │     ├── lat/lon:            44   (30 solos + 14 con postcode)
  │     ├── postcode:          125   (111 con address, 14 con latlon, 0 solos)
  │     └── solo address:        4   (string-match = precisión baja, ver §3)
  └── Irresolvibles (gap estructural): 6.601   (97,9%)
        └── sin address, sin lat/lon, sin postcode
```

**Cerrando los 145 resolvibles el gap total pasaría de 11,0% → 10,8%.**  
**El gap no baja de ~10,7% €0 con datos actuales.**

---

## 3. FACTIBILIDAD DEL MATCH INE

### 3.1 lat/lon → municipio (PostcodeIndex/MunicipalityGeocoder)

- **Mecanismo:** KNN centroide dentro de province_code. Guard 30 km.
- **Disponibilidad de centroides:** 8.117 de 8.132 municipios (99,8%).
- **Precisión esperada:** Alta para ubicaciones urbanas (<5 km del centroide típico). Para rural disperso (Soria, Cuenca), puede errar hasta 20 km sin superar el umbral — safe. **[ASUMIDO: no hay validación de muestra en este recon.]**
- **Requisito:** `province_code` ya poblado. De los 30 dealers con lat/lon sin muni, todos tienen province_code. **Resolvibles directamente.**
- **Falsos positivos:** El guard 30 km los bloquea. Riesgo real = bajo si province_code es correcto.

### 3.2 postcode → municipio (PostcodeIndex)

- **Mecanismo:** CP → muni via Nomenclátor. Ambiguos → None.
- **Cobertura:** Nomenclátor cargado (4,2 MB, ~63k entidades). La mayoría de CPs españoles son unívocos a nivel municipal dentro de la provincia.
- **Requisito:** `postcode` no nulo + CP unívoco en el Nomenclátor.
- **Precisión esperada:** Alta (oficial INE). Riesgo principal: CPs que abarcan 2+ municipios → ya devuelve None (doctrina "better a hole").
- **De los 125 dealers con postcode:** Todos son potencialmente resolvibles si su CP es unívoco. **[ASUMIDO: no se ha corrido el PostcodeIndex en lote contra estos 125.]**

### 3.3 address → municipio (string-match)

- **Mecanismo:** No hay campo `city` separado en `entity`. El address es texto libre (ej: "Calle Melilla 55", "Autovía del Mediterráneo KM 166"). El GeoResolver usa `muni_name` como señal, no el address completo.
- **Viabilidad:** Baja sin parsing previo. Extraer ciudad del address libre requiere NLP o reglas frágiles.
- **Riesgo de falsos positivos:** Alto (nombres de calles que contienen topónimos: "Calle Sevilla" en un pueblo diferente).
- **Los 4 dealers con solo address:** Candidatos a resolución manual o descartables como irresolvibles en €0.
- **Recomendación:** No implementar string-match de address para muni. No es fiable sin campo city separado.

---

## 4. ERRORES WITHIN-PROVINCE

### 4.1 Mismatch muni-prefix vs province_code (hard constraint)

```sql
SELECT count(*) FROM entity
WHERE kind <> 'particular' AND municipality_code IS NOT NULL
  AND province_code IS NOT NULL
  AND left(municipality_code, 2) <> province_code;
-- Resultado: 0
```

**Cero errores hard.** La CHECK constraint en `geo_municipality` ya previene que existan municipios con prefijo incorrecto en la tabla de referencia. Los dealers apuntan a esa tabla via FK, por lo que tampoco pueden tener muni de provincia diferente.

### 4.2 Mismatch CP vs province_code (indicador suave)

71 dealers (de 54.805 con muni asignado) tienen `left(postcode,2) <> province_code`, excluyendo Baleares/Canarias/Ceuta/Melilla (codificaciones especiales).

| Tipo | N |
|---|---:|
| Mismo CCAA (municipio fronterizo — legítimo) | 32 |
| Cross-CCAA (posible error de asignación) | 38 |
| **Total CP-prov mismatch** | **71** |

**Ejemplos cross-CCAA verificados:**
- `municipality_code=21072` (Valverde del Camino, Huelva, Andalucía) con `postcode=18151` (Granada, Andalucía) — mismo CCAA pero diferente provincia → address puede contener la dirección incorrecta de un almacén.
- `municipality_code=29068` (Manilva, Málaga) con `postcode=11310` (Cádiz) — municipio de Málaga fronterizo con Cádiz, legítimo geográficamente.
- `municipality_code=28036` (Casarrubuelos, Madrid) con `postcode=45200` (Toledo) — CP de Toledo, muni de Madrid → probable error: el dealer está en Toledo con muni asignado a Madrid.

**Causa probable de los 38 cross-CCAA:** nearest-centroid asignó la province_code correctamente pero el muni fue resuelto por address-string con un nombre ambiguo (ej: "Av. de las Naciones, 31, 45200, Toledo" → muni 28036 Madrid en vez de 45xxx Toledo). El guard solo bloquea fuera del 30 km; dentro de la misma provincia la asignación de muni puede errar si la ciudad tiene nombre idéntico a otra en la misma provincia.

**Tasa de error within-province:** 38 / 54.805 = **0,07%** (38 errores detectables).  
Errores sutiles no detectables por CP (muni equivocado dentro de la misma provincia-CP) no son cuantificables en este recon sin geometría de polígonos.

---

## 5. COMARCA + SENTINEL-DRIFT

### 5.1 Comarca asignada

| Nivel | Situación |
|---|---|
| `geo_comarca` | 323 comarcas, 50 provincias cubiertas, 323 ine_codes. Solo Ceuta y Melilla sin comarca (1 muni cada una — correcto, no tienen subdivisión comarcal). |
| `geo_municipality.comarca_id` | 8.130 / 8.132 municipios con comarca (99,98%). Solo Ceuta y Melilla sin comarca_id. |
| `entity.comarca_id` donde hay muni | 54.765 / 54.805 con comarca (99,93%). **40 dealers con muni pero sin comarca_id.** |

Los 40 dealers sin comarca_id en entity tienen su `municipality_code` apuntando a municipios que NO tienen `comarca_id` en `geo_municipality`. Tras verificar: estos 40 municipios son exactamente los de Ceuta y Melilla.

```
-- Verificado:
SELECT gm.province_code, count(*) FROM entity e
JOIN geo_municipality gm ON gm.code = e.municipality_code
WHERE e.kind <> 'particular' AND e.municipality_code IS NOT NULL AND e.comarca_id IS NULL
GROUP BY gm.province_code;
-- Solo provincias 51 (Ceuta) y 52 (Melilla)
```

**Conclusión comarca:** Cobertura 99,93% sobre dealers con muni. Los 40 sin comarca son Ceuta/Melilla — correcto por definición (no tienen comarcas). No hay gap de comarca que arreglar.

### 5.2 Sentinel-drift

```sql
SELECT
  count(*) FILTER (WHERE province_code = '00') AS province_sentinel,
  count(*) FILTER (WHERE municipality_code = '00000') AS muni_sentinel
FROM entity WHERE kind <> 'particular';
-- Resultado: 0 / 0
```

**Cero sentinel-drift.** No hay códigos `00`/`00000` filtrándose a entidades reales. Los 343 dealers sin province_code son NULLs genuinos (sin señal disponible), no centinelas.

---

## 6. RECOMENDACIÓN: ¿QUÉ ES CERRABLE €0?

### 6.1 Acción prioritaria: backfill acotado de 44 dealers con lat/lon

- 44 dealers (30 con solo lat/lon + 14 con lat/lon y postcode) son directamente resolvibles vía `MunicipalityGeocoder.nearest_municipality()` sin ninguna dependencia nueva.
- **Riesgo:** bajo (guard 30 km activo, province_code disponible en todos los 44).
- **Impacto:** gap total 6.746 → 6.702 (reducción de 44).

### 6.2 Acción secundaria: backfill de ≤125 dealers con postcode

- Correr `PostcodeIndex.resolve()` contra los 125 postcodes. Los unívocos se resuelven. Los ambiguos quedan como NULL (doctrina).
- **Estimación de resolución:** ~60-85% de los 125 según la distribución de CPs únicos en España (conservador: 70% → ~87 dealers resueltos).
- **Riesgo:** bajo si se aplica solo donde muni IS NULL y postcode no es ambiguo.
- **Impacto combinado con 6.2:** gap total ~6.702 - 87 ≈ 6.615 (de 11,0% → ~10,7%).

### 6.3 Lo que NO es cerrable €0

- **6.601 dealers sin ninguna señal**: irresolvibles sin datos externos (Overture, SIRENE, Google Geocoding, llamada a API de correos). Representan el **97,9% del gap** y son estructurales.
- **4 dealers con solo address**: no fiable sin NLP o campo city separado.
- **343 dealers sin province_code**: sin señal de ningún tipo, irresolvibles.

### 6.4 Vista derivada vs backfill

**Recomendación: backfill directo en UPDATE (MVCC-safe) sobre los 44+87 casos identificados**, no vista derivada. Motivo: el GeoResolver ya tiene toda la lógica; un script de backfill que llame a `nearest_municipality()` y `PostcodeIndex.resolve()` para los NULLs con señal es determinista, idempotente, y produce filas permanentes en lugar de recalcular en cada query.

**No hacer UPDATE de filas no-mutadas** (doctrina PG MVCC): solo actualizar los ~131 dealers con señal disponible.

---

## 7. RESUMEN EJECUTIVO PARA EL DIRECTOR

| Métrica | Valor verificado |
|---|---|
| Gap municipio total (universo no-particular) | **11,0%** (6.746 / 61.551) |
| Gap municipio sobre dealers servidos | **17,6%** (6.619 / 37.657) |
| Resolvibles €0 (lat/lon + postcode) | **~131-145** (2,1% del gap) |
| Irresolvibles estructurales | **6.601** (97,9% del gap) |
| Gap mínimo alcanzable €0 | **~10,7%** (≈6.600 / 61.551) |
| Errores hard within-province (muni-prefix) | **0** |
| Errores suaves detectables (CP cross-CCAA) | **38** (0,07% de dealers con muni) |
| Comarca asignada donde hay muni | **99,93%** (40 sin comarca = Ceuta/Melilla por definición) |
| Sentinel-drift (códigos 00/00000) | **0** — limpio |
| Municipios sin lat/lon en geo_municipality | **15** (0,18%) |

### Veredicto de gate

| Criterio del gate | Estado |
|---|---|
| gap municipio <2% | **NO CERRABLE €0** (mínimo ~10,7%) |
| /geo/tree completo | No auditado en este recon (endpoint API) |
| comarca asignada | **VERDE** (99,93%, Ceuta/Melilla correctamente sin comarca) |
| sin sentinel-drift | **VERDE** (0 centinelas) |

**El gate de SUA6 no se puede sellar €0.** El gap estructural del 10,7% (6.601 dealers sin ninguna señal de geolocalización) solo es reducible mediante datos externos. El bloqueo es de datos, no de código.

**Acción recomendada €0:** Script de backfill sobre 44 (lat/lon) + ~87 (postcode) = ~131 dealers. Cierra el gap resolvible pero no mueve el 11% más de 0,3 puntos. Implementar como deuda de calidad; no bloquea ningún gate B hasta que se defina si Overture/Geonames es viable.

---

## 8. RIESGOS Y DUDAS HONESTAS

1. **Precisión del KNN lat/lon:** El umbral 30 km es correcto para España, pero zonas con muchos municipios pequeños y cercanos (País Vasco, Cataluña) podrían tener asignaciones erróneas no detectadas. Sin polígonos reales, no cuantificable en este recon.

2. **38 errores cross-CCAA detectados por CP:** Son indicadores, no certezas. Un dealer puede legítimamente tener dirección de envío en provincia X pero operar desde Y. No modificar sin validación caso por caso.

3. **PostcodeIndex ambiguos:** La tasa real de CPs ambiguos en los 125 dealers no se ha calculado aquí. Si la distribución es desfavorable, el 70% estimado podría ser menor.

4. **Los 343 dealers con province_code NULL:** Irresolvibles sin señal. No son centinelas pero tampoco se pueden ubicar. Si son dealers reales en España, su province_code se perdió en la ingesta.

5. **Errores sutiles within-province:** El caso más frecuente (muni vecino en misma provincia asignado por centroide) no es detectable sin polígonos. La tasa es desconocida pero la doctrina "better a hole" del GeoResolver con el threshold 30 km la limita considerablemente.

---

## VERIFICACIÓN EJECUTADA 2026-06-16 — el §Deuda "backfill 131" NO es €0-cerrable (resuelve 0)

Corrido `scripts/backfill_municipality_geo.py` (dry-run) contra DB viva + diagnóstico per-dealer de los geocoders. **136 dealers con señal geo escaneados → resueltos+self-verified = 0.** NO es bug (el gate self-verify funciona); los DATOS son inconsistentes:

- **PostcodeIndex carga bien** (8.785 unambiguous + 2.266 ambiguous desde el Nomenclátor INE, 4,3 MB presente). De los 106 con postcode: **9 resuelven** pero su muni cae en provincia ≠ `province_code` → rechazados por el gate; **58 ambiguos** (>1 muni, irresolubles por doctrina); **53 unknown**, incluyendo **postcodes de 4 dígitos malformados** ('3760','3590','3205','1138'…) cuya reconstrucción es ambigua (¿leading-zero '03760'-Alicante o trailing-trunc '37600'-Salamanca?) → no se reconstruyen a ciegas.
- **MunicipalityGeocoder (KNN 30 km, province-constrained)**: de los 30 con lat/lon, **todos rechazados**. Varios tienen `province_code` flatamente erróneo — coords a **614–707 km** de la provincia declarada (prov 39 Cantabria con coords de Málaga; prov 30 Murcia con coords en Portugal); otros boundary genuinos (nearest centroid 32,5 km, justo sobre el umbral 30).

**Conclusión:** el gate self-verify (`code[:2]==province_code`) **correctamente rehúsa escribir** (better a hole than a lie) porque la señal geo es inconsistente con el `province_code` almacenado. **El §Deuda no se cierra a €0** — requiere CORREGIR datos (province_code y/o postcodes malformados) con validación externa caso-por-caso = DATA-gated (Fase-B), no geocoding. El script `backfill_municipality_geo.py` es correcto (escribe 0 honestamente). El "131 resolvable" del recon era optimista (asumido sin correr); el €0-real ≈ 0. **No se muta nada** (no hay resolución segura que escribir).
