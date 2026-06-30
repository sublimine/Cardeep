# Auto Trader UK — Auditoría atómica

> Slug: `auto-trader-uk` · Subdominio cardeep: **portal-insights** · Región: **Reino Unido** (+ Irlanda histórica)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (marketing del propio vendedor sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato de varias páginas), `[NO-VERIFICADO]`, `[VERIFICADO por ausencia]`.
> **Qué es Auto Trader UK:** el **mayor marketplace digital de automoción del Reino Unido** Y, a la vez, **la mayor casa de inteligencia de precio de coche usado de UK**. Su valor para cardeep no es el clasificado, sino el **motor de valoración + métricas de mercado en vivo** que destila de su propio inventario (≈450k listings/día + ≈800k–1,9M vehículos monitorizados/día) y que sirve por **API (Autotrader Connect)**, por **Portal de retailer** y por **tasador de consumidor**. Es el competidor directo de eVA/Manheim (de hecho **eVA consume su pricing** desde nov-2025 — ver `manheim-uk.md`) y el equivalente UK funcional a vAuto/Cox en US.
> **Relación con `manheim-uk.md` / `cox-automotive.md`:** Auto Trader es **socio y rival** de Cox: comparten el JV **Dealer Auction** (Cox 51% / Auto Trader 49%) y Cox embebe el pricing retail de Auto Trader en eVA. Pero Auto Trader es **entidad cotizada independiente** (LSE: AUTO, FTSE 100). Este informe audita su set de inteligencia **propio**.
> Sitios/marcas: `autotrader.co.uk` (consumidor + tasador `/cars/valuation`), `autotrader.co.uk/partners/retailer` (retailer/producto), `portal.autotrader.co.uk` (Portal del dealer), `developers.autotrader.co.uk` (API Autotrader Connect), `plc.autotrader.co.uk` (corporativo/investor), `help.autotrader.co.uk` (centro de ayuda/doc capacidades), `autotraderinsight-blog.co.uk` (blog de inteligencia), `trade.autotrader.co.uk` (productos trade).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **Autotrader** / **Auto Trader** (rebranding tipográfico a "Autotrader" en uso reciente) | autotrader.co.uk `[VERIFICADO]` |
| Entidad cotizada | **Autotrader Group plc** (antes **Auto Trader Group plc**), **LSE: AUTO**, constituyente **FTSE 100** | plc.autotrader.co.uk; Wikipedia; LSE `[VERIFICADO ×2]` |
| Cambio de razón social | De "Auto Trader Group plc" → **"Autotrader Group plc"** el **14-ene-2026** | WebSearch (Wikipedia/registro) `[PARCIAL]` |
| Company number (holding) | **09439967** (Autotrader Group plc) | plc.autotrader.co.uk/our-history `[PARCIAL]` |
| Entidad operativa | **Autotrader Limited** (antes Auto Trader Limited), **registered number 03909628** | footer autotrader.co.uk `[VERIFICADO]` |
| HQ / domicilio social | **No.3 Circle Square, 3 Hawkshaw Street, Manchester, M1 7BL, UK** (+ oficina en Londres) | footer autotrader.co.uk; our-history `[VERIFICADO ×2]` |
| Regulación | **Autotrader Limited autorizada y regulada por la FCA**, firm reference **735711** (credit broking + insurance introductions; no es prestamista) | footer autotrader.co.uk `[VERIFICADO]` |
| Fundación | **1977** como **Thames Valley Trader** (revista regional de clasificados de motor) | plc our-history; Wikipedia `[VERIFICADO ×2]` |
| Fundador(es) | **John Madejski** (fundador principal; "tras una visita a EE. UU."); fuentes secundarias citan también **Paul Gibbons y Peter Taylor** como co-fundadores | plc our-history (Madejski); WebSearch (co-fundadores) `[VERIFICADO Madejski / PARCIAL co-fundadores]` |
| Hitos | **1983** Guardian Media Group entra · **1988** rebrand a "Auto Trader" · **1995** cobertura UK+Irlanda · **1996** primer sitio web · **2000** se forma **Trader Media Group** · **2007** ingreso digital = ingreso print · **jun-2013** cesa la edición impresa (100% digital) · **24-mar-2015** **IPO en LSE** (cap. ~£2bn) | plc our-history; Wikipedia `[VERIFICADO ×2]` |
| Adquisiciones | **2017** Motor Trade Delivery (MTD) · **2018** JV **Dealer Auction** con Cox Automotive · **2019** **KeeResources** (£25,3m) · **2020** AutoConvert · **2022** **Autorama** (leasing coche nuevo, hasta £200m) | plc our-history; Travers Smith; AIM Group `[VERIFICADO ×2]` |
| Posición declarada | **"UK's largest digital automotive marketplace"**; **>75%** de todos los minutos en marketplaces de automoción UK; **10×** el competidor de clasificados más cercano | plc FY25; Genesys case study `[VERIFICADO ×2]` |

**Categorías de producto:** (1) **Marketplace de clasificados** (consumidor: buscar/comprar/vender coche usado y nuevo, leasing); (2) **Tasador de consumidor** (`/cars/valuation`, gratis); (3) **Inteligencia de valoración para retailer** = **Autotrader Valuations** (Retail / Trade / Part-exchange / Private) + **Trended Valuations** (histórico 6m + forecast 6m); (4) **Métricas de vehículo** = **Retail Rating**, **Price Position**, **Days to Sell**, **Confidence of Sale**; (5) **Inteligencia de mercado** = **Market Insight** (supply/demand/market condition) + **Retail Price Index** (índice mensual público); (6) **Gestión de forecourt** = **Retail Accelerator** (sustituye a i-Control) + **Retail Check** (con **Retail Back calculator**); (7) **Datos/specs** = taxonomía de vehículo + technical data + features (KeeResources); (8) **Provenance/historial** = Vehicle Check; (9) **Plataforma de integración** = **Autotrader Connect** (suite de APIs); (10) **Co-Driver** (IA: descripciones + orden de fotos); (11) **Leasing coche nuevo** (Autorama).

