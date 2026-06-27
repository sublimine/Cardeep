# Etapa 9 · Orquestar/Observar — Biblia
> Estado adversarial: **NEEDS_REWORK** (inquisidor Wave 1: `holds=false`). Fuente: Wave 1 (path:linea verificado contra código). Stack vivo CAÍDO → toda cifra de DB es **punto-en-el-tiempo**, no censo. Las cifras de líneas/código son [VERIFIED] leídas hoy.

> **Lectura honesta de cabecera.** Hoy el orquestador corre **byte-idéntico para ES** y es sólido para UN inquilino. Pero el inquisidor probó que **NINGÚN país #2 puede onboardarse sin construir antes los cambios de §Diseño**: el `country_code` se enhebró en el ESQUEMA (0052/0053) y en el prefijo `cdp_code`, **no** en la lógica de orquestación. Locks, due-selection, watchdog de silencio, registries y dispatch son **country-BLIND**. Esta biblia **no transcribe el diseño optimista como hecho**: separa lo `[VERIFIED]` (corre hoy) de lo `[DISEÑO]` (additivo, €0, espejo de 0052, **aún no en código**) y marca cada **OPEN ITEM con su causa**.
>
> **Mapa de navegación (v2 PROFUNDO).** Sobre la estructura v1 (Misión → Lo que existe → Motor/Pack → Costuras → Diseño → Onboarding → Sellado → Veredicto → Mejoras → Riesgos), este capítulo añade la § [**Sub-proyectos institucionales (360 por faceta)**](#sub-proyectos-institucionales-360-por-faceta): **21 átomos** de la orquestación (set COMPLETO: 12 del núcleo + 9 antes citados como punteros), cada uno un proyecto 360° con índice navegable, **anatomía fija de 7 partes** ((a) verificación · (b) mecanismo · (c) costura · (d) fix · (e) adversarial · (f) sellado · (g) herramienta NEXT-LEVEL €0). La cabecera adversarial (NEEDS_REWORK) y el §Veredicto por clusters siguen siendo la verdad de mando; los sub-proyectos son su **drill-down átomo a átomo**.

---

## Misión
Mantener el motor **vivo, fresco y observable** sin intervención humana: un productor único por host que selecciona qué fuentes tocar (cadencia), las lanza en serie sin auto-DDoS, registra cada corrida, corta fuentes rotas (circuit breaker), detecta las que enmudecen (watchdog de silencio), expone un lease observable para distinguir un holder sano de uno muerto, y dispara/resuelve alertas con **origen exacto**. La etapa 9 es el daemon que orquesta las etapas 1–8 y avisa cuando algo cae — y, para el motor genérico, debe hacerlo **por país** sin reescribir la maquinaria.

---

## Lo que existe HOY (verificado)
- **Scheduler de harvest durable:** APScheduler `BlockingScheduler(jobstores=SQLAlchemyJobStore, timezone="UTC")` con persistencia crash-safe de jobs en PG. [VERIFIED `pipeline/ops/scheduler.py:933`, jobstore `:931`]
- **Lock single-producer de host** `0x43415244` (1128354372, ASCII `CARD`): se adquiere vía `acquire_with_stale_retry`; un segundo proceso hace `SystemExit` (cicatriz AS24: nunca dos gobernadores). El lock es una **constante de módulo fija, no un parámetro**. [VERIFIED `scheduler.py:913`, acquire `:919`, SystemExit `:921-924`]
- **8 cadence jobs** registrados: `heartbeat_tick` [VERIFIED `:938`], `silence_watchdog` [VERIFIED `:953`], `inquisition_cadence` `:968`, `inquisition_prosecute` `:983` (+30 min stagger), `gestionador_detect` `:1002`, `canonical_key_backfill` `:1017`, `lease_heartbeat` `:1032`, `product_stats_refresh` `:1048`. [VERIFIED `scheduler.py:938-1048` per W1]
- **REGISTRY de harvest:** ~50 `SourceEntry` **ES hardcodeadas** (`source_key -> module + extra_args`), Tier1 24h / OEM 168h / families 720h. Dict literal a nivel de módulo. [VERIFIED `scheduler.py:150-326` (_build_registry), `REGISTRY` `:330`]
- **Due-selection determinista, country-BLIND:** `now()-COALESCE(last_ok,last_fail,'1970')>=harvest_interval_hours`, orden más-vencido-primero, skip si breaker `consecutive_fails>=3`. **Cero filtro de país** en el `SELECT ... FROM source_health`. [VERIFIED `scheduler.py:344-384`; SQL sin `country_code` `:357-371`; `BREAKER_TRIP_AT=3`]
- **Circuit breaker** con histéresis + cooldown exponencial (cap 24h), `record_run` único escritor de `source_health`/`source_breaker`, `is_open` consultado pre-run. Clave = `source_key` (global). [VERIFIED `pipeline/ops/health.py:84` record_run; W1 `:215-466`]
- **Red de seguridad crash-before-record_run:** graba el fallo sólo si no apareció `harvest_run` nuevo (idempotente por high-water id). El `heartbeat_tick` **salta** todo `source_key not in REGISTRY`. [VERIFIED `scheduler.py:544-549` skip-unmapped, `:550-553` high-water+crash-net]
- **Discovery daemon independiente:** `BlockingScheduler` propio, lock `0x43415244+1` (1128354373), 5 vectores ES (`borme_cnae`, `collapse_invisible`, `overture`, `graph_recursive`, `dork_municipal`); `dork_municipal` AUTO-gate por `requires_env=("CARDEEP_SEARXNG_URL",)`. [VERIFIED `pipeline/discover_schedule.py:50` lock, `:65-84` DISCOVERY_REGISTRY, gate `:83`]
- **Lease/heartbeat observable** (mig 0054 `scheduler_lease`): TTL 6 min = 3× heartbeat 2 min; `is_lease_stale` puro; `acquire_with_stale_retry` reintenta 1 vez si stale. Best-effort/inerte sin 0054. [VERIFIED `pipeline/ops/lock_heartbeat.py` `:170-338`; `migrations/0054_scheduler_heartbeat.sql`]
- **config_guard fail-fast prod:** rechaza DSN con credencial dev `cardeep_dev_only` o API-key ausente **sólo si** `CARDEEP_ENV=prod`; no-op byte-idéntico en dev/test. [VERIFIED `pipeline/config_guard.py` require_prod_secrets; cableado `scheduler.py:899-903`, `discover_schedule.py:246`]
- **Alerta origen-exacto + dedup + resolución:** `build_origin = "<source_key>:<phase>[:cdp]"`; `fire_alert`/`fire_silence_alert_sync` hacen UPDATE-si-abierta / INSERT-si-no; `resolve_alerts` cierra por origin. [VERIFIED `silence_watchdog.py:113-167` fire dedup; `health.py:169-173` resolve scoped a fase]
- **Watchdog de silencio:** detecta fuentes calladas (`now()-COALESCE(last_ok,last_fail) > 2× interval`), invisibles al S-HEALTH pasivo; dispara 1 alerta dedup `"<key>:silence"`. Scan **global, sin filtro de país**. [VERIFIED `silence_watchdog.py:57-83` find_silent_sources, `:127` origin, `SILENCE_MULTIPLIER=2`]
- **BUG ZOMBIE (raíz, verificado):** las alertas `":silence"` **NUNCA se resuelven**. `record_run` en éxito resuelve sólo `build_origin(source_key, phase)` con `phase ∈ {scrape, discover}`; ningún llamador de `resolve_alerts` cubre la fase `silence`. Una fuente que se recupera conserva su alerta de silencio abierta para siempre. [VERIFIED `health.py:172-173` resuelve sólo fase de la corrida; `silence_watchdog.py:127` la dispara; ningún resolver de `:silence` en `pipeline/`]
- **Esquema de orquestación SIN dimensión país:** `source_health` PK = `source_key` solo; `alert.origin` TEXT libre; `harvest_run`/`source_breaker`/`scheduler_lease` sin `country_code`. [VERIFIED `migrations/0004_verification_health.sql:25` (`source_key TEXT PRIMARY KEY`), `:36` (`origin TEXT`)]
- **Persistencia real = Windows 11 vía NSSM**, documentada como **prosa inline** en `docs/DEPLOY-DURABLE-DAEMONS.md §3` (NSSM AppExit Default Restart / Task Scheduler ONSTART, sin ampersand). **NO existe artefacto commiteado** `ops/windows/*.ps1`. Las units systemd existen pero asumen Linux `/opt/cardeep`. [VERIFIED ausencia de `ops/windows/`; `ops/systemd/cardeep-harvest.service` Restart=always/SIGTERM]

---

## Motor (invariante, reusado byte-idéntico por país)
Lo que es **genuinamente country-agnóstico hoy** y se reusa sin tocar una línea:

| Mecanismo | Por qué es invariante | Evidencia |
|---|---|---|
| Arnés APScheduler (BlockingScheduler + SQLAlchemyJobStore, `max_instances=1`, `coalesce`, `misfire_grace`) | persistencia crash-safe de cadencia; idéntica en cualquier país | `scheduler.py:930-948` [VERIFIED] |
| Circuit breaker (trip a 3, cooldown exp. cap 24h, `is_open` pre-run, half-open 1 sonda) | la mecánica de salud está keyed en `source_key`; agnóstica al país | `health.py:84-466` [VERIFIED W1] |
| Red de crash con idempotencia por high-water `harvest_run` id | universal; no depende de qué fuente ni de qué país | `scheduler.py:550-553` [VERIFIED] |
| Gramática de alerta (`build_origin`/`fire_*`/`resolve_alerts`, dedup por fase) | la **fase**, no el país, scopea el origin y la resolución | `silence_watchdog.py:113-167`, `health.py:169-173` [VERIFIED] |
| `config_guard` fail-fast (`require_prod_secrets`/`assert_safe_dsn`) | valida DSN/API-key por env, sin referencia a país | `config_guard.py`, cableado `scheduler.py:899` [VERIFIED] |
| Arnés best-effort por cadence-job (try/except que loguea y nunca mata al productor) | patrón reutilizable; aísla un job roto del resto | `scheduler.py` job-wrappers [VERIFIED W1] |
| Forma-de-proceso del supervisor (systemd `Restart=always`+SIGTERM / NSSM AppExit Default Restart) | el **single-instance lo garantiza SIEMPRE el advisory lock en PG**, no el supervisor | `DEPLOY-DURABLE-DAEMONS.md §0`; `ops/systemd/*` [VERIFIED] |

**Mecanismos que el diseño llamaba "invariantes" pero son country-BLIND (la espina dorsal de la rotura — NO se presentan como limpios):**

| Mecanismo | Reclamo del diseño | Realidad verificada |
|---|---|---|
| Advisory lock single-producer | "el `lock_key` es **PARÁMETRO**, idéntico en cualquier país" | **FALSO**: es constante de módulo fija `0x43415244` (`scheduler.py:913`) / `+1` (`discover_schedule.py:50`). En la DB multi-tenant compartida (0052/0053), sólo **UN país** puede cosechar a la vez → rotura DE-CRITICAL. |
| Due-selection | "opera sobre `source_health`, ciego al país" (como virtud) | El "ciego al país" **es** el defecto: scan global sin predicado → rotura FR-CRITICAL. `scheduler.py:357-371` [VERIFIED] |
| Watchdog de silencio | "country-agnóstico" | Scan global sobre `source_health`; con N inquilinos dispara alertas cruzadas → rotura FR-CRITICAL. `silence_watchdog.py:68-83` [VERIFIED] |

> Regla de honestidad (ANTI-DRIFT §2): un mecanismo country-BLIND **se reusa** pero **no está blindado para multi-país**. Su resolución vive en §Diseño y §Veredicto; aquí queda marcado como rotura, no como invariante limpio.

---

## Pack por país (lo que cada país aporta para esta etapa)
1. **Registry de harvest del país:** dict `source_key -> SourceEntry(module, extra_args)` de los conectores de ESE país (ES: ~50 entradas `autocasion_facet`/`coches_net_facet`/… `scheduler.py:156-325`; DE: `mobile_de_wholesale`, etc.).
2. **Registry de vectores de descubrimiento del país:** qué vectores existen + cadencia + gate de coste. ES declara `borme_cnae` (registro mercantil ES, 24h) y `dork_municipal` (barrido 8.132 municipios ES, 2160h) — **intrínsecamente nacionales** (`discover_schedule.py:65-84`).
3. **`pipeline/discover.py` ADAPTERS:** el mapa `vector -> adapter` es una **segunda superficie ES-inlined** (no sólo el registry de cadencia) que también debe empaquetarse. [VERIFIED `pipeline/discover.py` ADAPTERS, W1 `:48-74`]
4. **Filas semilla de `source_health`:** `harvest_interval_hours` (cadencia) + `is_tier1` (escalado de severidad) por fuente, sembradas por una migración de onboarding (patrón ES = `0039`), **con la aritmética watchdog-safe del centinela** (ver §Costuras).
5. **Designación Tier-1 por fuente** (`source_health.is_tier1`): hoy boolean → `critical` vs `warning` en silencio/alertas.
6. **Cadencias nacionales** de los vectores (BORME diario ES vs Handelsregister DE) y sus gates de coste (SearXNG, límites).
7. **(Sólo si aislamiento por host/VPS)** el namespace de `lock_key` de los productores del país. *(El inquisidor corrige: para la topología de DB compartida esto NO es opcional — ver §Veredicto, cluster B.)*

---

## Costuras ES-hardcoded -> fix

| Location | Issue | Fix |
|---|---|---|
| `silence_watchdog.py:174` `run_silence_watchdog` (+ ausencia de resolución); contraste `health.py:173` | **BUG ZOMBIE raíz:** el watchdog DISPARA `"<key>:silence"` pero ningún camino las RESUELVE. `record_run` resuelve sólo `scrape|discover`. Una fuente recuperada conserva su alerta para siempre (~7 zombies [ASSUMED, no consultado a DB]). No es deuda de país pero rompe la observabilidad del motor en **todo** país. | Añadir `resolve_recovered_silence_alerts(conn)->int`: un `UPDATE alert SET resolved_at=now() WHERE resolved_at IS NULL AND origin LIKE '%:silence' AND NOT EXISTS(predicado-de-silencio idéntico al de find_silent_sources)`. Llamarlo dentro de `run_silence_watchdog` cada ciclo (resolver-recuperadas → disparar-nuevas). El `NOT EXISTS` **debe espejar EXACTO** el 2× interval o flapea. Defensa en profundidad: en `record_run` éxito también `resolve_alerts(build_origin(key,'silence'))`. Test: recuperada→resuelta, aún-callada→NO-resuelta. €0, additivo, reversible. |
| `scheduler.py:150-330` `_build_registry` + `REGISTRY` | El REGISTRY MEZCLA motor (due-selection, single-producer) con country-pack (~50 entradas ES). País #2 no puede cargar otro pack sin **editar el motor**. | Extraer a proveedor por país: `pipeline/ops/registry/__init__.py` con `get_harvest_registry(country)->dict[str,SourceEntry]` y `active_countries()`; mover las ~50 entradas ES **verbatim** a `registry/es.py`; el scheduler importa el proveedor, no el literal. Con `active_countries()==['ES']` → byte-idéntico. |
| `discover_schedule.py:65-84` `DISCOVERY_REGISTRY` | Misma costura: 5 vectores ES (`borme_cnae`, `dork_municipal`) hardcodeados a módulo-nivel. | `get_discovery_registry(country)->dict[str,DiscoveryJob]`; pack ES en `registry/es.py`; DE declara su equivalente. El daemon carga el pack del/los país(es) activo(s). |
| `migrations/0004` (`source_health`), `0013` (`harvest_run`/`source_breaker`), `0054` (`scheduler_lease`) | Ninguna tabla de orquestación lleva `country_code` → namespace **GLOBAL** de `source_key`. No se puede scopear un productor a un país; riesgo de colisión de `source_key` entre países. | Migración additiva espejo de 0052: `ALTER TABLE source_health ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'`. Due-selection y silencio añaden `WHERE country_code = ANY($countries)` **OPCIONAL**. Con DEFAULT 'ES' y sin env → byte-idéntico. `source_key` sigue siendo identidad global (YAGNI, como 0052 difirió el swap de PK geo a 0053). |
| `scheduler.py:913` (`0x43415244`) y `discover_schedule.py:50` (`+1`) | Dos advisory locks **singleton de host literales**. Para varios países en el mismo host/DB con un productor por país harían falta locks por `(país,rol)`. | Por defecto: UN productor de host que drena en serie las fuentes due de TODOS los países (sin riesgo AS24: un subproceso a la vez). Para aislamiento VPS-país: `lock_key(role,country)=BASE+role_offset+country_ordinal*OFFSET`. `lock_heartbeat` ya recibe `lock_key` como parámetro → cambio sólo en el call-site; `scheduler_lease.holder = "harvest:ES"`. |
| `docs/DEPLOY-DURABLE-DAEMONS.md §3` (NSSM/Task Scheduler) vs `ops/` (sin `ops/windows`) | Persistencia REAL hoy (host Windows 11) = NSSM, pero **NO hay artefacto commiteado**: sólo prosa inline. Units systemd existen pero asumen Linux. Deriva doc-vs-realidad en el único host real. | Commitear `ops/windows/install-cardeep-services.ps1` idempotente (sin ampersand, NSSM AppExit Default Restart, `AppEnvironmentExtra`) parametrizado por `CARDEEP_COUNTRY`. El single-instance lo sigue garantizando el advisory lock. |
| `scheduler.py:1002/1017/1048` (`gestionador_detect`, `canonical_key_backfill`, `product_stats_refresh`) | **[ASSUMED]** Estos cadence jobs agregan sobre tablas ya country-tagged (`entity.country_code` post-0052), pero su SQL **podría** agregar cross-country sin partición, contaminando stats por-país. | Auditar cada job antes del onboarding #2: si agrega, añadir `GROUP BY/WHERE country_code`. El mecanismo (add_job/cadencia) es agnóstico; el riesgo vive en el SQL agregador, no en el scheduler. |

---

## Diseño genérico A->Z
> **[DISEÑO — additivo, €0, espejo de 0052, NO en código aún].** El orquestador se vuelve un **PRODUCTOR PARAMÉTRICO POR PAÍS** mediante tres cambios estructurales, todos additivos y byte-idénticos mientras ES sea el único inquilino. Es exactamente lo que falta construir para cerrar el `NEEDS_REWORK`.

### 1 · Abstracción REGISTRY-COMO-PACK
Hoy el motor importa dos dicts literales ES (`scheduler.REGISTRY:330`, `discover.DISCOVERY_REGISTRY:65`) más el mapa `ADAPTERS` de `pipeline/discover.py`. Se reemplazan por un proveedor `pipeline/ops/registry/`:
- `get_harvest_registry(country)->dict[str,SourceEntry]`
- `get_discovery_registry(country)->dict[str,DiscoveryJob]`
- `get_discovery_adapters(country)->dict[str,Adapter]`
- `active_countries()->list[str]` (de env `CARDEEP_COUNTRIES` o tabla `country`)

El pack ES se **MUEVE verbatim** a `registry/es.py` (los `SourceEntry` no cambian una línea); DE/IT/FR añaden `registry/<cc>.py`. El scheduler construye un registry **FUSIONADO** de los países activos. Con `active_countries()==['ES']` el merge devuelve exactamente el dict de hoy → **invariante de byte-identidad probado por el propio `--dry-run`**.

### 2 · `country_code` como TAG, no como reescritura de identidad
Migración additiva espejo de 0052: `source_health` (y opc. `harvest_run`/`source_breaker`) gana `country_code CHAR(2) NOT NULL DEFAULT 'ES'`. La due-query (`_due_sources:357`) y el predicado de silencio (`find_silent_sources:80`) ganan un filtro **OPCIONAL** `WHERE country_code = ANY($countries)`; cuando `$countries` es NULL devuelven el universo (comportamiento actual).
- `source_key` permanece como PK e **identidad global** (YAGNI idéntico a 0052, que dejó geo en `(code)` y difirió el swap a `(country_code,code)` hasta 0053 cuando un 2º inquilino lo forzó).
- Promoción a clave compuesta `(country_code,source_key)` **sólo** en la migración de onboarding cuando exista colisión real; hasta entonces la convención de nombrado `<plataforma>_<cc>` la evita a coste cero. **(El inquisidor sube esto a invariante duro — ver cluster C.)**
- `alert.origin` se mantiene `"<source_key>:<phase>"` (NO se prefija país: prefijarlo rompería la byte-identidad de todas las alertas ES y duplicaría filas vía dedup); el país se deriva por join a `source_health`.

### 3 · El lazo del productor se vuelve country-agnóstico
`heartbeat_tick:519` pasa a: `for country in active_countries(): cargar pack; due-query (scopeada o no); cada key se resuelve en el registry fusionado y se lanza como hoy` — **un subproceso a la vez**; el single-producer y el anti-AS24 se conservan porque el lock y la serie no cambian. Watchdog, breaker y red de crash NO se tocan. El lock por defecto sigue siendo UN singleton de host que drena todos los países en serie; para aislamiento VPS-país se deriva `lock_key(role,country)` con `holder="harvest:<cc>"`.

### 4 · Gobierno de cobertura (la red mecánica que cierra el lazo)
El `_gap_report` existente (`scheduler.py:394-398`, que lista filas de `source_health` SIN entrada en REGISTRY) se generaliza a **per-country**: un test de CI asegura que para cada país activo, **0 filas quedan UNMAPPED** y **todo `SourceEntry` tiene su semilla**. Un onboarding incompleto (semilla sin registry, o registry sin semilla) se vuelve un **fallo mecánico**, no una fuente silenciosamente no-planificada.

**Resultado:** el MOTOR (due-selection, lock, breaker, watchdog, lease, crash-net, alerta-origen-exacto, config_guard, arnés de cadencia, supervisor) es 100% reusado idéntico; el PACK (registry de harvest, registry de discovery + adapters, semillas de cadencia/tier1 con centinela, namespace de lock) es lo único que cada país declara.

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)
1. **Migración de columna** (una vez, espejo 0052, si no existe): `ALTER TABLE source_health ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES'`. Byte-idéntico para ES.
2. **Migración de semilla del país** (espejo `0039`): UPSERT en `source_health` una fila por fuente con `source_key`, `harvest_interval_hours`, `is_tier1`, `country_code='<CC>'` y el **centinela watchdog-safe** (`last_fail` ∈ `(interval, 2×interval)` para que la fila sea DUE pero NO falsamente SILENT — `0039:9-13`). Additiva, idempotente, reversible.
3. **Crear `pipeline/ops/registry/<cc>.py`** con la lista de `SourceEntry` (harvest) y de `DiscoveryJob` + `ADAPTERS` (descubrimiento) de los conectores del país, cadencia + env-gate de coste.
4. **Registrar el país en `active_countries()`** (`CARDEEP_COUNTRIES=ES,<CC>` o fila en `country`). Con el productor de host único, las fuentes ya entran en la cadencia.
5. **(Sólo aislamiento VPS-país)** calcular `lock_key(role,'<CC>')` para harvest y discovery y arrancar productores dedicados con `holder="harvest:<CC>"`; en host único, **SALTAR**.
6. **Verificar en seco:** `python -m pipeline.ops.scheduler --dry-run` debe mostrar las fuentes del país como WOULD RUN con el cmd correcto y **UNMAPPED=0 para ese país**; `python -m pipeline.discover_schedule --dry-run` muestra sus vectores con cadencia/gate.
7. **Verificar tracking pasivo:** `python -m pipeline.ops.scheduler --check-silence` (read-only) lista/contabiliza las filas nuevas sin disparar alertas.
8. **Persistencia:** host único → sin cambio de unidad; modelo per-país → instanciar la unit parametrizada con `CARDEEP_COUNTRY=<CC>` (NSSM `AppEnvironmentExtra` / systemd `EnvironmentFile`), sin ampersand, `Restart=always`/AppExit Default Restart.
9. **Sellar:** correr una cosecha real, confirmar que `record_run` escribe `source_health`, el breaker trackea fallos, una fuente deliberadamente callada dispara `"<key>:silence"` y **al recuperarse la alerta se RESUELVE** (verificación del fix zombie).

---

## Sellado + verificación multi-vía + rollback
**SELLADO en esta etapa = el país queda "gobernado mecánicamente":**
- (a) cada fila de `source_health` del país mapea a una entrada de registry (**0 UNMAPPED** en `--dry-run` per-country);
- (b) las fuentes due se seleccionan, se lanzan en serie bajo el único lock (sin doble productor), escriben su `record_run`, y breaker/silence/lease las trackean;
- (c) el lazo de observabilidad cierra en **AMBOS bordes**: una fuente callada dispara `"<key>:silence"` y una recuperada lo **RESUELVE** (fix raíz del zombie);
- (d) `config_guard` fail-fast acepta los DSN del país en prod.

**Verificación 2ª vía ortogonal (VAM):**
| Qué | Vía A | Vía B |
|---|---|---|
| Due-selection | `scheduler --dry-run` (ejecuta `_due_sources` vía psycopg2) | `SELECT` SQL directo del predicado `now()-COALESCE>=interval` contra PG — dos motores sobre la misma verdad, mismo conteo |
| Fix de silencio | log del watchdog `"resolved N recovered silence alerts"` | `SELECT count(*) FROM alert WHERE origin LIKE '%:silence' AND resolved_at IS NULL` antes/después: cae a 0 para recuperadas, permanece >0 para aún-calladas (test unitario nuevo: recuperada→resuelta, aún-callada→NO-resuelta) |
| Lease | log CRITICAL `"stale lease detected"` | `SELECT lock_key,holder,now()-last_heartbeat AS staleness FROM scheduler_lease` (`DEPLOY §4`) |

