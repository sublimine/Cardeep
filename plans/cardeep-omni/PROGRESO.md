# cardeep-omni — PROGRESO

> Tracker del programa completo (10 pilares de producto más allá del marketplace/censo).
> Mandato original del owner: 2026-07-16/17 (ver /loop transcript). Master de referencia: `00-MASTER.md`.

## FASE 1 — Decomposición + investigación adversarial + arquitectura — CERRADO 2026-07-17

- 10 cartas de pilar escritas y verificadas (`00-marketplace-engine.md` .. `09-trading-terminal.md`).
- Síntesis maestra (`00-MASTER.md`): 13 contradicciones cross-pilar resueltas, mapa de dependencias,
  orden de construcción en 5 bloques con justificación evidenciada.
- Workflow: 31/31 agentes completos tras 2 incidentes reales gestionados (fallos de API transitorios
  a las 19:10; límite de sesión de la plataforma agotado dos veces, resets 2:10am y 7:10am
  Europe/Berlin — ninguno de los dos era un bug del script, documentado en memoria del operador).
- Corrección de enrutado de modelos aplicada a mitad de fase: Fable 5 solo para razonamiento/
  arquitectura de alto nivel (las 10 síntesis + el master); recon e investigación siempre en Sonnet.
  Regla para TODO trabajo futuro del programa: Fable = excepción puntual, Sonnet = default.

## FASE 2 — BLOQUE 0 (cimientos) — EN CURSO

Orden fijado por `00-MASTER.md` §4, "serie, corto":
1. **00-F0..F2** — revivir motor de scraping supervisado (parado ~18 días) + watchdog externo +
   replay/triage de breakers. Gate absoluto del programa.
   **EJECUTADO 2026-07-17** (ver `EJECUCION_00_F0-F2_2026-07-17.md` para evidencia completa,
   comandos y timestamps reales — no re-auditar, leer ese log):
   - **F0**: motor revivido bajo `docker compose` (`autopilot`, `restart: unless-stopped`);
     imagen reconstruida desde main (borra drift de 5 commits/17 días); **regresión real
     encontrada y corregida en el propio rebuild** — `numpy` faltaba en `requirements.txt`
     (solo estaba en `-dev`), crasheaba 11/56 conectores (`pipeline/geocode.py`). Heartbeat +
     `apscheduler_jobs` descongelados y verificados por las 2 vías del protocolo §7. Hueco
     declarado: supervivencia real de 24h no verificable dentro de una sesión (mecanismo sí
     verificado: independencia de terminal, `restart: unless-stopped`).
   - **F1**: `pipeline/ops/engine_watchdog.py` (nuevo, 17 tests verdes) + tarea de Windows
     `CardeepEngineWatchdog` (cada 5 min, fuera del proceso/contenedor del motor), alerta
     `critical` (`origin=engine:heartbeat`) a los 30 min de latido parado, log externo
     `state/engine_watchdog.log` (funciona con la DB caída). Test destructivo real pendiente de
     cierre — ver bloque final de `EJECUCION_00_F0-F2_2026-07-17.md`.
   - **F2**: 5/6 breakers revividos con evidencia real reproducida en vivo (2 de ellos —
     `wallapop_wholesale` con un bug de código real corregido: `DELETE` prohibido por el guard
     append-only de `migrations/0035`, cambiado a `status='gone'`/`'closed'`; `nissan_...` con un
     bug de mensaje declarado, no corregido). 1/6 (`group_vo_chains_carplus`) sigue abierta con
     causa raíz documentada (sitio migrado a Next.js RSC, el parser JSON-LD ya no encuentra
     datos — requiere caza de receta nueva). Replay de arranque en frío NO completado (hueco
     declarado: 36+ fuentes en serie exceden una sesión) pero SÍ arrancado y con delta medido
     (`v_province_seal` venta 79,6655%→79,8151% durante la ventana observada — la prueba de vida
     exigida por el criterio). `state/validation_matrix.json` NO refrescado (hueco declarado:
     hacerlo en vivo violaría la doctrina single-producer mientras el motor ya cosecha).
2. **Barrido documental único** — corregir `docs/frontend/00-PLATFORM-BLUEPRINT-E2E.md` §3.5/3.10/3.11
   + cifra de migraciones en `05-multiposting.md` (C-13), aplicando las decisiones de ownership ya
   tomadas por el master (C-2, C-4, C-5, C-7). **EJECUTADO 2026-07-17, commit `3956e4a`.**
