# wallapop — wallapop
**Estado:** ✅ VALIDADO (verdict id=592, count=565.128, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

## Identidad
- cdp_code: `CDP-ES-00-EMRH0TWQ` · kind: `plataforma` · source_group: `marketplace_generalist` · defense_tier: `t1_soft` · family: `—` · data_surface: `app_api`

## Data-layer (la fuente real)
- Endpoint: `GET https://api.wallapop.com/api/v3/search/section?category_id=100&order_by=newest&section_type=organic_search_results`
- Headers: `accept: application/json, text/plain, */*`, `deviceos: 0`, `x-deviceid: <uuid-v4>`, `referer: https://es.wallapop.com/`, `origin: https://es.wallapop.com`
- Tope/partición: **la perilla de uncap es `order_by`**. `most_relevance`→53.467 (CAPPED), `closest`→59.324 (CAPPED), **`newest`/`price_low_to_high`/`price_high_to_low`→651.340 (UNCAPPED = catálogo completo)**.
- Cursor: JWT opaco `meta.next_page`, replayado como único param. 40 items/página fijo. Oráculo: el JWT lleva `pointers.ORGANIC.remaining_documents` (decrementa exacto → garantía de enumeración).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Primera página con `order_by=newest`, sin keywords (keywords scopea a query).
2. Walk `?next_page=<jwt>` hasta `meta.next_page` ausente o `remaining_documents→0`.
3. Dedup en `id`. Dealer attribution: `GET /api/v3/users/{user_id}` (`type` = `professional`|`normal`).
4. Estrategia híbrida: flat-cursor `newest` SATURA primero (`wholesale`), luego `wallapop_facet.py` particiona por seller_type × price para la cola profunda.

## Receta / config
- Conector wholesale (flat-cursor): `pipeline/platform/wallapop_wholesale.py` (`SEARCH_ENDPOINT = https://api.wallapop.com/api/v3/search/section`, L104) · facet: `wallapop_facet.py`
- Governor: host `api.wallapop.com` → **JSON_API** (12 req/s, burst 24) en `_HOST_RATE_CLASSES` (governor.py L107)
- Parser/identidad: dedup `id` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=592 TRUSTWORTHY** · count=**565.128** aristas · `db_edges=565.128 == db_join_vehicles=565.128 == db_distinct_refs=565.052` (divergence 0.00013). Split (ola anterior): dealer 3.932 cv · particular 160.847.
- Live actual: 575.353 aristas (delta +10.225, ingesta post-verdict).
- Denominador del oráculo ≈651.340; el resto a 651k es cola profunda (G1, ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).

## CLI (reproducible)
```bash
python -m pipeline.platform.wallapop_wholesale --target 651000 --concurrency 6
python -m pipeline.platform.wallapop_facet --seller-types professional,private --concurrency 6
python -m pipeline.platform.wallapop_facet --cell-max 10000 --max-pages 250
```

## Trampas / notas
- El "cap" no era el endpoint, era el ranker de relevancia: `order_by=newest` lo levanta.
- **Trampa de encoding:** `type_attributes.engine` latin-1 mojibake → re-encode.
- La cola profunda a 651k exige paginación facet/cursor aún no completada (band-boundary collapse por dedup).
