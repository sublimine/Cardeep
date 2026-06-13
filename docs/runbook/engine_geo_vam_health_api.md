# RUNBOOK — Motor, Geo, VAM, S-HEALTH, API, Esquema

> Dominio: `engine_geo_vam_health_api`. Guía operativa de **lo que funciona y está
> validado**. Regla dura: una unidad entra aquí **solo** si tiene `verification_verdict`
> persistido (TRUSTWORTHY) **y/o** un conector commiteado que se confirma que arranca.
> Lo aspiracional / no validado / roto va al final, en **§NO validado (fuera del runbook)**.
>
> **Entorno (verificado esta sesión):**
> - Python: `C:/Users/elias/AppData/Local/Programs/Python/Python311/python`
> - DB viva: `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`
> - Deps API: `fastapi 0.135.3`, `uvicorn 0.44.0`, `asyncpg`, `curl_cffi` (importan OK).
>
> **Aviso de deriva (cero maquillaje):** la DB está en **ingesta viva**. El último barrido
> VAM se selló a `2026-06-13 06:48:51 UTC`; desde entonces la cosecha siguió drenando, así
> que los absolutos vivos son **mayores** que los del veredicto. Donde citamos un veredicto
> damos su **id + valor sellado** Y el **valor vivo** medido esta sesión, con la deriva
> declarada. La metodología (≥2 caminos, divergencia 0) se reconfirma viva endpoint a
> endpoint. Conteos vivos de esta sesión (`SELECT count(*)`):
>
> | tabla | vivo (esta sesión) | tabla | vivo (esta sesión) |
> |---|---:|---|---:|
> | `entity` | 367.831 | `vehicle` | 1.482.522 |
> | `vehicle` available | 1.481.148 | `vehicle_event` | 1.485.644 |
> | `platform_listing` | 1.436.160 | `organization` | 0 |
> | `geo_province` | 52 | `geo_comarca` | 323 |
> | `geo_municipality` | 8.132 | muni con comarca | 8.130 (99,98%) |

---

## 0. Migraciones aplicadas (verificado en `schema_migrations`)

`SELECT version FROM schema_migrations ORDER BY version` →
`0001, 0002, 0003, 0004, 0005, 0006, 0007, 0009, 0013, 0016, 0017, 0018, 0019`.

Huecos **intencionados** (no son fallo): `0008` (partición de `vehicle` por provincia) está
DEFERIDA por diseño — `0009` se creó NON-partitioned y se re-homea cuando aterrice `0008`
(comentario en `migrations/0009_platform_listing.sql:5-14`). `0010-0012`, `0014`, `0015` no
existen en el árbol. La numeración del runbook sigue los ficheros reales en `migrations/`.

---

## 1. GOVERNOR por host — el cuello mecanizado

**(a) QUÉ es.** El único choke point de rate ante CADA fetch. Un token-bucket continuo
**por host registrable**, asyncio-safe, compartido por todas las corrutinas del proceso: por
muchos workers que corran, el agregado contra un host no supera su bucket. Buckets
independientes (el throttling de AS24 jamás frena a Kia). Fichero: `pipeline/engine/governor.py`.

**(b) La cicatriz AS24.** Existe para hacer imposible *"138 dealers cayeron por throttling de
AS24 bajo carga 4x; la cosecha es el cuello"*. Cuatro workers paralelos, cada uno educado
(`time.sleep` por worker), pero el AGREGADO contra un host era un martillo porque nada los
coordinaba. Fix: **un** token-bucket por host, compartido (`governor.py:4-9`).

**(c) Las dos clases de rate (`_HOST_RATE_CLASSES`, `governor.py:84-141`).** El pacing se
clava a la CLASE del host, no a un global:

| Clase | rate | burst | min_spacing | jitter | Para qué host |
|---|---:|---:|---:|---:|---|
| **STEALTH** (default) | 0,7 req/s | 3,0 | 1,43 s | 0,25 s | HTML / stealth / WAF, techo NO medido. La cicatriz vive aquí: por debajo del ritmo que ganó el ban. NUNCA se sube sin evidencia. |
| **JSON_API** | 12 req/s | 24,0 | 0,03 s | 0,02 s | gateways JSON first-party (backends SPA/móvil que sirven a toda la base de usuarios). |

Constantes: `DEFAULT_RATE_PER_SEC=0.7`, `DEFAULT_BURST=3.0`, `DEFAULT_JITTER_S=0.25`
(`governor.py:51-54`); `JSON_API_RATE_PER_SEC=12.0`, `JSON_API_BURST=24.0`,
`JSON_API_MIN_SPACING_S=0.03`, `JSON_API_JITTER_S=0.02` (`governor.py:88-91`).

**Hosts JSON_API** (`governor.py:102-141`): `web.gw.coches.net`, `api.wallapop.com`,
`gql.autocasion.com`, `es.renew.auto`, `scs.audi.de`, `kiaokasion.net`,
`services.flexicar.es`, `api-carmarket.ayvens.com`.

