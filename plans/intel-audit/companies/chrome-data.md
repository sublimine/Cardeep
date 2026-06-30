# Chrome Data (ChromeData) — Auditoría atómica de inteligencia competitiva

> Empresa de datos/descripción de automoción. Web: https://www.chromedata.com/ (redirige 302 a
> https://www.jdpower.com/business/automotive). Subdominio objetivo del encargo: `spec-catalog`.
> Auditoría para CARDEEP. Cada afirmación marcada [VERIFICADO] (leído en fuente) o [ASUMIDO].
> Fecha auditoría: 2026-06-30. Documentos primarios descargados y leídos (ver Fuentes).

---

## TL;DR para CARDEEP

ChromeData es la **capa de DESCRIPCIÓN / IDENTIFICACIÓN de vehículo** estándar de Norteamérica:
decodificación de VIN, catálogo de specs/equipamiento/opciones/colores, reglas de configuración y
precios as-configured, incentivos/financiación, imágenes y vídeo. **NO es una plataforma de
inteligencia de mercado de usado**: no ofrece days-to-sell, market days supply, price-to-market %,
índices de demanda/oferta ni curvas de depreciación como producto propio (eso vive en sus hermanos
J.D. Power Valuation Services / ALG / NADA, o en competidores tipo vAuto/Cox). Cobertura **solo
EE. UU. + Canadá**. Su patrón de PLACEMENT (qué dato va dónde) es muy explotable por CARDEEP:
rankings de relevancia de features para ordenar la VDP, benefit/definition statements como
tooltips educativos, galería multi-ángulo + color-match en SRP/VDP, e incentivos disparados por
VIN+código postal.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca de producto | **ChromeData** (estilizado "ChromeData", histórico "Chrome Data") | [VERIFICADO] |
| Entidad legal actual | **Autodata, Inc. dba ChromeData** (división Autodata Solutions de J.D. Power) | [VERIFICADO] (doc legal Product Information 05/2025, cláusula de apertura) |
| Entidad legal histórica | **Chrome Data Solutions, LP** (presentaciones SEC) | [VERIFICADO] |
| Propietario / grupo | **J.D. Power** (la marca opera como "ChromeData, part of J.D. Power" / "Autodata Solutions Division of JD Power") | [VERIFICADO] (LinkedIn, páginas de producto, bios de equipo) |
| Matriz de capital (PE) | **Thoma Bravo** (firma de private equity) | [VERIFICADO] |
| HQ del grupo combinado | **Troy, Michigan, EE. UU.** | [VERIFICADO] (anuncio de fusión) |
| Operaciones de contenido ChromeData | **Portland, Oregon** (soporte en horario Pacific Time) y **London, Ontario, Canadá** | [VERIFICADO] (guía de integración: soporte 6am–5pm PT; bios; lanzamiento 2011) |
| Trayectoria en datos descriptivos | "más de 25-30 años" (Chrome Systems → Chrome Data) | [VERIFICADO] (web: "industry standard for nearly three decades"; "over 25 years") |

### Línea temporal corporativa [VERIFICADO]
- **1990** — Se funda Autodata Solutions (London, Ontario).
- **~1986-1990s** — Chrome Systems Inc. provee datos descriptivos de vehículo (VIN decode para eBay Motors, etc.). 25-30 años de historia de "vehicle descriptive data".
- **2011** — **Chrome Data Solutions, LP** se lanza como *joint venture* de **DealerTrack** + **Autodata Solutions** (Autodata era subsidiaria de Internet Brands). [VERIFICADO] (Auto Remarketing: "DealerTrack & Autodata Solutions Launch Chrome Data Solutions").
- **Mayo 2019** — **Thoma Bravo** completa la adquisición de Autodata Solutions Group.
- **16 diciembre 2019** — **J.D. Power se fusiona con Autodata Solutions** (cierre de la compra de J.D. Power por Thoma Bravo). La compañía combinada opera como **J.D. Power**, HQ en Troy, MI. Las "Chrome-branded solutions" (rebates/incentives, VIN decode & describe, configuración y comparación) pasan a J.D. Power. [VERIFICADO] (Thoma Bravo, J.D. Power, Business Wire, Auto Remarketing).
- **Adquisición de EpiAnalytics** — empresa de IA/NLP de data-engineering de VIN; "now part of J.D. Power"; potencia los "Engineered VIN Data" y VINoptions. [VERIFICADO] (CVD Profile doc + bios).

### Categorías de negocio
Datos descriptivos de vehículo · Decodificación de VIN · Catálogo de especificaciones/equipamiento ·
Reglas de configuración y pricing · Incentivos y financiación (Lender Desk) · Imágenes y vídeo de
vehículo · Contenido editorial · Tablas de mapeo (interoperabilidad de IDs) · Gestión y sindicación
de inventario · Valoración as-built (con socios de guía). [VERIFICADO]

