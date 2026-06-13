# coches.net — coches-net
**Estado:** ✅ VALIDADO (verdict id=545, count=272.903, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

## Identidad
- cdp_code: `CDP-ES-00-TKRV45RP` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t1_soft` · family: `—` · data_surface: `internal_api`

## Data-layer (la fuente real)
- Endpoint: `POST https://web.gw.coches.net/search` (gateway JSON UNCAPPED; el cap ~155k es solo del UI frontend)
- Headers: `Content-Type: application/json`, `Accept: application/json, text/plain, */*`, `Origin: https://www.coches.net`, `Referer: https://www.coches.net/segunda-mano/`, `X-Schibsted-Tenant: coches`
- Tope/partición: `pagination.size` hard-cap 100; `meta.totalResults≈272.654`, `meta.totalPages=2727`. Sin facet ni province-loop necesario (surface uncapped).
- Esquema de petición (categoryId 2500 = turismos; `pagination` ANIDADO):
  ```json
  { "categoryId": 2500, "sortBy": "relevance", "sortOrder": "DESC",
    "pagination": { "page": 1, "size": 100 },
    "price": {"from":null,"to":null}, "year": {"from":null,"to":null}, "km": {"from":null,"to":null} }
  ```

## Micro-acciones (cómo se scrapea, paso a paso)
1. Sesión `curl_cffi`, `impersonate="chrome131"` (sin cookies, sin proxy).
2. `for page in 1..2727`: POST con el body, `pagination.size=100`.
3. Dedup en `items[].id` (deriva viva <1 %).
4. Re-walk en cadencia; el set es 100 % direccionable cada pasada. Páginas 1551–2727 (más allá del cap web UI) sirven filas reales por el gateway.
5. Segmentos VN/km0/renting: surface aparte (Imperva), `coches_net_segments.py`, referers `/nuevo/`, `/km-0/`, `/renting/`.

## Receta / config
- Conector wholesale VO: `pipeline/platform/coches_net_wholesale.py` · facet (rompe cap UI por province+price-band): `coches_net_facet.py` · segmentos: `coches_net_segments.py`
- Governor: host `web.gw.coches.net` → **JSON_API** (12 req/s, burst 24) en `_HOST_RATE_CLASSES` (governor.py L105)
- Parser/identidad: dedup `items[].id` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=545 TRUSTWORTHY** · count=**272.903** aristas · `db_edges=272.903 == db_join_vehicles=272.903 == db_distinct_refs=272.884` (refdiv 0.000070), `dup_veh=0`, **dealer=155.086 · particular=117.817**.
- Segmentos `platform_segment_slice` TRUSTWORTHY: **new=6.151 (id 584) · km0=3.107 (id 585) · renting=1.212 (id 587)**. Σ VN = 10.470, 100 % dealer-owned.
- Live actual: 274.138 aristas (delta +1.235, ingesta post-verdict).

## CLI (reproducible)
```bash
python -m pipeline.platform.coches_net_wholesale                 # VO backbone
python -m pipeline.platform.coches_net_facet --concurrency 8     # province+price-band (rompe cap UI)
python -m pipeline.platform.coches_net_facet --provinces 28,8,46 # subset
python -m pipeline.platform.coches_net_segments --segment new    # new | km0 | renting (o sin flag = los 3)
```

## Trampas / notas
- El cap solo es del UI frontend; el gateway sirve el 100 % del inventario.
- Los segmentos VN están tras Imperva → requieren `coches_net_segments.py` (escalada navegador camoufox).
- `platform.listing_counter` NULL: usar `count(platform_listing)`, no el counter.