**(d) Overrides per-host (la cicatriz codificada, `governor.py:312-364`).** STEALTH explícito
por debajo del default donde el techo es desconocido:

| Host | rate | burst | min_spacing | Razón |
|---|---:|---:|---:|---|
| `www.autoscout24.es` / `autoscout24.es` | 0,5 | 2,0 | 2,0 s | LA cicatriz: por debajo del ritmo que ganó el ban. |
| `www.coches.com` | 1,0 | 3,0 | 0,8 s | Imperva-fronted sirviendo a chrome131 (ventana decaying-open), superficie frágil. |
| `www.dasweltauto.es` | 1,0 | 3,0 | 0,8 s | AEM/Motorflash SSR tras muro TLS/UA suave (t1_soft). |
| `www.autocasion.com` | 4,0 | 8,0 | 0,25 s | CF MEDIDO permisivo; subido 2,0→4,0 monitoreado para drain PDP-per-car (135k). Reversible: ban→breaker→revertir. |
| `carmarket.ayvens.com` | 1,0 | 3,0 | 0,8 s | Origen HTML del SPA (ya NO es el data-path activo; el GraphQL `api-carmarket` lo es). |
| `www.ocasionplus.com` | 1,0 | 3,0 | 0,8 s | Next.js SSR, JSON-LD ItemList, t0_open pero superficie SSR. |

**Mecánica del bucket (`_Bucket`, `governor.py:161-208`):** refill continuo
(`min(burst, tokens + elapsed*rate)`); `acquire()` bloquea hasta token disponible **Y** que
haya pasado `min_spacing (+jitter)` desde el último grant; matemática bajo `asyncio.Lock` por
host (atómica). Empieza lleno (primer request inmediato). Token-bucket: no hay release; el
token se gasta en acquire y refilla con el tiempo (`slot()`, `governor.py:267-278`).

**Integración (`wrap_fetch_text`, `governor.py:280-299`):** devuelve un `fetch(url, **kw)`
async que deriva el host, `await acquire(host)`, y corre el curl_cffi síncrono en
`asyncio.to_thread` (event loop nunca bloqueado). Convenience proceso-wide:
`governor()` / `governed_fetch_text(engine=...)` (`governor.py:307-390`).

**(e) Resultado validado.** Estado vivo de la flota de fuentes (la cicatriz NO se repite — 0
breakers abiertos): `source_breaker` = **35 closed, 0 open**; `source_health` = **33 healthy,
2 degraded, 0 down**; `harvest_run` = **167 ok / 9 fail** (176 runs auditados). El
battle-test S-HEALTH cerró 25/25 PASS (cascada E2E, `SCOREBOARD.md`).

