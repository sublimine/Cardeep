# JATO Dynamics — Auditoría atómica

> Slug: `jato-dynamics` · Subdominio cardeep: **spec-catalog** · Región: **Global** (specs 50+ países; capas de mercado/finanzas EU-céntricas)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó; `[PARCIAL]` donde la fuente no enumera al detalle.
> Naturaleza: **el catálogo de especificaciones de coche NUEVO de referencia mundial** + capa de inteligencia de mercado (matriculaciones/volúmenes,
> precios de lista, incentivos/descuentos, cuotas mensuales, benchmarking de dealer). NO es una tabla de valor residual ni un historial de vehículo:
> la valoración de usado y el residual los aporta vía **alianza con autobiz** (2025). Su átomo es el **dato técnico/equipamiento/precio de lista
> estandarizado y comparable entre marcas** — exactamente el núcleo del subdominio `spec-catalog` de cardeep.
> Marca pública: **JATO** · sitio: `jato.com` · developer portal: `developer.jato.com` (JaaS) · app de specs: `carspecs5.jato.com`.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre legal | **JATO Dynamics Limited** (marca pública: **JATO**) | Companies House; jato.com |
| Company number | **02262299** (England & Wales) — *"Registered in England No: 2262299"* en sus PR | GOV.UK Companies House; PR JATO Volumes 2023 |
| Fundación (operativa) | **1984** — *"In 1984, we revolutionised the use of data in the automotive industry"* | jato.com/about-us |
| Entidad Ltd (incorporación registral) | **26-may-1988** (la sociedad limitada actual; trading desde 1984) | uk.globaldatabase.com |
| Fundador | **Jake Shafran** (Jacob Baruch Shafran) — **Founder & Chairman** | Wikipedia; WebSearch (Bloomberg/Crunchbase) `[VERIFICADO]` |
| CEO | **Andy Rothery** | WebSearch agregada `[VERIFICADO]` |
| HQ | **Building 1, ARC Uxbridge, Sanderson Road, Uxbridge, UB8 1DH, United Kingdom** (Uxbridge, Gran Londres) | jato.com/about-us; Companies House |
| Owner / grupo | **Privada, controlada por el fundador**. Ultimate parent = **JATO HOLDINGS LIMITED**. PSC=4 | Companies House (PSC) |
| Estructura accionarial | **JATO Holdings Ltd** 1.217.735 Ord A · **JATO Nominees Ltd** 94.500 Ord B + 30.000 Ord C · **Jacob Baruch Shafran** 12.265 Ord A | Companies House PSC; uk.globaldatabase.com |
| Financiación externa | **Ninguna** (sin PE/VC; *"has not raised any funding"*) | Tracxn/ZoomInfo vía WebSearch `[PARCIAL]` |
| Empleados | **800+** *"experts in over 50 countries"* (marketing) · **770** en cuentas 2023 (-1% YoY) | jato.com/about-us; uk.globaldatabase.com (accounts 2023) |
| Financieros 2023 (UK accounts) | **Turnover £83 M · Gross profit £64 M · EBITDA £14 M · PAT £11,6 M · cash £2 M** | uk.globaldatabase.com `[VERIFICADO vía accounts]` |
| Escala de datos | **250 M+ live vehicle data points** (About) · **375 M data points** (Specifications) · **~75.000 market events/mes** · **1.000 datapoints/coche** | jato.com/about-us; /our-capabilities/specifications |
| Cobertura declarada | **50+ países · 200+ marcas · 1.800+ modelos** · *"40 years of excellence"* | jato.com (specs, integrated solutions) |
| Tagline / misión | *"The global hub for automotive market intelligence and analysis"*; *"Delivering transparency… through accurate, impartial global market intelligence"* | jato.com (home, about) |
| Tech stack | **Microsoft Azure**: Cosmos DB, Azure SQL, Azure AI Search, Data Factory, **Azure OpenAI**, App Service, Functions, Dynamics CRM | Microsoft Customer Story |

> ⚠ **Discrepancia menor de escala:** About declara *"250+ million live vehicle data points"* y la página Specifications *"375 M data points"*.
> Probable distinción **live (vivos hoy)** vs **total en base (incl. histórico)**. Se reportan ambas con su fuente. `[VERIFICADO con matiz]`

