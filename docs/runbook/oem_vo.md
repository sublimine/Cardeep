# RUNBOOK — OEM-VO GROUP (`kind='oem_vo_portal'`)

> **Regla dura de este runbook:** entra SOLO lo validado y funcional. Cada portal
> listado tiene (a) una fila `verification_verdict` persistida con `verdict='TRUSTWORTHY'`
> (cito su `id`) **y** (b) un conector commiteado que carga y corre (verificado:
> `python -m … --help` OK para los 13 módulos). Lo aspiracional / amurallado va al final,
> en **"NO validado (fuera del runbook)"**.
>
> **Fuente de verdad de los números:** la DB viva
> `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`, contada el **2026-06-13**
> por join directo `platform_listing → vehicle`, agrupando por la entidad portal
> (`entity.kind='oem_vo_portal'`). Cada cifra se cruzó contra
> `verification_verdict` (subject_type `platform_slice`) y coincide al dígito con
> `primary_value` del veredicto más reciente.
>
> **ENV:** `python = C:/Users/elias/AppData/Local/Programs/Python/Python311/python`
> · DB arriba · todos los conectores se invocan como
> `python -m pipeline.platform.<module>` desde `C:\Users\elias\projects\cardeep`.

---

## 0. Qué es este grupo y CÓMO está separado del resto

Un **portal OEM-VO** es la TERCERA especie de fuente, distinta de los marketplaces
(`marketplace_motor` / `marketplace_generalist`): **un fabricante-dueño publicando el
stock certificado de ocasión de su PROPIA red de concesionarios oficiales**. No es
marketplace, no es clasificados generalistas, no hay vendedores particulares.

**Ejes de clasificación** (mismos tres en los 14 portales; solo varían `defense_tier` y
`family`). `[VERIFIED]` contra la DB:

| Eje | Valor | Origen |
|---|---|---|
| `kind` (ontología, migración 0005) | `oem_vo_portal` | `entity.kind` de la entidad PORTAL |
| `source_group` (migración 0016) | `oem_vo_portal` | `entity.source_group` |
| `role` | `platform` | `entity.role` |
| `is_tier1` | depende (ver tabla) | `entity.is_tier1` |

### Cómo se separa este grupo — la regla de propiedad (modelo de doble membresía)

- **Los coches son de los concesionarios, no del portal.** Cada `vehicle.entity_ulid`
  apunta a su concesionario oficial vendedor (`kind='compraventa'`). El PORTAL en sí
  **tiene 0 coches directos**: no es dueño de ningún `vehicle`.
- **El coche EN el portal es una arista** `platform_listing`
  (`platform_entity_ulid` = portal ↔ `vehicle_ulid` = coche). Membresía plural: el mismo
  coche físico puede llevar a la vez una arista OEM-VO y una de `coches.net` sin cambiar
  nunca su concesionario dueño.
- **`source_group='oem_vo_portal'` etiqueta también a los concesionarios poseídos**
  (`kind='compraventa'`, `role` de POS), no solo a las 14 plataformas. Por eso filtrar
  por `source_group` devuelve miles de filas (los dealers); el conjunto de PORTALES se
  aísla con `entity.kind='oem_vo_portal'` → exactamente **14** entidades `[VERIFIED]`.

```sql
-- Las 14 entidades-portal (NO los dealers):
SELECT cdp_code, trade_name, defense_tier, is_tier1
FROM entity WHERE kind = 'oem_vo_portal';   -- -> 14 filas
```

### Disyunción (sin solapamiento) `[VERIFIED]` en la DB viva

- **Coches:** la suma de los 14 conteos por portal = **32 360**, idéntica a
  `COUNT(DISTINCT vehicle_ulid)` sobre las 14 aristas a la vez = **32 360**. **Cero**
  coches compartidos entre portales — cada marca publica solo su propia marca.
- **Dealers:** `COUNT(DISTINCT v.entity_ulid)` sobre las 14 aristas = **5 755**
  concesionarios oficiales distintos. La suma por-portal es 5 758, así que hay un
  **solape mínimo de 3 dealers** entre portales (3 concesionarios oficiales venden bajo más
  de un programa de marca) — los coches NO se comparten (32 360 = 32 360), solo esos pocos
  dealers. El total de grupo de dealers (5 755) usa el `COUNT(DISTINCT)`, no la suma.

> **Nota de reconciliación honesta.** `docs/architecture/OEM_VO_GROUP.md` reporta un
> rollup ANTERIOR (22 222 coches / 1 171 dealers, snapshot previo). Ese documento está
> **desactualizado**: re-harvests posteriores (veredictos 5xx del 2026-06-13) crecieron
> spoticar 5884→6138, toyota 2024→3834, bmw 507→2848, mercedes 300→4792, mini 100→678,
> kia 1036→1519, nissan 1546→1622, volvo 1697→1801. Este runbook reporta los números del
> **veredicto TRUSTWORTHY más reciente por portal**, que coinciden al dígito con las
> aristas vivas. La regla manda: gana la DB + el veredicto persistido.

---

## 1. Rollup validado — las 14 plataformas

`cars` = `COUNT(*)` de `platform_listing` del portal = `COUNT(DISTINCT vehicle)` vía join
(idénticos, exacto). `dealers` = concesionarios oficiales dueños distintos vía esa arista.
`verdict id` = fila `verification_verdict` más reciente (`subject_type='platform_slice'`,
`verdict='TRUSTWORTHY'`), cuyo `primary_value` == `cars`.

