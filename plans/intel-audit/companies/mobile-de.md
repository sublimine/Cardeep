# Auditoría atómica — mobile.de (Adevinta)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> **mobile.de** = mayor marketplace de vehículos de Alemania (turismos, vehículos comerciales, motos, autocaravanas, e-bikes) **+ una capa de datos/inteligencia de mercado** para concesionarios (price-rating, Inserats-Analyse, Market Health, m.Q Market Intelligence) y para anunciantes/OEM.
> Web principal: https://www.mobile.de/ · Portal de anunciantes/insights: https://advertising.mobile.de/ · API pública para vendedores/integradores: https://services.mobile.de/ · Owner: **Adevinta** (https://adevinta.com/brand/mobile-de/).
> Fecha auditoría: **2026-06-30**. Método: WebSearch + WebFetch; **descarga directa (curl) y minería** de la documentación oficial de la **Seller API** (`services.mobile.de/docs/seller-api.html`, 1,67 MB → texto plano), del **XSD** `seller-ad-1.1.xsd`, de la **Search API** (facets), y del **PDF "m.Q Market Intelligence & Insights" Sep-2025** (pdftotext → métricas atómicas, definición del Market Health y de la Inserats-Analyse); prensa especializada alemana (kfz-betrieb/Vogel, autohaus.de, auto-motor-und-sport, AUTO BILD), AIM Group (automotive intelligence), Adevinta (brand/press/history) y agregadores (Kompass, RocketReach, PitchBook).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).
>
> **Nota de alcance sobre el subdominio "portal-insights"**: **VERIFICADO que el host existe** — `portal-insights.mobile.de` resuelve vía **CloudFront** (IPs 143.204.55.x) pero responde **HTTP 302 → https://www.mobile.de/** para tráfico anónimo (Cloudfront-Function "generated-by-CloudFront"). Es decir, es el **portal de insights del concesionario detrás de login** (no servible sin autenticación de Händler). El contenido funcional equivalente públicamente documentado es la **Inserats-Analyse / Analyse-Übersicht del Händlerbereich** y el reporte **m.Q**. Marco como [V] la existencia del host y como [A] que su contenido = el dashboard de insights del dealer.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **mobile.de** (también escrito "Mobile.de") | [V] |
| Categoría | **Marketplace de clasificados de vehículos** (C2C + B2C/B2B) **con capa de datos/inteligencia**: price-rating algorítmico, valoración, análisis de inserción (Inserats-Analyse), Market Health index, market intelligence (m.Q), financiación, leasing, publicidad/lead-gen | [V] |
| Owner / grupo | **Adevinta** (mobile.de es subsidiaria de Adevinta) | [V — adevinta.com/brand/mobile-de + AIM] |
| Propiedad última | **Adevinta fue tomada private en 2024 por un consorcio liderado por Permira + Blackstone** (con **General Atlantic** y **TCV**, y rollover de **Schibsted** y **eBay**); oferta **NOK 115/acción**, **~€14.000M enterprise value**; vehículo de adquisición en footer Adevinta: **"Aurelia Netherlands TargetCo B.V."** | [V — Adevinta press + PE Insights + footer] |
| Estado actual mobile.de | **Sigue siendo subsidiaria de Adevinta (2025-2026)**; reportada **preparación de IPO de mobile.de para 2026**; el consorcio trocea Adevinta (venta de activos españoles a **EQT por ~€2.000M**, 2025; desinversión de Willhaben/Austria) y se concentra en **Alemania, Francia, Benelux** | [V — PYMNTS + Private Equity Wire + AIM] |
| HQ | **Albert-Einstein-Ring 26, 14532 Kleinmachnow-Dreilinden** (Brandeburgo, área de Berlín; "Europarc Dreilinden") | [V — Kompass + Impressum mobile.de] |
| Entidad legal | **mobile.de GmbH** | [V — Impressum + Kompass] |
| Fundación | **1996** | [V — Adevinta brand + múltiples] |
| CEO | **Ajay Bhatia** (CEO de mobile.de) | [V — Adevinta press; histórico MD Malte Krüger 2021] |
| Empleados | **~484** (Kompass/RocketReach; orden de magnitud) | [A — secundario, no oficial] |
| Facturación mobile.de | **No desglosada públicamente** (consolida dentro de Adevinta; Adevinta grupo ~€1.800M ingresos) | [A — GAP, ver Gaps] |
| Liderazgo de producto datos | **Julia Lüders — Staff Product Lead, Pricing & Insights** (responsable de la Inserats-Analyse / price-rating) | [V — m.Q Sep-2025] |
| Pila técnica | Web + apps; **CDN CloudFront/AWS**, imágenes en `img.classistatic.de` (infra compartida de clasificados del grupo); API REST en `services.mobile.de` (media type `application/vnd.de.mobile.api+json`) | [V — headers + docs API] |

### Posicionamiento [V]
"**Deutschlands größter Fahrzeugmarkt**" (el mayor mercado de vehículos de Alemania). Se presenta como **"one-stop shop"**: comprar, vender, financiar, asegurar y (hasta jul-2025) transaccionar online. Para el concesionario añade la promesa **data-driven**: "Auf Basis von mehr als zwei Millionen Marktwerten täglich schätzen wir den Wert deines Autos" (estimamos el valor con **>2 millones de valores de mercado diarios**).

