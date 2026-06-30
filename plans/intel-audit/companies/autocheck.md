# AutoCheck (by Experian) — Auditoría atómica

> **slug:** `autocheck` · **subdominio de audit:** `vin-history` · **web:** https://www.autocheck.com (consumer) · https://www.experian.com/automotive/autocheck-business (B2B)
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; **[V]** = verificado leyendo la fuente · **[NV]** = no verificado / inferido (marcado siempre). Nada inventado.
> **Veredicto express:** AutoCheck **NO es una guía de valoración** (no es KBB/Black Book/cap): es el **informe de historial de vehículo por VIN** de **Experian Automotive**, el **#2 del duopolio US de vehicle-history frente a Carfax**. Su arma única y patentada (**US Patent 8,005,759**) es el **AutoCheck Score® (1-100) + Score Range**, un índice que resume el historial y **predice la probabilidad de que el coche siga circulando en 5 años**, comparándolo contra coches de su misma **edad y clase**. Diferencial duro: **anuncios exclusivos de las dos mayores subastas US (Manheim/ADESA)** + **98.86% de cobertura de auction houses** + **Buyback Protection** (recompra si se escapa un title brand estatal). Cobertura **solo EE.UU.** (50 estados + DC). Entrega: **informe web/PDF por VIN o matrícula US**, **API/integración B2B**, y **embebido** en KBB, Cars.com, CarGurus, eBay Motors, Edmunds, AutoTrader, TrueCar, CarZing. Modelo consumer: **$29.99 / informe**, **$59.99 / 5 informes-21 días**.
> **Patrón a copiar por cardeep:** (1) el **"Vehicle History at a Glance"** — rejilla de 9 tiles tipo semáforo (Issue Found / No Issue / Severe) como resumen-cabecera; (2) el **AutoCheck Score + Score Range** como índice único que jerarquiza todo el dossier; (3) el **Detailed Vehicle History** como **timeline cronológico agrupado por dueño** con columnas `Event Date | Location | Odometer | Data Source | Details`.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca de producto | **AutoCheck®** / **AutoCheck by Experian** / **Experian AutoCheck Report** | [V — header del informe, autocheck.com] |
| Operador | **Experian Automotive** (división de automoción de Experian) | [V — autocheck.com, experian.com/automotive] |
| Grupo / owner | **Experian plc** — "global leader in information services" | [V — backed-by-experian, Wikipedia] |
| Cotización del grupo | **London Stock Exchange `EXPN`**, constituyente **FTSE 100**; demerge de **GUS** y salida a bolsa **oct-2006** | [V — Wikipedia/Experian plc] |
| HQ corporativo grupo | **Dublín, Irlanda**; HQ operativos: **Costa Mesa, CA (Norteamérica)** y **Nottingham, UK** | [V — experian corporate locations] |
| Marca "Experian" | Creada en **1996** (fusión CCN Group de GUS + TRW Information Systems & Services); linaje GUS data de **1826** | [V con matiz — Wikipedia; "1826" = linaje GUS, no Experian-info] |
| Dirección AutoCheck (footer informe) | **Experian Automotive C/O AutoCheck Customer Service, 1515 E. Woodfield Road, Suite 500, Schaumburg, IL 60173** | [V — footer del informe + T&C] |
| HQ de la entidad AutoCheck | **Costa Mesa, CA**; oficinas adicionales **Schaumburg, IL** y **Skokie, IL** | [V — BBB profile] |
| Fundación / inicio AutoCheck | **Incorporada 30-oct-1996**, **inicio de actividad 03-may-1999** (BBB). Su propia página (~2016) dice "debuted over 10 years ago" | [V con discrepancia — BBB vs autocheck-vs-carfax] |
| Soporte | **AutoChecksupport@experian.com** · **888-409-2204** | [V — autocheck-business] |
| Contacto comercial | **1-888-409-2204** | [V — NMVTIS page] |
| Copyright vigente | **© Experian 2026. All rights reserved.** | [V — footer autocheck.com] |
| Patente clave | **U.S. Patent No. 8,005,759** (cubre aspectos del AutoCheck Score) | [V — patent notice del informe] |

