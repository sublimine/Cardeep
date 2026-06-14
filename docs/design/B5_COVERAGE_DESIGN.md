# B5 — Cobertura total + filtrado · diseño verificado (2026-06-14)

> El 100% de los puntos de venta de coches de España, con denominador medido, dealers separados
> del ruido C2C, y el long-tail cazado. Diseño sobre el recon `docs/recon/B5_COVERAGE_RECON.md`,
> con los números base re-verificados por el Director. Acoplado a B4: cerrar la cobertura de
> wallapop cierra su geo residual (39,5k particulares sin municipio).

## Estado real [VERIFICADO DB 2026-06-14]

Split por kind: `particular` 328.776 · `compraventa` 39.308 · `garaje` 7.220 ·
`concesionario_oficial` 1.844 · `desguace` 1.645 · `subasta` 97 · `plataforma` 18 · resto 35.
POS (no-particular) = **50.167**. Particulares por nº coches: 1→281.855 (85,7%) · 2-3→45.599 ·
4-10→1.107 · 11-30→161 · 30+→54 (legacy buckets).

Denominadores oficiales [VERIFICADO fuente, recon]:
| Segmento | Denominador | Tenemos | Cobertura |
|---|---|---|---|
| Concesionarios franquiciados | 2.143 grupos / 5.358 instalaciones (FACONAUTO/DBK 2024) | 1.844 | 86,1% grupos |
| Desguaces CAT | 1.292 (censo legal DGT, exacto) | 1.645 | >100% → **overcount, deflación** |
| Compraventas indep. | 1.662 floor (PA) / 15-27k techo (CNAE 4511) | 39.308 | **overcount sobre floor** |
| Garajes que venden | indefinido (sells_cars NULL 99,7%) | 7.220 | inmensurable sin clasificar |
| Plataformas | ~23 | 18 | 78% |

## Sub-bloques (orden por impacto/desbloqueo)

- **B5.1 — Wallapop exhaustivo** *(en curso)*. El cap 8000 era el flag `--target`, NO un límite de
  API [VERIFICADO código L1470]; el fix de memoria `_BoundedSeen`+`_BoundedSellerCache` ya existe
  [L690/728]. `--target` alto (chunks de 100k) enumera wallapop hasta saturar el cursor plano
  (~224k) + sweep keyword×centroid. Cierra el geo residual de wallapop (39,5k sin municipio, vía
  resolver B4.2 + lat/lon persist B4.4 + reverse-geocode B4.3) Y sube cobertura 89,7%→~100%. €0.
  Luego `cleanup_legacy_buckets()` purga los 22.900 legacy bucket cars.
- **B5.2 — Filtrado particular/dealer** *(gate B5 central)*. La señal `type=professional`
  (wallapop `/users/{id}`) y `sellerType=professional` (milanuncios) ya se capturan pero no
  reclasifican. Upgrade `kind=particular`→`compraventa` para professionals; los >3 coches son
  candidatos secundarios. API: exponer `kind != 'particular'` por defecto (los 50.167 POS), C2C
  solo en modo explícito. Decide "particular vs dealer" sin perder el inventario C2C real.
- **B5.3 — Deflación de overcount**. Desguaces 1.645 vs 1.292 censo + compraventa 39.308 vs floor:
  ¿duplicados intra/cross-source que B1 (entity_cluster) no colapsó? Re-correr el dedup B1 sobre
  los nuevos + medir contra el censo DGT (verdad legal). El cluster debe acercar desguace a ~1.292.
- **B5.4 — Denominador Chapman**. Capture-recapture sobre `entity_source`: OSM ∩ PA ∩ AS24 ∩
  Overture por provincia → N̂ honesto del universo compraventa/garaje (hoy desconocido). La
  infraestructura (`entity_source`) existe; falta la query. Primer denominador medido por provincia.
- **B5.5 — Long-tail** (€0, alto ROI): (a) **AS24 drain completo** — 278k coches declarados, solo
  262 dealers atribuidos; el drain wholesale descubre miles de dealers como side-effect. (b)
  **Overture Maps dump** (DuckDB/Parquet, `car_dealer`/`automotive`, ~5-10k POIs, ortogonal a OSM
  para Chapman). (c) CCAA taller registries (RASIC/CETRAA ~20k) + classifier Haiku para `sells_cars`.
  (d) 157 dominios WordPress dealers → una receta drena todos.
- **B5.6 — Gaps geográficos**: Ceuta (9 dealers) + Melilla (17) subrepresentadas → censo manual
  OEM locators + Cámara de Comercio. Soria/Segovia/Teruel/Ávila/Palencia rural under-count → Overture
  + PA crawl. Canarias/Baleares ya bien cubiertos.

## Gate B5 (binario, honesto)

- `sells_cars` resuelto para garajes (classifier) → denominador de SEG-garaje medible.
- particular vs dealer DECIDIDO: professionals reclasificados, API filtra por defecto, C2C servible aparte.
- Overcount deflactado: desguace ≈ censo DGT 1.292 (±tolerancia), compraventa cluster-deduplicado.
- Denominador Chapman por provincia para compraventa/garaje (numerador VAM / N̂).
- Canarias/Ceuta/Melilla con cobertura medida y gap-con-causa.
- Cada segmento: SELLADO (cobertura ≥ umbral) o gap confesado con causa y número. Alimenta B6 (sello 52/52).
