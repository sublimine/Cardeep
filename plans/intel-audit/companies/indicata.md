# Auditoría atómica — INDICATA (Autorola Group)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos e inteligencia de automoción centrada en el **vehículo de ocasión (VO)**: market intelligence de precios/oferta/demanda, gestión de inventario, valoración y residual values.
> Web producto: https://indicata.com/ · Login plataforma: https://pro.indicata.com/login (vía AWS Cognito `auth.indicata.com`) · Web histórica (rica en detalle): https://www.indicata.co.uk/ (archivada) · Grupo: https://www.autorolagroup.com/ y https://autorolasolutions.com/
> Fecha auditoría: 2026-06-30. Método: navegación de indicata.com (5 páginas de segmento + market-tracker + company + market-watch), renderizado con Playwright (real browser, salta 403) de am-online y pro.indicata.com, recuperación vía Wayback CDX + curl de la **página de producto INDICATA 2019** (estructura atómica completa) y del **PDF "7 KPIs you must track"** (pdftotext → definiciones de KPIs), artículo **PwC "Autorola's Digital Revolution"** (identidad/escala/metodología), serie de **KPIs de Jörg Höhner en LinkedIn** (MDS, Stock Turn), prensa (Fleet News, Motor Trader, Fleet Europe) y agregadores (CB Insights, Tracxn, Crunchbase).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).
> Nota de alcance: el usuario citó "subdominio: market-intelligence". **VERIFICADO que NO existe**: `market-intelligence.indicata.com` no resuelve (HTTP 000) y `indicata.com/market-intelligence/` devuelve 404. "Market intelligence" es la **categoría/descriptor** del producto, no un subdominio. El subdominio operativo real es `pro.indicata.com` (la plataforma).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **INDICATA** | [V] |
| Categoría | **Business intelligence & analytics para operaciones de VO**: market intelligence de precios/oferta/demanda, gestión de inventario, valoración live, residual values y forecasting, generación de leads de reprise | [V] |
| Unidad de negocio | Una de las **3 unidades** de **Autorola Group**: (1) **Autorola Marketplace** (subastas online B2B), (2) **Autorola Solutions** (de-fleet management, inspección, software de procesos), (3) **INDICATA** (BI & Analytics) | [V — about/company + PwC] |
| Owner / grupo | **Autorola Group** | [V] |
| Propiedad última | **Peter Grøftehauge = propietario único desde diciembre 2023** (compró la parte de su hermano Martin) | [V — PwC] |
| HQ (grupo e INDICATA) | **Skibhusvej 52A, DK-5000 Odense C, Dinamarca** | [V — company + footer] |
| Fundación Autorola | **1996** (hermanos **Peter y Martin Grøftehauge**); plataforma de subastas online lanzada en **1998**; portal de valoración **Bilpriser.dk** (la "cash cow" inicial) | [V — PwC] |
| Lanzamiento INDICATA | **~2014** (la unidad usa **IA desde 2014** para reconocimiento de datos de coche + Big Data; primera gran alianza OEM pública **Volvo, nov-2015**). Año de constitución exacto **no publicado** | [V metodología/IA 2014 + Volvo 2015; A año exacto] |
| Entidad legal | **CVR: 30242882** (registro mercantil danés; footer indicata.com) | [V] |
| Tel / email | **(+45) 70 20 16 61** · **info@indicata.dk** | [V] |
| Empleados (grupo) | **~700–750** (PwC "over 700"; agregadores "~750"); snapshot 2016/2019 citaba **~350** | [V — variación temporal] |
| Países (grupo Autorola) | **19 países, 5 continentes** (Europa, Norteamérica, Latinoamérica, Asia-Pacífico) | [V — PwC + company] |
| Escala plataforma grupo | **70.000+ compradores/dealers activos** en el marketplace | [V] |
| Facturación grupo (2024) | **> 1.000M DKK** (~€134M) de ingresos; **83M DKK** de beneficio; objetivo +20% anual | [V — PwC] |
| Tagline INDICATA | "**Used vehicle decision making intelligence**" / "Put data-driven insights in every decision you make" | [V] |
| Liderazgo (BU INDICATA) | **Andy Shields** — Global Business Unit Director (2025) · **Dean Merritt** — UK Head of Sales (2026) · **Jörg Höhner** — Global Managing Director **2015–2017** (histórico; autor de la serie de KPIs) | [V — prensa] |
| Pila técnica | Plataforma web SaaS cloud; login federado vía **AWS Cognito** (`auth.indicata.com`, OIDC/PKCE) | [V — Playwright en pro.indicata.com] |

