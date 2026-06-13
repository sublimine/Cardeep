# Centauro — centauro
**Estado:** ✅ VALIDADO (dentro del verdict id=542 `rentacar_vo`, group count=166, 2026-06-13)  ·  **Grupo:** Rent-a-car VO

## Identidad
- cdp_code: `CDP-ES-03-BMPR08V3` · kind: `rent_a_car_vo` · source_group: `rentacar_vo` · defense_tier: `t1_soft` · source_key: `group_rentacar_vo_centauro`

## Data-layer (la fuente real)
- Endpoint: `GET https://ventas.centauro.net/coches-ocasion/?pagina=N` (SSR puro). Solo `?pagina=` pagina. 12 coches/página, clamp-repeat en el tail.
- Campos en hidden inputs: `precio`, `precioNuevo`, `kilometros`, `marcaVehiculo`, `modeloVehiculo`, `mesesAntiguedad`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `?pagina=N`.
2. Extraer hidden inputs por card.
3. Parar en clamp-repeat del tail (página que añade 0 nuevos).

## Receta / config
- Conector: `pipeline/platform/group_rentacar_vo_wholesale.py` (member `centauro`)
- Governor: **STEALTH** default 0.7 · `defense_tier=t1_soft`
- Owner: la empresa (single-operator) · Cage: operador + delta + recipe

## Validación (VAM)
- **Dentro del verdict id=542 `rentacar_vo` TRUSTWORTHY** por su pathA (`source_group=rentacar_vo`). edges vivos = **28**. (El `primary_value=166` del verdict refleja el estado a 00:37Z, solo OK Mobility; Centauro se añadió después.)

## CLI (reproducible)
```bash
python -m pipeline.platform.group_rentacar_vo_wholesale --member centauro
```

## Trampas / notas
- Solo `?pagina=` pagina; clamp-repeat en el tail (parar al añadir 0 nuevos). Precio retail real 100 % no-NULL.
