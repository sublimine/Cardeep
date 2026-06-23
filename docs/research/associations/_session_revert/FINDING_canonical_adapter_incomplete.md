# HALLAZGO — La migración canónica de asociaciones (909a7be) está incompleta

Fecha: 2026-06-20 (sesión cobertura-100%)
Estado: **[VERIFICADO contra BD viva]** · Step 2 NO SELLABLE sin fix.

## Qué pasó
`python -m pipeline.discover {aedra,acevas,aecs}` (camino canónico introducido en 909a7be)
se corrió contra la BD viva y produjo:

| source | declared | fetched | new (insertados) | skip_no_province | VAM |
|--------|----------|---------|------------------|------------------|-----|
| aedra  | 615      | 615     | 0                | **615**          | REFUTED |
| acevas | 99       | 99      | **92 (dup)**     | 4                | REFUTED |
| aecs   | 74       | 74      | **32 (dup)**     | 2                | REFUTED |

Los `new` de acevas/aecs eran **duplicados** de dealers ya presentes (de OSM/plataformas/
script viejo) bajo otro cdp_code → 124 entidades basura. **Revertidas** en transacción
(snapshot en `duplicates_created_this_session.tsv`). Baseline restaurado: acevas=98, aecs=73
(+5 corroboraciones legítimas), aedra=586.

## Causa raíz (dos defectos del camino canónico)
El script standalone viejo `scripts/associations/upsert_associations.py` hace lo correcto:
1. **Escalera de dedup** contra `entity` viva ANTES de mintear: `bare-host website` →
   `nombre+municipio` → `nombre+provincia`. Si el dealer ya existe, **adjunta la asociación
   como `entity_source` corroborante** (propósito capture-recapture) en vez de crear entidad.
2. **Geocodifica desde `address_raw`** vía `geo_from_address.resolve()` → coloca aedra
   (que solo trae dirección, sin provincia ni lat/lon).

El camino canónico `pipeline.discover._upsert`:
1. **NO tiene escalera de dedup** — solo colisión exacta de `cdp_code` (ON CONFLICT). Y mintea
   códigos DISTINTOS al script viejo (usa `e.website` completo vs `bare_host`, y geo distinta)
   → no colapsa → duplica.
2. **No geocodifica direcciones** → aedra: 615/615 skip.

## Por qué importa más allá de asociaciones
`_upsert` es el camino COMPARTIDO de TODAS las fuentes censales (OSM, Overture, OEMs,
plataformas). La ausencia de escalera de dedup explica la duplicación residual del audit
`cd23e91` (139.851 filas): cdp_code no es clave de dedup suficientemente fuerte entre
fuentes ortogonales que describen el mismo dealer con atributos distintos.

## Remediación (decisión pendiente del Director)
- **A)** Portar la escalera de dedup + geocoding-from-address al camino canónico
  (`_upsert` o un pre-pass por fuente). Hace de `discover` la única verdad; reduce la
  duplicación global. Cambio de semántica de ingesta en producción → requiere aviso.
- **B)** Mantener `upsert_associations.py --commit` como ingester correcto de asociaciones,
  y que el adapter canónico DELEGUE en las mismas libs (`dedup_upsert`/`geo_from_address`)
  para no tener dos fuentes de verdad.
- **C)** Híbrido: el adapter canónico llama a la escalera de dedup compartida; el gate VAM
  cuenta `attached_or_new` en vez de exigir `new==declared`.

VAM honesto: ninguna de las tres asociaciones queda SELLADA hasta cerrar esto.
