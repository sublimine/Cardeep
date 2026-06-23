# Estado del Arte — Descubrimiento exhaustivo del 100% de puntos de venta de coches en España

Fecha: 2026-06-20. Investigación con WebSearch/WebFetch reales. Cada afirmación marcada [VERIFICADO] (leída en fuente) o [ASUMIDO] (inferencia/cálculo).

6 vectores complementarios. Ninguno cubre el 100% solo; la cobertura total = unión + dedup cruzado (Vector 6 como colapsador final).

---

## VECTOR 1 — Marketplace-as-census (vendedores profesionales por plataforma)

| Plataforma | Directorio público | Enumeración | Defensa | Estado |
|---|---|---|---|---|
| autocasion.com | SÍ `/profesional/{prov}` | sitemap `stock.xml` = 2.981 URLs + `ref{N}` | abierta | Diana óptima |
| motor.es | SÍ `/concesionarios/` (24 pág) | crawl paginado slugs | abierta | Diana fuerte |
| coches.com | NO (404 raíz) | IDs secuenciales `D{N}` (~D232–D2933) | abierta | Diana fuerte por ID |
| ocasionplus.com | SÍ `sitemap.concesionarios.xml` = 138 | sitemaps por marca | abierta | Diana óptima (cadena) |
| flexicar.es | SÍ `/delegaciones-flexicar/` (+200) | sitemap delegaciones+stock; VIN | abierta | Diana fuerte (cadena) |
| autoscout24.es | SÍ `/profesionales/` | `regional/{prov}/{ciudad}` slug | Akamai | TIER-1 |
| coches.net | SÍ `/concesionarios/{prov}/` | sitemap-index tras muro | DataDome | TIER-1 |
| wallapop | NO índice HTML | API v3 geo lat/long+radio | API abierta | Vía API |
| milanuncios | parcial (`/api/` oculto) | — | DataDome (Adevinta) | TIER-1 |
| carplus.es | SÍ `/donde-estamos/` | crawl dinámico | abierta | Cadena pequeña |
| clicars.com | NO (1 centro online) | ID numérico + `__NEXT_DATA__` | abierta | Ya en runbook (t0_open) |
| automoviles.es | NO (landing vacía) | — | — | Descartar hoy |

### Endpoints/repos clave
- autocasion: `https://www.autocasion.com/uploads/sitemap-ng/stock/stock.xml` (2.981 dealers, lastmod diario). API interna `/api/partial/ads/*`.
- motor.es: `https://www.motor.es/concesionarios/` + `/concesionarios/{provincia}/{N}`. Sitemap VO `https://www.motor.es/xml/sitemap_vo.xml`.
- coches.com: perfiles `https://www.coches.com/concesionario-{slug}/D{ID}/` — ID secuencial enumerable.
- ocasionplus: `https://www.ocasionplus.com/sitemap.concesionarios.xml` (138 sedes).
- flexicar: `https://www.flexicar.es/delegaciones-flexicar/` (+200, VIN embebido = dedup ideal).
- wallapop API: `https://api.wallapop.com/api/v3/general/search` (keywords, latitude, longitude, distance_in_km, category_id). Repo: https://github.com/toniprada/wallapop-users-scraper
- coches.net repos: https://github.com/hmeleiro/cochista · https://github.com/lorenzovigo/APIcoches
- milanuncios repos: https://github.com/lreyp/Scraping-Milanuncios-Coches · https://github.com/mondeja/milanuncios
- autoscout24 repos: https://github.com/lorenzoelia/autoscout24_scraping · guía https://scrapfly.io/blog/posts/how-to-scrape-autoscout24

Orden de ataque: (1) abiertas sin defensa: autocasion, motor.es, ocasionplus, flexicar, coches.com, clicars. (2) wallapop API. (3) TIER-1 Camoufox+IP ES: coches.net, autoscout24.es, milanuncios.

---

## VECTOR 2 — Barrido geo-grid (APIs de mapas)

