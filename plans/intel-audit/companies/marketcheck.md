# Auditoría atómica — MarketCheck (MarketCheck Cars Inc)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos e inteligencia de automoción API-first**: agregación VIN-level de inventario, listings, ventas inferidas, pricing y build-data desde miles de webs de concesionario/clasificados. Web UK (producto del scope): https://marketcheck.uk/ · Web matriz US/Canadá: https://www.marketcheck.com/ · Docs API unificadas: https://docs.marketcheck.com/ (apidocs.marketcheck.uk → 301 a docs.marketcheck.com) · Portal pricing/desarrolladores: https://www.marketcheck.com/apis/pricing/ · API base: `https://api.marketcheck.com/v2/`.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **market-intelligence** (no es un host DNS; market-intelligence.marketcheck.uk y .com **no resuelven** — NXDOMAIN verificado).
> Fecha auditoría: 2026-06-30. Método: navegación de marketcheck.uk (about, products, sectors, resources, market-analysis), marketcheck.com (home, apis, apis/cars, marketcheck-price, data_feed/neovin, pricing), docs.marketcheck.com (data introduction + data-definitions, API introduction, inventory-search, neovin, marketcheck-price, market-days-supply, sales-stats, apis/cars), informe mensual real UK enero-2026, + verificación cruzada con agregadores (Neudata, ZoomInfo, Crunchbase, Tracxn, Owler, Datarade, Gust, LinkedIn).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **MarketCheck** / **MarketCheck.com** / **MarketCheck UK** | [V] |
| Razón social | **MarketCheck Cars Inc** (también "Market Check Inc") | [V] |
| Categoría | **Agregador neutral de datos de automoción API-first**: inventario VIN-level en tiempo real, listings de concesionario/clasificados/subasta/particular, ventas inferidas, pricing/market trends, build-data (NeoVIN), incentivos, recalls. No es una guía editorial de valoración tipo Glass's/Eurotax. | [V] |
| Fundación | **2010-2012** (variación entre fuentes: búsqueda agregada "2010"; Neudata "2012"; about-us "hace 10+ años"; plataforma de datos "cada 24h desde 2012/2014-2015"). Troy Campbell en extracción de datos web "desde 2002". | [V — con variación, ver Gaps] |
| HQ matriz | **3280 N Frontage Rd, Lehi, Utah 84043, EE.UU.** (ZoomInfo); Neudata la describe **"remote only"** (remote-first, originada en Lehi, Utah) | [V] |
| Oficina UK | **7 Bell Yard, London, WC2A 2JR** | [V — home marketcheck.com] |
| Equipo de desarrollo | **~40 desarrolladores in-house full-time** (about-us); equipo de desarrollo en **India** | [V] |
| Fundadores | **Troy Campbell** y **Dan Campbell** (hermanos) | [V] |
| Liderazgo | **CONFLICTO DE FUENTES**: about-us UK dice **CEO = Troy Campbell, President = Dan Campbell**; agregadores (ZoomInfo, LinkedIn `troycampbell67`, Crunchbase) dicen **Troy = President & Co-Founder y Dan = CEO**. Co-CTOs: **Anand Mahajan** y **Vivek Mahajan**. | [V — discrepancia explícita, ver Gaps] |
| Empleados | **64** (Neudata, independiente); "40 desarrolladores in-house" + management/sales/ops (about-us) | [V] |
| Facturación | **No divulgada** | [V — no hay cifra pública] |
| Propiedad | **Privada** (privately owned); sin grupo matriz cotizado conocido | [V — Neudata] |
| Infraestructura | **Google Cloud + AWS** | [V — about-us] |
| Clientes | **"200+ clientes"** (about-us) / **"150+ companies"** (página Investor Reports UK); declara **"powers some of the Internet's most recognized companies"**: grandes portales de coches, value guides y reporting agencies | [V — variación de cifra] |

### Hitos / cronología [V]
- **2002** Troy Campbell comienza en extracción de datos web (Xtractly; antes LenderLab).
- **~2010-2012** Fundación en Lehi, Utah; nace como **buscador agregador de anuncios de VO** y evoluciona a plataforma de datos VIN-level.
- **desde 2012/2014-2015** Plataforma de datos: scraping diario de 100.000+ webs (US/Canadá).
- **Enero 2022** **Lanzamiento de operaciones en UK** (marketcheck.uk).
- **2025** **Entrada en el mercado de Investment Funds** (lanzamiento de Investor Reports para hedge funds/pension funds). [V — Neudata + página Investors]

### Clientes objetivo (segmentos declarados) [V]
1. **Concesionarios / retailers** (dealers).
2. **Auto lenders / finance companies** (financieras de auto).
3. **Finance brokers** (brokers de financiación).
4. **Compañías de seguros**.
5. **Repair companies** (talleres/reparación).
6. **Auction companies** (casas de subasta).
7. **Automotive software providers** (proveedores de software, integradores API).
8. **Inversores / hedge funds / pension funds / PLC investors**.
9. **Data analysts** (analistas de datos).
10. **AI-first startups** (pricing preferencial).
11. **Journalists** (acceso gratuito a market data). [V]
12. **Entrenamiento de LLMs / agentes de IA** (página "Automotive Data for LLMs & Agents"). [V]

---

## 2. Cobertura

### Geográfica [V]
- **EE.UU., Canadá y Reino Unido** ("the most comprehensive view available for the vehicle retail market across the US, Canada, and the UK").
- **EE.UU. exclusivamente**: RVs (autocaravanas), motocicletas, maquinaria pesada (heavy equipment).

