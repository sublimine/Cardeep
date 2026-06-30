# AutoUncle — Auditoría atómica

> **slug:** `autouncle` · **subdominio de audit:** `market-intelligence` · **web:** https://www.autouncle.com/ · **B2B:** https://b2b.autouncle.com/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído, `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** AutoUncle es el **agregador/metabuscador independiente de coche usado y el estándar de tasación basada-en-mercado
> de Europa**, nacido en Aarhus (Dinamarca, 2010). Su foso NO es una guía de tasación clásica (Eurotax/Schwacke con curvas de
> depreciación teóricas): es **la primera tasación EMPÍRICA paneuropea** — recolecta **~8,6M+ anuncios vivos de 2.600+ webs en 14 países**,
> y para cada coche calcula un **precio de mercado** por **comparación estadística contra coches similares (hasta 100 "facts")**, del que
> deriva un **rating de precio de 5 niveles (Super price → Good price → Fair price → A bit pricey → Expensive)** = el **AutoScore**. Ese
> mismo motor alimenta tres negocios: (1) **B2C** metabuscador + app (millones de usuarios/mes); (2) **B2B dealer** (Website Booster con
> widgets de tasación/valoración/carrusel + AutoUncle Traffic de leads PPC); (3) **Enterprise/API** (valoración en tiempo real para
> marketplaces, OEMs, bancos, CRMs, DMS — *market value, deal rating, sales-time forecast, residual, trade-in, risk models*). Patrón directo
> a copiar para cardeep: **rating de precio visible en CADA tarjeta/ficha de coche + "ahorras X vs mercado" + comparables similares en vivo +
> widget embebible en web de dealer + API que devuelve valor+rating+sales-time**. La métrica-firma es el **price rating como semáforo de
> confianza del comprador**, no un número frío.

> **Aviso de desambiguación:** este informe cubre **AutoUncle ApS** (autouncle.com, Aarhus, DK). El producto consumidor vive en dominios
> por país (autouncle.dk/.de/.co.uk/.it/.es/.se/.fr/.nl…) **protegidos por Cloudflare** (devuelven HTTP 403 a fetch automatizado); el
> producto profesional vive en **b2b.autouncle.com** (accesible) y el blog de inteligencia en **b2b-blog.autouncle.com**. La app móvil se
> llama **"AutoUncle: Search used cars"** y la herramienta de tasación B2C histórica **"ValuateCar"**. [VERIFICADO: careers, b2b, App Store]

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre legal/comercial | **AutoUncle** (AutoUncle ApS) | [VERIFICADO] |
| Grupo / owner | **Independiente** (sin grupo industrial matriz; respaldo VC seed, no adquirida) | [VERIFICADO ≥2: Tracxn, Crunchbase] |
| Fundación | **2010** (Dinamarca; parte del 1er programa Startupbootcamp Copenhague) | [VERIFICADO ≥2: careers, Tracxn, Crunchbase] |
| HQ | **Aarhus, Dinamarca** (Klostergade 56 C, 8000 Aarhus) | [VERIFICADO ≥2: LinkedIn/Tracxn, careers] |
| Oficinas | **Aarhus (HQ), Ámsterdam, Hamburgo, Berlín, Dresde, Karlsruhe, Dublín, Milán, Cluj-Napoca** + remoto | [VERIFICADO ≥2: careers home, careers about-us] |
| Fundadores (3) | **Johan Frederik Schjødt, Niels Kristian Schjødt, Jonas Bylov** (alias Jonas Bruun Nielsen) | [VERIFICADO ≥2: careers, Tracxn] |
| CEO | **Johan Frederik Schjødt** (Co-Founder & CEO) | [VERIFICADO: careers about-us] · ⚠ discrepancia: una people-page de careers y LinkedIn etiquetan a **Jonas Bylov** como "CEO & Co-founder" (posible cambio de rol / dato stale) |
| COO | **Jonas Bylov** (Co-Founder & COO) | [VERIFICADO: careers about-us] |
| Empleados | **90+ "co-workers"** (auto-reportado careers) · **66** (Tracxn, 31-may-2026) | [VERIFICADO ≥2 — cifras divergentes; ver Gaps] |
| Mercados consumidor | **14 países europeos** | [VERIFICADO ≥2: careers, App Store] |
| Financiación total | **~US$1,99M** en **5 rondas** (early-stage seed; última Seed **21-jun-2017**) | [VERIFICADO ≥2: Crunchbase, Tracxn] |
| Inversores | **Startupbootcamp Copenhagen, Slamdunk Capital, Nordic Makers, Northcap Partners** (+otros) | [VERIFICADO ≥2: Crunchbase, Tracxn] |
| Salud financiera | "**Triple digit annual growth rates; operating with healthy finances**" (auto-reportado) | [VERIFICADO: careers] · auto-declarado, sin estados auditados públicos |
| Misión / visión | "**make it hassle-free to buy and sell cars**" / "become the **most trusted car valuation brand in Europe**" / "Build The Most Human Company" | [VERIFICADO: careers about-us] |
| Posicionamiento | "**the international standard for car valuations and price comparisons in Europe**" · B2C: "your **independent price-check** for used cars" | [VERIFICADO ≥2: careers, autouncle.com] |

