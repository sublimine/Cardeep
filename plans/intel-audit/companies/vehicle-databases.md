# Auditoría atómica — Vehicle Databases (vehicledatabases.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos de automoción API-first, self-serve, low-cost**: 25+ APIs REST/JSON sobre VIN decode, especificaciones (catálogo de specs), valor de mercado, historial de vehículo, subastas, OCR, fitment, recalls/TSB y datasets descargables. Web: https://vehicledatabases.com/ · API index: https://vehicledatabases.com/api · Docs: https://vehicledatabases.com/docs/ (v3.8, act. 06-jun-2026) · Marketplace: RapidAPI (`vehicle-database`) · Datasets: https://vehicledatabases.com/downloads · MCP server: https://vehicledatabases.com/mcp (waitlist).
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **spec-catalog** (NO es un host DNS — `spec-catalog.vehicledatabases.com` **no resuelve**, ENOTFOUND verificado). Mapea a su producto insignia **Vehicle Specifications API** ("16,000+ data points" por vehículo) y al **catálogo de specs descargable**.
> Fecha auditoría: 2026-06-30. Método: navegación de home, /api, /docs, page-sitemap.xml (40 páginas de producto enumeradas) y ~28 páginas de producto individuales (specs, EV specs, motorcycle, market value, VIN decoder, history, auction, sales/used-car, window-sticker, oem-build-data, vehicle-services, warranty, maintenance, recalls, repair-pricing, TSB, towing, tire/wheel fitment, windshield, OBD2, owner-manual, vin-title-check, NMVTIS, stolen, license-plate, vin-suggestion, classic-VIN, KBB/Edmunds/Carfax-alternatives, OCR) + verificación cruzada (Tracxn, Crunchbase, ZoomInfo, LinkedIn, Trustpilot, RapidAPI, apis.io).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). Donde una página solo muestra categorías y no JSON literal, se marca explícitamente.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Vehicle Databases** | [V] |
| Dominio | vehicledatabases.com | [V] |
| Categoría | **Proveedor de Car APIs y bases de datos descargables de automoción**, self-serve y de bajo coste. Se autodenomina "The #1 Provider of Car APIs for Automotive Businesses". NO es una guía editorial de valoración (tipo Glass's/Eurotax/J.D. Power); el valor de mercado es un módulo más dentro de una suite amplia de specs+historial+OCR. | [V] |
| Fundación | **2021** | [V — Tracxn + búsqueda agregada, 2 fuentes] |
| HQ | **65 Brunswick Blvd, Dollard-Des-Ormeaux, Québec, Canadá** (tel. (800)-205-9337) | [V — footer home + ZoomInfo] |
| Fundadores | **No divulgados** públicamente | [V — ausencia confirmada en Tracxn/Crunchbase] |
| CEO / liderazgo | **No divulgado** públicamente | [V — ausencia] |
| Empleados | **51-200** (ZoomInfo/LinkedIn) | [V] |
| Propiedad | **Privada, bootstrapped — "has not raised any funding yet"** (sin financiación externa). Sin grupo matriz cotizado conocido. | [V — Tracxn] |
| Posición competitiva | Tracxn Score **24/100**, ranking **65 de 184** competidores activos. Competidores top según Tracxn: **Carfax (64), CarInfo (62), carVertical (57)**. | [V — Tracxn] |
| Reputación | **Trustpilot ~19 reseñas, mixtas**: positivas sobre la *value API* (valores de mercado precisos, integración fácil, reporting de uso, precio razonable, soporte —se cita a "Achim"); negativas con patrón "scam-like" (llamadas no solicitadas ofreciendo checks tipo HPI, informes prometidos no entregados). La empresa responde negando esas llamadas y enfatizando prevención de fraude. | [V — Trustpilot + búsqueda] |
| Programa de marca-blanca | Sí: informes de historial **white-label, rebrandeables y revendibles** (HTML/PDF con logo del cliente). | [V — /vehicle-history-api] |

### Clientes objetivo / verticales declarados [V — home + páginas /industria]
1. **Car insurance / auto-insurance** (cotización, suscripción, siniestros, pérdida total/salvage).
2. **Car dealerships** (concesionarios — inventario, pricing, historial).
3. **Auto repair service** (talleres).
4. **Car website / car portal**.
5. **Classified websites** (clasificados).
6. **Car rental** (rent-a-car).
7. **Auto parts company** (recambios — catálogo OEM, fitment).
8. **Car finance** (financiación — valoración, decode, historial).
9. **Developers / integradores** (self-serve, RapidAPI, MCP).

---

## 2. Cobertura

### Geográfica [V]
- **Núcleo: EE.UU. + Canadá** (decode, specs, market value, historial, subastas, placas).
- **Europa: limitada** — `Europe VIN Decoder API` (decode de VINs europeos, tier Advanced), `UK Registration Decode` (MOT/taxes/fuel economy desde matrícula UK). Algunas páginas de specs mencionan "North America and the European Union". **No** hay valor de mercado ni profundidad de specs europeas comparable a la de NA.
- **NO es un actor España/ES**; sin guía de valores ES, sin DGT, sin cobertura ibérica específica.

### Escala — cifras declaradas (con discrepancias entre páginas) [V]
- **Registros VIN/vehículo**: **"over 80 million vehicle records and growing"** (home, 2026); **"70M+ VIN records"** (RapidAPI/otras); **"100M+ VIN records and growing"** (página /downloads). → cifra inconsistente entre superficies (ver Gaps).
- **Subastas**: **"largest auction database globally, 80M+ vehicle auction records"**, creciendo a diario; **10+ imágenes de alta resolución por evento**.
- **Rango de años**: **1900–2025** (home); **1980/1981–present** (VIN decode/specs); **pre-1981** (Classic VIN); motos **1894–2025**.
- **Specs (Vehicle Specifications API)**: **74 makes, 1,831 models, 80,000+ trims**, **16,000+ data points**, años **1981–2026**. "Updated and improved almost monthly".
- **Uptime declarado**: **99.99%**; respuestas JSON **< 1 segundo**.

### Scope (tipo de vehículo / nuevo-usado) [V]
- **Tipos**: turismos, SUV, camionetas/trucks, vans, **motos** (API dedicada muy granular), trailers; clásicos/vintage (decode).
- **Nuevo**: specs + MSRP + window sticker (Monroney) + warranty + OEM build data.
- **Usado**: market value, historial, subastas, listings de venta, title/salvage.

---

## 3. Productos + campos atómicos

> Patrón general de respuesta: JSON con envoltura `{ status, vin/data{...} }` agrupado en **secciones** (`intro` → `basic` → grupos de specs → `market_value` → `recalls`). Input típico: **VIN** o **YMM(T)** (year/make/model/trim). Entrada y salida verificadas vía ejemplos JSON publicados en cada página de producto salvo donde se indique.

### 3.1 VIN Decoder API (Basic / Advanced / NHTSA / Europe / Canada) [V]
Secciones y campos del ejemplo (VIN JTEDW21A860014011): `vin`; **basic**: `make`, `model`, `year`, `trim`, `body_type`, `vehicle_type`, `doors`, `vehicle_size`, `seating_capacity`; **motor**: `cylinders`, `engine_size`, `engine_description`, `engine_capacity`, `engine_configuration`, `electrification_level`; **transmisión**: `transmission_style`; **fabricante**: `manufacturer`, `region`, `country`, `plant_city`; **restraint**: `others`; **dimensiones**: `gvwr`; **drivetrain**: `drive_type`; **combustible**: `fuel_type`, `secondary_fuel_type`.
- **Advanced tier** añade [V — descrito, sin JSON literal]: `MSRP`, `invoice`, `total_price`, **OEM options**, **packages**, **colors**; cobertura Europa solo en Advanced.
- **NHTSA VIN Decoder** = wrapper sobre datos oficiales vPIC/NHTSA [A — por naming].
- Cobertura años **1980–present**; US/Canada (Europa en Advanced).

### 3.2 Vehicle Specifications API (YMM Specs) — PRODUCTO INSIGNIA / "spec catalog" [V]
Catálogo de specs por VIN o YMMT. **16,000+ data points**. Campos atómicos verificados:
- **Básico**: `make`, `model`, `year`, `trim`, `doors`, `vehicle_size`.
- **Motor/prestaciones**: `displacement_(l_ci)`, `engine_model`, `engine_camshaft`, `net_torque`, `horsepower`, `sae_net_horsepower_rpm`.
- **Transmisión/drivetrain**: `transmission_style`, `drive_type`, `final_drive_axle_ratio`.
- **Dimensiones/habitáculo**: `trunk_volume`, `width`, `height`, `length`, `wheelbase`, `min_ground_clearance`, `front_legroom`, `rear_legroom`, `front_shoulder_room`, `rear_shoulder_room`, `front_hip_room`, `rear_hip_room`, `front_head_room`, `rear_head_room`.
- **Peso**: `curb_weight`.
- **Frenos**: `front_brake_type`, `rear_brake_type`, `disc_front`, `anti_lock_brakes`.
- **Suspensión/dirección**: `steering_type`, `rear_suspension`, `suspension_type_front_cont`.
- **Consumo/depósito**: `fuel_economy`, `city_mileage`, `highway_mileage`, `fuel_capacity`.
- **Ruedas/neumáticos**: `wheel_size_(inches)`, `front_tire_size`, `rear_tire_size`, `front_tire_order_code`, `rear_tire_order_code`.
- **Colores**: `exterior[]` (`color`, `rgb`), `interior[]` (`color`, trim).
- **Asientos/confort**: `standard_seating`, `front_seat_type`, `rear_seats`, `heated_front_seats`, `lumbar_support`.
- **Features (categorizadas)**: Mechanical & Powertrain; Interior (climate, lighting, storage, instrumentation, airbags, restraints); Exterior (lights, mirrors, body material, paint, sunroof, wipers, headlights).
- **Precio**: `msrp`, `destination_charge`.
- **Adjuntos**: bloque `market_value`, array `recalls`.

### 3.3 Electric Vehicle Specifications API [V]
- **Batería/carga**: `Hybrid traction battery capacity (kWh)`, `battery type`, `battery voltage`, `battery number of cells`, `battery all electric range`, `charge time (hrs) @ 240V`, `peak DC fast charge rate (kW)`, `peak DC fast charge time (minutes)`, `DC fast charge connector`, `onboard charger (kW)`, `battery power output (kW)`.
- **Powertrain**: `Powertrain number of motors`, `Electric motor horsepower`, `Electric motor 1 torque`, `Electric motor 2 torque`, `Hybrid electric powertrain type` (p.ej. BEV), `Drive type`, `Engine location`.
- **Eficiencia**: `Fuel economy city` (MPGe), `highway`, `combined`, `combined (kWh)`.
- + specs estándar (dimensiones, peso, asientos, carga, suspensión, features, seguridad).

### 3.4 Motorcycle Data API [V — JSON con nombres literales]
Muy granular (US/Canada, VIN 5–14 o 17, 1894–2025):
- **Motor**: `Displacement`, `Horsepower`, `Torque`, `Bore`, `Stroke`, `Engine Type`, `Primary Compression Ratio`, `Cooling`, `Lubrication System`, `Clutch`, `Fuel Type` (inyección), `Top Speed`, `Acceleration`, `Idle Speed`, `Green house` (emisiones g/Km), `Starter`, `Exhaust System`, `Fuel Control`.
- **Transmisión**: `Transmission Type`, `Number Of Speeds`, `Primary Drive Rear Wheel`, ratios por marcha (First…Sixth).
- **Dimensiones/geometría**: `Length`, `Width`, `Height`, `Wheelbase`, `Ground Clearance`, `Trail`, `Fork Rake Angle`.
- **Pesos**: `Dry Weight`, `Wet Weight`, `Total Weight`, `Payload Capacity`, `Gross Vehicle Weight Rating`, `Power Weight Ratio`.
- **Suspensión**: `Front Suspension Type`, `Rear Suspension Type`, `Front Travel`, `Rear Travel`, `Front/Rear Suspension Size`.
- **Frenos**: `Front Brake Type`, `Rear Brake Type`, `Front/Rear Brake Diameter`, `Abs System`, `Brake Fluid`.
- **Ruedas/neumáticos**: `Wheel Type`, `Front/Rear Wheel Diameter`, `Front/Rear Wheel Width`, `Front Tire Size`, `Rear Tire Size`, `Front/Rear Tire Pressure`, `Tires Brand`.
- **Asientos**: `Seat Height`, `Alternate Seat Height`, `Seat Type`, `Seat Material`, `Number Of Seats`, `Heated Seat`, `Lumbar Adjustment`.
- **Combustible/fluidos**: `Tank Capacity`, `Reserve Tank Capacity`, `Oil Capacity`, `Storage Capacity`.
- **Eficiencia**: `EPA City`, `EPA Highway`, `EPA Combined`, `Maximum Range`.
- + `Vehicle class`, `Base MSRP`, colores, features, warranty (Basic/Charging System/Battery).

### 3.5 Vehicle Market Value API [V] — (módulo de valoración; clave para Cardeep)
- **Input**: VIN o YMMT + `mileage` + `state` (+ color como factor).
- **Salida**: matriz **condición × tipo-de-valor**.
  - **Condiciones (4)**: `Outstanding`, `Clean`, `Average`, `Rough`.
  - **Tipos de valor (3)**: `Trade-In`, `Private Party`, `Dealer Retail`.
- **Secciones JSON**: `intro` (`vin`) → `basic` (`make`, `model`, `year`, `trim`, `state`, `mileage`) → `market_value` → `market_value_data[]` → `market_value[]` (`Condition`, `Trade-In`, `Private Party`, `Dealer Retail`).
- **KBB-alternative / Edmunds-alternative**: misma triada `Trade-In / Private Party / Dealer Retail`; se posiciona como **alternativa más barata** a KBB y Edmunds (NO integración oficial). Edmunds nativo aporta `True Market Value® / True Cost to Own®`; Vehicle Databases NO replica TMV/TCO.

### 3.6 Vehicle History API (informe / report) [V]
Salida **JSON o HTML white-label rebrandeable (PDF)**. Secciones y campos:
- **Owner History**: `status`, `purchase_year`, `state`, `ownership_duration`.
- **Title & Damage Checks**: brands `salvage`, `rebuilt/rebuildable`, `junk`, `flood`, `auction brand`; `lien`/`loan records`.
- **Detailed Vehicle History (timeline)**: `event_date`, `event_type` (registration/accident/service/auction…), `location`, `data_source`, `odometer_mi`, `odometer_km`, `details`.
- **Mileage Records**: `date_reported`, `status`, `mileage`, `verification_status`.
- **Accident Records**: `accident_number`, `date`, `location`; `damage`, `insurance_loss`, `air_bag_deployment`, `tow_status`.
- **Service Records**: `service_date`, `location`, `service_type`, `mileage`.
- **Auction History**: imágenes, `lot_number`, `price`, `damage`, `sale_status`.
- **Sales Listing History**: transacciones por marketplace + condición + valoración.
- **Recalls**: `date`, `campaign_number`, `recall_number`, `component`.
- **Vehicle Usage Verification**: `fleet`, `lease`, `livery` + clasificación personal/rental/commercial-fleet/government (records found/not found).
- **Stolen Records**: verificación de robo.
- Cobertura US + Canadá, 1981–2024 (+ clásicos 5–13 dígitos).

### 3.7 Auction History API [V — JSON con nombres literales]
`price`, `sale status`, `lot-number`, `Auction Date`, `vname`, `VIN`, `year`, `make`, `model`, `Primary Damage`, `Secondary Damage`, `Title Type`, `Title Description`, `Odometer`, `Body Style`, `Engine Type`, `Transmission`, `Fuel Type`, `Color`, `Estimated Repair Cost`, `Estimated Retail Value`, `Damage Ratio`, `Location`, `Seller Type`, `Seller Name`, `images` (10+), `Runs_Drives`, `Engine_Starts`, `Has_Keys`.

### 3.8 Sales History API / Used Car API (listings) [V — JSON con nombres literales]
`vin`, `year`, `make`, `model`, `trim`, `vehicle_type`; `post_date`, `sale_date`, `sale_status`, `seller_type`, `dealer_name`, `listing_id`; `listing_price.price`, `listing_price.retail_value`, `listing_price.repair_cost`, `listing_price.currency`; `odometer_mi`, `odometer_km`, `condition`, `exterior_condition`, `interior_condition`, `primary_damage`, `secondary_damage`; `city`, `state`, `zip_code`, `country`, `address`; `drivetrain`, `transmission`, `fuel`, `cylinders`, `engine`, `doors`, `exterior_color`, `interior_color`, `fuel_capacity`, `airbags`, `keys`; `images[]`, `sale_document`, `report_url`, `accident_records`, `title_record`, `owner_record`; `features`, `interior_features`, `exterior_features`, `technology`, `mechanical`, `safety`, `other`; `fair_market_value` (min/max), `last_updated`, `reduced_price` (bool), `newly_listed` (bool).

### 3.9 Window Sticker API (Monroney) [V — categorías; salida triple]
**Salida simultánea: JSON estructurado + URL de PDF + render PNG** del sticker.
- **ID**: VIN, Year, Make, Model, Trim, Body style, drivetrain.
- **Precio**: `Base MSRP`, `Individual option pricing`, `Destination charge`, `Total MSRP`.
- **Equipamiento de serie**: Interior, Exterior, Safety systems.
- **Opcional**: factory-installed options, `Option codes`, individual pricing.
- **Mecánica**: Engine, Transmission, Horsepower, Torque, Towing capacity.
- **Consumo**: City/Highway/Combined MPG, MPGe (EV), Estimated annual fuel cost.
- **Seguridad (NHTSA)**: Overall rating, Frontal crash, Side crash, Rollover.
- **Emisiones**: CO₂ output, Smog rating.
- **Garantía**: Basic, Powertrain, Roadside assistance, Corrosion.

### 3.10 OEM Build Data API (build sheet) [V — categorías]
`VIN`, `Year`, `Make`, `Model`, `Trim`; **Installed OEM Options** (engine/transmission pairing, performance/audio/technology/safety/appearance/towing packages); **Standard Equipment**; **Equipment Groups** (bundles del fabricante); **Factory Colors & Interior Codes** (`exterior paint description`, `interior trim information`); `MSRP` (al momento de producción).

### 3.11 Vehicle Services API (agregador de 7 servicios) [V]
Bundle único que agrupa: **Warranty**, **Recalls**, **Fuel Economy** (EPA MPG/MPGe, technology type, fuel type, emisiones, comparativa de coste), **Repair Pricing**, **Maintenance**, **Car Parts** (`part_name`, `part_number`, `part_drawing`/esquema + fitment), **OBD Port**.

### 3.12 Vehicle Warranty API [V]
`year`, `make`, `model`, `warranty[]` con strings tipo `"Basic: 3 years / 36000 miles"`, `"Powertrain: 5 years / 60000 miles"`, `"Corrosion: 5 years / Unlimited miles"`, Roadside Assistance. (NO desglosa transferable/start-date como campos atómicos.)

### 3.13 Vehicle Maintenance API [V — JSON literal]
`year`, `make`, `model`, `trim`; `mileage` (intervalo); `conditions[]` (`normal`, `severe`), `had_one_condition` (bool); por condición: `menus[]` (tareas), `valueHigh`, `valueLow`, `value` (coste estimado). (NO expone capacidades de fluido ni part numbers.)

### 3.14 Vehicle Recalls API [V]
`date_of_recall_issue`, `campaign_number`, `manufacturer_recall_number`, `component` (airbags/brakes/electrical/steering/suspension/powertrain…), `date_of_manufacture`, `summary`, `consequence`, `remedy`, `number_of_units_affected`, `year`, `make`, `model`.

### 3.15 Repair Pricing API [V — JSON literal]
`year`, `make`, `model`, `trim`; `title` (servicio), `description`, `value` (id de mapeo); `costs[]` con `name` (`Parts`/`Labor`), `desc`, `low`, `high`. (NO horas de mano de obra, NO tarifa/hora, NO OEM part number, NO total agregado.)

### 3.16 Technical Service Bulletins (TSB) API [V — JSON literal]
`number`, `title`, `date`, `summary`, `pdf`, `year`, `make`, `model`. (síntoma/diagnóstico/acción van empaquetados dentro de `summary`, no atomizados.)

### 3.17 Towing Capacity API [V — JSON literal]
`vin`, `year`, `make`, `model`, `trim`, `body_style`, `engine`, `drivetrain`, `axle_ratio`, `additional_equipment`, `tow_capacity_lb` (convencional), `fifth_wheel_capacity_lb`, `GVWR`, `GCWR`, `payload_capacity`.

### 3.18 Tire & Wheel Fitment Specifications API [V]
`year`, `make`, `model`; `tire_size`, `bolt_pattern` (p.ej. 5x114.3), `center_bore`, `thread_size`, `wheel_tightening_torque`, `track_width_front_in`, `track_width_rear_in`, `wheelbase_in`.

### 3.19 Windshield-by-VIN API [V] — (nicho cristal/ADAS)
`year`, `make`, `model`, `vin`, `nags_number`, `oem_numbers[]`, `features[]` (`Rain Sensor`, `Lane Departure`…), `calibrations` (p.ej. `Dynamic calibration` / static).

### 3.20 OBD2 Code + OBD Port Location API [V — JSON literal]
- Code decode: `code` (p.ej. P0128), `definition` (SAE), `cause[]`.
- Port location: `year`, `make`, `model`, `location` (p.ej. "Driver Side - Under Lower Left Side of Dashboard").

### 3.21 Owner's Manual API [V — JSON literal]
`status`, `vin`, `year`, `make`, `model`, `path` (URL/PDF descargable).

### 3.22 VIN Title Check API [V — JSON literal]
`status`, `vin`, `salvage` (bool), `salvage_details[]` (`cause`, `date`). (otros brands —flood/junk/lemon— mencionados pero NO mostrados como campos en el ejemplo público.)

### 3.23 NMVTIS API [V — categorías]
current title status, previous title status, date of title issuance, latest odometer reading, reported theft history, branded title, salvage history. (NO es el proveedor oficial NMVTIS/AAMVA; nombres de campo atómicos no publicados.)

### 3.24 Stolen Vehicle API [V — JSON literal]
`possible stolen` (bool), `make`, `model`, `plate`, `color`, `location`, `date`, `VIN`, `year`.

### 3.25 License Plate Decode (US) / UK Registration Decode [V]
- **US**: input `license` + `state` → `vin`, `license`, `state`, `make`, `model`, `year` (sin trim ni specs en el ejemplo).
- **UK**: decode de matrícula → make, model, color, fuel type, body style, emisiones, **MOT status/taxes**, fuel economy [V — descrito en /api; página específica devolvió 404].

### 3.26 VIN Suggestion API [V — JSON literal]
`entered_vin`, `vin_status` (p.ej. Invalid), `suggested_vin`, `year`, `make`, `model` (corrección de VINs mal tecleados, 1982–present).

### 3.27 Classic VIN Decoder API [V — JSON literal]
VIN 5–14 dígitos, pre-1981, todas las marcas US: `vin`, `year`, `make`, `model`, `transmission`, `fuel`, `engine`, `drive`, `doors`.

### 3.28 OCR APIs [V]
- **VIN OCR**: imagen → VIN detectado (alta precisión, "segundos").
- **License Plate Recognition (ALPR)**: imagen → texto de matrícula + state, hasta **95% accuracy**, salida JSON/CSV/texto.
- **Receipt OCR** y **Invoice OCR**: documentos → JSON estructurado (no-automoción; expansión a OCR de documentos generales para accounting/ERP).

### 3.29 Datasets descargables (Downloads) [V — parcial]
"Production-ready datasets", **100M+ VIN records**, licencia comercial (uso interno + para alimentar apps/servicios), "samples to try before you buy", "Request Custom Database". El catálogo se carga dinámicamente ("Loading databases…") → nombres/columnas/formatos exactos **no expuestos** en HTML estático (ver Gaps). Búsqueda corrobora descarga en Excel/CSV/structured files.

---

## 4. Metodología / fuentes de datos [V]
- **Fuentes declaradas**: **NMVTIS**, registros de **subastas** (directos de plataformas de subasta partner, verificados antes de ingestar), **registros policiales**, **bases de datos de seguros**, y base propia de historial que **se actualiza a diario con millones de registros nuevos**.
- **Valoración**: valores nuevo/usado **computados analizando millones de transacciones reales de venta + precios de subasta** (la señal de precio "más fiable" según su narrativa, para valuation/underwriting/insurance appraisal).
- **Specs**: dataset propio, **74 makes / 1,831 models / 80,000+ trims**, "actualizado y mejorado casi mensualmente".
- **NHTSA wrapper**: el NHTSA VIN Decoder y datos de recalls/safety se apoyan en datos oficiales NHTSA/vPIC [A — por naming/estándar del sector].
- **Posicionamiento "alternativa"**: páginas KBB/Edmunds/Carfax = su propia data ofrecida como sustituto barato, NO integraciones oficiales [V].

---

## 5. Entrega (delivery) [V]
- **API REST/JSON** (núcleo); respuestas < 1 s, 99.99% uptime; auth por **API Key** (`X-API-Key`).
- **Formatos de salida**: JSON (todo); además **HTML white-label** (history report), **PDF** (history report, window sticker, owner's manual, TSB), **PNG** (window sticker), **CSV/texto** (OCR de placa).
- **Datasets descargables** (bulk): Excel / CSV / structured files, con licencia comercial.
- **Marketplace**: **RapidAPI** (`vehicle-database`) como canal alternativo.
- **MCP Server**: en **waitlist** (https://vehicledatabases.com/mcp) — integración para agentes/LLM, no GA.
- **Tooling dev**: documentación oficial (docs v3.8), **Postman Collection**, guía de arquitectura/rate-limits/credit-usage.
- **Portal cliente** (Client Login) + onboarding self-serve (free trial → API key instantánea).
- **Reventa**: history reports rebrandeables (revender al consumidor final).

---

## 6. Precio (pricing) [V — parcial; opaco en portal propio]
- **Free trial**: **15 créditos gratis** + API key al instante, **sin tarjeta**.
- **Modelo**: basado en **créditos**, con planes **pay-as-you-go, mensual y anual**. Coste por crédito/llamada por API **NO publicado** (gated: "pricing details available once you sign up").
- **RapidAPI (tiers públicos del bundle `vehicle-database`)** [V — búsqueda]:
  - **BASIC**: **$0.00/mes**.
  - **PRO**: **$14.99/mes**.
  - **ULTRA**: **$99.90/mes**.
  - **MEGA**: **$199.99/mes**.
  - (cuotas/req límite por tier no detallados en el resultado).
- **Datasets**: precio **bajo petición** ("Request Custom Database").

---

## 7. Placement — DÓNDE colocan cada dato (patrón a copiar por Cardeep)

> Vehicle Databases es **API-first**: no expone un dashboard de mercado propio, sino **estructuras de respuesta** que el cliente renderiza. El "placement" se infiere de (a) el agrupamiento de secciones JSON y (b) los artefactos renderizados (report, sticker, cards). Esto ES el patrón de ubicación reutilizable.

| Dato / métrica | Dónde lo colocan (sección/pantalla) | Estado |
|---|---|---|
| VIN / matrícula / state | Cabecera del registro: sección `intro` (primer bloque de toda respuesta) | [V] |
| Make/Model/Year/Trim + body/doors/size/seating | Bloque `basic` (identidad del vehículo, justo bajo `intro`) | [V] |
| Specs técnicas (motor, transmisión, dimensiones, frenos, suspensión, ruedas, consumo, asientos, colores, features) | **Ficha de especificaciones** en grupos temáticos colapsables (Mechanical/Interior/Exterior); patrón "spec sheet" multi-sección | [V] |
| MSRP / destination charge / option pricing | Bloque de precio dentro de specs y, sobre todo, **Window Sticker (Monroney)** renderizado como PDF/PNG con bloque de precios base+opciones+total | [V] |
| Valor de mercado (Trade-In / Private Party / Dealer Retail) | **Panel de valoración = matriz/tabla** filas=condición (Outstanding/Clean/Average/Rough) × columnas=tipo-de-valor; bloque `market_value` anidado en la ficha del coche | [V] |
| Equipamiento de serie vs opcional + option codes | **Window Sticker** (dos columnas) y **OEM Build Data** (build sheet) | [V] |
| Consumo/MPG/MPGe + coste anual combustible + emisiones CO₂/smog | Panel de eficiencia del **Window Sticker** + Fuel Economy API | [V] |
| Crash ratings NHTSA (overall/frontal/side/rollover) | Panel de seguridad del **Window Sticker** | [V] |
| Garantía (basic/powertrain/corrosion/roadside) | Bloque de garantía (sticker + Warranty API) | [V] |
| Historial completo (owners, title brands, accidentes, odómetro, servicio, subastas, recalls, usage, robo) | **Informe de historial white-label (HTML/PDF)** con secciones apiladas: timeline de propietarios → badges de title/damage → timeline cronológico de eventos → registros de km → accidentes → servicio → galería de subastas → recalls | [V] |
| Evento de subasta (precio, daños 1º/2º, repair cost, retail est., damage ratio, runs/drives/keys) | **Card por evento de subasta** con galería de 10+ imágenes + badges de daño/condición + bloque de precio/estimaciones | [V] |
| Listing de venta (precio, km, ubicación, dealer, fotos, condición, days/flags) | **Card de listing** (price, retail_value, repair_cost, mileage, ubicación, `images[]`, flags `newly_listed`/`reduced_price`) | [V] |
| Recalls / TSB / Maintenance | Listas/acordeón de ítems (recall: campaign+component+consequence+remedy; TSB: number+title+date+pdf; maintenance: intervalo+menús+coste low/high) | [V] |
| Fitment ruedas/neumáticos, towing, OBD port, windshield/NAGS | Sub-fichas técnicas específicas (recambio/servicio): bolt pattern/torque; tow/fifth-wheel/GVWR/GCWR; "location" textual del OBD; NAGS+features+calibration del cristal | [V] |
| OEM build sheet | **Build sheet** (documento de configuración de fábrica por VIN) | [V] |

---

## 8. Diferencial (lo que ofrece y la mayoría no)
- **Amplitud bajo un solo key/crédito**: 25+ APIs (specs + value + history + subastas + OCR + fitment + windshield/ADAS + OBD + owner manual + TSB + towing) en un único proveedor self-serve. [V]
- **Classic/Vintage VIN Decoder** (5–14 dígitos, **pre-1981**): se autodenomina "el único" decoder de VIN vintage de longitud variable. [V]
- **Window Sticker (Monroney) reproducible** como **JSON + PDF + PNG** simultáneos. [V]
- **Informes de historial white-label, rebrandeables y revendibles** (HTML/PDF) — habilita reventa al consumidor final. [V]
- **Windshield-by-VIN con NAGS + features ADAS + tipo de calibración** (nicho cristal/recalibración ADAS poco cubierto). [V]
- **Base de subastas masiva** (80M+ registros, 10+ imágenes/evento) con repair cost + retail estimate + damage ratio. [V]
- **Motocicletas con profundidad extrema** de specs (bore/stroke/trail/rake/ratios por marcha…). [V]
- **Triple canal de entrega**: API + datasets bulk (licencia comercial) + RapidAPI + **MCP server (waitlist)** + Postman. [V]
- **Estrategia "alternativa low-cost"** explícita frente a KBB/Edmunds/Carfax/NMVTIS, con acceso instantáneo y 15 créditos gratis (vs licensing complejo de los incumbentes). [V]
- **Self-serve + bootstrapped**: sin fricción de ventas enterprise para empezar. [V]

## 9. Gaps (lo que NO ofrece / debilidades)
- **Valoración pobre en inteligencia de mercado**: solo `Trade-In / Private Party / Dealer Retail` × 4 condiciones. **NO** ofrece: **valor residual %**, **forecast/valor futuro**, **curva de depreciación**, **days-to-sell**, **market days supply**, **price-to-market %**, **índice de demanda/oferta**, **ajuste regional explícito como campo**, **wholesale/MMR**, **residuales de leasing**. → brecha grande frente a Black Book / J.D. Power / MarketCheck / Autovista para el caso de uso "inteligencia de mercado/residuales" de Cardeep. [V — confirmado por ausencia en /vehicle-market-value-api]
- **Sin analítica de inventario en tiempo real a escala nacional**: sales/used-car es *record-based*, no un feed vivo de inventario con days-on-market/turn como MarketCheck/vAuto. [V/A]
- **Sin incentivos/rebates de coche nuevo**, sin lease programs. [A — no aparecen]
- **Cobertura desbalanceada hacia NA**: Europa limitada (decode + UK reg), sin valor de mercado ni specs profundas EU; **sin presencia España/ES**. [V]
- **Repair Pricing** sin horas de mano de obra, tarifa/hora ni OEM part numbers (solo low/high de coste). [V]
- **Maintenance** sin capacidades de fluido ni part numbers (solo menús + coste). [V]
- **Title/NMVTIS infra-documentados**: VIN Title Check público solo muestra `salvage`; NMVTIS sin esquema de campos atómico publicado. [V]
- **Opacidad de precio** en portal propio (gated); solo tiers de RapidAPI son públicos. [V]
- **Catálogo de datasets no transparente** (carga dinámica; sin nombres/columnas/record-counts/formatos en HTML estático). [V]
- **Cifras de escala inconsistentes** entre páginas (70M vs 80M vs 100M registros VIN). [V]
- **Reputación frágil**: base de reseñas pequeña (~19 Trustpilot) con quejas de patrón "scam-like" (disputadas); Tracxn Score bajo (24/100). [V]
- **Provenance/IP sensibles**: marketing como "alternativa" a marcas registradas (KBB®/Edmunds®/Carfax®) sin integración oficial → riesgo de marca/licencia. [V/A]
- **Fundadores/CEO/ownership no divulgados** públicamente → baja transparencia corporativa. [V]
- **MCP server aún en waitlist** (no GA). [V]

---

## 10. Fuentes (URLs)
- https://vehicledatabases.com/ (home — stats, MCP waitlist, footer/HQ)
- https://vehicledatabases.com/api (índice de 25+ APIs)
- https://vehicledatabases.com/docs/ (docs v3.8, arquitectura, rate limits, credit usage, Postman, MCP)
- https://vehicledatabases.com/page-sitemap.xml (enumeración de 40 páginas de producto + 8 de industria)
- https://vehicledatabases.com/api/vehicle-specifications (campos specs)
- https://vehicledatabases.com/api/electric-vehicle-specifications (campos EV)
- https://vehicledatabases.com/api/motorcycle-data (campos moto)
- https://vehicledatabases.com/vehicle-market-value-api · https://vehicledatabases.com/api/vehicle-market-value (valoración)
- https://vehicledatabases.com/vin-decoder-api · https://vehicledatabases.com/api/vin-decoder (decode)
- https://vehicledatabases.com/api/classic-vin-decoder · https://vehicledatabases.com/api/vin-suggestion
- https://vehicledatabases.com/vehicle-history-api · https://vehicledatabases.com/api/vehicle-history (informe + secciones)
- https://vehicledatabases.com/api/auction-history (subastas)
- https://vehicledatabases.com/api/sales-history · https://vehicledatabases.com/api/used-car (listings)
- https://vehicledatabases.com/api/window-sticker (Monroney JSON+PDF+PNG)
- https://vehicledatabases.com/api/oem-build-data (build sheet)
- https://vehicledatabases.com/api/vehicle-services (agregador 7 servicios)
- https://vehicledatabases.com/api/vehicle-warranty · /vehicle-maintenance · /vehicle-recalls · /repair-pricing · /technical-service-bulletins
- https://vehicledatabases.com/api/towing-capacity-by-vin · /tire-wheel-fitment-specifications · /windshield-by-vin · /obd2-code-location
- https://vehicledatabases.com/api/owner-manual · /vin-title-check · /nmvtis · /stolen-vehicle · /license-plate
- https://vehicledatabases.com/api/kelley-blue-book-kbb · /edmunds · /carfax (posicionamiento "alternativa")
- https://vehicledatabases.com/api/ocr · /ocr/vin · /ocr/license-plate-recognition · /ocr/receipt · /ocr/invoice
- https://vehicledatabases.com/downloads (datasets bulk)
- https://apis.io/providers/vehicle-databases/ (conteo de propiedades por schema)
- https://rapidapi.com/vehicle-databases-vehicle-databases-default/api/vehicle-database/pricing (tiers $0/$14.99/$99.90/$199.99)
- https://tracxn.com/d/companies/vehicle-databases/ (fundación 2021, unfunded, competidores, ranking)
- https://www.crunchbase.com/organization/vehicle-databases (403 al fetch directo; corroborado vía búsqueda)
- https://www.zoominfo.com/c/vehicle-databases/ (empleados 51-200, HQ)
- https://ca.linkedin.com/company/vehicles-databases-api (perfil)
- https://www.trustpilot.com/review/vehicledatabases.com (reputación; 403 al fetch directo, corroborado vía búsqueda)

---

### Nota de verificación
- **Fundación 2021**: 2 fuentes (búsqueda agregada + Tracxn). **[V]**
- **HQ Dollard-Des-Ormeaux, Québec**: footer del sitio + ZoomInfo. **[V]**
- **Campos de producto**: verificados leyendo ejemplos JSON publicados en cada página; donde la página solo mostró categorías (Window Sticker, OEM Build, NMVTIS, KBB/Edmunds/Carfax) se marca explícitamente "categorías, sin JSON literal".
- **Pricing por-llamada del portal propio**: NO verificable (gated). Tiers RapidAPI verificados vía búsqueda. **[V parcial]**
- **`spec-catalog` como subdominio DNS**: FALSO (ENOTFOUND). Es la categoría taxonómica del orquestador; el producto real equivalente es la Vehicle Specifications API + catálogo de specs descargable. **[V]**