### Escala — matriz US/Canadá [V — home marketcheck.com + Datarade]
- **290.000 millones (290B) de data points totales**.
- **3.500 millones (3.5B) de listings de vehículos** acumulados.
- Escaneo de **100.000+ webs de concesionario al día** (Datarade cita "65k+ dealer websites daily"; variación según fuente).
- **84.000 concesionarios**, **262M VINs únicos**, **540M listings retail** (cifras del producto MarketCheck Price™).
- **~110 data points por listing**.
- **Latencia media de API: 100 ms**; datos **actualizados cada día**.
- **6 años** de histórico de inventario (US/Canadá).

### Escala — UK [V — about + products + informe enero-2026]
- **600.000-680.000 anuncios** de VO rastreados a diario (cifras 600k / 650k / 680k según página; el informe enero-2026 contabiliza **861.831 listings ICE + 65.611 EV** ese mes).
- **10.000-11.000 concesionarios** y **14.000-16.496 "rooftops"/ubicaciones** rastreados a diario.
- **1.000 millones (1B) de data points** (UK).
- Cobertura: **"every used car advert since January 2021 is tracked"** (histórico UK desde ene-2021).
- Cotejado contra **DVLA, SMMT y "3 fuentes de datos" adicionales** para normalización y precisión.

### Scope de vehículos [V]
- **Coches** (núcleo): **new, used, certified (CPO), lease, auction y private-seller**.
- **US-only**: **RVs, motocicletas, maquinaria pesada**.
- En UK incluye **electric vans** (furgonetas eléctricas) en sus informes; segmenta **ICE vs EV** sistemáticamente.
- **[A]** No se observa cobertura de moto/RV/heavy-equipment fuera de EE.UU. (ausentes en UK/Canadá).

---

## 3. Productos + campos atómicos

Arquitectura **API-first** (catálogo de ~20 endpoints de coches + datasets bulk + productos UK + herramientas). Cada listing = **~110 data points**. A continuación, el desglose atómico por producto.

### — BLOQUE INVENTARIO / LISTINGS (API) —

### 3.1 Inventory Search API (`/v2/search/car/active`) [V]
"Search active inventory across all dealers." **112 parámetros de búsqueda**; devuelve listings + facets + stats + range_facets. **$0.002/call**.
**Campos del objeto listing (núcleo del esquema, ~110 data points):**
- Identidad/listing: `id`, `vin`, `heading`, `vdp_url`, `data_source`/`source`, `stock_no`, `is_certified`.
- Precio: `price`, `msrp`, `ref_price`, `ref_price_dt`, `price_change_percent`, `buy_now_price`.
- Km: `miles`, `ref_miles`, `ref_miles_dt`.
- Tiempo en mercado: `dom` (Days on Market lifetime), `dom_180`, `dom_active`, `dos_active` (Days on Site activo).
- Fechas/estado: `status_date`, `scraped_at`/`scraped_at_date`, `first_seen_at`(+`_date`), `first_seen_at_source`(+`_date`), `first_seen_at_mc`(+`_date`), `last_seen_at`(+`_date`), `in_transit`, `vehicle_status`, `availability_status`.
- Historial/título: `carfax_1_owner`, `carfax_clean_title`.
- Build/spec: `year`, `make`, `model`, `trim`, `version`, `vehicle_type`, `body_type`, `body_subtype`, `drivetrain`, `transmission`, `engine`, `engine_size`, `engine_block`, `engine_displacement`, `fuel_type`, `powertrain_type`, `door`/`doors`, `cylinders`, `std_seating`, `made_in`, `model_code`, `overall_height`, `overall_length`, `overall_width`, `city_mpg`, `highway_mpg`.
- Color: `exterior_color`, `interior_color`, `base_exterior_color`/`base_ext_color`, `base_interior_color`/`base_int_color`.
- Equipamiento: `options` (pipe-separated), `features` (pipe-separated), `high_value_features`, `options_packages`, `seller_comments`.
- Media: `photo_url`, `photo_links`, `photo_links_cached`.
- Dealer/ubicación: `seller_name`, `dealer.id`, `dealer.name`, `dealer.website`, `seller_type` (Dealership/private/auction), `inventory_type` (new/used), `dealer_type` (franchise/independent), `street`, `city`, `state`, `zip`, `country`, `latitude`, `longitude`, `phone`, `seller_email`, `dealership_group_name`, `msa_code`, `dist`.
- Ubicación física del coche (si difiere): `car_seller_name`, `car_street`, `car_city`, `car_state`, `car_zip`, `is_searchable` (1/0).
- Identificadores MarketCheck (objeto `mc_dealership`): `mc_category`, `mc_dealer_id`, `mc_location_id`, `mc_website_id`, `mc_rooftop_id`, `mc_dealership_group_id`, `mc_dealership_group_name`, `mc_sub_dealership_group_id`, `mc_sub_dealership_group_name`.
- Finance: `loan_term`/`finance_loan_term`, `loan_apr`/`finance_loan_apr`, `down_payment`/`finance_down_payment`, `down_payment_percentage`, `finance_emp`, `estimated_monthly_payment`.
- Lease: `lease_term`, `lease_down_payment`, `lease_emp`, `estimated_monthly_payment`.
- **Stats por campo** (cuando `stats=` solicitado): `min`, `max`, `count`, `missing`, `sum`, `mean`, `stddev`, `sum_of_squares`, `median`, `percentiles` (5/25/50/75/90/95/99). Campos estadisticables: `price`, `msrp`, `buy_now_price`, `miles`, `highway_mpg`, `city_mpg`, `dom`, `dom_180`, `dom_active`, `dos_active`, `lease_term`, `lease_emp`, `lease_down_payment`, `finance_loan_term`, `finance_loan_apr`, `finance_emp`, `finance_down_payment`.
- **range_facets**: `counts[lower_bound,upper_bound,count]`, `interval`, `start`, `end`, `before`, `between`, `after`. **Top-level**: `num_found`, `listings`, `facets`, `stats`, `range_facets`.

