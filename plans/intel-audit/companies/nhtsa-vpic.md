# Auditoría atómica — NHTSA vPIC (Product Information Catalog and Vehicle Listing)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> **vPIC** = **"Product Information Catalog and Vehicle Listing"** de la **NHTSA** (National Highway Traffic Safety Administration), agencia del **U.S. Department of Transportation (DOT)**. NO es una empresa comercial ni una guía de valoración: es la **fuente regulatoria pública y gratuita de identificación de vehículo por VIN** de EE.UU., poblada con los datos que los **fabricantes auto-reportan** bajo 49 CFR. Es el **backbone de VIN-decoding sobre el que se montan muchos proveedores comerciales** (DataOne, Vehicle Databases, ClearVin, etc. lo citan/usan como capa base). Web: https://vpic.nhtsa.dot.gov/ · API: https://vpic.nhtsa.dot.gov/api/ · Decoder web: https://vpic.nhtsa.dot.gov/decoder/ · MID: https://vpic.nhtsa.dot.gov/mid/ · Downloads: https://vpic.nhtsa.dot.gov/Downloads · Manufacturer Portal: https://vpic.nhtsa.dot.gov/mfrportal/
> Subdominio cardeep asignado por el orquestador (campo `subdomain`): **official-data**. Es una **etiqueta de categoría** ("dato oficial/gubernamental"), NO un host DNS de vPIC.
> Fecha auditoría: 2026-06-30. Método: **consulta directa a la API en vivo** (GetVehicleVariableList → 144 variables, DecodeVinValues + DecodeVinValuesExtended sobre el VIN de ejemplo `5UXWX7C5*BA` 2011 BMW X3 → 154 claves, GetVehicleVariableValuesList de `vehicle type`/`error code`, GetCanadianVehicleSpecifications, GetAllMakes=12.278, GetAllManufacturers) + navegación de api/ (doc de 25+ endpoints), api FAQ, decoder/, mid/, Downloads, data.transportation.gov + fuentes terceras (Microsoft Learn connector, Wikipedia/NHTSA history, wrappers shaggytech/PyPI).
> Convención: **[V]** = verificado leyendo la fuente / la respuesta de API real · **[A]** = asumido/inferido (marcado) · **[3P]** = dato de tercero, no oficial de NHTSA.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca / sistema | **vPIC — Product Information Catalog and Vehicle Listing** (informalmente "Vehicle Product Information Catalog"; la "v" históricamente = *vehicle*) | [V] |
| Operador | **NHTSA — National Highway Traffic Safety Administration** | [V] |
| Matriz / grupo | **U.S. Department of Transportation (DOT)** — agencia federal del gobierno de EE.UU. | [V] |
| Naturaleza | **Organismo público regulatorio** (no empresa privada, no ánimo de lucro, no producto comercial) | [V] |
| Fundación NHTSA | **1970** (Highway Safety Act of 1970; raíz en el National Traffic and Motor Vehicle Safety Act of 1966) | [V — Wikipedia/Britannica/Archives] |
| HQ | **1200 New Jersey Avenue SE, Washington, DC 20590, EE.UU.** | [V] |
| Helpdesk fabricantes | **manufacturerinfo@dot.gov · 1-888-399-3277** | [V — repetido en home/api/mid/downloads] |
| Versión del sistema | **vPIC v4.06**, último cambio de código **13-jun-2026**; MID **v4.05** (16-may-2026) | [V — api FAQ + mid home] |
| Modelo | **Gratuito, público, sin registro, sin API key, 24/7** | [V — api FAQ] |
| Misión | "Centralized source for basic **VIN decoding**, **Manufacturer Information Database (MID)**, **Manufacturer Equipment Plant Identification** and associated data" | [V — home] |

### Qué es (y qué no es) [V]
- **Es:** la base regulatoria que captura "all the information on how a VIN is assigned by the manufacturer", usada para **decodificar un VIN y extraer información del vehículo** + un **registro de fabricantes (MID)** + identificación de **plantas de equipamiento** + WMIs + documentos regulatorios.
- **No es:** guía de valor, índice de mercado, historial de vehículo, catálogo comercial de equipamiento/marketing, ni proveedor con SLA. No vende nada.
- **Rol en el ecosistema:** es el **"source of truth" oficial de WMI / fabricante / atributos build declarados**. Muchos vendors comerciales lo usan como capa base y construyen valor encima (normalización de trim, imágenes, valoración, mercado). Para Cardeep es la **fuente cero-coste y cero-confianza-friendly** de identidad de vehículo en mercado US.

