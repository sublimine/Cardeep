# Etapa 1 · Descubrir — Biblia (v2 PROFUNDO)

> Estado adversarial: **NEEDS_REWORK** (`holds=false`). El esquema es paramétrico por país (0052/0053), pero la **lógica** de descubrir es country-BLIND: el motor estampa ES por omisión y mezcla países por debajo del esquema. Fuente: Wave 1 (path:línea verificado, re-leído en código vivo 2026-06-27). Stack vivo CAÍDO: PG :5433/:5434 abajo → toda cifra DB es **punto-en-el-tiempo** y la coexistencia byte-idéntica del piloto DE es **[ASSUMED]** (verificado el código de 0052/0053 + andamiaje golden, NO la corrida viva).
>
> **Provenance v2.** Este capítulo añade el **deep-dive por faceta**: las **40 facetas** de la etapa (`relleno/01-discover/g0..g6.json`), cada una un proyecto navegable con deep-spec verificado + costura + fix + adversarial + sellado + herramienta NEXT-LEVEL (€0), con `path:linea` **[VERIFIED]** re-leído de la fuente. **422** marcas `[VERIFIED]` en las facetas. La estructura v1 (Misión → Veredicto adversarial → Mejoras → Riesgos) se conserva íntegra; la novedad es **`## Sub-proyectos institucionales (360 por faceta)`**.
>
> **Novedad v2.** «360» = tratamiento de 360° por faceta, no 360 facetas (la etapa tiene **40** átomos de código). 28 facetas autocontenidas + 12 magras, todas con la misma rejilla `(a)`–`(f)`. El deep-dive **no reescribe ES**: baja al átomo cada costura y la mapea a su fix raíz **R1–R11**, marcando los 2 open items (R6 BLOQUEADOR 6, R7 transliteración) con causa y gating.

---

## Navegación (funnel)

