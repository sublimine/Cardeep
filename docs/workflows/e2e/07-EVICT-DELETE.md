# 07 — EVICT-DELETE

> **ESTADO: IMPLEMENTADO** (€0) — `pipeline/evict.py` + `migrations/0033_evict.sql` + 25 tests. El módulo, los 3 gates y la migración están construidos y probados (tmp/rolled-back). **`--apply` (borrado real) NUNCA se ha ejecutado** sobre los datos reales (161 MB raw / DB): es destructivo y requiere dealer confirmado-muerto + los 3 gates verdes + autorización del Director.

Borrar de forma segura e irreversible un dealer y su inventario tras confirmar que está muerto: sin actividad, sin verdict `TRUSTWORTHY` vigente (evidencia `REFUTED`/`UNVERIFIED` o gone-reconcile), recipe preservada en git.

## Disparador

**Manual exclusivo** — solo el Director puede disparar BORRAR. No hay scheduler automatico para este workflow.

```bash
# Ejecucion real (irreversible)
python -m pipeline.evict --cdp CDP-ES-XX-XXXXXXXX

# Siempre verificar primero con dry-run
python -m pipeline.evict --cdp CDP-ES-XX-XXXXXXXX --dry-run
```

## Entradas

| Entrada | Descripcion |
|---------|-------------|
| `cdp_code` | Codigo canonico del dealer a evictar |
| Estado en DB | Tablas/vista: `entity`, `vehicle`, `verification_verdict`, `entity_completion`, `v_dealer_recipe`, `gestion_item` (no existe tabla `dealer_recipe`; la receta es `recipe.yaml` en git + la vista `v_dealer_recipe`) |

## Precondiciones — 3 GATES DUROS

Los tres deben ser `True` simultaneamente antes de ejecutar cualquier cambio. Si cualquiera falla: abort inmediato, cero cambios.

### Gate 1 — VAM confirma muerte (NO hay TRUSTWORTHY vigente)

- (Los valores reales de `verification_verdict.verdict` son `TRUSTWORTHY | REFUTED | UNVERIFIED | QUARANTINED` — NO existe 'UNTRUSTWORTHY'.)
- No existe ningún verdict `TRUSTWORTHY` vigente (`expires_at IS NULL OR expires_at > now()`, `superseded_by IS NULL`) para el inventario del dealer.
- Existe evidencia reciente `REFUTED`/`UNVERIFIED` (o gone-reconcile) de que el dealer está muerto.
- Quorum: ≥2 paths confirman muerte (inventario disponible = 0 o fuente inaccesible).

### Gate 2 — Recipe PRESERVADA + commiteada (re-scrapeable post-evict)

Pasa si CUALQUIERA de las dos formas se cumple:
- **(a)** `recipe.yaml` per_dealer commiteado en `git HEAD` (`countries/ES/.../dealers/{cdp}/recipe.yaml`; own-site / long-tail), O
- **(b)** **connector-coverage**: `v_dealer_recipe.recipe_kind = 'connector'` — la receta ES el conector de plataforma compartido (Python commiteado en `pipeline/platform/`), que cubre ~98,4% del corpus. Exigir un yaml per-dealer a los dealers connector los haría permanentemente in-evictables (incorrecto); el conector es el activo commiteado que los re-scrapea si reaparecen.
- Propósito: preservar el conocimiento de cómo scrapearlo. Sin NINGUNA de las dos formas → abort.

### Gate 3 — Counts cuadrados

- `vehicle` disponible == 0 para el dealer (`WHERE entity_ulid = <ulid> AND status='available'` — `vehicle` NO tiene columna `cdp_code`; se une por `entity_ulid`).
- `entity_completion.g4_served = False` (inventario vacío confirmado por el gate G4 de completitud).
- `gestion_item` del dealer en estado `RESOLVED` o sin items `OPEN`.

## Pasos atomo (IMPLEMENTADO — `pipeline/evict.py`, migracion `0033_evict.sql`)

Orden real de `evict_dealer(conn, cdp_code, *, dry_run=True, actor="director")`:

1. **`check_preconditions(conn, cdp_code) -> (bool, list[str])`** — verifica los 3 gates. Solo reads. Si cualquiera falla: `evicted=False` + razones, cero cambios.

2. **Si `dry_run` (DEFAULT)** — resuelve `entity_ulid`, cuenta vehiculos, retorna el plan (`vehicles_to_delete`, etc.) sin tocar nada.