3. **09-Fase0** — demoler `Market.tsx`+`terminal/intelligence.ts` (incluye el artefacto `carNews()`
   que fabrica titulares falsos atribuidos a marcas reales), rescatar `indicators.ts`+tests+
   `MarketChart.tsx`+`drawings.tsx` en cuarentena. Desbloquea la demolición de 01-F6.
   **EJECUTADO 2026-07-17, commit `672259f`**: build web verde, 0 imports rotos a los archivos
   borrados, `/terminal` confirmado fuera del nav (ya lo estaba). Motor de 53 indicadores +
   `MarketChart.tsx`+`drawings.tsx` en cuarentena, no borrados.

## BLOQUE 0 — CERRADO 2026-07-17 (3/3, 0 errores)

Commits en `main`/`origin`: `5635811` (motor), `3956e4a` (docs), `672259f` (demolición).
Huecos honestos que quedan abiertos y declarados (no bloquean el resto del programa):
supervivencia de 24h del motor sin verificar dentro de sesión (mecanismo sí verificado),
1/6 breaker (`group_vo_chains_carplus`) sigue caído por migración del sitio a Next.js RSC
(requiere receta nueva), replay de arranque en frío no completado (36+ fuentes exceden una
sesión, sigue drenando solo), `validation_matrix.json` no refrescado a propósito (doctrina
single-producer).

## BLOQUE 1 — CERRADO 2026-07-18 (4/4, 0 errores, task wkzzck2q4)