### Posicionamiento [V]
INDICATA se autodefine como "**global leader in providing business intelligence and analytics solutions for used car operations**". Producto de la colaboración entre ejecutivos del sector y desarrolladores; "engineered for high-performance used vehicle management". Slogan del 404/landing RV: "**Most see data. We reveal what it means**".

### Clientes objetivo (5 segmentos = arquitectura del sitio) [V]
1. **Dealer groups & retailers** (grupos de concesionarios y minoristas).
2. **OEMs & NSCs** (fabricantes y national sales companies).
3. **Fleet Remarketers** (remarketing de flotas).
4. **RV Setters & Risk managers** (fijadores de valor residual y gestores de riesgo: leasing, finanzas, banca).
5. **Insurance** (aseguradoras).

### Clientes nombrados [V]
**Volvo** (alianza nov-2015) · **Nissan GB** (renovación) · **BMW** · **Sixt** · **Santander** (vía grupo) · **John Clark Motor Group** (Indicata Pro en sus 54 concesionarios de Escocia, 2026) · **Glyn Hopkin** ("halved stocking days en 3 meses") · **Carbase** · **SLM Group / St Leonards Motors**. Marcas con assets de logo en web histórica: Audi, BMW, Citroën, Ford, Hyundai, Jaguar, Kia, Lexus, Mercedes, Opel, Renault, Tesla, Toyota, Volvo, VW.

---

## 2. Cobertura

### Geográfica [V]
- **INDICATA market intelligence / Market Watch: 16 países europeos + Brasil** = 17 mercados.
- Lista de mercados localizados (selector de idioma/región de indicata.com): **Reino Unido, Alemania, Francia, España, Italia, Países Bajos, Bélgica, Austria, Suiza, Suecia, Noruega, Finlandia, Dinamarca, Portugal, Polonia, Turquía** (16 europeos) **+ Brasil**.
- Idiomas: **~20 variantes** (DA, DE, DE-AT, DE-CH, EN-GB, EN-US, ES, FI, FR, FR-BE, FR-CH, IT, IT-CH, NL, NL-BE, NO, PL, PT-PT, PT-BR, SV, TR). Market Watch publicado en **9–10 idiomas**.
- Grupo Autorola opera en **19 países / 5 continentes** (mayor que el footprint de market intelligence de INDICATA).

### Escala de procesamiento de datos [V]
- **Hasta 15 millones de coches analizados a diario** mediante **reconocimiento de imagen avanzado** (image recognition). [V — PwC]
- Datos de **todos los VO actualmente a la venta** en cada mercado, recopilados **en tiempo real** (live market data).
- Histórico: **hasta 5 años** de tendencias de mercado (Market Tracker); valoraciones retrospectivas "millones de anuncios de años atrás" (seguros).
- Frecuencia de actualización: **live/diaria** en la plataforma Pro; **mensual** en Market Tracker y Market Watch.
- IA propia desde **2014** (departamento interno dedicado a IA).

### Scope de vehículos [V/A]
- **Núcleo absoluto = vehículo de ocasión (VO) / used cars** (turismos). [V]
- Market Tracker (UK): universo = "todos los VO vendidos en UK en los últimos 5 años, **>3 años de antigüedad y >38.000 millas** (~61.000 km)" — define el segmento de coche usado "maduro". [V]
- Atributos por vehículo: **make, model, trim/versión, body type, fuel type, transmission, category, segment, registration year, mileage, equipamiento ("similarly equipped")**. [V]
- **No se mencionan** motos, LCV ni vehículo industrial como tipos cubiertos (foco turismo VO). [A — ausencia, ver Gaps]

---

## 3. Productos + campos atómicos

