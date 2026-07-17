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

## BLOQUE 1 — EN CURSO (lanzado 2026-07-17, 4 frentes en paralelo, task wkzzck2q4)

1. 01-market-intelligence F0-F5 (market_stat, M1-M10, market.py, DGT, price-position)
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

## Próximos bloques (no empezar sin cerrar el anterior — ver 00-MASTER.md §4)

- BLOQUE 2: 03-garage-fleet + 04-arbitrage + 05-multiposting (frente A), tras AUTH-0 y 01.
- BLOQUE 3: 06-CRM + 07-marketing + 09 (resto) + 00-F5/F6.
- BLOQUE 4 (último a propósito): 08-forum-community — requiere OK explícito del owner (gate duro
  ya registrado) antes de una sola línea de frontend.

## Reglas operativas vigentes (de 00-MASTER.md §"Reglas operativas")

Ownership de archivo vinculante (tabla §5.1 del master), un solo helper estadístico de cohortes,
un solo esquema de auth (AUTH-0), un solo CRM (dueño 06), regla del primer llegado para demoliciones
compartidas, nav/rutas solo en commits atómicos al cierre de fase, jobs batch registrados en el
scheduler durable de 00 — nunca procesos sueltos.
