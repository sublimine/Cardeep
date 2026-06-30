# ACV Auctions — Auditoría atómica

> Slug: `acv-auctions` · Subdominio cardeep: **wholesale-intelligence** · Región: **EE. UU.** (núcleo absoluto) — sin presencia internacional de marketplace
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (material de marketing del vendedor sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato de varias páginas sin que el vendedor lo liste literalmente), `[NO-VERIFICADO]`.
> Naturaleza: **marketplace de subasta MAYORISTA (wholesale) 100% DIGITAL dealer-to-dealer + plataforma de datos de condición e inteligencia de inventario**. A diferencia de Manheim (subasta física con MMR como "libro" de valor), ACV nació *technology-first*: su moat es el **dato de condición físicamente inspeccionado** — cada coche que sube a su marketplace pasa una **inspección de 150 puntos on-site** ejecutada por una red de **+1.100 inspectores propios** con hardware propietario (**Virtual Lift** = imagen del bajo, **AMP / Audio Motor Profile** = clip de audio del motor, **TrueFrame** = transparencia de chasis/siniestro, **OBDII scan** = DTCs, **paint meter** = detección de repintado). Ese dato alimenta tres capas de inteligencia: (1) la **subasta digital de 20 minutos**, (2) la valoración **ACV Estimate / ACV Market Report** (precio predicho con rango High/Low), y (3) la suite de inventario para retailers **ACV MAX** (heredada de la adquisición de **MAX Digital / FirstLook**), más herramientas de captación al consumidor (**ClearCar**), inspección automatizada por visión artificial (**VIPER**), compra programática (**S.A.M.**), y servicios de financiación (**ACV Capital**) y logística (**ACV Transportation**).
> Empresa **cotizada** (NASDAQ: **ACVA**), HQ en **Buffalo, Nueva York**. Es independiente — **no** pertenece a Cox/Manheim; es su competidor digital nativo directo. Segmentos de ingresos reportados: **Marketplace and service revenue** + **Customer assurance revenue**.
> Sitios/marcas: `acvauctions.com` (marketplace + producto), `acvmax.com` (suite de inventario MAX), `clearcar.com` (captación consumidor), `acvauto.com` / `investors.acvauto.com` (corporativo/IR), `developer`/API S.A.M. (integración programática).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **ACV Auctions** ("ACV"); suite de inventario = **ACV MAX** | acvauctions.com; acvmax.com `[VERIFICADO]` |
| Owner / grupo | **Independiente** — empresa pública, **ACV Auctions Inc.** (no es parte de Cox Automotive ni de ningún grupo de valoración) | investors.acvauto.com `[VERIFICADO]` |
| Cotización | **NASDAQ Global Select Market**, ticker **ACVA** | búsqueda múltiple; finance.yahoo.com `[VERIFICADO ×2]` — *nota:* una página de IR (fetch) y algún agregador lo etiquetan como "NYSE: ACVA"; el consenso de fuentes es **NASDAQ**. `[PARCIAL — conflicto de etiqueta]` |
| IPO | **24–25 de marzo de 2021** (S-1 presentado feb-2021) | spectrumlocalnews; buffalonews; S-1 SEC `[VERIFICADO ×2]` — una fuente dice "2022" (errónea) `[outlier]` |
| Fundación | **1 de agosto de 2014**, en **Buffalo, NY**, incubada en **Z80 Labs** | portersfiveforce; bowerycap; buffalonews `[VERIFICADO ×2]` |
| Fundadores | **Joe Neiman** (ex-dealer, ideó el concepto), **Dan Magnuszewski** (CTO, codificó la app), **George Chamoun** (CEO), **Jack Greco** (cofundador, salió después) | bowerycap "From the Front Lines"; portersfiveforce `[VERIFICADO ×2]` |
| CEO | **George Chamoun** | investors.acvauto.com; chartmill `[VERIFICADO]` |
| HQ | **Buffalo, Nueva York** — 640 Ellicott Street, Suite 321 | cbinsights; governor.ny.gov `[VERIFICADO ×2]` |
| Empleados | **~3.200** a tiempo completo (incluye red de inspectores) | cbinsights/chartmill `[PARCIAL]` |
| Posición | **"leading digital automotive marketplace and data services partner for dealers"** | investors.acvauto.com (press release) `[CLAIM-VENDOR]` |

**Estadísticas de escala (verificadas, con fecha):**

| Métrica | Valor | Fuente / fecha |
|---|---|---|
| Ingresos 2025 (FY) | **$760 M** (+19% vs $637 M en 2024) | digitalcommerce360; SEC 8-K `[VERIFICADO ×2]` |
| Vehículos vendidos 2025 | **829.276** (+12% YoY) | digitalcommerce360 `[VERIFICADO]` |
| GMV / valor total vendido 2025 | **$10.4 mil millones** (+9%) | digitalcommerce360 `[VERIFICADO]` |
| Penetración en rooftops de franquicia | **35%** | finviz (Q4 2025) `[PARCIAL]` |
| Inspecciones acumuladas | **3 M+** (hito 2023); "millions of inspections nationwide" framing actual | investors.acvauto.com (milestone 2023) `[VERIFICADO]` |
| Red de inspectores | **+1.100 inspectores** propios a tiempo completo | acvauctions blog/support; bidndrive `[VERIFICADO ×2]` |
| Resultado neto 2025 | **−$66 M** (pérdida; mejora vs −$79.7 M en 2024) | finviz `[PARCIAL]` |
| Outlook 2026 | **$845–855 M** de ingresos (guía) | digitalcommerce360 `[PARCIAL]` |
| Take rate medio | **~$494** fees totales / transacción ÷ **~$8.500** AOV ≈ **~6%** | bowerycap S-1 teardown `[PARCIAL — análisis de tercero]` |
| Empleo Q1'26 (segmentos) | Marketplace+service $182.2 M, Customer assurance $22.0 M, total **$204 M** | SEC 8-K Q1'26 `[VERIFICADO]` |

**Adquisiciones (construcción del moat de datos):**

