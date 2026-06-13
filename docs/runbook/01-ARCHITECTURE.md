# 01 · ARCHITECTURE — el motor

> El sustrato común que toda fuente atraviesa: **governor · fetch · schema · geo · cdp_code ·
> VAM · S-HEALTH · API · dedup watermark**. Recontado vivo esta sesión contra
> `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`.
>
> **ENV verificado:** Python `C:/Users/elias/AppData/Local/Programs/Python/Python311/python` ·
> API deps `fastapi 0.135.3`, `uvicorn 0.44.0`, `asyncpg`, `curl_cffi` (importan OK).
>
> **Aviso de deriva (cero maquillaje):** la DB está en ingesta viva. Donde un veredicto va por
> detrás del conteo vivo, se da el **id + valor sellado** Y el **valor vivo**, con la deriva
> declarada. La metodología (≥2 caminos, divergencia 0) se reconfirma viva endpoint a endpoint.

---

## 1. GOVERNOR — el cuello mecanizado (`pipeline/engine/governor.py`)

**Qué es.** El único choke point de rate ante CADA fetch: un token-bucket continuo **por host
registrable**, asyncio-safe, compartido por todas las corrutinas. Por muchos workers que corran,
el agregado contra un host no supera su bucket; buckets independientes (el throttling de AS24
jamás frena a Kia).

**La cicatriz AS24.** Existe para hacer imposible *"138 dealers cayeron por throttling agregado
bajo carga 4x"*. Cuatro workers educados cada uno, pero el agregado era un martillo porque nada
los coordinaba. Fix: **un** token-bucket por host, compartido (`governor.py:4-9`).

**Las dos clases de rate (`_HOST_RATE_CLASSES`, `governor.py:84-141`):**

| Clase | rate | burst | min_spacing | jitter | Para qué |
|---|---:|---:|---:|---:|---|
| **STEALTH** (default) | 0,7 req/s | 3,0 | 1,43 s | 0,25 s | HTML / stealth / WAF, techo NO medido. La cicatriz vive aquí: por debajo del ritmo que ganó el ban. NUNCA se sube sin evidencia. |
| **JSON_API** | 12 req/s | 24,0 | 0,03 s | 0,02 s | gateways JSON first-party (backends SPA/móvil hechos para servir millones). |

Constantes: `DEFAULT_RATE_PER_SEC=0.7`, `DEFAULT_BURST=3.0`, `DEFAULT_JITTER_S=0.25`
(`governor.py:51-54`); `JSON_API_RATE_PER_SEC=12.0`, `JSON_API_BURST=24.0`,
`JSON_API_MIN_SPACING_S=0.03`, `JSON_API_JITTER_S=0.02` (`governor.py:88-91`).

**Hosts JSON_API registrados** (`governor.py:102-141`): `web.gw.coches.net`, `api.wallapop.com`,
`gql.autocasion.com`, `es.renew.auto`, `scs.audi.de`, `kiaokasion.net`, `services.flexicar.es`,
`api-carmarket.ayvens.com`.

**Overrides per-host (la cicatriz codificada, `governor.py:312-364`)** — STEALTH explícito por
debajo del default donde el techo es desconocido:

| Host | rate | burst | min_spacing | Razón |
|---|---:|---:|---:|---|
| `www.autoscout24.es` / `autoscout24.es` | 0,5 | 2,0 | 2,0 s | LA cicatriz: por debajo del ritmo que ganó el ban. |
| `www.coches.com` | 1,0 | 3,0 | 0,8 s | Imperva-fronted sirviendo a chrome131 (ventana decaying-open). |
| `www.dasweltauto.es` | 1,0 | 3,0 | 0,8 s | AEM/Motorflash SSR tras muro TLS/UA suave (t1_soft). |
| `www.autocasion.com` | 4,0 | 8,0 | 0,25 s | CF MEDIDO permisivo; subido 2,0→4,0 monitoreado para drain PDP-per-car. Reversible: ban→breaker→revertir. |
| `carmarket.ayvens.com` | 1,0 | 3,0 | 0,8 s | Origen HTML del SPA (ya NO es el data-path; el GraphQL `api-carmarket` lo es). |
| `www.ocasionplus.com` | 1,0 | 3,0 | 0,8 s | Next.js SSR, JSON-LD ItemList, t0_open pero superficie SSR. |