### Clientes objetivo (segmentos)
- **B2C:** compradores/vendedores particulares de coche usado (millones/mes).
- **B2B dealer:** concesionarios y grupos de concesión (independientes y de marca).
- **Enterprise/API:** **Marketplaces, OEMs (fabricantes), Dealers/grupos, sistemas CRM, portales DMS, Bancos & Aseguradoras, Agencias web/marketing**. [VERIFICADO: automotive-api, enterprise]

### Clientes / logos nombrados (B2B)
**Carwow, Carla (SE), Mazda Motor Sweden, Auto Eder Group (DE), AutoHero, Autobörse, Hyundai, Procar, coches.com, Instamotion, Spoticar,
Subito, ViaBovag (Bovag NL), Pisca Pisca (PT), Mobile.de.** Integración mostrada con **Facebook Marketplace** (rating de precio sobre el
anuncio). [VERIFICADO ≥2: automotive-api, autouncle-enterprise]

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Países consumidor (14) | **Alemania, Austria, Dinamarca, Italia, España, Polonia, Portugal, Suecia, Finlandia, Rumanía, Reino Unido, Países Bajos, Suiza, Francia** | [VERIFICADO ≥2: App Store (lista explícita), careers] |
| Países cobertura de datos/API | "**14 European countries**" (Dinamarca → Italia citados); esquema API unificado, localizado por mercado | [VERIFICADO: automotive-api] |
| Benchmarks enterprise | "**Benchmarks across 10+ countries**" (overview competitivo) | [VERIFICADO: autouncle-enterprise] |
| Volumen de anuncios | **8,6M+ anuncios vivos** evaluados a diario (B2B/API actual) · **10M+ "cars"** citado en enterprise · **11M+ listings** (app, cifra histórica/mayor) | [VERIFICADO ≥2: automotive-api, prodotti, enterprise, App Store] · ver Gaps (cifras divergentes) |
| Fuentes (webs) | **2.600+ webs/sources** (API/producto) · **2.700** (enterprise) · **1.900** (app, histórico) | [VERIFICADO ≥2 — evolución al alza; rango 1.900→2.700] |
| Frescura | Datos **ingeridos y normalizados varias veces al día**; refresco diario; "millions of cars each day" | [VERIFICADO ≥2: automotive-api, careers] |
| Scope nuevo/usado | **Usado = núcleo** (precio empírico de anuncios reales). **Nuevo**: presente en fichas (estado new/used) y como input de trade-in/residual | [VERIFICADO ≥2: prodotti, demo] |
| Tipos de vehículo | **Turismos / coches de pasajeros** (incl. SUV, berlina, station wagon, EV) — catálogo de coche; sin evidencia de moto/camión/caravana | [VERIFICADO: scraper schema bodyType, demo] · [NO-VERIFICADO que cubra no-turismo] |
| Marcas | Todas las del mercado europeo de usado (agnóstico de marca; agrega cualquier anuncio listado) | [VERIFICADO: naturaleza de metabuscador] |
| Idiomas | App soporta **12 idiomas** | [VERIFICADO: App Store] |

---

## 3. Productos + campos atómicos

> AutoUncle expone **un solo motor de dato** (AutoScore sobre el censo paneuropeo de anuncios) a través de **3 superficies**: B2C
> (metabuscador+app), B2B dealer (Website Booster + Traffic), Enterprise/API. Los campos atómicos se reconstruyeron de: el esquema de
> anuncio (scraper Apify del sitio consumidor), las páginas de producto B2B (prodotti / pricing / demo), la página de API y la de Enterprise.
> **No hay documentación OpenAPI pública** del endpoint de valoración; los outputs de API son los **nombrados** en la página de producto.

