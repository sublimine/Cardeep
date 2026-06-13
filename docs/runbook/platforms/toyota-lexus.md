# toyota_lexus — toyota-lexus
**Estado:** ✅ VALIDADO (verdict id=572, count=3.834, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-GNAJ5S16` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `toyota_lexus_vo`

## Data-layer (la fuente real)
- Endpoint: `POST https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es?brand={toyota|lexus}` (Toyota-Europe USC = Used Stock Cars Web Components, una API JSON). Dos redes OEM-VO (Toyota Ocasión/Plus + Lexus Select) sobre UN backend.
- Body: `{filterContext:"used", distributorCode:"9424M", offset, ...}` (Lexus añade `filters:[{usedCarBrand:["22"]}]`). CloudFront (`x-amz-cf-id`), SIN WAF bot → 200 incluso a curl.
- Tope/partición: `{totalResultCount, totalPageCount, results:[…]}`; `offset` es cursor de FILA, FLAT.

## Micro-acciones (cómo se scrapea, paso a paso)
1. POST por marca (mismo `distributorCode` ES `9424M`).
2. Caminar `offset=0..totalResultCount` por `resultCount`, FLAT.
3. Cada `results[]` trae coche + `dealer{}` embebido (id, address+zip, lat/lon, phone).
4. Provincia = `dealer.address.zip[:2]` (INE) con fallback geocode. Re-encode latin-1.

## Receta / config
- Conector: `pipeline/platform/oem_toyota_lexus_wholesale.py`
- Governor: **STEALTH** · `defense_tier=t0_open`
- Parser/identidad: `results[]` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=572 TRUSTWORTHY** · count=**3.834** coches / 129 dealers · div 0.0086.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_toyota_lexus_wholesale --pages 80
```

## Trampas / notas
- Un solo backend sirve ambas marcas; el `brand` query-param las separa.
