# CarOffer — Auditoría atómica

> Slug: `caroffer` · Subdominio cardeep: **wholesale-intelligence** · Región: **EE. UU.** (CarOffer = solo Estados Unidos; el marketplace matriz CarGurus opera además en Canadá y Reino Unido)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes independientes), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (cifra de marketing del propio vendedor sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato a partir de varias páginas sin que el vendedor lo liste literalmente), `[VERIFICADO por ausencia]` (afirmo que NO existe tras búsqueda exhaustiva).
> Naturaleza: **plataforma digital de comercio mayorista instantáneo dealer-to-dealer + consumer-to-dealer** ("the automotive industry's leading digital wholesale marketplace"), construida sobre la tecnología propietaria **BuyingMatrix™** (modelo "tipo bolsa de valores": órdenes permanentes de compra + ofertas instantáneas). NO es un libro de valor (KBB/Black Book) ni un valuador puro: es una **bolsa de inventario transaccional** con logística integrada (transporte + titulación + inspección + arbitraje) y una capa de **inteligencia de precios/mercado** que la sobrevive.
> **HECHO CAPITAL (clave para entender el caso):** CarGurus **cerró ("wound down") el negocio transaccional de CarOffer**. Anunciado el **7-ago-2025**; **"abandonado" a efectos contables el 31-dic-2025**. Lo que **sobrevive** y hereda el subdominio *wholesale/inventory intelligence* es la **capa de datos/analítica** (Dealer Data Insights, PriceVantage, Acquisition Insights) + el sourcing de consumidor **"Sell My Car – Top Dealer Offers"**. Por tanto esta auditoría documenta **(A)** el producto transaccional histórico (campos que ya no se transan pero definen el patrón) y **(B)** la capa de inteligencia viva que lo reemplaza. `[VERIFICADO ×3]`
> Owner / grupo: **CarGurus, Inc.** (Nasdaq: **CARG**), Boston, Massachusetts.
> Sitios/marcas: `caroffer.com` (producto histórico, hoy con aviso de cese de matches), `blog.caroffer.com`, `dealer.caroffer.com` (login), `dealers.cargurus.com/drc/caroffer` (página de dealer en CarGurus — **protegida por bot, HTTP 418**), `cargurus.com` (marketplace de consumidor), `investors.cargurus.com` (IR), `caroffer.com/dealercenter` (integración DealerCenter).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **CarOffer™** (a CarGurus company) | caroffer.com; globenewswire `[VERIFICADO]` |
| Owner / grupo | **CarGurus, Inc.** (Nasdaq **CARG**); CarGurus fundada 2006 por **Langley Steinert** (co-fundador de TripAdvisor), HQ **Boston, MA**; CEO CarGurus **Jason Trevisan** | Wikipedia CarGurus; cargurus/about `[VERIFICADO ×2]` |
| Fundación CarOffer | **2019** (plataforma lanzada **6-ago-2019**) | prnewswire (launch); globenewswire (finalize "Founded 2019") `[VERIFICADO ×2]` |
| Fundador | **Bruce T. Thompson** (Founder & CEO; dejó el cargo al completarse la adquisición) | prnewswire; globenewswire finalize `[VERIFICADO ×2]` |
| HQ | **Plano, Texas** (al lanzamiento 2019) → **Addison, Texas** (al cierre de adquisición 2023) | prnewswire launch (Plano); globenewswire finalize (Addison) `[VERIFICADO — dos fuentes, fechas distintas]` |
| CEO post-adquisición | **Zach Hallowell** (asumió al finalizar la compra, dic-2023) | globenewswire finalize `[PARCIAL — fuente oficial única]` |
| Naturaleza | **Marketplace mayorista digital** dealer-to-dealer + consumer-to-dealer, automatizado 24/7, con logística integrada | globenewswire; pymnts `[VERIFICADO]` |

**Cronología de propiedad y producto (timeline):**

