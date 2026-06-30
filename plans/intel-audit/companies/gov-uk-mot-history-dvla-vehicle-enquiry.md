# GOV.UK MOT History & DVLA Vehicle Enquiry — Auditoría atómica

> **slug:** `gov-uk-mot-history-dvla-vehicle-enquiry` · **subdominio de audit:** `official-data`
> **web (consumer MOT):** https://www.gov.uk/check-mot-history · **web (consumer tax/datos):** https://www.gov.uk/check-vehicle-tax · https://www.gov.uk/get-vehicle-information-from-dvla
> **UI pública real:** https://vehicleenquiry.service.gov.uk/ · **MOT API (DVSA):** https://documentation.history.mot.api.gov.uk/ · **VES API (DVLA):** https://developer-portal.driver-vehicle-licensing.api.gov.uk/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído, `[NV]` lo no verificado; nada inventado.
>
> **Veredicto express:** esto **NO es una empresa de inteligencia de mercado ni un valuador**. Son los **canales público-gratuitos y las APIs gratuitas del
> Estado británico** que exponen el **dato de verdad (ground truth)** del parque: el **historial de MOT (ITV británica) por matrícula** (operado por **DVSA**)
> y el **estado/atributos del vehículo** (tax, SORN, MOT, specs) por matrícula (operado por **DVLA**, vía **Vehicle Enquiry Service**). De aquí beben *todos*
> los auditados UK (HPI Check, cap hpi, Percayso, Auto Trader, Experian, resellers `ukvehicledata.co.uk`/`vehicledataglobal.com`). **Cero** residual value,
> days-to-sell, price-to-market, demand index, depreciación: nada de analítica — es **dato crudo oficial**. Su valor para cardeep es triple:
> **(1)** el **feed canónico VRM→identidad+estado** (VES) como **capa 0 de identidad del vehículo**;
> **(2)** la **timeline de MOT** (fecha/resultado/km/defectos) como **prueba censal de existencia + honestidad de kilometraje** (clocking);
> **(3)** la **UI pública** — el patrón **"2 semáforos" (Tax / MOT) + panel de detalles expandible** (vehicleenquiry) y la **timeline de tarjetas de test con
> badge PASS/FAIL + agrupación "reparar ya / vigilar"** (check-mot-history) — como blueprint exacto de *ficha de estado/historial* minimalista.

> **Relación con otros ficheros del audit:**
> - `dvla.md` audita la **agencia completa** (VES + APIs gated de pago KADOE/ADD + bulk feeds + venta de matrículas). **Este fichero** se centra en el eje
>   **público-gratuito + APIs gratuitas** (consumer gov.uk + MOT History API de DVSA + VES) y su **placement de UI**, que es lo que cardeep copia.
> - `hpi-check.md`, `cap-hpi.md`, `percayso-vehicle-intelligence.md`, `experian-automotive.md` consumen estos feeds **aguas abajo** y construirán encima la analítica.
> - El **MOT lo opera DVSA** (Driver & Vehicle Standards Agency); el **vehicle enquiry lo opera DVLA** (Driver and Vehicle Licensing Agency). Son **agencias
>   hermanas distintas** del **Department for Transport**. **Irlanda del Norte** = **DVA** (agencia separada), pero el MOT History API ya integra NI.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Naturaleza | **Servicios públicos digitales del gobierno del Reino Unido** (no empresa, no cotiza, no tiene "owner" privado) | [VERIFICADO ≥2: gov.uk, api.gov.uk] |
| Operador del MOT History | **DVSA — Driver and Vehicle Standards Agency**, agencia ejecutiva del **Department for Transport (DfT)** | [VERIFICADO ≥2: documentation.history.mot.api.gov.uk, dvsadigital.blog.gov.uk] |
| Operador del Vehicle Enquiry | **DVLA — Driver and Vehicle Licensing Agency**, agencia ejecutiva del **DfT** | [VERIFICADO ≥2: developer-portal.driver-vehicle-licensing.api.gov.uk, api.gov.uk] |
| Owner / grupo | **HM Government** (gobierno británico) vía **DfT**. Plataforma de publicación = **GOV.UK / GDS (Government Digital Service)** | [VERIFICADO ≥2: gov.uk, dvladigital.blog.gov.uk] |
| HQ | **DVSA: Bristol/Swansea** · **DVLA: Swansea (Gales)** | [VERIFICADO: gov.uk, Wikipedia; HQ exacto DVSA = Bristol] |
| Origen / hitos | DVSA creada en **2014** (fusión VOSA+DSA); **datos MOT abiertos al público en 2015**; **MOT History API pública desde ene-2018** ("opening up our MOT history data"); **portal API de DVLA + VES lanzados mar-2020** (primer organismo con dominio `*.api.gov.uk`) | [VERIFICADO ≥2: dvsadigital.blog.gov.uk 2018-01-05, dvladigital.blog.gov.uk 2020-03-12, UKAuthority] |
| Marca digital | **"MOT history API"** (DVSA) · **"DVLA API Developer Portal"** + **"Vehicle Enquiry Service (VES)"** (DVLA) · canales ciudadano en **GOV.UK** | [VERIFICADO ≥2] |

