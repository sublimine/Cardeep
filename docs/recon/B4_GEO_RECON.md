# B4 GEO RECON — Bloque B4: "Geo al átomo"
**Fecha:** 2026-06-14  
**Auditor:** Agente de reconocimiento (solo-lectura)  
**DB:** cardeep @ docker:cardeep-pg:5432  
**Repo:** C:\Users\elias\projects\cardeep  

---

## 1. ESQUEMA GEO REAL [VERIFICADO DB]

### Jerarquía implementada

La jerarquía es **país → provincia → comarca → municipio** con FKs reales. No es plana.

```
geo_province  (PK: code CHAR(2))        → 52 filas (provincias INE + Ceuta + Melilla)
geo_comarca   (PK: id BIGINT, FK→province) → 323 filas (comarcas con ine_code CHAR(2))
geo_municipality (PK: code CHAR(5), FK→province, FK→comarca) → 8.132 filas (municipios INE)
```

**Columnas geo de `entity`:**

| Columna | Tipo | FK destino |
|---|---|---|
| `province_code` | CHAR(2) | `geo_province(code)` |
| `municipality_code` | CHAR(5) | `geo_municipality(code)` |
| `comarca_id` | BIGINT | `geo_comarca(id)` |
| `lat` / `lon` | DOUBLE PRECISION | — |
| `address` | TEXT | — |
| `postcode` | TEXT | — |
| `geocode_source` | TEXT | — (vacío, ver §3) |
| `geocode_precision` | TEXT | CHECK: rooftop/street/postcode/municipality/province |

**Trigger:** `trg_entity_set_comarca` — al insertar/actualizar `municipality_code`, el trigger `entity_set_comarca()` rellena automáticamente `comarca_id` desde `geo_municipality.comarca_id`. La comarca no se asigna directamente; se hereda del municipio.

**Gazetteer interno:** `geo_municipality` tiene **0 centroides lat/lon** (columnas presentes pero vacías). Ceuta (51001) y Melilla (52001) son los únicos municipios sin `comarca_id`.

### Queries ejecutadas
```sql
\d entity
\d geo_province
\d geo_comarca
\d geo_municipality
SELECT 'geo_province', COUNT(*) FROM geo_province UNION ALL ...
SELECT COUNT(*) FROM geo_municipality WHERE comarca_id IS NULL;  -- → 2 (Ceuta, Melilla)
SELECT COUNT(*) FROM geo_municipality WHERE lat IS NULL;          -- → 8132 (todos)
```

---

## 2. GAP REAL POR NIVEL [VERIFICADO DB]

### Global (N = 369.535 entidades totales)

| Nivel | Con dato | Sin dato | % poblado |
|---|---|---|---|
| province_code | 369.191 | 344 | **99,91%** |
| municipality_code | 289.497 | 80.038 | **78,34%** |
| comarca_id | 288.571 | 80.964 | **78,09%** |
| lat/lon | 12.499 | 357.036 | **3,38%** |
| postcode | 8.550 | 360.985 | **2,31%** |
| address | 9.287 | 360.248 | **2,51%** |

**Gap real de municipio: 21,66% (80.038 entidades).** La cifra "32,5%" citada en el brief NO se reproduce — [ASUMIDO que era una estimación anterior o de otro corte].

### Por kind

| kind | total | pct_prov | pct_mun | pct_comarca | pct_lat |
|---|---|---|---|---|---|
| particular | 326.637 | 100,0% | 79,8% | 79,6% | 0,0% |
| compraventa | 32.039 | 99,3% | 74,9% | 74,9% | 8,6% |
| garaje | 7.220 | 100,0% | 24,0% | 24,0% | 99,7% |
| concesionario_oficial | 1.844 | 100,0% | 85,1% | 84,8% | 68,0% |
| desguace | 1.645 | 100,0% | 86,6% | 86,4% | 78,5% |
| subasta | 97 | 0,0% | 0,0% | 0,0% | 0,0% |
| plataforma | 18 | 0,0% | 0,0% | 0,0% | 0,0% |
| oem_vo_portal | 14 | 0,0% | 0,0% | 0,0% | 0,0% |

**Garaje** es el outlier: 76% sin municipio pero 99,7% con lat/lon (OSM POIs). **Particular** tiene el volumen más alto de gap absoluto (260k sin municipio: 65.886 solo-provincia + resto con municipio).

### Por source_group

