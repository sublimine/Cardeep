# DVLA — Auditoría atómica

> **slug:** `dvla` · **subdominio de audit:** `official-data` · **web:** https://developer-portal.driver-vehicle-licensing.api.gov.uk/
> · **catálogo gov:** https://www.api.gov.uk/dvla/ · **UI pública:** https://vehicleenquiry.service.gov.uk/ · **MOT (DVSA):** https://documentation.history.mot.api.gov.uk/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[NV]` = no verificado; nada inventado.
> **Veredicto express:** DVLA **no es un valuador ni una empresa de inteligencia de mercado**. Es la **FUENTE OFICIAL Y AUTORITATIVA**
> del registro de vehículos y conductores del Reino Unido — el **dato de verdad (ground truth)** del que beben *todos* los demás auditados
> (cap hpi, HPI Check, Percayso, Auto Trader, Experian, los resellers `ukvehicledata.co.uk`/`vehicledataglobal.com`...). Agencia ejecutiva del
> **Department for Transport**, sede en **Swansea**, **50M+ registros de conductor / 40M+ de vehículo**. Su "producto" no es analítica: son
> **APIs/feeds de dato crudo oficial** por matrícula (VRM) o VIN — atributos del vehículo, **estado de tax/SORN/MOT**, y (con causa legítima y de pago)
> **datos del titular (keeper)**. **Cero** residual value, days-to-sell, price-to-market, demand index o curva de depreciación: eso lo construyen otros
> *encima* de DVLA. **Patrón a copiar por cardeep:** (1) el feed canónico VRM→atributos+tax+MOT (VES) como **capa base de identidad del vehículo**;
> (2) el gating **"reasonable cause" + fee-per-enquiry** del dato sensible de titular (KADOE/ADD); (3) la **UI pública gov.uk de 2 semáforos** (Tax / MOT)
> + panel "additional vehicle details" como blueprint de *ficha de estado* minimalista.

> **Relación con otros ficheros:** DVLA es el **upstream** de `hpi-check.md`, `cap-hpi.md`, `percayso-vehicle-intelligence.md`, `experian-automotive.md`
> y de los resellers. El **MOT History API** lo opera **DVSA** (Driver & Vehicle Standards Agency), agencia hermana — distinta de DVLA — pero se audita
> aquí por pertenecer al mismo ecosistema "official data" y compartir portal histórico. **Northern Ireland** = **DVA** (agencia separada); DVLA cubre **GB**
> para conductores y **UK entero** para vehículos.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **Driver and Vehicle Licensing Agency (DVLA)** | [VERIFICADO ≥2: Wikipedia, gov.uk] |
| Naturaleza | **Agencia ejecutiva (executive agency) del Department for Transport (DfT)** del gobierno británico | [VERIFICADO ≥2: Wikipedia, api.gov.uk] |
| Owner / grupo | **Gobierno del Reino Unido** (HM Government) vía **DfT**. No es empresa privada, no cotiza | [VERIFICADO ≥2] |
| HQ | **Swansea, Gales** (edificio de 16 plantas en Clase + oficinas en Swansea Vale) | [VERIFICADO ≥2: Wikipedia] |
| Origen / fundación | Centralización de registros en Swansea desde **1965** (parte del Ministry of Transport); centro **DVLC** establecido **1968-1970s**; renombrada **DVLA** y convertida en agencia ejecutiva de DfT en **1990** | [VERIFICADO ≥2: Wikipedia, regplates, búsqueda] |
| Escala de datos | **50M+ registros de conductor** y **40M+ registros de vehículo** | [VERIFICADO ≥2: búsqueda, Oreate/blogs citando DVLA] |
| Funciones nucleares | Emite **driving licences**, mantiene el **registro de vehículos (Vehicle Main File)**, recauda **Vehicle Excise Duty (road tax)**, gestiona **SORN**, vende **matrículas personalizadas (personalised registrations)**, comparte datos con causa legítima | [VERIFICADO ≥2: Wikipedia, gov.uk] |
| Marca digital / dev | **"DVLA API Developer Portal"** — primer organismo en obtener dominio API de GDS (`*.api.gov.uk`); lanzó su portal en **mar-2020** con VES como primera API | [VERIFICADO ≥2: dvladigital.blog.gov.uk, UKAuthority] |
| Agencia hermana (MOT) | **DVSA** (Driver & Vehicle Standards Agency) — opera el **MOT History API** (history.mot.api.gov.uk) | [VERIFICADO ≥2: DVSA docs] |
| Agencia NI | **DVA** (Driver & Vehicle Agency, Irlanda del Norte) — separada; DVLA = GB para conductores | [VERIFICADO: Wikipedia] |

