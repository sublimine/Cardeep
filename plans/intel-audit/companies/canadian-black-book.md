# Canadian Black Book — Auditoría atómica

> Slug: `canadian-black-book` · Subdominio cardeep: **valuation** · Región: Norteamérica (Canadá)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó.
> Naturaleza: **autoridad independiente #1 de valoración de vehículos usados en Canadá** (el equivalente
> canadiense de Black Book US / Kelley Blue Book). Marca de datos B2B + portal de trade-in al consumidor.
> Nota de acceso: `canadianblackbook.com` **resetea la conexión** a fetchers automáticos
> (ERR_CONNECTION_RESET en Playwright; "Socket is closed" en WebFetch). El contenido de páginas propias
> se extrajo vía el backend de WebSearch (que sí las lee) + fuentes terceras verificables.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre | Canadian Black Book (CBB) | canadianblackbook.com |
| Fundación (Canadá) | **1961** ("Powering the automotive industry since 1961") | canadianblackbook.com/about |
| Fundación (matriz US) | **1955**, Gene McDonald, Gainesville/Lawrenceville (Georgia) | Wikipedia (Black Book / National Auto Research) |
| Owner / grupo | **Hearst** — US Black Book lo publica **National Auto Research**, división de **Hearst Communications**; "Black Book" es marca registrada de **Hearst Business Media Corporation**. CBB es la unidad canadiense del mismo grupo. | Wikipedia; búsqueda D&B; about page |
| Adquisición Hearst | US Black Book adquirido por Hearst Corporation en **1980** | Wikipedia |
| HQ Canadá | **Markham, Ontario** (Wikipedia US dice "Toronto"; D&B y perfiles dicen Markham, ON) | D&B; ZoomInfo; Wikipedia |
| HQ matriz US | **Lawrenceville, Georgia** (+ oficinas FL, MD) | Wikipedia |
| Posicionamiento | "the leading independent authority on used vehicle valuations in Canada" · "The Authority for vehicle values" | canadianblackbook.com; press |
| Tagline | **"Powering the Auto Industry [with Data]"** | homepage |
| Promesa de dato | "the most precise, **VIN-specific**, actionable data in the market, **updated daily from more sources than anyone else**" | homepage |

**Categorías de producto:** (1) Valoración de vehículos usados (núcleo: wholesale/retail/trade-in/private party),
(2) Forecast de valor residual / future value, (3) APIs y data feeds (GraphQL/REST), (4) Herramientas de
dealer (Cherry app, TradeMax lead-gen, Pulse analytics, ValuEngine batch), (5) Datos de coche nuevo y VIN
decode / Enhanced Vehicle Matching, (6) Inteligencia de mercado (Used Vehicle Retention Index, awards,
informes), (7) **Canadian Black Book Financial** (brazo de financiación al consumidor — lead/originación).

**Cliente objetivo (segmentos declarados en home):** **Dealers · Auto Finance · OEMs · Remarketing ·
Insurance · Marketing · Integration Partners · Rental, Fleet & Ride Share** + **consumidores** (portal
trade-in gratuito). (Fuente: homepage + about.)

> ⚠ **No confundir** con: **Canadian Red Book** (canadianredbook.com, competidor directo de valoración) ni
> con **Canadian Blue Book** (canadianbluebook.com, powersports: motos/snowmobiles/ATV/PWC — **otra empresa**).

---

## 2. Cobertura

- **Geografía:** **Canadá** (todas las regiones/provincias; valores ajustados por **código postal**). El
  índice se construye con datos de "all regions of Canada". **No** hay cobertura europea ni de EE. UU. bajo
  la marca CBB (EE. UU. = Black Book US, hermana). (Fuente: black-book-index; about.)
- **Nuevo y usado:** ambos. Usado es el núcleo (wholesale/retail/trade-in/private party + residual). Nuevo
  vía **New Car API** (lookup por VIN, trims) y datos de MSRP para residual.
- **Tipos de vehículo cubiertos:**
  - **Cars, SUVs, light-duty trucks** (núcleo) + **commercial vans**. (vehicle-values; awards "20 categorías": cars, trucks, SUVs, PHEV, EV.)
  - **Cars of Particular Interest (CPI):** **colección, lujo, exóticos, highline** — coches y light trucks **desde 1946**; valores retail en **fair / good / excellent**. (api page)
  - **Recreational Vehicles (RV):** vía Recreational Vehicle API. (api page)
  - **History-Adjusted Valuations** disponibles para **cars, SUVs y light-duty trucks**. (vehicle-values)