### Clientes objetivo / usuarios [V]
- **Desarrolladores, programadores e investigadores** que necesitan "raw Vehicle or Manufacturer data".
- **Fabricantes** (vía Manufacturer Portal: presentan VIN guidance/identification).
- **Consumidores** (vía nhtsa.gov/vin-decoder y decoder web).
- **Proveedores comerciales de datos** que lo usan como base (uso de facto, no declarado por NHTSA).

---

## 2. Cobertura

### Geográfica [V]
- **EE.UU.**: vehículos cuyos fabricantes **se registraron con la intención de venderlos, usarlos y/o matricularlos en EE.UU.** Vehículos no registrados vía el proceso de importación 565 → **resultado limitado / excluido** (`Error Code 7`).
- **Canadá (dataset auxiliar):** **Canadian Vehicle Specifications (CVS)** — dimensiones físicas para investigación de colisiones, **año ≥ 1971**, en métrico o US.

### Temporal y de confianza (declarada por NHTSA) [V — api FAQ]
- **1995 → actual: ~99% de exactitud.**
- **1980-1994: 60-65%.**
- **Pre-1980: sin datos** ("el estándar VIN no estaba establecido en EE.UU."). El decoder web rechaza pre-1981 ("Invalid Year Submitted – Pre-1981 Year Decode Attempt").
- Recomendación oficial: **enviar siempre el `modelyear`** (mejora la precisión; permite rangos pre-1980 y actuales).

### Escala / amplitud (medida en vivo) [V]
- **144 variables** de vehículo en el catálogo (`GetVehicleVariableList`, Count=144).
- **154 claves** en el output flat de decode (`DecodeVinValues`) — incluye meta/error/NCSA.
- **12.278 makes** (`GetAllMakes`, Count=12.278).
- **Miles de fabricantes** (`GetAllManufacturers` pagina de 100 en 100, múltiples páginas).
- **9 tipos de vehículo** (ver abajo).

### Scope de vehículos [V]
- **Tipos** (lookup `vehicle type`): **Motorcycle, Passenger Car, Truck, Bus, Trailer, Multipurpose Passenger Vehicle (MPV), Low Speed Vehicle (LSV), Incomplete Vehicle, Off-Road Vehicle.**
- **Nuevo vs usado:** los datos son **build/as-submitted** (cómo el fabricante asigna el VIN) → identifican el vehículo "tal como se fabricó". VIN-referenciados, sirven para nuevo y usado, pero **sin vida del vehículo** (no hay uso/siniestro/km).
- **Tipos de fabricante** (`ManufacturerType`, vía API): 2 Completed Vehicle, 3 Incomplete Vehicle, 4 Intermediate, 5 Final-Stage, 6 Vehicle Alterer, 7 Fabricating Mfr of Equipment, 8 Importer of Equipment, 9 Importer of Vehicles (conform to FMVSS), 10 Replica Vehicle Manufacturer.
- **Tipos de equipamiento regulado** (`GetEquipmentPlantCodes`, 2016+): 1 Tires, 3 Brake Hoses, 13 Glazing, 16 Retread.

---

## 3. Productos + campos atómicos

vPIC ofrece **una sola base de datos** servida por **7 superficies**: (1) Vehicle API, (2) VIN Decoder web, (3) MID, (4) Manufacturer Portal, (5) Standalone DB downloads, (6) Canadian Vehicle Specifications, (7) Modifiers Identification Database. El núcleo de valor para Cardeep son las **144 variables de vehículo** + el **registro de fabricante/WMI/planta**.

### 3.1 Vehicle API (vPIC API) — núcleo [V]
REST sobre HTTPS, **JSON · XML · CSV**, **gratis, sin key, sin registro, 24/7**. **25+ endpoints**. Capacidad ~**1.000-2.000 transacciones/min**; sin límite diario pero piden lotes grandes en off-peak (noches/fines de semana EST). Endpoints documentados (verbatim del doc):

**VIN decoding:**
- `DecodeVin/{vin}` — decodifica a pares **clave-valor con `VariableID` y `ValueID`**; admite VIN parcial con comodín `*`; params `modelyear`, `format`.
- `DecodeVinValues/{vin}` — mismo decode en **formato plano (flat)** (una fila, 154 columnas).
- `DecodeVinExtended/{vin}` — como DecodeVin + variables de **otros programas NHTSA (NCSA, etc.)**.
- `DecodeVinValuesExtended/{vin}` — extended en flat (en la práctica el flat ya incluye los campos NCSA → **mismas 154 claves** que DecodeVinValues; verificado: delta = 0).
- `DecodeVINValuesBatch/` — **lote de hasta 50 VINs**; input `vin,modelYear;vin,modelYear;...`; output flat por VIN.

