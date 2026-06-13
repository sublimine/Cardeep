# OK Mobility — ok-mobility
**Estado:** ✅ VALIDADO (base del verdict id=542 `rentacar_vo`, count=166, 2026-06-13)  ·  **Grupo:** Rent-a-car VO

## Identidad
- cdp_code: `CDP-ES-07-KWGRMQ7B` · kind: `rent_a_car_vo` · role: `chain` · source_group: `rentacar_vo` · defense_tier: `t1_soft` · data_surface: `sitemap` · source_key: `group_rentacar_vo_okmobility`

## Data-layer (la fuente real)
- Endpoint: `GET https://okmobility.com/en/buy-car/used?page=N` (SSR HTML). Operador de rent-a-car (Palma, prov. 07) que liquida su ex-flota VO. Locale `/en/` (200); `/es/` 404.
- Tope/partición: `<span id="total-cars">` = stock total; ~35/pág, ~6 págs.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET page=1.
2. `<span id="total-cars">` = stock total.
3. Por tarjeta `<a class="own-car-card" data-carid=...>`: make/model (`div.car-name`), version (`div.car-motorization`), año/km/fuel/trans (`div.car-summary`), precio (`div.big-cipher-text`), prev_price (`div.deleted-small-cipher-text`), foto (`div.car-image[data-srcbg]`).
4. Caminar `?page=N` hasta página con 0 tarjetas.

## Receta / config
- Conector: `pipeline/platform/group_rentacar_vo_wholesale.py` (member `okmobility`)
- Governor: **STEALTH** default 0.7 · `defense_tier=t1_soft` (beacon Opticks; HTML no gateado)
- Owner: la empresa es el punto de venta y dueña de cada coche · `surface_intent=ssr_html_used_stock_storefront` · Cage: operador + delta + recipe

## Validación (VAM)
- **base del verdict id=542 `rentacar_vo` TRUSTWORTHY** (group, div 0.0; OK Mobility en solitario certificó 166). edges vivos = **169**.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_rentacar_vo_wholesale --member okmobility --pages 6
```

## Trampas / notas
- Locale `/en/` da 200; `/es/` da 404.
- Precio retail real (no bid-gated): 100 % no-NULL.
