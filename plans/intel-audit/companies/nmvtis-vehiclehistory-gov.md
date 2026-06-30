# NMVTIS / VehicleHistory.gov — Auditoría atómica

> **slug:** `nmvtis-vehiclehistory-gov` · **subdominio de audit:** `official-data` · **web oficial:** https://vehiclehistory.bja.ojp.gov · **operador:** https://www.aamva.org/vehicles/nmvtis · **regulación:** 28 CFR Part 25 (74 FR 5740, 30-ene-2009)
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; **[V]** = verificado leyendo la fuente · **[NV]** = no verificado / inferido (marcado siempre). Nada inventado.
> **Veredicto express:** NMVTIS **NO es una empresa privada ni una guía de valoración**: es el **National Motor Vehicle Title Information System**, el **sistema federal de información de título de vehículo de EE.UU.**, creado por la **Anti Car Theft Act de 1992**, propiedad del **U.S. Department of Justice → Office of Justice Programs → Bureau of Justice Assistance (BJA)**, y **operado por contrato por la AAMVA** (American Association of Motor Vehicle Administrators). Su web pública de marca es **VehicleHistory.gov** (`vehiclehistory.bja.ojp.gov`). Es la **única base de datos de historial de vehículo del país a la que TODOS los estados, TODAS las aseguradoras y TODOS los desguaces/junk-salvage yards están obligados POR LEY FEDERAL a reportar** — ese mandato legal es su diferencial irreproducible. Cubre **solo EE.UU.** (50 estados + DC; ~99% del parque titulado). Escala (2024): **>2.000 millones de registros** repartidos en 4 BBDD (Título 680M, Histórico de título 1.200M, Brand 219M, Junk/Salvage/Insurance 256M). Es un **sistema pointer-based**: el registro central apunta al **estado que actualmente tiene el título** y consolida brand/odómetro/JSI. **No vende directo al consumidor**: licencia el dato por VIN a **19 Approved Data Providers** (26 webs: VinAudit, ClearVin, Bumper, EpicVin, GoodCar, Carvertical, etc.) que **maquetan su propio informe** y fijan su propio precio (rango histórico **$2–$12.99/informe**). El informe NMVTIS es **deliberadamente conciso**: **5 indicadores** (estado de título + última fecha · brand history · odómetro · total loss · salvage/junk history). Entrega: **informe web/PDF por VIN** vía providers, **API/data feed por-VIN** a providers, **State Web Interface (SWI)** para DMVs (verificación de título pre-emisión, real-time o batch), y **LEAT** (Law Enforcement Access Tool) para policía.
> **Patrón a copiar por cardeep:** (1) la idea de un **registro de procedencia autoritativo y normalizado** — NMVTIS **mapea los brands heterogéneos de cada estado a un vocabulario único de ~60 brands estandarizados**; ese es exactamente el patrón "country-proof / normalización a un esquema canónico" que cardeep necesita para fusionar fuentes nacionales. (2) El **layout del informe de los providers**: rejilla de **tiles-resumen tipo contador** (Ownership / Title records / Title brands / Junk&Salvage / Insurance / Theft / Recalls, cada uno con `N record(s) found`) seguida de **tablas cronológicas por sección** (Title History dividido en *Current* + *Historical*; Odómetro como **chart + tabla** oldest→newest; **checklist de los ~60 brands** con estado `Found / No Brand Reported` + fecha + estado emisor). (3) El **modelo pointer**: guardar el puntero "qué jurisdicción tiene la verdad ahora" + el histórico, en vez de duplicar el registro.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre del sistema | **National Motor Vehicle Title Information System (NMVTIS)** | [V — vehiclehistory.bja.ojp.gov] |
| Marca web pública | **VehicleHistory.gov** (host real `vehiclehistory.bja.ojp.gov`) | [V — sitio] |
| Propietario / patrocinador | **U.S. Department of Justice (DOJ)** → **Office of Justice Programs (OJP)** → **Bureau of Justice Assistance (BJA)** | [V — bja.ojp.gov/program/nmvtis] |
| Operador (system operator) | **American Association of Motor Vehicle Administrators (AAMVA)** — operador tercero designado, mediante **Cooperative Agreement** con DOJ/OJP | [V — FY2024 Annual Report, Preface] |
| CEO del operador (AAMVA) | **Ian Grossman, President & CEO** (firma el mensaje del operador en el FY2024 report) | [V — FY2024 report, p.5] |
| Naturaleza | **Sistema federal de gobierno**, NO empresa privada; NO es un valuation guide | [V — Anti Car Theft Act] |
| Autoridad legal / fundación | **Anti Car Theft Act of 1992**; reautorizada/enmendada **1996** (la supervisión pasó de **DOT → DOJ**) | [V — bja.ojp.gov + system-overview] |
| Reglamento operativo | **NMVTIS Final Rule — 28 CFR Part 25, publicado 30-ene-2009 (74 FR 5740)** | [V — FY2024 report Preface + ecfr] |
| Inicio reporting obligatorio JSI | **31-marzo-2009** (junk/salvage/insurance) | [V — eCFR §25.56 + ClearVin] |
| Teléfono programa NMVTIS (BJA) | **202-616-6500** | [V — bja.ojp.gov] |
| Gobernanza | **NMVTIS Advisory Board** (charter expiró sep-2016) → ahora supervisa **BJA**; AAMVA gestiona subcomités (State Program Subcommittee SPS, Law Enforcement Subcommittee LESC) | [V — system-overview + FY2024] |
| Uptime sistema FY2024 | **99,99%** | [V — FY2024 report, p.5/8] |
| Modelo de financiación | **Self-funded**: state user fees + revenue credits de la venta de informes por providers; nuevo modelo de funding implementado FY2024 | [V — FY2024 report] |

