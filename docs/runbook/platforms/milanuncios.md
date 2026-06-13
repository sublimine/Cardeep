# milanuncios — milanuncios
**Estado:** ✅ VALIDADO (verdict id=554, count=259.706, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

## Identidad
- cdp_code: `CDP-ES-00-E382JYEH` · kind: `plataforma` · source_group: `marketplace_generalist` · defense_tier: `t1_soft` · family: `—` · data_surface: `internal_api`

## Data-layer (la fuente real)
- Endpoint: `GET https://searchapi.gw.milanuncios.com/v4/classifieds?category=13&transaction=supply&limit=100&sort=newest&offset=0`
- Headers: `accept: application/json, text/plain, */*`, `origin: https://www.milanuncios.com`, `referer: https://www.milanuncios.com/`. Sin auth, sin reese84, sin bearer.
- Tope/partición: cap duro `from+size ≤ 10.000` por vista filtrada (sin cursor que lo levante). `category=13` = Coches; `limit` honrado hasta 100 (101+ → fallback de 30).
- Oráculo de cobertura: `pagination.totalHits` es `track_total_hits` ES (`>10k → {relation:"gte", value:10000}`; `≤10k → {relation:"eq", value:<EXACTO>}`).

## Micro-acciones (cómo se scrapea, paso a paso)
1. `for prov in 1..52`: `count({province:prov})`; si `relation=="eq"` → drenar la celda.
2. Si `gte:10000` (6 metros: Alicante 3, Barcelona 8, Madrid 28, Málaga 29, Sevilla 41, Valencia 46) → sub-partir por `priceFrom`/`priceTo` hasta que toda celda sea `eq`.
3. Drenar cada celda `≤10k` por `offset += limit`. Dedup en `id`.

## Receta / config
- Conector: `pipeline/platform/milanuncios_wholesale.py` (`ENDPOINT = https://searchapi.gw.milanuncios.com/v4/classifieds`, L105)
- Governor: host `searchapi.gw.milanuncios.com`. **HALLAZGO:** el connector (L54/L1186/L1200) afirma "JSON_API class", pero el host **NO está en `_HOST_RATE_CLASSES`** → en ejecución hereda **STEALTH (0.7 req/s)**. Discrepancia comentario↔código (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)); el drenaje funciona igual, solo más lento.
- Parser/identidad: dedup `id` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=554 TRUSTWORTHY** · count=**259.706** aristas · `db_edges=259.706 == db_join_vehicles=259.706` (el 3er path `harvested_cageable=12.573` es snapshot parcial → divergence 0.95, pero los dos caminos DB primarios concuerdan exacto → TRUSTWORTHY). **Split: dealer 135.250 · particular 123.784.**
- Live actual: 259.706 aristas (**delta 0 — cuadrado al coche**).

## CLI (reproducible)
```bash
python -m pipeline.platform.milanuncios_wholesale --pages 100
python -m pipeline.platform.milanuncios_wholesale --provinces 42,28 --limit 100
python -m pipeline.platform.milanuncios_wholesale --concurrency 6 --segment supply
```

## Trampas / notas
- **Trampa de filtro:** usar `province` (singular) y `brand`; `provinces`/`make` se ignoran silenciosamente (devuelven `gte:10000` + anuncios off-target). Validar que el filtro "tomó".
- **Trampa de encoding:** strings llegan latin-1 mojibake → `s.encode('latin-1').decode('utf-8')`.
- La conclusión vieja "server-rendered, DOM-scrape" era FALSA: la SPA llama a un REST gateway limpio.
