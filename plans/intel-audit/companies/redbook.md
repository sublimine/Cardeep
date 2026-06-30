# RedBook — Auditoría atómica

> **slug:** `redbook` · **subdominio de audit:** `valuation` · **web:** https://www.redbook.com.au/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído, `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** el **benchmark histórico** de valoración de coche (usado y nuevo) de **Australia + APAC**, parte de
> **CAR Group** (dueño de carsales). Su foso: **feed diario auténtico y exclusivo de la red carsales** (el mayor marketplace AU)
> que alimenta una **Real Time Valuation (RTV)** ajustada por km/margen/condición, **days-to-sell** y **market days' supply** en vivo.
> Profundidad atómica fuerte en valoración (4 tipos de precio × 6 condiciones × 10 plates × bandas de km), specs (800+ atributos),
> identificación (VIN/Rego→RedBook ID, opciones de fábrica, NEVDIS, VFACTS, PPSR) y forecast residual (PredictRV PRO, hasta 5 años).
> Es un **patrón directo a copiar** para la ficha de valoración + panel de mercado de cardeep.

> **Aviso de desambiguación (crítico):** existen ≥4 "Red Book" distintos. Este informe cubre **RedBook de CAR Group (Australia/APAC)**.
> NO confundir con: **cap hpi "Red Book"** (Reino Unido, grupo Solera — auditado aparte en `cap-hpi.md`), **"Auto Red Book" / Price Digests**
> (Norteamérica), ni el **RICS "Red Book"** (estándar de valoración inmobiliaria, sin relación). [VERIFICADO ≥2: cap-hpi.com, pricedigests.com, rics.org]

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **RedBook** (estilizado "RedBook"; consumidor "redbook.com.au") | [VERIFICADO] |
| Razón social | **Automotive Data Services Pty Ltd** (trading as Red Book) — ABN 21 001 680 593 | [VERIFICADO ≥2: treasury.gov.au PDF, ACCC merger register] |
| Grupo / owner | **CAR Group Limited** (ASX: **CAR**) — vía su filial **carsales.com.au Pty Ltd** | [VERIFICADO ≥2: búsqueda corporativa, Wikipedia CAR Group, business.carsales.com.au] |
| Rebranding del grupo | "carsales.com Limited" → **CAR Group Limited** en **2023** (refleja escala fuera de AU) | [VERIFICADO] |
| Adquisición | carsales.com.au Limited adquirió Automotive Data Services (Red Book) el **31-ago-2007** | [VERIFICADO ≥2: ACCC public register, búsqueda] |
| Fundación | Fundada en **Sídney** por **Keith Halfhide** en los **años 1940**; primera circulación formal de "The RedBook" en **1949** | [VERIFICADO: redbook about-us snippet + redbook.co.nz/about-us] |
| Histórico de datos | Precios usados individuales que se remontan a **1935**; specs desde **1960**; 10M+ registros de venta desde **1950** | [VERIFICADO ≥2: búsqueda about + commercial product pages] |
| HQ | **Sídney, Australia** | [VERIFICADO] |
| Antigüedad declarada | "más de 70 años" operando | [VERIFICADO: business.carsales] |
| Posicionamiento | "líder tecnológico que aplica machine learning y AI" en specs, pricing analysis, valuations y forecasting | [VERIFICADO: business.carsales/redbook] |
| Email comercial | info@redbook.com.au | [VERIFICADO] |

**Qué es:** negocio de **datos e inteligencia de automoción** que suministra a la industria **identificación de vehículo**,
**datos técnicos/specs**, **valoración** (usada actual/histórica, tiempo real, residual/forecast), **costes de explotación**,
**imágenes** y **market intelligence**, sirviéndose del acceso exclusivo a la red carsales.

