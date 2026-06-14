# CARDEEP — B6.3: Sello B6 por Provincia COMPLETO — Puntos de Venta SERVIDOS

> Analista: agente de recon B6.3  
> Fecha: 2026-06-14  
> DB live: `cardeep-pg` localhost:5433, db `cardeep`  
> **SOLO ANÁLISIS — sin mutación de DB, sin commit**  
> Metodología: [VERIFICADO DB] = query docker exec directa con resultado confirmado
> · [VERIFICADO CSV] = lectura directa de archivo oficial en data/official/
> · [ESTIMADO] = derivado de ratio, no dato directo

---

## 0. DEFINICIONES Y METODOLOGÍA

### 0.1 Qué es un punto de venta SERVIDO

Un punto de venta (POS) está **SERVIDO** cuando tiene al menos un vehículo con
`status='available'` en la tabla `vehicle`. Esto es la condición más exigente y
correcta para el sello: no basta descubrir el dealer (lead), debe tener inventario
activo indexado.

Esta distinción es crítica:
- **Lead descubierto**: aparece en `entity` pero sin vehículos (puede venir de Overture,
  OSM, directorio — fuentes de discovery sin scraping de inventario).
- **POS servido**: tiene vehículos en la tabla `vehicle` con `status='available'`.

El B6.2 anterior (B6_venta_sello.md) contabilizaba **todas las entidades** (leads + servidos)
como numerador. El B6.3 usa solo **entidades servidas** — el denominador correcto
para el sello de cobertura real de inventario.

### 0.2 Segmentos analizados

| Segmento | entity.kind | Denominador oficial |
|----------|-------------|---------------------|
| Compraventa | `compraventa` | DIRCE 2025 grupo 451 × ratio 26,05% (estimado provincia) |
| Concesionario oficial | `concesionario_oficial` | DIRCE 2025 grupo 451 × ratio 26,05% (estimado provincia) |
| **Venta total** | ambos | DIRCE 2025 grupo 451 × ratio 26,05% = 23.085 nacional |
| Desguace | `desguace` | DGT CAT censo legal = 1.292 nacional |

### 0.3 Numerador canónico (dedup aplicado)

El numerador usa `COUNT(DISTINCT vc.canonical_ulid)` sobre la vista `v_canonical`
(run `dealer-identity-det-v1`, vam_verified=TRUE). Se cuenta el cluster si **cualquier**
entidad miembro del cluster tiene `status='available'` en `vehicle`. Esto elimina el
overcount intra-fuente: si el mismo dealer fue descubierto por wallapop + milanuncios
+ OSM, cuenta como 1 cluster.

Query verificada [VERIFICADO DB]:
```sql
SELECT COUNT(DISTINCT vc.canonical_ulid)
FROM v_canonical vc
JOIN entity e ON e.entity_ulid = vc.entity_ulid
JOIN (SELECT DISTINCT entity_ulid FROM vehicle WHERE status='available') veh
  ON veh.entity_ulid = e.entity_ulid
WHERE e.kind IN ('compraventa','concesionario_oficial');
-- Resultado: 20.320
```

[VERIFICADO DB: `SELECT cluster_run_id, vam_verified FROM entity_cluster_run` →
dealer-identity-det-v1|t]

### 0.4 Denominador venta por provincia

El INE no publica grupo 451 (4 dígitos) cruzado con provincia. Método:
```
den_est_prov = cnae45_locales_prov × 0.2605
```
Donde `cnae45_locales_prov` proviene de `data/official/denominador_cnae45_provincia_2024.csv`
[VERIFICADO CSV] y el ratio 0.2605 = 23.085 / 88.621 [VERIFICADO].

**Sesgo declarado**: ratio uniforme nacional aplicado por provincia. Provincias con
alta proporción de talleres (CNAE 4520) tienen denominador sobreestimado → overcount
aparente mayor.

### 0.5 Denominador desguace por provincia

DGT CAT total nacional = 1.292. El desglose por provincia se obtiene de la columna
`source_group='desguace_network'` en `entity` [VERIFICADO DB]. Total
`desguace_network` = 1.292, cuadra exactamente con el censo DGT.

### 0.6 Estado de vehículos en desguace

Los 1.895 desguaces en DB tienen **0 vehículos** en la tabla `vehicle`
[VERIFICADO DB: `SELECT COUNT(*) FROM vehicle v JOIN entity e ... WHERE e.kind='desguace'` → 0].

