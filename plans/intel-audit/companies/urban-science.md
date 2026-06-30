# Urban Science — Auditoría atómica

> Slug: `urban-science` · Subdominio cardeep: **market-intelligence** · Región: **Global** (datos diarios = núcleo EE. UU.; consultoría/red = 70+ países)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó; `[ESTIMADO-3os]` para cifras de agregadores.
> Naturaleza: **consultoría + firma tecnológica de automoción**. NO es una "tabla/book de valor" ni un proveedor de
> precios/residuales. Su activo es **el DataHub™**: el único feed de **ventas reales near-real-time directas del fabricante**
> (no matriculaciones modeladas/retrasadas), sobre el que monta software de performance para **OEM, dealer y AdTech**.
> Pedigrí: inventó el **dot mapping** y la **planificación de red** moderna (site selection) en 1977.
> Marca pública: `Urban Science` · sitio: `urbanscience.com` · subsidiaria de software: `ChannelVantage` (channelvantage.com).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre | **Urban Science Applications, Inc.** ("Urban Science") | Wikipedia; urbanscience.com |
| Tipo | **Privada** (no cotiza); consultoría + tecnología automotriz | Wikipedia; ZoomInfo |
| Fundación | **1977** | Wikipedia; about; autonews |
| Fundador | **James A. "Jim" Anderson** | Wikipedia; about |
| Origen | 1977 **Cadillac** necesitaba ubicar **37.000 compradores en Chicago en un mapa** → Anderson inventa el **computer-generated dot mapping** y funda la firma para entregar la solución; luego desarrolla la **planificación de red** (nº y ubicación óptima de puntos de venta) | Wikipedia (verbatim) |
| HQ | **Renaissance Center, Detroit, Michigan (EE. UU.)** | Wikipedia; LeadIQ |
| Oficinas | **"over 20 offices"** (about) / **15 global offices** (Wikipedia) / **18 locations** (LeadIQ) — *discrepancia de fuente; rango 15-20* | about; Wikipedia; LeadIQ `[VERIFICADO con matiz]` |
| Países | **"over 70 countries"** (sirve a casi todos los OEM) / *"every corner of the world"* | Wikipedia; about |
| Empleados | **"over 850 employees"** (about) / **812** (RocketReach) / **500-1.000** (LeadIQ) | about; RocketReach; LeadIQ |
| Revenue (estimado) | **~$175,8 M** (Prospeo) / **~$189,8 M** (RocketReach) — *no oficial, agregadores* | Prospeo; RocketReach `[ESTIMADO-3os]` |
| Liderazgo (2026) | **Jim Anderson** President/CEO 1977→2026; pasa a **chairman (advisory)** tras nombrar a **Tom Longo** como **President/CEO** | Wikipedia (verbatim) |
| Subsidiaria | **ChannelVantage** — *"wholly owned subsidiary, formed in 2001 as a strategic alliance between General Motors and Urban Science"* (aloja el software de marketing/distribución) | Wikipedia (verbatim) |
| Metodología-marca | **"the Power of 4®"** = **people + process + data + technology** | about (verbatim) |

**Clientes objetivo (3 audiencias declaradas):**
1. **Manufacturers / OEMs** — Network, Sales, Aftersales, Marketing Performance.
2. **Dealers / grupos de concesionarios** — Dealership Performance.
3. **AdTech / agencias / publishers / plataformas** — Media Performance.

**Categorías de solución (6 "Performance" pillars):** (1) **Network Performance** · (2) **Sales Performance** ·
(3) **Aftersales Performance** · (4) **Marketing Performance** · (5) **Media Performance** · (6) **Dealership Performance**.
(Fuente: home + páginas /network/ /sales/ /aftersales/ (ETL) /marketing/ /media/ /dealer/.)

**Credenciales declaradas:** *"serves nearly every automotive OEM"* / *"served every major automaker"* en **70+ países**;
**40+ años** de experiencia; *"unique set of automotive data sourced directly from the automakers"*. (home; ZoomInfo; prnewswire.)

---

## 2. Cobertura

