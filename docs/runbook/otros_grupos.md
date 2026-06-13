# RUNBOOK — OTROS GRUPOS (`chain` · `rentacar_vo` · `subastas`)

> **Alcance.** Las tres fuentes no-marketplace y no-OEM-VO de la taxonomía de
> `migrations/0016_tiering_groups.sql`: las **cadenas VO** (`source_group='chain'`), el
> **rent-a-car VO** (`source_group='rentacar_vo'`) y las **subastas B2B** (`kind='subasta'`,
> `source_group='official_registry'`). Todas drenan por la ÚNICA arquitectura
> (`pipeline/platform/group_*_wholesale.py` + `scripts/cage_autorola_bca_subastas.py`):
> governor como punto de estrangulamiento, `GeoResolver`, doble-membresía
> (`vehicle.entity_ulid` = propiedad atómica; `platform_listing` = membresía de plataforma),
> ingesta idempotente `ON CONFLICT`, eventos NEW-delta y quórum de conteo VAM.
>
> **Regla dura de este runbook.** Solo entra lo VALIDADO + FUNCIONAL: cada unidad tiene
> (a) un `verification_verdict` persistido `TRUSTWORTHY` **y** (b) un conector commiteado
> que confirmo compila/corre, con aristas vivas en la DB. Lo aspiracional/roto va al final,
> en **"NO validado (fuera del runbook)"**.
>
> **Fuente de verdad.** DB viva `cardeep` (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`)
> y tabla `verification_verdict`, ambas consultadas **2026-06-13**. ENV de ejecución:
> `PY=C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.

---

## 0. Veredictos VAM persistidos (la base del runbook)

Tres filas `verification_verdict` (`subject_type='group_vam'`) cubren este dominio. Cita
literal de la tabla (id + valor + veredicto):

| `id` | `subject_key` | `claim` | `primary_value` | `divergence` | `verdict` | `created_at` |
|---:|---|---|---:|---:|---|---|
| **541** | `chains` | group car count reconciled across 2 orthogonal DB paths AND disjoint from sibling groups | **37319** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |
| **542** | `rentacar_vo` | (idem) | **166** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |
| **543** | `subastas` | (idem) | **27** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |

- **Caminos del veredicto 541 (`chains`):** pathA `source_group=chain (join entity)` = 37319 vs
  pathB `entity_source source_key ~ '^group_vo_chains'` = 37319; divergencia 0.0; disjunto de
  oem_vo/rentacar_vo/subasta a nivel vehículo (0 owners cruzados).
- **Caminos del veredicto 542 (`rentacar_vo`):** pathA `source_group=rentacar_vo` = 166 vs
  pathB `entity.kind=rent_a_car_vo` = 166; divergencia 0.0.
- **Caminos del veredicto 543 (`subastas`):** pathA `entity.kind=subasta` = 27 vs
  pathB `entity_source source_key ~ 'subastas'` = 27; divergencia 0.0.

> **Honestidad sobre el desfase veredicto ↔ DB viva `[VERIFICADO]`.** Los tres veredictos se
> persistieron a las **00:37Z**. Después de esa hora se ejecutaron drenes adicionales (los
> conectores `group_vo_chains_wholesale.py`, `group_rentacar_vo_wholesale.py` y el script
> `cage_autorola_bca_subastas.py` se modificaron entre las 09:23 y las 18:14 del mismo día) que
> ampliaron el inventario muy por encima de los conteos certificados. El veredicto persistido es
> la **validación formal** (lo que el runbook reporta como TRUSTWORTHY); el conteo **vivo actual**
> se reporta junto a él como cross-check, marcado explícitamente. Ambos son `[VERIFICADO]`; no se
> presenta el conteo vivo como si fuese el conteo certificado.

**Cross-check de disjunción (DB viva, 2026-06-13) `[VERIFICADO]`:**
`DISTINCT(edges ∪ owned)` sobre los tres grupos = **46201** = 39201 (`chain`) + 215 (`rentacar_vo`)
+ 6785 (`subastas`). Las sumas por grupo igualan el total distinto → **ningún vehículo se comparte
entre los tres grupos**.

```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
$PY -c "
import psycopg2
c=psycopg2.connect('postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep'); cur=c.cursor()
cur.execute(\"select id,subject_key,primary_value,divergence,verdict from verification_verdict where id in (541,542,543) order by id\")
for r in cur.fetchall(): print(r)
"
```

---

## 1. Separación de grupos (ejes de `migrations/0016`)

| Grupo | `source_group` | `kind` | `role` | Naturaleza |
|---|---|---|---|---|
| **vo_chains** | `chain` | `cadena` (plataforma) / `compraventa` (sucursal) | `chain` / `standalone_pos` | cadena nacional de VO con muchos puntos físicos |
| **rentacar_vo** | `rentacar_vo` | `rent_a_car_vo` | `chain` | rent-a-car que liquida su ex-flota VO directo |
| **subastas** | `official_registry` | `plataforma` (plataforma) / `subasta` (lote) | `platform` / `registry` | subasta/remarketing B2B; vendedor = el evento de venta |

- **No hay enum `auction` en `source_group`.** Las subastas usan el más cercano,
  `official_registry`, llevando la semántica de subasta en `kind='subasta'` y en
  `family ∈ {ayvens_carmarket, bca_europe, autorola}`. `[VERIFICADO]` en `platform_meta`.
- **Doble-membresía idéntica al grupo OEM-VO.** Propiedad singular en el punto atómico
  (sucursal / cadena / lote de subasta); membresía plural vía arista `platform_listing`
  (plataforma ↔ vehículo). El mismo coche físico puede portar una arista de este grupo y otra de
  un marketplace sin cambiar de dueño.

---

## 2. PRICE-GATE honesto (subastas) — la distinción central

`[VERIFICADO]` en DB viva 2026-06-13:

| Grupo | vehículos | con `price` no-NULL | aristas | `platform_price` no-NULL |
|---|---:|---:|---:|---:|
| `chain` | 39201 | **39201** (100%) | — | (precio retail real) |
| `rentacar_vo` | 215 | **215** (100%) | — | (precio retail real) |
| `subastas` (`kind='subasta'`) | **6785** | **0** (0%) | 6785 | **0** (0%) |

> **El precio de subasta es NULL por diseño, no por fallo.** Las cadenas y el rent-a-car publican
> precio de venta retail → se cagea. En las subastas el precio es de **puja con login** (`Ayvens`
> `fixedPrice` solo en lotes tender; `BCA CanViewPricing=false`; `Autorola loginRequired=true`),
> así que `vehicle.price = NULL` y `platform_listing.platform_price = NULL` en los **6785** lotes y
> **6785** aristas. El vehículo (make/model/año/km/foto/ubicación) sí es público y se cagea; el
> precio jamás se inventa. Esto es lo que el conector llama `price_gate='bid_login_gated'`.

```bash
$PY -c "
import psycopg2
c=psycopg2.connect('postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep'); cur=c.cursor()
cur.execute(\"select count(*), count(price) from vehicle v join entity e on e.entity_ulid=v.entity_ulid where e.kind='subasta'\")
print('subasta owned total/priced:', cur.fetchone())  # -> (6785, 0)
"
```

---

## 3. GRUPO `vo_chains` (`source_group='chain'`) — veredicto **541** TRUSTWORTHY

**Conector:** `pipeline/platform/group_vo_chains_wholesale.py` (compila OK; `--help` corre).
**CLI:** `--members {carplus,clicars,flexicar,ocasionplus}` (default los cuatro), `--pages N` (def 6).
**Governor:** `services.flexicar.es` → clase **JSON_API** (12 req/s, burst 24, min_spacing 0.03 s, en
`_HOST_RATE_CLASSES`); el resto (`www.ocasionplus.com`, `www.clicars.com`, `www.carplus.es`) →
clase **STEALTH** (`www.ocasionplus.com` con override explícito 1.0/3/0.8 en `governor.py:364`; los
demás heredan el default STEALTH 0.7 req/s).
**Defense:** todos `t0_open` (sin WAF). **`is_tier1=FALSE`.**

**DB viva (cross-check) `[VERIFICADO]`:** 189 entidades `chain`; owned=edges=union=**39201**, divergencia 0.0.

### 3.1 Flexicar — `CDP-ES-00-FYECEGD5`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Cadena nacional de VO; API REST/JSON abierta de primera parte. |
| (b) **SURFACE** | `GET https://services.flexicar.es/api/v1/vehicles?page=N&size=24` · `Accept: application/json` · `Origin: https://www.flexicar.es` · `Referer: https://www.flexicar.es/` · `curl_cffi impersonate=chrome131`. Respuesta `{total, pages, results[]}`. **MICRO-ACCIONES:** (1) GET page=1 → leer `total`/`pages`; (2) cargar el directorio de 186 sucursales una vez desde `__NEXT_DATA__` de `https://www.flexicar.es/coches-segunda-mano/` (`.props.pageProps.dealerships[]`); (3) caminar `page=1..pages`; (4) por coche, `result.carDealershipSlug` → sucursal → geo (CP[:2]=provincia INE). `size` HARD-cap 24 (`size>24` → HTTP 400). |
| (c) **RECETA** | conector `group_vo_chains_wholesale.py` · member `flexicar` · governor JSON_API · `defense_tier=t0_open` · `source_group=chain` · `kind=cadena` (plataforma) + 186 sucursales `kind=compraventa`/`role=standalone_pos` · `data_surface=internal_api` (`surface_intent=json_api`, `owner_model=branch`) · `source_key=group_vo_chains_flexicar`. |
| (d) **RESULTADO** | edges vivos = **23874**; 186 entidades-sucursal. Cubierto por veredicto **541** (`chains`, TRUSTWORTHY, div 0.0). |
| (e) **CLI** | `$PY -m pipeline.platform.group_vo_chains_wholesale --members flexicar --pages 1000` |

### 3.2 OcasionPlus — `CDP-ES-00-SWN09H0C`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Cadena VO Next.js; capa de datos = schema.org JSON-LD `ItemList` embebido en SSR. |
| (b) **SURFACE** | `GET https://www.ocasionplus.com/coches-segunda-mano?page=N` · `Referer: https://www.ocasionplus.com/` · `chrome131`. **MICRO-ACCIONES:** (1) GET page=1; (2) parsear el bloque JSON-LD: `Product.offers (AggregateOffer).offerCount` = stock total; `ItemList.itemListElement[].@type=Vehicle` = 20 coches/página; (3) caminar `?page=N` server-side (≈703 págs). `?pagina=N` se ignora (devuelve page 1). Per-branch no está en el listado → la cadena es el punto de venta (`owner_model=chain`). |
| (c) **RECETA** | member `ocasionplus` · governor STEALTH (override 1.0/3/0.8) · `t0_open` · `source_group=chain` · `kind=cadena` · `data_surface=json_ld` (`surface_intent=ssr_jsonld_itemlist`, `owner_model=chain`) · `source_key=group_vo_chains_ocasionplus`. |
| (d) **RESULTADO** | edges vivos = **13445**. Cubierto por veredicto **541**. |
| (e) **CLI** | `$PY -m pipeline.platform.group_vo_chains_wholesale --members ocasionplus --pages 1000` |

### 3.3 Clicars — `CDP-ES-00-QCMVM26T`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Cadena VO; tarjetas SSR HTML en `__NEXT_DATA__`. |
| (b) **SURFACE** | `GET https://www.clicars.com/coches-segunda-mano-ocasion` · `chrome131` · 12 coches/página · `surface_intent=ssr_html_cards`. |
| (c) **RECETA** | member `clicars` · governor STEALTH (default 0.7) · `t0_open` · `source_group=chain` · `kind=cadena` · `data_surface=next_data` · `owner_model=chain` · `source_key=group_vo_chains_clicars`. |
| (d) **RESULTADO** | edges vivos = **1470**. Cubierto por veredicto **541**. |
| (e) **CLI** | `$PY -m pipeline.platform.group_vo_chains_wholesale --members clicars --pages 1000` |

### 3.4 Carplus — `CDP-ES-00-4YVMXZ3T`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Cadena VO; JSON-LD `Vehicle` en SSR. |
| (b) **SURFACE** | `GET https://www.carplus.es/coches-segunda-mano/` · `chrome131` · 16 coches/página · `surface_intent=ssr_jsonld_vehicles`. |
| (c) **RECETA** | member `carplus` · governor STEALTH (default 0.7) · `t0_open` · `source_group=chain` · `kind=cadena` · `data_surface=json_ld` · `owner_model=chain` · `source_key=group_vo_chains_carplus`. |
| (d) **RESULTADO** | edges vivos = **412**. Cubierto por veredicto **541**. |
| (e) **CLI** | `$PY -m pipeline.platform.group_vo_chains_wholesale --members carplus --pages 1000` |

> **Atribución `[VERIFICADO]`.** Flexicar = per-branch (cada coche a su sucursal `compraventa`,
> 186 puntos); OcasionPlus/Clicars/Carplus = chain-as-owner (la cadena posee su stock). `source_key`
> en DB: `group_vo_chains_flexicar`(186 ent.), `_carplus`(1), `_clicars`(1), `_ocasionplus`(1).

---

## 4. GRUPO `rentacar_vo` (`source_group='rentacar_vo'`) — veredicto **542** TRUSTWORTHY

**Conector:** `pipeline/platform/group_rentacar_vo_wholesale.py` (compila OK; `--help` corre).
**CLI:** `--member {all,okmobility,centauro,recordgo}`, `--pages N`, `--limit N`.
**DB viva (cross-check):** 3 entidades; owned=edges=union=**215**, div 0.0. Precio retail 100% no-NULL.
**Modelo:** rent-a-car single-operator → la empresa es el punto de venta y dueña de cada coche.

### 4.1 OK Mobility — `CDP-ES-07-KWGRMQ7B` (PRIMARY, base del veredicto 542)

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Operador de rent-a-car (Palma, prov. 07) que liquida su ex-flota VO. |
| (b) **SURFACE** | `GET https://okmobility.com/en/buy-car/used?page=N` · `chrome131` · SSR HTML. **MICRO-ACCIONES:** (1) GET page=1; (2) `<span id="total-cars">` = stock total; (3) por tarjeta `<a class="own-car-card" data-carid=...>` extraer make/model (`div.car-name`), version (`div.car-motorization`), año/km/fuel/trans (`div.car-summary`), precio (`div.big-cipher-text`), prev_price (`div.deleted-small-cipher-text`), foto (`div.car-image[data-srcbg]`); (4) caminar `?page=N` (~35/pág, 6 págs) hasta página con 0 tarjetas. Locale `/en/` (200); `/es/` 404. |
| (c) **RECETA** | member `okmobility` · governor STEALTH (default 0.7) · `defense_tier=t1_soft` (beacon Opticks; HTML no gateado) · `source_group=rentacar_vo` · `kind=rent_a_car_vo` · `role=chain` · `data_surface=sitemap` (`surface_intent=ssr_html_used_stock_storefront`) · `source_key=group_rentacar_vo_okmobility`. |
| (d) **RESULTADO** | edges vivos = **169**; veredicto **542** certificó **166** (OK Mobility en solitario, div 0.0, TRUSTWORTHY). |
| (e) **CLI** | `$PY -m pipeline.platform.group_rentacar_vo_wholesale --member okmobility --pages 6` |

### 4.2 Centauro — `CDP-ES-03-BMPR08V3` · 4.3 Record Go — `CDP-ES-12-H26EC1KD`

Ambos miembros del MISMO conector, `source_group=rentacar_vo`, `kind=rent_a_car_vo`,
`defense_tier=t1_soft`, drenados 2026-06-13.

| Miembro | `cdp_code` | Surface | edges vivos |
|---|---|---|---:|
| **Centauro** | `CDP-ES-03-BMPR08V3` | `GET https://ventas.centauro.net/coches-ocasion/?pagina=N` (SSR puro; campos en hidden inputs `precio/precioNuevo/kilometros/marcaVehiculo/modeloVehiculo/mesesAntiguedad`; 12/pág, clamp-repeat en el tail) · `source_key=group_rentacar_vo_centauro` | **28** |
| **Record Go** | `CDP-ES-12-H26EC1KD` | `GET https://www.recordgoocasion.es/coches/segunda-mano/?page=N` (CMS DealerK/MotorK, clases `vcard-*`, parseado byte-a-byte por la misma familia; solo `?page=` pagina) · `source_key=group_rentacar_vo_recordgo` | **18** |

- **CLI:** `$PY -m pipeline.platform.group_rentacar_vo_wholesale --member all`
  (o `--member centauro` / `--member recordgo`).
- **Cobertura del veredicto:** Centauro+Record Go (28+18) están en la DB viva bajo
  `source_group=rentacar_vo` y por tanto **dentro del veredicto 542** por su pathA
  (`source_group=rentacar_vo`); el `primary_value=166` del veredicto refleja el estado a las 00:37Z
  (solo OK Mobility), antes de añadir estos dos. Conteo vivo actual del grupo: **215** (169+28+18).

---

## 5. GRUPO `subastas` (`kind='subasta'`, `source_group='official_registry'`) — veredicto **543** TRUSTWORTHY

Tres plataformas de subasta caged, todas con **precio NULL** (bid-gated honesto, §2).
**DB viva (cross-check):** 3 plataformas + 94 vendedores `kind=subasta`; owned=edges=union=**6785**, div 0.0.

| Plataforma | `cdp_code` | family | edges vivos | vendedores `subasta` |
|---|---|---|---:|---:|
| Ayvens Carmarket | `CDP-ES-00-H1VCV020` | `ayvens_carmarket` | **3977** | 54 (`group_subastas_wholesale`) |
| BCA España | `CDP-ES-00-WYJKTP6S` | `bca_europe` | **1752** | 20 (`group_subastas_bca`) |
| Autorola | `CDP-ES-00-RJ109M0T` | `autorola` | **1056** | 20 (`group_subastas_autorola`) |

### 5.1 Ayvens Carmarket — `CDP-ES-00-H1VCV020` (base del veredicto 543)

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Plataforma de remarketing ALD/Ayvens; SPA Angular sobre un gateway GraphQL HotChocolate de primera parte. |
| (b) **SURFACE** | `POST https://api-carmarket.ayvens.com/graphql/saleevents` · `Content-Type: application/json` · `Origin/Referer https://carmarket.ayvens.com/` · headers **client-side** `x-ald-subscription-key: 3b2cc62fd26c4e29a762db3de181266b`, `x-tenant: ald`, `x-country: es` (NO secretos de servidor; el SPA los embarca para el gateway público) · `chrome131`. **MICRO-ACCIONES:** (1) `query SaleEvents` → catálogo de vendedores (id/country/name/reference/type/state/lotsCount); (2) `query LoadLots(order,take=200,skip,where)` con `where.state nin [closed,withdrawn,sold]` y `aggregates.count` = denominador (3977); (3) paginar `skip += 200` hasta `count`; (4) filtrar `saleEventCountry=='es'`; cada lote → vehículo OWNED por su `saleEventId`. Campos: id/make/model/version/mileage/fuelType/transmissionType/firstRegistrationDate/`fixedPrice`(solo tender)/mainImageUrl. |
| (c) **RECETA** | conector `group_subastas_wholesale.py` · governor JSON_API (`api-carmarket.ayvens.com` en `_HOST_RATE_CLASSES`) · `defense_tier=t0_open` · `source_group=official_registry` · `kind=plataforma`/`role=platform` (lotes `kind=subasta`/`role=registry`, provincia NULL) · `data_surface=internal_api` (`surface_intent=graphql_gateway`) · `source_key=group_subastas_wholesale`. |
| (d) **RESULTADO** | edges vivos = **3977** (precio 0/3977 no-NULL); veredicto **543** certificó **27** (snapshot SSR previo; div 0.0, TRUSTWORTHY). |
| (e) **CLI** | `$PY -m pipeline.platform.group_subastas_wholesale` (opcional `--concurrency 1`) |

### 5.2 BCA España — `CDP-ES-00-WYJKTP6S`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | British Car Auctions España, remarketing VO B2B; SPA tras un reto JS de Cloudflare. |
| (b) **SURFACE** | `POST https://es.bca-europe.com/buyer/facetedsearch/GetViewModel?q=&bq=salecountry_exact:ES` (faceted-search ViewModel). **MICRO-ACCIONES:** se ejecuta a través de un **stealth browser JS-executing** (Playwright/camoufox) que pasa el reto Cloudflare (un `curl_cffi` plano recibe 403 "Just a moment..."); la respuesta JSON (`VehicleResults[]`, `TotalVehicles`, `IsUserAnonymous=true`, `CanViewPricing=false`) se captura de la red del browser y se ingiere idempotente. Filtro de coche: `VehicleType ∈ {car, crosscountryvehicle}` (descarta moto/van). Vendedor = `SaleId/SaleName`. |
| (c) **RECETA** | script `scripts/cage_autorola_bca_subastas.py` (member `bca`) · engine `stealth_browser_js_spa` · governor STEALTH (default 0.7, `es.bca-europe.com` no en tabla) · `defense_tier=t2_js_challenge` · `source_group=official_registry` · `kind=plataforma`/`role=platform` · `data_surface=internal_api` (`surface_intent=spa_facetedsearch_viewmodel`, `price_gate=bid_login_gated`) · `source_key=group_subastas_bca`. |
| (d) **RESULTADO** | edges vivos = **1752** (precio 0/1752 no-NULL); 20 vendedores `subasta`. Dentro del veredicto **543** por su pathA (`entity.kind=subasta`). |
| (e) **CLI** | `$PY scripts/cage_autorola_bca_subastas.py --bca <bca_es_full.json>` (slice ya capturado del browser vivo en `bca_es_full.json`). |

### 5.3 Autorola — `CDP-ES-00-RJ109M0T`

| Campo | Valor |
|---|---|
| (a) **QUÉ** | Subastas de remarketing Autorola Group; SPA Angular con JWT anónimo por petición. |
| (b) **SURFACE** | `GET https://old.autorola.es/rest/vehiclesearchenrollment/result?locale=es_ES&offset&limit[&auctionId]` (capa REST pública que el SPA pide tras un **JWT anónimo crudo** por petición; sin login). **MICRO-ACCIONES:** se conduce por **stealth browser JS-executing** que arranca el SPA y obtiene el JWT anónimo; la respuesta (`groups[].vehicleDTOS[]` con `vehicleDTO{headline,details,countryCode,localizedMileage,presentationYear,pictureUrl}` + `auctionId/auctionTitle` + `firstReg`/`sortableMileage`) se captura e ingiere idempotente. Filtro ES: `vehicleDTO.countryCode=='ES'`. Dedup en `enrollId`. `loginRequired=true`/`price=None` → precio NULL. |
| (c) **RECETA** | script `scripts/cage_autorola_bca_subastas.py` (member `autorola`) · engine `stealth_browser_js_spa` · governor STEALTH (default 0.7, `old.autorola.es` no en tabla) · `defense_tier=t1_soft` (SPA cookie-gated + JWT anón; sin WAF duro) · `source_group=official_registry` · `kind=plataforma`/`role=platform` · `data_surface=internal_api` (`surface_intent=spa_rest_vehiclesearch`, `price_gate=bid_login_gated`) · `source_key=group_subastas_autorola`. |
| (d) **RESULTADO** | edges vivos = **1056** (precio 0/1056 no-NULL); 20 vendedores `subasta`. Dentro del veredicto **543** por su pathA. |
| (e) **CLI** | `$PY scripts/cage_autorola_bca_subastas.py --autorola <autorola_es_full.json>` (slice ya capturado en `autorola_es_full.json`). |

> **Nota sobre Autorola/BCA `[VERIFICADO]`.** El doc `docs/architecture/OTHER_GROUPS.md` y la receta
> `subastas_datalayer.md` aún los listan como "GATED, sin capa de datos pública". Ese veredicto
> quedó **obsoleto**: la sonda previa usaba un `curl_cffi` sin JS que no arranca los SPA Angular.
> Conducidos por un stealth browser JS-executing, ambos exponen el stock per-lote ES sin login (el
> precio sigue gateado → NULL). El código (`scripts/cage_autorola_bca_subastas.py`) y la DB viva
> (3 plataformas, 6785 aristas) mandan sobre el `.md` aspiracional. Aristas commiteadas y
> verificadas; entran en el runbook.

---

## 6. Comandos de reproducción/verificación rápida

```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"

# (a) Conteos vivos por grupo (owned == edges == union)
$PY -c "
import psycopg2
c=psycopg2.connect('postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep'); cur=c.cursor()
for label, where in [('chain',\"source_group='chain'\"),('rentacar_vo',\"source_group='rentacar_vo'\"),('subastas',\"kind='subasta' OR (role='platform' AND source_group='official_registry')\")]:
    cur.execute(f'''WITH g AS (SELECT entity_ulid FROM entity WHERE {where})
      SELECT count(DISTINCT x) FROM (
        SELECT v.vehicle_ulid x FROM vehicle v JOIN g ON v.entity_ulid=g.entity_ulid
        UNION SELECT pl.vehicle_ulid FROM platform_listing pl JOIN g ON pl.platform_entity_ulid=g.entity_ulid) u''')
    print(label, cur.fetchone()[0])
"
# -> chain 39201 · rentacar_vo 215 · subastas 6785  (union total 46201, disjunto)

# (b) Re-correr conectores (idempotente, ON CONFLICT = no-op si nada cambió)
$PY -m pipeline.platform.group_vo_chains_wholesale --members flexicar ocasionplus clicars carplus --pages 1000
$PY -m pipeline.platform.group_rentacar_vo_wholesale --member all
$PY -m pipeline.platform.group_subastas_wholesale
$PY scripts/cage_autorola_bca_subastas.py --autorola autorola_es_full.json --bca bca_es_full.json
```

---

## 7. NO validado (fuera del runbook)

No entran: sin veredicto `TRUSTWORTHY` y/o sin conector que escriba aristas vivas confirmado.

| Grupo | Miembro | Estado `[VERIFICADO]` |
|---|---|---|
| rentacar_vo | **Sixt ES** | Sin storefront VO español; negocio "GW" solo en `sixt.de`. Ausente de `entity`. |
| rentacar_vo | **Europcar ES** ("2nd Move") | Ex-flota solo vía plataforma B2B con registro (`b2b.2ndmove.eu`). Cagearla desde el marketplace duplicaría. Ausente como fila propia. |
| rentacar_vo | **Goldcar** | Sitemap = solo páginas de alquiler/app; ex-flota vía 2ndMove B2B. Sin surface propio. |
| vo_chains | **Aurgi, GpsAutos, Crandon** | Citados como futuros `chain`; sin probe de surface ni aristas en DB. |
| subastas | **Allane** (Sixt Leasing) | Remarketer DE-céntrico; sin surface de stock VO ES alcanzable. Ausente de `entity`. |
| subastas | **Aucto** (`aucto.es`) | Connection refused / no alcanzable. Ausente de `entity`. |

> **Desfase veredicto↔DB (declarado, no maquillado).** Los `verification_verdict` 541/542/543
> certifican TRUSTWORTHY a conteos **37319 / 166 / 27** (snapshot 00:37Z). La DB viva creció después
> a **39201 / 215 / 6785** por drenes posteriores commiteados. El delta de conteo de cada grupo
> **no** tiene aún un `verification_verdict` re-persistido a su valor vivo; el runbook reporta el
> conteo certificado como validación formal y el conteo vivo como cross-check `[VERIFICADO]` en DB.
> Acción pendiente: re-emitir el VAM por grupo para cerrar el ledger a los valores vivos.
