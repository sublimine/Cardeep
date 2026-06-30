# Auditoría atómica — CarGurus (CarGurus.co.uk / CarGurus.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos e inteligencia de automoción B2B2C**: el **marketplace de coches usado+nuevo más visitado de EE.UU.** (también Canadá y UK), construido sobre un **algoritmo propietario de pricing — Instant Market Value (IMV)** que estima el precio justo de retail de cada coche y deriva un **Deal Rating** (Great/Good/Fair/High/Overpriced) impreso en cada anuncio. El IMV ordena los resultados de búsqueda y se vende a los concesionarios como **inteligencia de pricing, sourcing y demanda** (Pricing Tool, PriceVantage, Market Analysis, Acquisition Insights, Dealer Data Insights, Digital Deal). El negocio es **suscripción de dealer** (≈92% de los ingresos). Web del scope (audit): **https://www.cargurus.co.uk/** (mercado UK) + matriz US **https://www.cargurus.com/**.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **portal-insights** (etiqueta de categoría = "portal/marketplace con brazo de insights", NO un host DNS verificado).
> Fecha auditoría: 2026-06-30. Método: navegación de cargurus.co.uk (home, price-trends, research/car-valuation, sell-my-car, about/dealer-pricing-policy) + datasheets oficiales en PDF (CarGurus-IMV-one-pager.pdf 2018, US Digital Deal FAQs.pdf 2022, leídos byte-a-byte) + help docs oficiales (helpscoutdocs US + UK) + SEC/10-K + earnings releases (FY2024, Q1/Q2/Q3 2025) + prensa (Automotive News, AIM Group, Auto Remarketing, Motor Trader, GlobeNewswire) + Wikipedia + perfiles de parsers (Carapis, Apify, webscraper.io) para cross-check de campos de listing.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **CarGurus** (+ submarcas independientes **PistonHeads** UK, **Autolist** US, **CarOffer** US en wind-down) | [V] |
| Razón social | **CarGurus, Inc.** (cotizada **NASDAQ: CARG**, Class A) | [V] |
| Categoría | **Marketplace/portal de anuncios de coche (usado+nuevo) con motor de pricing propietario (IMV) y brazo de inteligencia de mercado B2B para dealers.** Compite con Auto Trader (UK), Cars.com/CarMax/AutoTrader (US), iSeeCars, TrueCar. No es guía editorial de valores (KBB/Black Book) ni proveedor de datos API-first puro (MarketCheck). | [V] |
| Fundación | **2006** (Cambridge, Massachusetts) | [V — Wikipedia + S-1 + Grokipedia] |
| Fundador | **Langley Steinert** (co-fundador de **TripAdvisor**); CEO hasta **enero 2021** | [V] |
| CEO actual | **Jason Trevisan** (ex-CFO, CEO desde **enero 2021**) | [V — Wikipedia] |
| HQ | **Boston, Massachusetts** — **1001 Boylston Street** (nueva sede global de 225.000 sq ft inaugurada **oct-2024**, unifica ~1.000 empleados de dos oficinas de Cambridge) | [V] |
| IPO | **12-oct-2017**, NASDAQ **CARG**, ~**$150M** captados | [V — Wikipedia] |
| Ingresos | **FY2024 ≈ $894M** (−2% YoY); **Marketplace ≈ 92% del top-line** y creciendo doble dígito; **Digital Wholesale (CarOffer) en declive** | [V — earnings release + AIM Group] |
| Empleados | ~**1.000** en HQ Boston (cifra de la sede 2024); plantilla global mayor (no consolidada exacta) | [V parcial / A] |
| Submarcas / M&A | **PistonHeads** (clasificados/comunidad entusiasta UK, adquirida **2018/2019**) · **Autolist** (app de shopping US, **2020**) · **CarOffer** (plataforma instant-trade wholesale US; participación mayoritaria cerrada **ene-2021**, 100% en **2023**, **wind-down decidido ago-2025**) | [V — con discrepancia de fechas, ver Gaps] |

### Hitos / cronología [V]
- **2006** Fundación en Cambridge MA por Langley Steinert.
- **dic-2015** Lanza en **Reino Unido** (primera incursión europea); en 2015 ya superaba **15M usuarios únicos/mes** y **6.000 dealers** en US.
- **2016-2019** Expansión a **Canadá, Alemania, Italia, España** (planes también Francia).
- **2017** IPO en NASDAQ (CARG).
- **2018/2019** Adquiere **PistonHeads** (UK).
- **abr-2020** **COVID:** recorta **13% de la plantilla** y **cierra Alemania, Italia y España**; Canadá y UK quedan como únicos mercados internacionales. Adquiere **Autolist** (US).
- **ene-2021** Cierra participación mayoritaria en **CarOffer** (instant trade wholesale); Jason Trevisan → CEO.
- **2023** Completa el 100% de **CarOffer**.
- **27-jun-2024** **Retira los anuncios de particular (private listings)** en US y UK → **marketplace 100% dealer**.
- **oct-2024** Nueva sede global en Boston (1001 Boylston St).
- **ago-2025** El Board decide **wind-down de CarOffer** (Dealer-to-Dealer + Instant Max Cash Offer); 101 despidos, cierre oficina Dallas, coste $14-19M, completado en H2-2025. Conserva **tecnología y analítica** de CarOffer, abandona la parte física (inspección, entrega, arbitraje, garantías de precio).
- **dic-2025** Lanza **PriceVantage** (pricing predictivo con IA para dealers).

