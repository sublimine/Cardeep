# COUNTRY-PACK-CONTRACT — El contrato del country-pack
> El contrato único y consolidado: **las cosas EXACTAS que un país nuevo debe aportar** para que el motor genérico lo cubra. Síntesis Ola 2 de los 10 átomos-review de etapa (Ola 1). Sitúa en el funnel en `BOOTSTRAPPED`: el [Dossier de País](COVER-NEW-COUNTRY.md) (KNOW_COUNTRY) se **deriva** en este pack; el motor (etapas `stages/01..10`) lo **consume**. Doctrina madre: [`00-MASTER.md`](00-MASTER.md) · blindaje: [`ANTI-DRIFT-HARDENING.md`](ANTI-DRIFT-HARDENING.md).

## Índice
- [0 · Cómo leer este contrato](#0--cómo-leer-este-contrato)
- [1 · La espina dorsal — el hallazgo que obliga este contrato](#1--la-espina-dorsal--el-hallazgo-que-obliga-este-contrato)
- [2 · Las 8 piezas transversales (la columna vertebral del pack)](#2--las-8-piezas-transversales-la-columna-vertebral-del-pack)
- [3 · El contrato por etapa (qué aporta el país)](#3--el-contrato-por-etapa-qué-aporta-el-país)
- [4 · Forma física del pack — `countries/<CC>/`](#4--forma-física-del-pack--countriescc)
- [5 · Checklist de validación — la compuerta de `cover(CC)`](#5--checklist-de-validación--la-compuerta-de-covercc)
- [6 · Open items — lo que el pack NO puede cerrar solo (de-cegado del motor)](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor)
- [7 · Invariante de cierre — byte-identidad ES](#7--invariante-de-cierre--byte-identidad-es)

---

## 0 · Cómo leer este contrato

**Etiquetas de evidencia (BLINDAJE — obligatorias, sin excepción):**
- `[VERIFIED path:line]` — leído **de primera mano en el código vivo** esta sesión (2026-06-27). La espina dorsal (§1) es 100% de primera mano.
- `[W1 path:line]` — costura reportada por el **átomo-review Ola 1** (los `wave1-stages/*.json`, ellos mismos `[VERIFIED]` por su autor); **citada, no re-leída** esta sesión. Se eleva a `[VERIFIED]` al re-tocar ese archivo.
- `[ASSUMED]` — sin verificar, declarado como tal. Jamás se presenta como `[VERIFIED]`.

**El reparto (invariante de la biblia, [`00-MASTER.md` §«Las 10 etapas»](00-MASTER.md)):** el **motor** (maquinaria: union-find, MSE, delta, API, schedulers, `cover(CC)`) es **invariante**; el **pack** es **profundo y 100% a medida** del país. Este documento es el contrato del **pack**, no del motor.

**Honestidad cruda (mandato):** un diseño roto **no se transcribe como hecho**. Donde una costura es un **hueco real del motor** (no una simple parametrización del pack), se marca **open item con causa** en [§6](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor). El pack es **necesario pero no suficiente** hasta que esos open items (de-cegado del motor) estén cerrados.

---

## 1 · La espina dorsal — el hallazgo que obliga este contrato

**El hallazgo transversal, confirmado por los 10 átomos-review y re-verificado de primera mano aquí:** `country_code` se enhebró en el **ESQUEMA** (`0052` + `0053`) y en el **prefijo `cdp_code`** (paramétrico en `codes.py`), pero **NO en la lógica** del pipeline / serving / orquestación. **Por debajo del esquema, el motor sigue siendo country-BLIND.** El piloto DE probó que el esquema **coexiste**; lo que falta es de-cegar la **lógica**.

**Verificado de primera mano (2026-06-27):**

| Hecho | Evidencia |
|---|---|
| El esquema YA lleva país | `[VERIFIED migrations/0052_country.sql]` añade `country_code` a geo-backbone + `entity` (FASE-0, aditivo, `DEFAULT 'ES'`). `[VERIFIED migrations/0053_country_onboarding.sql]` promueve la PK geo a `(country_code, code)` y reescribe las 6 FKs a compuestas. |
| El prefijo `cdp_code` YA es paramétrico | `[VERIFIED services/api/codes.py:53]` `mint_code` → `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`, con `country_code=DEFAULT_COUNTRY`. `[VERIFIED codes.py:24]` `DEFAULT_COUNTRY="ES"`. |
| …pero el **write-site** de descubrimiento es ciego | `[VERIFIED pipeline/discover.py:97-107]` el `INSERT INTO entity` **omite la columna `country_code`** (cae a `'ES'` por DEFAULT) y la llamada a `cdp_code(...)` **omite `country_code`** (mintea `CDP-ES-`). |
| …el **resolver geo** es ciego | `[VERIFIED pipeline/geo.py:151-159]` `GeoResolver.load(conn)` hace `SELECT code,name FROM geo_province` / `geo_municipality` **sin filtro `country_code` y sin parámetro** → tras un 2º país, ES-`28` y DE-`28` colisionan en el índice → mintea provincia (y `cdp_code`) **errónea e irreversible**. |
| …la **identidad de vehículo** es ciega | `[VERIFIED pipeline/identity/cluster_vehicles.py:397]` `block_key=(make,model,year,km,province)` — sin país ni moneda → false-merge transfronterizo latente. |
| …la **autoridad de teléfono** es ES-clavada | `[VERIFIED pipeline/identity/phone_es.py:30-49]` `+34` / `len==9` / `_VALID_LEADING` fijos; `phone_match_key(raw)` **no acepta `country_code`** → un teléfono no-ES devuelve `None` (señal fuerte descartada). |
| …el **gate G1** clava ES | `[VERIFIED pipeline/complete.py:89]` `_CDP_CODE_RE=^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$`; `[VERIFIED complete.py:73]` `_PROVINCE_RE` = rango INE `01-52`. Rechaza todo `CDP-{CC}-` ajeno (el «6º blocker»). |
| …los **mints de plataforma** clavan ES | `[VERIFIED]` 31 conectores `pipeline/platform/*` hacen `return f"CDP-ES-…"`, **0 importan `mint_code`** (63 ficheros contienen el literal `CDP-ES-`; 80 en todo `pipeline/services/scripts`). El docstring `codes.py:46-51` que afirma «`CDP-{country}-` exists in exactly one place» es **FALSO en la práctica**. |
| …el **governor** clava hosts ES | `[VERIFIED pipeline/engine/governor.py:102]` `_HOST_RATE_CLASSES` cablea `web.gw.coches.net`, `searchapi.gw.milanuncios.com`, … dentro del motor. |

> **Consecuencia para el contrato:** cada pieza del pack existe **porque** hay una costura ES-clavada que la exige. El pack es el conjunto de datos/perfiles que, inyectados, hacen que el motor de-cegado produzca el país nuevo **sin tocar un byte de ES**. El de-cegado en sí (cambios de motor, una vez) vive en [§6](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor); su garantía mecánica, en [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md).

---

## 2 · Las 8 piezas transversales (la columna vertebral del pack)

Las costuras de las 10 etapas colapsan en **8 piezas**. Todo lo demás del pack es una instancia de una de éstas. Cada pieza: qué aporta exactamente · qué etapas alimenta · la costura del motor que cierra · su forma física.

| # | Pieza | Qué aporta exactamente | Alimenta | Costura del motor que cierra | Forma física |
|---|-------|------------------------|----------|------------------------------|--------------|
| **1** | **`country_code` ISO** | El ISO-3166 **alpha-2** (≠ a los tenants ya activos). Es la **dimensión más externa** de todo estrato, clave de bloque, lock y agregado. | 1–10 | `[VERIFIED codes.py:24]` `DEFAULT_COUNTRY="ES"`; `[VERIFIED discover.py:97-107]` INSERT omite la columna → todo cae a `'ES'`. | `country.toml: country_code` |
| **2** | **Árbol geo + anchos de código** | Backbone L1 (provincia/región/Bundesland) + capa intermedia opcional + LAU/municipio con **código oficial** (INE `2+5`, AGS `8`, INSEE `5`, ISTAT `6`); **predicado de ancho/prefijo** (¿`left2==prov`?); centroides lat/lon; gazetteer CP→muni; alias provincia/región; `KNN_MAX_DISTANCE_KM`; perfil de normalización (fold ASCII vs transliteración no-Latina); etiqueta **admin-L1** (CCAA-equiv) `NOT NULL`. | 1,3,4,5,6,7,8 | `[VERIFIED geo.py:151-159]` `load()` sin filtro/param país; `[VERIFIED complete.py:73]` `_PROVINCE_RE` `01-52`; `[VERIFIED 0053]` PK `(country_code,code)`. | `countries/<CC>/geo/` (backbone, centroides, gazetteer, alias) + `country.toml` (validador de subdivisión) |
| **3** | **Roster de plataformas + recetas** | La **lista de plataformas** que operan en el país (cuáles de las formas conocidas — AS24, marketplace, OEM-VO, cadenas, subastas — existen + las **nativas**) y, por plataforma, su **receta** anclada al dominio del país (`base_url` + `url_template` + `field_map` + `defense_tier`); tabla **host→rate-class**; prioridades `route-around`. | 2,3 | `[VERIFIED governor.py:102]` `_HOST_RATE_CLASSES` hosts ES; `[W1 source_fallback.py:75]` `DEFAULT_PRIORITIES` claves ES; `[W1]` 31 mints `CDP-ES-`. | `countries/<CC>/recipes/ + _tier1/ + _platforms/` (YAML VERIFIED, tras el harness) |
| **4** | **Adaptadores de discovery** | Los **módulos** adaptadores del país (registro mercantil → BORME/Handelsregister/…, localizadores OEM, marketplaces, capa POI-geo bbox+filtro, dorks idioma, extractores phone/reg-id); entradas del registro `ADAPTERS`; entradas `DISCOVERY_REGISTRY` (vector + `cadence_hours` + `orthogonal` + `requires_env`). | 1,9 | `[VERIFIED discover.py:118]` `ADAPTERS[source_key]()` sin noción de país; `[W1 discover_schedule.py:65]` `DISCOVERY_REGISTRY` 5 vectores ES; `[W1 scheduler.py:150]` `REGISTRY` dict ES. | `pipeline/sources/<src>.py` + `pipeline/ops/registry/<cc>.py` |
| **5** | **Ancla de denominador + listas ortogonales** | **Censo externo** `census/<name>.csv` con clave `(region_code, segment, n_external)` + roll-up nacional + `SOURCE.md` de provenance que etiqueta cada cifra `[MEDIDO]`/`[ESTIMADO DECLARADO]` (construido por un **mecanismo distinto** al scrape); mapeo `source_key → bucket ortogonal` (las 7 clases: GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG); taxonomía `kind → segment`; **predicado de punto-venta canónico** (qué kinds cuentan, gate de inventario, exclusiones). | 1,7 | `[W1 0048:39,58]` estratos MSE sin `country_code`; `[W1 lists.py:27]` `_EXACT` ES → el resto cae a `MKT`; `[VERIFIED 0056]` `v_servable_dealer` **0 lectores**. | `countries/<CC>/census/` + `taxonomy.yaml` + filas `discovery_list(country_code,…)` |
| **6** | **Autoridad de teléfono/dirección** | **Plan de numeración**: `calling_code` + conjunto de longitudes nacionales válidas + regla de dígito-líder → la **clave E.164**; léxico de **sufijos societarios** (sl/sa… ; gmbh/ag… ; sarl/sas… ; srl/spa…); lista de **tokens de cadena**/multi-sucursal; **autoridad de id fiscal** (CIF→VAT y su token-prefijo); léxico de **tipos de vía** para el guard de dirección. | 4 | `[VERIFIED phone_es.py:30-49]` `+34`/`len9`/`_VALID_LEADING`, `phone_match_key(raw)` sin param país; `[W1 cluster_dealers.py:117 + cross_source_dedup.py:196]` sufijos/cadenas ES duplicados. | `IdentityLocale(cc)` / bloque `identity` en `country.toml` |
| **7** | **Bandas de precio/moneda + locale/idioma** | `currency` (por vehículo); `PRICE_MAX` por moneda (KM/year son **físicos**, se heredan); `LocaleProfile` (separador miles/decimal, símbolo/código de divisa, formato de fecha, idioma); mapas de enum `fuel_map`/`transmission_map` → **canónico neutro** (PETROL/DIESEL/EV/HYBRID, AUTOMATIC/MANUAL); léxico stock/conteo; extensión de alias de marca local (opcional). | 3,5 | `[W1 price_sanity.py:49]` `PRICE_MAX=5M` ES/EUR; `[W1 recipe_extract_web.py:28]` hints en castellano; `[VERIFIED cluster_vehicles.py:397]` block-key sin currency/país. | `countries/<CC>/locale.yaml` + `brands.yaml` |
| **8** | **Prefijo `CDP-{CC}-`** | El **segmento país** de cada `cdp_code`. Derivado de `country_code`; debe existir en **UN solo sitio** (`mint_code`). El país no «aporta» un literal — aporta el `country_code` (pieza 1) y exige que **todo coder** lo enrute por `mint_code`. | 1,2,4,10 | `[VERIFIED complete.py:89]` `_CDP_CODE_RE=^CDP-ES-`; `[VERIFIED]` 31 mints `return f"CDP-ES-`, 0 importan `mint_code`; docstring `codes.py:46-51` «exactly one place» **FALSO**. | derivado; gate por `mint_code(country_code=CC)` (ver [OI-1](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor)) |

> **Mapa al Dossier:** piezas 1·8 ← Dossier §A; pieza 2 ← §B; piezas 3·(egress) ← §D/§G; pieza 4 ← §C/§D; pieza 5 ← §C/§E; pieza 6 ← §A/§F; pieza 7 ← §A/§F. (Dossier A–G en [`COVER-NEW-COUNTRY.md`](COVER-NEW-COUNTRY.md).)

---

## 3 · El contrato por etapa (qué aporta el país)

Una tabla por etapa. Columna **Aporta** = el ítem exacto del pack (elevado, no verbatim). **Costura** = la costura del motor que lo exige (ancla verificada). **Pieza** = la transversal de [§2](#2--las-8-piezas-transversales-la-columna-vertebral-del-pack). Detalle por etapa: `stages/NN-*.md`.

### Etapa 1 · Descubrir → [`stages/01-discover.md`](stages/01-discover.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Módulos adaptadores del país (registro mercantil, OEM-loc, marketplaces, POI-geo, dorks, extractores phone/reg-id) | `[VERIFIED discover.py:118]` `ADAPTERS[source_key]()` country-blind | 4 |
| Entradas del registro `ADAPTERS` (`source_key`→clase) y de `DISCOVERY_REGISTRY` (vector+cadence+orthogonal+requires_env) | `[W1 discover.py:48 / discover_schedule.py:65]` | 4 |
| Mapeo de taxonomía MSE (`lists._EXACT` + `bucket_for`) para los `source_key` del país | `[W1 lists.py:27-45]` claves desconocidas caen a `MKT` (excluidas del MSE) | 5 |
| Filas geo (`geo_province/comarca/municipality` con `country_code=CC`) + alias + gazetteer + validador de rango | `[VERIFIED geo.py:151-159]` `load()` sin scope país | 2 |
| CSV censo/denominador `countries/<CC>/census/<name>.csv` | `[W1 triangulation.py:27]` `CENSUS_CSV_NAME='dirce_cnae451.csv'` ES | 5 |
| Dicts `categoría→kind` + convención geo (`postcode→L1`) que cada adaptador aplica | `[W1 overture.py:227/osm.py:77/…]` regla `postcode[:2]==prov` copiada inline en 5+ | 2 |
| Perfil de identidad local (normalizador teléfono E.164, validador id registral) | `[VERIFIED phone_es.py]` ES-clavado | 6 |

### Etapa 2 · Scrapear → [`stages/02-scrape.md`](stages/02-scrape.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Roster de plataformas del país (conocidas presentes + nativas), cada una con conector que reusa el `_core` | `[W1]` 31 mints `CDP-ES-`, 0 usan `mint_code` | 3 |
| Receta por plataforma anclada al dominio (base_url, url_template, field_map, defense_tier) | `[W1 recipe.py:20-40]` `AS24_RECIPE` ES-shaped | 3 |
| Tabla host→rate-class (STEALTH vs JSON_API) | `[VERIFIED governor.py:102]` `_HOST_RATE_CLASSES` hosts ES | 3 |
| Locale de fingerprint (`Accept-Language` + geoip) coherente con la IP de egress | `[W1 fingerprints.py:46]` `es-ES,…` clavado | 7 |
| Filtro de país para cosecha de proxies libres | `[W1 free_proxies.py:26]` `_COUNTRY='ES'` | 1 |
| Prioridades route-around de los marketplaces del país | `[W1 source_fallback.py:75]` `DEFAULT_PRIORITIES` claves ES | 3 |
| Pack de palabras del idioma (hints stock/conteo) | `[W1 recipe_extract_web.py:28]` keywords en castellano | 7 |
| Set de recetas YAML VERIFIED commiteado bajo `countries/<CC>/` (tras el harness) | `[W1]` | 3 |
| Taxonomía provincia/región para el segmento `{prov}` del `cdp_code` | `[VERIFIED complete.py:73]` `_PROVINCE_RE` `01-52` | 2 |

### Etapa 3 · Extraer/Normalizar → [`stages/03-extract.md`](stages/03-extract.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Plantillas de receta por fuente (selectores deterministas: base_url/impersonate/timeout, pagination, parsing.container_path + field_map) | `[W1 recipe_extractors.py:245]` `engine` vocabulario abierto → no ejecutable | 3 |
| `LocaleProfile`: sep miles/decimal, símbolo/código divisa, formato fecha, idioma | `[W1 dealerprobe.py:127]` parser EU re-implementado ad-hoc; peldaño web sin parser EU | 7 |
| Léxicos de idioma (stock hints, palabra de conteo, blocklist marketplaces) | `[W1 recipe_extract_web.py:28-33]` | 7 |
| Dicts enum→canónico neutro (`fuel_map`, `transmission_map`) | `[W1 coches_net_wholesale.py:130 + ingest.py:101]` `'Automático'` almacenado verbatim | 7 |
| Tabla de alias de marca calibrada a la distribución del país | `[W1 make_normalizer.py:9-13]` `_CANON` «grounded in LIVE ES data» | 7 |
| Calibración de `PRICE_MAX` (techo del mercado nacional); km/year heredados | `[W1 price_sanity.py:49]` | 7 |
| Adaptador geo de extracción (regla CP→región; el parser emite crudo, etapa 04 resuelve) | `[W1 autocasion_wholesale.py:195]` rango INE `01..52` dentro del parser | 2 |
| (Opcional, hoy €0) modelo + gramática GBNF capa-2 por idioma | `[W1]` hoy vacío | 7 |
| Segmento de prefijo `CDP-<CC>-` + mapeo superficie→`kind` | `[VERIFIED complete.py:89]` | 8 |

### Etapa 4 · Identidad → [`stages/04-identity.md`](stages/04-identity.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Plan de numeración telefónica (calling_code + longitudes + líder → clave E.164 **completa**) | `[VERIFIED phone_es.py:30-49]` `+34`/`len9`/`_VALID_LEADING`, sin param país | 6 |
| Léxico de sufijos societarios a recortar antes de name-keying | `[W1 cluster_dealers.py:117 + cross_source_dedup.py:196]` listas ES duplicadas | 6 |
| Lista de tokens de cadena/multi-sucursal (nunca name-merge entre POS distintos) | `[W1 cross_source_dedup.py:163 + build_residual_namemuni_dedup.py:69]` formas divergentes | 6 |
| Autoridad de id fiscal nacional (id fuerte de dedup + token-prefijo: CIF→VAT) | `[W1]` rama id de `canonical_key` | 6 |
| Reglas de normalización de dirección (léxico tipos-de-vía por locale) | `[W1]` hoy solo alnum-strip naïf | 6 |
| `country_code` para el prefijo `CDP-{CC}-` (único sitio del literal) | `[VERIFIED]` 80 ficheros con `CDP-ES-` | 8 |
| **NO** aporta `municipality_code`: lo entrega la etapa Geo (los bordes de identidad consumen el código opaco) | — (separación geo↔identidad) | 2 |

### Etapa 5 · Vehículo → [`stages/05-vehicle.md`](stages/05-vehicle.md)
> **Pack ≈ mínimo:** el vehículo es casi universal. Cero código de dedup/delta/evento por país.

| Aporta | Costura | Pieza |
|--------|---------|-------|
| Código de unidad geo en `entity.province_code` (mismo grano del guard «misma unidad geo» de Signal B) | `[VERIFIED cluster_vehicles.py:397]` `block_key` country-blind | 2 |
| `vehicle.currency` (los conectores la fijan; necesaria para que ±2% y `PRICE_CHANGE` comparen dentro de una moneda) | `[VERIFIED cluster_vehicles.py:397]` block-key sin currency; `[W1 delta.py:319]` `PRICE_CHANGE` sin moneda | 7 |
| Calibración de `PRICE_MAX` por moneda si difiere (KM_MAX/year físicos, se heredan) | `[W1 price_sanity.py:49]` | 7 |
| (Opcional) extensión de `_CANON` con grafías/alias locales — el fallback verbatim ya es seguro | `[W1 make_normalizer.py:19-40]` | 7 |

### Etapa 6 · Geo → [`stages/06-geo.md`](stages/06-geo.md)
> **El pack más grande.** El corazón de la pieza 2.

| Aporta | Costura | Pieza |
|--------|---------|-------|
| `country_code` ISO-3166 alpha-2 (**debe** ser ≠ ES; el piloto lo fuerza) | `[VERIFIED 0053]` colisión PK probada (DE-`28` ↔ ES-`28`) | 1 |
| Manifiesto de mapeo de niveles (qué nivel fuente → province/comarca[null]/municipality) | `[W1 load_geo.py:26]` backbone ES en un script único | 2 |
| Backbone: L1 oficial + etiqueta región (CCAA-equiv) + capa intermedia opc. + lista LAU con código oficial | `[W1 geo.py:153,157]` `SELECT` sin `WHERE country_code` | 2 |
| Predicado de forma del código (¿prefijo `left2==prov`?) materializado como CHECK gated `country_code<>'CC' OR <pred>` | `[VERIFIED complete.py:73]` `_PROVINCE_RE` ES; `[W1]` muni `char(2)` asume ancho-2 | 2 |
| Centroides lat/lon por municipio (KNN reverse-geocode) | `[W1 geocode.py:80-87]` índice clavado por `province_code` solo | 2 |
| Gazetteer CP→municipio + (opc.) localidades→municipio | `[W1 geo.py:46-48]` `_GAZETTEER_PATH` Nomenclátor INE clavado | 2 |
| Tabla de alias región/provincia (islas, exónimos, bilingües) | `[W1 geo.py:61-73]` `_PROVINCE_ALIASES` 100% ES | 2 |
| `KNN_MAX_DISTANCE_KM` calibrado al tamaño típico de municipio | `[W1 geocode.py:49]` `30.0` km ES | 2 |
| Perfil de normalización (fold ASCII Latino vs transliteración no-Latino) | `[W1 geo.py:51-53]` `encode('ascii','ignore')` destruye griego/cirílico | 2 |
| Regex de limpieza de sufijo país en texto libre (`, Spain`/`, España`-equiv) | `[W1]` | 2 |
| Etiquetas región L1 (`ccaa_code`/`name`-equiv), `NOT NULL` en `geo_province` | `[W1 geo.py:419-420]` `ccaa_*` filtra a la salida genérica | 2 |

### Etapa 7 · Calidad/Sello → [`stages/07-quality-seal.md`](stages/07-quality-seal.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Ancla censal externa `census/<name>.csv` `(region_code,segment,n_external)` + roll-up nacional + `SOURCE.md` con cada cifra `[MEDIDO]`/`[ESTIMADO DECLARADO]` | `[W1 triangulation.py:27]` filename ES; `[W1 0048]` sin `country_code` | 5 |
| Mapeo `source_key → bucket ortogonal` de las fuentes **reales** del país (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG) | `[W1 lists.py:27-74]` enumera fuentes ES; heurísticas incluyen `'oficial'`/`'mercedes'` | 5 |
| Taxonomía `dealer-kind → segment` (el enum `kind` del país colapsado a segmentos) | `[W1 capture.py:19-46]` `DEALER_KINDS` 9 ES + mapa hardcodeado | 5 |
| Partición de región + códigos (vocabulario de la dimensión-1 del estrato) | `[W1 0048:39,58]` `province_code char(2)` modela INE | 2 |
| **Predicado de punto-venta canónico** (qué kinds cuentan, gate de inventario, exclusiones) | `[VERIFIED 0056]` `v_servable_dealer` definido, **0 lectores** → ver [OI-7](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor) | 5 |
| (Opcional) parámetros del techo registral legacy (ratio CNAE, totales asociación, splits por región) — un país puede **omitirlo** y fiarse de MSE + censo | `[W1 load_denominator_provincia.py:38]` `assert len(rows)==52` ES | 5 |

### Etapa 8 · Servir → [`stages/08-serve.md`](stages/08-serve.md)
> **Pack ≈ mínimo y puramente declarativo.** El binario de la API es idéntico en todos los países; el país es solo una **dimensión**. Cero código aportado.

| Aporta | Costura | Pieza |
|--------|---------|-------|
| `country_code` — el **único** valor nuevo que la capa serve necesita (todo lo demás son datos que las etapas previas ya produjeron bajo ese código) | `[W1 0046:18-23]` `servable_entity` (37 cols) no proyecta `country_code` → [OI-9](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor) | 1 |
| Una fila de `country_registry` `{country_code, admin1_label, display_name}` (ES=«Comunidad Autónoma», DE=«Bundesland», FR=«Région») | `[W1 geo.py:419-420]` `ccaa_*` ES filtrado a la forma genérica | 2 |
| (Aserción, no dato) que existen filas geo+entity para `CC` | `[VERIFIED 0053]` | 1,2 |
| `currency` **NO** se exige al pack: ya es por-vehículo en el contrato (heredada de extracción) | `[W1 entities.py:132]` | 7 |

### Etapa 9 · Orquestar/Observar → [`stages/09-orchestrate.md`](stages/09-orchestrate.md)
| Aporta | Costura | Pieza |
|--------|---------|-------|
| Harvest registry del país (`source_key → SourceEntry(module, extra_args)`) | `[W1 scheduler.py:150]` `REGISTRY` dict ES mezcla motor+pack | 4 |
| Discovery vector registry (qué vectores + cadencia + env-gate; p.ej. BORME 24h vs Handelsregister) | `[W1 discover_schedule.py:65]` 5 vectores ES (borme_cnae, dork_municipal 8.132 muni) | 4 |
| Filas semilla de `source_health` (`harvest_interval_hours` + `is_tier1`) vía migración de onboarding | `[W1 0004:24-31]` `source_health` sin `country_code` (namespace global) | 4,5 |
| Designación Tier-1 por fuente (severidad critical vs warning) | `[W1]` `source_health.is_tier1` | 4 |
| (Solo si aislamiento por host/VPS) namespace de `lock_key` de los productores del país | `[W1 scheduler.py:913]` advisory locks singleton de host | 4 |
| Cadencias nacionales específicas de los vectores + gates de coste | `[W1 discover_schedule.py:65-84]` | 4 |

### Etapa 10 · Cerebro/Automatización → [`stages/10-automation.md`](stages/10-automation.md)
> El **manifiesto** que nombra y enlaza las 8 piezas: `countries/<CC>/country.toml`.

| Aporta | Costura | Pieza |
|--------|---------|-------|
| `countries/<CC>/country.toml` (**nuevo**, hoy inexistente): `country_code`; validador de subdivisión (regex/rango que reemplaza `_PROVINCE_RE`); override de national-kinds; léxico `kind` local→canónico; override de SLA por tier; referencia al backbone geo; hints de tier de receta | `[VERIFIED complete.py:73]` `_PROVINCE_RE`; `[VERIFIED complete.py:83-85]` `_NATIONAL_KINDS` | 1,2,8 |
| Golden-set del clasificador de `kind` por país (semilla capa-2 + eval del bus) | `[W1]` `detect_classifier_drift` | 5 |
| Lista-semilla de fuentes (`source_health`/discovery rows iniciales con `harvest_interval_hours`) | `[W1]` | 4 |
| Árbol `countries/<CC>/` (recipes, `census/`, subdivisions seed) | `[W1]` | 3,5 |
| Seed del backbone geo de subdivisiones cargado vía adapter sobre `(country_code, code)` | `[VERIFIED 0053]` | 2 |
| Prompts/hints de decisión específicos del país para el bus de Claude (denominador nacional, ambigüedades geo) | `[W1]` | 5 |
| (Opcional) overrides de cadencia por-CC de los 8 jobs (cuando el self-tuning esté activo) | `[W1]` | 4 |

---

## 4 · Forma física del pack — `countries/<CC>/`

El pack es un **árbol versionado** + filas DB sembradas por una migración de onboarding + módulos Python de adaptadores. Estructura objetivo:

```
countries/<CC>/
  country.toml              # PIEZA 1+8: country_code; validador subdivisión; national_kinds; kind→canónico; SLA; refs
  geo/                      # PIEZA 2
    backbone.csv            #   L1 + región-label + LAU con código oficial (INE 2+5 / AGS 8 / INSEE 5 / ISTAT 6)
    centroides.csv          #   lat/lon por municipio (KNN)
    gazetteer.csv           #   CP→municipio (+ opc. localidades→municipio)
    aliases.csv             #   alias provincia/región (islas, exónimos, bilingües)
  locale.yaml               # PIEZA 7: sep miles/decimal, símbolo/código divisa, fecha, idioma, PRICE_MAX, fuel/transmission, stock/count
  brands.yaml               # PIEZA 7: extensión _CANON local (opcional)
  identity.toml             # PIEZA 6: plan teléfono, sufijos societarios, tokens cadena, autoridad id fiscal, léxico tipos-vía
  recipes/                  # PIEZA 3: receta por-dealer (post-harness, VERIFIED)
    _tier1/  _platforms/    #   recetas Tier-1 runtime + por plataforma
  census/                   # PIEZA 5
    <name>.csv              #   (region_code, segment, n_external) + roll-up nacional
    SOURCE.md               #   provenance: cada cifra [MEDIDO] | [ESTIMADO DECLARADO]
  taxonomy.yaml             # PIEZA 5: DEALER_KINDS, kind→segment, predicado punto-venta canónico

pipeline/sources/<src>.py            # PIEZA 4: módulos adaptadores discovery del país
pipeline/ops/registry/<cc>.py        # PIEZA 4: harvest + discovery registries del país (≠ del motor)
migrations/00NN_onboard_<cc>.sql     # filas semilla source_health/discovery_list/country_registry + backbone load
```

> **`registry/<cc>.py` y el split motor↔pack:** el átomo-review 09 prescribe extraer el `REGISTRY` Python a `pipeline/ops/registry/__init__.py` con `get_harvest_registry(country)` / `active_countries()`, moviendo las ~50 entradas ES **verbatim** a `registry/es.py`. Con `active_countries()==['ES']` el comportamiento es **byte-idéntico**. `[W1 scheduler.py:150]`

---

## 5 · Checklist de validación — la compuerta de `cover(CC)`

**Regla dura (mandato, ANTI-DRIFT regla de oro «prohibido adivinar»):** un **pack incompleto NO arranca `IN_COVERAGE`**. La máquina de estados `cover(CC)` (`REGISTERED → KNOW_COUNTRY → BOOTSTRAPPED → IN_COVERAGE → SEALED`, [`COVER-NEW-COUNTRY.md`](COVER-NEW-COUNTRY.md)) **no transiciona de `BOOTSTRAPPED` a `IN_COVERAGE`** hasta que **todas** las casillas estén verdes. Casilla roja → el motor **escala** (`decision_request` → Claude), **no improvisa**. Cada casilla es un **predicado verificable** (query/assert), no una opinión.

**Por pieza (gate de completitud del pack):**

- **Pieza 1 · `country_code`**
  - [ ] `country.toml.country_code` casa `^[A-Z]{2}$` y **no** está en `active_countries()`.
- **Pieza 2 · Árbol geo + anchos**
  - [ ] `SELECT count(*) FROM geo_province WHERE country_code=:cc` `> 0` **Y** `geo_municipality` `> 0`.
  - [ ] Ninguna fila `CC` viola el CHECK de ancho/prefijo declarado (`country.toml` subdivisión).
  - [ ] Todo `geo_province.code` de `CC` casa el regex de subdivisión declarado (reemplazo de `_PROVINCE_RE`).
  - [ ] Existen centroides para `≥` el umbral de municipios objetivo (KNN operativo).
- **Pieza 3 · Roster + recetas**
  - [ ] `≥1` receta **VERIFIED** commiteada bajo `countries/<CC>/recipes/` que **pasó el harness**.
  - [ ] Toda entrada host→rate-class del roster está presente en el pack (no en el motor).
- **Pieza 4 · Adaptadores discovery**
  - [ ] `get_discovery_registry(CC)` no vacío; cada vector lleva `cadence_hours` + `orthogonal` + `requires_env`.
  - [ ] Cada `source_key` del roster resuelve a una clase en `ADAPTERS`.
  - [ ] Filas semilla `source_health(country_code=CC)` con `harvest_interval_hours` + `is_tier1` sembradas.
- **Pieza 5 · Denominador + ortogonales**
  - [ ] `countries/<CC>/census/<name>.csv` existe, esquema `(region_code,segment,n_external)` válido, con roll-up nacional.
  - [ ] `SOURCE.md` etiqueta **cada** cifra `[MEDIDO]` o `[ESTIMADO DECLARADO]` (cero cifra sin provenance).
  - [ ] **≥3 listas ortogonales** identificadas; **todo** `source_key` del roster mapea a una de las 7 clases (**ninguno** cae a `MKT` por defecto).
  - [ ] Predicado de punto-venta canónico declarado en `taxonomy.yaml` (qué kinds cuentan + gate de inventario).
- **Pieza 6 · Autoridad teléfono/dirección**
  - [ ] Plan de numeración (`calling_code`, longitudes, líder), léxico de sufijos societarios, tokens de cadena, autoridad de id fiscal y léxico de tipos-de-vía presentes para `CC`.
- **Pieza 7 · Precio/moneda + locale**
  - [ ] `locale.yaml`: `currency`, `PRICE_MAX` (por moneda), separadores, símbolo, formato fecha, idioma.
  - [ ] `fuel_map`/`transmission_map` mapean a los enums **neutros** (PETROL/DIESEL/EV/HYBRID, AUTOMATIC/MANUAL).
  - [ ] Léxico stock/conteo en el idioma del país.
- **Pieza 8 · Prefijo `CDP-{CC}-`**
  - [ ] Una entidad-sonda mintada con `mint_code(country_code=CC,…)` empieza por `CDP-{CC}-` **Y** pasa G1 (`complete.py`). *(Depende de [OI-1](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor) — de-cegado del motor.)*

**Gate de regresión (cruza todas las piezas):**
- [ ] **Byte-identidad ES:** añadir el pack **no cambia un solo byte** de la salida ES. `test_country_golden` + Ferrari + CI en **verde**.
- [ ] **Country-proof:** el golden cross-country ([`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md)) está **verde** — ningún cluster servido mezcla `>1 country_code`.

**Veredicto del gate:** `BOOTSTRAPPED` se sella ⇔ **todas** las casillas de pieza están verdes **Y** ambos gates de regresión pasan. Hueco con **causa declarada** permitido (queda como open item rastreado); **hueco silencioso, no** → `cover(CC)` se detiene en `BOOTSTRAPPED` y abre `decision_request`.

---

## 6 · Open items — lo que el pack NO puede cerrar solo (de-cegado del motor)

**Honestidad cruda:** estos son **huecos del motor**, no contenido del pack. Son **precondiciones**: aunque el pack esté 100% completo, un 2º país no corre correctamente hasta cerrarlos. Cada uno es un **fix de motor UNA vez** (no por-país) y está diseñado para dejar ES **byte-idéntico**. El piloto DE probó que el **esquema** coexiste (`0052/0053`); esto es de-cegar la **lógica**.

| ID | Open item | Evidencia | Causa | Cierre (motor, una vez) | Bloquea |
|----|-----------|-----------|-------|-------------------------|---------|
| **OI-1** | G1 clava el prefijo ES (el «6º blocker») | `[VERIFIED complete.py:89]` `_CDP_CODE_RE=^CDP-ES-` | Rechaza todo `CDP-{CC}-`; vigilado por `xfail(strict)` | Ensanchar a `^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` (superset estricto) + quitar el xfail | Casilla pieza 8 |
| **OI-2** | 31 mints de plataforma bypasean `mint_code` | `[VERIFIED]` 31 `return f"CDP-ES-`, 0 importan `mint_code`; docstring `codes.py:46-51` **FALSO** | `cover(DE)` vía un platform connector acuñaría `CDP-ES-` → corrupción silenciosa de identidad | Enrutar los 63 ficheros por `mint_code(country_code=campaign.CC)`; ES queda byte-idéntico (`mint_code` default ES) | Identidad del país #2 |
| **OI-3** | Resolver/geocoder geo country-blind | `[VERIFIED geo.py:151-159]` sin filtro/param; `[W1 geocode.py:80-87]` índice por `province_code` solo | ES-`28` ↔ DE-`28` se funden → provincia/`cdp_code` errónea e **irreversible** | `WHERE country_code=$1` + instancia por-país + índice `(country_code, province_code)` | Toda resolución geo |
| **OI-4** | `discover._upsert` omite `country_code` | `[VERIFIED discover.py:97-107]` INSERT sin la columna; `cdp_code()` sin el arg | Toda entidad descubierta cae a `'ES'` por DEFAULT, mintea `CDP-ES-` | Añadir la columna al INSERT + `SourceAdapter.country_code` enhebrado a `cdp_code()` | Todo descubrimiento no-ES |
| **OI-5** | `_PROVINCE_RE` clava INE `01-52` | `[VERIFIED complete.py:73]` | Rechaza subdivisiones válidas no-ES | Inyectar el validador desde `country.toml` (resuelto por `country_of_cdp`) | Casilla pieza 2 |
| **OI-6** | Esquema MSE sin dimensión país | `[W1 0048:39,58]` `province_code char(2)`, sin `country_code`; `[W1 0048:82-106]` `v_exhaustiveness_seal` toma 1 build global | Dos países colapsan en un estrato; el último build oculta el sello del otro | Migración aditiva (espejo `0052`): `ADD country_code` + estrato más externo + `DISTINCT ON (country_code)` | Sello multi-país |
| **OI-7** | Numerador no canónico (**núcleo realmente sin resolver**) | `[VERIFIED 0056]` `v_servable_dealer` definido, **0 lectores**; `[W1]` stats/geo/seal usan 3 numeradores distintos (~54.6k / unverified-excl / ~18.3k) | «Coverage = num/den» se computa contra numeradores **distintos** → toda cobertura es denominador-honesto pero **numerador-ambiguo** | Cablear `v_servable_dealer` como el **único** numerador/scope (registral + MSE + conteo público); hacer el predicado parámetro del pack | Honestidad del % de cobertura |
| **OI-8** | `photo_hash` sin ruta de escritura | `[VERIFIED]` 0 writers (INSERT/REFRESH/backfill), 4 refs totales | pHash strong-key + `PHOTO_CHANGE` **inertes** → dedup fuerte limitado a VIN-exact (over-count ~131.8K) | Añadir `photo_hash` a INSERT/REFRESH + writer de backfill gateado por governor (€0) | Plan pHash country-agnóstico |
| **OI-9** | Superficie servida country-blind | `[W1 0046:18-23]` `servable_entity` (37 cols) no proyecta `country_code`; `[W1 geo.py:229,292,352]` rutas con `province_code` desnudo; `[W1 stats.py]` 4 agregados sin filtro país | Tras el 2º país, las vistas servidas mezclan ES+DE → regresión de **corrección** | `CREATE OR REPLACE VIEW servable_entity` (+`country_code`) + `AND country_code=$cc` en rutas/agregados; default `'ES'` | Serving multi-país |
| **OI-10** | Tablas de orquestación en namespace global + zombie de silencio | `[W1 0004:24-31]` `source_health` sin `country_code`; `[W1 silence_watchdog.py:174]` dispara `:silence` y **nada lo resuelve** (~7 zombies) | No se puede scopear un productor a un país; alertas de silencio nunca cierran (observabilidad rota en **todo** país) | `ADD country_code DEFAULT 'ES'` (aditivo) + `resolve_recovered_silence_alerts()` cada ciclo | Orquestación/observabilidad multi-país |
| **OI-11** | Costuras de **entorno** (no de país) | `[W1 build_particular_dedup.py:38 / capture.py:17 / migrate.py:15]` DSN hardcodeado sin `os.environ` | Bloquea correr la cadena contra otra DB (p.ej. dry-run `:5434`) para un tenant | `DSN = os.environ.get('CARDEEP_DSN', …)` (espejo de los scripts hermanos) | dry-run/onboarding por tenant |

> **Relación con la garantía mecánica:** OI-3 (geo) y el false-merge de identidad son exactamente el vector que [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md) eleva de «checklist que se pudre» a **invariante mecánico** (`COUNT(DISTINCT country_code)=1` por cluster, golden cross-country en CI). El de-cegado (estos OIs) es el **fix**; el invariante es el **guard** que impide que la ceguera reaparezca.

---

## 7 · Invariante de cierre — byte-identidad ES

**El contrato entero descansa sobre una garantía:** ni una sola pieza del pack ni un solo open item de [§6](#6--open-items--lo-que-el-pack-no-puede-cerrar-solo-de-cegado-del-motor) altera **un byte** de la salida ES.

- `[VERIFIED codes.py:24,53]` `DEFAULT_COUNTRY="ES"` + `mint_code → f"CDP-{country_code}-…"` → con default ES, salida idéntica al histórico `CDP-ES-`.
- `[VERIFIED 0052]` aditivo (`DEFAULT 'ES'`); `[VERIFIED 0053]` el swap de PK es un **relabel 1:1** (toda fila viva es ES: `entity` no-ES `= 0`, `geo_province = 52`, `geo_municipality = 8.132`, todas ES).
- El gate del golden (`test_country_golden`) **pinea** la byte-identidad y bloquea el merge ante cualquier regresión (ANTI-DRIFT §1.6).

**ES no es un caso especial: es el primer pack explícito.** «Tomar lo que funciona y está VERIFICADO → generalizar → luego mejorar; cero pérdida de lo construido» ([`00-MASTER.md` §Doctrina de onboarding](00-MASTER.md)). Este contrato es la forma de esa doctrina: el país nuevo entra como **otra ejecución**, derivando su pack del Dossier, sin reescribir lo probado.

---
> **Cómo encaja en el funnel:** [`README.md`](README.md) (entrada) → [`COVER-NEW-COUNTRY.md`](COVER-NEW-COUNTRY.md) `KNOW_COUNTRY` (Dossier A–G) → **este contrato** `BOOTSTRAPPED` (deriva+valida el pack) → `stages/01..10` `IN_COVERAGE` (el motor lo consume) → [`stages/07-quality-seal.md`](stages/07-quality-seal.md) `SEALED`. Garantía mecánica de la dimensión país: [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md).
