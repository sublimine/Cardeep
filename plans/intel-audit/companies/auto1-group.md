# Auditoría atómica — AUTO1 Group (AUTO1.com · wirkaufendeinauto.de · Autohero)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa **transaccional** de automoción de ocasión (VO) con un componente de **inteligencia de precios mayorista** propio: la inteligencia de AUTO1 NO se vende como SaaS de analítica independiente (a diferencia de Indicata/Autovista), sino que está **embebida en su marketplace B2B** (AUTO1 Price Indicator) y **publicada como índice de mercado gratuito** (AUTO1 Group Price Index). Su activo único = la mayor base de datos europea de **transacciones mayoristas REALES de VO** desde 2015.
> Webs: grupo https://www.auto1-group.com/ · marketplace B2B https://www.auto1.com/ · EVA https://www.auto1.com/en/auto1-eva · Price Index https://www.auto1-group.com/index/ · sourcing particulares https://www.wirkaufendeinauto.de/ · retail B2C https://www.autohero.com/
> Fecha auditoría: 2026-06-30. Método: WebSearch + WebFetch sobre auto1-group.com (company, index, blog, press) y auto1.com (home/buy/sell), renderizado **Playwright** (innerText real) de las SPA `auto1.com/en/auto1-eva`, `/en/home/sell` y `/en/home/buy` (extracción literal de servicios y flujo), press releases del Price Index (métricas exactas), CNBC (IPO), agregadores financieros.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre) · **[NV]** = no verificado.
> Nota de alcance: el usuario citó "subdominio: wholesale-intelligence". **VERIFICADO que NO es un host vivo**: `wholesale-intelligence.auto1.com` no resuelve (ENOTFOUND). Es el **descriptor de categoría** de cardeep (la inteligencia mayorista de AUTO1), no un portal independiente. El subdominio operativo real del marketplace es `www.auto1.com` (B2B, cerrado, solo dealers verificados).
> ⚠ **Aviso anti-contaminación:** durante el render, un enlace de la web derivó a `auth.bca.co.uk` / BCA España (British Car Auctions / Constellation Automotive Group), empresa **DISTINTA y competidora**. Nada de BCA (AVILOO battery check, "14 países", etc.) se atribuye a AUTO1 en este informe.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca / grupo | **AUTO1 Group SE** (Societas Europaea, cotizada) | [V] |
| Categoría | **Plataforma digital transaccional de VO** (marketplace mayorista B2B + retail B2C + compra a particulares) **con inteligencia de precios mayorista propia** (Price Index público + Price Indicator embebido) | [V] |
| Marcas operativas | **3**: (1) **wirkaufendeinauto.de** y marcas hermanas — compra a particulares (sourcing); (2) **AUTO1.com** — marketplace mayorista B2B (segmento *Merchant*); (3) **Autohero** — venta retail B2C online (segmento *Retail*) | [V — company] |
| Producto de inteligencia | **AUTO1 Group Price Index** (índice de precios mayorista europeo, público) + **AUTO1 Price Indicator** (valoración en tiempo real embebida en EVA/plataforma) | [V] |
| Owner / propiedad | **Cotizada** en Frankfurt (Prime Standard). Respaldada históricamente por **SoftBank** (inversor pre-IPO). Incluida en el índice **STOXX Europe 600** (mar-2025) | [V — CNBC + press] |
| HQ | **Berlín, Alemania** — AUTO1.com GmbH, **Bergmannstrasse 72, 10961 Berlin** (footer/Imprint del sitio). Segunda base en **Múnich** | [V sede Berlín; A Múnich vía agregador] |
| Fundación | **2012**, por **Christian Bertermann** (CEO & co-fundador) y **Hakan Koç** | [V — financecharts + company] |
| IPO | **4-feb-2021**, Frankfurt Stock Exchange (Prime Standard), ticker **AG1**; captó **~€1.800M** de acciones de nueva emisión; +45% el primer día | [V — CNBC] |
| Ticker / cotización | **AG1** (Xetra/Frankfurt) · OTC US **ATOGF** · market cap ~$5,55B (may-2026) | [V — financecharts/PitchBook] |
| Empleados | **~6.300** (fin 2024) → **~8.600** (fin 2025) | [V — press + company] |
| Ingresos | **€6,3B** (2024) → **€8,2B** (2025); TTM ~$8,5B | [V — company + press] |
| Beneficio (2024) | Gross profit **€724,7M** (+37,3% YoY); Adj. EBITDA **€109,2M** | [V — press FY2024] |
| Segmentos | **2**: *Merchant* (AUTO1.com B2B) ingresos €1,3B 2024 (+26%); *Retail* (Autohero B2C) €352,5M 2024 (+38,8%) | [V — press FY2024] |
| Escala transaccional | **6M+ coches comercializados** desde 2012; **842.200+ vendidos en 2025** (2024: **689.773** = Merchant 615.335 + Retail 74.438) | [V — company + press] |
| Red logística | **170+ centros logísticos** + **300+ socios logísticos** (transporte pan-europeo) | [V — company] |
| Tagline | "Europe's leading digital automotive platform" / "Transform the used car market by building the best way to buy, sell, and finance cars" | [V] |

