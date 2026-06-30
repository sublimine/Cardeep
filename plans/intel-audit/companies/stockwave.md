# Stockwave (vAuto · Cox Automotive) — Auditoría atómica

> Slug: `stockwave` · Subdominio cardeep: **wholesale-intelligence** · Región: **Norteamérica (EE. UU.)**
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes o leído en su propia página primaria), `[PARCIAL]` (1 fuente / agregador), `[NO-VERIFICADO]` / `[CLAIM-VENDOR]` donde no se confirmó de forma independiente, `[RECONSTRUIDO]` donde compongo el dato a partir de varias páginas sin que el vendedor lo liste literalmente.
> Naturaleza: **software de SOURCING / ADQUISICIÓN MAYORISTA** (wholesale buying) para concesionarios. No es un libro de valor ni una guía de valoración: es la **capa de decisión de COMPRA en subasta** — "qué comprar, dónde encontrarlo, cuánto pagar para ser rentable y cómo rendirá el coche en mi lote" — que agrega múltiples libros de valor de terceros (MMR, Black Book, NADA/J.D. Power, KBB, Galves) + el retail-book propietario de vAuto (**rBook™**) + señales de demanda (Autotrader Scarcity) en **una sola pantalla por vehículo de subasta**, y devuelve un **Stockwave Max Bid** y una **Strategy Action**.
> Es un producto de **vAuto** (marca de **Cox Automotive** / Cox Enterprises). Comparte el motor **Live Market View** y se integra nativamente con **Provision, ProfitTime GPS, KBB Instant Cash Offer, Manheim/Simulcast y Upside (disposición mayorista)**. Lanzado ~2016; nombre interno/legado de la app móvil: **AuctionGenius**.
> Páginas: `vauto.com/products/stockwave/` (producto), `vauto.com/independent/wholesale/products/stockwave/` (versión independiente), `vauto.com/resources/stockwave-plus/` + `cloud.e.vauto.com/stockwave-plus` (Stockwave Plus), `vauto.com/what-do-i-know-about-this-car/` (demo interactiva con los data points), `vauto.com/uberflip/stockwave-gross-calculator/` (calculadora ROI).
>
> ⚠ Nota de método: este fichero audita **Stockwave como producto atómico**. El padre `vauto.md` cubre vAuto completo y lista Stockwave como un módulo (§3.7). Aquí se profundiza solo en Stockwave. Investigación con **WebSearch + WebFetch + Playwright** (lectura directa del HTML renderizado de la página de producto). **exa MCP NO disponible** en el entorno (ToolSearch "exa…" devolvió solo gbrain/claude-mem/WebFetch/WebSearch). La página `cloud.e.vauto.com/stockwave-plus` y el PDF de términos Cox no se pudieron renderizar limpios (422/JS/binario) → datos de Plus tomados del **snippet del propio vendedor surfaced por WebSearch** (marcado).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **Stockwave** (a veces "vAuto Stockwave") | vauto.com/products/stockwave `[VERIFICADO]` |
| Nombre legado de la app | **AuctionGenius** (bundle ID `com.vauto.auctiongenius`; App Store id 606985669) | Google Play; Apple App Store `[VERIFICADO ×2]` |
| Owner / grupo | **vAuto, Inc.** → **Cox Automotive** (división de **Cox Enterprises**) | App Store ("vAuto, Inc."); vauto.com `[VERIFICADO]` |
| HQ | **Oakbrook Terrace, Illinois, EE. UU.** (HQ de vAuto) | prnewswire 2019 (dateline Oakbrook Terrace); vauto.md `[VERIFICADO]` |
| Fundación del producto | **~2016** — solución standalone de sourcing wholesale en subastas (dentro de vAuto, fundada 2005 por Dale Pollak) | dalepollak.com/vauto (vauto.md §timeline) `[PARCIAL]` |
| Hito clave | **12-jun-2019** — vAuto añade **4 métricas de mercado clave** (Autotrader Scarcity Index + 3 métricas rBook) a **todos** los dealers de Stockwave (antes solo para los que tenían Provision) | prnewswire 300864159; autoremarketing `[VERIFICADO ×2]` |
| Roles nombrados | **Patrick Janes** (Business Development Director, Stockwave) · **Dale Pollak** (fundador vAuto, autor de los vídeos Stockwave Plus) | prnewswire 2019; vauto.com/resources/stockwave-plus `[VERIFICADO]` |
| Categoría | **Wholesale vehicle sourcing / auction buying software** | vauto.com `[VERIFICADO]` |
| Promesa núcleo | *"Stockwave tells you what to buy, where to find it and how much to pay to be profitable"* / *"Buy the right cars at the right price, every time"* | vauto.com/products/stockwave `[VERIFICADO]` |

**Variantes de producto:**