- **NO cubre (gaps de scope):**
  - **Motocicletas / powersports** (motos, snowmobiles, ATV, PWC) → eso es **Canadian Blue Book**, empresa distinta. `[VERIFICADO]`
  - **Medium/heavy-duty commercial trucks & trailers** — la matriz **US Black Book sí** los cubre, pero **CBB Canadá no** los lista. `[VERIFICADO por ausencia + contraste con catálogo US]`

> Contraste matriz US (referencia, **no** aplicable 1:1 a Canadá): Black Book US cubre new+used, cars, light
> trucks, **colección 1946+, motorcycles, ATVs, snowmobiles, PWC, y heavy-duty commercial trucks & trailers**.
> (Wikipedia.) En Canadá el scope es **más estrecho** (sin powersports propios, sin heavy-duty dedicado).

---

## 3. Productos + campos atómicos

### 3.1 Tipos de VALOR (materia prima)

Fuente: `vehicle-values/`, `api/`, `toolkit-5-essential-apis…`.

| Valor | Definición / nota atómica |
|---|---|
| **Wholesale value** (current + historical) | Valor mayorista en subasta. **Residual values disponibles para wholesale.** |
| **Wholesale Average** | Benchmark del vehículo en subasta mayorista con calidad en condición **Average**; base del índice UVRI. |
| **Retail value** (current + historical) | Valor minorista (precio de venta a consumidor). |
| **Trade-in value** (current + historical) | Lo que un dealer paga al entregar; **único valor expuesto al consumidor** en el portal. |
| **Private Party value** (current + historical) | Valor entre particulares (disponible vía datos, no en el portal de consumo). |
| **Residual / Future value** | Pronóstico de valor futuro. **Proyecciones 1–72 meses** con **History Adjustments** (ValuEngine / Residual APIs). |
| **History-Adjusted Value** | Valor ajustado por historial VIN-específico (ver §3.4). |
| **Custom (adjusted) Trade Value** | **Un único** valor CBB ajustado en tiempo real según respuestas a preguntas de condición + km real + ubicación (Custom Trade Value API). |
| **CPI retail value** | Para colección/lujo: retail en **Fair / Good / Excellent**, vehículos desde 1946. |
| **New Car data** | Datos de coche nuevo; lookup por VIN; identificación de trims (New Car API). |

> **Condición:** el portal de consumo asume **condición media por defecto y NO permite especificarla** (gap).
> Las herramientas profesionales sí ajustan condición (Custom Trade Value API: preguntas bespoke; CPI:
> fair/good/excellent). **Las etiquetas exactas de los tiers de condición wholesale de CBB no se publican**
> abiertamente — los tiers "Extra Clean / Clean / Average / Rough" son nomenclatura conocida de **Black Book
> US** y **no están verificados como idénticos en CBB Canadá**. `[NO-VERIFICADO]`

### 3.2 Used Car Web API — esquema de campos (el núcleo de datos)

Fuente: `api/` + `toolkit-5-essential-apis…` (lectura vía WebSearch). Usuarios: dealers, lenders, insurers.
Integración en apps/web/sistemas de inventario. **Actualización diaria.**

**Valores entregados:** retail, trade-in, wholesale, **historical** (los cuatro) + residual (wholesale).
**VIN decode (Enhanced Vehicle Matching):** matching preciso a **trim, options, mileage, condition**;
17-dígitos → **single trim + add/deducts** aplicables.

**Descripción / atributos de vehículo:**
- Year · Make · Model · Series · Body style · Trim · Options/equipment · add/deducts.

**Métricas de mercado incluidas (atómico, verbatim del backend):**
- **Number of price changes**
- **Price history** · **Mileage history**
- **Days to turn**
- **Market days' supply**
- **Minimum price** · **Maximum price**
- **Minimum mileage** · **Maximum mileage**
- **Mean price** · **Median price**
- **Mean mileage** · **Median mileage**

**Developer Portal (entorno cloud):** salida **JSON & XML**, llamadas **"what if"**, **robust query
filtering**, test harness, documentación, gestión de seguridad, reporting de actividad.
**GraphQL** disponible para Used Car Web API, New Car Web API y Retail Web API.