### Categorías de producto
1. **Pricing & Valuations** (usado actual/histórico, **RTV** tiempo real, residual/forecast) — núcleo.
2. **Vehicle Identification** (VIN/Rego → **RedBook ID**, opciones de fábrica, VFACTS).
3. **Vehicle Specifications** (800+ atributos técnicos).
4. **NEVDIS** (rego→VIN, registration status, written-off, stolen — broker autorizado).
5. **PPSR Certificate** (encumbrance / finance owing / certificado de gravámenes).
6. **Cost to Own / Cost to Run** (TCO/TCR — coste whole-of-life).
7. **PredictRV PRO** (forecast de valor residual usado, "ahead of the market").
8. **Marketplace LIVE Reports / RedBook LIVE / LiveMarket** (market intelligence: days-to-sell, days' supply, price movements).
9. **Digital Image Library** (biblioteca de imágenes por variante).
10. **Fleetmaster** (portal web — canal de entrega de casi todo lo anterior).
11. **Consulting Services** (análisis bespoke).

### Cliente objetivo (8 sectores declarados)
**Financial Services** · **Fleet Management** · **Insurance** · **OEM** (fabricantes) · **Professional Services** ·
**Aftermarket** · **Government** (departamentos) · **Automotive Dealers**. [VERIFICADO ≥2: commercial homepage + páginas de sector]

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado principal | **Australia** (donde vive todo el dato atómico: pricing carsales, specs, NEVDIS) | [VERIFICADO] |
| Países (APAC + Golfo) | **8 mercados**: **Australia, Nueva Zelanda, China, Hong Kong, Malasia, Tailandia, Singapur, Emiratos Árabes Unidos (UAE)** | [VERIFICADO ≥2: redbookasiapacific.com + redbook.co.nz/about] |
| Portales por país | redbook.com.au · redbook.co.nz · redbook.net.cn · redbook.com.hk · redbook.com.my · redbook.co.th · redbook.com.sg · redbook.ae | [VERIFICADO: redbookasiapacific.com] |
| Indonesia | Mencionado en algún material de carsales como región servida | [NO-VERIFICADO — no aparece en el listado autoritativo de 8 de redbookasiapacific.com] |
| Scope temporal | Usado **y nuevo**; pricing histórico a 1935, specs a 1960 | [VERIFICADO] |
| Tipos de vehículo | **Cars, SUVs, Light Commercial Vehicles (LCV), Trucks, Motorbikes/Bikes, Boats/Marine, Caravans** | [VERIFICADO ≥2: pricing-and-valuations + vehicle-specifications] |
| Segmentos en API | `car`, `bike`, `heavy`, `marine`, `caravan` (path param `segment`) | [VERIFICADO: swagger api.redbookdirect.com] |
| Volumen de catálogo | **2.000+ modelos** de todos los fabricantes; **50.000+ variants** (consumidor cita "65.000+ models"); **800+ atributos** de spec; **8M data attributes** investigados/año | [VERIFICADO ≥2: business.carsales + vehicle-specifications + government] |
| Base de transacciones | **10M+ registros reales** de venta de usado (desde 1950) | [VERIFICADO ≥2: búsqueda pricing] |
| Granularidad de valoración | por **make → family/model → year group → variant (RedBook Code)**; histórico mensual hasta **3 años atrás**; forecast hasta **5 años** (con scope para ir más allá) | [VERIFICADO ≥2: web lookup help + financial-services] |

---

## 3. Productos + campos atómicos

> Notación: campos confirmados en página de producto / OpenAPI (`api.redbookdirect.com/swagger/v1/swagger.json`) / pantallas del web-lookup
> (capturas de ayuda de redbookasiapacific.com). Donde la página es solo marketing, se marca el hueco.

### 3.1 Pricing & Valuations — núcleo (RTV + Used Prices + Residuals)
**Qué es:** suite de precios para usado/nuevo. **RTV (Real Time Valuation)**: precios diarios dinámicos ajustados por km/margen/condición,
con `pricing scores` y `average days to sell`. Servido por API v3 y portal Fleetmaster.

**Tipos de precio (price types):** [VERIFICADO ≥2: swagger enum + web lookup + consumidor]
- `wholesale` (mayorista / trade entre empresas, base de subasta)
- `retail` (dealer retail — lo que un dealer vende)
- `tradein` (trade-in — oferta de un dealer al recibir el coche a cambio)
- `private` (venta particular a particular; típicamente < retail)
- `RRP` / `New Price` (precio nuevo / lista del fabricante)

**Condiciones (6 grados):** `poor`, `fair`, `average`, `good`, `verygood`, `asnew` (Poor, Fair, Average, Good, Very Good, As New) [VERIFICADO ≥2: swagger enum + pantalla AutoCalc]
- Definiciones editoriales por grado (km esperados, estado mecánico, daños, historial de servicio) — p.ej. *Average*≈30.000 km/año, *Good*≈20.000 km/año, *As New* = "show room condition, no money to spend". [VERIFICADO: captura AutoCalc condition definitions]

**RTV (Real Time Valuation) — campos / parámetros:** [VERIFICADO: swagger `AU Car v3 Pricing`]
- `rtvType`: **Base** (vehículo base) vs **Market** (option-equipped — valor con opciones de mercado)
- `pointInTime`: `current` o fecha `yyyy-MM-dd`
- valor por `priceType` × `condition`
- **AutoCalc**: ajuste por `km` + `condition` → `Adjustment %` → `Adjusted Price` (por cada price type)
- RTV **history** (autocalc histórico) — `historyCount` 1-90 días
- `pricing score` (puntuación de confianza del precio)
- `average days to sell` (días medios hasta venta)

**Used Prices / Price Guide — campos:** [VERIFICADO: swagger `Pricing` + `usedprices`]
- precio por `priceType` y `condition` en `pointInTime` (current o histórico)
- versión `autocalc` (ajuste por km/condición) y `history/autocalc`
- precio de **opciones** (`VehicleOptions/{id}/usedprices`) y de **after-market options** (`AfterMarketOptions/{id}/usedprices`)
- entradas de cálculo: `km`/`kms` (lista), `accessoriesCost`, `optionIds` (lista)

**Residuals / Forecast — campos:** [VERIFICADO: swagger `residuals` + `forecast`]
- `Predicted Residual` por `vehicleAgeYears` (1-10)
- forecast `with-redbook-pricing` (con pricing RedBook) vs `with-user-price` (precio definido por usuario)
- parámetros de forecast: `annualKm`, `expectedEndKm`, `startKm`, `startPrice`, `startPriceType`, `startPriceVehicleCondition`, `periodType` (daily/monthly/yearly), `periodPoints`
- valor residual expresado en **% y monetario** (ver Price Ahead, §7)

### 3.2 PredictRV PRO — forecast de residual ("ahead of the market")
**Qué es:** forecast forward de valor de usado a nivel granular para financieras/leasing. [VERIFICADO: financial-services]
**Campos atómicos:**
- Forecast por **make, model, year, variant**
- Horizonte: **hasta 5 años** (con scope para ir más allá); **actualización trimestral** + ad-hoc por lanzamiento de modelo
- Supuestos ajustables: **kilometres per year**, **vehicle condition**
- `end-of-term value` (valor a fin de contrato/lease)
- `downside risk` (identificación de riesgo a la baja)
- `contract equity` targeting (equidad de contrato)
- `provisioning values` (provisión financiera) · `portfolio risk assessment`
- Tipos de precio y condición variables; escenarios customizables

### 3.3 Vehicle Identification — VIN/Rego → RedBook ID
**Qué es:** match de Registration o VIN al **RedBook ID** único, con detalle a nivel de variante y opciones de fábrica. [VERIFICADO ≥2: vehicle-identification + swagger `VIN Rego`]
**Campos / endpoints atómicos:**
- `RedBook Code` / `RedBook ID` (RBC) · `RedbookCodeLegacy` · `VehicleId`
- `VIN` (17 caracteres) · `Registration` (rego) + `state`
- `Make`, `Family`/`model`, `Year Group`, `variant`, `Series`, `Model Code`
- `Build date` / `Compliance date` (NEVDIS) · `Vehicle Age` · `vehicleYear`
- `Power to Weight` ratio
- **Factory-fitted options** identificadas por VIN (datos de fábrica autorizados FCAI/OEM, desde 2010)
- variantes de endpoint: `findbyvinplus`, `findbyvinpluswithdate`, `findbyregoplus`, `findbyvinenhanced`, `findbyvinenhancedoptions`, `findbyregoenhanced` (+ familia `-cb` "extra data package", + entorno `test`)
- "Help me choose" — **drop-down menu** para seleccionar vehículo sin VIN/rego (árbol de preguntas, ver VehicleBrowse)
- fuentes: datos propietarios RedBook + FCAI + NEVDIS + **Register of Approved Vehicles (RAV)**

### 3.4 VFACTS — build & paint por VIN
**Qué es:** datos VFACTS de construcción y pintura por VIN. [VERIFICADO: swagger `VFACTS`]
- `/vfacts/build/{vin}` → datos de **build**
- `/vfacts/paint/{vin}` → datos de **paint** (pintura/color de fábrica)

### 3.5 NEVDIS — registro nacional (broker autorizado)
**Qué es:** acceso vía API a la base **NEVDIS** (National Exchange of Vehicle and Driver Information System), agregada de las **8 autoridades de tránsito** estatales/territoriales AU (vía Austroads). [VERIFICADO ≥2: nevdis + vehicle-identification]
**Calls / campos disponibles:**
- `Plate to VIN` (rego → VIN)
- `Vehicle Details`
- `Build/Compliance date`
- `Vehicle Age`
- `Registration Status` (estado de matriculación)
- `Power to Weight`
- `Written Off History` (historial de siniestro total)
- `Stolen Check` (comprobación de robo)

### 3.6 PPSR Certificate — gravámenes / finance owing
**Qué es:** broker de certificado **PPSR** (Personal Property Securities Register). [VERIFICADO: swagger `PpsrCertificate`]
- `create-by-vin` (requiere `vin`; marine requiere `hin`)
- `create-by-rego/{rego}` (VIN resuelto vía NEVDIS)
- `status/{referenceId}` (estado de procesamiento)
- `generateReport` → datos planos del informe PPSR (URLs de certificado, etc.)
- segmentos no-marine usan `vin`; marine usa `hin` (Hull Identification Number)

### 3.7 Vehicle Specifications — 800+ atributos
**Qué es:** specs técnicas de todos los vehículos importados oficialmente a AU (50.000+ variants, desde 1960). [VERIFICADO ≥2: vehicle-specifications + government]
**Campos atómicos VERIFICADOS (captura de la pestaña "Vehicle Specifications" del web-lookup):**
- *Identification:* `Release Date`, `Body Style`, `Doors`, `Seat Capacity`, `Series`, `Model Code`, `VIN`
- *Drive Train:* `Drive` (p.ej. Rear Wheel Drive), `Transmission` (p.ej. 4sp Automatic), `Gear Location`, `Steering` (p.ej. Rack and Pinion)
- *Engine:* `Engine Size` (cc), `Cylinders`, `Engine Configuration` (p.ej. V90), `Cam` (p.ej. Pushrod), `Valves Per Cylinder`, `Compression Ratio`, `Engine Cycle` (4 Stroke), `Engine Type` (Piston), `Engine Location` (Front), `Engine Num`
- *Fuel:* `Fuel Type` (p.ej. Petrol - Unleaded ULP), `RON Rating`, `Fuel Capacity` (L), `Fuel Delivery` (Multi-Point Injected), `Method Of Delivery` (Electronic Sequential), `Induction` (Aspirated/Turbo)
- *Specifications / Performance:* `Power` (kW @ RPM), `Torque` (Nm @ RPM), `Acceleration 0-100 Km/h` (s), `Fuel Consumption Urban` (L/100km), `Fuel Consumption Extra Urban`, `Fuel Consumption Combined`, `CO2` (g/km)
**Campos adicionales (consumidor / sector, no en la captura):**
- `ANCAP Safety Rating`, `Vehicle Emissions Star Rating` (contaminación del aire), `Green Star`/`Greenhouse Rating`, `Engine Description`, `Turbo` [VERIFICADO: búsqueda consumer spec page]
- `Dimensions`, `Weights`/`Tare weight`, `Electric vehicle plug type`, perfiles de emisiones, safety credentials [VERIFICADO: government + aftermarket; campos individuales no enumerados]
- `Standard Equipment` (lista) · `Optional/Factory Options` (cada uno con precio) · `After Market Options` · `Manufacturer colours` [VERIFICADO: Main Vehicle Workscreen + swagger `standards`/`options`/`colours`]
- Agrupación: la API expone `Vehicles/{rbc}/attributes` (atributos en lista con meta-data), `standards`, `options`, `colours`, `media`, `Equipment`, `AfterMarketOptions`, `WithdrawnVehicles`, `VehicleAspect` (agrupación + conteos) [VERIFICADO: swagger]

### 3.8 Cost to Own (CTO) / Cost to Run (CTR)
**Qué es:** coste whole-of-life más allá del precio de compra. **Hasta 5 años / 75.000 km**, vehículos **MY2022+**, cars/SUV/LCV. [VERIFICADO ≥2: cost-to-own + fleet-management]
**Componentes (campos):**
- `Fuel/Energy costs` (incluye energía de **vehículo eléctrico**)
- `On-road costs` (registration, government duties, third-party/CTP insurance, levies)
- `Comprehensive insurance`
- `Tyre` expenses
- `Servicing` (mantenimiento programado)
- `Finance costs` (solo **CTO**)
- `Depreciation` (solo **CTO**)

### 3.9 Marketplace LIVE Reports / RedBook LIVE / LiveMarket
**Qué es:** "Vehicle Intelligence & Insights" — pricing diario, tendencias y transparencia de opciones de fábrica a nivel VIN; informe pre-accidente para seguros. [VERIFICADO ≥2: marketplace-live-reports + insurance + carsales news]
**Campos / elementos de informe:**
- `Confidence Score` (fiabilidad de la valoración según dato dinámico diario)
- `Price History` graphs (gráficos de histórico de precio)
- `Market Comparisons` — listings **live y delisted** (activos y retirados)
- `Factory Options` breakdown (desglose por opción de fábrica + contribución al valor)
- `Accessories` detail (aftermarket / dealer-installed)
- `Estimated Repair Costs`
- `Pre-Accident Valuation` (informe pre-siniestro)
- `Damage Assessment` (provisiones, `reference numbers`, `notes`)
- **LiveMarket dashboard:** `Stock Volume` advertised online, `Average Time to Sell`, `Days' Supply`, `Price Movements`, `Benchmarking` vs inventario activo

### 3.10 Digital Image Library
**Qué es:** una de las mayores bibliotecas propietarias de imágenes de automoción de AU. [VERIFICADO ≥2: digital-image-library + government]
**Campos atómicos:**
- Hasta **20 composiciones interior/exterior** por **variante**
- Fondos: **clean (blanco)** o **generic retail dealership setting**
- Todas con **watermark RedBook**
- Acceso vía **API usando RedBook code bajo licencia**

### 3.11 Datos de referencia / taxonomía (API "RedBook Data")
[VERIFICADO: swagger]
- `Makes` (`makeId`, `makeName`) · `Families` (`familyId`) · `YearGroups` (`yearGroupId`) · `Vehicles` (`rbc`)
- `VehicleBrowse` — navegación por **árbol de preguntas** (`QuestionVM`: `aspectName`, `answers[]` con `value`, `displayText`, `vehicleCount`)
- `VehicleAspect/{aspect}` — agrupación por aspecto + conteo de vehículos
- `WithdrawnVehicles` (vehículos retirados)
- filtros sobre la mayoría de atributos con operadores: `year=range(2015..2019)`, `BodyStyle=in(Sedan,Wagon)`, `makeid=`; `projection` para elegir campos de salida; `limit`/`offset` para paginación

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Fuente primaria de pricing | **Feeds diarios exclusivos y auténticos de la red carsales** (carsales.com.au + verticales) — el mayor marketplace online de AU | [VERIFICADO ≥2: pricing-and-valuations + business.carsales] |
| Fuentes wholesale | **auction houses** + **dealer networks** + datos tradicionales de mayorista | [VERIFICADO ≥2: pricing-and-valuations + búsqueda] |
| Base histórica | **10M+ registros reales** de venta de usado desde 1950; precios individuales a 1935 | [VERIFICADO ≥2] |
| Catálogo | 2.000+ modelos · 50.000-65.000 variants · **800+ spec attributes** · **8M data attributes** investigados/año | [VERIFICADO ≥2] |
| Datos de fábrica | **FCAI**/OEM-authorised factory specification & options data (desde 2010); **VFACTS** build & paint | [VERIFICADO ≥2: vehicle-identification + swagger] |
| Identidad/estado | **NEVDIS** (8 autoridades de tránsito vía Austroads), **Register of Approved Vehicles (RAV)**, **PPSR** | [VERIFICADO ≥2: nevdis + swagger] |
| Técnica analítica | **machine learning + AI** aplicados a specs, pricing analysis, valuations y forecasting | [VERIFICADO: business.carsales] |
| Señales de mercado | `live vs delisted listings`, `stock volume`, `days to sell`, `days' supply`, `price movements` → `confidence score` y `pricing score` | [VERIFICADO ≥2] |
| Frecuencia | **diaria** (RTV, RedBook LIVE, Fleetmaster); residual forecast **trimestral** + ad-hoc | [VERIFICADO ≥2] |

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **API REST** | **RedBook Direct API** (`api.redbookdirect.com`) — OpenAPI 3.0.4; auth por `x-api-key` → access token + refresh token (`/token`, `/token/refresh`, headers `x-accesstoken`/`x-refreshtoken`); `projection`, `limit`/`offset`, filtros con operadores `range()`/`in()`; 67 endpoints; servidor de producción | [VERIFICADO: swagger.json descargado] |
| **API "Enhanced"/CB** | familia `-cb` ("extra data package") y endpoints `enhanced`/`enhancedoptions` para identificación enriquecida | [VERIFICADO: swagger] |
| **Secure FTP / ficheros** | "Available via API or **secure FTP**" para heavy, caravan, marine y data sets; **flat file** bajo licencia para specs | [VERIFICADO ≥2: researched-vehicles + vehicle-specifications] |
| **Portal web — Fleetmaster** | portal online "anywhere, any time": identificación + pricing diario, RTV, AutoCalc, specs, model history, price trend graphs, imágenes, cost-to-own, insights dashboard, compare basket, favourites | [VERIFICADO ≥2: fleetmaster + web-lookup help] |
| **Web-lookup (consumer/AP)** | herramienta de lookup con pantallas: Vehicle Browse, Main Vehicle Workscreen, AutoCalc, Vehicle Specifications, Photos, Model History, Price Ahead, Price History, Trend Graph | [VERIFICADO: redbookasiapacific weblookup help] |
| **RedBook LIVE** | dashboard/informe diario de market intelligence (insurers, dealers, fleet, finance) | [VERIFICADO ≥2] |
| **Informe PDF (consumidor)** | **RedBook Valuation Report** ("What's that vehicle worth?") — informe de pago | [VERIFICADO ≥2: redbook valuation-report + búsqueda] |
| **Integración DMS / 3rd-party** | integración con la mayoría de proveedores DMS; plataforma de inventario **carsales AutoGate**; powering de trade-in calculators y CRM cleansing | [VERIFICADO ≥2: automotive-dealers] |
| **Consulting Services** | análisis bespoke (portfolio, TCO studies) | [VERIFICADO ≥2: fleet-management + financial-services] |

---

## 6. Precio

| Aspecto | Detalle | Estado |
|---|---|---|
| Modelo B2B | **Quote-based / a medida** según necesidad y uso; vía "Enquire Now" en commercial.redbook.com.au | [VERIFICADO: búsqueda pricing] |
| Suscripciones Fleetmaster | **suscripción web anual** (individuos) + **bulk subscriptions** (organizaciones grandes) + **single lookups** | [VERIFICADO: búsqueda pricing] |
| API | licencia comercial (acceso por `x-api-key`); sin free tier público ni sandbox abierto | [VERIFICADO: swagger requiere api key] |
| Consumidor | **RedBook Valuation Report = AU$33** (informe personalizado de un vehículo); rangos de precio básicos (private/trade-in/dealer) gratis en redbook.com.au | [VERIFICADO ≥2: búsqueda valuation-report (precio $33), redbook FAQ] |
| Tarifa pública B2B | **No publicada** | [VERIFICADO] |

---

## 7. Placement (patrón web a copiar por cardeep)

> Cómo RedBook **coloca cada dato en su UI** (web-lookup / Fleetmaster + RedBook LIVE + informe consumidor).
> Es el blueprint para ubicar cada métrica en cardeep. Pantallas verificadas por captura.

| Dato | Dónde lo coloca RedBook |
|---|---|
| Selección de vehículo | **Vehicle Browse**: listas Make→Family→Year o **drop-down**, "Browse by Category", "Advanced Search", "Search for Similar Vehicles", o **árbol de preguntas** (VehicleBrowse); alternativamente **VIN/Rego lookup** → RedBook Code |
| Lista de variantes | **Tabla de variantes** tras elegir Make/Family/Year: columnas `RB Code` + **Wholesale/Retail por condición (Average, Good)** + `New Price` (RRP) en una fila por variant |
| Precios base (wholesale/retail/trade/private) | **Main Vehicle Workscreen**: dropdown **"Select Price to View"** (combinación condición+tipo, p.ej. "Good Retail") → `Vehicle Price` + `Option Price` + `Total` como salida principal |
| Equipamiento estándar vs opcional | Main Vehicle Workscreen en **dos paneles**: `Standard Equipment` (izquierda) y `Optional/Factory Options` (derecha, **cada opción con su precio**) + campo "Add Custom Option" (name + value) |
| Ajuste por km y condición | Pestaña **AutoCalc**: selectores `Kilometres` + `Condition` → tabla `Based On` × (`Vehicle Price`, `Option Price`, **`Adjustment %`**, **`Adjusted Price`**) por cada price type |
| Specs técnicas | Pestaña **Vehicle Specifications**: ficha en **categorías colapsables** (Identification, Drive Train, Engine, Fuel, Specifications/Performance…) — par etiqueta/valor |
| Fotos | Pestaña **Photos**: galería de composiciones interior/exterior |
| Historia del modelo | Pestaña **Model History** |
| Forecast residual | Pestaña **Price Ahead**: `New Price (RRP)` arriba + **matriz Age (1-5 años) × bandas de km (10K…150K)**, cada celda con **% residual + valor $** |
| Valor en el pasado | **Price History**: dropdown **"Select Point in Time"** (mensual, hasta 3 años atrás) → re-renderiza el workscreen al valor de esa fecha |
| Curva de depreciación | Pestaña **Trend Graph**: gráfico de línea de precio en el tiempo por price type + condición; RRP superponible |
| Comparación | **Add to Compare Basket** → comparación lado a lado de specs/precios de varios vehículos |
| Confidence score / market comparison | **RedBook LIVE report**: `confidence score`, `price history graph`, `market comparison` (live vs delisted), desglose de factory options/accessories, `estimated repair costs`, `pre-accident valuation`, notas/reference de damage assessment |
| Days-to-sell / days' supply / stock | **LiveMarket dashboard**: `stock volume`, `average time to sell`, `days' supply`, `price movements`, benchmarking |
| Valoración consumidor | **Informe PDF "Valuation Report"** ($33): rangos `trade-in` / `private` / `dealer retail` ajustados por `kilometres` + `condition` |
| Acceso programático | **API REST + secure FTP + flat file** embebidos en DMS/sistemas del cliente (sin UI propia) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Foso de dato carsales**: acceso **exclusivo y auténtico** al feed diario de la mayor red de marketplace de AU (carsales + verticales), con **listings live y delisted** — pocos competidores tienen una fuente de transacción/anuncio propia de esa escala dentro del mismo grupo.
2. **RTV (Real Time Valuation) diaria**: precio dinámico ajustado por **km/margen/condición**, con distinción **Base vs Market** (vehículo base vs option-equipped) — granularidad atómica.
3. **Market intelligence nativo**: `days-to-sell`, `market days' supply`, `price movements`, `stock volume` y `confidence/pricing scores` derivados del marketplace en vivo (equivalente a Indicata/Auto Trader, pero alimentado por carsales).
4. **Autoridad histórica APAC**: 75+ años, pricing individual a **1935**, 10M+ ventas desde 1950 — el benchmark de facto en Australia.
5. **PredictRV PRO**: forecast residual forward a **5 años+** por variant, con supuestos de km/condición, downside risk, end-of-term y contract equity.
6. **Identidad y estado completos**: broker **NEVDIS** (rego→VIN, written-off, stolen, reg status, build/compliance de 8 autoridades) + **PPSR** (gravámenes/finance owing) + **VFACTS** build/paint + **factory-fitted options por VIN** (FCAI-authorised) — revela valor oculto.
7. **RedBook ID/Code** como **llave universal** que conecta identificación + specs + pricing + imagen en un solo lenguaje, replicado en 8 países.
8. **Image library propietaria** (hasta 20 composiciones/variante) integrable por código.
9. **Multi-activo**: cars, bikes, trucks (heavy), marine/boats, caravans — no solo turismos.
10. **Pertenencia a CAR Group**: escala, integración con carsales/AutoGate y foso de datos difícil de replicar.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **Transparencia de precio B2B nula**: todo quote-based; sin self-serve pricing público ni free tier/sandbox de API (requiere `x-api-key`).
2. **Geografía APAC + Golfo**: el dato atómico vive en **Australia**; cobertura solo en 8 mercados APAC/UAE. **No hay cobertura de Europa ni América** bajo esta marca (el "Auto Red Book" de Norteamérica es **Price Digests**, empresa distinta; el "Red Book" de UK es **cap hpi/Solera**, distinta). **No cubre España/EU** — relevante para cardeep.
3. **Sin informe de historial completo tipo CARFAX**: solo `written-off`/`stolen`/`registration status` (NEVDIS) + `finance owing` (PPSR). El historial profundo de odómetro/siniestros (CarHistory) es **producto separado de carsales**, no de RedBook.
4. **Schema completo tras login/licencia**: muchas páginas de producto son marketing; la lista exhaustiva de los 800+ atributos y los campos de respuesta del pricing viven en objetos dinámicos de la API (el swagger no los enumera) y requieren credenciales.
5. **Cost-to-Own limitado**: solo **MY2022+**, ≤**5 años / 75.000 km**, y solo **cars/SUV/LCV**.
6. **Motor v3 AU-céntrico**: el forecast/RTV "New Gen" (v3) está marcado como **"works with Australian Cars only"**.
7. **No es marketplace ni huella de punto de venta**: vende el **valor/dato**, no publica inventario ni cataloga dealers/puntos de venta ni su presencia online (territorio propio de cardeep).
8. **Consumidor de pago**: valoración personalizada tras paywall ($33); el dato fino no es libre.
9. **Days-supply / price-to-market**: presentes en los dashboards LIVE, pero **no documentados como campos abiertos de API** públicamente (viven en objetos de respuesta dinámicos). [PARCIAL — no verificado que no existan internamente]
10. **Sin telemática / uso real / comportamiento de conductor** (fuera de scope).

---

## 10. Fuentes (URLs)

**Producto / catálogo (commercial.redbook.com.au)**
- https://commercial.redbook.com.au/ (catálogo de soluciones + sectores)
- https://commercial.redbook.com.au/products/pricing-and-valuations/
- https://commercial.redbook.com.au/products/vehicle-identification/
- https://commercial.redbook.com.au/products/vehicle-specifications/ (800+ attributes)
- https://commercial.redbook.com.au/products/nevdis/
- https://commercial.redbook.com.au/products/cost-to-own/
- https://commercial.redbook.com.au/products/fleetmaster/
- https://commercial.redbook.com.au/products/marketplace-live-reports/ (RedBook LIVE)
- https://commercial.redbook.com.au/products/financial-services/ (PredictRV PRO)
- https://commercial.redbook.com.au/products/digital-image-library/
- https://commercial.redbook.com.au/products/researched-vehicles/ (API/secure FTP)
- https://commercial.redbook.com.au/products/api-user-documentation/
- https://commercial.redbook.com.au/products/insurance/
- https://commercial.redbook.com.au/products/government/
- https://commercial.redbook.com.au/products/fleet-management/
- https://commercial.redbook.com.au/products/oem/
- https://commercial.redbook.com.au/products/aftermarket/
- https://commercial.redbook.com.au/products/professional-services/

**API / entrega**
- https://api.redbookdirect.com/index.html (Swagger UI — RedBook Direct API Production)
- https://api.redbookdirect.com/swagger/v1/swagger.json (OpenAPI 3.0.4: 67 endpoints, tags Authentication/VIN Rego/VIN Rego CB/VFACTS/RedBook Data/AU Car v3 Pricing/Pricing/PpsrCertificate; enums price/condition/rtvType/segment)
- https://business.carsales.com.au/redbook/ (overview + metodología + cobertura)
- https://business.carsales.com.au/news-room/redbook-insider/introducing-redbook-live-vehicle-intelligence-and-insights/

**Web-lookup / placement (capturas de pantalla verificadas)**
- https://www.redbookasiapacific.com/weblookup/help.php (índice de pantallas)
- https://www.redbookasiapacific.com/weblookup/help.php?page=vehiclespecifications (campos de spec)
- .../help.php?page=mainvehicleworkscreen · ?page=autocalc · ?page=priceahead · ?page=pricehistory · ?page=trendgraph · ?page=vehiclebrowse
- (imágenes leídas: au_vehiclespecifications1, au_mainvehicleworkscreen1, au_autocalc1/3, au_priceahead1, au_pricehistory1, au_trendgraph1, au_vehiclebrowse3)

**Consumidor**
- https://www.redbook.com.au/ (sitio consumidor — 403 a bots; vía búsqueda)
- https://www.redbook.com.au/valuation-report/ (Valuation Report — $33)
- https://www.redbook.com.au/info/about-us · https://www.redbook.com.au/info/faqs (definiciones de price type)

**Identidad / corporativo / desambiguación**
- https://www.redbookasiapacific.com/ (8 países)
- https://www.redbook.co.nz/about-us/ (fundación, historia)
- https://en.wikipedia.org/wiki/CAR_Group (owner ASX:CAR)
- https://www.accc.gov.au/public-registers/.../carsalescomau-limited-completed-acquisition-of-red-book (adquisición 2007)
- https://treasury.gov.au/sites/default/files/2024-10/c2021-224294-redbook.pdf (Automotive Data Services Pty Ltd, ABN 21 001 680 593)
- https://pricedigests.com/auto/ (desambiguación: "Auto Red Book" Norteamérica = empresa distinta)
- https://www.cap-hpi.com/products-and-services/red-book (desambiguación: "Red Book" UK = cap hpi/Solera, distinta)
- https://caredge.com/guides/what-are-red-book-values (definiciones de valores)

> **Marcas [NO-VERIFICADO] / inferencias:** Indonesia como país servido (no en listado autoritativo de 8); enumeración completa de los
> 800+ spec attributes (solo subset verificado por captura + sector pages); existencia de `price-to-market %`/`demand index` como campos
> de API (presentes en dashboards LIVE pero no documentados como campos abiertos); detalle de formatos de fichero (CSV/XML/JSON) en secure FTP
> (no especificado en web). Todo lo marcado [VERIFICADO ≥2] tiene doble fuente; el resto, fuente única declarada.
