# cap hpi — Auditoría atómica

> **slug:** `cap-hpi` · **subdominio de audit:** `valuation` · **web:** https://www.cap-hpi.com/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** el **benchmark histórico** de valoración de coche usado en UK (Black Book). Profundidad atómica
> brutal en valoración (trade clean/average/below + retail + future + opciones), specs de coche nuevo (NVD) y provenance
> (HPI Check). Entrega madura (API REST + SOAP + ficheros + portal). Es el patrón a copiar para la ficha de valoración de cardeep.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **cap hpi** (fusión de **CAP** + **HPI**) | [VERIFICADO] |
| Razón social | CAP Automotive Limited (LinkedIn: "cap-automotive-limited") | [VERIFICADO] |
| Grupo / owner | **Solera Holdings** (Solera, Inc.) — proveedor global de soluciones de claims/automoción | [VERIFICADO ≥2: PRNewswire, cap-hpi/about, solera.com] |
| HQ | **Leeds, Reino Unido** (tel. +44 (0)113 222 2000; metodología con University of Leeds ITS) | [VERIFICADO ≥2] |
| Oficina adicional | India (abierta 2009) | [VERIFICADO: cap-hpi/about] |
| Fundación HPI | **1938** — "Britain's first ever vehicle provenance check" | [VERIFICADO ≥2: cap-hpi/about, careers/our-story] |
| Fundación CAP | **1979** — lanzamiento del famoso **Black Book** | [VERIFICADO ≥2] |
| Adquisición por Solera | HPI **2008**; CAP **20-nov-2014** por **$464M**; marcas unificadas como "cap hpi" ~2015 | [VERIFICADO ≥2: PRNewswire, CBInsights/PitchBook]. Nota: cap-hpi/about dice "merged 2015"; perfiles financieros fijan la compra de CAP el 20-nov-2014 |
| Inversores históricos previos | Montagu Private Equity; Ascential (Media & Information Services) | [VERIFICADO: CBInsights] |
| Antigüedad declarada | "Trusted for over 75 years" / "40+ years" de valoración | [VERIFICADO: about / valuation-anywhere] |

**Qué es:** negocio de **datos e inteligencia de automoción** que suministra a la industria valoración de vehículo usado,
datos técnicos de vehículo nuevo (specs/precios), provenance/historial, costes de explotación (SMR/TCO) y soluciones embebidas.

### Categorías de producto
1. **Valoración** (usado actual, future/residual, opciones) — núcleo.
2. **Datos de vehículo nuevo / specs** (NVD, CAP Code, WLTP).
3. **Provenance / historial / compliance** (HPI Check, MOT, write-off, mileage/NMR, recalls, keeper).
4. **Costes de explotación** (SMR, TotalCost/TCO, P11D).
5. **Analítica de mercado / riesgo de activo** (Residual Tracker, Vehicle Census, Insight, Security/Crush/REACT).
6. **Seguros** (Market Value Manager — total loss).
7. **AfterSales / CRM de taller** y herramientas de tasación (Appraisal apps).

### Cliente objetivo (8 sectores declarados)
Dealerships/traders · Fleet, leasing & rental · Motor insurance · Vehicle manufacturers (OEM) ·
Lenders & brokers · Auctions & remarketing · Third-party systems integrators · Consumer services.

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado principal | **Reino Unido** (UK) — donde vive todo el dato atómico (Black Book, HPI Check, NVD UK) | [VERIFICADO] |
| Cobertura parc UK | **99%** del parque UK; **~2M+ vehículos valorados/mes**; "97%+ de los vehículos en circulación actualizados" (HPI) | [VERIFICADO: valuation-anywhere, hpi.co.uk] |
| Internacional (vía Solera) | El **cap hpi code** + **metodología única** se replican por mercado desde un *international hub* en UK; valoración/forecast gestionados por expertos locales. Solera opera en 70-120+ países. Filiales del grupo: **Informex** (Bélgica/Grecia), **Sidexa** (Francia), **ABZ** y **Market Scan** (Países Bajos), **AUTOonline** (Europa + LatAm) | [VERIFICADO ≥2: solera.com, búsqueda] |
| Producto multi-país explícito | **Insight** publica datos de UK **y Países Bajos** (RV, SMR, tyre, insurance, leasing) | [VERIFICADO: insight] |
| Cobertura específica fuera de UK (Irlanda, etc.) | No detallada en web pública de cap-hpi | [NO-VERIFICADO] |

