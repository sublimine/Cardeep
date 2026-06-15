# E2E — Ciclo de Vida de un Dealer

## Objetivo

Seguir a una entidad (dealer, compraventa, desguace) desde su primer descubrimiento en una
fuente del censo hasta su borrado definitivo de disco, pasando por cada fase del pipeline con
sus gates de verificacion y puntos de fallo explicitamente mapeados.

## Estados del dealer en DB

La tabla `entity` registra la posicion de cada dealer en el grafo. Los campos que gobiernan
las transiciones son `status` y `last_seen` en `entity`; el estado de completitud vive en
la tabla `entity_completion` (gates g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta).
`entity` no tiene columnas `vam_verified` ni `completion_score` — ambas son propiedades
derivadas de otras tablas.

```
DISCOVERED  (entity.status = 'unverified'; ingresado por discover.py)
    |
    | gate: cdp_code bien formado + VAM quorum post-discover
    v
SCRAPED  (status = 'unverified'; harvest_run registrada)
    |
    | gate: paginacion drenada + ultima pagina explicita
    v
RECIPE_LOCKED  (entity.recipe_version NOT NULL; gate G3 en entity_completion)
    |
    | gate: recipe reproduce >= umbral, 0 campos criticos nulos
    v
INGEST_READY  (vehicle rows INSERTadas; VAM verdict emitido)
    |
    | gate: VAM count post-ingest >= 2 vias + 0 filas invalidas
    v
LIVE  (entity.status = 'active'; entity_completion.g4_served=true; DELTA loop continuo)
    |
    | condicion: ingesta TRUSTWORTHY + recipe commiteada + conteos cuadrados
    v
[EVICTED]   <- pipeline/evict.py (POR CONSTRUIR; entity.status = 'closed')
```

Nota: DISCOVERED/SCRAPED/RECIPE_LOCKED/INGEST_READY/LIVE son nombres de fase del
pipeline, NO valores del enum `entity_status`. El enum real solo tiene:
`'active'`, `'closed'`, `'unverified'`.

El tipo enum `entity_status` solo admite `'active'`, `'closed'`, `'unverified'`.
Los estados internos de gestion (`RESEARCH`, `PAUSED`, `ERROR`) NO son valores de
`entity.status` — viven en `gestion_item.state` ∈ {OPEN, ROUTED, IN_PROGRESS,
REVERIFYING, RESOLVED, QUARANTINED, ESCALATED, WONT_FIX, REOPENED} y en la lane
del `gestion_item` ∈ {AUTO_FIX, RESEARCH, QUARANTINE, ESCALATE_GASTO, ESCALATE_OWNER}.

## Fases del pipeline

| Fase | Documento | Trigger | Modulo | Estado | €0/Gasto |
|---|---|---|---|---|---|
| 1 — DESCUBRIR | 01-DISCOVER.md | CLI / cadencia scheduler | pipeline/discover.py | IMPLEMENTADO | €0 |
| 2 — SCRAPEAR | 02-SCRAPE.md | post-discover / scheduler | pipeline/engine/fetch.py + governor.py | IMPLEMENTADO | €0 |
| 3 — RECETA | 03-RECIPE.md | post-scrape / recipe-hunt agent | pipeline/platform/ (44 conectores) | IMPLEMENTADO | €0 / Gasto Tier-1 |
| 4 — INGEST | 04-INGEST.md | post-recipe | pipeline/ingest.py | IMPLEMENTADO | €0 |
| 5 — SERVE-API | 05-SERVE-API.md | continuo | services/api/main.py | IMPLEMENTADO | €0 |
| 6 — DELTA | 06-DELTA.md | post-ingest / heartbeat | pipeline/delta.py + delta_guard.py | IMPLEMENTADO | €0 |
| 7 — EVICT/DELETE | 07-EVICT-DELETE.md | capacidad + VAM gate | pipeline/evict.py | POR CONSTRUIR | €0 |

## Gates duros entre fases

### DISCOVERED → SCRAPED
- `cdp_code` bien formado (patron: `dominio|cif|nombre+muni|nombre+prov`)
- `province_code` en rango "01"–"52"
- VAM quorum ≥2 vias sobre conteo de entidades de la fuente: TRUSTWORTHY
- `entity.status = 'discovered'` en DB

### SCRAPED → RECIPE_LOCKED
- Paginacion drenada hasta pagina explicita de fin (no timeout)
- `harvest_run.pages_scraped == harvest_run.pages_expected`
- Crudo guardado en `data/` con hash de integridad

### RECIPE_LOCKED → INGEST_READY
- Recipe reproduce >= umbral de campos correctos sobre muestra ciega
- 0 campos criticos nulos: precio, referencia/VIN, deep-link
- `recipe.yaml` commiteada en `pipeline/platform/`

### INGEST_READY → LIVE
- VAM count post-ingest: conteo DB == lote por ≥2 vias
- 0 filas rechazadas por validacion de borde (sin deep-link, sin campo clave)
- Sin drift de esquema detectado
- Gates G1–G5 calculados en `entity_completion` via `pipeline/complete.py`

### LIVE → [EVICTED]
- Ingesta TRUSTWORTHY (VAM ≥2): releido en el momento del borrado
- Recipe/config commiteada en git
- Conteos cuadrados entre DB y crudo a disco
- Si CUALQUIERA de los tres falla: no se borra NADA

## Idempotencia global

Cada fase esta disenada para ser re-ejecutable sin efectos secundarios adicionales:

- **Discover**: `INSERT entity ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()`
- **Scrape**: ficheros crudos identificados por `(cdp_code, harvest_run_id)`, no se sobreescriben
- **Ingest**: `INSERT vehicle ON CONFLICT (dedupe_key) DO UPDATE` solo campos mutados;
  eventos delta se emiten una sola vez por transicion de estado
- **VAM**: `record_count_verdict` con `subject_key` unico; re-ejecutar produce nueva fila
  sin invalidar la anterior; quorum se recalcula sobre el conjunto actualizado
- **Delta**: `reconcile_gone()` opera sobre ventana temporal; GONE solo se emite si
  `should_emit_gone()` aprueba: `DECLARED_THRESHOLD = 0.95` (probe principal) o
  `PREVIOUS_THRESHOLD = 0.50` (fallback sin declared); `reconcile_gone()` usa adicionalmente
  un `max_gone_fraction=0.50` propio como guarda interna.
- **Evict**: watermark de disco antes de borrar; `tombstone.json` como prueba de vida

## Tablas DB involucradas

| Tabla | Fase principal | Proposito |
|---|---|---|
| entity | DISCOVER | Registro maestro de cada punto de venta |
| vehicle | INGEST / DELTA | Inventario vivo con historia de cambios |
| verification_verdict | VAM (todas) | Resultado del quorum de verificacion |
| inquisition_verdict | INQUISITION | Veredicto adversarial por entidad |
| gestion_item | GESTIONADOR | Cola de tareas y estados de reparacion |
| alert | Cualquier fallo | Alertas con origen exacto y lane de routing |
| harvest_run | SCRAPE / INGEST | Registro de cada corrida de harvest |
| source_health | DISCOVER | Salud por fuente del censo |
| verdict_audit | Transversal | Cadena de auditoria inmutable por INSERT en verification_verdict |
