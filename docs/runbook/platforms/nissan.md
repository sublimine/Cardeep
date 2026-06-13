# nissan — nissan
**Estado:** ✅ VALIDADO (verdict id=566, count=1.622, 2026-06-13)  ·  **Grupo:** OEM-VO

## Identidad
- cdp_code: `CDP-ES-00-TDWVVTAF` · kind: `oem_vo_portal` · source_group: `oem_vo_portal` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `nissan_intelligent_choice`

## Data-layer (la fuente real)
- Next.js SSR sobre AWS AppSync GraphQL. Slice elegido del frente nissan/mazda/honda (Mazda amurallado, Honda sin data-layer — ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).
- Mint de idToken Cognito (público, sin auth): `GET https://apigateway-eu-prod.nissanpace.com/euw1nisprod/public-access-token` (`Origin: https://www.ocasion.nissan.es`) → `{"idToken":"<JWT ~1169 chars>"}`. **Refrescar por run.**
- Inventario: `POST https://gq-eu-prod.nissanpace.com/graphql` (`GetUsedCarsInventoryData`), `Authorization: <idToken>` (bare o `Bearer`).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Mint idToken Cognito (refrescar por run).
2. Paginar inventario por GraphQL `GetUsedCarsInventoryData`.
3. Dealer-locator query resuelve cada `dealerId` a postCode/lat-lng/city.
4. Provincia = postCode[:2].

## Receta / config
- Conector: `pipeline/platform/oem_nissan_mazda_honda_wholesale.py` (cubre SOLO la slice Nissan)
- Governor: **STEALTH** · `defense_tier=t0_open` · `is_tier1=FALSE`
- Parser/identidad: `dealerId` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=566 TRUSTWORTHY** · count=**1.622** coches / 41 dealers · div 0.0401.

## CLI (reproducible)
```bash
python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104
```

## Trampas / notas
- **NO usar `graphqlkey`/`x-api-key`** (→ Unauthorized); solo `Authorization: <idToken>`.
- El idToken Cognito caduca → refrescar cada run.