**Cliente objetivo:** **retailers/dealers** (franquiciados e independientes) = núcleo del negocio (modelo ARPR); **fabricantes (OEM)** y **agency/new car**; **leasing/flota** (vía KeeResources/Autorama); **partners tecnológicos** (DMS/software, vía Autotrader Connect); y **consumidores** (tasador + marketplace, gratis, como motor de audiencia). (Fuentes: plc FY25; partners/retailer; developers.autotrader.co.uk. `[VERIFICADO]`)

---

## 2. Cobertura

- **Geografía:** **Reino Unido** = núcleo absoluto. Cobertura histórica **UK + Irlanda** (desde 1995). El set de inteligencia (valoraciones, RPI, Retail Rating) es **UK-céntrico** (matrícula VRM, libros UK, mercado UK). `[VERIFICADO]`
- **Nuevo vs usado:** **USADO** es el núcleo de la inteligencia (valor de mercado en vivo). Cubre **coche nuevo** (stock nuevo, brand campaigns, agency model) y **leasing de coche nuevo** (Autorama). El tasador y las valoraciones se centran en **usado**; el "nearly new"/brand new queda **sin price label**. `[VERIFICADO]`
- **Tipos de vehículo:** **cars, vans (LCV), bikes, motorhomes, caravans, trucks, farm, plant, electric bikes** (canales de búsqueda dedicados). La inteligencia profunda (valoraciones/Retail Rating) cubre sobre todo **cars y vans**; taxonomía API incluye **Car, Van, Truck, Bike, Plant, Farm**. `[VERIFICADO ×2]`
- **Escala (FY25, año fiscal a mar-2025):**
  - **14.013 forecourts de retailer** de media anunciando (2024: 13.783; +2%); **≈80% de los retailers de automoción de UK**; **>13.500 retailer partners**. `[VERIFICADO ×2]`
  - **449.000 coches** en stock vivo de media (2024: 445.000); **≈450.000 vehículos** anunciados (privado+trade) de media. `[VERIFICADO]`
  - **81,6M visitas cross-platform/mes** (2024: 77,5M; +5%); **≈65M visitas de consumidor/mes**; **>75%** de minutos en marketplaces de automoción; **557M minutos/mes**; **11M usuarios únicos/mes** + **5M followers/subscribers**. `[VERIFICADO ×2]`
- **Frescura del dato (clave):**
  - **Retail Price Index / data science:** monitoriza **≈800.000 vehículos/día**, **116.000 updates/día**, **39.000 altas-bajas/día**, **≈450.000 trade listings/día** + datos de forecourt. `[VERIFICADO]`
  - **Retail Accelerator:** monitoriza **>1,9M vehículos/día**, **90.000 updates/día**, **19.000 altas-bajas/día**. `[VERIFICADO]`
  - **Market Insight:** monitoriza **>1,3M vehículos** y **>20.000 cambios de precio/día**. `[VERIFICADO ×2]`