| Fecha | Hito | Fuente |
|---|---|---|
| **6-ago-2019** | Lanzamiento de la "Instant Wholesale Trade Platform" (TradeGrade + Matrix + Instant Offers + 45-Day Guarantee). +1.000 ubicaciones comprometidas al lanzar | prnewswire `[VERIFICADO]` |
| **dic-2020 → ene-2021** | CarGurus **acuerda y cierra la compra del 51%** de CarOffer: **$173,2 M** ($103,6 M en acciones + $70,8 M en efectivo); **valoración empresarial ~$275 M** (enmendada después a **~$342 M** según SEC); opción de comprar el resto en 3 años | globenewswire (dic-2020); thebanksreport; autoremarketing `[VERIFICADO ×3]` |
| **may-2021** | "Dealer Enrollments Soar" — el inventario escaso dispara altas de concesionarios | globenewswire `[VERIFICADO]` |
| **2020-2021 (Group Trade)** | Lanza **Group Trade** (matrix a nivel multi-tienda; +2.000 rooftops en la red) | blog.caroffer; autosuccessonline `[VERIFICADO]` |
| **feb-2022** | **10.000 rooftops** de concesionario inscritos (~2,5 años tras lanzar BuyingMatrix) | globenewswire; dealers.cargurus `[VERIFICADO]` |
| **~2023 (Version 2.0)** | **CarOffer® Version 2.0**: 24 Hour With-a-Look, Set Floor Price, Buy-It-Now channel, inspección pre-compra (mecánica/eléctrica/motor); arbitraje −47 % YoY, titulación +30 %, transporte ~600 mi/~7 días | einpresswire; autoremarketing `[VERIFICADO ×2]` |
| **4-dic-2023** | CarGurus **completa la adquisición** del 100 %: **$75 M** por el interés minoritario restante (coste total acumulado ~**$215 M**) | globenewswire finalize; autobodynews; dealershipguy `[VERIFICADO ×3]` |
| **9-dic-2025** | Lanza **PriceVantage** (inteligencia predictiva de precios; capa que hereda el rol de "inteligencia") | globenewswire; digitaldealer `[VERIFICADO ×2]` |
| **7-ago-2025** | **Anuncia el cierre del negocio transaccional de CarOffer** (dealer-to-dealer + Instant Max Cash Offer). caroffer.com: *"As of Aug. 7, CarOffer is no longer processing new matches."* | investors.cargurus (Q2'25); autoremarketing; caroffer.com `[VERIFICADO ×3]` |
| **31-dic-2025** | Wind-down completado; negocio **"abandoned" a efectos contables**; coste total ~**$14–19 M** | autoremarketing; dealershipguy; pymnts `[VERIFICADO ×3]` |

**Categorías de producto:** (1) **Comercio mayorista dealer-to-dealer** (BuyingMatrix: buy/sell/trade); (2) **Venta instantánea / liquidación** (Instant Offer + 45-Day Guarantee + TradeGrade); (3) **Compra automatizada** (standing buy orders / limit orders + Buy-It-Now); (4) **Trade multi-tienda** (Group Trade); (5) **Sourcing de consumidor** (Instant Max Cash Offer → hoy "Sell My Car – Top Dealer Offers"); (6) **Logística integrada** (transporte + titulación + inspección + arbitraje); (7) **CAPA DE INTELIGENCIA (viva)**: IMV/Deal Rating, PriceVantage, Dealer Data Insights (Next Best Deal Rating, Max Margin, Merchandise Health, Acquisition Insights).

**Cliente objetivo:** **concesionarios** franquiciados e independientes y **grupos multi-tienda / 20 Groups** (compra/venta/trade mayorista); **consumidores particulares** (lado sourcing, vía Instant Max Cash Offer / Sell My Car). El comprador final del dato de inteligencia es el **used-car manager / GM** del concesionario.

---

## 2. Cobertura

- **Geografía:**
  - **CarOffer (transaccional) = solo EE. UU.** Red nacional de concesionarios; transporte nacional (avg ~600 millas). **Sin Canadá, sin Europa, sin LATAM.** `[VERIFICADO]`
  - **CarGurus marketplace (matriz) = EE. UU. + Canadá + Reino Unido** (algunas fuentes citan presencia histórica adicional en DE/IT, hoy reducida). `[VERIFICADO ×2]`
  - **Dealer Data Insights (capa viva):** ~**20.000 concesionarios en Norteamérica + Reino Unido** la usaban a Q3-2025. `[VERIFICADO ×2]`
- **Nuevo vs usado:** núcleo **USADO** (wholesale de seminuevos/usados). El marketplace CarGurus lista nuevo + usado, pero CarOffer y la inteligencia de adquisición/precio se centran en **usado**. `[VERIFICADO]`
- **Tipos de vehículo:** turismos, pickups y SUV de retail de concesionario (light vehicles). No comercial pesado/flota especializada. `[PARCIAL]`
- **Escala (transaccional, histórica):** **10.000+ rooftops** inscritos (feb-2022); **+2.000 rooftops** en contexto de Group Trade; **+1.000 ubicaciones** comprometidas ya en el lanzamiento (2019). `[VERIFICADO]`
- **Escala de señales (capa de inteligencia):** **>10.000 millones de "intent signals"/mes** (demanda de comprador + oferta de mercado) alimentan PriceVantage; CarGurus procesa **~500 millones de señales first-party de shopper al día** (media 2025). `[VERIFICADO ×2]`
- **Frescura:** **IMV recalculado a diario**; ofertas instantáneas 24/7; Deal Ratings actualizados automáticamente y sindicados a los IMS. `[VERIFICADO]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Estado |
|---|---|---|---|
| **BuyingMatrix™** | Bolsa "tipo stock market": órdenes permanentes de compra (limit orders) + ofertas instantáneas; casa compradores y vendedores 24/7 sin subasta física | Match precio + checkout instantáneo | Cerrado (transaccional) |
| **TradeGrade™** | Plataforma de puja integrada "point of appraisal" en tiempo real (tasación del trade-in del cliente) | Oferta/grado en el momento de la tasación | Cerrado |
| **Instant Offer / 45-Day Guarantee** | Oferta automatizada 24/7 de liquidación instantánea + oferta de venta garantizada a 45 días | Precio de venta instantáneo + garantía 45 días | Cerrado |
| **Buy-It-Now Channel** | Lista diaria de "cientos de vehículos frescos" para compra instantánea | Precio Buy-It-Now por VIN | Cerrado |
| **Group Trade** | BuyingMatrix a nivel multi-tienda (grupos / 20 Groups) | Oferta in-group en tiempo real al punto de tasación | Cerrado |
| **Instant Max Cash Offer → Sell My Car (Top Dealer Offers)** | Sourcing de consumidor: el particular vende online; la red de dealers puja | Mejor oferta de la red por el coche del consumidor | Reorientado (sobrevive como sourcing) |
| **Logística integrada** | Transporte + titulación + inspección pre-compra + arbitraje, en un bill of sale | Estado de transporte/título/inspección | Cerrado |
| **CarGurus IMV + Deal Rating** | Valor de mercado instantáneo + clasificación del precio del listado | IMV ($) + Deal Rating (5 niveles) | **VIVO** |
| **PriceVantage** | Inteligencia predictiva de precios por VIN basada en demanda real-time | Precio recomendado por objetivo de turn-time + forecast de leads | **VIVO** |
| **Dealer Data Insights (DDI)** | Suite de reportes: Next Best Deal Rating, Max Margin, Merchandise Health, Acquisition Insights | Recomendaciones de precio/merchandising/adquisición | **VIVO** |

### 3.1 BuyingMatrix™ — parámetros de la orden de compra (el núcleo transaccional)

> "Lets buying dealers create **standing buy orders** and provides **instant offers** to selling dealers… works much like today's stock market." El comprador define **qué coches quiere, en qué cantidad y a qué precio**, y la plataforma cumple la orden automáticamente.

| Campo / parámetro | Definición atómica | Fuente |
|---|---|---|
| **Standing buy order / limit order** | Orden permanente de compra estilo bursátil; el dealer fija condiciones y el sistema sourcing los vehículos que las cumplen | globenewswire; sec/IR `[VERIFICADO]` |
| **Desired price (límite)** | Precio máximo que el comprador está dispuesto a pagar por la unidad | globenewswire (snippet) `[PARCIAL]` |
| **Desired equipment / options** | Equipamiento/opciones exactas requeridas | globenewswire `[PARCIAL]` |
| **Desired mileage** | Rango de kilometraje/odómetro aceptado | globenewswire `[PARCIAL]` |
| **Desired condition** | Condición mínima del vehículo aceptada | globenewswire `[PARCIAL]` |
| **Quantity / quota** | Número de unidades a adquirir (cuota) | globenewswire `[PARCIAL]` |
| **Instant offer (match)** | Oferta instantánea que el sistema presenta al vendedor cuando su coche cruza con una orden | prnewswire; globenewswire `[VERIFICADO]` |
| **Buy-It-Now price** | Precio de compra inmediata en el canal Buy-It-Now (cientos de unidades frescas/día) | einpresswire; autoremarketing `[VERIFICADO]` |
| **Set Floor Price (reserve)** | Precio mínimo/reserva del vendedor; si no hay aprobación en 24 h, se reciben **follow-up bids por encima de la reserva**, gana la aprobación más alta | einpresswire; autoremarketing `[VERIFICADO]` |

### 3.2 TradeGrade™ + Instant Offer + 45-Day Guarantee (lado venta / tasación)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **TradeGrade™** | "Real-time, integrated **'point of appraisal' bidding platform**" — al tasar el trade-in del cliente, lanza la puja de la red para ese coche en el momento | prnewswire `[PARCIAL]` |
| **Instant inventory offer (24/7)** | Oferta automatizada disponible 24/7 para **liquidación instantánea** del inventario | prnewswire; globenewswire `[VERIFICADO]` |
| **45-Day Guaranteed Sell offer** | Oferta **opcional de venta garantizada a 45 días** (precio asegurado de salida) | prnewswire; caroffer.com/solutions/45-day-guarantee `[VERIFICADO]` |
| **Appraisal close ratio** | Métrica de resultado: los dealers "double their appraisal close ratio" usando TradeGrade | prnewswire `[CLAIM-VENDOR]` |

### 3.3 Identidad y condición del vehículo (inputs de la transacción)

`VIN` · `license plate` (lookup en flujo de consumidor) · `year` · `make` · `model` · `trim` · `mileage / odometer` · **`vehicle condition`** · **`condition report`** · `equipment / options` · `exterior/interior color` (implícito) · **`vehicle history report`** · **`vehicle photos`**. (Fuentes: caredge; cargurus press; einpresswire. `[VERIFICADO/PARCIAL]`)

### 3.4 24 Hour With-a-Look + inspección pre-compra (Version 2.0)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **24 Hour With-a-Look** | Ventana de **24 h** para que el comprador **revise condition report + vehicle history + photos** y apruebe la compra antes de que se procese automáticamente | einpresswire; autoremarketing `[VERIFICADO ×2]` |
| **Pre-purchase inspection — mechanical** | Inspección mecánica pre-compra (la mayoría de vehículos la reciben) | einpresswire; autoremarketing `[VERIFICADO ×2]` |
| **Pre-purchase inspection — electrical** | Análisis eléctrico pre-compra | einpresswire `[PARCIAL]` |
| **Pre-purchase inspection — engine analysis** | Análisis de motor pre-compra | einpresswire `[PARCIAL]` |
| **Arbitration rate** | Tasa de arbitraje (disputas post-venta); **−47 % YoY** en Version 2.0 | einpresswire; globenewswire finalize `[VERIFICADO ×2]` |

### 3.5 Logística integrada — campos atómicos

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Transportation / delivery** | Transporte nacional gestionado; **media ~600 millas en ~1 semana (~7 días)** | einpresswire; autoremarketing `[VERIFICADO ×2]` |
| **Title processing** | Obtención y procesado de título; **+30 % de mejora en tiempo** en Version 2.0 | einpresswire; globenewswire finalize `[VERIFICADO ×2]` |
| **Single bill of sale** | Transporte + titulación + inspección entregados en **un solo bill of sale** | globenewswire; blog.caroffer (group) `[VERIFICADO]` |
| **Instant buy fee** | **$350** de comisión de compra instantánea por transacción | WebSearch (caroffer.com/faq, snippet) `[PARCIAL]` |
| **Inspection fee** | **$149** de comisión de inspección por vehículo | WebSearch (caroffer.com/faq, snippet) `[PARCIAL]` |
| **Sin subscripción mensual** | Modelo **transaccional**, "without the burden of monthly subscription fees or contracts" | WebSearch (caroffer); autosuccessonline `[PARCIAL]` |

### 3.6 Group Trade — campos atómicos

| Campo | Definición atómica | Fuente |
|---|---|---|
| **In-group instant offer (point of appraisal)** | Ofertas in-group automatizadas **en tiempo real al punto de tasación** sobre todo el inventario del grupo | blog.caroffer; autosuccessonline `[VERIFICADO]` |
| **Central vs store-level control** | Las ofertas se gestionan/controlan **centralmente o a nivel de tienda** | blog.caroffer `[VERIFICADO]` |
| **Inter-group transfer bill-of-sale** | CarOffer agiliza toda la logística y los bill-of-sales de transferencia inter-grupo | blog.caroffer `[VERIFICADO]` |
| **Private trading platform (20 Groups)** | Group Trade puede construirse a medida para **tiendas no afiliadas** (plataformas de trading privadas tipo 20 Groups) | blog.caroffer `[VERIFICADO]` |
| **Buying-power optimization** | Maximiza poder de compra y optimiza demanda de vehículo entre ubicaciones | autosuccessonline `[VERIFICADO]` |

### 3.7 Instant Max Cash Offer / Sell My Car — campos atómicos (lado consumidor)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **VIN / license plate input** | El particular introduce VIN o matrícula + datos básicos | caredge; cargurus press `[VERIFICADO]` |
| **Mileage** | Kilometraje del vehículo del consumidor | caredge `[VERIFICADO]` |
| **Condition** | Condición declarada del vehículo | caredge `[VERIFICADO]` |
| **Multiple dealer offers (comparación)** | "Compare multiple offers in under 2 minutes": la red de dealers puja y el sistema casa con la **mejor oferta** (Buying Matrix selecciona la **highest buy offer**) | cargurus/sell-car; press IMCO `[VERIFICADO]` |
| **Highest buy offer** | Oferta más alta de la red, presentada al consumidor | cargurus press `[VERIFICADO]` |
| **Offer validity** | Oferta válida **7 días o +250 millas adicionales**, lo que ocurra primero | caredge `[PARCIAL]` |
| **On-the-spot inspection (pickup)** | Pago tras inspección rápida in situ en la recogida | caredge `[PARCIAL]` |
| **Eligibility flags (exclusiones)** | No elegibles: **branded title, daño extenso, alto kilometraje, antigüedad, exótico/raro, no conducible, sin interés local** | caredge `[PARCIAL]` |

### 3.8 CarGurus IMV + Deal Rating (CAPA DE INTELIGENCIA — VIVA)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Instant Market Value (IMV)** | **Precio retail justo estimado** de un vehículo, por análisis de **listados comparables actuales e históricos del mercado**; **recalculado a diario** con "millones de data points" | cargurus help (IMV); Wikipedia `[VERIFICADO ×2]` |
| **IMV inputs** | **make · model · trim · year · mileage · options · vehicle history** (+ mercado/geografía) | cargurus help (IMV); cardog (snippet) `[VERIFICADO]` |
| **Deal Rating** | Clasificación del precio del listado vs IMV en **5 niveles: Great Deal · Good Deal · Fair Deal · High Price · Overpriced** | cargurus help; Wikipedia `[VERIFICADO ×2]` |
| **Price vs IMV (%)** | Diferencia porcentual entre precio pedido e IMV que determina el Deal Rating (umbrales aprox.: Great ≥~10 % bajo IMV; Good ~5-10 % bajo; Fair ±pocos puntos; High ~5-10 % sobre; Overpriced >~10 % sobre — **umbrales NO publicados oficialmente**) | cardog (snippet) `[PARCIAL]` |
| **Dealer reputation/rating** | La reputación/valoración del concesionario **se factoriza** en el Deal Rating | cargurus help; WebSearch `[VERIFICADO]` |
| **Days on market / days on lot** | Días que el listado lleva en el mercado/lote (mostrado en la ficha) | WebSearch (listing fields) `[PARCIAL]` |
| **Price history / price drop** | Historial de precio y caídas de precio del listado | WebSearch (listing fields) `[PARCIAL]` |
| **Comparable listings (comp set)** | Conjunto de coches similares contra los que se posiciona el listado | WebSearch; cargurus help `[VERIFICADO]` |
| **Market average price** | Precio medio de mercado de comparables (referencia del IMV) | cargurus help `[PARCIAL]` |

### 3.9 PriceVantage (CAPA DE INTELIGENCIA — VIVA, lanzada dic-2025)

> "The only used vehicle pricing solution powered by **real-time consumer demand data**." Traduce **>10.000 M de intent signals/mes** en recomendaciones a medida del **objetivo de turn-time** del dealer (no solo "el siguiente Deal Rating").

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Price recommendation (turn-time-based)** | Precio recomendado por VIN, **alineado al objetivo de turn-time** del concesionario (no solo al Deal Rating) | globenewswire; digitaldealer `[VERIFICADO ×2]` |
| **Intent signals (>10 B/mes)** | Señales de intención: **demanda de shopper + oferta de mercado** | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Market days supply** | Días de oferta de unidades similares en el mercado local | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Local competition / competitor pricing** | Vista en tiempo real del precio de los competidores locales | globenewswire; digitaldealer `[VERIFICADO ×2]` |
| **Turn-time goal** | Objetivo individual de rotación que fija el dealer | globenewswire; digitaldealer `[VERIFICADO ×2]` |
| **Lead-potential forecast** | Previsión de **cómo un cambio de precio impacta el potencial de leads** (simular antes de aplicar) | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Shopper connections** | Conexiones de shopper = **text/chat leads + map clicks + website visits**; beta: **+71 % de media diaria** | digitaldealer; stocktitan `[VERIFICADO ×2]` |
| **Turn-time performance** | Beta: turn-times **5× más rápidos** que los top competidores | globenewswire; stocktitan `[VERIFICADO ×2]` |
| **VIN-level activity analysis** | Análisis de actividad a nivel VIN | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Missing vehicle details flag** | Marca detalles de vehículo faltantes para corrección instantánea | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Deal Rating auto-update** | Actualiza automáticamente los Deal Ratings (mantiene el rating) | globenewswire; stocktitan `[VERIFICADO ×2]` |
| **IMS syndication** | Sindicación directa a los **Inventory Management Systems** | globenewswire; digitaldealer; stocktitan `[VERIFICADO ×3]` |
| **Chrome extension overlay** | Extensión de Chrome que superpone la inteligencia PriceVantage en otras herramientas de workflow fuera de CarGurus | globenewswire; digitaldealer `[VERIFICADO ×2]` |

### 3.10 Dealer Data Insights (DDI) — los 4 reportes (CAPA VIVA)

> Suite de reportes que entrega **insights de precio a nivel VIN, forecasts de turn-time y benchmarking competitivo** dentro del workflow del dealer; impulsa ~**75 cambios de precio/inventario por dealer**.

| Reporte | Campo / salida atómica | Fuente |
|---|---|---|
| **Next Best Deal Rating** | Recomendación del **siguiente Deal Rating** alcanzable por VIN (qué precio mueve de Fair→Good→Great); en Q3 generó **>700.000 cambios de precio**, mediana **+48 % de VDP views** | WebSearch (Q4'25 updates) `[PARCIAL]` |
| **Max Margin** | Recomendación de precio que **maximiza el margen** por unidad; adopción **5.032 dealers** | WebSearch `[PARCIAL]` |
| **Merchandise Health** | Salud de **merchandising** del listado (completitud de fotos/datos); adopción **9.791 dealers** | WebSearch `[PARCIAL]` |
| **Acquisition Insights** | **Recomendaciones de qué make/model comprar** para rentabilidad en el mercado local + **turn-time estimado**; de los dealers que la usaron, **69 % adquirió los vehículos recomendados** y **65 % se vendió dentro del turn-time estimado** | WebSearch (Acquisition Insights); pymnts `[VERIFICADO]` |
| **Group-level reports** | Versiones a nivel grupo de Next Best Deal Rating, Max Margin y Merchandising Health | WebSearch (Q4'25) `[PARCIAL]` |

---

## 4. Metodología / fuentes de datos

- **BuyingMatrix™ (motor transaccional):** modelo "tipo bolsa" — **órdenes permanentes de compra (limit orders) + ofertas instantáneas**; el algoritmo **casa** la unidad del vendedor con la orden del comprador que mejor encaja, eliminando la puja manual y la subasta física. `[VERIFICADO]`
- **IMV (motor de valor):** análisis diario de **listados comparables actuales + históricos** en el mercado del usuario; pondera make/model/trim/year/mileage/options/vehicle history sobre "millones de data points". Es **retail-market-derived**, no un libro de tasador. `[VERIFICADO]`
- **PriceVantage / inteligencia (capa viva):** se nutre de la **demanda real-time del marketplace CarGurus** — **>10.000 M de intent signals/mes** y **~500 M de señales first-party de shopper/día**; cruza demanda de shopper × oferta de mercado para precio por VIN y forecast de leads/turn-time. **Ventaja propietaria:** el dato de demanda viene del propio marketplace de mayor tráfico, difícil de replicar por un valuador puro. `[VERIFICADO ×2]`
- **Condición/inspección (transaccional):** condition report + vehicle history + photos en la ventana 24 Hour With-a-Look; inspección pre-compra mecánica/eléctrica/motor; arbitraje como red de seguridad post-venta. `[VERIFICADO]`
- **Logística como dato:** transporte (~600 mi/~7 días), titulación (+30 % tiempo), todo en un bill of sale → el "estado logístico" es parte del registro de la transacción. `[VERIFICADO]`

(Fuentes: globenewswire; prnewswire; einpresswire; digitaldealer; cargurus help; pymnts.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web / SaaS (dealer)** | Plataforma CarOffer (login `dealer.caroffer.com`): dashboard de BuyingMatrix (órdenes), Instant Offer, Buy-It-Now channel, 24 Hour With-a-Look, Group Trade. **Página de dealer en CarGurus**: `dealers.cargurus.com/drc/caroffer` (**protegida por bot, HTTP 418** — no accesible a crawler). |
| **Portal web (consumidor)** | `cargurus.com/sell-car` (Instant Max Cash Offer / Sell My Car – Top Dealer Offers): flujo VIN/plate → ofertas → recogida. |
| **Marketplace de consumidor** | `cargurus.com`: ficha de coche con **IMV + Deal Rating + price history + days on market + comparable cars + dealer rating**. |
| **Integración DMS / IMS** | **DealerCenter** (`caroffer.com/dealercenter`, `support.dealercenter.net`); **sindicación directa a Inventory Management Systems** (PriceVantage); Deal Ratings auto-sindicados a los IMS. |
| **Extensión de navegador** | **Chrome extension** de PriceVantage: overlay de inteligencia de precio sobre otras herramientas del dealer. |
| **Reporting / Insights** | **Dealer Data Insights** (4 reportes en el dealer dashboard, además a nivel grupo); **CarGurus Intelligence Report** (informe de mercado periódico público para concesionarios). |
| **App móvil** | App CarGurus (consumidor): listings, IMV, Deal Ratings, Sell My Car. |
| **Logística** | Transporte + titulación + inspección gestionados por CarOffer (un bill of sale). |

> **API pública:** **no documentada/expuesta** para terceros. La integración es vía **DMS/IMS partners** (DealerCenter, sindicación a IMS) y la extensión Chrome, no una API REST abierta. `[VERIFICADO por ausencia]`

---

## 6. Precio

| Concepto | Precio | Fuente / nota |
|---|---|---|
| **Instant buy fee (CarOffer transaccional)** | **$350** por transacción | WebSearch (caroffer.com/faq, snippet) `[PARCIAL]` |
| **Inspection fee** | **$149** por vehículo | WebSearch (caroffer.com/faq, snippet) `[PARCIAL]` |
| **Modelo CarOffer** | **Transaccional / por operación**, "sin cuotas mensuales ni contratos" | autosuccessonline; WebSearch `[PARCIAL]` |
| **Transporte** | Coste de transporte adicional (no público; integrado en el bill of sale) | einpresswire `[PARCIAL]` |
| **Adquisición corporativa (referencia de valor)** | 51 %: **$173,2 M** (val. ~$275–342 M, ene-2021); resto: **$75 M** (dic-2023); **total ~$215 M** | thebanksreport; globenewswire; dealershipguy `[VERIFICADO]` |
| **PriceVantage / DDI** | **No público** — venta a concesionario por demo/cotización (parte del paquete de software de dealer de CarGurus) | globenewswire; investors.cargurus `[VERIFICADO por ausencia de tarifa pública]` |

> **Modelo:** el CarOffer histórico era **transaccional puro** ($350 buy fee + $149 inspección/coche, sin suscripción) — distinto de los SaaS por suscripción mensual (vAuto, AccuTrade). La capa de inteligencia (PriceVantage/DDI) sigue el modelo **software-de-dealer de CarGurus** (cotizado, no tarifado públicamente). `[PARCIAL]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca CarOffer/CarGurus **cada dato**. Reconstruido de PRs, páginas de producto, help docs y artículos. Patrón rector doble: **(transaccional)** "el mercado convertido en oferta ejecutable" — cada coche tiene una **oferta instantánea accionable**, no solo un valor; **(inteligencia)** "el dato pegado al listado y al workflow" — IMV/Deal Rating en la ficha, recomendación de precio en el IMS.

**A. Dashboard de BuyingMatrix (dealer, comprador).** Rejilla estilo "stock market" de **standing buy orders / limit orders**: cada fila = una orden con sus parámetros (**desired price, equipment, mileage, condition, quantity/quota**). El sistema rellena la orden automáticamente y muestra los **matches** entrantes con su **instant offer**. El **Buy-It-Now channel** es una lista paralela de "cientos de vehículos frescos/día" con **precio Buy-It-Now** por VIN. `[RECONSTRUIDO]`

**B. Pantalla de venta / tasación (dealer, vendedor — TradeGrade).** En el **punto de tasación** del trade-in del cliente, TradeGrade lanza la puja de la red y devuelve la **oferta instantánea** + la opción de **45-Day Guarantee** (precio de salida garantizado). El dealer fija un **Set Floor Price (reserva)**; si no aprueba en 24 h, entran **follow-up bids** por encima de la reserva. `[RECONSTRUIDO]`

**C. Panel 24 Hour With-a-Look (comprador, pre-cierre).** Antes de procesar la compra, un panel de revisión de 24 h presenta **condition report + vehicle history + photos** + resultado de **inspección pre-compra** (mecánica/eléctrica/motor). Botón aprobar/declinar; si no se actúa, se procesa solo. `[VERIFICADO]`

**D. Checkout / transacción (logística).** El registro de la operación muestra **buy fee ($350) + inspection fee ($149) + transporte (~600 mi/~7 días) + estado de titulación + arbitraje**, todo consolidado en **un bill of sale**. `[RECONSTRUIDO]`

**E. Group Trade (multi-tienda).** Vista de grupo: **oferta in-group en tiempo real al punto de tasación** sobre todo el inventario; control **central o por tienda**; los transfers inter-grupo se liquidan con bill-of-sale unificado. `[VERIFICADO]`

**F. Flujo Sell My Car / Instant Max Cash Offer (consumidor).** Pantalla 1: entrada de **VIN/matrícula + mileage + condition**. Pantalla 2: **comparación de múltiples ofertas de dealers** ("en menos de 2 minutos") con la **highest buy offer** destacada; **validez 7 días/+250 mi**. Recogida + **inspección in situ** → pago. **Flags de elegibilidad** bloquean coches con branded title/daño/exótico/no conducible. `[VERIFICADO]`

**G. Ficha de coche del marketplace (consumidor, cargurus.com).** El **IMV** y el **Deal Rating** (badge: Great/Good/Fair/High/Overpriced) encabezan el precio; debajo, **days on market/lot, price history (con price drops), comparable cars y dealer rating**. Es el patrón "valor + veredicto de precio" pegado al listado. `[VERIFICADO]`

**H. PriceVantage en el workflow del dealer.** Por VIN: **precio recomendado** alineado al **turn-time goal**, junto a **market days supply, competencia local y forecast de lead-potential** (deslizador "si bajo X el precio, los leads/turn-time hacen Y"). Marca **missing vehicle details**. Se **sindica al IMS** y se superpone vía **extensión Chrome** en otras herramientas. `[VERIFICADO]`

**I. Dealer Data Insights (reportes).** Reportes separados en el dashboard del dealer (y a nivel grupo): **Next Best Deal Rating** (qué precio sube de rating, +48 % VDP views), **Max Margin** (precio de margen máximo), **Merchandise Health** (completitud del listado), **Acquisition Insights** (qué make/model comprar + turn-time estimado por mercado local). `[PARCIAL]`

**J. Reporting de mercado (público).** Fuera de la ficha: **CarGurus Intelligence Report** periódico (tendencias de inventario, precio, demanda, EV/híbridos) para concesionarios. `[VERIFICADO]`

---

## 8. Diferencial (lo que ofrece y otras no)

1. **De "valor" a "oferta ejecutable".** A diferencia de un libro de valor (KBB/Black Book) o un valuador (vAuto/AccuTrade), CarOffer convertía el dato de mercado en una **transacción instantánea real**: el coche no solo "vale X", se **vende/compra ya** vía BuyingMatrix. Modelo "stock-market" de **limit orders + instant offers**. `[VERIFICADO]`
2. **Logística end-to-end integrada** (transporte ~600 mi/~7 días + titulación +30 % + inspección pre-compra mecánica/eléctrica/motor + arbitraje −47 %), todo en **un bill of sale** — pocas plataformas de dato cubren la entrega física. `[VERIFICADO]`
3. **Dato de demanda propietario del marketplace #1 de tráfico.** PriceVantage/IMV se alimentan de **>10.000 M de intent signals/mes** y **~500 M de señales de shopper/día** del propio CarGurus — señal de **demanda real-time** que un valuador sin marketplace no tiene. `[VERIFICADO]`
4. **Precio por objetivo de turn-time, no por "deal rating" genérico** (PriceVantage): recomienda el precio que cumple **el objetivo de rotación del dealer** y **simula el impacto en leads** antes de aplicar. `[VERIFICADO]`
5. **Sourcing de consumidor a escala** (Instant Max Cash Offer / Sell My Car): casa el coche del particular con la **highest buy offer** de la red de dealers automáticamente. `[VERIFICADO]`
6. **Group Trade / plataformas privadas (20 Groups):** matrix multi-tienda con control central/tienda — capa enterprise para grandes grupos. `[VERIFICADO]`
7. **Entrega del dato dentro del workflow:** IMV/Deal Rating en la ficha de consumidor + sindicación a IMS + **extensión Chrome** que sobreimprime la inteligencia en otras herramientas. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece)