**Qué es:** servicio de **informe de historial de vehículo (Vehicle History Report, VHR) por VIN** orientado a **vehículo USADO** en **EE.UU.**, equivalente categórico de **Carfax**. No produce valoraciones/precios propios (se apoya en NADAguides para la fórmula de recompra). Su núcleo es el **dato de historial agregado** (títulos, daños, odómetro, eventos) + el **AutoCheck Score** patentado.

### Categorías de producto / negocio [V]
1. **AutoCheck consumer** (informe por VIN/matrícula, web + dashboard).
2. **AutoCheck for Business / Dealerships** (membresías, ilimitado, API/integración).
3. **AutoCheck for Lenders** (riesgo de préstamo, LTV, Score en originación).
4. **AutoCheck for Insurers / Manufacturers / Auctions / Credit Unions** (paquetes B2B).
5. **NMVTIS reports** (Experian es **approved NMVTIS data provider** / revendedor; informe federal de título a dealers).
6. **Embebido / co-branded** en marketplaces y guías (KBB, Cars.com, CarGurus, eBay Motors, Edmunds, AutoTrader, TrueCar, CarZing).

### Clientes objetivo (segmentos declarados) [V]
Consumidores (compra/venta de usado) · **Concesionarios** (acquisition + cesión al cliente) · **Lenders / financieras / credit unions** · **Aseguradoras** · **Fabricantes (OEM) + programas Certified Pre-Owned** · **Subastas de coches** (Manheim, ADESA y otras) · **Portales/guías** que revenden el informe.

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía | **EE.UU. exclusivamente** — title & registration data de **los 50 estados + el Distrito de Columbia** | [V — autocheck-vs-carfax, autocheck-score] |
| Búsqueda por matrícula | **US License Plate** con selector de los **50 estados** (sin internacional) | [V — subscription-benefits / order page] |
| Internacional | **No** (sin cobertura fuera de EE.UU.; vehículos importados aparecen vía import/export sources, no como cobertura de país) | [NV explícito — no se observa ningún mercado no-US] |
| Escala BBDD (footer informe) | **"over 4 billion records on a half a billion vehicles"** (>4.000M registros sobre ~500M vehículos) | [V — footer del informe] |
| Escala BBDD (otra cifra Experian) | **North American Vehicle Database ≈ 700M vehículos** | [V — búsqueda Experian Automotive] |
| Cobertura subastas | **98.86% U.S. Auction House coverage** (business) · **"Data from 95% of all U.S. auction houses"** (order page) · **"over 95%"** (lenders) | [V — business / order / lenders] |
| Anuncios exclusivos | **"329M vehicles on the road with exclusive auction announcements"** | [V — autocheck-business] |
| Daño estructural | **Structural damage information on 4.5M vehicles** | [V — autocheck-business] |
| Fuentes de accidente | **"tens of thousands of distinct accident sources"** (la mayoría exclusivas de Experian) | [V — business / lenders / order] |
| Accidentes policiales | **Police-reported accident information disponible para los 50 estados + DC** | [V — autocheck-score] |
| Recalls (OEM) | **82% manufacturer coverage of open recall data** para coches en circulación | [V — búsqueda NMVTIS] |
| Tormentas | Datos de vehículos en **zonas de daño por tormenta declaradas por FEMA** en eventos mayores | [V — autocheck-score] |

### Scope de vehículo [V]
- **USADO** (used car) como caso de uso central; aplica también a CPO y a venta dealer.
- Tipos: **coches y light trucks / pickups** (la propia explicación del Score contrasta "compact cars" vs "pickup trucks"). **No** se observan moto/RV/heavy-equipment como verticales separadas.
- Granularidad: **por VIN** (17 dígitos) o **por matrícula US + estado** (plate→VIN).
- Histórico: desde matriculación/eventos del vehículo; el informe es **dinámico** (acceso a *dynamic vehicle data updates* durante 21 días en consumer).

---

## 3. Productos + campos atómicos

> El esquema atómico de campos se extrae del **informe real renderizado** (sample 2015 Acura TLX V6) + glosario embebido + página "Data Backed by Experian". Es la fuente de verdad del schema.

### 3.1 AutoCheck Vehicle History Report — el informe (producto núcleo) [V]
Estructura **verificada** del informe, sección por sección:

**(A) Cabecera de identidad del vehículo**
- `Report Run Date` (fecha/hora, p.ej. "02/10/20XX 13:51:14 EST")
- `Year` · `Make` · `Model` · `Trim/Version` (p.ej. "2015 Acura TLX V6")
- `Body Style` (p.ej. "Sedan 4D")
- `Engine` (p.ej. "3.5L V6 DI Gasoline") · `Fuel Type`
- `VIN`
- `Class` (segmento, p.ej. "Car - Compact Luxury")
- `Country of Assembly`
- `Vehicle Age` (en años)
- `Last Reported Odometer` (valor + fecha)

**(B) Bloque de propiedad / uso**
- `Number of Owners` (p.ej. "Owners - 2")
- `Vehicle Usage` / `Owner Type` — valores: **Personal, Fleet, Rental, Lease, Taxi, Livery, Police, Government, Drivers Ed, Commercial** [V glosario/usos]

**(C) AutoCheck Score® (ver 3.2)** — `AutoCheck Score` (1-100) + `Score Range` (low–high para edad/clase similares)

**(D) Vehicle History at a Glance** — rejilla de **9 tiles** tipo semáforo, cada uno con estado (`Issues Found` / `No Issue` / `Severe` / `Events Reported` / icono alert/warning/success):
1. `State Title Brand` (p.ej. "Multiple State Title Brands")
2. `Auction Brand / Issues`
3. `Accident / Damage` (p.ej. "Multiple Damage Events" + severidad)
4. `Open Recall Check` (nº de open recalls)
5. `Insurance Loss / Transfer`
6. `Odometer Check` (+ last reported odometer)
7. `Certified Pre-Owned` (CPO info)
8. `Service / Repair`
9. `Additional History` (p.ej. "Corrected Title")

**(E) Buyback Protection banner** — elegibilidad del vehículo (eligible / not eligible) + Terms & Conditions (ver 3.4)

**(F) Accident & Damage** — diagrama del coche con `Point of Impact (POI)` + indicadores `Airbag Deployed`, `Structural Damage`, `Overturned`, `Severe`; tabla con columnas:
- `Damage Date` · `Damage Type` (p.ej. Collision) · `Severity` (Minor / Moderate / Severe / Unknown)

**(G) Open Recall Check** — tabla:
- `Recall Date` · `Recall Type` (Safety / Emission) · `Mfr. Recall No.` · `Campaign Description` · `Status` (p.ej. "Remedy Available"); enlace a NHTSA + dealer OEM

**(H) Recommended Maintenance** — `OEM Recommended Maintenance Schedule` por intervalos de millaje (p.ej. "70000 Mile Service") con items (`Maintenance Minder`), estado `Not Yet Due`

**(I) Odometer Check** — veredicto `Problem Reported` / OK + 3 sub-chequeos:
- `State Title Odometer Check` (brands del DMV)
- `Auction Odometer Check`
- `Odometer Calculation Check` (secuencia de lecturas)

**(J) Detailed Vehicle History** — **timeline cronológico agrupado** por `Vehicle Prep and Other Pre-Titling Events` → `Owner 1` → `Owner 2`…; por dueño: `Location`, `Owned From` (mm/aaaa), `Usage`; tabla de eventos:
- `Event Date` · `Location` (city, ST) · `Odometer` · `Data Source` · `Details`

**(K) Warranty Check** — estimación por in-service date + millaje; tabla:
- `Coverage Type` (Basic, Battery, Corrosion, Powertrain, Roadside Assistance, Safety Restraint) · `Remaining Miles` · `Remaining Time` · `Status` (Coverage active / expired) · `Coverage Details` (term/miles)

**(L) This Vehicle's Glossary** — tabla `Term | Section Location | Definition` con definiciones de todos los términos del informe.

**(M) Footer legal** — Terms & Conditions, Buyback T&C, "About AutoCheck" (>4.000M registros / ~500M vehículos), Patent Notice (8,005,759).