**Qué es:** un **repositorio federal centralizado** que verifica e intercambia datos de **título, brand, robo y odómetro** entre **agencias estatales de titulación (DMVs), aseguradoras, desguaces/recicladores (JSI), policía y consumidores**. No produce valoración, ni specs de equipamiento, ni precio de mercado: produce **procedencia legal y de condición** del vehículo por VIN.

### Categorías de "producto" / programa [V]
NMVTIS opera **4 programas** (= sus líneas de servicio), servidos por **5 grupos de usuarios y 11 aplicaciones** (FY2024):

| Programa | Usuario | Apps |
|---|---|---|
| **State Program** | State titling agencies (DMVs) | 5 aplicaciones |
| **Consumer Access Program** | Approved NMVTIS Data Providers (revenden al público/dealers) | 2 aplicaciones |
| **Law Enforcement Access Program** | Policía (federal/estatal/local/tribal/territorial + militar + Canadá) | 1 aplicación (LEAT) |
| **JSI Reporting Program** | Junk/Salvage/Insurance Data Consolidators | 2 aplicaciones |
| (Supervisión) | **U.S. Department of Justice** | 1 aplicación |

### Clientes / usuarios objetivo (declarados) [V]
- **Consumidores** (individuales y comerciales) comprando coche usado → vía providers.
- **Concesionarios / dealers** (compliance de título; algunos providers son dealer-only).
- **State DMVs** (verificación de título antes de emitir uno nuevo; anti-clonado/anti-fraude).
- **Aseguradoras, desguaces, recicladores, salvage pools, shredders** (como **reporting entities** obligados).
- **Policía y agencias de investigación** (LEAT) — incluye **RCMP / Service Alberta** (Canadá).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía | **EE.UU. exclusivamente** — "state" = los **50 estados + el Distrito de Columbia** | [V — FY2024 report, Notes] |
| Participación estatal | **49 estados + DC** participan (niveles variables: proveen datos / consultan antes de titular / ambos) | [V — búsqueda AAMVA/Missouri DOR] |
| Cobertura del parque titulado | **~99% de los datos de título de vehículos de EE.UU. representados en el sistema** (FY2024) | [V — FY2024 report, Executive Summary] |
| Usuarios fuera de EE.UU. | Solo **law enforcement canadiense** (RCMP, Service Alberta SIU) tiene acceso LEAT; NO hay cobertura de datos de vehículos no-US | [V — FY2024 report, p.39] |
| Escala — 4 BBDD (2024) | **Título: 680M registros** · **Histórico de título: 1.200M (1.2B)** · **Brand: 219M** · **Junk/Salvage/Insurance: 256M** → **>2.000M registros totales** | [V — FY2024 report, Executive Summary] |
| Aporte estatal FY2024 | **>20M** registros de título actuales nuevos + **>89M** registros de histórico de título en el año | [V — búsqueda FY2024] |
| Registros JSI FY2024 | **16,9M** reportados (−4% vs 17,7M FY2023) | [V — FY2024 report, p.26] |
| Transacciones estatales FY2024 | **>269M** (inquiries + title updates + brand updates) | [V — FY2024 report, Executive Summary] |
| Transacciones de consumidor (billed) FY2024 | **~26M** (subió desde ~19M, **+38%**) | [V — FY2024 report, p.35] |
| Consultas LEAT FY2024 | **2.374.562** (vs 1.711.510 FY2023, **+39%**); **11.105 usuarios LEAT** | [V — FY2024 report, p.39] |