**Mecánica del bucket (`_Bucket`, `governor.py:161-208`):** refill continuo
(`min(burst, tokens + elapsed*rate)`); `acquire()` bloquea hasta token disponible **Y** que haya
pasado `min_spacing (+jitter)`; matemática bajo `asyncio.Lock` por host (atómica). Empieza lleno
(primer request inmediato). Token-bucket: no hay release. Integración (`wrap_fetch_text`,
`governor.py:280-299`): deriva el host, `await acquire(host)`, corre el curl_cffi síncrono en
`asyncio.to_thread` (event loop nunca bloqueado).

**Resultado validado vivo (la cicatriz NO se repite):** `source_breaker` = **35 closed, 0 open**;
`source_health` = **33 healthy, 2 degraded, 0 down**; `harvest_run` = **170 ok / 9 fail**.
Battle-test S-HEALTH 25/25 PASS.

---

## 2. FETCH — curl_cffi por tiers + escalada de navegador (`pipeline/engine/fetch.py`)

**Tier-0 (`fetch.py:1-21`).** `curl_cffi` con impersonación de navegador completa: fingerprint
TLS/JA3 + HTTP2 de Chrome real, **coherente a nivel de sesión** (una `Session` → un fingerprint →
un cookie jar). Perfil `_IMPERSONATE = "chrome131"` (`fetch.py:31`). Reemplaza urllib porque los
WAF cierran sobre el *fingerprint del cliente*, no el UA: urllib emite un handshake TLS de Python
que un WAF marca al instante; curl_cffi emite el de Chrome.

**Headers (`fetch.py:33-47`).** `_DEFAULT_HEADERS`: UA Chrome 131, `Accept` html/xhtml/avif/webp,
`Accept-Language: es-ES,es;q=0.9,en;q=0.8`, `Upgrade-Insecure-Requests: 1`, `Sec-Fetch-*`.
`fetch_text(url, *, tier=0, headers=None)` mergea headers extra sobre el default.

**Retry (`fetch.py:49-134`).** `_RETRYABLE = {429,500,502,503,504}`; `_TIMEOUT=40`;
`_MAX_RETRIES=4`; backoff exponencial `_BACKOFF_BASE=2.0` (2,4,8,16 s) con **full jitter**,
honrando `Retry-After` (cap 30 s); espera educada `_POLITE_MIN=0.7`/`_POLITE_MAX=1.4`. **Falla en
voz alta:** un status no-retryable (403/404/410…) lanza `FetchError` — nunca devuelve un body de
challenge/vacío en silencio.

**Escalada Tier-1 (el seam, `fetch.py:14-20`, 94-98).** Con `tier >= 1` este módulo **lanza
`NotImplementedError`** apuntando al path camoufox: el caller elige el motor explícitamente y un
target Tier-1 jamás cae en silencio al Tier-0 insuficiente. Doctrina
(`docs/architecture/02-SCRAPING-ENGINE.md`): T0 curl_cffi optimista primero, escala **solo ante
una respuesta de challenge tipada** ("optimism is free; escalation is on evidence"). Injector
stealth canónico: `patchright`/`DynamicFetcher` (forma Chromium), **camoufox** (forma Firefox).

**Validado vivo.** El stock GRATIS de las 6 Tier-1 se cerró con Tier-0. La escalada de navegador
se usó realmente para `coches.net` VN/km0/renting tras Imperva (camoufox, +10.470 aristas) y para
subastas Autorola+BCA (Playwright JS) — ambos cerrados gratis, VAM 2 caminos.

---

## 3. SCHEMA — migraciones, enums, tablas clave

**Migraciones aplicadas (`schema_migrations`, verificado vivo):**
`0001, 0002, 0003, 0004, 0005, 0006, 0007, 0009, 0013, 0016, 0017, 0018, 0019`.