### 3.2 Variantes de búsqueda de inventario [V]
- **Dealer Active Inventory / Dealer API** (`/v2/dealers/car`, `/v2/dealer/car/{id}`, `/v2/dealerships/car`) — inventario por dealer ID o geografía + datos de contacto del dealer. **$0.0025/call**.
- **Dealer Inventory Syndication API** — listings activos para sindicación con paginación masiva. **$1.00/call**.
- **Marketplace Inventory Syndication API** — convierte inventario de dealer a formato marketplace.
- **Private Party Search API** (`/v2/search/car/private`) — anuncios de particulares (US/Canadá). **$0.01/call**.
- **Auction Inventory Search API** (`/v2/search/car/auction`) — listings de subasta (US/Canadá). **$0.008/call**.
- **Recent Inventory Search / Dealer Recent Inventory** — inventario de los **últimos 90 días**. **$0.006/call**.
- **Listing Details API** — ficha completa de un listing.
- **Auto-complete API** — autosugerencia de input de usuario.
- **Cached Images API** — imágenes del vehículo desde su BBDD interna. **$0.001/call**.

### — BLOQUE IDENTIFICACIÓN / BUILD-DATA (VIN) —

### 3.3 Basic VIN Decoder API (`/v2/decode/car/{vin}/specs`) [V]
"Decode 17-digit VIN for specifications." Devuelve year, make, model, trim + equipamiento instalado + specs detalladas. **$0.0015/call**.

### 3.4 Epi (Enhanced) VIN Decoder API [V]
Decode mejorado de especificaciones. **$0.08/call**.

### 3.5 NeoVIN Enhanced Decoder API (`/v2/decode/car/neovin/{vin}`) — producto estrella de build-data [V]
"Set a new standard for automotive build data, capturing vehicle specs at the VIN level." Build-specs VIN-level para vehículos **fabricados después de 1997**, incluyendo opciones/packages/features **aunque no figuren en el anuncio ni en el window sticker**. **$0.08/call**.
**Campos devueltos:**
- Identidad: `vin`, `squish_vin`, `decode_version`.
- Specs: `year`, `make`, `model`, `vehicle_type`, `trim`, `version`, `body_type`, `body_subtype`, `country`.
- Transmisión/tracción: `transmission`, `transmission_description`, `transmission_confidence`, `drivetrain`, `powertrain_type`.
- Motor/combustible: `engine`, `fuel_type`, `city_mpg`, `highway_mpg`.
- Dimensiones/peso: `doors`, `weight`, `width`, `height`, `length`, `seating_capacity`.
- Pricing OEM: `msrp`, `delivery_charges`, `installed_options_msrp`, `combined_msrp`, `mc_msrp`, `build_specs_msrp`, `oem_msrp`, `original_msrp`.
- Códigos: `manufacturer_code`, `package_code`, `build_code` (body style + set de options-packages instalados).
- Color (objeto): `interior_color`/`exterior_color` con `{code, name, confidence, base}`.
- Opciones/equipamiento: `options_packages` (lista de packages instalados), `installed_options_details` (`code, name, msrp, type, confidence, verified, rule, sale_price`), `available_options_details` (`code, name, msrp, type`), `features` (por categoría), `high_value_features` (premium por categoría), `installed_equipment` (`category, item, attribute, location, value`).
- Confianza/calidad: `listing_confidence`, `trim_confidence`, `version_confidence`, `transmission_confidence`, `record_confidence` (float 0-1).
- Metadatos: `created_at`(+`_date`), `updated_at`(+`_date`), `record_source`, `generic`.
- **Available Options Packages API** (`/v2/decode/car/{vin}/options`): devuelve **todos los packages de opciones del fabricante disponibles para ese VIN al momento de venta**.
- Datasets adicionales NeoVIN: **MPG, dimensiones, delivery dates, window sticker data**.

### — BLOQUE PRICING / VALORACIÓN —

### 3.6 MarketCheck Price™ API (`/v2/predict/car/price`) — valoración (3 tiers) [V]
"Deep insights into vehicle pricing trends, comparing real-time data from millions of listings." ML sobre **84k dealers / 262M VINs únicos / 540M listings retail**. Precisión declarada: **±5% para 25+ años-modelo; ±4% para vehículos de 1-5 años**.
- **Base** (**$0.07/call**): `marketcheck_price` (precio de mercado predicho), `msrp`.
- **Premium** (**$0.09/call**): añade `comparables` y `recent_comparables` (cada uno: `num_found`, `listings[]`, `stats{price, miles, dos_active}` con min/max/count/missing/sum/mean/stddev/sum_of_squares/median/percentiles). Listings comparables: `id, vin, price, miles, dom, dom_180, dom_active, dos_active, year, make, model, trim, photo_url, dealer_id, latitude, longitude, mc_website_id`.
- **Premium Plus** (**$0.13/call**): añade `decode` (NeoVINDecode completo — equipamiento/features VIN-level).
- Campos relacionados: **neoVIN Combined MSRP**, **Equipment and Feature Data**, **Comparable Active Listings** (en región definida), **Accuracy Ranges**.

> Nota analítica: MarketCheck **no expone** un campo etiquetado literalmente como **"price-to-market %"** ni "trade/retail/wholesale" discretos; su valoración es **un único `marketcheck_price` predicho** + **distribución estadística de comparables** (mean/median/percentiles de `price`), de la que el cliente deriva el posicionamiento. (Ver Gaps.)