1. **El negocio transaccional está CERRADO.** El núcleo (BuyingMatrix dealer-to-dealer + Instant Max Cash Offer transaccional) fue **wound down** (anuncio 7-ago-2025; abandonado 31-dic-2025). Hoy CarOffer **no procesa nuevos matches**: el diferencial #1 y #2 ya **no operan**. Lo que queda es la **capa de inteligencia + sourcing de consumidor**. `[VERIFICADO ×3]` ← contexto decisivo para cardeep.
2. **Solo EE. UU.** (CarOffer); el marketplace matriz añade Canadá + Reino Unido, pero **sin Europa continental, sin LATAM, sin Asia**. ← hueco mayor para cardeep. `[VERIFICADO]`
3. **No es libro/autoridad de valor citable** tipo KBB/Black Book/J.D. Power: IMV es un **valor de mercado retail derivado de listados**, no una guía de tasador con cobertura histórica por trim/año independiente. `[VERIFICADO]`
4. **Sin valor residual / forecast de depreciación multi-anual** ni curva de leasing (a diferencia de ALG/Autovista/J.D. Power): horizonte = **precio de mercado AHORA**, no previsión a años. `[VERIFICADO por ausencia]`
5. **Vehicle history NO propio**: usa report de historial de terceros dentro de la ventana de revisión; no es un proveedor de historial tipo Carfax/AutoCheck. `[PARCIAL]`
6. **Sin diagnóstico OBD-II / telemetría** en la tasación (a diferencia de AccuTrade); la condición es condition report + inspección humana. `[VERIFICADO por ausencia]`
7. **Sin API pública documentada** para terceros; integración cerrada a DMS/IMS partners + extensión Chrome. `[VERIFICADO por ausencia]`
8. **Umbrales del Deal Rating no publicados** oficialmente (Great/Good/Fair/High/Overpriced); los % son estimaciones de terceros. `[PARCIAL]`
9. **Páginas de producto bloqueadas/retiradas:** `dealers.cargurus.com/drc/caroffer` devuelve **HTTP 418** (anti-bot); `cargurus.com` también 418; las subpáginas de producto de `caroffer.com` (FAQ, solutions, trade-inventory) devuelven **404** tras el wind-down → varios campos transaccionales finos quedan **[PARCIAL]** (no confirmables a doble fuente hoy). `[NOTA DE MÉTODO]`
10. **Enumeración fina de fees/transporte** no publicada de forma estable (el $350+$149 viene de snippet de la FAQ, no de página viva verificable hoy). `[PARCIAL]`

