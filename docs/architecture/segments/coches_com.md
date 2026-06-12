# coches.com — auditoría de segmentos (verificada a mano, 2026-06-13)
> El audit por agente falló (rate-limit de la API). Números contados por el Director
> a mano contra la fuente real (sitemaps + SRP __NEXT_DATA__). VAM: 2 caminos por segmento
> (sitemap urlset/index + SRP total).

## Breakdown real (coches INDIVIDUALES a la venta)
| Segmento | URL/superficie | Sitemap | SRP __NEXT_DATA__ total | Cubierto |
|---|---|---|---|---|
| VO usados | `/coches-segunda-mano/` · per-make SRP | vo.xml = 92.259 (4 shards) | classifieds.total = **92.378** | ✅ conector (per-make SRP) |
| km0 | `/km0/` | renting.xml mezclado/incompleto | popularClassified.total = **15.630** | ❌ HUECO |
| VN nuevos (stock real) | `/coches-nuevos/coches-nuevos.htm` | vn.xml = 828 | search.total = **815** | ❌ HUECO |
| renting | `/renting/` (home 404; sitemap) | renting.xml = 266 | — | ❌ HUECO |
| **TOTAL individual** | | | **~109.089** | tengo 92.378 = 85% |

## "230.000" (marketing)
La home muestra ~230.000. El delta vs ~109k individual = el **configurador de coches nuevos**
(`/coches-nuevos/` pageProps = makes/news/variant, catálogo modelo×versión, NO stock individual
con id/precio/km/dealer). CARDEEP indexa coches reales a la venta → objetivo = ~109k individual.
Si el owner quiere también el catálogo de configuraciones nuevas, es un segmento aparte (kind distinto).

## Acción
Extender `coches_com_wholesale.py` con `--segment {vo|km0|vn|renting|all}`:
- VO: ya implementado (per-make SRP classifiedList).
- km0: `/km0/` per-make SRP (clave popularClassified/classifiedList), ~15.630.
- VN: `/coches-nuevos/coches-nuevos.htm` SRP (search/classifiedList), ~815.
- renting: enumerar renting.xml (266 PDPs) directo.
Re-drenar DESPUÉS de que termine el drenaje VO en vuelo (mismo host www.coches.com → evitar baneo).
Item VO de muestra confirmado: {id, visibleId, price.amount, make, model} — misma estructura sirve a km0/VN.