- **Datos diarios (DataHub™) = EE. UU.** (el activo near-real-time es US-céntrico):
  - **96% de TODAS las ventas de vehículo nuevo** y **99% de las ventas Certified Pre-Owned (CPO)** en EE. UU. (cifra canónica del site).
  - Variantes citadas: **97% del volumen de ventas US** (LiveRamp) y **"over 99% of total U.S. new vehicle sales"** (nota DriveTraffic) — el sello estándar es **96% nuevo / 99% CPO**. `[VERIFICADO con matiz]`
- **Consultoría + planificación de red + Network/Sales software:** alcance **global, 70+ países** (casi todos los OEM).
- **Aftersales en Europa:** alianza con **ETL Solutions** para extracción de datos de aftersales *"across Europe"* (ServiceView). `[VERIFICADO]`
- **Nuevo y usado:** **ambos** — nuevo (96%) + **CPO (99%)**. NO cubre usado independiente/no-CPO como dataset propio. `[VERIFICADO por ausencia]`
- **Tipos de vehículo:** vehículo ligero de pasajeros (light vehicle) del canal OEM/dealer; **no** hay producto declarado de heavy/commercial, moto o RV (a diferencia de S&P Global Mobility). `[NO-VERIFICADO exhaustivo]`
- **Naturaleza del dato:** **transacción de VENTA real** (no matriculación, no listing, no valoración). Granularidad **hasta ZIP code y dealer individual**.

---

## 3. Productos + campos atómicos

> Núcleo = **DataHub™** (dato). Encima, **20 productos nombrados** repartidos en los 6 pilares. Campos verbatim de las páginas.

### 3.0 DataHub™ — el feed de ventas (la base de todo)

*"the only near real-time source of industry-wide sales fueled directly from the automakers and not on modeled or
delayed vehicle registrations"*. Cobertura **96% nuevo / 99% CPO US**, **update diario**.
**Campos por transacción:** `date of sale` · `ZIP code` · `make` · `model` · `trim` · `previous purchase` · `selling dealer`.
Atributos de vehículo asociados (vía MarketView): `fuel type` · `body style` · `transmission` · `engine size`.
(Fuente: marketview; dealer; trafficview; marketing.)

### 3.1 MarketView™ — análisis de mercado/ventas (pilar Network + Sales)

Software de análisis competitivo. **Métricas:** `sales volume` · `market share` · `percent change` —
*"for any combination of brands, segments, models, geographies, and even competitive dealers"*.
**Dimensiones/atributos:** `make` · `model` · `trim` · `fuel type` · `body style` · `transmission` · `engine size` ·
`segment` · `brand` · `geography (macro → ZIP code)` · `competitive dealer` · `date of sale` · `previous purchase` · `benchmark`.
**Módulos:** vistas flexibles **market / brand / dealer**; **mapping macro→ZIP** con creación de mapas custom; filtros avanzados.
**Entrega:** dashboard web responsive, **export multi-formato** ("delivered to any platform"). Drill **market-level → dealer-level**.
**Privacidad:** *"stringent partitioning of dealer and brand data"*. (Fuente: marketview; channelvantage/marketview; sales.)

### 3.2 NetworkPlanner™ — planificación de red de nueva generación (lanzado 26-feb-2026)

Plataforma online de **visualización + optimización** de red de dealers. **Capacidades/campos:**
`dealership location` · `competitor location` · `EV charging station location` · `point of interest (POI)` · `network health` ·
**overlay de KPIs + location data** · `pan / zoom / query` interactivo · **automated performance summaries** *"across every
geographic level"* · captura de **feedback de stakeholders** in-interface · **export de mapas y reports**. Permite *"test and
tailor networks"* (escenarios) sobre **datos de venta + procesos científicos** propios. (Fuente: PR NetworkPlanner 26-feb-2026; networkplanning.)

### 3.3 Network Planning™ (consultoría) — el 8-step Dealer Network Analysis Process

