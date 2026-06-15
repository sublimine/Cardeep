# 07 — EVICT-DELETE

> **ESTADO: IMPLEMENTADO** (€0) — `pipeline/evict.py` + `migrations/0033_evict.sql` + 24 tests. El módulo, los 3 gates y la migración están construidos y probados (tmp/rolled-back). **`--apply` (borrado real) NUNCA se ha ejecutado** sobre los datos reales (161 MB raw / DB): es destructivo y requiere dealer confirmado-muerto + los 3 gates verdes + autorización del Director.

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

## Pasos atomo (DISENO — pipeline/evict.py POR CONSTRUIR)

1. **`check_preconditions(conn, cdp_code) -> (bool, list[str])`** — verifica los 3 gates. Solo reads. Retorna `(False, [lista de razones])` si cualquier gate falla.

2. **Si `--dry-run`** — imprimir plan de borrado detallado (que filas se borrarian, que se actualizaria) y terminar sin ejecutar nada. Siempre disponible, sin permisos adicionales.

3. **LRU evict de raw storage** — borrar archivos raw de harvest en disco por watermark: los mas antiguos primero si disco supera threshold definido. Solo archivos raw del dealer, no recipes ni artefactos de pipeline.

4. **`tombstone_entity(conn, cdp_code)`** — `UPDATE entity SET status = 'EVICTED', evicted_at = now()`. NO DELETE de la fila de entity: preservar historial de existencia del dealer.

5. **`delete_vehicle_rows(conn, entity_ulid)`** — `DELETE FROM vehicle WHERE entity_ulid = :entity_ulid` (el `entity_ulid` se resuelve desde `cdp_code` vía `entity`; `vehicle` NO tiene `cdp_code`). Los vehículos sí se borran definitivamente: ahorran espacio y no tienen valor histórico post-evicción.

6. **`update_capacity_ledger(conn, cdp_code)`** — decrementar contadores en `capacity_ledger` (tabla NUEVA, se crea con el build de evict) y `source_health` para reflejar la baja del dealer.

7. **Log de auditoría** — `INSERT INTO audit_eviction (cdp_code, evicted_at, reason, actor)` (tabla NUEVA, append-only, se crea con el build de evict). Registro permanente e inmutable del borrado.

> **Tablas/columnas a crear con el build** (POR CONSTRUIR, no existen aún): `capacity_ledger`, `audit_eviction`, y `entity.status`/`entity.evicted_at` para el tombstone (o un mecanismo equivalente). El migration del build las añade.

## Gate de verificacion post-ejecucion

| Check | Condicion esperada |
|-------|-------------------|
| entity tombstone | `entity.status == 'EVICTED'` |
| Vehiculos borrados | `COUNT(vehicle WHERE entity_ulid = :ulid) == 0` |
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
