# Autovista Group — Auditoría atómica de inteligencia competitiva

> **Slug:** `autovista-group` · **Web:** https://autovistagroup.com (301 → https://autovista.com) · **Plataforma SaaS:** https://www.autovistaintelligence.com · **Subdominio "valuation":** ver nota abajo.
> **Auditoría:** 2026-06-30 · **Fuentes:** ≥2 por hecho material cuando fue posible. Cada afirmación marcada [VERIFICADO] (leído en fuente) o [NO VERIFICADO] (tercero / inferido).
> **Nota subdominio:** `valuation.autovistagroup.com` NO resuelve por DNS (`ENOTFOUND`) [VERIFICADO]. La oferta de "valuation" vive como línea de producto bajo `autovista.com/product/*` (AutovistaVALUATION, AutovistaREFORECAST, Compare, RVI, RVM) y como módulos en `autovistaintelligence.com`. La auditoría cubre esa línea completa.

---

## 1. Identidad

| Atributo | Dato | Estado |
|---|---|---|
| Nombre | Autovista Group (marca operativa: "J.D. Power Autovista") | [VERIFICADO] |
| Propietario / grupo | **J.D. Power** (a su vez propiedad de **Thoma Bravo**, private equity) | [VERIFICADO] |
| Adquisición | Anunciada **12-sep-2023**; **completada 01-marzo-2024** | [VERIFICADO] (2 press releases JD Power) |
| Rol post-adquisición | Es **la plataforma de datos y analítica de automoción de J.D. Power para Europa y Australia** | [VERIFICADO] |
| HQ | **Londres, Reino Unido** | [VERIFICADO] (highperformr/Tracxn + registro GOV.UK company 05763626) |
| Herencia / fundación | **Principios de los años 1930** (Glass's Guide publica desde **1933**) | [VERIFICADO] (JD Power press + Wikipedia Glass's) |
| Empleados | **750** | [VERIFICADO] (press oficial JD Power) |
| Especialistas/analistas automoción | **~400** ("nearly 400 automotive professionals") | [VERIFICADO] (autovista.com why-choose-us / autovista-api) |
| Expertos red Car-to-Market | **750 expertos en 20 países** | [VERIFICADO] (product/car-to-market) |
| Ingresos | **~$178.8M** | [NO VERIFICADO] (Tracxn, tercero) |
| Liderazgo | Lindsey Roberts pasó de CEO de Autovista Group a President de J.D. Power Europe | [VERIFICADO] |
| Antiguo nombre | **EurotaxGlass's Group**, relanzado como Autovista Group | [VERIFICADO] |

### Marcas (6) y país/rol
[VERIFICADO] vía press release JD Power + homepage autovista.com:

| Marca | País / rol |
|---|---|
| **Autovista** | Marca pan-europea de analítica y datos (paraguas) |
| **Glass's** | Reino Unido (el "Glass's Guide", la "biblia" del trade UK desde 1933) |
| **Schwacke** | Alemania (SchwackeNet, sistema de gestión de usado líder) |
| **Eurotax** | Europa continental: Austria, España, Suiza, Polonia, Hungría, Rumanía, Portugal, Chequia, Eslovaquia, Eslovenia |
| **Rødboka** | Noruega |
| **EV Volumes** | Datos globales de vehículo eléctrico (120-130+ mercados) |

### Categorías de oferta
Tres pilares de datos a lo largo del ciclo de vida del vehículo [VERIFICADO]:
1. **Vehicle Identification & Specification** (identificación + ficha técnica)
2. **Pricing & Valuations** (precios, valor residual, forecast)
3. **Service, Maintenance & Repair (SMR)** (mantenimiento, reparación, daños, TCO)

### Clientes objetivo (sectores con página propia)
[VERIFICADO]: Manufacturers & Importers · Dealers · Fleet & Finance/Leasing · Insurance · Bodyshops & Assessors · Aftermarket · Remarketing · Professional Services · Government · Telematics.

---

## 2. Cobertura