**Capítulo (estructura A→Z):**
[Misión](#misión) · [Lo que existe HOY](#lo-que-existe-hoy-verificado) · [Motor](#motor-invariante-reusado-byte-idéntico-por-país) · [Pack por país](#pack-por-país-lo-que-cada-país-aporta-para-esta-etapa) · [Costuras → fix](#costuras-es-hardcoded--fix) · [Diseño genérico A→Z](#diseño-genérico-az) · [Onboarding](#onboarding-de-país-nuevo-pasos-de-biblia-para-esta-etapa) · [Sellado + rollback](#sellado--verificación-multi-vía--rollback) · [Veredicto adversarial](#veredicto-adversarial-roturas--resolución) · [**Sub-proyectos (360 × 40)**](#sub-proyectos-institucionales-360-por-faceta) · [Mejoras nivel-inalcanzable](#mejoras-a-nivel-inalcanzable-0-priorizadas) · [Riesgos / open items](#riesgos--open-items)

**Los 40 sub-proyectos (por familia):**

| Familia | Sub-proyectos |
|---|---|
| **A · Frontera de normalización (contrato · DTO · registro)** | [F01 Contrato SourceAdapter](#f01) · [F07 DTO DiscoveredEntity](#f07) · [F13 Registro ADAPTERS + dispatch CLI](#f13) |
| **B · Resolución geográfica (cascada · índice · provincia · fallbacks)** | [F02 Cascada municipality_code](#f02) · [F08 Matcher fuzzy de municipio](#f08) · [F14 Gazetteer INE Nomenclator](#f14) · [F20 Fallbacks de recuperacion geo + SKIP h…](#f20) · [F31 GeoResolver: carga de indice + alcance…](#f31) · [F36 Resolutor de provincia + alias + ancho…](#f36) |
| **C · Minteo de identidad inmutable (hash · normalización · mint · gate G1)** | [F03 Hashing cdp_pair/cdp_code + base32 + i…](#f03) · [F25 _upsert idempotente + costura nuclear…](#f25) · [F26 Politica de normalizacion de texto](#f26) · [F32 Algebra de identidad canonical_key](#f32) · [F35 Gate G1 IDENTITY por-entidad](#f35) · [F37 Ensamblado mint_code](#f37) |
| **D · Cuórum VAM + oráculo de cuenta** | [F09 Motor de quorum record_count_verdict](#f09) · [F15 Taxonomia de familias VAM + oraculo de…](#f15) · [F19 Orquestacion discover() + cuenta por-r…](#f19) |
| **E · Planificación recurrente (scheduler · gate · cadencia · breaker · lock)** | [F04 Gate AUTO-run por requires_env](#f04) · [F10 Lanzador _run_vector + auditoria _record](#f10) · [F21 DiscoveryJob + DISCOVERY_REGISTRY](#f21) · [F27 Motor de vencimiento de cadencia](#f27) · [F33 Circuit breaker del scheduler](#f33) · [F38 Advisory lock singleton + lease heartb…](#f38) |
| **F · Capa MSE (sello · captura · listas · estimadores · triangulación)** | [F05 Sello compute + roll-up nacional honesto](#f05) · [F11 Persistencia del sello + tablas MSE ci…](#f11) · [F16 Taxonomia de listas ortogonales (bucke…](#f16) · [F17 Triangulacion externa DIRCE](#f17) · [F22 Taxonomia DEALER_KINDS → segmento](#f22) · [F28 Construccion de la matriz de captura](#f28) · [F34 Lectura de patrones 0/1](#f34) · [F39 Estimadores captura-recaptura](#f39) |
| **G · Pack de país + sustrato (FS · perfiles · esquema · vectores · roster)** | [F06 Layout de filesystem por pais](#f06) · [F12 Perfil de pais: convencion postcode→L1](#f12) · [F18 Perfil de pais: validadores de identidad](#f18) · [F23 Clasificador de actividad / dealer](#f23) · [F24 Pack de fuentes por pais](#f24) · [F29 Filtro geografico de scope + excluded_…](#f29) · [F30 Vector geo-POI global dia-uno](#f30) · [F40 Sustrato de esquema geo+entity por pai…](#f40) |

---

## Misión
Reducir **cualquier fuente de cualquier país** —registro mercantil, mapas POI, dorks, localizadores OEM, marketplaces, grafo corporativo— a un censo de puntos de venta con identidad inmutable (`cdp_code`), conteo verificado por cuórum (VAM) y completitud estimada por captura-recaptura (MSE). En la Etapa 1 nace la entidad: aquí se decide su **país**, su **provincia**, su **clave de identidad** y su **cuenta de confianza**. Un error aquí es **append-only e irreversible** (el `cdp_code` no se re-mintea). Por eso Descubrir es la etapa donde un sangrado country-blind no es un bug cosmético: corrompe el censo en silencio.

El norte (00-MASTER §Norte): España NO es el producto, es la **primera ejecución** que endurece el motor. Cubrir un país nuevo = **añadir módulos + filas**, jamás reescribir ES (byte-identidad pineada por `tests/test_country_golden.py`).

---

## Lo que existe HOY (verificado)
- **Contrato `SourceAdapter` country-agnóstico** [VERIFIED `pipeline/sources/base.py:29-40`]: `source_key`, `declared_count()->int|None` (oráculo de cuenta para VAM), `fetch()->list[DiscoveredEntity]`. Es la frontera de normalización.
- **DTO `DiscoveredEntity` de 18 campos** [VERIFIED `pipeline/sources/base.py:7-26`]: lleva `province_name`/`municipality_name` **CRUDOS** (texto), resueltos a código en el ingest, nunca pre-resueltos. Cualquier fuente del mundo se reduce a este DTO.
- **Registro `ADAPTERS`** [VERIFIED `pipeline/discover.py:48-74`]: `dict[str, type[SourceAdapter]]` con 25 adaptadores (dgt_cat, 8×oem_*, osm, 3×assoc, 5×*_census, overture, dork_municipal, borme_cnae, axesor_cnae, graph_recursive, paginas_amarillas, collapse_invisible).
- **Orquestación `discover()`** [VERIFIED `pipeline/discover.py:117-167`]: fetch → log declared/fetched/excluded → por entidad: geo-resolve + mint + upsert → cuenta `in_db` scoped al run (`seen_at >= run_start`, `:152-154`) → veredicto VAM.
- **`_upsert` con cascada geo + INSERT idempotente** [VERIFIED `pipeline/discover.py:77-114`]: `province_code → municipality_code → resolve_city_global → geocoder.nearest_province`, con **SKIP honesto** si no hay provincia (`:88-90`); `INSERT entity ... ON CONFLICT(cdp_code) DO UPDATE last_seen RETURNING (xmax=0) AS inserted` (`:99-101`); `entity_source` idempotente.
- **Mint `cdp_code` YA parametrizado** [VERIFIED `services/api/codes.py:44-53`]: `mint_code` es el **ÚNICO hogar del literal de prefijo** (`:53` → `CDP-{country_code}-{province_code}-{base32}`), `country_code` default `'ES'` (`:24`). `canonical_key` **IGNORA `country_code` a propósito** (`:62-65`) → el país no entra en la pre-imagen de dedup, no re-keya entidades.
- **VAM `record_count_verdict`** [VERIFIED `pipeline/verify.py:31-50` + `:53-212`]: cuenta TRUSTWORTHY solo con **cuórum ≥2 familias/orígenes ortogonales** que coinciden (modal exacto); `primary_path` debe concordar; cero no certifica sin observación. Mapea path→familia (`db`/`http`/`source`/`registral`/`other`, `:42-50`).
- **Scheduler de descubrimiento recurrente (6º eje)** [VERIFIED `pipeline/discover_schedule.py:53-84`]: `DISCOVERY_REGISTRY` de 5 vectores (borme_cnae 24h, collapse_invisible 168h, overture 720h, graph_recursive 720h, dork_municipal 2160h); `DiscoveryJob(source_key, vector, cadence, orthogonal, env, requires_env)`.
- **Robustez del scheduler** [VERIFIED `pipeline/discover_schedule.py:49-50,101-206`]: circuit breaker (`consecutive_fails>=3`), advisory lock propio `0x43415244+1` (distinto del harvest `0x43415244`), AUTO-run gate por `requires_env`, `--once` bypasa el gate (intención del operador), due-tracking reusa `source_health` vía upsert €0.
- **Taxonomía MSE de listas ortogonales** [VERIFIED `pipeline/exhaustiveness/lists.py:27-49,65-74`]: `bucket_for(source_key)→clase`; `ORTHOGONAL_LISTS=(GEO,CENSUS,DGT,ASSOC,OEM,DORK,REG)` (`:49`); MKT/GRAPH/COLLAPSE excluidos por sesgo/dependencia.
- **Matriz de captura MSE** [VERIFIED `pipeline/exhaustiveness/capture.py:49-92`]: unidad = entidad RESUELTA (`v_dealer_resolved.resolved_ulid`) → dupes cross-source colapsan a 1; estratos = `province_code × segment`; `read_patterns` construye vectores 0/1 sobre buckets y excluye el patrón all-zero.
- **Sello MSE** [VERIFIED `pipeline/exhaustiveness/seal.py:27,39-162`]: estrato SELLADO sii `coverage_lower = n_obs/ci_high >= 0.95` (`:27`), **NUNCA el punto**; roll-up nacional = suma de N̂ por estrato IDENTIFICADO (no-identificados reportados aparte, anti-maquillaje, `:84-107`).
- **Triangulación census externo YA parametrizada** [VERIFIED `pipeline/exhaustiveness/triangulation.py:24-81`]: `load_external_census(path, country_code='ES')` resuelve `census_dir(country_code)/dirce_cnae451.csv`; devuelve `{}` (no_anchor) si ausente; `triangulate` consistente si `0.7 <= N̂/ext <= 1.4`.
- **GeoResolver** [VERIFIED `pipeline/geo.py:129-183,200-314`]: índice en memoria, cascada exacta → fuzzy (rapidfuzz WRatio≥88 con guardas) → locality (Nomenclátor INE), guardas de ambigüedad ("mejor un hueco que una mentira").
- **Sustrato de esquema parametrizado** [VERIFIED `migrations/0052_country.sql:49-81` + `0053_country_onboarding.sql:1-10,51-174`]: 0052 añade `country_code CHAR(2) NOT NULL DEFAULT 'ES'` a geo/entity + UNIQUE compuesto `(country_code,code)`; 0053 promueve PK geo a `(country_code,code)`, reescribe 6 FK a compuestas, relaja los 2 CHECK ES con `country_code<>'ES' OR <pred>`. La cabecera de 0053 PRUEBA la colisión: `INSERT geo_province(code='28',country_code='DE')` fallaba bajo `geo_province_pkey(code)`.
- **FS por país** [VERIFIED `pipeline/paths.py:33-63`]: `countries/<CC>/recipes|census`, `data/<CC>`; `country_of_cdp` parsea `^CDP-([A-Z]{2})-`; árbol `countries/` contiene SOLO `ES` hoy.
- **Guarda golden de byte-identidad ES + xfail(strict) G1** [VERIFIED `tests/test_country_golden.py:262-291`]: vigila el ensanche de `complete.py:89` (auto-flip a XPASS al ensancharse).
- **[ASSUMED]** Piloto DE byte-idéntico coexistió con ES y se revirtió (decisión bloqueada #1, 00-MASTER). Verificado el código de migración (0053) y el andamiaje golden (`tests/test_country_golden.py:169,249` → `CDP-DE-28-*`), **NO** la corrida viva (PG :5433 caído).

---

## Motor (invariante, reusado byte-idéntico por país)
La columna vertebral de Descubrir es, por diseño, country-agnóstica. Lo que NO cambia de un país a otro:

1. **Frontera de normalización** — `SourceAdapter` (`base.py:29-40`) + `DiscoveredEntity` 18 campos (`base.py:7-26`). N fuentes heterogéneas → 1 DTO con códigos geo SIN resolver.
2. **Bucle por-entidad** — `discover()`/`_upsert` (`discover.py:77-167`): fetch → cascada geo → mint `cdp_code` → `INSERT ON CONFLICT(cdp_code)` idempotente → `entity_source` → VAM. La forma del bucle es idéntica país a país.
3. **Mint de identidad** — `mint_code`/`canonical_key`/`cdp_pair`/`cdp_code` (`codes.py`): prefijo en UNA línea (`:53`), `country_code` fuera de la pre-imagen de dedup (`:62-65`). Reusado byte-idéntico.
4. **Juez de cuentas** — `record_count_verdict` (`verify.py:53-212`): cuórum por familias ortogonales. El mismo juez para todo país.
5. **Planificación recurrente** — `discover_schedule.py` (`DiscoveryJob`/`_tick`/`_due`/`_gated`/`_record`): cadencia, breaker, lock, gate `requires_env`. La maquinaria no cambia.
6. **Matemática MSE** — `lists` + `capture` + `seal` + estimadores (Chapman/Chao2/Jackknife) + `triangulation`. La captura-recaptura es idéntica; **solo cambian los DATOS de entrada** (esta promesa es la que el inquisidor rompe — ver §Veredicto).
7. **Algoritmo GeoResolver** — cascada exacta/fuzzy/locality + guardas de ambigüedad (`geo.py:129-314`). El **algoritmo** nombre→código es invariante (su **forma de código** y sus **datos** NO lo son — ver §Costuras).
8. **Sustrato de esquema** — `entity`, `entity_source`, `discovery_list`, `discovery_capture`, `exhaustiveness_estimate`, `source_health`, `harvest_run`, `verification_verdict`, PK geo compuesta `(country_code,code)`.
9. **Invariantes transversales** — `cdp_code` inmutable, append-only, sample-verify-delete, SKIP honesto sin provincia, €0.

---

## Pack por país (lo que cada país aporta para esta etapa)
Genérico ≠ uniforme (00-MASTER §Doctrina): el país aporta un pack **profundo y a medida**, no config fina. Para Descubrir, el pack de país `CC` es:

1. **Módulos adaptadores** `pipeline/sources/<src>.py` para sus vectores: registro mercantil (BORME → Handelsregister/Unternehmensregister DE), localizadores OEM (`kia.com/es-es` → `kia.de`), marketplaces (coches.net/milanuncios → mobile.de/autoscout24.de), capa POI geo (bbox + filtro país), dorks (plantillas + idioma), extractores phone/reg-id.
2. **Entradas de `ADAPTERS`** (`discover.py:48`): qué `source_key` mapea a qué clase para `CC`.
3. **Entradas de `DISCOVERY_REGISTRY`** (`discover_schedule.py:65`): vectores recurrentes + `cadence_hours` + `orthogonal` + `requires_env`.
4. **Mapeo de taxonomía MSE** para los `source_key` de `CC`: qué mecanismo de captura es cada lista (declarado en el adaptador, no en `_EXACT` — ver §Diseño).
5. **Datos geo**: filas `geo_province`/`comarca`/`municipality` con `country_code=CC` (fuente oficial análoga a INE), mapa de alias + gazetteer del resolver, validador de rango de provincia.
6. **CSV census/denominador**: `countries/<CC>/census/dirce_cnae451.csv` (análogo: KBA/Destatis DE, SIV/ANFIA IT) con mapeo de clasificación (NACE/WZ/NAF/SCIAN/JSIC → segment).
7. **Convenciones geo del país**: `postcode → L1` (cuando aplica), dicts `categoría → kind`.
8. **Perfil de identidad local**: normalizador de teléfono (E.164 del plan de numeración), validador de id registral (CIF → VAT/registro del país), **política de normalización/transliteración del alfabeto** (latino vs no-latino).

> Estos 8 puntos son el **CountryProfile + roster** que la etapa Descubrir consume. El contrato consolidado vive en `COUNTRY-PACK-CONTRACT.md` (Ola 2).

---

## Costuras ES-hardcoded → fix
Cada costura es un punto donde ES está cableado en el **motor** (no en el pack). Todas verificadas en código vivo 2026-06-27.

| location | issue | fix |
|---|---|---|
| `pipeline/discover.py:95-104` | El `INSERT entity` **NO incluye `country_code`**. Como la columna es `NOT NULL DEFAULT 'ES'` (`0052:54`), TODA entidad descubierta cae a `'ES'` en silencio. Un adaptador extranjero estampa su dealer como ES sin error. Es la **costura nuclear**: el upsert es el único punto de escritura. | Añadir `country_code` a las columnas del INSERT y pasar `adapter.country_code`. Gate: `SELECT count(*) FROM entity WHERE country_code='CC' AND cdp_code NOT LIKE 'CDP-CC-%' == 0`. |
| `pipeline/discover.py:91-93` | La llamada a `cdp_code(...)` omite `country_code` → default `'ES'` (`codes.py:24,125`). Aunque `entity.country_code` fuese DE, el código minteado sería `CDP-ES-`. El mint ya es paramétrico (`mint_code:53`); el call-site no lo aprovecha. | Pasar `country_code=adapter.country_code` a `cdp_code(...)`. Una línea. Golden pinea byte-identidad ES (`test_country_golden.py:72-96`). |
| `pipeline/discover.py:117-118,127` | `discover(source_key)` no tiene noción de país: hace `ADAPTERS[source_key]()` y corre; `GeoResolver.load(conn)` sin país. El adaptador no declara su país → upsert/mint/geo no saben qué `country_code` enhebrar. | Atributo de clase `SourceAdapter.country_code='ES'` (override por adaptador de país); `discover()`/`_upsert` lo leen para enhebrar geo-scope + mint + INSERT. Cero cambio de CLI. |
| `pipeline/geo.py:151-157` | `GeoResolver.load(conn)` hace `SELECT code,name FROM geo_province` (`:153`) y `SELECT code,name,province_code FROM geo_municipality` (`:157`) **SIN filtro `country_code`** (grep: 0 hits de `country` en geo.py). Cargado un 2º país, ES y DE provincia `'28'`/muni colisionan en el índice en memoria → resuelve nombres cross-país → mintea provincia (y `cdp_code`) **ERRÓNEO e IRREVERSIBLE**. | `WHERE country_code=$1` en ambas queries + enhebrar arg `country_code` en `load()` y API pública, default `'ES'`. Gate: una resolución ES devuelve el mismo código que antes del scoping. |
| `pipeline/geo.py:46-48,61-73,101-104,200-207` | Datos INE-ES + **forma de código ES** horneados en el resolver genérico: `_GAZETTEER_PATH` INE, `_PROVINCE_ALIASES` (menorca→07…), `province_code()` asume ancho 2-díg (`s.zfill(2)`, `:205`), gazetteer deriva `prov_code = muni_code[:2]` descartando `len!=5` (`:101-104`). Un país con L1 de otro ancho/esquema rompe. | Inyectar `gazetteer_path` + `alias_map` + `postcode_to_l1` + `province_validator` como **CountryProfile** (no reusar CSV/alias INE); el resolver los recibe por arg, default a los artefactos ES. |
| `migrations/0048_discovery_capture.sql:39,58` + `pipeline/exhaustiveness/capture.py:77-92` | Estratos MSE **SIN dimensión país**: `discovery_capture.province_code char(2)` y `exhaustiveness_estimate.province_code char(2)`; `_fetch_raw` lee TODAS las filas `entity` sin filtro país (grep: 0 hits `country` en capture.py). Dos países con provincia `'28'` COLAPSAN en un estrato → contaminan `coverage_lower`. Deuda NETA no cubierta por los playbooks. | Migración aditiva: `ALTER discovery_capture/exhaustiveness_estimate ADD country_code`, incluirlo en la tupla de estrato + PK/índices; country-scope `_fetch_raw` con `WHERE e.country_code=$1`. Reversible (additive). |
| `pipeline/exhaustiveness/lists.py:27-45,65-74` | `_EXACT` mapea `source_key` ES→bucket (100% claves ES); `bucket_for` cae a `'MKT'` (excluido de `ORTHOGONAL_LISTS`) para cualquier clave desconocida (`:74`). Un roster extranjero cae todo a MKT **SIN error** → cada lista extranjera se descarta del MSE → `coverage_lower` sub-cuenta en silencio. | Declarar el bucket en el adaptador (`SourceAdapter.orthogonal_bucket`) y que `bucket_for` lo lea → cero acoplamiento. (Alt. inferior: `_EXACT` por país.) |
| `overture.py:227` / `osm.py:77` / `oem_kia.py:72` / `borme_cnae.py:207` / `graph_recursive.py:163` | La convención ES `postcode[:2]==provincia INE` está COPIADA inline en 5+ adaptadores (DRY roto). `oem_kia.py:72` hardcodea el rango `'01'<=p<='52'` (52 provincias ES). Un país cuyo CP no prefijee la provincia obliga a reescribir cada adaptador. | Hook `CountryProfile.postcode_to_l1(postcode)` que el adaptador llama; override una vez. El rango de provincia se **deriva** de `geo_province` filtrado por `country_code`, no de un literal. |
| `pipeline/complete.py:73,83-85,89` | Aguas abajo de discover (gate de COMPLETION) pero valida su salida. **DOBLE costura ES**: `_PROVINCE_RE=^(0[1-9]|[1-4][0-9]|5[0-2])$` (solo 01-52, `:73`), `_CDP_CODE_RE=^CDP-ES-([0-9]{2})-...` (`:89`), `_NATIONAL_KINDS` ES (`:83-85`). Rechaza toda entidad `CDP-CC-` y todo distrito extranjero. | Ensanchar `_CDP_CODE_RE` a `^CDP-([A-Z]{2})-([0-9]{2})-...` (superconjunto estricto) y quitar el xfail (`test_country_golden.py:286-290`); hacer `_PROVINCE_RE`/`_NATIONAL_KINDS` table-driven desde `geo_province` por `country_code`. |
| `services/api/codes.py:29-32` + `pipeline/geo.py:51-53` | `_normalize` hace `NFKD + encode('ascii','ignore')`; `_norm` igual. Un nombre/municipio no-latino → `''` → `canonical_key` colapsa a `name:|{muni}` idéntico para todo dealer sin dominio/CIF del mismo municipio → **fusión masiva cross-entity** en un solo `cdp_code`; búsquedas geo por `''` nunca resuelven → 100% SKIP. | Política de transliteración por país en el CountryProfile (latino: identidad; no-latino: romanización determinista o capa-2 IA-local). **OPEN ITEM** para alfabetos no-latinos (ver §Veredicto R7). |
| `pipeline/verify.py:48` | La familia `registral` del VAM lleva nombres de instituciones ES: `dgt/cnae/faconauto/borme/census/official/registr`. Una autoridad MX (RPPC/SAT) o JP (JSIC) no casa ninguna → familia `'other'` (`:50`) → independencia debilitada. | `registral` derivado de `CountryProfile.reg_authorities` (lista de tokens del país); marcar explícitamente cuando la pata registral está ausente (no degradar a `db==http` en silencio). |

---

## Diseño genérico A→Z
La genericidad **NO** se logra reescribiendo ES, sino abriendo costuras de parametrización sobre lo ya probado. Cinco movimientos:

**A) El país es un atributo del ADAPTADOR, no un argumento de la CLI.**
Se añade `SourceAdapter.country_code: str = 'ES'` como atributo de clase. Un adaptador ES (`DgtCatAdapter`) lo hereda `'ES'`; un adaptador DE (`HandelsregisterAdapter`) declara `'DE'`. `discover()` lee `adapter.country_code` y lo enhebra en los **TRES puntos donde hoy ES es implícito**:
1. `GeoResolver.load(conn, country_code)` → `WHERE country_code=$1` → índice en memoria scoped, sin colisión cross-país.
2. `cdp_code(..., country_code=cc)` → prefijo `CDP-{cc}-` vía `mint_code` (`codes.py:53`, ya paramétrico).
3. `INSERT entity(..., country_code, ...)` → sella la fila.

Así un país nuevo se cubre **AÑADIENDO** módulos + filas, sin tocar una sola línea de la lógica ES (byte-identidad pineada por `test_country_golden.py`).

**B) Registro derivable por país.**
`ADAPTERS` (`discover.py:48`) y `DISCOVERY_REGISTRY` (`discover_schedule.py:65`) son dicts planos. El diseño evoluciona a un registro derivable: `ADAPTERS_BY_COUNTRY[cc] = {sk:cls for sk,cls in ADAPTERS.items() if cls.country_code==cc}`, de modo que el scheduler planifique "todos los vectores DUE de DE" sin nuevo cableado. Cada adaptador declara `orthogonal: bool` y `orthogonal_bucket: str` → `lists.bucket_for` lee del adaptador en vez de `_EXACT` ES-hardcoded → **elimina el sumidero silencioso a MKT**.

**C) Dimensión país en la capa MSE.**
El sustrato geo/entity ya está sellado (0052/0053). Falta extender país a `discovery_capture`/`exhaustiveness_estimate`: hoy estratifican por `province_code char(2)` SIN país → dos países con provincia `'28'` colapsan. Migración aditiva `005X` que añade `country_code` a esas dos tablas y a la tupla de estrato, y country-scope `capture._fetch_raw`. El estrato pasa de `(province,segment)` a `(country,province,segment)` y el roll-up nacional de `seal.compute` es **por-país sin tocar la matemática** (Chapman/Chao2/Jackknife, `coverage_lower>=0.95`).

**D) `CountryProfile` — el objeto que mata el copy-paste.**
Hoy `postcode[:2]→provincia INE` está replicado inline en 5+ adaptadores y el resolver carga gazetteer/alias INE hardcodeados. Se introduce:
```
CountryProfile {
  postcode_to_l1,      # CP -> código L1 (o None si el país no lo deriva del CP)
  phone_normalizer,    # E.164 del plan de numeración
  reg_id_validator,    # CIF -> VAT/registro del país
  reg_authorities,     # tokens de la familia 'registral' del VAM (codes -> verify.py)
  alias_map,           # alias de provincia (NO reusar _PROVINCE_ALIASES INE)
  gazetteer_path,      # gazetteer de localidades (NO reusar el CSV INE)
  province_validator,  # rango/forma de L1 (deriva de geo_province, no de un literal 01-52)
  code_shape,          # forma del código administrativo (ancho, no-dígito: FR 2A/2B, DE AGS-8)
  translit_policy,     # latino: identidad; no-latino: romanización determinista
}
```
El motor lo consume: el adaptador llama `profile.postcode_to_l1(cp)` en vez de `cp[:2]`; `GeoResolver` recibe `alias_map`+`gazetteer`+`code_shape` por arg. ES provee el perfil INE **byte-idéntico al inline actual**; DE provee el suyo una vez. ~10 hardcodes dispersos → 1 punto de override por país.

**E) Modelo 3-capas aplicado a Descubrir** (00-MASTER §Modelo).
- **Capa-1 (músculo determinista 24/7)** = scheduler + adaptadores + VAM, corriendo continuo.
- **Capa-3 (Claude decididor)** = autoría del roster por país + adjudicación de costuras + caza de recetas Tier-1.
- **Capa-2 (IA-local obrera, HOY 0 en código)** = futura: el clasificador objeto-social/CNAE de `borme_cnae._classify` es ES-keyword-hardcoded; una IA-local lo vuelve country-agnóstico ("¿es automotor?" sin lista de keywords por país). Palanca futura con caso de uso probado, **no cimiento** (gate GPU = €>0, firma owner).

**Resultado:** cubrir un país en Descubrir = (a) cargar su geo con `country_code`, (b) escribir su roster declarando `country_code`+`orthogonal_bucket`, (c) registrarlos, (d) proveer su `CountryProfile` + census. **CERO reescritura de ES; el motor es el mismo binario.**

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)
> Estado destino `cover(CC)`: `BOOTSTRAPPED → IN_COVERAGE` (00-MASTER §Estados).

0. **Pre-flight.** Verificar FASE-0+0053 intactas (entity/geo con `country_code`, PK geo compuesta, ES byte-idéntico). `pytest tests/test_country_golden.py` verde; `SELECT count(*) entity WHERE country_code='ES' == baseline`. (REPLICATION-PLAYBOOK B.0.)
1. **Sembrar backbone geo de CC.** `scripts/load_geo_CC.py` (clon de `load_geo.py`) inserta `geo_province`/(comarca si 3-nivel)/`geo_municipality` con `country_code='CC'` desde la fuente oficial. `INSERT ... ON CONFLICT DO NOTHING`. Gate: counts == grid oficial, ES intacto (52/8.132).
2. **Country-scope el GeoResolver.** `WHERE country_code=$1` en `geo.py:153,157` + enhebrar arg `country_code` (default `'ES'`); proveer `alias_map`+`gazetteer` de CC (NO reusar INE). Gate: resolución ES byte-idéntica; resolución CC sin sangrado.
3. **Escribir el `CountryProfile` de CC.** `postcode_to_l1`, `phone_normalizer`, `reg_id_validator`, `province_validator`, `code_shape`, `translit_policy`, `reg_authorities`. Mínimo: override de `postcode→L1` si CC no prefijea provincia.
4. **Escribir los MÓDULOS adaptadores** bajo `pipeline/sources/<src>.py`: `fetch()->DiscoveredEntity` (province/muni crudos), `declared_count()` para VAM, y declarar `country_code='CC'` + `orthogonal_bucket`. Cubrir vectores: registral (V1), geo POI (V2 overture/osm casi-globales), dork (V3), OEM locators (V4), census marketplace (V5), graph/collapse (V6).
5. **Registrar.** Entradas en `ADAPTERS` (`discover.py:48`) y, para recurrentes, en `DISCOVERY_REGISTRY` (`discover_schedule.py:65`) con `cadence_hours`/`orthogonal`/`requires_env`.
6. **Enhebrar `country_code` en discover.** Pasar `adapter.country_code` a `cdp_code()` (`discover.py:91`) + añadir la columna `country_code` al INSERT (`discover.py:96-104`). Verificar: ninguna entidad CC con `cdp_code NOT LIKE 'CDP-CC-%'`.
7. **Capa MSE.** Mapear `source_key` de CC a buckets (vía `adapter.orthogonal_bucket`) + aplicar la migración aditiva que añade `country_code` a `discovery_capture`/`exhaustiveness_estimate` + country-scope `capture._fetch_raw`.
8. **Census/denominador** (opcional al inicio). `countries/CC/census/dirce_cnae451.csv` + `SOURCE.md` (anclaje €0 oficial: KBA/Destatis DE). Sin él, triangulación degrada a `no_anchor` (honesto, **marcado**, no silencioso — ver §Veredicto R11).
9. **Correr y sellar.** `python -m pipeline.discover <cc_src>` debe cerrar VAM TRUSTWORTHY (`declared==fetched==in_db`). `python -m pipeline.exhaustiveness.cli` scoped a CC para `coverage_lower`.
10. **Re-verificar golden.** ES byte-idéntico (`entity WHERE country_code='ES' == baseline`, todo `CDP-ES-`) y CC todo `CDP-CC-`; ensanchar `complete.py:89` a `^CDP-([A-Z]{2})-` y quitar el xfail G1 para que las entidades CC pasen el gate de completion.

---

## Sellado + verificación multi-vía + rollback
**SELLADO de Descubrir = CUATRO cosas simultáneas para CC:**
- (a) toda entidad lleva `country_code='CC'` y `cdp_code 'CDP-CC-'` (cero fuga ES en INSERT/mint);
- (b) cada corrida de adaptador cierra un VAM TRUSTWORTHY (`declared==fetched==in_db`, scoped al run vía `seen_at>=run_start`, `discover.py:152-164`);
- (c) `coverage_lower MSE >= 0.95` para ≥1 estrato CC identificado, o `no_anchor` honestamente reportado;
- (d) **CERO regresión ES** (`entity WHERE country_code='ES' == baseline`, todo `CDP-ES-`, golden verde).

**VERIFICACIÓN POR 3 VÍAS ORTOGONALES (no una):**
1. **INTRA-RUN (conteo)** — el VAM no es una cuenta sola sino un cuórum de ≥2 familias/orígenes ortogonales (`verify.py:117-119` exige `family_n>=2` y `origin_n>=2`). Una pérdida silenciosa de ingestión (colisión/skip) diverge el `primary_path` y NUNCA lee TRUSTWORTHY.
2. **CROSS-LIST (completitud)** — el MSE captura-recaptura es un mecanismo DISTINTO al conteo por-fuente: estima la celda no-observada cruzando listas ortogonales (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG). Verifica COMPLETITUD, no cuenta.
3. **EXTERNO (anclaje)** — la triangulación contrasta N̂ contra un census de mecanismo legal/fiscal (`triangulation.py:66-81`, consistente si `0.7<=N̂/ext<=1.4`).

Tres vías que **no comparten punto ciego**. El 100% es un INTERVALO certificado (`coverage_lower`, cota inferior con margen que encoge), **nunca un entero**.

**ROLLBACK:**
- Migración: cada una lleva bloque `-- Rollback:` (`0052:83-91`, `0053:176-218`; el runner lo strip-ea en apply, `migrate.py`).
- Adaptador: quitar de `ADAPTERS`/`DISCOVERY_REGISTRY` + `DELETE FROM entity WHERE country_code='CC' AND first_discovered_source='<src>'` (reversible, no toca ES; REPLICATION-PLAYBOOK B.4).
- Geo: `DELETE FROM geo_municipality/geo_province WHERE country_code='CC'` (loader INSERT-only, ninguna fila ES tocada).
- Census: borrar el CSV (degrada a `no_anchor`).
- **[ASSUMED]** El piloto DE ya probó esta reversibilidad (coexistió byte-idéntico con ES y se revirtió); verificado el código 0053 + golden, NO la corrida viva (PG :5433 caído).

**CRÍTICO:** el `cdp_code` es INMUTABLE; un mint con provincia errónea (por geo no-scoped) re-keya la entidad de forma IRREVERSIBLE. Por eso la costura `geo.py:151-157` es **bloqueante ANTES** de cargar datos de un 2º país.

---

## Veredicto adversarial: roturas → resolución
> El inquisidor falló **NEEDS_REWORK** (`holds=false`). Ningún break se oculta. Cada uno mapea a un **fix raíz Rn**; los que no se pueden cerrar en diseño quedan como **OPEN ITEM con causa + gating**.

### Mapa de fixes raíz
| Rn | Fix raíz | Cierra |
|---|---|---|
| **R1** | Country threading (atributo `SourceAdapter.country_code` → 3 puntos de escritura) | B-DE-mint, parte de B-DE-geo, parte de B-MX-MSE |
| **R2** | `GeoResolver.load` country-scoped (`WHERE country_code=$1`) | B-DE-geo |
| **R3** | `CountryProfile.code_shape` + gazetteer/alias inyectados | B-FR-codeform |
| **R4** | `SourceAdapter.orthogonal_bucket` (taxonomía declarada por adaptador) | B-IT-bucket |
| **R5** | Dimensión país en MSE (migración + `_fetch_raw` scope) | B-MX-MSE |
| **R6** | Ensanche `complete.py` (ambas regex + table-driven) | B-PT-complete · **OPEN (BLOQUEADOR 6)** |
| **R7** | `CountryProfile.translit_policy` (alfabetos no-latinos) | B-JP-normalize · **OPEN (deuda neta, gated)** |
| **R8** | `registral` desde `CountryProfile.reg_authorities` + marcar pata ausente | B-JP-VAM |
| **R9** | Taxonomía `DEALER_KINDS`/segment por país | B-PT-capture · sealing-hole-3 · missing-6 |
| **R10** | `ORTHOGONAL_LISTS` extensible por país | sealing-hole-6 · missing-3 |
| **R11** | `no_anchor` explícito en el veredicto de sello | sealing-hole-4 |

### Roturas (breaks) — 8/8 integradas
1. **[CRITICAL · DE] GeoResolver ciego al país** [VERIFIED `geo.py:153,157`]. Cargado DE, su provincia `'28'` resuelve contra municipios de Madrid (ES) → `municipality_code` erróneo acuñado en `cdp_code`, append-only, IRREVERSIBLE. El CHECK `chk_entity_muni_province` está relajado para no-ES (`0053:170-174`), así que ni lo atrapa. → **Resolución R2**: `WHERE country_code=$1` en ambas queries + arg `country_code`. Gate bloqueante ANTES de cargar el 2º país (un mint erróneo no se revierte). Cierra para DE/FR/IT/PT.
2. **[CRITICAL · DE] La orquestación nunca pasa el país** [VERIFIED `discover.py:91-93`, 0 hits `country_code`]. Todo dealer alemán se acuña `CDP-ES-`. `codes.py` es paramétrico (`:53`) pero su único call-site del pipeline no lo ejerce. → **Resolución R1**: `adapter.country_code` → `cdp_code(...,country_code=cc)` + columna en el INSERT. Una vez enhebrado, el bucle por-entidad es de verdad invariante. Cierra para todo país.
3. **[HIGH · FR] La forma del código INE está horneada** [VERIFIED `geo.py:204-206` `zfill(2)`, `:101-104` `muni_code[:2]`]. Córcega `'2A'/'2B'` no es dígito (→ rama de nombre → miss → SKIP), los DOM `971-976` son 3 díg, el INSEE de 5 chars tiene departamento `2A/2B`. → **Resolución R3**: `CountryProfile.code_shape` parametriza ancho/forma; `province_code()` y el gazetteer-loader lo consumen. FR provee su `code_shape` (acepta `2A/2B`, deriva DOM de 3). Cierra para FR; DE (AGS-8) e IT (provincia 2-letras) por la misma vía.
4. **[CRITICAL · IT] `bucket_for` falla en ABIERTO hacia MKT** [VERIFIED `lists.py:65-74`]. Registro Imprese/PRA/UNRAE caen a MKT SIN error → la lista ortogonal autoritativa del país DESAPARECE de la matriz → `coverage_lower` sobre un set oculto-incompleto → **sello falso**. → **Resolución R4**: el adaptador declara `orthogonal_bucket`; `bucket_for` lo lee. Además **falla en CERRADO**: un `source_key` sin bucket declarado **lanza**, no cae a MKT en silencio (ver sealing-hole-1). Cierra para IT/DE/FR/PT.
5. **[HIGH · PT] Identidad ES-dura por DOBLE costura** [VERIFIED `complete.py:73` `_PROVINCE_RE` 01-52 + `:89` `_CDP_CODE_RE` `^CDP-ES-`]. G1 IDENTITY falla para todo distrito/código portugués → ninguna entidad PT alcanza COMPLETED. El diseño solo nombró `:89` (el xfail); `:73` es una 2ª regex que el golden NO vigila. → **Resolución R6 (OPEN ITEM, BLOQUEADOR 6)**: ensanchar `_CDP_CODE_RE` a `^CDP-([A-Z]{2})-` (superconjunto estricto, acepta todo `CDP-ES-` vigente) + hacer `_PROVINCE_RE`/`_NATIONAL_KINDS` table-driven desde `geo_province`. **Causa de apertura**: el ensanche es un cambio de código pendiente; el xfail(strict) (`test_country_golden.py:286-290`) lo vigila y auto-flip a XPASS al ensancharse. **Gating**: hasta el commit de ensanche + quitar el xfail, ninguna entidad no-ES completa. Diseño cerrado, ejecución pendiente.
6. **[CRITICAL · JP] Normalización no-latina aniquila la identidad** [VERIFIED `codes.py:29-32` NFKD+ascii-ignore, `geo.py:51-53` ídem]. `'株式会社トヨタ'` → `''` → `canonical_key` colapsa a `name:|{muni}` idéntico → **fusión masiva cross-entity** en un `cdp_code`; geo por `''` → 100% SKIP. → **Resolución R7 (OPEN ITEM, deuda neta)**: `CountryProfile.translit_policy` (latino: identidad byte-idéntica al actual; no-latino: romanización determinista —p.ej. ICU/pykakasi— o capa-2 IA-local). **Causa de apertura**: requiere una romanización real + golden por script; para JP/CJK la calidad determinista es dudosa y puede exigir capa-2 (gate GPU €>0, firma owner). **Gating**: no-UE no-latino NO se onboardea hasta tener `translit_policy` probada por golden. Latino (DE/FR/IT/PT) NO afectado.
7. **[HIGH · MX] La matriz MSE es ciega al país** [VERIFIED `capture.py:72,88` `WHERE kind IN DEALER_KINDS`, 0 hits `country`]. El estado `'28'` de México y la provincia `'28'` (Madrid) se MEZCLAN; el roll-up nacional suma N̂ de ambos (`seal.py:84-107`). No existe denominador sellado por-país. → **Resolución R5**: migración aditiva `country_code` en `discovery_capture`/`exhaustiveness_estimate` + tupla de estrato `(country,province,segment)` + `_fetch_raw WHERE e.country_code=$1`. Matemática intacta. Cierra para todo país.
8. **[MEDIUM · JP] La familia `registral` del VAM lleva nombres ES** [VERIFIED `verify.py:48`]. RPPC/SAT/JSIC no casan → familia `'other'` → independencia debilitada; y la mayoría de países no-ES carecen de un `declared_count` tipo DGT → el VAM cae a `db==http` (2 familias) **sin marcar** que falta la pata registral. → **Resolución R8**: `registral` derivado de `CountryProfile.reg_authorities`; cuando no hay oráculo registral, **marcar explícitamente** `registral_absent=true` en el veredicto (no certificar TRUSTWORTHY como si la 3ª pata existiera). Cierra el silencio; la cobertura registral real depende del pack del país.

### Pack faltante (missing_pack) — 8/8 integradas
| # | Falta | Resolución |
|---|---|---|
| 1 | Loader GeoResolver country-scoped + filas geo etiquetadas | **R2** (parte del CountryProfile + paso onboarding 2). Cerrado por diseño. |
| 2 | Adaptador de **forma de código** por país (FR 2A/2B, DOM 3-díg, DE AGS-8, IT 2-letras) | **R3** `CountryProfile.code_shape`. Cerrado por diseño. |
| 3 | Mapa `source_key→bucket` por país + buckets ORTOGONALES nuevos | **R4** (declarado en adaptador) + **R10** (`ORTHOGONAL_LISTS` extensible). Cerrado por diseño. |
| 4 | Política de transliteración para alfabetos no-latinos | **R7** `translit_policy`. **OPEN ITEM** (gated, ver break-6). |
| 5 | Validadores `complete.py` por país (AMBAS regex + `_NATIONAL_KINDS`) | **R6**. **OPEN ITEM** (BLOQUEADOR 6, ver break-5). |
| 6 | Taxonomía de tipos de dealer del país → `DEALER_KINDS`/segment | **R9**: `_fetch_raw WHERE kind IN DEALER_KINDS` tira tipos foráneos (`capture.py:72,88`); el enum de 9 (`capture.py:19-29`) debe ser table-driven por país. Cerrado por diseño; ejecución con el roster de cada país. |
| 7 | Extracto de censo/triangulación por país + mapeo de clasificación (NACE/WZ/NAF/SCIAN/JSIC→segment) | Pack §6 + **R11**. Cerrado por diseño (opcional al inicio → `no_anchor` marcado). |
| 8 | Alcance de país en orquestación y tablas operativas (`source_health`/`harvest_run`/advisory-lock/`discovery_capture.build`) | **R1**+**R5**. El advisory lock `0x43415244(+1)` es global; para concurrencia cross-país sin contención se compone con `country_code` (lock por `(país,vector)`). Cerrado por diseño. |

### Agujeros de sellado (sealing_holes) — 7/7 integradas
1. **`bucket_for` falla en ABIERTO** [VERIFIED `lists.py:65-74`] → el sello MSE se computa sobre un set oculto-incompleto y puede certificar TRUSTWORTHY mientras falta la lista más fuerte del país. → **R4**: con bucket declarado en el adaptador, un `source_key` sin bucket **lanza** (fail-closed); imposible descartar una lista ortogonal en silencio.
2. **Matriz de captura ciega al país** [VERIFIED `capture.py` 0 hits `country`] → estratos `'28'` ES/CC se fusionan; roll-up suma cross-país. → **R5**. Denominador sellado por-país.
3. **`WHERE kind IN DEALER_KINDS` tira tipos foráneos** [VERIFIED `capture.py:72,88`] → esas entidades nunca entran a `n_obs` → `coverage_lower` SOBRESTIMA. → **R9**: `DEALER_KINDS` table-driven por país.
4. **Triangulación opcional → `no_anchor` silencioso** [VERIFIED `triangulation.py:51-52,72-73`] → un país sin su CSV produce `national sealed=True` SOLO con captura-recaptura, saltándose el único cross-check externo. → **R11**: `no_anchor` se **propaga al veredicto de sello** como `external_anchor=absent`; el sello nacional sin ancla externa se marca explícitamente (no se vende como verificado por 3 vías). Cierra el silencio; el ancla real depende del pack §6.
5. **G1 rechaza-duro todo código no-ES** [VERIFIED `complete.py:73,89`] → ninguna entidad no-ES alcanza COMPLETED; el xfail solo vigila `:89`, no `:73`. → **R6**. **OPEN ITEM** (BLOQUEADOR 6).
6. **`ORTHOGONAL_LISTS` fijo en 7 buckets sabor ES** [VERIFIED `lists.py:49`] → un país con un set distinto de mecanismos ortogonales no puede expresarlo sin editar el motor. → **R10**: `ORTHOGONAL_LISTS`/`LIST_METADATA` derivables por país (el conjunto de buckets es parte del pack, no del motor). Cerrado por diseño.
7. **La vara probatoria del VAM baja en silencio sin oráculo registral** [VERIFIED `verify.py:42-50` + `discover.py:159-164`] → cuórum se apoya en `db==http` sin marcar la pata registral ausente. → **R8**: marcar `registral_absent`. Cierra el silencio.

**Síntesis del veredicto:** de 8 breaks + 8 missing + 7 holes, **21/23 se cierran por diseño** (R1–R5, R8–R11) sin tocar ES; **2 quedan OPEN con causa y gating** declarados: R6 (BLOQUEADOR 6, ensanche `complete.py`, diseño cerrado / commit pendiente, xfail lo vigila) y R7 (transliteración no-latina, deuda neta que puede exigir capa-2 GPU €>0). El motor de Descubrir **NO es genérico aún por debajo del esquema**; lo será cuando R1–R5 estén enhebrados y verificados contra DB viva.

---

## Sub-proyectos institucionales (360 por faceta)

> **Qué es esta sección.** La etapa Descubrir descompuesta en sus **40 átomos de código** (F01–F40), cada uno tratado como un proyecto institucional independiente con su **deep-spec verificado** (mecanismo al átomo) + **costura** ES→genérico + **fix** exacto + **adversarial** concreto + **sellado** multi-vía + **herramienta NEXT-LEVEL €0**. Es el mismo sistema del §Veredicto visto por **autoridad-de-código** en vez de por **síntoma**: las roturas (8 breaks + 8 missing + 7 holes) viven distribuidas en estas 40 facetas y mapean a los fixes raíz **R1–R11**. «360» = tratamiento de 360° por faceta (círculo completo), no 360 facetas.

> **Cómo leerla (funnel).** Cada faceta es autocontenida: salta por la [tabla de familias](#navegación-funnel), lee el **Deep-spec** para el mecanismo verificado y baja a Costura→Fix→Adversarial→Sellado→Herramienta. Todo `path:linea` es `[VERIFIED]` leído de la fuente; los `[ASSUMED]` y open-items se marcan con su causa. **Honestidad cruda: nada se transcribe como sano si el código dice lo contrario.** Stack vivo CAÍDO (PG `:5433/:5434`) → toda cifra DB es punto-en-el-tiempo, no entero eterno.

> **Modelo de render.** **28** facetas autocontenidas portan su propio bloque `(a)`–`(f)` (verificación · mecanismo · costura+fix · adversarial · sellado · herramienta); **12** facetas magras (F07–F12, F19–F24) llevan el mecanismo en `(a)`–`(b)` y su costura/fix/adversarial/sellado/herramienta en los bloques `(c)`–`(f)` que siguen. Estructura idéntica en las 40 para que nadie se pierda.

---

### Familia A · Frontera de normalización (contrato · DTO · registro)

---

<a id="f01"></a>

#### F01 · Contrato SourceAdapter (frontera de normalizacion)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `pipeline/sources/base.py:29-40` [VERIFIED]: `class SourceAdapter` con `source_key: str = "base"` (:33), `declared_count(self) -> int | None` que retorna `None` (:35-37, el oraculo de cuenta del VAM), y `fetch(self) -> list[DiscoveredEntity]` que lanza `NotImplementedError` (:39-40). **No existe** ningun atributo de clase `country_code` ni `orthogonal_bucket** en el contrato.
- DTO asociado en `base.py:7-26` [VERIFIED]: `@dataclass DiscoveredEntity` de 18 campos; `province_name`/`municipality_name` documentados como *raw, resolved to INE code at ingest* (:16-17).

**(b) Mecanismo al atomo**
ABC-por-convencion (clase plana con `NotImplementedError`, no `abc.ABC`). Tres superficies y solo tres: (1) **identidad de fuente** `source_key`; (2) **oraculo de cuenta** `declared_count()` que alimenta la familia de path `source` del quorum VAM; (3) **grifo de datos** `fetch()` que emite `list[DiscoveredEntity]`. Toda fuente de todo pais colapsa a este trio. `discover()` instancia el adaptador, llama `fetch()` para las filas y `declared_count()` para el path declarado del VAM. La clasificacion de bucket MSE la hace **aguas abajo** `lists.bucket_for(source_key)` leyendo la cadena del key, NO un atributo de clase.

**(c) Costura ES->generico + fix exacto**
- **Costura:** el contrato no porta dimension pais ni dimension bucket-MSE. En cuanto un `DiscoveredEntity` entra a `discover()`, el pais se pierde (discover asume ES) y `lists.bucket_for` clava sobre el `source_key` pelado -> cae a MKT (excluido).
- **Fix:** anadir dos atributos de clase al contrato — `country_code: str = "ES"` y `orthogonal_bucket: str | None = None` (junto a `base.py:33`). `discover()/_upsert` leen `adapter.country_code` para enhebrar pais en geo-scope/mint/INSERT; `lists.bucket_for` lee `adapter.orthogonal_bucket` (o `_EXACT` por pais) en vez de adivinar del key. ES byte-identico porque el default es `"ES"` y el bucket por defecto preserva el `_EXACT` actual.

**(d) Riesgo adversarial concreto**
Un roster extranjero (adaptador DE Handelsregister) hereda el contrato pero, sin `country_code`, discover() acuna `CDP-ES-` para concesionarios alemanes (irreversible) y `bucket_for` tira su lista autoritativa a MKT (fuera del MSE) -> el pais entra sin identidad de pais NI de mecanismo de captura. Dos paises con un `source_key` generico (`'osm'`, `'overture'`) colisionan en el dict ADAPTERS (faceta 3): la ausencia de namespace de pais en el contrato es la raiz.

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** un adaptador foraneo hereda el contrato y declara su pais/bucket SIN cambiar la firma de `fetch`/`declared_count` ni la CLI.
- **Via 1 (unit):** stub adaptador DE con `country_code='DE'` -> discover lo enruta a `CDP-DE-` y a un bucket no-MKT.
- **Via 2 (golden):** todos los adaptadores ES intactos -> `country_code` resuelve 'ES', cdp_code byte-identico.
- **Via 3 (adversarial/tipada):** un guard Pydantic en CI asevera la biyeccion `source_health<->registry<->bucket` por pais activo = 0 UNMAPPED / 0 ORPHAN; un adaptador sin declaracion rompe el build en ROJO.

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**Pydantic** — Guard de drift de registry/semilla como CONTRATO TIPADO en CI [NEXT-LEVEL.md:584-591 VERIFIED]. URL https://github.com/pydantic/pydantic (MIT, EUR0). Modela el country-pack (country.toml + registry + semillas + lock_key) como esquema Pydantic; el test CI itera `active_countries()` y falla si la biyeccion no cierra. Convierte el hueco silencioso de onboarding en build ROJO mecanico, corre sin DB viva (fixtures). Alternativas: Frictionless (contrato de los ficheros del pack), jsonschema, Cerberus.

---

<a id="f07"></a>

#### F07 · DTO DiscoveredEntity (18 campos, geo cruda)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED pipeline/sources/base.py:7-26].** `@dataclass DiscoveredEntity` declara exactamente 18 campos: `kind`(:9), `source_key`(:10), `source_ref`(:11), `legal_name`(:12), `trade_name`(:13), `cif`(:14), `cnae`(:15), `province_name`(:16), `municipality_name`(:17), `address`(:18), `postcode`(:19), `lat`(:20), `lon`(:21), `phone`(:22), `email`(:23), `website`(:24), `is_tier1`(:25), `extra`(:26). El invariante geo-cruda esta LITERAL en el codigo: el comentario de `province_name`(:16) dice "raw, resolved to INE code at ingest" -> los nombres viajan crudos y se resuelven a codigo en ingest, nunca pre-resueltos. El comentario de `kind`(:9) enumera tipos ES ("concesionario_oficial|compraventa|garaje|desguace|plataforma|cadena"). El contrato base `SourceAdapter` (base.py:29-40) consume estos DTO via `fetch()->list[DiscoveredEntity]`.

**(b) Mecanismo al atomo.** El DTO es un contenedor pasivo sin logica: cada `SourceAdapter.fetch()` (base.py:39) emite `list[DiscoveredEntity]` y `discover()` los consume uno a uno. Dos campos son taxonomia ES horneada: (1) `kind` es el enum de 9 tipos que mas abajo el MSE filtra DURO en `capture._fetch_raw` con `WHERE kind IN DEALER_KINDS`; (2) `cnae` es la clasificacion de actividad espanola que alimenta la triangulacion CNAE-451. `province_name`/`municipality_name` crudos son CORRECTOS por diseno (la resolucion es responsabilidad de `_upsert`->GeoResolver), pero el contrato NO porta `country_code`: una fila emitida no sabe de que pais es, y esa informacion se reconstruye mas tarde leyendo `adapter.country_code` (costura de la faceta 1 SourceAdapter). El DTO es el cuello por donde pasa el 100% del censo; un campo ES-especifico horneado obliga a cada pais a forzar su realidad al molde espanol. La inmutabilidad aguas abajo (cdp_code) convierte cualquier kind mal-clasificado en un sesgo permanente del estrato `segment`.

**(c) Costura ES→genérico.** El DTO hornea taxonomia ES en dos campos: `kind` (enum de 9 tipos espanoles, base.py:9) y `cnae` (clasificacion CNAE espanola, base.py:15). No existe un campo de categoria neutral ni un mapa categoria-fuente->kind por pais. Un dealer extranjero cuyo tipo real no encaje en el enum de 9 entra con un `kind` forzado o invalido, y `cnae` queda vacio o mal-mapeado. El DTO tampoco porta `country_code` (lo reconstruye discover() leyendo el adaptador).

**Fix exacto.** Anadir al DTO un campo `raw_category: str|None` (la categoria tal cual la declara la fuente) y trasladar la traduccion categoria->kind a un hook del perfil de pais `country.kind_for(raw_category, source_key)->str`, con el enum `DEALER_KINDS` pasando a ser table-driven por pais (no un literal). `cnae` se generaliza a `activity_code` con su esquema declarado en el perfil (CNAE-ES, NACE, WZ-DE, ATECO-IT). El DTO sigue siendo de 18+ campos pero ninguno asume Espana; ES queda como el perfil #1 que reproduce el enum actual byte-identico (golden).

**(d) Riesgo adversarial concreto.** DE/FR/IT/PT: un `Autohaus`/`garage`/`autosalone`/`stand` cuyo tipo no mapea al enum de 9 -> `_fetch_raw` lo tira en `WHERE kind IN DEALER_KINDS` (capture.py) -> el dealer extranjero DESAPARECE del denominador MSE sin error -> coverage_lower SOBREESTIMA la cobertura (denominador mutilado). `cnae` ES-only descoloca la triangulacion CNAE-451 para cualquier pais con otra clasificacion (NACE G45). No-UE/ruido: una fuente que emite `kind` de texto libre contamina el eje `segment` del estrato aguas abajo; un kind vacio cae fuera del enum y se pierde silenciosamente.

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) golden ES byte-identico — el perfil ES produce el mismo `kind` para los 26 adaptadores actuales (cero re-mapeo). (2) Contrato de datos sobre el DTO: cada fila emitida valida los 18 campos y `kind in DEALER_KINDS[country]` o falla CERRADO en emision (no silenciosamente en `_fetch_raw`). (3) Cross-check: para un pais nuevo, el conteo de filas con `kind` valido == filas emitidas (0 caidas silenciosas por kind fuera de enum), verificado contra `declared_count()` del adaptador (oraculo VAM).

**(f) Herramienta NEXT-LEVEL (€0).** **Frictionless Framework (Table Schema)** — MIT, EUR0 [VERIFIED https://github.com/frictionlessdata/frictionless-py] (NEXT-LEVEL.md:337, cluster geo 'Country-pack como CONTRATO de datos auto-verificado'). Declara el DTO emitido como un Table Schema versionado con tipos + enum country-scoped de `kind`/`activity_code`, validado ANTES del INSERT: un kind fuera del enum del pais FALLA la validacion con diagnostico claro en vez de evaporarse en `_fetch_raw`. Complementos: **Pandera** (MIT) como contrato-unit-test del dato, y **Pydantic** (MIT, NEXT-LEVEL.md:587 'Guard de drift de registry como CONTRATO TIPADO') si se promueve el dataclass a modelo tipado con validador en la frontera. Eleva la regla 'el contrato porta el pais y su taxonomia' de prosa a invariante mecanico fail-closed (doctrina COUNTRY-PROOF).

---

<a id="f13"></a>

#### F13 · Registro ADAPTERS + dispatch CLI

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/discover.py:48-74] `ADAPTERS: dict[str, type[SourceAdapter]]` literal con **exactamente 25 entradas** (conte: dgt_cat, oem_kia, oem_mg, oem_byd, oem_skoda, oem_dacia, oem_hyundai, oem_mercedes, oem_seat, osm, aedra, acevas, aecs, autocasion_census, motor_es_census, ocasionplus_census, flexicar_census, overture, dork_municipal, borme_cnae, axesor_cnae, graph_recursive, paginas_amarillas, autoscout24_census, collapse_invisible). El insumo dice "25"; **coincide**.
- [VERIFIED pipeline/discover.py:117-118] `discover()` despacha `adapter = ADAPTERS[source_key]()` — instancia O(1) por clave.
- [VERIFIED pipeline/discover.py:170-175] `main()` toma `sys.argv[1]` (default 'dgt_cat'), valida `if key not in ADAPTERS` -> `print(... available: {list(ADAPTERS)})` + `sys.exit(2)`.
- [VERIFIED pipeline/sources/base.py:29-37] `SourceAdapter` declara SOLO `source_key` + `declared_count()` + `fetch()`. **NO existe `country_code` ni `orthogonal_bucket`** -> la costura del insumo esta confirmada al byte.

**(b) Mecanismo al atomo**
`ADAPTERS` es una tabla plana de despacho a nivel modulo, construida importando 25 clases concretas (discover.py:20-42) y ligando cada una a su `source_key` string. Es el UNICO punto de traduccion nombre->clase: `discover()` hace lookup directo, `main()` valida pertenencia. No hay dimension pais en ninguna parte: la clave es global y plana.

**(c) Costura ES->generico**
No existe `ADAPTERS_BY_COUNTRY`. Para que el scheduler targetice "todos los vectores de CC" hay que derivarlo agrupando por `cls.country_code` — pero la clase NO porta `country_code` (base.py:33 solo `source_key`). La costura es doble: (1) anadir el atributo de clase a `SourceAdapter`; (2) derivar `ADAPTERS_BY_COUNTRY[cc] = {sk: cls for sk, cls in ADAPTERS.items() if cls.country_code == cc}`.

**(d) Riesgo adversarial concreto**
**Colision silenciosa de clave.** `osm` y `overture` son fuentes GLOBALES; DE/FR/IT querran reusar esos mismos source_key. Un dict literal de Python con clave repetida **conserva la ULTIMA** sin error: `ADAPTERS = {'overture': EsOverture, ..., 'overture': DeOverture}` deja el adaptador ES inalcanzable, sin traza. Un roster extranjero que reuse 'osm'/'overture' pisa ES en el despacho. Es exactamente la violacion COUNTRY-PROOF: dos paises con el mismo source_key generico colapsan.

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** anadir un pais = anadir entradas, sin tocar `discover()` ni `main()`.
- via1: test asserta `len(ADAPTERS)` claves globalmente unicas Y `ADAPTERS_BY_COUNTRY['ES']` == las 25 ES (golden de conteo).
- via2: biyeccion — cada valor tiene `cls.country_code` seteado y aparece bajo su bucket de pais.
- via3: disjuntez cross-pack — ningun source_key bajo dos paises salvo namespacing; un duplicado adversarial -> build ROJO.
- via4: CLI golden — `discover ES:osm` corre solo el OSM de ES; `discover bogus` -> exit(2) inalterado.

**(f) Herramienta de nivel inalcanzable**
**Pydantic** (guard de drift de registry/semilla como CONTRATO TIPADO en CI). Modela el country-pack (country.toml + registry + semillas + lock_key) como esquema Pydantic; un test CI asevera la biyeccion `source_health<->registry<->lock_key` por pais activo = 0 UNMAPPED / 0 ORPHAN, y el guard de disjuntez bloquea source_key duplicado entre packs. Convierte el hueco silencioso (hoy solo visible en un `--dry-run` manual, scheduler.py:394 `_gap_report`) en un build ROJO mecanico. [VERIFIED NEXT-LEVEL.md:584-590] MIT, EUR0, https://github.com/pydantic/pydantic

### Familia B · Resolución geográfica (cascada · índice · provincia · fallbacks)

---

<a id="f02"></a>

#### F02 · Cascada municipality_code (dispatcher + exacto)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `pipeline/geo.py:209-234` [VERIFIED]: `municipality_code(self, province_code, muni_name)`. Guarda: `None` si falta provincia o nombre (:218-219). **Scope estricto:** `d = self._muni.get(province_code, {})` (:221) — diccionario province-local, jamas cross-province. Paso 1 exacto: `d.get(_norm(muni_name)) or d.get(_sorted_key(muni_name))` (:224). Paso 2 fuzzy: `self._fuzzy_match(province_code, muni_name)` (:229). Paso 3 locality: `self._locality_match(province_code, muni_name)` (:234).
- Helpers [VERIFIED]: `_norm` (:51-53) = NFKD + `encode('ascii','ignore')` + lower + colapso de no-alfanumerico a espacio + strip; `_sorted_key` (:56-57) = token-sort de `_norm` (asi 'Rioja, La' == 'La Rioja'). `_fuzzy_match` (:240-299): tier A token-subset ambiguity-safe (:265-274), tier B rapidfuzz `WRatio>=_FUZZY_CUTOFF` (=88, :32; :276-299) con guardas `_FUZZY_QUERY_MIN_LEN=4` (:37), `_FUZZY_CAND_LEN_FLOOR=4`/`_DIVISOR=3` (:42-43). `_locality_match` (:301-314): gazetteer, `>1` municipio -> `None`.

**(b) Mecanismo al atomo**
Cascada de 3 tiers con corto-circuito, CADA tier scoped al unico dict `self._muni[province_code]`. **Tier 1 (exacto):** dos claves — `_norm` (acento/caso-insensible) y `_sorted_key` (orden-insensible). **Tier 2 (fuzzy):** primero token-subset (query cuyos tokens son subconjunto de EXACTAMENTE 1 municipio -> match de prefijo confiado; subconjunto de >=2 -> ambiguo -> `None`, 'mejor un hueco que una mentira'), luego WRatio>=88 solo si NO es subconjunto de ninguno. **Tier 3 (gazetteer):** resuelve pedanias/barrios, `None` si la localidad mapea a >1 municipio. Devuelve el primer tier que acierta o `None` honesto.

**(c) Costura ES->generico + fix exacto**
- **Costura:** el dispatcher en si es ORQUESTACION country-agnostica y NO tiene literal ES propio; pero hereda el indice de `GeoResolver.load` (faceta 6) y la forma-de-nombre de `_norm`/`_sorted_key`/WRatio (faceta 12 + faceta 9), todos calibrados al latino-ES. Su correccion es rehen de (i) que el `province_code` venga bien resuelto y country-scoped aguas arriba, y (ii) que `_norm` no vacie nombres no-latinos a `''`.
- **Fix:** cero cambios en el cuerpo del dispatcher. El fix vive en sus dependencias — country-scope del indice `_muni` en el load (faceta 6, `WHERE country_code`) e insertar transliteracion/parse por pais ANTES de `_norm` (faceta 12) para que el nombre no-latino sobreviva al tier exacto. Opcional: alimentar el dispatcher con un `city` ya tipado por libpostal en vez de un blob de tokens crudo.

**(d) Riesgo adversarial concreto**
Si la provincia viene de un resolver no-scoped (bleed faceta 6/7), el municipio se resuelve contra el set de la provincia EQUIVOCADA (DE '28' contra municipios de Madrid) -> `municipality_code` erroneo acunado en un cdp_code inmutable. Nombres no-latinos ('Yokohama' en kanji) -> `_norm` -> `''` -> nunca casan ninguno de los 3 tiers -> 100% SKIP honesto (sin mint falso, pero cobertura cero). El scope estricto a provincia es la red de seguridad; romperlo aguas arriba propaga el error al mint.

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** dado un `province_code` valido, el municipio resuelve por el primer tier que acierta o devuelve `None` honesto — nunca cross-province, nunca falso positivo.
- **Via 1 (golden ES):** corpus ES resuelve byte-identico.
- **Via 2 (adversarial):** un nombre ambiguo entre dos municipios de la provincia devuelve `None` (guarda token-subset), probado por la probe B4.1 de 0 FP [geo.py:255 VERIFIED].
- **Via 3 (ortogonal):** el `city`/`state` parseado por libpostal sobre el mismo texto crudo debe converger con la salida del resolver; divergencia = hueco confesado, no merge [NEXT-LEVEL.md:348 VERIFIED].

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**libpostal** — Parsing/normalizacion de direcciones multilingue (entrenado, no regex curado) [NEXT-LEVEL.md:342-349 VERIFIED]. URL https://github.com/openvenues/libpostal (MIT, EUR0). Parser estadistico entrenado en 1B+ direcciones, 60+ idiomas, devuelve componentes etiquetados (road/city/state/postcode/country) y alimenta `GeoResolver.municipality_code(province, city)` con campos tipados country-agnosticos, retirando el troceo ES-shaped. Alternativas: pypostal (binding), Pelias parser. Se acopla con AnyAscii (faceta 12) para el identity-path no-latino.

---

<a id="f08"></a>

#### F08 · Matcher fuzzy de municipio (rapidfuzz + guardas)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED pipeline/geo.py:240-299].** `_fuzzy_match(province_code, muni_name)` implementa dos tiers province-scoped. Constantes [VERIFIED geo.py:32,37,42-43]: `_FUZZY_CUTOFF=88`, `_FUZZY_QUERY_MIN_LEN=4`, `_FUZZY_CAND_LEN_FLOOR=4`, `_FUZZY_CAND_LEN_DIVISOR=3`. Tier A token-subset [VERIFIED :265-274]: `query_tokens <= set(key.split())`; si `len(supersets) >= 2` -> `return None` (:272, "ambiguous short form -> confess the gap"); si `== 1` -> match unico (:274). Tier B WRatio [VERIFIED :276-299]: `from rapidfuzz.process import extractOne` con `ImportError: return None` (:280-281), filtro de candidato `len(key) >= max(_FLOOR, len(query)//_DIVISOR)` (:283), `extractOne(..., scorer=WRatio, score_cutoff=_FUZZY_CUTOFF)` (:292-295). El docstring (:255) cita la probe B4.1 con 0 falsos positivos.

**(b) Mecanismo al atomo.** El matcher resuelve variantes ortograficas SIN inventar. La clave es el ORDEN: Tier A corre ANTES que el scoring porque WRatio rompe empates artificialmente por longitud — "WRatio cannot catch this" (:250-251) — asi que la ambiguedad genuina ('San Martin' subset de dos municipios) debe atraparla el test de subconjunto y confesar None. Tier B solo entra cuando el query NO es subconjunto de ningun municipio (formas mas ricas: 'Palma de Mallorca'->'Palma', 'Orense'->'Ourense'). Las tres guardas (query>=4, candidato>=max(4,len/3), score>=88) estan calibradas sobre nombres ES por la probe. `_norm` (:51-53, NFKD+ascii-ignore) normaliza ambos lados asumiendo alfabeto latino. Todo esta scoped a `province_code`: el matcher nunca cruza provincia. Un falso positivo aqui mintea un `cdp_code` con muni erroneo, INMUTABLE y append-only — de ahi que la guarda de ambiguedad sea la red de seguridad ('mejor un hueco que una mentira').

**(c) Costura ES→genérico.** Dos costuras ES: (1) los umbrales (`_FUZZY_CUTOFF=88`, query>=4, candidato>=max(4,len/3)) estan calibrados por la probe B4.1 sobre nombres de municipio ESPANOLES; otro idioma/alfabeto cambia la distribucion de WRatio. (2) `_norm` hace NFKD+ascii-ignore (geo.py:51-53): un nombre no-latino normaliza a '' y nunca casa. El algoritmo de dos tiers es estructuralmente generico (token-subset + WRatio); solo los NUMEROS y el normalizador son Espana.

**Fix exacto.** Mover los cuatro umbrales a `country.fuzzy_profile` (cutoff, query_min_len, cand_floor, cand_divisor) re-calibrados por una probe por pais sobre su backbone de municipios; e insertar el transliterador del perfil (faceta de normalizacion) ANTES de `_norm` para que alfabetos no-latinos produzcan tokens comparables. El algoritmo de dos tiers no cambia (la guarda de ambiguedad es invariante); solo se inyectan datos. ES queda byte-identico reusando la probe B4.1 como golden.

**(d) Riesgo adversarial concreto.** DE: ascii-ignore destruye la 'ss' de eszett ('Strasse' vs 'Strasse') desalineando el score. FR/IT/PT: diacriticos y formas bilingues re-calibran WRatio — umbral 88 ES puede dar demasiados FP (muni erroneo INMUTABLE) o demasiados miss (SKIP masivo). No-UE/CJK: nombres no-latinos -> '' -> 100% miss -> SKIP total. Operativo: `rapidfuzz` ausente -> `ImportError` -> Tier B desaparece SIN aviso (:280-281), degradando a solo-token-subset en silencio. Ruido: un municipio con nombre de 3 chars queda bajo `_FUZZY_QUERY_MIN_LEN` y nunca entra a fuzzy.

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) 0 falsos positivos en el set del pais (espejo de la probe B4.1 que certifica ES). (2) La ambiguedad genuina (subconjunto de >=2 municipios) SIEMPRE devuelve None — golden adversarial con 'San Martin'-equivalentes del pais. (3) Determinismo: misma entrada -> mismo codigo (WRatio es deterministico). (4) Guard de dependencia: un test asevera que `rapidfuzz` esta presente en el entorno de mint, de modo que Tier B no degrade en silencio.

**(f) Herramienta NEXT-LEVEL (€0).** **datasketch (MinHash-LSH) + RapidFuzz** — MIT, EUR0 [VERIFIED https://github.com/ekzhu/datasketch] (NEXT-LEVEL.md:538, cluster identity-vehicle 'Scalable, language-neutral fuzzy blocking'). MinHash-LSH sobre n-gramas de caracter da blocking sub-cuadratico y LANGUAGE-NEUTRAL (cualquier escritura) que retira la dependencia del umbral ES, con RapidFuzz (ya en uso) para la comparacion fina intra-bloque. Complementos del cluster geo: **AnyAscii** (ISC, NEXT-LEVEL.md:329/482) para transliteracion no-destructiva ANTES del fold, y **libpostal** (MIT, NEXT-LEVEL.md:345) para segmentar el nombre antes de matchear. Eleva el matcher de 'umbrales ES por probe' a 'blocking neutral de idioma + comparacion calibrada por pais'.

---

<a id="f14"></a>

#### F14 · Gazetteer INE Nomenclator (localidades)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/geo.py:46-48] `_GAZETTEER_PATH = Path(__file__).resolve().parent.parent / 'data' / 'geo' / 'nomenclator_entidades_ine.csv'` — ruta **hardcoded** al CSV INE.
- [VERIFIED pipeline/geo.py:76-127] `_load_gazetteer()`: si `not _GAZETTEER_PATH.exists()` -> `return index` vacio (**non-fatal**); `csv.DictReader`; `muni_code = row['municipio_id'].strip()`, `if len(muni_code) != 5: continue` (**ancho 5 horneado**); `prov_code = muni_code[:2]` (**coding INE 2+3 asumido**); por campo `('entidad_singular_nombre','nucleo_nombre')` normaliza, salta `'diseminado'`, **acumula en `set`** por (prov, key).
- [VERIFIED pipeline/geo.py:301-314] `_locality_match(province_code, locality_name)`: `loc_index = self._locality.get(province_code, {})`; `codes = loc_index.get(_norm(...)) or loc_index.get(_sorted_key(...))`; `if codes and len(codes) == 1: return next(iter(codes))`; else `None` — **guarda de ambiguedad** ("better a hole than a lie").

**(b) Mecanismo al atomo**
Tercer tier de resolucion geo, scoped a provincia. Tras fallar exacto (tier1) y fuzzy (tier2), `_locality_match` busca pedanias/parroquias/barrios en el indice `dict[prov_code][locality_norm_key] -> set[muni_code5]` (geo.py:133 `_locality`). El indice se construye UNA vez al cargar desde un CSV de ~63k filas. Tres invariantes: (1) ancho `muni_code5` horneado (`len != 5 -> skip`) y `prov = muni_code[:2]`; (2) un nombre que mapea a >1 municipio devuelve `None` (jamas liga arbitrario); (3) ausencia non-fatal (CSV faltante -> `{}` -> tier ausente, fuzzy sigue).

**(c) Costura ES->generico**
`_GAZETTEER_PATH` esta clavado al CSV INE (geo.py:46-48); el esquema de columnas (`municipio_id` de 5, `entidad_singular_nombre`, `nucleo_nombre`) es 100% INE-ES; `muni_code[:2]==provincia` asume el coding INE 2+3. Un pais necesita inyectar SU propio gazetteer via CountryProfile: `profile.gazetteer_path` + mapa de columnas + regla de ancho/slice L1, NO reusar el CSV INE.

**(d) Riesgo adversarial concreto**
Reusar el CSV INE para otro pais ata localidades ESPANOLAS a municipios extranjeros; una consulta DE contra el gazetteer ES o falla o, peor, false-resuelve un homonimo. El `len != 5 -> skip` **descarta en silencio** cualquier pais cuyo codigo municipal no sea de 5 chars (freguesia PT 6-dig, AGS DE 8-dig): el tier entero devuelve `{}` sin error, solo cobertura perdida. `muni_code[:2]` deriva una "provincia" erronea para cualquier coding no-2+3.

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** localidad ES resuelve byte-identico; localidades de CC resuelven solo contra SU gazetteer; ausencia degrada non-fatal.
- via1: ES golden — el indice ~63k actual resuelve las mismas localidades al mismo `muni_code5`.
- via2: aislamiento de pais — un gazetteer CC no produce codigos ES; una consulta ES nunca toca una localidad CC (assert prov-scoped).
- via3: ambiguedad preservada — localidad compartida por >1 muni sigue `None` para el nuevo pais.
- via4: non-fatal — borrar el CSV CC deja exacto/fuzzy vivos (sin crash).

**(f) Herramienta de nivel inalcanzable**
**GeoNames** (loader pan-pais + alternateNames). La capa de localidades sale de `allCountries.zip` (feature_class 'P' poblaciones + ADM3/ADM4) — un gazetteer GLOBAL que reemplaza el Nomenclator ES-only; un solo loader cubre todo pais, ES queda como adaptador degenerado (su fuente sigue siendo el dict INE). `alternateNamesV2.zip` auto-mina los nombres bilingues/exonimos/historicos de localidad que el CSV INE no escala a mano. [VERIFIED NEXT-LEVEL.md:374-388] CC-BY 4.0, EUR0, https://download.geonames.org/export/dump/

---

<a id="f20"></a>

#### F20 · Fallbacks de recuperacion geo + SKIP honesto

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** Cascada de ultimo recurso dentro de _upsert [VERIFIED pipeline/discover.py:80-90]:
- `prov = geo.province_code(e.province_name)`; `muni = geo.municipality_code(prov, e.municipality_name)` [VERIFIED :80-81].
- Recurso 1: `if not prov and e.municipality_name: prov, muni = geo.resolve_city_global(e.municipality_name)` [VERIFIED :82-84].
- Recurso 2: `if not prov and geocoder is not None: prov = geocoder.nearest_province(e.lat, e.lon)` [VERIFIED :85-87].
- SKIP honesto: `if not prov: return (False, False, False)` — NO mintea [VERIFIED :88-90]; traza por-entidad (name/province_name/municipality/source_ref) impresa en el bucle [VERIFIED :139-146].
- `resolve_city_global` [VERIFIED pipeline/geo.py:189-198]: devuelve (prov,code) SOLO si el indice `_city_global` tiene EXACTAMENTE 1 hit (`hits and len(hits)==1`); si no, (None,None) — guarda de unicidad nacional.
- `ProvinceGeocoder.nearest_province` [VERIFIED pipeline/geocode.py:89-100]: argmin de distancia equirectangular sobre centroides cargados de `SELECT lat,lon,province_code FROM entity WHERE ... province_code IS NOT NULL` [VERIFIED :80-83].

**(b) mecanismo al atomo + HALLAZGO.** La cascada es province -> city_global (unico nacional) -> geocoder (centroide mas cercano) -> SKIP. El SKIP es el sello anti-maquillaje: prefiere el hueco a inventar provincia y deja rastro debuggable de los 4 campos [VERIFIED :144-146], evitando que una perdida sistematica de geo sea irrecuperable sin re-fetch.

**HALLAZGO [VERIFIED] (corrige el code_hint de la faceta):** la constante `KNN_MAX_DISTANCE_KM=30.0` [VERIFIED geocode.py:49] guarda EXCLUSIVAMENTE a `MunicipalityGeocoder.nearest_municipality` (`if dist_km > KNN_MAX_DISTANCE_KM: return (None, dist_km)` [VERIFIED :191-192]). `ProvinceGeocoder.nearest_province` [VERIFIED :89-100] — la rama que _upsert realmente usa como Recurso 2 — NO tiene NINGUNA guarda de distancia: hace argmin y devuelve la provincia mas cercana de forma incondicional. Un lat/lon en CUALQUIER punto del planeta resuelve a la provincia ES mas proxima sin techo. La faceta atribuia el umbral 30km al geocoder de provincia; en el codigo real ese umbral NO protege esta rama.

**(c) Costura ES→genérico.** resolve_city_global usa `_city_global`, indice cargado SIN country_code (hereda el bleed de la facet GeoResolver); su guarda de unicidad nacional (`len(hits)==1` [VERIFIED geo.py:195]) deja de cumplirse al cargar un 2o pais. nearest_province usa centroides de la tabla entity sin filtro de pais [VERIFIED geocode.py:80-83] y SIN techo de distancia [VERIFIED :89-100]. El umbral 30km (ES: radio municipal max ~24km, racional documentado [VERIFIED :43-49]) es geografia espanola.

**Fix exacto.** (1) Scopear `resolve_city_global` y `ProvinceGeocoder.load` por country_code (WHERE country_code=$cc en el SELECT de centroides + indices country-keyed). (2) Anadir techo de distancia a `nearest_province` (HOY ausente): rechazar -> None si el centroide mas cercano supera el p99 del radio provincial del pais. (3) Derivar el umbral del GeoProfile por pais, no del literal 30.0. La doctrina SKIP se mantiene: sin provincia fiable -> hueco con traza, jamas invento.

**(d) Riesgo adversarial concreto.** DE/FR/IT/PT/no-UE: un POI extranjero con lat/lon pero sin provincia (p.ej. Overture sobre-captura S Francia/Portugal) entra al Recurso 2; `nearest_province` SIN guarda devuelve la provincia ES mas cercana aunque el punto este a 800km, y _upsert mintea un cdp_code 'CDP-ES-{prov}' INMUTABLE y append-only. Ciudad homonima en 2 paises ('Cordoba' ES/AR, 'Valencia' ES/VE, 'Leon' ES/MX) rompe la unicidad de resolve_city_global -> deja de resolver o resuelve al pais equivocado. Ruido: un lat/lon (0,0) o corrupto cae a la provincia mas cercana en vez de a SKIP.

**(e) Criterio de sellado + verificación multi-vía.** Sello: el SKIP deja rastro y nunca inventa provincia. Verificacion multi-via: (1) golden ES byte-identico antes/despues del scoping; (2) test adversarial de techo: alimentar nearest_province con un punto fuera del pais y assert que devuelve None (hueco) — HOY ESTE TEST FALLA (no hay guarda de distancia); (3) unicidad cross-pais: cargar ES+CC y assert que una ciudad homonima resuelve a su pais o confiesa (None,None); (4) auditar el log de SKIP: cada hueco trae los 4 campos de traza.

**(f) Herramienta NEXT-LEVEL (€0).** PostGIS (ST_Contains + GiST) sobre fronteras geoBoundaries CGAZ — datos geoBoundaries CC-BY 4.0 / ODbL; PostGIS GPL-2.0 (servicio, no se embebe) [VERIFIED NEXT-LEVEL.md:353] — https://github.com/wmgeolab/geoBoundaries. Sustituye el KNN-centroide + umbral heuristico por CONTENCION exacta point-in-polygon: lat/lon cae dentro de exactamente un municipio o en ninguno (hueco confesado, doctrina intacta), eliminando de raiz tanto el umbral 30km ES-calibrado como los falsos positivos cross-province/cross-pais (poligonos scoped por country_code => bleed=0). Complemento exacto del umbral cuando se conserve el fallback centroide: 'Auto-calibracion del umbral por pais desde el radio inscrito' via PostGIS ST_MaximumInscribedCircle/ST_Area + GeoPandas/Shapely (BSD-3-Clause) [VERIFIED NEXT-LEVEL.md:369] fija el techo al p99 del radio municipal real, recalculable por pais.

---

<a id="f31"></a>

#### F31 · GeoResolver: carga de indice + alcance de pais

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion del code_hint [VERIFIED]**
- `GeoResolver.load(cls, conn)` [VERIFIED pipeline/geo.py:150-183] ejecuta DOS SELECT sin dimension pais: `SELECT code, name FROM geo_province` [VERIFIED geo.py:153] y `SELECT code, name, province_code FROM geo_municipality` [VERIFIED geo.py:157]. Ninguno lleva `WHERE country_code`.
- Construye 5 indices en memoria con **clave PELADA** (string normalizado + code crudo, sin pais): `_prov: dict[str,str]` province_key->code2 [VERIFIED geo.py:132,138-148], `_muni: dict[str,dict[str,str]]` prov_code->{muni_key:code5} [VERIFIED geo.py:131,158-169], `_city_global: dict[str,set[tuple[str,str]]]` muni_key->{(prov,code5)} [VERIFIED geo.py:133,170], `_locality` [VERIFIED geo.py:134,181], `_muni_names` para fuzzy [VERIFIED geo.py:136,175-178].
- `_PROVINCE_ALIASES` (islas/bilingue ES: alava/menorca/gipuzkoa/...) se inyecta SIEMPRE e incondicional [VERIFIED geo.py:155-156], 100% ES [VERIFIED geo.py:61-73].

**(b) Mecanismo al atomo**
Indice O(1) por run. `_index_prov` registra `_norm(name)`, `_sorted_key(name)` y cada fragmento >=4 chars de los nombres bilingues partidos por `[/,]` [VERIFIED geo.py:138-148], saltando articulos pelados ('la','las') que mintearian provincia erronea. La municipalidad replica el patron [VERIFIED geo.py:158-169]. La clave del indice es SIEMPRE el code crudo (`r["code"]`, `r["province_code"]`); el `country_code` no entra en ninguna clave ni en ningun SELECT.

**(c) Costura ES->generico + fix exacto**
Cargar un 2o pais en el mismo proceso funde `'28'`(DE) y `'28'`(ES) en `_muni['28']` y `_prov` cruzados. Fix: `load(cls, conn, country_code: str = 'ES')` con `SELECT code,name FROM geo_province WHERE country_code=$1` y `SELECT code,name,province_code FROM geo_municipality WHERE country_code=$1`, y re-key de `_muni`/`_prov`/`_city_global` por `(country_code, code)` o, mas limpio, UN `GeoResolver` instanciado por tenant (un indice por pais, cero cross-talk). `_PROVINCE_ALIASES` pasa de constante de modulo a `profile.province_aliases` inyectado por pais.

**(d) Riesgo adversarial concreto**
Entidad DE bajo provincia `'28'` resuelve contra municipios de Madrid -> `municipality_code` ESPANOL acunado dentro de un `cdp_code` INMUTABLE y append-only [VERIFIED services/api/codes.py inmutabilidad cdp_pair:117-118]; el `CHECK chk_entity_muni_province` relajado para no-ES NO lo atrapa. Es BLOQUEANTE antes de cargar cualquier 2o pais. FR `'2A'/'2B'` y DOM `'971'-'976'` agravan aguas arriba (facet provincia). Ruido: dos rosters en el mismo daemon sin scoping = bleed silencioso e irreversible.

**(e) Sellado + verificacion multi-via**
- V1 (golden ES): resolucion ES byte-identica antes/despues del scoping sobre 52 provincias / 8.132 municipios.
- V2 (coexistencia): cargar DE+ES en el MISMO proceso y assert claves disjuntas (`GeoResolver(country='DE').province_code('28')` NUNCA devuelve un code ES).
- V3 (cuadre): `count` de claves cargadas en cada indice == filas geo filtradas por `country_code` en DB. Sin sangrado cross-pais.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**GeoNames pan-country backbone loader** (CC-BY 4.0, EUR0 [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md tabla:45]) — dump `allCountries.zip + hierarchy.zip + admin1CodesASCII`: surte el backbone admin1/admin2 de CUALQUIER pais keyed por `country_code` el dia uno, refrescable, asi el indice nace country-scoped desde la fuente en vez de parchearse. URL: https://www.geonames.org . **Guard companion:** **Frictionless Table Schema** (frictionless-py, MIT, EUR0 [VERIFIED NEXT-LEVEL.md:337]) https://github.com/frictionlessdata/frictionless-py — valida tipo/forma/ANCHO y unicidad `(country_code, code)` ANTES del INSERT, imponiendo mecanicamente la regla de grain que hoy solo atrapa (tarde) el motor de tipos de Postgres.

---

<a id="f36"></a>

#### F36 · Resolutor de provincia + alias + ancho zfill(2)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- **`_PROVINCE_ALIASES`** [VERIFIED pipeline/geo.py:61-73]: dict literal de **27 cadenas-alias** que cubren **~12 provincias distintas** (01,07,12,15,17,20,25,26,32,35,38,48). Contenido 100% ES: islas (`menorca/mallorca/ibiza/eivissa/formentera`->07, `gran canaria/fuerteventura/lanzarote`->35, `tenerife`->38), bilingues vasco/catalan/galego (`araba`->01, `gipuzkoa`->20, `bizkaia`->48, `castello`->12), y exonimos castellanos historicos (`gerona`->17, `lerida`->25, `orense`->32, `vizcaya`->48).
- **`province_code(name_or_code)`** [VERIFIED pipeline/geo.py:200-207]: rama A si `s.isdigit()` -> `c = s.zfill(2)` [VERIFIED :205] -> `return c if c in self._muni else None` [VERIFIED :206]; rama B (nombre) -> `self._prov.get(_norm(s)) or self._prov.get(_sorted_key(s))` [VERIFIED :207].
- **`_norm`** [VERIFIED pipeline/geo.py:51-53]: `NFKD` + `encode("ascii","ignore")` + `lower()` + `re.sub(r"[^a-z0-9]+"," ")` + `strip()`.
- **Inyeccion de alias** [VERIFIED pipeline/geo.py:155-156]: en `load()`, `for k,v in _PROVINCE_ALIASES.items(): self._prov.setdefault(k,v)` — el `setdefault` da prioridad a los nombres oficiales de `geo_province` ya indexados.
- **Guarda anti-articulo** [VERIFIED pipeline/geo.py:141-148]: `_index_prov` parte por `[/,]` y descarta fragmentos `len(p) < 4` (evita que `la`/`a`/`las` de nombres bilingues `Rioja, La` minten un province_code erroneo — e irreversible).

**(b) El mecanismo al atomo**
Entrada = `province_name` O `province_code` (L1 administrativo). Dos caminos deterministas:
1. **Digito** -> `zfill(2)` normaliza a ancho-2 -> valida contra el keyset `self._muni` (la provincia debe tener municipios cargados). La validez se ata a "tiene municipios", no a una lista estatica.
2. **Nombre** -> `_norm`/`_sorted_key` (acento/caso/orden-insensible) -> lookup en `_prov`, indice construido de `geo_province.name` + fragmentos bilingues (split `[/,]`, guarda len>=4) + los 27 alias manuales.
El `zfill(2)` **hornea** la asuncion de que el codigo L1 es exactamente 2 digitos numericos (esquema INE). Es el unico atomo no-universal de la pieza.

**(c) Costura ES->generico**
Dos hornados ES: (1) `zfill(2)` asume ancho-2 numerico; (2) `_PROVINCE_ALIASES` es un dict ES manual. Un pais con L1 alfanumerico (Corse `2A/2B`), de otro ancho (DOM `971-976`), o de 2 letras (provincia IT `MI/RM/TO`) rompe la rama digito; un pais bilingue (BE/CH/ES-CCAA) sin sus alias pierde 30-50% de variantes de nombre.

**(d) Riesgo adversarial concreto**
- **FR Corse**: `2A`/`2B` -> `isdigit()` False -> rama nombre -> miss en `_prov` -> `province_code`=None -> `municipality_code` exige provincia -> **SKIP**: concesionarios corsos caen en silencio.
- **FR DOM**: `971-976` (3 digitos) -> `zfill(2)` es no-op (ya >2) -> `'971' in self._muni`? No (con backbone ES) -> None -> SKIP.
- **IT**: provincia = 2 letras -> rama nombre -> miss -> SKIP salvo alias.
- **DE/PT cross-bleed**: L1 numerico `01-16`/`01-18` solapa el rango ES; sin scoping de pais (dependencia con facet 6 GeoResolver) DE Schleswig-Holstein `01` resuelve contra municipios de Araba -> municipality_code erroneo acunado en cdp_code inmutable.
- **Ruido**: provincia = articulo desnudo `A`/`La`/`Las` -> neutralizado por la guarda len>=4 [VERIFIED :147] (no mintea codigo erroneo).

**(e) Criterio de sellado + verificacion multi-via**
1. **Golden ES byte-identico**: las 52 provincias + las 27 cadenas-alias resuelven al MISMO code tras la costura (fixture pineado).
2. **Cobertura >= curado humano**: cada uno de los 27 alias manuales DEBE aparecer en el set auto-minado (si falta, el cruce esta incompleto).
3. **Ancho CC**: un CountryProfile con L1 no-2-digitos resuelve sus provincias; la validez `c in self._muni` rechaza un L1 desconocido con None honesto (nunca un code erroneo).
4. **Aislamiento**: ningun alias mapea la misma cadena a 2 provincias cross-pais (assert country/province isolation); alias ambiguo -> rechazado, no forzado.
5. **2a via**: alias GeoNames vs alias Wikidata convergen en una muestra; divergencia auditada.

**(f) Herramienta NEXT-LEVEL**
**GeoNames alternateNamesV2.zip** (CC-BY 4.0) — https://download.geonames.org/export/dump/ [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:385]. Auto-mina la tabla de alias por pais (isolang bilingues, flags isHistoric/isColloquial/isShortName para exonimos/formas-cortas/islas), normalizada por el mismo perfil de transliteracion, retirando el dict ES de 27 entradas y actualizandose sola cuando GeoNames cambia. Soporte: **GeoNames admin1CodesASCII.txt** (mismo dump, CC-BY 4.0) provee el code L1 oficial de ancho variable por pais, retirando el literal `zfill(2)`; **anyascii** (ISC) — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:224] para normalizar el key de nombre sin que un nombre no-latino colapse a '' bajo el ascii-ignore actual de `_norm`.

### Familia C · Minteo de identidad inmutable (hash · normalización · mint · gate G1)

---

<a id="f03"></a>

#### F03 · Hashing cdp_pair/cdp_code + base32 + inmutabilidad

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/codes.py:35-41` [VERIFIED] `_base32(digest, length=8)`: lee el digest sha256 como int big-endian, pela 5 bits por char contra `_CROCKFORD="0123456789ABCDEFGHJKMNPQRSTVWXYZ"` (:26, sin I/L/O/U), 8 chars, reversed.
- `:100-118` [VERIFIED] `cdp_pair(...)`: llama `canonical_key(...)` (:112-116) -> `digest = hashlib.sha256(key.encode("utf-8")).digest()` (:117) -> retorna `(key, mint_code(province_code=..., digest=digest, country_code=...))` (:118). `cdp_code` (:121-130) retorna `cdp_pair(...)[1]`.
- `mint_code` (:44-53) -> `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`. `canonical_key` (:56-97) **EXCLUYE country_code de la pre-imagen a proposito** (:62-65 VERIFIED).

**(b) Mecanismo al atomo**
Identidad -> codigo inmutable en 4 atomos: (1) `canonical_key` construye la pre-imagen de dedup (particular > domain > cif > name+muni > name+prov); (2) sha256 sobre UTF-8 de ese key -> digest de 32 bytes; (3) `_base32` codifica Crockford los 40 bits bajos (8x5) del digest en un sufijo human-safe; (4) `mint_code` antepone `CDP-{cc}-{prov}-`. El INSERT usa `ON CONFLICT(cdp_code) DO UPDATE last_seen` -> misma identidad re-descubierta = mismo codigo = idempotente, append-only. `country_code` se enhebra SOLO al prefijo (mint_code), nunca al digest (canonical_key:62-65), de modo que el pais jamas re-keya una entidad.

**(c) Costura ES->generico + fix exacto**
- **Costura:** NINGUNA estructural en este modulo — ya es parametrico por pais (`mint_code` es el unico hogar del literal `CDP-`, ~30 minters enrutan aqui [codes.py:48 VERIFIED]). La costura es aguas arriba: la calidad del digest depende de (i) un `province_code` bien scoped en el prefijo y (ii) un `canonical_key` no colapsado. El base32 usa solo 40 de 256 bits de sha256 (espacio 2^40) — colision despreciable por provincia, pero la pre-imagen DEBE ser honesta.
- **Fix:** asegurar que los call-sites pasen `country_code` (faceta 5, discover.py) y que geo/normalizacion aguas arriba esten scoped+transliterados. Cero edicion de la matematica de hashing. Para volver AUDITABLE la inmutabilidad, envolver cada mint en una atestacion (herramienta).

**(d) Riesgo adversarial concreto**
Un mint con provincia erronea (geo no-scoped, faceta 6) o identidad colapsada (normalizacion no-latina, faceta 12) produce un codigo IRREVERSIBLE; el append-only convierte el error en permanente y sample-verify-delete NO lo revierte. Para un pais foraneo, si aguas arriba es correcto la matematica es country-blind y segura; el unico riesgo intrinseco es que un minter NUEVO reintroduzca el literal `CDP-ES-` fuera de `mint_code` (faceta 14).

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** mismo input ES -> mismo codigo byte-identico (golden); INSERT ON CONFLICT(cdp_code) garantiza idempotencia.
- **Via 1 (golden):** re-mint de un corpus ES, diff de cdp_code = 0 drift.
- **Via 2 (round-trip):** name->key->digest->code->re-mint = mismo codigo.
- **Via 3 (adversarial/atestada):** una atestacion in-toto liga {SHA del codigo, content-hashes de inputs} -> {cdp_code}; alterar un input FALLA la verificacion, asi un tercero PRUEBA que el codigo inmutable salio exactamente de esos inputs sin confiar en nosotros.

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**in-toto** — Sello criptograficamente reproducible y ATESTIGUADO [NEXT-LEVEL.md:140-147 + 309-315 VERIFIED]. URL https://github.com/in-toto/in-toto (Apache-2.0, EUR0; graduado en CNCF 2025-02-10). Emite una atestacion de provenance firmada y tamper-evident que liga inputs->outputs, anclable a un transparency log Sigstore/rekor. Convierte el cdp_code inmutable de una afirmacion a un CERTIFICADO no-repudiable re-verificable bit a bit. Alternativas: Sigstore cosign, DVC (inputs content-addressed [NEXT-LEVEL.md:148-155]), SLSA provenance.

---

<a id="f25"></a>

#### F25 · _upsert idempotente + costura nuclear country_code

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED `pipeline/discover.py:77-114`].** Firma `_upsert(conn, geo, e: DiscoveredEntity, geocoder=None) -> tuple[bool,bool,bool]` que devuelve `(entity_was_new, municipality_resolved, province_resolved)` [:77-79]. Cascada geo previa al mint: `prov = geo.province_code(e.province_name)` [:80] -> `muni = geo.municipality_code(prov, e.municipality_name)` [:81] -> si no hay prov y hay municipio: `prov, muni = geo.resolve_city_global(e.municipality_name)` [:82-84] -> si aún no hay prov y hay geocoder: `prov = geocoder.nearest_province(e.lat, e.lon)` [:85-87] -> si aún no hay prov: `return (False, False, False)` (SKIP honesto, no mintea) [:88-90]. Mint: `code = cdp_code(province_code=prov, domain=e.website, cif=e.cif, name=e.legal_name or e.trade_name, municipality_code=muni, address=e.address)` [:91-93] — la llamada NO pasa `country_code`, así que `cdp_code` cae al default `country_code="ES"` [VERIFIED `services/api/codes.py:121-130`] y `mint_code` emite el literal `CDP-ES-{prov}-{b32}` [VERIFIED `codes.py:44-53`]. Escritura: `INSERT INTO entity (entity_ulid, cdp_code, kind, ... , is_tier1, status, first_discovered_source, last_seen) VALUES (...,'active',$18, now())` [:96-104] — la lista de columnas NO incluye `country_code`, luego `entity.country_code` cae a su DEFAULT de esquema `'ES'` (0052). Idempotencia atómica: `ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now() RETURNING entity_ulid, (xmax = 0) AS inserted` [:100-101]; el truco `xmax=0` distingue INSERT real (xmax=0) de UPDATE-en-conflicto, y `entity_ulid` vuelve por RETURNING — sin SELECT separado, sin ventana de carrera donde un delete concurrente devuelva NULL y aborte el run [:105-107]. Cierra con upsert idempotente de procedencia: `INSERT INTO entity_source (entity_ulid, source_key, source_ref) ... ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now(), source_ref = COALESCE(EXCLUDED.source_ref, entity_source.source_ref)` [:109-113] — refresca `seen_at`, que es la frontera por-run del VAM (Q7). Retorno `(bool(row['inserted']), muni is not None, True)` [:114].
**(b) Costura ES->genérico.** Es el ÚNICO punto de escritura del censo, y porta DOS fugas de país, ambas silenciosas: (1) la llamada a `cdp_code()` [:91] omite `country_code` -> prefijo ES por default; (2) la lista de columnas del INSERT [:96] omite `country_code` -> `entity.country_code` = DEFAULT 'ES'. El bucle por-entidad es idéntico país a país; sólo falta enhebrar `adapter.country_code` (del contrato SourceAdapter, faceta 1) hasta el mint y el INSERT.
**(c) Fix exacto.** En `discover()`: `cc = getattr(adapter, 'country_code', 'ES')`. Ampliar `_upsert(conn, geo, e, geocoder, *, country_code)`. En :91: `code = cdp_code(..., country_code=country_code)`. En :96-104: añadir la columna `country_code` a la lista y bindearla (`$19=cc`). Cargar el `GeoResolver` scopeado a `cc` (acopla faceta 6). Default 'ES' preserva byte-identidad histórica.
**(d) Riesgo adversarial.** Un adaptador DE (Handelsregister / mobile.de) con `country_code='DE'` pero `_upsert` sin enhebrar estampa `entity.country_code='ES'` y `cdp_code='CDP-ES-...'` SIN excepción. El CHECK `chk_entity_muni_province` (relajado para no-ES en 0053) no lo atrapa porque la fila se declara ES. Por inmutabilidad del cdp_code (append-only, `ON CONFLICT(cdp_code)`), la corrupción es INVISIBLE e IRREVERSIBLE: cada entidad DE se disfraza de ES en el código inmutable. PT, FR (DOM) e IT sufren idéntico.
**(e) Sellado + verificación multi-vía.** Invariante COUNTRY-PROOF: `SELECT count(*) FROM entity WHERE country_code='CC' AND cdp_code NOT LIKE 'CDP-CC-%'` == 0. (1) Golden: salida ES byte-idéntica a la histórica `CDP-ES-{prov}-{b32}` tras enhebrar (ruta default intacta). (2) Fixture DE: cada `cdp_code` emitido empieza `CDP-DE-` Y `entity.country_code='DE'`. (3) Idempotencia: re-correr el mismo fetch DE produce 0 inserts nuevos (count de `xmax=0` == 0 en 2ª pasada) — prueba que `ON CONFLICT(cdp_code)` es país-estable. (4) Aislamiento cross-país: sembrado ES+DE, cero prefijos que no casen su columna `country_code`.
**(f) Herramienta nivel-inalcanzable.** Pydantic (MIT, EUR0) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL:584-590]. Modelar el country-pack + el invariante del punto de escritura como CONTRATO TIPADO y un test de CI que asevera la biyección (cada adaptador de país activo porta `country_code`, y `entity.country_code == prefix(cdp_code) == adapter.country_code`), convirtiendo el fallback-ES silencioso en build ROJO mecánico — el guard country-proof del mandato: el invariante pasa de esperanza a precondición tipada.

---

<a id="f26"></a>

#### F26 · Politica de normalizacion de texto (NFKD+ascii-ignore)

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED].** `services/api/codes.py:29-32` `_normalize(text)`: `unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')` y luego `re.sub(r'[^a-z0-9]+', '', text.lower())` — NFKD descompone tildes, `ascii-ignore` DESCARTA todo codepoint no-ASCII, lower, y colapsa lo no-`[a-z0-9]` a cadena VACÍA (sin separador). `pipeline/geo.py:51-53` `_norm(text)`: mismo NFKD + ascii-ignore + lower, pero `re.sub(r'[^a-z0-9]+', ' ', ...).strip()` — sustituye lo no-alfanumérico por ESPACIO (preserva frontera de token para `_sorted_key`). `_sorted_key(text) = ' '.join(sorted(_norm(text).split()))` [VERIFIED `geo.py:56-57`] depende de que `_norm` emita tokens separados por espacio. Es la canonicalización COMPARTIDA: `_normalize` alimenta `canonical_key` (identidad, `codes.py:92-96`) y `_norm` alimenta las claves de provincia/municipio/localidad (resolución geo). Una política, dos consumidores.
**(b) Costura ES->genérico (ROTURA).** Para alfabetos no-latinos (kanji/kana JP, cirílico, griego, árabe, hebreo, tailandés, chino) `encode('ascii','ignore')` borra TODO carácter -> la función devuelve `''`. El texto se ANIQUILA, no se translitera. La política ascii-ignore es la costura de script; debe pasar a una política de transliteración por pack (`pack.normalize_policy`) que romanice ANTES del fold ASCII.
**(c) Fix exacto.** Sustituir `.encode('ascii','ignore').decode('ascii')` en AMBAS funciones (`codes.py:30` y `geo.py:52`) por `anyascii(text)` aplicado tras NFKD y antes del strip `[a-z0-9]`, enrutado por el CountryProfile activo: packs latinos byte-idénticos (anyascii es identidad sobre ASCII), packs no-latinos transliterados. AMBAS funciones DEBEN compartir el mismo transliterador para que identidad y geo queden coherentes.
**(d) Riesgo adversarial.** NO es la rotura EU-latina (DE/FR/IT/PT normalizan bien — el latino acentuado se fold correctamente). Es el onboarding NO-latino (JP/RU/GR/CJK/árabe): **Identidad** — todo nombre de dealer en kanji colapsa a `''` -> `canonical_key` queda `name:|{muni}` IDÉNTICO para todo dealer del municipio sin dominio/CIF -> FUSIÓN MASIVA en UN cdp_code (cientos de dealers distintos fundidos, irreversible). **Geo** — todo nombre de provincia/municipio no-latino normaliza a `''` -> no casa nada -> 100% SKIP (cero mints). **Ruido** — un nombre todo-puntuación/emoji ('★★★') también cae a `''` -> mismo colapso.
**(e) Sellado + verificación multi-vía.** (1) Golden latino: corpus ES normaliza byte-idéntico antes/después del swap (anyascii es identidad sobre ASCII-tras-NFKD -> 0 drift). (2) Fixture no-latino (JP/RU): `canonical_key` DISTINTO por entidad real distinta (0 fusiones falsas) Y provincia/municipio resuelven (sin SKIP masivo). (3) Coherencia inter-consumidor: el MISMO token transliterado alimenta `codes._normalize` y `geo._norm` (assert romanización idéntica en muestra compartida). (4) No-destructividad: `normalize(x) != ''` para todo x no vacío (guard del bug-vacío).
**(f) Herramienta nivel-inalcanzable.** anyascii (ISC, EUR0) — https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL:224,329,482]. Python puro, sin deps nativas, ~200-500KB de tablas embebidas, transliteración exhaustiva CJK/cirílico/griego/árabe. Licencia ISC comercial-limpia, explícitamente preferida sobre Unidecode/text-unidecode (GPL/Artistic copyleft) para la ruta servida. Cierra la doble-falla CRÍTICA ascii-fold (colapso de identidad + vacío geo) en un solo swap.

---

<a id="f32"></a>

#### F32 · Algebra de identidad canonical_key (pre-imagen de dedup)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion del code_hint [VERIFIED]**
- `canonical_key(...)` [VERIFIED services/api/codes.py:56-97] aplica prioridad ESTRICTA de senal mas fuerte a mas debil:
  1. particular: `f"particular:{plat}:{sid}"` [VERIFIED codes.py:72-75] (plat normalizado, sid crudo).
  2. domain: `f"domain:{host}"` SOLO si el host va sin path (un URL con path = portal OEM/agregador, cae a name+address) [VERIFIED codes.py:76-87].
  3. cif: `f"cif:{cif.upper().strip()}"` [VERIFIED codes.py:88-89].
  4. name+muni: `f"name:{_normalize(name)}|{municipality_code}{addr}"` [VERIFIED codes.py:93-94].
  5. name+prov: `f"name:{_normalize(name)}|p{province_code}{addr}"` [VERIFIED codes.py:95-96]; `raise ValueError` si nada aplica [VERIFIED codes.py:97]. `addr = |{_normalize(address)}` es desempate [VERIFIED codes.py:92].
- `country_code` se acepta en la firma [VERIFIED codes.py:61] pero se EXCLUYE deliberadamente de la pre-imagen, con comentario literal: *"mixing the country into it would change every sha256 hash and re-key all entities"* [VERIFIED codes.py:62-65]. CONFIRMA la decision del facet.

**(b) Mecanismo al atomo**
Es la pre-imagen del `sha256` -> `_base32` Crockford -> `mint_code` (via `cdp_pair` [VERIFIED codes.py:100-118]). Define cuando dos descubrimientos son la MISMA entidad (dedup cross-source): un particular con N coches colapsa a 1 seller; el dominio pelado es identidad fuerte cross-source; el cif manda sobre el nombre.

**(c) Costura ES->generico + fix exacto**
La prioridad domain>cif>name+muni>name+prov es YA generica. Lo ES-especifico entra SOLO por dos puntos: (i) `_normalize` [VERIFIED codes.py:29-32: NFKD + `encode('ascii','ignore')`] y (ii) la semantica de 'host pelado'. Fix: MANTENER `country_code` fuera de la pre-imagen (no tocar codes.py:62-65); anadir un **empty-name guard** (raise si `_normalize` colapsa el nombre a `''` ANTES de mintear); mover la transliteracion country-scoped a `_normalize` (es la facet de normalizacion, posicion 12 — NO el algebra). El algebra no cambia su forma.

**(d) Riesgo adversarial concreto**
Si una costura de pais metiera `country_code` en la pre-imagen, cambiaria TODO `sha256` -> re-key masivo irreversible de los ~431k cdp_code vivos. Via `_normalize`, nombres no-latinos (JP kanji/kana, cirilico, griego) colapsan a `''` -> `name:|{muni}` IDENTICO para todo dealer name-only de un municipio sin dominio/cif -> fusion masiva en UN cdp_code inmutable (la peor rotura, Raiz B). Diacriticos DE: `'Straße'` vs `'Strasse'` divergen -> under-merge. VAT DE/IT/PT no valida por checksum CIF ES -> cae a identidad por nombre (mas debil, mas colisiones).

**(e) Sellado + verificacion multi-via**
- V1 (golden ES): re-descubrir la misma entidad por otra fuente NUNCA mintea un 2o codigo; particular con N coches = 1 vendedor; `sha256`/`cdp_code` ES byte-identico sobre el corpus golden.
- V2 (ER independiente): Splink cluster debe ser refinamiento/superset del union-find determinista — NINGUN merge que el determinista prohibe se auto-aplica; el determinista es el PISO.
- V3 (cardinalidad): el intervalo distinct-entity de ER-Evaluation contiene el conteo determinista servido; divergencia bloquea el sello.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**Splink** (MIT, EUR0 [VERIFIED NEXT-LEVEL.md:450]) https://github.com/moj-analytical-services/splink — linkage Fellegi-Sunter APRENDIDO (EM entrena los pesos m/u por comparacion desde los datos), calibrado, exportable como `model.json` reproducible y auditable (waterfall por merge), re-fit por pais/run; corre EUR0 in-process sobre DuckDB. El `canonical_key` determinista queda como lower-bound/piso; Splink es la capa-2 certificable cuyas propuestas alimentan el VAM gate. **Companion:** **pyJedAI** (Apache-2.0, EUR0 [VERIFIED NEXT-LEVEL.md:546]) https://github.com/AI-team-UoA/pyJedAI — 3a via ER arquitectonicamente independiente para certificacion de sello 2-via -> 3-via (determinista + Splink + pyJedAI concuerdan dentro del intervalo o el sello falla).

---

<a id="f35"></a>

#### F35 · Gate G1 IDENTITY por-entidad (complete.py)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion del code_hint [VERIFIED]**
- DOBLE costura ES en `pipeline/complete.py`: `_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")` (solo 01-52, las 52 provincias de Espana) [VERIFIED complete.py:73] y `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` (prefijo `CDP-ES-` hardcodeado) [VERIFIED complete.py:89]. `_NATIONAL_KINDS = frozenset({"subasta","plataforma","oem_vo_portal","importador"})` [VERIFIED complete.py:83-85].
- `check_g1(conn, cdp_code)` [VERIFIED complete.py:107-148]: fetch 1 fila por `cdp_code` [VERIFIED complete.py:123-131]; `is_national = row.get("kind") in _NATIONAL_KINDS and prov_str is None` [VERIFIED complete.py:141]; `if not is_national and (prov_str is None or not _PROVINCE_RE.match(prov_str)): return False, "invalid_province_code:..."` [VERIFIED complete.py:142-143]; `if not _CDP_CODE_RE.match(cdp_code): return False, "cdp_code_format_invalid:..."` [VERIFIED complete.py:145-146].
- **Hallazgo critico confirmado:** el golden `TestG1RegexCountryWidening._regex()` devuelve EXCLUSIVAMENTE `complete._CDP_CODE_RE` [VERIFIED tests/test_country_golden.py:271], con `xfail(strict)` que auto-flipa a XPASS al ensanchar [VERIFIED test_country_golden.py:286-291]. `_PROVINCE_RE` (la 2a regex ES, :73) NO esta vigilado por NINGUN golden -> exactamente la costura invisible que el facet denuncia: el diseno solo nombro `:89`.

**(b) Mecanismo al atomo**
Sello por-entidad aguas abajo de discover: una entidad alcanza COMPLETED en G1 sii existe 1 fila, su `province_code` es valido (01-52) O es NATIONAL_KIND con province NULL (el '00' vive solo en el `CDP-ES-00-*`), y su `cdp_code` casa el patron Crockford-base32.

**(c) Costura ES->generico + fix exacto**
Fix: ensanchar `_CDP_CODE_RE` a `r"^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"`; hacer `_PROVINCE_RE` y `_NATIONAL_KINDS` table-driven desde `geo_province` (o ISO 3166-2) por pais en vez de literales; quitar el `xfail` G1 [VERIFIED test_country_golden.py:287] cuando ambas regex esten ensanchadas; y ANADIR un golden gemelo que vigile `_PROVINCE_RE` (hoy ausente). El '00' sentinel tambien es ES-shaped y debe derivarse del perfil.

**(d) Riesgo adversarial concreto**
Toda entidad `CDP-PT-`/distrito PT (ancho/forma de L1 distintos) falla G1 IDENTITY -> ninguna entidad no-ES alcanza nunca COMPLETED -> el pais NUNCA se sella en la puerta por-entidad. IT tiene 107 provincias (> 52), FR DOM `'971'-'976'` son 3 digitos, DE Kreis 5 digitos: el rango `01-52` los rechaza a todos. Y como `_PROVINCE_RE` NO tiene golden, un onboarder que ensanche SOLO `_CDP_CODE_RE` (lo unico que el xfail vigila) dejaria la 2a costura ES viva -> falso 'pais abierto' que pasa el golden pero rechaza toda provincia foranea.

**(e) Sellado + verificacion multi-via**
- V1 (golden ES): `_CDP_CODE_RE` acepta TODO `_ES_GOLDEN` byte-for-byte [VERIFIED test_country_golden.py:273-276] y RECHAZA malformados (1-dig prov, 3-letter country, lowercase, tail 7/9 chars, I/L/O/U fuera de Crockford) [VERIFIED test_country_golden.py:294-303].
- V2 (golden de ensanche): acepta `CDP-DE-28-...`/`CDP-FR-75-...` (el xfail deja de disparar [VERIFIED test_country_golden.py:286-292]) Y un golden gemelo NUEVO sobre `_PROVINCE_RE` table-driven que hoy no existe.
- V3 (autoridad externa): `pycountry` ISO 3166-2 valida el set de subdivisiones por pais (ES=52, FR=101, IT=107, DE=16, MX=32, JP=47) cross-checked contra una 2a fuente.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**pycountry** (LGPL-2.1, EUR0 [VERIFIED NEXT-LEVEL.md:530]) https://github.com/pycountry/pycountry — empaqueta el dataset Debian iso-codes (ISO 3166-1/-2 + ISO 4217): el grain, el ancho de codigo y el conteo de subdivisiones de primer nivel de CADA pais se vuelven DATOS que alimentan un manifest de sello por-pais, sustituyendo `_PROVINCE_RE` (01-52 = los 52 centinelas ES) y los caps ES-shaped por valores derivados de la autoridad. Uso build/config-time (no hot-path), asi el caveat LGPL es no-issue. **Alternativa estrictamente permisiva:** `iso3166` (MIT) para el subset de paises + el JSON crudo de iso-codes para subdivisiones.

---

<a id="f37"></a>

#### F37 · Ensamblado mint_code (hogar unico del prefijo)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- **`mint_code`** [VERIFIED services/api/codes.py:44-53]: firma keyword-only `mint_code(*, province_code, digest, country_code="ES")` -> `return f"CDP-{country_code}-{province_code}-{_base32(digest)}"` [VERIFIED :53].
- **`DEFAULT_COUNTRY = "ES"`** [VERIFIED services/api/codes.py:24].
- **`_base32(digest, length=8)`** [VERIFIED services/api/codes.py:35-41]: Crockford base32, alfabeto `_CROCKFORD` sin I/L/O/U [VERIFIED :26].
- **Hogar unico**: docstring [VERIFIED :46-52] declara "the ONE home of the prefix literal... Every coder (this module plus the ~30 pipeline/platform mints) routes through here, so `CDP-{country}-` exists in exactly one place"; salida byte-identica al historico `f"CDP-ES-{province_code}-{_base32(digest)}"` verificada por golden.
- **country_code fuera de la pre-imagen**: `cdp_pair` [VERIFIED :100-118] llama `mint_code(..., country_code=country_code)` en :118, pero `canonical_key` [VERIFIED :56-97] acepta `country_code` y DELIBERADAMENTE no lo usa [VERIFIED :62-65] — la pre-imagen del digest queda ciega al pais (re-descubrir la misma entidad nunca re-keya).

**(b) El mecanismo al atomo**
Ensamblaje puro de cadena: toma `province_code` (ya resuelto, 2-digitos), `digest` (sha256 bytes de canonical_key) y `country_code`; emite `CDP-{cc}-{prov}-{8 Crockford}`. El UNICO hilo estructural de pais es el **prefijo**; el digest es ciego al pais. Ya parametrico: `country_code` default "ES" -> todo call-site existente y toda salida ES son byte-identicos. Su valor de diseno es la **concentracion**: el literal del prefijo vive en una sola linea (:53), asi que abrir un pais es trivial.

**(c) Costura ES->generico**
**NINGUNA estructural en este modulo** — esta ya verificado como generico. La costura vive en los CALL-SITES: discover.py:91 (y los ~30 minters) que no pasan `country_code` y por tanto caen al default "ES". El fix es aguas arriba (enhebrar `adapter.country_code` en las llamadas a cdp_pair/cdp_code), no aqui. El criterio propio de esta faceta es que NINGUN minter nuevo reintroduzca un literal `CDP-ES-` fuera de `mint_code`.

**(d) Riesgo adversarial concreto (intrinsecamente BAJO)**
- **Re-introduccion de literal**: un minter futuro que arme el code a mano (`f"CDP-ES-{prov}-..."`) saltandose `mint_code` reintroduce el literal ES fuera de control central; una entidad DE recibe entonces `CDP-ES-` irreversiblemente (cdp_code append-only).
- **DE/FR/IT/PT**: si el call-site no enhebra country_code, `mint_code` cae a "ES" y estampa `CDP-ES-` sobre una entidad foranea — la corrupcion nace en el call-site, no en `mint_code`.
- **Ruido**: `province_code` vacio/None produce `CDP-ES--{b32}` (doble guion); `mint_code` no valida province_code — confia en la resolucion aguas arriba (facet 7) y en la regex G1 (facet 34) que rechaza codes malformados aguas abajo.

**(e) Criterio de sellado + verificacion multi-via**
1. **Golden byte-identidad**: para las 431.211 entidades ES vivas, `mint_code(prov,digest,"ES")` == historico `f"CDP-ES-{prov}-{_base32(digest)}"` exacto (docstring lo declara golden-verificado).
2. **Fuente unica (grep-gate)**: el literal `CDP-` (o la regex `CDP-[A-Z]{2}-`) aparece en EXACTAMENTE un sitio (codes.py:53) — assert en CI.
3. **Propiedad (Hypothesis)**: para todo `(country_code in [A-Z]{2}, province_code, digest)`, la salida empieza por `f"CDP-{country_code}-"`, tiene sufijo de 8 chars en `_CROCKFORD`, y para country_code="ES" iguala al formateador legacy — cubre todo input que el pack pueda producir, no solo ejemplos ES.
4. **2a via (round-trip)**: `country_of_cdp` (paths.py, facet 36) parsea el prefijo de vuelta al pais — mint y parse deben concordar.

**(f) Herramienta NEXT-LEVEL**
**Hypothesis** (MPL-2.0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:320]. El criterio de sellado de esta faceta ES un golden test; Hypothesis lo eleva de por-ejemplo (ES) a por-propiedad: sintetiza tuplas adversariales `(country_code, ancho de province, digest)` y MINIMIZA al contraejemplo mas simple, congelandolo como regression-fixture determinista. Es la diferencia entre "pasa en ES" y "el contrato del prefijo se sostiene para todo input que el pack pueda producir". Alternativas: pandera (schema-como-contrato, integra Hypothesis), schemathesis (fuzz del contrato API). EUR0, CPU puro, se integra en el job unit/db-tests existente.

### Familia D · Cuórum VAM + oráculo de cuenta

---

<a id="f09"></a>

#### F09 · Motor de quorum record_count_verdict

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED pipeline/verify.py:53-166,201-210].** `record_count_verdict` recibe `paths: dict[str,int]`. `_path_family` [VERIFIED :31-50] mapea cada path a familia por keywords: db (:42), http (:44), source (:46), registral (:48, keywords 'registr','official','dgt','cnae','faconauto','borme','census'), fallback 'other' (:50). Independencia [VERIFIED :117-119]: `families = {_path_family(k)...}`, `origins = {k...}`, `has_independence = len(families)>=2 and len(origins)>=2`. Logica de veredicto [VERIFIED :125-166]: `modal_ok` (:137 = top_n>=2 AND no rivals AND primary_agrees), `drift_ok` (:148 = len>=2 AND divergence<=tolerance), `zero_certifiable` (:155 = top_val!=0 OR measured_by_observation); TRUSTWORTHY solo si `modal_ok and has_independence and zero_certifiable` (:156-159); si no, UNVERIFIED (:164) o REFUTED (:166). Supersession [VERIFIED :205-210]: UPDATE marca todos los verdicts previos como superseded.

**(b) Mecanismo al atomo.** Es el juez de cuentas: TRUSTWORTHY sii el valor modal tiene >=2 paths identicos, sin rival con >=2, el primary_path concuerda (anti-perdida-silenciosa, :133-136), independencia real (>=2 familias Y >=2 origenes), y el cero solo certifica con observacion explicita. Computa `verifier_paths`/`independent_values` para satisfacer el CHECK `chk_trustworthy_needs_quorum` (0026) — el comentario (:111-116) documenta el bug que esto arregla: "989/991 TRUSTWORTHY had quorum_n=0 from string paths". La matematica del quorum es INVARIANTE por pais; el motor no cambia. El riesgo no es el motor sino la calidad/ortogonalidad de los paths que recibe: si un pais carece de oraculo registral, el quorum cae a db==http (2 familias) y certifica sin la pata registral, bajando la vara en silencio. La supersession garantiza que solo el verdict mas nuevo esta activo (un current por subject_key).

**(c) Costura ES→genérico.** El motor es invariante (pura aritmetica de quorum); la costura ES vive en `_path_family`(:31-50): las keywords de la familia 'registral' (:48) son nombres de instituciones ESPANOLAS — 'dgt','cnae','faconauto','borme'. Un path de autoridad extranjera (Handelsregister DE, RPPC/SAT MX, JSIC JP) no casa ninguna keyword -> colapsa a 'other' -> debilita la independencia SIN marca. No hay seam estructural en la matematica, solo en la taxonomia de familias.

**Fix exacto.** Hacer las keywords de familia table-driven por pais: `country.path_families` anade los nombres de instituciones registrales/oficiales del pais a la familia 'registral'. El motor de quorum y los umbrales (modal/drift/zero) quedan intactos. Adicionalmente, marcar explicitamente cuando un TRUSTWORTHY se emitio SIN pata 'registral' (solo db+http) para que la ausencia del oraculo registral sea VISIBLE en el evidence, no silenciosa.

**(d) Riesgo adversarial concreto.** DE/MX/JP: una ruta de autoridad (Handelsregister, RPPC/SAT, JSIC) no casa las keywords ES de :48 -> familia 'other' -> si las otras dos rutas son db+http el `has_independence` se cumple por familias equivocadas y el verdict lee TRUSTWORTHY apoyado en una independencia degradada. PT/no-UE sin un declared_count tipo DGT: el VAM cierra con db==http (2 familias reales) y NO marca que falta la pata registral -> la vara baja en silencio. Ruido: paths con nombres genericos ('count','total') casan 'source' por accidente y fingen ortogonalidad.

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) cada cuenta del pais cierra con >=2 familias REALES (no degradadas a 'other') — test que asevera que las rutas del pais mapean a familias nombradas. (2) El INSERT que emite TRUSTWORTHY siempre satisface `chk_trustworthy_needs_quorum` (quorum_n>=2 AND family_n>=2 AND origin_n>=2) — el CHECK de DB es la 2a via mecanica. (3) Cross-check: un verdict TRUSTWORTHY sin familia 'registral' se reporta como 'cobertura sin ancla registral' (honestidad), no se pliega como pleno.

