# Etapa 8 · Servir — Biblia (v2 PROFUNDO)

> Estado adversarial: **NEEDS_REWORK** (`holds=false`). El inquisidor probó que la tesis del diseño —"el servido ya es ~80% multi-país, el pack es trivial {country_code, admin1_label, display_name}"— es **FALSA** en las superficies geo/seal/stats/exhaustiveness: el motor está enhebrado en el ESQUEMA (0052/0053) y en el prefijo `cdp_code`, pero la **lógica de servido es country-BLIND**.
> Fuente: Wave 1 — cada hecho de código lleva `[VERIFIED path:línea]` leído de la fuente; toda corrección aún no construida se marca `propuesta [no implementada]`.
> Stack vivo CAÍDO: las cifras de DB citadas son **punto-en-el-tiempo** (censo vivo), nunca enteros absolutos.

Convención de blindaje en este capítulo:
- `[VERIFIED path:línea]` — leído en la fuente real, es un hecho del sistema HOY.
- `propuesta [no implementada]` — diseño de cierre que **aún no existe en código**; jamás se presenta como hecho.
- Una rotura del inquisidor NO se transcribe como resuelta: se integra con su resolución de diseño o se declara **OPEN ITEM** con causa y gate.
- **v2 PROFUNDO:** la sección **Sub-proyectos institucionales** atomiza la etapa en **31 facetas**, cada una un proyecto 360° (deep-spec `[VERIFIED]` + costura + fix `propuesta [no implementada]` + adversarial + sellado + herramienta €0). Es expansión, no sustitución: las secciones v1 se conservan.

---

## Misión

El servido es la **única boca** del censo sellado: una superficie HTTP read-only (FastAPI sobre asyncpg) que expone, tras `require_api_key`, el conjunto de puntos de venta y su inventario que las etapas 1–7 produjeron y certificaron. No descubre, no scrapea, no muta: **lee** vistas publish-gated y las envuelve en el contrato `{ok,data,error,meta}`.

El norte country-proof: **el país es una DIMENSIÓN de filtro, jamás una rama de código.** Un país nuevo no añade un binario ni un endpoint; añade filas bajo su `country_code` y una fila declarativa de registro. El motor de transporte (skeleton, envelope, auth, rate-limit, cache) es invariante byte-idéntico; lo que el inquisidor demolió es que la **capa de datos servida y los agregados** todavía no llevan esa dimensión, así que hoy un 2º país **sangra** en silencio.

---

## Lo que existe HOY (verificado)

**Maquinaria de transporte (genérica, sin lógica de país) — sólida:**
- App FastAPI con `lifespan` que crea el pool asyncpg `min_size=1,max_size=8` y un type-codec `jsonb/json` para que `vehicle_event.old_value/new_value` lleguen como objetos reales al envelope `[VERIFIED services/api/main.py:89-97,100-111]`.
- **18 endpoints GET** en 5 routers: `entities/*` (4), `platforms/*` (2), `vehicles/*` (2), `geo/*` (6), `ops/*` (4) `[VERIFIED grep @router.get services/api/routers = 18; main.py:146-150]`.
- Envelope uniforme `{ok,data,error,meta}` vía `ok()/err()` y paginación honesta `page_slice()` (over-fetch `size+1`, la última página exacta reporta `has_more=false`) `[VERIFIED services/api/deps.py:52-57,60-68]`.
- Auth `require_api_key`: público en dev (`CARDEEP_ENV` unset), **fail-closed 503** en prod sin clave, 401 en mismatch; aplicado por `Depends` en endpoints de datos, NO en `/health` `[VERIFIED services/api/deps.py:32-49]`.
- Cache in-memory `TTLCache` (60 s, maxsize 512), key `METHOD:PATH?sorted-qs`, sólo 2xx `ok=true`, prefijos `/geo//entities//platforms/`, excluye `/health//alerts//sources` `[VERIFIED services/api/cache.py:49-62,79-94,135-165]`.
- Rate-limit `slowapi memory://` (€0), 429 en el envelope del proyecto, middleware como capa más externa junto a CORS GET/OPTIONS `[VERIFIED services/api/main.py:125-127,135-144]`.
- `/stats` lee una sola fila precomputada de `product_stats` con fallback a `compute_counts` en `UndefinedTableError` `[VERIFIED services/api/routers/ops.py:74-98; services/api/stats.py:44-49]`.
- Fail-fast de arranque en prod: `require_prod_secrets((DSN),require_api_key=True)` rechaza DSN dev-default o clave ausente `[VERIFIED services/api/main.py:106]`.
- `resolve_cluster()` mapea cualquier `cdp_code` a su canónico vía `v_dealer_resolved` (COALESCE-a-sí-mismo) y devuelve la membresía completa `[VERIFIED services/api/deps.py:98-149]`.

**Sustrato country ya presente (esquema), pero NO conectado a la lógica de servido:**
- `mint_code()` es el único hogar del prefijo `CDP-{country_code}-{province}-…`, con `country_code` default `'ES'` ⇒ salida ES byte-idéntica `[VERIFIED services/api/codes.py:44-53]`. `canonical_key()` es **deliberadamente country-blind** (el país NO entra en la pre-imagen de dedup) `[VERIFIED services/api/codes.py:56-65]`.
- `country_code CHAR(2) NOT NULL DEFAULT 'ES'` en `entity` + backbone geo (0052) y PK geo promovido a compuesto `(country_code,code)` con los 6 FK reescritos compuestos (0053) `[VERIFIED migrations/0052_country.sql:51-54; 0053_country_onboarding.sql:75,93-157]`.
- `pg_trgm` + `btree_gin` instalados; índices GIN trigram sobre `entity.trade_name/legal_name` — el sustrato de un `/search` typo-tolerante existe `[VERIFIED migrations/0005_types_and_guards.sql:6-7]`.
- `v_servable_dealer` (0056) — la definición ÚNICA de "punto de venta" (active, kind NOT IN particular/desguace, garaje sólo con inventario) — **EXISTE como vista pero ningún router la referencia** `[VERIFIED migrations/0056_v_servable_dealer.sql:26-37; grep v_servable_dealer en services/api = 0]`.
- Harness de test serve-layer: HTTP (TestClient) cross-check contra SQL crudo asyncpg, con golden ES y coexistencia DE en txn revertida — pero la coexistencia ejercita SÓLO el esquema (PK/FK), no toca ningún endpoint HTTP con 2º país `[VERIFIED tests/test_country_coexistence.py:259-369]`.