Proceso propietario en **4 fases**: **(1) Market Foundations** (competitive landscape, dealer territories, equitable sales
targets) → **(2) Network Scenarios** (nº recomendado de dealerships, ubicaciones ideales, tipo de facility, mejor operador) →
**(3) Performance Benchmarks** (cuantifica oportunidad real con benchmarks *"que tienen en cuenta el local consumer preference"*) →
**(4) Action Planning** (estrategia incremental hacia la red ideal).
**Campos/outputs:** `market opportunity (quantified)` · `sales potential` · `network coverage` · `local consumer preference` ·
`dealer territory` · `equitable sales target` · `recommended number of dealerships` · `facility type recommendation` ·
`dealer operator identification`. **Tool de location intelligence asociado: Ni2®** *"the industry's most comprehensive
location intelligence tool"*. (Fuente: networkplanning.)

### 3.4 NetworkDynamics™ — gestión de red / contratos / workflow (single source of truth)

*"comprehensive solution for network-wide efficiency and consistency"*. **Campos/funciones:**
`digital dealer contract repository` (puntos de dealer, **relocations**, **buy/sells**, **terminations**) ·
**workflow** multi-departamento (notificaciones automáticas, escalations, real-time status) · **brand-standards compliance audit** ·
`facility guidelines` · `customized follow-up / noncompliance correction plans` · repositorio central de planes/acciones/
programas/performance · validación de calidad de dato. **Entrega:** **mobile-first**, role-based, *"anywhere/anytime"*.
**Métrica de caso:** dealerships participantes **+32% incremental unit sales** vs no participantes. (Fuente: networkdynamics.)

### 3.5 ServiceView™ — performance de aftersales (Service & Parts)

*"premier science-driven aftersales performance solution"*. **Campos atómicos:**
`service retention rate` (clientes retenidos vs perdidos) · `service advisor performance` · `technician performance` ·
`service-to-sales conversion` · `service-loyal customer defection` · `parts sales volume` ·
`incremental wholesale parts opportunity` · benchmark vs **local & national composites** · `service bay optimization`
(nº óptimo de bays) · `technician staffing requirement` · `recall completion rate` · `missing/lost service traffic` ·
`new customer conversion in service lane`. **Entrega:** dashboard responsive + **Tableau API integration** (self-service con
*"information firewalls"*). **Integración Europa: ETL Solutions** (extracción de dato aftersales). (Fuente: serviceview; PR ETL.)

### 3.6 FinancialView™ — salud financiera de la red (versión Sales + versión Aftersales)

Monitoriza la **salud financiera del dealer/red**. **Campos:** `dealer financial KPI (tracked geographically)` ·
`dealership profitability` · benchmark vs **composite groups relevantes** · `network financial health (OEM→dealer)` ·
**módulo de business planning online** · **"what-if" scenario planning** (modela `EV adoption` · `shifting policies` ·
`disruptive technologies` · `tariffs`). Versión **aftersales** = profitability de Service & Parts. (Fuente: financialview/; aftersales/financialview/; insightlab.)

### 3.7 TrafficView® — match CRM × ventas reales (Marketing + Dealership)

*"first-ever insights into your dealers' traffic by matching CRM data with industry-wide sales data from the DataHub"*.
**Campos:** `lead source` · `sales (unit)` · `defections (to competitor)` · `same-brand defections` · `model` · `trim` ·
`salesperson` · `geography / ZIP` · `date of sale` · `previous purchase` · **`90 Days to Sale` (consumer journey)** ·
`inventory mix` · `close/conversion rate` · `group-level performance` · `lead quality` · `sales generated`.
**Integración:** **15+ CRM/CDP** (VINSolutions, CDK eLeads, DealerSocket, Reynolds & Reynolds, Tekion…), API en **95% de
sistemas**; entrega a *"all major platforms"*. (Fuente: trafficview/; marketing/trafficview/; dealer; PR new features.)

### 3.8 SalesAlert™ — alertas de defección (Dealership)

Notifica al dealer cuando un cliente **defecciona** (vía **CRM / API notification**); **automatic closure of defected leads**.
Detalle de defección: `date of sale` · `ZIP code` · `make/model/trim` · `previous purchase` · `selling dealer` · `same-brand defection`.
**Resultado de caso:** *"up to 20% decrease in defections in your first 90 days"*. (Fuente: dealer; trafficview.)

### 3.9 AutoHook® — ofertas/incentivos → showroom (Sales + Marketing)

