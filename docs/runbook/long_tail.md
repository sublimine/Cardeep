# RUNBOOK — LONG-TAIL (own-site harvest, CMS/DMS family multiplier)

> Dominio: **long_tail**. Solo entra lo **validado + funcional**: cada unidad de
> este runbook tiene un `verification_verdict` persistido **TRUSTWORTHY** (cito el
> `id` y el `primary_value`) **y** un conector commiteado que confirmo presente en
> `pipeline/platform/`. Lo aspiracional, no validado o conocido-roto está al final
> bajo **§NO validado (fuera del runbook)**.
>
> Toda cifra cruzada contra la DB viva `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`
> (contenedor `cardeep-pg`, `127.0.0.1:5433->5432`, **UP** verificado) y contra la
> tabla `verification_verdict`. Verificado **2026-06-13**.
>
> ENV: `python C:/Users/elias/AppData/Local/Programs/Python/Python311/python`.
> Code/comandos en inglés; prosa en español. Cero maquillaje.

---

## 0. Qué es el long-tail y cuál es el multiplicador

Más allá de los marketplaces Tier-1 (coches.net, AS24, wallapop, autocasion,
motor.es) y los portales OEM de VO certificado, el inventario vive en la **web
propia de cada dealer** (`www.<dealer>.es`). Rasparlos uno a uno no escala. El
multiplicador es la **familia CMS/DMS**: agrupar dealers por la plataforma que
corre su web y escribir **UNA receta por familia** — cada dealer de esa familia
expone su stock igual, así un parser drena muchos dealers.

**Modelo de propiedad (la mitad long-tail, más simple que un marketplace):** la web
propia del dealer es la fuente PRIMARIA de su stock, **no** un marketplace. Por eso
NO hay arista `platform_listing`: cada coche es `vehicle.entity_ulid = el dealer`.
La propiedad es singular y directa.

**Arquitectura compartida:** las 7 familias replican la espina de
`pipeline.platform.family_dealerk_wholesale` / `coches_net_wholesale` EXACTAMENTE
— mismo governor (choke point por host), misma `GeoResolver`, mismos upserts
idempotentes `ON CONFLICT`, mismos eventos NEW-delta, mismo quórum de conteo VAM,
mismo heartbeat S-HEALTH + breaker. No es un fork: el long-tail fluye por la ÚNICA
arquitectura probada.

---

## 1. Cifras maestras (vivas, cruzadas contra la DB)

### 1.1 Totales own-site (definición global)

`SELECT count(*)` de `vehicle` cuyo `entity` tiene `website` y **sin** arista
`platform_listing`:

| métrica | valor (vivo 2026-06-13) | reconciliación |
|---|---:|---|
| **long-tail own-site cars** (website + owned + no-edge) | **20 165** | — |
| no-website own-site cars (excluidos por diseño) | 26 198 | — |
| total no-edge vehicles | 46 363 | `20 165 + 26 198 = 46 363` ✓ |
| total `vehicle` en DB | 1 482 547 | — |
| con arista `platform_listing` | 1 436 184 | `1 482 547 − 1 436 184 = 46 363` ✓ |

> **Nota de honestidad (la DB manda sobre el doc):** la cifra global creció desde
> los `20 006` que cita `docs/architecture/LONGTAIL_STATUS.md` hasta **20 165**
> (la DB sigue creciendo). El balance por descomposición sigue cerrando exacto, lo
> que confirma que el delta es crecimiento real, no deriva de conteo.

CLI de reproducción:

```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"

# headline own-site total
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid
 WHERE e.website IS NOT NULL AND e.website<>''
   AND NOT EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid)''');print(cur.fetchone())"
# -> (20165,)

# balance check
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 SELECT (SELECT count(*) FROM vehicle),
        (SELECT count(DISTINCT vehicle_ulid) FROM platform_listing),
        (SELECT count(*) FROM vehicle v WHERE NOT EXISTS
          (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid))''');print(cur.fetchone())"
# -> (1482547, 1436184, 46363)
```