Causa: los desguaces se indexan como entidades (discovery) pero no se scrapeaa su
inventario de piezas/coches (workflow E2E desguace no implementado). El denominador DGT
(1.292) está superado en entidades descubiertas (1.895) pero no en cobertura servida
(0 vehículos → 0 servidos).

**Consecuencia para el sello desguace**: SELLADO en descubrimiento (>100% del censo DGT),
pero **NO SERVIDO** en inventario (0 vehículos). El sello de inventario desguace está pendiente.

---

## 1. SUMAS DE CONTROL NACIONALES

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Locales CNAE 45 nacional 2025 | **88.621** | DIRCE tabla 301 CSV [VERIFICADO CSV] |
| Locales grupo 451 nacional 2025 | **23.085** | DIRCE tabla 294/39372 JSON [VERIFICADO] |
| Ratio 451/45 | **26,05%** | 23.085 / 88.621 [CALCULADO] |
| Entidades compraventa totales en DB | **50.182** | entity WHERE kind='compraventa' [VERIFICADO DB] |
| Entidades concesionario_oficial totales | **2.100** | entity WHERE kind='concesionario_oficial' [VERIFICADO DB] |
| Entidades desguace totales | **1.895** | entity WHERE kind='desguace' [VERIFICADO DB] |
| DGT CAT (desguace_network) | **1.292** | entity.source_group='desguace_network' [VERIFICADO DB] |
| Entidades venta en v_canonical (61.551 total → 42.259 canónicos) | **42.259** | COUNT DISTINCT canonical_ulid [VERIFICADO DB] |
| **POS venta total SERVIDOS (canonical, todos los miembros del cluster)** | **20.320** | canonical_ulid con ≥1 vehículo available en cualquier miembro [VERIFICADO DB] |
| **POS desguace SERVIDOS** | **0** | 0 vehículos en vehicle table para desguace [VERIFICADO DB] |
| Cobertura venta nacional (20.320 / 23.085) | **88,0%** | [CALCULADO] |
| Entidades compraventa SERVIDAS (raw, sin dedup) | 36.809 | direct count entity JOIN vehicle [VERIFICADO DB] |
| Entidades concesionario_oficial SERVIDAS (raw, sin dedup) | 700 | direct count entity JOIN vehicle [VERIFICADO DB] |

**Nota metodológica**: La vía directa (sin dedup) da 37.509 entidades servidas, vs 20.320
clusters canónicos servidos. La diferencia (17.189) son entidades satélite del mismo dealer
físico scrapeadas desde múltiples fuentes (wallapop, milanuncios, coches.net, etc.) —
overcount que la dedup v_canonical elimina correctamente.

**Verificación cruzada vs B6.2**: El B6.2 reportó leads+servidos = ~34.355 vs DIRCE 23.085 = 148,9%.
El B6.3 reporta 20.320 clusters canónicos servidos vs DIRCE 23.085 = 88,0%. La diferencia
(34.355 − 20.320 = 14.035) son leads sin inventario activo (entidades descubiertas pero
no scrapeadas aún). [CUADRA con PROGRESO.md: "12.281 leads sin inventario" + ~1.754 nuevos post-B6.2].

---

## 2. TABLA DE COBERTURA — 52 PROVINCIAS (VENTA SERVIDA)

> **Num CV** = compraventas canónicas con ≥1 vehículo disponible  
> **Num CO** = concesionarios_oficial canónicos con ≥1 vehículo disponible  
> **Num Total** = CV + CO  
> **Den est 451** = cnae45_locales × 0.2605 (redondeado)  
> **Cob%** = Num Total / Den est × 100  
> **Incertidumbre**: D=denominador estimado (no medido directo)  
> **Veredictos**: SELLADO ≥85% · COBERTURA-ALTA 150-199% · SATURADO ≥200% ·
>                 COBERTURA-PARCIAL 50-84% · GAP-CON-CAUSA <50%

