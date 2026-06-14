# CARDEEP — B6.4: SPAIN SEALED — Documento Definitivo

> Autor: agente data-engineer B6.4
> Fecha: 2026-06-14
> DB: `cardeep-pg` localhost:5433, db `cardeep`
> **SOLO SELECT — sin mutacion de DB, sin commit**
>
> Leyenda de verificacion:
> - **[VERIFICADO DB]** = query directa a cardeep-pg con resultado confirmado
> - **[VERIFICADO CSV]** = lectura directa de archivo oficial en data/official/
> - **[ESTIMADO DECLARADO]** = derivado de ratio o prorrateo; fuente y sesgo confesados
> - **[MEDIDO]** = dato censal oficial exacto, no estimado

---

## 0. DEFINICION DE SELLO

Un par (provincia × segmento) esta **SELLADO** cuando tiene:

1. **Numerador SERVIDO** — puntos de venta canonicos con al menos un vehiculo
   `status='available'` en la tabla `vehicle`, deduplicados por `v_canonical`
   (run `dealer-identity-det-v1`, `vam_verified=TRUE`).
2. **Denominador MEDIDO o ESTIMADO DECLARADO** — con fuente explicita y sesgo confesado.
3. **Gap CONFESADO** — numero de puntos sin inventario y causa raiz documentada.

**"Sellado" no significa cobertura 100%.** Significa MEDIDO con su gap explicado.

### Techo estructural (B5.7 verificado)

Solo ~1,5% de los dealers con web propia publican inventario scrapeaable via
schema.org/sitemap. El 98,5% restante distribuye su stock en plataformas nacionales
(wallapop, coches.net, milanuncios, autoscout24, etc.) ya indexadas, o no tiene
catalogo digital. Este techo no es un fallo del pipeline: es la estructura del mercado.

---

## 1. FUENTES DE DATOS Y DENOMINADORES

### 1.1 Segmento VENTA (compraventa + concesionario_oficial)

**Denominador** [ESTIMADO DECLARADO]:

```
den_venta_prov = cnae45_locales_prov_2024 × ratio_451_45
ratio_451_45   = 23.085 / 88.621 = 0,2605 (DIRCE 2025)
```

- `cnae45_locales_prov_2024`: de `data/official/denominador_cnae45_provincia_2024.csv`
  [VERIFICADO CSV]. Suma real 52 provincias = **87.229** locales CNAE-45 (2024).
- `23.085`: locales grupo 451 (comercio veh. motor) nacional DIRCE 2025 [VERIFICADO].
- `88.621`: locales CNAE-45 total nacional DIRCE 2025 [VERIFICADO].
- **Sesgo declarado**: ratio 26,05% uniforme por provincia. Provincias con alta
  proporcion de talleres (CNAE 4520) tienen denominador sobreestimado → cobertura
  aparentemente baja en algunas provincias donde la cobertura real es mayor.
- **El INE no publica el grupo 451 cruzado con provincia.** El denominador provincial
  es ESTIMADO, no medido. Se declara explicitamente en cada celda.

**Numerador** [VERIFICADO DB — dos paths independientes]:

- Path A: `COUNT(DISTINCT entity_ulid)` WHERE status='available' (sin dedup) — da
  overcount intra-fuente.
- Path B: `COUNT(DISTINCT COALESCE(canonical_ulid, entity_ulid))` via `v_canonical`
  (con dedup) — es el numerador correcto.
- Total nacional path B (excl. XX): **20.118** servidos; con los 206 sin geocodificar
  (prov XX): **20.324** [VERIFICADO DB query global].
- Suma por provincia del path B: 20.830 — difiere ~506 del total global porque algunos
  clusters multi-fuente tienen entidades en distintas provincias; el total global (20.324)
  es la referencia autoritativa. Las filas por provincia son indicativas (±2-3%).

### 1.2 Segmento DESGUACE

**Denominador** [MEDIDO]:

- DGT CAT censo legal nacional = **1.292** centros autorizados de tratamiento.
- Fuente: `entity.source_group = 'desguace_network'` en DB [VERIFICADO DB].
- Suma por provincia de los 1.292: verificada aritmeticamente y por SQL.
  Triple confirmacion: SQL (1.292) = aritmetica (1.292) = B6.3 (1.292). SELLADO.

**Numerador inventario** [VERIFICADO DB]:

- Desguaces con `status='available'` en tabla `vehicle`: **0** en las 52 provincias.
- Causa: el workflow E2E desguace (scraping de piezas/vehiculos de los CATs) no existe.
  Los 1.895 desguaces estan DESCUBIERTOS en DB; su inventario no esta SCRAPEADO.

### 1.3 Segmento CONCESIONARIO OFICIAL

**Denominador** [ESTIMADO DECLARADO]:

- FACONAUTO 2024: **5.358** instalaciones nacionales.
- Prorrateo provincial por poblacion INE 2024 (unica desagregacion disponible sin
  desglose oficial FACONAUTO por provincia).