### Scope de vehículo [V]
- **Usado** es el caso de uso central (anti-fraude en compra de usado), pero el sistema cubre el **ciclo de título completo** (nuevo y usado).
- **Tipos incluidos:** **automóviles, autobuses, camiones, motocicletas, autocaravanas / RVs (motor homes), y truck tractors (tractoras)**. [V — system-overview + FAQ]
- **Tipos excluidos:** **remolques (trailers), mobile homes, embarcaciones (vessels), ciclomotores (mopeds) y golf carts**. [V — system-overview]
- **Granularidad:** **por VIN** (consulta de un solo VIN a AAMVA).
- **Histórico:** registros de título acumulados a lo largo de la vida del vehículo (current + historical) + brands con fecha + JSI desde 31-mar-2009.

---

## 3. Productos + campos atómicos

> NMVTIS-native ≠ enriquecimiento del provider. El esquema atómico de **NMVTIS** se extrae de: los **5 indicadores oficiales** (vehiclehistory.bja.ojp.gov), los **elementos legales** (28 CFR §25.56), el **vocabulario de ~60 brands estandarizados** y los **samples renderizados** de providers (ClearVin, VINData). Lo que el provider añade encima (specs por VIN-decode, Black Book values, recalls NHTSA, accident/damage, sale history) **NO es dato NMVTIS** y se marca como *provider-added*.

### 3.1 NMVTIS Vehicle History Report — los 5 indicadores oficiales (producto núcleo) [V]
El informe NMVTIS es **intencionadamente conciso** (más corto que Carfax/AutoCheck). Contiene **5 indicadores**:

1. **Current State of Title + Last Title Date** — `Current state of title` (jurisdicción que tiene el título ahora) · `Last/previous state of title` · `Title issue date`.
2. **Brand History** — cualquier `Brand` aplicado al vehículo + `Date applied` + `State` (vocabulario estandarizado, ver §3.4).
3. **Odometer Reading** — `Latest reported odometer reading` (reportado al titular el vehículo).
4. **Total Loss History** — designaciones de `total loss` por aseguradora (si las hay).
5. **Salvage History** — reportes de desguace/junk yard/salvage yard que manejaron el vehículo + `disposition`.

**Campos atómicos NMVTIS-native (esquema de verdad):**

**(A) Identidad del vehículo (de la descripción de título / VIN):**
- `VIN`
- `Make` · `Model` · `Model Year` · `Body type/style` (vehicle description del certificado de título)

**(B) Title — Current Title Information:**
- `Title Issue Date`
- `State` (jurisdicción de titulación actual = el **pointer record**)
- `Reported Odometer` (al emitir título)
- `Title Number` (reportado por el estado) [V — vía providers]
- `Title Type / Event` (original, duplicate, lien release, transfer, superseded…) [V — VINData "Type/Event"]
- `Name of individual/entity to whom title was issued` → **solo law enforcement** (no en informe de consumidor) [V — eCFR + búsqueda]

**(C) Title — Historical Title Information** (mismas columnas, N registros): `Date Issued` · `State` · `Type` · `Event` · `Reported Odometer` · `Source`. [V — VINData/ClearVin samples]

**(D) Brand record:**
- `Brand` (uno de ~60 estandarizados)
- `Brand Issued Date` / `Date applied`
- `State` (jurisdicción que aplicó el brand)
- `Description` (definición del brand)

**(E) Odometer record:**
- `Odometer Reading` (valor)
- `Date` de la lectura
- `Type` / status de la lectura (Actual, Not Actual, Exceeds Mechanical Limits, etc. — *odometer brands*, ver §3.4)
- `Source` (DMV / título)

**(F) Junk / Salvage record (JSI):**
- `Reporting Entity Name` · `Address` · `Contact info`
- `Reporting Entity Type` (Individual · Insurer · Recycler · Salvage Pool · Shredder)
- `VIN`
- `Date Obtained` (fecha en que la entidad obtuvo el vehículo)
- `Name of individual/entity from whom obtained` (→ restringido a law enforcement)
- `Disposition` / `Event` (valores: **Crush · Parts · Retained · Salvage · Scrap · Sold · To Be Determined (TBD)**)
- `Intended for Export` (Yes/No)
- `Source` (entidad reportante / consolidador)

**(G) Insurance / Total Loss record (JSI):**
- `Date Obtained`
- `Entity` (aseguradora)
- `Location`
- `Contact info`
- `Disposition`
- `Total Loss` declaration (sí/no)

**(H) Theft record:**
- `Theft / Stolen status` (p.ej. "NOT LISTED AS STOLEN")
- `Theft recovery status` (si aplica)