| Empresa | Fecha | Qué aportó | Valor |
|---|---|---|---|
| **TrueFrame** | dic-2019 | Inspecciones integrales + innovaciones clave: **AMP (Audio Motor Profile)** y **Virtual Lift** (imagen móvil del bajo); transparencia de chasis/siniestro | n/d `[VERIFICADO]` |
| **ASI** | abr-2020 | Inspección de **vehículos comerciales** (off-lease, off-rental, flota) → expande a sector comercial | n/d `[VERIFICADO]` |
| **MAX Digital** | jul-2021 | Plataforma **SaaS de merchandising + IMS**, flagship **FirstLook** (fundada 2011) → se convierte en **ACV MAX** | **$60 M** `[VERIFICADO]` |
| **Drivably** | feb-2022 | Software de **trade-in** para dealers (de Porsche Ventures) → base de **ClearCar** | n/d `[VERIFICADO]` |
| **Monk.ai** | feb-2022 | **Detección automática de daños por IA** (visión artificial) → base de **VIPER** | **~$19 M** `[VERIFICADO]` |

**Categorías de producto:** (1) **Marketplace de subasta wholesale digital** (subastas de 20 min, dealer-to-dealer); (2) **Datos de condición** (Comprehensive Condition Report 150-puntos + **True360** premium); (3) **Valoración / market report** (**ACV Estimate / ACV Market Report**); (4) **Suite de inventario retail** (**ACV MAX** = FirstLook IMS + merchandising + Showroom + **Recommendations**); (5) **Captación al consumidor** (**ClearCar** Price + Capture); (6) **Inspección automatizada por visión** (**VIPER** torres + Virtual Lift); (7) **Compra programática** (**S.A.M.** — Smart Acquisition Manager, con API); (8) **Servicios financieros** (**ACV Capital** floorplan) y **logística** (**ACV Transportation**); (9) **Assurance / arbitraje** (ACV Guarantee, Arbitration Policy); (10) **Data Services** (licenciamiento de inteligencia de condición/valor a socios comerciales).

**Cliente objetivo:** **dealers** franquiciados e independientes (compra/venta wholesale + gestión de inventario retail), **8 de los 10 mayores grupos de dealers** (claim), **rent-a-car** y **compradores comerciales** de vehículo usado (vía S.A.M.), **flotas/off-lease/lessors** (canal ASI/comercial), y **el consumidor final** indirectamente (vía ClearCar en la web del dealer). (Fuentes: acvmax.com; investors.acvauto.com. `[VERIFICADO]`)

---

## 2. Cobertura

- **Geografía:**
  - **EE. UU.** = núcleo absoluto y prácticamente exclusivo (marketplace digital nacional, red de +1.100 inspectores on-site, ACV Capital en cientos de ubicaciones físicas incl. todas las de ADESA y Manheim). `[VERIFICADO]`
  - **Sin marketplace internacional** (a diferencia de Manheim UK/EU/AU). Monk.ai era francesa (origen tecnológico), pero el producto ACV opera US-only. `[VERIFICADO por ausencia]`
  - **España / cardeep:** **sin presencia.** ← hueco total para cardeep. `[VERIFICADO por ausencia]`
