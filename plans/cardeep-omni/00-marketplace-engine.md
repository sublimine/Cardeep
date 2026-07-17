# Carta de sub-proyecto — Pilar 00: Motor de indexación total (marketplace engine)

> Programa: cardeep-omni · Clave: `00-marketplace-engine` · Fecha: 2026-07-17
> Fase: SYNTHESIS (arquitectura) para F5-F7; **EJECUCIÓN F3+F4 CERRADAS 2026-07-18**
> (breaker half-open + cadencia adaptativa, ver §9); F3 incluye un bug real de
> doble-reclamo cazado, corregido y re-verificado en vivo antes de declarar nada cerrado.
> F0-F2 cerradas previamente (commit `5635811`). Este documento es la fuente de verdad del
> pilar hasta que una fase de ejecución lo enmiende con evidencia nueva.
> Doctrina aplicada: antialucinación tolerancia cero — cada afirmación lleva
> [VERIFICADO] (leída en código/DB/doc real, con archivo:línea cuando aplica),
> [VERIFICADO-RECON] (verificada en la sesión RECON 2026-07-16/17 por consulta
> directa a la DB viva o al sistema operativo, evidencia citada) o [ASUMIDO]
> (declarada como suposición, jamás disfrazada de certeza).
> Alcance: España hoy, UE en horizonte. Este pilar ES el corazón del producto:
> sin motor latiendo, todos los demás pilares sirven datos muertos.

---

## 1. Estado actual

### El hecho central: el motor lleva ~18 días PARADO [VERIFICADO-RECON, 3 vías independientes]

No es una hipótesis. Tres caminos distintos coinciden (sesión 2026-07-16/17):

1. **Proceso**: 0 procesos `python -m pipeline.ops.scheduler` ni `pipeline.discover_schedule`
   en el host (`Get-CimInstance Win32_Process`: de 5 python.exe vivos, 4 son de otro
   proyecto y 1 es la API `uvicorn` solo-lectura, PID 20584).
2. **Docker**: `docker ps -a` no muestra NUNCA un contenedor `cardeep-autopilot`. El
   servicio existe definido en `docker-compose.yml:63-72` con
   `command: ["python", "-m", "pipeline.ops.scheduler"]` (línea 67) y
   `restart: unless-stopped` (línea 72) — pero jamás se ha arrancado en este host. [VERIFICADO archivo + VERIFICADO-RECON docker]