---

## 10. Fuentes

**Oficiales / IR / producto (CarGurus · CarOffer):**
- CarOffer home (aviso wind-down "no longer processing new matches"): https://www.caroffer.com/
- Blog CarOffer (Group Trade press release): https://blog.caroffer.com/pressrelease01/07 · index: https://blog.caroffer.com
- DealerCenter integration: https://www.caroffer.com/dealercenter · https://support.dealercenter.net/hc/en-us/articles/4416347864212-Using-CarOffer-in-DealerCenter (403)
- Dealer CarGurus (CarOffer): https://dealers.cargurus.com/drc/caroffer (**HTTP 418, bloqueado**) · PriceVantage dealer: https://dealers.cargurus.com/pricevantage (**bloqueado**)
- Sell My Car (consumidor): https://www.cargurus.com/sell-car (**418**) · IMV one-pager (PDF): https://assets.ctfassets.net/0czyc7nlfvzo/4f2pymo70GTJ6EqnoMB7GO/d50c19b3b16a83f71e4b7e35075f46c3/CarGurus-IMV-one-pager.pdf (binario, no parseable)
- IMV help doc: https://cargurus.helpscoutdocs.com/article/10-what-is-imv
- Investor Relations: https://investors.cargurus.com/ · Q2'25 wind-down: https://investors.cargurus.com/news-releases/news-release-details/cargurus-announces-second-quarter-2025-results-shares-plans-wind

