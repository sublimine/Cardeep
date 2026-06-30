# Glass's — Auditoría atómica (intel-audit · cardeep)

> Slug: `glass-s` · Subdominio: `valuation` · Región primaria: Reino Unido (UK) · Grupo: Autovista Group (J.D. Power)
> Auditoría: 2026-06-30 · Doctrina VAM aplicada: cada campo lleva fuente; lo no confirmado va marcado `[NO-VERIFICADO]`.
> Web: https://glass.co.uk/ — todas las páginas de producto cuelgan de `glass.co.uk/product/<slug>/`.

---

## 1. Identidad

| Atributo | Valor | Fuente |
|---|---|---|
| Nombre comercial | Glass's (histórico: **Glass's Guide**, apodado "the bible" del comercio británico de VO) | [VERIFICADO] glass.co.uk, Wikipedia |
| Fundación | **Julio 1933**, por **William Glass** (ingeniero escocés, n. 1881) | [VERIFICADO] Wikipedia |
| Producto original | Guía impresa de valores de coches usados; "leading British motor trades guide to used car prices" | [VERIFICADO] Wikipedia |
| Expansión histórica | VI/comerciales, motos y caravanas en los años 50-60; luego formatos electrónico y online | [VERIFICADO] Wikipedia |
| Grupo / owner actual | **Autovista Group**, propiedad de **J.D. Power** | [VERIFICADO] glass.co.uk, JD Power PR, AM-Online |
| HQ | Reino Unido (oficinas Autovista Group en Londres desde 2017) | [VERIFICADO] glass.co.uk, Wikipedia |
| Marcas hermanas en el grupo | **Autovista, Eurotax, Glass's, Schwacke, Rødboka** | [VERIFICADO] búsqueda JD Power/Autovista |

### Historia de propiedad (cadena completa, verificada)
- **1933-1998:** Glass's Information Systems Ltd (independiente).
- **1998:** adquirida por **Hicks, Muse, Tate & Furst**.
- **2000:** fusión con **Eurotax AG** → **EurotaxGlass's AG** (Freienbach, Suiza).
- **2006:** comprada por **Candover Investments** por **€480 millones**.
- **2015:** pasa a **Hayfin Capital Management**.
- **2017:** rebranding del holding a **Autovista Group** + nueva sede en Londres.
- **2023-09-12:** J.D. Power anuncia acuerdo de adquisición de Autovista Group.
- **2024-03-01:** J.D. Power **completa** la adquisición. Glass's queda dentro del portfolio J.D. Power.

Fuentes: Wikipedia "Glass's Guide"; AM-Online (2023-09-12); JD Power press releases (announcement + close); autovista24.

---

## 2. Categorías y cliente objetivo

**Categoría madre:** valoración de vehículos + datos de especificación + datos de reparación/mantenimiento, "across the entire lifecycle of a vehicle". Se autodefinen "automotive pricing experts".

**Clientes objetivo (sectores con página propia `glass.co.uk/sector/<x>/`):**
- Manufacturers & Importers (fabricantes/importadores)
- Dealers (concesionarios)
- Fleet & Finance / Leasing-Contract Hire (flota, financieras, leasing)
- Insurance (aseguradoras) — uso fuerte en **total loss / siniestro**
- Bodyshops & Assessors (talleres de chapa, peritos)
- Remarketing
- Professional Services
- Government (administración)
- Telematics (proveedores telemáticos)

Fuente: [VERIFICADO] glass.co.uk homepage (navegación "Who we help").

---

## 3. Cobertura

