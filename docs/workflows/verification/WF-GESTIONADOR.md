# WF-GESTIONADOR — Detección + Máquina de Estados (L3)

## Objetivo

Detectar anomalías en el pipeline con 7 detectores deterministas €0 y gestionar
su ciclo de vida mediante una máquina de estados con SLA por lane, garantizando
que ninguna anomalía quede sin verdict antes de marcarse RESOLVED.

---

## Disparador

- **Post-ingest**: llamado tras cada harvest para detectar anomalías en la
  fuente procesada.
- **Post-Inquisition**: `router.py` en L4 abre `gestion_item` con lane
  asignada; el gestionador toma el relevo.
- **Scheduler heartbeat**: `scheduler.py` puede disparar detect sobre fuentes
  recientemente procesadas dentro del tick de 15 min.

---

## Entradas

| Fuente | Descripción |
|--------|-------------|
| Métricas de harvest actual vs. histórico | En DB; detectores hacen reads puros |
| `gestion_item` | Tabla con `dedupe_key UNIQUE` para idempotencia |
| `alert` | Tabla donde se escribe la alerta con origen exacto |

---

## Pasos átomo — Detección (7 detectores LIVE)

Todos los detectores son reads puros sobre la DB: idempotentes, sin efectos
secundarios.

### 1. `count_inflation`

Cuenta actual > histórico × (1 + TAU_COUNT) sin que exista un declared match
que justifique el incremento.

```
TAU_COUNT = 0.02
```

### 2. `silent_cap`

La cuenta reportada por la fuente es ≤ `SILENT_CAP_MAX_ROWS` durante ≥3 runs
consecutivos, indicando un techo artificial de paginación.

```
SILENT_CAP_MAX_ROWS = 1000
```

### 3. `field_loss`

Tasa de campos nulos supera el umbral duro o el Z-score crítico respecto a la
distribución histórica de la fuente.

```
FIELD_LOSS_HARD_THRESH = 0.30   # 30% de nulos en cualquier campo relevante
FIELD_LOSS_Z_CRIT      = 3.0    # Z-score sobre media histórica
```

### 4. `staleness`

`now() - last_seen > STALENESS_TTL[kind]`. TTL por tipo de entidad:

| kind | TTL |
|------|-----|
| `compraventa` | 3 días |
| `concesionario_oficial` | 3 días |
| `garaje` | 7 días |
| `particular` | 7 días |
| `desguace` | 30 días |
| `plataforma` | 1 día |

### 5. `fabrication`

Vehículos con campos implausibles: `year < 1900` o `year > current_year + 2`,
precios negativos, o combinaciones de make/model estadísticamente imposibles.

### 6. `coverage_gap`

`captured / declared < _DEFAULT_FLOOR` de forma persistente a lo largo de
múltiples runs, indicando que la fuente no está siendo drenada completamente.

```
_DEFAULT_FLOOR = 0.85
```

### 7. `price_trap`

Todos los precios de una fuente son iguales o caen en un rango
sospechosamente estrecho, sugiriendo datos sintéticos o un error de parseo.

### Detectores STUB (no disparan aún)

| Detector | Estado | Motivo |
|----------|--------|--------|
| `geo_resolution_drift` | STUB | Diseñado, no activado |
| `classifier_drift` | STUB | Diseñado, no activado |

---

## Pasos átomo — Routing y máquina de estados

### `open_or_refresh(conn, anomaly: AnomalyResult, *, actor='detector') -> int`

Recibe un `AnomalyResult` (de `detect.py`: detector, subject_type, subject_key, severity,
score, measured, baseline, lane, quarantines, dedupe_key) y devuelve el `id` del item. UPSERT
MVCC-safe:

```sql
INSERT INTO gestion_item (detector, subject_type, subject_key, severity, score,
    measured, baseline, lane, state, quarantines, opened_at, sla_due, dedupe_key)
VALUES (..., 'OPEN', ..., now(), <now()+SLA>, ...)
ON CONFLICT (dedupe_key) DO UPDATE
    SET measured = EXCLUDED.measured, severity = EXCLUDED.severity, score = EXCLUDED.score,
        -- reopen si estaba cerrado (regresión): state→REOPENED, limpia closed_at/closed_reason
        state = CASE WHEN gestion_item.closed_at IS NOT NULL THEN 'REOPENED' ELSE gestion_item.state END
RETURNING id, state, (xmax = 0) AS is_new
```

Idempotente: una segunda llamada con el mismo `dedupe_key` refresca measured/severity/score
sin crear duplicado (y reabre si estaba cerrado). NO toca state/opened_at de un item ya abierto.

### Máquina de estados

```
OPEN
  |
  v
ROUTED ──────────────────────────── lane asignada por router.py
  |
  v
IN_PROGRESS ─────────────────────── trabajo activo en la lane
  |
  ├──→ REVERIFYING ────────────────── re-check en curso
  |         |
  |         v
  ├──→ RESOLVED* ──────────────────── requiere verdict_id FK
  ├──→ QUARANTINED
  ├──→ ESCALATED
  ├──→ WONT_FIX
  └──→ REOPENED
```

*RESOLVED no puede alcanzarse sin `verdict_id` (FK a `verification_verdict(id)` — "sin recheck independiente, no se cierra"; `transition()` lo exige).

---

## SLA por lane

| Lane | SLA |
|------|-----|
| `AUTO_FIX` | 6 horas |
| `RESEARCH` | 7 días |
| `QUARANTINE` | 48 horas |
| `ESCALATE_GASTO` | Sin SLA — decisión del Director |
| `ESCALATE_OWNER` | Sin SLA — requiere intervención de ownership |

---

## Gate de verificación

| Gate | Mecanismo |
|------|-----------|
| RESOLVED requiere verdict | `gestion_item.verdict_id` FK a `verification_verdict(id)` — `transition()` exige verdict_id para RESOLVED |
| Sin duplicados | `dedupe_key UNIQUE` constraint en `gestion_item` |
| Origen exacto en alert | `source_key:phase[:cdp]` — trazabilidad completa |

---

## Artefactos

| Artefacto | Tabla | Descripción |
|-----------|-------|-------------|
| Item de gestión | `gestion_item` | Estado, lane, dedupe_key, severity, sla_hours, verdict_id |
| Alerta | `alert` | Origen exacto: `source_key:phase[:cdp]`, severidad |

---

## Fallo → routing

| Fallo | Consecuencia |
|-------|-------------|
| Detector exception | Log + skip del detector fallido; no bloquea el pipeline ni los demás detectores |
| `open_or_refresh` exception | Log + alert; el item no se crea en este ciclo |
| Constraint `dedupe_key` collision | Solo posible si el formato de dedupe_key cambia; requiere investigación manual |

---

## Idempotencia

- `open_or_refresh`: `ON CONFLICT (dedupe_key) DO UPDATE` — idempotente.
- Detectores: reads puros sobre DB — idempotentes, sin efectos secundarios.

---

## Estado

IMPLEMENTADO — `pipeline/gestionador/detect.py`, `pipeline/gestionador/route.py`.
Stubs `geo_resolution_drift` y `classifier_drift` están en `detect.py` pero no
se activan.

---

## €0 vs gasto

€0 total — DB reads para detección, DB upserts para routing y alertas. Sin
HTTP, sin LLM, sin proxies.