**Prensa / wire (verificación cruzada):**
- Lanzamiento 2019 (TradeGrade, Matrix, Instant Offers, 45-Day Guarantee, Bruce Thompson, Plano TX): https://www.prnewswire.com/news-releases/caroffer-launches-new-instant-wholesale-trade-platform-designed-to-reverse-current-margin-compression-trend-300896743.html · https://www.autosuccessonline.com/caroffer-launches-new-instant-wholesale-trade-platform-designed-to-reverse-current-margin-compression-trend/
- Acuerdo 51 % (dic-2020): https://www.globenewswire.com/news-release/2020/12/10/2142934/0/en/CarGurus-Agrees-to-Acquire-a-Majority-Stake-in-Instant-Trade-Platform-CarOffer.html · cierre 51 %: https://www.autoremarketing.com/ar/technology/cargurus-completes-deal-buy-51-stake-caroffer/
- Términos/valoración ($173,2 M; ~$275-342 M): https://thebanksreport.com/vendor-acquisitions/cargurus-to-acquire-remaining-minority-interest-in-caroffer-following-a-somewhat-choppy-ride/
- 10.000 rooftops (feb-2022): https://www.globenewswire.com/news-release/2022/02/15/2385352/0/en/CarGurus-Subsidiary-CarOffer-Reaches-a-Major-Milestone-of-10-000-Enrolled-Dealer-Rooftops-on-its-Industry-Leading-Inventory-Trading-Platform.html
- Dealer enrollments soar (2021): https://www.globenewswire.com/news-release/2021/05/21/2234145/0/en/CarOffer-s-Dealer-Enrollments-Soar-as-its-Instant-Used-Vehicle-Trading-Platform-Provides-Much-Needed-Inventory-Supply.html
- Group Trade: https://www.autosuccessonline.com/caroffer-group-trade-platform-optimize-profitability-automate-inventory-management-across-multiple-stores/ · https://www.prnewswire.com/news-releases/caroffers-new-group-trade-platform-helps-dealers-optimize-profitability-and-automate-inventory-management-across-multiple-stores-301202471.html
- Version 2.0 (24 Hour With-a-Look, Set Floor Price, Buy-It-Now, inspección, arbitraje −47 %, título +30 %, 600 mi/7 días): https://www.einpresswire.com/article/659148618/caroffer-version-2-0-offers-significant-operational-improvements-for-wholesale-vehicle-buyers-and-sellers · https://www.autoremarketing.com/ar/caroffer-announces-revamped-version-2-0-platform/
- Adquisición completa $75 M (dic-2023): https://www.globenewswire.com/en/news-release/2023/12/04/2790085/0/en/CarGurus-Finalizes-Acquisition-of-CarOffer.html · https://www.autobodynews.com/news/cargurus-completes-75m-acquisition-of-caroffer
- Wind-down (Aug-2025, abandono 31-dic-2025, ~$215 M total): https://www.autoremarketing.com/ar/wholesale/cargurus-to-wind-down-caroffer-before-year-end/ · https://news.dealershipguy.com/p/cargurus-is-phasing-out-its-caroffer-transactions-business-2025-08-08 · https://aimgroup.com/2025/08/08/cargurus-shuts-down-caroffer-18-months-after-acquiring-it/
- Estrategia AI SaaS post-CarOffer: https://www.pymnts.com/earnings/2026/cargurus-exits-wholesale-platform-to-go-all-in-on-ai-saas/
- PriceVantage (campos completos): https://www.globenewswire.com/news-release/2025/12/09/3202412/0/en/PriceVantage-CarGurus-Latest-AI-Powered-Solution-Brings-Predictive-Intelligence-to-Vehicle-Pricing-Decisions.html · https://digitaldealer.com/news/cargurus-introduces-pricevantage-to-bring-predictive-ai-to-used-car-pricing/168866/ · https://www.stocktitan.net/news/CARG/price-vantage-car-gurus-latest-ai-powered-solution-brings-predictive-iiv81cy1fvm5.html