Convierte prospectos in-market en **visitas a showroom y ventas** vía **private offers** (text / email / website overlay / API).
**Targeting:** `model` · `individual vehicle` · `inventory age` · `geography` · `lead source`. **Triggers:** `page view` ·
`site reentry` · `KPI completion`. **Scoring:** `intent-to-buy`. **Incentivo:** valor ajustable test-drive/compra + **gift cards/virtual cards**.
**Atribución directa:** `impressions` · `showroom visits` · `sales` · `losses` (real-time campaign reporting). **Seguridad:**
2FA, verificación de identidad en redemption, fraud detection, **redemption en 30s**. **Conversión hasta 39%** (dealer page). (Fuente: sales/autohook/; dealer.)

### 3.10 MarketGrowth™ — expansión/DMA (Dealership)

*"most in-depth designated marketing area (DMA) data available"*. **Campos:** `DMA dynamics (current + historical, down to
dealer level)` · `actual vs expected sales volume` (brand effectiveness) · `market share trend` · `segment / model detail` ·
`competitive performance vs other dealers` · **`growth brands` (por market share y volume)**. **Cadencia:** **daily** (next-day
sales) · **monthly** (reporting) · **quarterly** (planning). Target: grupos evaluando adquisición/expansión. (Fuente: marketgrowth/.)

### 3.11 LeadManagement™ + MediaPerformance™ + RetailPer4mance™ + DriveTraffic

- **LeadManagement™** (Marketing): *"industry-standard lead generation, capture, distribution and tracking"* para dealers. `lead quality` · `sales generated`.
- **MediaPerformance™** (Marketing): optimización **cross-channel** con sales data diaria para **probar ROI**.
- **RetailPer4mance™ con TrafficView®** (Sales): examina **4 áreas** → `inventory` · `traffic` · `value proposition` · `sales experience`; near-real-time sales insight.
- **DriveTraffic** (umbrella Marketing): paquete = **TrafficView + AutoHook** para drive/measure de **showroom traffic**; **partner CTV: VDX.tv** (desde 2019). (Fuente: marketing; sales; retailper4mance; drivetraffic; VDX.tv.)

### 3.12 Media Performance (AdTech) — 4 productos sobre el DataHub

**(a) In-Market Audiences™** — segmentos **people-based** de compradores **predichos a 0-3 meses / 90 días**.
**Audiencias:** `automotive brand` · `make/model` (incl. launch models) · `vehicle segment` (incl. **EV**) · `conquest/competitor` (customizable).
**Señales de construcción (vía LiveRamp):** `purchase history (make, model, segments)` · `location relative to dealership` ·
`demographics` · `lifestyle` · `life stage` · `household demographics` + **machine learning** (predice el próximo vehículo del hogar).
**Lift (purchase rate):** **10×** overall · **25×** brand · **7×** segment · **5×** EV · **2,5×** vs *"leading competitors"*.
**(b) Suppression Audiences™** — excluye compradores recientes; *"layer across all data"*; reinversión de **10-15% del budget**; *"closer to real-time than any other solution"*.
**(c) Planning Intelligence™** — planning de medios con benchmarking competitivo **down to ZIP / dealer / segment**; win/loss.
**(d) SalesMatch™** — **atribución determinista, first-party** ad-exposure → venta real *"at scale"*, *"directly in your current reporting tools"*.
**Resultados de caso:** **43× ROAS** (OEM en social) · **+66% Tier 1 sales attribution** · **+83% Tier 2 lift** · **−12% cost per unit sold**.
**Métricas/fields de SalesMatch:** `Buy-Through Rate (BTR)` · `Ad Frequency` · `ID Reach` · `Media CPM` · `Impressions` · `Incremental Vehicle Sales %`.
**Integración:** **The Trade Desk (UID2)** · **LiveRamp** (RampID/identidad) · **VDX.tv (CTV)** · *"all major platforms"* (DSP/social/publishers/CTV). (Fuente: media; media/platforms; media/agencies; PR ad-targeting; LiveRamp.)

---

## 4. Metodología / fuentes de datos

- **DataHub™ = first-party OEM feed:** dato de **venta** entregado **directamente por los fabricantes**, *"as frequently as
  daily"* — explícitamente **NO** matriculaciones modeladas ni retrasadas. Es la diferencia metodológica central frente a
  proveedores basados en registration (Polk/S&P). Cobertura **96% nuevo / 99% CPO US**.