3. **DB en vivo** (postgresql://127.0.0.1:5433/cardeep): `scheduler_lease` tiene una sola
   fila muerta — holder='harvest', pid=34712, last_heartbeat=2026-06-29 01:36:09Z.
   `apscheduler_jobs` (8 jobs) con next_run_time CONGELADO en 2026-06-29.
   `vehicle_event.observed_at` máximo = 2026-06-28 20:15:42Z.
   `source_health.last_ok` máximo entre 56 fuentes = 2026-06-28 19:27:26Z.
   now() del servidor en la consulta = 2026-07-16 22:32:23Z. [VERIFICADO-RECON]

Antes de morir, el motor trabajaba de verdad y a escala: pico de 490.141 eventos NEW en
un solo día (21-jun) y 210k GONE (23-jun). No era un mock. [VERIFICADO-RECON]

### Arquitectura real del motor [VERIFICADO en código]

- `pipeline/ops/scheduler.py:1-25` (docstring) — BlockingScheduler de APScheduler 3.x con
  SQLAlchemyJobStore persistido en la propia cardeep-pg. **Single-producer, en SERIE**:
  un `heartbeat_tick` cada 15 min (`TICK_INTERVAL_MINUTES = 15`, scheduler.py:121)
  consulta `source_health` por fuentes DUE
  (`now() - COALESCE(last_ok, last_fail) >= harvest_interval_hours`, docstring líneas 10-13)
  y las lanza una subprocess a la vez, timeout 4h/fuente. Diseño deliberado anti-cicatriz
  AS24 ("two governors fighting the same host", scheduler.py:8). Advisory lock de Postgres
  impide un segundo productor.
- `pipeline/engine/governor.py:1-36` (docstring) — token bucket POR HOST compartido entre
  todas las tareas del proceso; `DEFAULT_RATE_PER_SEC = 0.7` (governor.py:51), burst 3.0,
  jitter. **Explícitamente single-process**: "This is correct and crash-safe for ONE
  process (P1). The documented upgrade hook for MULTI-process / multi-machine (P2,
  04 §5.1) is a Redis-backed GCRA/token-bucket Lua script keyed by host" — y el propio
  docstring habla del hook en futuro ("when that lands", governor.py:22-28). Que NO está
  construido se confirma por vía independiente: cero referencias a `redis` en todo el
  módulo (grep). [VERIFICADO — cita literal corregida en la revisión de esta carta]
- Flota de conectores: 70 archivos — 23 adaptadores de descubrimiento en
  `pipeline/sources/` (pacing ad-hoc por `time.sleep`, SIN gobernador compartido) y 46
  conectores de inventario en `pipeline/platform/` (TODOS enrutados por el governor).
  [VERIFICADO-RECON vía código + `state/validation_matrix.json` de 2026-06-15 — matriz
  ~1 mes desactualizada, hueco conocido]
- 56 fuentes registradas en `source_health` con cadencias estáticas 24h/168h/720h/2160h.
  `harvest_interval_hours` creado en `migrations/0021_harvest_cadence.sql:13` (default 168).
  `is_tier1` es campo de primera clase (`migrations/0002_entities.sql:26` en entity;
  `migrations/0013_resilience.sql:61` en source_health; estructura granular de tiers en
  `migrations/0016_tiering_groups.sql`). [VERIFICADO]

### La causa raíz del apagón: procedimiento de arranque sin supervisión [VERIFICADO]

- `docs/runbook/DEPLOY.md:115-119` — §8 "Arrancar el motor (cadencia durable)" es el
  ÚNICO procedimiento documentado, y es un comando en PRIMER PLANO
  (`python -m pipeline.ops.scheduler`): muere al cerrar la terminal. Exactamente el patrón
  que reproduce la caída. [VERIFICADO]
- Las unidades systemd (`ops/systemd/cardeep-harvest.service`, `cardeep-discovery.service`)
  se declaran a sí mismas "Linux VPS... INSTALL is an OWNER host step. Inert in-repo
  artifact until installed" — inaplicables a este Windows 11 dev box. [VERIFICADO-RECON]
- No existe supervisor nativo de Windows (Task Scheduler/NSSM) configurado. [VERIFICADO-RECON]

### El punto ciego que agravó el apagón: el vigilante murió con el vigilado [VERIFICADO]

- El `silence_watchdog` que alerta fuentes calladas es un job DEL PROPIO scheduler
  (scheduler.py:17-19, docstring): al morir el scheduler, murió el watchdog. Desde el
  29-jun no se ha generado NINGUNA alerta nueva — incluida la del propio apagón.
- `/health` de la API (`services/api/routers/ops.py:26-45`) solo comprueba la DB
  (`SELECT 1`), NO la vida del scheduler. Un dashboard que mire /health ve "live" con el
  motor muerto. [VERIFICADO — leído el handler completo]
- Tabla `alert` (`migrations/0004_verification_health.sql:34`): 88 filas, 59 sin resolver
  (9 critical + 50 warning) — deuda operativa PREVIA al apagón. [VERIFICADO-RECON]

### Estado congelado del producto [VERIFICADO-RECON]

- Cobertura segmento venta (view `v_province_seal`, creada en
  `migrations/0042_province_seal_view.sql:18`, extendida 0043, recreada
  `migrations/0059_geo_code_width.sql:324`): nacional 79,7% (18.100/22.720),
  11 SELLADO / 35 PARCIAL / 6 GAP de 52 provincias. Desguace: 52/52 SELLADO.
  Cifra estática desde el 29-jun por definición: nada ha corrido.
- 6 de 56 fuentes con circuit breaker abierto (`consecutive_fails` ≥ 3, columna en
  `migrations/0004_verification_health.sql:28` y `0013_resilience.sql:23`):
  autocasion_wholesale y wallapop_wholesale (ambas Tier-1 de alto volumen),
  group_vo_chains_carplus, oem_audi_wholesale, nissan_intelligent_choice_wholesale,
  miclasico_wholesale. El breaker NO tiene auto-recuperación: abierto = excluido
  indefinidamente de `_due_sources` hasta diagnóstico manual.
- Imagen `cardeep-app:latest` construida 2026-06-29T15:09:45Z — 17 días más vieja que
  main; 5 commits posteriores tocan pipeline/services/migrations. Arrancar sin rebuild =
  correr código desactualizado.

### Huecos conocidos que esta carta NO resuelve con certeza

- Segundo daemon `pipeline/discover_schedule.py --serve` (lock advisory distinto,
  1128354373): sin evidencia de haber corrido nunca en modo servidor en este host
  (cero fila con ese lock en `scheduler_lease`). [ASUMIDO/PARCIAL — declarado, no resuelto]
- Ningún documento del repo — incluido el swarm de auditoría de docs/ai/audits/ — había
  detectado el apagón de 18 días; `08_SCHEDULER_OPS_AUDIT.md` sigue stub NOT_STARTED.
  El hallazgo es nuevo de la sesión RECON. [VERIFICADO-RECON]
- El volumen exacto de conectores VIVOS hoy (vs. los 70 archivos) depende de
  `state/validation_matrix.json`, desactualizado ~1 mes. Se cierra en F2. [HUECO DECLARADO]

---

## 2. Investigación competitiva/adversarial

RESEARCH ejecutado sobre 14 referencias. Criterios EXACTOS extraídos — no genéricos:

| Referencia | Criterio operativo exacto |
|---|---|
| **MarketCheck** (US, peer MÁS directo) | ~84.000 webs de dealer + microsites OEM + clasificados, scrapeados/normalizados/dedupeados con TODO el dataset en un ciclo uniforme de **24h** (rebuild de backend ~11:00 UTC diario). Una sola cadencia al universo completo — más simple que los tiers de Cardeep, pero FUNCIONANDO a diario desde hace años. |
| **AutoTempest** (US, meta-buscador líder) | La arquitectura deliberadamente MÁS POBRE: feeds/API solo de socios; para lo no-socio (Craigslist, FB Marketplace...) NO scrapea ni guarda nada — genera un deep-link de búsqueda y redirige fuera. Sin base propia del long-tail. Mide cuánto más ambicioso es Cardeep. |
| **DataOne Software** (US) | Modelo COOPERATIVO: feed diario que entrega el propio dealer/DMS; el coche vendido sale del feed el MISMO DÍA; enriquecimiento VIN cruzando DOS fuentes independientes (OEM Build Data + Verified Records). |
| **Google Crawl Budget** (doc oficial) | Tasa de rastreo = CAPACIDAD (sube con respuestas rápidas sostenidas, baja de inmediato ante 5xx/timeout) × DEMANDA (popularidad + frecuencia de cambio observada). Fórmula ADAPTATIVA de dos factores, no tabla estática. |
| **Heritrix3** (Internet Archive) | delay = max(minDelayMs, delayFactor × duración del último fetch al host); UNA conexión por host; `AdaptiveRevisitingFrontier` varía el intervalo de revisita POR URL según cambio de contenido observado (WaitEvaluator/ChangeEvaluator). |
| **Cho & Garcia-Molina** (Stanford 2003; INRIA 2020) | Estimador matemáticamente óptimo de frecuencia de cambio POR FUENTE desde historial incompleto/censurado ("cambió desde la última visita"). Mejora de frescura probada: **35%** frente a tasas ingenuas. Publicado hace >20 años. |
| **Apache StormCrawler** | Politeness particionada por hostname ANTES del fetch en clúster distribuido; estado de URL y próximo-fetch-time PERSISTIDOS (Elasticsearch) → el calendario sobrevive a reinicios y escala añadiendo workers. |
| **Netflix Hystrix** (parámetros publicados) | Circuito ABRE con ≥20 peticiones en ventana de 10s Y error rate >50%; tras sleep window de 5s deja pasar UNA sonda (HALF-OPEN); éxito ⇒ auto-CLOSE, fallo ⇒ re-OPEN. Auto-recuperación total, cero intervención manual. |
| **Michael Nygard, Release It! (2007)** | Los dos patrones anti-cascada más efectivos son Circuit Breaker y Timeout usados JUNTOS — un breaker sin presupuesto de timeout forzado por llamada es una implementación incompleta. |
| **Bright Data** | 72M+ IPs residenciales en 195 países + 98 nodos datacenter + 5.000+ operadores móviles; rotación automática con sesiones pegajosas de 1 min a 24h. Estado comercial del arte anti-ban Tier-1. |
| **Zyte API** | Ante rate-limit/ban: backoff exponencial con jitter, reintentar PARA SIEMPRE (no N intentos y rendirse), espaciado generoso — documentado explícitamente. |
| **Common Crawl** | Ancla de techo de escala: ~2,3 mil millones de páginas / ~400 TiB por snapshot mensual. NO es análogo vertical — citado solo como referencia de escala. |
| **Splink** (MoJ UK, open-source) | Resolución de entidades Fellegi-Sunter: blocking rules deterministas baratas → scoring probabilístico con ajuste por frecuencia de término. Benchmark: 1M registros <2 min en portátil (DuckDB); 100M+ vía Spark. |
| **DGT Parque de Vehículos / INE CNAE** (ES) | Ground truth oficial externo contra el que la propia `v_province_seal` ya se autoevalúa (referenciado en docs/ai/audits/DEDUP_IDENTITY_AUDIT.md, 02, 06). [VERIFICADO grep interno] |

**Resultado negativo honesto**: AutoScout24 (tech.autoscout24.com), OLX Group y
Adevinta/coches.net — los tres mayores operadores de clasificados de Europa y el peer-set
real del horizonte EU — NO publican nada de su ingeniería de crawler/harvest/dedup (solo
posts de plataforma de datos, Kubernetes y ML de personalización). No se puede comparar
punto por punto contra ellos; es una laguna de la industria, no de esta investigación.

---

## 3. Objetivo Cardeep para este pilar — y el límite honesto

### Veredicto sin maquillaje

La ventaja estructural de Cardeep es REAL pero está en el MODELO DE DATOS, no en el motor:
ninguna de las 14 referencias documenta públicamente un equivalente al par
`vehicle_event` append-only (altas/bajas/precio/foto con historial completo,
`migrations/0003_vehicles_events.sql:33`) + VAM como capa de consenso por señal + dedup
cross-platform de unidad física (`migrations/0023_vehicle_cluster.sql`). La ambición de
llegar al "garaje perdido en la montaña" que ningún feed provider toca no tiene análogo
público. Eso es un diferencial de ALCANCE genuino.

Pero en la ingeniería del motor, Cardeep está HOY POR DEBAJO del estándar resuelto, en
tres dimensiones concretas y verificadas:

1. **Auto-recuperación**: breaker de Cardeep abre a 3 fallos y queda abierto
   INDEFINIDAMENTE (6/56 fuentes excluidas ahora, 2 Tier-1). Hystrix lo resolvió en 2011
   con half-open automático cada 5s. Estrictamente menos capaz que el patrón de referencia.
2. **Frescura**: tabla estática de 4 tiers (24h/168h/720h/2160h) frente al estimador
   dinámico por fuente de Cho & Garcia-Molina (2003, +35% frescura probada). MarketCheck
   ni siquiera lo necesita: 24h uniforme a 84.000 fuentes, en producción real.
3. **Distribución**: governor single-process con el upgrade hook P2 (Redis GCRA)
   documentado pero sin construir (governor.py:22-28; confirmado por ausencia total de
   `redis` en el módulo) frente a StormCrawler distribuido de fábrica. Para el horizonte
   EU es sustrato que falta CONSTRUIR, no activar.

Y la brecha decisiva no es de algoritmo sino de OPERACIÓN: el pilar se llama "motor de
indexación" y el motor lleva 18 días muerto por falta del primitivo operativo más básico
(supervisión de proceso). La mejor racha probada de Cardeep es ~1 mes; MarketCheck y
Common Crawl tienen años de operación ininterrumpida. En la dimensión que da nombre al
pilar, Cardeep hoy está en cero frente a cualquier referencia seria.

> **Actualización F3/F4 (2026-07-17/18)**: los puntos 1 y 2 de este veredicto quedaron
> cerrados por ejecución — ver §9 F3/F4 para la evidencia completa. Punto 1 (auto-
> recuperación) tenía un matiz que solo se descubrió al ejecutar: el half-open YA estaba
> construido en `pipeline/ops/health.py` (0013), simplemente inalcanzable desde el
> scheduler real — corregido sin migración. Punto 2 (frescura adaptativa) se construyó y
> se MIDIÓ contra 90 días reales: el mecanismo funciona, pero el apagón de 18 días deja
> HOY sin muestra suficiente a las fuentes que más se beneficiarían (168h/720h/2160h) —
> mejora medida = 0% en las 7 fuentes que sí calificaron (ya estaban a la cadencia
> correcta), hueco declarado para 30-60 días vista. Punto 3 (distribución/governor Redis)
> sigue exactamente como se describe aquí — está gated a F7, fuera del alcance de F3/F4.

### Objetivo del pilar (en orden de dependencia real)

1. **Motor que no se cae** — supervisión externa al proceso + watchdog independiente del
   scheduler. Un segundo apagón silencioso de 18 días debe ser IMPOSIBLE por construcción.
2. **Motor que se cura solo** ✅ — breaker half-open estilo Hystrix: una fuente sana vuelve
   sola al servicio, sin diagnóstico manual. Cerrado en F3 (§9).
3. **Motor que aprende su cadencia** ✅ — estimador de frecuencia de cambio por fuente
   (Cho & G-M) alimentado por el historial `vehicle_event` que YA existe, sustituyendo
   gradualmente la tabla estática de tiers. Construido y medido en F4 (§9); rollout
   gradual real (7/56 fuentes) — el resto espera muestra suficiente.
4. **Track record medible** — uptime del motor y frescura por fuente como métricas de
   primera clase, servidas por la API y visibles en el frontend. La superioridad no se
   afirma: se demuestra con serie temporal.

### Por qué puede superar a la referencia — y dónde no puede

**Puede**: en PROFUNDIDAD por mercado. MarketCheck cubre anchura (84k dealers, US) con
snapshot diario; Cardeep puede ser el único censo de España con delta completo por
vehículo, dedup de unidad física cross-platform y verificación de consenso por señal —
una capa de verdad que el ciclo de 24h de MarketCheck no produce. El motor no necesita
ser más grande que el de MarketCheck: necesita ser más profundo y estar VIVO.

**No puede (límite honesto)**: igualar la infraestructura anti-ban comercial (Bright Data
72M IPs) a coste €0. El hueco Tier-1/WAF es real: Obscura/Camoufox siguen SIN benchmark
contra WAFs reales (declarado en CLAUDE.md del repo). Mientras no se cace la receta por
plataforma, las Tier-1 duras seguirán siendo el techo de cobertura — se declara como
techo, no se maquilla. Tampoco puede afirmar todavía fiabilidad operativa: el track
record se construye en F1-F6, no se proclama.

---

## 4. Criterios de evaluación CONCRETOS (qué se muestra y cómo se calcula)

Cada número/badge/sección del frontend traza a un criterio de esta tabla. Nada aleatorio.

| Elemento mostrado | Cálculo exacto | Fuente de datos (verificada) |
|---|---|---|
| **Badge global del motor**: `LATIENDO / DEGRADADO / PARADO` | `LATIENDO` si `now() - scheduler_lease.last_heartbeat < 2 × TICK_INTERVAL` (= 30 min, TICK en scheduler.py:121); `DEGRADADO` si < 24h; `PARADO` si ≥ 24h o sin fila | `scheduler_lease` (migrations/0054_scheduler_heartbeat.sql:28) vía endpoint nuevo (F5) |
| **Frescura por fuente**: `FRESCA / RETRASADA / MUERTA` | `FRESCA` si `now() - last_ok ≤ harvest_interval_hours`; `RETRASADA` si ≤ 2× intervalo; `MUERTA` si > 2× (mismo umbral que el silence_watchdog, scheduler.py:17-19) | `source_health.last_ok` + `harvest_interval_hours` (0004:24 + 0021:13), servido por `/sources` (ops.py:156) |
| **Estado de breaker por fuente**: `CERRADO / ABIERTO / SONDA` | `ABIERTO` si `consecutive_fails ≥ 3` (0004:28); `SONDA` = estado half-open nuevo de F3 | `source_health.consecutive_fails` + columnas nuevas F3 |
| **Cobertura por provincia**: `SELLADO / PARCIAL / GAP` + % nacional | Directo de la view — misma cifra que el sello del producto (79,7% congelado hoy); NUNCA recalculada en frontend | `v_province_seal` (0042/0043/0059:324) vía `/geo/seal` (geo.py:105) |
| **"Datos de hace X"** (por dealer/provincia) | `now() - max(vehicle_event.observed_at)` filtrado por entidad o provincia — independiente de source_health (ver §7) | `vehicle_event` (0003:33) vía `/entities/{cdp_code}/delta` (entities.py:171) |
| **Alertas abiertas**: contador por severidad | `COUNT(*) WHERE resolved IS NULL GROUP BY severity` — hoy daría 9 critical + 50 warning | `alert` (0004:34) vía `/alerts` (ops.py:101) |
| **Uptime del motor** (serie 30/90 días) | % de ventanas de 15 min con heartbeat presente en el ledger nuevo de F6 (hoy IMPOSIBLE de calcular: `scheduler_lease` guarda solo el último heartbeat, no historia) | tabla nueva F6 (§5) |
| **Progreso de replay de arranque en frío** | `fuentes procesadas desde el arranque / fuentes DUE al arrancar` — visible solo durante replay (F2) | `source_health` (delta de `last_ok` post-arranque) |
| **Separación Tier-1 vs resto** | Filtro duro por `is_tier1` (0002:26, 0013:61) y grupos de 0016 — nunca mezclados en una misma lista, mandato del CLAUDE.md del repo | `entity.is_tier1` + `source_health.is_tier1` + 0016_tiering_groups |

Regla de oro: si un dato falla su verificación cruzada (§7), el frontend muestra estado
`SIN VERIFICAR` explícito — nunca el último valor bueno disfrazado de actual.

---

## 5. Modelo de datos + almacenamiento backend

### Se REUTILIZA (existente, verificado en migraciones/código — cero tabla inventada)

| Objeto | Creado en | Papel en este pilar |
|---|---|---|
| `source_health` | migrations/0004_verification_health.sql:24 (+0013 tuning/is_tier1, +0021 harvest_interval_hours, +0024 coverage) | Registro maestro de las 56 fuentes: cadencia, breaker, last_ok/last_fail |
| `alert` | migrations/0004_verification_health.sql:34 | Alertas con dedup por origin y severidad (ladder en docs/runbook/OPERATE.md) |
| `scheduler_lease` | migrations/0054_scheduler_heartbeat.sql:28 | Lease + heartbeat del productor único (hoy: 1 fila muerta) |
| `apscheduler_jobs` | creada por SQLAlchemyJobStore de APScheduler (scheduler.py:4-5) | Persistencia de los 8 jobs; sobrevive reinicios |
| `vehicle_event` | migrations/0003_vehicles_events.sql:33 | Ledger append-only NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE — insumo del estimador de cadencia F4 y de la frescura §4 |
| `entity` / `entity_source` | migrations/0002_entities.sql (entity_source en :43, is_tier1 en :26) | Censo de dealers y procedencia por fuente |
| `v_province_seal` | migrations/0042 (:18), 0043, recreada 0059:324 | Sello de cobertura por provincia/segmento |
| Tiers granulares | migrations/0016_tiering_groups.sql | Separación Tier-1/grupos exigida en frontend |
| API `/health` `/stats` `/alerts` `/sources` | services/api/routers/ops.py:26,48,101,156 | Superficie ops existente — F5 la extiende, no la duplica |
| API `/geo/seal` `/geo/completeness` `/geo/exhaustiveness` | services/api/routers/geo.py:105,32,168 | Cobertura servida — el frontend consume esto, no SQL propio |
| `pipeline/ops/scheduler.py`, `pipeline/ops/silence_watchdog.py`, `pipeline/ops/lock_heartbeat.py` | código vivo | El motor mismo — F3/F4 lo modifican, no lo reescriben |
| `pipeline/engine/governor.py` | código vivo | Rate-limit por host — F7 le añade el backend Redis ya previsto en su docstring (:24-28) |
| `docker-compose.yml` servicio `autopilot` | docker-compose.yml:63-72 | El supervisor Docker YA definido y nunca usado — F0 lo estrena |

### Se CREA nuevo (nombres PROPUESTOS — no existen hoy; nacen por migración numerada)

1. **`engine_heartbeat_log`** [NUEVO, propuesta F6] — historia append-only de heartbeats
   (hoy `scheduler_lease` es UPSERT de una fila: el uptime histórico es incalculable).
   Columnas mínimas: holder, pid, beat_at. Retención acotada (p.ej. 90 días) para respetar
   la doctrina anti-dead-tuples del stack (INSERT-only + purga por rango).
2. **Columnas de half-open en `source_health`** [CORREGIDO en F3 — NO hicieron falta].
   La sección original de esta carta asumía que había que crear `breaker_opened_at`,
   `next_probe_at`, `probe_inflight`. Ejecutando F3 se verificó [VERIFICADO,
   `pipeline/ops/health.py` + `migrations/0013_resilience.sql:19-26`] que la tabla
   `source_breaker` (creada en 0013, MESES antes de esta carta) YA tiene
   `state CHECK IN ('closed','open','half_open')`, `opened_at`, `cooldown_until` — el
   estado half-open que el §3 de esta misma carta declaraba inexistente. `record_run()` y
   `is_open()` en `health.py` YA implementaban la máquina de estados Hystrix casi completa
   (trip exponencial, transición a half-open tras cooldown). Lo que faltaba de verdad —
   confirmado leyendo `pipeline/ops/scheduler.py:_due_sources()` — es que el SCHEDULER
   nunca consultaba `source_breaker`: excluía por `source_health.consecutive_fails >= 3`
   de forma PERMANENTE, sin dimensión temporal, dejando el mecanismo de auto-recuperación
   ya construido inalcanzable desde el motor real. F3 cerró la brecha SIN migración: solo
   código (scheduler.py LEFT JOIN + `_breaker_decision`/`_prepare_launch`; health.py añadió
   jitter al backoff y corrigió `is_open()` para bloquear una segunda sonda concurrente
   durante half-open, que antes de F3 se permitía por error). Detalle completo en F3 más
   abajo.
3. **Columnas de estimador de cambio en `source_health`** [CONSTRUIDO en F4,
   `migrations/0076_adaptive_cadence.sql`]: `observed_change_rate` (λ estimada Cho&G-M),
   `cadence_mode` (`static`/`adaptive`, default `static` — cero fila existente cambia de
   comportamiento), `computed_interval_hours`, `cadence_computed_at`. La tabla de tiers
   (`harvest_interval_hours`, 0021) queda como piso/techo de seguridad y como el valor
   efectivo para toda fuente aún en modo `static` — no se borra, no se toca su default.
4. **Endpoint `/engine/status`** [NUEVO, F5] en ops.py: expone badge global (§4),
   lease/heartbeat, replay-progress y uptime. `/health` NO se toca (contrato de liveness
   barato, ops.py:29-37 lo documenta).
5. **Supervisor externo** [NUEVO, F0/F1 — no es tabla]: en este host Windows, el servicio
   `autopilot` de docker-compose (ya definido) O un servicio nativo (NSSM/Task Scheduler).
   Decisión en F0 con criterio explícito. Para el VPS Linux futuro ya existen las unidades
   systemd inertes (ops/systemd/).

Sin ClickHouse, sin Redis nuevo en este pilar (Redis solo entra en F7, y como upgrade ya
documentado por el propio governor). PG sigue siendo primario, doctrina del stack.

---

## 6. Especificación de pantalla/sección en el frontend

Superficie existente verificada: `web/src/pages/` contiene Dashboard.tsx, Marketplace.tsx,
Inteligencia.tsx, etc., con layout en `web/src/layout/Shell.tsx`. [VERIFICADO listado]

Dos superficies, dos audiencias, un mismo dato de origen:

### 6a. Para el dealer (integrado en Dashboard/Marketplace — NO página nueva de ops)

El dealer no sabe qué es un scheduler ni le importa. Lo que le quita el sueño es:
*"¿estos datos son de verdad y son de hoy?"* y *"¿está toda mi competencia aquí o me
enseñáis media provincia?"*. En su lenguaje:

- **Sello de frescura por listado/dealer**: "Inventario comprobado hace 3 h" — calculado
  de `vehicle_event.observed_at` (§4, fila 5). Si la fuente está MUERTA: "Última
  comprobación: 28 de junio" en ámbar — la fecha real, nunca ocultada. La honestidad del
  dato ES el producto.
- **Cobertura de SU zona, en su idioma**: "Tu provincia: 41 de 44 vendedores profesionales
  detectados están indexados (SELLADO al 93%)" — directo de `v_province_seal` vía
  `/geo/seal`. Un dealer de Cuenca ve Cuenca, no un KPI nacional.
- **Separación que el dealer entiende**: "Portales grandes" (Tier-1) vs "vendedores
  directos" (resto) — el filtro `is_tier1` con etiquetas humanas, nunca la palabra "tier".
- **Regla dura anti-atrezzo**: ningún número de esta superficie puede venir de una
  constante hardcodeada. El patrón mock de Inteligencia.tsx (documentado en la carta 01)
  queda PROHIBIDO en este pilar desde el primer commit.

### 6b. Para el owner/operador (sección "Sala de máquinas" — puede vivir bajo /portal o ruta interna)

- **Cabecera**: badge `LATIENDO / DEGRADADO / PARADO` (§4, fila 1) + "último latido hace
  X min" + uptime 30/90 días (F6). Grande, arriba, imposible de ignorar: la lección del
  apagón invisible de 18 días hecha interfaz.
- **Tabla de 56 fuentes** (de `/sources`, ops.py:156): nombre, tier/grupo, frescura
  (§4 fila 2), breaker (§4 fila 3), última cosecha, filas de la última corrida. Orden por
  defecto: más-vencida primero — el mismo orden que usa `_due_sources`.
- **Panel de alertas** (de `/alerts`, ops.py:101): las 59 abiertas de hoy visibles con
  severidad y origen exacto; acción de resolución manual traza a la ladder de OPERATE.md.
- **Durante replay de arranque en frío** (F2): barra "Replay: 23/54 fuentes procesadas,
  ~Xh restantes" — el estado transitorio se muestra como transitorio, no como régimen.

---

## 7. Protocolo de verificación (2 vías independientes por dato mostrado)

El mismo estándar antialucinación del proyecto, aplicado al producto. Un dato solo se
muestra como bueno si DOS caminos que no comparten escritor coinciden:

| Dato mostrado | Vía A | Vía B (independiente) | Si discrepan |
|---|---|---|---|
| Motor vivo | `scheduler_lease.last_heartbeat` (escrito por lock_heartbeat) | `apscheduler_jobs.next_run_time` avanza entre dos lecturas separadas ≥15 min (escrito por APScheduler, código distinto) + healthcheck del supervisor (docker `Status=healthy` o servicio Windows `Running`) | Badge `PARADO` + alerta critical — nunca "live" por una sola vía |
| Frescura por fuente | `source_health.last_ok` (escrito por record_run del conector) | `max(vehicle_event.observed_at)` de esa fuente (escrito por el pipeline de ingesta, tabla distinta) | Estado `SIN VERIFICAR`; discrepancia >1 intervalo abre alerta warning (detecta conector que "corre" sin ingerir — modo de fallo real) |
| Cobertura provincial | `v_province_seal` (agregado interno) | Censo externo DGT/INE — el mismo ground truth que ya usan las auditorías internas (DEDUP_IDENTITY_AUDIT.md) | Se muestra el % interno CON el delta vs censo externo anotado; nunca solo el número que más favorece |
| Conteos de producto (/stats) | Endpoint `/stats` (ops.py:48) | Re-derivación SQL directa periódica por camino distinto al del endpoint (job de QC, no el mismo query cacheado) | Alerta + se sirve el menor de los dos con marca |
| Breaker abierto | `consecutive_fails` en source_health | Últimos N registros de corrida de esa fuente muestran fallo real (la corrida cruda, no el contador) | El contador NO se resetea a mano sin evidencia de la vía B |
| Alertas abiertas | tabla `alert` | El origen citado por la alerta se re-comprueba en su tabla fuente antes de mostrar detalle (p.ej. una alerta de silencio se cruza contra last_ok real) | La alerta se marca `stale` si el origen ya no reproduce |

Principio de diseño: las vías A y B nunca comparten el mismo código escritor. Es la
generalización del hallazgo del RECON — el watchdog murió con el vigilado porque
compartían proceso; aquí ningún verificador comparte proceso con lo verificado.

---

## 8. Uso de LLM (doctrina €0 del CLAUDE.md: local para lo masivo, caro solo para decidir)

Infraestructura verificada: Ollama vivo en el host (HTTP 200 en :11434, RECON) y ya
cableado en docker-compose.yml:49-50 (`CARDEEP_OLLAMA_URL`, `CARDEEP_LLM_MODEL=qwen2.5:7b`).

### Corre con modelo LOCAL/barato (masivo, verificable, fuera del camino crítico)

- **Clasificación de texto de alertas y errores de conector**: agrupar stack traces y
  mensajes de fallo por causa probable ANTES del triage humano (las 59 alertas abiertas
  son el primer caso de uso real). Salida = sugerencia etiquetada, nunca auto-resolución.
- **Parseo de fichas de dealer no estructuradas** en fuentes long-tail donde la receta
  determinista no extrae un campo: el LLM local propone, un validador de esquema
  determinista acepta/rechaza. El LLM jamás escribe directo a la DB.
- **Explicación de candidatos de dedup**: anotar por qué dos listados parecen la misma
  unidad física — como ayuda al revisor. El matching en sí NO es LLM: el patrón correcto
  es Splink-style (blocking determinista + scoring probabilístico, §2), más barato,
  reproducible y auditable que cualquier modelo generativo.

### JUSTIFICA modelo caro (decisiones puntuales, alto coste de error, baja frecuencia)

- **Caza de receta Tier-1**: decidir la estrategia anti-WAF por plataforma dura
  (combinación Camoufox/Obscura/curl_cffi, orden de sondas, presupuesto) — pocas
  decisiones, cada una condiciona semanas de cosecha.
- **Diagnóstico de breaker abierto con evidencia ambigua**: cuando la vía B (§7) no da
  causa clara (¿ban? ¿rediseño del site? ¿DNS?) y el coste de reintentar a ciegas es
  quemar el host.
- **Revisión de arquitectura de las fases F3/F4/F7** antes de ejecutar (patrón ya operativo
  del proyecto: razonamiento profundo vía subagente, ejecución en Sonnet).

### Explícitamente SIN LLM (doctrina de indexado pasivo, memoria del proyecto)

El camino crítico del motor — scheduling, fetch, rate-limit, breaker, ingesta, delta —
es 100% determinista. Ningún LLM decide si una fuente está DUE, si un breaker abre, ni
qué se ingesta. La IA queda fuera del camino crítico por mandato previo del owner.

---

## 9. Fases de construcción (orden estricto; cada una con criterio de verificación real)

> Autoridad asumida: reemplazar/reestructurar código existente donde haga falta.
> Ninguna fase se declara cerrada por "deploy y ya": cada una exige build + test +
> revisión real + evidencia por 2 vías.

**F0 — Rebuild + arranque supervisado (el botón, bien pulsado)**
Rebuild de `cardeep-app:latest` desde main actual (borra el drift de 5 commits/17 días);
aplicar migraciones pendientes si las hay; decisión documentada del supervisor en este
host (opción A: `docker compose up -d autopilot` — ya definido, docker-compose.yml:63-72;
opción B: servicio nativo Windows). Criterio de decisión explícito: fiabilidad de
`restart: unless-stopped` + acceso del contenedor al host (Ollama vía host.docker.internal
ya resuelto, docker-compose.yml:49) vs. overhead de mantener imagen.
✔ Verificación: contenedor/servicio `Up`; `scheduler_lease.last_heartbeat` avanza en 2
lecturas separadas ≥30 min; `apscheduler_jobs.next_run_time` descongelado (las 2 vías de
§7); primera fuente cosechada con filas nuevas en `vehicle_event` posteriores a la fecha
de arranque. Test de la causa raíz: cerrar la terminal/sesión que lo lanzó y confirmar a
las 24h que sigue latiendo.

**F1 — Watchdog EXTERNO al proceso (que el apagón invisible sea imposible)**
Monitor fuera del scheduler (tarea programada del host o healthcheck del supervisor) que
lee `scheduler_lease.last_heartbeat` y, si supera el umbral (§4), inserta alerta critical
en `alert` Y notifica por canal externo a la DB (el apagón de la DB también debe verse).
✔ Verificación: test destructivo real — matar el proceso del scheduler a propósito y
medir tiempo-hasta-alerta (<30 min); matar también la DB y confirmar notificación externa.
Sin este test ejecutado y cronometrado, F1 no está cerrada.

**F2 — Replay de arranque en frío gestionado + triage de los 6 breakers**
Cuantificar el replay (54+ fuentes DUE simultáneas, en serie, hasta 4h/fuente): medirlo,
documentarlo en OPERATE.md (hueco declarado del RECON) y exponer progreso (§6b). Triage
manual de las 6 fuentes con breaker abierto por la vía B de §7; refrescar
`state/validation_matrix.json` (hoy ~1 mes stale) contra la flota real.
✔ Verificación: replay completado con log por fuente; cifra de `v_province_seal` se MUEVE
(hoy congelada en 79,7% — el primer delta es la prueba de vida del producto); cada uno de
los 6 breakers con diagnóstico escrito (revivida o causa raíz documentada); matriz de
validación re-fechada.

**F3 — Breaker half-open auto-recuperable (cerrar el gap vs. Hystrix 2011) — ✅ CERRADA
2026-07-17/18, verificación en vivo confirmada (incluye un bug real de doble-reclamo
cazado, corregido y re-verificado en la misma sesión — ver punto 3)**

Hallazgo previo a construir nada [VERIFICADO, leído el código]: `pipeline/ops/health.py`
(`record_run`/`is_open`) YA implementaba, desde antes de esta carta, casi toda la máquina
de estados Hystrix sobre `source_breaker` (0013): trip exponencial con cooldown, y
transición a `half_open` tras cooldown. Pero `pipeline/ops/scheduler.py::_due_sources()`
NUNCA consultaba `source_breaker` — excluía por
`source_health.consecutive_fails >= BREAKER_TRIP_AT` de forma PERMANENTE (sin cooldown, sin
reloj), dejando el mecanismo de auto-recuperación ya construido INALCANZABLE desde el motor
real. Confirmado en vivo antes de tocar nada: 7 fuentes con `cooldown_until` vencido hacía
horas seguían excluidas del `--dry-run` (`coches_net_wholesale`, `family_builder_wholesale`,
`family_framework_webbuilder`, `family_unreachable`, `group_rentacar_vo_recordgo`,
`group_vo_chains_carplus`, `motorflash_wholesale`). El gap real no era "no existe half-open"
sino "el scheduler no lo mira". Corrección de esta carta: la fila 2 de §5 (creación de
columnas nuevas) queda anulada — cero migración para F3.

Construido (TDD, RED→GREEN, sin excepción):
- `_breaker_decision(state, cooldown_until, now)` [scheduler.py] — función pura
  CLOSED/None→`allow`, OPEN+cooldown futuro→`skip`, OPEN+cooldown vencido→`probe`,
  HALF_OPEN→`skip` (una sonda ya en curso). 7 tests unitarios sin DB
  (`tests/test_scheduler_half_open.py::TestBreakerDecision`).
- `_due_sources()` — LEFT JOIN a `source_breaker`; incluye como candidato "probe" a toda
  fuente OPEN con cooldown vencido (el fix). Contrato externo (tupla de 4) sin cambios.
- `_prepare_launch(source_key)` — re-chequeo de FRESCURA (solo lectura, sin CAS) justo
  antes de lanzar el subproceso, para el caso de una tanda DUE larga donde fuentes previas
  ya consumieron horas del mismo tick. **La reclamación real del cupo half-open NO vive
  aquí** — ver el incidente en vivo documentado abajo, que es exactamente por qué.
- `health.py::is_open()` — CORREGIDO en dos sentidos: (a) antes de F3 devolvía `False`
  (permitido) para CUALQUIER estado distinto de `open`, incluido `half_open` — permitiendo
  más de una sonda concurrente durante la ventana half-open; ahora `half_open`→bloqueado
  (Hystrix: exactamente una petición en vuelo), vía CAS atómico. (b) Este `is_open()` — NO
  `_prepare_launch()` — es el ÚNICO lugar del sistema donde el cupo half-open se reclama de
  verdad (lo llama cada conector antes de su propio scrape).
- `health.py::_compute_backoff_cooldown_seconds()` — NUEVO: jitter ±20% (patrón Zyte, §2)
  sobre el backoff exponencial ya existente (base 900s, techo 24h) — antes de F3 el cooldown
  era determinista, sin jitter (riesgo de sondas sincronizadas si varias fuentes abren a la
  vez). `rng` inyectable para test determinista.
- Suites nuevas: `tests/test_scheduler_half_open.py` (20) + `tests/test_breaker_jitter_and_half_open.py`
  (8) = 28 tests, todos verdes (incluye la reescritura post-incidente de `TestPrepareLaunch`
  y `TestFullTransitionLiveDB` para la semántica de solo-lectura corregida). `tests/
  test_scheduler_due.py` actualizado (3 tests que asumían el mecanismo viejo, reescritos a
  la semántica real de breaker; 19 tests verdes, 0 regresión). `tests/test_resilience_loop.py`
  + `tests/test_autorepair_loop.py` (18 tests pre-existentes) verdes sin cambios — el fix no
  rompe el comportamiento ya probado.

✔ Verificación (real, no maquillada):
1. **TDD**: tests de transición escritos y en RED antes de implementar `_breaker_decision`/
   `_prepare_launch` (confirmado: `ImportError` al importar antes de escribir el código);
   GREEN tras implementar.
2. **Integración sintética**: `TestFullTransitionLiveDB` (DB real :5433, clave sintética
   `__f3_half_open_scheduler_test__`, limpiada en `finally`) — CLOSED→(3 fallos reales vía
   `record_run`)→OPEN→(cooldown forzado al pasado)→`_due_sources()` la incluye como
   probe→`_prepare_launch()` re-confirma elegibilidad (solo lectura, idempotente)→el propio
   `is_open()` del conector reclama el cupo half-open (True→bloqueado en la segunda
   llamada, exactamente-una-sonda)→sonda falla→re-OPEN con backoff MÁS profundo que el
   primer trip (medido, no asumido)→sonda alternativa con éxito→CLOSED. Los 2 tests pasan.

Corroboración independiente [VERIFICADO, `docs/runbook/OPERATE.md:118-119`]: el runbook
operativo YA documentaba, como diseño intencional, "El scheduler salta las fuentes con
breaker `open` hasta `cooldown_until` — no se quema una fuente ya caída" — una afirmación
que era FALSA en el código real antes de F3 (el scheduler ignoraba `cooldown_until` por
completo). F3 no inventa comportamiento nuevo: hace que el código cumpla lo que el propio
runbook ya prometía.

3. **En vivo, sin intervención manual — INCLUIDO UN BUG REAL CAZADO Y CORREGIDO EN LA MISMA
   SESIÓN** [VERIFICADO-RECON 2026-07-17/18]: estado real ANTES del fix — 7 fuentes con
   `source_breaker.state='open'` y `cooldown_until` vencido entre 1h y 5h antes (consultado
   en vivo), permanentemente excluidas del scheduler.

   **Primer despliegue (roto, detectado en el acto)**: `docker cp` de `scheduler.py` +
   `health.py` + `cadence_estimator.py` a `cardeep-autopilot` (NO rebuild de imagen — ver
   nota de aislamiento) + `docker restart`. Tick de las 23:02:48Z: log confirma las 7
   fuentes correctamente detectadas `PROBE-ELIGIBLE`, el CAS de `_prepare_launch` reclama
   el cupo y lanza el subproceso — pero CADA UNO de los 7 conectores, al arrancar, hace su
   PROPIO chequeo interno `is_open()` (llamada independiente, vía asyncpg, desde dentro del
   subproceso) — y como `_prepare_launch` YA había puesto `source_breaker.state='half_open'`
   un instante antes, el `is_open()` del propio conector veía el cupo "ya reclamado por
   otro" (mi propia corrección de Hystrix, que bloquea una SEGUNDA llamada durante
   half-open) y abortaba de inmediato ("breaker OPEN; skipping drain") — sin ejecutar el
   scrape real ni llamar a `record_run()`. Confirmado en vivo con SQL directo tras el tick:
   las 7 filas de `source_breaker` habían quedado en `state='half_open'` PERMANENTEMENTE
   (peor que el bug original: ahora ni siquiera el reintento normal las tocaría, porque
   `_breaker_decision()` excluye `half_open` incondicionalmente y nada volvía a llamar
   `record_run()` para resolverlas) — cero filas nuevas en `harvest_run` para las 7 en los 5
   minutos posteriores al tick, confirmando que ninguna llegó a intentar el scrape real.

   **Causa raíz**: dos gates independientes (el CAS de `_prepare_launch` en el scheduler, y
   el `is_open()` que cada conector llama por su cuenta) reclamando el MISMO cupo
   half-open — el segundo veía el reclamo del primero como "otro llamante concurrente" y se
   bloqueaba a sí mismo.

   **Corrección** (mismo commit, antes de cerrar F3): `_prepare_launch` se redujo a un
   re-chequeo de solo-lectura (sin CAS, sin mutación) — la reclamación atómica real del
   cupo half-open vive EXCLUSIVAMENTE en `health.py::is_open()`, que cada conector ya
   llamaba. `tests/test_scheduler_half_open.py::TestPrepareLaunch` y
   `TestFullTransitionLiveDB` reescritos para la semántica correcta (6+2 tests, verdes).
   Reparación de los datos dañados por el bug: las 7 filas `half_open` restauradas a `open`
   (con su `cooldown_until` ya vencido intacto — corrección reversible de mi propio error,
   no un maquillaje). Redeploy: `docker cp` del `scheduler.py` corregido + `docker restart`
   (23:07:59Z).

   **Segunda verificación (post-fix) — ✅ CONFIRMADA, tick real de las 23:22:59Z-23:25:04Z**:
   log completo, las 7 fuentes procesadas en serie, CADA UNA con un intento REAL (ninguna
   se auto-bloqueó en `is_open()`):
   - `family_unreachable`: crash antes de `record_run` — `RuntimeError: Tier-1 engine needs
     Playwright... No module named 'playwright'` (dependencia no instalada en el
     contenedor, red de seguridad `_record_crash_if_unrecorded` grabó el fallo).
   - `family_framework_webbuilder`: corrió completo (8 dealers candidatos, fingerprint por
     dealer), se auto-reportó `ok=False` ("VAM verdict UNVERIFIED").
   - `family_builder_wholesale`: crash — `FileNotFoundError:
     /app/docs/_longtail_fingerprints.json` (fichero de receta ausente en el contenedor).
   - `group_vo_chains_carplus`: corrió completo, se auto-reportó `ok=False` ("VAM verdict
     TRUSTWORTHY" — el propio conector decidió no marcar éxito pese al verdict; sin
     rascar más hondo, fuera de alcance de F3).
   - `motorflash_wholesale`: corrió, se auto-reportó `ok=False` ("Tier-1 chain exhausted...
     camoufox not installed").
   - `group_rentacar_vo_recordgo`: corrió, se auto-reportó `ok=False` ("SSL certificate...
     has expired").
   - `coches_net_wholesale`: crash — `RuntimeError: HTTP 400 on
     https://web.gw.coches.net/search` (la API externa devolvió 400).

   Resultado SQL tras el tick: las 7 filas de `source_breaker` — CERO quedaron en
   `half_open` (el bug del primer intento no se repite); las 7 volvieron a `open` con
   `consecutive_fails` incrementado correctamente (4, salvo `group_vo_chains_carplus` que
   ya iba en 4→5) y `cooldown_until` genuinamente MÁS profundo que antes del tick (p.ej.
   `motorflash_wholesale`: de 13:11:48Z a 23:59:16Z). Las 7 tienen fila NUEVA en
   `harvest_run` con su motivo real y distinto de fallo.

   **Lectura honesta**: el mecanismo de auto-recuperación queda demostrado end-to-end con
   datos reales — las 7 fuentes se re-intentaron SOLAS, sin intervención manual, cada una
   recibió un chance real (ninguna bloqueada por el propio breaker), y el resultado
   (fallo real) se procesó correctamente con backoff más profundo, nunca con exclusión
   permanente ni con doble-conteo. Que NINGUNA de las 7 tuviera éxito esta vez no es un
   fallo de F3: son 6 causas de fallo DISTINTAS y ajenas al breaker (3 dependencias no
   instaladas en la imagen del contenedor — playwright, camoufox, el fichero de
   fingerprints —, 1 certificado SSL expirado, 1 API externa devolviendo 400, y 1 conector
   que se autorrechaza por su propio gate VAM) — remediarlas es trabajo de infraestructura/
   receta (F2 triage, o una fase de mantenimiento aparte), no de este pilar. El criterio de
   F3 ("una fuente real re-entra sola sin intervención manual, con la transición visible en
   source_health") queda satisfecho: la re-entrada y la transición son reales y visibles;
   el éxito del scrape en sí depende de causas fuera del alcance del breaker.

   Nota de aislamiento: `cardeep-api` y `cardeep-autopilot` comparten UNA imagen
   (`docker-compose.yml`); un `docker compose build` en este momento habría horneado
   también los cambios EN CURSO, sin commitear, de otro frente paralelo de este mismo
   Bloque (pilar 01, `services/api/routers/vehicles.py` + `pipeline/market/*` —
   confirmado por `git status` y por una TaskList ajena visible en la sesión). `docker cp`
   de los archivos exactos que F3/F4 tocan evita desplegar código ajeno no probado por mí.

**F4 — Cadencia adaptativa por fuente (cerrar el gap vs. Cho & G-M 2003) — ✅ CONSTRUIDA Y MEDIDA 2026-07-17/18**

Migración real: `migrations/0076_adaptive_cadence.sql` — `source_health.observed_change_rate`,
`cadence_mode` (default `static`, cero fila cambia de comportamiento), `computed_interval_hours`,
`cadence_computed_at`. Aplicada en vivo (`python -m scripts.migrate up` → `applied 0076`).

Estimador `pipeline/ops/cadence_estimator.py` (TDD, RED→GREEN): MLE de Cho & Garcia-Molina
con corrección de continuidad `λ̂ = -ln((X̄+0.5)/(n+1)) / I` (evita degenerar a 0 cuando
X̄=n, o a infinito cuando X̄=0); ventanas fijas de `harvest_interval_hours` de la propia
fuente; una ventana solo cuenta si hubo AL MENOS una visita real dentro (`harvest_run.ok`);
`MIN_WINDOWS=5` como piso de confianza; `computed_interval_hours` = clamp(1/λ̂, 24h, 2160h)
— mismo piso/techo que la tabla estática. 15 tests puros (`test_cadence_estimator.py`) +
2 tests DB reales (`test_cadence_estimator_live.py`, transacción abortada — ver nota de
incidente abajo) + 4 tests de la CASE SQL en `_due_sources()`
(`test_scheduler_adaptive_cadence.py`: modo estático ignora el estimado, modo adaptativo
con intervalo MÁS CORTO adelanta la fecha DUE, con intervalo MÁS LARGO la retrasa, sin
estimado cae al estático). 21 tests, todos verdes.

`_due_sources()` extendida con un `CASE WHEN cadence_mode='adaptive' AND
computed_interval_hours IS NOT NULL THEN computed_interval_hours ELSE
harvest_interval_hours END` — tanto en el filtro DUE como en el ORDER BY. Job periódico
nuevo `cadence_estimate_job()` (cadencia diaria, `CADENCE_ESTIMATE_CADENCE_HOURS=24`):
recalcula el estimado de TODAS las fuentes registradas, escribe solo las columnas de
estimado — NUNCA cambia `cadence_mode` (eso es un paso de rollout deliberado y separado,
`scripts/enable_adaptive_cadence.py`).

✔ Verificación — backtest real (`scripts/backtest_adaptive_cadence.py`, corrido en vivo
2026-07-17T22:44:54Z, lookback 90 días, contra la 5433 real):

- **56 fuentes evaluadas. Solo 7 alcanzan `MIN_WINDOWS=5` con el estándar de producción**:
  `autocasion_wholesale`, `coches_com_wholesale`, `coches_net_wholesale`,
  `dealerprobe_ownsite`, `milanuncios_wholesale`, `motor_es_wholesale`,
  `wallapop_wholesale` — las 7 son Tier-1/24h de alta frecuencia.
- **Hallazgo honesto, no maquillado**: en las 7, `computed_interval_hours` calculado = 24h
  — EXACTAMENTE el mismo que su cadencia estática actual (λ̂ tan alto — cambian en el
  100% de las ventanas visitadas — que el estimador converge al piso). Delta de staleness
  medido: **+0.00h en las 7, 0%** — el mecanismo NO tiene margen de mejora medible HOY
  para estas fuentes, porque ya estaban a la cadencia correcta. Esto NO es un fallo del
  estimador: es la confirmación de que reconoce correctamente una fuente de alto cambio y
  no intenta espaciarla.
- **El valor real de Cho & G-M (comprimir fuentes 168h/720h/2160h de bajo cambio) NO se
  puede medir todavía con confianza de producción**: el apagón de 18 días (documentado en
  §1) truncó el historial de TODAS las fuentes de cadencia más lenta a <5 ventanas
  visitadas distintas en 90 días — matemáticamente imposible de resolver ampliando el
  lookback mientras la ventana siga atada a la cadencia propia de la fuente. **Hueco
  declarado, no maquillado**: el backtest exploratorio (umbral relajado `min_windows=2`,
  41 fuentes, marcado explícitamente BAJA CONFIANZA / no apto para rollout) muestra el
  motivo exacto por el que `MIN_WINDOWS=5` existe — con 2-4 ventanas el resultado es
  errático en ambas direcciones: `group_subastas_wholesale` (n=4) sugiere -81h de
  staleness (mejora real) mientras `group_rentacar_vo_recordgo` (n=3) sugiere +84h
  (empeoraría si se aplicara a ciegas). Ninguna de las 41 exploratorias entra en rollout.
- **Rollout aplicado** (`scripts/enable_adaptive_cadence.py --apply`, en vivo): las 7
  fuentes calificadas están en `cadence_mode='adaptive'` desde 2026-07-17T22:46Z —
  comportamiento hoy IDÉNTICO al estático (verificado, 0.00h de delta), y listo para
  comprimir/expandir automáticamente el día que su patrón de cambio real varíe, sin tocar
  código de nuevo.
- **Repetir en 30-60 días** cuando el historial post-apagón acumule suficientes ventanas
  para las fuentes 168h/720h/2160h — re-correr `scripts/backtest_adaptive_cadence.py` es
  la acción de seguimiento declarada, no una promesa vaga.

**Incidente durante la construcción de tests (declarado, no ocultado)**: la primera versión
de `test_cadence_estimator_live.py` usó una conexión con commit directo (no transacción
abortada) para sembrar `entity`/`vehicle`/`vehicle_event` sintéticos. `vehicle_event` tiene
un guard append-only real (`migrations/0035_append_only_row_guards.sql`,
`cardeep_vehicle_event_guard()`, `BEFORE DELETE` que lanza excepción) — el intento de
limpieza posterior falló: 3 filas de `vehicle_event` sintéticas (`entity_ulid`
`0F4CADENC3TESTENT7Y0000000`, `vehicle_ulid` `0F4CADENC3TESTVEH7C3000000`) quedaron
PERMANENTES en producción (no se puede ni se debe forzar el guard). Diagnóstico de impacto
real: `v_province_seal` las excluye (`province_code IS NULL`) — cero efecto en el sello de
cobertura; `vehicles_unique_available` las excluye (nunca entraron en
`v_canonical_vehicle`) — cero efecto; SÍ contaban en `dealers` (vía `v_dealer_resolved` +
`servable_vehicle`) — corregido sin borrar nada: `UPDATE vehicle SET status='gone'`
(verificado: el conteo de `dealers` volvió a 19.509, el valor de antes del incidente). El
conteo bruto de `events` en `product_stats` queda permanentemente +3 sobre el real
(3.749.360→3.749.363 en el siguiente refresh, ~0,00008%) — no se puede corregir sin violar
el propio guard de inmutabilidad que hace confiable la tabla; documentado aquí en vez de
disfrazado. El test se reescribió con transacción abortada (patrón ya usado por
`test_resilience_loop.py`/`test_autorepair_loop.py`) y no volverá a ocurrir.

**F5 — Superficie de estado: `/engine/status` + Sala de máquinas + sellos de frescura dealer**
Endpoint nuevo (§5.4) + sección operador (§6b) + sellos de frescura/cobertura en las
páginas dealer existentes (§6a). Cada elemento traza a su fila de §4 — revisión de la
tabla como checklist de aceptación.
✔ Verificación: cero constantes hardcodeadas (grep en CI del patrón mock, mismo criterio
que la carta 01); test E2E con motor parado a propósito → el frontend DEBE mostrar
`PARADO`/fechas reales viejas (el estado honesto es el caso de test principal, no el caso
feliz); protocolo §7 aplicado a cada dato con sus 2 vías nombradas en el PR.

**F6 — Ledger de uptime + track record público del motor**
Tabla `engine_heartbeat_log` (§5.1, INSERT-only + purga por rango, doctrina MVCC) escrita
por el heartbeat; agregado de uptime 30/90 días en `/engine/status`; badge en §6b.
✔ Verificación: el uptime calculado desde el ledger coincide con el log del supervisor
(vía B externa) en un periodo de prueba con una caída provocada; sin la caída provocada
reflejada correctamente en ambas vías, no se cierra.

**F7 — Governor multi-proceso (Redis GCRA) — gate del horizonte EU**
Implementar el upgrade hook ya documentado en governor.py:24-28 (API pública `acquire`/
`slot`/`wrap_fetch_text` invariante). GATED: solo se ejecuta cuando exista necesidad real
de >1 proceso cosechando (España saturada o arranque EU) — antes es YAGNI y la doctrina
de gasto lo veta.
✔ Verificación: test de contención con 2+ procesos contra un host sintético midiendo que
la tasa AGREGADA nunca supera el bucket (la cicatriz AS24 como test); suite del governor
single-process sin regresión; revisión adversarial del script Lua/GCRA.

Regla transversal: ninguna fase abre hasta cerrar la anterior con su evidencia; el estado
de cada fase se persiste en `plans/cardeep-omni/` (enmienda a esta carta o PROGRESO
adjunto), nunca solo en contexto volátil.

---

## Resumen

El motor de Cardeep existe, funcionó a escala real (490k eventos/día) y lleva ~18 días
muerto por la ausencia del primitivo operativo más básico: supervisión de proceso — y su
propio watchdog murió con él, así que nadie lo vio. La ventaja estructural real del
proyecto (delta append-only + VAM + dedup de unidad física) está aguas abajo de un motor
que hoy está por detrás del estándar de la industria en auto-recuperación (Hystrix 2011),
frescura adaptativa (Cho & G-M 2003) y distribución (StormCrawler), y en cero de track
record operativo. Este pilar se cierra en 8 fases: revivir supervisado (F0), hacer el
apagón invisible imposible (F1), drenar el replay y los breakers (F2), curarse solo (F3),
aprender su cadencia (F4), mostrar su estado con honestidad verificada por 2 vías al
dealer y al owner (F5-F6), y solo entonces escalar horizontalmente hacia la UE (F7).

**Estado 2026-07-18**: F0-F4 cerradas. F3: el half-open que existía en código pero era
inalcanzable desde el scheduler real ahora está cableado, con jitter de backoff añadido y
una corrección real de concurrencia en `is_open()` — el primer intento de despliegue
reveló un bug real (doble-reclamo del cupo half-open entre el scheduler y el propio
conector, que dejaba las 7 fuentes probadas atascadas en `half_open` PERMANENTE), cazado
con SQL directo, corregido y re-verificado en vivo con un segundo tick limpio: las 7
fuentes se reintentaron solas, ninguna quedó atascada, cada una resolvió correctamente
(6 fallos reales por causas ajenas al breaker — dependencias no instaladas, un SSL
expirado, un 400 externo —, con backoff correctamente más profundo, cero exclusión
permanente). El motor aprende su cadencia donde el dato ya lo permite (F4: 7/56 fuentes en
modo adaptativo, mejora medida hoy = 0% porque esas 7 ya
estaban óptimas — el hueco honesto es que el apagón de 18 días aún no deja acumular
muestra en las fuentes lentas que sí tienen margen). Quedan F5-F7: superficie de estado
visible, ledger de uptime, y el governor distribuido gateado al horizonte EU.
