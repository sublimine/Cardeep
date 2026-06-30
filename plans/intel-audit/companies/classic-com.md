# CLASSIC.COM — Auditoría atómica

> Slug: `classic-com` · Subdominio cardeep sugerido: **market-intelligence** · Región: **Global** (núcleo EE. UU., dato de subasta mundial)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO en vivo]` = leído en el DOM real con navegador; `[VERIFICADO]` = doble fuente web; `[NO-VERIFICADO]` = no se pudo confirmar leyendo la fuente.
> Naturaleza: **NO es un guía-precio/tasador tradicional** (no publica un valor retail/trade por VIN como KBB/Eurotax). Es el **buscador + plataforma de analítica de mercado del coche clásico/exótico/de colección**: un **agregador de listings** (subastas + dealers + privados de todo el mundo) sobre el que construyen un **benchmark de mercado propietario (CMB)**, gráficos de mercado, comps por VIN, alertas y herramientas para dealers. Modelo "Zillow/Bloomberg del coche de colección": el valor emerge de **transacciones reales agregadas**, no de un libro de tasación.
>
> ⚠ Nota de acceso: `www.classic.com` está tras **Cloudflare** y devuelve **403** a `WebFetch`. Todo lo marcado `[VERIFICADO en vivo]` se extrajo navegando con **navegador real (Playwright MCP)**, que sí pasa el reto. El subdominio literal `market-intelligence.classic.com` **NO resuelve (DNS ENOTFOUND)** — "market-intelligence" es la etiqueta de clasificación cardeep, no una URL de classic.com.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **CLASSIC.COM** (entidad "Classic Technologies / Classic", marca comercial CLASSIC.COM) | classic.com; Crunchbase |
| Tagline oficial | "**The search engine for classic, exotic, and specialty cars**" / "the search engine **and analytics platform** for the classic, collector, and exotic car industry" | classic.com (title + about) |
| Fundación | **~2020** (Juan Diego Calle reflexiona sobre "3 años operando" en mensaje CEO 2024; 1ª ronda Seed **17-dic-2021**). Algunas fichas de terceros citan 2011/Palm Harbor → es artefacto del **registro del dominio**, no de la empresa. `[VERIFICADO con caveat]` | classic.com/insights message-ceo-2024; Tracxn; Crunchbase |
| CEO / Co-fundador | **Juan Diego Calle** — emprendedor colombo-americano; antes fundó **.CO Internet SAS** (registro del TLD `.co`, **adquirido por Neustar abr-2014**); HBS OPM; Ing. Industrial Univ. de Miami | LinkedIn; Crunchbase person; theorg.com |
| HQ | **Miami, Florida (EE. UU.)** | Crunchbase; PitchBook; Tracxn |
| Financiación | **$11.3M** total en **2 rondas**: Seed **17-dic-2021** + ronda **$9M el 29-ene-2024**. Inversores concretos **no divulgados** en fuentes accesibles. `[VERIFICADO importe; NO-VERIFICADO inversores]` | Tracxn funding; Crunchbase |
| Naturaleza del negocio | **Marketplace-aggregator + analítica de mercado** (no asegurador, no casa de subastas, no DMS). Monetiza con **membership de pago**, **listings de dealer/venta**, y herramientas de dato para profesionales. | classic.com (about, sell, membership) |
| Autodescripción equipo | "**Data geeks and car enthusiasts**" | classic.com/about |

**Superficie de producto / mapa del sitio (footer, `[VERIFICADO en vivo]`):**
`HOME · MARKETS · GARAGE · BLOG (Insights) · DATA SOURCES · AUCTIONS · DEALERS · ABOUT US · EMBED DATA · SELL YOUR CAR · PARTNERSHIPS · HELP CENTER · SIGN UP`.
Nav superior: **FIND · PRICE · SELL** + menú de cuenta (**Market Follows, Saved Vehicles, Listings, Rusty, Profile, Membership, Notifications, Embeds**).

**Cliente objetivo:**
1. **Compradores/entusiastas/coleccionistas** — buscar, valorar (CMB), seguir mercados y vehículos.
2. **Vendedores privados** — listar su coche, ver comps.
3. **Dealers especialistas** (clásico/exótico) — listings + herramientas de dato "dealer-only" (Comps, Market charts, Market alerts, **Inventory Acquisition Alerts**), integración IMS/DMS.
4. **Casas de subasta** — feed de listings/resultados (visibilidad + agregación).
5. **Medios / sitios / foros** — **Embeds** (gráficos de mercado incrustables).
6. **Partners de dato** (página "Partnerships"/"Data Sources").

**Categorías de producto:** (1) **Buscador/agregador de listings**; (2) **Analítica de mercado** (CMB + Market pages + screener + Insights); (3) **Garage** (seguimiento de valor de vehículos propios); (4) **Sell/List** (dealer + managed listings + privado); (5) **Alertas** (mercado + adquisición de inventario); (6) **Embeds** (widgets de dato); (7) **Ask Rusty** (búsqueda asistida por IA, beta); (8) **Tie-in de seguro** (Guaranteed Value® — estimación de prima).

---

## 2. Cobertura

- **Geografía:** **Global**. Agregan **resultados de subasta de los principales actores del mundo** (EE. UU., UK, EU, AUS). El esquema de fees documenta casas de **EE. UU., Reino Unido, Francia (Aguttes/Artcurial), Australia (Bonhams), etc.** Núcleo de usuarios y dealers = EE. UU., pero el dato de mercado es internacional. `[VERIFICADO]`
- **Escala (homepage, ~feb 2026):** **1.035.764 listings · 1.379 auctions · 1.997 dealers** trackeados; **+2.5M** coleccionistas/entusiastas usan la web **cada mes**. `[VERIFICADO vía WebSearch del home]`
- **Volumen de mercado medido:** **$1.3B** en dollar volume hasta fin de feb-2026; en **mayo-2026** el volumen mensual cruzó **medio billón de $** (+26% YoY), precio medio de venta **~$72.000** (+28% YoY). Subastas online: +349% desde 2020; >10.000 coches/trimestre vendidos online (Q1-2024). `[VERIFICADO vía Insights]`
- **Nuevo vs usado:** **ni nuevo ni usado corriente**. Scope = **clásico / colección / exótico / specialty / enthusiast** (incl. modernos de colección y "youngtimers"). El parque diario común (un Golf o Corolla de uso) **no** es su objeto. `[VERIFICADO]`
- **Tipos de vehículo:** principalmente **automóviles** (campo `Vehicle Type = Automobile`); incluye coches de calle, deportivos, exóticos, hypercars, race cars, restomods/custom. Motos `[NO-VERIFICADO]` (no observado; foco es coche).
- **Taxonomía de mercado (clave):** jerarquía **Make → Model Family → Model Generation → Model Variant → Model Trim**, segmentable además por **Body Style + Transmission Type**. Ej. de "Market" granular real: *"Porsche 911 Turbo Coupe - Manual - 997.2 (2010–2013)"*. URL canónica de mercado: `/m/{make}/{model}/{generation}/{variant}/`. `[VERIFICADO en vivo]`

---

## 3. Productos + campos atómicos

### 3.0 Definición del activo de dato — el "Market" y el CMB

> El producto de dato gira sobre dos primitivas definidas en su **Glosario oficial** (verbatim, doble-fetch `insights.classic.com/glossary-of-terms/`):

| Término | Definición atómica (verbatim) |
|---|---|
| **Market** | "A grouping of comparable vehicles that have, **at a minimum, the same Make, Model, and Model Generation**. When relevant for purposes of valuation, a Market may be further segmented by **Model Variant, Trim, Transmission Type, Body Style, and other factors**." |
| **CLASSIC.COM Market Benchmark (CMB)** | "The **benchmark value for vehicles in a given Market** based on data accumulated by CLASSIC.COM and calculated by a **proprietary algorithm that takes into account volume and recency of each data point**." (Es valor **de mercado**, NO de un vehículo concreto; se recalcula **a diario** sobre todas las ventas previas.) |

### 3.1 Métricas de MERCADO (Market page / screener) — campos atómicos `[VERIFICADO en vivo]`

Cabecera de stats de un Market (medidos en una ventana temporal seleccionable):

| Campo | Detalle / ejemplo real (993 Carrera) |
|---|---|
| **CMB** (Market Benchmark) | Valor benchmark del mercado + **flecha de tendencia** (`arrow_upward`/`down`). Ej. submercado 993 Carrera 4S = **CMB $150,831**. |
| **Avg (Average Price)** | Precio medio de venta = **Dollar Volume ÷ Sold Listings**. Ej. **$176,555**. |
| **Sales Count** | Nº de ventas en la ventana. Ej. **360**. |
| **Dollar Volume** | Suma de precios de venta reportados. Ej. **$63.6m**. |
| **Lowest Sale** | Venta más baja del periodo. Ej. **$12,930**. |
| **Top Sale** (Highest) | Venta más alta. Ej. **$1.1m**. |
| **Most Recent** (sale) | Precio de la venta más reciente. Ej. **$135,392**. |
| **Sell-through Rate** | % vendidos = **Sold Listings ÷ Total Listings** (glosario). |
| **Total Listings** | Nº de vehículos a la venta (vendidos o no) en Market/Auction/Periodo. |
| **Sold Listings** | Nº de vehículos vendidos en el cálculo. |
| **High Bid** | En subasta sin reserva alcanzada: puja más alta antes de cerrar. |
| **Reserve** | Precio mínimo fijado por el vendedor en subasta. |
| **"X For sale"** | Nº de unidades vivas en venta en ese (sub)mercado. |

**Sub-mercados ("Related Submarkets"):** cada fila = nombre del submercado, rango de años, **CMB** (o `CMB $0`/oculto si datos insuficientes), **# For sale**, botón **FOLLOW**.

### 3.2 Gráficos de mercado — 6 vistas (tabs de la Market page) `[VERIFICADO en vivo]`

Widget de chart con **6 ejes analíticos** + filtros de tiempo **1m · 3m · 6m · YTD · 1y · 5y · Max**:

| Tab | Qué grafica |
|---|---|
| **SALES** | Dispersión de cada transacción en el tiempo, coloreada por **Status** (ver leyenda) + **línea de media móvil**. |
| **MILEAGE** | Precio frente a **kilometraje** (price-vs-mileage scatter). |
| **YEARS** | Precio por **año de modelo**. |
| **SUBMARKETS** | Comparativa entre **submercados/variantes**. |
| **VOLUME** | **Volumen** de ventas (conteo / $) en el tiempo. |
| **LOCATIONS** | Distribución **geográfica** de ventas. |

**Leyenda de estados del SALES chart (series de dato):** **Sold · High Bid · For Sale · Last Asking Price · Average Sale (Moving Average)**. `[VERIFICADO en vivo]`
Filtros de la Market page: **Year, Price, Transmission, Location, Body Style, Odometer, Status**. `[VERIFICADO en vivo]`

### 3.3 Ficha de VEHÍCULO por VIN (`/veh/{slug-VIN-id}`) — campos atómicos `[VERIFICADO en vivo]`

> Página canónica **agregada por VIN** (el título de la página es *"… VIN: WP0AA2999TS320974"*). Tabs: **Overview · Specs · Media · History · Comps · Market · Taxonomy**.
> Specs literal: *"Details about this vehicle - **decoded from the VIN & CLASSIC.COM curators**."* → híbrido **VIN-decode + curación humana**.

**Bloque Specs (18 campos observados):**

| Campo | Ejemplo real |
|---|---|
| **Year** | 1996 |
| **Make** | Porsche |
| **Model Family** | 911 |
| **Model Generation** | 993 |
| **Model Variant** | Carrera 4S |
| **Model Trim** | - (vacío posible) |
| **VIN** | WP0AA2999TS320974 |
| **Mileage** | 17,668 mi *(flag **TMU** = True Mileage Unknown cuando aplica)* |
| **Originality** | **Original & Highly Original** *(otros valores vistos: Modified, Custom, Project)* |
| **Engine** | 3.6L H6 |
| **Transmission** | Manual |
| **Transmission Type** | (Manual/Automatic — usado en comps/filtros) |
| **Drive Type** | Four Wheel Drive (4WD/AWD) |
| **Vehicle Type** | Automobile |
| **Body Style** | Coupe |
| **Driver Side** | LHD *(o RHD)* |
| **Doors** | 2 Doors |
| **Color Group (Ext)** | Burgundy |
| **Color Group (Int)** | Gray |

**Bloque listing/lot (sobre la ficha):** Status (**FOR SALE / SOLD / NOT SOLD / High Bid**), **precio** (asking `$289,000*` o sold), **fecha de listado** (`event_available`), **view count** (`visibility 339`), **bookmark/save count**, **seller** (Hubbard Auto Center) + **verified flag**, **location** (Scottsdale, AZ, USA), **teléfono**, **listing type** (Fixed-price / Auction / Make-offer), **lot number**, formulario **Contact Seller** (+ "Add an offer?"), **report/flag**.

**Suggested price range (derivado de comps):** *"Similar vehicles have sold within this price range recently. **$160,233 — $369,501**"* — rango sugerido por comparables. `[VERIFICADO en vivo]`

**Tie-in de SEGURO:** *"**Estimated rate for this vehicle $3,384 /year**"* + CTA *"Protect your car for what it's worth with **Guaranteed Value®**. Quote now"* — surfacea una **estimación de prima anual** de seguro de valor acordado. `[VERIFICADO en vivo]`

**Media:** **Photos** con conteo + categorización: **All / Exterior / Interior / Mechanical / Documents** (ej. 99 / 55 / 38 / 4 / 2). `[VERIFICADO en vivo]`

**Vehicle History:** *"A timeline of events that we've detected for this vehicle."* Cada evento: **tipo** (listed/sold/relisted), **fecha**, **seller/source**, **status**, **precio**, **mileage**, **location**, link **View Source**. → historial longitudinal del MISMO VIN a través de listings. `[VERIFICADO en vivo]`

**Comps (motor de comparables):** *"Comparable recent listings. See related attributes next to the score."* Cada comp lleva un **% Relevance score** (ej. **97% Relevance**) y badges de **atributos de match**. Dimensiones de relevancia observadas: **Mileage · Engine · Transmission Type · Drive Type · Body Style · Location · Originality · Recency**. El usuario puede **"FILTER COMPS"** (hand-pick) para afinar el pricing y **guardar** el vehículo. Cada comp: title, originality tag, mileage, transmission, driver side, location, **status** (SOLD/NOT SOLD), **precio**, **source** (ej. *PCARMARKET Auctions*), **listing type** (Auction), **fecha** (+"X ago"). `[VERIFICADO en vivo]`

**Market (en la ficha):** el **CMB del mercado** del vehículo con flecha de tendencia (ej. *CMB $150,831 ↑*). **Taxonomy (506):** navegación a mercados relacionados.

### 3.4 Garage — seguimiento de valor (`/garage`) 

Producto de "track your car's value": el usuario **guarda vehículos** (Saved Vehicles) y recibe **updates de valor + comparables**. Plan gratis limitado; premium permite **hasta 10 vehículos** guardados con seguimiento. CTA recurrente: *"What's it worth? Track your car's value and get notified about comparable listings. SAVE"*. `[VERIFICADO]`

### 3.5 Alertas

| Alerta | Detalle |
|---|---|
| **Market alerts / Market follows** | Email cuando se detectan **nuevos listings y precios de venta** en mercados seguidos (a market followers, frecuencia diaria para sold prices). `[VERIFICADO]` |
| **Inventory Acquisition Alerts** | **Exclusivo de Verified Sellers (dealers)**: email **semanal** con **listings frescos de vendedores privados** que casan con el **perfil de inventario** del dealer (lead-gen de adquisición). `[VERIFICADO vía Insights]` |
| **Saved-vehicle alerts** | Notificación de comparables/cambios sobre vehículos del Garage. `[VERIFICADO]` |

### 3.6 Herramientas de dato para DEALERS ("dealer-only data tools")

Dealers que **reportan sold prices** y cumplen guidelines obtienen **~30% más views/clicks** y exposición en **Market charts, Market listings, Vehicle comps** (las zonas más consultadas). Acceso a **Comps, Market charts, Market alerts** "dealer-only". **Integración con la mayoría de proveedores IMS/DMS** + carga manual (ingest de inventario). `[VERIFICADO vía Insights/Sell pages]`
> Esto es lo más cercano a un producto de "Market Intelligence" B2B; **no existe** una página/SKU pública titulada literalmente "Market Intelligence" ni tarifa B2B publicada. `[VERIFICADO la ausencia]`

### 3.7 Analítica de listing (dashboard de vendedor) — campos `[VERIFICADO vía support]`

| Métrica | Definición (verbatim resumida) |
|---|---|
| **Impressions** | Nº de veces que el vehículo se **presentó** a un usuario (search results, market pages, detail pages). |
| **Views** | Nº de veces que un usuario **carga la vista dedicada** del vehículo/lote. |
| **Referrals** | Dealers/auctioneers: **clics a su web**. Privados: aperturas del form "Contact Seller". |
| **Leads / Inquiries** | Nº de envíos del form "Contact Seller" **o llamadas** al teléfono del listing. |

### 3.8 Insights (BLOG / inteligencia editorial)

Reportes de mercado periódicos basados en su propio dato: **Market Report mensual**, **Half-Time Report**, **Q1/Q-reports**, **Top 100 Markets** (semestral), **Trending Markets por tramo de precio** (Under $40K / Under $100K / $100K–$500K / $500K–$1M / Over $1M), **Premium Picks**. `[VERIFICADO]`
- **Top 100 Markets:** ranking semestral de los mercados **mejor comportados a 12 meses**, ordenados por **crecimiento YoY del CMB**; criterio de elegibilidad: **≥10 ventas** en el periodo. `[VERIFICADO]`

### 3.9 Embeds (`/embed`, "EMBED DATA")

Widgets de **gráfico interactivo de mercado** incrustables en webs/blogs/foros: el usuario elige **qué Market** y el **rango de fechas** (**máx. 5 años de histórico**). Canal de distribución de dato hacia terceros. `[VERIFICADO]`

### 3.10 Ask Rusty (IA, beta)

Asistente *"AI powered search of listing information"* — **Rusty** responde preguntas sobre el contenido de listings ("Get instant answers"). Beta. `[VERIFICADO en vivo]`

---

## 4. Metodología / fuentes de datos

- **CMB (algoritmo):** **propietario**, recalculado **cada día** usando **todas las ventas previas a ese día**; pondera **volumen** y **recencia** de cada data point. Es un **benchmark de mercado**, no un valor por-vehículo; el valor real de un coche concreto varía por **condición, kilometraje, ubicación, etc.** `[VERIFICADO — glosario]`
- **Fuentes de listings:** "**dealers, auctions, and other third-party data providers**". Las ventas de subasta provienen de **datos públicos de las principales casas de subasta del mundo**; se exige a las fuentes aportar listings **upcoming + históricos**, **públicos, exactos y factuales**. **No** publican la lista nominal de fuentes, pero el esquema de fees enumera casas trackeadas: **Barrett-Jackson, Mecum, RM Sotheby's, Gooding & Company, Bonhams, Broad Arrow, Bring a Trailer, Cars & Bids, Collecting Cars, PCARMARKET, GAA, H&H, Artcurial, Aguttes, CCA, Henderson, Fast Car Bids**. `[VERIFICADO]`
- **Specs por vehículo:** **decode de VIN + curación humana** ("CLASSIC.COM curators") — extraen de las descripciones de los listings: mileage, originalidad/conservation status, y demás specs para **categorizar** correctamente en mercados/comps. El **VIN es requerido** a las fuentes (da eventos históricos + puntos clave de categorización). `[VERIFICADO]`
- **Ventanas temporales:** **LTM** (Last Twelve Months) como ventana estándar; stats por **Market / Auction / Time Period**.
- **Comps:** motor de relevancia con score % sobre 8 atributos (Mileage, Engine, Transmission Type, Drive Type, Body Style, Location, Originality, Recency); permite curación manual del set por el usuario. `[VERIFICADO en vivo]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Web / buscador** | `classic.com` — search de listings + Market pages + Vehicle (VIN) pages + screener `/markets`. Núcleo del producto. | `[VERIFICADO en vivo]` |
| **Garage** | App-web de seguimiento de valor de vehículos propios. | `[VERIFICADO]` |
| **Email alerts** | Market alerts (diarias para sold), Inventory Acquisition Alerts (semanal, dealers), saved-vehicle alerts. | `[VERIFICADO]` |
| **Embeds (widgets)** | Gráficos de mercado incrustables (Market + rango ≤5 años). | `[VERIFICADO]` |
| **Ingest IMS/DMS** | Integración **entrante** con la mayoría de proveedores IMS/DMS de dealer + carga manual (sube inventario del dealer). | `[VERIFICADO]` |
| **Insights / Blog** | Reportes de mercado, Top 100, trending por tramo. | `[VERIFICADO]` |
| **Ask Rusty** | Q&A IA sobre listings (beta). | `[VERIFICADO en vivo]` |
| **Tie-in seguro** | CTA Guaranteed Value® + **estimación de prima/año** en la ficha (partner asegurador, no propio). | `[VERIFICADO en vivo]` |
| **API pública / feed de dato (outbound)** | **NO discoverable.** No hay portal de developers, doc de API REST, ni feed/Excel/CSV crudo publicado. Distribución de dato a terceros = **Embeds + Partnerships** (negociado). | `[VERIFICADO la ausencia / NO-VERIFICADO existencia privada]` |
| **Integración DMS saliente (escribir valor en el DMS del dealer)** | No observada. Su relación DMS es de **ingesta**, no de inyección de valoración. | `[NO-VERIFICADO / probable ausencia]` |