**(f) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "from pipeline.engine.governor import governor, host_of; g=governor(); \
import asyncio; print('host:', host_of('https://www.autoscout24.es/lst')); \
print('waited_s:', asyncio.run(g.acquire('www.autoscout24.es')))"
# Inspeccionar el estado de la flota (la prueba de la cicatriz no-repetida):
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute('SELECT state,count(*) FROM source_breaker GROUP BY state'); print('breaker:', c.fetchall()); \
c.execute('SELECT status,count(*) FROM source_health GROUP BY status'); print('health:', c.fetchall())"
```

---

## 2. FETCH — motor curl_cffi por tiers + escalada de navegador

**(a) QUÉ es.** El motor de fetch tiered que reemplaza el patrón urllib. Fichero:
`pipeline/engine/fetch.py`.

**(b) Tier-0 (lo construido, `fetch.py:1-21`).** `curl_cffi` con impersonación de navegador
completa: fingerprint TLS/JA3 + HTTP2 de Chrome real, **coherente a nivel de sesión** (una
`Session` → un fingerprint → un cookie jar) para que un drain paginado parezca un navegador,
no N requests sueltos. Perfil: `_IMPERSONATE = "chrome131"` (`fetch.py:31`). Por qué
reemplaza urllib: AS24 (y casi todas) cierran sobre el *fingerprint del cliente*, no el UA;
urllib emite un handshake TLS de Python que un WAF marca al instante; curl_cffi emite el de
Chrome (verificado vivo 2026-06-12, `fetch.py:9-12`).

**(c) Schema de request / headers (`fetch.py:33-47`).** `_DEFAULT_HEADERS`: UA Chrome 131,
`Accept` html/xhtml/avif/webp, `Accept-Language: es-ES,es;q=0.9,en;q=0.8`,
`Upgrade-Insecure-Requests: 1`, `Sec-Fetch-Dest/Mode/Site/User`. `fetch_text(url, *, tier=0,
headers=None)` mergea headers extra sobre el default.

**(d) Política de retry (`fetch.py:49-134`).** `_RETRYABLE = {429,500,502,503,504}`;
`_TIMEOUT=40`; `_MAX_RETRIES=4`; backoff exponencial `_BACKOFF_BASE=2.0` (2,4,8,16s) con
**full jitter** y honrando `Retry-After` (cap 30s); espera educada por sesión
`_POLITE_MIN=0.7`/`_POLITE_MAX=1.4`. **Falla en voz alta:** un status no-retryable
(403/404/410…) lanza `FetchError` — nunca devuelve un body de challenge/vacío en silencio
(el caller DEBE ver el fallo, `fetch.py:118-119`).

**(e) Escalada Tier-1 (el seam, NO construido en fetch.py — `fetch.py:14-20`, 94-98).**
Plataformas tras challenge activo (Akamai sensor, Cloudflare managed, GeeTest, DataDome)
necesitan navegador real. El seam es `fetch_text(..., tier=...)`: con `tier >= 1` este módulo
**lanza `NotImplementedError`** apuntando al path camoufox — el caller elige el motor
explícitamente y un target Tier-1 jamás cae en silencio al Tier-0 insuficiente.

**Doctrina de escalada (`docs/architecture/02-SCRAPING-ENGINE.md`):** T0 `curl_cffi`
optimista primero; escala **solo ante una respuesta de challenge tipada** (§272-273:
"optimism is free; escalation is on evidence"). Canónico del injector stealth:
`patchright` (default Scrapling) + `DynamicFetcher` (Playwright) para forma Chromium;
**camoufox** (pinned/vendored) para forma Firefox — el wrapper pip de camoufox está ~16 meses
stale, demota a opcional (§152-167). Mapa por WAF (§286): Cloudflare → T0 curl_cffi, on
challenge T1 `StealthyFetcher`.

**(f) Validado vivo.** El stock GRATIS de las 6 Tier-1 se cerró con Tier-0 curl_cffi
(coches.net VO, milanuncios, autocasion, motor.es por gateway JSON; ver `SCOREBOARD.md §1`).
La escalada de navegador se usó realmente para `coches.net` VN/km0/renting tras Imperva
(camoufox, +10.470 aristas) y para subastas Autorola+BCA (Playwright JS, 2.808 coches) —
ambos cerrados gratis, VAM 2 caminos (`SCOREBOARD.md §1`, veredictos ids 584-587).

**(g) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
# Tier-0 vivo (fingerprint Chrome):
"$PY" -c "from pipeline.engine.fetch import fetch_text; print(len(fetch_text('https://example.com')), 'chars')"
# Confirmar que el seam Tier-1 falla fuerte (no fallback silencioso):
"$PY" -c "from pipeline.engine.fetch import fetch_text; \
try: fetch_text('https://example.com', tier=1)
except NotImplementedError as e: print('Tier-1 seam OK:', str(e)[:60])"
```

---

## 3. GEO — jerarquía pais / provincia / comarca / ciudad + cdp_code inmutable

**(a) QUÉ es.** El backbone administrativo INE de España: `pais → PROVINCIA → COMARCA →
ciudad`. Migraciones `0001_geo.sql` (province/comarca/municipality) + `0018_comarca.sql`
(populate comarca + trigger).

**(b) Esquema (`migrations/0001_geo.sql`).**
- `geo_province`: PK `code CHAR(2)` (INE), `name`, `ccaa_code`, `ccaa_name`.
- `geo_comarca`: PK `id` IDENTITY, FK `province_code`, `name`, UNIQUE(province_code,name);
  `0018` añade `ine_code CHAR(2)` (comarca-agraria INE) + `source`, unique parcial
  `(province_code, ine_code) WHERE ine_code IS NOT NULL`.
- `geo_municipality`: PK `code CHAR(5)` (INE; provincia = izq 2), `name`, FK `province_code`,
  FK `comarca_id`, `lat`/`lon`. **Invariante CHECK:** `left(code,2) = province_code`
  (`municipality_province_prefix`).

**Geocoder/trigger (`0018_comarca.sql:27-40`):** `entity_set_comarca()` BEFORE INSERT/UPDATE
OF `municipality_code` ON `entity` — resuelve `comarca_id` desde `geo_municipality`
automáticamente, así toda entidad live-insertada hereda su comarca sin backfill.
Backfill histórico: `scripts/backfill_comarca.py`.

**(c) cdp_code — código inmutable (`services/api/codes.py`).** Determinista sobre la identidad
canónica: re-descubrir la misma entidad por otra fuente NO acuña un segundo código. Prioridad
de clave canónica (`canonical_key`, `codes.py:34-70`): `particular(platform:sellerId)` >
`domain` (host pelado; **una URL con path NUNCA es identidad** — evita el colapso Hyundai
175→48) > `CIF` > `name|municipality_code(|address)` > `name|province_code(|address)`.
Formato: `CDP-ES-{province2}-{8×Crockford-base32(sha256(key))}` (`codes.py:73-82`). Crockford
sin I,L,O,U (`codes.py:16`).