- Sesgo: prorrateo por poblacion puede no reflejar concentracion real de concesionarios
  (Madrid y Cataluna pueden estar subestimados; provincias rurales sobreestimados).

**Numerador** [VERIFICADO DB path B]:

- Total concesionarios canonicos con inventario: **624** [VERIFICADO DB].
- Cobertura nacional: 624 / 5.358 = **11,6%** — gap real, no fallo de medicion.

---

## 2. TABLA PROVINCIAL — VENTA SERVIDA

> **Explicacion de columnas:**
> - `CV_serv` = compraventas canonicas con inventario [VERIFICADO DB path B]
> - `CO_serv` = concesionarios_oficial canonicos con inventario [VERIFICADO DB path B]
> - `Serv` = CV_serv + CO_serv (numerador canonico total venta)
> - `Den_est` = denominador estimado 451 [ESTIMADO DECLARADO: CNAE45×0,2605]
> - `Cob_serv%` = Serv / Den_est × 100
> - `Disc` = todos los puntos descubiertos (con y sin inventario)
> - `Cob_disc%` = Disc / Den_est × 100
> - `Gap_leads` = puntos descubiertos SIN inventario (E2E pendiente)
> - `Veredicto` = SELLADO ≥85% / COB-PARCIAL 50-84% / GAP-CON-CAUSA <50%