### — BLOQUE MÉTRICAS DE MERCADO —

### 3.7 Market Days Supply (MDS) API (`/v2/mds/car`) [V]
"Get Market Days Supply value for a car." **$0.006/call**. Mismos ~110 filtros que Inventory Search (vin/ymmt/body/car_type/fuel/engine/drivetrain/transmission/color/miles_range/price_range/geo/dealer…).
**Respuesta:** `mds` (null si 0 ventas), `total_active_cars_for_ymmt` (inventario activo actual), `total_cars_sold_in_last_45_days`, `sold_vins[]` (si `include_sold=true`, hasta 10.000), `debug{year[],make[],model[],trim[]}`.
**Fórmula:** `MDS = (inventario activo) / (tasa de venta diaria de los últimos 45 días)`. Niveles: city / state / national.

### 3.8 Sales Stats API (`/v2/sales/car`) — ventas inferidas [V]
"Fetch sales stats for cars in last **90 days** by year, make, model, trim, taxonomy vin combination." Niveles **city / state / national**. **$0.006/call** ("Cars Market APIs"). Métricas inferidas de ventas + stats de precio/km/dom asociadas.

### 3.9 Stats API [V]
Estadísticas de disponibilidad actual de vehículos (current vehicle availability statistics).

### 3.10 Popular Cars API (`/v2/popular/cars`) [V]
"Fetch most popular cars in US and Canada on national, state and city level" + sales statistics (ranking de popularidad).

### — BLOQUE HISTORIAL / ENRIQUECIMIENTO —

### 3.11 VIN History API (`/v2/history/car/{vin}`) [V]
"Enter a 17-digit VIN to see the **price history, changing odometer readings & full details** about each car for up to **six years** back." (UK: el used-car-market-data-api cita "listing history spanning **2 years**" / "past 90 days activity" — variación por región.) **$0.006/call**.
**Campos por evento:** historial de `price` (cambios), `miles`/odómetro (cambios), `dom`, cambios de dealer/`seller_name`, `first_seen`/`last_seen` (date, advertised price, mileage observed, VDP URL, seller name).

### 3.12 OEM Incentives API (`/v2/search/car/incentive/oem`, `/v2/search/car/incentive/{make}/{zip}`) [V]
"Search Incentive Programs for **30+ car manufacturers** at one place" / "manufacturer financing incentives". **$0.20/call**.

### 3.13 Recalls API (`/v2/car/autorecalls/{vin}`) [V]
"Get recall information for a VIN from AutoRecalls." **$0.07/call** (third-party AutoRecalls).

### 3.14 APIs de terceros (revendidas) [V]
- **AutoRecalls API** — $0.07/call.
- **VINData Title Check API** — $0.49/call (title/branding check).
- **CarsXE Plate to VIN API** — $0.70/call (matrícula→VIN, US).

### — BLOQUE OTRAS VERTICALES (US-only) —
### 3.15 RV / Motorcycle / Heavy Equipment APIs [V]
Cada vertical: **Inventory Search, Listing Details, Auto-complete, Dealer API**. RV Inventory Search **$0.002/call**, RV Dealer **$0.0025/call**.

### — BLOQUE DATASETS / FEEDS —
### 3.16 Data Feeds (bulk) [V]
"Bulk data of every dealership's inventory in a single **normalized data feed**, formatted your way and delivered when you need it." Entrega a destino cloud/SFTP, en el **schedule** que el cliente elija. Datasets: **Historical Inventory Data, Historical Sales Data, NeoVIN Data Feed, Window Sticker Data**.

### — BLOQUE PRODUCTOS UK (marketcheck.uk) —

### 3.17 UK Used Car Market Data API [V]
Cobertura: **10.000 dealers / 14.000 ubicaciones UK, 1B data points**, actividad de **últimos 90 días**. Lookup por **VRM (matrícula)**. Devuelve: year/make/model/variant, `price` + price changes en el tiempo, engine type/transmission/displacement/fuel_type, interior/exterior color, body style/subtype, odómetro, **listing history (2 años)**, dealership/seller info, cambios de ubicación del vehículo. Entrega: API REST v2 / bulk dumps / custom reports vía **SFTP**; "Full documentation and Postman tools".

### 3.18 Auction Stock Analysis (UK) — análisis de stock de subasta [V]
"All you need is a **CSV of the data to upload**, and we will do the rest." Cruza el VRM contra los **650.000+ vehículos rastreados a diario** en redes de dealer UK. Métricas por VRM:
- **Fair Market Value** = "a **linear regression price** based on **MMV (make-model-variant), mileage and age**".
- **Price Predictor** = "uses **AI** to create **retail pricing** based on **unit availability, popularity (velocity to sell) y las features del coche**".
- **Price range** (lower bound, upper bound).
- **Margin gap** = diferencia entre precio de venta estimado y **hammer price** (precio de martillo de subasta).
- Tracking first-seen: `first seen seller name, first seen date, first seen advertised price, first seen mileage observed, first seen VDP URL`.
- Tracking last-seen: `last seen seller name, last seen date, last seen advertised price, last seen mileage observed, last seen VDP URL`.
- **Days on market**, **time to prep** (tiempo de preparación), **retail turnover** (rotación retail post-subasta).

### 3.19 Integrated Car Search (UK) — widget de búsqueda + CRM [V]
Plugin **WordPress** (cut & paste) con búsqueda en vivo sobre **600.000+ VO UK / 10.000+ dealers**; proceso de **solicitud de financiación** integrado. Filtros documentados (~13 visibles; la web reclama "40+ parámetros"): Make, Body type, Drive train, Fuel type, Transmission, **Dealer FCA status**, **Write-off (CAT) category**, Price range, Mileage, **Days on market**, Registration year, Engine size, **VRM required**. **Integración CRM AutoConvert** (genera tareas/notas automáticas: creación de solicitud, envíos de email, consultas de cliente). Trackea **favouriting** (saves/likes/shares de coches al CRM).