**WMI (World Manufacturer Identifier):**
- `DecodeWMI/{wmi}` — info de un WMI (3 chars = posiciones 1-3 del VIN, o 6 chars = 1-3 & 12-14).
- `GetWMIsForManufacturer/{manufacturer}` — todos los WMIs de un fabricante; filtro `vehicleType`.

**Fabricante:**
- `GetAllManufacturers` — todos (paginado 100/pág); filtro `ManufacturerType`.
- `GetManufacturerDetails/{manufacturer}` — detalle (dirección, productos, tipos…).

**Make / tipo:**
- `GetAllMakes` — todos los makes (12.278).
- `GetMakeForManufacturer/{manufacturer}` · `GetMakesForManufacturerAndYear/{manufacturer}/{year}`.
- `GetMakesForVehicleType/{type}` · `GetVehicleTypesForMake/{make}` · `GetVehicleTypesForMakeId/{id}`.

**Modelo:**
- `GetModelsForMake/{make}` · `GetModelsForMakeId/{id}`.
- `GetModelsForMakeYear/make/{m}/modelyear/{y}/vehicletype/{t}` · `GetModelsForMakeIdYear/...` (modelyear > 1995).

**Variables / valores:**
- `GetVehicleVariableList` — **las 144 variables** (Name, Description, GroupName, DataType, ID).
- `GetVehicleVariableValuesList/{variable}` — valores aceptados de una variable de tipo *lookup*.

**Regulatorio / equipamiento / Canadá:**
- `GetParts` — ORGs con fecha de carta en rango (type **565** VIN Guidance / **566** Manufacturer ID); máx 1000/pág.
- `GetEquipmentPlantCodes` — códigos de planta de equipamiento (year 2016+; equipmentType 1/3/13/16; reportType New/Updated/Closed/All).
- `GetCanadianVehicleSpecifications/` — dimensiones canadienses (year ≥ 1971; Make/Model; units Metric/US).

---

### 3.2 CAMPOS ATÓMICOS — las 144 variables del catálogo (`GetVehicleVariableList`, en vivo) [V]
> Cada variable tiene `ID`, `Name`, `GroupName`, `DataType` (lookup/string/int/decimal). Listadas por grupo tal como las devuelve la API.

**General:** Make · Manufacturer Name · Model · Model Year · Series · Series2 · Trim · Trim2 · Vehicle Type · Base Price ($) · Destination Market · Note · Non-Land Use · Plant City · Plant Company Name · Plant Country · Plant State.

**Engine:** Displacement (CC) · Displacement (CI) · Displacement (L) · Engine Number of Cylinders · Engine Configuration · Engine Model · Engine Manufacturer · Engine Brake (hp) From · Engine Brake (hp) To · Engine Power (kW) · Engine Stroke Cycles · Fuel Type - Primary · Fuel Type - Secondary · Fuel Delivery/Fuel Injection Type · Valve Train Design · Cooling Type · Turbo · Top Speed (mph) · Electrification Level · Other Engine Info.

**Mechanical/Transmission:** Transmission Style · Transmission Speeds.
**Mechanical/Drivetrain:** Drive Type · Axles · Axle Configuration.
**Mechanical/Brake:** Brake System Type · Brake System Description.
**Mechanical/Battery (EV):** Battery Type · Battery Energy (kWh) From · Battery Energy (kWh) To · Battery Voltage (Volts) From · Battery Voltage (Volts) To · Battery Current (Amps) From · Battery Current (Amps) To · Number of Battery Cells per Module · Number of Battery Modules per Pack · Number of Battery Packs per Vehicle · EV Drive Unit · Other Battery Info.
**Mechanical/Battery/Charger:** Charger Level · Charger Power (kW).

**Exterior/Body:** Body Class · Doors · Windows · Wheelbase Type · Track Width (inches).
**Exterior/Dimension:** Bed Length (inches) · Curb Weight (pounds) · Gross Vehicle Weight Rating From · Gross Vehicle Weight Rating To · Gross Combination Weight Rating From · Gross Combination Weight Rating To · Wheelbase (inches) From · Wheelbase (inches) To.
**Exterior/Truck:** Bed Type · Cab Type.
**Exterior/Bus:** Bus Type · Bus Length (feet) · Bus Floor Configuration Type · Other Bus Info.
**Exterior/Trailer:** Trailer Body Type · Trailer Type Connection · Trailer Length (feet) · Other Trailer Info.
**Exterior/Motorcycle:** Custom Motorcycle Type · Motorcycle Chassis Type · Motorcycle Suspension Type · Combined Braking System (CBS) · Wheelie Mitigation · Fuel-Tank Type · Fuel-Tank Material · Other Motorcycle Info.
**Exterior/Wheel Tire:** Number of Wheels · Wheel Size Front (inches) · Wheel Size Rear (inches).