- **Geografía:** pan-europea + Australia. Países operativos listados [VERIFICADO]: Austria, Bélgica, Croacia, Chequia, Finlandia, Francia, Alemania, Hungría, Irlanda, Italia, Luxemburgo, Países Bajos, Noruega, Polonia, Portugal, Rumanía, Eslovaquia, Eslovenia, España, Suecia, Suiza, Reino Unido, **Australia**. (≈20+ países.)
- **Cobertura de parque:** "99% de turismos y LCV" / "97-99% del car parc europeo" / "90%+ del mercado relevante" / "98% de vehículos vía VRN" para SMR [VERIFICADO].
- **Nº de mercados varía por producto** [VERIFICADO] (dato atómico relevante):
  - AutovistaSPEC: 13-15 mercados, 40+ OEM
  - AutovistaVALUATION: **15 mercados** core; **17 países** en histórico
  - AutovistaREFORECAST: **12 mercados**
  - Residual Value Monitor (RVM): **17 mercados**, 38 marcas, hasta 150 model types/mercado
  - Residual Value Intelligence (RVI): **7 mercados**, 42 marcas, 14 segmentos, 7 fuel types
  - Compare (Eurotax): **15 mercados**, 100K nuevos + 200K usados
  - Car to Market: **20 países**
  - Car Cost Expert: **12 mercados**, 300+ escenarios TCO
  - EV Volumes: **120-130+ mercados globales**
- **Scope vehículo:** nuevo **y** usado; **turismos (cars), LCV (furgonetas), motocicletas/bikes**; ICE + híbrido + eléctrico. Desde forecast pre-producción hasta valor de usado antiguo.
- **Profundidad temporal:** datos técnicos y de precio hasta **20 años atrás**; histórico de precio en RVI desde **2017**; forecast hasta **120 meses (10 años)**.

---

## 3. Productos + campos atómicos

> Los nombres de campo se conservan en inglés (son nombres de dato). Marketing oculta diccionarios exhaustivos; los campos listados son los **nombrados explícitamente** en fuentes (no inventados).

### 3.1 AutovistaSPEC — *Vehicle Identification & Specification* (data feed)
Identifica y describe el vehículo. Aseguradoras: identifica **>5.000 componentes individuales**, 40+ OEM.
**Campos:** VIN · VRM/VRN · NatCode (search-tree) · automotive ID · make/brand · model · version/trim/specification · body type · engine · power / engine performance · dimensions · fuel type (ICE/hybrid/EV) · transmission/gearbox · drivetrain · build year/date · WLTP emissions (CO2) · fuel/energy consumption · EV range · EV battery capacity · EV charging time · list price (new, histórico 20 años) · factory-fitted optional extras · standard equipment · individual components (5.000+).
**Entrega:** data feed CSV tab-delimited; también API. **Cobertura:** 99% cars/LCV/motos, 13-15 mercados.

### 3.2 AutovistaVALUATION — *Residual Value / used-car valuation* (data feed + API)
**Campos:** trade value · retail value · residual value (absoluto) · **residual value % (RV%)** · residual value forecast (hasta **120 meses**) · average mileage (incluido) · mileage-adjusted value / **mileage band** · **16 age-distance (age-mileage) scenarios** · optional-equipment-adjusted value · histórico 4 años (17 países).
**Entrega:** "unified data feed" (un único feed armonizado multi-mercado); **API** devuelve valor por-VIN ajustado a km real (1.000 vehículos → 1.000 entradas a medida; feed → 1 valor). **Cobertura:** cars, LCV, bikes; 15 mercados (99%).

### 3.3 AutovistaREFORECAST — *Dynamic re-forecast / revaluación batch*
**Campos:** current residual value · future/contract-end value (hasta **5 años** / por fecha seleccionada) · múltiples valoraciones por vehículo en distintos puntos age & mileage · VIN-level inventory valuation · depreciation of optional features · risk identification.
**Entrega:** batch — envías lista de vehículos, recibes **CSV estandarizado**; herramienta real-time accesible desde cualquier dispositivo. **Cobertura:** 99% cars/LCV; 12 mercados.

### 3.4 Residual Value Monitor (RVM) — *aplicación / dashboard*
**Campos:** current trade & retail values · age-mileage combinations · historical trends (4 años) · **model performance rankings** · competitive benchmarking KPIs · value changes ligados a **facelifts / new launches** · **predecessor-successor tracking**.
**Entrega:** web app con **dashboards Tableau** personalizados; raw data mensual. **Cobertura:** 17 mercados, 38 marcas, ≤150 model types/mercado.