### 3.20 Investor Reports (UK) — inteligencia para inversores [V]
Para fondos/PLC investors (150+ companies). KPIs:
- **Market-Wide Analysis**: tendencias de industria, preferencias de consumidor por región/segmento, oportunidades de inversión.
- **Dealer-Level Insights**: análisis de dealers/grupos, active inventories y actividad reciente, presencia de mercado, brand performance, customer engagement, **identificación de targets de adquisición** (top performers / infrautilizados).
- **Market-Days-Supply (MDS) Insights**: dinámica de oferta para estrategia de inversión.
- **Competitive Intelligence**: market share, pricing strategies, customer satisfaction ratings (local y nacional).
- **Pricing Intelligence**: "the **largest database of car comparables online**"; valoración para evitar adquisiciones sobrevaloradas.
- **Benchmarking** de rendimiento de compañía vs competidores; análisis granular por **brand, franchise type, pricing model**; **identificación de outliers** de rendimiento; **takeover target identification**.
- Cadencia: **daily / weekly / monthly** (custom).

### 3.21 Car & Dealer Data Feeds + Dealer Email & Data Lists (UK) [V]
- **Data Feeds**: datos de vehículo normalizados en el formato elegido, a destino cloud, schedule custom.
- **Dealer Email & Data Lists**: datos de contacto y de rendimiento (performance) de los concesionarios (lista de dealers + métricas).

### 3.22 UK Market Analysis Reports — el corazón "market-intelligence" [V]
Informes **mensuales y semanales** publicados (resources / market-analysis-reports). Ejemplo verificado (enero-2026): ver §7 Placement para la lista completa de métricas. Acceso gratuito declarado para periodistas.

### — HERRAMIENTAS / CANALES —
### 3.23 Chrome Extension · Cowork Plugins · Postman [V]
- **Chrome Extension** (consulta de datos en navegación).
- **Cowork Plugins** (cowork.marketcheck.com) — plugins con pricing por uso (`search_uk_active_cars`, `search_uk_recent_cars`, `decode_vin_neovin`…).
- **Postman collections** + documentación pública.

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = agregación/scraping masivo, NO panel editorial**: "scrapes, normalizes, and dedupes information from **every dealership website** in the US and Canada, así como **every OEM microsite and public classifieds site**". **100.000+ webs/día** (US/Canadá); **650k+ vehículos/día** (UK).
- **Fuentes**: webs de concesionario, **OEM microsites**, sitios de clasificados/marketplace públicos, sitios de subasta, anuncios de particular. **UK**: cotejo contra **DVLA** (matriculaciones/datos oficiales), **SMMT** (estadística de industria) y **"3 fuentes de datos" adicionales** para normalización y precisión.
- **Pipeline**: collect → **normalize** → **dedupe** → enriquecer con **NeoVIN** (build-data VIN-level) → **confidence scoring** (`record_confidence`, `trim_confidence`, `version_confidence`, `transmission_confidence`, `listing_confidence`). "**100% data coverage quality assurance**" declarado.
- **Frecuencia**: **cada 24h** (diario); API en tiempo real (latencia ~100 ms); feeds en schedule del cliente.
- **NeoVIN**: reconstruye specs VIN-level **incluso si no están en el anuncio ni en el window sticker** (post-1997); deriva `build_code` (body + options-packages).
- **Métricas computadas**:
  - **MDS** = inventario activo ÷ tasa de venta diaria de 45 días (ventas **inferidas**, no transaccionales reales).
  - **Sales Stats** = ventas **inferidas** de los últimos 90 días por ymmt/taxonomy-vin (desaparición de listing ≈ venta).
  - **Fair Market Value** (UK) = **regresión lineal** sobre MMV + mileage + age.
  - **Price Predictor / MarketCheck Price™** = **ML** sobre 540M listings (availability + popularity/velocity + features).
- **Neutralidad**: se posiciona como **"largest neutral data provider in the automotive industry"** — dato crudo de mercado, no opinión de valor de un editor.

---

## 5. Entrega
- **API REST v2** (`https://api.marketcheck.com/v2/`, API key) — canal primario; docs unificadas en docs.marketcheck.com; **Postman**. [V]
- **Bulk data feeds / data dumps** — feed normalizado único, a **destino cloud / SFTP**, con **schedule** a medida. [V]
- **Custom reports / market reports** (daily/weekly/monthly), incl. **Investor Reports**. [V]
- **Carga CSV → análisis** (Auction Stock Analysis: subes CSV de VRMs, devuelven el dataset enriquecido). [V]
- **Widget web embebible** (Integrated Car Search — **plugin WordPress**) + integración **CRM AutoConvert**. [V]
- **Chrome Extension** + **Cowork plugins**. [V]
- **Direct database access** (acceso directo a BBDD, citado para NeoVIN). [V]
- **Informes/artículos públicos** en marketcheck.uk/resources (market intelligence). [V]
- **Datos para LLMs/agentes IA** (training/grounding). [V]

---

## 6. Precio
**Modelo "blended" = suscripción (flat fee por velocidad/SLA) + coste de dato por volumen/tipo.** Verificado en marketcheck.com/apis/pricing/. [V]