### 1.2 Las 7 familias VAM-firmadas (la fila que SÍ entra al runbook)

Cada familia tiene un `verification_verdict` `subject_type='family_slice'`,
`verdict=TRUSTWORTHY`, `divergence=0.0`, con `claim = "distinct (dealer, deep_link)
harvested == family vehicles persisted in DB"`. Estos son los **últimos** verdicts
firmados (`DISTINCT ON (subject_key) … ORDER BY created_at DESC`), leídos en vivo:

| source_key | verdict id | primary_value (cars own-site VAM) | verdict | div | health / breaker |
|---|---:|---:|---|---:|---|
| `family_dealerk_wp` | **606** | **2 270** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_builder_wholesale` | **598** | **1 224** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_generic_custom` | **597** | **1 029** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_dms_vendor_platforms` | **596** | **799** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_cms_wp` | **535** | **518** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_framework_webbuilder` | **525** | **358** | TRUSTWORTHY | 0.0 | healthy / closed |
| `family_unreachable` | **498** | **246** | TRUSTWORTHY | 0.0 | healthy / closed |
| **TOTAL VAM family-slice** | — | **6 444** | — | — | 7/7 healthy, 7/7 closed |

> El `evidence` de cada verdict reza `paths={'db_family_vehicles': N, 'harvested_pairs':
> N, 'cars_ingested_distinct': N}` con los tres iguales y `divergence=0.0` (cero
> tolerancia). `family_framework_webbuilder` usa `cars_caged_distinct` en lugar de
> `cars_ingested_distinct` (misma semántica: 358==358==358).

> **La DB manda — discrepancias con el doc declaradas:** los `primary_value` vivos
> difieren de `LONGTAIL_STATUS.md` (que firmaba dealerk 2 253, builder 1 778,
> generic 1 169, dms 802). Re-firmados al alza tras nuevas pasadas: **dealerk 2 270,
> builder 1 224, generic 1 029, dms 799**. El runbook usa la DB viva, no el rollup.

Las cifras "no-edge def #2" (superset: own-site del dealer incluso en hosts
no-plataforma de terceros) por familia, vivas:

| source_key | members (entity_source) | producing (≥1 own-site car) | no-edge own-site cars (def #2) |
|---|---:|---:|---:|
| `family_dealerk_wp` | 37 | 34 | 2 841 |
| `family_generic_custom` | 10 | 10 | 2 499 |
| `family_builder_wholesale` | 9 | 2 | 1 781 |
| `family_dms_vendor_platforms` | 27 | 22 | 1 691 |
| `family_framework_webbuilder` | 7 | 4 | 680 |
| `family_cms_wp` | 13 | 13 | 599 |
| `family_unreachable` | 1 | 1 | 246 |
| **distinct family-tagged entities** | **104** | — | — |

> Tres conteos legítimos por familia, **nunca conflados**: (1) **VAM harvest slice**
> = pares `(dealer, deep_link)` firmados a 0.0 (tabla §1.2, la cifra fiable); (2)
> **no-edge def #2** = superset (tabla de arriba); (3) **global** 20 165. No son
> intercambiables.

CLI:

```bash
# (1) últimos VAM verdicts por familia
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 SELECT DISTINCT ON (subject_key) id, subject_key, primary_value, verdict, divergence
 FROM verification_verdict WHERE subject_type='family_slice'
 ORDER BY subject_key, created_at DESC''');[print(r) for r in cur.fetchall()]"

# (2) members / producing por familia
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 WITH osv AS (SELECT v.entity_ulid, v.vehicle_ulid FROM vehicle v
   WHERE NOT EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid=v.vehicle_ulid))
 SELECT es.source_key, count(DISTINCT es.entity_ulid) members,
        count(DISTINCT osv.entity_ulid) producing, count(DISTINCT osv.vehicle_ulid) cars
 FROM entity_source es LEFT JOIN osv ON osv.entity_ulid=es.entity_ulid
 WHERE es.source_key LIKE 'family_%' GROUP BY es.source_key ORDER BY es.source_key''');[print(r) for r in cur.fetchall()]"