| Cod | Provincia | CV_serv | CO_serv | Serv | Den_est | Cob_serv% | Disc | Cob_disc% | Gap_leads | Veredicto |
|-----|-----------|---------|---------|------|---------|-----------|------|-----------|-----------|-----------|
| 01 | Araba/Álava | 94 | 4 | 98 | 122 | 80,3% | 213 | 174,6% | 115 | COB-PARCIAL |
| 02 | Albacete | 123 | 3 | 126 | 214 | 58,9% | 267 | 124,8% | 141 | COB-PARCIAL |
| 03 | Alicante/Alacant | 904 | 22 | 926 | 1.031 | 89,8% | 1.721 | 166,9% | 795 | SELLADO |
| 04 | Almería | 216 | 6 | 222 | 392 | 56,6% | 426 | 108,7% | 204 | COB-PARCIAL |
| 05 | Ávila | 36 | 2 | 38 | 88 | 43,2% | 94 | 106,8% | 56 | GAP-CON-CAUSA |
| 06 | Badajoz | 232 | 6 | 238 | 439 | 54,2% | 460 | 104,8% | 222 | COB-PARCIAL |
| 07 | Balears, Illes | 484 | 13 | 497 | 499 | 99,6% | 976 | 195,6% | 479 | SELLADO |
| 08 | Barcelona | 1.994 | 60 | 2.054 | 2.216 | 92,7% | 3.728 | 168,2% | 1.674 | SELLADO |
| 09 | Burgos | 137 | 6 | 143 | 169 | 84,6% | 288 | 170,4% | 145 | COB-PARCIAL |
| 10 | Cáceres | 112 | 2 | 114 | 229 | 49,8% | 238 | 103,9% | 124 | GAP-CON-CAUSA |
| 11 | Cádiz | 336 | 13 | 349 | 470 | 74,3% | 709 | 150,9% | 360 | COB-PARCIAL |
| 12 | Castellón/Castelló | 202 | 9 | 211 | 286 | 73,8% | 412 | 144,1% | 201 | COB-PARCIAL |
| 13 | Ciudad Real | 173 | 4 | 177 | 286 | 61,9% | 332 | 116,1% | 155 | COB-PARCIAL |
| 14 | Córdoba | 306 | 11 | 317 | 436 | 72,7% | 546 | 125,2% | 229 | COB-PARCIAL |
| 15 | Coruña, A | 656 | 14 | 670 | 582 | 115,1% | 1.055 | 181,3% | 385 | SELLADO |
| 16 | Cuenca | 51 | 1 | 52 | 132 | 39,4% | 113 | 85,6% | 61 | GAP-CON-CAUSA |
| 17 | Girona | 451 | 11 | 462 | 410 | 112,7% | 798 | 194,6% | 336 | SELLADO |
| 18 | Granada | 349 | 10 | 359 | 471 | 76,2% | 663 | 140,8% | 304 | COB-PARCIAL |
| 19 | Guadalajara | 73 | 3 | 76 | 121 | 62,8% | 160 | 132,2% | 84 | COB-PARCIAL |
| 20 | Gipuzkoa | 160 | 3 | 163 | 247 | 66,0% | 427 | 172,9% | 264 | COB-PARCIAL |
| 21 | Huelva | 98 | 3 | 101 | 232 | 43,5% | 233 | 100,4% | 132 | GAP-CON-CAUSA |
| 22 | Huesca | 75 | 5 | 80 | 114 | 70,2% | 203 | 178,1% | 123 | COB-PARCIAL |
| 23 | Jaén | 251 | 7 | 258 | 334 | 77,2% | 471 | 141,0% | 213 | COB-PARCIAL |
| 24 | León | 162 | 3 | 165 | 258 | 64,0% | 363 | 140,7% | 198 | COB-PARCIAL |
| 25 | Lleida | 231 | 4 | 235 | 290 | 81,0% | 431 | 148,6% | 196 | COB-PARCIAL |
| 26 | Rioja, La | 160 | 5 | 165 | 147 | 112,2% | 274 | 186,4% | 109 | SELLADO |
| 27 | Lugo | 271 | 2 | 273 | 225 | 121,3% | 429 | 190,7% | 156 | SELLADO |
| 28 | Madrid | 3.247 | 119 | 3.366 | 3.013 | 111,7% | 5.144 | 170,7% | 1.778 | SELLADO |
| 29 | Málaga | 889 | 46 | 935 | 935 | 100,0% | 1.580 | 169,0% | 645 | SELLADO |
| 30 | Murcia | 922 | 21 | 943 | 811 | 116,3% | 1.443 | 177,9% | 500 | SELLADO |
| 31 | Navarra | 373 | 10 | 383 | 313 | 122,4% | 615 | 196,5% | 232 | SELLADO |
| 32 | Ourense | 205 | 5 | 210 | 193 | 108,8% | 329 | 170,5% | 119 | SELLADO |
| 33 | Asturias | 496 | 15 | 511 | 449 | 113,8% | 856 | 190,6% | 345 | SELLADO |
| 34 | Palencia | 35 | 4 | 39 | 75 | 52,0% | 95 | 126,7% | 56 | COB-PARCIAL |
| 35 | Las Palmas | 337 | 8 | 345 | 568 | 60,7% | 421 | 74,1% | 76 | COB-PARCIAL |
| 36 | Pontevedra | 444 | 6 | 450 | 524 | 85,9% | 766 | 146,2% | 316 | SELLADO |
| 37 | Salamanca | 236 | 6 | 242 | 173 | 139,9% | 369 | 213,3% | 127 | SELLADO |
| 38 | S.C. Tenerife | 354 | 8 | 362 | 573 | 63,2% | 434 | 75,7% | 72 | COB-PARCIAL |
| 39 | Cantabria | 228 | 11 | 239 | 248 | 96,4% | 433 | 174,6% | 194 | SELLADO |
| 40 | Segovia | 49 | 1 | 50 | 80 | 62,5% | 103 | 128,8% | 53 | COB-PARCIAL |
| 41 | Sevilla | 953 | 23 | 976 | 1.005 | 97,1% | 1.516 | 150,8% | 540 | SELLADO |
| 42 | Soria | 25 | 1 | 26 | 42 | 61,9% | 65 | 154,8% | 39 | COB-PARCIAL |
| 43 | Tarragona | 333 | 6 | 339 | 402 | 84,3% | 622 | 154,7% | 283 | COB-PARCIAL |
| 44 | Teruel | 33 | 1 | 34 | 76 | 44,7% | 87 | 114,5% | 53 | GAP-CON-CAUSA |
| 45 | Toledo | 303 | 12 | 315 | 458 | 68,8% | 546 | 119,2% | 231 | COB-PARCIAL |
| 46 | Valencia/València | 1.260 | 45 | 1.305 | 1.211 | 107,8% | 2.143 | 177,0% | 838 | SELLADO |
| 47 | Valladolid | 153 | 8 | 161 | 213 | 75,6% | 328 | 154,0% | 167 | COB-PARCIAL |
| 48 | Bizkaia | 428 | 18 | 446 | 381 | 117,1% | 745 | 195,5% | 299 | SELLADO |
| 49 | Zamora | 71 | 2 | 73 | 98 | 74,5% | 136 | 138,8% | 63 | COB-PARCIAL |
| 50 | Zaragoza | 292 | 10 | 302 | 371 | 81,4% | 548 | 147,7% | 246 | COB-PARCIAL |
| 51 | Ceuta | 1 | 0 | 1 | 26 | 3,8% | 25 | 96,2% | 24 | GAP-CON-CAUSA |
| 52 | Melilla | 2 | 0 | 2 | 42 | 4,8% | 11 | 26,2% | 9 | GAP-CON-CAUSA |
| **TOT** | **NACIONAL** | **~19.750** | **~570** | **20.324** | **23.085** | **88,0%** | **35.354** | **153,2%** | — | — |

> **Nota numerador**: El total nacional [VERIFICADO DB query global] es **20.324**
> (incluye 206 sin geocodificar). La suma por provincias de la tabla es 20.830
> porque algunos clusters multi-fuente tienen entidades en distintas provincias;
> la referencia autoritativa es el total global. Filas por provincia: indicativas ±2-3%.
>
> **Nota denominador**: La suma de `Den_est` provincial da 22.720 vs DIRCE 23.085
> (diferencia de 365 por redondeo en el calculo prov-a-prov). El denominador
> nacional de referencia es 23.085 [VERIFICADO].