| source_group | total | pct_mun | pct_lat |
|---|---|---|---|
| NULL (348.520) | 348.520 | 79,9% | 0,0% |
| directory | 9.953 | 23,9% | 100,0% |
| oem_vo_portal | 5.769 | 84,8% | 0,0% |
| marketplace_motor | 1.764 | 51,6% | 0,0% |
| oem_dealer_network | 1.526 | 86,8% | 82,2% |
| desguace_network | 1.292 | 92,8% | 100,0% |
| official_registry | 102 | 0,0% | 0,0% |

El bloque NULL (348k) = particulares + compraventas de plataformas C2C. **directory** es el peor caso para municipio (23,9%) a pesar de tener lat/lon 100%.

### Accionabilidad del gap (excluyendo plataforma/subasta/oem_vo_portal/cadena)

| Bucket | N | % total |
|---|---|---|
| OK: tiene municipio | 289.497 | 78,34% |
| BLOQUEADO: solo provincia (Wallapop/Milanuncios particular) | 71.337 | 19,30% |
| ACCIONABLE: reverse-geocode lat/lon | 7.837 | 2,12% |
| ACCIONABLE: CP → municipio | 483 | 0,13% |
| BLOQUEADO: sin datos geo | 211 | 0,06% |
| ACCIONABLE: address fuzzy match | 37 | 0,01% |

**Gap accionable técnicamente: 8.357 entidades (2,26%).**  
**Gap estructuralmente bloqueado por diseño de fuente: 71.548 entidades (19,36%).**

---

## 3. ORIGEN DEL GEO ACTUAL [VERIFICADO código]

### Pipeline de resolución (en orden de prioridad)

**Archivo:** `pipeline/geo.py` — clase `GeoResolver`  
**Archivo:** `pipeline/geocode.py` — clase `ProvinceGeocoder`  
**Archivo:** `pipeline/discover.py` — función `_upsert()` (L49-113)  
**Archivo:** `pipeline/ingest.py` — función `ingest_dealer()` (L40-60)

**Cadena para `discover.py` (particulares / long-tail):**

1. `geo.province_code(e.province_name)` — match texto → INE code en `geo_province` (accent/case insensitive, token-sorted, aliases curados: Menorca→07, Alava→01, etc.)
2. `geo.municipality_code(prov, e.municipality_name)` — match texto en `geo_municipality` por province_code
3. Si sin provincia pero hay city: `geo.resolve_city_global(city)` — solo cuando el municipio es ÚNICO en España (sin ambigüedad)
4. Si no hay provincia y hay lat/lon: `ProvinceGeocoder.nearest_province(lat, lon)` — nearest-neighbor euclidean sobre las entidades con provincia conocida (no usa Nominatim, no usa polígonos, no usa shapely)
5. Si sin provincia: **entidad descartada** (no se puede mintear cdp_code)

**Cadena para `ingest.py` (dealers de directorio):**

1. `geo.municipality_code(d.province_code, d.city)` — el scraper ya entrega `province_code` (INE) y `city` (texto)
2. No hay fallback a lat/lon en ingest_dealer

**No se usa Nominatim, geopy ni ningún geocoder externo.** El campo `geocode_source` está vacío en la DB (`SELECT geocode_source, COUNT(*) FROM entity WHERE geocode_source IS NOT NULL` → 0 filas).

**Problema clave para Wallapop/Milanuncios particulares:** El API entrega `province_code` (INE directo) y `city.name` (texto). El `GeoResolver` intenta el match texto→municipio. Cuando falla (nombre de ciudad ambiguo, abreviado, o no normalizable), la entidad queda con solo `province_code`. **No hay fallback de CP para particulares** porque Wallapop no siempre devuelve el CP, y Milanuncios entrega CP solo en anuncios profesionales.

---

## 4. HERRAMIENTAS DISPONIBLES [VERIFICADO]

### Instaladas en el entorno Python

```
numpy  2.4.4   ✓ (usado en ProvinceGeocoder)
```

```
shapely    ✗ NO instalado
geopy      ✗ NO instalado
rapidfuzz  ✗ NO instalado
unidecode  ✗ NO instalado
```

(`pip show shapely geopy rapidfuzz unidecode` → WARNING: Package(s) not found)

### Datasets locales en el repo

```
data/geo/comarcas_ine.xls       ✓ presente
data/geo/diccionario_ine.xlsx   ✓ presente
```