### Clientes objetivo [V]
1. **Particulares** (compra/venta C2C, valoración, financiación).
2. **Concesionarios / Autohändler** (clientes de pago; inserción, Inserats-Analyse, price-rating, Werbemanager, gestión de reputación).
3. **OEM, marcas, anunciantes** (publicidad display + market intelligence m.Q vía `advertising.mobile.de`).
4. **Integradores / TSP (Transfer Service Providers)** y **"Self-Uploading Dealers"** (consumidores de la Seller API).
5. **Partners del "Data Partner Program"** (acceso a Quality-Check API y datos avanzados).

---

## 2. Cobertura

### Geográfica [V/A]
- **Núcleo: Alemania** (mercado doméstico; el mayor de DE). [V]
- **Listados y búsqueda transfronterizos**: la Search API soporta filtro **`country` (ISO 3166-1 alpha-2)** y `ambit.zipcode`/`ambit.radius`, e incluye vendedores de varios países europeos (p.ej. AT, NL, BE, IT, dealers fronterizos). El alcance de inventario es **DACH + EU occidental**, no solo DE. [V — Search API]
- Versiones de idioma: **DE** (principal) y **EN** (`/en/…`). [V]
- No es un operador pan-europeo de marcas múltiples como su matriz Adevinta; **mobile.de = marca única, mercado alemán**. [A]

### Escala (cifras vivas) [V]
- **~1,6 millones de anuncios** (media anual 2025, Adevinta brand) · **1,680 Mio. de Inserate en jun-2025** (m.Q). [V — dos fuentes]
- **>140 millones de visitas/mes** (media ene-dic 2025). [V — Adevinta brand]
- **Bestand histórico**: 665.633 vehículos listados oct-2023 (+12% interanual). [V — Autobarometer]
- **Demanda**: Anrufe + Mails (llamadas + emails) **+20,6% H1-2025 vs H1-2024**. [V — m.Q]
- **Más de 2 millones de valores de mercado procesados al día** (motor de valoración/price-rating). [V — mobile.de]

### Scope de vehículos [V]
- **Tipos**: **Pkw (turismos)**, **Nutzfahrzeuge (vehículos comerciales/industriales ligeros)**, **Motorräder (motos)**, **Wohnmobile (autocaravanas)**, **e-Bikes**, además de remolques/maquinaria en categorías especiales (la Search API tiene facets de carretillas, ejes, horas de operación, etc.). [V — Search API + autohaus]
- **Condición**: **NEU (nuevo)** y **GEBRAUCHT (usado)** (`condition` = NEW/USED). [V]
- **El price-rating algorítmico solo aplica a coches usados** (excluye nuevos y dañados — ver reasons `Price_Rating_Only_Cars`, `Price_Rating_No_New_Cars`, `Price_Rating_Vehicle_Is_Damaged`). [V]

---

## 3. Productos + campos atómicos

mobile.de combina **(A)** el objeto de anuncio (todos los atributos de vehículo), **(B)** productos de **datos/inteligencia** sobre ese anuncio (price-rating, statistic, quality-check, rating del dealer, Inserats-Analyse, Market Health), **(C)** market intelligence agregada (m.Q, Preisbarometer/Autobarometer), **(D)** valoración para particulares, y **(E)** monetización (financiación, leasing, publicidad/lead-gen). Detalle atómico abajo.

### 3.A Objeto de anuncio / atributos de vehículo (Seller API ad + Search API facets) [V]
Campos atómicos por anuncio (creación/lectura vía Seller API; búsqueda vía Search API):

**Identificación / metadatos:** `mobileAdId`, `mobileSellerId`, `creationDate`, `modificationDate`, `renewalDate`, `internalNumber`, `uploadSticky`, `export`, `reserved`.
**Clasificación:** `vehicleClass` (Car/Motorbike/Motorhome/…), `category` (Limousine, OffRoad/Geländewagen, SUV, Kombi…), `make`, `model`, `modelDescription`, `modelRange`, `trimLine`, `condition` (NEW/USED), `usageType` (p.ej. CLASSIC).
**Identidad técnica:** `vin`, `kba` (**HSN** + **TSN**, claves oficiales alemanas Hersteller-/Typschlüssel), `schwackeCode`.
**Antigüedad / uso:** `firstRegistration` (YYYY-MM), `constructionYear`, `constructionDate`, `mileage` (km), `numberOfPreviousOwners`, `generalInspection` (HU/TÜV), `exhaustInspection` (AU), `monthsTillInspection`.
**Motorización:** `power` (kW), `cubicCapacity` (ccm), `gearbox`, `fuel` (DIESEL/BENZIN/HYBRID/ELEKTRO/…), `drivingMode` (cadena/correa, motos).
**EV / electrificación:** `batteryCapacity` (kWh), `battery` (alquilada/propia), `range` (autonomía), `chargingTime`, `chargingTimeFast`, **`batteryStateOfHealth.documentUrl`** (certificado de salud de batería adjunto).
**Emisiones / consumo:** `emissionClass` (EURO), `emissionSticker` (Umweltplakette), `emissions` (CO2 combinado, `co2Class`), `consumptions` (city/suburban/rural/highway/combined), `costModel` (fuelPrice, tax, co2Costs, consumptionCosts, timeFrame).
**Carrocería / aspecto:** `exteriorColor`, `manufacturerColorName`, `metallic`, `interiorColor`, `interiorType` (leather/alcantara/…), `doors`, `seats`.
**Equipamiento (features booleanas):** `abs`, `airbag`, `alloyWheels`, `centralLocking`, `climatisation`, `electricHeatedSeats`, `electricWindows`, `esp`, `immobilizer`, `navigationSystem`, `parkingAssistants`, `powerAssistedSteering`, `speedControl` (cruise), `radio` (DAB), `daytimeRunningLamps`, `headlightType`, `sunroof` (Schiebedach), `feature[]` / `excludeFeature[]` (set extendido).
**Condición jurídica/estado:** `damageUnrepaired`, `accidentDamaged`, `roadworthy`, `fullServiceHistory`.
**Comercial / precio:** `price` → `dealerPriceGross`, `consumerPriceGross`, `dealerPriceNet`, `consumerPriceNet`, `vatRate`, `vatable`, `type`, `currency`; `deliveryPeriod`, `deliveryDate`, `countryVersion`, `warranty`, `dealerHomepage`, `description`, `videoUrl`, `nationalDelivery` (radius/period/fee/info).
**Media:** `images[]` (ref, hash; URLs en `img.classistatic.de`), **`auto-panorama`** (imágenes 360º interior + exterior), `imageCount`.
**Vendedor / geo (Search):** `sellerType` (DEALER / FOR_SALE_BY_OWNER), `customerNumber`, `customerId`, `country`, `ambit.zipcode`, `ambit.radius`.
**Comerciales/industriales (Search facets):** `liftingCapacity` (kg), `installationHeight` (mm), `operatingHours`, `loadCapacity` (kg), `axles`, `licensedWeight` (kg), `wheelFormula`.
**e-Bike (Search facets):** `numberOfGears`, `frameShape`, `frameHeight`, `frameMaterial`, `wheelSize`, `batteryCapacityWh` (Wh), `weight` (kg), `bikeGearType`, `motorPosition`, `batteryPosition`.