3. **Snapshot de disco + `_measure_raw_files(cdp_code)`** — mide los archivos raw del dealer SIN borrarlos aun (se borran solo tras el commit; borrar antes arriesgaba perdida permanente en un abort).

4. **Transaccion atomica unica** (la DB se toca solo aqui; el filesystem NO):
   - **Re-check de los 3 gates DENTRO de la transaccion** — si el estado cambio entre el check externo y la transaccion, abort (raise) y rollback total.
   - **Tombstone entity** — `UPDATE entity SET status='evicted', evicted_at=now() WHERE cdp_code=$1 AND status<>'evicted'`. NO DELETE: preserva el historial de existencia. El guard evita reescribir una fila ya evicted (no MVCC no-op).
   - **Tombstone vehiculos como GONE** — `UPDATE vehicle SET status='gone', last_seen=now() WHERE entity_ulid=$1 AND status<>'gone'`. **NO `DELETE FROM vehicle`**: el DELETE cascadea a `vehicle_event` (FK ON DELETE CASCADE), cuyo trigger append-only PROHIBE borrar filas -> la eviccion entera abortaria para cualquier dealer que haya emitido un evento. El tombstone conserva el `historial completo` que promete el producto y saca los coches del inventario servido.
   - **`INSERT INTO capacity_ledger`** `(cdp_code, vehicles_deleted, raw_bytes_freed, disk_free_before, disk_free_after)` — `raw_bytes_freed` = bytes PLANEADOS; `disk_free_after` = NULL (los archivos se borran tras el commit).
   - **`INSERT INTO audit_eviction`** `(cdp_code, reason, actor, vehicles_deleted, raw_bytes_freed)` — append-only, inmutable.

5. **`_delete_raw_files(...)` tras el commit** — solo entonces se borran fisicamente los archivos raw del dealer (post-commit; un abort no pierde datos).

> Las tablas `capacity_ledger` y `audit_eviction` y las columnas `entity.status`/`entity.evicted_at` YA existen (migracion `0033_evict.sql`). `--apply` (borrado real) NUNCA se ha ejecutado sobre datos reales.

## Gate de verificacion post-ejecucion

| Check | Condicion esperada |
|-------|-------------------|
| entity tombstone | `entity.status == 'evicted'` |
| Vehiculos retirados | `COUNT(vehicle WHERE entity_ulid = :ulid AND status='available') == 0` (filas conservadas como `status='gone'`) |
| Ledger decrementado | `capacity_ledger` refleja la baja del dealer |

## Artefactos

| Artefacto | Accion | Reversible |
|-----------|--------|-----------|
| `entity` row | UPDATE a `status='EVICTED'` (tombstone) | No (pero la fila permanece) |
| `vehicle` rows | DELETE permanente | No |
| `audit_eviction` | INSERT registro permanente | No |
| Raw storage | Archivos LRU purgados | No |
| `recipe.yaml` en git | Preservada intacta en HEAD (geo tree / `_tier1` / `_platforms`) | N/A |

## Fallo — routing de errores

| Fallo | Comportamiento |
|-------|---------------|
| Cualquier gate fallido | Abort con mensaje descriptivo; cero cambios en DB |
| Error DB en medio de ejecucion | Rollback atomico via transaccion; estado pre-eviccion intacto |
| Disco insuficiente para LRU evict | Log warning; continuar con el borrado DB igualmente |

## Idempotencia

- `check_preconditions`: idempotente (solo reads).
- `tombstone_entity`: idempotente — `UPDATE ... WHERE status != 'EVICTED'` o `ON CONFLICT DO NOTHING`.
- Si la ejecucion cae a mitad: los 3 gates se re-verifican en el siguiente intento y bloquean si el estado es inconsistente.

## Estado

**IMPLEMENTADO** (€0) — `pipeline/evict.py` + `migrations/0033_evict.sql` (`entity_status`+'evicted', `entity.evicted_at`, `capacity_ledger`, `audit_eviction` append-only con trigger de inmutabilidad) + `tests/test_evict.py` (24✓). Gate 2 acepta recipe.yaml-en-HEAD **o** connector-coverage. **El borrado real (`--apply`) sigue gated**: destructivo, requiere dealer confirmado-muerto + 3 gates verdes + autorización; no se ha corrido sobre datos reales.

## Coste

€0 total — DB ops y filesystem, sin LLM, sin HTTP externo.
