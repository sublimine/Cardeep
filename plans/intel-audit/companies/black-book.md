# Black Book — Auditoría Atómica de Inteligencia Competitiva

> **Slug:** `black-book` · **Web:** https://www.blackbook.com/ · **Vertical cardeep:** valuation
> **Auditado:** 2026-06-30 · **Método:** lectura directa de páginas de producto/API/press releases del sitio vivo (vía `curl`, porque WebFetch bloquea el dominio) + verificación cruzada con Wikipedia, directorios corporativos (D&B, NTEA) y prensa del sector.
> **Nota de subdominio:** `valuation.blackbook.com` (y `values/valuengine/api/developer/portal/app`) **NO resuelven en DNS** [VERIFICADO: HTTP 000]. La ruta `www.blackbook.com/valuation/` existe pero devuelve **403** (gated). "valuation" es la etiqueta de vertical de cardeep, no un host real de Black Book. El portal de desarrolladores y "Black Book Digital" son áreas con login dentro del dominio principal.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre comercial | Black Book® | sitio |
| Razón social / editor | National Auto Research (publica los datos a diario) | About / press releases |
| Propietario / grupo | **Hearst** — marca registrada de **Hearst Business Media Corporation**; dentro de la división **Hearst Transportation** | footer "© 2026 Hearst Business Media Corporation"; hearst360 |
| Empresas hermanas | **Canadian Black Book** (Toronto) y **MOTOR Information Systems** | About; OEM page; hearst360 |
| HQ | **1745 N Brown Rd #130, Lawrenceville, GA 30043, EE. UU.** | D&B, NTEA, Yahoo Local [VERIFICADO 2ª fuente] |
| Otras oficinas | Georgia (HQ) + Toronto (Canadian Black Book). PR de 2017 citaba también Florida y Maryland (probablemente histórico) | press releases |
| Fundación | **1955** ("books sold out of a car") | About; Wikipedia |
| Antigüedad declarada | "más de 75 años" como fuente de valoraciones | autoremarketing/hearst360 |
| Cabeza de grupo (Hearst Transportation) | Tom Cross (Group Head of Transportation) | F&I Magazine, Auto Remarketing |

**Línea temporal (hitos de producto):** 1955 fundación · 1962 partnership con William Ward Publishing (origen de Canadian Black Book) · 1980 compra por Hearst (vía United Technical Publication) · 1996 Black Book Express (CD) · 2001 Web Services · 2004 app Palm Pilot · 2010 apps iPhone/Android · 2013 Web API · 2014 Black Book Digital · 2018 Black Book Cherry + History Adjusted Valuations + Retail Listings · 2019 Enhanced Vehicle Matching · 2021 History Adjusted Residual Values · 2023 Retail Listings Visualization · 2024 (nov) Brand Value Index. [VERIFICADO: página About]

**Equipo directivo:** Jared Kalfus (President) · Kyle Luck (SVP Product & Technology) · Laura Wehunt (VP Data & Analytics) · Jim Jabaay (VP Data Licensing) · Kim Breidenbach (VP Marketing/Comms/CS) · Alex Yurchenko (SVP & Chief Data Science Officer) · Eric Lyman (VP Product – Auto Finance).

**Categoría:** proveedor B2B de **pricing de vehículos + analítica/inteligencia de mercado** (valoración, residuales, datos de listados retail, índices). NO es herramienta de consumidor (a diferencia de KBB): "Black Book doesn't offer a direct consumer pricing tool" — alimenta sitios de terceros (p. ej. Car and Driver). [VERIFICADO: /what-is-my-car-worth/]

**Clientes objetivo (7 verticales):** Auto Finance / Lenders · Dealers · Insurance · Marketing · OEMs · Remarketing · Rental, Fleet & Rideshare. Tracción declarada: **"usado por el 90% de los top lenders del país"**, **30.000+ dealers**, **22+ marcas de automoción (OEM)**. [VERIFICADO: /autofinance/, /what-is-my-car-worth/, /oem/]

---

## 2. Cobertura

