# Cox Automotive — Auditoría atómica

> Slug: `cox-automotive` · Subdominio cardeep: **wholesale-intelligence** · Región: **Global** (EE. UU. núcleo + Europa/UK + Australia/NZ + Canadá)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[NO-VERIFICADO]` / `[CLAIM-VENDOR]` donde no se confirmó de forma independiente, `[RECONSTRUIDO]` donde compongo el dato de varias páginas sin que el vendedor lo liste literalmente.
> **Alcance de esta ficha:** Cox Automotive es un ecosistema gigante. Esta auditoría se centra en la **espina de WHOLESALE INTELLIGENCE** — **Manheim** (el mayor marketplace mayorista del mundo) y los **productos de dato/inteligencia** que lo rodean: **Manheim Market Report (MMR)**, **Manheim Used Vehicle Value Index (MUVVI)** + índices satélite, **MMR Valuations/Forecast API**, **VI Data**, **AutoGrade / Condition Report**, **Cox Automotive Intelligence (capa IA)**, **RMS Automotive**, **VPM** (carteras), **eVA** (UK) y los **índices de mercado** (Dealer Sentiment Index, Forecast, Affordability).
> **Hermanas con ficha propia** (NO se duplican aquí, solo se referencian): [`vauto.md`](vauto.md) (gestión de inventario / Live Market View) y [`kelley-blue-book.md`](kelley-blue-book.md) (valoración al consumidor / ICO).
> Sitios/marcas: `coxautoinc.com` (corporativo US), `coxautoinc.eu` (Europa), `site.manheim.com` + `manheim.com` + `mmr.manheim.com` (Manheim US), `developer.manheim.com` (API), `manheim.co.uk` / `evavaluations.com` (UK), `manheim.com.au` / `manheim.co.nz` (ANZ).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre | **Cox Automotive Inc.** | coxautoinc.com `[VERIFICADO]` |
| Owner / grupo | **Cox Enterprises, Inc.** (privada, familiar, Atlanta) — una de las ~15 mayores privadas de EE. UU.; ~**$21 B** ingresos grupo, ~55.000 empleados grupo | Wikipedia Cox Enterprises; coxautoinc.com/about-us `[VERIFICADO ×2]` |
| Cox Enterprises fundada | **1898** por el gobernador de Ohio **James M. Cox** | Wikipedia `[VERIFICADO]` |
| Cox Automotive formada | **2014** — Cox Enterprises consolidó sus negocios de automoción (ya incluían **vAuto** y **NextGear Capital**) bajo el nombre Cox Automotive | coxautoinc.com/insights (formación); Wikipedia `[VERIFICADO ×2]` |
| HQ | **Atlanta, Georgia, EE. UU.** | coxautoinc.com/about-us; Wikipedia `[VERIFICADO]` |
| Escala Cox Automotive | **~29.000–33.000 empleados**, **200+ ubicaciones**, **cinco continentes** | coxautoinc; ZoomInfo/Owler (agregadores) `[PARCIAL — rango entre fuentes]` |
| Clientes | **40.000+ concesionarios** + la mayoría de los grandes **OEM** + **lenders, flotas, remarketers, compradores** | coxautoinc.com/about-us `[VERIFICADO]` |
| Misión declarada | *"Transform the way the world buys, sells, owns and uses cars"* | coxautoinc.com/about-us `[VERIFICADO]` |
| Otras divisiones de Cox Enterprises | **Cox Communications** (cable/telco) y **Cox Media Group** (broadcast) | Wikipedia `[VERIFICADO]` |

**Grupo operativo clave para este subdominio — Inventory Solutions Group** (presidenta **Grace Huang**): agrupa **Manheim Physical Services & Auctions**, **Digital Marketplace**, **Logistics Solutions (Central Dispatch)** y **Cox Automotive International**. **Este grupo ES la maquinaria de wholesale intelligence.** `[VERIFICADO — coxautoinc/insights bio Grace Huang + growjo]`

**Cartera de marcas Cox Automotive (13+ marcas principales):**

| Marca | Función | ¿Wholesale-intel? |
|---|---|---|
| **Manheim®** | Subastas mayoristas físicas+digitales (el mayor marketplace wholesale del mundo) | **NÚCLEO** |
| **Kelley Blue Book® (KBB)** | Valoración al consumidor + Instant Cash Offer | satélite (ficha propia) |
| **Autotrader®** | Marketplace retail / media | satélite |
| **vAuto®** | Gestión de inventario dealer (Live Market View) | satélite (ficha propia) |
| **Dealertrack®** | DMS + F&I + registro/título | financiera |
| **NextGear Capital™** | Floor-plan / financiación de inventario | financiera |
| **CentralDispatch®** | Marketplace de transporte de vehículos | logística |
| **FleetNet America®** | Mantenimiento/logística de flota | flota |
| **Dealer.com** | Marketing digital / web del dealer | media |
| **VinSolutions** | CRM | retail |
| **Xtime** | Tecnología de servicio/taller | fixed-ops |
| **Fullpath** | Automatización IA de ventas/marketing (CDXP) | retail |
| **EV Battery Solutions** | Ciclo de vida de baterías EV | EV |
| **RMS Automotive** | Optimización de cartera wholesale (IA) | **NÚCLEO** |

(Fuentes: coxautoinc.com home + about; WebSearch marcas. `[VERIFICADO]`)

**Marcas internacionales adicionales (Cox Automotive Europe / ANZ):** **Dealer Auction** (JV con Auto Trader UK, 2018/2019), **Movex** (transporte UK, adquirida 2015), **Modix** (retail digital DE/EU), **eVA Valuations & Appraisals** (valoración UK), **Manheim Inspection Services**, **Manheim Vehicle Services**. (Fuentes: coxautoinc.eu; manheim.co.uk. `[VERIFICADO]`)

---

## 2. Cobertura

- **Geografía:**
  - **EE. UU.** = núcleo absoluto. Manheim = **~111 ubicaciones** físicas/digitales/móviles, **650+ digital lanes**, **80.000+ concesionarios** servidos. `[VERIFICADO — agregación WebSearch + site.manheim]`
  - **Europa / Reino Unido** = presencia mayor vía **Cox Automotive Europe**: **Manheim opera 13 centros de subasta en Europa** y vende **300.000+ vehículos/año**; **Dealer Auction**, **Movex**, **Modix**, **NextGear Capital UK**, **eVA**. ← **a diferencia de vAuto/KBB, Cox SÍ tiene huella europea fuerte por el lado wholesale.** `[VERIFICADO ×2: coxautoinc.eu + manheim.co.uk]`
  - **Australia / Nueva Zelanda** = `manheim.com.au`, `manheim.co.nz` (subastas + grading). `[VERIFICADO]`
  - **Canadá** = Manheim Canada. `[PARCIAL]`
- **Wholesale vs retail:** primario **WHOLESALE** (subasta/trade dealer-a-dealer y comercial); también **retail** (Autotrader/KBB) y **nuevo+usado** a nivel grupo. `[VERIFICADO]`
- **Tipos de vehículo:** turismos + light trucks/SUV + **LCV** (eVA UK = primera plataforma de tasación LCV del mercado). El **índice MUVVI excluye explícitamente camiones pesados y motocicletas** (20 clases J.D. Power). `[VERIFICADO]`
- **Profundidad / frescura del dato wholesale (EE. UU.):**
  - **~8 M de vehículos ofrecidos a la venta/año**; transacciones por **~$80 B** de valor. `[PARCIAL — cifra de prensa/agregador]`
  - **5 M+ transacciones usadas/año** alimentan el índice; **MMR recalculado cada noche** sobre ventana de **13 meses**. `[VERIFICADO]`
  - **70 M+ búsquedas MMR/año** (gold-standard de pricing wholesale). `[VERIFICADO — site.manheim large-portfolio]`
  - **AutoGrade** = estándar de condición **NAAA** disponible a todas las subastas miembro NAAA. `[VERIFICADO]`
- **Frescura de mercado (ej. Q1 2026):** sales conversion **68,2%**; **~37.000 EV** mayoristas vendidos (récord). `[VERIFICADO — coxautoinc MUVVI Q1 2026]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos (subdominio wholesale-intelligence)