**ROLLBACK (todo additivo, reversible, €0):** el registry del país es un `.py` que se borra + des-registrar de `active_countries()`; la columna `country_code` se revierte con `DROP COLUMN` (DEFAULT 'ES' garantiza que ninguna fila ES dependa de ella); el fix de silencio es una función additiva + una llamada (revert = quitar la llamada); el namespace de lock vuelve al singleton quitando la derivación. Ninguna acción toca datos servidos ni es irreversible; **el lock garantiza que un rollback a medias jamás produce doble productor**.

---

## Veredicto adversarial: roturas -> resolución
> El inquisidor falló `holds=false` / **NEEDS_REWORK**, y se **ACEPTA**. Hoy el motor corre byte-idéntico para ES, pero **ningún país #2 puede onboardarse sin construir los cambios de §Diseño**. Ninguno está en código; todos están diseñados, additivos y €0. Abajo, **cada** break, missing_pack y sealing_hole con su resolución — o su OPEN ITEM con causa. Nada se oculta.

### Cluster A — Country-blindness de la orquestación (la espina dorsal)
Cubre **FR-CRITICAL #2** (due-selection y watchdog son scans globales sin predicado), **missing country_code**, **sealing_hole s2** (no hay query de salud/sello por país).
**Resolución [DISEÑO-LISTO]:** §Diseño-2 (columna `country_code` espejo 0052, DEFAULT 'ES') + filtro `WHERE country_code = ANY($countries)` opcional en `_due_sources:357` y `find_silent_sources:80`. Con ello: (i) un watchdog per-país deja de disparar `:silence` sobre filas de otro país; (ii) un scheduler per-país sólo selecciona sus filas; (iii) `s2` se cierra porque `source_health`/`alert` (vía join) ya cortan por país. Byte-idéntico para ES (sin `$countries` → universo).

### Cluster B — Advisory lock no paramétrico
Cubre **DE-CRITICAL #1** (lock fijo `0x43415244` → en DB compartida sólo UN país cosecha a la vez), **missing_pack m4** (LOCK_KEY por país + filas `scheduler_lease`), **sealing_hole s4** (el sello "single-producer" no coexiste con "todas las due de cada país corren").
**Resolución [DISEÑO-LISTO] + corrección al diseño:** el diseño gateaba el namespace de lock como "solo si VPS" — **el inquisidor lo invierte y tiene razón**: para la topología de DB compartida que el resto del sistema manda, **es obligatorio** uno de los dos modos, y el sello debe declarar cuál:
- **Modo host-único (default):** UN lock, UN productor que itera `active_countries()` y drena en serie. `s4` se reconcilia: "single-producer" se mantiene y "todas las due corren" se logra porque el lazo recorre todos los países. Las filas foráneas dejan de ser UNMAPPED porque el registry fusionado las mapea.
- **Modo VPS-por-país:** `lock_key(role,country)=BASE+role_offset+country_ordinal*OFFSET` + `holder="harvest:<cc>"` + due-selection scopeada (cluster A). `lock_heartbeat` ya recibe `lock_key` como parámetro (`lock_heartbeat.py:170-338`) → cambio sólo en call-site.
El sello **elige y declara el modo**; nunca ambos a la vez sobre la misma DB. `m4` se cierra con la función `lock_key()` + semilla `scheduler_lease`.

### Cluster C — Colisión de `source_key` (PK global) en fuentes pan-EU
Cubre **IT-CRITICAL #3** (`as24_wholesale`, OEM portals = una instancia/módulo sirviendo IT/DE/FR colisionan en el PK), **missing_pack m1** (convención de nombrado como invariante duro), **sealing_hole s5** (ningún gate prueba disjunción de `source_key` entre packs).
**Evidencia:** `source_health.source_key` es PK único (`0004:25`); ES ya registra fuentes pan-EU: `as24_wholesale` → `autoscout24_wholesale` (`scheduler.py:192`), `oem_audi_wholesale`/`oem_bmw_premium_selection_wholesale`/`oem_kia_wholesale`/… (`scheduler.py:255-269`) — mismas marcas y misma instancia AutoScout24 sirven varios países. Sembrar una fila IT para la misma fuente pan-EU colisiona en el PK (`ON CONFLICT` mantiene la fila ES).
**Resolución [DISEÑO-LISTO]:** elevar la **convención `<plataforma>_<cc>` a INVARIANTE duro** del country-pack (no mera sugerencia): toda `source_key` lleva sufijo de país, de modo que `autoscout24_es` ≠ `autoscout24_de` aunque compartan módulo (el `country` se pasa por dispatch — cluster D). `s5` se cierra con un **gate de CI de disjunción**: la unión de `source_key` de todos los packs activos debe ser libre de colisión, o falla el merge. Promoción a PK compuesta `(country_code,source_key)` diferida a la migración de onboarding cuando exista colisión real (espejo 0052→0053). Hasta entonces, la convención + el gate la evitan a coste cero.

### Cluster D — El contrato de dispatch no lleva país
Cubre **DE-HIGH #4** (`_build_cmd`/`_run_vector` no enhebran `--country`), **missing_pack m2**.
**Evidencia:** `_build_cmd = [python, -m, entry.module, *extra_args]` (`scheduler.py:405-407`); `_run_vector = [python, -m, pipeline.discover, job.vector]` (`discover_schedule.py:166`). Ningún flag de país. Un conector compartido o un vector global (`overture`/`collapse_invisible`/`graph_recursive`) no puede invocarse "para DE".
**Resolución [DISEÑO-LISTO]:** añadir un campo `country` al `SourceEntry`/`DiscoveryJob` del pack y enhebrarlo: `_build_cmd` añade `["--country", entry.country]` y `_run_vector` `["--country", job.country]`. Un único módulo pan-EU se reusa across países desde el scheduler sin hardcodear su país. Aditivo: para conectores ES que ya asumen ES, el flag es default `ES` → byte-idéntico.

### Cluster E — Registries hardcodeados, sin loader
Cubre **PT-HIGH #5** (onboarding PT = editar 3 dicts Python + la constante de lock = reescribir código, viola "country-pack sin reescribir código"), **missing_pack m3** (registry-loader), **missing_pack m6** (`pipeline/discover.py` ADAPTERS es una 2ª superficie ES-inlined).
**Resolución [DISEÑO-LISTO]:** §Diseño-1 (proveedor `pipeline/ops/registry/` con `get_harvest_registry`/`get_discovery_registry`/`get_discovery_adapters`/`active_countries`). El pack se **registra** sin editar el motor; `m6` se cierra explícitamente empaquetando ADAPTERS junto a los otros dos. Con `active_countries()==['ES']` → byte-idéntico (probado por `--dry-run`).

### Cluster F — Eje de descubrimiento ES-nacional / no-UE
Cubre **JP-HIGH #6** (`borme_cnae`/`dork_municipal` son 100% ES; para Japón haría falta hojin-bango/kokuzeicho, para México otro registro o ninguno; el dork no-latino necesita plantillas distintas).
**Resolución [OPEN ITEM con causa — gated en KNOW_COUNTRY]:** la orquestación NO puede cerrar esto sola. El registry de descubrimiento es **salida del pack**, derivada del Dossier de País (`COVER-NEW-COUNTRY.md §C/§E`). Si un país **no tiene** registro mercantil abierto €0, ese eje **simplemente no existe** en su pack y el denominador se apoya en otras listas ortogonales (mapas/asociaciones) — declarado como hueco-con-causa, no silencioso. La plantilla de dork no-latina es **preocupación del conector**, no del scheduler (que sólo lanza el vector con `--country`). **Causa del gate:** depende de la realidad registral del país, no del motor; se resuelve país-a-país en el Dossier, no en esta etapa.

### Cluster G — Triggers de intervalo + UTC, sin wall-clock/cron
Cubre **JP-MEDIUM #7** (`BlockingScheduler(timezone="UTC")` + `trigger="interval"`; una fuente que exige hora local fija no se expresa).
**Resolución [OPEN ITEM — diseño €0, diferido por YAGNI con causa]:** APScheduler soporta `CronTrigger` nativo; añadir al `SourceEntry`/`DiscoveryJob` un campo opcional `schedule: {kind: "interval"|"cron", tz, expr}` y, cuando `kind=="cron"`, registrar con `CronTrigger(..., timezone=pack_tz)` en vez de `interval`. **Causa del gate:** ningún país onboardado hoy demanda harvesting time-of-day-aware; se construye cuando un Dossier lo pruebe (no antes — invariante €0/YAGNI). Mientras tanto, queda declarado como knob ausente, no como capacidad falsa.

### Cluster H — Severidad binaria + aritmética de semilla no empaquetada
Cubre **FR-MEDIUM #8** (`is_tier1?critical:warning` es política ES-tuned; el centinela `0039` no está en el pack declarado), **missing_pack m5** (la aritmética watchdog-safe como paso explícito de onboarding).
**Evidencia:** severidad binaria en `silence_watchdog.py:128`; centinela `last_fail = now()-interval '169 hours'` para `as24_wholesale` (interval 168h) en `0039:23` → DUE pero no falsamente SILENT.
**Resolución [DISEÑO-LISTO]:** (i) empaquetar la aritmética del centinela como **paso de onboarding #2 obligatorio** (ya incorporado arriba) — sin él un país dispara `:silence` falso en el primer tick; (ii) gradiente de severidad: reemplazar el boolean por `tier SMALLINT` (0/1/2…) en `source_health`, mapeando `tier→severity` en el pack, para mercados con un marketplace dominante de criticidad mayor. Aditivo con DEFAULT que reproduce el comportamiento ES (`tier=1`→critical, resto→warning).

### Cluster I — Zombie `:silence` nunca se resuelve
Cubre **sealing_hole s1** (verificado: tras cualquier corte transitorio, cada país acumula un `:silence` abierto permanente → el sello "una recuperación cierra su propia alerta" y todo gate "0 alertas abiertas" son inalcanzables).
**Resolución [DISEÑO-LISTO; OPEN hasta merge]:** el fix de §Costuras (`resolve_recovered_silence_alerts` + defensa en `record_run`) cierra el lazo en ambos bordes. Test-contract especificado (recuperada→resuelta, aún-callada→NO-resuelta, espejando el contrato dedup existente). **Estado honesto:** el diseño y el test están listos y son €0, pero **NO está en código aún** → es un sealing-hole **activo** hasta el merge; ningún sello de etapa 9 (ni de país) puede declararse verde mientras zombies abiertos existan.

### Cluster J — Cobertura de gate/sello por país
Cubre **sealing_hole s3** (la cadena dry-run→golden→Ferrari→CI valida sólo el REGISTRY ES global; una semilla foránea aparece como UNMAPPED noise, no como sello fallido), **sealing_hole s4** (reconciliación single-producer ↔ "todas las due corren", ya tratada en cluster B).
**Resolución [DISEÑO-LISTO]:** §Diseño-4 (gobierno de cobertura) eleva `_gap_report` a per-country y lo conecta a CI: para cada país activo, **0 UNMAPPED** y todo `SourceEntry` con semilla, más el gate de disjunción (cluster C) y la verificación de que cada `source_key` sembrada tiene **registry + adapter + lock_key**. Un onboarding incompleto pasa de "ruido silencioso" a "CI rojo".

### Cluster K — Durabilidad Windows sin sellar + instancing de supervisor
Cubre **missing_pack m7** (artefacto Windows per-país commiteado), **missing_pack m8** (instancing del supervisor: `cardeep-harvest@<CC>.service` / NSSM-per-país), **sealing_hole s6** (la persistencia viva es prosa, no código; "el daemon sobrevive al reboot" no tiene artefacto ni cobertura CI/golden en el host real Windows 11).
**Resolución [OPEN ITEM con causa — €0, sólo falta construir]:** commitear `ops/windows/install-cardeep-services.ps1` idempotente (NSSM AppExit Default Restart, sin ampersand, `CARDEEP_COUNTRY`) + plantilla systemd `cardeep-harvest@.service` con `EnvironmentFile` por país. **Causa del gate:** hoy NO existe artefacto (verificado: sin `ops/windows/`), sólo prosa en `DEPLOY §3`; el sello de durabilidad se apoyaría en texto, lo cual viola "probado y funcional". Hasta el commit del PS1, la durabilidad queda **declarada pero no test-verificada** en el único host real.

### Tabla de trazabilidad (NADA oculto)
| Id | Severidad | Resolución | Estado |
|---|---|---|---|
| DE-CRIT #1 (lock global) | CRITICAL | Cluster B (lock_key paramétrico / host-único declarado) | DISEÑO-LISTO |
| FR-CRIT #2 (scans country-blind) | CRITICAL | Cluster A (country_code + filtro opcional) | DISEÑO-LISTO |
| IT-CRIT #3 (PK collision pan-EU) | CRITICAL | Cluster C (convención `_cc` invariante + gate disjunción) | DISEÑO-LISTO |
| DE-HIGH #4 (dispatch sin país) | HIGH | Cluster D (`--country` en `_build_cmd`/`_run_vector`) | DISEÑO-LISTO |
| PT-HIGH #5 (registries hardcoded) | HIGH | Cluster E (proveedor registry) | DISEÑO-LISTO |
| JP-HIGH #6 (descubrimiento no-UE) | HIGH | Cluster F (pack-derivado del Dossier) | **OPEN ITEM** (gated KNOW_COUNTRY) |
| JP-MED #7 (UTC/interval only) | MEDIUM | Cluster G (CronTrigger opcional) | **OPEN ITEM** (diferido YAGNI, €0) |
| FR-MED #8 (tier binario + semilla) | MEDIUM | Cluster H (centinela en onboarding + `tier` gradiente) | DISEÑO-LISTO |
| m1 naming convention invariante | — | Cluster C | DISEÑO-LISTO |
| m2 `--country` en dispatch | — | Cluster D | DISEÑO-LISTO |
| m3 registry-loader seam | — | Cluster E | DISEÑO-LISTO |
| m4 LOCK_KEY por país + lease rows | — | Cluster B | DISEÑO-LISTO |
| m5 aritmética semilla watchdog-safe | — | Cluster H + onboarding paso #2 | DISEÑO-LISTO |
| m6 ADAPTERS como 2ª superficie | — | Cluster E | DISEÑO-LISTO |
| m7 artefacto Windows per-país | — | Cluster K | **OPEN ITEM** (sin artefacto hoy) |
| m8 supervisor per-país instancing | — | Cluster K | **OPEN ITEM** (sin artefacto hoy) |
| s1 zombie `:silence` | — | Cluster I | DISEÑO-LISTO / **OPEN hasta merge** |
| s2 sin query salud por país | — | Cluster A | DISEÑO-LISTO |
| s3 gate sólo valida ES | — | Cluster J | DISEÑO-LISTO |
| s4 single-producer ↔ due-de-todos | — | Cluster B | DISEÑO-LISTO |
| s5 sin gate de disjunción | — | Cluster C | DISEÑO-LISTO |
| s6 durabilidad Windows sin sellar | — | Cluster K | **OPEN ITEM** (prosa, no código) |

---

## Sub-proyectos institucionales (360 por faceta)

> Esta sección es la **capa más profunda** del capítulo: cada átomo de la orquestación tratado como un **proyecto institucional 360°** independiente —verificado contra el código, roto adversarialmente por país y devuelto con su sellado y su palanca de élite €0—. Donde §Veredicto razona por **clusters** (la vista de mando), aquí se baja **átomo a átomo** (la vista de obra). Nada se inventa: cada afirmación lleva su `[VERIFIED path:línea]` o se declara `[ASSUMED]`; los open items conservan su causa. El set está **COMPLETO: 21 sub-proyectos** (los 12 del núcleo + los 9 que la v2 parcial sólo citaba como punteros, ahora con deep-dive propio).

**Anatomía fija de cada sub-proyecto** (funnel: la MISMA forma en los 21, nadie se pierde):

- **(a) Verificación de code_hints** contra el código real
- **(b) Mecanismo al átomo**
- **(c) Costura ES→genérico**
- **(d) Fix** exacto (additivo, ES byte-idéntico)
- **(e) Adversarial** (rotura concreta por país)
- **(f) Sellado + verificación multi-vía** (≥2 vías ortogonales)
- **(g) Herramienta NEXT-LEVEL** (€0, battle-tested)

> Las partes **(a)+(b)** salen del deep-dive de cada átomo (verificación de code_hints + mecanismo); algunas las titula como *(a)/(b)*, otras como *Verificación/Mecanismo* — el contenido es el mismo contrato. Las partes **(c)–(g)** son uniformes en los 21.

**Mapa de átomos → sub-proyecto (cross-referencias resueltas, NADA colgando).** Los deep-dives se citan entre sí por su número de átomo interno (`faceta N`). A diferencia de la v2 parcial —que dejaba faceta 6/10/12-13/20 como punteros `[VERIFIED]` sin deep-dive—, **todos** tienen ya su sub-proyecto. Cualquier `faceta N` del texto verbatim resuelve aquí:

| Átomo | Sub-proyecto | Átomo | Sub-proyecto |
|---|---|---|---|
| faceta 1 | SP-01 | faceta 10 | SP-14 |
| faceta 2 | SP-04 | faceta 12 | SP-11 |
| faceta 3 | SP-13 | faceta 13 | SP-17 |
| faceta 4 | SP-07 | faceta 14 | SP-03 / SP-21 |
| faceta 5 | SP-10 | faceta 16 | SP-06 |
| faceta 6 | SP-16 | faceta 20 | SP-18 |
| faceta 9 | SP-05 | faceta 21 | SP-20 |

### Índice navegable de sub-proyectos

> **Núcleo (01–12)** = los átomos del primer barrido. **Completado (13–21)** = los átomos antes citados como punteros, ahora deep-dive 360°.