| Variante | Qué es | Fuente |
|---|---|---|
| **Stockwave** (estándar) | Sourcing en **300+ marketplaces**, 15+ data points, Live Market View, Lightbulbs, Simulcast, app móvil, Saved Searches, VIN-Click, Business Plans | vauto.com/products/stockwave `[VERIFICADO]` |
| **Stockwave Plus** | Integración ampliada: **50+ subastas**, **Live Auction Integration** con **lane monitor alerts**, **Cross-auction Research** (condition reports de subastas de todo el país) y **Enhanced Strategy Page** | cloud.e.vauto.com/stockwave-plus (vía WebSearch del vendedor) `[VERIFICADO — vendor page vía search]` |
| **Stockwave para independientes** | Misma feature-list, página dedicada a dealers independientes | vauto.com/independent/wholesale/products/stockwave `[VERIFICADO]` |
| **App móvil (AuctionGenius)** | iOS (15.0+) + Android; VIN scan, run lists, bid guidance, profit projections | App Store; Google Play `[VERIFICADO ×2]` |

**Cliente objetivo:** concesionarios **franquiciados e independientes** que **compran en subastas mayoristas** (wholesale dealer auctions / dealer-only auctions). Usuarios: **used-car buyers, used-car managers, pre-owned directors, GMs**. *"Built for dealerships that buy at wholesale car dealer auctions—franchise or independent."* `[VERIFICADO — vauto.com]`

---

## 2. Cobertura

- **Geografía: SOLO ESTADOS UNIDOS.** Todas las subastas, marketplaces, testimonios (Performance Toyota, Kelley Automotive Group, Ourisman Lexus) y la app son de EE. UU. **Sin Europa ni global.** ← hueco mayor para cardeep. `[VERIFICADO por ausencia + nationwide]`
- **Nuevo vs usado:** **SOLO USADO** (wholesale de coche usado). El sourcing de coche nuevo lo cubre el producto hermano **Conquest**, no Stockwave. `[VERIFICADO]`
- **Etapa del ciclo:** **adquisición / compra mayorista** (upstream). No es retail, no es disposición (eso es **Upside**), no es recon (eso es **iRecon**). Es el **punto de COMPRA en subasta**. `[VERIFICADO]`
- **Tipos de vehículo:** turismos/light-duty de retail de concesionario (cars/trucks/SUV) que pasan por subasta dealer. No moto, RV, flota pesada como guía. `[PARCIAL]`
- **Escala / frescura:** **~300.000 vehículos/día** accesibles desde **300+ marketplaces**, respaldados por el **Live Market View** "up-to-the-minute". Stockwave Plus llega a **50+ subastas** con integración en vivo. `[VERIFICADO]`
- **Naturaleza del catálogo:** no es un catálogo de valores estático — es el **run-list vivo de las subastas** (lo que está físicamente/digitalmente a la venta hoy) enriquecido con valores de mercado. `[VERIFICADO]`
- **Ecosistema de dato (ventaja Cox):** Live Market View se nutre de **Manheim** (MMR, condition reports, Simulcast), **Autotrader** (Scarcity / señales de demanda retail), **KBB** (ICO), **Dealer.com** — dato propietario difícil de replicar. `[VERIFICADO]`

---

## 3. Productos + campos atómicos

### 3.0 Qué hace Stockwave (las 4 preguntas)

vAuto estructura Stockwave alrededor de **4 preguntas de decisión** que muestra como pilares en la propia página de producto:

| Pregunta | Qué resuelve | Dato que la responde |
|---|---|---|
| **What to Buy** | Qué vehículos encajan en mi lote y mis profit goals | Recomendaciones de stocking + third-party data + Live Market View |
| **Where to Find It** | Localizar la mejor opción en subastas nationwide (online o in-lane) | Búsqueda en 300+ marketplaces, seller/auction source |
| **How Much to Pay** | Pagar el precio correcto y proteger el margen | **Stockwave Max Bid** (target retail − profit − recon − transporte) |
| **How a Car Will Perform** | Predecir el rendimiento antes de comprar | Demanda + pricing + market trends en tiempo real |

(Fuente: vauto.com/products/stockwave, texto renderizado. `[VERIFICADO]`)

### 3.1 LOS 15+ DATA POINTS POR VEHÍCULO (Live Market View) — enumeración atómica

> Estos son los **"15+ trusted data points"** que Stockwave muestra **side-by-side por cada coche de subasta**. Enumerados literalmente desde la **demo interactiva oficial** `vauto.com/what-do-i-know-about-this-car/` (con números de ejemplo del propio vendedor). **Es el hallazgo clave de esta auditoría.**