### Scope de vehículo
- **Usado y nuevo.**
- Tipos: **Cars, LCV (vans), HGV (trucks), Bikes/Motorcycles** (Green Book), + grey imports. Census añade **motorhomes y agrícolas**.
- Antigüedad de valoración: **hasta 20 años** de histórico (60.000+ car IDs); forecast **hasta 5 años** (60 meses).
- Granularidad: por **manufacturer → range → model → derivative**, con **10 plates** y **6 mileage points**.

---

## 3. Productos + campos atómicos

> Notación: campos confirmados en página de producto / API / web service. Donde la página es solo marketing se marca el hueco.

### 3.1 Valoración usado — Black Book / Valuation Anywhere / Used Values WS
**Qué es:** el benchmark de valor de coche usado UK. Black Book (mensual), **Black Book Live** (tiempo real, 365 d/año),
servido por el portal **Valuation Anywhere** y vía API/SOAP.
**Campos atómicos:**
- `Retail value` (valor retail / "sweet spot")
- `Clean` value (trade — condición CAP Clean)
- `Average` value (trade — CAP Average)
- `Below` value (trade — CAP Below average)
- `Internet/online prices`: `high` y `low` valuation (rango de precios de anuncios live)
- `mileage` + `mileagePoints` (6 puntos de km)
- `plates` (`yearMonth`, `plateSequenceNumber` — 10 plates)
- `valuationDate`
- Movimientos de valor en vivo: **6 millones de movimientos** entre publicaciones mensuales; *qué* derivative se movió y *por qué*
- `comments` (`commentDate`, `comment`) — comentario editorial del movimiento
- Opinion values al lanzamiento de modelo
- Valoración **incl. VAT**
- VRM lookup devuelve además: `cap code`, `cap manufacturer`, `range`, `model`, `derivative`, `standard equipment`
- Valoración **single** y **bulk** (subida de CSV / lista de matrículas)
- Vehículos: cars, bikes, LCV, HGV

### 3.2 Option Values (lanzado 2024)
**Qué es:** valora extras de fábrica en el usado (techo panorámico, llantas, packs…). Gratis para subs de Valuation Anywhere.
**Campos atómicos (API `OptionValues/v1`):**
- `option.id`, `option.name`
- `costNew` (PVP del extra cuando nuevo)
- `value` (valor actual del extra)
- `includedInValuation` (flag)
- `cleanTotalOptionsValue`, `averageTotalOptionsValue`, `belowTotalOptionsValue`, `retailTotalOptionsValue`
- `packs` (packs de opciones, misma estructura + opciones anidadas)
- Reglas: `maxPercentOfVehiclePrice`, `maxNum`
- Entrada: `registrationDate`, `mileage`, `conditionsRequired[]` (Clean/Average/Below/Retail), `requiredValuationMonths[]` (0-60)

### 3.3 Future / Residual Values — Gold Book / Gold Book 0-12 / Gold Book iQ / CAP Monitor / Future Values
**Qué es:** forecast de valor/residual hasta 5 años; "step change" de mensual a tiempo real.
**Campos atómicos:**
- `Residual value` (% y monetario) hasta **60 meses / 5 años**
- Forecast `clean/average/below` por mes (API Short Term Forecast: `plusValues` → `date`, `mileagePoints`; `mileagePoints` → `mileage`, `clean`, `average`, `below`)
- `valuationDate`, `plates` (`yearMonth`, `plateSequenceNumber`)
- Términos de km/forecast **a medida** (bespoke mileage & forecast terms)
- Base **CAP Clean incl. VAT**, indexado por manufacturer/model/derivative, ajustado por **age y mileage**
- **YOY% (Year-over-Year % Deflation/Inflation)** = (Valor hoy − Valor hace 1 año) / Valor hace 1 año — "pure market measure", segmentado por **age (p.ej. 36/60 meses)**, **sector (Lower/Upper Medium)** y **fuel type**
- **Model Life Overlay** (+/- por edad del modelo, calculado por sector & fuel desde histórico)
- **Pence-per-mile (PPM)** / PCH valuation (API `GetPpmValuation`)
- Alertas de movimiento de RV definidas por usuario (Gold Book iQ)
- `comments` / forecast evidence & rationale (editorial)
- Comparación competitiva entre derivatives
- Datos pre-launch / opinion forecast

