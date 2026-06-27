# REMEDIATION-BLUEPRINT — El puente biblia→build (PR por PR, irreversibles primero)

> El documento que un builder —humano o IA— sigue para **ejecutar** el des-cegado de país sin perderse ni desviarse. Traduce el diagnóstico de [`SPINE-COUNTRY-THREADING.md`](SPINE-COUNTRY-THREADING.md) (las roturas), el guard de [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md) (la garantía mecánica) y los open items de [`COUNTRY-PACK-CONTRACT.md` §6](COUNTRY-PACK-CONTRACT.md) (OI-1..OI-11) en una **lista ordenada de PRs ejecutables**. Doctrina madre: [`00-MASTER.md`](00-MASTER.md) · blindaje: [`ANTI-DRIFT-HARDENING.md`](ANTI-DRIFT-HARDENING.md).
>
> **Cada `path:línea` de este documento fue re-leído de primera mano contra el código vivo esta sesión (2026-06-27).** No transcribe los docs: confirma a la fuente. Lo que la DB caída impide verificar va `[ASSUMED]` con causa.

---

## 0 · Cómo leer y ejecutar este blueprint

| § | Contenido |
|---|---|
| [1](#1--blindaje-y-procedencia) | Blindaje + procedencia (`[VERIFIED]` vs `[ASSUMED]`, DB caída) |
| [2](#2--la-puerta-de-secuencia-la-única-regla-dura) | La puerta de secuencia — la única regla dura |
| [3](#3--mapa-de-prs-grafo-de-dependencias) | Mapa de PRs + grafo de dependencias |
| [4](#4--pr-0--harness-country-proof-preflight-establece-el-rojo) | PR-0 · Harness country-proof (preflight) |
| [5](#5--pr-1--t1-identidad-dealer-country-scope-irreversible) | PR-1 · T1 Identidad-dealer |
| [6](#6--pr-2--t1-vehículo-country-scope-irreversible) | PR-2 · T1 Vehículo |
| [7](#7--pr-3--t2-numerador-canónico-único-v_servable_dealer) | PR-3 · T2 Numerador canónico único |
| [8](#8--pr-4--t3-geo-country-scope-irreversible) | PR-4 · T3 Geo country-scope |
| [9](#9--pr-5--t4-dimensión-país-en-la-cadena-de-sellado) | PR-5 · T4 Cadena de sellado |
| [10](#10--pr-6--t5-filtro-de-país-en-serving) | PR-6 · T5 Serving |
| [11](#11--pr-7--t6-minting-de-cegado-g1--31-mints--write-site-irreversible) | PR-7 · T6 Minting de-cegado |
| [11.5](#115--pr-8--pr-9--capas-de-fusión-omitidas-ola-25) | **PR-8 · PR-9** — capas de fusión omitidas (Ola 2.5) |
| [12](#12--follow-on-fuera-del-tren-irreversible) | Follow-on (post-T6) |
| [13](#13--criterio-de-cierre-de-toda-la-transformación) | Criterio de cierre |

> **Endurecimiento Ola 2.5 (2026-06-27).** Una re-verificación adversarial de 4 lentes (`train-completeness`, `golden-sufficiency`, `additive-safety`, `spine-completeness`) **ROMPIÓ** la versión previa de este blueprint: el «tren irreversible» omitía vectores de false-merge transfronterizo. Lo integrado en esta revisión: **(1)** `cluster_vehicles` **Signal A photo_url** (HIGH, irreversible) → ampliado PR-2; **(2)** anti-FP `print` post-write → convertido en **pre-write bloqueante** en PR-2; **(3)** guard mecánico de `vehicle_cluster` + golden Signal A → PR-0 + invariante; **(4)** `cluster_dealers` **arista-4 fuzzy** → ampliado PR-1; **(5)** resolver **β** (`resolve_entities`) → nuevo **PR-8**; **(6)** `canonical_dedup` (`deep_link`, Layer-2 servida) + `cross_source_dedup` → nuevo **PR-9**. Más correcciones de honestidad en PR-3, PR-7, F7 y nuevas filas F8-F10 (§12). Cada cita re-leída de primera mano esta sesión.

**Convención de cada PR:** `ID` · `tier` · `IRREVERSIBLE|REVERSIBLE` · **Scope** (1 frase) · **Archivos** (`path:línea [VERIFIED]`) · **Migración** (aditiva, espejo `0052`) · **Golden cross-country** (el vector de colisión DE↔ES → 0 merge/0 bleed) · **Gate de aceptación** (`dry-run:5434 → golden → Ferrari → CI`) · **Rollback** · **PENDING-OWNER**.

**Principio invariante de todos los PRs:** aditivo, €0, `DEFAULT 'ES'` / `country_code='ES'` por defecto en cada firma → **ES byte-idéntico**, pineado por `tests/test_country_golden.py` `[VERIFIED]`. Un PR que mueva un byte de ES es un PR **rechazado**.

---

## 1 · Blindaje y procedencia

Conforme a [`ANTI-DRIFT-HARDENING.md`](ANTI-DRIFT-HARDENING.md): cada cita es `[VERIFIED path:línea]` (leída en la fuente esta sesión) o `[ASSUMED]` (declarada, sin prueba viva).

- **Stack vivo CAÍDO** (PG `:5433`/dry-run `:5434` no responden). Consecuencia honesta: **toda cifra de DB y toda corrida de golden es punto-en-el-tiempo `[ASSUMED]`**. Los goldens de cada PR están **especificados y con su fixture**, pero **se corren al reiniciar la DB** (secuencia owner). Declarar "probado/funcional" sin correrlos sería el maquillaje que el mandato prohíbe. Donde digo "golden verde" es el **criterio de aceptación**, no una afirmación de hecho presente.
- **Scaffolding de prueba YA existe** `[VERIFIED]`: `tests/test_country_golden.py` (pinea ES byte-idéntico + helpers `paths`) y `tests/test_country_coexistence.py` (fixtures sintéticas DE `(DE,'28')`↔`(ES,'28')`, muni `'28001'`, patrón txn-`ROLLBACK`). Los goldens de este blueprint **extienden esos dos archivos**, no parten de cero.
- **Helpers de país YA existen** `[VERIFIED pipeline/paths.py:22,33,50,55]`: `DEFAULT_COUNTRY="ES"`, `recipe_root(cc)`, `census_dir(cc)`, `country_of_cdp(cdp)`. Varios fixes (T4 censo, T6 glob de receta) **reutilizan** estos helpers en vez de construir parametricidad nueva.

---

## 2 · La puerta de secuencia — la única regla dura

> **Mandato** ([`SPINE` §6 "regla de oro"](SPINE-COUNTRY-THREADING.md), [`COUNTRY-PROOF-INVARIANT`](COUNTRY-PROOF-INVARIANT.md)): el `cdp_code` es **inmutable y append-only**. Un mint con provincia/municipio erróneo o un cross-merge transfronterizo **no se revierte** — huérfana el ledger. Por eso:

**REGLA DURA (PENDING-OWNER en el push, no en el código):**

```
Ningún país #2 se SIEMBRA (ni una fila geo/entity no-ES) hasta que
el TREN IRREVERSIBLE esté { merged + AMBOS guards verdes + golden cross-country verde }:
   PR-1  identidad-dealer : aristas 1-3 + ARISTA-4 fuzzy SQL (Ola 2.5)
   PR-2  vehículo         : Signal B firma + SIGNAL A photo_url + anti-FP PRE-WRITE BLOQUEANTE (Ola 2.5)
   PR-4  geo
   PR-7  minting + write-site + G1
   PR-8  β inventory-fingerprint : CERRAR su country-scope ANTES de poder gatear la capa (Ola 2.5)
   PR-9  canonical_dedup (deep_link) : Layer-2 SERVIDA de v_dealer_resolved (Ola 2.5)
Los PRs REVERSIBLES { PR-0, PR-3, PR-5, PR-6 } pueden aterrizar antes o después:
son vistas/predicados aditivos, no corrompen dato.
cross_source_dedup (gateado vam_verified=FALSE) viaja con PR-9: NO bloquea el tren
mientras no se gatee, pero su country-scope es PRECONDICIÓN para gatearlo.
```

> **Por qué el tren creció de 4 a 6 (Ola 2.5).** La versión previa listaba sólo `{PR-1, PR-2, PR-4, PR-7}` y dentro de PR-1/PR-2 cubría sólo un subconjunto de las aristas. La re-verificación probó que **Signal A** (`cluster_vehicles.py:326-376`, country-blind por diseño, `only_photo` sin firma `[VERIFIED :471-473]`), la **arista-4 fuzzy** (`cluster_dealers.py:262-392` `[VERIFIED]`), el resolver **β** (`resolve_entities.py`, una compuerta de activación de una **fábrica** de cross-merge) y `canonical_dedup` (**ya servido** vía `v_dealer_resolved` Layer-2 `[VERIFIED 0028:57-67]`) son rutas de fusión transfronteriza **igual de irreversibles**. Las cuatro entran al tren.

El orden de presentación de abajo es el orden de tiers del mandato (`T0/T1 → T6`); PR-8 y PR-9 se ejecutan dentro de la misma ventana «sin sembrar». El orden **AMONG** los irreversibles es flexible; lo que **no** es flexible es que **los seis** (PR-1·2·4·7·8·9) cierren —con **los dos** guards de aislamiento (dealer `v_dealer_resolved` **y** vehículo `v_canonical_vehicle`) en verde— antes del primer byte no-ES. PR-0 establece el **ROJO** que prueba que las roturas existen; cada PR siguiente vuelve **su** porción **VERDE**.

---

## 3 · Mapa de PRs (grafo de dependencias)

| PR | Tier | Reversibilidad | Scope en una línea | OI / Break | Depende de |
|----|------|----------------|--------------------|-----------|-----------|
| **PR-0** | preflight | REVERSIBLE | Harness country-proof: fixtures de colisión (ROJO) + **2 guards** (dealer + **vehículo**) + meta-test | INVARIANTE | — |
| **PR-1** | T1 | **IRREVERSIBLE** | `cluster_dealers` scopea cada block-key por `country_code` — **aristas 1-3 + arista-4 fuzzy SQL** | I1·I2 / OI-3-adj | PR-0 |
| **PR-2** | T1 | **IRREVERSIBLE** | `cluster_vehicles` scopea load + **Signal A photo_url** + Signal B block_key + anti-FP **pre-write BLOQUEANTE** por país | V1·V2 | PR-0 |
| **PR-3** | T2 | REVERSIBLE | `v_servable_dealer` = **único** numerador; proyecta `country_code` | OI-7·OI-9 | PR-0 |
| **PR-4** | T3 | **IRREVERSIBLE** | Geo resolver/geocoder/centroide/trigger scopeados por país | G1-G4 / OI-3 | PR-0 |
| **PR-5** | T4 | REVERSIBLE | `country_code` en estratos MSE + caller de censo + `latest`-por-país | Q1·Q2·Q4 / OI-6 | PR-0, PR-3 |
| **PR-6** | T5 | REVERSIBLE | Predicado país en routers + agregados + `product_stats` | R1-R5 / OI-9 | PR-3 |
| **PR-7** | T6 | **IRREVERSIBLE** | G1 regex widen + 31 mints→`mint_code` + write-site `discover` | OI-1·OI-2·OI-4·OI-5 | PR-0, PR-4 |
| **PR-8** | T1-adj | **IRREVERSIBLE** (cerrar-antes-de-gatear) | `resolve_entities` (β): `country_code` en fingerprint-merge + city-guard + phone | Ola 2.5 / SH8 | PR-0, **PR-2** |
| **PR-9** | T2 | **IRREVERSIBLE** (`canonical_dedup` servida) + REVERSIBLE (`cross_source` gateado) | `build_canonical_dedup` (`deep_link`) + `cross_source_dedup` (`value,muni`) scopeados por país | Ola 2.5 | PR-0 |

> **Por qué PR-7 depende de PR-4:** el write-site (`discover._upsert`) mintea **con** el `province_code` que el resolver geo (PR-4) le entrega; si el resolver aún cruza países, el mint nace con muni errónea aunque el prefijo `CDP-{CC}-` ya sea correcto. Geo de-cegado **antes** que minting de-cegado.
>
> **Por qué PR-8 depende de PR-2:** β consume `vehicle_cluster.canonical_vehicle_ulid` `[VERIFIED resolve_entities.py:462-466]`. Si Signal A (PR-2) aún cruza la frontera, β **hereda** ese cross-merge y lo amplifica vía Jaccard de inventario, aunque su propio block-key ya esté scopeado. Vehículo de-cegado **antes** que β.
>
> **Por qué PR-9 es mitad irreversible:** `build_canonical_dedup` escribe `canonical_dedup`, **Layer-2 de la vista SERVIDA `v_dealer_resolved`** `[VERIFIED 0028:57-67]` → un cross-merge ahí se sirve (irreversible en efecto). `cross_source_dedup` escribe `entity_cluster` con `vam_verified=FALSE` `[VERIFIED :52-53]` → reversible mientras no se gatee.

---

## 4 · PR-0 · Harness country-proof (preflight, establece el ROJO)

`tier preflight` · **REVERSIBLE** · cierra el meta-mandato de [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md)

**Scope (1 frase):** instalar el **guard de aislamiento de país** (validación SQL aditiva) + el **golden cross-country** (fixtures de colisión DE↔ES que hoy fallan en ROJO) + el **meta-test enumerador** "toda query servida lleva país", de modo que cada PR posterior tenga un criterio de aceptación mecánico.

**Archivos:**
- `tests/test_country_coexistence.py` `[VERIFIED:83-166]` — **extender** con los fixtures de colisión por capa (reutiliza el patrón `(DE,'28')`↔`(ES,'28')`, muni `'28001'`, txn-`ROLLBACK`). Una clase por capa: `TestIsolationIdentity` (**arista-1 name+muni Y arista-4 fuzzy `levenshtein<=2`** — son rutas distintas, una no cubre la otra), `TestIsolationVehicle` (**Signal A foto compartida `[VERIFIED :326-376]` Y Signal B firma** — el fixture Signal-B-solo NO ejercita Signal A), `TestIsolationDealerDedup` (**NUEVA**: `canonical_dedup` por `deep_link` cross-país), `TestIsolationBeta` (**NUEVA**: β fingerprint-merge cross-país, Jaccard>=0.30), `TestIsolationGeo`, `TestIsolationSeal`, `TestIsolationServe`.
  > **Aviso Ola 2.5 sobre el write-site:** el fixture DE de `test_country_coexistence.py:260` inserta a mano un `CDP-DE-28-*` distinto `[VERIFIED :180-185, :349-356]`, **saltándose** el write-site country-blind (`discover.py:91-104` mintea `CDP-ES-` y absorbe por `ON CONFLICT (cdp_code)` `[VERIFIED :101]`). El golden NO puede reproducir el over-merge de producción del write-site hasta PR-7; mientras tanto el guard `COUNT(DISTINCT country_code)>1` ve **una** fila 'ES' y pasa en falso. Documentar este límite en el fixture (no fingir cobertura que no hay).
- `tests/test_country_proof_meta.py` — **nuevo**: enumera las queries de `services/api/` + `pipeline/` que tocan `geo_*`/`entity`/`vehicle` y asserta filtro `country_code` o allow-list justificada (hoy la allow-list = todas; se vacía PR a PR). **Ampliar el enumerador (Ola 2.5)** para que cubra también las rutas que el original omitía: `services/api/stats.py:_QUERIES` `[VERIFIED :22-38 — dealers + geo_province/geo_municipality sin país]`, el writer `scripts/refresh_product_stats.py:30` (`VALUES (1,…) ON CONFLICT (id)`) `[VERIFIED]` y el reader `services/api/routers/ops.py:88` (`FROM product_stats WHERE id = 1`) `[VERIFIED]` — `product_stats` no es `geo_*`/`entity`/`vehicle`, así que el enumerador estrecho NO lo veía.
- `migrations/0057_country_isolation_guard.sql` — **nuevo**, aditivo: **DOS** funciones de aserción de build (no triggers bloqueantes todavía): `assert_country_isolation_dealer()` sobre `v_dealer_resolved` y `assert_country_isolation_vehicle()` sobre `v_canonical_vehicle` (espejo del anti-FP `[VERIFIED cluster_vehicles.py:843-853]` cambiando `province_code`→`country_code`). Cada `cluster_*` la invoca al final y el CI las corre. Promoción a trigger `BEFORE`/constraint cuando el país #2 exista.

**Los guards canónicos — DOS, no uno** (la Ola 2.5 probó que el guard dealer-only dejaba `vehicle_cluster` sin backstop pese a nombrarlo el invariante §1):

Guard DEALER `[VERIFIED estructura contra migrations/0028_dealer_resolved.sql:70-76 — v_dealer_resolved proyecta cdp_code + resolved_cdp_code; resuelve B1 ∘ canonical_dedup Layer-2 :57-67]`:
```sql
-- Debe devolver 0 filas. >0 = false-merge transfronterizo en lo servido.
SELECT d.resolved_cdp_code, COUNT(DISTINCT e.country_code) AS n_countries
FROM v_dealer_resolved d
JOIN entity e ON e.cdp_code = d.cdp_code   -- [VERIFIED 0028:70-76 — cdp_code de la entidad-miembro]
GROUP BY d.resolved_cdp_code
HAVING COUNT(DISTINCT e.country_code) > 1;
```

Guard VEHÍCULO `[VERIFIED v_canonical_vehicle 0023:57-76; vehicle sin country_code → JOIN entity]` — **NUEVO (Ola 2.5)**:
```sql
-- Debe devolver 0 filas. >0 = false-merge de vehículo transfronterizo servido.
SELECT vc.canonical_vehicle_ulid, COUNT(DISTINCT e.country_code) AS n_countries
FROM v_canonical_vehicle vc                       -- [VERIFIED 0023:57-76]
JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
JOIN entity  e ON e.entity_ulid  = v.entity_ulid  -- [VERIFIED entity.country_code 0052]
GROUP BY vc.canonical_vehicle_ulid
HAVING COUNT(DISTINCT e.country_code) > 1;
```

**Migración:** `0057` additive; `country_code` ya vive en `entity` `[VERIFIED 0052]` y `vehicle` lo alcanza por `JOIN entity` `[VERIFIED vehicle sin country_code en 0003]` → **ambos** guards son construibles HOY sin tocar dato.

**Golden cross-country (el ROJO de partida):** con el fixture DE inyectado en txn, las cinco clases `TestIsolation*` **fallan** (merge/bleed presente) → prueba mecánica de que las roturas existen. Marca cada assert con el PR que lo vuelve verde (`# GREEN by PR-1`, etc.). El meta-test parte con allow-list llena y un `# TODO(PR-N)` por entrada.

**Gate de aceptación:** dry-run:5434 (instalar `0057` + correr el guard → **>0 filas = ROJO esperado**) → golden (las `TestIsolation*` en **xfail→fail documentado** hasta su PR) → Ferrari (suite ES byte-idéntica, sin regresión) → CI (verde salvo los xfail declarados).

**Rollback:** `DROP FUNCTION IF EXISTS assert_country_isolation;` + revertir los dos archivos de test. Cero efecto sobre dato servido.

**PENDING-OWNER:** ninguno (€0, additive, no toca prod).

---

## 5 · PR-1 · T1 Identidad-dealer country-scope `IRREVERSIBLE`

`tier T1` · **IRREVERSIBLE** · breaks **I1·I2** ([`SPINE §3.2`](SPINE-COUNTRY-THREADING.md)) · vector exacto del invariante

**Scope (1 frase):** añadir `country_code` a **cada** block-key de **las cuatro** aristas de `cluster_dealers.py` — las tres exactas (1-3) **y la arista-4 fuzzy SQL** — (y sufijar `RUN_ID`/`SCOPE` por país) para que dos dealers de países distintos con el mismo `(normalized_name, municipality_code)` **nunca** caigan en la misma componente union-find.

**Archivos (`[VERIFIED]`, `grep -c country_code cluster_dealers.py = 0`):**
- `pipeline/identity/cluster_dealers.py:59` `[VERIFIED]` `SCOPE_CONDITION = "kind <> 'particular' AND status <> 'closed'"` → `+ " AND country_code = %(cc)s"` (param, default `'ES'`).
- `cluster_dealers.py:56` `[VERIFIED]` `RUN_ID = "dealer-identity-det-v1"` → `f"dealer-identity-det-v1-{cc}"` (run por país; el gate servido `v_dealer_resolved` se ancla por país en PR-5/M2).
- `cluster_dealers.py:410-430` `[VERIFIED]` los tres índices `idx_name_muni`/`idx_phone_muni`/`idx_web_muni` → clave `(nn, muni, cc)` / `(ph, muni, cc)` / `(wh, muni, cc)`. El `SELECT` que hidrata `entities` añade `e.country_code` a la proyección.
- **ARISTA-4 fuzzy SQL (Ola 2.5 — omitida en la versión previa):** `cluster_dealers.py:262-392` `_load_fuzzy_sql_edges` `[VERIFIED]`. Es una fusión **más ancha** que la arista-1 porque une nombres NO idénticos (`levenshtein<=2` `[VERIFIED :377]`). Tres cambios:
  - `:312-318` `[VERIFIED]` la temp table `_tmp_fuzzy_candidates(entity_ulid, muni_code, norm_name)` gana columna `country_code text NOT NULL`; el `INSERT … VALUES` `[VERIFIED :319-325]` añade `cc` a cada fila (la proyección que la hidrata `[VERIFIED :290-302]` ya puede leer `e.country_code`).
  - `:366` `[VERIFIED]` el self-join `ON a.muni_code = b.muni_code` → `+ " AND a.country_code = b.country_code"`; el índice `:327` `[VERIFIED CREATE INDEX … (muni_code)]` → `(country_code, muni_code)`.
  - el `GROUP BY muni_code` del cómputo de bloques `[VERIFIED :336]` y del `eligible` `[VERIFIED :369-374]` → `GROUP BY country_code, muni_code` (un país no contamina el `FUZZY_BLOCK_CAP` del otro).
- `cluster_dealers.py:404-406` (docstring de aristas) → reflejar el `+ country_code` en el comentario, incluida la arista-4.

> **Honestidad (Ola 2.5):** bajo el default mono-país (`SCOPE_CONDITION` + `AND country_code=%(cc)s` → `_load_entities` devuelve un solo país) la arista-4 es **segura** sin cambio. Pero la decisión misma de scopear las aristas 1-3 sólo tiene sentido en co-residencia multipaís; en ese régimen (dealers drenados `ANY(ccs)`), la arista-4 funde `'talleres garcia'` ES-28001 con `'talleres garcic'` DE-28001. Si se scopean 1-3 y se deja la 4, el guard va **ROJO sin fix en el tren**. Por eso entra aquí, no en follow-on.

**Migración:** ninguna nueva (la columna existe `[VERIFIED 0052]`). El `cluster_*` ya escribe `entity_cluster` por `RUN_ID`; el sufijo de run es additive.

**Golden cross-country** (`TestIsolationIdentity`, vuelve VERDE el assert de PR-0):
- **Fixture arista-1:** entity DE que colisiona en `(norm_name='talleres garcia', municipality_code='28001')` con una ES.
- **Fixture arista-4 (Ola 2.5):** entity DE `norm_name='talleres garcic'` en `municipality_code='28001'` vs ES `'talleres garcia'` (`levenshtein=1`) — ejercita el self-join fuzzy `muni`-solo `[VERIFIED :366]`, que el fixture exacto **no** toca.
- **Asserts:** (a) el resolver **NO** las funde — distinta componente, **ni por arista-1 ni por arista-4**; (b) recompute SQL del guard `§4` = **0 filas** con `COUNT(DISTINCT country_code)>1`; (c) ES byte-idéntico: los `resolved_cdp_code` de las filas ES no cambian (txn-`ROLLBACK`).
- **2.ª vía independiente:** el guard de `0057` (recompute SQL) co-igual al assert Python.

**Gate de aceptación:** dry-run:5434 (sembrar fixture DE → correr `cluster_dealers` → guard = 0) → golden (`TestIsolationIdentity` verde) → Ferrari (clustering ES idéntico: mismo nº de componentes, mismos `resolved_cdp_code`) → CI.

**Rollback:** revertir el diff (el `RUN_ID` viejo re-genera el cluster ES idéntico; no hay migración que deshacer). Como el run es por-`RUN_ID`, el run ES legacy sigue intacto hasta recomputar.

**PENDING-OWNER:** el **recompute del cluster ES en prod** (re-correr `cluster_dealers` sobre la DB de servir) toca serving-of-record → gate ESCRITURA-EN-PROD. El PR (código + golden en dry-run) es €0/reversible; el recompute productivo lo firma el owner.

---

## 6 · PR-2 · T1 Vehículo country-scope `IRREVERSIBLE`

`tier T1` · **IRREVERSIBLE** · breaks **V1·V2** ([`SPINE §3.3`](SPINE-COUNTRY-THREADING.md))

**Scope (1 frase):** scopear el load, **el índice de Signal A (`photo_url`)**, el `block_key` de Signal-B y el check anti-FP de `cluster_vehicles.py` por `(country_code[, currency])`, **y convertir el anti-FP en un chequeo PRE-WRITE que aborta la txn**, para que un VW Golf ES-28 y otro DE-28 (firma idéntica) **o** dos coches que comparten una `photo_url` de feed mayorista/CDN **no** se fusionen cruzando frontera y, si un bug lo intentara, el run **falle y no escriba** en vez de imprimir el cruce después de servirlo.

**Archivos (`[VERIFIED]`, `grep -c country_code cluster_vehicles.py = 0`):**
- `cluster_vehicles.py:255` `[VERIFIED]` `e.province_code` → `e.province_code, e.country_code` en la proyección del load (`_load_vehicles`). *(Nota: `vehicle` no tiene `country_code` `[VERIFIED: ninguno en 0003]`; viene de `entity` por el `LEFT JOIN` ya presente `[VERIFIED :257]`.)*
- `cluster_vehicles.py:258` `[VERIFIED]` `WHERE v.status = 'available'` → `+ " AND e.country_code = %(cc)s"` (param, default `'ES'`) — o, si se drena multipaís en serie, `country_code = ANY(%(ccs)s)` con la dimensión presente en el bucket.
- **SIGNAL A photo_url (Ola 2.5 — omitida en la versión previa; es HIGH e irreversible):** `cluster_vehicles.py:326-376` `[VERIFIED]`. El índice `idx_photo` se teclea por `_normalize_photo_url` SOLO `[VERIFIED :327-331]`, sin país ni provincia; sus únicos guards (high-collision `K>=12` `[VERIFIED :338-347]`, km=0 `[VERIFIED :365-367]`, cross-generación `[VERIFIED :372-373]`) son **todos** ciegos al país, y el docstring la declara «suficiente sola» `[VERIFIED :10-14]`, fundiendo con `only_photo` sin firma `[VERIFIED :471-473]`. Fix: la clave del índice pasa de `norm` a **`(country_code, norm)`** — o, equivalente, el par candidato `(va,vb)` se descarta si `va.country_code != vb.country_code` antes de `photo_edges.add` `[VERIFIED :374-375]`. Esto blinda el caso «misma foto mayorista en feed pan-EU < K=12, ES-28 y DE-28, mismo model/year, km>0, span=0» que pasa **todos** los guards actuales.
- `cluster_vehicles.py:397` `[VERIFIED]` Signal B `block_key = (make, model, year, km, province)` → `(country_code, currency, make, model, year, km, province)`. **Requiere** `vehicle.currency` en la proyección (ver dependencia M5/currency en Follow-on §12; hoy `province` ya separa de facto ES↔DE porque `28` es compartido pero el par `(cc,province)` lo blinda).
- **anti-FP PRE-WRITE BLOQUEANTE (Ola 2.5 — el `print` post-write es la rotura):** `cluster_vehicles.py:834-859` `[VERIFIED]` `_run_anti_fp_checks` (a) cuenta `DISTINCT e.province_code` `[VERIFIED :852]`, ciego al país, y (b) sólo hace `print` `[VERIFIED :858-859]`. Peor: en `main()` corre como **Step 5** `[VERIFIED :944]` **después** del `_write_to_pg` Step 4 `[VERIFIED :939]` y del `conn.autocommit = True` `[VERIFIED :942]` que **commitea** — el cross-merge ya está escrito y servido. **Dos cambios, no uno:**
  1. **Contar el par país+provincia:** `HAVING COUNT(DISTINCT e.province_code) > 1` → `HAVING COUNT(DISTINCT (e.country_code, e.province_code)) > 1` (un cluster ES-28+DE-28 da `count=2`, ya no `count=1` silencioso).
  2. **Mover el check a PRE-WRITE y hacerlo bloqueante:** calcular las violaciones **en memoria sobre `cluster_rows`** (antes de `_write_to_pg`) o sobre una tabla `TEMP` dentro de la txn; si `>0`, `raise` → el `except` `[VERIFIED :946-948]` propaga y el `finally` cierra sin commit (la txn era `autocommit=False` `[VERIFIED :921]`). Sólo tras 0 violaciones se permite el write + `autocommit=True`. El `print` informativo puede quedar **post-write** como telemetría, pero **el gate que decide escribir es el pre-write**.

**Migración:** ninguna nueva. (La dimensión `currency` del `block_key` se beneficia de M5 pero no la bloquea: el par `(country_code, province)` ya cierra el false-merge transfronterizo; la moneda cierra el caso intra-país multi-moneda, marcado en §12.)

**Golden cross-country** (`TestIsolationVehicle` — **DOS fixtures, no uno**):
- **Fixture Signal A (Ola 2.5 — el que faltaba):** dos `vehicle` con el **mismo** `_normalize_photo_url` (feed mayorista/CDN, `< K=12` listings), `entity` ES-`28` y DE-`28`, mismo `make/model/year`, `km>0`, `span=0`. Pasa **todos** los guards actuales (high-collision, km, cross-gen) → hoy funden. Sin sembrar este `photo_url` compartido, el golden NO cubre Signal A.
- **Fixture Signal B firma:** dos `vehicle` — VW Golf `entity` ES-`28` y DE-`28`, `year/km` iguales, `price` ±2 % (ambos EUR), título ASCII idéntico.
- **Asserts:** (a) **0** fusiones cross-país en `vehicle_cluster` para **ambos** vectores (Signal A y Signal B); (b) el guard de vehículo `§4` (`v_canonical_vehicle` JOIN `entity`) = **0 filas** con `COUNT(DISTINCT country_code)>1`; (c) el anti-FP **pre-write** lanza/aborta ante el cruce (la txn **no** escribe) en vez de imprimir "OK (0)" tras servir; (d) ES byte-idéntico (clustering de vehículos ES sin cambio).

**Gate de aceptación:** dry-run:5434 (fixture Signal A + Signal B → `cluster_vehicles` → la txn **ABORTA** sin escribir pre-fix-incorrecto / escribe 0 cross-país post-fix) → golden (`TestIsolationVehicle` verde en ambos vectores + guard vehículo = 0) → Ferrari (delta/cluster ES idéntico) → CI.

**Rollback:** revertir el diff; sin migración. El run de vehículos legacy (`RUN_ID` `cluster_vehicles`) sigue válido hasta recomputar.

**PENDING-OWNER:** recompute productivo del cluster de vehículos → gate ESCRITURA-EN-PROD (firma owner). Código + golden en dry-run son €0/reversibles.

---

## 7 · PR-3 · T2 Numerador canónico único (`v_servable_dealer`)

`tier T2` · **REVERSIBLE** · cierra **OI-7** (núcleo realmente sin resolver) + **OI-9** (proyección país)

**Scope (1 frase):** cablear `v_servable_dealer` `[VERIFIED 0056, 0 lectores]` como el **único** numerador de punto-de-venta en `stats.py`, el router `/geo` y el sello, y proyectar `country_code` en `servable_entity` + `v_servable_dealer` para que el numerador sea contable por país.

**El problema verificado — cuatro numeradores distintos hoy `[VERIFIED]`:**
- `services/api/stats.py:23-26` → `count(DISTINCT vdr.resolved_cdp_code) WHERE e.kind NOT IN ('particular','desguace')` (~54.6k/19.1k).
- `migrations/0042_province_seal_view.sql:18-44` `v_province_seal` → `count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid)) WHERE kind IN ('compraventa','concesionario_oficial') AND EXISTS available vehicle`.
- el MSE/sello → ~18.3k.
- `migrations/0056_v_servable_dealer.sql:26-37` `v_servable_dealer` → el numerador **canónico declarado** (publish-gated + active + sells-cars + garaje-con-inventario), **con 0 lectores**.

**Archivos:**
- `migrations/0046_servable_entity_status_filter.sql:17-23` `[VERIFIED — 37 cols, sin country_code]` → `CREATE OR REPLACE VIEW servable_entity` añadiendo `country_code` a la proyección (col 38). Aditivo; `DEFAULT 'ES'` en `entity` garantiza byte-identidad.
- `migrations/0058_v_servable_dealer_country.sql` — **nuevo**: `CREATE OR REPLACE VIEW v_servable_dealer` re-proyectando `se.country_code` (ahora disponible) para que el conteo sea `GROUP BY country_code`.
- `services/api/stats.py:23-26` → reemplazar el numerador inline por `count(DISTINCT resolved_cdp_code) FROM v_servable_dealer [WHERE has_inventory] [AND country_code=$cc]`.
- `services/api/routers/geo.py:113-114` (`/geo/seal`) y `migrations/0042:18-44` → re-anclar el numerador de `v_province_seal` a `v_servable_dealer` (predicado de punto-venta unificado, ya no `kind IN (...)` divergente).

**Migración:** `0046` re-emitida (additive, +1 col), `0058` nueva (additive). Espejo `0052`: `DEFAULT 'ES'`.

**Golden cross-country** (`TestIsolationServe` parcial + test de numerador):
- **Assert de unificación:** `stats numerator == v_province_seal numerator == seal numerator` para ES (los cuatro colapsan a uno) — hoy divergen, post-PR coinciden.
- **Assert de país:** con DE sembrado, `v_servable_dealer WHERE country_code='ES'` == conteo ES crudo independiente; `='DE'` no suma ES.
- **Byte-identidad:** el conteo ES de `v_servable_dealer` no cambia al añadir la columna.

**Gate de aceptación:** dry-run:5434 (recrear vistas → numeradores coinciden) → golden (test de numerador verde) → Ferrari (el headline "Puntos de venta" coincide con el set paginado, el bug de inflación ~2.9x cerrado) → CI.

**Rollback:** `0046`/`0058` son `CREATE OR REPLACE VIEW` → restaurar la proyección previa (rollback embebido en cada `.sql`, espejo del bloque de `0056:45-46`). Cero riesgo: una vista es una query guardada.

**PENDING-OWNER:** ninguno para el merge (vistas + lectura). El **número público** que cambia (de ~54.6k a ~36.3k/18.3k) es una corrección de honestidad ya flagged por el owner (`plans/P-census-data-quality.md`); su publicación en el serving-of-record es gate ESCRITURA-EN-PROD.

> **Corrección de honestidad (Ola 2.5, lente additive-safety).** El invariante «cada PR es ES byte-idéntico / un PR que mueva un byte de ES se rechaza» (§0, §1·este-doc) está genuinamente **scopeado a `cdp_code`/identidad/paths**, NO a los **agregados servidos**. PR-3 re-ancla el numerador `dealers` de `services/api/stats.py:22-28` `[VERIFIED — count(DISTINCT vdr.resolved_cdp_code) WHERE kind NOT IN (particular,desguace) AND EXISTS servable_vehicle]` a `v_servable_dealer`, lo cual **cambia el conteo público ES** (~19.1k → 18.3k/36.3k según el predicado de inventario `[VERIFIED 0056:17-37]`) — una mutación servida **deliberada y disclosed**, no una violación del invariante de identidad. PERO `tests/test_country_golden.py` **NO cubre `/stats`** `[VERIFIED — pinea mint_code+cdp_pair, :56-68]`, así que el guard de regresión es ciego a esa superficie. **Acción:** el meta-test de PR-0 (ampliado) debe enumerar `stats.py:_QUERIES`; y el blueprint NO debe presentar el blanket «ES byte-idéntico» como si cubriera los agregados — sólo cubre identidad.

---

## 8 · PR-4 · T3 Geo country-scope `IRREVERSIBLE`

`tier T3` · **IRREVERSIBLE** · breaks **G1-G4** ([`SPINE §3.1`](SPINE-COUNTRY-THREADING.md)) · cierra **OI-3**

**Scope (1 frase):** añadir `country_code` (param, default `'ES'`) a **toda** lectura/escritura/trigger que hoy cruza `geo_province`/`geo_municipality` por `code` pelado, para que ES-`28` y DE-`28` **nunca** colisionen en el índice del resolver ni se pisen en el centroide ni hereden comarca cruzada — los tres irreversibles porque alimentan el mint del `cdp_code`.

**Archivos (`[VERIFIED]`, `grep -c country_code pipeline/geo.py = 0`):**
- `pipeline/geo.py:151` `async def load(cls, conn)` → `load(cls, conn, country_code: str = "ES")`.
- `pipeline/geo.py:153` `SELECT code, name FROM geo_province` → `... WHERE country_code = $1`.
- `pipeline/geo.py:157` `SELECT code, name, province_code FROM geo_municipality` → `... WHERE country_code = $1`. El índice en memoria pasa de `_muni[province_code]` a `_muni[(country_code, province_code)]` (o instancia de resolver por país).
- `scripts/seed_geo_centroides.py:71,97` `[VERIFIED]` `SELECT ... WHERE code = ANY($1::char(5)[])` / `UPDATE geo_municipality SET lat,lon WHERE code = $3` → ambos `+ AND country_code = $N` (G3: hoy `(ES,'28001')` y `(DE,'28001')` se pisan).
- `migrations/0059_comarca_trigger_country.sql` — **nuevo**, aditivo: `CREATE OR REPLACE FUNCTION entity_set_comarca()` añadiendo `AND m.country_code = NEW.country_code` a `[VERIFIED 0018_comarca.sql:31]` `WHERE m.code = NEW.municipality_code` (G4: hoy entity DE hereda comarca ES).
- (pack, no motor) `pipeline/geo.py:46-48` `_GAZETTEER_PATH`, `:51-53` `_norm` (ascii-ignore destruye no-latino), `:61-73` `_PROVINCE_ALIASES` 100 % ES → **inyectados desde el pack** `countries/<CC>/geo/` (pieza 2 del contrato); ES mantiene sus valores en su `.toml`. Anchos `CHAR(2)/CHAR(5)` → `VARCHAR` es deuda T2-almacén marcada en §12 (AGS DE 8 dígitos desborda).

**Migración:** `0059` (trigger `CREATE OR REPLACE`, additive, rollback embebido). Sin cambio de columnas (la PK geo ya es `(country_code, code)` `[VERIFIED 0053]`).

**Golden cross-country** (`TestIsolationGeo`):
- **Fixture:** muni DE `code='28001'` que colisiona con ES.
- **Asserts:** (a) `GeoResolver.load(conn, 'DE')` devuelve el `code` **del país pedido**, no el ES; (b) centroide ES intacto tras seed DE; (c) entity DE hereda comarca **DE** (o `NULL`), no la comarca ES; (d) recompute SQL: filas con FK-bleed geo = 0.
- **2.ª vía:** recompute SQL independiente del índice en memoria.

**Gate de aceptación:** dry-run:5434 (seed muni DE → `load('ES')`/`load('DE')` disjuntos; trigger no cruza) → golden (`TestIsolationGeo` verde) → Ferrari (resolución geo ES idéntica: mismos `province_code`/`municipality_code` resueltos) → CI.

**Rollback:** revertir `pipeline/geo.py`/`seed_geo_centroides.py`; `0059` trae su `DROP FUNCTION`/restore embebido. Con default `'ES'`, el comportamiento previo se preserva exacto.

**PENDING-OWNER:** ninguno para el merge (€0, additive, default ES). La **carga de filas geo no-ES** es parte del seed del país #2 → gateado por la puerta de secuencia §2.

---

## 9 · PR-5 · T4 Dimensión país en la cadena de sellado

`tier T4` · **REVERSIBLE** · breaks **Q1·Q2·Q4** ([`SPINE §3.6`](SPINE-COUNTRY-THREADING.md)) · cierra **OI-6**

**Scope (1 frase):** añadir `country_code` (additive, `DEFAULT 'ES'`) a los estratos MSE, enhebrar el país al caller del censo externo, y hacer la vista de sello `latest`-por-país, para que dos países no colapsen en un estrato ni el último build borre el sello del otro.

**Archivos (`[VERIFIED]`):**
- `migrations/0060_seal_country_dimension.sql` — **nuevo**, aditivo (espejo `0052`):
  - `ALTER TABLE discovery_capture ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'` `[VERIFIED 0048:39 — province_code char(2), sin país]`; estrato pasa a `(country_code, province_code, segment)`; reescribir `ix_discovery_capture_stratum`.
  - `ALTER TABLE exhaustiveness_estimate ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'` `[VERIFIED 0048:58]`.
  - `CREATE OR REPLACE VIEW v_exhaustiveness_seal` con `latest` por país: `[VERIFIED 0048:82-88]` `ORDER BY created_at DESC LIMIT 1` → `DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC` (Q4: hoy el 2.º build borra el sello del 1.º).
- `pipeline/exhaustiveness/seal.py:69` `[VERIFIED]` `external_census = triangulation.load_external_census()` → `load_external_census(country_code=cc)`. **El loader YA es paramétrico** `[VERIFIED triangulation.py:36-50 — country_code default ES, census_dir(country_code)]`; el ciego es **el caller**. `seal.compute(...)` enhebra `cc` (default `'ES'`).
- `pipeline/exhaustiveness/capture.py:19` `[VERIFIED]` `DEALER_KINDS` → la membresía `source_key→bucket` ortogonal y `kind→segment` se inyectan desde `taxonomy.yaml` del pack (pieza 5); ES en su `.toml`.

**Migración:** `0060` additive, `DEFAULT 'ES'` → toda fila viva queda ES, byte-idéntica `[ASSUMED — re-validar contra DB viva: entity no-ES = 0 al cierre de sesión]`.

**Golden cross-country** (`TestIsolationSeal`):
- **Fixture:** estrato DE-`'01'` y ES-`'01'`.
- **Asserts:** (a) los estratos **no** colisionan (clave `(country_code, region, segment)`); (b) `seal.compute(country='DE')` triangula contra censo DE (`census_dir('DE')`), no DIRCE/DGT ES; (c) `v_exhaustiveness_seal` devuelve el sello de **ambos** países (el build DE no borra el ES).
- **2.ª vía:** prosecutor R/LCMCR re-deriva desde `verification_verdict` crudo, por país.

**Gate de aceptación:** dry-run:5434 (`0060` → estratos disjuntos → `seal.compute('ES')` da el sello ES histórico) → golden (`TestIsolationSeal` verde) → Ferrari (cifras de sello ES sin cambio `[ASSUMED MSE ~37,7 %/registral ~80,5 %, re-correr `cli.py` contra DB viva]`) → CI.

**Rollback:** `0060` trae `ALTER TABLE ... DROP COLUMN country_code` + restore de la vista (rollback embebido). Las columnas son additive `DEFAULT 'ES'` → drop reversible sin pérdida (toda fila era ES).

**PENDING-OWNER:** ninguno para el merge (€0, additive). La re-corrida del sello en prod → gate ESCRITURA-EN-PROD.

---

## 10 · PR-6 · T5 Filtro de país en serving

`tier T5` · **REVERSIBLE** · breaks **R1-R5** ([`SPINE §3.7`](SPINE-COUNTRY-THREADING.md)) · cierra **OI-9**

**Scope (1 frase):** añadir el predicado `country_code` a los routers `/geo` + `/stats` + agregados y promover `product_stats` a clave por país, para que tras sembrar el país #2 ninguna vista servida mezcle ES+DE (corregible en caliente; no corrompe DB).

**Archivos (`[VERIFIED]`, routers con 0 params país funcionales):**
- `servable_entity` ya proyecta `country_code` tras **PR-3** (dependencia) → los routers solo añaden el predicado.
- `services/api/routers/geo.py:229-268` `[VERIFIED]` `/geo/{province_code}/entities` → `WHERE se.province_code = $1` gana `AND se.country_code = $2` (default `'ES'` vía query param `?country=ES`). R2: hoy `'28'` resuelve a `(ES,28)` **o** `(DE,28)` arbitrario.
- `services/api/routers/geo.py:53,60,62,66,69-73` `[VERIFIED]` agregados `count(*) FROM entity WHERE kind <> 'particular' ...` y `count(*) FROM geo_province` → `+ AND country_code = $cc`.
- `services/api/routers/geo.py:113-114,169-172` `[VERIFIED]` lecturas de `v_province_seal`/`v_exhaustiveness_seal` → predicado país (las vistas lo proyectan tras PR-5).
- `services/api/stats.py` → `?country=` param; `migrations/0055_product_stats.sql:15` `[W1 — fila única CHECK(id=1)]` → `0061_product_stats_country.sql` additive: PK `(country_code)` en vez de `CHECK(id=1)` (R3: hoy no puede guardar conteos por país).
- `services/api/cache.py:79` `[W1 _cache_key sin tenant]` → incluir `country` en la clave de cache (R5: bleed de cuerpo cacheado cross-país).
- `services/api/routers/entities.py` → param país en los listados de entidades.

**Migración:** `0061` (product_stats por país, additive con backfill `country_code='ES'` de la fila única existente). Vistas `CREATE OR REPLACE`.

**Golden cross-country** (`TestIsolationServe`, completa el assert de PR-0):
- **Fixture:** request `/geo/28/entities?country=DE` y `/stats?country=DE` con DE sembrado.
- **Asserts:** (a) cada vista devuelve **solo** el país pedido; (b) `/stats?country=ES` == `COUNT` SQL crudo ES independiente (patrón `test_api_gaps` HTTP-vs-SQL); (c) sin param país, default `'ES'` → respuesta histórica byte-idéntica.

**Gate de aceptación:** dry-run:5434 (API contra DB con DE sembrado → 0 bleed) → golden (`TestIsolationServe` verde + meta-test §4 con allow-list de routers **vaciada**) → Ferrari (API ES idéntica sin param) → CI.

**Rollback:** vistas/`0061` con restore embebido; quitar los predicados (default ES preserva el comportamiento). Reversible en caliente.

**PENDING-OWNER:** ninguno para el merge (default ES = comportamiento actual). Exponer el selector de país en el serving-of-record → gate ESCRITURA-EN-PROD.

---

## 11 · PR-7 · T6 Minting de-cegado (G1 + 31 mints + write-site) `IRREVERSIBLE`

`tier T6` · **IRREVERSIBLE** · cierra **OI-1·OI-2·OI-4·OI-5** · el «6.º blocker»

**Scope (1 frase):** ensanchar el regex G1 para aceptar todo `CDP-{CC}-`, enrutar los 31 mints de plataforma por `mint_code(country_code=…)` y enhebrar `country_code` al write-site de `discover`, para que el país #2 minte su propio prefijo y pase el sellado en vez de acuñar `CDP-ES-` silenciosamente o quedar `INCOMPLETE` para siempre.

**Archivos (`[VERIFIED]`):**
- `pipeline/complete.py:89` `[VERIFIED]` `_CDP_CODE_RE = ^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` → `^CDP-([A-Z]{2})-([0-9A-Z]{2})-[0-9A-HJKMNP-TV-Z]{8}$` (superset estricto: acepta todo ES byte-a-byte + alfanumérico Córcega `2A/2B`). **El golden ya vigila el flip** `[VERIFIED tests/test_country_golden.py:279-291 — pytest.xfail(strict), "Remove this xfail once widened"]` → auto-XPASS al ensanchar.
- `pipeline/complete.py:73` `[VERIFIED]` `_PROVINCE_RE = ^(0[1-9]|[1-4][0-9]|5[0-2])$` (INE `01-52`) → validador **inyectado** desde `country.toml` resuelto por `paths.country_of_cdp(cdp_code)` `[VERIFIED paths.py:55 — helper existe]`; ES declara `01-52` en su `.toml`. (OI-5)
- `pipeline/complete.py:305,309` `[VERIFIED]` glob `countries / "ES"` literal → `paths.recipe_root(paths.country_of_cdp(cdp_code))` `[VERIFIED paths.py:33,55 — helpers existen]` (cero literal `'ES'`).
- **Los 31 mints** `[VERIFIED — 31 ocurrencias f"CDP-ES-" en pipeline/; 63 ficheros en pipeline/platform/ con el literal; 0 importan mint_code]`: cada `return f"CDP-ES-{SENTINEL}-{_base32(digest)}"` → `return mint_code(province_code=SENTINEL, digest=digest, country_code=campaign.country_code)`. `_base32(digest)` no cambia → ES **byte-idéntico** `[VERIFIED codes.py:53 — mint_code default ES reproduce el literal]`. El docstring `[VERIFIED codes.py:46-51 — afirma "exactly one place", FALSO hoy]` se vuelve verdadero.
  > **CAVEAT Ola 2.5 (lente additive-safety): los 31 NO son uniformes — port literal-por-`SENTINEL` re-keya un mint real.** No todos devuelven un centinela: `pipeline/platform/group_rentacar_vo_wholesale.py:803` `[VERIFIED]` devuelve `f"CDP-ES-{m.hq_province}-{_base32(digest)}"` con la **provincia REAL** (`m.hq_province`, p.ej. `'28'` northgate), no un `SENTINEL`. Aplicar la sustitución literal `province_code=SENTINEL` a `member_cdp_code` **reescribiría** el `cdp_code` ES (append-only, **IRREVERSIBLE**). Cada port DEBE leer la línea `return` real y preservar su segmento de provincia. Y `tests/test_country_golden.py:56-68` `[VERIFIED]` pinea **`mint_code`+`cdp_pair`**, NO las 31 funciones de plataforma → un port mal hecho pasa CI verde. **Acción:** golden que pinee la salida byte-a-byte de **cada** call-site migrado (los 31), no sólo `mint_code`.
- `pipeline/discover.py:91-93,96-104` `[VERIFIED]` `cdp_code(province_code=prov, ...)` sin `country_code` + `INSERT INTO entity (... province_code, municipality_code ...)` sin la columna `country_code` → añadir `SourceAdapter.country_code` enhebrado a `cdp_code(country_code=cc)` y la columna `country_code` al INSERT (default `'ES'`). (OI-4)

**Migración:** ninguna de esquema (la columna `entity.country_code` existe `[VERIFIED 0052]`); el write-site solo deja de omitirla.

**Golden cross-country** (extiende `test_country_golden.py` + `test_country_coexistence.py`):
- **G1:** `_CDP_CODE_RE.match("CDP-DE-28-FPB3W1R6")` → el `xfail(strict)` `[VERIFIED:286-291]` se vuelve **XPASS**; quitar el `pytest.xfail`. Y `match` de todo código ES vivo sigue verdadero (byte-identidad del validador).
- **Mints:** un platform connector con `campaign.country_code='DE'` minta `CDP-DE-…`, **nunca** `CDP-ES-`; con default ES, mint byte-idéntico `[VERIFIED test_country_coexistence.py:156-166]`.
- **Write-site:** `discover._upsert` de una entity DE escribe `country_code='DE'` y `cdp_code` `CDP-DE-…`.

**Gate de aceptación:** dry-run:5434 (descubrir una entity DE → `CDP-DE-`, pasa G1) → golden (`test_country_golden` xfail→XPASS + coexistence verde) → Ferrari (todo `CDP-ES-` vivo pasa G1 byte-a-byte; mint ES idéntico) → CI.

**Rollback:** revertir el diff; sin migración. El regex viejo y los literales `CDP-ES-` se restauran 1:1. **Importante:** este PR **no** re-mintea nada existente — solo cambia el camino de **futuros** mints; por eso es reversible en código aunque el efecto (un `cdp_code` ya acuñado) sea inmutable.

**PENDING-OWNER + AVISO DE INMUTABILIDAD** ([`SPINE §8.3`](SPINE-COUNTRY-THREADING.md), open item): el widen `[0-9A-Z]{2}` cubre Córcega `2A/2B` pero **NO** DOM FR `971-976` (3 dígitos) ni ISTAT IT >99. **Congelar ancho+alfabeto+centinela del `cdp_code` ANTES de mintear/sellar** un país es obligatorio e irreversible: un país onboardeado con gramática equivocada exige re-mintear códigos inmutables. Falta un **gate de congelación de gramática** explícito en el onboarding del país #2 → **PENDING-OWNER** (decisión de ancho de gramática, no un swap de regex).

---

## 11.5 · PR-8 + PR-9 — capas de fusión omitidas (Ola 2.5)

> La re-verificación adversarial encontró DOS capas de fusión transfronteriza que la enumeración previa del tren no tocaba: el resolver **β** (`resolve_entities.py`, fábrica de cross-merge a una compuerta de activación) y la **Layer-2 servida** (`canonical_dedup` por `deep_link`, ya leída por `v_dealer_resolved`) junto a `cross_source_dedup`. Ambas entran al tren irreversible (§2).

### 11.5.1 · PR-8 · β resolver (`resolve_entities.py`) — cerrar ANTES de gatear `IRREVERSIBLE-adjacent`

`tier T1-adj` · **IRREVERSIBLE** (cerrar-antes-de-gatear) · break Ola 2.5 (lente train-completeness) · depende de **PR-0, PR-2**

**Scope (1 frase):** scopear por `country_code` el fingerprint-merge, el city-guard y el phone-match de `resolve_entities.py` (β) — que hoy funde P-entities **cross-province (y por tanto cross-country)** con `Jaccard>=0.30` sin país — **antes** de que el owner pueda gatear/servir esa capa, porque [`stages/04-identity.md`] exige «cerrar ANTES de gatear» y β consume los cross-merge de Signal A (PR-2).

**Archivos (`[VERIFIED]`, `grep -c country_code resolve_entities.py = 0`):**
- `resolve_entities.py:388-418` `[VERIFIED]` `_load_p_entities` → añadir `e.country_code` a la proyección (`:397,:411`) y al dict de entidad.
- `resolve_entities.py:690-691` + `:753-768` `[VERIFIED — "Fingerprint dominates: accept regardless of province", signals=["fingerprint"]]` → añadir guard de país: un par con `country_code` distinto **NUNCA** se funde, ni por fingerprint Jaccard, ni por phone, ni por website. Es el equivalente del `cross_province`-block existente `[VERIFIED :707-712]` pero por país y **sin excepción de fingerprint**.
- `resolve_entities.py:238-249` `[VERIFIED]` `_load_ine_municipalities` → `SELECT name FROM geo_municipality` `[VERIFIED :245]` gana `WHERE country_code = %(cc)s`: hoy el city-guard (SH8) mezcla nombres de municipio ES+DE y el único guard cross-locale **se misfire** tras sembrar geo DE (PR-4).
- `resolve_entities.py:135-146` `[VERIFIED]` `_normalize_phone` devuelve `digits[-9:]` (descarta el prefijo internacional) → una colisión de teléfono cross-country queda invisible; con el guard de país del fingerprint-merge arriba, el phone-match cross-country queda bloqueado de raíz (mismo `country_code` obligatorio para todo merge).
- `resolve_entities.py:89` `[VERIFIED]` `RUN_ID = "entity-resolution-fingerprint-v1"` → sufijo por país (espejo PR-1).

**Migración:** ninguna (la columna `entity.country_code` existe `[VERIFIED 0052]`).

**Golden cross-country** (`TestIsolationBeta`):
- **Fixture:** un dealer ES y uno DE que comparten `>=30 %` de `canonical_vehicle_ulid` (alcanzable vía un cross-merge Signal A de PR-2); y un par cuyo `_normalize_phone` last-9 coincide pero el país difiere.
- **Asserts:** (a) β **no** los funde (distinta componente) por **ningún** signal; (b) el city-guard cargado con `country='ES'` no resuelve nombres de municipio DE; (c) ES byte-idéntico: las componentes β de ES no cambian.

**Gate de aceptación:** dry-run:5434 (fixture → `resolve_entities` → 0 merge cross-país) → golden (`TestIsolationBeta` verde) → Ferrari (β ES idéntico: mismas componentes/`resolved`) → CI.

**Rollback:** revertir el diff; sin migración. β legacy ES se regenera idéntico.

**PENDING-OWNER:** β **NO está servido hoy** `[VERIFIED: 0 refs a resolve_entities/entity_resolution/resolved_dealer en services/]`. Este PR NO toca serving; es la **precondición** para que el owner pueda gatear β sin abrir una fábrica de cross-merge transfronterizo. Si β se activa/sirve, su recompute productivo → gate ESCRITURA-EN-PROD. **OPEN con causa:** mientras β siga sin servir, su golden es regresión-preventiva, no fix de algo servido — declarado, no maquillado.

### 11.5.2 · PR-9 · `canonical_dedup` (`deep_link`) + `cross_source_dedup` country-scope

`tier T2` · **IRREVERSIBLE** (`canonical_dedup` servida) + REVERSIBLE (`cross_source` gateado) · break Ola 2.5 · depende de **PR-0**

**Scope (1 frase):** scopear por `country_code` el agrupado por `deep_link` de `build_canonical_dedup.py` — que escribe `canonical_dedup`, **Layer-2 de la vista SERVIDA `v_dealer_resolved`** — y los edges `(value, muni)` de `cross_source_dedup.py` (gateado `vam_verified=FALSE`), para que un `deep_link` o un `(phone|web|name, muni)` compartido entre un canonical ES y uno DE **no** los funda en un super-canonical/cluster transfronterizo.

**Archivos (`[VERIFIED]`):**
- `scripts/build_canonical_dedup.py:169-208` `[VERIFIED]`: el load `deep_link → canonical` `[VERIFIED :173-194]` y el mapa `dl_to_canons` `[VERIFIED :196-199]` no tienen dimensión país; `ANTI_HUB_K = 3` `[VERIFIED :88]`. Fix: resolver el `country_code` de cada canonical (JOIN a `entity` por su `cdp_code`) y **sólo unir canonicals del mismo país** — un `deep_link` que apunte a dos países se trata como hub y se excluye (o se particiona por país). Determinismo y `ANTI_HUB_K` intactos.
- `migrations/0028_dealer_resolved.sql:57-67` `[VERIFIED]`: `canonical_dedup` es la **Layer-2** que `v_dealer_resolved` aplica → el **guard dealer §4 ya cubre** este cross-merge **una vez las etiquetas de país difieran** (precondición PR-7 write-site). Ningún cambio de esquema; el fix vive en el build script.
- `pipeline/identity/cross_source_dedup.py:365` `[VERIFIED]` `_load_entities` → añadir `e.country_code`; `:447-457` `[VERIFIED]` el índice `by_muni` y las claves `phone_idx/web_idx[(value, muni)]` → `(country_code, value, muni)` (o exigir mismo país en `_build_cross_source_edges` `[VERIFIED :433]`). Escribe `entity_cluster` con `vam_verified=FALSE` `[VERIFIED :52-53]`.

**Migración:** ninguna de esquema (`canonical_dedup`/`entity_cluster` existen; el país llega vía `entity`).

**Golden cross-country** (`TestIsolationDealerDedup`):
- **Fixture:** dos canonicals (ES, DE) que comparten un `deep_link`; y un par cross-source `(phone|web|name, muni)` con país distinto.
- **Asserts:** (a) `build_canonical_dedup` **no** los une en un super-canonical; (b) `cross_source_dedup` no emite la arista cross-país; (c) guard dealer §4 (`v_dealer_resolved`) = 0 filas; (d) ES byte-idéntico: el dedup ES no cambia (`n_merged=2 385`, `40 016` deduped `[VERIFIED 0028:8-10,0027:23-28]`).

**Gate de aceptación:** dry-run:5434 (fixture → `build_canonical_dedup` + `cross_source_dedup` → 0 super-canonical/cluster cross-país) → golden (`TestIsolationDealerDedup` verde + guard dealer = 0) → Ferrari (dedup ES idéntico) → CI.

**Rollback:** revertir `build_canonical_dedup.py` + `cross_source_dedup.py`; `canonical_dedup` se reconstruye 1:1 para ES. Sin migración.

**PENDING-OWNER:** el **recompute productivo de `canonical_dedup`** toca la vista servida `v_dealer_resolved` → gate ESCRITURA-EN-PROD (firma owner). `cross_source_dedup` está **gateado** (`vam_verified=FALSE`) → su country-scope es **precondición para gatearlo**, no bloquea el serving actual. **OPEN con causa:** la probabilidad cross-país real de un `deep_link` compartido es baja (URLs por-listing raramente cruzan frontera), pero la ruta es country-blind y servida → se cierra igual.

---

## 12 · Follow-on (fuera del tren irreversible)

Reversibles/aditivos, fuera de la enumeración T0-T6 del mandato pero rastreados para no dejar hueco silencioso. Cada uno = fix + guard + golden, €0.

| ID | Scope | Archivos `[VERIFIED/W1]` | Tier | Reversibilidad |
|----|-------|--------------------------|------|----------------|
| **F1 · Moneda (M5)** | `price_currency` en el contrato `Vehicle`; leer `vehicle.currency` `[0003:14]` en todo gate de precio; bandas `PRICE_MAX`/`FAB_PRICE_CEIL` por moneda | `recipe_extract_web.py:79`, `price_sanity.py:49`, `cluster_vehicles.py:397` | T4-adj | REVERSIBLE |
| **F2 · Detectores por moneda (A2-A4)** | `FAB_PRICE_CEIL`/`COVERAGE_ANCHORS`/`price_trap` por país/moneda | `[VERIFIED pipeline/gestionador/detect.py:70]` `FAB_PRICE_CEIL=5_000_000`, `:78` `COVERAGE_ANCHORS`, `:786` `GROUP BY make, model, year` | T3 | REVERSIBLE |
| **F3 · Orquestación multipaís (O1-O5)** | lock por país, `_due_sources`/`silence` scopeados, `source_health +country_code`, resolver el zombie `:silence` | `scheduler.py:913`, `discover_schedule.py:50`, `silence_watchdog.py`, `0004:25` | T5 | REVERSIBLE (espejo `0052`) |
| **F4 · pHash (OI-8)** | `photo_hash` a INSERT/REFRESH + writer de backfill gateado por governor | `[VERIFIED OI-8 — 0 writers]` | indep | REVERSIBLE |
| **F5 · DSN de entorno (OI-11)** | `DSN = os.environ.get('CARDEEP_DSN', …)` para correr la cadena contra `:5434` | `build_particular_dedup.py:38`, `capture.py:17`, `migrate.py:15` | infra | REVERSIBLE |
| **F6 · Registry split (O4)** | extraer `REGISTRY` Python a `pipeline/ops/registry/<cc>.py`; `active_countries()==['ES']` byte-idéntico | `scheduler.py:150-325` | T5 | REVERSIBLE |
| **F7 · Ancho de columna (G5)** | `CHAR(2)/CHAR(5) → VARCHAR` (AGS DE 8 / ISTAT IT 6 / DOM FR 3 desbordan) | `0001:5,19`, `0002:13-14` **+ `0053:64-157`** | **T2-almacén** | **NO aditivo** (PK+FK surgery) `[VERIFIED]` |
| **F8 · Normalizador de mint no-latino (spine CRITICAL)** | `_normalize` NFKD+`ascii,ignore` destruye nombres no-latinos → `''` en el camino de mint inmutable | `[VERIFIED services/api/codes.py:30; canonical_key country-blind por diseño :35-38; name-key :67]` | identidad | **IRREVERSIBLE** (mint append-only); **OPEN** (eje intra-país) |
| **F9 · Capa de scrape ES-hardcoded (spine)** | egress sólo-ES + `Accept-Language: es-ES` → país #2 sale por IP ES con locale ES = quemado | `[VERIFIED pipeline/engine/free_proxies.py:27 (+:34,:39,:43); fingerprints.py:46,:65,:80]` | motor | REVERSIBLE |
| **F10 · Cadena `/stats` + quórum de sello country-blind (spine)** | writer single-row + reader + quórum registral ES-hardcoded | `[VERIFIED scripts/refresh_product_stats.py:30; services/api/routers/ops.py:88; pipeline/verify.py:48,:119]` | T5/sello | REVERSIBLE |

> **F7 ya NO es «aditivo» — corrección Ola 2.5 (lente additive-safety).** Ensanchar `CHAR→VARCHAR` toca columnas que `0053` `[VERIFIED]` promueve a **PRIMARY KEY compuesta `(country_code, code)`** (`:75 geo_province`, `:84 geo_municipality`) y que son destino de **6 FOREIGN KEY compuestas** (`:104,:114,:124,:134,:144,:154`). Alterar el tipo de una columna-PK referenciada por FKs **NO es aditivo**: PostgreSQL fuerza a **dropear cada FK dependiente y reconstruir la PK** — la misma cirugía FK-breaking, en una sola transacción, que `0053:47-49` documenta como su «mitad FK-breaking». La fila F7 original listaba sólo `0001/0002` y omitía `0053`: un ejecutor que confíe en la etiqueta «aditivo» choca con un error de dependencia dura o hace drops de FK a mano **sin** la danza ordenada «PK-primero, nunca-sin-guard» de `0053`, reabriendo una ventana de unicidad sin guard en el camino geo **irreversible**. No muta dato ES (los codes ES son full-width), pero la **clasificación de seguridad** era falsa. Sigue siendo bloqueante de **almacenamiento**, no de false-merge.
>
> **F8 es el residual más severo y honesto — OPEN con causa.** `codes.py:30 _normalize` (NFKD + `encode('ascii','ignore')`) colapsa todo nombre no-latino (EL/BG/RU/JP) a `''` → en el camino de mint inmutable (`canonical_key:67 name-key` → `cdp_pair` → `discover.py`) **todos** los dealers name-only de un municipio comparten `canonical_key` → **un solo `cdp_code`** acuñado para todos (append-only, IRREVERSIBLE). Es un over-merge **INTRA-país**, en un **eje distinto** al de este mandato (aislamiento cross-país): el guard `COUNT(DISTINCT country_code)=1` lo deja pasar (todas las filas serían del mismo país). **Gating honesto:** el piloto DE es **latino** → NO dispara F8; un país con alfabeto no-latino sí. Pertenece al invariante de **no-fabricación/normalización** (gramática), no al de país. Se rastrea aquí para no dejar hueco silencioso, pero **queda OPEN**: cerrarlo exige una decisión de transliteración/normalización por país (no un swap trivial) y NO bloquea el onboarding de un país latino. Declarado, no maquillado.
>
> **F9/F10 son reversibles y de capa motor/serving** (no corrompen identidad ni dato): el egress ES-only (`_COUNTRY='ES'`) y el `Accept-Language: es-ES` queman al país #2 (incoherencia IP/locale), y la cadena `/stats` (`product_stats` fila única `id=1` `[VERIFIED ops.py:88, refresh_product_stats.py:30]`) suma ES+país#2 en un agregado; el quórum de independencia del sello (`verify.py:48` familia registral `{registr,official,dgt,cnae,faconauto,borme,census}` ES-hardcoded → `has_independence` `:119`) sesga el TRUSTWORTHY del país #2. Se inyectan desde el pack del país / se parametrizan; ninguno es irreversible, pero **ninguno estaba en el tren ni en F1-F7 previos** — se rastrean para cerrar el hueco que la lente spine-completeness abrió.

---

## 13 · Criterio de cierre de toda la transformación

La transformación a genérico **no se declara hecha** hasta que:

1. **El tren irreversible** —ampliado por la Ola 2.5 a **{PR-1, PR-2, PR-4, PR-7, PR-8, PR-9}**— está merged y **LOS DOS guards de aislamiento** (`§4`, recompute SQL `COUNT(DISTINCT country_code)>1 = 0` sobre `v_dealer_resolved` **y** `v_canonical_vehicle`) están **verdes** — las 3 vías del blindaje ([`ANTI-DRIFT §"Cómo se PRUEBA"`](ANTI-DRIFT-HARDENING.md)): (a) golden verde en CI, (b) un inquisidor intenta el cross-merge a mano y el guard lo bloquea, (c) recompute SQL independiente = 0. El anti-FP de `cluster_vehicles` es **pre-write bloqueante** (no `print` post-write).
2. **El golden cross-country** ([`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md)) está verde en CI en cada push, **cubriendo los vectores que la Ola 2.5 destapó**: arista-1 **y** arista-4 fuzzy (dealer), **Signal A photo_url** **y** Signal B firma (vehículo), β fingerprint-merge, `canonical_dedup` por `deep_link` → la ceguera de país **no puede reaparecer** sin poner el build rojo. *(Un golden que sólo ejercite Signal B o la arista-1 deja vivos Signal A y la arista-4: cobertura insuficiente = criterio NO cumplido.)*
3. **El meta-test §4** "toda query servida lleva país" tiene la allow-list **vacía** (o cada excepción justificada), **incluyendo** `stats.py:_QUERIES`, el writer `refresh_product_stats.py` y el reader `product_stats` (`ops.py`) que el enumerador estrecho original omitía.
4. **Byte-identidad ES** pineada por `tests/test_country_golden.py` + Ferrari + CI en verde — ni un byte de ES de **identidad** (`cdp_code`/paths) movido. *(Honestidad Ola 2.5: este invariante NO cubre los agregados servidos; PR-3 cambia el conteo público `/stats` a propósito y disclosed — el guard de ese número es el meta-test §4 + el gate de prod, no la byte-identidad.)*
5. **Residuales OPEN declarados (no son blockers de un país latino, sí de su eje):** **F8** (`codes.py:30 _normalize` colapsa nombres no-latinos en el mint inmutable — eje **no-fabricación/normalización**, intra-país, el guard de país es ciego a él; gateado a un país de alfabeto no-latino) y **F9/F10** (capa de scrape/serving ES-hardcoded). Ninguno bloquea el onboarding DE; todos rastreados con causa+gating. Declarar «done» con un residual de eje-distinto **sin** nombrarlo sería maquillaje.

**Honestidad de ejecución (mandato, no maquillar):** el stack vivo está **CAÍDO** `[ASSUMED]`. Estos PRs están **especificados, con su fixture y su gate**, pero los goldens **se corren al reiniciar la DB** (secuencia owner: (1) golden ROJO prueba el merge; (2) aplico fix+guard; (3) golden VERDE + recompute=0; (4) las 3 vías). Hasta entonces: **spec + vector verificado de primera mano**, NO afirmación de funcional. La byte-identidad ES y las cifras de sello vivas se **re-validan contra DB viva** antes de declarar el sello del país #2.

---

> **Cómo encaja en el funnel:** [`README.md`](README.md) → [`00-MASTER.md`](00-MASTER.md) (constitución) → [`SPINE-COUNTRY-THREADING.md`](SPINE-COUNTRY-THREADING.md) (diagnóstico) → **este blueprint** (ejecución PR-por-PR) → [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md) (el guard que lo vuelve invariante) → [`COUNTRY-PACK-CONTRACT.md`](COUNTRY-PACK-CONTRACT.md) (lo que aporta el país #2). El blueprint es el **CÓMO ejecutar** el des-cegado que el SPINE diagnostica y el INVARIANT blinda.