### Clientes objetivo (segmentos) [V/A]
1. **Concesionarios (dealers)** — cliente que PAGA (≈92% de ingresos): suscripción de listing + herramientas de pricing/sourcing/demanda + leads. [V]
2. **Compradores de coche (usado/nuevo/CPO)** — núcleo de tráfico B2C; consumen IMV + Deal Rating gratis. [V]
3. **Vendedores particulares** — vía **Sell My Car / Instant Offer** (oferta de la red de dealers/partner); ya **no pueden listar** su coche directamente desde jun-2024. [V]
4. **Grupos de dealer / OEM** — programas de marketing, Digital Deal, datos de demanda. [A/V]
5. **Lenders / F&I providers** — integrados en Digital Retail (Capital One, Westlake, GLS, AutoFi, PEN). [V]
6. **Prensa / analistas / mercado** — consumen **CarGurus Index, Demand Index, Intelligence Report, Consumer Insights Report**. [V]

---

## 2. Cobertura

### Geográfica [V]
- **Estados Unidos** (marca CarGurus + **Autolist**) — mercado principal y matriz del producto.
- **Canadá** (marca CarGurus, **cargurus.ca**).
- **Reino Unido** (marca CarGurus **cargurus.co.uk** + **PistonHeads**) — **mercado del scope de esta auditoría**.
- **Salió de Alemania, Italia y España en abril 2020** (COVID). El hint del orquestador "multi-country EU" está **DESACTUALIZADO**: hoy NO hay cobertura DE/IT/ES; solo US, CA, UK. [V — Motor Trader + AIM Group + Automotive News]

### Escala (cifras divulgadas) [V]
- **~41M visitantes únicos medios/mes** (Q3 2025, US; era ~42M Q3 2024) — **el sitio de anuncios más visitado de EE.UU.** (ruptura de metodología GA→GA4 en jun-2024, no comparable hacia atrás).
- **32.372 dealers de pago globales** (Q1 2025; +1.197 YoY).
- **QARSD (Quarterly Average Revenue per Subscribing Dealer) = $9.442** (Q1 2025; +9,0% YoY) — KPI central del negocio.
- Agrega listings de **40.000+ dealer partners** en Norteamérica; **>20% más inventario medio mensual** que el competidor siguiente.
- **>5 millones de data points** por cálculo de IMV (datasheet 2018; hoy "millones"); **10.000 millones (10B+) de señales de intención/mes** alimentan PriceVantage.
- **~20.000 dealers** (US+UK) usando los **Dealer Data Insights** a Q3 2025.

### Scope de vehículos [V]
- **Coches usados + nuevos + certificados (CPO)**. Filtro de condición: **New / Used / Certified Pre-Owned**.
- Body styles (UK): **Convertible, Coupe, Estate, Hatchback, MPV, Pickup Truck, Saloon, SUV/Crossover, Van** (+ categorías curadas: small & sporty, eco-friendly, automatic, seven-seater, affordable 4x4, great first cars, dog-friendly, fuel-efficient).
- **Sin** motos, RV, comercial pesado ni maquinaria como verticales propias. **Solo turismos/ligeros.** [V/A]

---

## 3. Productos + campos atómicos

Arquitectura **marketplace web/app + dashboard de dealer + datasets de inteligencia**. Bloques: (A) Marketplace consumer + IMV/Deal Rating, (B) Car Values (valoración), (C) Sell My Car / Instant Offer, (D) Price Trends / Índices, (E) Dealer: Pricing Tool + PriceVantage, (F) Dealer: Market Analysis / Acquisition Insights / Dealer Data Insights, (G) Digital Deal (retail digital), (H) Listing packages + Top Rated Dealer, (I) CarOffer wholesale (wind-down), (J) Reports de inteligencia.

### — BLOQUE A: MARKETPLACE CONSUMER + IMV / DEAL RATING —

### 3.1 Instant Market Value (IMV) — el motor [V]
**"Estimated fair retail price for a vehicle based on a detailed analysis of comparable current and previous car listings in your market."** Calculado y **actualizado a diario** con un algoritmo propietario sobre **>5M data points**. **Inputs del modelo (diagrama oficial del datasheet):** `make` · `model` · `trim` · `mileage` · `options` · `region` (mercado local) · `history` (historial del vehículo). El IMV (1) determina el **Deal Rating**, (2) **ordena los resultados de búsqueda** (mejores deals arriba), (3) alimenta la valoración consumer y el trade-in de Digital Deal.

