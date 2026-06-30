# Orange Book Value (OBV) — Auditoría Atómica de Inteligencia Competitiva

> **Slug:** `orange-book-value-obv` · **Web:** https://orangebookvalue.com/ (entrada dada: `/global-gr`) · **Vertical cardeep:** valuation
> **Auditado:** 2026-06-30 · **Método:** lectura directa de páginas de producto, enterprise, metodología, premium-reports, homepage y blog del sitio vivo vía WebFetch + verificación cruzada con prensa del sector (Inc42, Business Standard, Deccan Chronicle/Asian Age, Entrackr, AIM Group), Tracxn (perfil corporativo) y stores (Google Play / App Store).
> **Nota de subdominio:** `valuation.orangebookvalue.com` **NO resuelve en DNS** [VERIFICADO: HTTP 000 / NXDOMAIN, `nslookup` 2026-06-30]. En cambio `orangebookvalue.com/valuation` **SÍ existe** [VERIFICADO: HTTP 200] y es la **calculadora núcleo** (la página que se autodescribe como "India's first Algorithmic Pricing Calculator Engine"). Por tanto "valuation" es a la vez (a) la etiqueta de vertical de cardeep y (b) una ruta real y central del sitio de OBV — pero **no** un host/subdominio independiente.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre comercial | **Orange Book Value (OBV)** | sitio |
| Producto de | **Droom** ("OBV is a product of Droom") | droom.in/obv, homepage |
| Razón social | **Droom Technology Private Limited** (incorporada **9-sep-2014**) | Tracxn |
| Fundador del grupo (Droom) | **Sandeep Aggarwal** (también fundó ShopClues) | WebSearch (múltiples) |
| Lanzamiento de OBV | **Agosto 2016** | Inc42, Business Standard, The Hans India [VERIFICADO 2ª fuente] |
| HQ | **Gurugram (Gurgaon), Haryana, India** — Plot No. 336, Ground Floor, Udyog Vihar, Phase 4 | Tracxn |
| Patente | **US patent certified / "USA Patent"** (pricing engine) | homepage, methodology, prensa |
| Empleados (entidad OBV) | **~156** (may-2025; +24% YoY) | Tracxn |
| Revenue (entidad OBV, Tracxn) | **₹100–500 Cr** (a 31-mar-2025) | Tracxn |
| Revenue grupo Droom (FY24) | **₹85,4 Cr** operativo (−66% YoY desde ₹253,3 Cr FY23); EBITDA −44% | Entrackr, Inc42 [VERIFICADO 2ª fuente] |
| Estado IPO | **Retirado** (DRHP retirado oct-2022; refiling abortado 2024 por volatilidad/SEBI; foco en rentabilidad) | AIM Group, Inc42, IPO Central |

**Categoría:** proveedor de **pricing/valoración algorítmica de vehículos usados** ("algorithmic benchmark pricing engine") con **doble cara**: (a) herramienta de **consumidor** gratuita e instantánea (≈KBB) y (b) **OBV Enterprise** B2B (API/widget/dashboard) para BFSI, OEM y dealers. Se autoposiciona como **"India's first algorithmic pricing engine"** y "de facto industry standard" del usado en India.

**Posicionamiento declarado:** "independent, objective and unbiased" — precio por **cálculo científico/data science**, NO por markup de dealer ni estimación subjetiva, y explícitamente **NO basado solo en datos históricos de transacción** ("empirical evidence + proprietary methodologies" vs "past transactional data").

**Clientes objetivo (verticales):** consumidores · **auto dealers** · **banks & NBFCs** · **insurance companies** (cálculo de IDV) · **OEMs** · **ride/taxi aggregators** · **repo companies** · **rentals**. Verticales de producto con landing propia: **OBV for Insurance** y **OBV for Rentals** [VERIFICADO: nav homepage].

**Validación de terceros:** **Ford India** adoptó OBV como **calculadora oficial de precio para "Ford Assured"** (usado), vía **API integration + certificación de pricing** [VERIFICADO 2ª fuente: Deccan Chronicle / Asian Age, ago-2019]. Insurers lo usan para **Insured Declared Value (IDV)**.

**⚠ Riesgo de continuidad de negocio:** el grupo matriz **Droom** sufrió caída de ingresos del 66% en FY24, IPO retirado dos veces (2022, 2024), recortes de plantilla y reestructuración de gobierno/CFO. La salud de OBV depende de la del grupo. [VERIFICADO 2ª fuente: Entrackr/Inc42/AIM Group]

