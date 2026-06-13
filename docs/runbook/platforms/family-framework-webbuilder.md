# family_framework_webbuilder — Next/Astro/Nuxt/Angular SaaS
**Estado:** ✅ VALIDADO (verdict id=525, count=358, 2026-06-13)  ·  **Grupo:** Long-tail (familia framework)

## Identidad
- source_key: `family_framework_webbuilder` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa · members: 7 · producing: 4

## Data-layer (la fuente real)
Dealers en una SPA JS sobre un dealer-site SaaS compartido. La UI es JS, pero la plataforma emite DOS superficies SSR **sin browser**:
- Fingerprint (spine): logo en `firebasestorage.googleapis.com/v0/b/web-builder/*` **Y** fotos en `storage.googleapis.com/vehicle-multipost-multimedia/*` (o `/vehicles-prd/*`).
- **Superficie 1 — `sitemap.xml`** (candidatos `/sitemap.xml`, `/sitemap-0.xml`, `/sitemap_index.xml`): el inventario COMPLETO, cada `<loc>…-de-segunda-mano-<uuid></loc>` (coincide con el `numberOfItems` de la página). La paginación por query-param es client-side y NO se usa.
- **Superficie 2 — JSON-LD `Car`** por PDP: `offers.price` (EUR), `mileageFromOdometer.value` (km), `productionDate` (year), `brand`, `model`, `name`, `vehicleEngine.fuelType`, `vehicleTransmission` (M/A), `vehicleIdentificationNumber` (UUID = `listing_ref`), `image[0]`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Fingerprint home/listing.
2. Drenar sitemap → todas las URLs.
3. Por PDP parsear el `Car` JSON-LD. UN parser, byte-idéntico en la familia.

## Receta / config
- Conector: `pipeline/platform/family_framework_next_astro_nuxt_angular__wholesale.py` · `FAMILY_KEY='family_framework_webbuilder'` · STEALTH · t0_open

## Validación (VAM)
- **verdict id=525 TRUSTWORTHY** · count=**358** cars · div 0.0 (`db_family_vehicles=358 == cars_caged_distinct=358`) · healthy/closed.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale \
    --dealers inmocoches.com lgautomocion.com vallolidmotor.es furgogandia.com
python -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale --from-db --limit 6
```

## Trampas / notas
- La UI es JS pero el sitemap + JSON-LD son SSR → se drena sin browser. Verificado live: inmocoches 133, lgautomocion 149, vallolidmotor 54, furgogandia 22 (sitemap == numberOfItems).
- Este verdict usa `cars_caged_distinct` en lugar de `cars_ingested_distinct` (misma semántica).
