# Auditoría atómica — Autotelex (B.V., Arnhem)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos/valoración de automoción de los Países Bajos. Web: https://autotelex.nl/ (EN: /en/).
> Subdominio indicado por el owner: `valuation.autotelex.nl` → **host de backend/API de valoración** (devuelve "webserver is functioning normally"; no UI pública). [V]
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva del sitio NL + EN (PRO, ADS, TMC/AMC, B2B, Import, Trade-in tools, Fleet, Insurance, About, Our values, Developers), extracción de **los Swagger/OpenAPI JSON reales** de sus APIs (Advertisement API + Company Stock Valuation API), doc de "Autotelex for developers", herramienta de consumo dagwaarde.nl, una marktupdate mensual, + verificación cruzada (company.info/KvK, LinkedIn, D&B, fleet.be, búsquedas).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido · **[V-claim]** = afirmación de la propia empresa con una sola fuente (su web).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Autotelex** ("Marktleider in motorvoertuiggegevens" / "the standard in values", "de norm in waarden") | [V] |
| Razón social | **Autotelex B.V.** | [V] |
| KvK (registro mercantil NL) | **09045121** (vestiging 000016220358) | [V] |
| Forma jurídica | B.V. (privada). LinkedIn la marca como **"Particuliere onderneming"** (empresa privada), sin grupo declarado | [V] |
| HQ | **Snelliusweg 1, 6827 DG Arnhem**, Gelderland, Países Bajos | [V] |
| Fundación / autoridad desde | **1964** ("leading supplier of premium quality automotive data since 1964"; "Behind the numbers since 1964") | [V] (about + LinkedIn + múltiples) |
| Empleados | **11–50** (LinkedIn) | [V single] |
| Owner / matriz | **No verificado.** company.info lista **"Kovi Specials B.V." (desde 1995)** en gestión/dirección (es un holding NEERLANDÉS, **no** la Kovi brasileña de Moove); búsquedas asocian **Nenova IT B.V.** (Arnhem) como entidad vinculada. Estructura accionarial tras paywall | [A] |
| SBI (códigos de actividad) | 62100 (desarrollo de software), 58110 (edición), 62900 (otros servicios IT), 46645, 46720 (comercio mayorista, incl. piezas de vehículo) | [V] |
| Teléfono / contacto | +31 26-3700080 (general) / 26-3700099 / info@autotelex.nl; horario L-V 08:30–17:00 | [V] |
| Categoría | Datos e inteligencia de vehículos + **software de tasación (VMS)** + **plataforma B2B de remarketing** + cálculo **BPM/importación** + **feed de datos para aseguradoras** + valores residuales de flota/OEM | [V] |

### Clientes objetivo [V]
Concesionarios y autobedrijven · mayoristas (handelaren) · importadores · empresas de leasing/renting · **aseguradoras** · bancos · casas de subasta · administración pública/Belastingdienst (fiscal) · flotas · **OEM/importadores de marca** · sitios de comparación · y **particulares/consumidores** (vía dagwaarde.nl). "Many thousands of professionals".

---

## 2. Cobertura

### Geográfica [V]
- **Núcleo: Países Bajos** (profundidad total; integración nativa con RDW, Belastingdienst, NAP).
- **Pan-europea solo vía PARTNERS** (no datos propios): informes RV para OEM "pan-European reporting via **DAT** (DE), **L'Argus** (FR), **Quattroruote Professional** (IT)". [V single — Fleet page]
- No es un proveedor multimercado propio: su autoridad y datos son NL-céntricos. [A]