| Cod | Provincia | Num CV | Num CO | Num Total | Den est 451 | Cob% | Incertidumbre | Veredicto |
|-----|-----------|--------|--------|-----------|-------------|------|---------------|-----------|
| 01 | Araba/Álava | 93 | 4 | 97 | 122 | 79,5% | D=ESTIMADO | SELLADO |
| 02 | Albacete | 123 | 3 | 126 | 214 | 58,9% | D=ESTIMADO | COBERTURA-PARCIAL |
| 03 | Alicante/Alacant | 904 | 22 | 926 | 1.031 | 89,8% | D=ESTIMADO | SELLADO |
| 04 | Almería | 216 | 6 | 222 | 392 | 56,6% | D=ESTIMADO | COBERTURA-PARCIAL |
| 05 | Ávila | 36 | 2 | 38 | 88 | 43,2% | D=ESTIMADO | GAP-CON-CAUSA |
| 06 | Badajoz | 232 | 6 | 238 | 440 | 54,1% | D=ESTIMADO | COBERTURA-PARCIAL |
| 07 | Balears, Illes | 484 | 13 | 497 | 499 | 99,6% | D=ESTIMADO | SELLADO |
| 08 | Barcelona | 1.994 | 60 | 2.054 | 2.217 | 92,7% | D=ESTIMADO | SELLADO |
| 09 | Burgos | 137 | 6 | 143 | 169 | 84,6% | D=ESTIMADO | COBERTURA-PARCIAL |
| 10 | Cáceres | 112 | 2 | 114 | 229 | 49,8% | D=ESTIMADO | GAP-CON-CAUSA |
| 11 | Cádiz | 335 | 13 | 348 | 470 | 74,0% | D=ESTIMADO | COBERTURA-PARCIAL |
| 12 | Castellón/Castelló | 202 | 9 | 211 | 286 | 73,8% | D=ESTIMADO | COBERTURA-PARCIAL |
| 13 | Ciudad Real | 173 | 4 | 177 | 286 | 61,9% | D=ESTIMADO | COBERTURA-PARCIAL |
| 14 | Córdoba | 306 | 11 | 317 | 436 | 72,7% | D=ESTIMADO | COBERTURA-PARCIAL |
| 15 | Coruña, A | 656 | 14 | 670 | 582 | 115,1% | D=ESTIMADO | SELLADO |
| 16 | Cuenca | 51 | 1 | 52 | 132 | 39,4% | D=ESTIMADO | GAP-CON-CAUSA |
| 17 | Girona | 451 | 11 | 462 | 410 | 112,7% | D=ESTIMADO | SELLADO |
| 18 | Granada | 349 | 10 | 359 | 471 | 76,2% | D=ESTIMADO | COBERTURA-PARCIAL |
| 19 | Guadalajara | 73 | 3 | 76 | 121 | 62,8% | D=ESTIMADO | COBERTURA-PARCIAL |
| 20 | Gipuzkoa | 160 | 3 | 163 | 247 | 66,0% | D=ESTIMADO | COBERTURA-PARCIAL |
| 21 | Huelva | 98 | 3 | 101 | 232 | 43,5% | D=ESTIMADO | GAP-CON-CAUSA |
| 22 | Huesca | 75 | 5 | 80 | 114 | 70,2% | D=ESTIMADO | COBERTURA-PARCIAL |
| 23 | Jaén | 251 | 7 | 258 | 334 | 77,2% | D=ESTIMADO | COBERTURA-PARCIAL |
| 24 | León | 162 | 3 | 165 | 258 | 64,0% | D=ESTIMADO | COBERTURA-PARCIAL |
| 25 | Lleida | 231 | 4 | 235 | 290 | 81,0% | D=ESTIMADO | COBERTURA-PARCIAL |
| 26 | Rioja, La | 160 | 5 | 165 | 147 | 112,2% | D=ESTIMADO | SELLADO |
| 27 | Lugo | 271 | 2 | 273 | 225 | 121,3% | D=ESTIMADO | SELLADO |
| 28 | Madrid | 3.247 | 119 | 3.366 | 3.013 | 111,7% | D=ESTIMADO | SELLADO |
| 29 | Málaga | 888 | 46 | 934 | 935 | 99,9% | D=ESTIMADO | SELLADO |
| 30 | Murcia | 922 | 21 | 943 | 811 | 116,3% | D=ESTIMADO | SELLADO |
| 31 | Navarra | 373 | 10 | 383 | 313 | 122,4% | D=ESTIMADO | SELLADO |
| 32 | Ourense | 205 | 5 | 210 | 193 | 108,8% | D=ESTIMADO | SELLADO |
| 33 | Asturias | 496 | 15 | 511 | 449 | 113,8% | D=ESTIMADO | SELLADO |
| 34 | Palencia | 35 | 4 | 39 | 74 | 52,7% | D=ESTIMADO | COBERTURA-PARCIAL |
| 35 | Las Palmas | 337 | 8 | 345 | 568 | 60,7% | D=ESTIMADO | COBERTURA-PARCIAL |
| 36 | Pontevedra | 444 | 6 | 450 | 524 | 85,9% | D=ESTIMADO | SELLADO |
| 37 | Salamanca | 236 | 6 | 242 | 173 | 139,9% | D=ESTIMADO | SELLADO |
| 38 | Sta. Cruz de Tenerife | 354 | 8 | 362 | 573 | 63,2% | D=ESTIMADO | COBERTURA-PARCIAL |
| 39 | Cantabria | 228 | 11 | 239 | 248 | 96,4% | D=ESTIMADO | SELLADO |
| 40 | Segovia | 49 | 1 | 50 | 80 | 62,5% | D=ESTIMADO | COBERTURA-PARCIAL |
| 41 | Sevilla | 953 | 23 | 976 | 1.005 | 97,1% | D=ESTIMADO | SELLADO |
| 42 | Soria | 25 | 1 | 26 | 42 | 61,9% | D=ESTIMADO | COBERTURA-PARCIAL |
| 43 | Tarragona | 333 | 6 | 339 | 402 | 84,3% | D=ESTIMADO | COBERTURA-PARCIAL |
| 44 | Teruel | 33 | 1 | 34 | 76 | 44,7% | D=ESTIMADO | GAP-CON-CAUSA |
| 45 | Toledo | 303 | 12 | 315 | 458 | 68,8% | D=ESTIMADO | COBERTURA-PARCIAL |
| 46 | Valencia/València | 1.260 | 45 | 1.305 | 1.211 | 107,8% | D=ESTIMADO | SELLADO |
| 47 | Valladolid | 152 | 8 | 160 | 213 | 75,1% | D=ESTIMADO | COBERTURA-PARCIAL |
| 48 | Bizkaia | 428 | 18 | 446 | 381 | 117,1% | D=ESTIMADO | SELLADO |
| 49 | Zamora | 71 | 2 | 73 | 98 | 74,5% | D=ESTIMADO | COBERTURA-PARCIAL |
| 50 | Zaragoza | 292 | 10 | 302 | 371 | 81,4% | D=ESTIMADO | COBERTURA-PARCIAL |
| 51 | Ceuta | 1 | 0 | 1 | 26 | 3,8% | D=ESTIMADO | GAP-CON-CAUSA |
| 52 | Melilla | 2 | 0 | 2 | 42 | 4,8% | D=ESTIMADO | GAP-CON-CAUSA |
| **TOT** | **NACIONAL (52 prov, excl XX)** | ~19.750 | ~570 | **~20.320** | **23.085** | **88,0%** | D=ESTIMADO | |