### 3.5 Residual Value Intelligence (RVI) — *aplicación / dashboard*
**Campos:** current & forecast values (trade & retail) · RV en moneda local (EUR/GBP) · **RV%** · **weekly price index** (controla "basket effects") · price history (desde 2017) · **16 age-distance scenarios** · **fuel-type benchmarking** (diferencia en puntos porcentuales) · comparación cross-market · KPI tracking (dashboard customizable).
**Filtros:** fuel type · scenario · segment · brand · body-type · trade-or-retail.
**Entrega:** web app, **Tableau**; dashboards por **Fuel / Brand / Segment / Country**, cada uno con vista **Overview** + **Detailed**; export a reports. **Cobertura:** 7 mercados, 42 marcas, 14 segmentos, 7 fuel types.

### 3.6 Compare (Eurotax) — *aplicación / dashboard*
**Campos:** actual & forecast residual values · cross-market comparison · optional equipment valuations · like-for-like national & international comparison · depreciation tracking.
**Entrega:** web tool/dashboard, descarga; updates mensuales. **Cobertura:** 15 mercados, 100K nuevos + 200K usados.

### 3.7 Car to Market (C2M) — *consultoría + aplicación pre-lanzamiento*
Optimiza el RV de un modelo **hasta 4 años antes del lanzamiento**. Analiza **16 key residual value drivers**.
**Campos/drivers:** concept strengths/weaknesses (perceived quality) · commercial strategy (equipment levels, volume planning, incentive structures) · everyday usability (range & charging) · cost vs performance (fuel/energy efficiency) · brand RV performance benchmark · go-to-market strategy · build quality · **RV forecast por variant / powertrain / trim level**.
**Fases:** Phase 0 (concept shaping) · Phase 1 (strategy definition) · Phase 2 (RV forecasting). **Cobertura:** 20 países, 750 expertos; 65% de nuevos lanzamientos; mayoría de lanzamientos BEV.

### 3.8 EV Volumes — *base de datos de inteligencia EV*
**Campos:** EV sales (by OEM & model) · registrations/volume · market share / penetration · market sizing · monthly sales tracker · **battery shipments (kWh)** · **battery cell type** · **cathode chemistry** · battery manufacturer · battery capacity (by model) · EV specs · EV pricing · charging infrastructure (growth) · connector type · future model launches · powertrain split (**BEV/PHEV/FCEV/HEV/MHEV**).
**Entrega:** data center (dashboards), API, reports **Excel / PDF / CSV**, tracker mensual. **Cobertura:** 120-130+ mercados.

### 3.9 Car Cost Expert (CCE / CCE-NG) — *aplicación TCO*
**Campos:** total cost of ownership (TCO) · depreciation · fuel cost · energy cost (EV) · taxation/road tax · maintenance (SMR) cost · tyre cost · insurance cost · monthly cost · cost per km · fixed cost vs variable cost.
**Entrega:** web app. **Cobertura:** 12 mercados, **300+ escenarios TCO**. (Claim: "1% mejora TCO ≈ €2M ahorro por 10.000 vehículos".)

### 3.10 AutovistaSMR — *Service, Maintenance & Repair data* (feed)
**Campos:** service schedules · maintenance intervals · labour times · labour rates · SMR rates · maintenance cost predictions · TCO components · OEM-sourced pricing ligado a matrícula.
**Cobertura:** cars + LCV; 40+ OEM; Europa / Norteamérica / Australia.

### 3.11 AutovistaREPAIR — *Repair / damage data* (feed)
**Campos:** labour times ("costed to the minute") · labour rates · paint times · **paint material cost (AZT-sourced)** · spare part numbers · part prices · repair cost estimate · replacement cost · **interactive graphical part data** (click en pieza → precio) · body/structure data · **TecDoc-compatible parts codes** · damage assessment data.
**Cobertura:** hasta 98% de vehículos vía VRN; 40+ OEM. **Entrega:** feed compatible con la suite Autovista.

