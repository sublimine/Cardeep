# 04-INGEST — Ingesta de vehículos scrapeados y gate VAM post-ingest

Recibe el harvest normalizado de `harvest_dealer.py`, lo reconcilia contra el estado previo
en DB, emite deltas (NEW/GONE/PRICE_CHANGE/KM_CHANGE/PHOTO_CHANGE) y calcula el completion
score del dealer.

---

## Disparador

Llamado por `pipeline/harvest_dealer.py` tras scraping exitoso (coverage gate pasado en
`pipeline/ops/coverage_verify.py`). No se invoca directamente desde el scheduler.

---

## Entradas

| Entrada | Tipo | Descripción |
|---|---|---|
| `harvest` | `list[dict]` | Vehículos normalizados: `deep_link`, `vin_ref`, `make`, `model`, `year`, `km`, `price`, `fuel`, `transmission`, `photo_url` |
| `conn` | `psycopg2.Connection` | Conexión PostgreSQL |
| `geo` | `dict` | Municipio resuelto del dealer |
| `source_key` | `str` | Identificador de fuente, ej. `"as24"`, `"coches_net"` |
| `cdp_code` | `str` | Identificador canónico del dealer |

---

## Pasos átomo

1. **Llamar función principal**: `ingest_dealer(conn, geo, harvest, source_key="as24")`.
   Firma real: `async def ingest_dealer(conn: asyncpg.Connection, geo: GeoResolver, harvest: DealerHarvest, source_key: str = "as24") -> dict`.
   El `cdp_code` se calcula internamente a partir de los datos del dealer en el harvest — no se pasa como parámetro.

2. **Validar province_code**: verificar que `province_code.isdigit() and "01" <= province_code <= "52"` — gate duro.
   Si falla → retorna `{"error": "...", "ingested": 0}`, no se lanza `ValueError`.

3. **Diff por vehículo**: para cada vehículo en harvest, `diff_vehicle(old, new)` →
   detecta `PRICE_CHANGE`, `KM_CHANGE`, `PHOTO_CHANGE` comparando contra fila previa.

4. **INSERT/UPDATE vehículos**: `INSERT INTO vehicle ... ON CONFLICT (entity_ulid, deep_link) DO UPDATE` no aplica aquí — ingest.py usa un patrón explícito: SELECT previo de `vehicle WHERE entity_ulid=...`, luego INSERT si `deep_link` no existe o UPDATE si existe. La constraint única real en `vehicle` es `UNIQUE (entity_ulid, deep_link)`. Los vehículos nuevos tienen `status='available'` (no `'NEW'` — `'NEW'` es el event_type en `vehicle_event`, no el status de la fila).

5. **GONE guard**: `should_emit_gone(harvested, declared, previous_available)` →
   `(bool, reason)`.
   - `DECLARED_THRESHOLD=0.95`: si `harvested >= declared * 0.95` → safe emitir GONE.
   - `PREVIOUS_THRESHOLD=0.50`: fallback cuando `declared` no disponible.
   Protege contra purga prematura por harvest incompleto.

6. **Reconciliar GONE**: `reconcile_gone(conn, source_key, run_started_at, *,
   min_captured)` — marca como GONE los vehículos no presentes en el harvest actual,
   scoped por `(source_key, run_started_at)`.

7. **VAM gate**: `await record_count_verdict(conn, subject_type="entity_inventory", subject_key=code, claim="available inventory == source declared count", paths={"db_available": available, "harvested": len(harvest.vehicles), "source_declared": harvest.declared_count}, tolerance=0.0)` → `TRUSTWORTHY` si modal con quórum ≥2 paths sin rival de ≥2. Nótese: `subject_type` es `"entity_inventory"`, no `"dealer"`.

8. **Completion gates**: `upsert_completion(conn, cdp_code)` →
   `compute_completion(conn, cdp_code)` evalúa G1–G5 y escribe en `entity_completion`
   (no en una columna `completion_score` de `entity` — esa columna no existe).

---

## Gate de verificación

| Gate | Condición | Bloquea ingest |
|---|---|---|
| `province_code` | `"01"` ≤ code ≤ `"52"` | Sí — `ValueError` + abort |
| G1 (`complete.py`) | entity existe + province_code válido + cdp_code bien formado | No bloquea, señaliza |
| G2 (`complete.py`) | `deep_link NOT NULL` rate ≥ 0.98 en el harvest | No bloquea, alert |
| G4 (`complete.py`) | `available_inventory == declared` (DB count == declared) | No bloquea, señaliza |
| VAM quórum | ≥2 paths coinciden en count modal sin rival | No bloquea; señaliza con verdict `REFUTED` o `UNVERIFIED` (no `UNTRUSTWORTHY` — ese valor no existe) |
| GONE guard | `should_emit_gone()` → True antes de reconcile_gone | Protege — no purga si False |

---

## Artefactos

- `vehicle` — filas INSERT / UPDATE con `status='available'`; eventos de cambio en `vehicle_event`
- `verification_verdict` — fila por run (`subject_type='entity_inventory'`, `claim_kind='count'`,
  `verdict` ∈ {`TRUSTWORTHY`,`REFUTED`,`UNVERIFIED`,`QUARANTINED`} — no existe `UNTRUSTWORTHY`)
- `entity_completion` — gates G1–G5 actualizados vía `upsert_completion` (no `entity.completion_score`)
- `vehicle_event` — eventos: `NEW`, `GONE`, `PRICE_CHANGE`, `KM_CHANGE`, `PHOTO_CHANGE`

---

## Fallo → routing

| Fallo | Acción |
|---|---|
| `province_code` inválido | `ValueError`, abort, `fire_alert(phase='ingest')` |
| VAM REFUTED / UNVERIFIED | `gestion_item` lane RESEARCH, ingest continúa (el valor de verdict es `REFUTED` o `UNVERIFIED`, nunca `UNTRUSTWORTHY`) |
| G2 < 0.98 (deep_links corruptos) | alert severity='warning' + `auto_repair('re_receta')` |
| `reconcile_gone` no cableado en conector | GONE no se emite para esa source (pendiente A4-phase-2) |

---

## Idempotencia

| Objeto | Mecanismo |
|---|---|
| `vehicle` | `INSERT ON CONFLICT (source_key, external_id) DO UPDATE` |
| `verification_verdict` | INSERT simple (sin ON CONFLICT — la tabla no tiene `dedupe_key`; la idempotencia es por TTL cadencia, no por constraint única en esta tabla) |
| `reconcile_gone` | Scoped por `(source_key, run_started_at)` — re-ejecución produce el mismo conjunto GONE |

---

## Estado

**IMPLEMENTADO** — `pipeline/ingest.py`, `pipeline/delta.py`, `pipeline/delta_guard.py`,
`pipeline/complete.py`, `pipeline/verify.py`.

Nota A4-phase-2: `reconcile_gone` en `pipeline/delta.py` está implementado pero **pendiente
de cableado en los 43 conectores wholesale**. Actualmente funciona en el path manual;
los conectores automáticos no lo invocan todavía.

---

## €0 vs gasto

€0 total — operaciones DB puras (PostgreSQL), sin LLM, sin HTTP externo.