**Qué es:** el **registro estatal autoritativo** de vehículos (UK) y conductores (GB). Su "negocio de datos" consiste en **exponer ese registro** a
terceros mediante (a) **APIs gratuitas de dato no personal** (VES), (b) **APIs de pago y gated de dato sensible** (KADOE = titular, ADD = conductor),
(c) **feeds en bloque (bulk/anonymised/mileage data sets)** a empresas habilitadas, y (d) un **canal público gratuito** (gov.uk vehicle enquiry).
Es la **capa 0** de la pirámide de datos de automoción británica.

### Categorías de "producto" (todas = dato oficial, no analítica)
1. **APIs por vehículo (no personal):** Vehicle Enquiry Service (VES).
2. **APIs por vehículo + titular (gated, de pago):** KADOE (Keeper At Date Of Event).
3. **APIs por conductor (gated, de pago):** Access to Driver Data (ADD) + CPC + Tachograph.
4. **Feeds en bloque:** Bulk data set (V995/1, 47 campos) · Anonymised data set (V995, 30 campos) · Mileage data.
5. **Solicitudes puntuales de titular:** formulario **V888** (reasonable cause).
6. **Canal público gratuito:** gov.uk "Check if a vehicle is taxed" + "Get vehicle information from DVLA" (vehicleenquiry.service.gov.uk).
7. **APIs de soporte/infra:** DVLA Authentication, Print Request Service, Driving Licence Renewal Service, Driver Find API, Driver Image API.
8. **Adyacente (DVSA):** MOT History API.

### Cliente objetivo
**Desarrolladores/integradores** (VES) · **Operadores de aparcamiento privado, autoridades locales, agentes judiciales/bailiffs, aseguradoras**
(KADOE, datos de titular) · **Empleadores/fleets, alquiler de vehículos, grey-fleet** (ADD, comprobación de licencia de conductor) · **Empresas de
"vehicle check" y motor trade** (bulk data set → revenden a HPI/cap/Percayso/resellers) · **Marketing** (anonymised data set) · **Ciudadano/comprador
particular** (canal público gratuito) · **Industria del MOT/talleres y check providers** (MOT History API vía DVSA).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado geográfico | **Reino Unido** para registro de **vehículos**; **Great Britain (Inglaterra, Escocia, Gales)** para **conductores**. Irlanda del Norte = DVA (separado) | [VERIFICADO ≥2: Wikipedia] |
| MOT (vía DVSA) | **GB desde 2005** (coches/motos/vans), **NI desde 2017**; **HGV/trailers/buses/coaches GB desde 2018**, NI desde 2017 | [VERIFICADO ≥2: DVSA docs] |
| Parque cubierto | **Todo vehículo registrado en UK** (es el registro mismo) — cobertura censal por definición, no muestral | [VERIFICADO: naturaleza del registro] |
| Scope nuevo/usado | **Ambos**: registra desde **primera matriculación (new)** y mantiene todo el ciclo de vida (keeper changes, SORN, export, scrap) del **usado** | [VERIFICADO: campos VES/bulk] |
| Tipos de vehículo | Coches, motos, vans/LCV, HGV, trailers, buses/coaches, agrícolas — cualquier vehículo con matrícula UK | [VERIFICADO: type approval / wheelplan / revenue weight fields] |
| Identificador de entrada | **VRM (matrícula)** principal; **VIN/chassis** aceptado en KADOE; **driving licence number** en ADD | [VERIFICADO ≥2: schemas VES/KADOE/ADD] |
| Histórico temporal | Registro vivo desde 1970s; KADOE permite consulta **"a fecha de evento"** (keeper at a point in time); MOT desde 2005 | [VERIFICADO ≥2] |

---

## 3. Productos + campos atómicos

> **Importante para cardeep:** DVLA devuelve **atributos de identidad + estado regulatorio + titularidad**, NO métricas de mercado.
> Los labels de campo son **exactos del schema OpenAPI** de cada API (verificados en el developer portal). Cada producto está delimitado abajo.