### 3.12 Autovista API — *REST API*
**Campos/datos:** automotive ID · engine · dimensions · performance · WLTP emissions · fuel consumption · valuation/residual value benchmarks · depreciation · market value & trends · daily pricing · car tax & registration calculation · VIN/VRM check · **DVLA vehicle check** · **stolen car check** · queries dinámicas (mileage-adjusted).
**Entrega:** REST, **pay-per-use**, actualización diaria.

### 3.13 VIN API — *REST API*
**Campos:** perfil completo desde VIN → make · model · version · trim · body · engine · fuel · transmission · drivetrain · build date · **factory-installed equipment & options** · emissions · consumption · dimensions · engine performance.
**Entrega:** REST, basado en datos OEM, update mensual.

### 3.14 Data Feeds & APIs / Data Solutions — *capa de entrega*
REST APIs (pay-per-use) · bulk file processing · data feed integration · dynamic per-record queries · documentación API + soporte técnico.

### 3.15 Activos de marca nacional (web tools)
- **Glass's (UK):** Glass's Trade value · Glass's Retail value · Private value · Forecast values · live retail advertised prices · **Market Value Assessor** (combina current values + live retail + forecast sobre 65.000+ vehículos) · Glass Forecast portal. [VERIFICADO parcialmente — homepage glass.co.uk no expone nomenclatura completa]
  - ⚠ **Corrección antialucinación:** los tiers "CAP Clean / CAP Average / CAP Below Average" son de **CAP HPI (competidor)**, NO de Glass's; un blog de terceros los confundió. No atribuidos a Autovista.
- **Schwacke (DE):** Restwerte · Restwerttrends · Restwertentwicklungen · Restwert-Performance · Fahrzeugspezifikationsdaten · SchwackeNet (gestión de usado VIN-enhanced) · SchadenManager · Forecast · Reforecast. (Claim: ~85% de las leasing rates se basan en RV.)

### 3.16 Autovista24 — *portal editorial / reports*
Market reports · forecasts · news; reports del mercado "Big 5" de turismos nuevo y usado. Acceso también como módulo en Autovista Intelligence.

---

## 4. Metodología y fuentes de datos
[VERIFICADO] vía `autovista.com/our-accuracy` + `/why-choose-us` + páginas API:

- **Observaciones de mercado:** "millones de observaciones de mercado **cada día**" desde los principales marketplaces online de vehículos.
- **Resultados de subastas** (auction house results).
- **Datos OEM:** 40+ OEM, 5.000+ componentes.
- **Diálogo con stakeholders** de toda la cadena.
- **Independencia:** "sin lazos con stakeholders de la industria" → valoraciones imparciales. Diferenciador clave.
- **Híbrido ML + humano:** "advanced machine learning + expert human oversight"; **~400 especialistas**.
- **Sesiones editoriales mensuales** → fijan tasa media de depreciación y destacan segmentos/marcas/modelos notables.
- **Benchmark contra transacciones reales**; ajuste por insight regional/local.
- **Validación / cross-check** de inconsistencias; **métricas de accuracy refrescadas cada mes** y publicadas (transparencia).
- **Identificación:** VIN · VRM · NatCode (search-tree).
- ⚠ **% de accuracy concreto (MAPE):** NO publicado en páginas públicas [NO VERIFICADO — no localizado].

---

## 5. Entrega (delivery)
[VERIFICADO]:
- **Data feeds** (CSV / tab-delimited, armonizados; un feed multi-mercado).
- **REST APIs** (pay-per-use, dinámicas, mileage-adjusted; VIN API, Autovista API).
- **Aplicaciones web / SaaS** → plataforma **Autovista Intelligence** con **dashboards Tableau** (módulos: RVM, RVI, Car To Market, Autovista24 Reports; servicio de soporte "Ask Autovista").
- **Reports Excel / PDF / CSV** (EV Volumes).
- **Batch / bulk processing** (REFORECAST: lista→CSV).
- **Integración en sistemas / DMS** del cliente.
- **Portal editorial** (Autovista24) gratuito.
- Marcas nacionales con web propia: glass.co.uk, schwacke.de, compare.eurotax.com, carcostexpert.com, datacenter.ev-volumes.com.

---