---

## 2. Cobertura

- **Países:** **38** [VERIFICADO: homepage + global pages]. Desglose reconstruido (corroborado por rutas `/global-XX`, `/sg/`, `/mt/en`):
  - **Europa (27 — UE completa):** Austria, Bélgica, Bulgaria, Croacia, Chipre, Chequia, Dinamarca, Estonia, Finlandia (`/global-fi`), Francia, Alemania, **Grecia** (`/global-gr`, la URL de entrada), Hungría, Irlanda, Italia, Letonia, Lituania, Luxemburgo, Malta (`/mt/en`), Países Bajos, Polonia, Portugal, **Rumanía** (`/global-ro`), Eslovaquia, Eslovenia, España, Suecia.
  - **Asia (4):** India (mercado primario), Singapur (`/sg/`), Tailandia, Malasia.
  - **Oriente Medio (6):** EAU, Arabia Saudí, Kuwait, Omán, Catar, Baréin.
  - **ANZ (1):** Australia.
- **Idiomas:** **7** · **Monedas:** **11** [VERIFICADO: homepage/global].
- **Tipos de vehículo (scope) — 14 categorías** [VERIFICADO: homepage; 12 enumeradas + three-wheeler vía prensa]: **Car · Bike/Motorcycle · Scooter · Plane · Bicycle · Taxi · Truck · Bus · Tractor · Electric Car · Electric Scooter · Electric Bike** (+ **Three-wheeler** confirmado en prensa; la 14ª no enumerada explícitamente). Cubre **nuevo y usado** (la calculadora tiene tab "New").
- **Profundidad de catálogo (India):** **24.000+ productos**, **100+ makes**, **~1.000 models**, **4.000+ variants**, **15–16 años** de historia de fabricación [VERIFICADO 2ª fuente: Deccan Chronicle/prensa de lanzamiento]. Print Edition: **35.000+ vehículos**.
- **Frescura:** valoración en **<10 segundos**, "real-time data science". Comparables/listings del informe premium usan ventana de **últimos 3 meses** (50 transacciones + 50 listings).

---

## 3. Productos + campos atómicos

### 3.1 Calculadora OBV (consumidor, gratuita) — núcleo (`/valuation`, `/used-cars`)
**Flujo de 4 pasos:** (1) Purpose → (2) Category → (3) parámetros del vehículo → (4) OBV Fair Market Price.

**5 formatos de precio (tabs de la calculadora)** [VERIFICADO: homepage tabs + lista de "free tools" del enterprise coinciden]:
1. **Used** — precio de mercado justo del usado.
2. **New** — precio/estimación de depreciación del nuevo.
3. **Exchange** — valor de intercambio (exchange value).
4. **Future Price** — predictor de precio de reventa futuro.
5. **Residual (Lease)** — valor residual para leasing.

**Inputs (campos que aporta el usuario):**
- **Purpose:** Buy / Sell — con sub-tipo de Sell: **To Individual / To Dealer**.
- **Category** (1 de 14).
- **Make** · **Model** · **Year** (año de fabricación) · **Trim/Variant**.
- **Fuel Type**.
- **Kilometers Driven** (lectura de odómetro).
- **Condition** (estado físico/mecánico).
- **City / Location** (precio geolocalizado).
- **Ownership Type** (Individual / Dealer) · **Number of Owners**.

**Outputs (resultado):**
- **Fair Market Price** actual (según condición).
- Precio en **3 grados visibles** en el informe consumidor: **Fair / Good / Excellent** (la metodología internamente cita **4**: **Excellent · Very Good · Good · Fair** — "Excellent/Very Good = coche sano; Good/Fair = partes con problemas/reparación"). [discrepancia 3 vs 4 marcada]
- Los 4 outputs adicionales de los otros tabs: New price, Exchange value, Future resale price, Residual/Lease value.
- **Trade-in vs retail** (valoración diferenciada Individual/Dealer).