### 3.B Price-Rating — el "semáforo" de precio (producto estrella de datos) [V]
Sistema algorítmico (desde **2017**; **rehecho con IA el 30-jun-2025**) que clasifica el **precio del anuncio** frente al mercado. API: `GET /…/ads/:id/price-rating` y `POST /…/ads/price-rating` (preview antes de publicar). Campos atómicos de la respuesta:
- **`label`** — la clasificación del anuncio, una de **5 categorías**: **`VERY_GOOD_PRICE`** (Sehr guter Preis), **`GOOD_PRICE`** (Guter Preis), **`REASONABLE_PRICE`** (Fairer Preis), **`INCREASED_PRICE`** (Erhöhter Preis), **`HIGH_PRICE`** (Hoher Preis). [V — enum; labels alemanes [A] mapeo ampliamente reportado]
- **`labelRanges[]`** — para ESE vehículo, el **rango de precio en EUR de cada una de las 5 categorías**: `{label, from, to}`. Ej. real del doc: VERY_GOOD 13.600–16.200 · GOOD 16.200–17.300 · REASONABLE 17.300–19.200 · INCREASED 19.200–21.400 · HIGH 21.400–23.100. → permite al dealer ver **exactamente cuánto bajar para subir de categoría**.
- **`NO_RATING`** + **`reasons[]`** — sin rating; 11 reason codes: `Price_Rating_Not_Possible_Invalid_Input`, `Price_Rating_Only_Cars`, `Price_Rating_Vehicle_Is_Damaged`, `Price_Rating_Repaired_Damage`, `Price_Rating_Not_Roadworthy`, `Price_Rating_No_New_Cars`, `Price_Rating_No_Old_Cars`, `Price_Rating_Differing_Price_Too_High`, `Price_Rating_Differing_Price_Too_Low`, `Price_Rating_Not_Possible_Little_Data`, `Price_Rating_Evaluation_In_Progress` (+ `unsupported_make_model`). [V]
- **Refinamiento por imágenes**: el preview acepta referencias de fotos; con imágenes la respuesta es **más precisa** (matching de modelrange/trimline contra reference data) y tarda **~4 s**. [V]

### 3.C Ad Statistic — rendimiento por anuncio [V]
`GET /…/ads/:id/statistic` devuelve **4 métricas atómicas** por anuncio:
- **`impressions`** (apariciones/visualizaciones del anuncio), **`parkings`** (veces "aparcado"/guardado en la lista de seguimiento), **`emails`** (contactos por email), **`calls`** (llamadas). [V]

### 3.D Quality-Check — calidad del anuncio (Data Partner Program) [V]
`GET /…/ads/quality-check` (lote por `adIds`) y `…/:id/quality-check`. Evalúa imágenes, descripción y completitud de atributos. Campos:
- **`overallQualityCheck`** (score 0–100), `status` (PROCESSED).
- **`imageQuality`**: `score` + por imagen `{baseUrl, status, vehicleVisibility.result, vehicleFocus.result, overlays.result}` con `reason` en fallo (`vehicle_not_in_focus`, `overlays_present`, vehículo no visible). → IA de visión que verifica **coche visible / enfocado / sin overlays/marcas de agua**.
- **`imageQuantity`**: `{score, min: 10, optimal: 25, current}` (nº de fotos; mínimo 10, óptimo 25).
- **`descriptionLength`**: `{score, min: 500, optimal: 1000, current}` (caracteres; mín 500, óptimo 1000).
- **`attributeCoverage`**: `{score, optimal: 23, current, attributes:{covered[], missing[]}}` — lista de atributos cubiertos vs ausentes (de un set "óptimo" de **23**: modelRange, trimLine, power, climatisation, exteriorColor, interiorType, airbag, emissionSticker, emissionClass, doors, seats, batteryCapacity, range, chargingTime, chargingTimeFast, parkingAssistants, fuel, category, make, model, modelDescription, condition, deliveryPeriod). [V]