### Clientes objetivo [VERIFICADO] (definiciones del doc legal + casos de uso de la web)
OEMs · Concesionarios (franquiciados e independientes de usado) · Dealer Tech Providers · Sitios de
consumidor / marketplaces · Subastas (Auctions) · Finance / Lenders · Insurance (suscripción,
siniestros, total loss) · Fleet (gestión y pedido de flotas) · Aftermarket (recambio, cristal/ADAS,
asistencia en carretera, reciclaje/desguace) · Remarketing. Canal directo OEM y canal "non-OEM
partner/reseller".

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Países | **EE. UU. y Canadá** (Norteamérica). El catálogo VIN/descripción NO cubre Europa/España/LatAm/Asia. (J.D. Power tiene sitios regionales Canada/China/Europe/Japan/Mexico, pero el catálogo ChromeData es NA). | [VERIFICADO] |
| Tipos de vehículo | Coches y light trucks **hasta serie 3500** ("up to and including 3500 series"). Comerciales medianos/pesados solo vía configuradores de pedido (Vehicle Spec & Ordering). Exóticos y comerciales excluidos en varios productos de imagen. | [VERIFICADO] |
| Nuevo / Usado | **Ambos.** Datos de vehículo NUEVO (catálogo, specs, pricing) + decodificación de VIN de USADO (1992+). Valores de usado (auction/trade-in/loan/retail) vía As-Built Valuation Service. | [VERIFICADO] |
| Rango de años (ADS) | **1981 → Current Model Year** (Automotive Description Service) | [VERIFICADO] |
| Rango de años (VIN Descriptions) | **1992+ EE. UU.**, **1996+ Canadá** | [VERIFICADO] |
| Rango de años (Vehicle Selector Service) | **1997 → CMY** | [VERIFICADO] |
| Imágenes | Galleries 2010+; Stock Image Library 2001+; Still & Colorized 2003+; Historic Multi-View 2001-2009 | [VERIFICADO] |
| "Current Model Year" (CMY) | = año en curso **+ 2 años previos** | [VERIFICADO] |
| Escala | **100%** de los vehículos en venta hoy cubiertos por datos VIN de ChromeData; **20.000** build manifests nuevos/día desde plantas OEM; **12.000 millones (12B)** de llamadas/año a los servicios ChromeData combinados | [VERIFICADO] (página Vehicle Specs & Descriptions) |

---

## 3. Productos + campos atómicos

> El subdominio del encargo, `spec-catalog`, corresponde a la familia **"Vehicle Specs &
> Descriptions Services"** (el "catálogo de especificaciones"): Automotive Description Service +
> Vehicle Selector Service (vista "catalog view" de StyleDetails) + el catálogo de datos que
> alimenta toda la suite. NOTA: `spec-catalog.chromedata.com` **no resuelve por DNS** a fecha de
> auditoría (`ENOTFOUND`); muy probablemente retirado/migrado tras la integración en J.D. Power.
> [VERIFICADO] (fallo DNS reproducido).

### 3.1. ChromeData VIN Descriptions (CVD) — producto estrella
RESTful API. Endpoints: `GET /vindescription` y `PUT /vindescription` (PUT permite estrechar a
estilos concretos con atributos extra). También **batch processing**. Tres tiers:
- **Standard** — datos núcleo de catálogo (básico).
- **Premium** — registros verificados de catálogo + **Engineered VIN Data** (EpiAnalytics) cuando hay.
- **Premium+** — verificado contra **OEM Build Data** (máxima precisión, "1-to-1 trim match").

**Campos de respuesta (atómicos, notación por niveles del Integration Guide oct-2024):** [VERIFICADO]

Meta / estado:
`message`, `error`, `executionTimeMS`, `copyright`, `result`, `vinSubmitted`, `vinProcessed`,
`validVin`, `source` (B=Build / V=Verified / E=Engineered / C=Catalog / S=Sparse), `httpStatusCode`,
`validationErrorMessage`, `language`.

Cabecera de vehículo:
`year`, `make`, `model`, `modelID` (Chrome YMMID), `buildMSRP`, `estimatedMSRP`, `buildDate`,
`wmiCountry`, `wmiManufacturer`, `buildSource`.

Objeto `vehicles` (estilo):
`styleId` (Chrome StyleId), `styleDescription`, `trim`, `baseMSRP`, `destinationCharge`,
`driveType`, `bodyType`, `standardCurbWeight`, `standardPayload`, `standardTowingCapacity`,
`country`, `standardGVWR`, `mfrModelCode` (MMC), `doors`, `boxStyle`, `segment` (array),
`wheelbase`, `baseInvoice`, `modelDesignChangeDetails.designChange`,
`modelDesignChangeDetails.designChangeReason`.

`exteriorColors`:
`genericDesc`, `description` (desc. del fabricante), `colorCode`, `installCause`, `styles`,
`rgbValue`, `rgbHexValue`, `type` (1=body / 2=rooftop / 3=stripe), `primary`.

`interiorColors`:
`genericDesc`, `colorCode`, `description`, `installCause`, `styles`.