| Producto | Qué es | Salida principal |
|---|---|---|
| **Manheim Market Report (MMR)** | El **benchmark de precio mayorista** estándar del sector; "living algorithm" recalculado cada noche | Valor wholesale (above/avg/below) + retail estimado + MMR Range + ajustes + histórico + forecast |
| **MMR Valuations API** | MMR servido como API REST (VIN o YMMT, single/batch, fecha histórica) | JSON con todos los campos de valor + ajustes + intervalos |
| **MMR Forecast API** | Valor MMR proyectado hasta **106 semanas** adelante | adjustedForecastPricing por fecha futura |
| **Manheim Used Vehicle Value Index (MUVVI)** | Índice macro de precios mayoristas ajustado por mix/km/estacionalidad (base ene-1997=100) | Índice mensual + sub-índices (3-yr-old, EV vs non-EV, segmentos) |
| **VI Data (Vehicle Information)** | Capa de dato de inspección/condición por VIN | DTC/OBDII, imágenes 360, daños, build, AutoGrade, salud de batería EV |
| **AutoGrade® / Condition Report** | Grado de condición 1.0–5.0 estandarizado | Score + disclosures cosmético/mecánico/estructural |
| **Cox Automotive Intelligence** | Capa IA transversal sobre Manheim | Recomendaciones personalizadas de inventario + MMR potenciado IA |
| **RMS Automotive** | Optimización de cartera wholesale (remarketers/flotas/lessors) | Precio suelo VIN-specific, ubicación óptima, recon óptimo |
| **VPM (Vehicle Portfolio Management)** | Gestión de ciclo de vida para grandes carteras | Tracking en servicio + grounding + remarketing + settlement |
| **DealShield** | Garantía de recompra post-subasta | Devolución 21 días / 500 millas |
| **Índices de mercado Cox** | Dealer Sentiment Index, Forecast, Affordability Index, Car Buyer Journey | Métricas de sentimiento/demanda/asequibilidad |
| **eVA Valuations & Appraisals (UK)** | Tasación omnicanal coche+LCV | Trade + retail + part-exchange value |

---

### 3.1 Manheim Market Report (MMR) — campos atómicos (núcleo del subdominio)

> El MMR es el **valor de mercado mayorista** de referencia. Modelo estadístico que **recalcula cada noche** sobre **millones de transacciones de los últimos 13 meses**, excluyendo outliers. Base MMR = precio mayorista medio + odómetro + grado de condición + build quality de transacciones recientes.

| Campo (verbatim donde aplica) | Definición atómica | Fuente |
|---|---|---|
| **Base MMR** | Precio mayorista medio de transacciones recientes para ese YMMT (excluye outliers). | site.manheim MMR Help; valuation `[VERIFICADO ×2]` |
| **Wholesale: Above / Average / Below** | Tres tiers de precio mayorista según condición (por encima/en/por debajo de la media). API: `wholesale.above`, `wholesale.average`, `wholesale.below`. | developer.manheim valuations; MMR Help `[VERIFICADO ×2]` |
| **Estimated Retail: Above / Average / Below** | Rango retail estimado a partir de precios retail **anunciados reales** de Cox Automotive. API: `retail.above/average/below`. | valuation; developer.manheim `[VERIFICADO]` |
| **MMR Range (confidence interval)** | Intervalo de confianza: probabilidad de que el **70%** de ventas con atributos similares caigan dentro del rango. API: `confidenceInterval.priceRange.adjustedHigh / adjustedLow`. | MMR Help; developer.manheim `[VERIFICADO ×2]` |
| **Adjusted Pricing (wholesale & retail)** | Valor ajustado al VIN concreto. API: `adjustedPricing.wholesale.{average/above/below}`, `adjustedPricing.retail.{…}`. | developer.manheim `[VERIFICADO]` |
| **adjustedBy: Odometer** | Ajuste por odómetro/kilometraje (depreciación por milla). | developer.manheim; MMR Help `[VERIFICADO ×2]` |
| **adjustedBy: Region** | Ajuste geográfico (regiones US: **SE, NE, MW, SW, WC**; defecto NA). | developer.manheim forecast `[VERIFICADO]` |
| **adjustedBy: Grade** | Ajuste por **AutoGrade** (grade "30" = 3.0 en la API). | developer.manheim `[VERIFICADO]` |
| **adjustedBy: Color** | Ajuste por color exterior. | developer.manheim; MMR Help `[VERIFICADO ×2]` |
| **adjustedBy: EVBH** | Ajuste por **Electric Vehicle Battery Health** (salud de batería). | developer.manheim; MMR Help `[VERIFICADO]` |
| **adjustedBy: buildOptions** | Ajuste por opciones/paquetes instalados de fábrica. | developer.manheim; valuation `[VERIFICADO ×2]` |
| **averageOdometer / odometerUnits** | Odómetro medio del sample + unidades. | developer.manheim `[VERIFICADO]` |
| **averageGrade** | AutoGrade medio del sample. | developer.manheim `[VERIFICADO]` |
| **averageEVBH** | Salud de batería media (EV). | developer.manheim `[VERIFICADO]` |
| **EVBH score (0–100)** | Salud de batería **VIN-específica**: capacidad restante en escala 0–100. | MMR Help `[VERIFICADO]` |
| **sampleSize** | Nº de transacciones en la muestra. | developer.manheim `[VERIFICADO]` |
| **Small Sample Size icon** | Indicador de muestra insuficiente para cálculo fiable. | MMR Help; best-practices `[VERIFICADO ×2]` |
| **Outlier flag (asterisco / "not in sample")** | Marca de transacción outlier excluida del cálculo; exclusiones explícitas incluyen **ventas canadienses previas** y **vehículos con <50 millas**. | MMR Help (re-verif. viva 2026-06-30) `[VERIFICADO ×2]` |
| **bestMatch** | Indicador de mejor coincidencia de configuración. | developer.manheim `[VERIFICADO]` |
| **historicalAverages: last30Days** | Media (precio + odómetro) últimos 30 días. | developer.manheim `[VERIFICADO]` |
| **historicalAverages: lastMonth / lastTwoMonths / lastSixMonths / lastYear** | Valores históricos a 1 / 2 / 6 / 12 meses (precio + odómetro). | developer.manheim; caredge `[VERIFICADO ×2]` |
| **forecast.nextMonth.wholesale / .retail** | Proyección a 1 mes (wholesale y retail). | developer.manheim `[VERIFICADO]` |
| **forecast.nextYear.wholesale / .retail** | Proyección a 1 año (wholesale y retail). | developer.manheim `[VERIFICADO]` |
| **Wholesale / Retail Spread** | Diferencial wholesale-retail (mostrado por integradores tipo Carbly). | getcarbly `[VERIFICADO]` |
| **Number of Auctions Included** | Nº de subastas incluidas en el cálculo. | getcarbly `[VERIFICADO]` |
| **Transactions table** | Tabla de transacciones de subasta recientes (~30 días, hasta ~100): **sale price, mileage, condition, fecha, ubicación**. | MMR Help; best-practices `[VERIFICADO]` |
| **requestedDate / returnedDate / currency / href / count** | Metadatos de la respuesta API. | developer.manheim `[VERIFICADO]` |