| Tier | Flat fee | Llamadas | Velocidad | Extras |
|---|---|---|---|---|
| **Free** | $0/mo + data fee | 500/mes | 5 calls/s | radio máx 100 millas |
| **Basic** | **$299/mo** + data fee | 5.000/mes | 5 calls/s | acceso a todos los endpoints |
| **Standard** | **$749/mo** + data fee | ilimitadas | 40 calls/s | radio 500 millas, **white-label** |
| **Enterprise** | "Inquire" (custom) | ilimitadas | — | sin restricción de radio, **bulk delivery** |

**Coste de dato por llamada (ejemplos [V]):** Inventory Search **$0.002** · Cached Images **$0.001** · Basic VIN Decoder **$0.0015** · VIN History / MDS / Sales Stats / Recent Inventory **$0.006** · Auction Search **$0.008** · Private Party **$0.01** · MarketCheck Price **$0.07 / $0.09 / $0.13** · Epi & NeoVIN Decoder **$0.08** · AutoRecalls **$0.07** · OEM Incentive **$0.20** · VINData Title Check **$0.49** · CarsXE Plate-to-VIN **$0.70** · Dealer Inventory Syndication **$1.00**.
**Otros:** datasets/APIs "**start at $8**" (Datarade); facturación **mensual** (subscription + data cost a principio de mes); **billing anticipado** si el data cost supera **$1.000** antes de fin de mes; bulk feed pricing "use-case dependent, vía discovery meeting"; muestras gratis bajo petición; pricing preferencial para **AI-first startups**. UK: "request a data trial". **No hay free trial clásico**; el tier Free (500 calls/mes) hace de prueba continua.

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: mapeo pantalla/sección/respuesta → dato.

### Respuesta de Inventory Search (objeto listing) — "ficha de coche" API [V]
- **Cabecera**: `heading` (year+make+model+trim) + `photo_url`/`photo_links` + `vdp_url`.
- **Bloque precio**: `price`, `msrp`, `price_change_percent`, `ref_price`/`ref_price_dt` (precio de referencia previo), `buy_now_price`.
- **Bloque "salud del anuncio"**: `dom` / `dom_active` / `dos_active` (días en mercado/sitio), `first_seen`/`last_seen`, `vehicle_status`, `in_transit`.
- **Bloque historial/título**: `carfax_1_owner`, `carfax_clean_title`.
- **Bloque dealer**: objeto `dealer` + `mc_dealership` (jerarquía grupo→sub-grupo→rooftop→location) + geo (`latitude/longitude/dist`) + `phone`.
- **Bloque finance/lease**: cuotas estimadas, APR, term, down payment.
- **Bloque agregado** (cuando pides `stats`/`facets`): distribución min/max/mean/median/percentiles de `price`/`miles`/`dom` sobre el conjunto → posicionamiento del vehículo dentro del mercado.

### MarketCheck Price™ — pantalla de valoración [V]
- **Cifra central**: `marketcheck_price` (valor predicho) + `msrp`.
- **Panel de comparables** (Premium): `comparables`/`recent_comparables` → lista de listings similares + **stats** (mean/median/percentiles de precio, miles, dos_active) en la **región definida**.
- **Panel de equipamiento** (Premium Plus): `decode` NeoVIN (features/options VIN-level, combined MSRP).

### Market Days Supply — indicador de oferta/demanda [V]
- Pantalla/endpoint dedicado: **`mds`** + `total_active_cars_for_ymmt` (oferta) + `total_cars_sold_in_last_45_days` (demanda). Comparable a "market days supply" del sector; nivel city/state/national.

### Auction Stock Analysis (UK) — flujo CSV→informe [V]
- **Subes CSV de VRMs** → por cada coche: **Fair Market Value** + **Price Predictor (retail)** + **price range** + **margin gap vs hammer price** + **first/last seen** (precio, km, fecha, vendedor, VDP) + **days on market** + **time to prep** + **retail turnover**. Vista pensada para evaluar **margen post-subasta**.

### Integrated Car Search (UK) — widget en web del cliente [V]
- Barra de filtros (make/body/fuel/transmission/price/mileage/year/engine/**FCA status**/**write-off CAT**/**DOM**/**VRM**) → resultados sobre 600k coches → CTA de **financiación** → eventos a **CRM AutoConvert** (favouriting, application, email, inquiry).

### Investor Reports (UK) — dashboard/informe de inversor [V]
- Secciones: **Market-Wide** (tendencias/segmentos/regiones) · **Dealer-Level** (inventarios activos, brand performance, targets de adquisición) · **MDS** · **Competitive Intelligence** (market share, pricing, satisfacción) · **Pricing Intelligence** (comparables) · **Benchmarking** (brand/franchise/pricing-model, outliers, takeover targets).

