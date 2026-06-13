# mini — mini
**Estado:** ✅ VALIDADO (verdict id=527, count=678, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-EV9ECTV7` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `bmw_group_vo` · data_surface: `json_ld`

## Data-layer (la fuente real)
- Endpoints: `GET https://www.mininext.es/sitemap.xml` → roster (~47 dealers) + `GET https://www.mininext.es/concesionarios/{prov}/{dealer}?pagina=N` (**MINI: SIN slash final, 404 con slash**) → 12 cards/página. Listado SSR Motorflash (mismo backend que BMW Premium Selection).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Sitemap → roster de dealers.
2. Por dealer, `?pagina=N` hasta agotar (igual que BMW).
3. Por card: coche + `concesionario`/`provincia`. VIN embebido en card, NO PDP.
4. Provincia desde el slug de la URL.

## Receta / config
- Conector compartido: `pipeline/platform/oem_bmw_mini_wholesale.py` (`--brand mini`)
- Governor: **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE`
- Parser/identidad: `anuncio_id`/VIN · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=527 TRUSTWORTHY** · count=**678** coches / 83 dealers · div 0.0059.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_bmw_mini_wholesale --brand mini
```

## Trampas / notas
- MINI: **SIN slash final** en la URL del dealer (404 con slash). BMW es lo contrario.
- Re-encode latin-1 + vocabulario fijo fuel/gearbox.
