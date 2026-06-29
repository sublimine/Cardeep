# Autonomy E2E — Cableado integral para que Cardeep corra solo, end-to-end

> GOAL (owner, 2026-06-29): vía más robusta y ambiciosa; cada punto dividido en subpuntos; cada
> subpunto tratado como proyecto institucional de élite; **verificado y probado; luego pusheado.**
> Doctrina heredada del road-to-13: TDD/RED→GREEN, €0, mutaciones de serving SOLO dry-run(:5434)→
> golden→prod-con-backup, gates owner PARQUEAN (no detienen), antialucinación (gana el código).

## Principio de aceptación (aplica a TODO subpunto)
Un subpunto está CERRADO solo si: (a) código completo sin huecos · (b) test que lo prueba RED→GREEN ·
(c) verificado contra PG real donde aplique (clon :5434; prod :5433 solo con backup+owner) ·
(d) sin regresiones (suite verde) · (e) **pusheado a `main`**. Nada se declara hecho sin (a–e).

## Estado base (verificado 2026-06-29)
- `main` única rama; `:5433` HEAD 0072 (13/10: invariantes mecánicos vivos). Solo PG corre.
- `run_campaign` (ops/autopilot.py) = loop onboarding-país casi completo (REGISTERED→SEALED, dry-run),
  con `_supervise_proof` cableado pero **`health_rollup` (supervisor full) NO cableado** (lo dice el código).
- `gates.py` puro; **persistencia PENDIENTE-OWNER = "later piece"** (sin construir).
- Scheduler/heartbeat/silence-watchdog: existen como módulos; cableado al daemon = por verificar.
- `docker-compose` solo define `cardeep-pg`. **No hay daemon de arranque.** API/Ollama caídos.
- `country_campaign` vacío (ES no registrada).

---

## PUNTO 1 — EL CEREBRO: ensamblar el loop de campaña
- **1.1** Cablear `supervisor.health_rollup` como paso SUPERVISA completo de `run_campaign` (hoy solo proof). Test DB-backed RED→GREEN vs :5434.
- **1.2** Persistir el veredicto de gates (PENDIENTE-OWNER) — la "later piece": tabla/escritura desde el orchestrator + lectura para resume. Test.
- **1.3** Registrar ES en `country_campaign` como incumbente `SEALED` (idempotente, ES byte-identical). Test + aplicar a :5434, luego :5433 (backup).

## PUNTO 2 — EL LATIDO: loop de cosecha continua
- **2.1** Reconocer + cablear `ops/scheduler.py` (due-sources → harvest) como ciclo invocable. Test.
- **2.2** `lock_heartbeat` + `scheduler_lease` (single-producer observable, anti-doble-ejecución). Test.
- **2.3** `silence_watchdog` (fuentes silenciosas → gestion_item). Test.

## PUNTO 3 — EL CUERPO: daemon que lo mantiene vivo
- **3.1** Servicio compose `api` (services/api/main.py) con healthcheck.
- **3.2** Servicio compose `autopilot` (loop persistente: scheduler tick + supervisa + lease/heartbeat).
- **3.3** Restart policies + healthchecks + arranque ordenado (depends_on pg). Verificar `compose up` E2E en clon.

## PUNTO 4 — LOS SENTIDOS: dependencias por vías €0
- **4.1** Ollama local + modelo(s) de la LLM-ROUTING-MATRIX (instalar, smoke, fallback si ausente).
- **4.2** Egress/proxies gratuitos (`engine/free_proxies`) — verificar pool vivo.
- **4.3** Seed/activar `source_health` (fuentes ES) para que el scheduler tenga qué cosechar.

## PUNTO 5 — LA FRONTERA HONESTA: gates a firma owner
- **5.1** Dossier de activación: qué queda PENDIENTE-OWNER (legal/ToS por país, harvest-prod, rutas €>0) y el comando exacto para desbloquear cada uno.
- **5.2** Runbook: arrancar/parar/observar el sistema autónomo (un comando), con rollback.

---

## Orden de ejecución
1 → 2 → 3 (cerebro→latido→cuerpo: cada capa habilita la siguiente) · 4 en paralelo donde el contexto
lo permita · 5 al cierre. Estado vivo en `PROGRESO.md`; cada subpunto commit atómico a `main`.