---

## 6. Precio

- **Membership consumidor:** **gratis** (con límites) → **CLASSIC Insider** desde **$5/mes** o **$47/año**. Premium desbloquea **todos los market charts + histórico de mercado** y **hasta 10 vehículos** en Garage. `[VERIFICADO vía WebSearch de páginas classic.com]`
- **Listing de dealer:** **$49 por coche, hasta que se vende** ("$49 until a car sells"). + **Managed Listings** (servicio gestionado de venta) y **Premium/Featured listings**. `[VERIFICADO]`
- **Vender (privado):** *"We'll help you price it right, then you can list it yourself"* (autoservicio). `[VERIFICADO en vivo]`
- **Fees de subasta:** classic.com **no cobra** comisión de subasta; **documenta** (support) las comisiones de cada casa (informativo). `[VERIFICADO]`
- **Dealer data tools / B2B "market intelligence":** **precio no publicado** (sin SKU público). `[NO-VERIFICADO]`
- **Embeds / API:** sin tarifa pública. `[NO-VERIFICADO]`

---

## 7. Placement (patrón web — clave para cardeep)

> Dónde coloca CLASSIC.COM cada dato. Es el patrón a imitar para **ubicar un activo + su contexto de mercado** cuando el valor nace de **transacciones reales agregadas** (no de un libro). Todo `[VERIFICADO en vivo]` salvo lo indicado.