Huecos **intencionados** (no son fallo): `0008` (partición de `vehicle` por provincia) está
DEFERIDA por diseño — `0009` se creó NON-partitioned y se re-homea cuando aterrice `0008`
(`migrations/0009_platform_listing.sql:5-14`). `0010-0012`, `0014`, `0015` no existen en el árbol.

**`entity_kind` enum (`0005:12-18` + `0017:21`).** Valores: `concesionario_oficial,
agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta, importador,
oem_vo_portal, plataforma, cadena (DEPRECATED read-only), particular`. Distribución viva:

| kind | vivo | kind | vivo |
|---|---:|---|---:|
| `particular` | 326.117 | `compraventa` | 31.513 |
| `garaje` | 7.220 | `concesionario_oficial` | 1.681 |
| `desguace` | 1.645 | `subasta` | 94 |
| `oem_vo_portal` | 14 | `plataforma` | 10 |
| `cadena` | 4 | `rent_a_car_vo` | 3 |

**`particular` (`0017`):** vendedor privado como entidad de 1ª clase — donde la fuente expone
seller-id estable (milanuncios authorId, wallapop user_id) → 1 entidad por humano; donde anonimiza
(coches.net) → 1 bucket por provincia. NUNCA se fabrica identidad que la fuente oculta.

**Multi-eje de clasificación (`0016_tiering_groups.sql`).**
- `defense_tier` enum: `t0_open` (sin muro), `t1_soft` (WAF sirviendo a curl_cffi), `t2_js_challenge`
  (navegador stealth para cookie), `t3_hard_sensor` (Akamai/Kasada/PX), `t4_spend_gated` (solo
  residencial/sensor de pago). Vivo: `t0_open 196`, `t1_soft 19`, `t2_js_challenge 1` (resto NULL).
- `source_group` enum (11): `marketplace_generalist, marketplace_motor, oem_vo_portal,
  oem_dealer_network, chain, rentacar_vo, official_registry, association, directory,
  desguace_network, long_tail_web`.
- `entity_role` enum: `platform, dealer_network, chain, standalone_pos, registry, directory`.

**`platform_listing` — la arista dual-membership (`0009` + `0019`).** PK `(vehicle_ulid,
platform_entity_ulid)` — una arista por (coche, plataforma). `vehicle.entity_ulid` queda el DEALER
vendedor (propiedad singular); la membership de plataforma es ESTA arista (plural, 0..M). Columnas:
`listing_url`, `listing_ref`, `platform_price`, `listing_fingerprint` (hash cross-platform
same-car), `status listing_status`, `first/last_seen`, `removed_at`. `0019` añade `segment` CHECK
`IN ('used','new','km0','renting')` DEFAULT `'used'` — el segmento es propiedad de la arista.

**Otras tablas.** `vehicle`/`vehicle_event` (`0003`): snapshot + delta append-only, enum
`vehicle_event_type` (`0005:56-61`) `NEW, GONE, REAPPEARED, PRICE_CHANGE, PHOTO_CHANGE, KM_CHANGE,
STATUS_CHANGE, SPEC_CHANGE`. `entity_source`/`entity_alias` (`0002`): provenance
capture-recapture + dedup. `organization` (`0007`): capa cadena/grupo (**vacía viva, 0 filas**).
`platform_meta` + vista `platform` (`0006`). Trigger compartido `cardeep_block_mutation()`
(`0005:71-76`) prohíbe UPDATE/DELETE en logs append-only.

---

## 4. GEO — jerarquía país / provincia / comarca / ciudad + cdp_code

**Backbone INE (`0001_geo.sql` + `0018_comarca.sql`).** `pais → PROVINCIA → COMARCA → ciudad`.
- `geo_province`: PK `code CHAR(2)` (INE), `name`, `ccaa_code`, `ccaa_name`.
- `geo_comarca`: PK `id` IDENTITY, FK `province_code`, `name`, UNIQUE(province_code,name); `0018`
  añade `ine_code CHAR(2)` + `source`.
