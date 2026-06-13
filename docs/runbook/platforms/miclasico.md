# Miclasico — miclasico

**Estado:** ✅ VALIDADO (verdict id=637, count=959, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace (clásicos MERGED como `compraventa`)

## Identidad
- cdp_code: `CDP-ES-00-TSJFC4J2` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `—` · data_surface: `sitemap` (SSR HTML, DJ-Classifieds/Joomla)

## Data-layer (la fuente real)
- Endpoint listado: `GET https://www.miclasico.com/anuncios?se=1,p1&se_cats=1,p1&start=N` (9 cards/página, `start` en pasos de 9; el último start poblado ~981 acota el drenaje a ~990 coches).
- Endpoint PDP: `GET https://www.miclasico.com/anuncios/ad/{make}/{slug}-{id}` (geo-anclaje por coche).
- Auth/headers: curl_cffi `chrome131` impersonate, sin WAF reto → `t0_open`.
- Esquema: HTML plano DJ-Classifieds (sin JSON único). El card da id, make (slug del href), título, precio y (cuando lo lleva) año + transmisión. El PDP da la LOCALIZACIÓN (`Ubicación` panel → ciudad/provincia) + coords ({lat,lng} en el JSON `uk-map`) + galería.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Drenar el listado `start=0,9,18,...` hasta el último start poblado (~981). Por card: id, make, título, precio, año/transmisión.
2. Por coche, GET el PDP SOLO para geo-anclar la provincia (el card no lleva location) y elegir la primera foto de galería.
3. Dedup por id nativo del anuncio.
4. Cagear cada coche bajo un bucket sintético `compraventa` PER PROVINCIA (geo-resuelto del PDP: nombre primero, luego lat/lng → provincia); location sin anclar → bucket nacional `00`.

## Receta / config
- Conector: `pipeline/platform/miclasico_wholesale.py` (`mc_platform_cdp_code()`, surface `sitemap`/SSR HTML dos etapas)
- Governor: host `www.miclasico.com` → **STEALTH** (no en `_HOST_RATE_CLASSES`); ambas etapas (listado + PDP) pasan por el bucket per-host.
- Parser/identidad: dedup `id` nativo · Cage: plataforma-entidad + bucket-compraventa-por-provincia + platform_listing + delta + recipe
- **Decisión de owner (2026-06-13):** clásicos MERGEADOS como `kind='compraventa'`, sin tipo especial. Miclasico NO expone id estable de vendedor (el bloque 'Anunciante' es contacto free-text), así que NO se fabrica identidad: bucket sintético per-provincia (patrón coches.net).

## Validación (VAM)
- **verdict id=637 TRUSTWORTHY** · count=**959** aristas · `db_edges=959 == db_join_vehicles=959 == db_distinct_refs=959` (div 0.0), confirmado en DB viva esta sesión.
- Live actual: 959 aristas (**delta 0 — cuadrado al coche**).

## CLI (reproducible)
```bash
python -m pipeline.platform.miclasico_wholesale --pages 110
python -m pipeline.platform.miclasico_wholesale --pages 110 --concurrency 4 --start-page 0
```

## Trampas / notas
- El listado pagina por `start=N` (paso 9), NO por `page=N`. El último start poblado acota el boundary.
- El card NO lleva location; obliga a un GET PDP por coche para geo-anclar (dos etapas).
- DJ-Classifieds/Joomla SSR sin payload JSON → parsing de HTML UIkit + islas Vue.