**Inputs de búsqueda/decodificación MMR:** `VIN` · `YEAR` · `MAKE` · `MODEL` · `TRIM` · `SUBSERIES` · `TRANSMISSION` · `odometer` · `region` / `zipCode` / `geoLocation (lat/long)` · `color` · `grade` · `evbh` · `date` (histórica hasta 01-11-2018) · `include` · `extendedCoverage` · `excludeBuild` · `orgId` · `orderBy` · `country` (parámetro internacional). (Fuente: developer.manheim valuations — re-verificado contra doc viva 2026-06-30. `[VERIFICADO ×2]`)

### 3.2 MMR Forecast API — campos atómicos

| Campo (verbatim) | Definición | Fuente |
|---|---|---|
| **forecastedPricing** | Valor forecast medio **sin ajustar**. | developer.manheim forecasts `[VERIFICADO]` |
| **adjustedForecastPricing.wholesale** | Valor forecast **ajustado** (métrica principal). | developer.manheim `[VERIFICADO]` |
| **forecastDate / edition** | Fecha (lunes) de la edición de forecast. | developer.manheim `[VERIFICADO]` |
| **forecastedAverageOdometer / odometerUnits** | Odómetro esperado a la fecha forecast. | developer.manheim `[VERIFICADO]` |
| **forecastedAverageGrade** | AutoGrade medio proyectado. | developer.manheim `[VERIFICADO]` |
| **Horizonte forecast** | Hasta **106 semanas** en el futuro, basado en patrones de depreciación históricos (13 meses, refresco semanal). | developer.manheim `[VERIFICADO]` |
| Inputs | `VIN`, `date` (futura, YYYY-MM-DD), `odometer`, `region` (SE/NE/MW/SW/WC), `zipCode`, `color`, `grade`, `orgId`, `geoLocation`, `SUBSERIES`. | developer.manheim `[VERIFICADO]` |

### 3.3 Manheim Used Vehicle Value Index (MUVVI) + índices satélite

| Campo / parámetro | Definición atómica | Fuente |
|---|---|---|
| **Índice MUVVI** | Medida de precios mayoristas **ajustada por mix/km/estacionalidad**, independiente del cambio de características de la flota vendida. | site.manheim consulting; Moody's `[VERIFICADO ×2]` |
| **Base / referencia** | **Enero 1997 = 100** (rebase ene-2023 desde la base previa ene-1995=100; series desde ene-2015 idénticas). | WebSearch MUVVI rebase `[VERIFICADO]` |
| **Universo** | Todas las ventas completadas en subastas **Manheim US** que caen en **20 market classes** (esquema de clasificación **J.D. Power**); **excluye camiones pesados y motos**. | WebSearch; methodology `[VERIFICADO ×2]` |
| **Eliminación de outliers** | Media de millas y precio por model-year/make/body; outlier = transacción cuyo **precio Y millas** caen **fuera de 2,6 desviaciones estándar**. | WebSearch methodology (re-verif. 2026-06-30) `[VERIFICADO ×2]` |
| **Ajuste de mix** | Ponderado por **media móvil de 24 meses** de ventas pasadas por market class. | WebSearch methodology `[VERIFICADO]` |
| **Ajuste de km** | Regresión lineal simple precio↔millas por market class del mes actual; diferencial = km medio del mes − km medio 24 meses. | WebSearch methodology `[VERIFICADO]` |
| **Ajuste estacional** | Metodología **Census X** (método del Census Bureau) sobre los totales corregidos por mix y km. | WebSearch methodology `[VERIFICADO]` |
| **Datos fuente** | **5 M+ transacciones usadas/año** en subastas Manheim. | site.manheim consulting `[VERIFICADO]` |
| **Frecuencia de publicación** | **Mensual (5º día hábil)** + **actualizaciones de mitad de mes**. | site.manheim consulting `[VERIFICADO]` |
| **Sub-índices satélite** | **Three-Year-Old MMR Index** (depreciación, con price change %) · **EV Index** (base **ene-2015 = 100**) vs **Non-EV Index** (cada uno con YoY %) · **índices por segmento** (lujo, trucks, compactos…, seguidos por separado). | site.manheim consulting; trends MUVVI (re-verif. 2026-06-30) `[VERIFICADO ×2]` |
| **Data points publicados** | **MUVVI value** (índice) · **MoM %** · **YoY %** · **precios no ajustados YoY %** · **Three-Year-Old Index price change %** · **MMR retention %** · **sales conversion rate %** · **wholesale supply / days' supply (days' inventory)** + Δ vs mes/año previo · **EV Index YoY %** · **Non-EV Index YoY %**. | site.manheim consulting + trends mensuales (re-verif. 2026-06-30) `[VERIFICADO ×2]` |

### 3.4 AutoGrade® / Condition Report (CR) — campos atómicos

