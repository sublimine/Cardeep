# CCC Intelligent Solutions — Auditoría atómica

> **Slug:** `ccc-intelligent-solutions` · **Web:** https://www.cccis.com/ · **Vertical cardeep:** valuation
> **Auditado:** 2026-06-30 · **Método:** páginas de producto vivas recuperadas vía **Wayback Machine** (`web.archive.org` raw `id_`, porque Cloudflare bloquea WebFetch/curl/Playwright directos con "Attention Required"), **PDF oficial de formación de CCC** (`How to Read the Market Valuation Report`, 11 pp.) extraído con `pdftotext`, + verificación cruzada con SEC/IR, prensa del sector (Repairer Driven News, Claims Journal), perfiles corporativos (Encyclopedia.com, Reference for Business) y guías de terceros de litigio de total loss (SecondAppraisal, SnapClaim, DiminishedValueExpert, AutoClaimConsultants).
> **Nota de subdominio:** `valuation.cccis.com` **NO resuelve en DNS** [VERIFICADO: HTTP 000]. `www.cccis.com` y `cccone.com` resuelven pero devuelven **403 (Cloudflare)** al bot. "valuation" es la etiqueta de vertical de cardeep, no un host real de CCC. El producto de valoración vive en `cccis.com/insurance-carriers/apd/claims-valuation` y dentro de la app **CCC ONE / portal `cccone.com`** (con login).
> **Naturaleza:** CCC **NO es un "libro de valores" estilo KBB/J.D. Power/Black Book.** Es la **plataforma SaaS de claims** de la economía de seguros P&C de EE. UU. Su valoración es un **motor de Actual Cash Value (ACV) para total loss** embebido en el flujo de siniestro — el estándar de facto con el que la mayoría de las aseguradoras de EE. UU. liquidan vehículos siniestrados. El "dato" no se vende como guía de precio; se entrega como **Market Valuation Report (MVR)** dentro del expediente del siniestro.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre actual | **CCC Intelligent Solutions Holdings Inc.** | cccis.com (footer ©); SEC |
| Ticker | **NASDAQ: CCCS** (antes **NYSE: CCCS**; trasladó cotización a Nasdaq Global Select el **19-dic-2022**) | bitget/stockanalysis; WebSearch |
| Nombre legal histórico | **Certified Collateral Corporation** (1980) → **CCC Information Services Inc.** → **CCC Intelligent Solutions** (rebrand tras SPAC, 2021) | Encyclopedia.com; Reference for Business; SEC |
| Fundación | **1980**, por **Howard Allen Tullman** (n. St. Louis, 1946), con **$300.000** de inversión inicial; idea: aplicar bases de datos informatizadas al proceso de claims de auto | Encyclopedia.com; Reference for Business `[VERIFICADO 2 fuentes]` |
| Propósito original | Proveer **información de valoración de coches a aseguradoras** para fijar el valor de pérdidas por robo/accidente | Encyclopedia.com |
| HQ | **Chicago, IL** — **222 Merchandise Mart Plaza, Suite 900, Chicago, IL 60654** (sede histórica/legal: "World Trade Center Chicago, 444 Merchandise Mart") | WebSearch (SEC/perfiles) `[PARCIAL: dirección exacta puede haber cambiado]` |
| CEO y Chairman | **Githesh Ramamurthy** (CEO desde **1999**, también Chairman of the Board) | crunchbase; cccis.com/about/leadership; WebSearch |
| Salida a bolsa | **SPAC**: fusión con **Dragoneer Growth Opportunities Corp.** (anunciada **3-feb-2021**, cerrada **Q3 2021**), valoración ≈ **$7.000 M**; cotización inicial NYSE | Oak Hill; Insurance Business; Kirkland & Ellis |
| Owner / grupo (pre-IPO y mayor accionista) | **Advent International** (compró CCC en **2017**); **Oak Hill Capital** coinversor; siguen como accionistas de referencia post-SPAC | Advent International; Oak Hill; WebSearch |
| Financiación SPAC | ~$968 M levantados (PIPE Fidelity, T. Rowe Price; ~$690 M trust de Dragoneer; $175 M forward purchase incl. family office de Michael Bloomberg) | Insurance Business; Oak Hill |
| Revenue FY2024 | **≈ $944,8 M** (+9% YoY) (una fuente cita **$926,2 M** +9%) | WebSearch (8-K/IR) `[VERIFICADO con ligera discrepancia de fuente]` |
| Margen Adj. EBITDA | **≈ 42%** (2024) | bitget/stockanalysis |
| Red / escala | **35.000+** empresas conectadas; **18M+** claims procesados/año; **>$1 billón (trillion US)** de datos históricos | cccis.com (home, Data+AI) |
| Cuota total-loss | **≈ 75%** del mercado de valoración de total loss de seguros de EE. UU. | mydvac; autoclaimconsultants; myfairclaim `[VERIFICADO 3 fuentes terceras; no cifra oficial CCC]` |