INDICATA hoy comercializa **5 productos nombrados** (lista literal del formulario "I would like a demo of" en indicata.com) + el reporte **Market Watch** + **suites OEM** + **oferta seguros**. La plataforma core para dealers es **Indicata Pro / Inventory Management**. El detalle atómico de KPIs y pantallas proviene de la página de producto INDICATA (estructura estable confirmada en archivo 2019) + el PDF "7 KPIs".

> **Los 8 KPIs maestros de INDICATA** (motor de toda la plataforma) [V — página de producto + PDF 7 KPIs]:
> **Market Days Supply · Inventory Age · Price to Market · Pricing Strategy · Stock Turn · Share over First Price to Market · Price not changed recently · Too few pictures (Number of photographs)**

### 3.1 Indicata Inventory Management (plataforma "Indicata Pro" — producto core para dealers) [V]
Dashboard web con KPIs en tiempo real para "monitorizar el rendimiento, planificar estrategias, mejorar la transparencia de mercado, medir la posición de mercado al instante, conocer oferta/demanda del stock, optimizar precios y gestionar riesgos". Campos/KPIs atómicos:

**KPIs de inventario (los 8 maestros):**
- **Market Days Supply (MDS)** — días de oferta de mercado: nº de vehículos iguales/similares disponibles ÷ ventas retail medias/día (últimos **45 días**). Mide fuerza relativa oferta/demanda. **Benchmark 60–70** para el inventario total. (Ej.: 200 disponibles ÷ 4 vendidos/día = MDS 50.)
- **Inventory Age** (antigüedad de inventario / days in stock) — reparto fresh vs old. Bandas con benchmark recomendado: **1–30 días = 50%**, **31–60 = 30%**, **61–90 = 15%**, **90+ = 5%**.
- **Price to Market** (precio a mercado, %) — cómo se compara el precio del vehículo con el **precio medio de vehículos competidores iguales o equipados de forma similar** en el mercado.
- **Pricing Strategy** — el **price-to-market medio por cada banda de inventory age** (estrategia de precio por antigüedad).
- **Stock Turn** (rotación) — nº de veces/año que se vende el inventario = **ventas retail anuales ÷ nº de VO en stock**. **Benchmark 8–9x/año**; política de antigüedad 60–90 días, trade-out >90 días.
- **Share over First Price to Market** — % de vehículos del inventario cuyo precio ha "subido" relativamente (el mercado ha caído más de lo que se ha ajustado el precio desde la primera publicación).
- **Price not changed recently** — bandera de precio sin reajustar (precio estancado).
- **Too few pictures / Number of Photographs** — control del nº ideal de fotos online (calidad del anuncio; evitar "image fatigue" y maximizar conversión a leads).

**Datos de valoración y mercado por vehículo:**
- **Live market pricing**: nacional, local y **cross-border** (transfronterizo).
- **Retail price** (precio de venta minorista) y **trade / wholesale price** (precio mayorista/de comercio).
- **Vehículos competidores en el mercado** (ver el set de competencia para cada coche).
- **Demanda** (likely to sell quickly / sales rate) y **oferta** (supply) para tu stock.
- **Nivel de competencia** ("how much competition").
- **Clasificación fast-moving vs slow-moving** (rápido vs lento).
- **Recomendación stock vs trade** ("should it be stocked or traded? Retail or Trade?").

**Sourcing / stock locating:**
- **Mapa de stock de 140.000+ dealers** (franquiciados y no franquiciados).
- **Localización de stock pan-europea** para sourcing entre dealers (identifica el stock de venta más rápida).
- Análisis de mercado para "el stock óptimo a comprar" (no solo valora; recomienda qué comprar).

### 3.2 Indicata Lead Generator [V]
Herramienta de **valoración de reprise (trade-in) online** embebida en la web del concesionario para captar tráfico/leads. Campos:
- **Valoración de trade-in online** para el visitante de la web.
- Entrega como **API** (alimenta el interfaz de valoración propio de la web del cliente) **o** módulo **"plug & play"** preconfigurado de INDICATA.
- **Captura de lead** (contacto) → oportunidad de venta.
- Resultado declarado: **triplica (3×)** la generación de leads de la web. Despliegue directo a OEM o vía red de dealers.