**Qué es:** dos cosas que el usuario agrupa bajo una sola ficha por compartir ecosistema "official data" y entrada por matrícula:
1. **GOV.UK Check MOT history + MOT History API (DVSA):** expone el **historial completo de pruebas MOT** (la ITV británica) de cada vehículo — pasa/falla,
   kilometraje leído, defectos y advisories, fecha de caducidad, número de certificado, ubicación del test.
2. **GOV.UK Check vehicle tax / Get vehicle information + Vehicle Enquiry Service API (DVLA):** expone el **estado e identidad del vehículo** — tax, SORN,
   MOT status, make, color, año, cilindrada, CO2, combustible, export marker, type approval, wheelplan, peso, Euro status, RDE, fecha último V5C.

### Categorías de "producto" (todas = dato oficial, no analítica)
1. **Canal público ciudadano (gratis, sin login):** `gov.uk/check-mot-history`, `gov.uk/check-vehicle-tax`, `gov.uk/get-vehicle-information-from-dvla`, `gov.uk/check-mot-status`.
2. **API REST de historial MOT (DVSA, gratis con API key + OAuth):** MOT History API (por matrícula, por vehicleId, por VIN, paginada, por fecha).
3. **Bulk + delta data download (DVSA):** snapshot completo semanal + deltas diarios.
4. **API REST de consulta de vehículo (DVLA, gratis con API key):** Vehicle Enquiry Service (VES).
5. **Servicio adyacente:** GOV.UK MOT reminders (recordatorio por SMS/email).

### Cliente objetivo
**Ciudadano/comprador particular** de usado (canal público) · **Desarrolladores/integradores** (APIs gratis) · **Motor trade, dealers, talleres, check-providers**
(MOT History API + bulk) · **Aseguradoras, fleets, lead-gen, apps de gestión de coche** (VES + MOT) · **Toda la cadena de "vehicle check" UK** que revende encima.

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado geográfico | **Reino Unido completo.** MOT History API integra **Great Britain (Inglaterra, Escocia, Gales) + Northern Ireland**; VES cubre el registro UK de vehículos | [VERIFICADO ≥2: documentation.history.mot.api.gov.uk, gov.uk/check-mot-history] |
| Histórico MOT | **Coches, motos, vans: desde 2005** (GB) · **Northern Ireland: desde 2017** · **HGV, trailers, buses, coaches: desde 2018** (GB), 2017 (NI) | [VERIFICADO ≥2: gov.uk/check-mot-history, documentation.history.mot.api.gov.uk] |
| Parque cubierto | **Censal por definición** (es el registro estatal mismo, no muestra). Todo vehículo con matrícula UK y todo MOT realizado | [VERIFICADO: naturaleza del registro] |
| Scope nuevo/usado | **Ambos.** Vehículo recién matriculado sin MOT aún → objeto con `motTestDueDate` (primer MOT). Usado → timeline completa de tests | [VERIFICADO ≥2: documentation.history.mot.api.gov.uk version-history, gov.uk] |
| Tipos de vehículo | Coches, motos, vans/LCV, HGV, trailers, buses/coaches — cualquier vehículo con matrícula UK sujeto a MOT | [VERIFICADO ≥2: gov.uk/check-mot-history] |
| Identificador de entrada | **VRM (matrícula)** principal; MOT API admite además **VIN** y **vehicleId**; para *test location* en GB se exige el **nº de 11 dígitos del V5C** | [VERIFICADO ≥2: gov.uk/check-mot-history, dvsa.github.io, dlthub] |
| Limitación NI | En NI no se muestran fail/minor detalle ni test location vía la UI pública (sí pasa/falla, km, próximo MOT) | [VERIFICADO: gov.uk/check-mot-history] |