**(f) Herramienta NEXT-LEVEL (€0).** **in-toto + Sigstore cosign** — Apache-2.0, EUR0 [VERIFIED https://github.com/in-toto/in-toto] (NEXT-LEVEL.md:143 cluster discovery-trust y :643 cluster ops 'Sello CERTIFICABLE'). Convierte el verdict TRUSTWORTHY de una fila de DB mutable a una atestacion FIRMADA y tamper-evident que liga {paths, independent_values, verdict, git SHA, content-hashes de los inputs} -> certificado no-repudiable verificable por un tercero sin confiar en nosotros. in-toto graduo en CNCF (2025-02). Complemento: **Great Expectations / Pandera** (Apache-2.0, NEXT-LEVEL.md:167 'Contrato de datos PRE-sello') como contrato PRE-quorum que asevera que cada clase de path tiene >=1 fuente real (fail-closed) antes de que el motor compute. Eleva el quorum de 'afirmacion interna' a 'certificado criptografico re-verificable'.

---

<a id="f15"></a>

#### F15 · Taxonomia de familias VAM + oraculo de cuenta

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/verify.py:31-50] `_path_family(path_name)`: baja a minusculas y mapea por substring a familia: `db` (db/ingest/persist/land/stored/cdp/distinct/join), `http` (fetch/harvest/scrape/http/api/live/cage/pair/page), `source` (declar/source/oracle/header/total/numberofresults/remaining), `registral` (**registr/official/dgt/cnae/faconauto/borme/census** :48), else `'other'`.
- [VERIFIED pipeline/verify.py:117-119] `families = {_path_family(k) for k,_ in items}`; `origins = {k for k,_ in items}`; `has_independence = len(families) >= 2 and len(origins) >= 2`.
- [VERIFIED pipeline/discover.py:120] `declared = adapter.declared_count()`.
- [VERIFIED pipeline/discover.py:159-164] `record_count_verdict(paths={'db_ingested': in_db, 'fetched': len(entities), 'source_declared': declared})`.
- [VERIFIED pipeline/sources/base.py:35-37] `declared_count()` default `return None`; [VERIFIED verify.py:109] `items = [(k,v) ... if v is not None]` -> un None se filtra del quorum.