### 3.3 Indicata Forecasting [V]
Forecasting de **valor residual (RV)** con el motor de valoración de INDICATA. Campos:
- **Valoraciones actuales** (current valuations) — dataset consistente y de calidad.
- **Curvas de RV futuras** (future RV curves) por mercado.
- **Métodos estandarizados** de valoración y forecasting **desplegados en todos los países** (comparabilidad cross-market).
- **Overlay macroeconómico** + análisis de tendencia (fact-based) sobre el histórico para las predicciones.
- Forecasts **transparentes y específicos por mercado**.
- Entrega: **API** directa a sistemas del cliente · **CSV / Excel** (bulk) · **interfaz visual "Forecast Module"**.
- Soporte: Market Watch reports, White Papers, webinars que explican supuestos y tendencias.

### 3.4 Indicata Market Tracker (lanzado 20-feb-2026) [V]
Plataforma "plug & play" de inteligencia de mercado de VO; dashboard único que une histórico **hasta 5 años** + actualizaciones **mensuales en tiempo real**. Para OEM, leasing/rental y dealer groups. Campos/vistas:
- **Price Index & market trend analysis** (índice de precios y análisis de tendencia).
- **Market Days Supply (MDS)**.
- **Supply & demand dynamics** (dinámica de oferta y demanda).
- **Brand, model & segment comparisons** (comparativas marca/modelo/segmento).
- **Cross-country views with multi-year data** (vistas multi-país con datos multi-año).
- **Filtros**: **make, model, body type, fuel type, category, segment, transmission**.
- **RV pressure / demand fluctuations / stock trends** (presión sobre RV, fluctuaciones de demanda, tendencias de stock).
- "Qué vehículos se mueven y cuáles no."
- Beneficio por rol: OEM → posicionamiento competitivo, cuota de mercado, performance por segmento; leasing/rental → presión de RV, riesgo de cartera, composición de flota; dealers → oportunidades de precio, forecast de demanda, eficiencia de stock turn.
- **4 niveles de suscripción** (desde herramienta simple con filtros básicos hasta motor multi-país, todas las marcas). [V — prensa AM/Fleet News]

### 3.5 Indicata RV Tracker [V]
Inteligencia de **valor residual** para fijación de RV y gestión de riesgo (OEM, leasing, finanzas). "RV Tracker turns data into decision-ready insight." Campos:
- **Vista multi-mercado armonizada** (harmonised multi-market view).
- **Benchmarking competitivo** de RV (competitive RV comparison).
- **Análisis RV histórico, actual y forecast** (historical, current & forecast RV analysis).
- **Insight de value drivers y tendencias** (qué impulsa el valor).
- **Totalmente configurable**: por mercados, marcas y selección de vehículos.
- **Acceso a RV Market Experts** (sesiones dedicadas incluidas en la licencia) para interpretar tendencias.
- **Executive Breakfast events** (invite-only) y **RV Intelligence Check** (sesión de benchmark de mercado: benchmark por segmentos/marcas, comparación RV competitiva, tendencias clave, riesgos y oportunidades).
- Foco por usuario: OEM (Product&Pricing, Fleet&Remarketing, RV Management) y Leasing&Finance (Pricing&Future Values, Risk&Portfolio, Finance).

### 3.6 Indicata Market Watch (reporte) [V]
Informe **mensual** de insights del mercado de VO europeo. Campos:
- Cobertura **16 países europeos + Brasil**, en **9–10 idiomas**.
- **Índice de precios de VO** y cambios de precio medio.
- **Market Days Supply (MDS) indicators**.
- **Oferta / demanda / niveles de stock** y tendencias.
- Tendencias por **tipo de combustible** (EV/ICE) y desarrollos de mercado por país.
- Entrega: **descarga PDF** previa registro/suscripción; complementado con White Papers y webinars.

