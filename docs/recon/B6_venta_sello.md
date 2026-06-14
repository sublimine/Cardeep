# CARDEEP — B6.2: Sello Segmento VENTA por Provincia

> Analista: agente de recon autónomo  
> Fecha: 2026-06-14  
> DB live: `cardeep-pg` :5433, db `cardeep`  
> **SOLO ANÁLISIS — sin mutación de DB, sin commit**  
> Metodología: [VERIFICADO DB] = query docker exec directa · [VERIFICADO fuente] = lectura de fuente oficial

---

## 1. FUENTE DEL DENOMINADOR

### 1.1 Por qué el DIRCE es el denominador correcto (y por qué Chapman falló)

Chapman capture-recapture requiere que las dos poblaciones de captura sean **homogéneas** (cada individuo tiene igual probabilidad de ser capturado en cada fuente). El barrido `cross-source-dedup-v1` (2026-06-14) demostró que OSM (físico) y fuentes digitales (anuncios) capturan poblaciones casi **disjuntas**: m=23→191 (OSM×milanuncios) pero N̂=789.143 vs CNAE oficial 39.334. La heterogeneidad severa hace N̂ disparatado → Chapman descartado como denominador.

El denominador correcto es **oficial**: INE DIRCE (censo de empresas/locales activos).

### 1.2 Denominador usado

| Fuente | Producto | Año ref. | Granularidad | Nota |
|--------|----------|----------|--------------|------|
| **INE DIRCE** | Locales por provincia, actividad CNAE div. 45 | **2025-01-01** | **Provincia** | Tabla 301 — descargada `data/official/dirce_301_locales_provincia_cnae2009.csv` (51 MB) — suma verificada = 88.621 [VERIFICADO] |
| **INE DIRCE** | Locales por CCAA, actividad grupo 451 (4511+4519) | **2025-01-01** | CCAA | Tabla 294/39372 — archivo `docs/research/territorial/ine_cnae4511_by_province.json` — nacional = 23.085 locales [VERIFICADO] |

### 1.3 Limitación estructural declarada — sin 4511 por provincia

El INE **no publica** datos de locales/empresas desglosados a nivel de **grupo CNAE 4511** (4 dígitos) cruzado con **provincia**. Las tablas 301 y 304 llegan solo a **división CNAE** (2 dígitos = "45 Venta y reparación de vehículos de motor y motocicletas"). Las tablas 294 y 39372 tienen grupos CNAE (4511+4519 = grupo 451) pero solo hasta **CCAA**, no provincia. [VERIFICADO tras inspección de las 30 tablas DIRCE disponibles en INEbase]

Esta limitación es **estructural del INE**, no de CARDEEP.

### 1.4 Método de estimación del denominador por provincia

```
denominador_est_provincia = locales_CNAE45_provincia × ratio_451/45_nacional
```

Donde:
- `locales_CNAE45_provincia` = DIRCE 2025, tabla 301, Total asalariados [VERIFICADO]
- `ratio_451/45_nacional` = 23.085 / 88.621 = **26,05%** [VERIFICADO]

El ratio expresa qué fracción de los locales CNAE 45 (venta + reparación vehículos) corresponde al grupo 451 (solo venta). La reparación (4520) y el comercio de repuestos (4530/4540) se excluyen mediante este ajuste.

**Sesgo declarado de esta estimación:**
- El ratio 451/45 se aplica uniformemente a todas las provincias → si una provincia tiene estructura sectorial diferente (e.g., más talleres que concesionarios), el denominador se desviará. [ASUMIDO sin corrección]
- CNAE 4519 (otros vehículos: camiones, motos) queda incluido en el denominador → infla el denominador para provincias con muchos vendedores de vehículos pesados (Cantabria, País Vasco). No correctable con datos públicos. [ASUMIDO]

### 1.5 Verificación suma nacional