---

## 3. Productos + campos atómicos

> **Regla de lectura:** nombres de campo **literales** tal como aparecen en la API/UI. `[V]` = visto en schema/ejemplo real. `[V-prosa]` = nombrado en doc/prosa pero no en
> un schema completo. `[PARCIAL]` = capacidad verificada pero nombre/forma exacta no confirmada en esta auditoría.

### 3.1 — DVSA MOT History API · objeto **Vehicle** (con MOT)
Endpoint núcleo: `GET /v1/trade/vehicles/mot-tests?registration={VRM}` (legacy `check-mot.service.gov.uk`) / nueva combinada `history.mot.api.gov.uk`. Respuesta **JSON**.

| # | Campo | Significado | Estado |
|---|---|---|---|
| 1 | `registration` | Matrícula del vehículo | [V: ejemplo JSON dvsa.github.io] |
| 2 | `make` | Marca | [V] |
| 3 | `model` | Modelo | [V] |
| 4 | `firstUsedDate` | Fecha de primera puesta en circulación | [V: dvsa.github.io] |
| 5 | `fuelType` | Combustible (Petrol, Diesel, Electric, Hybrid Electric (Clean), Gas/LPG/CNG/LNG, Gas Bi-Fuel, Gas Diesel, Electric Diesel, Fuel cells, Steam, Other) | [V: bulk-file-formats] |
| 6 | `primaryColour` | Color primario | [V] |
| 7 | `secondaryColour` | Color secundario | [V: bulk-file-formats] |
| 8 | `vehicleId` | Identificador interno del vehículo (para búsqueda por vehicleId) | [V: version-history 2019-01-22] |
| 9 | `registrationDate` | Fecha de matriculación | [V] |
| 10 | `manufactureDate` | Fecha de fabricación | [V] |
| 11 | `engineSize` | Cilindrada del motor | [V] |
| 12 | `hasOutstandingRecall` | Indicador de recall de seguridad pendiente (depende del fabricante) | [PARCIAL: capacidad verificada en UI pública gov.uk; nombre de campo de la nueva API] |
| 13 | `lastMotTestDate` | Fecha del MOT más reciente (en bulk) | [V: bulk-file-formats] |
| 14 | `dataSource` | Origen del registro: `dvsa` / `dvla` / `dva ni` | [V: bulk-file-formats] |
| 15 | `last_update_date` | Fecha de última actualización del registro (en bulk) | [V: bulk-file-formats] |
| 16 | `motTests[]` | Array de pruebas MOT (ver 3.2) | [V] |

### 3.2 — Objeto **MOT test** (cada ítem de `motTests[]`)
| # | Campo | Significado | Estado |
|---|---|---|---|
| 17 | `completedDate` | Fecha/hora de realización del test (`YYYY.MM.DD HH:MM:SS`) | [V: ejemplo JSON] |
| 18 | `testResult` | Resultado: **`PASSED` / `FAILED`** (null cuando el origen es DVLA) | [V: ejemplo + bulk] |
| 19 | `expiryDate` | Fecha de caducidad del MOT (solo si PASSED) | [V] |
| 20 | `odometerValue` | Lectura del odómetro (kilometraje) en el test | [V] |
| 21 | `odometerUnit` | Unidad: **`mi` / `km`** (`MI`/`KM` en bulk) | [V] |
| 22 | `odometerResultType` | **`READ` / `UNREADABLE` / `NO_ODOMETER`** | [V: version-history 2017-11-14] |
| 23 | `motTestNumber` | Número de certificado del test (12 dígitos) | [V] |
| 24 | `dataSource` | Origen del test (en bulk): `dvsa`/`dvla`/`dva ni` | [V: bulk-file-formats] |
| 25 | `registrationAtTimeOfTest` | Matrícula del vehículo en el momento del test (detecta cambios de placa) | [V: bulk-file-formats] |
| 26 | `rfrAndComments[]` / `defects[]` | Array de Reasons For Rejection + comentarios/defectos (ver 3.3) | [V] |