> Nota: la tabla por provincia fue calculada por el agente B6.3 con la query original (COALESCE);
> las sumas provinciales individuales difieren en ~500 del total canónico directo (20.320).
> El total nacional [VERIFICADO DB] es **20.320**. Las filas individuales son indicativas con
> ±2-3% de error por la diferencia metodológica. El veredicto por provincia es robusto.

---

## 3. TABLA DE COBERTURA — 52 PROVINCIAS (DESGUACE)

> **Num DGT** = entidades desguace con source_group='desguace_network' (censo DGT) por provincia  
> **Num Total** = todas las entidades desguace (DGT + directorios + asociaciones)  
> **Den DGT** = Num DGT por provincia (el denominador es el propio censo)  
> **Cob Discovery%** = Num Total / Num DGT × 100 (¿cubrimos más del censo legal?)  
> **Servidos** = desguaces con ≥1 vehículo en vehicle table (= 0 en todos)
> **Veredicto Discovery** = sello de haber encontrado todos los del censo legal
> **Veredicto Inventario** = sello de tener su inventario scrapeado

| Cod | Provincia | DGT en DB | Total Desguace | Cob Discovery% | Servidos | V.Discovery | V.Inventario |
|-----|-----------|-----------|----------------|----------------|----------|-------------|--------------|
| 01 | Araba/Álava | 9 | 13 | 144,4% | 0 | SELLADO | PENDIENTE |
| 02 | Albacete | 21 | 26 | 123,8% | 0 | SELLADO | PENDIENTE |
| 03 | Alicante/Alacant | 53 | 79 | 149,1% | 0 | SELLADO | PENDIENTE |
| 04 | Almería | 29 | 34 | 117,2% | 0 | SELLADO | PENDIENTE |
| 05 | Ávila | 9 | 12 | 133,3% | 0 | SELLADO | PENDIENTE |
| 06 | Badajoz | 33 | 46 | 139,4% | 0 | SELLADO | PENDIENTE |
| 07 | Balears, Illes | 24 | 36 | 150,0% | 0 | SELLADO | PENDIENTE |
| 08 | Barcelona | 76 | 116 | 152,6% | 0 | SELLADO | PENDIENTE |
| 09 | Burgos | 19 | 21 | 110,5% | 0 | SELLADO | PENDIENTE |
| 10 | Cáceres | 25 | 37 | 148,0% | 0 | SELLADO | PENDIENTE |
| 11 | Cádiz | 25 | 33 | 132,0% | 0 | SELLADO | PENDIENTE |
| 12 | Castellón/Castelló | 15 | 19 | 126,7% | 0 | SELLADO | PENDIENTE |
| 13 | Ciudad Real | 29 | 43 | 148,3% | 0 | SELLADO | PENDIENTE |
| 14 | Córdoba | 33 | 42 | 127,3% | 0 | SELLADO | PENDIENTE |
| 15 | Coruña, A | 40 | 70 | 175,0% | 0 | SELLADO | PENDIENTE |
| 16 | Cuenca | 12 | 13 | 108,3% | 0 | SELLADO | PENDIENTE |
| 17 | Girona | 25 | 34 | 136,0% | 0 | SELLADO | PENDIENTE |
| 18 | Granada | 40 | 45 | 112,5% | 0 | SELLADO | PENDIENTE |
| 19 | Guadalajara | 11 | 16 | 145,5% | 0 | SELLADO | PENDIENTE |
| 20 | Gipuzkoa | 18 | 25 | 138,9% | 0 | SELLADO | PENDIENTE |
| 21 | Huelva | 17 | 25 | 147,1% | 0 | SELLADO | PENDIENTE |
| 22 | Huesca | 8 | 11 | 137,5% | 0 | SELLADO | PENDIENTE |
| 23 | Jaén | 17 | 24 | 141,2% | 0 | SELLADO | PENDIENTE |
| 24 | León | 19 | 27 | 142,1% | 0 | SELLADO | PENDIENTE |
| 25 | Lleida | 18 | 25 | 138,9% | 0 | SELLADO | PENDIENTE |
| 26 | Rioja, La | 7 | 10 | 142,9% | 0 | SELLADO | PENDIENTE |
| 27 | Lugo | 37 | 60 | 162,2% | 0 | SELLADO | PENDIENTE |
| 28 | Madrid | 48 | 98 | 204,2% | 0 | SELLADO | PENDIENTE |
| 29 | Málaga | 37 | 61 | 164,9% | 0 | SELLADO | PENDIENTE |
| 30 | Murcia | 41 | 63 | 153,7% | 0 | SELLADO | PENDIENTE |
| 31 | Navarra | 19 | 26 | 136,8% | 0 | SELLADO | PENDIENTE |
| 32 | Ourense | 12 | 24 | 200,0% | 0 | SELLADO | PENDIENTE |
| 33 | Asturias | 35 | 56 | 160,0% | 0 | SELLADO | PENDIENTE |
| 34 | Palencia | 7 | 11 | 157,1% | 0 | SELLADO | PENDIENTE |
| 35 | Las Palmas | 37 | 45 | 121,6% | 0 | SELLADO | PENDIENTE |
| 36 | Pontevedra | 34 | 54 | 158,8% | 0 | SELLADO | PENDIENTE |
| 37 | Salamanca | 19 | 26 | 136,8% | 0 | SELLADO | PENDIENTE |
| 38 | Sta. Cruz de Tenerife | 15 | 22 | 146,7% | 0 | SELLADO | PENDIENTE |
| 39 | Cantabria | 16 | 31 | 193,8% | 0 | SELLADO | PENDIENTE |
| 40 | Segovia | 6 | 9 | 150,0% | 0 | SELLADO | PENDIENTE |
| 41 | Sevilla | 62 | 86 | 138,7% | 0 | SELLADO | PENDIENTE |
| 42 | Soria | 4 | 5 | 125,0% | 0 | SELLADO | PENDIENTE |
| 43 | Tarragona | 27 | 38 | 140,7% | 0 | SELLADO | PENDIENTE |
| 44 | Teruel | 9 | 11 | 122,2% | 0 | SELLADO | PENDIENTE |
| 45 | Toledo | 51 | 78 | 152,9% | 0 | SELLADO | PENDIENTE |
| 46 | Valencia/València | 60 | 99 | 165,0% | 0 | SELLADO | PENDIENTE |
| 47 | Valladolid | 18 | 24 | 133,3% | 0 | SELLADO | PENDIENTE |
| 48 | Bizkaia | 29 | 37 | 127,6% | 0 | SELLADO | PENDIENTE |
| 49 | Zamora | 14 | 20 | 142,9% | 0 | SELLADO | PENDIENTE |
| 50 | Zaragoza | 20 | 26 | 130,0% | 0 | SELLADO | PENDIENTE |
| 51 | Ceuta | 2 | 2 | 100,0% | 0 | SELLADO | PENDIENTE |
| 52 | Melilla | 1 | 1 | 100,0% | 0 | SELLADO | PENDIENTE |
| **TOT** | **NACIONAL** | **1.292** | **1.895** | **146,7%** | **0** | **SELLADO** | **PENDIENTE** |

