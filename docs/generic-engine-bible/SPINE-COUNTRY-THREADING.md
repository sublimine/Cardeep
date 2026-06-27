# SPINE — El enhebrado de `country_code` (la espina dorsal del des-cegado de país)
> El corazón de "transformar a genérico". **Diagnóstico + programa unificado de remediación**, confirmado por los **10 inquisidores** (Ola 1) y **re-verificado al átomo contra el código vivo** (cada `path:línea` de la espina leído a mano, no transcrito). Léelo después de `00-MASTER.md` (constitución) y `ANTI-DRIFT-HARDENING.md` (blindaje). El level-up que lo vuelve **invariante mecánico** vive en `COUNTRY-PROOF-INVARIANT.md`; la campaña operativa en `COVER-NEW-COUNTRY.md`; el detalle por etapa en `stages/01..10`.

---

## 0 · TL;DR — la única frase
`country_code` se enhebró en el **ESQUEMA** (`0052` lo añade `DEFAULT 'ES'` a geo+entity; `0053` promueve la PK geo a `(country_code, code)` + 6 FK compuestas) y en el **prefijo del `cdp_code`** (`mint_code`, `services/api/codes.py:53`). **Ahí paró.** Toda la **lógica** —pipeline, serving, orquestación, sellado— es **country-BLIND** por debajo del esquema: las queries cruzan por `code`/`province_code`/`municipality_code`/`source_key` sin dimensión país, los locks son constantes fijas, los gates clavan literales ES, los anchos `CHAR(2)/CHAR(5)` y el rango `01-52` están moldeados por INE. El motor **no es genérico todavía**: es un motor ES con una costura de esquema multipaís **sin coser**.

**Veredicto Ola 1: 10/10 etapas `holds=false → NEEDS_REWORK`.** La misma espina rota en todas.

---

