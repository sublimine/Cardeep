# CARDEEP — Auditoría de integridad de datos (2026-06-16)

> Disparada por el owner: "todo roto, 1,5M imposible, máx 15/dealer, dealers multiplicados con el
> mismo inventario, falta inventario, gaps/parciales, ¿me vacilas?". Veredicto: **sus quejas son
> correctas.** Todo lo de abajo es [VERIFICADO] contra cardeep-pg viva (no estimado).

## Hallazgos medidos
| Métrica | Valor | Fuente |
|---|---|---|
| Filas vehicle available | 1.697.247 | `count(*) status=available` |
| Filas gone | 7.721 | idem |
| **deep_links únicos** (available) | **1.557.396** | `count(distinct deep_link)` |
| **Filas duplicadas (mismo deep_link, >1 entidad)** | **139.851 (~8,2%)** | group by deep_link having n>1 |
| Coches únicos físicos (B7, cross-plataforma) | 1.486.285 | v_canonical_vehicle |
| Filas entity no-particular | 61.729 | — |
| Canónicos resueltos (v_dealer_resolved) | 40.194 | — |
| **Dealers no-particular con 0 inventario** | **23.916 (~39%)** | distribución |
| …de ellos sin vehículo NUNCA y sin receta | 23.888 | never-harvested |
| Dealers con recipe_version no-null | 537 | — |
| Reparto available por kind | compraventa 1.180.409 · particular 502.541 · subasta 7.153 · oficial 3.297 · resto <2k | group by kind |
| Distribución no-particular | 0:23.916 · 1-5:15.026 · 6-15:10.038 · 16-50:8.771 · 51-200:3.304 · 200+:674 | buckets |
| Ejemplo duplicación | QUADIS Autolica = 520 filas → 6 canónicos; 11Eleven ×3 comparten 6 deep_links | — |

## Causas raíz (systematic-debugging)
1. **DUPLICADOS VISIBLES — defecto de SERVIDO (no de datos).** El clustering `v_dealer_resolved`
   SÍ colapsa (61.729→40.194; QUADIS 520→6), pero `/geo/{prov}/entities` sirve `servable_entity`
   (filas crudas), no los canónicos. → Hay que servir el canónico y agregar el inventario del clúster.
   **Arreglable sin gasto (código/SQL).**
2. **INVENTARIO FRAGMENTADO/DUPLICADO POR DEALER.** El mismo coche (deep_link) cuelga de varias
   entidades alias; `/entities/{cdp}/inventory` dedupa dentro del clúster sólo si las 3 alias están en
   el mismo clúster. El listado por provincia, al no resolver, parte el inventario. → Servir inventario
   agregado del clúster, dedup por deep_link/canonical_vehicle. **Arreglable sin gasto.**
3. **VACÍOS / FALTA INVENTARIO / GAPS — fase de cosecha no ejecutada.** 23.888 dealers descubiertos
   pero nunca scrapeados (0 vehículos, 0 receta). Esto es el "no completaste todo": cosechar el stock de
   los 61.729 dealers es la fase de compute/gasto que estaba **congelada por decisión de gasto**.
   **Requiere correr la flota de scrapers** (D1: dentro de los límites del PC).
4. **"1,5M sobrevendido".** El número es real (1.486.285 únicos físicos) pero su LECTURA fue engañosa:
   no es "1,5M de anuncios navegables por dealer" — es 502k C2C + volumen concentrado en pocos grandes
   + ~140k duplicados. Reportarlo como logro limpio fue maquillaje por mi parte. Corregido aquí.

## Plan de corrección
- **F-A (sin gasto): servir canónicos.** `/geo/{prov}/entities` y el conteo → colapsar a
  `v_dealer_resolved` (un dealer = un canónico, agregando alias). Mata "11Eleven ×3" / "QUADIS ×520".
- **F-B (sin gasto): inventario por clúster, deduplicado** por deep_link/canonical_vehicle, agregando
  todas las alias del canónico. Un dealer muestra TODO su stock real, sin duplicar.
- **F-C (sin gasto): honestidad de cifras** en la UI — distinguir "anuncios", "coches únicos",
  "C2C vs dealer", y no mezclar.
- **F-D (compute/cosecha): completar inventario** de los 23.888 vacíos + parciales. Campaña de la flota
  de scrapers dentro de los límites del PC. Es la única vía a "completar absolutamente todo".

## Estado
Diagnóstico cerrado y verificado. F-A/F-B/F-C son código/SQL y no necesitan gasto → se ejecutan ya.
F-D es la cosecha (compute) que el owner había diferido; sin ella no hay "todo completo". Sin maquillaje.