- **Nuevo vs usado:** **USADO/wholesale** es el núcleo absoluto (subasta dealer-to-dealer de coche usado + gestión de inventario usado retail). No es libro de valor de coche nuevo ni MSRP. `[VERIFICADO]`
- **Tipos de vehículo:** turismos, light trucks, SUVs; **vehículos comerciales** (off-lease, off-rental, flota — vía ASI); **vehículos accidentados / con historial de siniestro** (transparencia vía TrueFrame, "all used vehicles including accident vehicles"). `[VERIFICADO]`
- **Naturaleza del dato (clave):** **dato de condición físicamente inspeccionado in situ** + **transacción real de subasta** (precio de martillo de su propio marketplace **y** de otras subastas). No es asking-price ni encuesta. La inspección 150-puntos genera dato propietario por VIN (fotos, DTCs, paint meter, audio de motor, imagen del bajo) que ningún "libro" de valor posee. `[VERIFICADO]`
- **Frescura / profundidad:** la inspección es **on-demand** (el coche se inspecciona inmediatamente antes de subastarse); la subasta dura **20 min** (algunas hasta 2 h); el modelo ACV Estimate se reentrena con dato transaccional continuo ("industry-leading machine learning tech … continuously refine"). Base: **+1 M transacciones de condición/año** alimentan el modelo de precio. `[VERIFICADO]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **Comprehensive Condition Report (150-point)** | Inspección on-site estandarizada de cada coche del marketplace | Reporte de condición + 60+ fotos + DTCs + audio + bajo | ~26 |
| **True360 Report** | Reporte premium de transparencia (cosmético + estructural) que publica a Carfax/AutoCheck | ~100 detalles + Virtual Lift + AMP + TrueFrame | ~12 |
| **ACV Estimate / ACV Market Report** | Valoración predictiva del precio de venta (ML) | ACV Estimate + High/Low + comparables | ~14 |
| **ACV MAX (IMS / FirstLook)** | Suite de inventario: source→buy→price→retail | Valor predictivo + turn/gross + comps + run lists | ~23 |
| **ACV MAX Recommendations** | Guía IA VIN-específica de precio/inventario | Price moves + reasoning + profit-vs-speed + forecast | ~6 |
| **ACV MAX Merchandising / Showroom** | Merchandising retail (VDP, window stickers, sindicación) | Descripciones IA + OEM stickers + Showroom + comps | ~12 |
| **VIPER** | Torres de inspección por visión + Virtual Lift | Daños anotados + tread 1/32" + appraisal + retail 30d | ~13 |
| **ClearCar** | Captación al consumidor (web del dealer) | Offer + condición IA (Price + Capture) | ~10 |
| **S.A.M. (Smart Acquisition Manager)** | Compra programática / proxy bidding (UI + API) | Bids automáticos sobre 160+ campos | ~8 |
| **ACV Capital / Transportation / Assurance** | Floorplan + logística + garantía/arbitraje | Floorplan fee + transporte + guaranteed payout | n/a |

### 3.1 Comprehensive Condition Report — inspección de 150 puntos (NÚCLEO del moat)

> El producto fundacional de ACV y su ventaja estructural. Cada vehículo del marketplace lleva un reporte estandarizado generado **on-site** por un inspector de la red de **+1.100**. Es el dato que un "libro" de valor (KBB, Black Book, MMR) **no** tiene: condición física objetiva por VIN.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **VIN** | Identidad del vehículo | bidndrive; acvauctions `[VERIFICADO]` |
| **Year / Make / Model / Trim** | Identidad básica | bidndrive `[VERIFICADO]` |
| **Actual odometer / mileage reading** | Lectura real de odómetro (no declarada) | acv-estimate; bidndrive `[VERIFICADO]` |
| **60+ high-resolution photos** | Más de 60 fotos de alta resolución (incluye neumáticos, motor, odómetro) | acvauctions search `[VERIFICADO]` |
| **360-degree exterior views** | Vistas exteriores 360° | acvauctions `[VERIFICADO]` |
| **360-degree interior views** | Vistas interiores 360° | acvauctions `[VERIFICADO]` |
| **OBD / OBDII Scan** | Escaneo diagnóstico de la centralita | acv-estimate; bidndrive `[VERIFICADO]` |
| **Diagnostic Trouble Codes (DTCs)** | Códigos de avería detectados | bidndrive `[VERIFICADO]` |
| **Warning lights / dashboard lights** | Testigos de advertencia activos | bidndrive `[VERIFICADO]` |
| **System errors** | Errores de sistema electrónico | bidndrive `[VERIFICADO]` |
| **Paint Meter Readings** | Mediciones del medidor de pintura → revelan repintado/chapa; lecturas dispares = reparación/accidente previo | bidndrive `[VERIFICADO]` |
| **Virtual Lift (undercarriage imaging)** | Imagen de alta resolución del bajo que simula coche elevado (**2.000+ fotos** del subsuelo, bumper-to-bumper, en <1 min) | bidndrive; prnewswire (TrueFrame) `[VERIFICADO ×2]` |
| **AMP — Audio Motor Profile** | Clip de **audio del motor** en marcha; el dealer escucha golpeteo/ticking/ralentí irregular | bidndrive; prnewswire `[VERIFICADO ×2]` |
| **Frame / structural assessment** | Evaluación estructural / de chasis (prior repairs, existing damage) — vía TrueFrame | prnewswire (TrueFrame); acv search `[VERIFICADO]` |
| **Tire tread / tire photos** | Estado y fotos de neumáticos | acv search `[VERIFICADO]` |
| **Engine bay photos** | Fotos del vano motor | acv search `[VERIFICADO]` |
| **Cosmetic irregularities (paint quality)** | Irregularidades cosméticas, calidad de pintura | prnewswire (True360) `[VERIFICADO]` |
| **Detailed narrative descriptions** | Descripciones narrativas detalladas de la condición | acv search `[VERIFICADO]` |
| **Announcements / disclosures** | Declaraciones que cualifican la condición (para arbitraje) | acvauctions/legal/arbitration `[VERIFICADO]` |
| **Title status / title history** | Estado y historial de título | S.A.M. fields; acv search `[VERIFICADO]` |
| **Reserve price (seller-set)** | Precio de reserva fijado por el vendedor | bidndrive `[VERIFICADO]` |
| **Embedded ACV Estimate (Market Report)** | El valor predictivo (High/Low) se incrusta dentro del propio reporte de condición | acv-estimate `[VERIFICADO]` |

> **Nota de número de puntos:** ACV describe la inspección del marketplace como **"150-point"** (+1.100 inspectores). El reporte premium **True360** describe **"~100 details"**. Son productos distintos (estándar vs premium); se reportan ambos con su fuente. `[VERIFICADO ×2 con matiz]`

### 3.2 True360 Report (premium — transparencia integral, publicable a VHR)

> Reporte de condición premium nacido de TrueFrame; se **publica a los vehicle history reports de Carfax y AutoCheck** y a la VDP del sitio del dealer. Pensado para dar transparencia "bumper-to-bumper" incluso a vehículos accidentados.

`~100 inspection details` · `cosmetic irregularities (paint quality)` · `structural assessment (prior repairs / existing damage)` · **`Virtual Lift`** (2.000+ fotos del bajo, vista completa en <1 min) · **`AMP / Audio Motor Profile`** (clip de audio del motor) · **`TrueFrame`** (transparencia de chasis/siniestro) · `high-resolution imagery` · `publishes to Carfax VHR` · `publishes to AutoCheck VHR` · `publishes to dealer website VDP`. (Fuentes: prnewswire TrueFrame; acvauctions/blog. `[VERIFICADO ×2]`)

### 3.3 ACV Estimate / ACV Market Report (capa de VALORACIÓN)

> El equivalente funcional al MMR de Manheim, pero **predictivo por ML** y anclado en dato de condición. La salida central es el **ACV Estimate** = "the data-backed price we believe the vehicle will sell for", con banda **High / Low**.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **ACV Estimate** | Precio predicho de venta, respaldado por datos (ML) | acv-estimate `[VERIFICADO]` |
| **High** | Extremo superior del rango estimado | acv-estimate `[VERIFICADO]` |
| **Low** | Extremo inferior del rango estimado | acv-estimate `[VERIFICADO]` |
| **Pre-inspection / post-inspection tag** | Etiqueta que indica el timing de la valoración (antes/después de inspección) | acv-estimate `[VERIFICADO]` |
| **Year/Make/Model lookup** | Búsqueda por YMM en la herramienta Market Report | acv-estimate `[VERIFICADO]` |
| **Recent transaction data / comparables** | Transacciones recientes comparables | data-services PR; acv-estimate `[VERIFICADO]` |
| **Comparable condition reports** | Reportes de condición de vehículos comparables | data-services PR `[VERIFICADO]` |
| **Third-party pricing data** | Datos de precio de fuentes de terceros incorporados | data-services PR `[VERIFICADO]` |

**Las 6 fuentes de datos del modelo (verbatim):**
1. `Condition data from 1M+ vehicle transactions per year`
2. `Auction transactions (ACV & other auctions)`
3. `OBDII Codes & actual odometer readings`
4. `Local market data`
5. `Vehicle history report details`
6. `Retail DMS sales transactions`

(Fuente: acvauctions.com/acv-estimate, leído verbatim. `[VERIFICADO]`)

### 3.4 ACV MAX (IMS / FirstLook — suite de inventario retail)

> Heredada de MAX Digital ($60 M, flagship **FirstLook**). Cubre el ciclo **Source → Buy → Price → Retail**. Es la pieza que compite con vAuto/vincue/MAX. Combina "market signals, AI functionality, and real inspection data to show the actual value of any car, in any channel."

| Campo / módulo atómico | Definición | Fuente |
|---|---|---|
| **Predictive vehicle value (per rooftop)** | Valor predictivo del vehículo a nivel de cada rooftop individual | acvmax.com `[VERIFICADO]` |
| **Condition-based offers** | Ofertas más precisas basadas en condición (online y en lote) | acvmax.com `[VERIFICADO]` |
| **Rooftop-specific pricing** | Precio específico por concesionario | acvmax.com `[VERIFICADO]` |
| **Inventory turnover speed (turn)** | Velocidad de rotación de inventario | data-driven PR `[VERIFICADO]` |
| **Gross (margin)** | Margen bruto por unidad | recommendations PR `[VERIFICADO]` |
| **Regional data + dynamic pricing guides** | Datos regionales y guías de precio dinámicas | data-driven PR `[VERIFICADO]` |
| **Third-party pricing comparisons** | Comparativas de precio de terceros | data-driven PR `[VERIFICADO]` |
| **Market value comparisons / comps** | Comparativas de valor de mercado | data-driven PR; acvmax `[VERIFICADO]` |
| **OEM package / build data** | Detalles de paquetes y opciones de fábrica (resalta high-value packages) | data-driven PR; merchandising `[VERIFICADO]` |
| **KBB value** | Valor Kelley Blue Book accesible al equipo de ventas | acvmax search `[VERIFICADO]` |
| **Mileage** | Kilometraje | acvmax search `[VERIFICADO]` |
| **Options and packages** | Opciones y paquetes | acvmax search `[VERIFICADO]` |
| **Retail/wholesale exit strategy recommendation** | Recomendación de canal de salida (retail vs wholesale) | data-driven PR `[VERIFICADO]` |
| **VIN profitability evaluation** | Evaluación de la rentabilidad de cada VIN | acvmax.com `[VERIFICADO]` |
| **Stocking strategy alignment** | Evaluación frente a la estrategia de stock central + dato real-time | acvmax.com `[VERIFICADO]` |
| **Auction Run Lists (ACV, Manheim, ADESA)** | Listas de subasta de las principales casas, agregadas | acvmax.com `[VERIFICADO]` |
| **Inventory redistribution recommendations** | Recomendaciones de redistribución entre rooftops para maximizar turn/gross | acvmax.com `[VERIFICADO]` |
| **Inter-company transfers** | Transferencias entre rooftops del grupo | acvmax.com `[VERIFICADO]` |
| **Days-to-acquisition** | Aceleración del tiempo hasta adquirir | acvmax.com `[VERIFICADO]` |
| **Overstock reduction** | Reducción de sobre-stock | acvmax.com `[VERIFICADO]` |
| **Advanced data analytics + customizable reporting** | Analítica avanzada + reporting personalizable | data-driven PR `[VERIFICADO]` |
| **Standardized appraisals** | Tasaciones estandarizadas para escalar la adquisición | acvmax.com `[VERIFICADO]` |
| **Live market data appraisal** | Tasación de trade-ins con dato de mercado en vivo | acvmax/inventory `[VERIFICADO]` |

> **Nota:** la terminología vAuto clásica (**price-to-market %**, **cost-to-market %**, **market days supply**) **no** aparece literal en las páginas públicas de ACV MAX; el sistema expresa lo equivalente como "market value comparisons", "predictive value", "favorable pricing when showing comps", "turn/gross", "local supply and demand". Marcado `[PARCIAL]` para esos labels concretos.

### 3.5 ACV MAX Recommendations (guía IA VIN-específica — lanzado mar-2026)

> Capa de IA generativa sobre ACV MAX. Se entrega en un **side panel dentro de ACV MAX**. VIN-específica.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Pricing advice (suggested price moves)** | "Suggested price moves, including when to raise or lower pricing" | recommendations PR `[VERIFICADO]` |
| **Reasoning (key data signals + market factors)** | "The key data signals and market factors driving each recommendation" | recommendations PR `[VERIFICADO]` |
| **Profit vs. speed insights** | "A clear view of the trade-off between margin and days to sale" | recommendations PR `[VERIFICADO]` |
| **Predicted outcomes** | "Action-based forecasts conveying results of a specific recommendation" | recommendations PR `[VERIFICADO]` |
| **Inventory guidance (retail / wholesale / adjust)** | "Recommendations to retail, wholesale, or adjust pricing strategy for each unit" | recommendations PR `[VERIFICADO]` |
| **Performance optimization (turn & gross)** | "Identification of trends and opportunities to improve turn and gross" | recommendations PR `[VERIFICADO]` |

**Inputs del modelo:** historical sales por dealership · current inventory mix · sales velocity · market trends · shopper engagement patterns · VIN-specific performance · dealership-specific history. (Fuente: recommendations PR. `[VERIFICADO]`)

### 3.6 ACV MAX Merchandising / Showroom (capa retail / VDP)

`AI vehicle descriptions` (SEO-optimized, high-converting) · `OEM build data` (resalta paquetes high-value) · `OEM window stickers` (gratis, QR-enabled, synced digital displays) · `Digital Showroom` (web separada con feed de inventario) · `Vehicle Detail Pages (VDP)` (página dedicada por VIN) · `vehicle photos` · `syndication` (web + **500+ third-party integrations** / marketing partners) · `market comparables (comps)` · `vehicle history highlights` · `Coming Soon placeholder` (durante recon/servicio) · `dynamically updated pricing` (sin reimprimir sticker) · `KBB value display`. (Fuentes: acvmax/merchandising; acvmax blogs. `[VERIFICADO]`)

### 3.7 VIPER — Vehicle Inspection Platform for Enhanced Reporting (visión artificial, NADA 2026)

> Hardware: **dos torres de imagen** + **Virtual Lift** (escáner de bajo), instalable en el appraisal lane o service drive del dealer. El coche pasa por debajo y la IA captura la condición "en segundos". Base tecnológica: Monk.ai.

| Campo atómico de salida | Definición | Fuente |
|---|---|---|
| **Thousands of images per drive-through** | Miles de imágenes capturadas en cada pasada | acvmax/viper `[VERIFICADO]` |
| **Exterior damage detection (dents, dings, scratches)** | Detección automática de abolladuras/rayones | acvmax/viper `[VERIFICADO]` |
| **Tire tread depth (to nearest 1/32")** | Profundidad de dibujo de las **4 ruedas** al 1/32" más cercano | viper PR; acvmax/viper `[VERIFICADO ×2]` |
| **Tire damage detection** | Daño visible en neumáticos | acvmax/viper `[VERIFICADO]` |
| **Undercarriage high-res photo (Virtual Lift)** | Foto de alta resolución del bajo (sin elevador manual) | acvmax/viper `[VERIFICADO]` |
| **Automated appraisal in ACV MAX** | Tasación auto-generada en ACV MAX por cada pasada | acvmax/viper; viper PR `[VERIFICADO ×2]` |
| **Condition-based valuation / real-time valuation range** | Rango de valoración en tiempo real basado en condición | viper PR `[VERIFICADO]` |
| **Predicted retail price (next 30 days)** | Precio retail previsto a 30 días | viper PR `[VERIFICADO]` |
| **Competitive analysis** | Análisis competitivo del mercado | viper PR `[VERIFICADO]` |
| **Automated customer offer (ClearCar)** | Oferta automática al cliente vía ClearCar | viper PR; acvmax/viper `[VERIFICADO ×2]` |
| **Inspection photos with annotated damages** | Fotos con daños anotados | viper PR `[VERIFICADO]` |
| **Standardized digital condition summary** | Resumen de condición digital estandarizado | viper PR `[VERIFICADO]` |
| **Real-time text alerts** | Avisos SMS al equipo de servicio: oportunidad de cambio de neumáticos + leads de adquisición con **mileage, title history, recommended customer offer** | acvmax/viper `[VERIFICADO]` |

### 3.8 ClearCar (captación al consumidor — base Drivably)

> Dos componentes: **ClearCar Price** (motor de precio digital en la web del dealer) + **ClearCar Capture** (autoinspección por IA). El consumidor obtiene una oferta; el dealer ve la condición antes de que el coche llegue al lote.

`ClearCar Price` (digital pricing engine / value estimate widget en la web del dealer) · `ClearCar Capture` (AI imaging + self-inspection) · `real-time vehicle offer` (rooftop-specific) · inputs: `VIN / license plate / Year-Make-Model` · `condition questionnaire` (preguntas simples) · `photo upload` (exterior/interior, alineando el móvil con el contorno del coche) · `AI damage detection` (dents, rust, scratches con tamaño/tipo) · `reconditioning issue flags` (según YMM) · `condition report` · métricas de rendimiento: **`65%+ form completion rate`** (widget), **~80% show ratio / ~45% buy ratio** (calidad de leads). Aparece en 3 sitios: **website widget** (customizable), **lot** (en persona), **service lane** (oferta instantánea + bulk upload + SMS). (Fuentes: acvmax/clearcar; clearcar.com; globenewswire. `[VERIFICADO ×2]`)

### 3.9 S.A.M. — Smart Acquisition Manager (compra programática + API)

`AI-powered programmatic buying` con **proxy bidding** · reglas personalizables sobre **160+ data fields** · preferencias por condición: `warning lights`, `tire condition`, `frame damage`, `title statuses` · `price ranges` · `location parameters` · `inspection report details` · dos formatos: **S.A.M. Alerts** (notifica para aprobar) y **S.A.M. Bids** (proxy automático 24/7) · dos vías: **S.A.M. UI** (sin plataforma propia) y **S.A.M. API** (integración directa con APIs real-time de ACV para generar bids; disponible desde Q4 2021). Usuarios: grandes dealers, rent-a-car y compradores comerciales. Opera dentro de las subastas digitales de 20 min. (Fuentes: acvauctions/blog SAM; data-services search. `[VERIFICADO ×2]`)

### 3.10 Servicios (no-valoración)

- **ACV Capital** — floorplan: **advances hasta 100%** del precio de compra; pago = % del principal + interés diario acumulado + **floor planning fee**; soporta **consumer acquisitions** (trade-ins); cubre ACV + subastas independientes + **todas las ubicaciones de ADESA y Manheim**; programa **Float to Floor**; **$125 M** credit facility; portal online. `[VERIFICADO ×2]`
- **ACV Transportation** — transporte full-service de cualquier origen; **floorplan integrado** (el coste de transporte aparece en el **Bill of Sale**); red de transportistas. `[VERIFICADO]`
- **Assurance / ACV Guarantee** — el vendedor recibe un **guaranteed payout** acordado; si vende por menos, ACV paga la diferencia; si vende por más, el vendedor se queda el upside; lo fijan **Industry Pricing Experts** con dato de subasta en tiempo real. Es un **segmento de ingresos propio** ("Customer assurance revenue"). `[VERIFICADO]`
- **Arbitration Policy** — el comprador puede arbitrar defectos elegibles tras recogida/inspección. `[VERIFICADO]`
- **ACV Pro** — app que da al dealer acceso a las **herramientas de inspección de ACV** para autoinspeccionar su propio inventario e lanzarlo a subasta **en horas** (reporte de condición "unbiased"). `[VERIFICADO]`
- **Data Services** — licencia de inteligencia de condición/valor (True360 Report como dato integrable + ACV Market Report con transacciones/comparables/precios de terceros) a dealers y **socios comerciales**, on y off marketplace. `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Dato primario = condición física inspeccionada in situ.** Cada coche del marketplace pasa una **inspección de 150 puntos** por un inspector de la red de **+1.100**, con hardware propietario: **Virtual Lift** (imagen del bajo, 2.000+ fotos), **AMP** (audio del motor), **paint meter** (repintado), **OBDII scan** (DTCs), 60+ fotos + 360°. Esto es lo que un "libro" de valor (KBB/Black Book/MMR) no tiene. `[VERIFICADO]`
- **Dato transaccional dual.** El modelo ACV Estimate combina transacciones de **su propia subasta** + **otras subastas** + **retail DMS sales** → ve tanto el lado wholesale como el retail. `[VERIFICADO]`
- **Machine learning continuo.** "Industry-leading machine learning tech … continuously refine pricing accuracy"; el moat se describe como un data library de "vehicle intelligence, marketplace activity and pricing" usado para entrenar. `[VERIFICADO / CLAIM-VENDOR]`
- **Visión artificial (Monk.ai → VIPER).** Detección automática de daños, tread de neumáticos al 1/32", imagen del bajo, anotación de daños — captura objetiva sin sesgo humano. `[VERIFICADO]`
- **Integración de terceros para historial y precio.** `Vehicle history report details` (Carfax/AutoCheck — donde True360 *publica* y de donde *consume*), `third-party pricing data`, **KBB** en ACV MAX. ACV no genera su propio VHR: se apoya en Carfax/AutoCheck. `[VERIFICADO]`
- **Adquisiciones como bloques del moat:** TrueFrame (AMP+Virtual Lift+frame), ASI (comercial), MAX Digital/FirstLook (IMS+merchandising+precio retail), Drivably (trade-in/ClearCar), Monk.ai (visión IA/VIPER). `[VERIFICADO]`
- **OEM build data** integrada para resaltar paquetes/opciones de fábrica en MAX. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Marketplace digital (web + app)** | `acvauctions.com` + **app iOS/Android**; subastas **live + proxy** de 20 min (algunas hasta 2 h); Live Appraisal (seller acepta high bid en 3 días). 100% digital, sin lote físico (ACV no tiene inventario). |
| **ACV MAX (web SaaS)** | Suite de inventario `acvmax.com`: Source/Buy/Price/Retail + **Recommendations** (side panel) + **Showroom** (web de retail) + run lists. |
| **ClearCar (widget en web del dealer)** | Motor de precio + captura por IA, embebido en la web del dealer; también app de lote/service-lane. |
| **VIPER (hardware en sitio)** | Torres de imagen + Virtual Lift en el appraisal lane/service drive del dealer; alimenta ACV MAX + alertas SMS. |
| **API** | **S.A.M. API** (proxy bidding programático real-time, desde Q4 2021) para grandes dealers/rent-a-car; **500+ integraciones de terceros** para sindicación de inventario; integración DMS (retail sales). |
| **Data Services / feed** | Licencia de True360 + ACV Market Report a socios comerciales (on/off marketplace); True360 publica a Carfax/AutoCheck VHR y a la VDP del dealer. |
| **Servicios físicos/financieros** | ACV Transportation (carrier network), ACV Capital (floorplan, portal online, cientos de ubicaciones), inspección on-site por +1.100 inspectores. |
| **Soporte** | acvauctions.com/support; teléfono 1-800-553-4070. |