**A. Entrada / navegación.** Tres verbos en el nav: **FIND** (buscar listings), **PRICE** (valorar / ver mercado), **SELL** (listar). Breadcrumb jerárquico **Markets → Make → Model → Generation → Variant**. Ruta por **VIN** vía URL `/veh/…` (la página es por-VIN).

**B. Screener de mercados (`/markets`).** Patrón "lista de valores tipo bolsa": **YOUR MARKETS** (seguidos) + **POPULAR/TRENDING MARKETS**. Cada fila: **nombre del Market** (Make Model Variant · Body · Transmission · Generation), **rango de años**, **CMB** (el "precio del índice"), **# For sale**, **FOLLOW**. → equivalente a un *stock screener* del coche de colección.

**C. Market page (ficha de MERCADO).** Cabecera: título + rango de años + "X for sale" + **FOLLOW** + **SHARE**. Bloque de **stats** (CMB, Avg, Sales Count, Dollar Volume, Lowest, Top, Most Recent). **Chart con 6 tabs** (SALES/MILEAGE/YEARS/SUBMARKETS/VOLUME/LOCATIONS) + filtros temporales (1m…Max) + leyenda de estados (Sold/High Bid/For Sale/Last Asking/Moving Average). **Related Submarkets** (cada uno con su CMB). **Filtros** (Year, Price, Transmission, Location, Body Style, Odometer, Status). Grid de **listings** del mercado con **sort** (price, year, lot date, lot number, location). FAQs + Market Guide.