### 3.7 Suites para OEM & NSC [V]
- **CPO Reporting Suite** — efectividad del programa Certified Pre-Owned: **% de stock vendido a través de la red**, RV tracking, **rentabilidad de la red**, performance en tiempo real sobre 140.000 retailers branded y no-branded.
- **Network Reporting Suite** — performance **dealer por dealer**; de métricas de alto nivel a issues vehículo por vehículo; identifica mejores/peores ubicaciones; **early warning de viabilidad financiera** del dealer.
- **Brand Stock Tracking** — monitoriza **cada VO de la red de la marca** (quién lo vende y a qué precio); detecta **leakage de producto** a retailers no-branded; tendencias de mercado + métricas de retención.

### 3.8 Oferta para Insurance [V]
- **Settlement Pricing** — valoración online vía **API** integrada en sistemas de cotización del asegurador (valoración instantánea de cualquier vehículo).
- **Retrospective Valuations** — valoración del vehículo **a una fecha concreta** (de siniestro/accidente) accediendo a "millones de anuncios de años atrás".
- **Evidence-Based Settlement Values** — valores de liquidación basados en comparación con **vehículos equivalentes y sus precios anunciados** (reduce disputas).
- Entrega: **API** directa · **CSV/Excel** (bulk) · interfaces a medida.

---

## 4. Metodología y fuentes de datos [V]
- **Valor 100% de mercado y observado**: INDICATA "**collects, processes and analyses live used car market data**" para insights de **demand, supply, pricing, inventories**. Datos de **todos los VO actualmente a la venta** en un mercado, recopilados **en tiempo real**.
- **Reconocimiento de imagen avanzado (image recognition)** para analizar **hasta 15M coches/día** — la IA "lee" anuncios online y extrae/normaliza atributos del vehículo. [V — PwC]
- **IA + Big Data desde 2014**; departamento interno de IA dedicado; cultura data-driven; "trial and error" como método.
- **Granularidad de matching** (MDS): vehículos con **mismo registration year, make, model, trim level y configuración exacta o similar** ("same or similarly equipped").
- **Sales Rate**: ventas retail/día (ventana **45 días**) como denominador de demanda en MDS.
- **Forecasting**: motor de valoración propio → curvas RV futuras; **métodos estandarizados en todos los países**; **overlay macroeconómico** + análisis de tendencia sobre histórico.
- **Frecuencia**: plataforma Pro **live/diaria**; Market Tracker y Market Watch **mensual**; histórico hasta **5 años**.
- **Sinergia de grupo ("sweet spot")**: INDICATA (market intelligence) + Autorola Marketplace (subasta B2B) + Autorola Solutions (de-fleet/inspección, p.ej. **Fleet Monitor**) → ecosistema digital completo para decidir cuándo/dónde defleet y exportar cross-border según el footprint de datos europeo.

---

## 5. Entrega
- **Plataforma web SaaS (Indicata Pro)**: `pro.indicata.com`, login federado **AWS Cognito** (`auth.indicata.com`). Dashboards web en tiempo real. [V]
- **API**: Lead Generator (valoración trade-in), Forecasting (RV a sistemas del cliente), Insurance (settlement pricing en cotizadores). [V]
- **Módulo embebible "plug & play"** en la web del concesionario (Lead Generator). [V]
- **Carga/intercambio masivo**: **CSV y Excel** (Forecasting, Insurance bulk). [V]
- **Dashboard "plug & play"** independiente: Market Tracker (multi-año, single view). [V]
- **Informe / PDF**: Market Watch mensual (descarga con registro), White Papers, Executive Reports. [V]
- **Servicios profesionales** ("your Sherpa"): Implementation, Training, Advanced analytics, **Inventory assessment workshops**, Executive reports, **Integrations** (a DMS/sistemas del cliente). [V]
- **Sesiones expertas**: RV Market Experts, RV Intelligence Check, Executive Breakfast (RV Tracker). [V]
- Multi-idioma (~20 variantes) y multi-mercado. [V]

---