1. 01-market-intelligence F0-F5 (market_stat, M1-M10, market.py, DGT, price-position) —
   **✅ CERRADAS 2026-07-18** (evidencia completa en
   `01-market-intelligence-f{0,1,2,3,4,5}.md` — leer ahí, no re-auditar). Commits en `main`:
   `d10365f` (F0), `bdca888` (F1), `55bef8e` (F2), `529b102` (F3), `b4af8d2` (F4), `9d2afbc` (F5).
   - **F0**: verdad de volumen por SQL directo (`scripts/f0_market_volume_truth.py`, re-ejecutable):
     `vehicle` 2.670.827 (2.124.671 disponibles), `vehicle_event` 3.749.360 (verificado 2ª vía contra
     `product_stats`), span real **35 días** (gate disparado: ventanas de M3/M4/M7 reducidas en F2, nunca
     fingiendo 90/45/30d), 1 run `vam_verified` (M1-M10 usan `v_canonical_vehicle` estricto).
   - **F1**: migración `0074_market_stat.sql` (renumerada de 0073 por colisión real con
     `0073_auth.sql` del frente AUTH-0 de este mismo bloque) + `pipeline/market/compute_stats.py`
     (M1) + helper compartido `pipeline/market/cohort.py` (percentiles/cohortes, factorizado UNA vez
     per 00-MASTER.md C-1/C-12 para que 03/04/06/07/09 lo importen, 16 tests sin DB). Cross-check
     SQL-vs-Python sobre 5 segmentos reales: **divergencia 0,0%**. Run de producción real: 117.652
     filas, `published=FALSE` (criterio F1).
   - **F2**: M3/M4/M5/M7/M9/M10 + gate ±3% (`pipeline/market/publish_gate.py`). **Bug real de
     producción encontrado y corregido dentro de la propia fase**: la primera corrida escribió 0
     filas de M7 — causa raíz, el `canon` estricto (copiado de M1) excluye 408.155 vehículos
     (15,3% de la flota) nunca tocados por el resolver `vehicle_cluster` (último `vam_verified`
     2026-06-22); la ventana "reciente" de M7 cae entera después de esa fecha. Corregido con un
     `_COALESCE_CANON_CTE` (mismo patrón ya probado en `entities.py:74` para la clase idéntica de
     bug). Corrida defectuosa despublicada (no borrada, nota de auditoría); corrida corregida
     publicada: 502.749 filas (M7 pasó de 0 a 4.386). 33/33 tests tras el fix.
   - **F3**: `services/api/routers/market.py` (M1/M3/M4/M5/M7/M9/M10) + `web/src/pages/Api.tsx`
     reescrito línea a línea (catálogo de 6 endpoints ficticios `/v1/*` reemplazado por 6 endpoints
     reales, verificados contra los 26 endpoints reales del proyecto por grep). M2/M8 deliberadamente
     ausentes (alcance F5/F4); M6 declarado como hueco de numeración heredado de la propia carta
     (nunca asignado a F0-F5 ni F7 salvo su mitad longitudinal). 11/11 tests de contrato + **107/107
     tests de API preexistentes sin regresión**.
   - **F4**: ingesta real DGT (`migrations/0077_dgt_transfer.sql`+`0078_dgt_corroboration.sql`,
     renumeradas de 0074/0075 por colisión con frentes paralelos) + `pipeline/market/ingest_dgt.py`
     + `corroborate.py` (M8). Esquema DGT confirmado byte a byte contra el documento oficial (69
     campos, suma exacta 714 bytes). **Dos hallazgos reales no anticipados por la carta, corregidos
     en la raíz antes de comprometer datos**: (1) códigos de provincia DGT son letras de matrícula
     histórica, no los códigos INE de Cardeep — mapeo `pipeline/market/dgt_provinces.py` construido
     cruzando el Anexo I oficial + `geo_province` en vivo, 52/52 provincias mapeadas sin huecos; (2)
     el fichero de transferencias cubre TODO tipo de vehículo, no solo turismos — `cod_tipo` añadido
     al esquema, filtrado a `'40'` antes de cualquier cómputo de M8. Además: un bug de sintaxis real
     en `scripts/migrate.py` (comentario `--` terminado en `;` corta el CREATE TABLE) evitado en la
     propia migración, y un error de FK real (`geo_province`'s PK es compuesta
     `(country_code, code)`, no la forma de una sola columna que documentaba `0002_entities.sql`)
     corregido tras verificar `pg_constraint` en vivo. Ingesta real junio 2026: 396.069 filas, doble
     descarga con hash SHA256 idéntico. M8 real: 89.144 cohortes, ratios de ejemplo (Madrid) 25%-66%,
     reconciliado contra GANVAM con desviación explicada (censo DGT ≠ ventas mediadas por negocio).
     27 tests nuevos, todos verdes.
   - **F5**: `GET /market/price-position/{vehicle_ulid}` (M2), calculado en vivo. Distribución real
     analizada sobre 1.183.432 vehículos (p25=0,898 p50=1,000 p75=1,127) confirma los cortes
     0,92/1,08 de la carta. `03-garage-fleet`/`07-marketing` (consumidores previstos de este motor)
     verificados por grep: no existen todavía — nada con qué verificar consistencia cross-pilar aún.
     **Bloqueo real declarado, no maquillado**: el gate adversarial formal de modelo caro (Fable
     5/Opus) que la doctrina del operador reserva para recalibrar METODOLOGÍA no fue ejecutable en
     este contexto de sesión (sin herramienta para invocar un modelo distinto como segunda opinión
     literal) — el análisis completo queda listo para que ese gate decida, la validación adversarial
     en sí NO se reclama como hecha. 6/6 tests de contrato + 17/17 de F3/F4 sin regresión.
   - **F6/F7 explícitamente fuera de este mandato** (instrucción literal del Director): no se tocó
     `Inteligencia.tsx`/`Arbitrage.tsx`/`Analitica.tsx`/`Shell.tsx` — quedan para el siguiente bloque.
