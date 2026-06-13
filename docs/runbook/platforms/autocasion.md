# autocasion — autocasion
**Estado:** ✅ VALIDADO (verdict id=638, count=111.844, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

> ✅ **RE-VAM CERRADO (2026-06-13).** El delta vivo se re-derivó por 3 caminos ortogonales que
> concuerdan al dígito (`db_edges=111.844 == db_join_vehicles=111.844 == db_distinct_refs=111.844`,
> div 0.0) y se persistió **verdict id=638 TRUSTWORTHY (`platform_slice`)**. El número del runbook
> sube de 15.765 (id=549, slice sellada vieja) a **111.844 (id=638)**. El caveat "pendiente de re-VAM"
> queda RESUELTO. (Histórico: id=549 = 15.765 fue la slice inicial; id=613 = 111.844 fue un veredicto
> `platform_facet` intermedio del mismo valor.)

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
- **verdict id=638 TRUSTWORTHY** · count=**111.844** aristas · `db_edges=111.844 == db_join_vehicles=111.844 == db_distinct_refs=111.844` (div 0.0), `dup_veh=0`. Re-derivado y persistido en DB viva esta sesión vía `pipeline.verify.record_count_verdict` (helper canónico, los 3 caminos ortogonales concuerdan al dígito).
- Histórico: id=549 = 15.765 (slice inicial sellada); id=613 = 111.844 (veredicto `platform_facet` intermedio, mismo valor vivo).
- Live actual: 111.844 aristas (**delta 0 — cuadrado al coche tras el re-VAM**).

## CLI (reproducible)
```bash
python -m pipeline.platform.autocasion_facet --makes all                  # drena todas las makes
python -m pipeline.platform.autocasion_facet --make audi --make seat
python -m pipeline.platform.autocasion_facet --segment vo --concurrency 8
python -m pipeline.platform.autocasion_wholesale
```

## Trampas / notas
- **Cierre hecho (2026-06-13):** el re-VAM se ejecutó y persistió (id=638); el número del runbook ya refleja la slice viva.
- Usar facets **path-segment** (`/{make}-ocasion/{province}`), NO `?marca=&provincia=` (robots disallowa los query-param y los ignora).