**Categorías (3 capabilities + APIs):**
1. **Specifications** — el catálogo técnico/equipamiento/precio de coche nuevo (núcleo histórico, "Carspecs").
2. **Analysis** — inteligencia de mercado: Volumes/matriculaciones (Nowcasting), Price Tracker, Incentives, Monthly Payments, Transaction/Sales Link, Benchmarking.
3. **JATO Advisory** — consultoría/informes a medida.
4. **Integrated Solutions / JaaS** — suite de APIs RESTful (developer portal) + Datafeed.

**Cliente objetivo (declarado):** **Automakers (OEM/OES) · Retail (dealers, marketplaces digitales, venta online) · Leasing & fleet management ·
Professional services (investment banks, financial services, consultoras) · Insurance · portales de automoción.**
*"The JATO client base includes all of the world's volume vehicle manufacturers."*

---

## 2. Cobertura

- **Specifications (núcleo):** **50+ países / mercados**, **200+ marcas**, **1.800+ modelos**, **passenger cars + LCV** (+ **quadricycle**, foco EU emergente). Actualización **diaria**.
- **Volumes / matriculaciones:** **40+ mercados** con **registros oficiales de matriculación**; integra forecast corto de **S&P Global Mobility**.
- **Incentives:** **13 mercados europeos**; **dato dealer-level EXCLUSIVO para EU5** (Alemania, Francia, Italia, España, Reino Unido); **10+ años** de histórico; **mensual**.
- **Monthly Payments:** **EU7** (UK, DE, FR, IT, ES, BE, NL); **80-85% del mercado local**, **50 marcas OEM**, **80+ modelos**; **semanal**.
- **VINView / VINView Pro:** **UK, FR, DE, IT, ES, BE, NL, LU** (8 mercados EU); specs JATO globales **50+ mercados**.
- **Sales Link:** **5 países** en vivo (benchmark de dealer); **55+ marcas**.
- **JATO Index:** specs sin VIN, histórico **desde 2010**.
- **Valoración de usado / residual (vía autobiz):** **22 países europeos** (autobiz: Paris, Berlin, Valencia, Milan; 20+ años de datos de usado EU).
- **Scope nuevo/usado:** **NUEVO = núcleo** (specs, precio de lista, incentivos, cuotas, volúmenes). **USADO = identificación** (VINView Pro decode + *price when new*); **valoración/residual NO nativa** (autobiz).
- **Tipos de vehículo:** **turismo + LCV/furgoneta** (+ cuadriciclo). **Camión pesado / moto: no enfatizados** `[VERIFICADO por ausencia]`.

---

## 3. Productos + campos atómicos

### 3.1 JATO Specifications (Carspecs / "Vehicle Viewer" / JATO Net) — el núcleo

> **1.000 datapoints por coche**, **375 M datapoints** en base, **200+ marcas**, **1.800+ modelos**, **50+ mercados**, **updates diarios**.
> Taxonomía **OEM-agnóstica** estandarizada **hasta nivel de versión**.

**Identificación (taxonomía):** `make` · `model` · `trim / grade` · `derivative / version` · `body style` · `model year` (taxonomy-aligned) ·
`fuel type` · `transmission` · `segment` (segmentación JATO) · **`JATO UID` / `Instance ID`** (identificador único global de cada instancia de vehículo).

**Dimensiones y pesos:** `length` · `width` · `height` · `wheelbase` `[PARCIAL]` · `vehicle dimensions` · `weight` (kerb/gross) · **`towing capacity`** ·
`boot / luggage capacity` `[PARCIAL]` · `fuel tank capacity` `[PARCIAL]`.

**Ruedas/neumáticos:** **`standard tyre sizes`** · **`optional tyre sizes`**.

**Motor / powertrain / prestaciones:** `engine` · `displacement` `[PARCIAL]` · `cylinders` `[PARCIAL]` · `power` · `torque` · `performance` (0-62 / top speed) `[PARCIAL]` ·
`drive type` · `transmission / gears` · `powertrain` (incl. **BEV / PHEV / HEV / ICE**).

**Consumo / emisiones:** `fuel consumption` · **`CO2 emissions`** · **`Electric Energy Consumption (EEC)`** (EV/PHEV) · `electric range` · **`WLTP values`** (vía WLTP Link).

**Equipamiento:** **`standard equipment`** (factory) · **`optional equipment`** · **`option packs / packages`** · **`colours`** (exterior + interior) **con códigos OEM oficiales** ·
`infotainment` · **`ADAS / safety / driver assistance`** (p.ej. lane assist) · `comfort & convenience` (p.ej. wireless charging) · `technical & performance attributes`.