### 3.3 Catálogo de APIs (las "5 esenciales" + extras)

| API | Qué hace | Campos / outputs atómicos |
|---|---|---|
| **Used Car Web API** | Valoración usado VIN-específica | retail/trade-in/wholesale/historical + residual; VIN decode (trim/options/mileage/condition); métricas de mercado §3.2; JSON/XML/GraphQL. |
| **Custom Trade Value API** | Valor de trade ajustado a cliente | Inputs: respuestas a **preguntas bespoke de condición** + **km real** + **ubicación** → **un único** valor CBB ajustado **en tiempo real**. |
| **Residual Value API(s)** | Forecast de residual | Combina **historical + current + forecast**; modela impacto de cambios de mercado, **incentivos**, **shifts de oferta regional**. **Residual Sensitivity Analysis**: ajustar **MSRP**, **incentive packages**, **rental penetration** para modelar escenarios de depreciación. |
| **Retail Market Insights API** | Análisis de datos retail canadienses | KPIs granulares: **Days On Market**, **Listing Mileage**; **market activity tracking** por **modelo / geografía / dealer group**; segmentos para **optimización de programa CPO**. Retail Listings mapeadas a descripciones BB con precisión a nivel trim. |
| **ValuEngine** | Valoración batch de portfolio | Procesa de **miles a millones de VINs en un solo job**; **historical/current/projected residual** a nivel **trim**; loss forecasting, detección de **delinquencies**, estrategia de collections, risk analysis; **proyecciones 1–72 meses con History Adjustments**; **Enhanced Vehicle Matching** (ML+NLP); CSV / archivo delimitado; nueva interfaz web; analiza "all VIN-specific data points and valuations" para profit potential y risk levels. |
| **New Car (Web) API** | Datos de coche nuevo | Integrar new car data; lookup por VIN; encontrar trim levels. |
| **Recreational Vehicle API** | Datos de RV | Valoración de RVs. |
| **Cars of Particular Interest API** | Colección/lujo/exótico/highline | Coches y light trucks **desde 1946**; retail en **Fair / Good / Excellent**. |
| **Retail Web API** | Datos de listings retail | Retail Listings mapeadas a descripciones BB (precisión a trim); GraphQL. |
| **Connect API** | (connect-api.canadianblackbook.com) | Endpoint de integración. `[NO-VERIFICADO contenido]` |

### 3.4 History-Adjusted Valuations (HAV) — diferencial fuerte

VIN-specific, analytics-driven. **Factores de historial analizados (atómico):**
- **Number of owners** (nº de dueños previos)
- **Vehicle usage** (uso: flota/rental/personal)
- **Accident occurrence** (siniestro)
- **Accident severity** (severidad del siniestro)
- **Title issues** (problemas/branding de título)
- **Flood damage** (inundación)
- **Hail damage** (granizo)
- **Fire damage** (fuego)
- **CPO history** (historial de certificación)
- "+ other variables not obvious on physical inspection"

**Precisión:** en promedio **31% más preciso** vs precio de transacción de subasta que una valoración sin
ajuste de historial. Disponible para **cars, SUVs, light-duty trucks**. (Fuentes: Digital Dealer; Auto
Remarketing; Dealer Marketing Magazine.)

### 3.5 Enhanced Vehicle Matching (EVM) — decode VIN→trim

- Problema: **~30% de los VINs no decodifican a un único trim**; ajustar por equipo suele requerir trabajo manual.
- Solución: IA + big data; analiza **millones de registros al día** de múltiples fuentes + **OEM build data**
  → reduce drásticamente los one-to-many decodes y **aplica add/deducts automáticamente**.
- "Industry leader in trim decoding". Campos: year, make, model, series, body style, trim. (Fuente: vin-decoding; enhanced-vehicle-matching.)

### 3.6 Used Vehicle Retention Index (UVRI) — métrica de mercado insignia

- **Qué es:** índice de salud del mercado de usados en Canadá.
- **Cómo se calcula (atómico):** **Wholesale Average** publicado sobre vehículos de **2 a 6 años**, como
  **% del MSRP original típicamente equipado**; **ponderado por volumen de matriculaciones** de usados;
  **ajustado por edad, kilometraje, condición e inflación (MSRP)**.
- **Fuente del dato:** actualizaciones diarias de valor agregadas de **cientos de subastas mayoristas
  físicas y online** por todo Canadá; "no bias toward any brand, auction or region".
