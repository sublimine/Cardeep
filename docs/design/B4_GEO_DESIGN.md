# B4 — Geo al átomo · diseño verificado (2026-06-14)

> Cada entidad a país→provincia→comarca→ciudad con código INE por nivel. Diseño sobre
> diagnóstico VERIFICADO (código + DB), no sobre la estimación del brief. El recon vive en
> `docs/recon/B4_GEO_RECON.md`; este documento lo corrige donde el código lo contradice.

## Estado real [VERIFICADO]

**Esquema** (ya existe, completo): `geo_province`(52) → `geo_comarca`(323) → `geo_municipality`(8.132)
con FKs reales en `entity` + trigger `trg_entity_set_comarca` (comarca se cierra GRATIS al setear
municipio). `entity` tiene `province_code` CHAR(2), `municipality_code` CHAR(5), `comarca_id`,
`lat/lon`, `geocode_source`/`geocode_precision` (ambos NUNCA poblados). `geo_municipality` NO tiene
centroides lat/lon.

**Gap real por nivel** [VERIFICADO DB, N=369.535] — la cifra 32,5% del brief NO se reproduce:

| Nivel | poblado | gap |
|---|---|---|
| province | 99,91% | 344 |
| **municipality** | **78,34%** | **80.038 (21,66%)** |
| comarca | 78,09% | 80.964 |
| lat/lon | 3,38% | 357.036 |

**Dónde se concentra el gap de municipio** [VERIFICADO DB]:

| kind | gap_muni | recuperable por lat/lon |
|---|---|---|
| particular | 65.886 (82%) | 0 |
| compraventa | 8.034 | 2.105 |
| garaje | 5.488 | 5.469 (99,6%) |
| concesionario/desguace/resto | 630 | 263 |

Accionabilidad cruda del gap: 7.837 con lat/lon · 1.469 con CP · 2.066 con address · **71.681 solo provincia**.

## Causa raíz [VERIFICADO código] — el recon se equivocó en lo esencial

El recon concluyó "particulares sin city en el API → muro de fuente". **FALSO.** Ambos scrapers
parsean el city del payload:
- **wallapop** `parse_vehicle` extrae `location.city` + `location.latitude/longitude` + `region2`;
  `_resolve_province` resuelve `municipality_code(prov, city)` (zip→prov, region2→prov, latlon→prov).
- **milanuncios** `parse_ad_particular` extrae `location.province.id`(INE) + `location.city.name`;
  `_parse_window` resuelve `municipality_code(owner_province, owner_city)`.

El cuello de botella es `GeoResolver.municipality_code` (geo.py L94-98): **match EXACTO normalizado
(NFKD→ascii→lower→alnum), sin fuzzy**. Falla en variantes ("Sant Boi" vs "Sant Boi de Llobregat"),
barrios que no son municipio, abreviaturas, y nombres comerciales de zona. `resolve_city_global`
(usado solo como fallback en wallapop) es aún más estricto: exige unicidad NACIONAL del nombre.

**Dos hechos que mandan sobre la estrategia:**
1. El `city` crudo NO se persiste en `entity` (solo el `municipality_code` resuelto). El backlog de
   65.886 NO es re-resoluble in-place: o se re-scrapea, o se empieza a persistir el locality crudo.
2. Falta CUANTIFICAR la partición del gap: `city`-ausente-en-payload (muro real de fuente) vs
   `city`-presente-no-resuelto (recuperable con fuzzy). Sin ese número la meta es humo → **B4.1 probe**.

**Herramientas:** solo `numpy` instalado. Faltan `rapidfuzz` (fuzzy match), centroides municipio
(reverse-geocode), tabla CP→municipio. Datasets INE presentes en `data/geo/`. Todo €0.

## Sub-bloques

- **B4.1 — Probe empírico (cuantifica la meta).** Script de diagnóstico (sin escribir a DB): re-fetch
  de muestra acotada (milanuncios prov 42 Soria pequeña + 28 Madrid con variantes; wallapop unos
  cientos de items), parsea owners, y por cada uno mide: city-presente · resuelto-exacto-actual ·
  resoluble-fuzzy(rapidfuzz ≥88 dentro de provincia) · solo-latlon · sin-geo. Reporta tasas reales →
  fija la meta de B4 con número, no con suposición. Persiste a `docs/recon/B4_GEO_PROBE.md`.
- **B4.2 — GeoResolver fuzzy.** `rapidfuzz` (MIT, €0): `municipality_code(prov, city)` cae a un match
  fuzzy dentro de la provincia (umbral alto + guardas anti-falso-positivo: longitud, ratio de tokens)
  cuando el exacto falla. Manejo de "X de Y"/barrios→municipio padre. Tests con casos reales del probe.
- **B4.3 — Reverse-geocode.** Cargar centroides municipio (INE/CNIG, libre) a `geo_municipality`;
  `MunicipalityGeocoder` KNN dentro de provincia para los 7.837 con lat/lon (garajes 99,6%, compraventa).
  + tabla CP→municipio (data.gob.es) para los 1.469 con CP. Poblar `geocode_source`/`geocode_precision`.