- **Países:** **EE. UU.** (Black Book) y **Canadá** (Canadian Black Book, Toronto). Scope geográfico interno de EE. UU. con **ajuste regional/estatal** del valor.
- **Tipos de vehículo (scope):** coches, SUV y light-duty trucks; medium & heavy duty trucks (Class 4-8) y commercial trailers; motos y powersports (ATV, dirt bikes, scooters, PWC, jet boats, snowmobiles); RV (travel trailers, park models, motor homes, truck campers, camping trailers); collectible/exotic (CPI, desde 1946); **EV** (con datos de batería vía Recurrent).
- **Nuevo y usado:** ambos. Valores de coche nuevo (retail/invoice/MSRP/residual) y usado (wholesale/retail/trade/private party/residual).
- **Profundidad histórica por clase:** usado desde MY 1981; CPI desde 1946; trucks ~26 años hacia atrás; powersports desde 1980-1981; RV desde 1997; new car specs desde MY 2002.
- **Frescura:** valores de coche usado **actualizados a diario** ("daily vehicle value updates"); las guías Price Point por clase se actualizan **mensualmente**. UVI actualizado mensual.

---

## 3. Productos + campos atómicos

### 3.1 Vehicle Values (núcleo — coches/SUV/light-duty)
Tipos de valor: **Wholesale, Retail, Trade-In, Private Party, Finance Advance™ (loan), Residual, End of Term, History Adjusted Value.**
Condiciones (wholesale usado): **Extra Clean (XCL), Clean, Average, Rough** [VERIFICADO 2ª fuente: Pocketsense/withclutch]. (Wholesale Average es el benchmark central.)
Ajustes aplicados al valor base: **mileage, optional equipment (add/deducts), region/state.**
Otros campos: standard equipment, vehicle colors, specification PDF, VIN decoding.
Disponibilidad de valor por clase (página vehicle-values):
- Cars/SUV/light trucks: histórico+actual de wholesale/retail/trade-in/private party; residual (wholesale); History Adjusted.
- Medium & Heavy Duty: histórico+actual wholesale/retail.
- Powersports: histórico+actual trade-in/wholesale/retail.
- Collectible (CPI): histórico+actual retail.
- RV: histórico+actual wholesale/retail.

### 3.2 History Adjusted Valuations (HAV) — "primero del mercado"
Valoración VIN-específica que integra el **Vehicle History Report de AutoCheck® (Experian)**. Modelo entrenado sobre "millones de transacciones". Eventos del VHR que ajustan el valor: **número de propietarios, accidentes, despliegue de airbag, uso del vehículo (flota/rental/personal), flood/hail/fire, otros eventos del VHR.** Muestra el impacto de cada ajuste sobre el precio total. Extiende a residuales (History Adjusted Residual Values, 2021 — VIN-specific a nivel residual, "industry first").

### 3.3 Enhanced Vehicle Matching (EVM)
Resuelve el problema "~30% de los VIN no decodifican a un único trim". IA + big data, **millones de registros/día** de múltiples fuentes, **incluye build data de OEM**. Mapea VIN de 17 dígitos a un único trim y aplica **add/deducts automáticamente**. Sustrato de Cherry, AVT y APIs.

### 3.4 Black Book Cherry (app insignia, móvil + desktop) — $772.98/año
Funciones/secciones: **VIN Scanner** · **Values** (con HAV, impacto de cada evento) · **History Adjusted Valuations** · **Retail Market Insights** (vehículos comparables cercanos: average days to turn, days supply in market, average price, average mileage) · **Inventory Discovery** (recomienda inventario pre-subasta vía EVM; ver run lists; filtros: auction, price range, mileage, condition report grade, make, model) · **Cherry List** (guardar/like, notas, compartir). Integración **Credit Acceptance**: cálculo de Front-end Profit estimado (programas Portfolio y Purchase, según perfil CAPS) y **Vehicle Policy Report** de compliance ($0.49/report).