### 3.1 Vehicle Enquiry Service (VES) API — núcleo gratuito por matrícula
**Qué es:** servicio REST que, dada una **matrícula (VRM)**, devuelve detalles **no personales** del vehículo. **Gratis.** `POST /v1/vehicles`,
auth por `x-api-key`. JSON. *(Registro de nuevas altas temporalmente cerrado por upgrades de sistema.)* **22 campos atómicos** (v1.2.0):

| # | Campo (label exacto) | Tipo | Descripción | Estado |
|---|---|---|---|---|
| 1 | `registrationNumber` | string | Matrícula del vehículo | [VERIFICADO: OpenAPI v1.2.0] |
| 2 | `make` | string | Fabricante | [VERIFICADO] |
| 3 | `colour` | string | Color de pintura actual | [VERIFICADO] |
| 4 | `fuelType` | string | Tipo de combustible (método de propulsión) | [VERIFICADO] |
| 5 | `engineCapacity` | integer | Cilindrada en cc | [VERIFICADO] |
| 6 | `yearOfManufacture` | integer | Año de fabricación | [VERIFICADO] |
| 7 | `co2Emissions` | integer | CO2 en g/km | [VERIFICADO] |
| 8 | `markedForExport` | boolean | Marcado para exportación | [VERIFICADO] |
| 9 | `typeApproval` | string | Categoría de homologación (Type Approval) | [VERIFICADO] |
| 10 | `wheelplan` | string | Plan de ruedas (configuración de ejes) | [VERIFICADO] |
| 11 | `revenueWeight` | integer | Peso fiscal (revenue weight) en kg | [VERIFICADO] |
| 12 | `realDrivingEmissions` | string | Valor RDE (Real Driving Emissions) | [VERIFICADO] |
| 13 | `euroStatus` | string | Euro status (Euro 1-6) | [VERIFICADO] |
| 14 | `dateOfLastV5CIssued` | date | Fecha de emisión del último V5C (logbook) | [VERIFICADO] |
| 15 | `monthOfFirstRegistration` | date | Mes de primera matriculación | [VERIFICADO] |
| 16 | `monthOfFirstDvlaRegistration` | date | Mes de primera matriculación DVLA | [VERIFICADO] |
| 17 | `taxStatus` | enum | Estado de tax: `Taxed` / `SORN` / `Untaxed` / `Not Taxed for on Road Use` | [VERIFICADO] |
| 18 | `taxDueDate` | date | Fecha de vencimiento del tax | [VERIFICADO] |
| 19 | `artEndDate` | date | Additional Rate of Tax End Date | [VERIFICADO] |
| 20 | `motStatus` | enum | Estado MOT: `Valid` / `Not valid` / `No details held by DVLA` / `No results returned` | [VERIFICADO] |
| 21 | `motExpiryDate` | date | Fecha de caducidad del MOT | [VERIFICADO] |
| 22 | `automatedVehicle` | boolean | Vehículo automatizado (AV) | [VERIFICADO] |

> **NO devuelve** (explícito): nombre/dirección del titular, historial de servicio, historial de siniestros, ni dato personal alguno.
> Errores: 400 (`code 105` = formato de matrícula inválido), 404 (no encontrado), 500, 503. Rate limit por cliente (HTTP 429); **1 API key por empresa**.

### 3.2 KADOE (Keeper At Date Of Event) API — titular del vehículo (gated, de pago)
**Qué es:** REST `POST /kadoe/v1/vehicle-keeper`. Devuelve **el vehículo y su titular (keeper) en un punto temporal** (la "fecha de evento", p.ej. la
infracción de aparcamiento). Requiere **JWT (DVLA Authentication API) + API key**. Solo para quien tiene **"reasonable cause"** (operadores de aparcamiento
privado, autoridades locales, bailiffs, aseguradoras). **£2.50/consulta** para empresas privadas (gratis para councils).

**Request (campos de entrada):** `enquirerId` · `linkProviderId` · `reasonCode` · `registrationNumber` · `chassisVin` · `eventDate` (YYYY-MM-DD) · `referenceNumber`. [VERIFICADO: OpenAPI v1.0.4]