**Partición de los 18 endpoints (la geografía de la rotura):**
| Familia | N | Dónde | Estado country |
|---|---|---|---|
| Keyed-by-identity (`cdp_code`/ULID) | 8 | `entities/*`(4) `platforms/*`(2) `vehicles/*`(2) | Correctos DENTRO de un país; **caveat** colisión cross-border (break #6) |
| Geo province-keyed (`/geo/{province_code}/…`) | 3 | `geo.py:229,292,352` | **Bleed garantizado** tras PK compuesto |
| Agregados nacionales (implícitamente ES) | 4 | `geo.py:32,92,147` + `ops.py:49` | **Suma ES+CC silenciosa** |
| Ops globales | 3 | `ops.py:27,105,160` | Sin dimensión país por contrato |

---

## Motor (invariante, reusado byte-idéntico por país)

Lo que un país nuevo reusa SIN tocar una línea (verificado country-neutro):

1. **El skeleton FastAPI completo:** `lifespan` + pool + codec jsonb/json + orden de middleware (rate-limit → CORS externo) + registro de routers `[VERIFIED main.py:89-150]`. La construcción de la app nunca es asunto de país.
2. **El envelope `{ok,data,error,meta}` y `ok()/err()/page_slice()`** `[VERIFIED deps.py:52-68]`. La forma del contrato es invariante; el país es un campo más dentro de `data/meta`.
3. **Auth, rate-limit y cache como mecanismo de transporte puro**, cero lógica de país `[VERIFIED deps.py:32-49; cache.py; ratelimit memory://]`. La cache key ya pliega los query params ordenados, así que un `?country=` se auto-particiona sin tocar `cache.py` — **siempre que el país entre por path/query** (ver break #7: hoy NINGÚN endpoint lo acepta, así que el auto-particionado es potencial, no real).
4. **El MECANISMO de precompute** `product_stats` + `compute_counts` `[VERIFIED stats.py:44-49]` — la misma maquinaria re-apuntada a una query country-scoped. **Caveat fuerte (break #4):** el mecanismo es reusable, pero el ESQUEMA actual (`PK CHECK(id=1)`, una fila global) NO puede almacenar conteos por país; el diseño que afirmaba "sólo re-apuntar la query" es FALSO sin cambio de PK.
5. **Las FORMAS de query SQL de cada handler** (DISTINCT ON canónico, fan-out `ANY($1::text[])`, COALESCE-a-sí-mismo, alerts por severidad). Sólo su `WHERE`/scope gana un predicado país; la forma es idéntica.
6. **El gate prod fail-fast** y la postura de seguridad (auth env-gated, señal de cobertura tras auth, `/health` liveness sin auth) `[VERIFIED main.py:106; deps.py:42-46; ops.py:27-46]` — idénticos para todo país.
7. **`resolve_cluster()`** keyed sobre `cdp_code/entity_ulid` `[VERIFIED deps.py:98-149]`. **Caveat (break #6):** es country-correct sólo si el clustering upstream no fusionó miembros de varios países bajo un `canonical_key` desnudo.
8. **El PATRÓN de definición única de punto-de-venta:** UNA vista (`v_servable_dealer`) es el censo; stats/geo/seal la leen. El patrón es invariante; sólo difieren sus filas por país. **Caveat:** hoy la vista NO está cableada (3 superficies, 3 scopes) y NO proyecta país.

> Honestidad: los puntos 1–3 y 6 son invariantes **limpios y verificados**. Los puntos 4, 7 y 8 son invariantes **de patrón** cuyo cierre multi-país exige los fixes de la sección de veredicto; presentarlos como "ya genéricos" sería transcribir un diseño roto.

---

## Pack por país (lo que cada país aporta para esta etapa)

El diseño original listaba sólo `{country_code, admin1_label, display_name}`. El inquisidor probó que ese pack **omite el ítem más pesado de toda la etapa** y trata la geo como un único nivel cuando es un árbol de profundidad variable. El pack REAL del servido:

| # | Aporte del país | Por qué (verificado) | Naturaleza |
|---|---|---|---|
| 1 | `country_code` ISO-3166 alpha-2 (`'DE'`) + fila de `country_registry {country_code, display_name}` | Único eje nuevo; todo lo demás son datos que geo/extracción ya produjeron | Declarativo |
| 2 | **Fuente + loader del DENOMINADOR del sello**, por segmento: equivalente a DIRCE CNAE-451 (venta) y al censo DGT-CAT (desguace), con su `source_key` | Sin él `/geo/seal` es `NO_DENOM` permanente `[VERIFIED 0042:42; 0043:31,62]` | **Pesado** (dato + ToS/legal) |
| 3 | **Mapa de profundidad administrativa**: ¿el país tiene tier "comarca"? ¿cuántos niveles país→provincia→…→ciudad?, y qué tier nativo mapea a cada columna | El árbol y completeness son estructuralmente 4-tier ES y exigen `comarca_id IS NOT NULL` `[VERIFIED geo.py:388-390]` | Estructural |
| 4 | Etiqueta `admin_level_1` (Bundesland/Région/…) — sustituye el literal ES `ccaa_*` | Hoy `ccaa_code/ccaa_name` son literales de contrato `[VERIFIED geo.py:370,419-420]` | Declarativo |
| 5 | **Mapeo de tipos nativos de dealer → enum compartido `entity_kind`** | El árbol fija literales ES (`compraventa/concesionario_oficial/desguace/…`) en SQL y JSON `[VERIFIED geo.py:378-386; enum en 0005:13-17]` | Tabla de mapeo |
| 6 | **Validador de tax-id del país** alimentando la rama `cif:` de `canonical_key` | `tax_id.py` es sólo NIF/NIE/CIF español `[VERIFIED services/api/tax_id.py:1-93]` | Código (1 módulo) |
| 7 | Confirmación de que existen filas geo+entity bajo `CC` (precondición, no producción) | El servido sólo lee | Aserción |

La moneda **NO** se aporta: ya es per-vehicle en el contrato, heredada de extracción (design-cited `entities.py:132`). La decisión de **cómo entra el país en la request** (path `/{cc}/…` vs query vs header) es un cambio de **motor de una sola vez**, no un aporte por país (ver break #7).

---

## Costuras ES-hardcoded → fix

> Todos los `fix` son **propuesta [no implementada]**: describen el cierre de diseño, no código existente.

| Location (verificado) | Issue | Fix (propuesta) |
|---|---|---|
| `migrations/0046_servable_entity_status_filter.sql:17-29` | `servable_entity` NO proyecta `country_code` aunque `entity` lo lleva desde 0052. Todo router geo lee esta vista ⇒ no puede filtrar país. **Primera ficha del dominó.** | `CREATE OR REPLACE VIEW servable_entity` añadiendo `country_code` (aditivo 38 cols, idempotente, rollback = restaurar 37 cols como el bloque de 0046). |
| `services/api/routers/geo.py:229,292,352` (`/geo/{province_code}/…`) | Keyed sobre `province_code` desnudo. Tras 0053 el PK es `(country_code,code)` ⇒ `'28'` = (ES,28)∪(DE,28). No es "ambiguo": es **bleed garantizado**. | Prefijo `/{country_code}/geo/{province_code}/…` (o query `?country=` default `'ES'`). `AND country_code=$cc` en `entities_by_province`/`entities_by_municipality`/`province_inventory_tree` y en el lookup `geo_province` `[VERIFIED geo.py:369-371]`. Default `'ES'` preserva toda URL ES byte-idéntica. |
| `services/api/routers/geo.py:32,92,147` + `ops.py:49` | Los 4 agregados nacionales suman TODAS las filas sin predicado país. Hoy todo es ES; al entrar un 2º país reportan ES+CC fusionado — **regresión de corrección, no cosmética**. | Parametrizar cada agregado por `country_code` (default `'ES'`): `AND e.country_code=$cc`/`WHERE g.country_code=$cc` en `stats.py` y en completeness/seal/exhaustiveness; `product_stats` keyed por país; exponer `country` en `meta`. |
| `services/api/routers/geo.py:370,419-420` | El árbol fija el concepto ES `CCAA` como nivel estructural y nombre de campo. DE/FR no tienen CCAA. | Renombrar el nivel a `admin_level_1 {code,label}` desde `country_registry`; ES sigue emitiendo el valor `ccaa_*` bajo la clave genérica (el dato no cambia, el nombre del nivel deja de ser ES). |
| `services/api/routers/geo.py:378-390` | El árbol exige `comarca_id IS NOT NULL` y hace JOIN `geo_comarca`; `geo_comarca` no tiene columna `code` (PK=`id`, UNIQUE `(province_code,name)`) y es división **sólo española** `[VERIFIED 0052:39-41]`. Países sin comarca → árbol VACÍO. | Generalizar el árbol a **profundidad variable**: el nivel intermedio es opcional, declarado en el pack (#3). Para país sin comarca, JOIN directo provincia→municipio sin el `IS NOT NULL`. |
| `services/api` (toda la superficie) | NO existe `/search` pese a GIN trgm instalado `[VERIFIED grep 'search' en services/api = 0 endpoints]`. | `GET /{country_code}/search?q=` sobre `servable_entity` (tras añadir `country_code`): `WHERE country_code=$cc AND (trade_name % $q OR legal_name % $q) ORDER BY similarity(...) DESC`. **Nace country-scoped** o es la próxima costura. |
| `services/api/codes.py:24` `DEFAULT_COUNTRY='ES'` | Default tenant horneado. Correcto para byte-identidad HOY, pero cualquier ruta que maneje un código sin threadear país asume ES en silencio. | Conservar el default como ancla del golden; exigir que todo call-site multi-país pase `country_code` explícito desde la dimensión de la request. |
| `services/api/cache.py:79-94` | `_cache_key` sin dimensión tenant/país (auto-anotado en :82-85). | Seguro bajo una sola API key; al introducir país por default-de-servidor o keys por tenant, **incluir el país efectivo en la key** o un país recibe el cuerpo cacheado de otro. |
| `services/api/tax_id.py:1-93` | `is_valid_cif` sólo valida NIF/NIE/CIF ES; un VAT DE/FR/MX cae a keying `name+muni`, degradando la identidad del país nuevo. | Registrar un validador de tax-id por país (pack #6) que alimente la rama `cif:` de `canonical_key`. |

---

## Diseño genérico A→Z (la abstracción country-proof)

**Tesis corregida.** El servido NO es greenfield, pero tampoco el "~80% hecho" que el diseño afirmó: 8 de 18 endpoints son key-safe DENTRO de un país, y el resto (7 geo/agregados + `/search` ausente) está **country-blind por construcción**. El trabajo genérico es real y se concentra ahí.

**1 · El eje único.** Se introduce UNA dimensión, `country_code` (ISO-2), que entra a la request por una de dos vías equivalentes:
- (a) **implícita** en el `cdp_code`/ULID → el endpoint keyed ya es correcto dentro del país;
- (b) **explícita** para geo/agregados, vía **segmento de path `/{country_code}/…`** (recomendado: inequívoco, cacheable, RESTful) con default `'ES'` para retrocompat.

> Decisión pendiente y bloqueante (missing_pack #6): hoy **ningún** endpoint acepta país por ninguna vía `[VERIFIED grep country/X-Country/tenant en routers = 0 params]`. El path-segment es la propuesta; hasta tomarla, el predicado SQL y la cache key no tienen de dónde leer el país.

**2 · Capa de datos (la costura raíz).** El único cambio estructural es exponer en las vistas servidas la dimensión que la tabla base ya tiene:
- `servable_entity += country_code` (aditivo sobre 0046, zero-risk: una vista es una query guardada; rollback = restaurar 37 cols).
- `v_servable_dealer` hereda `country_code` de la `servable_entity` ampliada y se **CABLEA** como definición única en stats/geo/seal (hoy 3 scopes divergentes `[VERIFIED 0056:1-10]`).
- `servable_vehicle` NO lo necesita: país derivable por `entity_ulid→entity.country_code` `[VERIFIED 0052:37 nota d]`.

**3 · Interfaz de endpoints. Dos familias:**
- **Keyed-by-identity:** contrato sin cambios; el país viaja en la clave. Se AÑADE `country_code` aditivo al objeto de salida para consumidores pan-EU.
- **Keyed-by-geo y agregados:** se parametrizan por `country_code` (`WHERE … AND country_code=$cc`), con el árbol generalizado a **profundidad variable** (no un único `admin1_label`).

**4 · Estructura del contrato.** El envelope es invariante; `meta` gana `country_code` en respuestas con dimensión país. El árbol generaliza el nivel ES `ccaa` a `admin_level_1 {code,label}` desde `country_registry`. ES sigue emitiendo los mismos valores bajo la clave genérica.

**5 · `product_stats` por país.** De `PK SMALLINT CHECK(id=1)` (una fila global, **físicamente incapaz** de guardar conteos por país `[VERIFIED 0055:14-22]`) a `PK (country_code)` (o fila por país). `/stats?country=DE` lee su propia fila precomputada con `computed_at`.

**6 · Sello y exhaustividad por país.** `v_province_seal` agrupa hoy SÓLO por `province_code` `[VERIFIED 0042:18-44; 0043:16-66]` ⇒ debe agrupar por `(country_code, province_code)`. `v_exhaustiveness_seal` sirve sólo el `build_run_id` más reciente GLOBAL `[VERIFIED 0048:82-88]` ⇒ debe ser **latest-build POR PAÍS** (particionar por país antes del `LIMIT 1`).

**7 · `/search` (la mayor palanca, nacido genérico).** `GET /{country_code}/search?q=&page=&size=` sobre `servable_entity`, índices GIN trgm ya instalados, `similarity` threshold como constante de módulo (no mágico), paginado con `page_slice`, rate-limited `RATE_EXPENSIVE`, cacheado. `btree_gin` (ya instalado `[VERIFIED 0005:7]`) habilita en onboarding un índice compuesto `(country_code, trade_name gin_trgm_ops)` para escala.

**8 · Seguridad.** La PII (phone/email/address/lat/lon) ya está tras `require_api_key` salvo `/health`. La misma puerta protege todos los países. Añadido multi-país recomendable: la cache key incorpora el país efectivo cuando proviene de un default de servidor. TLS NO lo termina la app (uvicorn loopback) → reverse-proxy €0 en el borde (gate de infra, no de código).

**9 · Invariancia €0.** Todo es código + vistas aditivas + (opcional) un índice compuesto. Cero infra nueva, cero servicio pago, cero IA. El binario de la API es idéntico entre países; difieren las **filas** y una fila de `country_registry`.

**10 · Por qué no se reescribe ES.** Cada cambio es aditivo y default-`'ES'`: la proyección del view crece (no muta), el predicado país lleva default `'ES'`, el nivel admin1 conserva el valor `ccaa`, `/search` es nuevo. El golden de byte-identidad (coexistence) es el cinturón que hace fallar cualquier deriva ES.

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)

0. **PREREQUISITO (otras etapas):** `CC` ya tiene backbone geo (province/municipality con `country_code=CC`) y ≥1 entidad `CDP-CC-…`. Verificar: `SELECT count(*) FROM entity WHERE country_code='CC' > 0`. El servido sólo lee.
1. **Registrar la fila declarativa** en `country_registry`: `{country_code, admin1_label, display_name}` + la **profundidad administrativa** (¿hay tier comarca?) + el **mapeo de tipos nativos → `entity_kind`**.
2. **Cargar el DENOMINADOR del sello** de `CC` (equivalente DIRCE para venta, censo para desguace) en `denominator_estimate` con su `source_key`. **Sin esto el país no puede certificarse** (gate legal/ToS — PENDING-OWNER).
3. **Asegurar cambios de motor hechos UNA vez** (no por país): `servable_entity` y `v_servable_dealer` proyectan `country_code`; `product_stats` con PK por país; `v_province_seal` agrupa por `(country_code,province_code)`; `v_exhaustiveness_seal` latest-por-país.
4. **NO tocar los 8 endpoints keyed-by-identity.** Verificar con un `cdp_code CDP-CC-real`: `GET /entities/{cdp}/inventory` devuelve sólo stock de `CC`. (Vigilar break #6: que el clustering upstream no haya fusionado miembros cross-border.)
5. **Confirmar que el país llega** a los 7 endpoints con dimensión país (path `/{cc}/geo/…`). El default `'ES'` NO debe usarse para `CC`.
6. **Registrar el validador de tax-id** de `CC` que alimenta la rama `cif:` de `canonical_key`.
7. **Precomputar `product_stats` para `CC`**; verificar `GET /stats?country=CC` devuelve su fila con `computed_at`.
8. **Verificar `/search?country=CC&q=<nombre real>`**: typo-tolerante, sólo entidades `CC`, ordenado por `similarity`. Si lento, índice compuesto (opcional, sólo a escala).
9. **Correr la suite serve country-scoped** (ver sellado): golden ES byte-idéntico + no-bleed + disjunción + aislamiento de cache.
10. **Smoke HTTP:** `GET /health` (200 sin auth), `GET /stats?country=CC` (con `X-API-Key`), comparar el conteo contra SQL directo independiente. Sellar sólo si coinciden.
11. **Documentar** en `country_registry`/CHANGELOG la fecha de alta y los conteos sellados de `CC` (cota inferior + freshness), **nunca un entero absoluto**.

---

## Sellado + verificación multi-vía + rollback

**Qué significa SELLADO en servido (intervalo, no entero):**
1. **ES byte-idéntico:** con default `'ES'` cada uno de los 18 endpoints devuelve forma+contenido idénticos al baseline pre-país. El golden + coexistence unit hacen fallar cualquier deriva de `cdp_code/canonical_key/paths` `[VERIFIED tests/test_country_coexistence.py:105-204]`.
2. **Aislamiento país (no-bleed):** una request de país X jamás devuelve filas de Y. Estructural para los 8 keyed (CDP-X/ULID); probado por predicado para los 7 con dimensión país.
3. **Disjunción:** el conjunto de `cdp_code` servidos para `/geo/X/…` y `/geo/ES/…` es disjunto cuando ambos existen (province `'28'` compartido resuelve a entidades distintas).
4. **`/search` country-scoped:** typo-tolerante y confinado al país.
5. **Auth/rate-limit/cache intactos:** PII sólo tras `require_api_key`; la cache no sirve cuerpo de un país a otro.

**Requisitos de sellado AÑADIDOS por el inquisidor (sealing_holes — hoy ausentes):**
- **Golden multi-país de la CAPA DE SERVIR** (no sólo del esquema): tests HTTP-vs-SQL contra `/geo/seal`, `/geo/{prov}/entities`, `/geo/{prov}/tree`, `/stats`, `/geo/exhaustiveness` con una DB sembrada con un 2º país, asertando que sólo retornan filas de ESE país.
- **Test de aislamiento de cache cross-country** (DE-28 nunca recibe el cuerpo cacheado de ES-28).
- **Precondición "denominador presente"** antes de sellar: un `NO_DENOM` `[VERIFIED 0042:37; 0043:62]` debe leerse como "no certificable", no como "pendiente".
- **Exhaustividad por país durable** (no latest-build-global): el build de `CC` no puede borrar el certificado de ES.
- **Criterio de rollback de la capa de servir** (cache flush + recompute `product_stats`).
- **Intervalo monótono/estable por país** (la cota inferior servida no cambia cuando otro país hace build).

**Verificación por 2ª vía ortogonal** (patrón canónico del repo, `[VERIFIED tests/test_api_gaps.py:50-61]` HTTP-vs-SQL):
- (a) **cota por conteo:** `GET /stats?country=CC.dealers` == `SELECT count(DISTINCT resolved_cdp_code) FROM v_servable_dealer WHERE country_code='CC' AND has_inventory`, ejecutada por separado;
- (b) **no-deriva ES por txn reversible:** sembrar filas `CC` en una txn y `rollback`, asertando que los conteos ES no cambian — exactamente el método ya probado con DE byte-idéntico y revertido `[VERIFIED tests/test_country_coexistence.py:309-369]`;
- (c) **invariante de txn revertida** que no depende de ningún conteo.

**Rollback** (el servido es código stateless + vistas aditivas; cero datos mutados):
- Routers: `git revert` (vuelven a la forma ES-implícita).
- Vistas `servable_entity`/`v_servable_dealer`: `CREATE OR REPLACE VIEW` restaura la proyección previa (bloque Rollback en 0046/0056), sin tocar filas.
- `product_stats` por país: restaurar single-row (rollback de 0055) **y recomputar** (la fila global queda doble-contada hasta el refresh).
- Cache: se vacía al reiniciar el proceso (in-memory).
- Filas `CC` sembradas: `DELETE WHERE country_code<>'ES'` (precondición del rollback de 0053). Todo reversible en local; sólo el push es PENDING-OWNER.

---

## Veredicto adversarial: roturas → resolución

> El inquisidor declaró `NEEDS_REWORK`. NINGUNA rotura se oculta. Cada break/missing_pack/sealing_hole lleva su resolución de diseño (cómo se cierra) o un **OPEN ITEM** con causa y gate. Las resoluciones son **propuesta [no implementada]** salvo donde se indique código existente.

### Breaks (8)

**B1 · DE — `/geo/{province}/tree` VACÍO para todo país sin comarca [CRITICAL].**
Verificado: la query exige `e.comarca_id IS NOT NULL` y hace JOIN `geo_comarca` `[VERIFIED geo.py:388-390]`; `geo_comarca` es división sólo-ES sin columna `code` `[VERIFIED 0052:39-41]`; el fixture DE siembra la muni con `comarca_id=NULL` `[VERIFIED test_country_coexistence.py:276-278]` ⇒ todo dealer alemán cae fuera del `HAVING count>0`.
**Resolución:** generalizar el árbol a **profundidad administrativa variable** declarada en el pack (#3): el tier intermedio es opcional. Para país sin comarca, JOIN directo provincia→municipio y eliminar el `comarca_id IS NOT NULL`. El diseño que redujo la geo a un único `admin1_label` ignoró la PROFUNDIDAD; esta es la corrección de fondo. **Cierra DE/FR/IT/PT** (cualquier país define su número de niveles).

**B2 · FR — `/geo/{province_code}/entities|tree|municipalities` mezclan países [CRITICAL].**
Verificado: `WHERE se.province_code=$1` sin país `[VERIFIED geo.py:268,323]`; lookup `SELECT … FROM geo_province WHERE code=$1` por `fetchrow` SIN `ORDER BY` `[VERIFIED geo.py:369-371]`; PK compuesto `(country_code,code)` `[VERIFIED 0053:75]` ⇒ el departement FR `'28'` coexiste con ES `'28'` y `fetchrow` devuelve una provincia de país arbitrario.
**Resolución:** path `/{country_code}/geo/{province_code}/…` + `AND country_code=$cc` en los 3 endpoints y en el lookup. El diseño lo llamó "ambiguo" pero con PK compuesto es **bleed garantizado**, no ambigüedad. Default `'ES'` preserva ES. **Cierra FR/IT/PT/MX/global.**

**B3 · IT — `/geo/seal` colisiona provincias entre países [CRITICAL].**
Verificado: `v_province_seal` agrupa SÓLO por `province_code` (venta y desguace) `[VERIFIED 0042:18-44; 0043:16-66]`; el endpoint suma en una fila `[VERIFIED geo.py:112-136]` ⇒ dealers IT y ES con el mismo código de provincia se funden y el `coverage_pct` nacional es una mezcla sin sentido.
**Resolución:** `v_province_seal` agrupa por `(country_code, province_code)` y el `denominator_estimate` se une por país; el endpoint filtra `WHERE country_code=$cc`. **Cierra todos.** Depende de B-pack #2 (denominador por país).

**B4 · PT — `/stats` reporta suma multi-país sin sentido [CRITICAL].**
Verificado: las 5 queries no filtran país `[VERIFIED stats.py:14-39]` y `product_stats` es UNA fila global `PK CHECK(id=1)` `[VERIFIED 0055:14-22]`, **físicamente incapaz** de guardar conteos por país.
**Resolución:** `product_stats` → `PK (country_code)` (o fila por país), eliminar `CHECK(id=1)`; `compute_counts` gana `WHERE country_code=$cc`. **Refuta explícitamente** el `engine_invariant` que afirmaba "re-apuntar la query sirve a cualquier país": FALSO sin cambio de esquema. La resolución lo corrige.

**B5 · MX (no-UE) — `/geo/exhaustiveness` borra el certificado ES y `/geo/seal` queda sin denominador [CRITICAL].**
Verificado: `v_exhaustiveness_seal` sirve sólo el `build_run_id` más reciente GLOBAL (`ORDER BY created_at DESC LIMIT 1`) `[VERIFIED 0048:82-88]` ⇒ el build de MX vuelve "latest" y el certificado ES desaparece de la vista. Además el denominador (DIRCE venta `[VERIFIED 0042:42]`, censo `dgt_cat` desguace `[VERIFIED 0043:31]`) no tiene equivalente MX cableado.
**Resolución (2 partes):**
- Exhaustividad: `v_exhaustiveness_seal` particiona por país antes del `LIMIT 1` (latest-build POR PAÍS) — cierra el borrado.
- Denominador MX: **OPEN ITEM — gate LEGAL/ToS + GASTO (PENDING-OWNER).** El servido no puede fabricarlo; depende de que la etapa 7 + inteligencia de país encuentren una fuente MX (no-UE, sin DIRCE/DGT). Hasta entonces `/geo/seal` de MX es legítimamente `NO_DENOM`, lo cual el diseño de sellado debe mostrar como "no certificable", no como bug.

**B6 · Japón/global (no-UE) — los 8 endpoints "country-correct BY CONSTRUCTION" NO lo son bajo colisión de identidad cross-border [HIGH].**
Verificado: `canonical_key` es country-blind `[VERIFIED codes.py:56-65]`; un dominio desnudo colapsa a `domain:{host}` `[VERIFIED codes.py:76-87]`; el test asegura que ES y DE `domain:ford.es` son IDÉNTICOS `[VERIFIED test_country_coexistence.py:133-136 — design-cited]`. Si el clustering upstream dedup por `canonical_key`, `resolve_cluster` `[VERIFIED deps.py:131-138]` devuelve un cluster con miembros de varios países.
**Resolución:** dos capas.
- **En servido (cierra el síntoma):** `resolve_cluster` y el fan-out de los 8 endpoints filtran los miembros por el `country_code` del canónico solicitado, de modo que la respuesta nunca incluye miembros cross-border aunque el cluster los tenga.
- **En raíz (etapa 4 — Identidad):** decidir si `canonical_key` debe threadear país. **OPEN ITEM cross-stage:** es una decisión de la etapa de Identidad, no del servido; el servido la **defiende** pero no la **resuelve**. Causa: cambiar `canonical_key` re-keya entidades (rompe el golden) — debe litigarse en 04-identity con su propia coexistence.

**B7 · DE — bleed de cache cross-country [HIGH].**
Verificado: `_cache_key` es `METHOD:PATH?sorted-qs` SIN dimensión tenant/país (auto-anotado) `[VERIFIED cache.py:79-94]` y NINGÚN router acepta parámetro/header de país `[VERIFIED grep = 0 params]`. El diseño afirmó "`?country=` se auto-particiona", pero **ese parámetro no existe** y el diseño nunca definió DÓNDE entra el país.
**Resolución:** **tomar primero la decisión de missing_pack #6** (país por path-segment `/{cc}/…`). Con el país en el path, la cache key lo pliega automáticamente y el bleed desaparece sin tocar `cache.py`. Si en cambio el país llega por header/tenant, `_cache_key` DEBE incorporarlo explícitamente. **Bloqueado por** la decisión de entrada de país (ver missing_pack #6).

**B8 · DE — `/geo/completeness` reporta 0% y mezcla el grid geo entre países [HIGH].**
Verificado: cuenta "full" sólo con `comarca_id IS NOT NULL` `[VERIFIED geo.py:51-67]` y reporta conteos `geo_comarca/geo_municipality` sin filtro de país `[VERIFIED geo.py:68-74]`.
**Resolución:** mismo fix de profundidad que B1 (comarca opcional) + `WHERE country_code=$cc` en los 7 COUNT. Un país sin comarca reporta su cobertura real, no 0%, y el grid se cuenta por país.

### Missing pack (8)

| # | Falta (verificado) | Resolución / gate |
|---|---|---|
| MP1 | **Fuente+loader del denominador del sello** por país (DIRCE-451 venta, DGT-CAT desguace) `[VERIFIED 0042:42; 0043:31]` — el ítem más pesado, omitido por el diseño | Pack #2. **OPEN ITEM por país** (gate LEGAL/ToS + posible GASTO, PENDING-OWNER): sin él ningún país se certifica. |
| MP2 | **Mapa completo de niveles administrativos** (profundidad), no un único `admin1_label`; el árbol es 4-tier ES `[VERIFIED geo.py:359,388-390]` | Pack #3 + resolución B1. Declarativo. |
| MP3 | `servable_entity` debe proyectar `country_code` `[VERIFIED 0046:17-29]` | Cambio de motor UNA vez; vista aditiva. **Primera ficha del dominó.** |
| MP4 | `product_stats` por país (PK `country_code`, quitar `CHECK(id=1)`) `[VERIFIED 0055:14-22]` | Resolución B4. Refuta "el binario API es idéntico para servir". |
| MP5 | **Mapeo tipos nativos → `entity_kind`** `[VERIFIED geo.py:378-386; enum 0005:13-17]` | Pack #5. Tabla de mapeo por país. |
| MP6 | **DECISIÓN de cómo entra el país** en la request (path/query/header/tenant) — ningún endpoint lo acepta `[VERIFIED grep=0]` | Propuesta: **path-segment `/{cc}/…`**. Bloquea B2/B7 y el predicado SQL. Decisión de arquitectura — tomarla es prerequisito de todo lo demás. |
| MP7 | `source_key` del censo desguace ES-only (`dgt_cat`) `[VERIFIED 0043:31]` | Parte de MP1; cada país declara su `source_key` de desguace. |
| MP8 | Validador de tax-id por país `[VERIFIED tax_id.py:1-93]` alimentando rama `cif:` | Pack #6. Un módulo por país; degrada identidad si falta. Cruza con B6/etapa 4. |

### Sealing holes (6)

| # | Hueco (verificado) | Resolución |
|---|---|---|
| SH1 | **No hay golden multi-país de la capa de servir**; el coexistence sólo ejercita el esquema en txn revertida `[VERIFIED test_country_coexistence.py:259-369]` | Añadir tests HTTP-vs-SQL country-scoped sobre seal/entities/tree/stats/exhaustiveness con 2º país sembrado. Sin ellos un país puede declararse sellado mientras la API sangra ES en silencio. |
| SH2 | **No hay test de aislamiento de cache cross-country** `[VERIFIED cache.py:79-94]` | Test que prueba que DE-28 nunca recibe el cuerpo cacheado de ES-28. Depende de MP6. |
| SH3 | `v_exhaustiveness_seal` single-build-global `[VERIFIED 0048:82-88]` | Resolución B5: latest-build por país ⇒ el contrato de servir el sello es durable entre países. |
| SH4 | **No hay precondición "denominador presente"** antes de sellar `[VERIFIED 0042:37; 0043:62]` | Condicionar el sellado a la existencia del denominador; `NO_DENOM` se muestra como "no certificable", no "pendiente". |
| SH5 | **No hay criterio de rollback de la capa de servir** (cache flush + recompute `product_stats`) | Especificado arriba (sección Rollback). `product_stats` global queda doble-contada hasta el refresh. |
| SH6 | El intervalo "100% certificado" sólo es estable para la fila nacional ES; con latest-build-global la cota de un país sellado puede cambiar al hacer build otro | Resolución B5 (latest-por-país) lo vuelve **monótono/estable por país**. |

> Síntesis del veredicto: el motor de **transporte** (skeleton/envelope/auth/rate-limit/cache) HOLD limpio y genérico. La **capa de datos servida y los agregados** NO HOLD: requieren las vistas aditivas (`servable_entity +country`, `v_servable_dealer` cableada, seal/exhaustiveness por país), `product_stats` por país, la decisión de entrada de país, y la generalización de la profundidad geográfica. Dos OPEN ITEMS no se cierran en esta etapa: el **denominador por país** (gate legal/ToS) y la **identidad cross-border** (`canonical_key`, etapa 4). El servido los **defiende** (filtra por país, muestra `NO_DENOM` honesto) pero no los origina.

---

## Sub-proyectos institucionales — 360° por faceta (31 facetas)

> Mandato owner 2026-06-27: **cada punto = proyecto paralelo**. Esta etapa se atomiza en **31 facetas**, y cada faceta es un **proyecto institucional 360°** con seis caras fijas: **deep-spec** (`[VERIFIED path:línea]` leído a la fuente) · **costura** ES→genérico · **fix** `propuesta [no implementada]` · **adversarial** (DE/FR/IT/PT/no-UE) · **sellado** multi-vía · **herramienta NEXT-LEVEL** €0.
>
> **Trazabilidad con el veredicto.** Las 31 facetas son la expansión PROFUNDA de los **8 breaks + 8 missing-pack + 6 sealing-holes** del veredicto adversarial y de las **9 mejoras**: ninguna rotura se diluye; cada una recibe su tratamiento 360°. Los dos **OPEN ITEMS** que esta etapa NO origina —denominador por país (gate LEGAL/ToS, facetas 10/11) e identidad cross-border (`canonical_key`, etapa 4, faceta 14)— se **defienden** (filtrado por país, `NO_DENOM` honesto), no se fabrican.
>
> **Coherencia con `00-MASTER`.** El maestro fija para Servir «pack = ~nada (país = dimensión)»: cierto para el **motor de transporte** (skeleton/envelope/auth/rate-limit/cache, HOLD limpio), FALSO para la **capa de datos servida y los agregados** —que es exactamente lo que estas 31 facetas convierten en país-dimensión. Honra los invariantes del maestro: €0 de cimiento, `cdp_code` paramétrico, VAM cero-confianza, «antes confesar un hueco que vender una mentira».

**Las dos fichas-madre del dominó.** Casi toda faceta geo/agregada depende de **[Faceta 1](#f1)** (`servable_entity` proyecta `country_code` — la costura raíz) y de **[Faceta 16](#f16)** (cómo entra el país en la request — la decisión no tomada). Sin esas dos, ningún predicado país tiene de dónde leer ni dónde aterrizar.

<a id="indice-subproyectos"></a>

### Índice navegable (funnel por clúster)

**I · Capa de datos raíz (vistas servidas)**

- [Faceta 1](#f1) · servable_entity +country_code (la costura raíz)
- [Faceta 2](#f2) · v_servable_dealer: cablear la definición única + country

**II · Geo keyed + árbol de profundidad variable**

- [Faceta 4](#f4) · Geo keyed-by-province: lookup compuesto (country,code)
- [Faceta 5](#f5) · Árbol geo: profundidad administrativa variable
- [Faceta 6](#f6) · admin_level_1: neutralizar ccaa → {code,label}
- [Faceta 7](#f7) · Taxonomía entity_kind: mapeo nativo→compartido
- [Faceta 8](#f8) · /geo/completeness por país (full_pct + geo_grid)

**III · Sello, denominador y exhaustividad por país**

- [Faceta 9](#f9) · v_province_seal: country-scoping del segmento VENTA
- [Faceta 10](#f10) · Denominador VENTA: fuente + loader por país
- [Faceta 11](#f11) · Denominador DESGUACE: censo de desguaces por país
- [Faceta 12](#f12) · v_exhaustiveness_seal: durabilidad y monotonía por país
- [Faceta 13](#f13) · NO_DENOM como precondición de sellado

**IV · Stats y agregados nacionales**

- [Faceta 3](#f3) · product_stats por-país (PK country_code)

**V · Identidad servida cross-border**

- [Faceta 14](#f14) · canonical_key cross-border: pureza de cluster servido
- [Faceta 15](#f15) · Validador tax-id por país (rama cif:)

**VI · Dimensión-país en el transporte**

- [Faceta 16](#f16) · Plomería de la dimensión-país en la request
- [Faceta 17](#f17) · Cache key: dimensión país/tenant + aislamiento
- [Faceta 24](#f24) · country_code aditivo en salida + meta.country

**VII · Seguridad, borde y operación**

- [Faceta 18](#f18) · Rate-limit: import-time, mono-proceso, por país
- [Faceta 19](#f19) · Auth + fail-fast de prod (invariancia multi-país)
- [Faceta 20](#f20) · Terminación TLS en el borde (reverse-proxy €0)
- [Faceta 21](#f21) · CORS multi-origen / per-deployment
- [Faceta 27](#f27) · Paginación keyset (cursor) + ETag/304
- [Faceta 28](#f28) · /alerts y /sources: atribución por país

**VIII · Endpoints nuevos nacidos genéricos**

- [Faceta 22](#f22) · /search typo-tolerante country-scoped
- [Faceta 23](#f23) · Índice compuesto GIN (country_code, trgm)
- [Faceta 25](#f25) · /countries: índice del censo servible
- [Faceta 26](#f26) · country_registry: la fila declarativa del pack

**IX · Sellado mecánico (gates de verificación)**

- [Faceta 29](#f29) · Golden multi-país + suite no-bleed (HTTP-vs-SQL)
- [Faceta 30](#f30) · Snapshot OpenAPI/contrato de los 18 endpoints
- [Faceta 31](#f31) · Runbook de rollback per-país de la capa de servido

---

<a id="f1"></a>

### Faceta 1 · servable_entity +country_code (la costura raíz)

**(a) Code_hints verificados**
- **[VERIFIED migrations/0046_servable_entity_status_filter.sql:17-29]** `CREATE OR REPLACE VIEW servable_entity AS SELECT entity_ulid, cdp_code, kind, legal_name, trade_name, cif, cnae, province_code, municipality_code, comarca_id, address, postcode, lat, lon, phone, email, website, website_waf, is_tier1, status, recipe_version, first_discovered_source, created_at, last_seen, org_id, sells_cars, kind_source, geocode_source, geocode_precision, defense_detail, closed_at, close_reason, canonical_key, attest_count, defense_tier, source_group, role FROM entity e WHERE e.status NOT IN ('evicted','closed') AND NOT EXISTS(...quarantine...)`. Conteo exacto = **37 columnas, SIN `country_code`**. PII en la proyeccion: `address, postcode, lat, lon` (:18-19) + `phone, email` (:19).
- **[VERIFIED migrations/0046:31-42]** bloque `-- Rollback` comentado que restaura la definicion quarantine-only de 0031 con la MISMA proyeccion de 37 columnas (sin status guard) — la reversion es byte-exacta.
- **[VERIFIED migrations/0052_country.sql:54]** `ALTER TABLE entity ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` — la TABLA BASE ya tiene `country_code` desde 0052; el view simplemente no lo proyecta. DEFAULT 'ES' => todas las filas existentes backfilled como Spain (no hay NULL posible: NOT NULL).
- **[VERIFIED migrations/0052_country.sql:36-38]** nota (d): `vehicle.country` es derivable via `vehicle.entity_ulid -> entity.country_code`; FASE-0 mantiene geo+entity como unica fuente del pais (YAGNI, evita reescritura de 2.3M filas) — justifica NO tocar `servable_vehicle`.
- **Consumidores que hoy NO pueden filtrar pais** (leen el view sin la columna): **[VERIFIED services/api/routers/geo.py:266]** `FROM servable_entity se` (entities_by_province), **[:322]** `FROM servable_entity` (entities_by_municipality), **[:387]** `FROM servable_entity e` (province_inventory_tree), **[:414-415]** `SELECT count(*) FROM servable_entity WHERE province_code=$1 ...` (province_only).

**(b) Mecanismo al atomo**
`servable_entity` es el **publish-gate VIEW** que 0031 declaro como contrato ("the API reads through these views, never the raw tables ... the subject vanishes from every served surface, mechanically"). 0046 es su definicion viva. Un VIEW es una **query guardada, no filas materializadas**: un `CREATE OR REPLACE VIEW` que anade una columna ya presente en la tabla base (`se.country_code`) **toca cero filas**, es idempotente y de riesgo cero. El resultado es un view de **38 columnas**; la nueva es la dimension pais que CADA router geo necesita en su `WHERE`. No hay computo, no hay reindexado, no hay migracion de datos: es pura algebra relacional adicional.

**(c) Costura ES->generico**
Hoy el view es **country-blind**. Con un 2o pais cargado, el view devuelve filas ES+CC **fusionadas** y **ningun** handler geo puede anadir `AND country_code=$cc` porque la columna **no esta proyectada**. Esta es la **primera ficha del domino**: las facetas 4-9 (predicados geo, arbol, completeness, sello-venta) **no pueden filtrar** hasta que esto aterrice. "Existen filas geo para CC" es necesario pero **NO suficiente** hasta que el view exponga el pais.

**(d) Riesgo adversarial**
**DE/FR/IT/PT:** con 2o pais cargado y el view aun a 37 columnas, `/geo/{prov}/entities`, `/geo/{prov}/municipalities/{m}/entities` y `/geo/{prov}/tree` devuelven filas ES+CC fusionadas **SIN lanzar excepcion** — regresion de **correccion silenciosa**, el peor modo de fallo (no hay error, solo datos mal). Provincia '28' => devuelve (ES Madrid)+(DE Brandenburg) fusionados. **No-UE/ruido:** imposible NULL bleed (NOT NULL DEFAULT 'ES'), pero una fila mal-etiquetada 'ES' upstream se serviria en silencio bajo ES.

**(e) Criterio de sellado + verificacion multi-via**
1. **Introspeccion de schema:** `information_schema.columns` muestra `servable_entity` con `country_code` (37->38 cols).
2. **ES byte-identico:** las 37 columnas servidas previas inalteradas; snapshot golden de una fila `cdp_code` conocida igual pre/post (solo se anade `country_code='ES'`, aditivo, no rompe `dict(row)`).
3. **Precondicion no-bleed:** con una fila DE sembrada en txn revertida (patron [VERIFIED tests/test_country_coexistence.py:416-458]), `SELECT DISTINCT country_code FROM servable_entity WHERE <pred CC>` devuelve solo el CC pedido.
4. **Rollback:** aplicar el bloque Rollback de 0046 restaura exactamente 37 columnas.

**(f) Herramienta NEXT-LEVEL (si aplica)**
El cambio de view en si es **SQL de dependencia cero**. La elevacion honesta es el **contrato de datos** alrededor: **Frictionless Framework (frictionless-py, Table Schema) — MIT** — https://github.com/frictionlessdata/frictionless-py **[VERIFIED NEXT-LEVEL.md:337]**. Declara la proyeccion servida como un Table Schema versionado que asevera `country_code` presente + `CHAR(2)` + toda fila servida con pais no-nulo, validado en CI/bootstrap ANTES de confiar en el view — convierte "el view expone pais" de promesa a invariante maquina. Adyacente: **Great Expectations / Pandera (Apache-2.0)** **[VERIFIED NEXT-LEVEL.md:338,167]** como contrato PRE-sello fail-closed.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** servable_entity (publish-gate VIEW, 0046) proyecta 37 columnas SIN country_code aunque la tabla base entity YA lo tiene (0052:54). Hasta proyectarlo, NINGUN router geo (geo.py:266/322/387/415) puede anadir AND country_code=$cc. Es la costura RAIZ: bloquea facetas 4-9.
- **Fix — propuesta [no implementada].** Nueva migracion aditiva (p.ej. 0057): CREATE OR REPLACE VIEW servable_entity reproduciendo las 37 columnas de 0046 + se.country_code (38 cols), idempotente, con bloque Rollback que restaura la proyeccion exacta de 37. ES byte-identico: toda fila country_code='ES' (DEFAULT 0052), consumidores SELECT*/dict(row) solo ganan un campo 'ES' aditivo. servable_vehicle NO se toca (YAGNI 0052 nota d: pais derivable via entity_ulid).
- **Adversarial (DE/FR/IT/PT/no-UE).** DE/FR/IT/PT: con 2o pais y view a 37 cols, cada endpoint geo devuelve filas ES+CC fusionadas SIN excepcion -> regresion de correccion silenciosa (no error, solo datos mal). Provincia '28' = (ES Madrid)+(DE Brandenburg) mezclados. No hay NULL bleed (NOT NULL DEFAULT 'ES').
- **Sellado + verificación multi-vía.** (1) information_schema.columns: servable_entity tiene country_code (37->38). (2) Golden ES byte-identico: 37 columnas servidas inalteradas, fila conocida igual pre/post. (3) No-bleed: DE en txn revertida (patron test_country_coexistence.py:416-458) -> SELECT DISTINCT country_code tras predicado = solo CC pedido. (4) Rollback restaura 37 cols exactas.
- **Herramienta NEXT-LEVEL (€0).** Frictionless Framework (frictionless-py, Table Schema) — MIT [VERIFIED NEXT-LEVEL.md:337] — https://github.com/frictionlessdata/frictionless-py. Contrato de datos versionado que asevera country_code presente/CHAR(2)/no-nulo en la superficie servida, validado en CI/bootstrap. Adyacente: Great Expectations/Pandera Apache-2.0 [VERIFIED NEXT-LEVEL.md:338]. El cambio de view en si es SQL dependencia-cero.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f2"></a>

### Faceta 2 · v_servable_dealer: cablear la definición única + country

**(a) code_hints VERIFICADOS leyendo la fuente**
- **El view existe** [VERIFIED migrations/0056_v_servable_dealer.sql:26-37]: `CREATE OR REPLACE VIEW v_servable_dealer AS SELECT se.entity_ulid, se.cdp_code, se.kind, vdr.resolved_cdp_code, EXISTS(SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid=se.entity_ulid) AS has_inventory FROM servable_entity se JOIN v_dealer_resolved vdr ON vdr.entity_ulid=se.entity_ulid WHERE se.status='active' AND se.kind::text NOT IN ('particular','desguace') AND (se.kind::text<>'garaje' OR EXISTS(... servable_vehicle ...))`.
- **CERO routers lo leen** [VERIFIED] — `grep v_servable_dealer services/` devuelve 0 ficheros. El view 0056 fue creado para unificar y quedo huerfano.
- **Cuatro scopes divergentes que verifico uno a uno:**
  1. `/stats` "dealers" [VERIFIED services/api/stats.py:22-28]: `count(DISTINCT vdr.resolved_cdp_code) FROM v_dealer_resolved vdr JOIN entity e ... WHERE e.kind::text NOT IN ('particular','desguace') AND EXISTS(servable_vehicle)`. Lee **entity** (no servable_entity), **sin** filtro `status='active'`, y exige inventario para **TODO** kind. Comentario declara ~19.1k [VERIFIED stats.py:20-21].
  2. Numerador del sello VENTA [VERIFIED migrations/0042:19-28 y 0043:17-26]: `count(DISTINCT COALESCE(vdr.resolved_ulid,e.entity_ulid)) WHERE e.kind IN ('compraventa','concesionario_oficial') AND EXISTS(vehicle available)`. ~18.3k.
  3. `/geo/completeness` e_total [VERIFIED services/api/routers/geo.py:51]: `count(*) FROM entity WHERE kind <> 'particular'` (~54.6k, la cifra inflada 2.9x que el owner cazo).
  4. El propio view 0056: row-set "directory" ~36.3k vs subconjunto `has_inventory` ~18.3k [VERIFIED 0056 comment :17-20].

**(b) El mecanismo al atomo**
El view define "punto de venta de coches" como entidad **publish-gated** (vive en servable_entity), **active**, que NO es listado particular (kind='particular') NI desguace de piezas (kind='desguace'), y para garajes/talleres SOLO con inventario. `has_inventory` es una columna SEPARADA (un EXISTS sobre servable_vehicle, 0056:31), de modo que el consumidor decide si cuenta el directorio (todas las filas) o solo los activos-con-stock (`WHERE has_inventory`). Atomo clave: stats.py exige inventario para **todos** los kinds (EXISTS incondicional), el view solo para **garaje** — asi que una compraventa con cero servable_vehicle entra en el directory del view pero NO en /stats. Las dos definiciones "unificadas" ya difieren en ese atomo. La unificacion correcta = `/stats dealers := count(DISTINCT resolved_cdp_code) FROM v_servable_dealer WHERE has_inventory`, que reconcilia ambas a la misma cifra (~19.1k).

**(c) Costura ES->generico**
El view selecciona `se.*` de servable_entity pero **no proyecta country_code**, y servable_entity (0046) tampoco lo expone todavia (es la faceta 1, dependencia dura). Por tanto v_servable_dealer es hoy fisicamente incapaz de filtrar pais aunque se quisiera.

**(d) Riesgo adversarial**
Con Portugal cargado, cada superficie hereda su propio scope erroneo: /stats una cota, /geo otra, /seal otra — incomparables — y el owner re-caza un inflado ahora multiplicado por N paises. Cross-border: una compraventa con codigo de provincia '28' compartido entre ES y PT suma a un conteo mixto si country no entra en el predicado del view.

**(e) Sellado + verificacion multi-via**
Detallado en `sealing`.

**(f) Herramienta de nivel inalcanzable**
Detallado en `tool`.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** v_servable_dealer (0056:27-33) lee se.* de servable_entity pero NO selecciona country_code; servable_entity (0046) no lo proyecta (faceta 1, dependencia). Ademas el view existe pero 0 routers lo consumen [VERIFIED grep=0]: las 4 superficies (stats.py:22-28, sello 0042/0043, geo.py:51) inlinean scopes divergentes en vez de leer la unica fuente de verdad. La costura es doble: (1) cablear los 3-4 consumidores al view, (2) anadir country al view tras faceta 1.
- **Fix — propuesta [no implementada].** 1) DEPENDENCIA faceta 1: servable_entity proyecta country_code. 2) CREATE OR REPLACE VIEW v_servable_dealer anadiendo `se.country_code` al SELECT (aditivo, idempotente; rollback DROP VIEW ya presente 0056:45-46). 3) Re-apuntar las superficies a LEER el view: stats.py dealers := `count(DISTINCT resolved_cdp_code) FROM v_servable_dealer WHERE has_inventory AND country_code=$cc`; el numerador del sello y geo derivan su scope del mismo view (filtrando kinds venta donde aplique). 4) ES con country_code default 'ES' lee cifras byte-identicas (~19.1k dealers).
- **Adversarial (DE/FR/IT/PT/no-UE).** Portugal/2o pais: el titular 'Puntos de venta' deja de ser el conteo de NINGUN pais y cada superficie reporta una cota distinta e incomparable; el inflado 2.9x reaparece por N paises. Cross-border: codigo de provincia '28' compartido ES/PT colapsa numeradores mixtos si country no entra en el predicado del view. Ruido: entidades 'garaje' sin inventario y desguaces se recuentan distinto entre superficies (stats exige inventario a todos, el view solo a garaje), produciendo deltas inexplicables entre /stats y /geo.
- **Sellado + verificación multi-vía.** Criterio: headline == set paginado == scope certificado, POR PAIS. Multi-via: (a) golden ES — `count(DISTINCT resolved_cdp_code) FROM v_servable_dealer WHERE has_inventory` == el /stats dealers historico (~19.1k) byte-identico; (b) no-bleed coexistencia — sembrar DE en txn revertida (patron tests/test_country_coexistence.py:416-458) y asegurar que el conteo ES no cambia y que cada superficie devuelve solo filas del pais consultado; (c) 2a via — query asyncpg cruda independiente reproduce cada conteo de superficie; (d) guard de grep — ningun router vuelve a inlinear los SQL de scope (todos leen el view).
- **Herramienta NEXT-LEVEL (€0).** sraoss/pg_ivm (matview-incremental-ivm) — PostgreSQL License [VERIFIED docs/generic-engine-bible/NEXT-LEVEL.md:764] — https://github.com/sraoss/pg_ivm . Eleva el VIEW unificador a CREATE INCREMENTAL MATERIALIZED VIEW: la fuente unica de verdad del conteo de puntos de venta queda canonica Y siempre-fresca en O(delta) via triggers AFTER, sin ventana de staleness ni REFRESH manual. Aislamiento: IMMV con PK (country_code) — sembrar DE en txn revertida no altera los conteos ES [NEXT-LEVEL:767]. Rollback = volver a view normal (limpio).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f3"></a>

### Faceta 3 · product_stats por-país (PK country_code)

**(a) Code_hints VERIFICADOS leyendo la fuente real**
- [VERIFIED migrations/0055_product_stats.sql:14-22] `CREATE TABLE IF NOT EXISTS product_stats (id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1), dealers BIGINT, vehicles_unique_available BIGINT, events BIGINT, provinces INTEGER, municipalities INTEGER, computed_at TIMESTAMPTZ NOT NULL DEFAULT now())`. La fila global UNICA esta fisicamente impuesta por PK + CHECK(id = 1).
- [VERIFIED services/api/stats.py:14-39] `_QUERIES` = 5 agregados (dealers = count(DISTINCT vdr.resolved_cdp_code) JOIN entity WHERE kind NOT IN ('particular','desguace') AND EXISTS servable_vehicle; vehicles_unique_available; events; provinces; municipalities). NINGUNO lleva predicado de pais. `compute_counts(conn)` itera el dict sin parametro pais.
- [VERIFIED services/api/routers/ops.py:84-98] el handler /stats hace `fetchrow('SELECT dealers, ... FROM product_stats WHERE id = 1')`, con fallback a `compute_counts(c)` ante `UndefinedTableError`, y responde `ok({counts}, computed_at, source)`.
- [VERIFIED scripts/refresh_product_stats.py:26-44] `INSERT INTO product_stats (id, ...) VALUES (1, $1..$5, now()) ON CONFLICT (id) DO UPDATE` — UPSERT con id=1 cableado.
- Matiz [VERIFIED services/api/cache.py:57-62]: /stats NO esta en CACHEABLE_PATH_PREFIXES ('/geo/','/entities/','/platforms/'), asi que el TTLCache HTTP es no-op para /stats; el unico cache de /stats es la fila precomputada product_stats. Por tanto la re-arquitectura por-pais de product_stats es la UNICA palanca de rendimiento de un /stats por pais.

**(b) Mecanismo al atomo**
GET /stats lee UNA fila. dealers y vehicles_unique_available son COUNT(DISTINCT)/JOIN sobre 2,3M+ filas (~83s en frio segun cabecera de 0055), por eso deben precomputarse fuera del request. product_stats ES ese precompute: una sola fila fisica id=1; el CHECK(id=1) hace estructuralmente imposible una segunda fila. refresh_product_stats calcula los 5 conteos GLOBALES y hace UPSERT de esa unica fila por cadencia del scheduler; el handler la lee con WHERE id=1 y un fallback live para pre-migracion/pre-refresh, exponiendo computed_at.

**(c) Costura ES->generico + fix exacto**
El engine_invariant afirma 'product_stats re-apuntado sirve cualquier pais' — FALSO: una fila con CHECK(id=1) no puede guardar conteos por pais. El fix es una migracion de PK, no un tweak de query:
1. Migracion 0057: `CREATE TABLE product_stats (country_code CHAR(2) PRIMARY KEY REFERENCES country_registry(country_code), dealers BIGINT, ..., computed_at TIMESTAMPTZ NOT NULL DEFAULT now())` — eliminar id y el CHECK(id=1); PK = country_code (una fila por pais). Migrar la fila id=1 existente a country_code='ES' preservando conteos byte-identicos. Aditiva/reversible (rollback recrea la tabla single-row id=1 y copia la fila ES de vuelta a id=1).
2. stats.py: parametrizar los 5 `_QUERIES` con `AND <tabla>.country_code = $1` — entity.country_code (existe desde 0052) para dealers; geo_province/geo_municipality por country_code (PK compuesto desde 0053); vehicle_event/servable_vehicle via entity.country_code. Firma `compute_counts(conn, country_code)`; ES-default pasa 'ES' y lee numeros byte-identicos.
3. refresh_product_stats.py: iterar country_registry y computar+UPSERT por pais con `ON CONFLICT (country_code) DO UPDATE`.
4. ops.py: /stats?country=CC (dimension de faceta 16) -> `fetchrow('SELECT ... FROM product_stats WHERE country_code = $1', cc)`, su propio computed_at y fallback live country-scoped.

**(d) Riesgo adversarial concreto**
Portugal (o cualquier 2o pais) cargado con product_stats aun single-row: el titular 'Puntos de venta' pasa a ser la SUMA ES+PT — el conteo real de NINGUN pais — y refresh_product_stats sobre-escribe id=1 con un total mezclado. Cero excepcion: regresion de correccion silenciosa sobre el numero mas publico del producto.

**(e) Criterio de sellado + verificacion multi-via**
1. Fila por pais existe: tras migracion+refresh, `count(*) FROM product_stats` == nº de paises onboardeados; el dealers de cada fila casa un compute_counts country-scoped vivo (2a via: recount SQL independiente).
2. Golden ES byte-identico: product_stats['ES'].dealers == el valor pre-migracion id=1 (cero regresion ES).
3. Aislamiento: sembrar DE en txn revertida (patron test_country_coexistence.py:416-458), refresh, asegurar product_stats['ES'] intacto y product_stats['DE'] solo con filas DE.
4. Via HTTP: /stats?country=ES y ?country=DE devuelven conteos disjuntos; /stats?country=XX (sin fila) cae al fallback live country-scoped, jamas a la suma global.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
[VERIFIED NEXT-LEVEL.md:761-767] **sraoss/pg_ivm** (PostgreSQL License [VERIFIED], EUR0) — https://github.com/sraoss/pg_ivm. Sustituir el refresh manual por cadencia con una INCREMENTAL MATERIALIZED VIEW keyed por country_code: el agregado se auto-mantiene en O(delta) via triggers AFTER en las tablas base, eliminando la ventana de staleness y el riesgo de un job de refresh olvidado — el titular nunca miente ni envejece sin un solo cron. Complementar [VERIFIED NEXT-LEVEL.md:769-775] con **citusdata/pg_cron** (PostgreSQL License [VERIFIED], https://github.com/citusdata/pg_cron) + freshness-SLO en deps.py (meta.freshness = now()-computed_at, degradar sobre umbral) para los agregados que IVM no mantiene incrementalmente.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** PK CHECK(id=1) [VERIFIED 0055:14-15] impide fisicamente conteos por pais; _QUERIES [VERIFIED stats.py:14-39], el UPSERT id=1 [VERIFIED refresh_product_stats.py:26-44] y el WHERE id=1 [VERIFIED ops.py:86-94] son todos country-blind. La afirmacion 'product_stats re-apuntado sirve cualquier pais' es falsa.
- **Fix — propuesta [no implementada].** Migracion 0057: PK pasa de id SMALLINT CHECK(id=1) a country_code CHAR(2) REFERENCES country_registry; migrar id=1 -> 'ES' byte-identico. Parametrizar los 5 _QUERIES con country_code=$1 (entity/geo/vehicle via country_code de 0052/0053). refresh itera country_registry con ON CONFLICT (country_code). /stats?country=CC lee su fila. Reversible (rollback recrea single-row id=1).
- **Adversarial (DE/FR/IT/PT/no-UE).** Con un 2o pais y product_stats single-row, 'Puntos de venta' = suma ES+PT (conteo de ningun pais) y el refresh sobre-escribe id=1 con un total mezclado, sin excepcion.
- **Sellado + verificación multi-vía.** (1) count(*) product_stats == nº paises y cada fila casa recount SQL independiente; (2) product_stats['ES'] == valor pre-migracion (golden); (3) DE sembrado en txn revertida no altera la fila ES (test_country_coexistence:416-458); (4) /stats?country=ES vs DE disjuntos, XX cae a fallback live, nunca a la suma.
- **Herramienta NEXT-LEVEL (€0).** [VERIFIED NEXT-LEVEL.md:761-775] sraoss/pg_ivm (PostgreSQL License, EUR0) https://github.com/sraoss/pg_ivm — IMMV por country_code, fresca sin cron; + citusdata/pg_cron (PostgreSQL License) https://github.com/citusdata/pg_cron + freshness-SLO en meta para agregados no-incrementales.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f4"></a>

### Faceta 4 · Geo keyed-by-province: lookup compuesto (country,code)

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/routers/geo.py:229` — `@router.get("/geo/{province_code}/entities")`, handler `entities_by_province(province_code: str, ...)`. El predicado de pertenencia esta en `geo.py:268`: `WHERE se.province_code = $1` (param unico, SIN `country_code`). El SELECT (geo.py:259-274) ya colapsa alias a canonical via `JOIN v_dealer_resolved vdr` con `DISTINCT ON (vdr.resolved_cdp_code)` — el unico eje de filtrado es la provincia desnuda. [VERIFIED]
- `geo.py:292` — `@router.get("/geo/{province_code}/municipalities/{muni_code}/entities")`; WHERE en `geo.py:323-324`: `WHERE province_code = $1 AND municipality_code = $2` (sin country). [VERIFIED]
- `geo.py:352` — `@router.get("/geo/{province_code}/tree")`; el lookup de cabecera en `geo.py:369-371`: `await c.fetchrow("SELECT code, name, ccaa_code, ccaa_name FROM geo_province WHERE code=$1", province_code)` — monocolumna `code=$1`, **SIN `ORDER BY`**, sin `country_code`. El GROUP BY del arbol en `geo.py:390`: `WHERE e.province_code = $1 AND e.comarca_id IS NOT NULL`; el fetchval `province_only` en `geo.py:414-417` tambien keyea `province_code=$1` solo. [VERIFIED]
- PK compuesto: `migrations/0053_country_onboarding.sql:75` — `ALTER TABLE geo_province ADD CONSTRAINT geo_province_pkey PRIMARY KEY (country_code, code);` (gemelo `geo_municipality_pkey (country_code, code)` en :84). Tras 0053 la identidad geo es compuesta. [VERIFIED]

**(b) Mecanismo al atomo**
Tres handlers leen una provincia por su `code` desnudo:
1. **entities_by_province**: `SELECT DISTINCT ON (vdr.resolved_cdp_code) ... FROM servable_entity se JOIN v_dealer_resolved vdr ON vdr.entity_ulid=se.entity_ulid WHERE se.province_code=$1 AND se.status='active' AND se.kind<>'particular'`, paginado por `page_slice`. El `province_code` llega del path; no hay segundo eje.
2. **entities_by_municipality**: identico con `province_code=$1 AND municipality_code=$2`.
3. **province_inventory_tree**: primero `fetchrow` de `geo_province WHERE code=$1` para el header (name+ccaa_code+ccaa_name), luego el GROUP BY comarca/municipio `WHERE e.province_code=$1`. El `fetchrow` devuelve EXACTAMENTE UNA fila: con PK monocolumna (pre-0053) habia 1 sola fila '28'; con PK compuesto (post-0053) coexisten (ES,28) y (DE,28), y `WHERE code=$1` sin `ORDER BY` deja al planner elegir cual devolver — no determinista (depende del plan / orden fisico de tupla).

**(c) Costura ES->generico**
La costura es la AUSENCIA del eje pais en tres sitios: (i) la firma de ruta, (ii) cada `WHERE`, (iii) el `fetchrow` de cabecera del arbol. ES funciona hoy porque 0053 relabela TODAS las filas a `country_code='ES'` 1:1 (migrations/0053:7-13): el predicado de pais es implicito y unico, asi que `code=$1` resuelve sin ambiguedad. En cuanto entra un 2o pais, el `code` deja de ser clave.

**(d) Fix exacto**
1. **Eje pais en la ruta**: anteponer segmento `/{country_code}/geo/...` o aceptar `?country=` con default `'ES'` resuelto por la faceta 16 (plomeria de dimension-pais); prohibido `DEFAULT_COUNTRY` silencioso.
2. **entities_by_province**: anadir `AND se.country_code = $N` al WHERE (geo.py:268). Requiere que `servable_entity` proyecte `country_code` (faceta 1 — dependencia dura).
3. **entities_by_municipality**: `AND country_code = $N` (geo.py:323).
4. **province_inventory_tree**: cambiar el `fetchrow` (geo.py:369-371) a `WHERE country_code=$1 AND code=$2` — lookup por el PK compuesto COMPLETO, lo que elimina la no-determinacion de raiz; anadir `AND e.country_code=$N` al GROUP BY (geo.py:390) y al fetchval `province_only` (geo.py:414-417).
5. **ES byte-identico**: con default `'ES'`, cada `(ES,28)` resuelve la misma fila -> URL y cuerpo actuales exactos (golden ES diff vacio).

**(e) Sellado + verificacion multi-via**
- **Golden ES**: `/geo/28/entities`, `/geo/28/tree`, `/geo/28/municipalities/M/entities` con default `'ES'` reproducen el cuerpo actual byte-identico (diff vacio).
- **No-bleed**: con `(DE,28)` sembrado en txn revertida, `/geo/ES/28/entities` NO contiene ningun cdp_code de DE y viceversa (patron HTTP-vs-SQL `tests/test_api_gaps.py:50-61`; suite de faceta 29).
- **Determinismo del header**: `/geo/ES/28/tree` devuelve SIEMPRE name/ccaa de (ES,28) en N ejecuciones del mismo proceso (el fetchrow ya keyea por PK compuesto).
- **Disjuncion**: el set de cdp_code de `/geo/ES/X` y `/geo/DE/X` es disjunto.

**(f) Herramienta NEXT-LEVEL**
**api-schema-fuzz — Schemathesis** (MIT [VERIFIED]) https://github.com/schemathesis/schemathesis [NEXT-LEVEL.md:828]. Genera property-based (Hypothesis) miles de `province_code`/`country_code` desde el `/openapi.json` que FastAPI ya expone; un check stateful custom asserta que toda respuesta con dimension pais SOLO trae ese pais. Convierte el no-bleed de afirmacion a invariante AUTO-ATACADO en cada push y caza el 500 / la fila arbitraria del fetchrow ambiguo que ningun test escrito a mano cubre. Complementa el golden no-bleed de la faceta 29 (verificacion escrita) con generacion adversarial (verificacion descubierta). Alternativa: **oasdiff** (api-breaking-change-gate, Apache-2.0 [VERIFIED], NEXT-LEVEL.md:836) para garantizar que anadir el eje pais es aditivo y no rompe el contrato pan-EU.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** Los 3 handlers /geo/{province_code}/{entities, municipalities/{muni}/entities, tree} keyean por province_code DESNUDO: WHERE se.province_code=$1 (geo.py:268), WHERE province_code=$1 (geo.py:323), y el fetchrow de cabecera del arbol 'SELECT code,name,ccaa_code,ccaa_name FROM geo_province WHERE code=$1' SIN ORDER BY ni country (geo.py:369-371). Tras migrations/0053:75 el PK geo es (country_code,code): el codigo '28' identifica (ES,Madrid) Y (DE,Eure-et-Loir). Falta el eje pais en la firma de ruta, en cada WHERE y en el lookup monocolumna de provincia.
- **Fix — propuesta [no implementada].** Introducir la dimension pais (segmento /{country_code}/ o ?country= con default 'ES' via faceta 16, nunca DEFAULT_COUNTRY silencioso) y threadearla: AND se.country_code=$N en geo.py:268, AND country_code=$N en geo.py:323, AND e.country_code=$N en el GROUP BY geo.py:390 y el fetchval province_only geo.py:414-417. CRITICO: cambiar el fetchrow de cabecera (geo.py:369-371) a 'WHERE country_code=$1 AND code=$2' para keyear por el PK compuesto completo y eliminar la no-determinacion. Dependencia dura de la faceta 1 (servable_entity debe proyectar country_code). ES con default 'ES' resuelve la misma fila -> golden byte-identico.
- **Adversarial (DE/FR/IT/PT/no-UE).** FR/DE: con (DE,28) cargado, GET /geo/28/entities lista filas ES+DE fusionadas (el JOIN v_dealer_resolved no acota pais) y GET /geo/28/tree toma name+ccaa de la provincia que el planner devuelva primero en el fetchrow sin ORDER BY (geo.py:370) — NO determinista entre ejecuciones. PT/IT comparten codigos numericos de provincia con ES -> colision GARANTIZADA, no teorica (el diseno la llama 'ambigua' pero con PK compuesto es bleed seguro). No lanza excepcion: regresion de correccion SILENCIOSA con CI verde.
- **Sellado + verificación multi-vía.** Multi-via: (1) Golden ES byte-identico en los 3 endpoints con default 'ES' (diff vacio). (2) No-bleed HTTP-vs-SQL (test_api_gaps.py:50-61) con DE-28 sembrado en txn revertida: cero cdp_code de DE en /geo/ES/28 y viceversa. (3) Determinismo: /geo/ES/28/tree devuelve siempre (ES,28) en N corridas (fetchrow ahora por PK compuesto). (4) Disjuncion de cdp_code entre /geo/ES/X y /geo/DE/X.
- **Herramienta NEXT-LEVEL (€0).** api-schema-fuzz — Schemathesis (MIT [VERIFIED]) https://github.com/schemathesis/schemathesis [NEXT-LEVEL.md:828]. Fuzz property-based del /openapi.json de FastAPI: caza el 500/fila-arbitraria del fetchrow ambiguo y, con un check custom de pais, sella el no-bleed mecanicamente en cada push (complementa el golden escrito de la faceta 29 con generacion adversarial). Alt: oasdiff (api-breaking-change-gate, Apache-2.0 [VERIFIED], NEXT-LEVEL.md:836) para que el eje pais sea aditivo sin breaking change.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f5"></a>

### Faceta 5 · Árbol geo: profundidad administrativa variable

**(a) Code_hints verificados a la fuente real**
- **El arbol es estructuralmente 4-tier ES** (`pais -> PROVINCIA -> COMARCA -> ciudad`) declarado en el docstring [VERIFIED services/api/routers/geo.py:359]. El endpoint es `province_inventory_tree` [VERIFIED geo.py:352-426], RATE_EXPENSIVE + cacheado.
- La query del arbol [VERIFIED geo.py:374-395] encadena DOS INNER JOIN obligatorios:
  - `JOIN geo_municipality m ON m.code = e.municipality_code` [VERIFIED geo.py:388]
  - `JOIN geo_comarca co ON co.id = m.comarca_id` [VERIFIED geo.py:389]
  - filtro `WHERE e.province_code = $1 AND e.comarca_id IS NOT NULL AND e.kind <> 'particular'` [VERIFIED geo.py:390-391]
  - `GROUP BY co.id, co.name, co.ine_code, m.code, m.name` [VERIFIED geo.py:392] con `HAVING count(e.entity_ulid) > 0` [VERIFIED geo.py:393]
- **geo_comarca no tiene columna `code`**: PK es `id`, UNIQUE es `(province_code, name)` [VERIFIED migrations/0052_country.sql:39-41]; recibe country_code por consistencia pero NO hay superficie `(country, code)` que aplique [VERIFIED 0052:52]. La comarca es un surrogate INTERNO ES (`co.id`), no un codigo administrativo oficial cross-walkable.
- El fixture de coexistencia siembra la muni DE con `comarca_id=NULL` [VERIFIED tests/test_country_coexistence.py:276-278, la fila VALUES con NULL en :277].
- La misma dependencia de comarca contamina `/geo/completeness`: `full` exige `comarca_id IS NOT NULL` [VERIFIED geo.py:54,66-67] (faceta 8, hermana).

**(b) Mecanismo al atomo**
El arbol se construye con UNA sola SQL cuya espina es la cadena `entity -> geo_municipality (por municipality_code) -> geo_comarca (por comarca_id)`. Como el JOIN a geo_comarca es **INNER** y ademas el WHERE impone `e.comarca_id IS NOT NULL`, todo dealer cuya municipality tenga `comarca_id NULL` se ELIMINA del resultado entero. La comarca (`co.id`) es ademas la **clave de agrupacion** y el **contenedor de nodo** de la respuesta (`comarcas: dict[int]` [VERIFIED geo.py:396-410], las municipalities cuelgan de un nodo comarca). El 3er tier es estructuralmente portante: sin el no hay clave de GROUP BY ni nodo donde colgar municipios. El contrato de salida fija una profundidad de 4 niveles soldada en la forma del JSON, no parametrizada.

**(c–f) Síntesis**
Convertir la PROFUNDIDAD en DATO (un manifiesto de niveles por país derivado de ISO 3166-2) y el mid-tier en OPCIONAL/colapsable (LEFT JOIN + nodo sintético), de modo que un país sin comarca produzca árbol no-vacío `provincia -> ciudad`; ES mantiene 4-tier byte-idéntico. *Costura, fix, adversarial, sellado y herramienta NEXT-LEVEL: en la **Ficha operativa** debajo.*

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** **ES -> generico.** `comarca` es un tier administrativo SOLO espanol (agrupacion uniforme de municipios dentro de provincia; oficial solo en algunas CCAA, fabricado uniforme para el resto). El contrato del arbol hardcodea una profundidad fija de 4 tiers via los dos INNER JOIN + el predicado `comarca_id IS NOT NULL` [VERIFIED geo.py:388-390]. Un pais cuya geografia administrativa es 3-tier (p.ej. DE `Bundesland->Kreis->Gemeinde`, que mapea a provincia->...->municipio SIN equivalente de comarca; o un pais plano `pais->provincia->ciudad`) no puede poblar geo_comarca: `comarca_id` es NULL en cada fila y el INNER JOIN + NOT NULL vacia el resultado. Ademas geo_comarca no tiene `code` oficial [VERIFIED 0052:39-41], asi que ni siquiera se puede cross-walkear a un mid-tier extranjero. La profundidad de niveles es una decision NO tomada por el diseno, que redujo la geo a un solo admin1_label e ignoro cuantos tiers tiene cada pais.
- **Fix — propuesta [no implementada].** **Fix exacto — el mid-tier OPCIONAL/colapsable:**
1. Leer el numero de tiers del pais de un manifiesto por-pais (`geo_unit_level`, alimentado por country_registry de faceta 26, derivado de pycountry/ISO 3166-2).
2. `geo.py:389`: cambiar `JOIN geo_comarca co` a **`LEFT JOIN geo_comarca co ON co.id = m.comarca_id`**.
3. `geo.py:390`: WHERE pasa a `WHERE e.province_code = $1 AND e.country_code = $cc AND e.kind <> 'particular'` (ELIMINAR `AND e.comarca_id IS NOT NULL`); anadir `AND m.country_code = $cc` al join de muni.
4. `geo.py:392` GROUP BY: mantener `co.id` ahora nullable — un comarca NULL colapsa a UN nodo sintetico por provincia.
5. `geo.py:396-410` builder Python: cuando `r['comarca_id'] is None`, agrupar bajo un nodo centinela (`comarca_id='__none__'`, `name = admin-mid-label del manifiesto o '—'`) de modo que las municipalities sigan renderizando como `provincia -> municipio`.
6. `geo.py:369-370`: lookup de geo_province por `(country_code, code)` (PK compuesto 0053), no por `code` solo.
7. ES conserva `comarca_id NOT NULL` poblado -> el LEFT JOIN nunca cambia la salida ES (golden byte-identico). La profundidad pasa a ser DATA (manifiesto), no un doble-JOIN soldado.
- **Adversarial (DE/FR/IT/PT/no-UE).** **Alemania (CRITICAL).** El propio fixture de coexistencia siembra la muni DE con `comarca_id=NULL` [VERIFIED test_country_coexistence.py:277]. Con DE cargado, `/geo/{prov}/tree` de cualquier provincia DE corre el INNER JOIN geo_comarca + `comarca_id IS NOT NULL` -> **CERO filas -> el arbol entero sale VACIO para el pais completo**. Es el endpoint de drill-down (la UX de exploracion del producto, screenshots cardeep-02/03-explore) que deja de funcionar en TODO pais sin comarca. Y falla en SILENCIO: arbol vacio, HTTP 200, `comarca_count=0`, no excepcion. **FR** (regions/departements/communes), **IT** (regioni/province/comuni), **PT** (distritos/concelhos/freguesias), **MX** (estados/municipios), **JP** (prefectures) — ninguno tiene tier 'comarca'; todos devuelven arbol vacio. **Ruido intra-ES:** Ceuta/Melilla tienen municipio sin comarca (el bucket `municipality_no_comarca_ceuta_melilla` [VERIFIED geo.py:80] / completeness:55-57); esas filas YA se caen del arbol hoy — bug ES latente que la generalizacion tambien cierra.
- **Sellado + verificación multi-vía.** **Criterio de sellado + verificacion multi-via:**
- **Golden ES:** `/geo/28/tree` byte-identico antes/despues (anidamiento comarca, conteos por kind, orden por `co.ine_code`); el LEFT JOIN no puede alterar ES porque toda muni ES tiene `comarca_id NOT NULL`.
- **DE no-vacio:** sembrar el piloto DE (provincia '28' DE, muni '28001' comarca_id NULL, 1 dealer) en txn revertida [patron test_country_coexistence.py:259-285], pegar `/DE/geo/28/tree` (o `?country=DE`), assert arbol NO-VACIO con el dealer bajo un camino `provincia -> municipio` sin tier comarca.
- **Via 1 (HTTP-vs-SQL):** los conteos del arbol == `SELECT count(*) ... WHERE country_code='DE' AND province_code='28' AND kind<>'particular' AND status='active'`.
- **Via 2 (no-bleed):** `/DE/geo/28/tree` devuelve cero filas ES y `/ES/geo/28/tree` cero filas DE (disjuncion de cdp_code).
- **Via 3 (manifiesto de profundidad):** un pais con `geo_unit_level=2` produce arbol 2-tier, `=3` un 3-tier, aseverado contra el conteo de subdivisiones de pycountry.
- **Precondiciones:** faceta 1 (servable_entity proyecta country_code), faceta 26 (country_registry / manifiesto de nivel), faceta 16 (dimension pais en la request).
- **Herramienta NEXT-LEVEL (€0).** **pycountry (ISO 3166-1/-2 + ISO 4217)** — LGPL-2.1, €0 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. Conduce un manifiesto de sello/nivel por-pais (`geo_unit_level`, `geo_unit_width`, caps por sobre-merge) desde datos estandar, de modo que la PROFUNDIDAD del arbol (cuantos tiers, si existe mid-tier) se vuelve DATA self-pinning en vez de un doble-JOIN ES-shaped [VERIFIED:527-529]. Uso build/config-time, no hot path, asi que el data-use LGPL es non-issue [VERIFIED:532]; alternativa estricta-permisiva: `iso3166` (MIT) + iso-codes raw JSON [VERIFIED:531]. **Sustrato companero:** loader N-niveles desde GeoNames (ADM1->province, **ADM2->comarca[nullable]**, ADM3/4->municipality) — CC-BY 4.0, €0 — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377], que modela EXPLICITAMENTE el mid-tier como nullable, el aplanado exacto que esta faceta necesita.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f6"></a>

### Faceta 6 · admin_level_1: neutralizar ccaa → {code,label}

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/routers/geo.py:369-371` [VERIFIED] — el handler `province_inventory_tree` lee **solo dos columnas ES-administrativas** via un unico fetchrow:
  `prov = await c.fetchrow("SELECT code, name, ccaa_code, ccaa_name FROM geo_province WHERE code=$1", province_code)`.
- `services/api/routers/geo.py:418-420` [VERIFIED] — y las re-emite **verbatim** como claves JSON del contrato:
  `tree = {"province": {"code": prov["code"], "name": prov["name"], "ccaa_code": prov["ccaa_code"], "ccaa_name": prov["ccaa_name"]}, ...}`.
- `migrations/0001_geo.sql:7-8` [VERIFIED] — `ccaa_code CHAR(2) NOT NULL`, `ccaa_name TEXT NOT NULL`: toda fila de provincia ES **siempre** tiene ambos (jamas NULL), por eso el leak es invisible en ES.
- `migrations/0052_country.sql:51` [VERIFIED] — `geo_province ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'`: la dimension pais YA existe en la tabla base.
- `migrations/0053_country_onboarding.sql:75` [VERIFIED] — `geo_province_pkey PRIMARY KEY (country_code, code)`: PK ya compuesto; el `WHERE code=$1` del fetchrow es por tanto **monocolumna sobre un PK compuesto** (costura compartida con faceta 4).
- `country_registry` y la columna `admin1_label` **NO EXISTEN** [VERIFIED — grep `admin1_label|admin_level_1|country_registry|admin1` sobre `migrations/` = 0 matches]. No hay fuente generica del label hoy.

**(b) El mecanismo al atomo**
El arbol de provincia fija **dos leaks ortogonales** en el mismo punto:
1. **Leak de FORMA (clave de salida):** las claves JSON `ccaa_code`/`ccaa_name` exponen el concepto administrativo espanol "Comunidad Autonoma". El NIVEL (admin1 = primera division subnacional) es universal; lo que difiere es su ETIQUETA (ES=Comunidad Autonoma, DE=Bundesland, FR=Region, IT=Regione). Un consumidor pan-EU recibe una clave `ccaa_*` que no tiene sentido para DE/FR.
2. **Leak de FUENTE (de donde sale el label):** el valor `ccaa_name` es por-fila (p.ej. "Comunidad de Madrid") y vive NOT NULL en `geo_province` solo para ES; no hay tabla declarativa (`country_registry`) que provea ni el sustantivo-de-nivel ("Comunidad Autonoma" vs "Bundesland") ni el label por pais.

El valor en si (el codigo ccaa y el nombre de la ccaa de cada provincia) es un dato legitimo; **el pecado es el nombre de la clave y la ausencia de una fuente de nivel por pais**.

**(c) Costura ES->generico**
El `fetchrow` y el dict de respuesta cablean `ccaa` como columna leida Y como clave emitida. Ademas el `SELECT ... WHERE code=$1` es monocolumna: tras 0053 (PK `(country_code,code)`) necesita `country_code` para no leer la provincia de otro pais (solapa faceta 4, pero la **neutralizacion del label** es el atomo propio de la 6).

**(d) Fix exacto**
1. **Renombrar la forma de salida** a un contrato neutro: emitir
   `"admin_level_1": {"code": prov["ccaa_code"], "label": prov["ccaa_name"]}`
   en lugar de `ccaa_code`/`ccaa_name`. **ES sigue emitiendo los MISMOS valores** bajo la clave generica: el dato no cambia, solo la clave.
2. **Sustantivo de nivel desde `country_registry`** (faceta 26): anadir un campo de meta `admin_level_1_noun` poblado por `SELECT admin1_label FROM country_registry WHERE country_code=$cc` con la fila ES = `'Comunidad Autonoma'`, DE = `'Bundesland'`, FR = `'Region'`. El VALOR por-provincia (`admin_level_1.label`) sigue saliendo de `geo_province`; el SUSTANTIVO-de-nivel sale del registry.
3. **Threadear `country_code`** en el lookup `geo_province` (de `WHERE code=$1` a `WHERE country_code=$cc AND code=$1`), tomando el `$cc` de la faceta 16 (dimension-pais en la request), default `'ES'` ancla.

**(e) Criterio de sellado + verificacion multi-via**
- **Snapshot OpenAPI golden (faceta 30 / oasdiff):** la forma de `/geo/{prov}/tree` debe exponer `admin_level_1{code,label}` y NO `ccaa_*`; CI falla ante cualquier deriva de clave.
- **Golden ES byte-identico:** para una provincia ES, `admin_level_1.code`/`.label` == los valores `ccaa_code`/`ccaa_name` de hoy (cero regresion del dato).
- **Fixture multi-pais (DE/FR):** una provincia DE sembrada emite `admin_level_1_noun = "Bundesland"` desde registry, **no** el ES por defecto, **no** NULL.
- **Cross-check ISO 3166-2 (pycountry):** el manifest de conteo/ancho de admin1 derivado de la norma reproduce las 52 provincias ES y los 16 Bundeslaender DE conocidos (2a via independiente).

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**pycountry — ISO 3166-2 subdivision authority** [VERIFIED `NEXT-LEVEL.md:530`; https://github.com/pycountry/pycountry; LGPL-2.1; EUR0=True]. Convierte el grano/ancho/etiqueta de admin1 de **sentinela ES** a **dato de norma**: el conteo y el code-width de las subdivisiones de nivel-1 de CADA pais se vuelven datos que alimentan el seal manifest y la semilla de `country_registry` [VERIFIED:528-529]. Uso build/config-time (no en hot path), por lo que el dato LGPL es no-issue; postura estrictamente permisiva: `iso3166` (MIT) + el JSON crudo iso-codes [VERIFIED:531-532]. **Complemento:** Frictionless Table Schema [VERIFIED:337, MIT] para validar la fila del country-pack (ancho/forma de `admin1_label`) ANTES del INSERT, cerrando el "value too long for type character(n)" a mitad de seed [VERIFIED:335-336].

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** geo.py:369-371 lee ccaa_code/ccaa_name de geo_province y geo.py:418-420 las re-emite como claves JSON 'ccaa_*' (concepto admin ES). Ademas no hay country_registry/admin1_label (grep=0) que provea el label de nivel por pais, y el fetchrow es monocolumna (WHERE code=$1) sobre PK compuesto (country_code,code) de 0053.
- **Fix — propuesta [no implementada].** Renombrar la salida a admin_level_1{code,label} (ES emite los MISMOS valores ccaa_* bajo clave generica, dato sin cambio); poblar el sustantivo de nivel (Comunidad Autonoma/Bundesland/Region) desde country_registry por country_code; y threadear country_code al lookup geo_province (WHERE country_code=$cc AND code=$1).
- **Adversarial (DE/FR/IT/PT/no-UE).** Cualquier no-ES: el cliente pan-EU recibe la clave 'ccaa_*' sin sentido para DE/FR; y un onboarding sin la fila country_registry deja el label NULL o cae al ES por defecto, rompiendo el sustantivo de nivel.
- **Sellado + verificación multi-vía.** Snapshot OpenAPI (oasdiff) pinea admin_level_1{code,label} y rompe CI ante 'ccaa_*'; golden ES byte-identico (mismo code/label que ccaa_* hoy); fixture DE emite noun 'Bundesland' desde registry (no ES, no NULL); cross-check ISO 3166-2 reproduce 52 ES / 16 DE.
- **Herramienta NEXT-LEVEL (€0).** pycountry (ISO 3166-2 subdivision authority) [VERIFIED NEXT-LEVEL.md:530; https://github.com/pycountry/pycountry; LGPL-2.1; EUR0] — grano/ancho/label de admin1 como dato de norma, build-time (LGPL no-issue); alt permisiva iso3166 MIT + iso-codes JSON [VERIFIED:531-532]; complemento Frictionless Table Schema [VERIFIED:337] valida ancho de admin1_label pre-INSERT.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f7"></a>

### Faceta 7 · Taxonomía entity_kind: mapeo nativo→compartido

**(a) Verificacion de code_hints [VERIFIED]**
- **Arbol /geo/{prov}/tree**: la query agrega con **9** literales de `entity_kind` cableados como `count(*) FILTER (WHERE e.kind='<literal>')` [VERIFIED services/api/routers/geo.py:378-386]: `compraventa`, `concesionario_oficial`(→clave `oficial`), `desguace`, `plataforma`, `garaje`, `subasta`, `oem_vo_portal`, `importador`, `rent_a_car_vo`. El hint decia "10x"; son 9 FILTER + el total `count(e.entity_ulid) AS entities` [VERIFIED geo.py:377].
- **Mismos literales = CLAVES JSON de salida** [VERIFIED geo.py:406-410]: `compraventa/oficial/desguace/plataforma/garaje/subasta/oem_vo_portal/importador/rent_a_car_vo`. No hay capa de mapeo: la taxonomia ES nativa ES el contrato de cable.
- **/stats dealers**: scope distinto — `WHERE e.kind::text NOT IN ('particular','desguace')` [VERIFIED services/api/stats.py:26].
- **Numerador del SELLO venta**: scope AUN mas estrecho — `WHERE e.kind IN ('compraventa','concesionario_oficial')` [VERIFIED migrations/0042_province_seal_view.sql:24 y migrations/0043_province_seal_desguace.sql:22]. Sello DESGUACE: `WHERE e.kind='desguace'` [VERIFIED 0043:34].
- **Enum**: `entity_kind` declara 11 labels [VERIFIED migrations/0005_types_and_guards.sql:13-17] (concesionario_oficial, agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta, importador, oem_vo_portal, plataforma, cadena[deprecated]); `particular` se anade despues por `ALTER TYPE entity_kind ADD VALUE` [VERIFIED migrations/0017_particular_kind.sql:21]. Total 12 labels vivos.

**(b) Mecanismo al atomo**
PostgreSQL evalua cada `count(*) FILTER (WHERE e.kind='compraventa')` por grupo `GROUP BY co.id,...,m.code,m.name` [geo.py:392]; el literal es una etiqueta del enum comparada por igualdad. Los 9 literales viven DOS veces: como texto SQL y, verbatim, como claves de un `dict` Python en la respuesta JSON [geo.py:404-410]. El sello reduce "punto de venta certificable" a un subconjunto de **2** literales en su WITH numerador. No existe tabla de mapeo ni enum->clave; la taxonomia espanola es simultaneamente el predicado, el nombre de columna y la clave de salida.

**Hallazgo de precision (pre-multi-pais):** `agente_oficial` es un label REAL del enum [0005:14] pero tiene **0 uso** en `services/` [VERIFIED grep agente_oficial services/ = vacio]. Un dealer `agente_oficial` se cuenta en el total `entities` [geo.py:377] pero NO tiene bucket de kind en el arbol y queda FUERA del numerador del sello (que solo suma compraventa+concesionario_oficial). La perdida de taxonomia ya existe dentro de ES. Ademas hay TRES scopes de "punto de venta" divergentes (arbol 9 literales + `<>particular`; /stats `NOT IN(particular,desguace)`; sello `IN(compraventa,concesionario_oficial)`) — same-concept-three-scopes ENCIMA del acoplamiento de literal ES.

**(c) Costura ES->generico + fix exacto**
Un mercado con tipos nativos ausentes del enum compartido (DE: *Autohaus* / *freier Haendler* / *Vertragshaendler*; FR: *concessionnaire* / *mandataire* / *agent*; IT: *concessionaria* / *salone*) no mapea: o colapsa a un label compartido incorrecto (pierde la distincion nativa), o cae fuera de los 9 FILTER y del numerador de 2 literales → contado en `entities` total pero **cero** en cada bucket de kind y **cero** en el sello. Las claves JSON siguen en castellano, sin sentido para DE/FR.

**Fix:**
1. Tabla/seed `entity_kind_map(country_code, native_label, shared_kind)` + presentacion `shared_kind -> {output_key estable = el propio valor del enum, display_label[country]}` (display desde country_registry, x-ref faceta 26).
2. Generar las columnas FILTER del arbol ITERANDO el conjunto del enum compartido (no 9 literales a mano), emitiendo TODOS los labels incluido `agente_oficial` (cierra la perdida ES).
3. Unificar el scope "punto de venta" en UN solo predicado `is_sales_point(shared_kind)` reusado por arbol, /stats y sello (x-ref faceta 2 `v_servable_dealer`), retirando los 3 scopes divergentes.
4. ES byte-identico: seed del mapa ES como identidad (cada label ES → si mismo) + golden que fija las claves de salida ES.

**(d) Riesgo adversarial concreto**
- **DE**: *freier Haendler* sin equivalente → mapeado a `compraventa` (lossy) o descartado; si el sello mantiene `IN('compraventa','concesionario_oficial')`, un mercado DE mayoritariamente garaje/subasta/importador reporta numerador ~0 → **veredicto GAP falso para el pais entero**.
- **FR**: *mandataire auto* (canal de alto volumen) no mapea → invisible en buckets del arbol y en el sello.
- **agente_oficial** ya prueba el bug HOY en ES (sin bucket, fuera del numerador) [VERIFIED].
- **Output-key rot**: un consumidor DE recibe claves `subasta`/`oem_vo_portal` en espanol; un cliente pan-EU no puede keyear de forma estable.

**(e) Sellado + verificacion multi-via**
- **Criterio**: cada label activo del enum tiene exactamente 1 bucket en el arbol; suma de buckets + residual sin-bucket == total `entities` (conservacion, sin descarte silencioso); `is_sales_point` devuelve el MISMO row-set en arbol/stats/sello para un pais (invariante de scope unico, gate H3 de faceta 2).
- **Via 1 HTTP-vs-SQL**: suma de buckets de la respuesta == `GROUP BY kind` crudo via asyncpg; residual de labels sin bucket == 0.
- **Via 2 Pydantic CI**: `entity_kind_map` valida como manifest tipado; biyeccion native↔shared y todo shared con output_key (0 UNMAPPED / 0 ORPHAN), espejo del guard de registry-drift.
- **Via 3 oasdiff/Schemathesis**: congelar el set de claves JSON del arbol como contrato country-invariante; anadir DE no renombra una clave (clave ES `compraventa` estable) ni 500ea ante un label ausente en un pais.
- **Via 4 golden ES**: respuesta del arbol para una provincia fijada byte-identica antes/despues del refactor.

**(f) Herramienta NEXT-LEVEL**
**Pydantic** (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela `entity_kind_map`/country-pack como contrato tipado con validators de coherencia y un test de CI que asevera la biyeccion native↔shared↔output_key por pais activo = 0 UNMAPPED / 0 ORPHAN, convirtiendo el acoplamiento de literal ES en un build ROJO [NEXT-LEVEL.md:584-590]. Emparejar con **oasdiff** (Apache-2.0) — https://github.com/oasdiff/oasdiff [VERIFIED NEXT-LEVEL.md:836] para gatear el set de claves JSON del arbol como frontera de breaking-change country-invariante. Alternativa si el mapa se entrega como dato versionado, no tipos: **Frictionless** (MIT) — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337].

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** Los 9 literales de entity_kind del arbol (geo.py:378-386) son a la vez predicado SQL y clave JSON de salida, y el sello reduce 'punto de venta' a 2 literales ES (compraventa+concesionario_oficial, 0042:24/0043:22); un mercado DE/FR/IT con tipos nativos distintos no mapea, cae fuera de los buckets y del numerador, y recibe claves en castellano. Ya en ES, agente_oficial (label real del enum) no tiene bucket ni entra al numerador.
- **Fix — propuesta [no implementada].** Introducir entity_kind_map(country_code,native_label,shared_kind) + presentacion shared_kind->{output_key=valor del enum, display_label[country]}; generar las columnas FILTER iterando el enum (emitiendo TODOS los labels, incl. agente_oficial); unificar el scope 'punto de venta' en un unico is_sales_point() reusado por arbol/stats/sello (x-ref faceta 2). ES identidad + golden de claves.
- **Adversarial (DE/FR/IT/PT/no-UE).** DE mayoritariamente garaje/subasta/importador con sello IN(compraventa,concesionario_oficial) → numerador ~0 → veredicto GAP falso del pais entero; FR mandataire y DE freier Haendler invisibles en buckets y sello; claves JSON en espanol sin sentido pan-EU. agente_oficial ya prueba la perdida en ES hoy.
- **Sellado + verificación multi-vía.** Criterio: 1 bucket por label activo, suma+residual==entities (conservacion), is_sales_point devuelve el mismo row-set en arbol/stats/sello. Via1 HTTP-vs-SQL (buckets==GROUP BY kind crudo, residual==0). Via2 Pydantic CI biyeccion 0 UNMAPPED/0 ORPHAN. Via3 oasdiff/Schemathesis congela claves JSON country-invariantes. Via4 golden ES byte-identico.
- **Herramienta NEXT-LEVEL (€0).** Pydantic (MIT) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587] — contrato tipado del kind-map + CI bijection 0 UNMAPPED/0 ORPHAN; + oasdiff (Apache-2.0) https://github.com/oasdiff/oasdiff [VERIFIED NEXT-LEVEL.md:836] congela las claves JSON; alt Frictionless (MIT) https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f8"></a>

### Faceta 8 · /geo/completeness por país (full_pct + geo_grid)

**(a) Code_hints verificados**
- **[VERIFIED services/api/routers/geo.py:32-89]** handler `geo_completeness` (RATE_EXPENSIVE [:33], cached [:42-44]).
- **e_total [VERIFIED :51]** `SELECT count(*) FROM entity WHERE kind <> 'particular'` — lee la **tabla `entity` directamente** (NO `servable_entity`), **sin predicado pais**.
- **e_full [VERIFIED :52-54]** exige `province_code IS NOT NULL AND municipality_code IS NOT NULL AND comarca_id IS NOT NULL` -> "full" = **4-tier ES** (prov+comarca+muni). El atado a `comarca_id IS NOT NULL` esta en **:54**.
- **e_no_comarca_city [VERIFIED :55-57]**, **e_prov_only [VERIFIED :58-60]**, **e_no_geo [VERIFIED :61-62]** — todos `FROM entity WHERE kind<>'particular'`, sin pais.
- **v_total [VERIFIED :63]** `count(*) FROM vehicle`; **v_full [VERIFIED :64-67]** `JOIN entity` exigiendo `e.comarca_id IS NOT NULL` (:67).
- **geo_grid [VERIFIED :68-74]** cuenta `geo_province` (:69), `geo_comarca` (:70), `geo_municipality` (:71), `municipalities_with_comarca` (:72-73) **SIN filtro de pais** — un total global unico.
- **[VERIFIED migrations/0052_country.sql:39-41]** nota (e): `geo_comarca` **no tiene columna `code`** (PK=`id`, UNIQUE=`(province_code,name)`); la **comarca es una division SOLO espanola**. Las 3 tablas geo tienen `country_code` (**[VERIFIED 0052:51-53]**).

**(b) Mecanismo al atomo**
7 `COUNT(*)` secuenciales sobre `entity`+`vehicle` completas, cacheado RATE_EXPENSIVE [:33]. Produce el reporte nacional de completitud **de DEALERS** (scope `kind<>'particular'` [:49-50,78], coherente con `/geo/{prov}/entities` y `/tree`): conteos por granularidad geo (full / no_comarca_city / prov_only / no_geo), `full_pct`, y un `geo_grid` con los tamanos de las tablas backbone. "full" se define como **prov+comarca+muni** presentes (:54), i.e. la jerarquia 4-tier ES `pais->provincia->comarca->ciudad`.

**(c) Costura ES->generico**
Dos supuestos ES rompen para un pais sin comarca o coexistiendo:
1. **"full" exige `comarca_id IS NOT NULL`** (:54,:67) — comarca es Spain-only **[VERIFIED 0052:39-41]**; un dealer DE/FR/IT/PT tiene SIEMPRE `comarca_id NULL` -> `full_pct=0%` para el pais entero.
2. **`geo_grid` (:69-73) cuenta TODAS las provincias/comarcas/municipios sin filtro** -> con 2+ paises es **un total mezclado unico**, sin sentido por pais.
Ningun `COUNT` lleva predicado pais -> con un 2o pais el reporte fusiona ES+CC. (Matiz: `e_total` lee `entity` directo, que ya tiene `country_code` [VERIFIED 0052:54], asi que el predicado es viable sin depender de la faceta 1; aun asi conviene coherencia con `servable_entity`.)

**(d) Riesgo adversarial**
**Alemania:** `full_pct` reporta **0% de cobertura geo de dealers** (nadie tiene comarca) — CRITICAL, senal falsa: el pais aparenta geo-vacio cuando esta geocodificado a prov+muni. **IT/PT/FR:** mismo `comarca`-NULL -> 0% full; ademas `geo_grid` suma DE+ES+IT en un unico entero "provinces" que describe a ningun pais. **No-UE/ruido:** un pais con mid-tier distinto (p.ej. county US) colapsa mal en la logica comarca o desaparece de "full".

**(e) Criterio de sellado + verificacion multi-via**
1. **Numerico por pais:** `/geo/completeness?country=DE` da `full_pct>0` sobre fixture DE donde todo dealer tiene prov+muni (prueba comarca desacoplada).
2. **HTTP-vs-SQL** (patron [VERIFIED tests/test_api_gaps.py:50-61]): cada uno de los 7 conteos = query asyncpg cruda independiente con el mismo predicado pais.
3. **ES byte-identico:** `?country=ES` (o default) == numeros vivos actuales (golden).
4. **Aislamiento geo_grid:** con DE sembrado en txn revertida, los conteos ES del grid inalterados (patron [VERIFIED tests/test_country_coexistence.py:416-458]).

**(f) Herramienta NEXT-LEVEL**
**zachasme/h3-pg — Apache-2.0** — https://github.com/zachasme/h3-pg **[VERIFIED NEXT-LEVEL.md:788]**, via *coverage-cube-h3-matview* **[VERIFIED NEXT-LEVEL.md:785-791]**. Eleva la completitud atada-a-comarca a un **cubo de cobertura H3 country-agnostico** (conteo / %sello / freshness / densidad por celda H3 x resolucion x `country_code`, computado desde lat/lon dentro de Postgres): la **profundidad administrativa deja de importar**, asi un pais sin comarca reporta cobertura REAL en vez de 0%. Companero: **sraoss/pg_ivm — PostgreSQL License** — https://github.com/sraoss/pg_ivm **[VERIFIED NEXT-LEVEL.md:764]** (IMMV) auto-refresca el cubo/agregado en O(delta) sin REFRESH manual, matando el coste de los 7 COUNT secuenciales. Ambos EUR0, intra-Postgres.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** Los 7 COUNT(*) de /geo/completeness (geo.py:51-73) no llevan predicado pais, y 'full' esta atado a comarca_id IS NOT NULL (:54,:67) — comarca es division SOLO ES (0052:39-41, geo_comarca sin columna code). geo_grid (:69-73) suma todas las prov/comarca/muni sin filtrar pais.
- **Fix — propuesta [no implementada].** Anadir country_code=$cc a los 7 COUNT(*) (entity.country_code existe 0052:54; vehicle via JOIN entity). Desacoplar 'full' de comarca: definirlo por la profundidad admin declarada del pais (country_registry/GeoProfile) -> pais sin comarca: full=prov+muni, comarca como mid-tier opcional/colapsable (acopla faceta 5). Filtrar geo_grid por country_code (las 3 tablas lo tienen 0052:51-53). Exponer country en meta. ES-default reproduce numeros actuales.
- **Adversarial (DE/FR/IT/PT/no-UE).** Alemania: full_pct=0% cobertura geo de dealers (nadie tiene comarca) -> CRITICAL senal falsa de pais geo-vacio. IT/PT/FR: mismo 0% full por comarca-NULL; geo_grid suma DE+ES+IT en un entero 'provinces' que describe a ningun pais. No-UE: mid-tier distinto colapsa mal o desaparece de 'full'.
- **Sellado + verificación multi-vía.** (1) /geo/completeness?country=DE da full_pct>0 sobre fixture prov+muni (comarca desacoplada). (2) HTTP-vs-SQL (test_api_gaps.py:50-61): cada conteo = query asyncpg cruda con predicado pais. (3) ES byte-identico vs numeros vivos (golden). (4) DE en txn revertida no cambia el geo_grid ES (test_country_coexistence.py:416-458).
- **Herramienta NEXT-LEVEL (€0).** zachasme/h3-pg — Apache-2.0 [VERIFIED NEXT-LEVEL.md:788] — https://github.com/zachasme/h3-pg (coverage-cube-h3-matview): cubo de cobertura H3 country-agnostico (conteo/%sello/freshness/densidad por celda x resolucion x country_code), profundidad admin irrelevante -> pais sin comarca reporta cobertura real. Companero pg_ivm PostgreSQL License [VERIFIED:764] para frescura O(delta) sin REFRESH. EUR0 intra-PG.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f9"></a>

### Faceta 9 · v_province_seal: country-scoping del segmento VENTA

**(a) code_hints VERIFICADOS**
- **Numerador agrupado SOLO por provincia** [VERIFIED migrations/0042_province_seal_view.sql:18-28]: `WITH num AS (SELECT e.province_code, count(DISTINCT COALESCE(vdr.resolved_ulid,e.entity_ulid)) AS numerator FROM entity e LEFT JOIN v_dealer_resolved vdr ... WHERE e.kind IN ('compraventa','concesionario_oficial') AND e.province_code IS NOT NULL AND EXISTS(vehicle available) GROUP BY e.province_code)` — sin country_code.
- **Join al denominador por province_code solo** [VERIFIED 0042:42-44]: `FROM denominator_estimate d LEFT JOIN num n ON n.province_code=d.province_code WHERE d.segment='venta'`.
- **0043 redefine el view, rama venta byte-identica** [VERIFIED migrations/0043_province_seal_desguace.sql:16-52]: venta_num agrupa por `e.province_code`; UNION ALL con la rama desg (tambien province_code-only, 0043:28-36).
- **El endpoint lee el view plano** [VERIFIED services/api/routers/geo.py:112-114]: `SELECT province_code, segment, denominator, numerator, coverage_pct, verdict FROM v_province_seal ORDER BY segment, province_code`. La agregacion nacional [VERIFIED geo.py:124-141] suma numerador y (si den) denominador por **segment**, sin distinguir pais.
- **El denominador YA tiene country** [VERIFIED migrations/0053_country_onboarding.sql:53]: `ALTER TABLE denominator_estimate ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'`, con FK compuesta (country_code,province_code)->geo_province(country_code,code) [VERIFIED 0053:141-147]. Y el PK de geo_province es compuesto (country_code,code) [VERIFIED 0053:75].

**(b) El mecanismo al atomo**
El sello VENTA = dealers canonicos servidos con stock (numerador) / techo registral DIRCE CNAE-451 (denominador), umbral SELLADO>=85 / PARCIAL 50-85 / GAP <50 [VERIFIED 0042:36-41]. La dedup canonica `COALESCE(vdr.resolved_ulid,e.entity_ulid)` es obligatoria (entity_ulid crudo sobre-cuenta ~2x: 164.9% vs el correcto 79.4% nacional) [VERIFIED 0042:8-12]. Atomo de fallo: la llave de agrupacion y de join es `province_code` mono-columna mientras los datos ya viven en un espacio (country_code, province_code) desde 0053. La rama desguace replica el defecto (GROUP BY e.province_code, 0043:35).

**(c) Costura ES->generico**
denominator_estimate.country_code existe (0053:53) pero el view lo ignora: ni lo selecciona, ni lo agrupa, ni lo une. El fix es cerrar esa asimetria entre el dato (que ya es por pais) y el view (que aun no).

*Costura, fix, adversarial, sellado y herramienta NEXT-LEVEL: en la **Ficha operativa** inmediatamente debajo.*

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El CTE numerador agrupa solo por e.province_code (0042:28, 0043:26) y el join al denominador es ON province_code solo (0042:43), aunque denominator_estimate ya lleva country_code desde 0053:53 y geo_province tiene PK compuesto (country_code,code) desde 0053:75. Provincias con el MISMO codigo en distintos paises colapsan en UNA fila y unen un numerador mixto a un denominador ajeno.
- **Fix — propuesta [no implementada].** CREATE OR REPLACE VIEW v_province_seal: (1) anadir e.country_code al SELECT y GROUP BY del venta_num CTE -> GROUP BY (country_code, province_code); (2) anadir d.country_code al SELECT externo; (3) cambiar el join a `ON n.country_code=d.country_code AND n.province_code=d.province_code`; (4) mismo tratamiento en la rama desg (anadir e.country_code). Exponer country_code como columna. En geo.py: anadir country_code al SELECT (geo.py:112-114) y rekeyar la agregacion nacional por (country_code, segment) en vez de segment (geo.py:124-141); meta expone country. ES byte-identico: con todo country_code='ES' la agrupacion (ES,prov) es relabel 1:1, nacional venta sigue ~79.4%.
- **Adversarial (DE/FR/IT/PT/no-UE).** Italia: provincias que comparten codigo numerico con ES suman dealers IT+ES en una fila contra el denominador ES, dando un coverage sin sentido y un veredicto SELLADO/PARCIAL/GAP FALSO. El roll-up nacional (geo.py:133-141) entonces doble-cuenta el numerador del codigo compartido. PT/FR identico. Ruido: un denominador NULL de un pais sin DIRCE se mezcla con numerador de otro y enmascara el NO_DENOM correcto.
- **Sellado + verificación multi-vía.** Criterio: cada fila de sello es mono-pais y su veredicto es estable bajo coexistencia. Multi-via: (a) golden ES — coverage_pct por provincia y nacional 79.4% byte-identicos pre/post; (b) no-bleed — sembrar IT con provincia codigo '28', asertar que la fila ES-28 excluye entidades IT y que IT-28 tiene su propia fila (txn coexistencia revertida); (c) 2a via — recompute SQL crudo de numerador/denominador por (country,province) coincide con el view; (d) pureza de veredicto — el SELLADO del pais A no cambia al sembrar el pais B.
- **Herramienta NEXT-LEVEL (€0).** great-expectations (Contrato de datos PRE-sello) — Apache-2.0 [VERIFIED NEXT-LEVEL.md:167] — https://github.com/great-expectations/great_expectations . Una suite de expectativas PRE-seal asegura la precondicion oculta antes de seal.compute: (country_code, province_code) es el grano de join (ningun province_code colapsa cross-country en una fila de sello); el country del numerador casa el del denominador; ningun source_key cae en silencio. Falla CERRADO: una expectativa violada NIEGA sellar ese estrato — espejo mecanico del invariante COUNTRY-PROOF, no revision humana.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f10"></a>

### Faceta 10 · Denominador VENTA: fuente + loader por país

**(a) Code_hints VERIFICADOS leyendo la fuente real**
- [VERIFIED scripts/load_denominator_provincia.py:34-38] el denominador VENTA es DIRCE CNAE-451 (techo registral ES): `RATIO_451_45 = 23085 / 88621` (= 0.2605), `CSV_PATH = ROOT/data/official/denominador_cnae45_provincia_2024.csv`, DSN cableada 127.0.0.1:5433.
- [VERIFIED load_denominator_provincia.py:53] `den_venta = round(cnae45 * RATIO_451_45)`.
- [VERIFIED load_denominator_provincia.py:64-65] guardia ES `if len(rows) != 52: raise SystemExit(... refusing to load a partial set)`.
- [VERIFIED load_denominator_provincia.py:88-94] `INSERT INTO denominator_estimate (segment, province_code, method, n1, point_est, ci_low, ci_high, sources_used, evidence_uri) VALUES ('venta', $1, 'registral_ceiling', ...)` — country_code NO esta en la lista de columnas.
- [VERIFIED migrations/0026_verification_deep.sql:250-266] tabla denominator_estimate; `province_code CHAR(2) REFERENCES geo_province(code)  -- NULL = nacional` (linea 253); method CHECK incluye 'registral_ceiling' (linea 255).
- [VERIFIED migrations/0053_country_onboarding.sql:53] `ALTER TABLE denominator_estimate ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'`; y [VERIFIED 0053:141-145] la FK se reconstruye compuesta `(country_code, province_code) REFERENCES geo_province (country_code, code)`.

**(b) Mecanismo al atomo**
El sello VENTA = numerador_canonico_servido / techo_registral_DIRCE-451 por provincia; veredicto SELLADO>=85% / PARCIAL 50-85% / GAP<50% [VERIFIED geo.py:108]. El denominador vive en denominator_estimate, una fila por (segment='venta', province_code) con method='registral_ceiling', point_est=round(cnae45_locales * 0.2605). El loader lo deriva de UN ratio nacional (DIRCE grupo 451 / division 45 = 23085/88621) aplicado a un conteo de locales CNAE-45 por provincia desde un CSV ES (DIRCE 2025 tabla 301). Es el artefacto MAS COSTOSO de toda la etapa y el que el country-pack del diseno ({country_code, admin1_label, display_name}) OMITE.

**(c) Costura ES->generico + fix exacto**
Tres soldaduras ES:
1. FUENTE: DIRCE CNAE-451 es registral espanol. Fix = contrato de adaptador: por pais, identificar el conteo registral/estadistico equivalente de establecimientos de venta de coches. Para la UE = **Eurostat SBS, NACE G45.1** (venta de vehiculos), equivalente transfronterizo libre del techo DIRCE. No-UE (MX/JP) usa el equivalente de su oficina estadistica nacional o un denominador declarado-asumido explicito.
2. LOADER: load_denominator_provincia.py cablea el ratio ES, la ruta CSV ES y un ABORT `len != 52` (provincias ES). Generalizar a `load_denominator(country_code)`: leer data/<cc>/denominator/*.csv, el ratio del pais (o su 451/45 desde su SBS) y validar contra el conteo de admin1 de country_registry, no el literal 52. FIX ATOMICO CRITICO: el INSERT (lineas 88-94) OMITE country_code, asi que toda fila cae a country_code='ES' por DEFAULT [VERIFIED 0053:53]. Para una carga no-ES esto etiqueta denominadores PT/DE como 'ES', y la FK compuesta (country_code, province_code)->geo_province los RECHAZA (los codigos PT no existen bajo ES) -> abort a media carga. Fix: anadir country_code como 1a columna del INSERT y bindear $cc.
3. CONTRATO: denominator_estimate.country_code YA existe y YA esta en la FK compuesta [VERIFIED 0053:141-145]; solo falta que el loader lo escriba y el view del sello agrupe por el (faceta 9).

**(d) Riesgo adversarial concreto**
Cualquier pais sin equivalente DIRCE cableado deja el segmento VENTA permanentemente NO_DENOM (point_est NULL/0 -> el CASE de 0042 devuelve NO_DENOM), el sello nacional es incomputable y el dashboard malinterpreta NO_DENOM como 'pendiente' (faceta 13). Peor: si el loader corre para PT sin el fix de country_code, estampa denominadores PT como 'ES' y la FK compuesta aborta a media carga, dejando un set parcial.

**(e) Criterio de sellado + verificacion multi-via**
1. Denominador por pais presente: `count(*) FROM denominator_estimate WHERE segment='venta' AND country_code=$cc` == nº provincias del pais; sum(point_est) dentro de la banda de triangulacion del ancla nacional.
2. Triangulacion 2a via: el techo VENTA por pais cruzado contra un ancla INDEPENDIENTE (conteo GLEIF/LEI de entidades NACE-automocion del pais, o el total SBS) aterriza N en banda 0.7-1.4, o se marca distrust.
3. ES byte-identico: re-correr el loader ES reproduce las filas segment='venta' exactas (sum point_est inalterado); sello ES ~79.4%.
4. Fail-closed: una fila con province_code ajeno al geo_province del pais la rechaza la FK compuesta (guard mecanico), y un pais sin denominador da NO_DENOM explicito, jamas una cobertura fabricada.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
[VERIFIED NEXT-LEVEL.md:188-194] **Eurostat Structural Business Statistics (SBS, NACE G45)** (Reutilizacion libre, Decision 2011/833/EU + atribucion [VERIFIED], EUR0) — https://ec.europa.eu/eurostat/web/structural-business-statistics — el equivalente transfronterizo del techo DIRCE CNAE-451 que EXISTE para todo pais UE dia-uno, convirtiendo el denominador de un CSV en un PANEL de anclas independientes. Reforzar [VERIFIED NEXT-LEVEL.md:172-178] con **GLEIF LEI Golden Copy** (CC0 1.0 [VERIFIED], https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) como 2o ancla registral de mecanismo distinto, y envolver el pack de denominador por pais en un contrato de datos **Frictionless Table Schema** [VERIFIED NEXT-LEVEL.md:334-340] (frictionless-py, MIT [VERIFIED], https://github.com/frictionlessdata/frictionless-py) para que un pack mal formado/ancho-corto falle la validacion ANTES del INSERT en vez de abortar a media carga.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El denominador VENTA es DIRCE CNAE-451 ES: ratio 23085/88621 [VERIFIED load_denominator_provincia.py:38], CSV ES [VERIFIED :35], ABORT len!=52 [VERIFIED :64-65], y el INSERT OMITE country_code -> default 'ES' [VERIFIED :88-94 + 0053:53]. Es el artefacto mas caro que el country-pack del diseno omite.
- **Fix — propuesta [no implementada].** Adaptador de fuente por pais (UE = Eurostat SBS NACE G45.1; no-UE = oficina estadistica o declarado-asumido). Generalizar load_denominator(country_code): CSV+ratio por pais, validar vs admin1 de country_registry (no 52). FIX CRITICO: anadir country_code como 1a columna del INSERT y bindear $cc (sino la FK compuesta 0053:141-145 rechaza filas no-ES). country_code ya existe y ya esta en la FK.
- **Adversarial (DE/FR/IT/PT/no-UE).** Pais sin DIRCE-equivalente -> VENTA permanentemente NO_DENOM, sello incomputable, dashboard lo lee como 'pendiente'. Si el loader corre para PT sin el fix, estampa denominadores como 'ES' y la FK compuesta aborta a media carga (set parcial).
- **Sellado + verificación multi-vía.** (1) count denominator_estimate venta por cc == nº provincias del pais, sum(point_est) en banda del ancla; (2) cross-check 2a via vs GLEIF/LEI o SBS en banda 0.7-1.4; (3) loader ES reproduce filas byte-identicas (sello ~79.4%); (4) FK compuesta rechaza province_code ajeno, NO_DENOM explicito si falta denominador.
- **Herramienta NEXT-LEVEL (€0).** [VERIFIED NEXT-LEVEL.md:188-194] Eurostat SBS NACE G45 (Reutilizacion libre Dec.2011/833/EU, EUR0) https://ec.europa.eu/eurostat/web/structural-business-statistics como equivalente del DIRCE; + GLEIF LEI Golden Copy (CC0 1.0) https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [NEXT-LEVEL.md:172-178]; + Frictionless Table Schema (MIT) https://github.com/frictionlessdata/frictionless-py [NEXT-LEVEL.md:334-340] como contrato pre-INSERT.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f11"></a>

### Faceta 11 · Denominador DESGUACE: censo de desguaces por país

**(a) Verificacion de code_hints [VERIFIED]**
- `migrations/0043_province_seal_desguace.sql:28-36` — CTE `desg`: `count(DISTINCT e.entity_ulid) AS numerator` (TODO desguace hallado) y `count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key = 'dgt_cat') AS denominator` (solo el subset del censo DGT-CAT). `LEFT JOIN entity_source es ON es.entity_ulid = e.entity_ulid` (:33). `WHERE e.kind = 'desguace' AND e.province_code IS NOT NULL` (:34). `GROUP BY e.province_code` (:35) — **SIN `country_code`**. [VERIFIED]
- `0043:61-65` — verdict desguace: `NO_DENOM` si `denominator IS NULL OR =0`; `SELLADO` si `numerator >= denominator`; else `GAP`. [VERIFIED]
- `0043:7-11` — el comentario de cabecera fija la fuente: numerator = `dgt_cat + aedra + overture + geo_sweep`, denominator = el subset `entity_source.source_key='dgt_cat'`; "Verified live 2026-06-16: 52/52 SELLADO (total 1895 >= census 1292)", spot-checks Madrid 48/98, Barcelona 76/116. `'dgt_cat'` es un literal ES cableado en el view. [VERIFIED]
- `services/api/routers/geo.py:99-101` (docstring de `geo_seal`) — "DESGUACE = discovery coverage: scrapyards found vs the DGT official census (SELLADO when found >= census)". `geo.py:107-110` — `_METHODS = {"venta": ..., "desguace": "found / DGT census (discovery; SELLADO when found>=census)"}`. [VERIFIED]
- `entity_source` es ES-only hoy (la unica fuente de censo cableada es `dgt_cat`). [VERIFIED via 0043:31]

**(b) Mecanismo al atomo**
La rama desguace mide COBERTURA DE DESCUBRIMIENTO, no de inventario (los CATs no publican schema.org). Por provincia:
- **Numerador** = `count(DISTINCT entity_ulid)` de todos los `kind='desguace'` (encontrados por cualquier fuente).
- **Denominador** = los que tienen una fila en `entity_source` con `source_key='dgt_cat'` (el censo oficial DGT de Centros Autorizados de Tratamiento espanol).
- `coverage_pct = round(100*num/NULLIF(den,0),1)`; **SELLADO** cuando `num>=den` (encontramos al menos el censo). El denominador entero es un literal de fuente: `FILTER (WHERE es.source_key='dgt_cat')`.

**(c) Costura ES->generico**
`'dgt_cat'` es el source_key del censo de UN pais (ES). La rama desguace (i) carece de eje `country_code` (GROUP BY province_code solo, 0043:35) y (ii) tiene el censo cableado a un literal ES. Es ademas el item MAS PESADO que el diseno omitio: el country_pack del diseno solo lista `{country_code, admin1_label, display_name}` y NO incluye el artefacto mas costoso (el censo de desguaces por pais).

**(d) Fix exacto**
1. **Parametrizar el censo**: reemplazar el literal `source_key='dgt_cat'` por un origen de censo resoluble por pais — opcion A: tabla `country_seal_source(country_code, segment, census_source_key)`; opcion B: bandera `entity_source.is_census BOOLEAN` que el loader del pais marca. El view filtra `FILTER (WHERE es.source_key = <census_key del pais>)` o `FILTER (WHERE es.is_census)`.
2. **Eje pais**: anadir `e.country_code` al SELECT y `GROUP BY` del CTE `desg`, y al join, igual que la rama venta de la faceta 9.
3. **Cargar el censo por pais** bajo ese source_key (en la UE: el registro nacional de plantas ELV/CAT autorizadas bajo la Directiva 2000/53/CE; cada Estado tiene su autoridad competente), **o** declarar el segmento N/A por pais con semantica explicita (faceta 13: NO_DENOM != pendiente).
4. **ES byte-identico**: con `'dgt_cat'` mapeado al census_key de ES, el FILTER resuelve el MISMO subset -> 52/52 SELLADO intacto.

**(d') Riesgo adversarial concreto**
- **Mexico / no-UE**: no hay equivalente `dgt_cat` cableado -> el FILTER da 0 filas -> `denominator=0` -> verdict `NO_DENOM` PERMANENTE para el pais entero; un dashboard lo lee como 'pendiente' (faceta 13).
- **Pais nuevo que carga desguaces sin marcar censo**: el numerador cuenta (encontrados) pero el denominador queda 0 -> NO_DENOM aunque la cobertura real sea alta.
- **DE/FR/IT/PT**: cada uno exige SU censo nacional de CATs cargado; sin el, el segmento desguace nunca certifica, y el sello nacional de ese pais es incomputable.

**(e) Sellado + verificacion multi-via**
- **Golden ES**: el view re-mapeado da 52/52 SELLADO, total 1895>=1292 byte-identico; cross-check vs `calc_spain_sealed.py` (Madrid 48/98, Barcelona 76/116, 0043:11).
- **Country-scoped**: con un 2o pais y su censo cargado, el CTE `desg` agrupa por (country_code, province_code) y el verdict del pais usa SU censo, no el de ES.
- **Fail-closed**: un pais sin censo cargado -> NO_DENOM EXPLICITO (no 'pendiente'), sellado por la faceta 13.
- **2a via (triangulacion)**: el conteo del census source por pais debe caer en banda contra un ancla externa independiente (Eurostat SBS establecimientos NACE E38.31 'dismantling of wrecks').

**(f) Herramienta NEXT-LEVEL**
**Panel de anclas de triangulacion MULTIPLES auto-minadas — Eurostat Structural Business Statistics** (Reutilizacion libre, Decision 2011/833/EU; atribucion [VERIFIED]) https://ec.europa.eu/eurostat/web/structural-business-statistics [NEXT-LEVEL.md:188-194]. Convierte el censo unico ES-bound (`dgt_cat`) en un denominador contrastado por N mecanismos independientes por pais (para desguace, la clase NACE E38.31 da el conteo de establecimientos de desmantelamiento por pais), de modo que ningun pais quede NO_DENOM por falta de un censo nacional cableado a mano. Alternativa registral dia-uno: **GLEIF LEI Golden Copy** (CC0 1.0 [VERIFIED], https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy, NEXT-LEVEL.md:172-178) filtrada por NACE de desguace = lista de plantas para cualquier pais. Para sellar la precondicion NO_DENOM como fail-closed: **Great Expectations** (Apache-2.0 [VERIFIED], https://github.com/great-expectations/great_expectations, NEXT-LEVEL.md:164-170).

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El denominador del segmento DESGUACE esta cableado a un literal de fuente ESPANOL: count(DISTINCT e.entity_ulid) FILTER (WHERE es.source_key='dgt_cat') (migrations/0043:31), via LEFT JOIN entity_source (0043:33), agrupado solo por province_code (0043:35) sin country_code. El numerador cuenta TODO desguace hallado (dgt_cat+aedra+overture+geo_sweep) pero el denominador es exclusivamente el censo DGT-CAT de ES. entity_source es ES-only. Es el artefacto mas costoso de la etapa, omitido por el country_pack del diseno.
- **Fix — propuesta [no implementada].** Parametrizar el origen del censo: tabla country_seal_source(country_code,segment,census_source_key) o bandera entity_source.is_census, y filtrar FILTER (WHERE es.source_key=<census_key del pais>) en lugar del literal 'dgt_cat' (0043:31). Anadir e.country_code al SELECT/GROUP BY del CTE desg. Cargar el censo nacional de desguaces por pais (registro ELV/CAT bajo Directiva 2000/53/CE) bajo ese source_key, O declarar el segmento N/A por pais con NO_DENOM explicito (faceta 13). ES: 'dgt_cat' mapeado al census_key de ES da 52/52 SELLADO byte-identico.
- **Adversarial (DE/FR/IT/PT/no-UE).** Mexico/no-UE: sin equivalente dgt_cat cableado, el FILTER da 0 filas -> denominator=0 -> NO_DENOM PERMANENTE para el pais entero, que un dashboard malinterpreta como 'pendiente'. Pais nuevo que carga desguaces sin marcar censo: numerador cuenta pero denominador=0 -> NO_DENOM con cobertura real alta. DE/FR/IT/PT: cada uno exige su censo nacional de CATs; sin el, el segmento desguace nunca certifica y el sello nacional es incomputable.
- **Sellado + verificación multi-vía.** Multi-via: (1) Golden ES: el view re-mapeado reproduce 52/52 SELLADO, 1895>=1292 byte-identico (cross-check calc_spain_sealed.py Madrid 48/98, Barcelona 76/116). (2) Country-scoped: con 2o pais+censo, desg agrupa por (country_code,province_code) y el verdict usa su censo. (3) Fail-closed: pais sin censo -> NO_DENOM explicito (no 'pendiente'). (4) Triangulacion: el census source por pais cae en banda contra Eurostat SBS NACE E38.31.
- **Herramienta NEXT-LEVEL (€0).** Panel de anclas MULTIPLES — Eurostat SBS (Reutilizacion libre, Decision 2011/833/EU [VERIFIED]) https://ec.europa.eu/eurostat/web/structural-business-statistics [NEXT-LEVEL.md:188]. Reemplaza el censo unico ES-bound por un denominador contrastado por N anclas independientes por pais (NACE E38.31 'dismantling of wrecks' da el conteo de desmanteladoras). Alt registral dia-uno: GLEIF LEI Golden Copy (CC0 1.0 [VERIFIED], gleif.org/.../download-the-golden-copy, NEXT-LEVEL.md:172). Fail-closed NO_DENOM: Great Expectations (Apache-2.0 [VERIFIED], NEXT-LEVEL.md:164).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f12"></a>

### Faceta 12 · v_exhaustiveness_seal: durabilidad y monotonía por país

**(a) Code_hints verificados a la fuente real**
- **El view sirve UN solo build, el mas reciente GLOBAL, sin pais** [VERIFIED migrations/0048_discovery_capture.sql:82-106]:
  ```sql
  CREATE OR REPLACE VIEW v_exhaustiveness_seal AS
  WITH latest AS (SELECT build_run_id FROM exhaustiveness_estimate ORDER BY created_at DESC LIMIT 1)
  SELECT ... FROM exhaustiveness_estimate e JOIN latest l ON l.build_run_id = e.build_run_id;
  ```
  [VERIFIED 0048:83-88 el CTE `latest`, 0048:105-106 el JOIN].
- **La tabla `exhaustiveness_estimate` NO tiene columna country_code** [VERIFIED 0048:55-74]: sus dimensiones son `build_run_id`, `province_code char(2)` (NULL=roll-up nacional [VERIFIED 0048:58]) y `segment` (NULL=todos los tipos [VERIFIED 0048:59]). grep country en 0048 = 0.
- **`discovery_capture` (la matriz de captura) tampoco tiene country_code** [VERIFIED 0048:36-44]: `province_code char(2)` [VERIFIED 0048:39], PK `(resolved_ulid, list_key, build_run_id)` [VERIFIED 0048:43].
- El handler `geo_exhaustiveness` lee el view [VERIFIED geo.py:147-221]: el fetch en [VERIFIED geo.py:168-172] con `ORDER BY segment NULLS FIRST, province_code NULLS FIRST` [VERIFIED geo.py:172]; el titular gran-nacional es la fila `segment IS NULL AND province IS NULL` [VERIFIED geo.py:201-204]; sirve `build_run_id` [VERIFIED geo.py:197,216] como provenance re-ejecutable.

**(b) Mecanismo al atomo**
El certificado lo sirve un view que elige UN `build_run_id` — el globalmente mas reciente por `created_at` (`ORDER BY created_at DESC LIMIT 1`) — y devuelve TODAS las filas-estrato de ese unico build. El handler extrae la fila gran-nacional (`segment=NULL, province=NULL`) como el titular `coverage_lower` + flag `sealed` + `build_run_id`. Por tanto TODO el certificado (nacional + por-segmento + por-provincia) esta scopeado a exactamente un build, elegido GLOBALMENTE. No hay dimension pais en ningun eslabon: ni en discovery_capture (matriz), ni en exhaustiveness_estimate (estimacion por estrato), ni en el CTE `latest` del view. El diseno append-only (una fila por build_run_id) PRESERVA la historia, pero el view SERVIDO solo expone el unico build mas nuevo de la tabla entera.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** **ES -> generico.** La capa de exhaustividad se construyo single-tenant: `build_run_id` es la unica clave de particion y 'latest' significa el mas reciente del PLANETA. Cuando un 2o pais corre su propio build MSE, sus filas aterrizan en exhaustiveness_estimate con un `build_run_id` NUEVO y un `created_at` mas NUEVO; el CTE `latest` [VERIFIED 0048:83-88] selecciona ESE build_run_id y el view devuelve SOLO los estratos del 2o pais. El certificado nacional sellado del 1er pais sigue en la tabla (append-only) pero DESAPARECE del view servido. El contrato de monotonia de la cota inferior (un pais sellado nunca ve bajar su coverage_lower) se rompe en la capa de SERVIDO aunque la fila de estimacion subyacente este intacta. El contrato 'servir el sello' nunca fue por-pais.
- **Fix — propuesta [no implementada].** **Fix exacto — latest build POR PAIS:**
1. `ALTER TABLE exhaustiveness_estimate ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` (y lo mismo en `discovery_capture` para atribuir los estratos por pais) — patron 0052: backfill ES implicito, cero-NULL, additivo.
2. Reescribir el CTE `latest` del view a latest-build-POR-PAIS:
   ```sql
   WITH latest AS (
     SELECT DISTINCT ON (country_code) country_code, build_run_id
     FROM exhaustiveness_estimate ORDER BY country_code, created_at DESC)
   SELECT ... FROM exhaustiveness_estimate e
     JOIN latest l ON l.country_code = e.country_code AND l.build_run_id = e.build_run_id;
   ```
   (CREATE OR REPLACE additivo; rollback restaura el CTE global de 0048:83-88).
3. `geo.py:169-172`: anadir `country_code` al SELECT y `WHERE country_code = $cc` (o exponer todos y agrupar por pais); anadir `country` al meta del certificado y al ORDER BY.
4. El writer del build MSE (pipeline/exhaustiveness/) estampa `country_code` en cada fila de estimate + capture.
5. ES: con DEFAULT 'ES' y un solo pais, `DISTINCT ON (country_code)` rinde exactamente el mismo unico build -> certificado byte-identico.
- **Adversarial (DE/FR/IT/PT/no-UE).** **Mexico/Portugal corre su build MSE** -> su `build_run_id` es el mas reciente globalmente -> el CTE `latest` lo selecciona -> `/geo/exhaustiveness` deja de servir el certificado ES sellado (DESAPARECE, no error). El 'intervalo certificado' de un pais ya sellado cambia o se borra cuando OTRO pais construye — viola monotonia y durabilidad por pais. **Concreto:** con DE+ES, si DE corre build a las 10:00 y ES sello a las 09:00, a las 10:01 el certificado nacional servido en el MISMO endpoint (sin parametro de pais) pasa de 'ES 80,5% sellado' a 'DE 12% no-sellado'; un comprador que ayer vio el sello ES hoy ve el de DE. **No-UE (MX/JP):** igual, agravado porque su denominador puede ser NO_DENOM (facetas 11/13) y aun asi su build 'gana' el latest global y oculta el certificado europeo. **Ruido:** dos builds del MISMO pais en append-only ya funcionan bien (latest gana, monotonia intra-pais); el fallo es estrictamente cross-country.
- **Sellado + verificación multi-vía.** **Criterio de sellado + verificacion multi-via:**
- **Durabilidad:** tras correr el build del pais B, `/[A]/geo/exhaustiveness` sigue devolviendo el certificado sellado de A byte-identico (seed A sellado -> correr B -> assert A intacto).
- **Monotonia:** para un pais sellado, el `coverage_lower` servido NUNCA decrece tras un build de otro pais (golden de serie temporal).
- **Via 1 (DISTINCT ON):** con N paises el view devuelve exactamente N filas gran-nacional (una por pais), cada una con su build_run_id mas reciente.
- **Via 2 (HTTP-vs-SQL):** el `build_run_id` servido por pais == `SELECT build_run_id FROM exhaustiveness_estimate WHERE country_code=$cc ORDER BY created_at DESC LIMIT 1`.
- **Via 3 (no-bleed):** el certificado de A no contiene ninguna fila province/segment de B.
- **Via 4 (reproducibilidad):** re-ejecutar el build de A desde su build_run_id da `coverage_lower` identico (acopla con la atestacion in-toto).
- **Precondiciones:** faceta 16 (dimension pais en request), faceta 25 (/countries expone la cota por pais), faceta 13 (NO_DENOM no se confunde con sellado).
- **Herramienta NEXT-LEVEL (€0).** **in-toto + Sigstore/rekor** — Apache-2.0, €0 — https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143]. Cada build de sello emite una atestacion que liga {git SHA del codigo, content-hashes de census CSV + matriz de captura + membresias de lista + version de estimador} -> {coverage_lower, CI, N_hat} por estrato, firmada y anexada a un transparency log tamper-evident con prueba de inclusion. Eleva la durabilidad-por-pais de 'el view ahora filtra bien' a 'el certificado de CADA pais es un artefacto no-repudiable, re-verificable por un tercero sin confiarnos, que NO PUEDE desaparecer ni mutar sin que la verificacion FALLE' [VERIFIED:141-142]; in-toto graduo en CNCF 2025-02-10 [VERIFIED:142]. **Companero:** DVC (versionado content-addressed de inputs del sello) — Apache-2.0, €0 — https://github.com/iterative/dvc [VERIFIED:151], que hace cada `build_run_id` bit-reproducible y sostiene la monotonia como medicion real y no drift [VERIFIED:149-150]. Ruta €0: cosign keyless OIDC / rekor public-good o self-host, CPU-only [VERIFIED:145].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f13"></a>

### Faceta 13 · NO_DENOM como precondición de sellado

**(a) Verificacion de code_hints [VERIFIED]**
- `migrations/0042_province_seal_view.sql:36-41` [VERIFIED] — rama VENTA:
  `CASE WHEN d.point_est IS NULL OR d.point_est = 0 THEN 'NO_DENOM' WHEN ... >= 85 THEN 'SELLADO' WHEN ... >= 50 THEN 'PARCIAL' ELSE 'GAP' END AS verdict`.
- `migrations/0043_province_seal_desguace.sql:44-49` (venta, byte-identica) y `0043:61-65` [VERIFIED] — rama DESGUACE:
  `CASE WHEN dg.denominator IS NULL OR dg.denominator = 0 THEN 'NO_DENOM' WHEN dg.numerator >= dg.denominator THEN 'SELLADO' ELSE 'GAP' END`.
- `services/api/routers/geo.py:124-141` [VERIFIED] — el rollup nacional en `geo_seal`:
  `den = int(r["denominator"]) if r["denominator"] is not None else None` (:124);
  `seg["national"]["numerator"] += num` **incondicional** (:133);
  `if den: seg["national"]["denominator"] += den` (:134-135) — el denominador solo suma si es truthy;
  `seg["distribution"][r["verdict"]] = ... + 1` (:136) — **NO_DENOM se cuenta en el histograma como un veredicto mas**;
  `nat["coverage_pct"] = round(100*nat["numerator"]/nat["denominator"],1) if nat["denominator"] else 0` (:140-141).
- `services/api/routers/geo.py:174-189` [VERIFIED] — `/geo/exhaustiveness._cert` expone `"sealed": r["sealed"]` (:188) pero **sin** ninguna precondicion de existencia-de-denominador/ancla.

**(b) El mecanismo al atomo**
El veredicto se computa en SQL por `(province, segment)`. `NO_DENOM` se emite **exactamente** cuando el denominador es NULL o 0 (`point_est` para venta `0042:37`; el subconjunto censal `dgt_cat` para desguace `0043:62`). En la API, `geo_seal` pliega filas a un rollup nacional con **tres fallos atomicos**:
1. **Suma asimetrica:** suma el numerador SIEMPRE (`:133`) pero el denominador **solo si es truthy** (`:134`). Una provincia `NO_DENOM` aporta su numerador al numerador nacional y **0** al denominador -> el `coverage_pct` nacional se calcula sobre un denominador PARCIAL sin avisar.
2. **Histograma contaminado:** `NO_DENOM` entra en `distribution` (`:136`) como si fuese un estado de cobertura (junto a SELLADO/PARCIAL/GAP).
3. **Sin gate de certificabilidad:** no existe ningun campo top-level que diga "este segmento/pais NO es certificable porque su denominador esta ausente". El veredicto `NO_DENOM` es por-provincia y se diluye.
La rama exhaustividad expone `sealed` pero nunca lo condiciona a la existencia del ancla/denominador.

**(c) Costura ES->generico**
En ES **toda** provincia tiene `point_est` DIRCE, asi que `NO_DENOM` practicamente nunca se dispara y la precondicion ausente es **invisible**. En cuanto entra un 2o pais con denominador ausente/parcial (facetas 10/11), aparecen filas `NO_DENOM` que se **malinterpretan como "pendiente/progreso"** en vez de "no certificable". La semantica que separa "denominador ausente => no se puede certificar" de "cubierto/parcial/gap" **no existe en el contrato**.

**(d) Fix exacto**
1. **Precondicion explicita y legible por maquina** en el envelope del sello, a nivel segmento Y nacional Y por-pais:
   `"certifiable": bool`, `"reason": "NO_DENOM" | null`, derivado de "existe denominador para TODO estrato contado de este scope". Un scope con CUALQUIER estrato `NO_DENOM` (o denominador nacional nulo) es `certifiable=false`, **distinto** de un `coverage_pct` bajo.
2. **Detener la inflacion silenciosa del numerador nacional:** o excluir las provincias `NO_DENOM` del rollup nacional, o exponer `numerator_without_denominator` aparte, para que el `coverage_pct` nacional sea honesto sobre su base de denominador.
3. **Separar `NO_DENOM` del histograma** (`:136`) a su propio `no_denominator_count`, de modo que un dashboard nunca lo lea como veredicto de cobertura.
4. **Espejo en exhaustividad:** `sealed=true` exige denominador/ancla presente (precondicion), no solo `coverage_lower >= threshold`.

**(e) Criterio de sellado + verificacion multi-via**
- **Unit golden del rollup:** un pais sintetico con 2 provincias (una con denominador, una `NO_DENOM`) => nacional `certifiable=false`, `no_denominator_count=1`, y `coverage_pct` nacional **no** es un numero fabricado sobre base parcial.
- **Golden ES byte-identico:** ES (toda provincia con denominador) => `certifiable=true`, `no_denominator_count=0`, `coverage_pct` inalterado (~79.4% venta).
- **Snapshot de contrato (faceta 30 / oasdiff):** los nuevos campos `certifiable`/`reason` quedan pineados; su ausencia en un build futuro rompe CI.
- **Contrato de datos pre-sello (GE/Pandera):** un estrato cuyo denominador cayo a NULL en silencio FALLA CERRADO antes de servir.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**Great Expectations** (alt. Pandera) — *Contrato de datos PRE-sello* [VERIFIED `NEXT-LEVEL.md:167`; https://github.com/great-expectations/great_expectations; Apache-2.0; EUR0=True]. Codifica la **precondicion estadistica oculta** del sello ("todo estrato contado tiene un denominador real; ningun `source_key` cae en silencio a un bucket equivocado") como una expectativa **ejecutable, versionada y bloqueante** que FALLA el build CERRADO en vez de servir un `NO_DENOM` disfrazado de progreso [VERIFIED:165-170]. EUR0 Python puro, corre en CI y pre-seal; la baseline ES pasa byte-identica [VERIFIED:170]. Es el mecanismo exacto que convierte "denominador presente" de suposicion a **precondicion probada** del sello; la suite de expectativas se versiona por country-pack (aditiva).

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El veredicto NO_DENOM (0042:37 venta point_est NULL/0; 0043:62 desguace denominator NULL/0) es por-provincia; el rollup nacional geo.py:124-141 suma numerador siempre (:133) pero denominador solo si truthy (:134), mete NO_DENOM en el histograma distribution (:136) y no expone ningun gate de certificabilidad. /geo/exhaustiveness tiene 'sealed' (:188) sin precondicion de denominador. En ES nunca se dispara (todas con DIRCE), asi que el hueco es invisible hasta el 2o pais.
- **Fix — propuesta [no implementada].** Anadir certifiable:bool + reason:'NO_DENOM'|null a nivel segmento/nacional/pais (false si CUALQUIER estrato NO_DENOM); dejar de inflar el numerador nacional con provincias sin denominador (exponer numerator_without_denominator o excluirlas); sacar NO_DENOM del histograma a no_denominator_count; y exigir denominador/ancla presente para sealed=true en exhaustividad.
- **Adversarial (DE/FR/IT/PT/no-UE).** Pais nuevo sin denominador: NO_DENOM aparece indefinidamente y un dashboard/operador lo lee como 'en progreso', pudiendo declarar el pais sellado sobre un denominador inexistente (certificar humo). O el coverage_pct nacional marca p.ej. 92% mientras medio pais es NO_DENOM, porque sus numeradores cuentan y sus denominadores ausentes no.
- **Sellado + verificación multi-vía.** Unit golden: pais con 1 provincia con denom + 1 NO_DENOM => nacional certifiable=false, no_denominator_count=1, coverage_pct no-fabricado. Golden ES byte-identico (certifiable=true, ~79.4%). Snapshot oasdiff pinea certifiable/reason. GE/Pandera pre-seal: estrato con denom NULL falla CERRADO.
- **Herramienta NEXT-LEVEL (€0).** Great Expectations (alt Pandera) — contrato de datos PRE-sello [VERIFIED NEXT-LEVEL.md:167; https://github.com/great-expectations/great_expectations; Apache-2.0; EUR0]. Expectativa ejecutable/versionada/bloqueante que falla CERRADO si un estrato no tiene denominador real; ES pasa byte-identica [VERIFIED:165-170]; versionada por country-pack.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f14"></a>

### Faceta 14 · canonical_key cross-border: pureza de cluster servido

**(a) Verificacion de code_hints [VERIFIED]**
- **Pre-image country-blind**: `canonical_key` acepta `country_code` (param :61) pero lo EXCLUYE deliberadamente del pre-image [VERIFIED services/api/codes.py:62-65, comentario "mixing the country into it would change every sha256 hash and re-key all entities"]. Ramas del pre-image: `particular:{plat}:{sid}` [codes.py:72-75], `domain:{host}` solo host desnudo [86-87], `cif:{CIF}` SIN validar [88-89], `name:{norm}|{muni}[|addr]` [93-94], `name:{norm}|p{prov}[|addr]` [95-96]. El pais vive SOLO en el prefijo humano via `mint_code` [codes.py:44-53].
- **resolve_cluster country-blind**: paso 1 busca entity por cdp_code [VERIFIED deps.py:114-124]; paso 2 colecciona TODOS los miembros `WHERE COALESCE(vdr.resolved_ulid, e.entity_ulid) = canonical_ulid` [VERIFIED deps.py:131-140] — **sin predicado country_code en ninguna parte**. La membresia del cluster es ciega al pais.
- **Test que fija la ceguera**: `canonical_key(domain="ford.es", country_code="ES") == ...("DE") == "domain:ford.es"` [VERIFIED tests/test_country_coexistence.py:133-136]; mismo para `cdp_pair` [172-178].
- Consumido por los 8 endpoints keyed-by-identity (entities/platforms/vehicles: inventory/delta/history) que dependen de que `resolve_cluster` devuelva miembros de UN pais.

**(b) Mecanismo al atomo**
Identidad de dedup = `sha256(pre-image)` [codes.py:117]. Como el pre-image omite el pais, dos entidades que comparten dominio desnudo / VAT-shaped CIF / name+muni normalizados a traves de fronteras hashean al MISMO `canonical_key`. Si el clustering upstream (`v_dealer_resolved`, clusters transitivos VAM-verificados) las liga bajo un `resolved_ulid`, el COALESCE de `resolve_cluster` [deps.py:137] devuelve miembros de >1 pais, y los 8 endpoints "country-correct by construction" sirven un cluster cross-border: `/entities/{cdp}/inventory` une stock de varios paises, `/delta` emite eventos de todos los miembros. **No se lanza error** — es regresion de correccion silenciosa.

**(c) Costura ES->generico + fix exacto**
Dentro de ES, domain/CIF/name+muni son suficientemente unicos a nivel nacional. Cross-border colisionan tres familias del pre-image:
- **domain**: un dominio global desnudo (toyota.com; el sitio unico de un grupo pan-EU) compartido por sucursales nacionales → un canonical_key.
- **cif**: `codes.py:88-89` keyea CUALQUIER string pasado como `cif` sin validar (x-ref faceta 15); un USt-IdNr DE o TVA FR que coincida en forma, o un VAT de grupo reusado entre filiales, colisiona.
- **name+municipality_code**: los codigos de municipio son country-scoped (PK compuesto tras 0053) pero el pre-image usa el string desnudo del muni → `name:x|28079` podria coincidir si un 2o pais reusa el codigo 28079.

**Fix (decision + sello, sin re-keyear ES):**
- **Decision de identidad**: incluir el pais en el pre-image SOLO para las familias country-relativas (name+muni, name+prov, y cif una vez validado por pais en faceta 15), manteniendo `domain` country-blind (un dominio desnudo ES globalmente unico por DNS). Gatear el cambio por el argumento country para que el default ES quede byte-identico.
- **Sello mecanico mas seguro (preserva el golden de 431k entidades)**: dejar `canonical_key` byte-identico y SELLAR la pureza en la capa cluster/serve — anadir `AND e.country_code = $cc` a la query de miembros de `resolve_cluster` [deps.py:131-140] y al cierre transitivo de `v_dealer_resolved`, de modo que un canonical_key cross-border pueda existir pero un cluster servido sea mono-pais por construccion. El pais del cdp_code pedido (prefijo CDP-XX- / entity.country_code) scopea la membresia.
- **Declarar y testear la politica**: el clustering cross-border es FORBIDDEN (membresia country-scoped) o INTENCIONAL+explicito (multinacional documentada, flag), nunca silencioso.

**(d) Riesgo adversarial concreto**
- **Japon/global**: un dealer alcanzable como toyota.com (dominio desnudo) descubierto en dos paises colapsa a `domain:toyota.com`; `/entities/{cdp}/inventory` mezcla stock JP+global.
- **Grupo pan-EU** (opera en ES+PT+FR bajo un dominio corporativo) → un canonical_key, un cluster, bleed de inventario cross-border.
- **Reuso de VAT**: un VAT de grupo o un DE/FR VAT de forma coincidente keyeado como `cif:` (sin validar, faceta 15) fusiona entidades nacionales distintas → infla un cluster, deflaciona el conteo de dealers del otro pais.
- El invariante estrella del diseno ("la mayoria de la superficie ya es multi-pais") se rompe en silencio, sin excepcion.

**(e) Sellado + verificacion multi-via**
- **Criterio**: para todo cdp_code servido, todos los miembros del cluster comparten el pais pedido (member.country_code == cc pedido), O el cluster esta marcado multinacional por politica explicita. `canonical_key`/`cdp_code` ES byte-identicos.
- **Via 1 DB no-bleed**: sembrar una entidad de 2o pais que COMPARTE dominio desnudo / CIF con una ES en txn revertida (patron tests/test_country_coexistence.py:309-369), y asertar que `resolve_cluster(es_cdp).member_ulids` no contiene ulids no-ES y `resolve_cluster(de_cdp)` ninguno no-DE.
- **Via 2 Schemathesis bleed-check**: un check custom asevera que toda respuesta de `/entities|/platforms|/vehicles` con dimension pais devuelve solo miembros de ese pais; fuzz N casos.
- **Via 3 golden**: la ceguera de pais de `domain` (ford.es ES==DE) PRESERVADA donde se quiere [test_country_coexistence.py:133-136], mientras la familia name+muni prueba dedup country-scoped bajo la nueva politica.
- **Via 4 2a via ER (Splink)**: recomputa el cluster independientemente; las fusiones cross-border afloran como desacuerdo.

**(f) Herramienta NEXT-LEVEL**
**Schemathesis** (MIT) — https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828]. Su fuzzing property-based dirigido por el schema con un check de country-bleed es el inquisidor mecanico que sella "todo cluster servido es mono-pais" en los 8 endpoints keyed-by-identity — auto-detecta el leak de miembros cross-border que ningun test a mano enumera [NEXT-LEVEL.md:831 nombra el bleed-check explicito]. Emparejar con **python-stdnum** (LGPL-2.1) — https://github.com/arthurdejong/python-stdnum [VERIFIED NEXT-LEVEL.md:487; licencia tabla:59] para validacion VAT/registral por pais con digitos de control, de modo que la rama `cif:` [codes.py:88-89] solo keyee un id nacional VALIDADO (cierra la colision en origen, x-ref faceta 15). Para recomputo 2a-via del cluster, **Splink** (MIT) — https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:447] da linkage Fellegi-Sunter aprendido que marca fusiones cross-border.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El pre-image de canonical_key es deliberadamente country-blind (codes.py:62-65; ford.es ES==DE, test:133-136) y resolve_cluster colecciona miembros sin predicado de pais (deps.py:131-140); cross-border, las familias domain/cif/name+muni colisionan, y si el clustering upstream las liga, los 8 endpoints keyed-by-identity sirven un cluster con miembros de varios paises sin lanzar error.
- **Fix — propuesta [no implementada].** Decision de identidad: incluir pais en el pre-image solo para familias country-relativas (name+muni/prov, cif validado en faceta 15), domain queda global. Sello que preserva el golden de 431k: dejar canonical_key byte-identico y anadir AND e.country_code=$cc a la query de miembros de resolve_cluster (deps.py:131-140) y al cierre de v_dealer_resolved -> cluster mono-pais por construccion. Declarar la politica cross-border (forbidden o intencional+flag).
- **Adversarial (DE/FR/IT/PT/no-UE).** toyota.com (dominio desnudo) descubierto en 2 paises colapsa a un canonical_key y /entities/{cdp}/inventory mezcla stock JP+global; grupo pan-EU bajo un dominio = bleed de inventario; VAT de grupo keyeado como cif: sin validar fusiona entidades nacionales distintas (infla un cluster, deflaciona el conteo del otro pais). Silencioso, sin excepcion.
- **Sellado + verificación multi-vía.** Criterio: todos los miembros del cluster servido comparten el pais pedido (o flag multinacional explicito); ES byte-identico. Via1 DB no-bleed (sembrar 2o pais que comparte dominio/CIF en txn revertida, resolve_cluster sin ulids del otro pais). Via2 Schemathesis country-bleed check sobre los 8 endpoints. Via3 golden domain ES==DE preservado + name+muni country-scoped. Via4 Splink recomputo 2a-via marca fusiones cross-border.
- **Herramienta NEXT-LEVEL (€0).** Schemathesis (MIT) https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828] — bleed-check property-based sella cluster mono-pais en los 8 endpoints; + python-stdnum (LGPL-2.1) https://github.com/arthurdejong/python-stdnum [VERIFIED NEXT-LEVEL.md:487] valida cif: por pais (cierra colision en origen); + Splink (MIT) https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:447] recomputo ER 2a-via.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f15"></a>

### Faceta 15 · Validador tax-id por país (rama cif:)

**(a) Code_hints verificados**
- **[VERIFIED services/api/tax_id.py:1-93]** validador **SOLO ES**, pure-stdlib: `_NIF_LETTERS="TRWAGMYFPDXBNJZSQVHLCKE"` (:20), `_CIF_ORG_DIGIT/_LETTER/_EITHER` (:26-28), `is_valid_nif` (:39-43), `is_valid_nie` (:46-51), `_cif_check_digit` (:54-64, Luhn-like BOE), `is_valid_cif` (:67-82), `is_valid_tax_id` (:85-86), `canonical_tax_id` (:89-93). Todos algoritmos **BOE espanoles**.
- **[VERIFIED services/api/codes.py:88-89]** rama cif de `canonical_key`: `if cif:` (:88) -> `return f"cif:{cif.upper().strip()}"` (:89) — **keyea sobre un `cif` desnudo SIN validacion alguna**.
- **[VERIFIED services/api/codes.py:19-21]** `codes.py` importa solo `hashlib, re, unicodedata` — **NO importa `tax_id`**; `canonical_key` **nunca llama** `is_valid_cif`. El validador ES que EXISTE **no esta cableado** en el path de la clave servida.
- **[VERIFIED tax_id.py:3-7]** el propio docstring: `canonical_key` keyea sobre cif desnudo sin validar, "a corrupt CIF mints identity off garbage and risks inflating the dealer denominator", y se declara "the EUR0 replacement for python-stdnum (es.nif/es.cif)".
- **[VERIFIED codes.py:90-97]** fallback cuando no hay cif/domain/particular: `name+municipality_code` / `name+province_code`.

**(b) Mecanismo al atomo**
Prioridad de `canonical_key` **[VERIFIED codes.py:8]**: `particular > domain > CIF > name|muni`. La rama `cif:` (codes.py:88-89) es la "strong registral key". **Dos defectos independientes:**
1. **La rama cif NO valida** (codes.py:88-89): cualquier string pasado como `cif` mintea una identidad `cif:{X}`; un VAT basura/extranjero se vuelve clave dura de dedup sobre basura -> infla el denominador de dealers o fusiona mal.
2. **`tax_id.py` valida SOLO ES** NIF/NIE/CIF (algoritmos BOE); no hay validador DE USt-IdNr / FR TVA / IT P.IVA / PT NIF / MX RFC, y `canonical_tax_id` ni siquiera es invocado por `canonical_key`.

**(c) Costura ES->generico**
La clave registral dura es Spain-shaped **dos veces**: (a) el unico validador (tax_id.py) conoce solo checksums ES; (b) `canonical_key` no valida en absoluto. Un VAT no-ES o (i) se keyea crudo como `cif:` basura (falsa identidad fuerte), o (ii) si se anadiera un gate ingenuo `is_valid_cif` ES, **todo VAT DE/FR fallaria** y degradaria a keying `name+municipality` — perdiendo la dedup fuerte que ES si tiene y **cambiando el conteo de dealers** del pais nuevo.

**(d) Riesgo adversarial**
**DE (USt-IdNr `DE123456789`):** falla `is_valid_cif` -> hoy keyea crudo `cif:DE123456789` (falsa clave fuerte) o, con gate ES ingenuo, degrada a name+muni -> el mismo dealer Mercedes hallado por 2 fuentes ya no dedup -> conteo inflado. **FR/IT/PT:** TVA francesa, Partita IVA italiana, NIF portugues fallan las reglas org-letter/check-digit ES; o keyean basura o degradan. **MX/no-UE (RFC), JP corporate-number:** sin esquema; keyea garbage o degrada. **Ruido:** un CIF ES corrupto (typo) hoy pasa directo (sin validacion en codes.py:88-89) y mintea un dealer fantasma — la inflacion de denominador que el docstring de tax_id.py advierte **[VERIFIED tax_id.py:3-6]**.

**(e) Criterio de sellado + verificacion multi-via**
1. **Golden por esquema:** python-stdnum trae numeros validos/invalidos por pais; pinearlos (`de.vatid, fr.tva, it.iva, pt.nif`) pasan/fallan correctamente.
2. **Preservacion ES:** todo CIF almacenado vivo sigue validando y el token `cif:` byte-identico -> golden cdp_code (**[VERIFIED tests/test_country_golden.py:67-68]** `cif:B12345678` -> `CDP-ES-28-8H6PF2E7`) sigue verde.
3. **Junk-rejection:** un id malformado falla su digito de control y se descarta (no siembra arista), probado por unit test; `canonical_key` cae a name+muni, no a `cif:garbage`.
4. **Cross-via:** tax_id.py ES y python-stdnum `es.cif` coinciden sobre una muestra de CIFs vivos (dos implementaciones independientes convergen).

**(f) Herramienta NEXT-LEVEL**
**python-stdnum — LGPL-2.1** — https://github.com/arthurdejong/python-stdnum **[VERIFIED NEXT-LEVEL.md:490]**, via *python-stdnum registral/VAT validation* **[VERIFIED NEXT-LEVEL.md:487-493]**. Valida+formatea ~50 paises' company/VAT/tax con **digitos de control** (`es.cif, es.nif, de.vatid, fr.siren/siret, it.iva, pt.nif, mx.rfc, eu.vat`). Cierra B19/MP3: clave registral fuerte country-proof y auto-validante; `canonical_key` pasa a `{scheme}:{validated}` (migracion aditiva `cif -> (registral_id, id_scheme)` + ensanchar enum `alias_kind`). **Nota licencia [VERIFIED NEXT-LEVEL.md:492]:** import dinamico sin modificar = compliant server-side; si se exige permisivo puro, portar las funciones de check-digit (estandares publicos) al repo. **tax_id.py ES queda como ancla byte-identica.**

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** canonical_key keyea cif: SIN validar (codes.py:88-89) y el unico validador (tax_id.py:39-82) es SOLO ES (BOE NIF/NIE/CIF), ademas codes.py ni siquiera importa tax_id (codes.py:19-21). Un VAT no-ES o se keyea como cif: basura (falsa identidad fuerte) o, con gate ES ingenuo, degrada a name+muni y cambia el conteo de dealers.
- **Fix — propuesta [no implementada].** certified_tax_id(raw, country_code) que enruta ES->tax_id.py (intacto, ancla) y DE/FR/IT/PT->python-stdnum (de.vatid/fr.tva/it.iva/pt.nif/eu.vat) con check digits. Cablearlo en la rama cif de canonical_key: solo keyear cif:{validated} si pasa el checksum del pais, si no caer a name+location (no mintear sobre id no validado). Token generico {scheme}:{validated} (migracion aditiva cif->(registral_id,id_scheme), ensanchar alias_kind). ES byte-identico (es.cif acepta CIFs vivos, token sin cambio).
- **Adversarial (DE/FR/IT/PT/no-UE).** DE USt-IdNr 'DE123456789' falla is_valid_cif -> keyea cif:DE123456789 basura o degrada a name+muni -> mismo Mercedes por 2 fuentes no dedup -> conteo inflado. FR TVA/IT P.IVA/PT NIF: keyean basura o degradan. MX RFC/JP: sin esquema. Ruido: CIF ES corrupto pasa directo (sin validacion codes.py:88-89) y mintea dealer fantasma (inflacion denominador, tax_id.py:3-6).
- **Sellado + verificación multi-vía.** (1) Golden por esquema: numeros validos/invalidos de python-stdnum pinneados (de.vatid/fr.tva/it.iva/pt.nif). (2) ES: todo CIF vivo valida y token cif: byte-identico -> golden test_country_golden.py:67-68 (cif:B12345678->CDP-ES-28-8H6PF2E7) verde. (3) Junk-rejection: id malformado falla check-digit, cae a name+muni no cif:garbage. (4) Cross-via: tax_id.py ES vs python-stdnum es.cif convergen en muestra viva.
- **Herramienta NEXT-LEVEL (€0).** python-stdnum — LGPL-2.1 [VERIFIED NEXT-LEVEL.md:490] — https://github.com/arthurdejong/python-stdnum. Valida+formatea ~50 paises VAT/company con check digits (es.cif, de.vatid, fr.siren, it.iva, pt.nif, mx.rfc, eu.vat). Cierra B19/MP3. Licencia [VERIFIED:492]: import dinamico OK server-side; o portar check-digits publicos para permisivo puro. tax_id.py ES queda como ancla.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f16"></a>

### Faceta 16 · Plomería de la dimensión-país en la request

**(a) code_hints VERIFICADOS**
- **Ningun endpoint acepta pais** [VERIFIED] — grep funcional de `country` en services/api/routers/ devuelve UN solo match y es prosa de docstring [VERIFIED services/api/routers/geo.py:305 "country -> province -> municipality"], no un parametro ni un predicado. Las 18 firmas `@router.get` no toman country [VERIFIED listado de routers].
- **DEFAULT_COUNTRY='ES'** [VERIFIED services/api/codes.py:24] threadeado como kwarg por defecto en mint_code/canonical_key/cdp_pair/cdp_code [VERIFIED codes.py:45,61,104,125], y deliberadamente FUERA del pre-image de canonical_key [VERIFIED codes.py:62-65].
- **El cache key pliega solo path+query** [VERIFIED services/api/cache.py:79-94]: `_cache_key` = `f"{method}:{path}?{qs}"`; nota de auditoria explicita [VERIFIED cache.py:82-85]: "this key has NO auth/tenant dimension".

**(b) El mecanismo al atomo**
Es la decision-madre: de DONDE entra el pais (segmento de path `/{country_code}/...`, query `?country=`, header `X-Country`, o tenant API-key->pais) cuelgan literalmente (1) la clave de cache (cache.py:79-94, que solo captura path+query) y (2) todos los predicados SQL de las facetas 4-12. El atomo peligroso: `DEFAULT_COUNTRY='ES'` (codes.py:24) convierte cualquier handler que olvide threadear pais en un servidor silencioso de ES — no lanza error, devuelve ES etiquetado como el pais pedido.

**(c) Costura ES->generico**
El diseno afirma "?country= se auto-particiona" pero ese parametro NO existe en ningun sitio del codigo servido [VERIFIED grep], y el punto de entrada nunca se decidio. Sin tomar esta decision, las demas facetas (4-12, 17, 22-25) no tienen por donde recibir el pais.

*Costura, fix, adversarial, sellado y herramienta NEXT-LEVEL: en la **Ficha operativa** inmediatamente debajo.*

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El diseno asume `?country=` auto-particionante pero ese parametro no existe [VERIFIED grep funcional=0; geo.py:305 es comentario]. DEFAULT_COUNTRY='ES' (codes.py:24) hace que todo handler que olvide threadear pais asuma ES en silencio. La clave de cache (cache.py:79-94) solo pliega path+query, asi que la eleccion del punto de entrada (path/query vs header/tenant) determina si el aislamiento de cache es gratis o roto.
- **Fix — propuesta [no implementada].** Decision: adoptar segmento de path `/{country_code}/...` (o `?country=` default 'ES') como entrada UNICA, porque el cache key ya pliega path+query (cache.py:79-94) -> el pais queda capturado en la clave sin trabajo extra, mientras header/tenant NO se captura y arrastra la faceta 17. Threadear una dependencia unica `country: str` a TODOS los handlers con dimension pais y pasarla a cada predicado SQL. Prohibir DEFAULT_COUNTRY implicito en requests multi-pais: convertirlo en ancla de golden explicita (p.ej. dependencia que exige la dimension cuando hay >1 pais cargado), nunca fallback silencioso.
- **Adversarial (DE/FR/IT/PT/no-UE).** Si el pais se enhebra por header X-Country o tenant API-key en vez de path/query, el cache key (que pliega solo path+query) sirve a un cliente DE el cuerpo cacheado de ES para el mismo path — bleed cross-country invisible hasta el TTL. Y DEFAULT_COUNTRY='ES' hace que cualquier handler sin threadear devuelva datos ES etiquetados como el pais pedido (FR/IT/PT/MX). Ruido: un `?country=XX` de un pais no cargado debe resolver determinista (vacio o 4xx), no caer a ES.
- **Sellado + verificación multi-vía.** Criterio: una unica via de entrada del pais, capturada por la clave de cache, sin default silencioso. Multi-via: (a) guard de grep — #handlers con dimension pais == #endpoints country-aware; (b) aislamiento de cache — GET /DE/geo/28 nunca devuelve el cuerpo cacheado de /ES/geo/28 (test); (c) golden ES — /ES/... (o sin country) byte-identico a las URLs de hoy; (d) fail-loud — con 2 paises cargados, una request sin country resuelve determinista o 4xx, jamas ES en silencio.
- **Herramienta NEXT-LEVEL (€0).** darkweak/souin (edge-http-cache-swr) — MIT [VERIFIED NEXT-LEVEL.md:780] — https://github.com/darkweak/souin . Una vez elegida la dimension pais, la cache de borde RFC-7234 de Souin (montada en el mismo Caddy del borde TLS) keyea la dimension mecanicamente — incluido Vary si el pais llega por header — country-proof entre workers y reinicios, cerrando el leak de cache.py:79-86 [NEXT-LEVEL:783 explicito: 'la cache key incluye el country efectivo -> /geo/ES/... nunca sirve el cuerpo de /geo/DE/...']. Nota honesta: la eleccion path/query-vs-header es la mitad de diseno (humana); Souin impone mecanicamente la dimension que se elija.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f17"></a>

### Faceta 17 · Cache key: dimensión país/tenant + aislamiento

**(a) Code_hints VERIFICADOS leyendo la fuente real**
- [VERIFIED services/api/cache.py:79-94] `_cache_key(request)` construye `f'{method}:{path}?{qs}'` con method + path + query params ORDENADOS; el docstring (lineas 82-85) se auto-marca: 'this key has NO auth/tenant dimension ... introducing per-tenant API keys WITHOUT adding the key/tenant-id to this key would let tenant A be served tenant B cached body. Multi-tenant auth MUST extend this key.'
- [VERIFIED services/api/cache.py:57-62] `CACHEABLE_PATH_PREFIXES = ('/geo/', '/entities/', '/platforms/')`; y [VERIFIED cache.py:66-70] `CACHE_EXCLUDED_PATHS = ('/health','/alerts','/sources')`. is_cacheable exige GET. -> la superficie cacheada es EXACTAMENTE geo/entities/platforms; /stats NO se cachea (no esta en prefixes), lo que ACOTA el riesgo de bleed a esas tres familias.
- [VERIFIED services/api/cache.py:49-76] `_cache = TTLCache(maxsize=512, ttl=60)`, singleton in-process.

**(b) Mecanismo al atomo**
Un GET a /geo/, /entities/ o /platforms/ computa una clave string determinista = METHOD:PATH?sorted-qs y la busca en un cachetools.TTLCache in-process (TTL 60s, 512 entradas, LRU). Hit -> copia con meta.cache='hit'; miss -> el handler golpea la DB y cache_set guarda el envelope 2xx. La clave pliega SOLO path + query string ordenado — sin principal de auth, sin tenant, sin pais. Seguro HOY porque hay UNA sola CARDEEP_API_KEY compartida y el pais es ES implicito, asi que todo cuerpo cacheado pertenece al unico tenant y unico pais.

**(c) Costura ES->generico + fix exacto**
El diseno afirma '?country= se auto-particiona en la clave' — cierto SOLO si el pais llega como segmento de path/query (la decision no tomada de faceta 16). La costura es el acoplamiento, porque _cache_key pliega path+query:
- Si el pais entra por PATH (/{cc}/geo/...) o QUERY (?country=CC), la clave YA particiona (path/qs difieren) — sin cambio. Es el diseno mas barato y correcto, y la razon de que faceta 16 deba elegir path/query.
- Si el pais entra por HEADER (X-Country) o TENANT (API-key->pais), _cache_key es CIEGO: /geo/28/entities desde un cliente DE y desde uno ES colisionan en la misma clave, y el DE recibe el cuerpo cacheado de ES-28 hasta el TTL.
Fix exacto: computar un pais EFECTIVO en deps (resuelto de path|query|header|tenant, cayendo a DEFAULT_COUNTRY solo como ancla explicita) e inyectarlo en _cache_key: `key = f'{method}:{cc}:{path}?{qs}'` (o plegar el tenant id resuelto). La nota cache.py:82-85 ya lo manda para multi-tenant; lo mismo aplica a multi-pais. La cache sigue in-memory EUR0.

**(d) Riesgo adversarial concreto**
Alemania onboardeada, pais enhebrado por header/tenant: /geo/28/entities sirve a un cliente DE el cuerpo cacheado de ES-28 (mismo path+query), un bleed cross-country invisible que persiste todo el TTL de 60s sin error. El mismo hueco sirve al tenant A el cuerpo del tenant B en cuanto existan keys por tenant (el aviso P2 exacto del audit).

**(e) Criterio de sellado + verificacion multi-via**
1. Test de aislamiento: cache_clear() [VERIFIED cache.py:168-170], pedir /geo/28/... como ES (miss->store), luego como DE (debe ser MISS, no el cuerpo ES); asegurar entradas cacheadas distintas.
2. Test de composicion de clave (caja blanca): _cache_key de dos requests que solo difieren en el pais efectivo devuelve strings distintos.
3. No-bleed e2e en la golden (faceta 29): /geo/X y /geo/ES devuelven sets de cdp_code disjuntos incluso con cache caliente.
4. Si se elige path/query: regresion que asegura que la clave ya difiere (la URL porta el pais; no existe via header-only).

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
[VERIFIED NEXT-LEVEL.md:777-783] **darkweak/souin** (MIT [VERIFIED], EUR0) — https://github.com/darkweak/souin — elevar el TTLCache in-process (por-worker, se pierde al reiniciar, thundering-herd en clave fria) a una cache de BORDE compartida RFC-7234 montada en el Caddy del reverse-proxy que la faceta 20 (TLS) ya anade: compartida entre workers, persistente a reinicios, con stale-while-revalidate (nunca un 500 en frio) y request coalescing (N peticiones identicas simultaneas -> 1 query). Su clave incluye el pais efectivo (Vary), cerrando el bleed de cache.py:79-86 en el borde con CERO cambio de app.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** _cache_key pliega solo method+path+sorted-qs, SIN dimension auth/tenant/pais [VERIFIED cache.py:79-94, auto-marcado :82-85]. Si faceta 16 enhebra el pais por header/tenant (no path/query), la clave es ciega y colisiona entre paises. Superficie afectada acotada a /geo/,/entities/,/platforms/ [VERIFIED :57-62] (/stats no se cachea).
- **Fix — propuesta [no implementada].** Computar pais EFECTIVO en deps (path|query|header|tenant, DEFAULT_COUNTRY solo como ancla explicita) e inyectarlo: key = f'{method}:{cc}:{path}?{qs}'. Si faceta 16 elige path/query, la clave ya particiona sin cambio (diseno preferido). Cache sigue in-memory EUR0.
- **Adversarial (DE/FR/IT/PT/no-UE).** DE onboardeada con pais por X-Country/tenant: /geo/28/entities sirve a un cliente DE el cuerpo cacheado de ES-28 (mismo path+query), bleed invisible durante el TTL de 60s, sin error; y tenant A recibe el cuerpo de tenant B con keys por tenant.
- **Sellado + verificación multi-vía.** (1) cache_clear() [cache.py:168-170] + pedir /geo/28 como ES (store) luego DE (MISS, no el cuerpo ES); (2) _cache_key caja-blanca: requests que solo difieren en pais -> claves distintas; (3) no-bleed e2e (faceta 29) con cache caliente: cdp_code disjuntos; (4) si path/query, regresion de que la URL porta el pais.
- **Herramienta NEXT-LEVEL (€0).** [VERIFIED NEXT-LEVEL.md:777-783] darkweak/souin (MIT, EUR0) https://github.com/darkweak/souin — cache de borde compartida RFC-7234 en el Caddy de la faceta 20, persistente, SWR + coalescing, con clave que incluye el pais efectivo (Vary), cerrando el bleed de cache.py:79-86 sin cambio de app.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f18"></a>

### Faceta 18 · Rate-limit: import-time, mono-proceso, por país

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/ratelimit.py:72` — `_ENABLED: bool = os.environ.get("CARDEEP_API_RATELIMIT_ENABLED", "1") != "0"` leido UNA vez al import. [VERIFIED]
- `ratelimit.py:68-71` — NOTE explicito del PROPIO codigo (audit P2 E-ratelimit): "_ENABLED and the RATE_* limits below are read ONCE at import and baked into the Limiter -- unlike require_api_key, which reads os.environ per request. Toggling CARDEEP_API_RATELIMIT_ENABLED (or changing a limit) in an already-running process has NO effect; it requires a process restart." [VERIFIED] — el concern ya esta auto-documentado en el codigo.
- `ratelimit.py:79,82,86` — `RATE_DEFAULT="120/minute"`, `RATE_EXPENSIVE="30/minute"`, `RATE_HEALTH="300/minute"` (o `_NOOP_LIMIT="9999/second"` si disabled), TODOS horneados al import via el ternario sobre `_ENABLED`. [VERIFIED]
- `ratelimit.py:93-102` — `limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_DEFAULT], storage_uri="memory://")`. [VERIFIED]
- `ratelimit.py:100-101` — comentario: "storage_uri='memory://' is the slowapi default (in-process dict). Never change this to Redis -- cardeep-redis is a different project." [VERIFIED] — constraint que fuerza PostgresBucket (no Redis) como la via €0.
- `main.py:125-126` — `app.state.limiter = limiter`; `app.add_middleware(SlowAPIMiddleware)`. [VERIFIED]
- Paralelo estructural en `cache.py:18-24`: "The FastAPI worker runs in a single OS process (uvicorn, single-worker) ... If multi-process uvicorn is ever used, promote to a shared-memory or Redis-backed cache." [VERIFIED] — el mismo defecto (estado en heap por-proceso) afecta cache y rate-limit.

**(b) Mecanismo al atomo**
slowapi `Limiter` con backend `memory://` (dict en el heap del proceso). Por cada request el `SlowAPIMiddleware` (main.py:126) calcula la key con `get_remote_address` (IP del cliente) y decrementa el bucket del limite declarado en el decorador del handler (`@limiter.limit(RATE_DEFAULT)` o `RATE_EXPENSIVE`). Los limites son strings CONSTANTES congelados al import (ternario sobre `_ENABLED`, ratelimit.py:79-86): cambiar la env var o el numero NO surte efecto hasta reiniciar el proceso. El dict vive en el worker: con N workers uvicorn, cada uno mantiene su propio contador -> el limite agregado real es N x el configurado.

**(c) Costura ES->generico (3 defectos acoplados, ninguno por-endpoint)**
1. **Import-time baked**: no hay hot-reload (ratelimit.py:72, 79-86).
2. **memory:// no compartido**: multi-proceso = N buckets independientes (ratelimit.py:101).
3. **key por IP**: no separa pais ni tenant (ratelimit.py:94 `get_remote_address`). En multi-pais/multi-tenant, clientes DE y ES tras el mismo NAT/proxy comparten bucket; o un tenant ruidoso agota el de otro pais.

**(d) Fix exacto**
1. **Sellar el contrato actual**: elevar el NOTE (ratelimit.py:68-71) de comentario a invariante PROBADO (test que afirma que togglear en caliente no surte efecto sin restart — documenta el comportamiento, no lo oculta).
2. **Buckets por pais/tenant**: `key_func` que componga `(tenant_or_country, ip)` cuando la dimension-pais entre por tenant/API-key (acopla facetas 16/19), no solo IP.
3. **Transicion multi-proceso €0**: respaldar el token-bucket con **PyrateLimiter PostgresBucket** sobre el Postgres que el proyecto YA corre (NO Redis, respetando el veto de ratelimit.py:100-101), dando limite AGREGADO correcto entre workers/maquinas. Los limites leidos de tabla -> hot-reload sin restart.
4. **ES byte-identico mientras single-proc**: el bucket PG con la misma key IP y los mismos numeros (120/30/300 por minuto) reproduce el comportamiento actual.

**(d') Riesgo adversarial concreto**
- **Escala (multi-proceso uvicorn)**: limites N veces mas laxos de lo creido (cada worker su dict) — un atacante satura la DB pese al '30/minute' nominal.
- **Operador enganado**: 'ajusta' el limite por pais en caliente y NO cambia nada (sigue el baked al import); cree estar protegido.
- **DE/tenant**: key por IP deja que un tenant tras un proxy compartido agote el bucket de otro pais; o un scraper DE tras CGNAT comparta limite con clientes ES legitimos.

**(e) Sellado + verificacion multi-via**
- **Test single-proc (golden ES)**: los 89 tests existentes verdes con `CARDEEP_API_RATELIMIT_ENABLED=0` (NOOP `9999/second`) intactos.
- **Multi-proc adversarial**: 4 procesos concurrentes contra un endpoint -> el rate AGREGADO respeta el limite (el bucket PG no permite el burst que el `memory://` single-proc dejaria pasar) — espejo de la verificacion (b) de PyrateLimiter en NEXT-LEVEL.md:307.
- **Hot-reload**: cambiar el limite en la tabla -> surte efecto sin restart (probar el guard rompiendolo).
- **Aislamiento tenant/pais**: dos tenants/paises distintos NO comparten bucket (key compuesta).

**(f) Herramienta NEXT-LEVEL**
**PyrateLimiter (RedisBucket/PostgresBucket/MultiprocessBucket)** (MIT [VERIFIED]) https://github.com/vutran1710/PyrateLimiter [NEXT-LEVEL.md:304]. El **PostgresBucket** reusa el Postgres existente (cero infra nueva, €0, respeta el veto a Redis de ratelimit.py:100-101), da rate-limit DISTRIBUIDO battle-tested entre procesos/maquinas y permite key custom por pais/tenant + limites leidos de tabla (hot-reload sin restart). [VERIFIED]. Alternativas: `limits` (storage PG/Redis/Memcached), redis-cell (modulo GCRA exacto `CL.THROTTLE`, self-host €0).

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** ratelimit.py hornea TODO al import: _ENABLED (ratelimit.py:72) y RATE_DEFAULT/EXPENSIVE/HEALTH (ratelimit.py:79-86) se leen una vez via ternario sobre _ENABLED -> togglear/ajustar en caliente NO surte efecto sin restart (el propio codigo lo documenta en el NOTE ratelimit.py:68-71). El Limiter usa storage_uri='memory://' (dict por-proceso, NO compartido entre workers; ratelimit.py:101, con veto explicito a Redis en :100-101) y key_func=get_remote_address (por IP, ratelimit.py:94) que no separa pais ni tenant. cache.py:18-24 sufre el mismo defecto estructural.
- **Fix — propuesta [no implementada].** Sellar el contrato 'ajuste exige restart' como invariante probado (el NOTE ratelimit.py:68-71 a test). key_func compuesta (tenant_or_country, ip) para multi-tenant/pais (acopla facetas 16/19). Respaldar el bucket con PyrateLimiter PostgresBucket sobre el Postgres existente (NO Redis, respeta ratelimit.py:100-101) -> limite agregado correcto multi-proceso + limites leidos de tabla = hot-reload sin restart. Single-proc con misma key IP y numeros (120/30/300 por minuto) = comportamiento byte-identico.
- **Adversarial (DE/FR/IT/PT/no-UE).** Escala multi-proceso uvicorn: limites N veces mas laxos de lo creido (cada worker su propio dict) -> un atacante satura la DB pese al '30/minute' nominal. Un operador cree haber ajustado el limite por pais en caliente y no: el proceso sigue con el viejo baked al import (ratelimit.py:79-86). DE/tenant: la key por IP (get_remote_address) deja que un tenant tras proxy compartido agote el bucket de otro pais, o un scraper DE tras CGNAT comparta limite con clientes ES legitimos.
- **Sellado + verificación multi-vía.** Multi-via: (1) Golden ES single-proc: los 89 tests verdes con CARDEEP_API_RATELIMIT_ENABLED=0 (NOOP 9999/second) intactos. (2) Multi-proc adversarial: 4 procesos concurrentes -> rate AGREGADO respeta el limite (PG bucket niega el burst que memory:// single-proc permitiria; espejo NEXT-LEVEL.md:307). (3) Hot-reload: cambiar el limite en tabla surte efecto sin restart (probar el guard). (4) Aislamiento: dos tenants/paises no comparten bucket (key compuesta).
- **Herramienta NEXT-LEVEL (€0).** PyrateLimiter (RedisBucket/PostgresBucket/MultiprocessBucket) (MIT [VERIFIED]) https://github.com/vutran1710/PyrateLimiter [NEXT-LEVEL.md:304]. PostgresBucket reusa el Postgres que el proyecto ya corre (cero infra nueva, €0, respeta el veto a Redis de ratelimit.py:100-101): rate-limit distribuido battle-tested multi-proceso/multi-maquina + key custom por pais/tenant + limites de tabla (hot-reload). Alt: 'limits' (storage PG), redis-cell (GCRA CL.THROTTLE self-host €0).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f19"></a>

### Faceta 19 · Auth + fail-fast de prod (invariancia multi-país)

**(a) Code_hints verificados a la fuente real**
- **`require_api_key`** [VERIFIED services/api/deps.py:32-49]: lee `CARDEEP_API_KEY` POR REQUEST (`os.environ.get` [VERIFIED deps.py:40]). Si no hay key + `is_prod()` -> 503 fail-closed [VERIFIED deps.py:42-46]; si no hay key + dev -> publico (`return` [VERIFIED deps.py:47]); si hay key + `x_api_key != configured_key` -> 401 [VERIFIED deps.py:48-49]. `is_prod` se importa de `pipeline.config_guard` [VERIFIED deps.py:15].
- **El gate de arranque** `require_prod_secrets((DSN, 'CARDEEP_DSN'), require_api_key=True)` corre en el `lifespan` [VERIFIED services/api/main.py:106, dentro de :100-111].
- **`pipeline/config_guard.py`**: `is_prod()` lee `CARDEEP_ENV` default 'dev' [VERIFIED config_guard.py:57-69]; `assert_safe_dsn` lanza RuntimeError en prod si el DSN aun lleva el marcador `cardeep_dev_only` [VERIFIED config_guard.py:76-106, marcador en :44]; `require_api_key_or_fail` lanza en prod si no hay key [VERIFIED config_guard.py:113-133]; el agregado `require_prod_secrets` [VERIFIED config_guard.py:140-170].
- **PII servida tras auth**: la proyeccion `servable_entity` expone `address, postcode, lat, lon, phone, email, website` [VERIFIED migrations/0046_servable_entity_status_filter.sql:18-19] y NO proyecta country_code (faceta 1), asi que la PII de TODOS los paises fluye por la MISMA proyeccion.
- CORS sin HSTS [VERIFIED main.py:135-144].

**(b) Mecanismo al atomo**
Dos lineas de defensa, ambas country-invariantes por construccion. **(1) Gate de arranque** (main.py:106 -> config_guard.require_prod_secrets): solo armado si `CARDEEP_ENV=prod`. En prod (a) rechaza arrancar si el DSN resuelto contiene `cardeep_dev_only` (assert_safe_dsn), (b) rechaza arrancar si `CARDEEP_API_KEY` no esta (require_api_key_or_fail). En dev/test (CARDEEP_ENV unset -> 'dev') es no-op TOTAL — arranque byte-identico. **(2) Gate por-request** (deps.py require_api_key, Depends en cada endpoint de datos, NO en /health): no-key+prod -> 503; key+header malo -> 401; no-key+dev -> publico. La key se lee de env EN CADA request, asi que hay exactamente UNA key global, sin dimension tenant/pais. La misma key abre la PII de todos los paises porque la proyeccion (servable_entity) y todos los routers son country-blind hoy. La seguridad es una UNICA puerta para todos los paises — correcto como invariancia, pero ACOPLA con la cache: `_cache_key` no tiene dimension tenant/pais (faceta 17), asi que introducir keys por tenant/pais serviria a A el cuerpo cacheado de B.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** **ES -> generico (INVERSO).** La capa auth/fail-fast es genuinamente country-invariante — y eso es lo CORRECTO: la misma puerta debe proteger la PII de DE/FR/IT/PT/MX/JP exactamente como protege la de ES; la escala de cobertura sigue siendo senal competitiva tras auth para CADA pais. La costura NO es 'hacer auth por-pais' — es lo OPUESTO: SELLAR que auth queda uniforme y hacer EXPLICITO que el modelo de key-unica es una PRECONDICION sobre la multi-tenancy. El `config_guard` hand-rolled (checks `in` de string: `DEV_CREDENTIAL_MARKER in dsn` [VERIFIED config_guard.py:101]) es ad-hoc de la era ES: valida un marcador de DSN y la presencia de una key, sin contrato tipado, sin manifiesto de secretos por-pais, y sin asercion de acoplamiento a la cache key. Si/cuando las API keys pasen a por-tenant->pais (la evolucion multi-pais natural), NADA fuerza mecanicamente extender la cache key (faceta 17) primero.
- **Fix — propuesta [no implementada].** **Fix exacto — sellar la invariancia, no fragmentarla:**
1. Mantener UNA puerta auth; anadir un test que asevere que los 18 endpoints de datos llevan `Depends(require_api_key)` y que `/health` NO — asi ninguna superficie de pais queda publica por accidente.
2. Elevar `config_guard` a un CONTRATO tipado (pydantic-settings `BaseSettings`): modelar `{CARDEEP_DSN, CARDEEP_API_KEY, CARDEEP_ENV, CARDEEP_CORS_ORIGINS}` con validators que reproducen el fail-fast prod (DSN no puede contener el marcador dev en prod; key requerida en prod), reemplazando los checks `in` de string por un contrato de secretos validado al boot con error tipado.
3. Couple-guard: test/asercion de que SI existe mas de una key/tenant ENTONCES la cache key DEBE incluir el pais/tenant efectivo (liga mecanicamente faceta 19 -> faceta 17 ANTES de enviar multi-tenant).
4. PII-uniformidad: asevera que la proyeccion servable_entity (post-faceta-1, con country_code) se sirve tras `require_api_key` para CADA pais — ningun camino sin-auth a phone/email/address/lat/lon de ningun pais.
5. ES/dev byte-identico: `CARDEEP_ENV` unset -> todos los guards no-op (contrato config_guard preservado [VERIFIED config_guard.py:16-19]).
- **Adversarial (DE/FR/IT/PT/no-UE).** **Introducir keys por pais/tenant SIN extender la cache key (faceta 17):** el tenant DE recibe el cuerpo cacheado del tenant ES para el mismo path+query (cache `_cache_key` solo pliega `METHOD:PATH?qs`) — bleed cross-tenant invisible hasta el TTL, sirviendo PII de un pais a otro tras una puerta 'segura'. **Segundo:** un prod mal configurado (CARDEEP_ENV=prod pero olvidan CARDEEP_API_KEY) — HOY el doble gate lo ataja (startup RuntimeError [VERIFIED config_guard.py:129-133] + 503 por request [VERIFIED deps.py:42-46]); pero si alguien anade un tenant-resolver que lee la key de otra fuente y bypassa require_api_key, la senal de cobertura de TODOS los paises queda abierta. **Tercero:** el check string `'cardeep_dev_only' in dsn` [VERIFIED config_guard.py:101] es fragil — un DSN prod que casualmente no contenga el marcador pero apunte a una DB dev pasa el gate (falso negativo); un contrato tipado con allow-list de hosts prod lo cierra. **Ruido/no-UE:** da igual el pais — la puerta es UNA; el riesgo es de acoplamiento (cache) y de bypass, no de fuga por-pais directa.
- **Sellado + verificación multi-vía.** **Criterio de sellado + verificacion multi-via:**
- **Auth uniforme:** test que enumera `app.routes` y asevera `Depends(require_api_key)` en los 18 data endpoints y su AUSENCIA en `/health`.
- **Fail-fast:** con CARDEEP_ENV=prod + DSN dev-default -> startup RuntimeError [VERIFIED config_guard.py:101-105]; prod + key ausente -> RuntimeError [VERIFIED config_guard.py:129-133] y 503 por request [VERIFIED deps.py:42-46]; key set + header malo -> 401 [VERIFIED deps.py:48-49].
- **Via 1 (Schemathesis):** property-based sobre `/openapi.json` — assert que NINGUNA respuesta sin X-API-Key valida devuelve data de PII para NINGUN pais (todas 401/503), en N=10k casos.
- **Via 2 (couple-guard):** test que falla si existe >1 key y el cache key no incluye pais/tenant.
- **Via 3 (ES byte-identico):** CARDEEP_ENV unset -> guards no-op, los 89 tests API verdes sin cambio.
- **Precondicion que ARRASTRA:** faceta 17 (cache key con dimension pais/tenant) ANTES de multi-tenant auth.
- **Herramienta NEXT-LEVEL (€0).** **Pydantic (pydantic-settings)** — MIT, €0 — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela el config/secret-pack como un `BaseSettings` tipado con validators de coherencia, convirtiendo `config_guard` de checks `in` string a un CONTRATO tipado validado al boot que falla ROJO mecanicamente ante un secreto prod ausente/mal — el mismo patron que NEXT-LEVEL aplica al registry-drift [VERIFIED:584-589]. €0 pip, corre en CI sin DB viva con fixtures [VERIFIED:589]. **Companero de verificacion:** Schemathesis (api-schema-fuzz) — MIT, €0 — https://github.com/schemathesis/schemathesis [VERIFIED:828], que auto-ataca el contrato y, con un check custom de auth+pais, certifica que la puerta protege la PII de TODOS los paises (cero 500/PII-sin-key en N=10k casos) [VERIFIED:826,831]; consume el `/openapi.json` que FastAPI ya expone, cero infra [VERIFIED:830].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f20"></a>

### Faceta 20 · Terminación TLS en el borde (reverse-proxy €0)

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/main.py:153-155` [VERIFIED] — `if __name__ == "__main__": import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8090)`: **HTTP plano, loopback, sin TLS**.
- `migrations/0046_servable_entity_status_filter.sql:18-19` [VERIFIED] — `servable_entity` proyecta `... address, postcode, lat, lon, phone, email, website ...`: **PII de dealer** servida por esta superficie.
- `services/api/main.py:135-144` [VERIFIED] — el unico middleware "de borde" es CORS (`CARDEEP_CORS_ORIGINS`, `allow_methods GET/OPTIONS`, `allow_headers X-API-Key,Content-Type`). **No hay HSTS, ni `X-Content-Type-Options`, ni `X-Frame-Options`, ni `Referrer-Policy`, ni `Permissions-Policy`** en toda la app.
- `services/api/deps.py:32-49` [VERIFIED] — `require_api_key` protege los endpoints de PII, pero **auth != cifrado de transporte**: autentica al llamante, no cifra el canal.

**(b) El mecanismo al atomo**
uvicorn liga `127.0.0.1:8090` en HTTP plano. La superficie servida incluye PII (telefono/email/direccion postal/lat-lon) directa desde `servable_entity` [`0046:18-19`]. **No existe terminacion TLS, ni HSTS, ni security headers** en ningun punto de la app (CORS es el unico middleware ademas de slowapi). La app **hace bien** en quedarse HTTP en loopback —TLS pertenece a un borde, no al ASGI app— pero **ese borde no existe todavia**, asi que cualquier exposicion no-loopback sirve PII en claro.

**(c) Costura ES->generico**
Esta faceta es **pais-INVARIANTE**: un unico borde TLS protege la PII de **todos** los paises identicamente; no hay codigo per-pais aqui. La costura es que el borde es un **gate de infra+DNS, no de codigo**, y hoy esta ausente. Es ademas el **mismo borde** sobre el que cuelgan la cache Souin (facetas 17/27) y los security headers.

**(d) Fix exacto**
1. **Reverse-proxy EUR0 delante:** **Caddy** con HTTPS automatico (Let's Encrypt) terminando TLS y haciendo proxy al loopback uvicorn (`127.0.0.1:8090` se queda HTTP, sin cambios).
2. **Headers en el borde:** `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
3. **Nunca exponer 8090 directo:** firewall/bind a loopback. **Cero cambio de codigo de app** — ya habla HTTP en loopback por diseno.
4. **Un solo borde:** el mismo Caddy es el punto de montaje de Souin (facetas 17/27) — construir una vez con `xcaddy build --with souin`.

**(e) Criterio de sellado + verificacion multi-via**
- **Probe TLS:** `curl https://host` con cert valido; `curl http://host` redirige 301->https (o rechaza); el puerto 8090 **no** alcanzable desde fuera del host (`ss`/`nmap`).
- **Assert de headers:** la respuesta lleva HSTS + nosniff + X-Frame-Options + Referrer-Policy (test automatico de headers en CI contra staging, p.ej. `testssl.sh`).
- **Negativo PII-en-claro:** una captura en el cable / proxy muestra **cero** telefono/email en texto plano (solo TLS).
- **Invariancia de pais:** la misma config de borde sirve `/geo/ES/...` y `/geo/DE/...` — un cert, una politica de headers, aseverada identica.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**Caddy (reverse-proxy auto-TLS) + darkweak/souin** como su modulo de cache [VERIFIED `NEXT-LEVEL.md:780-782`; souin MIT; https://github.com/darkweak/souin; EUR0=True]. La biblia **pareja explicitamente** el Caddy del borde-TLS con Souin: *"se instala en el reverse-proxy que YA va a existir"* y *"Pairea con la mejora ... reverse-proxy Caddy TLS"* [VERIFIED:778,782]. Caddy da **disponibilidad grado-CDN + HTTPS automatico sobre un loopback de PII a EUR0**; Souin anade cache RFC-7234 compartida, persistente a reinicios y stale-while-revalidate sobre el mismo borde. Alternativas: Varnish, nginx `proxy_cache` [VERIFIED:781]. **Honestidad:** la linea de la biblia etiqueta la licencia de **Souin** ([VERIFIED] MIT), no la de **Caddy**; la licencia de Caddy es Apache-2.0 [ASSUMED — verificar a fuente en la adopcion]. El atomo TLS es Caddy; Souin es el inquilino que monta encima.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** PAIS-INVARIANTE: main.py:153-155 corre uvicorn en HTTP plano loopback 127.0.0.1:8090 sin TLS; servable_entity 0046:18-19 sirve PII (phone/email/address/lat/lon); main.py:135-144 solo tiene CORS, sin HSTS ni security headers. require_api_key (deps.py:32-49) autentica pero no cifra el canal. El borde TLS es un gate de infra/DNS ausente, el mismo sobre el que cuelgan Souin y los headers.
- **Fix — propuesta [no implementada].** Caddy auto-TLS (Let's Encrypt) delante haciendo proxy al loopback HTTP (app sin cambios); anadir en el borde HSTS+nosniff+X-Frame-Options+Referrer-Policy+Permissions-Policy; firewall que nunca expone 8090; construir el Caddy una vez con xcaddy --with souin para reusarlo en faceta 17/27.
- **Adversarial (DE/FR/IT/PT/no-UE).** Exponer 8090 directo en prod filtra la PII de dealers de TODOS los paises en texto plano; sin HSTS hay downgrade a HTTP en el primer hop. Un prod mal configurado que ligue 0.0.0.0:8090 sirve PII abierta aun con API-key, porque auth no cifra el canal.
- **Sellado + verificación multi-vía.** curl https con cert valido + http redirige/rechaza + 8090 no alcanzable off-host (ss/nmap); assert de headers HSTS/nosniff/X-Frame/Referrer en CI; captura de cable sin PII en claro; misma config de borde para /geo/ES y /geo/DE (un cert, identica).
- **Herramienta NEXT-LEVEL (€0).** Caddy auto-TLS + darkweak/souin (modulo cache) [VERIFIED NEXT-LEVEL.md:780-782; souin MIT; https://github.com/darkweak/souin; EUR0]. La biblia pareja el Caddy TLS con Souin [VERIFIED:778,782]; disponibilidad grado-CDN sobre loopback de PII; alts Varnish/nginx [VERIFIED:781]. NOTA: la biblia etiqueta la licencia de Souin (MIT), no la de Caddy (Apache-2.0 [ASSUMED — verificar a fuente]).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f21"></a>

### Faceta 21 · CORS multi-origen / per-deployment

**(a) Verificacion de code_hints [VERIFIED]**
- **Configuracion**: `_cors_origins = os.environ.get("CARDEEP_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173")` [VERIFIED services/api/main.py:135-138]; `CORSMiddleware(allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()], allow_methods=["GET","OPTIONS"], allow_headers=["X-API-Key","Content-Type"])` [VERIFIED main.py:139-144].
- **Sin `allow_credentials`** → default Starlette `allow_credentials=False`: peticiones credentialed (cookies) NO se reflejan; el auth viaja por header `X-API-Key` (permitido) [VERIFIED por ausencia del kwarg, main.py:139-144].
- **Orden de middleware**: `app.add_middleware(SlowAPIMiddleware)` en :126, exception handler :127, `CORSMiddleware` anadido en :139 (ULTIMO). Starlette aplica el stack en orden INVERSO de adicion → el ultimo anadido es el MAS EXTERNO. CORS es outermost y maneja el preflight primero [VERIFIED main.py:126-144 + comentario :133 "Added last so it is the outermost middleware and handles preflight first"].
- `include_router` despues de los middleware [:146-150]; `require_api_key` es `Depends` por-ruta, corre dentro de la ruta (innermost) [VERIFIED deps.py:32-49].

**(b) Mecanismo al atomo**
Starlette construye una cebolla: CORSMiddleware (externa) → SlowAPIMiddleware (interna) → router → `Depends(require_api_key)`. Un preflight OPTIONS del navegador con `Origin`+`Access-Control-Request-*` lo responde CORSMiddleware ANTES de rate-limit/auth, devolviendo `Access-Control-Allow-Origin` solo si el Origin esta en `allow_origins` (lista de match exacto, sin comodin). Un GET no-preflight pasa: CORS registra el Origin, rate-limit lo cuenta, la ruta valida `X-API-Key`. `allow_origins` es lista de strings EXACTOS (Starlette tambien soporta `allow_origin_regex`, no usado). Default = 4 origenes localhost de dev; en prod, `CARDEEP_CORS_ORIGINS` debe setearse o los front-ends quedan bloqueados.

**(c) Costura ES->generico + fix exacto**
Un despliegue pan-EU sirve front-ends por pais (es.cardeep, de.cardeep, fr.cardeep) en origenes distintos. El unico env var debe llevar el allow-list explicito de TODOS los origenes-pais; **no hay scoping CORS por pais** (CORS es country-invariante, una puerta para todos). El riesgo es operacional, no de codigo: (a) un default mal-portado a prod deja solo origenes localhost (todo front real bloqueado) o, peor, alguien pone `*`; (b) `*` con auth por header es riesgo de exposicion; (c) como `allow_credentials=False`, los navegadores ACEPTAN `*` para peticiones no-credentialed, asi que un `allow_origins=["*"]` descuidado abre en silencio la superficie tras la key.

**Fix:**
1. CORS sigue country-invariante pero la lista de origenes pasa por un settings **Pydantic** VALIDADO que (a) rechaza `*` en prod (`CARDEEP_ENV=prod`) — simetria fail-fast con `require_prod_secrets` [main.py:106], (b) exige `https://` en prod, (c) de-dup + valida forma de URL.
2. Preservar el orden (CORS outermost) como INVARIANTE testeado: un refactor que anada un middleware despues de CORS (haciendolo no-outermost) deja que rate-limit 429ee un preflight OPTIONS (sin headers CORS en el 429 → el navegador muestra fallo CORS opaco).
3. Nunca `allow_origins=["*"]`; si se necesita patron de subdominio por pais, usar `allow_origin_regex` `^https://[a-z]{2}\.cardeep\.<tld>$` (explicito, acotado).
4. ES/dev byte-identico: lista localhost default intacta con `CARDEEP_ENV` sin setear.

**(d) Riesgo adversarial concreto**
- **DE**: de.cardeep.de da consola CORS-blocked porque el env var de prod se copio de dev (solo localhost) → producto DE a oscuras con la API arriba.
- **`*` en prod**: como `allow_credentials=False`, los navegadores aceptan `*` para reads no-credentialed → cualquier web puede fetchear la senal de cobertura (key-gated) si una key se filtra, deshaciendo el movimiento del audit de poner la escala tras auth.
- **Regresion de preflight**: si se anade un middleware despues de CORS, un OPTIONS a `/geo/28/entities` se rate-limita/autentica antes que CORS, devolviendo 429/401 SIN `Access-Control-Allow-Origin` → el navegador reporta error CORS generico, enmascarando el status real; el front FR aparece "CORS-roto" intermitente bajo carga.

**(e) Sellado + verificacion multi-via**
- **Criterio**: CORS es outermost; prod rechaza `*` y origenes no-https; el preflight OPTIONS devuelve 200 + ACAO correcto para un origen permitido y NO se rate-limita/autentica; un origen no listado no recibe ACAO.
- **Via 1 Schemathesis/httpx**: OPTIONS preflight con Origin permitido → ACAO==ese origen y `Access-Control-Allow-Methods`⊇GET; con Origin no permitido, sin header ACAO. Correr por cada origen-pais configurado.
- **Via 2 invariante de orden**: asertar que `CORSMiddleware` es el outermost en `app.user_middleware` (chequeo de indice) para que la cebolla no se invierta en silencio; test de que un preflight bajo rate-limit disparado SIGUE devolviendo headers CORS.
- **Via 3 gate Pydantic (espejo require_prod_secrets)**: un prod con `CARDEEP_CORS_ORIGINS="*"` o un origen `http://` falla el arranque; testearlo booteando con ese env y asertando que el guard lanza.
- **Via 4 golden ES/dev**: con `CARDEEP_ENV` sin setear y sin env var, `allow_origins` == los 4 localhost default (byte-identico).

**(f) Herramienta NEXT-LEVEL**
**Schemathesis** (MIT) — https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828]. Dirige el contrato OpenAPI y, con un check CORS/preflight, certifica mecanicamente que OPTIONS en cada endpoint devuelve los headers `Access-Control-*` documentados para origenes permitidos y rechaza los no listados, en N casos generados — convierte "CORS bien configurado por despliegue" en un gate por-push, no un curl manual. **Honestidad de alcance**: NO hay libreria CORS dedicada €0 en NEXT-LEVEL.md; la correccion del allow-list de origenes es un gate de config de despliegue que empareja con la faceta de borde (Caddy/TLS, faceta 20) y se endurece mejor con un validador **Pydantic** (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587] que rechaza `*`/origenes no-https en prod (simetria fail-fast con `require_prod_secrets`, main.py:106). El fit de herramienta es parcial y se declara como tal.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** CORS es country-invariante (una puerta para todos) pero el unico env var CARDEEP_CORS_ORIGINS (default 4 localhost, main.py:135-144) debe enumerar explicitamente los origenes de cada front-end por pais (es./de./fr.cardeep); no hay scoping por pais. Como allow_credentials=False, un '*' descuidado se acepta para reads no-credentialed y abre la superficie tras la API-key.
- **Fix — propuesta [no implementada].** Parsear CARDEEP_CORS_ORIGINS por un settings Pydantic que rechaza '*' y origenes no-https en prod (simetria con require_prod_secrets main.py:106), de-dup y valida URL; preservar CORS outermost como invariante testeado; usar allow_origin_regex acotado en vez de '*' para subdominios por pais; default localhost intacto en dev.
- **Adversarial (DE/FR/IT/PT/no-UE).** DE bloqueado (env de prod copiado de dev, solo localhost) -> producto a oscuras con API arriba; '*' en prod -> cualquier web fetchea la cobertura key-gated si una key se filtra (deshace el audit); middleware anadido tras CORS -> preflight OPTIONS rate-limitado/401 SIN headers CORS -> el front FR aparece CORS-roto intermitente bajo carga.
- **Sellado + verificación multi-vía.** Criterio: CORS outermost; prod rechaza '*'/no-https; preflight permitido devuelve 200+ACAO sin rate-limit/auth; origen no listado sin ACAO. Via1 Schemathesis/httpx OPTIONS por origen-pais. Via2 invariante de indice outermost en app.user_middleware + preflight bajo rate-limit sigue con headers CORS. Via3 gate Pydantic falla arranque con '*'/http en prod. Via4 golden dev 4 localhost byte-identico.
- **Herramienta NEXT-LEVEL (€0).** Schemathesis (MIT) https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828] — check CORS/preflight certifica ACAO por origen y rechazo de no-listados por-push; + Pydantic (MIT) https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587] valida el allow-list (rechaza '*'/http en prod). Fit PARCIAL: no hay libreria CORS dedicada en NEXT-LEVEL; empareja con el borde Caddy/TLS (faceta 20).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f22"></a>

### Faceta 22 · /search typo-tolerante country-scoped

**(a) Code_hints verificados**
- **/search AUSENTE: [VERIFIED grep "search" -i services/api = "No matches found"]** — no hay endpoint ni referencia a search en toda la API.
- **Sustrato instalado:** **[VERIFIED migrations/0005_types_and_guards.sql:6]** `CREATE EXTENSION IF NOT EXISTS pg_trgm;` (comentario "fuzzy name/alias search (GIN trigram)"); **[:7]** `CREATE EXTENSION IF NOT EXISTS btree_gin;` (comentario "composite GIN (enum + trigram) for filtered search").
- **Indices GIN trgm:** **[VERIFIED migrations/0006_entity_evolve.sql:62]** `idx_entity_tradename_trgm ON entity USING gin (trade_name gin_trgm_ops)`; **[:63]** `idx_entity_legalname_trgm ON entity USING gin (legal_name gin_trgm_ops)`; **[VERIFIED migrations/0007_organization.sql:18]** `idx_org_name_trgm ON organization USING gin (name gin_trgm_ops)`.
- **Estos indices son trgm PUROS, monocolumna, SIN dimension pais** [VERIFIED] — **no existe** indice compuesto `(country_code, ... gin_trgm_ops)` (grep solo encontro los 3 monocolumna) — el hueco de la faceta 23.
- **Helpers reusables:** `page_slice` **[VERIFIED services/api/routers/geo.py:21 import, :280,:335 uso]**; envelope `ok()` (deps.py). Cache key pliega path+query **[VERIFIED services/api/cache.py:79-94]** -> `?q=`/`?country=` auto-particionan **si** el pais es query param o segmento de path.

**(b) Mecanismo al atomo**
El endpoint de mayor leverage que el producto **NO expone** pese a tener el sustrato instalado desde 0005/0006. Una query trgm `%` (similarity) sobre `servable_entity.trade_name/legal_name` devuelve matches typo-tolerantes ordenados por similitud; el indice GIN trgm sirve el operador `%`.

**(c) Costura ES->generico (nacido generico o se vuelve la proxima costura ES)**
Construir `GET /{country_code}/search?q=&page=&size=` **sobre `servable_entity`** (tras faceta 1), `WHERE country_code=$cc AND (trade_name % $q OR legal_name % $q) ORDER BY similarity DESC`, con `set_limit` (umbral trgm) como **constante de modulo**, paginado con `page_slice`, RATE_EXPENSIVE + cacheado. Si se construye **country-blind hereda la enfermedad de los agregados**: devuelve dealers de TODOS los paises mezclados, y un umbral trgm implicito/magico se comporta distinto entre idiomas.

**(d) Riesgo adversarial**
**DE/FR/IT/PT:** sin pais en la clave/predicado, `/search?q=auto` devuelve dealers ES+DE+FR intercalados por similitud cruda — un usuario aleman buscando recibe dealers espanoles rankeados por encima de los locales. **Cross-language threshold:** un umbral trgm fijo afinado para trade_names espanoles mis-dispara con palabras compuestas alemanas / acentos FR/PT — magico, recall impredecible entre idiomas. **No-Latino/ruido** (si aterriza un pais CJK/cirilico): trgm sobre nombres no-transliterados degrada (acopla con anyascii).

**(e) Criterio de sellado + verificacion multi-via**
1. **HTTP-vs-SQL** (patron [VERIFIED tests/test_api_gaps.py:50-61]): la lista del endpoint == query asyncpg independiente con el mismo `country_code=$cc AND trade_name % $q`.
2. **Aislamiento pais:** `/DE/search` nunca devuelve un `cdp_code` ES; con ES+DE sembrado, el `country_code` del set es uniformemente el CC pedido (prefijos cdp_code disjuntos).
3. **Aislamiento cache:** `/DE/search?q=X` y `/ES/search?q=X` nunca comparten cuerpo cacheado (claves distintas: segmento/param de pais distinto) **[VERIFIED cache.py:79-94]**.
4. **Golden de relevancia:** qrels fijo por pais; el umbral es una constante explicita, aseverada.

**(f) Herramienta NEXT-LEVEL**
**postgrespro/rum — PostgreSQL-like (BSD-style permisiva, "similar to PostgreSQL")** — https://github.com/postgrespro/rum **[VERIFIED NEXT-LEVEL.md:724]**, via *search-ranked-in-postgres* **[VERIFIED NEXT-LEVEL.md:721-727]**. Eleva `ORDER BY similarity` (parecido de cadena) a **relevancia REAL** dentro de Postgres (tsvector/tsquery + indice RUM que guarda el rank DENTRO del indice para `ts_rank` sub-50ms, con pg_trgm como rama de typos), y un indice **compuesto `(country_code, tsv)`** garantiza que `/search?country=ES` **nunca toca filas DE** — EUR0, cero datastore nuevo, reusa el sustrato exacto 0005:6/0006:62-63/0007:18. **Gate companero:** **AmenRa/ranx — MIT** — https://github.com/AmenRa/ranx **[VERIFIED NEXT-LEVEL.md:756]** (*search-quality-eval-gate* [VERIFIED:753-759]): qrels por `country_code` en CI (nDCG@k/MRR), build falla si la relevancia regresa; ES sellado no se degrada al anadir DE. **Adyacentes:** **anyascii — ISC** https://github.com/anyascii/anyascii **[VERIFIED NEXT-LEVEL.md:482]** (normalizacion cross-script); **meilisearch — MIT** **[VERIFIED NEXT-LEVEL.md:748]** (autocompletado sub-10ms si PG-puro se queda corto).

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** /search NO existe (grep services/api=0) pese a sustrato instalado desde 0005/0006 (pg_trgm 0005:6, btree_gin 0005:7, GIN trgm en trade_name/legal_name 0006:62-63, organization.name 0007:18). Los indices trgm son monocolumna SIN dimension pais; si el endpoint nace country-blind hereda la enfermedad de los agregados (mezcla paises) y el umbral trgm queda magico entre idiomas.
- **Fix — propuesta [no implementada].** GET /{country_code}/search?q=&page=&size= sobre servable_entity (tras faceta 1): WHERE country_code=$cc AND (trade_name % $q OR legal_name % $q) ORDER BY similarity DESC, set_limit (umbral trgm) como constante de modulo, page_slice, RATE_EXPENSIVE+cacheado. Pais en segmento de path (o ?country= default ES) threadeado a WHERE Y a la cache key (cache.py:79-94 pliega path+query). A escala requiere el indice compuesto (faceta 23). Nacido country-scoped.
- **Adversarial (DE/FR/IT/PT/no-UE).** DE/FR/IT/PT: sin pais en clave/predicado, /search?q=auto devuelve ES+DE+FR intercalados por similitud cruda (usuario aleman ve dealers espanoles arriba). Umbral trgm fijo afinado a ES mis-dispara con compuestos alemanes/acentos FR-PT (recall impredecible entre idiomas). Pais CJK/cirilico: trgm sin transliterar degrada (acopla anyascii).
- **Sellado + verificación multi-vía.** (1) HTTP-vs-SQL (test_api_gaps.py:50-61): lista endpoint == query asyncpg con country_code=$cc AND trade_name % $q. (2) /DE/search nunca devuelve cdp_code ES; con ES+DE sembrado, country_code uniforme = CC pedido (prefijos disjuntos). (3) Cache: /DE/search?q=X y /ES/search?q=X claves distintas, sin cuerpo compartido (cache.py:79-94). (4) Golden relevancia: qrels por pais, umbral constante explicita.
- **Herramienta NEXT-LEVEL (€0).** postgrespro/rum — PostgreSQL-like BSD-style [VERIFIED NEXT-LEVEL.md:724] — https://github.com/postgrespro/rum (search-ranked-in-postgres): relevancia real (tsvector+RUM rank-en-indice sub-50ms, pg_trgm rama typos) con indice compuesto (country_code,tsv) que garantiza aislamiento pais; reusa sustrato 0005:6/0006:62-63/0007:18, EUR0. Companero AmenRa/ranx MIT [VERIFIED:756] (qrels por country_code en CI, ES no degrada al anadir DE). Adyacentes: anyascii ISC [VERIFIED:482], meilisearch MIT [VERIFIED:748].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f23"></a>

### Faceta 23 · Índice compuesto GIN (country_code, trgm)

**(a) code_hints VERIFICADOS**
- **pg_trgm + btree_gin instalados** [VERIFIED migrations/0005_types_and_guards.sql:6-7]: `CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS btree_gin;` — el comentario :7 literalmente dice "composite GIN (enum + trigram) for filtered search".
- **Indices trgm SIN dimension pais** [VERIFIED migrations/0006_entity_evolve.sql:62-63]: `CREATE INDEX IF NOT EXISTS idx_entity_tradename_trgm ON entity USING gin (trade_name gin_trgm_ops); CREATE INDEX IF NOT EXISTS idx_entity_legalname_trgm ON entity USING gin (legal_name gin_trgm_ops);`.
- **Indice compuesto inexistente** [VERIFIED] — grep de `gin_trgm_ops`/`btree_gin`/`USING gin` por las migraciones de pais (0042/0043/0053/0055/0056) no devuelve ningun DDL de indice compuesto; ninguna migracion crea (country_code, trade_name).
- **/search ausente** [VERIFIED grep 'search' services/api -> NONE] — depende de la faceta 22 (el endpoint nuevo).

**(b) El mecanismo al atomo**
A escala mono-pais (ES) el GIN trgm puro basta. Pero /search (faceta 22) hara `WHERE country_code=$cc AND (trade_name % $q OR legal_name % $q)`. Con el indice trgm country-blind, Postgres hace trigram-scan de TODAS las trade_name del planeta y luego post-filtra el pais en heap. La extension btree_gin (instalada 0005:7) es justo la que permite anteponer una columna escalar (el CHAR(2)/enum country_code) al operador trgm en un mismo indice GIN, eliminando el post-filtro.

**(c) Costura ES->generico**
El sustrato lleva instalado desde 0005/0006 pero el indice que combina pais+trgm no se crea en ninguna migracion. La costura es puramente de ESCALA: no rompe ES (un pais), se manifiesta al coexistir N paises grandes.

*Costura, fix, adversarial, sellado y herramienta NEXT-LEVEL: en la **Ficha operativa** inmediatamente debajo.*

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El sustrato (pg_trgm 0005:6, btree_gin 0005:7, indices trgm 0006:62-63) esta instalado, pero el indice compuesto (country_code, trade_name gin_trgm_ops) NO existe en ninguna migracion [VERIFIED grep]. /search country-scoped (faceta 22) filtrara pais y luego hara trigram-scan global con post-filtro, en vez de un scan acotado al pais.
- **Fix — propuesta [no implementada].** En la migracion de onboarding de pais: `CREATE INDEX IF NOT EXISTS idx_entity_country_tradename_trgm ON entity USING gin (country_code, trade_name gin_trgm_ops);` (btree_gin habilita la columna lider escalar). Aditivo, idempotente (IF NOT EXISTS), EUR0; rollback = DROP INDEX. Opcional/solo-a-escala: justificado cuando coexisten >=2 paises grandes. Igual para legal_name si /search lo cubre.
- **Adversarial (DE/FR/IT/PT/no-UE).** Con N paises grandes y un q corto, /search?country=ES degrada a trgm-scan de TODAS las trade_name del planeta y luego descarta los no-ES: la latencia crece con el total GLOBAL, no con el tamano del pais consultado. Un q ruidoso de 2 caracteres amplifica esto a un scan casi-total del indice. DE/FR/IT con censos densos hunden la latencia de las consultas ES y viceversa.
- **Sellado + verificación multi-vía.** Criterio: el plan de /search usa el indice compuesto y la latencia depende solo del pais consultado. Multi-via: (a) EXPLAIN ANALYZE muestra Bitmap Index Scan sobre idx_entity_country_tradename_trgm, no scan del trgm global + filtro; (b) latencia — p99 de /search?country=ES acotado por filas ES, invariante al anadir filas DE (load test); (c) 2a via de correccion — resultados identicos al plan country-then-trgm; (d) aislamiento — la columna lider country_code garantiza que /search?country=ES nunca puntua filas DE.
- **Herramienta NEXT-LEVEL (€0).** postgrespro/rum (search-ranked-in-postgres) — PostgreSQL-like / BSD-style permisiva [VERIFIED NEXT-LEVEL.md:724] — https://github.com/postgrespro/rum . Eleva el filtro trgm compuesto a un indice RUM sobre (country_code, tsv) que almacena rank/posiciones DENTRO del indice, resolviendo ORDER BY ts_rank sub-50ms sin re-rankear en heap (GIN no puede), con pg_trgm como rama de typos. Aislamiento por la columna lider compuesta [NEXT-LEVEL:727: 'el indice compuesto (country_code, tsv) garantiza que /search?country=ES nunca toca filas DE']. Migracion aditiva (columna tsv GENERATED + CREATE INDEX rum); rollback DROP.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f24"></a>

### Faceta 24 · country_code aditivo en salida + meta.country

**(a) Code_hints VERIFICADOS leyendo la fuente real**
- [VERIFIED services/api/routers/entities.py:80-87] get_entity hace `data = dict(row)` y anade created_at, last_seen, available_inventory, canonical_cdp_code, n_aliases, queried_cdp_code. SIN country_code (la fila entity LO tiene desde 0052 pero no se proyecta ni emite).
- [VERIFIED services/api/routers/geo.py:418-420] el nodo province del arbol emite {code, name, ccaa_code, ccaa_name}; sin country_code.
- [VERIFIED services/api/routers/vehicles.py:99-106] vehicle_detail `data = dict(row)` + price/first_seen/last_seen/is_canonical/canonical_vehicle_ulid; sin country.
- [VERIFIED services/api/routers/platforms.py:69-85] la respuesta es ok(items, page, size, returned, has_more, platform, cdp_code); los items llevan dealer_province/dealer_municipality pero no country.
- [VERIFIED services/api/deps.py:52-53] `def ok(data, **meta): return JSONResponse({'ok': True, 'data': data, 'error': None, 'meta': meta or None})`. Helper de envelope unico; meta es el sitio natural de un country top-level.
- [VERIFIED services/api/routers/entities.py:132-133] el SELECT de inventory proyecta v.currency por fila; la moneda ya viaja per-vehicle, asi que no requiere cambio.

**(b) Mecanismo al atomo**
Cada router construye su respuesta por `dict(row)` + claves derivadas ad-hoc, envuelta por ok(data, **meta). Hay ~18 proyecciones de salida en ops/entities/geo/vehicles/platforms (faceta 30). Hoy NINGUNA lleva dimension de pais; el pais es ES implicito. Un consumidor pan-EU que mezcla censos no puede saber de que pais es cada fila salvo parseando el prefijo del cdp_code (CDP-{cc}-).

**(c) Costura ES->generico + fix exacto**
El cambio es aditivo y trivial por endpoint pero debe ser COHERENTE en las ~18 proyecciones o el contrato deriva entre paises. Fix exacto, decidido UNA vez:
- Data por fila: donde la fila es entity/vehicle/dealer, proyectar su country_code (entity.country_code existe desde 0052; vehicle lo deriva via entity_ulid) y `data['country_code'] = row['country_code']`. Para geo, anadir country_code a los nodos province/municipality.
- Envelope: anadir `country=<cc_efectivo>` al meta de todo endpoint country-scoped via ok(data, country=cc, ...). meta.country es la senal top-level canonica; el country_code por-fila desambigua listas mezcladas.
- Regla: country_code por-fila en objetos data que representen una entidad geo-portadora, Y meta.country para el scope del request. currency intacto (ya per-vehicle). Aplicar uniforme; congelar con el snapshot OpenAPI (faceta 30).

**(d) Riesgo adversarial concreto**
Si se anade incoherentemente — unos endpoints con country en data, otros en meta, otros sin el — el cliente pan-EU no puede confiar en el campo y debe inferir el pais por el prefijo del cdp_code, frustrando el proposito. Un cambio futuro que anade country a una proyeccion y a otra no rompe en silencio a los consumidores que esperaban la forma previa.

**(e) Criterio de sellado + verificacion multi-via**
1. Test de coherencia: un contrato asegura que toda respuesta country-scoped lleva meta.country, y todo objeto data entity/vehicle/dealer lleva country_code (enumerar las 18 proyecciones; fallar si alguna carece).
2. Golden cross-country: con ES+DE sembrados, /entities/{cdp} de un dealer DE devuelve country_code='DE'; uno ES devuelve 'ES' (sin bleed, atribucion correcta).
3. ES byte-identico salvo el campo aditivo: el diff del snapshot OpenAPI muestra SOLO campos country aditivos, cero removidos/retipados (faceta 30 + oasdiff).
4. Round-trip: el valor de meta.country == el prefijo del cdp_code de cada fila de data (consistencia interna).

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
[VERIFIED NEXT-LEVEL.md:833-839] **oasdiff/oasdiff** (Apache-2.0 [VERIFIED], EUR0) — https://github.com/oasdiff/oasdiff — gate de CI que diffea el OpenAPI base-vs-HEAD y FALLA ante cualquier breaking change, convirtiendo 'el contrato es country-invariante / solo-aditivo' de promesa a garantia mecanica: anadir country_code coherentemente registra 0 breaking changes, mientras quitar/retipar un campo en cualquier proyeccion rompe el build. Complementar [VERIFIED NEXT-LEVEL.md:857-863] con **openapi-ts/openapi-typescript** (MIT [VERIFIED], https://github.com/openapi-ts/openapi-typescript) para que el SDK tipado del consumidor pan-EU haga del drift un error de compilacion, y [VERIFIED NEXT-LEVEL.md:825-831] **schemathesis/schemathesis** (MIT [VERIFIED], https://github.com/schemathesis/schemathesis) para fuzz property-based de los 18 endpoints incl. un check de country-bleed.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** Ninguna de las ~18 proyecciones emite pais: dict(row) sin country en entities.py:80-87, geo.py:419-420, vehicles.py:99-106, platforms.py:77-85 [todos VERIFIED]; entity.country_code existe (0052) pero no se proyecta. El consumidor pan-EU solo puede inferir el pais por el prefijo del cdp_code.
- **Fix — propuesta [no implementada].** Decidir UNA vez: country_code por-fila en objetos entity/vehicle/dealer (data['country_code']=row['country_code']; geo en nodos province/municipality) + meta.country=cc_efectivo via ok(data, country=cc) [deps.py:52-53]. currency intacto (ya per-vehicle, entities.py:132). Aplicar coherente en las 18 proyecciones y congelar con snapshot OpenAPI.
- **Adversarial (DE/FR/IT/PT/no-UE).** Anadido incoherente (unos en data, otros en meta, otros sin el) -> el cliente pan-EU no confia en el campo y vuelve a inferir por el prefijo cdp_code; un cambio futuro que lo anade a una proyeccion y no a otra rompe en silencio el shape esperado.
- **Sellado + verificación multi-vía.** (1) contrato: toda respuesta country-scoped con meta.country y todo data entity/vehicle/dealer con country_code (18 proyecciones); (2) golden ES+DE: /entities/{cdp} DE -> 'DE', ES -> 'ES'; (3) diff OpenAPI = solo campos aditivos (oasdiff); (4) round-trip meta.country == prefijo cdp_code de cada fila.
- **Herramienta NEXT-LEVEL (€0).** [VERIFIED NEXT-LEVEL.md:833-863] oasdiff (Apache-2.0) https://github.com/oasdiff/oasdiff gate de breaking-change (aditivo=0 breaks); + openapi-typescript (MIT) https://github.com/openapi-ts/openapi-typescript (drift = error de compilacion); + schemathesis (MIT) https://github.com/schemathesis/schemathesis fuzz de los 18 endpoints + check de bleed.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f25"></a>

### Faceta 25 · /countries: índice del censo servible

**(a) Verificacion de code_hints [VERIFIED]**
- **AUSENTE**: no existe router /countries. `grep countries services/api/routers` = sin coincidencias; `main.py:146-150` incluye SOLO `ops, entities, geo, vehicles, platforms`. [VERIFIED]
- **Dependencia country_registry AUSENTE**: `grep country_registry migrations` = sin archivos (faceta 26 sin construir). [VERIFIED]
- **Envelope**: `deps.py:52-53` — `def ok(data, **meta): return JSONResponse({"ok": True, "data": data, "error": None, "meta": meta or None})`. [VERIFIED]
- **Restriccion competitiva**: `main.py:34-35` (docstring) — "/health is a liveness probe ... product counts moved to /stats (authed) -- coverage scale is a competitive signal (audit P2/P1)." [VERIFIED] — /countries NO debe filtrar la escala cruda sin auth.
- **Cache**: `cache.py:57-62` `CACHEABLE_PATH_PREFIXES = ("/geo/", "/entities/", "/platforms/")` — /countries no esta -> no se cachearia salvo anadir el prefijo. [VERIFIED]
- **Deps de datos** (precondicion): product_stats por-pais (faceta 3) y v_exhaustiveness_seal por-pais (faceta 12). Hoy product_stats es single-row (CHECK id=1) y v_exhaustiveness_seal sirve el latest GLOBAL — ambos deben ser por-pais antes de que /countries liste cota+freshness fiables [ASSUMED por facetas 3/12; country_registry AUSENTE [VERIFIED]].

**(b) Mecanismo al atomo (a construir)**
`GET /countries` lee `country_registry` (los paises declarados) LEFT JOIN a:
- **product_stats por-pais** (faceta 3) -> conteo + `computed_at` (freshness);
- **v_exhaustiveness_seal por-pais** (faceta 12) -> la cota inferior SELLADA (`coverage_lower` del grand-national de cada pais + `sealed`).

Devuelve por pais `{country_code, display_name, admin1_label, coverage_lower, sealed, computed_at}` en el envelope `ok([...])`. Sin auth: SOLO cota inferior + freshness + etiqueta; NUNCA el entero absoluto de escala (vive en /stats authed, main.py:34-35).

**(c) Costura ES->generico**
Hoy todo es implicito-ES; no hay indice de paises. La pieza NO existe y depende de 3 facetas: 26 (la fila declarativa `country_registry`), 12 (cota por pais via exhaustiveness por-pais) y 3 (conteo+freshness via product_stats por-pais). Nace generico o no nace: un /countries construido country-blind no tendria nada que indexar.

**(d) Fix exacto**
1. **Construir** `services/api/routers/countries.py` con `GET /countries`; registrarlo en `main.py` (`app.include_router(countries.router)`) tras los existentes (main.py:146-150).
2. **Query**: `SELECT cr.country_code, cr.display_name, cr.admin1_label, x.coverage_lower, x.sealed, ps.computed_at FROM country_registry cr LEFT JOIN v_exhaustiveness_seal x ON x.country_code=cr.country_code AND x.segment IS NULL AND x.province_code IS NULL LEFT JOIN product_stats ps ON ps.country_code=cr.country_code` (requiere facetas 3, 12, 26). Envelope `ok(rows, ...)`.
3. **Auth**: decidir si incluso la cota es senal -> `Depends(require_api_key)`; o publico SOLO con cota inferior + freshness. NUNCA conteo crudo sin auth (main.py:34-35).
4. **Cache**: anadir `/countries` a `CACHEABLE_PATH_PREFIXES` (cache.py:57) o cachear explicito; cambia solo entre builds.
5. **Freshness honesta**: `meta.freshness` desde `computed_at` por pais.

**(d') Riesgo adversarial concreto**
- **Fuga competitiva**: si /countries expone el conteo CRUDO de dealers por pais sin auth, filtra la escala competitiva — justo lo que el audit movio de /health a /stats (main.py:34-35).
- **Mentira de confianza**: si sirve un entero absoluto en vez del `coverage_lower` con CI, miente sobre la confianza por pais.
- **Pais a medias**: un pais en `country_registry` pero sin exhaustiveness por-pais (faceta 12 incompleta) da `coverage_lower NULL` -> debe marcarse 'no certificado aun', no 0 ni omitirse.
- **PT/DE recien onboarded**: deben aparecer con `sealed=false` y cota baja HONESTA, nunca con un 100% fabricado.

**(e) Sellado + verificacion multi-via**
- **Contrato sin fuga**: un test asserta que NINGUN campo de escala cruda sin auth aparece (espejo del audit /health->/stats); solo cota inferior + freshness + etiqueta.
- **Honestidad**: un pais sin exhaustiveness por-pais sale `sealed=false` / `coverage_lower=null` marcado 'no certificado', nunca 100%.
- **Golden**: con solo ES en `country_registry`, /countries lista EXACTAMENTE 1 pais con la cota viva de `v_exhaustiveness_seal` (cross-check vs /geo/exhaustiveness `national`).
- **Freshness**: `meta.freshness` por pais = `now()-computed_at`, cruzado contra la fila real.

**(f) Herramienta NEXT-LEVEL**
**matview-incremental-ivm — pg_ivm** (PostgreSQL License [VERIFIED]) https://github.com/sraoss/pg_ivm [NEXT-LEVEL.md:764]. Convierte product_stats (y los agregados de cobertura por pais que /countries lista) en IMMV mantenidas por triggers AFTER en O(delta), de modo que la cota inferior y el `computed_at` que sirve el indice JAMAS estan viejos ni dependen de un REFRESH manual — el indice de paises nunca miente sobre freshness. Complemento para el contrato de freshness EXPLICITO: **matview-scheduled-refresh + freshness-SLO — pg_cron** (PostgreSQL License [VERIFIED], https://github.com/citusdata/pg_cron, NEXT-LEVEL.md:772) expone `computed_at age` en `meta.freshness` + guard de staleness. Para consumo pan-EU type-safe del indice: **typed-census-sdk — openapi-typescript** (MIT [VERIFIED], https://github.com/openapi-ts/openapi-typescript, NEXT-LEVEL.md:860).

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** No existe /countries (main.py:146-150 incluye solo ops/entities/geo/vehicles/platforms; grep countries en routers = 0) ni un indice de censos servibles. La unica fila declarativa que lo alimentaria, country_registry, tampoco existe (grep country_registry migrations = 0; faceta 26). El endpoint depende ademas de product_stats por-pais (faceta 3, hoy single-row CHECK id=1) y v_exhaustiveness_seal por-pais (faceta 12, hoy latest GLOBAL) para la cota+freshness. Hoy todo es implicito-ES; un consumidor no sabe que censos existen ni con que confianza.
- **Fix — propuesta [no implementada].** Construir services/api/routers/countries.py con GET /countries y registrarlo en main.py tras los existentes. Query: country_registry LEFT JOIN v_exhaustiveness_seal (segment IS NULL AND province_code IS NULL -> coverage_lower+sealed) LEFT JOIN product_stats (computed_at) por country_code (requiere facetas 3,12,26). Envelope ok() (deps.py:52-53). Servir SOLO cota inferior + freshness + etiqueta (nunca conteo crudo sin auth, main.py:34-35); decidir Depends(require_api_key) si la cota es senal. Anadir /countries a CACHEABLE_PATH_PREFIXES (cache.py:57). meta.freshness desde computed_at por pais.
- **Adversarial (DE/FR/IT/PT/no-UE).** Si /countries expone el conteo CRUDO de dealers por pais sin auth, filtra la escala competitiva (justo lo que el audit movio de /health a /stats, main.py:34-35). Si sirve un entero absoluto en vez de coverage_lower con CI, miente sobre la confianza por pais. Un pais en country_registry sin exhaustiveness por-pais (faceta 12 incompleta) da coverage_lower NULL -> debe marcarse 'no certificado', no 0 ni omitirse. PT/DE recien onboarded deben salir sealed=false con cota baja honesta, nunca un 100% fabricado.
- **Sellado + verificación multi-vía.** Multi-via: (1) Contrato sin fuga: test asserta cero escala cruda sin auth (espejo audit /health->/stats); solo cota inferior+freshness+etiqueta. (2) Honestidad: pais sin exhaustiveness por-pais sale sealed=false/coverage_lower=null 'no certificado', nunca 100%. (3) Golden: con solo ES en country_registry, /countries lista exactamente 1 pais con la cota viva de v_exhaustiveness_seal (cross-check vs /geo/exhaustiveness national). (4) Freshness: meta.freshness=now()-computed_at cruzado contra la fila real.
- **Herramienta NEXT-LEVEL (€0).** matview-incremental-ivm — pg_ivm (PostgreSQL License [VERIFIED]) https://github.com/sraoss/pg_ivm [NEXT-LEVEL.md:764]: product_stats y los agregados por pais como IMMV mantenidas por triggers AFTER en O(delta) -> la cota inferior y el computed_at que sirve el indice nunca estan viejos ni dependen de REFRESH manual. Complemento freshness-SLO: pg_cron (PostgreSQL License [VERIFIED], NEXT-LEVEL.md:772) expone computed_at age en meta.freshness + guard de staleness. Consumo type-safe: openapi-typescript (MIT [VERIFIED], NEXT-LEVEL.md:860).

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f26"></a>

### Faceta 26 · country_registry: la fila declarativa del pack

**(a) Code_hints verificados a la fuente real**
- **AUSENTE**: ninguna migracion crea `country_registry` [VERIFIED grep country_registry: aparece SOLO en docs (`docs/generic-engine-bible/INSTITUTIONAL-BACKLOG.md`, `COUNTRY-PACK-CONTRACT.md`, `stages/08-serve.md`); cero hits en `migrations/` y en `services/`]. No hay tabla ni seed.
- **Forma del contrato declarada**: 'Una fila de `country_registry` `{country_code, admin1_label, display_name}` (ES=Comunidad Autonoma, DE=Bundesland, FR=Region)' [VERIFIED docs/generic-engine-bible/COUNTRY-PACK-CONTRACT.md:165]. La migracion de onboarding la siembra: '`migrations/00NN_onboard_<cc>.sql` # filas semilla source_health/discovery_list/country_registry + backbone load' [VERIFIED COUNTRY-PACK-CONTRACT.md:218].
- **Consumidores previstos**: el label admin1 del arbol [VERIFIED geo.py:419-420] (hoy emite `prov['ccaa_code'], prov['ccaa_name']` leidos de geo_province [VERIFIED geo.py:370]); y `/countries` (faceta 25, ausente). Envelope `ok()` [VERIFIED deps.py:52-53].

**(b) Mecanismo al atomo**
`country_registry` es la UNICA pieza pais-especifica puramente DECLARATIVA de la capa de servido — la que sostiene la afirmacion del diseno 'el binario de la API es identico entre paises; solo difiere esta fila + los datos'. Lleva exactamente tres campos: `country_code` (la clave de join), `admin1_label` (el nombre humano del primer tier administrativo — Comunidad Autonoma / Bundesland / Region), y `display_name` (el nombre del pais para `/countries`). Alimenta: (1) el `admin_level_1 {code,label}` de faceta 6 — el slot `ccaa_name` del arbol pasa a ser un lookup en `country_registry.admin1_label` en vez del literal `geo_province.ccaa_name`; (2) el `/countries` de faceta 25 — el indice lista cada pais servido con su `display_name` + cobertura sellada. Hoy NADA de esto existe: geo.py:419-420 lee `ccaa_*` directo de geo_province (soldado-ES) y no hay `/countries`.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** **ES -> generico.** El diseno afirma que el pack de servido se reduce a 'una fila `{country_code, admin1_label, display_name}`' [VERIFIED COUNTRY-PACK-CONTRACT.md:165] pero esa tabla es VAPOR — referenciada en tres docs de diseno y sembrada por una migracion `00NN_onboard` hipotetica [VERIFIED COUNTRY-PACK-CONTRACT.md:218], pero NINGUNA migracion la crea y NINGUN codigo la lee. Sin ella, dos superficies genericas no tienen fuente: (1) el label admin1 (faceta 6) cae al `geo_province.ccaa_name` de ES (el concepto espanol 'Comunidad Autonoma' leakeado a la FORMA de salida generica), y (2) `/countries` (faceta 25) no tiene nombre ni etiqueta por-pais que listar. La costura: el unico input declarativo pais-especifico de la capa generica esta INDEFINIDO, asi que toda 'etiqueta parametrizada por pais' silenciosamente cae a la taxonomia ES.
- **Fix — propuesta [no implementada].** **Fix exacto:**
1. `CREATE TABLE country_registry (country_code CHAR(2) PRIMARY KEY, admin1_label text NOT NULL, display_name text NOT NULL [+ opcional admin1_label_plural, currency, locale])` — migracion additiva; seed `ES = {'ES','Comunidad Autonoma','Espana'}` para que la salida ES no cambie.
2. **Cableado faceta 6:** geo.py:370 (query del arbol) + 419-420 (respuesta) leen `admin1_label` de country_registry por country_code (JOIN o lookup cacheado) en vez del literal `ccaa_name`; el valor para filas ES sigue siendo 'Comunidad Autonoma' (byte-identico), la CLAVE del JSON pasa al generico `admin_level_1 {code,label}`.
3. **Cableado faceta 25:** `/countries` hace SELECT de country_registry + join product_stats-por-pais (faceta 3) + v_exhaustiveness_seal-por-pais (faceta 12) para la cota inferior sellada + freshness.
4. **Contrato de onboarding:** cada country-pack envia exactamente UNA fila country_registry; un guard CI (Pydantic/Frictionless) asevera que todo pais activo tiene su fila (biyeccion registry<->pais activo).
5. El contrato 'binario API identico' pasa a ser literal: el unico delta de servido por-pais es esta fila + los datos.
- **Adversarial (DE/FR/IT/PT/no-UE).** **Onboarding de un pais sin su fila country_registry:** el arbol emite `admin1_label` NULL (o cae al ES 'Comunidad Autonoma' si el fallback es laxo) — DE muestra 'Comunidad Autonoma' en vez de 'Bundesland', FR en vez de 'Region', IT en vez de 'Regione' — taxonomia ES leakeada a otro pais. `/countries` no puede listar el pais con su `display_name` correcto (NULL o ausente). **Concreto:** el operador onboarda PT, carga backbone+entities (faceta 1 ok), pero olvida la fila registry -> `/PT/geo/{prov}/tree` responde con `admin_level_1.label='Comunidad Autonoma'` (absurdo para distritos PT) y `/countries` omite PT o lo lista sin etiqueta. **Silencioso:** HTTP 200, dato presente, etiqueta equivocada — el peor fallo (parece correcto). **Ruido/no-UE:** MX (Estados), JP (Prefectures) — sin su fila, ambos heredan 'Comunidad Autonoma'.
- **Sellado + verificación multi-vía.** **Criterio de sellado + verificacion multi-via:**
- **Existencia:** guard CI que itera `active_countries()` y falla ROJO si algun pais activo carece de su fila country_registry (biyeccion 0 ORPHAN / 0 MISSING).
- **ES byte-identico:** con la fila ES sembrada, `/geo/{prov}/tree` emite 'Comunidad Autonoma' exactamente como hoy (golden inalterado).
- **Via 1 (Frictionless):** Table Schema valida cada fila del pack (country_code casa ISO 3166-1 alpha-2, admin1_label/display_name no vacios) ANTES del INSERT.
- **Via 2 (HTTP):** `/DE/geo/tree`.admin_level_1.label == `country_registry.admin1_label WHERE country_code='DE'` == 'Bundesland'.
- **Via 3 (/countries):** lista exactamente las filas de country_registry, ninguna de mas/menos.
- **Via 4 (pycountry):** `country_code` es un codigo ISO 3166-1 real y `display_name` razonable.
- **Precondicion:** faceta 1 (servable_entity.country_code); habilita faceta 6 (admin_level_1 label) y faceta 25 (/countries).
- **Herramienta NEXT-LEVEL (€0).** **Frictionless Framework (frictionless-py, Table Schema)** — MIT, €0 — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Declara `country_registry` (y el resto del pack) como un Table Schema con tipos + regex de forma de codigo + ancho per-pais, validado en el bootstrap del pais ANTES de cargar una fila — aplica la doctrina COUNTRY-PROOF 'no documentar la regla, que la maquina la imponga y la pruebe sola' a la INGESTA del pack [VERIFIED:334-340]. €0 pip, schema YAML/JSON versionado en `data/<cc>/`, corre en CI y bootstrap [VERIFIED:339]. **Companeros:** Pydantic `CountryPack(BaseModel)` — MIT, €0 — https://github.com/pydantic/pydantic [VERIFIED:587] para el guard de biyeccion registry<->pais activo en CI [VERIFIED:585,589]; pycountry — LGPL-2.1, €0 — https://github.com/pycountry/pycountry [VERIFIED:530] para certificar que `country_code` es ISO 3166-1 alpha-2 real y que el conteo/ancho admin1 casan el estandar [VERIFIED:527-529].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f27"></a>

### Faceta 27 · Paginación keyset (cursor) + ETag/304

**(a) Verificacion de code_hints [VERIFIED]**
- `services/api/deps.py:60-68` [VERIFIED] — `page_slice(rows, size)` hace **over-fetch** y retorna `rows[:size], len(rows) > size`: deriva `has_more` honesto, pero **sin cursor**; es OFFSET-based.
- Callers con OFFSET [VERIFIED]:
  - `services/api/routers/entities.py:121` — `offset = (page - 1) * size` (+ `LIMIT $2 OFFSET $3` en el inventory `:141`).
  - `services/api/routers/geo.py:253` (entities_by_province) y `geo.py:316` (municipality) — `offset = (page - 1) * size`.
  - `services/api/routers/platforms.py:43` — `offset = (page - 1) * size` (+ `LIMIT $2 OFFSET $3` `:65`).
  - `services/api/routers/ops.py:124` (/alerts) — `offset = (page - 1) * size`.
- **Sin ETag en ningun endpoint** [VERIFIED] — `services/api/cache.py:109-165` construye `JSONResponse` con el envelope `{ok,data,error,meta}` y `meta.cache=hit|miss`; **no genera header `ETag` ni honra `If-None-Match`**; no hay ruta 304.
- **Escala** [VERIFIED docstrings] — `servable_vehicle` 500k+ (`main.py:19`), `platform_listing` 576k+ Wallapop (`platforms.py:36`).

**(b) El mecanismo al atomo**
Cada endpoint paginado computa `offset=(page-1)*size` y emite `LIMIT size+1 OFFSET offset`; `page_slice` recorta la fila sobre-leida para el `has_more`. PostgreSQL **debe recorrer y descartar `offset` filas** antes de devolver la pagina: **O(n) por request**, asi que paginas profundas sobre `servable_vehicle` (500k+) / `platform_listing` (576k+) degradan linealmente. Peor: OFFSET es **inestable bajo insercion concurrente** del harvester — una fila insertada "por encima" del offset desplaza toda pagina siguiente, **duplicando o saltando** items entre fronteras de pagina. Ningun endpoint emite `ETag`, asi que un cliente que repite una pagina inalterada **re-descarga el cuerpo completo** cada vez; no hay 304.

**(c) Costura ES->generico**
El coste esta **amplificado por pais**: con N paises las tablas crecen a millones y un OFFSET profundo escanea la tabla **GLOBAL** aun para una pagina de un solo pais. El fix son **dos atomos ortogonales**: (1) la paginacion keyset/cursor es un cambio **hecho a mano** (la clave de orden UNICA y monotona correcta por endpoint); (2) ETag/conditional-GET es justo lo que la cache de borde (Souin, RFC-7234) provee gratis.

**(d) Fix exacto**
1. **Sustituir OFFSET por keyset** sobre una clave de orden UNICA y monotona por endpoint, emitiendo el cursor en `meta`:
   - `/entities/{cdp}/inventory` y `/platforms/{cdp}/inventory`: ya ordenan `... first_seen DESC, vehicle_ulid` [`entities.py:138`, `platforms.py:64`] => keyset `WHERE (first_seen, vehicle_ulid) < ($cur_fs, $cur_ulid)`.
   - `/geo/{prov}/entities`: hoy `ORDER BY q.trade_name NULLS LAST, q.cdp_code` [`geo.py:271-273`] => keyset con el desempate UNICO `cdp_code` (trade_name es nullable/duplicado): `(trade_name, cdp_code) > (...)` con manejo de NULLS.
   - `/alerts`: `ORDER BY severity-rank, created_at DESC` [`ops.py:131-137`] => keyset sobre `(severity_rank, created_at, id)` con `id` como desempate unico.
2. **Reescribir `page_slice`** [`deps.py:60-68`] a un helper encode/decode de cursor (p.ej. base64 de la tupla-clave de la ultima fila); conservar el over-fetch `size+1` para `has_more`.
3. **Emitir `ETag`** (hash del cuerpo / version de contenido) y honrar `If-None-Match` => 304 con cuerpo vacio. Lo mas limpio: que el borde **Souin** (faceta 17/20) genere/valide el ETag por RFC-7234; la app provee una representacion estable.
4. **Mantener OFFSET solo** donde la tabla es minima (p.ej. `/sources`) — YAGNI sobre sets pequenos.

**(e) Criterio de sellado + verificacion multi-via**
- **Estabilidad bajo insercion concurrente (el test clave):** sembrar una tabla, empezar a paginar con keyset, INSERT de filas "por encima" del cursor a mitad de iteracion => el recorrido keyset entrega cada item **exactamente una vez** (sin dup, sin salto); la version OFFSET **falla** este test de forma demostrable.
- **Prueba O(log n):** `EXPLAIN ANALYZE` de una pagina profunda muestra un **index range scan** sobre la clave de orden, no un `Rows Removed by ...`/seq-scan que crece con el offset.
- **Round-trip de ETag:** el primer GET retorna 200 + `ETag`; el segundo GET con `If-None-Match` retorna **304** cuerpo vacio; tras una mutacion de harvest el `ETag` cambia y retorna 200.
- **Golden ES byte-identico** de la pagina 1 (cursor por defecto): los payloads de primera pagina existentes quedan inalterados.

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
**darkweak/souin — edge HTTP cache (RFC-7234, SWR)** [VERIFIED `NEXT-LEVEL.md:780`; MIT; https://github.com/darkweak/souin; EUR0=True]. Souin resuelve la **mitad ETag/conditional-request/304 y el request-coalescing** en el borde Caddy — compartida entre workers, persistente a reinicios, sirviendo stale-while-revalidate para que un pico viral sobre el censo **nunca de un 500** [VERIFIED:778-783]. Su item de verificacion (4) **pliega explicitamente el pais en la cache key** para que `/geo/ES` jamas sirva el cuerpo de `/geo/DE` [VERIFIED:783]. El **cursor keyset en si es un cambio a mano** (no necesita libreria); Souin certifica el contrato de caching/ETag. **Pareja con el borde TLS Caddy de la faceta 20** — un borde, tres victorias (TLS + cache + ETag). El SLO de latencia se sella con **vegeta slo-perf-gate** (p99<50ms en CI, falla el build si se degrada) [VERIFIED:844, MIT].

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** deps.py:60-68 page_slice es OFFSET-based sin cursor; callers offset=(page-1)*size en entities.py:121, geo.py:253 y :316, platforms.py:43, ops.py:124. OFFSET es O(n) sobre servable_vehicle 500k+ (main.py:19) y platform_listing 576k+ (platforms.py:36) e inestable bajo insercion concurrente. Sin ETag en ninguna ruta (cache.py:109-165 no emite ETag ni honra If-None-Match). Amplificado por pais: el OFFSET escanea la tabla global aun para una pagina de un pais.
- **Fix — propuesta [no implementada].** Keyset por clave UNICA monotona por endpoint emitiendo cursor en meta: (first_seen,vehicle_ulid) en inventories [entities.py:138/platforms.py:64], (trade_name,cdp_code) en /geo/{prov}/entities [geo.py:271-273], (severity_rank,created_at,id) en /alerts [ops.py:131-137]; reescribir page_slice a encode/decode de cursor (over-fetch size+1 se conserva); emitir ETag + 304 If-None-Match (delegado al borde Souin); OFFSET solo en sets minimos.
- **Adversarial (DE/FR/IT/PT/no-UE).** A escala multi-pais con millones de filas, /platforms/{cdp}/inventory?page=N alto hace scan O(n) por request; un harvest concurrente inserta filas que desplazan el OFFSET, duplicando o saltando items entre paginas. Sin ETag, un cliente pan-EU que hace polling re-descarga paginas identicas de varios MB.
- **Sellado + verificación multi-vía.** Estabilidad concurrente: paginar con keyset mientras se INSERTan filas por encima del cursor => cada item exactamente una vez (OFFSET falla); EXPLAIN ANALYZE muestra index range scan, no seq-scan que crece con offset; round-trip ETag (200+ETag -> If-None-Match 304 -> mutacion cambia ETag -> 200); golden ES byte-identico de pagina 1.
- **Herramienta NEXT-LEVEL (€0).** darkweak/souin edge cache RFC-7234/SWR [VERIFIED NEXT-LEVEL.md:780; MIT; https://github.com/darkweak/souin; EUR0] resuelve ETag/304/coalescing en el borde Caddy, compartido/persistente, con cache key que pliega el pais (cierra el bleed) [VERIFIED:778-783]; el cursor keyset es cambio a mano. Pareja con el Caddy TLS de faceta 20. SLO sellable con vegeta (p99<50ms en CI) [VERIFIED:844; MIT].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f28"></a>

### Faceta 28 · /alerts y /sources: atribución por país

**(a) Verificacion de code_hints [VERIFIED]**
- **/alerts**: `SELECT id, origin, severity, message, payload, created_at FROM alert WHERE resolved_at IS NULL ORDER BY CASE severity ... END, created_at DESC LIMIT $1 OFFSET $2` [VERIFIED services/api/routers/ops.py:105-157, query :126-142]. **Sin predicado de pais**; paginado; sirve `origin` (label de fuente) pero ninguna columna country.
- **/sources**: `SELECT source_key, status, consecutive_fails, last_ok, last_fail, is_tier1 FROM source_health ORDER BY CASE status ... END, consecutive_fails DESC, source_key` [VERIFIED ops.py:160-199, query :174-190]. **Sin predicado de pais**; sin paginar; keyed por `source_key` (id de scraper).
- **Excluidos de cache**: `CACHE_EXCLUDED_PATHS = ("/health","/alerts","/sources")` [VERIFIED services/api/cache.py:66-70] → ambos bypassean la cache in-memory (near-real-time).

**(b) Mecanismo al atomo**
Ambos endpoints son reads planos sobre tablas de monitoreo GLOBALES. `/alerts` aflora alertas no resueltas ordenadas por severidad (critical→warning→info via CASE) y luego recencia; `/sources` aflora salud de scrapers ordenada por enfermedad (down→degraded→unknown via CASE, luego consecutive_fails DESC). Ninguna tabla esta cortada por pais: `alert.origin` es un label de fuente de forma libre, `source_health.source_key` es un identificador de scraper. En despliegue mono-pais es correcto. La exclusion de cache es deliberada (alertas/salud cambian de continuo).

**(c) Costura ES->generico + fix exacto**
En multi-pais, los scrapers/fuentes son por-pais (una fuente registral DE, un scraper marketplace IT) y las alertas tienen un pais de origen (un Tier-1 :silence en FR, un lease rancio en PT). Un operador por-pais debe ver SOLO sus alertas/fuentes, o el feed global ahoga la senal de un pais bajo la de otro. La faceta plantea la decision: ¿ops es deliberadamente pan-EU, o por-pais? En cualquier caso debe DECIDIRSE y la dimension threadearse.

**Fix:**
1. Atribucion de pais en origen: `alert` y `source_health` ganan columna `country_code` (nullable para alertas genuinamente globales), poblada por el scraper/build que las dispara (la cosecha ya conoce su pais).
2. Threadear la dimension en ambos handlers consistente con la decision de request-country (faceta 16: path `/{cc}/alerts` o `?country=cc`): anadir `AND (country_code = $cc OR country_code IS NULL)` (nacional + global) a `/alerts` y `/sources`; exponer country por fila y en `meta.country`.
3. Mantener la exclusion de cache (sigue near-real-time); si se anade filtro country y en el futuro se cachea, la clave DEBE incluir el pais (x-ref faceta 17).
4. ES-default (`CARDEEP_ENV` sin setear / sin country) lee el feed global byte-identico — el predicado es no-op cuando no se pasa pais.

**(d) Riesgo adversarial concreto**
- **DE+ES vivos**: `/alerts` devuelve alertas ES+DE interleaved por severidad; un operador DE triando una critica DE la ve sepultada bajo warnings ES, y una critica del OTRO pais (irrelevante) ocupa la cima → se destruye la senal de urgencia por-pais.
- **/sources**: reporta scrapers DE como "down" a un operador ES (ruido irrelevante) y viceversa; el orden "fuente mas enferma" mezcla paises, asi que la cima puede ser la caida de otro pais.
- **Persona pan-EU**: un operador global, al contrario, puede necesitar la vista fusionada — un country-scope DURO sin modo global rompe ESA persona. El fix nullable-country + `(cc OR NULL)` soporta ambas.

**(e) Sellado + verificacion multi-via**
- **Criterio**: para una request country-scoped, `/alerts` y `/sources` devuelven solo filas de ese pais mas las genuinamente globales (NULL); ES-default devuelve el feed global byte-identico a hoy.
- **Via 1 DB no-bleed**: sembrar una alerta + fila source_health de 2o pais en txn revertida; asertar que `/alerts?country=ES` excluye la alerta DE y `/sources?country=ES` excluye la fuente DE; asertar que `?country=DE` las devuelve.
- **Via 2 HTTP-vs-SQL**: el row-set del endpoint == query asyncpg independiente con el mismo predicado `(country_code=$cc OR country_code IS NULL)`.
- **Via 3 golden**: sin arg country la respuesta == la respuesta global actual (byte-identica) sobre un fixture fijo.
- **Via 4 entrega out-of-band (Apprise)**: el conteo de notificaciones por-pais despachadas == filas de alerta Tier-1 abiertas de ese pais (sin perdida/dup), espejo del dedup de fire_alert.

**(f) Herramienta NEXT-LEVEL**
**Apprise** (BSD-2-Clause) — https://github.com/caronc/apprise [VERIFIED NEXT-LEVEL.md:707]. Hoy las alertas viven solo in-DB y un humano debe consultar el endpoint — inutil cuando el stack esta caido. Apprise reparte una alerta a 100+ canales (email/ntfy/Slack/Telegram/webhook) con claves de routing por-pais: un sink en `fire_alert` mapea (severidad, country_code, tier) → URLs de canal, asi un Tier-1 :silence DE alcanza al operador DE fuera-de-banda y los gates PENDING-OWNER pingan al owner [VERIFIED NEXT-LEVEL.md:704-710]. Hace la atribucion de pais ACCIONABLE, no solo visible. Emparejar con **Grafana** (AGPL-3.0; uso interno no-distribuido OK) — https://github.com/grafana/grafana [VERIFIED NEXT-LEVEL.md:715] leyendo una vista SQL `v_orchestrator_health` (source_health+source_breaker+scheduler_lease+alert, cortada por country_code) con variable `$country`, convirtiendo `/sources` de un JSON plano en un board de operador por-pais; su test de bleed (sembrar pais #2, confirmar que `$country=DE` no mezcla filas ES) es el mismo guard de aislamiento [VERIFIED NEXT-LEVEL.md:712-718]. Alternativa licencia-limpia: **Prometheus** (Apache-2.0)+postgres_exporter si AGPL no se quiere [VERIFIED NEXT-LEVEL.md:716].

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** /alerts (ops.py:105-157) y /sources (ops.py:160-199) son reads planos sobre las tablas globales alert y source_health sin predicado de pais (y excluidos de cache, cache.py:66-70); en multi-pais los scrapers/fuentes y las alertas son por-pais, asi que un operador de un pais ve mezcladas las alertas y la salud de fuentes de todos.
- **Fix — propuesta [no implementada].** Anadir country_code (nullable=global) a alert y source_health poblado en origen por la cosecha; threadear la dimension (path /{cc}/... o ?country=, faceta 16) con AND (country_code=$cc OR country_code IS NULL) en ambos handlers + country en fila y meta; mantener exclusion de cache (y si se cachea, clave con pais, faceta 17); ES-default no-op byte-identico.
- **Adversarial (DE/FR/IT/PT/no-UE).** DE+ES: /alerts interleava por severidad y una critica DE queda sepultada bajo warnings ES mientras una critica del otro pais (irrelevante) ocupa la cima; /sources reporta scrapers DE 'down' al operador ES como ruido y la cima de 'mas enferma' es la caida de otro pais; un country-scope duro sin modo global romperia la persona pan-EU (de ahi nullable + (cc OR NULL)).
- **Sellado + verificación multi-vía.** Criterio: request country-scoped devuelve solo ese pais + globales (NULL); ES-default global byte-identico. Via1 DB no-bleed (sembrar alerta+source de 2o pais en txn revertida; ?country=ES excluye DE, ?country=DE las incluye). Via2 HTTP-vs-SQL mismo predicado. Via3 golden sin-country == global actual. Via4 Apprise: notificaciones por-pais == alertas Tier-1 abiertas del pais (sin perdida/dup).
- **Herramienta NEXT-LEVEL (€0).** Apprise (BSD-2-Clause) https://github.com/caronc/apprise [VERIFIED NEXT-LEVEL.md:707] — fan-out de alerta country-routed out-of-band (sink en fire_alert mapea severidad,country_code,tier -> canales); + Grafana (AGPL-3.0, interno OK) https://github.com/grafana/grafana [VERIFIED NEXT-LEVEL.md:715] board v_orchestrator_health con $country; alt licencia-limpia Prometheus (Apache-2.0)+postgres_exporter [VERIFIED NEXT-LEVEL.md:716].

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f29"></a>

### Faceta 29 · Golden multi-país + suite no-bleed (HTTP-vs-SQL)

**(a) Code_hints verificados**
- **[VERIFIED tests/test_country_coexistence.py:309-369]** `TestDbProvinceCoexistence` + **[:372-458]** `TestDbEsCountsUnchanged` — ejercitan **SOLO el SCHEMA backbone**: coexistencia PK/FK de `geo_province`/`geo_municipality`/`entity` en txn revertida (`_seed_de_rows` :259-285 inserta geo_province/municipality/entity; asevera PK compuesto/FK; rollback). **CERO endpoints HTTP** se golpean.
- **[VERIFIED tests/test_country_coexistence.py:40-46]** importa solo `services.api.codes` (funciones de codigo) + asyncpg — **sin FastAPI app / sin TestClient**.
- **Patron HTTP-vs-SQL: [VERIFIED tests/test_api_gaps.py:21-23]** `from fastapi.testclient import TestClient` + `from services.api.main import app`, y helpers asyncpg de cross-check `_fetchval` (:50-61), `_canonical_map` (:64-79), `_cluster_counts` (:82-90) — el patron canonico: golpear el endpoint via TestClient y cruzar el conteo contra una query SQL cruda independiente.
- **Golden ES: [VERIFIED tests/test_country_golden.py]** es el golden de byte-identidad de `codes.py` (cdp_code/canonical_key/mint_code), **NO** un golden HTTP — pinea literales cdp_code (**[:54-69]** p.ej. `domain:ford.es` -> `CDP-ES-28-ZB6C77HC`) a nivel de CODIGO.
- **`cache_clear()` disponible [VERIFIED services/api/cache.py:168-170]** para estado de test determinista.
- **Por ausencia [VERIFIED]:** ningun test golpea `/geo/seal`, `/geo/{prov}/entities`, `/tree`, `/stats`, `/geo/exhaustiveness` ni `/search` contra una BD sembrada con 2o pais aseverando retorno mono-pais.

**(b) Mecanismo / hueco al atomo**
El diseno cita `test_country_coexistence.py` como prueba de que la capa servida es generica, pero ese archivo **solo prueba el BACKBONE** (PK compuesto/FK coexisten) — **nunca toca la superficie API servida**. Asi un pais puede declararse **SELLADO** mientras la API **sangra filas ES en silencio** por cualquier handler geo cuyo predicado pais se olvido (facetas 4-12) o cuya cache key carece de pais (faceta 17). La suite faltante es la verificacion que convierte "el servido es generico" de **afirmacion** a **invariante mecanico**.

**(c) Costura ES->generico**
Construir la suite que, con el patron canonico **HTTP-vs-SQL** ([VERIFIED test_api_gaps.py:50-61]) + txn reversible que siembra un 2o pais:
- **(a) no-bleed por endpoint:** `/geo/{prov}/entities`, `/municipalities/{m}/entities`, `/tree`, `/stats`, `/geo/seal`, `/geo/exhaustiveness`, `/search` retornan SOLO filas del pais pedido;
- **(b) disjuncion cdp_code:** el set de `/geo/DE/...` y `/geo/ES/...` comparten **cero** cdp_codes;
- **(c) aislamiento de cache:** DE-28 **nunca** recibe el cuerpo cacheado de ES-28;
- **(d) golden ES byte-identico:** las respuestas ES inalteradas por la coexistencia DE.

**(d) Fix exacto**
Nuevo modulo (p.ej. `tests/test_api_country_nobleed.py`) con `TestClient(app)` + asyncpg, sembrando DE en una **txn que ROLLBACK** (patron [VERIFIED test_country_coexistence.py:259-285,416-458]), con `cache_clear()` (cache.py:168-170) antes de cada asercion para derrotar el TTLCache in-memory. Por endpoint: aseverar que el `country_code` de la respuesta HTTP == CC pedido **Y** == query SQL cruda con el mismo predicado; aseverar `/ES` disjunto de `/DE` en cdp_code; aseverar que un `/DE` tras un `/ES` (misma forma de path) **no** recibe el cuerpo cacheado de ES. Gate en CI; verde en schema mono-pais (skip si DB inalcanzable / PK 2o-pais no aplicado, mismo guard [VERIFIED test_country_coexistence.py:28-30,236-237]).

**(e) Riesgo adversarial**
**DE/FR/IT/PT:** sin esta suite, cualquier regresion de las facetas 4-12 (un `AND country_code=$cc` olvidado, un cache key sin pais) pasa CI **verde** y solo se detecta cuando un cliente real ve datos de otro pais en produccion. Provincia '28' es la trampa canonica: ES Madrid vs DE Brandenburg comparten codigo '28' **[VERIFIED test_country_coexistence.py:88-93]**, asi que `/geo/28/entities` es el vector de bleed exacto. **Cache (no obvio):** aun con SQL correcto, un pais threadeado por header/tenant (no path/query) hace que ES-28 y DE-28 compartan cache key (cache.py:79-94 pliega solo path+query) -> DE servido el cuerpo ES hasta el TTL; solo una asercion explicita de aislamiento de cache lo caza. **Ruido:** un province_code que existe en un pais y no en otro debe 404/vacio para el ausente, no fallback al otro.

**(f) Criterio de sellado + verificacion multi-via**
1. **La suite ES el sello:** no-bleed por endpoint + disjuncion + aislamiento-cache + golden-ES, todo verde, sobre fixture 2-paises en txn revertida.
2. **Dos oraculos independientes por endpoint:** respuesta HTTP vs SQL asyncpg cruda (patron test_api_gaps.py:50-61).
3. **Break-the-guard:** quitar deliberadamente un predicado pais de un handler -> el test no-bleed se pone **rojo** (prueba que el guard muerde).
4. **Reversibilidad:** el seed DE en txn revertida -> BD byte-identica despues (patron test_country_coexistence.py:364-366,454-455); conteos ES vivos inalterados.

**(g) Herramienta NEXT-LEVEL**
**schemathesis/schemathesis — MIT** — https://github.com/schemathesis/schemathesis **[VERIFIED NEXT-LEVEL.md:828]**, via *api-schema-fuzz* **[VERIFIED NEXT-LEVEL.md:825-831]**. Mas alla del golden escrito a mano, Schemathesis genera **miles de casos por endpoint** desde el `/openapi.json` que FastAPI ya expone y, con un check stateful custom + un hook de pais, auto-detecta 500s no documentados **Y bleed cross-country** ("toda respuesta con dimension pais solo trae ese pais" **[VERIFIED NEXT-LEVEL.md:831(3)]**) — el contrato se auto-ataca en cada push, hallando el province_code raro que ningun caso a mano cubre. **Companeros:** **oasdiff — Apache-2.0** https://github.com/oasdiff/oasdiff **[VERIFIED NEXT-LEVEL.md:836]** (*api-breaking-change-gate*, faceta 30: gate semantico de breaking-change para que anadir un pais nunca rompa el contrato pan-EU) y **tsenart/vegeta — MIT** https://github.com/tsenart/vegeta **[VERIFIED NEXT-LEVEL.md:844]** (*slo-perf-gate*, p99<50ms certificado). Todos EUR0, consumen el `/openapi.json` que FastAPI ya genera.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** El unico test 'de pais' (test_country_coexistence.py:309-458) prueba SOLO el schema backbone (PK/FK en txn revertida, cero endpoints, sin TestClient :40-46). El golden ES (test_country_golden.py) es a nivel de codigo (cdp_code), no HTTP. No existe suite que golpee /geo/seal, /geo/{prov}/entities, /tree, /stats, /geo/exhaustiveness, /search contra BD con 2o pais aseverando retorno mono-pais. Un pais puede declararse SELLADO mientras la API sangra filas ES en silencio.
- **Fix — propuesta [no implementada].** tests/test_api_country_nobleed.py con TestClient(app) + asyncpg, sembrando DE en txn que ROLLBACK (patron test_country_coexistence.py:259-285,416-458), cache_clear() (cache.py:168-170) antes de cada asercion. Por endpoint: country_code de respuesta HTTP == CC pedido == query SQL cruda (patron test_api_gaps.py:50-61); /ES disjunto de /DE en cdp_code; /DE tras /ES no recibe cuerpo cacheado ES. Gate CI, skip en schema mono-pais (guard test_country_coexistence.py:28-30,236-237).
- **Adversarial (DE/FR/IT/PT/no-UE).** DE/FR/IT/PT: sin suite, regresion de facetas 4-12 (predicado pais olvidado, cache key sin pais) pasa CI verde y solo se ve en prod. Provincia '28' = ES Madrid vs DE Brandenburg (test_country_coexistence.py:88-93), /geo/28/entities es el vector exacto. Cache: pais por header/tenant hace que ES-28 y DE-28 compartan key (cache.py:79-94 pliega solo path+query) -> DE recibe cuerpo ES hasta TTL.
- **Sellado + verificación multi-vía.** (1) La suite ES el sello: no-bleed por endpoint + disjuncion cdp_code + aislamiento-cache + golden-ES, verde sobre fixture 2-paises en txn revertida. (2) Dos oraculos: HTTP vs SQL asyncpg (test_api_gaps.py:50-61). (3) Break-the-guard: quitar un predicado pais -> test rojo. (4) Reversibilidad: seed DE en txn revertida, BD byte-identica, conteos ES inalterados (test_country_coexistence.py:364-366,454-455).
- **Herramienta NEXT-LEVEL (€0).** schemathesis/schemathesis — MIT [VERIFIED NEXT-LEVEL.md:828] — https://github.com/schemathesis/schemathesis (api-schema-fuzz): genera miles de casos desde /openapi.json, con check stateful+hook de pais auto-detecta 500s Y bleed cross-country [VERIFIED:831]. Companeros: oasdiff Apache-2.0 [VERIFIED:836] (breaking-change gate, faceta 30) y tsenart/vegeta MIT [VERIFIED:844] (p99<50ms). EUR0, consumen el openapi.json de FastAPI.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f30"></a>

### Faceta 30 · Snapshot OpenAPI/contrato de los 18 endpoints

**(a) code_hints VERIFICADOS**
- **No hay snapshot/openapi test** [VERIFIED] — grep de `openapi`/`snapshot` en tests/ devuelve NONE.
- **La app FastAPI genera el schema** [VERIFIED services/api/main.py:114]: `app = FastAPI(title="Cardeep API", version="0.2.0", lifespan=lifespan)` — expone /openapi.json automaticamente.
- **Exactamente 18 endpoints GET** [VERIFIED listado @router.get]: entities (4: /entities/{cdp}/canonical, /entities/{cdp}, /entities/{cdp}/inventory, /entities/{cdp}/delta), geo (6: /geo/completeness, /geo/seal, /geo/exhaustiveness, /geo/{prov}/entities, /geo/{prov}/municipalities/{muni}/entities, /geo/{prov}/tree), ops (4: /health, /stats, /alerts, /sources), platforms (2: /platforms/{cdp}/inventory, /vehicles/{ulid}/platforms), vehicles (2: /vehicles/{ulid}/history, /vehicles/{ulid}). Total 18.
- **El golden de cdp_code existe** como referencia de "mismo espiritu" [VERIFIED tests/test_country_golden.py existe].

**(b) El mecanismo al atomo**
FastAPI ya genera el contrato (app.openapi()), pero NADA lo congela. El atomo de deriva: anadir country a unas proyecciones y a otras no (faceta 24), o renombrar ccaa->admin1 para un pais (faceta 6), cambia la FORMA de salida sin detector mecanico — el "contrato generico" queda sin blindar. El golden de contrato pinea el JSON-shape de los 18 endpoints (mismo espiritu que el golden de cdp_code) y hace fallar CI ante cualquier cambio de forma no declarado.

**(c) Costura ES->generico**
El invariante del engine es "el binario de la API es identico entre paises / el contrato es country-invariante". Sin un gate, esa afirmacion es promesa, no garantia: una faceta futura puede cambiar la forma para un pais y romper en silencio a los consumidores del otro.

*Costura, fix, adversarial, sellado y herramienta NEXT-LEVEL: en la **Ficha operativa** inmediatamente debajo.*

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** FastAPI genera el schema (main.py:114) pero nada lo congela [VERIFIED no snapshot test]. Anadir country a unas de las 18 proyecciones y a otras no (faceta 24), o renombrar ccaa->admin1 para un pais (faceta 6), cambia la forma de salida sin deteccion. El contrato 'generico entre paises' no esta blindado mecanicamente.
- **Fix — propuesta [no implementada].** Anadir un golden que (a) snapshotea app.openapi() (la forma JSON de los 18 endpoints) a un fichero versionado y falla CI ante cualquier deriva de forma no declarada (mismo espiritu que el golden de cdp_code, tests/test_country_golden.py); y (b) en CI, diffea el openapi.json base vs HEAD y falla ante breaking changes. Actualizar el golden exige un commit intencional -> todo cambio de forma queda revisado. Aditivo, EUR0.
- **Adversarial (DE/FR/IT/PT/no-UE).** Una faceta futura cambia la forma de salida de un endpoint para un pais (p.ej. emite admin1 vs ccaa -faceta 6-, o country en data para unos endpoints y en meta para otros -faceta 24-) y rompe en silencio a los consumidores del OTRO pais (DE/FR/IT/PT) que esperaban el shape anterior — detectado solo en produccion sin el gate snapshot/diff. Ruido: un campo opcional anadido por error como requerido rompe a todo consumidor pan-EU.
- **Sellado + verificación multi-vía.** Criterio: la forma de los 18 endpoints es invariante entre paises salvo cambio declarado. Multi-via: (a) break-it — quitar un campo de cualquier endpoint hace fallar el gate (anti-drift via-b); (b) onboarding aditivo de pais -> 0 breaking changes (el invariante de genericidad se sostiene); (c) 2-via — oasdiff y openapi-diff coinciden en el veredicto sobre el mismo par de specs; (d) snapshot regenerado determinista — misma app -> mismo schema -> diff vacio.
- **Herramienta NEXT-LEVEL (€0).** oasdiff/oasdiff (api-breaking-change-gate) — Apache-2.0 [VERIFIED NEXT-LEVEL.md:836] — https://github.com/oasdiff/oasdiff . Match exacto: 'el contrato es generico entre paises como invariante mecanico' [NEXT-LEVEL:833]; entiende SEMANTICA de breaking changes (no diff textual) y es el estandar de gating de API en CI. 2a via: schemathesis/schemathesis — MIT [VERIFIED NEXT-LEVEL.md:828] — https://github.com/schemathesis/schemathesis : fuzz property-based de los 18 endpoints desde el schema para cazar 500s y, con hook de pais, bleed cross-country — ataca el comportamiento, no solo congela la forma.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="f31"></a>

### Faceta 31 · Runbook de rollback per-país de la capa de servido

**(a) Code_hints VERIFICADOS leyendo la fuente real**
- [VERIFIED services/api/cache.py:168-170] `def cache_clear() -> None: _cache.clear()`. La cache in-memory se vacia solo por esta llamada o por reinicio del proceso (el TTLCache no sobrevive a nada externo).
- [VERIFIED migrations/0055_product_stats.sql:14-15] la fila global id=1; HOY no hay fila por-pais que borrar, asi que un rollback de pais no puede quitar su contribucion quirurgicamente — debe recomputar toda la fila id=1 (hasta que aterrice faceta 3).
- [VERIFIED migrations/0046_servable_entity_status_filter.sql:31-42] bloque Rollback: servable_entity se restaura con CREATE OR REPLACE a la definicion quarantine-only de 37 columnas; aditivo/idempotente.
- [VERIFIED migrations/0056_v_servable_dealer.sql:45-46] rollback de v_servable_dealer = `DROP VIEW IF EXISTS v_servable_dealer`.
- [VERIFIED migrations/0053_country_onboarding.sql:176-181] precondicion: 'CLEAN ONLY while NO non-ES geo rows exist ... any pilot/onboarding MUST delete all country_code <> ES geo rows BEFORE rolling this back' (un PK monocolumna sobre code no puede sostener ES-28 y DE-28 a la vez).

**(b) Mecanismo al atomo**
Revertir un onboarding de pais desde la capa SERVIDA no es un solo DROP; es un procedimiento ordenado y reversible porque el servido guarda estado derivado/cacheado que sobrevive a las filas base:
1. Cache: el TTLCache in-memory aun retiene los cuerpos del pais retirado hasta 60s; hay que invocar cache_clear() (o reiniciar) o el borde sigue sirviendo dato retirado.
2. product_stats: hoy fila global unica — tras borrar las filas del pais queda DOBLE-CONTADA hasta que refresh_product_stats reejecuta; tras faceta 3 es una fila por-pais que hay que DELETE.
3. Views: servable_entity / v_servable_dealer son CREATE OR REPLACE (aditivos, country-blind) — no requieren revert por-pais, pero si una migracion de onboarding los altero, los bloques Rollback de 0046/0056 restauran la proyeccion previa exacta.
4. Filas base: la precondicion de rollback de 0053 obliga a borrar todas las filas geo country_code<>'ES' ANTES de revertir el PK compuesto (el PK monocolumna no coexiste con dos paises que comparten code).

**(c) Costura ES->generico + fix exacto**
NO hay criterio de rollback documentado para el servido — el diseno especifica onboarding pero no offboarding. Runbook exacto (doc aditiva + script), por pais CC:
1. Parar escrituras de CC (scheduler/harvest de CC en pausa).
2. DELETE de filas base servidas de CC en orden FK-safe: entity/vehicle/platform_listing/... WHERE country_code=CC; denominator_estimate/organization WHERE country_code=CC; geo_municipality/geo_comarca/geo_province WHERE country_code=CC (hijos antes que padres) — satisfaciendo la precondicion de 0053.
3. product_stats: `DELETE FROM product_stats WHERE country_code=CC` (post faceta-3) O reejecutar refresh de la fila global (pre faceta-3).
4. cache_clear() (o reiniciar uvicorn) para que el TTLCache suelte los cuerpos de CC al instante; con el borde Souin (faceta 17) purgar el key-space de CC.
5. country_registry: DELETE la fila CC (su admin1_label/display_name) para que /countries (faceta 25) y el label admin1 (faceta 6) dejen de anunciar CC.
6. Verificar ES byte-identico (golden) y la precondicion del PK compuesto (cero filas geo no-ES) antes de cualquier reversal de esquema 0053.

**(d) Riesgo adversarial concreto**
Revertir un pais en caliente sin flush deja la cache sirviendo el dato del pais retirado durante todo el TTL de 60s, y /stats reporta un total inflado (el pais retirado aun sumado en id=1) hasta el siguiente refresh manual — el titular publico miente en silencio durante la ventana. Saltarse el orden del paso 2 o la precondicion de 0053 deja FKs huerfanas o bloquea la reversion del PK.

**(e) Criterio de sellado + verificacion multi-via**
1. Golden de reversibilidad: onboardear DE en txn revertida, correr el script de rollback, asegurar DB+API byte-identicos al baseline ES pre-DE (cero residuo) — el mismo harness de coexistencia (test_country_coexistence.py) extendido a offboarding.
2. Prueba de cache: tras rollback, una peticion del path del pais retirado devuelve 404/vacio, NO un cuerpo cacheado stale (asegurar que cache_clear corrio; 2a via: el key-space del borde esta vacio para CC).
3. Prueba de titular: /stats (o /stats?country=ES) == el valor ES pre-onboarding inmediatamente tras rollback+refresh (sin residuo de doble-conteo).
4. Precondicion de esquema: `count(*) FROM geo_province WHERE country_code<>'ES'` == 0 antes de cualquier down-migration de 0053 (guard mecanico de 0053:176-181).

**(f) Herramienta NEXT-LEVEL (nivel inalcanzable)**
[VERIFIED NEXT-LEVEL.md:592-598] **transitions (pytransitions)** (MIT [VERIFIED], EUR0) — https://github.com/pytransitions/transitions — modelar el ciclo de vida de pais cover(CC) (REGISTERED->KNOW_COUNTRY->BOOTSTRAPPED->IN_COVERAGE->SEALED, +REOPENED) como una maquina de estados declarativa y guard-gated persistida en country_campaign.state, donde el offboarding es una transicion legal con conditions=(cache_flushed, rows_deleted, stats_recomputed, precondition_zero_nonES) — la libreria rechaza todo salto ilegal y GraphMachine renderiza el diagrama del funnel, convirtiendo la prosa de rollback ad-hoc en una transicion impuesta y diagramable.

**Ficha operativa (cierre 360°):**

- **Costura (ES→genérico).** No existe criterio de rollback del servido (el diseno cubre onboarding, no offboarding). El TTLCache solo se vacia por cache_clear()/restart [VERIFIED cache.py:168-170]; product_stats es single-row id=1 [VERIFIED 0055:15] sin fila por-pais que borrar; la precondicion 0053:176-181 exige cero filas geo no-ES antes de revertir el PK compuesto.
- **Fix — propuesta [no implementada].** Runbook + script por pais CC: (1) parar writes; (2) DELETE filas base WHERE country_code=CC en orden FK-safe (hijos->padres); (3) DELETE product_stats WHERE country_code=CC (post f3) o refresh global (pre f3); (4) cache_clear()/restart + purgar key-space CC en Souin; (5) DELETE country_registry CC; (6) verificar ES byte-identico y cero geo no-ES antes del reversal 0053. Views via CREATE OR REPLACE/DROP (0046/0056).
- **Adversarial (DE/FR/IT/PT/no-UE).** Revertir en caliente sin flush -> la cache sirve el pais retirado todo el TTL de 60s y /stats reporta total inflado (id=1 aun lo suma) hasta el refresh manual; saltarse el orden FK o la precondicion 0053 deja FKs huerfanas o bloquea la reversion del PK.
- **Sellado + verificación multi-vía.** (1) golden de reversibilidad: DE en txn revertida + rollback -> DB+API byte-identicos al baseline ES (test_country_coexistence extendido); (2) post-rollback el path de CC da 404/vacio, no cuerpo stale (cache_clear corrio); (3) /stats == valor ES pre-onboarding tras refresh; (4) count geo_province no-ES == 0 antes del down-migration 0053.
- **Herramienta NEXT-LEVEL (€0).** [VERIFIED NEXT-LEVEL.md:592-598] transitions (pytransitions) (MIT, EUR0) https://github.com/pytransitions/transitions — cover(CC) como FSM guard-gated persistida en country_campaign.state; offboarding = transicion legal con conditions=(cache_flushed, rows_deleted, stats_recomputed, precondition_zero_nonES); GraphMachine diagrama el funnel y la libreria rechaza saltos ilegales.

[↩ Índice de sub-proyectos](#indice-subproyectos)

---

## Mejoras a nivel inalcanzable (€0, priorizadas)

> Cada mejora se profundiza como **sub-proyecto 360°** en su faceta: 1→[F2](#f2), 2→[F12](#f12), 3→[F22](#f22), 4→[F30](#f30), 5→[F23](#f23), 6→[F24](#f24), 7→[F25](#f25), 8→[F27](#f27), 9→[F20](#f20). El índice vive en [Sub-proyectos institucionales](#indice-subproyectos).

| Prio | Mejora | Por qué (verificado) | €0 | Esfuerzo |
|---|---|---|---|---|
| 1 | **Cablear `v_servable_dealer` (0056)** como definición ÚNICA en `/stats`, `/geo`, `/seal` | La vista existe pero ningún router la referencia `[VERIFIED 0056; grep=0]`; 3 scopes divergentes (~54.6k vs ~36.3k vs ~18.3k) ⇒ el titular nunca cuadra con lo paginado. Cierra el gate de coherencia. | sí | S |
| 2 | **`v_exhaustiveness_seal` latest-build POR PAÍS** | Hoy global `[VERIFIED 0048:82-88]`; sin esto el sello no es durable entre países (SH3/SH6). | sí | S |
| 3 | **`/search` typo-tolerante country-scoped** sobre GIN trgm ya instalado | Ausente `[VERIFIED grep=0]` pese a sustrato desde 0005 `[VERIFIED 0005:6-7]`. El endpoint de mayor leverage. | sí | M |
| 4 | **OpenAPI/contract snapshot test** que congele el JSON-shape de los 18 endpoints como golden | FastAPI genera el schema; falta pinearlo. Convierte "el contrato es genérico" de afirmación a invariante mecánico (espíritu del golden `cdp_code`). | sí | S |
| 5 | **Índice compuesto `(country_code, trade_name gin_trgm_ops)`** vía `btree_gin` | `btree_gin` ya instalado `[VERIFIED 0005:7]`; sin él `/search` filtra país y luego trigram-scan. | sí | S |
| 6 | **Campo `country_code` aditivo** en cada objeto de salida + `meta.country` | Hoy ninguna respuesta lleva país (implícito ES). Aditivo; habilita consumidores pan-EU. | sí | M |
| 7 | **Endpoint `/countries`** que lista censos servibles con su cota sellada y `computed_at` | No existe índice de países servidos; el `country_registry` lo habilita. | sí | S |
| 8 | **Paginación keyset** (cursor `(first_seen,vehicle_ulid)`) + ETag/If-None-Match | `OFFSET` grande es O(n) en tablas 500k+ `[VERIFIED page_slice usa OFFSET, geo.py:253,316]`; keyset es O(log n) y estable bajo inserción concurrente. | sí | M |
| 9 | **Reverse-proxy €0 (Caddy)** terminando TLS + HSTS delante de uvicorn loopback | La app sirve PII por HTTP en loopback; prod multi-país necesita TLS. Caddy auto-TLS es €0 pero requiere proceso de borde + DNS — **gate de infra**. | sí | M |

---

## Riesgos / open items

- **Costura silenciosa de agregados (corrección, no error visible):** añadir un 2º país sin parametrizar `/stats`+`/geo/completeness`+`/geo/seal`+`/geo/exhaustiveness` `[VERIFIED geo.py:32,92,147; ops.py:49]` produce un total ES+CC mezclado con apariencia correcta. Debe blindarse con el test HTTP-vs-SQL country-scoped (SH1) ANTES de sembrar CC.
- **`servable_entity` sin `country_code` es bloqueante (MP3):** hasta que el view lo proyecte `[VERIFIED 0046:17-29]`, ningún endpoint geo puede filtrar país por mucho parámetro que se añada. Primera ficha del dominó.
- **OPEN ITEM — denominador por país (gate LEGAL/ToS + GASTO, PENDING-OWNER):** sin fuente equivalente a DIRCE/DGT cableada, `/geo/seal` de un país nuevo es `NO_DENOM` permanente `[VERIFIED 0042:37; 0043:62]`. No bloquea el diseño del servido; bloquea la **certificación** de ese país. Honesto: se muestra como "no certificable".
- **OPEN ITEM cross-stage — identidad cross-border (etapa 4):** `canonical_key` country-blind `[VERIFIED codes.py:56-65]` puede fusionar miembros de varios países en un cluster. El servido lo **defiende** (filtra el fan-out por país, B6) pero la decisión de threadear país en la clave es de 04-identity, con su propio golden.
- **OPEN ITEM — decisión de entrada de país (MP6):** ningún endpoint acepta país hoy `[VERIFIED grep=0]`. Propuesta: path-segment `/{cc}/…`. Hasta tomarla, el predicado SQL y la cache key no tienen de dónde leer el país (bloquea B2, B7, SH2).
- **Cache key sin dimensión tenant (B7):** segura bajo una sola API key `[VERIFIED cache.py:82-85]`; debe resolverse antes de multi-tenant auth.
- **TLS no terminado por la app (gate de infra):** sirve PII por HTTP en loopback `[VERIFIED main.py:155 uvicorn host="127.0.0.1" port=8090]`; sin reverse-proxy TLS en el borde, exponerla en prod multi-país filtra PII en claro. No bloquea el diseño; sí el despliegue.
- **rate-limit leído una vez al import:** togglear/ajustar límites en caliente no surte efecto sin reiniciar `[VERIFIED ratelimit env-gated al import]`; un operador podría creer que ajustó el límite por país y no.
- **`DEFAULT_COUNTRY='ES'` es ancla y mina a la vez `[VERIFIED codes.py:24]`:** conservarlo para el golden, pero exigir país explícito en todo handler multi-país; cualquier ruta que maneje un código sin threadear país asume ES en silencio.