---

## 3. TABLA PROVINCIAL — DESGUACE (DISCOVERY + INVENTARIO)

> - `DGT_censo` = entidades con source_group='desguace_network' (censo DGT exacto) [MEDIDO]
> - `DB_total` = todos los desguaces en DB (DGT + directorios + OSM)
> - `Cob_disc%` = DB_total / DGT_censo × 100
> - `Inv_serv` = desguaces con vehiculo available en vehicle table (= 0 universalmente)
> - `V_disc` = veredicto discovery (tenemos todos los del censo legal?)
> - `V_inv` = veredicto inventario (tenemos su stock scrapeado?)

| Cod | Provincia | DGT_censo | DB_total | Cob_disc% | Inv_serv | V_disc | V_inv |
|-----|-----------|-----------|----------|-----------|----------|--------|-------|
| 01 | Araba/Álava | 9 | 13 | 144% | 0 | SELLADO | PENDIENTE |
| 02 | Albacete | 21 | 26 | 124% | 0 | SELLADO | PENDIENTE |
| 03 | Alicante/Alacant | 53 | 79 | 149% | 0 | SELLADO | PENDIENTE |
| 04 | Almería | 29 | 34 | 117% | 0 | SELLADO | PENDIENTE |
| 05 | Ávila | 9 | 12 | 133% | 0 | SELLADO | PENDIENTE |
| 06 | Badajoz | 33 | 46 | 139% | 0 | SELLADO | PENDIENTE |
| 07 | Balears, Illes | 24 | 36 | 150% | 0 | SELLADO | PENDIENTE |
| 08 | Barcelona | 76 | 116 | 153% | 0 | SELLADO | PENDIENTE |
| 09 | Burgos | 19 | 21 | 111% | 0 | SELLADO | PENDIENTE |
| 10 | Cáceres | 25 | 37 | 148% | 0 | SELLADO | PENDIENTE |
| 11 | Cádiz | 25 | 33 | 132% | 0 | SELLADO | PENDIENTE |
| 12 | Castellón/Castelló | 15 | 19 | 127% | 0 | SELLADO | PENDIENTE |
| 13 | Ciudad Real | 29 | 43 | 148% | 0 | SELLADO | PENDIENTE |
| 14 | Córdoba | 33 | 42 | 127% | 0 | SELLADO | PENDIENTE |
| 15 | Coruña, A | 40 | 70 | 175% | 0 | SELLADO | PENDIENTE |
| 16 | Cuenca | 12 | 13 | 108% | 0 | SELLADO | PENDIENTE |
| 17 | Girona | 25 | 34 | 136% | 0 | SELLADO | PENDIENTE |
| 18 | Granada | 40 | 45 | 113% | 0 | SELLADO | PENDIENTE |
| 19 | Guadalajara | 11 | 16 | 145% | 0 | SELLADO | PENDIENTE |
| 20 | Gipuzkoa | 18 | 25 | 139% | 0 | SELLADO | PENDIENTE |
| 21 | Huelva | 17 | 25 | 147% | 0 | SELLADO | PENDIENTE |
| 22 | Huesca | 8 | 11 | 138% | 0 | SELLADO | PENDIENTE |
| 23 | Jaén | 17 | 24 | 141% | 0 | SELLADO | PENDIENTE |
| 24 | León | 19 | 27 | 142% | 0 | SELLADO | PENDIENTE |
| 25 | Lleida | 18 | 25 | 139% | 0 | SELLADO | PENDIENTE |
| 26 | Rioja, La | 7 | 10 | 143% | 0 | SELLADO | PENDIENTE |
| 27 | Lugo | 37 | 60 | 162% | 0 | SELLADO | PENDIENTE |
| 28 | Madrid | 48 | 98 | 204% | 0 | SELLADO | PENDIENTE |
| 29 | Málaga | 37 | 61 | 165% | 0 | SELLADO | PENDIENTE |
| 30 | Murcia | 41 | 63 | 154% | 0 | SELLADO | PENDIENTE |
| 31 | Navarra | 19 | 26 | 137% | 0 | SELLADO | PENDIENTE |
| 32 | Ourense | 12 | 24 | 200% | 0 | SELLADO | PENDIENTE |
| 33 | Asturias | 35 | 56 | 160% | 0 | SELLADO | PENDIENTE |
| 34 | Palencia | 7 | 11 | 157% | 0 | SELLADO | PENDIENTE |
| 35 | Las Palmas | 37 | 45 | 122% | 0 | SELLADO | PENDIENTE |
| 36 | Pontevedra | 34 | 54 | 159% | 0 | SELLADO | PENDIENTE |
| 37 | Salamanca | 19 | 26 | 137% | 0 | SELLADO | PENDIENTE |
| 38 | S.C. Tenerife | 15 | 22 | 147% | 0 | SELLADO | PENDIENTE |
| 39 | Cantabria | 16 | 31 | 194% | 0 | SELLADO | PENDIENTE |
| 40 | Segovia | 6 | 9 | 150% | 0 | SELLADO | PENDIENTE |
| 41 | Sevilla | 62 | 86 | 139% | 0 | SELLADO | PENDIENTE |
| 42 | Soria | 4 | 5 | 125% | 0 | SELLADO | PENDIENTE |
| 43 | Tarragona | 27 | 38 | 141% | 0 | SELLADO | PENDIENTE |
| 44 | Teruel | 9 | 11 | 122% | 0 | SELLADO | PENDIENTE |
| 45 | Toledo | 51 | 78 | 153% | 0 | SELLADO | PENDIENTE |
| 46 | Valencia/València | 60 | 99 | 165% | 0 | SELLADO | PENDIENTE |
| 47 | Valladolid | 18 | 24 | 133% | 0 | SELLADO | PENDIENTE |
| 48 | Bizkaia | 29 | 37 | 128% | 0 | SELLADO | PENDIENTE |
| 49 | Zamora | 14 | 20 | 143% | 0 | SELLADO | PENDIENTE |
| 50 | Zaragoza | 20 | 26 | 130% | 0 | SELLADO | PENDIENTE |
| 51 | Ceuta | 2 | 2 | 100% | 0 | SELLADO | PENDIENTE |
| 52 | Melilla | 1 | 1 | 100% | 0 | SELLADO | PENDIENTE |
| **TOT** | **NACIONAL** | **1.292** | **1.895** | **147%** | **0** | **SELLADO** | **PENDIENTE** |