### 3.5 Price Point (guías por clase, desktop/móvil)
Lookup por **VIN / vehicle description / drill down**. Variantes y campos:
- **Used Car – Price Point** ($717.98/año): 32.000+ valores usados, MY 1981-actual, update mensual. Wholesale, Retail, Trade-In, Finance Advance, Residual, History Adjusted; ajustes mileage/options/region.
- **New Car & Light Truck** ($582.11/año): config OEM + specs desde MY 2002; last retail & invoice; standard/optional equipment configurator; residual del MY actual; packages; interior/exterior colors; major changes vs año previo.
- **Medium & Heavy Duty Truck & Commercial Trailer** ($362.98/año): Class 4-8, ~26 años; wholesale & retail; Finance Advance/loan; 11 tipos de trailer; ajuste por optional equipment y mileage; **GVW, GCW, cilindros, horsepower, transmisión**; histórico.
- **Motorcycle & Powersports** ($362.98/año): desde ~1980; **Auction Wholesale, Average Retail, Clean Trade, Fair Trade**, MSRP, Finance Advance; engine displacement, nº cilindros; histórico.
- **Recreational Vehicles** ($362.98/año): MY 1997-actual; **Clean/Average Wholesale, Retail, Finance Advance, MSRP**; tipos (travel trailers, park models, motor homes, truck campers, camping trailers); histórico.
- **Cars of Particular Interest (CPI)** ($362.98/año): collectible+exotic desde 1946; **3 valores por vehículo: Excellent, Good, Fair (retail)**; domestic+import+light trucks; histórico.

### 3.6 ValuEngine (plataforma de valoración de colateral, desktop) — precio a medida
Valoración de portfolio en tiempo real, self-service. Valora **históricos, actuales y residuales proyectados** de cualquier colateral **a nivel de trim**. Determina cómo cambian los **LTV** del portfolio en el tiempo. Mejora loss forecasting, identifica **delinquencies** para collections, risk analysis. **Batch processing de millones de VIN en un solo job**; auto-run cuando detecta nuevos ficheros; refrescos de portfolio; ingiere Excel/.csv/texto delimitado. Incorpora HAV VIN-specific a nivel residual.

### 3.7 Pulse (visualización de mercado retail, desktop) — request access
Crea **segmentos** desde portfolio propio o desde vista holística del mercado retail; filtros por atributos de **vehículo, dealer o geografía**. KPIs: **Daily Vehicle Volume, Average Listing Mileage, Days on Market.** Casos: localizar vehículos en venta/vendidos dentro y fuera de red, non-grounded vehicles, oportunidades CPO, mercados ideales por modelo/trim, brand performance. (La ruta `/rlv/` sirve el mismo contenido que Pulse.)

### 3.8 Visual Analytics (plataforma Tableau, desktop)
Workbooks interactivos con datos históricos/actuales/proyectados. Features: Market Trends, Segment & Model Analysis, **Loss Forecasting**, Emerging Opportunities, **Depreciation Trends**, **Vehicle Segment Model Explorer**, Portfolio Insights. Aloja el **Brand Value Index (BVI)**.

### 3.9 Brand Value Index (BVI) — métrica de marca (lanzado nov-2024)
Mide **brand equity, market position, perception** → score de marca ponderado por ventas. Metodología: identifica contenido/configuración/precio nuevo típico por segmento y compara el **wholesale average-condition price de vehículos de 1-5 años** de cada modelo contra el precio medio del segmento. Quarterly BVI Report (mainstream + premium).

### 3.10 Used Vehicle Retention Index (UVI) — índice de mercado
Calculado con el **Wholesale Average de vehículos de 2-6 años como % del MSRP original típicamente equipado**. Ponderado por volumen de matriculaciones; ajustado por **age, mileage, condition, inflation (MSRP)**. Agregado de cientos de subastas físicas y online en todo EE. UU.; sin sesgo de marca/subasta/región. Publicación mensual descargable.

### 3.11 Residual / Forecasting (suite)
- **Residual values:** proyección **1-120 meses** sobre los **10 model years** más recientes (expandido en 2022 desde 1-72 meses / 7 MY) [VERIFICADO: PR 21-oct-2022]. A nivel segment/model/trim.
- **Scenario-Based Residuals:** proyecta wholesale residuals bajo escenarios económicos **baseline, adverse, severe/stressed** + escenarios custom; soporta **CCAR/DFAST** stress testing; segment/model/trim.
- **Residual Sensitivity Analysis:** entorno "War Game" para ajustar **MSRP, incentives, rental penetration** y ver impacto combinado en residuales.
- **Residual Studies:** recomendaciones de analistas sobre contenting óptimo, estrategias lease/fleet, competitive analysis, go-to-market de modelos nuevos/rediseñados, cuándo comprar/vender, maximizar remarketing.

