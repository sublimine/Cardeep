# Carplus — carplus
**Estado:** ✅ VALIDADO (cubierto por verdict id=541 `chains`, group count=37.319, 2026-06-13)  ·  **Grupo:** Cadenas VO

## Identidad
- cdp_code: `CDP-ES-00-4YVMXZ3T` · kind: `cadena` · source_group: `chain` · defense_tier: `t0_open` · data_surface: `json_ld` · source_key: `group_vo_chains_carplus`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.carplus.es/coches-segunda-mano/` (cadena VO; JSON-LD `Vehicle` en SSR). `chrome131`, 16 coches/página, `surface_intent=ssr_jsonld_vehicles`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET el listado.
2. Parsear bloques JSON-LD `Vehicle` (16 coches/página).
3. Paginar.
4. Owner = la cadena (`owner_model=chain`).

## Receta / config
- Conector: `pipeline/platform/group_vo_chains_wholesale.py` (member `carplus`)
- Governor: **STEALTH** default 0.7 · `defense_tier=t0_open`
- Owner model: `chain` · Cage: cadena + delta + recipe

## Validación (VAM)
- **Cubierto por verdict id=541 `chains` TRUSTWORTHY** (group, div 0.0). edges vivos = **412**.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_vo_chains_wholesale --members carplus --pages 1000
```

## Trampas / notas
- Atribución chain-as-owner. La cadena más pequeña del grupo.