**(b) Mecanismo al atomo**
`_path_family` es el clasificador de ORTOGONALIDAD del VAM. El CHECK de deep-ledger `chk_trustworthy_needs_quorum` (0026) exige `family_n >= 2` familias distintas para TRUSTWORTHY; `_path_family` mapea cada NOMBRE de path (string) a una familia gruesa por keyword. Nombres desconocidos colapsan a `'other'` (verify.py:50) — fail-safe deliberado (Law I: ortogonalidad no probada nunca otorga quorum). El shape default en discover (db_ingested->db, fetched->http, source_declared->source) da 3 familias -> independencia. `declared_count()` es el oraculo `source`; devuelve None default (base.py:37) y se filtra, asi que un pais sin oraculo declarado cae a un quorum db+http de 2 familias.

**(c) Costura ES->generico**
Las keywords `registral` (dgt/cnae/faconauto/borme/census, verify.py:48) son NOMBRES DE INSTITUCIONES ESPANOLAS. Un path de autoridad extranjera (MX RPPC/SAT, JP JSIC, DE Handelsregister) no casa ninguna keyword -> colapsa a `'other'`. Y la mayoria de fuentes no-ES no publican un `declared_count` tipo total (sin DGT-equivalente), debilitando tambien la familia `source`. El quorum puede leer TRUSTWORTHY de db==http (2 familias) SIN la pata registral, bajando la vara en silencio.

**(d) Riesgo adversarial concreto**
Ruta MX (RPPC/SAT) o JP (JSIC) no casa keywords ES -> familia `'other'`; combinada con otra `'other'` o un par db/http, la prueba `len(families)>=2` se satisface con db+http SOLO mientras el pais NO tiene verificacion registral independiente — la vara cae sin marca. A la inversa, DOS paths foraneos -> ambos `'other'` colapsan a UNA familia y FALLAN independencia (sobre-conservador): otro fallo silencioso de signo opuesto.

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** cada cuenta cierra con >=2 familias REALES del pais, jamas degradadas a `'other'`; la presencia/ausencia de la pata registral es explicita.
- via1: guard test enumera el roster de paths del pais activo y asserta que cada uno mapea a una familia NOMBRADA (ninguna -> 'other').
- via2: ES golden — db_ingested/fetched/source_declared siguen mapeando a db/http/source (family_n=3 byte-identico).
- via3: adversarial — inyectar un path de autoridad foranea y asertar que el verdict NO lee TRUSTWORTHY puro de db+http cuando el roster declarado esperaba pata registral.

**(f) Herramienta de nivel inalcanzable**
**GLEIF LEI Golden Copy** — surte una pata `registral` REAL a CUALQUIER pais dia-uno (LEI, CC0, descarga diaria): cada entidad legal con LEI lleva pais + direccion + (a menudo) id de registro local, una lista de captura registral que EXISTE sin escribir adaptador nacional. Cierra "sin DGT-equivalente el VAM no marca que falta la pata registral". Complemento: el contrato de datos pre-sello (Great Expectations) mecaniza "familia colapsa a 'other' -> build falla". [VERIFIED NEXT-LEVEL.md:172-178] CC0 1.0, EUR0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy

**Costura/fix complementarios [VERIFIED].** [VERIFIED verify.py:48] keywords `registral` = dgt/cnae/faconauto/borme/census (instituciones ES); un path de autoridad foranea (RPPC/SAT MX, JSIC JP, Handelsregister DE) no casa -> 'other'. [VERIFIED base.py:37] `declared_count` default None -> paises sin DGT-equivalente debilitan la familia 'source'. — 1) Dejar de clasificar por NOMBRE de path; portar la familia EXPLICITA: anadir `orthogonal_bucket`/`family` a SourceAdapter y pasar paths estructurados {name,family,value}. 2) Generalizar el set 'registral' a tokens country-driven (country.toml). 3) Hacer VISIBLE la pata faltante: cierre solo db+http (sin source/registral) -> verdict UNVERIFIED-degraded o nota 'no_registral_anchor', nunca TRUSTWORTHY silencioso.

---

<a id="f19"></a>

