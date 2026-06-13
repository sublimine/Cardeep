# GRUPO · Long-tail own-site (`source_group='long_tail_web'`, multiplicador de familia CMS/DMS)

> Más allá de Tier-1 y OEM-VO, el inventario vive en la **web propia de cada dealer**
> (`www.<dealer>.es`). Rasparlos uno a uno no escala. El multiplicador es la **familia CMS/DMS**:
> agrupar dealers por la plataforma que corre su web y escribir **UNA receta por familia**.

## Modelo de propiedad (la mitad más simple)

La web propia del dealer es la fuente PRIMARIA de su stock, **no** un marketplace. Por eso NO hay
arista `platform_listing`: cada coche es `vehicle.entity_ulid = el dealer`. Propiedad singular y
directa. Arquitectura compartida: las 7 familias replican la espina de `family_dealerk_wholesale` /
`coches_net_wholesale` (mismo governor, `GeoResolver`, upserts idempotentes, eventos NEW-delta,
quórum VAM, heartbeat S-HEALTH). No es un fork.

## Cifras maestras (vivas)

| métrica | valor | reconciliación |
|---|---:|---|
| **long-tail own-site cars** (website + owned + no-edge) | **20.165** | — |
| no-website own-site cars (excluidos por diseño) | 26.198 | — |
| total no-edge vehicles | 46.363 | 20.165 + 26.198 = 46.363 ✓ |
| total `vehicle` | 1.482.547 | con arista: 1.436.184 → diff 46.363 ✓ |

> Tres conteos legítimos por familia, **nunca conflados**: (1) **VAM harvest slice** = pares
> `(dealer, deep_link)` firmados a 0.0 (la cifra fiable, tabla de abajo); (2) **no-edge def #2** =
> superset; (3) **global** 20.165. No son intercambiables.

## Las 7 familias VAM-firmadas (lo que SÍ entra al runbook)

Cada familia tiene un `verification_verdict` `subject_type='family_slice'`, TRUSTWORTHY, `div=0.0`,
claim `"distinct (dealer, deep_link) harvested == family vehicles persisted in DB"` (últimos verdicts).

| source_key | verdict id | primary_value (VAM slice) | members | producing | Ficha |
|---|---:|---:|---:|---:|---|
| `family_dealerk_wp` | **606** | **2.270** | 37 | 34 | [family-dealerk-wp](../platforms/family-dealerk-wp.md) |
| `family_builder_wholesale` | **598** | **1.224** | 9 | 2 | [family-builder-wholesale](../platforms/family-builder-wholesale.md) |
| `family_generic_custom` | **597** | **1.029** | 10 | 10 | [family-generic-custom](../platforms/family-generic-custom.md) |
| `family_dms_vendor_platforms` | **596** | **799** | 27 | 22 | [family-dms-vendor-platforms](../platforms/family-dms-vendor-platforms.md) |
| `family_cms_wp` | **535** | **518** | 13 | 13 | [family-cms-wp](../platforms/family-cms-wp.md) |
| `family_framework_webbuilder` | **525** | **358** | 7 | 4 | [family-framework-webbuilder](../platforms/family-framework-webbuilder.md) |
| `family_unreachable` | **498** | **246** | 1 | 1 | [family-unreachable](../platforms/family-unreachable.md) |
| **TOTAL VAM family-slice** | — | **6.444** | — | — | 7/7 healthy, 7/7 closed |

El `evidence` de cada verdict reza `paths={'db_family_vehicles': N, 'harvested_pairs': N,
'cars_ingested_distinct': N}` con los tres iguales y `divergence=0.0`.
`family_framework_webbuilder` usa `cars_caged_distinct` (misma semántica: 358==358==358).

## Ranking de familias (`docs/_longtail_family_ranking.json`)

Sobre el set own-site vivo (369 dominios distintos). La unidad que una receta ataca es el **dominio
registrable**: `cms` 157 dom / 179 ent (42,5 %), `unreachable` 86/91 (23,3 %), `generic/custom`
73/83 (19,8 %), `dms` 28/33 (7,6 %), `framework` 17/18 (4,6 %), `builder` 8/9 (2,2 %). 283/369
reachable; 86 unreachable.

## Config común

`kind` del dealer `compraventa`/`concesionario_oficial`; el `source_key` ES la familia
(`family_<X>`); governor **STEALTH** (ningún host de familia en `_HOST_RATE_CLASSES`, bucket por
host); `defense_tier=t0_open` para las 6 familias Tier-0, **t1_browser** solo para
`family_unreachable` (Chromium real, body-gate ciego al status); ownership directa sin arista.

## De dónde salen los dealers own-site (fase DESCUBRIR)

Los puntos de venta que alimentan este grupo se hallan con los arneses de descubrimiento validados
([03-DISCOVERY.md](../03-DISCOVERY.md)): el **association-mining** (+409 nuevos AEDRA/ACEVAS/AECS, de
los que 5 concesionarios AECS DealerK aportaron **327 coches** own-site vía verdict id 609) y el
**barrido geográfico** (+68 dealers, 40 con web propia cosechable lista para receta per-dealer). Son
candidatos de familia: una vez fingerprinteados caen en una de las 7 familias de arriba.

## Canal `importador` (ola new-channels) — sin unidad validada

El conector `pipeline/platform/group_importador_wholesale.py` se construyó para poblar el canal
`kind='importador'` (operadores de importación alemana). De la censada, solo **MODRIVE** (`modrive.com`)
exponía stock own-site curl_cffi-alcanzable (SSR JSON-LD ItemList). **Estado actual:** el verdict id 626
selló 19 aristas, pero la DB viva tiene **0 listings y 0 platform row** para `CDP-ES-00-MVRE0FYC`
(`[VERIFICADO]` esta sesión) → retirado, no registrable. Las entidades `kind='importador'` reclasificadas
(Carismatic ×4, Trend Cars ×6) no tienen aristas propias cosechadas; el resto de candidatos son sitios
WordPress lead-gen sin catálogo machine-readable. **Por eso NO existe `groups/importador.md`: no hay
unidad validada que lo respalde.** Detalle y evidencia en [NOT-VALIDATED.md](../NOT-VALIDATED.md) §5.3.

**Fuera del runbook:** 89 unreachable genuinamente muertas/walled (confirmadas por camoufox stealth),
9.828 cars own-site sin familia asignada, builders sin superficie machine-readable. Ver
[NOT-VALIDATED.md](../NOT-VALIDATED.md).