### 3.0 AutoScore — el rating de precio (la métrica-firma)
Cada coche recibe un **price rating** en **5 niveles**: **`Super price`** · **`Good price`** · **`Fair price`** · **`A bit pricey`** ·
**`Expensive`**. Definición: un coche **"Fair price"** está al **precio de mercado actual**; **"Super price"/"Good price"** = oportunidad de
ahorro (por debajo de mercado); **"A bit pricey"/"Expensive"** = por encima. Se calcula por **comparación estadística** del coche y su precio
contra **coches similares actualmente a la venta**, sobre **hasta 100 "facts"/parámetros**. Es **market-based (empírico)**, NO fórmula de
depreciación teórica. [VERIFICADO ≥2: about-autoscore (vía extracción), App Store, automotive-api]

### 3.1 Objeto `listing` / ficha de coche (campos atómicos B2C)
Esquema observado por anuncio (scraper del sitio consumidor + demo de producto) [VERIFICADO: Apify scraper schema, demo]:
- **Identidad:** `id` (listing ID único de AutoUncle), `title` (modelo), `subtitle` (versión/variante).
- **Precio:** `price` (formateado, ej. "12.000 €"), `priceValue` (numérico), **`priceRating`** (los 5 niveles), **`savingText`** (texto de ahorro vs mercado, "si disponible").
- **Specs:** `registrationDate` (matriculación), `mileage` (km), `engineFuel` (Diesel/Benzina/Hybrid/…), `bodyType` (SUV/Berlina/Station Wagon/…), `transmission` (Manual/Automático), `power` (CV/kW/PS), `consumption` (L/100km), `co2Emissions`, **color exterior**, **condition** (new/used).
- **Medioambiente (panel "Verbrauch und Umwelt"):** consumo por ciclo (**ciudad/extraurbano/autovía/autopista**), CO₂, **clasificación medioambiental / norma de emisiones EU**, **autonomía eléctrica** (EV). [VERIFICADO: demo BMW i7]
- **Vendedor/ubicación:** `location` (ciudad + CP), `seller` (dominio del vendedor), **`dealerVerified`** (dealer verificado), **`availabilityVerified`** (disponibilidad verificada).
- **Media/enlaces:** `imageUrl`, `imageAlt`, `detailUrl` (ficha AutoUncle), `externalUrl` (anuncio original del vendedor).
- **Meta:** `scrapedAt`, `sourceUrl`.
- **Factores de comparación (entran en el rating, no siempre mostrados):** make, model, **engine**, year, mileage, **car type**, transmission, **equipment/options**. [VERIFICADO: about-autoscore]

### 3.2 ValuateCar / Used-car appraisal — tasación B2C (free, 30s, sin registro)
Herramienta de tasación gratuita. El usuario introduce datos del coche y obtiene: **market price valuation** del coche según los datos;
**guardar el coche para trackear cómo cambia el market price en el tiempo** (price tracking/history); **ver coches similares actualmente a la
venta**. Basada en los mismos **>100 parámetros**. [VERIFICADO ≥2: about-autoscore (vía búsqueda), App Store "Trade-in calculator"]
**Campos atómicos:** `market_price` (valoración), **price-range** (implícito), **similar_cars_for_sale[]** (comparables vivos), **price_history** (evolución temporal), `priceRating`. [VERIFICADO: about-autoscore; rango = NO-VERIFICADO explícito]

### 3.3 App móvil "AutoUncle: Search used cars" (iOS/Android, gratis)
Funciones [VERIFICADO ≥2: App Store, Google Play]:
- **Free price evaluation** por anuncio (el AutoScore en cada coche).
- **Smart algorithm / >100 data points** para el valor.
- **Price tracking** — monitorizar cambios de precio en el tiempo.
- **Search alerts** — aviso cuando nuevos anuncios matchean tu búsqueda **o bajan de precio**.
- **Trade-in calculator** — estimar valor de mercado actual del propio coche.
- **Filtrado avanzado** por precio, km, combustible, potencia (HP).
- **Favoritos** (guardar) y **compartir** anuncios.

