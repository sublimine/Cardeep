# spoticar — spoticar
**Estado:** ✅ VALIDADO (verdict id=573, count=6.138, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-D6X2282Y` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `stellantis_vo`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.spoticar.es/api/vehicleoffers/paginate/search?page={N}` (API JSON interna de SPA Drupal sobre Elasticsearch). Stellantis ES (Peugeot, Citroën, DS, Opel, Fiat, Jeep, Alfa, Abarth) — la red OEM-VO más grande de ES.
- Headers (200 application/json): `X-Requested-With: XMLHttpRequest`, `Referer: https://www.spoticar.es/comprar-coches-de-ocasion`, UA Chrome. (curl pelado → 403 AkamaiGHost.)
- Tope/partición: FLAT, 12 coches/página, ~528 páginas. Opcional `GET /api/count-published-vo` → `{"count_vo_published":"6336"}` (denominador).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Opcional GET `/api/count-published-vo` (denominador).
2. Paginar `page=1..~528`, 12 coches/página, FLAT (sin cap de relevancia ni muro de profundidad).
3. Cada `hits[]._source` trae coche + dealer vía `field_pdv_*` (`field_pdv_geo_id`, `field_pdv_geolocation="lat,lng"`, `field_pdv_city`); atribución por-coche, NO PDP.
4. Provincia desde lat/lng (no hay ZIP). Re-encode latin-1.

## Receta / config
- Conector: `pipeline/platform/spoticar_wholesale.py`
- Governor: `www.spoticar.es` → **STEALTH** (no está en la tabla JSON_API)
- Parser/identidad: `hits[]._source` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=573 TRUSTWORTHY** · count=**6.138** coches / 136 dealers · `db_edges=db_join=6138`, `harvested=5888`, div 0.0407 (dentro de tolerancia).

## CLI (reproducible)
```bash
python -m pipeline.platform.spoticar_wholesale --pages 528
```

## Trampas / notas
- Akamai-fronted (curl pelado → 403); chrome131 TLS pasa. is_tier1=TRUE por ello.
- Sin ZIP en el listado → provincia desde lat/lng.