**Interior:** Steering Location · Entertainment System.
**Interior/Seat:** Number of Seats · Number of Seat Rows.

**Passive Safety System:** Seat Belt Type · Pretensioner · Other Restraint System Info.
**Passive Safety/Air Bag Location:** Curtain Air Bag Locations · Front Air Bag Locations · Knee Air Bag Locations · Seat Cushion Air Bag Locations · Side Air Bag Locations.

**Active Safety System:** Antilock Braking System (ABS) · Electronic Stability Control (ESC) · Traction Control · Tire Pressure Monitoring System (TPMS) Type · Event Data Recorder (EDR) · Keyless Ignition · Auto-Reverse System for Windows and Sunroofs · Automatic Pedestrian Alerting Sound (Hybrid/EV) · SAE Automation Level From · SAE Automation Level To · Active Safety System Note.
**Active Safety/911 Notification:** Automatic Crash Notification (ACN)/Advanced ACN (AACN).
**Active Safety/Backing Up & Parking:** Backup Camera · Parking Assist · Rear Automatic Emergency Braking · Rear Cross Traffic Alert.
**Active Safety/Forward Collision Prevention:** Crash Imminent Braking (CIB) · Dynamic Brake Support (DBS) · Forward Collision Warning (FCW) · Pedestrian Automatic Emergency Braking (PAEB).
**Active Safety/Lane & Side Assist:** Blind Spot Warning (BSW) · Blind Spot Intervention (BSI) · Lane Departure Warning (LDW) · Lane Keeping Assistance (LKA) · Lane Centering Assistance.
**Active Safety/Lighting:** Adaptive Driving Beam (ADB) · Daytime Running Light (DRL) · Headlamp Light Source · Semiautomatic Headlamp Beam Switching.
**Active Safety/Safe Distance:** Adaptive Cruise Control (ACC).

**Internal (NCSA crash program):** NCSA Body Type · NCSA Make · NCSA Model · NCSA Note.

**Meta / error (no-grupo):** Error Code · Error Text · Additional Error Text · Suggested VIN · Possible Values · Vehicle Descriptor.

### 3.2.b Campos de output adicionales del decode flat (no en el catálogo de 144) [V]
Devueltos por `DecodeVinValues` pero sin entrada propia en `GetVehicleVariableList`: **VIN** (echo) · **MakeID / ModelID / ManufacturerId** (IDs numéricos) · **Adaptive Headlights** · **Driver Assist** · **Rear Visibility System** · **Cash For Clunkers** (elegibilidad del programa CARS) · **NCSA Mapping Exception** · **NCSA Map Exc Approved By** · **NCSA Map Exc Approved On**. (El resto de las 154 claves son abreviaturas JSON de las 144 variables: ABS, ESC, GVWR/GVWR_to, EngineHP/EngineHP_to, etc.)

### 3.3 VIN Decoder (herramienta web) [V]
`https://vpic.nhtsa.dot.gov/decoder/` — "Welcome to VIN Decoding :: provided by vPIC". Input **VIN** + **Model Year** (opcional; "If entered the year from VIN will be ignored"). Decodifica completo o parcial. Resultados agrupados por las **categorías del catálogo** (General, Engine, Exterior, Mechanical, Active/Passive Safety…) con **sección "Plant Information"** (lugar y país de fabricación) al final. Permite **imprimir/extraer** datos de vehículo y de tráiler. Enlaza a **Canadian Vehicle Specifications** y al **New Manufacturer's Handbook** (cálculo del check digit). Hay también la versión consumer en `nhtsa.gov/vin-decoder` (403 al fetch directo, pero documentada).

### 3.4 Manufacturer Information Database (MID) [V]
`https://vpic.nhtsa.dot.gov/mid/` (v4.05). Buscador de **fabricantes de vehículo y equipamiento**. Funciones/pantallas:
- **Organization** — buscar fabricante por **name, DBA, trade names, location, type** (multi-criterio = AND). Devuelve dirección, productos, makes/models, tipos.
- **Part 565 & 566** — documentos de submittal regulatorio por **file name (formato `ORG10126`)** y filtro por fechas de carta.
- **Part 586 (Replica Vehicles)** — réplicas por original make/model/body type/model year + link a fabricante de réplica aprobado.
- **Equipment Plants** — fabricantes de **tire, brake hose, retread, glazing** por equipment type y **DOT code**.
- **World Manufacturer Identifier (WMI)** — fabricante por WMI, product type, make/model.
- **Modifiers** (`/mid/home/modifiersearch`) — registro de **modificadores de vehículo para personas con discapacidad** (Modifiers Identification Database).