| Dimensión | Cobertura | Fuente |
|---|---|---|
| Mercado primario | Reino Unido (marca Glass's) | [VERIFICADO] |
| Cobertura pan-europea (datos del grupo) | Hasta **15-17 mercados europeos** según producto (Compare 15; RVM 17; RVI 7) | [VERIFICADO] páginas de producto |
| Identificación del parque | **>97% / 99% del parque europeo** identificable solo con matrícula (cifra varía por página: 97% en Data Solutions, 99% en AutovistaSPEC/Insurance) | [VERIFICADO] data-solutions, autovistaspec, sector/insurance |
| Tipos de vehículo | **Turismos, LCV (furgonetas), motos** de serie; incluye **todos los EV e híbridos** | [VERIFICADO] MVA, glasss, data-solutions |
| Scope temporal valoración | **20 años rolling** turismos/motos; **15 años** LCV | [VERIFICADO] welcome-to-market-value-assessor |
| Histórico de precios | Hasta **20 años** de pricing histórico (feeds); **24 meses** de valoración en MVA; **4 años** de tendencia en RVI/RVM | [VERIFICADO] data-solutions, MVA, RVI/RVM |
| Nº de vehículos cubiertos | **>65.000 vehículos** (Market Value Assessor) | [VERIFICADO] MVA + VendorMotive |
| EV global | **>130 mercados**, **600+ modelos EV** (EV Volumes) | [VERIFICADO] ev-volumes |

---

## 4. Productos + campos ATÓMICOS

Glass's vende dos cosas a la vez: (a) **aplicaciones web** (Glass's platform, MVA, RVI, RVM, Compare, Car Cost Expert, Repair Estimate) y (b) **feeds/APIs de datos** marca **Autovista*** (SPEC, VALUATION, FORECAST, REFORECAST, REPAIR, SMR, WLTP, EV Volumes). Además consultoría (Car to Market).

### 4.1 Glass's (plataforma integrada) — `/product/glasss/`
Portal único, responsive, multi-dispositivo (Edge/Chrome/Firefox; no IE). "One competitive set price", look-ups ilimitados.

**Campos / métricas atómicas:**
- `Live retail pricing` (precio retail de mercado en vivo)
- `Trade pricing` (precio trade/mayorista)
- `Estimated depreciation over time` (curva de depreciación proyectada)
- `Forecast values` (valores forecast)
- `Repair cost data` (datos de coste de reparación, de **>40 fabricantes** por contrato)
- `Damage repair estimates` (estimaciones de daño leve y de colisión)
- `Valuation range` hasta **20 años**
- `Vehicle desirability` (deseabilidad por modelo y trim)
- Ajuste por **factory-fitted optional extras**
- Look-up por **VRN** (matrícula), look-ups ilimitados
- `Provenance checks` vía integración **Experian** (suscripción aparte)

**Pantallas/secciones (placement):**
- **Vehicle lookup** (entrada VRN → identifica y valora "in seconds")
- **Valuation screen** (trade + live retail + forecast + depreciación + ajuste opciones + desirability)
- **Market performance dashboard** con 3 KPIs: **Fastest Sellers**, **Highest Volumers**, **Most Desirable**
- **Stock management** interface
- **Fastest selling cars dashboard** (gráfico interactivo, filtro por región/edad, datos retail últimos 24 meses)

### 4.2 Market Value Assessor (MVA) — `/product/market-value-assessor/`
Herramienta núcleo de **valoración + liquidación de siniestros** (insurance/automoción). Cobertura **>65.000 vehículos** (coches, vans, motos). Valores actualizados **mensualmente**.

**Base de datos / observaciones:** **1,8 M observaciones de trade** + **8,6 M observaciones retail** + **>250.000 anuncios de concesionario verificados**.

**Campos / métricas atómicas:**
- `Trade valuations` (históricas y actuales)
- `Retail pricing` (live)
- Hasta **24 meses** de datos históricos de valoración
- `Mileage adjustments` (ajuste por kilometraje)
- `Vehicle specifications/identification`
- `Pre-accident damage assessments` (valor pre-accidente)
- `Repair cost calculations`
- `Valuation ratio settings` (ratio coste reparación / valor → decisión total loss)
- **Total Loss indicator** (full repair cost + valuation ratio)