| Campo | Definición atómica | Fuente |
|---|---|---|
| **AutoGrade score (1.0–5.0)** | Cálculo de condición global del vehículo; **misma fórmula para todo coche** independientemente del año. (0 también referenciado como suelo.) | vininfohub; mymanheim PDF; NAAA `[VERIFICADO ×2]` |
| **Componentes del score** | **Daño cosmético** + **condición mecánica** + **maintenance/wear items**. | vininfohub; mymanheim `[VERIFICADO]` |
| **Bandas de interpretación** | **4.0–5.0** retail-ready (recon ligero, mayor valor) · **3.0–3.5** uso normal (desgaste visible, recon) · **≤2.5** problemas significativos (wholesale/export/parts). | vininfohub; manheim.co.nz `[VERIFICADO ×2]` |
| **Estándar de industria** | Creado por Manheim; vía acuerdo con **NAAA** disponible **gratis** a todas las subastas miembro NAAA. | vininfohub; NAAA PDF `[VERIFICADO ×2]` |
| **Seller's Disclosures** | Declaraciones del vendedor sobre condición **cosmética, mecánica y estructural**. | site.manheim VDP/CR `[VERIFICADO]` |
| **Structural Condition** | Evalúa componentes estructurales visibles (rocker panels, pillars, frame). | site.manheim CR `[VERIFICADO]` |
| **Announcements** | Anuncios del vendedor (defectos/condiciones que disparan arbitraje). | site.manheim arbitration guide `[VERIFICADO]` |
| **Tires & Wheels Details** | **Tamaño, condición y precio** de neumáticos/llantas. | site.manheim VDP `[VERIFICADO]` |
| **Odometer / disclosures** | Lectura de odómetro + disclosures de millaje. | site.manheim VDP `[VERIFICADO]` |

### 3.5 VI Data (Vehicle Information) — campos atómicos de inspección

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Diagnostic Trouble Codes (DTC / OBD-II)** | Códigos de diagnóstico capturados vía OBD-II, **near real-time**. | site.manheim VI Data `[VERIFICADO]` |
| **Engine audio/video (cold start)** | Captura de audio/vídeo del motor en arranque en frío. | VI Data `[VERIFICADO]` |
| **Mechanical condition observations** | Ruido, transmisión, fugas (leaks), escape (exhaust). | VI Data `[VERIFICADO]` |
| **6 high-resolution images con hotspots** | 6 imágenes HD con puntos de daño marcados. | VI Data `[VERIFICADO]` |
| **360-degree images** | Spin 360º del vehículo. | VI Data; Manheim Express `[VERIFICADO ×2]` |
| **Cosmetic damage: location + type** | Clasificación de daño cosmético por localización y tipo. | VI Data `[VERIFICADO]` |
| **Manufacturer build information + equipment** | Datos de fábrica y equipamiento vía VIN. | VI Data; Manheim Express `[VERIFICADO ×2]` |
| **High-value features highlighted** | Features de alto valor resaltadas para decisión rápida. | VI Data `[VERIFICADO]` |
| **AutoGrade Condition Score** | Score de condición (ver §3.4). | VI Data `[VERIFICADO]` |
| **EV battery capacity % vs original** | Capacidad de batería actual vs original. | VI Data `[VERIFICADO]` |
| **EV range: current vs new** | Autonomía actual comparada con la de nuevo. | VI Data `[VERIFICADO]` |
| **EV battery performance vs average** | Rendimiento de batería relativo a la media. | VI Data `[VERIFICADO]` |

### 3.6 Cox Automotive Intelligence (capa IA wholesale)

| Campo / capacidad | Definición atómica | Fuente |
|---|---|---|
| **Personalized inventory recommendations** | Aflora inventario wholesale según tu **actividad de puja y compra** + **potencial retail del vehículo** + **tendencias de mercado** → "inventario que encaja en tu lote". | coxautoinc home; autodealertoday `[VERIFICADO ×2]` |
| **Vehicle recommendation engine (ML)** | Motor que **puntúa el inventario Manheim disponible contra el perfil histórico de compra/puja del dealer** sobre un amplio set de atributos de vehículo y mercado. | coxautoinc RMS; press.manheim RMSAI `[VERIFICADO ×2]` |
| **AI-infused MMR valuations** | Capa IA sobre las valoraciones MMR para decisiones más rápidas en tiempo real. | coxautoinc new Manheim App `[VERIFICADO]` |
| **Trade Desk (AI-assisted)** | Curación de compra asistida por IA + negociación de deal. | coxautoinc new Manheim App `[PARCIAL]` |

### 3.7 RMS Automotive — optimización de cartera (remarketers / flotas / lessors)

| Producto | Campos atómicos | Fuente |
|---|---|---|
| **Pricing Optimization** | Fija **precio suelo de subasta (floor price) VIN-específico** usando atributos del VIN; uplift declarado **$100–200/vehículo** (≈$10–20 M en 100k unidades/año). | coxautoinc RMS `[VERIFICADO / CLAIM-VENDOR en cifras]` |
| **Location Optimization** | Distribuye inventario entre subastas físicas teniendo en cuenta **coste de transporte** para maximizar retención de cartera. | coxautoinc RMS `[VERIFICADO]` |
| **Reconditioning Optimization** | Recomienda **reparaciones VIN-específicas** usando el score **AutoGrade**. | coxautoinc RMS `[VERIFICADO]` |
| **Operación** | Integración en tiempo real, actualización dinámica de mercado, UI web con reporting, decisión a nivel VIN. | coxautoinc RMS `[VERIFICADO]` |

### 3.8 VPM (Vehicle Portfolio Management) — grandes carteras

`In-service vehicle tracking` (por **driver / mileage / location**) · `real-time vehicle status` · `pre-termination inspections` (captura de wear + documentación de **charge-back**) · `vehicle grounding` (con remarketing rápido) · `auto-consign tracking` (consignación a subasta física) · `online remarketing` (turnaround acelerado para reducir depreciación) · `transportation quote tracking` (visibilidad de ciclo completo) · `centralized payment / settlement` (post-sale). (Fuente: site.manheim large-portfolio-owners. `[VERIFICADO]`)

### 3.9 Manheim Express / Manheim App — tooling de transacción (campos)

**Lado vendedor (Manheim Express):** escanea VIN → presenta **MMR value** + **AutoCheck Snapshot** (historial) + **manufacturer build data** · **Condition Report** (Manheim Mobile Inspection CR o **Insight CR** por partner certificado) · **360º images** (creadas en <3 min) · **Guaranteed First Bid / Upside** (la única **garantía de primera puja** wholesale del sector) · **OBD-II code capture**. (Fuentes: press.manheim ManheimExpress; site.manheim. `[VERIFICADO ×2]`)

