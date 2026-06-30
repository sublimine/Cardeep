# Cars Commerce (Cars.com Inc.) — Auditoría atómica

> Slug: `cars-commerce` · Subdominio cardeep: **portal-insights** · Región: **Norteamérica** (EE. UU. núcleo + Canadá)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[V]` = verificado (≥2 fuentes o fuente oficial leída), `[V1]` = una sola fuente, `[A]` = asumido/inferido (marcado siempre), `[CLAIM]` = cifra de marketing del propio vendedor.
> Naturaleza: **plataforma conectada de comercio de automoción** que **NO es un proveedor de datos/feeds tipo guía de valor**, sino un **marketplace de consumo (Cars.com) + SaaS para concesionario (Dealer Inspire) + tasación/adquisición (AccuTrade) + subasta mayorista (DealerClub) + red de medios (Media Network) + reputación (DealerRater) + fintech (CreditIQ)**. Su "dato" se monetiza **embebido en productos** (suscripción de dealer, publicidad, transacción), no como API/feed crudo.
> Empresa cotizada: **Cars.com Inc., NYSE: CARS**. Marca comercial B2B desde oct-2023: **Cars Commerce**.
> Sitios: `carscommerce.inc` (B2B/plataforma), `cars.com` (marketplace consumidor), `dealerrater.com` (reseñas), `dealerclub.com` (subasta), `accu-trade.com`/`galves.com` (tasación → ver fichero **accu-trade.md**), `investor.cars.com` (IR).
> **Nota de relación con cardeep**: el subdominio `portal-insights` agrupa marketplaces + inteligencia de mercado. Cars Commerce es el arquetipo **portal de consumo + insights de industria** de Norteamérica (análogo a Auto Trader UK / CarGurus / Edmunds / TrueCar). AccuTrade tiene fichero propio (`accu-trade.md`); aquí se referencia sin re-duplicar su esquema completo.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca comercial (B2B) | **Cars Commerce** | [V] |
| Razón social / emisor | **Cars.com Inc.** (NYSE: **CARS**) | [V] |
| Rebrand a "Cars Commerce" | **17-oct-2023** — "the first connected platform for automotive that spans **pretail, retail and post-sale**"; unifica Cars.com, Dealer Inspire, FUEL, DealerRater, CreditIQ y Accu-Trade.com bajo una marca B2B | [V — investor.cars.com + Auto Remarketing] |
| Fundación (Cars.com) | **1998** (originada como joint venture de grupos de prensa, Classified Ventures); IPO/spin-off como Cars.com Inc. en **2017** | [V] |
| HQ | **300 South Riverside Plaza, Suite 1000, Chicago, IL 60606, EE. UU.** | [V — múltiples agregadores] |
| Tipo | **Pública**, cotiza en NYSE bajo **CARS** | [V] |
| Revenue FY2024 | **$719.2 M** (+4 % YoY); Q4-2024 **$180.4 M** (plano) | [V — cars.com IR] |
| Revenue FY2025 | **~$723.2 M** (+0.57 %); guía original 2025 era **$745–755 M** | [V — stockanalysis + IR] |
| Net income FY2024 | **$48.2 M**; Adjusted Net Income **$114.9 M**; **Adjusted EBITDA $209.7 M (29.2 % margen)** | [V — IR] |
| Free Cash Flow FY2024 | **$128.1 M**; Operating CF $152.5 M | [V — IR] |
| Empleados | **~1.500–1.800** [A — rango de agregadores, no auditado] | [A] |
| CEO | **Alex Vetter** (CEO histórico de Cars.com) | [V1 — conocimiento del emisor] |

### Marcas / propiedades de la plataforma [V]
1. **Cars.com** — marketplace #1 de coches para shoppers + sitio de reputación de dealer (núcleo de audiencia y de datos).
2. **Dealer Inspire** — webs de concesionario, digital retail, chat/Conversations, SEO, servicios gestionados.
3. **AccuTrade** — tasación/valoración VIN + oferta garantizada + IMS (ver `accu-trade.md`).
4. **DealerClub** — subasta mayorista dealer-to-dealer **reputation-based** (adquirida ene-2025).
5. **Cars Commerce Media Network** — publicidad in-market (vídeo, display, social, VIN performance media); incluye la marca histórica **FUEL** (vídeo).
6. **DealerRater** — sitio de reseñas de concesionario más grande (adquirido **1-ago-2016**).
7. **CreditIQ** — fintech de financiación instantánea (adquirida **nov-2021, $30 M**).

### Cronología de M&A [V]
- **2016 (1-ago)** Adquiere **DealerRater** (mayor web de reseñas de dealer; 44.000 dealers US/Canadá).
- **2017** Spin-off como Cars.com Inc.; cotiza NYSE: CARS.
- **2021 (nov, $30 M)** Adquiere **CreditIQ** (fintech, fundada 2014, NY; instant loan approvals, "BYOL").
- **2022 (feb, ~$65 M + ~$63 M earnout)** Adquiere **The Accu-Trade Group + Galves Market Data + MADE Logistics** (ver `accu-trade.md`).
- **2023 (oct-17)** **Rebrand a Cars Commerce.**
- **2025 (ene-23, $25 M + hasta $88 M earnout)** Adquiere **DealerClub** (subasta mayorista; fundador **Joe Neiman**, co-fundador de ACV Auctions).

### Clientes objetivo (segmentos) [V]
1. **Concesionarios** (franquiciados e independientes) — cliente que paga (suscripción).
2. **OEMs / fabricantes** (Tier 1 branding + audiencia + certificación de webs).
3. **Lenders / financieras** (vía CreditIQ, "BYOL").
4. **Consumidores / shoppers** (audiencia gratuita del marketplace).
5. **Prensa / industria** (Industry Insights Report, gratuito).

---

## 2. Cobertura

### Geográfica [V]
- **EE. UU.** (núcleo absoluto del marketplace, media, dealer SaaS, insights).
- **Canadá** — vía **DealerRater** ("44.000 dealerships US y Canadá") y **AccuTrade** (Canadá desde 2016). [V — DealerRater + accu-trade.md]
- **Sin Europa ni global** ← hueco mayor para cardeep. [V por ausencia]

### Escala / audiencia [V con matiz]
- **Concesionarios cliente (de pago): 19.206** (FY2024, −2 % YoY). [V — IR]
- **ARPD (avg revenue per dealer): $2.475/mes** (−2 % YoY). [V — IR]
- **Monthly Unique Visitors: 23.1 M** (FY2024, −5 % YoY); **Traffic 143.8 M visits** (+1 %); **organic 61 %**. [V — IR, métrica auditada]
- **Marketing claim: "25–26 M monthly unique shoppers" / "29 MM unique monthly in-market shoppers"** (Media Network). ⚠ **Discrepancia**: la cifra auditada en el 10-K/earnings es **23.1 M MUV**; las cifras 25/26/29 M son de marketing/red de medios. [CLAIM vs V — ver Gaps]
- **Reseñas de consumidor acumuladas: ~13 M** (citado en el Insights Report). [CLAIM]
- **DealerClub: 650+ dealers** clientes (a la adquisición). [V]

### Scope de vehículos [V]
- **Coches de pasajeros y light-duty trucks**: **new, used, CPO (certified pre-owned)** en el marketplace; **wholesale (dealer-to-dealer)** en DealerClub; **trade-in/adquisición** en AccuTrade.
- **EV / híbridos** tratados explícitamente (badges de rango EV, EV share en insights).
- **[A]** No cubre moto/RV/heavy-equipment como vertical nombrada (a diferencia de MarketCheck US).

---

## 3. Productos + campos atómicos

Arquitectura **multi-producto de plataforma** (no API-first). El dato vive en pantallas de consumidor (Cars.com), webs de dealer (Dealer Inspire), consolas de dealer (AccuTrade IMS, dashboards), informes (Insights) y reporting de medios. Desglose atómico por producto:

### — BLOQUE MARKETPLACE DE CONSUMO (Cars.com) —

### 3.1 Anuncio / listing en Cars.com (SRP + VDP) — el "ficha de coche" [V — SRP en vivo]
Campos verificados en la **Search Results Page** en vivo (used, zip 60606):
- Identidad: `year`, `make`, `model`, `trim`, `body_style` (ej. "Used 2025 Ford Expedition Max Active 4x2"), `VIN` (en VDP), `exterior_color`, `interior_color`, `fuel_type`, `drivetrain`, `transmission`, `engine`, `features`/`options`, `seller_notes`.
- Precio: **`list_price`** (ej. "$52,376"), **`price_drop`** (indicador con $ — ej. "$2.9K"), **`monthly_payment_estimate`** ("Est. $930/mo"), **`MSRP`** (en vehículos nuevos).
- **`deal_badge`**: **Great Deal / Good Deal / Fair Deal (Fair Price) / Well-Equipped** (badge de posicionamiento de precio vs mercado; ver §3.2).
- **`High Demand` badge** ("Hot Car" — vehículo popular, "act fast"). [V]
- **`Range Score`** (EV): etiqueta tipo "Range Score | Excellent" = **EV Battery Rating** (rango esperado **actual vs cuando nuevo**, captura degradación de batería). [V]
- **`American-Made Index` badge** (índice propietario Cars.com, ver §3.3). [V]
- Estado/CPO: **`certified` / CPO badge** (con garantía de fabricante). [V]
- Kilometraje: **`mileage`** ("24,600 mi."). [V]
- Dealer: **`dealer_name`** ("Ron Tirapelli Ford"), **`dealer_star_rating`** ("4.5", escala 5★), `dealer_review_count`, **`location`** (city, state) + **`distance`** ("38 mi"). [V]
- Media: **`photo_count`** (varias imágenes/anuncio). [V]
- Historial: **`Free AutoCheck Report`** (link en el anuncio; **AutoCheck = powered by Experian**): AutoCheck Score, accident history, mileage, ownership info. [V]
- **Sort options (SRP)**: Best match · Lowest price · Highest price · Lowest mileage · Highest mileage · Nearest location · **Best deal** · Newest year · Oldest year · **Newest listed** · **Oldest listed**. [V — implican `days_on_market`/`listing_date` como campos internos]
- Alertas: **`price_drop_notification`** (alerta cuando un coche guardado baja de precio). [V]

### 3.2 Deal Badges (motor de valoración de mercado) — metodología técnica [V — tech.cars.com]
"Designa cómo de bien está **valorado** un usado frente a sus comparables más cercanos; se asigna según cuán lejos está el `list_price` del **estimated market value**."
- **Modelo**: **XGBoost** (boosted regression trees), entrenado sobre **1 año** de datos de usados.
- **Features de entrada**: `body_style`, `brand`, `model`, `listing_location`, `dealership_characteristics`, `seasonality`, `supply_demand_data`. **NO** usa el `list_price` como input (clave: el precio no contamina el valor predicho).
- **Salidas**: `estimated_market_value` (valor medio esperado), `market_value_lower_bound`, `market_value_upper_bound` (banda de desviación esperada vs comparables).
- **Lógica de badge**: por debajo del lower bound = **Great Deal** (competitivo); por encima del upper bound = **Fair Deal** (menos competitivo); en banda = Good Deal; **Well-Equipped** cuando el precio sube por features de alta demanda en la región más allá de YMMT.
- **Precisión**: **MdAPE ~4 %** global; objetivo **≤5 %** por body-style y brand (vans excedían por muestra limitada). [V]

### 3.3 American-Made Index (AMI) — índice propietario [V — cars.com/american-made-index]
Índice anual (20+ años, desde ~2006). Ranking de light-duty en **escala 100 puntos** por **5 factores**:
1. **Assembly location** (montaje final en una de **46 plantas US** de **13 grupos** fabricantes).
2. **Parts sourcing** (según American Automobile Labeling Act).
3. **U.S. factory employment** relativo a la producción.
4. **Engine sourcing**.
5. **Transmission sourcing**.
Tiebreaker: **curb weight**. Se muestra como **badge** en los anuncios cualificados. [V]

### — BLOQUE REPUTACIÓN (DealerRater + Cars.com reviews) —

### 3.4 DealerRater / Cars.com Reviews — dato de reputación de dealer [V]
- **Cobertura**: **44.000 dealerships** US y Canadá; **5.000+ Certified Dealers**. [V]
- **`PowerScore™`**: algoritmo de puntuación de dealer (0–5). [V]
- **Dimensiones de reseña (DealerRater, histórico)**: `customer_service`, `quality_of_work`, `friendliness`, `pricing`, `overall_experience`. [V]
- **Dimensiones (criterio reciente)**: `trade_in_experience`, `financing_experience`, `quality_of_work`, `transaction_speed`, `pricing_transparency`, `overall_experience`. [V]
- **Dimensiones en Cars.com**: `customer_service`, `buying_process`, `quality_of_repair`, `overall_facilities`. [V]
- Campos: `overall_rating` (5★), `recommend_dealer` (yes/no), `review_text`, `employee_ratings`, `dealer_response`, `review_date`. [V — DealerRater UI]
- **Premios**: **Consumer Satisfaction Award** (≥25 reseñas/año + PowerScore ≥4.0; top 10 % de new-car dealers US) y **Dealer of the Year**. [V]
- Volumen: **>1 M reseñas de consumidor/año** (premios); ~13 M acumuladas (plataforma). [CLAIM]

### — BLOQUE TASACIÓN / ADQUISICIÓN (AccuTrade) —

### 3.5 AccuTrade — tasación VIN + oferta garantizada + IMS [V — ver `accu-trade.md`]
> Esquema completo en el fichero dedicado. Headline de campos relevantes a la plataforma:
- `real_cash_value` / `guaranteed_offer`, `value_range`, `Galves Trade-in Value`, `Galves Market Ready Value`.
- `daily_adjusted_VIN_value`, `daily_depreciation_rate`, `projected_days_on_market`.
- `gross_profit_retail`, `gross_profit_wholesale`, **`Inventory Intelligence Score`** (riesgo, no edad), `vehicle_pedigree`, `dealer_fit`, `market_fit`.
- `reconditioning_cost`, **`OBD-II diagnostic deduction`**, `VIN-level deductions` (vacs[]).
- Cuestionario de condición ultra-granular (luces por sistema, averías por componente, daños con importe, título/robo).
- **AccuTrade Connected**: ~1.000 suscriptores (record FY2024), endosado por **10 OEM partners**. [V — IR]

### — BLOQUE SUBASTA MAYORISTA (DealerClub) —

### 3.6 DealerClub — subasta dealer-to-dealer reputation-based [V con matiz de fuente]
- **Sistema de reputación (primero de la industria)**: cada dealer es **rated**; reduce arbitrajes y problemas de título.
- **Categorías de rating del vendedor** (visibles al comprador): **`sell_through_rate`**, **`vehicle_inspection_accuracy`**, **`title_consistency`** (consistencia en proveer títulos). [V1 — dealerclub.com / Auto Remarketing; no detalladas en el PR de adquisición → ver Gaps]
- **Condición del vehículo**: **`letter_grade`** (calificación de condición), `guaranteed_condition_aspects` (el vendedor garantiza ciertos aspectos), **`photos` + `videos`** detallados.
- **Mecánica**: listing now / scheduled / auction event; **interactive bidding** (preguntas al vendedor en vivo); **public chats** (resuelven dudas/disputas de forma transparente); **follow/block dealers**; filtros por geografía/specs/seller; notificaciones email/SMS.
- **Modelo de incentivo**: vendedores con alto rating **cobran por vender** (en vez de pagar sell-fee); ingresos vía **transaction fees**.
- **Fundador**: **Joe Neiman** (co-fundador de ACV Auctions); lanzado a clientes 2024.

### — BLOQUE WEBS / DIGITAL RETAIL (Dealer Inspire) —

### 3.7 Dealer Inspire — plataforma de web + digital retail [V]
- **Websites data-driven**: mensajería personalizada por **ubicación y actividad**; **búsqueda en 0.2 s** ("fastest in auto"); **2× conversión web**.
- **Online Shopper / Digital Retail**: comparación de **payment options** por múltiples vehículos guardados (dealer lenders + F&I); **pre-approval instantánea** ("15 % higher close rate on pre-approved leads").
- **Conversations** (chat/text): recomendaciones de vehículo, ajuste de pagos, cierre en tiempo real.
- **Trade-In** embebido (powered by **AccuTrade**).
- **SEO** (origen de la empresa) + **Managed Services** (creatividad, incentivos, "Why Buy").
- **OEM certification**: certificado en casi todos los programas OEM (Tier 1 branding + audience data). Soporte: 98 % quality score.

### — BLOQUE MEDIOS (Cars Commerce Media Network) —

### 3.8 Media Network — publicidad in-market [V]
Productos:
- **In-Market Video** (incl. marca histórica **FUEL**): vídeo en social/streaming; **150+ channels**; **AI auto-genera vídeo por VIN** sincronizado con data+fotos.
- **In-Market Display**: display en research/inventory pages de Cars.com + retargeting.
- **Cars Social**: dynamic inventory ads en social → VDPs.
- **VIN Performance Media**: promoción AI-driven de inventario en top de búsquedas + recomendaciones cross-channel.

**Señales de audiencia / métricas (data points):**
- `unique_monthly_in_market_shoppers` (**26–29 M** según página). [CLAIM]
- `% plan to buy within 6 months` (**81–83 %**); `% undecided where to buy` (**88–90 %**); `% undecided what to buy` (**72–73 %**). [CLAIM]
- **`VIN-level sales attribution`** (new + CPO). [V]
- **`location-based data signals`** (view de streaming → showroom visit). [V]
- Métricas de rendimiento: `VDP_conversion` (+35 % vs paid social estándar), `dealer_website_visits` (3.4×), `website_leads` (2×), `sales_influenced_by_Cars.com` (+29 %). [CLAIM]
- Targeting: activity-based (en Cars.com), local market, vehicle preference matching, in-market shopper identification.

### — BLOQUE FINTECH (CreditIQ) —

### 3.9 CreditIQ — financiación instantánea [V]
- **Instant loan approval/decision** en web del dealer y en Cars.com.
- **`penny-perfect monthly payment`** (pago exacto).
- Campos: `APR`, `loan_term`, `down_payment`, `pre-approval`, `lender_match`.
- **"BYOL" (Bring Your Own Lender)** — primero de la industria; **800+ lenders**, **1.700 integraciones** tecnológicas.

### — BLOQUE INTELIGENCIA DE MERCADO (Industry Insights Report) —

### 3.10 Cars Commerce Industry Insights Report — el "portal-insights" [V]
Informe **mensual** (+ annual year-in-review) "crafted by an expert team of Cars Commerce data analysts" desde **supply, demand, pricing y consumer behavior** de la plataforma (Cars.com + Dealer Inspire + AccuTrade). Indicadores recurrentes (data points):
- **`New Car Pricing Index (NCPI)`** — índice propietario: **coste total de comprar + financiar** un vehículo, expresado como **% sobre MSRP** (ej. "32.7 % above MSRP"). [V]
- **New-vehicle sales** (seasonally adjusted, YoY) + **days on lot** (~70 días nuevo).
- **New inventory level** (YoY/MoM) + **average new list price** (ej. **$49,575**, ene-2026).
- **Model-year mix** (% de inventario por MY; ej. "2026 MY >50 % por noviembre").
- **Mass-market vs luxury**: inventory + price por segmento.
- **Used-vehicle**: inventory (YoY), **average used price** (ej. **$29,099**), **days on lot** (~53–54 días).
- **Affordability**: vehículos **bajo $20K / bajo $30K** (inventario + tendencia).
- **Body-style distribution** (SUV/truck vs sedan).
- **EV / used-EV**: share, inventory (ej. "+136.7 %"), price, days.
- **Market share by brand** + **brand-level inventory** (ej. Ford −20 %, GM −13 % YoY).
- **Demand = `Searches on Cars.com`** (proxy de demanda de consumidor). [V]
- **Trade-in values** (de AccuTrade). [V]
- Cadencia: **mensual**; entrega: web + PDF + Google Slides embebible + email subscription. [V]

### — DASHBOARDS DE DEALER (reporting) —

### 3.11 Analítica de dealer / Experience [A — detalle no auditado en fuente oficial]
El dealer ve, en consola/dashboard: `VDP_views`, `leads` (+ `lead_source`), `conversion_rate`, `market_position`/ranking competitivo, `website_traffic`, reporting de medios (atribución VIN). [A — patrón de industria + Media Network reporting; nombres exactos del producto no verificados en fuente oficial]

---

## 4. Metodología y fuentes de datos [V]
- **Fuente primaria = el propio ecosistema** (first-party): comportamiento de **23.1 M visitantes únicos/mes** en Cars.com (búsquedas, VDP views, leads, favoritos), inventario sindicado de **19.206 dealers**, datos de tasación AccuTrade, reseñas de DealerRater, transacciones de DealerClub. **NO es scraping de terceros ni panel editorial.**
- **Deal Badges**: ML **XGBoost** sobre 1 año de usados; features de mercado (body/brand/model/location/dealer/seasonality/supply-demand); excluye list_price; MdAPE ~4 %.
- **AccuTrade**: valor de **Galves Market Data** (mayorista desde 1957, regionalizado, análisis humano + diario) + transacciones de subasta internas (red Hollenshead/MADE ~1.000 veh/semana) + OBD-II (ver `accu-trade.md`).
- **EV Battery Rating / Range Score**: rango esperado actual vs cuando nuevo (modela degradación). [V]
- **Vehicle history**: **AutoCheck (Experian)** — tercero, no propio. [V]
- **Insights Report**: agregación de supply/demand/pricing/consumer-behavior de la plataforma; **NCPI** = coste total compra+financiación vs MSRP; demanda proxied por **Searches on Cars.com**.
- **American-Made Index**: metodología propia de 5 factores (assembly, parts AALA, US employment, engine, transmission), 100 puntos.
- **DealerRater PowerScore**: algoritmo multifactor de reputación.
- **Frecuencia**: marketplace en tiempo real; insights mensual; ARPD/financials trimestral.

---

## 5. Entrega
- **Marketplace web + apps** (Cars.com iOS/Android) — canal de consumidor. [V]
- **Webs de concesionario** (Dealer Inspire, SaaS) + **digital retail / online shopper** embebido. [V]
- **Consolas de dealer**: AccuTrade Appraiser app + IMS; dashboards de leads/medios. [V]
- **App de subasta** (DealerClub iOS) + web. [V]
- **Red de medios** (vídeo/display/social en Cars.com y 150+ canales/streaming) con **reporting de atribución VIN**. [V]
- **Informes** (Industry Insights): **web + PDF + Google Slides + email subscription** (gratuito). [V]
- **Integraciones DMS/CRM/F&I** (AccuTrade 100+; CreditIQ 1.700; Dealer Inspire OEM-certified). [V]
- **Financiación instantánea** (CreditIQ) embebida en web/marketplace. [V]
- ⚠ **NO ofrece API/feed público de datos crudos de listings** — terceros (BrightData, Apify, Carapis, ScrapingBee, MarketCheck) **scrapean** Cars.com; no hay producto oficial de data-licensing/feed. [V — ver Gaps]

---

## 6. Precio
- **Modelo dealer = suscripción mensual** (paquetes marketplace + add-ons). **ARPD reportado: $2.475/mes** (media por dealer, FY2024). [V — IR]
- **Cars Commerce Media Network**: "turnkey ad solutions" que **requieren suscripción al marketplace**; presupuesto de medios sobre la suscripción base. [V]
- **AccuTrade**: ~$1.500/mo reportado por comunidad de dealers post-adquisición (ver `accu-trade.md`); API/IMS por demo. [V1/COMMUNITY]
- **DealerClub**: **transaction fees**; vendedores top-rated pueden **cobrar** por vender (incentivo invertido). [V]
- **CreditIQ**: integración fintech (precio no público). [A]
- **Instant Offer / Insights Report / reseñas**: **gratis** para consumidor/prensa; se monetiza vía dealer/leads/medios. [V]
- **Para shopper**: marketplace **gratuito**. [V]
- ⚠ Precio por producto **mayormente opaco** (venta por demo); la única cifra dura pública es **ARPD $2.475** y la guía de revenue. [V]

---

## 7. Placement — dónde se ubica cada dato en la UI
> Patrón a copiar por Cardeep: pantalla/sección → dato.

### A. SRP (Search Results Page) de Cars.com — tarjeta de anuncio [V en vivo]
Por cada tarjeta, de arriba a abajo: **foto(s)** → **`deal_badge`** (Great/Good/Fair Deal) + badges especiales (**High Demand**, **American-Made Index**, **Range Score | Excellent**) → **`year/make/model/trim`** → **`list_price`** (+ **`price_drop` $** si aplica) + **`Est. $/mo`** → **`mileage`** → **`dealer_name`** + **`★ rating`** → **`city, state (distancia)`**. Barra de **sort** incluye "Best deal", "Newest/Oldest listed" (exponen days-on-market/listing-date).

### B. VDP (Vehicle Detail Page) de Cars.com [V parcial]
Cabecera con **galería de fotos** + **`list_price`/`Est. $/mo`** + **`deal_badge`** + **CPO badge**. Bloques: **specs** (year/make/model/trim/mileage/color/drivetrain/fuel/transmission/engine/features), **`Free AutoCheck Report`** (historial Experian), **calculadora de pago mensual** (CreditIQ → pre-approval), **EV Range Score** (en EVs), **seller notes**, **bloque de dealer** (rating ★, reseñas, ubicación), CTA de **contacto/lead** y **trade-in (AccuTrade)**.

### C. Página de concesionario (DealerRater / Cars.com dealer) [V]
**`PowerScore`** + **★ overall** + desglose por dimensión (customer service / buying process / quality of repair / facilities; o trade-in/financing/transaction speed/pricing transparency), **reseñas** con texto + employee ratings + dealer response, **Certified Dealer / Consumer Satisfaction Award / Dealer of the Year** badges.

### D. Pantalla de tasación (AccuTrade) — ver `accu-trade.md` §7 [V]
Entrada VIN/plate/YMM → condición (stepper) → **valor garantizado / rango** + caducidad + **deducciones itemizadas**; panel IMS con gross profit retail vs wholesale, daily depreciation, projected DOM, Inventory Intelligence Score.

### E. Subasta (DealerClub) [V]
Por vehículo: **`letter_grade`** + fotos/vídeos + **`guaranteed_condition`**; junto al **vendedor**: **rating de reputación** (sell-through / inspection accuracy / title consistency); **bidding interactivo** + **public chat**; controles **follow/block**.

### F. Reporting de medios (Media Network) [V]
Dashboard de campaña: **impresiones a in-market shoppers**, **VIN-level sales attribution** (new+CPO), **location-based signals** (view→showroom), VDP conversion, dealer website visits, sales influenced.

### G. Industry Insights Report (web/PDF/Slides) [V]
Estructura mensual: executive summary → **New** (sales SAAR, inventory YoY, avg price, days on lot, model-year mix, mass-market vs luxury, **NCPI**) → **Used** (inventory, avg price, days on lot, affordability <$20K/<$30K, body-style) → **EV** (share, inventory, price, days) → **brand-level** (market share, inventory por marca) → **demand** (Searches on Cars.com) → **trade-in values**. Gráficos en PDF/Slides; suscripción email.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Plataforma conectada end-to-end** "pretail → retail → post-sale" bajo un techo: audiencia de consumidor (Cars.com) + web/digital-retail (Dealer Inspire) + tasación/adquisición (AccuTrade) + subasta mayorista (DealerClub) + medios (Media Network) + reputación (DealerRater) + fintech (CreditIQ). Pocos competidores cierran todo el funnel.
- [V] **Audiencia de consumidor propia masiva** (23.1 M MUV auditados; 143.8 M visits) como **fuente first-party** de demanda — no scraping. Permite **VIN-level sales attribution** en medios (raro: conecta vista de anuncio/vídeo con venta de VIN concreto).
- [V] **Deal Badges con ML serio** (XGBoost, MdAPE ~4 %, excluye list_price del input) + **estimated market value** con banda — posicionamiento de precio accionable para el shopper.
- [V] **Índices propietarios de marca**: **NCPI** (coste total compra+financiación vs MSRP) y **American-Made Index** (5 factores, 20+ años) — termómetros citables que generan PR/autoridad.
- [V] **EV Battery Rating / Range Score** (rango actual vs nuevo) — métrica de **salud de batería de usados** que casi nadie expone en el anuncio.
- [V] **Reputación de dealer a escala** (DealerRater 44k dealers, PowerScore, 13 M reseñas) integrada en el marketplace — capa de confianza.
- [V] **DealerClub reputation-based** (sell-through / inspection accuracy / title consistency + incentivo invertido: top sellers cobran) — diferencial frente a subastas tradicionales.
- [V] **Oferta garantizada (AccuTrade) respaldada por Cars Commerce** + OBD-II → cierre transaccional, no estimación (ver `accu-trade.md`).
- [V] **CreditIQ "BYOL"** (800+ lenders, sin cambiar procesos del dealer) — financiación instantánea penny-perfect en el funnel.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Solo Norteamérica (US + Canadá)**; **sin Europa ni global** ← hueco mayor para cardeep.
- [V] **NO es proveedor de datos/feeds**: **no hay API ni feed oficial de listings crudos**; terceros scrapean Cars.com (BrightData/Apify/Carapis/ScrapingBee/MarketCheck). El dato se monetiza embebido, no licenciado. Contraste fuerte con MarketCheck/guías de valor.
- [V] **No es guía de valor editorial** (trade/retail/wholesale/residual % nombrados): la valoración al consumidor es **deal badge + estimated market value** (banda ML), no una "cote" con valores discretos por condición/km como Glass's/cap hpi/KBB-libro. (El valor en firme vive en AccuTrade, dentro del dealer.)
- [V] **Sin valores residuales / forecasting de RV / leasing forecast** como producto (no compite con ALG/J.D. Power/Autovista).
- [V] **Sin TCO / running costs / SMR / tiempos de reparación** (no hay catálogo técnico de reparación).
- [V] **Vehicle history NO propio** — depende de **AutoCheck (Experian)**; provenance/siniestros vía tercero.
- [V] **Insights Report = inteligencia agregada de marca (free PR)**, **no un dataset granular vendible** ni dashboard de mercado por dealer/VIN tipo vAuto/MarketCheck Investor Reports; sin dimensión internacional.
- [V] **Demanda "proxied" por Searches on Cars.com** y ventas de medios por atribución — señales de su propia audiencia, no transacciones de mercado totales (sesgo de plataforma).
- [V] **Discrepancia de audiencia**: marketing 25–29 M shoppers vs **23.1 M MUV auditados** (−5 % YoY, en declive) — la cifra grande es de la red de medios, no del 10-K.
- [V1] **Detalle interno de DealerClub** (categorías exactas de TrustScore, mecánica de arbitraje, grading) **poco documentado en fuente oficial**; las categorías (sell-through/inspection/title) provienen de descripción agregada, no del PR de adquisición.
- [V] **Precio por producto opaco** (venta por demo); única cifra dura = ARPD $2.475 + guía de revenue.
- [A] **Verticales no-coche (RV/moto/heavy-equipment) ausentes** (a diferencia de MarketCheck US).
- [A] **Concentración de dependencia**: el máximo valor exige adoptar varias piezas del stack; fuera del ecosistema, menos diferencial.

---

## 10. Fuentes (URLs)
**Oficiales / producto (Cars Commerce / Cars.com):**
- https://www.carscommerce.inc/ — plataforma: 5 soluciones (Cars.com, Dealer Inspire, AccuTrade, DealerClub, Media Network); claims (89 % lead conversion, 34 % appraisal accuracy, $2,700/VIN, 4-day faster turn).
- https://www.carscommerce.inc/dealer-inspire/ — websites data-driven, 0.2 s search, 2× conversión, Online Shopper, Conversations, pre-approval (15 %), trade-in AccuTrade, SEO, OEM certification.
- https://www.carscommerce.inc/media-network/ — In-Market Video/Display, Cars Social, VIN Performance Media; 29 MM shoppers, 83/88/73 %, métricas (3.4×, +35 %, +50 %, +29 %).
- https://www.carscommerce.inc/media-network/in-market-video/ — 26 M shoppers, 81/90/72 %, 150+ channels, VIN-level attribution, location signals, AI video por VIN.
- https://www.carscommerce.inc/dealerclub-online-wholesale-auctions/ — dealer ratings, follow/block, public chats, dealer-to-dealer auctions.
- https://www.carscommerce.inc/insights-report/ — Industry Insights mensual (Nov-2025): new sales YoY, days on lot ~70, avg new ~$49,700, MY mix >50 %, mass-market vs luxury, used inventory +2 %/price +2.7 %, days ~54, <$20K, body-style; PDF/Slides/email.
- https://www.carscommerce.inc/ai-car-shopping-funnel/ — AI search natural-language, AI assistant, structured data, review sentiment ranking; 97 % influenced by AI (AI Consumer Study Q3-2025), 61 % organic.
- https://www.cars.com/ — marketplace; SRP en vivo (badges, price, price drop, Est./mo, mileage, dealer ★, distancia, Range Score, American-Made Index, High Demand).
- https://www.cars.com/shopping/results/?stock_type=used&zip=60606 — SRP verificada: sort options + campos de tarjeta verbatim.
- https://www.cars.com/american-made-index/ — AMI: 100 puntos, 5 factores (assembly/parts AALA/US employment/engine/transmission), 46 plantas, 13 grupos, tiebreaker curb weight.
- https://tech.cars.com/cars-deal-badges-4dac3ad15bf5 — Deal Badges: XGBoost, 1 año de usados, features (body/brand/model/location/dealer/seasonality/supply-demand), excluye list_price, lower/upper bound, MdAPE ~4 % (≤5 % objetivo).
- https://www.cars.com/articles/2026-starts-with-fewer-sales-but-faster-sells-522113/ — insights ene-2026: avg new $49,575, avg used $29,099, new inv −5 %, Ford −20 %, GM −13 %, 4 fewer days on lot.

**Prensa / IR / corporativo:**
- https://www.cars.com/articles/cars-com-reports-fourth-quarter-and-full-year-2024-results-505688/ — FY2024: revenue $719.2 M, Q4 $180.4 M, dealer rev +3 %, OEM&National +18 %, 19.206 dealers, ARPD $2.475, 23.1 M MUV, 143.8 M visits, organic 61 %, net income $48.2 M, Adj EBITDA $209.7 M (29.2 %), FCF $128.1 M, AccuTrade Connected ~1.000, DealerClub cerrado ene-2025.
- https://investor.cars.com/2023-10-17-CARS-Rebrands-Commercial-Enterprise-as-Cars-Commerce... — rebrand oct-2023 (pretail/retail/post-sale; une Cars.com, Dealer Inspire, FUEL, DealerRater, CreditIQ, Accu-Trade).
- https://www.cars.com/articles/cars-com-inc-acquires-dealerclub-...-504148/ y https://www.prnewswire.com/news-releases/carscom-inc-acquires-dealerclub-...-302359447.html — DealerClub: $25 M + hasta $88 M earnout, cierre 23-ene-2025, 650+ dealers, fundador Joe Neiman (ACV Auctions), reputation-based.
- https://www.prnewswire.com/news-releases/carscom-closes-acquisition-of-dealerrater-300306964.html — DealerRater cerrado 1-ago-2016 (mayor web de reseñas).
- https://investor.cars.com/2021-11-09-CARS-Closes-Acquisition-of-CreditIQ... y https://www.cars.com/articles/cars-acquires-creditiq-...-443540/ — CreditIQ: $30 M, nov-2021, fundada 2014 (Liatsis/Gerhard, NY), BYOL, 800+ lenders, 1.700 integraciones.
- https://www.cars.com/articles/cars-commerce-debuts-monthly-industry-insights-report-...-478349/ — debut Insights Report: supply/demand(Searches on Cars.com)/pricing/inventory; NCPI = coste total compra+financiación vs MSRP (32.7 % above); data de Cars.com (26 M MUV, 13 M reviews) + Dealer Inspire + AccuTrade.
- https://www.prnewswire.com/news-releases/...dealerraters-dealer-of-the-year...-301473539.html — DealerRater: dimensiones (customer service/quality/friendliness/pricing/overall), PowerScore, 44k dealers, 5k Certified, Consumer Satisfaction Award (≥25 reviews, ≥4.0, top 10 %).
- https://www.dealerrater.com/ — UI de reseñas y dimensiones.
- https://www.cars.com/articles/how-do-i-get-a-free-carfax-report-420848/ + https://www.autocheck.com/vehiclehistory/ — Cars.com usa **Free AutoCheck Report (Experian)** en muchos anuncios.

**Terceros / verificación de ausencia de API:**
- https://brightdata.com/products/datasets/cars-com · https://apify.com/.../cars-com-scraper · https://carapis.com/platforms/north-america/cars-com · https://www.scrapingbee.com/scrapers/cars.com-api/ — confirman que **Cars.com no ofrece API pública oficial**; terceros scrapean.
- stockanalysis.com/stocks/cars/ — revenue FY2025 ~$723.2 M.

**Fichero relacionado en este audit:** `accu-trade.md` (esquema atómico completo de AccuTrade/Galves/IMS).

### Notas de verificación
- **Identidad, M&A, financials, dealer count/ARPD/traffic:** doble fuente (IR + agregadores). **[V]**
- **Deal Badges (XGBoost, features, bounds, MdAPE):** blog de ingeniería oficial tech.cars.com. **[V]**
- **SRP fields + badges (Great/Good/Fair Deal, High Demand, American-Made Index, Range Score, Est./mo, price drop, ★):** página en vivo de Cars.com. **[V]**
- **NCPI, American-Made Index (5 factores), AutoCheck=Experian:** fuentes oficiales. **[V]**
- **DealerClub TrustScore (sell-through/inspection/title):** descripción agregada (dealerclub.com / Auto Remarketing), **no en el PR de adquisición**. **[V1]**
- **Audiencia 23.1 M (auditada) vs 25–29 M (marketing):** discrepancia marcada, no resuelta por invención. **[V vs CLAIM]**
- **exa/firecrawl MCP no disponibles** en el entorno (ToolSearch solo devolvió WebSearch/WebFetch); investigación con WebSearch + WebFetch. **[NOTA DE MÉTODO]**
- **SEC 8-K (sec.gov) y cardog.app devolvieron 403/404;** financials reconstruidos vía cars.com IR press release. **[NOTA DE MÉTODO]**
- **Analítica de dealer/Experience (§3.11):** patrón de industria, nombres exactos del producto no verificados en fuente oficial. **[A]**