### 3.2 Disposition (JSI) — valores atómicos y distribución FY2024 [V]
El campo `DISPOSITION` indica qué pasó con el vehículo desde que la entidad lo obtuvo. **62%** de los registros FY2024 cerraron con disposición final; **38%** quedaron en *To Be Determined*. Valores:
- `Crush` (~37% de los registros con disposición) · `Sold` (~29%) · `Parts` (14%) · `Scrap` (12%) · `Salvage` (6%) · `Retained` (1%) · `To Be Determined` (pendiente).
*(Porcentajes de las figuras 20/21 del FY2024 report; el mapeo exacto slice→categoría no se publica numerado, se reportan como rangos observados.)* [V con matiz]

### 3.3 Entidades reportantes JSI — tipos (FY2024) [V]
`Individual` · `Insurer` (aseguradora) · `Recycler` (reciclador) · `Salvage Pool` · `Shredder` (trituradora). Umbral: entidades que manejan **5 o más** vehículos salvage/junk al año están obligadas a reportar **mensualmente**.

### 3.4 Vocabulario estandarizado de BRANDS — los ~60 brands NMVTIS (diferencial duro) [V]
NMVTIS **mapea los brands heterogéneos de cada estado a un vocabulario único** para consistencia. Lista completa verificada (VinAudit "Title Brands", que refleja los códigos estandarizados NMVTIS/AAMVA):

**Daño / condición:** `Flood Damage` · `Salt Water Damage` · `Fire Damage` · `Hail Damage` · `Vandalism` · `Collision` · `Disclosed Damage` · `Hazardous` (contaminado por sustancia peligrosa).
**Salvage / Junk / pérdida:** `Salvage: Damage` · `Salvage: Stolen` · `Salvage: Other` · `Salvage Retention` · `Junk` · `Dismantled` · `Crushed` · `Totaled` · `Owner Retained` · `Prior Owner Retained` · `Bond Posted` · `Export Only Vehicle` · `Prior Non-Repairable / Repaired`.
**Reconstrucción / fabricación:** `Rebuilt` · `Reconstructed` · `Remanufactured` · `Refurbished` · `Kit` · `Replica` · `Street Rod` · `Test Vehicle` · `Recovered Theft`.
**Uso previo / actual:** `Prior Taxi` · `Original Taxi` · `Prior Police` · `Original Police` · `Former Rental` · `Agricultural Vehicle` · `Logging Vehicle`.
**Edad / origen:** `Antique` (>50 años) · `Classic` (>20 años) · `Gray Market` (fabricado para fuera de EE.UU.).
**Garantía / defecto OEM:** `Manufacturer Buy Back` (lemon law) · `Warranty Return` · `Non-conformity: Uncorrected` · `Non-conformity: Corrected` · `Safety Defect: Uncorrected` · `Safety Defect: Corrected`.
**Título / VIN:** `Memorandum Copy` · `Reissued VIN` · `VIN Replaced` · `Titling Issue`.
**Odometer brands (status de lectura):** `Odometer: Actual` · `Odometer: Not Actual` · `Odometer: Tampering Verified` · `Odometer: Exempt from Disclosure` · `Odometer: Exceeds Mechanical Limits` · `Odometer: Exceeds Mechanical Limits Rectified` · `Odometer: May be Altered` · `Odometer: Replaced` · `Odometer: Reading at Time of Renewal` · `Odometer: Discrepancy`.

### 3.5 NMVTIS State Title Verification (State Program / SWI) [V]
Para **DMVs**: verificación del título **antes de emitirlo** para evitar clonado/fraude/títulos lavados (title washing). Modos: **Integrated** (online en el flujo de titulación), **State Web Single VIN Inquiry** (manual) y **Batch Inquiry**. Responde si el VIN tiene título válido en otra jurisdicción, brands a arrastrar (*carry forward*), robo, etc. El **State Web Interface (SWI)** estaba en *rewrite* de 4 fases (a concluir FY2025).

### 3.6 NMVTIS Law Enforcement Access Tool (LEAT) [V]
Búsqueda para policía verificada (RISS o FBI). Datos extra solo-LE: identidad del titular, identidad de quien entregó el vehículo a un junk/salvage yard, etc. FY2024: **2,37M** consultas, **11.105** usuarios.

### 3.7 JSI Single VIN Reporting Service / Data Consolidators [V]
Canal para que las entidades reportantes cumplan. **Data Consolidators** aprobados: **AAMVA Single VIN Reporting Service**, **Solera/Audatex**, **Auto Data Direct, Inc. (ADD)**, **Insurance Services Office (ISO ClaimSearch)**. Algunos estados (Georgia DOR, Tennessee DOR) reportan en nombre de sus entidades vía ADD (consolida reporte estatal + federal en un proceso, sin coste a la entidad).