## 6. Precio
- **No hay precios públicos.** Modelo enterprise: "Get Started" / contacto comercial. [VERIFICADO — ninguna página de pricing pública]
- **API explícitamente "pay-per-use"** (cloud, por consulta). [VERIFICADO]
- **Suscripciones** para las apps Intelligence (páginas `/subscribe/...`). [VERIFICADO]
- Importes concretos: **NO descubribles** [NO VERIFICADO].

---

## 7. Placement (dónde se ubica cada dato — patrón a copiar por cardeep)

| Dato | Dónde / pantalla |
|---|---|
| Identificación + ficha técnica | Entrada por **VIN / VRM / NatCode** → devuelve perfil completo del vehículo (make/model/trim/engine/equipment) — VIN API / AutovistaSPEC |
| Trade & retail value, RV%, forecast | Vista de valoración por vehículo; **fila por vehículo** en data feed; **API → valor por-VIN** ajustado a km |
| Dashboards de valor residual | Plataforma **Autovista Intelligence**, **dashboards Tableau** organizados por **Fuel / Brand / Segment / Country**, cada uno con vista **Overview** + **Detailed** |
| KPIs | **Dashboard de KPIs customizable** (RVI) / dashboard "at a glance" (RVM) |
| Rankings de modelo y benchmarking competitivo | Vistas de **model selection / ranking** en RVM |
| Weekly price index | Gráficos de tendencia en RVI |
| Tendencias históricas (4 años) | Trend charts en RVM / RVI |
| Comparación cross-market like-for-like | Tablas comparativas / market-overview en Compare |
| Desglose TCO | App **Car Cost Expert**: breakdown por componente (depreciation/fuel/tax/maintenance/tyres/insurance), cost/km, monthly cost |
| Reparación / despiece | **Diagrama gráfico interactivo de piezas** (click en pieza → precio) en AutovistaREPAIR; labour "costed to the minute" |
| Drivers de RV pre-lanzamiento | Reports por fases (Phase 0/1/2) en **Car to Market** |
| Métricas EV (batería, química, ventas) | Dashboards del **EV Volumes data center** + exports Excel/PDF/CSV + tracker mensual |
| Reports y forecasts de mercado | Portal **Autovista24** |
| Days-to-sell / time-to-sale, stock duration, pricing premium | KPIs de stock en páginas **Dealers / Remarketing** |
| Total loss value, repair-vs-replace | Workflow de **Insurance** (claims/underwriting/pricing) sobre AutovistaVALUATION + REPAIR |

---

## 8. Diferencial (lo que ofrece y otras no)
1. **Dataset pan-europeo armonizado/estandarizado** en 20+ países vía un único feed → comparación cross-border **like-for-like** real.
2. **Herencia y autoridad** (desde los 1930s): Glass's, Eurotax, Schwacke son las "biblias" nacionales del trade; valoraciones tratadas como **estándar de industria**.
3. **Independencia** (sin propiedad/lazos OEM) → imparcialidad.
4. **Forecast de RV pre-lanzamiento hasta 4 años antes** (Car to Market) — raro en el mercado.
5. **Inteligencia EV best-in-class** (EV Volumes: cell type, cathode chemistry, battery kWh, 130+ mercados).
6. **Cobertura de ciclo completo**: identification → spec → valuation → forecast → SMR/repair → TCO.
7. **Híbrido ML + ~400 expertos humanos**; forecast a **120 meses (10 años)**.
8. **40+ OEM data partnerships, 5.000+ componentes**.
9. Respaldo de **J.D. Power** (analítica predictiva global + datasets de customer experience).

---

## 9. Gaps (lo que NO ofrece — relevante para cardeep)
- **NO es marketplace ni listado de inventario** ni clasificados de consumidor: es datos B2B. Agrega "observaciones de mercado", **no publica un censo/directorio de puntos de venta ni el stock vivo por dealer** (justo el core de cardeep: huella digital punto-de-venta).
- **NO hay feed de inventario individual por concesionario** ni `cdp_code`/identidad de dealer.
- **Métricas de velocidad estilo J.D. Power US** ("market days supply", "price-to-market %") **no evidenciadas** en producto europeo; sí aparece **days-to-sell / time-to-sale** (KPI de stock), pero supply/price-to-market = **gap probable**.
- **Pricing opaco** (sin lista pública).
- **Norteamérica limitada** (foco Europa + Australia; SMR menciona NA pero las valoraciones son europeas).
- **NO hay informe de historial por-VIN de siniestros/km** tipo Carfax/autoDNA: tienen **coste de reparación** (SMR/REPAIR), no una base de **eventos/historial** del vehículo (accidentes, fraude de cuentakilómetros).
- **% de accuracy (MAPE) concreto no publicado**.
- **Camiones pesados / agrícola** no destacados (foco cars/LCV/bikes; Schwacke históricamente tiene truck data pero no se expone).

