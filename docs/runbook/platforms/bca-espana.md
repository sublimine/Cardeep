# BCA España — bca-espana
**Estado:** ✅ VALIDADO (dentro del verdict id=543 `subastas`, group count=27, 2026-06-13)  ·  **Grupo:** Subastas

## Identidad
- cdp_code: `CDP-ES-00-WYJKTP6S` · kind: `plataforma`/`role=platform` · source_group: `official_registry` · defense_tier: `t2_js_challenge` · family: `bca_europe` · data_surface: `internal_api` · source_key: `group_subastas_bca`

## Data-layer (la fuente real)
- Endpoint: `POST https://es.bca-europe.com/buyer/facetedsearch/GetViewModel?q=&bq=salecountry_exact:ES` (faceted-search ViewModel). British Car Auctions España, remarketing VO B2B; SPA tras un reto JS de Cloudflare.
- Engine: **stealth browser JS-executing** (Playwright/camoufox) que pasa el reto Cloudflare (un `curl_cffi` plano recibe 403 "Just a moment..."); la respuesta JSON (`VehicleResults[]`, `TotalVehicles`, `IsUserAnonymous=true`, `CanViewPricing=false`) se captura de la red del browser.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Stealth browser arranca, pasa el reto Cloudflare.
2. Captura la respuesta JSON del ViewModel de la red.
3. Filtro de coche: `VehicleType ∈ {car, crosscountryvehicle}` (descarta moto/van).
4. Vendedor = `SaleId/SaleName`. Ingesta idempotente.

## Receta / config
- Conector: `scripts/cage_autorola_bca_subastas.py` (member `bca`) · engine `stealth_browser_js_spa`
- Governor: **STEALTH** default 0.7 (`es.bca-europe.com` no en tabla) · `defense_tier=t2_js_challenge`
- `surface_intent=spa_facetedsearch_viewmodel` · `price_gate=bid_login_gated` · Cage: plataforma + lotes + delta + recipe

## Validación (VAM)
- **Dentro del verdict id=543 `subastas` TRUSTWORTHY** por su pathA (`entity.kind=subasta`). edges vivos = **1.752** (precio 0/1.752 no-NULL); 20 vendedores `subasta`.

## CLI (reproducible)
```bash
python scripts/cage_autorola_bca_subastas.py --bca bca_es_full.json   # slice capturado del browser vivo
```

## Trampas / notas
- `curl_cffi` plano recibe 403 "Just a moment..." → exige stealth browser JS-executing.
- `CanViewPricing=false` → precio NULL por diseño. El doc viejo lo listaba "GATED sin data-layer"; quedó obsoleto.