- **Machine learning** sobre el DataHub para predicción (In-Market Audiences) y scoring de intención.
- **Matching determinista first-party** (SalesMatch): person-based, conecta exposición de anuncio con venta real (no probabilístico).
- **CRM/CDP matching** (TrafficView/SalesAlert): cruza el CRM del dealer con el DataHub; **15+ integraciones**, API en 95% de sistemas.
- **Composite benchmarking** (ServiceView/FinancialView/MarketGrowth): compara dealer vs **composites locales y nacionales**;
  benchmarks *"equitativos"* que ajustan por **local consumer preference** (herencia de network planning).
- **Location intelligence / dot mapping** (NetworkPlanner/Ni2/Network Planning): geoespacial — núcleo histórico desde 1977.
- **"Power of 4®"**: people + process + data + technology (consultoría con equipos on-site + software).
- **Identidad/activación de medios:** vía **LiveRamp** (RampID) y **The Trade Desk (UID2)**.
- **Aftersales EU:** extracción de dato vía **ETL Solutions**.
(Fuentes: marketview; media/platforms; trafficview; serviceview; networkplanning; LiveRamp; PR ETL.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Data feed (DataHub)** | Ventas OEM **diarias / near-real-time**; *"can be delivered to any platform"*. |
| **Software web / dashboards** | MarketView, ServiceView, FinancialView, MarketGrowth, NetworkPlanner, NetworkDynamics, TrafficView — drill market→dealer, filtros, mapping. |
| **Mobile-first / responsive** | NetworkDynamics (mobile-first, role-based), MarketView (responsive). |
| **BI embebido** | **ServiceView vía Tableau API** (self-service con information firewalls). |
| **API / notificaciones** | SalesAlert (**API notification** de defección + auto-close), AutoHook (API a vendors), TrafficView (API en 95% de CRM/CDP). |
| **Export** | MarketView/NetworkPlanner: **export multi-formato** de datos, mapas y reports. |
| **Integración CRM/CDP** | **15+** (VINSolutions, CDK eLeads, DealerSocket, Reynolds & Reynolds, Tekion…). |
| **Activación AdTech** | **LiveRamp** (audiencias In-Market/Suppression), **The Trade Desk (UID2)**, **VDX.tv (CTV)**, social/DSP/publishers. |
| **Consultoría** | Equipos **on-site**, **8-step Dealer Network Analysis Process**, business planning online (FinancialView). |
| **Subsidiaria software** | **ChannelVantage** (channelvantage.com) aloja MarketView/FinancialView para distribución. |

---

## 6. Precio (opaco — enterprise/consultoría)

| Producto | Precio | Fuente |
|---|---|---|
| **Todos** (MarketView, TrafficView, ServiceView, FinancialView, NetworkPlanner, NetworkDynamics, MarketGrowth, AutoHook, audiencias Media) | **No público** — licencia/suscripción/consultoría enterprise negociada ("Contact"/demo). Sin tarifa en G2/Capterra. | búsqueda G2/Capterra (sin listing); páginas con CTA contacto `[NO-VERIFICADO importe]` |
| Modelo | **B2B**: consultoría + suscripción de software + servicios de dato/medios; sin self-service ni precio de consumo | inferido del catálogo `[ASUMIDO]` |

> No se encontró **ninguna** tarifa pública ni listing en marketplaces de software. Precio 100% enterprise/negociado.

---

## 7. Placement (patrón web — clave para cardeep)

> Urban Science NO tiene "ficha de coche" de consumo: su UI son **dashboards B2B de performance** y **mapas de red**.
> El patrón valioso para cardeep es **(a) el embudo cerrado venta-real** y **(b) dónde cuelga cada métrica en cada panel**.

**A. Panel/overview de mercado (MarketView).** Vista tipo cubo: selector de **brand/segment/model/geography/dealer** → tres
KPIs maestros **`volume` · `market share` · `% change`**, con **benchmark** al lado y **mapa macro→ZIP**. Toggle de módulo
**market / brand / dealer**. (Patrón: el dato de mercado vive en un panel filtrable multidimensión, no en una ficha.)

**B. Mapa de red (NetworkPlanner / Ni2).** **Mapa interactivo** con pins de **dealership / competidor / EV charging / POI**,
**overlays de KPI**, pan/zoom/query, y **automated summaries** por nivel geográfico en panel lateral. (Patrón: ubicación +
oportunidad cuantificada sobre mapa — el "site selection".)

**C. Dashboard de dealer / journey (TrafficView).** Tabla/breakdown por **lead source · model · salesperson · geography**, con
**defections** y **same-brand defections** resaltadas, **`90 Days to Sale`** como línea de tiempo del cliente, e **inventory mix**.
(Patrón: rendimiento del concesionario con el customer journey de contacto→venta.)

**D. Alerta (SalesAlert).** No es panel: es **notificación push/API** "tu cliente se fue a la competencia" con el detalle de la
transacción (make/model/trim, ZIP, dealer ganador). (Patrón: alerta event-driven sobre la ficha/CRM del cliente.)

**E. Dashboard de aftersales (ServiceView).** Panel de **retention · parts · bays · recall · service-to-sales** con benchmark
vs composite, en **Tableau** con firewalls de dato. (Patrón: vertical de servicio separado del de ventas.)

**F. Dashboard financiero (FinancialView).** KPIs financieros **geográficos**, benchmark vs composite, y **panel de what-if**
(EV/policy/tariff) — business planning. (Patrón: capa de rentabilidad como pantalla aparte.)

**G. Atribución embebida (SalesMatch).** No es UI propia: los KPIs (`BTR`, `ID Reach`, `Media CPM`, `Incremental Vehicle
Sales %`, `ROAS`) se inyectan **dentro de la herramienta de reporting del cliente** (DSP/social). (Patrón: el dato de
performance se entrega *donde el usuario ya mira*, no en un portal nuevo.)

**H. Audiencias activadas fuera (In-Market/Suppression).** El "dónde" es **el DSP/plataforma social del anunciante** vía
LiveRamp/UID2 — Urban Science no muestra la audiencia, la **entrega activable**. (Patrón: dato como segmento portable.)

> **Lectura cardeep:** Urban Science demuestra el patrón **"dato de mercado en panel multidimensión filtrable (volume/share/%
> change) + mapa de ubicación con oportunidad cuantificada + alerta de defección event-driven"**, todo **anclado a venta real**
> (no a listing ni a valoración). Es el complemento del eje "ficha + valor": aquí el dato vive en **overview de mercado, mapa y
> alerta**, no en la ficha del coche.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **DataHub™ = ventas reales near-real-time directas del OEM** (96% nuevo / 99% CPO US), **NO** matriculaciones modeladas/
   retrasadas. Único feed diario de transacción real de la industria. Es su foso.