### 3.12 Asset Verification Tool (AVT) — extensión de navegador (+ API)
En el momento de origination, protege a lenders contra misrepresentation. Botón que **verifica trim level + opciones instaladas** (vía EVM) desde la listing en vivo del dealer; entrega **fully-adjusted Wholesale Value**, los **add/deducts** de EVM y la **History Adjustment** del AutoCheck VHR. Disponible como API para integrar en automated approval / Loan Origination Systems.

### 3.13 Web APIs (Developer Portal) — formato JSON/XML
Portal con "What If" calls, test de parámetros, gestión de auth, tracking de uso en tiempo real, conmutación JSON/XML, logs de query, code samples. Endpoints y campos:
- **Used Car API:** Wholesale, Trade-In, Retail, Private Party, Residual, End of Term, Finance Advance, Specification PDF, Vehicle Colors, Standard equipment, VIN Decoding.
- **New Car API:** Vehicle description, Manufacturer marketing message, MSRP/invoice/destination, **Equipped Retail Price** (MSRP+destination+popular options/packages), Residual, End of Term, Major changes vs MY previo, **Build & Price option logic (requires/includes/excludes)**.
- **Retail Market Insights API:** year/make/model/series/body style; nº de price changes con **price & mileage history**; **days on market**; **days to turn**; **market days' supply**; min/max price y mileage; mean & median price y mileage; **VDP URL & Image URL**; Listing Price; **CPO/Leather/Navigation flags**; Mileage; exterior/interior colors; optional & standard features; seller name & notes; paginación. Escala: **45.000+ dealerships, 14M listings** (página API) / 40.000+ dealerships, 7M listings, 3M unique VIN (página solutions — cifra anterior).
- **Custom Trade Value API:** un único valor Black Book ajustado por respuestas a un cuestionario de condición configurable; analytics endpoint para medir "breakage".
- **Medium & Heavy Duty Truck & Trailer API:** year/make/model, vehicle style, manufacturer name & model number, Black Book mileage category, class code & name, wholesale, retail, Finance Advance, MSRP + features incluidas, **GVW & GCW**, nº cilindros & displacement, base horsepower, transmission.
- **Recreational Vehicle API:** year/make/model, style & class, wholesale, retail, **external length**, Finance Advance.
- **Powersports API:** year/make/model, wholesale average, retail average, trade-in, Finance Advance, MSRP, nº cilindros, engine displacement.
- **CPI API:** retail en Fair/Good/Excellent; year/make/model.

### 3.14 EV-specific (partnership Recurrent, 2022)
Integra datos VIN-específicos de Black Book con el **Range Score** de Recurrent (salud de batería): compara el **rango esperado actual vs. cuando era nuevo** (distinto del EPA-rated), modelado sobre **100 millones de millas EV registradas**; ajusta valor por batería. Recurrent Reports: garantías de batería, rango en distintas condiciones, **proyección de rango a 3 años**. Modelos iniciales: Chevy Bolt/Volt, Nissan LEAF, Tesla 3/S/X/Y. Ampliado después ("Black Book enhances EV values with Recurrent battery insights").

### 3.15 Insurance (capacidades)
Underwriting, Policy Pricing, Gap Insurance, **Diminished value**, **Catastrophic modeling**, **Symboling**, VIN decoding, **Claims Payout**, total loss valuation.

---

## 4. Metodología / Fuentes de datos