**Consumidor / terceros / referencia:**
- Sell My Car / Instant Max Cash Offer (VIN/plate, validez 7 días/250 mi, elegibilidad): https://caredge.com/guides/best-instant-cash-offer-websites · https://www.cargurus.com/Cars/articles/reviewing-instant-cash-offers-for-car · IMCO press: https://www.cargurus.com/press/consumers_can_sell_vehicles_100_online_cargurus_instant_max_cash_offer.html
- Corporativo CarGurus (2006, Langley Steinert, Boston, CARG, US/CA/UK, CEO Trevisan): https://en.wikipedia.org/wiki/CarGurus
- IMV / Deal Rating thresholds (estimaciones terceros): https://cardog.app/blog/how-cargurus-works · https://cardog.app/blog/is-cargurus-accurate
- LinkedIn CarOffer: https://www.linkedin.com/company/caroffer

### Notas de verificación
- **Fundación 2019 / Bruce Thompson / lanzamiento 6-ago-2019:** prnewswire + globenewswire. **[VERIFICADO]**. **HQ: Plano (2019) → Addison (2023)** — dos fuentes oficiales con sede distinta por fecha; documentado como evolución, no contradicción.
- **Adquisición 51 % $173,2 M (~$275-342 M) ene-2021 + $75 M resto dic-2023 (~$215 M total):** globenewswire + thebanksreport + autoremarketing + dealershipguy. **[VERIFICADO ×3]**
- **Wind-down (7-ago-2025; abandono contable 31-dic-2025; ~$14-19 M coste):** investors.cargurus + autoremarketing + pymnts + dealershipguy. **[VERIFICADO ×3]** — HECHO CAPITAL.
- **BuyingMatrix / limit orders / instant offers / 10.000 rooftops / Group Trade:** múltiples wire + IR. **[VERIFICADO]**
- **Version 2.0 (24 Hour With-a-Look, Set Floor Price, Buy-It-Now, inspección mec/elec/motor, arbitraje −47 %, título +30 %, 600 mi/7 días):** einpresswire + autoremarketing + globenewswire finalize. **[VERIFICADO ×2]**
- **PriceVantage (10 B intent signals, market days supply, lead-potential forecast, VIN-level, IMS syndication, Chrome ext., 5× turn, +71 % shopper connections):** globenewswire + digitaldealer + stocktitan. **[VERIFICADO ×3]**
- **IMV + Deal Rating (5 niveles, inputs make/model/trim/year/mileage/options/history, daily, dealer reputation):** cargurus help + Wikipedia + cardog. **[VERIFICADO]**. Umbrales % del rating: **[PARCIAL]** (no oficiales).
- **DDI 4 reportes + cifras de adopción (9.791 / 5.032 / 700k cambios / +48 % VDP / 69 %-65 % Acquisition):** WebSearch (Q4'25 updates + Acquisition Insights). **[PARCIAL]** salvo Acquisition Insights y "20.000 dealers DDI" que cruzan con pymnts/globenewswire → **[VERIFICADO]**.
- **Fees $350 buy + $149 inspección, sin suscripción:** snippet de WebSearch citando caroffer.com/faq (hoy 404). **[PARCIAL]**.
- **Buy-order params (price/equipment/mileage/condition/quota):** snippet globenewswire. **[PARCIAL]**.
- **exa MCP:** NO disponible en el entorno (ToolSearch "exa…" no devolvió la herramienta). Investigación con **WebSearch + WebFetch + Playwright**. **[NOTA DE MÉTODO]**
- **Bloqueos de acceso:** `dealers.cargurus.com` y `cargurus.com` devuelven **HTTP 418** (anti-bot) tanto vía WebFetch como vía Playwright (`ERR_HTTP_RESPONSE_CODE_FAILURE`); `web.archive.org` no accesible vía WebFetch; `sec.gov` 403; subpáginas vivas de `caroffer.com` (faq/solutions/trade-inventory) **404** tras wind-down. Campos finos del producto transaccional → **[PARCIAL]** donde no hubo segunda fuente.