**Módulo Radar (MVA Radar):**
- `Settlement figures` (cifras de liquidación)
- `Spot prices` (precios spot actuales)
- `Ad Search` → `average advert prices` (precios medios de anuncio)
- (Histórico: "GlassNet Radar" mostraba `live retail prices` + `advert durations`)

**Identificación:** VRM primario; árbol Make&Model si no hay VRM. **VIN no soportado** en MVA.

**Equipamiento:** equipo estándar incluido en la valoración; opciones adicionales visibles pero **no** alteran el valor en MVA.

**Placement / pantallas:**
- Look-up por matrícula → identificar y valorar
- **Status dashboard** (valoraciones guardadas; autosalva al identificar)
- **Total Loss** (repair cost + valuation ratio)
- **Gestión de caso**: collate de imágenes, notas y adjuntos del vehículo
- Interfaz **permission-based** (workflow de claims)
- **PDF reports** (estándar + custom vía "my account > PDF reports")
- Módulo **Repair Estimate** como suscripción opcional

**Discontinuado en MVA:** import DMS, revaluación masiva (bulk).

**Precio:** prueba gratis; sin precio público.

### 4.3 Residual Value Intelligence (RVI) — `/product/residual-value-intelligence/`
Software de **visualización** para trackear y optimizar valores residuales pan-europeos.

**Cobertura:** **42 marcas**, **14 segmentos**, **7 mercados** europeos principales, histórico **hasta 4 años**.

**Campos / métricas atómicas:**
- `Price Index` semanal (índice de precios, actualización **semanal**)
- **16 Age-Mileage Scenarios** (16 escenarios edad-km)
- `Trade & Retail values` (actuales)
- `Cross-Country Comparison` con **weighted averages** (medias ponderadas)
- Segmentación por `fuel types`, `segments`, `brands`, `market subsets`
- Análisis de tendencia a 4 años (controlando "basket effects")
- KPIs personalizables

**Placement / pantallas:**
- **KPI Dashboard** personalizable
- Gráfico de **Price Index** (tendencia semanal)
- Comparador **cross-country** (medias ponderadas)
- Export: **gráficos y datasets descargables** para presentaciones

**Usuarios:** Remarketing Managers, Risk Managers, OEM Remarketing, Fleet/Finance. Prueba gratis.

### 4.4 Residual Value Monitor (RVM) — `/product/residual-value-monitor/`
Monitorización/benchmark de rendimiento de stock nacional y europeo.

**Cobertura:** **38 marcas**, hasta **150 modelos/mercado**, **17 mercados europeos**, actualización **mensual** (opción raw data).

**Campos / métricas atómicas:**
- `Trade and retail values` (actuales y up-to-date)
- Histórico **hasta 4 años** en 17 mercados
- `Age-mileage combinations`
- `Performance rankings` (ranking de modelos por rendimiento RV)
- `Forecast values` (proyección de RV futuros)
- `Competitive benchmarking` (vs marcas rivales)
- `Facelift/launch uplift` (uplift por facelift o lanzamiento)
- `Predecessor/successor tracking` (transición de modelos, automático)
- Análisis tendencia **4 años**

**Placement / pantallas:**
- **KPI dashboards** ("single dashboard, at-a-glance"), personalizables (cloud)
- Tablas de **performance ranking**
- Comparativas multi-mercado (17)
- Gráficos de tendencia 4 años

### 4.5 Compare (Eurotax) — `/product/compare/`
Predicción/benchmark de RV pan-europeo. **15 mercados**, **100K vehículos nuevos / 200K usados**, actualización **mensual**.

**Campos / métricas atómicas:**
- `Residual value forecasts`
- `Current pricing benchmarks`
- `Depreciation/appreciation trajectories`
- `Retained value comparisons` (valor retenido like-for-like)
- `Optional specification pricing impacts` (impacto de opciones en precio)
- `Cross-border pricing datasets`
- Monitor de influenciadores locales (inflación, oferta, regulación)