### Google Places API (New)
- [VERIFICADO] Cap duro: 20 resultados/página × 3 páginas = **60 máx/consulta**. Radio Nearby máx 50 km. `next_page_token` requiere 2–5 s.
- [VERIFICADO] Place Types: `car_dealer`, `car_repair`. https://developers.google.com/maps/documentation/places/web-service/place-types
- Pricing (Woosmap, estructura SKU oficial): Nearby/Text Search Pro $32/1K (free 5.000/mes); Place Details Essentials $5/1K. https://www.woosmap.com/blog/google-maps-api-pricing-breakdown
- Vencer el cap: grid adaptativo (quadtree) — subdividir solo celdas que devuelven ≥60.
- Repos: https://github.com/gbrlpzz/maps_poi_extractor · https://github.com/apify-alexey/google-maps-radar-search · https://github.com/gosom/google-maps-scraper · https://github.com/Danzigerrl/Google-Maps-Scraper

### OpenStreetMap / Overpass
- [VERIFICADO] Tags: shop=car, shop=car_repair, shop=car_parts, shop=tyres, amenity=fuel. https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar
- [VERIFICADO] taginfo global: shop=car = 163.288 objetos, shop=car_repair = 288.366 (mundial). https://taginfo.openstreetmap.org/api/4/tag/stats?key=shop&value=car
- [PENDIENTE] taginfo no filtra por país; ejecutar Overpass `out count` contra `area["ISO3166-1"="ES"]` para cifra España.
- Endpoint: https://overpass-api.de/api/interpreter
- Query patrón (España):
```
[out:json][timeout:180];
area["ISO3166-1"="ES"][admin_level=2]->.es;
(nwr["shop"="car"](area.es); nwr["shop"="car_repair"](area.es);
 nwr["shop"="car_parts"](area.es); nwr["shop"="tyres"](area.es););
out center tags;
```

### Overture Maps (places theme)
- [VERIFICADO] >50M POIs, >2.000 categorías (incl. automotive), Parquet en S3, consultable con DuckDB por bbox. Coste 0/llamada, sin cap.
- `s3://overturemaps-us-west-2/release/<REL>/theme=places/type=place/*.parquet`. https://docs.overturemaps.org/guides/places/
- CLI: `overturemaps download --bbox=...`. https://github.com/OvertureMaps/data

### Esquema teselado España (~505.000 km²)
3 capas en cascada: (1) base gratis Overture+Overpass (semilla); (2) grid adaptativo Google 5 km radius (~15.000 celdas reales sobre tierra, subdivisión solo urbano ≥60); (3) Text Search por provincia para long-tail no tipificado ("desguace", "compraventa"). Coste Google estimado ~$1.000 una corrida nacional [ASUMIDO/cálculo]. Dos bboxes (península+Baleares / Canarias).
Otras fuentes abiertas: HERE Places, Foursquare OSS Places (Parquet gratis).

---

## VECTOR 3 — Dorking por municipios

- [VERIFICADO] 8.132 municipios (INE, 1-ene-2025). Tabla maestra GitHub: https://raw.githubusercontent.com/codeforspain/ds-organizacion-administrativa/master/data/municipios.csv
- INE relación municipios: https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031
- datos.gob.es: https://datos.gob.es/es/catalogo/ea0042823-relacion-de-municipios-y-sus-codigos-por-provincias

### Motores programables
| Motor | Free | Nota | URL |
|---|---|---|---|
| Google CSE | 100/día | **Cerrado a nuevos clientes** (→Vertex AI 2027); 100 result/query | https://developers.google.com/custom-search/v1/overview |
| Bing Search API | — | **RETIRADA 11/08/2025** | https://learn.microsoft.com/en-us/lifecycle/announcements/bing-search-api-retirement |
| SerpAPI | 250/mes | Google ES (google_domain=google.es) | https://serpapi.com/ |
| Serper.dev | 2.500/mes | Más barato a volumen | https://serper.dev/ |
| Brave API | $5 cred/mes | Free eliminado feb-2026 | https://brave.com/search/api/ |
| SearXNG self-host | ilimitado | **Caballo de batalla coste-cero** | https://github.com/searxng/searxng |

Veredicto: SearXNG self-hosted (masivo) + Serper.dev (calidad Google de respaldo). Google CSE descartado.

### Plantillas dork (iterar {municipio}×8.132, {provincia}×50)
`concesionario {municipio}` · `compraventa coches {municipio}` · `coches segunda mano {municipio}` · `desguace {provincia}` · `site:.es ("compraventa" OR "concesionario") {municipio}` · excluir agregadores `-site:coches.net -site:wallapop.com` para cazar dominios propios (long-tail).