**Response — Vehículo:**
| Campo | Descripción | Estado |
|---|---|---|
| `registrationNumber` | Matrícula | [VERIFICADO v1.0.4] |
| `chassisVin` | VIN / nº de chasis | [VERIFICADO] |
| `make` | Fabricante | [VERIFICADO] |
| `model` | Modelo | [VERIFICADO] |
| `fleetNumber` | Nº de flota | [VERIFICADO] |
| `colour` | Color primario | [VERIFICADO] |
| `secondaryColour` | Color secundario | [VERIFICADO] |
| `taxClass` | Clase fiscal | [VERIFICADO] |
| `taxStatus` | `Taxed`/`SORN`/`Untaxed`/`Not Taxed for on Road Use` | [VERIFICADO] |
| `bodyType` | Tipo de carrocería | [VERIFICADO] |
| `seatingCapacity` | Plazas (integer) | [VERIFICADO] |
| `message` | Marcador para vehículo **robado / desguazado (scrapped) / exportado** | [VERIFICADO] |

**Response — Keeper (titular):** `title` · `firstNames` · `lastName` · `companyName` · **address** (`line1`,`line2`,`line3`,`line4`,`line5`,`postcode`). [VERIFICADO v1.0.4]

### 3.3 Access to Driver Data (ADD) API — registro del conductor (gated, de pago)
**Qué es:** REST/HTTPS `POST`, JSON. Dado un **driving licence number**, devuelve el **registro de conducción** del ciudadano UK. Auth: **JWT (Authentication API) + API key**.
Solo **"authorised consumers"** con necesidad de negocio demostrable; **prohibido para identity-checking**; solo para verificar **derecho a conducir**.
**£0.60/consulta** (revisado anualmente), facturación mensual por direct debit, **throttle 10/s**, 24/7. Versión v1.26.0 (jul-2025).

**Campos atómicos (driver + licence):**
- **Driver:** `drivingLicenceNumber` · `firstNames` · `surname` · `gender` · `dateOfBirth` · `address` (lines + `postcode`)
- **Licence:** `licenceType` (Full/Provisional) · `licenceStatus` (Valid) · `issueNumber` · `validFrom` · `validTo` (expiry)
- **Entitlements (categorías):** `categoryCode` (A, B, C…) · `categoryLegalDescription` · `categoryType` · `fromDate` · `expiryDate` · `restrictionCode` · `restrictionDescription`
- **Endorsements (sanciones):** `offenceCode` · `offenceLegalDescription` · `offenceDate` · `penaltyPoints` · `penaltyPointsExpiryDate` *(nuevo v1.25.0)* · disqualification (`startDate` · `removalDate` · `reimposedDate` · `suspensionStatus`)
- **Opcionales bajo petición:** **CPC** (Certificate of Professional Competence) · **Tachograph card** (`cardNumber` · `cardStatus` · `cardExpiryDate` · `cardStartOfValidityDate`)
[VERIFICADO ≥2: driver-view-description, búsqueda v1.26.0]

### 3.4 Bulk data set (V995/1) — feed en bloque para "vehicle check" providers
**Qué es:** dataset de **47 campos** de información de vehículo, **sin nombres ni direcciones**. DVLA lo licencia a "certain companies" que prestan
**servicios de comprobación de vehículo** al público y al motor trade (es el feed que alimenta a HPI/cap/resellers). Incluye **VRN + VIN + make + model**
y atributos de identidad/estado. [VERIFICADO ≥2: gov.uk/data-requests-dvla, V995/1 publication]

> ⚠ **47 campos no enumerados individualmente:** el documento oficial **V995/1** es un PDF **basado en imagen** (sin capa de texto extraíble, y `pdftoppm`
> no disponible en este entorno) → **no pude verificar uno a uno los 47 labels**. Lo confirmado: el **superset** coincide con VES (22) + identificadores
> (VIN) + datos de keeper-count/keeper-change típicos del V5C. Campos del bulk set **confirmados** = los 22 de VES + `chassisVin`/`VIN` + `model`. Campos
> **probables [NV exact label]** (estándar V5C, presentes en el ecosistema pero no verificados en el PDF imagen esta sesión): `numberOfPreviousKeepers`,
> `dateOfLastKeeperChange`, `cylinderCapacity`, `seatingCapacity`, `bodyType`, `scrapped/CoD marker`. **No inventar el resto** hasta leer V995/1 en texto.

### 3.5 Anonymised data set (V995) — marketing
**Qué es:** **30 campos por registro**, agregado/anonimizado, **para marketing**. Incluye `make` · `model` · **partial postcode**. Sin identificación individual. [VERIFICADO ≥2: gov.uk, theukrules]