- **Lectura reciente:** **marzo 2026 = 132,5 puntos** (febrero 132,2); **YoY −5,3%**. (Fuente: black-book-index; press CBB; Auto Remarketing.)

### 3.7 Awards (capa de autoridad / marketing)

| Programa | Mide | Métrica atómica |
|---|---|---|
| **Best Retained Value Awards** | Valor retenido del **pasado** | **% del MSRP original retenido tras 4 años**. 18ª edición; 2025 analizó MY2022 en **15 categorías + 4 Overall Brand**. **Media industria 2025 = 67,5%** (máximo histórico 80% en 2022, COVID). |
| **Best Residual Value Awards** | Valor proyectado al **futuro** | Modelos propietarios de forecast: tendencias históricas de depreciación, condiciones de mercado, fuerza de marca, oferta/demanda. Categorías **PHEV/BEV** mainstream + premium. |

> Regla mnemotécnica oficial: **"Retained = value held from the past; Residual = values held into the future."**

### 3.8 Apps y herramientas de producto

| Producto | Qué es | Campos / features |
|---|---|---|
| **Cherry (CBB Cherry)** mobile app | App de dealer "for Better Decisions" | **VIN scanner** líder (point/scan/complete); valoración + appraisal estándar; **inventory discovery** (auto-identifica los vehículos más deseables **en subasta**); **wholesale + retail + trade-in** en uno; **comparables cercanos**; **Retail Market Insights**: **days-to-turn, market days' supply, average listing price**; updates diarios; lista de búsquedas recientes. |
| **Pulse** | Herramienta de **visualización** de datos retail canadienses | Crear **segmentos** desde portfolio propio o desde vista holística del mercado retail CA; filtrar por **vehículo / dealer / geografía**; KPIs por segmento: **Daily Vehicle Volume, Average Listing Mileage, Days on Market**. |
| **TradeMax** | Widget de **lead-gen / trade-in** embebible en web de dealer | Captura de lead rápida (mayor conversión); **fully customizable** (logo, colores, fuente); **ADF compliant** + compatible con la mayoría de **CRM**; valor de trade respaldado por dato CBB. Subdominios: `trade.canadianblackbook.com/embed`, `tradein.canadianblackbook.com`. |
| **Value Your Vehicle** (portal consumo) | Tasación de **trade-in** gratuita al consumidor | Ver §7 (placement). Solo **trade-in value** (rango). |
| **ValuEngine** | Plataforma batch de collateral/portfolio | Ver §3.3. |
| **Digital / Print book** | Suscripción de "pricing book" | Acceso online, móvil o **edición impresa** (publicada **semanalmente**). `[precio = dato US, ver §6]` |
| **Canadian Black Book Financial** | Brazo de **financiación al consumidor** | Partner con proveedores financieros canadienses para tasas competitivas de auto-financing; capta leads (`listings.canadianblackbook.com/cbbf`). |

---

## 4. Metodología / fuentes de datos

- **Fuentes:** transacciones de vehículos por todo Canadá — **subastas mayoristas** (cientos, físicas +
  online), **ventas de dealer**, **transacciones entre particulares**, **registros provinciales de venta**,
  **listings online**, tendencias de mercado. Revisado regularmente. (Fuentes: autocorp.ai; clutch.ca; black-book-index.)
- **Proceso:** combinación de **subject-matter experts (analistas automotrices)** + **data scientists** con
  **machine learning** y **NLP**; "advanced algorithms + deep industry experience". (vehicle-values; valuengine press.)