| # | Sub-proyecto | Rotura / qué cierra | Estado |
|---|---|---|---|
| 01 | [Mutex single-producer + lock_key por (rol,país)](#sp-01) | Cluster B · lock global `0x43415244` no paramétrico (DE-CRIT #1) | DISEÑO-LISTO |
| 02 | [Arnés de subproceso + muro de timeout](#sp-02) | Muro global 4h / scar `motor_es` (SIGKILL pre-`record_run`) | DISEÑO-LISTO |
| 03 | [Aritmética de semilla watchdog-safe (onboarding)](#sp-03) | Cluster H · semilla no empaquetada (m5) + `_seed` NULL/NULL | DISEÑO-LISTO |
| 04 | [Lease/heartbeat observable (crashed-vs-vivo)](#sp-04) | Diagnosticabilidad per-país (m4) · holder sin país | DISEÑO-LISTO |
| 05 | [Circuit breaker (trip/cooldown/half-open)](#sp-05) | Cluster C · colisión `source_key` pan-EU (IT-CRIT #3) + divergencia de sonda | DISEÑO-LISTO |
| 06 | [Arnés de cadencia APScheduler (jobstore/triggers)](#sp-06) | Cluster G · UTC/interval sin wall-clock (JP-MED #7) + asimetría de durabilidad | OPEN (cron diferido YAGNI) |
| 07 | [Discovery registry + ADAPTERS como country-pack](#sp-07) | Cluster E · registries hardcoded + 2ª superficie (PT-HIGH #5, m6) | DISEÑO-LISTO |
| 08 | [Watchdog de silencio — DETECCIÓN](#sp-08) | Cluster A · scan country-blind (FR-CRIT #2) | DISEÑO-LISTO |
| 09 | [config_guard fail-fast prod + secretos por país](#sp-09) | Drift de cobertura de la matriz de secretos | DISEÑO-LISTO |
| 10 | [Dimensión país en el esquema de orquestación](#sp-10) | Cluster A+C · `country_code` ausente en orquestación | DISEÑO-LISTO |
| 11 | [Resolución del zombie `:silence` (bug raíz)](#sp-11) | Cluster I · borde *resolve* inexistente (s1) | DISEÑO-LISTO / OPEN hasta merge |
| 12 | [Supervisor de proceso + artefactos de durabilidad](#sp-12) | Cluster K · Windows sin artefacto (m7/m8/s6) | OPEN (sin artefacto) |
| 13 | [Harvest registry como country-pack cargable](#sp-13) | Cluster E · roster ES soldado al motor (PT-HIGH #5, m3) | DISEÑO-LISTO |
| 14 | [Red de seguridad crash-before-record_run](#sp-14) | Cluster C · high-water `source_key`-global → falso-negativo cross-país (IT-CRIT #3) | DISEÑO-LISTO |
| 15 | [Jobs de mantenimiento + auditoría de agregación cross-país](#sp-15) | §Costuras · cohort/stats agregan sin `country_code` (price_trap, product_stats) | DISEÑO-LISTO |
| 16 | [Motor de due-selection con scoping de país](#sp-16) | Cluster A · scan global sin predicado (FR-CRIT #2) + fair-share | DISEÑO-LISTO |
| 17 | [Gramática de alerta origen-exacto + dedup](#sp-17) | Cluster A/C · dedup en `origin` texto-libre sin país, espejo sync/async | DISEÑO-LISTO |
| 18 | [Gate de gobierno de cobertura (registry-drift CI)](#sp-18) | Cluster J+C · `_gap_report` sólo-ES, sin gate de disjunción (s3/s5) | DISEÑO-LISTO |
| 19 | [Contrato de dispatch con parámetro de país](#sp-19) | Cluster D · `_build_cmd`/`_run_vector` sin `--country` (DE-HIGH #4, m2) | DISEÑO-LISTO |
| 20 | [Superficie unificada de salud del orquestador](#sp-20) | sealing_hole s2 · `v_orchestrator_health` inexistente (next_level 09 #1) | OPEN (depende de SP-10 / faceta 5) |
| 21 | [Aritmética de semilla watchdog-safe — banda `[interval, 2·interval)` (2ª pasada)](#sp-21) | Cluster H · refuerzo de SP-03 — banda semiabierta + property-test | DISEÑO-LISTO |

---

<a id="sp-01"></a>
### SP-01 · Mutex single-producer + lock_key por (rol,país)

*Mapa de átomos: faceta 1.*

#### (a) Verificacion de code_hints contra el codigo real
- **[VERIFIED `pipeline/ops/scheduler.py:913`]** `_SCHEDULER_SINGLETON_LOCK = 0x43415244` — constante FIJA de modulo (ASCII 'CARD' = 1128354372), comentada como "fixed host-singleton key".
- **[VERIFIED `pipeline/ops/scheduler.py:914-915`]** `_lock_conn = psycopg2.connect(_RAW_DSN); _lock_conn.autocommit = True` — la conexion del lock se mantiene ABIERTA toda la vida del proceso (auto-release de la session-lock al cerrar al salir).
- **[VERIFIED `pipeline/ops/scheduler.py:919-924`]** `if not acquire_with_stale_retry(_lock_conn, _SCHEDULER_SINGLETON_LOCK): _lock_conn.close(); raise SystemExit("another cardeep scheduler already holds the singleton advisory lock (...) refusing to start a second producer on this host")` — el 2o productor MUERE con SystemExit.
- **[VERIFIED `pipeline/ops/scheduler.py:928`]** `record_heartbeat(_lock_conn, _SCHEDULER_SINGLETON_LOCK, holder="harvest")` — el holder se nombra "harvest" SIN pais.
- **[VERIFIED `pipeline/discover_schedule.py:50`]** `_LOCK_KEY = 0x43415244 + 1  # 'CARD'+1 — distinct from the harvest scheduler's singleton lock` — segunda constante FIJA, rol discovery.
- **[VERIFIED `pipeline/discover_schedule.py:252-253`]** `if not acquire_with_stale_retry(lock, _LOCK_KEY): raise SystemExit("another discovery scheduler holds the advisory lock; refusing to start")`.
- **[VERIFIED `pipeline/ops/lock_heartbeat.py:309-338`]** `acquire_with_stale_retry(conn, lock_key, *, now=None, ttl_minutes=None) -> bool`: ejecuta `SELECT pg_try_advisory_lock(%s)` con `lock_key`; si falla y la lease esta stale, reintenta UNA vez. **El parametro `lock_key` YA es un argumento** — la funcion del mutex es generica; el hardcodeo vive SOLO en los dos call-sites (`:913`, `:50`).
- **[VERIFIED `docs/DEPLOY-DURABLE-DAEMONS.md`]** doctrina "el single-instance lo garantiza el advisory lock en PG, no el host".

#### (b) El mecanismo al atomo
1. Cada daemon abre UNA conexion autocommit dedicada y la deja viva todo el proceso.
2. `pg_try_advisory_lock(lock_key)` es el **mutex atomico de sesion**: devuelve `true` solo si NINGUNA otra sesion lo tiene. Nunca desplaza a un vivo (propiedad clave anti-AS24).
3. Si devuelve `false`, `acquire_with_stale_retry` consulta `scheduler_lease` (faceta 2): si el holder previo crasheo en duro (heartbeat > TTL 6min) loguea CRITICAL y **reintenta una sola vez** — porque una vez PG recolecta la sesion muerta, el lock queda libre.
4. Si sigue ocupado por un vivo -> `SystemExit`. Asi NUNCA hay dos productores contra el mismo `lock_key`.
5. El holder vivo refresca su lease cada 2min (`_lease_heartbeat_job`, faceta 2). Al salir limpio (SIGTERM), cerrar la conexion auto-libera el lock instantaneamente.

El invariante real garantizado es: **un (1) productor por valor de `lock_key`**. Hoy hay exactamente dos valores en TODO el sistema (BASE harvest, BASE+1 discovery), GLOBALES, sin eje pais.

#### (c) Costura ES→genérico

COSTURA ES->generico: el mutex (`acquire_with_stale_retry`, lock_heartbeat.py:309) YA toma `lock_key` como PARAMETRO, asi que el motor del mutex es generico y NO se toca una linea. La soldadura ES esta EXCLUSIVAMENTE en los dos call-sites que pasan una constante de modulo fija: `scheduler.py:913 _SCHEDULER_SINGLETON_LOCK=0x43415244` y `discover_schedule.py:50 _LOCK_KEY=0x43415244+1`. Ambos derivan el lock_key de NADA (literal). El eje (rol,pais) no existe en el valor del lock => en una DB compartida multi-tenant (espejo de 0052/0053) dos paises chocan en el MISMO advisory lock. La decision de topologia ortogonal: (A) UN productor de host que drena todos los paises en serie con fair-share en la due-query (faceta 6) -> un solo lock_key por ROL, el pais NO entra en el lock; (B) UN productor por pais -> lock_key disjunto por (rol,pais). El seam soporta AMBAS sin tocar el mutex.

#### (d) Fix exacto

FIX EXACTO (additivo, ES byte-identico en ordinal 0):
Nuevo modulo generico `pipeline/ops/lock_keys.py`:
```python
_LOCK_BASE = 0x43415244          # 'CARD' — unchanged anchor
_ROLE_OFFSET = {'harvest': 0, 'discovery': 1}
_ROLE_SPAN = len(_ROLE_OFFSET)   # 2 roles -> stride 2 so country slots never overlap roles

def lock_key_for(role: str, country: str, ordinals: dict[str, int]) -> int:
    """Disjoint 32-bit advisory-lock key per (role, country).
    ES at ordinal 0 reproduces today's keys EXACTLY:
      harvest/ES   = BASE + 0 + 0*2 = 0x43415244       (== scheduler.py:913)
      discovery/ES = BASE + 1 + 0*2 = 0x43415244 + 1   (== discover_schedule.py:50)
    DE at ordinal 1 -> {BASE+2, BASE+3}, disjoint from ES."""
    return _LOCK_BASE + _ROLE_OFFSET[role] + ordinals[country] * _ROLE_SPAN
```
Call-site harvest (`scheduler.py:913`): `lock_key = lock_key_for('harvest', cc, ORDINALS)` con `cc=os.environ.get('CARDEEP_COUNTRY','ES')` y `ORDINALS` del active-countries registry (faceta 3); call-site discovery (`discover_schedule.py:50`) identico con role='discovery'. TOPOLOGIA-A (default EUR0, single-host): se instancia un solo daemon por rol -> usa el lock_key de su CARDEEP_COUNTRY pero el drenado multi-pais ocurre en la due-query (faceta 6), no en el lock. TOPOLOGIA-B (escala multi-host/tenant): un daemon por (rol,pais) toma su lock disjunto. El mutex `pg_try_advisory_lock` permanece intacto -> cero riesgo de doble-productor.

#### (e) Adversarial — rotura por país

[VERIFIED] BREAK CRITICO Germany: en DB compartida (0052/0053) un scheduler DE contra el mismo PG obtiene `pg_try_advisory_lock==false` porque ES ya tiene 0x43415244=1128354372, y hace SystemExit (scheduler.py:919-924) => solo UN pais cosecha a la vez. El design lista el namespace de lock bajo country_pack pero lo gatea '(Solo si VPS)' — al reves: es OBLIGATORIO para la topologia DB-compartida. El fix (lock_key disjunto por ordinal) deja a DE tomar BASE+2 mientras ES tiene BASE.
Riesgos adversariales del PROPIO fix: (1) COLISION DE ORDINAL — si el country-pack asigna a DE el mismo ordinal que ES (typo, registry no-injectivo), dos paises vuelven a compartir lock_key => single-producer-cross-pais SILENCIOSO; el sello DEBE probar inyectividad del mapa ordinal. (2) PT/IT/no-UE sin registry aun: no se debe pre-asignar slot a un pais que active_countries() no incluye (slots fantasma) — el ordinal se materializa solo al activar el pais. (3) RUIDO/overflow: con stride 2 y un 32-bit key, el espacio aguanta ~2.000M paises; no hay overflow real, pero un OFFSET mal elegido (p.ej. solapar role_offset con el stride) reintroduciria colision rol<->pais — por eso `_ROLE_SPAN == len(_ROLE_OFFSET)`.

#### (f) Sellado + verificación multi-vía

CRITERIO DE SELLADO + verificacion multi-via:
(a) UNIT byte-identidad: `lock_key_for('harvest','ES',{'ES':0}) == 0x43415244` y `lock_key_for('discovery','ES',{'ES':0}) == 0x43415244+1` — ES intacto.
(b) INTEGRATION disjuncion: dos schedulers ES+DE contra el mismo PG AMBOS adquieren (keys disjuntos, ninguno SystemExit); un SEGUNDO scheduler ES SI hace SystemExit (single-producer intra-pais preservado, anti-AS24).
(c) ADVERSARIAL inyectividad: el guard del country-pack (faceta 20, Pydantic) FALLA si el mapa de ordinales no es injectivo (dos paises -> mismo slot).
(d) 2a VIA ortogonal: `SELECT objid, classid FROM pg_locks WHERE locktype='advisory'` devuelve EXACTAMENTE una fila por (rol,pais) vivo; el conjunto observado == el conjunto esperado de `lock_key_for` para active_countries(). El conteo de filas pg_locks (camino PG) cruza contra el calculo Python (camino aplicacion) — dos vias independientes del mismo invariante.

#### (g) Herramienta NEXT-LEVEL (€0)

HERRAMIENTA NEXT-LEVEL: Procrastinate (MIT, EUR0=True) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555,67]. Eleva el single-producer de un advisory-lock hecho a mano (cuyo lease es 'best-effort, NO takeover', riesgo declarado scheduler/lock_heartbeat) a una COLA DURABLE Postgres-nativa con claim idempotente `FOR UPDATE SKIP LOCKED` exactamente-una-vez. Con una cola/tarea por (rol,pais) cada cosecha de pais es una TAREA reclamada exactamente una vez -> la colision de lock_key pan-EU DESAPARECE (no hay un unico mutex global que repartirse) y un worker matado a mitad REANUDA sin perder unidad de trabajo. Corre sobre el PG existente (:5433/:5434), cero infra nueva, cero GPU. Alternativa-piso: pgqueuer (MIT, https://github.com/janbjorge/pgqueuer) — LISTEN/NOTIFY + SKIP LOCKED si solo se quiere el claim durable sin el motor de retry. Descartado como cimiento: Temporal (exige cluster aparte, no EUR0).

---

<a id="sp-02"></a>
### SP-02 · Arnés de subproceso + muro de timeout

#### (a) Verificacion de code_hints contra el codigo real
- **[VERIFIED `pipeline/ops/scheduler.py:123`]** `SUBPROCESS_TIMEOUT_SEC = int(os.environ.get("CARDEEP_SUBPROCESS_TIMEOUT", 14400))  # 4h default` — muro GLOBAL de modulo, uno para TODAS las fuentes/paises.
- **[VERIFIED `pipeline/ops/scheduler.py:410-445`]** `_run_source(source_key)`: lee `entry = REGISTRY[source_key]`, construye `cmd = _build_cmd(entry)`.
- **[VERIFIED `pipeline/ops/scheduler.py:425`]** `child_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}` — inyeccion utf-8 (fix B3.3, alert id 6 coches_com Sigma crash), asume cp1252-Windows como UNICO problema de encoding.
- **[VERIFIED `pipeline/ops/scheduler.py:427-432`]** `subprocess.run(cmd, timeout=SUBPROCESS_TIMEOUT_SEC, check=False, env=child_env)`.
- **[VERIFIED `pipeline/ops/scheduler.py:434-436`]** `except subprocess.TimeoutExpired: log.error("TIMEOUT %s after %ds", ...); exit_code = -1` y `:437-439 except Exception: exit_code = -2` — try/except best-effort que NUNCA mata al productor.
- **[VERIFIED `pipeline/ops/scheduler.py:175-182`]** scar `motor_es_wholesale`: el prior `--full --segment all` drenaba ~51k en ~4.7h -> excedia el muro de 4h -> **SIGKILL antes de record_run -> silent re-timeout cada cadencia** (last_ok atascado 2026-06-15). Reparado con `--cursor` (offset persistente por celda) + `--max-cells 40 --limit 12000`.
- **[VERIFIED `pipeline/discover_schedule.py:48`]** `SUBPROCESS_TIMEOUT_SEC = int(os.environ.get("CARDEEP_DISCOVERY_TIMEOUT", "21600"))  # 6h`.
- **[VERIFIED `pipeline/discover_schedule.py:163-183`]** `_run_vector(job)`: `cmd=[sys.executable,"-m","pipeline.discover",job.vector]`, `child_env={**os.environ,"PYTHONIOENCODING":"utf-8",**job.env}` (:167), `subprocess.run(..., timeout=SUBPROCESS_TIMEOUT_SEC, capture_output=True, text=True)` (:170-171), `TimeoutExpired -> return -1, None` (:172-174).

#### (b) El mecanismo al atomo
1. `heartbeat_tick` (scheduler.py:519) trae las fuentes DUE y por cada una llama `_run_source`.
2. `_run_source` lanza UN subproceso (`python -m <module> <extra_args>`) y BLOQUEA esperando hasta `SUBPROCESS_TIMEOUT_SEC`.
3. El muro de 4h (harvest) / 6h (discovery) es un `subprocess.run(timeout=...)`: al expirar, Python manda SIGKILL al hijo y levanta `TimeoutExpired` -> exit_code=-1.
4. El conector es **responsable de escribir su PROPIO `record_run`**; el scheduler NO lo hace en el camino normal. Si el conector es SIGKILLeado ANTES de su record_run, `source_health` queda intacto -> el breaker no salta, el watchdog tarda 2x interval -> la red de seguridad (faceta 10, `_record_crash_if_unrecorded`) graba el fallo si no aparecio un harvest_run nuevo.
5. La inyeccion `PYTHONIOENCODING=utf-8` fuerza I/O UTF-8 en el hijo independientemente del default de plataforma (Windows cp1252).

El arnes es **country-agnostico por mecanica** (solo corre argv con un muro), pero el muro y el locale estan FIJOS como constantes ES.

#### (c) Costura ES→genérico

COSTURA ES->generico: el arnes fisico (`subprocess.run` + try/except) es generico, pero DOS parametros estan congelados como constantes de modulo ES: (1) `SUBPROCESS_TIMEOUT_SEC=14400` (scheduler.py:123) — UN muro de 4h para TODA fuente de TODO pais; (2) `PYTHONIOENCODING='utf-8'` hardcodeado (scheduler.py:425, discover_schedule.py:167) — asume que el unico problema de encoding es cp1252-Windows. El scar `motor_es` (scheduler.py:175-182) PRUEBA el fallo: un censo nacional grande en un solo modulo (~51k/~4.7h) supera el muro global, es SIGKILLeado antes de su record_run y RE-TIMEOUTea silenciosamente cada cadencia. La costura es: el muro debe ser PER-FUENTE (declarado por el country-pack en la SourceEntry), no una constante unica, y el locale/encoding del hijo debe ser declarable por fuente, no utf-8 cableado.

#### (d) Fix exacto

FIX EXACTO (additivo, ES byte-identico por defaults):
Extender `SourceEntry` (scheduler.py:144) con dos campos con default que reproducen HOY:
```python
class SourceEntry(NamedTuple):
    source_key: str
    module: str
    extra_args: list[str]
    timeout_sec: int = SUBPROCESS_TIMEOUT_SEC   # per-source wall; default == today's 4h
    child_env: dict[str, str] = {}              # per-source locale/encoding overlay; default {}
```
En `_run_source` (scheduler.py:425-429):
```python
child_env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', **entry.child_env}
result = subprocess.run(cmd, timeout=entry.timeout_sec, check=False, env=child_env)
```
Con `timeout_sec` default 14400 y `child_env` default `{}`, TODA SourceEntry ES produce argv+env byte-identicos (las ~50 entradas no cambian una linea). Un censo nacional lento declara `timeout_sec=` mayor O — preferido y country-proof — empaqueta un slice resumible `--cursor` (patron motor_es) que cabe en el muro default y escribe last_ok cada tick. Un pais de escritura no-latina declara `child_env={'LANG':'ja_JP.UTF-8','LC_ALL':'ja_JP.UTF-8'}`. Identica extension en `DiscoveryJob`/`_run_vector` (discover_schedule.py:163) para el muro de 6h de discovery.

#### (e) Adversarial — rotura por país

[VERIFIED] El muro de 4h es GLOBAL, no por-fuente/pais: un mercado nacional con un censo grande en un solo modulo (motor_es drenaba ~51k en ~4.7h, scheduler.py:175-182) es SIGKILLeado antes de record_run. La inyeccion utf-8 asume cp1252-Windows; un pais con script no-latino puede necesitar locale distinto que el arnes no expresa.
Concrecion por pais: (1) DE/IT — un marketplace nacional dominante (p.ej. mobile.de, autoscout24 DE) cuyo censo COMPLETO exceda 4h en un modulo reedita el scar motor_es CROSS-PAIS: re-timeout silencioso, last_ok congelado, breaker nunca salta porque el SIGKILL precede al record_run. (2) JP/no-UE — el locale del hijo no es declarable: un conector que emite a stdout en Shift-JIS/CJK puede crashear por encoding pese al utf-8 forzado (que asume que el PROBLEMA es solo cp1252). (3) RUIDO — un conector que cuelga en un socket sin progreso (red lenta del pais) debe AUN golpear el muro y disparar el crash-net (faceta 10); si el muro per-fuente se fija demasiado alto 'por si acaso', un hang real tarda horas en detectarse. El fix obliga a dimensionar el muro por la naturaleza de la fuente, no por un default unico.

#### (f) Sellado + verificación multi-vía

CRITERIO DE SELLADO + verificacion multi-via:
(a) UNIT byte-identidad: cada SourceEntry ES tiene `timeout_sec==14400` y `child_env=={}` por default -> argv+env identicos al HEAD actual (golden de las ~50 entradas).
(b) INTEGRATION muro+crash-net: un conector de test que duerme MAS alla de un muro pequeno es SIGKILLeado Y `_record_crash_if_unrecorded` (faceta 10) graba el fallo (last_ok intacto, breaker engancha) -> CERO re-timeout silencioso.
(c) ADVERSARIAL censo-grande: una fuente con slice `--cursor` TERMINA dentro del muro y escribe last_ok a lo largo de N ticks que cubren toda la particion make->model (la reparacion motor_es, generalizada) — verificado por la progresion monotona del cursor y last_ok avanzando.
(d) 2a VIA ortogonal: contar filas `harvest_run` por tick (camino DB) vs el gate high-water de la red de seguridad (faceta 10, scheduler.py:489-495, camino aplicacion) — el crash-net dispara EXACTAMENTE cuando el conector no grabo, ni una vez de mas (idempotencia por high-water id).

#### (g) Herramienta NEXT-LEVEL (€0)

HERRAMIENTA NEXT-LEVEL: Procrastinate (MIT, EUR0=True) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555,67]. Aplicada AQUI a la unidad-de-trabajo del subproceso: reemplaza el `subprocess.run` con muro duro + try/except best-effort por una TAREA durable con `RetryStrategy(max_attempts, exponential)`, deferral y REANUDACION a-mitad-de-vuelo tras crash (NEXT-LEVEL.md:553-554: 'una fuente con fallo transitorio se reintenta con backoff en vez de quemar el breaker', 'reanudacion real de la unidad de trabajo'). Cierra el scar motor_es de raiz: el offset `--cursor` se checkpointea en el ESTADO de la tarea durable, asi un timeout/restart REANUDA la cosecha en vez de re-timeoutear cada cadencia. Sobre el PG existente, cero infra, cero GPU. Alternativa para UN conector grande paso-a-paso: DBOS Transact (MIT, https://github.com/dbos-inc/dbos-transact-py) — ejecucion durable por decoradores, workflow reanudable step-by-step. Piso sin dependencia: mantener el muro per-fuente + cursor (ya en-repo para motor_es) como patron replicable.

---

<a id="sp-03"></a>
### SP-03 · Aritmética de semilla watchdog-safe (onboarding)

*Mapa de átomos: faceta 14.*

#### (a) Verificacion de code_hints contra el codigo real
- **[VERIFIED `migrations/0039_schedule_segments_as24.sql:9-14`]** comentario "WATCHDOG-SAFE SEED": `last_fail` se siembra a un sentinel mas VIEJO que `harvest_interval_hours` (=> inmediatamente DUE) pero mas NUEVO que `2*harvest_interval_hours` (=> el silence_watchdog, que marca `now()-COALESCE(last_ok,last_fail,epoch) > 2*interval`, NO levanta falsa `:silence`). `status='unknown' + consecutive_fails=0` mantienen el breaker CLOSED.
- **[VERIFIED `migrations/0039:16-19`]** `INSERT ... VALUES ('coches_net_segments', FALSE, 24, 'unknown', 0, NULL, now() - interval '25 hours') ON CONFLICT DO NOTHING` — interval=24h, sentinel=25h: 24 <= 25 < 48. DUE pero NO SILENT.
- **[VERIFIED `migrations/0039:21-24`]** `VALUES ('as24_wholesale', FALSE, 168, 'unknown', 0, NULL, now() - interval '169 hours')` — interval=168h, sentinel=169h: 168 <= 169 < 336. DUE pero NO SILENT. **Patron exacto: sentinel = interval+1.**
- **[VERIFIED `pipeline/discover_schedule.py:87-98`]** `_seed`: `INSERT INTO source_health (source_key, harvest_interval_hours, status) VALUES ($1,$2,'unknown') ON CONFLICT (source_key) DO UPDATE SET harvest_interval_hours = EXCLUDED.harvest_interval_hours` — **inserta last_ok/last_fail = NULL/NULL** (no estan en la columna-lista). `COALESCE(NULL,NULL,'1970')` => ~55 anos > 2x interval => SILENT en el PRIMER ciclo.
- **[VERIFIED `pipeline/ops/silence_watchdog.py` predicado 2x interval]** confirma que `now()-COALESCE(last_ok,last_fail,'1970')>2*interval` es la condicion de silencio (espejo del comentario 0039).

#### (b) El mecanismo al atomo
1. El scheduler es invisible a una fuente sin fila en `source_health` (`_due_sources` lee esa tabla). Onboarding = sembrar la fila + tener entrada en REGISTRY (leccion autocasion-orphan, 0039:5-7).
2. La fila recien sembrada debe estar en un estado preciso: **DUE** (para que el primer tick la lance) pero **NO SILENT** (para no disparar una `:silence` falsa el dia uno), con el **breaker CLOSED** (consecutive_fails=0, si no `_due_sources:377` la salta).
3. La aritmetica que satisface las tres: `last_ok=NULL`, `last_fail = now() - (interval+1)h`, `status='unknown'`, `consecutive_fails=0`. Porque `interval <= interval+1 < 2*interval` para todo `interval>=1`.
4. El BUG INTERNO: el `_seed` de discovery NO aplica este sentinel — inserta NULL/NULL -> `COALESCE->'1970'` -> ~55 anos > 2x interval -> SILENT inmediato. `borme_cnae` (24h, nunca corrido) aparece callado el primer ciclo.
5. El sentinel del 0039 es correcto pero esta HARDCODEADO a mano por fuente (25h, 169h) — no es una receta reutilizable; un onboarding ingenuo lo reinventa mal.

#### (c) Costura ES→genérico

COSTURA ES->generico: la receta de siembra watchdog-safe existe SOLO como dos INSERTs hechos a mano en `migrations/0039` con sentinels pre-calculados (25h para interval 24h, 169h para 168h) y comentario explicativo. No hay funcion/helper que DERIVE el sentinel de un interval arbitrario, asi que un pais nuevo debe re-calcular a mano `(interval, 2*interval)` por cada fuente — fragil y propenso a error. Peor: el `_seed` de discovery (discover_schedule.py:87-98) NO usa el sentinel — inserta NULL/NULL, que via `COALESCE(...,'1970')` lo convierte en SILENT el primer ciclo (deuda interna, no de pais). La costura es: empaquetar la aritmetica `last_fail = now() - (interval+1)h, status='unknown', consecutive_fails=0` como UN helper generico usado por (i) el generador de semillas del onboarding y (ii) el `_seed` de discovery, eliminando el NULL/NULL.

#### (d) Fix exacto

FIX EXACTO (additivo, ES byte-identico — reproduce 0039):
Helper generico (SQL-expresable, sin dependencia):
```python
def watchdog_safe_seed(source_key: str, interval_hours: int, is_tier1: bool) -> dict:
    """DUE-but-not-SILENT seed: last_fail = now() - (interval+1)h.
    interval <= interval+1 < 2*interval  for all interval >= 1, so the row is
    immediately DUE yet never falsely SILENT; breaker CLOSED. Reproduces 0039
    EXACTLY: 24h -> 25h, 168h -> 169h."""
    return {'source_key': source_key, 'is_tier1': is_tier1,
            'harvest_interval_hours': interval_hours, 'status': 'unknown',
            'consecutive_fails': 0, 'last_ok': None,
            'last_fail_offset_hours': interval_hours + 1}
```
FIX del bug interno en `discover_schedule._seed` (discover_schedule.py:91-96) — sustituir el INSERT NULL/NULL por el sentinel, preservando el ON CONFLICT que NUNCA revierte una fila viva:
```sql
INSERT INTO source_health (source_key, harvest_interval_hours, status,
                           consecutive_fails, last_fail)
VALUES ($1, $2, 'unknown', 0, now() - ($2 + 1) * interval '1 hour')
ON CONFLICT (source_key) DO UPDATE
  SET harvest_interval_hours = EXCLUDED.harvest_interval_hours
```
El sentinel solo aparece en VALUES (fila NUEVA); el DO UPDATE toca SOLO harvest_interval_hours, asi una fila viva conserva su last_ok/last_fail real. El generador de migraciones de onboarding emite los INSERT por fuente con `now() - (interval+1) * interval '1 hour'` en vez de literales a mano.

#### (e) Adversarial — rotura por país

[VERIFIED] BREAK France (MEDIUM) + deuda interna: el `_seed` de discovery (discover_schedule.py:87-98) ya inserta NULL/NULL => sus vectores aparecen SILENT inmediatamente (borme_cnae 24h nunca corrido => callado). El sentinel del 0039 no esta empaquetado como receta reutilizable; un onboarding ingenuo lo reinventa mal y floodea `:silence` falsas.
Concrecion por pais: (1) FR — borme_cnae/dork_municipal sembrados NULL/NULL disparan `:silence` el dia uno (y por la faceta 13, esas alertas zombie NUNCA se resuelven -> contaminan el gate '0 alertas abiertas' para siempre). (2) PT/IT onboarding ingenuo — un operador que copie a mano NULL/NULL o un timestamp naive (sin tz, o en hora local) dispara un FLOOD de falsas `:silence`; el helper unico lo previene. (3) no-UE cadencia larga — una fuente con interval enorme (p.ej. dork_municipal 2160h) sigue cumpliendo `interval <= interval+1 < 2*interval`, asi el sentinel (interval+1) es correcto en TODO el rango; debe verificarse sobre {24,168,720,2160}. (4) RUIDO — un timestamp naive vs tz-aware: el `now()` de PG es tz-aware; el helper debe emitir SQL `now() - N*interval` (tz-aware) y NUNCA un datetime Python naive que desfase por zona.

#### (f) Sellado + verificación multi-vía

CRITERIO DE SELLADO + verificacion multi-via:
(a) UNIT aritmetica: `watchdog_safe_seed(_, interval, _)['last_fail_offset_hours'] == interval+1` y se asevera `interval <= offset < 2*interval` para CADA interval en {24,168,720,2160} (cubre todo el rango de cadencias del DISCOVERY_REGISTRY).
(b) INTEGRATION dia-uno: sembrar las filas de un pais fresco -> `_due` las da TODAS como DUE; correr `silence_watchdog` -> CERO `:silence` disparada sobre las filas recien sembradas.
(c) ADVERSARIAL regresion-FR: el `_seed` de discovery ya NO inserta NULL/NULL -> borme_cnae no esta SILENT en el primer ciclo; test de regresion sobre el break exacto.
(d) 2a VIA byte-identidad: la salida del helper para las dos fuentes de 0039 == los literales del migration (24h->25h, 168h->169h) — el camino generico reproduce el camino hecho-a-mano EXACTO, probando que no se introduce drift al generalizar.

#### (g) Herramienta NEXT-LEVEL (€0)

HERRAMIENTA NEXT-LEVEL: Pydantic (MIT, EUR0=True) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587,71]. Modela el country-pack (country.toml + registry + SEMILLAS + lock_key) como un esquema tipado y anade un test de CI que (a) valida cada semilla contra el esquema y (b) asevera el INVARIANTE watchdog-safe `interval <= (now-last_fail) < 2*interval, status='unknown', consecutive_fails=0` como contrato, ademas de la biyeccion source_health<->registry<->lock_key (NEXT-LEVEL.md:585). Convierte una semilla NULL/NULL o un sentinel mal calculado de un hueco SILENCIOSO de onboarding en un build ROJO mecanico, sin DB viva (fixtures), EUR0. Es exactamente el cierre del 'GOBIERNO DE COBERTURA' que el design nombra pero deja aspiracional. Alternativas: frictionless Table Schema (MIT, NEXT-LEVEL.md:40) para validar la FILA de semilla como contrato de datos; jsonschema (validacion declarativa pura) como piso sin tipos Python.

---

<a id="sp-04"></a>
### SP-04 · Lease/heartbeat observable (crashed-vs-vivo)

*Mapa de átomos: faceta 2.*

#### (a) Verificacion de code_hints [VERIFIED]
Todos los hints son exactos contra el codigo real:
- **`_DEFAULT_TTL_MIN = 6`** [VERIFIED pipeline/ops/lock_heartbeat.py:89] y `_DEFAULT_HEARTBEAT_MIN = 2` [VERIFIED :88] — TTL = 3x el latido (comentario :86-89 "Default TTL = 3x the heartbeat interval so a single missed beat never false-positives").
- **`is_lease_stale(...)`** [VERIFIED :141-163] — funcion PURA, sin DB: `None`->stale (:157-158), frontera ESTRICTA `age > timedelta(minutes=ttl)` (:163), TTL via `lease_ttl_minutes()` env `CARDEEP_LEASE_TTL_MIN` (:120-122,:160).
- **`record_heartbeat(...)`** [VERIFIED :170-218] — UPSERT best-effort `INSERT ... ON CONFLICT (lock_key) DO UPDATE` (:192-206) que refresca `holder`/`pid` y resetea `started_at` SOLO cuando el holder/pid cambia (sucesor) (:201-204). `UndefinedTable`->inerte+warning, nunca raise (:212-218).
- **`check_and_clear_stale_lease(...)`** [VERIFIED :259-302] — diagnostico pre-acquire: log **CRITICAL** nombrando holder/pid muerto (:293-301); NO borra fila ni hace `pg_advisory_unlock` (:279-282).
- **`acquire_with_stale_retry(...)`** [VERIFIED :309-338] — `pg_try_advisory_lock` (:331), reintento UNICO solo si lease stale (:334-337).
- **`scheduler_lease(lock_key BIGINT PRIMARY KEY, holder TEXT, pid INTEGER, started_at, last_heartbeat)`** [VERIFIED migrations/0054_scheduler_heartbeat.sql:28-34] — additivo `CREATE TABLE IF NOT EXISTS` (:28), reversible `DROP TABLE` (:42).
- Call-sites: **`record_heartbeat(_lock_conn, _SCHEDULER_SINGLETON_LOCK, holder="harvest")`** [VERIFIED pipeline/ops/scheduler.py:928]; job periodico **`_lease_heartbeat_job` con `args=[_SCHEDULER_SINGLETON_LOCK, "harvest"]`** [VERIFIED :1032-1043], cuerpo modulo-nivel picklable que abre conn, llama record_heartbeat y cierra [VERIFIED :872-892]; discovery **`holder="discovery"`** en acquire [VERIFIED pipeline/discover_schedule.py:255] y en el job-lambda [VERIFIED :262].

#### (b) Mecanismo al atomo
La faceta NO es el mutex (eso es faceta 1) sino la **capa de observabilidad** encima de el. El advisory lock de sesion (0x43415244 harvest / +1 discovery) sigue siendo el unico mutex duro; auto-libera en salida limpia, pero en crash duro PG conserva la sesion muerta y su lock hasta el reaping TCP/idle (lock_heartbeat.py:11-15, 0054 cabecera :3-13). El lease anade una FILA por `lock_key` cuyo `last_heartbeat` el holder vivo bombea cada 2 min. La matematica de frescura es la funcion pura `is_lease_stale` (TTL 6 min = 3x latido): `None` o `age>TTL` => stale. Un sucesor lee la fila (`read_lease` :221-256), y si stale loguea CRITICAL y reintenta el lock UNA vez (`acquire_with_stale_retry`). **Garantia honesta declarada en codigo: observabilidad + retry, NO takeover** (lock_heartbeat.py:24-27,:66-68,:316-328) — `pg_try_advisory_lock` es atomico y NUNCA desplaza a un vivo, asi que el retry no reintroduce el doble-productor AS24. Toda llamada DB es best-effort: sin 0054 la capa es inerte con una sola warning (:345-356), el daemon arranca byte-identico.

#### (c) Costura ES→genérico

El lease es mono-pais por dos atomos: holder es el literal 'harvest'/'discovery' [VERIFIED scheduler.py:928,:1036; discover_schedule.py:255,:262] y la fila se llava por lock_key (PK constante FIJA) [VERIFIED 0054:29]. Costura: nombrar el pais en holder ('harvest:<cc>') es byte-trivial porque holder es texto libre que la UPSERT refresca [VERIFIED lock_heartbeat.py:174,:196]; la distincion de FILA por pais depende de que faceta 1 derive lock_key(rol,pais) — como lock_key es la PK BIGINT, dos lock_keys distintos dan dos filas de lease GRATIS sin tocar 0054. La v_lease_health por pais necesita country_code additivo (espejo 0052) o derivar cc por reverse-map del lock_key.

#### (d) Fix exacto

1) scheduler.py:928 record_heartbeat(..., holder='harvest') -> holder=f'harvest:{country}'. 2) scheduler.py:1036 args=[_SCHEDULER_SINGLETON_LOCK,'harvest'] -> args=[lock_key, f'harvest:{country}'] (mantener literal/picklable, NO closure). 3) discover_schedule.py:255,:262 holder='discovery' -> f'discovery:{country}'. 4) lock_key proviene de la derivacion de faceta 1; scheduler_lease.lock_key (PK) ya distingue filas por pais sin cambio de esquema. 5) (opcional, para v_lease_health) ALTER scheduler_lease ADD country_code CHAR(2) NOT NULL DEFAULT 'ES' (additivo, espejo 0052) o derivar cc del lock_key en la vista. Onboarding: aplicar 0054 es paso obligatorio del checklist.

#### (e) Adversarial — rotura por país

DE/multi-tenant (HIGH si faceta 1 incompleta): holder literal 'harvest' + lock_key no parametrizado => ES y DE pisan la MISMA fila de lease (holder/pid sobrescritos cada latido), un sucesor no sabe que pais murio. Invariante todo-pais: best-effort, NO takeover — un productor muerto-duro espera el reaping de sesion PG; prometer takeover seria mentira [VERIFIED lock_heartbeat.py:24-27,:316-328]. Onboarding: sin 0054 la capa es inerte con UNA warning [VERIFIED :345-356], un pais nuevo pierde diagnosticabilidad del orphan en silencio. Trampa cruzada faceta 16: el heartbeat de discovery es lambda closure [VERIFIED discover_schedule.py:262] valido solo bajo MemoryJobStore; bajo SQLAlchemyJobStore no es picklable y el lease deja de bombear.

#### (f) Sellado + verificación multi-vía

Multi-via: (1) unit puro is_lease_stale (None->stale, age==TTL->no stale frontera estricta, age>TTL->stale) [VERIFIED :141-163]; (2) integracion dos paises lock_key distinto -> ambos adquieren sin bloqueo cruzado, cada lease nombra holder='harvest:<cc>'; (3) adversarial SIGKILL per-pais -> check_and_clear_stale_lease loguea CRITICAL con holder/pid del pais correcto tras TTL, restart re-adquiere tras reaping; (4) v_lease_health: una fila por (pais,rol) con last_heartbeat fresco; (5) inert-path: drop 0054 -> daemon arranca byte-identico, una warning, cero raise.

#### (g) Herramienta NEXT-LEVEL (€0)

Healthchecks (BSD-3-Clause, EUR0) — https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:563]. Dead-man switch EXTERNO con reloj propio: el lease es in-process y ciego a la muerte de su propio proceso/host (Windows 11 unico). Cada heartbeat_tick pinguea una URL de check por (rol,CC); grace=2x cadencia (espeja SILENCE_MULTIPLIER=2); alerta fuera-de-banda si el productor calla. Alternativas [VERIFIED NEXT-LEVEL.md:564]: Uptime Kuma (MIT), ntfy self-host, Apprise (BSD-2-Clause).

---

<a id="sp-05"></a>
### SP-05 · Circuit breaker (trip/cooldown/half-open)

*Mapa de átomos: faceta 9.*

#### (a) Verificacion de code_hints [VERIFIED]
- **`record_run(...)` = UNICO escritor de source_health+source_breaker** [VERIFIED pipeline/ops/health.py:84-129] — docstring :100 "THE single writer". Atomico bajo `async with conn.transaction()` (:130) + `SELECT ... FOR UPDATE` (:138-140,:193-195) que serializa por fuente (sin lost-update del `consecutive_fails`).
- **`BREAKER_TRIP_AT = 3`** [VERIFIED health.py:49] y `BREAKER_COOLDOWN_SEC = 900` (base) [VERIFIED :50].
- **Trip + cooldown exponencial cap 24h** [VERIFIED :215-234]: `depth = new_fails - trip_at` (:224), `cool = min(cooldown_sec * (2 ** depth), 86400)` (:225) — cap 86400s = 24h.
- **`is_open(...)` con sonda half_open** [VERIFIED :443-466]: `state!='open'`->False (:453-454); `cooldown_until IS NULL`->True (:456-457); `now() >= cooldown_until` -> `UPDATE ... SET state='half_open'` y return False (UNA sonda) [VERIFIED :462-464].
- **Histeresis de status** healthy/degraded/down [VERIFIED :176-177] (`DEGRADE_AT=1` :46, `DOWN_AT=3` :47); recuperacion `ok`->closed+reset (:199-214).
- **`source_breaker(source_key TEXT PRIMARY KEY, state CHECK(closed|open|half_open), consecutive_fails, opened_at, cooldown_until)`** [VERIFIED migrations/0013_resilience.sql:19-26] — comentario "One breaker per source_key" (:17). Sin `country_code`.
- **Due-selection re-chequea el breaker INLINE** [VERIFIED scheduler.py:344-384]: `if consecutive_fails >= BREAKER_TRIP_AT: ... continue` (:377-382), `BREAKER_TRIP_AT=3` duplicado en scheduler (:119). NO llama `is_open`, NO lee `cooldown_until`, NO promueve a half_open (comentario :352-354 "to avoid the extra round-trip to source_breaker").

#### (b) Mecanismo al atomo
Maquina de estados de 3 estados sobre una fila por `source_key`. **Un solo escritor real**: `record_run` escribe source_health y source_breaker en la MISMA transaccion, serializado por `FOR UPDATE` (cero corrupcion del contador concurrente). Camino del fallo: `new_fails = prior_fails+1` (:175); si `>= trip_at` => `state='open'`, `cooldown_until = now() + cool` con `cool = min(900 * 2^(new_fails-trip_at), 86400)` (base 900s, x2 por cada fallo mas profundo, cap 24h) (:215-234) — "una fuente que sigue tripeando enfria mas, sin segundo contador". Camino del exito: una corrida limpia cierra el breaker y resetea (:199-214). La **sonda half_open** vive SOLO en `is_open`: tras pasar `cooldown_until` flipea atomico open->half_open y deja pasar exactamente UNA sonda (:458-465). Los umbrales (3, 900s) son globales, override por fuente via `source_health.tuning` JSONB (`fail_threshold`, `cooldown_sec`) leido en cada llamada (:146-149, 0013:62). **Divergencia atomica clave:** el camino de la due-query (scheduler.py:377) NO usa `is_open` — solo salta mientras `consecutive_fails>=3`, sin leer `cooldown_until` ni promover a half_open; la semantica de la sonda existe unicamente en el camino que llama `is_open`.

#### (c) Costura ES→genérico

Breaker country-AGNOSTICO por mecanica (cero literal ES) pero llavado en source_key SOLO [VERIFIED 0013:20 PK; health.py:194,:452]. Dos packs que reusen un source_key pan-EU (as24_wholesale, oem_audi/bmw/kia) COMPARTEN fila de breaker => un fallo DE pone en cuarentena la cosecha IT del mismo modulo. Costura = colision de source_key (compartida con facetas 5/10/13). Segunda costura: los dos caminos del breaker divergen — record_run usa is_open (con sonda half_open) pero la due-query reimplementa consecutive_fails>=3 inline [VERIFIED scheduler.py:377] sin leer cooldown_until ni promover a half_open.

#### (d) Fix exacto

Minimo/honesto: guard de DISJUNCION de source_key cross-pack (faceta 20, test CI Pydantic) => ningun par de packs activos comparte source_key, el breaker keyed-en-source_key no puede fusionar paises; cero cambio de esquema, ES byte-identico. Si un conector pan-EU compartido DEBE servir N paises desde 1 modulo con 1 source_key: ALTER TABLE source_breaker ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES' y swap PK a (country_code, source_key) (espejo 0052/0053); record_run hila country_code en cada WHERE source_key=$1 (health.py:194,:452,:459-464) y en is_open. Unificar la sonda: reemplazar el skip inline consecutive_fails>=BREAKER_TRIP_AT (scheduler.py:377) por una llamada a un espejo sincrono de is_open para honrar half_open identico en ambos caminos.

#### (e) Adversarial — rotura por país

IT/pan-EU (sealing_hole [VERIFIED 0013:20]): dos packs reusando un source_key (as24/OEM) mezclan el estado de breaker de dos paises en silencio; un bloqueo transitorio DE skipea IT. FR/DE divergencia de sonda [VERIFIED scheduler.py:377]: la due-query usa consecutive_fails>=3 inline en vez de is_open, la sonda half_open (health.py:462-464) difiere entre camino harvest y camino conector — una fuente clavada en consecutive_fails=3 se skipea por siempre en el due-path incluso tras pasar cooldown_until. JP/no-UE: trip=3 y cooldown base=900s son globales (health.py:49-50), override solo via tuning JSONB (0013:62) que ningun pack declara hoy.

#### (f) Sellado + verificación multi-vía

Multi-via: (1) unit FSM: 3 fallos->open, exito->closed+reset, cooldown elapsed->half_open (una sonda), sonda-falla->open con cooldown duplicado (math depth=new_fails-trip_at), cap 86400 [VERIFIED health.py:215-234,:443-466]; (2) disjuncion cross-pack: interseccion de source_keys entre packs activos == vacio (CI); (3) adversarial: dos packs con source_key colisionado -> guard ROJO mecanico; (4) paridad de caminos: due-path skip e is_open concuerdan sobre la misma fila (caza la divergencia half_open); (5) idempotencia por pais: con PK compuesta, record_run(DE,key) no toca (IT,key) bajo FOR UPDATE.

#### (g) Herramienta NEXT-LEVEL (€0)

transitions (pytransitions) (MIT, EUR0) — https://github.com/pytransitions/transitions [VERIFIED NEXT-LEVEL.md:595]. El breaker es una FSM de 3 estados hecha a mano, desparramada entre record_run (health.py:199-243) y reimplementada inline en el due-path (scheduler.py:377). transitions la vuelve declarativa + guard-gated (conditions=/unless= mapean cooldown_until/consecutive_fails), unifica ambos caminos bajo un contrato, GraphMachine auto-renderiza el diagrama. Nota honesta: la entrada NEXT-LEVEL apunta primariamente a la FSM cover(CC), pero transitions es la FSM generica y aplica 1:1 a closed/open/half_open. Alternativa: python-statemachine (MIT) [VERIFIED NEXT-LEVEL.md:596].

---

<a id="sp-06"></a>
### SP-06 · Arnés de cadencia APScheduler (jobstore/triggers)

*Mapa de átomos: faceta 16.*

#### (a) Verificacion de code_hints [VERIFIED]
- **`jobstores = {"default": SQLAlchemyJobStore(url=DB_URL)}`** [VERIFIED pipeline/ops/scheduler.py:930-932] + import :904 — persistencia crash-safe de jobs en PG.
- **`BlockingScheduler(jobstores=jobstores, timezone="UTC")`** [VERIFIED :933].
- **Trigger interval del heartbeat** [VERIFIED :938-948]: `trigger="interval"`, `minutes=TICK_INTERVAL_MINUTES`, `replace_existing=True`, `max_instances=1`, `coalesce=True`, `misfire_grace_time=300`.
- **Stagger `start_date`** [VERIFIED :990] — `start_date=datetime.now(timezone.utc) + timedelta(hours=INQUISITION_CADENCE_HOURS, minutes=30)` (offset +30min prosecute tras cadence).
- **`_lease_heartbeat_job` modulo-nivel picklable + args literales** [VERIFIED :1032-1043], comentario explicito :1030 "Module-level picklable job + literal args (the SQLAlchemy jobstore pickles jobs)".
- **Discovery usa MemoryJobStore (default) + lambda closures** [VERIFIED pipeline/discover_schedule.py:256] `BlockingScheduler(timezone="UTC")` SIN arg `jobstores=`; tick lambda :257-259; heartbeat lambda closure :262-264; comentario :260 "MemoryJobStore so the closure is fine".
- **Arnes best-effort try/except por job** [VERIFIED scheduler.py:571-584] — `silence_watchdog_job` con `except Exception` (:579) que loguea y sale limpio "so the scheduler continues" (:566-567); el patron se repite por cada job de mantenimiento (inquisition/gestionador/canonical/product_stats).

#### (b) Mecanismo al atomo
`BlockingScheduler` bloquea el hilo principal hasta SIGINT/SIGTERM, con un `SQLAlchemyJobStore` sobre el PG existente (`DB_URL`) => las DEFINICIONES de job sobreviven un restart de proceso (cadencia crash-safe). `timezone='UTC'` fijo. Cada job: `trigger='interval'` (minutes/hours), `max_instances=1` (nunca dos ticks solapados — el brazo in-process del single-producer), `coalesce=True` (colapsa N ticks perdidos en UNA corrida tras downtime), `misfire_grace_time` (presupuesto de slippage 120-600s), `replace_existing=True` (un cambio de cadencia surte efecto en restart sin limpieza manual de DB). El stagger via `start_date` (:990) desfasa prosecute +30min tras cadence (cadence encola -> prosecute drena). **Restriccion atomica clave:** SQLAlchemyJobStore PICKLEA los jobs, asi que deben ser callables modulo-nivel con args LITERALES — por eso `_lease_heartbeat_job` es funcion top-level alimentada `args=[lock, "harvest"]` (:1032-1036) y NO un closure. El daemon de discovery, en cambio, usa el MemoryJobStore por defecto (discover_schedule.py:256, sin `jobstores=`) y por eso PUEDE usar lambda closures (:257,:262) — pero sus jobs se PIERDEN en restart (no persisten). **Limitacion:** solo triggers de intervalo UTC — no wall-clock/cron, asi que "golpea esta fuente a las 09:00 local" es inexpresable.

#### (c) Costura ES→genérico

La mecanica add_job/interval/jobstore ya es country-agnostica, pero hornea tres supuestos ES: (1) cadencias = constantes de modulo sembradas una vez [VERIFIED scheduler.py:95-116] sin realimentacion del delta; (2) timezone='UTC' + trigger='interval' SOLO [VERIFIED :933,:940] — sin ventana local-time por pais; (3) la picklabilidad del SQLAlchemyJobStore [VERIFIED :930-932,:1030] obliga a pasar el pais como arg LITERAL (como args=[lock,'harvest'] :1036), NO cerrar sobre una variable — el patron lambda de discovery [VERIFIED discover_schedule.py:262] NO generaliza al store persistido.

#### (d) Fix exacto

1) Jobs per-pais picklables: registrar cada job por (rol,pais) bajo SQLAlchemyJobStore pasando country como literal en args=[...] exactamente como scheduler.py:1036 (args=[lock_key, holder]); NUNCA lambda/closure capturando country en el store persistido (el patron discover_schedule.py:262 solo es seguro bajo MemoryJobStore). 2) Cadencia hora-local: para fuentes cuyo pack declare ventana local, registrar con trigger=CronTrigger(timezone=<country_tz>, hour=<h>) en vez de 'interval'; default sigue interval/UTC (byte-identico ES); el pack lleva un campo tz/ventana OPCIONAL (hoy cadencias en HORAS solo). 3) Durabilidad discovery: si los jobs de discovery deben sobrevivir reboot por pais, cambiar discover_schedule.py:256 del MemoryJobStore implicito a SQLAlchemyJobStore y convertir sus lambdas (:257,:262) a funciones modulo-nivel picklables con args literales (espejo scheduler.py:1032).

#### (e) Adversarial — rotura por país

JP/no-UE (MEDIUM [VERIFIED scheduler.py:933,:940]): BlockingScheduler(timezone='UTC')+trigger='interval' no puede expresar golpe a hora LOCAL fija (registro publica 09:00 JST, marketplace throttlea en horario comercial local); el intervalo deriva sobre el ciclo diurno local. DE/cualquiera asimetria crash-safety [VERIFIED]: harvest persiste (SQLAlchemyJobStore :931) pero discovery es en-memoria (MemoryJobStore discover_schedule.py:256) => tras reboot la cadencia discovery se re-siembra desde codigo, harvest reanuda desde PG. Trampa picklabilidad: refactor multi-pais que cierre sobre country en un lambda funciona contra MemoryJobStore pero lanza PicklingError en el SQLAlchemyJobStore de harvest (solo aflora en prod). coalesce=True + downtime largo colapsa N ticks en UNA corrida [VERIFIED :946]; mal compartido entre paises, un pais lento starve a otros en el drenado serie (acopla faceta 6).

#### (f) Sellado + verificación multi-vía

Multi-via: (1) restart-durability: kill -9 al daemon harvest, restart, jobs reaparecen del SQLAlchemyJobStore con ids identicos (replace_existing); mismo test en discovery DEBE mostrar jobs perdidos (asimetria documentada honesta); (2) picklability golden: pickle.dumps(job) por cada job per-pais en CI (caza la trampa del closure); (3) local-time: CronTrigger dispara en el instante UTC correcto cruzando borde DST (PT/IT/FR/DE tienen DST, JP no); (4) byte-identidad ES: sin ventana local, triggers interval/UTC identicos a hoy (golden diff de la tabla de jobs); (5) coalesce/misfire: bajo downtime simulado, UNA corrida no N.

#### (g) Herramienta NEXT-LEVEL (€0)

river (BSD-3-Clause, EUR0) — https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:579]. Cadencias estaticas constantes de modulo (scheduler.py:95-116) sin realimentacion del delta. river: detectores de cambio ONLINE (ADWIN, Page-Hinkley) sobre el stream de filas-cambiadas/run de harvest_run -> fuente aplanada sube harvest_interval_hours, churn lo baja; EUR0 sobre PG, per-CC. ruptures (BSD-2-Clause) change-point OFFLINE para semilla + 2a via; MABWiser (Apache-2.0) explore/exploit [VERIFIED NEXT-LEVEL.md:580]. Complemento adyacente: Procrastinate (MIT) ataca la misma superficie scheduler.py:930 con semantica de TAREA durable (claim/retry/backoff/resume) que APScheduler+jobstore no expresa [VERIFIED NEXT-LEVEL.md:552-556].

---

<a id="sp-07"></a>
### SP-07 · Discovery registry + ADAPTERS como country-pack

*Mapa de átomos: faceta 4.*

#### (a) Verificacion de code_hints [VERIFIED]
- `DISCOVERY_REGISTRY` abre en `discover_schedule.py:65`; 5 entradas `DiscoveryJob` (dataclass frozen `:53-60`, campos source_key/vector/cadence_hours/orthogonal/env/requires_env): `borme_cnae` cadence_hours=24 `:66-68`, `collapse_invisible` 168h `:69-71`, `overture` 720h `:72-73`, `graph_recursive` 720h `:74-76`, `dork_municipal` 2160h con `requires_env=('CARDEEP_SEARXNG_URL',)` `:77-83`. [VERIFIED discover_schedule.py:65-84]
- SEGUNDA superficie oculta: `ADAPTERS` en `discover.py:48-74` = 25 entradas vector->clase Adapter, alimentadas por 25 imports literales de modulo `discover.py:21-42`. Los 5 vectores de cadencia resuelven aqui (borme_cnae->BormeCnaeAdapter `:68`, collapse_invisible->CollapseInvisibleAdapter `:73`, overture->OvertureAdapter `:66`, graph_recursive->GraphRecursiveAdapter `:70`, dork_municipal->DorkMunicipalAdapter `:67`). [VERIFIED discover.py:48-74]
- Comentario '8.132-municipality' en `discover_schedule.py:15`; el docstring de `_gated` cuantifica '8.132 municipalities x 5 templates ~= 40k requests' `:124-125`. [VERIFIED]
- Puente entre superficies: `_tick :186-204` hace `job = DISCOVERY_REGISTRY[key]` y `_run_vector(job) :200`, que lanza `python -m pipeline.discover <job.vector> :166`; el main de `pipeline.discover` resuelve `ADAPTERS[source_key]() :118`. Un vector solo es ejecutable si existe en AMBOS dicts: la cadencia la da DISCOVERY_REGISTRY, el ejecutor lo da ADAPTERS. [VERIFIED]
- `_due :101-117` lee source_health `WHERE source_key = ANY(list(DISCOVERY_REGISTRY)) :104-106` — clavado SOLO en las claves de vector ES.

#### (b) Mecanismo al atomo
Dos registros ES-inlineados independientes con una INVARIANTE de referencia-cruzada (todo vector de cadencia debe estar en el mapa de adapters) que NO se impone en ningun sitio. El registro de cadencia es el 'que + cuando' del scheduler; el mapa de adapters es el 'como ejecutar'. El onboarding del pais #2 = EDITAR ambos literales Python + anadir 25-estilo imports al tope del modulo = reescribir el motor, violando 'country-pack sin reescribir codigo'. El design solo nombra la primera superficie (la cadencia); la segunda (vector->Adapter) queda invisible, asi que un pais nuevo puede recibir cadencia pero quedarse sin ejecutor.

#### (c) Costura ES→genérico

Extraer AMBAS superficies a `get_discovery_registry(country)` y `get_discovery_adapters(country)` en un proveedor `pipeline/ops/registry/` (o `countries/<cc>/discovery.py`). El pack ES (borme_cnae=registro mercantil BORME, dork_municipal=8.132 municipios) vive verbatim en `registry/es.py`. El mapa de adapters debe pasar de imports literales (`discover.py:21-42`) a un registro por entry-point/decorador keyed por pais, para que un pack registre sus adapters SIN editar `discover.py`. Con `active_countries()==['ES']` el merge devuelve dicts byte-identicos a los de hoy (invariante probado por el propio `--dry-run`). Un pais no-UE declara su equivalente registral (Handelsregister / hojin-bango) o lo marca ausente.

#### (d) Fix exacto

1) `pipeline/ops/registry/__init__.py` con `get_discovery_registry(country)->dict[str,DiscoveryJob]`, `get_discovery_adapters(country)->dict[str,type[SourceAdapter]]` y `active_countries()`. 2) Mover los 5 literales `DiscoveryJob` a `registry/es.py`; mover las 25 entradas ADAPTERS + sus imports a un modulo de adapters por-pais expuesto via entry-point o decorador de registro. 3) `discover_schedule.py:65` sustituye el dict modulo-nivel por `DISCOVERY_REGISTRY = merge(get_discovery_registry(cc) for cc in active_countries())`; `discover.py:48` sustituye el literal ADAPTERS por el merge equivalente. 4) `_due :104-106` y `_seed :87-98` iteran el dict merged (sin cambio para ES). 5) Un `model_validator` asegura que todo `DiscoveryJob.vector` del pack tiene clave de adapter en el MISMO pack: el hueco 'cadencia sin ejecutor' pasa a error de carga.

#### (e) Adversarial — rotura por país

[VERIFIED] BREAK Japan: `borme_cnae` y `dork_municipal` son 100% ES (BORME = Boletin Oficial del Registro Mercantil; las plantillas dork asumen nombres de municipio latin-script). Los vectores 'globales' overture/collapse_invisible/graph_recursive asumen datos EU/latinos. Para Japon el eje registral entero puede ser INCONSTRUIBLE a EUR0, pero el design trata discovery como eje siempre-presente. El gate `requires_env=SearXNG` (`:83`) es global pero un dork no-latino necesita plantillas de query distintas que la orquestacion no expresa. Fallo concreto cross-tenant: si PT se onboarda editando SOLO DISCOVERY_REGISTRY (cadencia) y se olvida la entrada ADAPTERS, `pipeline.discover ADAPTERS[source_key] :118` lanza KeyError en el hijo, el padre graba exit!=0 via `_record :201`, y la fuente flapea degraded->down cada cadencia con un opaco 'exit 1' — cadencia sin ejecutor, exactamente el key_concern.

#### (f) Sellado + verificación multi-vía

SELLO = con `active_countries()==['ES']` el DISCOVERY_REGISTRY y el ADAPTERS merged son byte-identicos a los literales de hoy (golden de dict-equality) Y para todo pais activo cada `DiscoveryJob.vector` tiene adapter. Multi-via: (via 1) unit test `get_discovery_registry('ES')==<snapshot congelado>` y `get_discovery_adapters('ES').keys() superset de los vectores de cadencia`; (via 2) el `--dry-run` vivo imprime las mismas 5 filas de cadencia + marcas DUE que la baseline pre-refactor (observable ortogonal `discover_schedule.py:209-227`); (via 3) adversarial — un pack con vector de cadencia sin adapter FALLA el validator en import (build rojo), y un pack que declara adapter sin cadencia se marca ORPHAN. Check de DISJUNCION cross-pack para que dos paises no compartan una clave de vector en silencio.

#### (g) Herramienta NEXT-LEVEL (€0)

Pydantic (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modelar el country-pack (registro de cadencia + mapa de adapters + semillas + lock_key) como un `CountryPack(BaseModel)` tipado con `model_validator` que impone la biyeccion vector-de-cadencia subset claves-de-adapter y la disjuncion de source_key cross-pack; `tests/test_registry_drift.py` itera `active_countries()` y convierte el hueco silencioso 'cadencia sin ejecutor' en build rojo mecanico [VERIFIED NEXT-LEVEL.md:584-590, EUR0, effort S]. Nota honesta de alcance: el doc enmarca este guard Pydantic sobre el registro de HARVEST y su `_gap_report (scheduler.py:394)`; aplicarlo a la doble-superficie de DISCOVERY es el mismo mecanismo extendido al segundo registro que esta faceta posee.

---

<a id="sp-08"></a>
### SP-08 · Watchdog de silencio — DETECCIÓN

#### (a) Verificacion de code_hints [VERIFIED]
- `find_silent_sources` en `silence_watchdog.py:57-98`; SQL `:68-83`; predicado `:80-81`: `now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz) > %(multiplier)s * harvest_interval_hours * interval '1 hour'`; `SILENCE_MULTIPLIER=2 :46`; `ORDER BY hours_silent DESC :82`; devuelve dicts source_key/last_ok/last_fail/harvest_interval_hours/is_tier1/hours_silent `:88-98`. NO hay `country_code` en SELECT ni WHERE [VERIFIED grep count=0 sobre silence_watchdog.py].
- `run_silence_watchdog :174-216` llama find_silent_sources y dispara una alerta dedup por fuente; nunca lanza (try/except por fuente `:196-214`).
- Cableado: `scheduler.py silence_watchdog_job :562-584` — horario, `psycopg2.connect(_RAW_DSN) :572`, `run_silence_watchdog :573`, best-effort try/except `:579-583`.
- CLI read-only: `_check_silence scheduler.py:796-843` — `find_silent_sources :806`, `_redact_dsn(_RAW_DSN) :814`, imprime most-overdue-first, NO dispara nada.

#### (b) Mecanismo al atomo
El watchdog es la SONDA ACTIVA de liveness sobre la tabla PASIVA de salud: caza fuentes invisibles a `record_run` (nunca corrieron / siempre crashean antes de escribir health). 'Silencio' = ultimo evento mas viejo que 2x su PROPIO intervalo; el intervalo por-fuente hace el umbral auto-escalable (una fuente 24h calla a las 48h; un dork 2160h a las 4320h). Es una lectura pura (cero mutacion DB) que alimenta la capa de disparo dedup (facetas 12/13, fuera de scope aqui). El scope de ESTA faceta es la CORRECCION de la deteccion: el predicado, su scoping por pais y el orden.

#### (c) Costura ES→genérico

`find_silent_sources` es un scan GLOBAL de source_health sin predicado de pais. Anadir un parametro opcional: `find_silent_sources(conn, *, countries=None)` que apende `AND country_code = ANY(%(countries)s)` SOLO cuando `countries is not None` (None = universo actual => byte-identico para ES). Hilar el mismo scope por `run_silence_watchdog` y `silence_watchdog_job` / `_check_silence` para que el watchdog de un productor per-pais solo inspeccione SUS filas. Depende de la faceta 5 (country_code en source_health — hoy AUSENTE [VERIFIED 0004 grep=0]).

#### (d) Fix exacto

1) `silence_watchdog.py`: firma `find_silent_sources(conn, *, countries: list[str] | None = None)`; construir el WHERE como predicado base + clausula de pais opcional; el dict de params anade 'countries' solo cuando se pasa. 2) `run_silence_watchdog(conn, *, countries=None)` lo reenvia. 3) `scheduler.py silence_watchdog_job :562` lee un scope (CARDEEP_COUNTRIES o derivado del pack) y lo pasa; `_check_silence :796` igual. 4) Para ES (sin scope) el SQL emitido es identico al de hoy (probado por comparacion de string / EXPLAIN). Sin cambio a SILENCE_MULTIPLIER, al orden, ni a la forma de retorno.

#### (e) Adversarial — rotura por país

[VERIFIED] BREAK France: `find_silent_sources :80-81` escanea source_health con cero filtro de pais. Si FR corre su propio proceso watchdog dispara '<key>:silence' para fuentes ES y ES dispara para FR => alertas cross-tenant DUPLICADAS sobre las MISMAS filas globales; y como la dedup se llava en origin '<source_key>:silence' (`silence_watchdog.py:127` via `_build_origin :105-110`, sin pais en el origin) los dos watchdogs hacen UPDATE-colision sobre UNA fila de alerta para una fuente pan-EU compartida (as24/OEM). Hoy NO hay perilla de scoping que haga correcto un watchdog per-pais. Ruido/no-UE: un pais con intervalos enormes (registral trimestral) queda bajo umbral durante meses — correcto, pero un operador ingenuo lee 'sin silenciadas' como 'sano' cuando la fuente simplemente no alcanzo aun el 2x.

#### (f) Sellado + verificación multi-vía

SELLO = (1) ES con `countries=None` devuelve el mismo set de silenciadas y el mismo SQL que hoy (golden sobre fixture de source_health). (2) Multi-via: (via 1) unit test siembra un fixture de 2 paises (filas ES + DE, una fuente DE silenciada) y asevera que `find_silent_sources(countries=['DE'])` devuelve solo la fila DE, `countries=['ES']` la excluye, `countries=None` devuelve ambas — probando aislamiento y retro-compatibilidad; (via 2) SQL ortogonal: un SELECT directo psycopg2 del predicado con `WHERE country_code='DE'` iguala el conteo de la funcion; (via 3) adversarial: una fuente pan-EU compartida ES+DE con un tenant silenciado debe alzar EXACTAMENTE una alerta scoped por tenant, no una UPDATE-colision cross-tenant (expone la dependencia origin-necesita-derivacion-de-pais de la faceta 13). La deteccion solo sella cuando scan-por-pais == SQL-directo-por-pais para todo pais activo.

#### (g) Herramienta NEXT-LEVEL (€0)

Healthchecks (BSD-3-Clause) — https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:563]. El watchdog in-process NO puede detectar su PROPIA muerte de proceso (host Windows 11 unico, stack hoy CAIDO): si el daemon muere, las ~7 alertas zombie y el lease quedan congelados sin que nadie se entere. Una instancia self-hosted de Healthchecks da un dead-man switch con reloj propio — cada `heartbeat_tick (scheduler.py:519)` hace ping a una URL de check unica por (rol,CC); fallar la grace window (2x cadencia, espejando el `SILENCE_MULTIPLIER=2` ya existente) dispara una alerta fuera-de-banda (ntfy/webhook/email) [VERIFIED 560-566, EUR0, effort S]. Es el vigilante-del-vigilante que esta faceta de DETECCION carece estructuralmente. Alternativas in-doc: Uptime Kuma (MIT) push-monitors, ntfy self-host como canal out-of-band.

---

<a id="sp-09"></a>
### SP-09 · config_guard fail-fast prod + secretos por país

#### (a) Verificacion de code_hints [VERIFIED]
- `config_guard.py`: `assert_safe_dsn :76-106` (lanza RuntimeError SOLO cuando `is_prod()` AND `DEV_CREDENTIAL_MARKER in dsn :99-105`); `require_api_key_or_fail :113-133` (lanza solo `is_prod()` AND key None/vacia `:127-133`); `require_prod_secrets :140-170` (varargs de pares (dsn,var); no-op si `not is_prod() :165-166`; loop `assert_safe_dsn :167-168`; api_key opcional `:169-170`).
- Constantes: `DEV_CREDENTIAL_MARKER='cardeep_dev_only' :44`, `PROD_ENV='prod' :47`, `DEFAULT_ENV='dev' :50`; `cardeep_env()` lee `CARDEEP_ENV` default 'dev' `:57-64`; `is_prod() :67-69`. CERO referencias a pais [VERIFIED grep country_code=0 sobre config_guard.py].
- Cableado: `scheduler.py _start_scheduler :895-903` -> `require_prod_secrets((_RAW_DSN,'CARDEEP_DSN'),(DB_URL,'CARDEEP_DB_URL'),(_ASYNCPG_DSN,'CARDEEP_ASYNCPG_DSN'))` = 3 DSN, `require_api_key` por defecto False; `discover_schedule.py _serve :240/:246` -> `require_prod_secrets((raw,'CARDEEP_DSN_KW'),(_ASYNCPG_DSN,'CARDEEP_ASYNCPG_DSN'))` = 2 DSN.
- `_redact_dsn scheduler.py:81-90` — enmascara la forma kw `password=... :88` y la forma URL `://user:secret@ :89` antes de imprimir en `--dry-run` / `--check-silence (:814)`.

#### (b) Mecanismo al atomo
UN gate validado cableado en las pocas costuras reales de arranque (API lifespan + ambos schedulers), que se ARMA solo si un operador pone `CARDEEP_ENV=prod`, asi dev/test (que nunca lo ponen) son no-op byte-identicos. Rechaza la credencial dev colandose en un DSN prod resuelto y una API key ausente, en vez de reescribir los ~158 defaults DSN hardcodeados. El redactor es el brazo de seguridad-de-impresion para que una password prod jamas aterrice en logs. config_guard YA es country-agnostico: su costura no es parametrizacion sino COBERTURA COMPLETA de la matriz de secretos por pais.

#### (c) Costura ES→genérico

config_guard YA es country-agnostico (valida por env, sin ref a pais) — su costura no es parametrizar sino COMPLETITUD DE COBERTURA sobre la MATRIZ de secretos por pais. Hoy `require_prod_secrets` toma un varargs enumerado a mano en cada entry point; el set es correcto para los 3/2 DSN de ES pero un pais que anada un 4o secreto (endpoint SearXNG, proxy residencial por pais, un DSN de segundo tenant) que nadie cablea se sirve SIN GATE. El fix deriva el manifest de secretos del country-pack para que anadir pais = DECLARAR sus secretos, y el guard itera el manifest declarado en vez de una lista de args literal.

#### (d) Fix exacto

1) Anadir un manifest/Settings tipado por-pais (pydantic-settings) que lista TODO secreto requerido de un pais activo: cada var DSN, cada API key, cada credencial proxy/SearXNG, con field validator que rechaza `DEV_CREDENTIAL_MARKER` en prod y asevera no-vacio. 2) `require_prod_secrets` gana un overload que acepta el manifest para `active_countries()` y recorre cada `(value,var)` declarado bajo el mismo gate `is_prod()` — los entry points dejan de enumerar DSN a mano. 3) Extender/centralizar `_redact_dsn :81-90` para cubrir TODA forma de DSN que un pack introduzca (URL asyncpg, kw libpq, URL de proxy con creds embebidas) para que `--dry-run` nunca filtre. 4) dev/test siguen byte-identicos porque todo el loop del manifest vive dentro de `if not is_prod(): return`.

