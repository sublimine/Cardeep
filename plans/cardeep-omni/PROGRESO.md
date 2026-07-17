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
2. 02-history-reports F0-F2 (cuarentena Check/Dossier, motor lifetime_link, API)
   - **F0 EJECUTADO 2026-07-18** (evidencia completa en `02-history-reports.md` §10 — leer
     ahí, no re-auditar): coverage SQL real medida en vivo (censo NO congelado — motor de
     Bloque 0 ya escribe, `last_seen` máx = 2026-07-17; `photo_hash`=0/2.670.827 confirmado;
     `vin_ref` contaminado — 94,4% no-nulo pero solo 25.777 filas de patrón-VIN-válido, y ese
     25.777 proviene EXCLUSIVAMENTE de 13 fuentes OEM-CPO, cero de wallapop/milanuncios/
     coches.net/AS24/autocasion — causa raíz: `pipeline/sources/autoscout24.py:208` puebla
     `vin_ref` con el listing-id de AS24, no un VIN; corrige y refina la cifra heredada de
     C-9/04, 17.730→25.777, discrepancia declarada no reconciliada con 04). Universo de pares
     candidato GONE→NEW cross-dealer en ventana 0-12m: 344 vehículos/434 pares. Cuarentena
     Check/Dossier ejecutada: `useCheck.ts`/`useDossier.ts`/`DossierReport.tsx` borrados, ruta
     `/check` retirada de `App.tsx`/`Shell.tsx`, proxy huérfano de `vite.config.ts` limpiado.
     **Corrección de alcance**: `web/src/api/client.ts` NO se borra (5 consumidores fuera de
     02: `AuthContext.tsx`=AUTH-0, `useApi/useDeals/useInbox/useKanban.ts`=06 — borrarlo
     rompía su build, colisión directa con el mandato de cero-colisión de Bloque 1). Build web
     verde (`tsc --noEmit && vite build`), greps `8506`/`useDossier`→0. Commit atómico
     pendiente de este cierre.
3. AUTH-0 (fusión 03-F1+05-F3+06-F1-tenancy+08-F1 en un esquema único, security review obligatoria)
4. 00-F3/F4 (circuit breaker half-open, cadencia adaptativa por fuente)

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