### 3.4 Website Booster — suite de widgets para web de dealer (B2B núcleo)
Módulos embebibles ("pocas líneas de código", GDPR doble-consentimiento) [VERIFICADO ≥2: prodotti, da-dk/priser, demo]:
- **Trade-in Valuation** (IT "Permuta Auto" / DE "Ankaufmodul"): el cliente mete **matrícula/datos** y recibe **tasación de mercado de su coche** vía AutoScore (**hasta 100 parámetros**). Captura lead de recompra. Vive en **página de tasación/permuta dedicada** del dealer.
- **Price Rating Widget** (IT "Valutazione Prezzo"): **validación de precio por tercero** sobre el anuncio del dealer → construye confianza del comprador (muestra el rating Super/Good/Fair…).
- **Test-Drive Booking** (IT "Prenotazione Test-Drive"): agenda online integrada con el calendario del dealer.
- **Offer Carousel** (IT "Carosello di Offerte" / DE "Auto-Karussell"): carrusel de stock con vehículos alternativos **bajo el anuncio principal**.
- **Price Drop Notification** (IT "Notifica di Riduzione Prezzo" / "Price alarm"): alerta automática cuando baja un precio.
- **Dashboard / LeadBox** (IT "Dashboard Personale"): tracking de leads con **sincronización CRM** (Dealer Desk, Auto-CRM, CATCH).
**Métrica de resultado citada:** "+**20%** conversión de lead a contrato". [VERIFICADO: prodotti]

### 3.5 AutoUncle Traffic / Advertising — generación de leads (B2B)
Servicio de exposición + tráfico cualificado [VERIFICADO ≥2: prodotti, da-dk/priser]:
- **Stock Auto Upload**: publicación automática del stock del dealer en autouncle.<país>.
- **Visitor Forwarding / Qualified Traffic**: enlaces directos del portal a la web del dealer (el dealer convierte en su propia web) — modelo **pay-per-click**.
- **Google Analytics 4 Monitoring**: reporting automatizado de rendimiento + soporte de setup GA4.
- **Stock Analysis Tools**: optimización del stock según tendencias de mercado.
- **Weekly/Monthly Management Reports**: rendimiento por email + **insight de conversión lead-to-sale**.
- **Customizable Campaign Budget**: gestión flexible del gasto.

### 3.6 Real-Time Automotive Valuation API (Enterprise)
"**Europe's most-used real-time automotive valuation API**". Auth: **API key**. Flujo: "Authenticate → Send a vehicle → Get back a complete
valuation". Esquema unificado entre mercados, localizado por país. [VERIFICADO: automotive-api]
**Outputs nombrados (campos atómicos):**
- **`market value`** (valor de mercado)
- **`deal rating` / `price ratings`** (el AutoScore: Super price…Expensive)
- **`sales-time forecast`** (pronóstico de tiempo de venta / days-to-sell)
- **`live comparables`** (comparables vivos del mercado)
- **`pricing intelligence`**
- **`residual values`** (valores residuales / forecasting de RV)
- **`trade-in valuations` / `trade-in offers`**
- **`risk models`** (modelos de riesgo — para origination/seguro)
**Inputs:** vehicle (especificación del vehículo) + API key. [VERIFICADO: automotive-api]
**Aplicación por segmento (qué consume cada cliente):**
| Segmento | Uso del dato |
|---|---|
| **Marketplaces** | **price rating en cada anuncio** |
| **OEMs** | new/used pricing, **trade-in offers**, **residual forecasting** |
| **Dealers/grupos** | **inventory appraisal at scale** (tasación de stock masiva) |
| **CRM systems** | enriquecimiento de ficha de vehículo, **sync de valor de mercado en vivo** |
| **DMS portals** | **competitor pricing**, **market alerts** |
| **Banks & Insurance** | **loan origination**, **residual determination**, **claims processing** |
| **Web/Marketing agencies** | underwriting, revaluation |
[VERIFICADO: automotive-api]