### Clientes objetivo [V]
- **Compradores B2B**: concesionarios profesionales (solo dealers verificados; alta requiere registro mercantil de comerciante de coches).
- **Vendedores B2B / partners de Remarketing**: **car dealers, dealer groups, leasing & rental companies, OEMs, banks, fleet providers** (lista literal del sell page).
- **Particulares**: vendedores (vía wirkaufendeinauto.de) y compradores retail (vía Autohero).
- Red: **60.000+ dealers activos** en **30+ países**.

---

## 2. Cobertura

### Geográfica [V]
- **30+ países / mercados** de Europa continental (marketplace B2B AUTO1.com) con **60.000+ dealers activos**.
- **AUTO1 Group Price Index**: cobertura **pan-europea** (todos los mercados de AUTO1; "first of its kind at a European level").
- **wirkaufendeinauto.de** + hermanas: **725+ puntos de entrega** / **350+ sucursales** en Europa para compra a particulares.
- Marcas localizadas detectadas: Austria, Bélgica, Francia, Alemania, Italia, Países Bajos, Portugal, España, Suecia (entre otras dentro de los 30+).

### Scope de vehículos [V/A]
- **Núcleo absoluto = turismo de OCASIÓN (VO)**. [V]
- **Cross-brand / brand-independent** (todas las marcas; "large brand-independent stock"). [V]
- Incluye explícitamente: **trade-ins, marcas de terceros, devoluciones de leasing, coches dañados** ("damaged cars where dealers need fast usage decisions"). [V]
- **EV/BEV**: comercializados como cualquier VO (no hay producto de salud de batería propio verificado en AUTO1 — ver Gaps; AVILOO es de BCA, no de AUTO1). [V ausencia]
- **No se mencionan** motos, LCV ni vehículo industrial como tipos cubiertos. [A — ausencia, ver Gaps]

### Escala / frescura de datos [V]
- **30.000+ VO inspeccionados** en stock en todo momento; **3.000+ coches nuevos añadidos al día**.
- Base de inteligencia: **transacciones mayoristas REALES** acumuladas desde **ene-2015**; volumen citado creciente: **~3,6M** (releases antiguas) → **~5,8M** (abr-2026) → **~6M** (general).
- Price Index: actualización **mensual**. Price Indicator y marketplace: **tiempo real / 24-7**.

---

## 3. Productos + campos atómicos

AUTO1 expone su inteligencia en **2 superficies de datos** (Price Index público + Price Indicator embebido) sobre una plataforma transaccional de **3 marcas**. Detalle atómico por producto:

### 3.1 AUTO1 Group Price Index — índice de precios mayorista europeo (PRODUCTO DE DATOS PÚBLICO) [V]
Único índice europeo basado en **precios de venta y transacción REALES de VO mayorista** desde 2015. Publicación **mensual**. Campos/métricas atómicas:
- **Valor del índice** (en puntos; **base ene-2015 = 100**). Ej. verificado: **abr-2026 = 142,0 pts** (mar-2026 = 139,3; abr-2025 = 141,9).
- **Variación mes a mes (MoM %)** — ej. abr-2026 **+1,9%**.
- **Variación acumulada en el año (YTD %)** — ej. 4 primeros meses 2026 **+4,0%**.
- **Variación interanual (YoY %)** — ej. abr-2026 vs abr-2025 **+0,1%**.
- **Precio medio de venta mensual** (mean sales price por categoría) — base del cálculo.
- **Serie desestacionalizada** (modelo de **descomposición aditiva a 12 meses** que extrae y elimina la estacionalidad).
- **Segmentación interna del cómputo** (para representatividad): **clase de vehículo · tipo de combustible · rango de antigüedad · rango de kilometraje**. (Ponderaciones actuales + históricas agregadas.)
- **Tratamiento de outliers**: precios/edad/km fuera del percentil **[0,5 ; 99,5]** se descartan.
- **Sentimiento de dealers** (en algunas notas: encuesta de expectativas, p.ej. "half of European dealers foresee further declines", ene-2026). [V — release ene-2026]
- Disclaimer: "shouldn't be considered predictive" (no es forecast). [V]

### 3.2 AUTO1 Price Indicator para Trade-Ins — valoración mayorista en tiempo real (DATO EMBEBIDO) [V]
Herramienta de **precio mayorista en tiempo real** para tasar un trade-in en **~5 minutos**, integrada en EVA y en la plataforma de Remarketing. Campos:
- **Precio estimado de trade-in (€)** en tiempo real, basado en **mercado actual + pujas en tiempo real (real-time bidding)**.
- Base de datos: **"datos de 3,6M+ coches vendidos"** (sell page, 2026); históricamente citado como **"2M transacciones"** (app store, ~2020-2022) → la base crece.
- Sirve de referencia para fijar el **precio esperado / expectativa de precio** que el vendedor introduce en subasta.

### 3.3 AUTO1.com — marketplace mayorista B2B (segmento Merchant) [V]
Plataforma cerrada (solo dealers verificados; alta con registro mercantil, verificación en horas). Inventario de **30.000+ VO inspeccionados**, **3.000+/día**. Campos/funciones:

**Canales de venta (sourcing channels) [V]:**
- **Customer Auction** (subasta de coches de particulares — acceso exclusivo al mayor canal de trade-ins de particulares de Europa, vía wirkaufendeinauto).
- **24h Auction** (subasta que cierra en 24h; cada coche se subasta **individualmente**, sin block auctions).
- **Instant Purchase / Direct Buy** (compra inmediata 24-7, precio fijo).
- **Catalogue Auction** (subasta por catálogo). [V — buy page menciona los 3 principales + catálogo]

**Herramientas de compra [V]:**
- **Live bidding dashboard** — pujar por varios coches a la vez y gestionar todos los trades en una vista.
- **Smart bid agent** (agente de puja automático: puja eficiente sin estar presente).
- **Búsqueda detallada + funciones de alerta** (filtros sobre el stock).
- **Watchlist** (lista de seguimiento).
- **Search requests / alertas** (notificación instantánea cuando entra un coche que casa con tus criterios).
- **Default settings / automatización** del proceso.
- App móvil iOS/Android + desktop, 24-7.