### 3.E Dealer Rating — reputación del concesionario [V]
`GET /…/rating/overview` (requiere cuenta **Gold**+). Agregado de reseñas de compradores:
- **`score`** (global, p.ej. 4.4), **`totalActiveRatings`** (nº de valoraciones activas), **`advice`** (Beratung), **`friendliness`** (Freundlichkeit), **`responseTime`** (Reaktionszeit), **`recommendation`** (% recomendaría), **`vehicleAsDescribed`** (% vehículo como se describió). [V]
- Endpoints relacionados: `…/rating/ratings`, `…/rating/ratings/:id` (reseña individual), `PUT …/comment` (responder), `…/rating/invites` + `POST …/invites/:adId` (invitar a valorar). [V]

### 3.F Inserats-Analyse — "Listing Analysis" (dashboard de inteligencia del dealer; el corazón de "portal-insights") [V]
Herramienta **KI-gestützt** lanzada/relanzada **sep-2025** (Julia Lüders, Staff Product Lead Pricing & Insights). "Trae todos los datos de performance y precio de un coche a un solo lugar" combinando el análisis de vehículo + el Marktvergleich. Cinco bloques de datos atómicos:
1. **Performance-Kennzahlen** — los KPIs del anuncio: **Aufrufe (views), E-Mails, Anrufe (calls), Parkungen (guardados)** (= los 4 campos del endpoint `statistic`). Para reacción rápida a tendencias de demanda. [V]
2. **Marktpreis + Preisbewertung** — la IA calcula el **mobile.de Marktpreis** del vehículo (considerando el influjo de cada característica en el precio) y muestra **qué ajuste es necesario para alcanzar la siguiente categoría de Preis-Label** (p.ej. de GOOD a VERY_GOOD). [V]
3. **Position in den Suchergebnissen** — **posición/ranking del vehículo en los resultados de búsqueda** y **en qué página** aparece; optimización de placement. (Futuro: ajustar la búsqueda para analizar la posición con más detalle.) [V]
4. **60-Tage-Verkaufswahrscheinlichkeit** — **probabilidad de venta en los primeros 60 días de stock (Standtage)**: la chance de que el vehículo se venda en sus primeros 60 días. Permite medidas tempranas. [V]
5. **Marktvergleich** — **vehículos similares de la competencia en una tabla**, comparables hasta por **~100 atributos**; elimina la propia investigación de competencia; resalta puntos comunes relevantes para el precio; **análisis a escala nacional (deutschlandweit)**. [V — m.Q + autohaus + kfz-betrieb]
- **Roadmap declarado**: Suchkriterienanalysen (análisis de criterios de búsqueda) + recomendaciones de acción más detalladas (Handlungsempfehlungen). [V]

### 3.G Market Health Index — índice de mercado (oferta/demanda) [V]
**"Der mobile.de Market Health ist ein indexierter Wert, der Angebot (Inserate) und Nachfrage (Leads) auf mobile.de ins Verhältnis zueinander setzt"** — índice que pone en relación **oferta (anuncios)** y **demanda (leads)**. **Ø = 100 puntos**; **<100 = la categoría rinde por debajo de la media; >100 = por encima**. Se publica desagregado por (m.Q, H1-2025, con variación interanual):
- **Antriebsform (motorización)**: Diesel, Benzin, **Hybrid 141 (+20%)**, **Elektro 95 (+22%)**.
- **Fahrzeugklasse (segmento)**: **Mittelklasse 135 (+18%)**, **Geländewagen 133 (+29%)**, **Kompaktklasse 96 (+23%)**, **Kleinwagen 65 (+21%)**, **SUV 66 (+21%)**.
- **Fahrzeugalter (antigüedad)**: **Bis 1 Jahr 33 (+17%)**, **1–3 Jahre 64 (+14%)**, **3–5 Jahre 119 (+23%)**, **5–10 Jahre 137 (+34%)**, **>10 Jahre 146 (+22%)**.
- **Gesamtmarkt +22,0%** vs año anterior. [V]

### 3.H m.Q "Market Intelligence & Insights" — informe de mercado (anunciantes/OEM) [V]
Reporte periódico (trimestral/semestral; ed. Sep-2025) vía `advertising.mobile.de`. Métricas atómicas observadas:
- **Inserate (oferta)** total: **1,680 Mio.** (jun-2025). **Durchschnittspreis (precio medio)** en mobile.de ~**€28.000–30.000**; **−0,7% H1-2025 vs H1-2024**. **Nachfrage (Anrufe+Mails) +20,6%**. [V]
- **Market Health** por motorización/segmento/edad (ver 3.G). [V]
- **Top-5 Suchanfragen por Ausstattung (equipamiento más buscado)**: **Schiebedach 13,9%**, **Standheizung 7,0%**, **Apple CarPlay ~5,0%/4,5%**, **Ambiente-Beleuchtung 2,6%**. [V]
- **Suchanfragen por Fahrzeugtyp**: **Limousine 33,8%**, otros (Kombi/SUV) 44,8% / 21,4%. [V]
- **Cuotas de mercado por motorización** y **Durchschnittsalter (edad media ~10 años)** por segmento; **EV/ICE share** por clase; **Pkw-Jahresleistung (km/año medios)** y **Bestand der Pkw-Flotte (parque, millones)**. [V]
- **Händlerklima (sentiment del concesionario)** H1-2025 (encuesta B2B Market Research). [V]
- Más del **60% de los usuarios de mobile.de** [contexto de adopción de leasing/financiación]. [V]

