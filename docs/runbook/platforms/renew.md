# renew — renew
**Estado:** ✅ VALIDADO (verdict id=423, count=918, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-DT59NK3D` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `renault_group`

## Data-layer (la fuente real)
- Endpoint: `GET https://es.renew.auto/vehiculos.data?<facets>&page=N` (catálogo facetado AEM+Elasticsearch tras un loader single-fetch React-Router). Portal del grupo Renault ES (Renault + Dacia + stock Refactory) — el PRIMER portal OEM-VO que abrió el grupo.
- La ruta pública `/vehiculos` acepta params ES crudos (`brand.label.raw=RENAULT`, …). Sin WAF a curl_cffi.
- Tope/partición: slice `content.contentZone.slice243v0.data`: `totalElements/totalPages` (denominador) + `data[]` (23 coches/página).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `.data` con `page=N`.
2. Leer `totalElements/totalPages` + `data[]`.
3. `page` es paginador estable (0 solape entre páginas).
4. Cada coche trae VIN real + `vehicleExhibitionSite` = dealer (dealerId, name, postalCode, locality, geolocalization); provincia = postalCode[:2].

## Receta / config
- Conector: `pipeline/platform/renew_wholesale.py`
- Governor: **JSON_API** (`es.renew.auto` registrado) · `defense_tier=t0_open`
- Parser/identidad: VIN · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=423 TRUSTWORTHY** · count=**918** coches / 115 dealers (slice probado; el portal declara ~5.739 nacionales) · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.renew_wholesale --pages 8
```

## Trampas / notas
- El portal declara ~5.739 nacionales; el verdict 423 avala el slice de 918 probado. Subir el número exige re-VAM del drain completo.