**Reglas de configuración:** **`build rules`** · **`option interdependencies`** (dependencias entre opciones y spec estándar — grado configurador).

**Precios:** **`list price / RRP`** · **`price when new` / `original price at build time`** · **`option pricing`** · **`pack pricing`** · **`colour pricing`** ·
**`estimated pricing`** (decode VIN).

**Histórico:** modelos **current + historical** (JATO Index desde 2010).
**Entrega:** app web **Carspecs** (`carspecs5.jato.com`) / **Vehicle Viewer platform** · **Specifications API** (endpoints Vehicle Content, Options Build, Compare, Incentives) · **JATO Datafeed**.

### 3.2 VINView / VINView Pro — decode VIN/VRM → build exacto (API-first + web)

**Identificación:** `make` · `model` · `trim` · `derivative` · `body style` · `fuel type` · `transmission` · `model year` (taxonomy-aligned) · **`JATO ID`** (link de datos).
**Spec estándar (VINView):** cobertura OEM-standard completa: `safety / ADAS / driver assistance` · `comfort / convenience / infotainment` · `technical & performance`.
**Opciones de fábrica (VINView Pro):** **`factory exterior & interior colours`** · **`OEM pack content & configuration`** · **`technology & convenience add-ons`** · **`verified factory-fitted equipment`** (lo realmente instalado).
**Precio:** **`estimated pricing`** · **`original list price when new`**.
**Compañero — JATO Index:** specs **sin VIN** mediante filtros `make · model · year · fuel type · transmission · body style` (histórico **desde 2010**).
**Uso:** retail listings (usado), **stock acquisition** (auction/trade-in/part-exchange: distinguir spec real entre coches "iguales", fijar oferta por valor de equipamiento, detectar combinaciones premium, reducir riesgo de sobrepago).

### 3.3 JATO Incentives — descuentos públicos + dealer-level (EU5 exclusivo)

> **13 mercados EU**, **dealer-level EXCLUSIVO EU5**, **10+ años** histórico, **mensual**, **volume-weighted** (ponderado por mix de modelo).

**Tipos de incentivo:** `manufacturer rebates` · `cash contributions` · `scrappage schemes` · `government programmes` · `stock clearance discounts` · `dealer discounts`.
**Campos/métricas:** `list prices` · **`discount composition by category`** · **`potential / net transaction prices`** · **`incentive level distributions`** ·
`market share dynamics` · `competitor pricing structures` · **`registration volume correlations`** (cómo se distribuyen las ventas por nivel de incentivo y punto de precio).
**Entrega:** **7 dashboards pre-construidos** → `summary · trend · price · comparison · discount · volume · detailed` · **Incentives API endpoint**.

### 3.4 JATO Volumes with Nowcasting — matriculaciones + forecast corto

> **40+ mercados**, **registros oficiales**, integra **specs JATO + ventas históricas + forecast corto de S&P Global Mobility** → *"always on"* Nowcast hasta el mes **actual y siguiente**.

**Campos/métricas:** `registration / sales volumes` · `market size` · `trend` · `market share` · `segment performance` · `brand performance / positioning` ·
`fuel types / powertrains` (incl. **BEV**) · `pricing` · **`consumer option choices by market`** · **`quadricycle segment`** · **`short-term forecast`** (current + next month).
**Interfaz:** **ModelMix Navigator** (dashboards market share / segments / portfolio + custom query + integración con feeds existentes).
**Salida pública (marketing):** rankings **mensuales globales** (best-selling models/brands, BEV share, breakdown regional) — output de prensa de alto perfil.

### 3.5 JATO Price Tracker — precios de lista (RRP) y valor por equipamiento

**Campos:** **`RRP / Retail Recommended Prices`** · **`value through equipment changes`** (cómo cambia el valor al alterar equipamiento) · `price inflation metrics` · `value metrics` · `competitive positioning`.
**Dimensiones:** `country · make · model · segment · powertrain · body type · version` · **`JATO UID`** (análisis a nivel spec).
**Features:** **`unlimited baskets`** (sets competitivos personalizados) · one-click analysis · alertas de cambio de RRP / cambios de equipamiento de competidor.
**Frecuencia:** **`weekly`** (semanal) · **Entrega:** plataforma web (multidispositivo).

### 3.6 JATO Monthly Payments — affordability / oferta financiera (EU7)

> **EU7**, **80-85% del mercado**, **50 marcas**, **80+ modelos**, **70+ datapoints financieros**, **semanal**.