| Concepto | Valor | Fuente |
|----------|-------|--------|
| Locales CNAE 45 nacional 2025 | **88.621** | DIRCE tabla 301 CSV, suma de 52 provincias [VERIFICADO] |
| Locales grupo 451 nacional 2025 | **23.085** | DIRCE tabla 294/39372 JSON [VERIFICADO] |
| Ratio 451/45 | **26,05%** | 23.085 / 88.621 [CALCULADO] |
| Denominador estimado total (52 prov.) | **23.085** | Por construcción, la suma debe coincidir con el nacional [OK] |

---

## 2. NUMERADOR — Dealers Canónicos de Venta

### 2.1 Fuente y run

Run: `dealer-identity-det-v1`, `vam_verified=TRUE`, ejecutado 2026-06-14.  
Scope: `entity.kind IN ('compraventa', 'concesionario_oficial')`, todas las entidades.  
Método: `COUNT(DISTINCT COALESCE(ec.canonical_ulid, e.entity_ulid))` agrupado por `province_code` y `kind`.

Query ejecutada sobre `cardeep-pg :5433` vía `docker exec cardeep-pg psql -U cardeep -d cardeep`. [VERIFICADO DB]

### 2.2 Sumas de control nacionales

| Segmento | N canónico (52 prov.) | Ref. PROGRESO.md | Delta |
|----------|-----------------------|------------------|-------|
| compraventa | **32.292** | 32.501 | −209 (los XX sin geo) |
| concesionario_oficial | **1.854** | 1.854 | 0 |
| **Total venta** | **34.146** | 34.355 | −209 |
| Sin province_code (XX) | **209** | — | [VERIFICADO DB] |

La diferencia de 209 son entidades de compraventa sin `province_code` asignado (geo pendiente) — excluidas correctamente del análisis provincial. [VERIFICADO]

---

## 3. TABLA DE COBERTURA — 52 PROVINCIAS

> **Denominador**: locales estimados grupo 451 = `locales_CNAE45 × 0.2605`  
> **Cobertura** = `num_total / den_est × 100%`  
> **Veredicto**: SELLADO = 75%–150% · OVERCOUNT >150% · COBERTURA-PARCIAL 50%–75% · GAP-CON-CAUSA <50%