**Lado comprador (new Manheim App):** VIN scanning instantáneo · **MMR** + **MMR Range** · search · **real-time notifications** · **Simulcast** (puja en vivo) · **Cox Automotive Intelligence** (recomendaciones) · **evolved Condition Report** · **OBD-II capture** · **Trade Desk** · **Dealer Services** (soporte a nivel VIN con guía de pricing y recon). (Fuente: coxautoinc new-Manheim-App. `[VERIFICADO]`)

### 3.10 DealShield — protección de compra

`Garantía de devolución 21 días / 500 millas` con **reembolso total incl. fees de subasta** sobre compras digitales cualificadas · **DealShield Select** (actualizaciones de inventario cualificado). (Fuentes: dealer101; site.manheim DealShield. `[VERIFICADO ×2]`)
Relacionado (protección/arbitraje): **PSI (Post-Sale Inspection)** — inspección mecánica opcional post-compra (motor, transmisión, frame), ~**$100–200**. `[VERIFICADO]`

### 3.11 Índices de mercado Cox Automotive (inteligencia macro)

| Producto | Campos / métricas atómicas | Fuente |
|---|---|---|
| **Cox Automotive Dealer Sentiment Index (CADSI)** | Encuesta trimestral a dealers franquiciados+independientes US; escala **100 = fuerte/creciente, 50 = medio/estable, 0 = débil/decreciente**. Sub-índices: **current market**, **3-month outlook**, **customer traffic**, **profitability**, **EV sales sentiment**, **new/used inventory**, **costs**, **price pressure**, **F&I**, **limiting factors**. | coxautoinc CADSI Q1/Q2 2026 `[VERIFICADO ×2]` |
| **Cox Automotive Forecast (US auto sales)** | **New-vehicle sales forecast** (ej. 15,8 M 2026) · **retail sales** (12,9 M) · **fleet sales** (2,9 M) · SAAR · cuota por segmento/powertrain. | coxautoinc forecast jun-2026; outlook `[VERIFICADO ×2]` |
| **Vehicle Affordability Index** | Índice mensual de asequibilidad (semanas de ingreso medio para comprar; incorpora precio, tipos de interés, incentivos, renta). | coxautoinc; WebSearch `[VERIFICADO]` |
| **Car Buyer Journey (study)** | Estudio de comportamiento del comprador (tiempo de compra, satisfacción, canales online/offline). | WebSearch `[PARCIAL]` |
| **Industry Insights & Forecast Call** | Llamada trimestral con economista jefe + presentación PDF descargable. | coxautoinc; site.manheim consulting `[VERIFICADO]` |
| **Average EV transaction price** | Precio medio de transacción EV (ej. $54.523 may-2026). | coxautoinc home `[PARCIAL]` |

### 3.12 eVA Valuations & Appraisals (UK) — campos atómicos

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Trade value** | Valor trade (vía part-exchange). | evavaluations; coxautoinc.eu `[VERIFICADO]` |
| **Retail value** | Valor retail (vía datos retail de **Auto Trader UK**). | coxautoinc.eu; bodyshopmag `[VERIFICADO ×2]` |
| **Part-exchange value** | Valor de tasación part-ex omnicanal. | evavaluations `[VERIFICADO]` |
| **Cobertura de activos** | **Cars + LCV** (primera plataforma de tasación LCV del mercado UK). | fleetnews; motortrader `[VERIFICADO ×2]` |
| **Modos de captura** | Online · in-store · roadside · **eVA Self-Inspect**. | evavaluations; am-online `[VERIFICADO]` |
| **Volumen de dato** | **800.000+ price observations/día** (homepage); una fuente Cox Europe declara **1M+/día**. | evavaluations; coxautoinc.eu `[PARCIAL — discrepancia 800k vs 1M]` |
| **Precisión declarada** | **>99% de media** (combinando wholesale Manheim/Dealer Auction + retail Auto Trader). | coxautoinc.eu fuelfive `[CLAIM-VENDOR]` |
| **Tracción** | **450+ concesionarios**, **10 M+ valoraciones** servidas. | coxautoinc.eu; evavaluations `[VERIFICADO]` |

> **Nota wholesale-intel UK:** eVA fusiona el **wholesale de Cox (Manheim + Dealer Auction)** con el **retail de Auto Trader** → es el equivalente UK al "Live Market View" pero con dato de tasación; relevante como patrón de **fusión wholesale+retail** que cardeep puede imitar.

---

## 4. Metodología / fuentes de datos

- **MMR — "living algorithm":** modelo estadístico que **recalcula cada noche** los valores. Base = **media de precio mayorista, odómetro, grado de condición y build quality** de transacciones recientes, **excluyendo outliers**. Ventana de **13 meses** de ventas; cobertura de **~100% de transacciones de subasta Manheim** (5–10 M+ ventas según fuente). Ajustes derivados de algoritmos estadísticos: **odómetro, región, condición/AutoGrade, color, build/options, EVBH**. `[VERIFICADO ×2: valuation + MMR Help]`
- **MUVVI:** elimina outliers → media de precio por km y market class → ajusta por km (regresión lineal) → ajusta mix por **media móvil 24 meses** → **ajuste estacional Census X**. Base **ene-1997=100**, **20 clases J.D. Power**. `[VERIFICADO]`
- **AutoGrade:** fórmula consistente (cosmético + mecánico + wear), **idéntica para todo modelo/año**; estándar **NAAA**. `[VERIFICADO]`
- **VI Data / Condition Report:** inspección física (mobile inspection team) + **OBD-II near real-time** + audio/vídeo de motor + 6 fotos HD con hotspots + 360º + diagnóstico de batería EV. `[VERIFICADO]`
- **Cox Automotive Intelligence (IA):** ML que cruza **patrones históricos de puja/compra del dealer** × **atributos de vehículo/mercado** para puntuar inventario disponible. `[VERIFICADO ×2]`
- **eVA (UK):** **800k–1M+ price observations/día** combinando **Manheim + Dealer Auction (wholesale)** + **Auto Trader (retail)** → mayor dataset de vehículos UK. `[VERIFICADO]`
- **Ecosistema propietario:** el dato nace de la **transacción real de subasta** (Manheim), no de listings ni de paneles → ventaja de "ground truth" wholesale difícil de replicar. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle | Fuente |
|---|---|---|
| **Web portal** | `mmr.manheim.com` ("Go to MMR"), `manheim.com` (marketplace + VDP), `site.manheim.com`. | valuation; MMR Help `[VERIFICADO]` |
| **App móvil** | **Manheim App** (iOS/Android, buyer) + **Manheim Express** (seller, VIN scan/360/CR). | press.manheim; coxautoinc `[VERIFICADO]` |
| **API REST** | **`developer.manheim.com`**: **MMR Valuations API** (VIN o YMMT, single/batch, fecha histórica hasta 01-11-2018) + **MMR Forecast API** (hasta 106 semanas). | developer.manheim `[VERIFICADO]` |
| **Cox Automotive Integration Platform** | Plataforma de integración para partners/dealers (developer.coxautoinc.com). | WebSearch `[PARCIAL]` |
| **Data licensing (enterprise)** | "Licensed Data" vía **API u otra transmisión electrónica**; permitted-use: *Use Within Industry Software Application / Wholesale Marketplace / Auction Software Application* (según Order Form). | MMR Additional Terms PDF `[VERIFICADO]` |
| **Índices / data files** | MUVVI: portal web + **data files descargables** + **manheim.data@coxautoinc.com** (email request) + newsletter + **llamadas trimestrales** + PDFs. | site.manheim consulting `[VERIFICADO]` |
| **Integraciones de terceros** | **Carbly**, **Laser Appraiser** (VIN scanners que sirven MMR vía suscripción), **vAuto** (Live Market View), DMS. | getcarbly; laserappraiser `[VERIFICADO ×2]` |
| **Simulcast** | Puja online en vivo embebida (subasta digital + física simultánea). | site.manheim simulcast `[VERIFICADO]` |
| **Inspección/CR** | Insight Condition Report (insightcr.manheim.com), AutoCheck Snapshot (vehiclehistservice.manheim.com). | WebSearch `[VERIFICADO]` |

