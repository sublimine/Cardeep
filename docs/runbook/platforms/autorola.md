# Autorola — autorola
**Estado:** ✅ VALIDADO (dentro del verdict id=543 `subastas`, group count=27, 2026-06-13)  ·  **Grupo:** Subastas

## Identidad
- cdp_code: `CDP-ES-00-RJ109M0T` · kind: `plataforma`/`role=platform` · source_group: `official_registry` · defense_tier: `t1_soft` · family: `autorola` · data_surface: `internal_api` · source_key: `group_subastas_autorola`

## Data-layer (la fuente real)
- Endpoint: `GET https://old.autorola.es/rest/vehiclesearchenrollment/result?locale=es_ES&offset&limit[&auctionId]` (capa REST pública que el SPA pide tras un **JWT anónimo crudo** por petición; sin login). Subastas de remarketing Autorola Group; SPA Angular.
- Engine: **stealth browser JS-executing** que arranca el SPA y obtiene el JWT anónimo; la respuesta se captura e ingiere idempotente.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Stealth browser arranca el SPA → obtiene JWT anónimo.
2. Captura la respuesta REST: `groups[].vehicleDTOS[]` con `vehicleDTO{headline,details,countryCode,localizedMileage,presentationYear,pictureUrl}` + `auctionId/auctionTitle` + `firstReg`/`sortableMileage`.
3. Filtro ES: `vehicleDTO.countryCode=='ES'`.
4. Dedup en `enrollId`. `loginRequired=true`/`price=None` → precio NULL.

## Receta / config
- Conector: `scripts/cage_autorola_bca_subastas.py` (member `autorola`) · engine `stealth_browser_js_spa`
- Governor: **STEALTH** default 0.7 (`old.autorola.es` no en tabla) · `defense_tier=t1_soft` (SPA cookie-gated + JWT anón; sin WAF duro)
- `surface_intent=spa_rest_vehiclesearch` · `price_gate=bid_login_gated` · Cage: plataforma + lotes + delta + recipe

## Validación (VAM)
- **Dentro del verdict id=543 `subastas` TRUSTWORTHY** por su pathA. edges vivos = **1.056** (precio 0/1.056 no-NULL); 20 vendedores `subasta`.

## CLI (reproducible)
```bash
python scripts/cage_autorola_bca_subastas.py --autorola autorola_es_full.json   # slice capturado
```

## Trampas / notas
- JWT anónimo crudo por petición → exige stealth browser que arranque el SPA Angular.
- `loginRequired=true` → precio NULL. El doc viejo lo listaba "GATED sin data-layer"; quedó obsoleto.