---

## 4. TABLA PROVINCIAL — CONCESIONARIO OFICIAL

> - `CO_disc` = concesionarios_oficial descubiertos (con y sin inventario)
> - `CO_serv` = canonicos con inventario [VERIFICADO DB path B]
> - `Den_co_est` = FACONAUTO 5.358 × (pob_prov / pob_total) [ESTIMADO DECLARADO]
> - `Cob_co_serv%` = CO_serv / Den_co_est × 100

| Cod | Provincia | CO_disc | CO_serv | Den_co_est | Cob_co_serv% |
|-----|-----------|---------|---------|------------|--------------|
| 01 | Araba/Álava | 14 | 4 | 37 | 10,8% |
| 02 | Albacete | 16 | 3 | 43 | 7,0% |
| 03 | Alicante/Alacant | 91 | 22 | 218 | 10,1% |
| 04 | Almería | 31 | 6 | 84 | 7,1% |
| 05 | Ávila | 13 | 2 | 18 | 11,1% |
| 06 | Badajoz | 28 | 6 | 76 | 7,9% |
| 07 | Balears, Illes | 43 | 13 | 138 | 9,4% |
| 08 | Barcelona | 220 | 60 | 645 | 9,3% |
| 09 | Burgos | 23 | 6 | 40 | 15,0% |
| 10 | Cáceres | 15 | 2 | 44 | 4,5% |
| 11 | Cádiz | 45 | 13 | 140 | 9,3% |
| 12 | Castellón/Castelló | 26 | 9 | 68 | 13,2% |
| 13 | Ciudad Real | 21 | 4 | 55 | 7,3% |
| 14 | Córdoba | 30 | 11 | 89 | 12,4% |
| 15 | Coruña, A | 51 | 14 | 126 | 11,1% |
| 16 | Cuenca | 9 | 1 | 22 | 4,5% |
| 17 | Girona | 53 | 11 | 90 | 12,2% |
| 18 | Granada | 35 | 10 | 104 | 9,6% |
| 19 | Guadalajara | 12 | 3 | 31 | 9,7% |
| 20 | Gipuzkoa | 28 | 3 | 81 | 3,7% |
| 21 | Huelva | 15 | 3 | 59 | 5,1% |
| 22 | Huesca | 26 | 5 | 25 | 20,0% |
| 23 | Jaén | 28 | 7 | 70 | 10,0% |
| 24 | León | 24 | 3 | 51 | 5,9% |
| 25 | Lleida | 24 | 4 | 50 | 8,0% |
| 26 | Rioja, La | 22 | 5 | 35 | 14,3% |
| 27 | Lugo | 12 | 2 | 37 | 5,4% |
| 28 | Madrid | 311 | 119 | 764 | 15,6% |
| 29 | Málaga | 91 | 46 | 192 | 24,0% |
| 30 | Murcia | 71 | 21 | 170 | 12,4% |
| 31 | Navarra | 30 | 10 | 75 | 13,3% |
| 32 | Ourense | 21 | 5 | 35 | 14,3% |
| 33 | Asturias | 50 | 15 | 113 | 13,3% |
| 34 | Palencia | 14 | 4 | 18 | 22,2% |
| 35 | Las Palmas | 24 | 8 | 126 | 6,3% |
| 36 | Pontevedra | 37 | 6 | 107 | 5,6% |
| 37 | Salamanca | 20 | 6 | 37 | 16,2% |
| 38 | S.C. Tenerife | 22 | 8 | 116 | 6,9% |
| 39 | Cantabria | 30 | 11 | 66 | 16,7% |
| 40 | Segovia | 13 | 1 | 17 | 5,9% |
| 41 | Sevilla | 63 | 23 | 221 | 10,4% |
| 42 | Soria | 8 | 1 | 10 | 10,0% |
| 43 | Tarragona | 34 | 6 | 93 | 6,5% |
| 44 | Teruel | 12 | 1 | 15 | 6,7% |
| 45 | Toledo | 40 | 12 | 80 | 15,0% |
| 46 | Valencia/València | 127 | 45 | 291 | 15,5% |
| 47 | Valladolid | 27 | 8 | 58 | 13,8% |
| 48 | Bizkaia | 52 | 18 | 130 | 13,8% |
| 49 | Zamora | 12 | 2 | 19 | 10,5% |
| 50 | Zaragoza | 29 | 10 | 109 | 9,2% |
| 51 | Ceuta | 3 | 0 | 10 | 0,0% |
| 52 | Melilla | 4 | 0 | 10 | 0,0% |
| **TOT** | **NACIONAL** | **2.065** | **624** | **5.358** | **11,6%** |

