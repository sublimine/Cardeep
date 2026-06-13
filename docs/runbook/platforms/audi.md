# audi — audi
**Estado:** ✅ VALIDADO (verdict id=482, count=3.798, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-NP3AWN4X` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `audi_vo`

## Data-layer (la fuente real)
- Endpoint: `GET https://scs.audi.de/api/v2/search/filter/esuc/es?from={N}&size=96&sort=prices.retail:asc` (`esuc` = ES Used Cars). SPA OneAudi/NEMO (VTP) → API JSON global Stock Car Search (SCS). Portal mono-marca de Audi ES (separado de Das WeltAuto del VW Group).
- Headers (200): **`token: FJ54W6H`** (api-key PÚBLICA estática del `envConfig.scs.apiKey`; 401 sin ella — NO es credencial), `Referer: https://www.audi.es/`, `Origin`. Sin WAF ni cookie.
- Tope/partición: `{totalCount:3798, vehicleBasic:[…]}`; paginar `from=0..totalCount` por `size` (96 honrado), FLAT; `from>=totalCount` → 400 (frontera limpia).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET con `token`.
2. Paginar `from=0..totalCount` por `size`.
3. Cada `vehicleBasic` trae coche + `dealer{}` (id, city, street, `zipCode`, geoLocation).
4. Provincia = `zipCode[:2]` (rango 01..52) con fallback geocode. Re-encode latin-1.

## Receta / config
- Conector: `pipeline/platform/oem_audi_wholesale.py`
- Governor: **JSON_API** (`scs.audi.de` registrado) · `defense_tier=t0_open`
- Parser/identidad: `vehicleBasic` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=482 TRUSTWORTHY** · count=**3.798** coches / 56 dealers · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_audi_wholesale --pages 40
```

## Trampas / notas
- El `token: FJ54W6H` es público estático del `envConfig`, no una credencial — 401 sin él.