**Placement (3 modos):** **Optimize** (forecast apreciación/depreciación sobre el contrato) · **Benchmark** (like-for-like + descarga) · **Analyse** (oportunidades de remarketing cross-border).

### 4.6 Forecast (Glass Forecast / AutovistaFORECAST) — `/product/forecast/`
Forecasting de valor residual al inicio de contrato.

**Campos / métricas atómicas + horizontes:**
- `Residual values at start of contract`
- Horizonte forecast: **hasta 120 meses** (10 años) — feed API
- **16 age-mileage combinations** (turismos y LCV)
- Depreciación de **genuine optional extras** (con parámetros de mercado)
- Coches nuevos: hasta **6 años / 250.000 mi**
- Coches usados: hasta **6 años**, edad máx **10 años / 250.000 mi**
- LCV nuevos: hasta **6 años / 350.000 mi**
- LCV usados: hasta **6 años**, edad máx **10 años / 350.000 mi**
- Benchmark independiente vs inflación, escasez de oferta, regulación
- Cobertura de **vehículos nicho**; capacidad de **stress-testing**

**Entrega:** Forecast API · Bulk Re-forecast Data Feed · plataforma online.
**Usuarios:** risk managers fleet/leasing, financieras (PCP/PCH), rent-a-car, underwriting.

### 4.7 Car to Market — `/product/car-to-market/` (CONSULTORÍA)
Consultoría de RV **pre-lanzamiento**, hasta **4 años antes** del lanzamiento. **750 expertos en 20 países**.

**Entregable — informe con 16 "key residual-value drivers", incluyendo:**
- `Conceptual strengths/challenges`
- `Commercialisation strategy`
- `Suitability for everyday use`
- `Cost vs. performance metrics`
- `Brand residual value performance`

**Fases:** 1-3 fases opcionales (de concepto a determinación final del RV). What-if: impacto de selección de equipamiento en retención de RV. "Supports the majority of all new BEV launches in Europe". Entrega: consultoría + informe escrito.

### 4.8 Car Cost Expert — `/product/car-cost-expert/` (TCO)
Cálculo y simulación de **Total Cost of Ownership**.

**Campos / métricas atómicas:**
- `Total Cost of Ownership` (TCO)
- **300 escenarios** mileage/age · **12 mercados** · **600+ model ranges**
- `Holding costs` (costes de tenencia, flota)
- Factoring de equipamiento y mantenimiento
- Integración de servicing programmes

**Entrega:** simulador online; export **Excel y PDF**. Prueba gratis.
Reclamo: "1% de mejora del TCO ≈ €2 M de ventaja por cada 10.000 coches vendidos".
**Nota [NO-VERIFICADO]:** la página NO desglosa públicamente los componentes individuales (combustible, seguro, neumáticos, VED/impuestos, electricidad). Se infiere que existen tras el simulador, pero no aparecen nombrados.

### 4.9 Repair Estimate — `/product/repair-estimate/`
Estimación de reparación, online/portal, multi-dispositivo. **Licenciado, sin cargo por estimación**, look-ups ilimitados.

**Campos / métricas atómicas:**
- `Parts Prices` (de bases de fabricante, **mensual**)
- `Labour Times` (disponible para **98% de vehículos** vía VRN)
- `Paint Data` (de bases de fabricante)
- `Vehicle Specifications` (match exacto en segundos)
- `Custom Items` (ítems definidos por usuario)
- `Labour Rate` ajustable (por estimación o global)
- `Shadow Vehicle Interface` (cubre huecos cuando falta el vehículo exacto)

**Cobertura:** 98% de vehículos, registrados últimos 20 años; cars + LCV populares UK; **excluye** algunas marcas de lujo (Ferrari, Bentley). Contratos con **>40 fabricantes**.

**Placement:** **interfaz gráfica** (click en cualquier pieza → su precio), selección múltiple de piezas, **PDF report builder** con plantillas, toolbar para custom items.