| Portal | `cdp_code` | Cars | Dealers | `defense_tier` | `is_tier1` | `family` | Verdict id | `primary_value` |
|---|---|--:|--:|---|:--:|---|--:|--:|
| **spoticar** (Stellantis: Peugeot, Citroën, Opel, DS, Fiat, Jeep…) | `CDP-ES-00-D6X2282Y` | **6 138** | 136 | `t1_soft` | TRUE | `stellantis_vo` | **573** | 6138 |
| **mercedes_benz** (Mercedes-Benz Certified) | `CDP-ES-00-A57R0YK8` | **4 792** | 4 749 | `t0_open` | FALSE | `mercedes_benz_vo` | **515** | 4792 |
| **toyota_lexus** (Toyota Plus + Lexus Select) | `CDP-ES-00-GNAJ5S16` | **3 834** | 129 | `t0_open` | FALSE | `toyota_lexus_vo` | **572** | 3834 |
| **audi** (Audi Selection :plus) | `CDP-ES-00-NP3AWN4X` | **3 798** | 56 | `t0_open` | FALSE | `audi_vo` | **482** | 3798 |
| **bmw** (BMW Premium Selection) | `CDP-ES-00-ZXZD056M` | **2 848** | 51 | `t1_soft` | TRUE | `bmw_group_vo` | **524** | 2848 |
| **hyundai** (Hyundai Promise / Seminuevos) | `CDP-ES-00-C2SVJWB5` | **1 994** | 63 | `t1_soft` | TRUE | `hyundai_vo` | **569** | 1994 |
| **volvo_jlr_suzuki** (Volvo Selekt + JLR Approved) | `CDP-ES-00-T0G18J3M` | **1 801** | 98 | `t1_soft` | TRUE | `volvo_jlr_suzuki_vo` | **571** | 1801 |
| **nissan** (Nissan Intelligent Choice) | `CDP-ES-00-TDWVVTAF` | **1 622** | 41 | `t0_open` | FALSE | `nissan_intelligent_choice` | **566** | 1622 |
| **kia** (Kia Seminuevos Certificados) | `CDP-ES-00-YK54F18S` | **1 519** | 63 | `t1_soft` | FALSE | `kia_vo` | **570** | 1519 |
| **seat_cupra** (CUPRA Approved) | `CDP-ES-00-3N995HG6` | **1 323** | 87 | `t1_soft` | TRUE | `seat_cupra_vo` | **567** | 1323 |
| **renew** (Renault Group: Renault, Dacia, Refactory) | `CDP-ES-00-DT59NK3D` | **918** | 115 | `t0_open` | FALSE | `renault_group` | **423** | 918 |
| **mini** (MINI NEXT) | `CDP-ES-00-EV9ECTV7` | **678** | 83 | `t1_soft` | TRUE | `bmw_group_vo` | **527** | 678 |
| **das_weltauto** (VW Group: VW, SEAT, Škoda, CUPRA, Audi) | `CDP-ES-00-XWX9RHG7` | **552** | 56 | `t1_soft` | FALSE | `vw_group` | **428** | 552 |
| **ford** (Ford Selección / Vehículos de Ocasión) | `CDP-ES-00-ZB6C77HC` | **543** | 31 | `t1_soft` | TRUE | `ford_vo` | **488** | 543 |
| **TOTAL** | — | **32 360** | **5 755** | — | — | — | **14/14 TRUSTWORTHY** | — |

**Convergencia VAM (la quórum de 3 conteos).** Cada veredicto guarda 3 rutas ortogonales
en `independent_values`: `harvested_cageable` (verdad del harvest), `db_edges` (verdad de
escritura) y `db_join_vehicles` (verdad de lectura). En los 14:
`db_edges == db_join_vehicles == primary_value` **exacto**. La `divergence` solo aparece en
`harvested_cageable` (snapshot de la API ligeramente por detrás de la DB tras re-runs), toda
dentro de tolerancia → TRUSTWORTHY:

| Portal | verdict id | harvested | db_edges | db_join | divergence |
|---|--:|--:|--:|--:|--:|
| renew | 423 | 918 | 918 | 918 | 0.0000 |
| das_weltauto | 428 | 552 | 552 | 552 | 0.0000 |
| audi | 482 | 3798 | 3798 | 3798 | 0.0000 |
| ford | 488 | 543 | 543 | 543 | 0.0000 |
| mercedes_benz | 515 | 4792 | 4792 | 4792 | 0.0000 |
| bmw | 524 | 2848 | 2848 | 2848 | 0.0000 |
| seat_cupra | 567 | 1323 | 1323 | 1323 | 0.0000 |
| hyundai | 569 | 1994 | 1994 | 1994 | 0.0000 |
| kia | 570 | 1513 | 1519 | 1519 | 0.0039 |
| mini | 527 | 674 | 678 | 678 | 0.0059 |
| toyota_lexus | 572 | 3801 | 3834 | 3834 | 0.0086 |
| volvo_jlr_suzuki | 571 | 1740 | 1801 | 1801 | 0.0339 |
| nissan | 566 | 1557 | 1622 | 1622 | 0.0401 |
| spoticar | 573 | 5888 | 6138 | 6138 | 0.0407 |