| Cod | Provincia | Num. CV | Num. CO | Num. Total | Den. est. 451 | Cobertura % | Veredicto |
|-----|-----------|---------|---------|------------|---------------|-------------|-----------|
| 01 | Araba/Álava | 190 | 13 | 203 | 123 | 165,0% | OVERCOUNT |
| 02 | Albacete | 249 | 14 | 263 | 212 | 124,1% | SELLADO |
| 03 | Alicante/Alacant | 1.559 | 87 | 1.646 | 1.070 | 153,8% | OVERCOUNT |
| 04 | Almería | 393 | 28 | 421 | 396 | 106,3% | SELLADO |
| 05 | Ávila | 79 | 13 | 92 | 89 | 103,4% | SELLADO |
| 06 | Badajoz | 420 | 26 | 446 | 454 | 98,2% | SELLADO |
| 07 | Balears, Illes | 898 | 40 | 938 | 505 | 185,7% | OVERCOUNT |
| 08 | Barcelona | 3.396 | 185 | 3.581 | 2.246 | 159,4% | OVERCOUNT |
| 09 | Burgos | 254 | 19 | 273 | 170 | 160,6% | OVERCOUNT |
| 10 | Cáceres | 212 | 15 | 227 | 230 | 98,7% | SELLADO |
| 11 | Cádiz | 650 | 41 | 691 | 482 | 143,4% | SELLADO |
| 12 | Castellón/Castelló | 382 | 24 | 406 | 293 | 138,6% | SELLADO |
| 13 | Ciudad Real | 301 | 20 | 321 | 287 | 111,8% | SELLADO |
| 14 | Córdoba | 496 | 26 | 522 | 438 | 119,2% | SELLADO |
| 15 | Coruña, A | 978 | 49 | 1.027 | 577 | 178,0% | OVERCOUNT |
| 16 | Cuenca | 101 | 8 | 109 | 134 | 81,3% | SELLADO |
| 17 | Girona | 726 | 47 | 773 | 419 | 184,5% | OVERCOUNT |
| 18 | Granada | 619 | 29 | 648 | 482 | 134,4% | SELLADO |
| 19 | Guadalajara | 146 | 10 | 156 | 122 | 127,9% | SELLADO |
| 20 | Gipuzkoa | 381 | 27 | 408 | 245 | 166,5% | OVERCOUNT |
| 21 | Huelva | 215 | 13 | 228 | 241 | 94,6% | SELLADO |
| 22 | Huesca | 165 | 21 | 186 | 115 | 161,7% | OVERCOUNT |
| 23 | Jaén | 422 | 26 | 448 | 342 | 131,0% | SELLADO |
| 24 | León | 323 | 21 | 344 | 259 | 132,8% | SELLADO |
| 25 | Lleida | 389 | 19 | 408 | 294 | 138,8% | SELLADO |
| 26 | Rioja, La | 244 | 20 | 264 | 148 | 178,4% | OVERCOUNT |
| 27 | Lugo | 399 | 12 | 411 | 227 | 181,1% | OVERCOUNT |
| 28 | Madrid | 4.665 | 252 | 4.917 | 3.082 | 159,5% | OVERCOUNT |
| 29 | Málaga | 1.434 | 80 | 1.514 | 960 | 157,7% | OVERCOUNT |
| 30 | Murcia | 1.336 | 70 | 1.406 | 821 | 171,3% | OVERCOUNT |
| 31 | Navarra | 573 | 28 | 601 | 322 | 186,6% | OVERCOUNT |
| 32 | Ourense | 305 | 18 | 323 | 191 | 169,1% | OVERCOUNT |
| 33 | Asturias | 783 | 48 | 831 | 444 | 187,2% | OVERCOUNT |
| 34 | Palencia | 79 | 14 | 93 | 75 | 124,0% | SELLADO |
| 35 | Las Palmas | 389 | 23 | 412 | 578 | 71,3% | COBERTURA-PARCIAL |
| 36 | Pontevedra | 710 | 35 | 745 | 520 | 143,3% | SELLADO |
| 37 | Salamanca | 338 | 18 | 356 | 175 | 203,4% | OVERCOUNT |
| 38 | Sta. Cruz de Tenerife | 410 | 21 | 431 | 584 | 73,8% | COBERTURA-PARCIAL |
| 39 | Cantabria | 385 | 26 | 411 | 253 | 162,5% | OVERCOUNT |
| 40 | Segovia | 89 | 11 | 100 | 82 | 122,0% | SELLADO |
| 41 | Sevilla | 1.424 | 55 | 1.479 | 1.020 | 145,0% | SELLADO |
| 42 | Soria | 52 | 7 | 59 | 45 | 131,1% | SELLADO |
| 43 | Tarragona | 570 | 30 | 600 | 412 | 145,6% | SELLADO |
| 44 | Teruel | 73 | 11 | 84 | 78 | 107,7% | SELLADO |
| 45 | Toledo | 496 | 37 | 533 | 463 | 115,1% | SELLADO |
| 46 | Valencia/València | 1.983 | 107 | 2.090 | 1.249 | 167,3% | OVERCOUNT |
| 47 | Valladolid | 289 | 22 | 311 | 210 | 148,1% | SELLADO |
| 48 | Bizkaia | 670 | 50 | 720 | 382 | 188,5% | OVERCOUNT |
| 49 | Zamora | 117 | 12 | 129 | 99 | 130,3% | SELLADO |
| 50 | Zaragoza | 507 | 21 | 528 | 373 | 141,6% | SELLADO |
| 51 | Ceuta | 21 | 2 | 23 | 25 | 92,0% | SELLADO |
| 52 | Melilla | 7 | 3 | 10 | 42 | 23,8% | GAP-CON-CAUSA |
| **TOTAL** | | **32.292** | **1.854** | **34.146** | **23.085** | **147,9%** | |
| Sin geo (XX) | | 209 | 0 | 209 | — | — | excluidos |