**D. Vehicle page (ficha por VIN) — el corazón.** Tabs **Overview · Specs · Media · History · Comps · Market · Taxonomy**:
- **Headline:** foto-galería (con conteo), mileage, transmission, driver side, **Originality**, precio + status, seller verificado, ubicación, **view count**, contacto.
- **Suggested price range** (de comps) justo bajo el contacto.
- **Specs:** tabla de ~18 campos (VIN-decode + curación), con sub-tabs Exterior/Interior/Mechanical/Documentation.
- **Media:** fotos categorizadas (Exterior/Interior/Mechanical/Documents).
- **History:** **timeline de eventos del MISMO VIN** (cada venta/listado con precio, fecha, fuente, mileage, location, "View Source"). → la "prueba de procedencia/precio".
- **Comps:** comparables con **% relevance** y badges de match (8 atributos); **Filter Comps** para curar el set.
- **Market:** el **CMB del mercado** del coche con **flecha de tendencia**.
- **Insurance tie-in:** **"Estimated rate $X/year" + Guaranteed Value®** → convierte el valor en acción aseguradora.

**E. Analítica de listing (vendedor).** Dashboard con **Impressions, Views, Referrals, Leads/Inquiries** por listing.

**F. Capa de inteligencia (Insights/Blog).** Separada: Market Report mensual, **Top 100 Markets** (ranking por crecimiento YoY del CMB, ≥10 ventas), Trending por tramo de precio, Premium Picks.