### Informe mensual UK (market-intelligence) — estructura verificada (enero-2026) [V]
> El patrón editorial más valioso para Cardeep: cómo ordenan el mercado en un PDF/página.
Bloques y métricas exactas del informe enero-2026:
- **Snapshot ICE**: total dealers **10.694**, total rooftops **16.496**, total listings **861.831**, **Average DOM 80 días**, **Average price £18.692**; MoM (dic 790.652 → ene 861.831).
- **Snapshot EV**: EV dealers **3.257**, electric rooftops **6.982**, EV listings **65.611**, **Average DOM 65 días**, **Average price £24.261** (dic £24.747 → softening).
- **Price Band Breakdown** (ICE y EV): listings por banda **£0-10K / 10-20K / 20-30K / 30-40K / 40-50K / 50K+**.
- **Dealer Distribution by Inventory Volume** (nº dealers por tamaño de stock: 0-100 / 101-250 / 251-500 / 500-1.000 / 1.000+).
- **Top 100 dealers vs resto** (ICE y EV): stock, **Average DOM**, average price, **market share** (top 100 ICE ≈ 40%; DOM 55 vs 96 días).
- **EV vs ICE**: **EV share 7,61%** (dic 6,74%), non-EV 92,39%; **EV premium > £6.000**; DOM EV 65 vs ICE 80.
- **Top 10 Electric Models** (ranking por listings: Tesla Model 3 4.026, Model Y 2.602, Nissan Leaf 1.866…).
- Métricas que **NO** trae el informe: desglose regional, perfil de edad del vehículo, datos de híbridos, métricas de demanda real (inquiries/conversión), cambio MoM de precio ICE.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Agregador "neutral" API-first a escala continental**: 290B data points / 3.5B listings / 100k+ webs diarias (US-CA) — dato crudo de mercado en tiempo real, no una "cote"/guía editorial. Se posiciona como **"largest neutral data provider"** que **alimenta a portales, value guides y reporting agencies** (es decir, infraestructura de datos de terceros).
- [V] **Listings vivos + ~110 data points por anuncio** con historial por VIN (precio/km hasta 6 años), `dom`/`dos`, first/last seen — granularidad de anuncio individual que las guías de valoración no exponen.
- [V] **NeoVIN**: build-data VIN-level que **reconstruye opciones/packages aunque no estén en el anuncio ni en el window sticker** (post-1997), con `build_code` y MSRP combinado — profundidad de spec por VIN poco común.
- [V] **MDS + Sales Stats (ventas inferidas)** y **Popular Cars**: métricas de oferta/demanda/velocidad calculadas desde la desaparición de listings — inteligencia de rotación que un editor de valores no da.
- [V] **Pricing transparente por llamada + self-service** (free tier 500 calls, $299/$749, white-label en Standard) — onboarding de desarrollador inmediato, frente al modelo "contacta a ventas" de los incumbentes europeos.
- [V] **Cobertura tri-país unificada (US/Canadá/UK)** bajo una misma API v2 y un mismo esquema — raro entre proveedores regionales.
- [V] **Productos verticales de inversión** (Investor Reports, entrada en Investment Funds 2025): targets de adquisición, takeover, outliers, benchmarking de PLC — orientado a M&A/equity, no solo a concesionario.
- [V] **Auction Stock Analysis (UK)**: FMV por regresión + Price Predictor IA + **margin gap vs hammer price** + time-to-prep/retail-turnover — caso de uso de arbitraje de subasta accionable vía simple CSV.
- [V] **Informes de market intelligence públicos y frecuentes** (mensual/semanal, gratis para prensa) con segmentación **EV vs ICE** sistemática y bandas de precio/distribución de dealers — buen "termómetro" de marca.
- [V] **Datos preparados para LLMs/agentes de IA** (vertical declarada) — posicionamiento hacia clientes IA.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **No es una guía de valor editorial / trade-retail-wholesale discretos**: su valoración es **un único `marketcheck_price` predicho + distribución de comparables**; **no hay campos** etiquetados "trade value", "retail value", "wholesale", "residual value %", "future value", "price-to-market %", "depreciation curve" ni "mileage adjustment" como índices normalizados nombrados (el cliente los deriva de stats/comparables). Contraste fuerte con Glass's/cap hpi/Eurotax.
- [V] **Sin valores residuales / forecasting de RV** como producto (no compite con Autovista Compare / cap Future Values).
- [V] **Sin TCO / running costs / SMR** (tiempos de mano de obra, precios de pieza, calendario de mantenimiento) — no hay catálogo de reparación.
- [V] **Ventas "inferidas", no transaccionales reales**: MDS/Sales Stats infieren venta por desaparición de listing; no son matrículas/transacciones verificadas (riesgo de sesgo).
- [V] **Provenance limitada / dependiente de terceros**: title/branding y plate-to-VIN se **revenden** (VINData, CarsXE); no hay informe propio de siniestros/historial de propietarios/fraude de km tipo HPI Check/Carfax. UK ofrece "Validate Car Listing History by VRM" pero como check de listing, no provenance oficial completa.
- [V] **Verticales no-coche (RV/moto/heavy-equipment) solo en EE.UU.**; UK/Canadá = solo coches (+ vans EV en informes).
- [V] **Histórico desigual**: VIN History "6 años" (US) vs "2 años / 90 días" (UK); UK trackeado solo desde **enero 2021**.
- [V] **Informes de mercado sin dimensión regional ni perfil de edad** (ausentes en el informe enero-2026 verificado); sin métricas de demanda real (inquiries/conversión).
- [V] **Reviews públicas escasas**: Datarade "not enough reviews and ratings" — poca validación social independiente verificable.
- [V] **Discrepancia de gobierno corporativo no resuelta públicamente**: rol CEO/President de Troy vs Dan Campbell difiere entre la propia web UK y los agregadores (ver §1).
- [V] **Fundación ambigua** (2010 vs 2012 vs "desde 2014/2015") y **facturación no divulgada**.
- [A] **Sin marketplace transaccional propio** ni motor de reprise/lead B2C tipo autobiz; el widget UK capta financiación, no compra de coche al particular.
- [A] **Calidad de specs fuera de Norteamérica**: NeoVIN nació sobre datos US (post-1997, MSRP en USD); profundidad equivalente en UK/EU no está verificada.

---