**Legado técnico:** la red **EZNet** (claims network) conectaba ya **~350 aseguradoras y ~15.000 talleres** procesando **>1 millón de transacciones/día hábil** (era CCC Information Services). Hoy esa red es el **CCC IX Cloud / CCC Network**.

**Adquisiciones clave (expansión de capacidades):**
- **Safekeep** (feb-2022) — IA de **subrogación** (auto, property, workers' comp). → producto **Subrogation**.
- **EvolutionIQ** (firmada 20-dic-2024, **completada ene-2025**, **$730 M**, ~40% acciones / 60% cash + term loan $225M) — **IA de guía para disability & injury / casualty claims** (fundada 2019). → expande **Third-Party Casualty**.
- Histórico: **Auto Injury Solutions** (casualty/medical bill review) y otras integradas en la suite Casualty. `[PARCIAL-VERIFICADO]`

**Categoría:** **SaaS / DaaS para la economía de seguros P&C de auto** — no es editor de guía de valores. Combina **valoración de total loss (ACV)**, **estimación de reparación (collision estimating)**, **gestión de siniestro (claims management/FNOL)**, **casualty (lesiones)**, **subrogación**, **pagos**, **datos de vehículo/VIN/equipamiento** e **IA de visión por computador**.

**Clientes objetivo (verticales declarados):** **Insurance Carriers** · **Collision Repairers** · **Auto Manufacturers (OEMs)** · **Parts Suppliers** · **Lenders** · **Fleet Operators** · **Independent Appraisers**. Tracción declarada: **300+ aseguradoras** (18 de las top 20 / "18 de top 20 carriers"); **30.500+ talleres de colisión** (~27.000 repair facilities); **5.000+ parts suppliers**; **12 de los top 15 OEMs**; **700+ medical professionals** (13 de top 15 medical providers); **4.000+ talleres usando IA de CCC**; **100+ aseguradoras usando IA de CCC**.

---

## 2. Cobertura

- **Geografía:** **Estados Unidos** (núcleo absoluto). La valoración MVR aplica a vehículos US-spec y se ajusta por **jurisdicción estatal/municipal** (tasas de impuesto y fees por estado/municipio; "may vary based on state-specific regulations"). **Sin cobertura europea ni española.** ← hueco mayor para cardeep. `[VERIFICADO por ausencia + nota state-specific en MVR]`
- **Nuevo y usado:** el foco es el **valor de mercado del vehículo siniestrado (usado)** para liquidación de total loss; usa **comparables de mercado** (coches a la venta en concesionario/anunciados). No publica "valor de coche nuevo" como guía; el MSRP/configuración nueva entra como dato de equipamiento.
- **Tipos de vehículo / activo:**
  - **PPV — Private Passenger Vehicles** (núcleo: coches, SUV, light trucks).
  - **CRV — Commercial and Recreational Vehicles**, valorados por un **equipo de 160+ expertos de línea de producto**: **motorcycles, scooters, boats, trucks, motorhomes, RVs y más**. (Producto **CCC ONE Valuation with CRV Services**, con datasheet propio.)
  - **Motorcycle** tiene **calculadora de fees específica por clase de moto**.
- **Profundidad de dato de referencia (declarada en la FAQ de Valuation):**
  - **7,6 M comparable vehicles** (inventario de comparables disponibles).
  - **41k+** municipality tax rate data (tasas de impuesto municipal).
  - **53k+** state and local fees.
  - **3k dealership inspections** con **metodología de valoración por jurisdicción**.
- **Escala de la plataforma (no solo valoración):** **24M+ estimates/año** procesados para talleres; **20M+ parts quoted/día** vía CCC ONE; **18M+ claims/año**.
- **Frescura:** valoración **on-demand por siniestro** (no es guía periódica); comparables reflejan **precios de mercado actuales** (advertised/inspected dealer prices) en el momento del informe.

---

## 3. Productos + campos atómicos

> CCC organiza por **vertical de cliente**. El núcleo cardeep-relevante es **APD → Claims Valuation** (total loss). Se documenta primero y a máximo detalle.

### 3.1 CCC® Valuation / CCC ONE® Valuation — núcleo total loss (el producto cardeep)

**Qué es:** *"Deliver valuations representing a vehicle's fair market value based on CCC's market-driven valuation methodology."* Entrega el **Market Valuation Report (MVR)** = Actual Cash Value (ACV) del vehículo siniestrado. **"#1 in Valuations" — el proveedor líder de valoraciones de vehículo de EE. UU.**

**Líneas de servicio:**
- **Valuation – PPV** (Private Passenger Vehicles): equipo de CCC gestiona la valoración.
- **Valuation – CRV** (Commercial & Recreational Vehicles): motos, scooters, barcos, camiones, motorhomes, RVs (160+ expertos).

**Features nombrados del producto Valuation:**
| Feature | Detalle atómico | Fuente |
|---|---|---|
| **Build Sheets** | Trae los detalles del vehículo de total loss para asegurar que **opciones y paquetes** se consideran correctamente (build data de fábrica). | claims-valuation |
| **Salvage Assignment** | Asigna el **salvamento** directamente a salvors según el workflow del carrier. | claims-valuation |
| **Branded Title** | Acceso a **branded titles existentes** y comparables con título de marca. | claims-valuation |
| **Fee Calculator** | Aplica automáticamente **fees fijados por la aseguradora** para inclusión en el MVR. | claims-valuation |
| **Motorcycle Fee Calculator** | Listado de fees por **clase de motocicleta**, activables/desactivables por el claim professional. | claims-valuation |

**Campos ATÓMICOS del Market Valuation Report (MVR)** — fuente primaria: **PDF oficial de CCC "How to Read the Market Valuation Report" (©2015-2024, 11 pp.)**:

**(A) Report Summary Page (pág. 1):**
- **Claim Information:** `Owner`, `Garage Location`, `Loss Vehicle`.
- **Insurance Information:** `Report reference number`, `Claim reference number`, `Adjuster name`, `Appraiser name`, `Odometer`.
- **Valuation Summary:** `Base Vehicle Value`, `Condition Adjustment`, `Adjusted Vehicle Value`, `Total (Valuation)`.
- **Table of Contents** (esquina inferior derecha) + **Side Bar** (definiciones de términos).
  - *`Base Vehicle Value`* = derivado de la metodología de mercado (pág. 2).
  - *`Adjusted Vehicle Value`* = Base ajustado por **condición real** del loss vehicle + atributos reportados (**refurbishments**, **after-factory equipment**).

**(B) Vehicle Information (varias páginas):**
- **Vehicle Details:** `Location`, `VIN`, `Year`, `Make`, `Model`, `Trim`, `Body Style`, `Body Type`, `Engine`, `Transmission`, `Curb Weight`.
- **Vehicle History Summary:** `Experian AutoCheck`, `NICB (National Insurance Crime Bureau)`, `NHTSA`.
- **Vehicle Equipment:** `Standard` (equipamiento de base de fábrica) y `Additional Equipment` (no estándar, detectado en el loss vehicle) — marcados con iconos.

**(C) Vehicle Condition:**
- `Condition Ratings` (seleccionados por el appraiser, por componente) + **value impact** de cada rating.
- `Inspection Notes` (observaciones del appraiser) + `Inspection Guidelines`.
- `Total Condition Adjustments` (suma al pie). *Nota CCC: la terminología de condition rating varía por aseguradora.*

**(D) Comparable Vehicles** (el corazón del valor):
- Formato expandido: **hasta 3 comparables por página**, con **option configuration de cada comparable vs. loss vehicle**.
- Por comparable: `List Price` (sticker price de un inspected dealer vehicle / **advertised price** del vehículo anunciado), `Take Price` (precio que el dealer aceptaría; puede bajar por negociación), `Distance` (línea recta loss↔comparable).
- `Adjusted Comparable Value` = importe tras ajustes por **make/model/trim, options, mileage** para llevar el comparable a un **nivel de condición común**.
- `Additional Comparable Vehicles` (comparables extra en formato resumen; mismo ajuste).
- *Aviso CCC:* los comparables **no pretenden ser vehículos de reemplazo**, reflejan **market value** y pueden ya no estar a la venta.

**(E) Valuation Notes:** notas de total-loss request del appraiser + notas del sistema/staff de Valuation.

**(F) VINguard® Vehicle History (opcional):** `Experian AutoCheck`, `NICB`, `NHTSA`, `collision history`, `previous sales`, `vehicle title information`; detecta **odometer rollbacks**, **prior potential total loss**, **unrelated prior damage**.

**(G) NHTSA Vehicle Recall (opcional):** info de **recalls** del loss vehicle según NHTSA.

**Ajustes (cuantías, de fuentes de litigio de terceros — no publicadas por CCC):**
- **Mileage adjustment:** típicamente **$0,02–$0,15 por milla** de diferencia (positivo o negativo). `[3ª fuente]`
- **Condition adjustment / "uniform condition adjustment":** corrige la diferencia entre vehículos en **"dealer ready" condition** y vehículos privados en **"normal wear"** condition; basado en guidelines por **edad** del vehículo (escala citada por terceros como **Poor → Fair → Good → Very Good → Excellent**). `[3ª fuente; CCC dice "varía por compañía"]`
- **Options/Equipment adjustment:** crédito (+) por opciones que el loss tiene y el comparable no; deducción (−) inversa.
- **Typical Negotiation adjustment:** ≈ **4–7%** de reducción sobre el advertised price (refleja el descuento "take vs list"). `[3ª fuente]`
- **Salvage / Rebuilt title deduction:** las aseguradoras **deducen 20–40%** del valor. `[3ª fuente]`
- **Sales tax** por municipio (41k+ jurisdicciones) + **state/local fees** (53k+) vía Fee Calculator.
- Recuento de comparables: **"hasta 3 por página"** (formato CCC); terceros citan **~12 comparables** habituales (típicamente 4–12). `[CONFLICTO display vs total; reportado tal cual]`

### 3.2 CCC® Quick Valuation — captura móvil self-service (acelerador de total loss)

App móvil que el cliente final usa para **acelerar el procesamiento del total loss**. Campos/capacidades:
- **VIN Capture** (escaneo y decodificación de VIN).
- **Clear Photo & Video Capture** con **blur detection** (control de calidad de foto).
- Captura de **vehicle options** y **mileage**.
- **Automated Results**: los assets se añaden automáticamente al **claim folder**.
- **Integration with Smart Total Loss**: capa extra para claims que pasaron por photo estimating + Smart Total Loss.
- Variantes: **Quick Val – Insurance** (según MOI/estimate data), **Quick Val – Salvor** (integra con salvage assignments), **Quick Val – Repair Facility** (talleres capturan opciones vía **build sheet data**).
- **KPI:** reduce el ciclo de FNOL→valuation una media de **3,4 días**.

### 3.3 CCC® Mobile Appraiser Pro — app de field appraiser

App para **field appraisers**: conecta con herramientas AI de **estimate o valuation**, guía la captura de **fotos/vídeos** de soporte, permite **identificar partes dañadas**, y comparte a sistemas del carrier.

### 3.4 CCC® First Look — claims management / FNOL (predicción de total loss temprana)

IA aplicada a fotos **inmediatamente tras First Notice of Loss**. Campos/predicciones:
- **AI predictions:** `repairability vs. total loss`, `primary point of impact`, y más, vía **vehicle damage photo analysis**; routing del claim al siguiente paso según reglas.
- **Photo Validation** (calidad de fotos unguided), **Photo Ingesting** (camera roll, guided app, salvage vendor, repair facility).
- **Datos capturados digitalmente al crear el claim:** `VIN`, `Odometer Readings`, `Vehicle Location`, `License Plate States/Numbers`, y más.
- **KPI:** ahorro medio de **1,5 días** cuando el claim empieza con First Look.

### 3.5 CCC® Estimating (APD, lado aseguradora) — estimación de reparación

| Subproducto | Campos / capacidades | Fuente |
|---|---|---|
| **CCC Intelligent Estimating** | Estimaciones **line-level** en segundos sobre vehículos reparables con IA; **Parts Sourcing** (disponibilidad + recomendación de parts según reglas); **AI-Built Estimates**: predicciones de `repair or replace`, `remove and install (R&I)`, `labor hours`, `blend procedures`. IA escribe **≥80%** de las líneas alineadas a reglas del insurer. | claims-estimating |
| **CCC Advanced Estimating** | `Field Appraiser Estimates` (app móvil), `CRV Estimates` (consumidor sube detalles+fotos), `PPV Estimates` (self-service). | claims-estimating |
| **CCC Core Estimating** | Punto único de acceso a data + supplier network + herramientas de estimación. | claims-estimating |
| **KPI** | 30% de ganancia de eficiencia por estimate (caso de carrier nacional). IA entrenada en base histórica deidentificada de claims + **millones de fotos de daño**. | claims-estimating |

### 3.6 Otros productos APD (aseguradora)

- **Claims Processing** / **Smart (Estimate STP)** — straight-through processing de estimación por foto; **Smart Total Loss**; **Smart Audit**.
- **Claims Reinspection** — reinspección asistida por IA.
- **Fraud Solutions** — **Smart Red Flag Detection**.
- **Incident Detection & Management** — **Accident Documentation**, **Predictive Method of Inspection (MOI)**.
- **Telematics**.

### 3.7 Casualty (lesiones / bodily injury)

- **First Party Casualty:** intelligent rules engine para routing + **bill reimbursement recommendations** según guidelines del insurer.
- **Third Party Casualty:** workflow end-to-end de settlement por reglas configurables (reforzado por **EvolutionIQ** desde 2025).
- Capacidades: claim segmentation automatizada, automatización de tareas, análisis de injury claim data; **700+ medical professionals**.

### 3.8 Subrogation

- **Inbound Subrogation:** evalúa demandas en minutos usando **parts history automatizado** + audit rules; repairable y total loss.
- **Outbound Subrogation:** **detection models** entrenados por profesionales de subrogación para auto, property y workers' comp; prioriza oportunidades y genera demandas. (Base: adquisición **Safekeep**.)

### 3.9 Payments

- **Enterprise Payments / Insurer Payments** — pagos end-to-end del siniestro; también **Shop Payments**, **OEM Payments**, **Parts Payments**, **consumer financing**.

### 3.10 Lado Collision Repairer (CCC ONE)

- **CCC ONE Estimating** (`cccone.com` + **CCC ONE Mobile App**): estimación line-level; **parts pricing/availability en tiempo casi real**; **OEM Repair Methods**; insurer guidelines; **Mobile Jumpstart** (estimate preliminar en <2 min); VIN scan/decode; damage photos; **Shop-Configured AI Settings** (confidence thresholds). **24M+ estimates/año**, **20M+ parts quoted/día**.
- **Repair Workflow** (parts, payroll, diagnostics), **Repair Quality / Repair Methods**, **Diagnostics Workflow**.
- **Consumer Engagement:** **Engage**, **Carwise**, **Amplify**, websites, online scheduling, **consumer financing**, surveys, **reputation management**, repair status updates.
- **Shop Management / ELEVATE by CCC**, **Parts (Network + Ordering)**.

### 3.11 Lado OEM y Parts Suppliers

- **OEM:** Certified Network & Programs, **OEM Analytics**, **OEM Parts**, **OEM Payments**, **VIN Connect**, **Accident Advisor**.
- **Parts Suppliers:** **Parts Network** (pricing+availability a talleres), **Recyclers** (yard management), **Parts Payments**.

### 3.12 Tecnología transversal

- **CCC IX Cloud™** (Intelligent Experiences) — plataforma event-driven, microservicios, sobre apps cloud existentes.
- **Data + AI:** **Predictive AI** (datos históricos), **Deep Learning AI** (computer vision sobre fotos/vídeo: repairability, estimate creation, repair vs replace, injury predictions, subrogation demands), **Generative AI** (síntesis de datos, comunicaciones). **100+** data scientists/engineers/physicists. **>$1 billón** de datos históricos.

---

## 4. Metodología / fuentes de datos

**Metodología de valoración (declarada como "market-driven"):**
1. **Identificar y configurar** el loss vehicle (VIN decode → year/make/model/trim/body/engine/transmission + equipment standard/additional).
2. **Localizar comparables** de mercado: vehículos **anunciados por dealers** (advertised price) e **inspected dealer vehicles** (sticker `List Price` + `Take Price`), priorizados por proximidad (`Distance` en línea recta) y similitud (make/model/year/mileage). Pool de **7,6M comparables**; **3.000 dealership inspections** con metodología por jurisdicción.
3. **Ajustar cada comparable** a un nivel de condición común: por make/model/trim, **options**, **mileage** → `Adjusted Comparable Value`.
4. **Calcular** `Base Vehicle Value` promediando los comparables ajustados; luego aplicar `Condition Adjustment` (condición real del loss vehicle) → `Adjusted Vehicle Value`.
5. **Añadir** sales tax (41k+ municipios) y **state/local fees** (53k+) vía Fee Calculator → `Total` (ACV de liquidación).

**Fuentes de dato integradas:**
- **Inventario de comparables:** precios de dealer **anunciados** + **inspecciones físicas de dealer** (List/Take price).
- **Build / equipment data:** OEM build sheets (opciones/paquetes por VIN).
- **Historial de vehículo:** **Experian AutoCheck**, **NICB**, **NHTSA** (+ **CCC VINguard** para collision history, previous sales, título, odometer rollback, prior total loss).
- **Fiscalidad/fees:** bases de tasas municipales/estatales propias.
- **IA:** base histórica **deidentificada** de claims + **millones de fotos** de daño (computer vision) para predicciones (repairability, total loss, MOI, estimate STP).

**Crítica/litigio (relevante a la metodología):** múltiples demandas alegan que la **"uniform condition adjustment"** y el **"typical negotiation" (take vs list)** **infravaloran sistemáticamente** los total loss. El **DA de California demandó (may-2024) a USAA, Progressive, CCC y Mitchell** por presunta infravaloración coordinada; class actions contra State Farm (NC, TN). Un **panel de apelación dividido (jul-2023) avaló** valoraciones hechas con software de CCC. CCC sostiene que es una **herramienta** y que el carrier la **configura** ("may vary based on your company's configuration"). `[VERIFICADO 2+ fuentes; señala riesgo reputacional/regulatorio, no defecto probado]`

---

## 5. Entrega (delivery)

| Canal | Detalle |
|---|---|
| **Market Valuation Report (MVR)** | **PDF estructurado de ~11+ secciones** entregado dentro del expediente del siniestro (Report Summary, Vehicle Info, Condition, Comparables, Valuation Notes, VINguard, Recall). Configurable por carrier y por estado. |
| **App CCC ONE (desktop + web `cccone.com`)** | Plataforma del taller/appraiser: estimating, valuation lookup, workflow. |
| **CCC ONE Mobile App** (iOS/Android) | VIN scan/decode, damage photos, **Mobile Jumpstart**. |
| **CCC Quick Valuation** (app móvil) | Self-service del consumidor / salvor / repair facility para captura de fotos+opciones+mileage. |
| **CCC Mobile Appraiser Pro** (app) | Field appraisers: estimate/valuation + fotos/vídeo + identificación de partes. |
| **CCC IX Cloud / API / event-driven** | Integración entre carriers, talleres, OEMs, parts, lenders, salvors; intercambio de **lienholder info, valuation reports, title info**; integraciones con salvage yards. |
| **Datasheets / Solution briefs** | p.ej. **"CCC ONE Valuation with CRV Services Datasheet"**, "Crash Course" (informe trimestral de tendencias). |
| **Ecosystem** | Red de **35.000+** empresas conectadas (one connection). |

---

## 6. Precio (modelo)

- **No hay tarifas públicas.** Modelo **SaaS por suscripción + enterprise negociado**. Valuation/APD/Casualty/Subrogation = **contrato enterprise con aseguradora** (volumen de claims). CTA omnipresente: *"Request More Info" / "Let's Connect"*.
- **Lado taller (CCC ONE):** **4 ediciones de pricing** (Capterra/G2); add-ons "Power-Ups" (p.ej. **RPS – Recycled Parts Search**); reputado como **"de los más caros del mercado"**; coste final **negociado** según paquete del taller. `[VERIFICADO existencia de tiers; importes NO públicos]`
- **Add-on con micro-tarifa documentado:** la **Fee Calculator** y presets de fees existen como documento de configuración; CCC no publica precio por MVR. `[NO-VERIFICADO importe por informe]`

---

## 7. Placement (dónde colocan CADA dato — patrón a copiar por cardeep)

> CCC es el **mejor modelo del set para cardeep en el patrón "ficha de valoración de un vehículo concreto"**, porque el MVR es literalmente una ficha estructurada de un vehículo con su valor, comparables y ajustes. El flujo es **siniestro-céntrico**, no catálogo-céntrico.

**A. Report Summary Page (la "portada de valor" — patrón canónico).** Arriba, juntos: **`Base Vehicle Value` → `Condition Adjustment` → `Adjusted Vehicle Value` → `Total`** (ACV). Un solo bloque-resumen con la cifra titular y el desglose de cómo se llega a ella. A la derecha, **Table of Contents**; en el lateral, un **Side Bar** con **definiciones** de cada término (glosario inline) — patrón excelente para que cardeep explique cada métrica donde aparece.

**B. Vehicle Details (ficha de identidad del coche).** Bloque con `VIN, Year, Make, Model, Trim, Body Style, Body Type, Engine, Transmission, Curb Weight, Location`. Es la cabecera de identidad — cardeep la replica como cabecera de su ficha de punto/vehículo.

**C. Vehicle Equipment (sección de specs/opciones).** Lista de equipamiento separada en **`Standard` vs `Additional`** con iconos. Patrón claro para mostrar specs/equipamiento por VIN distinguiendo de serie vs. extra.

**D. Vehicle History (sello de confianza).** Resumen de **AutoCheck/NICB/NHTSA** arriba + **VINguard detallado** y **NHTSA Recall** más abajo (collision history, previous sales, title, odometer rollback). El historial vive como **sección dedicada**, no mezclado con el valor.

**E. Vehicle Condition (panel de ajuste por estado).** Tabla de **condition ratings por componente** con el **value impact** de cada uno + `Inspection Notes` + `Total Condition Adjustments` al pie. Patrón: cada factor que mueve el precio se muestra con su impacto en €/$.

**F. Comparable Vehicles (el comparador / prueba del valor).** Hasta **3 comparables por página**, cada uno con `List Price`, `Take Price`, `Distance`, **option configuration vs. el loss vehicle**, y `Adjusted Comparable Value` al final. Es el patrón **"así llegué a tu valor: estos coches reales del mercado, ajustados"** — directamente transplantable a cardeep para justificar un valor con comparables localizados.

**G. Valuation Notes (transparencia/auditoría).** Notas del appraiser + del sistema, al lado del valor. Patrón de trazabilidad.

**H. Captura previa (Quick Valuation / First Look).** El **input** del dato se coloca en una **app móvil guiada** (VIN scan, fotos con blur detection, opciones, mileage) *antes* de la ficha — separa "captura" de "informe". First Look inyecta **predicciones tempranas (total loss sí/no, punto de impacto)** en el workflow del adjuster, no en una pantalla aparte.

**I. Estimating (ficha de reparación, no de valor).** Estimate **line-level** con repair/replace, R&I, labor hours, blend, parts en tiempo real — vive en el flujo del taller (`cccone.com`/app), separado del MVR pero conectado por el IX Cloud.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Estándar de facto del total loss de EE. UU. (~75% de cuota):** la valoración no es una "guía" que consultas, es el **motor de liquidación embebido** que usan State Farm, GEICO, Allstate, Nationwide, Liberty Mutual, Progressive, USAA. Aceptación operativa difícil de replicar.
2. **Valoración por COMPARABLES DE MERCADO con `List`/`Take Price` e inspecciones físicas de dealer**, no por extrapolación de subasta (KBB/Black Book) ni transacción retail agregada (J.D. Power PIN). Modelo distinto: "estos coches concretos a la venta cerca de ti, ajustados".
3. **El dato vive dentro del WORKFLOW de siniestro end-to-end:** FNOL → foto-IA (First Look) → estimate → total loss decision → MVR → salvage → payment → subrogation. Ningún "libro de valores" tiene este pipeline.
4. **IA de visión por computador a escala industrial:** repairability vs total loss, punto de impacto, estimate line-level desde fotos (≥80% de líneas), MOI — sobre **millones de fotos** y **>$1B de datos**.
5. **MVR como ficha de valor ultra-estructurada y auditable** (comparables con distancia/opciones, condition por componente, fees por municipio, glosario lateral) — el mejor patrón de "placement de ficha de valor" del set.
6. **Cobertura CRV con equipo experto:** motos, barcos, RVs, motorhomes, camiones (160+ expertos) + fee calculator por clase de moto.
7. **VINguard:** historial propio integrado (collision, previous sales, title, odometer rollback, prior total loss) sobre AutoCheck/NICB/NHTSA, embebido en el MVR.
8. **Fiscalidad hiperlocal:** 41k+ tasas municipales + 53k+ state/local fees aplicadas automáticamente al settlement.
9. **Ecosistema de 35.000+ empresas** (carriers + talleres + OEMs + parts + lenders + salvors + medical) bajo una conexión — DaaS + SaaS + payments.
10. **Expansión a casualty/injury con IA (EvolutionIQ, Safekeep):** más allá del valor del coche, hacia lesiones y subrogación.

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Solo EE. UU.** — sin Europa/España; valor atado a jurisdicción US y a fees estatales. ← hueco mayor para cardeep.
2. **No es guía de valor consultable ni producto de consumidor:** el ciudadano **no compra** un "valor CCC"; solo recibe un MVR cuando su aseguradora declara total loss. Sin lookup público de precio, sin app de consumidor tipo KBB.
3. **No vende dato de mercado independiente** (residual %, days-to-sell, market days supply, price-to-market %, índice oferta/demanda, curva de depreciación) como producto. **No hay índice de mercado** estilo UVPI (J.D. Power) ni UVI (Black Book) ni residuales/forecast de leasing.
4. **No cubre valor de coche nuevo / MSRP como guía**, ni residual/forecast para leasing/lending (su vertical Lenders es de claims, no de book value).
5. **Metodología propietaria y opaca**, bajo litigio activo (CA DA, class actions) por presunta infravaloración (uniform condition adjustment, typical negotiation/take-vs-list). Riesgo regulatorio/reputacional. `[VERIFICADO litigio; no defecto probado]`
6. **Pricing totalmente opaco** (enterprise/quote); fricción de descubribilidad.
7. **Valor on-demand por siniestro, no serie temporal:** no publica histórico de precios ni tendencia descargable a nivel vehículo (el "Crash Course" es agregado de industria, no dato de coche).
8. **Condición y opciones dependen del appraiser/foto**, no de telemetría/odómetro en vivo (aunque First Look/Quick Val digitalizan la captura).
9. **Historial = terceros** (Experian AutoCheck/NICB/NHTSA) reempaquetado en VINguard; no es dataset propio descargable.
10. **Comparables pueden "ya no estar a la venta"** (CCC lo advierte): reflejan market value, no inventario vivo garantizado — distinto del censo de inventario vivo que persigue cardeep.

---

## 10. Fuentes

**Sitio CCC (vía Wayback Machine `id_`, por Cloudflare 403 en acceso directo):**
- Home: https://www.cccis.com/ (35.000+, 300+ insurers, 18M+ claims, $1T datos, 12 de top 15 OEMs)
- Insurance Carriers (overview): https://www.cccis.com/insurance-carriers
- **Claims Valuation** (CCC Valuation, PPV/CRV, Build Sheets, Salvage Assignment, Branded Title, Fee Calculator, 7.6M/41k/53k/3k/160+): https://www.cccis.com/insurance-carriers/apd/claims-valuation
- Total Loss Management (CCC ONE Valuation "market-driven fair market value", Quick Valuation, Mobile Appraiser Pro, #1 in Valuations, 3.4 días): https://www.cccis.com/insurance-carriers/claims-solutions/apd/total-loss-management
- Quick Valuations (VIN capture, blur detection, Smart Total Loss, Salvor/Repair Facility): https://www.cccis.com/insurance-carriers/claims-solutions/apd/total-loss-management/quick-valuations
- Claims Management / **CCC First Look** (FNOL AI, repairability vs total loss, primary point of impact, VIN/Odometer/Location/Plate, 1.5 días): https://www.cccis.com/insurance-carriers/apd/claims-management
- Claims Estimating (Intelligent/Advanced/Core, AI ≥80% líneas, R&I, blend, labor hours, 30%): https://www.cccis.com/insurance-carriers/apd/claims-estimating
- Casualty (First/Third Party): https://www.cccis.com/insurance-carriers/casualty
- Subrogation (Inbound/Outbound, Safekeep): https://www.cccis.com/insurance-carriers/subrogation
- Data + AI (Predictive/Deep Learning/Generative, 100+ scientists): https://www.cccis.com/our-technology/ai
- CCC ONE Estimating (repairer; 24M estimates/año, 20M parts/día, Mobile Jumpstart, cccone.com; menciona adquisición EvolutionIQ): https://www.cccis.com/collision-repairers/ccc-one/estimating
- Automaker IX (CCC IX Cloud detalle; CRV Services Datasheet): https://www.cccis.com/automakers-ix

**Documento oficial de CCC (campos del MVR — fuente primaria de campos atómicos):**
- **"How to Read the Market Valuation Report"** (PDF, ©2015-2024, 11 pp., vía Wayback): https://help.cccis.com/training/insurance_company/cat-training/HowToReadAnMVR.pdf

**Identidad / corporativo:**
- Fundación 1980 / Tullman / Certified Collateral Corp / HQ Merchandise Mart / EZNet: https://www.encyclopedia.com/books/politics-and-business-magazines/ccc-information-services-group-inc · https://www.referenceforbusiness.com/history/Ca-Ch/CCC-Information-Services-Group-Inc.html
- SPAC Dragoneer / Advent / Oak Hill / $7B: https://oakhill.com/2021/02/03/ccc-information-services-inc-and-dragoneer-growth-opportunities-corp-announce-business-combination/ · https://www.insurancebusinessmag.com/us/news/technology/ccc-information-services-to-go-public-with-7-billion-merger-deal-245534.aspx
- NASDAQ/CEO/revenue/employees: https://stockanalysis.com/stocks/ccc/company/ · https://www.crunchbase.com/person/githesh-ramamurthy
- Adquisición EvolutionIQ ($730M, ene-2025): https://ir.cccis.com/news-releases/news-release-details/ccc-intelligent-solutions-completes-acquisition-evolutioniq · https://www.businesswire.com/news/home/20250430540969/en/
- Adquisición Safekeep (subrogación, 2022): WebSearch (cccis news)

**Terceros (campos del informe + cuota + metodología + litigio):**
- SecondAppraisal (anatomía MVR, 4 ajustes, condición Poor-Excellent, typical negotiation 4-7%): https://secondappraisal.com/guides/ccc-one-valuation-report-explained · https://secondappraisal.com/glossary/ccc-one
- SnapClaim (estructura del report, condición/mileage/options): https://snapclaim.com/ccc-one-market-valuation-report/ · https://snapclaim.com/ccc-one-market-valuation-report-flaws/
- DiminishedValueExpert (claim header, summary, take vs list): https://diminishedvalueexpert.com/what-is-a-ccc-report/
- AutoClaimConsultants (base value, comparables, mileage $0.02-$0.15): https://autoclaimconsultants.com/2026/02/ccc-one-total-loss-valuation-guide/
- MyDVAC / MyFairClaim (75% cuota, carriers, salvage 20-40%): https://www.mydvac.com/blog/total-loss-settlements-ccc-is-it-accurate/ · https://myfairclaim.com/ccc-one-total-loss-valuations-state-farm-lawsuits/
- Claims Journal (panel de apelación avala CCC, jul-2023): https://www.claimsjournal.com/news/southeast/2023/07/06/317896.htm
- Repairer Driven News (CA DA demanda a USAA/Progressive/CCC/Mitchell, may-2024): https://www.repairerdrivennews.com/2024/05/14/california-da-sues-insurers-estimating-system-providers-over-alleged-lowball-total-loss-payouts/
- Capterra/G2 (4 pricing editions, Power-Ups): https://www.capterra.com/p/83656/CCC-ONE-Total-Repair-Platform/

### Notas de verificación
- **Campos del MVR (Base/Condition/Adjusted/Total, Vehicle Details, Equipment Standard/Additional, Comparables List/Take/Distance/Adjusted, VINguard, Recall):** **[VERIFICADO]** — PDF oficial de CCC + corroborado por guías de terceros.
- **Cuantías de ajuste (mileage $0.02-$0.15, negotiation 4-7%, salvage 20-40%, condición Poor-Excellent):** **[3ª FUENTE — no publicadas por CCC]**; CCC declara que la config/terminología varía por carrier.
- **Cuota ~75%:** **[3 fuentes terceras coincidentes; no cifra oficial CCC]**.
- **Revenue FY2024 (~$944,8M vs $926,2M):** **[VERIFICADO con discrepancia de fuente]**.
- **HQ dirección exacta (222 Merchandise Mart Plaza ste 900 / 444 Merchandise Mart):** **[PARCIAL]** — Chicago confirmado; suite puede haber cambiado.
- **Recuento de comparables (3/página vs ~12 total):** **[CONFLICTO display vs total, reportado tal cual]**.
- **`valuation.cccis.com` no existe (DNS 000); cccis.com/cccone.com = 403 Cloudflare:** **[VERIFICADO]**.
- **Litigio de infravaloración:** **[VERIFICADO existencia de demandas]**; no implica defecto probado (panel de apelación avaló en 2023).