### 3.3 — Objeto **Defect / RFR** (cada ítem de `rfrAndComments[]` / `defects[]`)
| # | Campo | Significado | Estado |
|---|---|---|---|
| 27 | `text` | Descripción del defecto, con código de manual MOT entre paréntesis (ej. `"Front brake disc excessively pitted (3.5.1h)"`) | [V: ejemplo JSON] |
| 28 | `type` | Clasificación: **`DANGEROUS` / `MAJOR` / `MINOR` / `ADVISORY` / `PRS` (Pass after Rectification at Station) / `FAIL` / `USER ENTERED`** (legacy: `NON SPECIFIC`, `SYSTEM GENERATED`) | [V: ejemplo + bulk-file-formats] |
| 29 | `dangerous` | Booleano: defecto peligroso sí/no | [V: ejemplo JSON] |

### 3.4 — Objeto **Vehicle recién matriculado** (sin MOT aún)
Variante de respuesta cuando el vehículo está en DVLA pero no tiene MOT todavía. Reusa campos 1-11 y añade/sustituye:

| # | Campo | Significado | Estado |
|---|---|---|---|
| 30 | `motTestDueDate` | **Fecha del primer MOT exigible** (renombrado desde `motTestExpiryDate` el 2018-01-30) | [V-prosa: version-history] |
| 31 | `manufactureYear` | Año de fabricación (variante string) | [PARCIAL: legacy DVLA-ID object] |
| 32 | `dvlaId` | Identificador DVLA del vehículo sin MOT (precursor de `vehicleId`) | [PARCIAL: legacy] |
| 33 | `cylinderCapacity` | Cilindrada (cc) del motor | [V-prosa: búsqueda "cylinder capacity of the engine"] |
| 34 | `co2Emissions` | CO2 (g/km) — aportado al fusionar con dato DVLA | [PARCIAL] |
| 35 | `euroStatus` | Norma Euro de emisiones | [PARCIAL] |
| 36 | `realDrivingEmissions` | Nivel RDE | [PARCIAL] |

### 3.5 — DVLA **Vehicle Enquiry Service (VES) API** · respuesta
Endpoint: `POST /vehicle-enquiry/v1/vehicles` (body `{ "registrationNumber": "..." }`). Base prod `https://driver-vehicle-licensing.api.gov.uk`; UAT `https://uat.driver-vehicle-licensing.api.gov.uk`. Respuesta **JSON**. **Todos [V] del spec v1.2.0.**

| # | Campo | Tipo | Significado | Estado |
|---|---|---|---|---|
| 37 | `registrationNumber` | string | Matrícula | [V] |
| 38 | `taxStatus` | enum | **`Taxed` / `Untaxed` / `SORN` / `Not Taxed for on Road Use`** | [V] |
| 39 | `taxDueDate` | date | Fecha de vencimiento del tax (para cálculo de licencia) | [V] |
| 40 | `artEndDate` | date | **Additional Rate of Tax End Date** (`YYYY-MM-DD`) | [V] |
| 41 | `motStatus` | enum | **`Valid` / `Not valid` / `No details held by DVLA` / `No results returned`** | [V] |
| 42 | `motExpiryDate` | date | Caducidad del MOT | [V] |
| 43 | `make` | string | Marca | [V] |
| 44 | `monthOfFirstDvlaRegistration` | date | Mes de primera matriculación en DVLA | [V] |
| 45 | `monthOfFirstRegistration` | date | Mes de primera matriculación | [V] |
| 46 | `yearOfManufacture` | int32 | Año de fabricación | [V] |
| 47 | `engineCapacity` | int32 | Cilindrada en cm³ | [V] |
| 48 | `co2Emissions` | int32 | CO2 en g/km | [V] |
| 49 | `fuelType` | string | Combustible (método de propulsión) | [V] |
| 50 | `markedForExport` | boolean | True solo si está marcado para exportación | [V] |
| 51 | `colour` | string | Color | [V] |
| 52 | `typeApproval` | string | Categoría de homologación (Type Approval) | [V] |
| 53 | `wheelplan` | string | Configuración de ruedas (wheelplan) | [V] |
| 54 | `revenueWeight` | int32 | Peso fiscal (revenue weight) en kg | [V] |
| 55 | `realDrivingEmissions` | string | Valor Real Driving Emissions | [V] |
| 56 | `dateOfLastV5CIssued` | date | Fecha del último V5C (libro de registro) emitido | [V] |
| 57 | `euroStatus` | string | Norma Euro (Dealer/Customer provided en nuevos) | [V] |
| 58 | `automatedVehicle` | boolean | Vehículo autónomo (AV) | [V] |

