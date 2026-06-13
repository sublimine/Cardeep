# Flexicar — flexicar
**Estado:** ✅ VALIDADO (cubierto por verdict id=541 `chains`, group count=37.319, 2026-06-13)  ·  **Grupo:** Cadenas VO

## Identidad
- cdp_code: `CDP-ES-00-FYECEGD5` · kind: `cadena` (plataforma) + 186 sucursales `kind=compraventa`/`role=standalone_pos` · source_group: `chain` · defense_tier: `t0_open` · data_surface: `internal_api` · source_key: `group_vo_chains_flexicar`

## Data-layer (la fuente real)
- Endpoint: `GET https://services.flexicar.es/api/v1/vehicles?page=N&size=24` (API REST/JSON abierta de primera parte). Headers: `Accept: application/json`, `Origin: https://www.flexicar.es`, `Referer: https://www.flexicar.es/`. Respuesta `{total, pages, results[]}`.
- Tope/partición: `size` HARD-cap 24 (`size>24` → HTTP 400).

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET page=1 → leer `total`/`pages`.
2. Cargar el directorio de 186 sucursales una vez desde `__NEXT_DATA__` de `https://www.flexicar.es/coches-segunda-mano/` (`.props.pageProps.dealerships[]`).
3. Caminar `page=1..pages`.
4. Por coche, `result.carDealershipSlug` → sucursal → geo (CP[:2]=provincia INE).

## Receta / config
- Conector: `pipeline/platform/group_vo_chains_wholesale.py` (member `flexicar`)
- Governor: **JSON_API** (`services.flexicar.es` en `_HOST_RATE_CLASSES`, 12 req/s) · `defense_tier=t0_open`
- Owner model: `branch` (per-branch) · `surface_intent=json_api` · Cage: cadena + 186 sucursales + delta + recipe

## Validación (VAM)
- **Cubierto por verdict id=541 `chains` TRUSTWORTHY** (group, div 0.0). edges vivos = **23.874**; 186 entidades-sucursal.

## CLI (reproducible)
```bash
python -m pipeline.platform.group_vo_chains_wholesale --members flexicar --pages 1000
```

## Trampas / notas
- `size` hard-cap 24 (>24 → 400). Atribución per-branch: cada coche a su sucursal `compraventa` (186 puntos).