### 3.2 OBV Valuation / Premium Report — certificado (₹199, PDF 10 páginas)
Entrega **instantánea por WhatsApp o email**. Contiene [VERIFICADO: droom.in/obv/valuation + /premium-reports]:
- **Current Market Valuation** del vehículo (en Fair / Good / Excellent).
- **"New Vehicle Price — Now and Then"**: precio on-road original (año de compra) **vs** precio on-road actual del modelo nuevo (cambio de precio a lo largo de los años de producción).
- **"Next 3-Year Depreciation"**: estimación de pérdida de valor futura.
- **"What Others Have Paid"**: precios de transacciones comparables (mismo make/model/year/trim).
- **Total Cost of Ownership (TCO) a 5 años**: desglosado en **fuel charges · insurance renewal · servicing · tire replacement · repairs**.
- **Recent Transactions** (50 ventas, últimos 3 meses): **average / highest / lowest selling price**, **average number of owners**, **average kilometers driven**.
- **Recent Listings** (50 listings activos, últimos 3 meses): mismas métricas (avg/high/low price, avg owners, avg km).
- **Compare Similar Vehicles**: comparación de features/performance de modelos similares.
- **Available model options / variants**.
- **Frequently purchased complementary items** (accesorios).
- **Lifespan of vehicle components**.
- **Expert Reviews** (pros/cons).
- **User Ratings and Reviews** (de usuarios de droom.in).

### 3.3 OBV Enterprise 2.0 (B2B — OEM / BFSI / Dealers)
Tracción declarada: **3 Lakh+ (300.000+) dealers**, **500mn+ queries**, **2 Lakh+ (200.000+) reports descargados** [VERIFICADO: /enterprise]. Módulos/funciones [VERIFICADO: blog "Droom Launched OBV Enterprise"]:
- **OBV Price Check:** 5 pricing formats + **Bulk Pricing** + **Pricing Comparison**, "independent/objective/unbiased".
- **Quick Check:** verificación de precio puntual (redirige al sitio OBV).
- **Bulk Upload:** subir lista de vehículos en **CSV/Excel**, valor OBV devuelto en **<10 s**, **customización de condición por vehículo**.
- **Bulk Report Download:** seleccionar varios vehículos y descargar reports (**basic / premium**) en lote.
- **API Integration Panel:** **generación de token** para mostrar precios OBV en la web del partner + **API Document (PDF) descargable**.
- **Widget JavaScript:** "generate a code and get a widget", disponible en **distintas dimensiones**.
- **Enterprise Dashboard / Panel** (login en homepage): **total queries (lifetime / last 15 days / last 30 days)**, **gráfico day-wise de queries (14 días)**, **reports downloaded (basic/premium)**, **subscription status**.
- **My Account:** datos de usuario y organización.
- **Consumer Intelligence:** market overview + **buy/sell preference analytics**.
- **Resultados de negocio prometidos:** Dealers "**sell 2x faster**", "**+40% conversion**"; OEMs "**+25% dealer conversion**" + market insights + pricing strategies.

### 3.4 OBV Global (internacional)
Misma calculadora y campos que la india, escalada a 38 países / 11 monedas / 7 idiomas; mismo set de inputs (purpose, category, make/model/year/trim, km, condition) y grados (Excellent/Very Good/Good/Fair). Verticales B2B: banks/NBFC, insurance, ride-hailing, repo, dealers.

### 3.5 OBV for Insurance / OBV for Rentals (verticales)
- **Insurance:** cálculo de **Insured Declared Value (IDV)** = valor de mercado actual del usado para fijar prima/suma asegurada.
- **Rentals:** valoración para flotas de alquiler (landing propia en nav).

### 3.6 OBV Print Edition (guía física)
Libro de precios que calcula el valor de **35.000+ vehículos usados** (incluye trucks, buses, tractors); publicado por **Droom Technology Pvt Ltd** en múltiples versiones (v3, v5…), vendido en retailers online (ZorbaBooks). [VERIFICADO 2ª fuente: ZorbaBooks]

### 3.7 Apps móviles
**OBV: Used Car & Bike Valuation** en **Google Play** (`in.droom.online_obv_app`) y **App Store** (id 1120532296). Mismo flujo de calculadora.

---

## 4. Metodología / Fuentes de datos