### 3.4 Residual Tracker
- Histórico de `Used Values` (búsqueda)
- Histórico de `Monitor Values` (forecast)
- Tendencias **estacionales**, de **mercado** y de **lifecycle**
- Patrones de depreciación en el tiempo · Cars + LCV
- "Miles de data parts manipulables" (time series)

### 3.5 Commercial — Red Book / Commercial Vehicle Valuations / New & Used Monitor
- Valores LCV (light commercial)
- Valores HGV / trucks
- Monitor de residual nuevo & usado comercial (tendencias RV LCV/HGV)

### 3.6 Motorcycles — Green Book
- Valores de moto usada (benchmark mensual)

### 3.7 New Vehicle Data (NVD) / Spec Check / CAP Code / VRM Lookup / WLTP
**Qué es:** "UK's biggest tech and spec database" — **460.000+ options & list prices**, **55-58 fabricantes**, **35.000 piezas de info nueva/semana**, datos desde ago-2011.
**Campos atómicos (NVD WS + WLTP API + DVLA WS):**
- Identificadores: `CAP Code` (estándar de industria), `CAP ID`, `manufacturer`, `range`, `model`, `derivative`, `modelYear`
- Precios: `list price`, `OTR`, opciones y list prices (460k+)
- `CO2` (g/km) · **WLTP**: `WLTP - CO2 (g/km) - Combined`, `WLTP - MPG - Low/Medium/High/Extra-High/Combined`, `examinationDate`, `validUntil` · NEDC (legacy, Legislation WS)
- `CC` (cilindrada) · `engine power` (BHP/kW) · `MPG` / fuel consumption · `fuel type`
- `fuel tank capacity` · `luggage/boot capacity`
- `dimensions` (largo/ancho/alto) · `mass data` / pesos
- `insurance group`
- `euro emissions` standard
- `P11D` value · `P11D percentages` (BIK %, 3 ejercicios fiscales)
- `body type` · `doors` · `seating`/seats · `colour`
- `standard equipment` (`option code`, `category description`, `option description`)
- `generic options` (`category name`, `option description`, `option code`) + `generic option links`
- `technical data` (`technical code`, `description`, `category`, `value`)
- `colour/hood links` (descapotables) · `colour/trim links` (combinaciones interior)
- `GetNvdChangeDates`: tipos de cambio (model year, price, options, standard equipment, technical data)
- **Digital Vehicle Imagery**: fotografía exterior **360°** + imágenes de interior (toda Europa)
- `Electric range` (vía WLTP/spec) [parcialmente VERIFICADO — WLTP confirmado, "range" inferido]

### 3.8 Tyre Data
- `tyre size` / dimensiones · `tyre profile` (vía VRM lookup)

### 3.9 LCV Chooser
- Comparador de specs LCV (payload, dimensiones — detalle no enumerado en web) [PARCIAL]

### 3.10 Provenance — HPI Check (+ MOT, Write-Off, Recalls, Vehicle Identity, Keeper)
**Qué es:** "Britain's first provenance check". **80+ data points** desde **20+ fuentes** (DVLA, Trading Standards, Police, partners).
**Campos atómicos (lista completa de checks):**
- **Outstanding finance** (`finance type`, `date of agreement`, `finance company`, `contact details`); logbook loans / inherited debt
- **Stolen** (Police National Computer)
- **Cloned / false identity**
- **Insurance write-off records** + `damage classification`
- **Write-off category** (`Cat A/B/S/N`; legacy `Cat C/D` — C/D = económico, no inseguro)
- **Scrapped** (marcador DVLA)
- **Mileage / odometer discrepancy** (flag instantáneo)
- **Number of previous keepers** + `date of last keeper change`
- **Plate changes** (cada matrícula previa + fecha de aplicación)
- **Colour changes**
- **Imported** status · **Exported** status
- **VIN / chassis check** · **engine number**
- **Vehicle Identity Check** (localización/identificación)
- **MOT history** (`test date`, `recorded mileage`, `pass/fail`, `advisories`, `previous status`)
- **Road tax / VED** renewal date / status
- **Safety recall data**
- **Keeper Enquiries** (datos del registered keeper)
- Vehicle details base: make/model/colour/engine/year/fuel
- Valoración incluida en ciertos checks
- Gráfico **top-down del vehículo** mostrando todos los daños + desglose de coste (Write-Off Data)