- **Naturaleza del dato:** **transacción no garantizada / dato de anuncio real** — Auto Trader observa el **precio pedido (asking)**, cambios de precio, retiradas y velocidad de venta de su propio inventario (el mayor de UK) + datos de forecourt de retailers conectados. **No** es subasta (eso es Dealer Auction/Manheim); es **el termómetro del retail forecourt UK**. `[VERIFICADO]`
- **Aval institucional:** la **ONS (Office for National Statistics)** usa los datos de listings de Auto Trader para **transformar las estadísticas oficiales de inflación (CPI) de coche usado** de UK — sello de credibilidad del dato. `[VERIFICADO ×2]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **Tasador de consumidor** (`/cars/valuation`) | Valoración gratis instantánea por matrícula | Private sale value + Part-exchange value | ~6 |
| **Autotrader Valuations** (retailer) | Valor de mercado en vivo (Connect/Portal) | Retail / Trade / Part-exchange / Private + ajustadas | ~10 |
| **Trended Valuations** | Histórico 6m + forecast 6m | curva valor + +30/+60/+90d + 6m | ~8 |
| **Price Indicator** | Etiqueta de precio en el anuncio | Lower/Great/Good/Fair/Higher + bandas | ~7 |
| **Retail Rating** | Probabilidad/velocidad de venta 1–100 | score 1–100 personalizado por ubicación | ~5 |
| **Retail Check** | Workbench de pricing por vehículo | Retail Val + Price Position + Days to Sell + Retail Back | ~9 |
| **Retail Accelerator** | Gestión de forecourt + alertas | alertas pricing/ageing/valuation + estrategia | ~12 |
| **Market Insight** | Inteligencia macro supply/demand | Supply / Demand / Market Condition / Days to Sell | ~8 |
| **Retail Price Index** | Índice de precio mensual público | like-for-like % + mix % por segmento | ~6 |
| **Vehicle data / Taxonomy** (KeeResources) | Specs, features, taxonomía | technical data + standard/optional features | ~40 |
| **Vehicle Check** | Provenance/historial | write-off/stolen/finance/mileage/owners | ~12 |
| **Autotrader Connect** | Suite de APIs (entrega) | 15 prod + 3 beta APIs | (transversal) |
| **Co-Driver** | IA: descripciones + fotos | AI description + image ordering | ~3 |

### 3.1 Tasador de consumidor (`autotrader.co.uk/cars/valuation`)

> Captura web verificada (Playwright). Heading **"Value my car"** / "In the know, in 10 seconds". Input: **Registration** (matrícula) → "Get my free instant valuation" (luego solicita mileage). Claim: **"We look at millions of vehicles"**, **"independent valuation that is only driven by data"**, **"Over 40 years of experience… since 1977"**, Trustpilot **4,6/5**.

| Campo / output atómico | Definición | Fuente |
|---|---|---|
| **Registration (VRM)** | Input: matrícula del vehículo | snapshot /cars/valuation `[VERIFICADO]` |
| **Mileage** | Input: kilometraje (paso 2) | snapshot + WebSearch `[VERIFICADO]` |
| **Private sale value** | Valor de venta privada en Autotrader | theusedcarguy; collections/value-my-car `[VERIFICADO ×2]` |
| **Part-exchange value** | Valor de toma a cambio (trade-in al dealer) | theusedcarguy; collections/value-my-car `[VERIFICADO ×2]` |
| **Factores incluidos** | **age, mileage, spec, optional extras** | snapshot /cars/valuation `[VERIFICADO]` |
| **Factores excluidos** | modifications, full service history, desirable colour, no damage (↑) · significant wear & tear, parts not working, lots of previous owners, gaps in service history/no MOT (↓) | snapshot /cars/valuation `[VERIFICADO]` |

### 3.2 Autotrader Valuations (motor de valor para retailer — NÚCLEO de inteligencia)

> **El producto que cardeep debe estudiar con más detalle.** Es el valor de mercado **en vivo** servido por **Autotrader Connect** (API) y en **Portal**. Doc verbatim de la capacidad **"Current Valuations"** (help.autotrader.co.uk, snapshot Playwright): disponible vía **Vehicles API, Stock API, Valuations API**. Disponible para todos los retailers desde **ene-2024** (antes solo en herramientas Portal).

**Tipos de valor (definición verbatim):**
| Campo atómico | Definición (verbatim) | Fuente |
|---|---|---|
| **Retail** | "what the vehicle is worth if listed on Autotrader by a dealer. Assumes condition is 'retail ready'." | help Current Valuations `[VERIFICADO]` |
| **Trade** | "what the vehicle is worth if listed for trade between dealers. Effectively the value excluding any margin." | help Current Valuations `[VERIFICADO]` |
| **Private** | "what the vehicle is worth if listed by a private seller on Autotrader" | help Current Valuations `[VERIFICADO]` |
| **Part-exchange** | "what the vehicle is worth if used by a consumer as part-exchange for another vehicle" | help Current Valuations `[VERIFICADO]` |

**Capacidades de la valoración (verbatim):**
- **Vehicle lookup valuations** (por VRM) · **In-stock valuations** (sobre stock del dealer). `[VERIFICADO]`
- **Adjusted valuations:** **Condition-adjusted valuation** · **Feature-adjusted valuation** · **Expected price indicator rating** (qué price label resultaría a un precio dado). `[VERIFICADO]`
- **Variantes VAT** por cada valor: `amountGBP`, `amountExcludingVatGBP`, `amountNoVatGBP` (para VI/commercial). `[VERIFICADO]`
- **Price indicator rating bands** (`upper`/`lower` price values) = los umbrales £ de cada banda de price indicator. `[VERIFICADO]`

### 3.3 Trended Valuations (histórico + forecast)

> Lanzado 2024; incluido en packages desde el evento de precios de abril-2024 (palanca "product" del ARPR). Muestra **lo que un vehículo ha valido en los últimos 6 meses** y **cómo se prevé que cambie hasta 6 meses adelante**.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Historic valuation (6m atrás)** | Curva de valor retroactiva 6 meses | trended-valuations; help `[VERIFICADO ×2]` |
| **Forecast +30 días** | Predicción a 30d (**precisión ~1%** del valor logrado) | help "how accurate"; insight blog `[VERIFICADO ×2]` |
| **Forecast +60/+90 días** | Predicción a 60–90d (**~3%** hasta 3 meses) | help; insight blog `[VERIFICADO ×2]` |
| **Forecast hasta 6 meses** | Predicción a 6m (**~5%**) | help; insight blog `[VERIFICADO ×2]` |
| **Valuation at Average Days to Sell** | El forecast se plotea también en la fecha de venta media | help "future trended" `[VERIFICADO]` |
| **Inputs del forecast** | current supply & demand · seasonal pricing trends · most recent **OEM new car list price** por derivative · current & historical retailer pricing | help "future trended"; insight blog `[VERIFICADO]` |
| API: `plus30Days` / `plus60Days` / `plus90Days` | Campos de Stock API (trended) | developers.autotrader.co.uk `[VERIFICADO]` |

### 3.4 Price Indicator (etiqueta de precio en el anuncio — patrón placement icónico)

> Captura verbatim de `autotrader.co.uk/price-indicator-info` (Playwright). "We have compared the seller's asking price… with our own Auto Trader valuation, and given it a label." Comparado con coches de cualidades similares: **make, model, age, mileage**.

| Banda | Definición (verbatim) | Fuente |
|---|---|---|
| **Lower price** | "Priced much lower than other similar cars on the market" | price-indicator-info `[VERIFICADO ×2]` |
| **Great price** | "Slightly cheaper than most other similar cars on the market" | price-indicator-info `[VERIFICADO ×2]` |
| **Good price** | "Priced very closely to other similar cars on the market" | price-indicator-info `[VERIFICADO ×2]` |
| **Fair price** | "Only slightly more expensive than most other similar cars" | price-indicator-info `[VERIFICADO ×2]` |
| **Higher price** | "More expensive than most other similar cars, but may have additional benefits" | price-indicator-info `[VERIFICADO ×2]` |

- **Datos usados para el cálculo:** **Make · Model · Age · Fuel type · Optional extras and features** ("data from millions of vehicles"). `[VERIFICADO]`
- **Excluidos:** condición · color · supply/demand local · modificaciones especiales · servicios extra (garantías/finance) · nº de propietarios · service history. `[VERIFICADO]`
- **Sin etiqueta (No Analysis) si:** brand new/nearly new · rare/classic · vendedor privado · precio **<£1.500 o >£70.000** · **>15 años** · **siniestrado (Cat C/D/S/N)** · importado. `[VERIFICADO ×2]`

### 3.5 Retail Rating (probabilidad/velocidad de venta)

> Métrica propietaria: "**how desirable the vehicle is based on demand, supply and days to sell**", en escala **1–100**.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Retail Rating (1–100)** | Predicción de potencial retail del vehículo **si se vende a market value (100% price position)** desde tu ubicación | help "What is Retail Rating"; Retail Check `[VERIFICADO ×2]` |
| **Inputs** | national speed of sale + market conditions (**supply & demand**) + **Average Days to Sell**, **ajustado por ubicación del forecourt** | help; Retail Check `[VERIFICADO ×2]` |
| **Personalización** | live customer demand + live vehicle supply + average days to sell, **por ubicación** | help `[VERIFICADO]` |
| **Independencia del precio** | El Retail Rating **no cambia** al subir/bajar precio (eso afecta a la velocidad real, no al rating) | help `[VERIFICADO]` |

### 3.6 Retail Check (workbench de pricing por vehículo)

> Disponible standalone y embebido (Retail Accelerator, Connect, Portal). "Broad suite of data and metrics… picture of the live retail market a nivel nacional y local."

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Retail Valuation (live)** | Valor retail en tiempo real (Autotrader Valuations) | retail-check; am-online `[VERIFICADO ×2]` |
| **Price Position (%)** | **Precio del vehículo como % de la Retail Valuation** (cómo está fijado vs mercado) | retail-check; insight blog `[VERIFICADO ×2]` |
| **Retail Rating (1–100)** | (ver 3.5) | retail-check `[VERIFICADO]` |
| **Days to Sell / Average Days to Sell** | Estimación de cuántos días tardará en venderse a market value | retail-check; Market Insight `[VERIFICADO ×2]` |
| **Supply & Demand** | Oferta/demanda del vehículo (nacional + local) | retail-check `[VERIFICADO]` |
| **Competitor view / similar stock** | Análisis competitivo de price position vs stock similar en el mercado | retail-check; developers (Competitor View) `[VERIFICADO ×2]` |
| **Retail Back calculator** | **Retail Valuation − costes esperados − target gross margin = precio máximo a pagar** | retail-check `[VERIFICADO]` |

### 3.7 Retail Accelerator (gestión de forecourt + alertas — sustituye i-Control)

> Lanzado abr-2019 reemplazando a **i-Control**. "Optimise your entire forecourt… live alerts… set a strategy for your stock and pricing." Snapshot Playwright verbatim.

| Campo atómico / feature | Definición | Fuente |
|---|---|---|
| **Vista completa de forecourt** | Estado en vivo de cada vehículo del stock | snapshot retail-accelerator `[VERIFICADO]` |
| **Alerta: valuation changes** | Cambios de valoración del vehículo | WebSearch; press `[VERIFICADO]` |
| **Alerta: incorrect pricing** | Precio incorrecto vs mercado | WebSearch; press `[VERIFICADO]` |
| **Alerta: ageing / overage stock** | Stock envejecido fuera de política | WebSearch; snapshot `[VERIFICADO]` |
| **Alerta: fuera de estrategia** | Vehículos que no cumplen la retail strategy | snapshot retail-accelerator `[VERIFICADO]` |
| **Personalised plan** | required stock turn + pricing + overage policy según metas | snapshot retail-accelerator `[VERIFICADO]` |
| **Dynamic performance reporting** | Reporte dinámico de rendimiento / posición competitiva | WebSearch `[VERIFICADO]` |
| **Competitor activity review** | Revisión de actividad de competidores con filtros y vistas de mercado | WebSearch `[VERIFICADO]` |
| **Pricing inclusive de admin fee** | Alertas y precios de estrategia sobre el precio total (incl. admin fee) | WebSearch `[VERIFICADO]` |

### 3.8 Market Insight (inteligencia macro supply/demand — dentro de Vehicle Insight/Portal)

| Métrica atómica | Definición (verbatim) | Fuente |
|---|---|---|
| **Supply** | "national supply for a vehicle on Autotrader over the last 7 days, compared to the supply over the last 6 months" | help "What is Market Insight" `[VERIFICADO ×2]` |
| **Demand** | "national demand… last 7 days vs last 6 months, calculado por consumer activity en vehículos similares" | help `[VERIFICADO ×2]` |
| **Market Condition** | "current market condition for a vehicle, based on supply and demand" | help `[VERIFICADO]` |
| **Days to Sell** | "estimación de días que tardará un vehículo en venderse" | help; Market Insight `[VERIFICADO ×2]` |
| **Filtros / granularidad** | make · model · fuel type · age band; **nacional + regional** | help; partner page `[VERIFICADO ×2]` |
| **Escala del dato** | >1,3M vehículos + >20.000 cambios de precio/día | partner Market Insight `[VERIFICADO ×2]` |

### 3.9 Retail Price Index (índice de precio mensual público)

> Informe mensual público (plc.autotrader.co.uk/news-views/retail-price-index). Aval ONS (CPI UK).

| Métrica atómica | Definición | Fuente |
|---|---|---|
| **Like-for-like price growth (%)** | Cambio de precio % **eliminando el efecto del mix de stock** | plc RPI; WebSearch `[VERIFICADO]` |
| **Mix growth (%)** | % de cambio en el **mix de stock** (tipos de vehículo que entran/salen del mercado) | plc RPI `[VERIFICADO]` |
| **Average price (£)** | Precio medio del mercado retail por periodo/segmento | plc RPI; press `[VERIFICADO]` |
| **Segmentación** | Por **car segments** re-clasificados (resegmentación mar-2020) | plc RPI `[VERIFICADO]` |
| **Base de datos** | ≈800k vehículos/día + 450k trade listings/día + forecourt data | plc RPI `[VERIFICADO]` |

### 3.10 Vehicle data / Taxonomy (specs y features — base KeeResources)

> **KeeResources** (adq. 2019, £25,3m): "su **vehicle taxonomy data** sustenta gran parte de la plataforma core de Auto Trader" (Nathan Coe). Servido vía **Taxonomy API + Vehicles API**. Lista de campos extraída de developers.autotrader.co.uk:

**Identidad/derivative:** registration, VIN, make, model, generation, derivative, **derivativeId**, OEM model code, trim, style, sub-style.
**Technical data:** engineCapacityCC, enginePowerBHP, engineTorqueNM, transmissionType, drivetrain, seats, doors, cylinders.
**Performance:** topSpeedMPH, zeroToSixtyMPHSeconds, zeroToOneHundredKMPHSeconds.
**Emisiones/consumo:** co2EmissionGPKM, emissionClass, fuelEconomyNEDCCombinedMPG, fuelEconomyWLTPCombinedMPG.
**Dimensiones/pesos:** lengthMM, heightMM, widthMM, wheelbaseMM, minimumKerbWeightKG, grossVehicleWeightKG.
**EV:** batteryRangeMiles, batteryCapacityKWH, charge times.
**Garantía:** manufacturerWarrantyStandardDurationYears, manufacturerWarrantyCorrosionDurationYears.
**Features:** standard & optional, con **genericName, category, factoryCodes, rarityRating, valueRating**.
**Taxonomía:** vehicleTypes, bodyTypes, fuelTypes, transmissionTypes, drivetrains, wheelbaseTypes, cabTypes, trims, styles, subStyles. `[VERIFICADO]`

### 3.11 Vehicle Check (provenance / historial)

> Disponible vía Vehicles API ("Full vehicle check") y en flujo de compra. Campos (developers + WebSearch):

`insurance write-off status` (Cat C/D/S/N) · `outstanding finance agreements` · `stolen` · `scrapped` · `imported` · `previousOwners` (nº) · `mileage discrepancy` · `number plate changes` · `vehicle tax` · `CO2` · `import/export records` · `MOT history` (completedDate, testResult, odometerValue, **rfrAndComments** = advisories) · `estimated fuel costs`. `[VERIFICADO]` (proveedor de provenance UK **[NO-VERIFICADO]** — no confirmado si Experian u otro)

### 3.12 Autotrader Connect — campos de Stock/Search/Deals (señales de demanda)

> Además de valoraciones y métricas, las APIs exponen **señales de comportamiento** únicas del marketplace líder:

**Stock API:** stockId, lifecycle state, retailAdverts.price, tradeAdverts.price, **priceIndicatorRating**, advertiserVehicleHighlight (1–3), priceCommentary, **responseMetrics** (advertViews, searchViews, naturalAdvertViews, **paidPPCAdvertViews**), financeOffers, trended (plus30/60/90Days).
**Search API:** soldPrice.amountGBP, **buyerPostcode**, finance (monthlyPriceOption), facets (make/model/fuelType/transmissionType).
**Deals API:** **dealIntentScore**, intent, **localCustomer**, advertSaved, preferences, reservation (status, fee).
**Co-Driver API (IA):** sugerir orden óptimo de imágenes, detectar imágenes faltantes, **generar descripciones de vehículo con IA**. `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Dato propio del mayor marketplace UK:** Auto Trader observa **precio pedido (asking), cambios de precio, retiradas y velocidad de venta real** de su inventario (≈450k listings) + **forecourt data** de retailers conectados. De ahí derivan valoraciones, Retail Rating, Days to Sell, Supply/Demand y el RPI. `[VERIFICADO]`
- **Volumen de observación:** RPI/data science **≈800k veh/día** (116k updates, 39k altas-bajas) + **450k trade listings/día**; Retail Accelerator **1,9M veh/día**; Market Insight **1,3M veh + 20k cambios precio/día**. `[VERIFICADO]`
- **Demanda del consumidor:** señal de **la mayor audiencia de compradores de UK** (81,6M visitas, 65M consumidor, 11M únicos) → demand/Retail Rating no son solo supply-side. `[VERIFICADO]`
- **Taxonomía/specs:** **KeeResources** (data de vehículo, residual values, whole-life costs, forecast) sustenta la taxonomía core. `[VERIFICADO]`
- **Forecast (Trended):** supply/demand + estacionalidad + **OEM new car list price** por derivative + pricing histórico de retailers; precisión declarada 1%/3%/5% (1m/3m/6m). `[VERIFICADO]`
- **Aval externo:** **ONS** transforma el **CPI oficial de coche usado UK** con listings de Auto Trader. `[VERIFICADO ×2]`
- **NO es subasta:** el dato wholesale/hammer real vive en **Dealer Auction** (JV Cox 51/AT 49) y **Manheim** — Auto Trader es **retail-side**. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Tasador de consumidor** | `autotrader.co.uk/cars/valuation` — gratis, por matrícula, private + part-exchange. |
| **Marketplace web/app** | autotrader.co.uk + apps iOS/Android (búsqueda, price indicator, leasing). |
| **Portal de retailer** | `portal.autotrader.co.uk` — stock list con Retail Valuation + Price Position, Vehicle Edit (tab "Valuation and pricing"), Retail Check, Market Insight / Vehicle Insight dashboard, Retail Accelerator. |
| **Autotrader Connect (API)** | `developers.autotrader.co.uk` — **15 APIs producción + 3 beta**: Vehicles, Stock, Search, Taxonomy, Valuations, **Historic Valuations**, **Future Valuations**, **Vehicle Metrics**, Images, Co-Driver, Deals, Messages, Part Exchange, Delivery, Calls + (beta) Finance, Advertisers, Integrations. JSON; sandbox + producción; colección Postman pública. Integración vía partners DMS o directa. |
| **Informe público** | **Retail Price Index** mensual (plc.autotrader.co.uk) + **Autotrader Insight** blog + Market Intelligence Report (LinkedIn). |
| **Integración de terceros** | Connect embebido en DMS/software (p.ej. MotorDesk); **Cox/eVA consume el pricing retail de Auto Trader** (nov-2025). |
| **Leasing** | Autorama (marketplace transaccional de leasing de coche nuevo). |