#### (e) Adversarial — rotura por país

config_guard NO rompe con un pais nuevo (sin ref a pais) — el riesgo adversarial es DRIFT DE COBERTURA. Concreto: onboardar DE con un endpoint SearXNG por-pais `CARDEEP_SEARXNG_URL` que lleva un token embebido y un DSN proxy DE-especifico; ninguno esta en `scheduler.py:899-903` ni `discover_schedule.py:246`, asi que en prod NUNCA se aseveran — un daemon arranca con un proxy dev/placeholder y sirve degradado en silencio, o un token real lo imprime sin redactar `--dry-run` porque `_redact_dsn :88-89` solo casa `password=` y `://user:secret@`, no `?token=...` ni `url=...@`. No-UE/ruido: un DSN de pais en un formato que `_redact_dsn` no reconoce filtra su password en la salida de `--check-silence (scheduler.py:814)`. El gate es honesto pero solo tan ancho como los args que se le entregan.

#### (f) Sellado + verificación multi-vía

SELLO = (1) dev/test byte-identico: con `CARDEEP_ENV` sin setear todo guard + el loop del manifest son no-op (tests existentes pasan sin cambio). (2) Multi-via: (via 1) unit test pone `CARDEEP_ENV=prod` + un manifest de pais con un secreto aun en `cardeep_dev_only` y asevera que `require_prod_secrets` lanza nombrando esa var; manifest real-completo pasa; (via 2) test de cobertura ortogonal: enumerar TODA env var que el pack declara como secreto y aseverar que cada una aparece en el manifest que el guard itera (ningun secreto declarado sin gate) — property test sobre `active_countries()`; (via 3) adversarial de redaccion: pasar TODA forma DSN/credencial del pack por `_redact_dsn` y aseverar que ninguna password-centinela inyectada sobrevive en el string (golden sobre kw, URL, token-query, proxy). El sello se sostiene solo cuando el set de secretos-con-gate == el set de secretos-declarados para todo pais activo Y la redaccion cubre toda forma declarada.