| # | Data point | Definición atómica | Ej. (vendedor) | Fuente |
|---|---|---|---|---|
| 1 | **Provision® Appraised Value** | Valor tasado por Provision basado en **tu** appraisal; **sigue al vehículo a través de la venta** (conecta compra→retail). | $19,000 | what-do-i-know; vauto.com `[VERIFICADO ×2]` |
| 2 | **MMR Wholesale Average** | **Manheim Market Report**: valor mayorista medio de subasta (hermana Cox). | $18,050 | what-do-i-know `[VERIFICADO]` |
| 3 | **Black Book Wholesale Average** | Valor mayorista medio de **Black Book** (3rd-party, competidor de KBB). | $18,725 | what-do-i-know `[VERIFICADO]` |
| 4 | **J.D. Power Clean Trade-in** | Valor trade-in "clean" de **J.D. Power / NADA**. | $20,125 | what-do-i-know `[VERIFICADO]` |
| 5 | **rBook™ Adjusted Avg. List Price** | **rBook Adjusted Market Average Price**: precio retail medio real del mercado **ajustado por el kilometraje del inventario de los competidores** (tecnología propietaria vAuto). | $22,430 | what-do-i-know; prnewswire 2019 `[VERIFICADO ×2]` |
| 6 | **Autotrader® average listing** | Precio medio de **anuncio** en Autotrader. | $20,252 | what-do-i-know `[VERIFICADO]` |
| 7 | **CarGurus average listing** | Precio medio de **anuncio** en CarGurus (3rd-party). | $19,211 | what-do-i-know `[VERIFICADO]` |
| 8 | **rBook™ Average Odometer** | **Market Average Odometer**: kilometraje medio de los vehículos retail en el mercado del dealer. | 29,684 mi | what-do-i-know; prnewswire 2019 `[VERIFICADO ×2]` |
| 9 | **rBook Days Supply** | **rBook Market Days Supply**: si el vehículo se venderá rápido dado el stock competidor y las ventas recientes. | 120 | what-do-i-know; prnewswire 2019 `[VERIFICADO ×2]` |
| 10 | **rBook "Like Mine" Days Supply** | Days Supply afinado a vehículos **idénticamente equipados** ("like mine"), no genérico. | 69 | what-do-i-know `[VERIFICADO]` |
| 11 | **Autotrader® Scarcity Index** | Demanda de **búsqueda online** de un coche **relativa al número disponible** en el área de mercado (upstream de demanda). | 70 | what-do-i-know; prnewswire 2019; one-two-punch `[VERIFICADO ×3]` |
| 12 | **Condition Report (grade)** | Calificación de condición del coche de subasta en escala **1–5**. | 4.1 | what-do-i-know `[VERIFICADO]` |
| 13 | **CARFAX® Status** | Estado del historial CARFAX (badge numérico / check / caution). | check/caution | what-do-i-know `[VERIFICADO]` |
| 14 | **Stockwave Max Bid** | **Puja máxima recomendada**: lo máximo que debes pagar para cumplir tu profit goal (target retail − profit − recon − transporte). | $21,620 | what-do-i-know; 4-problems `[VERIFICADO ×2]` |
| 15 | **Stockwave Strategy Action** | Indicador **numérico** de estrategia (+/−) que resume si el coche es buena jugada para tu mercado (p. ej. +3, −1, +6). | +3 / −1 / +6 | what-do-i-know `[VERIFICADO]` |

> *"The additional data you get with Stockwave is information you can't get anywhere else."* (vauto.com/what-do-i-know-about-this-car). `[CLAIM-VENDOR]`

### 3.2 Libros de valor adicionales accesibles (vía app / suscripción)

La **app móvil** confirma acceso a guías de precio adicionales **según tu suscripción**: **MMR, KBB, Black Book, NADA, Galves**. Es decir, Stockwave **agrega múltiples libros de valor de terceros** (no solo el ecosistema Cox), además de su rBook propietario. (Fuente: App Store / Google Play. `[VERIFICADO ×2]`)

| Libro | Tipo de valor | Fuente |
|---|---|---|
| **MMR (Manheim Market Report)** | Mayorista de subasta (Cox) | App Store; what-do-i-know `[VERIFICADO]` |
| **KBB (Kelley Blue Book)** | Retail/trade + **Instant Cash Offer (ICO)** | App Store; vauto.com connections `[VERIFICADO]` |
| **Black Book** | Mayorista/trade | App Store; what-do-i-know `[VERIFICADO]` |
| **NADA / J.D. Power** | Trade-in / retail | App Store; what-do-i-know `[VERIFICADO]` |
| **Galves** | Mayorista | App Store `[VERIFICADO]` |
| **rBook™** (propietario vAuto) | **Retail book** de coches idénticamente equipados en vivo | prnewswire 2019; caredge `[VERIFICADO]` |

### 3.3 Features funcionales (herramientas de Stockwave)