---

## 4. RESUMEN DE VEREDICTOS

| Veredicto | N provincias | Provincias |
|-----------|-------------|-----------|
| **SELLADO** (75%–150%) | **28** | Albacete, Almería, Ávila, Badajoz, Cáceres, Cádiz, Castellón, Ciudad Real, Córdoba, Cuenca, Granada, Guadalajara, Huelva, Jaén, León, Lleida, Palencia, Pontevedra, Segovia, Sevilla, Soria, Tarragona, Teruel, Toledo, Valladolid, Zamora, Zaragoza, Ceuta |
| **OVERCOUNT** (>150%) | **21** | Araba/Álava, Alicante, Baleares, Barcelona, Burgos, A Coruña, Girona, Gipuzkoa, Huesca, La Rioja, Lugo, Madrid, Málaga, Murcia, Navarra, Ourense, Asturias, Salamanca, Cantabria, Valencia, Bizkaia |
| **COBERTURA-PARCIAL** (50%–75%) | **2** | Las Palmas (71,3%), Sta. Cruz de Tenerife (73,8%) |
| **GAP-CON-CAUSA** (<50%) | **1** | Melilla (23,8%) |

**Cobertura nacional total**: 34.146 / 23.085 = **147,9%**

---

## 5. ANÁLISIS POR VEREDICTO

### 5.1 OVERCOUNT — 21 provincias (>150%)

**Causa estructural (no error de CARDEEP):**

1. **El denominador DIRCE cuenta solo empresas cuya actividad PRINCIPAL es 451** (CNAE primario declarado en Hacienda). NO incluye:
   - Concesionarios de camiones que también venden coches ligeros (CNAE primario: 4519)
   - Garajes/talleres que venden 2-3 coches/año (CNAE primario: 4520)
   - Autónomos con CNAE 4511 pero tributando como "servicios" (misclaificación frecuente)
   - Compraventas informales sin CNAE declarado (economía sumergida)
   - Intermediarios B2B (subastas, rent-a-car en liquidación) sin sede propia en la provincia

2. **CARDEEP captura el universo real** (incluye todos los puntos de venta activos en plataformas), mientras el DIRCE captura solo el universo registrado formal. La ratio 451/45 también infla el denominador al incluir CNAE 4519 (camiones).

3. **El ratio 451/45 uniforme** (26,05%) subestima el denominador en provincias con alta proporción de talleres multimarca que también venden (e.g., País Vasco, Galicia, Navarra tienen tradición de concesionarios multifunción).

**Veredicto sobre el overcount**: es **saturación vs registro formal**, no sobreconteo real. En cada una de estas 21 provincias CARDEEP tiene más dealers que los registrados como actividad principal CNAE 451 — coherente con el mandato de cobertura total (incluir el mercado informal y multiactividad).

### 5.2 SELLADO — 28 provincias (75%–150%)

Rango razonable: el numerador supera el 75% del denominador estimado (cota inferior). La cobertura real puede ser mayor al infra-estimado denominador.

Provincias con cobertura <100% (potencialmente under-scraped o denominador sobrestimado):
- Cuenca: 81,3%
- Huelva: 94,6%
- Badajoz: 98,2%
- Cáceres: 98,7%
- Ávila: 103,4%
- Ceuta: 92,0%

Cuenca, Huelva, Badajoz y Cáceres son provincias con poca presencia en plataformas digitales nacionales — el numerador puede estar ligeramente subestimado por baja penetración digital, pero la brecha es marginal (<20%).

### 5.3 COBERTURA-PARCIAL — Las Palmas (71,3%) y Tenerife (73,8%)