#### F19 · Orquestacion discover() + cuenta por-run + cierre VAM

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** `discover(source_key)` vive en [VERIFIED pipeline/discover.py:117-167]. Secuencia atomica confirmada linea a linea:
- `adapter = ADAPTERS[source_key]()` + `entities = adapter.fetch()` + `declared = adapter.declared_count()` + `excluded = getattr(adapter,"excluded_count",0)` [VERIFIED :118-121]; log `declared= fetched= excluded_out_of_scope=` [VERIFIED :122-123].
- `geo = await GeoResolver.load(conn)` [VERIFIED :127] — cargado SIN country_code.
- geocoder perezoso: solo si `any(e.lat is not None and not e.province_name ...)` [VERIFIED :129-132].
- `run_start = await conn.fetchval("SELECT now()")` — frontera del conteo por-run (Q7) [VERIFIED :134].
- bucle por-entidad `for e in entities: _upsert(conn, geo, e, geocoder)` acumulando new/resolved/skipped [VERIFIED :135-146].
- `in_db = count(*) FROM entity_source WHERE source_key=$1 AND seen_at >= $2` con $2=run_start [VERIFIED :152-154].
- `record_count_verdict(..., paths={db_ingested:in_db, fetched:len(entities), source_declared:declared}, tolerance=0.0)` [VERIFIED :159-164].
- `_upsert` [VERIFIED :77-114]: cascada geo :80-90, `INSERT INTO entity ... ON CONFLICT (cdp_code) DO UPDATE SET last_seen=now() RETURNING entity_ulid, (xmax=0) AS inserted` :95-104, upsert entity_source idempotente :109-113.

**(b) mecanismo al atomo.** El bucle es el corazon invariante pais-a-pais: idempotente, sin estado entre entidades salvo 3 contadores enteros (new/resolved/skipped). La honestidad del cierre descansa en UN detalle quirurgico: `run_start` se captura ANTES del bucle y `in_db` se acota con `seen_at >= run_start`, de modo que cuenta SOLO las filas entity_source TOCADAS este run (nuevas, o re-vistas via el `ON CONFLICT ... SET seen_at=now()` de _upsert [VERIFIED :109-113]). Sin esa cota el conteo se vuelve acumulativo: tras la 1a corrida completa `in_db == total historico de la fuente`, y una corrida posterior que pierda N entidades en silencio seguiria mostrando in_db==fetched==declared -> TRUSTWORTHY falso (este es justo el fix Q7 que el comentario :147-151 documenta).

**Independencia de las 3 vias.** `db_ingested` (PostgreSQL), `fetched` (longitud de la lista en memoria del adaptador) y `source_declared` (`declared_count()`, el oraculo de la fuente) son 3 mecanismos ortogonales; su igualdad exacta (tolerance=0.0) certifica que no hubo perdida silenciosa entre fetch y persistencia. El VAM certifica la CUENTA, no la correccion geografica de cada fila.

**(c) Costura ES→genérico.** discover(source_key) NO enhebra pais: lee solo source_key. GeoResolver.load(conn) se carga country-blind [VERIFIED discover.py:127], el geocoder idem, y el conteo in_db filtra por source_key+seen_at pero NO por country_code [VERIFIED :152-154]. Un adaptador extranjero corre por este mismo discover() sin que su country_code llegue al geo-scope, al mint ni al INSERT.

**Fix exacto.** Tras instanciar el adaptador leer `cc = adapter.country_code` y propagarlo: `geo = await GeoResolver.load(conn, country_code=cc)` (costura facet GeoResolver), pasar `cc` a `_upsert(...)` para el INSERT/mint country-scoped (costura facet _upsert), y namespacing del subject_key del VAM como `{cc}:{source_key}` para que el verdict no colisione entre paises. La matematica del quorum no cambia (enteros); solo se da identidad de pais a sus insumos y a su sujeto.

**(d) Riesgo adversarial concreto.** DE/FR/IT/PT: un roster extranjero corrido por discover() hoy resuelve geo contra el indice ES (bleed), mintea cdp 'CDP-ES-' e ingiere con entity.country_code DEFAULT 'ES' — y el VAM lo CIERRA TRUSTWORTHY porque las 3 vias (in_db/fetched/declared) cuadran numericamente aunque cada fila este geograficamente corrupta: el quorum certifica la cuenta, no la geografia. no-UE/ruido: si declared_count() devuelve None (fuente sin oraculo), el path source_declared cae y el quorum se apoya solo en db==http (2 familias), bajando la vara sin marca (costura facet VAM/oraculo).

**(e) Criterio de sellado + verificación multi-vía.** Sello: declared==fetched==in_db por 3 caminos ortogonales => TRUSTWORTHY. Verificacion multi-via: (1) golden ES: correr una fuente real y assert verdict byte-identico al historico; (2) prueba de honestidad por-run (Q7): correr 2 veces; en la 2a inyectar un skip silencioso de N y assert que el verdict NO es TRUSTWORTHY porque in_db(scoped)=fetched-N < fetched — un conteo acumulativo lo habria ocultado; (3) cross-pais (tras fix): correr ES y CC y assert que cada verdict referencia su propio subject_key y que ningun in_db cuenta filas del otro pais.

**(f) Herramienta NEXT-LEVEL (€0).** in-toto (atestacion de provenance del build) — Apache-2.0 [VERIFIED NEXT-LEVEL.md:143] — https://github.com/in-toto/in-toto. Eleva el cierre VAM de un `print(verdict)` volatil a una ATESTACION firmada que liga {git SHA del codigo, content-hash de la lista fetched, declared_count, in_db} -> verdict, anexada a un transparency log (Sigstore/rekor): cualquier tercero PRUEBA que 'este TRUSTWORTHY salio de exactamente estos insumos y este codigo' sin confiar en nosotros. Cierra el hueco de que hoy el verdict es una afirmacion en stdout, no un certificado no-repudiable. Ruta EUR0: in-toto + cosign keyless (OIDC) + rekor public-good, CPU-only.

### Familia E · Planificación recurrente (scheduler · gate · cadencia · breaker · lock)

---

<a id="f04"></a>

#### F04 · Gate AUTO-run por requires_env (defensa anti-ban)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `pipeline/discover_schedule.py:60` [VERIFIED] `requires_env: tuple[str, ...] = ()` — campo del dataclass `DiscoveryJob` (:53-60).
- `:77-83` [VERIFIED] `dork_municipal` declara `requires_env=("CARDEEP_SEARXNG_URL",)` con el racional inline: el fallback DuckDuckGo en un barrido nacional no acotado (~40k requests) arriesga ban (:80-82).
- `:120-130` [VERIFIED] `_gated(job)` -> devuelve la 1a env var requerida AUSENTE (`for var in job.requires_env: if not os.environ.get(var): return var`), si no `None`.
- `:194-199` [VERIFIED] `_tick`: `gate = None if only else _gated(job)` (:195) — un `--once VECTOR` explicito (con `only` set) BYPASA el gate; un vector gateado imprime `GATED ... skipped (not run, not failed)` y `ran[key] = {"gated": gate}` (:197-198), sin tocar `_record`/breaker.

**(b) Mecanismo al atomo**
El gate es una precondicion funcion-pura sobre el AUTO-run. `_due` (faceta 19) selecciona vencidos; antes de lanzar, `_tick` llama `_gated`. Si una env var requerida falta, el vector se reporta GATED y se salta SIN correr y SIN fallar — asi nunca incrementa `consecutive_fails` (breaker, faceta 20) ni escribe source_health. La ruta de operador `--once` setea `only`, que fuerza `gate=None` (:195), expresando intencion explicita de bypass. `_dry_run` (:220-224) muestra la marca GATE para que el operador vea que vectores estan bloqueados.

**(c) Costura ES->generico + fix exacto**
- **Costura:** la REGLA es generica; solo cambia QUE vectores del pais necesitan gating. El `requires_env` del dork esta hardcoded a `CARDEEP_SEARXNG_URL`. El vector de busqueda de un pais nuevo debe declarar su propio `requires_env` o martillara el motor.
- **Fix:** derivar el registry (y por tanto `requires_env`) por pais (faceta 18) — `DISCOVERY_REGISTRY` country-aware para que el dork de CC herede el mismo requisito SearXNG. Cero cambio en la logica de `_gated`/`_tick`. ES byte-identico.

**(d) Riesgo adversarial concreto**
Un pais cuyo vector de busqueda NO declare `requires_env` auto-corre un barrido nacional no acotado sobre el fallback DuckDuckGo y se gana un ban (perdida permanente de la fuente gratis). A la inversa, un vector GATED que contaminara el breaker quedaria auto-deshabilitado tras 3 'fallos' que en realidad eran skips de seguridad — el codigo lo evita correctamente al NO llamar `_record` en un skip gateado (:197-198).

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** un vector gateado se reporta GATED (ni corrido ni fallado), nunca se auto-ejecuta sin su env.
- **Via 1 (unit):** sin env SearXNG, `_tick` retorna `{"gated": "CARDEEP_SEARXNG_URL"}` y source_health/breaker intactos.
- **Via 2 (bypass):** `--once dork_municipal` corre igual (intencion del operador).
- **Via 3 (adversarial/distribuida):** aun con la env presente, un rate-limiter distribuido (herramienta) acota el rate AGREGADO para que procesos concurrentes no re-ganen el ban que el gate existe para evitar.

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**PyrateLimiter** — defense-tier-preselect + distributed-pacing [NEXT-LEVEL.md:301-308 VERIFIED]. URL https://github.com/vutran1710/PyrateLimiter (MIT, EUR0). Token-bucket distribuido (PostgresBucket/RedisBucket/MultiprocessBucket) que reusa el PG existente, de modo que cosechar desde N procesos/maquinas respeta el limite AGREGADO — el gate dice 'no corras sin endpoint seguro', PyrateLimiter anade 'y aun asi, pacelo entre todos los workers'. Alternativas: redis-cell (GCRA exacto), limits; complementa Healthchecks (dead-man switch externo [NEXT-LEVEL.md:560-567]).

---

<a id="f10"></a>

#### F10 · Lanzador _run_vector + auditoria _record (cero EUR)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED pipeline/discover_schedule.py:133-183].** `_record` [VERIFIED :133-160]: docstring (:135) "EUR0 source_health upsert for a discovery run (no harvest side-effects)"; inserta `harvest_run` de auditoria (:137-139); en exito hace upsert `source_health` con `consecutive_fails=0, status='healthy'` ON CONFLICT (:141-148); en fallo escala `consecutive_fails+1` y `status = CASE WHEN ...+1 >= 3 THEN 'down' ELSE 'degraded'` (:150-160). `_run_vector` [VERIFIED :163-183]: `cmd = [sys.executable, "-m", "pipeline.discover", job.vector]` (:166), env recipe-first `{**os.environ, ..., **job.env}` (:167), `subprocess.run(..., timeout=SUBPROCESS_TIMEOUT_SEC, ...)` (:170), `TimeoutExpired -> return -1, None` (:172-174), parsing TEXTUAL de `"] new="` (:177-182).

**(b) Mecanismo al atomo.** El discovery NO posee vehiculos; usar el `record_run` del harvest dispararia side-effects sin sentido (reconcile_gone/coverage), de ahi el upsert EUR0 PROPIO (:135). `_run_vector` lanza un subproceso `python -m pipeline.discover <vector>` con env recipe-first, captura stdout, y extrae el conteo `new=` parseando texto del log (:177-182) — acoplamiento TEXTUAL fragil al formato de `discover()`. El timeout (`SUBPROCESS_TIMEOUT_SEC`, :170) acota pero ENMASCARA un vector colgado: si el subproceso se cuelga, se consume el timeout completo antes del `-1,None`. Cada tick deja rastro en `harvest_run` + `source_health` visible al watchdog, sin disparar gates de harvest ajenos. El breaker se alimenta de `consecutive_fails` en `source_health` (:157), clavado por `source_key` pelado (sin dimension pais).

**(c) Costura ES→genérico.** Dos costuras: (1) el parsing de `new=` (:177-182) esta acoplado TEXTUALMENTE al formato de log de `discover()` — un cambio de formato devuelve `None` y la metrica de filas se pierde en silencio. (2) `source_health` se clava por `source_key` pelado (:142, sin `country_code`): dos paises con el mismo `source_key` ('osm','overture') contienden en la misma fila de salud/breaker. El lanzador en si es generico (subprocess + env recipe-first + timeout).

**Fix exacto.** Sustituir el parsing textual por un canal estructurado: `discover()` escribe el conteo a una columna/payload (p.ej. `harvest_run.rows` o una last-line JSON en stdout) que `_run_vector` lee sin regex de log. Y clavar `source_health`/breaker por `(country_code, source_key)` para aislar paises. El upsert EUR0 y el aislamiento del harvest se preservan; ES byte-identico para `source_key` ES.

**(d) Riesgo adversarial concreto.** Cualquier pais: si `discover()` cambia el formato `] new=` el parsing (:178) devuelve `None` y la fila se cuenta como 0 filas -> metrica perdida en silencio. DE/FR con `source_key` compartido ('overture','osm'): la fila `source_health` de uno marca al otro como 'reciente'/'healthy', y el breaker de uno apaga o mantiene vivo al otro (faceta breaker/_due). Operativo: un vector colgado consume el `SUBPROCESS_TIMEOUT_SEC` completo antes de fallar, enmascarando el cuelgue. Ruido: un subproceso que imprime '] new=' en un log de debug confunde el parser.

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) cada tick deja fila en `harvest_run` + `source_health` consultable por el watchdog (auditoria append-only). (2) El conteo de filas se recupera por canal estructurado, no por regex — test que asevera robustez ante cambio de formato de log. (3) Aislamiento pais: un vector ES y uno DE con el mismo `source_key` tienen filas de salud DISTINTAS (clave compuesta). (4) Un vector colgado se detecta por liveness externo ANTES de agotar el timeout.

**(f) Herramienta NEXT-LEVEL (€0).** **Procrastinate** — MIT, EUR0 [VERIFIED https://github.com/procrastinate-org/procrastinate] (NEXT-LEVEL.md:555, cluster ops 'Bus de decisiones + drains como TAREAS DURABLES sobre Postgres'). Reemplaza el lanzador subprocess+parsing-textual por tareas durables sobre el PG existente: claim idempotente `FOR UPDATE SKIP LOCKED`, retry con backoff exponencial por tipo, y reanudacion a-mitad-de-vuelo tras crash — un vector colgado/muerto reanuda exactamente-una-vez sin perder el conteo. Complementos: **Healthchecks** (BSD-3-Clause, NEXT-LEVEL.md:563 'Dead-man switch EXTERNO') que detecta el cuelgue con reloj propio (lo que el watchdog in-process no puede), y **WinSW/Shawl** (MIT, NEXT-LEVEL.md:571 'Artefacto de servicio Windows VERSIONADO') para versionar el daemon Windows que hoy es prosa NSSM. Eleva el launcher de 'subprocess + regex de log + timeout-que-enmascara' a 'ejecucion durable con liveness certificado'.

---

<a id="f21"></a>

#### F21 · DiscoveryJob + DISCOVERY_REGISTRY (5 vectores)

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** Dataclass frozen [VERIFIED pipeline/discover_schedule.py:53-60]:
`DiscoveryJob(source_key, vector, cadence_hours, orthogonal: bool, env: dict=field(default_factory=dict), requires_env: tuple=())`. `vector` es el argumento de `python -m pipeline.discover <vector>`; `orthogonal` marca si es lista MSE (lists.py) o vector dependiente/resolucion; `requires_env` lista env vars que GATEAN el auto-run.
DISCOVERY_REGISTRY [VERIFIED :65-84] = 5 entradas confirmadas:
- `borme_cnae` cadence_hours=24, orthogonal=True, env={CARDEEP_BORME_DAYS:"1"} [VERIFIED :66-68]
- `collapse_invisible` cadence_hours=168, orthogonal=False [VERIFIED :69-71]
- `overture` cadence_hours=720, orthogonal=True [VERIFIED :72-73]
- `graph_recursive` cadence_hours=720, orthogonal=False, env={CARDEEP_GRAPH_LIMIT:"200"} [VERIFIED :74-76]
- `dork_municipal` cadence_hours=2160, orthogonal=True, requires_env=('CARDEEP_SEARXNG_URL',) [VERIFIED :77-83]
Constantes vecinas: `BREAKER_TRIP_AT=3` [VERIFIED :49], `_LOCK_KEY=0x43415244+1` (distinto del lock del harvest) [VERIFIED :50], `TICK_INTERVAL_MINUTES` (default 60) y `SUBPROCESS_TIMEOUT_SEC=21600`=6h [VERIFIED :47-48]. `_seed` inserta/refresca una fila source_health por vector (idempotente, EUR0) [VERIFIED :87-94].

**(b) mecanismo al atomo.** El registro es una tabla plana de despacho declarativo: la maquinaria de planificacion (_due / breaker / advisory-lock / gate / launcher, facetas 19-23) es INVARIANTE pais-a-pais; solo cambia el CONTENIDO del dict. Las cadencias son literales horarios calibrados al volumen de delta ES (24h registral por la velocidad del BORME, 720h geo-POI por la inercia de Overture/OSM, 2160h dork por coste/ban). `env` lleva defaults recipe-first conservadores (un tick local es barato), overridables por env real en el barrido nacional del VPS.

**(c) Costura ES→genérico.** Cadencias y registro son globales y planos: literales horarios y claves source_key sin dimension pais. Un pais declara sus vectores ANADIENDO entradas (derivable por country_code, p.ej. ADAPTERS_BY_COUNTRY[cc]). El `orthogonal:bool` y `requires_env` son genericos; lo ES es el VALOR de la cadencia (sintonizado al churn espanol) y el supuesto de unicidad del source_key.

**Fix exacto.** (1) Dar identidad de pais al registro: `country_code` en DiscoveryJob (o clave compuesta (cc,source_key)) con `registry_for(cc)` filtrando. (2) Mover las cadencias del literal de modulo a un country-pack/GeoProfile versionado para que cada pais fije su interval. (3) source_key unico por pais para que source_health/_due/breaker no se pisen (costura compartida con facets 19-20 'Motor de vencimiento' y 'Circuit breaker'). Anadir un pais = anadir Jobs con su cadence/orthogonal/requires_env, cero cambio en la maquinaria.

**(d) Riesgo adversarial concreto.** DE/FR/IT/PT: cadencias hardcoded (24/168/720/720/2160h) calibradas al volumen ES; un pais con otra tasa de delta barre de mas (coste + superficie de ban) o de menos (staleness del censo). Dos paises con el mismo source_key generico ('overture','osm') comparten la fila source_health -> el _due/breaker de uno marca 'reciente' o 'roto' al otro. no-UE/ruido: un vector cuyo requires_env no se declare (un dork de otro pais) auto-correria sin su endpoint sin-cuota y se ganaria un ban (perdida de la fuente).

**(e) Criterio de sellado + verificación multi-vía.** Sello: anadir pais = anadir Jobs; la maquinaria no se toca. Verificacion multi-via: (1) biyeccion source_health<->registry<->lock_key por pais activo = 0 UNMAPPED / 0 ORPHAN; (2) golden: el registro ES produce los mismos 5 vectores con sus cadencias historicas (24/168/720/720/2160); (3) disjuntez cross-pack: assert que ningun source_key se repite entre dos packs activos; (4) un Job con requires_env no satisfecho se reporta GATED, no corrido ni fallado (costura facet Gate).

**(f) Herramienta NEXT-LEVEL (€0).** river (deteccion de cambio online: ADWIN / Page-Hinkley) — BSD-3-Clause [VERIFIED NEXT-LEVEL.md:579] — https://github.com/online-ml/river. Eleva la cadencia de constante-de-modulo ES a AUTO-AJUSTABLE: corre incrementalmente sobre el stream de filas-cambiadas por run de cada fuente (historial harvest_run) y sube `harvest_interval_hours` cuando la fuente se aplana / lo baja cuando churnea, por-CC, reduciendo ban y trabajo inutil, EUR0/CPU con memoria sublineal. Complementos: 'Guard de drift de registry/semilla como CONTRATO TIPADO (Pydantic, MIT [VERIFIED NEXT-LEVEL.md:587])' convierte el hueco silencioso de onboarding (registry sin semilla o viceversa) en build CI ROJO via biyeccion validada; 'transitions/pytransitions (MIT [VERIFIED :595])' para una FSM cover(CC) guard-gated si el funnel de campana se formaliza.

---

<a id="f27"></a>

#### F27 · Motor de vencimiento de cadencia (_due)

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED `pipeline/discover_schedule.py:101-117`].** `_due(conn) -> list[str]`: `SELECT source_key, harvest_interval_hours, last_ok, last_fail, consecutive_fails FROM source_health WHERE source_key = ANY($1::text[])` con `list(DISCOVERY_REGISTRY)` como arg [:103-106]. Por fila: si `(consecutive_fails or 0) >= BREAKER_TRIP_AT(3)` -> `continue` (breaker abierto, acopla faceta 20) [:110-111]; `last = last_ok or last_fail` [:112]; `overdue_h = inf if last is None else (now-last).total_seconds()/3600.0` [:113]; vence si `overdue_h >= (harvest_interval_hours or 0)` [:114]; acumula `(overdue_h, source_key)`, `due.sort(reverse=True)` (más vencido primero), `return [k for _o,k in due]` [:115-117]. `BREAKER_TRIP_AT=3` [:49]; `_seed` siembra `source_health.harvest_interval_hours` desde el registro [:87-98]; las 5 cadencias son literales: borme 24h, collapse 168h, overture 720h, graph 720h, dork 2160h [:65-84]. El estado vive en `source_health`, clavado por `source_key` PELADO (sin dimensión país). La matemática de vencimiento es país-invariante; el CONTENIDO (cadencias) y el NAMESPACE de la clave son las costuras.
**(b) Costura ES->genérico (dos capas).** (1) Namespace: `source_health` se clava por `source_key` solo; dos países que reúsan una clave genérica ('overture','osm','graph_recursive') CONTIENDEN en la misma fila de salud. (2) Calibración: los literales 24h/168h/720h/2160h están afinados al volumen de delta ES; otro país con otra tasa de cambio barre de más (coste/ban) o de menos (staleness).
**(c) Fix exacto.** Namespace: clave compuesta — prefijar el registro/source_key por país ('DE:overture') o añadir columna `country_code` a `source_health` y cambiar el WHERE a `source_key = ANY($1) AND country_code=$2`, derivando `DISCOVERY_REGISTRY` por país (ADAPTERS_BY_COUNTRY, faceta 3/18). Estructural, sin librería. Calibración: gobernar `harvest_interval_hours` desde el delta observado por (país, fuente) en vez de un literal de módulo.
**(d) Riesgo adversarial.** Colisión de clave: DE y ES registran ambos 'overture'. ES corre overture y escribe `source_health['overture'].last_ok=now`; el `_due` de DE lee la MISMA fila -> ve 'recién corrido' -> DE-overture NUNCA vence (inanición), O el fallo de DE dispara el breaker que silencia ES-overture. El breaker (faceta 20), sobre la misma clave, amplifica el sangrado cross-país. Mismatch de cadencia: el equivalente-BORME PT publica semanal, no diario -> el literal 24h lo barre 7x de más (ban); un marketplace FR de alto churn a 720h se queda stale.
**(e) Sellado + verificación multi-vía.** (1) Un vector vence IFF su cadencia transcurrió Y el breaker no está disparado — unit test con filas `source_health` sintéticas (`last_ok` en la frontera ± epsilon). (2) Aislamiento por-país: sembrar ES+DE con 'overture'; correr ES-overture NO debe marcar DE-overture como reciente (assert DE sigue venciendo) -> prueba clave país-namespaced. (3) Orden: más-vencido-primero estable. (4) Interacción con breaker: 3 fallos consecutivos de DE no afectan el estado de vencimiento de ES.
**(f) Herramienta nivel-inalcanzable.** river (BSD-3-Clause, EUR0) — https://github.com/online-ml/river [VERIFIED NEXT-LEVEL:576-582]. Eleva la mitad de calibración: detectores de cambio ONLINE (ADWIN, Page-Hinkley) corren incrementalmente sobre el stream de tasa-de-cambio de cada fuente (filas cambiadas por run en `harvest_run`) y proponen `harvest_interval_hours` por (país, fuente) — fuentes que se aplanan suben el intervalo, las que churnean lo bajan, con cota dura [min,max] por tier. Sustituye los literales ES-afinados por una cadencia APRENDIDA por-CC (framing explore/exploit con MABWiser; `ruptures` BSD-2 para calibrar semillas offline). Honesto: river eleva la calibración; la costura de colisión de clave es un fix estructural de clave compuesta, no una librería.

---

<a id="f33"></a>

#### F33 · Circuit breaker del scheduler

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion del code_hint [VERIFIED]**
- `BREAKER_TRIP_AT = 3` [VERIFIED pipeline/discover_schedule.py:49].
- En `_due` [VERIFIED discover_schedule.py:101-117]: `if (r["consecutive_fails"] or 0) >= BREAKER_TRIP_AT: continue` [VERIFIED discover_schedule.py:110-111] excluye el vector disparado de los vencidos.
- En `_record` rama-fallo [VERIFIED discover_schedule.py:149-160]: `INSERT INTO source_health ... ON CONFLICT (source_key) DO UPDATE SET last_fail=now(), consecutive_fails = source_health.consecutive_fails + 1, status = CASE WHEN source_health.consecutive_fails + 1 >= 3 THEN 'down' ELSE 'degraded' END` [VERIFIED discover_schedule.py:154-159]. Rama-ok resetea `consecutive_fails = 0, status = 'healthy'` [VERIFIED discover_schedule.py:140-148].

**(b) Mecanismo al atomo**
3 fallos consecutivos -> el vector deja de aparecer en `_due` (no auto-corre) hasta un exito que resetea el contador a 0. La escalada de status healthy->degraded->down protege a la fuente externa de martilleo. El estado completo (last_ok/last_fail/consecutive_fails/interval/status) vive en una fila de `source_health`.

**(c) Costura ES->generico + fix exacto**
El umbral 3 es generico. El estado vive en `source_health` clavado por `source_key` PELADO — el `ON CONFLICT (source_key)` [VERIFIED discover_schedule.py:94,145,151] y el `_seed`/`_due` operan SIN dimension pais. Dos paises con el mismo `source_key` generico ('overture','osm') contienden la MISMA fila. Fix: clave compuesta `(source_key, country_code)` en `source_health` (PK/UNIQUE) o `source_key` namespaced por pais ('overture@DE'); `_due` (`WHERE source_key = ANY(...)` [VERIFIED discover_schedule.py:104-106]) y `_record` leen/escriben la fila country-scoped.

**(d) Riesgo adversarial concreto**
Si DE y ES comparten `source_key='overture'`: 3 fallos del barrido DE marcan 'overture' como `down` -> el vector NO corre para ES aunque ES este sano; o, al reves, el reset-en-exito de ES borra el `consecutive_fails` acumulado por DE y revive un vector que deberia estar cortado. Un GATED (env ausente, p.ej. `CARDEEP_SEARXNG_URL`) NO debe contaminar el breaker — se distingue de un fallo real (no incrementa `consecutive_fails`).

**(e) Sellado + verificacion multi-via**
- V1 (unit aislamiento): 3x `_record(ok=False)` sobre `(overture, DE)` deja `(overture, ES)` en `healthy`; un `_record(ok=True)` resetea SOLO su fila.
- V2 (state machine declarativa): formalizar las transiciones legales healthy->degraded->down->healthy y PROHIBIR saltos invalidos (transitions); el FSM prueba el invariante por construccion.
- V3 (dead-man externo): Healthchecks confirma 'daemon vivo == pings recibidos' — el breaker in-process es ciego a la muerte del propio proceso; un observador con reloj propio cierra ese punto ciego.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**transitions / pytransitions** (MIT, EUR0 [VERIFIED NEXT-LEVEL.md tabla:72 "Maquina de estados cover(CC) sobre 'transitions' (declarativo)"]) — modela el breaker como FSM declarativa por `(source_key, country)`: estados {healthy, degraded, down}, transiciones tipadas con guardas (trip@3, reset@ok), saltos ilegales imposibles por construccion; el estado por-pais es trivialmente correcto porque cada (vector,pais) tiene su propia maquina. URL: https://github.com/pytransitions/transitions [URL ASSUMED — la fila de tabla estaba truncada; licencia MIT y EUR0 [VERIFIED]]. **Companion de verificacion:** **Healthchecks** (BSD-3-Clause, EUR0 [VERIFIED NEXT-LEVEL.md:560-561]) https://github.com/healthchecks/healthchecks — dead-man switch EXTERNO (un check por (rol,CC)) que vigila al vigilante cuando el host entero cae.

---

<a id="f38"></a>

#### F38 · Advisory lock singleton + lease heartbeat

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- **`_LOCK_KEY = 0x43415244 + 1`** [VERIFIED pipeline/discover_schedule.py:50] `# 'CARD'+1 — distinct from the harvest scheduler's singleton lock` (harvest usa 0x43415244 [VERIFIED pipeline/ops/lock_heartbeat.py:8-9]).
- **`_serve()`** [VERIFIED pipeline/discover_schedule.py:230-265]: importa `acquire_with_stale_retry, heartbeat_interval_minutes, record_heartbeat` [VERIFIED :235-239] y `require_prod_secrets` [VERIFIED :240]; `require_prod_secrets((raw,"CARDEEP_DSN_KW"),(_ASYNCPG_DSN,"CARDEEP_ASYNCPG_DSN"))` [VERIFIED :246]; `lock = psycopg2.connect(raw); lock.autocommit = True` [VERIFIED :247-248]; `if not acquire_with_stale_retry(lock,_LOCK_KEY): raise SystemExit(...)` [VERIFIED :252-253]; `record_heartbeat(lock,_LOCK_KEY,holder="discovery")` en acquire [VERIFIED :255] y job periodico cada `heartbeat_interval_minutes()` [VERIFIED :262-264].
- **`acquire_with_stale_retry`** [VERIFIED pipeline/ops/lock_heartbeat.py:309-338]: `pg_try_advisory_lock(lock_key)` [VERIFIED :331]; si tomado -> True; si no, `check_and_clear_stale_lease` y si stale reintenta UNA vez [VERIFIED :334-337]. Contrato: "pg_try_advisory_lock is the atomic mutex: this can NEVER acquire a lock a LIVE session still holds, so the retry carries no double-producer risk" [VERIFIED :325-328].
- **`is_lease_stale`** [VERIFIED pipeline/ops/lock_heartbeat.py:141-163]: None last_heartbeat = STALE [VERIFIED :157]; frontera estricta (edad debe EXCEDER el TTL [VERIFIED :163]); TTL default 6min = 3x el heartbeat de 2min [VERIFIED :88-89].
- **No-takeover declarado**: "We deliberately do NOT pg_advisory_unlock another session's lock... 'Auto-release' here means observable + retry on the next start once PG reaps the dead session, NOT instantaneous takeover" [VERIFIED pipeline/ops/lock_heartbeat.py:24-27].
- **Best-effort / inerte sin 0054**: lease en migrations/0054_scheduler_heartbeat.sql; el modulo NUNCA la crea; toda llamada DB envuelta best-effort, boot byte-identico sin 0054 [VERIFIED :31-37, 212-218].
- **`require_prod_secrets`** [VERIFIED pipeline/config_guard.py:140-170]: no-op salvo `CARDEEP_ENV=prod`; entonces `assert_safe_dsn` rechaza el marcador `cardeep_dev_only` [VERIFIED :99-106, :44].

**(b) El mecanismo al atomo**
Garantia single-producer en el host. Session advisory lock PG `0x43415244+1` (offset del harvest `0x43415244`, asi los dos daemons nunca contienden) sostenido en una conexion psycopg2 autocommit dedicada. `pg_try_advisory_lock` es el mutex atomico. Encima, una capa de OBSERVABILIDAD: la fila `scheduler_lease.last_heartbeat` bumpeada cada 2min; un sucesor la lee para distinguir "holder sano vivo" (fresco) de "holder previo presunto muerto" (stale > 6min TTL). El lease NUNCA hace unlock cross-session (inseguro); convierte un huerfano silencioso en un CRITICAL ruidoso + un acquire que reintenta-una-vez-si-stale. Best-effort: inerte y byte-identico sin migracion 0054.

**(c) Costura ES->generico**
El lock es **GLOBAL** (un scheduler de discovery por host), NO por-pais. `_LOCK_KEY` es constante de modulo. Si un pais necesitara su propio daemon (barridos paralelos por-CC), el lock key debe parametrizarse por pais (p.ej. `_DISCOVERY_LOCK_BASE + country_offset(CC)`) para que dos daemons de pais no se excluyan mutuamente — garantizando single-producer POR pais. El `holder` del lease ya soporta country-awareness (`holder=f"discovery:{CC}"`); NEXT-LEVEL:561 propone explicitamente "un check por (rol,CC)".

**(d) Riesgo adversarial concreto**
- **Inanicion por lock compartido**: arrancar un daemon DE mientras ES sostiene `0x43415244+1` -> DE hace `SystemExit("another discovery scheduler holds the advisory lock")` [VERIFIED :253] -> discovery DE NUNCA corre (inanicion de pais silenciosa).
- **Colision con harvest**: un key por-CC mal derivado que aterrice en `0x43415244` (harvest) -> discovery y harvest se bloquean mutuamente; ninguno corre.
- **2o scheduler sin lock**: arrancado bypaseando el lock (p.ej. DSN host distinto) duplica descubrimientos -> doble-conteo, rompe la cuenta por-run del VAM (facet 4).
- **Muerte del host** (Win11 unico, stack hoy CAIDO): el lease in-process se congela; nada externo lo nota; las ~7 alertas zombie + el lease quedan congelados [VERIFIED NEXT-LEVEL.md:562]. Country-agnostico pero es el riesgo operativo real.
- **Ruido**: lease stale por un tick lento-pero-limpio -> mitigado por TTL=3x heartbeat (un beat perdido nunca falso-positivea un holder sano) [VERIFIED :87-89].