### 3.6 Mileage data — feed de millaje
**Qué es:** feed en bloque con `registrationNumber` + **`mileageReading` (redondeado a las 1.000 millas más cercanas)** + **cómo obtuvo DVLA el dato (source)** + **`notificationDate`**. Ayuda a comprobar el km del vehículo. [VERIFICADO ≥2: gov.uk/data-requests-dvla, theukrules]

### 3.7 V888 (solicitud puntual de titular) + canal público
**V888:** formulario para solicitar **datos del titular actual/anterior** de un vehículo con **"reasonable cause"** (Data Protection Act). Devuelve keeper details + info limitada del vehículo. [VERIFICADO ≥2: gov.uk/request-information-from-dvla]
**Canal público gratuito** (vehicleenquiry.service.gov.uk / gov.uk/check-vehicle-tax): por matrícula, devuelve **tax status + due date**, **SORN**, **MOT expiry**, y panel de **additional vehicle details** (ver §7). **Color y keeper NO disponibles online.** [VERIFICADO ≥2: gov.uk]

### 3.8 MOT History API (operado por DVSA) — historial de inspección técnica
**Qué es:** REST, JSON. Por **matrícula** (o vehicleId, o página/fecha para bulk). Auth: **OAuth2 client_credentials** (client ID + secret + scope + token URL vía Microsoft Entra ID, token 60 min) **+ `X-API-Key`**. **Gratis** (registro propio, aprobación 1-5 días). Versión clásica v6 **deprecada 01-sep-2025** en favor de la nueva (single API, incluye NI).

**Campos — nivel vehículo:** `registration` · `make` · `model` · `firstUsedDate` · `fuelType` · `primaryColour` · `vehicleId` · `registrationDate` · `manufactureDate` · `engineSize` · `hasOutstandingRecall` *(schema nuevo; [NV] en ejemplo clásico)* · `motTests[]`. [VERIFICADO ≥2: DVSA docs, github]
**Campos — `motTests[]`:** `completedDate` · `testResult` · `expiryDate` · `odometerValue` · `odometerUnit` · `odometerResultType` · `motTestNumber` · `rfrAndComments[]`. [VERIFICADO ≥2]
**Campos — `rfrAndComments[]` (defectos):** `text` · `type` (`FAIL`/`ADVISORY`/`MAJOR`/`DANGEROUS`/`MINOR`/`USER ENTERED`) · `dangerous` (boolean). [VERIFICADO ≥2]
**Endpoints:** `/trade/vehicles/mot-tests?registration=` · `?vehicleId=` · `?page=` (bulk) · `?date=&page=` (por fecha). [VERIFICADO: dvsa.github.io]

### 3.9 APIs de soporte / infra (no-dato de mercado)
`DVLA Authentication` (v1.0.7, emite JWT) · `Print Request Service` (v1.8.0) · `Driving Licence Renewal Service` (v1.0.2) · `Driver Find API` · `Driver Image API`. Son piezas internas/transaccionales, no feeds de inteligencia. [VERIFICADO: availableapis.html, api.gov.uk/dvla]

---

## 4. Metodología / fuentes de datos

| Fuente | Aporta | Estado |
|---|---|---|
| **Vehicle Main File** (registro propio DVLA) | Identidad del vehículo, keeper, tax/SORN, export/scrap, V5C | [VERIFICADO: naturaleza del registro] |
| **Driver record** (registro propio DVLA) | Licencia, entitlements, endorsements, disqualifications, CPC, tacho | [VERIFICADO: ADD] |
| **Auto-declaración del ciudadano / V5C** | Cambios de keeper, color, SORN, export — notificados por el titular | [VERIFICADO: proceso V5C] |
| **DfT / fabricantes (homologación)** | Type approval, CO2, Euro status, RDE en primera matriculación | [VERIFICADO: campos VES] |
| **DVSA (agencia hermana)** | MOT tests, odómetro, defectos/advisories | [VERIFICADO: MOT API] |
| **HMRC / sistema VED** | Estado de tax y vencimiento | [VERIFICADO: taxStatus] |
| Naturaleza del dato | **Dato primario/de origen** — DVLA *crea* el registro, no lo deriva de terceros. Es el ground truth | [VERIFICADO] |