### Scope de vehículos [V]
- **Tipos**: turismos (personenauto's), vehículos comerciales / LCV (bedrijfswagens), **motocicletas** (motoren/motorfietsen), **autocaravanas** (camper vans — en módulo Import).
- **Nuevo y usado** (incl. occasions). Valoración por matrícula, marca-modelo-uitvoering (versión) o VIN.
- **Powertrains**: combustión, híbridos y **eléctricos** (campos batería kWh, consumo kWh ciudad/autopista, rango combinado/eléctrico presentes en la API; CO₂, etiqueta energética).

---

## 3. Productos + campos atómicos

Ecosistema de 8 productos + APIs de desarrollador + herramienta de consumo. Los campos más fiables provienen de **los OpenAPI JSON reales** (sección 3.9).

### 3.1 AutotelexPRO — sistema de tasación/intake (núcleo) [V]
App de escritorio (autotelexpro.nl) + móvil (iOS/Android, offline) + API. **€58,50/mes**, cálculos BPM ilimitados, sin coste variable. Campos/funciones:
- **Handelswaarde** (precio de compra/trade-in) fundamentado, según versión y especificaciones correctas.
- Todos los **valores incl. información BPM**.
- **Valores residuales** (restwaarde).
- **Valor actual o futuro** ("actual or future value").
- Enriquecimiento por **matrícula** → nivel de acabado (trim) + specs técnicas + opciones de fábrica.
- Valoración de **opciones instaladas por el dealer**.
- **Historia de propietarios** vía registro **NAP** (control de cuentakilómetros / odómetro).
- **Historial publicitario** (advertising history) del vehículo.
- **Informe de daños** completo (damage-report).
- **Comprobación de kilometraje** (mileage check).
- **Fotos** del vehículo en el informe + **registro de opciones** junto a fotos de vehículo/daños.
- **Firma digital** en informes.
- Gestión de tasaciones **multi-ubicación** (vestiging/holding).
- Seguimiento de **pujas** de dealers asociados (vía B2B).
- **Informes aceptados por la oficina de impuestos** (import/export); valoración aceptada **sin problemas por la Belastingdienst**.
- Gestión de stock/inventario.

### 3.2 AutotelexADS — VMS de publicación de anuncios [V]
**€50/mes** (+ €20/mes listas de stock prefabricadas). Campos/funciones:
- Anuncios online **en < 1 minuto**.
- App móvil completa.
- **Publicación con códigos OEM**.
- **Dual pricing** (doble precio).
- Fotos ilimitadas.
- Integración automática del **informe de kilometraje** (NAP).
- Inventario visible **multi-ubicación**.
- Compartir anuncios con partners.
- Diseñador de plantillas con **logo** de la empresa.
- Distribución a **cientos de portales** vía partnership **Hexon**.
- ⚠ **NO** muestra métricas de mercado (días-para-vender, price-to-market, listados comparables, índice de demanda) — confirmado por ausencia explícita.

### 3.3 AutotelexTMC = AMC — Taxatie/Appraisal Management Console [V]
Consola de gestión del proceso de occasion para sales managers (módulo dentro de PRO). TMC (NL "Taxatie Management Console") ≈ AMC (EN "Appraisal Management Console"). Campos/funciones:
- **Overview** de todas las tasaciones por vestiging o por toda la dealerholding.
- **Pujas internas y externas** (internal/external bids) entregadas al vendedor.
- **Chat integrado** vendedor ↔ sales manager.
- **Asignación de destino** del vehículo (trade/subasta/otra sucursal) con **notificación automática por email** al trader/administración/vendedor.
- Integración con **casa de subastas**.
- **Asignación de facturación** (invoicing assignments).
- **Reservas** de vehículo.
- **Pagos iDEAL** / enlaces de pago (incl. coordinación de transporte).
- **Reportes y estadísticas**: cuántos vehículos esperan puja · cuántos tasados esperan destino · cuáles NO se tasaron y **por qué** · estadísticas de conversión y eficiencia.

### 3.4 AutotelexB2B — plataforma de remarketing/pujas + app [V]
Red de trading por invitación. Por vehículo muestra:
- **Historia de propietarios** (owner history).
- **Estado de importación** (import Sí/No).
- **Galería de fotos** con zoom.
- **Factores de valor** (elementos que aumentan/disminuyen valor — increasing/decreasing).
- **Historial publicitario** por anuncio.
- **Marca, tipo de combustible, modelo, tipo de carrocería (chassis), kilometraje**.
Funciones: pujar desde la app; **push notifications** de solicitudes de puja; **historial de pujas**; perfiles de trading configurables (filtros por marca/combustible/modelo/carrocería/km); estadísticas de **conversión** y eficiencia; 3 vistas (gestión de pujas / descubrimiento de vehículos / procesamiento de pago).

### 3.5 AutotelexIMPORT — calculadora BPM / importación [V]
**€39,50/declaración (incl. IVA)**. Calcula:
- **BPM** (impuesto NL de matriculación de turismos y motos).
- **BPM-indicatie** (estimación previa).
- **Rest-BPM** (BPM residual del usado importado).
- **BPM según koerslijst** (lista de cotización/trade value, con km y opciones ajustables).
- **BPM según informe de tasación** (tegenbewijsregeling / contraprueba para vehículos dañados o con depreciación real superior).
- **Compara todos los regímenes BPM** y aplica el **método de depreciación más favorable** ("most beneficial result").
Inputs: tipo de vehículo (turismo/moto/camper) · datum eerste toelating (1ª matriculación) · marca · combustible · transmisión · modelo/uitvoering · kilometraje · opciones con precios de consumo · **RSIN** (o **BSN** para autónomos).
Output: **formulario de declaración BPM en PDF**, impreso en los papeles oficiales según directrices de Hacienda, listo para firmar. Integración **S-TAX** (registro automático de tasaciones BPM vía Autotelex). [V — bkan.nl]

### 3.6 AutotelexINRUILTOOLS — herramientas de trade-in (lead-gen web) [V]
- **Trade-in API**: el cliente final introduce su **matrícula** en la web del concesionario → solicita cotización de inruilwaarde.
- Captura de **leads** (detalles del cliente): naam (initials/first_name/infix/last_name), empresa, email, teléfono, dirección (street/house_number/postal_code/city/province/country), salutation.
- Detalles trade-in del lead: license_plate, make_model_type, make, model, type, odometer_value/unit, transmission, fuel, **price_new** (precio nuevo), date_1st_reg, buildyear, remarks, **bid**.
- Todas las tasaciones + datos del cliente se envían **automáticamente a AutotelexPRO**.
- Integración **DMS** (link al sistema de cotización del negocio).
- Partners de implementación: **Powerkraut, Bynco, UnameIT**.

### 3.7 AutotelexFLEET — valoración de flota + informes RV para OEM [V]
Valores entregados:
- **Valor actual** (current value).
- **Valor residual futuro** (future residual value).
- **Handelswaarde** (trade value).
- **Verkoopwaarde** (sales value) **con y sin IVA**.
- Valoración por **matrícula / marca-modelo-tipo / nivel de acabado**.
- Módulo **AutoToekomst**: "valor residual futuro realista" según **kilometraje + duración de contrato** sobre flotas completas.
- **Batch enrichment**: Excel con matrícula + km → enriquecido con valor actual, futuro, trade y sales value.
- Fuentes/integración: bases de **matrículas**, **JATO**, **RDC-VGS**.
- **Webservices SOAP/XML** hacia sistemas del cliente.
- **RV Reports (OEM)**: análisis del mercado NL · **cuota de mercado** competitiva · **SWOT** · **análisis por trim** · reporting pan-europeo vía DAT/L'Argus/Quattroruote.
- Asesoría declarada en about/home: "**planning and purchasing of after-market equipment**" (consejo sobre equipamiento de posventa y su impacto en valor). [V-claim — about/home]

### 3.8 AutotelexINSURANCE — feed de datos para aseguradoras [V]
- **[V-claim] El 90% de todas las pólizas de seguro de coche neerlandesas se contratan con base en datos Autotelex.** (1 fuente: su web).
- Identificación por **matrícula** o árbol **marca-modelo-tipo**.
- **Estructuración de datos crudos RDW** (clasificación ordenada).
- **Especificación de modelo precisa** (ej.: "BMW X-REIHE" → "BMW X5").
- **Clasificación de carrocería correcta** (ej.: BMW Serie 1 como hatchback aunque RDW diga station).
- **Versión/trim** (ej.: High-Executive) para precio exacto.
- **Precio de compra** (purchase price) vía datos de importador + listas de precio.
- Pipeline diario: RDW a las **07:00** → enlace de datos de importador a las **09:00** → actualización de servidor **09:30** → habilita **tender proposals** (propuestas de licitación).
- **Mensajes Audascan** personalizados por aseguradora.

### 3.9 APIs de desarrollador (catálogo atómico real, de los OpenAPI/Swagger) [V]
> Fuente más fiable. Field names verbatim.

**(a) Advertisement API** (REST, `advertisementapi.autotelexpro.nl/swagger/v1/swagger.json`). Endpoints: `GET /Vehicle/ByLicensePlate/{}`, `/ByVin/{}`, `/ByStockNumber/{}`, `/ByDmsReference/{}`, `/All`; `POST /Vehicle/CreateByLicenseplate|CreateByAtxId|CreateByMake`; `PUT /Vehicle/{Vin,Mileage,LicensePlate,ExpectedDate,DmsReference,VehicleTarget,VehicleOrigin,Price,VatMargin}`; `PATCH /Stock/SetSold|SetInStock/{}`; `GET /Establishment/All`.
- **V1VehicleModel**: establishmentId, establishmentName, stockNumber, licensePlate, vin, make, model, version, advertisementTitle, advertisementCategory, firstAdmissionDate, constructionYear, constructionMonth, mileage, mileageUnit, exteriourColor, prices, images, advertisementUrl, vatMargin, stockStatus, expectedDate, publicationDate, inStockDate, soldDate, dmsReference, isAdvertised, vehicleTarget, carOrigin, carOriginDescription, internalReference, fuelType, transmission, power, powerUnit, powerRPM, torque, torqueRPM, cylinders, displacement, brakedTowingCapacity, unbrakedTowingCapacity, weight, batteryCapacity, consumptionKwh, standardEquipment, accessories, options, packages, extOptions, extOptionsImport, consumptionCityKwh, consumptionHighwayKwh, rangeCombined, rangeElectric.
- **V1PriceModel**: amount, amountExVat, taxIncluded, priceType, countrycode, currency, currencySymbol, vatPercentage.
- **V1Option / V1Package / V1PackageOption**: optionId, description, price, optionCode, manufacturerName, selected, **increasesResidualValue**, options.
- **V1EstablishmentModel**: establishmentId, name, city, zipCode, address, email, phoneNumber.

**(b) Company Stock Valuation API** (REST, `companystockapi.autotelexpro.nl/swagger`). Entrega diaria de mutaciones in/out + **stock position, stock turn, stock value**. Endpoint `/CompanystockVehicleAppraisal`.
- **CompanystockFilter**: offset, amount, companystockType, establishmentIds, cocNumbers, vatNumbers, onlyVehiclesSelectedForFinancing, fromDateCreated, toDateCreated.
- **CompanystockVehicleAppraisal**: licenseplate, availableFrom, availableUntil, brand, model, type, consumerprice, companystockOwner, cocNumber, vatNumber, shouldBeFinanced, dateCreated, dateRegistered, appraisalDate, **tradevalue**, **tradevalueExcludingVAT**, isYellow, dateFirstRegistration, dateFirstRegistrationNL, vehicleType, rdwConstruction, rdwCoachworkDescription, companystockType, **energylabel**, **cO2Combined**, **autotelexId**, **tradeInValue**, **tradeValueExt**, transmission, power, powerUnit, displacement, standardEquipment, vin.
- **CompanystockVehicleResidualValue**: value, vatValue, **vatIncluded**, **bpmIncluded**.
- **CompanystockVehicleOption**: optionId, description, price, optionCode, manufacturerName, selected, increasesResidualValue.

**(c) Doorlinken Voorraad (DV) — inventario en web propia + entrega de leads** (`eigenwebsite.doorlinkenvoorraad.nl/docs/`). REST/JSON + SOAP/WSDL (`/v1/leads/deliver.html?wsdl`). Schemas `voorraad.xsd` / `voertuig.xsd` (versionados). Lead: key, klantnummer, voertuignr, lead{received, type, contactDetails{...}, title, message, website, tradeInDetails{license_plate, make_model_type, make, model, type, odometer_value, odometer_unit, transmission, fuel, price_new, date_1st_reg, buildyear, remarks}, more_information_link, bid}, testmode.

**(d) Webservices in-house SOAP/XML**: integran license plate info, vehicle info y valoración Autotelex en el entorno del cliente. `valuation.autotelex.nl` actúa como host de backend de valoración. [V]

### 3.10 Herramienta de consumo — dagwaarde.nl ("powered by Autotelex") [V]
- Inputs: **kenteken** (matrícula) · **km-stand** (kilometraje) · **VIN/meldcode** (13 + 4 dígitos).
- Outputs: **Dagwaarde / vervangingswaarde** (valor de día/reposición, **excl. IVA y BPM**) · **Inruilwaarde** (trade-in) · **Total Loss Value** (valor de pérdida total para siniestros).
- Entrega: pantalla + "Rapport downloaden" (PDF) + email. Contacto dagwaarde@autotelex.nl.
- "Autotelex levert auto-informatie aan de meeste autoverzekeraars, vergelijkingssites, sites van importeurs en autobedrijven."

---

## 4. Metodología y fuentes de datos [V]
- **Valoración manual experta**: "manual calculation based on many information sources" → traducida a un **porcentaje de depreciación**; equipo de especialistas como estándar de industria.
- **Red multifuente** (declarada repetidamente): concesionarios · mayoristas (handelaren) · importadores · empresas de leasing (devoluciones) · aseguradoras · bancos · **resultados de subasta** (auction proceeds) · **portales de occasions** (clasificados de internet) · **pujas internas** (internal bids).
- **Precio nuevo ponderado** según equipamiento estándar; relación verkoopwaarde↔handelswaarde "constantly monitored and tested against current market information".
- Datos técnicos/specs: **JATO**, **RDC-VGS**, **RDW** (registro oficial NL, actualización diaria 07:00), datos de **importador** (listas de precio).
- **Frecuencia**: feed aseguradoras **diario** (pipeline 07:00/09:00/09:30); APIs de stock con **mutaciones diarias**; **marktupdate mensual** (blog).
- **Opciones con flag `increasesResidualValue`**: impacto granular del equipamiento en el valor residual.

---

## 5. Entrega
[V] Modalidades:
- **App web** (AutotelexPRO.nl, AutotelexADS) + **apps móviles** (PRO offline, ADS, B2B; iOS/Android).
- **APIs REST** (Swagger/OpenAPI): Advertisement API, Company Stock Valuation API.
- **SOAP/XML Webservices** in-house (valoración, license plate, vehicle info; WSDL) — host `valuation.autotelex.nl`.
- **Doorlinken Voorraad**: data link a la web propia del dealer + **entrega de leads** (REST/JSON + SOAP).
- **Batch**: Excel (Fleet enrichment) en formato preferido, periódico.
- **Integración DMS / CRM / ERP**.
- **PDF**: informe de tasación, declaración BPM oficial, informe dagwaarde.
- **Distribución a portales** vía Hexon (ADS).
- **Mensajes Audascan** (aseguradoras).

---

## 6. Precio
- **Parcialmente público** (raro en el sector; el resto de competidores no publican nada):
  - **AutotelexPRO: €58,50/mes** (BPM ilimitado, sin coste variable). [V]
  - **AutotelexADS: €50,00/mes** (+ €20,00/mes listas de stock). [V]
  - **AutotelexIMPORT: €39,50/declaración (incl. IVA)**. [V]
- **No público**: Fleet, Insurance, B2B, APIs de datos, RV Reports OEM → cotización vía contacto/account manager. [V que no es público]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla → dato.

### AutotelexPRO — pantalla de tasación/intake [V]
- **Input matrícula** (arriba) → enriquecimiento automático: trim + specs + datos RDW + **NAP** (control odómetro) + **historia de propietarios** + **historial publicitario**.
- **Bloque de valores**: handelswaarde (trade-in) · verkoopwaarde (sales) · restwaarde actual + futura · **toda la info BPM**.
- **Sección de opciones/equipamiento**: cada opción/paquete con flag de si **aumenta valor residual**.
- **Sección de daños**: damage-report compilado.
- **Fotos + registro de opciones** junto a fotos de vehículo/daños.
- **Firma digital** → **informe PDF aceptado por Hacienda**.

### AMC/TMC — consola del sales manager [V]
- **Lista overview** de tasaciones a nivel vestiging/holding.
- **Panel de pujas internas** entregadas al vendedor + **chat** integrado.
- **Asignación de destino** (trade/subasta/sucursal) con notificación automática.
- **Enlace de pago iDEAL** (+ transporte).
- **Vista de reportes**: esperando-puja · tasado-esperando-destino · no-tasado + motivo · conversión/eficiencia.

### AutotelexB2B — app de remarketing [V]
- **3 vistas**: gestión de pujas / descubrimiento / pago.
- **Tarjeta por vehículo**: galería con zoom · historia de propietarios · import Sí/No · **factores de valor (+/–)** · historial publicitario · marca/combustible/modelo/carrocería/km.
- **Filtros/perfil de trading** (marca, combustible, modelo, carrocería, km).
- **Push notifications** de pujas + historial + stats de conversión.

### AutotelexADS — editor de anuncio [V]
- **Editor**: códigos OEM · dual pricing · fotos ilimitadas · plantilla con logo · informe km automático.
- **Lista de inventario multi-ubicación** → **distribución a cientos de portales (Hexon)** en < 1 min.
- (Sin panel de métricas de mercado competitivo.)

### AutotelexIMPORT — formulario BPM [V]
- **Formulario de input** (tipo, datum eerste toelating, marca/combustible/transmisión, modelo/uitvoering, km, opciones).
- **Comparador de regímenes BPM** → muestra el **resultado más favorable** (rest-BPM, koerslijst vs tasación).
- **Output**: declaración BPM en **PDF oficial** lista para firmar.

### Widget Trade-in (web del concesionario) [V]
- **Campo matrícula** embebido → cotización inruilwaarde → **formulario de lead** (nombre/empresa/email/teléfono) → ruteado a PRO/DMS.

### AutotelexFLEET — entrega batch/OEM [V]
- **Excel in → columnas enriquecidas out** (valor actual/futuro/trade/sales).
- **AutoToekomst**: valor futuro por km + duración de contrato.
- **Informe OEM**: cuota de mercado · SWOT · análisis por trim · benchmark pan-EU.

### AutotelexINSURANCE — backend feed [V]
- **Pipeline temporizado** (07:00/09:00/09:30) → datos RDW estructurados + importador + clasificación trim/carrocería → **tender proposals** + **mensajes Audascan** por aseguradora.

### dagwaarde.nl — consumidor [V]
- **Formulario de 3 campos** (kenteken/km/VIN) → **dagwaarde + inruilwaarde + total loss** en pantalla + PDF/email.

### Marktupdate mensual (news/blog) [V]
- **Agregados de mercado NL**: tendencia de nº de **taxaties y biedingen** · cuota EV de nuevas ventas (ej. 49% nov-2025) · volúmenes import/export (import +8% ~300k; export +11% ~120k) · "los niveles de restwaarde se mueven poco". (Sin price-to-market ni days-to-sell por vehículo.)

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **EL estándar de facto neerlandés**: las valoraciones se **aceptan sin problema por la Belastingdienst** y **[V-claim] el ~90% de los seguros de coche NL** se basan en datos Autotelex. Autoridad fiscal+aseguradora difícil de replicar por un extranjero.
- [V] **Especialización BPM/importación profundísima**: rest-BPM, koerslijst vs tegenbewijsregeling, comparación de **todos los regímenes** al más favorable, **PDF oficial de Hacienda**, integración **S-TAX**. Nicho regulatorio NL casi inexpugnable.
- [V] **Stack end-to-end del proceso de occasion en un solo proveedor**: datos → tasación (PRO) → consola de trade (TMC/AMC) → **marketplace B2B transaccional con pujas** → import/BPM → lead-gen trade-in → flota → feed aseguradoras → embudo de consumo (dagwaarde.nl).
- [V] **Marketplace B2B real con pujas** (no solo datos): push, historial de pujas, perfiles de trading, iDEAL, conversión — la mayoría de competidores de pura valoración no transaccionan.
- [V] **Flag `increasesResidualValue` por opción/paquete**: impacto granular del equipamiento en valor residual, expuesto en API y en PRO.
- [V] **Integración nativa RDW + NAP + importador** (estructuración y corrección de specs/carrocería que el propio RDW no da bien).
- [V] **APIs REST modernas (Swagger/OpenAPI) coexistiendo con SOAP** + Doorlinken Voorraad para web propia del dealer.
- [V] **Precio SaaS transparente** (PRO €58,50 / ADS €50 / Import €39,50) — inusual en el gremio.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Cobertura geográfica = NL.** Lo pan-europeo es **datos de terceros** (DAT/L'Argus/Quattroruote), no propios.
- [V] **Sin analítica de mercado de listados en vivo como métricas nombradas**: no hay **price-to-market %**, ni **days-to-sell / market days supply por vehículo**, ni **índice de demanda/oferta**. Lo más cercano es **stock turn/position/value** a nivel de stock de dealer (Company Stock API) y agregados mensuales del blog. **Hueco grande vs Eurotax Market Radar y players US.**
- [V] **Sin historial de siniestros/accidentes tipo Carfax por VIN**: tienen NAP (odómetro), historia de propietarios, WOK e importmeldingen, pero el **informe de daños es manual** en PRO, no una BBDD de accidentes.
- [V] **Precio no público** para Fleet/Insurance/B2B/APIs/RV-Reports (solo los 3 SaaS SMB).
- [A] **Owner/estructura accionarial opaca** (KvK paywall; señales hacia "Kovi Specials B.V." / "Nenova IT B.V." sin confirmar).
- [V] **Sin BBDD de especificaciones pan-EU propia**: depende de **JATO / RDC-VGS / RDW**.
- [A] **Metodología parcialmente manual** ("manual calculation… depreciation %") frente a modelos estadísticos/ML de competidores.
- [A] **Doc de API sin auth/rate-limits públicos**; SOAP legacy aún central en valoración.
- [A] **Curva de depreciación / histórico multi-año** no expuesto como dato vendible explícito (sí "valor en el pasado/futuro" en PRO, pero sin serie histórica publicada).

---

## 10. Fuentes (URLs)
- https://autotelex.nl/ y https://autotelex.nl/en/ — home, tagline, nav, "since 1964", scope vehículos.
- https://autotelex.nl/en/pro/ — AutotelexPRO (campos, €58,50, BPM, NAP, daños, firma).
- https://autotelex.nl/en/ads/ — ADS (€50, OEM codes, dual pricing, Hexon; ausencia de métricas de mercado).
- https://autotelex.nl/en/tmc/ y https://autotelex.nl/en/amc/ — Taxatie/Appraisal Management Console (pujas, chat, destino, iDEAL, reportes).
- https://autotelex.nl/en/b2b/ — B2B (factores de valor, owner history, import, conversión, 3 vistas).
- https://autotelex.nl/en/import/ y https://autotelex.nl/auto-import/ — BPM (rest-BPM, koerslijst, tegenbewijsregeling, €39,50, RSIN/BSN, PDF oficial).
- https://autotelex.nl/en/trade-in-tools/ — trade-in API, leads, DMS, partners Powerkraut/Bynco/UnameIT.
- https://autotelex.nl/en/fleet/ — Fleet (valor actual/futuro/trade/sales, AutoToekomst, JATO/RDC-VGS, RV Reports OEM, DAT/L'Argus/Quattroruote).
- https://autotelex.nl/en/insurance/ — Insurance (90% pólizas NL, pipeline 07:00/09:00/09:30, Audascan, tender proposals).
- https://autotelex.nl/en/our-values/ — metodología/clientes.
- https://autotelex.nl/en/about-autotelex/ — historia 1964.
- https://autotelex.nl/en/autotelex-for-developers/ — APIs (Advertisement, Company Stock, Doorlinken Voorraad, SOAP/XML).
- https://advertisementapi.autotelexpro.nl/swagger/v1/swagger.json — **OpenAPI real** (V1VehicleModel y schemas, field names verbatim).
- https://companystockapi.autotelexpro.nl/swagger/v1/swagger.json — **OpenAPI real** (CompanystockVehicleAppraisal/ResidualValue/Option; stock turn/position/value).
- https://eigenwebsite.doorlinkenvoorraad.nl/docs/ — lead/trade-in API (campos de lead y trade-in).
- https://autotelex.nl/restwaarde-berekenen-auto/ , /restwaarde-berekenen/ , /auto-zakelijk-taxeren/ — verkoopwaarde/handelswaarde/inruilwaarde, dagwaarde, Belastingdienst, NAP, eigenarenhistorie, WOK, importmeldingen.
- https://autotelex.nl/workflow-autobedrijf/ y /vms-systeem/ — ecosistema PRO→ADS→TMC→B2B→Import.
- https://autotelex.nl/autotelex-marktupdate-december-2025/ — agregados de mercado mensuales (EV share, import/export, taxaties/biedingen).
- https://dagwaarde.nl/ — herramienta de consumo (kenteken/km/VIN → dagwaarde/inruilwaarde/total loss).
- https://www.bkan.nl/s-tax-gaat-bpm-taxaties-automatisch-registreren-via-autotelex/ — integración S-TAX/BPM.
- https://cube.nl/en/connections-integrations/autotelex y https://www.carcollect.com/integrations/autotelex — uso como proveedor de valores NL.
- https://companyinfo.nl/...autotelex-b-v-arnhem-09045121-000016220358 — KvK 09045121, SBI, "Kovi Specials B.V." en gestión.
- https://nl.linkedin.com/company/autotelex-bv — 11–50 empleados, "particuliere onderneming", specialties.
- https://www.fleet.be/fiche-fib/autotelex-b-v/ (403), https://www.dnb.com/.../autotelex_bv... , https://www.zoominfo.com/c/autotelex-bv/372869994 , https://tracxn.com/.../auto-telex/... — perfiles corporativos (Arnhem, 1964).

> Verificación: identidad (1964, Arnhem, KvK, BPM/Belastingdienst, fuentes de datos) cruzada con ≥2 fuentes. **Catálogo de campos = leído directamente de los OpenAPI JSON reales** (máxima fiabilidad). Owner/matriz y "90% seguros NL" marcados [A]/[V-claim] por fuente única; no inventados.