# (3) health + breaker
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 SELECT sh.source_key, sh.status, sh.consecutive_fails, sb.state
 FROM source_health sh LEFT JOIN source_breaker sb ON sb.source_key=sh.source_key
 WHERE sh.source_key LIKE 'family_%' ORDER BY sh.source_key''');[print(r) for r in cur.fetchall()]"
```

### 1.3 La clasificación de familias (`docs/_longtail_family_ranking.json`)

Ranking re-agregado sobre el set own-site vivo (369 dominios distintos / 413 filas
own-site, tras quitar OEM/Tier-1). **Esta es la unidad que una receta ataca: el
dominio registrable.**

| family | domains | entities served | share |
|---|---:|---:|---:|
| **cms** (WordPress-dominado) | 157 | 179 | 42.5% |
| unreachable | 86 | 91 | 23.3% |
| generic / custom | 73 | 83 | 19.8% |
| **dms** (inventario.pro + motorflash) | 28 | 33 | 7.6% |
| framework (Next/Astro/Nuxt/Angular) | 17 | 18 | 4.6% |
| builder (Wix/Ueni/Google Sites/…) | 8 | 9 | 2.2% |

Subfamilias top: `cms/wordpress` 143/164, `generic/custom` 66/76,
`dms/inventario_pro` 15/19, `dms/motorflash` 11/12, `framework/nextjs` 9/9,
`framework/astro` 5/5. **283/369 dominios reachable; 86 unreachable.**

> **Reconciliación 86 vs 92 (declarada, no maquillada):** el ranking
> (`_longtail_family_ranking.json`, set own-site vivo de 369 dominios) marca **86
> unreachable**; el roster completo de fingerprints (`_longtail_fingerprints.json`,
> 401 registros del probe entero) marca **92 unreachable**. Ambas son reales,
> medidas sobre cortes de población distintos (369 own-site vivo vs 401 probe
> total). El re-test stealth (§3.7) cubrió las 92.

---

## 2. Modelo de configuración común a las 7 familias

Todas las familias comparten estos ejes de receta/config (verificado leyendo cada
`pipeline/platform/family_*.py`):

| eje | valor |
|---|---|
| **kind** del dealer (entity) | `compraventa` / `concesionario_oficial` (ya en DB por discovery; resuelto por host de `website`, touch + stamp familia) |
| **source_group / family key** | el `source_key` ES la familia, no un dealer: `entity_source.source_key = 'family_<X>'`. Constante `FAMILY_KEY` en cada módulo |
| **governor rate-class** | **STEALTH** (default 0.7 req/s, burst 3.0, min-spacing 1.43 s + jitter 0.25 s) — ningún host de familia está en `_HOST_RATE_CLASSES`, así que heredan el default seguro. Bucket **por host**: cada dealer se pacea independiente. (`pipeline/engine/governor.py`) |
| **defense_tier** | **t0_open** para las 6 familias Tier-0 (HTML/JSON SSR servido limpio a `chrome131`, sin WAF/JS). **t1_browser** solo para `family_unreachable` (Chromium real, body-gate ciego al status) |
| **engine / fetch** | `curl_cffi` con `impersonate="chrome131"`, GET, sin proxy/browser/creds (Tier-0). `family_unreachable`: headless Chromium (Playwright sync en thread dedicado vía el seam `asyncio.to_thread` del governor) |
| **ownership** | `vehicle.entity_ulid = el dealer`. **Sin** arista `platform_listing` |
| **recipe artifact** | cada run escribe la `FAMILY_RECIPE` con `write_recipe(FAMILY_KEY, …)` (en `pipeline/platform/_recipes_runtime/`) |
| **VAM** | `subject_type='family_slice'`, `subject_key=FAMILY_KEY`, claim conteo-quórum a `divergence=0.0` |

---

## 3. Las 7 familias — receta, data-layer, micro-acciones, resultado, CLI

### 3.1 `family_dealerk_wp` — DealerK (MotorK) WordPress  — **2 270 cars, verdict 606**

- **(a) Qué es:** stack WordPress + Elementor + plugin "tucoche" (DealerK / MotorK),
  multisite. Markup `vcard-*` **byte-idéntico** entre miembros → UN parser los lee
  todos. 37 members en `entity_source`, 34 productores.
- **(b) Data-layer / micro-acciones:**
  - Engine: `curl_cffi` GET, `impersonate=chrome131`, server-rendered HTML.
  - **Fingerprint (membership):** HTML lleva `dealerk` (spine) **Y** al menos uno de
    `tucoche` o `cdn.dealerk.es/dealer/datafiles/vehicle`.
  - **Listing paths (en orden):** `/coches/segunda-mano/`, `/seminuevos/`, `/coches/`.
  - **Micro-acciones:** (1) resolver dealer en DB por host de `website`; (2) GET del
    primer listing-path que devuelva cards; (3) paginar `?page=1..N` hasta página sin
    cards (o `--max-pages`); (4) por card `<div class="vcard …">` extraer:
    `deep_link` = anchor PDP `…/coches/segunda-mano/…/<id>/`; `listing_ref` = `<id>`
    numérico del path; make/model = `vcard-main-info__make-model`; price =
    `vcard-price__price`; year/km/fuel = `vcard-consumption__title` (`MM/YYYY - KM Km
    - Fuel`); photo = primera imagen `cdn.dealerk.*`.
- **(c) Receta/config:** connector `pipeline/platform/family_dealerk_wholesale.py`;
  `FAMILY_KEY='family_dealerk_wp'`; rate-class STEALTH; defense_tier t0_open;
  kind `compraventa`. `FAMILY_RECIPE` versión 1.
- **(d) Resultado validado:** **2 270** own-site cars; **verdict id 606**,
  TRUSTWORTHY, div 0.0; healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_dealerk_wholesale --from-db --limit 5
  $PY -m pipeline.platform.family_dealerk_wholesale --dealers archiauto.com autochristian.com
  ```

### 3.2 `family_dms_vendor_platforms` — inventario.pro + motorflash — **799 cars, verdict 596**

El multiplicador más limpio (template uniforme por subfamilia). Dos subfamilias, una
receta + un governor + un cage.

- **Subfamilia inventario.pro (15 dealers / 19 entities):**
  - Fingerprint: el asset host `inventario.pro` aparece en cada página.
  - Listing paths: `/coches`, `/coches-ocasion`, `/coches-nuevos`, `/vehiculos`.
    Paginación `?pagina=N`.
  - Detail template: `/coches/<make>/<model>/<numeric_id>` (el `<id>` final = `listing_ref`).
  - Field map: make/model del `titulo_card` o del slug de la URL; price `div.precio`;
    km `span.uk-icon-road`; year `span.uk-icon-calendar-o`; fuel `inventario-icon-fuel`;
    photo `imgs.inventario.pro/*`. SSR, **sin JS**.
  - Seeds verificados: canaauto.es, carsandbikes.es, ftome.com, masmotorcantabria.net,
    eveauto.es, autosniser.es, integralmotion.es, iluscar.com, mobilitycentro.com,
    garciautodelvalles.com, automovilesgabilondo.com, autosocasionalminares.com,
    carmotors99.com, tuokasion.es, bellamachina.es.
- **Subfamilia motorflash (11 dealers / 12 entities):**
  - Fingerprint: la señal `motorflash` (widget de stock; CMS host varía — Drupal/custom).
  - Listing paths: `/coches-ocasion`, `/coches`, `/coches-segunda-mano`, … `?pag=N`.
  - Detail template: `/ficha-vehiculo-ocasion/<slug>/<id>`.
  - Field map vía **hidden inputs** limpios: `marcaVehiculo`, `modeloVehiculo`,
    `precio`, `kilometros`, `mesesAntiguedad` (→ year), photo `images.motorflash.com/*`.
  - Seeds: helmantica.es, grupmibec.com, autoelia.es, movento.es, bmwpremiumselection.es.
- **(c)** connector `family_dms_vendor_platforms__wholesale.py`;
  `FAMILY_KEY='family_dms_vendor_platforms'`; STEALTH; t0_open. 27 members, 22 productores.
- **(d)** **799** cars; **verdict id 596**, TRUSTWORTHY, 0.0; healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_dms_vendor_platforms__wholesale --seeds
  $PY -m pipeline.platform.family_dms_vendor_platforms__wholesale --from-db --limit 8
  $PY -m pipeline.platform.family_dms_vendor_platforms__wholesale --dealers canaauto.es helmantica.es
  ```

### 3.3 `family_cms_wp` — WordPress-dominado (CMS #1) — **518 cars, verdict 535**

La familia más grande (157 dominios / 179 dealers) pero theme-VARIADA. Dos
estrategias en orden por dealer, bajo una receta:

- **STRATEGY A — Vehica REST (el multiplicador limpio):** el plugin "Vehica" expone
  un gateway JSON público de primera parte en **`/wp-json/vehica/v1/cars`** que
  devuelve TODO el inventario en UNA llamada (`resultsCount` + `results[]` con
  `attributes[]`: Marca/Modelo/Año/Kilómetros/Combustible/"Precio al contado").
  Byte-idéntico entre dealers Vehica → un parser, sin JS, sin paginación.
- **STRATEGY B — HTML cards SSR (el volumen):** dealers WP no-Vehica renderizan cards
  bajo un slug de listing. **Ranked slug probe** (frecuencia real medida en la familia):
  `/coches` (229) > `/vehiculos` (49) > `/catalogo` (17) > `/ocasion` (17) >
  `/vehiculos-ocasion` (14) > `/stock` (12) > `/km0` (9) > `/seminuevos` (9) >
  `/coches-segunda-mano` (7) > `/coches-ocasion` (7) … Selector de card por tema vía
  tabla **THEME_OVERRIDE** (p.ej. `ga-car-card`, `sc_cars_item`): añadir un tema es
  una entrada de tabla.
- **(b) Micro-acciones:** (1) resolver dealer por host; (2) probar `/wp-json/vehica/v1/cars`
  → si 200 JSON, parsear `results[]` (FIN); (3) si no, recorrer `LISTING_SLUGS` en orden
  hasta hallar el índice; (4) match del marker de tema → extractores; (5) paginar.
- **(c)** connector `family_cms_wordpress_dominated__wholesale.py`;
  `FAMILY_KEY='family_cms_wp'`; STEALTH; t0_open; 13 members, 13 productores.
- **(d)** run-slice **518** cars; **verdict id 535**, TRUSTWORTHY, 0.0; healthy/closed.
  (Stock own-site de los 13 dealers en DB, def #2: 599.)
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_cms_wordpress_dominated__wholesale \
      --dealers autosraul.com automovilesjfz.com automovileslacanal.com gestiauto.es
  $PY -m pipeline.platform.family_cms_wordpress_dominated__wholesale --from-db --limit 8
  ```

### 3.4 `family_generic_custom` — bespoke own-site — **1 029 cars, verdict 597**

La mitad dura: 83 dealers / 73 dominios sin señal de plataforma compartida. El
multiplicador es **arquitectónico**: UN spine drena N recetas per-dealer registradas
en un `REGISTRY: dict[str, DealerRecipe]` (cada una: `listing_path`, `parser`, modo de
paginación, subfamily). Aun así sobreviven micro-familias (p.ej. **Pymecar**:
carhay.com + autopai.es comparten `parse_pymecar`, cards `img.pymecar.com`).

- **(b) Data-layer:** `curl_cffi` chrome131, SSR HTML; cada `DealerRecipe` define su
  `listing_path` (`/coches-segunda-mano`, `/vehiculos-ocasion/`, `/es/inventario/`,
  `/index.php/es/stock-automoviles`…) y su `parser` dedicado. Paginación por dealer:
  `query` (`?page=N`), `single` (todo en una página), `template` (WP/Joomla `/page/N/`
  o `?start=N`).
- **Dealers registrados (10, todos en DB):** autofesa.com, carhay.com, autopai.es,
  arguelles-automoviles.com, frworldcars.com, csvmotor.com, autocastro.es,
  puntomotortenerife.com, robledauto.com, gupicarauto.es.
- **(c)** connector `family_generic_custom_wholesale.py`;
  `FAMILY_KEY='family_generic_custom'`; STEALTH; t0_open; 10 members, 10 productores.
- **(d)** **1 029** cars; **verdict id 597**, TRUSTWORTHY, 0.0; healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_generic_custom_wholesale --all
  $PY -m pipeline.platform.family_generic_custom_wholesale --dealers autofesa.com carhay.com
  ```

### 3.5 `family_framework_webbuilder` — Next/Astro/Nuxt/Angular SaaS — **358 cars, verdict 525**

Dealers en una SPA JS sobre un dealer-site SaaS compartido. La UI es JS, pero la
plataforma emite DOS superficies SSR sin browser:

- **(b) Data-layer / micro-acciones:**
  - Fingerprint (spine): logo en `firebasestorage.googleapis.com/v0/b/web-builder/*`
    **Y** fotos en `storage.googleapis.com/vehicle-multipost-multimedia/*` (o
    `/vehicles-prd/*`).
  - **Superficie 1 — `sitemap.xml`** (candidatos `/sitemap.xml`, `/sitemap-0.xml`,
    `/sitemap_index.xml`): el inventario COMPLETO, cada `<loc>…-de-segunda-mano-<uuid></loc>`
    (coincide con el `numberOfItems` de la página). La paginación por query-param es
    client-side y NO se usa.
  - **Superficie 2 — JSON-LD `Car`** por PDP: `offers.price` (EUR),
    `mileageFromOdometer.value` (km), `productionDate` (year), `brand`, `model`,
    `name`, `vehicleEngine.fuelType`, `vehicleTransmission` (M/A),
    `vehicleIdentificationNumber` (UUID = `listing_ref`), `image[0]`.
  - Micro-acciones: (1) fingerprint home/listing; (2) drenar sitemap → todas las URLs;
    (3) por PDP parsear el `Car` JSON-LD. UN parser, byte-idéntico en la familia.
  - Verificado live: inmocoches 133, lgautomocion 149, vallolidmotor 54, furgogandia 22
    (sitemap == numberOfItems declarado).
- **(c)** connector `family_framework_next_astro_nuxt_angular__wholesale.py`;
  `FAMILY_KEY='family_framework_webbuilder'`; STEALTH; t0_open; 7 members, 4 productores.
- **(d)** **358** cars; **verdict id 525**, TRUSTWORTHY, 0.0
  (`db_family_vehicles=358 == cars_caged_distinct=358`); healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale \
      --dealers inmocoches.com lgautomocion.com vallolidmotor.es furgogandia.com
  $PY -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale --from-db --limit 6
  ```

### 3.6 `family_builder_wholesale` — Wix/Ueni/Google Sites/BaseKit/Squarespace/Duda — **1 224 cars, verdict 598**

La cola más dura/variada. El multiplicador que SÍ generaliza es la **superficie de
datos estructurados** (schema.org JSON-LD que el builder emite para SEO). Receta
degradada en estrategias ordenadas:

- **Strategy 1 — schema.org `ItemList` de `Vehicle`/`Product`** (listado ueni,
  verificado live en crestanevada.es: `<script id="jsonld-itemlist-listado">` con 24
  `Vehicle` por página: brand/model/year/km/fuel/transmission/price + PDP url con id
  numérico final; `?pagina=N` acumulativo → drena todo, ~2 450 cars).
- **Strategy 2 — bloques `Vehicle`/`Product` JSON-LD sueltos** (cualquier builder que
  los emita).
- **Strategy 3 — heurística SSR card** (anchors con precio; fallback honesto).
- **(b)** `curl_cffi` chrome131, SSR; `LISTING_PATHS` propios del builder; paginación
  `?pagina=N` (`DEFAULT_MAX_PAGES=120`). Miembros sin superficie machine-readable (Wix
  warmupData JS, Squarespace/BaseKit SSR vacío, Google Sites contacto) se registran
  HONESTAMENTE como reachable-pero-sin-inventario-SSR (no se fabrican).
- **(c)** connector `family_builder_wix_ueni_google_sites_basekit__wholesale.py`;
  `FAMILY_KEY='family_builder_wholesale'`; STEALTH; t0_open; 9 members, 2 productores
  (la cola es genuinamente de bajo rendimiento, como predijo el mapa de familias).
- **(d)** **1 224** cars; **verdict id 598**, TRUSTWORTHY, 0.0; healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale \
      --dealers crestanevada.es majadahondamotor.es bugasgroup.com
  $PY -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale --from-fingerprints --limit 12
  ```

### 3.7 `family_unreachable` — Tier-1 browser-only — **246 cars, verdict 498**

La mitad más dura: dominios marcados dead/walled por el probe Tier-0 (DNS muerto,
403/202/503, timeout). La señal definitoria — y la única receta — es la escalada que
`pipeline/engine/fetch.py` documenta: **Tier-1 = Chromium real juzgado por el BODY
RENDERIZADO, no por el status HTTP**, porque un miembro sirve un listado completo bajo
un status 403 honeypot. Ese **body-gate ciego al status** es el multiplicador.

- **Miembro recuperado (único, ya cageado):** **hrmotor.com** (HR Motor, Lleida 25 /
  Madrid 28). Home: HTTP 403 + 287 KB de HTML real. Listing `/coches-segunda-mano/`:
  HTTP 200, 772 KB, cards `vercoche` byte-uniformes, paginación `/page/N/`. El
  body-gate lo lee; el status-gate (y el probe original) lo tiraba.
- **(b)** Engine: headless Chromium (Playwright sync en thread dedicado, UA Chrome
  coherente + locale ES), driven a través del seam `asyncio.to_thread` del governor.
  Parser `parse_hrmotor`: card `<div class="vercoche …">`, `deep_link` via
  `data-href="…/coches-segunda-mano/…-<hash12+>/"`, `listing_ref` = hash final.
  `DEFAULT_MAX_PAGES=6` (proof-slice; el connector soporta el drain completo).
- **(c)** connector `family_unreachable_wholesale.py`;
  `FAMILY_KEY='family_unreachable'`; STEALTH; **defense_tier t1_browser**; 1 member,
  1 productor.
- **(d)** **246** own-site cars (verificado directo en DB: `family_unreachable`
  own-site no-edge = 246); **verdict id 498**, TRUSTWORTHY, 0.0; healthy/closed.
- **(e) CLI:**
  ```bash
  $PY -m pipeline.platform.family_unreachable_wholesale --dealers hrmotor.com
  $PY -m pipeline.platform.family_unreachable_wholesale --all
  ```

#### Re-test stealth de las 92 unreachable (auditado, `docs/architecture/UNREACHABLE_STEALTH_RETEST.md`)

Las 92 (= 86 own-site vivo + extra del roster de fingerprints) se RE-TESTARON con
camoufox 135 (anti-detect Firefox, locale ES) en gate de **body renderizado ciego al
status**. Resultado DB-verificado:

| bucket | n | significado |
|---|---:|---|
| **recovered-free (caged)** | **1** | hrmotor.com — sirve stock own-site bajo stealth; 246 cars en DB |
| dead — NXDOMAIN | 39 | DNS no resuelve (ningún browser lo arregla) |
| dead — hard wall | 50 | resuelve pero nunca pasa el body-gate (CF 107-byte 403, DataDome, SSL roto, timeouts) |
| resolves, no own-site listing | 2 | avolo.net (HTTP 500), renaultleioa.es (0 precios own-site) |
| **total** | **92** | **genuinely dead = 89** (39 NXDOMAIN + 50 hard wall) |

**Verdict:** el stealth CONFIRMA el veredicto original para 91 de 92. El probe no-JS
NO mentía aquí. Cero recuperaciones nuevas; `family_unreachable` queda en **1 dealer
/ 246 cars** (DB-live).

---

## 4. Re-verificación rápida (un comando por cosa)

```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"

# contenedor vivo
docker ps --format '{{.Names}} {{.Status}}' | grep cardeep-pg

# los 7 VAM verdicts firmados (ids 606/598/597/596/535/525/498)
$PY -c "import psycopg2;c=psycopg2.connect('$DSN');cur=c.cursor();cur.execute('''
 SELECT DISTINCT ON (subject_key) id, subject_key, primary_value, verdict, divergence
 FROM verification_verdict WHERE subject_type='family_slice'
 ORDER BY subject_key, created_at DESC''');[print(r) for r in cur.fetchall()]"

# regenerar el ranking de familias (artefactos de evidencia)
$PY scripts/longtail_fingerprint.py   # probe domains -> _longtail_fingerprints.json
$PY scripts/longtail_refine.py        # recover unreachables + expanded signatures
$PY scripts/unreachable_stealth_reprobe.py   # re-test stealth de las 92
$PY scripts/unreachable_db_verify.py         # tally DB del re-test
```

---

## 5. NO validado (fuera del runbook) — declarado, no maquillado

Esto NO entra al runbook porque carece de un `verification_verdict` TRUSTWORTHY o de
un conector que confirme su funcionamiento sobre la superficie reclamada:

1. **Las 89 unreachable genuinamente muertas/walled** (39 NXDOMAIN + 50 hard wall) —
   confirmadas no-recuperables por camoufox stealth (§3.7). Negocios muertos / dominios
   expirados / Cloudflare-DataDome-SSL roto. **No hay receta porque no hay superficie.**
2. **avolo.net** (HTTP 500, shell de error) y **renaultleioa.es** (renderiza pero 0
   precios own-site; sus links de vehículo apuntan off-site a agregadores). Resuelven
   pero **sin stock own-site que cagear** — excluidos honestamente.
3. **9 828 cars own-site sin familia asignada** (de los 20 165 globales, 10 178 están
   family-tagged; el resto en entities con website **sin** receta de familia). Es
   long-tail real **pendiente** de asignar a una familia — no validado como cosechado.
4. **Roster generic excluido honestamente** (en docstring de `family_generic_custom`):
   homepages de marca OEM/global (ford.com, maserati.com, honda.es, polestar.com,
   lancia.es, mopar.eu, copart.es), delegadores cuyo stock vive en otro connector
   (es.renew.auto, quadis.es, concesionarios.seat, lexusauto.es, yomovo.es), shells
   JS sin cards SSR (automotordursan.com, automovilesroel.es, promosale.es,
   grupoadarsa.com, stylecarcanarias.com), y hosts parked/thin. Construir receta para
   un shell JS o una homepage de marca **fabricaría propiedad** → se saltan, no se fingen.
5. **Miembros builder sin superficie machine-readable** (Wix warmupData, Squarespace/
   BaseKit SSR vacío, Google Sites contacto): reachable-pero-sin-inventario-SSR.
   Registrados honestamente; **no producen** (de 9 members builder, solo 2 productores).
6. **grupogamboa.com, setienherra.es** (inventario.pro): comparten template pero
   devolvieron cert errors; probable misma familia, **no confirmados** como cosechados.

---

> **Cierre de honestidad:** todas las cifras de este runbook son vivas de `cardeep-pg
> :5433` a 2026-06-13, cruzadas contra `verification_verdict` (ids citados). Donde la
> DB discrepó del rollup `LONGTAIL_STATUS.md`, **gana la DB** y el delta está declarado
> inline (§1.1, §1.2). Lo no validado vive en §5, nunca disfrazado de cosechado.