**Campos:** **`deposit amount`** · **`APR`** · **`monthly repayment / payment`** · **`external / manufacturer price contributions`** · **`contract type`** · **`contract duration / term`**.
**Canales/proveedores:** `retail` vs `business` channel · `captive` vs `non-captive` finance.
**Features:** comparación side-by-side de ofertas · gráficos/charts/dashboards personalizables.
**Entrega:** **JATO Account portal**.

### 3.7 JATO Sales Link — benchmarking de concesionario (transacción real anonimizada)

> **5 países** en vivo · **55+ marcas** · datos anonimizados de **miles de competidores** · construido sobre **Azure + Azure OpenAI**.

**KPIs/campos:** **`transaction / sales price`** · **`discount rates`** · **`feature / option popularity`** · **`days-to-sell`** · **`option uptake`** · **`model popularity`** · **`colour popularity`** ·
`market share` · breakdown de performance por **options / discounts / final sales price** **por site** y **vs competidores anonimizados** · acceso a **factory build-sheet specs**.
**IA:** **AI content generator** (artículos de web, posts de redes, newsletters auto-generados — vía Azure OpenAI). **Ahorro declarado ~32 h/mes por dealer.**

### 3.8 WLTP Link — emisiones/consumo por configuración (un punto de acceso multi-OEM)

> **200+ marcas / 1.800+ modelos**, real-time multi-OEM, sobre JATO Specifications.

**Campos:** **`CO2 emissions`** (por make/model/trim) · **`fuel consumption`** · **`Electric Energy Consumption (EEC)`** (EV/PHEV) · `electric range` ·
`standard & optional equipment` que afectan a **weight / rolling resistance / aerodynamics** · **cálculo WLTP instantáneo por configuración individual** · **total acquisition cost** (registration + tax implications).
**Uso:** quotes compliant, **car labels**, configuración dentro de presupuesto, compliance de política de flota. **Entrega:** **API**.

### 3.9 VANFinder — buscador/comparador de LCV (leasing/fleet)

> **75.000 LCVs · 80+ marcas · 200+ modelos · 20+ body styles · 50+ mercados.**

Herramienta online de **search / select / compare** de furgonetas; *"comprehensive LCV data"* (payload, load volume, dimensiones detalladas **no enumerados** en la página) `[PARCIAL]`.
Target: equipos de venta de leasing y fleet sin expertise específico en LCV.

### 3.10 JATO V5 — planificación de producto y volumen (OEM)

Solución de **product & sales volume planning**; usada por **product managers, brand managers y directores** para preguntas competitivas inmediatas; los equipos técnicos trabajan en el "deep work" de V5. `[PARCIAL — página no enumera campos]`

### 3.11 JATO Advisory — consultoría/informes a medida

**Deliverables:** informes bespoke sobre `alternative fuels` · `vehicle technology` · `connectivity` · `mobility ownership trends` · **competitor specifications reports** · **finance offer insights** · **OEM discount trend monitoring**.
**Proceso (5 pasos):** `Discovery → Proposal → Analysis → Delivery → Review`.

### 3.12 Integrated Solutions / JaaS (developer portal)

**APIs:** **JATO Index** (search/discovery del catálogo) · **VINView / VINView Pro** (VRM/VIN → Instance ID + specs + estimated pricing) · **Specifications API** · **WLTP Link**.
**Endpoints de Specifications API:**
- **Vehicle Content** — *"OEM-defined standard equipment and options, packs, colours (with official codes & pricing)"*.
- **Options Build** — *"Build Rules to understand interdependencies between options and standard specifications"*.
- **Compare** — comparación side-by-side resaltando diferencias de features.
- **Incentives** — insight de ofertas de incentivos.
**Conceptos:** **`Instance ID`** (*"unique identifier for every vehicle instance globally"*) · **Taxonomy** (default ID → **~250 datapoints**; sin taxonomy → **50 datapoints**; **custom** a petición).
**Auth/entrega:** **OAuth 2.0 JWT** (tokens 60 min) · subscription keys (primary/secondary) · **RESTful**, real-time auto-updating, cloud-hosted · **Smart Descriptions** (contenido de listing auto-generado por IA).

### 3.13 (Partner) autobiz — valoración de usado + residual (cierra el gap)