| Feature | Definición atómica | Fuente |
|---|---|---|
| **Live Market View** | Capa de 15+ data points por vehículo (pricing, demanda, oferta, detalles de subasta) comparados side-by-side. | vauto.com `[VERIFICADO]` |
| **Lightbulbs** | Guía **"appraisal-like" de un clic**: al pulsar la bombilla en un coche (o en una **Instant Cash Offer**), despliega los 15+ data points + **CARFAX report**. | vauto.com `[VERIFICADO]` |
| **Glance** | Vista rápida que **totaliza tus costes (recon + transporte)** y los calcula contra tu **target retail price** para evaluar el potencial del vehículo. | resources/glance (vía WebSearch del vendedor) `[VERIFICADO — vendor]` |
| **Saved Searches / wish lists** | Búsquedas y wish lists reutilizables; Stockwave recuerda tus criterios para prep de subasta. | vauto.com `[VERIFICADO]` |
| **Auction Simulcast** | Unirse a subastas dealer en vivo **online**: ver, **pujar y comprar en tiempo real** desde múltiples marketplaces en un sitio (experiencia "in-lane online"). | vauto.com; simulcast resource `[VERIFICADO]` |
| **Mobile App (AuctionGenius)** | Buscar/evaluar/comprar desde el móvil; **VIN scan**, run lists, notas por vehículo, bid guidance + profit projections en tiempo real. | App Store; Google Play `[VERIFICADO ×2]` |
| **Set Profit Goals (Business Plans)** | Fija **profit targets** y **filtra vehículos por profit potential** — solo ves los coches que cumplen tu objetivo. | vauto.com `[VERIFICADO]` |
| **VIN-Click Extension** | Extensión de navegador: convierte **cualquier VIN válido** en una appraisal de vAuto con un clic (abre ventana de appraisal nueva, sin tecleo manual). | vauto.com `[VERIFICADO]` |
| **Personalized recommendations / stocking-level** | Recomendaciones de stocking basadas en **tu mercado + tus preferencias de compra + tu exit strategy**. | vauto.com `[VERIFICADO]` |
| **Strategy Page (grid de stocking)** | Rejilla **segmentos (columnas) × bandas de precio (filas)** con **ventas históricas a 125 días** que marca **sobre-stock vs infra-stock** por categoría. (En **Stockwave Plus** = "Enhanced Strategy Page" con movimientos de mercado por segmento.) | 4-problems autoremarketing; cloud.e Plus `[VERIFICADO]` |

### 3.4 Stockwave Plus — deltas sobre el estándar

| Capacidad | Definición atómica | Fuente |
|---|---|---|
| **50+ auctions** | Acceso a **más de 50 subastas** (vs el pool general de 300+ marketplaces del estándar). | cloud.e.vauto.com/stockwave-plus `[VERIFICADO — vendor vía search]` |
| **Live Auction Integration + Lane Monitor Alerts** | Participar en subastas en tiempo real con **alertas de monitor de lane** para no perder el coche cuando baja por la pista. | cloud.e Plus `[VERIFICADO — vendor vía search]` |
| **Cross-auction Research** | Ver **detalles de vehículo + condition reports** de subastas de **todo el país** para precisar qué coches darán más gross en tu mercado. | cloud.e Plus `[VERIFICADO — vendor vía search]` |
| **Enhanced Strategy Page** | Dashboard que muestra **qué movimientos hace el mercado en un segmento** para fijar la estrategia de stocking. | cloud.e Plus `[VERIFICADO — vendor vía search]` |

### 3.5 Calculadora de gross (Stockwave Gross Calculator) — campos

Herramienta de ROI (no parte de la decisión por-coche, sino del caso de negocio). **Inputs:** (1) *Average Front-End Gross on Auction-Sourced Units* ($), (2) *Average Monthly Unit Sales* (n.º), (3) *Units Sourced From Auction Each Month* (n.º), (4) *Time Spent Sourcing (Hours Per Week)*. **Outputs comparativos (actual vs con Stockwave):** *Annual Front-End Gross*, *Monthly Average Unit Sales*, *Annual Time Spent Sourcing*. **Supuestos del vendedor:** +10% ventas retail mensuales, +25% front-end gross, −50% tiempo de sourcing. (Fuente: vauto.com/uberflip/stockwave-gross-calculator. `[VERIFICADO; supuestos = CLAIM-VENDOR]`)

### 3.6 Cómo se calcula el Stockwave Max Bid (mecánica de pricing)

Stockwave parte del **target retail price** (precio al que el dealer puede vender), le resta el **profit margin deseado**, los **gastos de reacondicionamiento** y el **transporte**, y devuelve el **máximo que el dealer debería pagar** para cumplir su profit goal. Resuelve "cuánto pagar / si el coche es demasiado caro" — una pregunta que de otro modo cuesta horas. (Fuente: autoremarketing 4-problems; WebSearch Max Bid. `[VERIFICADO]`)

### 3.7 Identidad / spec del vehículo (inputs)

`VIN` (+ VIN scan en móvil) · `year` · `make` · `model` · `trim` · `equipment/options` (rBook compara por **idénticamente equipado** / "like mine") · `odometer/mileage` · `seller / auction source` · `auction location / lane / run list position` · `condition report (1–5)` · `vehicle history` (**CARFAX** + Vehicle History Reports). (Fuentes: what-do-i-know; App Store; one-two-punch. `[VERIFICADO/PARCIAL]`)

