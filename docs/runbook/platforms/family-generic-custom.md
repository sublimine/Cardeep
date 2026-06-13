# family_generic_custom — bespoke own-site
**Estado:** ✅ VALIDADO (verdict id=597, count=1.029, 2026-06-13)  ·  **Grupo:** Long-tail (familia bespoke)

## Identidad
- source_key: `family_generic_custom` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa · members: 10 · producing: 10

## Data-layer (la fuente real)
La mitad dura: 83 dealers / 73 dominios sin señal de plataforma compartida. El multiplicador es **arquitectónico**: UN spine drena N recetas per-dealer registradas en un `REGISTRY: dict[str, DealerRecipe]` (cada una: `listing_path`, `parser`, modo de paginación, subfamily). Aún sobreviven micro-familias (p.ej. **Pymecar**: carhay.com + autopai.es comparten `parse_pymecar`, cards `img.pymecar.com`).
- Engine: `curl_cffi` chrome131, SSR HTML; cada `DealerRecipe` define su `listing_path` (`/coches-segunda-mano`, `/vehiculos-ocasion/`, `/es/inventario/`, `/index.php/es/stock-automoviles`…) y su `parser` dedicado.
- Paginación por dealer: `query` (`?page=N`), `single` (todo en una página), `template` (WP/Joomla `/page/N/` o `?start=N`).

## Micro-acciones (cómo se scrapea, paso a paso)
1. Resolver dealer → su `DealerRecipe` del REGISTRY.
2. GET `listing_path`, aplicar el `parser` dedicado.
3. Paginar según el modo registrado.

## Receta / config
- Conector: `pipeline/platform/family_generic_custom_wholesale.py` · `FAMILY_KEY='family_generic_custom'` · STEALTH · t0_open

## Validación (VAM)
- **verdict id=597 TRUSTWORTHY** · count=**1.029** cars · div 0.0 · healthy/closed.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_generic_custom_wholesale --all
python -m pipeline.platform.family_generic_custom_wholesale --dealers autofesa.com carhay.com
```

## Trampas / notas
- Dealers registrados (10, todos en DB): autofesa.com, carhay.com, autopai.es, arguelles-automoviles.com, frworldcars.com, csvmotor.com, autocastro.es, puntomotortenerife.com, robledauto.com, gupicarauto.es.
- Roster excluido honestamente (homepages OEM/global, delegadores, shells JS sin cards SSR) → ver [NOT-VALIDATED.md](../NOT-VALIDATED.md). Construir receta para un shell JS o homepage de marca fabricaría propiedad → se saltan.
