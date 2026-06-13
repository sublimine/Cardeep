# Ayvens Carmarket — ayvens-carmarket
**Estado:** ✅ VALIDADO (base del verdict id=543 `subastas`, count=27, 2026-06-13)  ·  **Grupo:** Subastas

## Identidad
- cdp_code: `CDP-ES-00-H1VCV020` · kind: `plataforma`/`role=platform` (lotes `kind=subasta`/`role=registry`, provincia NULL) · source_group: `official_registry` · defense_tier: `t0_open` · family: `ayvens_carmarket` · data_surface: `internal_api` · source_key: `group_subastas_wholesale`

## Data-layer (la fuente real)
- Endpoint: `POST https://api-carmarket.ayvens.com/graphql/saleevents` (SPA Angular sobre gateway GraphQL HotChocolate de primera parte). Plataforma de remarketing ALD/Ayvens.
- Headers client-side: `Content-Type: application/json`, `Origin/Referer https://carmarket.ayvens.com/`, `x-ald-subscription-key: 3b2cc62fd26c4e29a762db3de181266b`, `x-tenant: ald`, `x-country: es` (NO secretos de servidor; el SPA los embarca para el gateway público).
- Tope/partición: `LoadLots(order,take=200,skip,where)` con `where.state nin [closed,withdrawn,sold]` y `aggregates.count` = denominador (3977); paginar `skip += 200`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. `query SaleEvents` → catálogo de vendedores (id/country/name/reference/type/state/lotsCount).
2. `query LoadLots(take=200, skip)` con el filtro de estado; `aggregates.count` = denominador.
3. Paginar `skip += 200` hasta `count`.
4. Filtrar `saleEventCountry=='es'`; cada lote → vehículo OWNED por su `saleEventId`. Campos: id/make/model/version/mileage/fuelType/transmissionType/firstRegistrationDate/`fixedPrice`(solo tender)/mainImageUrl.

## Receta / config
- Conector: `pipeline/platform/group_subastas_wholesale.py`
- Governor: **JSON_API** (`api-carmarket.ayvens.com` en `_HOST_RATE_CLASSES`) · `defense_tier=t0_open`
- `surface_intent=graphql_gateway` · `price_gate=bid_login_gated` · Cage: plataforma + lotes (provincia NULL) + delta + recipe

## Validación (VAM)
- **base del verdict id=543 `subastas` TRUSTWORTHY** (group, div 0.0; el 543 certificó 27 del snapshot SSR previo). edges vivos = **3.977** (precio 0/3.977 no-NULL); 54 vendedores `subasta`.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_subastas_wholesale   # opcional --concurrency 1
```

## Trampas / notas
- Precio bid-gated → NULL por diseño (`fixedPrice` solo en lotes tender). El host HTML `carmarket.ayvens.com` ya NO es el data-path; el GraphQL `api-carmarket` lo es.