2. 02-history-reports F0-F2 — **✅ CERRADAS 2026-07-18** (evidencia completa en
   `02-history-reports.md` §10/§11/§12 — leer ahí, no re-auditar). Commits en `main`:
   `36bf903` (F0), `2fcf1f9` (F1), pendiente el de F2 (este cierre).
   - **F0**: coverage SQL real medida en vivo (censo NO congelado — motor de Bloque 0 ya
     escribe, `last_seen` máx = 2026-07-17; `photo_hash`=0/2.670.827 confirmado; `vin_ref`
     contaminado — 94,4% no-nulo pero solo 25.777 filas de patrón-VIN-válido, y ese 25.777
     proviene EXCLUSIVAMENTE de 13 fuentes OEM-CPO, cero de wallapop/milanuncios/coches.net/
     AS24/autocasion — causa raíz: `pipeline/sources/autoscout24.py:208` puebla `vin_ref` con
     el listing-id de AS24, no un VIN; corrige y refina la cifra heredada de C-9/04,
     17.730→25.777, discrepancia declarada no reconciliada con 04). Universo de pares
     candidato GONE→NEW cross-dealer en ventana 0-12m: 344 vehículos/434 pares. Cuarentena
     Check/Dossier ejecutada: `useCheck.ts`/`useDossier.ts`/`DossierReport.tsx` borrados, ruta
     `/check` retirada de `App.tsx`/`Shell.tsx`, proxy huérfano de `vite.config.ts` limpiado.
     **Corrección de alcance**: `web/src/api/client.ts` NO se borra (5 consumidores fuera de
     02: `AuthContext.tsx`=AUTH-0, `useApi/useDeals/useInbox/useKanban.ts`=06 — borrarlo
     rompía su build). Build web verde, greps `8506`/`useDossier`→0.
   - **F1**: `pipeline/identity/link_lifetimes.py` (nuevo) + migración `0075_lifetime_link.sql`
     (`lifetime_link_run`/`lifetime_link`/`v_vehicle_lifetime`, número re-verificado tras
     0073/0074). TDD 43 tests, RED→GREEN. **Hallazgo adversarial real**: la primera corrida
     viva (208 edges) resultó ser 100% churn intra-dominio (mismo portal OEM-CPO reemitiendo
     un listing bajo nueva URL — caso ancla verificado: mismo dealer, mismo UUID de listing,
     solo cambió el formato de la URL de Toyota), NO coches rebotados entre negocios
     independientes. Corregido con un guard duro nuevo (`_platform_domain`, 6 tests) antes de
     considerar la muestra manual de §7. Segunda corrida (con el guard): **0 edges** — resultado
     correcto, no un fallo: con el `vin_ref` de hoy (100% OEM-CPO), no sobrevive ningún caso
     genuino tras excluir el churn. `vam_verified` se deja en `FALSE`, honestamente (nada que
     gatear). Camino a yield real: 04-F6 puebla `photo_hash` — el motor ya soporta esa señal
     end-to-end sin tocar código. Incidente operativo declarado (higiene): un proceso propio
     quedó bloqueado en un pipe (`| tail`) durante una corrida en background; diagnosticado por
     CPU-time plano + `pg_stat_activity` en `idle in transaction`, terminado sin tocar
     conexiones de otros frentes (verificado por texto de query exclusivo del módulo).
   - **F2**: `GET /vehicles/{ulid}/lifetime` en `vehicles.py` (extendido, no duplicado) +
     `services/api/lifetime_aggregates.py` (nuevo, C1-C10, 26 tests sin DB) +
     `tests/test_api_lifetime.py` (6 passed/1 skip honesto — sin cadena verificada hoy) +
     `docs/API_CONTRACT.md` §4.8b. Servidor nativo de `:8090` (llevaba desde el 16 de julio,
     ni siquiera tenía el router de AUTH-0) reiniciado y verificado por curl real — beneficio
     colateral para el resto de frentes. Latencia real medida: p95≈241ms/20 reqs → decisión
     de NO cachear en v1 (la medición no lo exige). 0 regresión: 126 passed/1 skip en la
     suite completa de tests de API tocados (incluye `test_api_gaps`/`test_api_canonical`/
     `test_api_pagination`/`test_api_ratelimit_cache`, no solo los propios).
   - **Autocorrección declarada**: el commit de F1 (`2fcf1f9`) incluyó por error
     `tests/test_lifetime_aggregates.py` sin el módulo que testea
     (`services/api/lifetime_aggregates.py`, escrito para F2 pero no comiteado a tiempo) —
     `main` quedó momentáneamente con un test huérfano tras ese push. Corregido en el commit
     de cierre de F2 (el módulo se comitea junto con el resto de F2). Declarado aquí para que
     quien audite el historial de `main` no lo interprete como un fallo oculto.