#### (g) Herramienta NEXT-LEVEL (€0)

Pydantic / pydantic-settings (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Pydantic BaseSettings es el validador canonico de config/secretos tipado: modelar la matriz de secretos por-pais como una clase Settings tipada cuyos field validators rechazan el marker dev en prod y aseveran presencia de cada secreto declarado, reemplazando el check de string a mano (`marker in dsn`, `assert_safe_dsn :101`) y convirtiendo 'un pais anadio un 4o secreto que nadie cablea' en un manifest tipado y enumerable que el guard recorre. Nota honesta de alcance: NEXT-LEVEL.md lista Pydantic EXPLICITAMENTE bajo el guard de registry/seed-drift (linea 584), NO bajo config_guard; la misma libreria (y su brazo pydantic-settings) es la elevacion aplicable y doc-presente para esta faceta de matriz-de-secretos — config_guard es por lo demas ya generico, asi que el lift es modesto y aditivo (effort S). Alternativas in-doc: jsonschema / Cerberus para validacion declarativa pura.

---

<a id="sp-10"></a>
### SP-10 · Dimensión país en el esquema de orquestación

*Mapa de átomos: faceta 5.*

#### (a) Verificacion de code_hints [VERIFIED]
- **source_health nace SIN pais:** `migrations/0004_verification_health.sql:24-31` declara `source_health (source_key TEXT PRIMARY KEY, last_ok, last_fail, consecutive_fails, status)` — `source_key` es la PK unica y NO hay columna de pais.
- **La tabla ACRECE columnas, nunca pais:** `0013_resilience.sql:61-62` anade `is_tier1 BOOLEAN DEFAULT FALSE` + `tuning JSONB`; `migrations/0021_harvest_cadence.sql` anade `harvest_interval_hours` ([VERIFIED] por grep: 0021/0024/0039/0051 lo referencian). Tres+ migraciones tocan source_health y NINGUNA introduce `country_code`.
- **source_breaker** `0013_resilience.sql:19-26`: `source_breaker (source_key TEXT PRIMARY KEY, state, consecutive_fails, opened_at, cooldown_until)` — PK source_key, sin pais. El comentario :17-18 lo declara "one breaker per source_key".
- **harvest_run** `0013_resilience.sql:30-40`: `source_key TEXT NOT NULL`, indice `idx_harvest_run_source (source_key, started_at DESC)` :40 — sin pais.
- **scheduler_lease** `0054_scheduler_heartbeat.sql:28-34`: keyed por `lock_key BIGINT PRIMARY KEY`, sin pais.
- **alert** `0004:34-45`: `origin TEXT NOT NULL`, `idx_alert_origin` :44, `idx_alert_unresolved` :45 — origin libre, sin pais.
- **grep `country_code` en `pipeline/ops/` => CERO matches [VERIFIED]** — el plano de orquestacion entero es country-blind.
- **El patron a espejar EXISTE y esta probado:** `0052_country.sql:49-54` anade `country_code CHAR(2) NOT NULL DEFAULT 'ES'` al geo backbone + entity (el DEFAULT estampa las 431.211 filas como ES, backfill implicito cero-NULL, doc :20-23); `0053_country_onboarding.sql:64-91` hace el swap diferido a PK compuesta `(country_code, code)` re-escribiendo 6 FKs a compuestas. La decision YAGNI de diferir el swap a una migracion separada esta documentada en `0052:25-31` (items a/b/c).
- **Colision pan-EU REAL:** `as24_wholesale` `scheduler.py:192` (autoscout24, DE-origen sirviendo IT/AT/...), `oem_audi_wholesale` :255, `oem_bmw_premium_selection_wholesale` :258, `oem_ford_wholesale` :264, `oem_hyundai_wholesale` :266, `oem_kia_wholesale` :268 — UN modulo / UN source_key sirve multiples paises.

#### (b) Mecanismo al atomo
La etapa de orquestacion mantiene CUATRO tablas de estado (source_health, source_breaker, harvest_run, scheduler_lease) mas `alert`, todas keyed por `source_key` (o `lock_key`/`origin`) como **identidad GLOBAL plana**. El plano de IDENTIDAD geo ya es country-aware desde 0052/0053, pero el plano de ORQUESTACION quedo atras: la salud, el breaker, el audit y el lease de una fuente NO saben de que pais son. Mientras ES es el unico tenant esto es correcto-por-vacuidad (todo es ES). El atomo del fallo es la PK `source_key`: es el punto fisico donde dos paises que comparten una fuente pan-EU colapsan en una sola fila.

#### (c) Costura ES→genérico

source_health(0004:25)/source_breaker(0013:20)/harvest_run(0013:32)/scheduler_lease(0054:29)/alert(0004:36) todas keyed por source_key|lock_key|origin SIN country_code (grep pipeline/ops = 0 matches); el geo ya es country-aware (0052/0053) pero el plano de orquestacion quedo atras.

#### (d) Fix exacto

Migracion additiva 0057 espejo de 0052: ALTER ... ADD COLUMN country_code CHAR(2) NOT NULL DEFAULT 'ES' en las 5 tablas (DEFAULT estampa ES byte-identico, doc 0052:20-23); declarar convencion source_key <plataforma>_<cc> como invariante duro; diferir PK compuesta (country_code,source_key) hasta colision real (YAGNI 0052->0053); indices country-scoped espejo 0052:80-81.

#### (e) Adversarial — rotura por país

[VERIFIED] BREAK Italy/Germany: source_key PK unica (0004:25) + fuentes pan-EU compartidas (as24_wholesale :192, oem_audi/bmw/kia :255-269) => sembrar fila IT/DE para la misma fuente colisiona en PK, ON CONFLICT(source_key) conserva ES en silencio, IT/DE sin salud/breaker/cadencia independientes. PT/FR heredan al reusar un OEM paneuropeo; semilla foranea sin country_code = fila global indistinguible.

#### (f) Sellado + verificación multi-vía

count(*) source_health WHERE country_code<>'ES'==0 (byte-identidad) + columna DEFAULT 'ES' en \d; via dry-run golden ES sin cambio en mapped/unmapped; via SQL directo == conteo dry-run (todas ES); via adversarial: insert (as24_wholesale,'DE') colisiona con PK simple y convive con PK compuesta; rollback DROP COLUMN limpio sin filas non-ES (espejo 0053:177-181).

#### (g) Herramienta NEXT-LEVEL (€0)

pycountry (ISO 3166-1/-2 + ISO 4217) LGPL-2.1 EUR0 https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:64,530] — valida country_code CHAR(2) contra ISO 3166-1 alpha-2 (autoridad, no string libre), ISO 3166-2 para subdivisiones del grain geo, ISO 4217 para moneda del pack; alt iso3166 MIT countries-only [VERIFIED NEXT-LEVEL.md:531].

---

<a id="sp-11"></a>
### SP-11 · Resolución del zombie `:silence` (bug raíz)

*Mapa de átomos: faceta 12.*

#### (a) Verificacion de code_hints [VERIFIED]
- **El watchdog DISPARA ':silence' pero el lazo de resolucion NO existe:**
  - `silence_watchdog.py:127` `origin = _build_origin(source_key, "silence")` — la fase del origin es el literal `"silence"`.
  - `silence_watchdog.py:174-216` `run_silence_watchdog` SOLO llama `find_silent_sources` (:181) + `fire_silence_alert_sync` (:197) por cada fuente callada; NO hay NINGUNA llamada de resolucion.
  - `fire_silence_alert_sync` :113-167 hace dedup (SELECT abierto :143-148 -> UPDATE :153-156 / INSERT :158-162) pero nunca cierra.
- **El UNICO resolutor automatico es por fase de RUN, no de silencio:**
  - `health.py:172-173` en `record_run` con `ok=True`: `_ok_origin = build_origin(source_key, phase); await resolve_alerts(conn, _ok_origin)`. El comentario :169-171 lo acota: "a scrape success resolves scrape alerts only". `phase` aqui es scrape/discover — NUNCA "silence".
  - `build_origin` :289-292 y `resolve_alerts` :327-333 cierran por `origin` exacto.
- **Ningun caller resuelve ':silence':** grep `resolve_alerts` => `ingest.py:163` (`as24:gone_guard`), `coverage_verify.py:333` (coverage_origin), `group_subastas_wholesale.py:1013` / `localizavo_wholesale.py:820` / `subastacar_wholesale.py:810` (todos `:gone_guard`), `health.py:173` (scrape/discover). **CERO tocan `:silence`** [VERIFIED].
- **Tests:** `tests/test_silence_watchdog.py` — clases `TestSilencePredicate` (:84), `TestBuildOrigin` (:169), `TestFireSilenceAlertSync` (:205), `TestRunSilenceWatchdog` (:296), `TestFindSilentSourcesLiveDB` (:442). TODAS son deteccion/dedup/fire; **CERO test de recuperacion/resolucion** [VERIFIED].

#### (b) Mecanismo al atomo
El alert lifecycle tiene DOS bordes: **fire** (abre) y **resolve** (cierra por origin). El borde fire del silencio existe (`fire_silence_alert_sync`); el borde resolve NO. **Causa raiz al atomo:** `record_run` solo cierra el origin de SU fase (`<key>:scrape` / `<key>:discover`), pero el silencio vive en un origin DISTINTO (`<key>:silence`) que ningun `record_run` produce. Asi una fuente que se recupera (sube `last_ok`, deja de cumplir el predicado `now()-COALESCE(last_ok,last_fail,'1970') > 2*interval`) cierra su alerta de scrape pero deja su `:silence` ABIERTA para siempre. Resultado observado: ~7 zombies acumulados.

#### (c) Costura ES→genérico

Bug del motor (no de pais): el borde 'resolve' del silencio NO existe. record_run cierra solo build_origin(source_key,phase) phase in {scrape,discover} (health.py:172-173), pero el silencio vive en origin '<key>:silence' (silence_watchdog.py:127) que ningun record_run produce; run_silence_watchdog (:174-216) solo detecta+dispara; ningun caller de resolve_alerts toca ':silence'.

#### (d) Fix exacto

Nueva resolve_recovered_silence_alerts: UPDATE alert SET resolved_at=now() WHERE origin LIKE '%:silence' AND resolved_at IS NULL AND NOT EXISTS(<predicado silencio identico a find_silent_sources :68-83>); cablear en run_silence_watchdog ANTES del fire (resolver-recuperadas->disparar-nuevas). El NOT EXISTS debe espejar EXACTO SILENCE_MULTIPLIER=2 (:46) + COALESCE(...,'1970') o la alerta flapea. Pais derivado por JOIN a source_health.country_code, SIN prefijar origin.

#### (e) Adversarial — rotura por país