**Reproducir el conteo de cualquier portal contra la DB:**
```bash
# por CDP code -> edges == distinct vehicles == dealers, y el verdict más reciente:
psql "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep" -c "
  WITH p AS (SELECT entity_ulid FROM entity WHERE cdp_code='CDP-ES-00-D6X2282Y')
  SELECT count(*) edges,
         count(DISTINCT pl.vehicle_ulid) cars,
         count(DISTINCT v.entity_ulid)  dealers
  FROM platform_listing pl JOIN vehicle v ON v.vehicle_ulid=pl.vehicle_ulid
  WHERE pl.platform_entity_ulid=(SELECT entity_ulid FROM p);"

psql "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep" -c "
  SELECT id, verdict, primary_value, independent_values, divergence
  FROM verification_verdict
  WHERE subject_type='platform_slice' AND subject_key='CDP-ES-00-D6X2282Y'
  ORDER BY id DESC LIMIT 1;"
```

---

## 2. Configuración común (la receta UNA, no un fork)

Los 14 conectores son `pipeline/platform/*_wholesale.py` y **espejan exactamente**
`spoticar_wholesale.py` / `oem_toyota_lexus_wholesale.py` (la plantilla OEM-VO probada):
mismo modelo de doble membresía, misma jaula bulk, mismo cableado governor/health/VAM.

- **Engine de fetch:** `curl_cffi impersonate='chrome131'` (TLS JA3 de Chrome) en un worker
  thread, ruteado SIEMPRE por el governor por-host (`pipeline/engine/governor.py`), el único
  cuello de botella. POST/GET síncrono fuera del event loop.
- **Governor rate-class** (`pipeline/engine/governor.py`, `_HOST_RATE_CLASSES`):
  - **JSON_API** (12 req/s, burst 24) — solo 3 hosts OEM-VO registrados explícitamente:
    `es.renew.auto` (renew), `scs.audi.de` (audi), `kiaokasion.net` (kia).
  - **STEALTH** (default 0.7 req/s) — **todos los demás hosts OEM-VO** lo heredan (no están
    en la tabla → tratados como frágiles hasta probar lo contrario). Esto incluye
    `www.spoticar.es`, `usc-webcomponents.toyota-europe.com`, `www.hyundai.es`,
    `ocasion.mercedes-benz.es`, `www.servicescache.ford.com`, `gq-eu-prod.nissanpace.com`,
    `services.codeweavers.net`, `production-api.search-api.netdirector.auto`,
    `vtpapi.seat.com`, `www.bmwpremiumselection.es`, `www.mininext.es`,
    `www.dasweltauto.es`.
- **`defense_tier`** (columna `entity.defense_tier`, valor real de la DB en la tabla §1):
  - `t0_open` — sirve a fetch sin WAF (a veces solo un token público estático): audi,
    toyota_lexus, mercedes_benz, nissan, renew.
  - `t1_soft` — WAF/edge-gate blando, 403 a curl pelado, pasa con chrome131 TLS; sin reto JS:
    spoticar, hyundai, kia, seat_cupra, volvo_jlr_suzuki, das_weltauto, ford, bmw, mini.
- **GEO:** preferencia `ZIP[:2]` → provincia INE (autoritativo); fallback `lat/lon` vía
  `ProvinceGeocoder` (punto etiquetado más cercano); ciudad → municipio best-effort vía
  `GeoResolver`. spoticar/kia no traen ZIP en el listado (lat/lng o ciudad respectivamente).
- **Encoding trap:** la mayoría sirve texto humano como mojibake latin-1 sobre el cable
  (`autom�tico`=`automático`). Re-encode por campo: `s.encode('latin-1').decode('utf-8')`.
  Excepciones limpias UTF-8: `seat_cupra` (UTF-8 genuino), `mercedes_benz` (UTF-8 con BOM,
  decode `utf-8-sig`).

---

## 3. Ficha por portal — superficie, micro-acciones, receta, resultado, CLI

> Para cada portal: **(a)** qué es · **(b)** superficie/data-layer + micro-acciones paso a
> paso · **(c)** receta (fichero conector, governor class, `defense_tier`, `source_group`,
> `kind`, `family`) · **(d)** resultado validado (count + verdict id) · **(e)** CLI exacta.

### 3.1 spoticar — Stellantis VO (Drupal SPA + Elasticsearch)

- **(a)** Portal certificado de ocasión del grupo Stellantis ES (Peugeot, Citroën, DS, Opel,
  Fiat, Jeep, Alfa Romeo, Abarth). La red OEM-VO más grande de ES.
- **(b) Superficie:** API JSON interna de un SPA Drupal sobre Elasticsearch.
  - **Endpoint:** `GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}`
  - **Headers (200 application/json):** `X-Requested-With: XMLHttpRequest`,
    `Referer: https://www.spoticar.es/comprar-coches-de-ocasion`, UA Chrome. (curl pelado → 403 AkamaiGHost.)
  - **Micro-acciones:** 1) opcional `GET /api/count-published-vo` → `{"count_vo_published":"6336"}`
    (denominador). 2) Paginar `page=1..~528`, 12 coches/página, FLAT (sin cap de relevancia ni
    muro de profundidad). 3) Cada `hits[]._source` trae coche + dealer vía `field_pdv_*`
    (`field_pdv_geo_id`, `field_pdv_geolocation="lat,lng"`, `field_pdv_city`); atribución
    por-coche, NO PDP. 4) Provincia desde lat/lng (no hay ZIP). Re-encode latin-1.