### 3.2 Deal Rating — badge por anuncio [V]
Se compara `asking_price` vs `IMV` **factorizando la reputación del dealer**. Cinco niveles:
- **Great Deal** (verde) — precio muy por debajo del IMV (≈≥10% bajo mercado). [V label; umbral A]
- **Good Deal** (verde claro) — moderadamente por debajo (≈5-10%). [V label; umbral A]
- **Fair Price / Fair Deal** (amarillo) — en torno al IMV. [V]
- **High Price** (naranja) — por encima (≈5-10%). [V label; umbral A]
- **Overpriced** (rojo) — muy por encima (≈>10%). [V label; umbral A]
- **Visual:** badge + flecha + **barra de gradiente verde→amarillo→naranja→rojo** con un marcador que sitúa el precio del coche dentro del espectro de mercado. Los umbrales exactos **no se publican** (varían por categoría/precio/mercado). **80% de los leads van a Fair/Good/Great.**

### 3.3 Campos de la tarjeta de anuncio (SRP) y ficha (VDP) [V — datasheet + help docs + parsers]
**Tarjeta / ficha del vehículo:**
- `CarGurus Instant Market Value™` (ej. "$30,884") — el valor de referencia.
- `price` / asking price (ej. "$29,100").
- `New Price` / original price — precio anterior tras bajada (price drop).
- **`Savings`** — diferencia vs IMV (ej. "$2,471"); en datos de parser: **`priceDifferential`**, **`expectedPrice`** (=IMV), **`dealScore`**, **`dealRating`**, **`imvPrice`**.
- **`price_history`** — historial de cambios de precio del propio anuncio. [V help doc]
- **`days_listed`** — "how long a vehicle has been listed" / *time on the forecourt* (UK). [V]
- `mileage` (ej. "26,799 mi").
- `year` · `make` · `model` · `trim`.
- `body_type` · `exterior_colour` · `interior_colour` · `condition` (New/Used/CPO) · `VIN` · `stock_number`.
- `engine` · `fuel_type` · `transmission` · `drivetrain`.
- **`options` / features** (ej. "Navigation System, Bluetooth, Leather Seats") — alimentan el IMV y los filtros.
- `photo_gallery`.
- **`vehicle_history`** — issues marcados, vía **AutoCheck.com** (Experian). [V help doc]
- **Dealer:** `dealer_name` · `dealer_rating` (estrellas) · `review_count` · `reviews` (texto) · `website` · `phone` · `address`/location · badge **Top Rated Dealer**.
- **Payment Calculator** (financiación estimada): `monthly_payment`, inputs `down_payment` · `APR` · `loan_term` · `credit_score` band. [V help doc]
- **Chat** 24/7 (representante CarGurus) en algunos anuncios. [V]

**Métricas visibles al DEALER sobre su anuncio (datasheet IMV):** `Search Rank` ("22 out of 436 based on this search") · `Search Page` ("2") · `Total Saves` ("12") · `Total Connections` (leads) · `VDP views`.

**Filtros de búsqueda (SRP):** make/model/trim/year · price · mileage · **Deal Rating** · body type · condition (New/Used/CPO) · colour · fuel · transmission · drivetrain · options/features · postcode + radio · dealer rating. **Orden por defecto: mejores Deal Ratings primero** ("unbiased sorting", no pay-to-rank). [V]

### — BLOQUE B: CAR VALUES (VALORACIÓN CONSUMER) —

### 3.4 Car Values / "What's My Car Worth" (`/research/car-valuation`) [V]
**Inputs:** `registration`/number plate (UK) **o** `VIN` **o** manual (`make`, `model`, `year`, `trim`, `mileage`, `zip/postcode`, opciones). **Outputs** (basados en IMV, actualizados a diario):
- **Instant Market Value (IMV)** — precio de **retail** (lo que se pagaría en concesionario).
- **Private Sale Value / Private Sale Estimate** — venta a particular.
- **Trade-in Value** — lo que ofrecería un dealer al cambiarlo (típicamente menor).

### — BLOQUE C: SELL MY CAR / INSTANT OFFER —

### 3.5 Sell My Car / Instant Offer (`/sell-my-car`) [V]
**Inputs:** `registration`/license plate o `VIN` + `mileage`. **Output:** **`instant_cash_offer`** de la red de dealers, en **<2 min**. UK: liquidación vía partner **The Car Buying Group** (recogida + pago el mismo día). US: **Instant Max Cash Offer (IMCO)** (impulsado por CarOffer, **en wind-down** desde ago-2025). El consumidor **ya no puede listar privately** desde jun-2024.

### — BLOQUE D: PRICE TRENDS / ÍNDICES (inteligencia pública) —

### 3.6 Price Trends / CarGurus Index (`/Cars/price-trends/`) [V]
Herramienta pública de tendencias de precio. **Por make / model / body style, columnas exactas:**
- **`Avg. price`** (£/$).
- **`Last 30 days`** (% cambio).
- **`Last 90 days`** (% cambio).
- **`Year over year`** (% cambio).
- (ej. fila real: "Honda £11,738 −6.81% −24.71% −13.98%").
- **`Shop now`** — enlace al SRP filtrado.
- **Biggest decrease (30 días)** y **Biggest increase (30 días)** — top movers, para makes y para models.
- **Export de datos + gráficos custom** por rango de fechas y tipo de vehículo.