- **VIN→valor:** Enhanced Vehicle Matching (§3.5) — millones de registros/día + OEM build data → trim único + add/deducts.
- **Factores del cálculo:** make/model/year, **mileage**, **condition**, **equipment/options**, **región (postal code)**.
- **History-Adjusted:** capa analítica que cuantifica el impacto del historial VIN-específico (§3.4).
- **Actualización:** **diaria** ("updated daily from more sources than anyone else").
- **Volumen exacto** (nº total de data points / VINs / vehículos): **no publicado** más allá de "millones de
  registros al día" (EVM) y "cientos de subastas". `[NO-VERIFICADO]` un número duro agregado.

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web consumo** | `canadianblackbook.com` → "Value Your Vehicle" (trade-in gratuito, lead a dealers). |
| **API (REST + GraphQL)** | Developer Portal (`developer.canadianblackbook.com`): Used Car / New Car / Retail / Custom Trade Value / Residual / Retail Market Insights / RV / CPI / Connect. JSON & XML, GraphQL, "what if", query filtering. |
| **Batch / archivo** | **ValuEngine** (self-service, on-demand): CSV / delimitado; miles→millones de VINs por job. |
| **Apps móviles** | **Cherry** (iOS/Android, VIN scanner) `[plataformas no verificadas explícitamente para CBB]`; integraciones de terceros (Carbly, Laser Appraiser). |
| **Embebido en web de dealer** | **TradeMax** (widget de trade-in, ADF/CRM). |
| **Dashboard / analytics** | **Pulse** (visual analytics retail). |
| **Suscripción de libro** | Digital (online/móvil) + **impreso semanal**. |
| **Data feeds / licencia** | Datos licenciables/sublicenciables a empresas cualificadas vía web services, APIs y feeds. |
| **Integración DMS/CRM** | TradeMax ADF-compliant + compatible con la mayoría de CRM; datos integrables en sistemas de inventario y originación de préstamos. |

---

## 6. Precio

- **Sin tarifa pública canadiense.** Modelo = **licencia/suscripción B2B + "Buy Now"/contactar ventas**.
  Las soluciones de datos y apps "available for purchase with flexible solutions". (automotive-solutions.)
- **Portal de consumo:** **gratis** (se monetiza con **leads** a dealers — exige nombre/email/teléfono).
- **Canadian Black Book Financial:** monetiza vía partners financieros (lead/originación).
- **Referencia US (NO confirmada para Canadá, vía dealercue):** suscripción base **desde US$65/mes**; libro
  online/móvil/impreso **semanal**; **API y Visual Analytics cuestan extra**; Digital incluye History-Adjusted
  (accident history, past owners, factores históricos). `[NO-VERIFICADO para CBB Canadá]`

---

## 7. Placement (patrón web — clave para cardeep)

> Dónde coloca CBB cada dato. Esto es lo que cardeep imita para ubicar cada métrica.

**A. Portal de consumo "Value Your Vehicle" — flujo de 4 pasos** (verificado x2: clutch.ca + goauto.ca):
1. **Vehicle Details:** Year → Make → Model → **Trim** (selección encadenada).
2. **Location:** **Postal code** (ajuste regional).
3. **Additional Info:** **Odometer** + **Colour** + **Optional features/packages**.
4. **Contact Details:** nombre/email/teléfono (→ compartido con dealers participantes).
5. **Pantalla de resultado:** **Trade-in value** como **rango de precio** + nota de "current market trends".
   **Solo trade-in** — no muestra retail ni private. Condición **fija en media** (no editable). → *El dato de
   valor vive al final de un funnel de captación de lead, no en una ficha rica.*

**B. Ficha/herramienta de dealer (Cherry app):** los valores se presentan **juntos** — **wholesale + retail +
trade-in** del vehículo escaneado; debajo, bloque **Retail Market Insights** (days-to-turn · market days'
supply · average listing price) + **comparables cercanos** en un listado. Inventory discovery = lista
priorizada de "vehículos más deseables en subasta".

**C. Panel de mercado (Pulse):** vista de **segmentos** (creados del portfolio propio o del mercado CA);
filtros por vehículo/dealer/geografía; cada segmento muestra **Daily Vehicle Volume · Average Listing Mileage
· Days on Market** como KPIs apilados. → patrón "overview de mercado segmentable".

**D. Portfolio / collateral (ValuEngine):** tabla batch por VIN con **historical/current/projected residual a
nivel trim**; columnas de loss forecasting y flags de delinquency/risk. → patrón "tabla de cartera".

**E. Widget embebido (TradeMax):** caja de trade-in en la web del dealer, **rebrandeable** (logo/colores/
fuente), salida de lead a CRM vía ADF. → patrón "CTA de valoración white-label".

**F. Índice/inteligencia (UVRI):** página de índice con el **valor en puntos** + variación MoM/YoY + lectura
narrativa mensual; awards mostrados como **sellos/badges** por categoría (autoridad). → patrón "barómetro de mercado + badges de premio".