### 3.I Preisbarometer / "Autobarometer" — barómetro mensual de precios (público/prensa) [V]
Estadística **mensual** de mercado de VO: **Durchschnittspreis** (€33.137 ej. nov-2023), **Kilometerstand medio** (52.600 km), **Standzeit/Tage hasta venta** (**96 días** medios), **Bestand** y variación interanual, y **variación de precio por categoría** (Vans +2,2%, Kleinwagen −0,7%, Mittel-/Oberklasse y Premium a la baja…). [V]

### 3.J Fahrzeugbewertung — valoración para particulares ("Was ist mein Auto wert?") [V/A]
Tasación online gratuita (`/verkaufen/auto/bewertung/`, `/wertermittlung/`) y vía **integración Schwacke** (`/verkaufen/bewertung-schwacke-liste/`). Input: **marca, modelo, primera matriculación, kilómetros, equipamiento/versión**; Output: **valor estimado / rango de precio de mercado** (motor: >2M valores de mercado/día). [V existencia + metodología; campos exactos del formulario [A] — página bloquea bots]

### 3.K Monetización del dealer / lead-gen (no "datos" puros pero parte del portal) [V]
- **Werbemanager** (Advertising Manager): extiende anuncios a **Instagram/Facebook**; **Social Plus** (auto-promoción en redes de vehículos con alta Standzeit + analytics); **Google Performance Max** (YouTube, Gmail, red Google). [V]
- **Booking Assistant / Feature Settings** (`/feature-settings`): productos de visibilidad **`topOfPage`** (arriba de resultados) y **`eyeCatcher`** (resalte), por `mobileAdId`. [V]
- **Direct Offer** (`/ads/:id/direct-offer`) + push notifications → **+14% más consultas**. [V]
- **Leasing rate** (`/ads/:id/leasing`), **financiación**, formularios de contacto que capturan **financiación, prueba de manejo, leasing**. [V]
- **Cost Control** (en Feature Settings) y **Quality-Check** como guía de optimización. [V]

---

## 4. Metodología y fuentes de datos [V]
- **100% datos propios del marketplace**: oferta = **~1,6–1,68M anuncios** vivos; demanda = **leads reales** (Aufrufe, Parkungen, E-Mails, Anrufe) medidos por anuncio. El **Market Health** es literalmente **oferta(Inserate) / demanda(Leads)** normalizado a Ø=100. [V]
- **Motor de valoración / price-rating**: **>2 millones de valores de mercado procesados al día**; el **mobile.de Marktpreis** se calcula por configuración exacta (make/model/modelRange/trimLine + equipamiento) ponderando **el influjo de cada característica en el precio**, con **efectos regionales y estacionales**. Comparación contra el conjunto de vehículos equivalentes del mercado. [V — mobile.de + prensa]
- **IA de visión (Quality-Check)**: clasifica cada foto por **visibilidad del vehículo, enfoque y presencia de overlays**; el price-rating preview mejora con imágenes. [V]
- **60-Tage-Verkaufswahrscheinlichkeit**: modelo predictivo sobre probabilidad de venta en los **primeros 60 Standtage** (no publica la fórmula). [V existencia; método interno = A]
- **Granularidad de identificación**: **HSN/TSN (KBA)**, **VIN**, **SchwackeCode** → enlaza con catálogos oficiales alemanes y con Schwacke (valoración). [V]
- **Reset de algoritmo 30-jun-2025** (nueva IA de price-rating): cambió clasificaciones de muchos anuncios → controversia de concesionarios (ver Gaps). [V]
- **Frecuencia**: statistic/price-rating **en tiempo real/diario**; Market Health y m.Q **semestral/trimestral**; Preisbarometer **mensual**. [V]

---

## 5. Entrega
- **Web/Apps de marketplace** (`www.mobile.de`): ficha de vehículo con price-rating; área de cuenta. [V]
- **Händlerbereich (portal del concesionario)** rediseñado + **portal de insights tras login** (`portal-insights.mobile.de`, 302 para anónimos): Bestandsübersicht, **Analyse-Übersicht**, Inserats-Analyse, Nachfrageanalyse, Performance, Werbemanager. [V host; A contenido exacto]
- **Seller API REST** (`services.mobile.de`): CRUD de anuncios, imágenes, auto-panorama, **price-rating**, **statistic**, **quality-check**, **rating**, **battery-health-certificate**, **leasing**, **direct-offer**, multi-locations, feature-settings, self-upload-account. Media type `application/vnd.de.mobile.api+json`. **Sandbox + SwaggerUI** disponibles. [V]
- **Search API** (`services.mobile.de/docs/search-api.html`): búsqueda con decenas de facets; paginación (page.size máx 100; tope 2.000 anuncios); refdata de clasificación. [V]
- **Ad Stream API**: **eventos push** (create/update/delete de anuncios) con payload completo de Ad + Seller → feed para integradores. [V]
- **Acceso**: Seller API para **TSP (Transfer Service Providers)** y **Self-Uploading Dealers**; **Quality-Check + datos avanzados solo vía "mobile.de Data Partner Program"** (contactar Strategic Partner Manager). [V]
- **Informes**: **m.Q** (PDF, `advertising.mobile.de`), **Preisbarometer mensual** (prensa/newsroom). [V]
- **Plugins de terceros** (ecosistema): conectores Shopware/WordPress para la API. [V]