**Garantía/calidad:** ninguna garantía monetaria tipo "data guarantee" (no es producto comercial). La autoridad viene de ser el **registro legal estatal**.
Caveat: parte del dato es **auto-declarado** (color, km del MOT, keeper) → puede ir desactualizado entre notificaciones.

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **API REST/JSON** | VES, KADOE, ADD, MOT (DVSA) — vía `*.api.gov.uk`; UAT + producción | [VERIFICADO ≥2] |
| **Developer portal** | `developer-portal.driver-vehicle-licensing.api.gov.uk` — docs OpenAPI versionadas, onboarding, soporte | [VERIFICADO ≥2] |
| **Autenticación** | VES: `x-api-key`. KADOE/ADD: **JWT (Authentication API) + API key**. MOT: **OAuth2 client_credentials + X-API-Key** | [VERIFICADO ≥2] |
| **Feeds en bloque** | Bulk/anonymised/mileage data sets — entrega a empresas habilitadas (típicamente fichero/SFTP; vía Data Sharing team) | [VERIFICADO: gov.uk/data-requests-dvla] |
| **Link Providers (KADOE)** | Pasarela B2B vía proveedores (Valcon, Data Interchange, Taranto, Epicor, TrueCommerce…) — API/SFTP/portal gestionado | [VERIFICADO ≥2] |
| **UI pública web** | `vehicleenquiry.service.gov.uk` + `gov.uk/check-vehicle-tax` — gratis, por matrícula | [VERIFICADO ≥2] |
| **Solicitud manual** | Formulario **V888** (correo postal) para keeper data | [VERIFICADO ≥2] |
| **DMS/integración** | No hay integración nativa con DMS; los **resellers** (cap hpi, HPI, Percayso, ukvehicledata...) empaquetan DVLA dentro de sus productos DMS | [VERIFICADO indirecto] |

---

## 6. Precio

| Producto | Precio | Notas | Estado |
|---|---|---|---|
| **VES API** | **£0 (gratis)** | API key gratuita; altas nuevas temporalmente cerradas | [VERIFICADO ≥2] |
| **MOT History API (DVSA)** | **£0 (gratis)** | registro propio, credenciales OAuth gratis | [VERIFICADO ≥2] |
| **Canal público gov.uk** | **£0** | tax/MOT/SORN + detalles del vehículo | [VERIFICADO ≥2] |
| **ADD (driver data)** | **£0.60 / consulta exitosa** | revisado anual; direct debit; throttle 10/s | [VERIFICADO ≥2: ADD FAQ] |
| **KADOE (keeper data)** | **£2.50 / consulta** (empresas privadas/parking) · **£0 para councils/autoridades** | + setup fee DVLA + fees del link provider | [VERIFICADO ≥2: Carwow, contrato KADOE] |
| **Bulk / anonymised / mileage data sets** | **fee a medida** (licencia comercial, no tarifa pública) | acceso restringido a empresas habilitadas | [NV importe exacto] |
| **V888** | tasa administrativa (histórica £2.50, sujeta a cambio) | por solicitud manual | [NV importe actual] |

> Modelo: **dato no personal = gratis** (servicio público); **dato sensible (titular/conductor) = fee-per-enquiry + gating legal**; **feeds en bloque = licencia comercial**.
> DVLA ha sido criticada por **monetizar el dato de keeper** (KADOE: ingresos por venta de detalles de conductor en máximos históricos, ~£2.15bn en multas asociadas reportadas por prensa). [VERIFICADO: Carwow]

---

## 7. Placement (patrón web a copiar por cardeep)

> DVLA tiene **dos superficies** muy distintas: (A) la **UI pública** (minimalista, 2 semáforos) y (B) el **developer portal** (docs de API).
> Para cardeep el valor está en la **UI pública** como blueprint de *ficha de estado oficial del vehículo*, y en el **modelo de gating** del dato sensible.