- **(c) Receta:** conector `pipeline/platform/spoticar_wholesale.py` · governor **STEALTH**
  (`www.spoticar.es` no está en la tabla JSON_API) · `defense_tier=t1_soft` · `is_tier1=TRUE`
  (Akamai) · `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=stellantis_vo`.
- **(d) Resultado:** **6 138 coches / 136 dealers**. Verdict id **573** TRUSTWORTHY
  (`db_edges=db_join=6138`, `harvested=5888`, div 0.0407 dentro de tolerancia).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.spoticar_wholesale --pages 528
  ```

### 3.2 mercedes_benz — Mercedes-Benz Certified (SSR + AJAX `/ajxvl`)

- **(a)** Portal certificado de ocasión de Mercedes-Benz ES. Perfil de red invertido:
  red ancha y poco profunda (4 792 coches sobre 4 749 dealers, ~1 coche/dealer).
- **(b) Superficie:** listado SSR cuya paginación es un endpoint AJAX.
  - **Endpoint:** `POST https://ocasion.mercedes-benz.es/ajxvl`
  - **Headers/body:** `Content-Type: application/x-www-form-urlencoded`,
    `X-Requested-With: XMLHttpRequest`, Origin/Referer
    `https://ocasion.mercedes-benz.es/vehicles?referrer=vehiclesearch&language=es-ES`;
    FormData `{type:'vehiclelist', q, page:N, area:1}`. Setea cookie `UCSSID` (warm-up del
    listado por sesión del pool).
  - **Micro-acciones:** 1) GET `/vehicles` una vez (cookie + chrome del pager). 2) `POST /ajxvl`
    `page=1..401`, 12 coches/página de markup HTML autocontenido (401 = 4 coches cola;
    400*12+4 = 4804 = `data.count`). FLAT. 3) Por tarjeta: coche + dealer
    (`result-box-location-item` nombre + `"<CP> <ciudad>"` + `dealerCode` = prefijo de
    `"<dealerCode>-<carCode>"`). 4) Provincia = `CP[:2]` (INE). 5) Decode `utf-8-sig` (BOM);
    UTF-8 limpio, sin re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_mercedes_benz_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t0_open` (urllib pelado da 200; sin WAF) · `is_tier1=FALSE` ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=mercedes_benz_vo`.
- **(d) Resultado:** **4 792 coches / 4 749 dealers**. Verdict id **515** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_mercedes_benz_wholesale --pages 401
  ```

### 3.3 toyota_lexus — Toyota Plus + Lexus Select (Toyota-Europe USC)

- **(a)** Dos redes OEM-VO (Toyota Ocasión/Plus + Lexus Select) sobre UN backend.
- **(b) Superficie:** Toyota-Europe **USC** (Used Stock Cars) Web Components, una API JSON.
  - **Endpoint:** `POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}`
  - **Body:** `{filterContext:"used", distributorCode:"9424M", offset, ...}` (Lexus añade
    `filters:[{usedCarBrand:["22"]}]`). CloudFront (`x-amz-cf-id`), SIN WAF bot → 200 incluso a curl.
  - **Micro-acciones:** 1) POST por marca (mismo `distributorCode` ES `9424M`). 2) Respuesta
    `{totalResultCount, totalPageCount, results:[…]}`; `offset` es cursor de FILA, caminar
    `offset=0..totalResultCount` por `resultCount`, FLAT. 3) Cada `results[]` trae coche +
    `dealer{}` embebido (id, address+zip, lat/lon, phone). 4) Provincia = `dealer.address.zip[:2]`
    (INE) con fallback geocode. Re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_toyota_lexus_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t0_open` · `is_tier1=FALSE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=toyota_lexus_vo`.
- **(d) Resultado:** **3 834 coches / 129 dealers**. Verdict id **572** TRUSTWORTHY (div 0.0086).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_toyota_lexus_wholesale --pages 80
  ```

### 3.4 audi — Audi Selection :plus (SCS `scs.audi.de`)

- **(a)** Portal certificado mono-marca de Audi ES (separado de Das WeltAuto del VW Group).
- **(b) Superficie:** SPA OneAudi/NEMO (VTP) → API JSON global Stock Car Search (SCS).
  - **Endpoint:** `GET https://scs.audi.de/api/v2/search/filter/esuc/es?from={N}&size=96&sort=prices.retail:asc`
    (`esuc` = ES Used Cars).
  - **Headers (200):** **`token: FJ54W6H`** (api-key PÚBLICA estática del `envConfig.scs.apiKey`;
    401 sin ella — NO es credencial), `Referer: https://www.audi.es/`, `Origin`. Sin WAF ni cookie.
  - **Micro-acciones:** 1) GET con `token`. 2) `{totalCount:3798, vehicleBasic:[…]}`; paginar
    `from=0..totalCount` por `size` (96 honrado), FLAT; `from>=totalCount` → 400 (frontera limpia).
    3) Cada `vehicleBasic` trae coche + `dealer{}` (id, city, street, `zipCode`, geoLocation).
    4) Provincia = `zipCode[:2]` (rango 01..52) con fallback geocode. Re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_audi_wholesale.py` · governor **JSON_API**
  (`scs.audi.de` registrado) · `defense_tier=t0_open` · `is_tier1=FALSE` ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=audi_vo`.