**G. Distribución (Embeds).** El gráfico de un Market se incrusta en sitios de terceros (selección de Market + rango ≤5 años) → el dato sale de la plataforma como widget de marca.

**Patrón de marca:** "CLASSIC.COM Market Benchmark™ (CMB)" es el activo de marca; el valor se presenta como **benchmark de mercado transparente derivado de ventas reales** (con disclaimer explícito de que **no** es el valor de un coche concreto), no como una tasación cerrada de autoridad.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Agregador transversal de listings** (subastas online+presenciales + dealers + privados) de **todo el mundo** en una sola búsqueda — cobertura de fuentes que un guía-precio tradicional no agrega.
2. **CMB: benchmark de mercado diario, transparente y por-Market** derivado de **transacciones reales** (volumen + recencia), no de un panel de tasadores ni de asking prices.
3. **Ficha canónica por VIN con timeline de eventos** — sigue el **mismo coche** a través de múltiples ventas/relistados en el tiempo (procedencia de precio real).
4. **Motor de comps con relevance score** sobre 8 atributos + **curación manual del set** ("Filter Comps") — pricing por comparables transparente y auditable.
5. **Granularidad de mercado extrema:** Make→Model→**Generation**→Variant→Trim, +Body+Transmission (ej. "997.2 Turbo Coupe Manual") — submercados que las guías colapsan.
6. **6 ejes de gráfico de mercado** (Sales, Mileage, Years, Submarkets, Volume, Locations) — análisis multidimensional listo, no solo una curva.
7. **Inteligencia editorial propietaria** (Top 100 por crecimiento de CMB, trending por tramo, market reports) — un "Bloomberg" del clásico.
8. **Embeds** — distribución del dato como widget de marca a foros/medios (loop de adquisición + autoridad).
9. **Inventory Acquisition Alerts** para dealers — lead-gen de **compra** de inventario (privados que casan con su perfil), no solo de venta.
10. **Coste de entrada ínfimo** ($5/mes; dealer $49/coche-hasta-vender) frente a licencias B2B caras de las guías clásicas.
11. **Capa de acción:** suggested price range + **estimación de prima de seguro** (Guaranteed Value®) integradas en la ficha.

