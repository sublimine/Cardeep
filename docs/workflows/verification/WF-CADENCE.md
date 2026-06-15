# WF-CADENCE — Jobs de Cadencia: Heartbeat, Silencio, δ TTL

## Objetivo

Mantener el pipeline activo y auto-supervisado mediante tres jobs deterministas
€0 que controlan el ritmo de harvest, detectan fuentes silentes y relanza claims
expirados para re-verificación.

---

## Backend de scheduling

APScheduler 3.x con `BlockingScheduler` y `SQLAlchemyJobStore` apuntando a
`cardeep-pg`. Los jobs son persistentes: sobreviven reinicios del proceso.

---

## Job 1 — `heartbeat_tick` (`pipeline/ops/scheduler.py`)

### Propósito

Seleccionar la source más atrasada y disparar su harvest, manteniendo el
pipeline activo sin solapar runs.

### Trigger

APScheduler cron: **cada 15 minutos**.

### Pasos átomo

1. Seleccionar la source con mayor retraso:
   ```sql
   SELECT * FROM source_health
   WHERE now() - last_ok >= harvest_interval_hours * interval '1 hour'
   ORDER BY (now() - last_ok) DESC
   LIMIT 1
   ```
2. Comprobar circuit breaker: `is_open(source)` — si `consecutive_fails >= BREAKER_TRIP_AT`, omitir.
   ```
   BREAKER_TRIP_AT     = 3
   BREAKER_COOLDOWN_SEC = 900  (15 min)
   ```
3. Disparar harvest de esa source (una por tick — nunca paralelo).
4. `record_run(conn, source_key, phase, success, count)` → actualiza
   `harvest_run` y `source_health`.
5. Si falla: `fire_alert(source_key:harvest)`, incrementar
   `consecutive_fails`, evaluar cooldown.

### CLI

```
python -m pipeline.ops.scheduler [--dry-run] [--check-silence]
```

- `--dry-run`: muestra qué source se procesaría, sin ejecutar.
- `--check-silence`: emite alerta si alguna source supera el umbral de
  silencio sin entrar en el tick normal.

### Nota de gasto

La lógica de scheduling y circuit breaker es €0. El scraping real que se
dispara en el tick puede incurrir en gasto de proxies si la source es Tier-1
(anti-bot).

---

## Job 2 — `silence_watchdog` (`pipeline/ops/silence_watchdog.py`)

### Propósito

Detectar fuentes que llevan más tiempo del esperado sin un run exitoso y emitir
alertas antes de que el silencio se convierta en pérdida de cobertura.

### Trigger

APScheduler cron: **cada 1 hora** (fijado en `scheduler.py` como `trigger="interval", hours=1`). También invocable manualmente.

### Pasos átomo

1. `find_silent_sources(conn)` — read puro:
   ```sql
   SELECT * FROM source_health
   WHERE now() - last_ok > harvest_interval_hours * SILENCE_MULTIPLIER * interval '1 hour'
   ```
   `SILENCE_MULTIPLIER = 2`

2. Por cada source silente:
   - `run_silence_watchdog(conn)` invoca `fire_alert()`:
     - `tier1` sources → severidad `'critical'`
     - resto → severidad `'warning'`
   - Origen exacto en `alert`: `source_key:silence`

3. Implementación: `psycopg2` síncrono (no asyncio).

### CLI

```
python -m pipeline.ops.silence_watchdog
```

### Lógica de umbral

`SILENCE_MULTIPLIER = 2` significa que una source se considera silente solo
cuando ha pasado el doble de su intervalo de harvest sin éxito. Esto evita
false alerts durante ventanas normales de downtime temporal.

---

## Job 3 — `inquisition_cadence` / δ TTL (`pipeline/ops/inquisition_schedule.py`)

### Propósito

Relanzar a Inquisition L4 los verdicts de verificación que han expirado su TTL,
cerrando el ciclo de re-verificación continua.

### Trigger

APScheduler cron: **cada 6 horas** (`INQUISITION_CADENCE_HOURS=6` en `scheduler.py`, `trigger="interval", hours=6`). También invocable manualmente.

### Pasos átomo