- **Datos de subasta wholesale:** capturados en **cientos de subastas físicas y online** por todo EE. UU. (asistencia presencial + online), comparados contra precios anunciados por dealers; proceso editorial + modelado estadístico.
- **Equipo híbrido:** data scientists + analistas de automoción ("subject matter experts"), apoyados en machine learning. Proceso editorial sobre los residuales.
- **Build data de OEM** incorporado en EVM.
- **Listados retail** (Retail Listings) mapeados a descripciones Black Book con precisión a nivel trim (millones de listados, decenas de miles de dealers).
- **Vehicle History** de **AutoCheck® (Experian)** para HAV.
- **Batería EV** vía **Recurrent** (Range Score; 100M millas).
- **Volumen de matriculaciones** como ponderación del UVI.
- **Frecuencia:** valores usados a diario; guías por clase mensual.
- **Thought leadership:** **Vehicle Depreciation Report anual conjunto con Fitch Ratings** (edición 2025: depreciation trends, EV dynamics, auto-loan/ABS performance, proyección -15% depreciación 2025, UVI).

---

## 5. Entrega (delivery)

| Canal | Detalle |
|---|---|
| App móvil + desktop | Black Book Cherry (iOS/Android/desktop); Price Point guías por clase |
| Plataforma web self-service | ValuEngine (portfolio), Visual Analytics (Tableau), Pulse |
| **Web API (DaaS)** | JSON/XML vía Developer Portal; 8 endpoints (Used/New/Truck/RV/Powersports/CPI/Retail Market Insights/Custom Trade) + Asset Verification API |
| Extensión de navegador | Asset Verification Tool |
| Batch / file feed | ValuEngine: Excel/.csv/texto delimitado, jobs programados, millones de VIN |
| Data licensing (DaaS) | Licenciamiento de datasets a integradores/partners |
| Integraciones embebidas | 100+ partners (DMS, LOS, marketplaces, appraisal tools): Origence, defi SOLUTIONS, DriveCentric/DRIVE, Autodata, Fox Factory, DriveBid, Carwiser, etc. |
| Reports / newsletters | UVI mensual; Residual Value Insights (trimestral); Market Insights (semanal); Depreciation Report (anual, c/ Fitch); BVI Report (trimestral) |

---

## 6. Precio (lo descubrible)

Suscripciones self-service publicadas (USD/año), resto a medida (contact sales):

| Producto | Precio |
|---|---|
| Black Book Cherry | **$772.98/año** |
| Used Car – Price Point | **$717.98/año** |
| New Car & Light Truck – Price Point | **$582.11/año** |
| Medium & Heavy Duty Truck & Trailer | **$362.98/año** (iPhone/Android/Desktop) |
| Motorcycle & Powersports | **$362.98/año** |
| Recreational Vehicles | **$362.98/año** |
| Cars of Particular Interest (CPI) | **$362.98/año** |
| Credit Acceptance Vehicle Policy Report (add-on Cherry) | **$0.49/report** |
| ValuEngine, Visual Analytics, Pulse, APIs, Data Licensing, Scenario Residuals | **Custom / contact sales** (800.554.1026) |

Descuentos multi-subscriber por teléfono. Modelo: suscripción anual (productos self-service) + licenciamiento/enterprise negociado (datos, API, portfolio).

---

## 7. Placement (dónde colocan CADA dato — patrón a copiar por cardeep)

**A. Ficha de vehículo / pantalla de decisión (Black Book Cherry):** el patrón canónico.
1. **Entrada por VIN Scanner** (point-and-scan) → identifica el vehículo y resuelve trim vía EVM.
2. **Bloque Values:** tabla de Wholesale / Retail / Trade-In / Finance Advance / Residual.
3. **Bloque History Adjusted Valuations:** muestra el valor ajustado y, evento a evento (owners, accidents, airbag, usage, flood/hail/fire), **cuánto suma/resta cada uno al precio total** — desglose de ajustes inline bajo el valor.
4. **Panel Retail Market Insights:** comparables cercanos con average days to turn, days supply, average price, average mileage ("…and more").
5. **Inventory Discovery:** lista de inventario de subasta recomendado + run lists con **filtros** (auction, price, mileage, condition grade, make, model).
6. **Cherry List:** colección guardada con notas (workspace del usuario).