### 4.10 Data Feeds & APIs (familia Autovista*) — `/product/data-solutions/`
"All the data you need throughout the entire lifecycle of a vehicle". **>97% del parque europeo** identificable solo con código de matrícula; incluye todos los EV/híbridos; **20 años de histórico** de pricing. APIs = **pay-per-use** cloud con ajuste por km por vehículo; Data Feeds = datasets completos para procesamiento masivo. Guías de integración + soporte técnico incluido.

| Feed/API | Qué es | Campos atómicos clave | Entrega |
|---|---|---|---|
| **AutovistaSPEC** | Datos de especificación estandarizados | NatCode generado para valoraciones; specs estandarizadas; **list prices hasta 20 años**; EV: `charging time`, `driving range`, `battery capacity`; specs para underwriting de seguro | Feed (CSV tab-delimited) |
| **AutovistaVALUATION** | Valores residuales real-time | `Residual values`; `Mileage average`; specs; **15 mercados / 99% de vehículos y LCV**; ajuste por km por vehículo | API + Feed |
| **AutovistaFORECAST** | Forecast de RV | **16 age-mileage combinations**; **hasta 120 meses** de forecast; turismos + LCV | API |
| **AutovistaREFORECAST** | Riesgo de inventario | Funcionalidad **VIN**; **bulk-upload**; valor hoy y a fin de contrato | Feed |
| **AutovistaREPAIR** | Coste de reparación | Estimación coste reparación; identificación de pieza (incl. **superseded**); **AZT-sourced paint data**; gráficos click-to-price; **compatible TecDoc**; turismos + LCV | Feed |
| **AutovistaSMR** | Servicio/mantenimiento/reparación | `OEM-sourced service & maintenance price`; `labour times`; **predictive maintenance scheduling**; `service cost benchmarking`; part codes **TecDoc**; idiomas locales | Feed |
| **WLTP** | Emisiones/consumo nuevos | `WLTP CO2`; `WLTP consumption`; CO2/consumo por **cualquier combinación de opciones/packs**; "single interface for all makes/models/markets" → calcula impuestos y precio final | Web Service / integración con sistemas OEM |
| **EV Volumes** | Datos y forecast EV | ver 4.11 | Excel/PDF/CSV |

### 4.11 EV Volumes — `/product/ev-volumes/`
**>130 mercados**, **600+ modelos EV**, actualización **mensual** (origen: adquisición EV-Volumes por Autovista).

**Campos / métricas atómicas:**
- `EV sales by OEM` y `EV sales by model`
- `Registration data by geography` / penetración de mercado
- Cuota por powertrain: **BEV, PHEV, FCEV, HEV, MHEV**
- `Battery shipments` (tracking en **kWh** de cell makers a OEMs)
- `Cell-type specifications` y `cathode chemistries`
- `Cell-maker tracking`
- Capacidad de batería por modelo
- `Future model roll-outs`
- `Charging infrastructure` (expansión por país) + tipos de conector
- `Granular EV specifications and prices`
- Forecast EV

**Usuarios:** OEMs, flotas, gobiernos, inversores, proveedores de batería, consultoras.

---

## 5. Metodología / fuentes de datos

Fuente: [VERIFICADO] `glass.co.uk/our-accuracy/`, `/fastest-selling-cars/`, MVA.

**Fuentes de dato (UK):**
- **Subastas trade:** observaciones de **NAMA** (National Association of Motor Auctions).
- **Retail:** "UK's leading car advertising portals" — base de **8,4 M anuncios trade** (página fastest-selling) / **8,6 M observaciones retail** + **>250.000 anuncios de concesionario verificados** + **1,8 M observaciones trade** (página MVA). *(Discrepancia menor de cifras entre páginas; se reportan tal cual aparecen.)*
- **Input experto:** clientes, expertos del motor trade, fabricantes, dealers, subastadores, rent-a-car, leasing/contract hire.