---

## 6. Precio
- **Marketplace dealer = suscripción mensual por paquetes**. Paquetes renombrados (04-10-2023) de Kompakt/Komfort/Premium → **Bronze, Silber, Gold, Platin**. [V]
- **Modelo de tarifa**: **Sockelbetrag (base) + Aufschlag (recargo)** dependiente del **precio medio mensual del inventario anunciado**. Ej.: dealer pequeño con **11–15 vehículos/mes** paga **€389,99–€649,99/mes** según paquete. [V — bikeundbusiness/kfz-betrieb]
- **Servicios add-on**: "Direktlink zur eigenen Homepage" subió **€50 → €200/mes** (incluido en Platin); productos de visibilidad (topOfPage/eyeCatcher), Werbemanager, Social Plus, Google PMax. [V]
- **Tier de cuenta condiciona features de API**: p.ej. la gestión de **rating** del dealer requiere **cuenta Gold+**. [V]
- **Particulares**: lista de precios de inserción propia (`/service/pricelistConsumer`). [V existencia]
- **m.Q / market intelligence**: producto de marketing para anunciantes (descarga); price tag no público. [A]
- **Importe exacto de cada paquete y del Data Partner Program = no totalmente público** (cambia con subidas periódicas — "mobile.de erhöht Preise"). [V tendencia; importes completos = GAP]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. mobile.de separa **placement de consumidor** (ficha) de **placement de dealer** (Inserats-Analyse / Analyse-Übersicht). Mapeo sección → dato:

### Ficha de vehículo (consumidor) — listing detail [V/A]
- **Badge de Preisbewertung** junto al precio: etiqueta de color (Ampelsystem) "**Sehr guter Preis / Guter Preis / Fairer Preis / Erhöhter Preis / Hoher Preis**". [V que existe desde 2017 en cada anuncio de VO]
- **Barra/escala de precio de mercado**: visualización del rango (los `labelRanges` from→to) con la **posición del precio del coche** dentro del espectro de las 5 categorías. [V dato; layout exacto = A inferido del API labelRanges]
- Specs del vehículo (make/model/modelDescription/firstRegistration/mileage/power/fuel/gearbox…), equipamiento, **HU/TÜV**, **emisión/CO2/consumo**, **fotos + auto-panorama 360º**, **certificado de salud de batería** (EV) con **health + garantía en km y meses**, reputación del vendedor. [V]
- **Filtro de garantía de batería** en la búsqueda (buyers filtran por condición de garantía de batería). [V — AIM]

### Inserats-Analyse (pantalla del dealer, por vehículo) [V]
Tool único que reúne, por anuncio:
- **Bloque Performance-Kennzahlen**: Aufrufe · E-Mails · Anrufe · Parkungen.
- **Bloque Marktpreis + Preisbewertung**: mobile.de Marktpreis + label actual + **delta para subir de categoría**.
- **Bloque Position in Suchergebnissen**: ranking + página en resultados.
- **Bloque 60-Tage-Verkaufswahrscheinlichkeit**: % de probabilidad de venta a 60 días.
- **Tabla Marktvergleich**: vehículos similares de la competencia (hasta ~100 atributos).

### Analyse-Übersicht (Händlerbereich, nivel cartera) [V]
- Vista de **toda la cartera de anuncios** ordenada por **qué listings necesitan atención** (placement débil o baja probabilidad de venta) → priorización de acción. [V]

### Nachfrageanalyse (demanda) [V]
- Panel de **accesos/Zugriffe a cada anuncio** y tendencias de engagement por listing. [V]

### Quality-Check (calidad del anuncio) [V]
- Score global + sub-scores **imágenes (cantidad/calidad), longitud de descripción, cobertura de atributos** con listas **covered/missing** → checklist de mejora del anuncio. [V]

### m.Q Market Intelligence (informe agregado) [V]
- **Market Health** por motorización/segmento/edad (gráficos de puntos vs Ø=100); **Top-Suchanfragen por equipamiento y tipo**; precio medio y tendencias; Händlerklima. [V]

### Preisbarometer (informe mensual de mercado) [V]
- Precio medio, **Standzeit (días hasta venta)**, kilometraje medio, Bestand y variación por categoría. [V]