3. AUTH-0 (fusión 03-F1+05-F3+06-F1-tenancy+08-F1 en un esquema único, security review obligatoria)
   **EJECUTADO 2026-07-17/18** (registro completo en `AUTH-0.md` — leer ahí, no re-auditar):
   migración `0073_auth.sql` (`app_user`+`dealer_membership`+`user_session`+`user_notification`,
   número re-verificado contra `ls migrations/` al crearla, sin colisión con 0074/0075/0076
   tomados por los otros 3 frentes de este mismo bloque) + router `services/api/routers/auth.py`
   (register/login/me/logout/refresh/claim-dealer) + `services/api/auth_security.py` (argon2id,
   tokens opacos revocables con rotación en refresh, anti-enumeración por timing y por
   respuesta) + `RATE_AUTH` dedicado (10/min) + CORS corregido para las primeras escrituras
   reales de la API (POST + Authorization/X-Tenant-ID). `DEV_BYPASS` desmontado UNA sola vez de
   `AuthContext.tsx` (no tres, como planeaban 03/05/08 por separado); `Register.tsx` recableado
   a un `register()` real (antes llamaba `login()` y nunca registraba nada). Verificado:
   migración aplicada en vivo, 20/20 tests propios verdes con teardown limpio comprobado (0
   filas residuales), 0 regresión en 18 archivos de test que tocan `services.api` (263
   passed/31 skipped en el subconjunto de impacto real), login real de extremo a extremo por
   curl con preflight CORS real, build de frontend verde. Encontrado y corregido en el propio
   proceso: el guard repo-wide `test_served_queries_have_country.py` detectó una query nueva
   (`dealer_membership JOIN entity` sin dimensión de país) — corregida con
   `AND e.country_code = 'ES'` antes de cerrar. Huecos declarados (no bloqueantes): sin job de
   purga de `user_session` expiradas, sin ruta de auto-registro para `role='staff'` (YAGNI hasta
   que exista un consumidor real). Commit atómico pendiente de este cierre.
4. 00-F3/F4 (circuit breaker half-open, cadencia adaptativa por fuente) — **✅ AMBAS
   CERRADAS 2026-07-17/18, F3 con verificación en vivo confirmada por dos ticks reales**
   (registro completo en `00-marketplace-engine.md` §9 F3/F4 — leer ahí, no re-auditar):
   F3 — el mecanismo half-open Hystrix YA existía en `pipeline/ops/health.py`
   (`source_breaker`, 0013) pero `scheduler.py::_due_sources()` nunca lo consultaba
   (excluía por `consecutive_fails` sin dimensión temporal, dejándolo inalcanzable). Cero
   migración nueva: `_breaker_decision` + jitter ±20% en el backoff + corrección de
   `is_open()` (antes admitía más de una sonda concurrente en half-open).
   **Bug real cazado y corregido en vivo**: el primer despliegue tenía `_prepare_launch`
   haciendo su PROPIO CAS del cupo half-open en el scheduler — que chocaba con el CAS que
   cada conector YA hace por su cuenta vía `is_open()`, causando que las 7 sondas
   legítimamente autorizadas se auto-bloquearan y quedaran `half_open` PERMANENTE (peor que
   el bug original). Diagnosticado con SQL directo tras el primer tick (cero filas nuevas en
   `harvest_run`, las 7 estancadas en `half_open`), corregido (`_prepare_launch` ahora
   solo-lectura, la reclamación real vive únicamente en `is_open()`), datos reparados
   (`half_open`→`open`), redesplegado. **Segundo tick real confirmó el fix**: las 7 fuentes
   se reintentaron solas, ninguna se auto-bloqueó, las 7 completaron un intento real y
   resolvieron a `open` con backoff más profundo (6 fallos por causas ajenas al breaker —
   playwright/camoufox/fichero de receta ausentes, SSL expirado, HTTP 400 externo — cero
   quedó en `half_open`). 28 tests nuevos (F3) + 21 tests nuevos (F4) + 3 reescritos, TDD
   RED→GREEN, 0 regresión en 86 tests del subconjunto de impacto. Desplegado en vivo vía
   `docker cp` (NO rebuild — habría
   horneado el trabajo en curso sin commitear de 01/02, ver nota de aislamiento en la
   carta) + `docker restart cardeep-autopilot` (×2, tras el fix). F4 — migración
   `0076_adaptive_cadence.sql`
   (aditiva, `cadence_mode` default `static`); estimador Cho&G-M en
   `pipeline/ops/cadence_estimator.py` (21 tests); backtest real
   (`scripts/backtest_adaptive_cadence.py`) contra 90 días de historia real: de 56 fuentes,
   solo 7 (todas Tier-1/24h) alcanzan `MIN_WINDOWS=5` de confianza — las 7 convergen a
   computed_interval=24h, IDÉNTICO a su cadencia estática (mejora medida = 0,00h/0%,
   hallazgo honesto: el apagón de 18 días truncó el historial de las fuentes 168h/720h/2160h
   por debajo del umbral, hueco declarado, repetir el backtest en 30-60 días). Rollout
   aplicado a las 7 (`scripts/enable_adaptive_cadence.py --apply`). Incidente declarado
   durante el desarrollo de tests: una primera versión de un test escribió 3 filas
   sintéticas reales en `vehicle_event` (append-only, guard `0035`, no se pudieron borrar);
   impacto diagnosticado y neutralizado en las métricas de producto (`dealers` restaurado a
   19.509 vía `vehicle.status='gone'`), residuo permanente de +3 en el conteo bruto de
   `events` (~0,00008%) documentado, no oculto. Commit atómico + push pendiente de este
   cierre (solo archivos propios: `pipeline/ops/{scheduler,health,cadence_estimator}.py`,
   `migrations/0076...`, `scripts/{backtest,enable}_adaptive_cadence.py`, tests nuevos,
   esta carta).