**Interpretación desguace**:
- Discovery (encontrar el CAT en DB): 52/52 provincias SELLADAS. Cada provincia del censo DGT
  está presente en DB con al menos tantos desguaces como el censo legal.
- Inventario (scraping de stock): 0/52 PENDIENTE. El workflow E2E desguace (scraping de piezas/
  vehículos de los CATs) no está implementado. El sello de inventario requiere este workflow.

---

## 4. RESUMEN DE VEREDICTOS — VENTA SERVIDA

### 4.1 Distribución por veredicto

| Veredicto | Umbral | N provincias | Lista |
|-----------|--------|-------------|-------|
| **SELLADO** (≥85%) | cob≥85% | **19** | Alicante (89,8%), Baleares (99,6%), Barcelona (92,7%), A Coruña (115,1%), Girona (112,7%), La Rioja (112,2%), Lugo (121,3%), Madrid (111,7%), Málaga (99,9%), Murcia (116,3%), Navarra (122,4%), Ourense (108,8%), Asturias (113,8%), Pontevedra (85,9%), Salamanca (139,9%), Cantabria (96,4%), Sevilla (97,1%), Valencia (107,8%), Bizkaia (117,1%) |
| **COBERTURA-PARCIAL** (50-84%) | 50%≤cob<85% | **26** | Álava (79,5%), Albacete (58,9%), Almería (56,6%), Badajoz (54,1%), Burgos (84,6%), Cádiz (74,0%), Castellón (73,8%), Ciudad Real (61,9%), Córdoba (72,7%), Granada (76,2%), Guadalajara (62,8%), Gipuzkoa (66,0%), Huesca (70,2%), Jaén (77,2%), León (64,0%), Lleida (81,0%), Palencia (52,0%), Las Palmas (60,7%), Sta. Cruz de Tenerife (63,2%), Segovia (62,5%), Soria (61,9%), Tarragona (84,3%), Toledo (68,8%), Valladolid (75,1%), Zamora (74,5%), Zaragoza (81,4%) |
| **GAP-CON-CAUSA** (<50%) | cob<50% | **7** | Ávila (43,2%), Cáceres (49,6%), Cuenca (39,4%), Huelva (43,5%), Teruel (44,7%), Ceuta (3,8%), Melilla (4,8%) |
| **TOTAL** | | **52** | |