### 3.7 Índices de mercado [V]
- **CarGurus Index** — precio medio agregado del usado (ej. US $27,311), con deltas 30d/90d/YoY; publicado para **UK y US**.
- **CarGurus Vehicle Demand Index** — demanda de usado MoM y YoY.
- **Availability Index** — niveles de inventario/oferta del mercado.
- **Market days supply** — días de oferta, desglosable por combustible (ej. híbrido 46,8 / gasolina 74,7 / BEV 85,3 / PHEV 97,7 días).

### — BLOQUE E: DEALER — PRICING TOOL + PRICEVANTAGE —

### 3.8 CarGurus Pricing Tool [V — datasheet]
Herramienta del Dealer Dashboard. Por cada unidad del inventario muestra:
- **`IMV`** del vehículo + **`Deal Rating`** actual.
- **"Exactly what it would take to make a listing a Great, Good, or Fair Deal"** — umbrales de precio por nivel de deal.
- Oportunidades de **subir precio sin bajar de nivel de deal** (maximizar margen sin perder ranking).
- `Search Rank` · `Search Page` · `VDP views` · `Total Saves` · `Total Connections`.
- Acción **"mark as sold"** (retira de búsquedas; inventario se sincroniza cada 24h vía feed).

### 3.9 PriceVantage (lanzado dic-2025) — pricing predictivo con IA [V]
Traduce **>10B señales de intención/mes** (demanda de shoppers + oferta de mercado) en recomendaciones:
- **VIN-level price change recommendation** — ajuste de precio recomendado **atado al objetivo de turn time** del dealer (no solo al siguiente Deal Rating).
- **`market_days_supply`** (oferta local).
- **Real-time competitor pricing** (precios de la competencia local).
- **`comparable_listings`** + **IMV lookup**.
- **Forecast del impacto en lead potential** de un cambio de precio **antes de aplicarlo**.
- **IMS syndication** (sincroniza precios al Inventory Management System del dealer).
- **Chrome browser extension** que superpone la inteligencia PriceVantage sobre otras herramientas del flujo.
- Resultados citados: turn times **5×** más rápidos; **+71%** de conexiones diarias.

### — BLOQUE F: DEALER — SOURCING / DEMANDA / INSIGHTS —

### 3.10 Market Analysis [V]
Decisiones data-driven de **qué comprar y promocionar** según **lo que los consumidores buscan en su mercado** (demanda por make/model/segmento + oferta). Pestaña del Dashboard.

### 3.11 Acquisition Insights / Dealer Data Insights [V]
- **Recomendaciones de adquisición de inventario** para mejorar **turn time**, basadas en **actividad del mercado local**.
- Desgloses por **región**, **segmento de precio**, **combustible**, y **recomendaciones de vehículos** concretos.
- Datos propietarios de **demanda y oferta** del consumidor para sourcing. **~20.000 dealers** (US+UK) los usan (Q3 2025).

### — BLOQUE G: DIGITAL DEAL (RETAIL DIGITAL) —

### 3.12 Digital Deal [V — FAQ PDF oficial 2022]
Permite al shopper **construir el deal online** (trade-in + financiación + cita) antes de pisar el concesionario. Campos atómicos:
- **Trade-in:** inputs `make` · `model` · `year` · `trim` · `mileage` · `zip` → **trade-in value vía IMV** (estimado, sujeto a inspección).
- **Payment Calculator:** `down_payment` · `credit_score` band · `APR` · `loan_term` → `monthly_payment`.
- **F&I products** (recomienda 3-5): **VSC** (Vehicle Service Contract), **GAP**, **Tire & Wheel** — precios vía **PEN (Provider Exchange Network)** / `eRating`, VIN- y deal-specific, sobre `dealer_cost` + markup (flat o rate-based).
- **Financiación pre-qualification (soft pull):** **GLS, Westlake, Capital One**.
- **Hard-pull credit application** (powered by **AutoFi**): Bank of America, Chase, US Bank, Huntington, Exeter, Regional Acceptance, Santander, Truist, TD Auto Finance, Westlake, Wells Fargo, ACA **+ 33 captive lenders**. Routing por reglas (dealer+lender logic, **payment-to-income ratio**, **credit score threshold**). Ventana de 14 días = una sola inquiry.
- **Custom APR** (sin credit check, manual).
- **Sale price components:** `down_payment` + `dealer_fees` + `title_&_registration_fees` + `taxes` + `delivery_fee`. Taxes/DMV calculados por **tool de terceros** según location del dealer + zip del shopper.
- **Reservation deposit** = **$500** vía **Stripe** (fee 2,4%; posible captura de $15); payout al dealer el lunes tras 5 días.
- **Lead types en CRM (vía ADF):** `CarGurus – Deposit – Digital Deal` · `CarGurus – Hard Pull – Digital Deal` · `CarGurus – Soft Pull – Digital Deal` · `CarGurus – Appt – Digital Deal` · `CarGurus – Digital Deal`.
- **Integraciones:** CRM (ADF) · **RouteOne / Dealertrack** (credit apps) · PEN (F&I) · AutoFi (hard pull) · Stripe (deposits).
- **Area Boost** — vender fuera del mercado local (hasta +120% leads). **Finance in Advance™** — feature de pre-financiación. Leads Digital Deal cierran **2-5×** más.
- Roles del Dashboard: Dashboard/Digital Retail administrator · Deposit Manager · Deposit Admin.

