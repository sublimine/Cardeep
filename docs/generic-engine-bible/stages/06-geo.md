# Etapa 6 · Geo — Biblia

> Estado adversarial: **NEEDS_REWORK** (el inquisidor falla `holds=false`: el esquema físico NO es paramétrico por país — los anchos `CHAR(2)/CHAR(5)` están soldados y el *identity-path* de normalización colapsa nombres no-Latinos). Fuente: Wave 1 (cada cita es `path:línea` verificada contra el código). **Stack vivo CAÍDO:** toda cifra DB es punto-en-el-tiempo (no re-verificada en esta pasada); el código SÍ se leyó línea a línea.
>
> **Capítulo v2 PROFUNDO (2026-06-27):** se conserva la estructura v1 íntegra y se añade [Sub-proyectos institucionales (360 por faceta)](#sub-proyectos) — los **27** sub-proyectos átomo-a-átomo (deep-spec a→f + ficha costura/fix/adversarial/sellado/NEXT-LEVEL) que cierran las raíces A–H. Toda cita `path:línea` es `[VERIFIED]` contra el código; las cifras DB son punto-en-el-tiempo (stack caído).

Navegación: [Misión](#misión) · [Lo que existe HOY](#lo-que-existe-hoy-verificado) · [Motor](#motor-invariante-reusado-byte-idéntico-por-país) · [Pack por país](#pack-por-país) · [Costuras → fix](#costuras-es-hardcoded--fix) · [Diseño genérico A→Z](#diseño-genérico-az) · [Onboarding](#onboarding-de-país-nuevo) · [Sellado](#sellado--verificación-multi-vía--rollback) · [Veredicto adversarial](#veredicto-adversarial-roturas--resolución) · [Sub-proyectos 360](#sub-proyectos) · [Nivel inalcanzable](#mejoras-a-nivel-inalcanzable-eur0-priorizadas) · [Riesgos](#riesgos--open-items)

---

## Misión

Resolver **dónde** está cada punto de venta, de forma country-proof: dado un texto sucio (`"Talleres García, Alcorcón, Madrid"`) o un par `(lat, lon)`, emitir el **código administrativo oficial** del país (`municipality_code`, `province_code`) o **confesar el hueco** — nunca inventar. El árbol administrativo (país → provincia → comarca[opcional] → municipio) es el esqueleto sobre el que se agrega el inventario y se sella la cobertura nacional.

La doctrina rectora, transversal a todo el motor geo: **"mejor un hueco que una mentira"** — toda resolución ambigua devuelve `None`, jamás un código fabricado [VERIFICADO `pipeline/geo.py:301-314` doctrina de rechazo por ambigüedad].

El norte del mandato: el motor geo **no es de España**. España es la primera ejecución que lo endurece. Cada país aporta un **pack profundo y a medida** (su árbol, sus centroides, sus alias, su perfil de normalización); la maquinaria se reusa byte-idéntica.

---

## Lo que existe HOY (verificado)

**Backbone administrativo de 3 niveles (esquema canónico):**
- `geo_province` — PK `code CHAR(2)`, `name`, `ccaa_code CHAR(2) NOT NULL`, `ccaa_name TEXT NOT NULL` [VERIFICADO `migrations/0001_geo.sql:4-9`].
- `geo_comarca` — `id BIGINT IDENTITY`, `province_code CHAR(2) FK`, `UNIQUE(province_code, name)`; capa **opcional** [VERIFICADO `migrations/0001_geo.sql:11-16`].
- `geo_municipality` — PK `code CHAR(5)`, `province_code CHAR(2) FK`, `comarca_id BIGINT` **nullable**, `lat/lon DOUBLE PRECISION` [VERIFICADO `migrations/0001_geo.sql:18-24`].
- Invariante de prefijo INE: `CONSTRAINT municipality_province_prefix CHECK (left(code,2)=province_code)` [VERIFICADO `migrations/0001_geo.sql:26`].
- `entity.province_code CHAR(2) FK`, `entity.municipality_code CHAR(5) FK`, `entity.comarca_id BIGINT FK` [VERIFICADO `migrations/0002_entities.sql:13-15`].
- Cifras DB (punto-en-el-tiempo, Wave 1, **stack caído — no re-verificado**): `geo_province=52`, `geo_comarca=323`, `geo_municipality=8132`, `8117/8132` municipios con `lat NOT NULL`.

**Dimensión país (0052/0053) — el esquema ya conoce `country_code`, la lógica NO:**
- `country_code CHAR(2) NOT NULL DEFAULT 'ES'` añadido a `geo_province/geo_comarca/geo_municipality/entity`; el DEFAULT rellena toda fila existente como ES [VERIFICADO `migrations/0052_country.sql:49-54`].
- PK compuesta `(country_code, code)` en `geo_province` y `geo_municipality`; 6 FK reescritas a compuestas `(country_code, col)` con `MATCH SIMPLE` [VERIFICADO `migrations/0053_country_onboarding.sql:64-104`]; entre las FK reescritas están `denominator_estimate.province_code` y `organization.hq_province_code` [VERIFICADO `migrations/0053_country_onboarding.sql:60-62`].
- El invariante de prefijo dejó de ser global: gated `CHECK (country_code <> 'ES' OR left(code,2)=province_code)` [VERIFICADO `migrations/0053_country_onboarding.sql:166-168`]; espejo en `entity` [VERIFICADO `migrations/0053_country_onboarding.sql:170-174`].

**Resolver textual (`GeoResolver`):**
- Cascada nombre→código: normalización → clave token-ordenada → exacto → fuzzy (rapidfuzz, guardas de subconjunto de tokens y longitud) → gazetteer Nomenclátor INE [VERIFICADO `pipeline/geo.py:129-314`; `load:150-169`].
- `_norm` = `NFKD` + `encode("ascii","ignore")` + minúsculas [VERIFICADO `pipeline/geo.py:51-53`].
- `_PROVINCE_ALIASES` = diccionario 100% ES (`menorca→07`, `gipuzkoa→20`, `orense→32`, …) [VERIFICADO `pipeline/geo.py:61-73`].
- Gazetteer de localidades hardcodeado a `data/geo/nomenclator_entidades_ine.csv`; ausencia es **no-fatal** (fuzzy sigue) [VERIFICADO `pipeline/geo.py:46-48,94-96`].

**Geocoders espaciales (`pipeline/geocode.py`):**
- `ProvinceGeocoder` (lat/lon→provincia por centroide de `entity`) [VERIFICADO `pipeline/geocode.py:70-100`].
- `MunicipalityGeocoder` (KNN intra-provincia desde centroides de `geo_municipality`, umbral `KNN_MAX_DISTANCE_KM=30.0`) [VERIFICADO `pipeline/geocode.py:49,106-152`].
- `PostcodeIndex` (CP→municipio; CP ambiguo → `None`) y `_NOMENCLATOR_PATH` ES [VERIFICADO `pipeline/geocode.py:51-53,205-260`].
- Matemática: haversine + aproximación equirectangular para el argmin [VERIFICADO `pipeline/geocode.py:59-67,96-99`].

**Minteo de identidad (`services/api/codes.py`):**
- `mint_code` = `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`; el país vive **solo en el prefijo** [VERIFICADO `services/api/codes.py:44-53`].
- `canonical_key` (preimagen de dedup) es **country-blind** por diseño: acepta `country_code` por simetría pero NO lo usa [VERIFICADO `services/api/codes.py:56-65,92-97`].
- `DEFAULT_COUNTRY="ES"` propagado a todo coder → salida ES byte-idéntica [VERIFICADO `services/api/codes.py:24`].

**Harness de pilotaje 2º país (`scripts/pilot_country.py`):**
- `dry-run / seed / verify / revert`, exige 0053 aplicada, prueba coexistencia `(DE,'28')`+`(ES,'28')` y ES byte-idéntico [VERIFICADO `scripts/pilot_country.py:76-127,242-302`].

**Certificado de cobertura (serving):**
- `/geo/exhaustiveness` sirve la vista `v_exhaustiveness_seal` (MSE capture-recapture): `coverage_lower` con CI + `sealed`; **honesto por construcción** — un estrato fino reporta cobertura cerca de 0 y `sealed=false`, nunca un 100% fabricado [VERIFICADO `services/api/routers/geo.py:147-221`].

---

## Motor (invariante, reusado byte-idéntico por país)

Lo que NO cambia entre países — la "física" del motor geo:

1. **Topología canónica de 3 tablas** `geo_province → geo_comarca[opcional] → geo_municipality`, con PK compuesta `(country_code, code)` y FK compuestas. La capa comarca es opcional (`comarca_id` nullable) → un backbone de 2 niveles es válido de fábrica [VERIFICADO `migrations/0001_geo.sql:22`, `migrations/0053_country_onboarding.sql:64-104`].
2. **Algoritmo de la cascada del resolver:** normalizar → clave token-ordenada → exacto → fuzzy subconjunto-de-tokens → WRatio con guardas → gazetteer. Country-agnóstico: solo cambian los DATOS indexados, no la lógica [VERIFICADO `pipeline/geo.py:209-314`].
3. **Matemática de geocodificación:** haversine + equirectangular para argmin, KNN intra-nivel-1, rechazo por umbral de distancia y por ambigüedad [VERIFICADO `pipeline/geocode.py:59-67,154-194`].
4. **Doctrina `PostcodeIndex`:** CP→leaf; cualquier CP que mapea a >1 leaf devuelve `None` [VERIFICADO `pipeline/geocode.py:243-260`].
5. **Contrato de minteo:** país solo en el prefijo `CDP-{cc}-`; `canonical_key` country-blind → el mismo dealer en 2 países comparte clave de dedup y difiere solo en el prefijo [VERIFICADO `services/api/codes.py:44-65`].
6. **Doctrina "mejor un hueco que una mentira":** transversal a resolver, geocoder y gazetteer.
7. **Disciplina de datos:** append-only, idempotencia por `ON CONFLICT (country_code, code)`, escalera `dry-run → golden → Ferrari → CI`.
8. **Harness de pilotaje reversible** como contrato de aceptación de cualquier país.
9. **Proyección de identidad ES-default:** `country_code DEFAULT 'ES'` + override explícito → todo call-site sin tocar produce salida ES byte-idéntica (patrón `codes.py`/`paths.py`).

> **Honestidad cruda (núcleo del veredicto):** el punto 1 dice "topología canónica reusable", PERO el *tipo y ancho* de la columna `code` **NO** es invariante hoy: `CHAR(2)/CHAR(5)` solo alberga el esquema INE de España. La afirmación "esquema de 3 tablas idéntico para todo país" del diseño original es **FALSA** para DE/IT/PT/FR-DOM (ver [Veredicto](#raíz-a--ancho-de-código-soldado-la-rotura-keystone)). El invariante real, una vez aplicado el fix, es la **topología + el algoritmo**, con el `code` como `VARCHAR` opaco cuyo ancho lo declara el pack.

---

## Pack por país

Lo que cada país DEBE aportar para esta etapa (contrato profundo, no config fina):

| # | Aporte del pack | Equivalente ES | Verificación |
|---|---|---|---|
| 1 | `country_code` ISO-3166 alpha-2 (`!= ES`; el piloto lo fuerza) | `ES` | `scripts/pilot_country.py` |
| 2 | **Tipo/ancho del `code`** (longitud en bytes del código de municipio y provincia) | INE 2+5 | **omitido por el diseño original — keystone, ver Veredicto Raíz A** |
| 3 | Manifiesto de mapeo de niveles (GeoNames ADM1/2/3/4 u OSM `admin_level` 4/6/8 → province/comarca[nullable]/municipality) | INE 1:1 | — |
| 4 | Dataset del backbone: nivel-1 + etiqueta de región (equiv. CCAA) + capa intermedia opcional + lista LAU/municipios con código oficial | xlsx INE + provincias/CCAA hardcodeadas | `scripts/load_geo.py:26-70` |
| 5 | Predicado de forma del código (¿prefijo `left2=prov` sí/no?) materializado como `CHECK` gated `country_code<>'<CC>' OR <pred>` | `left(code,2)=province_code` | `migrations/0053_country_onboarding.sql:166-168` |
| 6 | Dataset de centroides lat/lon por municipio (KNN reverse-geocode) | `seed_geo_centroides.py` | `scripts/seed_geo_centroides.py` |
| 7 | Gazetteer CP→municipio (si hay fuente libre) + **formato de CP del país** | Nomenclátor INE | `pipeline/geocode.py:205-260` |
| 8 | Gazetteer localidades→municipio (opcional; mejora cobertura del resolver) | Nomenclátor INE | `pipeline/geo.py:76-126` |
| 9 | Tabla de alias de región/provincia que la normalización no salva (islas, exónimos, bilingües) | `_PROVINCE_ALIASES` | `pipeline/geo.py:61-73` |
| 10 | **Perfil de normalización** (fold ASCII para Latino; transliteración previa CC0 para no-Latino) — aplica también al *identity-path* | `_norm`/`codes.py:_normalize` ASCII | **identity-path omitido — ver Veredicto Raíz B** |
| 11 | Umbral `KNN_MAX_DISTANCE_KM` calibrado al tamaño típico de municipio | `30.0` | `pipeline/geocode.py:49` |
| 12 | Regex de limpieza de sufijo de país en texto libre (equiv. `", Spain"`) | curado | — |
| 13 | **Pack del validador G1:** predicado de provincia per-país + regex `cdp_code` de segmento ensanchado + `_NATIONAL_KINDS` per-país | `_PROVINCE_RE` 01-52, `^CDP-ES-([0-9]{2})-` | **omitido — ver Veredicto Raíz D** |

---

## Costuras ES-hardcoded → fix

Inventario completo. La columna **Origen** distingue lo que el diseño original ya marcó (`design`) de lo que el inquisidor **añadió** porque el diseño lo omitió (`verdict+`) — esta distinción es la razón del `NEEDS_REWORK`.

| Location | Issue | Fix | Origen |
|---|---|---|---|
| `0001_geo.sql:5,19,7` · `0002_entities.sql:13-14` | `code CHAR(2)/CHAR(5)`, `province_code CHAR(2)`, `municipality_code CHAR(5)`, `ccaa_code CHAR(2)` — **soldados al ancho INE**. AGS-DE=8, ISTAT-muni=6/prov=3, freguesia-PT=6, FR-DOM=3 → `value too long` | Migración additiva `code/…→VARCHAR(n)`; el pack declara el ancho. Para ES (valores llenos, sin padding) es byte-idéntico | **verdict+** |
| `services/api/codes.py:29-32` (`_normalize`) | `encode("ascii","ignore")` en el **identity-path**: CJK/cirílico/griego → `''` → `canonical_key` colapsada → `cdp_code` colisionado e **INMUTABLE**; `ß` cae (no decompone) | Transliteración CC0 (unidecode/ICU) **antes** del fold, según el `GeoProfile`; ES/DE-fold Latino byte-idéntico | **verdict+** |
| `pipeline/geo.py:51-53` (`_norm`) | Igual que arriba, en el resolver | Perfil de normalización per-país | design |
| `pipeline/geo.py:153,157` (`GeoResolver.load`) | 2 `SELECT … FROM geo_province/geo_municipality` **sin** `WHERE country_code` → tras 0053 mezcla ES+DE en un índice; `province_code('Madrid')` contamina | `load(conn, country_code=DEFAULT_COUNTRY)` con `WHERE country_code=$1`; resolver pasa a instancia-por-país | design |
| `pipeline/geo.py:61-73` (`_PROVINCE_ALIASES`) | Alias 100% ES hardcodeados en el módulo | Mover a `GeoProfile` por país; ES = perfil por defecto | design |
| `pipeline/geo.py:46-48` · `pipeline/geocode.py:51-53` | Ruta única al Nomenclátor INE ES | Resolver ruta por `country_code` (`data/<cc>/geo/gazetteer.csv`); ausencia = no-fatal | design |
| `pipeline/geocode.py:49` (`KNN_MAX_DISTANCE_KM`) | `30.0` calibrado a ES | Trasladar el umbral al `GeoProfile`; futuro auto-calibrar al p99 | design |
| `pipeline/geocode.py:78-87,129-152` (`Province/MunicipalityGeocoder.load`) | `SELECT … sin country_code`; índice clavado por `province_code` solo → ES-28 y DE-28 se funden en un bucket | `load(conn, country_code)` con `WHERE country_code=$1`; índice por `(country_code, province_code)` | design |
| `pipeline/geocode.py:205-260` (`PostcodeIndex.load`) | Loader CSV `load(path=_NOMENCLATOR_PATH)` con **ruta ES hardcodeada** (no es query DB); emite `municipio_id` 5-dígitos en espacio-ES, sin dimensión país | Fuente de CP per-país en el pack (`data/<cc>/geo/`) + formato de CP del país; el código emitido viaja con su `country_code` | **verdict+** (los otros 2 geocoders sí estaban en design) |
| `scripts/seed_geo_centroides.py:70-72,96-99` | `fetch WHERE code=ANY(::char(5)[])` y `UPDATE … WHERE code=$3` **sin** `country_code` → `(ES,'28001')` y `(DE,'28001')`: el UPDATE pisa AMBAS filas | `--country`, `AND country_code=$x` en fetch y UPDATE; CSV de centroides del pack | design |
| `scripts/geo_backfill.py:67-77` · `scripts/backfill_municipality_geo.py:33-35,58` | `SELECT … FROM entity WHERE municipality_code IS NULL` sin `country_code`, contra geocoder country-blind | `AND country_code=$1` + geocoder country-scoped; iterar por país | design |
| `migrations/0018_comarca.sql:30-31` (`entity_set_comarca()`) | Trigger `SELECT m.comarca_id … WHERE m.code=NEW.municipality_code` **sin** `country_code` → una entity DE/MX hereda el `comarca_id` del municipio ES homónimo. No corregido por ninguna migración posterior | Migración additiva `CREATE OR REPLACE` con `AND m.country_code=NEW.country_code`; byte-idéntico ES | design |
| `services/api/routers/geo.py:370,388-389` | `geo_province WHERE code=$1` ambiguo post-0053; JOINs `ON m.code=e.municipality_code` sin pais → cruzan países y multiplican | `country_code` en path/filtro; JOIN compuesto `ON m.country_code=e.country_code AND m.code=e.municipality_code` | design |
| `services/api/routers/geo.py:51,69-73` · `services/api/stats.py:37-38` | `COUNT(*)` de entity/geo sin `WHERE country_code` → `/geo/completeness` y `/stats` mezclan totales | Scoping por `country_code`; default ES preserva el número | design |
| `pipeline/discover.py:91-104` (`_upsert`) | `INSERT INTO entity` no setea `country_code` (hereda DEFAULT 'ES') y `cdp_code(...)` usa `'ES'` → 2º país mintearía `CDP-ES-` | Propagar `country_code` por `DiscoveredEntity → _upsert → cdp_code(...)` y a la columna | design |
| `scripts/load_geo.py:26-70` | Backbone ES (52 prov + CCAA + xlsx con `zfill(2)/zfill(3)`) hardcodeado; asume coding 2+3 | Loader genérico parametrizado por `country_code` desde el manifiesto del pack | design |
| `pipeline/complete.py:73` (`_PROVINCE_RE`) | `^(0[1-9]|[1-4][0-9]|5[0-2])$` clava 01-52 → rechaza FR-DOM `971`, IT `>52` | Predicado de provincia per-país en el `GeoProfile` | **verdict+** (design solo marcó `:89`) |
| `pipeline/complete.py:83-85` (`_NATIONAL_KINDS`) | `{subasta,plataforma,oem_vo_portal,importador}` = taxonomía ES | `_NATIONAL_KINDS` per-país en el pack | **verdict+** |
| `pipeline/complete.py:89` (`_CDP_CODE_RE`) | `^CDP-ES-([0-9]{2})-…` clava ES y segmento 2-dígitos → rechaza todo `CDP-DE-*` y todo FR-DOM 3-dígitos | `^CDP-([A-Z]{2})-([0-9A-Z]{2,3})-…` (segmento **variable** + alfanumérico; la semántica de provincia va al predicado per-país) | design (regex) **+ verdict** (el design dejó `{2}` fijo — insuficiente) |

---

## Diseño genérico A→Z

El motor geo **no se reescribe**: se EXTRAE in-place separando **cuatro planos**, todos articulados por la dimensión `country_code` ya presente y la PK compuesta `(country_code, code)` que 0053 dejó probada. El diseño original definió tres planos correctos pero **omitió el ancho de código y el identity-path**; aquí se integran como parte del plano 1 y 3 (es la corrección que cierra el `NEEDS_REWORK`).

### 1) Almacenamiento canónico — topología fija, `code` opaco de ancho declarado

Las 3 tablas son el contrato físico, idénticas para todo país, ya con `country_code NOT NULL DEFAULT 'ES'` (0052) y PK/FK compuestas (0053). **Corrección keystone:** el `code` deja de ser `CHAR(n)` soldado y pasa a **`VARCHAR` de ancho declarado por el pack** (migración additiva `0054`, ver Veredicto Raíz A). El `code` es **opaco** — lo que dicte el esquema oficial (INE 2+5, AGS 8, INSEE 5, ISTAT 6) — y la colisión la absorbe `(country_code, code)`. El invariante de prefijo deja de ser global (0053:166-168 ya lo dejó gated por `country_code='ES'`); cada país añade su disyuntor gated en migración additiva, o queda sin restringir. La capa comarca es OPCIONAL → un backbone de 2 niveles es válido de fábrica.

### 2) Adaptador de árbol administrativo N-niveles (pieza nueva, country-agnóstica)

La "N-nivelidad" es un problema de **ingesta**, no de almacenamiento: el árbol de la fuente (GeoNames `feature_code` ADM1..ADM4, u OSM `admin_level` 2..10) se **proyecta/aplana** sobre los 3 slots canónicos mediante un manifiesto del pack. Interfaz:

```
GeoSource.fetch_tree() -> Iterable[Node(level, native_code, name, parent_native_code, lat, lon)]
GeoProjection(manifest): level1=province <- {geonames:ADM1 | osm:admin_level=4}
                         level2=comarca[nullable] <- ADM2 | admin_level=6
                         level3=municipality <- ADM3-4 | admin_level=8
```

Resuelve el padre por los punteros nativos y emite filas con el `code` **OFICIAL** del país (no el id de GeoNames). **ES es un adaptador degenerado del mismo interfaz:** su "fuente" es el diccionario INE (provincias hardcodeadas + xlsx municipios) y su manifiesto mapea 1:1 — por eso ES sigue INE sin reescribirse y COEXISTE con un adaptador GeoNames/OSM que apunta a las MISMAS 3 tablas. Si un país tuviera 4 niveles vinculantes, se añade `geo_subregion` additiva con el mismo patrón compuesto (YAGNI: hoy `{top, mid-opcional, leaf}` cubre el bucketing de dealers).

### 3) Perfil de país (`GeoProfile`) + country-scoping del resolver/identidad

Todo literal ES disperso (alias, ruta de gazetteer, normalizador, umbral KNN, regex de sufijo, etiqueta de región, **predicado de provincia G1**, **regex `cdp_code`**) se consolida en un `GeoProfile` registrado por `country_code`, con ES como perfil por defecto → ningún call-site sin tocar cambia su salida. `GeoResolver` y los geocoders dejan de ser singletons globales y pasan a **instanciarse por país**: `load()` gana `country_code`, añade `WHERE country_code=$1` a cada fetch, y clava sus índices internos por país → la contaminación cross-país es **imposible por construcción**, no por filtro a posteriori.

**Corrección de identidad (omitida por el diseño original):** la normalización se vuelve estrategia del perfil y aplica **también** a `services/api/codes.py:_normalize` (el path que alimenta el `cdp_code` inmutable), no solo a `pipeline/geo.py:_norm`. Latino-con-diacríticos (ES/DE/FR/IT/PT) usa el fold ASCII actual (byte-idéntico); no-Latino (JP/CJK, EL, BG/RU) registra **transliteración previa** (ICU/unidecode, CC0) ANTES del fold. Sin esto, JP minta identidad colisionada permanente (ver Veredicto Raíz B).

### 4) Escritura y lectura coherentes — cerrar el lazo PRODUCTOR→LECTOR

El minteo ya es genérico. Falta cerrar el lazo en los **productores** (`discover/ingest` propagan `country_code` a `entity` y a `cdp_code`) y en los **lectores/efectos** post-0053 que siguen country-blind: el trigger `entity_set_comarca`, los seeders de centroide/backfill, `PostcodeIndex.load`, y las queries de router/stats. **Principio rector:** toda junta geo (`JOIN`, `WHERE`, `SELECT INTO`, `UPDATE`) que hoy cruza por `code` debe cruzar por `(country_code, code)`. Para ES (único tenant) el resultado es byte-idéntico; para el país #2 es la diferencia entre verdad y mezcla.

**Resultado:** el motor (esquema-topología + algoritmo resolver/geocoder + mint + harness) se reusa idéntico; cada país aporta un pack declarativo (ancho de código + manifiesto de niveles + datasets libres + `GeoProfile` con perfil de normalización y pack G1); ES nunca se reescribe.

---

## Onboarding de país nuevo

Pasos de biblia para esta etapa. **Reordenado vs el diseño original:** los pre-requisitos irreversibles (ancho de esquema, cierre de country-blindness, identity-path) van **ANTES** de sembrar cualquier fila no-ES — sembrar primero corrompe en silencio.

1. **Asignar `country_code`** ISO-3166 alpha-2 (`!= ES`; `pilot_country` lo fuerza).
2. **Confirmar 0053 aplicada** (PK compuesta geo): el harness lo prueba con un INSERT rolled-back y rehúsa si falta [VERIFICADO `scripts/pilot_country.py:167-197`].
3. **[PRE-REQ — keystone] Migración `0054` de ancho:** `code/province_code/municipality_code/ccaa_code/hq_province_code/denominator_estimate.province_code` de `CHAR(2)/CHAR(5)` → `VARCHAR(n)`. Additiva; ES byte-idéntico (valores llenos). Verificar que las comparaciones de igualdad y los JOINs siguen exactos (CHAR ignora padding, VARCHAR no — ES no tiene padding, pero **probar**).
4. **Redactar el `GeoProfile` + manifiesto:** mapeo de niveles, **ancho/forma del código**, predicado de prefijo (o ninguno), umbral KNN, **perfil de normalización (con transliteración si no-Latino)**, regex de sufijo, tabla de alias, etiquetas de región, **predicado de provincia G1 + regex `cdp_code` per-país + `_NATIONAL_KINDS`**.
5. **Obtener datos del backbone por vía libre €0:** GeoNames (CC0) admin1/admin2 + lista LAU/municipios, u OSM/Overture (el adaptador `overture` ya existe); aterrizar en `data/<cc>/geo/`.
6. **Migración additiva del `CHECK` de prefijo** si el país tiene invariante de código (espejo de `0053:166-168`).
7. **[PRE-REQ — cerrar country-blindness] En el MISMO PR del país #2:** migración del trigger `entity_set_comarca` a forma compuesta; `country_code` en `GeoResolver.load`, `Province/MunicipalityGeocoder.load`, `PostcodeIndex.load`, `seed_geo_centroides`, backfills, router y stats; propagación en `discover/_upsert`. **Sin esto, el seed corrompe.**
8. **Ejecutar el loader geo genérico** `--country <CC>`: inserta province/comarca/municipality con `ON CONFLICT (country_code, code) DO NOTHING`.
9. **Ejecutar el seeder de centroides genérico** `--country <CC>` (UPDATE country-scoped) desde el CSV del pack.
10. **Backfill de comarca** si hay capa intermedia; si no, `comarca_id NULL` (válido).
11. **Registrar el `GeoProfile`** para que el resolver y los geocoders construyan índices country-scoped.
12. **Verificar (2-vía)** — ver [Sellado](#sellado--verificación-multi-vía--rollback).
13. **`pilot_country --dry-run` → `--apply`**, dejar probado `--revert`.
14. **Sellar:** persistir el certificado geo (conteos + intervalo de cobertura) y cablearlo a CI, **incluido un golden de forma extranjera real** (código de ancho nativo, nombre no-Latino, provincia 3-dígitos si aplica).

---

## Sellado + verificación multi-vía + rollback

**SELLADO geo de un país = conjunción de:**
- **(a) Backbone completo** — el conteo por nivel iguala el denominador publicado por la oficina estadística nacional (ES: 52 prov / 8132 muni; comprobación 2-vía `orphans=0`, `provinces_covered=N` [VERIFICADO `scripts/load_geo.py:94-100`]).
- **(b) Cobertura de centroides ≥ umbral** del país (ES: `8117/8132 ≈ 99,8%`, **cifra punto-en-el-tiempo, stack caído**).
- **(c) Integridad FK compuesta** — 0 municipios sin provincia-padre del mismo país y `bleed=0` [VERIFICADO `tests/test_country_coexistence.py:489-495` (`JOIN … ON p.country_code=m.country_code AND p.code=m.province_code WHERE m.country_code='DE' AND p.country_code<>'DE'` → `assert bleed==0`)].
- **(d) Resolver cerrado** — un golden de pares `(nombre_provincia, nombre_municipio)→código` resuelve byte-idéntico al pinneado.
- **(e) ES byte-idéntico** — conteos ES exactos (`geo_province=52`, `geo_municipality=8132` [VERIFICADO `tests/test_country_coexistence.py:79-81`]) y `verify()` asegura `entity/province/municipality` ES sin drift vs baseline [VERIFICADO `scripts/pilot_country.py:292-301`].

**VERIFICACIÓN POR 2ª VÍA ORTOGONAL (la única fuente de confianza):**
- El conteo del backbone se contrasta contra la fuente externa nacional (INE/GeoNames LAU/Eurostat), **independiente del loader** que lo cargó (el loader nunca se autovalida).
- El resolver se cruza por dos caminos **independientes que deben converger**: el textual (`GeoResolver` nombre→código) y el espacial (`MunicipalityGeocoder` lat/lon→código). Sobre una muestra, nombre y geometría deben coincidir — rutas ortogonales (texto vs geometría); su acuerdo es la prueba cruzada. Más round-trip `código→nombre→re-resolver→mismo código`.
- El 100% es un **INTERVALO certificado** (`coverage_lower` con CI, patrón `v_exhaustiveness_seal`), no un entero; un estrato fino reporta cota cerca de 0 y `sealed=false`, jamás un 100% fabricado [VERIFICADO `services/api/routers/geo.py:147-221`].

**ROLLBACK:** `pilot_country.py --revert` borra TODA fila `country_code<>'ES'` en orden inverso de FK (entity → municipality → province), idempotente y probado reversible [VERIFICADO `scripts/pilot_country.py:305-325`]. El rollback de 0053 exige **primero** borrar las filas geo no-ES — una PK de columna única no puede sostener ES-28 y DE-28 a la vez [VERIFICADO `migrations/0053_country_onboarding.sql:177-181`]. Para volcados de harvest crudos: sample-verify-delete. Cero efecto sobre ES en cualquier ruta (los `WHERE` son `country_code=<CC>` o prefijo `CDP-<CC>-`).

> **Honestidad cruda — el sello de HOY es ciego a las roturas que importan.** El "proof DE byte-idéntico" usa provincia `'28'` y municipio `'28001'` sintéticos con **forma ES EXACTA** [VERIFICADO `scripts/pilot_country.py:76-82`, `tests/test_country_coexistence.py:85-92`]. Prueba ÚNICAMENTE que la PK compuesta elimina la colisión; NO ejercita ancho de código, normalización ni provincia 3-dígitos. La rama de relajación del `CHECK` (`country_code<>'ES'`) **nunca se ejecuta** en el sello (el muni `'28001'` satisface igual el predicado ES) [VERIFICADO `tests/test_country_coexistence.py:85-87`]. Y `verify()` **nunca lee `entity.comarca_id`** [VERIFICADO `scripts/pilot_country.py:242-302`] → el sangrado del trigger comarca pasaría el sello en VERDE. Los huecos del sello se cierran en el [Veredicto](#sealing-holes--cierre-del-sello-ciego).

---

## Veredicto adversarial: roturas → resolución

El inquisidor falla **NEEDS_REWORK / `holds=false`**. Aquí cada `break`, `missing_pack` y `sealing_hole` con su resolución de diseño (cómo se cierra para DE/FR/IT/PT/MX/JP) o, si no se puede cerrar hoy, **OPEN ITEM con causa y gating**. Ninguna rotura se oculta. Las roturas se agrupan por **raíz** (varias comparten causa).

### Raíz A — Ancho de código soldado (la rotura keystone)

**Cubre breaks:** DE-`CHAR(5)`/AGS-8 [CRITICAL]; FR-`CHAR(2)`/DOM-3 [CRITICAL, mitad de almacenamiento]; IT-doble overflow muni-6/prov-3 [CRITICAL]; PT-freguesia-6 [HIGH]. **+ `missing_pack`:** "estrategia de tipo/ancho por país (el ítem más grave omitido)".

**Evidencia [VERIFICADO]:** `geo_municipality.code CHAR(5)` (`0001_geo.sql:19`), `geo_province.code CHAR(2)` (`0001_geo.sql:5`), `entity.municipality_code CHAR(5)` (`0002_entities.sql:14`), `entity.province_code CHAR(2)` (`0002_entities.sql:13`). Ni 0052 ni 0053 alteran el TIPO (solo añaden columnas/constraints/PK). Un AGS alemán de 8 dígitos revienta con `value too long for type character(5)`.

**Resolución (diseño):** migración additiva `0054` que cambia `geo_province.code`, `geo_municipality.code`, `geo_province.ccaa_code`, `entity.province_code`, `entity.municipality_code`, `organization.hq_province_code`, `denominator_estimate.province_code` y las columnas FK gemelas de `CHAR(n)` a `VARCHAR(n)` (ancho declarado por el pack, p.ej. `VARCHAR(12)`). El pack pasa a aportar el **ancho** como dato (Pack #2). Para ES es byte-idéntico: todo valor está lleno (`'28'`, `'28001'` — sin padding), así que las igualdades y JOINs no cambian. **Subtlety a probar:** `CHAR` ignora espacios finales en la comparación, `VARCHAR` no — ES no tiene padding, pero el golden debe confirmarlo.

**Estado: OPEN ITEM.** Causa: la migración NO está escrita (el código de hoy es `CHAR`). **Gating:** debe shippear ANTES de insertar cualquier fila no-ES (es un pre-req del onboarding, paso 3). Es reversible (additiva, rollback documentado; reverso a `CHAR` limpio solo mientras ningún valor exceda el ancho ES — mismo patrón que `0053:177-181`).

### Raíz B — Normalización del identity-path (no solo el resolver)

**Cubre breaks:** JP-CJK→colisión de `cdp_code` inmutable [CRITICAL, "la peor rotura porque corrompe identidad permanente"]; DE-`ß` no decompone [MEDIUM]. **+ `missing_pack`:** "perfil de normalización para el identity-path, no solo para el resolver geo".

**Evidencia [VERIFICADO]:** `services/api/codes.py:30` hace `unicodedata.normalize("NFKD",text).encode("ascii","ignore")` y alimenta `canonical_key → mint_code` (el `cdp_code` es INMUTABLE, append-only). El diseño original SOLO marcó `pipeline/geo.py:51-53`, dejando intacto el path de minteo. **Mecanismo probado por ejecución determinista local** (stack caído no afecta a Python puro): `横浜`/`名古屋`/`Αθήνα`/`Москва` → `''` (cadena vacía) → `canonical_key="name:|{muni}"` colapsa TODA entidad name-based de un municipio a UNA clave → `cdp_code` colisionados; y `Weißenfels → 'weienfels'` ≠ `Weissenfels → 'weissenfels'` (el `ß` se **cae**, no se pliega a `ss`).

**Resolución (diseño):** el `GeoProfile` declara la **estrategia de normalización** y se aplica en AMBOS sitios (`codes.py:_normalize` y `geo.py:_norm`). Latino (ES/DE/FR/IT/PT) usa el fold ASCII actual → byte-idéntico. No-Latino (JP/CJK, EL, BG/RU) registra **transliteración CC0 (unidecode/ICU) ANTES del fold** → `横浜→"yokohama"`, `ß→"ss"`. Esto cierra DE y JP con un solo mecanismo.

**Estado: OPEN ITEM con GATE DURO.** Causa: no existe capa de transliteración en código. **Gating:** **prohibido mintear una sola entidad name-based no-Latina antes de que la transliteración esté en el identity-path** — el `cdp_code` es inmutable y `sample-verify-delete` NO revierte un código mal minteado. Para países Latinos (DE/FR/IT/PT) la rotura del identity-path se limita a `ß`/ligaduras raras (MEDIUM) y puede acompañar al PR de país; para JP/CJK/EL/cirílico es bloqueante de cimiento.

### Raíz C — Lecturas/efectos country-blind (sangrado cross-país)

**Cubre breaks:** MX-trigger comarca [CRITICAL, "sangrado irreversible"]; MX-geocoders + `seed_geo_centroides` [CRITICAL]. **+ `missing_pack`:** "inventario de queries country-blind a escanear y scopear en cada onboarding".

**Evidencia [VERIFICADO]:** `entity_set_comarca()` hace `SELECT m.comarca_id … WHERE m.code=NEW.municipality_code` **sin** `country_code` (`0018_comarca.sql:30-31`) → tras 0053, `code` ya no es único → `SELECT INTO` toma fila arbitraria → entidad MX hereda `comarca_id` de ES. `ProvinceGeocoder.load`/`MunicipalityGeocoder.load` no filtran país (`geocode.py:80-87,129-152`); `seed_geo_centroides` hace `UPDATE … WHERE code=$3` sin país (`seed_geo_centroides.py:96-99`) → `(ES,'28001')` y `(MX,'15001')`… el seeder ES pisa centroides del homónimo.

**Resolución (diseño):** migración additiva `CREATE OR REPLACE FUNCTION entity_set_comarca()` con `AND m.country_code=NEW.country_code` (byte-idéntico ES, toda fila ES); `country_code` en `load()` de ambos geocoders con índice por `(country_code, province_code)`; `--country` + `AND country_code=$x` en fetch y UPDATE del seeder; resolver/geocoders instancia-por-país. **Precisión vs el inquisidor:** el inquisidor dice "el diseño omitió los TRES loaders de geocode.py" — verificado, el diseño SÍ cubrió `ProvinceGeocoder`/`MunicipalityGeocoder` (`es_seams`), pero **omitió `PostcodeIndex.load`** (`geocode.py:205-260`); ese es el loader genuinamente faltante, ahora añadido en [Costuras](#costuras-es-hardcoded--fix).

**Estado: OPEN ITEM.** Causa: ninguna migración posterior a 0018 corrigió el trigger; los loaders siguen country-blind. **Gating:** todas estas juntas deben volverse compuestas **en el MISMO PR que siembra el país #2** (paso 7 del onboarding). Reversible (migración additiva + parámetros con default ES).

### Raíz D — Gate de identidad G1 ES-hardcoded

**Cubre breaks:** FR-DOM `_PROVINCE_RE` rechaza `971` [parte de CRITICAL]; IT `>52` provincias [parte de CRITICAL]; "Todos" — G1 hardcodea 2 cosas ES [HIGH]. **+ `missing_pack`:** "pack del validador G1".

**Evidencia [VERIFICADO]:** `_PROVINCE_RE = ^(0[1-9]|[1-4][0-9]|5[0-2])$` (`complete.py:73`) rechaza `971` y `>52`; `_CDP_CODE_RE = ^CDP-ES-([0-9]{2})-…` (`complete.py:89`) clava ES y segmento de 2 dígitos numéricos; `_NATIONAL_KINDS = {subasta,plataforma,oem_vo_portal,importador}` (`complete.py:83-85`) es taxonomía ES. El golden `test_rejects_malformed` **ancla** el rechazo de `'CDP-ES-1-…'` (provincia no-2-dígitos) (`test_country_golden.py:294-298`) y el test `foreign` es `xfail` que solo prueba `'CDP-DE-28-…'` de 2 dígitos (`test_country_golden.py:285-292`).

**Resolución (diseño + corrección):** el `GeoProfile` aporta (i) **predicado de provincia per-país** (ES: 01-52; FR: 01-95 + 2A/2B Córcega + 971-976 DOM; IT: 01-110), (ii) **regex `cdp_code` de segmento variable** `^CDP-([A-Z]{2})-([0-9A-Z]{2,3})-[0-9A-HJKMNP-TV-Z]{8}$` — la semántica de provincia se mueve al predicado per-país, la regex solo valida estructura, (iii) `_NATIONAL_KINDS` per-país. El golden gana una rama per-país. **Corrección al diseño original:** su fix nombrado era `^CDP-([A-Z]{2})-([0-9A-Z]{2})-…` con segmento **fijo de 2** — INSUFICIENTE: seguiría rechazando FR-DOM/IT de 3 dígitos. Por eso aquí el segmento es `{2,3}`.

**Estado: OPEN ITEM (xfail conocido).** Causa: la regex y el rango siguen ES; el golden incluso bloquea activamente un código FR/IT correcto. **Gating:** mientras no se amplíe, **todo punto del país #2 falla G1** y no promociona a servible aunque el geo esté correcto (bloquea el funnel de serving, no la corrección geo). Es el "6º blocker" ya pinneado por el propio test [VERIFICADO `test_country_golden.py:280-291`].

### Raíz E — Taxonomía de región nivel-1: ancho y síntesis

**Cubre `missing_pack`:** "taxonomía de región nivel-1 con su ANCHO" + `sealing_hole` "ccaa sintética BB/BE nunca valida taxonomía real".

**Evidencia [VERIFICADO]:** `geo_province.ccaa_code CHAR(2) NOT NULL`, `ccaa_name TEXT NOT NULL` (`0001_geo.sql:7-8`). El piloto cubre el `NOT NULL` con etiquetas sintéticas `BB/BE` de 2 chars (`pilot_country.py:117-126`) → el sello nunca valida una región real ni su ancho para un país sin agrupación supra-provincial (MX 32 estados, JP 47 prefecturas sin super-región).

**Resolución (diseño):** el pack aporta la etiqueta de región Y una **regla de síntesis** para países sin agrupación supra-provincial (sintetizar `region_code = province_code` o un código de macro-región oficial). `ccaa_code` se ensancha junto con Raíz A (entra en la lista de columnas de la `0054`). **Estado: OPEN ITEM**, atado a la migración de ancho.

### Raíz F — Código postal / gazetteer per-país

**Cubre break:** JP-sin gazetteer/CP Latino [HIGH]. **+ `missing_pack`:** "fuente y formato de CP per-país".

**Evidencia [VERIFICADO]:** `PostcodeIndex.load` lee `data/geo/nomenclator_entidades_ine.csv` ES-only con columnas `codigo_postal/municipio_id` (`geocode.py:51-53,234-241`); el CP japonés es 7-dígitos y el romaji está ausente.

**Resolución (diseño):** `PostcodeIndex` per-país (fuente + formato de CP en el pack: DE/FR/IT 5, PT `NNNN-NNN`, JP 7, MX 5) + transliteración (romaji) para el índice de CP/localidad cuando el país es no-Latino. **Estado: OPEN ITEM**, no-fatal hasta el onboarding de JP (el resolver textual y el KNN espacial siguen funcionando sin CP).

### Raíz G — Cargador de backbone genérico

**Cubre `missing_pack`:** "cargador de backbone genérico". **Evidencia [VERIFICADO]:** `load_geo.py:26-70` hardcodea `PROVINCES/CCAA` ES + lectura xlsx con `zfill(2)/zfill(3)` que asume coding 2+3. **Resolución:** contrato de loader parametrizado por `country_code` que lee el manifiesto/datasets del pack y no presupone el ancho INE; ES queda como pack-default que produce el mismo INSERT. **Estado: OPEN ITEM** (reversible, no destructivo).

### Raíz H — Calibración del umbral KNN

**Cubre `missing_pack`:** "calibración de `KNN_MAX_DISTANCE_KM` por país". **Evidencia [VERIFICADO]:** `KNN_MAX_DISTANCE_KM=30.0` constante global ES (`geocode.py:49`). **Resolución:** umbral en el `GeoProfile` (default 30 ES); futuro auto-calibrar al p99 del radio municipal (requiere polígonos, idea de [nivel inalcanzable](#mejoras-a-nivel-inalcanzable-eur0-priorizadas)). **Estado: OPEN ITEM** (parámetro, trivial; el dato calibrado por país falta).

### Sealing holes — cierre del sello ciego

El inquisidor lista 8 huecos del sello. Resolución conjunta: **el sello gana fixtures de forma extranjera REAL como puerta obligatoria** (paso 14 del onboarding), sin los cuales el certificado "paramétrico por país" no tiene evidencia.

| Sealing hole [VERIFICADO] | Cierre |
|---|---|
| `i`+`viii` — proof DE hueco: `'28'/'28001'` con forma ES exacta (`pilot_country.py:76-82`); DECISION-1 sobre-afirmada | Golden obligatorio con código de ancho nativo (AGS-8), nombre no-Latino, provincia 3-dígitos. **Restatement honesto:** el piloto probó SOLO que la PK compuesta elimina la colisión, NO que el esquema sea paramétrico |
| `ii` — la rama `country_code<>'ES'` del CHECK nunca se ejecuta (`test_country_coexistence.py:85-87`) | Fixture con muni que **viole** el prefijo ES (p.ej. `left2≠prov`) bajo `country_code<>'ES'` → ejercita la relajación |
| `iii` — ningún fixture ejercita ancho-8/no-Latino/prov-3/sangrado comarca/sangrado geocoder | Cada uno gana un caso en el golden de forma extranjera (depende de Raíz A+B+C aplicadas) |
| `iv` — `verify()` nunca lee `entity.comarca_id` (`pilot_country.py:242-302`) | Añadir aserción: tras seed de país con homónimo ES, `entity.comarca_id` del país NO es el del municipio ES |
| `v` — golden `foreign` es `xfail` solo 2-dígitos; `test_rejects_malformed` fija rechazo de prov no-2-dígitos (`test_country_golden.py:286-298`) | Rama per-país en el golden (Raíz D); el rechazo de "1-dígito ES" se mantiene vía predicado ES, sin bloquear "3-dígitos FR" |
| `vi` — sin rollback probado para onboarding que aborta a mitad por overflow | Test: seed que aborta por width/normalización deja ES byte-idéntico (transacción + `--revert`); cablear a CI |
| `vii` — ccaa sintética BB/BE nunca valida región real ni ancho (`pilot_country.py:117-126`) | Fixture con taxonomía de región real del país (Raíz E) |

**Veredicto de cierre, honesto:** la etapa **NO sostiene hoy** (`holds=false`). El esquema-topología + algoritmo + mint-prefijo + harness SÍ son reusables y están probados para la coexistencia de PK. Pero **paramétrico-por-país completo exige cuatro fixes no-construidos** (Raíz A ancho, Raíz B identity-normalización, Raíz C cierre country-blind, Raíz D pack-G1), todos reversibles, todos con gate de "antes de sembrar el país #2". Hasta entonces, la genericidad geo es **arquitectónica y de esquema, no operativa**.

---

<a id="sub-proyectos"></a>

## Sub-proyectos institucionales (360 por faceta)

Esta sección descompone la etapa Geo en **27 sub-proyectos institucionales**, cada uno tratado a **360°**: el átomo verificado a fuente, su mecanismo, la costura ES→genérico con fix exacto, el riesgo adversarial (DE/FR/IT/PT/MX/JP/no-UE), el criterio de sellado multi-vía y la herramienta de elevación a nivel inalcanzable (toda €0, licencia declarada). Es la expansión átomo-a-átomo de las raíces A–H del [Veredicto adversarial](#veredicto-adversarial-roturas--resolución): cada raíz se resuelve en una o más facetas aquí, con su gate de reversibilidad declarado.

> **Honestidad cruda.** "360 por faceta" describe la PROFUNDIDAD del tratamiento, no un recuento: son **27 facetas (F1–F27)**, no 360. Cada cita `path:línea` se marca `[VERIFIED]` (leída contra el código en Wave 1). Las cifras DB siguen siendo punto-en-el-tiempo (**stack vivo caído**); el código se leyó línea a línea. Ningún `OPEN ITEM` se presenta como hecho: lleva causa y gate.

**Estructura de cada sub-proyecto:** una *Ficha rápida* (Costura · Fix · Adversarial · Sellado · NEXT-LEVEL) para escaneo, seguida del *Deep-spec 360* con sus apartados (a) verificación → (b) mecanismo → (c) costura+fix → (d) adversarial → (e) sellado multi-vía → (f) herramienta. Cada faceta cierra con un enlace de vuelta al índice.

### Mapa raíz adversarial → faceta

| Raíz del Veredicto | Sub-proyectos que la cierran |
|---|---|
| A — Ancho de código soldado (keystone) | F1, F5, F7, F13, F17 (guardas de ancho) |
| B — Normalización del identity-path | F11 (la peor), F10 (resolver), F14 (tokenización) |
| C — Lecturas/efectos country-blind | F2, F6, F9, F15, F18, F19, F20, F21 |
| D — Gate de identidad G1 ES-hardcoded | F22, F3 (predicado de forma) |
| E — Taxonomía de región nivel-1 | F7 |
| F — Código postal / gazetteer per-país | F17, F13 |
| G — Cargador de backbone genérico | F5, F4 (adaptador N-niveles) |
| H — Calibración del umbral KNN | F16, F26 (PIP lo elimina de raíz) |
| Sealing holes — cierre del sello ciego | F23 (harness), F24 (certificado) |
| Infra transversal (gobierno del pack) | F8 (GeoProfile), F12 (alias), F25 (suministro) |
| Palancas next-level (capa-2/€>0) | F26 (point-in-polygon), F27 (IA-local) |

<a id="indice-sub"></a>

### Índice de sub-proyectos

**[Capa I · Esquema y backbone físico](#capa-1) (F1–F7)**

- [F1 · Ancho/tipo de codigo de unidad administrativa (CHAR->VARCHAR parametrico)](#f1)
- [F2 · Identidad geo multi-tenant (PK/FK compuesta) + rollback abort-safe](#f2)
- [F3 · Predicado de forma de codigo por pais (CHECK gated + predicado unico compartido)](#f3)
- [F4 · Adaptador de arbol administrativo N-niveles (GeoSource + GeoProjection)](#f4)
- [F5 · Loader de backbone generico + verificacion 2-via](#f5)
- [F6 · Capa comarca opcional + trigger entity_set_comarca country-scoped](#f6)
- [F7 · Taxonomia de region nivel-1 (ccaa) + ancho + regla de sintesis](#f7)

**[Capa II · Resolver textual, perfil y normalización](#capa-2) (F8–F14)**

- [F8 · GeoProfile registry (espina dorsal de literales ES)](#f8)
- [F9 · GeoResolver country-scoping (texto nombre->codigo)](#f9)
- [F10 · Normalizacion — plano RESOLVER (_norm)](#f10)
- [F11 · Normalizacion — plano IDENTIDAD/MINT (codes._normalize) la peor rotura](#f11)
- [F12 · Tabla de alias de provincia/region](#f12)
- [F13 · Gazetteer de localidades (nombre->muni) + resolucion de ruta por pais](#f13)
- [F14 · Fuzzy matcher (WRatio + token-subset) + tuning por pais](#f14)

**[Capa III · Geocodificación espacial, escritores y lectores](#capa-3) (F15–F21)**

- [F15 · Geocoders espaciales country-scoping (Province + Municipality KNN)](#f15)
- [F16 · Calibracion del umbral KNN por pais](#f16)
- [F17 · PostcodeIndex (CP->muni) + fuente/formato de CP por pais](#f17)
- [F18 · Seeder de centroides country-scoped + dataset/quirk](#f18)
- [F19 · Backfill write-loops country-scoping + self-verify por predicado](#f19)
- [F20 · Propagacion de pais en PRODUCTORES (discover/ingest -> entity + cdp_code)](#f20)
- [F21 · Country-scoping de LECTORES/API (router geo + stats + vistas)](#f21)

**[Capa IV · Identidad servible, sellado, suministro y palancas next-level](#capa-4) (F22–F27)**

- [F22 · Validador de identidad G1 generico (complete.py, geo-adyacente)](#f22)
- [F23 · Harness de onboarding/pilot endurecido (fixture forma-extranjera real)](#f23)
- [F24 · Certificado de sellado geo (2-via ortogonal + intervalo con CI)](#f24)
- [F25 · Suministro de datos geo EUR0 + denominador nacional de 2a via](#f25)
- [F26 · Next-level Reverse-geocode por point-in-polygon (elimina la heuristica KNN)](#f26)
- [F27 · Next-level Desambiguacion IA-local de localidad irreducible (>1 municipio)](#f27)

---

<a id="capa-1"></a>

### Capa I · Esquema y backbone físico (F1–F7)

> El contrato físico donde el árbol administrativo vive y se carga: ancho de código, identidad multi-tenant, predicado de forma, adaptador N-niveles, loader, herencia de comarca y taxonomía de región. Aquí nacen las roturas *keystone* (Raíz A) y el sangrado de nivel-medio (Raíz C).

<a id="f1"></a>

#### F1 · Ancho/tipo de codigo de unidad administrativa (CHAR->VARCHAR parametrico)

**Ficha rápida**

- **Costura (ES→genérico):** 0052/0053 anaden country_code CHAR(2) DEFAULT 'ES' [VERIFIED 0052:51-54] pero git grep 'ALTER COLUMN' en 0052/0053 = CERO [VERIFIED]: las 7 columnas de codigo siguen CHAR(2)/CHAR(5) soldadas [VERIFIED 0001:5,19; 0002:13-14; 0007:12; 0026:253; 0048:39,58]. ES nunca se reescribe; el pais #2 con codigo mas ancho no CABE. El propio 0052:23 admite 'CHAR(2) carries no blank-padding ambiguity' (solo cierto para ES).
- **Fix:** Migracion additiva 0054_widen_geo_codes.sql: ALTER COLUMN ... TYPE VARCHAR(16) sobre las 7 columnas + geo_comarca.ine_code; cambiar casts ::char(5)[] -> ::varchar[]/::text[] en seed_geo_centroides.py:71 y geo_backfill.py:164. CHAR->VARCHAR(>=n) es additivo, ES byte-identico (2/5 chars exactos, sin padding); FK/CHECK intactos. Ancho real per-pais declarado por el pack (Frictionless). Segmento de provincia del cdp_code intacto (mint_code, codes.py:53).
- **Adversarial:** DE AGS Gemeinde 8-digit, ISTAT-IT 6 + prov 3, PT DICOFRE 6, FR DOM 971-976 = 3 -> INSERT 'value too long for type character(5/2)' aborta el seed a mitad. El cast ::char(5)[] (seed_geo_centroides:71, geo_backfill:164) TRUNCA en silencio un codigo de 8 a 5 -> match contra el homonimo ES en vez de error. El piloto prueba DE con '28001' forma-ES exacta -> el overflow nunca se ejerce; el sello pasa verde con la rotura viva.
- **Sellado:** 7 columnas+casts en VARCHAR; golden ES byte-identico (diff 0 filas tras 0054); fixture forma-extranjera real (AGS-8/DOM-3) INSERTA sin overflow; max(length(code)) real <= ancho declarado en pack. Multi-via: test de migracion (diff cero ES) + test de inserto extranjero (8-digit entra y se lee identico) + contrato Frictionless que falla rojo ante codigo demasiado-largo.
- **NEXT-LEVEL:** Frictionless Framework (frictionless-py, Table Schema) -- MIT, EUR0 -- https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]: declara el ancho-en-bytes per-pais como Table Schema versionado, valida el pack ANTES del INSERT (overflow -> fallo claro temprano, no abort tardio); 0054 toma VARCHAR(n) del mismo schema. Complemento pycountry (ISO 3166-2 width authority, LGPL-2.1, [VERIFIED NEXT-LEVEL.md:530]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
Las 7 columnas portadoras del codigo opaco, confirmadas una a una por `git grep -i "CHAR(2)|CHAR(5)"`:
- `migrations/0001_geo.sql:5` `code CHAR(2) PRIMARY KEY` (geo_province) [VERIFIED]
- `migrations/0001_geo.sql:19` `code CHAR(5) PRIMARY KEY` (geo_municipality) [VERIFIED]
- `migrations/0002_entities.sql:13` `province_code CHAR(2)`, `:14` `municipality_code CHAR(5)` [VERIFIED]
- `migrations/0007_organization.sql:12` `hq_province_code CHAR(2)` [VERIFIED]
- `migrations/0026_verification_deep.sql:253` `province_code CHAR(2)` [VERIFIED]
- `migrations/0048_discovery_capture.sql:39` y `:58` `province_code char(2)` (estrato MSE) [VERIFIED]
- casts de array en escritura: `scripts/seed_geo_centroides.py:71` `ANY($1::char(5)[])` [VERIFIED]; `scripts/geo_backfill.py:164` `unnest($2::char(5)[])` [VERIFIED]

Hallazgo nuclear: `git grep "ALTER COLUMN" migrations/0052_country.sql migrations/0053_country_onboarding.sql` -> CERO [VERIFIED]. Las migraciones de pais anaden la DIMENSION (`ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'`, `0052:51-54` [VERIFIED]) pero NUNCA ensanchan las 7 columnas de codigo. Mas aun, `0052_country.sql:23` documenta la decision explicita: "chars, so CHAR(2) carries no blank-padding ambiguity" -- el diseno SABIA del CHAR y argumento que ES no sufre padding, dejando el overflow extranjero sin tratar. El propio NEXT-LEVEL.md:336 lo reconoce: "geo_municipality.code es CHAR(5) y geo_province.code CHAR(2) soldados [VERIFIED 0001_geo.sql:5,19] (Raiz A, rotura keystone)".

##### (b) Mecanismo al atomo
`CHAR(n)` en Postgres es `character(n)`: almacenamiento blank-padded de ancho FIJO. Dos consecuencias atomicas:
1. Overflow duro: insertar una cadena de longitud > n lanza `value too long for type character(n)` y aborta la transaccion. No hay truncado en INSERT.
2. Semantica blank-padded: `'28'::char(2) = '28 '::char(3)` es TRUE bajo reglas char (ignora trailing blanks), mientras `varchar`/`text` compara byte-a-byte. Las 6 FK compuestas y el CHECK `municipality_province_prefix` (`0001_geo.sql:26` `left(code,2)=province_code`) dependen de esta semantica; migrar a VARCHAR debe preservar que ES (siempre 2/5 chars exactos, cero padding real) compare identico.

El cast `::char(5)[]` en los writers (`seed_geo_centroides.py:71`, `geo_backfill.py:164`) es el atomo mas traidor: un codigo extranjero de 8 digitos pasado por `ANY($1::char(5)[])` se TRUNCA a 5 ANTES de tocar la fila, produciendo un match contra el codigo ES homonimo en vez de un error -- corrupcion silenciosa, no abort.

##### (c) Costura ES->generico + fix exacto
Nueva migracion additiva `0054_widen_geo_codes.sql`:
```sql
ALTER TABLE geo_province     ALTER COLUMN code              TYPE VARCHAR(16);
ALTER TABLE geo_municipality ALTER COLUMN code              TYPE VARCHAR(16);
ALTER TABLE geo_municipality ALTER COLUMN province_code     TYPE VARCHAR(16);
ALTER TABLE entity           ALTER COLUMN province_code     TYPE VARCHAR(16);
ALTER TABLE entity           ALTER COLUMN municipality_code TYPE VARCHAR(16);
ALTER TABLE organization     ALTER COLUMN hq_province_code  TYPE VARCHAR(16);
-- + 0026:253, 0048:39/58 province_code, geo_comarca.ine_code (0018:8)
```
`CHAR(n)->VARCHAR(m>=n)` es additivo y NO reescribe datos ES de forma observable: PG conserva el valor logico; el unico cambio es que desaparece el blank-padding (que ES nunca usa, 2/5 exactos). FK y CHECK siguen validos porque VARCHAR compara '=' igual sin trailing blanks. `VARCHAR(16)` cubre AGS-8/ISTAT-6/DICOFRE-6/DOM-3 con margen; el ancho real per-pais lo declara el pack (ver tool). Los casts `::char(5)[]` pasan a `::varchar[]`/`::text[]` en `seed_geo_centroides.py:71` y `geo_backfill.py:164`. El segmento de provincia del cdp_code NO se toca (vive en `mint_code`, `codes.py:53`, parametrico). ES byte-identico: un golden de carga ES produce los mismos INSERT.

##### (d) Riesgo adversarial concreto
- DE: AGS de Gemeinde = 8 digitos -> `value too long for type character(5)` aborta el seed a mitad. ISTAT-IT muni = 6, provincia = 3. PT freguesia/DICOFRE = 6. FR DOM '971'-'976' = 3 digitos de provincia -> `character(2)` overflow.
- Trampa del piloto: `pilot_country.py` prueba DE con muni sintetico '28001' (5 chars, forma-ES EXACTA) que NO es un AGS real -> el overflow JAMAS se ejerce, el sello pasa verde con una rotura viva (cruza con F23).
- Ruido/no-UE: codigos alfanumericos (algunos UK ward) rompen ademas el `[0-9]{2}` aguas abajo (F22), pero el storage VARCHAR ya no es la barrera.
- A escala: UNA columna olvidada (p.ej. `0048:58` en el roll-up MSE) aborta el onboarding del pais #2 tras escribir backbone parcial -> estado de migracion corrupto (cruza con F2 rollback).

##### (e) Criterio de sellado + verificacion multi-via
SELLADO si y solo si (1) las 7 columnas + casts en VARCHAR; (2) golden ES byte-identico (hash de tabla post-0054 == pre-0054); (3) fixture forma-extranjera real (AGS-8, DOM-3) INSERTA sin overflow; (4) `max(length(code))` real del dataset <= ancho declarado en el pack. Multi-via: via A test de migracion (aplica 0054 sobre dump ES, diff = 0 filas mutadas); via B test de inserto extranjero (8-digit entra y se lee identico); via C el contrato Frictionless (tool) valida el ancho ANTES del INSERT y un fixture de codigo demasiado-largo debe FALLAR rojo.

##### (f) Herramienta de elevacion
Frictionless Framework (frictionless-py, Table Schema) -- MIT, EUR0 -- https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Declara cada dataset del pack (`data/<cc>/geo/pack.schema.json`) con tipo, regex de forma y el ancho-en-bytes per-pais como CONTRATO versionado; valida en el bootstrap ANTES de cargar una fila, convirtiendo `value too long for type character(5)` (abort tardio, sin diagnostico) en un fallo de validacion claro y temprano. La migracion 0054 toma `VARCHAR(n)` del MISMO schema -> una sola fuente de verdad para el ancho. Complemento: pycountry (ISO 3166-2, LGPL-2.1, [VERIFIED NEXT-LEVEL.md:530,528]) aporta la autoridad del code-width de subdivisiones (DE Kreis 5-digit, FR '971'-'976') que alimenta el ancho declarado, sin investigarlo a mano.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f2"></a>

#### F2 · Identidad geo multi-tenant (PK/FK compuesta) + rollback abort-safe

**Ficha rápida**

- **Costura (ES→genérico):** El PK/FK compuesto (country_code, code) ya es generico y ES-byte-identico (0052:51-77 DEFAULT 'ES' + 0053:71-157 relabel 1:1 con MATCH SIMPLE). La costura ABIERTA es el rollback abort-safe: 0053:176-219 es prosa COMENTADA, no codigo ni test; pilot_country.py:305-325 revert() borra por country_code pero solo para el pilot ES-shaped y no encadena con la reversion de 0053 ni prueba ES byte-identico tras un abort REAL por overflow/normalizacion.
- **Fix:** Implementar un protocolo transaccional de onboarding: (i) snapshot ES, (ii) cada bucle de escritura (loader/seeder/backfill) en savepoint, (iii) ante fallo DELETE FROM geo_* WHERE country_code=$cc en orden FK-inverso (entity->municipality->province, patron pilot_country.py:314-324) ANTES de permitir revertir 0053, (iv) test que prueba ES byte-identico row-level. Materializar la seccion comentada 0053:183-218 como down() ejecutable gated por 'cero filas no-ES'.
- **Adversarial:** DE/IT/FR: seed de AGS-8/ISTAT-6/DOM-FR-3 desborda el INSERT con 'value too long for type character(5)' a mitad del backbone -> 0053 aplicada + filas no-ES parciales vivas; revertir 0053 con ellas presentes hace fallar 'ADD CONSTRAINT geo_province_pkey PRIMARY KEY (code)' (0053:203) por duplicate-key (ES-28+DE-28). Estado de migraciones corrupto irreversible. no-UE: abort por normalizacion deja cdp_code colisionados append-only no revertibles.
- **Sellado:** Test que prueba el ciclo abort->byte-identico->revert-limpio (NO existe hoy: test_country_coexistence.py:416 es rollback deliberado de filas ES-shaped, no abort-por-overflow). Multi-via: (1) conteo ES pre==post (pilot_country.py:142-149,292-301, existe parcial); (2) diff row-level de filas ES added/removed/changed=0 (FALTA); (3) tras DELETE no-ES + revert 0053, _composite_pk_applied=False y PRIMARY KEY(code) se restaura sin duplicate-key; (4) abort disparado con muni 8-digit REAL, no '28001' ES-shaped (cruza F23).
- **NEXT-LEVEL:** DataComPy (Apache-2.0) — https://github.com/capitalone/datacompy [VERIFIED NEXT-LEVEL.md:417]. Su nucleo added/removed/changed es la via-2 de sellado: diff de filas geo+entity ES pre-onboarding vs post-abort -> changed=added=removed=0 prueba ES byte-identico row-level (no un count enganable por re-key compensado). EUR0 pip puro, CI-runnable. Alternativa SQL: DuckDB EXCEPT/ANTI JOIN (NEXT-LEVEL.md:418).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **`migrations/0052_country.sql:51-54`** [VERIFIED]: `ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` en `geo_province / geo_comarca / geo_municipality / entity`. El DEFAULT 'ES' estampa las 431.211 entity / 52 province / 8.132 municipality / 323 comarca como ES atomicamente (`:20-23`), backfill implicito cero-NULL.
- **`0052_country.sql:61-77`** [VERIFIED]: anade los UNIQUE compuestos `uq_geo_province_country_code (country_code, code)` y `uq_geo_municipality_country_code (country_code, code)` guardados por DO-block de presencia (idempotente), **dejando intactos los PK de columna unica** -> los 7 FK siguen resolviendo (`:56-58`). `:25-41` declara DELIBERADAMENTE DIFERIDO: (a) el PK-swap a compuesto, (b) country_code en denominator/organization, (c) la relajacion de los CHECK ES.
- **`migrations/0053_country_onboarding.sql:56-157`** [VERIFIED]: ejecuta exactamente lo diferido — drop de los 6 FK hijos (`:57-62`), `ADD CONSTRAINT geo_*_pkey PRIMARY KEY (country_code, code)` PRIMERO (`:71-87`), drop de los UNIQUE redundantes (`:90-91`), re-add de los 6 FK como compuestos `FOREIGN KEY (country_code, <col>) REFERENCES geo_*(country_code, code)` con **MATCH SIMPLE** (`:99-157`). El orden (PK antes de drop-UNIQUE) garantiza que la superficie unica nunca falta (`:47-48`).
- **`0053:176-219`** [VERIFIED]: la seccion Rollback esta **ENTERAMENTE COMENTADA** (cada linea con `-- `). Aviso literal `:177-179`: *"CLEAN ONLY while NO non-ES geo rows exist — a single-column PK on `code` cannot hold ES-28 and DE-28 simultaneously; any pilot/onboarding MUST delete all country_code <> 'ES' geo rows BEFORE rolling this back."*
- **`scripts/pilot_country.py:152-164`** [VERIFIED]: `_composite_pk_applied` lee `pg_get_constraintdef(oid)` del PK de `geo_province` y comprueba `"country_code" in pk_def` (no adivina, "assume nothing"). **`:167-197`** `_ensure_ready` levanta una transaccion, intenta `INSERT INTO geo_province(code,...,country_code) VALUES ('28',...,$country)`, y si el PK aun es de columna unica captura `asyncpg.UniqueViolationError` y rehusa; SIEMPRE `tr.rollback()` (la prueba de readiness deja cero residuo).
- Contexto del runner [VERIFIED `0053:35-45`]: `migrate.py` abre `async with conn.transaction()` y ejecuta cada statement; por eso 0053 OMITE BEGIN/COMMIT y la atomicidad la da la transaccion del runner (cualquier excepcion auto-aborta toda la migracion; el ledger inserta solo en exito).

##### (b) Mecanismo al atomo
La identidad geo multi-tenant es una sustitucion de **superficie de unicidad**: PK(`code`) -> PK(`country_code,code`). En el estado actual TODAS las filas son ES (entity non-ES = 0), asi que el swap es un relabel 1:1 puro: ninguna fila se renumera, ningun cdp_code/canonical_key se toca (0053 nunca hace UPDATE de columna portadora de codigo, `:9-13`). El nucleo de coexistencia (probado por `test_country_coexistence.py:309 test_de_28_coexists_with_es_28`) demuestra que tras 0053 (DE,'28') y (ES,'28') conviven. **MATCH SIMPLE** es deliberado (`0053:96-98`): una componente NULL (province/municipality) deja la fila sin forzar, preservando el comportamiento de dealer-sin-provincia. El atomo abierto NO es el forward —ya entregado— sino el **contrato de rollback abort-safe**: 0053 es atomica-en-exito por la transaccion del runner, pero un onboarding REAL de pais #2 inserta backbone en MULTIPLES statements/transacciones (loader F5 + seeder F18 + backfill F19); si uno revienta a mitad (overflow F1 / normalizacion F11), 0053 queda aplicada + filas parciales no-ES vivas, y el rollback comentado de 0053 ya NO es limpio (un PK de columna unica no puede sostener ES-28 + DE-28). El mecanismo que falta: un **protocolo transaccional de onboarding** que (i) snapshotea ES, (ii) envuelve cada bucle de escritura en savepoint, (iii) ante fallo hace `DELETE WHERE country_code=$cc` de TODA tabla geo antes de permitir revertir 0053, (iv) prueba ES byte-identico.

##### (c) Costura ES -> generico
La PK/FK compuesta YA es generica y ES-byte-identica por construccion (DEFAULT 'ES' + relabel 1:1). La costura ABIERTA es el **rollback probado**: hoy es prosa comentada (`0053:176-219`), no codigo ejecutable ni test. `pilot_country.py:305-325 revert()` borra filas pilot por `country_code=$cc` en orden FK-inverso (entity -> municipality -> province) — es el paso (iii) del protocolo, pero solo para el pilot ES-shaped, y NO encadena con la reversion de 0053 ni prueba byte-identidad de ES tras un abort REAL.

##### (d) Riesgo adversarial concreto
- **DE/IT/FR (overflow encadenado, F1)**: seed de AGS-8 / ISTAT-6 / DOM-FR-3 revienta el INSERT con `value too long for type character(5)` a mitad del backbone -> 0053 aplicada + provincias DE parciales vivas. El operador intenta revertir 0053 con filas no-ES presentes -> la restauracion `ADD CONSTRAINT geo_province_pkey PRIMARY KEY (code)` (`0053:203`) FALLA con duplicate key (ES-28 + DE-28). Estado de migraciones corrupto, irreversible sin cirugia manual.
- **Ruido / doble-onboarding**: dos onboardings concurrentes del mismo cc; el segundo ve filas parciales del primero y el `ON CONFLICT (country_code,code) DO NOTHING` enmascara la corrupcion.
- **no-UE (MX/JP)**: un seed MX que aborta por normalizacion (F11) deja entity MX con cdp_code colisionado + filas geo MX parciales; revert por `country_code='MX'` borra geo pero los cdp_code colisionados son append-only (no revertibles).

##### (e) Criterio de sellado + verificacion multi-via
**Sello = existe un test que prueba el ciclo abort->byte-identico->revert-limpio.** Hoy NO existe: `test_country_coexistence.py` tiene `test_inserting_de_rows_does_not_change_es_counts:416` [VERIFIED] pero es un rollback de transaccion DELIBERADO de filas ES-shaped (`:455 await tx.rollback()`), NO un abort-por-overflow. Multi-via:
1. **Via conteo** (existe parcial): `_es_baseline` snapshot de counts ES; assert post-abort == pre (`pilot_country.py:142-149, 292-301`).
2. **Via diff de filas** (FALTA): no basta el count — hay que diffear las FILAS ES (codes, names, FKs) antes vs despues del abort -> added/removed/changed = 0. Esta es la via que eleva "ES byte-identico" de count-assert a prueba row-level (ver herramienta).
3. **Via estado-de-migraciones**: tras `DELETE WHERE country_code<>'ES'` + revert de 0053, `_composite_pk_applied` devuelve False y `geo_province_pkey = PRIMARY KEY (code)` se restaura sin duplicate-key error.
4. **Via fixture forma-extranjera** (cruza con F23): el abort debe dispararse con muni 8-digit REAL, no con '28001' ES-shaped (que nunca desborda).

##### (f) Herramienta next-level
**DataComPy** (Apache-2.0) — https://github.com/capitalone/datacompy [VERIFIED NEXT-LEVEL.md:417]. Aunque su uso primario minado es la reconciliacion de backbone (deteccion de fusiones/escisiones municipales, `NEXT-LEVEL.md:414-420`), su capacidad nuclear `added/removed/changed` es EXACTAMENTE la via-2 de sellado de F2: diffear el snapshot de filas geo+entity ES antes del onboarding contra el estado tras un abort -> `changed=0 AND added=0 AND removed=0` convierte "ES byte-identico tras rollback" en una prueba mecanica row-level, no un count que un re-key compensado podria enganar. Ruta EUR0 (pip puro, corre en CI). Alternativa SQL pura: `DuckDB EXCEPT / ANTI JOIN` (`NEXT-LEVEL.md:418`).

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f3"></a>

#### F3 · Predicado de forma de codigo por pais (CHECK gated + predicado unico compartido)

**Ficha rápida**

- **Costura (ES→genérico):** El invariante de forma esta CUADRUPLICADO y soldado a ES en 4 motores que no comparten codigo: CHECK SQL `left(code,2)=province_code` [VERIFIED 0001_geo.sql:26] y su gemelo en entity [VERIFIED 0041_entity_muni_province_invariant.sql:14-17], ambos relajados por gate de pais [VERIFIED 0053_country_onboarding.sql:166-174]; self-verify Python `code[:2] != prov` [VERIFIED backfill_municipality_geo.py:72]; y G1 con rango+regex ES `_PROVINCE_RE` 01-52 [VERIFIED complete.py:73] + `_CDP_CODE_RE ^CDP-ES-([0-9]{2})-` [VERIFIED complete.py:89]. La rama de relajacion `country_code <> 'ES'` (0053) NUNCA se ejerce: es codigo muerto sin fixture extranjero. No existe ninguna `GeoProfile.shape` que unifique la regla; cada pais nuevo exige editar los 4 sitios a mano, con riesgo de drift entre ellos.
- **Fix:** Crear `GeoProfile.shape: CodeShape` (en F8) con dos predicados + opcion 'sin invariante': `muni_belongs_to_province` (ES=`lambda code,prov: code[:2]==prov`; DE/FR=`None`) y `province_re` (ES=`^(0[1-9]|[1-4][0-9]|5[0-2])$`; otros derivados de ISO 3166-2 via pycountry). Cablear los 4 consumidores a esa unica definicion: (1) el bootstrap del pais #2 genera su CHECK `country_code<>'<CC>' OR <pred>` desde el perfil, omitiendo el CHECK de prefijo cuando `muni_belongs_to_province is None` — ES queda literal (0001/0041 verbatim por la rama `<>'ES'`, byte-identico); (2) backfill_municipality_geo.py:72 -> `not profile.shape.muni_belongs_to(code, prov)` (ES igual; pais sin prefijo NO rechaza, la validez pasa al FK compuesto + geocoder country-scoped); (3) complete.py:73/142 -> `profile.shape.province_re` (ES=01-52 exacto, golden sin drift), entregando ademas a G1 el `province_re` per-pais que el `_CDP_CODE_RE` debe incrustar. Una sola fuente de verdad; 4 lectores; default 'ES' byte-identico.
- **Adversarial:** DE AGS de 8 digitos sin relacion prefijo: backfill_municipality_geo.py:72 `code[:2]!=prov` rechaza TODA resolucion valida -> censo DE a 0 sin error en log (sobre-vaciado total). IT/PT con provincia > 52: `_PROVINCE_RE` (tope 52) rechaza la identidad correcta -> entidad nunca servible (G1 bloquea promocion en silencio). FR-DOM 971-976 de 3 digitos: rango 01-52 y `[0-9]{2}` del cdp_code la rechazan; un CDP-FR-971 valido seria bloqueado ACTIVAMENTE por el sello. Pais de mismo ancho con coding distinto: el prefijo VALIDA MAL (acepta relacion inexistente), inyectando munis mal-asignados que pasan el CHECK. La rama `country_code<>'ES'` jamas se ejercio: el primer pais real es su primer test, en produccion.
- **Sellado:** Sellado cuando: una sola `GeoProfile.shape` existe y los 4 consumidores la leen (`grep` = 0 ocurrencias de `code[:2]`/`01-52`/`left(code,2)` fuera del default ES), la rama de relajacion se ejerce por fixture extranjero (F23), y ES no drifta. Multi-via: (1) ES byte-identico — `test_country_golden` + Ferrari verdes, re-evaluar 433.211 entity contra G1 nuevo = 0 cambios de veredicto; (2) adversarial pais sin prefijo — fixture DE acepta la resolucion valida y rechaza un AGS mal-asignado por FK, no por slice; (3) rango — IT=58/FR=971 pasan `province_re` per-pais mientras siguen rechazados bajo el perfil ES; (4) consistencia inter-motor — CHECK SQL, self-verify Python y G1 concuerdan sobre el mismo (code,prov,country) por derivar del mismo perfil.
- **NEXT-LEVEL:** Frictionless Framework (frictionless-py, Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:334-340]: convierte el predicado de forma en CONTRATO de datos auto-verificado por pais (regex de forma + ancho en bytes en `data/<cc>/geo/pack.schema.json`), validado ANTES del INSERT, fuente unica de la que CHECK/backfill/G1 derivan; su golden de pack-malo prueba la rama de rechazo hoy inerte. Complemento: pycountry (ISO 3166-2) — LGPL-2.1 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533] surte el conjunto/ancho autoritativo de subdivisiones que llena `province_re`, retirando el sentinel 01-52 (uso build-time, LGPL no contamina; alt permisiva iso3166 MIT). Ambas €0.

**Deep-spec 360**

##### (a) Verificacion de code_hints [leido a fuente]
- **[VERIFIED migrations/0001_geo.sql:26]** `CONSTRAINT municipality_province_prefix CHECK (left(code, 2) = province_code)` — el invariante de prefijo ES nace aqui, soldado y SIN gate de pais. `geo_municipality.code` es `CHAR(5)` (:19) y `province_code CHAR(2)` (:21).
- **[VERIFIED migrations/0041_entity_muni_province_invariant.sql:14-17]** (el hint decia `0041_*.sql:14-17`; el fichero real es `0041_entity_muni_province_invariant.sql`) `ALTER TABLE entity ADD CONSTRAINT chk_entity_muni_province CHECK (municipality_code IS NULL OR province_code IS NULL OR left(municipality_code, 2) = province_code)` — segundo portador del MISMO predicado de prefijo, NULL-tolerante, sin pais.
- **[VERIFIED migrations/0053_country_onboarding.sql:166-168]** relajacion gated del primero: `CHECK (country_code <> 'ES' OR left(code, 2) = province_code)`.
- **[VERIFIED migrations/0053_country_onboarding.sql:170-174]** relajacion gated del segundo: `CHECK (country_code <> 'ES' OR municipality_code IS NULL OR province_code IS NULL OR left(municipality_code, 2) = province_code)`. El comentario :159-165 confirma la doctrina: para una fila ES el disyunto `country_code <> 'ES'` es FALSE -> PG evalua el predicado ES verbatim (byte-identico); un esquema no-ES queda SIN restringir.
- **[VERIFIED scripts/backfill_municipality_geo.py:72]** self-verify en Python: `if code not in valid or code[:2] != prov:` -> `skipped["resolved_invalid_or_wrong_province"] += 1; continue`. El docstring :12-14 lo declara puerta dura ("a non-matching/invalid resolution is skipped").
- **[VERIFIED pipeline/complete.py:73]** `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` — rango ES 01-52 hardcodeado; consumido por G1 en :142 `if not is_national and (prov_str is None or not _PROVINCE_RE.match(prov_str)): return False, ...`. Ademas **[VERIFIED complete.py:89]** `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` clava 2 digitos de provincia y prefijo `CDP-ES-` en la identidad servible.

CONCLUSION: el invariante de forma esta **CUADRUPLICADO** y atado a ES en 4 lugares con 2 mecanismos distintos (CHECK SQL x2 + predicado Python x2: prefijo en backfill, rango+regex en G1). No hay UNA fuente de verdad.

##### (b) Mecanismo al atomo
El "predicado de forma" responde a una sola pregunta por pais: *dado un `municipality_code` y un `province_code` (o un `province_code` suelto), esta BIEN-FORMADO?* En ES son DOS afirmaciones acopladas por el coding INE:
1. **Relacion muni<->provincia**: `left(code,2) = province_code` (el muni "pertenece" a su provincia por prefijo).
2. **Forma de la provincia**: `province_code in 01..52` (rango censal INE) + el segmento de provincia del `cdp_code` es `[0-9]{2}`.
Estas dos afirmaciones se evaluan en 4 motores (Postgres CHECK x2, regex Python G1, comparacion de slice en backfill) que HOY no comparten ni una linea: cada uno re-implementa la regla ES. La genericidad exige colapsarlas a un objeto unico `GeoProfile.shape` con dos predicados: `muni_belongs_to_province(code, prov) -> bool` y `province_wellformed(prov) -> bool`, mas la opcion explicita "sin invariante de prefijo" (DE/FR), de modo que los 4 consumidores LEAN del mismo objeto y la rama de relajacion (`country_code <> '<CC>'`) por fin se EJERZA.

##### (c) Costura ES->generico + fix exacto
**Costura**: tres copias del predicado ES viven fuera de cualquier perfil; la 4a (G1) usa rango+regex en vez de prefijo. Un pais sin relacion prefijo (DE AGS de 8 digitos cuyos 2 primeros NO son el code de Bundesland; FR INSEE de 5 cuyos 2 primeros son el departamento, relacion DISTINTA; provincias IT/PT > 52) rompe los 4.
**Fix (una sola definicion, 4 consumidores)**:
1. Crear en el `GeoProfile` (pieza F8) `shape: CodeShape` con:
   - `muni_belongs_to_province: Callable[[str,str],bool] | None` — ES = `lambda code, prov: code[:2] == prov`; DE/FR = `None` (sin invariante de prefijo).
   - `province_re: re.Pattern` — ES = `^(0[1-9]|[1-4][0-9]|5[0-2])$`; otros pais = patron propio derivado del catalogo ISO 3166-2 (ver tool).
2. **CHECK SQL (0053:166-174)**: el bootstrap del pais #2 emite su propio `country_code <> '<CC>' OR <pred>` donde `<pred>` se genera del perfil: si `muni_belongs_to_province` es `None`, el predicado adicional es ausente (no se anade CHECK de prefijo para ese pais), preservando byte-identico el de ES. **ES intacto: la rama `country_code <> 'ES'` deja la fila ES en el predicado verbatim de 0001/0041.**
3. **backfill_municipality_geo.py:72**: sustituir `code[:2] != prov` por `not profile.shape.muni_belongs_to(code, prov)` donde para ES devuelve `code[:2]==prov` (byte-identico) y para un pais sin prefijo devuelve `True` (NO rechaza) — la validez la aporta entonces el FK compuesto + el geocoder country-scoped (F15), no el slice.
4. **complete.py:73/142**: `_PROVINCE_RE` -> `profile.shape.province_re`; G1 evalua `profile.shape.province_re.match(prov_str)`. Para ES, `province_re` = 01-52 exacto (golden sin drift). (El ensanche del `_CDP_CODE_RE` :89 es co-responsabilidad de G1/F22; F3 le ENTREGA el `province_re` per-pais que ese regex debe incrustar.)
**Default ES = byte-identico por construccion**: el perfil 'ES' reproduce las 4 reglas actuales literal; ningun call-site sin tocar cambia su veredicto.

##### (d) Riesgo adversarial concreto
- **DE (AGS 8 digitos, sin relacion prefijo)**: `backfill_municipality_geo.py:72` `code[:2] != prov` rechaza TODA resolucion valida (los 2 primeros del AGS son el Land, no la "provincia"/Kreis) -> sobre-vaciado total del backfill, censo DE artificialmente a 0 sin un solo error en log.
- **IT/PT (provincia > 52)**: `complete.py:73` `_PROVINCE_RE` (tope 52) RECHAZA la identidad de una provincia 58/70/etc. -> entidad correcta JAMAS pasa G1 -> nunca servible (bloqueo de promocion silencioso).
- **FR-DOM (971-976, 3 digitos)**: tanto el rango 01-52 como el `[0-9]{2}` del `cdp_code` la rechazan; un `CDP-FR-971-...` valido seria bloqueado activamente por el sello.
- **Pais de mismo ancho que ES con coding DISTINTO**: peor que rechazar — el prefijo `left(code,2)` VALIDA MAL (acepta una relacion que no existe), inyectando munis mal-asignados que pasan el CHECK.
- **Ruido**: la rama de relajacion `country_code <> 'ES'` (0053:166/170) NUNCA se ejerce en el sello actual (ningun fixture extranjero la atraviesa, cf. F23) -> es codigo muerto no probado; el primer pais real es su primer test en produccion.

##### (e) Criterio de sellado + verificacion multi-via
**Sellado** cuando: (1) existe UNA definicion `GeoProfile.shape` y los 4 consumidores (2 CHECK, backfill, G1) la leen — `grep` confirma 0 ocurrencias residuales de `code[:2]`, `01-52`, `left(code,2)` fuera del perfil ES-default; (2) la rama de relajacion se EJERCE por un fixture de pais sin prefijo (cruza F23); (3) ES golden sin drift.
**Multi-via**:
- *Via 1 (ES byte-identico)*: golden `test_country_golden` + suite Ferrari verdes; re-evaluar los 433.211 entity contra G1 nuevo -> 0 cambios de veredicto.
- *Via 2 (adversarial pais sin prefijo)*: fixture DE (AGS 8-dig, Land != prefijo) -> el backfill ACEPTA la resolucion valida (no sobre-vacia) y el CHECK del pais #2 no impone prefijo; un AGS deliberadamente mal-asignado a otro Land se rechaza por FK compuesto, no por slice.
- *Via 3 (rango)*: provincia IT=58 y FR-DOM=971 PASAN `province_re` per-pais y G1; el mismo input bajo el perfil ES sigue siendo rechazado (no se relaja ES).
- *Via 4 (consistencia inter-motor)*: para una muestra, el veredicto del CHECK SQL, del self-verify Python y de G1 sobre el MISMO (code,prov,country) CONCUERDAN (los 3 derivan del mismo perfil) — divergencia = drift, bloquea.

##### (f) Herramienta NEXT-LEVEL [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md]
- **Frictionless Framework (frictionless-py, Table Schema)** — MIT — https://github.com/frictionlessdata/frictionless-py — [VERIFIED NEXT-LEVEL.md:334-340]. Eleva el predicado de forma de "regla hardcodeada x4" a **CONTRATO de datos auto-verificado**: el Table Schema del pack declara, por pais, el regex de forma del codigo y el ancho en bytes; el pack se valida ANTES del INSERT. Es exactamente "no documentar la regla — que la maquina la imponga y la pruebe sola": la UNICA fuente de verdad del shape vive en `data/<cc>/geo/pack.schema.json` y CHECK/backfill/G1 derivan de ella. Su golden de pack-malo (un codigo que excede ancho o viola el predicado FALLA la validacion) prueba la rama de rechazo que hoy nunca se ejerce.
- **pycountry (ISO 3166-1/-2 + ISO 4217)** — LGPL-2.1 — https://github.com/pycountry/pycountry — [VERIFIED NEXT-LEVEL.md:527-533]. Surte el DATO autoritativo que llena `province_re`/`province_wellformed`: el conjunto y ancho de subdivisiones de primer nivel de cada pais (ES=52, DE=16, FR=101, IT=107) se vuelve DATA, retirando el sentinel 01-52 ES-shaped. Uso en build/config-time (no hot-path) -> LGPL no contamina; alternativa estricta-permisiva `iso3166` (MIT) + JSON crudo de iso-codes. €0.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f4"></a>

#### F4 · Adaptador de arbol administrativo N-niveles (GeoSource + GeoProjection)

**Ficha rápida**

- **Costura (ES→genérico):** load_geo.py funde fuente+proyeccion+loader y hardcodea 52 provincias ES + CCAA + zfill(2)/zfill(3) [VERIFIED load_geo.py:26-71]. Extraer GeoSource.fetch_tree() (formato de fuente) y GeoProjection(manifest) (aplanado N-niveles->3 slots: geo_province / comarca_id nullable / geo_municipality), dejando el dict INE+xlsx como adaptador degenerado ES 1:1 apuntando a las mismas 3 tablas.
- **Fix:** Manifiesto ES declara coding={province:2, municipality:5=2+3}; GeoProjection reproduce el zfill por DATO-del-manifiesto (no hardcode) -> INSERT ES byte-identico (52/8132). Padre resuelto por puntero nativo (hierarchy.zip parentId), NO por prefijo, para paises sin relacion prefijo (DE AGS/FR). Emite el code OFICIAL nacional via cross-walk LAU/OSM, no el geonameid. Default country='ES' (patron codes.py:24).
- **Adversarial:** DE 4 niveles vinculantes (Land>Regierungsbezirk>Kreis>Gemeinde) desborda los 3 slots -> requiere geo_subregion additiva NO PROBADA. Punteros padre ciclicos/huerfanos en GeoNames hierarchy.zip rompen FK compuesta. OSM admin_level=6 = provincia en un pais y comarca en otro -> backbone torcido a escala sin manifiesto por pais. Fuente global sobre-captura vecinos por bbox (overture.py:222-224 hoy filtra !='ES' hardcodeado).
- **Sellado:** (1) ES byte-identico: 52 prov / 8132 muni, diff vs INSERT historico = 0. (2) Integridad jerarquia: 0 muni sin padre del mismo pais (FK compuesta); todos los parentId resuelven. (3) 2-via denominador vs oficina estadistica nacional (orphans=0, niveles=N) -cruza F25-. (4) Idempotencia ON CONFLICT (country_code,code) DO NOTHING sin cambio de conteo. (5) Cruce de code GeoNames vs oficial (INE/AGS/INSEE) coincide tras cross-walk.
- **NEXT-LEVEL:** GeoNames dump (allCountries.zip + hierarchy.zip + admin1CodesASCII.txt + admin2Codes.txt) — CC-BY 4.0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377]. Complemento: DuckDB + spatial extension — MIT — https://github.com/duckdb/duckdb-spatial [VERIFIED NEXT-LEVEL.md:409] (build reproducible CI-runnable sin Postgres vivo; patron ya probado por pipeline/sources/overture.py).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **PIEZA NUEVA confirmada**: no existe ninguna clase `GeoSource` ni `GeoProjection` en el repo; el unico escritor de backbone es `scripts/load_geo.py`, 100% ES-soldado.
- **Referencia ES a portar** [VERIFIED scripts/load_geo.py:26-71]:
  - `CCAA` dict (19 entradas CODAUTO->nombre) en lineas 26-34.
  - `PROVINCES` dict (52 provincias, `code -> (name, CODAUTO)`) en lineas 37-56 — autoritativo, hardcodeado.
  - `read_municipalities()` lineas 59-71: lee el xlsx INE con `cpro = str(row[1]).strip().zfill(2)` (:67) y `cmun = str(row[2]).strip().zfill(3)` (:68), emite `(cpro+cmun, name, cpro)` (:70) -> el coding 2+3 esta SOLDADO en los dos `zfill`.
- **Fuente OSM/Overture viva** [VERIFIED pipeline/sources/overture.py]: `_BBOX` Espana en :35; campos admin emitidos en el SELECT DuckDB `addresses[1].region/locality/postcode/country` lineas 184-186; derivacion de provincia desde el CP en :227-228; filtro pais `if country and country != "ES": continue  # keep only Spain` en :222-224. El adaptador ya prueba que una fuente N-niveles global se consulta in-process via DuckDB+spatial (httpfs) a coste cero (:87-106).

##### (b) El mecanismo al atomo
1. `GeoSource.fetch_tree()` -> iterador de nodos `(level, native_code, name, parent_native_code, lat, lon)`. Es el unico punto que conoce el formato de la fuente (GeoNames ADM1..ADM4, OSM admin_level 2..10, o el dict INE).
2. `GeoProjection(manifest)` APLANA ese arbol de profundidad arbitraria sobre los **3 slots canonicos** que son las 3 tablas vivas: `geo_province` (slot top), `geo_municipality.comarca_id` nullable (slot mid), `geo_municipality` (slot leaf). El manifiesto declara, por pais, que `level` de la fuente cae en que slot (p.ej. ES `{top: ADM-prov, mid: none, leaf: muni}`; GeoNames generico `{ADM1->province, ADM2->comarca?, ADM3/4->municipality}`).
3. La proyeccion resuelve el padre por **puntero nativo** (`parent_native_code` -> `hierarchy.zip parentId`), NO por prefijo de codigo, de modo que un pais sin relacion prefijo (DE AGS, FR) tambien encadena padre->hijo.
4. Emite SIEMPRE el **codigo OFICIAL nacional** (INE/AGS/ISTAT/INSEE), no el `geonameid`, via cross-walk (tabla LAU Eurostat / tags OSM `ref:INE`).
5. ES es un **adaptador degenerado**: su `GeoSource` envuelve los dicts `PROVINCES`/`CCAA` + el xlsx; su manifiesto es 1:1; los 3 adaptadores apuntan a las MISMAS 3 tablas.

##### (c) La costura ES->generico con su fix exacto
- **Costura**: hoy `load_geo.py` ES el loader Y la fuente Y la proyeccion, fundidos. Extraer la fuente (dicts+xlsx) detras de `GeoSource` y el aplanado detras de `GeoProjection(manifest)`, dejando `load_geo.py` como el adaptador degenerado ES.
- **Fix exacto**: el manifiesto ES declara `coding={province:2, municipality:5=prov(2)+local(3)}` -> el `GeoProjection` reproduce `zfill(2)`/`zfill(3)` SOLO para ES por dato-del-manifiesto, no por hardcode; para DE el manifiesto declara `coding={municipality:8 (AGS)}` y el zfill se ajusta. El INSERT ES resultante es **byte-identico** (mismas 52 filas province, 8.132 muni). El default de pais es `'ES'`, patron `codes.py:24 DEFAULT_COUNTRY`.

##### (d) El riesgo adversarial concreto
- **4 niveles vinculantes desbordan 3 slots**: DE (Land > Regierungsbezirk > Kreis > Gemeinde) o cualquier pais con 4 ADM legalmente vinculantes -> el slot mid unico (comarca) no basta. Mitigable con `geo_subregion` additiva, **no probado**.
- **Punteros padre ciclicos/huerfanos** en `hierarchy.zip` de GeoNames -> un nodo sin padre del mismo pais rompe la FK compuesta `(country_code, province_code)`.
- **Mis-asignacion de admin_level**: OSM `admin_level=6` es provincia en un pais y comarca en otro -> sin manifiesto explicito por pais, el backbone sale TORCIDO a escala continental (el nivel-medio de un pais entra como leaf de otro).
- **Ruido no-UE**: una fuente global (Overture) sobre-captura paises vecinos por bbox (:222-224 hoy lo filtra con `!= "ES"` hardcodeado); el generico necesita el filtro de pais parametrico o mete POIs de PT/FR en el censo ES.

##### (e) Criterio de sellado + verificacion multi-via
1. **ES byte-identico** (golden de carga inalterado): el adaptador degenerado ES produce exactamente 52 provincias / 8.132 municipios; diff contra el INSERT historico = 0.
2. **Integridad de jerarquia**: 0 municipios sin padre del MISMO pais (FK compuesta); todos los `parentId` de `hierarchy.zip` resuelven dentro del pais.
3. **2-via denominador**: el conteo por nivel del loader se contrasta contra la oficina estadistica nacional independiente (orphans=0, niveles cubiertos = N) — cruza con F25.
4. **Idempotencia**: re-correr con `ON CONFLICT (country_code, code) DO NOTHING` no cambia conteos.
5. **Cruce de code**: muestra de municipios con `code` GeoNames vs `code` oficial (INE/AGS/INSEE) coincide tras el cross-walk -> prueba que se emite el codigo nacional, no el geonameid.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **GeoNames dump** (`allCountries.zip` + `hierarchy.zip` + `admin1CodesASCII.txt` + `admin2Codes.txt`) — CC-BY 4.0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377]. Un SOLO ingestor cubre todos los paises objetivo: `feature_class='A'`, `feature_code ADM1..ADM4`, padre via `hierarchy.zip`, cross-walk a codigo oficial via tabla LAU Eurostat (free-reuse) o tags OSM. Eleva el adaptador de 'pieza nueva por escribir a mano por pais' a 'una pasada pan-pais auto-verificable'.
- **Complemento**: **DuckDB + spatial extension** — MIT — https://github.com/duckdb/duckdb-spatial [VERIFIED NEXT-LEVEL.md:409] materializa el build (descarga->aplanado->centroides->H3) como artefacto reproducible CI-runnable SIN Postgres vivo (cierra la honestidad 'stack caido -> no puedo correr el golden'). El adaptador Overture vivo (overture.py) ya prueba el patron DuckDB+httpfs+spatial a EUR0.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f5"></a>

#### F5 · Loader de backbone generico + verificacion 2-via

**Ficha rápida**

- **Costura (ES→genérico):** load_geo.py bakea ES en tres ejes: dicts de modulo PROVINCES(52)+CCAA(19) (:26-56), zfill(2)/zfill(3) que presupone el split de codigo INE 2+3 (:67-68), y posiciones fijas de columna xlsx (row[1]/row[2]/row[4]). El INSERT YA es composite-PK-aware (ON CONFLICT (country_code,code), :81-88). La 2-via existe (:90-100) pero NO es independiente (mismo script) y es country-blind (orphan-join :96 y covered :98 sin country_code).
- **Fix:** (1) loader recibe el pack por --country en vez del xlsx+dicts; (2) code de cada nivel llega ya formado y validado contra Table Schema (ancho/regex per-pais) ANTES del INSERT; (3) externalizar la 2-via a un job independiente que re-derive el denominador nacional desde una fuente ortogonal y diffee; (4) scopear orphan-join y covered por (country_code,code). ES = pack-default byte-identico (52/8132). Imprecisiones del enunciado corregidas: el loader SI se auto-valida (falta INDEPENDENCIA, no la 2-via); zfill PADEA, el truncado real es el CHAR(5) de F1.
- **Adversarial:** DE AGS-8 / IT ISTAT-6 / PT DICOFRE-6 / FR DOM-3 rompen el split 2+3 y desbordan CHAR(5) (F1) a mitad de seed; columnas en otro orden cargan name como code; covered country-blind reporta 'provinces_covered=52' verde mezclando el pais #2; sin denominador nacional libre (F25) la cobertura no certifica; filas de cabecera/totales de un xlsx no-INE entran como municipios fantasma.
- **Sellado:** Golden carga ES byte-identico (orphans=0, covered=52); 2-via INDEPENDIENTE loader-vs-oficina-estadistica (drift abre PR); idempotencia ON CONFLICT; integridad jerarquica FK compuesta 0-huerfanos; cruce code-pack vs code-oficial. sealed=false sin denominador independiente.
- **NEXT-LEVEL:** GeoNames dump (allCountries+hierarchy+admin codes) — loader pan-pais N-niveles, CC-BY 4.0, https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377]. 2-via independiente: DataComPy (Apache-2.0, https://github.com/capitalone/datacompy [VERIFIED:417]). Contrato ancho pre-INSERT: Frictionless (MIT, https://github.com/frictionlessdata/frictionless-py [VERIFIED:337]). Build CI serverless: DuckDB+spatial (MIT, https://github.com/duckdb/duckdb-spatial [VERIFIED:409]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **load_geo.py:26-34** [VERIFIED] `CCAA` = dict literal de modulo, 19 pares CODAUTO->nombre, 100% ES ("01":"Andalucia"...).
- **load_geo.py:37-56** [VERIFIED] `PROVINCES` = dict literal de 52 provincias ES con (nombre, CODAUTO) cableado a mano.
- **load_geo.py:67-68** [VERIFIED] `cpro = str(row[1]).strip().zfill(2)` ; `cmun = str(row[2]).strip().zfill(3)`: presupone (i) el split de codigo INE 2+3 y (ii) posiciones fijas de columna xlsx (row[1]=cpro, row[2]=cmun, row[4]=name en :69).
- **load_geo.py:70** [VERIFIED] `out.append((cpro + cmun, name, cpro))`: el code de municipio se CONSTRUYE concatenando 2+3 = exactamente 5 chars (forma ES).
- **load_geo.py:81-83, 86-88** [VERIFIED] los dos INSERT ya llevan `ON CONFLICT (country_code, code) DO NOTHING`: el loader YA es composite-PK-aware (0052/0053 aplicado); el INSERT no es la rotura.
- **load_geo.py:90-100** [VERIFIED] 2-via: `nprov/nmuni` counts (90-91, country-blind), `orphans` (94-97, `LEFT JOIN geo_province p ON p.code = m.province_code` SIN country_code), `covered` (98, `COUNT(DISTINCT province_code)` country-blind).

**Honestidad cruda — dos imprecisiones del enunciado corregidas:**
1. La facet dice "El loader nunca se auto-valida" → IMPRECISO: SI se auto-valida (94-98). El defecto real es que la 2-via (a) vive en el MISMO script/conexion/proceso (no es un denominador INDEPENDIENTE) y (b) su orphan-join (96) y su `covered` (98) son country-blind → tras 0053 cruzan paises.
2. La facet dice "carga codigos truncados/mal-padded" → IMPRECISO: `zfill` PADEA, nunca trunca; el truncado real ocurre aguas abajo en el cast/columna `CHAR(5)` (dominio F1). Lo que SI bakea ES aqui es ESTRUCTURAL: el split 2+3 y las posiciones de columna del xlsx INE.

##### (b) Mecanismo al atomo
`read_municipalities()` (59-71) abre `data/geo/diccionario_ine.xlsx` con openpyxl read_only, itera desde `min_row=3`, descarta filas sin cpro/cmun (`row[1] is None or row[2] is None`, :65), padea cpro→2 y cmun→3, concatena a code5 y emite `(code5, name, cpro)`. `main()` (74-102) abre asyncpg, lanza dos `executemany` idempotentes (provincias desde el dict PROVINCES+CCAA, municipios desde el xlsx), luego 4 `fetchval` de verificacion e imprime `provinces=… municipalities=… orphans=… provinces_covered=…`. Comarcas quedan vacias (no hay capa INE universal, :8-9).

##### (c) Costura ES→generico + fix exacto
El contrato del loader debe: (1) recibir el **pack** (manifiesto + datasets) por `--country` en vez de leer el xlsx INE y los dicts de modulo; (2) NO presuponer ancho ni split — el code de cada nivel llega del pack ya formado y **validado contra un Table Schema** (ancho/regex per-pais) ANTES del INSERT, capturando el overflow en frontera, no en el motor PG; (3) **externalizar la 2-via** a un job independiente que re-derive el denominador nacional desde una fuente ORTOGONAL (oficina estadistica) y lo diffee, en lugar de contar sobre los mismos datos que inserto; (4) scopear el orphan-join y el `covered` por `(country_code, code)` (cruza con F20/F21). ES queda como **pack-default** que produce las mismas 52 / 8132 filas byte-identicas (golden de carga inalterado). El cast `char(5)[]` de seeders/backfills toma `n` del mismo schema (una sola fuente de verdad de ancho con F1).

##### (d) Riesgo adversarial concreto
- **DE** AGS=8 / **IT** ISTAT muni=6 / **PT** DICOFRE=6 / **FR** DOM 971-976=3: el split 2+3 no aplica → code mal-estructurado; el `CHAR(5)` (F1) revienta/trunca a mitad de seed dejando datos parciales (cruza F2 rollback).
- **Columnas en otro orden**: un pack con name en otra posicion carga `name` como `code` silenciosamente (las posiciones row[1]/row[2]/row[4] son INE-especificas).
- **`covered` country-blind** (98): cuenta provincias de TODOS los paises → reporta "provinces_covered=52" como verde aun mezclando el pais #2.
- **Denominador**: sin oficina estadistica nacional libre (cruza F25) la cobertura no se certifica (sello degrada a cota inferior).
- **Ruido**: filas de cabecera/totales/subtotales de un xlsx no-INE pasan el filtro fragil `row[1] is None` (:65) y entran como municipios fantasma.

##### (e) Criterio de sellado + verificacion multi-via
1. **Golden de carga ES**: pack-default ES → 52 provincias + 8132 munis byte-identico, `orphans=0`, `provinces_covered=52`.
2. **2-via INDEPENDIENTE**: conteo por nivel del loader contrastado contra oficina estadistica nacional (diff added/removed/changed con tolerancia); drift abre PR, no se auto-aplica.
3. **Idempotencia**: re-run con ON CONFLICT no altera counts.
4. **Integridad jerarquica**: 0 municipios sin provincia del mismo pais (FK compuesta), todos los parent resuelven.
5. **Cruce de code**: muestra code-pack vs code-oficial (INE/AGS/INSEE/ISTAT) coincide tras cross-walk. `sealed=false` si falta el denominador independiente.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **PRIMARIA — GeoNames dump** (allCountries.zip + hierarchy.zip + admin1CodesASCII.txt + admin2Codes.txt): loader pan-pais de una pasada, aplana ADM1→province / ADM2→comarca[nullable] / ADM3-4→municipality emitiendo el code OFICIAL; ES queda como adaptador degenerado (fuente INE, manifiesto 1:1). **CC-BY 4.0**, €0. https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377].
- **2-via INDEPENDIENTE — DataComPy** (diff added/removed/changed backbone-vivo vs snapshot autoritativo). **Apache-2.0**, €0. https://github.com/capitalone/datacompy [VERIFIED NEXT-LEVEL.md:417].
- **Contrato de ancho/forma pre-INSERT — Frictionless Framework** (Table Schema, captura el overflow ANTES del INSERT). **MIT**, €0. https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337].
- **Build reproducible/serverless en CI — DuckDB + spatial**. **MIT**, €0. https://github.com/duckdb/duckdb-spatial [VERIFIED NEXT-LEVEL.md:409].

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f6"></a>

#### F6 · Capa comarca opcional + trigger entity_set_comarca country-scoped

**Ficha rápida**

- **Costura (ES→genérico):** entity_set_comarca() resuelve comarca con 'WHERE m.code = NEW.municipality_code' SIN country_code [VERIFIED 0018_comarca.sql:30-31]; SELECT INTO sin STRICT toma fila arbitraria tras la PK compuesta de 0053. El verify() del piloto [VERIFIED pilot_country.py:242-302] nunca lee comarca_id.
- **Fix:** Migracion additiva CREATE OR REPLACE FUNCTION entity_set_comarca() con 'WHERE m.code = NEW.municipality_code AND m.country_code = NEW.country_code' (byte-identico ES, toda fila ES). Backbone 2-niveles deja comarca_id NULL valido. Ademas: el harness debe ASSERTear entity.comarca_id (cross-pais=0).
- **Adversarial:** DE/MX entity con muni homonimo '28001' hereda comarca_id ES -> FK compuesta de comarca falla o apunta a comarca de otro pais; sangrado cross-pais irreversible del nivel-medio que el verify() del piloto no detecta (nunca consulta comarca_id). PT/IT (6 digitos) no colisionan, pero cualquier pais ancho-5 si.
- **Sellado:** 1) Golden: entity extranjera en muni colisionante -> comarca_id NULL o extranjera, jamas ES. 2) 2a via SQL: count(e.comarca_id IS DISTINCT FROM m.comarca_id por JOIN compuesto)=0 (bleed=0). 3) ES byte-identidad: re-trigger sobre corpus ES, diff comarca_id=0. 4) verify() amplia asserts a comarca_id.
- **NEXT-LEVEL:** GeoNames N-niveles backbone loader (ADM2 -> comarca[nullable] via allCountries.zip + hierarchy.zip) — https://download.geonames.org/export/dump/ · CC-BY 4.0 · €0=True [VERIFIED NEXT-LEVEL.md:374-380]. Nota honesta: el fix del trigger es mecanico (un AND); la herramienta eleva el SOURCING generico de la capa comarca, no el parche.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED migrations/0018_comarca.sql:8-9] `geo_comarca` gana `ine_code CHAR(2)` + `source TEXT` (additive, nullable -> comarcas no-agrarias siguen validas).
- [VERIFIED migrations/0018_comarca.sql:27-35] funcion VIVA `entity_set_comarca()` (plpgsql):
  `IF NEW.municipality_code IS NOT NULL THEN SELECT m.comarca_id INTO NEW.comarca_id FROM geo_municipality m WHERE m.code = NEW.municipality_code; END IF;` — el `WHERE` cruza SOLO por `code`, sin `country_code`.
- [VERIFIED migrations/0018_comarca.sql:37-40] trigger `trg_entity_set_comarca BEFORE INSERT OR UPDATE OF municipality_code ON entity FOR EACH ROW EXECUTE FUNCTION entity_set_comarca()`.
- [VERIFIED migrations/0018_comarca.sql:18-21] indices parciales `idx_entity_comarca`/`idx_municipality_comarca WHERE comarca_id IS NOT NULL`.
- [VERIFIED scripts/pilot_country.py:242-302] `verify()` comprueba (a) coexistencia provincia 28, (b) FK compuesta muni->provincia [:262-277 lee `p.country_code=m.country_code AND p.code=m.province_code`], (c) `resolve_cluster` sin ES-bleed, (d) ES byte-identidad [:293-301]. NUNCA consulta `entity.comarca_id` -> el sangrado de nivel-medio es invisible al sello.

##### (b) Mecanismo al atomo
El nivel intermedio es `entity.comarca_id` (nullable), heredado del municipio. El trigger se dispara BEFORE en cada INSERT/UPDATE de `municipality_code` y resuelve `comarca_id` via `SELECT ... INTO`. El atomo de rotura: `SELECT m.comarca_id INTO NEW.comarca_id ... WHERE m.code = NEW.municipality_code`. En plpgsql un `SELECT ... INTO` SIN `STRICT` que casa >1 fila NO lanza error: asigna una fila ARBITRARIA (la primera que devuelva el plan). Pre-0053 `geo_municipality.code` era unico (mono-tenant ES) -> exactamente 1 fila -> correcto. Post-0053 la PK es compuesta `(country_code, code)` y `code` deja de ser unico: `'28001'` existe como (ES,...) y como (DE/MX,...). El trigger toma una fila al azar -> una entity extranjera hereda el `comarca_id` del municipio ES homonimo.

##### (c) Costura ES->generico + fix exacto
- Costura: predicado de join mono-tenant (`WHERE m.code = NEW.municipality_code`).
- Fix: migracion additiva (0054+) `CREATE OR REPLACE FUNCTION entity_set_comarca()` con `WHERE m.code = NEW.municipality_code AND m.country_code = NEW.country_code`. CREATE OR REPLACE = byte-identico para ES (toda fila ES casa solo el municipio ES). Backbone de 2 niveles deja `comarca_id` NULL (valido, como Ceuta/Melilla). Segundo fix obligatorio: el harness DEBE LEER `entity.comarca_id` para que el sangrado no pase verde.

##### (d) Riesgo adversarial concreto
DE/MX entity con muni homonimo '28001' hereda el `comarca_id` de la fila ES -> la FK compuesta de comarca luego falla o apunta a una comarca de OTRO pais. PT/IT (6 digitos) no colisionan en '28001' pero cualquier pais de ancho-5 colisiona exacto. `SELECT INTO` sin STRICT no avisa: corrupcion silenciosa e irreversible del nivel-medio. El `verify()` del piloto (pilot_country.py:242-302) jamas lee `comarca_id` -> el sello certifica verde sobre datos sangrados.

##### (e) Criterio de sellado + verificacion multi-via
1. Golden de sangrado: sembrar piloto extranjero con un muni cuyo `code` colisione con un municipio ES que TENGA `comarca_id`; insertar entity extranjera ahi; ASSERT `entity.comarca_id` es NULL o la comarca extranjera, JAMAS la ES.
2. 2a via (SQL ortogonal): `SELECT count(*) FROM entity e JOIN geo_municipality m ON m.country_code=e.country_code AND m.code=e.municipality_code WHERE e.comarca_id IS DISTINCT FROM m.comarca_id` debe ser 0 (bleed=0).
3. ES byte-identidad: re-disparar el trigger sobre el corpus ES -> diff de `comarca_id` = 0.
4. Cierre del punto ciego: `verify()` amplia sus asserts a `comarca_id` (cross-pais = 0).

##### (f) Herramienta next-level
El fix del trigger es plumbing mecanico (un AND), no necesita herramienta. Lo que ELEVA la CAPA comarca a nivel inalcanzable es el sourcing generico del nivel-medio: **GeoNames N-niveles backbone loader** (allCountries feature_code ADM2 -> comarca[nullable], hierarchy.zip resuelve el padre) — un solo ingestor cubre el nivel-medio de cualquier pais y ES queda como adaptador degenerado (comarca agraria INE 1:1). URL https://download.geonames.org/export/dump/ · Lic CC-BY 4.0 · €0=True [VERIFIED NEXT-LEVEL.md:374-380].

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f7"></a>

#### F7 · Taxonomia de region nivel-1 (ccaa) + ancho + regla de sintesis

**Ficha rápida**

- **Costura (ES→genérico):** El dato de region nivel-1 (codigo + nombre + ANCHO) y la asignacion provincia->CCAA viven como literales ES de modulo en load_geo.py (CCAA dict :25-34 + columna CODAUTO de PROVINCES :37-56), y el contrato de columna (CHAR(2) NOT NULL sin default) vive en 0001_geo.sql:7-8. La etiqueta de region debe pasar a ser un campo del GeoProfile/country-pack (F8) con ES por defecto reproduciendo byte-identico el CODAUTO INE; el ancho CHAR(2) debe ensancharse (cruza con F1) para codigos de region no-2-char (MX/JP/DE ISO 3166-2); y -- lo critico -- el pack debe declarar una REGLA DE SINTESIS honesta para paises sin agrupacion supra-provincial, en vez de inventar un relleno como hace el piloto con 'BB'/'BE'. ES nunca se reescribe: el pack ES = los dos dicts actuales verbatim.
- **Fix:** Schema (additivo, ES byte-identico): ALTER TABLE geo_province ALTER COLUMN ccaa_code TYPE VARCHAR(N) con N del seal manifest (los valores '01'..'19' son ya exactamente 2 chars, sin trailing-space, asi que el cast CHAR(2)->VARCHAR es limpio; verificar que ninguna provincia tenga codigo de 1 char). Mantener NOT NULL pero el VALOR lo provee el pack. Loader: leer region_code/region_name por provincia desde el dataset del pack (pack ES = CCAA + PROVINCES actuales), no desde constantes de modulo. Regla de sintesis: el pack declara region_policy in {native_admin1, province_is_region, country_is_region}. MX/DE/JP -> native_admin1 derivado de ISO 3166-2 (pycountry). Pais plano sin super-region -> province_is_region (region_code=province_code, region_name=province_name): honesto, no inventado; el NOT NULL queda satisfecho por una derivacion REAL, no por un literal de relleno.
- **Adversarial:** DE: 16 Bundeslander, ISO 3166-2 'DE-BW'..'DE-TH' (5 char con prefijo) o nativo 2-char 'BW'/'BY'. Si el pack mapea a la forma ISO completa 'DE-BW' (5 char) -> overflow CHAR(2) 'value too long for type character(2)'. Si mapea al 2-char desnudo, encaja solo por suerte de ancho. MX: 32 estados ISO 'MX-AGU' (3-char nativo) -> overflow. JP: 47 prefecturas; 2-digit encaja, forma ISO 'JP-01' overflow. PT: 18 distritos (ancho OK a 2) pero el concepto 'region' (NUTS vs distrito) es ambiguo; elegir mal el grano mislabela. Pais SIN region / ruido: un pais de administracion plana NO tiene capa supra-provincial; forzar un relleno 2-char ('BB') fabrica una taxonomia -> el sello valida una mentira. Un pais con codigo de region de 3 chars viola NOT NULL CHAR(2) -> INSERT abortado a mitad del onboarding. El piloto 'BB'/'BE' (pilot_country.py:118-119,124-125) oculta TODO esto: nunca ejerce un ancho real, un conteo real, ni la rama no-region.
- **Sellado:** Sello = 4 vias ortogonales. (1) ES golden fila-a-fila: pack ES reproduce el CODAUTO de las 52 provincias byte-identico, cero drift. (2) Sanity de conteo+ancho por pais desde ISO 3166-2 via pycountry (DE=16, MX=32, JP=47, IT=20, FR metro+ultramar), cruzado contra 2a fuente independiente (iso3166/Wikipedia). (3) Rama no-region ejercida por un fixture forma-extranjera real (cruza F23): un pais province_is_region inserta region_code=province_code derivado y el harness asserta que NINGUN literal sintetico 'BB' sobrevive a una fila sellada. (4) Fail-closed: region ausente en el pack FALLA el load (Great Expectations/frictionless), jamas rellena en silencio. Criterio: el sello solo es verde cuando una taxonomia REAL (no fake) pasa para >=1 pais sin agrupacion supra-provincial.
- **NEXT-LEVEL:** pycountry (ISO 3166-1/-2 + ISO 4217) [VERIFIED NEXT-LEVEL.md:530] - LGPL-2.1 - EUR0=True - https://github.com/pycountry/pycountry. Empaqueta el dataset Debian iso-codes: el conteo y el ancho-de-codigo de las subdivisiones de nivel-1 de cada pais se vuelven DATO que alimenta un seal manifest por pais (region count + geo_unit_width), retirando los centinelas forma-ES. Build/config-time only (no hot-path) -> data-use LGPL no-issue; alt estricta-permisiva = iso3166 (MIT, solo paises) + JSON crudo iso-codes de subdivisiones [VERIFIED NEXT-LEVEL.md:531-532]. Eleva la taxonomia de region a country-proof y auto-fijada (la decision native_admin1 vs province_is_region se DERIVA del estandar, no se adivina).

**Deep-spec 360**

##### (a) code_hints verificados al byte
- **[VERIFIED migrations/0001_geo.sql:7-8]** En `geo_province`: `ccaa_code CHAR(2) NOT NULL` (l.7, comentario "autonomous community code") + `ccaa_name TEXT NOT NULL` (l.8). **Sin DEFAULT**. La region nivel-1 NO es una tabla propia: esta DENORMALIZADA como dos columnas que cada fila de provincia porta.
- **[VERIFIED scripts/load_geo.py:25-34]** `CCAA = {...}` dict CODAUTO->nombre, **19 entradas** (estandar INE: "01":"Andalucia" ... "19":"Melilla"). Es 100% ES a nivel de modulo.
- **[VERIFIED scripts/load_geo.py:37-56]** `PROVINCES = {code: (name, CODAUTO)}` 52 entradas; el segundo elemento de la tupla es el CODAUTO que ata cada provincia a su CCAA. La asignacion provincia->region esta hardcodeada ES.
- **[VERIFIED scripts/load_geo.py:83]** `[(code,name,ccaa,CCAA[ccaa]) for code,(name,ccaa) in PROVINCES.items()]` -> el INSERT toma `ccaa_code=ccaa` (el CODAUTO, 2 digitos exactos) y `ccaa_name=CCAA[ccaa]`.
- **[VERIFIED scripts/pilot_country.py:112-127]** `_provinces(country)` devuelve 2 provincias sinteticas con `ccaa_code:"BB"`/`"BE"` (2-char inventado) y `ccaa_name:"Brandenburg"`/`"Berlin"`. El piloto SATISFACE el NOT NULL CHAR(2) inventando etiquetas de 2 chars; jamas ejerce una taxonomia real ni un ancho != 2.

##### (b) Mecanismo al atomo
`ccaa_code CHAR(2)` es ancho-fijo: un valor < 2 chars se rellena con espacio a la derecha (blank-pad); un valor > 2 chars revienta con `value too long for type character(2)`. `NOT NULL` sin DEFAULT obliga a que CADA INSERT entregue un valor no nulo. Para ES el CODAUTO INE encaja exacto en CHAR(2) (siempre 2 digitos, '01'..'19'), por eso nunca hubo padding ni overflow y el contrato parecio universal. El atomo de dependencia-pais: el ANCHO (2), la OBLIGATORIEDAD (NOT NULL), y la EXISTENCIA de una agrupacion supra-provincial estan los tres asumidos a la forma INE. Un pais sin nivel supra-provincial no puede satisfacer NOT NULL sin (i) una taxonomia real o (ii) una regla de sintesis declarada -- jamas un relleno.

##### (c+d) Costura y riesgo: ver campos seam/adversarial.

##### (e) Sello multi-via
1. **ES golden**: el mapeo region derivado del pack ES reproduce byte-identico las 52 provincias x su CODAUTO (dict CCAA + columna CODAUTO de PROVINCES), fila a fila, cero drift.
2. **Conteo/ancho por pais desde ISO 3166-2 (pycountry)**: DE=16 Bundeslander, MX=32 estados, JP=47 prefecturas, IT=20 regiones, FR metropolitana+ultramar -- cruzado contra 2a fuente independiente (iso3166 / Wikipedia ground-truth); el `region_width` derivado debe sostener TODO codigo real sin overflow.
3. **Rama no-region ejercida por fixture extranjero real** (cruza F23): un pais declarado `province_is_region` inserta con region_code=province_code (valor DERIVADO, no inventado) y pasa NOT NULL; el harness asserta que ningun literal sintetico tipo 'BB' sobrevive a una fila sellada.
4. **Contrato fail-closed**: una region ausente en el pack debe FALLAR el load (frictionless/Great Expectations), nunca rellenar en silencio.

##### (f) Palanca next-level
**pycountry** (ISO 3166-1/-2 + ISO 4217) **[VERIFIED NEXT-LEVEL.md:530]** LGPL-2.1, EUR0, https://github.com/pycountry/pycountry. Empaqueta el dataset Debian iso-codes; el CONTEO y el ANCHO-de-codigo de las subdivisiones de nivel-1 de cada pais se vuelven DATO que alimenta un seal manifest por pais (geo_unit_level, geo_unit_width, region count), retirando los centinelas con forma-ES. Uso build/config-time (no hot-path) -> el data-use LGPL es no-issue; alternativa estricta-permisiva = iso3166 (MIT, solo paises) + JSON crudo de subdivisiones iso-codes **[VERIFIED NEXT-LEVEL.md:531-532]**. Es la fuente autoritativa EUR0 que vuelve la taxonomia de region (conteo + ancho + decision de sintesis) country-proof y auto-fijada en vez de derivada a mano.

↩ [Índice de sub-proyectos](#indice-sub)

---

<a id="capa-2"></a>

### Capa II · Resolver textual, perfil y normalización (F8–F14)

> La cascada nombre→código y su gobierno: el registro `GeoProfile` que consolida todo literal ES, el country-scoping del resolver, las DOS normalizaciones (resolver recomputable vs identidad inmutable — Raíz B), alias, gazetteer y fuzzy. El plano donde una mala normalización corrompe identidad para siempre.

<a id="f8"></a>

#### F8 · GeoProfile registry (espina dorsal de literales ES)

**Ficha rápida**

- **Costura (ES→genérico):** git grep GeoProfile = CERO [VERIFIED]: pieza nueva. Patron a espejar ya vivo: paths.py:22 DEFAULT_COUNTRY='ES' + helpers con default+root override [VERIFIED:33-52]; codes.py:24 idem + mint_code [VERIFIED:44-53]. Literales ES dispersos: geo.py:61-73 _PROVINCE_ALIASES dict 100% ES A NIVEL DE MODULO [VERIFIED], geo.py:46-48 _GAZETTEER_PATH unica ES, geocode.py:49 KNN=30, complete.py:73 _PROVINCE_RE.
- **Fix:** Nuevo pipeline/geo_profile.py: dataclass GeoProfile(country_code, aliases, gazetteer_path, norm_strategy, knn_max_km, region_label_rule, shape_predicate) + _REGISTRY + for_country(cc='ES'). Registrar ES con los literales actuales movidos desde geo.py/geocode.py. Consumidores se INSTANCIAN por perfil: GeoResolver.load(conn, profile). Default 'ES' EXACTO (como paths.py:22) -> byte-identico; un default mal puesto re-keya 431k entidades.
- **Adversarial:** Singleton trap: si el perfil es global mutable (como _PROVINCE_ALIASES a nivel modulo geo.py:61) un proceso multi-pais comparte indices -> DE/FR ven alias ES (menorca->07 mis-rutea texto homonimo). DE/FR sin alias no resuelven Bayern/Sachsen. Defaulting != 'ES' exacto cambia un cdp_code inmutable. La instanciacion por-pais es el invariante; el aislamiento debe ser por construccion, no filtro a posteriori.
- **Sellado:** GeoProfile existe + registra ES con literales actuales; consumidores instanciados por perfil (no globales); golden ES byte-identico en todos los call-sites; test de doble-instancia (resolver ES y DE vivos en el mismo proceso devuelven codigos disjuntos para texto homonimo). Multi-via: golden por call-site + test aislamiento doble-instancia + guard Pydantic de biyeccion del registry en CI.
- **NEXT-LEVEL:** Pydantic -- MIT, EUR0 -- https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]: CountryPack(BaseModel) con validators de coherencia + tests/test_registry_drift.py que itera active_countries() y falla rojo si la biyeccion registry no cierra (0 UNMAPPED/0 ORPHAN), sin DB viva. El perfil pasa de dataclass confiado a contrato tipado y probado.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- `git grep "GeoProfile"` en `*.py` -> CERO [VERIFIED]: la pieza NO existe, es construccion nueva.
- Patron a espejar -- `pipeline/paths.py:22` `DEFAULT_COUNTRY = "ES"`; helpers `recipe_root/data_root/census_dir` (`:33-52`) que DEFAULTean a `DEFAULT_COUNTRY` y aceptan `root` override [VERIFIED]; `country_of_cdp` (`:55-63`) deriva el pais del prefijo `CDP-XX-`. El docstring (`:6-9`) declara la doctrina: "centralizes those roots behind helpers that DEFAULT to ES so the resolved paths are byte-identical".
- `services/api/codes.py:24` `DEFAULT_COUNTRY = "ES"`; `mint_code` (`:44-53`) es "the ONE home of the prefix literal"; `canonical_key` (`:56-97`) acepta `country_code` pero deliberadamente NO lo usa en la pre-imagen (`:62-65`) para no re-keyar.
- Literales ES dispersos a consolidar: `pipeline/geo.py:61-73` `_PROVINCE_ALIASES` (dict 100% ES a NIVEL DE MODULO: `alava->01`, `menorca->07`...) [VERIFIED]; `geo.py:46-48` `_GAZETTEER_PATH` (ruta unica ES); `geo.py:51-53` `_norm` (estrategia ascii-fold); `geocode.py:49` `KNN_MAX_DISTANCE_KM=30.0`; `complete.py:73` `_PROVINCE_RE` (01-52); regex de sufijo-pais; etiqueta de region.

##### (b) Mecanismo al atomo
El patron `paths.py`/`codes.py` es el molde EXACTO: una constante `DEFAULT_COUNTRY="ES"` + funciones que la toman por defecto -> todo call-site sin tocar resuelve ES byte-identico, y pasar otro `country_code` es lo UNICO que cambia el output. `GeoProfile` lo eleva de funciones-con-default a un dataclass registrado por country_code que agrupa TODOS los literales geo en un objeto: `aliases`, `gazetteer_path`, `norm_strategy`, `knn_max_km`, `country_suffix_re`, `region_label`, `shape_predicate`. El atomo critico es el defaulting y la INSTANCIACION: hoy `_PROVINCE_ALIASES` es un dict a nivel de modulo (`geo.py:61`) -> se carga UNA vez en el namespace del proceso y lo comparten TODOS los runs/paises. `GeoProfile` debe entregarse por-instancia (`GeoProfile.for_country("ES")`) y los consumidores (GeoResolver, geocoders) instanciarse CON el perfil, de modo que la contaminacion cross-pais sea imposible POR CONSTRUCCION, no por filtro a posteriori.

##### (c) Costura ES->generico + fix exacto
Nuevo `pipeline/geo_profile.py`:
```python
@dataclass(frozen=True)
class GeoProfile:
    country_code: str
    aliases: Mapping[str, str]
    gazetteer_path: Path
    norm_strategy: str          # "ascii_fold" | "translit_then_fold"
    knn_max_km: float
    region_label_rule: str
    shape_predicate: str | None  # ES: "left(code,2)=province_code"; DE/FR: None

_REGISTRY: dict[str, GeoProfile] = {}
def register(p: GeoProfile) -> None: _REGISTRY[p.country_code] = p
def for_country(cc: str = "ES") -> GeoProfile: return _REGISTRY.get(cc, _REGISTRY["ES"])
```
El perfil ES se registra con EXACTAMENTE los literales actuales (`_PROVINCE_ALIASES` movido aqui, `_GAZETTEER_PATH`, `_norm` ascii-fold, 30.0). Los call-sites pasan de leer globales de modulo a `profile = geo_profile.for_country(run_country)` -> `GeoResolver.load(conn, profile)`. Default `"ES"` implica byte-identico. El defaulting debe ser EXACTAMENTE `"ES"` (igual que `paths.py:22`/`codes.py:24`): un default mal puesto cambiaria un solo cdp_code y re-keyaria 431k entidades.

##### (d) Riesgo adversarial concreto
- Singleton trap: si `GeoProfile` se implementa como singleton global (replicando el error de `_PROVINCE_ALIASES` a nivel de modulo), un proceso multi-pais comparte indices -> DE/FR ven los alias ES. La INSTANCIACION por-pais es el invariante; un atajo de "registro global mutable" reintroduce el sangrado.
- DE/FR sin alias: `Bayern`/`Sachsen` no resuelven porque el dict ES no los tiene, y peor, un texto extranjero homonimo podria mis-rutear a un codigo ES (`menorca->07`).
- Defaulting roto: cualquier path que no devuelva EXACTAMENTE `"ES"` para legacy (p.ej. `None`->`""`) cambia el prefijo minteado -> identidad ES alterada e inmutable.
- PT/IT/no-UE: cada uno necesita su `shape_predicate` (None para DE/FR sin relacion prefijo) -- sin el registro, el predicado sigue triplicado y hardcodeado (cruza con F3).

##### (e) Criterio de sellado + verificacion multi-via
SELLADO si y solo si (1) `GeoProfile` existe y registra ES con los literales actuales; (2) GeoResolver/geocoders se instancian POR perfil (no globales); (3) golden ES byte-identico en TODOS los consumidores; (4) test adversarial de aislamiento: dos perfiles (ES, DE) vivos en el mismo proceso NO comparten indice. Multi-via: via A golden de output ES inalterado por call-site; via B test de doble-instancia (resolver ES y resolver DE en el mismo runtime devuelven codigos disjuntos para texto homonimo); via C el guard tipado Pydantic (tool) que asevera la biyeccion del registry en CI.

##### (f) Herramienta de elevacion
Pydantic -- MIT, EUR0 -- https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela el country-pack/GeoProfile como `CountryPack(BaseModel)` con validators de coherencia y un test de CI (`tests/test_registry_drift.py`) que itera `active_countries()` y FALLA si la biyeccion `source_health <-> registry <-> lock_key` no cierra (0 UNMAPPED / 0 ORPHAN). Convierte el "registry drift" silencioso de cada onboarding en un build ROJO mecanico, sin DB viva (fixtures), EUR0. Es exactamente el "GOBIERNO DE COBERTURA" que el diseno nombra pero deja como test aspiracional -- el perfil deja de ser un dataclass confiado para ser un contrato tipado y probado.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f9"></a>

#### F9 · GeoResolver country-scoping (texto nombre->codigo)

**Ficha rápida**

- **Costura (ES→genérico):** geo.py:150-183 load(cls, conn) NO tiene country_code; geo.py:153 y :157 fetchean 'SELECT ... FROM geo_province/geo_municipality' SIN WHERE country_code, volcando TODOS los paises a un solo conjunto de 5 indices (_prov/_muni/_city_global/_locality/_muni_names). Tras 0053 'code' ya no es unico (ES-28+DE-28), asi que los indices funden homonimos cross-pais.
- **Fix:** Aditivo en la firma: load(cls, conn, country_code: str = 'ES'); geo.py:153 'SELECT code,name FROM geo_province WHERE country_code=$1'; geo.py:157 'SELECT code,name,province_code FROM geo_municipality WHERE country_code=$1'; clavar cada indice interno por pais; los productores (discover.py:127-131, F20) pasan el country del run; _PROVINCE_ALIASES deja de inyectarse incondicional (a perfil F12). Default 'ES' selecciona exactamente las 52+8.132 filas de hoy -> 5 indices byte-identicos, cero codigos cambiados. El resolver pasa de singleton-global a instancia-por-pais; contaminacion imposible por construccion.
- **Adversarial:** DE: municipality_code('28','Potsdam') busca en _muni['28'] que mezcla el muni ES-28xxx y el DE-28001 -> devuelve el code del homonimo equivocado; si alimenta cdp_code (F11/F20) es INMUTABLE. PT/IT/FR (mismo ancho): resolve_city_global con len(hits)==1 colapsa dos municipios de paises distintos si comparten nombre normalizado. no-UE: MX comparte homonimos con ES (Guadalajara/Madrid/Cordoba/Leon) -> el indice global devuelve el INE code ES para un run MX.
- **Sellado:** El resolver es instancia por-pais y el golden ES no mueve un codigo (contrato B4, geo.py:186-187). Multi-via: (1) golden ES byte-identico re-resolviendo corpus con load(conn,'ES'); (2) aislamiento cross-pais: sembrar DE-28/Potsdam, assert load(conn,'DE').municipality_code('28','Potsdam')=code DE y load(conn,'ES') jamas ve la fila DE (indices disjuntos), probando el homonimo deliberado; (3) via ortogonal texto-vs-espacial country-scoped convergen (cruza F15); (4) via firma: default 'ES' identico a la firma vieja.
- **NEXT-LEVEL:** libpostal (MIT) — https://github.com/openvenues/libpostal [VERIFIED NEXT-LEVEL.md:345]. Parser estadistico (1B+ direcciones, 60+ idiomas) que entrega province/city/postcode/country TIPADOS a GeoResolver.municipality_code(province,city), eliminando las heuristicas ES (regex sufijo ', Spain', troceo ad-hoc). EUR0: compila en C (apt + ~2GB modelos una vez), pypostal envuelve, modelo estatico reproducible OSM+OpenAddresses+OpenCage (NEXT-LEVEL.md:347). 2-via ortogonal: province/city libpostal vs GeoResolver convergen o hueco confesado (NEXT-LEVEL.md:348). Data-side: GeoNames loader (CC-BY 4.0, NEXT-LEVEL.md:377) + alternateNames mining (CC-BY 4.0, NEXT-LEVEL.md:385).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/geo.py:150-183`** [VERIFIED]: `@classmethod async def load(cls, conn: asyncpg.Connection)` — la firma **NO tiene parametro country_code**. Construye una unica instancia con 5 indices internos: `_muni` (`:131`), `_prov` (`:132`), `_city_global` (`:133`), `_locality` (`:134`), `_muni_names` (`:136`).
- **`geo.py:153`** [VERIFIED]: `for r in await conn.fetch("SELECT code, name FROM geo_province")` — **SIN `WHERE country_code`**. Indexa TODAS las provincias de TODOS los paises en `_prov`.
- **`geo.py:157`** [VERIFIED]: `for r in await conn.fetch("SELECT code, name, province_code FROM geo_municipality")` — **SIN `WHERE country_code`**. Indexa TODOS los municipios en `_muni[province_code]` y en `_city_global[key] = {(province_code, code)}` (`:170`).
- **`geo.py:189-198`** [VERIFIED]: `resolve_city_global(city)` devuelve `(prov, code)` solo si el nombre mapea a EXACTAMENTE 1 municipio nacional (`:195 len(hits)==1`); con homonimos cross-pais, `hits` mezcla paises.
- **`geo.py:200-207`** [VERIFIED]: `province_code(name_or_code)` — si `s.isdigit()` hace `s.zfill(2)` y comprueba `c in self._muni` (`:204-206`); si es texto, `self._prov.get(_norm(s))`. El indice `_prov` es global multi-pais.
- **`geo.py:209-234`** [VERIFIED]: `municipality_code(province_code, muni_name)` — cascada exacta (`:224`) -> fuzzy (`:229`) -> gazetteer locality (`:234`), TODO scopeado al `province_code` pasado, que NO lleva pais.
- **`geo.py:155-156`** [VERIFIED]: `_PROVINCE_ALIASES` (dict 100% ES, `:61-73`) se inyecta en `_prov` para CUALQUIER carga (cruza con F12).

##### (b) Mecanismo al atomo
`GeoResolver` es un singleton-por-carga: una `load()` produce una instancia con 5 dicts en memoria que mapean claves normalizadas de nombre -> codigo. El scoping del indice es por `province_code` (string desnudo), NUNCA por pais. Tras 0053 el universo de filas es multi-tenant: `code` ya no es unico (ES-28 + DE-28 coexisten, F2). El atomo de rotura: los dos `conn.fetch` (`:153,:157`) vuelcan TODAS las filas a un solo conjunto de indices, asi que `_prov['madrid']` y `_prov['brandenburg']` (DE, code '28') colisionan en el value '28', y `_city_global['potsdam']` puede contener `{('28', '28001')}` de DE junto a un homonimo ES. La firma publica (`province_code`, `municipality_code`, `resolve_city_global`) es el contrato B4 (`:186-187`) y NO debe cambiar de salida para ES. El fix es puramente aditivo en la FIRMA de carga: `load(conn, country_code='ES')` + `WHERE country_code=$1` en los 2 fetch + clavar cada indice interno por pais. Como hoy todo es ES, el default 'ES' produce indices byte-identicos. El resolver pasa de singleton-global a instancia-por-pais; la contaminacion cross-pais se vuelve imposible POR CONSTRUCCION (el indice solo contiene filas de su pais), no por filtro a posteriori.

##### (c) Costura ES -> generico
1. `load(cls, conn)` -> `load(cls, conn, country_code: str = 'ES')` (default preserva todos los call-sites ES sin tocar).
2. `geo.py:153`: `SELECT code, name FROM geo_province WHERE country_code=$1`, country_code.
3. `geo.py:157`: `SELECT code, name, province_code FROM geo_municipality WHERE country_code=$1`, country_code.
4. Los call-sites productores (`pipeline/discover.py:127-131`, cruza con F20) pasan el country del run; default ES -> byte-identico.
5. `_PROVINCE_ALIASES` deja de inyectarse incondicionalmente (mueve a perfil F12); para ES el set es identico.
**ES byte-identico**: con un solo tenant ES, `WHERE country_code='ES'` selecciona exactamente las 52+8.132 filas de hoy; los 5 indices salen identicos; ningun codigo cambia.

##### (d) Riesgo adversarial concreto
- **DE (homonimo de codigo)**: tras sembrar DE, `province_code('Madrid')` y un texto que normaliza a un nombre DE comparten el espacio `_prov`; peor, `municipality_code('28', 'Potsdam')` busca en `_muni['28']` que ahora mezcla el muni ES-28xxx y el DE-28001 -> puede devolver el code del homonimo del otro pais. Identidad cruzada minteada (si el resultado alimenta cdp_code, F11/F20, es INMUTABLE).
- **PT/IT/FR (mismo ancho de provincia)**: IT provincia 2-digit, PT/FR con prefijos numericos solapados -> `resolve_city_global` con `len(hits)==1` puede colapsar dos municipios de paises distintos a 1 si comparten nombre normalizado, devolviendo un par (prov, code) del pais equivocado.
- **Ruido**: un texto basura que normaliza a '' (cruza con F10) ya devuelve None; pero un texto valido de pais B procesado en un run de pais A, con el indice global, resuelve silenciosamente al codigo de A.
- **no-UE (MX 'Madrid')**: MX tiene municipios homonimos de ES (Guadalajara, Madrid, Cordoba, Leon) -> el indice global los funde; un run MX devuelve el INE code ES.

##### (e) Criterio de sellado + verificacion multi-via
**Sello = el resolver es una instancia por-pais y el golden ES no mueve un solo codigo.** Multi-via:
1. **Golden ES byte-identico**: re-resolver un corpus ES con `load(conn,'ES')` -> mismos codigos que hoy (cero drift). Es el contrato B4 (`geo.py:186-187`).
2. **Aislamiento cross-pais**: sembrar DE-28/Potsdam, cargar `load(conn,'DE')`, y assert que `municipality_code('28','Potsdam')` devuelve el code DE y `load(conn,'ES').municipality_code('28', <muni ES>)` jamas ve la fila DE (indices disjuntos). Probar el homonimo deliberado (Madrid ES vs Brandenburg DE en code '28').
3. **Via ortogonal texto vs espacial** (cruza con F15): el resolver textual y el geocoder KNN, ambos country-scoped, deben converger en el mismo municipio para una muestra; divergencia = hueco.
4. **Via firma**: test que `load` rechaza/!acepta country_code y que la salida del default 'ES' es identica a la firma vieja.

##### (f) Herramienta next-level
**libpostal** (MIT) — https://github.com/openvenues/libpostal [VERIFIED NEXT-LEVEL.md:345]. El scoping por pais (F9) hace al resolver CORRECTO multi-tenant; libpostal lo hace INALCANZABLE: un parser estadistico entrenado en 1B+ direcciones que devuelve componentes etiquetados (house_number, road, city, state/province, postcode, country) en 60+ idiomas, alimentando `GeoResolver.municipality_code(province, city)` con campos YA TIPADOS (`NEXT-LEVEL.md:343`). El resolver deja de adivinar "que token es la provincia" con heuristicas ES (el regex de sufijo ', Spain'/', Espana' y el troceo ad-hoc) y recibe province/city/postcode segmentados country-agnostico — un texto DE/JP con orden de campos distinto (CP primero, calle al final) que hoy no se parsea pasa a segmentarse. Ruta EUR0: compila en C (apt build-essential + ~2GB modelos descargados una vez), pypostal envuelve; sin servicio ni API de pago; modelo estatico reproducible (OSM+OpenAddresses+OpenCage, `NEXT-LEVEL.md:347`). Verificacion 2-via ortogonal: el province/city de libpostal vs el del GeoResolver sobre el mismo texto crudo deben converger; divergencia = hueco confesado, no merge (`NEXT-LEVEL.md:348`). Complementos data-side: GeoNames loader (CC-BY 4.0, `NEXT-LEVEL.md:377`) puebla el backbone country-scoped, y alternateNames mining (CC-BY 4.0, `NEXT-LEVEL.md:385`) llena el resolver de variantes multilingues sin curado manual.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f10"></a>

#### F10 · Normalizacion — plano RESOLVER (_norm)

**Ficha rápida**

- **Costura (ES→genérico):** `_norm` es funcion de modulo global, identica para todo pais y soldada a escritura Latina: `unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode("ascii")` [VERIFIED geo.py:51-53], con `_sorted_key` construido encima [VERIFIED geo.py:56-57]. No hay inyeccion per-pais; el `GeoResolver`, `_PROVINCE_ALIASES` y el gazetteer clavan sus indices con estas funciones. Para Latino-1 (ES/DE/FR/IT/PT) el fold es correcto; para no-Latino `encode('ascii','ignore')` colapsa a cadena vacia. Separacion institucional: este es el INDICE RECOMPUTABLE del resolver, distinto y MENOS grave que el path de identidad/mint (F11) — un fallo aqui se repara recargando el indice, sin dano permanente.
- **Fix:** Mover `_norm` a estrategia del `GeoProfile` (F8): `profile.normalize_resolver(text)`. ES/Latino conservan el cuerpo actual literal (NFKD + `encode('ascii','ignore')` + lower + `re.sub`) -> byte-identico, golden de indice ES sin drift. No-Latino (EL/BG/RU/CJK/JP) anteponen `anyascii(text)` ANTES del fold: 'Αθηνα'->'athina', 'Москва'->'moskva', '横浜'->'yokohama' en vez de ''. `_sorted_key` no se toca (hereda la correccion via `_norm`). El `GeoResolver` instancia-por-pais (F9) recibe `profile` y clava sus indices con `profile.normalize_resolver`, imposibilitando mezcla de estrategias cross-pais. Reversible por construccion: recargar el indice basta, sin migracion (a diferencia de F11).
- **Adversarial:** EL griego / BG-RU cirilico / CJK / JP: `encode('ascii','ignore')` -> '' -> el resolver queda CIEGO (toda clave vacia colisiona), resolucion texto->codigo imposible para esos paises — ceguera total del escalon exacto, no un sesgo. DE: funciona pero degradado, 'Straße'->'strae' pierde 'ss' y los nombres compuestos largos pierden senal de match fino (recall baja, no a 0). Mixto: un token no-Latino intercalado se pierde; si era el discriminante, el match se degrada sin error. PT/FR/IT (Latino): sin riesgo — el fix debe dejarlos byte-identicos o introduce regresion gratuita.
- **Sellado:** Sellado cuando `_norm` es estrategia del perfil, ES/Latino es byte-identico, y ningun pais registrado produce clave vacia para nombre no-vacio. Multi-via: (1) ES/Latino byte-identico — re-clavar indice ES y diff = 0; alias y gazetteer ES resuelven igual; (2) adversarial no-vacio — fixture {'Αθηνα','Москва','横浜','Straße'} con `assert normalize_resolver(x)!=""` y dos no-Latino distintos no comparten clave; (3) recuperabilidad — recargar el indice con la nueva estrategia recupera el matching sin tocar dato persistido (confirma reversibilidad, separa F10 de F11); (4) ortogonal — AnyAscii vs romanizacion de fuente (GeoNames asciiname) convergen en muestra; la divergencia (Pinyin vs romaji) se tolera en el resolver y se reserva source-first para F11.
- **NEXT-LEVEL:** AnyAscii — ISC — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:326-332 y :221-227]: transliteracion data-driven sin dependencias nativas (~200-500KB tablas embebidas [VERIFIED NEXT-LEVEL.md:331]), ISC permisiva — la via limpia frente a unidecode (GPL, contamina la API) e ICU. Drop-in en el call-site `_norm` bajo la rama de script de `pack.normalize_policy`: 'Αθηνα'->'athina', '横浜'->'yokohama'. Para el plano resolver (recomputable) la transliteracion algoritmica basta; el "source-romaji-first" que evita Pinyin-en-JP es exigencia de F11 (identidad inmutable), no de F10. €0, CPU puro.

**Deep-spec 360**

##### (a) Verificacion de code_hints [leido a fuente]
- **[VERIFIED pipeline/geo.py:51-53]** `def _norm(text: str) -> str:` -> `text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")` y `return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()`. El `encode("ascii","ignore")` DESCARTA todo punto de codigo no-ASCII tras descomponer NFKD.
- **[VERIFIED pipeline/geo.py:56-57]** `def _sorted_key(text: str) -> str:` -> `return " ".join(sorted(_norm(text).split()))` — clave token-order-invariante construida ENCIMA de `_norm`, asi que hereda su perdida.
- Consumidores [VERIFIED por lectura del modulo]: `_PROVINCE_ALIASES` (geo.py:61-73) y el gazetteer (`_load_gazetteer` :111 `raw_norm = _norm(raw)`, :118 `for key in (raw_norm, _sorted_key(raw))`) construyen sus indices con estas dos funciones; el `GeoResolver` (clase desde :129) clava `_prov/_muni/_locality` con claves `_norm`/`_sorted_key`.

CONCLUSION: `_norm` es la funcion-clave del INDICE del resolver textual. Para Latino-1 (ES) el NFKD+drop produce el fold esperado ('Cadiz'->'cadiz', 'A Coruna'->'a coruna'); para NO-Latino colapsa a cadena vacia.

##### (b) Mecanismo al atomo
`_norm` hace 4 pasos atomicos: (1) NFKD descompone cada grafema en base + marcas combinantes; (2) `encode('ascii','ignore')` TIRA todo byte > 0x7F (las marcas combinantes Y los caracteres base no-ASCII); (3) `lower()` + (4) `re.sub` colapsa no-alfanumerico a espacio. Para 'Munchen' (u-umlaut) NFKD da 'Mu'+combinante+'nchen' -> drop de la combinante -> 'munchen' (correcto). Para la eszett 'Straße' NFKD NO descompone ß -> drop -> 'strae' (pierde 'ss', sub-optimo pero no vacio). Para 'Αθηνα' (griego) / 'Москва' (cirilico) / '横浜' (han): NINGUN punto es ASCII -> `encode('ascii','ignore')` -> **''** -> clave vacia. El indice del resolver, clavado por `_norm(name)`, queda con clave vacia para todo nombre no-Latino: colision masiva o ceguera total.
CLAVE INSTITUCIONAL (la separacion mas critica del stage): este es el INDICE RECOMPUTABLE del resolver, NO el path de identidad/mint (F11). Un fallo aqui se REPARA recargando el indice con la estrategia corregida; no hay dano permanente. Por eso F10 y F11 son proyectos distintos aunque compartan la linea-bug: F10 es reversible, F11 es append-only e inmutable.

##### (c) Costura ES->generico + fix exacto
**Costura**: `_norm` es una funcion de modulo global, identica para todo pais; asume escritura Latina. No hay punto de inyeccion per-pais.
**Fix exacto**:
1. Convertir `_norm` en estrategia del `GeoProfile` (F8): `profile.normalize_resolver(text) -> str`. ES/Latino (ES/DE/FR/IT/PT) mantienen EXACTAMENTE el cuerpo actual (NFKD + `encode('ascii','ignore')` + lower + sub) -> byte-identico, golden de indice ES sin drift.
2. No-Latino (EL/BG/RU/CJK/JP) registran una transliteracion ANTES del fold: `text2 = anyascii(text)` y luego el mismo `re.sub`/lower. 'Αθηνα'->'athina', 'Москва'->'moskva', '横浜'->'yokohama' (romanizacion) en vez de ''.
3. `_sorted_key` no se toca: al apoyarse en `_norm` via el perfil, hereda la correccion automaticamente.
4. El `GeoResolver` recibe `profile` y clava sus indices con `profile.normalize_resolver`; al ser instancia por-pais (F9), no hay mezcla cross-pais de estrategias.
**Reversibilidad declarada**: como el indice se reconstruye cada `load()`, cambiar la estrategia y recargar BASTA — a diferencia de F11, aqui no hay que migrar identidad.

##### (d) Riesgo adversarial concreto
- **EL/BG/RU/CJK/JP**: `encode('ascii','ignore')` -> '' -> el resolver queda CIEGO (toda clave vacia colisiona); resolucion texto->codigo imposible para esos paises. No es un sesgo: es ceguera total del escalon exacto.
- **DE**: funciona pero degradado — 'Straße'->'strae' pierde senal; nombres compuestos largos (guiones, eszett, umlaut multiple) pierden capacidad de match fino, bajando recall del resolver aunque no a 0.
- **Mixto/ruido**: un nombre con un solo caracter no-Latino intercalado en texto Latino pierde ESE token; si el token discriminante era el no-Latino, el match se degrada en silencio (sin error).
- **PT/FR/IT (Latino)**: SIN riesgo — el fold actual es correcto; el fix debe NO tocarlos (byte-identico) o introduce regresion gratis.

##### (e) Criterio de sellado + verificacion multi-via
**Sellado** cuando: (1) `_norm` es estrategia del perfil; (2) ES/Latino byte-identico; (3) ningun pais registrado produce clave vacia para un nombre no-vacio.
**Multi-via**:
- *Via 1 (ES/Latino byte-identico)*: golden — re-clavar el indice ES y diff contra el actual = 0 cambios; mismo set de `_PROVINCE_ALIASES` y gazetteer ES resuelven igual.
- *Via 2 (no-vacio adversarial)*: fixture {'Αθηνα','Москва','横浜','Straße'} -> `assert profile.normalize_resolver(x) != ""` para todos; y dos nombres no-Latino DISTINTOS no comparten clave (no colapsan).
- *Via 3 (recuperabilidad)*: probar que recargar el indice con la nueva estrategia recupera el matching sin tocar ningun dato persistido (cero migracion) — confirma que F10 es reversible y separable de F11.
- *Via 4 (ortogonal de transliteracion)*: para una muestra no-Latina, la transliteracion algoritmica (AnyAscii) y la romanizacion oficial de fuente (GeoNames `asciiname`) convergen; divergencia (p.ej. Han via Pinyin vs romaji JP) se loguea — para el RESOLVER (recomputable) es tolerable; se reserva el rigor source-first para F11.

##### (f) Herramienta NEXT-LEVEL [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md]
- **AnyAscii** — ISC — https://github.com/anyascii/anyascii — [VERIFIED NEXT-LEVEL.md:326-332 (geo cluster #1) y :221-227 (extraction-scrape 'script-aware-transliteration')]. Reemplaza `encode('ascii','ignore')` por una transliteracion data-driven, sin dependencias nativas (~200-500KB de tablas embebidas [VERIFIED NEXT-LEVEL.md:331]), licencia ISC permisiva — explicitamente la via LIMPIA frente a unidecode (GPL-2.0+, contamina el servicio) e ICU. Para el plano RESOLVER (recomputable) la transliteracion algoritmica de AnyAscii basta; el matiz "romanizacion de fuente PRIMERO" (GeoNames asciiname/alternateNames) que evita mintear Han via Pinyin en JP es critico en F11 (identidad inmutable), no aqui. €0, CPU puro, drop-in en el call-site `_norm` bajo la rama de script del `pack.normalize_policy`.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f11"></a>

#### F11 · Normalizacion — plano IDENTIDAD/MINT (codes._normalize) [la peor rotura]

**Ficha rápida**

- **Costura (ES→genérico):** codes._normalize hace NFKD + encode('ascii','ignore') [VERIFIED codes.py:30] -> CJK/cirilico/griego colapsan a '' -> canonical_key='name:|{muni}' (:94) funde TODA entidad name-based de un municipio a UNA clave -> cdp_code colisionado e INMUTABLE (:53,:117-118). El diseno solo marco geo.py (F10, recomputable) y dejo intacto el identity-path append-only. Insertar transliteracion ANTES del fold, estrategia per-pais del GeoProfile.
- **Fix:** _normalize(text, *, translit=None): default None (ES/Latino) = byte-identico. No-Latino: (1) romanizacion de FUENTE primero (GeoNames asciiname/alternateNames isolang=en/romaji), (2) AnyAscii algoritmico solo si falta. Orden critico: AnyAscii/ICU romanizan Han via Pinyin chino [VERIFIED NEXT-LEVEL.md:327], incorrecto para JP -> la fuente gana para no mintear identidad japonesa mal-romanizada e inmutable. El fix DEBE tocar codes.py, no solo geo.py.
- **Adversarial:** Nombre CJK/japones -> _normalize='' -> canonical_key colapsa -> cdp_codes colisionados e inmutables; sample-verify-delete NO lo revierte (append-only). Corrupcion de identidad PERMANENTE. Incluso Latino: ß (U+00DF) carece de descomposicion NFKD -> ascii-ignore lo descarta -> 'weienfels' en vez de 'weissenfels' (consistente con golden NEXT-LEVEL.md:332); AnyAscii mapea ß->ss bien.
- **Sellado:** (1) Golden no-Latino obligatorio: Yokohama/Weissenfels(ß->ss)/Athina/Moskva -> key no-vacia, no-colisionada; 2 municipios distintos no comparten clave. (2) 2-via: AnyAscii vs GeoNames asciiname convergen; divergencia loguea y gana la fuente. (3) ES byte-identico: re-mint corpus ES, diff vs golden cdp_code = 0 drift. (4) Round-trip name->translit->key->re-mint->mismo cdp_code. (5) Fuzzer no-Latino: 0 colisiones cross-municipio.
- **NEXT-LEVEL:** AnyAscii — ISC — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:329] (Python puro, sin deps nativas, ~200-500KB, pip). Autoridad de fuente orden-1: GeoNames asciiname + alternateNamesV2.zip — CC-BY 4.0 [VERIFIED NEXT-LEVEL.md:385]. NOTA: unidecode es GPL-2.0+ (copyleft, contamina) [VERIFIED NEXT-LEVEL.md:328]; AnyAscii ISC es la via EUR0 limpia.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED services/api/codes.py:29-32]** `_normalize`:
  ```python
  def _normalize(text: str) -> str:
      text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")  # :30
      text = re.sub(r"[^a-z0-9]+", "", text.lower())                                          # :31
      return text
  ```
  `encode("ascii","ignore")` DESCARTA todo punto de codigo no-ASCII. Para CJK/cirilico/griego -> cadena vacia tras el `re.sub`.
- **[VERIFIED codes.py:56-97]** `canonical_key`: la rama name-based (sin domain/cif/particular) en :93-94 devuelve `f"name:{_normalize(name)}|{municipality_code}{addr}"` (:94) y :95-96 el fallback a provincia `f"name:{_normalize(name)}|p{province_code}{addr}"`.
- **[VERIFIED codes.py:44-53]** `mint_code`: `return f"CDP-{country_code}-{province_code}-{_base32(digest)}"` (:53). Y `cdp_pair` (:100-118) hashea la key con `hashlib.sha256(key.encode("utf-8")).digest()` (:117) -> `mint_code` (:118). El `cdp_code` es **append-only / inmutable** (doctrina del modulo, docstring :1-16).

##### (b) El mecanismo al atomo
1. `canonical_key` (:56) devuelve la **pre-imagen de dedup INMUTABLE**. El propio modulo declara que `country_code` se acepta por simetria pero **NO** entra en la key (:62-65) para no re-keyar 431k entidades.
2. Para una entidad name-based, la key es `name:{_normalize(name)}|{muni}` (:94).
3. `_normalize` (:29) hace NFKD + `encode('ascii','ignore')`: un nombre **CJK/japones/cirilico/griego** -> todos los chars caen -> `''`.
4. -> `canonical_key = "name:|{muni}"` para TODA entidad name-based de ese municipio -> **una sola clave** para todas.
5. `cdp_pair` (:117-118) las hashea a la MISMA `digest` -> `mint_code` emite `cdp_code`s **COLISIONADOS e INMUTABLES**.
6. **Por que es la peor**: es el path de IDENTIDAD (append-only), no el indice del resolver. El `sample-verify-delete` NO lo revierte (no es recomputable). Es la separacion institucional mas critica del stage: F10 (geo.py:_norm, indice del resolver) se arregla recargando; F11 corrompe identidad para siempre.

##### (c) La costura ES->generico con su fix exacto
- **Costura**: insertar una capa de transliteracion ANTES del fold ASCII, dentro de `codes._normalize`, gobernada por una estrategia per-pais del `GeoProfile` (F8). El diseno original SOLO marco `geo.py:51-53` (F10) y dejo **intacto** el identity-path -> hay que cerrarlo aqui.
- **Latino-con-diacriticos (ES/DE/FR/IT/PT)**: conservan el fold actual -> **byte-identico** (NFKD descompone 'a'->'a'+combining, el ignore quita el combining).
- **No-Latino (JP/CJK, EL griego, BG/RU cirilico)**: orden CRITICO -> (1) romanizacion provista por la FUENTE primero (`asciiname` y `alternateNames isolang=en/romaji` de GeoNames), (2) solo si falta, transliteracion algoritmica `AnyAscii`. Razon [VERIFIED NEXT-LEVEL.md:327]: AnyAscii/ICU romanizan Han via Pinyin CHINO, incorrecto para toponimos japoneses -> usar el romaji oficial de la fuente evita mintear identidad japonesa mal-romanizada e inmutable.
- **Fix exacto**: `_normalize(text, *, translit=None)`; `translit` es la estrategia del perfil; default `None` (ES/Latino) = comportamiento actual byte-identico. El call-site `canonical_key` pasa `translit=profile.translit`. El fix DEBE tocar `codes.py` (no solo `geo.py`).

##### (d) El riesgo adversarial concreto
- **JP/CJK** 'ﾖｺﾊﾏ'/kanji -> `_normalize=''` -> `canonical_key="name:|{muni}"` -> colapso total de identidad name-based del municipio -> cdp_codes colisionados e INMUTABLES. Corrupcion de identidad PERMANENTE, la peor del censo.
- **Latino con trampa**: DE 'Weissenfels' escrito 'Weiszenfels' con eszett (U+00DF) -> `unicodedata.normalize('NFKD','ß')` NO descompone (ß carece de descomposicion NFKD) -> `encode('ascii','ignore')` lo DESCARTA -> 'weienfels' (no 'weissenfels'). Consistente con el golden [VERIFIED NEXT-LEVEL.md:332] que exige 'ss preservado, no weienfels'. AnyAscii mapea ß->ss correctamente. -> el fold corrompe senal incluso en Latino.
- **EL/BG/RU**: 'Athina'/'Moskva' en alfabeto nativo -> '' -> mismo colapso.

##### (e) Criterio de sellado + verificacion multi-via [VERIFIED NEXT-LEVEL.md:332]
1. **Golden de identidad no-Latina OBLIGATORIO**: 'Yokohama'->yokohama, 'Weissenfels'(ß->ss, no weienfels), 'Athina', 'Moskva' -> `canonical_key` NO vacia y NO colisionada; assert que dos municipios distintos no comparten clave.
2. **2-via ortogonal**: transliteracion algoritmica (AnyAscii) vs romanizacion de fuente (GeoNames `asciiname`) deben converger en una muestra; divergencia (JP Pinyin vs romaji) se loguea y **gana la fuente**.
3. **ES byte-identico**: re-mint de un corpus ES y diff contra el golden de `cdp_code` = **0 drift**.
4. **Round-trip**: name -> translit -> key -> re-mint -> mismo `cdp_code`.
5. **No-colision adversarial**: un fuzzer de nombres no-Latinos no produce NINGUN par de municipios distintos con la misma key.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **AnyAscii** — ISC — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:329]. Paquete Python puro, sin dependencias nativas, ~200-500KB de tablas embebidas; `pip install anyascii`. Cero infra, cero GPU.
- **Autoridad de fuente (orden #1)**: GeoNames `asciiname` + `alternateNamesV2.zip` (romanizacion oficial, isolang) — CC-BY 4.0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:385].
- **Via limpia confirmada**: la biblia nombraba 'unidecode/ICU CC0' pero `unidecode` es **GPL-2.0+** [VERIFIED NEXT-LEVEL.md:328], copyleft -> contamina; AnyAscii (ISC) es la ruta EUR0 limpia. Convierte 'hueco > mentira' en invariante: la identidad no-Latina deja de colapsar a '' por construccion.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f12"></a>

#### F12 · Tabla de alias de provincia/region

**Ficha rápida**

- **Costura (ES→genérico):** _PROVINCE_ALIASES (geo.py:61-73) es un dict a NIVEL DE MODULO 100% ES: 27 claves alias sobre 12 provincias (islas/exonimos/bilingues/formas-cortas). GeoResolver.load(conn) (:155-156) lo inyecta con setdefault SIN country_code → los alias ES entran en el indice _prov de CUALQUIER run, incluido el pais #2.
- **Fix:** Mover _PROVINCE_ALIASES al GeoProfile por-pais (F8), cargado por country_code; ES = default byte-identico (27 claves). load(conn, country_code) inyecta SOLO los alias del pais del run. A futuro auto-minar desde GeoNames alternateNamesV2 (isolang bilingues; flags isHistoric/isShortName/isColloquial) normalizados por la transliteracion del perfil, eliminando el curado manual cientos-de-alias x pais.
- **Adversarial:** Dict global → un run DE/IT inyecta menorca→07/castello→12 y mis-rutea texto homonimo extranjero al codigo ES (y por F11 a un cdp_code inmutable equivocado); un 2º pais sin su tabla pierde 30-50% de variantes (Bayern/Sachsen, BE/CH bilingues no resuelven); a escala continental el curado manual es inviable; un alias compartido entre 2 provincias forzado a un codigo funde identidades.
- **Sellado:** Regresion ES: las 27 claves aparecen en el set final (cobertura >= curado humano, golden); precision: cada alias → codigo correcto, ambiguo se RECHAZA; aislamiento: run pais-X sin ningun alias de pais-Y; 2-via GeoNames vs Wikidata convergen; no-fusion de 2 provincias por alias compartido.
- **NEXT-LEVEL:** GeoNames alternateNamesV2.zip — mineria automatica de alias/exonimos/bilingues por unidad ADM, CC-BY 4.0, https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:385]. Alternativas: Wikidata (CC0), OSM name:xx/alt_name/old_name. Normalizacion no-Latina de claves: AnyAscii (ISC, https://github.com/anyascii/anyascii [VERIFIED:329]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **pipeline/geo.py:61-73** [VERIFIED] `_PROVINCE_ALIASES: dict[str, str]` declarado a NIVEL DE MODULO, 100% ES. Conteo exacto = **27 claves alias sobre 12 provincias**: `alava/araba`→01; `menorca/mallorca/ibiza/eivissa/formentera/islas baleares/illes balears`→07; `a coruna/la coruna`→15; `guipuzcoa/gipuzkoa`→20; `las palmas/gran canaria/fuerteventura/lanzarote`→35; `la rioja`→26; `vizcaya/bizkaia`→48; `gerona`→17; `lerida`→25; `orense`→32; `tenerife/santa cruz de tenerife`→38; `castellon/castello`→12. (NEXT-LEVEL.md:384 dice "~12 entradas" = 12 provincias; el numero exacto de CLAVES es 27.)
- **pipeline/geo.py:155-156** [VERIFIED] dentro de `GeoResolver.load(cls, conn)`: `for k, v in _PROVINCE_ALIASES.items(): self._prov.setdefault(k, v)`. La firma `load(conn)` NO recibe `country_code` → los 27 alias ES se inyectan en el indice `_prov` para CUALQUIER run, incluido el pais #2.

##### (b) Mecanismo al atomo
`_prov` es el indice nombre-normalizado→codigo-de-provincia. Se puebla primero desde `geo_province` (153-154 via `_index_prov`, que registra `_norm`, `_sorted_key` y partes >=4 chars del nombre bilingue), y LUEGO se sobreponen los alias con `setdefault` (no pisan claves ya presentes, :156). El alias cubre variantes que la normalizacion sola no salva: **islas** (Menorca→07 Balears), **exonimos/bilingues** (Gipuzkoa/Guipuzcoa→20, Orense/Ourense→32, Gerona→17, Lerida→25), **formas cortas** (La Rioja→26). Es DATO curado a mano, no algoritmo: cada entrada es una decision humana.

##### (c) Costura ES→generico + fix exacto
Sacar `_PROVINCE_ALIASES` del scope de modulo a un campo del **GeoProfile** por-pais (F8), cargado por `country_code`; ES registrado como default byte-identico (mismas 27 claves). `GeoResolver.load(conn, country_code)` inyecta SOLO los alias del pais del run. A futuro, **auto-minar** los alias desde GeoNames `alternateNamesV2` (columna isolang para bilingues; flags isHistoric/isShortName/isColloquial para exonimos/formas-cortas/islas), normalizados por la estrategia de transliteracion del perfil — eliminando el curado manual de cientos de alias × pais. La inyeccion deja de ser global y pasa a ser instancia-por-pais: contaminacion cross-pais imposible por construccion, no por filtro.

##### (d) Riesgo adversarial concreto
- **Contaminacion global**: el dict vive a nivel de modulo → un run **DE/IT** inyecta `menorca→07`, `gipuzkoa→20`, `castello→12` en su `_prov`; un texto extranjero con token homonimo ("Castello" es comun en IT, "Gerona"/"Orense" como apellido/odonimo) mis-rutea al codigo de provincia ES → mintea provincia equivocada (y por F11 un cdp_code inmutable equivocado).
- **Pais sin alias**: un 2º pais no tiene su tabla (Bayern/Sachsen, o variantes BE/CH bilingues no resuelven) → pierde 30-50% de variantes de nombre; el resolver nace ciego.
- **Escala continental**: curar islas/exonimos/bilingues a mano por pais es inviable → sin la mineria de alternateNames cada pais nuevo arranca sin cobertura de variantes.
- **Ruido**: un alias compartido entre dos provincias (homonimia real) forzado a un solo codigo funde identidades; debe rechazarse, no resolverse.

##### (e) Criterio de sellado + verificacion multi-via
1. **Regresion ES**: las 27 claves manuales DEBEN aparecer en el set final (registrado o auto-minado) — cobertura >= curado humano; golden pinneado, si falta una el cruce esta incompleto.
2. **Precision**: muestra de alias resueltos → cada alias mapea al codigo correcto; un alias ambiguo (mismo nombre, 2 provincias) se RECHAZA, no se fuerza.
3. **Aislamiento**: un run pais-X no contiene NINGUN alias de pais-Y (assert `_prov` scopeado por pais).
4. **2-via ortogonal**: alias GeoNames vs Wikidata convergen en muestra; divergencia se audita.
5. **No-fusion**: el set ampliado no funde dos provincias por un alias compartido (assert country/province isolation).

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **PRIMARIA — GeoNames alternateNamesV2.zip**: mineria automatica de alias/exonimos/bilingues por unidad ADM (isolang + flags isHistoric/isShortName/isColloquial); el resolver gana cobertura multilingue sin curado y se auto-actualiza cuando GeoNames cambia. **CC-BY 4.0**, €0. https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:385].
- **Alternativas**: Wikidata (P1448 nombre oficial / P1705 nombre nativo / also-known-as, **CC0**), OSM `name:xx` / `alt_name` / `old_name`.
- **Normalizacion multilingue de las claves alias — AnyAscii** (transliteracion no-destructiva antes del fold, para alias no-Latino). **ISC**, €0. https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:329].

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f13"></a>

#### F13 · Gazetteer de localidades (nombre->muni) + resolucion de ruta por pais

**Ficha rápida**

- **Costura (ES→genérico):** _GAZETTEER_PATH es constante de modulo unica ES [VERIFIED geo.py:46-48]; _load_gazetteer filtra 'len(muni_code) != 5' y slicea 'muni_code[:2]' como provincia [VERIFIED geo.py:101-104]; columnas del esquema INE; se carga para cualquier pais [VERIFIED geo.py:181].
- **Fix:** Resolver la ruta via GeoProfile (data/<cc>/geo/gazetteer.csv) y pasar country_code a _load_gazetteer; sustituir 'len != 5' por el ancho/regex del pack (cruza F1); derivar prov_code por el predicado de forma del perfil (cruza F3), no por [:2]; mapa de columnas en el schema del pack. Doctrina ambiguo->None y ausencia no-fatal intactas.
- **Adversarial:** 2o pais sin gazetteer -> locality off (no-fatal, OK). Peor: gazetteer de 6/8 digitos -> 'len != 5' descarta TODAS las filas -> cobertura de localidad 0 sin error. 'muni_code[:2]' inventa provincia en pais sin prefijo. PT 'NNNN-NNN' rompe parsing; nombres no-Latinos -> _norm vacio -> claves ciegas (cruza F10).
- **Sellado:** 1) Golden pack-malo: gazetteer 8-digit no se vacia en silencio (rojo si dropea callado). 2) 2a via: len(keys)==filas validas no-diseminado; discrepancia=drop silencioso. 3) ES byte-identidad: indice ES identico (conteo claves+mappings). 4) Ambiguedad: localidad en 2 munis -> None pinneado. 5) Cross-pais: nucleo extranjero no resuelve a muni ES.
- **NEXT-LEVEL:** libpostal (+ pypostal) — parser de direcciones multilingue entrenado, alimenta GeoResolver.municipality_code con campos tipados country-agnosticos. https://github.com/openvenues/libpostal · MIT · €0=True [VERIFIED NEXT-LEVEL.md:342-348]. Dato alternativo del gazetteer: GeoNames populated places (feature_class='P'), CC-BY 4.0 [VERIFIED NEXT-LEVEL.md:377].

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED pipeline/geo.py:46-48] `_GAZETTEER_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "geo" / "nomenclator_entidades_ine.csv"` — constante de modulo, ruta UNICA al Nomenclator INE ES, sin parametro de pais.
- [VERIFIED pipeline/geo.py:76-126] `_load_gazetteer()` -> `dict[prov_code, dict[locality_key, set[muni_code5]]]`:
  - [:94-96] si la ruta no existe -> indice vacio (NO-FATAL: fuzzy sigue, locality off).
  - [:101-104] `muni_code = row["municipio_id"].strip(); if len(muni_code) != 5: continue; prov_code = muni_code[:2]` — HARDCODEA ancho 5 + coding 2+3 INE.
  - [:88-90,107] columnas INE: `municipio_id`, `entidad_singular_nombre`, `nucleo_nombre`.
  - [:116-117] descarta `'diseminado'`. [:118-124] acumula TODOS los muni por nombre (deteccion de ambiguedad downstream).
- [VERIFIED pipeline/geo.py:181] `self._locality = _load_gazetteer()` dentro de `GeoResolver.load` -> se carga para CUALQUIER pais.
- [VERIFIED pipeline/geo.py:301-314] `_locality_match`: scoped a provincia; `if codes and len(codes) == 1: return ...; return None` -> >1 municipio = ambiguo -> None ("better a hole than a lie").

##### (b) Mecanismo al atomo
El gazetteer es el 3er escalon de `municipality_code()` (exacto -> fuzzy -> localidad). Resuelve nucleos/pedanias/parroquias/barrios (equivalente Nomenclator INE, ~63k pares) a su municipio. Atomos ES-soldados: (1) la RUTA del CSV es una constante de modulo (un solo fichero ES); (2) el filtro `len(muni_code) != 5` descarta toda fila cuyo codigo de municipio no mida exactamente 5 (presupone INE); (3) `prov_code = muni_code[:2]` presupone que los 2 primeros chars son la provincia (relacion de prefijo ES); (4) los NOMBRES de columna son del esquema INE.

##### (c) Costura ES->generico + fix exacto
- Costura 1 (ruta): constante de modulo ES. Fix: resolver via GeoProfile -> `data/<cc>/geo/gazetteer.csv`; `_load_gazetteer(country_code)` o inyectar la ruta del perfil.
- Costura 2 (ancho): `len(muni_code) != 5` clava el ancho ES (cruza con F1). Fix: usar el ancho/regex del pack del pais (AGS-DE 8, ISTAT-IT 6, freguesia-PT 6); guardia `len(muni_code) != width[cc]` o un predicado de forma.
- Costura 3 (coding prefijo): `muni_code[:2]` presupone prefijo->provincia (cruza con F3). Fix: derivar `prov_code` por el predicado de forma del perfil, o por columna explicita; un pais sin prefijo (AGS, INSEE) NO puede slicear [:2].
- Costura 4 (esquema): nombres de columna INE. Fix: mapa de columnas en el schema del pack (codigo_postal/municipio_id/entidad_singular_nombre/nucleo_nombre -> roles canonicos).
- Doctrina preservada: ambiguo->None, ausencia no-fatal.

##### (d) Riesgo adversarial concreto
2o pais sin gazetteer -> locality off (ya no-fatal, OK). PEOR: un gazetteer extranjero con codigos de muni de 6/8 digitos -> `len(muni_code) != 5` DESCARTA TODAS las filas -> cobertura de localidad cae a 0 SIN error (sello ciego). `muni_code[:2]` en un pais sin prefijo asigna una provincia falsa. PT 'NNNN-NNN' mezcla CP en columnas. Nombres no-Latinos (EL/CJK/cirilico) pasan por `_norm` (ascii ignore) -> clave vacia (cruza con F10) -> el indice queda ciego para esas localidades.

##### (e) Criterio de sellado + verificacion multi-via
1. Golden de pack-malo: un gazetteer extranjero de 8 digitos NO debe vaciarse en silencio; el loader acepta el ancho del perfil o falla ruidoso (test rojo si dropea todo callado).
2. 2a via: `len(keys cargadas)` == filas no-diseminado con ancho valido; discrepancia = drop silencioso.
3. ES byte-identidad: el gazetteer ES carga indice identico (mismo conteo de claves, mismas asignaciones muni) — golden.
4. Invariante de ambiguedad: una localidad compartida por 2 municipios -> None (pinneado).
5. Cross-pais: el indice se scopea por pais via perfil; un nucleo extranjero no resuelve a un muni ES.

##### (f) Herramienta next-level
**libpostal** (+ pypostal): parser estadistico entrenado en 1B+ direcciones que devuelve componentes etiquetados (road, city, state, postcode, country) en 60+ idiomas, alimentando `GeoResolver.municipality_code(province, city)` con tokens YA tipados en vez de adivinar 'que token es la localidad' con heuristicas ES. URL https://github.com/openvenues/libpostal · Lic MIT · €0=True [VERIFIED NEXT-LEVEL.md:342-348]. Fuente de dato alternativa para el gazetteer en si: **GeoNames** populated places (allCountries feature_class='P') — CC-BY 4.0 [VERIFIED NEXT-LEVEL.md:377].

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f14"></a>

#### F14 · Fuzzy matcher (WRatio + token-subset) + tuning por pais

**Ficha rápida**

- **Costura (ES→genérico):** Los cuatro enteros de tuning (_FUZZY_CUTOFF=88, _FUZZY_QUERY_MIN_LEN=4, _FUZZY_CAND_LEN_DIVISOR=3, _FUZZY_CAND_LEN_FLOOR=4; geo.py:32-43) son module-global y estan calibrados al token-structure Latino ES (probe B4.1). Deben trasladarse al GeoProfile (F8) como un bloque fuzzy_tuning, con ES por defecto = (88,4,3,4) byte-identico. El ALGORITMO (Tier A subset + Tier B WRatio) se queda; la instancia del matcher es country-scoped via el resolver (F9) de modo que `candidates` ya estan country+province scoped. La costura mas profunda: Tier A `.split()` asume whitespace -> un perfil para script sin-espacio (CJK) necesita una estrategia de tokenizacion propia; y el ASCII-fold (F10) debe transliterar ANTES de _norm para que los tokens no-Latinos sobrevivan (cruza F10/AnyAscii). El hueco se confiesa: re-tunear por pais NO debe romper el contrato 0-falsos-positivos.
- **Fix:** Anadir al GeoProfile: fuzzy = FuzzyTuning(cutoff=88, query_min_len=4, cand_len_divisor=3, cand_len_floor=4, tokenizer='whitespace'); ES = estos defaults exactos. `_fuzzy_match` lee self._profile.fuzzy.* en vez de las constantes de modulo (los cuatro ints de geo.py:32-43 pasan a ser los valores-default del dataclass). Tier A: query_tokens = set(self._profile.fuzzy.tokenize(query_norm)); el tokenize default = str.split (byte-identico ES); un perfil CJK aporta char-ngram o word-break ICU. Mantener el try/except ImportError pero declarar rapidfuzz como dependencia DURA (el equipo ya golpeo el bug de rapidfuzz undeclared-dep, ver MEMORY) y CI asserta rapidfuzz importable, matando el silent None de produccion. Re-tune por pais gated por una probe-fixture 0-FP (el analogo de B4.1).
- **Adversarial:** DE: nombres compuestos ('Moenchengladbach', 'Muenchen-Gladbach' con guion) -- tras ASCII-fold el WRatio a cutoff ES-88 puede sobre-rechazar una variante valida o, si el guion parte tokens distinto, dar un falso hit de token-subset. JP/CJK: sin whitespace, Tier A `.split()` produce un solo token gigante; el ASCII-fold (F10) puede vaciarlo -> ambos tiers ciegos -> None silencioso (parece 'no match', en realidad 'no tokeniza'). Aglutinantes (FI/HU/TR): tokens unicos largos; el Levenshtein interno de WRatio se comporta distinto, cutoff ES mal-calibrado. rapidfuzz ausente (:281) -> Tier B devuelve None para TODA query -> el matching degrada a Tier-A-solo sin error, la cobertura cae en silencio (bug real ya golpeado, MEMORY). Ruido: una query foranea de 2-3 chars la bloquea query_min_len=4 (bien), pero un pais cuyos munis reales sean comunmente <=3 chars quedaria sobre-bloqueado por el floor ES.
- **Sellado:** Sello = 5 vias. (1) ES golden: probe B4.1 con constantes desde el perfil ES -> 0 falsos positivos, set de match identico (byte-identico), en CI. (2) Determinismo: misma entrada->misma salida (WRatio deterministico, orden candidato fijo), fixture pineado. (3) Probe 0-FP por pais: cada pais trae set etiquetado; el sello exige 0 FP a SUS constantes tuneadas (el contrato de ambiguedad re-probado, no asumido). (4) Ortogonalidad: el fuzzy solo PROPONE; province-scope + country-scope (F9) acotan -> fuzzy mas laxo no puede mintear codigo cross-pais (candidatos ya country-scoped). (5) Gate de dependencia: CI asserta rapidfuzz importable (mata el silent-None :281). Criterio: ningun pais sella sin su probe 0-FP verde a sus propias constantes.
- **NEXT-LEVEL:** datasketch (MinHash, LSH) + RapidFuzz [VERIFIED NEXT-LEVEL.md:538] - datasketch MIT - EUR0=True - https://github.com/ekzhu/datasketch. La entrada 'Scalable, language-neutral fuzzy blocking' (535-541) propone MinHash-LSH sobre char n-grams del nombre normalizado para candidate-generation sub-cuadratica y language-neutral, con RapidFuzz (ya dependencia real) para la comparacion fina in-block, retirando la matematica de strings O(n^2)/ES-tuneada; opcional jellyfish phonetic keys (Metaphone/NYSIIS) por pais [VERIFIED:536,539]. Verificacion de la entrada: recall parity vs baseline ES (sin regresion), determinismo por seed MinHash fijo (golden), ortogonalidad (blocking solo propone; la decision de merge no cambia) [VERIFIED:541]. Para el hueco de tokenizacion no-Latina, la palanca transversal es AnyAscii (ISC, https://github.com/anyascii/anyascii [VERIFIED:482,329]) aplicada ANTES de _norm para que nombres no-Latinos den tokens no-vacios. Juntas vuelven el matcher language-neutral y scale-proof en vez de ES-token-shaped.

**Deep-spec 360**

##### (a) code_hints verificados al byte
- **[VERIFIED pipeline/geo.py:240-299]** `_fuzzy_match(self, province_code, muni_name)`, province-scoped, dos tiers:
  - **Tier A token-subset (ambiguity-safe), l.265-274**: `query_tokens = set(query_norm.split())`; `supersets = {code for key,code in candidates if query_tokens <= set(key.split())}`; `len(supersets) >= 2 -> return None` (ambiguo, "confess the gap"); `== 1 -> return next(iter(supersets))` (prefijo/short-form confiado). Corre ANTES de puntuar porque WRatio rompe empates artificialmente por longitud (comentario :250-251).
  - **Tier B WRatio fallback, l.276-299**: solo si la query NO es subconjunto de ningun candidato; `from rapidfuzz.process import extractOne; from rapidfuzz.fuzz import WRatio` dentro de try/except; `min_cand_len = max(_FUZZY_CAND_LEN_FLOOR, len(query_norm)//_FUZZY_CAND_LEN_DIVISOR)`; filtra `eligible` por longitud; `extractOne(query_norm, keys, scorer=WRatio, processor=None, score_cutoff=_FUZZY_CUTOFF)`.
- **[VERIFIED pipeline/geo.py:32-43]** constantes de tuning: `_FUZZY_CUTOFF=88` (:32); `_FUZZY_QUERY_MIN_LEN=4` (:37, evita 'la'/'las'/'el' via WRatio token-overlap, comenta `WRatio('las','las rozas de madrid')==90`); `_FUZZY_CAND_LEN_DIVISOR=3` (:42, ratio 1/3 deja 'palma'(5) matchear 'palma de mallorca'(17); el //2 original excluia mal ese caso); `_FUZZY_CAND_LEN_FLOOR=4` (:43). Comentario :30 "validated by B4.1 probe (0 false positives at these values)".
- **[VERIFIED pipeline/geo.py:277-281]** `except ImportError: return None` -> si rapidfuzz ausente, Tier B devuelve None EN SILENCIO para toda query.

##### (b) Mecanismo al atomo
El matcher es province-scoped: `candidates = self._muni_names.get(province_code)` (:257) = lista de (clave_normalizada, muni_code). La query se normaliza con `_norm` (el ASCII-fold; cruza con F10). Tier A es algebra de conjuntos pura sobre tokens split-por-espacio -- country-agnostica en ESTRUCTURA pero dependiente de (i) tokenizacion por whitespace y (ii) un ASCII-fold que produzca tokens no-vacios. Tier B es rapidfuzz WRatio (composite de ratio/partial/token-sort/token-set con peso por longitud) con cutoff duro 88 y guardas de longitud calibradas al token-structure ES. El contrato "0 false positives" ES la garantia de ambiguedad: Tier A devuelve None ante ambiguedad genuina (>=2 supersets); Tier B solo dispara en formas mas ricas/variantes, gated por cutoff+longitud. **El atomo de dependencia-pais**: el ALGORITMO (subset-primero, WRatio-despues) es country-agnostico; solo los CUATRO ENTEROS (88,4,3,4) estan ES-calibrados y son module-global, no per-profile. La asuncion mas profunda es la tokenizacion `.split()` de Tier A: presupone tokens separados por espacio -- falso para scripts aglutinantes/sin-espacio (JP/CJK), y el ASCII-fold upstream (F10) puede vaciar los tokens del todo para no-Latino.

##### (e) Sello multi-via
1. **ES golden**: re-correr la probe B4.1 con constantes desde el perfil ES -> 0 falsos positivos, set de match identico al de hoy (byte-identico), aserto en CI.
2. **Determinismo**: misma entrada -> misma salida (WRatio determinista, orden de candidatos fijo); fixture golden pineado.
3. **Probe 0-FP por pais**: cada pais onboardeado trae un set etiquetado; el sello exige 0 falsos positivos a las constantes tuneadas de ESE pais (el contrato de ambiguedad se RE-prueba, no se asume).
4. **Ortogonalidad**: el fuzzy solo PROPONE; las guardas estructurales (province-scope, country-scope F9) lo acotan -- un fuzzy mas laxo no puede mintear un codigo cross-pais porque los candidatos ya estan country-scoped.
5. **Gate de dependencia**: CI asserta que rapidfuzz importa (mata el path silent-None :281; MEMORY confirma un bug real de rapidfuzz undeclared-dep).

##### (f) Palanca: ver campo tool.

↩ [Índice de sub-proyectos](#indice-sub)

---

<a id="capa-3"></a>

### Capa III · Geocodificación espacial, escritores y lectores (F15–F21)

> El eje geométrico y todo lo que escribe o lee `(country_code, code)`: geocoders KNN, umbral, índice CP, seeder de centroides, backfills, productores de minteo y lectores de API. La superficie viva donde el country-blindness (Raíz C) sangra en silencio si no se cierra en el MISMO PR del país #2.

<a id="f15"></a>

#### F15 · Geocoders espaciales country-scoping (Province + Municipality KNN)

**Ficha rápida**

- **Costura (ES→genérico):** geocode.py:79-83 (ProvinceGeocoder.load) y :130-137 (MunicipalityGeocoder.load) SELECTan sin country_code [VERIFIED]; el bucket del indice se clava por province_code DESNUDO (self._index.get(province_code) :174 [VERIFIED]). Tras 0052/0053 'province_code' ya no es unico entre paises. Default 'ES' (un solo tenant) hace el output byte-identico hoy.
- **Fix:** ProvinceGeocoder.load(conn, country_code='ES') y MunicipalityGeocoder.load(conn, country_code='ES') con 'AND country_code=$1' en el SELECT; clave del bucket = tupla (country_code, province_code); nearest_municipality recibe el country del run -> self._index.get((country_code, province_code)). Propagar country a los 16 call-sites de produccion [VERIFIED git grep]: discover.py:131 + 11 modulos *_wholesale/facet + 3 scripts (overture_ingest carga ambos). Default 'ES' = byte-identico.
- **Adversarial:** country-blind + bucket por province_code (geocode.py:80-83,132-137,174): ES-28 y DE/MX-28 se funden; el KNN devuelve code5 sin pais y un punto MX en 'provincia 15' resuelve a A Coruna ES. 11 modulos *_wholesale.py consumen esto VIVO -> el sangrado entra en la ingesta de todo el censo, no en un script aislado. FR DOM 971 sin country_code mezcla su bucket; ruido DE-28 con indice ES dominante -> argmin elige Madrid.
- **Sellado:** ambos load aceptan+filtran country_code; bucket por (country_code, province_code); los 16 call-sites pasan el country del run; golden ES byte-identico (mismo code5 por (lat,lon,prov)). Multi-via: golden espacial ES pinneado + test bleed=0 (centroide DE-28 vs ES-28, punto ES->ES, punto DE->DE) + cruce ortogonal con resolver textual F9; tests/test_geo_reverse.py [VERIFIED] extendido con caso cross-pais.
- **NEXT-LEVEL:** PostGIS (ST_Contains + GiST) sobre geoBoundaries CGAZ -- geoBoundaries CC-BY 4.0/ODbL, PostGIS GPL-2.0, EUR0 -- https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353]: contencion exacta por poligono etiquetado por country_code (bleed=0 por construccion, frontera ES/PT correcta), elimina el umbral KNN. + Uber H3 (h3-py) Apache-2.0 https://github.com/uber/h3 [VERIFIED NEXT-LEVEL.md:361]: celda_h3->muni O(1), celdas country-scoped, estratos area-igual para el sello MSE.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/geocode.py:70-103` `ProvinceGeocoder` [VERIFIED]; `load(cls, conn)` (`:78-87`) hace `SELECT lat, lon, province_code FROM entity WHERE lat IS NOT NULL ... province_code IS NOT NULL` -- sin `country_code` [VERIFIED:80-83].
- `pipeline/geocode.py:106-202` `MunicipalityGeocoder` [VERIFIED]; `load` (`:129-152`) hace `SELECT code, province_code, lat, lon FROM geo_municipality WHERE lat IS NOT NULL ...` -- sin `country_code` [VERIFIED:132-137]; agrupa el indice `prov_data.setdefault(r["province_code"], ...)` -> bucket SOLO por `province_code` [VERIFIED:141].
- `nearest_municipality` (`:154-194`): `entry = self._index.get(province_code)` [VERIFIED:174] -- la clave del bucket es province_code DESNUDO; `if dist_km > KNN_MAX_DISTANCE_KM: return (None, dist_km)` [VERIFIED:191]; `KNN_MAX_DISTANCE_KM = 30.0` [VERIFIED:49].
- Fan-out de consumidores (mayor que el "14+" del diseno): `git grep "Geocoder.load("` = 16 call-sites de produccion en 15 ficheros [VERIFIED]: `discover.py:131`; 11 modulos `pipeline/platform/` (`oem_audi:842`, `oem_ford:907`, `oem_hyundai:852`, `oem_nissan_mazda_honda:878`, `oem_seat_cupra_new_stock:897`, `oem_seat_cupra_wholesale:880`, `oem_toyota_lexus:899`, `oem_volvo_jlr_suzuki:1149`, `spoticar:777`, `wallapop_facet:372`, `wallapop_wholesale:1233`); 3 scripts (`backfill_municipality_geo:43`, `geo_backfill:192`, `overture_ingest:421-422`).

##### (b) Mecanismo al atomo
El geocoder construye un indice en memoria desde el centroide de cada municipio y resuelve `(lat,lon,province_code)->code5` por vecino-mas-cercano (equirectangular argmin + haversine exacto para el ganador, `:182-190`). La matematica (haversine/equirectangular) es 100% country-agnostica. La rotura es de DOMINIO del indice: la clave del diccionario `self._index` es `province_code` (`:141,174`), un string de 2 digitos que tras 0052/0053 YA NO es unico entre paises (`'28'` = Madrid-ES y Brandenburg-DE / Edomex-MX). El `SELECT` de `load` no filtra por `country_code` (`:132-137`) -> el indice MEZCLA centroides de todos los paises bajo la misma clave de provincia. Atomo: `argmin` sobre un bucket contaminado devuelve el centroide mas cercano SIN saber su pais -> un punto MX en "provincia 15" resuelve a A Coruna-ES.

##### (c) Costura ES->generico + fix exacto
Tres cambios quirurgicos, todos additivos:
1. `ProvinceGeocoder.load(cls, conn, country_code: str = "ES")` -> `SELECT ... FROM entity WHERE ... AND country_code = $1`.
2. `MunicipalityGeocoder.load(cls, conn, country_code: str = "ES")` -> `SELECT ... FROM geo_municipality WHERE ... AND country_code = $1`, y la clave del bucket pasa a la TUPLA `(country_code, province_code)`; `nearest_municipality` recibe el `country_code` del run -> `self._index.get((country_code, province_code))`.
3. Propagar el `country_code` del run a los 16 call-sites [VERIFIED]; default `"ES"` implica que los SELECT y el indice resuelven exactamente lo de hoy (un solo tenant ES), byte-identico. El fan-out a 11 modulos wholesale VIVOS es el riesgo de cobertura del refactor: cada `Geocoder.load(conn)` pasa a `Geocoder.load(conn, run_country)`.

##### (d) Riesgo adversarial concreto
- Sangrado de identidad cross-pais: `geocode.py:80-83,132-137` country-blind + bucket por province_code (`:174`) -> ES-28 y DE/MX-28 se FUNDEN; el KNN devuelve un `code5` sin pais y un punto fisico en MX cae sobre un centroide ES -> municipality_code ES estampado a una entity MX.
- Propagacion a escala: 11 modulos `*_wholesale.py` consumen esto VIVO (cada OEM resuelve la provincia de sus concesionarios) -> el sangrado entra en la INGESTA de todo el censo, no en un script aislado.
- DE/FR/IT/PT: cualquier pais con un codigo de provincia que colisione numericamente con uno ES (inevitable en 2-digit) hereda el centroide ES mas cercano. FR DOM '971' no colisiona pero, sin `country_code`, su bucket se mezcla con cualquier '97' ES -> None silencioso.
- Ruido: una entity con `country_code='DE'` pero `province_code='28'` y lat/lon en Brandenburg -> si el indice ES domina (mas centroides), argmin elige Madrid.

##### (e) Criterio de sellado + verificacion multi-via
SELLADO si y solo si (1) ambos `load` aceptan `country_code` y filtran el SELECT; (2) bucket por `(country_code, province_code)`; (3) los 16 call-sites pasan el country del run; (4) golden ES byte-identico (mismo code5 para el mismo (lat,lon,prov) que hoy). Multi-via: via A golden espacial ES (corpus (lat,lon,prov)->code5 pinneado, sin cambio); via B test de bleed=0 (sembrar un centroide DE-28 y un ES-28; un punto ES resuelve a ES, un punto DE a DE, nunca cruzado); via C cruce ortogonal con el resolver textual (F9): para una muestra, geocoder-espacial y resolver-textual convergen al mismo code dentro del mismo pais. El test de referencia `tests/test_geo_reverse.py` [VERIFIED existe] se extiende con el caso cross-pais.

##### (f) Herramienta de elevacion
Dos palancas que ELIMINAN la heuristica KNN, no solo la country-scopean:
1. PostGIS (ST_Contains + GiST) sobre geoBoundaries CGAZ -- geoBoundaries CC-BY 4.0/ODbL (datos), PostGIS GPL-2.0 (servicio, no se embebe), EUR0 -- https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353]. Sustituye centroide+umbral por contencion exacta: `lat/lon -> ST_Contains(poligono) -> municipio` (cae en exactamente uno, o en ninguno -> hueco confesado). Los poligonos se etiquetan por `country_code` implica bleed=0 por construccion, y un punto en la frontera ES/PT resuelve al pais correcto [VERIFIED NEXT-LEVEL.md:356 via 4].
2. Uber H3 (h3-py) -- Apache-2.0, EUR0 -- https://github.com/uber/h3 [VERIFIED NEXT-LEVEL.md:361]. Pre-tila cada municipio a celdas H3 (`celda_h3 -> municipality_code`) implica reverse-geocode O(1); las celdas se etiquetan con `country_code` y "ninguna celda mapea a municipios de 2 paises" [VERIFIED NEXT-LEVEL.md:364 via 4]. Segundo uso: estratos de area-igual para endurecer la cota MSE del sello (cruza con F24). Juntas cierran la "Raiz H" sin umbral que calibrar.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f16"></a>

#### F16 · Calibracion del umbral KNN por pais

**Ficha rápida**

- **Costura (ES→genérico):** geocode.py:49 KNN_MAX_DISTANCE_KM=30.0 es constante global de modulo soldada a ES (rationale :16-22 Lorca/Caceres radio ~24km); geocode.py:191 'if dist_km > KNN_MAX_DISTANCE_KM: return (None, dist_km)' es el unico parametro de calidad del geocoder. La matematica haversine es country-agnostica (eso es F15); solo el 30 esta hardcodeado a ES.
- **Fix:** Sacar KNN_MAX_DISTANCE_KM a campo del GeoProfile (F8) profile.knn_max_distance_km (default 30.0 ES); MunicipalityGeocoder recibe el umbral en load/__init__ desde el perfil del pais; :191 usa self._threshold_km. ES byte-identico (perfil ES=30 -> comportamiento identico). Next-level: job por pais deriva el umbral del p99 del radio municipal (sqrt(area/pi) o ST_MaximumInscribedCircle sobre poligonos, cruza F26) y lo escribe al perfil versionado.
- **Adversarial:** Nordicos/MX/JP rural (municipios grandes): 30km SOBRE-RECHAZA geocodificaciones validas (centroide legitimamente a 40-60km) -> huecos falsos masivos. DE/zonas densas (municipios pequenos): 30km demasiado LAXO -> acepta cross-municipio en vez de confesar hueco. IT/PT bimodal: un solo umbral falla por ambos lados. Sin poligonos no hay p99 -> calibrar a mano 6 paises es el trabajo inviable; el umbral queda conjetura disfrazada.
- **Sellado:** El umbral vive en el perfil (no en codigo) y idealmente esta derivado del p99 reproducible. Multi-via: (1) sanity ES: p99 calculado ~30km valida el metodo (NEXT-LEVEL.md:372); (2) % de geocodificaciones validas rechazadas pre/post -> con p99 los rechazos de municipios grandes caen a ~0 sin subir falsos positivos (golden textual-vs-espacial); (3) reproducibilidad determinista; (4) cambiar el umbral no toca el motor (data/<cc>), default ES=30 byte-identico; (5) fixture extranjero: municipio grande pais#2 con punto a 45km no se rechaza bajo SU umbral (cruza F23).
- **NEXT-LEVEL:** PostGIS (ST_MaximumInscribedCircle/ST_Area) + GeoPandas/Shapely (BSD-3-Clause ambos) — https://github.com/geopandas/geopandas [VERIFIED NEXT-LEVEL.md:369]. Match DIRECTO: deriva el p99 del radio municipal por pais desde poligonos y fija el umbral como dato calibrado del GeoProfile (self-improving). EUR0 pip puro, job una vez por pais. Palanca superior: PostGIS ST_Contains+GiST sobre geoBoundaries CGAZ (geoBoundaries CC-BY 4.0/ODbL; PostGIS GPL-2.0 servicio) — https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353] elimina el umbral de raiz con point-in-polygon exacto, reservandolo solo para fallback centroide (F26).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/geocode.py:49`** [VERIFIED]: `KNN_MAX_DISTANCE_KM: float = 30.0` — constante global de modulo, no parametrica.
- **`geocode.py:191`** [VERIFIED]: dentro de `nearest_municipality`, `if dist_km > KNN_MAX_DISTANCE_KM: return (None, dist_km)` — el umbral decide si la geocodificacion se acepta o se confiesa hueco. `:189-190` calcula `dist_km` por haversine exacto solo para el ganador del argmin equirectangular (`:187`).
- **`geocode.py:16-22`** [VERIFIED]: el rationale del docstring fija el 30km al tamano ES: *"The largest Spanish municipalities by area have a typical radius of 15-20 km (Lorca ~1,676 km², radius ~23 km; Caceres ~1,750 km², radius ~24 km). A 30 km threshold gives a comfortable margin for sparse rural provinces (e.g. Soria, Cuenca)..."*. `:43-48` repite la justificacion ES ("30 km is defensible for Spain").
- Doctrina [VERIFIED `geocode.py:13-14`]: el umbral implementa "better a hole than a lie" — heredada del B4.2 ambiguity guard.

##### (b) Mecanismo al atomo
El reverse-geocode municipal es KNN-centroide: dado (lat, lon, province_code) busca el centroide de municipio mas cercano DENTRO de la provincia (`_index[province_code]`, F15) por distancia equirectangular (argmin barato, `:182-187`), confirma con haversine exacto el ganador (`:190`), y RECHAZA si supera `KNN_MAX_DISTANCE_KM` (`:191`). El umbral es el unico parametro de CALIDAD del geocoder: demasiado bajo sobre-rechaza (huecos falsos), demasiado alto sobre-acepta (cross-municipio). El 30km esta calibrado a mano al radio tipico del municipio ES (Lorca/Caceres ~24km). El atomo: este es un numero de DATO, no de algoritmo — la matematica haversine es country-agnostica (F15), solo el 30 esta soldado a ES. F16 NO es correctness (eso es F15, el scoping del indice), es la CALIBRACION: trasladar el 30 al GeoProfile (default 30 ES, byte-identico) y, a nivel inalcanzable, DERIVARLO del p99 del radio municipal real del pais en vez de elegirlo a mano. Separacion limpia con F15: F15 arregla que el indice no funda paises (sangrado); F16 arregla que el umbral no sobre/infra-rechace por pais (calidad).

##### (c) Costura ES -> generico
1. Sacar `KNN_MAX_DISTANCE_KM = 30.0` de constante de modulo a campo del GeoProfile (F8): `profile.knn_max_distance_km` con default 30.0 para 'ES'.
2. `MunicipalityGeocoder` recibe el umbral en `load`/`__init__` desde el perfil del pais del run; `:191` usa `self._threshold_km` en vez de la global.
3. **ES byte-identico**: el perfil ES declara 30.0 -> `:191` se comporta identico; ninguna geocodificacion ES cambia de resultado.
4. **Nivel siguiente (next-level)**: un job por pais deriva el umbral del p99 de la distribucion de radio municipal (sqrt(area/pi) o ST_MaximumInscribedCircle sobre los poligonos, cruza con F26) y lo escribe al perfil versionado; el numero se gana del dato, no del criterio humano.

##### (d) Riesgo adversarial concreto
- **Nordicos / MX rural / JP rural (municipios grandes)**: 30km global SOBRE-RECHAZA geocodificaciones validas — un municipio sueco/mexicano cuyo centroide esta legitimamente a 40-60km del punto del PdV devuelve None -> hueco FALSO masivo, la cobertura cae sin que falte el dato.
- **DE/zonas densas (municipios pequenos)**: 30km es DEMASIADO LAXO — en un area metropolitana con municipios de 2-3km de radio, el centroide vecino esta a <30km, asi que un punto mal-provincia-do acepta el municipio equivocado (cross-municipio) en vez de confesar hueco.
- **IT/PT (mixto)**: distribucion bimodal (Alpes/interior grandes vs costa densa) -> un solo umbral no sirve para ambos extremos; 30km falla por los dos lados.
- **Honestidad estadistica**: sin poligonos no hay forma de calcular el p99 -> la calibracion "a mano" para 6 paises es exactamente el trabajo inviable que el sello debe evitar; sin el dato, el umbral es una conjetura disfrazada de constante justificada.

##### (e) Criterio de sellado + verificacion multi-via
**Sello = el umbral vive en el perfil (no en codigo) y, idealmente, esta derivado del p99 reproducible.** Multi-via:
1. **Sanity ES**: el p99 calculado para ES debe quedar cerca de 30km — valida que el metodo reproduce el valor historico elegido a mano (`NEXT-LEVEL.md:372`).
2. **Rechazo medido pre/post**: el % de geocodificaciones validas rechazadas por umbral antes vs despues; con p99 calibrado, los rechazos de municipios grandes legitimos caen a ~0 SIN que suban los falsos positivos, medido sobre el golden textual-vs-espacial.
3. **Reproducibilidad**: re-correr el job da el mismo umbral (determinista).
4. **Via perfil**: cambiar el umbral NO toca el motor (vive en data/<cc>); test que el default ES=30 produce geocodificacion byte-identica.
5. **Via fixture extranjero** (cruza con F23): probar que un municipio grande de pais #2 con punto a 45km no se rechaza bajo SU umbral calibrado.

##### (f) Herramienta next-level
**PostGIS (ST_MaximumInscribedCircle / ST_Area) + GeoPandas/Shapely** (GeoPandas: BSD-3-Clause; Shapely: BSD-3-Clause) — https://github.com/geopandas/geopandas [VERIFIED NEXT-LEVEL.md:369]. **Match DIRECTO** con F16 (`NEXT-LEVEL.md:366-372`): deriva por pais la distribucion del radio municipal a partir de los poligonos (`ST_MaximumInscribedCircle` o `sqrt(area/pi)`) y fija `KNN_MAX_DISTANCE_KM` al p99 — el umbral deja de ser constante ES elegida a mano y pasa a DATO calibrado y reproducible del GeoProfile, recalculable cuando cambian las fronteras (self-improving: el numero se gana del dato). Ruta EUR0: todo BSD/MIT pip puro; el job corre una vez por pais sobre los poligonos ya descargados. PALANCA SUPERIOR ASOCIADA: **PostGIS ST_Contains + GiST sobre geoBoundaries CGAZ** (geoBoundaries: CC-BY 4.0 / ODbL; PostGIS: GPL-2.0 servicio no-embebido) — https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353] elimina el umbral DE RAIZ: point-in-polygon da contencion exacta (un punto cae en exactamente 1 municipio o en ninguno -> hueco), reservando el umbral solo para el fallback centroide cuando falta poligono (F26). Verificacion 2-via del p99 (`NEXT-LEVEL.md:372`): sanity ES~30km + caida de rechazos de municipios grandes a ~0 sin nuevos falsos positivos. Alternativa: DuckDB spatial (ST_Area sobre GeoParquet) o Shapely puro.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f17"></a>

#### F17 · PostcodeIndex (CP->muni) + fuente/formato de CP por pais

**Ficha rápida**

- **Costura (ES→genérico):** El indice CP->muni esta soldado al Nomenclator INE ES en 4 atomos: ruta unica `_NOMENCLATOR_PATH` al CSV INE [VERIFIED geocode.py:51-53]; columnas `codigo_postal`/`municipio_id` del header INE [VERIFIED geocode.py:237-238]; guarda de ancho `len(mid)!=5` que asume muni de 5 chars [VERIFIED geocode.py:239]; y clave CP tratada como string opaco con `.strip()` sin parser de formato postal del pais [VERIFIED geocode.py:237,257]. La doctrina ambiguo/desconocido->None [VERIFIED geocode.py:253-260] ya es generica y correcta. Resultado: un 2o pais no tiene indice, el `len==5` descarta en silencio todo CSV de muni 6/8-dig, y PT/JP con CP de 7-con-guion no se parsean.
- **Fix:** Parametrizar por `GeoProfile` (F8): (1) ruta `profile.postcode_source` -> `data/<cc>/geo/postcodes.csv` (default ES = `_NOMENCLATOR_PATH`, ausencia no-fatal ya existente geocode.py:231-232); (2) esquema `profile.postcode_schema={"cp":"codigo_postal","muni":"municipio_id"}`; (3) ancho `len(mid)!=profile.shape.muni_width` (cruza F1: ES=5/DE=8/IT=6); (4) formato `cp = profile.normalize_postcode(raw)` aplicado IGUAL en load y en resolve — ES=`raw.strip()` byte-identico, PT `NNNN-NNN`/JP `NNN-NNNN` canonizan el guion idempotentemente. Doctrina ambiguo->None intacta para todo pais. Default ES reproduce el indice bit a bit. Para el indice de localidad que comparte CSV (F13), declarar transliteracion del nombre via AnyAscii cuando el perfil lo pida (cruza F10).
- **Adversarial:** 2o pais sin Nomenclator: indice vacio -> CP off (no-fatal) pero el backfill pierde su 2a via €0. DE-AGS 8 / IT-ISTAT 6: la guarda `len(mid)!=5` descarta SILENCIOSAMENTE todo el CSV extranjero (ningun muni mide 5) -> cobertura de CP a 0 sin error. PT `NNNN-NNN` y JP `NNN-NNNN` (7 con guion): el CP entra como clave cruda; si la consulta llega sin guion (o al reves) `resolve` falla el match -> huecos espureos. JP + romaji ausente: el campo CP es numerico (ok) pero el indice de localidad que comparte el mismo CSV no transliterado (F13) queda ciego. Colision de ancho: un CP de longitud distinta no canonizado puede colisionar claves entre munis -> resoluciones cruzadas.
- **Sellado:** Sellado cuando ruta+esquema+ancho+formato de CP vienen del perfil, ES es byte-identico, y un CP de 7-con-guion (PT/JP) resuelve sin que la guarda de ancho descarte su muni. Multi-via: (1) ES byte-identico — `load()` con perfil ES da los mismos unambiguous/ambiguous y el backfill rellena los mismos ~111 por CP; (2) ancho extranjero — fixture DE/IT muni 8/6-dig CARGA con `profile.shape.muni_width` donde el `len==5` viejo cargaba 0; (3) formato — PT `1000-001`/JP `100-0001` resuelven con o sin guion (idempotencia de `normalize_postcode`); (4) ortogonal — el muni del CP cruza contra el geocoder espacial (F15) y/o el `postcode` de libpostal sobre el texto crudo; divergencia = hueco, no merge; (5) ambiguedad — un CP que abarca >1 muni sigue devolviendo None en todo pais.
- **NEXT-LEVEL:** libpostal (+ pypostal) — MIT — https://github.com/openvenues/libpostal [VERIFIED NEXT-LEVEL.md:342-348 y :471-477]: parser estadistico (1B+ direcciones, 60+ idiomas) que extrae el `postcode` etiquetado de cualquier texto de direccion sin importar orden de campos, alimentando el PostcodeIndex con el CP ya tipado en vez de regex ES-shaped, y aportando la 2a via ortogonal (su `province/city` cruza contra el muni del CP). Modelo estatico OSM+OpenAddresses, ~2GB descarga unica, sin servicio -> €0. Secundaria: AnyAscii — ISC — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:326-332] para transliterar la clave-nombre del indice de localidad que comparte CSV (JP romaji ausente); el campo CP en si es numerico y no la requiere.

**Deep-spec 360**

##### (a) Verificacion de code_hints [leido a fuente]
- **[VERIFIED pipeline/geocode.py:51-53]** `_NOMENCLATOR_PATH: Path = (Path(__file__).resolve().parent.parent / "data" / "geo" / "nomenclator_entidades_ine.csv")` — ruta UNICA al Nomenclator INE ES, constante de modulo.
- **[VERIFIED pipeline/geocode.py:205-212]** `class PostcodeIndex:` con docstring "Map Spanish postcodes to municipality_code via the INE Nomenclator. Postcodes that span more than one municipality are ambiguous and return None ('better a hole than a lie')".
- **[VERIFIED pipeline/geocode.py:224-251]** `load(cls, path: Path = _NOMENCLATOR_PATH)`: lee CSV con `csv.DictReader`; **[VERIFIED :237-240]** `cp = row.get("codigo_postal", "").strip(); mid = row.get("municipio_id", "").strip(); if not cp or len(mid) != 5: continue` — columnas INE soldadas y guarda de ancho `len(mid)!=5`; **[VERIFIED :243-249]** colapsa a `unambiguous` (1 muni) vs `ambiguous` (>1).
- **[VERIFIED pipeline/geocode.py:253-260]** `resolve(self, postcode)`: `if cp in self._ambiguous: return None; return self._unambiguous.get(cp)` — doctrina ambiguo/desconocido -> None.
- Consumidor [VERIFIED scripts/backfill_municipality_geo.py:44,64] `cp = PostcodeIndex.load()` y `code = cp.resolve(r["postcode"])`.

CONCLUSION: el indice CP->muni esta soldado al Nomenclator INE ES (ruta + columnas `codigo_postal`/`municipio_id` + guarda `len==5`), aunque la doctrina ambiguo->None ya es generica y correcta.

##### (b) Mecanismo al atomo
`PostcodeIndex` es un mapa determinista CP->leaf con red de seguridad de ambiguedad: agrupa `cp -> {munis}` (geocode.py:229-241); un CP con UN muni va a `unambiguous`, con >1 va a `ambiguous` (:245-249); `resolve` devuelve el muni o None si ambiguo/desconocido (:253-260). Es el SEGUNDO geosignal del backfill €0 (tras lat/lon): `backfill_municipality_geo.py:63-68` lo usa cuando no hay coordenadas. Tres atomos lo atan a ES:
1. **Fuente/ruta**: un solo CSV INE (`_NOMENCLATOR_PATH`).
2. **Esquema**: columnas `codigo_postal` + `municipio_id` (header INE).
3. **Forma del leaf**: `len(mid) != 5` -> descarta toda fila cuyo muni no sea de 5 chars (ancho INE), cruza con F1.
La CLAVE (el CP) es ademas tratada como string opaco con `.strip()` — no hay parser de formato postal: ES "28001" entra crudo; un PT "1000-001" o un JP "100-0001" entrarian con guion sin normalizar.

##### (c) Costura ES->generico + fix exacto
**Costura**: ruta unica + columnas INE + `len==5` + clave CP sin parsear el formato del pais.
**Fix exacto**:
1. **Ruta por perfil (F8)**: `path = profile.postcode_source` -> `data/<cc>/geo/postcodes.csv`; default ES = `_NOMENCLATOR_PATH` (byte-identico). Ausencia no-fatal: `if not path.exists(): return cls({}, set())` ya existe (:231-232) -> CP off, fuzzy/lat-lon siguen.
2. **Esquema por perfil**: abstraer las columnas a `profile.postcode_schema = {"cp": "codigo_postal", "muni": "municipio_id"}`; ES mapea a las columnas INE actuales.
3. **Ancho del leaf por perfil**: `len(mid) != 5` -> `len(mid) != profile.shape.muni_width` (cruza F1: ES=5, DE-AGS=8, IT-ISTAT=6). Para ES el ancho es 5 -> mismo filtrado.
4. **Formato/normalizacion de CP por pais**: anteponer `cp = profile.normalize_postcode(raw)`. ES = `raw.strip()` (byte-identico). PT `NNNN-NNN` (7 con guion), JP `NNN-NNNN` (7 con guion), DE/FR/IT/MX (5 sin guion) -> el normalizador del perfil canoniza (mantiene o quita guion segun la clave que el indice usara), de modo que `resolve(raw)` aplique la MISMA canonicalizacion a la consulta. Para CP con romaji ausente (JP), la clave es numerica -> no necesita transliteracion; pero el INDICE de LOCALIDAD que comparte CSV hoy (gazetteer, F13) SI -> declarar transliteracion del campo nombre via AnyAscii cuando el perfil lo pida (cruza F10/F13).
5. **Doctrina ambiguo->None intacta** para todo pais (es generica y correcta — no se toca).
**Default ES = byte-identico**: ruta INE, columnas INE, ancho 5, `strip()` -> el indice ES resultante es identico bit a bit.

##### (d) Riesgo adversarial concreto
- **2o pais sin Nomenclator**: ruta unica ES -> el indice queda vacio para el pais #2 -> CP off (ya no-fatal por :231-232) — degradacion honesta, pero el backfill pierde su 2a via €0.
- **DE-AGS 8 / IT-ISTAT 6**: la guarda `len(mid)!=5` DESCARTA SILENCIOSAMENTE todo el CSV extranjero (ningun muni mide 5) -> cobertura de CP cae a 0 SIN error -> el backfill no puede usar CP en esos paises sin que nada lo avise.
- **PT `NNNN-NNN` (7) / JP `NNN-NNNN` (7)**: el CP con guion entra como clave cruda; si la consulta llega sin guion (o viceversa), `resolve` falla el match -> huecos espureos; el parsing del guion no esta contemplado.
- **JP + romaji ausente**: el CAMPO CP es numerico (ok), pero el indice de localidad/nombre que comparte el mismo CSV no transliterado (F13) queda ciego — el riesgo migra al gazetteer.
- **Ruido / colision de ancho**: un pais con CP de longitud distinta a ES que NO se filtra por `len==5` (porque ahi se filtra el MUNI, no el CP) podria colisionar claves CP entre munis si el formato no se canoniza -> resoluciones cruzadas.

##### (e) Criterio de sellado + verificacion multi-via
**Sellado** cuando: (1) ruta+esquema+ancho+formato de CP vienen del perfil; (2) ES byte-identico; (3) un pais con CP de 7-con-guion (PT/JP) resuelve correctamente y la guarda de ancho NO descarta su muni.
**Multi-via**:
- *Via 1 (ES byte-identico)*: golden — `PostcodeIndex.load()` con perfil ES produce los mismos `unambiguous`/`ambiguous` que hoy (mismos tamanos, mismas resoluciones); `backfill` rellena los mismos ~111 por CP.
- *Via 2 (ancho extranjero)*: fixture DE/IT con muni 8/6-dig -> con `profile.shape.muni_width` el indice CARGA (no descarta); con el `len==5` viejo cargaria 0 (prueba de que la guarda era la causa).
- *Via 3 (formato de CP)*: fixture PT `1000-001` y JP `100-0001` -> `resolve` con normalizador del perfil devuelve el muni correcto tanto si la consulta trae guion como si no (idempotencia de `normalize_postcode`).
- *Via 4 (ortogonal)*: el CP resuelto cruza contra el geocoder espacial (F15) y/o libpostal sobre el texto crudo de direccion — el muni del CP y el del componente postal parseado CONCUERDAN; divergencia = hueco confesado, no merge (doctrina ambiguo->None preservada).
- *Via 5 (ambiguedad)*: un CP que abarca >1 muni sigue devolviendo None en todo pais (regresion-test del invariante 'better a hole than a lie').

##### (f) Herramienta NEXT-LEVEL [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md]
- **libpostal (+ pypostal)** — MIT — https://github.com/openvenues/libpostal — [VERIFIED NEXT-LEVEL.md:342-348 (geo cluster) y :471-477 (identity-vehicle)]. Parser estadistico entrenado en 1B+ direcciones que devuelve componentes etiquetados (incl. `postcode`) en 60+ idiomas, country-agnostico: extrae el CP de un texto de direccion sin importar el orden de campos (DE/JP con CP primero, calle al final), ALIMENTANDO el `PostcodeIndex` con el CP ya tipado en vez de adivinar con regex ES-shaped [VERIFIED NEXT-LEVEL.md:343]. Modelo estatico reproducible (OSM+OpenAddresses), ~2GB descarga unica, sin servicio de pago — €0. Provee ademas la 2a via ortogonal: el `state/province/city` de libpostal cruza contra el muni del CP (sellado del punto si concuerdan).
- **AnyAscii** — ISC — https://github.com/anyascii/anyascii — [VERIFIED NEXT-LEVEL.md:326-332]. Secundaria pero nombrada por el propio riesgo de la faceta: el INDICE de localidad/nombre que comparte CSV con el CP (JP "romaji ausente") necesita transliteracion de la clave-nombre; AnyAscii la aporta limpia (ISC). El campo CP en si es numerico y no la requiere.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f18"></a>

#### F18 · Seeder de centroides country-scoped + dataset/quirk

**Ficha rápida**

- **Costura (ES→genérico):** seed_geo_centroides fetch (:70-73) y UPDATE (:96-98) son country-blind: 'WHERE code = ANY($1::char(5)[])' (:71) y 'WHERE code = $3' (:97) sin country_code. Ademas el swap lon/lat (:54-55) es especifico de la fuente ine-places. Parametrizar --country en ambas queries, cargar el CSV del pack, y declarar el quirk como transform per-fuente.
- **Fix:** fetch -> 'WHERE country_code=$2 AND code = ANY($1::text[])' (default $2=ES); UPDATE -> 'WHERE country_code=$4 AND code=$3' (default $4=ES). Cast char(5)[] (:71) -> text[] -cruza F1-. Swap lon/lat -> bandera coord_order del pack ('lonlat'|'latlon'), default ES 'lonlat' byte-identico. ES queda idempotente (0 updates en re-run).
- **Adversarial:** Sembrar el pais #2 con code homonimo '28001' SOBRESCRIBE el centroide ES (UPDATE WHERE code=$3 country-blind, :97) -> reverse-geocode ES falla tras el onboarding. Quirk lon/lat (:54-55) copiado a ciegas a una fuente con orden correcto refleja TODOS los centroides sobre el meridiano. Cast char(5)[] (:71) descarta silenciosamente codes de 6/8 digitos (AGS/ISTAT) -> 0 centroides, sin error.
- **Sellado:** (1) ES byte-identico: re-run -> 0 updates, conteo centroides inalterado. (2) Aislamiento cross-pais: tras sembrar pais #2 homonimo, centroide ES IDENTICO (bleed=0). (3) Gate de quirk: CSV como Table Schema frictionless con lat[-90,90]/lon[-180,180]+bbox per-pais -> swap/fuera-bbox FALLA antes del UPDATE [VERIFIED NEXT-LEVEL.md:340]. (4) Round-trip: centroide de X cae en poligono de X (ST_Contains, cruza F26). (5) Cobertura como intervalo, nunca 100% redondeado.
- **NEXT-LEVEL:** Frictionless Framework (frictionless-py, Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. CSV de centroides como data/<cc>/geo/pack.schema.json versionado (tipos lat/lon, bbox per-pais, regex ancho code) validado en bootstrap+CI ANTES del UPDATE country-blind. 'centroide fuera de bbox -> validacion FALLA' [VERIFIED NEXT-LEVEL.md:340] atrapa el swap lon/lat y el overflow de ancho en una puerta declarativa.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED scripts/seed_geo_centroides.py:30-57]** `_load_centroides`: el quirk lon/lat esta en :49-56:
  ```python
  real_lon = float(raw_lat)   # :54  -- la columna 'lat' del CSV lleva la LONGITUD
  real_lat = float(raw_lon)   # :55  -- la columna 'lon' del CSV lleva la LATITUD
  result[code] = (real_lat, real_lon)  # :56
  ```
  Especifico de la fuente `PopulateTools/ine-places` (docstring :2-4).
- **[VERIFIED seed_geo_centroides.py:68-99]** fetch + UPDATE **country-blind**:
  - fetch :70-73 `SELECT code, lat, lon FROM geo_municipality WHERE code = ANY($1::char(5)[])` — SIN `country_code`; el cast `char(5)[]` esta en :71.
  - UPDATE :96-98 `UPDATE geo_municipality SET lat = $1, lon = $2 WHERE code = $3` — SIN `country_code`; el `WHERE code=$3` esta en :97.

##### (b) El mecanismo al atomo
1. `_load_centroides` (:30) lee el CSV `data/geo/municipios_centroides.csv` (latin-1, :41), aplica el swap lon/lat (:54-55), devuelve `{code5: (lat, lon)}`.
2. `seed` (:60) hace fetch del estado DB SOLO para los codes del CSV via `ANY($1::char(5)[])` (:71) — **sin filtro de pais**.
3. Diff MVCC (:84-92): salta si ya correcto (`abs(current-new)<1e-9`, :89); si no, encola `(lat, lon, code)`.
4. `executemany` del UPDATE (:96-98) — **sin filtro de pais**.

**Dos concerns distintos** (F18 se separa de F1 por concern, no por archivo):
- **Seguridad-de-escritura**: el `WHERE code=$3` country-blind (:97) pisa AMBAS filas `(ES,'28001')` y `(DE,'28001')`.
- **Formato-dato/quirk**: el swap lon/lat (:54-55) es de la fuente `ine-places`; otra fuente con orden correcto se cargaria invertida si se copia el swap a ciegas.

##### (c) La costura ES->generico con su fix exacto
- **Costura**: parametrizar `--country` con `AND country_code=$x` en fetch Y UPDATE; cargar el CSV de centroides del pack; declarar el quirk como transform PER-FUENTE, no hardcode.
- **Fix exacto**:
  - fetch -> `SELECT code, lat, lon FROM geo_municipality WHERE country_code=$2 AND code = ANY($1::text[])` (default `$2='ES'`).
  - UPDATE -> `UPDATE geo_municipality SET lat=$1, lon=$2 WHERE country_code=$4 AND code=$3` (default `$4='ES'`).
  - el cast `char(5)[]` (:71) -> `text[]` (o el tipo per-pais) — **cruza con F1** (overflow de ancho).
  - el swap lon/lat -> bandera `coord_order` del pack (`'lonlat'|'latlon'`), default ES `'lonlat'` byte-identico.
- ES queda byte-identico: mismos UPDATE, mismo resultado (idempotente -> 0 updates en re-run).

##### (d) El riesgo adversarial concreto
- **Sobrescritura cross-pais**: sembrar centroides del pais #2 con un code homonimo (`'28001'`) SOBRESCRIBE el centroide ES de ese code -> el reverse-geocode ES empieza a fallar **tras** un onboarding. Corrupcion silenciosa.
- **Quirk copiado a ciegas**: el swap lon/lat (:54-55) es de `ine-places`; otra fuente (GeoNames, con orden correcto lat,lon) cargada con el swap -> TODOS los centroides reflejados sobre el meridiano (lat<->lon) -> cada punto cae en otro continente.
- **char(5)[] silencioso**: un code de muni de otra longitud (AGS 8, ISTAT 6) NO casa el `ANY($1::char(5)[])` (:71) -> 0 filas fetcheadas -> 0 centroides sembrados -> **sin error**, cobertura de centroides cae a 0.

##### (e) Criterio de sellado + verificacion multi-via
1. **ES byte-identico**: re-correr el seeder ES -> 0 updates (idempotente, todos ya sembrados); conteo de centroides ES inalterado.
2. **Aislamiento cross-pais**: tras sembrar el pais #2 con un code homonimo, assert que el centroide ES de ese code es **IDENTICO** al previo (bleed=0).
3. **Gate de quirk (herramienta)**: el CSV de centroides declarado como Table Schema frictionless con `lat in [-90,90]`, `lon in [-180,180]` Y un bbox per-pais -> un centroide swapeado/fuera-de-bbox **FALLA** la validacion ANTES del UPDATE [VERIFIED NEXT-LEVEL.md:340].
4. **Round-trip espacial** (cruza F26 point-in-polygon): el centroide del municipio X cae DENTRO del poligono de X (`ST_Contains=true`); los que fallan revelan centroides corruptos.
5. **Cobertura honesta**: `% muni con centroide` reportado como intervalo, nunca redondeado a 100%.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **Frictionless Framework** (frictionless-py, Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. El CSV de centroides se declara como `data/<cc>/geo/pack.schema.json` versionado: tipos `lat`/`lon`, bounds bbox per-pais, regex de ancho de `code`. Se valida en el bootstrap del pais y en CI ANTES de que el UPDATE country-blind pueda corromper nada. Verificacion clave [VERIFIED NEXT-LEVEL.md:340]: 'un centroide fuera de bbox del pais -> la validacion DEBE fallar' — atrapa el swap lon/lat (un centroide ES con lat=-3.7 cae fuera del bbox latitudinal de Espana) y el overflow de ancho de codigo en una sola puerta declarativa. Aplica la doctrina COUNTRY-PROOF ('que la maquina imponga y pruebe la regla') a la INGESTA del pack.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f19"></a>

#### F19 · Backfill write-loops country-scoping + self-verify por predicado

**Ficha rápida**

- **Costura (ES→genérico):** Dos scripts de escritura sin country_code: geo_backfill.py (_fetch_gap_entities :61-77 sin country; geocoder country-blind :105; UPDATE char(5)[] :155-170) y backfill_municipality_geo.py (_SELECT :32-37 sin country; valid set country-blind 'SELECT code FROM geo_municipality' :46; self-verify code[:2]!=prov :72 que hardcodea el prefijo ES — 3ª copia del predicado triplicado de F3).
- **Fix:** (1) AND country_code=$1 en ambos fetch; (2) geocoder country-scoped (F15) con bucket (country_code,province_code); (3) valid set por (country_code,code) no code solo; (4) self-verify llama al predicado de forma per-pais (F3, fuente unica): ES mantiene left(code,2)==province_code, un pais sin prefijo (DE AGS/FR) declara 'sin invariante' y valida por point-in-polygon; (5) cast char(5)[] → ancho del pack (F1). Default ES byte-identico.
- **Adversarial:** Entity pais#2 con provincia homonima '28' + geocoder country-blind → se rellena con municipio ES de Madrid (identidad geografica falsa escrita); en pais sin prefijo code[:2]!=prov rechaza TODA resolucion valida (sobre-vaciado total a 0 sin error); valid country-blind acepta code pais#2 que coincide con uno ES; char(5)[] trunca AGS-8/ISTAT-6 (F1); postcode PT NNNN-NNN / JP 7-digit rompen PostcodeIndex (len!=5, F17).
- **Sellado:** Golden ES idéntico (resoluciones/skips/counts); country-isolation: entity pais#2 jamas recibe municipio de otro pais (fixture forma-extranjera F23); el self-verify pasa para ES (prefijo) y para pais sin-prefijo (via PIP) sin sobre-vaciar; 2-via KNN vs PIP/postcode (divergencia=hueco); MVCC NULL→value idempotente. sealed=false si rechaza pais sin-prefijo.
- **NEXT-LEVEL:** PostGIS (ST_Contains+GiST) sobre geoBoundaries — el self-verify pasa de regla-string code[:2]==prov a invariante geometrico (point-in-polygon), country-proof sin predicado de prefijo. geoBoundaries CC-BY 4.0/ODbL (datos); PostGIS GPL-2.0 (servicio, no se embebe). https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353] (compartida con F26). Postcode multilingue: libpostal (MIT, https://github.com/openvenues/libpostal [VERIFIED:345]). Reconciliacion 2-via: DataComPy (Apache-2.0 [VERIFIED:417]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED] (DOS scripts)
**scripts/geo_backfill.py**
- **:61-77** [VERIFIED] `_fetch_gap_entities`: `SELECT entity_ulid,kind,lat,lon,postcode,province_code FROM entity WHERE municipality_code IS NULL AND ((lat IS NOT NULL AND lon IS NOT NULL) OR postcode IS NOT NULL)`. SIN `country_code`.
- **:105** [VERIFIED] `muni_geocoder.nearest_municipality(ent.lat, ent.lon, ent.province_code)` — geocoder country-blind (F15), solo recibe `province_code`.
- **:155-170** [VERIFIED] UPDATE bulk con `unnest($2::char(5)[])` (:164) → cast `char(5)[]` (cruza overflow de ancho F1); guard MVCC `AND e.municipality_code IS NULL` (:169), SIN country.
**scripts/backfill_municipality_geo.py**
- **:32-37** [VERIFIED] `_SELECT`: `WHERE municipality_code IS NULL AND kind <> 'particular' AND province_code IS NOT NULL AND (postcode IS NOT NULL OR (lat/lon))`. SIN `country_code`.
- **:46** [VERIFIED] `valid = {r["code"] for r in await conn.fetch("SELECT code FROM geo_municipality")}` — set de codigos validos country-blind; tras 0053 `code` NO es unico → colapsa ES + pais#2 en un solo set.
- **:57-58** [VERIFIED] `geo.nearest_municipality(r["lat"], r["lon"], prov)` — country-blind.
- **:72** [VERIFIED] `if code not in valid or code[:2] != prov:` — el self-verify HARDCODEA el invariante de prefijo ES (`left(code,2)==province_code`). Es la 3ª copia del predicado triplicado de F3, aqui en el backfill.

##### (b) Mecanismo al atomo
Ambos scripts rellenan `entity.municipality_code` para el hueco €0-señal (lat/lon o postcode). Orden por entity, primer match gana: (1) lat/lon → `MunicipalityGeocoder` KNN province-scoped, rechaza >`KNN_MAX_DISTANCE_KM`=30 → "better a hole than a lie"; (2) si falla, postcode → `PostcodeIndex` (ambiguo→None). `geo_backfill.py` escribe en paginas de 2000 con `UPDATE … unnest`, solo NULL→code; el trigger `trg_entity_set_comarca` cierra `comarca_id`. `backfill_municipality_geo.py` añade el **SELF-VERIFY gate** (:71-74): el code resuelto se escribe SOLO si (a) existe en `geo_municipality` y (b) su prefijo casa `province_code`; si no, se salta (NULL queda NULL — "a wrong municipality is never written").

##### (c) Costura ES→generico + fix exacto
1. **Country-scopear el fetch**: `AND country_code = $1` en `geo_backfill.py:67-77` y `backfill_municipality_geo.py:32-37`.
2. **Geocoder country-scoped** (F15): propagar el country del run a `nearest_municipality` (clavar el bucket por `(country_code, province_code)`).
3. **`valid` set por `(country_code, code)`**, no `code` solo (`backfill_municipality_geo.py:46`).
4. **Self-verify por PREDICADO per-pais** (F3, fuente unica): ES mantiene `left(code,2)==province_code` byte-identico; un pais sin relacion prefijo (DE AGS, FR) declara "sin invariante" y el gate valida por **pertenencia geometrica** (point-in-polygon), no por prefijo.
5. **Cast `char(5)[]` → ancho del pack** (`geo_backfill.py:164`, cruza F1). Default ES → backfill byte-identico.

##### (d) Riesgo adversarial concreto
- **Cross-pais silencioso**: una entity pais#2 con provincia homonima `'28'` + geocoder country-blind → se rellena con un municipio **ES** de la provincia 28 (Madrid) → identidad geografica falsa ESCRITA (no revertible por sample-delete si alimenta cdp_code).
- **Sobre-vaciado total**: en pais SIN prefijo, `code[:2] != prov` (:72) RECHAZA TODA resolucion valida (un AGS-DE nunca empieza por el codigo de provincia) → la cobertura del backfill cae a 0 sin un solo error.
- **`valid` country-blind**: acepta un code pais#2 que por casualidad coincide con un code ES existente.
- **Ancho**: `char(5)[]` (:164) trunca AGS-8 / ISTAT-6 (F1).
- **Ruido/postcode**: PT `NNNN-NNN` o JP 7-digit rompen `PostcodeIndex` (len!=5, F17) → el postcode-path muere callado.

##### (e) Criterio de sellado + verificacion multi-via
1. **Golden ES**: backfill ES idéntico (mismas resoluciones, mismos skips, mismos counts por metodo).
2. **Country-isolation**: una entity pais#2 JAMAS recibe un municipio de otro pais (assert: todo code escrito pertenece al country de la entity) — probado con fixture forma-extranjera (F23).
3. **Predicado**: el self-verify pasa para ES (prefijo) Y para un pais sin-prefijo (via PIP) sin sobre-vaciar.
4. **2-via**: resolucion KNN vs PIP/postcode en muestra; divergencia = hueco confesado, no merge.
5. **MVCC**: solo NULL→value, re-run idempotente. `sealed=false` si el self-verify rechaza un pais sin-prefijo.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **PRIMARIA — PostGIS (ST_Contains + GiST) sobre geoBoundaries**: el self-verify deja de ser la regla-string `code[:2]==prov` y pasa a invariante GEOMETRICO — el code se escribe SOLO si el punto de la entity cae en el poligono del municipio resuelto: exacto, country-proof, sin predicado de prefijo. geoBoundaries: **CC-BY 4.0 / ODbL** (datos); PostGIS: **GPL-2.0** (servicio, NO se embebe en codigo distribuido). https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353] (palanca compartida con F26).
- **Postcode-path multilingue — libpostal**: parser estadistico que extrae postcode/city/state tipados en 100+ paises (PT NNNN-NNN, JP, orden de campos distinto). **MIT**, €0. https://github.com/openvenues/libpostal [VERIFIED NEXT-LEVEL.md:345].
- **Reconciliacion 2-via — DataComPy** (Apache-2.0 [VERIFIED NEXT-LEVEL.md:417]).

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f20"></a>

#### F20 · Propagacion de pais en PRODUCTORES (discover/ingest -> entity + cdp_code)

**Ficha rápida**

- **Costura (ES→genérico):** DiscoveredEntity no transporta country_code; cdp_code(...) [VERIFIED discover.py:91-93] y el INSERT [VERIFIED discover.py:96-99] omiten country_code (caen al DEFAULT 'ES'); GeoResolver/ProvinceGeocoder.load sin pais [VERIFIED discover.py:127-131]. mint_code ya es parametrico [VERIFIED codes.py:44-53].
- **Fix:** End-to-end default-ES byte-identico: (1) country_code:str='ES' en DiscoveredEntity; (2) cdp_code(..., country_code=e.country_code); (3) anadir columna country_code al INSERT+VALUES; (4) GeoResolver.load(conn, country)/ProvinceGeocoder.load(conn, country) (cruza F9/F15). Con 'ES' por defecto, CDP-ES- + columna 'ES' = golden.
- **Adversarial:** Run del pais #2 -> entidades country_code DEFAULT 'ES' + prefijo CDP-ES- -> identidad mislabeled e INMUTABLE (append-only), indistinguible de ES en queries country-scoped. El productor es el sitio de minteo: corrupcion en la fuente. Homonimo de provincia (DE-28 vs ES-28): resolver country-blind -> muni ES -> CDP-ES-28 -> dealer aleman queda espanol para siempre.
- **Sellado:** 1) Golden: fixture pais #2 -> CDP-<cc>- + entity.country_code=<cc>; 0 filas CDP-ES- para input extranjero; run ES byte-identico (diff cdp_code=0). 2) 2a via: count GROUP BY country_code == count por prefijo cdp_code. 3) Invariante cross-pack: pais del prefijo == entity.country_code. 4) Inmutabilidad: re-discover ES no re-keya nada. 5) Trazas de skip intactas.
- **NEXT-LEVEL:** Pydantic — country-pack tipado + test CI de biyeccion source_health<->registry<->lock_key (0 UNMAPPED/0 ORPHAN) que convierte el DEFAULT-ES-silencioso en build ROJO. https://github.com/pydantic/pydantic · MIT · €0=True [VERIFIED NEXT-LEVEL.md:584-590]. Nota: el threading del productor es plumbing; Pydantic eleva el GUARD que impide el default ES silencioso en produccion.

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED pipeline/discover.py:77-114] `_upsert(conn, geo, e, geocoder)`:
  - [:80-90] resuelve `prov`/`muni` via `geo.*` (resolver country-blind) + recovery por ciudad/geocoder.
  - [:91-93] `code = cdp_code(province_code=prov, domain=e.website, cif=e.cif, name=..., municipality_code=muni, address=e.address)` — NO pasa `country_code` -> cae al DEFAULT 'ES'.
  - [:96-99] `INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code, municipality_code, address, postcode, lat, lon, phone, email, website, is_tier1, status, first_discovered_source, last_seen)` — la lista de columnas NO incluye `country_code` -> cae al DEFAULT 'ES' de la tabla.
- [VERIFIED pipeline/discover.py:127-131] `geo = await GeoResolver.load(conn)` (sin pais) y `ProvinceGeocoder.load(conn)` (sin pais) -> indices country-blind (cruza F9/F15).
- [VERIFIED services/api/codes.py:44-53] `mint_code(*, province_code, digest, country_code=DEFAULT_COUNTRY)` -> `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`; YA es parametrico.
- [VERIFIED services/api/codes.py:121-130] `cdp_code(...)` con `country_code: str = DEFAULT_COUNTRY` ('ES'); [:62-65] `canonical_key` deliberadamente NO mete el pais en la pre-imagen inmutable (no re-keya). El hueco es SOLO que el productor nunca pasa el pais.

##### (b) Mecanismo al atomo
`pipeline.discover` es el LAZO PRODUCTOR: corre un SourceAdapter, geo-resuelve, mintea `cdp_code` inmutable y upserta `entity`. El mint (`codes.py`) ya es generico; el atomo de rotura esta aguas-arriba, en el productor: (1) `DiscoveredEntity` no transporta `country_code`; (2) la llamada `cdp_code(...)` omite `country_code` -> 'ES'; (3) el `INSERT` omite la columna `country_code` -> DEFAULT 'ES'; (4) resolver/geocoder se cargan country-blind. Resultado: un run de cualquier pais estampa identidad ES.

##### (c) Costura ES->generico + fix exacto
- Costura: `DiscoveredEntity` sin pais; `cdp_code(...)` sin `country_code`; `INSERT` sin columna `country_code`; `GeoResolver.load`/`ProvinceGeocoder.load` sin pais.
- Fix end-to-end (default ES byte-identico):
  1. Anadir `country_code: str = "ES"` a `DiscoveredEntity` (sources/base).
  2. `code = cdp_code(..., country_code=e.country_code)` [discover.py:91-93].
  3. Anadir `country_code` a la lista de columnas y a VALUES del INSERT [discover.py:96-99].
  4. `GeoResolver.load(conn, country)` / `ProvinceGeocoder.load(conn, country)` [discover.py:127-131] (cruza F9/F15).
  - Con country='ES' por defecto, mint da `CDP-ES-` y la columna queda 'ES' -> golden byte-identico.

##### (d) Riesgo adversarial concreto
Un run del pais #2 produce entidades con `country_code` DEFAULT 'ES' y prefijo `CDP-ES-` -> identidad MISLABELED e INMUTABLE (cdp_code append-only), indistinguible de ES en queries country-scoped. El productor es el SITIO DE MINTEO: la corrupcion nace en la fuente de identidad. Se compone con el homonimo de provincia (DE-28 vs ES-28): el resolver country-blind devuelve un muni ES y el mint estampa `CDP-ES-28` -> un dealer aleman queda como espanol para siempre.

##### (e) Criterio de sellado + verificacion multi-via
1. Golden: fixture de pais #2 mintea `CDP-<cc>-` y setea `entity.country_code=<cc>`; ASSERT 0 filas `CDP-ES-` para input extranjero; ASSERT run ES byte-identico (diff cdp_code=0).
2. 2a via: `count(*) GROUP BY country_code` == `count(*)` por prefijo de substring del cdp_code; discrepancia = un mislabel se filtro.
3. Invariante (cross-pack disjointness): para toda fila, el pais del prefijo cdp_code == `entity.country_code`.
4. Inmutabilidad: re-correr discover para ES no re-keya ninguna entity (golden append-only).
5. Trazas de skip [VERIFIED discover.py:139-146] siguen emitiendo el motivo por entity (no se degrada el debug).

##### (f) Herramienta next-level
**Pydantic** — modelar el country-pack (country.toml + registry + semillas + lock_key) como esquema tipado y un test de CI que asevera la biyeccion `source_health<->registry<->lock_key` (0 UNMAPPED / 0 ORPHAN), convirtiendo el DEFAULT-'ES'-silencioso en un build ROJO mecanico. URL https://github.com/pydantic/pydantic · Lic MIT · €0=True [VERIFIED NEXT-LEVEL.md:584-590]. Nota honesta: el threading del productor es plumbing; Pydantic eleva el GUARD que impide que el default ES silencioso llegue a produccion.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f21"></a>

#### F21 · Country-scoping de LECTORES/API (router geo + stats + vistas)

**Ficha rápida**

- **Costura (ES→genérico):** Default-ES preserva los numeros: en una DB de tenant unico ES, anadir `AND <tabla>.country_code=$cc` con $cc='ES' devuelve resultados byte-identicos (toda fila es ES). La costura es enhebrar country_code (de path/header, default 'ES') en CADA query geo: el WHERE del lookup de provincia (:370), el JOIN de municipio (:388), el JOIN de comarca (defensivo), y cada COUNT/GROUP BY (:51-73,:390,:414-417, stats.py:37-38). Para ES es un no-op sobre el resultado; para el tenant #2 es la diferencia entre verdad y mezcla. El fan-out: endpoints /geo/* del router + stats.py. La dimension pais entra por la ruta (p.ej. /geo/{country}/... o header de pais + middleware) y se propaga a los params SQL. Precision: el join de comarca `co.id=m.comarca_id` es seguro sobre el surrogate id una vez `m` esta scoped; el vector real es el join de municipio y el lookup de provincia.
- **Fix:** Lookup de provincia (:370): '... FROM geo_province WHERE country_code=$2 AND code=$1'. Join del arbol (:388): 'JOIN geo_municipality m ON m.country_code=e.country_code AND m.code=e.municipality_code'. El join de comarca (:389) 'JOIN geo_comarca co ON co.id=m.comarca_id' es seguro sobre el surrogate id una vez m esta scoped; opcionalmente anadir 'AND co.country_code=e.country_code' como defensa. Anadir 'AND e.country_code=$cc' al WHERE (:390). COUNTs de completeness (:51-73): anadir 'AND country_code=$cc' a cada COUNT de entity y 'WHERE country_code=$cc' a cada COUNT de geo_*. province_only (:414-417): anadir 'AND country_code=$cc'. stats.py (:37-38): 'SELECT count(*) FROM geo_province WHERE country_code=$1' etc. (stats pasa a country-parametrizado, ES default). Invariante mecanico: todo cruce geo sobre (country_code, code).
- **Adversarial:** DE/MX-28 colisionan con ES-28: /geo/28/tree para ES podria empalmar municipios DE-Brandenburg-28 en el arbol de Madrid; el header de provincia (:370) podria devolver el nombre de DE-Brandenburg para code 28. Multiplicacion de filas: una entity con muni '28001' presente en ES y DE -> el GROUP BY del arbol doble-cuenta entities, prov_total inflado, full_pct de /completeness erroneo. Stats nacionales (stats.py:37-38): provinces count = 52 (ES) + N (DE) sumados -> el portal muestra p.ej. 68 'provincias' para ES, un numero visiblemente cross-tenant en cuanto se siembra el 2o pais. PT/FR/IT: misma colision sobre codigos numericos solapados; FR-DOM '971' no colisiona con ES (no hay ES '971') pero SI aparece en los COUNT country-blind, inflando los totales ES. Ruido/no-UE: cualquier tenant con un code que coincida numericamente con un code ES sangra; un tenant con codigos disjuntos aun asi infla los COUNT ciegos.
- **Sellado:** Sello = 5 vias. (1) ES golden: con country='ES', cada endpoint devuelve JSON byte-identico al de hoy (invariancia de tenant unico) -- snapshot golden en CI. (2) Aislamiento cross-country golden: sembrar un 2o tenant que comparte code '28'; asertar que /geo/ES/* contiene CERO filas del tenant-2 y que los conteos no cambian respecto al baseline ES-solo (invariante bleed=0; cruza test_country_coexistence bleed=0). (3) Schemathesis property-fuzz con hook de country-bleed: un check custom asserta que toda respuesta con dimension pais trae SOLO ese pais -> cierra el leak mecanicamente en los 18+ endpoints, halla 500s en province_code raro, y pinea el seed que rompe para regresion. (4) Aditividad: oasdiff confirma que enhebrar la dimension pais es additivo (sin breaking change al contrato pan-EU) o que el breaking change es intencional y versionado. (5) Conservacion de conteo: suma de COUNTs por pais == COUNT ciego de hoy en la DB ES-solo (sin doble cuenta).
- **NEXT-LEVEL:** Schemathesis [VERIFIED NEXT-LEVEL.md:828] - MIT [VERIFIED] - EUR0=True - https://github.com/schemathesis/schemathesis. La entrada 'api-schema-fuzz' (825-831): fuzzing property-based (Hypothesis) dirigido por el schema OpenAPI que FastAPI ya expone; genera miles de casos por endpoint auto-detectando 500s, violaciones de contrato y -- con checks stateful + hook de pais -- fuga cross-country; verificacion: 'un check custom asserta que toda respuesta con dimension pais solo trae ese pais (cierra los leaks CRITICAL del verdict mecanicamente)' [VERIFIED:831]. Es LA herramienta que certifica mecanicamente el country-scoping de los lectores: ATACA el comportamiento, no solo la forma. Complementaria: oasdiff (Apache-2.0 [VERIFIED], https://github.com/oasdiff/oasdiff [VERIFIED:836]) gatea que enhebrar la dimension pais queda additivo/country-invariante para el contrato pan-EU [VERIFIED:833-839]. Juntas vuelven 'los lectores estan country-scoped' de afirmacion de code-review a garantia mecanica por-push.

**Deep-spec 360**

##### (a) code_hints verificados al byte
- **[VERIFIED services/api/routers/geo.py:51-73]** /completeness: TODOS los COUNT son country-blind. `SELECT count(*) FROM entity WHERE kind <> 'particular' ...` (:51-62: e_total, e_full, e_no_comarca_city, e_prov_only, e_no_geo) y `SELECT count(*) FROM geo_province|geo_comarca|geo_municipality` (:69-73) sin filtro de country_code. v_total/v_full (:63-67) idem.
- **[VERIFIED services/api/routers/geo.py:369-371]** `SELECT code, name, ccaa_code, ccaa_name FROM geo_province WHERE code=$1` -- lookup por `code` SOLO, sin country_code -> `fetchrow` devuelve una fila arbitraria para code='28'.
- **[VERIFIED services/api/routers/geo.py:374-395]** tree query: `FROM servable_entity e JOIN geo_municipality m ON m.code = e.municipality_code JOIN geo_comarca co ON co.id = m.comarca_id WHERE e.province_code = $1 AND e.comarca_id IS NOT NULL AND e.kind <> 'particular' GROUP BY ...`. El join `m ON m.code = e.municipality_code` (:388) carece de country_code.
- **[VERIFIED services/api/routers/geo.py:414-417]** `SELECT count(*) FROM servable_entity WHERE province_code=$1 AND municipality_code IS NULL AND kind <> 'particular' AND status='active'` -- province_only, country-blind.
- **[VERIFIED services/api/stats.py:37-38]** `"provinces":"SELECT count(*) FROM geo_province"`, `"municipalities":"SELECT count(*) FROM geo_municipality"` -- los stats nacionales SUMAN todos los tenants.

##### Precision ganada de 0052/0053 (corrige el decomp)
- **[VERIFIED migrations/0052_country.sql:52]** `ALTER TABLE geo_comarca ADD COLUMN ... country_code CHAR(2) NOT NULL DEFAULT 'ES'` -- geo_comarca SI gano country_code.
- **[VERIFIED migrations/0053_country_onboarding.sql:39]** comentario: "geo_comarca has no `code` column (PK is `id`...)". El PK de geo_comarca sigue siendo `id` (GENERATED ALWAYS AS IDENTITY, surrogate GLOBAL unico; 0001_geo.sql:12). Por tanto `co.id = m.comarca_id` (:389) une sobre un surrogate globalmente unico -> es SEGURO *siempre que* `m` sea la fila correctamente country-scoped. **El vector de sangrado es el join `m.code = e.municipality_code` (:388) y el lookup `geo_province WHERE code=$1` (:370)**, NO el join de comarca. Una vez `m` esta scoped, `m.comarca_id` ya apunta a la comarca correcta.
- **[VERIFIED 0053:75,84]** geo_province/geo_municipality PK = compuesta (country_code, code); **[VERIFIED 0053:93-154]** las 6 FK hijas son compuestas. El schema YA fuerza identidad compuesta; los lectores del router son la ULTIMA capa country-blind leyendo sobre ella.

##### (b) Mecanismo al atomo
El router es la proyeccion de LECTURA del arbol geo. Cada JOIN/WHERE/COUNT que cruza geo hoy cruza por `code` a secas. Bajo tenant unico (ES) `code` es de facto unico -> resultados correctos. Bajo multi-tenant `code` colisiona (ES-28 vs DE-28) y: `WHERE code=$1` (:370) -> fetchrow devuelve una fila arbitraria (PG elige una de las colisionantes) -> nombre/ccaa de provincia equivocado para el pais servido. `JOIN m ON m.code=e.municipality_code` (:388) -> para una entity con municipality_code='28001' une AMBAS filas '28001' (ES y DE) -> el GROUP BY emite nodos de arbol duplicados/fundidos, prov_total doble-cuenta. Los COUNT (:51-73,:414-417, stats :37-38) -> suman todos los tenants -> numeros nacionales inflados. **El atomo**: el invariante a imponer es "todo cruce geo es sobre (country_code, code), jamas code solo".

##### (e) Sello multi-via: ver campo sealing. (f) Palanca: ver campo tool.

↩ [Índice de sub-proyectos](#indice-sub)

---

<a id="capa-4"></a>

### Capa IV · Identidad servible, sellado, suministro y palancas next-level (F22–F27)

> La puerta G1 que decide servibilidad (Raíz D), el harness que debe ejercer forma extranjera REAL, el certificado de sello 2-vía honesto, el suministro €0 + denominador independiente, y las dos palancas de nivel inalcanzable (point-in-polygon e IA-local con gramática).

<a id="f22"></a>

#### F22 · Validador de identidad G1 generico (complete.py, geo-adyacente)

**Ficha rápida**

- **Costura (ES→genérico):** complete.py:73 _PROVINCE_RE = 01-52 ES, :89 _CDP_CODE_RE = ^CDP-ES-([0-9]{2})-... (prefijo y provincia-2-digit hardcodeados), :83-85 _NATIONAL_KINDS ES [VERIFIED]. El gate check_g1:141-146 decide servibilidad con estos tres asserts ES-clavados. country_of_cdp (paths.py:55-63) ya deriva el CC.
- **Fix:** Tres niveles, no uno: (1) _CDP_CODE_RE -> ^CDP-([A-Z]{2})-([0-9A-Z]{2,})-[base32]$ (ensancha pais Y segmento de provincia, no solo el prefijo); (2) predicado de provincia per-pais desde el perfil/manifest ISO 3166-2 (ES sigue 01-52, DE 01-16, FR incl. 971-976, IT 01-107); (3) _NATIONAL_KINDS per-pais si difiere. Superset estricto: acepta+rechaza ES igual (golden), ademas acepta identidad extranjera correcta.
- **Adversarial:** complete.py:73,89 rechazan DE/IT (provincia >52) y FR-DOM 971 (3-digit) -> entity extranjera correcta jamas servible (bloqueo silencioso de promocion). El golden test_rejects_malformed (test_country_golden.py:294-305 [VERIFIED]) pinea el rechazo de CDP-ES-1- (1-digit) y solo ejerce CDP-FR-75 (2-digit, :292), NUNCA 3-digit: el sello ACTIVAMENTE bloquearia un CDP-FR-971- valido y lo celebraria. El xfail :286-291 solo cubre el prefijo; ensancharlo auto-flipea a XPASS y finge cierre con el [0-9]{2} vivo.
- **Sellado:** _CDP_CODE_RE ensanchado en pais Y provincia (2,+ alfanumerico); predicado de provincia per-pais (no 01-52); _NATIONAL_KINDS per-pais si difiere; golden ES sin regresion. Multi-via: golden ES verde (accepts_all_live_es + rejects_malformed) + golden extranjero REAL con CDP-FR-971- (3-digit) y CDP-DE-16- que DEBEN pasar G1 (y eliminar el xfail :286-291) + cross-check del predicado contra el manifest pycountry (conteo/forma de subdivisiones casa ISO 3166-2).
- **NEXT-LEVEL:** pycountry (ISO 3166-1/-2 + ISO 4217) -- LGPL-2.1, EUR0 -- https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]: el rango 01-52, el ancho y los caps ES-hardcoded (FR 101/IT 107/DE 16/MX 32/JP 47 [VERIFIED NEXT-LEVEL.md:528]) pasan a DATO; el predicado de provincia de G1 se vuelve 'es subdivision ISO 3166-2 real de CC?'. Build-time -> LGPL non-issue [VERIFIED:532]; estricto-permisivo: iso3166 (MIT)+iso-codes JSON. Complemento python-stdnum (check-digits id registral, [VERIFIED:490]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/complete.py:73` `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` -- rango ES 01-52 HARDCODEADO [VERIFIED].
- `pipeline/complete.py:83-85` `_NATIONAL_KINDS = frozenset({"subasta","plataforma","oem_vo_portal","importador"})` -- taxonomia de kinds nacionales ES [VERIFIED].
- `pipeline/complete.py:89` `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` -- prefijo `CDP-ES-` y segmento de provincia `[0-9]{2}` (exactamente 2 digitos) HARDCODEADOS [VERIFIED].
- `pipeline/complete.py:141-146`: `is_national = row.get("kind") in _NATIONAL_KINDS and prov_str is None`; `if not is_national and (prov_str is None or not _PROVINCE_RE.match(prov_str)): return False, ...`; `if not _CDP_CODE_RE.match(cdp_code): return False, ...` [VERIFIED] -- el gate G1 que decide si una entity es servible.
- Golden pin: `tests/test_country_golden.py:286-291` xfail estricto sobre `rx.match("CDP-DE-28-FPB3W1R6")` (pinea el "6th blocker" CDP-ES- no ensanchado) [VERIFIED]; `:292` `assert rx.match("CDP-FR-75-Z8KRFGEA")` (solo 2-digit); `:294-305` `test_rejects_malformed` con `"CDP-ES-1-FPB3W1R6"` (provincia 1-digit) en la lista de rechazo pinneado [VERIFIED:297].

##### (b) Mecanismo al atomo
`check_g1` (`:107-148`) es el GATE de promocion: una entity solo es "servible" si pasa identidad. Tres asserts atomicos: (1) la fila existe; (2) `province_code` en 01-52 O la entity es de un `kind` nacional con provincia NULL; (3) `cdp_code` casa `^CDP-ES-([0-9]{2})-{base32}$`. Cada uno esta clavado a ES: el rango `01-52` es el conteo EXACTO de provincias espanolas; el `^CDP-ES-` fija el pais; el `[0-9]{2}` fija que TODA provincia es de 2 digitos. El atomo letal es el `[0-9]{2}`: aunque se ensanche el prefijo a `CDP-[A-Z]{2}-`, el segmento de provincia SIGUE exigiendo exactamente 2 digitos numericos -> un `CDP-FR-971-` (DOM, 3 digitos) o cualquier provincia >52 (DE Kreis, IT 107) es RECHAZADO como malformado.

##### (c) Costura ES->generico + fix exacto
El fix nombrado por el diseno (CDP-ES -> CDP-[A-Z]{2}) es NECESARIO pero INSUFICIENTE; hay que ir mas profundo en los tres niveles:
1. Regex cdp: `_CDP_CODE_RE = re.compile(r"^CDP-([A-Z]{2})-([0-9A-Z]{2,})-[0-9A-HJKMNP-TV-Z]{8}$")` -- ensancha el pais a `[A-Z]{2}` Y el segmento de provincia de `[0-9]{2}` a `[0-9A-Z]{2,}` (longitud variable, admite alfanumerico).
2. Predicado de provincia: sustituir el `_PROVINCE_RE` 01-52 por un predicado per-pais derivado del perfil (F8) / manifest ISO 3166-2: "es `province_code` una subdivision real del pais CC?". ES sigue siendo 01-52 (golden), DE 01-16, FR incluye '971'-'976', IT 01-107.
3. _NATIONAL_KINDS: si la taxonomia de kinds difiere por pais, leerla del perfil; ES conserva el frozenset actual.
Superset ESTRICTO: el nuevo validador sigue aceptando TODO ES valido y rechazando TODO ES malformado (golden), pero ademas acepta la identidad extranjera correcta. `country_of_cdp` (`paths.py:55-63`) ya existe para derivar el CC.

##### (d) Riesgo adversarial concreto
- Bloqueo de promocion extranjera: `complete.py:73,89` rechazan la identidad de DE/IT (provincia >52), FR-DOM ('971', 3-digit) -> la entity extranjera CORRECTA jamas pasa G1, jamas es servible. El censo del pais #2 se mintea bien (codes.py es parametrico) pero el GATE lo descarta en silencio.
- El sello bloquea ACTIVAMENTE lo valido: `test_country_golden.py:294-305` `test_rejects_malformed` pinea el rechazo de `CDP-ES-1-` (provincia 1-digit) [VERIFIED:297], y el unico caso foraneo que el golden ejerce es `CDP-FR-75` (2-digit, `:292`) -- NUNCA un 3-digit. Es decir: incluso el golden "ensanchado" es CIEGO a la provincia de 3 digitos -> un `CDP-FR-971-` valido seria rechazado y el sello lo CELEBRARIA como correcto.
- xfail enganoso: `:286-291` marca xfail(strict) solo el prefijo `CDP-ES-`; al ensancharlo a `[A-Z]{2}` el test auto-flipea a XPASS y "parece" cerrado, pero el `[0-9]{2}` sigue vivo -> falso cierre.
- PT/no-UE: provincias alfanumericas o de ancho distinto rompen `[0-9]{2}`.

##### (e) Criterio de sellado + verificacion multi-via
SELLADO si y solo si (1) `_CDP_CODE_RE` ensanchado en pais Y en segmento de provincia (2,+ y alfanumerico); (2) predicado de provincia per-pais (no 01-52); (3) `_NATIONAL_KINDS` per-pais si difiere; (4) golden ES SIN regresion (acepta los live ES, rechaza los malformados ES). Multi-via: via A golden ES (`test_accepts_all_live_es_codes` + `test_rejects_malformed` siguen verdes); via B golden extranjero REAL que incluya `CDP-FR-971-` (3-digit) y `CDP-DE-16-` (provincia fuera de la gama ES) -> DEBEN pasar G1, y el xfail de `:286-291` se ELIMINA; via C cross-check del predicado de provincia contra el manifest pycountry (el conteo/forma de subdivisiones por pais casa ISO 3166-2). Eliminar el xfail strict es parte del sello: mientras viva, declara el hueco.

##### (f) Herramienta de elevacion
pycountry (ISO 3166-1/-2 + ISO 4217) -- LGPL-2.1, EUR0 -- https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. Convierte el rango `01-52`, el ancho de codigo y los caps por-pais (que el diseno reconoce ES-hardcoded: "MAX_COMPONENT_SIZE_CAP < 52 = Spain's provinces; FR 101, IT 107, DE 16, MX 32, JP 47" [VERIFIED NEXT-LEVEL.md:528]) en DATO: el conteo y code-width de las subdivisiones de primer nivel de cada pais alimentan un seal manifest per-pais (`geo_unit_width`, `KNOWN_REAL_MAX_*`). El predicado de provincia de G1 pasa de regex ES-shaped a "es una subdivision ISO 3166-2 real de CC?", country-proof y auto-pineante. Uso build/config-time (autoria del manifest, no hot-path) implica que LGPL es non-issue [VERIFIED NEXT-LEVEL.md:532]; alternativa estricta-permisiva: `iso3166` (MIT) + iso-codes JSON crudo. Complemento: python-stdnum (LGPL-2.1, [VERIFIED NEXT-LEVEL.md:490]) para los check-digits del id registral.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f23"></a>

#### F23 · Harness de onboarding/pilot endurecido (fixture forma-extranjera real)

**Ficha rápida**

- **Costura (ES→genérico):** pilot_country.py:76-82 usa forma ES EXACTA (COLLISION_PROVINCE='28', PILOT_MUNI='28001' con left(code,2)=='28' que pasa el CHECK 'regardless' de la relajacion 0053), ccaa 'BB'/'BE' de 2 chars (:112-127). verify() (:242-302) NUNCA lee entity.comarca_id (grep: comarca solo en comentario :52-53, INSERT que lo fija NULL :221, string dry-run :349). test_country_coexistence.py:83-97 replica el fixture ES-shaped; sin test de overflow/3-digit/no-Latino. El 'proof DE byte-identico' es hueco por construccion: con forma ES nunca desborda (F1), nunca colapsa normalizacion (F11), nunca ejerce 3-digit (F22).
- **Fix:** Endurecer el fixture a forma extranjera REAL como puerta obligatoria: (1) muni 8-digit AGS / 6-digit ISTAT/PT + provincia 3-digit DOM-FR que DESBORDE CHAR(5)/CHAR(2) -> rojo hoy, verde tras VARCHAR (F1); (2) nombre no-Latino que ejerza codes._normalize/geo._norm (F11/F10); (3) muni que NO cumple left(code,2)=province_code -> ejercer la rama country_code<>'ES' del CHECK (0053:168) que HOY nunca se ejerce; (4) verify() lee entity.comarca_id y assert no-bleed del comarca ES homonimo (cierra F6); (5) ES byte-identico additivo.
- **Adversarial:** DE (AGS-8): sin fixture 8-digit el sello pasa verde con '28001' y en produccion el primer INSERT AGS revienta 'value too long for type character(5)' a mitad del onboarding (F1). JP/CJK: sin fixture no-Latino el mint (F11) colapsa nombres a clave vacia INMUTABLE en produccion. FR-DOM (971): sin fixture 3-digit, G1 (complete.py:73 _PROVINCE_RE 01-52) rechaza identidad valida y nadie probo la rama (F22). Sangrado comarca (F6): entity DE/MX hereda comarca_id del muni ES homonimo via trigger sin country_code; verify() jamas lee comarca_id -> sangrado cross-pais irreversible PASA el sello.
- **Sellado:** El harness EJERCE forma extranjera real como puerta obligatoria. Multi-via: (1) fixture muni 8-digit + provincia 3-digit + nombre no-Latino: el seed que HOY revienta por ancho/normalizacion debe pasar tras F1/F11 y fallar-rojo mientras no esten; (2) verify() lee entity.comarca_id y assert no-bleed (cierra F6); (3) probar que un muni AGS que no cumple left(code,2)=province_code se acepta bajo country_code<>'ES' (0053:168, rama hoy nunca ejercida); (4) ES byte-identico (counts+diff row-level) con el fixture extranjero presente; (5) pack validado contra Table Schema con ancho declarado ANTES del INSERT.
- **NEXT-LEVEL:** Frictionless Framework (frictionless-py, Table Schema) (MIT) — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Eleva el harness a CONTRATO de datos auto-verificado: declara cada dataset del pack con tipos+regex de forma+ANCHO en bytes per-pais y valida ANTES de cargar una fila; un AGS-8/ISTAT-6/freguesia-6/DOM-FR-3 que no quepa FALLA con mensaje claro en vez de 'value too long' a mitad del seed (el abort que F2 debe revertir). EUR0 pip puro, schema versionado en data/<cc>/geo/pack.schema.json en CI+bootstrap; la migracion 0054 CHAR->VARCHAR(n) toma n del mismo schema. Alternativa generadora de formas adversariales: Hypothesis (MPL-2.0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:38].

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **`scripts/pilot_country.py:76-82`** [VERIFIED]: `COLLISION_PROVINCE = "28"` (comparte code con ES Madrid a proposito), `SECOND_PROVINCE = "11"`, `PILOT_MUNI = "28001"` con comentario literal *"left(code,2) == COLLISION_PROVINCE so the ES-shaped municipality_province_prefix CHECK passes regardless of the 0053 relaxation"*. Forma ES EXACTA (provincia 2-digit, muni 5-digit, prefijo INE).
- **`pilot_country.py:112-127`** [VERIFIED]: `_provinces` devuelve `ccaa_code: "BB"` / `"BE"` (etiquetas sinteticas de 2 chars) + `ccaa_name "Brandenburg"/"Berlin"`. Cubre el NOT NULL CHAR(2) con relleno de 2 chars, no una taxonomia real (cruza con F7).
- **`pilot_country.py:130-135`** [VERIFIED]: `_municipality` -> `code: "28001"`, `province_code: "28"`.
- **`pilot_country.py:242-302`** `verify()` [VERIFIED]: asserta (a) coexistencia province '28' = (ES,Madrid)+(country,...) `:249-260`; (b) FK compuesto del muni resuelve a la province del COUNTRY no ES Madrid `:262-277`; (c) `resolve_cluster` -> canonical=self, members=[code] (no ES bleed) `:279-290`; (d) ES byte-identidad por counts `:292-301`. **NUNCA lee `entity.comarca_id`** — grep confirma: comarca aparece solo en comentario `:52-53`, en el INSERT que lo fija NULL `:221`, y en un string de dry-run `:349`; jamas en un assert de aislamiento cross-pais.
- **`pilot_country.py:305-325`** `revert()` [VERIFIED]: DELETE en orden FK-inverso (entity por `cdp_code LIKE 'CDP-<cc>-%'` `:316-319`, luego municipality `:320`, luego province `:321`), refusa ES `:311-312`.
- **`tests/test_country_coexistence.py:83-97`** [VERIFIED]: fixtures `_DE_PROVINCE_CODE="28"`, `_DE_MUNI_CODE="28001"`, `_DE_CCAA_CODE="BB"`, con comentario *"Municipality '28001' satisfies the ES-shaped prefix CHECK left(code,2)=province_code so the seed is CHECK-clean regardless of whether 0053's CHECK relaxation shipped"* (`:85-87`). Ningun test de overflow/3-digit/no-Latino (grep `:106-470`: solo class TestEsByteIdentity / TestDeMintingDistinctFromEs / TestDbProvinceCoexistence / TestDbEsCountsUnchanged / TestDbPilotRows; el `rollback` de `:366` y `:455` son cleanups deliberados de transaccion, no abort-safety).

##### (b) Mecanismo al atomo
El harness `pilot_country.py` es el contrato de aceptacion reversible de cualquier pais: `dry-run` (sin escritura) -> `seed` (1 transaccion, `:204-239`) -> `verify` (`:242-302`) -> `revert` (`:305-325`). El mecanismo es solido en FORMA: seed atomico, verify con 4 asserts, revert idempotente FK-inverso, `_ensure_ready` que rehusa si 0053 no esta aplicada (F2). El atomo de ROTURA es el FIXTURE: usa codigos de forma ES EXACTA ('28', '28001', ccaa 'BB' de 2 chars). Con forma ES, el seed pasa CHECK-clean "regardless" de la relajacion 0053 (el comentario lo confiesa), el INSERT cabe en CHAR(5)/CHAR(2) (nunca desborda, F1), el nombre es ASCII (nunca colapsa en normalizacion, F11), y la provincia es 2-digit (nunca ejerce el rango 3-digit, F22/G1). Resultado: el "proof DE byte-identico" es HUECO POR CONSTRUCCION — prueba SOLO que la PK compuesta quita la colision, no que el motor sobreviva la forma extranjera REAL. Ademas `verify()` jamas lee `comarca_id`, asi que el sangrado del trigger `entity_set_comarca` (F6, SELECT sin country_code) pasaria el sello sin deteccion.

##### (c) Costura ES -> generico
El harness ES->generico ya es generico en FORMA (todo `country`-parametrizado). La costura abierta es ENDURECER el fixture a forma extranjera REAL como puerta obligatoria:
1. **Muni 8-digit (AGS-DE) / 6-digit (ISTAT-IT, freguesia-PT) / provincia 3-digit (DOM-FR 971)**: el fixture debe sembrar un code que DESBORDE CHAR(5)/CHAR(2) -> el seed REVIENTA hoy con `value too long`, exponiendo F1; tras el fix de ancho (VARCHAR), debe pasar.
2. **Nombre no-Latino (JP 'Yokohama' en kana, EL/cirilico)**: ejercer codes._normalize / geo._norm (F11/F10) -> hoy colapsa a '' -> canonical_key colisionada; el fixture lo expone.
3. **Provincia sin prefijo (AGS no cumple left(code,2)=province_code)**: ejercer la RAMA DE RELAJACION del CHECK `country_code<>'ES'` (0053:168,172) que HOY NUNCA se ejerce (el '28001' ES-shaped pasa el predicado original).
4. **assert comarca_id no-bleed**: `verify()` debe leer `entity.comarca_id` del pilot y assert que NO heredo el comarca ES homonimo (cierra F6).
5. **ES byte-identico se mantiene** (el fixture extranjero es additivo; el corpus ES no se toca).

##### (d) Riesgo adversarial concreto
- **DE (AGS-8)**: sin fixture de 8-digit, el sello pasa verde con '28001'; en produccion el primer INSERT AGS real revienta `value too long for type character(5)` a mitad del onboarding (F1) y nadie lo vio venir -> el "parametrico por pais" no tenia evidencia.
- **JP/CJK (no-Latino)**: sin fixture no-Latino, el mint de identidad (F11) colapsa nombres a clave vacia INMUTABLE en produccion; el sello fue ciego.
- **FR-DOM (971, 3-digit)**: sin fixture 3-digit, G1 (F22, `_PROVINCE_RE 01-52`, complete.py:73) rechaza la identidad valida en produccion y nadie probo la rama.
- **Sangrado de comarca (F6)**: una entity DE/MX hereda el `comarca_id` del municipio ES homonimo via el trigger sin country_code; `verify()` jamas lee comarca_id -> el sangrado cross-pais irreversible PASA el sello.
- **Ruido**: el ccaa 'BB'/'BE' sintetico de 2 chars (`:118-119`) nunca valida una taxonomia de region de 3 chars o ausente (F7) -> otro hueco enmascarado.

##### (e) Criterio de sellado + verificacion multi-via
**Sello = el harness EJERCE forma extranjera real como puerta obligatoria, no forma ES disfrazada.** Multi-via:
1. **Fixture forma-extranjera**: muni 8-digit + provincia 3-digit + nombre no-Latino sembrado y verificado; el seed que HOY revienta por ancho/normalizacion debe pasar tras los fixes F1/F11, y debe FALLAR-ROJO mientras no esten (test que detecta la regresion).
2. **assert comarca_id no-bleed**: `verify()` lee `entity.comarca_id` y assert que no es el comarca ES homonimo (cierra F6); test rojo si el trigger sangra.
3. **Rama de CHECK relajado ejercida**: probar que un muni que NO cumple `left(code,2)=province_code` (AGS) se acepta bajo `country_code<>'ES'` (0053:168) — esa rama HOY nunca se ejerce.
4. **ES byte-identico**: el corpus ES sigue byte-identico (counts + diff row-level) con el fixture extranjero presente.
5. **Via contrato de datos** (ver herramienta): el pack del fixture se valida contra un Table Schema con ancho declarado ANTES del INSERT -> el overflow se atrapa con mensaje claro, no con `value too long` a mitad.

##### (f) Herramienta next-level
**Frictionless Framework (frictionless-py, Table Schema)** (MIT) — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Eleva el harness de "fixture a mano" a CONTRATO de datos auto-verificado (`NEXT-LEVEL.md:334-340`): declarar cada dataset del pack (backbone, centroides, gazetteer/CP, alias) como Table Schema con tipos, regex de forma de codigo y —keystone— el ANCHO en bytes per-pais, y validar el pack ANTES de cargar una sola fila. Un AGS-DE de 8 / ISTAT-IT de 6 / freguesia-PT de 6 / DOM-FR de 3 que no quepa FALLA la validacion con mensaje claro en vez de reventar con `value too long for type character(5)` a mitad del seed dejando datos parciales (que es justo el abort que F2 debe poder revertir). Aplica la doctrina COUNTRY-PROOF ("no documentar la regla — que la maquina la imponga y la pruebe sola") a la INGESTA. Ruta EUR0: pip puro; el schema es YAML/JSON versionado en `data/<cc>/geo/pack.schema.json`, corre en CI y bootstrap. Verificacion (`NEXT-LEVEL.md:340`): golden de pack-malo (codigo que excede ancho / no-numerico donde el predicado exige numerico / centroide fuera de bbox) DEBE fallar; el ancho declarado se cruza contra `max(length(code))` real; el schema del pack ES produce el INSERT actual byte-identico; la futura migracion 0054 CHAR->VARCHAR(n) toma `n` del mismo schema (una sola fuente de verdad del ancho). Alternativa para generar formas adversariales automaticamente: **Hypothesis** (MPL-2.0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:38] (property-based, mina el caso de la longitud/forma que rompe).

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f24"></a>

#### F24 · Certificado de sellado geo (2-via ortogonal + intervalo con CI)

**Ficha rápida**

- **Costura (ES→genérico):** La 2-via del backbone es COUNTRY-BLIND: `load_geo.py:94-97` une `geo_municipality m LEFT JOIN geo_province p ON p.code = m.province_code` SIN country_code, y `nprov/nmuni/covered` (:90-91,98) cuentan todos los paises [VERIFIED]. Tras 0052/0053 `code` ya no es unico -> un muni del pais #2 "no es orphan" por casar una provincia ES homonima y los totales se inflan: el denominador que certifica el backbone se auto-engana cross-pais. Ademas el aparato de sello (`/geo/seal` v_province_seal [VERIFIED geo.py:92-144], `/geo/exhaustiveness` v_exhaustiveness_seal con coverage_lower+CI+sealed [VERIFIED geo.py:147-221], doctrina cota-inferior [VERIFIED 0048:12-13]) es honesto en forma pero CIEGO a las roturas reales: ningun fixture ejercita ancho (F1), normalizacion no-Latina (F11), provincia 3-digit (F3) ni sangrado comarca (F6), y depende de un denominador nacional libre que para no-ES puede no existir (F25).
- **Fix:** (1) Country-scopear la 2-via: anadir `AND p.country_code = m.country_code` al join de orphans (load_geo.py:96) y `WHERE country_code=$cc` a los cuatro count (mismo patron ya correcto en test_country_coexistence.py:493); ES byte-identico con un solo tenant. (2) Declarar los criterios de sello como EXPECTATIVAS ejecutables fail-closed: `ancho_ok(cc)`, `resolver_no_empty_keys(cc)`, `province_wellformed(cc)`, `comarca_bleed(cc)==0`, `es_byte_identico`, ademas de `coverage_lower>=threshold` con CI real — cada una versionada por pack y bloqueante del build (Great Expectations/Pandera). (3) Degradar a cota inferior honesta cuando falta denominador nacional libre, soportando MULTIPLES anclas (Eurostat SBS/GLEIF/oficina nacional) con desacuerdo como senal de distrust, nunca promedio silencioso ni 100% fabricado. (4) Atestar el build con in-toto para que el certificado sea re-verificable por terceros. Default ES: scopear por country_code no cambia ningun numero con un tenant.
- **Adversarial:** Denominador cross-pais: load_geo.py:90-98 country-blind -> al sembrar el pais #2 `nprov/nmuni/covered` se inflan y `orphans` baja (munis no-ES casan provincias ES homonimas) -> el backbone aparenta mas completo; el sello miente al alza. DE/IT/PT/FR sin ancla nacional libre fiable: sin denominador ortogonal `coverage_lower` no se certifica -> debe degradar a cota baja; reutilizar el threshold ES sella en falso. Roturas invisibles: una entidad mal-mintada (F11), rechazada por provincia 3-digit (F3) o arrastrada por sangrado comarca (F6) NO mueve ningun numero del sello -> certificado verde sobre censo corrupto. Estrato K<3 (DE/IT/PT con GEO+OEM): el MSE degenera a observed-only y casi nada sella sin SparseMSE/dga. No-UE: censo no reutilizable obliga triangulacion multi-ancla; una sola ancla sesgada mueve el denominador sin contraste.
- **Sellado:** Sellado del certificado, por pais, cuando: (1) backbone 2-via country-scoped (orphans=0, provinces_covered=N); (2) coverage_lower>=seal_threshold con CI real (no point); (3) criterios ejecutables (ancho, normalizacion no-vacia, provincia bien-formada, comarca_bleed=0, ES-byte-identico) TODOS verde y persistidos; (4) sealed=true solo entonces, jamas 100% fabricado. Multi-via: (1) backbone 2-via independiente del loader + denominador nacional independiente (DIRCE/Eurostat/GLEIF) en banda 0.7-1.4; (2) ortogonal resolver⟂geocoder concuerdan en muestra, divergencia=hueco; (3) round-trip code->name->code; (4) no-sangrado bleed=0 por pais (test_country_coexistence.py:489-495); (5) honestidad del intervalo — estrato delgado da coverage_lower~0/sealed=false (geo.py:159-160), fijar denominador conocido mantiene sellados los ya sellados y solo anade nuevos (monotonia, cero regresion); (6) fail-closed — inyectar una rotura (ancho extranjero, nombre no-Latino, provincia 3-digit) hace FALLAR la expectativa pre-sello, prueba mecanica de que el sello ya no es ciego.
- **NEXT-LEVEL:** in-toto — Apache-2.0 — https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:140-146]: atesta el build de sello ligando {git SHA, content-hashes de inputs} -> {coverage_lower, CI, n_hat}, firmado en transparency log (rekor) -> certificado no-repudiable, re-verificable por terceros (re-correr da coverage_lower byte-identico; alterar 1 fila del census hace fallar la atestacion); CNCF-graduado, €0. Stack de apoyo: Great Expectations/Pandera — Apache-2.0 — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:164-170] hace los criterios de sello expectativas fail-closed versionadas por pack; SparseMSE/dga — GPL(>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:116-130] cierran el coverage_lower con CI en estratos K<3 (DE/IT/PT de listas delgadas) via el bridge Rscript existente; Uber H3 — Apache-2.0 — https://github.com/uber/h3 [VERIFIED NEXT-LEVEL.md:358-364] da estratos de area-igual que endurecen la cota inferior. Todas €0.

**Deep-spec 360**

##### (a) Verificacion de code_hints [leido a fuente]
- **[VERIFIED services/api/routers/geo.py:92-144]** endpoint `/geo/seal` -> sirve `v_province_seal` (migrations 0042+0043): por provincia x segmento, VENTA = `served_canonical / DIRCE-451` (SELLADO>=85% / PARCIAL 50-85% / GAP<50%, :108), DESGUACE = `found / DGT census` (:109). Es el sello REGISTRAL (techo externo).
- **[VERIFIED services/api/routers/geo.py:147-221]** endpoint `/geo/exhaustiveness` -> sirve `v_exhaustiveness_seal`: "National coverage CERTIFICATE — capture-recapture / MSE" (:153). Devuelve `k_lists, n_obs, n_hat, ci_low, ci_high, coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, build_run_id` (:169-172). DOCTRINA explicita :159-160 "Honest by construction — a thin stratum reports coverage_lower near 0 and sealed=false, never a fabricated 100%". La fila grand-national (segment Y province NULL) es el certificado titular (:202-203).
- **[VERIFIED migrations/0048_discovery_capture.sql:12-13]** "Sealing doctrine: coverage is certified with the LOWER bound of the CI (coverage_lower = n_obs / ci_high). The point estimate is never used to seal." Tablas: `discovery_list` (taxonomia + `orthogonality_class`, :22-28 — keys de la misma clase NO son independientes, :19-20), `discovery_capture` (matriz `(resolved_ulid,list_key,build_run_id)` con `province_code`/`segment` como estratos, :36-44), `exhaustiveness_estimate` (`coverage_lower` :66, `sealed boolean` :70, `external_ref` triangulacion :71, :55-74).
- **[VERIFIED scripts/load_geo.py:90-100]** verificacion 2-via del backbone: `nprov`/`nmuni` (:90-91), `orphans` via `LEFT JOIN geo_province p ON p.code = m.province_code WHERE p.code IS NULL` (:94-97), `covered = count(DISTINCT province_code)` (:98).
- **[VERIFIED tests/test_country_coexistence.py:489-495]** assert de no-sangrado: un muni DE unido a provincia via FK compuesta `ON p.country_code=m.country_code AND p.code=m.province_code WHERE m.country_code='DE' AND p.country_code <> 'DE'` debe dar `bleed == 0`.

CONCLUSION: el aparato de sello YA es honesto en doctrina (cota inferior, sealed=false en estrato delgado, nunca 100% fabricado) y YA tiene 2 ejes (registral DIRCE/DGT + MSE capture-recapture). PERO la 2-via del backbone (load_geo.py:94-97) es COUNTRY-BLIND y ningun fixture ejercita las roturas reales (ancho/normalizacion/3-digit/sangrado): el sello es CIEGO a ellas.

##### (b) Mecanismo al atomo
El sello geo es un INTERVALO certificado compuesto por estratos. Atomos:
1. **Captura estratificada** (0048): cada `resolved_ulid` visto por una lista ortogonal (`list_key`) genera una fila en `discovery_capture`, estratificada por `(province_code, segment)`. Listas de la misma `orthogonality_class` colapsan a una (no independientes).
2. **Estimacion MSE por estrato** -> `n_hat` + `[ci_low, ci_high]`; `coverage_lower = n_obs / ci_high` (la cota CONSERVADORA, 0048:13/66). `sealed = coverage_lower >= seal_threshold` (0048:70).
3. **Roll-up nacional**: la fila (province NULL, segment NULL) suma estratos a un certificado titular con `build_run_id` (provenance re-ejecutable, geo.py:158-159).
4. **2-via ortogonal**: el sello textual (resolver) y el espacial (geocoder) son ejes que deben CONCORDAR; el round-trip `code->name->code` cierra el lazo; el backbone se contrasta contra un denominador nacional INDEPENDIENTE del loader (load_geo.py:94-98 + DIRCE/DGT).
5. **Honestidad estadistica**: un estrato fino reporta `coverage_lower` cerca de 0 y `sealed=false`; jamas se emite 100% entero.
El "100% geo" NO es un booleano: es el conjunto {backbone-completo, centroides>=umbral, FK-integridad=0-orphans, resolver-golden, ES-byte-identico, coverage_lower>=threshold con CI} verde, persistido y cableado a CI.

##### (c) Costura ES->generico + fix exacto
**Costura 1 (denominador 2-via country-blind)**: `load_geo.py:94-97` une `geo_municipality m LEFT JOIN geo_province p ON p.code = m.province_code` SIN `country_code`; tras 0052/0053 `code` ya no es unico -> un muni del pais #2 puede "no ser orphan" por casar con una provincia ES homonima, y `covered`/`nprov`/`nmuni` (:90-91,98) suman TODOS los paises. La 2-via que certifica el backbone se auto-engana cross-pais.
**Fix 1**: anadir `AND p.country_code = m.country_code` al join de orphans y `WHERE country_code = $cc` a los cuatro `count`. Para ES (unico tenant hoy) el resultado es byte-identico; para el pais #2 es la diferencia entre verdad y mezcla. (Es el mismo patron ya probado correcto en test_country_coexistence.py:493 `ON p.country_code=m.country_code AND p.code=m.province_code`.)
**Costura 2 (sello ciego a las roturas)**: ningun fixture ejercita ancho (F1), normalizacion no-Latina (F10/F11), provincia 3-digit (F3), ni sangrado del trigger comarca (F6); el "proof DE byte-identico" es hueco por construccion (cruza F23).
**Fix 2**: el certificado debe declarar como CRITERIOS DE SELLO ejecutables (no prosa): `assert ancho_ok(cc)`, `assert resolver_no_empty_keys(cc)`, `assert province_wellformed(cc)`, `assert comarca_bleed(cc)==0`, ademas de `coverage_lower>=threshold`. Cada criterio = una expectativa versionada que FALLA CERRADO el build del sello (ver tool).
**Costura 3 (denominador nacional puede no existir libre)**: el sello depende de un denominador nacional fiable y €0 (DIRCE para ES); para otros paises puede no existir (cruza F25).
**Fix 3**: el sello DEGRADA a cota inferior honesta cuando falta denominador (no declara 100%), y soporta MULTIPLES anclas (Eurostat SBS / GLEIF / oficina nacional) con desacuerdo como senal de distrust, no promedio.
**Default ES = numeros actuales**: scopear por `country_code='ES'` no cambia ningun conteo con un solo tenant.

##### (d) Riesgo adversarial concreto
- **Cross-pais en el denominador**: `load_geo.py:90-98` country-blind -> al sembrar el pais #2, `nprov`/`nmuni`/`covered` se INFLAN y `orphans` baja artificialmente (munis no-ES "casan" provincias ES homonimas) -> el backbone aparenta mas completo de lo que es; el sello miente al alza.
- **DE/IT/PT/FR sin denominador libre fiable**: GeoNames/OSM varian por pais; sin un ancla nacional ortogonal, `coverage_lower` no se puede certificar -> el sello DEBE degradar a cota baja honesta; si en su lugar reutiliza el threshold ES, sella en falso.
- **Roturas invisibles**: una entidad extranjera mal-mintada por normalizacion (F11) o rechazada por provincia 3-digit (F3) o arrastrada por el sangrado comarca (F6) NO mueve ningun numero del sello actual -> el certificado pasa verde sobre un censo corrupto.
- **Estrato fino gamed**: si un pais tiene listas infra-pobladas (K<3), el MSE degenera; sin SparseMSE/dga el `coverage_lower` cae a observed-only y casi nada sella — el riesgo es declarar "no sellable" cuando un estimador robusto SI cerraria, o peor, forzar `confidence` alto sin base.
- **Ruido (no-UE)**: un pais cuyo censo oficial no es libre ni reutilizable obliga a triangulacion multi-ancla; una sola ancla sesgada moveria el denominador sin contraste.

##### (e) Criterio de sellado + verificacion multi-via
**Sellado del CERTIFICADO** cuando, por pais: (1) backbone 2-via country-scoped (orphans=0, provinces_covered=N esperado) ; (2) `coverage_lower >= seal_threshold` con CI real (no point); (3) los criterios ejecutables (ancho, normalizacion no-vacia, provincia bien-formada, comarca_bleed=0, ES-byte-identico) TODOS verde y persistidos; (4) `sealed=true` SOLO si todo lo anterior; jamas 100% fabricado.
**Multi-via** (la doctrina del propio stage):
- *Via 1 (2-via backbone independiente del loader)*: `load_geo.py` country-scoped da orphans=0/covered=N; un denominador nacional INDEPENDIENTE (DIRCE/Eurostat/GLEIF) aterriza N en banda 0.7-1.4 — el loader nunca se auto-valida.
- *Via 2 (ortogonal resolver ⟂ geocoder)*: para una muestra, el muni por texto (resolver) y por geometria (geocoder/PIP) CONCUERDAN; divergencia = hueco confesado.
- *Via 3 (round-trip)*: `code -> name -> code` reproduce el code de origen para todo muni sellado.
- *Via 4 (no-sangrado)*: `test_country_coexistence.py:489-495` bleed=0 por pais (FK compuesta); ningun muni del pais #2 resuelve a provincia de otro.
- *Via 5 (honestidad del intervalo)*: un estrato sintetico delgado reporta `coverage_lower~0` y `sealed=false` (geo.py:159-160); fijar un denominador conocido MANTIENE sellados los ya sellados y solo ANADE los nuevos (monotonia, cero regresion).
- *Via 6 (criterios ejecutables fail-closed)*: inyectar una rotura (muni de ancho extranjero, nombre no-Latino que colapsa, provincia 3-digit) -> la expectativa pre-sello FALLA el build (prueba mecanica de que el sello YA NO es ciego).

##### (f) Herramienta NEXT-LEVEL [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md]
- **in-toto** (atestacion de provenance del build de sello) — Apache-2.0 — https://github.com/in-toto/in-toto — [VERIFIED NEXT-LEVEL.md:140-146]. Eleva el sello de AFIRMACION a CERTIFICADO no-repudiable: liga `{git SHA, content-hashes de TODO input (census CSV, matriz de captura, membresias de lista, versiones de estimador)} -> {coverage_lower, CI, n_hat por estrato}`, firmado y anexado a un transparency log (Sigstore/rekor). Cualquier tercero PRUEBA "este 80,5% salio de estos inputs y este codigo" sin confiar en nosotros; in-toto graduo en CNCF (2025-02-10), estandar industrial de provenance. €0 (firma keyless OIDC o clave local; rekor public-good o self-host). Verificacion: re-correr desde los hashes -> `coverage_lower` byte-identico; alterar 1 fila del census -> la atestacion FALLA.
- **Great Expectations / Pandera** (contrato de datos PRE-sello) — Apache-2.0 — https://github.com/great-expectations/great_expectations — [VERIFIED NEXT-LEVEL.md:164-170]. Convierte los criterios de sello (backbone-completo, centroides>=umbral, FK-integridad, ES-byte-identico, ningun `source_key` cae en silencio a otra clase) en EXPECTATIVAS ejecutables, versionadas por country-pack, que FALLAN CERRADO el build — el "estrato falla cerrado, no abierto". Hace mecanico el COUNTRY-PROOF-INVARIANT. €0, Python puro, en CI y pre-seal.
- **SparseMSE / dga** (estimador robusto + Bayesian model averaging) — GPL(>=2) — https://cran.r-project.org/package=SparseMSE — [VERIFIED NEXT-LEVEL.md:116-122 y :124-130]. Cierran la honestidad del `coverage_lower` CON CI donde las listas tienen poco/cero solapamiento (el fallo no-ES exacto marcado CRITICAL: DE/IT/PT con solo GEO+OEM => K<3): SparseMSE recupera intervalo finito donde el log-lineal degenera; dga promedia modelos para que la cota no dependa de UN modelo BIC. Corren bajo el bridge Rscript ya existente; degradan graceful si R ausente. €0.
- **Uber H3 (h3-py)** — Apache-2.0 — https://github.com/uber/h3 — [VERIFIED NEXT-LEVEL.md:358-364]. Da estratos de area-igual para el MSE: `coverage_lower` se calcula sobre celdas comparables en vez de municipios de tamano dispar, ENDURECIENDO la cota inferior honesta del certificado (un municipio rural enorme vs uno urbano diminuto ya no sesgan). €0, precomputado una vez por pais. (Palanca de hardening, no bloqueante de sello.)

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f25"></a>

#### F25 · Suministro de datos geo EUR0 + denominador nacional de 2a via

**Ficha rápida**

- **Costura (ES→genérico):** El suministro ES son 3 fuentes ES-soldadas: xlsx INE (load_geo.py:6), CSV ine-places (seed_geo_centroides.py:3, quirk lon/lat :54-55), Overture bbox-ES+filtro '!=ES' (overture.py:35,:224). La 2-via del loader (load_geo.py:94-100) se auto-valida (orphans/covered de la misma data). Pasar a manifiesto de pack por pais data/<cc>/geo/SOURCE.md con provenance+licencia, MAS un denominador nacional independiente.
- **Fix:** Manifiesto ES apunta a INE/ine-places/Overture existentes -> byte-identico. Bbox (:35) y filtro de pais (:224) parametrizados por country_code del pack. Rutas EUR0: GeoNames CC-BY (admin1/2+LAU+alternateNames+centroides en UNA fuente), OSM/Overture ODbL/CC-BY (poligonos). Tags de provenance [MEDIDO]/[ESTIMADO-DECLARADO] por dataset.
- **Adversarial:** Cobertura GeoNames/OSM desigual por pais -> backbone incompleto sin que el loader lo note. Bbox ES (:35) sobre-captura S Portugal/S France; filtro '!=ES' (:224) hardcodeado -> pack generico sin filtro parametrico mete vecinos. Denominador nacional libre+fiable puede no existir -> el sello degrada a cota honesta (cruza F24), nunca 100% sin denominador. Quirk lon/lat ES (seed:54-55) no universal -> invierte otras fuentes (cruza F18).
- **Sellado:** (1) SOURCE.md por pais con licencia+provenance, impuesto por contrato de unit tests (espejo triangulacion existente). (2) 2-via: conteo por nivel del backbone vs ancla nacional INDEPENDIENTE (Eurostat SBS G45 / oficina nacional / GLEIF-LEI) en banda 0.7-1.4 o marcado. (3) Panel de anclas (no una): desacuerdo = distrust, no promedio silencioso [VERIFIED NEXT-LEVEL.md:189-194]. (4) Licencia limpia CC0/CC-BY/ODbL/free-reuse, sin GPL, en CI. (5) ES byte-identico.
- **NEXT-LEVEL:** Suministro: GeoNames dump — CC-BY 4.0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377]. Denominador 2a via: Eurostat SBS NACE G45 — free-reuse (Dec. 2011/833/EU) — https://ec.europa.eu/eurostat/web/structural-business-statistics [VERIFIED NEXT-LEVEL.md:191]. Ancla registral: GLEIF LEI Golden Copy — CC0 1.0 — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175]. 3er denominador por area: geoBoundaries CGAZ — CC-BY 4.0/ODbL — https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353,356].

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **[VERIFIED scripts/load_geo.py:4-6]** la fuente del backbone ES es el xlsx INE: `https://www.ine.es/daco/daco42/codmun/diccionario25.xlsx` (:6), referenciado por `XLSX = ... "diccionario_ine.xlsx"` (:23). URL ES-soldada.
- **[VERIFIED scripts/seed_geo_centroides.py:1-7]** la fuente de centroides es `PopulateTools/ine-places` (docstring :2-4, 'MIT-compatible, derived from official INE data'); el quirk lon/lat en :49-56.
- **[VERIFIED pipeline/sources/overture.py]** `_BBOX` Espana en :35 (`xmin:-18.3 ... ymax:44.0`, incl. Canarias/Ceuta/Melilla); comentario 'Over-capture (S Portugal, S France) is harmless' :33-34; filtro pais `if country and country != "ES": continue  # keep only Spain` :222-224; docstring de clase 'across Spain' :119.
- **2-via que se auto-valida** [VERIFIED load_geo.py:94-100]: `orphans` y `provinces_covered` se computan de la MISMA data cargada (:94-98) -> no hay denominador nacional independiente.

##### (b) El mecanismo al atomo
1. El suministro ES vivo son **3 fuentes ES-especificas**: (i) xlsx INE (backbone codes+names, load_geo.py:6), (ii) CSV ine-places (centroides con quirk lon/lat, seed_geo_centroides.py:3), (iii) Overture bbox-ES (POIs, overture.py:35).
2. Las tres estan SOLDADAS a ES: URL INE, gem ine-places, bbox de Espana + filtro `!= "ES"` (:224).
3. La verificacion 2-via del loader (load_geo.py:94-100) mide `orphans`/`provinces_covered` sobre la propia data -> **se auto-valida**; no hay un denominador nacional ortogonal que confirme que el backbone esta completo.

##### (c) La costura ES->generico con su fix exacto
- **Costura**: para cada pais objetivo, encontrar+verificar+aterrizar en `data/<cc>/geo/` el backbone (niveles+codigos oficiales), centroides, gazetteer/CP y alternateNames por via gratuita, MAS un **denominador nacional independiente** para que la 2-via no se auto-valide.
- **Fix exacto**: el suministro pasa a ser un **manifiesto de pack por pais** `data/<cc>/geo/SOURCE.md` + datasets, con tags de provenance `[MEDIDO]` / `[ESTIMADO-DECLARADO]` y licencia por dataset. El manifiesto ES apunta a las fuentes INE/ine-places/Overture existentes -> byte-identico. El bbox de Overture (:35) y el filtro de pais (:224) se parametrizan por `country_code` del pack.
- **Rutas EUR0**: GeoNames CC-BY (admin1/2 + LAU/municipios + alternateNames + centroides en UNA fuente); OSM/Overture ODbL/CC-BY (poligonos/bbox).

##### (d) El riesgo adversarial concreto
- **Cobertura desigual**: la calidad/cobertura de GeoNames/OSM varia por pais (denso en DE/FR, ralo en algun no-UE) -> el backbone de un pais puede salir incompleto sin que el loader lo note.
- **Bbox sobre-captura**: el `_BBOX` ES (:35) es per-pais y sobre-captura vecinos (S Portugal, S France); el filtro `!= "ES"` (:224) esta hardcodeado -> un pack generico sin filtro parametrico mete POIs de paises vecinos en el censo.
- **Denominador inexistente**: un denominador nacional libre y fiable puede no existir para todo pais -> el sello DEBE degradar a cota inferior honesta (cruza F24), nunca declarar 100% sin denominador.
- **Quirk no universal**: el swap lon/lat de la fuente ES (seed_geo_centroides.py:54-55) NO es universal; copiarlo a otra fuente invierte coordenadas (cruza F18).

##### (e) Criterio de sellado + verificacion multi-via
1. **SOURCE.md por pais** con licencia + tag de provenance, impuesto por un contrato de unit tests (espejo del contrato de triangulacion ya existente en el stage de exhaustividad).
2. **2-via denominador**: el conteo por nivel del backbone vs un ancla nacional INDEPENDIENTE (Eurostat SBS NACE G45 establecimientos / oficina estadistica nacional / conteo GLEIF-LEI) aterriza `N_hat` en banda **0.7-1.4** o se marca.
3. **Panel de anclas (no UNA)** [VERIFIED NEXT-LEVEL.md:189-194]: el DESACUERDO entre anclas aflora como senal de distrust, no se promedia en silencio.
4. **Licencia limpia**: cada dataset CC0/CC-BY/ODbL/free-reuse, sin contaminacion GPL, aserado en CI.
5. **ES byte-identico**: el manifiesto ES reproduce el INSERT/seed actual sin drift.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **Suministro primario**: **GeoNames dump** — CC-BY 4.0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377] (backbone + codigos + centroides + alternateNames en UNA fuente gratis pan-pais).
- **Denominador nacional (la 2a via ortogonal)**: **Eurostat Structural Business Statistics (SBS, NACE G45** venta/reparacion de vehiculos) — Reutilizacion libre (Decision 2011/833/EU; atribucion) — https://ec.europa.eu/eurostat/web/structural-business-statistics [VERIFIED NEXT-LEVEL.md:191]. Mecanismo fiscal/estadistico INDEPENDIENTE del backbone.
- **Ancla registral complementaria**: **GLEIF LEI Golden Copy** — CC0 1.0 — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175] (descarga diaria, sin atribucion, da una pata registral dia-uno a CUALQUIER pais).
- **Tercer denominador por area**: conteo de poligonos por nivel de **geoBoundaries CGAZ** — CC-BY 4.0 / ODbL — https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353] como denominador nacional independiente del loader [VERIFIED NEXT-LEVEL.md:356 verificacion #3]. Tres mecanismos distintos (estadistico/registral/geometrico) convierten 'confia en el conteo' en 'el denominador se contrasta por N mecanismos'; el desacuerdo es senal, no ruido.

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f26"></a>

#### F26 · [Next-level] Reverse-geocode por point-in-polygon (elimina la heuristica KNN)

**Ficha rápida**

- **Costura (ES→genérico):** geocode.py:49 KNN_MAX_DISTANCE_KM=30.0 constante global ES (rationale Lorca/Caceres :16-22); nearest_municipality :154-194 = argmin equirectangular + haversine + umbral (:191) a reemplazar. overture.py existe pero para theme=places (POIs PUNTUALES, ST_X/ST_Y :180-186); la PIP necesita theme=divisions (POLIGONOS) NO ingerido — solo el plumbing S3/DuckDB/hive (:87-145) es reutilizable.
- **Fix:** (1) adaptador de poligonos nuevo sobre el patron overture.py (theme=divisions / geoBoundaries / GISCO LAU), scoped (country_code,code), ST_MakeValid en ingesta; (2) migracion additiva geo_municipality.geom geometry(MultiPolygon,4326) + GIST; (3) geocode_pip(lat,lon,country_code)=SELECT code WHERE country_code=$1 AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(lon,lat),4326)); (4) fallback KNN+p99 per-pais (F16) solo sin poligono. ES byte-identico (code_PIP==code_KNN en muestra). Next-level: NO bloquea el sello.
- **Adversarial:** 30 km global sobre-rechaza en municipios grandes (Nordicos/MX/JP rural) y sobre-acepta en urbano denso; KNN country-blind funde ES-28 y DE/MX-28; frontera ES/PT resuelve bien solo con poligonos scoped por country_code (bleed=0); poligonos OSM/Overture incompletos en rural no-UE → PIP None donde el centroide acertaba (degradar a fallback, no inventar); self-intersections → ST_Contains ambiguo, exige ST_MakeValid.
- **Sellado:** (lever no bloqueante) 2-via ST_Contains(centroide)==code de la fila; round-trip centroide-en-poligono (ST_Contains=true); denominador independiente conteo-poligonos vs INE/nacional; cross-pais frontera ES/PT bleed=0; cobertura como INTERVALO (huerfanos confesados, nunca 100%). Sello del lever = 'documentado como diferido con caso de uso probado'.
- **NEXT-LEVEL:** PostGIS (ST_Contains+GiST) sobre geoBoundaries CGAZ — contencion exacta, elimina el umbral 30 km. geoBoundaries CC-BY 4.0/ODbL (datos); PostGIS GPL-2.0 (servicio, no se embebe). https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353]. Alternativas: Overture Divisions (ODbL), OSM via PgOSM Flex (MIT), Eurostat GISCO LAU/NUTS. Aceleradores: Uber H3 (Apache-2.0, https://github.com/uber/h3 [VERIFIED:361]) reverse-geocode O(1)+estratos MSE; auto-calibracion p99 PostGIS ST_MaximumInscribedCircle+GeoPandas/Shapely (BSD-3, [VERIFIED:369], habilita F16); DuckDB spatial (MIT [VERIFIED:409]).

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- **pipeline/geocode.py:49** [VERIFIED] `KNN_MAX_DISTANCE_KM: float = 30.0` — constante GLOBAL, sin parametrizar por pais.
- **pipeline/geocode.py:16-22** [VERIFIED] rationale del umbral: Lorca ~1676 km²/radio ~23 km, Caceres ~1750 km²/radio ~24 km, margen 30 km para Soria/Cuenca rural. 100% calibrado al tamaño municipal **ES**.
- **pipeline/geocode.py:154-194** [VERIFIED] `nearest_municipality`: argmin equirectangular (182-187) + haversine exacto al ganador (190) + `if dist_km > KNN_MAX_DISTANCE_KM: return (None, dist_km)` (191). ESTE es el KNN-centroide + umbral a reemplazar.
- **pipeline/sources/overture.py:33-35** [VERIFIED] `_BBOX` = Spain (incl. Canarias/Ceuta/Melilla); el comentario 33-34 reconoce over-capture S Portugal/S France "harmless … dropped at INE geo-resolution".
- **pipeline/sources/overture.py:110** [VERIFIED] `theme=places/type=place`: el adaptador existente consulta **POIs (places)**, no fronteras.
- **pipeline/sources/overture.py:180-186** [VERIFIED] campos: `ST_X/ST_Y(geometry)` = **PUNTO**, `addresses[1].region/locality/postcode/country`.

**Honestidad cruda — matiz del enunciado:** la facet dice "adaptador overture ya existe". EXACTO pero parcial: existe `overture.py` para `theme=places` (POIs PUNTUALES). La PIP necesita `theme=divisions` (fronteras administrativas = POLIGONOS), que NO se ingiere hoy. Lo REUTILIZABLE es el *plumbing* (bucket anonimo S3, `INSTALL spatial; LOAD spatial`, httpfs, hive-partition pushdown, resolucion de release :87-145), NO la query de places. El adaptador de poligonos es pieza NUEVA sobre ese patron probado.

##### (b) Mecanismo al atomo
Hoy reverse-geocode = KNN sobre centroides lat/lon en `geo_municipality`, scopeado por `province_code`, con umbral heuristico 30 km. El punto se asigna al centroide mas cercano dentro de la provincia; si dista >30 km → None (hueco). **PIP** lo sustituye: ingestar poligonos de frontera municipal, indexar GIST, resolver lat/lon→municipio con `ST_Contains` (el punto cae en exactamente un poligono, o en ninguno→hueco confesado, doctrina intacta). Elimina el umbral (no hay constante que calibrar) y da **contencion exacta**, base para auto-calibrar el p99 (F16) y sellar cobertura por area real, no por centroide.

##### (c) Costura ES→generico + fix exacto
1. **Adaptador de poligonos NUEVO** sobre el patron `overture.py`: `theme=divisions` (Overture) / geoBoundaries CGAZ / Eurostat GISCO LAU, scopeado por `country_code`, poligonos etiquetados `(country_code, code)`, con `ST_MakeValid` en ingesta.
2. **Migracion additiva**: `ALTER TABLE geo_municipality ADD COLUMN geom geometry(MultiPolygon,4326)` + indice GIST.
3. **Resolver**: `geocode_pip(lat,lon,country_code)` = `SELECT code FROM geo_municipality WHERE country_code=$1 AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(lon,lat),4326))`, sustituyendo/aumentando `MunicipalityGeocoder.nearest_municipality`.
4. **Fallback** al KNN+centroide solo donde falte poligono, con el umbral p99 per-pais (F16). ES byte-identico: para ES `code_PIP == code_KNN` en la muestra (2-via). **Marcado next-level**: NO bloquea el sello, es mejora de exactitud.

##### (d) Riesgo adversarial concreto
- **Municipios grandes/irregulares** (Nordicos, **MX/JP** rural): el 30 km global sobre-rechaza geocodificaciones validas → huecos falsos masivos; en zonas densas (urbano) sobre-acepta cruzando municipio.
- **KNN country-blind** (F15): funde ES-28 y DE/MX-28; un punto MX en provincia '15' resuelve a A Coruña ES.
- **Frontera ES/PT**: un punto en la raya resuelve al pais correcto SOLO si los poligonos estan scopeados por `country_code` (bleed=0).
- **Cobertura de poligonos**: OSM/Overture incompletos en zonas rurales no-UE → PIP devuelve None donde el centroide acertaba; degradar a fallback, no inventar.
- **Ruido geometrico**: poligonos solapados / self-intersections → `ST_Contains` ambiguo o falla; exige `ST_MakeValid` + assert de no-solape intra-pais.

##### (e) Criterio de sellado + verificacion multi-via (lever next-level, NO bloqueante)
1. **2-via ortogonal**: para muestra, `ST_Contains(centroide)` == `code` de la fila → geometria y backbone convergen.
2. **Round-trip**: el centroide del municipio X cae dentro del poligono de X (`assert ST_Contains=true`; fallos revelan centroides corruptos o poligonos mal-mapeados).
3. **Denominador independiente**: conteo de poligonos por nivel vs INE/oficina nacional.
4. **Cross-pais**: punto frontera ES/PT resuelve al pais correcto, bleed=0 (poligonos scoped por country_code).
5. **Cobertura**: % de entities con punto-en-poligono reportado como INTERVALO; huerfanos confesados, nunca redondeado a 100%. Criterio de sello del lever = "documentado como diferido con caso de uso probado", no certificacion de cobertura.

##### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **PRIMARIA — PostGIS (ST_Contains + GiST) sobre geoBoundaries CGAZ**: contencion exacta, ELIMINA el umbral 30 km y cierra la Raiz H de raiz. geoBoundaries: **CC-BY 4.0 / ODbL** (datos, uso comercial con atribucion); PostGIS: **GPL-2.0** (servicio, NO se embebe en codigo distribuido). https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL.md:353].
- **Alternativas**: Overture Maps Divisions (admin boundaries, GeoParquet, **ODbL**), OSM admin via PgOSM Flex (**MIT**), Eurostat GISCO LAU/NUTS.
- **Aceleradores acoplados**: **Uber H3 (h3-py)** — pre-tiling celda→muni para reverse-geocode O(1) + estratos uniformes del sello MSE. **Apache-2.0**, €0. https://github.com/uber/h3 [VERIFIED NEXT-LEVEL.md:361]. **Auto-calibracion p99** — PostGIS `ST_MaximumInscribedCircle` + **GeoPandas/Shapely** (**BSD-3-Clause**, https://github.com/geopandas/geopandas [VERIFIED NEXT-LEVEL.md:369], habilita F16). **Build serverless** — DuckDB spatial (**MIT** [VERIFIED NEXT-LEVEL.md:409]).

↩ [Índice de sub-proyectos](#indice-sub)

<a id="f27"></a>

#### F27 · [Next-level] Desambiguacion IA-local de localidad irreducible (>1 municipio)

**Ficha rápida**

- **Costura (ES→genérico):** Doctrinal, no de codigo: HOY 0 IA, la doctrina confiesa el hueco siempre (None). Residuo irreducible = localidad->>1 muni [VERIFIED geo.py:312-314] y subset-de-tokens de 2+ municipios [VERIFIED geo.py:271-272]. La IA debe ir DETRAS del gate de hueco, recibir solo lo irreducible y probarse por pais.
- **Fix:** Gramatica = Literal[<municipality_code candidatos>] | NULL; temperatura 0; decodificador constrenido (Outlines) hace imposible por construccion un code fuera de set o mal-formado; cruce posterior contra geocoder de direccion (Pelias/PIP), gana la geometria en desacuerdo. Marcado next-level/XL; criterio de sello: 'documentada como diferida, jamas inventa'; NO bloquea el sello geo.
- **Adversarial:** IA en el path de identidad/geo arriesga alucinacion: un desempate equivocado mintea geo/identidad falsa e (si toca cdp_code) inmutable. Sin caso de uso medido es scope-creep. El guardrail de gramatica vuelve segura la palanca (no puede emitir code inventado). Residual: tokenizacion sin espacios en algunas lenguas; coste GPU para volumen masivo.
- **Sellado:** 1) Invariante de decodificacion: fuzzer adversarial -> salida NUNCA fuera del conjunto candidato ni mal-formada (rojo si emite uno). 2) 2a via: cruce contra geocoder de direccion; gana la geometria en desacuerdo. 3) Gate de abstencion: prefiere NULL a match dudoso (precision no-NULL>>recall). 4) Determinismo temp 0. 5) Cero hot-path (solo lo irreducible). 6) Sello del facet: 'diferida, jamas inventa' (no bloqueante).
- **NEXT-LEVEL:** Outlines (grammar-constrained generation) — fuerza la salida a uno de los municipality_code candidatos o NULL, imposible alucinar. https://github.com/dottxt-ai/outlines · Apache-2.0 · €0=True [VERIFIED NEXT-LEVEL.md:422-428]. Aislador aguas-arriba: Splink (Fellegi-Sunter), https://github.com/moj-analytical-services/splink · MIT [VERIFIED NEXT-LEVEL.md:398-404]. GPU = palanca €>0 PENDING-OWNER; guardrail corre en CPU (€0 cimiento) [VERIFIED NEXT-LEVEL.md:427].

**Deep-spec 360**

##### (a) Verificacion de code_hints [VERIFIED]
- [VERIFIED pipeline/geo.py:301-314] `_locality_match`: `codes = loc_index.get(_norm(locality_name)) or loc_index.get(_sorted_key(locality_name)); if codes and len(codes) == 1: return next(iter(codes)); return None` — una localidad que mapea a >1 municipio en la provincia -> None ("better a hole than a lie").
- [VERIFIED pipeline/geo.py:240-299] `_fuzzy_match` tier A (subconjunto de tokens, ambiguity-safe): [:266-274] `supersets = {code for key, code in candidates if query_tokens <= set(key.split())}; if len(supersets) >= 2: return None; if len(supersets) == 1: return next(iter(supersets))` — subset de 2+ municipios distintos -> None; tier B WRatio [:276-299] solo cuando NO es subset. [:277-281] `rapidfuzz ImportError -> None`.
- Confirmado: HOY hay 0 IA en codigo; la doctrina confiesa el hueco SIEMPRE (devuelve None, nunca adivina).

##### (b) Mecanismo al atomo
El residuo irreducible son exactamente los `None` que el determinismo emite a conciencia: (1) localidad -> >1 municipio [geo.py:312-314]; (2) nombre cuyos tokens son subconjunto de 2+ municipios [geo.py:271-272]. La palanca: invocar un LLM open-weight LOCAL con DECODIFICACION CONSTRENIDA POR GRAMATICA. La gramatica (Literal/regex del conjunto de `municipality_code` candidatos ∪ {NULL}) hace MECANICAMENTE IMPOSIBLE que el modelo emita un code inventado o fuera del conjunto. "Hueco > mentira" deja de ser disciplina y pasa a ser invariante de decodificacion. La IA solo DESEMPATA con contexto de direccion; no decide nada estrategico (doctrina capa-2 obrera).

##### (c) Costura ES->generico + fix exacto
NO hay codigo ES que portar (0 IA hoy): la "costura" es DOCTRINAL, no de codigo. La IA debe (i) situarse DETRAS del gate de hueco — nunca rellenar un `None` con conjetura; (ii) recibir SOLO los casos que el determinista/Splink marcaron irreducibles (no toca el hot-path); (iii) probarse por pais con caso de uso MEDIDO. Mecanismo del fix: gramatica = `Literal[<candidatos>] | NULL`; temperatura 0; el decodificador constrenido (Outlines) hace imposible por construccion un code fuera de set o mal-formado; cruce posterior contra el geocoder de direccion (Pelias/PIP) — gana la geometria en desacuerdo. Marcado next-level/XL: su criterio de sello es "documentada como diferida, jamas inventa"; NO bloquea el sello geo.

##### (d) Riesgo adversarial concreto
Meter IA en el path de identidad/geo arriesga ALUCINACION: un desempate equivocado mintea geo/identidad falsa e (si toca cdp_code) inmutable. Debe quedar TRAS el gate de hueco (nunca rellena un None con conjetura) y probarse por pais; sin caso de uso medido es scope-creep, no cimiento. El guardrail de gramatica convierte una palanca peligrosa en segura: no puede emitir un code inventado. Riesgo residual: separacion por espacios que algunas lenguas no respetan (tokenizacion), y coste GPU para volumen masivo.

##### (e) Criterio de sellado + verificacion multi-via
1. Invariante de decodificacion (la prueba clave): un fuzzer alimenta entradas adversariales; la salida NUNCA es un code fuera del conjunto candidato ni mal-formado -> la gramatica lo hace imposible (test rojo si lograra emitir uno).
2. 2a via: cuando la IA elige un candidato, cruzar contra el geocoder de direccion (Pelias/PIP); si el punto cae en otro municipio, gana la geometria, marca hueco/revision.
3. Gate de abstencion: en muestra con verdad conocida, la IA prefiere NULL antes que un match dudoso (precision de los no-NULL >> recall).
4. Determinismo reproducible: temperatura 0 + misma gramatica -> misma salida.
5. Cero entrada al hot-path: la IA solo toca lo que Splink/determinista marcaron irreducible; el 99% nunca la ve.
6. Sello del FACET en si: "documentada como diferida, jamas inventa" (next-level/XL, no bloqueante).

##### (f) Herramienta next-level
**Outlines** (structured/grammar-constrained generation): fuerza la salida a EXACTAMENTE uno de los `municipality_code` candidatos o NULL -> imposible alucinar un code. URL https://github.com/dottxt-ai/outlines · Lic Apache-2.0 · €0=True [VERIFIED NEXT-LEVEL.md:422-428]. Aislador aguas-arriba que entrega la zona gris irreducible a la IA: **Splink** (record linkage Fellegi-Sunter), https://github.com/moj-analytical-services/splink · MIT [VERIFIED NEXT-LEVEL.md:398-404]. Coste: la GPU para inferencia local masiva es la palanca €>0 declarada (PENDING-OWNER: 'GPU/IA-local se activa solo con caso de uso PROBADO + firma del owner'); el guardrail de gramatica corre en CPU para volumen bajo (€0 de cimiento) [VERIFIED NEXT-LEVEL.md:427].

↩ [Índice de sub-proyectos](#indice-sub)

---

## Mejoras a nivel inalcanzable (EUR0, priorizadas)

Todas €0 (vías libres CC0/OSM); ordenadas por relación cierre-de-rotura / esfuerzo.

1. **[S] Resolver multilingüe/no-Latino** vía transliteración CC0 (ICU/unidecode) en el perfil de normalización → habilita EL/BG/RU y **cierra la Raíz B** (la peor rotura) sin perder ES byte-idéntico. *Por qué inalcanzable hoy:* `_norm`/`_normalize` hacen `encode("ascii","ignore")` que vacía no-Latino [VERIFICADO `geo.py:52`, `codes.py:30`]; no hay capa de transliteración.
2. **[M] Backbone pan-EU de una pasada** desde GeoNames `hierarchy.zip` + `allCountries` (CC0): un loader genérico cubre todos los países objetivo de golpe, con `alternateNames` alimentando las tablas de alias **automáticamente** (cierra Raíz G + parte de Raíz E). *Inalcanzable hoy:* `load_geo.py:26-70` es ES-only; nadie escribió el ingestor GeoNames genérico.
3. **[M] Minería automática de alias** de provincia/región desde `alternateNames` (islas, exónimos, bilingües) en vez del dict curado a mano. *Inalcanzable hoy:* `_PROVINCE_ALIASES` es manual [VERIFICADO `geo.py:61-73`].
4. **[L] Reverse-geocode por point-in-polygon** con fronteras OSM/Overture (el adaptador `overture` ya existe) en vez del KNN-centroide: elimina la heurística de 30 km y da contención exacta de municipio (cierra Raíz H de raíz). *Inalcanzable hoy:* solo hay centroides + umbral [VERIFICADO `geocode.py:49`]; requiere polígonos + índice GIST.
5. **[M] Auto-calibración del umbral KNN** por país: derivar el radio de cada municipio de su polígono y fijar el umbral al p99 (depende de #4).
6. **[XL] IA local obrera (capa 2)** SOLO para lo irreducible: desambiguar una localidad que mapea a >1 municipio usando contexto de dirección, manteniendo "mejor hueco que mentira" como gate. *Inalcanzable hoy:* 0 IA en código; la doctrina actual confiesa el hueco [VERIFICADO `geo.py:301-314`]. Palanca futura con caso de uso probado + firma del owner, no cimiento.

---

## Riesgos / open items

| # | Riesgo / open item | Severidad | Causa-raíz | Gate |
|---|---|---|---|---|
| 1 | Esquema `CHAR(2)/CHAR(5)` no alberga DE-8/IT-6/PT-6/FR-3; sin `0054` el INSERT del país #2 revienta | CRITICAL | Raíz A | Migración `0054` ANTES de sembrar no-ES |
| 2 | `codes.py:_normalize` colapsa no-Latino → `cdp_code` colisionado **inmutable** (JP/CJK/EL/cirílico) | CRITICAL | Raíz B | Transliteración en identity-path ANTES de mintear no-Latino |
| 3 | Lecturas/efectos country-blind vivos (trigger comarca, geocoders, seeder, router/stats, `_upsert`) corrompen en silencio al sembrar país #2 | CRITICAL | Raíz C | Cerrar TODAS en el MISMO PR del país #2 |
| 4 | G1 `complete.py:73,89` rechaza FR-DOM/IT y todo `CDP-DE-*`; bloquea promoción a servible | HIGH | Raíz D | Pack-G1 (predicado per-país + regex `{2,3}`) |
| 5 | Canónico de 3 tablas puede quedar corto para país con 4 niveles vinculantes; `geo_subregion` additiva mitiga, no probada | MEDIUM | diseño | YAGNI hasta caso real |
| 6 | Sello actual ciego a ancho/no-Latino/prov-3/sangrado comarca/sangrado geocoder; verde sin probar nada de eso | HIGH | sealing holes | Golden de forma extranjera obligatorio (paso 14) |
| 7 | Completitud del backbone vía GeoNames/OSM varía por país; el denominador nacional libre no siempre existe | MEDIUM | dato | Sello degrada a intervalo con cota inferior honesta, jamás 100% sin denominador |
| 8 | `ccaa_code CHAR(2) NOT NULL` + síntesis de región para países sin agrupación supra-provincial | MEDIUM | Raíz E | Atado a `0054` + regla de síntesis en el pack |
| 9 | `VARCHAR` vs `CHAR` en comparaciones (padding) — ES sin padding, pero debe probarse en `0054` | LOW | Raíz A | Golden de igualdad/JOIN en la migración |

> **Cierre de honestidad:** todas las cifras DB de este capítulo son punto-en-el-tiempo (stack vivo caído, no re-verificado en esta pasada). Todas las citas `path:línea` fueron leídas contra el código en Wave 1. Los `OPEN ITEM` son reversibles y declarados; ninguno se presenta como hecho. La etapa Geo es genérica **en esquema y arquitectura**; **no** en operación, hasta cerrar Raíces A–D.
