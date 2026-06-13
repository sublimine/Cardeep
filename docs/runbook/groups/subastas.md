# GRUPO · Subastas (`kind='subasta'`, `source_group='official_registry'`) — veredicto 543 TRUSTWORTHY

> Subasta / remarketing B2B; el vendedor es el evento de venta. No hay enum `auction` en
> `source_group`: se usa el más cercano `official_registry`, llevando la semántica en
> `kind='subasta'` y `family ∈ {ayvens_carmarket, bca_europe, autorola}`. Plataformas `role='platform'`;
> lotes `kind='subasta'`/`role='registry'`.

## Veredicto

| id | subject_key | primary_value | divergencia | verdict | created_at |
|---:|---|---:|---:|---|---|
| **543** | `subastas` | **27** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |

Caminos: pathA `entity.kind=subasta` = 27 == pathB `entity_source source_key ~ 'subastas'` = 27.

> **Desfase veredicto↔DB viva (declarado).** El veredicto se selló a 00:37Z (27, snapshot SSR previo).
> Los conectores SPA/browser posteriores ampliaron a **6.785** aristas vivas. El runbook reporta 27
> como validación formal; el conteo vivo (6.785) es cross-check `[VERIFICADO]`. Re-emisión VAM:
> pendiente (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).

## El precio-gate honesto (la distinción central)

`[VERIFICADO]` en DB viva: los 6.785 lotes de subasta tienen `vehicle.price = NULL` (0/6.785) y
`platform_listing.platform_price = NULL` (0/6.785). **El precio de subasta es NULL por diseño, no
por fallo:** es de puja con login (`Ayvens fixedPrice` solo en tender, `BCA CanViewPricing=false`,
`Autorola loginRequired=true`). El vehículo (make/model/año/km/foto/ubicación) es público y se cagea;
el precio jamás se inventa. El conector lo llama `price_gate='bid_login_gated'`.

## Miembros validados (3)

| Plataforma | cdp_code | family | edges vivos | vendedores `subasta` | Ficha |
|---|---|---|---:|---:|---|
| **Ayvens Carmarket** (base del 543) | CDP-ES-00-H1VCV020 | ayvens_carmarket | 3.977 | 54 | [ayvens-carmarket](../platforms/ayvens-carmarket.md) |
| **BCA España** | CDP-ES-00-WYJKTP6S | bca_europe | 1.752 | 20 | [bca-espana](../platforms/bca-espana.md) |
| **Autorola** | CDP-ES-00-RJ109M0T | autorola | 1.056 | 20 | [autorola](../platforms/autorola.md) |

DB viva (cross-check): 3 plataformas + 94 vendedores `kind=subasta`; owned=edges=union=**6.785**,
div 0.0. Ayvens drena por GraphQL gateway (curl_cffi, t0_open); BCA y Autorola por **stealth browser
JS-executing** (Playwright/camoufox) que pasa el reto Cloudflare / arranca el SPA Angular — un
`curl_cffi` plano no los alcanza.

## Miembro B2B-auction añadido (ola new-channels)

| Plataforma | cdp_code | verdict id | count | tipo | precio | Ficha |
|---|---|---:|---:|---|---|---|
| **LocalizaVO** (`localizavo.es`) | CDP-ES-00-HFR3D62Y | **624** | 318 | `platform` | NULL (bid-login-gated) | [localizavo](../platforms/localizavo.md) |

> LocalizaVO es una subasta B2B FREE-PUBLIC: el catálogo per-lote es SSR HTML visible al cliente
> anónimo (`&nReg=0` = "Todos"), solo el precio se gatea (registro profesional) → `price=NULL`
> honesto, igual que Ayvens/BCA/Autorola. **verdict id=624 TRUSTWORTHY**, count=318, los 3 caminos DB
> concuerdan al dígito (`[VERIFICADO]` esta sesión, delta 0). **Gated en la misma censada
> (fuera del runbook):** CarCollect (`carcollect.com`, B2B-only, fee 82€/coche, todo `/api/*`→login) y
> Manheim España (login de comprador, sin credenciales) → [NOT-VALIDATED.md](../NOT-VALIDATED.md) §5.3.

> **Nota Autorola/BCA.** El doc viejo los listaba "GATED, sin capa de datos pública". Ese veredicto
> quedó obsoleto: conducidos por stealth browser, ambos exponen el stock per-lote ES sin login (el
> precio sigue gateado → NULL). El código (`scripts/cage_autorola_bca_subastas.py`) y la DB viva
> mandan sobre el `.md` aspiracional.

**Fuera del runbook:** Allane (Sixt Leasing, DE-céntrico), Aucto (`aucto.es`, connection refused).