**Datos por vehículo (ficha de coche / inspección) [V/A]:** cada listado se alimenta del **esquema de inspección EVA** (ver 3.4). Documentación de condición fiable por coche ("fully documented", "reliable documentation of car condition", "inspection report"). Campos atómicos = el set EVA + estado de subasta:
- Identidad: **VIN, marca, modelo, versión** [A versión], **primera matriculación** [A], **kilometraje**, **combustible**, **cambio/transmisión**, **potencia** [A], **color** [A].
- **Equipamiento/opciones** (importado vía **DAT** por VIN).
- **Inspección de condición**: daños, *highlights*, ruedas (neumáticos/llantas), frenos, test drive, documentos de servicio (ver 3.4).
- **Fotos** del coche (set guiado).
- Estado de mercado: **canal**, **puja actual / nº de pujas**, **nº de visualizaciones** (lado vendedor), **precio Instant Purchase**, **fin de subasta (24h)**, **ubicación/país de origen**, **coste de transporte** (ruta más rápida vs más barata).

### 3.4 AUTO1 EVA App — evaluación/digitalización de VO (esquema de inspección) [V]
App de auto-evaluación (iOS/Android) que digitaliza un trade-in en **<15 min** y lo pone a la venta ante **60.000 dealers**. Guía paso a paso; sincroniza desktop↔móvil; importa **DAT** automáticamente. **7 módulos** (literal del render):
1. **Car details** — info general: **Model, Gear (cambio), Fuel type, etc.** (+ kilometraje, matriculación [A]).
2. **Test drive** — documentar hallazgos de la prueba de conducción.
3. **Car photos** — fotos del coche (guiadas).
4. **Car quality** — capturar **damages (daños) & highlights**.
5. **Wheels and brakes** — documentar **rueda: neumáticos (tires), llantas (rims) y frenos (brakes)**.
6. **Equipment** — seleccionar el equipamiento existente **a partir del import DAT** (por VIN).
7. **Service and Documents** — fotos de los **documentos de servicio** (historial).
+ **VIN** y **mileage** (app store). + **Price Indicator** integrado (3.2). + Acciones de subasta: introducir precio esperado, **cambiar precios, aceptar pujas, reintroducir coche en subasta**.

### 3.5 AUTO1.com Remarketing — venta B2B full-service (servicio + reporting) [V]
Solución full-service de remarketing (evaluación → marketing → venta → entrega) para dealers, grupos, **leasing/rental, OEMs, bancos, flotas**. "Servicios AUTO1.com" (literal):
- **Self-Evaluation App** (EVA, 15 min).
- **Mobile Evaluation Service** (evaluadores de AUTO1 inspeccionan los coches **en el lote del cliente**).
- **Seamless integration via API** — conectar el sistema del cliente vía **REST API** ("Request API description"). [V]
- **Price Indicator for Trade-Ins** (3.2).
- **Logistics Services** (transporte a medida).
- **Live Reporting Tools** — **Remarketing Dashboard**: monitorizar/controlar todas las interacciones; **tracking en tiempo real de visualizaciones y pujas por coche**; descarga de reportings.
- 4 vías de carga de coche: EVA app · evaluador móvil · **subir inspecciones existentes** · **API**.

### 3.6 Financiación (servicio adyacente) [V]
- **Merchant Financing** (financiación a dealers, in-house, digital).
- **Consumer Financing** (financiación al particular, vía Autohero).
- Sin campos de dato de mercado; es servicio financiero, no producto de inteligencia.

### 3.7 Autohero — retail B2C (contexto, fuera de "wholesale-intelligence") [V]
Marca retail online: VO inspeccionados con **financiación, entrega, trade-in y garantía de devolución 21 días**. 74.438 unidades 2024. Ficha de coche B2C con condición detallada [A]. Relevante solo como **destino downstream** del dato; no es producto de inteligencia mayorista.

> **Resumen de la inteligencia AUTO1** (clave para cardeep): no hay dashboard de analítica vendido por suscripción. Las dos superficies de dato son **(a) Price Index público** (índice agregado de mercado) y **(b) Price Indicator embebido** (valor por coche en el flujo de venta). Todo lo demás (RV%, days-to-sell, price-to-market, MDS…) **no existe** como métrica expuesta (ver Gaps).

---