### 3.2 AutoCheck Score® — índice patentado (el diferencial) [V]
**Qué es:** índice **1-100** que resume el historial y permite **comparar vehículos de edad y clase similares**; predice la **probabilidad de que el vehículo siga en circulación a 5 años** (patente 8,005,759). Se lee **siempre junto al Score Range** (ej.: Score 84 con range 76-81 = favorable; Score 89 con range 90-95 = desfavorable).
**Campos:**
- `AutoCheck Score` (1-100)
- `AutoCheck Score Range` (banda esperada para misma make/model/age/class)
**Inputs / factores del modelo (verbatim):**
- `Age` (más viejo → score más bajo)
- `Vehicle Class` / segment (compact vs pickup → distinto historial de averías)
- `Mileage`
- `Number of Owners` (más de lo esperado → baja)
- `Vehicle Use and Events` (taxi use, accidents, repossession, theft)
**Factores que penalizan el Score (verbatim):** `Accidents` · `Mileage` · `Title brands (salvaged/rebuilt)` · `Odometer problems (rollback/broken)` · `Frame damage` · `Water damage` · `Lemon brand` · `Stolen or repossessed` · `Police or taxi use`.

### 3.3 Catálogo atómico de TITLE BRANDS y EVENTOS chequeados [V]
**State Title Brands** (caja "State Title Brand"): `Fire` · `Hail` · `Flood` · `Storm` · `Junk/Scrapped` · `Lemon` (manufacturer buyback) · `Salvage` · `Rebuilt/Rebuildable` · `Dismantled/Reconstructed` · `Water damage`. (`Grey Market` e `Insurance Loss/Theft` se chequean en otras cajas.)
**Odometer Brands:** `Not Actual Miles (NAM)` · `Broken Odometer` · `Exceeds Mechanical Limits` · `Mileage Discrepancy` · `Suspect Miles` · `Rollback/Rollover/Tampering`.
**Accident / Damage:** `Collision damage` · `Police-reported accident` · `Salvage auction` · `Recycler records` · `Crash test vehicle` · `Collision damage claim` · `Structural / Frame damage` · `Airbag deployed` · `Overturned` · `Point of impact` · `Severity` · daños no-colisión (`Fire`, `Hail`, `Flood`).
**Insurance Loss / Transfer:** `Insurance Total Loss` · `Reason for loss` · `Vehicle sold by insurer` · `Title transferred to insurer name`.
**Additional History:** `Abandoned` · `Grey Market` · `Lien check / Lien information` · `Repossessed` · `Theft / Stolen vehicle records` · `Theft recovery` · `Corrected Title` · `Ownership transfers`.
**Auction Issue:** disclosure de daño del vendedor, structural damage disclosure, title brands, odometer issues (según **NAAA Arbitration Policy**), incl. **exclusive auction announcements** de 2 grandes subastas.
**Otros eventos del timeline:** `Title (Title #)` · `Registration Event/Renewal` · `Leased Vehicle` flag · `Vehicle Prep / Pre-Titling` · `Open Recall` · `Certified Pre-Owned` · `Courtesy buyback` · `Emissions record` · `Safety inspection` · `Geographic location` (city/state).

### 3.4 Buyback Protection — póliza de recompra (diferencial) [V]
**Qué es:** garantía **gratuita** sobre vehículos cualificados y registrados: si el informe AutoCheck **se saltó un title brand estatal** que el estado había reportado a Experian **antes** de correr el informe, Experian **recompra el vehículo**.
**Campos / términos atómicos:**
- **Title brands cubiertos:** `Junk or salvage` · `Dismantled, rebuilt, or reconstructed` · `Flood damage` · `Hail damage` · `Fire damage` · `Manufacturer buyback ("lemon law")` · `Odometer exceeds mechanical limits` · `Odometer not actual mileage`
- **Compensación:** hasta **110% del valor retail publicado en NADAguides.com** **+** hasta **$500 en accesorios aftermarket**
- **Registro:** dentro de **90 días** de la compra
- **Regla del brand:** el branded title debió emitirse **≥60 días antes** de correr el informe
- **Ventana de reclamación:** **1 año** desde la fecha de run del informe; acuse en **2 días hábiles**; revisión **4-6 semanas**
- **Exclusiones:** **solo** state-reported title brands; **NO** cubre accidentes ni records de fuentes comerciales

### 3.5 AutoCheck for Dealers / Business [V]
- Membresías **flexibles**: **ilimitado** (con perks: open recall reports, vehicle listings, unlimited integrations, dedicated account manager) o **mensual** (dealers/grupos pequeños).
- Datos exclusivos: **auction announcements**, structural damage (4.5M), **98.86% auction coverage**, AutoCheck Score.
- Integración en plataformas de shopping (ver §5) + **API access**.