2. **Closed-loop venta-real de punta a punta:** medios (SalesMatch determinista, audiencias) → showroom (AutoHook) → venta
   (DataHub) → servicio (ServiceView) → red (NetworkPlanner). Toda métrica atada a **venta confirmada**, no a proxies.
3. **Pedigrí en network planning / site selection** (dot mapping, 1977): **8-step process**, Ni2, NetworkPlanner — disciplina
   geoespacial de red que las "tablas de valor" no tocan.
4. **Atribución determinista first-party** (SalesMatch): **43× ROAS**, person-based, dentro del reporting del cliente.
5. **In-Market Audiences con lift verificado** (**25× brand**, **2,5× vs competidores**) construidas sobre ventas reales + ML.
6. **Benchmarks "equitativos" ajustados por local consumer preference** (herencia de planificación de red) en Service/Financial/Market.
7. **Defección como producto** (SalesAlert/TrafficView): detecta y alerta cuando un cliente compra en otro dealer/marca — métrica que requiere ver **toda** la venta de la industria.
8. **Consultoría + software híbrido** con casi **todos los OEM** en **70+ países** y equipos on-site (Power of 4®).
9. **`90 Days to Sale`** y `service-to-sales conversion`: visión del **journey real** contacto→venta y venta→servicio.

---

## 9. Gaps (lo que NO ofrece)