**G. Sensibilidad de residual:** controles para **ajustar MSRP / incentivos / rental penetration** y ver el
efecto en la curva de depreciación (Residual Sensitivity Analysis). → patrón "simulador what-if".

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad independiente #1 de usados en Canadá** (desde 1961), respaldo Hearst/National Auto Research.
2. **History-Adjusted Valuations VIN-específicas** — 9+ factores de historial (dueños, uso, siniestro+
   severidad, título, flood/hail/fire, CPO) → **+31% de precisión** vs subasta. Pocos rivales lo cuantifican.
3. **Enhanced Vehicle Matching (ML+NLP)** — ataca el problema del **30% de VINs ambiguos**, con add/deducts
   automáticos sobre **OEM build data**; "industry leader in trim decoding".
4. **Residual Sensitivity Analysis** — simulador de escenarios ajustando MSRP/incentivos/rental penetration.
5. **Used Vehicle Retention Index** — barómetro propio del mercado canadiense (2–6 años, % de MSRP, ponderado por matriculaciones).
6. **Ecosistema completo de entrega:** consumo (Value Your Vehicle) + dealer app (Cherry, VIN scanner) +
   widget (TradeMax) + analytics (Pulse) + batch (ValuEngine) + GraphQL/REST + libro impreso semanal.
7. **Proyecciones de residual 1–72 meses** con History Adjustments.
8. **Cobertura de colección/lujo (CPI) desde 1946** en fair/good/excellent.
9. **Actualización diaria** ("from more sources than anyone else").
10. **Brazo financiero propio** (Canadian Black Book Financial) — monetización vertical poco común en un puro proveedor de datos.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Canadá.** Sin Europa ni cobertura propia US bajo marca CBB. ← hueco para cardeep.
2. **No cubre motos/powersports** (es Canadian Blue Book) ni **heavy/medium-duty commercial** (a diferencia de la matriz US). Scope canadiense estrecho a cars/SUV/light-truck/van + CPI + RV.
3. **Portal de consumo pobre:** **solo trade-in** (no retail/private), **condición no editable** (asume media),
   y **exige datos personales** que se ceden a dealers (es un funnel de leads, no una herramienta de valor neutral).
4. **Tiers exactos de condición wholesale no públicos** — opacidad metodológica de cara al exterior.
5. **Precio opaco** (sin tarifa pública canadiense); fricción de ventas; tarifas conocidas son del Black Book US.
6. **Volumen de datos no divulgado** (sin cifra dura de data points/VINs/transacciones agregadas).
7. **Sin historial/provenance VIN propio expuesto al consumidor** (Carfax Canada domina ese espacio); HAV usa
   historial pero es producto B2B, no un report de historial al usuario final.
8. **No es catálogo de specs/equipamiento profundo** como producto estrella — el decode es soporte de la
   valoración, no un dataset técnico vendido aparte (vs Autovista/Chrome Data).
9. **Days-to-sell / market days' supply / DOM** están en herramientas pro (Cherry/Pulse/Retail Market Insights
   API), **no** en el portal de consumo → el consumidor no ve velocidad de mercado.
10. **Developer Portal y esquema atómico de la API tras login** — los campos exactos (nombres de tipos
    GraphQL, enums de condición) no son públicos. `[NO-VERIFICADO]` el contrato completo.

---

## 10. Fuentes

**Páginas propias CBB (leídas vía backend de WebSearch; el origin bloquea fetch directo):**
- Home: https://www.canadianblackbook.com/
- About (1961): https://www.canadianblackbook.com/about-canadian-black-book/
- APIs: https://www.canadianblackbook.com/api/
- Toolkit 5 APIs: https://www.canadianblackbook.com/toolkit-5-essential-apis-for-accurate-vehicle-valuation-and-risk-analysis-in-canada/
- Vehicle Values: https://www.canadianblackbook.com/vehicle-values/
- VIN Decoding: https://www.canadianblackbook.com/vin-decoding/ · Enhanced Vehicle Matching: https://www.canadianblackbook.com/enhanced-vehicle-matching/
- Automotive Solutions / Buy Now: https://www.canadianblackbook.com/automotive-solutions/
- Used Vehicle Retention Index: https://www.canadianblackbook.com/black-book-index/
- TradeMax: https://www.canadianblackbook.com/trademax/ · embed: https://trade.canadianblackbook.com/
- Cherry: https://www.canadianblackbook.com/cbb-cherry/ · Pulse: https://www.canadianblackbook.com/pulse/
- Auto Finance: https://www.canadianblackbook.com/autofinance/ · CBB Financial: https://listings.canadianblackbook.com/cbbf
- Value Your Vehicle: https://www.canadianblackbook.com/value-your-vehicle-2/
- Developer Portal: https://developer.canadianblackbook.com/ · Connect API: https://connect-api.canadianblackbook.com/
- Best Residual/Retained Value Awards: https://www.canadianblackbook.com/canadian-black-book-releases-first-ever-best-residual-value-awards/ ; https://www.canadianblackbook.com/cbb-best-residual-value-awards-highlight-shifting-market-dynamics-in-2026/