### 3.6 AutoCheck for Lenders [V]
**Qué es:** gestión de riesgo en el ciclo del préstamo de auto. Campos / usos:
- `AutoCheck Score` para decisión de originación y **LTV thresholds**
- "Reduce risk by more accurately estimating a vehicle's value before originating a loan"
- "Price the loan more accurately"; "set thresholds for loan-to-value pricing"
- Identificación de `frame damage` y `title brands` → impacto de **"30% or more"** sobre el valor
- Base: **"billions of vehicle history records"**, **95%+ auction houses**, "4 de cada 10 coches han tenido un accidente"

### 3.7 NMVTIS reports (revendido) [V]
- Experian = **approved NMVTIS data provider**; informe federal de título a **dealers** (no a consumidores).
- **Precio: $0.43 / NMVTIS report**; "no minimum volume, no commitment"; un solo user ID/invoice/website para NMVTIS + AutoCheck; foco compliance (p.ej. **California NMVTIS**).

### 3.8 Herramientas / utilidades de consumidor [V]
- `Search by VIN` · `Search by US License Plate (+ estado)`
- `Dashboard` (guardar, comparar, seleccionar) + **Free Digital Dashboard Delivery**
- `Flood Risk Check` (herramienta de riesgo de inundación)
- Guías: How to Buy a Used Car, What is a VIN, VIN Decode Explained, Odometer Fraud, Title Brands, Glossary.

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Operación | Agregación de **muchas fuentes** bajo las "expert business rules" de Experian | [V — backed-by-experian] |
| Score | Modelo **estadístico patentado** (US 8,005,759); inputs age/class/mileage/owners/use/events; output 1-100 + Range; target = on-road @ 5 años | [V — autocheck-score + búsqueda] |
| Frecuencia | Informe **dinámico**; consumer incluye *dynamic vehicle data updates* (21 días) | [V — order page] |

### Taxonomía de fuentes (12 categorías, verbatim de "Data Backed by Experian") [V]
1. **State DMVs** → branded titles (salvage/junk, flood, hail, storm, fire), manufacturer buybacks/lemon, odometer rollback/NAM, city/state de matriculación previa, nº de owners, accidents & damage, stolen, uso rental/taxi/lease/government, lien info, ownership transfers.
2. **Auto auctions** → low odometer readings, structural/frame damage.
3. **Salvage auctions** → salvaged, junked/recycled (aunque el DMV no lo titulara salvage).
4. **Collision repair shops** → collision repair history, structural/frame damage.
5. **Service & maintenance facilities** → servicios/reparaciones realizados, odometer readings, fechas y ubicaciones.
6. **Insurance companies** → total loss + reason for loss, stolen.
7. **Manufacturers (OEM)** → open recalls, CPO vehicles, courtesy buybacks.
8. **Law enforcement** → stolen records + theft recovery, accident reports.
9. **Car dealerships & extended warranty** → geographic location, odometer, repair/maintenance history.
10. **Import/export companies** → vehicle transfers & locations.
11. **Rental & fleet companies** → total loss + damage history, maintenance/service.
12. **Vehicle inspection & state inspection stations** → odometer, ubicación, emissions records, safety inspection factors.
+ **NMVTIS** (federal), **NHTSA** (recalls), **FEMA** (zonas de tormenta), y **"tens of thousands of distinct accident sources"** mayoritariamente **exclusivas** de Experian, + **exclusive auction announcements** de las **2 mayores subastas US** (Manheim/ADESA por contexto).

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Web consumer** | autocheck.com — informe online + **dashboard** (SPA) por VIN o matrícula | [V] |
| **PDF / informe** | Informe estructurado descargable/compartible (dealers lo entregan al cliente) | [V] |
| **API / integración** | "available through integrations and API access"; **unlimited integrations** en plan ilimitado | [V — autocheck-business] |
| **Embebido / co-branded** | **Cars.com, CarGurus, KBB (Kelley Blue Book), eBay Motors, Edmunds, AutoTrader, CarZing, TrueCar** (business 2026); histórico: NADAguides, CarMax | [V — autocheck-business + autocheck-vs-carfax] |
| **Partnership 2025** | **Kelley Blue Book + Experian** (Cox Automotive) para mejorar VHR al comprador | [V — KBB mediaroom / Cox jun-2025] |
| **CPO / OEM** | Opción de VHR en programas **Certified Pre-Owned** (p.ej. Jaguar Land Rover NA, 2011) | [V — experianplc press] |
| **Dealer portal** | members/login.do; one user ID/invoice/website (AutoCheck + NMVTIS) | [V] |
| **Búsqueda** | por **VIN** o por **US License Plate + estado** (plate→VIN) | [V] |
| **Frecuencia datos** | dynamic updates 21 días (consumer) | [V] |