**(d) Resultado validado — veredicto `geo_hierarchy` id=581 (TRUSTWORTHY, divergencia 0).**
- Claim: *inventario de entidades agrupado por comarca reconcilia vía `entity.comarca_id`
  directo == vía `municipality→comarca` join; jerarquía sirve 52/52 prov*.
- Path A (directo `entity.comarca_id`) = **240.245** == Path B (vía muni) = **240.245**.
- `provinces_served = 52/52`, `comarcas_served = 322/323`, `municipalities_served = 4712/8132`.
- `municipality_with_comarca = 8130/8132 (99,98%)` — los 2 sin comarca son Ceuta/Melilla
  (ciudades autónomas sin comarca agraria; servidas aparte, sin ruido).
- **Vivo esta sesión:** grid confirmado `52 / 323 / 8132 / 8130`. (El valor de inventario
  por comarca subió con la ingesta; la metodología A==B se reconfirma viva en §6/API.)

**(e) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "from services.api.codes import cdp_code; \
print(cdp_code(province_code='28', domain='https://www.miconcesionario.es/'))"   # CDP-ES-28-...
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute(\"SELECT count(e.entity_ulid) FROM entity e JOIN geo_municipality m ON m.code=e.municipality_code JOIN geo_comarca co ON co.id=m.comarca_id WHERE e.comarca_id IS NOT NULL\"); \
print('pathB via_muni:', c.fetchone()[0]); \
c.execute('SELECT count(*) FROM entity WHERE comarca_id IS NOT NULL'); print('pathA direct:', c.fetchone()[0])"
```

---

## 4. VAM — la metodología de verificación adversarial multi-vía

**(a) QUÉ es.** El juez de "verificado": ≥2 caminos ortogonales por claim, con la **invariante
de landed-count** (el conteo que realmente vive en la DB DEBE estar entre los que coinciden;
nunca se enmascara pérdida de ingesta). Ledger: `verification_verdict`
(`migrations/0004_verification_health.sql:5-21`). Doctrina completa:
`docs/architecture/05-VERIFICATION-VAM.md`.

**(b) Esquema del ledger (`0004`, columnas verificadas vivas).** `id` BIGINT IDENTITY,
`subject_type`, `subject_key`, `claim`, `primary_value`, `primary_path`,
`verifier_paths JSONB`, `independent_values JSONB`, `divergence DOUBLE PRECISION`,
`verdict` CHECK `IN ('TRUSTWORTHY','REFUTED','UNVERIFIED')`, `evidence`, `created_at`.

**(c) Regla de quórum (05-VAM §2.2).** Dado caminos `P={p₁:v₁,…}` con `p₁` = landed truth
(conteo DB): `<2` caminos no-null → UNVERIFIED; mayoría limpia con `primary_agrees` y sin
rivales → TRUSTWORTHY; `divergence ≤ tolerancia` → TRUSTWORTHY; desacuerdo real → REFUTED.
Tres propiedades: (1) un camino que sobre-cuenta solo NO puede refutar; (2) `primary_agrees`
es la invariante de landed-count (la DB debe estar entre los ≥2 que coinciden); (3) `rivals`
detecta un split (no se promedian dos números en desacuerdo).

**(d) Estado vivo del ledger (verificado esta sesión).** **584 veredictos: 574 TRUSTWORTHY,
10 REFUTED.** Por subject_type: `entity_inventory` 371, `platform_slice` 135, `family_slice`
33, `source` 10, `platform_segment` 8, `platform_facet` 7, `group_vam` 5, `global_count` 4,
`platform_segment_slice` 4, `cross_platform_dedup_watermark` 3, `geo_hierarchy` 1,
`api_serves` 1, `dedup_watermark` 1, `platform_facet_mb_split` 1.

**(e) Veredictos `global_count` (TRUSTWORTHY, divergencia 0 — `count(*)` == suma de partición).**
| id | subject_key | claim | valor sellado | vivo esta sesión | deriva |
|---|---|---|---:|---:|---|
| 577 | `vehicle_total` | count* == Σ(available+reserved+gone) | 1.332.980 | 1.482.522 | ingesta viva (+149.542) |
| 578 | `entity_total` | count* == Σkind == Σrole | 309.148 | 367.831 | ingesta viva |
| 579 | `platform_listing_total` | count* == Σ status | 1.286.776 | 1.436.160 | ingesta viva |
| 580 | `vehicle_event_total` | count* == Σ event_type | 1.336.079 | 1.485.644 | ingesta viva |

> **Honestidad:** el valor de cada veredicto es el SELLADO en su barrido; el vivo es mayor por
> ingesta continua. La metodología (las 3 vías coinciden exactas) se sostiene: `CIERRE_FINAL.md`
> re-verificó a 07:04 UTC que tras drenar +3.567 vehículos el reconcile de 3 caminos sigue ==
> exacto y `available+gone==count*` sigue TRUE — la deriva absoluta es ingesta, NO descuadre.

**(f) REFUTED — los 10 (confesados, NO servidos).** `source`: `oem_mg`(55), `oem_byd`(56),
`oem_skoda`(57), `oem_hyundai`(59), `osm`(63) — count entidades ≠ declarado.
`entity_inventory` `CDP-ES-46-NM30P5P0`(5). `platform_slice` `CDP-ES-00-VMCZWW5N`(399, slice
AS24), `CDP-ES-00-XM91J1NZ`(548, coches.com 20.432 fantasmas cross-surface). `group_vam`
`long_tail_families`(544, no aditivo: 10.083 ya en otros grupos). `platform_segment`
`CDP-ES-00-XM91J1NZ:renting`(560). Estos son outcomes de PRIMERA CLASE (ruta la entidad FUERA
del set servido), no fallos del verificador.

**(g) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute('SELECT verdict,count(*) FROM verification_verdict GROUP BY verdict'); print(c.fetchall()); \
c.execute(\"SELECT id,subject_key,primary_value,independent_values,divergence FROM verification_verdict WHERE subject_type='global_count' ORDER BY id\"); \
[print(r) for r in c.fetchall()]"
```

---

## 5. S-HEALTH — watchdog, alerta de origen exacto, breaker, auto-repair

**(a) QUÉ es.** El cableado que hace cierto *"si una fuente falla, salta una alerta con el
ORIGEN EXACTO, se auto-repara, y Cardeep nunca se cae"*. Fichero: `pipeline/ops/health.py`.
Substrato durable: `migrations/0013_resilience.sql` (+ las tablas `0004` `source_health`,
`alert`).

**(b) Esquema (`0013` + `0004`).**
- `source_breaker` (`0013:19-26`): PK `source_key`, `state` CHECK `IN
  ('closed','open','half_open')`, `consecutive_fails`, `opened_at`, `cooldown_until` (DEBE
  sobrevivir a un restart, §9.4).
- `harvest_run` (`0013:30-39`): `id` IDENTITY, `source_key`, `started_at`, `finished_at`,
  `ok BOOLEAN`, `rows`, `error`, `http_status` — la auditoría que faltó al incidente 138.
- `repair_attempt` (`0013:45-54`): `source_key`, `detected_reason`, `action` CHECK `IN
  ('refingerprint','escalate_tier','re_receta','quarantine','escalate_owner')`,
  `succeeded BOOLEAN`, `created_at`.
- `source_health` (`0004:24-31` + `0013:61-62`): `consecutive_fails`, `status` CHECK `IN
  ('healthy','degraded','down','unknown')`, + `is_tier1`, + `tuning JSONB`.
- `alert` (`0004:34-43`): `origin`, `severity` CHECK `IN ('info','warning','critical')`,
  `message`, `payload JSONB`, `resolved_at`.

**(c) La máquina (`health.py`).**
- `record_run(...)` (`health.py:76-192`): ÚNICO escritor de `source_health` + `source_breaker`.
  Escribe `harvest_run`, lee-modifica-escribe `source_health` bajo `FOR UPDATE` (single writer,
  sin lost-update), trip del breaker a OPEN tras `BREAKER_TRIP_AT=3` fallos consecutivos con
  cooldown exponencial (`min(900 * 2^depth, 86400)`). Umbrales: `DEGRADE_AT=1`, `DOWN_AT=3`,
  `BREAKER_COOLDOWN_SEC=900` (`health.py:38-42`), tunables por `source_health.tuning`.
- `build_origin(source_key, phase, cdp_code)` (`health.py:195-198`): la clave canónica
  `<source_key>:<phase>[:<cdp_code>]` — el "origen exacto" machine-readable.
- `fire_alert(...)` (`health.py:201-230`): escribe `alert` con origen exacto + mensaje
  específico; **dedup**: si ya existe alerta sin resolver para ese origen, actualiza payload en
  vez de insertar (138 dealers throttling = UNA alerta AS24, no 138 filas).
- `classify_failure(reason, http_status)` (`health.py:246-278`): determinista, €0. 401/403/
  challenge → `refingerprint` (o `escalate_tier` si Akamai/DataDome/PerimeterX/sensor); 429/ban
  → `quarantine`; null/drift/schema/selector → `re_receta`; desconocido → `escalate_owner`.
- `auto_repair(...)` (`health.py:287-346`): clasifica, loguea `repair_attempt`, dispara
  alerta de origen exacto, devuelve la acción. `quarantine` y `escalate_owner` son **efectivos
  ya** (€0). `refingerprint`/`escalate_tier`/`re_receta` están **scaffolded tras P10 spend-gate**
  (`_SPEND_GATED_ACTIONS`, `health.py:284`): el LAZO (classify+audit+alerta+breaker) corre real;
  solo el efecto con gasto se difiere, marcado `succeeded=FALSE`, `repair_outcome='pending'`.
- `is_open(conn, source_key)` (`health.py:349-372`): gate que el harvest llama ANTES de correr.
  OPEN → skip graceful ("no se cae"). Pasado `cooldown_until` → `half_open` (un probe canario).

**(d) Resultado validado.** Estado vivo: `source_breaker` **35 closed / 0 open**;
`source_health` **33 healthy / 2 degraded / 0 down**; `harvest_run` **167 ok / 9 fail**.
`repair_attempt` **9**: `escalate_owner` 6 (succeeded=True), `quarantine` 1 (succeeded=True),
`refingerprint` 2 (succeeded=False, P10-pending — coherente con el spend-gate). `alert`: 4
critical + 2 warning abiertas. **Battle-test:** 25/25 PASS, cascada E2E
`record→breaker→alerta-origen→auto_repair→recovery`, 0 residuo TEST (`SCOREBOARD.md §1`).

**(e) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute('SELECT status,count(*) FROM source_health GROUP BY status'); print('health:', c.fetchall()); \
c.execute('SELECT action,succeeded,count(*) FROM repair_attempt GROUP BY action,succeeded'); print('repairs:', c.fetchall()); \
c.execute('SELECT ok,count(*) FROM harvest_run GROUP BY ok'); print('runs:', c.fetchall())"
# Origen exacto (función pura):
"$PY" -c "from pipeline.ops.health import build_origin, classify_failure; \
print(build_origin('as24','scrape','CDP-ES-28-XXXXXXXX')); \
print(classify_failure('HTTP 403 datadome challenge', http_status=403))"
```

---

## 6. LA API — endpoints, envelope, y arranque confirmado VIVO

**(a) QUÉ es.** API live FastAPI sobre el backbone PostgreSQL. Fichero:
`services/api/main.py`. **Envelope consistente:** `{ok, data, error, meta}`
(`main.py:33-38`). DSN por env `CARDEEP_DSN` (default = la DB del runbook). Pool asyncpg
`min_size=1, max_size=8` (`main.py:23`).

**(b) Confirmado que ARRANCA y SIRVE (esta sesión).** Levantado
`uvicorn services.api.main:app --port 8096`, respondió `/health` `ok:true`. Endpoints
(`main.py`):

| Método | Endpoint | Qué sirve |
|---|---|---|
| GET | `/health` | counts vivos (entities, vehicles_available, events, provinces, municipalities) |
| GET | `/entities/{cdp_code}` | la entidad + `available_inventory` |
| GET | `/entities/{cdp_code}/inventory` | vehículos available (deep_link, make…price…last_seen) |
| GET | `/entities/{cdp_code}/delta` | `vehicle_event` (?since=ISO), limit 500 sin since |
| GET | `/geo/{province_code}/entities` | entidades de la provincia |
| GET | `/geo/{province_code}/tree` | árbol pais→PROVINCIA→COMARCA→ciudad, 0 ruido NULL-geo |
| GET | `/geo/completeness` | reporte nacional de completitud geo (entity + vehicle) |
| GET | `/platforms/{cdp_code}/inventory` | coches de una plataforma vía `platform_listing` + dealer attribution |
| GET | `/vehicles/{vehicle_ulid}/platforms` | plataformas de un coche + su dealer dueño singular |

Guard: `/platforms/{cdp_code}/inventory` devuelve **400** si la entidad no es `kind=plataforma`
(`main.py:218-219`).

**(c) Resultado validado — veredicto `api_serves` id=583 (TRUSTWORTHY, divergencia 0).**
- Claim: *uvicorn sirve entity/inventory/delta/geo-tree(comarca-sort)/completeness/
  platform-inventory/vehicle-platforms con `{ok,data,error,meta}`; el geo tree reconcilia con
  DB directa*.
- Sellado: `/geo/28/tree` `entities_geo_clean = 36431` (API) == 36431 (DB), top comarca
  `Area Metropolitana de Madrid = 26213`, `geo_completeness full_pct = 77.71`.
- **Reconciliado VIVO esta sesión (2ª vía ortogonal):** `/geo/28/tree` API
  `entities_geo_clean = 43303` == DB Path B (`entity JOIN geo_municipality JOIN geo_comarca`)
  **= 43303 exacto**; top comarca API `Area Metropolitana de Madrid = 30385` == DB **= 30385
  exacto**; `full_pct` entities **78,14**. La deriva (36431→43303, 77,71→78,14) es ingesta
  viva; la **reconciliación A==B se sostiene exacta viva**.

**(d) CLI reproducir (arranque + reconcile).**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
CARDEEP_DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep" \
  "$PY" -m uvicorn services.api.main:app --host 127.0.0.1 --port 8096 &
# probe (envelope + reconcile geo tree):
"$PY" -c "import urllib.request,json; \
t=json.load(urllib.request.urlopen('http://127.0.0.1:8096/geo/28/tree')); \
print('envelope:', list(t.keys()), 'clean:', t['data']['entities_geo_clean'])"
```

---

## 7. EL ESQUEMA — migraciones 0001-0019, enums, tablas clave

**(a) `entity_kind` enum (`0005:12-18` + `0017:21`).** Valores vivos:
`concesionario_oficial, agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta,
importador, oem_vo_portal, plataforma, cadena (DEPRECATED read-only), particular`. Distribución
viva (`GROUP BY kind`): `particular 326.060`, `compraventa 31.510`, `garaje 7.220`,
`concesionario_oficial 1.618`, `desguace 1.299`, `subasta 94`, `oem_vo_portal 14`,
`plataforma 10`, `cadena 4`, `rent_a_car_vo 3`. **`particular`** (`0017`): vendedor privado como
entidad de 1ª clase — donde la fuente expone seller-id estable (milanuncios authorId, wallapop
user_id) → 1 entidad por humano; donde anonimiza (coches.net) → 1 bucket por provincia. NUNCA
se fabrica identidad que la fuente oculta.

**(b) Multi-eje de clasificación (`0016_tiering_groups.sql`).**
- `defense_tier` enum: `t0_open` (sin muro: JSON API/sitemap/registro), `t1_soft` (WAF
  sirviendo a curl_cffi), `t2_js_challenge` (navegador stealth para cookie), `t3_hard_sensor`
  (Akamai/Kasada/PX — stealth-Chromium gratis aún lo crackea), `t4_spend_gated` (solo
  residencial/sensor de pago, tras probar muertos todos los vectores gratis). Vivo:
  `t0_open 196`, `t1_soft 19`, `t2_js_challenge 1` (el resto NULL, no clasificado).
- `source_group` enum (11 valores): `marketplace_generalist, marketplace_motor, oem_vo_portal,
  oem_dealer_network, chain, rentacar_vo, official_registry, association, directory,
  desguace_network, long_tail_web`. Vivo (top): `directory 9.953`, `oem_vo_portal 5.769`,
  `oem_dealer_network 1.362`, `marketplace_motor 1.312`, `desguace_network 1.292`, `chain 189`.
- `entity_role` enum: `platform, dealer_network, chain, standalone_pos, registry, directory`.

**(c) `platform_listing` — la arista dual-membership (`0009` + `0019`).** PK `(vehicle_ulid,
platform_entity_ulid)` — una arista por (coche, plataforma). `vehicle.entity_ulid` queda el
DEALER vendedor (propiedad singular); la membership de plataforma es ESTA arista (plural,
0..M). Columnas: `listing_url`, `listing_ref`, `platform_price`, `listing_fingerprint`
(hash cross-platform same-car), `status listing_status`, `first/last_seen`, `removed_at`.
`0019` añade `segment` CHECK `IN ('used','new','km0','renting')` DEFAULT `'used'` — el segmento
es propiedad de la arista (coches.net lista el mismo catálogo bajo varios `offerTypeIds`).

**(d) `comarca`.** Ver §3 (`0001` define, `0018` puebla con `ine_code` + trigger
`entity_set_comarca`). 323 comarcas vivas, todas con `ine_code`; 8.130/8.132 muni con comarca.

**(e) Otras tablas.** `vehicle`/`vehicle_event` (`0003`): snapshot + delta append-only, enum
`vehicle_event_type` (`0005:56-61`) `NEW,GONE,REAPPEARED,PRICE_CHANGE,PHOTO_CHANGE,KM_CHANGE,
STATUS_CHANGE,SPEC_CHANGE`. `entity_source`/`entity_alias` (`0002`): provenance
capture-recapture + dedup. `organization` (`0007`): capa cadena/grupo (**vacía viva, 0 filas**).
`platform_meta` + vista `platform` (`0006`). Trigger compartido `cardeep_block_mutation()`
(`0005:71-76`) prohíbe UPDATE/DELETE en logs append-only.

**(f) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute('SELECT version FROM schema_migrations ORDER BY version'); print('migs:', [r[0] for r in c.fetchall()]); \
c.execute(\"SELECT enumlabel FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid WHERE t.typname='entity_kind' ORDER BY e.enumsortorder\"); \
print('entity_kind:', [r[0] for r in c.fetchall()])"
```

---

## 8. Watermark de dedup cross-platform

**(a) QUÉ es.** La marca de agua que mide (NO mergea) el sobre-conteo de "el mismo coche en
varias plataformas". Dos veredictos distintos, ambos TRUSTWORTHY.

**(b) `dedup_watermark` id=582 (TRUSTWORTHY, divergencia 0) — partición 1:1 limpia.**
- Claim: *ningún `vehicle_ulid` mapea a >1 `platform_entity_ulid` (partición 1:1 limpia; Path A
  edges == Path B distinct-vehicle en las 6 Tier-1)*.
- `vehicles_on_multiple_platform_entities = 0`, `excess_edges = 0`. La watermark se sostiene:
  cada coche cuelga de UNA plataforma-entidad, sin doble-membership entre plataformas.

**(c) `cross_platform_dedup_watermark` ids 556 / 559 / 574 (TRUSTWORTHY) — cota inferior del
sobre-conteo SAME-CAR.**
- Claim: *cota INFERIOR del sobre-conteo cross-platform sobre el piso fuzzy estricto (exacto
  make+model+year+km+price+province); auto-merge por clave fuerte limitado a VIN-exacto
  (03-DATA-MODEL §6.1, `photo_hash` sin poblar)*.
- Verificado por DOS caminos ortogonales: `excess_sql_groupby` vs `excess_python_grouping`.
- id=556: SQL 132.016 / Python 132.043 (div 0,0002). id=559: 132.157 / 132.178. **id=574
  (el más reciente): SQL 134.007 / Python 134.019 (div 0,00009)**.
- **MEASURE-ONLY, NO merge por defecto:** ≈134.027 filas excedentes (14,36%, cota inferior
  estricta). El merge cross-seller está fuera de v1 (riesgo de over-merge; `photo_hash` aún
  sin poblar) — confesado, no fingido (`SCOREBOARD.md §2`, 05-VAM §4.4/§10.3).

**(d) CLI reproducir.**
```bash
PY="C:/Users/elias/AppData/Local/Programs/Python/Python311/python"
"$PY" -c "import psycopg2; c=psycopg2.connect('postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep').cursor(); \
c.execute('SELECT count(*) FROM (SELECT vehicle_ulid FROM platform_listing GROUP BY vehicle_ulid HAVING count(DISTINCT platform_entity_ulid)>1) x'); \
print('vehicles_multi_platform (debe ser 0):', c.fetchone()[0])"
```

---

## NO validado (FUERA del runbook)

Declarado explícito, sin maquillaje. NO entra como "funciona":

1. **`organization` / `group_vam` VAM muerto.** Tabla `organization` **vacía (0 filas vivas)**,
   `entity.org_id` NULL. La capa cadena/grupo (`0007`) existe en esquema pero no poblada.
2. **`source` veredictos REFUTED (5):** `oem_mg`(55), `oem_byd`(56), `oem_skoda`(57),
   `oem_hyundai`(59), `osm`(63) — conteo de entidades ≠ declarado. NO servidos.
3. **`coches.com` doble-conteo cross-surface (REFUTED id=548):** 20.432 fantasmas; verdad =
   91.066 únicos. Clave de identidad = URL en vez de listing-id. Fix dedup pendiente.
4. **`long_tail_families` no aditivo (REFUTED id=544):** 10.083 ya en otros grupos;
   `family_*` es clasificador CMS, no partición disjunta.
5. **auto_repair efectos caros (P10-scaffold):** `refingerprint`/`escalate_tier`/`re_receta`
   con `succeeded=FALSE`, `repair_outcome='pending'`, `_SPEND_GATED_ACTIONS`. El LAZO corre
   real (€0); el EFECTO con gasto espera autorización P10. (El SCAFFOLD está marcado en código,
   `health.py:325-331` — es la única excepción declarada, no un stub oculto.)
6. **Escalada Tier-1 en `fetch.py`:** el seam lanza `NotImplementedError` (por diseño — no
   fallback silencioso). El motor camoufox/Playwright vive FUERA de `fetch.py` (se usó vía
   conectores `coches_net_segments.py` / `group_subastas_wholesale.py`, validado en
   `SCOREBOARD.md`), pero `fetch.py` por sí solo NO sirve Tier-1.
7. **`platform.listing_counter` NULL en las 24 plataformas** · **API sin endpoint propio
   `oem_vo_portal`** (HTTP 400 guard). Defectos de calidad flagged, sin spend.
8. **Watermark cross-platform ≈134k excedentes:** MEASURE-ONLY. NO se ha ejecutado merge; es
   una medición validada, no una capacidad de deduplicación activa.

---

> **Evidencia de cada unidad del runbook:** §1 governor (33 healthy/0 open vivo + battle-test
> 25/25); §2 fetch (Tier-0 vivo + seam Tier-1 falla fuerte, verificado); §3 geo (veredicto
> id=581); §4 VAM (ledger 574 TRUSTWORTHY + global_count ids 577-580); §5 S-HEALTH (estado
> vivo + repair_attempt coherente con spend-gate); §6 API (arrancada viva + reconcile A==B
> exacto + veredicto id=583); §7 esquema (`schema_migrations` 0001-0019 + enums vivos); §8
> watermark (ids 582 + 574). Todos los conteos cruzados contra la DB viva esta sesión, con la
> deriva de ingesta declarada donde el veredicto va por detrás del vivo.