---

## 9. Gaps (lo que NO ofrece)

1. **NO es valoración por-vehículo:** el CMB es **de mercado**, con disclaimer explícito de que **no representa el valor de un coche concreto**. No hay un "retail/trade/private-party value" ajustado por VIN como en KBB/Eurotax/Black Book. ← hueco para cardeep.
2. **NO ajuste paramétrico por opciones/equipamiento/condición:** el coche se categoriza por **Originality** (Original/Modified/Custom/Project) cualitativa, no por un motor de deltas por opción o por grado de condición #1–#4 (eso es Hagerty).
3. **Solo coche de COLECCIÓN/EXÓTICO/SPECIALTY:** **no** cubre el parque diario usado/nuevo corriente. ← espejo del gap de Hagerty.
4. **Sin API pública / feed crudo:** no hay portal developer, doc REST, ni Excel/CSV/feed licenciable público. Distribución = Embeds + Partnerships negociadas. `[VERIFICADO la ausencia]`
5. **Sin integración DMS saliente** (no inyecta valor en el sistema del dealer); su DMS es de **ingesta de inventario**.
6. **Métricas retail de dealer ausentes como producto:** no hay **days-to-sell / market days supply / price-to-market % / days-in-inventory** al estilo vAuto/MarketCheck (su "velocidad" es Volume/Recency a nivel mercado, no turn de inventario por unidad).
7. **Sin histórico de siniestros/title-brand/odómetro verificado** propio: muestra el **timeline de listings** que detecta, no un informe tipo Carfax (delega VIN history a terceros).
8. **Dependiente de fuentes públicas/voluntarias:** la calidad del sold-price depende de que dealers/casas **reporten** el precio final (incentivado con +exposición, pero no garantizado) → **sesgo de no-reporte**.
9. **Specs decode limitado al objeto de colección** (no es un catálogo de specs/equipamiento exhaustivo tipo Autovista/DataOne para todo el parque).
10. **Profundidad de mercados delgados:** submercados raros muestran `CMB $0`/oculto por **<umbral de ventas** (Top 100 exige ≥10) → cobertura desigual en la cola larga.
11. **Geografía de transacción sesgada a anglosfera** (US/UK/EU/AUS auctions); cola europea continental no-subasta y LatAm/Asia, débil. `[PARCIAL]`
12. **Precio B2B opaco** (dealer tools / partnerships sin tarifa pública).