**B. Guía de consulta (Price Point):** lookup por VIN/descripción/drill-down → tabla de valores **por condición** + sección de **ajustes** (mileage / options / region) que recalculan el valor base. Specs (GVW/HP/displacement/transmission) en ficha de truck/powersports.

**C. Panel/overview de portfolio (ValuEngine):** vista tabular por VIN del portfolio: histórico + actual + **residual proyectado (1-120m)** y **LTV en el tiempo**; columnas de delinquency/loss forecasting; pantalla de jobs/scheduling para batch.

**D. Dashboards de mercado (Visual Analytics — Tableau / Pulse):**
- Visual Analytics: workbooks de segment/model analysis, depreciation trends, loss forecasting, Vehicle Segment Model Explorer, BVI.
- Pulse: **segment builder + filtros vehículo/dealer/geo** con KPIs (Daily Vehicle Volume, Avg Listing Mileage, Days on Market) sobre mapa/segmento.

**E. Overlay en contexto externo (Asset Verification Tool):** extensión que **inyecta un panel sobre la listing del dealer / LOS**: trim verificado, opciones, add/deducts, fully-adjusted wholesale value y history adjustment — el dato aparece donde el usuario ya trabaja, no en una pantalla aparte.

**F. Módulo de compliance/riesgo (Scenario-Based Residuals):** columnas comparativas de residual baseline vs adverse vs severe a nivel segment/model/trim.

**G. Herramienta interactiva de simulación (Residual Sensitivity "War Game"):** sliders de MSRP/incentives/rental penetration → recálculo de residual.

**H. Índices y reports (UVI / BVI / Depreciation Report):** una sola cifra-titular (índice) + descarga PDF; el dato de mercado vive como publicación, no como ficha.

**I. API (Developer Portal):** cada dato es un campo de respuesta JSON/XML por endpoint; consola "What If" para probar inputs y ver el output formateado.

---

## 8. Diferencial (lo que ofrece y otros no)

- **History Adjusted Valuations / Residuals VIN-específicos** integrando AutoCheck — Black Book reclama ser **el primero** en valoración y residual ajustados por historial a nivel VIN.
- **Enhanced Vehicle Matching** con build data de OEM + millones de registros/día: resuelve el "one-to-many VIN→trim" y aplica add/deducts automáticamente.
- **Residuales hasta 120 meses sobre 10 model years** + **scenario-based (CCAR/DFAST)** + **sensitivity "War Game"**: profundidad de forecasting orientada a lenders/ABS poco común.
- **Foco wholesale/profesional**: el UVI se basa en **Wholesale Average** real de subasta (vs índices retail), benchmark de la industria de remarketing.
- **Brand Value Index (BVI)**: métrica propietaria de fuerza de marca / pricing power por nameplate (novedad 2024).
- **Valoración EV con datos de batería (Recurrent Range Score, 100M millas)**: ajuste de valor por salud real de batería, no solo edad/km.
- **AVT como extensión de navegador**: verificación de colateral in-situ en la listing, integrable en LOS.
- **Ecosistema de integración muy amplio** (100+ partners DMS/LOS/marketplaces) + DaaS.
- **Cobertura multi-clase** bajo una marca: light, MHD truck/trailer, powersports, RV, collectible/exotic.
- **Pulse**: inteligencia de listados retail (volumen diario, days-on-market) sin desarrollo interno del cliente.
- **Respaldo Hearst + Fitch Ratings** (credibilidad de datos / report conjunto de depreciación).

---

## 9. Gaps (lo que NO ofrece / límites observados)

