# mercedes_benz — mercedes-benz
**Estado:** ✅ VALIDADO (verdict id=515, count=4.792, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-A57R0YK8` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `mercedes_benz_vo`

## Data-layer (la fuente real)
- Endpoint: `POST https://ocasion.mercedes-benz.es/ajxvl` (listado SSR cuya paginación es un endpoint AJAX). Perfil de red invertido: ancha y poco profunda (4.792 coches / 4.749 dealers, ~1 coche/dealer).
- Headers/body: `Content-Type: application/x-www-form-urlencoded`, `X-Requested-With: XMLHttpRequest`, Origin/Referer `https://ocasion.mercedes-benz.es/vehicles?referrer=vehiclesearch&language=es-ES`; FormData `{type:'vehiclelist', q, page:N, area:1}`. Setea cookie `UCSSID` (warm-up por sesión).
- Tope/partición: FLAT, 12 coches/página, 401 páginas (401 = 4 coches cola; 400*12+4 = 4804 = `data.count`).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `/vehicles` una vez (cookie + chrome del pager).
2. `POST /ajxvl` `page=1..401`, 12 coches/página de markup HTML autocontenido.
3. Por tarjeta: coche + dealer (`result-box-location-item` nombre + `"<CP> <ciudad>"` + `dealerCode` = prefijo de `"<dealerCode>-<carCode>"`).
4. Provincia = `CP[:2]` (INE).

## Receta / config
- Conector: `pipeline/platform/oem_mercedes_benz_wholesale.py`
- Governor: **STEALTH** · `defense_tier=t0_open` (urllib pelado da 200; sin WAF)
- Parser/identidad: `dealerCode`+`carCode` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=515 TRUSTWORTHY** · count=**4.792** coches / 4.749 dealers · div 0.0.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_mercedes_benz_wholesale --pages 401
```

## Trampas / notas
- Decode `utf-8-sig` (BOM); UTF-8 limpio, sin re-encode latin-1.