### Descubrimiento dominios .es
- [VERIFICADO] No hay zone file público .es (Red.es no lo publica).
- Certificate Transparency crt.sh (PostgreSQL `psql --host=crt.sh --port=5432 --username=guest certwatch`, filtro `name_value ILIKE '%concesionario%'`). Cliente: https://github.com/knqyf263/crtsh
- Common Crawl URL index (filtro `.es` + paths `/vehiculos`, `/ocasion`, `/stock`).

---

## VECTOR 4 — Registros oficiales y localizadores OEM

### BORME (altas/bajas de empresas)
- [VERIFICADO] API datos abiertos BOE (gratis, XML+JSON): `https://www.boe.es/datosabiertos/api/borme/sumario/{aaaammdd}`. Sección I = constitución/disolución.
- libreborme: https://github.com/PabloCastellano/libreborme · parser: https://github.com/PabloCastellano/bormeparser
- API libreborme (solo búsqueda por nombre, NO filtra CNAE): https://libreborme.readthedocs.io/es/latest/api/
- Para filtrar por CNAE hay que ingerir BORME crudo con bormeparser y construir índice propio.

### CNAE automoción
- [VERIFICADO] 4511 venta automóviles ligeros (núcleo), 4519 otros vehículos, 4520 mantenimiento/reparación, 4531/4532 recambios. https://www.cnae.com.es/actividades.php?grupo=G
- [VERIFICADO] INE DIRCE: solo datos AGREGADOS (conteo por provincia×CNAE), no microdatos. Útil para dimensionar meta de cobertura. https://www.ine.es/jaxiT3/Tabla.htm?t=301
- Comerciales (de pago, listan empresas por CNAE+provincia con dirección): Axesor https://www.axesor.es/listado-empresas.aspx · eInforma https://www.einforma.com/empresas/CNAE.html

### Asociaciones (bajo valor — sin directorio abierto)
- FACONAUTO (~2.018 concesionarios oficiales): https://www.faconauto.com/
- GANVAM: afiliados tras login, no scrapeable. https://ganvam.es/afiliados/

### Localizadores OEM (ALTA prioridad para oficiales)
~35-40 marcas. Patrón: buscador con XHR/JSON detrás (lat/lng, dirección, CP, tel). Capturar endpoint por marca con Playwright network.
- VW: https://www.volkswagen.es/es/buscador-de-concesionarios.html
- Renault: https://www.renault.es/concesionarios.html
- Toyota: https://www.toyota.es/concesionarios
- [ASUMIDO] JSON exacto no capturado aún — acción pendiente: red Playwright por marca.

### DGT talleres (cruce validación)
- [VERIFICADO] Relación talleres Libro Taller Electrónico (filtrable provincia/municipio, sin CSV visible): https://www.dgt.es/conoce-la-dgt/con-quien-trabajamos/talleres/

Recomendación: OEM locators (oficiales) + BORME/bormeparser CNAE 45xx (long-tail + delta altas/bajas) + DGT talleres (cruce geo).

---

## VECTOR 5 — Descubrimiento recursivo en grafo

### Grupos verificados
- Grupo Quadis (+100 puntos): https://www.quadis.es/concesionarios
- Grupo Huertas (+50): https://www.grupohuertas.com/instalaciones/ — fichas URL semántica `/instalaciones/ficha-de-detalle/...-{marca}-{ciudad}` (auto-clasificable por path).
- Salvador Caetano (+50, incl. Carplus): https://caetano.es/quienes-somos/
- [ASUMIDO/pendiente] Bertolín, Grupo Marcos, Gom3z, Auto Sweden, Sabadell d'Cars: existen, URL listado no verificada.

### Heurística anchors (nodo expansor)
`instalaciones`, `concesionarios`, `delegaciones`, `centros`, `nuestras sedes`, `dónde estamos`, `red de concesionarios`, `puntos de venta`, `ficha-de-detalle`.

### Herramientas crawl
- Scrapy CrawlSpider + LinkExtractor (`restrict_css` sobre bloque de red): https://docs.scrapy.org/en/latest/topics/link-extractors.html
- Katana: https://github.com/projectdiscovery/katana (agrupa patrones repetidos de URL)
- Photon: https://github.com/s0md3v/Photon