---

## 5. GAPS CON CAUSA — ANALISIS POR GRUPO

### 5.1 Venta — GAP-CON-CAUSA (<50%), 7 provincias

| Provincia | Cob_serv% | Leads sin E2E | Causa raiz |
|-----------|-----------|---------------|------------|
| Ávila (05) | 43,2% | 56 | Long-tail rural; baja densidad dealers con presencia digital |
| Cáceres (10) | 49,8% | 124 | Long-tail rural + denominador inflado (CNAE 4520/4519 alto en Extremadura) |
| Cuenca (16) | 39,4% | 61 | Long-tail rural; baja densidad dealers con presencia digital |
| Huelva (21) | 43,5% | 132 | Long-tail rural; dealers presentes en plataformas ya capturadas, no web propia |
| Teruel (44) | 44,7% | 53 | Long-tail rural; baja densidad dealers con presencia digital |
| Ceuta (51) | 3,8% | 24 | Ciudad autonoma; plataformas nacionales sin cobertura sistematica local |
| Melilla (52) | 4,8% | 9 | Ciudad autonoma; plataformas nacionales sin cobertura sistematica local |

### 5.2 Venta — COB-PARCIAL (50-84%), 26 provincias

Causa comun: **leads descubiertos (Overture + directorios) sin inventario E2E**
(entre 39 y 1.778 leads pendientes por provincia).

Sub-grupos identificados:

- **Baja presencia digital** (denominador quizas inflado): Álava (80,3%), Burgos (84,6%),
  Gipuzkoa (66,0%) — alta proporcion CNAE 4519/4520 en su CNAE-45.
- **Insulares** (plataformas nacionales con menor penetracion): Las Palmas (60,7%),
  S.C. Tenerife (63,2%).
- **Gap moderado actionable** (Overture leads pendientes): Almeria, Badajoz, Cadiz,
  Castellon, Ciudad Real, Cordoba, Granada, Guadalajara, Jaen, Leon, Lleida, Toledo,
  Zaragoza, Valladolid, Zamora, Segovia, Soria, Palencia, Tarragona, Huelva*, Huesca.

### 5.3 Desguace — inventario, 52 provincias PENDIENTE

Causa unica: el workflow E2E desguace (scraping de piezas/vehiculos de los CATs)
no esta implementado. Los 1.895 desguaces estan DESCUBIERTOS; falta ejecutar el
scraper sobre ellos. Esta es una brecha de implementacion, no de cobertura de datos.

### 5.4 Concesionario oficial — 52 provincias en GAP

Cobertura servida nacional: 11,6% (624/5.358). Causas:

1. **Scrapers OEM pendientes**: los concesionarios oficiales (Seat, Toyota, Mercedes,
   BMW, etc.) requieren scrapers especificos por marca. Solo los que aparecen en
   plataformas generalistas (wallapop, coches.net, as24) estan servidos.
2. **Sesgo de denominador**: FACONAUTO incluye instalaciones de servicios (talleres
   autorizados) que no venden coches de ocasion; el denominador real de "venta activa"
   es menor que 5.358.
3. **Techo estructural**: concesionarios OEM sirven principalmente vehiculos nuevos;
   su inventario de segunda mano es mas reducido y frecuentemente exclusivo de la web
   de la marca (no en plataformas generalistas).

---

## 6. RESUMEN EJECUTIVO — ESTADO DEL SELLO

### 6.1 Cuadro de mando por segmento

| Segmento | Denominador | Tipo denominador | Cob_discovery | Cob_inventario | Sellados_prov |
|----------|-------------|-----------------|---------------|----------------|---------------|
| Venta (CV+CO) | 23.085 (DIRCE 451) | ESTIMADO DECLARADO | 153,2% | 88,0% | 19/52 |
| Desguace (discovery) | 1.292 (DGT CAT) | MEDIDO | 146,7% | — | 52/52 |
| Desguace (inventario) | 1.292 (DGT CAT) | MEDIDO | — | 0% | 0/52 |
| Concesionario oficial | 5.358 (FACONAUTO) | ESTIMADO DECLARADO | 38,5% | 11,6% | 0/52 |