### 3.11 Mileage — NMR (National Mileage Register) / NMR Mileage Services / Malta Odometer Check
- **NMR**: base de **500M+ readings** (histórico 265M→369M→450M→500M+), fuentes: DVLA, V5, VOSA/MOT, auction houses, insurance claims, leasing
- `mileage points` a lo largo del historial del vehículo
- **NMR Check** (compara km contra DB → discrepancia) + **NMR Investigation** (detección de "clocked")
- Malta Odometer Check (verificación para export)

### 3.12 SMR Data (Service, Maintenance & Repair) / SMR Forecast / History / Actuals
- `labour rates` · `labour times`
- `parts prices` (parts & labour cost)
- `fluid costs`
- `tyre prices`
- `component replacement intervals`
- `key component burn rates`
- `job frequencies`
- Coste de servicio por **term & distance**
- Histórico real de servicio en **etapas de 5.000 millas**
- SMR Forecast (futuro) / SMR History / SMR Actuals

### 3.13 TotalCost (TCO) / TCO Lite
- `Depreciation`
- `Fuel costs` (+ MPG / fuel consumption)
- `Tax` (VED / road tax)
- `Finance information`
- `CAP SMR forecast values`
- `Whole life cost` (whole life cost of operating)
- `Disposal value` (forecast)
- `Running costs`
- (cost/pence-per-mile derivado) [INFERIDO]

### 3.14 Market Value Manager (MVM) — seguros / total loss
- `Market value` evidenciado (external market values, advert-based)
- Cubre used cars, LCV, bikes, HGV, imports
- `Historic valuations` hasta **3 años**
- Settlement / loss valuation "justa"
- VRM lookup · gestión de claims · **informe PDF customer-friendly**

### 3.15 Vehicle Census Report — market research / parc (150+ campos)
**Vehículo:** make, model, vehicle segment, fuel type, engine size, engine model, CO2, body type, registration date,
date sold, number of owners, ownership type, colour, tyre information, vehicle age.
**Geografía/mercado:** postal sector del keeper actual, region, county, town, postcode distribution, distance & drive time
a puntos retail.
**Métricas:** vehicle population by area, distribución por region/postcode, market trends & forecasting, sales opportunity
quantification, **parts demand by postcode**, stocking level planning by location.
**Cubre:** cars, LCV, HGV, motorcycles, motorhomes, agricultural.

### 3.16 Insight — leasing (UK + NL)
- `Residual value` · `SMR costs` · `tyre prices` (NL) · `insurance prices` (NL)
- `full leasing price lists` de operadores principales
- Performance por brand / model / derivative / company car / van
- **Anomaly reporting** (varianza de tu oferta vs competidores) + resumen de posición y amenazas

### 3.17 Riesgo / activo — Security Watch · Crush Watch · REACT · Residual Tracker
- Alertas de vehículo de alto riesgo (Security Watch)
- Crush/disposal watch (protección frente a destrucción de activo)
- REACT: tracking de localización/estado de activo (finance)

### 3.18 AfterSales — Manager · Customer Watch · Retention Watch · Data Services
- Targeting de cliente de servicio · métricas de retención/lealtad · analítica de marketing de cliente