### — BLOQUE H: LISTING PACKAGES + TOP RATED DEALER —

### 3.13 Listing packages (suscripción de dealer) [V parcial]
- **Restricted** — listing **gratis**, leads **anonimizados** limitados.
- **Enhanced** — el más popular: más leads, **contacto completo**, branding del dealer en la VDP.
- **Featured+ / Featured Priority+** — exposición **garantizada en SRP** + incluye **Digital Deal**.
- (UK: paquete **CarGurus + PistonHeads** combinado.) Detalle exacto de cada tier no público; precio por inventario+mercado+features (§6).

### 3.14 Top Rated Dealer / Top Dealer Awards [V]
- **Rating de dealer 1-5★** por reseñas verificadas de la comunidad (post-lead).
- Award: **≥5 reseñas** + **media ≥4,5★** en los **últimos 12 meses** + análisis de datos de listing.
- Reseña = star rating + comentario; aparece en las VDP del dealer y en su showroom page. Badge on-site + placa física.

### — BLOQUE I: CAROFFER (WHOLESALE — WIND-DOWN ago-2025) —

### 3.15 CarOffer (plataforma instant-trade dealer-to-dealer) [V — histórico/en cierre]
- **Buying Matrix™** — el dealer comprador crea **standing buy orders / limit orders / quotas** definiendo `pricing` · `equipment` · `mileage` · `condition`; el sistema **machea automáticamente** ofertas a inventario.
- **Instant offer al vendedor** + **checkout tipo carrito**.
- **TradeGrade** (extensión) — ver y aceptar ofertas instantáneas sobre trade-ins, lease returns y auction cars **desde la herramienta de tasación**.
- **Instant Max Cash Offer (IMCO)** — oferta cash al consumidor (sell 100% online).
- **Dealer-to-Dealer (D2D)**, **garantía de venta ~45 días** [A — histórico].
- **ago-2025: wind-down** de D2D + IMCO (se abandona inspección/entrega/arbitraje/garantías; se conserva tecnología y analítica). El segmento **Digital Wholesale** se apaga.

### — BLOQUE J: REPORTS DE INTELIGENCIA —

### 3.16 Reports públicos / dealer-facing [V]
- **CarGurus Consumer Insights Report** — anual (8ª edición 2025), encuesta a **3.000+** compradores/vendedores recientes (comportamiento, digital, personalización).
- **CarGurus Intelligence Report** — **mensual/trimestral**, dealer-facing: tendencias de demanda/oferta, days-supply por combustible, segmento de precio, breakdowns regionales, recomendaciones de vehículos.
- **CarGurus Index / Demand Index / Availability Index** (§3.7).

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = agregación de listings de dealers (feeds cada 24h) + scoring algorítmico propietario (IMV), NO panel editorial ni transaccional.** Desde jun-2024 **solo inventario de dealer** (sin particulares).
- **IMV**: comparables **actuales + previos** del mercado local; **>5M data points** por cálculo; **actualizado a diario**; inputs make/model/trim/mileage/options/region/history. Es **estimación de retail**, declarado **no tasación oficial ni garantía**.
- **Deal Rating** = `asking_price` vs `IMV` + **reputación del dealer** → Great/Good/Fair/High/Overpriced; **ordena el SRP**.
- **Demanda**: **>10B señales de intención/mes** (búsquedas, VDP views, conexiones) → PriceVantage, Demand Index, Market/Acquisition Insights.
- **Historial de vehículo**: **AutoCheck.com (Experian)** — proveedor de terceros, no propio.
- **Financiación/F&I**: rates reales vía **PEN** (F&I) y **AutoFi** (hard pull); APRs agregadas + doc fees regionales por defecto.
- **Neutralidad declarada**: orden "unbiased", el ranking depende del algoritmo "**not how much a dealer pays us**".

---

## 5. Entrega
- **Portal web** consumer (cargurus.co.uk / .com / .ca) + **apps móviles** (CarGurus; Autolist; PistonHeads) — rating 4,85★. [V]
- **Dealer Dashboard** (web + **app móvil "CarGurus Dealer"**): secciones **Dashboard Homepage · VDP Activity · Dealer Insights · Pricing Tool · Market Analysis · Digital Deal · Settings/Reviews/Reports**. [V]
- **CSV export** de Leads / VDP Activity / Removed Listings (con columna `Type`: New/Used/CPO). [V]
- **Chrome browser extension** (PriceVantage). [V]
- **IMS syndication** (precios al Inventory Management System del dealer). [V]
- **CRM via ADF** + **RouteOne / Dealertrack** (credit apps) + **PEN** (F&I) + **AutoFi** + **Stripe** (deposits). [V]
- **Deal Rating Badges Service** — badges embebibles en la web del dealer (con permiso). [V]
- **Reports** (PDF/blog/press): Consumer Insights, Intelligence Report, Index. [V]
- **API pública de datos**: **no documentada como producto self-service**; el dato se entrega "cocinado" (IMV, deal rating, insights, dashboard). Parsers de terceros (Carapis/Apify) scrapean las VDP. [V/A]