## 6. Precio
- **No público.** No hay tarifas en la web; footer indica "**All prices are stated including VAT**" pero sin importes. [V]
- Modelo = **suscripción / licencia SaaS** por producto y módulo; acceso vía "**Request a demo**" / "Contact sales". [V]
- **Market Tracker**: **4 niveles de suscripción** ("desde herramienta muy accesible con filtros simples hasta motor de decisión multi-país, todas las marcas"). [V — prensa]
- **RV Tracker**: licencia que **incluye sesiones de RV Market Experts** + acceso a Executive Breakfast. [V]
- **Importe concreto = GAP** (no descubrible públicamente). Histórico: ofrecía "free trial".

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. La plataforma INDICATA es una **jerarquía de pantallas** (de grupo → dealer → vehículo) sobre el mismo set de 8 KPIs. Mapeo pantalla → dato [V — "Unique Suite of Advanced Modules & Features": Group overview, Dealer dashboard, Inventory list, Vehicle Details, Benchmark set, Vehicle appraisal].

### Pantalla "Group overview" (nivel grupo/HQ/NSC) [V]
- KPIs agregados de toda la organización (corporate, NSC, importador, field, dealer).
- Identifica **ubicaciones bajo-rendimiento** y problemas de "used car culture"; comparativa **location by location, brand by brand**.
- Para OEM: cuota de mercado, performance de red, % stock vendido por la red, leakage.

### Pantalla "Dealer dashboard" (nivel concesionario) [V]
- Resumen de los **8 KPIs** del dealer (MDS, inventory age, price to market, pricing strategy, stock turn, share over first price to market, price not changed, too few pictures).
- **Alertas** de "specific stock issues" + insight de **cómo ocurrieron** (proactivo/reactivo).

### Pantalla "Inventory list" (lista de stock) [V]
- Filas vehículo a vehículo con: **price to market %, days in stock (inventory age), MDS, demanda, bandera de pocas fotos, bandera de precio sin cambiar, fast/slow-moving**.
- Base para repricing diario "vehicle by vehicle / every day".

### Pantalla "Vehicle Details" (ficha de vehículo) [V]
- Por vehículo: **live retail price, trade/wholesale price, price-to-market %, MDS, vehículos competidores en el mercado, nivel de competencia, días en stock, demanda/oferta**, recomendación **stock vs trade**.
- Precios **nacional / local / cross-border**.

### Pantalla "Benchmark set" (set de comparables) [V]
- Definición del **conjunto de vehículos competidores/comparables** (mismo o similarmente equipado) contra el que se calcula price-to-market y MDS.

### Pantalla "Vehicle appraisal" (tasación/reprise) [V]
- Valoración de **trade-in / appraisal** del vehículo entrante; decisión de **stock vs trade**; alimenta Lead Generator (valoración online → lead).

### Market Tracker — dashboard de mercado [V]
- Vista única con **price index + trend**, **MDS**, **curvas oferta/demanda**, **comparador marca/modelo/segmento**, **cross-country multi-año**; barra de **filtros** (fuel/transmission/body/segment/category).

### RV Tracker — dashboard de residuales [V]
- **Vista multi-mercado armonizada**, **curvas RV histórico/actual/forecast**, **benchmark RV competitivo**, panel de **value drivers/tendencias**; configurable por mercado/marca/selección.

### Lead Generator — widget en web del concesionario [V]
- Formulario de **valoración trade-in online** embebido → resultado de valor → **captura de lead** (contacto).