**Terceros / verificación (≥2 fuentes):**
- Ownership Hearst/National Auto Research/1955/Lawrenceville: https://en.wikipedia.org/wiki/Black_Book_(National_Auto_Research)
- HQ Markham + perfil: https://www.dnb.com/business-directory/company-profiles.canadian_black_book_inc.* ; https://www.zoominfo.com/c/canadian-black-book-inc/6471997
- Guía consumidor (value types, inputs, condición): https://www.clutch.ca/blog/posts/canadian-black-book
- Metodología/data sources: https://autocorp.ai/blog/canadian-black-book-vs-market-value-unveiling-the-nuances-of-car-pricing-in-canada
- Flujo "Value Your Vehicle" (placement): https://www.goauto.ca/tools-resources/how-to-use-canadian-black-book-to-maximize-your-trade-in-value
- ValuEngine: https://www.fi-magazine.com/323158/black-book-reveals-updated-valuengine-collateral-platform ; https://www.autoremarketing.com/subprime/black-book-unveils-next-generation-valuengine-platform/
- History-Adjusted (factores + 31%): https://digitaldealer.com/news/black-book-unveils-history-adjusted-vehicle-values-auto-professionals/ ; https://www.dealermarketing.com/articles/black-book-unveils-history-adjusted-vehicle-value-auto-professionals/
- Cherry app (Retail Market Insights, days-to-turn): https://www.autodealertodaymagazine.com/news/black-book-upgrades-cherry-mobile-app ; https://digitaldealer.com/everyone/black-book-announces-key-enhancements-to-black-book-cherry-mobile-app/
- Awards (4 años, 67,5%, categorías): https://www.guideautoweb.com/en/articles/80011/canadian-black-book-hands-out-2025-best-retained-value-awards/ ; https://media.toyota.ca/en/releases/2026/toyota-canada-recognized-by-canadian-black-book-with-multiple-20.html
- UVRI lectura marzo 2026: https://www.autoremarketing.com/arcanada/ (CBB index reports)
- Precio US (no confirmado CA): https://dealercue.com/2019/01/29/dealers-guide-black-book (vía snippet; el fetch directo falló)
- Distinción Blue Book (powersports): https://canadianbluebook.com/ · Red Book (competidor): https://www.canadianredbook.com/

### Notas de verificación
- Ownership Hearst/National Auto Research, 1955 (US) / 1961 (CA), Markham: **doble fuente** (Wikipedia + D&B/ZoomInfo + about). [VERIFICADO]
- Campos de Used Car Web API (price changes, days-to-turn, market days' supply, min/max/mean/median price+mileage): página `api/` + toolkit, leídas x2 vía WebSearch. [VERIFICADO]
- History-Adjusted: 9 factores + "+31% precisión": **triple fuente** (Digital Dealer + Dealer Marketing + Auto Remarketing). [VERIFICADO]
- Flujo de 4 pasos del portal de consumo + "solo trade-in" + condición fija: **doble fuente** (clutch + goauto). [VERIFICADO]
- UVRI fórmula (Wholesale Average, 2–6 años, %MSRP, ponderado por matriculaciones, ajuste edad/km/condición/inflación): página índice + Auto Remarketing. [VERIFICADO]
- Tiers exactos de condición wholesale CBB (Extra Clean/Clean/Average/Rough): **[NO-VERIFICADO]** — nomenclatura US, no confirmada idéntica en CA.
- Precio (US$65/mes base, API/Visual Analytics extra): **[NO-VERIFICADO para CBB Canadá]** — cifra de Black Book US vía dealercue.
- Volumen agregado de data points/VINs: **[NO-VERIFICADO]** (solo "millones de registros/día" en EVM).
- Plataformas exactas de la app Cherry (iOS/Android) para CBB: **[PARCIAL]** — confirmado como app móvil; las stores no verificadas 1:1.