- `geo_municipality`: PK `code CHAR(5)` (INE; provincia = izq 2), `name`, FK `province_code`, FK
  `comarca_id`, `lat`/`lon`. **Invariante CHECK:** `left(code,2) = province_code`.

**Geocoder/trigger (`0018_comarca.sql:27-40`):** `entity_set_comarca()` BEFORE INSERT/UPDATE OF
`municipality_code` ON `entity` resuelve `comarca_id` desde `geo_municipality` automáticamente:
toda entidad live-insertada hereda su comarca sin backfill. Backfill histórico:
`scripts/backfill_comarca.py`.

**`cdp_code` — código inmutable (`services/api/codes.py`).** Determinista sobre la identidad
canónica: re-descubrir la misma entidad por otra fuente NO acuña un segundo código. Prioridad de
`canonical_key` (`codes.py:34-70`): `particular(platform:sellerId)` > `domain` (host pelado; **una
URL con path NUNCA es identidad** — evita el colapso Hyundai 175→48) > `CIF` >
`name|municipality_code(|address)` > `name|province_code(|address)`. Formato:
`CDP-ES-{province2}-{8×Crockford-base32(sha256(key))}` (sin I,L,O,U).

**Validado — veredicto `geo_hierarchy` id=581 (TRUSTWORTHY, divergencia 0).** Inventario por
comarca reconcilia vía `entity.comarca_id` directo (Path A = 240.245) == vía `municipality→comarca`
join (Path B = 240.245). `provinces_served = 52/52`, `comarcas_served = 322/323`,
`municipality_with_comarca = 8.130/8.132 (99,98 %)` — los 2 sin comarca son Ceuta/Melilla.
**Grid vivo esta sesión:** `52 / 323 / 8.132 / 8.130`.

---

## 5. VAM — verificación adversarial multi-vía

**Qué es.** El juez de "verificado": ≥2 caminos ortogonales por claim, con la **invariante de
landed-count** (el conteo que vive en la DB DEBE estar entre los que coinciden). Ledger:
`verification_verdict` (`0004_verification_health.sql:5-21`). Columnas: `id` BIGINT IDENTITY,
`subject_type`, `subject_key`, `claim`, `primary_value`, `primary_path`, `verifier_paths JSONB`,
`independent_values JSONB`, `divergence DOUBLE PRECISION`, `verdict` CHECK
`IN ('TRUSTWORTHY','REFUTED','UNVERIFIED')`, `evidence`, `created_at`.

**Quórum (05-VAM §2.2).** Dado caminos `P={p₁:v₁,…}` con `p₁` = landed truth: `<2` caminos
no-null → UNVERIFIED; mayoría limpia con `primary_agrees` y sin rivales → TRUSTWORTHY;
`divergence ≤ tolerancia` → TRUSTWORTHY; desacuerdo real → REFUTED. Tres propiedades: (1) un camino
que sobre-cuenta solo NO puede refutar; (2) `primary_agrees` es la invariante de landed-count;
(3) `rivals` detecta un split (no se promedian dos números en desacuerdo).

**Estado vivo del ledger (esta sesión).** **587 veredictos: 577 TRUSTWORTHY, 10 REFUTED.** Por
`subject_type`: `entity_inventory` 371, `platform_slice` 135, `family_slice` 36, `source` 10,
`platform_segment` 8, `platform_facet` 7, `group_vam` 5, `global_count` 4, `platform_segment_slice`
4, `cross_platform_dedup_watermark` 3, `geo_hierarchy` 1, `api_serves` 1, `dedup_watermark` 1,
`platform_facet_mb_split` 1.

**Veredictos `global_count` (TRUSTWORTHY, div 0 — `count(*)` == suma de partición):**

| id | subject_key | claim | valor sellado | vivo esta sesión |
|---|---|---|---:|---:|
| 577 | `vehicle_total` | count* == Σ(available+reserved+gone) | 1.332.980 | 1.485.133 |
| 578 | `entity_total` | count* == Σkind == Σrole | 309.148 | 368.301 |
| 579 | `platform_listing_total` | count* == Σ status | 1.286.776 | 1.438.443 |
| 580 | `vehicle_event_total` | count* == Σ event_type | 1.336.079 | (ingesta viva) |