### 3.8 NMVTIS Data (feed por-VIN a providers) [V]
El dato crudo que AAMVA licencia a los Approved Providers: **se solicita enviando un único VIN a AAMVA**; el provider construye su propio informe. Pricing mayorista "single rate" por **volumen** (ver §6). Vitu y otros exponen una **NMVTIS API**. [V — vitu.com/api + AAMVA]

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Arquitectura | **Pointer-based**: el sistema mantiene **pointer records** que indican **el estado que actualmente tiene el título** del VIN, + consolida histórico de título, brands y JSI en BBDD centrales | [V — FY2024 report (proxy de funding = pointer record count)] |
| Fuente 1 — DMV data | Las **agencias estatales de titulación** proveen: VIN, descripción/título del vehículo, todos los brands del certificado, nombre del titular, lectura de odómetro al titular | [V — búsqueda 28 CFR + system-overview] |
| Fuente 2 — JSI data | **Aseguradoras + junk/salvage yards + recicladores** (≥5 vehículos/año) reportan **mensualmente** los elementos del §25.56 | [V — eCFR §25.56] |
| Normalización | Brands estatales heterogéneos **mapeados a ~60 brands estandarizados** NMVTIS | [V — búsqueda AAMVA] |
| Obligatoriedad legal | **Única BBDD del país a la que estados, aseguradoras y junk/salvage yards DEBEN reportar por ley federal** | [V — aamva consumers] |
| Frecuencia de datos | Variable por estado: algunos **real-time** (RESTful), otros cada **24h** o "within a period of days"; JSI **mensual** | [V — FAQ + glossary] |
| Verificación pre-título | Estados consultan NMVTIS **antes de emitir** un título → previene clonado y title washing | [V — system-overview] |
| Lo que NO recoge | **No** owner names (consumidor), **no** lien holder address, **no** repair/service history detallado, **no** valoración/precio | [V — búsqueda consumers + add123] |

### Elementos legales exactos — 28 CFR §25.56 (lo que reportan junk/salvage/insurance) [V]
Reporte **mensual** (desde 31-mar-2009). Cada registro contiene:
1. `The name, address, and contact information for the reporting entity`
2. `VIN`
3. `The date the automobile was obtained`
4. `The name of the individual or entity from whom the automobile was obtained`
5. `A statement of whether the automobile was crushed or disposed of, for sale or other purposes, to whom it was provided or transferred, and if the vehicle is intended for export out of the United States`

**Exenciones:** entidades con <5 vehículos/año; yards que ya reportan a un estado que comparte con el operador; scrap processors cuando el proveedor ya reportó el vehículo.

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Informe web/PDF por VIN (consumidor)** | NO directo de NMVTIS; vía **19 Approved Data Providers / 26 webs** que maquetan su propio informe (VinAudit, ClearVin, Bumper, EpicVin, GoodCar, Carvertical, Checkthatvin, Titlecheck, Vindata, Vinsmart, Carsforsale) | [V — vehiclehistory.bja.ojp.gov/nmvtis_vehiclehistory] |
| **Providers dealer-only / comercial** | **Carfax, Experian/AutoCheck, Auto Data Direct, Vitu, Yassi, AIB (oneaib)** — los consumidores **NO** pueden recibir el informe NMVTIS de Carfax/DMVDesk/Experian | [V — misma página] |
| **API / data feed por-VIN** | AAMVA licencia el dato enviando 1 VIN; providers construyen el informe; **NMVTIS API** expuesta por algunos (Vitu) | [V — AAMVA + vitu] |
| **State Web Interface (SWI)** | Para DMVs: Integrated, Single VIN Inquiry, Batch Inquiry (real-time / batch); RESTful para sistemas modernizados | [V — aamva technology + glossary] |
| **LEAT (Law Enforcement Access Tool)** | Portal policial; acceso verificado por RISS/FBI | [V — FY2024 report] |
| **JSI reporting portals** | Single VIN Reporting Service (AAMVA), Audatex, ADD, ISO ClaimSearch | [V — reporting-entities] |
| **Confirm Last Reporting Date** | Herramienta pública para confirmar cuándo una entidad reportó por última vez | [V — homepage] |
| **Búsqueda** | **por VIN** (no por matrícula en el sistema federal) | [V] |

---

## 6. Precio