## BLOQUE 2 — CERRADO 2026-07-18 (3/3, 0 errores, task w2k2swd6o)

Prerrequisitos AUTH-0 y 01 confirmados cerrados (Bloque 1). Frentes:
1. 03-garage-fleet F1-F4 — **✅ CERRADAS** (`03-garage-fleet.md` §10). Primera escritura real de
   toda la API (`fleet_ops`/`fleet_ops_event`, router `dealer_ops.py`), auth real dealer↔cdp vía
   AUTH-0, aislamiento entre dealers verificado (403 cruzado probado), comparables consumiendo M1-M10
   de 01. Commits `b9bd4d9 84017db 4b27834 17f378f`.
2. 04-arbitrage F1-F5 + F6 (identidad-captura de fondo, C-9) — **✅ F1-F5 CERRADAS, F6 parcial y
   declarado** (`04-arbitrage.md` §10). Deal-score real (1.582.295 vehículos, doble vía 0,0%
   divergencia), dueño único de `/arbitrage`. **Hallazgo crítico F6**: de 2.520.623 `vin_ref`, solo
   41.510 (1,6%) eran VINs reales — 2.479.113 (98,4%) eran IDs de listado mal etiquetados
   (`autoscout24.py:208`); remediado en vivo (migración `0083`, 0 contaminados restantes). Explica
   directamente por qué 02-history-reports dio 0 edges. Hueco declarado: ~15 conectores más con el
   mismo patrón siguen sin corregir (recontaminarán en el próximo harvest, lista exacta en §10).
   Commits `bfb4aa1 cac2f0c 1bda49f 32f127a`.
