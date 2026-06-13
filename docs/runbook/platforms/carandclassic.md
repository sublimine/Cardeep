# Car & Classic — carandclassic

**Estado:** ✅ VALIDADO (verdict id=630, count=585, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace (clásicos MERGED como `compraventa`)

## Identidad
- cdp_code: `CDP-ES-00-WS3ZTNX7` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t1_soft` · is_tier1: `TRUE` · family: `—` · data_surface: `next_data`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.carandclassic.com/es/buscar?vehicle_type=cars&country=ES&page=N`
- Auth/headers: curl_cffi `chrome131` impersonate (sin proxy, sin browser, sin cookie warm-up). Cloudflare-walled pero sirve limpio al fingerprint Chrome → defense_tier `t1_soft`.
- Tope/partición: paginación limpia `?page=N`; `searchResults.pagination.total` declara el count. La superficie ES (`?vehicle_type=cars&country=ES`) = ~585-618 coches clásicos ubicados en España, 59-60/página, ~11 páginas.
- Esquema de respuesta: payload Inertia.js embebido en el SSR HTML — `<script data-page="app" type="application/json">{"component":"search/index/Page","props":{...,"searchResults":{"data":[<car>...],"pagination":{...}}}}</script>`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `/es/buscar?vehicle_type=cars&country=ES&page=1`; parsear el `data-page` JSON; leer `searchResults.pagination.total`.
2. Drenar `?page=1..⌈total/per_page⌉`; cada `searchResults.data[]` es un registro estructurado por coche (id, slug, url, title, price{value(cents),currency}, make, year, attributes{mileage,fuelType,transmissionType,engineSize,gears,colour}, location{countryCode,region,town}, type, isSold).
3. Dedup por id nativo. El tail `-{id}` del deep-link es el `listing_ref`.
4. Cagear cada coche bajo un bucket sintético `compraventa` PER PROVINCIA (geo-resuelto de `location.town`); el town sin geo cae al bucket nacional `00` (ningún coche se descarta).

## Receta / config
- Conector: `pipeline/platform/carandclassic_wholesale.py` (`cc_platform_cdp_code()`, surface `next_data`/Inertia.js)
- Governor: host `www.carandclassic.com` → **STEALTH** (no en `_HOST_RATE_CLASSES`, bucket por host)
- Parser/identidad: dedup `id` nativo · Cage: plataforma-entidad + bucket-compraventa-por-provincia + platform_listing + delta + recipe
- **Decisión de owner (2026-06-13):** los marketplaces de clásicos/coleccionismo entran EN SCOPE y se MERGEAN como `kind='compraventa'` — sin tipo especial, sin nuevo source_group. Car & Classic anonimiza el dealer vendedor en toda superficie (`listing.seller` = todo null), así que NO se fabrica identidad de dealer: bucket sintético per-provincia (patrón coches.net para vendedores anónimos).

## Validación (VAM)
- **verdict id=630 TRUSTWORTHY** · count=**585** aristas · `db_edges=585 == db_join_vehicles=585 == db_distinct_refs=585` (div 0.0), confirmado en DB viva esta sesión. Re-run idempotente (verdict previo id=629 = 585, mismo valor).
- Live actual: 585 aristas (**delta 0 — cuadrado al coche**).

## CLI (reproducible)
```bash
python -m pipeline.platform.carandclassic_wholesale --pages 11
python -m pipeline.platform.carandclassic_wholesale --pages 11 --concurrency 4 --start-page 1
```

## Trampas / notas
- La superficie ES se filtra por `country=ES` en `/es/buscar`; el coche se ubica por `location.town` (nivel municipio), no por dealer.
- El dealer está anonimizado en TODA superficie accesible (search + PDP `listing.seller` null incluso para dealers) → bucket per-provincia, nunca id de dealer fabricado.
- Cloudflare-walled (is_tier1=TRUE) pero `t1_soft`: sirve a Chrome TLS fingerprint sin reto.