### 3.6 — VES · objeto **error**
| # | Campo | Significado | Estado |
|---|---|---|---|
| 59 | `status` | Código HTTP del error | [V] |
| 60 | `code` | Código de referencia DVLA | [V] |
| 61 | `title` | Título del error | [V] |
| 62 | `detail` | Descripción significativa del error | [V] |

### 3.7 — Campos DERIVADOS / de presentación (solo UI pública, no API cruda)
Importan para *placement* (cardeep los recalcula encima del dato crudo):

| Campo derivado | Dónde | Estado |
|---|---|---|
| **Flag de inconsistencia de kilometraje (clocking)** — caída de odómetro entre tests consecutivos | UI MOT history (alerta automática) | [V: búsqueda placement check-mot] |
| **Next MOT due date** (etiqueta consumer de `expiryDate`/`motTestDueDate`) | Cabecera de la UI MOT | [V] |
| Agrupación **"Repair immediately"** (defectos dangerous+major) | Tarjeta de cada test FAILED | [V] |
| Agrupación **"Monitor and repair if necessary"** (minor+advisory) | Tarjeta de cada test | [V] |
| **Certificado MOT descargable** (actual + anteriores) | Acción en la UI | [V: gov.uk/check-mot-history] |
| **Test location** (centro donde se hizo el test) | Detalle del test, requiere V5C de 11 dígitos | [V] |
| **Safety recall** (sí/no recall pendiente) | Banner superior UI | [V] |

---

## 4. Metodología / fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Origen MOT | **Captura primaria en el acto del test**: cada estación MOT introduce resultado, lectura de odómetro y defectos en el sistema de DVSA. Es dato de *primera mano*, no estimado | [VERIFICADO: naturaleza del MOT + dvsadigital.blog] |
| Origen vehículo (VES) | **Vehicle Main File de DVLA** — el registro estatal alimentado por matriculación (V55), cambios de V5C, tax/SORN, export/scrap | [VERIFICADO ≥2: developer-portal DVLA, dvla.md] |
| Integración NI | El MOT History API combina ahora **DVSA (GB) + DVA (NI)** en una sola API; campo `dataSource` distingue origen | [VERIFICADO: documentation.history.mot.api.gov.uk] |
| Frescura | **VES = tiempo real** contra el registro. **MOT bulk = snapshot semanal (domingos) + deltas diarios (8:00, ventana 24 h)**; API por matrícula = al día | [VERIFICADO ≥2: download-vehicle-mot-history-data, rate-limits] |
| Naturaleza | **Dato fáctico oficial, censal.** Sin modelado, sin valoración, sin predicción. Es ground truth, no inteligencia | [VERIFICADO: ausencia de campos analíticos en todos los schemas] |
| Privacidad | El MOT History API publica una **privacy notice** propia; no expone datos de titular (eso es KADOE, gated y de pago — ver `dvla.md`) | [VERIFICADO: gov.uk MOT history API privacy notice] |

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **UI web ciudadano (gratis)** | `gov.uk/check-mot-history`, `gov.uk/check-vehicle-tax`, `gov.uk/get-vehicle-information-from-dvla`, `gov.uk/check-mot-status` → todas resuelven en `vehicleenquiry.service.gov.uk` y el servicio MOT. Sin login | [VERIFICADO ≥2: gov.uk] |
| **REST API — MOT History (DVSA)** | JSON. Endpoints: por `registration`, por `vehicleId`, por **VIN**, paginada (`page`), por `date`+page, y **`/v1/trade/vehicles/bulk-download`**. Auth = **OAuth2 client-credentials (Microsoft Entra ID) + `x-api-key`**; token Bearer 60 min | [VERIFICADO ≥2: dvsa.github.io, documentation.history.mot.api.gov.uk/authentication] |
| **REST API — VES (DVLA)** | JSON. `POST /vehicle-enquiry/v1/vehicles`. Auth = **`x-api-key`** header. Entornos **prod + UAT** | [VERIFICADO ≥2: developer-portal DVLA, code-examples] |
| **Bulk + delta download** | Ficheros **JSON (newline-delimited) comprimidos**: 1 bulk semanal (snapshot completo GB+NI) + N deltas diarios (cambios 24 h). Llamada miércoles → 1 bulk + 4 deltas (URLs firmadas) | [VERIFICADO ≥2: download-vehicle-mot-history-data, bulk-file-formats] |
| **Recordatorios** | GOV.UK MOT reminders (email/SMS por matrícula) | [VERIFICADO: gov.uk] |
| **SDKs comunidad** | Wrappers no oficiales en GitHub (PHP `billythekid/dvla-ves`, Python `tigattack/dvla-ves-api-py`, `dvsa-mot-history` PyPI, Apify actor) | [VERIFICADO ≥2: GitHub, PyPI, Apify] |
| **NO ofrece** | Dashboard analítico, Excel/CSV por consulta individual, integración DMS, informe PDF de mercado | [VERIFICADO: ausencia en docs] |