`features` (equipamiento/feature):
`id`, `key`, `sectionId`, `subSectionId`, `sectionName`, `name` (branded), `nameNoBrand`,
`description`, `rankingValue` (relevancia asignada por expertos), `featureKeyAnswers`,
`styles.styleIds`, `styles.installCause`, `styles.isStandard`, `isHybridFeature`, `isEVFeature`,
`benefitStatement.title`, `benefitStatement.definition`, `benefitStatement.statement`,
`adsCategoryIds`, `adsCategoryIdDescriptions`, `adsTypeIds`, `adsTypeIdDescriptions`.

`techSpecs` (especificaciones técnicas):
mismos campos que features + `unitsOfMeasureAndValues.unitOfMeasure`,
`unitsOfMeasureAndValues.Value`.

`packages` (paquetes):
`id`, `key`, `sectionId`, `subSectionId`, `sectionName`, `name`, `nameNoBrand`, `description`,
`rankingValue`, `styles.*`, `benefitStatement.*`, y `optionDetails`: `featureKeys`, `optionCode`,
`altOptionCode`, `group`, `isChromeCode`, `collectionCode`, `msrp`, `invoice`, `content` (array de
option codes contenidos), + `adsCategoryIds/...`.

`safetyInfo`: `source` (p.ej. NHTSA Crash Data), `value` (p.ej. "5 Star"), `description`, `note`,
`condition` (p.ej. Female), `styles`.

`recallInfo`: `recallId`, `campaignNo`, `mfgCampaignNo`, `component`, `recallType` (V=Vehicle /
T=Tire / E=Equipment), `reportedDate`, `styles`, `summaryDescription`, `consequenceDescription`,
`correctiveDescription`.

`optionCodes` (array de códigos instalados) · `optionCodeContent`: `featureKeys`, `optionCode`,
`altOptionCode`, `group`, `isChromeCode`, `collectionCode`, `isStandard`, `msrp`, `invoice`,
`optionDescription`, `installCause`.

`additionalBuildData`: `label`, `description`, `value`, `msrp`, `invoice`.

Enumeraciones de soporte:
- `group` de opción: Additional Options, Suspension, Exterior, Emissions, Engine, Entertainment,
  Fuel, Interior, Mechanical, Paint, Safety, Seating, Tires & Wheels, Trailering, Transmission,
  Warranty.
- `installCause`: B=Build, E=Engineered/Verified, V=VIN Pattern, R=Standard but changeable,
  S=Standard, I=User Input, A=Available.
- Segmentación: **EPA** (default) y **Marketing** (single o multi-segment): Sedan, Coupe,
  Convertible, SUV, Crossover, Van, Minivan, Pickup, Wagon, Hatchback, Chassis, etc.
- `Fuel Type` (Feature ID 10030): Regular Unleaded, Premium Unleaded, Diesel, Natural Gas, Propane,
  Gaseous, Electric, Ethanol, Methanol, Flex Fuel, Gas/CNG, Gas/Propane.
- `Drive Type` (Feature ID 10750): FWD, RWD, 4WD, AWD (+ 6x4/6x6/8x6/8x8/4x2/4x4 en vehicle object).
- Garantías (Feature IDs): Basic, Powertrain, Corrosion perforation, Roadside, Maintenance,
  Hybrid/electric components, Traction battery, Transmission warranty.

**Vehicle Details Report / "ChromeData Vehicle Report" (nuevo):** PDF formateado generado desde el
VIN y los `rankingValue` de CVD; contiene year/make/model/trim, key features, dealer info, pricing,
options y packages. Sales-aid descargable. [VERIFICADO]

### 3.2. Automotive Description Service (ADS) — catálogo "spec-catalog" SOAP
Web service SOAP/WSDL. Operaciones: `describeVehicle`, `getStyle`, `getConfigurationByStyleID`,
`getStyleFullyConfigured`, `getStyleFullyConfiguredByStyleID`, `compareAdvantages`,
`compareSideBySide`. Selectores Year/Make/Model/Style. Recupera por VIN / Chrome Style ID /
Chrome ACode. Tiers: **ADS-Full** y **ADS-Basic** (solo VIN). Años 1981→CMY. [VERIFICADO] (WSDL + doc legal)

**Campos atómicos del schema (XSD del WSDL):** [VERIFICADO]
- `AccountInfo`: number, secret, country, language, behalfOf.
- `vinDescription`: vin, modelYear, division, modelName, styleName, bodyType, drivingWheels, built,
  gvwr, WorldManufacturerIdentifier, ManufacturerIdentificationCode, restraintTypes, marketClass.
- `Style`: id, modelYear, name, nameWoTrim, trim, mfrModelCode, fleetOnly, modelFleet, passDoors,
  altModelName, altStyleName, altBodyType, drivetrain, division, subdivision, model, basePrice,
  bodyType(primary), marketClass, stockImage(filename), mediaGallery.