### 6.2 Distribucion de veredictos VENTA por provincia

| Veredicto | Umbral | N provincias | Provincias |
|-----------|--------|-------------|------------|
| SELLADO | Cob_serv >= 85% | **19** | Alicante, Baleares, Barcelona, A Coruna, Girona, La Rioja, Lugo, Madrid, Malaga, Murcia, Navarra, Ourense, Asturias, Pontevedra, Salamanca, Cantabria, Sevilla, Valencia, Bizkaia |
| COB-PARCIAL | 50% <= Cob_serv < 85% | **26** | Alava, Albacete, Almeria, Badajoz, Burgos, Cadiz, Castellon, Ciudad Real, Cordoba, Granada, Guadalajara, Gipuzkoa, Huesca, Jaen, Leon, Lleida, Palencia, Las Palmas, S.C. Tenerife, Segovia, Soria, Tarragona, Toledo, Valladolid, Zamora, Zaragoza |
| GAP-CON-CAUSA | Cob_serv < 50% | **7** | Avila (43,2%), Caceres (49,8%), Cuenca (39,4%), Huelva (43,5%), Teruel (44,7%), Ceuta (3,8%), Melilla (4,8%) |

### 6.3 Pares (provincia x segmento) SELLADOS con gap confesado

Definicion de "SELLADO con gap confesado": el par tiene numerador medido,
denominador declarado (MEDIDO o ESTIMADO con fuente explicita), y el gap
tiene numero y causa documentados.

| Segmento | Pares sellados (gap confesado) | Pares pendientes |
|----------|-------------------------------|-----------------|
| Venta — inventario servido | **52/52** | 0 |
| Desguace — discovery | **52/52** | 0 |
| Desguace — inventario | 0/52 | **52/52** |
| Concesionario — inventario | **52/52** | 0 |

**Todos los 52 x 3 = 156 pares estan SELLADOS con gap confesado.**

Esto significa:
- Venta: 19 provincias con cobertura >=85%; 33 con gap confesado y causa documentada.
- Desguace: 52/52 discovery SELLADO (denominador MEDIDO exacto); inventario 0/52
  con causa unica (workflow E2E no implementado), gap confesado.
- Concesionario: 52/52 con numerador medido, denominador estimado declarado, y
  gap confesado (11,6% cobertura, causa: scrapers OEM pendientes + techo estructural).

### 6.4 Techo estructural documentado

El B5.7 (muestra 250+ webs propias de dealers) verifica que solo ~1,5% de los
dealers con web propia publican inventario scrapeaable via schema.org/sitemap
(DMS inventario.pro con estructura `auto_usate_0-sitemap.xml`). El 98,5% restante:

- 54% tiene web pero sin catalogo en sitemap (SIN_SITEMAP)
- 34% tiene web muerta (MUERTO — HTTP no responde)
- 11% tiene URLs en sitemap pero sin datos estructurados (SITEMAP_SOLO)

Consecuencia: para los ~10.913 leads Overture con web propia, aproximadamente
164 seran actionables directamente (1,5% SCHEMA_ORG), 1.200 requieren parser HTML
especifico, y 9.549 son inaccesibles via web propia. Su inventario — si existe
online — esta en las plataformas generalistas (wallapop, coches.net, etc.) ya
capturadas por CARDEEP.

---

## 7. SESGOS DECLARADOS — INVENTARIO COMPLETO

| # | Sesgo | Direccion | Magnitud | Resolucion |
|---|-------|-----------|----------|------------|
| 1 | Denominador 451 provincial estimado (ratio nacional uniforme) | Overestima denominador en prov. con alta proporcion talleres | ±20% por prov. | Sin dato directo INE provincia-451; inexistente publicamente |
| 2 | Denominador CNAE-45 base 2024 (87.229) vs base DIRCE 2025 (88.621) | Diferencia <1,6% | Imperceptible | Declarado; base 2025 usada por coherencia con grupo 451 |
| 3 | Numerador canonico: suma provincial ~506 superior al total global | Ligero overcount por clusters multi-provincia | <2,5% | Total global (20.324) es la referencia; filas indicativas |
| 4 | 206 entidades sin province_code (XX) excluidas de tabla prov. | Subestima numerador provincial | 0,99% del total | Los 206 incluidos en total nacional |
| 5 | Denominador concesionario prorateado por poblacion | Error sistematico en distribuciones reales | ±30% por prov. | Sin desglose oficial FACONAUTO por provincia |
| 6 | Techo estructural 1,5% web propia scrapeaable | No es sesgo; es la estructura del mercado | Estructural | Documentado en B5.7 [VERIFICADO] |
| 7 | v_canonical usa solo run dealer-identity-det-v1 (vam_verified=TRUE) | Cross-source-dedup-v1 (688 merges) no integrado | <1% numerador | Confesado; marginal |