- **(d) Resultado:** **3 798 coches / 56 dealers**. Verdict id **482** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_audi_wholesale --pages 40
  ```

### 3.5 bmw — BMW Premium Selection (Motorflash SSR, barrido por dealer)

- **(a)** Portal certificado de BMW ES (mismo backend Motorflash que MINI NEXT).
- **(b) Superficie:** listado SSR Motorflash. Roster de dealers en `sitemap.xml`; cada dealer
  tiene un paginador profundo.
  - **Endpoints:** 1) `GET https://www.bmwpremiumselection.es/sitemap.xml` → roster
    (`/concesionarios/{prov}/{dealer}`). 2) `GET https://www.bmwpremiumselection.es/concesionarios/{prov}/{dealer}/?pagina=N`
    (**BMW requiere slash final**) → 12 car-cards/página, FLAT.
  - **Micro-acciones:** 1) Sitemap → lista de dealers. 2) Por dealer, `?pagina=N` hasta que
    `id_total_resultados` se agote; Σ sobre el roster = stock nacional. 3) Cada coche es una
    CARD de `<input>` ocultos: `anuncio_id, precio, marcaVehiculo, modeloVehiculo, kilometros,
    bastidorVehiculo`=VIN, `fechamatriculacion`, `img`, etc. — VIN embebido, NO PDP. 4) Provincia
    desde el slug de la URL `/{province-slug}/` vía `GeoResolver.province_code`. Re-encode latin-1
    + vocabulario fijo para fuel/gearbox con U+FFFD de origen.
- **(c) Receta:** conector compartido `pipeline/platform/oem_bmw_mini_wholesale.py` (`--brand bmw`)
  · governor **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE` (WAF/CDN) ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=bmw_group_vo` ·
  `data_surface=json_ld`.
- **(d) Resultado:** **2 848 coches / 51 dealers**. Verdict id **524** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_bmw_mini_wholesale --brand bmw
  # o ambas marcas a la vez:
  python -m pipeline.platform.oem_bmw_mini_wholesale --brand both
  ```

### 3.6 hyundai — Hyundai Promise / Seminuevos (OpenCart, listado plano + directorio)

- **(a)** Portal certificado de Hyundai Motor España.
- **(b) Superficie:** dos endpoints JSON internos de un storefront OpenCart.
  - **Stock:** `GET https://www.hyundai.es/seminuevos/index.php?route=product/vehiculo/listado`
    → `{vehiculos:[…]}` TODO el stock nacional FLAT en una respuesta (sin paginación). Headers:
    `X-Requested-With: XMLHttpRequest`, `Referer: https://www.hyundai.es/seminuevos/`.
  - **Dealers:** `GET https://www.hyundai.es/concesionarios/index.php?route=api/installation/seminuevos`
    → `{instalaciones:[…]}` (~155 instalaciones: nombre, phone, zipcode, zone, city, lat/lon,
    `concesionario_id`), fetch UNA vez por run.
  - **Micro-acciones:** 1) GET listado → coches con VIN real (`bastidor`) + `concesionario`
    (nombre) + `telefono`, pero SIN ubicación. 2) GET instalaciones → índice. 3) Join coche↔dealer
    por **teléfono** (primario exacto) → **nombre normalizado** (fallback). 4) Provincia =
    `installation.zipcode[:2]` (INE). **Trampas:** `vehiculo_id` ROTA por fetch (NO usar como
    dedup; usar VIN); leer `lat`/`lon` correctos e ignorar `latitud`/`longitud` (intercambiados).
    Re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_hyundai_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t1_soft` · `is_tier1=TRUE` (WAF) · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=hyundai_vo`.
- **(d) Resultado:** **1 994 coches / 63 dealers**. Verdict id **569** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_hyundai_wholesale
  ```

### 3.7 volvo_jlr_suzuki — Volvo Selekt + JLR Approved (DOS backends, UN conector)

- **(a)** Frente multi-marca: Volvo Selekt + Jaguar/Land Rover Approved. (Suzuki: diferido — §"NO validado".)
- **(b) Superficie:** dos plataformas vendor distintas.
  - **Volvo Selekt** (Codeweavers Digital Retail Store):
    1) `POST https://services.codeweavers.net/api/guest/initialise/proposal` con headers
       `x-cw-digitalretailstorereference`, `x-cw-applicationname: Storefront`, `x-cw-anti-cache`,
       y body `{"ApiKey":"n1WG1lPrjpggL45z6p","OrganisationIdentifier":{"Type":"CodeweaversReference","Value":"55388"}}`
       → `{"UserToken":"<guid>"}` (token de cliente invitado).
    2) `POST https://services.codeweavers.net/api/vehicles/search/count` con `x-cw-customertoken: <UserToken>`.
    3) `POST https://services.codeweavers.net/api/vehicles/search-with-facets` (paginación FLAT
       `Page`+`ResultsPerPage`). ~1 311 coches.
  - **JLR Approved** (GForces NetDirector AVL, GraphQL):
    `POST https://production-api.search-api.netdirector.auto/api/vehicle-search?uuid=…`
    (`getCount`+`getAll`), `Authorization` token cliente estático, marca por
    `companyHash`+`manufacturer`. Land Rover ~399 + Jaguar ~35.
  - **Micro-acciones GEO:** Volvo `Retailer.Address.Postcode` (+ lat/lng); AVL
    `location.details.address.postcode`. Provincia = `postcode[:2]` (INE). Dedup por
    `Physical.ExternalVehicleId` (MDX-xxxx) o VIN — NUNCA por `Reference` (token rotatorio).
    Re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_volvo_jlr_suzuki_wholesale.py` · governor **STEALTH**
  (ambos hosts) · `defense_tier=t1_soft` · `is_tier1=TRUE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=volvo_jlr_suzuki_vo`.
- **(d) Resultado:** **1 801 coches / 98 dealers** (Volvo + JLR; Suzuki no incluido).
  Verdict id **571** TRUSTWORTHY (div 0.0339).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20
  ```