---

## 6. Precio
**Consumer = GRATIS** (búsqueda, IMV, Deal Rating, valoración, price trends). **Monetización = suscripción de DEALER** (≈92% de ingresos). [V]
- **QARSD ≈ $9.442/trimestre** por dealer suscrito (Q1 2025) — métrica oficial; el precio escala por **tamaño de inventario + competitividad del mercado geográfico + features/tier**. [V]
- **Tiers:** Restricted (free, leads anónimos) → Enhanced → Featured+ / Featured Priority+ (con Digital Deal + SRP garantizado). [V — nombres; detalle de precio no público]
- Algunos modelos cobran **por lead** en vez de flat mensual. [V]
- **Digital Wholesale (CarOffer)**: ingresos por transacción (fees de compra/venta D2D + IMCO) — **en cierre**. [V]
- UK: línea de ventas dealer **0800 808 5557**; durante lockdowns 2020-21 ofreció **suscripciones gratis** a dealers UK. [V]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: mapeo pantalla/sección → dato.

### Tarjeta de anuncio (SRP) — listado de resultados [V]
- **Badge Deal Rating** (Great/Good/Fair/High/Overpriced) **junto al precio** — elemento visual dominante; los mejores deals **ordenados arriba**.
- `price` (grande) + `New Price` tachado (price drop) + **`Savings` vs IMV**.
- foto + `year+make+model+trim` + `mileage` + location + `days_listed` + estrellas del dealer.

### Ficha del vehículo (VDP) — página de detalle [V]
- **Bloque "Price Analysis":** `CarGurus Instant Market Value` + **barra de gradiente verde→rojo** con marcador del precio + Deal Rating + `priceDifferential`.
- **`price_history`** (gráfico/log de cambios de precio) + **`days_listed`**.
- **Specs**: make/model/trim/year, body, colores, VIN, stock, engine, fuel, transmission, drivetrain, **options/features**.
- **`vehicle_history`** (AutoCheck) — sección propia con issues marcados.
- **Payment Calculator** (monthly payment; sliders down payment / term) — bloque de financiación.
- **Dealer**: nombre, **estrellas + review count + reseñas**, badge **Top Rated Dealer**, contacto/location, **Chat 24/7**.

### Pantalla de valoración (Car Values) [V]
- Tres cifras: **IMV (retail)** arriba, **Private Sale Value**, **Trade-in Value** — input por matrícula/VIN/manual.

### Sell My Car / Instant Offer [V]
- Input matrícula+mileage → **instant cash offer** (<2 min) + CTA recogida/pago mismo día.

### Price Trends — inteligencia pública [V]
- **Tabla**: filas make/model con columnas `Avg. price` · `Last 30 days` · `Last 90 days` · `Year over year` + `Shop now`.
- **Bloques "Biggest decrease / Biggest increase (30 días)"** (makes y models) destacados arriba.
- **CarGurus Index** como cabecera agregada.

### Dealer Dashboard — la inteligencia como producto B2B [V]
- **Pricing Tool / PriceVantage**: lista de inventario con IMV + Deal Rating + **recomendación de precio (VIN-level) atada a turn time** + `market_days_supply` + competidores + forecast de leads. Acción "mark as sold".
- **VDP Activity**: views/saves/connections por unidad + `Search Rank`/`Search Page`.
- **Market Analysis / Acquisition Insights**: qué buscan los consumidores en el mercado + recomendaciones de qué comprar (turn time, región, segmento, combustible).
- **Digital Deal tab**: deal jackets (trade-in, F&I, financiación, cita, deposit); leads tipados en CRM.
- **Reviews/Reports**: gestión de reseñas + descargas CSV.