Alianza estratégica (2025) en **22 países europeos**: **autobiz** aporta **valoración de usado**, **modelos de valoración** y **residual value forecasting** (20+ años de datos de mercado de usado EU);
**JATO** aporta specs estructuradas + taxonomía + **VIN identification**. Marco combinado **new-car launch → used-car forecast** (full lifecycle). Aplicación real: **Europcar Mobility Group**.

---

## 4. Metodología / fuentes de datos

**Estandarización (6 pasos, doctrina propia):** (jato.com — *"Bringing order to data chaos"*)
1. **Research community** mundial investiga el mercado en continuo, captura eventos y particularidades OEM.
2. **SMEs de marca** detectan y *"dissect"* tecnologías/features nuevas, más allá del nombre de marketing.
3. **Traducción a JATO items/attributes** *"agnostic of OEM languages"* (vocabulario OEM-agnóstico).
4. **Data Definitions Tool** — repositorio propietario (diccionario + enciclopedia) que define cómo interpretar y codificar cada item estandarizado.
5. **Coding consistente** en las bases **down to version level** de cada modelo.
6. **Enriquecimiento anual** del esquema con nuevos items/attributes según emergen tecnologías.

- **Fuentes:** datos de fabricante + eventos OEM; para **Volumes**, **registros oficiales de matriculación** + forecast corto **S&P Global Mobility**; para **Incentives**, programas públicos + **dato dealer-level** propietario (EU5); para **Monthly Payments**, ofertas financieras captive/non-captive retail/business; para **Sales Link**, **transacciones reales anonimizadas** de miles de dealers.
- **Frecuencias:** Specs **diaria** · Price Tracker **semanal** · Monthly Payments **semanal** · Incentives **mensual** · Volumes **mensual + Nowcast** (current+next month).
- **Posicionamiento:** **impartial / independent**; *"trusted partner, 40 years"*.
- **Infra (Microsoft case study):** Azure Cosmos DB (transacciones), Azure SQL (consultas), Azure AI Search (indexado), Data Factory (pipelines), **Azure OpenAI** (generador de contenido de Sales Link), App Service + Functions (hosting), Dynamics CRM (permisos/cliente).

