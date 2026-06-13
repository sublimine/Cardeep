# family_dms_vendor_platforms — inventario.pro + motorflash
**Estado:** ✅ VALIDADO (verdict id=596, count=799, 2026-06-13)  ·  **Grupo:** Long-tail (familia DMS)

## Identidad
- source_key: `family_dms_vendor_platforms` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa · members: 27 · producing: 22

## Data-layer (la fuente real)
El multiplicador más limpio (template uniforme por subfamilia). Dos subfamilias, una receta + un governor + un cage.
- **inventario.pro (15 dealers / 19 entities):** fingerprint asset host `inventario.pro`. Listing paths `/coches`, `/coches-ocasion`, `/coches-nuevos`, `/vehiculos`; paginación `?pagina=N`. Detail `/coches/<make>/<model>/<numeric_id>` (`<id>`=`listing_ref`). Fields: make/model del `titulo_card` o slug; price `div.precio`; km `span.uk-icon-road`; year `span.uk-icon-calendar-o`; fuel `inventario-icon-fuel`; photo `imgs.inventario.pro/*`. SSR, sin JS.
- **motorflash (11 dealers / 12 entities):** fingerprint señal `motorflash` (widget de stock; CMS host varía). Listing `/coches-ocasion`, `/coches`, … `?pag=N`. Detail `/ficha-vehiculo-ocasion/<slug>/<id>`. Fields vía hidden inputs: `marcaVehiculo`, `modeloVehiculo`, `precio`, `kilometros`, `mesesAntiguedad`; photo `images.motorflash.com/*`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Resolver dealer por host; detectar subfamilia por fingerprint.
2. Recorrer listing paths de la subfamilia, paginar.
3. Extraer fields (DOM cards inventario.pro / hidden inputs motorflash).
4. `deep_link` + `listing_ref` del detail template.

## Receta / config
- Conector: `pipeline/platform/family_dms_vendor_platforms__wholesale.py` · `FAMILY_KEY='family_dms_vendor_platforms'` · STEALTH · t0_open

## Validación (VAM)
- **verdict id=596 TRUSTWORTHY** · count=**799** cars · div 0.0 · healthy/closed.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_dms_vendor_platforms__wholesale --seeds
python -m pipeline.platform.family_dms_vendor_platforms__wholesale --from-db --limit 8
python -m pipeline.platform.family_dms_vendor_platforms__wholesale --dealers canaauto.es helmantica.es
```

## Trampas / notas
- Seeds verificados inventario.pro: canaauto.es, carsandbikes.es, ftome.com, masmotorcantabria.net, eveauto.es, autosniser.es, integralmotion.es, iluscar.com, mobilitycentro.com, garciautodelvalles.com, automovilesgabilondo.com, autosocasionalminares.com, carmotors99.com, tuokasion.es, bellamachina.es. Motorflash: helmantica.es, grupmibec.com, autoelia.es, movento.es, bmwpremiumselection.es.
- `grupogamboa.com`/`setienherra.es` (inventario.pro) devolvieron cert errors → no confirmados (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).