**Proceso de valoración:**
1. Research desde casas de subasta + portales retail.
2. **Monthly editorial meetings** (reuniones editoriales mensuales).
3. Se genera un **% medio de depreciación** y se resaltan sectores/fabricantes/modelos fuertes.
4. **Cada sector** evaluado, **vetted y cross-checked** contra anomalías.
5. Cobertura desde forecasts de pre-producción hasta valores de los coches más antiguos.

**Datos del grupo (pan-EU):** datasets de pricing y especificación de Autovista Group con actualización por **expertos locales**, "transparent methodology", **state-of-the-art statistical procedures** (Car to Market). Segmentación robusta + medias ponderadas para comparación cross-country.

**Actualización:** valores MVA **mensual**; RVI **índice semanal**; RVM/Compare **mensual**; AutovistaVALUATION **continua/real-time**. Glass's **publica sus cifras de precisión cada mes**, contrastadas contra observaciones de subasta. Datos usados/confiados por el **Financial Ombudsman Service**.

---

## 6. Entrega

| Canal | Detalle |
|---|---|
| **Portal/Aplicación web** | Glass's platform, MVA, RVI, RVM, Compare, Car Cost Expert, Repair Estimate. Responsive, multi-dispositivo (Edge/Chrome/Firefox; no IE; tablet OK). Login + prueba gratis. |
| **API** | AutovistaVALUATION, AutovistaFORECAST (pay-per-use, cloud, ajuste km por vehículo). WLTP Web Service. |
| **Data Feed** | AutovistaSPEC (CSV tab-delimited), VALUATION, REFORECAST (VIN + bulk-upload), REPAIR, SMR. Datasets completos para procesamiento masivo. |
| **Export** | RVI/RVM gráficos+datasets descargables; Car Cost Expert Excel+PDF; EV Volumes Excel/PDF/CSV; MVA/Repair Estimate PDF report builder. |
| **Integración** | Guías de integración + soporte técnico; integración WLTP con sistemas OEM. **DMS import discontinuado** en MVA. |
| **Consultoría** | Car to Market (informe escrito + asesoría, 750 expertos/20 países). |

---

## 7. Precio (modelo)

