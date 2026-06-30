# Auditoría atómica — ClearVin (clearvin.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **vehicle history reports (VIN check) Norteamérica**, **self-serve, pay-as-you-go, low-cost**, **proveedor aprobado NMVTIS de primer nivel** (autorizado por el U.S. Department of Justice). Decodifica un VIN/matrícula/lot-number en un **informe de historial** que cubre título, propietarios, odómetro, daños/siniestros, junk/salvage, total-loss de seguro, liens/impound, robo, recalls, valoración de mercado (Black Book) y un **rating propietario A–F**. Web: https://www.clearvin.com/en/ · Blog: https://blog.clearvin.com/ · API/B2B: https://www.clearvin.com/en/api-subscribers/.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **vin-history**. Mapea a su producto insignia, el **Vehicle History Report** por VIN, y a su suite de APIs (VIN Decoder / Valuation / Auction History / NMVTIS).
> Fecha auditoría: 2026-06-30. Método: navegación de home (`/en/`), sample report (`/en/sample-report/`), página de estructura del informe (blog `clearvin-vehicle-report-structure`), página de fuentes (blog `where-do-clearvin-vehicle-history-reports-come-from`), pricing (`/en/payment/buy-credits/`), rating (`/en/vehicle-history-rating-review/`), las 4 páginas de API (`api-subscribers/{valuation-data,auction-history,nmvtis-history}-api`), free decoder, license-plate-lookup, vin-mileage-check, canada-vin-check, motorcycle-vin-check, window-sticker, vehicle-title-lien-check, warranty-check, stolen-vin-check, dealer, bulk-access, custom-solutions, helpful-information/brands + verificación cruzada (Tracxn, Crunchbase, LinkedIn, BBB, The Org, AutoBidMaster, vinmentor, dollarbreak, Trustpilot/Google reviews).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). **[NO-VERIFICADO]** donde la fuente no fue accesible.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **ClearVin** (también escrito ClearVIN) | [V] |
| Razón social | **ClearVin, LLC** | [V — Crunchbase/ZoomInfo/BBB] |
| Dominio | clearvin.com (informe en subdominio de marca: `clearvinreport.com`; datos API: `dataclearvin.com`) | [V] |
| Categoría | **Servicio de vehicle history report (VIN check) Norteamérica** + suite de APIs de datos de vehículo. NO es guía editorial de valoración (usa Black Book como fuente). NO es DMS ni analítica de inventario. | [V] |
| Fundación | **2014** (Tracxn) — pero Crunchbase data el **lanzamiento del producto en septiembre de 2016**. Discrepancia: 2014 = constitución LLC; 2016 = go-live del servicio. | [V — 2 fuentes, con discrepancia declarada] |
| Fundador y CEO | **Yury Strachuk** | [V — Crunchbase + LinkedIn + Tracxn] |
| HQ legal | **Dover, Delaware, EE.UU.** (estado de constitución / BBB Dover) | [V — Tracxn/BBB] |
| HQ operativa real | **Portland, Oregon** — comparte sede con su empresa hermana AutoBidMaster: **6807 NE 79th Ct, Ste B, Portland, OR 97218**; tel. **(503) 298-4300** (área 503 = Portland). | [V — allbiz/buzzfile/BBB AutoBidMaster] |
| **Grupo / propiedad** | **Grupo informal de empresas de Yury Strachuk** (sin matriz cotizada). Strachuk es Founder de **AutoBidMaster LLC** (plataforma de pujas online, **broker autorizado/Featured Broker de Copart**, desde mar-2009) y CEO/Founder de **EasyHaul.com LLC** (transporte/shipping de vehículos). ClearVin es la pata de "datos/historial" del mismo ecosistema. | [V — Crunchbase person + The Org + LinkedIn + AutoBidMaster] |
| Financiación | **Sin financiación externa** ("unfunded", sin rondas) | [V — Tracxn/Crunchbase] |
| Empleados | **~4** (Tracxn, abr-2026) — equipo muy pequeño | [V — Tracxn] |
| Posición competitiva | Tracxn Score **18/100**, ranking **97 de 184** competidores activos. Top competidores citados: **Carfax (64), CarInfo (62), carVertical (57)**. | [V — Tracxn] |
| Reputación | **Mixta**. Trustpilot: ~10 reseñas. **Google Reviews ~3.6**. Reviews independientes positivas (vinmentor 5.0 #2/22; dollarbreak 4.4/5) destacan fotos de subasta y precio; quejas recurrentes: informe de pago aporta poco sobre el gratuito, datos incompletos/desactualizados, sin info de propietario, web móvil lenta. | [V — Trustpilot/Google/vinmentor/dollarbreak] |

### Clientes objetivo / verticales [V]
1. **Used car buyers** (consumidor final — caso de uso núcleo).
2. **Car dealerships** (Dealer Program, bulk).
3. **Auction buyers** (compradores en Copart/IAA — sinergia con AutoBidMaster; búsqueda por lot number).
4. **Private sellers** (vendedores particulares).
5. **Automotive businesses / enterprises** (API, bulk, custom solutions: aseguradoras, financieras, portales, clasificados).
6. **Developers / integradores** (Partner Program / Vehicle Data API).

---

## 2. Cobertura

### Geográfica [V]
- **Núcleo: EE.UU.** — cubre **"99% of the U.S. DMV records"**, los **50 estados + Washington D.C.** (para license-plate lookup).
- **Canadá** — herramienta separada (`Canada VIN Check`); páginas dedicadas por provincia: **Alberta, British Columbia, New Brunswick, Nova Scotia, Ontario, Quebec**. Fuentes: registros de vehículos canadienses, auction records, insurance databases.
- **NO Europa / NO España** — sin cobertura, sin DGT, sin guía de valores EU. Estrictamente Norteamérica.
- **Limitación legal**: NO divulga información personal del propietario (cumplimiento **DPPA**).

### Escala — cifras declaradas [V] (con inconsistencias entre páginas — ver Gaps)
- **NMVTIS**: "**over 40 million records from over 9,000 sources**" (la base que ClearVin reexpone como proveedor aprobado).
- **Custom Solutions**: "**real-time access to over a billion records**" y "**one of the largest automotive, motorcycle, and specialty vehicle history and valuation databases**" (la cifra "billion" incluye listings/imágenes de subasta, no solo títulos).
- **API**: "**hundreds of millions of data points** from industry-leading organizations and government agencies".
- **VIN Decoder**: "**100+ VIN details**".

### Scope (tipo de vehículo / nuevo-usado) [V]
- **Tipos**: turismos, trucks, **motos** (Harley-Davidson, Honda, Yamaha, Kawasaki, Suzuki, BMW, Ducati, Triumph, KTM, Indian), **RVs** (specs en Dealer Program).
- **Usado**: foco principal (historial, salvage, subasta).
- **Nuevo**: specs + window sticker (Monroney) + MSRP + warranty + listings de venta "New".

---

## 3. Productos + campos atómicos

> El producto es **un informe único** (Vehicle History Report) servido por VIN / matrícula US / lot-number Copart-IAA. Lo demás son **vistas/herramientas filtradas del mismo informe** (mileage check, lien check, stolen check, warranty check…) o **APIs** que exponen los datos crudos. Campos verificados leyendo el **sample report live (VIN 5YFT4MCE3MP076873, 2021 Toyota Corolla XSE, Report ID 113BFA64)** y las páginas de cada API.

### 3.1 Vehicle Specifications / VIN Decode (100+ data points) [V — sample report + decoder]
`VIN`, `Make`, `Model`, `Year`, `Trim`, `Style` (body, p.ej. 4D Sedan), `Engine` (p.ej. 2.0L L4 DOHC 16V), `Engine displacement`, `Cylinders`, `Transmission` (p.ej. CVT), `Wheel Drive` / drivetrain, `Fuel Type`, `Standard Seating`, `Optional Seating`, `Tank Size` (gal), `Tires` (p.ej. 225/45R18), `Tire type`, `Tire Pressure Monitor`, `City Mileage` (MPG), `Highway Mileage` (MPG), `Overall Length`, `Overall Width`, `Overall Height`, `Front track size`, `Rear track size`, `Turning diameter`, `Loading capacity` / `Cargo volume`, `Headroom`, `Legroom`, `Shoulder room`, `Steering Type` (p.ej. R&P), `Suspension type`, `Spring type`, `Anti Brake System` (p.ej. 4-Wheel ABS), `Front brake type`, `Rear brake type`, `Electronic brake assistance`, `Vehicle Stability Control`, `Anti-theft System`, `Airbag availability`, `Heated steering wheel`, `Climate controls` / `Air conditioning`, `Electronic parking aid`, `Navigation aid`, `Remote ignition`, `Standard GVWR`, `Clearance` (ground clearance), `Made In` (country), `Manufacturing plant`, `Car warranty`.

### 3.2 Ownership History [V — sample report]
Por propietario (tabla): `Owner #`, `Status` (NEW/USED), `Purchase Date` (mm/yyyy), `Condition` (New/Used), `Ownership Duration` (años/meses; "Current owner"), `State`, `Odometer` (al cambio), `Usage` (Personal / Commercial / Fleet / Rental / Taxi / Lease). Cabecera: `count of previous owners`. Alerta: `Multiple Owners Reported`.

### 3.3 Odometer Reading / Mileage Check [V — sample report + vin-mileage-check]
Por lectura: `Date`, `Mileage` (M = miles), `Data Source` (MOTOR VEHICLE DEPARTMENT / NMVTIS / dealer name / sales record). Agregados: `Average Miles Driven` (M/year) con flag **`Overdriven`** (over-average alert), `Mileage progression` (gráfico/chart), `Odometer rollback` flag, `odometer_status` (ACTUAL / NOT ACTUAL), `Vehicle usage classification` (taxi/fleet/rental).

### 3.4 Title History [V — sample report]
`Current Title` → `Issue Date`, `State`, `Mileage`. `Historical Title Records[]` → `Issue Date`, `State`, `Mileage`. + `Vehicle Doc Type` (tipo de documento de título). Fuente: NMVTIS.

### 3.5 Title Brand Information (taxonomía completa NMVTIS) [V — sample report + helpful-information/brands]
Estructura por brand: `code`, `name`, `description`, `Status` (Brand Found / No Brand Reported), `Applied` (fecha), `Applied By` (estado). ClearVin chequea y reporta **el catálogo NMVTIS completo (~90 códigos)**; los con señal real:
- **Daño**: `00 Clear`, `01 Flood Damage`, `02 Fire Damage`, `03 Hail Damage`, `04 Salt Water Damage`, `05 Vandalism`, `14 Collision`, `51 Disclosed Damage`.
- **Salvage/Total loss**: `11 Salvage`, `31 Totaled`, `32 Owner Retained`, `49 Salvage–Stolen`, `50 Salvage–Other Reasons`, `16 Salvage Retention`, `52 Prior Non-Repairable Repaired`.
- **Reconstrucción**: `06 Kit`, `09 Rebuilt`, `10 Reconstructed`, `21 Remanufactured`, `13 Refurbished`, `53 Crushed`, `30 Replica`.
- **Disposal**: `07 Dismantled`, `08 Junk`, `90 Pending Junk Automobile`, `91 Junk Automobile`, `35 Parts Only`.
- **Uso**: `12 Test Vehicle`, `17 Prior Taxi`, `18 Prior Police`, `19 Original Taxi`, `20 Original Police`, `48 Former Rental`.
- **Clasificación/edad**: `24 Antique`, `25 Classic`, `26 Agricultural Vehicle`, `27 Logging Vehicle`, `28 Street Rod`.
- **Import**: `22/45/46 Gray Market`.
- **Fabricante (lemon)**: `23 Warranty Return`, `39/40 Vehicle Non-conformity`, `41/42 Vehicle Safety Defect`, **`47 Manufacturer Buyback` (lemon law)**.
- **Robo/otros**: `36 Recovered Theft`, `55 Hazardous Substance`, `29 Reissued VIN`, `43 VIN Replaced`, `38 Prior Owner Retained`.
- **Odómetro**: `68 Actual`, `69 Not Actual`, `70 Not Actual (tampering verified)`, `71 Exempt`, `72 Exceeds Mechanical Limits`, `73 May Be Altered`, `74 Replaced`, `75 Reading at Renewal`, `76 Discrepancy`, `77 Call Title Division`, `78 Rectify Previous Exceeds`.
- **Admin (legacy)**: `15 Reserved`, `33 Bond Posted`, `34 Memorandum Copy`, `37 Undisclosed Lien`.

### 3.6 Junk & Salvage Records [V — sample report + NMVTIS API]
`Date` (obtained), `Entity` (reporting entity name, p.ej. COPART INC.), `ReportingEntityCategory`, `Location` (city/state), `Contact` (phone/email), `Export` (intended-for-export Yes/No), `Disposition` (SOLD / CRUSHED / TO BE DETERMINED). API: `junkAndSalvageInformation[]` → `ReportingEntityAbstract`(`ReportingEntityCategoryCode`, `IdentificationID`, `EntityName`, `LocationCityName`, `LocationStateUSPostalServiceCode`, `TelephoneNumberFullID`, `ContactEmailID`), `VehicleObtainedDate`, `VehicleDispositionText`, `VehicleIntendedForExportCode`.

### 3.7 Insurance Records (total loss) [V — sample report + NMVTIS API]
`Date Obtained`, `Entity` (insurer, p.ej. STATE FARM INSURANCE), `Location`, `Contact`, `Disposition` (SALVAGE / total loss). API: `insuranceInformation[]` con misma `ReportingEntityAbstract` + `VehicleObtainedDate`.

### 3.8 Accident & Damage History [V — sample report]
`Date`, `Major Impact` / `Primary Damage` (p.ej. WATER/FLOOD), `Secondary Damage` (p.ej. MINOR DENTS/SCRATCHES), `Airbags` (deployment), `Repair Cost` ($), `Structural damage` indicator, **Copart/IAA damage codes** (front / rear / undercarriage), `Photo` (imagen de daño). Fuente: Salvage Auction. (Disclaimer: no todos los daños se reportan; recomienda inspección independiente.)

### 3.9 Lien & Impound Records [V — sample report + vehicle-title-lien-check]
`Date`, `State`, `Location`, `Reported By` (MVD), `Event` (p.ej. "TITLE ISSUED/UPDATED LIEN REPORTED", "LIEN REPORTED + REBUILT/REBUILDABLE + WATER DAMAGE"), `Lien status` (active/past). **`Lienholder name`** (banco/credit union/finance co) — **solo para liens ACTIVOS** (los históricos del DMV NO traen lienholder). `Impound` → fecha + ubicación + towing agency. Fuentes: red privada de lienholders (NVS) + DMV.

### 3.10 Theft Records [V — sample report + stolen-vin-check]
`Status` (NOT LISTED AS STOLEN / stolen), `Theft date`, `Recovery status`. Fuente: **NVS** (National Vehicle Service). (Stolen check standalone reusa el mismo bloque.)

### 3.11 Emission & Safety Inspection [V — sample report + vehicle-emission-check]
`Date`, `Location`, `Data Source` (MOTOR VEHICLE DEPARTMENT), `Result` (PASSED/FAILED EMISSION INSPECTION).

### 3.12 Recalls (NHTSA) [V — sample report + car-recalls (free)]
`Date`, `Recall #` (NHTSA campaign number, p.ej. 23V865000), `Manufacturer recall number(s)` (p.ej. 23TB15/23TA15), `Component` (p.ej. AIR BAGS: SENSOR: OCCUPANT CLASSIFICATION), `Affected Models`, `Issue/summary`, `Consequence`, `Remedy`, `Owner Contact` (fabricante), `NHTSA Hotline`. Fuente: NHTSA. (Herramienta gratuita.)

### 3.13 Black Book Market Values [V — sample report] + Valuation API [V — valuation-data-api]
**En el informe (UI)**: tabla 2×3 →
- **Trade-In**: `Rough Base`, `Average Base`, `Clean Base`.
- **Retail**: `Rough Base`, `Average Base`, `Clean Base`.

**En la Valuation API** (objeto `blackbook`, mucho más granular):
- Trade-in (wholesale): `adjusted_tradein_clean/avg/rough`, `base_tradein_clean/avg/rough`.
- Retail: `adjusted_retail_xclean/clean/avg/rough`, `base_retail_*` (incluye **xclean = extra clean**, 4ª condición).
- Loan (whole): `adjusted_whole_xclean/clean/avg/rough`.
- Referencia: `msrp`, `retail_equipped`.
- **Mileage adjustment** por rango: `xclean`, `clean`, `avg`, `rough`, `finadv`, con `range_begin` / `range_end` (ajuste por km como campo explícito).
- **Option/equipment adjustment**: `add_deduct_list[]` (valor +/− por opción: aluminum wheels, moonroof, engine variants…).
- Valuation API (partner): combina **histórico de compra + datos de subasta en tiempo real** → `peak sale value`, `average sale value`, `trade-in value`, `auction value`.

### 3.14 Sale History / Listings [V — sample report]
Por listing (card con galería): `Listing type` (Dealer Classifieds / Salvage Auction), `Date` (listed) + `Sale date`, `Seller` (dealer/insurer name), `Seller type`, `Location` (city/state/zip), `Condition` (New/Used), `Price` ($), `Mileage`, `Sale Status` (PUT UP FOR SALE / sold / On Minimum Bid), `Photos` (galerías de **55+ / 58+ / 10+** imágenes por listing). Sinergia: las fotos de venta/subasta revelan daños ya no visibles.

### 3.15 Auction History API [V — auction-history-api]
Por subasta (`auctions[]`): `announced_at_auction`, `date` / `sale_date`, `sale_status`, `vendor` (Copart/IAA), `auctionId` (lot), `location`, `title_state`, `make`, `model`, `odometer`, `odometer_status` (ACTUAL/NOT ACTUAL), `color`, `engine`, `cylinders`, `fuel`, `drive`, `primary_damage`, `secondary_damage`, `own_doc` (doc type), `acv` (Actual Cash Value), `repair_cost`, `condition` (Run & Drive / WON'T START), `images[]`. Envoltura: `status`, `result`{`id`, `vin`, `report`{`auctions[]`}}.

### 3.16 VIN Decoder API [V — partner blog]
Decoder propietario → "100+ VIN details" (mismos campos que §3.1) + **recall data**. Endpoints REST: `POST https://www.clearvin.com/rest/vendor/loginRequest` (login) → `GET https://www.clearvin.com/rest/vendor/report?vin=…` (informe), auth **Bearer token** en header.

### 3.17 NMVTIS API [V — nmvtis-history-api]
Estructura NIEM (`result.report.nmvtis`): `vinChanged` (bool); `currentTitleInformation[]` (`VehicleIdentification.IdentificationID`, `TitleIssuingAuthorityName`, `TitleIssueDate.Date`, `VehicleOdometerReadingMeasure`, `VehicleOdometerReadingUnitCode`, `RecordMatchSequenceID`, `HistoricTitleAbstract[]`); `historyInformation[]`; `brandsRecordCount`, `brandsInformation[]` (`code`, `name`, `description`, `record`{`ReportingEntityAbstract`, `VehicleBrandCode`, `VehicleBrandDate.Date`}); `junkAndSalvageInformation[]`; `insuranceInformation[]`.

### 3.18 Window Sticker (Monroney) [V — window-sticker]
`MSRP` / `Base price`, `Optional equipment` con `option pricing` individual, `Standard equipment`, `Engine and transmission characteristics`, `Exterior color`, `Interior color`, `Fuel economy` (city/highway/combined), `Safety features`, **`NHTSA 5-star safety rating`**, `Warranties`, `Emission compliance`, `Serial number/VIN`. Salida: **printable** ("in 2 clicks"). Limitación: no todos los fabricantes proveen build sheet.

### 3.19 Warranty Check [V — warranty-check]
`Warranty type` (factory / CPO / extended), `Coverage status` (active/expired), `Expiration` (calculada por `original in-service date` + `mileage`, no por model year), `Transferability` (transfiere a nuevo dueño sí/no), `Original in-service date`. Fuente: registros de garantía del fabricante. **NO incluye maintenance records.**

### 3.20 ClearVin Rating (A–F) [V — vehicle-history-rating-review + sample report]
Grado letra propietario: **A Excellent / B Good / C Average / D Bad / E Poor / F Irreparable** (en el sample = "Average"/C, mostrado con escala C-F-E-D-C-B-A). **13 factores de entrada**: `Title Brand`, `Vehicle Age`, `Odometer Reading`, `Liens & Theft Status`, `Auction History`, `Value Index` (retail vs MSRP), `Primary & Secondary Damage`, `Repair Costs` (% del precio), `Value Depreciation` (ACV vs MSRP), `Seller Information`, `Ownership History`, `Usage Type` (commercial vs personal), `Inspections` (emission/safety).

### 3.21 Quick Summary badges (overview) [V — sample report]
Fila de **10 icon-cards con contadores**: `Ownership History` (N previous owners), `Odometer Reading` (valor), `Title History` (N records), `Sale History` (N records), `Lien & Impound Records` (N), `Title Brands` (N), `Junk & Salvage` (N), `Insurance Records` (N), `Accident & Damage` (N), `Recalls` (N) + **ClearVin Rating**.

---

## 4. Metodología / fuentes de datos [V]
- **NMVTIS** (National Motor Vehicle Title Information System, DoJ): ClearVin es **proveedor aprobado de primer nivel**. "40M+ records, 9,000+ sources". Aporta título, title brands, junk/salvage, insurance total-loss, indicadores de fraude/robo. State DMVs, aseguradoras y salvage yards están **obligados por ley** a reportar a NMVTIS.
- **NVS** (National Vehicle Service): theft/recovery, impound, export, lien (red privada de lienholders), asset protection.
- **NHTSA**: recalls, complaints, airbag deployments, odometer fraud, safety.
- **Black Book**: market values (trade-in/retail/loan + ajustes km/opciones). [V — sample report muestra "Black Book Market Values"; objeto `blackbook` en Valuation API]. *(NADA citado en blog antiguo y J.D. Power citado por dollarbreak — evolución de proveedor; la fuente VIVA verificada en el informe = Black Book.)*
- **Subastas (Copart / IAAI)**: "**cientos** de salvage/insurance auction yards de EE.UU." → listings, doc type, daños, final bid/ACV, **fotos (10+/evento)**. **Ventaja estructural**: acceso vía empresa hermana **AutoBidMaster** (broker autorizado Copart) → "data other vehicle history reporters don't have access to".
- **State DMVs**: título, registro, odómetro, emission/safety inspection, liens.
- **Sales/dealer classifieds**: listings de venta con fotos (recolectados "all over North America").
- **Canadá**: motor vehicle registries provinciales + auction + insurance databases.

---

## 5. Entrega (delivery) [V]
- **Portal web self-serve**: lookup por **VIN (17 díg.) / matrícula US (50 estados + DC) / lot-number Copart-IAA** → informe online (HTML) + **descarga PDF** + **Print**.
- **Idiomas (11)**: English, Russian, Spanish, Arabic, German, Ukrainian, Polish, Bulgarian, French, Georgian, Romanian.
- **Vehicle Data API** (REST/JSON, **Bearer token**, modular pay-as-you-go): VIN Decoder, Valuation, Auction History, NMVTIS — combinables à la carte. Endpoints `…/rest/vendor/loginRequest` + `…/rest/vendor/report?vin=`.
- **Dealer Program**: bulk access a reportes, sin mínimos mensuales ni contrato, registro gratis.
- **Bulk Access / Custom Solutions**: **bulk hasta 1.000.000 de VINs por query**, salida **CSV / XLSX / PDF**; "à la carte data selection".
- **Affiliate Program** + **Window Sticker** + free tools (decoder, vin-explorer, car-recalls) como top-of-funnel.
- **Free tools (gratis)**: VIN Decoder, VIN Lookup/Explorer, Recall Check, License-plate lookup (lookup gratis; informe completo de pago).

---

## 6. Precio (pricing) [V — con variación temporal entre fuentes]
- **Modelo**: **pay-as-you-go, one-time fee, sin suscripción, sin cuotas recurrentes**, sistema de **créditos** (1 crédito = 1 informe). **100% money-back guarantee** (reembolso si el informe no refleja la info NMVTIS vigente a fecha de compra).
- **Página live `/payment/buy-credits/` (abr-2026)**: **1 report = $17.99** · **2 reports = $23.98** ($11.99/u) · **5 reports = $28.99** (~$5.80/u, "68% off").
- **Reviews independientes (variación / promos)**: 1 = **$14.99**; 3 = $21.98–$23.99; 5 = $28.99–$29.99.
- **Dealer/Bulk (vinmentor/dollarbreak)**: 20 = **$60** ($3/u) · 40 = **$100** ($2.50/u) · 100 = **$220** ($2.20/u); "bulk hasta 50 VINs a $2.50/u". Sin mínimo.
- **API / Custom**: pay-as-you-go, **precio bajo petición** (representante de ventas).

---

## 7. Placement — DÓNDE colocan cada dato (patrón a copiar por Cardeep)

> ClearVin es un **informe scroll-vertical de una sola página**: cabecera → fila de badges-resumen con rating → tabla de contenidos (anclas) → secciones apiladas con fuente declarada por sección → footer NMVTIS. **Este orden y este patrón "badge-summary-arriba + detalle-apilado-debajo" es el molde directo para la ficha de coche de Cardeep.**

| Dato / métrica | Dónde lo colocan (sección/pantalla) | Estado |
|---|---|---|
| VIN / vehículo / Report ID / fecha / **botón PDF** / thumbnail | **Cabecera del informe** ("Vehicle History Report For …") | [V] |
| Contadores por categoría (owners, odómetro, títulos, ventas, liens, brands, junk/salvage, insurance, accident, recalls) | **Fila de 10 icon-badges** (quick summary, justo bajo cabecera) | [V] |
| ClearVin Rating (A–F) | **En la fila de badges**, como veredicto destacado (escala letra) | [V] |
| Navegación a secciones | **Tabla de contenidos con anclas** (#specs, #owners, #carSales…) | [V] |
| Especificaciones técnicas / decode | **Sección "Vehicle Specifications"** en grid de campos | [V] |
| Propietarios | **"Ownership History"** = tabla por propietario + alerta "Multiple Owners" | [V] |
| Odómetro | **"Odometer Reading"** = tabla cronológica + `Average Miles Driven` con flag Overdriven + chart de progresión | [V] |
| Títulos | **"Title History"** = bloque "Current Title" + tabla "Historical Title Records" | [V] |
| Emission/safety | **"Emission & Safety Inspection"** = tabla 1 fila | [V] |
| Total-loss seguro | **"Insurance Records"** = tabla por insurer (con disclaimer) | [V] |
| Junk/salvage | **"Junk & Salvage Records"** = tabla por entidad + disposition | [V] |
| Daños/siniestro | **"Accident & Damage History"** = **imagen de daño + detalles** (primary/secondary, repair cost) | [V] |
| Liens/impound | **"Lien & Impound Records"** = tabla histórica (con nota de verificar en DMV) | [V] |
| Robo | **"Theft Records"** = **icono de estado** (check verde "NOT LISTED AS STOLEN") + texto | [V] |
| Title brands | **"Title Brand Information"** = **checklist exhaustivo** (brands "Found" arriba con def/fecha/estado, resto "No Brand Reported") | [V] |
| Valoración | **"Black Book Market Values"** = **tabla 2×3** (Trade-In / Retail × Rough/Average/Clean) | [V] |
| Ventas/subastas | **"Sale History"** = **cards por listing con galería de fotos grande (55+/58+/10+)** + precio/km/condición/seller | [V] |
| Recalls | **"Recalls"** = ítem narrativo (campaign #, component, issue, consequence, remedy, contacto) | [V] |
| Disclaimer NMVTIS + widget de búsqueda | **Footer** ("Instant Vehicle Report" CTA + "Get Report Package") | [V] |

---

## 8. Diferencial (lo que ofrece y la mayoría no)
- **Acceso privilegiado a datos de subasta Copart/IAA vía empresa hermana AutoBidMaster** (broker autorizado Copart): fotos de subasta (10+/evento), ACV, repair cost, doc type, daños 1º/2º — "data other reporters don't have". **Es su foso real.** [V]
- **Búsqueda por lot-number de subasta** (Copart/IAA), no solo VIN/plate — único entre VIN-checkers consumer. [V]
- **ClearVin Rating A–F** propietario con **13 factores explícitos** (incluye Value Index retail/MSRP y Value Depreciation ACV/MSRP). [V]
- **Proveedor NMVTIS aprobado de primer nivel** con money-back atado a NMVTIS. [V]
- **Galerías de fotos masivas** de ventas/subastas previas (revelan daño reparado/oculto). [V]
- **Multi-idioma (11)** — raro en VIN-checkers US (sirve a compradores-exportadores). [V]
- **Bulk hasta 1M VINs** + salida CSV/XLSX/PDF + API modular Bearer, sin mínimos. [V]
- **Lemon-law buyback alert + odometer-rollback alert** destacados. [V]
- **Window Sticker (Monroney) printable** incluido. [V]
- **Precio agresivo** (one-time desde ~$15–18; dealer ~$2.20–2.50/u). [V]

## 9. Gaps (lo que NO ofrece / debilidades)
- **NO maintenance/service records** (US): el informe lo dice explícito — gap clásico vs Carfax/AutoCheck. (Canadá menciona "service history" pero es débil.) [V]
- **NO collision/repair history detallado** estilo Carfax: los daños vienen de salvage-auction, no de talleres/aseguradoras a nivel evento de reparación. [V — vinmentor]
- **NO info de propietario** (DPPA): sin nombres/contacto de owners. [V]
- **Cobertura SOLO Norteamérica**: nada de Europa/España/DGT, sin guía de valores EU. [V]
- **Valoración = reventa de Black Book**, no motor propio: solo Trade-In/Retail × 3-4 condiciones en UI. **NO ofrece**: valor residual %, forecast/valor futuro, **curva de depreciación** como serie, **days-to-sell / market days supply / price-to-market %**, índice demanda/oferta, residuales de leasing, wholesale MMR. (La API expone más granularidad Black Book —loan/xclean/ajuste km/opciones— pero sigue siendo data licenciada de terceros.) [V]
- **NO analítica de inventario en tiempo real / days-on-market / turn** (no es MarketCheck/vAuto/Indicata). [V]
- **NO incentivos/rebates de coche nuevo, NO lease programs.** [A — ausentes]
- **Lienholder solo para liens ACTIVOS** (históricos del DMV sin nombre). [V]
- **Documentación API pública pobre**: campos parcialmente expuestos; detalles/pricing solo "contacta a un representante". [V]
- **Cifras de escala inconsistentes** (40M NMVTIS vs "billion records" vs "hundreds of millions of data points"). [V]
- **Pricing inconsistente** entre página live ($17.99) y reviews ($14.99) — promos/cambios sin transparencia histórica. [V]
- **Empresa diminuta (~4 empleados), unfunded, Tracxn 18/100, Google ~3.6**: reputación mixta, quejas de "informe de pago aporta poco", web móvil lenta, datos incompletos/desactualizados. [V]
- **Confusión de dominios/marca** (clearvin.com / clearvinreport.com / dataclearvin.com) — riesgo de phishing/percepción. [V]
- **Dependencia de Copart/AutoBidMaster**: el foso desaparece si cambia esa relación. [A — riesgo estructural]

---

## 10. Fuentes (URLs)
- https://www.clearvin.com/en/ (home — NMVTIS, 99% DMV, búsqueda VIN/plate/lot, footer)
- https://www.clearvin.com/en/sample-report/ (sample live VIN 5YFT4MCE3MP076873 — TODAS las secciones y campos)
- https://blog.clearvin.com/clearvin-vehicle-report-structure/ (estructura/orden del informe)
- https://blog.clearvin.com/where-do-clearvin-vehicle-history-reports-come-from/ (fuentes: NMVTIS/NVS/NHTSA/NADA/auctions)
- https://www.clearvin.com/en/about-us/ (mission, fuentes, 50 estados + Canadá, Black Book)
- https://www.clearvin.com/en/vehicle-history-rating-review/ (rating A–F + 13 factores)
- https://www.clearvin.com/en/payment/buy-credits/ (pricing $17.99/$23.98/$28.99 + money-back)
- https://www.clearvin.com/en/api-subscribers/ (índice API: VIN Decoder / Valuation / Auction / NMVTIS)
- https://www.clearvin.com/en/api-subscribers/valuation-data-api/ (campos Black Book: adjusted/base tradein/retail/loan, mileage adj, add_deduct_list, msrp, retail_equipped)
- https://www.clearvin.com/en/api-subscribers/auction-history-api/ (JSON keys auction)
- https://www.clearvin.com/en/api-subscribers/nmvtis-history-api/ (JSON keys NMVTIS NIEM)
- https://blog.clearvin.com/api-access-to-automotive-databases/ (Partner Program, endpoints, Bearer, peak/avg/auction value)
- https://www.clearvin.com/en/decoder/ (free VIN decoder — 100+ campos)
- https://www.clearvin.com/en/license-plate-lookup/ (50 estados + DC, DPPA, VIN-from-plate)
- https://www.clearvin.com/en/vin-mileage-check/ (odometer fields + rollback + chart)
- https://www.clearvin.com/en/canada-vin-check/ (Canadá 6 provincias, fuentes CA)
- https://www.clearvin.com/en/motorcycle-vin-check/ (motos: HD/Honda/Yamaha/Kawasaki/Suzuki/BMW/Ducati/Triumph/KTM/Indian)
- https://www.clearvin.com/en/window-sticker/ (Monroney fields)
- https://www.clearvin.com/en/vehicle-title-lien-check/ (lien fields, lienholder solo activo)
- https://www.clearvin.com/en/warranty-check/ (warranty type/coverage/expiration/transfer)
- https://www.clearvin.com/en/stolen-vin-check/ (theft status, NVS)
- https://www.clearvin.com/en/dealer/ (Dealer Program, comparativa vs Carfax/EpicVin/AutoCheck)
- https://www.clearvin.com/en/bulk-access/ + https://www.clearvin.com/en/custom-solutions/ (bulk 1M VINs, CSV/XLSX/PDF, "billion records")
- https://www.clearvin.com/en/helpful-information/brands/ (taxonomía completa ~90 title brands NMVTIS)
- https://tracxn.com/d/companies/clearvin/ (fundación 2014, Yury Strachuk CEO, Dover, unfunded, ~4 empleados, score 18/100, ranking 97/184, competidores)
- https://www.crunchbase.com/person/yury-strachuk (CEO ClearVin + Founder AutoBidMaster + CEO EasyHaul; ClearVin launch sep-2016)
- https://www.linkedin.com/company/clearvin · https://theorg.com/org/autobidmaster-llc/org-chart/yury-strachuk (grupo Strachuk)
- https://www.bbb.org/us/or/portland/profile/auto-auction/autobidmaster-llc-1296-22511580 (Portland OR, (503) 298-4300, Copart Featured Broker)
- https://www.autobidmaster.com/en/services/clearvin-vehicle-history-reports/ (integración ClearVin↔AutoBidMaster)
- https://vinmentor.com/review/clearvin/ (review: pricing dealer 20/$60·40/$100·100/$220, pros/cons, gap repair/collision)
- https://www.dollarbreak.com/clearvin-review/ (review: $14.99/$21.98/$28.99, dealer $2.50/u, 4.4/5, Google 3.6, J.D. Power citado)
- https://www.trustpilot.com/review/clearvin.com (reputación ~10 reseñas — 403 al fetch directo, vía búsqueda)

---

### Nota de verificación
- **Grupo Strachuk (ClearVin + AutoBidMaster + EasyHaul)**: Crunchbase person + The Org + LinkedIn + BBB AutoBidMaster. **[V]**. Es el hallazgo clave de propiedad/diferencial (acceso Copart).
- **Fundación**: 2014 (Tracxn, constitución) vs lanzamiento sep-2016 (Crunchbase). Discrepancia declarada. **[V parcial]**
- **HQ**: Dover DE (constitución legal/BBB) vs Portland OR (operación real, compartida con AutoBidMaster, área 503). **[V]**
- **Campos de producto**: verificados leyendo el **sample report live** + páginas de cada API (JSON keys literales en Auction/NMVTIS/Valuation). Window Sticker y Warranty = categorías declaradas (sin JSON literal). **[V]**
- **Valoración**: fuente VIVA = **Black Book** (sample report + objeto `blackbook` en API). NADA (blog viejo) y J.D. Power (dollarbreak) citados → proveedor ha evolucionado; se marca. **[V con matiz]**
- **Pricing**: página live $17.99 (primaria) vs reviews $14.99 (promo). **[V con variación]**