1. **NO es valoración/pricing de vehículo:** sin `residual value`, `retail/trade price`, `price-to-market %`, **curva de
   depreciación**, `market days supply`, `days-to-sell`. No hay "book of value". ← **clave para cardeep**: complementario, no competidor en valoración.
2. **NO historial de vehículo** (sin equivalente CARFAX): ni siniestros, ni odómetro, ni nº de dueños a nivel VIN.
3. **NO specs/equipamiento por VIN** ni VIN decode como producto. Sus atributos (fuel/body/trans/engine) son de **agregación de mercado**, no ficha técnica por unidad.
4. **NO listings/marketplace de inventario** ni métricas de velocidad de mercado por anuncio (days-to-sell, supply, price-to-market). Mide **ventas**, no inventario online.
5. **Dato diario = US-céntrico** (96/99% US). Fuera de EE. UU. su valor es **consultoría/red**, no el feed near-real-time.
6. **Usado limitado a CPO (99%)**: sin dataset de usado independiente/no-CPO ni precios de usado.
7. **Sin tipos de vehículo ampliados** (heavy/commercial, moto, RV) como producto declarado.
8. **Precio 100% opaco** (sin self-service ni tarifa pública).
9. **Sin producto de consumo / DTC:** pura B2B (OEM/dealer/AdTech); no hay portal ni app de comprador final.
10. **Owner demographics limitado:** usa `demographics/lifestyle/life stage/household` para audiencias de medios, pero **no** vende un panel de demografía de propietario tipo Polk. `[NO-VERIFICADO exhaustivo]`

---

## 10. Fuentes

**Sitio oficial (urbanscience.com) — vía WebFetch/WebSearch:**
- Home (taxonomía 6 pilares, DataHub, "nearly every OEM"): https://www.urbanscience.com/
- About (1977, Power of 4®, >20 oficinas, >850 empleados): https://www.urbanscience.com/about/
- MarketView (volume/share/%change, atributos, módulos): https://www.urbanscience.com/marketview/ · https://www.urbanscience.com/sales/marketview/
- ChannelVantage MarketView (campos make/model/trim/fuel/body/trans/engine): https://www.channelvantage.com/sales/marketview/
- Network Performance (NetworkPlanning/NetworkDynamics/MarketView): https://www.urbanscience.com/network/
- Network Planning (8-step, 4 fases, Ni2®): https://www.urbanscience.com/networkplanning/
- NetworkDynamics (contratos/workflow/compliance, +32% caso, mobile-first): https://www.urbanscience.com/networkdynamics/
- ServiceView (retention/parts/bays/recall, Tableau API): https://www.urbanscience.com/serviceview/
- FinancialView (Sales + Aftersales, what-if EV/tariff): https://www.urbanscience.com/financialview/ · https://www.urbanscience.com/aftersales/financialview/
- Sales Performance (RetailPer4mance, MarketView, AutoHook, FinancialView): https://www.urbanscience.com/sales/
- Marketing Performance (LeadManagement, TrafficView, AutoHook, MediaPerformance): https://www.urbanscience.com/marketing/
- TrafficView (lead source/salesperson/defection/90-days-to-sale/inventory mix; 15+ CRM): https://www.urbanscience.com/marketing/trafficview/ · https://www.urbanscience.com/trafficview/
- AutoHook (offers, targeting, triggers, attribution, redemption): https://www.urbanscience.com/sales/autohook/
- MarketGrowth (DMA, actual vs expected, growth brands, daily/monthly/quarterly): https://www.urbanscience.com/marketgrowth/
- Dealership Performance (SalesAlert, AutoHook, TrafficView, MarketGrowth; 20% defection caso, 39% conv): https://www.urbanscience.com/dealer/
- Media Performance + Platforms + Agencies (SalesMatch, In-Market/Suppression/Planning Intelligence; 43× ROAS; BTR/ID Reach/CPM; UID2): https://www.urbanscience.com/media/ · https://www.urbanscience.com/media/platforms/ · https://www.urbanscience.com/media/agencies/
- DriveTraffic (umbrella TrafficView+AutoHook; defección 20%/2025): https://www.urbanscience.com/drivetraffic/