- `Price`: msrp, invoice, destination, unknown. `PriceRange`/`Range`: low, high.
- `Engine`: engineType, fuelType, horsepower(value/rpm), netTorque(value/rpm), cylinders,
  displacement(liters/cubicIn), fuelEconomy(city/hwy + unit), fuelCapacity(unit), forcedInduction,
  highOutput, installed.
- `DriveTrain` enum: Front/Rear/All/Four Wheel Drive.
- `Standard` (equip. estándar): header, description, category, styleId, installed.
- `Option` (opciones de fábrica): header, description, category, price(OptionPrice:
  invoiceMin/invoiceMax/msrpMin/msrpMax), chromeCode, oemCode, altOptionCode, standard,
  optionKindId, utf, fleetOnly, ambiguousOption, styleId, installed.
- `GenericEquipment`: categoryId/definition, styleId, installed.
- `Color`: colorCode, colorName, rgbValue, genericColor(name/primary), styleId, installed.
- `ConsumerInformation`: type, item(name/conditionNote/value), styleId.
- `TechnicalSpecification`: titleId/definition(group/header/title/measurementUnit), range(min/max),
  value(value/condition/styleId).
- `MediaGallery`: view(Image: shotCode, backgroundDescription), colorized(Image:
  primaryColorOptionCode, secondaryColorOptionCode, match, shotCode, backgroundDescription,
  primaryRGBHexCode, secondaryRGBHexCode), styleId. `Image`: url, width, height.
- Navegación: ModelYears, Divisions, Subdivisions, Models, Styles (IdentifiedString con id).
- `Switch` (modificadores): ShowExtendedDescriptions, ShowAvailableEquipment,
  ShowConsumerInformation, ShowExtendedTechnicalSpecifications, IncludeRegionalVehicles,
  UseDependencyOrderingLogic, IncludeDefinitions, DisableSafeStandards.

