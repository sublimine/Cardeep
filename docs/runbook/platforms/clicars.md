# Clicars — clicars
**Estado:** ✅ VALIDADO (cubierto por verdict id=541 `chains`, group count=37.319, 2026-06-13)  ·  **Grupo:** Cadenas VO

## Identidad
- cdp_code: `CDP-ES-00-QCMVM26T` · kind: `cadena` · source_group: `chain` · defense_tier: `t0_open` · data_surface: `next_data` · source_key: `group_vo_chains_clicars`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.clicars.com/coches-segunda-mano-ocasion` (cadena VO; tarjetas SSR HTML en `__NEXT_DATA__`). `chrome131`, 12 coches/página, `surface_intent=ssr_html_cards`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET el listado.
2. Extraer `__NEXT_DATA__` → tarjetas SSR (12 coches/página).
3. Paginar.
4. Owner = la cadena (`owner_model=chain`).

## Receta / config
- Conector: `pipeline/platform/group_vo_chains_wholesale.py` (member `clicars`)
- Governor: **STEALTH** default 0.7 · `defense_tier=t0_open`
- Owner model: `chain` · Cage: cadena + delta + recipe

## Validación (VAM)
- **Cubierto por verdict id=541 `chains` TRUSTWORTHY** (group, div 0.0). edges vivos = **1.470**.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_vo_chains_wholesale --members clicars --pages 1000
```

## Trampas / notas
- Atribución chain-as-owner.