### Common Crawl (grafo a escala)
- Web Graph host/PLD (saltar de dealer a grupo matriz a hermanos): https://commoncrawl.org/web-graphs
- CDX Index API (todas las URLs de un host): `https://index.commoncrawl.org/CC-MAIN-<YYYY-WW>/cdx?url=*.dominio&output=json`. Colecciones: https://index.commoncrawl.org/collinfo.json . Cliente: https://github.com/ikreymer/cdx-index-client

### Datos estructurados
- JSON-LD `AutoDealer` (extiende LocalBusiness): parsear `<script type="application/ld+json">`, buscar `"@type":"AutoDealer"` → confirma dealer + extrae name/address/geo/telephone. Múltiples bloques = lista de sucursales geolocalizada. Cobertura parcial (Huertas no lo servía).

Pipeline: robots/sitemap → JSON-LD → Scrapy restrict_css → CC CDX → CC Web Graph.

---

## VECTOR 6 — Long-tail invisible (reconstruir dealer desde anuncios sueltos)

Problema = entity resolution / record linkage. Pipeline 5 capas.

### 1. Record linkage
- **Splink** (motor principal, Fellegi-Sunter probabilístico, no supervisado, TF-adjusted, escalable, auditable): https://github.com/moj-analytical-services/splink
- recordlinkage (diseñar blocking): https://github.com/J535D165/recordlinkage
- dedupe (active learning, humano en bucle): https://github.com/dedupeio/dedupe
- Blocking por: últimos 7 dígitos tel / dominio email / CP / trigramas nombre. Scoring fuzzy (Jaro-Winkler/Levenshtein) + pesos FS. TF adjustment evita colapsos falsos por dato hipercompartido.

### 2. Validación señales ES
- CIF/NIF: python-stdnum `stdnum/es/cif.py` (`is_valid()`, `split()`): https://github.com/arthurdejong/python-stdnum — CIF válido repetido = señal de colapso más fuerte.
- Teléfonos: phonenumbers (E.164 +34, `PhoneNumberMatcher(texto,"ES")` extrae del cuerpo): https://github.com/daviddrysdale/python-phonenumbers

### 3. Geocodificación inversa + clustering
- Nominatim self-hosted (gratis, sin límite; pública ~1 req/s): https://wiki.openstreetmap.org/wiki/Geocoding
- Photon (typo-tolerant), Pelias (BD descargable). 
- Clustering: DBSCAN métrica haversine (radio 50–150 m). La coordenada es señal, no prueba (polígonos industriales).

### 4. OCR fotos
- Texto/rótulos/teléfonos: PaddleOCR (más preciso) https://github.com/PaddlePaddle/PaddleOCR · EasyOCR https://github.com/JaidedAI/EasyOCR · Tesseract (CPU rápido) https://github.com/tesseract-ocr/tesseract
- ALPR matrículas: fast-alpr (MIT, ONNX, entrenable ES): https://github.com/ankandrew/fast-alpr — misma matrícula en 2 anuncios = mismo coche = mismo vendedor (señal potente; matrícula = dato personal RGPD, hashear).

### 5. Profesional vs particular
Features: mismo tel/email/CIF en N anuncios (discriminante de mayor señal), CIF válido, lenguaje comercial (financiación/garantía/IVA — LLM local barato), volumen stock, dirección geo repetida, logo recurrente. Clasificador simple (logreg/SVM/GBM). Ref shape: https://arxiv.org/pdf/1805.00464

Encaja con el dedup-overlay reversible ya en el repo: lo extiende con señales tel/email/CIF/geo/foto + motor probabilístico Splink.

---

## Acciones pendientes de verificación (huecos confesados)
1. Overpass `out count` real España (cifra OSM por país).
2. Capturar XHR/JSON exacto de cada localizador OEM con Playwright network.
3. Confirmar slug vivo dataset BORME en datos.gob.es (404 en URL probada).
4. Slugs categorías automotive Overture; páginas wiki car_parts/tyres/fuel.
5. URLs listado Bertolín/Marcos/Gom3z/Auto Sweden/Sabadell d'Cars.
6. coches.com: redirect ID-solo `D{N}` e ID máximo; estructura paginación coches.net (tras DataDome).
7. HERE Places y Foursquare OSS a fondo.