## 1 · Cómo navegar este documento
| § | Contenido | Para qué |
|---|---|---|
| [2](#2--blindaje-y-procedencia-de-verificación) | Blindaje + procedencia | Qué es `[VERIFIED]` vs `[ASSUMED]` aquí |
| [3](#3--diagnóstico-por-capa-country_code-en-el-esquema-no-en-la-lógica) | Diagnóstico por capa | Las breaks CRITICAL/HIGH con `path:línea` por capa |
| [4](#4--el-patrón-único-de-remediación) | El patrón único | Por qué TODO es el mismo fix |
| [5](#5--el-programa-unificado-de-remediación) | Programa unificado | Los 6 movimientos del des-cegado |
| [6](#6--orden-de-ataque-por-riesgo) | Orden de ataque | Los false-merge irreversibles PRIMERO |
| [7](#7--cómo-se-prueba-cada-fix-golden-cross-country) | Cómo se prueba | El golden cross-country por capa |
| [8](#8--open-items-honestos-causa-declarada) | Open items | Lo que NO se da por hecho |

---

## 2 · Blindaje y procedencia de verificación
Conforme a `ANTI-DRIFT-HARDENING.md`: cada afirmación es `[VERIFIED path:línea]` (leída en la fuente) o `[ASSUMED]` (declarada, sin prueba viva). **Un diseño roto no se transcribe como hecho** — se integra la rotura y su resolución, o se marca open item con causa (§8).

- **La espina completa fue re-leída EN VIVO contra el código** (no solo desde los inquisidores). Spot-check de las citas load-bearing, todas confirmadas a mano:
  - **Data-model:** `0001_geo.sql:5` (`geo_province.code CHAR(2)`), `:19` (`geo_municipality.code CHAR(5)`), `:7-8` (`ccaa_code CHAR(2) NOT NULL` / `ccaa_name TEXT NOT NULL`), `:26` (CHECK `left(code,2)=province_code`); `0002_entities.sql:13-14` (`province_code CHAR(2)` / `municipality_code CHAR(5)`); `0052_country.sql:51-54` (ADD `country_code CHAR(2) NOT NULL DEFAULT 'ES'`); `0053_country_onboarding.sql:75,84` (PK `(country_code, code)`), `:104-154` (6 FK compuestas), `:168` (CHECK gated `country_code<>'ES' OR …`); `0048_discovery_capture.sql:39,58` (`province_code char(2)`, **sin** `country_code`), `:86-87` (`ORDER BY created_at DESC LIMIT 1`); `0055_product_stats.sql:15` (`id … PRIMARY KEY DEFAULT 1 CHECK (id = 1)`).
  - **Identidad/geo (lo irreversible):** `cluster_dealers.py` → **0** ocurrencias de `country_code` (grep `-c` = 0), `SCOPE_CONDITION` sin país (`:59`), `RUN_ID` único (`:56`), edge-1 `normalized_name + municipality_code` (`:404,:416`); `cluster_vehicles.py` → **0** `country_code`, `block_key=(make,model,year,km,province)` (`:397`), anti-FP `HAVING COUNT(DISTINCT e.province_code) > 1` (`:852`); `phone_es.py:20` (`_VALID_LEADING=frozenset("6789")`), `:36` (`len==9`), `:41` (`phone_match_key(raw)` **sin** parámetro país); `codes.py:24` (`DEFAULT_COUNTRY="ES"`), `:53` (`mint_code` único hogar del prefijo), `:62` (`canonical_key` country-blind **deliberado**), `:30` (`_normalize` NFKD+ascii-ignore); `geo.py:52` (`_norm` ascii-ignore), `:151-157` (`GeoResolver.load(conn)` **sin** país: `SELECT code,name FROM geo_province` / `… FROM geo_municipality`), `:61` (`_PROVINCE_ALIASES`), `:205` (`s.zfill(2)`); `geocode.py:79,130` (loaders sin país); `seed_geo_centroides.py:71,97` (`UPDATE … WHERE code=$3` sin país); `0018_comarca.sql:30-31` (trigger `entity_set_comarca` por `m.code` sin país).
  - **Gate/serving/orquestación/sello:** `complete.py:73` (`_PROVINCE_RE=^(0[1-9]|[1-4][0-9]|5[0-2])$`), `:89` (`_CDP_CODE_RE=^CDP-ES-…`), `:305,:309` (glob `countries/ES/…` literal); `ingest.py:49` (gate `isdigit() and "01"<=code<="52"`); `fingerprints.py:46,65,80` (`Accept-Language: es-ES`); `free_proxies.py:27` (`_COUNTRY="ES"`); `pipeline/platform/*` → **31** funciones `return f"CDP-ES-{…}"`, **0** usan `mint_code` (grep `-rl`=31, `-c`=31, mint_code-importers=0); `servable_entity` (`0046:17-18`) **no** proyecta `country_code`; `geo.py:370` (`… FROM geo_province WHERE code=$1`), `:420` (`ccaa_code/ccaa_name` en el árbol); `cache.py:79` (`_cache_key` = METHOD+PATH+qs, sin tenant); `scheduler.py:913` (`_SCHEDULER_SINGLETON_LOCK=0x43415244` constante), `discover_schedule.py:50` (`_LOCK_KEY=0x43415244+1`); `source_health` (`0004:25` `source_key TEXT PRIMARY KEY`); `health.py:172-173` (`resolve_alerts` solo fase `scrape|discover`); `detect.py:70` (`FAB_PRICE_CEIL=5_000_000`), `:78-80` (`COVERAGE_ANCHORS` DGT/FACONAUTO ES), `:786` (`GROUP BY make,model,year` sin país); `seal.py:69` (`load_external_census()` → default ES); `lists.py:27-49` (`_EXACT` claves ES, `ORTHOGONAL_LISTS` 7 buckets); `load_denominator_provincia.py:38` (`RATIO_451_45`), `:64-65` (`SystemExit` si ≠ 52); `0005_types_and_guards.sql:13` (`entity_kind AS ENUM`).
- **`[ASSUMED]` declarado** (PG `:5433` caído → toda cifra de DB es punto-en-el-tiempo): la coexistencia byte-idéntica del piloto DE, las cifras de sello vivas (MSE ~37,7 % / registral ~80,5 %), y la **sobre-afirmación** de la Decisión-1 ("el piloto DE probó que el esquema es paramétrico") — el piloto usó muni sintético `'28001'` con forma ES exacta y **nunca** ejercitó ancho de 8 dígitos, nombre no-latino ni provincia de 3 dígitos. Ver §8.

---

## 3 · Diagnóstico por capa: `country_code` en el ESQUEMA, **no** en la lógica
> Severidad: **C**=CRITICAL, **H**=HIGH. Todas `[VERIFIED path:línea]` salvo marca `[ASSUMED]`. "Disparo" = cuándo se manifiesta la rotura.

### 3.0 · DATA-MODEL — dónde para el enhebrado (la raíz de todo) · **anchos + rangos**
| Hecho | Evidencia | Lectura |
|---|---|---|
| `country_code` llega al esquema | `0052_country.sql:51-54` (ADD a geo+entity, `DEFAULT 'ES'`); `0053_country_onboarding.sql:75,84` (PK `(country_code,code)`) + `:104-154` (6 FK compuestas) | El enhebrado **existe** hasta aquí |
| El prefijo del código es paramétrico | `codes.py:53` `mint_code` → `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`; `:62` `canonical_key` **excluye** país del hash (no re-keya) | La **identidad** sabe de país |
| **Y AHÍ PARA — anchos soldados a INE** | `geo_province.code CHAR(2)` (`0001:5`), `geo_municipality.code CHAR(5)` (`0001:19`), `entity.province_code CHAR(2)` / `municipality_code CHAR(5)` (`0002:13-14`); `ccaa_code CHAR(2) NOT NULL` (`0001:7`) | AGS DE (8) / ISTAT IT (6) / DOM FR `971-976` (3) **desbordan** |
| **…y rangos/tablas sin país** | `vehicle` sin `country_code` (`0052` nota d: derivable vía `entity_ulid`); `discovery_capture`/`exhaustiveness_estimate` `province_code char(2)` sin país (`0048:39,58`); `source_health`/`harvest_run`/`source_breaker`/`scheduler_lease` sin país (`0004:25`,`0013`,`0054`); `product_stats` fila única `CHECK(id=1)` (`0055:15`); `entity_kind` es **ENUM** (`0005:13`) → kind nuevo = `ALTER TYPE`, no config | La **lógica** que consume el esquema es ciega |

**El patrón de la raíz:** `0052` difirió a propósito el swap de PK a `(country_code,code)` hasta `0053` (cuando un 2.º inquilino lo forzó). El mismo diferimiento se aplicó —por inercia, no por diseño— a **toda** la lógica: nadie enhebró el país por debajo del esquema.

### 3.1 · GEO (stages 06, 01) — el sangrado **IRREVERSIBLE**
| # | Break | Sev | Disparo |
|---|---|---|---|
| G1 | `GeoResolver.load(conn)` sin país: `geo.py:153` `SELECT code,name FROM geo_province` y `:157` `… FROM geo_municipality` **sin** `WHERE country_code` → ES-28 y DE-28 colisionan en el índice en memoria → `municipality_code` **erróneo** acuñado en `cdp_code` inmutable | **C** | 2.º país cargado |
| G2 | Geocoders ciegos: `geocode.py:79` `ProvinceGeocoder.load`, `:130` `MunicipalityGeocoder.load`, `PostcodeIndex.load` sin filtro; índice clavado por `province_code` pelado | **C** | KNN cross-país |
| G3 | `seed_geo_centroides.py:97` `UPDATE geo_municipality SET lat,lon WHERE code=$3` sin país → `(ES,'28001')` y `(DE,'28001')` se **pisan** | **C** | seed 2.º país |
| G4 | Trigger `entity_set_comarca()` (`0018_comarca.sql:30-31`) `SELECT m.comarca_id … WHERE m.code=NEW.municipality_code` **sin** país → entity DE hereda comarca ES | **C** | INSERT entity DE |
| G5 | Anchos `CHAR(2)/CHAR(5)` soldados a INE (`0001:5,19`) → AGS DE (8), ISTAT IT (6), DOM FR `971-976` (3) **desbordan** la columna | **C** | INSERT geo no-ES |
| G6 | `_norm` `encode("ascii","ignore")` (`geo.py:52`) destruye no-latino → claves vacías; `_PROVINCE_ALIASES` 100 % ES (`geo.py:61`); `_GAZETTEER_PATH` INE ES (`geo.py:46`); `province_code` asume `s.zfill(2)` (`geo.py:205`) | **C** | EL/BG/RU/JP |

> **Por qué es lo primero:** `cdp_code` es **inmutable** y append-only. Un mint con `municipality_code` erróneo (por resolver/trigger/geocoder ciego) re-keya la entidad **sin vuelta atrás** y huérfana la historia. Estas seis costuras deben coserse **antes** de cargar datos de cualquier 2.º país.

### 3.2 · IDENTITY-DEALER (stages 04, 01) — el **false-merge transfronterizo**
| # | Break | Sev | Disparo |
|---|---|---|---|
| I1 | **Espina nuclear:** `cluster_dealers.py` con **0** ocurrencias de `country_code` (grep `-c`=0); `SCOPE_CONDITION="kind <> 'particular' AND status <> 'closed'"` (`:59`) sin filtro país; `RUN_ID="dealer-identity-det-v1"` único (`:56`); `v_canonical`/`v_dealer_resolved` sirven **el único** run `vam_verified` global (`0020:62-67`, `0028:36-44`) → país #2 re-clusteriza el mismo run que ES y comparten un gate servido | **C** | identity del país #2 |
| I2 | Block-key edge-1 `normalized_name + municipality_code` cross-país (`cluster_dealers.py:404,:416`); `0053:4`/PK compuesta prueban que `code '28'` coexiste ES↔DE → mismo nombre+muni **funde** dealers cruzando frontera | **C** | DB compartida |
| I3 | `phone_es.py:36` `len==9` + `_VALID_LEADING={6,7,8,9}` (`:20`), `+34`/`0034` (`:32`); `phone_match_key(raw)` **sin** parámetro país (`:41`): **rechaza** DE/IT/JP (señal más fuerte = 0 aristas) y **acepta en silencio** móviles FR/PT de 9 dígitos como ES → false-merge cross-país | **C** | FR/PT/DE/IT/JP |
| I4 | `codes.py:30` `_normalize` NFKD+`encode("ascii","ignore")`: nombre JP → `''` → `canonical_key` colapsa **todo** dealer name-only de un municipio a **un** `cdp_code` en mint-time (over-merge **IRREVERSIBLE**, append-only) | **C** | JP / no-latino |
| I5 | `DIGITAL_SOURCES`/sufijos legales/chain-tokens ES-only (`cross_source_dedup.py:117-153,196-211,163-176`) → overlay cross-source es **no-op** para DE; sufijos `gmbh/srl/sarl` no se strippean → under-merge | **H** | DE/IT/FR |
| I6 | `build_canonical_dedup.py:98-101` clava censo ES (`EXPECTED_DEDUPED_COUNT=54489…`) y `sys.exit(1)` al divergir (`:447-463`) → el 1.er build con filas no-ES **aborta** el sello | **H** | 1.er dedup multipaís |

> **Sutileza arquitectónica (no es break, es contrato):** `canonical_key` es country-blind **a propósito** (`codes.py:62`) para que enhebrar país **nunca** re-keye una entidad ES. La consecuencia: dos entidades pan-EU que comparten dominio desnudo (p. ej. `ford.es` ↔ `ford.de`) producen la **misma** `canonical_key`. Por eso el aislamiento de país **no** puede descansar en la clave de dedup — debe imponerse en el **scope del build de cluster** (M1/M2) + el **invariante de aislamiento** (`COUNTRY-PROOF-INVARIANT.md`). La country-blindness es una virtud que **exige** la red de seguridad, no la sustituye.

### 3.3 · VEHICLE (stage 05) — el coche que cruza la frontera
| # | Break | Sev | Disparo |
|---|---|---|---|
| V1 | `cluster_vehicles.py` **0** `country_code`; `:258` carga todos los países (`WHERE v.status='available'`, sin país); `:255` selecciona solo `e.province_code`; `:397` `block_key=(make,model,year,km,province)` con provincia **pelada** → VW Golf ES-28 y DE-28, mismo year/km, precio ±2 % (ambos EUR), título ASCII igual → **se fusionan** cruzando frontera | **C** | país #2 eurozona |
| V2 | Anti-FP Check 1 `HAVING COUNT(DISTINCT e.province_code) > 1` (`:852`) → cluster ES-28+DE-28 da `count=1` → **pasa** y certifica "0 cross-province" mientras el cross-PAÍS es **invisible** | **C** | sello miente |
| V3 | Comparación de precio currency-blind (grep `currency`=0 en cluster/delta); `price_sanity.py:49` `PRICE_MAX=5_000_000` calibrado EUR → coche JPY normal → `None` → Signal B y delta **ciegos** para JP | **C** | MX/JP |
| V4 | Watermark de over-count country-blind: agrupa por `province_code` pelado, `subject_key='ES_national'` → cota ±dup_ci mezcla fantasmas transfronterizos | **H** | DB multipaís |

### 3.4 · EXTRACT / NORMALIZE (stage 03) — corrupción silenciosa + moneda
| # | Break | Sev | Disparo |
|---|---|---|---|
| E1 | `ingest.py:49` gate `province_code.isdigit() and "01"<=code<="52"`: prefectura JP `01-47` **pasa** → mis-asignada a provincia ES; IT `MI/RM` → `isdigit()` False → **todo** dealer IT rechazado ("`out of Spain range`", `:50`); FR/DE `zip[:2]` mal-mapeado | **C** | JP/IT/FR/DE/PT |
| E2 | **Sin dimensión de moneda** en el contrato `Vehicle`; `priceCurrency` descartado (`recipe_extract_web.py:79`); parser EU disperso corrompe MX `'1,234.56'` ~1000× (`dealerprobe._to_float`) | **C** | MX/JP |
| E3 | `fuel`/`transmission` almacenados **verbatim en español** (`ingest.py:101`); `_STOCK_HINT`/`_COUNT_HINT` solo ES (`recipe_extract_web.py:28-32`) → no descubre stock no-ES | **H** | DE/FR/IT/PT |

### 3.5 · SCRAPE (stage 02) — el motor habla español + **los 31 mints**
| # | Break | Sev | Disparo |
|---|---|---|---|
| S1 | `fingerprints.py:46,65,80` `Accept-Language: es-ES,es;q=0.9,…` soldado en los 3 perfiles → todo fetch no-ES anuncia navegador español (tell de geo/locale) | **C** | cualquier host no-ES |
| S2 | `free_proxies.py:27` `_COUNTRY="ES"` constante de módulo; `:34,39,43` `&country={_COUNTRY}` → harvester solo cosecha IPs españolas | **C** | WAF IP-bound no-ES |
| S3 | `autoscout24.py:21` `_BASE=…es` + path `/profesionales/` (ES); el replay re-invoca el código ES → la plataforma que debía probar "parser reusable" exige **reescribir** la fuente | **C** | AS24 .de/.fr/.it |
| **S4** | **31 funciones de mint de plataforma** clavan `return f"CDP-ES-{SENTINEL}-{_base32(digest)}"` y **0** usan `mint_code` [VERIFIED grep `-rl`=31, `-c`=31, mint_code-importers=0] → país #2 minta `CDP-ES-` para sus plataformas (**corrupción de identidad** silenciosa). El path por-dealer (`cdp_code()`) es seguro; el de plataforma **no** | **C** | drain plataforma país #2 |
| S5 | `ban_detector.py:64-73` `_STRONG_BLOCK_MARKERS` mezcla tokens de vendor con texto ES ('algo se detuvo') → página de bloqueo localizada >30 KB puede clasificar `OK` → interstitial servido como inventario; `governor.py` hosts ES, scar AS24 clavado a `.es` no `.de` | **H** | DE/FR/JP |

### 3.6 · SEAL-DENOMINADOR (stage 07) — el denominador miente
| # | Break | Sev | Disparo |
|---|---|---|---|
| Q1 | **Ninguna** tabla de la cadena de sellado lleva país: `discovery_capture.province_code char(2)` (`0048:39`), `exhaustiveness_estimate.province_code char(2)` (`0048:58`), `discovery_list.list_key text PK` (`0048:23`) → estratos de 2 países colisionan; ES `'01'` y FR `'01'` se mezclan | **C** | país #2 |
| Q2 | `seal.compute()` nunca enhebra país; `:69` auto-carga `triangulation.load_external_census()` → `DEFAULT_COUNTRY='ES'` → build DE triangula contra censo español DIRCE/DGT/FACONAUTO | **C** | build no-ES |
| Q3 | 5 de 7 listas ortogonales son fuentes ES (`lists.py:27-49`: `dgt_cat→DGT`, `autocasion_census→CENSUS`, `aedra/aecs/acevas→ASSOC`, `borme_cnae→REG`, `dork_municipal→DORK`); roster extranjero cae a `MKT` (excluido de `ORTHOGONAL_LISTS`) → `K<3` → casi nada sella | **C** | DE/FR/IT/PT/MX/JP |
| Q4 | `v_exhaustiveness_seal` sirve **un** build global (`0048:86-87` `ORDER BY created_at DESC LIMIT 1`) → build del país #2 **borra** de la vista el sello del país #1 | **H** | 2.º build |
| Q5 | `load_denominator_provincia.py:64-65` `raise SystemExit` si `len(rows) != 52`; `:38` `RATIO_451_45=23085/88621` CNAE-451 ES; `DEALER_KINDS`/segmentos enum ES | **H** | sello registral no-ES |

### 3.7 · SERVING-API (stage 08) — el bleed en la API
| # | Break | Sev | Disparo |
|---|---|---|---|
| R1 | **La 1.ª ficha del dominó:** `servable_entity` (`0046:17-18`) **no** proyecta `country_code` aunque `entity` lo lleva desde `0052` → los routers geo no pueden filtrar país | **C** | raíz del serving ciego |
| R2 | `geo.py:370` `… FROM geo_province WHERE code=$1` (fetchrow, sin `ORDER BY`) y endpoints por `province_code` **pelado**; tras `0053` `'28'` es `(ES,28)` o `(DE,28)` → fila de país arbitrario, lista mezcla ES+FR | **C** | `/geo/28/…` |
| R3 | Agregados nacionales sin predicado país (`/stats`, `/geo/seal`, `/geo/exhaustiveness`) → **suman** ES+país#2; `product_stats` fila única `CHECK(id=1)` (`0055:15`) no puede guardar conteos por país | **C** | 2.º país aterriza |
| R4 | `/geo/{prov}/tree` exige `comarca_id IS NOT NULL` + JOIN `geo_comarca` (división **solo** ES); el árbol expone `ccaa_code/ccaa_name` (`geo.py:420`, taxonomía ES) → árbol **vacío** para todo país sin comarca; `v_province_seal` agrupa por `province_code` sin país | **C** | DE/cualquiera sin comarca |
| R5 | `cache.py:79` `_cache_key` = `METHOD+PATH+sorted-qs` **sin** dimensión tenant; ningún router acepta param país (grep=0) → bleed de cuerpo cacheado cross-país | **H** | multi-tenant |

### 3.8 · ORQUESTACIÓN (stage 09) — un solo país a la vez
| # | Break | Sev | Disparo |
|---|---|---|---|
| O1 | Advisory lock `_SCHEDULER_SINGLETON_LOCK=0x43415244` **constante fija** (`scheduler.py:913`), discovery `+1` (`discover_schedule.py:50`); el lock vive en la PG compartida → scheduler DE hace `pg_try_advisory_lock==false` y **SystemExit** (`:919-925`) → **solo UN país cosecha a la vez** | **C** | DB compartida |
| O2 | `_due_sources` (`scheduler.py:344`) y `find_silent_sources` (`silence_watchdog.py:57`) son scans globales sin predicado país; `source_health` sin `country_code` → watchdog FR dispara alertas sobre fuentes ES; scheduler global salta filas FR como unmapped → FR nunca cosecha | **C** | país #2 |
| O3 | `source_health.source_key` PK única (`0004:25`); fuentes pan-EU (`as24_wholesale`, portales OEM) son **un** módulo sirviendo N países → seed IT colisiona en la PK con la fila ES | **C** | fuente pan-EU |
| O4 | REGISTRY ~50 `SourceEntry` ES hardcodeadas (`scheduler.py:150-325`); `DISCOVERY_REGISTRY` 5 vectores ES; `ADAPTERS` ES → onboarding = **editar 3 dicts Python** (viola "pack sin reescribir código") | **H** | país #2 |
| O5 | **BUG ZOMBIE** (todos los países): alertas `:silence` **nunca** se resuelven — `record_run` en éxito solo resuelve `build_origin(source_key, phase)` con `phase∈{scrape,discover}` (`health.py:172-173`); ningún llamador toca `:silence` | **H** | recuperación de fuente |

### 3.9 · GATES-`complete.py` + BRAIN (stage 10) — el sello como kill-switch
| # | Break | Sev | Disparo |
|---|---|---|---|
| A1 | G1 (puerta de SELLADO) clava **dos** literales ES: `complete.py:89` `_CDP_CODE_RE=^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` y `:73` `_PROVINCE_RE=^(0[1-9]\|[1-4][0-9]\|5[0-2])$` (01-52) → ningún `CDP-DE-*` pasa el match (`:145`) → `derive_verdict`=INCOMPLETE **para siempre**. Además `:305,:309` globean `countries/ES/…` literal. El 6.º-blocker, vigilado por `xfail` estricto | **C** | toda entidad no-ES |
| A2 | `coverage_gap` usa `COVERAGE_ANCHORS` clavados a registros ES (`detect.py:78-80`: `desguace 1292` DGT, `concesionario_oficial 2018` FACONAUTO); el censo externo del sellador es ES (`seal.py:69`) → coverage y el intervalo certificado dan basura. (`grep CDP-ES = 0 en detect.py` es **prueba hueca**: estas son magic numbers de instituciones ES sin el substring) | **C** | DE/FR/IT/MX/JP |
| A3 | `detect_fabrication` `FAB_PRICE_CEIL=5_000_000` EUR implícito (`detect.py:70,:579`); la columna `currency` existe (`0003:14`) pero **ningún detector la lee** → inventario premium MX/JP marcado fabricación con `quarantines=True` → vistas `servable_*` lo **excluyen** → el sello = **kill-switch del país entero**, y CI verde (sin golden de detector por país) | **C** | MX/JP |
| A4 | `price_trap` `GROUP BY make,model,year` sin partición país/moneda (`detect.py:786`); `entity_kind` es **ENUM** Postgres (`0005:13`) → kind nuevo = `ALTER TYPE` (migración), no override en `country.toml` | **C/H** | cohorte multipaís |
| A5 | Capa-2 IA local = **0 en código**; capa-3 Claude orquestador = **0 en código** (`decision_request`/bus/`cover(CC)` no existen) → toda escalación muere en `ESCALATE_OWNER` (humano) | — | a construir |

---

## 4 · El patrón único de remediación
Los 10 inquisidores hallaron **la misma rotura con la misma forma**. No son 10 problemas: es **uno**, repetido en cada capa.

> **La causa raíz:** el esquema sabe de país; la lógica que lo consume, no. Toda query/clave/lock/gate que cruza por `code`/`province_code`/`municipality_code`/`source_key` asume implícitamente "un solo inquilino = ES".

**La cura, en una línea:** *enhebrar `country_code` desde el esquema (donde ya vive) hacia cada query, clave, lock y gate —con `DEFAULT 'ES'` para byte-identidad— y parametrizar las constantes soldadas a ES (anchos de código, rangos, bandas de precio/moneda, locale, país de proxies, locks) en un pack por país.*

Es el **espejo exacto del patrón `0052`**: aditivo, byte-idéntico mientras ES sea el único inquilino, promoción a clave compuesta **solo** cuando un 2.º inquilino lo fuerce (igual que `0052→0053` hizo con la PK geo). Ningún byte de ES se reescribe; ES pasa a ser el **pack #1 explícito**, no la base implícita.

---

## 5 · El programa unificado de remediación
Seis movimientos. Cada uno con `DEFAULT 'ES'` → la salida ES queda byte-idéntica (la pinea el golden `test_country_golden`/`test_country_coexistence`).

### M1 · Country-scope toda lectura/escritura/índice/trigger
Añadir `WHERE country_code = $1` y clavar los índices por `(country_code, code)` en **toda** junta que hoy cruza por `code` pelado.
- **Geo:** `GeoResolver.load(conn, country_code='ES')` (`geo.py:151`) con `WHERE country_code=$1` en ambos fetch (`:153,:157`); los 3 loaders de `geocode.py:79/130/225`; `seed_geo_centroides.py:71,97`; trigger `entity_set_comarca` (`0018:30-31` → migración aditiva `CREATE OR REPLACE … AND m.country_code=NEW.country_code`).
- **Identity-dealer:** `cluster_dealers` `SCOPE_CONDITION += " AND country_code=$1"` (`:59`) y `RUN_ID` sufijado por país (`:56`); **per-country served gate** (`v_canonical`/`v_dealer_resolved` filtran país); E.164 con prefijo país en `phone_match_key` (I3).
- **Vehicle:** `cluster_vehicles` SELECT `e.country_code` (`:255`); `block_key=(country_code,currency,geo_unit,make,model,year,km)` (`:397`); anti-FP Check `cross-(country,province)` (`:852`).
- **Serve:** proyectar `country_code` en `servable_entity` (`0046:17` — la 1.ª ficha, R1) y `v_servable_dealer`; predicado país en los endpoints geo/agregados (`geo.py:370` y `/stats`,`/geo/seal`,`/geo/exhaustiveness`); `product_stats` PK `(country_code)` en vez de `CHECK(id=1)` (R3).
- **Seal:** `country_code` en `discovery_capture`/`exhaustiveness_estimate` (`0048:39,58`); estrato `(country_code, region_code, segment)`; `seal.compute(country_code=…)` que pasa el país a `load_external_census` (`:69`).
- **Orchestrate:** `country_code` en `source_health` (espejo `0052`, `DEFAULT 'ES'`); `_due_sources`/`find_silent_sources` con filtro `WHERE country_code = ANY($countries)`; resolver el zombie `:silence` (O5) añadiendo `resolve_recovered_silence_alerts` al watchdog.

### M2 · Country-scope la identidad de run/gate/lock
- **Run:** `RUN_ID` por país; gate `vam_verified` por país; **vista `latest` por país** (`DISTINCT ON (country_code) … ORDER BY created_at DESC`) en `v_exhaustiveness_seal` (Q4) y `v_dealer_resolved`.
- **Lock-por-país:** `lock_key(role, country) = BASE + role_offset + country_ordinal*OFFSET` (O1); `scheduler_lease.holder='harvest:<CC>'`. Por defecto, **un** productor de host drena todos los países en serie (sin riesgo AS24); aislamiento por-VPS solo si se necesita. `lock_heartbeat` ya recibe `lock_key` como parámetro → el cambio es solo en el call-site.
- **Source key:** convención `<plataforma>_<cc>` + promoción a PK compuesta `(country_code, source_key)` cuando exista colisión pan-EU real (O3) — espejo `0052→0053`.

### M3 · Parametrizar las constantes ES en un `CountryProfile` / `country.toml`
Consolidar **todos** los literales ES dispersos en un objeto/pack por país, con ES como default:
- **Ancho + alfabeto del código de subdivisión** (province/municipality): `CHAR(2)/CHAR(5) → VARCHAR`; AGS DE (8) / ISTAT IT (6) / DOM FR (3) / Córcega `2A-2B` (G5).
- **Rango de provincia — quitar el gate INE `01-52`:** `ingest.py:49` (`isdigit() and "01"<=code<="52"`) y `complete.py:73` (`_PROVINCE_RE`) → **validador inyectado** desde el pack; ES mantiene `01-52` declarado en su `.toml`.
- **Locale / `Accept-Language`:** `fingerprints.py:46,65,80` (S1) → factory parametrizada por pack; normalización/transliteración (G6, I4, E1) — fold ASCII para latino-con-diacríticos, transliteración previa (unidecode/ICU, CC0) para no-latino.
- **`_COUNTRY` de proxies (egress):** `free_proxies.py:27` (S2) → parámetro `country` en `fetch_candidates/harvest_alive`; bbox/ISO de POI por pack.
- **Identity locale:** plan de teléfono E.164 (I3), sufijos legales, chain-tokens, taxonomía de fuentes digitales (I5).
- **Geo:** `_PROVINCE_ALIASES` (`geo.py:61`), `_GAZETTEER_PATH` (`:46`), `KNN_MAX_DISTANCE_KM` (`geocode.py:49`).
- **Seal:** membresía `source_key→bucket` ortogonal (Q3), `kind→segment`, ancla de censo externo (Q2, A2), `IDENT_CAP`/`threshold` calibrados.
- **Detector thresholds:** `FAB_PRICE_CEIL`/`PRICE_TRAP_FLOOR`/`KM_MAX` **por moneda** (A3-A4).

### M4 · Enrutar los **31 conectores** + widen la gramática del `cdp_code` (fix de motor, UNA vez)
- Enrutar las **31** funciones de mint de `pipeline/platform/*` (todas `return f"CDP-ES-{SENTINEL}-{_base32(digest)}"`, 0 usan `mint_code`, S4/A1) por `mint_code(province_code=…, digest=…, country_code=CC)`. `_base32(digest)` no cambia → ES **byte-idéntico** (lo pinea el golden).
- `complete.py:89` `_CDP_CODE_RE → ^CDP-([A-Z]{2})-([0-9A-Z]{2})-[0-9A-HJKMNP-TV-Z]{8}$` (superset estricto: acepta todo ES byte-a-byte + alfanumérico para Córcega `2A/2B`); quitar el `xfail` de `test_country_golden` (auto-flip a XPASS).
- `_PROVINCE_RE` y `_NATIONAL_KINDS` table-driven desde el pack; el read-path de receta `complete.py:305,309` → `paths.recipe_root(country_of_cdp(cdp_code))` (cero literal `'ES'`).
> **Aviso de inmutabilidad:** la gramática de subdivisión (ancho+alfabeto+centinela nacional `'00'`) debe **congelarse ANTES de mintear/sellar** el país. El `[0-9A-Z]{2}` de 2 chars sigue **sin** admitir DOM FR `971-976` (3 dígitos) ni ISTAT IT >99: esos países exigen una **decisión de ancho de gramática** previa, no un swap de regex. Un país onboardeado con gramática equivocada exige re-mintear códigos inmutables → huérfana el ledger append-only. "Onboarding reversible" es **falso** en el eje de la gramática del código (open item §8).

### M5 · Dimensión de moneda
- Añadir `price_currency` al contrato canónico `Vehicle` (hoy `price` es float pelado, sin moneda — E2); capturar `priceCurrency` (hoy descartado, `recipe_extract_web.py:79`); **leer** la `vehicle.currency` ya existente (`0003:14`) en toda comparación/gate de precio (V3, A3).
- `block_key` de Signal B incluye moneda (mismo bloque ⇒ misma moneda, `cluster_vehicles.py:397`); bandas `PRICE_MAX`/`FAB_PRICE_CEIL`/trap **por moneda** desde el pack.

### M6 · El guard que lo vuelve invariante (→ `COUNTRY-PROOF-INVARIANT.md`)
M1–M5 son "30 fixes que hay que recordar" — un checklist que se pudre. El level-up los **mecaniza**:
1. **Invariante de aislamiento en DB:** todo cluster servido (`entity_cluster`/`canonical_dedup`/`vehicle_cluster`) con `COUNT(DISTINCT country_code)=1`; un build que cruce países **falla y no sirve**.
2. **Golden cross-country en CI:** fixture que colisiona DE↔ES en el vector exacto; corre en cada push.
3. **Meta-test "toda query servida lleva país":** enumera las queries de `services/api/` y pipeline que tocan `geo_*`/`entity`/`vehicle` y asserta el filtro `country_code` (o allow-list justificada).

---

## 6 · Orden de ataque por riesgo
> Mandato: **los false-merge transfronterizos primero** — son IRREVERSIBLES (`cdp_code` inmutable, append-only) y corrompen **dato servido**. Lo reversible (bleed de serving, agregados mezclados) espera.

| Tier | Riesgo | Breaks | Por qué este orden |
|---|---|---|---|
| **T0 — IRREVERSIBLE, antes de tocar dato no-ES** | Corrupción permanente de identidad/geo | **G1-G4** (resolver/geocoder/centroide/trigger), **I4** (normalize no-latino), **G6**, `discover.py:91` (cdp_code + INSERT sin país), **S4** (31 mints) | Un `cdp_code` mal acuñado no se revierte; huérfana el ledger |
| **T1 — false-merge silencioso al aterrizar país #2** | Fusión cross-país en clustering (**identidad + vehículo**) | **I1-I3** (cluster_dealers + block-key + phone), **V1-V2** (cluster_vehicles + anti-FP Check) | Dispara en silencio en cuanto hay 2.ª fila; **ningún test lo captura hoy** |
| **T2 — bloqueo de almacenamiento/completion** | El dato no entra o nunca sella | **G5** (ancho `CHAR`), **A1/E1** (rango `01-52` + gate INE), **M4** (gramática `cdp_code`) | Sin esto el país ni se guarda ni pasa G1 |
| **T3 — mentira de sello (sin corromper dato)** | Sub/over-count, kill-switch | **Q1-Q3** (MSE sin país + censo + buckets), **A2-A4** (anchors + currency detectors) | El sello miente o cuarentena el país entero |
| **T4 — bleed de serving (visible, no corruptor)** | Mezcla en la API | **R1-R5** (servable_entity + endpoints + agregados + cache) | Corregible en caliente; no corrompe la DB |
| **T5 — multi-tenancy de orquestación** | Un país a la vez | **O1-O5** (lock + due/silence + registry + zombie) | El motor corre; escala después |

**Regla de oro de secuencia:** **T0 y T1 cierran en el mismo PR que siembra el país #2** (los inquisidores 06/04/05 lo exigen: sembrar antes corrompe en silencio). T2 puede ir en el PR de pre-flight. T3-T5 son aditivos y reversibles → se ejecutan y reportan sin gate (salvo el push).

---

## 7 · Cómo se prueba cada fix (golden cross-country)
La 2.ª-vía ortogonal canónica (espejo `test_country_coexistence.py`, ya probado con DE revertido byte-idéntico): **insertar una entidad DE sintética que COLISIONA con una ES en el vector exacto de la rotura y verificar 0 merge / 0 bleed**, todo en una txn que hace `ROLLBACK`.

Conforme a `ANTI-DRIFT-HARDENING` §"Cómo se PRUEBA", un fix no es `[VERIFIED]` hasta tener **las tres**: (a) test verde en CI, (b) intento adversarial que **falla** en romperlo, (c) verificación por vía independiente. Sin las tres → `[ASSUMED]`.

| Capa | Fixture de colisión | Asserts (0 merge / 0 bleed) | 2.ª vía independiente |
|---|---|---|---|
| **Geo** | muni DE con `code` que colisiona con ES (p. ej. `'28001'`) | resolver/geocoder devuelven el code **del país pedido**; centroide ES intacto; entity DE hereda comarca **DE** (no ES) | recompute SQL: `COUNT(*)` filas con FK-bleed = 0 |
| **Identity** | entity DE que colisiona en `(norm_name, municipality_code)` con una ES (reusa `'28'`) | resolver **NO** las funde; `COUNT(DISTINCT country_code)` por cluster servido = 1 | **recompute SQL: clusters con `>1 country_code` en lo servido = 0** |
| **Vehicle** | VW Golf DE-28 y ES-28, mismo year/km, precio ±2 % (EUR) | **0** fusiones cross-país; anti-FP Check cuenta `DISTINCT (country_code,province_code)` | watermark por `(country, province)`, no `province` pelado |
| **Extract** | dealer JP (prefectura 13) + IT (`MI`) + MX (`'1,234.56'`) | JP no cae en provincia ES; IT no es rechazado; MX no se lee ÷1000; `price_currency` poblado | golden de normalización por país (no solo ES) |
| **Phone** | móvil FR de 9 dígitos que comparte dígitos con uno ES | `phone_match_key` los mantiene **distintos** (clave E.164 con prefijo país) | golden por locale (espejo `test_phone_es`) |
| **Seal** | estrato DE-`'01'` y ES-`'01'` | estratos **no** colisionan; `seal.compute(country='DE')` triangula contra censo DE; `latest` por país | prosecutor R/LCMCR re-deriva desde `verification_verdict` crudo |
| **Serve** | request `/geo/28/…` y `/stats` con país #2 sembrado | cada vista devuelve **solo** el país pedido; agregados no suman ES+DE | HTTP-vs-SQL (`test_api_gaps`): `/stats?country=CC` == `COUNT` SQL crudo independiente |
| **Orchestrate** | scheduler DE + ES sobre la misma PG | ambos adquieren su `lock_key(role,country)`; due/silence scopeados; 0 `UNMAPPED` por país | log watchdog vs `SELECT count(*) FROM alert WHERE origin LIKE '%:silence' AND resolved_at IS NULL` |
| **Brain / Gates** | entity DE que debe pasar G1 | `CDP-DE-*` pasa G1 (xfail→XPASS); detector no cuarentena coche DE legítimo | `test_country_coexistence` prueba ES byte-idéntico (un sello que mueva ES = rechazado) |

**El guard canónico del aislamiento de identidad** (la fila clave de la tabla; plantilla completa y vector verificado en `COUNTRY-PROOF-INVARIANT.md` §"Vector concreto"):
```sql
-- Debe devolver 0 filas. >0 = false-merge transfronterizo en lo servido.
SELECT d.resolved_cdp_code, COUNT(DISTINCT e.country_code) AS n_countries
FROM v_dealer_resolved d
JOIN entity e ON e.cdp_code = d.cdp_code
GROUP BY d.resolved_cdp_code
HAVING COUNT(DISTINCT e.country_code) > 1;
```

**Invariante transversal de prueba:** ES byte-idéntico en cada caso (txn revertida asertando que los conteos ES no cambian). Un fix que mueva ES es un fix **rechazado**. → El criterio de aceptación de TODA la transformación spine es el **golden cross-country en verde** de `COUNTRY-PROOF-INVARIANT.md`: ninguna capa se declara country-proof sin él.

---

## 8 · Open items honestos (causa declarada)
No se da por hecho lo que no se probó. Estos son blockers/limitaciones con causa, **no** abandono del puesto:

1. **`[ASSUMED]` coexistencia byte-idéntica del piloto DE:** verificado el código `0052/0053` + andamiaje golden, **no** la corrida viva (PG `:5433` caído). Re-validar contra DB viva antes de declarar el sello del 2.º país.
2. **Decisión-1 sobre-afirmada:** "el piloto DE probó que el esquema es paramétrico" es `[ASSUMED]`. El piloto usó muni sintético `'28001'` con forma ES exacta; **nunca** ejercitó ancho de 8 dígitos (G5), nombre no-latino (I4/G6) ni provincia de 3 dígitos. La rama de relajación del CHECK (`country_code<>'ES'`, `0053:168`) **nunca** se ejecuta en el sello. El ancho `CHAR` (T2) es deuda **no probada**.
3. **Gramática de código no reversible:** congelar ancho+alfabeto+centinela del `cdp_code` **antes** de mintear/sellar es obligatorio; corregirlo después exige re-mintear códigos inmutables y huérfana el ledger append-only. El widen `[0-9A-Z]{2}` (M4) cubre Córcega `2A/2B` pero **no** DOM FR `971-976` ni ISTAT IT >99. Falta un **gate de congelación de gramática** explícito en el onboarding.
4. **Cifras de sello vivas `[ASSUMED]`:** MSE ~37,7 % / registral ~80,5 % provienen de recon/`liveseal` con el stack caído; no re-ejecutables ahora. Re-correr `cli.py` contra DB viva antes de declarar progreso.
5. **Capa-2/Capa-3 a construir:** IA local y bus de decisiones de Claude = **0 en código** (A5). El enhebrado de país es prerequisito; el cerebro genérico se diseña sobre él (`stages/10-automation.md`).
6. **Mercados de cola fina:** el cierre RESOLVED exige quórum `>=2` vías independientes; un país con un portal dominante (PT, regiones MX/JP) puede no producirlas → todo el país cae a `ESCALATE_OWNER`. Falta un **piso de independencia por país** en el pack (stage 10).
7. **Gates PENDING-OWNER** (no paran el loop, `00-MASTER`): GASTO (€>0), ESCRITURA EN PROD/serving-of-record, LEGAL (RGPD/ToS de fuentes no-ES). El enhebrado es €0 y reversible; el despliegue del 2.º país en prod queda gateado por owner.

---

## 9 · Una frase para cerrar
El esquema ya sabe de país. El `SPINE` es coser esa misma verdad —`country_code`— a través de cada query, clave, lock y gate de la lógica, con `DEFAULT 'ES'` para que ES no se mueva ni un byte, y `COUNTRY-PROOF-INVARIANT` para que la genericidad, una vez cosida, **no pueda volver a descoserse en silencio**. Eso, y nada menos, es "transformar a genérico".