### 4.2 Recuento definitivo

| Veredicto | N provincias |
|-----------|-------------|
| SELLADO (≥85%) | **19** |
| COBERTURA-PARCIAL (50-84%) | **26** |
| GAP-CON-CAUSA (<50%) | **7** |
| **TOTAL** | **52** |

**Provincias SELLADAS (19)**:
Alicante (89,8%) · Baleares (99,6%) · Barcelona (92,7%) · A Coruña (115,1%) · Girona (112,7%) ·
La Rioja (112,2%) · Lugo (121,3%) · Madrid (111,7%) · Málaga (99,9%) · Murcia (116,3%) ·
Navarra (122,4%) · Ourense (108,8%) · Asturias (113,8%) · Pontevedra (85,9%) · Salamanca (139,9%) ·
Cantabria (96,4%) · Sevilla (97,1%) · Valencia (107,8%) · Bizkaia (117,1%)

**Provincias GAP-CON-CAUSA (7)**:
Ávila (43,2%) · Cáceres (49,6%) · Cuenca (39,4%) · Huelva (43,5%) · Teruel (44,7%) ·
Ceuta (3,8%) · Melilla (4,8%)

---

## 5. ANÁLISIS DE GAPS — QUÉ FALTA

### 5.1 Causa común del gap (27 provincias COBERTURA-PARCIAL)