### 3.8 nissan — Nissan Intelligent Choice (Next.js + AppSync GraphQL + Cognito)

- **(a)** Portal certificado de Nissan Iberia. Slice elegido del frente nissan/mazda/honda
  (Mazda amurallado, Honda sin data-layer — §"NO validado").
- **(b) Superficie:** Next.js SSR sobre AWS AppSync GraphQL.
  - **Micro-acciones:** 1) Mint de idToken Cognito (público, sin auth):
     `GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token`
     (`Origin: https://www.ocasion.nissan.es`) → `{"idToken":"<JWT ~1169 chars>"}`. **Refrescar por run.**
    2) Paginar inventario: `POST https://gq-eu-prod.nissanpace.com/graphql`
     (`GetUsedCarsInventoryData`), `Authorization: <idToken>` (bare o `Bearer`).
     **NO usar `graphqlkey`/`x-api-key`** (→ Unauthorized). 3) Dealer-locator query resuelve cada
     `dealerId` a postCode/lat-lng/city. Provincia = postCode[:2].
- **(c) Receta:** `pipeline/platform/oem_nissan_mazda_honda_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t0_open` · `is_tier1=FALSE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=nissan_intelligent_choice`.
- **(d) Resultado:** **1 622 coches / 41 dealers**. Verdict id **566** TRUSTWORTHY (div 0.0401).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104
  ```

### 3.9 kia — Kia Seminuevos Certificados (vendor IIS, barrido de clusters)

- **(a)** Portal certificado de Kia Iberia, backend "Kia Okasión" (ASP.NET/IIS) en kiaokasion.net.
- **(b) Superficie:** un servlet multiplexado por campo `accion`.
  - **Endpoint:** `POST https://kiaokasion.net/kia/async/metodos.aspx`
    (`Content-Type: application/x-www-form-urlencoded`, `X-Requested-With: XMLHttpRequest`,
    `Origin/Referer: https://www.kia.com`). `accion=actualizarCoches` → coches;
    `accion=actualizarTodoBuscador` → facetas. (IIS raíz 403 a curl pelado; sirve a chrome131.)
  - **Hecho estructural — PARTICIÓN POR CLUSTER:** el catálogo se particiona por
    `idconcesionario` (el `__kiaClienteId` inline = id de GRUPO/cluster, NO un solo dealer).
    `idconcesionario=0` → 0 coches; solo un conjunto disperso (~55 clusters vivos, ids 331..1810)
    trae stock. `km=nacional` solo relaja el radio DENTRO del stock de un cluster, NO agrega.
  - **Micro-acciones:** 1) BARRER `idconcesionario` exhaustivamente 1..2000. 2) Por cluster vivo,
    `accion=actualizarCoches` paginado. 3) Stock nacional = UNIÓN sobre todos los clusters. 4)
    `concesionario` (nombre) + `poblacion` (ciudad) por coche → provincia vía
    `GeoResolver.resolve_city_global` (sin CP en lista). `dealerId` = compuesto
    (cluster + nombre + ciudad). Re-encode latin-1.
- **(c) Receta:** `pipeline/platform/oem_kia_wholesale.py` · governor **JSON_API**
  (`kiaokasion.net` registrado — el barrido de ~2000 probes exige ritmo alto) ·
  `defense_tier=t1_soft` · `is_tier1=FALSE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=kia_vo`.
- **(d) Resultado:** **1 519 coches / 63 dealers**. Verdict id **570** TRUSTWORTHY (div 0.0039).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_kia_wholesale
  python -m pipeline.platform.oem_kia_wholesale --limit 500   # ~target de coches
  ```

### 3.10 seat_cupra — CUPRA Approved (VTP `vtpapi.seat.com`, paginación por headers)

- **(a)** Portal certificado de CUPRA ES. La mitad SEAT YA está cubierta por Das WeltAuto
  (SEAT Ocasión redirige a dasweltauto.es); aquí solo CUPRA, sin doble conteo.
- **(b) Superficie:** SPA Web-Components (cuprawebfe) → REST VTP, tenant `cuesgwb`.
  - **Endpoint:** `GET https://vtpapi.seat.com/restapi/v1/cuesgwb/search/car`
  - **Headers (paginación va en HEADERS, no query):** `x-pattern: cuprawebfe` (requerido por el
    edge gate Traefik), `x-page: N`, `x-page-items: 96` (default SPA 12; API honra ≥96),
    `x-sort: DATE_OFFER`, `x-sort-direction: DESC`. (urllib pelado → 403; chrome131 → 200.)
  - **Micro-acciones:** 1) GET con headers. 2) Total en **RESPONSE header** `x-result-number: 1323`
    (no en el body). 3) Paginar `x-page=1..ceil(total/96)`, FLAT. 4) Cada coche trae
    `hypermediadealer.dealer{}` (key, city, name, zip, position lat/lng); provincia = `zip[:2]`
    con fallback lat/lng. 5) `deep_link` construido
    `https://www.cupra.com/es-es/localizador-stock/coche/{carid}`. UTF-8 limpio (sin re-encode).