### 3.19 Otros
- **P11D WS** (`GetP11DValuation`): company car tax benefit · P11D % BIK
- **Legislation WS**: emissions & regulatory compliance (WLTP/NEDC)
- **AudaEnterpriseGold**: estimación de reparación (colisión, ecosistema Solera/Audatex)
- **Consumer/Vehicle Appraisal App**: tasación electrónica part-exchange
- **Seller's HPI Check** (gratis para vendedores particulares)

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Volumen diario de anuncios | **~700.000 anuncios retail live/día** de portales líderes | [VERIFICADO ≥2: retail-values, búsqueda metodología] |
| Suppliers | **50+ proveedores** (auction groups + car sales websites) | [VERIFICADO: búsqueda metodología] |
| Transacciones | **~160.000 transacciones de motor trade/día** | [VERIFICADO: búsqueda metodología] |
| Output de valores | **~10M used car values/día** sobre **~2.300 model ranges** y **70.000+ derivatives**, 20 años atrás | [VERIFICADO: búsqueda metodología] |
| Granularidad | valor para cada vehículo en **10 plates** × **6 mileage points** | [VERIFICADO ≥2: metodología + API (`plates`+`mileagePoints`)] |
| Pipeline | feed diario → reglas de **data quality & validation** → **algoritmos de data mining** → reglas de negocio + ajuste editorial → publicación en Black Book | [VERIFICADO] |
| Rigor académico | metodología desarrollada con **University of Leeds — Institute for Transport Studies** (cuerpo independiente) | [VERIFICADO ≥2] |
| Equipo editorial | analistas de valoración (p.ej. Derren Martin, dir. valuations; Andrew Mee) "watch the market like hawks" | [VERIFICADO: Autocar, Motor Trader] |
| Precisión declarada | "más preciso que el competidor más cercano el **77%** de las veces" (trade values) | [VERIFICADO: trade-values] (claim propio) |
| NVD | **35.000 piezas/semana**, **460k+ options/list prices**, 55-58 fabricantes, desde ago-2011 | [VERIFICADO ≥2] |
| NMR | **500M+ readings** de DVLA, V5, VOSA/MOT, auctions, insurance claims, leasing | [VERIFICADO ≥2] |

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web** | **Valuation Anywhere** (`valuationanywhere.cap.co.uk`) — cloud, desktop + móvil, 24/7; single + bulk (CSV) | [VERIFICADO ≥2] |
| **API REST** | `cap API` (`developer.cap.co.uk/capapi`, `api.cap-hpi.co.uk`) — HTTP, **JSON y XML** vía Accept header; auth **token/Bearer** (subscriberId+password → accessToken); **HTTPS obligatorio**. Endpoints: Authentication, ShortTermForecast, OptionValues, WLTP, etc. | [VERIFICADO ≥2: developer docs + support] |
| **SOAP Web Services** | `soap.cap.co.uk`: VRM, DVLA, NVD, Vehicles, P11D, Used Values, Used Values Live, Future Values, SMR, TCO, Legislation, Data Download | [VERIFICADO: webservices docs] |
| **Ficheros (data files)** | descarga en **ASCII (fixed width), CSV o JSON**; por dataset o base de datos; vía SOAP o Subscriber Website | [VERIFICADO: support data-files] |
| **Frecuencia** | **diaria o mensual** según suscripción (Black Book Live = 365 d/año) | [VERIFICADO] |
| **Informes** | PDF (HPI Check report; MVM "customer-friendly PDF"; Vehicle Census report) | [VERIFICADO] |
| **Apps** | Consumer/Vehicle Appraisal App; Seller's HPI Check | [VERIFICADO] |
| **Integración DMS / 3rd-party** | "third-party systems integrators" como sector objetivo; conectores low-code (p.ej. Cyclr); partner Vertu Motors | [VERIFICADO ≥2] |

---

## 6. Precio

| Aspecto | Detalle | Estado |
|---|---|---|
| Modelo | **Suscripción B2B** (por dataset/base de datos, frecuencia diaria/mensual; consumo por lookups en VRM/DVLA con límites de cuenta) | [VERIFICADO indirecto: webservices `GetCurrentStatus`/límites + API `availableProducts`] |
| Tarifa pública | **No publicada** — quote-based; contacto comercial (helpdesk@cap-hpi.com / 0113 222 2000) | [VERIFICADO: búsqueda pricing] |
| Gratis | **TCO Lite** (dentro de Valuation Anywhere), **Option Values** (gratis para subs VA), **Seller's HPI Check** (particulares) | [VERIFICADO ≥2] |
| HPI Check consumidor | de pago por informe (consumer); freemium parcial | [VERIFICADO: hpicheck.com] |

---

## 7. Placement (patrón web a copiar por cardeep)

> Cómo cap hpi **coloca cada dato en su UI**. Es el blueprint para ubicar cada métrica en cardeep.