Campos del registro de fabricante/WMI/planta (atómicos): `Manufacturer Name` · `DBA / Trade Names` · `Address / City / State / Country` · `Manufacturer Type` · `WMI code` · `WMI Date Available To Public` · `Product/Vehicle Type` · `Make(s)` · `Model(s)` · `Year From` · `Year To` · `Equipment Plant Code (DOT)` · `Equipment Type` · `Plant Status` · `ORG document id` · `Letter date` · `Submittal type (565/566)`.

### 3.5 Manufacturer Portal [V]
`https://vpic.nhtsa.dot.gov/mfrportal/` — centro online donde los **fabricantes presentan** VIN requirements (565), manufacturer identification (566) y filings relacionados, con **seguimiento de estado** de las solicitudes. (Surface de entrada de datos, no de consumo.)

### 3.6 Standalone vPIC Database (Downloads) [V]
`https://vpic.nhtsa.dot.gov/Downloads` — base de datos descargable **lite (solo VIN decoding)**; resto (makes/models/variables/atributos) requiere la API. Formatos:
- **MS SQL Server**: `vPICList_lite_2026_06.bak.zip` (176 MB, 13-jun-2026; SQL Server 2019+; stored procedure `spVinDecode`).
- **PostgreSQL plain**: `vPICList_lite_2026_06.plain.zip` (72,3 MB; PG 17+; schema `vpic`).
- **PostgreSQL custom**: `vPICList_lite_2026_06.custom.zip` (65,5 MB).
- Patrón de nombre `vPICList_lite_YYYY_MM` → **actualización mensual** [V por patrón + fechas].

### 3.7 Canadian Vehicle Specifications (CVS) [V]
`GetCanadianVehicleSpecifications` / `decoder/CaVehSpec` — dimensiones físicas para **investigación de colisiones** (Transport Canada), año ≥ 1971. Campos (verificado en respuesta real): **MAKE · MODEL · MYR** (model year) · **A · B · C · D · E · F · G** (medidas longitudinales/verticales/voladizo) · **OL** (overall length) · **OW** (overall width) · **OH** (overall height) · **WB** (wheelbase) · **TWF** (front track width) · **TWR** (rear track width) · **CW** (curb weight) · **WD** (weight distribution Front/Rear %). Unidades cm/inch o kg/lb.

### 3.8 Open Data mirrors (data.transportation.gov / data.gov) [V]
La NHTSA publica vPIC también como **datasets abiertos** (VIN Decoder, Vehicle API JSON/JSV/CSV, MID) en `data.transportation.gov` y `catalog.data.gov`, replicando el contenido para descarga masiva / análisis.

---

## 4. Metodología y fuentes de datos
- **Auto-reporte regulatorio del fabricante** [V]: "The vPIC Dataset is populated using the information submitted by the Motor Vehicle manufacturers through the **565 submittals**." Marco: **49 CFR Parts 551-595**, en particular **Part 565** (VIN guidance), **Part 566** (manufacturer identification), **Part 574** (Tire Identification Numbers), **Part 586** (replica), + brake hose/glazing/adapted vehicles.
- **Decodificación determinista por patrón de VIN** [V]: el catálogo guarda **cómo cada fabricante asigna su VIN**; el decode mapea posiciones del VIN → variables. **No es predictivo ni "enriquecido" a marketing**: refleja exactamente lo declarado. De ahí la **debilidad en trim** (los fabricantes no reportan trim de forma homogénea).
- **Sistema VariableID/ValueID** [V]: cada dato es una variable (ID) con su valor (ID) — esquema normalizado y estable para integración.
- **Validación de check digit + códigos de error** [V]: 15 `Error Code` (verificado): 0 limpio/check digit OK; 1 check digit no calcula; 2/3/4 VIN corregido en 1 posición; 5 errores en varias posiciones; 6 VIN incompleto; 7 fabricante no registrado para venta/import en US; 8 sin datos detallados; 9 Glider Warning; 10 Off-Road Vehicle Warning; 11/12 model year incorrecto/aviso; 14 imposible decodificar algunos caracteres. Más `Suggested VIN` (corrección sugerida) y `Possible Values`.
- **Confianza declarada** [V]: ~99% (1995+), 60-65% (1980-94), nada pre-1980.
- **Actualización**: código vPIC v4.06 (13-jun-2026); DB descargable mensual (`_2026_06`); MID v4.05 (16-may-2026). La API refleja el catálogo vivo conforme entran submittals. Cadencia exacta del refresco de datos **no publicada** [A].