- **Núcleo:** "most advanced algorithmic and data science based pricing engine" sobre **Droom's proprietary data science methodologies**. Explícitamente **NO** se apoya solo en datos históricos de transacción ("empirical evidence" vs "past transactional data").
- **Curvas de depreciación:** "**thousands of depreciation curves**" mapeadas a vehículos individuales **según la duración de la propiedad** (ownership duration).
- **Factores del modelo:** make · model · year · trim · **kilometers driven** (patrón de desgaste) · **condition** (físico/mecánico) · **purpose** (buy/sell) · **party type** (private/dealer) · maintenance history · wear & tear · dents/damage · major repair records.
- **Grados de condición:** Excellent / Very Good / Good / Fair (4 internos; 3 en informe consumidor).
- **Real-time:** resultado en **<10 segundos**; AI/ML desarrollado en el **Droom AI Lab** (plataforma "Eco AI" del grupo integra pricing + inspection + fraud detection en tiempo real).
- **US patent** sobre el motor de pricing.
- **Limitación de transparencia:** la página de metodología **no publica** modelos ML, técnicas estadísticas ni arquitectura algorítmica concretas — es opaca por diseño ("proprietary").

---

## 5. Entrega (delivery)

| Canal | Detalle |
|---|---|
| Web (consumidor) | `orangebookvalue.com` + `/valuation` + `/used-cars`; calculadora gratuita instantánea |
| Apps móviles | iOS (App Store) + Android (Google Play) |
| **API REST** | Token-based (Enterprise panel genera token), **API Document PDF**; usada por Ford Assured y partners para mostrar precios OBV en su web |
| **Widget JavaScript** | Embebible, **múltiples dimensiones**, para webs de terceros |
| **PDF report** | Premium/Valuation Report (10 págs) por **WhatsApp / email**, ₹199 |
| **Bulk (CSV/Excel)** | Bulk Upload de vehículos + Bulk Report Download (basic/premium) en Enterprise |
| **Enterprise Panel/Dashboard** | Login web con analítica de queries, subscription, reports |
| **Print Edition** | Libro físico (35.000+ vehículos) |
| Integración OEM/marketplace | API integration (caso Ford Assured); ecosistema Droom (listings + transacciones reales alimentan comparables) |

---

## 6. Precio (lo descubrible)

| Producto | Precio |
|---|---|
| Calculadora OBV (consumidor, 5 formatos) | **Gratis** |
| OBV Premium / Valuation Report (PDF 10 págs) | **₹199** (≈ €2,2 / US$2,4) |
| OBV Enterprise (API/widget/bulk/dashboard) | **Contact sales / Book a demo** — sin tarifas públicas (página Plans & Pricing existe pero no expone importes) |
| OBV Print Edition | Precio de libro (varía por edición/retailer) |

Modelo: **freemium de consumidor** (atrae volumen y datos) + **microtransacción** del report (₹199) + **enterprise negociado** (API/datos/widget para BFSI/OEM/dealers). El gancho es el **precio instantáneo gratis**; la monetización seria es B2B.

---

## 7. Placement (dónde colocan CADA dato — patrón a copiar por cardeep)

**A. Calculadora / ficha de resultado (pantalla canónica del consumidor):**
1. **Selector superior de 5 tabs** = los 5 formatos de precio (**Used · New · Exchange · Future Price · Residual/Lease**). El usuario elige el "tipo de pregunta de precio" antes que nada — patrón clave: **un mismo vehículo, cinco lentes de valor, conmutables en una barra de tabs**.
2. **Toggle Buy / Sell** (y Sell → To Individual / To Dealer): el mismo dato de precio se reencuadra según la parte.
3. **Cascada de inputs** (Make → Model → Year → Trim → Fuel → Km → Condition → City): drill-down dependiente.
4. **Resultado:** **Fair Market Price** como cifra-titular grande + **desglose por condición (Fair / Good / Excellent)** como precios paralelos → el usuario ve de inmediato el rango por estado.

**B. Informe premium (PDF 10 páginas) — orden editorial de secciones:**
1. Cabecera: vehículo + **Current Market Valuation** (en 3 grados).
2. **"New Vehicle Price — Now and Then"** (precio nuevo entonces vs ahora) → contexto de depreciación.
3. **"Next 3-Year Depreciation"** → proyección forward.
4. **"What Others Have Paid"** → prueba social / comparables de transacción.
5. **Total Cost of Ownership 5 años** (fuel/insurance/servicing/tires/repairs) → bloque de coste.
6. **Recent Transactions (50)** + **Recent Listings (50)**: tablas con avg/high/low price, avg owners, avg km → evidencia de mercado.
7. **Compare Similar Vehicles** + **model options** + **complementary items**.
8. **Lifespan of components**.
9. **Expert Reviews (pros/cons)** + **User Ratings & Reviews** → cierre cualitativo.
→ Patrón: **precio primero, depreciación y comparables después, coste de propiedad en medio, opinión experta/usuario al final**.