> **Honestidad:** el valor de cada veredicto es el SELLADO en su barrido; el vivo es mayor por
> ingesta continua. La metodología (las 3 vías coinciden exactas) se sostiene: la deriva absoluta
> es ingesta, NO descuadre.

Los **10 REFUTED** (confesados, NO servidos) están enumerados en
[NOT-VALIDATED.md](NOT-VALIDATED.md). Son outcomes de PRIMERA CLASE (rutan la entidad FUERA del
set servido), no fallos del verificador.

---

## 6. S-HEALTH — watchdog, alerta de origen exacto, breaker, auto-repair

**Qué es.** El cableado que hace cierto *"si una fuente falla, salta una alerta con el ORIGEN
EXACTO, se auto-repara, y Cardeep nunca se cae"*. Fichero `pipeline/ops/health.py`; sustrato
`0013_resilience.sql` + tablas `0004` `source_health`/`alert`.

**Esquema.**
- `source_breaker` (`0013:19-26`): PK `source_key`, `state` CHECK `IN ('closed','open','half_open')`,
  `consecutive_fails`, `opened_at`, `cooldown_until` (sobrevive a restart).
- `harvest_run` (`0013:30-39`): `source_key`, `started_at`, `finished_at`, `ok`, `rows`, `error`,
  `http_status` — la auditoría que faltó al incidente 138.
- `repair_attempt` (`0013:45-54`): `source_key`, `detected_reason`, `action` CHECK
  `IN ('refingerprint','escalate_tier','re_receta','quarantine','escalate_owner')`, `succeeded`.
- `source_health` (`0004:24-31` + `0013:61-62`): `consecutive_fails`, `status` CHECK
  `IN ('healthy','degraded','down','unknown')`, `is_tier1`, `tuning JSONB`.
- `alert` (`0004:34-43`): `origin`, `severity` CHECK `IN ('info','warning','critical')`, `message`,
  `payload JSONB`, `resolved_at`.

**La máquina (`health.py`).**
- `record_run(...)` (`76-192`): ÚNICO escritor de `source_health` + `source_breaker`. Escribe
  `harvest_run`, lee-modifica-escribe bajo `FOR UPDATE` (single writer, sin lost-update), trip del
  breaker a OPEN tras `BREAKER_TRIP_AT=3` fallos con cooldown exponencial `min(900*2^depth, 86400)`.
  Umbrales `DEGRADE_AT=1`, `DOWN_AT=3`, `BREAKER_COOLDOWN_SEC=900`.
- `build_origin(source_key, phase, cdp_code)` (`195-198`): clave `<source_key>:<phase>[:<cdp_code>]`.
- `fire_alert(...)` (`201-230`): escribe `alert` con origen exacto; **dedup** (138 dealers = UNA
  alerta AS24, no 138 filas).
- `classify_failure(reason, http_status)` (`246-278`): determinista, €0. 401/403/challenge →
  `refingerprint` (o `escalate_tier` si Akamai/DataDome/PX); 429/ban → `quarantine`;
  null/drift/schema → `re_receta`; desconocido → `escalate_owner`.
- `auto_repair(...)` (`287-346`): clasifica, loguea, dispara alerta, devuelve acción. `quarantine`
  y `escalate_owner` **efectivos ya** (€0); `refingerprint`/`escalate_tier`/`re_receta`
  **scaffolded tras P10 spend-gate** (`_SPEND_GATED_ACTIONS`): el LAZO corre real, solo el efecto
  con gasto se difiere (`succeeded=FALSE`, `repair_outcome='pending'`).
- `is_open(conn, source_key)` (`349-372`): gate que el harvest llama ANTES de correr. OPEN → skip
  graceful. Pasado `cooldown_until` → `half_open` (probe canario).

**Validado vivo.** `source_breaker` **35 closed / 0 open**; `source_health` **33 healthy /
2 degraded / 0 down**; `harvest_run` **170 ok / 9 fail**. `repair_attempt` **9**: `escalate_owner`
6, `quarantine` 1, `refingerprint` 2 (P10-pending, coherente con el spend-gate). Battle-test 25/25
PASS.

