# autocasion — autocasion
**Estado:** ✅ VALIDADO (verdict id=549, count=15.765, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

> ⚠ **NÚMERO DEL RUNBOOK = 15.765 (verdict id=549).** La DB viva marca 107.612 aristas, pero ese
> crecimiento NO tiene verdict VAM persistido. Solo 15.765 está validado; los ~107k = **pendiente de
> re-VAM** (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)). El SCOREBOARD reclama 49.391 pero tampoco
> tiene un `verdict_id` que lo avale.

## Identidad
- cdp_code: `CDP-ES-00-QY06GW0B` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t1_soft` · family: `—` · data_surface: `graphql`

## Data-layer (la fuente real)
- Endpoints: `POST https://gql.autocasion.com/graphql/` (keys de partición + hidratación) + `GET https://www.autocasion.com/coches-segunda-mano/{make}-ocasion?page=N` (SSR, ~26 cards/page). Grupo Luike / Vocento.
- Tope/partición: GraphQL `search` y SSR comparten ES `from+size>10000 → 500` (sin scroll/searchAfter, introspección abierta lo confirma). El 100 % se alcanza por **partición de facet por path** (make, y make×province para la única make >10k).
- Sizing sin GraphQL: `<title>` del SSR facet = `N.NNN {Make} de segunda mano…`.
- Catálogo: `{brands(type:CAR){id name slug}}` → 184 makes (114 con stock); `{provinces{id name slug}}` → 52 (para MB).

## Micro-acciones (cómo se scrapea, paso a paso)
1. `brands(type:CAR)` → make slugs. Por make: GET facet, parsear total del `<title>`.
2. Si make <10k → drenar `?page=1..⌈N/26⌉` hasta page con 0 refs ("no hemos encontrado"). Solo **MERCEDES-BENZ (10.944)** excede 10k → split por province (las 50 <10k).
3. Refs: `href="(/coches-[^"]*-ref(\d+))"`. Dedup ref-ids entre páginas y slices.
4. Hidratar cada ref: GraphQL `ad(adId:{ID})` (coche) + PDP JSON-LD `offers.offeredBy=AutoDealer` (dealer).

## Receta / config
- Conector facet: `pipeline/platform/autocasion_facet.py` (`GQL_ENDPOINT`, `SSR_HOST`; segmentos `vo/vn/km0`) · wholesale: `autocasion_wholesale.py`
- Governor: **dos hosts** — `gql.autocasion.com` → **JSON_API** (12 req/s, governor.py L109); `www.autocasion.com` (SSR/PDP) → **STEALTH override 4.0 req/s, burst 8, min_spacing 0.25** (L347, subido 2.0→4.0 por evidencia CF-permisivo monitorizado).
- Parser/identidad: dedup `ref` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=549 TRUSTWORTHY** · count=**15.765** aristas · `db_edges=15.765 == db_distinct_refs=15.765 == db_join_vehicles=15.765` (div 0.0), `dup_veh=0`, **dealer=15.765 · particular=0**, refdiv 0.000000.
- Live actual: 107.612 aristas (delta **+91.847, sin re-VAM** → NO validado).

## CLI (reproducible)
```bash
python -m pipeline.platform.autocasion_facet --makes all                  # drena todas las makes
python -m pipeline.platform.autocasion_facet --make audi --make seat
python -m pipeline.platform.autocasion_facet --segment vo --concurrency 8
python -m pipeline.platform.autocasion_wholesale
```

## Trampas / notas
- **Acción de cierre:** re-correr el VAM (`record_count_verdict`) sobre la slice viva y persistir un verdict nuevo antes de subir el número del runbook.
- Usar facets **path-segment** (`/{make}-ocasion/{province}`), NO `?marca=&provincia=` (robots disallowa los query-param y los ignora).