---

## 10. Fuentes (URLs)
1. https://autovista.com/index.php — homepage (productos, sectores, navegación) [VERIFICADO]
2. https://autovista.com/product/autovistavaluation/ [VERIFICADO]
3. https://autovista.com/product/autovistareforecast/ [VERIFICADO]
4. https://autovista.com/product/residual-value-monitor/ [VERIFICADO]
5. https://autovista.com/product/residual-value-intelligence/ [VERIFICADO]
6. https://www.autovistaintelligence.com/subscribe/residual-value-intelligence — dashboards/placement [VERIFICADO]
7. https://www.autovistaintelligence.com/ — módulos plataforma [VERIFICADO]
8. https://autovista.com/product/car-to-market/ [VERIFICADO]
9. https://autovista.com/product/compare/ [VERIFICADO]
10. https://autovista.com/product/data-solutions/ [VERIFICADO]
11. https://autovista.com/product/repair-data/ (AutovistaREPAIR) [VERIFICADO]
12. https://autovista.com/service-maintenance-repair-data/ (AutovistaSMR) [VERIFICADO]
13. https://autovista.com/vehicle-identification-specification-data/ [VERIFICADO]
14. https://autovista.com/vehicle-identification-specification/how-can-i-accurately-identify-the-correct-vehicle/ [VERIFICADO]
15. https://autovista.com/pricing-valuations-data/ [VERIFICADO]
16. https://autovista.com/pricing-valuations/how-can-i-track-residual-values/ [VERIFICADO]
17. https://autovista.com/product/ev-volumes/ [VERIFICADO]
18. https://www.carcostexpert.com/ [VERIFICADO]
19. https://autovista.com/product/autovista-api/ [VERIFICADO]
20. https://autovista.com/product/vin-api/ [VERIFICADO]
21. https://autovista.com/our-accuracy/ — metodología [VERIFICADO]
22. https://autovista.com/why-choose-us/ — escala/identidad [VERIFICADO]
23. https://autovista.com/sector/dealers/ [VERIFICADO]
24. https://autovista.com/sector/fleet-leasing/ [VERIFICADO]
25. https://autovista.com/sector/insurance/ [VERIFICADO]
26. https://autovista.com/sector/remarketing/ [VERIFICADO]
27. https://autovista.com/products/ — lista de productos/Glass's [VERIFICADO]
28. https://glass.co.uk/ — Glass's UK [VERIFICADO]
29. https://schwacke.de/residual-values/ — Schwacke DE [VERIFICADO]
30. https://autovista24.autovistagroup.com/news/jd-power-completes-acquisition-of-autovista-group/ — adquisición, marcas, países [VERIFICADO]
31. https://autovista24.autovistagroup.com/news/jd-power-expands-automotive-data-and-analytics-portfolio-in-europe-and-australia-with-acquisition-of-autovista-group/ [VERIFICADO]
32. https://www.businesswire.com/news/home/20230912714491/en/ — press release adquisición [VERIFICADO]
33. https://find-and-update.company-information.service.gov.uk/company/05763626 — registro UK (HQ) [NO VERIFICADO directamente, vía búsqueda]
34. https://tracxn.com/d/companies/autovistagroup/ — ingresos/empleados (tercero) [NO VERIFICADO]
35. https://en.wikipedia.org/wiki/Glass's_Guide — fundación 1933 [VERIFICADO]

---
*Auditoría producida por reconocimiento web exhaustivo (WebSearch + WebFetch). Nota de entorno: no había servidor MCP de Exa registrado; se usó WebSearch/WebFetch de forma intensiva. Diccionarios de campo exhaustivos están tras muro comercial ("Get Started"); los campos listados son los nombrados explícitamente en fuentes públicas — no se inventó ninguno.*