[VERIFIED] sealing_hole: cada corte transitorio deja una ':silence' abierta para siempre (~7 zombies hoy); con N paises cada corte deja N zombies y sin country_code en alert no se distinguen => gate '0 alertas abiertas' INALCANZABLE en todo pais. Flapeo si multiplier!=2 o COALESCE difiere (banda interval..2*interval oscila cada hora); ruptura cruzada si _build_origin sync (silence_watchdog.py:105) diverge de build_origin async (health.py:289).

#### (f) Sellado + verificación multi-vía

End-to-end: callada->fire :silence; record_run(ok) sube last_ok; siguiente ciclo RESUELVE; count(:silence abiertas) recuperada->0. Via test recuperacion (hoy CERO en test_silence_watchdog.py, solo deteccion/dedup/fire); via idempotencia 2x sin oscilar; via espejo-predicado (silent XOR resolvible); via live ~7->solo las realmente calladas.

#### (g) Herramienta NEXT-LEVEL (€0)

Healthchecks (dead-man switch EXTERNO) BSD-3-Clause EUR0 https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:68,563] — auto-resuelve al reanudar el ping (el borde resolve que falta) y vigila al vigilante (si el scheduler muere el reloj independiente dispara igual). Verif NEXT-LEVEL.md:566 (detener daemon->dispara; 'down' vs scheduler_lease.last_heartbeat; reloj-deriva no engana). Self-host Docker.

---

<a id="sp-12"></a>
### SP-12 · Supervisor de proceso + artefactos de durabilidad

#### (a) Verificacion de code_hints [VERIFIED]
- **Artefacto Linux REAL y versionado:** `ops/systemd/cardeep-harvest.service` — `Type=simple` :31, `WorkingDirectory=/opt/cardeep` :34, `EnvironmentFile=/etc/cardeep/cardeep.env` :44 (**UN solo** EnvironmentFile, no por pais), `ExecStart=/opt/cardeep/.venv/bin/python -m pipeline.ops.scheduler` :46, `KillSignal=SIGTERM` :50 (salida limpia libera el advisory lock, comentario :48-49), `Restart=always` :53, `RestartSec=10` :54. Hardening NoNewPrivileges/PrivateTmp/ProtectSystem :57-59. El comentario :8-15 declara que el single-instance lo garantiza el advisory lock `0x43415244` en PG, **NO el host**.
- **Windows = SOLO PROSA:** `docs/DEPLOY-DURABLE-DAEMONS.md` §3 "Host actual Windows 11 — Task Scheduler / NSSM" :200-280. Dos rutas: NSSM (recomendado :210) y schtasks. Comandos `nssm install cardeep-harvest $PY "-m pipeline.ops.scheduler"` :230, `nssm set cardeep-harvest AppExit Default Restart` :232 (= equivalente Windows de `Restart=always`, declarado :247), `schtasks /Create /TN "cardeep-harvest" ... /SC ONSTART` :270. Todo inline en markdown, NINGUN fichero ejecutable.
- **`find ops/` => solo `ops/systemd/*` (api/discovery/harvest) + `ops/searxng/*`. NO existe `ops/windows/`** [VERIFIED]. El host real es Windows 11 (env verificado).
- **Per-pais ausente:** las units actuales NO estan instanciadas por pais (no hay template `cardeep-harvest@.service` ni EnvironmentFile por CC); `$ROOT` (Windows) y `/opt/cardeep` (Linux) son single-tenant.

#### (b) Mecanismo al atomo
El supervisor da DOS garantias: (1) **restart-on-crash** (`Restart=always` / `AppExit Default Restart`) y (2) **start-on-boot** (`WantedBy=multi-user.target` / schtasks ONSTART). El single-instance NO lo da el supervisor — lo da el advisory lock en PG (`scheduler.py:913` `_SCHEDULER_SINGLETON_LOCK`); en salida limpia SIGTERM cierra la conexion y libera el lock, en crash duro PG recolecta la sesion. **Atomo del fallo:** en el host REAL (Windows 11) la unica ruta de persistencia viva es NSSM, y NSSM se configura por comandos imperativos (`nssm set ...`) cuya config vive en el **registro de Windows**, NO en un artefacto repo-versionado. No hay golden de paridad cross-OS ni cobertura CI del "sobrevive al reboot".

#### (c) Costura ES→genérico

Durabilidad real = solo units systemd Linux (/opt/cardeep; cardeep-harvest.service: Restart=always:53, KillSignal=SIGTERM:50, EnvironmentFile unico:44); el host real es Windows 11 donde la persistencia viva es NSSM, configurado por comandos imperativos (DEPLOY §3:200-280, AppExit Default Restart:232, schtasks ONSTART:270) cuya config vive en el registro, NO en un artefacto. find ops/ => no existe ops/windows.

#### (d) Fix exacto

Commitear ops/windows/cardeep-harvest.xml (WinSW) espejo 1:1 de la unit systemd: executable python -m pipeline.ops.scheduler, onfailure restart, <env CARDEEP_COUNTRY=%CARDEEP_COUNTRY%>, workingdirectory $ROOT, SIN ampersand; install idempotente winsw install. Multi-pais: template cardeep-harvest@<CC>.service + EnvironmentFile /etc/cardeep/<CC>.env (Linux) y un XML id cardeep-harvest-<CC> (Windows). Single-instance lo sigue dando el advisory lock (per-pais lock_key faceta 1).

#### (e) Adversarial — rotura por país

[VERIFIED] sealing_hole: artefactos solo systemd Linux pero host real Windows 11 => deriva doc-vs-realidad; sin XML commiteado un reinstall pierde la config NSSM (vive en registro) y el daemon NO vuelve => 'sobrevive al reboot' indemostrable. EnvironmentFile unico (:44) mezcla secretos multi-pais; un DSN/proxy de pais nuevo sin env propio no arranca o no aisla. schtasks+NSSM a la vez => 2o SystemExit por el lock (solo el lock salva, el supervisor no coordina).

#### (f) Sellado + verificación multi-vía

NEXT-LEVEL.md:574: (a) reboot/stop forzado => arranque automatico + readquisicion limpia del lock; (b) diff semantico XML WinSW vs unit systemd (env/paths/restart/killsignal) golden de paridad cross-OS, CI falla si divergen; (c) matar el proceso => restart, sin double-produce (2o intento SystemExit). Via existencia test -f ops/windows/cardeep-harvest.xml (hoy FALLA); via no-double-produce lanzar manual => SystemExit del advisory lock.

#### (g) Herramienta NEXT-LEVEL (€0)

WinSW (Windows Service Wrapper) MIT EUR0 https://github.com/winsw/winsw [VERIFIED NEXT-LEVEL.md:69,571] — servicio Windows definido por XML REPO-VERSIONADO (cierra el hueco NSSM-prosa: NSSM vive en el registro, no es artefacto), parametrizable por %CARDEEP_COUNTRY%, espeja 1:1 la unit systemd para golden cross-OS. Alt: Shawl (Rust, MIT) https://github.com/mtkennerly/shawl [VERIFIED NEXT-LEVEL.md:572].

---

<a id="sp-13"></a>
### SP-13 · Harvest registry como country-pack cargable

*Mapa de átomos: faceta 3.*

#### (a) Verificación de code_hints [VERIFIED]
- `class SourceEntry(NamedTuple)` con campos `source_key / module / extra_args` [VERIFIED scheduler.py:144-147].
- `_build_registry()` construye una LISTA de ~50 literales `SourceEntry` inline y retorna `{e.source_key: e for e in entries}` [VERIFIED scheduler.py:150-326].
- `REGISTRY: dict[str,SourceEntry] = _build_registry()` se materializa UNA vez en import-time [VERIFIED scheduler.py:330].
- Entradas pan-EU inlineadas: `as24_wholesale`->autoscout24_wholesale [VERIFIED :192-193]; `oem_audi_wholesale` [VERIFIED :255-256]; `oem_bmw_premium_selection_wholesale`/`oem_mini_next_wholesale` via `--brand bmw|mini` [VERIFIED :258-263]; `oem_ford/hyundai/kia` [VERIFIED :264-269]. Modulos multi-source desambiguan por `extra_args` (`--member`/`--members`/`--brand`), p.ej. los 6 `group_rentacar_vo_*` comparten `group_rentacar_vo_wholesale` con `--member <suffix>` [VERIFIED :211-228].
- `_run_source` lee `entry = REGISTRY[source_key]` [VERIFIED :422]; `heartbeat_tick` hace `if source_key not in REGISTRY: ... continue` [VERIFIED :544-549].
- `UNMAPPED_KEYS: frozenset[str] = frozenset()` [VERIFIED :337]; `_gap_report` compara `all_keys` contra el REGISTRY global unico [VERIFIED :394-398].
- Live: `source_health` PK = `source_key` (columna unica) [VERIFIED live DB :5433]; `entity` 450.652 filas TODAS `country_code='ES'` [VERIFIED live DB].

#### (b) Mecanismo al átomo
1. **Import-time**: Python importa scheduler.py -> corre `_build_registry()` una sola vez -> devuelve un dict-literal de 50 entradas -> queda ligado al global de modulo `REGISTRY`. El literal ES *es* el motor.
2. **Identidad de entrada**: cada `SourceEntry=(source_key, module, extra_args)`. El `source_key` se mantiene IGUAL al `*_SOURCE_KEY` que el conector escribe en source_health para que health/breaker/harvest_run/due-selection casen (continuidad declarada en el comentario :161-164).
3. **Runtime**: `heartbeat_tick` -> `_due_sources(DB)` devuelve source_keys due -> por cada uno `if not in REGISTRY: SKIP` -> si esta, `_run_source` -> `REGISTRY[source_key]` -> `_build_cmd=[py,-m,module,*extra_args]` -> subprocess. NO hay eje pais ni costura de carga dinamica: el dict es el unico mapa autoritativo source_key->argv.

#### (c) Costura ES→genérico

El roster ES es un literal Python soldado dentro del modulo-motor (scheduler.py:156-325). Onboarding del pais #2 = EDITAR ese literal = reescribir codigo del motor, violando 'country-pack sin reescribir codigo'. Costura: introducir un proveedor `pipeline/ops/registry/` con `get_harvest_registry(country)->dict[str,SourceEntry]` y `active_countries()->list[str]`; mover las ~50 entradas ES VERBATIM (cero ediciones a cualquier SourceEntry) a `registry/es.py`; `REGISTRY` pasa a ser el merge de `get_harvest_registry(c) for c in active_countries()`.

#### (d) Fix exacto

1) `pipeline/ops/registry/__init__.py` expone `get_harvest_registry(country)`, `active_countries()` (allowlist, default `['ES']`) y `build_registry()` que mergea los packs activos. 2) `pipeline/ops/registry/es.py` aloja la lista ES verbatim (el cuerpo actual scheduler.py:156-325 movido 1:1). 3) En scheduler.py reemplazar `REGISTRY=_build_registry()` por `REGISTRY=build_registry()`; con `active_countries()==['ES']` el merge devuelve un dict BYTE-IDENTICO (invariante probado por --dry-run/golden ya existente). 4) `SourceEntry` queda intacto (o se promueve al modelo Pydantic del pack — ver tool). 5) GUARD de merge: lanzar excepcion ante `source_key` duplicado entre packs (disjuntez cross-pack: breaker/health/crash-net se llavan TODOS en source_key, asi que una colision fusiona dos paises en silencio).

#### (e) Adversarial — rotura por país

[VERIFIED BREAK Portugal] `_build_registry()` inlinea ~50 SourceEntry ES (scheduler.py:156-325); onboarding PT hoy = EDITAR el dict Python = reescribir el motor. No existe seam de carga dinamica. | [DE/IT/FR colision pan-EU] `as24_wholesale` (:192), `oem_audi/bmw/kia/ford/hyundai` (:255-269) son UN modulo que sirve varios mercados; si un pack DE y el pack ES declaran ambos `as24_wholesale`, el merge ingenuo `{e.source_key:e}` sobreescribe en silencio (last-wins) y, como source_health PK=source_key (VERIFIED live), comparten health/breaker/crash-net -> el merge DEBE rechazar el duplicado o forzar el naming `<plataforma>_<cc>` (faceta 5). | [non-EU/ruido Japon] un pack JP cuyos conectores aun no existen sembraria filas source_health que no mapean a ninguna entrada -> heartbeat_tick las SKIP por siempre (:544-549) = never-harvest silencioso salvo que el gate de drift (faceta 20) ponga el build en ROJO.

#### (f) Sellado + verificación multi-vía

Sello = 'con active_countries()==[ES] el dict mergeado es byte-identico al REGISTRY de hoy'. | Via 1 (codigo): `assert build_registry()==_build_registry()` con el literal viejo conservado como golden durante la transicion. | Via 2 (ortogonal, live): los conteos mapped/unmapped del `_gap_report` en --dry-run ANTES vs DESPUES del refactor deben coincidir exacto (delta 0) contra la source_health viva. | Via 3 (adversarial): un 2o pack sintetico reusando un source_key ES debe LANZAR en el merge (test de disjuntez); un 2o pack con keys disjuntos debe mergear limpio y crecer el dict exactamente su propio tamano. | Cross-ref live: entity 450.652 todas ES (VERIFIED) -> cualquier fila no-ES es neta-nueva, asi que el invariante de identidad-ES es hoy trivialmente satisfacible.

#### (g) Herramienta NEXT-LEVEL (€0)

Pydantic (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela el country-pack (registry + semillas + lock_key) como esquema TIPADO validado en LOAD: `SourceEntry`->`BaseModel` con validators (source_key unico, module importable, country_code presente), de modo que onboarding de un nuevo `registry/<cc>.py` es type-checked en vez de confiado a mano; el mismo modelo alimenta el gate CI de biyeccion de la faceta 20 (source_health<->registry<->lock_key, 0 UNMAPPED/0 ORPHAN, disjuntez cross-pack). Alternativas [VERIFIED NEXT-LEVEL.md:588]: jsonschema, Cerberus, dataclasses+asserts (piso). Frictionless Framework (MIT, NEXT-LEVEL.md:337) es la variante data-package si el pack se externaliza a TOML/CSV.

---

<a id="sp-14"></a>
### SP-14 · Red de seguridad crash-before-record_run

*Mapa de átomos: faceta 10.*

#### (a) Verificación de code_hints [VERIFIED]
- `_harvest_run_max_id(source_key)` -> `SELECT coalesce(max(id),0) FROM harvest_run WHERE source_key=%s` [VERIFIED scheduler.py:448-462]; ante fallo de query devuelve `None` -> 'record unconditionally below (better an extra alert than silence)' [VERIFIED :465-467].
- `_record_crash_if_unrecorded(source_key, exit_code, pre_max_id)` [VERIFIED scheduler.py:470-513]: abre asyncpg; si `pre_max_id is not None` hace `newest = SELECT coalesce(max(id),0) FROM harvest_run WHERE source_key=$1` [VERIFIED :490-493]; gate `if int(newest) > pre_max_id: return False  # connector wrote its own record_run this cycle` [VERIFIED :494-495]; si no, `await record_run(conn, source_key, ok=False, error=...)` [VERIFIED :496-501].
- Sitio de llamada en `heartbeat_tick`: `pre_max_id=_harvest_run_max_id(source_key)` ANTES de lanzar [VERIFIED :550]; `exit_code=_run_source(...)` [:551]; `if exit_code != 0: _record_crash_if_unrecorded(source_key, exit_code, pre_max_id)` [VERIFIED :552-553].
- Live: columnas harvest_run = `id, source_key, started_at, finished_at, ok, rows, error, http_status` — SIN country_code, CON source_key [VERIFIED live DB :5433]; source_health PK = source_key [VERIFIED live DB].

#### (b) Mecanismo al átomo
1. **Pre-lanzamiento**: capturar high-water `H0 = max(harvest_run.id) WHERE source_key` — el ancla de idempotencia.
2. **Lanzamiento**: subprocess; el conector OWNS su propio record_run en toda ruta normal (el scheduler NO lo escribe) [VERIFIED :473].
3. **Post-exit!=0**: releer high-water `H1`. Si `H1>H0` -> aparecio una fila harvest_run nueva -> el conector grabo su propio resultado -> `return False` (NO doble-contar). Si `H1==H0` -> nada aparecio -> el conector murio antes de su record_run (SIGKILL por timeout / fallo de lanzamiento / crash temprano) -> el scheduler graba el fallo el mismo con `record_run(ok=False)` para enganchar health/breaker y que el watchdog de 2x-intervalo no sea la unica red.
4. **Ruta degenerada**: si la query H0 fallo (`None`), se salta el gate y se graba incondicionalmente [VERIFIED :467].

#### (c) Costura ES→genérico

La clave de idempotencia es `source_key` SOLO (tanto la query pre-lanzamiento como la post-mortem filtran `WHERE source_key=$1`, sin pais). harvest_run no tiene country_code (VERIFIED live). Cuando dos packs reusan un source_key pan-EU, el high-water MEZCLA las filas harvest_run de ambos paises: ES escribe id=N+1 mientras DE crasheo -> la post-mortem de DE ve H1=N+1 > H0=N y concluye erroneamente 'el conector escribio' -> el crash de DE queda SIN GRABAR, el breaker nunca dispara, y solo el watchdog de 2x-intervalo lo nota.

#### (d) Fix exacto

1) Anadir country_code a harvest_run, additivo, espejando 0052: `ALTER TABLE harvest_run ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` + indice; rollback comentado reversible (plantilla 0052 VERIFIED migrations/0052_country.sql:49-91). 2) Hilar pais por la crash-net: `_harvest_run_max_id(source_key, country)` y el fetch post-mortem ganan `AND country_code=$2`; record_run estampa country_code. 3) Hasta la promocion a PK compuesta (faceta 5), el gate high-water pasa a `WHERE source_key=$1 AND country_code=$2`, de modo que dos packs que comparten un source_key pan-EU mantienen high-waters disjuntos. 4) Byte-identidad: con DEFAULT 'ES' y un unico tenant ES, todo resultado de query queda inalterado (el predicado anadido `country_code='ES'` selecciona las mismas filas).

#### (e) Adversarial — rotura por país

[VERIFIED sealing_hole] high-water llavado en source_key solo (scheduler.py:489-495); harvest_run sin country_code (VERIFIED live). Dos packs reusando un source_key (pan-EU as24/OEM) mezclan filas harvest_run -> falso-negativo de la crash-net para el pais crasheado. | [DE/IT/FR concreto] el host-lock unico fuerza UN productor drenando todos los paises en serie (faceta 1); dentro de UN tick la run as24 de ES y una hipotetica run as24 de DE escriben al MISMO high-water de source_key -> el crash del perdedor se mis-atribuye como 'grabado'. | [non-EU/ruido] un conector que sale 0 pero nunca escribio record_run (no-op silencioso) NO se captura aqui (el gate solo dispara con exit!=0) — ortogonal al pais pero un punto-ciego real; y una DB que flapea (la query harvest_run falla) graba incondicionalmente -> alertas duplicadas, aceptable-por-diseno (fallar hacia ruido, no hacia silencio).

#### (f) Sellado + verificación multi-vía

Sello = 'un crash-before-record_run engancha health/breaker exactamente una vez, scopeado al pais que crashea'. | Via 1 (unit): pre_max_id=N, conector no escribe nada, exit=-1 -> record_run llamado UNA vez (H1==H0). pre_max_id=N, conector escribe id=N+1, exit=1 -> record_run NO llamado (cero doble-conteo). Ambos ya testables; anadir asercion de dimension pais. | Via 2 (SQL ortogonal): tras un crash forzado, `SELECT count(*) FROM harvest_run WHERE source_key=$1 AND country_code=$2 AND ok=false` incrementa exactamente 1; una run cross-pais NO incrementa el conteo del otro pais (disjuntez). | Via 3 (adversarial): dos packs con el MISMO source_key pero distinto pais deben mantener high-waters independientes — el test debe FALLAR en el gate source_key-only de hoy y PASAR tras el predicado de pais (prueba que el fix cierra el hueco, no que solo pasa).

#### (g) Herramienta NEXT-LEVEL (€0)

Procrastinate (MIT) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555]. Reemplaza el 'captura high-water -> reconcilia tras exit' hecho a mano por una TAREA durable Postgres-nativa: claim idempotente via FOR UPDATE SKIP LOCKED, retry con backoff exponencial por tarea, y un worker que reanuda a mitad de vuelo tras un crash — asi 'crash before record_run' pasa a ser 'task failed', grabado atomicamente por la cola sin reconciliacion custom. Corre sobre el PG existente (:5433), cero infra nueva [VERIFIED NEXT-LEVEL.md:557]. Alternativas [VERIFIED NEXT-LEVEL.md:556]: DBOS Transact (MIT), pgqueuer (MIT, mas ligero LISTEN/NOTIFY+SKIP LOCKED), Hatchet (MIT); Temporal descartado como piso (cluster separado, no EUR0). Verificacion que aporta [VERIFIED :558]: matar el worker a mitad de CLAIMED y confirmar completado exactamente-una-vez; contar eventos append-only == transiciones esperadas via SQL directo.

---

<a id="sp-15"></a>
### SP-15 · Jobs de mantenimiento + auditoría de agregación cross-país

#### (a) Verificación de code_hints [VERIFIED]
- Jobs de mantenimiento registrados en `_start_scheduler`: `gestionador_detect_job` [VERIFIED scheduler.py:1002-1012], `canonical_key_backfill_job` [VERIFIED :1017-1027], `_lease_heartbeat_job` [VERIFIED :1032-1043], `_refresh_product_stats_job` [VERIFIED :1048-1058], `inquisition_cadence/prosecute` [VERIFIED :968-997], `silence_watchdog` [VERIFIED :953-963].
- Cohort price_trap `_price_trap`: CTE base `FROM vehicle WHERE status='available' AND price IS NOT NULL AND price>0 AND make IS NOT NULL AND year IS NOT NULL`, `GROUP BY make, model, year`, robust-z `(b.lp - mad.med_lp)/(1.4826*mad.mad_lp)` [VERIFIED detect.py:773-814]; SIN JOIN a entity y SIN country_code en la pasada cohort. Tiers `PRICE_TRAP_COHORT_MIN_A=15` (make,model,year) / `MIN_B=30` (make,year) [VERIFIED detect.py:102-103].
- Sub-detector OOB de price_trap SI hace `JOIN entity e ON e.entity_ulid=v.entity_ulid WHERE v.status='available'` pero solo por cdp_code, sin country_code [VERIFIED detect.py:559-573].
- `_refresh_product_stats_job` -> `scripts.refresh_product_stats.refresh`; product_stats es cache de UNA fila (PK SMALLINT CHECK id=1), columnas dealers/vehicles_unique_available/events/provinces/municipalities — SIN country_code [VERIFIED migrations/0055_product_stats.sql:14-22].
- `canonical_key_backfill` `_SELECT` es per-fila por entity_ulid (LEFT JOIN LATERAL entity_source, sin GROUP BY, sin agregacion pais) -> SEGURO [VERIFIED canonical_key_backfill.py:29-38].
- Live: vehicle NO tiene country_code (derivable via entity_ulid->entity per 0052:36-38) [VERIFIED live DB :5433]; entity 450.652 todas ES [VERIFIED live DB].

#### (b) Mecanismo al átomo
1. **add_job** es country-AGNOSTICO y seguro: cada job es una fn picklable de modulo-nivel sobre trigger interval. El RIESGO vive ENTERO en el SQL que cada job corre.
2. **price_trap**: una pasada cohort construye mediana+MAD de ln(price) por (make,model,year) sobre TODOS los vehiculos available, marca |z|>=6 (con co-guards Law-I: HIGH exige price>=150k, LOW exige price<0.25*mediana), QUARANTINE de outliers. El cohort es la unidad estadistica — si abarca paises, los precios de un mercado barato desplazan la mediana/MAD del otro y sesgan sus z-scores.
3. **product_stats**: 5x COUNT(DISTINCT)/JOIN sobre millones -> una fila global. Sin corte pais -> /stats reporta un conteo global mezclado, no por-pais.
4. **canonical_key_backfill**: recompute-and-rehash por entity_ulid; sin agregacion -> country-neutral por construccion.

#### (c) Costura ES→genérico

entity.country_code existe desde 0052 pero vehicle.country_code se OMITIO deliberadamente (YAGNI, derivable via vehicle.entity_ulid->entity.country_code, evita reescribir 2,3M filas) [VERIFIED migrations/0052_country.sql:36-38]. Por tanto TODO job que AGREGUE debe alcanzar el pais por el JOIN a entity. La pasada cohort (detect.py:773-814) lee `vehicle` SOLO — hoy no tiene ruta al pais; el fix debe anadir `JOIN entity e ON e.entity_ulid=v.entity_ulid` y particionar por `e.country_code`.

#### (d) Fix exacto

1) Cohort price_trap: anadir `JOIN entity e ON e.entity_ulid=v.entity_ulid` al CTE `base`, arrastrar `e.country_code`, y hacerlo clave-lider de agrupacion en todo: `GROUP BY country_code, make, model, year`; los joins med/mad/scored ganan `AND b.country_code=m.country_code`. Cohorts pasan a per-pais -> cero contaminacion de mediana cross-pais. 2) product_stats: promover a filas per-pais — reemplazar `PK CHECK(id=1)` por `PK (country_code)` (o anadir country_code + PK compuesta), y `GROUP BY country_code` en refresh_product_stats; /stats lee la fila del pais del caller. Additivo: mantener una fila 'ES' byte-identica. 3) inquisition / cualquier otro agregado: auditar cada uno; anadir `WHERE/GROUP BY country_code` donde agregue. 4) canonical_key_backfill: dejar como esta (per-fila, seguro) — VERIFIED sin cambio. 5) Byte-identidad: con un unico tenant ES y DEFAULT 'ES', `GROUP BY country_code, make, model, year` da los mismos cohorts que hoy (un pais) -> z-scores ES inalterados.

#### (e) Adversarial — rotura por país