---

## 6. Precio (modelo + datos descubiertos)

| Concepto | Valor | Fuente / nota |
|---|---|---|
| **Modelo núcleo (retailer)** | **ARPR** — Average Revenue Per Retailer **por mes** | plc FY25 `[VERIFICADO]` |
| **ARPR FY25** | **£2.854/mes** por retailer (2024: £2.721; **+5%**) | plc FY25; WebSearch `[VERIFICADO]` |
| **Palanca Price** | +£78 a ARPR (evento anual de precios, 1-abr) | plc FY25 `[VERIFICADO]` |
| **Palanca Product** | +£77 a ARPR (sobre todo **Trended Valuations + enhanced Retail Check** incluidos en packages abr-2024) | plc FY25 `[VERIFICADO]` |
| **Palanca Stock** | −£22 (menos slots por venta más rápida) | plc FY25 `[VERIFICADO]` |
| **Evento de precios** | Subida anual **1 de abril** para todos los clientes | plc FY25 `[VERIFICADO]` |
| **Subida de tarifas dealer** | **+8%** (jun-2025) | AIM Group `[VERIFICADO]` |
| **Packages dealer** | Tiered (Standard/Enhanced/Premium-style) por slot/visibilidad; precio por vehículo escalado | partners/retailer/packages `[PARCIAL — importes dealer no públicos sin login]` |
| **Anuncio privado (consumidor)** | <£1.000: Basic £9,95(2sem)/Standard £14,95(3sem)/Premium £19,95(6sem) · >£1.000: £36,95/£45,95/£56,95 | sell-my-car/advertising-prices `[VERIFICADO]` (sujeto a cambios) |
| **Tasador consumidor** | **Gratis** (motor de audiencia/lead) | autotrader.co.uk `[VERIFICADO]` |
| **API Connect** | Comercial B2B por capacidad/partner; **importes no públicos** | developers.autotrader.co.uk `[VERIFICADO por ausencia]` |

