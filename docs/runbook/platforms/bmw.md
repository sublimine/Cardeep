# bmw — bmw
**Estado:** ✅ VALIDADO (verdict id=524, count=2.848, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-ZXZD056M` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `bmw_group_vo` · data_surface: `json_ld`

## Data-layer (la fuente real)
- Endpoints: `GET https://www.bmwpremiumselection.es/sitemap.xml` → roster (`/concesionarios/{prov}/{dealer}`) + `GET https://www.bmwpremiumselection.es/concesionarios/{prov}/{dealer}/?pagina=N` (**BMW requiere slash final**) → 12 car-cards/página, FLAT. Listado SSR Motorflash (mismo backend que MINI NEXT).
- Tope/partición: barrido por dealer; Σ sobre el roster = stock nacional.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Sitemap → lista de dealers.
2. Por dealer, `?pagina=N` hasta que `id_total_resultados` se agote.
3. Cada coche es una CARD de `<input>` ocultos: `anuncio_id, precio, marcaVehiculo, modeloVehiculo, kilometros, bastidorVehiculo`=VIN, `fechamatriculacion`, `img` — VIN embebido, NO PDP.
4. Provincia desde el slug de la URL `/{province-slug}/` vía `GeoResolver.province_code`.

## Receta / config
- Conector compartido: `pipeline/platform/oem_bmw_mini_wholesale.py` (`--brand bmw`)
- Governor: **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE` (WAF/CDN)
- Parser/identidad: `anuncio_id`/VIN · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=524 TRUSTWORTHY** · count=**2.848** coches / 51 dealers · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_bmw_mini_wholesale --brand bmw
python -m pipeline.platform.oem_bmw_mini_wholesale --brand both   # ambas marcas
```

## Trampas / notas
- BMW requiere **slash final** en la URL del dealer (MINI es lo contrario, 404 con slash).
- Re-encode latin-1 + vocabulario fijo para fuel/gearbox con U+FFFD de origen.
