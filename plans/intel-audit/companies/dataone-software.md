# Auditoría atómica — DataOne Software (DataOne, LLC)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos de vehículo / VIN-decoding "OEM-direct"** (no es una guía de valoración): identifica y describe el vehículo al nivel de VIN/trim/opción con datos de construcción de fábrica, specs, equipamiento, colores, precios MSRP/invoice, ADAS, servicio y mapeos a estándares de terceros. Web producto: https://www.dataonesoftware.com/ · Catálogo PDF de productos: https://www.dataonesoftware.com/hs-fs/hub/123171/file-959562714-pdf/docs/Dataone-Catalog.pdf · Tech guide (data dictionary XML v6.0): https://vin.dataonesoftware.com/Portals/123171/docs/techguide-xml-vin-decoder.pdf · Portal cliente: https://my.dataonesoftware.com/client-portal/ · Trial: https://vins.dataonesoftware.com/vin_decoder_api_free_trial.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **spec-catalog**. **No es un host DNS**: `spec-catalog.dataonesoftware.com` → **ENOTFOUND/NXDOMAIN** (verificado). Es una etiqueta de categoría (= su "catálogo de especificaciones"/base de datos de specs VIN-referenciada), igual que el caso "market-intelligence" de MarketCheck.
> Fecha auditoría: 2026-06-30. Método: navegación de dataonesoftware.com (home, products, vehicle-data-vin-decoding + sub-páginas extended/research/service/mapping, web-services-vin-decoder-api, oem-build-data-and-verified-records, vinbasic, software/perfectfit-*, media/images, developers, faqs, about, solutions/*, newsroom, quote-pricing) + extracción de texto del **PDF data dictionary XML v6.0** y del **PDF Products & Services Catalog** + comunicados (PR Newswire Toyota 2020, fusión Cross-Sell 2026) + verificación cruzada (G2, Dominion Enterprises, Cross-Sell.com, prensa sectorial).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre) · **[3P]** = dato de tercero, no oficial de DataOne.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **DataOne Software** | [V] |
| Razón social | **DataOne, LLC** ("DataOne Software, a division/company of Dominion Enterprises") | [V] |
| Categoría | **Proveedor de datos de vehículo y VIN-decoding "OEM-direct"** (vehicle data & VIN decoding, vehicle shopping APIs, imágenes/overviews). **No** es guía de valor editorial; **sí** revende/mapea valoraciones de terceros (J.D. Power, KBB). | [V] |
| Fundación | **1999** ("Automotive Data Solutions Since 1999") | [V — about + boilerplate PR] |
| Adquisición | **Adquirida por Dominion Enterprises en 2007** | [V — about + G2] |
| Matriz | **Dominion Enterprises** (conglomerado privado de datos/tech/software: automoción, franquicia, marketing, recreativo, hospitality, real estate). HQ matriz **Norfolk, VA**. | [V] |
| HQ | **100 Cummings Center, Suite 251-C, Beverly, MA 01915, EE.UU.** | [V — about/contacto] |
| Teléfono | **1-877-GET-VINS** (877-438-8467 / variante 877-439-8467 en home) | [V — variación menor entre páginas] |
| Presidente | **Jake Maki** (President of DataOne Software; ponente Verisk Insurance Conference 2025) | [V — newsroom + PR fusión] |
| VP Product & Technology | **Joe Kiley** | [V — PR fusión 2026] |
| Empleados | **No divulgado** por DataOne; se amplía con la plantilla de Cross-Sell tras la fusión 2026 | [V — no hay cifra oficial] |
| Facturación | **No divulgada** (filial de Dominion, no reporta por separado) | [V] |
| Propiedad | **Privada** (wholly-owned por Dominion Enterprises) | [V] |

### Hito estructural 2026 — fusión de Cross-Sell [V]
- **29-ene-2026:** Dominion Enterprises **fusiona Cross-Sell dentro de DataOne Software**. Cross-Sell (**fundada 1989**, presidente **John "TD" Scheuren**) es proveedor de **market intelligence de automoción** y "gold standard" para que los dealers entiendan su market share y el rendimiento de la competencia.
- **Estructura de marca resultante:** **todos los productos de *data licensing* pasan a marca DataOne**; la **marca Cross-Sell se mantiene para los productos dealer-focused**. Plantillas integradas en una sola organización.
- **Implicación para Cardeep:** DataOne deja de ser solo "describe el coche por VIN" y pasa a tener **también inteligencia de mercado** (matriculaciones, ventas, market share, lienholder) vía Cross-Sell. Ver §3-G.

### Cronología de capacidades de datos [V]
- **1999** Fundación (datos de automoción).
- **2007** Adquisición por Dominion Enterprises.
- **2009** Documentado XML VIN Decoder **v6.0** (data dictionary canónico, base del esquema actual).
- **2015 MY** Inicio de datos **ADAS**.
- **30-sep-2020** Integración de **Toyota build data** (Toyota/Lexus/Scion) en el VIN Decoder API.
- **14-jul-2022** Integración de **Ford build data** (Ford/Lincoln/Mercury, MY2011→actual).
- **abr-2022** Partner de **Duck Creek** (ecosistema P&C insurance).
- **29-mar-2023** Integración de **GM build data**.
- **29-sep-2023** Lanzamiento **Reverse VIN Lookup API** (suite Research, caso insurance).
- **2024-2025** Casos AutoRevo, Total Care Auto, Overfuel (digital retail, F&I/loss-ratio).
- **29-ene-2026** **Fusión Cross-Sell** → market intelligence + sales/registration data bajo DataOne.

### Clientes objetivo / segmentos declarados [V]
Dealers y **dealer service providers**, **auto insurance**, **service & maintenance / aftermarket / parts**, **vehicle research / portales / clasificados**, **fleet & mobility management**, **vehicle transport logistics**, **OEM**, además de **finance/lenders, print y government agencies**. Cross-Sell añade **media agencies** y **loan institutions**.

### Clientes/partners citados (verificados en web/PR) [V]
Uber, CarGurus, Carfax, DealerSocket, AutoRevo, Total Care Auto, Overfuel, Xtime, The Zebra, Fleetio, LGM, Credit Karma, Experian, Bosch; partners de datos/tech: **Toyota MNA, Ford, GM** (build data), **EVOX / Izmo** (imágenes), **J.D. Power, KBB, Cox Automotive (AIS), Auto Care Association (ACES), EPA, NHTSA**, Duck Creek, SBD (VehiclePlannerPlus), Verisk (evento), **Tesla / Rivian** (vía Cross-Sell, datos EV).

---

## 2. Cobertura

### Geográfica [V]
- **EE.UU. y Canadá** ("the geographical scope of DataOne's vehicle data and VIN decoding solutions is the US and Canadian markets").
- **VINBasic Canadian**: vehículos de mercado canadiense (incl. trims/variantes solo-Canadá), **2001→actual**.
- **Cross-Sell (market intelligence)**: **38 estados de EE.UU.** ("all major markets", en expansión).

### Temporal [V]
- **VIN decoding / specs**: **1981 → model year actual** (no decodifica pre-1981 por no seguir el estándar VIN moderno → error `PR`).
- **Build data OEM "direct"**: cobertura por fabricante y rango de años (p. ej. **Ford MY2011→actual**); declaran **>80% de los vehículos new US light-duty** con 17-digit decoding/build data [V — about].
- **Extended Vehicle Data**: "**over 30 model years and 50+ brands**".
- **Colores RGB**: MY2000 y posteriores. **ADAS**: MY2015→. **Imágenes**: 2003→. **Awards & Accolades**: 2006→. **Vehicle Overviews**: 2009→.

### Escala / amplitud [V]
- "**3.000 vehicle configurations** por model year" y **35+ brands** (research). Decodifica **billones de VINs/año** (web-services). **Dealer Inventory Feeds**: **5.000+ dealers**.
- Alta capacidad: opciones para entidades que procesan **2-3 millones de vehículos/mes**.

### Scope de vehículos [V]
- **Núcleo (más detallado): passenger & light-duty** (autos & light trucks).
- **VINBasic HD**: mid/heavy-duty (clases 4-8), incl. incomplete y chassis.
- **VINBasic Powersports**: motos, scooters, off-road (dirt bikes, ATVs, UTVs, snowmobiles).
- **VINBasic Trailers**: 850+ fabricantes, 50+ tipos de trailer.
- **Nuevo y usado**: los datos son del coche "as sold new" (build/specs/MSRP), pero VIN-referenciados → se usan tanto para **inventario nuevo como de ocasión** (research, recall, valoración usada vía mapeos).
- **Errores por fuera-de-scope** (verificado en tech guide): ATV (`AT`), pre-1981 (`PR`), Canadian (`CA`), Chassis (`CH`), Fleet (`FL`), Grey Market (`GM`), Heavy-duty (`HV`), Mid-duty (`MD`), Trailer (`TR`), Out-of-Market (`OM`), Motorcycle (`UM`), RV (`RV`), Unknown→research queue (`UK`).

---

## 3. Productos + campos atómicos

Arquitectura: **base de datos de specs VIN-referenciada** servida por **(a) API REST (XML/JSON)**, **(b) fichero plano delimitado**, y **(c) dump de base de datos relacional**. El esquema canónico (XML VIN Decoder v6.0) define los grupos de elementos abajo; las páginas web/comunicados modernos añaden ADAS, EV, build data OEM y los mapeos.

### — FAMILIA A · VEHICLE DATA & VIN DECODING —

### 3.A.1 VINBasic™ Suite (decoder base) [V]
"El producto de VIN decoding más completo del mercado." Sub-productos:
- **VINBasic Autos & Trucks** (US, 1981→): campos núcleo + GVWR + price new (MSRP). Campos listados: `DataOne VehicleID`, `vehicle_type`, `doors`, dimensiones y pesos, `engine(s)`, `transmission`, `drive_type`, `fuel_type`, `restraint type`, `GVWR`, `available colors`, `vehicle MSRP (price as new)`.
- **VINBasic Canadian** (2001→): idem para mercado canadiense.
- **VINBasic HD** (1981→, clases 4-8): `year`, `make`, `model`, `style name`, `drive_type`, `trim`, `wheelbase`, `engine`, `fuel_type`, `transmission`, `vehicle weight specs`.
- **VINBasic Powersports** (motos/scooters 1996→; ATV/UTV/snowmobile 2004→): year/make/model/trim; **VIN Pattern de 9 dígitos** (1-8 + 10); opción `CRS ID` (Consumer Research Solutions) para parear imágenes/extended data.
- **VINBasic Trailers** (1981→): `year`, `make`, `model` (solo towable RVs), `trailer type`, `trailer subtype`, `trailer attachment type`, `length range`, `country_of_manufacture`.

### 3.A.2 Extended Vehicle Data (el "spec catalog" real) [V]
Datos OEM-direct, "**over 30 model years / 50+ brands**", entregable por **DB relacional o web service**. Bloques y **campos atómicos** (del data dictionary v6.0 + página extended):

**basic_data:** `year`, `make`, `model`, `trim`, `style`, `vehicle_type`, `body_type`, `body_subtype`, `doors`, `model_number`, `package_code`, `country_of_manufacture`, `plant`.

**specifications → Driven Wheels:** `drive_type`, `hub_type_4wd`.
**Performance:** `acceleration_to_60`, `acceleration_to_100`, `aerodynamic_drag`, `braking_distance`, `turning_circle`.
**Size & Shape:** `angle_of_approach`, `angle_of_departure`, `breakover_angle`, `front_track`, `rear_track`, `ground_clearance`, `height`, `length`, `length_no_bumpers`, `wheelbase`, `width`, `width_no_mirrors`.
**Weight:** `curb_weight`, `gross_vehicle_weight_rating (GVWR)`, `gross_vehicle_weight_range`, `gross_combined_weight_rating (GCWR)`, `max_payload`, `max_towing_capacity`, `base_towing_capacity`.
**Interior Dimensions:** `cargo_volume`, `cargo_volume_rear_seats_down`, `cargo_volume_row3_down`, `interior_volume`, `passenger_volume`, `passenger_volume_third_row`.
**Seating:** `head_room_front/rear/third_row`, `hip_room_front/rear/third_row`, `leg_room_front/rear/third_row`, `shoulder_room_front/rear/third_row`, `std_seating`, `max_seating`, `seating_rows`.
**Truck Bed:** `bed_code`, `bed_length`.
**Wheels & Tires:** `tire_type`, `rear_tire_type`, `wheel_dia`, `rear_wheel_dia`.
**Fuel Storage:** `tank_1_capacity`, `tank_2_capacity`.

**engines (engine: brand/name/id/standard/installed):** `aspiration`, `block_type`, `bore`, `cam_type`, `compression`, `cylinders`, `displacement`, `fuel_induction`, `fuel_quality`, `fuel_type`, `marketing_name`, `max_hp`, `max_hp_at` (rpm), `max_torque`, `max_torque_at` (rpm), `redline`, `stroke`, `valves`, `valve_timing`, `oil_capacity`, `order_code`, `invoice_price`, `msrp_price`, `max_payload`.

**transmissions (transmission: brand/name/id/standard/installed):** `type`, `detail_type`, `gears`.

**fuel_efficiency_ratings:** `mpg_city` (low/high, trans_type AT/MT/NA), `mpg_hwy` (low/high, trans_type). **eng_trans_mpg_associations:** MPG preciso por combinación motor+transmisión (`mpg_city`, `mpg_hwy`, `order_code`, `invoice_price`, `msrp_price`).

**features:** por `category` → `feature name` → `value` (equipamiento estándar; descripción OEM **y** descripción normalizada).
**options:** por `category` → `option (name, installed)` → `install_type` (factory/port/dealer), `order_code` (OEM interno), `description` (marketing name OEM), `invoice_price`, `msrp_price`. Cubre **packages de marketing, equipamiento opcional, colores, motor, transmisión**.

**colors:** `exterior_color` / `interior_color` / `roof_color`, cada uno con `mfr_code`, `basic_color_name` (normalizado), `mfr_color_name` (marketing), `primary_rgb_code (r,g,b)`, `secondary_rgb_code (r,g,b)`, `is_two_tone`, `fabric_type` (interior/upholstery); **HEX** y **RGB** para display online; `mfr_code` sirve para **touch-up paint / upholstery match**.

**warranties (warranty):** `type`, `name`, `months`, `miles` (warranty as-new).
**pricing:** `msrp_price` (base), `invoice_price`, `destination_charge`, `gas_guzzler_tax`; además **as-built/as-configured MSRP** (nivel opción, build data). Precio actualizado durante el año a OEM vigente.

**ADAS (página extended/web-services):** lista de componentes ADAS normalizados por marca/año (2015→), `sensor placement/location`, **parámetros de operación** (`min/max speed`, `min/max distance`), `manual configuration options` por feature.
**EV/Hybrid:** especificaciones EV y de powertrain híbrido, OEM order codes de powertrain.

### 3.A.3 OEM Build Data & DataOne Verified Records [V]
**Build data** = configuración real de fábrica directa del OEM (Toyota/Lexus/Scion, Ford/Lincoln/Mercury MY2011→, GM…). Campos clave: `trim` asignado, `standard equipment` del trim, `installed options & packages`, `interior_color`, `exterior_color`, `upholstery type`, `weights & dimensions`, `safety features`, `installed transmission`, `base MSRP`, `as-built/as-configured MSRP` (option-level), `available options`. **Verified Records** = fuente propia de DataOne ("industry-leading accuracy") cuando no hay build data OEM. Dos niveles: **trim-level** (trim + std equipment + base) y **option-level** (+ todas las opciones/packages instaladas + as-built MSRP).

### 3.A.4 Advanced VIN Decoding Logic API [V]
REST HTTPS, **POST con hasta 50 VINs/vehículos** por request, **XML o JSON** in/out. Devuelve **one-to-one style match** usando `model_numbers`, **raw DMS data** y descripciones **sin normalizar** como input. Output: vehicle descriptors, installed equipment, optional equipment (known installed **y** available), technical specs, factory warranties, original vehicle & option pricing, OEM internal/external colors. **High capacity** para 2-3M vehículos/mes. Parámetros documentados (tech guide): `client_id`, `auth_code`, `vins` (≤50, CSV), `style_ids`, `model_numbers`, `show_style_loop`. Estructura: `decoded_vin_data` → `decoded_version`, `decoder_error` (`error_code`/`error_message`), `vin_number` → `vin_error`, `common_data`, `available_vehicle_styles` → `vehicle_style` (name/style_id/complete).

### 3.A.5 Vehicle Research Data [V]
Para tools de shopping interactivo. **Datos normalizados** + **comparación** + **build logic**.
- **Vehicle Comparison Data** — agrupación normalizada "bottom-up" de equipamiento estándar/opciones por modelo/trim. Dimensiones comparables: `body style`, `seating capacity & configuration` (incl. third-row), `upholstery type`, `pricing`, `powertrain specs`, `engine specs`, `warranty`, `technical specs`, `installed safety equipment`, `safety ratings`, `EPA MPG`, `Green Vehicle Scores`, `technology features`, `entertainment features`, `comfort & convenience features`, `3rd-party awards & accolades`, `equipment`, `studio images`, `colors & colorized images`.
- **Vehicle Build Logic Data** — reglas OEM para configuradores (30+ brands): `color options`, `engine options`, `transmission options`, `equipment & packages`, **inclusions / exclusions / requirements**, **option combination pricing effects**, **date dependencies** (disponibilidad por fecha).
- **Weighted vehicle feature importance rankings** (scoring propietario de importancia de features).

### 3.A.6 Vehicle Service Data [V]
- **OEM Service Schedules:** intervalos **time-based** y **mileage-based**; schedule **normal/standard**, **premium**, **severe**, **high-mileage**; **region-specific**; `OEM warning codes`, `maintenance codes`, naming estandarizado.
- **Auto Care ACES Mapping:** liga `DataOne vehicle_id`, `engine_id`, `transmission_id` → **ACES `VehicleID`, `EngineConfigID`, `TransmissionID`, `VehicleToEngineID`** (VCdb); para parts/accessories/tires/fluids.
- **NHTSA Recalls (1981→, light-duty filtrado):** `recall year`, `make`, `model`, `equipment involved`, `issue description`, `recall schedule`, `corrective action`; VIN-referenced + DataOne VehicleID.

### 3.A.7 Mapping & 3rd-Party Validation Data [V]
Mapeos (vía `DataOne VehicleID`/`EngineID`/VIN/YMMT):
- **J.D. Power Used Car Guide** (ex-NADA) — VehicleID/EngineID mapping (valoración usado).
- **KBB (Kelley Blue Book) Used Car Guide** — VehicleID→KBB ID (valoración new/used).
- **Cox Automotive Rates & Incentives** (ex-AIS Rebates) — rates/incentivos/rebates.
- **EPA MPG** (VIN-referenced, todos los US).
- **EPA Green Scores** — `Air Pollution score`, `Greenhouse Gas score`, **SmartWay** y **SmartWay Elite** status.
- **NHTSA 5-Star Safety Ratings** (1990→) — overall + por **impact type** + por **passenger area** tested.
- **Awards & Accolades** (2006→) — `name`, `source`/awarding party, `website`, `citation`, `snippet`, `type`, `criteria` (engine/transmission-specific). Solo positivos. Fuentes: Car and Driver, Green Car Journal, IIHS, Edmunds, etc.
- **EVOX Media Mapping** — `evox VIF` ↔ DataOne VehicleID; color ID/code ↔ Evox colorized photos; nivel de match (`matches_year/make/model/trim/body_type/cab_type/doors/drive_type`). **Izmo Images** mapping análogo.
- **Custom mapping** a cualquier estándar (p. ej. otras guías de valoración usada).

### 3.A.8 Dealer Inventory Feeds [V]
**5.000+ dealers**; inventario **pre-decodificado** con opcional identificado + **fotos reales**; selección por **dealer / zip / state / national**; **feed XML nightly**; alta de dealer en horas.

### — FAMILIA B · VEHICLE SHOPPING SOLUTIONS (PerfectFit® API Suite) —
"Top-to-bottom of funnel": Shopper → Research → Compare → Build; modular o integrado; API web service.
- **3.B.1 PerfectFit Vehicle Shopper API** [V] — búsqueda **attribute-based** (no solo YMM). Rankea por **importancia del consumidor**: `green`, `luxury`, `performance`, `safety`, `technology` + **scoring propietario** de vehículos/equipamiento. Devuelve un "**PerfectFit vehicle**" + **best-fit list**; captura **behavioral insights** para marketing.
- **3.B.2 PerfectFit Research API** [V] — ficha completa por modelo/trim: `vehicle specs`, `installed & optional equipment`, `color options`, `MPG`, `safety ratings`, etc.; **accordion dropdowns**, navegación por model-year/trim, **imágenes interior/exterior multi-ángulo (eVox)**, ratings según criterio de búsqueda.
- **3.B.3 PerfectFit Compare API** [V] — comparación side-by-side entre makes/models/trims con datos **normalizados**; grupos: key features, MPG & Green Scores, safety ratings, specs, engine & drivetrain, warranty, options, awards, equipment, studio images, colors & colorized images.
- **3.B.4 PerfectFit Build API** [V] — configurador "build & price" con **reglas de opción y pricing OEM**; solo permite vehículos **buildable**; submit como **lead**.
- **Reverse VIN Lookup API** (suite Research, 2023) [V] — identifica vehículo con **mínima** info del consumidor; genera **partial VIN / VINStub** para envío a carrier (caso insurance quote).

### — FAMILIA C · VEHICLE IMAGES & OVERVIEWS —
- **3.C.1 Vehicle Images** [V] — **Single Studio Stills** y **Premium Colorized Images** (front 3/4, 2003→), model/trim/body-style específicas, fondo **blanco o transparente**; referenciadas a `DataOne VehicleID`, `VIN`, `Y/M/M`. Lifestyle gallery (shot_code/shot_name, thumb/full). EVOX/Izmo para colorizado completo.
- **3.C.2 Vehicle Overviews** [V] — reseñas editoriales del coche "as new" (writers desde 1992), **2009→**, update semanal, con foto de marketing; para VDP de clasificados/dealers y research genérico.

### — FAMILIA D · CUSTOM DEVELOPMENT & CONSULTATION —
- **3.D.1** [V] — soporte de integración (production support gratis) + **Client Services billable** (arquitectura, estructuras de datos custom).

### — FAMILIA G · MARKET INTELLIGENCE (Cross-Sell, marca dealer; data licensing → DataOne) —
**3.G.1 Cross-Sell market intelligence** [V] — desde la fusión 2026, su **data licensing** es DataOne.
- **Fuentes:** **state vehicle registrations / DMV records** + partnerships directos **Tesla / Rivian** (EV). Cobertura **38 estados**.
- **Métricas/fields:** `new vehicle registrations`, `used vehicle registrations`, `sales transactions (PII-free)`, `vehicle sales history`, `units sold by make`, `units sold by model`, `dealer market share`, `dealer rankings / scorecard`, `zip-code performance`, `year-over-year comparison`, `EV sales data`, `lender/lienholder summary`.
- **Reportes / plataforma:** **Cross-Sell Interactive®**, **MarketIntel™ Reporting**; **Dealer Scorecard**, **Custom Market Area**, **Market Analysis** (short-term trends), **Summaries** (monthly dealer/lienholder detail), **Heat mapping** (hotspots geográficos), Top dealership/zip reports. Paquetes **Starter / Advanced / Premium**.

---

## 4. Metodología y fuentes de datos [V]
- **OEM-direct, no predictivo:** "sourcing direct from the vehicle manufacturers… following actual **verified production schedules**, **without use of predictive VIN modeling or arbitrary vehicle carryovers**". Énfasis explícito anti-modelado predictivo (contraste con muchos decoders).
- **Dos capas de identificación por VIN:** (1) lo **codificado en el VIN** (year, make, model, engine, transmission, GVWR range, restraint type) y (2) **enriquecimiento** a trim/opción vía **build data OEM** (Toyota/Ford/GM) o **DataOne Verified Records**.
- **Manejo de ambigüedad de estilo:** un VIN puede mapear a varios `vehicle_style`; se devuelve `common_data` (compartido) + `available_vehicle_styles`; se resuelve con `style_ids` o `model_numbers` (proceso de 2 pasos o `show_style_loop=1`). Atributos `standard` / `installed` (Y/N/UK) en engines y transmissions para indicar instalado vs disponible.
- **Normalización dual:** mantiene **descripción de marketing OEM** (compliance) **y** **descripción normalizada** (search/compare).
- **Mapeo a estándares de industria:** ACES (Auto Care), NHTSA, EPA, J.D. Power, KBB, Cox/AIS, EVOX/Izmo — DataOne es **service provider identificado por Auto Care Association**.
- **Confianza/calidad:** "industry-leading accuracy"; build data "complete coverage for all vehicles sold within the model years offered".
- **Cross-Sell:** market intelligence a partir de **matriculaciones estatales/DMV** (PII-free) + feeds directos de OEMs EV.
- **Actualización:** API en tiempo real; ficheros **delimitados con updates diarios/semanales (SFTP)**; pricing OEM actualizado durante el año; feeds de inventario **nightly**; Cross-Sell **mensual** (dealer/lienholder).

---

## 5. Entrega
- **API REST sobre HTTPS** — XML **o** JSON; GET (v6) y **POST batch ≤50 VINs** (Advanced Logic). Free trial con `client_id`/`auth_code`. [V]
- **Fichero plano delimitado** (coma o tab) con **updates diarios/semanales vía SFTP**. [V]
- **Dump de base de datos relacional** — CSV para importar a **MSSQL / MySQL / Oracle / Postgres**. [V]
- **Feed XML nightly** (Dealer Inventory Feeds). [V]
- **Combinable**: todos los productos VINBasic + extended/research/mapping/service pueden entregarse en **un único fichero o una sola llamada**. [V]
- **Cross-Sell**: plataforma web **Cross-Sell Interactive®** + reporting (MarketIntel™). [V]
- **Portal cliente** (`my.dataonesoftware.com`), **dev docs** (elogiadas por Fleetio), production support + consultoría billable. [V]

---

## 6. Precio
- **Modelo = cotización personalizada, sin tarifas públicas.** "Each licensing instance is unique." Factores: **uso previsto**, **tipo y cantidad de datos**, **volumen de VINs/mes**, **nº de endpoints servidos**, **tráfico web mensual único**. Proceso: formulario de quote → pricing + recomendación de producto + llamada de consultoría "no obligation". [V]
- **Free VIN decoder API trial** disponible (límite de decodes; errores `ET`/`ED` al expirar/agotar). [V]
- **High-capacity** para 2-3M vehículos/mes (tier comercial grande). [V]
- **[3P]** Estimación de tercero (G2/comparadores): contratos enterprise "**desde $10.000+/año**", escalando por uso/productos; onboarding vía sales call + contrato. **No confirmado por DataOne** (no hay número oficial público). [A/3P]

---

## 7. Placement — dónde se ubica cada dato en su UI/entrega
> Patrón a copiar por Cardeep: superficie/pantalla → dato. (DataOne provee data + business logic; el "UI" final lo monta el cliente, pero las páginas de producto prescriben **placement sugerido**.)

| Dato | Dónde lo colocan (superficie) |
|---|---|
| Standard/optional equipment + marketing descriptions OEM | **Vehicle Detail Page (VDP)** y descripciones de inventario en webs de dealer (prioriza y resalta los features "consumer-friendly"). |
| Equipamiento normalizado + key features/categorías/ratings | **Filtros de inventory search** + **módulo Compare** (side-by-side por trim/modelo). |
| Technical specs / dimensiones / pesos / GVWR-GCWR | **Páginas de research model/trim**; clasificación para **vehicle transport logistics**. |
| EPA MPG + EPA Green Scores | **Vehicle details pages** ("provide EPA's Green Scores in your vehicle details pages"). |
| NHTSA 5-Star Safety Ratings | **Research + Compare** online y **inventory marketing**; también risk/insurance. |
| Awards & Accolades | **Marketing**: websites, mailers, email campaigns, ebrochures; promoción de **pre-owned**. |
| Vehicle Images (front 3/4, colorized) | **Inventory display / VDP** y **online quoting & lead forms**. |
| Vehicle Overviews (reseña editorial) | **Dealer websites** (research genérico de modelo y/o **VDP**); clasificados/portales en builder/configuration/compare. |
| Colores (HEX/RGB, two-tone) | **Display de color online**; `mfr_code` → match de **touch-up paint / upholstery**. |
| Build logic + reglas de opción OEM | **Configurador "Build & Price"** (PerfectFit Build) → submit como **lead**. |
| Scoring por importancia (green/luxury/perf/safety/tech) | **Landing de shopping attribute-based** (PerfectFit Vehicle Shopper) → "PerfectFit vehicle" + best-fit list. |
| Specs/equipment/MPG/safety por modelo-trim | **Research pages con accordion dropdowns** + navegación model-year/trim + imágenes multi-ángulo (PerfectFit Research). |
| Warranty (as-new) | **VDP** + **marketing dirigido** (clientes con warranty a punto de expirar). |
| ADAS / safety features / equipamiento instalado | **Insurance underwriting & rating** + **claims** (respuesta concreta de qué equipo lleva el VIN). |
| Reverse VIN Lookup / VINStub | **Formularios de cotización de seguro** (mínimo input del consumidor → partial VIN al carrier). |
| OEM service schedules + recalls + ACES | **Service lane / scheduling & shop logistics** + **service marketing/CRM** (recordatorios, recall outreach). |
| J.D. Power / KBB valuation mapping | **Dealer inventory management** (lookup de valoración usado/new vía mapping). |
| Cox rates & incentives mapping | **Web de dealer / F&I** (incentivos en tiempo real). |
| Registrations / sales / market share / lienholder (Cross-Sell) | **Cross-Sell Interactive® dashboard**, **Dealer Scorecard**, **heat maps**, **MarketIntel™ reports** (dealer/media/lender). |

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **VIN-decoding "OEM-direct" a nivel trim/opción con build data real de fábrica** (Toyota/Lexus/Scion, Ford/Lincoln/Mercury MY2011→, GM): identifica el **as-built** (opciones, packages, color, upholstery, as-configured MSRP) — más profundo que decoders basados solo en patrón VIN.
- [V] **Anti-predictivo declarado**: datos por **verified production schedules**, sin "predictive VIN modeling" ni "arbitrary carryovers" — argumento de exactitud frente a competidores que extrapolan.
- [V] **Profundidad de spec atómica enorme** (data dictionary completo: performance off-road —angles of approach/departure/breakover—, 3 filas de head/hip/leg/shoulder room, tank_1/2, oil_capacity, redline, valve_timing, bed_code, etc.) servida por API **o** DB relacional.
- [V] **ADAS estandarizado entre marcas (2015→) con ubicación de sensores y parámetros de operación** — útil para insurance/ADAS calibration; poco común a este nivel.
- [V] **Doble descripción marketing-OEM + normalizada** (compliance OEM **y** búsqueda/comparación), con `order_code` interno OEM.
- [V] **Suite shopping completa top-to-bottom-funnel** (Shopper attribute-based con scoring propietario → Research → Compare → Build→lead) lista para portales/dealers.
- [V] **Hub de mapeos a estándares de industria** (ACES/VCdb field-level, NHTSA, EPA Green/SmartWay, J.D. Power, KBB, Cox/AIS, EVOX/Izmo) bajo un único `DataOne VehicleID` — actúa de "rosetta stone" de IDs.
- [V] **Reverse VIN Lookup / VINStub** orientado a insurance (form-fill monetizable con mínimo input) — caso de uso vertical específico.
- [V] **Cobertura multi-segmento de vehículo** (autos, HD clases 4-8, powersports, trailers 850+ fabricantes) bajo una sola integración.
- [V] **Tras fusión Cross-Sell (2026): market intelligence (matriculaciones/ventas/market share/lienholder, 38 estados, EV directo de Tesla/Rivian)** bajo el mismo techo — pasa de "qué es el coche" a también "cómo se mueve el mercado".
- [V] **Respaldo de Dominion Enterprises** (estabilidad, sister brands) + base instalada (Uber, CarGurus, Carfax, Fleetio, Experian, Bosch…).

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **No es guía de valoración propia**: **no** publica trade/retail/wholesale, residual value %, depreciation curve, price-to-market %, days-to-sell ni forecasting. La valoración entra **solo por mapping revendido** a J.D. Power y KBB (IDs, no algoritmo propio). Contraste fuerte con Black Book/J.D. Power/cap hpi.
- [V] **No expone listings vivos ni inventario de mercado en tiempo real** como producto de pricing (los Dealer Inventory Feeds son datos de dealer pre-decodificados, no un índice de mercado VIN-level tipo MarketCheck). El "market" lo aporta Cross-Sell, pero vía **matriculaciones/ventas**, no listings online scrapeados.
- [V] **Sin historial de vehículo (siniestros, propietarios, odómetro/fraude, títulos)** tipo Carfax/HPI — DataOne describe el coche "as-new", no su vida. (Carfax es **cliente**, no competencia en esto.)
- [V] **Geografía limitada a EE.UU. + Canadá**; Cross-Sell solo **38 estados US**. Sin Europa/LatAm/APAC.
- [V] **No decodifica pre-1981** ni (en producto núcleo) fleet/grey-market/out-of-market sin packs específicos; RV explícitamente fuera (error `RV`).
- [V] **Sin TCO / running costs / labor times / part prices / fluid capacities como catálogo de reparación** — Vehicle Service Data da **schedules + recalls + ACES mapping**, pero **no itemiza tiempos de mano de obra, precios de pieza ni TSBs** (verificado: la página no lista estos como campos).
- [V] **Precio opaco**: sin tarifas públicas, todo por quote; el "$10k+/año" es **estimación de tercero**, no confirmada. Onboarding requiere sales call (fricción vs self-service de MarketCheck).
- [V] **`fabric_type` histórico marcado "unused"** en v6.0 (luego retirado de interior); algunos campos del dictionary pueden venir vacíos según el account (tags desactivados aparecen vacíos o ausentes).
- [V] **Awards & Accolades sesgado a positivo por diseño** (excluye reviews negativas) — sirve para marketing, **no** para evaluación objetiva.
- [V] **`spec-catalog.dataonesoftware.com` no resuelve** (NXDOMAIN): no hay un explorador de catálogo público; el data dictionary detallado vive en la **client section** (tras login) — transparencia pública parcial.
- [A] **Data dictionary canónico citado es v6.0 (2009)**: el **esquema base** sigue vigente y se ha **ampliado** (ADAS, EV, build data OEM, JSON, POST batch), pero **no** hay un dictionary v-actual público verificado campo-a-campo; las adiciones modernas se verifican por páginas de producto/PR, no por un doc de esquema reciente.
- [A] **Profundidad EV** (battery kWh, rango, tiempos de carga, etc.) mencionada como "EV specifications" pero **no** desglosada campo-a-campo en fuentes públicas.

---

## 10. Fuentes (URLs)
- https://www.dataonesoftware.com/ — home: VIN decoding líder, productos, clientes (Uber, CarGurus, Carfax, DealerSocket, AutoRevo, Total Care Auto, Overfuel), 877-GET-VINS.
- https://www.dataonesoftware.com/about — "Automotive Data Solutions Since 1999"; Dominion Enterprises 2007; HQ Beverly MA; >80% new US light-duty; clientes (Xtime, Zebra, Fleetio, LGM, Credit Karma, Experian, Bosch).
- https://www.dataonesoftware.com/products — taxonomía de productos.
- https://www.dataonesoftware.com/vehicle-data-vin-decoding — atributos núcleo + scope (passenger→tractor-trailer), US/Canadá, build data + verified records, partial/VINless, mapping 3P.
- https://www.dataonesoftware.com/web-services-vin-decoder-api — REST HTTPS JSON/XML; trim/option-level; ADAS; EV; as-built MSRP; NHTSA; service schedules; "billions of decodes/year".
- https://www.dataonesoftware.com/oem-build-data-and-verified-records — build data OEM (config de fábrica) vs Verified Records; campos trim/options/colors/upholstery/weights/safety/transmission/base+as-built MSRP.
- https://www.dataonesoftware.com/vehicle-data-vin-decoding/extended-vehicle-data — dimensiones, pesos, capacidades, ADAS (sensor placement, min/max speed/distance), colores HEX/RGB/two-tone/touch-up, pricing (MSRP/invoice/destination/gas-guzzler), warranty, EV/hybrid, 1981→ (ADAS 2015→).
- https://www.dataonesoftware.com/vehicle-data-vin-decoding/vehicle-research — comparison data (body/seating/upholstery/pricing/powertrain/warranty/specs/safety/MPG/green/tech/entertainment/comfort/awards), build logic (inclusions/exclusions/requirements, pricing effects, date deps), weighted feature importance.
- https://www.dataonesoftware.com/vehicle-data-vin-decoding/vehicle-service-data — OEM schedules (time/mileage; normal/premium/severe/high-mileage), ACES (VCdb IDs), NHTSA recalls, DataOne VehicleID.
- https://www.dataonesoftware.com/vehicle-data-vin-decoding/mapping-and-3rd-party-validation-data — J.D. Power, KBB, ACES, EPA Green/MPG, NHTSA 5-star, EVOX VIF; IDs (VehicleID, EngineID, Evox VIF, color IDs).
- https://www.dataonesoftware.com/vinbasic-vin-decoding — VINBasic Autos&Trucks (1981→, US), Canadian (2001→), HD (clases 4-8), Powersports, Trailers (850+ fab/50+ tipos); campos núcleo + GVWR + MSRP.
- https://www.dataonesoftware.com/software/perfectfit-vehicle-shopper — attribute-based shopping; ranking por green/luxury/performance/safety/technology + scoring propietario; PerfectFit + best-fit.
- https://www.dataonesoftware.com/software/perfectfit-research — research pages, accordion dropdowns, specs/equipment/colors/MPG/safety, imágenes multi-ángulo eVox.
- https://www.dataonesoftware.com/software/vehicle-comparison — Compare API: grupos (key features, MPG & green, safety, specs, engine & drivetrain, warranty, options, awards, equipment, studio/colorized images).
- https://www.dataonesoftware.com/software/perfectfit-build — Build & Price con reglas/pricing OEM, solo buildable, submit lead.
- https://www.dataonesoftware.com/media/images — Studio Stills + Colorized (front 3/4, 2003→, white/transparent), referenciadas a VehicleID/VIN/YMMT; EVOX/Izmo mapping.
- https://www.dataonesoftware.com/developers — entrega JSON/XML, flat files (coma/tab), DB dumps (MSSQL/MySQL/Oracle/Postgres); testimonial Fleetio.
- https://www.dataonesoftware.com/faqs — 1981→, US/Canadá, passenger/light/medium/HD + moto/scooter/off-road; delimited FTP daily/weekly; REST JSON/XML.
- https://www.dataonesoftware.com/solutions/dealer-service-providers — placement: VDP, merchandising, compare, build & price, service lane, marketing; DMS extraction/feeds, CRM, service scheduling.
- https://www.dataonesoftware.com/solutions/auto-insurance-data — underwriting/rating/claims; ADAS/safety features; Reverse VIN Lookup; partial VIN/VINStub; form-fill monetizable.
- https://offers.dataonesoftware.com/quote-pricing — pricing por quote; factores (uso, tipo/cantidad de datos, VINs/mes, endpoints, tráfico); free trial; no obligation.
- https://www.dataonesoftware.com/hs-fs/hub/123171/file-959562714-pdf/docs/Dataone-Catalog.pdf — **Products & Services Catalog** (taxonomía completa + Advanced VIN Decoding Logic API, Dealer Inventory Feeds 5000+, Cox Rates&Incentives, Izmo, ACES field-level, EPA Green Air/GHG/SmartWay, Vehicle Overviews desde 1992/2009→).
- https://vin.dataonesoftware.com/Portals/123171/docs/techguide-xml-vin-decoder.pdf — **XML VIN Decoder v6.0 Data Dictionary** (esquema atómico completo: basic_data, specifications, engines, transmissions, fuel_efficiency, eng_trans_mpg_associations, features, options, colors, warranties, pricing, media, awards_accolades, evox_mapping; parámetros, errores).
- https://www.dataonesoftware.com/newsroom — cronología: fusión Cross-Sell (29-ene-2026), Verisk 2025 (Jake Maki), casos Overfuel/Total Care/AutoRevo, Reverse VIN (2023), GM (2023), Ford (2022), Duck Creek (2022), SBD/VehiclePlannerPlus (2021).
- https://www.prnewswire.com/news-releases/dataone-software-vin-decoder-solution-to-integrate-toyota-build-data-301142171.html — Toyota/Lexus/Scion build data (30-sep-2020): as-configured MSRP, color int/ext, upholstery, options, packages; boilerplate (1999, Dominion 2007, US/Canadá).
- https://www.prnewswire.com/news-releases/dominion-enterprises-announces-strategic-merger-of-cross-sell-into-dataone-software-to-accelerate-data-solutions-growth-302674292.html — fusión 2026: Jake Maki (Pres. DataOne), John "TD" Scheuren (Pres. Cross-Sell), Joe Kiley (VP Product&Tech); marca DataOne=data licensing / Cross-Sell=dealer; Cross-Sell PII-free sales transaction data.
- https://www.cross-sell.com/ — Cross-Sell Interactive®, MarketIntel™; registrations new/used, sales, make/model perf, dealer scorecard/rankings, market share, zip perf, YoY, EV, lienholder; fuentes registrations/DMV + Tesla/Rivian; 38 estados; Starter/Advanced/Premium.
- https://www.g2.com/products/vehicle-data-vin-decoding/competitors/alternatives — [3P] posicionamiento enterprise, alternativas, estimación pricing "$10k+/año" (no confirmada por DataOne).
- DNS: `spec-catalog.dataonesoftware.com` → **ENOTFOUND/NXDOMAIN** (no es host; etiqueta de categoría del orquestador).

> Verificación: identidad contrastada con ≥3 fuentes (about + PR Newswire boilerplate + Dominion/G2). **Esquema de campos [V] leído directamente** del data dictionary XML v6.0 (PDF, extraído con pdftotext) y del Products & Services Catalog (PDF). Build data OEM y fusión Cross-Sell [V] de PR Newswire + newsroom. Pricing oficial = quote-based [V]; cifra "$10k+" marcada **[3P]** no confirmada. Subdominio "spec-catalog" = etiqueta taxonómica (NXDOMAIN como host, verificado). Campos modernos (ADAS/EV/JSON/POST) verificados por páginas de producto; data dictionary público canónico es v6.0 (2009) — marcado como tal en Gaps.