### Market Watch — informe mensual [V]
- Documento por país: **índice de precios**, **MDS**, **oferta/demanda/stock**, tendencias por **combustible (EV/ICE)**; narrativa de mercado.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Market intelligence "live" por reconocimiento de imagen a escala masiva**: hasta **15M coches/día** leídos de anuncios online; valor 100% observado del mercado real, no editorial.
- [V] **Set de KPIs operativos accionables y estandarizados** (MDS, inventory age, price-to-market, pricing strategy, stock turn, share over first price to market) con **benchmarks publicados** (MDS 60–70; stock turn 8–9x; bandas de edad 50/30/15/5%) — orientado a **gestión de stock y repricing diario**, no solo a "una valoración".
- [V] **Plataforma jerárquica grupo→dealer→vehículo** (Group overview / Dealer dashboard / Inventory list / Vehicle Details) — pensada para grupos multi-sitio y redes OEM, con **early-warning** y detección de **leakage** de producto.
- [V] **Stock locating sobre 140.000 dealers** + pricing **cross-border** → sourcing y arbitraje de exportación pan-europeo (sinergia con subasta Autorola Marketplace).
- [V] **"Sweet spot" de ecosistema**: única que combina **market intelligence (INDICATA) + subasta B2B (Marketplace) + de-fleet/inspección (Solutions)** bajo un mismo grupo — workflow VO de extremo a extremo.
- [V] **RV Tracker con experto humano incluido** (RV Market Experts + Executive Breakfast + RV Intelligence Check): "no es solo data, es entender lo que significa".
- [V] **Forecasting RV estandarizado cross-market** con overlay macroeconómico (comparabilidad real entre 16+ países).
- [V] **Valoración retrospectiva a fecha de siniestro** para seguros (millones de anuncios históricos) — caso de uso poco común.
- [V] **Lead Generator que triplica leads** de la web del dealer — captación comercial, no solo dato.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Precio no público**: sin tarifas; todo vía demo/contacto (importe = GAP).
- [V] **Sin subdominio `market-intelligence`** (no resuelve / 404): el término es categoría, no un portal independiente; la plataforma real es `pro.indicata.com`.
- [V] **Web actual pobre en detalle atómico**: el sitio nuevo (indicata.com) es por **segmento** y muy marketing; **no hay páginas de producto dedicadas** (solo Market Tracker tiene landing). El detalle de KPIs/pantallas hubo que recuperarlo de la web histórica (2019) y del PDF de KPIs.
- [V] **Sin documentación técnica de API pública**: no hay esquema JSON, auth, rate limits ni diccionario de campos del API (Lead Generator/Forecasting/Insurance) expuestos.
- [A] **Sin historial de vehículo / siniestros / fraude de km por VIN** tipo Carfax/autoDNA: INDICATA da posición de mercado y valor, no provenance/propietarios/incidentes certificados.
- [A] **Sin decode/identificación por VIN como producto** (a diferencia de autobizVIN/JATO): identifica por make/model/trim/equipamiento vía image recognition, no un servicio VIN-to-spec declarado.
- [A] **Sin datos OEM de mantenimiento/reparación tipo SMR** (tiempos de mano de obra, precios de piezas, TecDoc): calcula posición de precio/RV, no catálogo de reparación.
- [A] **Sin tipos de vehículo más allá de turismo VO**: no se mencionan motos, LCV ni industrial.
- [A] **Sin inteligencia de batería/EV granular** (kWh, química de celda, SoH) más allá de tendencias EV/ICE en Market Watch.
- [A] **Sin TCO/coste total de propiedad** como producto.
- [A] **Sin marketplace transaccional propio de listados** dentro de INDICATA (lo transaccional vive en la unidad hermana **Autorola Marketplace**, no en INDICATA).
- [A] **Métricas tipo "price-to-market %" sí, pero "days-to-sell" como índice nombrado no**: usan **Market Days Supply** y **stock turn / inventory age** en su lugar (days-to-sell es derivable de MDS).
- [A] **Foco de cobertura europeo + Brasil**: ausencias notables (EE.UU./Norteamérica no es mercado de market intelligence de INDICATA pese a presencia del grupo Autorola).

---