**C. Dashboard Enterprise (panel B2B):** KPIs de **uso** arriba (total queries lifetime / 15d / 30d), **gráfico de barras day-wise (14 días)**, **reports downloaded (basic/premium)** y **subscription status**; secciones de acción **Quick Check · Bulk Upload · Bulk Report Download · API Integration (token + doc) · My Account**. → El dato de mercado (precio) se consume vía Price Check / Bulk; el panel en sí es de **telemetría de consumo + gestión de integración**, no de ficha de coche.

**D. Overlay en contexto externo (Widget JS / API):** el precio OBV se **inyecta en la web del partner** (p. ej. listing de Ford Assured) — el dato aparece **donde el usuario ya navega**, no en una pantalla aparte. Mismo principio que el Asset Verification Tool de Black Book, pero vía widget/API en lugar de extensión.

**E. Vertical Insurance:** el dato relevante reencuadrado como **IDV** (valor de mercado → suma asegurada), no como "precio de venta".

---

## 8. Diferencial (lo que ofrece y otros no)

- **Herramienta de consumidor gratuita e instantánea** (<10 s) — a diferencia de los incumbentes B2B europeos (Autovista, cap hpi, DAT, Eurotax) y de Black Book (que **no** tiene herramienta de consumidor directa). OBV juega el rol de **KBB indio** + capa enterprise.
- **5 formatos de precio en un solo widget** (Used / New / Exchange / **Future resale price predictor** / **Residual-Lease**): pocas herramientas de consumidor exponen *future price* y *residual* en la misma UI.
- **Scope de vehículos extremadamente amplio** (14 categorías: incluye **planes, bicycles, tractors, three-wheelers, taxis, buses** y **EVs** — car/scooter/bike eléctricos).
- **Cobertura multi-país / multi-moneda / multi-idioma** (38 / 11 / 7) bajo **un mismo motor algorítmico**.
- **US patent** + narrativa "algorithmic, not transaction-history-only" como diferenciador de marca.
- **De facto standard en India** + **calculadora oficial de Ford Assured** (validación OEM) + uso por insurers para **IDV**.
- **Microtransacción de report (₹199)** + **Print Edition física** — monetización de consumidor poco común.
- **Ecosistema Droom**: el marketplace alimenta **transacciones y listings reales** (50+50 de los últimos 3 meses) como comparables dentro del report.
- **Onboarding enterprise low-friction**: token + widget + bulk CSV en self-service, sin proyecto de integración pesado.

---

## 9. Gaps (lo que NO ofrece / límites observados)

