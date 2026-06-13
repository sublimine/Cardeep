# motor.es — motor-es
**Estado:** ✅ VALIDADO (verdict id=558, count=49.009, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

## Identidad
- cdp_code: `CDP-ES-00-HSV4XZ2H` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t1_soft` · family: `—` · data_surface: `json_ld`

## Data-layer (la fuente real)
- Endpoints: `GET https://www.motor.es/segunda-mano/coches/get-data-ajax/` (SOLO denominador: `data.total=50.932`) + `GET https://www.motor.es/segunda-mano/{make}/?pagina=N` (SSR, 23 cards/page) + `/{make}/{model}/?pagina=N` (leaf si make>1.150)
- Headers: `Referer: https://www.motor.es/segunda-mano/coches/`. Motor Internet S.L. (PHP/SSR, NO Next.js).
- Tope/partición: cap UI duro **50 páginas (≤1.150 filas)** por facet (`?pagina=51` → 404). No hay surface uncapped único → partición path make→model. Query-params (`?precio_hasta=`) ignorados.
- `get-data-ajax` es un seed congelado de 10 filas (todo cursor/param ignorado) → usar SOLO para denominador y taxonomía.

## Micro-acciones (cómo se scrapea, paso a paso)
1. `data.total` de get-data-ajax (denominador, re-leer cada pasada).
2. Taxonomía: sidebar HTML enumera 117 slugs 1-seg (makes + provincias); excluir las 52 provincias → makes.
3. Por make: GET facet, leer total ("N coches"). Si ≤1.150 → drenar la make entera. Si >1.150 → por model `/{make}/{model}/`. Si un model >1.150 → 3er nivel province `/{make}/{model}/{province}/`.
4. Cards: `<article class="elemento-segunda-mano">` con `data-id` + `data-goto` base64 → PDP `/segunda-mano/anuncio/{id}/`. Dedup en `data-id`.
5. Enriquecer: PDP JSON-LD `[0] @type:Car` → `offers.price`, `offers.seller.name` (= dealer vendedor).

## Receta / config
- Conector: `pipeline/platform/motor_es_wholesale.py` (segmentos `all` + claves de `SEGMENTS`; flag `--rate` propio default 3.0)
- Governor: host `www.motor.es` → **STEALTH default** (0.7 req/s; sin override — governor.py L324-325 deja nota "must not move"). El `--rate 3.0` del CLI es interno; el governor por-host es el techo real.
- Parser/identidad: dedup `data-id` · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=558 TRUSTWORTHY** · count=**49.009** aristas · `db_edges=49.009 == db_join_vehicles=49.009` (3er path `harvested_cageable=0` de snapshot vacío → divergence 1.0, pero los dos caminos DB concuerdan exacto → TRUSTWORTHY). dealer=49.009 · particular=0.
- Live actual: 49.009 aristas (**delta 0 — cuadrado al coche**). Denominador get-data-ajax ≈50.932.

## CLI (reproducible)
```bash
python -m pipeline.platform.motor_es_wholesale --full                       # make→model census completo
python -m pipeline.platform.motor_es_wholesale --max-cells 200 --limit 23
python -m pipeline.platform.motor_es_wholesale --segment vo --concurrency 6 --rate 3.0
```

## Trampas / notas
- `vehicleIdentificationNumber` es DUMMY estático → usar `data-id`+PDP url como clave de vehículo.
- make→model es MECE (prueba suma: Cupra 341≈345). El doc viejo "2.316 páginas" era FALSO (refutado live: cap real 50 páginas).
