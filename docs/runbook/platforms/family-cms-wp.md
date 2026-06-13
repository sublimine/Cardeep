# family_cms_wp — WordPress-dominado (CMS #1)
**Estado:** ✅ VALIDADO (verdict id=535, count=518, 2026-06-13)  ·  **Grupo:** Long-tail (familia CMS)

## Identidad
- source_key: `family_cms_wp` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa · members: 13 · producing: 13

## Data-layer (la fuente real)
La familia más grande del ranking (157 dominios / 179 dealers) pero theme-VARIADA. Dos estrategias en orden por dealer, bajo una receta:
- **STRATEGY A — Vehica REST (el multiplicador limpio):** el plugin "Vehica" expone gateway JSON público de primera parte en **`/wp-json/vehica/v1/cars`** que devuelve TODO el inventario en UNA llamada (`resultsCount` + `results[]` con `attributes[]`: Marca/Modelo/Año/Kilómetros/Combustible/"Precio al contado"). Byte-idéntico entre dealers Vehica → un parser, sin JS, sin paginación.
- **STRATEGY B — HTML cards SSR (el volumen):** dealers WP no-Vehica renderizan cards bajo un slug. Ranked slug probe (frecuencia real): `/coches` (229) > `/vehiculos` (49) > `/catalogo` (17) > `/ocasion` (17) > `/vehiculos-ocasion` (14) > `/stock` (12) > `/km0` (9) > `/seminuevos` (9) > `/coches-segunda-mano` (7) > `/coches-ocasion` (7)… Selector de card por tema vía tabla **THEME_OVERRIDE** (`ga-car-card`, `sc_cars_item`…).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Resolver dealer por host.
2. Probar `/wp-json/vehica/v1/cars` → si 200 JSON, parsear `results[]` (FIN).
3. Si no, recorrer `LISTING_SLUGS` en orden hasta hallar el índice.
4. Match del marker de tema → extractores; paginar.

## Receta / config
- Conector: `pipeline/platform/family_cms_wordpress_dominated__wholesale.py` · `FAMILY_KEY='family_cms_wp'` · STEALTH · t0_open

## Validación (VAM)
- **verdict id=535 TRUSTWORTHY** · run-slice count=**518** cars · div 0.0 · healthy/closed. (Stock own-site de los 13 dealers en DB, def #2: 599.)

## CLI (reproducible)
```bash
python -m pipeline.platform.family_cms_wordpress_dominated__wholesale \
    --dealers autosraul.com automovilesjfz.com automovileslacanal.com gestiauto.es
python -m pipeline.platform.family_cms_wordpress_dominated__wholesale --from-db --limit 8
```

## Trampas / notas
- Añadir un tema nuevo = una entrada en la tabla THEME_OVERRIDE (no un fork de parser).
- La estrategia A (Vehica REST) es el multiplicador limpio; la B (HTML cards) el volumen.