## 4. Metodología y fuentes de datos [V]
- **Valor 100% transaccional REAL**: el Price Index se basa en **"actual sales and transaction prices of wholesale used cars"** — precios de transacciones mayoristas reales cerradas en la propia plataforma, **no en anuncios/listings ni en valor editorial**. Diferencia metodológica nuclear frente a Indicata (image recognition de anuncios) o cap hpi/Schwacke (editorial).
- **Base**: la propia red AUTO1.com (60.000 dealers, 30+ países) genera el dato al transaccionar; acumulado desde **ene-2015** (Price Index) y creciente (3,6M→5,8M→6M transacciones).
- **Price Index — cálculo**: media mensual de precios por categoría; **modelo de descomposición aditiva a 12 meses** para extraer/quitar estacionalidad; **ponderaciones** actuales + históricas agregadas; segmentación por **clase/combustible/edad/km**; recorte de **outliers** fuera del percentil [0,5; 99,5]; base 100 = ene-2015. Publicación mensual; explícitamente **no predictivo**.
- **Price Indicator — cálculo**: precio mayorista en tiempo real derivado del **mercado actual + pujas en vivo** sobre la base de transacciones (3,6M+).
- **Identificación/specs del vehículo**: **integración con DAT** (Deutsche Automobil Treuhand) — el equipamiento y specs se autorrellenan por **VIN** vía import DAT en EVA.
- **Inspección**: estructurada vía EVA (daños, ruedas/frenos, test drive, documentos de servicio, fotos guiadas) o evaluador móvil de AUTO1, o inspección de tercero subida por el cliente.
- **Frescura**: marketplace y Price Indicator en **tiempo real / 24-7**; Price Index **mensual**.

---

## 5. Entrega
- **Marketplace web B2B cerrado**: `www.auto1.com` (solo dealers verificados; login). [V]
- **Apps móviles** iOS/Android: una para **comprar** (AUTO1.com app) y otra para **vender/evaluar** (**AUTO1 EVA app**). [V]
- **API REST**: integración del sistema del cliente con AUTO1.com (carga de coches, conexión de sistemas); "Request API description". **Sin documentación pública** del esquema. [V existencia; GAP esquema]
- **Remarketing Dashboard / Live Reporting Tools**: panel web de monitorización (views/bids en tiempo real) + descarga de reportings. [V]
- **AUTO1 Group Price Index**: página web dedicada (`auto1-group.com/index/`) + **press releases mensuales** (con cifras) + blog; descargable. **Sin API/feed público** del índice verificado. [V web/press; GAP feed]
- **Subir inspecciones existentes** (intake de inspección de terceros). [V]
- **Logística como servicio** (transporte/export gestionados por AUTO1 como único partner contractual). [V]
- **wirkaufendeinauto.de**: web + **350+ sucursales / 725+ puntos** (canal físico de sourcing a particulares). [V]
- **No verificado**: entrega vía Excel/CSV bulk, feed de datos licenciado, o integración DMS de terceros (no anunciado como producto). [NV/GAP]

---

## 6. Precio
- **Marketplace B2B = SIN suscripción, SIN cuota mensual de membresía, SIN compra mínima.** Literal del sell page: "There is no subscription. There are only fees for services like transport that are booked additionally." [V]
- **Modelo de ingreso real** = **margen transaccional**: AUTO1 compra el coche y lo revende al comprador (es el único partner contractual; gana en el spread) + **fees por servicios adicionales** (principalmente **transporte/logística**). [V]
- **AUTO1 Group Price Index = gratuito** (público, web + press). [V]
- **Price Indicator / EVA = gratuitos** para el dealer registrado (la app EVA se descarga gratis; el valor está en transaccionar). [V]
- **API**: precio no público (vía "request API description" / comercial). [GAP]
- **Importe del margen / take rate exacto = GAP** (no desglosado públicamente por coche; inferible de cuentas: gross profit/unit).

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. AUTO1 separa nítidamente **(a) inteligencia de mercado agregada** (página de índice, fuera de la ficha), **(b) valor por coche** (Price Indicator dentro del flujo de evaluación), y **(c) estado de mercado por coche** (ficha de subasta / dashboard de pujas). Mapeo superficie → dato:

### Página AUTO1 Group Price Index (auto1-group.com/index) [V]
- **Índice agregado de mercado**: valor en puntos (base 100 = ene-2015) + **MoM% / YTD% / YoY%** + serie temporal desestacionalizada. Es una **publicación de mercado independiente de la ficha de coche** (barómetro), reforzada con press releases mensuales y, en algunas, **encuesta de sentimiento de dealers**.

### Flujo de evaluación EVA — 7 pasos secuenciales (app móvil/desktop) [V]
- Cada dato de inspección tiene **su propio paso/pantalla**: (1) Car details → (2) Test drive → (3) Car photos → (4) Car quality (daños & highlights) → (5) Wheels and brakes → (6) Equipment (DAT) → (7) Service and Documents.
- **Equipamiento** = lista preseleccionada por **import DAT** (no entrada manual desde cero).
- **Price Indicator** = valor de trade-in mostrado **dentro del flujo de venta**, junto al campo de **precio esperado** que el vendedor fija.

### Ficha de coche / listado de subasta (marketplace B2B, tras login) [A — detrás de login]
- Cabecera: **identidad del vehículo** (VIN, marca/modelo, matriculación, km, combustible, cambio).
- Bloque de **inspección/condición** (daños, ruedas/frenos, fotos, documentos de servicio) = "fully documented".
- Bloque de **subasta**: canal, **puja actual / nº pujas**, **precio Instant Purchase**, **cuenta atrás 24h**, ubicación, **coste de transporte** por ruta.

### Live bidding dashboard (comprador) [V]
- Vista única para **pujar por varios coches a la vez**, gestionar trades, activar el **bid agent**, watchlist y alertas. (Patrón "torre de control de compra".)

### Remarketing Dashboard / Live Reporting (vendedor) [V]
- **Tracking en tiempo real por coche**: **nº de visualizaciones** y **nº de pujas**; estado de cada subasta; descarga de reportings. (Patrón "panel de rendimiento de venta".)