| Concepto | Valor | Estado |
|---|---|---|
| **Informe al consumidor** | **Lo fija cada provider**; rango histórico **$2–$12.99 por informe** (FAQ DC DMV cita **$8–$12.99** as of may-2020) | [V — FAQ vehiclehistory.gov + dc.gov] |
| **Fee de desarrollo del provider** | **$30.000** (one-time) para construir la interfaz web que solicita/recibe el dato NMVTIS; pagadero al firmar contrato | [V — búsqueda AAMVA Consumer Access Data Provider] |
| **Pricing mayorista del dato** | "single rate" **por VIN**, estructura **basada en volumen**; en FY2024 AAMVA encargó un **Consumer Access Market and Price Assessment** para comparar su pricing mayorista contra otras fuentes de dato (concluye FY2025) | [V — FY2024 report, p.37] |
| **Revenue credits a estados** | Estados ganaron **>$3,4M** en créditos por venta de informes por providers (FY2024) | [V — FY2024 report] |
| **Gross revenue Consumer Access** | **$7,1M FY2024** (vs $5,8M FY2023, **+22%**) | [V — FY2024 report, p.35] |
| **Reseller conocido (referencia)** | Experian/AutoCheck revende el informe NMVTIS a dealers a **$0.43/informe** | [V — experian NMVTIS page, cruzado con autocheck.md] |
| **State user fees** | Financian la operación; proxy de asignación cambió de población de matriculación (FHWA) a **pointer record count** (efectivo FY2026) | [V — FY2024 report] |

---

## 7. Placement — dónde coloca cada dato (patrón a copiar por cardeep)

> El sistema federal no tiene UI de consumidor; el **placement canónico** se observa en los informes renderizados de los providers (ClearVin sample report 2026 + VINData RV sample). **Es el blueprint de la sección "procedencia/historial oficial" de la ficha de cardeep.**