---

## 7. API — endpoints, envelope, arranque confirmado (`services/api/main.py`)

**Qué es.** API live FastAPI sobre PostgreSQL. Envelope `{ok, data, error, meta}`
(`main.py:33-38`). DSN por env `CARDEEP_DSN`. Pool asyncpg `min_size=1, max_size=8`.

| Método | Endpoint | Qué sirve |
|---|---|---|
| GET | `/health` | counts vivos (entities, vehicles_available, events, provinces, municipalities) |
| GET | `/entities/{cdp_code}` | la entidad + `available_inventory` |
| GET | `/entities/{cdp_code}/inventory` | vehículos available (deep_link, make…price…last_seen) |
| GET | `/entities/{cdp_code}/delta` | `vehicle_event` (?since=ISO), limit 500 sin since |
| GET | `/geo/{province_code}/entities` | entidades de la provincia |
| GET | `/geo/{province_code}/tree` | árbol país→provincia→comarca→ciudad, 0 ruido NULL-geo |
| GET | `/geo/completeness` | reporte nacional de completitud geo |
| GET | `/platforms/{cdp_code}/inventory` | coches de una plataforma vía `platform_listing` + dealer |
| GET | `/vehicles/{vehicle_ulid}/platforms` | plataformas de un coche + su dealer dueño singular |

Guard: `/platforms/{cdp_code}/inventory` devuelve **400** si la entidad no es `kind=plataforma`
(`main.py:218-219`).

**Validado — veredicto `api_serves` id=583 (TRUSTWORTHY, divergencia 0).** `subject_key =
cardeep_api_8094`, `primary_value = all_endpoints_200`. El geo tree reconcilia con DB directa:
`/geo/28/tree` `entities_geo_clean` (API) == DB Path B (`entity JOIN geo_municipality JOIN
geo_comarca`) **exacto**, top comarca `Area Metropolitana de Madrid` API == DB exacto. La deriva de
absolutos es ingesta viva; la **reconciliación A==B se sostiene exacta**.

---

## 8. Watermark de dedup cross-platform

Mide (NO mergea) el sobre-conteo de "el mismo coche en varias plataformas". Dos veredictos, ambos
TRUSTWORTHY.

**`dedup_watermark` id=582 (TRUSTWORTHY, div 0) — partición 1:1 limpia.** Ningún `vehicle_ulid`
mapea a >1 `platform_entity_ulid`: `vehicles_on_multiple_platform_entities = 0`, `excess_edges = 0`.
Cada coche cuelga de UNA plataforma-entidad.

**`cross_platform_dedup_watermark` ids 556 / 559 / 574 (TRUSTWORTHY) — cota inferior del
sobre-conteo SAME-CAR.** Cota INFERIOR sobre el piso fuzzy estricto (make+model+year+km+price+
province); auto-merge limitado a VIN-exacto (`photo_hash` sin poblar). Dos caminos ortogonales
`excess_sql_groupby` vs `excess_python_grouping`: id=556 SQL 132.016 / Python 132.043; id=559
132.157 / 132.178; **id=574 (más reciente) SQL 134.007 / Python 134.019 (div 0,00009)**.
**MEASURE-ONLY, NO merge:** ≈134.027 filas excedentes (14,36 %, cota inferior). El merge
cross-seller está fuera de v1 (ver [NOT-VALIDATED.md](NOT-VALIDATED.md)).

---

> **Evidencia por unidad:** §1 governor (35 closed/0 open + battle-test 25/25); §2 fetch (Tier-0
> vivo + seam Tier-1 falla fuerte); §3 schema (`schema_migrations` 0001-0019 + enums vivos); §4 geo
> (id=581); §5 VAM (ledger 577 TRUSTWORTHY + global_count 577-580); §6 S-HEALTH (estado vivo +
> repair coherente con spend-gate); §7 API (arrancada + reconcile A==B + id=583); §8 watermark (ids
> 582 + 574). Conteos cruzados contra la DB viva esta sesión, deriva de ingesta declarada.