1. Buscar verdicts expirados:
   ```sql
   SELECT id, subject_type, subject_key, claim, claim_kind, verdict, expires_at, created_at
   FROM verification_verdict
   WHERE expires_at IS NOT NULL
     AND expires_at < now()
     AND superseded_by IS NULL
   ORDER BY expires_at ASC
   -- índice: idx_verdict_expiry (partial index sobre expires_at WHERE IS NOT NULL)
   ```

2. Por cada verdict expirado, construye un `AnomalyResult` con `detector='stale_verdict'` y llama:
   `open_or_refresh(conn, anomaly: AnomalyResult, *, actor='inquisition_cadence') -> int`
   (firma real — no acepta `lane` ni `dedupe_key` como args directos; estos se derivan de `anomaly`).
   El `gestion_item` RESEARCH resultante es recogido por `prosecute_pending()` en la
   siguiente ventana de Inquisition.

3. Bridge a Inquisition: el cycle completo es `inquisition_schedule` →
   `gestion_item RESEARCH` → `prosecute_pending` → nuevo `inquisition_verdict`.

### CLI

```
python -m pipeline.ops.inquisition_schedule
```

---

## Tabla de referencia rápida

| Job | Trigger | Intervalo | CLI |
|-----|---------|-----------|-----|
| `heartbeat_tick` | APScheduler cron | 15 min | `python -m pipeline.ops.scheduler` |
| `silence_watchdog_job` | APScheduler cron | 1 hora | `python -m pipeline.ops.scheduler --check-silence` (check-only) o invocado por el scheduler |
| `inquisition_cadence_job` | APScheduler cron | 6 horas | `python -m pipeline.ops.inquisition_schedule` |

---

## Gates de verificación

| Job | Gate |
|-----|------|
| `heartbeat_tick` | `consecutive_fails >= BREAKER_TRIP_AT=3` (filtrado en `_due_sources()` antes de encolar) |
| `silence_watchdog_job` | `SILENCE_MULTIPLIER=2` para evitar false alerts |
| `inquisition_cadence_job` | `idx_verdict_expiry` + `superseded_by IS NULL` garantizan que solo procesa verdicts realmente expirados y no ya reemplazados |

---

## Artefactos

| Job | Artefactos |
|-----|-----------|
| `heartbeat_tick` | `harvest_run` (INSERT append-only) + `source_health` (UPDATE) por cada source ejecutada |
| `silence_watchdog_job` | `alert` (por cada source silente — dedup-aware: UPDATE si alerta abierta ya existe, INSERT si nueva) |
| `inquisition_cadence_job` | `gestion_item` RESEARCH via `open_or_refresh(conn, AnomalyResult(...))` — idempotente por `dedupe_key UNIQUE` en `gestion_item` |

---

## Fallo → routing

| Fallo | Consecuencia |
|-------|-------------|
| APScheduler missed job | Coalesce: no re-ejecuta perdidos, espera el próximo tick |
| Job exception | Log + `fire_alert(source_key:scheduler)` + continue (el scheduler no muere) |
| DB unreachable | Job falla en la query inicial; APScheduler reintenta en el próximo tick |

---

## Idempotencia

- `heartbeat_tick`: itera TODAS las sources due en el tick (no solo una); single-producer (max_instances=1) garantiza no solapamiento.
- `inquisition_cadence_job`: `open_or_refresh(conn, AnomalyResult)` idempotente via `dedupe_key UNIQUE` en `gestion_item`.
- `silence_watchdog_job`: alerta dedup-aware — UPDATE de alerta abierta existente para la misma source antes de INSERT nueva.

---

## Estado

IMPLEMENTADO — `pipeline/ops/scheduler.py`, `pipeline/ops/silence_watchdog.py`,
`pipeline/ops/inquisition_schedule.py`. La lógica de scheduling y watchdog es
completamente funcional. El scraping real disparado por `heartbeat_tick` es
HARVEST-GATED en sources Tier-1.

---

## €0 vs gasto

| Componente | Coste |
|-----------|-------|
| Lógica de scheduling, circuit breaker, silence check | €0 |
| δ TTL cadencia, DB writes de alert y gestion_item | €0 |
| Scraping Tier-0 (HTTP abierto) disparado por heartbeat | €0 |
| Scraping Tier-1 (anti-bot, proxies premium) disparado por heartbeat | GASTO (proxies) |