| Dato | Dónde lo coloca cap hpi |
|---|---|
| Retail / Clean / Average / Below | **Tarjeta de resultado de valoración** en Valuation Anywhere tras introducir **VRM + km**: bloque de 4 valores como salida principal |
| Option Values | **Dentro de la misma tarjeta de valoración**, itemizado por extra (`name`, `costNew`, `value`) + total sumado al valor base |
| Future/residual values | **Dashboard de forecast** (Gold Book iQ): curva/tabla por mes hasta 60m + **panel de evidencia/rationale editorial** + **alertas** de movimiento de RV |
| Movimiento de valor (live) | **Panel de market movement** (Black Book Live): qué derivative se movió, cuánto y **por qué** (comment editorial) |
| YOY% deflación/inflación | **Índice de mercado** segmentado por age/sector/fuel (Gold Book iQ) |
| Provenance (finance/stolen/write-off/mileage…) | **Informe de historial** (HPI Check) con **indicadores de estado tipo semáforo** (pass / warning / alert) por check; **gráfico top-down del coche** para daños/write-off |
| Mileage discrepancy | **Flag/bandera** dentro del informe + timeline de lecturas NMR |
| Specs / NVD | **Spec Check / ficha técnica** por derivative: bloques de engine, CO2/WLTP, dimensiones, equipment estándar vs opcional, imágenes 360° |
| TCO / running costs | **Calculadora de whole-life cost** (TotalCost / TCO Lite): depreciación + fuel + tax + SMR + finance → coste total |
| Market value (seguros) | **Informe PDF de settlement** para el asegurado (MVM) con valor evidenciado |
| Parc / market research | **Informe geográfico** por region/county/town/postcode (Vehicle Census): distribución, demanda de parts, drive-time a retail |
| Posición competitiva (leasing) | **Anomaly report** (Insight): tu oferta vs competidores + resumen de amenazas |
| Acceso programático | **API REST/SOAP + ficheros** embebidos en el DMS/sistema del cliente (no UI propia) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad de benchmark histórico**: el Black Book (CAP, 1979) + HPI Check (1938) son el estándar *de facto* de la industria UK. Marca y confianza institucional difíciles de replicar.
2. **Profundidad atómica de valoración**: trade en 3 condiciones (Clean/Average/Below) **+ retail + internet high/low + future hasta 60m + option-level**, todo por derivative × 10 plates × 6 km points.
3. **Live data real (Black Book Live)**: ~6M movimientos entre publicaciones mensuales, 365 d/año, con **explicación editorial del porqué**.
4. **CAP Code como llave universal**: identificador que conecta valoración + specs + provenance + costes en un único lenguaje, replicado internacionalmente.
5. **Rigor académico** (University of Leeds ITS) sobre ~700k anuncios/día + 160k transacciones — pocos competidores publican respaldo independiente.
6. **NMR propietaria** (500M+ lecturas de km) — registro de millaje difícil de igualar.
7. **Stack de entrega maduro**: REST + SOAP + ficheros (ASCII/CSV/JSON) + portal + apps, pensado para embeber en DMS.
8. **Option Values** (2024): valoración atómica de extras de fábrica en usado — gap clásico del sector que ellos cierran.
9. **Cobertura de tipos**: cars + LCV + HGV + bikes + grey imports + (Census) motorhomes/agrícolas.
10. **One-stop**: valoración + specs + provenance + SMR/TCO + seguros + parc + AfterSales bajo un mismo proveedor.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **Transparencia de precio nula**: todo quote-based; sin self-serve pricing público — fricción para el long-tail.
2. **UK-céntrico**: la riqueza atómica vive en UK; fuera de UK el dato es vía filiales Solera (Informex/Sidexa/ABZ/Market Scan/AUTOonline), sin web pública equivalente; **no hay valoración paneuropea homogénea expuesta** (Insight solo UK+NL).
3. **Métricas de demanda/oferta de mercado poco expuestas**: a diferencia de Indicata/Auto Trader, **no publica abiertamente** *Market Days Supply*, *Days-to-Sell*, *price-to-market %* ni un *demand index* explícito en su web (el más cercano es el YOY% y el "internet high/low"). [NO-VERIFICADO que no exista internamente — no aparece en material público.]
4. **No es marketplace ni fuente de stock vivo**: vende el *valor/dato*, no el inventario en venta ni el anuncio (consume anuncios, no los publica).
5. **No huella digital de punto de venta**: no cataloga dealers/puntos de venta ni su presencia online (territorio propio de cardeep).
6. **Detalle técnico de campos enterrado tras login/contacto**: muchas páginas de producto son marketing; el schema completo (data files) exige suscripción/credenciales.
7. **VIN-decoding global**: fuerte en VRM (UK) y CAP Code; sin VIN-decode universal multi-país expuesto públicamente.
8. **Telemática / uso real / datos de conducción**: fuera de scope (no telemetría ni comportamiento de conductor).
9. **Sin API pública self-serve / sandbox abierto**: developer docs existen pero requieren subscriber ID; no hay free tier de API.