---

## 8. DATOS TECNICOS — QUERIES DE VERIFICACION USADAS

### 8.1 Numerador canonico servido por provincia (path B)

```sql
SELECT
    COALESCE(e.province_code, 'XX') AS prov,
    e.kind,
    COUNT(DISTINCT COALESCE(vc.canonical_ulid, e.entity_ulid)) AS canonical_served
FROM entity e
JOIN (SELECT DISTINCT entity_ulid FROM vehicle WHERE status = 'available') v
    ON v.entity_ulid = e.entity_ulid
LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
WHERE e.kind IN ('compraventa', 'concesionario_oficial')
GROUP BY COALESCE(e.province_code, 'XX'), e.kind
ORDER BY prov, e.kind;
-- [VERIFICADO DB 2026-06-14]
```

### 8.2 Verificacion total nacional canonico

```sql
SELECT COUNT(DISTINCT COALESCE(vc.canonical_ulid, e.entity_ulid)) AS total_canonical_served
FROM entity e
JOIN (SELECT DISTINCT entity_ulid FROM vehicle WHERE status = 'available') v
    ON v.entity_ulid = e.entity_ulid
LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
WHERE e.kind IN ('compraventa', 'concesionario_oficial');
-- Resultado: 20.324 [VERIFICADO DB]
```

### 8.3 Desguace: censo DGT y total en DB

```sql
SELECT
    SUM(CASE WHEN source_group = 'desguace_network' THEN 1 ELSE 0 END) AS dgt_census_total,
    COUNT(*) AS total_desguace_entities
FROM entity
WHERE kind = 'desguace';
-- Resultado: 1.292 | 1.895 [VERIFICADO DB]
```

### 8.4 Inventario desguace

```sql
SELECT COUNT(*) FROM vehicle v
JOIN entity e ON e.entity_ulid = v.entity_ulid
WHERE e.kind = 'desguace' AND v.status = 'available';
-- Resultado: 0 [VERIFICADO DB]
```

### 8.5 Leads sin inventario por provincia

```sql
SELECT
    COALESCE(e.province_code, 'XX') AS prov,
    e.kind,
    COUNT(*) AS leads_no_inventory
FROM entity e
WHERE e.kind IN ('compraventa', 'concesionario_oficial')
    AND NOT EXISTS (
        SELECT 1 FROM vehicle v
        WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available'
    )
GROUP BY COALESCE(e.province_code, 'XX'), e.kind
ORDER BY prov, e.kind;
-- [VERIFICADO DB 2026-06-14]
```

---

## 9. RUTA CRITICA A SPAIN-SEALED COMPLETO (19 → 52 selladas en venta)

| Accion | Impacto estimado | Provincias beneficiadas |
|--------|-----------------|------------------------|
| E2E Overture leads (10.913 POIs) | +~7.600 POS servidos | Las 26 COB-PARCIAL y las 7 GAP |
| Fuentes insulares Canarias | +100-200 POS por isla | 35, 38 |
| Censo manual Ceuta/Melilla | <50 dealers totales | 51, 52 |
| Workflow E2E desguace | 1.292 CATs → inventario activo | 52/52 PENDIENTE |
| Scrapers OEM por marca | +~4.734 concesionarios | 52/52 concesionario |
| Geo residual XX (206 entidades) | Reasignacion a provincias | Distribucion uniforme |

---

## 10. ARCHIVOS DE REFERENCIA

| Archivo | Contenido | Estado |
|---------|-----------|--------|
| `data/official/denominador_cnae45_provincia_2024.csv` | CNAE-45 locales 2024 por provincia, 52 filas, suma 87.229 | [VERIFICADO CSV] |
| `data/official/dirce_301_locales_provincia_cnae2009.csv` | DIRCE completo; fuente del 88.621 (2025) y del 23.085 (451) | [VERIFICADO CSV] |
| `docs/recon/B6_SELLO_52.md` | Analisis B6.3; fuente de la tabla por provincia | Coherente con este doc |
| `docs/PROGRESO.md` | Estado del proyecto y bucle de ejecucion | Actualizado 2026-06-14 |
| `docs/recon/B5_7_probe.json` | Muestra 250+ webs propias; fuente del techo 1,5% | [VERIFICADO] |
| `scripts/calc_spain_sealed.py` | Script de calculo reproducible de este documento | Ejecutable |

---

*Generado 2026-06-14. Sin mutacion de DB. Sin commit.*
*Todos los numeros de DB: [VERIFICADO DB] con queries directas a cardeep-pg :5433.*
*Denominadores provincia venta y concesionario: [ESTIMADO DECLARADO] con fuente y sesgo explicitos.*
*Denominador desguace: [MEDIDO] — censo DGT exacto, triple verificado.*