- **Sin VIN/chasis-decoding ni valoración VIN-específica:** OBV trabaja por **selección make/model/year/trim**, no por descodificación de VIN. No hay "one-to-many VIN→trim resolution" tipo Black Book EVM. → cardeep, si indexa por VIN/matrícula, cubre un eje que OBV no.
- **Condición autodeclarada por el usuario** (Fair/Good/Excellent a ojo): no hay inspección verificada ni grading objetivo en la calculadora gratuita → **riesgo de exactitud** (criticado en Quora "how reliable is OBV"). Black Book/J.D. Power anclan en subasta wholesale real.
- **Sin historial de siniestros / fraude de odómetro / título-robo propio:** no hay vehicle history report integrado (vs AutoCheck/Experian en Black Book, o CarFax). El grupo dice estar integrando "fraud detection" (Eco AI) pero no es un dataset expuesto en OBV.
- **Sin datos de subasta wholesale estructurados** (India carece de la infraestructura de subastas físicas/online de EE. UU.); el "wholesale/trade" se infiere algorítmicamente, no se mide.
- **Profundidad fuera de India dudosa:** los 24k productos / 100+ makes / 4k variants son cifras de **India**. La "cobertura global" de 38 países probablemente es **extrapolación algorítmica** más que datos locales profundos de transacción → previsible **gap de precisión vs incumbentes locales europeos** (Autovista, cap hpi, DAT, Eurotax, Ganvam, L'Argus).
- **Sin suite B2B de residuales/forecasting profunda:** tiene tab consumidor "Residual (Lease)" y "Next 3-Year Depreciation", pero **no** escenarios CCAR/DFAST, sensitivity "war game", ni residuales 1-120 meses como Black Book/J.D. Power.
- **Sin base de specs/equipamiento profunda** (add/deducts por opción, configurador OEM, packages) tipo Eurotax/DAT/Schwacke — limitado a make/model/year/trim.
- **Metodología opaca:** sin publicación de modelo, técnicas ni validación estadística.
- **Pricing enterprise opaco:** solo "contact sales".
- **Discrepancias de cifras** entre páginas: queries **800M+** (homepage) vs **500M+** (enterprise); revenue entidad OBV **₹100-500 Cr** (Tracxn) vs grupo Droom **₹85,4 Cr** FY24 (Entrackr) — el sitio/marketing y las finanzas auditadas no cuadran.
- **⚠ Riesgo de viabilidad del proveedor:** Droom con revenue −66% FY24, IPO retirado 2×, recortes — continuidad/soporte del producto en duda.
- **Grados de condición inconsistentes** (3 visibles vs 4 internos) — falta de pulido en la propia UX de datos.

---

## 10. Fuentes (URLs)

**Sitio OBV / Droom (WebFetch directo, 2026-06-30):**
- https://orangebookvalue.com/ (homepage: 5 tabs/formatos, 14 categorías, stats, nav productos)
- https://orangebookvalue.com/valuation (calculadora núcleo; HTTP 200 verificado)
- https://orangebookvalue.com/used-cars (flujo + inputs/outputs)
- https://orangebookvalue.com/methodology (factores del modelo, curvas, grados)
- https://orangebookvalue.com/enterprise (OBV Enterprise: price check, bulk, API, widget, métricas)
- https://orangebookvalue.com/global/blog/droom-launched-obv-enterprise (Enterprise 2.0: dashboard, token, bulk upload CSV, API doc)
- https://orangebookvalue.com/premium-reports + https://droom.in/obv/valuation (report premium ₹199, 10 págs, secciones/campos)
- https://droom.in/obv (overview producto, casos de uso, tipos de vehículo)
- https://orangebookvalue.com/global-ro , /global-gr (entrada), /global-fi , /sg/ , /mt/en (OBV Global por país)
- https://cloud.droom.in/obv (DCS — tool B2B banks/NBFC/OEM; familias ACS/AES/AVS)

**Verificación cruzada (2ª fuente):**
- https://inc42.com/flash-feed/droom-launches-obv/ (lanzamiento ago-2016, algorithmic engine)
- https://www.business-standard.com/article/news-ani/droom-launches-orange-book-value-... (lanzamiento, scope)
- https://www.deccanchronicle.com/.../obv-official-price-calculator-for-ford-assured.html + espejo asianage.com (Ford Assured: API integration + certificación; 24k productos / 9-14 categorías / 100+ makes / 1000 models / 4000 variants / 15-16 años)
- https://tracxn.com/d/companies/orangebookvalue/... (HQ Gurugram, Droom Technology Pvt Ltd inc. 2014, 156 empleados, revenue ₹100-500 Cr, competidores)
- https://entrackr.com/.../drooms-revenue-plummets-66-to-rs-85-cr-in-fy24-8699166 (finanzas grupo FY24)
- https://inc42.com/buzz/ipo-bound-drooms-fy24-loss-declines-35-... + https://aimgroup.com/2022/10/18/droom-abandons-ipo-plans/ (IPO retirado, reestructuración)
- https://www.zorbabooks.com/store/.../obv-orange-book-value/ (Print Edition, 35.000+ vehículos, v3/v5)
- https://play.google.com/store/apps/details?id=in.droom.online_obv_app + https://apps.apple.com/us/app/orange-book-value/id1120532296 (apps móviles)
- https://www.quora.com/How-reliable-is-Orange-Book-Value-... (señal de fiabilidad/condición autodeclarada)

**Verificación técnica propia:** `curl`/`nslookup` 2026-06-30 → `valuation.orangebookvalue.com` = HTTP 000 / NXDOMAIN (no es host real); `orangebookvalue.com/valuation` = HTTP 200.

**Limitaciones de método:** WebFetch resume con modelo pequeño (posible pérdida de campos finos); la documentación de API (PDF tras login enterprise) **no es pública** → los campos exactos de respuesta de la API no se pudieron auditar 1:1 (se infieren de los outputs de la calculadora). La 14ª categoría de vehículo no está enumerada explícitamente. Cifras de marketing (queries/users) divergen entre páginas — marcado en §9.