| Dato | Dónde lo coloca DVLA |
|---|---|
| **Estado de Tax (Taxed/SORN)** | **Semáforo #1, top de la results page** (`vehicleenquiry.service.gov.uk`): texto grande "**Vehicle is taxed / Taxed until {fecha}**" o "**SORN**" |
| **Estado de MOT** | **Semáforo #2, junto al de tax**: "**MOT valid until {fecha}**" / "**No MOT**" — los dos estados regulatorios son lo primero y lo más prominente |
| **Atributos del vehículo** | Panel **"Vehicle details" / "additional vehicle details"** debajo de los semáforos: make, year of manufacture, fuel type, engine size, CO2, RDE, Euro status, type approval, weight, wheelplan, export marker, first registration, last V5C issue |
| **Color** | **Oculto en el canal público** (solo por contacto directo/V888) — decisión de privacidad/antifraude |
| **Titular (keeper)** | **NO en UI pública**; gated tras **KADOE/ADD/V888** con "reasonable cause" + fee — patrón de *dato sensible bajo llave* |
| **MOT detail (historial)** | Servido por **DVSA** (no DVLA): lista de tests con fecha, resultado, **odómetro**, y **defectos/advisories** por test (`rfrAndComments`) |
| **Dato para desarrolladores** | **Developer portal**: cada API en su página OpenAPI **versionada** (v1.2.0…), con request/response schema, ejemplos, códigos de error, rate limits |
| **Onboarding/gating** | Flujo explícito **open vs secure**: VES = self-service key; KADOE/ADD = onboarding + JWT + contrato + fee + reason code |
| **Consistencia** | Toda la UI pública sigue el **GOV.UK Design System** (semántica, accesibilidad AA, sin ruido) — minimalismo institucional |

**Lección de placement para cardeep:** el **veredicto de estado (tax/MOT) va arriba y grande**; los **atributos técnicos** van en un **panel secundario**;
el **dato sensible de titular** se **esconde tras un gate** con causa legítima y coste. Es el patrón inverso al de un valuador (que pone el precio arriba):
aquí lo que manda es el **estado legal del vehículo**.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad absoluta / ground truth:** es la **fuente de origen**, no un derivado. Make/color/tax/MOT/keeper "según DVLA" es la verdad legal. Todos los demás (HPI, cap hpi, Percayso, Experian, resellers) **revenden DVLA**.
2. **Cobertura censal real (100%):** cubre **todo** vehículo matriculado en UK por definición — ningún valuador iguala esa exhaustividad de identidad.
3. **Estado regulatorio en vivo:** **tax/SORN + MOT status + export/scrap markers** que solo el Estado puede emitir con validez legal.
4. **Dato de titular (keeper) y de conductor:** KADOE/ADD exponen **identidad + dirección + entitlements + endorsements** — dato que ningún privado posee de origen.
5. **Gratuito en la capa no personal:** VES + MOT + canal público a **£0** — un *free tier* oficial que comoditiza el dato base de identidad.
6. **Modelo de gating ejemplar:** separación limpia **open vs secure**, "reasonable cause", reason codes, fee-per-enquiry — blueprint de gobernanza de dato sensible.
7. **Identificadores oficiales:** **VRM + VIN + V5C issue date/serial** desde la fuente — base anti-clonación/anti-fraude del resto del ecosistema.
8. **Homologación de origen:** type approval, Euro status, RDE, CO2 capturados en **primera matriculación** — dato técnico-regulatorio de máxima fiabilidad.

---

## 9. Gaps (lo que NO ofrece)

1. **Cero inteligencia de mercado:** **no** hay valoración, residual value %, retail/trade price, **days-to-sell**, market days supply, **price-to-market %**, demand/supply index, ni **curva de depreciación**. DVLA es dato crudo; el análisis lo construyen otros encima.
2. **Sin specs/equipamiento granular:** no da derivative/trim, lista de opciones de fábrica, P11D, ni spec WLTP atómico (eso es cap hpi/JATO). Solo make + atributos básicos del registro.
3. **Sin valoración ni ajuste por km:** no estima valor ni lo ajusta por mileage/condición. El `mileage data set` solo da lecturas redondeadas a 1.000 millas, sin analítica.
4. **Color y keeper fuera del canal gratis:** color oculto online; titular siempre gated + de pago + con causa legítima → fricción para un producto de consumo.
5. **VES con altas cerradas:** no se aceptan **nuevas** registraciones de VES API (upgrades de sistema) → barrera de acceso temporal al feed gratuito.
6. **Fragmentación de agencias:** **MOT = DVSA**, **NI = DVA**, **driver vs vehicle** en sistemas/gating distintos → no hay un único "one-call" que devuelva identidad+estado+MOT+keeper.
7. **Sin historial de siniestros/write-off ni finance:** eso vive en **MIAFTR (ABI)** y en finance houses, no en DVLA. DVLA no conoce el daño ni la financiación.
8. **Sin huella digital de punto de venta ni inventario:** no cataloga dealers, ni stock en venta, ni presencia online — territorio propio de cardeep, completamente ausente.
9. **PDF imagen / docs poco machine-friendly:** la spec del **bulk data set (47 campos)** está en PDF imagen, no enumerable programáticamente → fricción de integración del feed comercial.
10. **No marketplace, no feed de precios, no telemetría:** ningún dato de mercado, de anuncios, ni de uso real del vehículo.
11. **Latencia de actualización:** parte del dato es **auto-declarado** (color, keeper, SORN) y "puede tardar hasta 2 días laborables" en actualizar — no es tiempo real para todo.