---

## 6. Precio

| Aspecto | Detalle | Estado |
|---|---|---|
| Canal ciudadano | **100% gratuito**, sin registro | [VERIFICADO ≥2: gov.uk] |
| MOT History API | **Gratuita** (servicio público) pero **gated por aprobación**: hay que registrarse y DVSA aprueba la solicitud antes de emitir API key + credenciales OAuth | [VERIFICADO ≥2: documentation.history.mot.api.gov.uk/authentication, búsqueda] |
| VES API | **Gratuita** (servicio público) con API key. **A fecha de auditoría el registro de VES está CERRADO** ("not accepting new VES API registrations while we make system upgrades") | [VERIFICADO ≥2: vehicle-enquiry-service-description, búsqueda] |
| Modelo | **No hay pago por llamada ni tiers comerciales.** El control es **cuota + aprobación**, no precio. (El dato de pago real — titular/conductor — es **KADOE/ADD**, auditado en `dvla.md`) | [VERIFICADO ≥2] |
| Cuotas MOT API | **500.000 req/día**, **15 req/seg medio**, **burst 10**; exceso → **HTTP 429**; superar la cuota diaria bloquea la key **24 h** (reinstaura sola) | [VERIFICADO: documentation.history.mot.api.gov.uk/rate-limits] |
| Credenciales MOT | client_id + client_secret (caduca cada **2 años**, avisos 30/14 días) + API key (revocada si no se usa **90 días**) + access-token URL + scope | [VERIFICADO: authentication] |
| Cuota VES | Rate limit **definido por cliente** según "estimated monthly enquiry volumes" del formulario de alta; exceso → **429** | [VERIFICADO: vehicle-enquiry-service-description, búsqueda] |

---

## 7. Placement (blueprint de UI para cardeep)

> **Esto es lo que cardeep copia.** Dos patrones distintos y complementarios:

### 7.1 — `gov.uk/check-mot-history` (servicio MOT) → **timeline de tarjetas de test**
- **Cabecera / strip de identidad** (arriba): matrícula estilizada tipo placa, **make + model**, **color**, **fuel type**, **"date registered"**.
- **Resumen de estado** (justo debajo de la identidad): **validez/caducidad del MOT** ("MOT expiry / next MOT due"), y **banner de safety recall** prominente si `hasOutstandingRecall`.
- **Cuerpo = lista cronológica inversa de "test cards"**, una por MOT. Cada tarjeta:
  - Encabezado con **fecha del test** + **badge PASSED (verde) / FAILED (rojo)**.
  - **Mileage** (odómetro) leído en ese test.
  - **MOT test number**.
  - Enlace **"view test location"** (pide los 11 dígitos del V5C).
  - Para fails/advisories: **dos listas agrupadas** — **"Repair immediately"** (dangerous + major) y **"Monitor and repair if necessary"** (minor + advisory).