3. 05-multiposting F0-F2 (Frente A, solo-lectura) — matriz de publicación.
   **✅ CERRADAS 2026-07-18** (evidencia completa en `05-multiposting.md` — corrección de
   deriva + F0/F1/F2 registrados inline en esa misma carta — leer ahí, no re-auditar).
   - **F0**: censo real de `platform_listing` por plataforma×dealer, 2 vías (SQL directo +
     `GET /platforms/{cdp}/inventory` — 7 plataformas paginadas a completitud, 100% exactas;
     9 muestreadas por tamaño, 43 plataformas totales). **Hallazgo real no anticipado**:
     `platforms.py:49-50` rechaza (HTTP 400) 96.941 aristas reales cuyo `platform_entity_ulid`
     es `oem_vo_portal`/`cadena`/`rent_a_car_vo`/`importador` en vez de `plataforma` — 25
     entidades legítimas (portales OEM de VO, cadenas de compraventa, canales de desflotación)
     que el endpoint existente excluye por un gate de `kind` demasiado estricto. Declarado
     para quien posea `platforms.py`, NO corregido ahí (fuera de alcance F0-F2); el router
     nuevo de este pilar NO replica ese gate. Corrección de deriva: cifra "66 migraciones"
     de §1.1 seguía siendo la correcta (C-13 ya la fijó bien); pero hoy son 72 archivos reales
     — Bloque 1 consumió `0073`-`0078`, chocando por completo con la reserva original de este
     documento (`0073_dealer_account`→`0076_feed_export`), exactamente el escenario que
     `00-MASTER.md` C-6 anticipó. `dealer_account`/`dealer_user` (F3) quedan SUPERSEDIDOS por
     AUTH-0 (ya construido) — F3, cuando se ejecute, consume `dealer_membership`/`tenantId`,
     no crea un segundo esquema (C-3). §4.4 enmendado: el badge "anuncio viejo" reutiliza
     `market_stat` M3 de 01-market-intelligence (ya publicado) en vez de una segunda mediana-
     por-cohorte con banda de km (C-1/C-12) — evita la tercera implementación que el programa
     existe para prevenir. Blueprint §3.10 re-verificado: ya corregido por el barrido
     documental de Bloque 0, sin deriva nueva.
   - **F1**: `services/api/routers/publishing.py` (nuevo, registrado en `main.py`) — 2
     endpoints solo-lectura: `GET /publishing/{cdp}/coverage` (semáforo S4.1) y
     `GET /publishing/{cdp}/matrix` (S4.1-S4.4 fusionados por vehículo×plataforma:
     divergencia de precio, anomalías `sold_still_listed`/`available_removed`, frescura vía
     M3). 23 tests nuevos (8 unitarios de funciones puras + 15 de contrato/DB), 0 regresión
     en 13 archivos de test de impacto (`test_api_gaps/exhaustiveness/pagination/auth/
     canonical/seal/ratelimit_cache`, `test_platform_*`, `test_country_isolation_vin_
     xplatform`, `test_engine_api_proxies`, `test_api_lifetime`). Cross-check real contra
     `/platforms/{cdp}/inventory` en 3 dealers reales (Valdisa/Concesur/Autos Juanjo) — vía
     SQL directa tras descubrir que la vía HTTP ingenua (paginar la plataforma ENTERA
     filtrando por dealer client-side) es inviable a escala (colgó >15 min contra
     coches.net/274k filas antes de matarlo; `pg_stat_activity` confirmó que era una consulta
     real en curso, no un deadlock) — declarado, corregido. Divergencia de precio y hallazgo
     F0.2b (kind no restringido) verificados contra ejemplos reales vivos, no fixtures.
     `sold_still_listed` verificado solo por unidad: 0 instancias reales existen hoy (el
     harvester ya sincroniza `platform_listing.status→'removed'` en el mismo paso que marca
     `vehicle.status='gone'`, 491.245/491.245 coincide exacto) — declarado, no maquillado.
   - **F2**: página `/publicaciones` (`web/src/pages/Publicaciones.tsx`, nueva) + nav
     "OPERACIÓN" (`Shell.tsx`) + ruta (`App.tsx`) + cliente (`cardeep.ts`, sección propia
     append-only). Dealer scope = `useAuthContext().user.tenantId` (misma convención que
     03-garage-fleet F1 ya estableció para `pages/inventory/`, sin cdp hardcodeado). Cabecera
     de cobertura por plataforma + tabla vehículo×portal con estados reales (publicado/precio
     distinto/vendido-sigue-publicado/no publicado), sin un solo `MOCK_*` (grep=0). **C-10
     (regla del primer llegado, Inbox.tsx)**: 06-unified-crm-chat no había aterrizado
     (Bloque 3, no iniciado) — `MOCK_CONVS` (mobile.de/autoscout24, fuera de alcance España)
     retirado con empty-state honesto ("Bandeja aún no conectada"); registrado en el header de
     `06-unified-crm-chat.md` para que 06 no lo redescubra como sorpresa. Build web verde
     (`tsc --noEmit` + `vite build`), 0 regresión de rutas/nav. Frente B (`Publicar en AS24`)
     y Frente C (coches.net/Wallapop/Milanuncios) explícitamente NO tocados — gated F4/F5/F7,
     fuera del mandato de esta ejecución.

## BLOQUE 3 — EN CURSO (lanzado 2026-07-18, 4 frentes en paralelo)

1. 06-unified-crm-chat F1-F6 — CRM completo, dueño de Contacts/Deals/Kanban/Inbox (C-4/C-5/C-10),
   email como primer canal, cruce censo con M2 de 01. Nota: Inbox.tsx ya tiene un empty-state honesto
   dejado por 05 (§4.4 de PROGRESO arriba) — no es una sorpresa, ya registrado en la cabecera de
   `06-unified-crm-chat.md`.