**(e) Criterio de sellado + verificacion multi-via**
1. **Single-producer**: dos schedulers de discovery (mismo CC) -> el 2o `SystemExit`; nunca dos holders vivos.
2. **Aislamiento cross-daemon**: harvest (`0x43415244`) y discovery (`0x43415244+1`) nunca contienden — assert keys distintos por CC.
3. **Stale-retry**: `kill -9` al holder, reinicio -> `acquire_with_stale_retry` loguea CRITICAL nombrando al holder muerto y re-adquiere cuando PG reapa la sesion (superficie de test de lock_heartbeat).
4. **2a via**: estado 'down' de Healthchecks vs un `SELECT scheduler_lease.last_heartbeat` directo deben concordar en el corte temporal [VERIFIED NEXT-LEVEL.md:566].
5. **Adversarial**: simular reloj-deriva del host -> el reloj independiente de Healthchecks no se engana.

**(f) Herramienta NEXT-LEVEL**
**Healthchecks** (BSD-3-Clause) — https://github.com/healthchecks/healthchecks [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:563]. Cierra el hueco que el propio `lock_heartbeat.py` admite ("un watchdog in-process no puede detectar su propia muerte de proceso"): un dead-man switch con su PROPIO reloj. Cada tick pingea una URL de check por-(rol,CC); si el scheduler deja de pingar dentro de la grace window (2x cadencia, espeja SILENCE_MULTIPLIER), Healthchecks alerta fuera-de-banda — convirtiendo el huerfano por muerte-de-host en una alerta ruidosa nombrada por pais. EUR0 self-host. **Complementos**: **Procrastinate** (MIT) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555]: cola durable PG-nativa (claim-once FOR UPDATE SKIP LOCKED + retry/backoff) que cierra el no-promise declarado del modulo ("the lease is best-effort, NOT takeover") con reanudacion real de la unidad de trabajo. **WinSW** (MIT) — https://github.com/winsw/winsw [VERIFIED NEXT-LEVEL.md:571]: descriptor de servicio Windows versionado (parametrizado por %CARDEEP_COUNTRY%) con Restart=always + re-adquisicion limpia del lock tras reboot en el host real Win11 — el single-instance lo sigue garantizando el advisory lock PG, no el supervisor.

### Familia F · Capa MSE (sello · captura · listas · estimadores · triangulación)

---

<a id="f05"></a>

#### F05 · Sello compute + roll-up nacional honesto

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `pipeline/exhaustiveness/seal.py:27` [VERIFIED] `DEFAULT_THRESHOLD = 0.95`.
- `:39-47` [VERIFIED] `_seal_one(prov, seg, freqs, threshold)`: `e = est.estimate_stratum(freqs)`; `sealed = e.identified AND math.isfinite(cov_lower) AND cov_lower >= threshold`, con `cov_lower = e.coverage_lower` (la cifra conservadora `n_obs/ci_high`).
- `:50-162` [VERIFIED] `compute`: carga external_census si None (:68-69), lee patrones (:70-72), sella cada estrato (:74-82), y el **split HONESTO**: `identified` vs `unidentified` (:91-92), `n_obs_cert`/`n_obs_uncert` (:94-95), `n_hat_sum = sum sobre identified` = denominador certificado (:96), SE nacional por suma de half-widths/1.96 (:98-103), `nat_cov_lower = n_obs_cert / nat_ci_high` (:107). Estratos uncertified reportados aparte, NO plegados como cubiertos (:140-143).
- **CRITICO [VERIFIED]:** external_census se CARGA (:68-69) y se guarda como `external_ref` en `_persist` (:179,195) pero NO se inyecta en `_seal_one`/`estimate_stratum` — el ajuste IGNORA `n_external`. Confirma la deuda 'Fase-4 hoy SIN implementar' [NEXT-LEVEL.md:133].

**(b) Mecanismo al atomo**
`compute` convierte el censo vivo en veredicto de cobertura. Por estrato: `estimate_stratum(freqs)` -> `Estimate(n_obs, n_hat, ci_high, identified)`. `_seal_one` sella sii identified AND `cov_lower>=0.95` usando el `cov_lower=n_obs/ci_high` CONSERVADOR (el punto nunca certifica). Roll-up nacional: el denominador certificado es la SUMA de `n_hat` por estrato sobre IDENTIFICADOS solo (:96); los estratos sin solapamiento suficiente (unidentified) tienen denominador DESCONOCIDO y se reportan como observed-but-uncertified (:140-143), nunca inflados a '100% cubierto'. Los CIs por estrato se combinan asumiendo independencia entre-estrato (varianzas suman, :103). Un fit nacional pooled se computa solo como cross-check flagged-unreliable (:109-114,150-160). El 100% es un INTERVALO (coverage_lower), nunca un entero.

**(c) Costura ES->generico + fix exacto**
- **Costura:** la matematica es INVARIANTE de pais (solo cambian los DATOS). La costura oculta es que la tupla de estrato es `(province_code, segment)` SIN country_code (facetas 27/30), asi los estratos de un 2o pais se FUNDEN en el roll-up de ES. Y external_census se carga pero NUNCA VINCULA el fit (la palanca Fase-4 esta dormida).
- **Fix:** (i) anadir country_code a la tupla de estrato + country-scope de read_patterns/_fetch_raw (migracion faceta 30, aditiva); la matematica intacta. (ii) inyectar `n_external` como margen-conocido / offset Poisson para que los estratos uncertified obtengan N fijado por un mecanismo INDEPENDIENTE. Golden ES monotono: los ya-sellados siguen sellados, solo se anaden nuevos-identificados.

**(d) Riesgo adversarial concreto**
Si los estratos vienen colapsados cross-pais (province '28' MX fundida con '28' Madrid ES), el roll-up nacional suma `n_hat` a traves de paises y el 'national sealed' MIENTE sin sintoma (:104-107 suma sobre un set contaminado). Un pais onboardeado SIN su census produce `national sealed=True` SIN ancla externa (triangulation devuelve no_anchor, :144-149) -> la 3a via independiente de verificacion se salta en silencio.

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** el split certified/uncertified es el corazon anti-maquillaje — un estrato de denominador desconocido NUNCA se pliega como 100% cubierto (:88-90,140-143); national coverage_lower>=0.95 sobre identificados solo.
- **Via 1 (unit):** estratos de libro producen coverage_lower conocido (estimadores pure-Python unit-tested, faceta 28).
- **Via 2 (R crosscheck):** Rcapture/LCMCR sobre estratos identified con k>=3 (:78-81 VERIFIED).
- **Via 3 (triangulacion):** census externo en banda 0.7-1.4 (:144-149); con la herramienta, el census VINCULA el fit y la banda pasa de sanity-check a denominador.

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**Censo externo VINCULANTE como margen-conocido (dga / SparseMSE)** [NEXT-LEVEL.md:132-139 VERIFIED]. URL https://cran.r-project.org/package=dga (GPL >=2, EUR0; corre bajo el bridge Rscript existente estimators_r.py). Inyecta el ancla censal por pais como total marginal conocido / offset Poisson `log(n_external)`, trasladando masa de uncertified a certified SIN inventar dato; el gate de sello pasa a `coverage_lower>=0.95 AND census-consistent`. El CSV de ancla YA existe por pais (countries/<CC>/census/). Alternativas: SparseMSE (estratos sparse/solapamiento-cero), PyMC, Rcapture.

---

<a id="f11"></a>

#### F11 · Persistencia del sello + tablas MSE ciegas al pais

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED pipeline/exhaustiveness/seal.py:165-217; migrations/0048_discovery_capture.sql].** `_persist` [VERIFIED seal.py:165-217]: `DELETE FROM exhaustiveness_estimate WHERE build_run_id=%s` (:172-173, replace por build); INSERT por estrato con `province_code, segment` (:180-198); fila nacional `province_code NULL, segment NULL` (:199-214). Esquema [VERIFIED 0048:36-44]: `discovery_capture` tiene `province_code char(2)`(:39) y `segment text`(:40) pero NINGUN `country_code`. `exhaustiveness_estimate` [VERIFIED 0048:55-74]: `province_code char(2)`(:58), `segment`(:59), sin `country_code`. Grep confirmo 0 ocurrencias de 'country' en 0048. La vista `v_exhaustiveness_seal` (0048:82-106) toma el ultimo build sin dimension pais.

**(b) Mecanismo al atomo.** `_persist` materializa el sello: borra-y-reescribe por `build_run_id` (append-only por build, preserva OUTPUTS historicos) y puebla `exhaustiveness_estimate` por estrato `(province_code, segment)` mas una fila nacional `(NULL, NULL)`. La ROTURA es que el estrato es char(2) de provincia SIN pais: `discovery_capture.province_code` y `exhaustiveness_estimate.province_code` son ciegas al pais — deuda NETA que los playbooks de replicacion (que cubren geo/entity) NO enumeran. El `build_run_id` preserva los OUTPUTS pero NO un snapshot reproducible de los INPUTS (matriz de captura, anclas censales, version de estimador): sin eso, la serie temporal de `coverage_lower` (saturacion) es drift disfrazado de medicion.

**(c) Costura ES→genérico.** Deuda de esquema: `discovery_capture` (0048:36-44) y `exhaustiveness_estimate` (0048:55-74) tienen `province_code char(2)` SIN `country_code` — el estrato es `(province, segment)`, no `(country, province, segment)`. La fila nacional `(NULL,NULL)` (seal.py:199-214) suma TODOS los paises. Costura adicional: el `build_run_id` versiona outputs pero no hay snapshot content-addressed de los inputs del sello.

**Fix exacto.** Migracion ADITIVA (0054+) que anade `country_code char(2) NOT NULL DEFAULT 'ES'` a `discovery_capture` y `exhaustiveness_estimate`, lo incorpora a la tupla de estrato y a la PK/indices, y country-scope `_fetch_raw` (faceta build). `_persist` pasa el estrato de `(province, segment)` a `(country, province, segment)` y la fila nacional a una por pais `(country, NULL, NULL)`. La matematica del estimador NO se toca. ES byte-identico (default 'ES'); rollback = DROP COLUMN.

**(d) Riesgo adversarial concreto.** Cualquier 2o pais: sin `country_code` en estas tablas, sellar DE contamina el sello de ES en silencio — `province_code '28'` de Mexico y '28' (Madrid) se FUSIONAN en un estrato (faceta read_patterns) y el roll-up suma N_hat de ambos. La fila nacional `(NULL,NULL)` suma a traves de paises -> 'sealed nacional' MIENTE sin sintoma. DRIFT doc-vs-codigo: los playbooks no listan esta deuda -> un onboarder sella un 2o pais creyendo el esquema listo. Sin snapshot de inputs, la serie `coverage_lower` mezcla cambios de dato con cambios de cobertura (saturacion falsa).

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) el estrato pasa a `(country,province,segment)` sin tocar la matematica — golden que asevera que ES da el mismo `coverage_lower` antes/despues de la migracion. (2) `SELECT count(*) FROM exhaustiveness_estimate WHERE country_code IS NULL` == 0 tras la migracion (no quedan filas ciegas). (3) La fila nacional es una POR PAIS; un test asevera que sellar DE no cambia ninguna fila ES. (4) `build_run_id` reconstruible: re-correr un build desde inputs hash-pineados da `coverage_lower` byte-identico.

**(f) Herramienta NEXT-LEVEL (€0).** **DVC (Data Version Control)** — Apache-2.0, EUR0 [VERIFIED https://github.com/iterative/dvc] (NEXT-LEVEL.md:151, cluster discovery-trust 'Versionado content-addressed de inputs del sello'). Pone las anclas censales, las membresias de lista y la matriz de captura materializada bajo almacenamiento content-addressed, de modo que cada `build_run_id` referencie hashes inmutables y re-correr el build historico tire los inputs EXACTOS — cerrando el hueco donde el append-only-por-build_run_id preserva outputs pero no inputs. Complementos: **OpenLineage + Marquez** (Apache-2.0, NEXT-LEVEL.md:159) para el linaje fuente->estrato->coverage_lower (ve que pais/lista movio el sello), e **in-toto** (Apache-2.0, NEXT-LEVEL.md:143) para la atestacion firmada del sello. Eleva la persistencia de 'append-only de outputs' a 'sello bit-reproducible con linaje auditable'.

---

<a id="f16"></a>

#### F16 · Taxonomia de listas ortogonales (bucket_for) + fallo-ABIERTO

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/exhaustiveness/lists.py:27-45] `_EXACT: dict[str,str]` con claves ES: osm/overture/geo_sweep->GEO, autocasion_census->CENSUS, dgt_cat->DGT, aedra/aecs/acevas->ASSOC, dork_municipal->DORK, borme_cnae->REG, graph_recursive->GRAPH, collapse_invisible->COLLAPSE.
- [VERIFIED pipeline/exhaustiveness/lists.py:49] `ORTHOGONAL_LISTS = ('GEO','CENSUS','DGT','ASSOC','OEM','DORK','REG')` — **7 buckets**.
- [VERIFIED pipeline/exhaustiveness/lists.py:65-74] `bucket_for(source_key)`: si en `_EXACT` -> `_EXACT`; elif `startswith('oem_')` o `'mercedes'` -> OEM; elif `'oficial' in` o `endswith('_new_stock')` -> OEM; **else `return 'MKT'` (:74)**.

**(b) Mecanismo al atomo**
`bucket_for` es el clasificador de mecanismo-de-captura: source_key -> un bucket de ortogonalidad. El MSE trata GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG como listas ortogonales (lists.py:49) y EXCLUYE MKT/GRAPH/COLLAPSE (sesgo marketplace / dependencia de grafo / resolucion). La clasificacion es: override exacto (:67) -> prefijo oem_/oficial (:69-72) -> else MKT (:74). El fallback ES LA ROTURA: un source_key DESCONOCIDO cae a MKT, que esta EXCLUIDO del set MSE -> una lista ortogonal no registrada se DESCARTA en silencio. **Falla en ABIERTO** (hacia exclusion): el coverage_lower se computa sobre un set de listas oculta-incompleto.

**(c) Costura ES->generico**
`_EXACT` es todo claves ES; `bucket_for` no tiene dimension pais. Una lista autoritativa extranjera (IT Registro Imprese, IT PRA, IT UNRAE, DE KBA) no esta en `_EXACT` ni casa oem_/oficial -> cae a MKT -> desaparece del MSE. La taxonomia debe ser country-aware: o `_EXACT` por pais, o leer `adapter.orthogonal_bucket` (la costura declarada en el contrato SourceAdapter).

**(d) Riesgo adversarial concreto**
Registro Imprese (IT) / PRA / UNRAE no estan en `_EXACT` -> caen a MKT -> la lista autoritativa del pais DESAPARECE de la matriz captura-recaptura -> con <2 listas ortogonales el estrato queda unidentified o el `coverage_lower` SUB-CUENTA -> sello falso TRUSTWORTHY o sello falsamente bajo, ambos SILENCIOSOS. Es el bug exacto que el insumo nombra "falla en ABIERTO".

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** ninguna lista del pais cae a MKT por defecto; un source ortogonal sin mapear FALLA el build.
- via1: mecanico fail-closed — inyectar un source_key foraneo ausente del mapa de buckets -> la expectativa FALLA el build (espejo del invariante COUNTRY-PROOF).
- via2: ES byte-identico — los 25 source_keys ES mapean a los mismos buckets (golden).
- via3: aditivo por-pack — la suite de expectativas se versiona por country pack; cada source ortogonal del pack mapea a un bucket no-MKT.

**(f) Herramienta de nivel inalcanzable**
**Great Expectations / Pandera** (contrato de datos PRE-sello). Gate de calidad que corre ANTES de `seal.compute`: expectativas sobre los inputs de captura — "NINGUN source_key cae en silencio a MKT", cada clase ortogonal tiene >=1 source real, los codigos de region casan el ancho de la rejilla geo del pais. Si una expectativa falla, el build se NIEGA a sellar. Convierte la precondicion estadistica oculta del `bucket_for` fail-open en un contrato ejecutable, versionado y bloqueante. [VERIFIED NEXT-LEVEL.md:164-170] Apache-2.0, EUR0, https://github.com/great-expectations/great_expectations. Complemento: GLEIF/LEI registra un REG real para que registros foraneos no caigan a MKT por falta de adaptador.

---

<a id="f17"></a>

#### F17 · Triangulacion externa DIRCE (census)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/exhaustiveness/triangulation.py:24-63] `load_external_census(path=None, country_code=DEFAULT_COUNTRY)`: `p = path or (census_dir(country_code) / CENSUS_CSV_NAME)`; `if not p.exists(): return {}`; lee columnas `province_code,segment,n_external`; prov/seg vacios -> clave `None` (ancla nacional/all-segment); devuelve `{(prov,seg): n}`. `CENSUS_CSV_NAME = 'dirce_cnae451.csv'` (:27).
- [VERIFIED pipeline/exhaustiveness/triangulation.py:66-81] `triangulate(n_hat, n_external)`: si `n_external is None or <= 0` -> `no_anchor`; `ratio = n_hat/n_external`; `>1.4` -> n_hat_high; `<0.7` -> n_hat_low; else `consistent`.
- [VERIFIED pipeline/exhaustiveness/triangulation.py:84-88] `status()`: "loaded N anchors" o "pending external census".
- [VERIFIED triangulation.py:50] `census_dir(country_code)` -> **YA parametrico por pais**; el modulo es ES solo por DATOS/clasificacion (CNAE 451), no por codigo.

**(b) Mecanismo al atomo**
La TERCERA via de verificacion (tras VAM intra-run y MSE cross-list), de mecanismo INDEPENDIENTE (legal/fiscal). `load_external_census` carga `{(province,segment): N_ext}` desde un CSV por-pais (ya parametrico: `census_dir(country_code)`, :50). `triangulate` compara `N_hat/N_ext` contra una banda FIJA `[0.7, 1.4]` -> consistent / n_hat_high / n_hat_low / no_anchor. Es OPCIONAL: CSV faltante -> `{}` -> `no_anchor`, y el sello puede pasar con captura-recaptura SOLA, saltando el unico cross-check independiente. Ademas es NO-VINCULANTE: reporta verdict pero el objetivo Fase-4 de ALIMENTAR `n_external` como margen-conocido al ajuste no esta hecho (NEXT-LEVEL:133 cita seal.py:42-47 ignorando n_external).

**(c) Costura ES->generico**
El codigo YA es parametrico (`census_dir(cc)`, arg `country_code`). La costura es DATOS + clasificacion: el CSV (CNAE 451) es ES; un pais provee su extracto (KBA/Destatis DE, ANFIA/UNRAE IT) con mapeo NACE/WZ/NAF->segment. La banda fija `[0.7,1.4]` (triangulation.py:75-77) es tambien una constante calibrada.

**(d) Riesgo adversarial concreto**
Un pais onboardeado SIN su census produce `national sealed=True` SIN ancla externa -> la 3a via (banda 0.7-1.4) se pierde en silencio. Peor: un diseno de ancla UNICA deja que UN census sesgado mueva el denominador sin contraste. La banda ES `[0.7,1.4]` puede no encajar un pais cuyo registro sobre/sub-cuenta dealers estructuralmente.

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** `N_hat` ancla en `[0.7,1.4]` contra el census del pais O reporta `no_anchor` honesto; un sello no puede afirmar 100% sin el ancla presente.
- via1: ES golden — con DIRCE presente, las anclas cargan y el verdict de banda es inalterado.
- via2: aislamiento de pais — `census_dir(CC)` resuelve el CSV de CC, no el de ES; un ancla CC nunca contamina estratos ES.
- via3: monotonia (si se adopta margen-vinculante) — fijar con el census MANTIENE sellados los estratos sellados y solo ANADE nuevos-identificados (golden cero-regresion).

**(f) Herramienta de nivel inalcanzable**
**Eurostat Structural Business Statistics** (panel de anclas MULTIPLES). Convierte la triangulacion de UN ancla (DIRCE) a un PANEL independiente por pais (Eurostat SBS conteo de establecimientos NACE G45.1, conteos GLEIF/LEI, open-data de oficinas estadisticas nacionales): el sello debe ser consistente con la banda MAYORITARIA, y el DESACUERDO entre anclas se vuelve SENAL de distrust, no un promedio silencioso. [VERIFIED NEXT-LEVEL.md:188-194] Reutilizacion libre (Decision 2011/833/EU), EUR0, https://ec.europa.eu/eurostat/web/structural-business-statistics. Complemento (NEXT-LEVEL:132-138): "Censo externo VINCULANTE como margen-conocido" via dga/SparseMSE (bridge R) hace el ancla BINDING — convierte masa uncertified en certified.

---

<a id="f22"></a>

#### F22 · Taxonomia DEALER_KINDS → segmento (estratos)

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** Enum de 9 tipos [VERIFIED pipeline/exhaustiveness/capture.py:19-29]:
`DEALER_KINDS = (compraventa, concesionario_oficial, desguace, garaje, subasta, importador, cadena, rent_a_car_vo, oem_vo_portal)`.
Mapa kind->segmento `_SEGMENT` [VERIFIED :32-42]: compraventa->compraventa, concesionario_oficial->concesionario, desguace->desguace, y los 6 restantes (garaje/subasta/importador/cadena/rent_a_car_vo/oem_vo_portal)->'otros'. `segment_for(kind)` con default 'otros' [VERIFIED :45-46].
Filtro DURO: `_fetch_raw` une entity_source -> entity -> v_dealer_resolved con `WHERE e.kind::text IN %s` ligado a DEALER_KINDS, en ambas ramas: resolved [VERIFIED :88-90] y splink [VERIFIED :72-74]. Un kind fuera del enum NUNCA entra a n_obs.

**(b) mecanismo al atomo.** El enum define DOS cosas a la vez: (1) QUE entidades son 'dealer' para el MSE (el `WHERE kind IN`), y (2) el eje 'segment' del estrato (province_code x segment ~ 200 estratos, §2.2). El estrato es la UNIDAD DE SELLO de la captura-recaptura; el segmento colapsa 9 kinds a 4 clases para que cada celda tenga masa suficiente (n_obs) y el estimador no degenere. Es un filtro append-only de admision al denominador: lo que no es uno de los 9 kinds es invisible al MSE. La capture unit es `v_dealer_resolved.resolved_ulid` (dedup cross-source colapsa a 1 captura por lista [VERIFIED capture.py:1-9,80-90]).

**(c) Costura ES→genérico.** El enum de 9 y el mapa _SEGMENT son taxonomia ES (los tipos de punto de venta del mercado espanol). El `WHERE kind IN DEALER_KINDS` [VERIFIED capture.py:72,88] es un filtro DURO: un tipo foraneo fuera del enum se descarta sin error. Ademas _fetch_raw NO filtra por country_code (costura compartida con la facet 'Construccion de la matriz').

**Fix exacto.** (1) Hacer DEALER_KINDS y _SEGMENT table-driven desde el country-pack (enum extensible por pais) en vez de literal de modulo. (2) Cada pais declara sus tipos de dealer y su mapeo a los 4 segmentos canonicos (o a su propia rejilla). (3) Validar en CI que todo kind emitido por los adaptadores del pais pertenece al enum activo. El DTO ya transporta kind crudo; el mapeo categoria-pais->kind vive en el adaptador (costura facet DTO/pack).

**(d) Riesgo adversarial concreto.** PT/foraneos: un tipo de dealer sin equivalente ES (figura registral PT/IT propia) cae fuera del enum de 9 -> _fetch_raw lo TIRA -> denominador mutilado y coverage_lower SOBRESTIMA la cobertura (cuenta como cubierto un universo que excluyo entidades reales: numerador y denominador encogen juntos y el ratio miente al alza). DE/FR: si el adaptador fuerza un tipo foraneo al kind ES mas parecido, contamina el segmento y sesga el estrato. Ruido: un kind tipografico/no-canonico nunca entra a n_obs y desaparece sin marca.

**(e) Criterio de sellado + verificación multi-vía.** Sello: cada tipo de dealer del pais mapea a un segment y entra al MSE. Verificacion multi-via: (1) golden ES: los 9 kinds producen el split de segmentos historico; (2) cobertura del enum: assert que `DISTINCT kind` emitido por el roster del pais es subconjunto del enum activo (0 kinds huerfanos descartados por el WHERE IN); (3) contrato pre-sello (Great Expectations) que falla CERRADO si un kind del pais no mapea a segment; (4) cross-pais: el enum de CC es additive y no altera el de ES.

**(f) Herramienta NEXT-LEVEL (€0).** Snorkel (weak-supervision auto-labeler) — Apache-2.0 [VERIFIED NEXT-LEVEL.md:514] — https://github.com/snorkel-team/snorkel. Eleva la asignacion kind/segment de un mapa estatico ES a un etiquetador AUTO-MEJORABLE y country-portable: combina labeling functions de alta precision YA disponibles en el dato (membresia OEM->concesionario_oficial, keyword 'desguace/descontaminacion'->desguace, source=rent_a_car->rent_a_car_vo, objeto-social registral->compraventa) en una etiqueta probabilistica denoised, regenerada cada run conforme crece el censo, sin anotacion manual; cada pais re-autora sus LFs y el mapeo deja de ser un literal adivinado para ser un set trazable a su snapshot. Complemento de salida cerrada: Outlines (Apache-2.0 [VERIFIED NEXT-LEVEL.md:272]) si se quiere que un clasificador capa-2 emita UNICAMENTE un kind del enum (imposible alucinar fuera del vocabulario).

---

<a id="f28"></a>

#### F28 · Construccion de la matriz de captura (build)

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED `pipeline/exhaustiveness/capture.py:49-157`].** `DEALER_KINDS` (9-tupla) [:19-29]; `_SEGMENT` mapea kind->4 segmentos (compraventa/concesionario/desguace/otros) [:32-42]; `segment_for(kind)=_SEGMENT.get(kind,'otros')` [:45-46]. `_fetch_raw(conn, unit='resolved', splink_run_id=None)` ruta resolved [:77-92]: `SELECT dr.resolved_ulid, COALESCE(re.province_code, e.province_code) AS province_code, COALESCE(re.kind::text, e.kind::text) AS kind, es.source_key FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid JOIN v_dealer_resolved dr ON dr.entity_ulid=es.entity_ulid LEFT JOIN entity re ON re.entity_ulid=dr.resolved_ulid WHERE e.kind::text IN DEALER_KINDS` — NO filtra país, sólo la guarda DURA de kind; el `COALESCE(re.*, e.*)` toma la entidad RESUELTA para que dupes cross-source colapsen a la unidad resuelta. La ruta splink [:57-76] es igual con `COALESCE(sc.splink_cluster, dr.resolved_ulid)`. `build(build_run_id, dsn, replace=True, unit, splink_run_id)` [:95-157]: `raw=_fetch_raw` [:106]; colapsa a `seen: dict[(resolved_ulid,bucket) -> (province,seg)]` guardando la PRIMERA ocurrencia por `(resolved_ulid,bucket)` [:108-114] con `bucket=bucket_for(source_key)` [:110] (acopla faceta 24) y `seg=segment_for(kind)` [:111] (acopla faceta 25); `rows=[(ru,bucket,prov,seg,build_run_id)...]` [:115-118]; upsert `LIST_METADATA` en `discovery_list` (tabla ref) [:121-134]; si replace: `DELETE FROM discovery_capture WHERE build_run_id` [:135-139]; `executemany INSERT INTO discovery_capture (resolved_ulid,list_key,province_code,segment,build_run_id) ON CONFLICT (resolved_ulid,list_key,build_run_id) DO NOTHING` [:140-148]; retorna `{raw_links, capture_rows, distinct_resolved}` [:149-155]. La UNIDAD de captura es `resolved_ulid` (v_dealer_resolved) — el fix del viejo m=10: un dealer en OSM+autocasion colapsa a UNA captura por lista. Correcto y país-invariante; el DEFECTO es que `_fetch_raw` no scopea país.
**(b) Costura ES->genérico.** `_fetch_raw` selecciona TODA entidad dealer sin reparar en país. En cuanto un 2º país vive en `entity`, la matriz mezcla ambos. La tupla de estrato construida aquí es `(province_code, segment)` SIN `country_code` (propaga a facetas 27/30).
**(c) Fix exacto.** Añadir scope de país a ambas queries de `_fetch_raw`: `WHERE e.kind::text IN DEALER_KINDS AND e.country_code = %s` (bindeando el CC objetivo del build), y arrastrar `country_code` a la clave de colapso y a las filas de `discovery_capture` (acopla la migración aditiva de la faceta 30 que añade `country_code` a `discovery_capture`). `build()` gana parámetro `country_code`; el estrato pasa a `(country, province, segment)`.
**(d) Riesgo adversarial.** Con ES+DE ingeridos, `_fetch_raw` sin filtro devuelve la UNIÓN de dealers ES y DE; colapsan en el mismo espacio `(resolved_ulid, bucket)` y los mismos estratos `(province, segment)`. La provincia DE '28' (si algún código de 2 chars coincide) se FUSIONA con ES '28' (Madrid). La matriz se contamina EN EL ORIGEN -> todo estimador (faceta 28), sello (faceta 29) y roll-up hereda un denominador cross-país. PT/IT/FR idéntico. Peor: un kind foráneo fuera de `DEALER_KINDS` (faceta 25) lo tira el `IN`-list en silencio, mutilando el denominador.
**(e) Sellado + verificación multi-vía.** (1) Por entidad resuelta, exactamente 1 captura por bucket distinto — assert `raw_links >= capture_rows >= distinct_resolved` y unicidad `(resolved_ulid,bucket)`. (2) Aislamiento de país: sembrado ES+DE, `build(country='ES')` devuelve SÓLO resolved_ulids ES (assert 0 ulids DE en las filas). (3) Corrección-m: un dealer visto en 2 fuentes del MISMO bucket da 1 captura (sin doble conteo). (4) Integridad de estrato: cada fila `(country,province,segment)` internamente consistente; ninguna provincia pertenece a 2 países.
**(f) Herramienta nivel-inalcanzable.** Great Expectations (Apache-2.0, EUR0) — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL:164-170]. Contrato de datos PRE-build/PRE-sello que corre sobre los inputs de captura y FALLA EL BUILD (fallo-CERRADO) cuando: un código de región viola el ancho de la rejilla del país, una entidad de país foráneo se cuela en un build mono-país, un `source_key` cae en silencio a MKT (faceta 24 fallo-ABIERTO), o un estrato mezcla países. Convierte la precondición estadística oculta ('la matriz es mono-país y completa') en una expectations suite ejecutable, versionada y bloqueante por country-pack — la disciplina que PREVIENE mecánicamente el build contaminado en vez de detectarlo tras el sello mentiroso. Complemento: OpenLineage sobre `capture.build` para linaje del denominador [NEXT-LEVEL:157-162].

---

<a id="f34"></a>

#### F34 · Lectura de patrones 0/1 (read_patterns)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion del code_hint [VERIFIED]**
- `read_patterns(build_run_id, ...)` [VERIFIED pipeline/exhaustiveness/capture.py:160-218]. `buckets = orthogonal_buckets(include_mkt)` [VERIFIED capture.py:175]; query `SELECT resolved_ulid, province_code, segment, list_key FROM discovery_capture WHERE build_run_id=%s [+province_code/segment]` [VERIFIED capture.py:188-195] — SIN filtro de pais.
- Agrupa por unidad resuelta: `if list_key not in idx: continue` (MKT excluido cuando `include_mkt=False`) [VERIFIED capture.py:203-204]; `ukey = (prov, seg, resolved_ulid)` [VERIFIED capture.py:205]; `by_unit[ukey][2][idx[list_key]] = 1` [VERIFIED capture.py:208].
- Excluye el patron all-zero `if not any(pat): continue` [VERIFIED capture.py:213-214]; `stratum = (prov, seg)` [VERIFIED capture.py:215]; agrega `out[stratum][pat] += 1`.
- NOTA [VERIFIED capture.py:218]: devuelve `out, buckets` (TUPLA), pese a que el docstring dice "Returns {(province_code, segment): ...}" (drift menor doc-vs-codigo a corregir).

**(b) Mecanismo al atomo**
Produce `{(province, segment): {pattern_tuple: freq}}` sobre el orden de `orthogonal_buckets`; el all-zero (la celda no observada que el MSE estima) JAMAS entra al input de los estimadores; MKT se filtra si `include_mkt=False`. Cada unidad resuelta (cross-source deduped) aporta 1 vector 0/1 por estrato.

**(c) Costura ES->generico + fix exacto**
El estrato es `(province_code, segment)` SIN `country_code` [VERIFIED capture.py:205,215]; aguas abajo `discovery_capture.province_code` es `char(2)` sin pais (deuda de esquema migration 0048, NO cubierta por los playbooks geo/entity). Fix: migracion aditiva que anade `country_code` a `discovery_capture` (y a `exhaustiveness_estimate`), ensanchar la tupla de estrato a `(country, province, segment)`, anadir `WHERE country_code = %s` en `read_patterns`, y country-scope de `_fetch_raw` aguas arriba. La MATEMATICA del estimador no se toca (solo los DATOS por estrato).