---

## 10. Fuentes (URLs)

**Developer portal / APIs (primario)**
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/ (portal, identidad)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/availableapis.html (catálogo: Auth, Driving Licence Renewal, ADD, Print Request, KADOE, VES)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/v1.2.0-vehicle-enquiry-service.html (**schema VES, 22 campos**)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html (VES guide, no-personal, registro cerrado, rate limits)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/kadoe/kadoe-description.html (KADOE: keeper, reasonable cause, auth)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/kadoe/v1.0.4-kadoe.html (**schema KADOE completo: vehículo + keeper + request**)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/driver-view/driver-view-description.html (**ADD: driver/licence/entitlements/endorsements/CPC/tacho**)
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/driver-view/driver-view.html (driver-view-external v1.26.0)
- https://www.api.gov.uk/dvla/ (catálogo gov: ADD, Authentication, VES, Driver Find API, Driver Image API, KADOE)

**MOT History API (DVSA)**
- https://documentation.history.mot.api.gov.uk/ (operador DVSA, cobertura GB 2005 / NI 2017 / HGV 2018)
- https://documentation.history.mot.api.gov.uk/mot-history-api/authentication/ (OAuth2 client_credentials + X-API-Key, Entra ID, token 60min)
- https://dvsa.github.io/mot-history-api-documentation/ (**schema: vehicle + motTests + rfrAndComments; endpoints; v6 deprecada sep-2025**)

**Datos en bloque / solicitudes / canal público (gov.uk)**
- https://www.gov.uk/data-requests-dvla (bulk 47 campos · anonymised 30 campos · mileage data)
- https://assets.publishing.service.gov.uk/media/6964ca1a99fbdc498faeccc1/v995x1-bulk-data-set-information-for-vehicle-buyers.pdf (V995/1 bulk, dic-2025 — **PDF imagen, 47 labels no extraíbles**)
- https://www.gov.uk/get-vehicle-information-from-dvla (lista de campos del canal público; color/keeper excluidos online)
- https://www.gov.uk/check-vehicle-tax · https://vehicleenquiry.service.gov.uk/ (UI pública, semáforos tax/MOT)
- https://www.gov.uk/request-information-from-dvla/request-information-about-another-vehicle-registered-keeper (V888)
- https://www.theukrules.co.uk/rules/driving/vehicle-registration/dvla-data-request/ (bulk/anonymised/mileage, conteos de campos)

**Identidad / escala / pricing / verificación cruzada**
- https://en.wikipedia.org/wiki/Driver_and_Vehicle_Licensing_Agency (agencia ejecutiva DfT, Swansea, 1965/1990)
- https://dvladigital.blog.gov.uk/2020/03/12/dvlas-new-api-developer-portal-launch-first-api-vehicle-enquiry-service-ves-on-gov-uk/ (lanzamiento portal + VES, mar-2020)
- https://www.ukauthority.com/articles/dvla-sets-up-api-developer-portal/ (primer dominio API de GDS)
- https://www.carwow.co.uk/news/6725/drivers-fined-record-amounts (KADOE £2.50/consulta, gratis councils, ingresos por venta de keeper data)
- https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/455973/Annex_A_-_KADOE_Fee_Paying_Contract_V4.pdf (contrato KADOE fee-paying)

> **Marcas [NV] / pendientes:** enumeración campo-a-campo de los **47 del bulk data set V995/1** (PDF imagen, sin texto; `pdftoppm` ausente) y de los
> **30 del anonymised set**; importes exactos de las licencias de feeds en bloque y tasa V888 actual; `hasOutstandingRecall` en el schema MOT nuevo
> (no aparece en ejemplo clásico). Todo lo demás verificado en ≥2 fuentes o directamente en el schema OpenAPI oficial del developer portal.