(Fuentes: standardisation article; Volumes/S&P PR; Incentives/Monthly Payments pages; Microsoft Customer Story.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Apps web / plataformas** | **Carspecs** (`carspecs5.jato.com`) / **Vehicle Viewer** (specs+pricing+packs, baskets) · **JATO Net** (macro spec+volume) · **ModelMix Navigator** (Volumes) · **Incentives** (7 dashboards) · **Monthly Payments** (JATO Account portal) · **Price Tracker** (web multidispositivo) · **VANFinder** (online) · **Sales Link** (portal de dealer) |
| **APIs (JaaS, RESTful)** | developer.jato.com · **JATO Index · VINView/VINView Pro · Specifications API** (Vehicle Content / Options Build / Compare / Incentives) **· WLTP Link** · OAuth2 JWT · real-time auto-update · **Smart Descriptions** (IA) |
| **Datafeed** | Integración masiva de specs/precios/opciones a website/app/portal (single point of delivery) |
| **Informes / prensa** | Reports & whitepapers · newsletters · **rankings mensuales globales de matriculaciones** (prensa) |
| **Advisory** | Informes bespoke (Discovery→Proposal→Analysis→Delivery→Review) |
| **Partner** | Valoración/residual de usado vía **autobiz** (22 países EU) |

---

## 6. Precio (opaco — enterprise B2B)

| Producto | Precio | Fuente |
|---|---|---|
| Todo el catálogo (Specs, Volumes, Incentives, Monthly Payments, Price Tracker, VINView, WLTP Link, APIs) | **No público** — licencia/suscripción **enterprise B2B** negociada ("Get in touch" / "Request a demo") | jato.com (todas las páginas con CTA) `[NO-VERIFICADO importe]` |
| Sales Link | Probable **SaaS por dealer** (importe no público) | cardealermagazine; Microsoft story `[NO-VERIFICADO importe]` |
| Señal financiera | **Turnover £83 M (2023)**, PAT £11,6 M, EBITDA £14 M → negocio recurrente y rentable | uk.globaldatabase.com (accounts 2023) |

---

## 7. Placement (patrón web — clave para cardeep)

> JATO es **B2B puro** (no ficha de coche de consumo), pero su patrón de **ficha técnica/configurador + decode VIN + dashboards de mercado**
> es justo lo que cardeep imita en su subdominio `spec-catalog`. Mapa de colocación por superficie:

**A. Ficha técnica / build sheet (Carspecs / Vehicle Viewer / VINView).** Vertical por bloques:
**Cabecera de identificación** (make/model/trim/derivative/MY/fuel/transmission/body + JATO UID) → **equipamiento estándar agrupado** (safety/ADAS · infotainment · comfort) →
**opciones y packs con código OEM y precio** → **colores** (ext/int con código) → **técnica/dimensiones/powertrain/consumo-CO2** → **precio de lista + precio de opciones**.
Las **build rules** gobiernan las dependencias del configurador.

**B. Caja de decode VIN/VRM (VINView Pro).** Input (matrícula o VIN) → **build exacto fitted** + **price when new**. Es la puerta de las fichas de **usado** y del flujo de **stock acquisition** (distinguir spec real entre coches "idénticos").

**C. Comparador / baskets (Compare endpoint / Price Tracker baskets).** Side-by-side de sets competitivos resaltando **diferencias de features**; los *"baskets"* son sets competitivos guardados — patrón directo para el comparador de cardeep.

**D. Dashboard de mercado (ModelMix Navigator / JATO Net).** Panel de **market share · segments · brand/model volumes · fuel mix · Nowcast**; drill por región/segmento. Es el "panel/overview de mercado".

**E. Dashboard de precios (Price Tracker).** Seguimiento de **movimientos de RRP** + **valor por cambios de equipamiento** + posicionamiento; **alertas semanales**.

**F. Dashboards de incentivos (7 pestañas).** `summary · trend · price · comparison · discount · volume · detailed`: composición del descuento, **net transaction price**, distribución de incentivos, correlación con share.

**G. Vista de cuotas mensuales (Monthly Payments).** Comparación de ofertas: **deposit · APR · monthly · term · contribution**, retail vs business, captive vs non-captive. (La "affordability view": el dato que el consumidor realmente compara.)

**H. Informe de benchmark de dealer (Sales Link).** Tu-site **vs mercado anonimizado**: price · discount · feature popularity · **days-to-sell** · option uptake · colour popularity, + **narrativa auto-generada por IA**.

**I. Panel WLTP/emisiones (WLTP Link).** CO2 / consumo / EEC / range **por configuración**; etiquetas y quotes compliant; **TCO + tax**.

**J. Enriquecimiento de listing retail (Retail Listings).** Listings estandarizados y buscables, **filtros a nivel spec**, **Smart Descriptions** (texto auto), **price-when-new** en usado.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **El catálogo de specs de coche NUEVO más profundo y comparable del mundo:** **1.000 datapoints/coche**, taxonomía **OEM-agnóstica down to version level**, 200+ marcas / 1.800+ modelos / 50+ mercados, **updates diarios**. Es *la* referencia de specs/feature data nuevo.
2. **Datos grado-configurador:** **build rules + interdependencias de opciones** + **packs y colores con código OEM oficial y precio** — pocos lo tienen estructurado así.
3. **Metodología de estandarización** (Data Definitions Tool; SMEs que "diseccionan" features a items OEM-agnósticos) → **comparabilidad cross-brand** real.
4. **Incentives con dato dealer-level EXCLUSIVO (EU5)** + 10 años + volume-weighted → visibilidad de **descuento de transacción** que casi nadie publica.
5. **Monthly Payments:** **70+ datapoints financieros**, captive/non-captive, retail/business → benchmarking por **affordability** (cómo compra el cliente), no por precio de lista.
6. **Volumes con Nowcasting** (integración del forecast corto de **S&P Global Mobility**) → matriculaciones hasta el mes **actual y siguiente**.
7. **Sales Link:** benchmarking de dealer sobre **transacciones reales anonimizadas de miles de competidores** + **generación de contenido por IA**.
8. **WLTP Link:** punto único multi-OEM con **cálculo WLTP por configuración**.
9. **Independencia/imparcialidad** + base de clientes = **todos los fabricantes de volumen del mundo** + **40 años**.
10. **Ecosistema JaaS** (Instance ID, taxonomy custom) = **single point of delivery** de todo el dato de vehículo a web/app/portal.

---

## 9. Gaps (lo que NO ofrece)

1. **Sin valoración de usado / valor residual nativo** — lo aporta el **partner autobiz** (RV forecasting, valuation models). El dato propio de JATO es **specs + precio de lista + price-when-new**, no un libro retail/trade ni curva de depreciación. ← **gap clave para cardeep**.
2. **Sin historial de vehículo** (siniestros, propietarios, km, title) — no es un CARFAX/Experian/historial.
3. **Usado = identificación, no pricing:** VINView decodifica el build, pero **no entrega valoración trade/retail de usado** de forma nativa.
4. **Geografía sesgada a Europa en las capas de valor:** Incentives 13 EU, Monthly Payments EU7, VINView 8 EU, Sales Link 5 países; las **specs** sí son 50+ global, pero la **inteligencia de mercado/finanzas profunda es EU-céntrica**.
5. **Sin portal de consumo / valoración gratuita pública** — B2B puro; specs no públicas por modelo al consumidor.
6. **Sin producto de seguro / total-loss / claims valuation** (vs S&P Mobility/CCC/Solera).
7. **Camión pesado y moto no enfatizados** (turismo + LCV + cuadriciclo). `[VERIFICADO por ausencia]`
8. **Precio enterprise opaco** (todo "contact sales").
9. **Sin ingestión nativa de condición/odómetro/telemática** — el decode es de **spec**, no de estado real del coche.
10. **"Market days supply" / índice oferta-demanda por anuncio** (estilo vAuto/CarGurus) **no** es producto nombrado; Sales Link da **days-to-sell a nivel dealer**, no un índice de market-days-supply de mercado. `[NO-VERIFICADO como producto nombrado]`
11. **Ajuste de valor por km/daño:** no nativo (depende de autobiz/partners).

---

## 10. Fuentes

**Sitio oficial JATO (jato.com) — vía WebFetch (render limpio en páginas de marketing):**
- Home (tagline, capabilities, productos): https://www.jato.com/
- About (1984, HQ Uxbridge, 800+ experts, 50+ países, 250M+ datapoints, 75k events/mes, 40 años): https://www.jato.com/about-us
- Specifications capability (1.000 datapoints, 375M, 200+ marcas, categorías): https://www.jato.com/our-capabilities/specifications
- Specifications solution (categorías de campo, current+historical, fitted specs): https://www.jato.com/solutions/jato-specifications/
- Analysis capability (Benchmarking, Market Analysis, Pricing Optimisation, Transaction Analysis): https://www.jato.com/our-capabilities/analysis
- JATO Advisory (deliverables, proceso 5 pasos): https://www.jato.com/our-capabilities/jato-advisory
- Integrated solutions / JaaS (VINView, WLTP Link, Specs & Options, 1.800+ modelos): https://www.jato.com/our-capabilities/integrated-solutions
- VINView / VINView Pro (campos decode, 8 mercados EU, JATO Index desde 2010): https://www.jato.com/our-solutions/vinview
- Volumes with Nowcasting (40+ mercados, ModelMix Navigator, S&P forecast, quadricycle): https://www.jato.com/our-solutions/volumes
- Price Tracker (RRP, value-by-equipment, baskets, JATO UID, weekly): https://www.jato.com/our-solutions/price-tracker
- Monthly Payments (EU7, 50 marcas, 80+ modelos, 70+ datapoints: deposit/APR/monthly/term/contribution, captive/non-captive): https://www.jato.com/our-solutions/monthly-payments
- Incentives (13 EU, EU5 dealer-level, 10+ años, mensual, 7 dashboards, tipos de incentivo): https://www.jato.com/incentives
- WLTP Link (CO2/consumo/EEC, 200+ marcas/1.800+ modelos, cálculo por config, TCO/tax): https://www.jato.com/our-solutions/wltp-link
- Leasing & fleet (VINView valuations/remarketing, residual risk, EV transition, range/charging): https://www.jato.com/our-industries/leasing
- VANFinder (75.000 LCVs, 80+ marcas, 200+ modelos, 20+ body styles): https://www.jato.com/our-industries/leasing/vanfinder
- Automakers (productos OEM: Specs/Volumes/Price Tracker/Monthly Payments/Vehicle Viewer/Advisory): https://www.jato.com/our-industries/automakers
- Retail / dealers (Sales Link, VINView, use cases): https://www.jato.com/our-industries/retail/dealers
- Use case Retail Listings (VINView Pro, JATO Index, Specs API, Smart Descriptions; campos): https://www.jato.com/use-case/retail-listings
- Use case Stock Acquisition (VINView Pro VRM/VIN, original list price, optional extras): https://www.jato.com/use-case/stock-acquisition
- Standardisation methodology (6 pasos, Data Definitions Tool, items OEM-agnósticos): https://www.jato.com/resources/news-and-insights/bringing-order-to-data-chaos-jato-approach-standardisation
- PR autobiz (valoración/residual de usado, VIN, 22 países EU, Europcar): https://www.jato.com/resources/media-and-press-releases/jato-dynamics-and-autobiz-forge-strategic-european-partnership
- PR S&P Global Mobility (Nowcast, forecast corto integrado en Volumes): https://www.jato.com/resources/media-and-press-releases/jato-dynamics-sp-global-mobility-partnership-optimise-automotive-intelligence

**Developer portal (JaaS) — vía WebFetch (landings JS; endpoints desde getting-started):**
- Getting Started (endpoints Vehicle Content / Options Build / Compare / Incentives; Instance ID; OAuth2 JWT 60min; taxonomy 250/50 datapoints): https://developer.jato.com/getting-started
- APIs list / Products: https://developer.jato.com/apis · https://developer.jato.com/products
- Carspecs Customer API demo → Swagger (no parseado; redirige): https://webapi-customer-demo.jato.com/ → https://webapi-documentation-demo.jato.com/
- Carspecs app: https://carspecs5.jato.com/

**Terceros / verificación cruzada:**
- Microsoft Customer Story (Sales Link 5 países, 55+ marcas, ~32h/mes, stack Azure + OpenAI): https://www.microsoft.com/en/customers/story/19641-jato-dynamics-azure
- Companies House (No. 02262299; PSC: JATO Holdings Ltd ultimate parent, JATO Nominees, J.B. Shafran): https://find-and-update.company-information.service.gov.uk/company/02262299/persons-with-significant-control
- GlobalDatabase (accounts 2023: £83M turnover, £14M EBITDA, £11,6M PAT, 770 empleados; incorporación 1988): https://uk.globaldatabase.com/company/jato-dynamics-limited
- Wikipedia (1984, fundador Jake Shafran, HQ Uxbridge): https://en.wikipedia.org/wiki/JATO_Dynamics
- Car Dealer Magazine (Sales Link: KPIs days-to-sell/option uptake/colour popularity): https://cardealermagazine.co.uk/introducing-sales-link-from-jato-revolutionising-automotive-sales-analytics/288346
- Automotive World (rankings mensuales de matriculaciones EU — output de prensa de Volumes): https://www.automotiveworld.com/news-releases/jato-dynamics-stellantis-year-on-year-volumes-drop-by-25-driving-european-new-car-registrations-down-by-3-in-september/
- EMobility+ (Monthly Payments / finance insights): https://emobilityplus.com/2024/10/24/jato-revolutionizes-automotive-finance-with-data-driven-insights-for-a-changing-market/

### Notas de verificación
- **Identidad, ownership (parent JATO Holdings Ltd, PSC=4), financieros 2023, HQ, fundador, company number:** Companies House + GlobalDatabase + Wikipedia. **[VERIFICADO]**
- **CEO Andy Rothery / Founder-Chairman Jake Shafran:** WebSearch agregada (Bloomberg/Crunchbase/JATO). **[VERIFICADO]**
- **Campos atómicos de Specs, VINView, Incentives, Monthly Payments, Volumes, Price Tracker, WLTP Link, Sales Link:** páginas de producto JATO directas + corroboración WebSearch/3os. **[VERIFICADO]**
- **Endpoints API (Vehicle Content/Options Build/Compare/Incentives), Instance ID, taxonomy 250/50, OAuth2:** developer.jato.com/getting-started. **[VERIFICADO]**
- **autobiz = valoración/residual de usado (gap de JATO):** PR oficial JATO. **[VERIFICADO]** — confirma que JATO **no** hace residual nativo.
- **Escala 250M vs 375M datapoints:** discrepancia live-vs-total reportada con ambas fuentes. **[VERIFICADO con matiz]**
- **Precios enterprise:** no divulgados (todo "contact sales"). **[NO-VERIFICADO importe]**
- **VANFinder campos (payload/load volume/dimensiones) y JATO V5:** la página no enumera al detalle. **[PARCIAL]**
- **Ausencia de historial de vehículo, residual nativo, total-loss, market-days-supply, camión/moto:** inferida por ausencia del catálogo. **[NO-VERIFICADO exhaustivo / por ausencia]**
- **Swagger del Carspecs API demo:** no parseado (Swagger UI JS; el navegador Playwright estaba contendido por agentes concurrentes — redirección a classic.com; no usado como fuente). Endpoints/campos reconstruidos vía developer portal + páginas de producto.