- **Sin herramienta de consumidor directa** (declarado explícitamente): cardeep, si apunta a consumidor final, no compite ahí; Black Book delega en terceros (Car and Driver, etc.).
- **Geografía limitada a EE. UU. + Canadá** — sin cobertura Europa/España (oportunidad para cardeep en su mercado).
- **Private Party value** solo en light-duty; ausente en truck/RV/powersports/CPI.
- **Residual** centrado en wholesale para usado light-duty; no se publican residuales para MHD truck/RV/powersports.
- **EV**: cobertura de batería limitada a un set inicial de modelos (Bolt/Volt/LEAF/Tesla) — no universal.
- **Pricing opaco** para los productos enterprise (ValuEngine, API, Visual Analytics, Pulse, data licensing): solo "contact sales".
- **Discrepancias de cifras** entre páginas (Retail Listings 45k/14M vs 40k/7M/3M; powersports "1980" vs "1981") — el sitio no está perfectamente sincronizado.
- **No expone públicamente** datos atómicos como histórico de siniestros propio (depende de AutoCheck/Experian), título salvage propio, ni odómetro/telemetría directa; el historial es de terceros.
- **Sin API de consumidor / sin scraping de inventario propio publicado** más allá de Retail Listings agregado.
- **VIN-level histórico de propietarios/uso** llega vía VHR de terceros, no como dataset propio descargable.

---

## 10. Fuentes (URLs)

**Sitio Black Book (lectura directa vía curl):**
- https://www.blackbook.com/about-black-book/ (identidad, timeline, equipo, HQ)
- https://www.blackbook.com/automotive-solutions/ (catálogo de productos/verticales)
- https://www.blackbook.com/vehicle-values/ (tipos de valor por clase)
- https://www.blackbook.com/api/ (campos atómicos por endpoint)
- https://www.blackbook.com/used-car-price-point/ · /new-car-values/ · /medium-heavy-duty-truck-values/ · /motorcycle-and-powersports-values/ · /recreational-vehicle-values/ · /cars-of-particular-interest/ (campos + precios por clase)
- https://www.blackbook.com/history-adjusted-valuations/ · /vin-decoding/ (HAV + EVM)
- https://www.blackbook.com/black-book-cherry/ (app insignia, secciones/placement)
- https://www.blackbook.com/valuengine/ (portfolio/colateral)
- https://www.blackbook.com/visual-analytics/ (Tableau + BVI) · https://www.blackbook.com/pulse/ (KPIs retail)
- https://www.blackbook.com/asset-verification-tool/ (AVT)
- https://www.blackbook.com/scenario-based-residuals-2/ · /residual-sensitivity-analysis/ · /residual-studies/ (residual suite)
- https://www.blackbook.com/black-book-index/ (UVI metodología)
- https://www.blackbook.com/lenders/ · /autofinance/ · /oem/ · /insurance/ · /marketing/ · /remarketing/ (verticales/casos)
- https://www.blackbook.com/what-is-my-car-worth/ (posicionamiento B2B vs KBB)
- PR: /black-book-launches-innovative-brand-value-index-…/ (BVI, 14-nov-2024)
- PR: /black-book-announces-expanded-residual-valuation-capabilities/ (1-120m / 10 MY, 21-oct-2022)
- PR: /black-book-launches-next-generation-valuengine-collateral-platform/ (ValuEngine, 2017)
- PR: /black-book-and-recurrent-collaborate-…-battery-data/ (EV Range Score, 7-sep-2022)
- PR: /2025-vehicle-depreciation-report-released-by-black-book-and-fitch-ratings/ (report Fitch, 16-jul-2025)

**Verificación cruzada (2ª fuente):**
- https://en.wikipedia.org/wiki/Black_Book_(National_Auto_Research) (fundación 1955, Hearst, scope, canales)
- D&B / NTEA / Yahoo Local — dirección HQ Lawrenceville GA (1745 N Brown Rd #130)
- https://www.hearst360.com/case-study/hearst-transportation (Hearst Transportation = MOTOR + Black Book + Canadian Black Book)
- Auto Remarketing / F&I Magazine (Tom Cross, Group Head of Transportation)
- Pocketsense / withclutch-stickers — condiciones Extra Clean/Clean/Average/Rough (definiciones)
- https://www.jdpower.com/black-book-values (referenciado; bloqueó fetch 403)

**Limitaciones de método:** WebFetch y archive.org bloqueados para este dominio; todo el contenido del sitio se obtuvo con `curl` + extracción de texto local. Páginas `/lender-portfolio-valuations/`, `/get-auto-data/`, `/residual-value-insights/`, `/dealers/` rinden contenido JS-renderizado no capturable por curl (formularios/redirect); sus capacidades se infieren de páginas hermanas y press releases [marcado donde aplica].