### 3.7 Enterprise Solutions — Market Insights + Traffic Enterprise
**Market Insights** (sobre 10M+ listings): **demand**, **trends**, **price development**, **competitive overviews**, **benchmarks across
10+ countries**, **market-wide automotive valuations** (basadas en millones de anuncios reales + ventas recientes). Permite "build their own
tools, price vehicles correctly, sell faster". [VERIFICADO ≥2: autouncle-enterprise, automotive-api]
**Tiers (kickback con suscripción anual):**
- **Enterprise Basic (2% kickback):** single feed management, basic listing integration, standard AutoUncle carousels, top-funnel campaigns, **monthly status reporting**.
- **Enterprise Premium (5% kickback):** customized/segmented campaigns, advanced feed splitting & optimizations, superior visibility, **exclusive carousels**, top+lower funnel, **high-accuracy server-side tracking**, **tailored market insights across Europe**, dedicated support & reporting, **price rating widget**.
[VERIFICADO: autouncle-enterprise]
**Métricas de tracking/operación:** vehicle detail page views, visitor conversion metrics, cost-per-sale (caso Carla: "**30% lower than
target**"), lead-to-sale conversion. **Account management: reuniones de follow-up mensuales** ("track results, figures, opportunities,
insights, future improvements"). [VERIFICADO ≥2: autouncle-enterprise, enterprise]

### 3.8 Blog de inteligencia de mercado
**b2b-blog.autouncle.com** = "**Used Car Market Intelligence**" — canal donde publican contenido de inteligencia de mercado (tendencias,
desarrollo de precio, etc.). [VERIFICADO: search title] · contenido detallado [NO-VERIFICADO: el blog devolvió HTTP 403 a fetch]

---

## 4. Metodología y fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Naturaleza del dato | **Precios de ANUNCIO (asking price)** de coches a la venta online — NO precio de transacción confirmado | [VERIFICADO ≥2: about-autoscore, automotive-api] |
| Fuente | **Agregación/metasearch** de **2.600+ webs** (portales, webs de dealer) en 14 países; "millions of monthly users" aportan señales | [VERIFICADO ≥2: automotive-api, careers] |
| Método de valoración | **Empírico/market-based**: comparación estadística de cada coche vs **coches similares actualmente a la venta** (price, year, mileage, equipment), sobre **hasta 100 facts**. "First to use a market based method, not theoretical formulas" | [VERIFICADO ≥2: about-autoscore, búsqueda metodología] |
| Factores comparados | make, model, **engine**, year, mileage, **car type**, transmission, **equipment** (+ hasta 100 parámetros) | [VERIFICADO ≥2: about-autoscore] |
| Frescura/recalibración | Ingesta y normalización **varias veces al día**; valoraciones actualizadas regularmente para mantener precisión | [VERIFICADO ≥2: automotive-api, about-autoscore] |
| Señales enterprise | market trends, statistics, pricing, **demand signals**, **car catalogues**, **transaction data**, traffic insights | [VERIFICADO: enterprise/search] · "transaction data" citado en marketing |
| Confidence/accuracy | No expone un score numérico de confianza público (a diferencia de AutoGrab 0-1); precisión = argumento cualitativo | [NO-VERIFICADO: ausente de docs] |
| Validación externa (claim) | "valuation technology **used by the Danish Ministry of Taxation** to determine market car values" | [CLAIM de AutoUncle — NO-VERIFICADO independiente] · ver Gaps: SKAT/**Motorstyrelsen** es quien hace las valoraciones oficiales danesas |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Web B2C** | Metabuscador en dominios por país (autouncle.dk/.de/.co.uk/.it/.es/.se/…) | [VERIFICADO: search, autouncle.com] |
| **App móvil** | iOS (App Store) + Android (Google Play), gratis, 12 idiomas | [VERIFICADO ≥2: App Store, Play] |
| **Widgets embebibles (iFrame/JS)** | Website Booster: trade-in, price rating widget, test-drive, carrusel, price-drop, leadbox — "pocas líneas de código" | [VERIFICADO ≥2: prodotti, demo] |
| **REST API** | Real-Time Valuation API (API key, esquema unificado, localizado por mercado) | [VERIFICADO: automotive-api] |
| **Feeds / stock upload** | Subida automática de stock del dealer; feed management (single/advanced split) | [VERIFICADO ≥2: prodotti, enterprise] |
| **CRM integration (push de leads)** | Reenvío automático de leads a Dealer Desk, Auto-CRM, CATCH | [VERIFICADO ≥2: prodotti, da-dk/priser] |
| **Dashboard / LeadBox** | Panel de tracking de leads para el dealer | [VERIFICADO: prodotti] |
| **Reportes** | Management report (lead-to-sale), weekly email, monthly status; market insights reports; reuniones mensuales | [VERIFICADO ≥2: prodotti, enterprise] |
| **GA4 / server-side tracking** | Monitorización GA4 (Traffic) + server-side tracking de alta precisión (Premium) | [VERIFICADO ≥2: prodotti, enterprise] |
| **Blog inteligencia** | b2b-blog.autouncle.com (Used Car Market Intelligence) | [VERIFICADO: title] |

---

## 6. Precio (modelo)

| Producto | Modelo | Estado |
|---|---|---|
| **Website Booster** | **desde 28 DKK por coche/mes** (DK) · **€339/mes** (IT, paquete) | [VERIFICADO ≥2: da-dk/priser, prodotti] |
| **AutoUncle Traffic / Advertising** | **Pay-per-click desde €0,30/click** (IT) · **desde 50 DKK por coche/mes** (DK) | [VERIFICADO ≥2: prodotti, da-dk/priser] |
| **Enterprise Basic** | **2% kickback** (suscripción anual) | [VERIFICADO: enterprise] |
| **Enterprise Premium** | **5% kickback** (suscripción anual) | [VERIFICADO: enterprise] |
| **API valuation** | **Contact-sales** (sin tarifa pública) | [VERIFICADO: automotive-api — sin precio] |
| Condiciones | Sin lock-in de larga duración; facturación mensual/anual por transferencia o **SEPA**; consultoría de crecimiento gratis; **sin free-trial explícito** | [VERIFICADO: da-dk/priser] |
| Gratuito (B2C/lead-gen) | App, metabuscador, ValuateCar (tasación 30s sin registro) | [VERIFICADO ≥2: App Store, about-autoscore] |

---

## 7. Placement (dónde colocan cada dato — patrón a copiar por cardeep)

| Dato / métrica | Dónde se coloca (pantalla/sección) | Estado |
|---|---|---|
| **Price rating (AutoScore)** | **Badge en CADA tarjeta de coche** (resultados de búsqueda) **y en la ficha** — semáforo Super price→Expensive; también sobre el anuncio en **Facebook Marketplace** y como **Price Rating Widget** en la web del dealer | [VERIFICADO ≥2: scraper `priceRating`, automotive-api, prodotti] |
| **Ahorro vs mercado (`savingText`)** | Junto al precio en la **tarjeta/ficha** del coche ("si disponible") | [VERIFICADO: scraper schema] |
| **Market price + comparables similares** | **Ficha de coche / resultado de tasación**: precio de mercado + "**coches similares actualmente a la venta**" | [VERIFICADO ≥2: about-autoscore, ValuateCar] |
| **Price tracking (evolución temporal)** | **Coche guardado / ValuateCar**: trackea cómo cambia el market price en el tiempo | [VERIFICADO ≥2: ValuateCar, App Store] |
| **Specs + consumo/medioambiente** | **Panel de ficha** ("Verbrauch und Umwelt": consumo por ciclo, CO₂, norma EU, autonomía EV) | [VERIFICADO: demo BMW i7] |
| **Trade-in valuation** | **Página/módulo de permuta** embebido en la web del dealer (input matrícula → valor) | [VERIFICADO ≥2: prodotti, demo] |
| **Offer Carousel** | **Bajo el anuncio principal** en la ficha de coche del dealer (stock alternativo) | [VERIFICADO ≥2: prodotti, demo] |
| **Price-drop alert / search alert** | **Notificación push/email** al comprador (app) y al lead | [VERIFICADO ≥2: App Store, prodotti] |
| **Leads / conversión** | **Dashboard/LeadBox** del dealer + push a CRM (Dealer Desk/Auto-CRM/CATCH) | [VERIFICADO ≥2: prodotti, da-dk/priser] |
| **API valuation (market value/deal rating/sales-time/residual/trade-in/risk)** | **Respuesta REST** embebida en el sistema del cliente (marketplace listing, OEM pricing, CRM record, DMS alert, banco/seguro) | [VERIFICADO: automotive-api] |
| **Market insights (demand/trends/price development/benchmarks)** | **Reportes Enterprise + dashboards + reuniones de follow-up mensuales** | [VERIFICADO ≥2: enterprise, search] |
| **Stock analysis / rendimiento** | **Management reports (GA4, weekly/monthly)** de AutoUncle Traffic | [VERIFICADO: prodotti] |

---

## 8. Diferencial (lo que ofrece y otros no)

1. **Tasación 100% EMPÍRICA paneuropea** — comparación estadística contra coches reales a la venta (no curva teórica de depreciación tipo Eurotax/Schwacke). "First to use a market based method". [VERIFICADO]
2. **Price rating de 5 niveles (AutoScore) como métrica-firma** — semáforo de confianza (Super price→Expensive) visible en cada anuncio; copiable directamente. [VERIFICADO]
3. **Censo independiente de ~8,6M+ anuncios de 2.600+ webs en 14 países** — agregador neutral, no atado a un portal ni a un grupo. [VERIFICADO]
4. **Triple superficie sobre un mismo motor:** B2C (tráfico/marca) + B2B dealer (widgets+leads) + Enterprise/API (valoración). [VERIFICADO]
5. **Widgets embebibles listos** (trade-in, price rating, carrusel, price-drop, test-drive) con sync CRM e implantación de "pocas líneas". [VERIFICADO]
6. **API que devuelve el paquete completo** (market value + deal rating + **sales-time forecast** + residual + trade-in + **risk models**) con un único esquema multi-mercado. [VERIFICADO]
7. **Sales-time forecast** (pronóstico de tiempo de venta) como output nativo de API — métrica de velocidad rara en guías clásicas. [VERIFICADO]
8. **Modelo de precio dealer ultra-granular** ("por coche/mes": 28 DKK Booster / 50 DKK Traffic) + **PPC €0,30/click** + **kickback 2/5%** enterprise. [VERIFICADO]
9. **Tráfico de consumidor propio** (millones/mes) que reenvía leads cualificados a la web del dealer (menos dependencia de grandes portales). [VERIFICADO]
10. **Marca de confianza** apalancada en claim de uso por la administración fiscal danesa (aunque ese claim es marketing, ver Gaps). [VERIFICADO el claim, no su exactitud]

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Asking price, NO transaction price** — valora sobre precios de anuncio; "transaction data" se cita en marketing pero el motor público es de anuncios. [VERIFICADO]
2. **Sin confidence score numérico público** (a diferencia de AutoGrab 0-1) — la precisión es argumento cualitativo. [VERIFICADO — ausente de docs]
3. **Sin documentación API pública (OpenAPI/Swagger)** — los outputs son los *nombrados* en marketing; el contrato técnico de campos no es verificable sin acceso comercial. [VERIFICADO]
4. **`sales-time forecast`, `residual values`, `risk models`** son outputs nombrados pero **sin esquema de campos detallado** ni unidades públicas. [VERIFICADO — nombrados, no especificados] |
5. **Solo turismos** (sin evidencia de moto/camión pesado/caravana/comercial pesado). [NO-VERIFICADO el alcance exacto] |
6. **Claim "Danish Ministry of Taxation"** — las valoraciones oficiales danesas las realiza **Motorstyrelsen** (agencia de vehículos) y dealers registrados; el rol exacto de AutoUncle no está verificado de forma independiente. [NO-VERIFICADO] |
7. **Cifras divergentes**: anuncios 8,6M↔10M↔11M; fuentes 1.900↔2.600↔2.700; empleados 90+↔66 — mezcla de datos por mercado/fecha y auto-reporte vs terceros. [VERIFICADO la divergencia] |
8. **Datos oficiales/históricos por VIN** (siniestros, propietarios, ITV/MOT, robo, write-off) **NO forman parte** del producto — AutoUncle es precio+specs de anuncio, no provenance. [VERIFICADO — ausente] |
9. **Sin price-to-market % ni market-days-supply** como métrica nombrada y atómica al estilo incumbentes US (vAuto/CCC). [NO-VERIFICADO — no aparece] |
10. **Specs limitadas a las del anuncio** (no catálogo OEM profundo tipo JATO/DAT; sin equipamiento código a código verificado por VIN). [VERIFICADO — naturaleza de agregador] |
11. **Financiación seed pequeña (~US$1,99M, última 2017)** — crecimiento auto-financiado; sin rondas grandes recientes (vs AutoGrab A$80M). Implica menor músculo de I+D externo. [VERIFICADO] |
12. **Consumer site cerrado a fetch** (Cloudflare 403) — placement consumidor reconstruido vía scraper/demo/app, no de la web viva directamente. [Nota de método] |

---

## 10. Fuentes

| # | URL | Qué verifica |
|---|---|---|
| 1 | https://www.autouncle.com/ | Posicionamiento B2C "independent price-check"; marca |
| 2 | https://careers.autouncle.com/pages/about-us | Fundación 2010, fundadores (Johan CEO / Jonas COO / Niels), HQ Aarhus, 9 oficinas, 90+ empleados, 14 mercados, misión/visión, "triple digit growth" |
| 3 | https://careers.autouncle.com/ | Departamentos (Sales/Eng/CS/Product-Data/Marketing/Finance-BI), oficinas, "millions of cars daily", valoración por estadística |
| 4 | https://b2b.autouncle.com/en-gb/automotive-api | **API:** 8,6M+ listings / 2.600+ sources / 14 países; outputs (market value, deal rating, sales-time forecast, residual, trade-in, risk models, price ratings, live comparables); segmentos; logos (Autobörse, AutoHero, Hyundai, CarWow, Mazda, Procar); FB Marketplace |
| 5 | https://b2b.autouncle.com/en-gb/autouncle-enterprise | **Enterprise:** market insights (demand/trends/price development/benchmarks 10+ países); tiers Basic 2% / Premium 5% + inclusiones; logos (Carwow, Carla, Mazda SE, coches.com, Instamotion, Spoticar, Subito, ViaBovag, Pisca Pisca, Mobile.de); caso Carla -30% CPS; reuniones mensuales |
| 6 | https://b2b.autouncle.com/it-it/prodotti | **Website Booster €339/mes** (trade-in/price-rating/test-drive/carrusel/price-drop/leadbox) + **AutoUncle Traffic PPC €0,30/click**; +20% lead-to-contract; 8,6M/2.600 |
| 7 | https://b2b.autouncle.com/da-dk/priser | **Precios:** Website Booster desde **28 DKK/coche/mes**, Advertising desde **50 DKK/coche/mes**; CRM (Dealer Desk/Auto-CRM/CATCH); SEPA; sin lock-in; sin free-trial |
| 8 | https://b2b.autouncle.com/de-de/demo | **Demo:** módulos Ankauf (trade-in), Auto-Karussell, panel de ficha (BMW i7: precio/km/kW-PS/transmisión/combustible/color/ubicación), "Verbrauch und Umwelt" (consumo por ciclo, CO₂, norma EU, autonomía EV) |
| 9 | https://www.autouncle.co.uk/en-gb/about-autoscore | **Metodología AutoScore** (vía extracción de búsqueda; página 403 a fetch): 5 tiers (Super/Good/Fair/A bit pricey/Expensive), Fair=precio de mercado, comparación estadística, **hasta 100 facts**, factores (make/model/engine/year/mileage/car type/transmission/equipment), market-based no teórico |
| 10 | https://apps.apple.com/gb/app/autouncle-search-used-cars/id533433816 ; https://play.google.com/store/apps/details?id=com.autouncle.autouncle | **App:** lista 14 países explícita; tiers Super price→Expensive; >100 data points; price tracking; search alerts (match + price drop); trade-in calculator; filtros; 11M listings/1.900 webs (histórico); claim Danish Ministry of Taxation; 12 idiomas |
| 11 | https://apify.com/lofomachines/autouncle-scraper/api | **Esquema de listing** (campos atómicos por anuncio): id/title/subtitle/price/priceValue/priceRating/savingText/registrationDate/mileage/engineFuel/bodyType/transmission/power/consumption/co2Emissions/location/seller/dealerVerified/availabilityVerified/imageUrl/imageAlt/detailUrl/externalUrl/scrapedAt/sourceUrl |
| 12 | https://tracxn.com/d/companies/autouncle/__YuarGeOXOcsqbJP4q0N6g9rSJNeuG0qGIO6YAjUZTEs | Funding ~US$1,99M / 5 rondas / Seed jun-2017; inversores (Nordic Makers, Northcap +6); independiente; 66 empleados (may-2026); fundadores; HQ; competidor (Enatco) |
| 13 | https://www.crunchbase.com/organization/autouncle | Fundación 2010 Startupbootcamp Copenhague; ~US$1,99M; Slamdunk Capital + Startupbootcamp; metasearch de usado |
| 14 | https://b2b-blog.autouncle.com/ | Existencia del blog "Used Car Market Intelligence" (contenido 403 a fetch) |
| 15 | https://motorst.dk/en-us/individuals/vehicle-taxes/registration-tax/ ; https://skat.dk/en-us/individuals | Contexto fiscal danés: valoraciones oficiales por **Motorstyrelsen** + dealers (matiza el claim "tax ministry uses AutoUncle") |

> **Nota de método:** los dominios de consumidor (www.autouncle.<país>) están tras **Cloudflare** y devuelven **HTTP 403** a fetch
> automatizado; por eso la metodología AutoScore y el placement B2C se reconstruyeron de (a) extracción de buscador que cita esas páginas
> verbatim, (b) el esquema del scraper de terceros (Apify) que enumera los campos del anuncio, (c) la demo y páginas de producto B2B
> (accesibles) y (d) las fichas de App Store/Google Play. Los subdominios **b2b.autouncle.com** y **careers.autouncle.com** sí son accesibles
> y son la fuente primaria del producto profesional. Discrepancias de cifras (anuncios 8,6–11M, fuentes 1.900–2.700, empleados 66 vs 90+) y
> de rol CEO/COO (Johan vs Jonas) declaradas explícitamente. El claim "Danish Ministry of Taxation" se marca como afirmación de marketing
> **no verificada de forma independiente**. No hay OpenAPI público: los campos de API son los **nombrados** en la página de producto, no un
> contrato técnico leído verbatim.