---

## 6. Precio (parcialmente descubierto)

| Ítem | Precio / modelo | Fuente |
|---|---|---|
| **MMR — acceso base** | **Complimentary** (gratis) con cuenta Manheim.com / mmr.manheim.com / app — "to make it easy to get pricing data". | valuation `[VERIFICADO]` |
| **MMR — acceso completo** | **Suscripción** (full functionality); o vía terceros (**Carbly**, **Laser Appraiser** con free trial). | getcarbly; laserappraiser `[VERIFICADO ×2]` |
| **MMR API / Licensed Data** | **Licencia enterprise** por permitted-use; precio **no público** (Order Form). | MMR Additional Terms `[VERIFICADO por ausencia de precio]` |
| **Buyer fees (subasta)** | **Tiered por precio de vehículo × nivel de cuenta** (Advantage → Premier+); bajan con volumen anual. No hay tarifa única pública (location/account-specific). | dealer101; scribd buyer fees `[VERIFICADO]` |
| **Simulcast fee** | Fee adicional por vehículo comprado online (sobre el buyer fee normal). | site.manheim simulcast `[VERIFICADO]` |
| **PSI** | ~**$100–200** (inspección post-venta opcional). | dealer101 `[PARCIAL]` |
| **DealShield** | Coste por garantía (no público; sobre vehículos cualificados). | site.manheim `[PARCIAL]` |
| **Índices MUVVI/CADSI/Forecast** | **Gratis / público** (PR + PDFs + newsletter). | coxautoinc `[VERIFICADO]` |
| **vAuto / KBB / eVA** | Suscripción dealer (ver fichas propias; eVA = SaaS UK por cotización). | — |

