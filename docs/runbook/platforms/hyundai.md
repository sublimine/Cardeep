# hyundai — hyundai
**Estado:** ✅ VALIDADO (verdict id=569, count=1.994, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-C2SVJWB5` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `hyundai_vo`

## Data-layer (la fuente real)
- Endpoints (dos JSON internos de un storefront OpenCart):
  - Stock: `GET https://www.hyundai.es/seminuevos/index.php?route=product/vehiculo/listado` → `{vehiculos:[…]}` TODO el stock nacional FLAT en una respuesta (sin paginación). Headers: `X-Requested-With: XMLHttpRequest`, `Referer: https://www.hyundai.es/seminuevos/`.
  - Dealers: `GET https://www.hyundai.es/concesionarios/index.php?route=api/installation/seminuevos` → `{instalaciones:[…]}` (~155: nombre, phone, zipcode, zone, city, lat/lon, `concesionario_id`), fetch UNA vez.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET listado → coches con VIN real (`bastidor`) + `concesionario` (nombre) + `telefono`, SIN ubicación.
2. GET instalaciones → índice.
3. Join coche↔dealer por **teléfono** (primario exacto) → **nombre normalizado** (fallback).
4. Provincia = `installation.zipcode[:2]` (INE).

## Receta / config
- Conector: `pipeline/platform/oem_hyundai_wholesale.py`
- Governor: **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE` (WAF)
- Parser/identidad: VIN (`bastidor`) · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=569 TRUSTWORTHY** · count=**1.994** coches / 63 dealers · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_hyundai_wholesale
```

## Trampas / notas
- `vehiculo_id` ROTA por fetch (NO usar como dedup; usar VIN).
- Leer `lat`/`lon` correctos e ignorar `latitud`/`longitud` (intercambiados). Re-encode latin-1.