## 10. Fuentes (URLs)
- https://indicata.com/ — home, tagline, 5 segmentos, 5 productos, 16 países+Brasil, menú/links.
- https://indicata.com/dealer-groups-and-retailers/ — sourcing, 140.000 dealers, live pricing nacional/local/cross-border, retail/trade, fast/slow, stock vs trade, Lead Generator 3×.
- https://indicata.com/oems-and-nscs/ — CPO Reporting, Network Reporting, Brand Stock Tracking, % stock sold, leakage, early warning.
- https://indicata.com/rv-setters-and-risk-managers/ — Indicata Forecasting (motor de valoración, RV curves, macro overlay, API/CSV/Excel/Forecast Module).
- https://indicata.com/fleet-remarketers/ — start/reserve/buy-it-now pricing, Geo Pricing, Export Index, European Target Price, Marketability Scores.
- https://indicata.com/insurance/ — Settlement Pricing (API), Retrospective Valuations, Evidence-Based Settlement Values, CSV/Excel.
- https://indicata.com/market-tracker/ — Price index, MDS, supply/demand, brand/model/segment, cross-country multi-año, filtros, plug&play (renderizado vivo).
- https://indicata.com/market-watch/ — 16 países + Brasil, 9 idiomas, descarga con registro.
- https://indicata.com/company/ — Autorola Group, HQ Odense, 3 unidades, ~750 empleados, 21 países (versión actual).
- https://pro.indicata.com/login → https://auth.indicata.com/ — login AWS Cognito (pila técnica) [Playwright].
- https://web.archive.org/web/20190720200709/https://www.indicata.co.uk/product/ — **estructura atómica**: 8 KPIs (MDS, inventory age, price to market, pricing strategy, stock turn, share over first price to market, price not changed, too few pictures) + 6 módulos (Group overview, Dealer dashboard, Inventory list, Vehicle Details, Benchmark set, Vehicle appraisal) + servicios [curl].
- https://www.indicata.co.uk/images/blogs/7_KPIs_you_must_track_in_used_vehicle_business.pdf — **definiciones y benchmarks** de los 7 KPIs (pdftotext): stock turn, MDS, inventory age (bandas 50/30/15/5%), price to market, pricing strategy, share over first price to market, number of photographs.
- https://www.linkedin.com/pulse/...part-jörg-höhner — KPI Part 1 **Market Days Supply** (fórmula, benchmark 60–70, ventana 45 días).
- https://www.linkedin.com/pulse/...part-jörg-höhner-1 — KPI Part 2 **Stock Turn** (fórmula, benchmark 8–9x, política 60–90 días).
- https://www.fleeteurope.com/.../7-kpis-track-order-maximise-used-vehicle-business — los 7 KPIs de INDICATA (2ª fuente).
- https://autorolasolutions.com/autorolas-digital-revolution-in-the-automotive-industry/ — **PwC**: fundación 1996, Grøftehauge propietario único dic-2023, 19 países/700+ empleados, 3 unidades, **INDICATA = 15M coches/día por image recognition**, IA desde 2014, ingresos >1.000M DKK 2024 [curl].
- https://www.am-online.com/news/indicata-launches-market-tracker-used-car-intelligence-platform — Market Tracker (20-feb-2026): 5 años histórico, UK >3 años/>38.000 millas, filtros, mensual, beneficios por rol [Playwright].
- https://www.am-online.com/news/dealer-group-adopts-indicata-pro-insights-platform y motortrader.com — **Indicata Pro** en John Clark Motor Group (54 sedes Escocia): real-time market & pricing intelligence, group-wide stock visibility, competitor benchmarking.
- https://www.fleetnews.co.uk/news/new-used-car-intelligence-platform-launched-by-indicata — Market Tracker, 4 niveles, 16 países.
- https://www.autorolagroup.com/indicata_sep2025/ y .../indicata_oct2025/ — Market Watch (16 países+Brasil, 9 idiomas, MDS indicators), estudio de 73 redes OEM en 12 países.
- https://www.am-online.com/news/technology/2015/11/26/volvo-to-boost-used-car-business-with-market-insight-from-autorola — alianza Volvo (nov-2015), identidad temprana.
- CB Insights / Tracxn / Crunchbase (Autorola Group) — verificación cruzada de owner, HQ, empleados.
- Verificación negativa: `market-intelligence.indicata.com` HTTP 000 + `indicata.com/market-intelligence/` HTTP 404 (curl) → subdominio inexistente.

> Verificación: identidad/escala con ≥2 fuentes (company + PwC + agregadores). KPIs y pantallas [V] leídos de la página de producto INDICATA (archivo 2019, estructura estable) + PDF "7 KPIs" + serie LinkedIn (definiciones/benchmarks). Metodología (15M/día, image recognition, IA 2014) [V] vía PwC. Productos actuales [V] del formulario de demo en indicata.com. Precio = no público (GAP). Año de constitución exacto de INDICATA y docs de API no hallados (marcados [A]/GAP, no inventados).