## 10. Fuentes (URLs)
- https://marketcheck.uk/ — home UK: live pricing, 680k adverts / 11k dealers, DVLA/SMMT.
- https://marketcheck.uk/about — identidad: MarketCheck Cars Inc, lanzamiento UK ene-2022, ~40 devs in-house (India), Google Cloud+AWS, 200+ clientes, liderazgo (Troy/Dan Campbell, Mahajan co-CTOs).
- https://marketcheck.uk/products — catálogo UK: Car Search Widget, APIs, Integrations, Data Feeds, Investor Reports, Dealer Email & Data Lists, Auction Stock Analysis, MarketCheck Price™.
- https://marketcheck.uk/products/auction-stock-analysis — Fair Market Value (regresión MMV+mileage+age), Price Predictor (IA), margin gap vs hammer, first/last seen, time to prep, retail turnover, CSV upload, 650k+/día.
- https://marketcheck.uk/products/used-car-market-data-api — 10k dealers/14k ubicaciones/1B data points, VRM, 90 días, campos build/price/history(2y), SFTP, apidocs.marketcheck.uk.
- https://marketcheck.uk/products/integrated-car-search — widget WordPress, ~13 filtros (FCA, write-off CAT, VRM…), CRM AutoConvert, favouriting.
- https://marketcheck.uk/products/investor-reports — Market-Wide/Dealer-Level/MDS/Competitive/Pricing Intelligence, targets de adquisición, 150+ companies.
- https://marketcheck.uk/automotive-sectors — 6 sectores (dealers, insurance, finance lenders/brokers, investors, software providers, AI-first startups) + métricas por sector.
- https://marketcheck.uk/resources y /market-analysis-reports — informes mensuales/semanales; press EV/BYD; blogs.
- https://marketcheck.uk/market-analysis/january-2026/uk-monthly-used-car-market-data-january-2026 — informe verificado: snapshots ICE/EV, price bands, dealer distribution, top-100 vs resto, EV share 7,61%, top-10 EV models.
- https://www.marketcheck.com/ — matriz: 290B data points, 3.5B listings, 100k webs/día, 100ms, NeoVIN, MarketCheck Price™, Chrome Extension, oficina 7 Bell Yard London.
- https://www.marketcheck.com/apis/ — catálogo de APIs con **precio por llamada** (Inventory $0.002 … NeoVIN $0.08 … Syndication $1.00 + APIs de terceros).
- https://www.marketcheck.com/apis/cars/ — endpoints v2 (paths `/v2/search/car/active`, `/v2/history/car/{vin}`, `/v2/mds/car`, `/v2/sales/car`, `/v2/popular/cars`, `/v2/dealers/car`, incentive, autorecalls).
- https://www.marketcheck.com/apis/pricing/ — tiers Free/Basic $299/Standard $749/Enterprise, data costs, billing mensual, umbral $1000.
- https://www.marketcheck.com/marketcheck-price/ y https://docs.marketcheck.com/docs/api/cars/market-insights/marketcheck-price — MarketCheck Price™: tiers Base/Premium/Premium Plus, marketcheck_price, comparables, stats, decode NeoVIN, precisión ±4-5%, 84k dealers/262M VINs/540M listings.
- https://www.marketcheck.com/data_feed/neovin/ y https://docs.marketcheck.com/docs/api/cars/vehicle-specs/neovin — NeoVIN: esquema de campos completo (build_code, options_packages, installed_options_details, confidence scores, MSRP fields, dimensiones).
- https://docs.marketcheck.com/docs/api/cars/vehicle-specs/available-options — Available Options Packages.
- https://docs.marketcheck.com/docs/guides/data/introduction — 100k+ webs/día, DOM/DOS, inventory/incentives/recalls, verticales (cars/RV/moto/heavy-equipment).
- https://docs.marketcheck.com/docs/guides/data/cars/inventory/data-definitions — diccionario de campos del listing (~110 data points, citado arriba uno a uno).
- https://docs.marketcheck.com/docs/api/cars/inventory/inventory-search — 112 parámetros + campos de respuesta + stats fields + range_facets.
- https://docs.marketcheck.com/docs/api/cars/market-insights/market-days-supply — fórmula MDS (45 días), `mds`/`total_active_cars_for_ymmt`/`total_cars_sold_in_last_45_days`.
- https://docs.marketcheck.com/docs/get-started/api/introduction — lista de endpoints (cars/RV/moto/heavy-equipment), base URL, auth.
- https://datarade.ai/data-providers/marketcheck/profile — datasets, "start at $8", "largest neutral data provider", "100% QA", reviews insuficientes, USA/Canadá.
- https://webflow2.neudata.co/1/vendors/marketcheck — independiente: fundación 2012, "remote only" (origen Lehi UT), 64 empleados, privately owned, "desde 2012", entrada Investment Funds 2025.
- ZoomInfo (MarketCheck Cars Inc, 435939269 — HQ Lehi UT 84043), Crunchbase, Tracxn, Owler, Gust, LinkedIn (troycampbell67 = "President and Co-Founder") — verificación cruzada de identidad/fundadores/HQ.
- market-intelligence.marketcheck.uk y market-intelligence.marketcheck.com — **NXDOMAIN** (no resuelven; "market-intelligence" es etiqueta de categoría, no host).
- apidocs.marketcheck.uk — **301 → docs.marketcheck.com** (docs UK unificadas con las globales).

> Verificación: identidad corporativa contrastada con ≥3 fuentes independientes (about-us + Neudata + ZoomInfo/LinkedIn). Esquema de campos [V] leído directamente del diccionario de datos y la referencia de API (docs.marketcheck.com). Precios [V] de apis/ + apis/pricing/. Informe de mercado [V] de un PDF/página mensual real (enero-2026). Discrepancias (rol CEO/President, año de fundación, cifras 200 vs 150 clientes, histórico 6y vs 2y) marcadas explícitamente, no resueltas por invención. Subdominio "market-intelligence" = etiqueta taxonómica del orquestador (NXDOMAIN como host), confirmado contra `_audit_input.json`.