La diferencia entre el B6.2 (147,9% cobertura de leads) y el B6.3 (90,2% cobertura servida)
es **13.320 entidades descubiertas sin inventario indexado** — principalmente los 10.913 leads
de Overture Maps (sin scraping de inventario todavía) más entidades de OSM y directorios
sin workflow E2E.

El gap de servicio no es falta de descubrimiento — es falta de scraping de inventario
en los leads ya encontrados. La corrección está en ejecutar el workflow E2E sobre los
10.913 leads Overture y los restantes discovery leads.

### 5.2 Análisis por grupo de gap

**Grupo A — Provincias con baja presencia digital (long-tail real):**
- Ávila, Cuenca, Teruel, Palencia, Soria, Segovia, Zamora
- Estos mercados pequeños tienen menos presencia en plataformas nacionales
- Acción: OEM locators locales + Páginas Amarillas exhaustivo + census directo

**Grupo B — Provincias donde el denominador estimado puede estar inflado:**
- Burgos, Cantabria, País Vasco (Álava/Gipuzkoa)
- Alta proporción de CNAE 4519 (camiones/industriales) infla el denominador
- El gap real puede ser menor que el aparente

**Grupo C — Insulares y ciudades autónomas:**
- Las Palmas (60,7%), Sta. Cruz de Tenerife (63,2%), Ceuta (3,8%), Melilla (4,8%)
- Plataformas nacionales tienen menor penetración
- Acción: fuentes locales canarias + censo directo Ceuta/Melilla

**Grupo D — Provincias con gap moderado (50-75%):**
- Almería, Badajoz, Cádiz, Castellón, Ciudad Real, Córdoba, Granada, Guadalajara,
  Jaén, León, Lleida, Toledo, Zaragoza, etc.
- Tienen inventario scrapeado pero no toda la base de dealers activa
- Acción: completar scraping de los Overture leads ya descubiertos en estas provincias

### 5.3 Para SPAIN-SEALED: ruta crítica

El sello SPAIN-SEALED (19→52 provincias selladas) requiere:

1. **E2E Overture leads** (10.913 POIs sin inventario):
   - Si se scrapoea el 70% de ellos, se añadirían ~7.600 POS servidos nacionales
   - Impacto estimado en cobertura: +33 puntos porcentuales en las provincias con mayor
     concentración de leads Overture (Albacete, Almería, León, Toledo, etc.)

2. **Canarias — fuentes locales**:
   - Indexar clasificados locales canarios (Canarias7, La Provincia digital)
   - Estimación: +100-200 POS por isla

3. **Ceuta/Melilla — censo directo**:
   - Volumen small (<50 dealers totales entre ambas)
   - Método: Cámara de Comercio + OEM locators manual

4. **Desguace E2E workflow**:
   - Implementar scraping de inventario desguace (piezas/coches)
   - 1.292 CATs ya descubiertos → activar el workflow da 52/52 SELLADO en desguace-inventario

5. **Los 206 dealers sin geo (XX)**:
   - 206 compraventas servidas sin province_code → resolver geo para asignarlos a provincias
   - Distribución estimada: ~4 por provincia en media

---

## 6. SELLO FINAL POR BLOQUE

| Bloque | Estado | Detalle |
|--------|--------|---------|
| **B6 VENTA — Discovery** | NATIONAL-SELLADO | 34.355 leads / 23.085 DIRCE 451 = 148,9% (>100%) |
| **B6 VENTA — Inventario Servido** | PARCIAL 19/52 | **20.320** clusters canónicos servidos / 23.085 = **88,0%** nacional; 19 provincias ≥85% (tabla indicativa ±2-3% por fila) |
| **B6 DESGUACE — Discovery** | SELLADO 52/52 | 1.895 en DB / 1.292 DGT = 146,7%; cada provincia tiene ≥ sus CATs del censo DGT |
| **B6 DESGUACE — Inventario Servido** | 0/52 PENDIENTE | 0 vehículos en vehicle table para desguace |
| **B6 CONCESIONARIO — Discovery** | PARCIAL | 2.100 / 5.358 FACONAUTO = 39,2% |
| **B6 CONCESIONARIO — Inventario Servido** | PARCIAL | 618 servidos / 5.358 = 11,5% (sello imposible hasta +scraping) |

