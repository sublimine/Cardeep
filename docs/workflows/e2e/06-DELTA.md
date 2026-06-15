# 06 — DELTA

Detectar y registrar cambios de inventario entre runs de scraping: precios, kilometraje, fotos, entradas nuevas y bajas de stock.

## Disparador

Automatico: llamado por `pipeline/ingest.py` al final de cada harvest de dealer.

Manual para backfill o debug:

```bash
python -m pipeline.delta --source autoscout24 --since 2026-06-15T00:00:00
```

## Entradas

| Parametro | Descripcion |
|-----------|-------------|
| `conn` | Conexion PostgreSQL activa |
| `source_key` | Identificador de la fuente (ej: `"as24"`) |
| `run_started_at` | Timestamp ISO del harvest actual |
| `min_captured` | Minimo de vehiculos capturados — proviene de `delta_guard` |
| Estado previo en DB | Filas de `vehicle` con `last_seen`, `available`, `price`, `km`, `photo_url` |

## Pasos atomo

1. **`diff_vehicle(old, new) -> list[dict]`** — funcion pura sin I/O. Compara el estado previo contra el capturado y detecta:
   - `PRICE_CHANGE`: `price` cambio
   - `KM_CHANGE`: `km` cambio
   - `PHOTO_CHANGE`: `photo_url` cambio

2. **Aplicar diff** — UPDATE a los campos mutados + INSERT del evento delta en tabla de historial. Solo se escribe si hay cambio real (cero dead tuples innecesarios — respeta PG MVCC).

3. **`should_emit_gone(harvested, declared, previous_available) -> (bool, reason)`** — decide si es seguro emitir bajas:
   - **DECLARED guard**: `harvested >= declared * 0.95` → emitir GONE es seguro
   - **PREVIOUS guard**: `harvested >= previous_available * 0.50` → fallback cuando no hay `declared`
   - Si ambos guardianes fallan → NO emitir GONE (proteccion anti-purga prematura ante harvest parcial)

4. **`reconcile_gone(conn, source_key, run_started_at, *, max_gone_fraction=0.5) -> tuple[int, str]`** — ejecutar solo si el paso anterior retorno `True`:
   ```sql
   SELECT v.vehicle_ulid, v.price
     FROM vehicle v
     JOIN entity_source es ON es.entity_ulid = v.entity_ulid
    WHERE es.source_key = :source_key
      AND v.status = 'available'
      AND v.last_seen < :run_started_at
   ```
   Guarda interna adicional: si `stale/available > max_gone_fraction` (default 0.50) para inventarios de ≥ `MIN_INVENTORY_FOR_GUARD=20` vehículos, aborta sin tocar nada.
   Para cada vehiculo stale: `UPDATE vehicle SET status='gone', last_seen=now()` + evento GONE en `vehicle_event`.
   La columna no es `available BOOLEAN` sino `status TEXT` ∈ {`'available'`, `'gone'`}.
   Scope estricto via JOIN a `entity_source` — evita cross-source pollution.

## Umbrales de los guardianes

| Constante | Valor | Descripcion |
|-----------|-------|-------------|
| `DECLARED_THRESHOLD` | `0.95` | Fraccion minima de declarado para emitir GONE via guardian principal |
| `PREVIOUS_THRESHOLD` | `0.50` | Fraccion minima de anterior disponible para emitir GONE via fallback |

## Gate de verificacion

- `should_emit_gone()` debe retornar `True` antes de ejecutar cualquier `reconcile_gone`.
- Si el harvest fue parcial (below guard): delta abortado, warning en log, sin alert (comportamiento normal esperado).
- Ningun UPDATE de fila de vehicle sin cambio de campo verificado.

## Artefactos

| Artefacto | Descripcion |
|-----------|-------------|
| Filas `vehicle` actualizadas | `price`, `km`, `photo_url`, `status` (a `'gone'`), `last_seen` — no existe columna `available` ni `gone_at` en `vehicle` |
| Eventos delta | `PRICE_CHANGE`, `KM_CHANGE`, `PHOTO_CHANGE`, `NEW`, `GONE` en tabla `vehicle_event` |
| Sin dead tuples | Solo se escribe lo que cambio — compliance con mandato PG MVCC |

## Fallo — routing de errores

| Fallo | Comportamiento |
|-------|---------------|
| Harvest parcial (below guard) | Delta abortado; log warning; sin alert; estado DB intacto |
| Error DB en `reconcile_gone` | Rollback atomico; sin estado parcial; reintentar en proximo run |

## Idempotencia

- `reconcile_gone` es idempotente: vehículos ya con `status='gone'` son excluidos por `WHERE status='available'` — reejecutar no produce duplicados ni dead tuples adicionales.
- `diff_vehicle` es funcion pura: misma entrada produce mismo output, sin efectos laterales.

## Estado

IMPLEMENTADO — `pipeline/delta.py`, `pipeline/delta_guard.py`

**Nota A4-phase-2**: `reconcile_gone` esta activo en el path de harvest manual. Pendiente de cableado en los 43 conectores wholesale individuales del scheduler automatico.

## Coste

€0 total — DB ops puras, funcion Python pura, sin HTTP externo, sin LLM.
