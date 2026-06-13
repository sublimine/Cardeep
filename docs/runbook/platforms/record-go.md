# Record Go — record-go
**Estado:** ✅ VALIDADO (dentro del verdict id=542 `rentacar_vo`, group count=166, 2026-06-13)  ·  **Grupo:** Rent-a-car VO

## Identidad
- cdp_code: `CDP-ES-12-H26EC1KD` · kind: `rent_a_car_vo` · source_group: `rentacar_vo` · defense_tier: `t1_soft` · source_key: `group_rentacar_vo_recordgo`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.recordgoocasion.es/coches/segunda-mano/?page=N` (CMS DealerK/MotorK, clases `vcard-*`). Solo `?page=` pagina.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `?page=N`.
2. Parsear cards `vcard-*` byte-a-byte (la misma familia DealerK).
3. Paginar.

## Receta / config
- Conector: `pipeline/platform/group_rentacar_vo_wholesale.py` (member `recordgo`)
- Governor: **STEALTH** default 0.7 · `defense_tier=t1_soft`
- Owner: la empresa (single-operator) · Cage: operador + delta + recipe

## Validación (VAM)
- **Dentro del verdict id=542 `rentacar_vo` TRUSTWORTHY** por su pathA (`source_group=rentacar_vo`). edges vivos = **18**.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_rentacar_vo_wholesale --member recordgo
```

## Trampas / notas
- CMS DealerK/MotorK (clases `vcard-*`), parseado por la misma familia que `family_dealerk_wp`. Solo `?page=` pagina. Precio retail real 100 % no-NULL.