### Búsqueda + alertas (comprador) [V]
- Barra de **filtros** sobre el stock + **search requests** guardadas con **notificación instantánea** de coincidencias + **watchlist**.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Precio mayorista derivado de TRANSACCIONES REALES** (no de anuncios ni editorial): el AUTO1 Group Price Index es el **único índice europeo basado en precios de transacción mayorista reales** desde 2015. Es el dato "más verdad" del mercado (lo que de verdad se paga, no lo que se pide).
- [V] **Inteligencia fundida con liquidez**: a diferencia de Indicata/Autovista (analítica pura), AUTO1 **también ejecuta la transacción** — el Price Indicator no es un número aislado, está respaldado por **60.000 dealers pujando en vivo** (real-time bidding) que lo convierten en precio ejecutable.
- [V] **Acceso exclusivo al canal de trade-ins de particulares más grande de Europa** (vía wirkaufendeinauto.de, 725+ puntos): oferta de coches que no está en el mercado mayorista normal.
- [V] **Único partner contractual pan-europeo + logística integrada** (170+ centros, 300+ socios; export y documentación cross-border gestionados): arbitraje geográfico real (comprar barato en un país, vender caro en otro) operativizado.
- [V] **Sin suscripción / sin cuota / sin mínimos**: barrera de entrada cero para el dealer (monetiza en spread + transporte, no en licencias).
- [V] **Integración DAT por VIN** para autorrelleno de specs/equipamiento + **inspección estructurada propia** (EVA 7 módulos) o evaluador móvil a domicilio.
- [V] **Velocidad**: tasación EVA <15 min, Price Indicator ~5 min, subasta cerrada en **24h**, coche individual (no block auction).

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **NO vende un producto de analítica/BI por suscripción** (no hay equivalente a Indicata Pro / Autovista Intelligence / autobizCockpit). Su inteligencia se limita a **(a) índice agregado público** y **(b) valor por coche embebido en el flujo de venta**.
- [V] **NO expone KPIs de gestión de stock**: sin **price-to-market %**, **Market Days Supply**, **days-to-sell/days-to-turn**, **stock turn**, **inventory age**, **demanda/oferta por vehículo**, **fast/slow-moving** como métricas para el dealer (núcleo de Indicata/autobiz/Percayso). Solo da views/bids de SUS subastas.
- [V] **NO ofrece valor residual / forecast (RV%)** como producto: el Price Index es retrospectivo y **explícitamente no predictivo**; sin curvas de depreciación ni RV a 12-60 meses (vs cap hpi Gold Book, Autovista, ALG, Black Book).
- [A] **Sin desglose público del índice por segmento/combustible/país**: aunque el cómputo segmenta por clase/combustible/edad/km, las **press releases no publican** el detalle por segmento (solo el agregado + MoM/YTD/YoY).
- [A] **Sin historial de vehículo / provenance / fraude de km por VIN** tipo Carfax/autoDNA/HPI Check (da inspección de condición presente, no historial certificado de propietarios/siniestros).
- [A] **Sin SMR / despiece / tiempos de mano de obra / precios de pieza** (usa DAT solo para specs/equipamiento, no para reparación).
- [A] **Sin TCO / coste de uso** como producto.
- [A] **Sin valoración por condición Rough/Average/Clean** ni triple valor retail/trade/private expuesto como dato (el "valor" es el precio mayorista de subasta real, un único número ejecutable).
- [V] **Marketplace y fichas detrás de login** (solo dealers verificados): el detalle atómico de la ficha de coche y del esquema de inspección publicado no es accesible públicamente (inferido de EVA + descripciones).
- [V] **Sin documentación técnica pública de la API** (esquema, auth, rate limits, diccionario de campos): existe REST API pero a puerta cerrada ("request API description").
- [V] **Sin feed/Excel del Price Index** ni licenciamiento de datos anunciado (publicación = web + press; no data-as-a-service).
- [A] **Sin tipos de vehículo más allá de turismo VO** (no motos/LCV/industrial anunciados).
- [V] **Sin métricas de salud de batería EV propias** (el "Battery health check (AVILOO)" pertenece a **BCA**, empresa distinta — no confundir).

---

