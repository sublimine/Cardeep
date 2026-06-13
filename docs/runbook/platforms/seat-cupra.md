# seat_cupra — seat-cupra
**Estado:** ✅ VALIDADO (verdict id=567, count=1.323, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-3N995HG6` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `seat_cupra_vo`

## Data-layer (la fuente real)
- Endpoint: `GET https://vtpapi.seat.com/restapi/v1/cuesgwb/search/car` (SPA Web-Components cuprawebfe → REST VTP, tenant `cuesgwb`). Solo CUPRA: la mitad SEAT ya está cubierta por Das WeltAuto (SEAT Ocasión redirige a dasweltauto.es), sin doble conteo.
- Headers (paginación va en HEADERS, no query): `x-pattern: cuprawebfe` (requerido por el edge gate Traefik), `x-page: N`, `x-page-items: 96` (default SPA 12; API honra ≥96), `x-sort: DATE_OFFER`, `x-sort-direction: DESC`. (urllib pelado → 403; chrome131 → 200.)
- Tope/partición: total en RESPONSE header `x-result-number: 1323` (no en el body); FLAT.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET con headers.
2. Total en RESPONSE header `x-result-number`.
3. Paginar `x-page=1..ceil(total/96)`, FLAT.
4. Cada coche trae `hypermediadealer.dealer{}` (key, city, name, zip, position lat/lng); provincia = `zip[:2]` con fallback lat/lng.
5. `deep_link` construido `https://www.cupra.com/es-es/localizador-stock/coche/{carid}`.

## Receta / config
- Conector: `pipeline/platform/oem_seat_cupra_wholesale.py`
- Governor: **STEALTH** · `defense_tier=t1_soft` · `is_tier1=TRUE`
- Parser/identidad: `carid` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=567 TRUSTWORTHY** · count=**1.323** coches / 87 dealers · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_seat_cupra_wholesale --pages 14
```

## Trampas / notas
- La paginación va en HEADERS (`x-page`, `x-page-items`), no en query-params. UTF-8 limpio (sin re-encode).
- Solo CUPRA aquí; SEAT VO == Das WeltAuto (evita doble conteo).