**(d) Riesgo adversarial concreto**
`province_code='28'` de MX y `'28'` (Madrid) ES se FUSIONAN en un unico estrato -> el roll-up nacional del sello suma `N_hat` de ambos paises; no existe denominador sellado por-pais y el 'sealed nacional' miente sin sintoma. Ruido ortogonal: una lista que cae en silencio a MKT (bug `bucket_for` fail-ABIERTO, facet 24) desaparece del vector 0/1 -> `coverage_lower` sub-cuenta callado. PT/IT con grids de otro ancho rompen el `char(2)` antes incluso de la fusion.

**(e) Sellado + verificacion multi-via**
- V1 (golden ES): los patrones y frecuencias de ES son byte-identicos tras anadir `country_code`; un estrato CC y un estrato ES con el mismo `province_code` NUNCA se fusionan.
- V2 (contrato pre-sello fail-CERRADO): un gate que corre ANTES de `seal.compute` exige que el estrato lleve country, que los region codes casen el ANCHO de la rejilla del pais, que cada clase ortogonal tenga >=1 fuente real y que NINGUN `source_key` caiga en silencio a MKT.
- V3 (cuadre): suma de `freq` por estrato == numero de unidades resueltas con patron no-cero capturadas; cruza contra `distinct_resolved` de `build`.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**Great Expectations** (Apache-2.0, EUR0 [VERIFIED NEXT-LEVEL.md:167]) https://github.com/great-expectations/great_expectations — contrato de datos PRE-sello que falla CERRADO, no abierto: codifica las precondiciones estadisticas OCULTAS del estrato (lleva country, region casa el grid del pais, >=1 fuente por clase ortogonal, 0 source_key silenciado a MKT, all-zero correctamente excluido) como expectativas versionadas por country-pack que BLOQUEAN el build ante violacion. Convierte 'no tiramos en silencio la lista mas fuerte del pais' en invariante probado. **Alternativa:** Pandera (MIT) — schema-as-code equivalente integrable en el job db-tests.

---

<a id="f39"></a>

#### F39 · Estimadores captura-recaptura (Chapman/loglineal/robusto)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- **`chapman_point` / `chapman`** [VERIFIED pipeline/exhaustiveness/estimators.py:77-132]: N_hat=`((n1+1)(n2+1)/(m+1))-1` con varianza Seber [VERIFIED :79-83]; CI por bootstrap no-parametrico (`n_boot=4000, seed=20260620` [VERIFIED :91-92]); `ci_low=max(n_obs, p2.5)`, `ci_high=max(ci_low, p97.5)` [VERIFIED :120-121]; `confidence="low"` (2-listas es piso, nunca certificacion, §2.3 [VERIFIED :122]).
- **`loglinear_mse`** [VERIFIED pipeline/exhaustiveness/estimators.py:172-262]: Poisson GLM (statsmodels) sobre las 2^k-1 celdas observables, all-zero excluida [VERIFIED :147-157, 192-193]; seleccion greedy de interacciones pairwise por BIC [VERIFIED :217-236, max=6 :220]; `N_hat=n_obs+exp(intercept)` [VERIFIED :240-241]; CI delta-method [VERIFIED :242-245]; `confidence="high"` sii k_present>=3 [VERIFIED :246]; fallback degenerado a observado (`loglinear_failed`, confidence "none") si el GLM falla [VERIFIED :204-213].
- **`dependence_robust_bound`** [VERIFIED pipeline/exhaustiveness/estimators.py:268-292]: banda honesta, max N log-lineal sobre `{independiente} U {cada interaccion pairwise individual}`; lower=n_obs, upper=max(highs) [VERIFIED :283-292].
- **`IDENT_CAP=5.0`** [VERIFIED pipeline/exhaustiveness/estimators.py:304]; **`_mark_identified`** [VERIFIED :307-318]: identified sii `n_obs>0 AND isfinite(ci_high) AND n_hat<=cap AND ci_high<=cap AND confidence!="none"`; degrada "high"->"low" si no-identificado [VERIFIED :316-317].
- **`estimate_stratum`** [VERIFIED pipeline/exhaustiveness/estimators.py:321-373]: k>=3 -> loglinear ensanchado por robust_high [VERIFIED :342-350]; k==2 -> chapman [VERIFIED :352-360]; k<2 -> `single_list_no_estimate` (ci_high=inf, identified=False) [VERIFIED :363-373].
- **`coverage_lower`** [VERIFIED pipeline/exhaustiveness/estimators.py:66-71]: `n_obs/ci_high` (conservador, anti-maquillaje).
- **Contrato del modulo** [VERIFIED :1-7]: "the part of the system we cannot get wrong... zero external service dependencies (no DB, no R)... fully unit-tested against textbook values".

**(b) El mecanismo al atomo**
MSE multi-lista pure-Python. Un estrato = `{patron_captura(tupla 0/1): frecuencia}`, all-zero excluida (es la celda no observada que se estima). El dispatcher elige por `k_present` (listas con >0 capturas): K>=3 -> log-lineal Fienberg (Poisson GLM, interacciones BIC, CI delta) ensanchado por el techo dependence-robust; K==2 -> Chapman con CI bootstrap; K<2 -> solo piso observado. `_mark_identified` exige que N_hat este fijado (`<=5x n_obs`, CI finito) o marca unidentified (excluido del roll-up certificado). `coverage_lower = n_obs/ci_high` (usa la cota SUPERIOR de N -> conservador).

**(c) Costura ES->generico**
**NINGUNA por pais.** La matematica es invariante — solo cambian los DATOS (freqs por estrato). El modulo tiene cero conciencia de pais y cero constante pais-especifica. Es la unica faceta cuyo codigo NO se mueve al anadir un pais; lo que cambia es la calidad/ortogonalidad de las listas que alimentan los freqs (facets 24/25/26/27) y la tupla de estrato que porta el pais (facet 27/30).

**(d) Riesgo adversarial concreto (BAJO intrinseco — el riesgo entra por DATOS, no por el estimador)**
- **Fusion de estrato cross-pais** (bleed facet 27/30): freqs de provincia '28' mezclan capturas MX + ES -> un N_hat numericamente "correcto" sobre un input mentiroso; el estimador no puede detectarlo.
- **Lista ortogonal faltante** (facet 24 falla-ABIERTO a MKT): un estrato cae a k_present<3 -> piso Chapman (confidence "low") o k<2 -> unidentified -> los estratos del pais nunca certifican aunque la matematica sea correcta.
- **DE/FR/IT/PT**: si la lista autoritativa de un pais (Registro Imprese IT, KBA DE) cae de la matriz, IDENT_CAP marca unidentified (honesto) — pero el operador puede malinterpretar "muchos estratos unidentified" como fallo del estimador en vez de hueco del roster.
- **Borde numerico**: estrato con solapamiento explosivo (m0 enorme) -> ci_high explota -> `_mark_identified` marca unidentified (correcto, por diseno); el piso IDENT_CAP=5.0 (>=20% cobertura) es la guarda.
- **Ruido**: no-convergencia del GLM statsmodels -> fallback `loglinear_failed` (confidence "none") -> degrada honesto a piso-observado, nunca inventa.

**(e) Criterio de sellado + verificacion multi-via**
1. **Validacion textbook**: chapman/loglinear/robust unit-tested contra valores de libro (contrato del modulo).
2. **coverage_lower usa ci_high** (conservador) — un estrato con solapamiento insuficiente es unidentified, no sellado.
3. **Gate IDENT_CAP**: `N_hat<=5x n_obs AND CI finito`, si no uncertified (excluido del roll-up nacional).
4. **2a via (la herramienta)**: model-averaging bayesiano (dga) sobre el espacio de estructuras de interaccion — su mediana posterior debe coincidir con el punto log-lineal dentro de tolerancia, y el sello toma el MAS conservador de (cuantil 2.5% dga, ci_high Python).
5. **3a via**: triangulacion censo externo (facet 31) — `N_hat/N_ext in [0.7, 1.4]`.

**(f) Herramienta NEXT-LEVEL**
**dga: Capture-Recapture Estimation using Bayesian Model Averaging** (GPL >=2) — https://cran.r-project.org/package=dga [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:127]. De Johndrow/Lum/Ball (Human Rights Data Analysis Group), construido para "recuentos que aguantan un interrogatorio adversarial" (usado en tribunales para recuentos de victimas). Aumenta el unico log-lineal greedy-por-BIC (estimators.py:217-236) con promedio de modelos sobre TODO el espacio de estructuras de dependencia inter-lista, produciendo un POSTERIOR de N por estrato que YA integra la incertidumbre de seleccion-de-modelo en el intervalo — el CI honesto deja de ser condicional a un set de interacciones elegido. Corre como bridge Rscript offline (CPU, EUR0), asi el GPL NUNCA toca el served path — es una VIA de verificacion, no una dependencia linkada. Alternativas: LCMCR, SparseMSE, PyMC (un trio: model-averaging / latente / sparse sobre el mismo freqs) [VERIFIED NEXT-LEVEL.md:128]. Verificacion [VERIFIED NEXT-LEVEL.md:130]: mediana posterior dga ~ punto log-lineal dentro de tol; el sello usa el mas conservador de (cuantil 2.5% dga, ci_high Python); validacion publicada de HRDAG (tribunales) como referencia externa del metodo.

### Familia G · Pack de país + sustrato (FS · perfiles · esquema · vectores · roster)

---

<a id="f06"></a>

#### F06 · Layout de filesystem por pais (paths.py)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- `pipeline/paths.py:22` [VERIFIED] `DEFAULT_COUNTRY = "ES"`.
- `:33-52` [VERIFIED] `recipe_root(cc='ES', *, root=None)` -> `base/"countries"/cc` (:36); `recipes_flat_dir` -> `recipe_root/"recipes"` (:41); `data_root` -> `base/"data"/cc` (:47); `census_dir` -> `recipe_root/"census"` (:52). Cada helper acepta un override `root` (:35,46) para conservar la costura monkeypatch.
- `:55-63` [VERIFIED] `country_of_cdp(cdp_code)`: `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` (:30), retorna `m.group(1) if m else DEFAULT_COUNTRY` (:62-63) — **fallback silencioso a 'ES'** para input que no casa.

**(b) Mecanismo al atomo**
paths.py es el unico hogar de las raices FS por pais: `countries/<CC>/recipes|census` y `data/<CC>`. Cada helper DEFAULTea a 'ES' asi las rutas resueltas son byte-identicas a los literales pre-refactor (centraliza 4+ call-sites con `countries/ES/...` hardcoded en recipe.py/harvest_dealer.py/triangulation.py). `country_of_cdp` parsea el segmento `CDP-XX-` para enrutar un codigo a su arbol de pais sin lookup a DB. El override `root` conserva el monkeypatch de `recipe.ROOT` para tests. NO toca el minteo de cdp_code ni la clave de dedup — derivacion de rutas pura.

**(c) Costura ES->generico + fix exacto**
- **Costura:** NINGUNA estructural — el modulo ya es generico. El unico hueco es OPERATIVO: el arbol `countries/` contiene SOLO ES hoy; un 2o pais necesita su directorio creado y poblado (recipes + census).
- **Fix:** crear `countries/<CC>/recipes`, `countries/<CC>/census` y `data/<CC>` y depositar los artefactos del pais ahi. Cero cambio de codigo. Validar el contenido del pack contra un esquema tipado (herramienta) en el bootstrap.

**(d) Riesgo adversarial concreto**
`country_of_cdp` hace fallback SILENCIOSO a 'ES' para cualquier input que no case `^CDP-([A-Z]{2})-` (:62-63) — un cdp_code malformado se clasifica como ES en vez de fallar, enrutando un codigo foraneo/basura al arbol ES. Un pack de pais con un codigo de region de ancho equivocado o un census en esquema erroneo solo fallaria TARDE en el motor de tipos de Postgres, no en la frontera FS.

**(e) Criterio de sellado + verificacion multi-via**
- **Sello:** cada artefacto de CC vive bajo su prefijo; `country_of_cdp` clasifica codigos por pais sin ambiguedad (para input bien-formado).
- **Via 1 (unit):** `recipe_root('DE')` == `<repo>/countries/DE`; rutas ES byte-identicas.
- **Via 2 (round-trip):** `country_of_cdp('CDP-DE-09-...')` == 'DE', `country_of_cdp('CDP-ES-28-...')` == 'ES'.
- **Via 3 (adversarial/contrato):** un Frictionless Table Schema valida los ficheros del pack (ancho de codigo, tipos, centroide-en-bbox) en el bootstrap ANTES de cargar una fila, asi un pack malformado falla ROJO con mensaje claro en vez de un seed parcial.

**(f) Herramienta NEXT-LEVEL [VERIFIED]**
**Frictionless Framework** — Country-pack como CONTRATO de datos auto-verificado (Table Schema) [NEXT-LEVEL.md:334-341 VERIFIED]. URL https://github.com/frictionlessdata/frictionless-py (MIT, EUR0). Declara cada dataset del pack (backbone, centroides, gazetteer, alias, census) como Table Schema con tipos + ANCHO de codigo por pais, validado en el bootstrap del pais antes de cargar una fila; el ancho alimenta la futura migracion CHAR->VARCHAR(n) como fuente unica de verdad. paths.py dice DONDE vive el pack; Frictionless certifica QUE vive ahi. Alternativas: Pandera, jsonschema, Great Expectations; DVC [NEXT-LEVEL.md:148-155] para versionado content-addressed de los artefactos por pais.

---

<a id="f12"></a>

#### F12 · Perfil de pais: convencion postcode→L1 (anti copy-paste)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion [VERIFIED grep pipeline/sources/].** La convencion `postcode[:2] == codigo provincia INE` esta COPIADA inline en 8 adaptadores: `osm.py:77` (`str(postcode)[:2] if ... isdigit()`), `borme_cnae.py:207` (`postcode[:2] if postcode else None`), `graph_recursive.py:163`, `overture.py:227-228`, `autoscout24.py:232`, `axesor_cnae.py:135-136`, `autocasion_census.py:140-141`, `paginas_amarillas.py:47-50`; y el rango ES hardcodeado `"01" <= p <= "52"` en 6 OEM locators: `oem_kia.py:72`, `oem_byd.py:71`, `oem_dacia.py:103`, `oem_hyundai.py:83`, `oem_mercedes.py:99`, `oem_skoda.py:81`. Total = 14 hardcodes [VERIFIED cada hit por grep].

**(b) Mecanismo al atomo.** Cada adaptador deriva la provincia L1 del codigo postal con la regla INE 'los 2 primeros digitos del CP son el codigo de provincia'. Los OEM locators ademas validan contra el rango literal `'01'<=p<='52'` (las 52 provincias espanolas). Esto es DRY roto: ~14 hardcodes dispersos de la MISMA regla, mas un literal de rango ES en 6 sitios. La regla es doblemente ES: (1) asume que el CP prefijea la provincia (cierto en ES/IT/DE-parcial, FALSO en FR/PT/NL donde el CP no mapea a la division administrativa de primer nivel), y (2) asume ancho-2 y rango 01-52. Un pais cuyo CP no prefijee L1, o de otro ancho, produce provincias erroneas en CADA adaptador a la vez -> `cdp_code`s erroneos masivos e IRREVERSIBLES (append-only).

**(c) Costura ES→genérico.** DRY roto: la regla `postcode[:2]->provincia INE` esta inline en 8 adaptadores (osm:77, borme:207, graph_recursive:163, overture:227, autoscout24:232, axesor:135, autocasion:140, paginas:47) y el rango `'01'<=p<='52'` hardcodeado en 6 OEM locators (kia:72, byd:71, dacia:103, hyundai:83, mercedes:99, skoda:81). No existe un hook unico; cada fuente reimplementa la convencion y el rango Espana.

**Fix exacto.** Extraer un hook del perfil de pais `country.postcode_to_l1(postcode)->str|None` + `country.province_validator` cuyo conjunto valido se DERIVA de `geo_province WHERE country_code=$1` (no de un literal '01'-'52'). Los 8 adaptadores con `postcode[:2]` llaman al hook, y los 6 OEM reemplazan el rango por `validator`. ES override la convencion UNA vez (CP[:2], rango derivado de las 52 filas geo_province ES) y queda byte-identico al inline actual.

**(d) Riesgo adversarial concreto.** FR/PT/NL: el CP NO mapea a la division L1 (FR: depto != CP-prefijo limpio; PT: CP NNNN-NNN; NL: CP alfanumerico 'NNNN AA') -> `postcode[:2]` produce una provincia ERRONEA en los 8 adaptadores a la vez -> `cdp_code` erroneo masivo e irreversible. DE: Kreis de 5 digitos no cabe en char(2) y el [:2] del CP no es el Kreis. El rango `'01'<=p<='52'` rechaza TODA provincia de cualquier pais con >52 unidades L1 (FR 101, IT 107) o codigos fuera de 01-52. Ruido: un CP basura de 1 char pasa el `isdigit()` pero da L1 vacio.

**(e) Criterio de sellado + verificación multi-vía.** Multi-via: (1) ES byte-identico: el hook ES reproduce exactamente la salida de los 14 inline actuales (golden sobre los `cdp_code` vivos). (2) Un pais override la convencion en UN sitio; un test asevera que los adaptadores ya no contienen `postcode[:2]` (grep == 0 hits inline). (3) El `province_validator` deriva su conjunto de `geo_province` del pais (no literal): anadir un pais no toca ningun adaptador. (4) Cross-check: un CP del pais resuelve a una L1 que existe en `geo_province` o confiesa None (nunca inventa).