| Dato | Dónde lo colocan (UI del provider) |
|---|---|
| Cabecera (VIN, Report ID, Date Generated, rating) | **Top header** del informe |
| Resumen de hallazgos | **Rejilla de tiles-contador** arriba: `Ownership History` · `Odometer Reading` · `Title History (N records)` · `Title Brands (N)` · `Junk & Salvage (N)` · `Insurance Records (N)` · `Theft` · `Recalls` — cada tile con `N record(s) found` (patrón "Summary Cards") |
| Specs del vehículo *(provider-added, VIN decode)* | Sección **"Vehicle Specifications"** (make/model/engine/dimensiones/fuel economy…) |
| Propiedad | Sección **"Ownership History"** — tabla `Date of purchase · Condition · Length of ownership · Owned in states · Last reported odometer · Usage` |
| **Título (NMVTIS core)** | Sección **"Title History"** dividida en **`Current Title Information`** (Title Issue Date · State · Mileage) + **`Historical Title Information`** (mismas columnas, N filas) |
| **Brands (NMVTIS core)** | Sección **"Title Brand Information"** — **checklist de los ~60 brands** con `Brand name · Definition · Status (Found / No Brand Reported) · Application date · State` |
| **Odómetro (NMVTIS core)** | Sección **"Odometer Reading"** — **chart** (comparación vs media + flag `Overdriven`) + **tabla** `Date · Mileage · Data Source` (oldest→newest) |
| **Junk & Salvage (NMVTIS core)** | Sección **"Junk & Salvage Records"** — tabla `Date Obtained · Entity · Location · Contact info · Export (Y/N) · Disposition` |
| **Insurance / Total Loss (NMVTIS core)** | Sección **"Insurance Records"** — tabla `Date Obtained · Entity · Location · Contact info · Disposition` + disclaimer total-loss |
| **Theft (NMVTIS core)** | Sección **"Theft Records"** — indicador de estado (`NOT LISTED AS STOLEN`) |
| Junk/Salvage/Total-Loss unificado (VINData) | Tabla `Date Obtained · Reporting Entity · Reporting Entity Type · Event/Disposition · Intended for Export · Source` |
| Accident & Damage *(provider-added)* | Sección con imagen + `Date · Major Impact · Airbags · Repair Cost` + disclaimer "Not all damage reported" |
| Valores de mercado *(provider-added, ej. Black Book)* | Subsección `Trade-in values` / `Retail values` (Rough/Average/Clean Base) |
| Recalls *(provider-added, NHTSA)* | Sección **"Recalls"** — `Recall Date · Recall No · Component(s)` + Consequence/Remedy |
| Lien & Impound *(provider-added)* | Sección con `Date · State · Reported By · Event` |
| Legal | **Footer**: `NMVTIS Consumer Access Product Disclaimer` (+ Glossary + Data Sources) — **obligatorio** en todo informe NMVTIS |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Mandato legal federal único** — la **única BBDD del país a la que TODOS los estados, TODAS las aseguradoras y TODOS los junk/salvage yards están obligados por ley a reportar**. Carfax/AutoCheck dependen de fuentes voluntarias/comerciales; NMVTIS tiene el dato por imperativo legal. Es **irreproducible** por un privado.
2. **Vocabulario de ~60 brands estandarizados** — normaliza los brands heterogéneos de 50 estados + DC a un esquema único y consistente (incluye *carry-forward* de brands entre jurisdicciones). Patrón de normalización canónica directamente aplicable a cardeep.
3. **Arquitectura pointer + verificación pre-título** — los DMVs consultan NMVTIS **antes de emitir** un título → ataca el **title washing** y el **clonado de VIN** en origen, no a posteriori.
4. **Autoridad gubernamental** — es la fuente oficial; los informes comerciales (incl. AutoCheck) **citan NMVTIS** como fuente. Es el "ground truth" de título/brand/odómetro/salvage/total-loss en EE.UU.
5. **Cobertura JSI por sectores enteros** — 256M registros junk/salvage/insurance reportados por **sectores completos** (insurers, recyclers, salvage pools, shredders), no por acuerdos comerciales selectivos.
6. **Escala** — >2.000M registros; ~99% del parque titulado; 269M transacciones estatales/año.
7. **Distribución federada** — un solo dato canónico revendido por 19 providers/26 webs → ubicuidad sin que NMVTIS gestione UI ni atención al consumidor.
8. **Disclaimer y data-source obligatorios** — todo informe lleva el disclaimer oficial; transparencia legal forzada.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **Solo EE.UU.** — 50 estados + DC; **cero datos de vehículos fuera de EE.UU.** (irrelevante como fuente para el scope España/EU de cardeep salvo como **patrón de normalización y de placement**). Único cruce internacional: acceso LEAT a policía canadiense.
2. **No es valoración ni specs** — **no** publica retail/trade/wholesale, residual %, days-to-sell, price-to-market %, market days supply, curva de depreciación, ajuste por km, ni equipamiento/opciones VIN-level. Solo procedencia legal/condición. (Los providers añaden Black Book/specs por su cuenta, no es dato NMVTIS.)
3. **Informe deliberadamente conciso** — solo **5 indicadores**; **no** accidentes detallados, **no** service/repair records, **no** point-of-impact/airbag (eso lo añade el provider de otras fuentes). NMVTIS lo dice explícito: "shorter than other vehicle history reports".
4. **Falsos negativos posibles** — no todos los estados reportan en tiempo real; algunos no consultan; "more than half of the states report data" históricamente → un informe limpio **no garantiza** ausencia de problema. Disclaimer obligatorio por esto.
5. **No vende directo al consumidor** — depende de providers; la experiencia, el precio ($2–$12.99) y la maquetación las controla un tercero, no NMVTIS.
6. **No owner names ni lien address al consumidor** — datos de titular/origen restringidos a law enforcement.
7. **Latencia variable** — frecuencia de actualización dispar por estado (real-time vs 24h vs "period of days"); JSI mensual → un evento reciente puede no aparecer.
8. **Búsqueda solo por VIN** — el sistema federal no resuelve por matrícula (los providers que ofrecen plate→VIN lo hacen por su cuenta).
9. **Sin marketplace ni censo de puntos de venta** — es un registro por-VIN de procedencia, **no** un inventario ni un censo de dealers (territorio propio de cardeep).
10. **Schema de API/feed no público** — la estructura exacta del feed por-VIN y su pricing mayorista no se publican (en evaluación FY2024-25); requiere contrato + $30k dev fee. [NV detalle de campos del feed]

---

## 10. Fuentes (URLs)

**Sitio oficial NMVTIS / VehicleHistory.gov (DOJ/BJA)**
- https://vehiclehistory.bja.ojp.gov — homepage: qué es, operador BJA, navegación, 4 quick actions (purchase report / get reporting ID / law enforcement access / confirm last reporting date), alertas (flood damage).
- https://vehiclehistory.bja.ojp.gov/nmvtis_understandingvhr — los **5 indicadores**; informe "intentionally concise".
- https://vehiclehistory.bja.ojp.gov/nmvtis_consumers — qué provee al consumidor; brands ejemplo; disclaimers; falsos negativos.
- https://vehiclehistory.bja.ojp.gov/nmvtis_vehiclehistory — **lista completa de Approved Data Providers** (público + dealer-only) con URLs.
- https://vehiclehistory.bja.ojp.gov/nmvtis_auto — reporting entities; elementos JSI; data consolidators; umbral 5+/año.
- https://vehiclehistory.bja.ojp.gov/faq/list — data elements; junk/salvage report; vehicle types; pricing $8–$12.99 (may-2020); frecuencia.
- https://vehiclehistory.bja.ojp.gov/nmvtis-annual-reports-and-financial-audits/system-overview — Anti Car Theft Act 1992; AAMVA operador; tipos de vehículo incluidos/excluidos; verificación pre-título.
- https://vehiclehistory.bja.ojp.gov/nmvtis-annual-reports-and-financial-audits/glossary — glosario: Brand, Cloned Vehicle, JSI, Odometer Reading, Superseded Title, Data Consolidators (AAMVA, Audatex, ADD, ISO ClaimSearch), RESTful.
- https://vehiclehistory.bja.ojp.gov/doc/fy24-nmvtis-annual-report.pdf — **FY2024 Annual Report** (PDF, extraído vía pdftotext): 4 BBDD (680M/1.2B/219M/256M, >2B total), 99% parque, 269M tx estatales, 16.9M JSI, 19 providers/26 webs, billed tx 19M→26M (+38%), gross revenue $7.1M (+22%), LEAT 2.374.562 (+39%)/11.105 users, disposition values + 62%/38%, pointer records, $3.4M revenue credits, uptime 99.99%.