---

## 4. Metodología / fuentes de datos

- **Live Market View** = motor de dato propietario de vAuto, alimentado por el **ecosistema Cox** + **terceros**:
  - **Manheim** → **MMR**, condition reports, **Simulcast**, build/auction data. `[VERIFICADO]`
  - **Autotrader** → **Scarcity Index** (demanda de búsqueda online / disponibilidad) y señales de demanda retail. `[VERIFICADO]`
  - **Kelley Blue Book** → valores + **Instant Cash Offer (ICO)**. `[VERIFICADO]`
  - **rBook™** (propietario vAuto) → retail book de coches **idénticamente equipados** en vivo: Adjusted Avg List Price, Market Days Supply, "Like Mine" Days Supply, Market Average Odometer. `[VERIFICADO]`
  - **Terceros agregados:** **Black Book, NADA/J.D. Power, Galves** (libros mayoristas/trade), **CarGurus** (listings), **CARFAX** (historial). `[VERIFICADO]`
- **Naturaleza del dato:** mezcla **mayorista de subasta** (MMR/Black Book/Galves = precio de martillo/trade) + **retail vivo** (rBook/Autotrader/CarGurus = precios de anuncio) + **demanda** (Scarcity) → permite calcular spread compra-vs-retail y velocidad de venta antes de pujar. `[VERIFICADO]`
- **Comparación por equipamiento exacto ("like mine"):** rBook afina days-supply y precio a vehículos idénticamente equipados, no por trim genérico. `[VERIFICADO]`
- **Strategy / stocking:** rejilla segmento × banda de precio con **historial de ventas a 125 días** para detectar sobre/infra-stock. `[VERIFICADO]`
- **Conexión con el ciclo:** el **Provision Appraised Value** generado en la compra **sigue al vehículo a través de la venta** (link Stockwave→Provision→ProfitTime GPS). `[VERIFICADO]`