- **(c) Receta:** `pipeline/platform/oem_seat_cupra_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t1_soft` · `is_tier1=TRUE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=seat_cupra_vo`.
- **(d) Resultado:** **1 323 coches / 87 dealers**. Verdict id **567** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_seat_cupra_wholesale --pages 14
  ```

### 3.11 renew — Renault Group VO (AEM + ES, loader React-Router `.data`)

- **(a)** Portal certificado del grupo Renault ES (Renault + Dacia + stock Refactory). El PRIMER
  portal OEM-VO que abrió el grupo.
- **(b) Superficie:** catálogo facetado AEM+Elasticsearch tras un loader single-fetch React-Router.
  - **Endpoint:** `GET https://es.renew.auto/vehiculos.data?<facets>&page=N`. La ruta pública
    `/vehiculos` acepta params ES crudos (`brand.label.raw=RENAULT`, …). Sin WAF a curl_cffi.
  - **Micro-acciones:** 1) GET `.data` con `page=N`. 2) Slice
    `content.contentZone.slice243v0.data`: `totalElements/totalPages` (denominador) + `data[]`
    (23 coches/página). 3) `page` es paginador estable (0 solape entre páginas). 4) Cada coche
    trae VIN real + `vehicleExhibitionSite` = dealer (dealerId, name, postalCode, locality,
    geolocalization); provincia = postalCode[:2].
- **(c) Receta:** `pipeline/platform/renew_wholesale.py` · governor **JSON_API**
  (`es.renew.auto` registrado) · `defense_tier=t0_open` · `is_tier1=FALSE` ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=renault_group`.
- **(d) Resultado:** **918 coches / 115 dealers** (slice probado; el portal declara ~5 739
  nacionales). Verdict id **423** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.renew_wholesale --pages 8
  ```

### 3.12 mini — MINI NEXT (Motorflash SSR, barrido por dealer)

- **(a)** Portal certificado de MINI ES (mismo backend Motorflash que BMW Premium Selection).
- **(b) Superficie:** idéntica a §3.5 (BMW), base `https://www.mininext.es`.
  - **Endpoints:** `GET https://www.mininext.es/sitemap.xml` → roster (~47 dealers);
    `GET https://www.mininext.es/concesionarios/{prov}/{dealer}?pagina=N` (**MINI: SIN slash
    final, 404 con slash**) → 12 cards/página.
  - **Micro-acciones:** igual que BMW; MINI añade `concesionario`/`provincia` por card. VIN
    embebido en card, NO PDP. Re-encode latin-1 + vocabulario fijo fuel/gearbox.
- **(c) Receta:** conector compartido `pipeline/platform/oem_bmw_mini_wholesale.py` (`--brand mini`)
  · governor **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE` ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=bmw_group_vo` ·
  `data_surface=json_ld`.
- **(d) Resultado:** **678 coches / 83 dealers**. Verdict id **527** TRUSTWORTHY (div 0.0059).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_bmw_mini_wholesale --brand mini
  ```

### 3.13 das_weltauto — VW Group VO (AEM SSR + Motorflash, por provincia)

- **(a)** Portal certificado genérico multi-marca del grupo VW ES (VW, SEAT, Škoda, CUPRA, Audi
  certificados por su red). (La mitad Audi tiene además su portal propio §3.4; SEAT VO == este.)
- **(b) Superficie:** sitio AEM SSR (vw-dwa3) sobre feed Motorflash. HTML, pero cada card lleva
  JSON embebido en atributos.
  - **Endpoint:** `GET https://www.dasweltauto.es/esp/coches-de-segunda-mano-en-{provincia}?pagina=N`
    (la ruta nacional bare IGNORA `?pagina`). Origin 403 a fetch naïve; sirve a chrome131.
  - **Micro-acciones:** 1) Enumerar POR PROVINCIA (`{provincia}` slug), `?pagina=N`. 2) Por card:
    `data-configuration='{…}'` = coche (VehicleManufacturer, Model, Vehicle.VehicleId, Milage,
    RegistrationDate, FuelType, Price, Color) y `data-partner='{…}'` = dealer (InformationBnr,
    Name, City, ZIP). 3) **Señal de parada:** la última página CLAMP-REPITE → parar cuando una
    página añade CERO VehicleIds nuevos (no cuando está vacía). 4) Provincia = ZIP[:2].
- **(c) Receta:** `pipeline/platform/dasweltauto_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t1_soft` · `is_tier1=FALSE` · `source_group=oem_vo_portal` ·
  `kind=oem_vo_portal` · `family=vw_group` · `data_surface=next_data`.
