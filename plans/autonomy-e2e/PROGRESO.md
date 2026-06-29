# Autonomy E2E — PROGRESO (estado vivo)

## Resumen
Cableado integral para autonomía operacional E2E. Plan en `00-PLAN.md` (5 puntos / 14 subpuntos).
Cada subpunto = proyecto élite: código + test RED→GREEN + verificado vs PG + sin regresiones + pusheado.
Infra viva: `:5433` prod (HEAD 0072), `:5434` dry-run (`cardeep-pg-r13`). Push vía token gh inline
(`x-access-token:$(gh auth token)` — el credential helper cuelga tras 401; causa raíz documentada).

## Bitácora
- [x] **0 · PLAN + PROGRESO** — roadmap institucional verificado contra código (run_campaign / gates / supervisor / compose). Pusheado.
- [x] **1.1 · `health_rollup` → SUPERVISA de `run_campaign`** — el loop usaba `_supervise_proof` (proof global); ahora `health_rollup(conn,cc)` → `CountryHealth` (violations por-tenant + servable + seal + sources) reportado en checkpoints; `contaminated` preserva el fail-closed; huérfano eliminado. `test_supervisa_reports_full_health_rollup` + 14 loop E2E verdes vs :5434 limpio. **Pusheado.**
- [x] **1.2 · persistencia consultable de gates PENDIENTE-OWNER** — `state.mark_pending_gates` + `state.pending_owner_gates` (estado en `country_campaign.detail['pending_owner_gates']`, desacoplado de gates.py vía tuplas); `run_campaign` las persiste al parquear (dry-run y país-real). `test_pending_gates_persisted_and_queryable` (persiste→consulta→limpia) + 38 state/loop verdes vs :5434. **Pusheado.**
- [x] **1.3 · ES registrada `SEALED` en `country_campaign`** — `state.register_sealed_incumbent` (backfill directo None→SEALED, idempotente, ES byte-identical; un incumbente no camina el loop). `test_incumbent_backfilled_directly_in_sealed` (25 state verdes vs :5434) + **aplicado a :5433: ES None→SEALED** (additive, `country_campaign=[(ES,SEALED)]`). **Pusheado.** ⇒ **PUNTO 1 (cerebro) COMPLETO.**
- [x] **2.1 · `scheduler` due-sources → harvest** — gana el código: YA construido (`heartbeat_tick()` ciclo single-producer con circuit-breaker + `main()` entrypoint). Verificado: 21 `test_scheduler_due` verdes vs :5434. No se inventa código redundante.
- [x] **2.2 · `lock_heartbeat` + `scheduler_lease`** — YA construido (`lock_heartbeat.py`: acquire/renew sobre `scheduler_lease`, single-producer). Verificado dentro de los 104 tests del latido (heartbeat/lease/lock) verdes vs :5434.
- [x] **2.3 · `silence_watchdog` → gestion_item** — YA construido (`silence_watchdog.py`: SILENCE_MULTIPLIER → fuentes silenciosas). Verificado dentro de los 104 tests (silence/watchdog) verdes vs :5434.
  ⇒ **PUNTO 2 (latido) VERIFICADO** — el ciclo de cosecha existe y pasa 125 tests; lo que falta para "correr solo" es el DAEMON que invoca `heartbeat_tick` en bucle (Punto 3).
- [ ] 3.1 · compose service `api`
- [ ] 3.2 · compose service `autopilot` (daemon persistente)
- [ ] 3.3 · restart/healthcheck + `compose up` E2E en clon
- [ ] 4.1 · Ollama local + modelo (LLM matrix, €0)
- [ ] 4.2 · free-proxies pool vivo
- [ ] 4.3 · seed `source_health` ES (qué cosechar)
- [ ] 5.1 · dossier gates PENDIENTE-OWNER + comandos de desbloqueo
- [ ] 5.2 · runbook arranque/observación/rollback (un comando)

## Decisiones / hallazgos
- (0) `run_campaign` es el loop de ONBOARDING-país (dry-run, casi completo); el loop de COSECHA
  continua (Punto 2) es el que mantiene un país vivo — ambos hacen falta para "correr solo E2E".