El gazetteer `geo_municipality` (8.132 municipios) ya está cargado en PG con FK → comarca. Los ficheros `.xls`/`.xlsx` son la fuente original de esa carga.

**No hay shapefiles, GeoJSON de polígonos, ni base de datos de CP→municipio** en el repo.

### Servicios externos en uso

- **Ninguno para geo.** No hay llamadas a Nominatim, Google Maps, HERE, ni similar.
- `ProvinceGeocoder` es un KNN propio sobre entidades ya geocodificadas (bootstrapping interno).

---

## 5. FORMA DEL DATO SUCIO [VERIFICADO DB]

### Clasificación por tipo de dato disponible (entidades sin municipio, excluyendo platform/subasta)

| Material | N | Estrategia viable |
|---|---|---|
| Solo provincia (text INE code) | 71.337 | BLOQUEADO — no hay ciudad |
| Lat/lon sin municipio | 7.837 | Reverse geocode local con gazetteer |
| CP 5 dígitos válido | 483 | CP[:2]=provincia → buscar municipio por CP en INE |
| Address texto libre + lat/lon | 37 | Reverse geocode o fuzzy match address |
| Sin ningún dato geo | 211 | Irrecuperable |

### Ejemplos reales de particulares bloqueados (Wallapop / Milanuncios)

```
trade_name: Gonzalo    | province: 28 | city: NULL | address: NULL | postcode: NULL | lat: NULL
trade_name: Mario      | province: 28 | city: NULL | address: NULL | postcode: NULL | lat: NULL
trade_name: jaresa30   | province: 28 | city: NULL | address: NULL | postcode: NULL | lat: NULL
```

El API de estas plataformas entrega province_code (INE) + city_name. El city_name entra al `GeoResolver` pero falla cuando: (a) la ciudad tiene acento raro no normalizable, (b) es un barrio o nombre coloquial no en INE, (c) es ambiguo entre provincias. En esos casos la entidad queda con solo provincia. **No hay CP, lat/lon, ni address de texto libre** para particulares de Wallapop/Milanuncios — es un límite de la API upstream.

### Ejemplos reales de garajes bloqueados (OSM — accionables)

```
kind: garaje | province: 35 | lat: 28.1326 | lon: -15.4405 | municipality: NULL
kind: garaje | province: 07 | lat: 39.4722 | lon: 3.1450  | municipality: NULL
kind: compraventa | province: 18 | lat: 37.1569 | lon: -3.6091 | address: "Avenida Fernando de los Ríos 30"
```

Estos 7.837 POIs OSM tienen lat/lon precisas pero el `ProvinceGeocoder` solo resuelve provincia — nunca ejecutó un reverse-geocode a nivel municipio.

### Ejemplos de entidades con CP pero sin municipio

```
kind: compraventa | province: 45 | postcode: 45200 | lat: 40.1395 | lon: -3.8326 | municipality: NULL
kind: desguace    | province: 04 | postcode: 04xxx | lat: NULL    | lon: NULL    | municipality: NULL
```

483 entidades tienen CP 5 dígitos válido. El CP en España no tiene correspondencia 1:1 con municipio INE (varios municipios comparten rango de CPs), pero con el fichero INE de CP→municipio (disponible en data.gob.es) se puede resolver el 80-90% de estos casos.

---

## 6. QUERIES DE VERIFICACIÓN (referencia)

```sql
-- Gap global
SELECT COUNT(*), COUNT(province_code), COUNT(municipality_code), COUNT(comarca_id), COUNT(lat)
FROM entity;
-- → 369535 / 369191 / 289497 / 288571 / 12499

-- Gap por kind
SELECT kind, COUNT(*), ROUND(COUNT(municipality_code)*100.0/COUNT(*),1) AS pct_mun
FROM entity GROUP BY kind ORDER BY 2 DESC;

-- Accionabilidad
SELECT CASE WHEN municipality_code IS NOT NULL THEN 'OK'
            WHEN lat IS NOT NULL THEN 'ACCIONABLE: reverse'
            WHEN postcode ~ '^[0-9]{5}$' THEN 'ACCIONABLE: CP'
            WHEN address IS NOT NULL THEN 'ACCIONABLE: address'
            WHEN province_code IS NOT NULL THEN 'BLOQUEADO: solo_prov'
            ELSE 'BLOQUEADO: sin_dato' END AS bucket,
       COUNT(*) FROM entity
WHERE kind NOT IN ('plataforma','subasta','oem_vo_portal','cadena')
GROUP BY 1 ORDER BY 2 DESC;

-- Fuentes que producen más gap
SELECT es.source_key, COUNT(*), e.kind
FROM entity e JOIN entity_source es ON es.entity_ulid = e.entity_ulid
WHERE e.municipality_code IS NULL
GROUP BY es.source_key, e.kind ORDER BY 2 DESC LIMIT 20;
```