---

## 5. Entrega
- **API REST** (HTTPS) → **JSON · XML · CSV**; GET por VIN/recurso + **POST batch ≤50 VINs**. Sin key, sin registro. [V]
- **Decoder web** (HTML, imprimible/exportable) para uso manual. [V]
- **MID web** (buscador de fabricantes/WMI/plantas/documentos). [V]
- **Manufacturer Portal** (submission + tracking, lado fabricante). [V]
- **Standalone DB**: backup **MS SQL Server `.bak`** + **PostgreSQL plain/custom** (restaurable local, con stored procedure `spVinDecode`). [V]
- **Open Data**: descargas CSV/JSON/JSV en data.transportation.gov / data.gov. [V]
- **Conectores 3P**: existe **conector oficial-independiente "NHTSA vPIC" en Microsoft Power Platform** y múltiples wrappers (Python `vpic-api`, JS `@shaggytools/nhtsa-api-wrapper`, etc.) — ecosistema amplio por ser gratis/abierto. [V/3P]

---

## 6. Precio
- **Totalmente gratis.** [V — api FAQ] "NHTSA is a government agency and the services provided on the API are free for use." **Sin registro, sin API key, 24/7.**
- **Sin límite diario de queries**; control automático de tráfico ~**1.000-2.000 transacciones/min**; piden programar lotes grandes en off-peak (noches/fines de semana EST). [V]
- **Sin SLA, sin garantía de rendimiento, sin soporte comercial** — es una API pública compartida. [V/3P]
- **DB descargable**: gratis. **Datos de dominio público** (obra del gobierno federal de EE.UU.). [V/A]

---

## 7. Placement — dónde se ubica cada dato en su UI/entrega
> Patrón a copiar por Cardeep: superficie/pantalla → dato. vPIC sirve datos crudos + un decoder web; el patrón clave es **agrupación por categoría funcional** (mismo `GroupName` que estructura la ficha) y **VIN+ModelYear como única entrada**.