> **Modelo global:** **freemium en el dato wholesale** (MMR base gratis → fideliza al ecosistema Manheim) + **fees transaccionales** de subasta (la verdadera monetización) + **licencia enterprise de dato/API** + **SaaS de inventario** (vAuto). Los **índices macro son gratis** como herramienta de marca/thought-leadership. `[RECONSTRUIDO]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca Cox/Manheim **cada dato**. Patrón rector wholesale: **"la decisión de puja al lado del valor de mercado y de la condición"** — el comprador ve, en la misma Vehicle Details Page, qué vale (MMR), en qué estado está (AutoGrade/CR) y a cuánto puede pujar (bid bar) sin cambiar de pantalla.

**A. Vehicle Details Page (VDP) — ficha del lote en subasta (`manheim.com`).** Centro de la decisión. Layout: **fotos prominentes** (6 HD + 360º) arriba; **Condition Assessment Area** con **iconos visuales + AutoGrade/CR score** y descripciones exterior/interior con imágenes ancladas a cada zona; **Seller's Disclosures + Announcements** (cosmético/mecánico/estructural); **Structural Condition** (rocker panels, pillars, frame); **Tires & Wheels** (tamaño/condición/precio); **Odometer**; **diagnostic/OBD-II data** cuando existe; **AutoCheck Snapshot** (historial). El **bid bar permanece fijo al hacer scroll** y el **checkout es un slide-out** dentro de la propia VDP (rediseño abr-2026). El **MMR** del vehículo se consulta junto al lote.

**B. Pantalla MMR (`mmr.manheim.com` / app).** Encabezada por el **Base MMR** y el **MMR Range** (banda de confianza 70%); tres columnas **Above / Average / Below** para **wholesale** y **estimated retail**; bloque de **ajustes** (odómetro, región, color, grade, EVBH, build/options) que recalcula el **Adjusted Pricing** al VIN; **gráfico/serie histórica** (30 días, 2/6/12 meses); **proyección** (next month / next year); **tabla de transacciones** recientes (precio/km/condición/fecha) con **outliers marcados con asterisco** e **icono de small sample**.

**C. Recomendaciones (Cox Automotive Intelligence, home del marketplace/app).** Carrusel/feed de **inventario personalizado** ("fits your lot") puntuado por el motor ML contra el perfil de puja/compra; las **MMR valuations potenciadas por IA** se muestran inline en cada recomendación.

**D. Manheim Express (seller, móvil).** Flujo paso-a-paso: escaneo VIN → tarjeta con **MMR + AutoCheck + build data** → captura **360º + CR** → decisión: **Guaranteed First Bid (Upside)** vs listar en marketplace vs inspección vs consignar. El **GFB** se presenta como un número/oferta destacada.

**E. Índices macro (`coxautoinc.com/insights` + `site.manheim.com/consulting`).** Fuera de la ficha: **MUVVI** como **gráfico de serie temporal** (índice + %MoM/YoY) con sub-índices (3-yr-old, EV vs non-EV, segmentos); **CADSI** como **scorecard** de barras 0/50/100 por dimensión (current, outlook, traffic, profit, EV…); **Forecast/Affordability** como nota + tablas; todo con **PDF descargable** y **call trimestral**.

**F. VPM / Large Portfolio (lessors/flotas).** Dashboard de **ciclo de vida**: vehículos en servicio (driver/km/location), grounding, consignación auto, remarketing, transporte y settlement — vista de cartera, no de coche individual.

**G. eVA (UK).** Tasación omnicanal: en la ficha de trade-in se muestran **trade value + retail value + part-exchange**, alimentados por el dataset combinado wholesale+retail; captura por self-inspect/roadside/in-store.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Ground-truth wholesale propietario:** el MMR nace de **transacciones reales de subasta Manheim** (el mayor marketplace del mundo, ~8M coches ofrecidos/año), no de listings ni paneles. Es el **benchmark mayorista estándar del sector** (70M+ lookups/año). Casi imposible de replicar sin operar las subastas.
2. **MMR servido como dato Y como API Y como índice:** valor por VIN (above/avg/below + range), **API REST** (single/batch, histórico desde 2018, forecast a **106 semanas**) y **índice macro** (MUVVI) — la misma materia prima en tres formatos de entrega.
3. **EV Battery Health (EVBH 0–100) como factor de valoración nativo** + diagnóstico de batería (capacidad vs original, range vs new, performance vs media) — pocos valuadores integran salud de batería en el precio.
4. **AutoGrade como estándar de industria (NAAA):** un único score de condición 1.0–5.0 con la misma fórmula para todo coche, adoptado por todo el sector → comparabilidad universal.
5. **Capa IA (Cox Automotive Intelligence + RMS):** recomendación de inventario por perfil de puja, **floor pricing VIN-específico**, optimización de **ubicación** y **recon** para carteras — inteligencia accionable, no solo valor.
6. **Ciclo wholesale completo bajo un techo:** valorar (MMR) → inspeccionar (AutoGrade/VI Data/OBD-II) → vender (Express/Upside GFB) → comprar (Simulcast) → proteger (DealShield/PSI) → transportar (Central Dispatch) → financiar (NextGear) → gestionar cartera (VPM/RMS).
7. **Huella internacional wholesale:** a diferencia de vAuto/KBB (solo Norteamérica), Manheim+Cox operan **Europa (13 centros), UK, ANZ, Canadá**; **eVA** fusiona wholesale+retail en UK.
8. **Índices macro gratuitos** (MUVVI, CADSI, Forecast, Affordability) como autoridad de mercado citada por prensa, lenders y Wall Street (Moody's lista el MUVVI).

---

## 9. Gaps (lo que NO ofrece)

1. **MMR es valor WHOLESALE, no retail-consumer:** el "retail" del MMR es estimado/secundario; la autoridad de valor al consumidor es **KBB** (marca hermana, ficha aparte), no el MMR. `[VERIFICADO]`
2. **Curva de depreciación / residual a años vista limitada:** el Forecast MMR llega a **106 semanas (~2 años)**; **no** publica curvas de **valor residual multi-anual / forecast de leasing** estilo ALG/Autovista/J.D. Power Valuation. `[VERIFICADO por ausencia]`
3. **Vehicle history NO propio:** depende de **AutoCheck (Experian)** para el historial (Snapshot integrado), no publica un informe de historial propio tipo Carfax. `[VERIFICADO]`
4. **Specs/catálogo de equipamiento no es su producto:** usa **manufacturer build data** para ajustar valor, pero no vende una base de specs/VIN-decode independiente tipo Chrome Data/DataOne/JATO. `[VERIFICADO por ausencia]`
5. **Dato/índice macro centrado en EE. UU.:** el MUVVI y los índices son **US-only**; Europa/UK tienen productos distintos (eVA, Dealer Auction) **sin un índice MUVVI-equivalente público** del mismo peso. `[VERIFICADO por ausencia]`
6. **MMR base gratis pero "full" cerrado al ecosistema:** acceso completo exige **cuenta Manheim / dealer licenciado** + suscripción; **no consumer-facing** (solo profesionales). `[VERIFICADO]`
7. **Precio de subasta opaco:** buyer fees **tiered, location/account-specific, sin tarifa pública única** → difícil de modelar el coste total de adquisición desde fuera. `[VERIFICADO]`
8. **Atado al ecosistema Cox:** el máximo valor (recomendaciones IA, Upside, Express, VPM) solo se materializa **dentro de Manheim/Cox**; fuera del marketplace, menos diferencial. `[VERIFICADO]`
9. **No tasa al particular directamente bajo marca Manheim:** la captación al consumidor pasa por **KBB ICO** (hermana), no por Manheim/MMR. `[VERIFICADO]`
10. **Enumeración EU/ANZ menos transparente:** las páginas `.eu` devuelven 403 a fetchers; cobertura europea verificada vía PR/agregadores, con menos granularidad de campos que el lado US. `[NOTA DE MÉTODO]`

---

## 10. Fuentes

**Corporativo / identidad:**
- Cox Automotive home: https://www.coxautoinc.com/ · About: https://www.coxautoinc.com/about-us/
- Formación Cox Automotive (2014): https://www.coxautoinc.com/insights/cox-enterprises-announces-formation-cox-automotive/
- Cox Enterprises (1898, Atlanta, $21B, subsidiarias): https://en.wikipedia.org/wiki/Cox_Enterprises
- Escala/estructura (Inventory Solutions, Grace Huang; Mobility): https://growjo.com/company/Cox_Automotive_Mobility · https://www.zoominfo.com/c/cox-automotive/10748444 · https://www.owler.com/company/coxautoinc

**Manheim Market Report (MMR) + API:**
- MMR Help (canónico): https://site.manheim.com/en/help/mmr.html · Tutorial: https://site.manheim.com/tutorials/manheim-market-report-help · Best practices: https://site.manheim.com/tutorials/mmr-best-practices-2
- Valuation services: https://site.manheim.com/en/services/valuation.html
- API Developer Portal: https://developer.manheim.com/ · Valuations API (campos verbatim): https://developer.manheim.com/apis/marketplace/valuations.html · Forecast API: https://developer.manheim.com/apis/marketplace/forecasts.html
- MMR Additional Terms (licensing/permitted-use): https://www.coxautoinc.com/terms/wp-content/uploads/sites/3/MMR-Additional-Terms.pdf
- Integradores 3os: https://getcarbly.com/vehicle-appraisals/manheim-market-report/ · https://laserappraiser.com/car-appraisals/manheim-market-report · https://caredge.com/guides/what-are-mmr-values

**MUVVI + índices:**
- Used Vehicle Value Index (servicio): https://site.manheim.com/en/services/consulting/used-vehicle-value-index.html · Consulting: https://site.manheim.com/en/services/consulting.html
- Metodología (PDF): https://site.manheim.com/wp-content/uploads/sites/2/2023/07/Used-Vehicle-Summary-Methodology.pdf
- Moody's (lista el índice): https://www.economy.com/united-states/manheim-used-vehicle-value-index
- Trends recientes (Q1/May 2026): https://www.coxautoinc.com/insights/manheim-used-vehicle-value-index-may-2026-trends/ · https://www.coxautoinc.com/insights/q1-2026-muvvi/

**AutoGrade / Condition Report / VI Data / VDP:**
- AutoGrade (3os + PDF + NAAA): https://vininfohub.com/manheim-condition-grades · https://www.mymanheim.com/app/uploads/2023/09/All-About-Autograde-v3.0.pdf · https://www.naaa.com/References/reference_materials/Autograde_Std_Vehicle_Condition_Grade_5_15_2018.pdf · https://press.manheim.com/ManheimAutoGradeExpansion
- VI Data: https://site.manheim.com/solutions/vehicle-information/vi-data
- Condition Reporting / VDP: https://site.manheim.com/en/services/condition-reporting.html · https://site.manheim.com/tutorials/condition-reports · https://site.manheim.com/news/a-new-visual-experience-for-vehicle-pages · https://site.manheim.com/solutions/condition-report

**Cox Automotive Intelligence / RMS / VPM / Express / App:**
- Cox Automotive Intelligence + new Manheim App: https://www.coxautoinc.com/insights/introducing-the-new-manheim-app-and-more-steps-toward-a-seamless-more-connected-wholesale-journey/
- RMS Automotive (pricing/location/recon optimization + recommendation engine): https://www.coxautoinc.com/insights/rms-automotive-uses-artificial-intelligence-to-reshape-the-portfolio-management-business/ · https://press.manheim.com/RMSAI · https://www.autodealertodaymagazine.com/353876/manheim-personalized-recommendations-drive-sales
- Large Portfolio Owners (VPM): https://site.manheim.com/solutions/large-portfolio-owners
- Manheim Express (seller, GFB/Upside, AutoCheck, build data, 360): https://site.manheim.com/solutions/manheim-express · https://press.manheim.com/ManheimExpress

**Subasta / fees / protección:**
- Buyer fees / guía: https://dealer101.com/auctions/companies/manheim/ · https://www.scribd.com/document/700995654/manheim-buyer-fee
- Simulcast: https://site.manheim.com/en/help/simulcast.html
- DealShield: https://site.manheim.com/news/everything-you-need-to-know-about-dealshield-selects-inventory-updates · Digital Buyer Protection: https://site.manheim.com/en/marketplace-policies/us-policies/digital-buyer-protection.html

**Índices macro (CADSI / Forecast / Affordability):**
- CADSI Q1/Q2 2026: https://www.coxautoinc.com/insights/q1-2026-cadsi/ · https://www.coxautoinc.com/insights/q2-2026-cadsi/ · PDF: https://www.coxautoinc.com/wp-content/uploads/2026/03/Q1-2026-Cox-Automotive-Dealer-Sentiment-Index-Presentation.pdf
- Forecast / Outlook 2026: https://www.coxautoinc.com/insights/cox-automotive-forecast-june-2026-u-s-auto-sales-forecast/ · https://www.coxautoinc.com/insights/cox-automotive-2026-outlook/

**Europa / UK / ANZ:**
- Cox Automotive Europe: https://www.coxautoinc.eu/ · Manheim Auction Services: https://www.coxautoinc.eu/our-products/manheim/manheim-auction-services/ · Dealer Auction: https://www.coxautoinc.eu/experience-more/dealer-auction/ · Modix: https://www.coxautoinc.eu/our-products/modix/
- eVA: https://evavaluations.com/ · https://www.coxautoinc.eu/our-products/eva-valuations-appraisals/ · LCV first-to-market: https://www.fleetnews.co.uk/news/cox-automotive-launches-lcv-appraisal-and-valuation-platform · Auto Trader partnership: https://www.bodyshopmag.com/2025/news/cox-automotive-and-auto-trader-partner-on-vehicle-values/
- Dealer Auction JV (2018): https://www.manheim.co.uk/news/2018/dealer-auction-160818 · Movex: https://www.motorfinanceonline.com/news/cox-automotive-revamps-movex-app-in-digital-drive/
- ANZ grading: https://www.manheim.co.nz/passenger-vehicles/landing/vehiclegrading

### Notas de verificación
- **Owner Cox Enterprises (Atlanta, 1898), Cox Automotive formada 2014, 13+ marcas, 40k+ dealers:** Wikipedia + coxautoinc + WebSearch. **[VERIFICADO]**
- **MMR campos atómicos:** triangulados entre **developer.manheim (API, verbatim)** + **MMR Help** + integradores (Carbly/LaserAppraiser). **[VERIFICADO ×2+]**
- **MUVVI metodología (base ene-1997=100, 20 clases J.D. Power, mix 24mo / km regresión / Census X, outliers a 2,6σ en precio Y millas):** WebSearch metodología + página de servicio + Moody's. **[VERIFICADO]** — el PDF oficial de metodología no se pudo parsear localmente (falta `pdftoppm`), pero el contenido está confirmado por ≥2 fuentes secundarias ortogonales.
- **Re-verificación viva 2026-06-30:** pase independiente con WebFetch sobre fuentes canónicas vivas (developer.manheim valuations+forecasts, site.manheim VI Data + MMR Help + consulting/MUVVI, coxautoinc about + RMS) → confirmó verbatim los campos atómicos del MMR/Forecast API, VI Data (12 campos), AutoGrade, RMS y los data points MUVVI; deltas añadidos: inputs API `include`+`country`, exclusión outlier MMR (ventas CA previas, <50 mi), outlier MUVVI 2,6σ, EV Index base ene-2015=100, granularidad de data points MUVVI. **[VERIFICADO ×2]**
- **AutoGrade 1.0–5.0, NAAA, fórmula uniforme:** vininfohub + NAAA PDF + manheim.co.nz. **[VERIFICADO]**
- **VI Data / OBD-II / batería EV / 360 / 6 fotos:** site.manheim VI Data. **[VERIFICADO — 1 fuente oficial granular]**
- **Cox Automotive Intelligence + RMS (pricing/location/recon):** coxautoinc + press.manheim + autodealertoday. **[VERIFICADO ×2]**; cifras de uplift ($100–200/veh, $10–20M) = **[CLAIM-VENDOR]**.
- **Escala marketplace (111 ubicaciones, 650 lanes, 80k dealers, 8M coches, $80B, 70M lookups):** agregación de WebSearch + site.manheim; algunas cifras varían entre fuentes → **[PARCIAL]** donde aplica.
- **eVA UK (800k vs 1M obs/día, >99%):** homepage vs artículo Cox Europe discrepan en volumen → **[PARCIAL]**; precisión = **[CLAIM-VENDOR]**.
- **Páginas `.eu` y algunos PDFs:** devolvieron **403** a WebFetch → datos europeos vía PR/prensa/agregadores. **[NOTA DE MÉTODO]**
- **exa MCP:** NO disponible en el entorno (ToolSearch "exa…" solo devolvió gbrain/claude-mem/WebFetch/WebSearch). Investigación con **WebSearch + WebFetch + Read(PDF)**. **[NOTA DE MÉTODO]**
- **Hermanas vAuto / KBB:** auditadas en ficha propia; aquí solo referenciadas para no duplicar.