### Valoración particular (Fahrzeugbewertung) [V/A]
- Formulario (marca/modelo/matriculación/km/equipamiento) → **valor estimado + rango**. [V flujo; layout = A]

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Price-rating de mercado embebido en CADA anuncio de VO**, con **rangos EUR explícitos de las 5 categorías** (`labelRanges`) → el dealer (y el comprador) ven el umbral exacto de cada nivel. Pocas plataformas exponen el **delta-para-subir-de-categoría**.
- [V] **Market Health Index propio** (oferta-anuncios / demanda-leads, Ø=100) desagregado por motorización, segmento y edad — un termómetro oferta/demanda **basado en leads reales del propio marketplace**, no en estimaciones editoriales.
- [V] **60-Tage-Verkaufswahrscheinlichkeit** por vehículo (predicción de venta a 60 Standtage) — análoga al "days-to-sell/MDS" de INDICATA/vAuto pero **nativa del marketplace líder de DE**.
- [V] **Datos de demanda de primera parte a escala**: views/parkings/emails/calls por anuncio (endpoint `statistic`) + **>140M visitas/mes** → señal de demanda que un proveedor de datos puro (Schwacke, DAT) no posee.
- [V] **Quality-Check con IA de visión** (visibilidad/enfoque/overlays de fotos) + benchmarks publicados (≥10 fotos / óptimo 25; descripción 500/1000 car.; 23 atributos óptimos).
- [V] **Inteligencia EV nativa**: certificado de salud de batería adjuntable + **filtro de garantía de batería** para compradores + facets kWh/range/charging.
- [V] **Identificación oficial alemana** (HSN/TSN/KBA, SchwackeCode, VIN) integrada en el anuncio.
- [V] **Ecosistema de monetización del lead** (Werbemanager, Social Plus, Google PMax, Direct Offer +14%, Booking Assistant topOfPage/eyeCatcher) — convierte el dato en visibilidad pagada.
- [V] **API + Ad Stream (eventos) + Data Partner Program** → entrega tanto a TSPs/dealers como a partners de datos.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Discontinuó la compra de coche online (jul-2025)** ("hits the brake on online car purchases") → ya **no es marketplace transaccional/checkout**; vuelve a ser generación de leads. Retroceso vs su propia ambición "one-stop shop".
- [V] **price-rating solo VO turismo** (no nuevos, no dañados/no roadworthy, no motos/comerciales) → 11 reason codes de exclusión.
- [V] **Cobertura = Alemania (DACH/EU occidental por listados)**, no un índice pan-europeo multi-país tipo Indicata/Autovista; sin Norteamérica/LatAm/APAC.
- [V] **Sin valoración de valor residual (RV) forward / curvas de depreciación** como producto (eso es Schwacke/DAT/Autovista; mobile.de se apoya en Schwacke para la tasación). No publica RV%/forecast.
- [A] **Sin historial de siniestros/propietarios/odómetro certificado por VIN** tipo Carfax/autoDNA (declara accidentDamaged/owners como atributos del anuncio, no provenance verificada de terceros).
- [A] **Sin datos OEM de reparación/SMR** (tiempos de mano de obra, precios de piezas, TecDoc).
- [V] **Importes de precio no totalmente públicos** (paquetes Bronze/Silber/Gold/Platin con base+recargo variable; Data Partner Program por contacto). Facturación de mobile.de no desglosada (consolida en Adevinta).
- [V] **Quality-Check y datos avanzados gated** tras el **Data Partner Program** (no abiertos).
- [A] **No publica la fórmula** del Market Health ni de la 60-Tage-Verkaufswahrscheinlichkeit (índices/scores propietarios, método interno).
- [V] **`portal-insights.mobile.de` no es servible públicamente** (302 a la home): el dashboard de insights del dealer vive **tras login**; el detalle atómico hubo que reconstruirlo del m.Q + API + prensa.
- [A] **TCO/coste total de propiedad** no es un producto declarado (sí `costModel` parcial: combustible/impuesto/CO2 por anuncio).
- [V] **Controversia de confianza**: el reset de IA del price-rating (30-jun-2025) degradó ratings de muchos dealers → críticas (percepción de opacidad/inconsistencia).

---

