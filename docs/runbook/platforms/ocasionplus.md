# OcasionPlus — ocasionplus
**Estado:** ✅ VALIDADO (cubierto por verdict id=541 `chains`, group count=37.319, 2026-06-13)  ·  **Grupo:** Cadenas VO

## Identidad
- cdp_code: `CDP-ES-00-SWN09H0C` · kind: `cadena` · source_group: `chain` · defense_tier: `t0_open` · data_surface: `json_ld` · source_key: `group_vo_chains_ocasionplus`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.ocasionplus.com/coches-segunda-mano?page=N` (cadena VO Next.js; capa de datos = schema.org JSON-LD `ItemList` embebido en SSR). Headers: `Referer: https://www.ocasionplus.com/`, `chrome131`.
- Tope/partición: caminar `?page=N` server-side (≈703 págs). `?pagina=N` se ignora (devuelve page 1).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET page=1.
2. Parsear el bloque JSON-LD: `Product.offers (AggregateOffer).offerCount` = stock total; `ItemList.itemListElement[].@type=Vehicle` = 20 coches/página.
3. Caminar `?page=N` server-side.
4. Per-branch no está en el listado → la cadena es el punto de venta (`owner_model=chain`).

## Receta / config
- Conector: `pipeline/platform/group_vo_chains_wholesale.py` (member `ocasionplus`)
- Governor: **STEALTH** override 1.0/3/0.8 (governor.py:364) · `defense_tier=t0_open`
- Owner model: `chain` · `surface_intent=ssr_jsonld_itemlist` · Cage: cadena + delta + recipe

## Validación (VAM)
- **Cubierto por verdict id=541 `chains` TRUSTWORTHY** (group, div 0.0). edges vivos = **13.445**.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_vo_chains_wholesale --members ocasionplus --pages 1000
```

## Trampas / notas
- `?pagina=N` se ignora; usar `?page=N`. Atribución chain-as-owner (la cadena posee su stock).