---

## 10. Fuentes (URLs)

**Producto / catálogo**
- https://www.cap-hpi.com/products-and-services/ (catálogo, 51 productos)
- https://www.cap-hpi.com/products-and-services/valuation-anywhere/
- https://www.cap-hpi.com/products-and-services/retail-values-raw-data/
- https://www.cap-hpi.com/products-and-services/trade-values-raw-data/
- https://www.cap-hpi.com/products-and-services/black-book-live-used-car-values/
- https://www.cap-hpi.com/products-and-services/gold-book/
- https://www.cap-hpi.com/products-and-services/gold-book-iq/
- https://business.cap.co.uk/gold-book-iq/year-year-inflation (YOY% metodología)
- https://www.cap-hpi.com/products-and-services/new-vehicle-data/
- https://www.cap-hpi.com/products-and-services/hpi-check/
- https://www.cap-hpi.com/products-and-services/write-off-data/
- https://www.cap-hpi.com/products-and-services/residual-tracker/
- https://www.cap-hpi.com/products-and-services/smr-data/
- https://www.cap-hpi.com/products-and-services/totalcost/
- https://www.cap-hpi.com/products-and-services/market-value-manager/
- https://www.cap-hpi.com/products-and-services/vehicle-census-report/
- https://www.cap-hpi.com/products-and-services/insight/
- https://www.cap-hpi.com/products-and-services/nmr-mileage-services/
- https://business.cap.co.uk/products-and-services/data-products

**API / entrega**
- https://developer.cap.co.uk/capapi (endpoints + campos: Auth, ShortTermForecast, OptionValues, WLTP)
- https://developer.cap.co.uk/webservices (catálogo SOAP: VRM, DVLA, NVD, Vehicles, Used Values, Future, SMR, TCO, Legislation)
- https://api.cap-hpi.co.uk/docs/index.html
- https://support.cap-hpi.com/hc/en-us/articles/360007636993-cap-Data-Files-Developer-Documentation
- https://support.cap-hpi.com/hc/en-us/articles/360007134413-cap-API-Development-Documentation
- https://support.cap-hpi.com/hc/en-us/articles/360013605633-WLTP-API
- https://cyclr.com/integrate/cap-hpi (conector low-code, 3rd-party)

**Identidad / metodología / verificación cruzada**
- https://www.cap-hpi.com/about/ · https://www.cap-hpi.com/careers/our-story/ · https://www.cap-hpi.com/about/solera/
- https://business.cap.co.uk/about-cap/who-is-cap
- https://www.prnewswire.com/news-releases/solera-holdings-inc-announces-the-acquisition-of-cap-automotive-... (adquisición CAP 2014)
- https://www.cbinsights.com/company/cap-hpi · https://pitchbook.com/profiles/company/54324-55
- https://www.autocar.co.uk/car-news/features/inside-world-deciding-second-hand-car-values (metodología, equipo)
- https://www.solera.com/solutions/dealers/cap-hpi/ (cobertura internacional)
- https://www.hpi.co.uk/what-is-an-hpi-check.html · https://www.home.hpicheck.com/ (provenance fields)
- https://www.motortrader.com/.../new-cap-hpi-tool-values-optional-extras-used-cars-05-02-2024 (Option Values 2024)
- https://www.motortrader.com/.../cap-hpi-overhauled-mileage-checks-dealers-03-12-2024 (NMR 500M+)

> **Marcas [NO-VERIFICADO] / inferencias:** existencia de Days-to-Sell/Market Days Supply/demand index internos (no en web pública);
> cobertura específica Irlanda/otros países fuera de UK; payload exacto del LCV Chooser; "electric range" como campo NVD nombrado
> (WLTP confirmado, "range" inferido); pence/cost-per-mile en TotalCost (componentes confirmados, ratio inferido).