**Press releases / recursos (urbanscience.com + prnewswire):**
- NetworkPlanner launch (26-feb-2026; mapping dealership/competitor/EV charging/POI; pan/zoom/query): https://www.urbanscience.com/resources/urban-science-reinvents-the-automotive-retail-network-planning-experience-through-networkplanner-launch/
- In-Market Audiences enhanced (10×/25×/7×/5×; ML; daily): https://www.prnewswire.com/news-releases/urban-science-sets-new-standard-in-automotive-ad-targeting-through-machine-learning-powered-by-unrivaled-industry-sales-data-302257457.html · https://www.urbanscience.com/resources/urban-science-sets-new-standard-in-automotive-ad-targeting-through-machine-learning-powered-by-unrivaled-industry-sales-data/
- ETL Solutions / aftersales Europe (ServiceView extraction): https://www.urbanscience.com/resources/urban-science-and-etl-solutions-team-up-to-make-automotive-aftersales-data-extraction-cost-effective-and-efficient-across-europe/
- TrafficView new features (defection + group-level): https://www.urbanscience.com/resources/new-trafficview-features-deliver-deeper-defection-insights-and-group-level-performance-clarity/
- Close rate vs defection rate (16% defect internet leads, 6% 30-day close): https://www.urbanscience.com/resources/close-rate-vs-defection-rate-what-both-metrics-reveal-about-dealership-performance/

**Identidad / finanzas / terceros:**
- Wikipedia (1977, Anderson, Renaissance Center, 15 oficinas/70+ países, ChannelVantage 2001 GM JV, Longo CEO 2026): https://en.wikipedia.org/wiki/Urban_Science
- LeadIQ (500-1000 empleados, 18 locations): https://leadiq.com/c/urban-science/5a1d82f424000024005dbf50
- ZoomInfo (perfil): https://www.zoominfo.com/c/urban-science/40092043
- RocketReach (812 empleados, ~$189,8 M): https://rocketreach.co/urban-science-profile_b5c492eaf42e0dc9
- Prospeo (~$175,8 M revenue): https://prospeo.io/c/urban-science-revenue
- LiveRamp partner (In-Market/Suppression, 97% volumen US, señales de audiencia): https://partner-directory.liveramp.com/partners/urban-science
- VDX.tv partnership (CTV, drive/measure traffic, 2019): https://www.vdx.tv/blog/vdx-tv-and-urban-science-empower-automotive-marketers-to-drive-and-measure-dealership-traffic

### Notas de verificación
- **Identidad (1977, Anderson, Detroit RenCen, ChannelVantage, Longo CEO 2026):** Wikipedia + about + autonews. **[VERIFICADO]**
- **DataHub 96% nuevo / 99% CPO:** repetido en marketview, dealer, serviceview, marketing, trafficview, marketgrowth. Variantes 97% volumen (LiveRamp) y "99% total new" (DriveTraffic) anotadas. **[VERIFICADO con matiz]**
- **Campos atómicos por producto:** página de producto directa + corroboración WebSearch en cada caso. **[VERIFICADO]**
- **Lifts In-Market (10/25/7/5×, 2,5× vs competidores) y 43× ROAS / +66% Tier1 / +83% Tier2 / −12% CPU (SalesMatch):** PR + media/platforms + media/agencies. **[VERIFICADO]**
- **+32% unit sales (NetworkDynamics), 20% defección (SalesAlert), 39% conversión (AutoHook):** páginas de producto/dealer (casos). **[VERIFICADO afirmación; importes = claims de marketing]**
- **Empleados/oficinas/revenue:** rangos por discrepancia entre fuentes (15-20 oficinas; 500-1000 empleados; $175-190 M). **[VERIFICADO rango / ESTIMADO-3os revenue]**
- **Gaps (sin valoración/historial/VIN/listings; US-céntrico; B2B):** inferidos por **ausencia** en todo el catálogo navegado. **[VERIFICADO por ausencia]**
- **Tipos de vehículo ampliados y owner demographics:** no hallados como producto; marcados **[NO-VERIFICADO exhaustivo]**.
- **Precio:** sin tarifa pública ni listing en G2/Capterra. **[NO-VERIFICADO importe]**