## 10. Fuentes (URLs)
- https://www.mobile.de/ — marketplace, ficha, price-rating, tipos de vehículo, "Deutschlands größter Fahrzeugmarkt".
- https://adevinta.com/brand/mobile-de/ — owner Adevinta, fundación 1996, **~1,6M anuncios**, **>140M visitas/mes**, tipos (cars/commercial/motorcycles/e-bikes), one-stop shop.
- https://services.mobile.de/docs/seller-api.html — **(fuente primaria atómica)** endpoints + modelos: **price-rating** (enum 5 labels + labelRanges + 11 NO_RATING reasons + preview con imágenes), **statistic** (impressions/parkings/emails/calls), **quality-check** (overall + imageQuality vehicleVisibility/vehicleFocus/overlays + imageQuantity 10/25 + descriptionLength 500/1000 + attributeCoverage 23 covered/missing), **rating/overview** (score/advice/friendliness/responseTime/recommendation/vehicleAsDescribed), **battery-health-certificate** (PDF/JPG/PNG ≤10MB → batteryStateOfHealth.documentUrl), feature-settings (bookingAssistant topOfPage/eyeCatcher), leasing, direct-offer, auto-panorama, self-upload-account, Data Partner Program [curl + minería de 1,67 MB].
- https://services.mobile.de/docs/search-api.html — **facets atómicos** (classification, price.min/max, mileage, firstRegistrationDate, fuel, power, gearbox, feature/excludeFeature, batteryCapacity, emissionSticker, monthsTillInspection, sellerType, country, ambit.radius, imageCount, facets comerciales y e-bike, sort, paginación tope 2000).
- https://services.mobile.de/schema/seller/seller-ad-1.1.xsd — envelope del anuncio (ad/images/highlights/visibilities/feature) [curl].
- https://services.mobile.de/docs/ad-stream.html — Ad Stream (eventos push create/update/delete con payload Ad+Seller).
- https://advertising.mobile.de/fileadmin/user_upload/Mobile/Zielgruppe/mde-mQ-0225-DE-SCREEN.pdf — **m.Q Market Intelligence Sep-2025** (fuente primaria): **Market Health** (definición oferta/demanda Ø=100; tablas por motorización/segmento/edad), **Inserats-Analyse** (5 bloques: Performance-Kennzahlen, Marktpreis+Preisbewertung, Position in Suchergebnissen, 60-Tage-Verkaufswahrscheinlichkeit, Marktvergleich; Julia Lüders), Inserate 1,68M, precio medio −0,7%, demanda +20,6%, Top-Suchanfragen [curl + pdftotext].
- https://www.kfz-betrieb.vogel.de/mobilede-bietet-jetzt-ki-marktanalysen-a-c7c6585fa10a791cdac87fe4355772ab/ — KI-Marktanalysen, **Markt-Vergleich hasta 100 atributos**, nuevo Händlerbereich, Nachfrageanalyse, Social Plus, Google PMax.
- https://www.kfz-betrieb.vogel.de/mobile-startet-neue-ki-preisbewertung-haendler-kritisieren-massiv-a-c4fe1adc1d6e37b153260d25c4b5890a/ — **nueva IA de price-rating 30-jun-2025**, Ampelsystem desde 2017, críticas de dealers.
- https://www.autohaus.de/nachrichten/autohandel/herbst-update-bei-mobile-de-ki-tools-und-neuer-haendlerbereich-3566666 — Herbst-Update: KI-Tools, Händlerbereich, Bestandsübersicht, Nachfrageanalyse, Direct Offer **+14%**, atributos para motos/Wohnmobile/Nutzfahrzeuge.
- https://aimgroup.com/2025/03/17/mobile-de-unveils-new-dealer-tools/ — market price analysis, **60-day sale probability**, real-time competitive positioning, "Sale Probability", inventory list rediseñada, analysis overview (demand + performance), **battery certificates (health + garantía km/meses)**, **filtro de garantía de batería**, +20% leads.
- https://aimgroup.com/2025/07/17/mobile-de-updates-its-ai-based-price-valuation-system/ — enhanced AI price-valuation (rollout 30-jun-2025).
- https://aimgroup.com/2025/07/25/mobile-de-hits-the-brake-on-online-car-purchases/ — **discontinúa compra de coche online** (jul-2025).
- https://www.auto-motor-und-sport.de/verkehr/mobile-autobarometer-zu-gebrauchtwagenpreisen-standzeiten-und-mehr/ — **Autobarometer/Preisbarometer**: Durchschnittspreis €33.137, **Standzeit 96 días**, km medio 52.600, Bestand 665.633 (+12%), variación por categoría.
- https://www.mobile.de/verkaufen/auto/bewertung/ + /wertermittlung/ + /verkaufen/bewertung-schwacke-liste/ — valoración para particulares (>2M valores/día; integración Schwacke) [WebFetch bloqueado → vía search snippets].
- https://www.mobile.de/service/pricelistdealer + /en/service/pricelistConsumer + /en/service/imprint — listas de precios e Impressum (mobile.de GmbH, Albert-Einstein-Ring 26, Kleinmachnow).
- https://www.bikeundbusiness.de/artikel/gemischte-ansichten-zum-neuen-preismodell-bei-mobilede + autohaus.de "neue Preisrunde" — modelo de precios Bronze/Silber/Gold/Platin, base+recargo, ej. €389,99–649,99/mes, Direktlink €50→€200.
- https://adevinta.com/press-releases/permira-and-blackstone-announce-voluntary-offer-…-nok-115… + https://www.generalatlantic.com/investment/adevinta/ + https://pe-insights.com/blackstone-and-permira-backed-adevinta-… — take-private (Permira/Blackstone/General Atlantic/TCV, NOK 115, ~€14B; "Aurelia Netherlands TargetCo B.V.").
- https://www.pymnts.com/news/ipo/2025/adevinta-considers-ipo-sale-german-auto-marketplace-mobile-de/ + https://www.privateequitywire.co.uk/eqt-acquires-adevintas-spanish-marketplaces-…/ — **IPO mobile.de 2026** considerada; venta de activos españoles a EQT (~€2B).
- https://adevinta.com/press-releases/adevinta-appoints-ajay-bhatia-as-ceo-of-mobile-de/ — CEO **Ajay Bhatia**.
- Kompass / RocketReach (mobile.de GmbH, Kleinmachnow-Dreilinden, ~484 empleados) — HQ + tamaño [secundario].
- Verificación de host: `curl -I https://portal-insights.mobile.de/` → **HTTP/1.1 302 → https://www.mobile.de/** (CloudFront) + `nslookup` → 143.204.55.x → **subdominio EXISTE, gated tras login**.

> Verificación: identidad/owner con ≥2 fuentes (Adevinta + PE press + AIM). Campos atómicos de price-rating/statistic/quality-check/rating **[V] leídos directamente de la documentación oficial de la Seller API** (JSON de ejemplo + modelos). Inserats-Analyse y Market Health **[V] del PDF m.Q oficial**. Mapeo de labels alemanes y layout exacto de la barra de precio en la ficha marcados **[A]** (no inventados). Importes de precio completos, facturación de mobile.de y fórmulas de los scores = **GAP** declarado.
