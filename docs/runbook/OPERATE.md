# OPERATE — monitorizar, verificar y remediar (el día a día)

> El runbook **operativo**: cómo se vigila, se verifica y se repara CARDEEP una vez está corriendo.
> [DEPLOY.md](DEPLOY.md) levanta el sistema; [RUNBOOK.md](../../RUNBOOK.md) valida cada fuente;
> [06-RESILIENCE-OPS](../architecture/06-RESILIENCE-OPS.md) explica el *diseño* (doctrina, breakers,
> auto-repair ladder). Esto es el *cómo* procedimental. **Cada query aquí está verificada contra la DB
> viva** — no se documenta nada asumido.
>
> Acceso DB (todo lo de abajo lo usa):
> ```bash
> PSQL='docker exec -e PGPASSWORD=cardeep_dev_only cardeep-pg psql -U cardeep -d cardeep -c'
> ```

---

## 0. Salud del MOTOR (scheduler) — comprobar esto ANTES que nada

> El 2026-06-29 el motor murió y estuvo 18 días parado sin que NADA lo detectara — su propio
> `silence_watchdog` es un job DEL scheduler y murió con él. Todo lo demás en este runbook mide
> síntomas río abajo de un motor vivo; si el motor está muerto, ninguna otra sección importa.
> Ver `plans/cardeep-omni/00-marketplace-engine.md` (F0/F1) y
> `plans/cardeep-omni/EJECUCION_00_F0-F2_2026-07-17.md` para el incidente completo.

```bash
# Vía A: el propio latido (bumped cada 2 min por el proceso vivo)
$PSQL "SELECT holder, pid, last_heartbeat, now()-last_heartbeat AS age FROM scheduler_lease;"
# Vía B, independiente (escrita por APScheduler, no por lock_heartbeat.py): ¿avanza entre dos
# lecturas separadas >=15 min?
$PSQL "SELECT id, to_timestamp(next_run_time) FROM apscheduler_jobs ORDER BY next_run_time;"
# El contenedor supervisado en sí
docker compose -f docker-compose.yml ps autopilot
# El watchdog EXTERNO (Windows Task Scheduler, fuera del proceso/contenedor del motor) — su
# propio log, escrito incluso si la DB está caída:
Get-Content state\engine_watchdog.log -Tail 10
Get-ScheduledTaskInfo -TaskName CardeepEngineWatchdog | Select NextRunTime,LastRunTime,LastTaskResult
```

`age` de `scheduler_lease` ≤30 min = LATIENDO; entre 30 min y 24h = DEGRADADO (se investiga);
≥24h o sin fila = PARADO (crítico — exactamente el estado en que estuvo 18 días sin alerta). El
watchdog (`pipeline/ops/engine_watchdog.py`) dispara una alerta `critical` con
`origin='engine:heartbeat'` en cuanto cruza los 30 min — buscarla en la sección 4 de abajo.

## 1. Salud del sistema de un vistazo

```bash
# Fuentes por estado de salud (healthy / degraded / unknown / down)
$PSQL "SELECT status, count(*) FROM source_health GROUP BY status ORDER BY 2 DESC;"
# Breakers no cerrados (open = fuente apagada en cooldown)
$PSQL "SELECT state, count(*) FROM source_breaker GROUP BY state;"
# Alertas abiertas (sin resolver), con cuántas son severidad error
$PSQL "SELECT count(*) AS open, count(*) FILTER (WHERE severity='error') AS errors
       FROM alert WHERE resolved_at IS NULL;"
# Inventario servido
$PSQL "SELECT status, count(*) FROM vehicle GROUP BY status ORDER BY 2 DESC;"
```

Lectura sana de referencia (medida 2026-06-16): salud `healthy` dominante + `degraded` ≤ puñado;
breakers todos `closed`; inventario `available` ≫ `gone`. Un salto de `degraded`/`open` o de alertas
`error` es la señal de que algo se rompió.

## 2. Monitorizar una fuente concreta

```bash
# Salud + cadencia de UNA fuente (columnas reales: last_ok, last_fail, consecutive_fails, status,
# is_tier1, harvest_interval_hours, coverage_floor)
$PSQL "SELECT * FROM source_health WHERE source_key='coches_net_wholesale';"
# Su breaker (state, consecutive_fails, opened_at = PRIMER trip, cooldown_until)
$PSQL "SELECT * FROM source_breaker WHERE source_key='coches_net_wholesale';"
# Su último veredicto de cobertura B9 (captured vs declared)
$PSQL "SELECT coverage_pct, verdict, declared_total, captured_db, probed_at
       FROM source_coverage WHERE source_key='coches_net_wholesale';"
```

- `status='healthy'` + `consecutive_fails=0` + breaker `closed` = la fuente late bien.
- `coverage.verdict='TRUSTWORTHY'` y `coverage_pct≥coverage_floor` = la última cosecha fue completa
  (sólo entonces se activan las **bajas/GONE**: `reconcile_gone` rehúsa retirar stock sobre una cosecha
  parcial — "mejor un hueco que una mentira").

## 3. Verificar el delta (altas/bajas/Δprecio/Δfoto)