| Dato | Dónde lo colocan (superficie) |
|---|---|
| **VIN + Model Year** (entrada) | Cabecera del **Decoder web**: dos campos (VIN, Model Year opcional) + botón; única puerta de entrada. |
| **Identidad** (Make, Model, ModelYear, Manufacturer, Trim, Series, VehicleType) | Bloque superior del resultado del decode (y primeras columnas del flat). |
| **Plant Information** (Plant City/State/Country/Company) | **Sección al final** de los resultados del decoder web ("Plant Information"). |
| **Engine / Mechanical / Battery** (specs motor, transmisión, drivetrain, EV) | Grupos colapsables por categoría en la ficha del decoder (uno por `GroupName`). |
| **Exterior / Dimensiones / Body / Truck / Bus / Trailer / Motorcycle** | Grupos específicos por tipo de vehículo (sólo aparecen los relevantes al VIN). |
| **Active Safety System (ADAS)** | Bloque "Active Safety System" con sub-grupos (Forward Collision, Lane, Lighting, Backing Up…) — un check por feature. |
| **Passive Safety (airbags, cinturones, pretensioner)** | Bloque "Passive Safety System" / "Air Bag Location". |
| **Error Code / Error Text / Suggested VIN / Possible Values** | Encabezado del resultado: estado de la decodificación + corrección sugerida si el check digit falla. |
| **Atributos crudos (clave-valor + VariableID/ValueID)** | Respuesta **API DecodeVin** (estructurado) o **DecodeVinValues** (flat de 154 columnas) — para integración, no UI. |
| **Lote de VINs** | `DecodeVINValuesBatch` (≤50) — para procesamiento masivo backend. |
| **Fabricante / WMI / planta / documentos** | **MID**: pantallas Organization, WMI, Equipment Plants, Part 565/566, Part 586. |
| **Makes / Models / Vehicle Types / Variables** | Endpoints de listado de la API (`GetAllMakes`, `GetModelsForMake*`, `GetVehicleVariableList`) — alimentan dropdowns/cascadas. |
| **Canadian dimensions (OL/OW/OH/WB/CW/TWF/TWR/WD…)** | Pantalla **Canadian Vehicle Specifications** (selección Year/Make/Model → tabla de medidas). |
| **Modificadores (discapacidad)** | Pantalla **Modifier Search** del MID. |
| **DB completa (VIN decode)** | Página **Downloads** (backup SQL Server / PostgreSQL, restaurable local). |

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Fuente oficial, gubernamental y gratuita** de identificación de vehículo por VIN en EE.UU. — **dominio público, sin key, sin registro, sin coste, sin SLA-lock**. Ninguna guía comercial puede igualar el "$0 + autoridad regulatoria".
- [V] **Registro autoritativo de WMI ↔ fabricante** y de **plantas de equipamiento (DOT codes)** y **documentos regulatorios (565/566/586)** — el "padrón maestro" del que dependen los decoders comerciales.
- [V] **Profundidad en seguridad activa (ADAS) y pasiva regulatoria**: ~40 variables de safety (FCW, AEB, LDW/LKA, BSW/BSI, ACC, TPMS, EDR, ACN/AACN, airbag locations, pretensioner, SAE Automation Level From/To) — granularidad de seguridad poco común y normalizada por el regulador.
- [V] **Variables EV/batería regulatorias**: Battery Type/kWh/Volts/Amps (From/To), cells/modules/packs, EV Drive Unit, Charger Level/Power, Electrification Level — útiles para flota/EV sin coste.
- [V] **Batch de 50 VINs gratis** + **DB descargable completa** (SQL Server/PostgreSQL) para decode offline/local — independencia de red.
- [V] **Esquema estable VariableID/ValueID** + **códigos de error y check-digit + Suggested VIN** (auto-corrección) — ingeniería de integración madura.
- [V] **Canadian Vehicle Specifications** (dimensiones físicas para colisión) — dataset auxiliar único.
- [V] **Ecosistema enorme** (conector Microsoft, wrappers Python/JS, mirrors data.gov) — fricción de integración casi nula.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **CERO valoración y CERO precio de mercado**: no hay trade/retail/wholesale, residual %, curva de depreciación, price-to-market, days-to-sell, market days supply, índice demanda/oferta ni forecasting. Sólo existe **`Base Price ($)`** (MSRP base declarado, frecuentemente vacío), **no** un valor de mercado.
- [V] **Sin historial de vehículo**: nada de siniestros, títulos, propietarios, odómetro/fraude, robo. (Describe el coche "as-built", no su vida.) Contraste total con Carfax/AutoCheck/HPI.
- [V] **Resolución de trim débil e inconsistente** [V/3P]: los fabricantes no reportan trim de forma homogénea → `Trim`/`Series` a menudo vacío, ambiguo o pobre para variantes cercanas. Es su limitación más citada por terceros.
- [V] **Sin imágenes, sin colores, sin equipamiento de marketing/opciones-packages** a nivel comercial: no hay studio stills, RGB/HEX, listas de features de venta, order codes OEM ni MSRP as-configured (eso lo dan DataOne/Chrome/DataForce). vPIC es **atributos regulatorios**, no catálogo comercial.
- [V] **US-céntrico**; cobertura débil para clásicos, heavy-duty, moto y **no-US** (vehículos no destinados a venta/import en EE.UU. → resultado limitado, `Error 7`). Sólo el dataset CVS añade Canadá (dimensiones).
- [V] **Pre-1980 sin datos; 1980-1994 sólo 60-65% fiable.**
- [V] **Sin SLA / sin garantía de rendimiento / sin soporte comercial**: API pública compartida con rate-control; no apta como dependencia crítica sin cacheo/descarga local.
- [V] **Muchos campos vienen vacíos** según lo que el fabricante haya submitteado (p. ej. en el ejemplo BMW X3, sólo ~25 de 154 claves traen valor). La densidad de datos depende del submittal.
- [V] **DB descargable es "lite" (sólo VIN decode)**: makes/models/variables/atributos completos requieren la API online.
- [V] **No es comparador, ni dashboard de mercado, ni alertas, ni informe PDF de valor**: no hay capa analítica ni de mercado de ningún tipo.
- [A] **`DecodeVinValuesExtended` (flat) == `DecodeVinValues` (flat)** en claves: la "extensión" NCSA sólo aporta variables nuevas en la forma key-value (DecodeVin vs DecodeVinExtended), no en el flat (verificado: delta 0 claves). Matiz de implementación a tener en cuenta.

---

