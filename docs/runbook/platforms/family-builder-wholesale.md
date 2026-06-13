# family_builder_wholesale — Wix/Ueni/Google Sites/BaseKit/Squarespace/Duda
**Estado:** ✅ VALIDADO (verdict id=598, count=1.224, 2026-06-13)  ·  **Grupo:** Long-tail (familia builder)

## Identidad
- source_key: `family_builder_wholesale` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa · members: 9 · producing: 2

## Data-layer (la fuente real)
La cola más dura/variada. El multiplicador que SÍ generaliza es la **superficie de datos estructurados** (schema.org JSON-LD que el builder emite para SEO). Receta degradada en estrategias ordenadas:
- **Strategy 1 — schema.org `ItemList` de `Vehicle`/`Product`** (listado ueni, verificado live en crestanevada.es: `<script id="jsonld-itemlist-listado">` con 24 `Vehicle` por página: brand/model/year/km/fuel/transmission/price + PDP url con id numérico final; `?pagina=N` acumulativo → drena todo, ~2.450 cars).
- **Strategy 2 — bloques `Vehicle`/`Product` JSON-LD sueltos** (cualquier builder que los emita).
- **Strategy 3 — heurística SSR card** (anchors con precio; fallback honesto).
- Engine: `curl_cffi` chrome131, SSR; `LISTING_PATHS` propios del builder; paginación `?pagina=N` (`DEFAULT_MAX_PAGES=120`).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET listing del builder.
2. Strategy 1: parsear `jsonld-itemlist-listado` (24 Vehicle/página), `?pagina=N` acumulativo.
3. Fallback Strategy 2/3 si no hay ItemList.
4. Miembros sin superficie machine-readable se registran HONESTAMENTE como reachable-pero-sin-inventario-SSR (no se fabrican).

## Receta / config
- Conector: `pipeline/platform/family_builder_wix_ueni_google_sites_basekit__wholesale.py` · `FAMILY_KEY='family_builder_wholesale'` · STEALTH · t0_open

## Validación (VAM)
- **verdict id=598 TRUSTWORTHY** · count=**1.224** cars · div 0.0 · healthy/closed.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale \
    --dealers crestanevada.es majadahondamotor.es bugasgroup.com
python -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale --from-fingerprints --limit 12
```

## Trampas / notas
- 9 members, solo 2 productores: la cola es genuinamente de bajo rendimiento (como predijo el mapa de familias).
- Wix warmupData JS, Squarespace/BaseKit SSR vacío, Google Sites contacto → no producen, registrados honestamente (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).