- **Acción descarga**: certificado MOT actual y certificados anteriores.
- **Señal derivada**: cualquier **caída de kilometraje** entre tests se **marca automáticamente** (anticlocking).

| Dato | Dónde se coloca |
|---|---|
| make/model/color/fuel/fecha matriculación | Strip de identidad (cabecera) |
| MOT expiry / próximo MOT | Resumen de estado (top) |
| safety recall pendiente | Banner superior |
| fecha del test + PASS/FAIL | Encabezado de cada tarjeta de test |
| mileage (odómetro) | Cuerpo de la tarjeta de test |
| motTestNumber | Cuerpo de la tarjeta de test |
| defectos dangerous/major | Lista "Repair immediately" de la tarjeta |
| minor/advisory | Lista "Monitor and repair if necessary" |
| test location | Detalle del test (tras introducir V5C) |
| flag de clocking | Resaltado en la secuencia de mileage |

### 7.2 — `vehicleenquiry.service.gov.uk` (VES/DVLA) → **2 semáforos + panel expandible**
- **Paso de confirmación** ("Is this the right vehicle?"): muestra **make + colour** antes de revelar el detalle (evita falsos positivos de matrícula).
- **Dos paneles/cards de estado grandes y paralelos** = el patrón "2 semáforos":
  - **Vehicle tax**: `taxStatus` + `taxDueDate`.
  - **MOT**: `motStatus` + `motExpiryDate`.
- **Panel "additional vehicle details"** (expandible): make, colour, `yearOfManufacture`, `engineCapacity` (cc), `co2Emissions`, `fuelType`, `markedForExport`, `typeApproval`, `wheelplan`, `revenueWeight`, `euroStatus`, `realDrivingEmissions`, `dateOfLastV5CIssued`, `monthOfFirstRegistration`.

| Dato | Dónde se coloca |
|---|---|
| taxStatus + taxDueDate | Panel/semáforo izquierdo (Tax) |
| motStatus + motExpiryDate | Panel/semáforo derecho (MOT) |
| make + colour | Paso de confirmación de vehículo |
| año, cc, CO2, combustible, Euro, RDE, type approval, wheelplan, peso, último V5C, export | Panel "additional vehicle details" (expandible) |

---

## 8. Diferencial (lo que ofrece y casi nadie más)

1. **Ground truth censal y gratuito.** Es la **fuente primaria** del MOT y del registro de vehículo, no una estimación: el resto del mercado UK revende *encima* de esto.
2. **Timeline de kilometraje oficial verificado en el acto del test** — base anticlocking de coste cero (lo que HPI/Percayso empaquetan como producto premium).
3. **Defectos clasificados con severidad estandarizada** (dangerous/major/minor/advisory/PRS) y **código de manual MOT** en el texto — granularidad técnica real, no "advisory" genérico.
4. **Cobertura UK unificada GB+NI** en una sola API con `dataSource`.
5. **Bulk + delta**: permite a un tercero **replicar el dataset entero** (snapshot semanal + deltas diarios), cosa rarísima entre proveedores comerciales.
6. **`automatedVehicle`, `realDrivingEmissions`, `euroStatus`, `artEndDate`** — atributos regulatorios/emisiones que muchos agregadores no exponen.
7. **Coste cero + autoridad legal**: imbatible como capa base; ningún comercial puede competir en precio ni en autoridad sobre la fuente.

## 9. Gaps (lo que NO ofrece — y que cardeep/otros deben construir encima)

1. **Cero valoración**: no hay retail/trade price, residual value %, curva de depreciación, ajuste por km, price-to-market.
2. **Cero inteligencia de mercado**: no days-to-sell, market days supply, demand/supply index, volumen de stock, time-to-sell.
3. **No datos de titular/keeper** por estos canales (gated y de pago vía KADOE — ver `dvla.md`). El MOT API es explícitamente no-personal.
4. **No finance/outstanding loan, no stolen (PNC), no write-off/insurance category** (eso es HPI/Experian/Percayso encima de DVLA).
5. **No specs/equipamiento detallado por VIN** (trim, opcionales, paquetes): VES da atributos básicos, no la ficha técnica completa.
6. **No precio por consulta vía Excel/CSV individual, no dashboard, no DMS, no informe PDF de mercado**.
7. **Friccción de acceso API**: aprobación previa (MOT) y **registro de VES cerrado** a fecha de auditoría → no es "self-serve" inmediato.
8. **Sin valoración cross-border ni datos fuera de UK**.
9. **Limitación NI** en detalle de defectos/test location por la UI pública.
10. **`hasOutstandingRecall`** depende del fabricante (cobertura parcial); el recall no es exhaustivo.