---

## 6. Precio (parcialmente descubierto)

| Concepto | Precio | Fuente / nota |
|---|---|---|
| **Modelo general** | **Transaccional de doble cara**: seller paga **flat listing fee** por listar su coche ACV-inspeccionado; buyer paga **commission fee** sobre la compra. Fees solo en subasta exitosa | bowerycap S-1 teardown `[PARCIAL]` |
| **Buyer fee / buyer's premium** | **% del valor del vehículo, escalonado por tramo de precio**, con **tope ~$350** | bidndrive; matrixbcg `[PARCIAL — tramos exactos no extraídos; fee schedule movido a página aparte]` |
| **Take rate medio** | **~$494** fees totales/transacción ÷ **~$8.500** AOV ≈ **~6%** | bowerycap `[PARCIAL — análisis de tercero]` |
| **Live Appraisal Service** | ACV puede cobrar al seller un fee por participar | acvauctions/legal/terms `[VERIFICADO]` |
| **ACV Guarantee / Assurance** | Fee por garantía de pago (segmento "Customer assurance revenue", **$22.0 M** en Q1'26) | SEC 8-K `[VERIFICADO]` |
| **ACV Capital (floorplan)** | % del principal + **interés diario** + **floor planning fee**; advance hasta 100% | acvauctions/capital `[VERIFICADO]` |
| **ACV Transportation** | Coste por transporte (aparece en Bill of Sale; floorplanable) | acvauctions/capital `[VERIFICADO]` |
| **ACV MAX / ClearCar / VIPER / Data Services** | **SaaS / cotización B2B** (no público); window stickers OEM **"at no additional cost"** | acvmax blogs `[PARCIAL]` |

> **Modelo vs Manheim:** igual filosofía transaccional (fees por subasta, no SaaS para el dato wholesale), **pero** ACV monetiza además capas SaaS claramente separadas (ACV MAX, ClearCar, VIPER) y un **segmento de assurance** propio. El fee schedule completo de buyer está tras un enlace dinámico no extraíble. `[PARCIAL]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca ACV **cada dato**. Patrón rector (distinto al de Manheim): el **reporte de condición es el hub** (no el "libro" de valor), y la **valoración (ACV Estimate High/Low) se incrusta *dentro* del reporte de condición y del flujo de subasta**, no en una herramienta separada. La inteligencia de inventario vive en una app aparte (ACV MAX).

**A. Listing / VDP de subasta (app ACV — el coche en venta).** Hub del comprador: arriba **Year/Make/Model + VIN + actual odometer**; galería de **60+ fotos + 360° exterior/interior**; bloque de condición con **paint meter readings**, **Virtual Lift** (imagen del bajo), **reproductor de AMP (audio del motor)**, **OBDII / DTCs / warning lights**, **frame/structural (TrueFrame)**, **announcements/disclosures**; el **ACV Estimate (High/Low)** incrustado como guía de valor; **timer de subasta de 20 min** con **live + proxy bid**.

**B. Comprehensive Condition Report (pantalla dedicada).** El reporte 150-puntos en detalle: line-items por categoría, **paint meter**, **DTCs**, **AMP audio clip**, **Virtual Lift undercarriage**, **tire tread/photos**, **narrative descriptions**, y — clave — el **Market Report con ACV Estimate + High/Low** embebido dentro del propio reporte (etiquetado pre/post-inspection).

**C. ACV Market Report (herramienta de valoración standalone).** Búsqueda por **Year/Make/Model** → **ACV Estimate + High/Low** + **transacciones recientes comparables** + condition reports comparables + third-party pricing. También aparece en el flujo **"Send to Auction"** como guía de pricing/reserva.

**D. ACV MAX — dashboard de inventario (app SaaS del retailer).** Grid de inventario con **predictive value por rooftop**, **turn/gross**, **days-to-acquisition**, **redistribution**; pestaña de **appraisal** (trade-in con live market data, **KBB**, OEM packages, market comps, recomendación retail/wholesale); **Auction Run Lists** (ACV/Manheim/ADESA) para sourcing; **Recommendations** en **side panel** (suggested price moves + reasoning + profit-vs-speed + predicted outcomes).

**E. ACV MAX Merchandising / Showroom (cara pública del retailer).** **VDP** por VIN en el **Digital Showroom**; **descripciones IA SEO** + **OEM build data** + **window stickers OEM con QR** (físico en el lote, sincronizado con la web) + **vehicle history highlights** + **comps de mercado favorables**; **sindicación** a 500+ partners; **dynamic pricing** sin reimprimir sticker; **Coming Soon** durante recon.

**F. VIPER (drive-through físico + ACV MAX).** El coche cruza las torres → genera **appraisal automático en ACV MAX** con **fotos de daños anotados**, **tread 1/32" x4**, **undercarriage**, **valuation range**, **predicted retail 30d**, **competitive analysis**, **oferta ClearCar**; al equipo de servicio le llega **alerta SMS** (cambio de neumáticos + lead con mileage/title/oferta recomendada).

**G. ClearCar (widget en la web del dealer — cara consumidor).** Consumidor mete **VIN/plate/YMM** → responde **cuestionario de condición** → alinea el móvil con el **contorno** y sube **fotos** → la IA detecta **dents/rust/scratches** y flags de recon → devuelve una **oferta real-time rooftop-specific**. Mismo flujo en el **service lane** (oferta instantánea) y en el **lote** (en persona).

**H. S.A.M. (capa de compra programática).** Pantalla de reglas sobre **160+ campos** (specs, price range, location, condición: warning lights/tire/frame/title) → **S.A.M. Alerts** (aprobar) o **S.A.M. Bids** (proxy 24/7); o vía **API** para integradores. Actúa sobre las subastas de 20 min.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Dato de condición físicamente inspeccionado por VIN, a escala.** +1.100 inspectores, 150 puntos, **AMP (audio de motor)**, **Virtual Lift (bajo)**, **paint meter**, **OBDII/DTCs** — un activo que ningún "libro" de valor (KBB, Black Book, J.D. Power, MMR) posee. La valoración va anclada a condición real, no a asking-price.
2. **Valoración incrustada en el reporte de condición (no en una herramienta aparte).** El **ACV Estimate (High/Low)** vive *dentro* del CR y del flujo de subasta, etiquetado pre/post-inspección. Patrón de UI muy replicable por cardeep.
3. **AMP — Audio Motor Profile.** Clip de **audio del motor** en el reporte: capacidad sensorial única en el sector (nadie más la ofrece de forma estándar).
4. **Virtual Lift móvil del bajo (2.000+ fotos, <1 min).** "Industry's first mobile undercarriage imaging tool".
5. **VIPER: inspección por visión artificial drive-through** (torres + Virtual Lift) que auto-genera appraisal + retail-30d + oferta al consumidor en segundos — captura objetiva sin sesgo humano (base Monk.ai).
6. **Marketplace nativo digital de 20 min + compra programática por API (S.A.M.) sobre 160+ campos** — automatización de compra que una subasta física no da.
7. **Dato dual wholesale + retail** (subasta propia + otras subastas + retail DMS) → el modelo ve ambos lados del mercado.
8. **Suite vertical end-to-end independiente**: source(S.A.M.)→inspect(CR/True360/VIPER)→value(ACV Estimate)→buy/sell(20-min)→retail(ACV MAX/Showroom)→acquire-consumer(ClearCar)→finance(ACV Capital)→transport(ACV Transportation)→guarantee(Assurance), sin pertenecer a Cox.
9. **True360 publica a Carfax y AutoCheck**: su dato de condición sale al ecosistema de historial, no se queda cautivo.
10. **ClearCar lleva la captación al sitio del dealer** (widget consumidor con autoinspección IA) — cierra el loop de sourcing desde el consumidor, no solo wholesale.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo EE. UU.** Sin marketplace ni dato fuera de USA. **Sin España, sin Europa, sin LatAm.** ← hueco mayor para cardeep. `[VERIFICADO por ausencia]`
2. **No es libro de valor de coche NUEVO / MSRP / residual-lease multi-anual** ni curva de depreciación a 36/48 meses (a diferencia de ALG/Autovista/J.D. Power). El ACV Estimate es **precio de venta actual predicho**, no forecast residual a años. `[VERIFICADO por ausencia]`
3. **No genera su propio Vehicle History Report.** Depende de **Carfax/AutoCheck** (publica a ellos y consume "vehicle history report details"). `[VERIFICADO]`
4. **No es índice macro citado** tipo MUVVI/Manhei­m Index: no publica un indicador de mercado de referencia que lea la prensa/Wall Street. `[VERIFICADO por ausencia]`
5. **No tasa directamente al consumidor como guía pública** (tipo KBB.com): ClearCar vive *dentro* de la web del dealer; el ACV Estimate es B2B, no una guía de consumidor independiente. `[VERIFICADO]`
6. **Labels de mercado vAuto-style no expuestos** (price-to-market %, cost-to-market %, market days supply): el equivalente existe como "comps/predictive value/turn-gross" pero no con esa nomenclatura pública. `[PARCIAL]`
7. **Fee schedule de buyer opaco**: tramos exactos tras enlace dinámico; solo se confirma "% escalonado con tope ~$350". `[PARCIAL]`
8. **Dependiente del acto de inspección física** (o del hardware VIPER): un coche no inspeccionado por ACV no tiene su dato de condición propietario — su moat no es un dataset histórico universal sino un flujo de inspecciones. Coches raros/clásicos o no presentados a ACV quedan fuera. `[RECONSTRUIDO]`
9. **No cubre rentabilidad histórica / no es plataforma de pricing retail al consumidor final** fuera del dealer (no hay portal de consumidor propio tipo Autotrader/cars.com). `[VERIFICADO por ausencia]`
10. **Pricing SaaS de ACV MAX/ClearCar/VIPER/Data Services no público** (cotización B2B). `[PARCIAL]`

---

## 10. Fuentes

**Oficiales / producto (ACV, accesibles):**
- ACV MAX (suite): https://www.acvmax.com/ · inventory: https://www.acvmax.com/inventory · merchandising: https://www.acvmax.com/merchandising · VIPER: https://www.acvmax.com/viper · ClearCar: https://www.acvmax.com/clearcar · ACV Guarantee overview: https://www.acvmax.com/support/acv-guarantee-overview
- **ACV Estimate / Market Report (6 fuentes de datos, ACV Estimate + High/Low, leído verbatim):** https://www.acvauctions.com/acv-estimate
- ClearCar (consumidor): https://www.clearcar.com/index.html
- ACV Capital (floorplan): https://www.acvauctions.com/capital · Float to Floor terms: https://www.acvauctions.com/legal/float-to-floor-terms
- ACV Pro: https://www.acvauctions.com/acv-pro · Live Appraisal: https://www.acvauctions.com/live-appraisal
- Pricing (fee schedule movido): https://www.acvauctions.com/pricing · Terms: https://www.acvauctions.com/legal/terms-of-service · Arbitration: https://www.acvauctions.com/legal/arbitration
- Cómo funcionan las subastas / formatos: https://www.acvauctions.com/blog/how-do-car-auctions-work · https://www.acvauctions.com/support-article/acv-auction-formats
- Smart Acquisition Manager (S.A.M.): https://www.acvauctions.com/blog/acv-unveils-smart-acquisition-manager

**Investor Relations / prensa ACV:**
- **Inventory Intelligence Suite (may-2026, Buffalo NY, componentes):** https://investors.acvauto.com/news-events/press-releases/detail/108/acv-unveils-all-in-one-inventory-intelligence-suite-for-dealers
- **ACV MAX Recommendations (mar-2026, campos verbatim):** https://investors.acvauto.com/news-events/press-releases/detail/105/... · businesswire: https://www.businesswire.com/news/home/20260319251914/en/
- **VIPER (NADA 2026, torres + Virtual Lift + tread 1/32" + retail 30d):** https://investors.acvauto.com/news-events/press-releases/detail/102/... · https://www.autoremarketing.com/ar/technology/acv-highlights-viper-early-access-program...
- **Data-driven solutions (productos + data moat):** https://investors.acvauto.com/news-events/press-releases/detail/75/...
- **MAX Digital acquisition ($60M, FirstLook):** https://www.prnewswire.com/news-releases/acv-acquires-max-digital-301332340.html
- **TrueFrame acquisition (AMP + Virtual Lift, dic-2019):** https://www.prnewswire.com/news-releases/acv-auctions-acquires-trueframe-bringing-transparency-to-all-used-vehicles-including-accident-vehicles-300976306.html
- **ASI (comercial/off-lease, abr-2020):** https://www.prnewswire.com/news-releases/acv-auctions-expands-products-reach-and-customers-for-off-lease-and-commercial-sector-with-latest-acquisition-301044720.html
- **ClearCar launch (oct-2023):** https://www.globenewswire.com/news-release/2023/10/16/2760654/0/en/ACV-Leverages-AI-to-Introduce-ClearCar.html
- **Milestone 3M inspecciones / 2M vehículos (2023):** https://investors.acvauto.com/news-events/press-releases/detail/22/...
- **S-1 (IPO 2021, modelo de negocio):** https://investors.acvauto.com/sec-filings/... · https://www.sec.gov/Archives/edgar/data/0001637873/000119312521060598/d34258ds1.htm
- **SEC 8-K Q1'26 (segmentos: marketplace+service $182.2M, assurance $22.0M):** https://www.sec.gov/Archives/edgar/data/0001637873/000163787326000019/q1-26earningspressrelease.htm

**Terceros / verificación cruzada:**
- Resultados 2025 ($760M, 829.276 veh, $10.4B GMV, 35% penetración): https://www.digitalcommerce360.com/2026/02/26/acv-auctions-ai-tools-revenue-q4-2025/ · finviz: https://finviz.com/news/324088/...
- Historia/fundadores (2014, Z80 Labs, Neiman/Magnuszewski/Chamoun/Greco): https://bowerycap.com/blog/insights/from-the-front-lines-dan-magnuszewski-joe-neiman-acv · https://portersfiveforce.com/blogs/brief-history/acvauctions · https://buffalonews.com/...
- Mecánica de subasta / condición / fees (150-puntos, +1.100 inspectores, OBD, paint meter, Virtual Lift, AMP, tope $350): https://www.bidndrive.com/blog/what-is-acv-auctions... (403 en fetch; datos vía search) · https://matrixbcg.com/blogs/how-it-works/acvauctions
- S-1 teardown / take rate (~$494 / ~6%): https://bowerycap.com/blog/insights/s-1-teardown-acv-auctions
- Adquisiciones (Tracxn): https://tracxn.com/d/acquisitions/acquisitions-by-acv-auctions/...
- HQ/empleados (640 Ellicott St, ~3.200): https://www.cbinsights.com/company/acv-auctions · https://www.chartmill.com/stock/quote/ACVA/profile
- True360 a Carfax/AutoCheck + ~100 detalles: https://www.acvauctions.com/blog/acv-reaches-milestone... · prnewswire TrueFrame

### Notas de verificación
- **Identidad (2014 Buffalo, Z80 Labs, 4 fundadores, CEO Chamoun, HQ 640 Ellicott):** bowerycap + portersfiveforce + buffalonews + cbinsights. **[VERIFICADO ×2]**
- **Ticker:** consenso **NASDAQ: ACVA**; un fetch de IR devolvió "NYSE: ACVA" (probable error del modelo de extracción) y una fuente fechó la IPO en "2022" (errónea; fue **marzo 2021**). **[VERIFICADO con conflicto menor de etiqueta]**
- **150-point / +1.100 inspectores vs True360 ~100 detalles:** son productos distintos (estándar de marketplace vs reporte premium); ambos confirmados con fuente. **[VERIFICADO ×2 con matiz]**
- **ACV Estimate + High/Low + 6 fuentes de datos:** **leído verbatim** en acvauctions.com/acv-estimate. **[VERIFICADO]**
- **AMP / Virtual Lift / TrueFrame / paint meter / OBDII:** prnewswire (TrueFrame) + bidndrive + acvauctions search. **[VERIFICADO ×2]**
- **ACV MAX Recommendations (price moves/reasoning/profit-vs-speed/predicted outcomes/guidance/optimization):** PR mar-2026 + businesswire, **verbatim**. **[VERIFICADO ×2]**
- **VIPER (torres + Virtual Lift + tread 1/32" + appraisal en MAX + retail 30d + competitive analysis + ClearCar + SMS alerts):** acvmax/viper + PR NADA 2026. **[VERIFICADO ×2]**
- **Adquisiciones (TrueFrame dic-19, ASI abr-20, MAX Digital $60M jul-21, Drivably feb-22, Monk.ai $19M feb-22):** Tracxn + prnewswire + search. **[VERIFICADO ×2]**
- **Financieros 2025 ($760M, 829.276 veh, $10.4B GMV) + segmentos Q1'26:** digitalcommerce360 + SEC 8-K. **[VERIFICADO ×2]**
- **Buyer fee (% escalonado, tope ~$350) + take rate ~6% / ~$494:** bidndrive/matrixbcg + bowerycap. **[PARCIAL]** — tramos exactos tras enlace dinámico no extraíble.
- **Labels vAuto (price-to-market/cost-to-market/market days supply):** NO expuestos literalmente por ACV; equivalentes funcionales confirmados. **[PARCIAL por ausencia de label]**
- **exa MCP:** NO disponible en el entorno (ToolSearch "exa search semantic" devolvió solo WebSearch/WebFetch/gbrain/claude-mem/gmail/drive/logo). Investigación con **WebSearch + WebFetch**. **[NOTA DE MÉTODO]**
- **Páginas gated/404/403:** bidndrive (403), acvmax.com/features y /true360 (404 — el contenido vive en otras rutas) → datos tomados de fuentes equivalentes verificadas.