---

## 7. ESTRATEGIAS CANDIDATAS PARA CERRAR EL GAP

### Estrategia A — Reverse-geocode lat/lon → municipio (7.837 entidades)
**Coste: €0. Dependencia: data.gob.es centroide de municipio.**  
Añadir `lat`/`lon` centroide a `geo_municipality` (disponible en el INE shapefile o en el propio `diccionario_ine.xlsx`). Luego para cada entidad con lat/lon y sin municipio: encontrar el municipio cuyo centroide es más cercano dentro de la misma provincia. Complejidad O(N×M) donde N≈8k entidades, M≈8k municipios — ejecutable en segundos con numpy (ya instalado). **Precisión estimada: >95%** en zonas no limítrofes.

**Mejora alternativa:** Añadir polígonos GeoJSON de municipios (CNIG, libre) y usar un join espacial con shapely (instalar shapely). Precisión: ~100%. Coste shapely: `pip install shapely` (~5MB, MIT).

### Estrategia B — CP → municipio (483 entidades)
**Coste: €0. Dependencia: fichero INE Relación CP-Municipio (data.gob.es, libre).**  
El INE publica la tabla de correspondencia CP↔municipio. Cargarla como `geo_postcode` y hacer un join. Cuando un CP cae en un solo municipio, resolución directa. Cuando es ambiguo: usar province_code como filtro — un CP siempre está en una sola provincia. **Precisión estimada: ~85%** (algunos CPs abarcan varios municipios limítrofes).

### Estrategia C — Fuzzy match city_name → municipio (particulares bloqueados)
**Coste: €0. Dependencia: rapidfuzz (instalar).**  
Para los 71.337 particulares con solo province_code: el `GeoResolver` ya intenta el match exacto de city_name; reforzarlo con fuzzy (Levenshtein o token_sort_ratio ≥ 85). **Solo aplicable si el scraper devuelve city_name** — en la muestra analizada los particulares con municipio NULL también tienen city NULL (el API no siempre lo entrega). **Impacto real estimado: bajo** — el bloqueo no es el match sino la ausencia de dato.

### Estrategia D — Re-scraping selectivo con city_name
**Coste: €0 directo. Dependencia: re-ejecutar wallapop_facet/milanuncios con extracción de city.**  
Verificar si el API de Wallapop/Milanuncios devuelve `location.city` para los anuncios de particulares que hoy tienen province_code pero municipality=NULL. Si el raw_data tiene city y el pipeline lo descartó, corregir el parser. Si el API no lo envía, bloqueado a nivel de fuente.

### Estrategia E — Trigger de autocompletado de comarca
**Coste: €0. Ya parcialmente implementado.**  
El trigger `trg_entity_set_comarca` ya propaga comarca cuando se rellena municipality_code. Estrategias A y B automáticamente rellenan comarca también. El gap de comarca (21,91%) se cierra en paralelo sin trabajo adicional.

---

## RESUMEN EJECUTIVO

- **Gap real municipio: 21,66% (80.038 entidades).** La cifra 32,5% no se reproduce.
- **Gap accionable inmediato: 2,26% (8.357 entidades)** — reverse-geocode lat/lon + CP.
- **Gap estructuralmente bloqueado: 19,36% (71.548 entidades)** — particulares Wallapop/Milanuncios sin city en el payload API. No se puede cerrar sin cambiar la fuente o añadir datos de terceros.
- **Geocoder actual:** GeoResolver local (text-match INE gazetteer + KNN provincia). Sin APIs externas. Sin Nominatim.
- **Herramientas geo faltantes:** shapely, geopy, rapidfuzz, unidecode — ninguna instalada.
- **Datasets locales:** `data/geo/diccionario_ine.xlsx` + `data/geo/comarcas_ine.xls` presentes. Falta: centroides municipio, tabla CP→municipio, polígonos GeoJSON.