- **(d) Resultado:** **552 coches / 56 dealers** (slice capado; el portal anuncia >8 000
  nacionales). Verdict id **428** TRUSTWORTHY (div 0.0).
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.dasweltauto_wholesale --provinces 3 --pages 8
  ```

### 3.14 ford — Ford Selección / Vehículos de Ocasión (eUsed, gate consumidor blando)

- **(a)** Portal certificado de Ford ES (Approved-Used / Ford Store VO).
- **(b) Superficie:** SPA AngularJS (GUXFOE) sobre el servicio Ford eUsed (eUSL).
  - **Endpoint:** `POST https://www.servicescache.ford.com/api/eUsed/v1/searchVehicles`
  - **Headers (Akamai + gate de consumidor, todo reproducible cliente-side):**
    `Referer: https://secure.ford.es/`, `Origin`,
    `x-eusl-consumer: b-gux_approved_used-prod` (`b-{appName}-{env}`),
    `x-eusl-k: base64("{epoch_millis}:{nonce-16-bytes-hex}")` **fresco por request** (replay
    rechazado). NO bearer, NO cookie, NO login.
  - **Body:** búsqueda GEO-RADIO `longLatCoordinates="{lng},{lat}"` + `distance` (km) +
    `pagination:{maxRecords:20000, startingRecord:0}`.
  - **Micro-acciones:** 1) Generar headers por request. 2) UNA query nacional desde el centro de
    España con `distance>=2000` km cubre península + Canarias; `maxRecords=20000` devuelve los 543
    en una respuesta (FLAT). 3) `data.VehicleInventoryList.VehicleInventoryItem[]`: coche
    (`Vehicle.*`) + dealer (`VendorInformation.*`: VendorCode, VendorName, Address+PostCode+coords).
    Provincia = PostCode[:2].
- **(c) Receta:** `pipeline/platform/oem_ford_wholesale.py` · governor **STEALTH** ·
  `defense_tier=t1_soft` (Akamai + gate blando) · `is_tier1=TRUE` (akamai-grn) ·
  `source_group=oem_vo_portal` · `kind=oem_vo_portal` · `family=ford_vo`.
- **(d) Resultado:** **543 coches / 31 dealers**. Verdict id **488** TRUSTWORTHY (div 0.0);
  re-run idempotente añadió 0.
- **(e) CLI:**
  ```bash
  python -m pipeline.platform.oem_ford_wholesale --pages 1
  ```

---

## 4. NO validado (fuera del runbook)

Reconocido pero NO conectado por falta de superficie data-layer limpia — **no entra** al
runbook. Documentado en
`docs/architecture/tier1_recipes/oem_nissan_mazda_honda_datalayer.md` (§6) y
`docs/architecture/tier1_recipes/oem_volvo_jlr_suzuki_datalayer.md`.

| Marca | Superficie | Estado | Motivo |
|---|---|---|---|
| **Mazda** (`mazdaselected.es`) | Mazda Selected | ⛔ **AMURALLADO** | TLS connect hace timeout a `curl_cffi`; sin superficie limpia alcanzable (necesitaría camoufox / otro ingress). |
| **Honda** (`vehiculosdeocasion.honda.es`) | Honda Approved | ⚪ **SIN DATA-LAYER** | Sitio jQuery SSR; el "buscador" pagina re-GETeando la MISMA URL HTML (no hay JSON). Es un workaround facet, no una superficie data-layer. |
| **Suzuki** (`auto.suzuki.es/vehiculos-ocasion`) | directorio de ~30 subsitios `redsuzuki.es` | 🟡 **DIFERIDO (long-tail)** | Cada subsitio renderiza su propio HTML sin JSON central; scrape por-dealer, no superficie uncapped. Catalogado para un pase long-tail futuro. NO forzado por el conector volvo_jlr_suzuki. |

> El conector `oem_nissan_mazda_honda_wholesale.py` cubre SOLO la slice **Nissan**; el
> `oem_volvo_jlr_suzuki_wholesale.py` cubre SOLO **Volvo + JLR**. Los nombres compuestos de
> los ficheros reflejan el frente investigado, no la cobertura: Mazda/Honda/Suzuki quedan fuera.

---

## 5. Mapa de ficheros (verdad)

- **Conectores (commiteados, `--help` OK los 13 módulos = 14 portales):**
  `pipeline/platform/{spoticar,renew,dasweltauto}_wholesale.py`,
  `pipeline/platform/oem_{audi,bmw_mini,ford,hyundai,kia,mercedes_benz,nissan_mazda_honda,seat_cupra,toyota_lexus,volvo_jlr_suzuki}_wholesale.py`.
- **Recetas data-layer:** `docs/architecture/tier1_recipes/{portal}_datalayer.md`.
- **Rollup de grupo (desactualizado en cifras, válido en taxonomía):**
  `docs/architecture/OEM_VO_GROUP.md`.
- **Governor / rate-class:** `pipeline/engine/governor.py` (`_HOST_RATE_CLASSES`).
- **Taxonomía:** `migrations/0005_types_and_guards.sql` (kind ENUM),
  `migrations/0016_tiering_groups.sql` (defense_tier/source_group/role),
  `migrations/0009_platform_listing.sql` (arista de doble membresía),
  `migrations/0003_vehicles_events.sql` (modelo vehicle/event).
- **Veredictos VAM:** tabla `verification_verdict`, `subject_type='platform_slice'`,
  `subject_key=<cdp_code del portal>`.

> Fecha de validación: **2026-06-13**. Todas las cifras `[VERIFIED]` contra
> `cardeep-pg` (`:5433`, db `cardeep`) y la fila `verification_verdict` más reciente por portal.