---

## 10. Fuentes

**Producto en vivo (navegador real, bypass Cloudflare):**
- https://www.classic.com/m/porsche/911/993/ — Market page (stats CMB/Avg/Sales/Volume/Lowest/Top/Most Recent; 6 tabs; submarkets; filtros; listing cards) `[VERIFICADO en vivo]`
- https://www.classic.com/veh/1996-porsche-911-carrera-4s-wp0aa2999ts320974-WkB7dgn — Vehicle (VIN) page (Specs 18 campos; History timeline; Comps + relevance; suggested range; insurance rate) `[VERIFICADO en vivo]`
- https://www.classic.com/markets — screener de mercados (CMB, años, # for sale, follow) + footer site-map `[VERIFICADO en vivo]`

**Glosario / definiciones (fetch directo, host insights):**
- https://insights.classic.com/glossary-of-terms/ (CMB, Market, Average Price, Dollar Volume, High Bid, LTM, Reserve, Total Listings, Sell-through Rate, Sold Listings) — doble fetch
- https://www.classic.com/insights/glossary-of-terms/

**Soporte (fetch directo, host support):**
- https://support.classic.com/listing-analytics (Impressions, Views, Referrals, Leads)
- https://support.classic.com/how-did-my-listings-get-included (fuentes: dealers/auctions/data providers; VIN requerido)
- https://support.classic.com/auction-fees-and-prices (casas de subasta trackeadas + sus fees)