---

## 6. Precio

| Plan | Precio | Detalle | Estado |
|---|---|---|---|
| **Single Report** | **$29.99** | 1 informe, VIN o matrícula US, **21 días** de dynamic updates, pago único sin recurrencia | [V — order page live] |
| **5 Reports / 21 Days** | **$59.99** | 5 informes durante 21 días, dynamic updates durante el término, pago único | [V — order page live] |
| **AutoCheck for Business** | quote / membresía | Paquetes dealers/lenders/insurers/manufacturers/auctions/credit unions; ilimitado o mensual | [V — order + business] |
| **NMVTIS report** | **$0.43** | Para dealers; sin mínimo ni compromiso | [V — NMVTIS page] |
| Buyback fórmula | hasta **110% NADAguides retail + $500** accesorios | (no es precio de venta; es la compensación de la póliza) | [V] |

> **Discrepancia de precio histórico:** búsquedas de terceros citan $24.99 single y paquetes hasta $99.99 (incl. un viejo "25 reports"); la **página viva** (jun-2026) muestra **$29.99 / $59.99 (5 reports)** — tomo el dato vivo como autoridad y marco lo demás como histórico/revendedor. [V vivo vs NV terceros]

---

## 7. Placement — dónde coloca cada dato en su UI (patrón a copiar por cardeep)

> Mapeo pantalla/sección → dato, extraído del informe renderizado. **Es el blueprint de la ficha de coche + timeline de cardeep.**