### Reports / Índices [V]
- Páginas y PDFs de **Index / Demand Index / Intelligence Report / Consumer Insights** — autoridad de marca + SEO + lead-gen de dealer.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **IMV + Deal Rating de 5 niveles con barra de gradiente verde→rojo en CADA anuncio**, que además **ordena el SRP** ("unbiased sorting") — pricing transparente y accionable, gratis, a escala de 40k+ dealers y ~41M visitantes/mes. Patrón de UI icónico del sector.
- [V] **El MISMO motor (IMV) se vende como inteligencia B2B**: Pricing Tool muestra al dealer "qué precio lo hace Great/Good/Fair Deal" — convierte el rating consumer en herramienta de pricing del lado oferta.
- [V] **PriceVantage**: pricing predictivo con IA sobre **10B señales de intención/mes**, recomendación VIN-level **atada a turn time** + forecast de impacto en leads **antes de aplicar** + Chrome extension + IMS syndication. Pocos integran demanda real de shoppers a esta escala.
- [V] **Digital Deal end-to-end** (trade-in IMV + F&I vía PEN + soft/hard-pull AutoFi con 45+ lenders + deposit Stripe + leads tipados en CRM/RouteOne/Dealertrack) — retail digital completo integrado al marketplace.
- [V] **Acquisition Insights / Market Analysis**: sourcing basado en **demanda real de consumidor** (no solo oferta wholesale) — qué comprar para mejorar turn time.
- [V] **Triple índice público** (CarGurus Index de precio + Vehicle Demand Index + Availability Index) en **UK y US** + Intelligence Report mensual + Consumer Insights anual — autoridad de mercado y SEO.
- [V] **Marketplace multi-país (US/CA/UK) + submarcas** (PistonHeads entusiasta, Autolist mobile) bajo un mismo motor de pricing.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Solo US, Canadá y UK.** Sin Alemania/Italia/España (salió 2020) ni resto de Europa — **el hint "multi-country EU" es falso hoy**; irrelevante directo para cobertura ES de Cardeep salvo como patrón UI.
- [V] **No es proveedor de datos API-first self-service**: sin API pública documentada, sin bulk feeds/SFTP comerciales; el dato se entrega "cocinado" (IMV/rating/insights/dashboard). Terceros scrapean las VDP.
- [V] **No publica matrices editoriales de valor** (trade/retail/wholesale por trim normalizadas tipo KBB/Black Book/Glass's): da un **IMV predicho + 3 vistas (retail/private/trade-in)**, no tablas de referencia auditables.
- [V] **Sin valores residuales / forecasting de RV** para leasing/flotas; sin **TCO / running costs / SMR** (mantenimiento, tiempos de reparación, precios de pieza).
- [V] **Historial de vehículo dependiente de terceros** (AutoCheck/Experian) — no hay informe de siniestros/propietarios/km propio tipo Carfax/HPI.
- [V] **Marketplace solo-dealer desde jun-2024**: ya **no admite anuncios de particular**; el particular solo puede vender vía Instant Offer (a dealer/partner).
- [V] **Wholesale apagándose**: con el **wind-down de CarOffer (ago-2025)** desaparecen D2D + Instant Max Cash Offer + inspección/entrega/arbitraje/garantía; queda solo tecnología/analítica.
- [V] **Umbrales del Deal Rating no publicados** ("proprietary"); IMV "no es tasación ni garantía".
- [A] **No expone specs profundas de catálogo/equipamiento normalizado por trim** (tipo JATO/Autovista/DataOne); las options vienen del feed del dealer, con calidad variable.
- [A] **Métricas de scale mezcladas** (visitantes US vs dealers globales; ruptura GA→GA4 jun-2024) — no hay un dato único consolidado y datado.
- [V] **Pricing de dealer opaco** al público: QARSD es el único número oficial; los precios de tier no se publican.

---

## 10. Fuentes (URLs)
- https://www.cargurus.co.uk/ — home UK: nav (Buy used, Car values, Test drive reviews, Price trends, Discover, Advertise), categorías y body types, 6M+ buyers, app 4,85★, "unbiased sorting".
- https://assets.ctfassets.net/0czyc7nlfvzo/4f2pymo70GTJ6EqnoMB7GO/d50c19b3b16a83f71e4b7e35075f46c3/CarGurus-IMV-one-pager.pdf — **datasheet IMV oficial (2018)**: definición IMV, inputs (make/model/trim/mileage/options/region/history), >5M data points, daily, Deal Rating Great/Good/Fair, Pricing Tool, tarjeta con IMV/Price/New Price/Savings/Total Saves/Search Rank "22 of 436"/Search Page/Total Connections + barra gradiente.
- https://dealer.cargurus.com/rs/365-ECK-512/images/USDigitalDealFAQs.pdf — **Digital Deal FAQ oficial (2022)**: trade-in inputs, F&I (VSC/GAP/tire&wheel) vía PEN, soft-pull (GLS/Westlake/Capital One), hard-pull AutoFi (BoA/Chase/US Bank/Huntington/Exeter/Regional Acceptance/Santander/Truist/TD/Westlake/Wells Fargo/ACA +33 captive), sale price components, deposit $500 Stripe, 5 lead types en CRM/ADF, RouteOne/Dealertrack.
- https://cargurus.helpscoutdocs.com/article/10-what-is-imv — IMV oficial: "estimated fair retail price… comparable current and previous car listings", daily, Great/Good/Fair/High/Overpriced, "not an official appraisal".
- https://cargurus.helpscoutdocs.com/article/228-vehicle-history-and-negotiation — VDP: Vehicle History (AutoCheck), Days Listed, Price History, Price Analysis Tool, Dealer Reviews, Payment Calculator, Chat 24/7.
- https://www.cargurus.co.uk/research/car-valuation — Car Values UK: input matrícula/VIN/manual → IMV (retail) + Private Sale + Trade-in, actualizado a diario.
- https://www.cargurus.com/research/car-valuation — valoración US: IMV retail + Private Sale Estimate + Trade-in Value.
- https://www.cargurus.co.uk/Cars/price-trends/ — Price Trends: columnas Avg. price / Last 30 days / Last 90 days / Year over year + Biggest decrease/increase + Shop now + export.
- https://www.cargurus.com/research/price-trends — CarGurus Index US ($27,311), deltas 30/90/YoY.
- https://dealers.cargurus.com/pricevantage y https://investors.cargurus.com/news-releases/news-release-details/pricevantage-cargurus-latest-ai-powered-solution-brings — PriceVantage: 10B señales/mes, VIN-level recommendation atada a turn time, market days supply, competidores, comparables, IMV lookup, IMS syndication, Chrome extension, +71% conexiones / 5× turn time.
- https://dealers.cargurus.com/drc/pricing-to-your-market-how-to-use-the-cargurus-pricing-tool-to-move-more — Pricing Tool (deal rating thresholds).
- https://dealers.cargurus.com/blog/command-your-local-market-with-cargurus-market-analysis y .../cargurus-intelligence-report* — Market Analysis, Acquisition Insights, Dealer Data Insights (~20k dealers), days-supply por combustible.
- https://www.cargurus.co.uk/sell-my-car y research/articles/car-valuation-explained — Sell My Car / Instant Offer UK (reg+mileage → cash offer <2 min; partner The Car Buying Group).
- https://www.cargurus.com/about/top-dealer-awards y https://www.cargurus.com/Cars/articles/best-car-dealer-awards — Top Rated Dealer: ≥5 reseñas, ≥4,5★, verificadas 12 meses.
- https://dealer.cargurus.com/enhanceden.html, https://products.cargurus.com/welcome-to-restricted, https://dealers.cargurus.com/listings — tiers Restricted/Enhanced/Featured+/Featured Priority+.
- https://www.cargurus.co.uk/about/dealer-pricing-policy — política de pricing (precios full cash, no condicionales) + Deal Rating Badges Service.
- https://cargurus-uk.helpscoutdocs.com/article/567-discontinuation-of-private-listings-on-cargurus — **retirada de private listings 27-jun-2024 → marketplace solo-dealer**.
- https://investors.cargurus.com/news-releases/news-release-details/cargurus-announces-second-quarter-2025-results-shares-plans-wind y https://aimgroup.com/2025/08/08/cargurus-shuts-down-caroffer-18-months-after-acquiring-it/ y https://www.autonews.com/retail/an-cargurus-caroffer-layoffs-underway-0828/ — **wind-down CarOffer (ago-2025)**: D2D + IMCO, 101 despidos, $14-19M, H2-2025.
- https://en.wikipedia.org/wiki/CarGurus — identidad: fundación 2006 Langley Steinert (TripAdvisor), HQ Boston, IPO 12-oct-2017 CARG $150M, CEO Jason Trevisan desde ene-2021, M&A PistonHeads/Autolist/CarOffer, mercados US/CA/UK.
- https://www.motortrader.com/.../cargurus-pulls-plug-businesses-germany-spain-italy-17-04-2020 y https://www.autonews.com/dealers/cargurus-cut-13-global-work-force-exit-some-european-markets/ — **salida DE/IT/ES + 13% layoffs (abr-2020)**.
- https://www.sec.gov/Archives/edgar/data/1494259/000104746917005904/a2233230zs-1.htm y FY2024/Q1-Q3 2025 earnings — financials: ~$894M FY2024, Marketplace ~92%, QARSD $9.442 (Q1'25), 32.372 dealers, ~41M visitantes/mes.
- https://www.cargurus.com/press/20150318.html — histórico 2015: 15M usuarios/mes, 6.000 dealers.
- Cross-check de campos de listing: https://carapis.com/parsers/cargurus.com/intro, https://apify.com/lexis-solutions/cargurus-com, https://webscraper.io/marketplace/cargurus-vehicles-listings-scraper, https://github.com/rebrowser/carguruscom-dataset (expectedPrice, priceDifferential, dealScore, dealRating, imvPrice, specs, dealer rating/reviews).

> Verificación: identidad corporativa contrastada con ≥3 fuentes (Wikipedia + SEC S-1/10-K + earnings + prensa). Campos de IMV/Deal Rating/Pricing Tool [V] **leídos del datasheet PDF oficial** (byte-a-byte). Campos de Digital Deal [V] **leídos del FAQ PDF oficial 2022**. Valoración, price trends y private-listings [V] de páginas .co.uk navegadas. Wind-down CarOffer y salida europea [V] por prensa especializada (AIM Group, Automotive News, Motor Trader) + investor relations. Campos de listing cross-checados con 4 proveedores de parsing independientes. Umbrales exactos del Deal Rating y precios de tier marcados como **no públicos**; el hint "multi-country EU" del orquestador **corregido a US/CA/UK** (DE/IT/ES cerrados 2020). Cifra de ingresos de Wikipedia (FY2025 $841,5M) no usada como primaria por ambigüedad (revenue vs gross profit); se reporta FY2024 ≈$894M de earnings release.