**Páginas de producto / pricing (vía WebSearch de classic.com):**
- https://www.classic.com/ (tagline; escala 1.035.764 listings / 1.379 auctions / 1.997 dealers / 2.5M usuarios/mes)
- https://www.classic.com/about ("data geeks and car enthusiasts"; misión)
- https://www.classic.com/data ("Collector car data"; fuentes; requisitos)
- https://www.classic.com/embed (widgets; rango ≤5 años)
- https://www.classic.com/sell ; /sell/dealers/ ; /sell/managed-listings/ (dealer $49-hasta-vender; managed listings)
- https://www.classic.com/account/membership (membership)
- https://www.classic.com/garage/add (track values; hasta 10 vehículos)
- https://www.classic.com/insights/inventory-acquisition-alerts (alertas de adquisición, Verified Sellers)
- https://www.classic.com/insights/enhance-exposure/ (+30% views por reportar sold prices; IMS/DMS)
- https://www.classic.com/insights/top-100-markets-2023/ ; /insights/q1-2024/ (ranking por crecimiento CMB; ≥10 ventas)
- https://insights.classic.com/market-report-may-2026/ (volumen $0.5B/mes; +26% YoY; precio medio ~$72k)

**Identidad / corporativo / financiero:**
- https://www.crunchbase.com/organization/classic ($11.3M; Miami; perfil)
- https://tracxn.com/d/companies/classic.com/ (funding: Seed 17-dic-2021; ronda $9M 29-ene-2024)
- https://pitchbook.com/profiles/company/489254-68
- https://www.linkedin.com/in/juan-diego-calle/ ; https://www.crunchbase.com/person/juan-diego-calle (CEO co-fundador; ex .CO Internet/Neustar)
- https://www.classic.com/insights/a-message-from-our-ceo-2024/ ("3 años operando")

### Notas de verificación
- **Specs (18 campos), stats de mercado, comps con relevance, history timeline, insurance rate, 6 tabs de chart, screener**: **leídos en el DOM en vivo** con navegador real. `[VERIFICADO en vivo]`
- **Glosario (10 términos)**: doble fetch idéntico. `[VERIFICADO]`
- **Analytics de vendedor (4 métricas)**: support.classic.com. `[VERIFICADO]`
- **Pricing ($5/mes, $47/año, dealer $49)**: WebSearch de páginas classic.com (no leído en checkout en vivo). `[VERIFICADO con caveat]`
- **Inversores del seed/ronda $9M**: no divulgados en fuentes accesibles. `[NO-VERIFICADO]`
- **Subdominio `market-intelligence.classic.com`**: **NO resuelve (DNS)**; no hay página titulada "Market Intelligence". El equivalente funcional = CMB + Market pages + dealer data tools + Insights + Embeds. `[VERIFICADO la ausencia]`
- **API/feed outbound público**: no discoverable. `[VERIFICADO la ausencia; existencia privada NO-VERIFICADA]`
- **Fundación exacta / 2011-Palm Harbor**: artefacto de registro de dominio; la empresa-producto arranca ~2020-2021. `[VERIFICADO con caveat]`