> **Modelo:** **SaaS/suscripción dominante** — el retailer paga un package mensual (slots de anuncio + inteligencia incluida), medido como **ARPR** con tres palancas (price/product/stock). La **inteligencia premium (Trended Valuations, Retail Check) se monetiza empaquetándola en tiers superiores**, no vendiéndola por consulta. Connect (API) es comercial B2B. El tasador de consumidor es **gratis** (genera la audiencia y los leads que alimentan el modelo). `[RECONSTRUIDO de plc FY25 + packages]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> **Patrón rector de Auto Trader:** separa **tres planos** y cardeep debe copiarlos: (A) **plano consumidor** = tasador simple (matrícula → 2 valores) + **Price Indicator como etiqueta semáforo en la ficha del anuncio**; (B) **plano retailer (Portal)** = el **vehículo es el hub**, con valoración + price position + Retail Rating + days to sell embebidos en la **stock list** y en **Retail Check**; (C) **plano API/macro** = métricas servibles por endpoint + inteligencia de mercado (Market Insight) y RPI **fuera de la ficha**.

**A. Ficha de anuncio (VDP consumidor).** El dato estrella es el **Price Indicator** (etiqueta **Lower/Great/Good/Fair/Higher**) colocada **junto al precio**, comparando asking vs valoración propia; link a "About our price labels" que explica factores (make/model/age/fuel/extras) y exclusiones. Specs/features del vehículo (de la taxonomía) en el cuerpo de la ficha.

**B. Tasador de consumidor (landing dedicada).** Pantalla mínima: **un input (matrícula)** → "Get my free instant valuation" → paso mileage → resultado con **Private sale value + Part-exchange value**; bloque educativo "factores que suben/bajan el valor". Patrón: **fricción casi cero, dos números, lenguaje de confianza** ("driven by data", Trustpilot).

**C. Stock list del Portal (retailer).** Cada fila de stock muestra **Retail Valuation + Price Position (%)** directamente (release "now in your Portal stock list"). Es el patrón de **inteligencia inline en la tabla de inventario**.

**D. Retail Check (workbench por vehículo).** Pantalla de detalle del vehículo con: **Retail Valuation** (live) + **Price Position %** + **Retail Rating 1–100** + **Average Days to Sell** + **Supply/Demand** + **Competitor view** (stock similar) + **Retail Back calculator** (retail − costes − margen = max a pagar). Es el patrón de **"todo el pricing de un coche en una pantalla"**.

**E. Vehicle Edit → tab "Valuation and pricing".** Aquí viven **Trended Valuations** (curva 6m atrás + forecast 6m, con +30/+60/+90d) integradas en el flujo de edición del anuncio.

**F. Retail Accelerator (vista de forecourt).** Vista agregada de **todo el stock** con **alertas pro-activas** (valuation changes, incorrect pricing, ageing/overage, fuera de estrategia) + **performance reporting** + **competitor activity**. Patrón: **dashboard de gestión por excepción/alerta**, no ficha individual.

**G. Market Insight / Vehicle Insight dashboard.** **Fuera de la ficha**: Supply / Demand / Market Condition / Days to Sell con filtros make/model/fuel/age band, **nacional + regional**. Patrón de **panel macro de mercado** para decisiones de compra de stock.

**H. Capa pública/PR.** **Retail Price Index** mensual (like-for-like % + mix % + average price por segmento) como informe descargable/PR — patrón de **autoridad de mercado** (citado por ONS y prensa).

**I. API (Autotrader Connect).** Mismo dato pero como **endpoints**: `/valuations` (retail/trade/part-ex/private), `/vehicle-metrics` (retailRating, daysToSell, confidenceOfSale, pricePosition), `/vehicles` (specs+features+history), Future/Historic Valuations. Patrón de **headless intelligence** para integradores.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Dato de demanda real del mayor marketplace UK.** Retail Rating / Demand no son solo supply-side: incorporan **la mayor audiencia de compradores de UK** (81,6M visitas, 11M únicos). Casi nadie más tiene la **señal de demanda del consumidor** a esa escala. `[VERIFICADO]`
2. **Price Indicator (semáforo en la ficha).** Etiqueta **Lower/Great/Good/Fair/Higher** colocada junto al precio en el mayor escaparate de UK — patrón de placement icónico que disciplina el pricing de todo el mercado. `[VERIFICADO ×2]`
3. **Retail Rating 1–100 personalizado por ubicación** (desirability = demand+supply+days-to-sell, ajustado a tu forecourt). Métrica propietaria que CAP/Glass's puros no dan. `[VERIFICADO ×2]`
4. **Trended Valuations con forecast a 6 meses** (precisión declarada 1%/3%/5%) usando **OEM new car list price + estacionalidad + supply/demand**. Forecast retail nativo. `[VERIFICADO ×2]`
5. **Retail Back calculator** (retail − costes − margen objetivo = precio máximo a pagar): convierte la valoración en **decisión de compra accionable**. `[VERIFICADO]`
6. **Autotrader Connect = headless intelligence madura** (15+3 APIs, sandbox, Postman, Historic/Future Valuations, Vehicle Metrics, Deals con dealIntentScore). Pocos competidores UK exponen su inteligencia tan granularmente por API. `[VERIFICADO]`
7. **Price Position como % de retail valuation** embebido **inline en la stock list** del Portal — patrón de inteligencia en la tabla de inventario. `[VERIFICADO ×2]`
8. **Aval ONS** (CPI oficial UK) = credibilidad institucional del dato de precio que ningún competidor UK iguala. `[VERIFICADO ×2]`
9. **Cobertura de tipos amplia** (cars/vans/bikes/motorhomes/caravans/trucks/farm/plant) + **leasing de coche nuevo** (Autorama). `[VERIFICADO]`
10. **Co-Driver (IA):** descripciones automáticas + orden óptimo de fotos + detección de fotos faltantes — capa generativa sobre el anuncio. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece)

1. **No tiene dato de subasta/wholesale propio (hammer/MMR).** El precio de transacción real wholesale vive en **Dealer Auction** (JV) y **Manheim** (Cox), no en Auto Trader. Su valor es **asking/retail-side**, no transacción garantizada. `[VERIFICADO por ausencia]`
2. **Valoración = precio pedido + velocidad, no precio de venta confirmado.** Reconocido en su propia web: "unlikely to give the price you will sell for". No es un libro de precio de transacción. `[VERIFICADO]`
3. **Forecast a 6 meses, no residual multi-anual.** No ofrece curva de **valor residual a 36/48 meses** ni RV% de leasing como ALG/Autovista/KeeResources-RV puro (la RV de KeeResources es B2B fleet, no expuesta como producto Auto Trader retail). `[VERIFICADO por ausencia]`
4. **Condición/daño no integrados en la valoración.** El tasador y el price indicator **excluyen explícitamente** condición, color, modificaciones, service history y owners — no hay grading NAMA ni inspección mecánica (eso es Manheim). `[VERIFICADO]`
5. **UK-only.** Sin set de inteligencia para España/EU (matrícula VRM, mercado UK). ← hueco directo para cardeep en España. `[VERIFICADO]`
6. **Provenance: proveedor no transparente.** Expone write-off/finance/stolen/mileage, pero el **proveedor de datos de provenance UK no está verificado** públicamente (¿Experian u otro?). No es su producto estrella (lo es de HPI/Experian/cap hpi). `[NO-VERIFICADO]`
7. **Importes de package dealer no públicos.** El precio real por tier/slot solo tras login/account manager; solo el modelo ARPR y los packages de consumidor son públicos. `[PARCIAL]`
8. **Coche nuevo: valor de lista, no valoración propia.** Para nuevo usa **OEM list price** (input del forecast) y leasing (Autorama); no genera un "valor justo de coche nuevo" independiente. `[VERIFICADO por ausencia]`
9. **Battery health EV no expuesto.** Hay batteryRange/Capacity (spec), pero **no un score de salud de batería VIN-específico**. `[VERIFICADO por ausencia]`
10. **Days to Sell es estimación de mercado, no SLA.** Modela velocidad esperada a market value; no garantiza venta. `[VERIFICADO]`

---

## 10. Fuentes

**Oficiales / producto (Auto Trader UK):**
- Tasador consumidor: https://www.autotrader.co.uk/cars/valuation (snapshot Playwright) · colección: https://www.autotrader.co.uk/content/collections/value-my-car
- **Price Indicator (verbatim):** https://www.autotrader.co.uk/price-indicator-info (snapshot Playwright) · help: https://help.autotrader.co.uk/hc/en-gb/articles/19212037724957-Why-do-I-have-a-Price-Indicator-on-my-advert
- Retail Accelerator: https://www.autotrader.co.uk/partners/retailer/products/retail-accelerator (snapshot Playwright) · trade: https://trade.autotrader.co.uk/products/retail-accelerator/
- Market Insight: https://www.autotrader.co.uk/partners/retailer/solutions/market-insight · help: https://help.autotrader.co.uk/hc/en-gb/articles/13255055774749-What-is-Market-Insight
- Retail Check: https://www.autotrader.co.uk/partners/retailer/solutions/retail-check
- Trended Valuations: https://www.autotrader.co.uk/partners/retailer/solutions/trended-valuations · help (accuracy): https://help.autotrader.co.uk/hc/en-gb/articles/16450896474141-How-accurate-is-the-trended-valuation-forecast · help (método): https://help.autotrader.co.uk/hc/en-gb/articles/16450820091549-How-do-you-work-out-the-future-trended-valuation
- **Retail Rating (verbatim):** https://help.autotrader.co.uk/hc/en-gb/articles/19690017165981-What-is-Retail-Rating
- **Current Valuations (verbatim, snapshot Playwright):** https://help.autotrader.co.uk/hc/en-gb/articles/21923133513117-Introduction-to-Current-Valuations
- Vehicle Metrics (help): https://help.autotrader.co.uk/hc/en-gb/articles/21946149296029-Introduction-to-Vehicle-Metrics · Future Valuations: https://help.autotrader.co.uk/hc/en-gb/articles/21945605916573-Introduction-to-Future-Valuations
- **Autotrader Connect / API (campos atómicos):** https://developers.autotrader.co.uk/api · platform: https://www.autotrader.co.uk/partners/retailer/platform/autotrader-connect · Postman: https://www.postman.com/auto-trader-tam/partner-starter-collections
- Autotrader Valuations (Connect): https://www.autotrader.co.uk/partners/retailer/auto-trader-connect/valuations · price to live market: https://www.autotrader.co.uk/partners/retailer/data-and-insight/price-to-the-live-market
- Packages: https://www.autotrader.co.uk/partners/retailer/packages · advertising prices (consumidor): https://www.autotrader.co.uk/sell-my-car/advertising-prices

**Corporativo / investor / metodología:**
- Historia: https://plc.autotrader.co.uk/about/our-history/ (+ https://plc.autotrader.co.uk/who-we-are/our-history/)
- **FY25 full-year press release (ARPR, escala):** https://plc.autotrader.co.uk/media/umddcnxx/full-year-press-release-fy25.pdf · 2025 annual report: https://plc.autotrader.co.uk/investors/2025-annual-report/
- Retail Price Index: https://plc.autotrader.co.uk/news-views/retail-price-index/
- **ONS usa datos Auto Trader (CPI):** https://www.ons.gov.uk/economy/inflationandpriceindices/articles/usingautotradercarlistingsdatatotransformconsumerpricestatisticsuk/2022-06-28 · press: https://plc.autotrader.co.uk/news-views/press-releases/auto-trader-data-to-power-office-for-national-statistics-official-measures-of-inflation/
- Two-thirds de ventas vía marketplace: https://plc.autotrader.co.uk/news-views/press-releases/auto-trader-grows-influence-as-two-thirds-of-its-customers-used-car-sales-generated-through-its-marketplace/
- Wikipedia (identidad/IPO/rebrand): https://en.wikipedia.org/wiki/Auto_Trader_Group

**Adquisiciones / JV / verificación cruzada:**
- KeeResources: https://aimgroup.com/2019/10/02/auto-trader-buys-data-firm-keeresources/ · https://fleetworld.co.uk/keeresources-acquired-by-auto-trader-group/
- Autorama: https://www.traverssmith.com/knowledge/knowledge-container/travers-smith-advises-auto-trader-on-its-200m-acquisition-of-autorama/
- Dealer Auction (JV Cox 51/AT 49): https://www.am-online.com/news/supplier-news/2019/01/02/auto-trader-and-cox-automotive-launch-dealer-auction-joint-venture · https://www.dealerauction.co.uk/about-us/
- i-Control → Retail Accelerator: https://www.am-online.com/news/supplier-news/2019/04/12/auto-trader-replaces-i-control-with-more-powerful-retail-accelerator
- Valuations a todos los retailers (ene-2024): https://www.am-online.com/news/market-insight/2024/01/29/auto-trader-offers-dealers-new-valuations-tools
- Dealer fees +8% (2025): https://aimgroup.com/2025/06/03/auto-trader-raises-dealer-fees-by-8/
- Price Position en stock list: https://www.autotraderinsight-blog.co.uk/auto-trader-insight-blog/stay-on-top-of-pricing-with-the-retail-valuation-and-price-position-now-in-your-portal-stock-list

### Notas de verificación / método
- **Páginas de consumidor y de partner (`www.autotrader.co.uk/*`) y de ayuda (`help.autotrader.co.uk/*`) devuelven 403 a WebFetch** (protección anti-bot). Resueltas con **navegador real (Playwright)**: snapshots atómicos guardados de `/cars/valuation`, `/price-indicator-info`, `/partners/retailer/products/retail-accelerator` y help `Introduction to Current Valuations` — **[VERIFICADO]** verbatim.
- **El navegador Playwright es COMPARTIDO con otros agentes del workflow** (durante la sesión la página fue secuestrada a Motorway y Copart entre llamadas). Mitigación: solo se usó el **snapshot que captura `browser_navigate`** (atómico, fiable); se descartaron los `evaluate` posteriores (carrera). Contenido cruzado con WebSearch.
- **developers.autotrader.co.uk/api** sí accesible vía WebFetch → fuente primaria del listado atómico de campos por API. **[VERIFICADO]**.
- **PDF FY25** descargado pero ilegible vía WebFetch (binario); cifras de ARPR/escala obtenidas por **WebSearch sobre el propio dominio plc + prensa (AIM Group, am-online)**. **[VERIFICADO]** (ARPR £2.854, palancas £78/£77/−£22).
- **Co-fundadores (Gibbons/Taylor)** de 1 fuente secundaria → **[PARCIAL]**; **Madejski** confirmado por our-history + Wikipedia → **[VERIFICADO]**.
- **Proveedor de provenance UK** (Experian u otro) **no confirmado** → **[NO-VERIFICADO]**.
- **exa MCP:** ToolSearch "exa…" no devolvió herramienta semántica dedicada (solo WebSearch/WebFetch + gbrain/claude-mem); investigación con **WebSearch + WebFetch + Playwright + lectura directa**. **[NOTA DE MÉTODO]**.