[VERIFIED, era ASSUMED ahora confirmado] cohort robust-z price_trap sobre (make,model,year) en vehicle con solo status='available', SIN country_code (detect.py:773-814), pese a que entity.country_code existe desde 0052 -> dos paises que comparten un cohort (make,model,year) se mezclan; un mercado barato sesga el QUARANTINE del otro. | [IT/PT/DE concreto] un cohort VW Golf 2018 que pool ES + un mercado PT mas barato BAJA la mediana conjunta -> listings ES legitimos-pero-bajos cruzan el umbral z LOW y se cuarentenan mal; los altos PT escapan. La dispersion de precio transfronteriza es justo el ruido que el robust-z NO debe poolear. | [product_stats] un COUNT(DISTINCT) global mezcla tenants -> un numero de cobertura por-pais es incomputable y el portal muestra un total mezclado sin sentido. | [non-EU/ruido] vehicle no tiene country_code (VERIFIED live) asi que CADA fix de cohort depende de que el JOIN a entity siga intacto; el JOIN debe ser inner y country_code es NOT NULL DEFAULT 'ES' (0052) -> sin fuga de NULL, pero una entity mal-estampada contamina su cohort.

#### (f) Sellado + verificación multi-vía

Sello = 'ningun agregado de mantenimiento poolea >1 country_code; la salida ES es byte-identica'. | Via 1 (golden): re-correr price_trap sobre la DB viva ES-only antes/despues del JOIN+GROUP BY country_code -> set de flags identico (un solo tenant => mismos cohorts). La fila 'ES' de product_stats == la fila global de hoy. | Via 2 (SQL ortogonal): `SELECT count(DISTINCT country_code) FROM (cohort CTE) GROUP BY make,model,year HAVING count(DISTINCT country_code)>1` debe devolver 0 tras el fix (ningun cohort abarca paises) — asercion de data-contract. | Via 3 (adversarial sintetico): inyectar 2 entities con el MISMO (make,model,year) pero distinto country_code y precios muy dispares; aseverar que los cohorts per-pais producen medianas independientes y que ningun z-score de un pais mueve el del otro (el test debe FALLAR en la query pooleada actual y PASAR tras la particion). | Cross-ref live: vehicle sin country_code (VERIFIED) -> el JOIN es obligatorio, no opcional; entity 450.652 todas ES (VERIFIED) -> el pooling de hoy es inocuo SOLO porque hay un tenant.

#### (g) Herramienta NEXT-LEVEL (€0)

Great Expectations (Apache-2.0) — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Contrato de datos PRE-agregado que falla CERRADO: codificar 'cada cohort lleva exactamente un country_code', 'ningun resultado GROUP BY abarca >1 pais', 'cada fila de stat es country-scoped' como expectativas ejecutables, versionadas y bloqueantes ante violacion — convirtiendo la precondicion estadistica oculta en un guard mecanico espejo del invariante COUNTRY-PROOF. Alternativa [VERIFIED NEXT-LEVEL.md:168 + 338]: Pandera (mas ligero, schema de dataframe/SQL-result — asevera la homogeneidad-pais del resultado cohort directamente), Soda Core, dbt tests. EUR0 Python, corre en CI y pre-job [VERIFIED NEXT-LEVEL.md:169].

---

<a id="sp-16"></a>
### SP-16 · Motor de due-selection con scoping de país

*Mapa de átomos: faceta 6.*

#### (a)+(b) Verificación [VERIFIED] + mecanismo al átomo
La due-selection es la pregunta UNICA "que fuentes estan vencidas y son ejecutables AHORA", resuelta por DOS implementaciones paralelas que entregan la respuesta al lazo productor.

**Camino HARVEST (sync psycopg2)**
- `_due_sources(conn)` [VERIFIED scheduler.py:344-384] corre UN SQL contra `source_health`:
  `SELECT source_key, harvest_interval_hours, last_ok, last_fail, consecutive_fails FROM source_health WHERE now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz) >= harvest_interval_hours * interval '1 hour'` [VERIFIED :357-372].
  - Predicado DUE = elapsed-vs-interval con piso-epoca [VERIFIED :367-368]; una fuente jamas corrida (ambos timestamps NULL) coalesce a 1970 -> siempre DUE.
  - `ORDER BY <misma expresion> DESC` = mas-vencido-primero [VERIFIED :369-370]: una fuente hambrienta salta la cola.
  - Skip de breaker INLINE: filas con `consecutive_fails >= BREAKER_TRIP_AT` (=3 [VERIFIED :119]) se descartan en Python TRAS el fetch [VERIFIED :377-382], sin re-query a source_breaker (el comentario dice que consecutive_fails espeja el streak [VERIFIED :352-354]).
- `heartbeat_tick()` [VERIFIED :519-555] es el unico job APScheduler (max_instances=1). Llama `_due_sources` [VERIFIED :530], y por cada fila due [VERIFIED :543] SKIPea cualquier source_key AUSENTE del dict REGISTRY en memoria [VERIFIED :544-549] y si no lo lanza en serie [VERIFIED :550-553].

**Camino DISCOVERY (async asyncpg)**
- `_due(conn)` [VERIFIED discover_schedule.py:101-117] = MISMO algoritmo pero YA registry-scoped: `WHERE source_key = ANY($1::text[])` con `list(DISCOVERY_REGISTRY)` [VERIFIED :104-106]. Overdue/breaker en Python [VERIFIED :110-116], sort mas-vencido-primero [VERIFIED :116].

**El atomo clave:** el camino harvest es un SCAN GLOBAL de tabla sin filtro de key/pais; el camino discovery esta implicitamente acotado a sus propias registry keys. La DB viva confirma el universo: 56 filas source_health, country_code ausente [VERIFIED psql live 2026-06-27].

#### (c) Costura ES→genérico

El SQL de `_due_sources` (harvest) no tiene clausula `WHERE country_code` y source_health no tiene columna country_code [VERIFIED 0004:24-31; live psql has_country_code=false]. Con un unico productor global (lock faceta 1), `heartbeat_tick` trae TODA fila due de todos los tenants y luego SKIPea en silencio las cuyo source_key falta del REGISTRY ES [VERIFIED :544-549]. Invariante de byte-identidad ES: sin `$countries` ligado el predicado debe devolver el universo exacto de hoy (56 filas).

#### (d) Fix exacto

1) Depender del ALTER aditivo de faceta 5 (espejo 0052_country.sql:51-54 `ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'`) sobre source_health. 2) Filtro de pais OPCIONAL y NULL-universal: anadir `AND ($1::text[] IS NULL OR country_code = ANY($1))` al predicado; pasar NULL/None devuelve el universo ES exacto -> byte-identico (el conteo --dry-run es el oraculo invariante). 3) Converger las dos implementaciones a UN predicado parametrizado (harvest sync + discovery async comparten la clausula pais) de modo que el `ANY()` existente de discovery COMPONGA con pais, no lo reemplace. 4) Anadir termino de fair-share (p.ej. `ROW_NUMBER() OVER (PARTITION BY country_code ORDER BY overdue DESC)`, luego overdue DESC) para que un unico productor serie drene paises round-robin en vez de dejar que el pais mas-vencido monopolice cada tick — la mitigacion declarada del drenado serie (faceta 1).

#### (e) Adversarial — rotura por país

**FRANCIA (CRITICO, dual):** `_due_sources` es scan global [VERIFIED :357-372]. Si el lock global fuerza UN scheduler, heartbeat_tick trae filas due FR, las halla ausentes del REGISTRY ES y las SKIPea cada tick [VERIFIED :544-549] -> FR nunca cosecha. Trampa dual: anadir `WHERE country_code` SIN sembrar filas FR deja FR silenciosamente nunca-planificado (el predicado no devuelve nada) — mitigacion obligatoria = faceta 14 (seed) + faceta 20 (gap gate). **ITALIA/DE pan-EU:** ES ya registra fuentes pan-EU (as24_wholesale, oem_* [VERIFIED scheduler.py registry]); un source_key compartido no puede llevar interval/last_ok por-pais sin la identidad compuesta (faceta 5), asi que la cadencia IT de una fuente pan-EU no puede divergir de ES. **PORTUGAL/no-UE ruido:** un pack no-UE con fuentes delgadas igual floodea el ORDER-BY global con filas coalesced-1970 (nunca-corrido = infinitamente vencido), hambreando fuentes ES vivas del presupuesto de tick bajo drenado serie hasta que aterrice fair-share. **RUIDO:** cualquier fila source_health huerfana (sembrada pero des-registrada) es DUE para siempre y re-SKIPeada cada tick — ruido de log puro, invisible a la salud pasiva.

#### (f) Sellado + verificación multi-vía

**Sello conteo-ortogonal:** el conteo DUE del --dry-run via psycopg2 DEBE igualar un `SELECT count(*) FROM source_health WHERE <predicado>` corrido independiente (dos caminos de codigo, una verdad). Con $countries=NULL el conteo es byte-identico al universo de 56 filas de hoy. **Sello por-pais:** `_due_sources(['FR'])` devuelve SOLO filas FR; `_due_sources(['ES'])` devuelve el set legacy sin cambio (golden diff = vacio). **Sello fair-share:** un fixture sintetico 2-paises (ES muy-vencido, FR poco-vencido) debe intercalar en orden de tick, probando cero monopolio de un pais. **Sello regresion:** golden ES (Ferrari) re-corrido muestra 0 diff en el set planificado. **Elevacion NEXT-LEVEL (river):** verificar (a) serie sintetica con cambio-de-regimen -> ADWIN mueve harvest_interval_hours en la direccion esperada; (b) ruptures offline ubica el mismo change-point que river online en la misma serie; (c) churn ciclico dia/noche NO oscila el intervalo (anti-flapping) [VERIFIED NEXT-LEVEL.md:582].

#### (g) Herramienta NEXT-LEVEL (€0)

river — BSD-3-Clause — https://github.com/online-ml/river [VERIFIED NEXT-LEVEL.md:579]. Deteccion de cambio online (ADWIN/Page-Hinkley) realimenta el delta observado por-fuente (harvest_run filas-cambiadas) hacia source_health.harvest_interval_hours por-CC, con cotas duras [min,max] por tier; convierte la cadencia constante-de-modulo que due-selection consume [VERIFIED scheduler.py:344-368] en un intervalo aprendido y auto-sintonizado por-pais [VERIFIED NEXT-LEVEL.md:576-581]. EUR0, CPU-only.

---

<a id="sp-17"></a>
### SP-17 · Gramática de alerta origen-exacto + dedup

*Mapa de átomos: faceta 13.*

#### (a)+(b) Verificación [VERIFIED] + mecanismo al átomo
La gramatica de alerta es el contrato que convierte "algo fallo" en una clave de origen direccionable por maquina y de-duplicada, implementado DOS veces (async + espejo sync) sobre una tabla alert.

**GRAMATICA DE ORIGEN**
- `build_origin(source_key, phase, cdp_code=None)` [VERIFIED health.py:289-292] devuelve `'<source_key>:<phase>:<cdp_code>'` o `'<source_key>:<phase>'` — clave exacta delimitada por dos-puntos, jamas un blob de prosa.
- El espejo sync `_build_origin` [VERIFIED silence_watchdog.py:105-110] es un duplicado VERBATIM (docstring: "Mirrors health.build_origin() without importing the async module").

**DEDUP (el nucleo)**
- `fire_alert` [VERIFIED health.py:295-324]: SELECT la alerta NO-RESUELTA mas nueva para este origin exacto [VERIFIED :312-314]; si existe -> UPDATE su message+payload [VERIFIED :316-320]; si no -> INSERT [VERIFIED :321-324]. Asi 138 dealers throttling colapsan a UNA fila AS24 accionable.
- El camino silence sync `fire_silence_alert_sync` [VERIFIED silence_watchdog.py:113-167] re-implementa identico el dedup SELECT-open / UPDATE-else-INSERT [VERIFIED :141-164] con origin=`<key>:silence` [VERIFIED :127] y severidad = CRITICAL si is_tier1 si no WARNING [VERIFIED :128].
- `resolve_alerts(conn, origin)` [VERIFIED health.py:327-333]: UPDATE todas las filas abiertas de un origin SET resolved_at=now() — una recuperacion cierra su propia alerta.

**ALMACEN**
- alert(origin TEXT NOT NULL, severity CHECK in info/warning/critical, message, payload JSONB, resolved_at) [VERIFIED 0004:34-43]; idx_alert_origin [VERIFIED :44]; indice parcial idx_alert_unresolved WHERE resolved_at IS NULL [VERIFIED :45]. El SELECT del dedup cabalga el indice unresolved.

**El atomo clave:** el dedup se llava en el string origin de TEXTO-LIBRE, y origin embebe source_key SIN segmento de pais. source_health.source_key es un PK global pelado [VERIFIED 0004:25]. DB viva: 55 origins abiertos distintos, 10 de ellos ':silence' [VERIFIED psql live].

#### (c) Costura ES→genérico

La DECISION es NO prefijar pais en origin (prefijarlo romperia la byte-identidad de cada string de alerta ES y crearia filas duplicadas via dedup) y en su lugar derivar el pais por JOIN a source_health.country_code. Pero ese target de JOIN aun no existe [VERIFIED live psql has_country_code=false]. Las dos definiciones de _build_origin estan fisicamente duplicadas [VERIFIED health.py:289 vs silence_watchdog.py:105]; cualquier deriva entre ellas rompe la resolucion cruzada (una recuperacion phase=scrape resolviendo una alerta phase=silence, o viceversa).

#### (d) Fix exacto

1) Mantener origin='<source_key>:<phase>[:cdp]' SIN CAMBIO (sin prefijo de pais) — preserva la byte-identidad ES y el contrato de dedup. 2) Depender del country_code de faceta 5 en source_health; exponer pais via una vista JOIN (faceta 21 v_orchestrator_health) — `alert JOIN source_health USING(source_key)` — para lecturas de alerta por-pais SIN mutar origin. 3) Colapsar la gramatica duplicada: extraer build_origin + el dedup SELECT-open/UPDATE-else-INSERT a UN modulo importado por ambos callers async (health) y sync (silence_watchdog), O anadir un test de contrato que asevere `health.build_origin(k,p) == silence_watchdog._build_origin(k,p)` para una matriz fuzzeada — eliminando el atomo de deriva-espejo. 4) Cuando faceta 5 promueva a identidad compuesta para source_keys pan-EU genuinamente-colisionantes, origin pasa a '<source_key>@<cc>:<phase>' SOLO para las keys colisionantes (diferido, YAGNI espejo 0052->0053).

#### (e) Adversarial — rotura por país

**ITALIA/DE colision de dedup pan-EU (CRITICO):** el dedup se llava en origin texto-libre [VERIFIED 0004:36]; con un source_key global dos paises compartiendo as24_wholesale comparten un origin -> el fire_alert de IT hace UPDATE sobre la fila abierta de ES [VERIFIED health.py:316-320], asi que la alerta de un pais sobre-escribe en silencio el message/payload del otro y un solo resolve cierra ambas. **FR/PT cruce de caminos:** la gramatica silence sync y la gramatica health async son funciones separadas [VERIFIED :289 vs :105]; si una anade un segmento de pais y la otra no, una fuente FR recuperada disparando resolve phase=scrape nunca casa el origin phase=silence -> zombie permanente (hermano estructural del ':silence' no-resuelto de la faceta 12). **no-UE script:** un source_key construido de un slug de plataforma no-latino igual funciona (origin es texto opaco) PERO un cdp_code con no-ASCII podria romper routing de log/notificacion naive aguas abajo — la gramatica lo tolera, el transporte puede que no. **RUIDO:** 10 filas ':silence' abiertas hoy [VERIFIED live psql] cada una clava un origin distinto; sin derivacion de pais un operador no puede decir a que tenant pertenece cada una.

#### (f) Sellado + verificación multi-vía

**Sello equivalencia-espejo:** test de propiedad sobre (source_key, phase, cdp) fuzzeado aseverando async build_origin == sync _build_origin byte-a-byte. **Sello dedup:** disparar el mismo origin N veces -> exactamente 1 fila no-resuelta, payload refleja la ultima llamada (camino UPDATE) [VERIFIED health.py:316-320]; resolve -> 0 abiertas; re-disparar -> una fila NUEVA (no resucita la resuelta). **Sello disjuntez cross-pais (post faceta-5):** dos packs con el MISMO source_key disparan alertas -> con identidad compuesta aterrizan en origins DISTINTOS; sin ella, el sello DEBE fallar ruidoso (prueba que la colision se atrapa, no se oculta). **Invariante vivo:** `SELECT count(*) FROM alert WHERE resolved_at IS NULL GROUP BY origin HAVING count(*)>1` debe ser vacio (el dedup nunca deja dos filas abiertas por origin). **Verificacion elevacion NEXT-LEVEL:** (a) disparar un ':silence' Tier-1 -> entrega out-of-band en el canal correcto, resolve -> notificacion de cierre; (b) conteo notificaciones enviadas == filas alert abiertas Tier-1 (sin perdidas/dup); (c) una alerta ya abierta NO re-notifica cada ciclo (espeja el dedup de fire_alert) [VERIFIED NEXT-LEVEL.md:710].

#### (g) Herramienta NEXT-LEVEL (€0)

Apprise — BSD-2-Clause — https://github.com/caronc/apprise [VERIFIED NEXT-LEVEL.md:707]. Una libreria reparte una sola fila alert a 100+ servicios (email/ntfy/Slack/Telegram/webhook) con claves de routing por-pais; un sink en fire_alert/resolve_alerts mapea (severidad, CC, tier) -> URLs de canal de modo que un ':silence' Tier-1 o un lease-rancio CRITICAL alcanza al operador FUERA-DE-BANDA en vez de morir en una tabla que nadie mira cuando el stack esta caido [VERIFIED NEXT-LEVEL.md:704-709]. EUR0.

---

<a id="sp-18"></a>
### SP-18 · Gate de gobierno de cobertura (registry-drift CI)

*Mapa de átomos: faceta 20.*

#### (a)+(b) Verificación [VERIFIED] + mecanismo al átomo
El gate de gobierno-de-cobertura es la red que cierra el lazo de onboarding — probando que cada fuente sembrada mapea a un conector ejecutable y un lock_key, y viceversa. Hoy es un reporte parcial, manual y ES-only.

**LO QUE EXISTE**
- `_all_source_keys(conn)` [VERIFIED scheduler.py:387-391]: `SELECT source_key FROM source_health ORDER BY source_key` — el universo sembrado (vivo: 56 filas).
- `_gap_report(all_keys)` [VERIFIED scheduler.py:394-398]: particion de conjuntos pura — `mapped = [k for k in all_keys if k in REGISTRY]`, `unmapped = [k for k in all_keys if k not in REGISTRY]`. REGISTRY es el dict ES en memoria.
- `UNMAPPED_KEYS = frozenset()` [VERIFIED scheduler.py:337] es un placeholder MUERTO (comentario "populated dynamically in _gap_report" pero _gap_report devuelve sus propias listas; el frozenset nunca se escribe).
- Salida: SOLO dentro del printer --dry-run [VERIFIED scheduler.py:739-787] — imprime conteos "Mapped/UNMAPPED" y una lista GAP REPORT. Es un artefacto de consola LEIDO-por-humano, no una asercion. heartbeat_tick por separado SKIPea unmapped en runtime [VERIFIED :544-549].

El gate es MEDIA biyeccion: atrapa seed-sin-registry (UNMAPPED) pero NO registry-sin-seed (ORPHAN), no tiene brazo lock_key/adapter, no tiene particion por-pais, y nunca falla un build — solo imprime.

**El atomo clave:** la auditoria compara el set sembrado vivo contra UN dict REGISTRY global en memoria [VERIFIED :396], asi que una semilla de pais extranjero aparece solo como ruido de consola, y dos packs reusando un source_key son invisibles (sin chequeo de disjuntez).

#### (c) Costura ES→genérico

Toda la cadena dry-run -> golden -> Ferrari -> CI valida UNICAMENTE el REGISTRY ES global [VERIFIED scheduler.py:739-787 compara contra el dict global unico]. No hay gate per-pais pre-go-live que asevere que cada source_key sembrado de pais X tiene registry + adapter + lock_key, ni guard de disjuntez de source_key cross-pack. La incompletitud de onboarding degrada a ruido de consola UNMAPPED que alguien debe mirar a ojo en --dry-run, nunca un build rojo.

#### (d) Fix exacto

1) Generalizar `_gap_report` a una BIYECCION per-pais: por cada pais activo, cada fila source_health (WHERE country_code=cc, post faceta-5) debe mapear a (una entrada de registry) Y (un adapter de discovery donde aplique, faceta 4) Y (un lock_key derivable, faceta 1); y el inverso — cada SourceEntry tiene su semilla (cierra el hueco ORPHAN que el reporte actual ignora). 2) Anadir un guard de DISJUNTEZ CROSS-PACK: aseverar que los sets de source_key de dos packs activos cualesquiera son disjuntos (o, para keys pan-EU compartidas a proposito, que resuelven a la identidad compuesta de faceta 5) — el unico chequeo que defiende a las facetas 9 (breaker), 10 (crash-net) y 13 (dedup de alerta) de la fusion silenciosa de dos paises. 3) Promoverlo de print --dry-run a un TEST de CI que FALLA cuando UNMAPPED>0 O ORPHAN>0 O la disjuntez se rompe — corrible sin DB viva via fixtures. 4) Modelar el country-pack (country.toml + registry + semillas + lock_key) como un esquema tipado de modo que el manifest se valide a si mismo, no solo el cross-check de DB.

#### (e) Adversarial — rotura por país

**SEMILLA FORANEA ruido (cualquier pais no-ES):** una semilla PT/IT/FR sin entrada de registry ES aparece solo como una linea UNMAPPED en un --dry-run manual [VERIFIED :754-757,784-787]; nada falla, asi que un pais medio-onboardeado se publica silenciosamente nunca-planificado (compone con el FR-nunca-cosecha de la faceta 6). **FUSION CROSS-PACK (DE/IT pan-EU):** sin guard de disjuntez, dos packs reusando as24_wholesale/oem_* comparten breaker (faceta 9), high-water del crash-net (faceta 10) y origin de alerta (faceta 13) — el gate es el UNICO sitio donde esto se atrapa mecanicamente, y hoy no puede. **ORPHAN registry:** un SourceEntry anadido al pack pero nunca sembrado en source_health es invisible a _gap_report (solo itera keys sembradas [VERIFIED :396]) -> un conector que jamas puede estar due, sin detectar. **no-UE:** un pais cuyo eje registral es inconstruible a EUR0 (faceta 4, p.ej. Japon) puede legitimamente tener MENOS fuentes; un gate naive que exija un roster fijo false-fallaria — la biyeccion per-pais debe ser declarada-por-pack, no hardcodeada.

#### (f) Sellado + verificación multi-vía

**Sello red-build mecanico:** un country.toml con una fuente sembrada sin entrada de registry -> CI ROJO; biyeccion completa -> verde [VERIFIED NEXT-LEVEL.md:590a]. **Cross-check 2-via:** el conteo UNMAPPED del guard tipado DEBE igualar el conteo del _gap_report SQL --dry-run sobre la misma DB [VERIFIED NEXT-LEVEL.md:590b] — caminos de codigo independientes, un numero. **Sello disjuntez adversarial:** inyectar un source_key duplicado entre dos packs -> el guard de disjuntez BLOQUEA (espejo del sealing_hole CROSS-PACK) [VERIFIED NEXT-LEVEL.md:590c]. **Regresion ES:** active_countries()==['ES'] -> 0 UNMAPPED / 0 ORPHAN, byte-identico al reporte de hoy (el universo de 56 filas plenamente mapeado). **Sello inverso:** quitar una semilla de una fuente registrada -> ORPHAN>0 -> ROJO (prueba la segunda mitad de la biyeccion que el reporte actual no tiene).

#### (g) Herramienta NEXT-LEVEL (€0)

Pydantic — MIT — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela el country-pack como `CountryPack(BaseModel)` con validators de coherencia; `tests/test_registry_drift.py` itera active_countries() y falla si la biyeccion source_health<->registry<->lock_key no cierra (0 UNMAPPED / 0 ORPHAN), mas un validator de disjuntez cross-pack — convirtiendo el gap silencioso de --dry-run de `_gap_report` [VERIFIED scheduler.py:394] en un build rojo mecanico que corre en CI sin DB viva (fixtures) [VERIFIED NEXT-LEVEL.md:584-590]. EUR0.

---

<a id="sp-19"></a>
### SP-19 · Contrato de dispatch con parámetro de país

**Mecanismo al átomo — el argv ES el contrato (y no tiene eje pais)**

#### (a) code_hints VERIFICADOS
- `class SourceEntry(NamedTuple): source_key; module; extra_args` [VERIFIED pipeline/ops/scheduler.py:144-147]. El contrato productor->subproceso es UNA tupla posicional: clave, modulo, y una lista de args literales.
- `_build_cmd(entry)` -> `[sys.executable, "-m", entry.module, *entry.extra_args]` [VERIFIED pipeline/ops/scheduler.py:405-407]. Concatena interprete + `-m modulo` + los `extra_args` *horneados* en la tupla. **Cero ranura de pais.**
- `_run_source` toma `entry = REGISTRY[source_key]`, `cmd = _build_cmd(entry)` y lanza [VERIFIED scheduler.py:422-423]; loguea `LAUNCH %s -> %s` con el argv exacto [VERIFIED scheduler.py:424].
- El UNICO grado de libertad de desambiguacion es `extra_args`, usado HOY para partir un modulo multi-tenant en N source_keys, nunca para pais:
  - `["--members","faciliteacoches"]` / `["--members","racc"]` [VERIFIED scheduler.py:203/206]
  - `["--member","athlon"]` ... `["--member","northgate"]` (rentacar) [VERIFIED scheduler.py:211-228]
  - `["--members","flexicar"]` / `ocasionplus` / `clicars` / `carplus` [VERIFIED scheduler.py:235/238/241/244]
  - `["--brand","bmw"]` / `["--brand","mini"]` [VERIFIED scheduler.py:258-263]