- Modelo general: **suscripción/licencia** (no público en web). "One competitive set price" con look-ups **ilimitados** (Glass's platform, Repair Estimate "we do not charge per estimate").
- **APIs**: **pay-per-use** (cloud), con ajuste por km por vehículo.
- **Free trial** disponible en MVA, RVI, RVM, Compare, Car Cost Expert.
- Repair Estimate = producto **licenciado**, logins adicionales disponibles.
- Provenance (Experian) = **suscripción aparte**.
- `[NO-VERIFICADO]` cifras concretas de precio/tier: no publicadas; requieren contacto comercial.

---

## 8. Placement (patrón web — clave para cardeep)

Patrón que cardeep imitará para ubicar cada dato. Resumen por superficie:

| Dato / métrica | Dónde lo colocan (sección/pantalla) | Producto |
|---|---|---|
| Entrada de vehículo | **Vehicle lookup** por VRN/matrícula → identifica+valora "in seconds" | Glass's, MVA |
| Trade value + Retail (live) + Forecast + Depreciación | **Valuation screen** (ficha de valoración del vehículo); autosalva | Glass's, MVA |
| Ajuste por opciones de fábrica | Inline en la ficha de valoración ("adjust the price for factory-fitted optional extras") | Glass's |
| Desirability / Fastest Sellers / Highest Volumers / Most Desirable | **Market performance dashboard** (3 tiles KPI) | Glass's |
| Days-to-sell / stock days + live retail por región | **Fastest selling cars dashboard** (gráfico interactivo, filtro región/edad, 24 meses) | Glass's |
| Settlement figure + Spot price + Ad Search (avg advert price) | Módulo **Radar** dentro de MVA | MVA |
| Total Loss (repair cost + valuation ratio) | Indicador **Total Loss** en la ficha de siniestro | MVA |
| Imágenes/notas/adjuntos del caso | **Gestión de caso** (permission-based claims workflow) | MVA |
| Valoraciones guardadas | **Status dashboard** | MVA |
| Informe | **PDF report builder** ("my account > PDF reports") | MVA, Repair Estimate |
| Price Index (semanal) + 16 escenarios edad-km | **KPI Dashboard** + gráfico de índice | RVI |
| Cross-country weighted averages | Comparador cross-country (export de gráficos/datasets) | RVI |
| Performance ranking por RV + benchmark competitivo | **KPI dashboards** + tablas de ranking (17 mercados) | RVM |
| Optimize / Benchmark / Analyse | Tres modos/tabs del producto | Compare |
| Precio de pieza | **Interfaz gráfica click-to-price** (click en panel → precio) | Repair Estimate |
| Provenance | Check integrado vía Experian (sub. aparte) | Glass's |

Heurística de placement Glass's: **(1)** todo arranca en un look-up por matrícula; **(2)** la ficha del vehículo concentra trade/retail/forecast/depreciación/opciones; **(3)** las métricas de mercado (velocidad de venta, deseabilidad, volumen) viven en un **dashboard de KPIs separado**, no en la ficha; **(4)** RV/forecast y benchmarking cross-market viven en herramientas dedicadas con **gráfico de índice + ranking**; **(5)** el flujo de siniestro añade ratio reparación/valor + gestión documental; **(6)** la reparación usa un **diagrama gráfico de piezas** click-to-price.

---

## 9. Diferencial (lo que ofrece y otras no)

- **Marca-bíblia desde 1933**: equity de "trade guide" reconocida como benchmark del sector (heritage citado por el propio grupo y prensa).
- **Doble cara dato+app**: feeds/APIs Autovista* (SPEC/VALUATION/FORECAST/REFORECAST/REPAIR/SMR/WLTP/EV) **y** aplicaciones llave-en-mano sobre el mismo dato.
- **Transparencia de precisión**: publican **cifras de accuracy cada mes** contrastadas con subastas (poco común entre competidores).
- **Liquidación de siniestro nativa (MVA + Radar)**: settlement figures, spot prices, ratio reparación/valor, gestión de caso — datos confiados por el **Financial Ombudsman Service**.
- **Pan-europeo real**: misma metodología en 15-17 mercados con **medias ponderadas cross-country** (RVI/RVM/Compare) — ventaja del paraguas Autovista/Eurotax/Schwacke.
- **WLTP por configuración**: CO2/consumo para **cualquier combinación de opciones**, vía web service único multimarca/mercado → cálculo de impuestos/precio final.
- **EV Volumes (battery intelligence)**: tracking de **shipments de batería en kWh**, cell-maker, química de cátodo, conectores de carga, 130+ mercados — granularidad EV rara.
- **Forecast a 120 meses** con 16 combinaciones edad-km y stress-testing; **Car to Market** pre-lanzamiento hasta 4 años antes (750 expertos/20 países).
- **Repair Estimate gráfico click-to-price** con paint data AZT y compatibilidad **TecDoc**.

---

## 10. Gaps (lo que NO ofrece / límites detectados)

- **VIN no soportado en MVA** (la app de valoración va por VRM/Make-Model; VIN solo aparece en feeds como AutovistaREFORECAST y en mensajes de insurance). Inconsistencia VIN entre app y feed.
- **DMS import y revaluación masiva discontinuados** en MVA (perdió integración DMS directa en la app).
- **Componentes de TCO no desglosados públicamente** (Car Cost Expert no nombra combustible/seguro/neumáticos/impuestos como campos) `[NO-VERIFICADO]`.
- **No es un guía de historial/provenance propio**: la verificación de procedencia se **subcontrata a Experian** (sub. aparte) — no hay producto propio tipo HPI Check / write-off / finance / robo.
- **Sin marketplace ni subasta**: solo dato/valoración, no remarketing transaccional (a diferencia de BCA/Manheim).
- **Precio opaco**: sin pricing público ni tiers descubribles.
- **Excluye marcas de lujo** en Repair Estimate (Ferrari, Bentley).
- **Cobertura "real-time retail" centrada en UK**; el dato pan-EU se apoya en updates mensuales/semanales (no spot live como el UK retail).
- **Listas de atributos de especificación no publicadas al detalle** (AutovistaSPEC no enumera públicamente el set completo de campos técnicos: dimensiones, par, potencia, etc.) `[NO-VERIFICADO]` — confirmado que existen, pero el nº/nombres exactos no están en web abierta.
- **Discrepancia de cifras de observaciones** entre páginas (8,4 M vs 8,6 M vs 1,8 M) — no hay un único "data sheet" canónico público.

---

## 11. Fuentes (URLs)

**Glass's (primarias):**
- https://glass.co.uk/ (homepage, navegación, sectores)
- https://glass.co.uk/products/ (catálogo completo)
- https://glass.co.uk/product/glasss/
- https://glass.co.uk/product/market-value-assessor/
- https://glass.co.uk/welcome-to-market-value-assessor/ (Radar, VRM, 20/15 años)
- https://glass.co.uk/product/residual-value-intelligence/
- https://glass.co.uk/product/residual-value-monitor/
- https://glass.co.uk/product/compare/
- https://glass.co.uk/product/forecast/
- https://glass.co.uk/product/car-to-market/
- https://glass.co.uk/product/car-cost-expert/
- https://glass.co.uk/product/repair-estimate/
- https://glass.co.uk/product/data-solutions/ (AutovistaSPEC/VALUATION/FORECAST/REFORECAST/REPAIR/SMR)
- https://glass.co.uk/product/autovistavaluation/
- https://glass.co.uk/product/autovistaspec/
- https://glass.co.uk/product/service-maintenance-repair-data/ (AutovistaSMR)
- https://glass.co.uk/product/repair-data/ (AutovistaREPAIR)
- https://glass.co.uk/product/wltp/
- https://glass.co.uk/product/ev-volumes/
- https://glass.co.uk/pricing-valuations/
- https://glass.co.uk/vehicle-identification-specification/
- https://glass.co.uk/service-maintenance-repair/
- https://glass.co.uk/pricing-valuations/how-do-i-accurately-price-vehicles/
- https://glass.co.uk/pricing-valuations/how-can-i-track-residual-values/
- https://glass.co.uk/fastest-selling-cars/
- https://glass.co.uk/our-accuracy/
- https://glass.co.uk/sector/insurance/

**Externas (cross-verificación identidad/propiedad/mercado):**
- https://en.wikipedia.org/wiki/Glass's_Guide (fundación 1933, William Glass, cadena de propiedad)
- https://www.am-online.com/news/acquisitions-and-deals/2023/09/12/autovista-group-glass-s-owner-is-taken-over-by-jd-power
- https://www.jdpower.com/business/press-releases/autovista-group-acquisition-close (cierre 2024-03-01)
- https://www.jdpower.com/business/press-releases/autovista-group-acquisition-announcement
- https://www.vendormotive.com/vendors/glass-s (65.000 vehículos, current/live retail/forecast — vía snippet; fetch directo dio 429)
- https://www.am-online.com/dealer-management/retailing/motor-retailers-spoilt-for-choice-on-valuation-data (posición de mercado vs cap hpi)

---

### Verificación (doctrina VAM)
- **Identidad y propiedad:** ≥2 fuentes ortogonales (Wikipedia + JD Power PR + AM-Online). VERIFICADO.
- **Catálogo de productos:** página `/products/` + páginas individuales. VERIFICADO.
- **65.000 vehículos / live retail / forecast:** MVA + VendorMotive. VERIFICADO (2 vías).
- **Cifras de observaciones (8,4/8,6/1,8 M):** una vía cada una (páginas distintas); marcada la discrepancia.
- **Componentes TCO y set completo de specs:** `[NO-VERIFICADO]` (no publicados al detalle en web abierta).