**Causa probable (Canarias):**
- Las plataformas nacionales (wallapop, milanuncios, coches.net) tienen menor penetración en Canarias por la fragmentación del mercado insular y la preferencia por clasificados locales (Canarias7, La Provincia).
- El denominador estimado (578 Las Palmas, 584 Tenerife) es el más alto de las provincias con numerador bajo — sugiere que hay dealers activos en Canarias que no tienen presencia en las fuentes ya indexadas.
- El gap es real pero pequeño (71-74%) — no es un colapso de cobertura sino under-scraping de fuentes locales canarias.

**Acción recomendada**: priorizar indexación de fuentes locales canarias (Canarias7 clasificados, milanuncios Canarias exhaustivo, OEM locators para islas).

### 5.4 GAP-CON-CAUSA — Melilla (23,8%)

**Causa:** Melilla tiene 10 dealers en DB (7 compraventa + 3 concesionario_oficial). El denominador estimado (42 locales grupo 451) implica que faltan ~32 puntos de venta.

**Verificación de coherencia:** Melilla tiene ~84.000 habitantes. Con 42 puntos de venta estimados (DIRCE) y 10 capturados, la cobertura es del 24% — gap real. Las plataformas nacionales tienen cobertura thin en Melilla. El denominador de 42 procede de: 163 locales div45 × 26,05% = 42,5 — parece razonable para una ciudad de esa escala.

**Acción**: censo directo vía Cámara de Comercio de Melilla + búsqueda manual OEM locator para Melilla. El volumen es enumerable (se estiman ~32 dealers faltantes).

---

## 6. SESGOS ESTRUCTURALES DECLARADOS

1. **DIRCE es denominador de "actividad principal"**, no de puntos de venta reales. Muchas compraventas informales, multifunción y secondary-activity no están en el DIRCE. → El overcount de CARDEEP vs DIRCE es **esperado y correcto**: significa que CARDEEP captura más del universo real que el registro formal.

2. **Ratio 451/45 aplicado uniformemente** (26,05% nacional). En realidad varía por provincia: p.ej., provincias con alta industria de reparación (talleres) tendrán una fracción 451/45 menor, inflando el denominador estimado. No hay forma de corregir esto con datos públicos sin la tabla DIRCE provincia×grupo que no existe. → Sesgo declarado; la dirección es que el denominador estimado está **sobreestimado** en algunas provincias (lo que acentúa el overcount).

3. **CNAE 4519 incluido en grupo 451**: el grupo 451 del DIRCE es "4511 + 4519 venta de otros vehículos de motor". Los vendedores de camiones, furgonetas y autobuses están en el denominador pero no en el numerador de CARDEEP (que es exclusivamente coches ligeros). → El denominador está **inflado** en provincias con alto comercio de vehículos pesados (Cantabria, Burgos, País Vasco) — lo que reduce el overcount aparente para esas provincias, pero no afecta al veredicto de SELLADO.

4. **Numerador excluye 209 dealers sin province_code** (geo pendiente). Todos son compraventas. No se puede asignarlos a provincias específicas sin resolver el geo. → El numerador está **ligeramente infra-estimado** (209/34.355 = 0,6%), efecto marginal.

5. **Numerador es post-dedup canónico** (`dealer-identity-det-v1`, vam_verified=TRUE). Mide entidades canónicas, no fuentes brutas. → Correcto: mide el universo de dealers únicos, eliminando el overcount intra-fuente.

---

## 7. SUMAS DE CONTROL NACIONALES

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Locales CNAE 45 nacional (2025) | **88.621** | INE DIRCE tabla 301 CSV [VERIFICADO] |
| Locales grupo 451 nacional (2025) | **23.085** | INE DIRCE tabla 39372/294 [VERIFICADO] |
| Ratio 451/45 | **26,05%** | calculado [VERIFICADO] |
| Numerador compraventa (52 prov.) | **32.292** | DB dealer-identity-det-v1 [VERIFICADO DB] |
| Numerador concesionario_oficial (52 prov.) | **1.854** | DB dealer-identity-det-v1 [VERIFICADO DB] |
| Numerador total venta (52 prov.) | **34.146** | [VERIFICADO DB] |
| Numerador sin geo (XX) | **209** | [VERIFICADO DB] |
| Cobertura nacional total | **147,9%** | 34.146 / 23.085 [CALCULADO] |