- Lado discovery, el argv es aun mas rigido: `cmd = [sys.executable, "-m", "pipeline.discover", job.vector]` [VERIFIED pipeline/discover_schedule.py:166] — literalmente sin slot para flag alguno.
- `ADAPTERS: dict[str, type[SourceAdapter]]` (vector->clase) [VERIFIED pipeline/discover.py:48-74]: `overture` :66, `collapse_invisible` :73, `graph_recursive` :70, `dork_municipal` :67, `borme_cnae` :68. La clase se instancia DENTRO de `pipeline.discover` sin que la orquestacion le pase pais.

#### (b) Nucleo:
la orquestacion habla con el conector SOLO por argv posicional. `_build_cmd` no construye semantica: pega `module` + `extra_args`. "Que pais" es HOY implicito-ES porque cada `module` es un conector ES y cada `Adapter` es un adaptador ES. Para reutilizar UN modulo pan-EU entre paises desde el scheduler hace falta hilar un token de pais en ese argv; no existe.

#### (c) Costura ES→genérico

El eje 'que pais' esta implicito-ES en dos superficies: (1) harvest, `SourceEntry.extra_args` solo sabe partir multi-source (--member/--members/--brand), nunca pais [VERIFIED scheduler.py:203/235/259]; (2) discovery, `_run_vector` no tiene argumento variable alguno tras `job.vector` [VERIFIED discover_schedule.py:166]. La costura es extender AMBOS contratos con un token de pais opcional (default 'ES', omitido-cuando-ES) para que un conector/vector COMPARTIDO se invoque por pais sin que el modulo hardcodee su pais.

#### (d) Fix exacto

1) Anadir `country: str = 'ES'` como campo trailing-default a `SourceEntry` (NamedTuple admite default al final) y al `DiscoveryJob` dataclass (ya tiene defaults, discover_schedule.py:53-60). 2) En `_build_cmd`: `argv = [sys.executable,'-m',entry.module,*entry.extra_args]; if entry.country != 'ES': argv += ['--country', entry.country]` — ES omite el flag => argv BYTE-IDENTICO al de hoy; no-ES recibe el token. Espejar en `_run_vector` (discover_schedule.py:166). 3) Convencion: los conectores/adapters pan-EU aceptan `--country` (argparse con default 'ES', `parse_known_args`); los ES-only lo toleran/ignoran. Asi el harness dice 'corre esta invocacion PARA DE' a un modulo unico reusable en vez de forzar un fork de modulo por pais. (Token OPACO, no asumir CHAR(2): un mercado JP puede querer --market/--locale.)

#### (e) Adversarial — rotura por país

[VERIFIED BREAK Germany — HIGH] Ni `_build_cmd` (scheduler.py:405-407) ni `_run_vector` (discover_schedule.py:166) hilan `--country`. Para conectores genuinamente pan-EU (`as24_wholesale` scheduler.py:192 sirve DE/AT; `oem_audi/bmw/kia/ford/hyundai` :255-269 sirven toda la UE) y para los vectores globales ciegos al pais `overture`/`collapse_invisible`/`graph_recursive` (discover.py:66/73/70) NO hay forma de decir 'ejecuta para DE' vs 'para IT' => un solo modulo no se reusa entre paises; cada uno tendria que forkear un modulo por pais, explotando el registry. RUIDO/no-UE: (a) anadir `--country` a un conector cuyo argparse rechace flags desconocidos lo crashea (exit!=0 => trip de breaker FALSO); por eso el flag debe omitirse-cuando-ES Y el conector debe tolerarlo. (b) Japon: el token puede no ser ISO-2 (--market/--locale), asi que el contrato debe portar un string opaco, no asumir 2 letras. FR/IT/PT comparten exactamente el mismo break por reuso pan-EU.

#### (f) Sellado + verificación multi-vía

Multi-via: (1) **Byte-identidad ES** — test sobre TODO el REGISTRY que asevera `_build_cmd(entry)` identico antes/despues (country=='ES' => sin flag); idem los 5 vectores en `_run_vector`. (2) **Cross-via token** — SourceEntry sintetico country='DE' => assert argv termina en `['--country','DE']`; 2a via independiente: grep del argv en la linea de log `LAUNCH ... -> ...` (scheduler.py:424) confirmando que el token llego al subproceso. (3) **Adversarial argparse-contract** — todo modulo al que el harness pueda pasar `--country` debe aceptarlo (round-trip `parse_known_args`), probando que no hay trip de breaker falso. (4) **Paridad discovery** — misma asercion de byte-identidad sobre el cmd de los vectores ES.

#### (g) Herramienta NEXT-LEVEL (€0)

Procrastinate (MIT) — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555]. Eleva el contrato de dispatch: convierte el argv posicional ciego-al-pais (todo horneado en `extra_args`) en una TAREA durable Postgres-nativa donde el pais es kwarg de primera clase (`harvest.defer(source_key=..., country='DE')`), con claim idempotente FOR UPDATE SKIP LOCKED y retry/backoff exponencial, sobre el PG ya existente (:5433, cero infra nueva). Cierra el 'lease best-effort, NO takeover' aportando reanudacion real de la unidad de trabajo [VERIFIED NEXT-LEVEL.md:552-558]. Alternativas €0 mismas-pista: DBOS Transact / pgqueuer / Hatchet (todas MIT) [VERIFIED NEXT-LEVEL.md:556].

---

<a id="sp-20"></a>
### SP-20 · Superficie unificada de salud del orquestador

*Mapa de átomos: faceta 21.*

**Mecanismo al átomo — la vista v_orchestrator_health que aun no existe**

#### (a) code_hints VERIFICADOS
— las 4 tablas a unir, TODAS sin `country_code` hoy:
- `source_health (source_key TEXT PRIMARY KEY, ...)` [VERIFIED migrations/0004_verification_health.sql:24-25] — sin country.
- `alert (origin TEXT NOT NULL, resolved_at TIMESTAMPTZ)` [VERIFIED 0004:34-42]; `idx_alert_origin` :44, `idx_alert_unresolved ... WHERE resolved_at IS NULL` :45 — sin country.
- `source_breaker (source_key TEXT PRIMARY KEY, ...)` [VERIFIED migrations/0013_resilience.sql:19-20] — sin country.
- `scheduler_lease (lock_key BIGINT PRIMARY KEY, holder TEXT, pid, started_at, last_heartbeat)` [VERIFIED migrations/0054_scheduler_heartbeat.sql:28-33] — sin country.
- (`harvest_run (source_key TEXT NOT NULL, ...)` [VERIFIED 0013:30-32] — sin country.)
- `grep country_code pipeline/ops/` => NINGUNO [VERIFIED — Grep 'No files found'].
- NO existe vista `v_orchestrator_health` [VERIFIED — Grep CREATE VIEW sobre migrations/: la lista de vistas NO la incluye; la ultima es 0056_v_servable_dealer].
- El operador une las tablas A MANO [VERIFIED docs/DEPLOY-DURABLE-DAEMONS.md §4:302-308 = SELECT ad-hoc SOLO de scheduler_lease; §5:328-341 = cheatsheet que delega salud-de-fuentes/breakers/alertas a un runbook SEPARADO (OPERATE.md), y el silencio a la CLI `--check-silence` :338]. No hay UNA superficie con corte por pais.
- next_level 09 #1 'v_orchestrator_health' euro0 effort M [VERIFIED NEXT-LEVEL.md:712-718].

#### (b) Nucleo:
responder 'el pais X esta gobernado?' exige HOY un LEFT JOIN mental de cuatro tablas con claves distintas (source_health/source_breaker por source_key, scheduler_lease por lock_key, alert por `origin` texto-libre) a traves de DOS espacios de identidad — y sin columna de pais que cortar. El entregable es una vista de SOLO-LECTURA `v_orchestrator_health` que hace esos joins UNA vez y proyecta por source_key (y, tras faceta 5, por country_code): estado de silencio (`now()-COALESCE(last_ok,last_fail) vs 2*interval`), estado del breaker (`is_open`/`status`), vivacidad del lease (`staleness vs TTL`), y conteo de alertas abiertas/zombie (`origin LIKE source_key%`). Una fila = la salud de orquestacion COMPLETA de una fuente; un GROUP BY country = el panel de certificacion por pais.

#### (c) Costura ES→genérico

La vista es la superficie ortogonal canonica para certificar/sellar/revertir un pais INDEPENDIENTEMENTE. Pero es TOTALMENTE DEPENDIENTE de la faceta 5: sin `country_code` en source_health/source_breaker/scheduler_lease/alert no hay nada que GROUP BY; construida hoy AGREGA cross-pais y MIENTE (toda fuente pan-EU plegada en una unica fila etiquetada ES). La costura: esta vista DEBE construirse DESPUES de la migracion additiva de `country_code` (faceta 5, espejo de 0052:51-54 `ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'`), y su corte por pais derivarse del nuevo `source_health.country_code` o via convencion de nombrado del source_key. Mono-tenant ES => la vista devuelve el cuadro mono-pais de hoy byte-equivalente.

#### (d) Fix exacto

1) Aterrizar PRIMERO la faceta 5: `ALTER ... ADD COLUMN IF NOT EXISTS country_code CHAR(2) NOT NULL DEFAULT 'ES'` en las 4 tablas (espejo de 0052:51-54). 2) Migracion additiva `00NN_v_orchestrator_health.sql`: `CREATE OR REPLACE VIEW v_orchestrator_health AS SELECT sh.country_code, sh.source_key, sh.status, sh.is_tier1, (now()-COALESCE(sh.last_ok,sh.last_fail) > make_interval(hours=>2*sh.harvest_interval_hours)) AS silent, sb.* (breaker), COUNT(a.*) FILTER (WHERE a.resolved_at IS NULL) AS open_alerts FROM source_health sh LEFT JOIN source_breaker sb USING(source_key) LEFT JOIN alert a ON a.origin LIKE sh.source_key||':%' ... GROUP BY ...` + join de lease (lock_key derivado por (rol,pais)). Cortable por `$country`. 3) Panel de operador (Grafana) leyendo la vista con variable `$country`. (Las LEFT JOIN preservan fuentes sin breaker/lease: NULL = cerrado/ausente, no se cae la fila.)

#### (e) Adversarial — rotura por país

[VERIFIED sealing_hole] Sin `country_code` en las 4 tablas (todas confirmadas sin el) NO se puede computar ni certificar 'pais X esta sano / 100% cosechado', ni sellar el intervalo-certificado de un pais, ni scopear un rollback de onboarding por pais. Si la vista se construye ANTES de la faceta 5, agrega cross-pais y mal-cuenta en silencio (la alerta abierta de una fuente DE aparece bajo ES; el breaker de un source_key pan-EU compartido se atribuye al pais que lea la fila). El join de alerta `origin LIKE source_key%` (origin texto-libre, sin pais [VERIFIED 0004:36]) es en si cross-tenant-fragil: dos paises que compartan source_key comparten origin => el conteo de alertas-abiertas duplica. RUIDO: las LEFT JOIN deben preservar fuentes sin fila de breaker/lease (NULL=cerrado/ausente), no dropearlas, o una fuente nunca-tripeada desaparece del panel. DE/FR/IT/PT: el corte miente para todos hasta que la faceta 5 + el guard de disjuncion de source_key (faceta 20) cierren.

#### (f) Sellado + verificación multi-vía

Multi-via (espeja NEXT-LEVEL.md:718): (1) **HTTP-vs-SQL** — el panel 'fuentes calladas por pais' == SELECT directo del predicado de silencio para ese pais. (2) **Cross-via** — el conteo de breakers abiertos del board == `is_open` recomputado por SQL independiente (health.py). (3) **Adversarial aislamiento** — sembrar un pais #2 (DE) y confirmar que `$country=DE` muestra CERO filas ES y viceversa (guard de aislamiento de pais; espeja el guard de identidad/PK de la faceta 5). (4) **Gate de dependencia** — un test que FALLA si `v_orchestrator_health` se crea mientras CUALQUIERA de las 4 tablas carece de `country_code` (previene la regresion 'construida-antes-de-faceta-5 miente').

#### (g) Herramienta NEXT-LEVEL (€0)

Grafana (AGPL-3.0; uso interno no-distribuido OK, marcar) — https://github.com/grafana/grafana [VERIFIED NEXT-LEVEL.md:715]. Convierte la vista PG-nativa `v_orchestrator_health` en un board vivo de operador POR PAIS (fuentes calladas, breakers abiertos, leases rancios, alertas zombie, backlog del bus) con variable `$country` — reemplaza el JOIN de 4 tablas a mano (DEPLOY §4/§5). Honestidad de licencia: AGPL-3.0 OK para dashboard interno no-distribuido; carril licencia-limpia = Prometheus (Apache-2.0)+postgres_exporter+panel, u OpenObserve (AGPL) all-in-one [VERIFIED NEXT-LEVEL.md:712-718]. El entry nombra explicitamente la vista 09 #1 (une source_health+source_breaker+scheduler_lease+alert con corte por country_code) [VERIFIED NEXT-LEVEL.md:713].

---

<a id="sp-21"></a>
### SP-21 · Aritmética de semilla watchdog-safe — banda `[interval, 2·interval)` (2ª pasada)

*Mapa de átomos: faceta 14.*

> **Honestidad cruda — segundo deep-dive del MISMO átomo que [SP-03](#sp-03)** (aritmética de semilla watchdog-safe, *faceta 14*). Se conserva ÍNTEGRO, sin descartar nada: aporta el encuadre de la **banda semiabierta `[interval, 2·interval)`** y un property-test sobre la rejilla de cadencias `{24, 168, 720, 2160}`. Donde SP-03 da la receta `last_fail = now()-(interval+1)h`, esta pasada la generaliza a `interval·(1+ε)` con `ε∈(0,1)`. Misma raíz (`_seed` NULL/NULL en `discover_schedule.py:87-98`), misma herramienta (Pydantic). No es redundancia oculta: es la doble verificación adversarial co-igual que el mandato exige.

**Mecanismo al átomo — la banda [interval, 2*interval) y el agujero NULL/NULL**

#### (a) code_hints VERIFICADOS
- Receta sentinel del 0039 [VERIFIED migrations/0039_schedule_segments_as24.sql]:
  - Comentario WATCHDOG-SAFE :9-13: `last_fail` mas VIEJO que `harvest_interval_hours` (=> DUE) pero mas NUEVO que `2*interval` (=> el watchdog `now()-COALESCE(last_ok,last_fail,epoch) > 2*interval` NO dispara `:silence` falsa); `status='unknown'` + `consecutive_fails=0` mantienen el breaker CERRADO para que `_due_sources` no lo salte.
  - `VALUES ('coches_net_segments', FALSE, 24, 'unknown', 0, NULL, now() - interval '25 hours')` :18 — 25h en (24, 48).
  - `VALUES ('as24_wholesale', FALSE, 168, 'unknown', 0, NULL, now() - interval '169 hours')` :23 — 169h en (168, 336).
  - `ON CONFLICT (source_key) DO NOTHING` :19/:24 (idempotente, nunca revierte una fila de cadencia viva).
- Deuda interna discovery `_seed` [VERIFIED discover_schedule.py:87-98]: `INSERT INTO source_health (source_key, harvest_interval_hours, status) VALUES ($1,$2,'unknown') ON CONFLICT (source_key) DO UPDATE SET harvest_interval_hours=...` :91-96 — las columnas `last_ok`/`last_fail` NO se setean => ambas NULL.
- `_due` calcula `last = last_ok or last_fail` -> None -> `overdue_h = inf` (DUE, ok) [VERIFIED discover_schedule.py:112-114]; PERO el predicado de silencio usa `COALESCE(...,'1970')` => edad ~55 anios > 2*interval => SILENT en el primer ciclo (borme_cnae 24h jamas corrido aparece callado de inmediato).

#### (b) Nucleo:
dos predicados leen el MISMO COALESCE. DUE: `now()-COALESCE(last_ok,last_fail,epoch) >= interval`. SILENT: `... > 2*interval`. Una fuente fresca no tiene ni `last_ok` ni `last_fail`. Si dejas ambos NULL, COALESCE cae a '1970' => edad ~55 anios => excede AMBOS umbrales => la fila es a la vez DUE (bien) y SILENT (mal: alerta falsa dia uno). El sentinel del 0039 fija `last_fail` a una edad en la banda semiabierta [interval, 2*interval): >= interval (DUE) y < 2*interval (NO silent). Es una semilla de 3 invariantes: (DUE) interval <= edad < 2*interval (NO-SILENT); breaker CERRADO (`status='unknown'`, `consecutive_fails=0`).

#### (c) Costura ES→genérico

El sentinel del 0039 es la receta CORRECTA pero esta inlineada a mano en UNA migracion ES para DOS claves concretas (literales '25 hours'/'169 hours' atados a las cadencias ES 24h/168h); no es una primitiva de onboarding reutilizable. Un pais nuevo siembra sus propias filas `source_health`; si copia ingenuamente el `_seed` de discovery (NULL/NULL) o elige un timestamp arbitrario, floodea `:silence` falsas el dia uno. La costura: extraer la aritmetica del sentinel a un helper generico que, dado (source_key, interval_hours), emita `last_fail = now() - interval*(1+epsilon)` con epsilon en (0,1), `status='unknown'`, `consecutive_fails=0`, `ON CONFLICT DO NOTHING` — y REPARAR el `_seed` de discovery para usarlo en vez de NULL/NULL.

#### (d) Fix exacto

1) Funcion generica `seed_watchdog_safe(conn, source_key, interval_hours)` que inserta `last_fail = now() - make_interval(hours => interval_hours + 1)` (o `interval_hours*1.04`), `status='unknown'`, `consecutive_fails=0`, `ON CONFLICT (source_key) DO NOTHING` — el 0039 parametrizado por la cadencia de cada fuente. 2) Reparar `_seed` (discover_schedule.py:91-96): setear `last_fail` al sentinel en vez de omitirlo, para que los vectores (borme_cnae 24h, overture 720h, ...) sean DUE-pero-no-SILENT en el primer tick. 3) Declarar este helper como PASO de onboarding del country-pack: toda fila `source_health` sembrada pasa por el. 4) Cuando aterrice `country_code` (faceta 5) la semilla lo porta tambien.

#### (e) Adversarial — rotura por país

[VERIFIED BREAK France — MEDIUM + deuda interna] `discover_schedule.py:87-98` ya inserta NULL/NULL => cada vector de discovery aparece SILENT en el primer ciclo antes de haber corrido nunca => flood de `:silence` falsas. Un onboarding ingenuo PT/IT que siembre NULL/NULL o un timestamp demasiado-viejo (edad >= 2*interval) reproduce esto para TODAS sus fuentes a la vez. RUIDO inverso: sembrar demasiado-RECIENTE (edad < interval) hace la fila NO-due => nunca se planifica (callada-nunca-cosechada en silencio, peor que la alerta). No-UE: un pais con cadencias muy largas (p.ej. tirones registrales anuales) necesita la banda computada de SU interval; un literal '25h'/'169h' es especifico de cadencia ES y debe derivarse de `interval_hours`, no copiarse. RUIDO de reloj: los timestamps deben ser tz-aware (`now()` lo es; el fallback NULL->epoch es la trampa).

#### (f) Sellado + verificación multi-vía

Multi-via: (1) **Property test** — para una fila sembrada, asevera `interval <= edad(now-last_fail) < 2*interval` (en-banda), `status='unknown'`, `consecutive_fails=0` => simultaneamente DUE y NO-SILENT; correr sobre una rejilla de `interval_hours` (24, 168, 720, 2160). (2) **Cross-via ortogonal** — tras sembrar, correr A LA VEZ `_due` (debe INCLUIR la clave) y `find_silent_sources` (NO debe incluirla) contra la misma DB (SQL-vs-SQL de mecanismo distinto). (3) **Regresion ES** — las dos filas del 0039 byte-identicas; el fix de `_seed` asevera que borme_cnae pasa de 'SILENT en tick 1' a 'no silent'. (4) **Adversarial** — inyectar una semilla NULL/NULL y asegurar que el property test FALLA (prueba mecanica de que el guard atrapa el flood dia-uno).

#### (g) Herramienta NEXT-LEVEL (€0)

Pydantic (MIT) — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Modela las filas-semilla del country-pack como `SeedRow(BaseModel)` cuyo validator IMPONE la banda watchdog-safe (interval <= edad < 2*interval, `status=='unknown'`, `consecutive_fails==0`) y RECHAZA NULL/NULL en el onboarding => gate de CI que falla ROJO ante un pack mal-sembrado, sin DB viva (fixtures). El entry §584 'Guard de drift de registry/semilla como CONTRATO TIPADO' cubre explicitamente las *semillas* [VERIFIED NEXT-LEVEL.md:584-590]. Alternativas: jsonschema / Cerberus / dataclasses+asserts [VERIFIED NEXT-LEVEL.md:588].

---

## Mejoras a nivel inalcanzable (€0, priorizadas)
| # | Idea | Por qué hoy es inalcanzable | €0 | Esfuerzo |
|---|---|---|---|---|
| 1 | **Vista unificada `v_orchestrator_health`** que une `source_health`+`source_breaker`+`scheduler_lease`+`alert` (open/resolved) en un panel con corte por `country_code` — superficie ortogonal canónica para ver de un vistazo que ningún país tiene fuentes calladas, breakers abiertos ni zombies | El operador junta 4 tablas a mano con SQL ad-hoc (`DEPLOY §4/§5`); no hay agregado country-aware | ✓ | M |
| 2 | **Guard de "registry drift" en CI:** por cada país activo, toda fila de `source_health` mapea a un `SourceEntry` (0 UNMAPPED) y viceversa (toda entrada tiene semilla) | El `_gap_report` existe pero sólo se ve en `--dry-run` manual; un onboarding incompleto pasa silencioso | ✓ | S |
| 3 | **Artefacto NSSM commiteado** `ops/windows/install-cardeep-services.ps1` idempotente, sin ampersand, parametrizado por `CARDEEP_COUNTRY` — espeja las units systemd como código versionado | La persistencia real del host Windows vive sólo como prosa (`DEPLOY §3`); deriva doc-vs-realidad | ✓ | S |
| 4 | **`lock_key(role,country)` + `holder="<role>:<cc>"`** para aislamiento per-VPS-país sin editar el motor, más `v_lease_health` que liste leases por país | Los locks son literales (`scheduler.py:913`, `discover_schedule.py:50`); escalar exige hoy editar el motor | ✓ | S |
| 5 | **Cadencia auto-ajustable:** usar el historial de `harvest_run` para subir `harvest_interval_hours` de fuentes que nunca cambian y bajarlo de las volátiles — reduce superficie de ban y trabajo inútil | Las cadencias son estáticas por semilla; no hay realimentación del delta observado hacia el intervalo | ✓ | M |
| 6 | **IA-local obrera para triaje del cubo UNKNOWN:** `classify_failure` (`health.py:340`) es regex determinista y lo no-clasificado cae a `ESCALATE_OWNER`; un modelo local podría tipar esos fallos irreducibles en acciones de reparación | Capa 2 (IA-local) = 0 en código hoy; sólo se justifica con un corpus real de fallos UNKNOWN acumulados y caso de uso probado | ✓ | L |

---

## Riesgos / open items
- **[ESPINA DORSAL]** El `country_code` está en el ESQUEMA (0052/0053) y en `cdp_code`, **no** en la lógica de orquestación. Todo §Diseño es additivo y €0 pero **NO está en código**; mientras no se construya, el onboarding de país #2 es imposible sin editar el motor. El verdict NEEDS_REWORK es exacto.
- **Productor host-único en serie:** si los conectores de un país saturan el host, los demás esperan (drenado serie). Mitigación: fair-share en la due-query o productor per-país vía `lock_key(role,country)`.
- **`country_code` con DEFAULT 'ES' es byte-idéntico**, PERO si la due-query gana el filtro `WHERE country_code` sin sembrar filas del país nuevo, el país queda silenciosamente **nunca-planificado**. Mitigación **obligatoria**: `_gap_report` per-country + CI rojo si UNMAPPED>0.
- **El fix de silencio debe NO resolver una fuente aún callada:** el `NOT EXISTS` tiene que espejar EXACTO el 2× interval de `find_silent_sources`, o la alerta flapea (resuelve/redispara cada hora). Verificable por el test aún-callada→NO-resuelta.
- **El lease es best-effort/observabilidad, NO takeover:** un productor per-país muerto en duro sigue esperando a que PG recolecte la sesión; multi-país no cambia esto y no debe prometerse takeover instantáneo (`DEPLOY §6`).
- **Host real = Windows; units systemd asumen Linux `/opt/cardeep`** → la ruta de persistencia viva es NSSM, sin artefacto commiteado. Riesgo de sellar "daemons persistentes" sobre prosa. Mitigación: el PS1 commiteado (mejora #3).
- **[ASSUMED, verificar antes del onboarding #2]** Los cadence jobs de mantenimiento (`gestionador_detect`, `canonical_key_backfill`, `product_stats_refresh`) podrían agregar cross-country sin partición; auditar su SQL y añadir `country_code` donde agreguen, o un país contaminará las stats del otro.
- **`source_key` como identidad global** asume convención de nombrado sin colisiones; si dos países declaran el mismo `source_key` sin promover a `(country_code,source_key)`, el segundo sobrescribe la salud/cadencia del primero. Mitigación: convención `<plataforma>_<cc>` como invariante + gate de disjunción + promoción a clave compuesta cuando exista colisión real (espejo 0052→0053).
- **OPEN ITEMS gated (no cerrables a €0/hoy por causa declarada):** descubrimiento no-UE (cluster F, gated KNOW_COUNTRY) · wall-clock/cron (cluster G, diferido YAGNI) · durabilidad Windows (cluster K, sin artefacto) · zombie `:silence` (cluster I, hasta merge del fix).