```bash
# Eventos por tipo — el latido del delta. NEW=alta, GONE=baja, PRICE/KM/PHOTO_CHANGE=cambios.
$PSQL "SELECT event_type, count(*) FROM vehicle_event GROUP BY event_type ORDER BY 2 DESC;"
# Eventos de las últimas 24h (columna de tiempo real: observed_at, NO created_at)
$PSQL "SELECT event_type, count(*) FROM vehicle_event
       WHERE observed_at >= now()-interval '24 hours' GROUP BY event_type ORDER BY 2 DESC;"
# El historial completo de un coche (su línea de vida)
$PSQL "SELECT observed_at, event_type, old_value, new_value FROM vehicle_event
       WHERE vehicle_ulid='<ulid>' ORDER BY observed_at;"
```

Si NEW/GONE/PRICE_CHANGE no se mueven tras una cosecha de una fuente activa, el delta no está
aterrizando — revisar §2 (salud) y §4 (alertas) de esa fuente.

## 4. Leer y diagnosticar alertas (el origen EXACTO)

```bash
# Alertas abiertas, lo más severo primero. origin = build_origin(source, phase, cdp) = 'fuente:fase:slug'
$PSQL "SELECT severity, origin, message, created_at FROM alert
       WHERE resolved_at IS NULL ORDER BY severity, created_at DESC LIMIT 40;"
```

- `origin` dice **qué exactamente** se rompió (`as24:scrape:<slug>`, `coches_net:gone_guard:...`).
  Nunca "algo falló": la fase y la entidad están en el origin (06 §3.1).
- Dedup: una fuente que estrangula 138 dealers = **UNA** fila de alerta actualizada, no 138 (06 §3.4).
- Severidad: `error` exige acción; `warning` es degradación observada.

## 5. Diagnosticar un breaker disparado

```bash
# Breakers OPEN (la fuente está pausada hasta cooldown_until)
$PSQL "SELECT source_key, consecutive_fails, opened_at, cooldown_until
       FROM source_breaker WHERE state='open' ORDER BY opened_at;"
```

- `opened_at` = cuándo se abrió por PRIMERA vez (se preserva entre fallos sucesivos — fix M2 06-16),
  así que `now()-opened_at` = cuánto lleva caído de verdad.
- El cooldown crece exponencial con la profundidad del fallo (cap 24h). El scheduler **salta** las
  fuentes con breaker `open` hasta `cooldown_until` (06 §5.3) — no se quema una fuente ya caída.

## 6. Remediar

1. **Reset automático del breaker** — una cosecha OK (`record_run(ok=True)`) cierra el breaker y pone
   `consecutive_fails=0`. No hay reset manual: se arregla la causa y el siguiente run sano lo cierra.
2. **Escalera de auto-reparación** (06 §6, mecanizada): rung 0 retry con jitter → rung 1 re-fingerprint/
   subir tier → rung 2 re-derivar receta (drift) → rung 3 park + escalar (decisión humana → `gestion_item`).
3. **Forzar un run y ver el origen** (dry, no muta):
   ```bash
   python -m pipeline.ops.scheduler --dry-run       # qué fuentes están DUE ahora
   python -m pipeline.ops.scheduler --check-silence  # fuentes calladas > 2× su intervalo (read-only)
   ```
4. **Evictar un dealer muerto por capacidad** (SIEMPRE dry-run primero; las 3 puertas se re-chequean):
   ```bash
   python -m pipeline.evict --cdp CDP-ES-XX-XXXXXXXX            # DEFAULT dry-run: imprime el plan
   python -m pipeline.evict --cdp CDP-ES-XX-XXXXXXXX --apply    # destructivo: tombstone + libera raw
   ```
   La eviction tombstonea (`status='gone'`, NO DELETE — preserva el historial inmutable) y borra los
   archivos crudos SÓLO tras el commit (fix 06-16). Auditoría en `capacity_ledger` + `audit_eviction`.

## 7. Capacidad / disco

```bash
# Histórico de evictions (qué se liberó y cuándo)
$PSQL "SELECT cdp_code, vehicles_deleted, raw_bytes_freed, evicted_at
       FROM capacity_ledger ORDER BY evicted_at DESC LIMIT 20;"
```

La eviction de archivos crudos sólo se dispara por encima de `DISK_EVICT_THRESHOLD_PCT`; el activo
permanente es la **receta** (versionada en `countries/ES/recipes/`), no el crudo (efímero).

---

## Mapa rápido «síntoma → dónde mirar»

| Síntoma | Mirar | Acción |
|---|---|---|
| Alertas `error` subiendo | §4 (`alert` por origin) | leer el origin exacto → §6 |
| Una fuente `degraded`/`down` | §2 (su `source_health`) | §5 breaker → §6 escalera |
| Breaker `open` mucho tiempo | §5 (`opened_at`) | arreglar causa; un run OK lo cierra |
| Delta sin moverse | §3 (`vehicle_event` 24h) | §2 salud de la fuente que debía aterrizar |
| Cobertura `REFUTED` | §2 (`source_coverage`) | cosecha incompleta → NO hay bajas hasta recosechar |
| Disco lleno | §7 (`capacity_ledger`) | `evict --cdp ... --apply` sobre dealers muertos |