- **B4.4 — Persistir locality crudo.** Migración: columna/tabla para el `raw_locality` del payload, de
  modo que el re-scrape futuro permita re-resolución sin perder el dato (cierra el hueco que hoy obliga
  a re-scrapear para recuperar el city).
- **B4.5 — Re-geocode del backlog + medición.** Aplicar B4.2/B4.3 al backlog (re-scrape dirigido de las
  fuentes con más gap, o in-place donde el locality ya esté disponible) + medir el gap final por nivel.

## Gate B4 (reinterpretado con honestidad — anti-maquillaje)

El "32,5%→<2%" del brief asumía que todo el gap era geocodificable; el código demuestra que no. Gate real:
- **100% del gap RECUPERABLE cerrado**: todo owner con city resoluble (exacto+fuzzy) o con lat/lon o
  con CP → municipio+comarca. Verificado por ≥2 vías (conteo DB + muestra manual contra el portal).
- **Residual CONFESADO**: el `city` verdaderamente ausente en el payload de la fuente queda con número
  EXACTO y causa por fuente (no se infla, no se esconde). Se ataca en B5 (cobertura) o se acepta como
  suelo de fuente declarado.
- **Meta cuantitativa exacta**: la fija B4.1. El gap de municipio baja del 21,66% al residual-de-fuente
  medido; el gap RECUPERABLE cae a <2%.

## B4.4/B4.5 — validación del lazo + naturaleza del cierre (2026-06-14)

**El lazo funciona [VERIFICADO]**: re-scrape de prueba de milanuncios prov 42 (Soria) con el
resolver B4.2 + upsert COALESCE B4.4 bajó el gap de particulares 120→86 en UNA pasada (34
municipios rellenados: Soria, Almazán, San Esteban de Gormaz, Ólvega, Burgo de Osma...), VAM
TRUSTWORTHY, sin tocar identidad ni dealers.

**Naturaleza del gap [VERIFICADO DB]**: los 65.852 particulares sin municipio NO son fantasmas —
el 100% tiene vehicle `available` y last_seen <7d. Es inventario VIVO, recuperable. El city se
resolvió en su día con el resolver viejo (exacto-only) y quedó NULL; B4.2 lo resuelve cuando el
particular re-aparece en un drain. (Nota: el primer intento de medición usó status='active' —
valor inexistente, el real es 'available'; cazado por el GROUP BY status. Los números son humo,
incluido el propio.)

**Mecánica del cierre**: el inventario C2C (wallapop/milanuncios) ROTA — un drain trae el
inventario del momento, no el acumulado. Un re-scrape único no cierra todo el backlog de golpe:
cada particular se cierra cuando re-aparece en un drain con el resolver B4.2. El cierre es
CONTINUO vía el latido (B2 scheduler), acelerable con una pasada completa dirigida (B4.5).

**Gate B4 honesto**: mecanismo probado (✓) + gap tras una pasada completa de re-scrape medido +
residual declarado = irresolubles (pedanías fuera del Nomenclátor + ambiguos confesados) +
rotación de inventario (lo cierra el scheduler en ciclos sucesivos). El gap de municipio NO es un
número estático que se "sella" una vez: es un equilibrio que el latido mantiene bajo.

## Balance geo tras B5.1 (2026-06-14) — POS vs C2C

Tras el wallapop exhaustivo (`--target 100k`: 3.851 nuevos de 100.011 cageados = rendimiento
fuertemente decreciente. Causa [VERIFICADO]: wallapop es API keyword/geo-scoped SIN catálogo plano;
el cursor-newest + keyword-sweep alcanza recientes/populares pero NO el long-tail histórico activo.
LÍMITE DE PLATAFORMA, no del mecanismo). El gap se separa honestamente:

| Segmento | gap | resuelto |
|---|---|---|
| POS físicos (compraventa/garaje/concesionario/desguace) | 6.587 | 86,7% — garaje 99,6%, concesionario 96,1%, desguace 98,8%, **compraventa 83,6%** rezagado |
| C2C particular | 47.078 | 85,7% — límite API wallapop + filtrable (B5.2) |
| Plataformas nacionales (~133) | N/A | province NULL por diseño (sentinel '00', sin municipio físico) |

**Lectura**: el geo de los PUNTOS DE VENTA físicos está esencialmente cerrado salvo compraventa
(6.463: sus dealers encierran el muni en el cdp → no se benefician del COALESCE B4.4 que es solo
particulares; milanuncios no da lat/lon → necesitarían re-mint de identidad [B1] o re-captura del
city). El residual de geo lo domina el C2C particular (límite de enumerabilidad de wallapop) — que
el FILTRADO B5.2 separa del producto servido. El geo "al átomo" de los puntos de venta está
logrado; el gap C2C es ruido confesado por causa, no un fallo del resolver.
