# RACC Coches de Ocasión — racc

**Estado:** ✅ VALIDADO (verdict id=634, count=96, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace / aggregator (miembro del conector conjunto faciliteacoches+RACC)

## Identidad
- cdp_code: `CDP-ES-00-58C3W3P9` · kind: `plataforma` · source_group: `association` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `racc` · data_surface: `json_ld` (WordPress, Apache/PHP 8.3)

## Data-layer (la fuente real)
- Endpoint: `GET https://cochesocasion.racc.es/coches-ocasion/vehiculos-de-ocasion/` (page_size 12, paginado).
- Endpoint PDP: el card NO lleva vendedor; el dealer está en el JSON-LD del PDP `offers.seller` (@type:Organization, name).
- Auth/headers: curl_cffi `chrome131`, sin reto WAF → `t0_open`.
- Esquema: el card SRP lleva el coche (make/model/version/year/km/price/fuel/transmission/photo + id de comparación nativo + deep link); el vendedor (dealer por nombre) vive en el PDP JSON-LD. Portal nacional → sin province/address por coche.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Drenar el listado `/coches-ocasion/vehiculos-de-ocasion/` paginado (12/página). Por card: coche completo + id nativo + deep link.
2. Por coche, GET el PDP para leer `offers.seller.name` (el dealer).
3. Dedup por id de comparación nativo.
4. Cagear per-dealer-by-name: cada DEALER vendedor (por nombre) es una entidad `compraventa` nacional (geo NULL, portal nacional); el coche → vehicle owned por su dealer; arista platform_listing portal↔vehicle. Un coche cuyo PDP no expone seller se cagea bajo el bucket PORTAL (nunca se descarta).

## Receta / config
- Conector: `pipeline/platform/faciliteacoches_racc_wholesale.py` (miembro `racc`; `platform_cdp_code()`)
- Governor: host `cochesocasion.racc.es` → **STEALTH** (no en `_HOST_RATE_CLASSES`)
- Parser/identidad: dedup id-comparación nativo · Cage: plataforma-entidad + dealer-compraventa-by-name (nacional) + platform_listing + delta + recipe
- Naturaleza: portal VO del auto-club RACC; agrega feeds de inventario de dealers (`fotos.inventario.pro`).

## Validación (VAM)
- **verdict id=634 TRUSTWORTHY** · count=**96** aristas · `db_edges=96 == db_join_vehicles=96 == db_distinct_refs=96` (div 0.0), confirmado en DB viva esta sesión.
- Live actual: 96 aristas (**delta 0 — cuadrado al coche**).
- **Nota:** existe un verdict posterior id=635 (96, divergence 0.875) cuya divergencia alta proviene de un tercer path snapshot parcial; el verdict avalado es **id=634** (div 0.0, tres caminos DB iguales). El id=635 NO es el citado.

## CLI (reproducible)
```bash
python -m pipeline.platform.faciliteacoches_racc_wholesale --pages 6
python -m pipeline.platform.faciliteacoches_racc_wholesale --members racc --pages 10
```

## Trampas / notas
- Portal nacional: NO expone province/address por coche → el dealer se ancla nacional (province NULL).
- El vendedor NO está en el card; obliga a un GET PDP por coche para leer `offers.seller`.
- Conector conjunto con [Facilitea Coches](faciliteacoches.md): 788 (facilitea) + 96 (RACC) = 884 sobre los dos miembros.