### 3.3. ChromeData Vehicle Selector Service (VSS) — vista de catálogo sin VIN
RESTful. Endpoints: `Years`, `Makes`, `Models`, `Styles`, `getStyleDetails` (devuelve un "catalog
view" de un styleId+locale). Compañero de CVD para cuando NO hay VIN (research por Y/M/M). Años
1997→CMY. [VERIFICADO]
**Campos StyleDetails:** styleId, styleDescription, trim, baseMSRP, destinationCharge, driveType,
bodyType, doors, boxStyle, wheelbase, baseInvoice, designChangeReason, features (id/key/name/
nameNoBrand/description/rankingValue/styleIds/...), techSpecs, options, packages con
`msrpMin`/`msrpMax`/`invoiceMin`/`invoiceMax`. (mismo modelo de datos que CVD). [VERIFICADO]

### 3.4. Feature Exchange
Web service (VIN / Chrome Style ID) para features VIN-específicas; orientado a **glass replacement,
calibración ADAS, asistencia en carretera, tiendas de recambio**. Componente "Simple Model Walk":
selectores Y/M/M + `vinPatterns` por styleId + modelYearId. Años 1981→CMY. [VERIFICADO]

### 3.5. Chrome Construct + Carbook Pro + AutoPlanner (configuración/pricing)
- **Chrome Construct** — web service para comparar, configurar y precificar (10 años previos→CMY).
  Componentes: **Enhanced Pricing** (cálculos de precio OEM-específicos distintos de invoice/MSRP),
  **Canadian Invoice Pricing**.
- **Carbook Pro** — app web de research/config/compare/pricing (CMY).
- **AutoPlanner** — app web de pricing para product planners / marketing (tendencias de mercado,
  comparación competitiva de nuevos).
- **Configurator Engine / Comparator Engine / Criteria Search Engine** — engines Java server-side +
  Configuration Data / Comparison Data / Criteria Search Engine Data.
- **Build and Quote** — herramienta de configurar-y-cotizar. [VERIFICADO]

### 3.6. Chrome Incentives Service
Servicio de incentivos OEM regionales. **Campos:** cash incentives, finance incentives, lease
incentives, special programs; current retail, consumer cash, dealer cash incentives, retail
incentives, sub-vented APR programs, residuals, money factors, payment waivers, giveaways.
Incentivos regionales filtrados por **Zip Code / código postal**. [VERIFICADO]

### 3.7. ChromeData Lender Desk (+ Payment Services / Mirror / TT&L / EV)
Web service de programas de financiación. Tiers Base / Standard / Premium. **Campos:** programas
lease/loan/cash de lenders OEM captive + non-captive (nacional y regional) para nuevo, **certified
pre-owned** y usado; dealer cash incentives; sub-vented APR; **residuals**; **money factors**;
payment waivers; giveaways; lender guidelines; fees; **credit tiers**; terms; bulk quoting API
(retail digital). Add-ons:
- **EV Basic** (BEV/PHEV nuevos) y **EV Standard** (BEV/PHEV/FCEV nuevo y usado) con **rebates e
  incentivos federales, estatales y de utility**.
- **Lender Desk TT&L** — taxes & fees federales/estatales/county/city para registro y titulación.
- **Payment Services** — quoting end-to-end: consolida inventario, aplica reglas de pricing del
  dealer, incentivos OEM y devuelve **payment quotes** (loan/lease) por credit tier y term.
- **Lender Desk Mirror** — feed de datos (retención máx. 30 días). [VERIFICADO]

### 3.8. As-Built Valuation Service / VIN Precision+ (capa de valor)
Devuelve **valores retail y wholesale para cualquier VIN**; valoración line-item de todas las
opciones y **add/deducts**, o un único valor calculado por vehículo. Socios de guía: **Black Book**
y **Galves** + **J.D. Power Valuation Services**. VIN Precision+ combina valores J.D. Power + as-built
ChromeData. **Campos:** retail value, wholesale value, trade-in value, loan value, auction value,
historical values, line-item option add/deducts. [VERIFICADO] (snippet de búsqueda + página JDP)
> Matiz: técnicamente es un servicio "puente" entre ChromeData (specs/as-built) y la valoración de
> J.D. Power; lo incluyo porque es donde ChromeData toca "valor de mercado".

### 3.9. StudyPrice (riesgo / seguros)
RESTful. Devuelve info de vehículo para **quoting, rating y underwriting** de seguro. Foco en
features que previenen frecuencia/severidad de siniestro: **passive safety features, active safety
features, theft-prevention features** + atributos descriptivos. [VERIFICADO]

### 3.10. Imágenes y vídeo
- **Chrome Image Gallery** — Basic Multi-View (3 ext + 1 int), Expanded Multi-View (hasta 21
  ángulos int/ext), Historic Expanded Multi-View (2001-2009), Basic Color-Matched (1 imagen
  colorizada), Expanded Color-Matched (3 ángulos colorizados). 2010+.
- **Stock Image Library** — ~7 int + 7 ext press-kit + front colorizado + valores RGB de paletas. 2001+.
- **Still and Colorized Image Gallery** — ~15-17 stills/modelo + 1 front colorizado por color OEM. 2003+.
- **Stock Images** — 1 imagen a nivel modelo/body-style. 1997+ US / 2000+ CA.
- **Image on the Fly (IOF)** — utility server para acceder a las galerías.
- **ChromeData Ideal Inventory Images** — IA que aplica sombreado/tintado de ventanas/pintura y
  coloca el coche sobre un fondo elegido (normalización de fotos de inventario).
- **Model Test Drive Videos-Pro** — vídeos por modelo (2008+), con intro/outro de dealer, CTA, closed
  captioning. **VIN Test Drive Videos-Pro** — vídeo por VIN con imágenes reales del VIN. [VERIFICADO]

### 3.11. Contenido editorial
**AutoBrief Reviews** (descripciones a nivel modelo, 2007+), **New Car Test Drive Reviews** (reseñas
editoriales de tercero, 2000+), **Awards and Accolades** (premios de la industria US, 2007+),
**Runtime Vocabulary Engine** (RVE: traduce automáticamente descripciones de features a
descripciones alternativas), **Spanish Translation** / **French Translation** del Core Data (2004+). [VERIFICADO]

### 3.12. ChromeData Certified Inventory (gestión + sindicación de inventario)
Plataforma de inventory management que ingiere el feed del dealer, normaliza y consolida.
Tiers: Base Plus (decode sin Build Data), Enhanced / Extended Syndication (decode + Build Data +
Engineered VIN Data, identificación de features as-configured), Command Center (control de pricing
nuevo/usado, comment builder, upload de imágenes/vídeo del dealer), Dealer Direct / Standalone
Distribution (lista el inventario en **JDPower.com, MSN Autos y Google My Business**). [VERIFICADO]

### 3.13. Productos de identificación / VIN / datasets
- **VINMatch** — make/model/style/equipment por VIN (1981+); **sin valores**.
- **VINoptions** — NLP que categoriza features/opciones no estructuradas y las anexa al VIN (flat
  file o browser).
- **Squish VIN Table** — tabla de decode por posiciones 1-8,10,11 del VIN.
- **QuickData / New Vehicle Data (+ Archives) / Fleet New Vehicle Data (+ Archives) / PreRelease NVD
  / StyleMap Data / Core Data / Comparison Data / Configuration Data / Zip to Styles Data**.
- **Flat File Schema A** — flat files de VIN, stock images, mapping ACode→StyleID, vehicle options. [VERIFICADO]

### 3.14. Tablas de mapeo (interoperabilidad — activo estratégico)
ACES Mapping Table (Chrome Style ID ↔ AAIA ACES Vehicle ID, 1981+), Black Book Mapping Table
(1999+), Kelley Blue Book Mapping Table (Style ID/ACode ↔ KBB Car ID), **J.D. Power Valuation
Services Mapping Table** (Style ID ↔ JDP Vehicle ID, 1998+), Chrome ACode Mapping Table, Canadian
Chrome ACode↔Style ID, U.S. ACode↔U.S. Style ID, U.S.↔Canadian ACode, Autodata Mapping Table
(Acode↔Style ID, exact/inexact fit). [VERIFICADO]

### 3.15. Fleet Spec & Ordering / Vehicle Spec & Ordering / Custom Software
Configuradores de pedido para flotas y comerciales (incl. light/medium/heavy commercial). Custom
Software Solutions para OEM: ordering, vehicle allocation, incentive authoring, data engineering. [VERIFICADO]

---

## 4. Metodología y fuentes de datos

- **Catálogo propietario ChromeData de 30+ años**, normalizado **cross-OEM** (vocabulario común que
  hace comparable feature-a-feature entre fabricantes). [VERIFICADO]
- **OEM Build Data** (datos "as-built" de planta): partnerships verificados con **BMW, GM, Ford,
  Toyota, Hyundai, Kia, Mazda, Nissan/Infiniti (NNA), Stellantis, Subaru, Volvo**. **20.000 build
  manifests/día** desde plantas OEM. [VERIFICADO]
- **Engineered VIN Data** (**EpiAnalytics**, IA/NLP, ahora parte de J.D. Power): rellena huecos donde
  falta Build Data; depura registros, cruza catálogo + ordering rules, extrae features/color. [VERIFICADO]
- **Reglas de configuración/ordering** (option logic, combinaciones permitidas, as-configured price). [VERIFICADO]
- **Jerarquía de procedencia por atributo** (`source`/`installCause`): Build (B) > Verified/Engineered
  (V/E) > Catalog (C) > Sparse (S) — transparencia del origen de cada dato. [VERIFICADO]
- **Rankings de relevancia** asignados por **expertos de automoción** (rankingValue). [VERIFICADO]
- **Socios de valoración**: Black Book, Galves, J.D. Power Valuation Services / ALG / NADA. [VERIFICADO]
- Validación: "100% de los vehículos en venta cubiertos"; 12B llamadas/año. [VERIFICADO]

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| RESTful API | CVD (GET/PUT /vindescription), VSS, Lender Desk, StudyPrice, incentives, mapping. Swagger en el Developer Portal de J.D. Power/Autodata. | [VERIFICADO] |
| SOAP / WSDL | Automotive Description Service (describeVehicle, getStyle, getStyleFullyConfigured, compareSideBySide...). | [VERIFICADO] |
| Batch processing | CVD batch. | [VERIFICADO] |
| Flat files | Flat File Schema A (VIN, stock images, mapping, options). | [VERIFICADO] |
| Distributed database / DaaS | "data-as-a-service or distributed databases". | [VERIFICADO] |
| DTP / Data Distribution Service | utilities de transferencia de updates (pull vía internet). | [VERIFICADO] |
| Apps web | Carbook Pro, AutoPlanner, Chrome Construct, configuradores. | [VERIFICADO] |
| PDF | Vehicle Details Report / ChromeData Vehicle Report. | [VERIFICADO] |
| Imagen on-the-fly | Image on the Fly (IOF). | [VERIFICADO] |
| Mobile app | scan/decode VIN, window sticker, descarga de contenido, selección en subasta. | [VERIFICADO] |
| Sindicación inventario | a JDPower.com, MSN Autos, Google My Business. | [VERIFICADO] |
| Seguridad | Shared Secret Security Protocol (token en header Authorization); AccountInfo (number/secret); profile keys; ISO 27001/27002 para Build Data. | [VERIFICADO] |
| Soporte | tel. (800) 937-3661 / support@chromedata.com, L-V 6am-5pm PT. | [VERIFICADO] |

---

## 6. Precio (modelo)

- **No público.** Enterprise / quote-based ("Contact Us", "Book your free demo"). No hay tarifas
  absolutas descubribles. [VERIFICADO]
- **Facturación por transacción**: cada "successfully completed call" (describeVehicle, getStyle,
  getConfigurationByStyleID, RESTful de mapping/descriptions/incentives, imagen, incentivos) cuenta
  como Transaction. Llamadas inválidas (VIN/StyleID/ACode/geo fuera de scope) no facturan. [VERIFICADO]
- **Tarifas diferenciadas por Build Data**: usar perfiles con Build Data incurre tasas de transacción
  más altas; los **profile keys** seleccionan catálogo vs Build Data. [VERIFICADO]
- **Tiers de licencia** (Standard/Premium/Premium+; Lender Desk Base/Standard/Premium; Image
  Basic/Expanded/Historic) → distintos price points. [VERIFICADO]
- Modelo de "Licensed Works" por **Order**; algunas métricas se facturan por Unique Visitor /
  Location / Dealer según el Order. [VERIFICADO]

---

## 7. PLACEMENT — dónde colocan cada dato (patrón a copiar por CARDEEP)

> Esto es lo más accionable para CARDEEP: ChromeData no solo da el dato, define el patrón de UI.

| Dato / métrica | Dónde se coloca (sección/pantalla) | Estado |
|---|---|---|
| `rankingValue` de features/techSpecs/packages | **Vehicle Details Page (VDP)**: ordena y prioriza los features clave por relevancia ("display relevancy of key features on vehicle details pages for shopper convenience"). | [VERIFICADO] |
| `benefitStatement` (title/definition/statement) | VDP: **tooltips / texto expandible** que "educa al shopper" sobre cada feature. | [VERIFICADO] |
| Descripciones branded vs `nameNoBrand` | VDP / comparador: branded para merchandising, no-brand para comparación cross-OEM. | [VERIFICADO] |
| Vehicle Details Report (PDF) | **Punto de venta / descarga en VDP**: sales-aid con year/make/model/trim, key features, dealer info, pricing, options, packages. | [VERIFICADO] |
| Stock / colorized / multi-view images | **SRP** (thumbnail), **VDP** (galería hasta 21 ángulos), color-match al color exterior elegido. | [VERIFICADO] |
| Model Test Drive Videos | **Model research pages, SRP y VDP**. | [VERIFICADO] |
| VIN Test Drive Videos | **VDP del VIN** (listing concreto). | [VERIFICADO] |
| Incentivos regionales | Se muestran **tras introducir vehículo + Zip/código postal**; solo los incentivos de ese Zip para ese vehículo → **VDP / calculadora de pago**. | [VERIFICADO] |
| Lender Desk payment quotes | **Herramientas de digital retailing / payment / desking**; pago estático en listings (SRP/VDP). | [VERIFICADO] |
| Configuración / as-configured price | **Configurador "Build & Quote"** (selección de opciones, combinaciones permitidas, precio total). | [VERIFICADO] |
| Comparación lado a lado | **Comparador** (compareSideBySide / compareAdvantages). | [VERIFICADO] |
| Inventario normalizado | **SRP listings**, sindicado a JDPower.com / MSN Autos / Google My Business. | [VERIFICADO] |
| Window sticker / specs | **Mobile app** (scan VIN). | [VERIFICADO] |
| Safety/ADAS features | back-office de **reparación/calibración ADAS**, suscripción de seguro (StudyPrice). | [VERIFICADO] |
| As-Built valuation (retail/wholesale + add/deducts) | **Herramientas de tasación/trade-in, colateral de lender, total-loss**: valor por VIN con add/deducts line-item. | [VERIFICADO] |
| Awards & Accolades / reviews editoriales | **Model research pages / VDP** (refuerzo de merchandising). | [ASUMIDO] (uso típico; el doc define el contenido pero no fija pantalla) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Descripción VIN más profunda y precisa de Norteamérica**, validada contra **OEM Build Data**
   real (11 OEMs con partnership as-built) + 20k manifests/día. "1-to-1 trim match". [VERIFICADO]
2. **Chrome Style ID / Chrome ACode = estándares de facto** de la industria, con tablas de mapeo a
   ACES, Black Book, KBB, J.D. Power → **backbone de interoperabilidad** entre proveedores. [VERIFICADO]
3. **Capa de contenido de merchandising**, no solo datos crudos: rankings de relevancia, benefit/
   definition statements, descripciones branded/no-branded, normalización cross-OEM. [VERIFICADO]
4. **Reglas de configuración/ordering + pricing as-configured** (configurador completo, option logic). [VERIFICADO]
5. **Transparencia de procedencia por atributo** (source/installCause B/V/E/C/S/I). [VERIFICADO]
6. **Engineered VIN Data por IA/NLP (EpiAnalytics)** que rellena huecos donde falta Build Data. [VERIFICADO]
7. **Suite multimedia completa**: galería 21 ángulos, color-match, IA Ideal Inventory Images, vídeos
   model/VIN. [VERIFICADO]
8. **Historia 1981+** y escala (100% de vehículos en venta; 12B llamadas/año). [VERIFICADO]
9. Sinergia J.D. Power: incentivos, valoración (ALG/NADA), ratings/awards, datos de seguro. [VERIFICADO]

---

## 9. Gaps (lo que NO ofrece) — crítico para posicionar CARDEEP

1. **Solo EE. UU. + Canadá.** Cero cobertura Europa/**España**/LatAm/Asia en el catálogo ChromeData.
   (gap principal frente a CARDEEP). [VERIFICADO]
2. **No es inteligencia de mercado de usado.** NO ofrece **days-to-sell, market days supply,
   price-to-market %, índice de demanda/oferta, inventory turn, competitividad de precio regional**.
   Esas métricas viven en hermanos J.D. Power (Valuation Services, ALG) o en competidores
   (vAuto/Cox, CarGurus). ChromeData = descripción/identificación/incentivos/config/imagen. [VERIFICADO — por ausencia en toda la doc de producto]
3. **Curva de depreciación / residual forecast** no es producto propio de ChromeData; residuals solo
   como input de programas lease/finance (money factors, lease residuals) y vía ALG (separado). [VERIFICADO]
4. **Ajuste por kilometraje / valoración por odómetro**: pertenece a la capa de valor (As-Built
   Valuation / JDP Values), no al core ChromeData. [VERIFICADO]
5. **Historial de siniestros / título / propietarios**: NO lo provee (eso es Carfax/AutoCheck/
   Experian). Sí provee **recall info (NHTSA)** y safety ratings. [VERIFICADO]
6. **Sin censo de huella digital / descubrimiento de listings online / agregación de puntos de
   venta** (el core de CARDEEP). ChromeData describe el vehículo, no rastrea dónde se vende online. [VERIFICADO]
7. **Valoración consumer-facing (estilo KBB/Edmunds)**: vía JDPower.com/NADA, no por API ChromeData. [VERIFICADO]
8. **Precio no transparente** (solo enterprise/quote). [VERIFICADO]
9. **Inventario de mercado en tiempo real** limitado a lo que los dealers alimentan en Certified
   Inventory; no hay scan competitivo del mercado. [VERIFICADO]

---

## 10. Fuentes (URLs)

Documentos primarios (descargados y leídos):
- ChromeData Product Information 05/2025 (doc legal/definiciones de producto): https://www.jdpower.com/sites/default/files/file/2025-05/ChromeData%20Product%20Information_2025-05.pdf
- ChromeData Product Information 05/2023 (corroboración): https://www.jdpower.com/sites/default/files/file/2023-05/ChromeData%20Product%20Information_2023_05_03_1.pdf
- ChromeData VIN Descriptions Integration Guide (oct-2024, campos de respuesta): https://f-portal-tyk-stg.api.chromedata.com/wp-content/uploads/2024/10/CVD-Integration-Guide_2024_October.pdf
- ChromeData VIN Description Profiles (tiers Standard/Premium/Premium+): https://f-portal-tyk-stg.api.chromedata.com/wp-content/uploads/2024/04/CVDProfileDocument1.pdf
- ChromeData Vehicle Selector Service Integration Guide (StyleDetails / catalog view / segmentación): https://portal.jdpower.com/wp-content/uploads/2024/04/VSSIntegrationGuide_2025_October28.pdf
- Automotive Description Service WSDL (schema XSD completo): https://github.com/hooklift/gowsdl/blob/master/fixtures/chromedata.wsdl

Páginas de producto (J.D. Power / ChromeData):
- Vehicle Specs & Descriptions Services (familia "spec-catalog", KPIs 100%/20k/12B): https://www.jdpower.com/business/vehicle-specs-and-description-services
- ChromeData VIN Descriptions (tiers, casos de uso, placement): https://www.jdpower.com/business/chromedata-vin-descriptions
- Features, Price & Specs (datos del catálogo): https://www.jdpower.com/business/features-price-specs
- As-Built Valuation Service: https://www.jdpower.com/business/built-valuation-service
- StudyPrice (riesgo/seguros): https://portal-stg.chromedata.com/marketing-info/studyprice/
- Automotive hub: https://www.jdpower.com/business/automotive  (redirección desde https://www.chromedata.com/)
- Edmunds API "Car Style Details by Chrome Data ID" (uso de Chrome Style ID por partner): https://edmundsapi-preprod.github.io/api-documentation/vehicle/spec_style/v2/03_chrome/api-description

Identidad / corporativo:
- Thoma Bravo — J.D. Power to Merge with Autodata Solutions (16-dic-2019): https://www.thomabravo.com/press-releases/j.d.-power-to-merge-with-autodata-solutions-creating-a-leading-source-of-automotive-data-analytics-and-software-solutions
- J.D. Power — Autodata Solutions Group Merger Announcement: https://www.jdpower.com/business/press-releases/jd-power-autodata-solutions-group-merger-announcement
- Business Wire — fusión J.D. Power / Autodata: https://www.businesswire.com/news/home/20191216005199/en/J.D.-Power-Merge-Autodata-Solutions-Creating-Leading
- Auto Remarketing — DealerTrack & Autodata Solutions Launch Chrome Data Solutions (2011): https://www.autoremarketing.com/ar/dealertrack-autodata-solutions-launch-chrome-data-solutions/
- LinkedIn — "ChromeData, Part of J.D. Power": https://www.linkedin.com/company/chrome-data-solutions
- PRNewswire — Chrome Systems VIN data para eBay Motors (historia): https://www.prnewswire.com/news-releases/chrome-systems-provides-vin-data-and-decoding-solutions-to-ebay-motors-120614629.html

Notas de verificación:
- `spec-catalog.chromedata.com` NO resuelve por DNS (ENOTFOUND) a 2026-06-30 → subdominio retirado/migrado. [VERIFICADO]
- `chromedata.com` y `chromedata.com/data-products/` hacen 302 → jdpower.com/business/automotive. [VERIFICADO]
- Páginas HTML de jdpower.com devuelven 403 al fetcher genérico pero 200 con User-Agent de navegador (curl). PDFs accesibles directamente.