**Bureau of Justice Assistance (programa)**
- https://bja.ojp.gov/program/nmvtis/overview — autoridad legal; DOT→DOJ 1996; propósito; teléfono 202-616-6500.

**AAMVA (operador)**
- https://www.aamva.org/vehicles/nmvtis/nmvtis-for-general-public-consumers — informe contiene título/odómetro/brand/total loss/salvage; obligatoriedad legal; lista de providers (público vs dealer); $30k dev fee.
- https://www.aamva.org/technology/systems/vehicle-systems/nmvtis — operación; SWI Integrated/Single VIN/Batch; subcomités; RESTful.
- https://www.aamva.org/NMVTIS-Consumer-Access-Data-Provider/ — $30k development fee; single-rate por VIN; volumen.
- https://nmvtisreporting.aamva.org/ — Single VIN Reporting Service (JSI).

**Regulación (elementos atómicos legales)**
- https://www.law.cornell.edu/cfr/text/28/25.56 — §25.56: reporte mensual desde 31-mar-2009; 5 elementos requeridos (entity name/address/contact, VIN, date obtained, source, disposition+export); exenciones.
- https://www.ecfr.gov/current/title-28/chapter-I/part-25/subpart-B — eCFR Subpart B (redirige a captcha unblock; usado vía Cornell + búsquedas).

**Providers (samples renderizados — placement) + brand vocabulary**
- https://www.clearvin.com/en/sample-report/ — **sample renderizado**: tiles-contador, specs, ownership, title (current+historical), odometer (chart+tabla), brand checklist (49+), junk&salvage, insurance, theft, accident, Black Book, recalls, disclaimer.
- https://www.vindata.com/report/sample/vhr/rv/red — **sample renderizado**: nav anchors; Junk/Salvage/Total Loss (Date Obtained·Reporting Entity·Type·Event/Disposition·Intended for Export·Source); Title (Date·State·Type·Event·Reported Odometer·Source) + Title Brands (Brand Issued Date·State·Brand·Description); odometer; other (export/theft/towing/lien).
- https://www.vinaudit.com/title-brands — **lista completa de ~60 brands estandarizados** con definiciones.
- https://www.vinaudit.com/nmvtis-data — 5 elementos; "over 60 potential title problems"; "40M+ junk/salvage/insurance records"; API.
- https://www.vinaudit.com/nmvtis-dealer-compliance — compliance dealer; fuentes.
- https://vitu.com/api/nmvtisapi.html — NMVTIS API (provider comercial).

**Cruce de identidad / contexto**
- https://www.federalregister.gov/documents/2009/01/30/E9-1835/... — Final Rule 28 CFR Part 25 (74 FR 5740).
- https://dmv.dc.gov/page/nmvtis-frequently-asked-questions — FAQ estatal (pricing, providers).
- https://www.theiacp.org/news/blog-post/what-is-the-national-motor-vehicle-title-information-system-nmvtis — contexto policial.
- `autocheck.md` (este repo) — cross-check del precio reseller Experian $0.43/informe NMVTIS.

> **Marcas [NV] / matices declarados:** schema exacto del feed/API por-VIN y su pricing mayorista (no públicos; evaluación FY2024-25); mapeo numérico exacto slice→categoría de las disposiciones JSI (figuras del PDF, reportadas como rangos); "name from whom obtained" e identidad del titular = restringidos a law enforcement (no en informe de consumidor); algunos campos del placement (specs, Black Book, recalls, accident, lien) son **provider-added**, NO dato NMVTIS-native, y se marcan como tal; participación "49 estados + DC" con niveles variables (proveer/consultar/ambos) verificada por búsqueda AAMVA, no por conteo directo estado a estado.