**(f) Herramienta NEXT-LEVEL (€0).** **pycountry (ISO 3166-2)** — LGPL-2.1, EUR0 [VERIFIED https://github.com/pycountry/pycountry] (NEXT-LEVEL.md:530, cluster identity-vehicle 'ISO 3166-2 subdivision authority for the geo_unit grain, width'). Da la AUTORIDAD de subdivisiones de primer nivel por pais (conteo y ancho de codigo) como DATO, alimentando el `province_validator` y el manifiesto de pais sin literales '01'-'52' ni char(2) horneado — DE 16, FR 101 (metro+ultramar), IT 107, MX 32, JP 47. Complementos: **Frictionless Table Schema** (MIT, NEXT-LEVEL.md:337) que declara el ANCHO del codigo L1 por pais y lo valida ANTES del INSERT (captura el overflow char(2)), y **libpostal** (MIT, NEXT-LEVEL.md:345) que parsea el CP/provincia de la direccion cruda en 60+ idiomas para paises donde `postcode[:2]` no aplica. Eleva la regla 'CP[:2]=provincia' de hardcode x14 a hook de perfil con autoridad de subdivisiones data-driven.

---

<a id="f18"></a>

#### F18 · Perfil de pais: validadores de identidad (telefono/reg-id)

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints**
- [VERIFIED pipeline/sources/borme_cnae.py:55] `_CIF_RE = re.compile(r"\b([ABCDEFGHJNPQRSUVW])(\d{7})([0-9A-J])\b")` — forma del CIF ES (letra de organizacion + 7 digitos + control).
- [VERIFIED pipeline/sources/borme_cnae.py:64-78] `_cif_control_ok(cif)`: `fullmatch` `_CIF_RE`; `s_even = sum(int(digits[i]) for i in (1,3,5))`; `s_odd` duplica `digits[i]` en (0,2,4,6) sumando `d//10 + d%10`; `cd = (10-(total%10))%10`; `control_letter = "JABCDEFGHI"[cd]`; `return control in (str(cd), control_letter)` — **checksum ESPANOL** (Luhn-like sobre los 7 digitos).
- [VERIFIED pipeline/identity/phone_es.py:1-50] `_national(raw)`: strip no-digitos; quita `0034`/`34` (si 11-dig); valido **iff `len==9` and `digits[0] in {'6','7','8','9'}`** (:20,:36). `phone_match_key` -> national; `normalize_es_phone` -> `'+34'+national`. El docstring (:11) se autodeclara "EUR0 replacement for python-stdnum/phonenumbers", **ES-only**.

**(b) Mecanismo al atomo**
Dos validadores de identidad ES-horneados que alimentan `canonical_key`. (a) `_cif_control_ok` implementa el algoritmo de digito de control del CIF espanol (control = digito o letra de `"JABCDEFGHI"`). (b) `phone_es` valida el plan de numeracion espanol (9 digitos, leading 6/7/8/9, strip +34/0034) y emite el match key nacional de 9-dig o el E.164 `+34...`. Ambos pure-stdlib, testeados exhaustivos offline, ES-only por construccion. Importan porque `canonical_key` prioriza `cif:` por encima de `name` (facet identidad): un id mal-validado corrompe el dedup; el telefono es un hard key cross-source CAPA-0.

**(c) Costura ES->generico**
`phone_es` es +34/9-dig SOLO (phone_es.py:20,36) y `_cif_control_ok` es el checksum ESPANOL (borme_cnae.py:64-78). Un pais provee su propio normalizador E.164 y su validador VAT/registro (Handelsregister/USt-IdNr DE, Partita IVA IT, NIF/NIPC PT, RFC MX). La costura: dos validadores enchufables tras CountryProfile -> `profile.normalize_phone(raw)` y `profile.validate_registral_id(value) -> (scheme, value) | None`.

**(d) Riesgo adversarial concreto**
`_cif_control_ok` aplica el checksum ESPANOL; un VAT aleman/italiano VALIDO lo FALLA -> el `cif` se descarta -> la entidad cae a identidad por nombre (mas debil, mas colisiones / false-merges). Y `phone_es` toma solo +34/9-dig: un numero nacional frances de 9-dig puede FALSE-ACCEPT contra el plan ES (riesgo B8/B12 del docstring) fundiendo dos dealers distintos, mientras numeros DE/IT/MX se RECHAZAN (hard key perdido).

**(e) Criterio de sellado + verificacion multi-via**
**Criterio:** cada CIF/VAT del pais valida por SU propio checksum; los telefonos normalizan al E.164 del pais; ES byte-identico.
- via1: preservacion ES golden — `es.cif` acepta los CIF hoy almacenados; el token `cif:` de `canonical_key` byte-identico (cero re-key); paridad de telefono (key de phonenumbers superset de phone_es para ES).
- via2: golden por-esquema de los vectores PROPIOS de las librerias (python-stdnum trae validos/invalidos por pais; libphonenumber tablas de ejemplo) — el oraculo es upstream, no nuestra conjetura.
- via3: guard de false-merge cross-border — E.164 completo (`+33 != +34`) y prefijo `{scheme}:` hacen estructuralmente imposible que dos ids de paises distintos compartan key; un id basura falla su digito de control y se descarta antes de sembrar arista.

**(f) Herramienta de nivel inalcanzable**
DOS herramientas, una por validador:
- **python-phonenumbers** (port de Google libphonenumber): metadata validada de ~250 regiones, E.164 para todos los paises a la vez; mata el false-accept FR/PT 9-dig (B8/B12) y los rechazos DE/IT/MX/JP (B3/B10/B14/B17) en una dependencia; `is_valid_number` da el gate de rechazo de basura que phone_es nunca tuvo cross-border. ES puede quedar en phone_es como fast-path para byte-identidad. [VERIFIED NEXT-LEVEL.md:463-469] Apache-2.0, EUR0, https://github.com/daviddrysdale/python-phonenumbers
- **python-stdnum** (reg-id/VAT con digitos de control de ~50 paises: es.cif, de.vatid, fr.siren/siret, it.iva, pt.nif, mx.rfc, eu.vat...): hace el hard key registral country-proof y AUTO-VALIDANTE; un id basura falla su check digit y se rechaza antes de sembrar false-merge; `canonical_key` pasa a `'{scheme}:{validated_value}'`. Pareja con migracion aditiva `cif -> (registral_id, id_scheme)` + ensanchar `alias_kind`. [VERIFIED NEXT-LEVEL.md:487-493] LGPL-2.1, EUR0, https://github.com/arthurdejong/python-stdnum

---

<a id="f23"></a>

#### F23 · Clasificador de actividad / dealer (filtro de scope)

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** Multiples puertas de admision por actividad, todas con vocabulario/scope ES:
- BORME: `_AUTOMOTIVE` = 14 pares (keyword objeto-social -> kind) 100% castellano ('desguace','descontaminaci','compraventa de veh','venta de autom','concesionario','taller','reparaci','recambios','neumatic'...) [VERIFIED pipeline/sources/borme_cnae.py:36-51]; `_VEHICLE_TERMS` co-termino anti-falso-positivo ('veh','autom','coche','turismo','motocicl','automovil') [VERIFIED :53]; `_classify(objeto)` baja a lower, exige co-termino vehiculo para 'reparaci/taller/recambios' (`if kw in (...) and not has_vehicle: continue`) y devuelve kind o None [VERIFIED :97-105].
- schema.org JSON-LD: `is_dealer = t == 'AutoDealer' or (isinstance(t,list) and 'AutoDealer' in t)` [VERIFIED pipeline/sources/autocasion_census.py:122-124].
- OSM Overpass: query `area['ISO3166-1'='ES'][admin_level=2]` + `shop=car|car_repair|car_parts`, mapa `_KIND` [VERIFIED pipeline/sources/osm.py:24-35].
- Overture: whitelist explicita `_AUTOMOTIVE_CATEGORIES` (10 categorias primarias) + `_BBOX` ES [VERIFIED pipeline/sources/overture.py:35,39-50].

**(b) mecanismo al atomo.** Es la puerta que decide 'esto es un punto de venta automotor'. Dos estrategias coexisten: TAXONOMICA (schema.org/OSM/Overture: el @type/shop/category estructurado YA afirma que lo es -> el filtro es una pertenencia a whitelist universal) y POR-KEYWORDS (BORME: el objeto social es el proxy ES de CNAE 4511/4519/45.2/45.3 y hay que INFERIR el kind del texto juridico). La guarda co-termino (`has_vehicle`) impide que 'reparacion'/'comercio' genericos disparen falsos positivos. El BORME es el punto mas ES-duro: traduce lenguaje juridico-mercantil espanol a kind.

**(c) Costura ES→genérico.** Las keywords BORME (_AUTOMOTIVE/_VEHICLE_TERMS) son 100% castellano [VERIFIED borme_cnae.py:36-53]; el filtro OSM clava `ISO3166-1='ES'` [VERIFIED osm.py:26] y Overture el `_BBOX` ES [VERIFIED overture.py:35]. El objeto_social es el proxy ES de CNAE; un registro mercantil extranjero en otro idioma no casa ninguna keyword. Las categorias schema.org/OSM/Overture SI son universales; solo su scope geografico (ISO/bbox) esta clavado a ES.

**Fix exacto.** Dos capas. (capa-1 determinista) el vocabulario de actividad pasa a ser dato del country-pack (keywords/objeto-social por idioma); las categorias schema.org/OSM/Overture son universales y solo cambia el bbox/ISO via CountryProfile (costura facet 'Overture/OSM dia-uno'). (capa-2 IA-local) un clasificador country-agnostico 'es automotor? -> kind|null' con decodificacion por gramatica, invocado SOLO sobre el residuo que la capa-1 no cierra y con piso de aceptacion kind in enum.

**(d) Riesgo adversarial concreto.** DE: un Handelsregister con objeto social aleman ('Kraftfahrzeughandel','Kfz-Reparatur') no casa _AUTOMOTIVE -> _classify devuelve None -> toda alta automotriz alemana se descarta SIN error. FR/IT/PT: idem con 'concessionnaire'/'concessionario'/'stand'/'comercio de veiculos'. Ruido: 'taller de costura' se filtra bien hoy en ES por la guarda co-termino, pero el equivalente en otro idioma carece de esa guarda. schema.org/OSM/Overture degradan mejor (tipos universales) pero su scope ISO/bbox sigue clavado a ES -> sin reparametrizar, o no traen al pais o traen vecinos.

**(e) Criterio de sellado + verificación multi-vía.** Sello: cada fuente del pais admite solo actividad automotriz con su propio vocabulario/taxonomia. Verificacion multi-via: (1) golden ES: el corpus actual produce el mismo set de kinds (cero regresion); (2) recall por idioma: sobre una muestra etiquetada del pais, capa-1+capa-2 iguala o supera el recall ES sin nuevos falsos positivos; (3) invariante de decodificacion capa-2: un fuzzer no logra que el LLM emita un kind fuera del enum (imposible por gramatica, no solo filtrado); (4) cross-check det<->LLM: el determinista gana, el desacuerdo se marca y escala.

**(f) Herramienta NEXT-LEVEL (€0).** Outlines (generacion restringida por gramatica) — Apache-2.0 [VERIFIED NEXT-LEVEL.md:272 y :425] — https://github.com/dottxt-ai/outlines. Es la palanca capa-2 que la faceta nombra ('clasificador IA-local country-agnostico es automotor?'): un LLM open-weight emite UNICAMENTE {kind in DEALER_KINDS ∪ null} con decodificacion constrenida (JSON-Schema / regex / CFG-GBNF) -> fisicamente imposible alucinar una categoria fuera del vocabulario del pack. Seam dormante EUR0 con fallback determinista que siempre gana hoy; el dia que exista modelo local el gate ya esta cableado sin tocar el motor. Corre sobre llama.cpp/Ollama con GGUF Q4 en CPU (EUR0 de cimiento); la GPU es la palanca EUR>0 declarada con caso probado + firma del owner. Capa-1 determinista previa recomendada: lark (EBNF, MIT [VERIFIED NEXT-LEVEL.md:280]) para estructura de titulo/objeto antes de tocar IA.

---

<a id="f24"></a>

#### F24 · Pack de fuentes por pais (autoria del roster)

**Deep-spec institucional (al átomo, verificado).**

**(a) code_hints [VERIFIED].** El roster vive en pipeline/sources/. Glob confirma 26 ficheros .py [VERIFIED Glob pipeline/sources/*.py] = 24 modulos adaptadores + `base.py` (contrato SourceAdapter/DiscoveredEntity) + `__init__.py`. El registro ADAPTERS tiene 25 entradas source_key->clase [VERIFIED pipeline/discover.py:48-74] (associations.py aporta 3 adaptadores: Aedra/Acevas/Aecs, de ahi 24 modulos -> 25 entradas). DISCOVERY_REGISTRY enhebra 5 de ellos como vectores recurrentes [VERIFIED pipeline/discover_schedule.py:65].

**HALLAZGO [VERIFIED]:** `pipeline/sources/autoscout24.py` existe en el directorio pero NO esta registrado en ADAPTERS (solo `autoscout24_census` lo esta [VERIFIED discover.py:72]) -> modulo huerfano / no-despachado, riesgo de drift codigo-vs-registro.

Cobertura por los 6 vectores (todo ES hoy): V1 registral (borme_cnae, axesor_cnae, dgt_cat, associations, paginas_amarillas), V2 geo-POI (overture, osm), V3 dork (dork_municipal), V4 OEM locators (oem_kia/mg/byd/skoda/dacia/hyundai/mercedes/seat), V5 marketplace census (autocasion/motor_es/ocasionplus/flexicar/autoscout24_census), V6 graph/collapse (graph_recursive, collapse_invisible).

**(b) mecanismo al atomo.** El pack es el CONTENIDO especifico del pais (su huella DIGITAL): QUE fuentes online existen y como se extraen. Cada modulo implementa el contrato SourceAdapter (source_key + declared_count()->int|None + fetch()->list[DiscoveredEntity]) y se registra en ADAPTERS (despacho CLI [VERIFIED discover.py:48]) y, si es recurrente, en DISCOVERY_REGISTRY (cadencia [VERIFIED discover_schedule.py:65]). La autoria del roster es el grueso del onboarding: un sub-proyecto 360 por fuente, cada uno cerrando su VAM y aportando su lista ortogonal al MSE.

**(c) Costura ES→genérico.** Los 24 adaptadores son ES por construccion (BORME, DGT Cataluna, coches.net/autocasion, kia.es, paginas amarillas...). La costura es que cada modulo HOY hornea su pais (bbox/ISO/keywords/extractores phone/reg-id) en vez de declararlo. Para CC: cada vector se re-autora portando el patron (BORME->Handelsregister, kia.es->kia.de, coches.net->mobile.de/autoscout24.de) y declarando country_code+orthogonal_bucket + sus extractores locales.

**Fix exacto.** (1) Cada adaptador declara `country_code` y `orthogonal_bucket` como atributos de clase (costura facet 'Contrato SourceAdapter') para que discover()/lists/scheduler enhebren pais y bucket MSE. (2) Derivar `ADAPTERS_BY_COUNTRY[cc]` para targetizar 'todos los vectores de CC'. (3) Reparar el huerfano: registrar o eliminar autoscout24.py para que el roster sea autoexplicativo. (4) Onboarding = anadir modulos + filas sobre las 40 costuras, cero reescritura de ES (byte-identidad pineada por golden).

**(d) Riesgo adversarial concreto.** DE/FR/IT/PT: un roster incompleto (faltan vectores ortogonales) deja al MSE con <2 listas en estratos -> el estrato queda unidentified -> el pais NO se sella aunque el descubrimiento corra (el fallo no-ES exacto que la auditoria marco CRITICAL: DE/IT/PT con solo GEO+OEM => K<3 => piso Chapman/confidence 'low'). Colision de source_key generico entre paises (osm/overture) pisa source_health (costura facet scheduler). El huerfano autoscout24.py es drift vivo: codigo no despachado que un onboarder podria creer activo.

**(e) Criterio de sellado + verificación multi-vía.** Sello: cada vector cierra VAM TRUSTWORTHY y aporta su lista ortogonal al MSE (>=2 listas reales por estrato). Verificacion multi-via: (1) cobertura de vectores: assert que el pack cubre los 6 vectores con >=2 mecanismos ortogonales por estrato; (2) biyeccion ADAPTERS<->DISCOVERY_REGISTRY<->source_health (0 huerfanos: hoy autoscout24.py FALLARIA este test); (3) cada adaptador declara country_code/orthogonal_bucket no-nulos; (4) golden ES: las 25 entradas y sus source_key intactos.

**(f) Herramienta NEXT-LEVEL (€0).** GLEIF LEI Golden Copy (entidades legales globales) — CC0 1.0 Universal (dominio publico, comercial OK, sin atribucion) [VERIFIED NEXT-LEVEL.md:175] — https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy. Eleva la autoria del roster dando una pata REGISTRAL dia-uno a CUALQUIER pais SIN escribir un adaptador de registro nacional: cada entidad con LEI lleva pais + direccion + (a menudo) id de registro local, y el set de LEIs de NACE-automocion por region es una lista de captura registral que existe para DE/FR/IT/PT/MX/JP, tapando el hueco no-ES donde BORME/Handelsregister aun no existen (descarga diaria CC0, sin API key). Complemento web-footprint: 'Censo schema.org/AutoDealer desde Common Crawl' (CC BY 4.0 [VERIFIED NEXT-LEVEL.md:183]) aporta una lista ortogonal de huella-web-declarada para cualquier pais. Juntos con Overture+OSM (facet 'geo-POI dia-uno') arrancan el MSE de un pais con >=2-3 listas ortogonales antes de autorar un solo adaptador nacional.

---

<a id="f29"></a>

#### F29 · Filtro geografico de scope + excluded_count transparente

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED].** `pipeline/discover.py:121-123`: `excluded = getattr(adapter, 'excluded_count', 0)`; `print(... excluded_out_of_scope={excluded})` — el orquestador aflora el conteo fuera-de-scope auto-reportado por el adaptador. `pipeline/sources/oem_kia.py`: `excluded_count = 0` init [:60]; `_spain_province(d)`: `pc = _clean(d.get('dealerPostcode')) or ''; p = pc[:2]; return p if (len(pc)>=2 and p.isdigit() and '01'<=p<='52') else None` [:67-72]; `fetch`: por dealer, `province = self._spain_province(d); if not province: self.excluded_count += 1; continue` [:80-85]; `declared_count` = nº de dealers in-scope (Spain) [:74-76]. `pipeline/sources/oem_mercedes.py`: patrón idéntico sobre `d.get('address',{}).get('zipCode')`; el docstring nota que la API etiqueta Andorra (AD*) y Gibraltar (GX*) como country 'ES' y que la guarda de rango-dígito (`'01'<=p<='52'`) es lo que de hecho los excluye [:90-99]; `excluded_count` [:107-112]. `pipeline/sources/oem_byd.py`: igual sobre `d.get('zipCode')` [:66-71], `excluded_count` [:79-84]. La frontera 'pertenece a este país' es un test hardcoded de prefijo-postal ES, DUPLICADO en cada localizador OEM, con un contrato `excluded_count` genérico aflorado por `discover()`.
**(b) Costura ES->genérico.** El test 'pertenece a ES' es `'01' <= postcode[:2] <= '52'` (rango de provincia INE), hardcoded por adaptador OEM. Para CC debe pasar a 'pertenece a CC'. El contrato `excluded_count` es genérico y se queda; el PREDICADO interno es la costura. Acopla a faceta 37 (postcode->L1 copiado): el mismo literal de rango vive en ~10 sitios.
**(c) Fix exacto.** Extraer el predicado de scope al CountryProfile — `country.in_scope(postcode | lat,lon | country_field) -> bool` — y que cada localizador OEM lo llame en vez del inline `'01'<=p<='52'`. El rango se deriva de `geo_province` filtrado por `country_code`, no de un literal. Los casos 'etiquetado ES pero no lo es' (Andorra/Gibraltar) pasan a un test positivo in-rango/in-polígono, no a una guarda de dígito ad-hoc. Semántica de `excluded_count` intacta (cada adaptador sigue reportando qué tiró y por qué).
**(d) Riesgo adversarial.** Un localizador OEM global (kia.de, mobile.de) cuyo filtro 'no-Spain' NO se reparametriza a CC: (a) excluye los dealers del propio país (los CP de CC fallan el rango ES -> todo tirado, `excluded_count == total`, 0 ingerido), o (b) admite vecinos (un test sin scopear admite dealers FR/BE/NL fronterizos en el censo DE). Micro-estados etiquetados bajo el country-field de un vecino — Andorra (AD), Gibraltar (GX), San Marino, Mónaco, Liechtenstein — se cuelan o se pierden según la guarda de dígito. Scope contaminado = denominador erróneo del MSE (facetas 26/29).
**(e) Sellado + verificación multi-vía.** (1) Cada adaptador declara `excluded_count` y el orquestador lo loguea (invariante de transparencia) — assert `excluded + fetched == loaded`. (2) ES byte-idéntico — el predicado extraído da la misma partición in/out que el rango inline sobre el corpus ES (golden). (3) Scope CC — fixture DE con dealers fronterizos FR/BE: assert sólo se emiten dealers de CP DE, `excluded_count == las filas foráneas`. (4) Micro-estado — filas Andorra/Gibraltar excluidas (contadas), jamás minteadas.
**(f) Herramienta nivel-inalcanzable.** PostGIS (ST_Contains + GiST) sobre geoBoundaries CGAZ (geoBoundaries: CC-BY 4.0 / ODbL datos; PostGIS: GPL-2.0 servicio, EUR0) — https://github.com/wmgeolab/geoBoundaries [VERIFIED NEXT-LEVEL:350-356]. Sustituir el test de rango-postal hardcoded por contención exacta point-in-polygon: ingestar los polígonos de frontera del país, indexar con GiST, y resolver 'pertenece a CC' por `ST_Contains(country_polygon, point)` — un lat/lon cae dentro de exactamente un país o ninguno (hueco confesado). Mata la heurística de dígito ES y el mis-tag Andorra/Gibraltar en una verdad geométrica; los mismos polígonos sirven al reverse-geocode (eliminando la heurística KNN de 30km) y a la cobertura por área real.

---

<a id="f30"></a>

#### F30 · Vector geo-POI global dia-uno (Overture + OSM)

**Deep-spec institucional (al átomo, verificado).**

**(a) Mecanismo al átomo [VERIFIED].** `pipeline/sources/overture.py`: doc — Overture `places` (GeoParquet en S3 público, CC BY 4.0), consultado in-process con DuckDB (httpfs+spatial), filtrado al bbox de España + categorías automotrices primarias, con pushdown hive-partition sobre `bbox` para no descargar el planeta [:1-21]; `_BBOX = {'xmin': -18.3, 'xmax': 4.6, 'ymin': 27.5, 'ymax': 44.0}` — España incl. Canarias/Ceuta/Melilla; la sobre-captura (S Portugal, S Francia) 'is harmless: those POIs carry no Spanish postcode/region and are dropped at INE geo-resolution' [:33-35]; `_AUTOMOTIVE_CATEGORIES` (10-tupla) [:39-50]; `_KIND` [:53-59]; `_CANDIDATE_RELEASES` fallback [:63-66]; `_BUCKET` s3 release [:68]. `pipeline/sources/osm.py`: doc — OSM (ODbL), Overpass API, ~12.077 auto POIs (shop=car/car_repair/car_parts), provincia de `addr:postcode[:2]==INE`, ciudad de `addr:city` [:1-8]; `_QUERY = area['ISO3166-1'='ES'][admin_level=2]->.es; (nwr['shop'='car'](area.es); nwr['shop'='car_repair'](area.es); nwr['shop'='car_parts'](area.es);); out center tags;` [:24-33]; `_KIND` [:35]; `province = str(postcode)[:2] if postcode and str(postcode)[:2].isdigit() else None` [:77]. Overture y OSM son GLOBALES y mutuamente ortogonales (pools de contribuidores distintos) — el ÚNICO par de listas GEO ortogonales disponible para CUALQUIER país sin escribir adaptador, sólo parametrizando el scope espacial. Es el arranque MSE día-uno (>=2 listas ortogonales antes de existir roster nacional).
**(b) Costura ES->genérico (dos literales).** (1) `overture.py` hardcodea `_BBOX` al envoltorio de España [:35]; (2) `osm.py` hardcodea `area['ISO3166-1'='ES']` [:26]. Ambos deben venir de un hook por país (CountryProfile: bbox + ISO 3166-1 alpha-2). Además, el drop de sobre-captura depende de la convención postcode->L1 (faceta 37) para descartar las filas Overture de S-Portugal/S-Francia — un país cuyo CP no prefije la provincia deja entrar vecinos.
**(c) Fix exacto.** Introducir `CountryProfile.bbox` (alimenta `overture._BBOX`) y `CountryProfile.iso3166_1` (alimenta el filtro `area` de `osm._QUERY`), leídos por ambos adaptadores en vez de los literales. El bbox deriva del envoltorio de frontera del país; el ISO, del estándar. Los valores ES reproducen byte-idéntico. El drop de sobre-captura DEBE usar el validador postcode->L1 propio del país (faceta 37), no el rango ES.
**(d) Riesgo adversarial.** Con bbox/ISO hardcoded a ES, un país nuevo obtiene CERO census POI gratis — overture devuelve POIs españoles, osm consulta el área ES — así que el arranque día-uno >=2-listas falla en silencio y el país no puede sellar (faceta 29 exige K>=2 por estrato; el fallo CRÍTICO exacto no-ES: DE/IT/PT con sólo GEO+OEM -> K<3 -> casi nada sella). Aun con el bbox parametrizado, Overture sobre-captura vecinos (un bbox DE agarra POIs fronterizos NL/BE/FR/CH/AT/PL/CZ/DK) que SÓLO se dropean por carecer de CP DE — si la postcode->L1 (faceta 37) no se reparametriza, los vecinos se cuelan en el censo DE. Ruido: un bbox demasiado ancho sin la guarda de CP contamina el MSE con POIs transfronterizos.
**(e) Sellado + verificación multi-vía.** (1) Un país arranca su MSE con >=2 listas GEO (Overture + OSM) día-uno sólo con parámetros de perfil, sin roster — assert ambos adaptadores emiten sets no vacíos y ortogonales para un fixture CC. (2) ES byte-idéntico — el bbox/ISO parametrizados reproducen el set POI ES exacto (golden). (3) Seguridad de sobre-captura — los POIs fuera de CC (frontera vecina) se dropean por el validador postcode->L1 de CC (assert 0 POIs vecinos minteados). (4) Ortogonalidad — Overture y OSM tienen baja correlación de solapamiento (chequeo de mecanismo distinto que alimenta el `m` del MSE).
**(f) Herramienta nivel-inalcanzable.** DuckDB + spatial extension (MIT, EUR0) — https://github.com/duckdb/duckdb-spatial [VERIFIED NEXT-LEVEL:406-412]. Overture ya corre in-process sobre DuckDB; la extensión spatial (índice RTREE + ST_Contains index-scan + GeoParquet nativo) hace del census POI parametrizado por bbox/ISO un artefacto REPRODUCIBLE, serverless y CI-runnable: un único script lee el GeoParquet público, aplica el bbox por-país vía pushdown espacial, y exporta las listas GEO ortogonales sin Postgres vivo — el census día-uno de un país nuevo verificable en máquina limpia antes de tocar la DB servida. Emparejar los parámetros bbox/ISO con la autoridad ISO 3166 (pycountry) + envoltorio geoBoundaries.

---

<a id="f40"></a>

#### F40 · Sustrato de esquema geo+entity por pais + siembra geo

**Deep-spec institucional (al átomo, verificado).**

**(a) Verificacion de code_hints [VERIFIED]**
- **0052_country.sql** [VERIFIED migrations/0052_country.sql]: `ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` a geo_province/geo_comarca/geo_municipality/entity [VERIFIED :51-54]; UNIQUE compuesto `(country_code,code)` en geo_province+geo_municipality, guardado por DO-blocks [VERIFIED :61-77]; indices idx_entity_country/idx_geo_municipality_country [VERIFIED :80-81]; mantiene las PK de columna-unica para que las 7 FK sigan validas [VERIFIED :16-18, 56-60]; backfill implicito 431.211 entity / 52 province / 8.132 municipality / 323 comarca como ES [VERIFIED :20-23]; DIFIERE a 0053 el PK-swap, country_code en denominator/organization, y la relajacion de CHECKs [VERIFIED :25-41]; idempotente + reversible [VERIFIED :43-47, 83-91].
- **0053_country_onboarding.sql** [VERIFIED migrations/0053_country_onboarding.sql]: la mitad FK-breaking. Anade country_code a denominator_estimate+organization [VERIFIED :53-54]; dropea 6 FK hijas [VERIFIED :57-62]; swap de las PK geo a compuesta `(country_code,code)` — ADD PK compuesta primero, luego DROP PK columna-unica, luego DROP UNIQUE redundante [VERIFIED :64-91]; re-anade 6 FK COMPUESTAS `(country_code,col)->(country_code,code)` MATCH SIMPLE [VERIFIED :93-157]; relaja 2 CHECK ES: `municipality_province_prefix` -> `CHECK (country_code <> 'ES' OR left(code,2)=province_code)` [VERIFIED :166-168] y `chk_entity_muni_province` gateado en country_code<>'ES' [VERIFIED :170-174]. Colision PK probada en vivo (INSERT geo_province code='28' country_code='DE' falla en geo_province_pkey(code)) [VERIFIED :3-5]; runner omite BEGIN/COMMIT (su propia txn) [VERIFIED :35-40]; idempotente via ledger + IF EXISTS/DO-block [VERIFIED :42-45]; rollback inverso completo [VERIFIED :176-218].
- **load_geo.py** [VERIFIED scripts/load_geo.py]: hardcodea 52 PROVINCES + CCAA ES [VERIFIED :26-56], lee diccionario_ine.xlsx con zfill(2)/zfill(3) [VERIFIED :59-71]; `INSERT geo_province/geo_municipality ... ON CONFLICT (country_code, code) DO NOTHING` [VERIFIED :78-89] (ya actualizado para la PK compuesta); country_code default 'ES' para estas filas; check 2-vias de orphans [VERIFIED :94-100].
- **CONFIRMADO**: solo existe `scripts/load_geo.py`; NO existe `scripts/load_geo_CC.py` (el loader country-scoped esta "to create") [VERIFIED `ls scripts/load_geo*.py`].

**(b) El mecanismo al atomo**
La fundacion de datos YA sellada por pais. 0052 anade la dimension pais de forma aditiva (toda fila existente estampada 'ES', zero NULL, ninguna FK rota). 0053 promueve la identidad geo de `PK(code)` a `PK(country_code,code)`, reescribe las 6 FK referenciantes a compuestas, y gatea los dos CHECK ES (esquema INE `<prov2><muni3>`) en `country_code='ES'` para que sigan vinculantes+byte-identicos para ES pero dejen libre un esquema municipal no-ES. El esquema ya puede sostener ES-28 y DE-28 a la vez. Lo que falta: el loader country-scoped (load_geo_CC.py) y las filas geo CC reales — la fundacion existe, el motor aun no la ejerce (el INSERT de discover.py sigue omitiendo country_code: facet 5).

**(c) Costura ES->generico**
El sustrato (0052/0053) esta HECHO y es country-parametrico. Los huecos son: (a) el loader: load_geo.py es ES-hardcoded (52 provincias, xlsx INE, zfill 2+3); (b) las filas geo CC. La costura es puramente aditiva: nuevos modulos + nuevas filas sobre la superficie 0052/0053, cero reescritura de ES.

**(d) Riesgo adversarial concreto**
- **Sin loader**: un 2o pais tiene los slots de esquema pero sin filas backbone -> toda entidad CC hace SKIP (ninguna provincia resuelve) — discovery corre pero no sella nada.
- **DE-28 vs ES-28**: pre-0053 la PK(code) columna-unica RECHAZA fisicamente DE-28 (probado vivo [VERIFIED 0053:3-5]); post-0053 la PK compuesta admite ambas — pero SOLO si el loader estampa country_code='DE'. Un loader que olvide country_code default-ea las filas a 'ES' -> municipios DE contaminan el backbone ES irreversiblemente.
- **IT/PT** con codigo municipal no `<prov2><muni3>`: el CHECK relajado (`country_code<>'ES' OR ...`) los admite; pero si un CC se etiqueta mal como 'ES', el CHECK ES vincula y rechaza codes CC validos — o peor, una fila CC estampada 'ES' que casualmente satisface `left(code,2)=province_code` corrompe en silencio.
- **No-UE**: pais con codigos administrativos alfanumericos — las columnas CHAR los aceptan; el loader debe emitir el code oficial y el resolver (facet 7) manejar el ancho.
- **Drift doc-vs-codigo**: los playbooks dicen 0053 "to author" pero ya existe y esta aplicada [VERIFIED 0053 cabecera "VERIFIED LIVE 2026-06-23"] -> un onboarder podria intentar re-autorizarla (mitigado por el ledger schema_migrations idempotente, pero el doc miente).

**(e) Criterio de sellado + verificacion multi-via**
1. **Counts geo == grid oficial de CC** (p.ej. ES 52/8.132 inalterado — golden de carga), orphans=0 (cada municipio tiene su provincia, mismo pais).
2. **ES byte-identidad**: el adaptador degenerado ES produce exactamente las 52/8.132 filas actuales (golden de carga inalterado).
3. **Integridad de jerarquia**: 0 municipios sin padre del mismo pais (FK compuesta), todos los parentId resuelven.
4. **Idempotencia**: re-correr con `ON CONFLICT (country_code,code) DO NOTHING` -> counts inalterados.
5. **Rollback**: `DELETE WHERE country_code='CC'` restaura ES-only (el rollback de 0053 exige cero filas geo no-ES primero — documentado [VERIFIED :176-181]).
6. **2a via**: conteo por-nivel vs la oficina estadistica nacional (denominador independiente); muestra de code GeoNames vs code oficial (INE/AGS/INSEE) coincide tras cross-walk.

**(f) Herramienta NEXT-LEVEL**
**GeoNames dump (allCountries.zip + hierarchy.zip + admin1CodesASCII.txt + admin2Codes.txt)** (CC-BY 4.0) — https://download.geonames.org/export/dump/ [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:377]. La herramienta exacta para el load_geo_CC.py faltante: un unico ingestor GeoNames generico (`feature_class='A'`, ADM1/2/3/4 + resolucion de padre via hierarchy.zip) aplanado sobre los 3 slots canonicos segun manifiesto del pais (ADM1->province, ADM2->comarca[nullable], ADM3/4->municipality), emitiendo el code OFICIAL — un solo loader cubre todos los paises objetivo, ES degenera a su manifiesto INE (golden 52/8.132). Alternativas: Overture Divisions (jerarquia country/region/county/locality ya construida), Who's On First (jerarquia admin + concordancias GeoNames/Wikidata), Eurostat LAU code list (cross-walk a code oficial, no poligonos) [VERIFIED NEXT-LEVEL.md:378]. EUR0 (allCountries ~1.5GB gratis; cross-walk via Eurostat LAU u OSM ref:INE/ref:ISTAT). **Soporte** para la honestidad "stack CAIDO bloquea incluso correr el golden": **DuckDB + spatial extension** (MIT) — https://github.com/duckdb/duckdb-spatial [VERIFIED NEXT-LEVEL.md:409] habilita un build geo portatil/reproducible que corre SIN Postgres vivo (RTREE + ST_Contains + GeoParquet nativo), desacoplando la verificacion del seed de la liveness del servidor.

---

### Arsenal NEXT-LEVEL €0 consolidado (40 facetas → herramientas)

> Resumen navegable; el texto completo de cada herramienta (alternativas, líneas `[VERIFIED NEXT-LEVEL.md:…]`, racional de licencia) vive en el bloque **(f)** de cada faceta. Todas open-source, CPU/offline, **€0** de cimiento.

| Faceta | Sub-proyecto | Herramienta primaria | Licencia · coste | Fuente |
|---|---|---|---|---|
| [F01](#f01) | Contrato SourceAdapter | Pydantic (typed country-pack contract guard) | MIT · €0 | https://github.com/pydantic/pydantic |
| [F02](#f02) | Cascada municipality_code | libpostal (multilingual trained address/name par | MIT · €0 | https://github.com/openvenues/libpostal |
| [F03](#f03) | Hashing cdp_pair/cdp_code + base32 + i… | in-toto (atestacion de provenance firmada, tampe | Apache-2.0 · €0 | https://github.com/in-toto/in-toto |
| [F04](#f04) | Gate AUTO-run por requires_env | PyrateLimiter (token-bucket distribuido Postgres | MIT · €0 | https://github.com/vutran1710/PyrateLimiter |
| [F05](#f05) | Sello compute + roll-up nacional honesto | Censo externo VINCULANTE via dga/SparseMSE (marg | GPL · €0 | https://cran.r-project.org/package=dga |
| [F06](#f06) | Layout de filesystem por pais | Frictionless Framework (Table Schema, contrato d | MIT · €0 | https://github.com/frictionlessdata/frictionless-py |
| [F07](#f07) | DTO DiscoveredEntity | Frictionless Framework (Table Schema) | MIT · €0 | https://github.com/frictionlessdata/frictionless-py |
| [F08](#f08) | Matcher fuzzy de municipio | datasketch (MinHash-LSH) + RapidFuzz | MIT · €0 | https://github.com/ekzhu/datasketch |
| [F09](#f09) | Motor de quorum record_count_verdict | in-toto + Sigstore cosign | Apache-2.0 · €0 | https://github.com/in-toto/in-toto |
| [F10](#f10) | Lanzador _run_vector + auditoria _record | Procrastinate | MIT · €0 | https://github.com/procrastinate-org/procrastinate |
| [F11](#f11) | Persistencia del sello + tablas MSE ci… | DVC (Data Version Control) | Apache-2.0 · €0 | https://github.com/iterative/dvc |
| [F12](#f12) | Perfil de pais: convencion postcode→L1 | pycountry (ISO 3166-2) | LGPL-2.1 · €0 | https://github.com/pycountry/pycountry |
| [F13](#f13) | Registro ADAPTERS + dispatch CLI | Pydantic (MIT, EUR0=True) | MIT · €0 | https://github.com/pydantic/pydantic |
| [F14](#f14) | Gazetteer INE Nomenclator | GeoNames dump (allCountries 'P'+ADM3/4 + alterna | CC-BY 4.0 · €0 | https://download.geonames.org/export/dump/ |
| [F15](#f15) | Taxonomia de familias VAM + oraculo de… | GLEIF LEI Golden Copy (CC0 1.0, EUR0=True) | CC0 1.0 · €0 | https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy |
| [F16](#f16) | Taxonomia de listas ortogonales (bucke… | Great Expectations (Apache-2.0, EUR0=True) | Apache-2.0 · €0 | https://github.com/great-expectations/great_expectations |
| [F17](#f17) | Triangulacion externa DIRCE | Eurostat Structural Business Statistics NACE G45 | — · €0 | https://ec.europa.eu/eurostat/web/structural-business-statistics |
| [F18](#f18) | Perfil de pais: validadores de identidad | python-phonenumbers (Apache-2.0, EUR0=True) | Apache-2.0 · €0 | https://github.com/daviddrysdale/python-phonenumbers |
| [F19](#f19) | Orquestacion discover() + cuenta por-r… | in-toto (atestacion de provenance del build) | Apache-2.0 · €0 | https://github.com/in-toto/in-toto |
| [F20](#f20) | Fallbacks de recuperacion geo + SKIP h… | PostGIS (ST_Contains + GiST) sobre fronteras geo | CC-BY 4.0 · €0 | https://github.com/wmgeolab/geoBoundaries |
| [F21](#f21) | DiscoveryJob + DISCOVERY_REGISTRY | river (deteccion de cambio online: ADWIN / Page- | BSD-3-Clause · €0 | https://github.com/online-ml/river |
| [F22](#f22) | Taxonomia DEALER_KINDS → segmento | Snorkel (weak-supervision auto-labeler) | Apache-2.0 · €0 | https://github.com/snorkel-team/snorkel |
| [F23](#f23) | Clasificador de actividad / dealer | Outlines (generacion restringida por gramatica) | Apache-2.0 · €0 | https://github.com/dottxt-ai/outlines |
| [F24](#f24) | Pack de fuentes por pais | GLEIF LEI Golden Copy (entidades legales globale | CC0 1.0 · €0 | https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy |
| [F25](#f25) | _upsert idempotente + costura nuclear… | Pydantic (MIT, EUR0) | MIT · €0 | https://github.com/pydantic/pydantic |
| [F26](#f26) | Politica de normalizacion de texto | anyascii (ISC, EUR0) | ISC · €0 | https://github.com/anyascii/anyascii |
| [F27](#f27) | Motor de vencimiento de cadencia | river (BSD-3-Clause, EUR0) | BSD-3-Clause · €0 | https://github.com/online-ml/river |
| [F28](#f28) | Construccion de la matriz de captura | Great Expectations (Apache-2.0, EUR0) | Apache-2.0 · €0 | https://github.com/great-expectations/great_expectations |
| [F29](#f29) | Filtro geografico de scope + excluded_… | PostGIS (ST_Contains + GiST) sobre geoBoundaries | CC-BY 4.0 · €0 | https://github.com/wmgeolab/geoBoundaries |
| [F30](#f30) | Vector geo-POI global dia-uno | DuckDB + spatial extension (MIT, EUR0) | MIT · €0 | https://github.com/duckdb/duckdb-spatial |
| [F31](#f31) | GeoResolver: carga de indice + alcance… | GeoNames pan-country backbone (allCountries.zip+ | CC-BY 4.0 · €0 | https://www.geonames.org |
| [F32](#f32) | Algebra de identidad canonical_key | Splink (MIT, EUR0 [VERIFIED NEXT-LEVEL.md:450])  | MIT · €0 | https://github.com/moj-analytical-services/splink |
| [F33](#f33) | Circuit breaker del scheduler | transitions/pytransitions (MIT, EUR0 [VERIFIED N | MIT · €0 | https://github.com/pytransitions/transitions |
| [F34](#f34) | Lectura de patrones 0/1 | Great Expectations (Apache-2.0, EUR0 [VERIFIED N | Apache-2.0 · €0 | https://github.com/great-expectations/great_expectations |
| [F35](#f35) | Gate G1 IDENTITY por-entidad | pycountry (LGPL-2.1, EUR0 [VERIFIED NEXT-LEVEL.m | LGPL-2.1 · €0 | https://github.com/pycountry/pycountry |
| [F36](#f36) | Resolutor de provincia + alias + ancho… | GeoNames alternateNamesV2.zip (CC-BY 4.0) | CC-BY 4.0 · €0 | https://download.geonames.org/export/dump/ |
| [F37](#f37) | Ensamblado mint_code | Hypothesis (MPL-2.0) | MPL-2.0 · €0 | https://github.com/HypothesisWorks/hypothesis |
| [F38](#f38) | Advisory lock singleton + lease heartb… | Healthchecks (BSD-3-Clause) | BSD-3-Clause · €0 | https://github.com/healthchecks/healthchecks |
| [F39](#f39) | Estimadores captura-recaptura | dga: Capture-Recapture Estimation using Bayesian | GPL · €0 | https://cran.r-project.org/package=dga |
| [F40](#f40) | Sustrato de esquema geo+entity por pai… | GeoNames dump (allCountries.zip + hierarchy.zip  | CC-BY 4.0 · €0 | https://download.geonames.org/export/dump/ |

---

## Mejoras a nivel inalcanzable (€0, priorizadas)
> Listón 00-MASTER: que ningún intelecto —humano o IA— replique en años lo bien blindado que esto queda. Priorizado por leverage/coste.

1. **[S · €0] Adaptador auto-declara país + bucket MSE** (`SourceAdapter.country_code`/`orthogonal_bucket`; `discover()`/`_upsert`/`lists` los leen). El cambio de **mayor leverage y mínimo coste**: vuelve el motor 100% country-agnóstico sin cableado por-país más allá del módulo. Es **R1+R4**.
2. **[S · €0] Migración aditiva de país en MSE** (`country_code` en `discovery_capture`/`exhaustiveness_estimate` + `_fetch_raw` scoped). Sin esto el sello de un 2º país contamina el de ES en silencio; los playbooks NO lo cubren (deuda neta). Es **R5**.
3. **[M · €0] `CountryProfile` inyectado** en motor+adaptadores → mata el `postcode[:2]` copiado en 5+ adaptadores y los datos INE hardcodeados del resolver. Reversible pero amplio. Es **R3** (núcleo).
4. **[M · €0] Vector V2 geo POI gratis día-uno**: `overture` (S3 público, sin key) y `osm` (Overpass) son GLOBALES; parametrizar `bbox`+ISO por país vía `CountryProfile` da a CC un census POI ortogonal **sin escribir adaptador nuevo**. Hoy `overture.py:35,223` y `osm.py:26` hardcodean bbox ES y `country!='ES'`. Arranque MSE inmediato a cualquier país.
5. **[M · €0] Cadencia auto-sintonizada**: derivar `DISCOVERY_REGISTRY.cadence_hours` del volumen de delta observado en `source_health` en vez de literales (24h/168h/720h/2160h, `discover_schedule.py:66-83`). Optimiza coste de barrido a €0.
6. **[L · €0 cimiento / €>0 escala] Capa-2 IA-local obrera**: clasificador objeto-social/actividad country-agnóstico que reemplaza `borme_cnae._classify` (lista de keywords ES) → "¿es automotor?" sin keyword-list por país, generalizando V1 registral a cualquier registro mercantil. Es la palanca de **R7** (transliteración) y de la generalización registral. Capa-2 HOY = 0 en código; requiere modelo local + caso de uso probado + firma (gate GPU €>0). **No cimiento.**

---

## Riesgos / open items
- **[MÁXIMO · bloqueante] Estampado-ES silencioso** [VERIFIED `discover.py:91,96-104`]: un adaptador extranjero estampa `entity.country_code='ES'` y `cdp_code CDP-ES-` SIN error → corrompe el censo de forma invisible. **Bloqueante antes de cargar cualquier 2º país.** Mitiga: R1.
- **[IRREVERSIBLE] Sangrado geo cross-país** [VERIFIED `geo.py:151-157`]: muni DE resuelve contra índice ES → provincia errónea → `cdp_code` erróneo; como es inmutable, re-keya sin vuelta atrás. **Mitiga: R2, ANTES de datos del 2º país.**
- **[ALTO] Colapso de estrato MSE** [VERIFIED `capture.py` 0 hits `country`, `0048:39,58`]: DE+ES comparten estrato provincia `'28'` → contamina `coverage_lower` de AMBOS. El sello miente sin síntoma. Mitiga: R5.
- **[MEDIO] Listas extranjeras descartadas en silencio** [VERIFIED `lists.py:74`]: roster de CC cae a MKT → `coverage_lower` sub-cuenta. Mitiga: R4 (fail-closed).
- **[OPEN · BLOQUEADOR 6] `complete.py:89` sigue `^CDP-ES-`** [VERIFIED grep] + `:73` `_PROVINCE_RE` 01-52: entidades `CDP-CC-` rechazadas en el gate de completion. El xfail(strict) (`test_country_golden.py:286-290`) lo vigila. **Causa**: ensanche pendiente de commit. **Gating**: hasta entonces, ningún país nuevo completa. (R6)
- **[OPEN · deuda neta, gated] Transliteración no-latina** [VERIFIED `codes.py:29-32`, `geo.py:51-53`]: NFKD+ascii-ignore destruye nombres no-latinos → fusión masiva + 100% SKIP. **Causa**: requiere romanización real + golden por script, posible capa-2 GPU (€>0). **Gating**: no-UE no-latino no se onboardea hasta `translit_policy` probada. Latino no afectado. (R7)
- **[DRIFT DOC-VS-CÓDIGO] `0053` ya existe pero los docs dicen "[to author]"** [VERIFIED por contexto]: `REPLICATION-PLAYBOOK.md:753` y `COUNTRY-SWITCHOVER.md:120` dicen `0053 '[to author]'/'File to create'`, pero `0053_country_onboarding.sql` YA está escrita y (per contexto) aplicada. Un onboarder que siga el doc al pie podría re-autorizarla. Mitigado por idempotencia del ledger; **el doc debe corregirse** (open item documental).
- **[VERIFICACIÓN LIMITADA] PG :5433/:5434 caído**: toda cifra DB es **punto-en-el-tiempo** y la coexistencia byte-idéntica del piloto DE es **[ASSUMED]** (verificado código 0052/0053 + golden, no la corrida viva). **Re-validar contra DB viva** antes de declarar el sello del 2º país. Multi-vía (00-MASTER §Operación): ningún número se da por bueno sin ≥2 vías ortogonales y verificación adversarial co-igual.