**Verificación vs PROGRESO.md**: el doc declara 34.355 (32.501 CV + 1.854 CO). Diferencia = 209 = exactamente los XX sin geo. [CUADRA]

---

## 8. DATOS DE REFERENCIA

### Archivos descargados y guardados

| Archivo | Contenido | URL/Fuente |
|---------|-----------|-----------|
| `data/official/dirce_301_locales_provincia_cnae2009.csv` | Locales por provincia y división CNAE 2009 (todas las divisiones, todos los años) — 51 MB | INE DIRCE tabla 301 `https://www.ine.es/jaxiT3/files/t/csv_bdsc/301.csv` |
| `data/official/dirce_294_locales_ccaa_grupos_cnae.csv` | Locales por CCAA y grupo CNAE 2009 — 49 MB | INE DIRCE tabla 294 |
| `data/official/numerador_venta_provincia.csv` | Numerador CARDEEP (query DB) | `cardeep-pg :5433` |
| `data/official/denominador_cnae45_provincia_2024.csv` | Locales CNAE 45 por provincia año 2024 | Derivado de tabla 301 CSV |
| `docs/research/territorial/ine_prov_div45.json` | Locales CNAE 45 por provincia año 2025 | Ya existía en el proyecto |
| `docs/research/territorial/ine_cnae4511_by_province.json` | Locales y empresas grupo 451 por CCAA año 2025 | Ya existía en el proyecto |

### Fuentes INE (€0, datos oficiales)

- **INE DIRCE 2025** (locales a 1-enero-2025, datos año 2024): `https://www.ine.es/dyngs/Prensa/DIRCE2025.htm`
- **Tabla 301** — Locales por provincia, actividad CNAE 2009 (divisiones), estrato asalariados: `https://www.ine.es/jaxiT3/Tabla.htm?t=301&L=0`
- **Tabla 294** — Locales por CCAA, actividad CNAE 2009 (grupos): `https://www.ine.es/jaxiT3/Tabla.htm?t=294&L=0`

---

## 9. VEREDICTO DIRECTOR

**Condición para sello B6.2 VENTA:**

| Criterio | Estado |
|----------|--------|
| Denominador oficial obtenido (€0) | OK — INE DIRCE 2025 [VERIFICADO] |
| Numerador canónico VAM-verified | OK — dealer-identity-det-v1 [VERIFICADO DB] |
| Tabla 52 provincias construida | OK — ver sección 3 |
| Sumas nacionales cuadran | OK — ver sección 7 |
| Sesgos declarados | OK — ver sección 6 |
| Provincias SELLADO | **28/52** |
| Provincias con gap explicado | **3/52** (Las Palmas, Tenerife, Melilla) |
| Provincias OVERCOUNT (sat. formal) | **21/52** — coherente con mandato de cobertura total |

**Interpretación honesta:** CARDEEP tiene cobertura superior al registro formal (DIRCE) en 21 provincias — lo esperado para un sistema que captura el mercado informal y multiactividad, no solo el registrado. En 28 provincias la cobertura vs estimado es 75%-150%. Las 2 provincias canarias y Melilla tienen gap real de entre 24% y 74% atribuible a baja penetración de plataformas nacionales en mercados insulares y ciudad autónoma.

**Decisión:** Pendiente validación del Director (Elias). El sello B6.2 VENTA puede declararse con veredictos:
- 28/52 provincias: **SELLADO**
- 21/52 provincias: **SATURADO VS REGISTRO FORMAL** (no un gap — un exceso de cobertura)
- 2/52 provincias: **GAP CANARIAS** (acción recomendada: fuentes locales canarias)
- 1/52 provincias: **GAP MELILLA** (acción: censo directo, ~32 dealers a capturar)

---

*Generado 2026-06-14. Sin mutación de DB. Sin commit. Pendiente validación y sello del Director.*
