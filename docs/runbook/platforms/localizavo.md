# LocalizaVO — localizavo

**Estado:** ✅ VALIDADO (verdict id=624, count=318, 2026-06-13)  ·  **Grupo:** Subastas (B2B auction, lotes precio-gateado)

## Identidad
- cdp_code: `CDP-ES-00-HFR3D62Y` · kind: `plataforma` · source_group: `official_registry` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `localizavo` · data_surface: `next_data` (SSR ASP.NET)

## Data-layer (la fuente real)
- Endpoint eventos: `GET https://www.localizavo.es/` y `/subastas_listado.aspx` → links públicos de subasta `subastas?idSubasta=<id>`.
- Endpoint lotes: `GET https://www.localizavo.es/subastas?idSubasta={sid}&nReg=0` (`&nReg=0` = "Todos" drena el evento en un shot; alternativa `&numPagina=N`).
- Auth/headers: GET anónimo con `chrome131`, SIN login. El catálogo per-lote es SSR HTML totalmente visible al cliente anónimo; solo el PRECIO se retiene ("Precio visible solo para Usuarios Registrados") → bid-gated, `price=NULL` honesto.
- Esquema: card por lote — Ref, Matriculación, Estado, empresa consignataria, make/model/version, fuel, CV, km, foto, fecha de fin.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET la home + `/subastas_listado.aspx`; extraer los `idSubasta` de los eventos vivos.
2. Por evento: GET `subastas?idSubasta={sid}&nReg=0` (drena todos los lotes del evento de una vez).
3. Parsear cada card de lote (Ref nativo = `listing_ref`; precio NULL por bid-gate).
4. Cagear: la plataforma LocalizaVO es la entidad; cada EVENTO de venta es una entidad `subasta`/`role='registry'` nacional (province NULL); cada lote → vehicle owned por su evento; arista platform_listing portal↔vehicle.

## Receta / config
- Conector: `pipeline/platform/localizavo_wholesale.py` (`localizavo_platform_cdp_code()`, `localizavo_sale_cdp_code()`)
- Governor: host `www.localizavo.es` → **STEALTH** (no en `_HOST_RATE_CLASSES`)
- Parser/identidad: dedup `Ref` nativo · Cage: plataforma-entidad + entidad-evento-subasta (nacional) + platform_listing + delta + recipe · `price_gate='bid_login_gated'`

## Validación (VAM)
- **verdict id=624 TRUSTWORTHY** · count=**318** · `subject_type=platform` · `tolerance=0.10` (la metodología del conector para el catálogo público completo) · confirmado en DB viva esta sesión: `db_edges=318 == db_join_vehicles=318 == db_distinct_refs=318` (div 0.0). Re-run idempotente (verdict previo id=623 = 318, mismo valor).
- Live actual: 318 aristas (**delta 0 — cuadrado al coche**).

## CLI (reproducible)
```bash
python -m pipeline.platform.localizavo_wholesale
python -m pipeline.platform.localizavo_wholesale --concurrency 4
```

## Trampas / notas
- El precio de subasta es **NULL por diseño** (bid-login-gated), nunca inventado — igual que Ayvens/BCA/Autorola.
- El registro profesional gatea solo el bid/compra; el CATÁLOGO per-lote es público anónimo vía SSR.
- **CarCollect (carcollect.com)** y **Manheim España (manheim.es)** se probaron en la misma censada y son GATED (sin capa de datos pública anónima) → ver [NOT-VALIDATED.md](../NOT-VALIDATED.md). Ninguno escribió entidad.