## 10. Fuentes (URLs)
- https://www.auto1-group.com/ — identidad, "leading digital automotive platform", misión, Price Index en News [WebFetch].
- https://www.auto1-group.com/company/ — 3 marcas (wirkaufendeinauto/AUTO1.com/Autohero), 8.600 empleados 2025, €8,2B 2025, 842.200+ coches 2025, 6M+ desde 2012, 170+ centros/300+ socios, CEO Bertermann, Price Index [WebFetch].
- https://www.auto1-group.com/company/auto1/ — AUTO1.com "Europe's leading B2B used-car marketplace", 60.000 partners/30+ países, gestión data-driven, trade-ins/leasing/dañados [WebSearch+Fetch].
- https://www.auto1-group.com/company/wirkaufendeinauto/ — wirkaufendeinauto y hermanas, 725+ puntos/350+ sucursales, valoración gratis online → sucursal [WebSearch].
- https://www.auto1-group.com/index/ — **AUTO1 Group Price Index**: base 100=ene-2015, metodología (descomposición aditiva 12m, outliers [0,5;99,5]), segmentación clase/combustible/edad/km, mensual, ~6M transacciones [WebFetch].
- https://www.auto1-group.com/blog/auto1-group-price-index-the-european-used-car-price-report/ — "first of its kind at European level based on actual wholesale transaction prices since 2015", ~3,6M (histórico), no predictivo [WebFetch].
- https://www.auto1-group.com/press/pressrelease/auto1-group-price-index-april-2026/ — **métricas exactas**: 142,0 pts abr-2026; MoM +1,9%; YTD +4,0%; YoY +0,1%; base ~5,8M transacciones [WebFetch].
- https://www.auto1-group.com/press/pressrelease/auto1-group-price-index-january-2026/ — encuesta de sentimiento de dealers ("half foresee further declines") [WebSearch].
- https://www.auto1-group.com/press/pressrelease/auto1-group-announces-landmark-year-2024-and-record-q4-results/ — FY2024: 689.773 unidades (Merchant 615.335 + Retail 74.438), €6,3B, GP €724,7M, adj EBITDA €109,2M, 6.300 empleados [WebSearch].
- https://www.auto1.com/en/home/buy — **render Playwright**: canales (Customer Auction/24h/Instant Purchase + catálogo), live bidding dashboard, smart bid agent, filtros+alertas+watchlist+search requests, 30.000+/3.000+, logistics-as-a-service, account management, alta con registro mercantil [innerText].
- https://www.auto1.com/en/home/sell — **render Playwright**: 6 servicios (EVA / Mobile Evaluation / API REST / Price Indicator 3,6M / Logistics / Live Reporting Dashboard), partners (dealers/grupos/leasing/rental/OEM/bancos/flotas), "How it works" (4 vías evaluación → subasta 24h views&bids → processing), precio (sin suscripción; fees solo por servicios) [innerText].
- https://www.auto1.com/en/auto1-eva — **render Playwright**: **7 módulos EVA** (Car details[Model/Gear/Fuel] · Test drive · Car photos · Car quality[damages&highlights] · Wheels and brakes[tires/rims/brakes] · Equipment[DAT import] · Service and Documents), import DAT, oferta a 60.000 dealers, subasta 24h; sede AUTO1.com GmbH Bergmannstrasse 72 Berlín [innerText].
- https://www.auto1.com/en/auto1-eva (app store mirror) — campos: VIN, equipment via VIN, wheels, service docs, mileage, damages, guided photos, structured test drive; **Price Indicator "real time prices based on 2 million transactions"** [WebSearch].
- https://play.google.com/store/apps/details?id=com.auto1.inspectionapp — EVA: evaluación <15 min, import DAT, vender a 60.000 dealers [WebSearch].
- https://www.cnbc.com/2021/02/04/softbank-backed-auto1-rallies-45percent-after-ipo-on-frankfurt-exchange.html — **IPO 4-feb-2021** Frankfurt, ticker AG1, ~€1,8B captados, SoftBank-backed, +45% día 1 [WebSearch].
- https://www.auto1-group.com/press/pressrelease/auto1-group-to-be-included-in-the-stoxx-europe-600-index/ — inclusión STOXX Europe 600 (mar-2025) [WebSearch].
- https://www.financecharts.com/stocks/ATOGF/profile — fundación 2012, Bertermann & Koç, Berlín, 5M+ coches, segmentos Merchant/Retail, OTC ATOGF [WebSearch].
- Verificación negativa: `wholesale-intelligence.auto1.com` → **ENOTFOUND** (no es host vivo; es descriptor de categoría) [WebFetch error].
- ⚠ Descartado por contaminación: `auth.bca.co.uk` / BCA España (Constellation Automotive Group) — empresa distinta; su contenido (AVILOO, 14 países) NO se atribuye a AUTO1.

> Verificación: identidad/escala/financieros con ≥2 fuentes (company + press + CNBC + agregadores). Métricas del Price Index [V] de la página de índice + blog + press release abr-2026 (cifras exactas). Flujo EVA y servicios [V] por **render Playwright** (innerText literal) de las SPA oficiales. Precio [V] del sell page. KPIs de gestión de stock / RV / historial = **GAP confirmado** (ausentes). Subdominio "wholesale-intelligence" = inexistente como host (descriptor). Nada inventado; campos no listados explícitamente marcados [A].