| Dato | Dónde lo coloca AutoCheck |
|---|---|
| Identidad del vehículo (year/make/model/trim/VIN/class/engine/age/last odometer) | **Cabecera** del informe, bloque izquierdo |
| `Number of Owners` + `Vehicle Usage` | **Tarjeta de cabecera** central (con icono de owners) |
| **AutoCheck Score + Score Range** | **Tarjeta de cabecera derecha**, dial gráfico ("Similar vehicles usually range between X and Y") — el elemento dominante |
| Resumen de problemas (title/auction/accident/recall/insurance/odometer/CPO/service/additional) | **"Vehicle History at a Glance"** — rejilla de **9 tiles semáforo** justo bajo la cabecera |
| Elegibilidad Buyback Protection | **Banner dedicado** tras el "at a Glance" |
| Accidentes/daño (POI, airbag, structural, severity) | Sección **"Accident & Damage"** con **diagrama del coche** + tabla `Date/Type/Severity` |
| Open recalls | Sección **"Open Recall Check"** con tabla + enlace NHTSA/dealer |
| Mantenimiento OEM por millaje | Sección **"Recommended Maintenance"** (intervalos + Maintenance Minder) |
| Veredicto odómetro (3 sub-chequeos) | Sección **"Odometer Check"** (State Title / Auction / Calculation) |
| **Cronología completa de eventos** | Sección **"Detailed Vehicle History"** — **timeline agrupado por dueño** con `Event Date / Location / Odometer / Data Source / Details` |
| Garantía restante | Sección **"Warranty Check"** — tabla por `Coverage Type` con remaining miles/time/status |
| Definiciones | Sección **"This Vehicle's Glossary"** (Term / Section Location / Definition) |
| Legal / escala BBDD / patente | **Footer** (About AutoCheck, Patent Notice 8,005,759, T&C) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **AutoCheck Score® patentado (US 8,005,759)** — índice 1-100 + Score Range que **predice on-road @ 5 años** y normaliza por **edad y clase**. Carfax **no** tiene índice numérico equivalente. Es el activo único de la marca.
2. **Anuncios exclusivos de subasta** — *exclusive auction announcements* de las **dos mayores subastas US** (Manheim/ADESA), con structural/frame damage disclosado en subasta. **98.86% de cobertura de auction houses**; ventaja reconocida vs Carfax en **historial de subasta y título**.
3. **Buyback Protection** — recompra (110% NADAguides retail + $500) si se escapa un title brand estatal. Garantía contractual poco común.
4. **Backed by Experian** — misma infraestructura/"business rules" que el gigante de información/credit; **>4.000M registros / ~500M (–700M) vehículos**.
5. **Score como herramienta de riesgo B2B** — lenders lo usan para **LTV/originación**; va más allá del informe-consumidor.
6. **Distribución embebida masiva** — KBB, Cars.com, CarGurus, eBay Motors, Edmunds, AutoTrader, TrueCar, CarZing + CPO OEM; el informe llega "dentro" de los marketplaces.
7. **NMVTIS oficial** a $0.43 + compliance estatal (California) — combina informe comercial y federal en un mismo acceso.
8. **Precio agresivo vs Carfax** — $29.99 single / $59.99 por 5; históricamente más barato que Carfax.
9. **Tiles "at a Glance" + Warranty Check + Recommended Maintenance + Recall** — el dossier va más allá del puro historial e incorpora **garantía OEM estimada**, **mantenimiento recomendado** y **recalls NHTSA** integrados.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **Solo EE.UU.** — 50 estados + DC; **cero cobertura internacional** (inútil como fuente de huella digital fuera de US; irrelevante para el scope España/EU de cardeep salvo como patrón de UI).
2. **No es valoración** — **no** publica retail/trade/wholesale, residual %, days-to-sell, price-to-market %, curva de depreciación ni ajuste por km como índices propios. Para la fórmula Buyback **depende de NADAguides** (tercero). No compite con KBB/Black Book/cap.
3. **Service/maintenance records más débiles que Carfax** — percepción consolidada del mercado: Carfax tiene **más registros de servicio/taller**; AutoCheck es fuerte en subasta/título pero flojo en mantenimiento detallado.
4. **Severidad/diagramas de accidente menos granular** — Carfax suele dar más detalle de severidad/point-of-impact; AutoCheck depende de lo que la fuente reporte.
5. **Cobertura incompleta inherente** — "Not all accidents and/or damage events are reported"; recomienda inspección de tercero. Ningún VHR captura todo.
6. **Sin specs/equipamiento atómico tipo build-data** — decodifica VIN a year/make/model/trim/class/engine, pero **no** entrega opciones/packages/features VIN-level (no es NeoVIN/DataOne).
7. **No marketplace ni inventario** — no cataloga concesionarios ni su presencia online (territorio propio de cardeep); es un dato por-VIN, no un censo de puntos de venta.
8. **Opacidad de schema B2B/API** — la estructura de la API y los campos del feed no se publican; exige contacto comercial. [NV — no documentación pública de API]
9. **Discrepancias de cifras** — escala de BBDD ("4.000M registros / 500M vehículos" vs "700M vehículos"), fundación ("incorporada 1996 / inicio 1999" vs "debuted >10 años" en página ~2016), y precios (vivo $29.99/$59.99 vs terceros $24.99/$99.99) — todas marcadas, no resueltas por invención.
10. **SPA opaca a crawlers** — autocheck.com no renderiza sin JS (WebFetch sólo ve el `<title>`); el dato vive tras render — señal de fricción para scrapers, no para el usuario.
11. **NMVTIS no a consumidores** — el informe federal sólo a dealers; el consumidor recibe el informe comercial AutoCheck, no el NMVTIS directo.

---

## 10. Fuentes (URLs)