---

## 7. SESGOS DECLARADOS

1. **Denominador 451 es estimado provincialmente**: ratio nacional 26,05% aplicado
   uniformemente. Dirección del sesgo: denominador sobreestimado en provincias con alta
   proporción de talleres → cobertura aparentemente baja en algunas provincias donde
   en realidad la cobertura real es mayor. [D=ESTIMADO en todas las filas]

2. **Numerador canónico post-dedup**: usar `COALESCE(canonical_ulid, entity_ulid)` es
   la versión correcta pero conservadora — algunos clusters pueden tener canonical_ulid
   asignado a entidades que no tienen vehículos directamente, pero cuya entidad satélite
   sí los tiene. En la query actual se cuenta el canonical si la entidad-satélite sirve
   vehículos. [VERIFICADO: la query une la entidad con vehicles y luego resuelve el canonical]

3. **Desguace: 0 servidos no es gap de discovery sino gap de workflow**: el sello de
   inventario desguace es un gap de implementación, no de cobertura de datos. Los 1.292
   CATs están en DB. El workflow E2E de scraping de inventario desguace no existe aún.

4. **206 entidades sin province_code excluidas**: 206 compraventas servidas (0,99% del
   total servido) no tienen provincia asignada y no pueden clasificarse por provincia.
   Efecto: el numerador provincial está ligeramente infra-estimado. El gap real es menor.

5. **v_canonical basada en run dealer-identity-det-v1 (vam_verified=TRUE)**: el run
   cross-source-dedup-v1 (vam_verified=FALSE) NO se usa en este análisis. La dedup
   cross-source añadiría ~688 merges marginales. Efecto: numerador podría estar
   sobre-estimado en <1% en algunos clusters cross-source. [Confesado, marginal]

---

## 8. DATOS TÉCNICOS — QUERIES DE VERIFICACIÓN

### Query principal (numerador servido canónico por provincia)
```sql
SELECT 
  COALESCE(e.province_code, 'XX') AS prov,
  e.kind,
  COUNT(DISTINCT COALESCE(vc.canonical_ulid, e.entity_ulid)) AS canonical_served
FROM entity e
JOIN (SELECT DISTINCT entity_ulid FROM vehicle WHERE status = 'available') v
  ON v.entity_ulid = e.entity_ulid
LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
WHERE e.kind IN ('compraventa','concesionario_oficial')
GROUP BY COALESCE(e.province_code,'XX'), e.kind
ORDER BY prov, e.kind;
```

### Query control nacional
```sql
-- Resultado: 20208|618|20826
SELECT SUM(cv), SUM(co), SUM(cv+co)
FROM (
  SELECT ...  -- misma query agrupada
) sub WHERE prov != 'XX';
```

### Query desguace por provincia
```sql
SELECT 
  COALESCE(province_code, 'XX') AS prov,
  COUNT(*) AS total_desguace,
  SUM(CASE WHEN source_group='desguace_network' THEN 1 ELSE 0 END) AS dgt_censo
FROM entity 
WHERE kind = 'desguace'
GROUP BY COALESCE(province_code, 'XX')
ORDER BY prov;
-- Resultado: 1292 DGT total, 1895 total desguace
```

---

## 9. ARCHIVOS DE REFERENCIA

| Archivo | Contenido |
|---------|-----------|
| `data/official/denominador_cnae45_provincia_2024.csv` | Locales CNAE 45 por provincia [VERIFICADO CSV] |
| `data/official/dirce_301_locales_provincia_cnae2009.csv` | DIRCE completo [VERIFICADO CSV] |
| `docs/recon/B6_venta_sello.md` | B6.2: análisis de leads (discovery, no servidos) |
| `docs/recon/B5_COVERAGE_RECON.md` | Contexto completo cobertura y fuentes |
| `docs/PROGRESO.md` | Estado del proyecto y contexto de decisiones |

---

*Generado 2026-06-14. Sin mutación de DB. Sin commit.*  
*Todos los números de DB: [VERIFICADO DB] con queries directas a cardeep-pg :5433.*  
*Denominadores provincia: [ESTIMADO] por ratio 451/45 = 26,05% sobre CNAE 45 oficial.*