(Fuentes: vauto.com/products/stockwave; what-do-i-know; prnewswire 2019; App Store; autoremarketing.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Web / SaaS (desktop)** | Consola Stockwave dentro de la plataforma vAuto (login en `vauto.com`); dashboard con grid de vehículos + columnas de data points + Strategy Page. |
| **App móvil — AuctionGenius** | **iOS 15.0+** (iPhone; compatible iPad / Mac M1+ / Vision / iPod touch) y **Android** (`com.vauto.auctiongenius`). Requiere suscripción vAuto activa (AuctionGenius o Stockwave) + cámara con autofocus para VIN scan. Gratis. Rating **3.5/5 (31 ratings)** en App Store. |
| **Extensión de navegador** | **VIN-Click Extension** — cualquier VIN → appraisal vAuto en un clic. |
| **Simulcast (puja en vivo)** | Pujar/comprar en vivo online embebido desde múltiples marketplaces; experiencia "in-lane online". |
| **Integraciones nativas Cox** | **Provision/ProfitTime GPS** (Provision value sigue al coche; ProfitTime ayuda a comprar más de los correctos), **KBB Instant Cash Offer** (lightbulb→15+ data points + CARFAX), **Manheim** (MMR, condition reports, Simulcast), **Upside** (disposición mayorista con precio mínimo garantizado — producto hermano de salida). |
| **Datos de terceros** | Black Book, NADA/J.D. Power, Galves, CarGurus, Autotrader, CARFAX integrados como data points. |
| **Reporting / ROI** | Stockwave Gross Calculator; Strategy Page; Success Stories. |
| **Soporte / activación** | **Performance Consultant** (p. ej. la Scarcity Index se "turn on" contactando al consultor). |

> **API pública:** **no documentada/expuesta**. Igual que el resto de vAuto, la integración es **dentro del stack Cox** + partners DMS, no una API REST abierta para terceros. `[VERIFICADO por ausencia]`

---

## 6. Precio (no público)

| Concepto | Valor | Fuente / nota |
|---|---|---|
| **Modelo** | **SaaS por suscripción**, **cotizado por demo** (sin tarifa pública). Se puede comprar **standalone** o **bundleado** con Provision/ProfitTime GPS. | vauto.com (CTA "Request a Demo"); WebSearch `[VERIFICADO: opaco]` |
| **Standalone Stockwave** | **No público.** Búsquedas repetidas no devuelven cifra oficial ni de agregador para Stockwave standalone. | WebSearch ×3 `[VERIFICADO por ausencia]` |
| **App móvil** | **Gratis** (requiere suscripción vAuto activa). | App Store `[VERIFICADO]` |
| **Contexto de suite vAuto** | Provision ~$1.499/mes; suite vAuto ~$1.000–$5.000/mes (agregadores) — Stockwave entra en ese rango pero **sin desglose propio**. | vauto.md (Capterra/spyne) `[PARCIAL — agregador, no específico de Stockwave]` |

> **Modelo:** suscripción mensual cotizada individualmente; **el número específico de Stockwave no es público** y depende de si va solo o en bundle, tamaño del dealer y volumen. `[VERIFICADO: opaco]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca Stockwave **cada dato**. Reconstruido del HTML renderizado de la página de producto, la demo interactiva `what-do-i-know-about-this-car`, las PR de métricas y la descripción de la app. Patrón rector: **"el mercado al lado del coche de subasta"** — cada decisión de COMPRA se toma frente a 15+ valores + una puja máxima recomendada, en la misma fila/ficha.

**A. Grid de sourcing (pantalla principal — el run-list enriquecido).** Lista de vehículos de **300+ marketplaces** en filas; columnas = **data points de Live Market View**. Cada coche trae su **Lightbulb** (bombilla) que, al pulsar, despliega el **panel de 15+ data points** side-by-side. El **Profit Goal** filtra para que solo aparezcan coches que cumplen el objetivo. **Saved Searches / wish lists** pre-filtran antes de la subasta. → patrón cardeep para un **listado/scoreboard de oportunidades de compra** con KPI por fila + filtro por objetivo.

**B. Panel por vehículo (Lightbulb / "What do I know about this car").** Al abrir un coche, en una sola vista conviven, **side-by-side**: valores mayoristas (**MMR, Black Book, Galves, NADA/J.D. Power**), valores retail (**rBook Adjusted List, Autotrader, CarGurus**), **Provision Appraised Value**, métricas de velocidad/demanda (**rBook Days Supply, "Like Mine" Days Supply, Autotrader Scarcity Index, rBook Avg Odometer**), **Condition Report (1–5)**, **CARFAX Status**, y los **outputs de decisión**: **Stockwave Max Bid** + **Strategy Action (+/−)**. → **este es el patrón estrella para la ficha de coche de cardeep**: apilar todos los libros de valor + demanda + historial + condición y rematar con una recomendación accionable (puja/precio) y un indicador de estrategia.

**C. Glance (evaluación de potencial).** Vista que **totaliza costes (recon + transporte)** y los contrasta con el **target retail price** → muestra el potencial de gross del coche antes de pujar. → patrón cardeep para un **mini-calculador de margen** embebido en la ficha.

**D. Strategy Page (overview de stocking).** Rejilla **segmento × banda de precio** con **ventas a 125 días**: verde/rojo por sobre-stock vs infra-stock; en Plus, **movimientos de mercado por segmento**. → patrón cardeep para un **panel/overview de mercado** que dice qué categorías comprar.

**E. Simulcast (puja en vivo).** La puja en vivo se embebe junto a los data points del coche que baja por la lane; **lane monitor alerts** (Plus) avisan cuando llega tu coche. → patrón cardeep para **alertas + acción en tiempo real** sobre una oportunidad.

**F. Móvil (AuctionGenius, in-lane).** **VIN scan** → al instante "qué pujar"; navegación de **run lists**, **notas por vehículo**, **bid guidance + profit projections**, acceso a los libros de valor según suscripción. → patrón cardeep para **captura por VIN en campo** con valor + recomendación inmediata.

**G. VIN-Click Extension (en cualquier web).** Botón flotante que convierte cualquier VIN de cualquier página en una appraisal vAuto. → patrón cardeep para un **bookmarklet/extensión** que lleva el valor a cualquier listado externo.

**H. Conexiones (cross-product).** El **Provision Appraised Value** nacido en la compra **viaja con el coche** hasta la venta; la **KBB ICO** trae su propia Lightbulb con los 15+ data points + CARFAX. → patrón cardeep para **persistencia del valor de adquisición a lo largo del ciclo**.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Agregador multi-libro en una sola ficha de COMPRA.** Stockwave apila **MMR + Black Book + NADA/J.D. Power + KBB + Galves + rBook + Autotrader + CarGurus + CARFAX** side-by-side por coche de subasta — no un único libro, sino **todos a la vez**, mayorista y retail juntos. Pocos competidores agregan tantas fuentes en el punto de puja.
2. **rBook™ propietario "like mine".** Retail book de vAuto que ajusta **days-supply, precio y odómetro a vehículos idénticamente equipados** ("Like Mine" Days Supply), no por trim genérico.
3. **Autotrader Scarcity Index.** Señal de **demanda de búsqueda online vs disponibilidad** (upstream), combinable con Market Days Supply (downstream) en el "one-two punch" para cazar coches de alto profit que el dealer no habría stockeado por intuición.
4. **Output accionable, no solo valores:** **Stockwave Max Bid** (puja máxima para cumplir profit goal, ya restando recon + transporte) + **Strategy Action (+/−)** — convierte 15 valores en **una decisión**.
5. **300+ marketplaces / 300k vehículos/día** desde el ecosistema Cox (**Manheim/Simulcast**) — escala de sourcing real-time difícil de replicar.
6. **Simulcast + lane monitor alerts (Plus):** experiencia "in-lane online" con puja en vivo y aviso cuando tu coche baja por la pista — monitorizar **múltiples subastas a la vez** desde el escritorio.
7. **Continuidad de valor:** el **Provision Appraised Value** sigue al coche compra→venta (link Stockwave→Provision→ProfitTime GPS); no es una valoración de usar-y-tirar.
8. **Móvil in-lane con VIN scan + bid guidance + profit projections** y **VIN-Click Extension** para appraisal desde cualquier web.
9. **Strategy Page de stocking** (segmento × precio, 125-día) que dice **qué categorías comprar**, no solo cuánto vale un coche concreto.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo EE. UU.** — sin Europa ni global. ← hueco mayor para cardeep. `[VERIFICADO por ausencia]`
2. **Solo USADO y solo COMPRA mayorista.** No coche nuevo (eso es Conquest), no retail/disposición (eso es Upside), no recon (iRecon). Es un **eslabón** del ciclo, no el ciclo. `[VERIFICADO]`
3. **No es libro/autoridad de valor propio citable:** **toma prestados** los valores de terceros (MMR, KBB, Black Book, NADA, Galves) + su rBook; no publica una guía de valores que el consumidor consulte. `[VERIFICADO]`
4. **Sin valor residual / forecast de depreciación multi-anual** (a diferencia de ALG/Autovista/J.D. Power Valuation): su horizonte es **el coche en la subasta ahora** y su days-supply, no la curva a 3-5 años. `[VERIFICADO por ausencia]`
5. **Vehicle history NO propio** — depende de **CARFAX** (y AutoCheck vía el stack vAuto). `[VERIFICADO]`
6. **Sin diagnóstico OBD-II / telemetría** en la decisión (a diferencia de AccuTrade/VinCue VinTel); la condición es el **condition report 1–5 de la subasta**, no un escaneo del coche. `[VERIFICADO por ausencia]`
7. **Sin API pública** documentada para terceros; integración cerrada al stack Cox + DMS partners. `[VERIFICADO por ausencia]`
8. **Atado al ecosistema Cox:** el máximo valor (Manheim/Simulcast/KBB/Autotrader) se materializa dentro de Cox; fuera, menos diferencial. `[VERIFICADO]`
9. **Pricing opaco** (sin tarifa pública de Stockwave standalone). `[VERIFICADO por ausencia]`
10. **App móvil con rating modesto** (**3.5/5**, 31 ratings) — señal de fricción/UX no resuelta. `[VERIFICADO]`
11. **Enumeración exacta de "15+ data points":** el vendedor dice "15+" pero **no los lista en la página de producto**; la lista de §3.1 se extrajo de la **demo interactiva** (15 puntos exactos) — los "+" adicionales (p. ej. Cost-to-Market %, Price-to-Market %, vRank vía Provision) **no aparecen literalmente en el grid de Stockwave** y se infieren de la conexión Provision. `[PARCIAL/RECONSTRUIDO]`
12. **No tasa al consumidor particular** (no es instant-offer al vendedor privado); la captación al cliente pasa por **KBB ICO**, no por Stockwave. `[VERIFICADO]`

---

## 10. Fuentes

**Oficiales / producto (vAuto · Cox):**
- Stockwave (producto, leído renderizado): https://www.vauto.com/products/stockwave/
- Stockwave para independientes: https://www.vauto.com/independent/wholesale/products/stockwave/
- **"What do I know about this car?"** (demo interactiva con los 15 data points + números de ejemplo): https://www.vauto.com/what-do-i-know-about-this-car/
- Stockwave Gross Calculator (inputs/outputs ROI): https://www.vauto.com/uberflip/stockwave-gross-calculator/
- Glance (evaluar potencial; totaliza recon+transporte vs retail): https://www.vauto.com/resources/using-stockwaves-glance-to-evaluate-a-vehicles-potential-vauto/
- Stockwave Plus (resource + landing): https://www.vauto.com/resources/stockwave-plus/ · https://cloud.e.vauto.com/stockwave-plus
- Simulcast + Stockwave ("in-lane experience online"): https://www.vauto.com/resources/how-simulcast-and-stockwave-give-you-an-in-lane-experience-online-vauto/
- Learning Center Stockwave: https://www.vauto.com/learning-center/stockwave
- One-two punch (Scarcity + Market Days Supply): https://www.vauto.com/learning-center/patrick-janes-blog/acquire-high-profit-vehicle-with-a-one-two-punch
- Mobile app — Apple App Store (AuctionGenius, vAuto Inc., 3.5/5, features): https://apps.apple.com/us/app/auctiongenius/id606985669
- Mobile app — Google Play: https://play.google.com/store/apps/details?id=com.vauto.auctiongenius

**Prensa / IR (verificación cruzada):**
- PR Newswire — vAuto introduce métricas clave en Stockwave (12-jun-2019; Scarcity Index + 3 métricas rBook, definiciones): https://www.prnewswire.com/news-releases/vauto-introduces-key-market-metrics-in-stockwave-to-address-rising-used-vehicle-demand-weakening-supply-300864159.html
- AutoSuccessOnline (misma noticia): https://www.autosuccessonline.com/vauto-introduces-key-market-metrics-in-stockwave-to-address-rising-used-vehicle-demand-weakening-supply/
- Auto Remarketing — "4 key metrics now available to all vAuto Stockwave dealers" (definiciones + standalone vs Provision): https://www.autoremarketing.com/ar/4-key-metrics-now-available-all-vauto-stockwave-dealers/
- Auto Remarketing — "4 problems Stockwave aims to solve for dealers" (grid segmento×precio 125-día, Max Bid, sourcing nationwide, one-click auction): https://www.autoremarketing.com/ar/technology/4-problems-stockwave-aims-to-solve-for-dealers/
- Auto Dealer Today — "vAuto Adds Key Market Metrics to Stockwave" (Patrick Janes quote; un dashboard vs spreadsheets): https://www.autodealertodaymagazine.com/news/vauto-adds-key-market-metrics-to-stockwave
- Dale Pollak — Market Days Supply vs Scarcity Index (upstream/downstream): https://www.dalepollak.com/2010/03/market-days-supply-scarcity-index/

**Terceros / contexto:**
- CarEdge — rBook ("real-time prices of identically equipped used cars"): https://caredge.com/guides/what-is-vauto
- Profitable Pre-Owned — vAuto/Stockwave hacks (workflow): https://www.profitablepreowned.com/3-vauto-and-stockwave-hacks-for-increased-productivity/
- Dealer Tech Nerd — vAuto vendor listing (Stockwave en la suite, "biggest data set", integraciones Autotrader/Manheim/VinSolutions): https://dealertechnerd.com/inventory-management-vendors/
- OPENLANE corporate — landscape simulcast Manheim/ADESA (contexto marketplaces): https://corporate.openlane.com/manheim-adesa-and-the-independent-auto-auctions-announce-industry-progress-toward-a-multiplatform-bidding-solution/
- Padre: `vauto.md` (este repo) — vAuto completo, Stockwave §3.7.

### Notas de verificación
- **Los 15 data points (§3.1):** enumerados literalmente desde la demo oficial `what-do-i-know-about-this-car` con números de ejemplo del vendedor. **[VERIFICADO — página primaria]**. Coincide con el "15+ trusted data points" de la página de producto.
- **4 métricas clave (Scarcity Index, rBook Days Supply, rBook Adjusted Avg Price, rBook Avg Odometer) + fecha 12-jun-2019 + standalone-vs-Provision:** PR Newswire + Auto Remarketing + Auto Dealer Today. **[VERIFICADO ×3]**
- **Features (Live Market View, Lightbulbs, Saved Searches, Simulcast, Mobile, Profit Goals, VIN-Click):** texto renderizado de la página de producto + App Store. **[VERIFICADO ×2]**
- **Stockwave Max Bid (mecánica) y grid de stocking 125-día:** Auto Remarketing "4 problems". **[VERIFICADO]**
- **App móvil (AuctionGenius, MMR/KBB/Black Book/NADA/Galves, VIN scan, run lists, bid guidance, 3.5/5):** Apple App Store + Google Play. **[VERIFICADO ×2]**
- **Stockwave Plus (50+ auctions, lane monitor alerts, cross-auction research, Enhanced Strategy Page):** página propia `cloud.e.vauto.com/stockwave-plus` surfaced por WebSearch (no se pudo renderizar limpia: la navegación Playwright se redirigió a un sitio ajeno; WebFetch dio página vacía). **[VERIFICADO — vendor vía search; no confirmado por render directo]**
- **Cifras de uplift (40% gross, 80% outperform, 30% inventory, +10/+25/−50% calculadora, $600 PVR):** material de marketing del vendedor. **[CLAIM-VENDOR]**
- **Precio Stockwave standalone:** no público; sin cifra de agregador específica. **[VERIFICADO por ausencia]**
- **"15+" exactos:** 15 listados en la demo; los "+" extra (Cost/Price-to-Market %, vRank) se infieren de la conexión Provision, no aparecen literalmente en el grid Stockwave. **[PARCIAL/RECONSTRUIDO]**
- **PDF de términos Cox (vAuto-Provision-Conquest-and-Stockwave-Additional-Terms.pdf):** binario no parseable por WebFetch → no aporta. **[NO-VERIFICADO]**
- **exa MCP:** NO disponible en el entorno. Investigación con **WebSearch + WebFetch + Playwright (render directo de la página de producto)**. **[NOTA DE MÉTODO]**