**AutoCheck.com (renderizado vía Playwright — SPA; WebFetch sólo veía el título)**
- https://www.autocheck.com/vehiclehistory/sample-vehicle-history-report — **informe real renderizado** (2015 Acura TLX V6): cabecera, Score 48 / range 76-87, 9 tiles "at a Glance", Accident & Damage, Open Recall, Recommended Maintenance, Odometer Check, Detailed Vehicle History timeline, Warranty Check, glosario, footer (>4.000M registros / ~500M vehículos, Patent 8,005,759).
- https://www.autocheck.com/vehiclehistory/vehicle-history-reports — **pricing vivo**: Single $29.99, 5 Reports/21 Days $59.99, AutoCheck for Business; "95% of all U.S. auction houses".
- https://www.autocheck.com/vehiclehistory/backed-by-experian — **taxonomía de 12 fuentes** con campos por fuente.
- https://www.autocheck.com/vehiclehistory/autocheck-score — Score: factores (age/class/mileage/owners/use+events), penalizadores, Score Range, ejemplos, DMV/auctions/insurance/NHTSA/FEMA.
- https://www.autocheck.com/vehiclehistory/autocheck-vs-carfax — diferencial: Score patentado, 50 estados+DC, auction-announced data de 2 mayores subastas, insurance/salvage, Buyback, 13.000+ dealers (página ~2016, © 2016).
- https://www.autocheck.com/vehiclehistory/subscription-benefits — VIN & US License Plate search (50 estados), dashboard, multi-report.
- https://www.autocheck.com/vehiclehistory/buyback-terms — Buyback T&C (vía búsqueda).
- https://www.autocheck.com/vehiclehistory/title-brands — title brands (vía búsqueda).

**Experian (B2B / corporate, server-rendered)**
- https://www.experian.com/automotive/autocheck-business — 98.86% auction coverage, 329M vehículos con auction announcements, 4.5M structural damage, membresías, integraciones (Cars.com/CarGurus/KBB/eBay Motors/Edmunds/AutoTrader/CarZing/TrueCar), soporte.
- https://www.experian.com/automotive/autocheck_score — Score (escala 1-100, ejemplos 84/89, comparación por clase).
- https://www.experian.com/automotive/autocheck-lenders — riesgo de préstamo, LTV, billions of records, 95%+ auctions, impacto "30%+".
- https://www.experian.com/automotive/automotive-autocheck-nmvtis-new-customer — NMVTIS $0.43, approved provider, compliance.
- https://www.experian.com/blogs/insights/what-is-autocheck-buyback-protection/ — Buyback: brands cubiertos, 110% NADAguides + $500, 90 días, 60 días, 1 año claim.
- https://www.experian.com/content/dam/marketing/na/automotive/white-paper/1100-AUTO-AutoCheck_Score_Whitepaper.pdf — white paper del Score (**PDF binario no legible vía fetch**; metodología corroborada por las páginas de Score).
- https://www.experianplc.com/newsroom/press-releases/2011/jaguar-land-rover-north-america-llc-adds-experian-automotives-autocheck — AutoCheck como VHR en CPO de JLR.
- https://www.experianplc.com/newsroom/press-releases/2012/experian-automotive-launches-autocheck-elite — AutoCheck Elite.

**Identidad / verificación cruzada**
- https://en.wikipedia.org/wiki/Experian — Experian plc, LSE:EXPN, FTSE 100, HQ Dublín, demerge GUS 2006.
- BBB profile (AutoCheck, Costa Mesa CA; incorporada 30-oct-1996, inicio 03-may-1999; oficinas Schaumburg/Skokie IL).
- https://www.cbinsights.com/company/experian-automotive — Experian Automotive (HQ Schaumburg IL).
- https://www.coxautoinc.com/insights/kelley-blue-book-experian-team-up-to-bring-buyers-better-vehicle-history-reports/ + https://mediaroom.kbb.com/2025-06-10-Kelley-Blue-Book,-Experian-Team-Up... — partnership KBB+Experian (jun-2025).
- https://www.edmunds.com/car-buying/which-vehicle-history-report-is-right-for-you.html — comparativa AutoCheck vs Carfax (service records, auction).

> **Marcas [NV] / discrepancias declaradas:** cobertura internacional (no existe); schema/campos exactos de la API B2B (no públicos); escala BBDD 4.000M registros/500M vs 700M vehículos; fundación 1996/1999 vs "debuted >10y"; precios vivos $29.99/$59.99 vs terceros $24.99/$99.99; "1826" = linaje GUS, no de Experian-info; Manheim/ADESA como las "2 mayores subastas" (contexto de industria, no nombradas literalmente en la página). El white paper del Score llegó como **PDF binario ilegible**; su metodología se reconstruye desde las páginas públicas de Score, no del PDF.