## 10. Fuentes (URLs)
- https://vpic.nhtsa.dot.gov/ — home: vPIC = Product Information Catalog and Vehicle Listing; NHTSA/DOT; tools (VIN Decoder, MID, Manufacturer Portal, API 25+, Downloads SQL/PostgreSQL, Modifiers DB); marco 49 CFR 551-595 (565/566/574/586); helpdesk.
- https://vpic.nhtsa.dot.gov/api/ — **doc de los 25+ endpoints** (DecodeVin/Values/Extended/Batch, WMI, Manufacturers, Makes, Models, Variables, Parts, EquipmentPlantCodes, CanadianVehicleSpecifications), tipos de fabricante/equipamiento, dimensiones canadienses; "populated using the 565 submittals"; rate control.
- https://vpic.nhtsa.dot.gov/api/home/index/faq — **gratis, sin registro/key, 24/7**; ~1000-2000 txn/min; off-peak; confianza 99% (1995+), 60-65% (1980-94), nada pre-1980; vehículos registrados para venta/import US; v4.06 (13-jun-2026).
- https://vpic.nhtsa.dot.gov/decoder/ — Decoder web: input VIN + Model Year; pre-1981 rechazado; sección Plant Information; link Canadian Vehicle Specifications + Manufacturer's Handbook.
- https://vpic.nhtsa.dot.gov/mid/ — MID v4.05 (16-may-2026): Organization, Part 565/566, Part 586 (Replica), Equipment Plants (tire/brake hose/retread/glazing, DOT codes), WMI; multi-criterio AND.
- https://vpic.nhtsa.dot.gov/mid/home/modifiersearch — Modifiers Identification Database (vehículos adaptados para discapacidad).
- https://vpic.nhtsa.dot.gov/mfrportal/ — Manufacturer Portal (submission 565/566 + tracking).
- https://vpic.nhtsa.dot.gov/Downloads — Standalone DB lite: `vPICList_lite_2026_06.bak.zip` (176 MB, SQL Server 2019+, `spVinDecode`), `.plain.zip` (72,3 MB) / `.custom.zip` (65,5 MB) PostgreSQL 17+; mensual.
- **API en vivo (consultada 2026-06-30):**
  - `GetVehicleVariableList?format=json` → **Count=144** variables (la lista atómica completa, con ID/GroupName/DataType).
  - `DecodeVinValues/5UXWX7C5*BA?modelyear=2011&format=json` → **154 claves** flat (BMW X3 xDrive35i, Munich/Germany, 300 hp, AWD…).
  - `DecodeVinValuesExtended/...` → mismas 154 claves (delta 0).
  - `GetVehicleVariableValuesList/vehicle%20type` → 9 tipos; `/error%20code` → 15 códigos.
  - `GetCanadianVehicleSpecifications/?year=2011&make=Acura` → campos OL/OW/OH/WB/CW/A-G/TWF/TWR/WD.
  - `GetAllMakes` → **12.278 makes**; `GetAllManufacturers` → paginado 100/pág (miles).
- https://data.transportation.gov/Automobiles/NHTSA-Product-Information-Catalog-and-Vehicle-List/j7xy-dt4s — dataset abierto vPIC VIN Decoder (mirror data.transportation.gov).
- https://catalog.data.gov/dataset/nhtsa-product-information-catalog-and-vehicle-listing-vpic-vehicle-api-json — mirror data.gov (Vehicle API JSON).
- https://learn.microsoft.com/en-us/connectors/nhtsavpicip/ — [3P] conector "NHTSA vPIC (Independent Publisher)" Power Platform (confirma endpoints + uso libre).
- https://en.wikipedia.org/wiki/National_Highway_Traffic_Safety_Administration — [3P] NHTSA establecida 1970 (Highway Safety Act), agencia del US DOT, HQ Washington DC.
- https://pypi.org/project/vpic-api/ y https://vpic.shaggytech.com/ — [3P] wrappers Python/JS (ecosistema; confirman endpoints y campos).
- https://vehicledatabases.com/api/nhtsa-vin-decoder — [3P] "NHTSA alternative": confirma gaps (sin pricing/valoración, trim débil, US-céntrico, sin SLA).

> Verificación: identidad y marco regulatorio contrastados con ≥2 fuentes (home vPIC + api FAQ + Wikipedia/NHTSA). **Esquema de campos [V] leído directamente de la API en vivo** (GetVehicleVariableList Count=144 + DecodeVinValues 154 claves reales). Precio/gratis [V] de api FAQ. Placement [V] de decoder/ + mid/ + estructura GroupName real. Gaps [V] por ausencia en API + confirmados por terceros. "official-data" = etiqueta de categoría del orquestador, no host DNS. Cadencia exacta de refresco de datos marcada [A] (no publicada; inferida del versionado mensual de la DB).