---

## 10. Fuentes

> `[V≥2]` = verificado con ≥2 fuentes. Verificado el 2026-06-30.

**Canal ciudadano (gov.uk):**
- https://www.gov.uk/check-mot-history [V≥2] — qué muestra, histórico, V5C, recall
- https://www.gov.uk/get-vehicle-information-from-dvla [V≥2] — campos VES consumer
- https://www.gov.uk/check-vehicle-tax [V] — tax/SORN
- https://www.gov.uk/check-mot-status [V]

**DVSA MOT History API:**
- https://documentation.history.mot.api.gov.uk/ [V≥2] — overview, cobertura GB+NI
- https://documentation.history.mot.api.gov.uk/mot-history-api/api-specification/ [V] — REST/JSON
- https://documentation.history.mot.api.gov.uk/mot-history-api/authentication/ [V] — OAuth2 + x-api-key, credenciales
- https://documentation.history.mot.api.gov.uk/mot-history-api/rate-limits/ [V] — 500k/día, 15 rps, burst 10, 429
- https://documentation.history.mot.api.gov.uk/mot-history-api/download-vehicle-mot-history-data/ [V] — bulk + delta
- https://documentation.history.mot.api.gov.uk/mot-history-api/download-vehicle-mot-history-data/bulk-file-formats/ [V] — schema bulk (secondaryColour, dataSource, registrationAtTimeOfTest, last_update_date, enums)
- https://dvsa.github.io/mot-history-api-documentation/ [V≥2] — schema legacy + ejemplo JSON (motTests, rfrAndComments, type, dangerous)
- https://dvsadigital.blog.gov.uk/2018/01/05/opening-up-our-mot-history-data/ [V] — apertura del dato 2018
- https://dlthub.com/context/source/dvsa-mot-history [V] — endpoints (registration, VIN, paginación)
- https://findtransportdata.dft.gov.uk/dataset/mot-history-api [V]

**DVLA Vehicle Enquiry Service (VES) API:**
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/ [V] — Open vs Secure APIs
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/v1.2.0-vehicle-enquiry-service.html [V≥2] — schema completo de 22 campos + tipos
- https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/vehicle-enquiry-service-description.html [V≥2] — registro cerrado, UAT, ejemplo JSON, 429
- https://www.api.gov.uk/dvla/dvla-vehicle-enquiry-service/ [V] — catálogo gov
- https://dvladigital.blog.gov.uk/2020/03/12/dvlas-new-api-developer-portal-launch-first-api-vehicle-enquiry-service-ves-on-gov-uk/ [V≥2] — lanzamiento mar-2020
- https://www.ukauthority.com/articles/dvla-sets-up-api-developer-portal/ [V]

**SDKs comunidad (corroboran forma de payload):**
- https://github.com/billythekid/dvla-ves · https://github.com/tigattack/dvla-ves-api-py · https://pypi.org/project/dvsa-mot-history/ · https://apify.com/spookyweb/uk-mot-history [V]

**Notas de verificación / honestidad:**
- `hasOutstandingRecall`: la **capacidad de recall** está [V] en la UI pública; el **nombre de campo exacto** en la nueva API no se confirmó en schema en esta pasada → marcado [PARCIAL].
- Campos del objeto "vehículo recién matriculado" (`manufactureYear`, `dvlaId`, `cylinderCapacity`, `co2Emissions`, `euroStatus`, `realDrivingEmissions`): nombrados en prosa/legacy, **no** vistos todos juntos en un schema único → [V-prosa]/[PARCIAL]. `motTestDueDate` sí [V] vía version-history.
- Cuota exacta de VES: **no publicada** (se fija por cliente en el alta) → [NV].