2. 07-marketing F0-F5 — auditoría de anuncio, feeds, copy grounded; consume M2/C2 de 01; F6 integra
   con 05/06.
3. 09-trading-terminal Fases1-6 — agregación diaria + terminal real bajo `/terminal/*` (C-1);
   inferencia de venta consumiendo `lifetime_link` de 02 (C-9) — con el hallazgo de 04-F6 (vin_ref
   remediado, aunque ~15 conectores siguen sin corregir) como contexto de calidad de dato disponible.
4. 00-F5/F6 — superficie de estado (`/engine/status`) + ledger de uptime — **✅ AMBAS CERRADAS
   2026-07-18** (evidencia completa en `00-marketplace-engine.md` §9 F5/F6 — leer ahí, no
   re-auditar). F5: endpoint `/engine/status` (badge §4 + lease + apscheduler jobs + replay
   progress honesto + uptime) + página `Motor.tsx` ("Sala de máquinas", ruta `/motor`, grupo
   de nav propio "MOTOR") + sello de frescura/cobertura dealer (`EngineFreshnessStamp.tsx`,
   integrado en `Dashboard.tsx` con una inserción de 2 líneas para no crecer un archivo ya en
   el límite de tamaño) — cero mock, cero SQL propio donde ya existía endpoint (`/sources`,
   `/alerts`, `/geo/seal`, `/entities/{cdp}/delta` reutilizados tal cual). F6: migración
   `0085_engine_heartbeat_log.sql` (ledger INSERT-only) + `pipeline/ops/lock_heartbeat.py`
   extendido (escritura doble lease+ledger, independiente por fallos) +
   `pipeline/ops/engine_uptime.py` (nuevo, bucketing puro + guardia antialucinación
   `clipped_window` que nunca fabrica historial pre-ledger como caída) + job diario de purga
   por rango (retención 90d). **Prueba destructiva real ejecutada**: ~6 min de caída
   provocada de `cardeep-autopilot` (2026-07-18T02:25:58Z→02:32:03Z), verificada por 3 vías
   independientes que coinciden al segundo (ledger propio 476,19s bruto = 107s slack normal +
   364,07s caída real de Docker + 5s arranque; el watchdog externo de F1 corrobora
   `DB_UNREACHABLE`→`LATIENDO` en la misma ventana). 40 tests nuevos (20
   `test_engine_uptime.py` + 20 `test_engine_status_api.py`, estos últimos contra la DB VIVA)
   + `test_lock_heartbeat.py` extendido (75 tests, 0 regresión) — todos verdes. Desplegado en
   vivo vía `docker cp` (NO rebuild — los otros 3 frentes de este bloque tienen trabajo sin
   commitear en `services/api/cache.py`/`marketing.py`/`crm_*`/`terminal/*`, confirmado por
   `git status` antes de tocar nada) + `docker restart cardeep-autopilot`; API nativa de
   `:8090` reiniciada para servir el endpoint nuevo. Frontend: `tsc --noEmit` + `vite build`
   verdes (3617 módulos) integrando en caliente el trabajo concurrente de 06/07/09. Colisión
   de archivo compartido observada y resuelta sola: `App.tsx` tuvo un estado transitorio
   roto (`Cannot find name 'Chat'`) durante ~1 typecheck mientras 06-F3 completaba su propio
   retiro de `/chat` en dos pasos — se resolvió solo antes de que yo tocara el archivo, cero
   intervención necesaria, declarado aquí para que no se lea como sorpresa. Queda F7 (governor
   Redis), gateado al horizonte EU por la propia carta — YAGNI mientras España quepa en un
   proceso.

## Próximos bloques (no empezar sin cerrar el anterior — ver 00-MASTER.md §4)

- BLOQUE 4 (último a propósito): 08-forum-community — requiere OK explícito del owner (gate duro
  ya registrado) antes de una sola línea de frontend.

## Reglas operativas vigentes (de 00-MASTER.md §"Reglas operativas")

Ownership de archivo vinculante (tabla §5.1 del master), un solo helper estadístico de cohortes,
un solo esquema de auth (AUTH-0), un solo CRM (dueño 06), regla del primer llegado para demoliciones
compartidas, nav/rutas solo en commits atómicos al cierre de fase, jobs batch registrados en el
scheduler durable de 00 — nunca procesos sueltos.
