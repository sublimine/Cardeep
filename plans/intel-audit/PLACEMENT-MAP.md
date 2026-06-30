# Mapa de colocación — dónde poner cada dato en cardeep

> Patrón derivado de DÓNDE 109 empresas sitúan cada métrica en su UI. Agrupado por dato (frecuencia).

### specs  ·  (4 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Ficha de vehículo en guías Truck y Powersports (Price Point/API)
- **Molicar (KBB Brasil — Tabela Molicar)**: Ficha de cotação — junto al precio del vehículo
- **Stat.vin (1VIN STAT)**: Seccion VEHICLE DETAILS
- **Edmunds**: Pestañas Features & Specs de la ficha; sirven de capa de apoyo a precio y review

### inputs de valoracion  ·  (4 empresas lo colocan)
- **Kelley Blue Book**: Formulario/ficha de entrada previo a mostrar cualquier valor (todos obligatorios; Condition solo para Trade-In/Private Party)
- **J.D. Power Valuation Services**: Stepper de 4 pasos: (1) Car Basics [Year/Make/Model/Trim] -> (2) Car Details [mileage/condition/options] -> (3) Plan Ahead -> (4) Trade-In Value (resultado)
- **J.D. Power Valuation Services**: VIN (con scan) o Year-Make-Model + Mileage (obligatorio) + Zip (->DMA) + Trim (opcional); el VIN dispara VIN Precision+
- **Mahindra First Choice Wheels (MFCWL)**: Valuador IBB/carandbike: flujo de inputs en pasos

### vehicle history  ·  (4 empresas lo colocan)
- **J.D. Power Valuation Services**: CTA que deriva a AutoCheck (Experian); no es dato propio embebido
- **CLASSIC.COM**: Tab 'History' de la ficha de vehículo: cada listado/venta con precio, fecha, fuente, mileage, location y 'View Source'
- **CarGurus**: Ficha VDP, sección propia de historial con issues marcados
- **carsales (carsales.com.au)**: Botón 'Check vehicle history' en la ficha -> report; en CarFacts dealer se publica via AutoGate (auto/manual) y se imprime/emaila al cliente

### equipamiento  ·  (4 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Sección de equipamiento dentro de la ficha técnica de la versión
- **km77.com**: Sub-pestaña Equipamiento dentro de /datos
- **Standvirtual**: Ad Details — sección 'Equipamento' agrupada por categoría
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: bloque de equipamiento agrupado por categoria

### instant cash offer  ·  (3 empresas lo colocan)
- **Kelley Blue Book**: Flujo propio de 3 pantallas: VIN/matricula -> cuestionario de condicion -> oferta fija con validez 7 dias + dealers participantes
- **AutoGrab**: Valuation Widget embebido (iFrame) en la web del dealer — journey de captación de lead
- **CarGurus**: Flujo Sell My Car / Instant Offer (input matrícula+mileage → oferta <2 min)

### identidad del vehiculo  ·  (3 empresas lo colocan)
- **Datium Insights**: Acompana al valor en la respuesta/ficha de InstantVal
- **Stat.vin (1VIN STAT)**: Cabecera del STAT Report
- **Mahindra First Choice Wheels (MFCWL)**: Informe Autoinspekt: cabecera de identidad (PDF/portal)

### identidad del veh culo  ·  (3 empresas lo colocan)
- **AutoGrab**: Car card (cabecera de la ficha) en Realtime Pricing tras resolver rego/VIN/AGID
- **AutoCheck (by Experian)**: Cabecera del informe (bloque izquierdo)
- **NMVTIS / VehicleHistory.gov**: Cabecera (top header) del informe

### acceso programatico  ·  (2 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: API REST/SOAP + ficheros embebidos en el DMS/sistema del cliente (sin UI propia)
- **Percayso Vehicle Intelligence (formerly Cazana)**: API REST embebida en el DMS/sistema del cliente (sin UI propia)

### dma retail value  ·  (2 empresas lo colocan)
- **J.D. Power Valuation Services**: Panel de valores cuando hay zip introducido (si no, retail regional/nacional)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Cabecera del resultado de lookup en Values Online / MarketValues tras introducir VIN/Zip/Mileage/Trim

### comparacion de vehiculos  ·  (2 empresas lo colocan)
- **J.D. Power Valuation Services**: Side-by-side hasta 3: pricing, MPG, specs, pictures, safety features, warranty coverages
- **Datium Insights**: Vista de comparador: varias curvas RV solapadas para ver cual retiene mejor el valor

### tipo de veh culo  ·  (2 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Landing: tres pestañas/iconos; primer paso del flujo
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Pestañas en la cabecera del widget de estimación (home y /pinggu) — primer selector

### trade-in value  ·  (2 empresas lo colocan)
- **Canadian Black Book**: Portal de consumo 'Value Your Vehicle': pantalla de resultado al final de un funnel de 4 pasos (Y/M/M/Trim -> postal code -> odómetro/colour/opciones -> datos de contacto). Solo trade-in; condición fija en media.
- **Canadian Black Book**: Widget TradeMax embebido en la web del dealer (rebrandeable logo/colores/fuente); salida de lead a CRM vía ADF.

### deal rating badge  ·  (2 empresas lo colocan)
- **iSeeCars**: Tarjeta de anuncio (resultados de busqueda), junto al precio - elemento visual dominante
- **CarGurus**: Tarjeta de anuncio (SRP) junto al precio — elemento visual dominante; ordena resultados, mejores deals arriba

### savings vs market  ·  (2 empresas lo colocan)
- **iSeeCars**: Tarjeta de anuncio, bloque de precio bajo el price
- **AutoUncle**: Next to the price on the car card / detail page ('if available')

### history-based value  ·  (2 empresas lo colocan)
- **CARFAX**: Cabecera/top del Vehicle History Report (abre el informe) y pantalla /value/ como cifra central; tambien value_tracking en app myCARFAX
- **CARFAX Canada**: Appended at the END of the VHR as a value layer hanging off the same VIN

### recall  ·  (2 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Recall Check
- **ClearVin**: Seccion 'Recalls' = item narrativo con contacto fabricante/NHTSA

### estado de robo  ·  (2 empresas lo colocan)
- **ClearVin**: Seccion 'Theft Records' = icono de estado (check verde 'NOT LISTED AS STOLEN') + texto
- **NMVTIS / VehicleHistory.gov**: Sección 'Theft Records' — indicador de estado

### autocheck vehicle history  ·  (2 empresas lo colocan)
- **Manheim**: VDP (sección de historial)
- **OPENLANE**: VDP + Condition Report (integrado y gratuito en US)

### identidad  ·  (2 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: 出品票 — cabecera
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Bloque superior del resultado del decode y primeras columnas del output flat

### price indicator  ·  (2 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Ficha del anuncio de consumidor (VDP), etiqueta semaforo colocada JUNTO AL PRECIO, comparando asking vs valoracion propia; link 'About our price labels'
- **carsales (carsales.com.au)**: Badge automático sobre la ficha/anuncio (search card + detail page), con modal explicativo (10 atributos + exclusiones) accesible desde el badge

### instant offer  ·  (2 empresas lo colocan)
- **Edmunds**: Flujo Sell: placa/VIN -> style/options -> condición -> oferta + redención en CarMax; CTA en appraisal
- **carsales (carsales.com.au)**: Página /instant-offer: form minimo Rego+State arriba, 'How it works' en 3 pasos, cross-sell a Advertise/Free valuation

### distintivo ambiental  ·  (2 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Caja de consulta por matrícula → etiqueta (sede electrónica + miDGT), gratis
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Servicio aparte por matrícula, sin login, en sede.dgt y miDGT

### identificacion + ficha tecnica del vehiculo  ·  (1 empresas lo colocan)
- **Autovista Group**: Entrada por VIN / VRM / NatCode -> devuelve perfil completo del vehiculo (make/model/trim/engine/equipment). VIN API / AutovistaSPEC

### trade & retail value rv% forecast  ·  (1 empresas lo colocan)
- **Autovista Group**: Vista de valoracion por vehiculo; fila por vehiculo en data feed; API devuelve valor por-VIN ajustado a km

### dashboards de valor residual  ·  (1 empresas lo colocan)
- **Autovista Group**: Plataforma Autovista Intelligence, dashboards Tableau organizados por Fuel / Brand / Segment / Country, cada uno con vista Overview + Detailed

### kpis  ·  (1 empresas lo colocan)
- **Autovista Group**: Dashboard de KPIs customizable (RVI) / dashboard 'at a glance' (RVM)

### rankings de modelo y benchmarking competitivo  ·  (1 empresas lo colocan)
- **Autovista Group**: Vistas de model selection / ranking en Residual Value Monitor

### weekly price index  ·  (1 empresas lo colocan)
- **Autovista Group**: Graficos de tendencia en RVI

### tendencias historicas  ·  (1 empresas lo colocan)
- **Autovista Group**: Trend charts en RVM / RVI

### comparacion cross-market like-for-like  ·  (1 empresas lo colocan)
- **Autovista Group**: Tablas comparativas / market-overview en Compare (Eurotax)

### desglose tco  ·  (1 empresas lo colocan)
- **Autovista Group**: App Car Cost Expert, breakdown por componente

### reparacion / despiece y precios de pieza  ·  (1 empresas lo colocan)
- **Autovista Group**: Diagrama grafico interactivo de piezas (click en pieza -> precio) en AutovistaREPAIR; labour 'costed to the minute'

### drivers de rv pre-lanzamiento  ·  (1 empresas lo colocan)
- **Autovista Group**: Reports por fases (Phase 0/1/2) en Car to Market

### metricas ev  ·  (1 empresas lo colocan)
- **Autovista Group**: Dashboards del EV Volumes data center + exports Excel/PDF/CSV + tracker mensual

### reports y forecasts de mercado  ·  (1 empresas lo colocan)
- **Autovista Group**: Portal Autovista24

### days-to-sell / time-to-sale stock duration pricing premium  ·  (1 empresas lo colocan)
- **Autovista Group**: KPIs de stock en paginas de sector Dealers / Remarketing

### total loss value repair-vs-replace  ·  (1 empresas lo colocan)
- **Autovista Group**: Workflow de Insurance (claims/underwriting/pricing) sobre AutovistaVALUATION + REPAIR

### campos obligatorios de valoracion + selector de version  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: AutowertNet - parte superior/formulario de la pantalla de valoracion

### resultado de la valoracion  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: AutowertNet - parte inferior de la pantalla tras 'Guardar y actualizar valoracion'

### usuario creador de cada valoracion  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: AutowertNet - lista 'Valoraciones existentes' (una fila por valoracion)

### datos del cliente + nombre del usuario que imprime  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: AutowertNet - impresion de la valoracion (automatico)

### posicion de su vehiculo en el mercado  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - pantalla 'Resultado de la busqueda', elemento destacado

### lista de vehiculos similares de competidores  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - cuerpo central de resultados

### grado de semejanza  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - codigo de color por fila de resultado

### alternancia ofertas vo vs vehiculos ya vendidos  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - pestanas sobre la lista

### media de dias para la venta  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - metrica agregada destacada en resultados

### diferencia precio oferta vs valor spot  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - vista grafica/grafico comparativo por vehiculo

### dias anunciado por vehiculo + historial de cambios de precio  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - columna por fila (hover muestra cambios y fechas)

### filtro por palabras clave  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - arriba a la izquierda de resultados

### radio de busqueda / nacional + rango de km  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - control de area en resultados

### enlace al anuncio original  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - icono de camara por fila

### tarjeta de oferta competidor  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Market Radar - tarjeta de anuncio rival sobre mapa

### vr por marca/segmento/combustible graficos con codigo de color previsiones 3 anos  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Residual Value Intelligence - dashboards personalizables con pestanas filtrables + comparacion rapida desde home

### ranking de modelos comparacion vs competidores variacion por periodo causas  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Residual Value Monitor - paneles personalizados (flujo de 5 pasos)

### comparacion vr nacional/internacional + grafico forecast subida/bajada  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Compare - vista central pan-europea

### desglose de tco  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Car Cost Expert - dashboard + export Excel/PDF

### 16 drivers de vr + prevision final por variante  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: Car to Market - informe pre-lanzamiento por fases (0/1/2)

### perfil completo del vehiculo con equipamiento de fabrica y opciones  ·  (1 empresas lo colocan)
- **Eurotax (JD Power / Autovista Group)**: VIN API / Eurotax - tras identificacion por VIN o matricula en un solo paso

### vehicle entry  ·  (1 empresas lo colocan)
- **Glass's**: Vehicle lookup screen -> identify & value in seconds (Glass's, MVA)

### trade value + live retail + forecast + depreciation + options adjustment  ·  (1 empresas lo colocan)
- **Glass's**: Valuation screen / vehicle card (auto-saves on identify)

### desirability / fastest sellers / highest volumers / most desirable  ·  (1 empresas lo colocan)
- **Glass's**: Market performance dashboard (3 KPI tiles), separate from the vehicle card

### days-to-sell + regional live retail  ·  (1 empresas lo colocan)
- **Glass's**: Fastest selling cars dashboard (interactive chart, filter by region/age, last 24 months)

### settlement figure + spot price + ad search avg advert price  ·  (1 empresas lo colocan)
- **Glass's**: Radar module inside Market Value Assessor

### total loss  ·  (1 empresas lo colocan)
- **Glass's**: Total Loss indicator on the claim/valuation card (MVA)

### case images / notes / attachments  ·  (1 empresas lo colocan)
- **Glass's**: Case management area, permission-based claims workflow (MVA)

### saved valuations  ·  (1 empresas lo colocan)
- **Glass's**: Status dashboard (MVA)

### price index + 16 age-mileage scenarios  ·  (1 empresas lo colocan)
- **Glass's**: Customizable KPI dashboard + index chart (RVI)

### cross-country weighted averages  ·  (1 empresas lo colocan)
- **Glass's**: Cross-country comparator with downloadable graphs/datasets (RVI)

### rv performance ranking + competitive benchmark  ·  (1 empresas lo colocan)
- **Glass's**: KPI dashboards + ranking tables across 17 markets (RVM)

### rv forecast / benchmark / cross-border opportunities  ·  (1 empresas lo colocan)
- **Glass's**: Three modes: Optimize / Benchmark / Analyse (Compare)

### part price  ·  (1 empresas lo colocan)
- **Glass's**: Graphical click-to-price interface (click a body part -> its price), with PDF report builder (Repair Estimate)

### reports  ·  (1 empresas lo colocan)
- **Glass's**: PDF report builder (my account > PDF reports) in MVA and Repair Estimate

### marktentwicklung  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Dashboard/home del portal Schwacke

### einkaufspreis / verkaufspreis / schwacke tagespreis  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Pantalla de valoracion (resultado principal)

### geschaetzte wertminderung  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Valoracion: indicador junto al precio (momento optimo de venta)

### bewertungs-details  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Ventana modal sobre la valoracion

### equipamiento por vin  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: VIN-Ausstattungsanzeige tras VIN-Abfrage (lista serie/opcional)

### restwert / curva de valor residual  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Herramienta de seguimiento de restwert: de resumen estrategico hasta vehiculo individual (niveles de agregacion)

### standtage / marge / kpis / wettbewerbspreise  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Modulo de gestion de stock (tabla de inventario: dias en stock + precios competencia)

### automatische neubewertung  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Inventario: revaloracion periodica automatica

### reparaturkostenkalkulation  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: AutovistaREPAIR: grafico interactivo del vehiculo (clic en pieza -> precio)

### wiederbeschaffungswert / nutzungsausfall / schadenkalkulation  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: SchadenManager: flujo de caso (identificacion -> calculo -> freigabe)

### rv trade/retail + benchmark + ranking  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Dashboard Residual Value Monitor (ranking de modelos + benchmark vs competidores + tendencia 4 años)

### price index + tendencias del usado  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Dashboard Residual Value Intelligence (indice + filtros marca/segmento/combustible)

### tco breakdown + inputs de usuario  ·  (1 empresas lo colocan)
- **Schwacke (Schwacke GmbH / JD Power Autovista)**: Car Cost Expert: desglose TCO + filtros hasta trim + campos editables (labour/interes/consumo) + export Excel/PDF

### retail / clean / average / below  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Tarjeta de resultado de valoracion en Valuation Anywhere tras introducir VRM + km: bloque de 4 valores como salida principal

### option values  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Dentro de la misma tarjeta de valoracion, itemizado por extra (name, costNew, value) + total sumado al valor base

### future / residual values  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Dashboard de forecast (Gold Book iQ): tabla/curva por mes hasta 60m + panel de evidencia/rationale editorial + alertas de movimiento de RV

### movimiento de valor live  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Panel de market movement (Black Book Live): que derivative se movio, cuanto y por que (comment editorial)

### yoy% deflacion/inflacion  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Indice de mercado segmentado por age/sector/fuel (Gold Book iQ)

### provenance  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Informe de historial (HPI Check) con indicadores tipo semaforo (pass/warning/alert) por check; grafico top-down del coche para danos/write-off

### mileage discrepancy  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Flag dentro del informe + timeline de lecturas NMR

### specs / nvd  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Ficha tecnica por derivative (Spec Check): bloques engine, CO2/WLTP, dimensiones, equipment estandar vs opcional, imagenes 360

### tco / running costs  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Calculadora de whole-life cost (TotalCost/TCO Lite): depreciacion + fuel + tax + SMR + finance = coste total

### market value  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Informe PDF de settlement para el asegurado (Market Value Manager) con valor evidenciado

### parc / market research  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Informe geografico por region/county/town/postcode (Vehicle Census): distribucion, demanda de parts, drive-time a retail

### posicion competitiva  ·  (1 empresas lo colocan)
- **cap hpi (CAP + HPI, a Solera company)**: Anomaly report (Insight): tu oferta vs competidores + resumen de amenazas

### marca/modelo/versi n/antig edad  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Pantalla de búsqueda de la app GANVAM Valores VO (selección táctil paso a paso, embudo marca→modelo→versión→antigüedad)

### valor de mercado vo  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Pantalla de resultado de la app tras seleccionar criterios (1 valor de salida)

### inventario propio + valor  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Módulo de gestión de stock dentro de la app

### periodo/marca/tipo/modelo/a o  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Filtros superiores de la tabla web de consulta de boletines

### modelo / tipo / valor  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Columnas de la tabla de resultados web

### vin + datos t cnicos + equipamiento  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Ficha de vehículo del GANVAM-DAT tras IdentifyVIN

### valor de venta y valor de compra  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Bloque de valoración de la ficha GANVAM-DAT (par retail/trade)

### valor residual % / depreciaci n  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Salida del Índice GANVAM-DAT colgada de la ficha del vehículo

### stock completo valorado  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Vista de lista/lote tras carga masiva de inventario (uso fiscal/contable)

### matriculaciones / transferencias / bajas  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Dashboard interactivo VN/VO + boletines descargables, segmentado por provincia/marca/municipio/CP

### precio medio / retenci n % / rotaci n  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Notas de prensa e informes de tendencias (plano agregado de mercado, separado del per-vehículo)

### informes/facturas/operaciones/monedero virtual  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Área privada Mi GANVAM (panel de cuenta del asociado)

### productos de pago  ·  (1 empresas lo colocan)
- **GANVAM (Asociación Nacional de Vendedores y Reparadores de Vehículos) / GANVAM-DAT**: Tienda online (catálogo + checkout)

### fila de 5 tarjetas-valor  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Cabecera del dashboard de valoración pro, anclada al ciclo de vida VO: Reprise → Annonce → Vente → Gestion. Patrón maestro a copiar en la cabecera de la ficha de coche de cardeep.

### identificaci n del veh culo  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Bloque de entrada/identificación de la ficha; las versiones probables (candidates) se listan ordenadas por popularidad con 'suggested' arriba.

### cote argus / valor principal  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Tarjeta destacada 1 (fase Reprise); en web pública largus.fr/cote es el resultado central como 'Cote Argus Personnalisée'.

### marge de man uvre  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Adjunta a la tarjeta Valeur Argus Annonces®, como límite de precio recomendado a no superar.

### confidence-index + confidence-intervals + dispersion + influence  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Panel de detalle al desplegar un valor: cada precio se muestra con su intervalo de confianza, dispersión y palancas que lo mueven — nunca cifra desnuda.

### sonar anuncios/transacciones comparables anonimizados de veh culos similares  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Pantalla paramétrable accesible desde cada tarjeta de valor, filtrable por zona de chalandise o toda Francia.

### d lai argus rotation  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Tarjeta-valor 5 (fase Gestion), junto al coste de detención previsto.

### matriz de valeur r siduelle  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Panel Prevar: grid con la VR € en cada celda (matrice globale = nube; personnalisée = pares elegidos) + índice de decote con histórico + comparación de hasta 3 vehículos lado a lado.

### ajuste regional/geogr fico  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Toggle 'ajustar a mi zona' sobre el valor; mapa de dispersión geográfica cuando has-map=true.

### specs t cnicas + prix du neuf + equipamiento serie/opci n  ·  (1 empresas lo colocan)
- **L'argus (Cote Argus®)**: Bloque 'caractéristiques' de la ficha (un clic), alimenta también la identificación y el cálculo de valor.

### identificacion + specs  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Cabecera de identificacion: caja de entrada VIN/matricula que autorrellena un panel de identidad del vehiculo en segundos, antes de cualquier valoracion

### haendlereinkaufswert + haendlerverkaufswert  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Panel de resultado de valoracion: los dos valores como cifras protagonistas enfrentadas, con la Handelsspanne (margen) derivandolos; vista simplificada para cliente final

### equipamiento de serie/opcional y su impacto en valor  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Bloque desplegable bajo el panel de valor, con la depreciacion de cada opcional (Zeitwert/Restwert)

### comparacion de mercado  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Pestana/panel webScan separado: listings vivos de mobile.de/AutoScout24 con distribucion grafica de precio

### restwertprognose  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Curva de depreciacion/ciclo de vida con selectores de plazo x km; valor a fin de contrato; dashboard para leasing/banca

### dano + coste  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Pantalla de siniestro (FastTrackAI/myClaim): foto con overlay y marcadores POI; desglose de coste; flag de Totalschaden; residual

### kpis de mercado  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Dashboard de observacion mensual / Barometer: series temporales + tiles KPI segmentados por combustible

### indice de alquiler  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Selector de clase -> tabla regional min/max/media + cifra Nutzungsausfall

### documento formal de valoracion/siniestro  ·  (1 empresas lo colocan)
- **DAT (Deutsche Automobil Treuhand GmbH)**: Salida PDF (Bewertungsprotokoll) para uso legal/pericial/tribunal; dos vistas por dato: simplificada (cliente) y protocolo completo (profesional)

### wholesale/retail/trade-in/finance advance/residual values  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Bloque 'Values' de la ficha en Black Book Cherry (móvil/desktop) y tabla de Price Point tras lookup por VIN/descripción/drill-down

### history adjusted valuation + impacto evento-a-evento  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Bloque 'History Adjusted Valuations' bajo el valor en Cherry: desglose inline de cuánto suma/resta cada evento al precio total

### ajustes  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Sección de ajustes en Price Point que recalcula el valor base; selección de condición XCL/Clean/Average/Rough

### retail comparables days to turn days supply average price average mileage  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Panel 'Retail Market Insights' en Cherry (vehículos comparables en dealers cercanos)

### inventario de subasta + run lists  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Pantalla 'Inventory Discovery' en Cherry (recomendaciones EVM-powered)

### residual proyectado 1-120m + ltv en el tiempo + loss/delinquency  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Vista tabular por VIN del portfolio en ValuEngine (plataforma colateral self-service, con jobs/scheduling batch)

### kpis de mercado retail  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Dashboard de segmentos de Pulse con filtros vehículo/dealer/geografía

### depreciation trends segment/model analysis bvi loss forecasting  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Workbooks interactivos Tableau de Visual Analytics (incl. Vehicle Segment Model Explorer)

### trim verificado + opciones + add/deducts + fully-adjusted wholesale + history adjustment  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Panel overlay del Asset Verification Tool (extensión de navegador) inyectado sobre la listing del dealer / LOS en origination

### residual baseline vs adverse vs severe  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Columnas comparativas en módulo Scenario-Based Residuals a nivel segment/model/trim

### sensibilidad de residual a msrp/incentives/rental penetration  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Entorno interactivo 'War Game' de Residual Sensitivity Analysis (sliders -> recálculo)

### uvi / bvi / depreciation report  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Cifra-titular del índice + descarga PDF/newsletter (publicación de mercado, no ficha)

### todos los campos por endpoint  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Respuesta JSON/XML en Web API + consola 'What If' del Developer Portal para probar inputs

### ev range score / battery health adjustment  ·  (1 empresas lo colocan)
- **Black Book (National Auto Research — Hearst)**: Integrado en la valoración del EV (tool Recurrent + valor Black Book), Recurrent Reports adjuntos al inventario del dealer

### valor  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Pagina de valor con etiqueta de tipo, fecha, ZIP, descripcion del vehiculo, definicion en rollover/tooltip y disclaimer

### fair market range + fair purchase price  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Presentado como rango low-high con el punto medio destacado

### price advisor zona blanca/verde/roja + badge good/great price  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Sobre cada listing del dealer (SRP) y en la ficha de detalle del vehiculo (VDP)

### resale value % + grafico de depreciacion + rating de retencion  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: En TODOS los reportes de precio de coche NUEVO; enlace 'Learn More' a comparacion 3/4/5 anos vs segmento e industria

### 5-year cost to own  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Bloque expandible en la ficha de modelo nuevo, bajo encabezado 'Kelley Blue Book 5-Year Cost to Own'

### expert/consumer ratings  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Bloque Ratings & Reviews en ficha de modelo, con enlace 'See more at KBB.com'

### premios  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Badges/sellos de confianza en la ficha de modelo

### auction value / lending value  ·  (1 empresas lo colocan)
- **Kelley Blue Book**: Solo B2B/interno; PROHIBIDO mostrarlos en cualquier aplicacion publica

### cada tipo de valor  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Panel de valores B2B con fila por valor: Base value -> (+/-) Mileage Adjustment -> (+/-) Options/Content Adjustment -> Adjusted value

### trade-in por condicion  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Tres columnas Rough / Average / Clean en el panel; en consumo aparece en el paso 4

### opciones de fabrica  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Bloque de equipment/accessories detectados, cada uno con su Content Adjustment

### curva de forecast 1-36 meses + depreciacion  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Bloque adyacente al valor actual (pricing/marketing/portfolio)

### consumer verified ratings  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Ficha de modelo de consumo, junto a specs/MPG/safety/warranty, imagenes/videos e incentivos por zip

### awards / alg residual value award  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Sellos/badges en la ficha de modelo como prueba de confianza

### indice de mercado mayorista  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Fuera de la ficha: reporte mensual Excel/CSV con grafico de indice industria (desde 1995) y segmento (14+) y forecast a 2 anos

### cars for sale  ·  (1 empresas lo colocan)
- **J.D. Power Valuation Services**: Listings con descripcion a nivel VIN (build data del fabricante) + filtros body style/make/trim/fuel/location + dealer quote

### forecast curve + depreciation insights  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Bloque/gráfico bajo el valor actual en la ficha de valoración (curva de futuro)

### value grid  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Tabla de valores por tipo y condición (Rough/Average/Clean) en la ficha de valoración

### residual % / por plazo y millas  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Residual Value Viewer — pantalla de estructuración de lease deal del dealer (ajuste options/mileage/finance terms)

### tendencias + escenarios de mercado  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Residual Value Workbench — visualizador interactivo de tendencias + explorador de escenarios + export de sets de vehículos

### escenarios macro  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Stormwatch Portfolio Analysis — panel de cartera con selector de escenario (Growth/Inflation/Stagnation/Mild/Severe Recession)

### mark-to-market vin-level / loss reserves  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Portfolio Analysis — dashboard/report de cartera (lenders, captives, investment community, securitización)

### historical accuracy  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Reporte Historical Accuracy dedicado (back-test público)

### residuales de flota  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Fleet Tool — interfaz online de flota

### % msrp a 3/4 a os  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Award badge/seal colocado por OEM/dealer en materiales de marketing del vehículo (prueba de retención de valor)

### m tricas trimestrales  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: ALG Quarterly Reports (PDF/report de suscripción)

### vin decode / trim / specs + tasaci n guardada  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Input del lookup + Appraisal Snapshot (MarketValues App)

### mapping a vin/chrome/nada id  ·  (1 empresas lo colocan)
- **ALG (Automotive Lease Guide) — JD Power ALG**: Backend — Mapping Services (capa de integración, no UI de usuario final)

### vehicle selection  ·  (1 empresas lo colocan)
- **RedBook**: Vehicle Browse screen: Make->Family->Year lists or dropdown, 'Browse by Category', 'Advanced Search', 'Search for Similar Vehicles', or question-tree (VehicleBrowse); alternatively VIN/Rego lookup -> RedBook Code

### variant list with prices  ·  (1 empresas lo colocan)
- **RedBook**: Variant table after Make/Family/Year: one row per variant with RB Code + Wholesale/Retail at Average & Good conditions + New Price (RRP)

### base prices  ·  (1 empresas lo colocan)
- **RedBook**: Main Vehicle Workscreen: 'Select Price to View' dropdown (condition+type combo, e.g. 'Good Retail') -> Vehicle Price + Option Price + Total as primary output

### standard vs optional equipment  ·  (1 empresas lo colocan)
- **RedBook**: Main Vehicle Workscreen two panels: Standard Equipment (left) and Optional/Factory Options (right, each option priced) + 'Add Custom Option' (name+value)

### kilometre & condition adjustment  ·  (1 empresas lo colocan)
- **RedBook**: AutoCalc tab: Kilometres + Condition selectors -> table Based On x (Vehicle Price, Option Price, Adjustment %, Adjusted Price) per price type

### technical specs  ·  (1 empresas lo colocan)
- **RedBook**: Vehicle Specifications tab: collapsible categories (Identification, Drive Train, Engine, Fuel, Specifications/Performance) as label/value pairs

### photos  ·  (1 empresas lo colocan)
- **RedBook**: Photos tab: gallery of interior/exterior compositions

### model history  ·  (1 empresas lo colocan)
- **RedBook**: Model History tab

### residual forecast  ·  (1 empresas lo colocan)
- **RedBook**: Price Ahead tab: New Price (RRP) on top + matrix Age (1-5 years) x km bands (10K..150K), each cell showing residual % + $ value

### past value  ·  (1 empresas lo colocan)
- **RedBook**: Price History: 'Select Point in Time' dropdown (monthly, up to 3 years back) re-renders the workscreen at that date's value

### depreciation curve  ·  (1 empresas lo colocan)
- **RedBook**: Trend Graph tab: line chart of price over time by selected price type + condition, RRP overlay

### side-by-side comparison  ·  (1 empresas lo colocan)
- **RedBook**: Add to Compare Basket -> compare specs/prices of multiple vehicles

### confidence score / market comparison / pre-accident valuation  ·  (1 empresas lo colocan)
- **RedBook**: RedBook LIVE report: confidence score, price history graph, market comparison (live vs delisted), factory-options/accessories breakdown, estimated repair costs, pre-accident valuation, damage-assessment notes/reference

### days-to-sell / days supply / stock volume / price movements  ·  (1 empresas lo colocan)
- **RedBook**: LiveMarket dashboard

### consumer valuation  ·  (1 empresas lo colocan)
- **RedBook**: RedBook Valuation Report PDF (AU$33): trade-in / private / dealer-retail price ranges adjusted by kilometres + condition

### programmatic access  ·  (1 empresas lo colocan)
- **RedBook**: REST API + secure FTP + flat file embedded in client DMS/systems (no own UI)

### m s de refer ncia  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Dropdown de mes/año (vigente por defecto + históricos), antes de buscar

### modo de b squeda pesquisa por marca vs pesquisa por c digo fipe  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Dos pestañas/radio sobre el formulario de consulta

### marca - modelo - ano modelo  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Dropdowns en cascada con buscador interno (modo por Marca)

### c digo fipe + ano modelo  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Input directo (modo por Código Fipe) + botón 'Pesquisar'

### pre o m dio  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Tarjeta 'Resultado da Pesquisa': elemento HÉROE destacado (grande), centro del bloque

### descripci n del veh culo  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Cabecera de la tarjeta de resultado, sobre el precio

### c digo fipe  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Dentro de la tarjeta de resultado, junto a la descripción

### m s de refer ncia + data da consulta  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Tarjeta de resultado, como metadatos de fecha/contexto

### c digo de autentica o  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Tarjeta de resultado: sello de validez/auditoría de la consulta

### disclaimer  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Pie de la tarjeta de resultado

### no presentes trade/retail/private split gr fico de variaci n panel de specs comparador alertas  ·  (1 empresas lo colocan)
- **FIPE (Tabela Fipe Veículos)**: Ausentes a propósito: patrón minimalista de 'ancla única' (un valor + metadatos de confianza)

### wholesale + retail + trade-in por vin  ·  (1 empresas lo colocan)
- **Canadian Black Book**: App de dealer Cherry: tras escanear VIN, los tres valores aparecen agrupados en la ficha del vehículo.

### days-to-turn market days supply average listing price  ·  (1 empresas lo colocan)
- **Canadian Black Book**: App Cherry: bloque 'Retail Market Insights' bajo los valores, + listado de comparables cercanos.

### daily vehicle volume average listing mileage days on market  ·  (1 empresas lo colocan)
- **Canadian Black Book**: Pulse (visual analytics): KPIs apilados por segmento (filtrable por vehículo/dealer/geografía); vista de mercado CA o portfolio propio.

### residual hist rico/actual/proyectado a nivel trim  ·  (1 empresas lo colocan)
- **Canadian Black Book**: ValuEngine: tabla batch por VIN con columnas de loss forecasting y flags de delinquency/risk (vista de cartera/collateral).

### used vehicle retention index  ·  (1 empresas lo colocan)
- **Canadian Black Book**: Página de índice dedicada: valor en puntos + variación MoM/YoY + lectura narrativa mensual (barómetro de mercado).

### % msrp retenido / forecast de retenci n  ·  (1 empresas lo colocan)
- **Canadian Black Book**: Sellos/badges por categoría (Best Retained / Best Residual Value Awards) como prueba de autoridad.

### curva de depreciaci n / escenario residual  ·  (1 empresas lo colocan)
- **Canadian Black Book**: Residual Sensitivity Analysis: controles what-if para ajustar MSRP / incentivos / rental penetration y ver el efecto.

### trim + add/deducts  ·  (1 empresas lo colocan)
- **Canadian Black Book**: Capa de Enhanced Vehicle Matching: resuelve 17-dígitos VIN -> trim único y aplica add/deducts automáticamente antes de mostrar el valor (no es pantalla, es paso previo).

### valores b2c / network / c2c + b2b + reprise + 10 datos de mercado  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizMarket — bloque de resultado de valoración tras entrada por matrícula

### posicionamiento de precio vs competidores  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizMarket — vista de nube/scatter de precios (price cloud)

### n mero de veh culos a la venta + distribuci n de concesionarios  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizMarket — visualización de distribución de mercado (interfaz tablet)

### cart la cote + make/model/energ a/km/a o/precio + vendedor pro/particular + enlace al anuncio  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizAdsScan — fila/tarjeta de cada anuncio en la pantalla de resultados de sourcing

### 15 filtros + filtro geogr fico + filtro por diferencial de margen + b squedas guardadas + alertas email  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizAdsScan — barra de filtros superior y panel lateral

### tipo/severidad/parte de da o marcados sobre la foto + coste de reparaci n  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: Carcheck/Noa — informe de tasación (daño anotado en la imagen)

### alerta de discrepancia de reacondicionamiento  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: Carcheck — dentro del propio expediente, en la página de pricing

### perfil mec nico + perfil de carrocer a + recon + recomendaci n/precio final  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: Carcheck — pantallas secuenciales del flujo de tasación

### 20+ criterios de atractividad de precio/marketing + alertas de calidad de anuncio + stocks de competidores de la regi n  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizMyStock — dashboard resumen de una sola página

### kpis stock volumes / ventas / turns / calidad de anuncio  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizCockpit — dashboard jerárquico (global -> país -> grupo de distribución -> punto de venta)

### precio vs competidores por combinaciones edad/km  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizPricingPower — dashboard Tableau 100% personalizable (24/7)

### 30+ kpis de demanda vo / oferta vo / precios  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizBarometer — dashboard de señales de mercado (3 bloques)

### valoraci n en 22 mercados + impuestos locales + fiscalidad transfronteriza + log stica + cross-border potential score  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizCrossborder — salida por cada vehículo de la lista subida

### identificaci n del veh culo + input de estado + estimaci n de reprise + formulario de lead  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobiziFrame / autobizTradeIn — módulo embebido (branded) en la web del concesionario

### oferta de reprise instant nea + ubicaci n del cliente + recon declarado  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizClic2Buy — flujo QR físico -> SMS -> autoinspección; interfaz de leads del dealer

### formato de venta + reserva + tracking de pujas en tiempo real + contraoferta inteligente  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizTrade — interfaz de subasta B2B (publicación desde Carcheck/dashboard)

### estimaci n gratis en 2 minutos - oferta firme  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: vendre.autobiz.fr (B2C) — home con motor autobizMarket®, marca EasyReprise

### dataset de comprador make/model/rotaci n/precio vs valor de mercado + veh culos vendidos 12m + tax id  ·  (1 empresas lo colocan)
- **autobiz (autobiz Group)**: autobizTargeting — herramienta de decisión con export a CRM

### retail/trade value + valores por canal  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Valuation card de Companion tras introducir VRM (+ km): bloque de valores como salida principal

### days to sell + profit corridor indicator  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Indicadores en la misma valuation card, como ayudas de decision instantanea (margen + velocidad)

### market demand / price positioning  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Panel de market overview dentro de la card: comparacion vs whole retail market

### identical/comparable vehicles on the market today  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Lista de comparables en venta hoy, junto a la valoracion

### forecast rv  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Vista de forecast (curva/tabla); horizonte 10 anios solo via API

### vehicle history timeline  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Pantalla de timeline de fabricacion a presente

### provenance / dano / modificaciones  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Dentro del timeline + seccion de provenance check (dano inferido de fotos de anuncios)

### stock pricing / turnover / repricing  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Dashboard add-on Stockview (competencia + vehiculo local)

### benchmark regional de precio/demanda  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Portal Stockcompare (franchise vs independent)

### insurance point-of-quote  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Campos pre-rellenados en el formulario de cotizacion

### total loss / settlement  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Vista de claim (Claims Companion) con timeline de historial

### fraude / risk flags  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Flags en point-of-quote y al modificar el valor sugerido

### bulk valuation results  ·  (1 empresas lo colocan)
- **Percayso Vehicle Intelligence (formerly Cazana)**: Multi: subida Excel/CSV -> tabla de resultados en portal

### identificaci n + ficha t cnica + equipamiento + pvp  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Cabecera de entrada por matrícula/VIN → panel de identidad del vehículo autorrellenado al instante (fastEquipments); precede a toda valoración o cálculo [inferido del flujo]

### valor de compra + valor de venta ganvam-dat  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Panel de resultado de valoración: dos cifras protagonistas (compra/venta) tras identificar (fastVO/fastValuate) [inferido del flujo]

### equipamiento de serie/opcional + adas  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Bloque desplegable de equipamiento bajo la identificación; base del ajuste de valor [inferido del flujo]

### valor de mercado por vin en lote  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Grid de stock con valoración masiva por filas (Valoración de Stock + IdentifyVIN); carga masiva → columnas compra/venta [inferido del flujo]

### retenci n de valor a 3 a os por motorizaci n + precio medio  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Dashboard/artículo trimestral del Índice GANVAM-DAT: tiles por motorización (HEV/gasolina/diésel/PHEV/BEV) + series por tramo de antigüedad [verificado en art_indiceganvam]

### precio medio y volumen por tramo de antig edad  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Informe del Índice GANVAM-DAT: tablas por tramo 0-1/2-5/6-10/11-15/15-20 años [verificado]

### da o + piezas/operaciones/costes/presupuesto  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Pantalla de siniestro FastTrackAI: carga de fotos → IA marca daños → desglose piezas/operaciones/coste → presupuesto detallado (flujo de 3 pasos) [verificado]

### estado del siniestro + trazabilidad  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Timeline colaborativo de myClaim: estado en tiempo real visible para todos los actores, fase a fase [verificado]

### km real + valor residual recalculado  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Vista de activo conectado (SilverDAT Connect): telemetría → RV dinámico para renting/flota [verificado en art_renting]

### documento/informe formal  ·  (1 empresas lo colocan)
- **DAT Ibérica (DAT Automóvil Ibérica SLU)**: Informe de valoración customizable (formato configurable) [verificado en fastvo]

### matr cula + vin + identificadores del siniestro  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Cabecera del informe de peritación — banda superior azul 'DATOS VALORACIÓN' (patrón Cardeep: ficha-cabecera con matrícula+VIN+IDs al tope)

### actores del siniestro  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Bloque 'DATOS GENERALES' bajo la cabecera

### specs/equipamiento del veh culo + tipo de pintura + valor venal + fecha matriculaci n  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Sección 'EQUIPAMIENTO DEL VEHÍCULO' (panel de características; el valor venal/mercado se muestra destacado junto a la ficha)

### recambios  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Tabla 'PIEZAS/RECAMBIOS' con fila por pieza y total

### operaciones de mano de obra  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Tabla 'MANO DE OBRA' con tarifa €/hora declarada arriba

### pintura  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Bloque separado 'PINTURA' con resumen propio

### descuentos/recargos  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Matriz 'CÓDIGOS OPCIONALES'

### desglose econ mico  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Caja 'TOTALES' al pie del informe, con sello de origen y texto legal pericial

### valor de mercado del veh culo  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: AudaValue/VALUEpilot: 'corredor de valor' (rango min-máx) con las ofertas de mercado subyacentes como evidencia, NO un número único

### valor de mercado a m ltiples granularidades  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Typical Market Value Report: valores estatal/regional/nacional apilados en la Sección 2

### comparables + ajuste por estado  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Autosource (app GoTime): lista de vehículos comparables + recálculo del valor tras fotos (daño previo, km, extras)

### valor del veh culo da ado - acci n de venta  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: AUTOonline: entrada por matrícula -> valor 'al céntimo' -> subasta 48h -> puja ganadora -> logística+DGT+pago

### anal tica de mercado de reparaci n  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Dashboard Solera Analytics: vistas por comunidad autónoma, marca, tipo de vehículo y provincia/código postal, con benchmark propio vs mercado

### da o f sico del veh culo  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Qapter: gráfico 3D 360° con el daño localizado por IA sobre la foto, junto a la estimación línea a línea

### triaje del siniestro  ·  (1 empresas lo colocan)
- **Audatex España (Solera)**: Intelligent Triage / Guided Image Capture: clasificación total-vs-reparable a partir de fotos guiadas en el FNOL

### lista de presupuestos  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Home Page (tabla, una fila por estimate; acciones Edit/Copy/Delete/Report; buscador+filtros+orden por columna)

### identificacion de vehiculo + vrn look-up / vin query / vin scanner  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Vehicle Identification Screen (Vehicle Information con iconos de busqueda a la derecha)

### equipamiento de fabrica/opcional  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Equipment Screen (bloques que el usuario confirma/edita)

### tarifas sistema de pintura parts info excess taxes estimate attributes vehicle damages epa  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Estimate Data (bloques editables; estrella=Favourites; predefinidos en Work Environment/My Profile)

### seleccion de pieza y tareas + market value / colour code / reg.date  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Operations Selection Screen (Functional Group via grafico dinamico con joystick; Actions/Operations List lateral con Ref/Price/Quantity)

### total breakdown + lineas de operacion editables  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Results Screen (panel oscuro a la derecha = Total Breakdown; cuerpo central = lineas con Code/Description/Quantity/Price/Discount I/D; boton Reports->PDF)

### configuracion heredable  ·  (1 empresas lo colocan)
- **GT Motive**: GT Estimate - Work Environment / My Profile (pestañas de parametros predefinidos)

### valoracion de no-reparable + asignacion de salvamento  ·  (1 empresas lo colocan)
- **GT Motive**: GT Global - flujo de Total Loss (despliegue automatico al partner de salvage)

### facturacion por tipo de caso  ·  (1 empresas lo colocan)
- **GT Motive**: GT Global - Electronic invoicing

### kpis de siniestro insights y tendencias  ·  (1 empresas lo colocan)
- **GT Motive**: GT Global - MI dashboard (panel 'simple e intuitivo' + descarga de datos)

### reglas de negocio / auto-aprobacion / flag de incidencias  ·  (1 empresas lo colocan)
- **GT Motive**: GT Global - Business rules (se aplican antes del envio de la autorizacion)

### emisiones co2 por reparacion/pieza ranking segmentacion marca/modelo/perito/taller  ·  (1 empresas lo colocan)
- **GT Motive**: Servicio CO2 - Baseline Report (lote) + Follow-Up Reports mensuales (Eco Repair Score)

### verificacion/supersesion de lista de piezas  ·  (1 empresas lo colocan)
- **GT Motive**: GT QCheck - webservice API (input/output, antes de la compra de piezas)

### dano por ia - presupuesto  ·  (1 empresas lo colocan)
- **GT Motive**: GT Fusion - capa de transformacion (foto/imagen -> deteccion IA de partner -> base GT Motive -> presupuesto automatico)

### base vehicle value - condition adjustment - adjusted vehicle value - total  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Report Summary Page (MVR portada): bloque-resumen titular arriba con desglose; Table of Contents a la derecha; Side Bar lateral con glosario/definiciones inline de cada termino

### vin year make model trim body style/type engine transmission curb weight location  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Seccion Vehicle Details: cabecera de identidad del vehiculo (patron de header de ficha)

### equipamiento standard vs additional  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Vehicle Equipment Page: lista separada de serie vs extra con iconos indicadores

### autocheck / nicb / nhtsa + vinguard + recalls  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Vehicle History Summary arriba + seccion VINguard detallada y NHTSA Recall mas abajo: historial como seccion dedicada, separado del valor

### condition ratings por componente + value impact + inspection notes  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Vehicle Condition section: tabla con impacto en $ de cada rating y Total Condition Adjustments al pie

### comparables  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Comparable Vehicles section: hasta 3 por pagina con option config vs loss vehicle; patron 'asi llegue a tu valor: coches reales del mercado ajustados'; Additional Comparables en formato resumen

### notas de valoracion / trazabilidad  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Valuation Notes: notas del appraiser + sistema junto al valor (auditoria)

### captura de input  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: App movil guiada Quick Valuation ANTES del informe: separa captura del informe; blur detection asegura calidad

### predicciones tempranas  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: CCC First Look: inyectadas en el workflow del adjuster tras FNOL, no en pantalla aparte

### sales tax + state/local fees  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: Aplicados via Fee Calculator y sumados al Total/settlement, configurables por carrier y estado

### estimate line-level  ·  (1 empresas lo colocan)
- **CCC Intelligent Solutions**: App CCC ONE / cccone.com (flujo del taller), separado del MVR pero conectado por el IX Cloud

### cabecera de siniestro + bloque de identificaci n vin- decode- accuracy- history- audavin  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Secciones Administrative Data + VINSOURCE Analysis (arriba del informe)

### base price + ajustes l nea-a-l nea - market driven value - deductible - net adjusted market value  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Panel-dinero 'Valuation Detail' (3 columnas: Typical Vehicle | Your Vehicle | Adjustment) — primera pantalla de valor

### equipamiento por categor a + packages + trim levels  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Sección Vehicle Description (rejilla)

### estado por sub-categor a con tier y texto  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Sección Vehicle Condition + Typical Condition Statement (rúbrica)

### comparables reales con precio ajustado vin millas dealer+ciudad+tel fono+fuente+fecha y l nea advertised- negotiation/veh adj cierre con n /suma/media/spread  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Sección Comparable Vehicle Details (tarjetas numeradas) — la 'prueba de mercado'

### valor de libro independiente  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Bloque J.D. Power Value (segundo dictamen / cross-check)

### recalls aplicables  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Sección Recall Bulletins (NHTSA, embebida)

### cat logo opci n-a-opci n con precio packages base retail price msrp editions  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Sección Original Equipment Guide (OEG)

### valor t pico en 3 niveles geogr ficos  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Producto Typical Market Value: sección 'Typical Value' (State / Regional / National)

### metodolog a en prosa + alcance de datos + proprietary/subrogaci n + fuente de tax + patentes  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Secciones Loss Vehicle Valuation + About Your Valuation (pie del informe)

### captura del dato donde est el coche vin por foto - conditioning - resultado de valor  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: App GoTime Autosource (flujo móvil de 3 pasos)

### decisi n total-loss vs reparable previa a la valoraci n  ·  (1 empresas lo colocan)
- **Solera — Audatex AutoSource (Vehicle Market Value / Market-Driven Valuation)**: Intelligent Triage™ (web, post-FNOL)

### input matr cula enriquecimiento  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexPRO — parte superior de la pantalla de tasación/intake

### bloque de valores  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexPRO — bloque de resultados de la tasación

### opciones/equipamiento con flag aumenta valor residual  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexPRO — sección de opciones del vehículo

### informe de da os + fotos + registro de opciones  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexPRO — sección de daños; fotos junto a opciones

### firma digital informe pdf aceptado por hacienda  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexPRO — cierre del informe

### lista overview de tasaciones pujas internas chat destino pago ideal reportes  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: TMC/AMC — consola del sales manager

### tarjeta por veh culo + filtros + push de pujas  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexB2B — app de remarketing (3 vistas: pujas/descubrimiento/pago)

### editor de anuncio distribuci n multi-portal  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexADS — editor + lista de inventario multi-ubicación (Hexon)

### formulario bpm comparador de reg menes resultado m s favorable  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexIMPORT — formulario; output PDF oficial

### campo matr cula embebido cotizaci n inruilwaarde formulario de lead  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: Widget Trade-in en la web del concesionario → ruteado a PRO/DMS

### excel in columnas enriquecidas out autotoekomst por km+contrato  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexFLEET — entrega batch; informe OEM (cuota/SWOT/trim) aparte

### pipeline temporizado tender proposals + audascan  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: AutotelexINSURANCE — backend feed (sin UI)

### formulario de 3 campos dagwaarde + inruilwaarde + total loss  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: dagwaarde.nl — pantalla de consumo + PDF/email

### stock position / turn / value + mutaciones diarias  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: Company Stock Valuation API (entrega a sistemas del cliente, no UI propia)

### agregados de mercado nl  ·  (1 empresas lo colocan)
- **Autotelex B.V.**: Marktupdate mensual — sección news/blog del sitio

### kenteken + huidige kilometerstand  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 1 'Kenteken' — formulario de entrada con botón Verder

### uitvoering/versie  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 2 'Uitvoering' — lista de radios 'N uitvoeringen gevonden' + enlace 'Staat je uitvoering er niet bij?'

### ficha t cnica catalogusprijs optiebedrag nieuwprijs bouwjaar brandstof transmissie kw  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Panel lateral derecho persistente (aparece desde el paso 2 y permanece hasta el resultado)

### rdw oordeel kilometerstand  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Panel lateral derecho, con botón de tooltip 'meer informatie'

### optiebedrag agregado + explicaci n  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 3 'Opties'

### schatting waarde koop + bovag-dealer met garantie / merkdealer met garantie / rijklaarprijs / aankoop bij particulier  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 4 resultado — Bloque 1 'Deze auto kopen?' (CTA 'Tips kopen occasion')

### schatting waarde verkoop + inruilen bij autobedrijf / verkoop door particulier / veilingprijs  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 4 resultado — Bloque 2 'Deze auto verkopen?' (CTA 'Tips auto verkopen')

### vervangingswaarde i.v.m. total loss  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Paso 4 resultado — Bloque 3 'Vervangingswaarde'

### aviso dit betreft een import auto + fecha de importaci n  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Cabecera de la pantalla de resultado (condicional)

### disclaimer richtprijzen sin inspecci n incl. btw & bpm  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Nota a pie (asterisco) bajo los bloques de valor

### acciones printen / terug / nieuwe berekening maken  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Pie de la pantalla de resultado

### cross-sell bereken de autokosten y gegarandeerde prijs  ·  (1 empresas lo colocan)
- **ANWB Koerslijst (Autowaarde berekenen)**: Panel lateral derecho y bloque inferior del resultado

### eurotax blu + giallo  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Bloque de valores en la pantalla de resultado de valoracion (ADM/Online/WebApp), lado a lado, tras identificar el vehiculo por targa o marca-modello-allestimento

### correzione km  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Campo/control que recalcula el valor en vivo dentro de la pantalla de valoracion

### perizia personalizada  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Panel de personalizacion del valore di permuta; salida en perizia PDF imprimible con IVA

### valutazione retrodatata + valori storici  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Selector temporal (mes/ano) en ADM/Online + serie historica

### specs tecnicas + foto + listino + accessori + confronto 3  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Ficha del nuovo en Listini del nuovo

### ipt/incentivi/sconti/permuta/rottamazione  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Flujo del Preventivatore (configurador) que termina en preventivo PDF/poster/email

### svalutazione marca/segmento + top 5 + variazione mom/yoy  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Seccion publica Statistiche por vertical, con dropdown SELEZIONA LA MARCA y bloques de ranking/tendencia

### streetprice  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Panel del dealer por allestimento, con propios vs competidores y filtro geografico

### historial 360  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Report Motornet: informe de pagina unica con 12 secciones en orden, generado por targa

### identificacion oficial  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Resultado de Ricerca per targa

### configuracion exacta de fabrica  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Resultado single-click de Ricerca per VIN (2016+)

### vincoli/gravami  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Semaforo verde/giallo/rosso en Check Fermo Amministrativo (input targa+CF/P.IVA)

### configuratore del nuovo  ·  (1 empresas lo colocan)
- **Motornet (Sanguinetti Editore S.p.A — licenciatario exclusivo Eurotax para Italia)**: Widget Plug-in embebido en webs de terceros (testate/agenzie/software house)

### identificacion resuelta + annomeseimmatricolazione  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Cabecera de la ficha de vehiculo en Infocar Web tras busqueda por targa o VIN; selector de versiones si hay ambiguedad

### 400 datos tecnicos agrupados  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Pestana 'Dati tecnici' de la ficha; datos estimados marcados con sufijo 'Stimato'

### equipamiento serie vs optional paquetes reglas de incompatibilidad y equipamiento cualificante  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Pestana 'Equipaggiamenti' de la ficha; resaltado del equipamiento que afecta al valor

### quotazione di vendita y quotazione di ritiro lado a lado + correttivochilometrico aplicado + edizionequotazione  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Bloque Quotazione lateral/inferior de la ficha, tras introducir targa + km reales; boton a Quotazione certificata (PDF)

### valoreinstantweb + giornirotazione/rotazione  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: KPI superior de la pantalla InstantWeb / Valutazione Web

### por anuncio comparable prezzomercatoperc differenzaprezzo giorni in vendita numero cambi prezzo venditore ubicacion enlace  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Lista de anuncios comparables en InstantWeb (una fila por competidor)

### geolocalizacion de anuncios para varianza de precio por zona  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Mapa dentro de la pantalla InstantWeb / Valutazione Web

### matriz de escenarios de valor hard/medium/soft por canal y por portal  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Bloque 'Valutazioni' multi-fuente de InstantWeb

### curva de depreciacion vendita/ritiro en absoluto y % listino/pac por horizonte 6/12/24/36/48/60 meses condicionada a km  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Tabla/curva de Infocar Preview; categoria de retencion de valor (1 de 6)

### tendencia de valores previsivos de flota + impacto economico  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Vista 'Basket' agregada de Infocar Preview; comparacion con ediciones historicas

### pricing del concesionario  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Modulo de calculo de compra/venta sobre el vehiculo en Stock/Giacenze

### kpis por vehiculo en stock giorni in vendita estado comercial coherencia con demanda  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Panel Stock control del concesionario

### lineas de ricambio + manoopera - totalericambi + totalemanoopera + total preventivo  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Preventivatore Infocar Repair, tras seleccion grafica del dano sobre el SVG de la carroceria

### quotazione storica a fecha de siniestro + listino/optional  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Insurance Pro, tras input de targa, para liquidacion del siniestro

### historial de vehiculo / siniestros / odometro vincoli e gravami salud bateria bev  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Iconos/botones de integracion externa dentro de la ficha de Infocar Web

### anuncio generado con descripcion ia y fotos con watermark  ·  (1 empresas lo colocan)
- **Quattroruote Professional / Infocar (Editoriale Domus)**: Multipubblicatore/Dispatcher: una interfaz que despacha a 8+ portales con codificacion especifica de cada uno

### valor unico de coche  ·  (1 empresas lo colocan)
- **Datium Insights**: Resultado instantaneo tras introducir rego/VIN: tarjeta de valor unico en AUD (portal web o navegador movil); o campo DatiumInstantVal en el JSON de la API para integracion

### parametros de valoracion  ·  (1 empresas lo colocan)
- **Datium Insights**: Inputs del formulario / cuerpo del request; devueltos en eco junto al valor para trazabilidad

### curva de valor residual  ·  (1 empresas lo colocan)
- **Datium Insights**: Grafico central del dashboard: curva RV vs edad superpuesta a datos de reventa reales

### forecast rv por edad x km  ·  (1 empresas lo colocan)
- **Datium Insights**: Calculadora integrada dentro del dashboard de AutoPredict

### ajustes de rv  ·  (1 empresas lo colocan)
- **Datium Insights**: Controles de ajuste en el dashboard, junto a la curva

### auditoria de cambios y busquedas  ·  (1 empresas lo colocan)
- **Datium Insights**: Log/registro de auditoria (pantalla de compliance) en AutoPredict

### comparables de camion  ·  (1 empresas lo colocan)
- **Datium Insights**: Lista/tabla de resultados en PriceMyTruck con filtros para acotar

### factores de valor  ·  (1 empresas lo colocan)
- **Datium Insights**: Panel educativo en la home de PricesPeoplePay (8 iconos: odometro, edad, tipo, condicion, ubicacion, temporada, oferta, comprador/vendedor)

### estimacion de valor de mercado  ·  (1 empresas lo colocan)
- **Datium Insights**: Pantalla de resultado al final del flujo multi-paso 'Find your car' (bandas exactas no capturadas)

### prueba social  ·  (1 empresas lo colocan)
- **Datium Insights**: Contador en vivo en el hero de PPP: 'Trusted valuations: 22,578,926 since 2018'

### los 5 formatos de precio  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Barra de TABS superior de la calculadora: un mismo vehiculo, cinco lentes de valor conmutables. El usuario elige el tipo de pregunta de precio antes que nada

### buy/sell  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Toggle al inicio del flujo: el mismo precio se reencuadra segun la parte (retail vs trade-in)

### inputs del vehiculo  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Cascada de inputs dependientes (drill-down) antes del resultado

### fair market price + desglose por condicion  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Pantalla de resultado: cifra-titular grande del Fair Market Price + precios paralelos por grado de condicion, mostrando el rango por estado de inmediato

### current market valuation  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Cabecera del informe premium PDF (pagina 1)

### new vehicle price now and then  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium, tras la valuacion: contexto de depreciacion

### next 3-year depreciation  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium: bloque de proyeccion forward

### what others have paid  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium: bloque de prueba social/comparables

### total cost of ownership 5 anos  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium: bloque de coste de propiedad, en el medio del documento

### recent transactions + recent listings con avg/high/low price avg owners avg km  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium: tablas de evidencia de mercado

### expert reviews + user ratings & reviews + compare similar vehicles  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Informe premium: cierre cualitativo al final del documento

### kpis de uso  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Enterprise Dashboard B2B: telemetria de consumo arriba; el panel es de uso+gestion de integracion, NO ficha de coche

### acciones enterprise  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Secciones del panel Enterprise

### precio obv  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Overlay INYECTADO en la web del partner (p.ej. listing de Ford Assured) - el dato aparece donde el usuario ya navega, no en pantalla aparte

### insured declared value  ·  (1 empresas lo colocan)
- **Orange Book Value (OBV)**: Vertical Insurance: el valor de mercado reencuadrado como suma asegurada, no como precio de venta

### seleccion de vehiculo  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Pantalla de entrada de tasacion (movil con camara, web, iframe); tras seleccionar pide mileage, colores y opciones vacs[]

### cuestionario de condicion  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Stepper secuencial de preguntas; cada respuesta ajusta el valor en vivo (priceAdjustment emitido del iframe al padre)

### escaneo obd-ii  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Inyectado automaticamente en el bloque de condicion, sin tecleo manual (app movil / dispositivo en campo)

### valor garantizado o rango + caducidad  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Ficha de oferta junto al vehiculo (imagen, Y/M/M/Style/VIN/mileage); en consumer con aviso de 3 dias habiles sujeto a inspeccion

### deducciones/adiciones itemizadas  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Debajo del valor, explicando el numero (consumer-facing y compartible)

### gross profit retail vs wholesale daily adjusted value projected days on market daily depreciation inventory intelligence score  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Panel del IMS por VIN, para decidir retener (retail) o liquidar (wholesale/DealerClub)

### valor / bid guidance + encaje con inventario y mercado local  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: VIN-Dow: ventana flotante (overlay) sobre ACV Auctions / Manheim Simulcast mientras el dealer puja; boton para empujar al workflow

### instant cash offer al particular  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Widget embebido en la VDP / lead form de la web del dealer y en cars.com/sell; mismo dato auto-populado en todos los canales (web, chat Gubagoo/Darwin, retail)

### descripcion ia + photo overlays + sindicacion multi-marketplace  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Modulo MERCHANDISE del IMS, desde el mismo registro del VIN adquirido

### capture rate trades perdidos gross profit por equipo  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Reporting ROI fuera de la ficha: Profit Funnel report y Trade Capture report

### payoff / equity  ·  (1 empresas lo colocan)
- **Accu-Trade (AccuTrade)**: Bloque de equity en el flujo de oferta (offer/{id}/payoff + equity/lenders)

### inputs  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Lista vertical del widget de estimación; picker marca→serie→款型 emergente

### matriz de 3 precios  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Página de resultado de valoración, cuerpo principal [layout inferido del esquema API por gate anti-bot]

### valor por condici n  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Resultado de valoración, modulando cada uno de los 3 precios

### curva de precios futuros  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Resultado de valoración, como gráfico forward/depreciación

### contador de valoraciones acumuladas + sellos / / 100%  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Cabecera de /pinggu (banda de confianza bajo el H1 '估得准 才靠得住')

### ranking semanal por serie  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Bloque inferior de /pinggu — '全国一周车系估值排行榜' Top-20

### % + badge + delta vs valoraci n + tag  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Tarjeta de anuncio en 全网淘车 (/buycar) — análogo a Good/Great Price de KBB

### informe  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Ficha de detalle / informe 一键查 con flag 事故车 destacado; bloques cronológicos con km por evento

### del coche propio  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: App 大众版, sección 车主服务 (seguimiento en vivo)

### score de riesgo + / + pesos por regla + alertas de cartera  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Panel 伽马 embebido en el sistema de信审 del banco (no UI de consumo)

### herramientas pro  ·  (1 empresas lo colocan)
- **Che300 (车300 / 三百云 Sanbaiyun) — Nanjing Sanbaiyun Information Technology Co., Ltd.**: Dashboard de mosaico en la app 车300专业版

### entrada / busqueda  ·  (1 empresas lo colocan)
- **Hagerty**: Flujo Year -> Make -> Model -> Body style/variante; ruta alternativa VIN/numero de serie ('classic car VIN lookup'); browse por Make & Model. Gate: anonimo = 3 valores actuales, socio HDC = todo

### bloque de valor  ·  (1 empresas lo colocan)
- **Hagerty**: Los 4 valores de condicion lado a lado (#1 Concours / #2 Excellent / #3 Good / #4 Fair) como precios actuales, con tooltip/rollover de la definicion de cada condicion. Equivalente al bloque de valores de KBB pero indexado por condicion de coleccion

### tendencia de valor  ·  (1 empresas lo colocan)
- **Hagerty**: Grafico de value trend (sube/baja) con historico HPG desde 2006; historico completo bloqueado tras membership

### ventas comparables  ·  (1 empresas lo colocan)
- **Hagerty**: Seccion comparable sales: grafico + lista de ventas recientes (subasta + privadas) del mismo modelo; cada fila con precio, fecha, fuente/subasta, condicion, notas de equipamiento, fotos y market commentary

### specs / historia del modelo  ·  (1 empresas lo colocan)
- **Hagerty**: Ficha tecnica + model history (desde VIN decode) con notas de equipamiento/opciones que justifican el valor

### tie-in de seguro  ·  (1 empresas lo colocan)
- **Hagerty**: CTA 'Insure this value' -> Guaranteed Value junto al valor; en portal de agente, valor + condition guidelines + valuation history se usan para fijar el valor asegurado y cotizar

### watchlist  ·  (1 empresas lo colocan)
- **Hagerty**: Accion de seguir vehiculos para vigilar su valor en el tiempo

### hagerty market rating  ·  (1 empresas lo colocan)
- **Hagerty**: Zona 'Market Trends' (separada de la ficha del coche): gauge/medidor 0-100 + comentario mensual + bandas deflacionario/plano/peak/burbuja

### hagerty price guide indexes + hagerty hundred  ·  (1 empresas lo colocan)
- **Hagerty**: Zona 'Market Trends': graficos tipo bolsa (linea temporal, % cambio trimestral) de los 11 indices y el Hundred

### predicciones de subasta  ·  (1 empresas lo colocan)
- **Hagerty**: Seccion editorial/data-driven de Hagerty Media: totales previstos por evento de subasta (ej. $211M Arizona) y scoring de predicciones

### vehicle identification input  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: App/online: single license-plate field, OR flow manufacturer->model->year->trim; model code is the internal key

### base / average price  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: First line of the valuation result; in print, the price column next to the model name and its code

### weighted online price  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Online result (מחיר משוקלל), distinct from the printed book price

### ownership-type deduction  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Valuation result, 2nd line after base ('reduction for leasing -21% = 8,610 ₪') with running subtotal

### mileage deduction  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Next line over the subtotal ('for km -3% = 960 ₪')

### owners/hands deduction  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Next line over the subtotal ('for number of hands -7% = 5,500 ₪')

### final price  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Last highlighted line ('מחיר סופי / final price')

### auxiliary coefficient tables  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Annexed tables in the printed monthly magazine and inside the B2B portal

### safety rating score  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Dedicated feature section/page ('ציון רמת בטיחות רכב'), per model, new+used

### monthly depreciation  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Implicit in the monthly edition update; explained in FAQ

### historical price  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Archive — order the price list of month X (for claims/litigation)

### model-code equivalence  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: Public model-code conversion tool on the portal

### full coefficients & professional calc  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: B2B agents portal (login) for insurers/appraisers/dealers

### worked examples & community q&a  ·  (1 empresas lo colocan)
- **Levi Itzhak Price List (מחירון לוי יצחק) — Levi Itzhak Group**: 'דוגמאות לחישוב' and 'שאלות נפוצות' pages

### c digo molicar  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Pantalla de consulta — input único 'Faça a busca rápida' → Enviar (atajo experto)

### categoria  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Busca detalhada, paso 1 — radios con icono

### estado / uf  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Busca detalhada, paso 2 — dropdown ANTES del precio (la región se elige antes de ver el valor)

### marca ano fab ano modelo modelo vers o  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Busca detalhada, paso 3 — dropdowns en cascada → Enviar

### precios multivalor  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Ficha de cotação (frmResultado) — bloque de precios; histórico con fichas separadas por contexto (Comércio/Financiamento, Seguro, Sinistro)

### ajustes km / cor / opcionais  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Ficha de cotação — controles editables que recalculan el valor en vivo

### planos  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: ContratarAssinatura / planos — tarjetas de paquetes; pago boleto/Redecard (ruta hace 302→login)

### periodicidade / tipo de ve culo / regi o  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Página 'Banco de Dados Molicar' — formulario de cotización corporativa con CNPJ

### decoder situa o cadastral / restri es / gravames  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Dossier de garantía inyectado al INICIO de la esteira de financiamento de la IF (decodificación anticipada)

### variaci n por idade/categoria/marca/modelo + el tricos/h bridos  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Informe MVP (PDF mensual, coxautomotive.com.br) — tablas {ago, set, média 2024} × {0km, seminovo, usado}

### home login assinante + cta ver banco de dados  ·  (1 empresas lo colocan)
- **Molicar (KBB Brasil — Tabela Molicar)**: Homepage 'Molicar Digital' — separa superficie consumidor vs corporativo

### c digo fasecolda  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Ancla de identidad en la ficha técnica de la versión + input directo del modo 'Búsqueda por código'

### valor comercial  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Dato principal de la ficha técnica, para el año modelo seleccionado en la cascada Categoría→Estado→Modelo→Marca→Referencia→Tipología

### serie de valor por a o-modelo  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Mini-curva de depreciación devuelta por la API (varios años con su valor y estado nuevo/usado por un mismo código)

### ficha t cnica  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Vista 'Ver la ficha técnica' de cada versión en la lista de resultados

### filtros de afinamiento  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Modo 'Búsqueda avanzada' para reducir las opciones resultantes

### comparaci n de hasta 4 versiones  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Comparador atributo-por-fila tras seleccionar checkboxes en la lista de resultados

### disputa/correcci n de valor  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Centro de Ayuda dentro de la Guía (mesadeayuda.fasecolda.com) con adjunto de soporte documental

### dataset completo  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Descarga mensual en archivos Excel y archivos planos (público) / API REST Inverfas en tiempo real (aseguradoras)

### c digo de homologaci n y placa  ·  (1 empresas lo colocan)
- **Fasecolda — Guía de Valores**: Campos de la respuesta API que enlazan la versión con RUNT y permiten consulta por placa

### historial del vehiculo  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Ficha de vehiculo / CARFAX Vehicle History Report (VHR): bloques verticales Title -> Accident/Damage (diagrama overhead + severidad + airbags + punto de impacto) -> Owners timeline -> Service history cronologico -> Odometer (grafico + check rollback) -> Use -> Open recalls; badge CARFAX 1-Owner/No-Damage

### valor del coche  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Bloque de valoracion integrado EN la ficha/VHR: valor VIN-especifico + lista de ajustes por historial (mileage real, title brand, total loss, service) + comparables side-by-side (mismo year/make/model/trim/options/mileage/location). El valor vive junto al historial

### listados de usado filtrados por historial  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: SRP de CARFAX Used Car Listings: filtros 1-owner / sin daños / con service records; cada VDP lleva VHR + value + comparables

### incentivos + transaction price + unsold inventory + sales  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Dashboard integrado Mobility Pulse 360: una sola vista conectada, filtrable por make/model/MY/fuel/DMA, con monthly-payment view y share-impact; updates weekly + month-end

### volumen de ventas por pais/marca/modelo/fuel  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Mapa mundial interactivo del Global Auto Demand Tracker (Power BI embebido): hover sobre pais -> ventas del ultimo mes; drill a marca/modelo/fuel/body; toggles SA/SAAR/YoY/MoM

### matriculaciones vio demografia loyalty  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Cubos de dato multidimensionales de la plataforma web Polk: dimensiones age/make/model/body/fuel/owner-type/geo->ZIP con mapping, charts y export Excel; el usuario construye la vista (no es ficha)

### pago lease/finance/balloon  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Herramienta de desking/POS Market Scan mDesking (desktop) y mDrive (movil): Scientifically Perfect Payment penny-perfect en el punto de venta

### lender market share / apr / amount financed / ltv / monthly payment  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Dashboards de AutoCreditInsight por selling-dealer & ZIP, con bandas y geografias custom; entrega tambien email subscription / FTP feed

### specs vin  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Servicio headless VINtelligence (API REST / batch / web UI / deployed): VIN o YMM o matricula -> specs; capa de enriquecimiento que alimenta las demas fichas

### behavior prediction score equity mileage warranty  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Customer Deal Sheet de automotiveMastermind: BPS 0-100 + sub-scores (in-market/vehicle/deal); In-Market tab con current mileage/warranty/EV; Deal Score con equity position y trade-in

### atributos oem de seguro  ·  (1 empresas lo colocan)
- **S&P Global Mobility (Mobility Global Inc., NYSE: MBGL — spin-off 1-jul-2026)**: Feed/archivo CARFAX Banking & Insurance Group (carfaxbig.com): Claims Triage File real-time single VIN o batch XML; Total Loss Report/File para underwriting y claims

### heading + photo url/photo links + vdp url  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Cabecera de la ficha de coche (respuesta listing de Inventory Search)

### price msrp price change percent ref price/ref price dt buy now price  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Bloque de precio en la ficha del listing

### dom / dom active / dos active first seen/last seen vehicle status in transit  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Bloque 'salud del anuncio' (tiempo en mercado/sitio) de la ficha

### carfax 1 owner carfax clean title  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Bloque historial/título de la ficha

### objeto dealer + jerarquia mc dealership + lat/long/dist + phone  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Bloque concesionario/ubicacion de la ficha

### loan/lease term apr down payment estimated monthly payment  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Bloque finance/lease de la ficha

### stats + facets  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Respuesta agregada de Inventory Search (posicionamiento del vehiculo en el mercado)

### marketcheck price + msrp  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Cifra central de la pantalla MarketCheck Price (Base)

### comparables / recent comparables + stats por region  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Panel de comparables de MarketCheck Price (Premium)

### decode neovin  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Panel de equipamiento de MarketCheck Price (Premium Plus) y NeoVIN Decoder

### mds + total active cars for ymmt + total cars sold in last 45 days  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Endpoint/indicador dedicado Market Days Supply (oferta vs demanda, nivel city/state/national)

### fair market value + price predictor + price range + margin gap vs hammer + time to prep + retail turnover  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Informe de Auction Stock Analysis (UK), tras subir CSV de VRMs

### filtros make/fuel/price/mileage/dom/fca-status/write-off-cat/vrm + cta financiacion  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Widget Integrated Car Search (UK) embebido en web del cliente, eventos a CRM AutoConvert

### market-wide / dealer-level / mds / competitive / pricing intelligence + targets de adquisicion  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Investor Reports (UK), dashboard/informe de inversor

### total listings total dealers/rooftops average dom average price price-band breakdown dealer-volume distribution top-100 vs resto ev share % top-10 ev models  ·  (1 empresas lo colocan)
- **MarketCheck (MarketCheck Cars Inc)**: Informe mensual UK de market intelligence (PDF/pagina), segmentado ICE vs EV

### valores side-by-side + 4 metricas  ·  (1 empresas lo colocan)
- **vAuto**: Pantalla de Appraisal (tasacion de entrada), junto al vehiculo (VIN/YMM/trim/odometro/equipamiento AutoMatch)

### multi-out + vsquare  ·  (1 empresas lo colocan)
- **vAuto**: Pantalla de Appraisal — paneles de simulacion en vivo

### common problems + vehicle journey  ·  (1 empresas lo colocan)
- **vAuto**: Pantalla de Appraisal — paneles de contexto del VIN

### grado platinum/gold/silver/bronze + profit potential/roi + precio retail recomendado + pricing alignment + live demand  ·  (1 empresas lo colocan)
- **vAuto**: Panel de mercado/decision ProfitTime GPS (ficha por VIN); consola en 3 vistas Strategize/Analyze/Optimize

### 15+ data points + lightbulbs + total cost vs retail target + profit target  ·  (1 empresas lo colocan)
- **vAuto**: Lista de sourcing Stockwave (300+ marketplaces, columnas); Simulcast embebe la puja; VIN-Click flota sobre cualquier web de subasta

### price to market + days supply del nuevo + vin-specific incentives + factory rebates + fast/slow sellers  ·  (1 empresas lo colocan)
- **vAuto**: Ficha de coche nuevo (Conquest), con incentivos aplicados y sindicados al listing

### time-to-line + approval time + line-item approvals + ubicacion gps + filtro por metal profittime  ·  (1 empresas lo colocan)
- **vAuto**: Tablero de recon por etapas (iRecon), con boton 'promocionar aun en recon'

### snaplot 360 + descripcion ia + overlays + carfax smart field + billboards  ·  (1 empresas lo colocan)
- **vAuto**: Registro del vehiculo / VDP (Merchandising); un clic sindica a web + Autotrader + terceros; VDP views en Merchandising Tool

### estado de cada appraisal + kpis por tienda holding wholesale + envio bulk a subasta  ·  (1 empresas lo colocan)
- **vAuto**: Vista agregada Enterprise/multi-rooftop + Wholesale Hub

### market days supply trend days supply/inventory/pricing/sales trends  ·  (1 empresas lo colocan)
- **vAuto**: Reporting fuera de la ficha: Provision Reports + Industry Insights trimestrales + Live Market View quarterly

### 8 kpis agregados de toda la organizacion + ubicaciones bajo-rendimiento + cuota/leakage de red  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Group overview' (nivel grupo/HQ/NSC)

### resumen de los 8 kpis del concesionario + alertas de stock issues  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Dealer dashboard' (nivel concesionario)

### filas vehiculo-a-vehiculo price-to-market % days in stock mds demanda bandera pocas fotos bandera precio sin cambiar fast/slow-moving  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Inventory list'

### por vehiculo live retail price trade/wholesale price-to-market % mds competidores en mercado nivel competencia dias en stock demanda/oferta recomendacion stock vs trade precio nacional/local/cross-border  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Vehicle Details' (ficha de vehiculo)

### conjunto de vehiculos competidores/comparables contra el que se calcula price-to-market y mds  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Benchmark set'

### valoracion trade-in/appraisal del vehiculo entrante + decision stock vs trade  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Pantalla 'Vehicle appraisal' (tasacion/reprise)

### price index + trend mds curvas oferta/demanda comparador marca/modelo/segmento cross-country multi-ano + barra de filtros  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Dashboard Market Tracker (vista unica plug&play)

### vista multi-mercado armonizada curvas rv historico/actual/forecast benchmark rv competitivo panel value drivers/tendencias  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Dashboard RV Tracker (configurable por mercado/marca/seleccion)

### formulario de valoracion trade-in online - resultado de valor - captura de lead  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Widget Lead Generator embebido en web del concesionario

### indice de precios mds indicators oferta/demanda/stock tendencias por combustible por pais  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Informe Market Watch (PDF mensual, descarga con registro)

### curvas rv futuras + valoraciones actuales  ·  (1 empresas lo colocan)
- **INDICATA (Autorola Group)**: Forecast Module / entrega API-CSV-Excel

### valor retail + trade + offer suggestion  ·  (1 empresas lo colocan)
- **AutoGrab**: Car card / panel de valoración de Realtime Pricing ('in seconds')

### banda upper/lower + confidence score  ·  (1 empresas lo colocan)
- **AutoGrab**: Junto al valor (bounds + score); como aguja 'fill' 0-1 en el AutoGauge sobre rango min-max

### comparables de mercado  ·  (1 empresas lo colocan)
- **AutoGrab**: Panel LATERAL de la ficha del lead en la web app ('similar leads on the side of the page')

### gr fico de mercado  ·  (1 empresas lo colocan)
- **AutoGrab**: Market panel de Realtime Pricing (RTP-MarketOverlay-Graph)

### days to sell / retained value% / vol menes / benchmarking  ·  (1 empresas lo colocan)
- **AutoGrab**: Informe AIR (PDF/Excel) por secciones (Volume&Inventory · Pricing&Valuation · Velocity&Performance) y dashboards de Delve

### tendencias y consulta en lenguaje natural  ·  (1 empresas lo colocan)
- **AutoGrab**: Delve (NL query) y AutoMate (chat LLM)

### historial de precio/listings y rollback de km  ·  (1 empresas lo colocan)
- **AutoGrab**: Workflow de sourcing (analytics por vehículo) y sección Odometer History del PDF CarAnalysis

### indicador de precio en un listing  ·  (1 empresas lo colocan)
- **AutoGrab**: Gauge Widget (iFrame) embebido en la página del marketplace (aguja + rango de mercado)

### marketability snapshot  ·  (1 empresas lo colocan)
- **AutoGrab**: Market Insights Snapshot (popup/iFrame) sobre el listing

### pav / total loss valuation  ·  (1 empresas lo colocan)
- **AutoGrab**: Web app PAV (app.autograb.com.au/insurance-claims/<id>) + PDF + webhook claim_report_generated

### recompra de cliente  ·  (1 empresas lo colocan)
- **AutoGrab**: Notificación/sighting (webhook recapture_new) cuando el coche de un cliente reaparece listado

### factory fitted options / specs  ·  (1 empresas lo colocan)
- **AutoGrab**: Dentro del workflow de valoración del sourcing ('factory fitted options during the valuation workflow')

### ev market  ·  (1 empresas lo colocan)
- **AutoGrab**: Live dashboard EV Pulse + reporte 'Australian Used EV Market Report' descargable

### historial ppsr / recalls / stolen / write-off  ·  (1 empresas lo colocan)
- **AutoGrab**: Reporte CarAnalysis PDF (módulos sources) + flags en el certificate object vía API

### factory + aftermarket upgrades itemizados con valor en  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — bloque 'Why Buy' / Complete Package Breakdown en la VDP de valor

### kbb value + comparacion con resto de mercado + highlight por debajo de kbb/media  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — Value Report dentro de la ficha

### original msrp de paquetes oem  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — Value Report / seccion de packages

### oem build data + cpo data  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — ficha de vehiculo (VDP)

### vehicle history + highlights  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — VDP, bloque de historial

### recall identification & remedy  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom VDP + flujo de tasacion (appraisal)

### fotos grandes + carrusel + mapa interactivo  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — cabecera de la VDP (scroll unico)

### qr code / print / share-crm  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Digital Showroom — acciones de la ficha

### ten pricing proof points  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Modulo 'Market Pricing Service' dentro de DealerCenter + Showroom

### vin-level price/offer + minimum wholesale guarantee + margin protection  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Panel de tasacion/compra (Buy/Appraisal), parte superior por VIN

### condicion verificada  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Panel de tasacion (Buy/Source) — bloque de condicion

### predicted retail price 30 dias por vin  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Resultado del panel de tasacion/compra

### condition rating 10-puntos  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: MAX My Trade — stepper de walk-around guiado en iPad (cliente + vendedor)

### fair market price  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: MAX My Trade — market-based appraisal report al final del walk-around

### profitability report  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: MAX My Trade — vista de manager (oculta al cliente)

### recommended price adjustment + retail/wholesale + reasoning + margen dias  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Panel de Price / ACV MAX Recommendations, por unidad

### market days supply / price-to-market / cost-to-market / velocity  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: FirstLook — panel de inventario/stocking

### descripcion ia-seo + fotos retail + coming soon + feed 500+ sitios  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: Modulo de merchandising (MAX Ad / MAX for Website)

### oem window sticker / monroney  ·  (1 empresas lo colocan)
- **MAX Digital (ACV MAX)**: FirstLook — appraisal + eStock Card

### los 4 signals  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Pantalla de Appraisal — fila de señales junto al vehículo, recalculadas en vivo al ajustar la tasación

### value rank / value to market grade + rmv + ctm/ptm+ + predictive ads  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Pantalla de Appraisal (CATALYST) — bloque de valor/decisión, recalculado al mover odómetro/opciones/condición

### surgical / oem-linked comp sets  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Pantalla de Appraisal — comparables expandibles por trim/build/options

### vintel obd-ii  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Pantalla de Appraisal — integración que inyecta condición/estimación de recon

### kpis por funci n + cta al desviarse  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Executive/CATALYST Dashboard — tiles personalizables y reordenables por rol, con drill-in sin salir

### live attribution + ctm/ptm+ investment buckets  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: CATALYST Dashboard — tile Online Performance / buckets de inversión

### pricing + performance + attribution + lifecycle stage por veh culo alerts on-page status tags recon retail  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: New & Used Inventory page (command center) — una fila/ficha por VIN a nivel tienda o grupo

### sales velocity supply dynamics allocation efficiency merchandising por mmt color/engine por zip leads+vdp views por mmt dealer search para trades  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: New Car (Heads-Up) Dashboard — vista agregada de vehículo nuevo con drill-down

### oferta + carfax/autocheck + supply&demand + comparables vendidos + price history + cost-to-dealer  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: VMR (Vehicle Market Report) — reporte cara al cliente, imprimible/compartible (móvil incluido) vía flujo ACE

### oferta inmediata de venta particular  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: Widget embebido en la web del dealer / sell-to site; lead ruteado a la consola VBC

### leads inbound/outbound/third-party + auction + trade network  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: VBC (Vehicle Buying Center) — consola de adquisición de los buying agents

### recon estimado vs real variance por appraiser/advisor/source/store open ro alerts poached data  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: ReconIQ — vista de varianza VIN-level y outcomes del service drive

### inventory age mds vdp views/day leads/day presupuesto auto-priorizado  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: BOOST — consola de publicidad digital (atribución Orbee)

### mds/demanda regional/pricing shifts/seasonal + recomendaci n de canal + stocking gaps  ·  (1 empresas lo colocan)
- **VINCUE (DealerCue Automotive Corp.)**: PLAN — Intelligent Buying Plan + scoreboards vivos

### remaining lifespan  ·  (1 empresas lo colocan)
- **iSeeCars**: Tarjeta de anuncio (bloque salud/calidad) + filtro sidebar + opcion de sort 'Most Remaining Lifespan'

### dealer score  ·  (1 empresas lo colocan)
- **iSeeCars**: Tarjeta de anuncio + filtro sidebar

### days listed / days on market  ·  (1 empresas lo colocan)
- **iSeeCars**: Tarjeta de anuncio ('Listed 34 days ago')

### iseecars price rating + amount below market price  ·  (1 empresas lo colocan)
- **iSeeCars**: Sidebar de filtros, al mismo nivel jerarquico que precio/km (inteligencia como criterio de filtrado)

### specs completas  ·  (1 empresas lo colocan)
- **iSeeCars**: Detalle del anuncio (VDP/expandible)

### average market price + price range  ·  (1 empresas lo colocan)
- **iSeeCars**: Price My Car - cifra central

### suggested listing price  ·  (1 empresas lo colocan)
- **iSeeCars**: Price My Car - panel de recomendacion dual por urgencia, con % de similares mas caros + demanda

### comparables scatter + monthly history + depreciation curve  ·  (1 empresas lo colocan)
- **iSeeCars**: Price My Car - grafico con linea de market price + tablas inferiores

### secciones ivin  ·  (1 empresas lo colocan)
- **iSeeCars**: Informe iVIN por VIN - secciones secuenciales; local market report por ZIP + CARFAX solo en Pro

### metricas de estudio  ·  (1 empresas lo colocan)
- **iSeeCars**: Paginas de estudios/rankings - tabla Rank / Model / [metrica] / Compared to Average (multiplicador)

### original msrp + factory options + build sheet  ·  (1 empresas lo colocan)
- **iSeeCars**: Herramientas Window Sticker / Build Sheet lookup por VIN

### matriculaciones por canal  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: EU Geo / EU Country / Deutschland Dashboard (IRIS VIEWS Tableau), filtrable por marca/modelo/fuel/segmento

### segmentaci n de m xima  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Deutschland Dashboard

### potencial/performance regional + discount indicator  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Deutschland Geo Dashboard (400 distritos / 5-digit postcode)

### co2 target gap multas estimadas pooling credits  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Road 2 Zero Dashboard (WLTP/NEDC, por canal/OEM group)

### previsi n de matriculaciones a 5 a os por canal/fuel  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: EU Forecasting Dashboard (valores trimestre/mes, exportable)

### lealtad de marca conquest & losses  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Private Loyalty Dashboard (mensual, benchmark 1 competidor)

### planificaci n de red dealer locations catchment fleet score  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: GEO Explorer Dashboard + IRIS NET (cartográfico street-level, update diario)

### parque circulante edad holding period owner type  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: dashboards Parc/UIO (anual) en IRIS VIEWS / IBM Cognos Viewer

### calendario de lanzamientos/facelifts/fin de venta  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Vehicle Lifecycle Calendar (IRIS VIEWS online mensual o Excel offline bimensual)

### direcciones + composici n de flota + decision makers por empresa  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: FleetBase (portal/CRM DE, API) + International Company Database (ficheros texto/Excel)

### fiscalidad comparada por pa s  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Car Taxation Guide (PDF 68 pp, 11 países)

### consulta libre en lenguaje natural sobre matriculaci n  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Ask Dataforce (chat IA -> texto/tabla/gráfico, export Excel/CSV)

### reporting jer rquico  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: capa Reporting (Tableau online / PPT-PDF-XLS-HTML offline / API)

### estudios tem ticos  ·  (1 empresas lo colocan)
- **Dataforce (Dataforce Verlagsgesellschaft für Business Informationen mbH)**: Dataforce Studies (PDF; EU Vehicle Market Insights Report 2026)

### volume / market share / percent change  ·  (1 empresas lo colocan)
- **Urban Science**: MarketView - panel/overview de mercado tipo cubo, filtrable, con benchmark al lado y mapa macro->ZIP; toggle de modulo market/brand/dealer

### dealership / competitor / ev charging / poi locations + network opportunity  ·  (1 empresas lo colocan)
- **Urban Science**: NetworkPlanner - mapa interactivo con pins, overlays de KPI, pan/zoom/query y automated summaries por nivel geografico en panel lateral (el site-selection)

### lead source / salesperson / model / defections / same-brand defections / 90 days to sale / inventory mix  ·  (1 empresas lo colocan)
- **Urban Science**: TrafficView - dashboard de dealer con breakdown del customer journey contacto->venta, defecciones resaltadas

### defection event  ·  (1 empresas lo colocan)
- **Urban Science**: SalesAlert - notificacion push/API event-driven sobre el CRM (no es panel), con detalle make/model/trim/ZIP/dealer ganador

### service retention / parts / bays / recall / service-to-sales  ·  (1 empresas lo colocan)
- **Urban Science**: ServiceView - dashboard de aftersales en Tableau con information firewalls, benchmark vs composite

### dealer financial kpi + what-if  ·  (1 empresas lo colocan)
- **Urban Science**: FinancialView - dashboard financiero geografico con panel de what-if scenario y business planning online (pantalla aparte de ventas)

### dma actual vs expected sales / growth brands / market share trend  ·  (1 empresas lo colocan)
- **Urban Science**: MarketGrowth - dashboard de expansion/adquisicion para grupos de dealers (daily/monthly/quarterly)

### autohook attribution + offer config  ·  (1 empresas lo colocan)
- **Urban Science**: AutoHook - dashboard de campaign reporting real-time + UI de configuracion de oferta (targeting/triggers/incentivo)

### salesmatch kpis  ·  (1 empresas lo colocan)
- **Urban Science**: Embebidos DENTRO de la herramienta de reporting existente del cliente (DSP/social), no en portal propio - el dato se entrega donde el usuario ya mira

### in-market audiences / suppression audiences  ·  (1 empresas lo colocan)
- **Urban Science**: Activados en el DSP/plataforma social del anunciante via LiveRamp (RampID) / The Trade Desk (UID2) - dato como segmento portable, Urban Science no muestra la audiencia, la entrega

### forecast de ventas/produccion a 13 anos  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Panel de mercado / forecast dashboard: series temporales de volumen + cuota con drill-down por dimension (market overview macro)

### scorecard tematico puntuado por 200m senales  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Sector Scorecard: heatmap/ranking comparador con leaders vs challengers en el value chain

### actividad de compania news deals financials innovations patents hiring  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Pagina de perfil de compania (entity profile hiperconectado)

### ciclo de vida de modelo con sop/eop plataforma planta program  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Timeline de modelo / generacion (lifecycle chart)

### parc + aftermarket por componente/family/channel/region  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Panel de parque/aftermarket (market sizing del stock vivo y recambio)

### specs y planes de producto de 4000+ vehiculos futuros/actuales  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Hoja de producto / pipeline por modelo (Future Vehicle Intelligence)

### noticias + disruptor roundup mensual + innovaciones + vc deals  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Feed editorial / seccion de alertas de mercado (just-auto)

### top 10 temas del sector  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Theme Map: navegacion de issues estrategicos

### footprint de fabricacion plantas product portfolio oem customers cuota de proveedor  ·  (1 empresas lo colocan)
- **GlobalData Automotive**: Mapa de supply-chain (Factory Finder + Component Market Share)

### price rating  ·  (1 empresas lo colocan)
- **AutoUncle**: Badge on EVERY car card in search results and on the car detail page (consumer); also overlaid on the listing in Facebook Marketplace; and as the embeddable Price Rating Widget on the dealer's own website

### market price + live similar-cars comparables  ·  (1 empresas lo colocan)
- **AutoUncle**: Car detail page / valuation result: market price plus 'similar cars currently for sale'

### price tracking  ·  (1 empresas lo colocan)
- **AutoUncle**: Saved car / ValuateCar tool — tracks how the market price evolves over time

### specs + consumption/environment panel  ·  (1 empresas lo colocan)
- **AutoUncle**: Detail-page panel ('Verbrauch und Umwelt': per-cycle consumption, CO2, EU norm, EV range)

### trade-in valuation  ·  (1 empresas lo colocan)
- **AutoUncle**: Dedicated trade-in/permuta module embedded on the dealer website (input plate/details -> market value of own car)

### offer carousel  ·  (1 empresas lo colocan)
- **AutoUncle**: Below the main vehicle listing on the dealer's detail page

### price-drop alert / search alert  ·  (1 empresas lo colocan)
- **AutoUncle**: Push/email notification to the buyer (app) and to the lead

### leads & conversion  ·  (1 empresas lo colocan)
- **AutoUncle**: Dealer LeadBox/dashboard + push to CRM (Dealer Desk / Auto-CRM / CATCH)

### api valuation bundle  ·  (1 empresas lo colocan)
- **AutoUncle**: REST API response embedded in the client's own system (marketplace listing, OEM pricing, CRM record, DMS alert, bank/insurance flow)

### market insights  ·  (1 empresas lo colocan)
- **AutoUncle**: Enterprise reports + dashboards + monthly account follow-up meetings

### stock analysis / performance  ·  (1 empresas lo colocan)
- **AutoUncle**: AutoUncle Traffic management reports (GA4, weekly/monthly email)

### matriculaciones cuota de mercado ventas  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> Cuadros de Mando (tablas dinamicas OLAP) y modulo cartografico (capa sobre mapa por codigo postal/zona)

### invasiones territoriales cobertura capilaridad de red  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> modulo cartografico (mapa de Regiones/Zonas/Concesionarios con territorio contractual de la marca)

### segmentacion de producto / gama  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> Gestor de Segmentacion de Producto (maestro + simulado)

### territorios / red comercial  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> Gestor de Red Comercial (maestro + simulado)

### eficacia de red  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> Evaluador de eficacia de red

### rutas isocronas puntos de interes  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: SIMMIX -> modulo cartografico / Analisis Avanzados

### potencial de ventas vs real cuota ajustada desviaciones  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Estudio 'Potenciales y Objetivos' -> mapas de demanda real vs potencial

### prevision de matriculaciones  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Boletin/informe mensual (PDF) + Clubs de Prevision + consulta en SIMMIX

### caracteristicas tecnicas del vehiculo  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Base de datos de Matriculaciones (dataset/consulta), como atributos de fila; NO ficha visual por VIN

### parque vivo / oportunidad postventa  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Dataset PARQUE + SIMMIX (potencial de postventa) + informes

### kpis operativos de postventa  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Espacio de Datos SIMMIX-KPI / entorno NEXO (benchmarking sectorial anonimizado)

### datos geoeconomicos provinciales  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Capa de contexto dentro de SIMMIX para analisis de red/site

### matriculaciones nauticas  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Sistema web interactivo nautico (filtros por provincia/segmento/marca/eslora)

### flotas  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Informe analitico de Flotas (registro/listado por empresa)

### posicionamiento de precio / descuento medio  ·  (1 empresas lo colocan)
- **MSI - Sistemas de Inteligencia de Mercado, S.A.**: Informe analitico de Posicionamiento de Gama y Precio

### matriculaciones mtd por tipo de veh culo  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Sección 'Mercado' del home — 'Mercado Español, Matriculaciones mes actual a fecha', contadores en vivo (API TotalMarket)

### kpis de negocio vn+vo diarios + evoluci n de mercado  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Dashboard / Cuadro de Mandos (cockpit con gráfica + métrica)

### an lisis multidimensional  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: ID-Cube (explorador OLAP, pivot interactivo)

### ficha t cnica + ciclo de vida del veh culo  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: ID-Car (pantalla de consulta por vehículo, resultado instantáneo)

### datos por territorio / marca / red de concesionarios  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: ID-Geo (mapa coroplético, análisis geográfico)

### informes predefinidos con detalle t cnico a medida  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: ID-Custom (pantallas de informe específicas del OEM)

### parque volumen/edad media distintivo dgt fuente de energ a antig edad canal  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Informe Parque (PDF/report) en 4 secciones: Resumen · Detalle medioambiental · Antigüedad · Canal

### distintivo ambiental dgt por matr cula + precios  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Caja de input de matrícula en la landing de Distintivos → resultado etiqueta; página Tarifas; B2B en página Empresas

### recall propietario del veh culo  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Flujo de gestión Rellamadas (multietapa) + comunicación postal/digital

### certificado de conformidad comprador  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Flujo COC'S (impresión + envío postal)

### expediente cae de veh culo el ctrico  ·  (1 empresas lo colocan)
- **IDEAUTO — Instituto de Estudios de Automoción, S.L.U. (IEA)**: Flujo de validación en el concesionario (punto de venta)

### cmb + flecha de tendencia  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Market page (cabecera de stats) y bloque 'Market' de la ficha de vehículo por VIN; también como 'precio' de cada fila en el screener /markets y en cada Related Submarket

### stats de mercado  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Cabecera de la Market page, bajo el título del mercado, con filtros temporales 1m/3m/6m/YTD/1y/5y/Max

### gr ficos de mercado  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Widget central de la Market page, con leyenda de estados (Sold/High Bid/For Sale/Last Asking Price/Moving Average)

### screener de mercados  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Página /markets (YOUR MARKETS seguidos + POPULAR/TRENDING MARKETS), patrón stock-screener

### specs por vin  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Tab 'Specs' de la ficha de vehículo (/veh/{slug-VIN}), con sub-tabs Exterior/Interior/Mechanical/Documentation; nota 'decoded from VIN & CLASSIC.COM curators'

### comps con relevance % + 8 atributos de match  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Tab 'Comps' de la ficha de vehículo; cada comp con score y badges; botón 'Filter Comps' para curar el set y guardar el vehículo

### suggested price range  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: En la ficha de vehículo, justo bajo el formulario Contact Seller ('Similar vehicles have sold within this price range recently')

### media categorizada  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Tab 'Media' / galería de la ficha de vehículo, con conteo por categoría

### campos de listing/lot  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Tarjetas de listing en el grid de la Market page y cabecera de la ficha de vehículo

### estimated insurance rate + guaranteed value  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: CTA en la ficha de vehículo y en la Market page (convierte el valor en cotización de seguro)

### listing analytics  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Dashboard del vendedor/dealer por cada listing

### top 100 markets / trending por tramo / market reports  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Insights/Blog (capa de inteligencia separada de la ficha)

### gr fico de mercado embebible  ·  (1 empresas lo colocan)
- **CLASSIC.COM**: Embeds (EMBED DATA): incrustado en webs/blogs/foros de terceros, con selección de Market y rango <=5 años

### specs tecnicas + equipamiento estandar/opcional + packs + colores + precio de lista/opciones  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Ficha tecnica / build sheet vertical (Carspecs / Vehicle Viewer / VINView): cabecera de identificacion -> equipamiento estandar agrupado (safety/ADAS, infotainment, comfort) -> opciones y packs con codigo y precio -> colores -> tecnica/dimensiones/powertrain/consumo-CO2 -> precio. Build rules gobiernan las dependencias del configurador

### build exacto fitted + price-when-new desde matricula/vin  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Caja de decode VIN/VRM (VINView Pro): input matricula o VIN -> build real fitted + precio cuando nuevo; puerta de la ficha de usado y del flujo de stock acquisition

### diferencias de features entre vehiculos / sets competitivos  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Comparador side-by-side (Compare endpoint) y 'baskets' (sets competitivos guardados en Price Tracker)

### matriculaciones market share segmentos fuel mix nowcast  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Dashboard de mercado (ModelMix Navigator / JATO Net) con drill por region/segmento/marca/modelo

### movimientos de rrp y valor por cambios de equipamiento  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Dashboard de precios (Price Tracker) con alertas semanales y posicionamiento competitivo

### composicion de descuento net transaction price distribucion de incentivos correlacion con share  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Dashboards de incentivos (7 pestanas: summary / trend / price / comparison / discount / volume / detailed)

### deposit apr cuota mensual term contribution  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Vista de cuotas mensuales (Monthly Payments): comparacion side-by-side de ofertas - la 'affordability view'

### kpis de dealer vs mercado anonimizado price discount feature popularity days-to-sell option uptake colour popularity  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Informe de benchmark de concesionario (Sales Link), con narrativa auto-generada por IA

### co2 / consumo / eec / range por configuracion + tco + tax  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Panel WLTP/emisiones (WLTP Link): etiquetas y quotes compliant, configuracion dentro de presupuesto

### listing de usado estandarizado + filtros a nivel spec + descripcion auto + price-when-new  ·  (1 empresas lo colocan)
- **JATO Dynamics**: Enriquecimiento de listing retail (Retail Listings use case) con Smart Descriptions

### rankingvalue de features/techspecs/packages  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Vehicle Details Page (VDP): ordena y prioriza los features clave por importancia para conveniencia del shopper

### benefitstatement  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: VDP: tooltips / texto expandible que educa al shopper sobre cada feature

### name branded vs namenobrand  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: VDP usa branded (merchandising); comparador usa no-branded (comparación cross-OEM)

### vehicle details report / chromedata vehicle report  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Punto de venta / descarga en VDP como sales-aid, generado desde VIN + rankings CVD

### im genes stock / colorized / multi-view  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: SRP (thumbnail) y VDP (galería); color-match al color exterior seleccionado

### model test drive videos  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Model research pages, SRP y VDP

### vin test drive videos  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: VDP del listing concreto (VIN)

### incentivos regionales  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Se muestran tras introducir vehículo + Zip/código postal; solo los de ese Zip para ese vehículo -> VDP / calculadora de pago

### lender desk payment quotes  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Herramientas de digital retailing / payment / desking; pago estático en listings (SRP/VDP)

### configuraci n as-configured price  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Configurador 'Build & Quote'

### comparaci n lado a lado  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Pantalla de comparador de vehículos

### inventario normalizado  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: SRP listings, sindicado a JDPower.com / MSN Autos / Google My Business

### window sticker / specs por vin  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Mobile app (scan VIN)

### safety/adas features  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Back-office de reparación/calibración ADAS y suscripción de seguro (StudyPrice)

### as-built valuation  ·  (1 empresas lo colocan)
- **ChromeData (part of J.D. Power / Autodata Solutions Division)**: Herramientas de tasación/trade-in, colateral de lender, total-loss: valor por VIN

### standard/optional equipment + oem marketing descriptions  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Vehicle Detail Page (VDP) descriptions and inventory listings on dealer sites (highlights consumer-friendly features)

### normalized equipment + key features/categories/ratings  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Inventory search filters + Compare module (side-by-side by trim/model)

### technical specs / dimensions / weights  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Model/trim research pages; vehicle classification for transport logistics

### epa mpg + epa green scores  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Vehicle details pages

### nhtsa 5-star safety ratings  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Online research + Compare and inventory marketing; also insurance/risk

### awards & accolades  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Marketing: websites, mailers, email campaigns, ebrochures; pre-owned promotion

### vehicle images  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Inventory display / VDP and online quoting & lead forms

### vehicle overviews  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Dealer websites for generic model research and/or VDP; classifieds/portals builder/compare pages

### colors  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Online color display; mfr_code for touch-up paint / upholstery matching

### build logic + oem option rules/pricing  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Build & Price configurator (PerfectFit Build) -> submit as lead

### importance scoring  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Attribute-based shopping landing (PerfectFit Vehicle Shopper) -> PerfectFit vehicle + best-fit list

### per-model/trim specs equipment mpg safety  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Research pages with accordion dropdowns + model-year/trim navigation + multi-angle eVox images (PerfectFit Research)

### warranty  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: VDP + targeted marketing (customers with warranty about to expire)

### adas / safety features / installed equipment  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Insurance underwriting & rating + claims

### reverse vin lookup / vinstub  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Insurance quote forms (minimal consumer input -> partial VIN to carrier)

### oem service schedules + recalls + aces ids  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Service lane scheduling & shop logistics + service marketing/CRM (reminders, recall outreach)

### j.d. power / kbb valuation mapping  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Dealer inventory management (used/new valuation lookup)

### cox rates & incentives mapping  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Dealer website / F&I (real-time incentives display)

### registrations / sales / market share / lienholder  ·  (1 empresas lo colocan)
- **DataOne Software (DataOne, LLC)**: Cross-Sell Interactive dashboard, Dealer Scorecard, heat maps, MarketIntel reports

### vin / matr cula / state  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Cabecera del registro — sección JSON 'intro' (primer bloque de toda respuesta)

### make/model/year/trim + body/doors/size/seating  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Bloque 'basic' (identidad del vehículo, justo bajo 'intro')

### specs t cnicas  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Ficha de especificaciones en grupos temáticos colapsables (Mechanical & Powertrain / Interior / Exterior) — patrón 'spec sheet' multi-sección

### valor de mercado  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Panel de valoración = matriz/tabla: filas=condición (Outstanding/Clean/Average/Rough) x columnas=tipo-de-valor; bloque 'market_value' anidado en la ficha del coche

### msrp / destination charge / option pricing / equipamiento serie vs opcional  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Window Sticker (Monroney) renderizado como PDF/PNG: bloque de precios base+opciones+total y dos columnas de equipamiento + OEM Build Data (build sheet)

### consumo mpg/mpge + coste anual + emisiones co2/smog + crash ratings nhtsa + garant a  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Paneles del Window Sticker (eficiencia / seguridad / garantía)

### historial completo  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Informe de historial white-label (HTML/PDF) con secciones apiladas: timeline de propietarios -> badges title/damage -> timeline cronológico de eventos -> registros de km -> accidentes -> servicio -> galería de subastas -> recalls

### evento de subasta  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Card por evento de subasta con galería de 10+ imágenes + badges de daño/condición + bloque de precio/estimaciones

### listing de venta usado  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Card de listing (price/retail_value/repair_cost, mileage, ubicación, images[], flags newly_listed/reduced_price)

### recalls / tsb / maintenance  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Listas o acordeón de ítems (recall: campaign+component+consequence+remedy; TSB: number+title+date+pdf; maintenance: intervalo+menús+coste low/high)

### fitment ruedas/neum ticos towing obd port windshield/nags  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Sub-fichas técnicas de recambio/servicio (bolt pattern/torque; tow/fifth-wheel/GVWR/GCWR; 'location' textual del OBD; NAGS+features+calibration del cristal)

### configuraci n de f brica por vin  ·  (1 empresas lo colocan)
- **Vehicle Databases**: Build sheet — documento de configuración de fábrica (options instaladas + equipment groups + paint/interior codes + MSRP)

### precio + fiscalidad  ·  (1 empresas lo colocan)
- **km77.com**: Tabla superior izquierda de la pestaña /datos, junto a 2 fotos del coche

### herramientas de valor/coste  ·  (1 empresas lo colocan)
- **km77.com**: Columna lateral 'Herramientas de ayuda' de la ficha

### prestaciones y consumos homologados + distintivo ambiental dgt  ·  (1 empresas lo colocan)
- **km77.com**: Primer bloque de la sub-pestaña Datos técnicos

### dimensiones/peso/capacidades propulsi n motor bater a carga transmisi n bastidor/suspensi n direcci n neum ticos  ·  (1 empresas lo colocan)
- **km77.com**: Tablas sucesivas con caption por subsistema en Datos técnicos

### mediciones propias  ·  (1 empresas lo colocan)
- **km77.com**: Pestaña dedicada 'Mediciones propias' (/mediciones-propias)

### comparaci n de hasta 4 coches  ·  (1 empresas lo colocan)
- **km77.com**: Comparador (/comparador); botón 'Añadir al comparador' en cada ficha

### jerarqu a de identificaci n marca modelo a o carrocer a acabado versi n + estado del modelo  ·  (1 empresas lo colocan)
- **km77.com**: Breadcrumb superior de la ficha y etiqueta Disponible/Descatalogado/Prototipo

### matriz de todas las versiones de un modelo/marca  ·  (1 empresas lo colocan)
- **km77.com**: Listado completo por marca (/coches/<marca>/tecnica/listado-completo)

### estad sticas de matriculaciones por pa s/marca/modelo/mes  ·  (1 empresas lo colocan)
- **km77.com**: Sección Mercado (/mercado/...)

### tasaci n vo informe de inspecci n + oferta de compra + precio recomendado  ·  (1 empresas lo colocan)
- **km77.com**: Coches77 / KM77 VO (flujo C2B 'te ayudamos a vender / lo revisamos por ti')

### cat logo de especificaciones como configurador embebible  ·  (1 empresas lo colocan)
- **km77.com**: DriveK (hermano de grupo): widget integrado en +20 partners editoriales, ES/FR/DE/IT

### kpis macro del mercado + best-seller marca/modelo + leaderboard de ventas por marca  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: Home = dashboard macro (landing): fila de 4 KPI tiles grandes arriba, callouts de best-seller y tabla leaderboard debajo. El macro es lo primero, antes que cualquier coche.

### facetas de filtrado brand price body type fuel type lidar battery capacity motor power  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: EV Database (/database): sidebar de filtros junto a un grid de tarjetas de modelo (imagen + nombre + marca + precio + specs clave + 'Add to Compare').

### specs completas por modelo  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: Ficha de modelo (/database/{brand}/{model}): hoja de specs por bloques en orden cabecera -> precio USD/CNY+FX -> powertrain/performance -> bateria/autonomia -> dimensiones/peso -> ADAS/chip -> tabla de trims (nombre+precio+autonomia) -> linea de ventas (uds mes + MoM%).

### price history y china evs depreciation index  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: Montados SOBRE la ficha de modelo como chart, solo en planes de pago (premium).

### comparativa de specs entre 2+ modelos  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: EV Compare (/compare): columnas lado a lado del mismo set de specs de la ficha.

### ventas/matriculaciones con rank uds market share % mom% yoy%  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: EV Sales (/sales): tablas-leaderboard + graficas de serie temporal, con selector de periodo (mes); city-level con >1,000 ciudades y toggle para anadir ICE. Tras login.

### insurance registrations semanales + datasets criticos  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: Email alerts (notificacion al publicarse, 'ahead of others') + newsletter mensual 'State of China EV Market'.

### respuestas analiticas sobre el dataset  ·  (1 empresas lo colocan)
- **CarNewsChina Data (China EV DataTracker)**: China EV GPT: interfaz de chat IA (Enterprise).

### badges resumen  ·  (1 empresas lo colocan)
- **CARFAX**: Top del VHR junto al valor y en cada tarjeta de anuncio del marketplace/web de dealer

### at-a-glance summary  ·  (1 empresas lo colocan)
- **CARFAX**: Caja-resumen con iconos/checkmarks al inicio del VHR (el 'semaforo' de un vistazo)

### ownership history  ·  (1 empresas lo colocan)
- **CARFAX**: Tabla por propietario en seccion Ownership History del VHR

### title brands + lien  ·  (1 empresas lo colocan)
- **CARFAX**: Seccion Title Check del VHR

### accident/damage  ·  (1 empresas lo colocan)
- **CARFAX**: Seccion Additional History/Accident-Damage del VHR, con diagrama del vehiculo

### service history  ·  (1 empresas lo colocan)
- **CARFAX**: Seccion Service History del VHR

### recalls + safety  ·  (1 empresas lo colocan)
- **CARFAX**: Seccion Recalls/Safety del VHR

### detailed history  ·  (1 empresas lo colocan)
- **CARFAX**: Log cronologico al final del VHR (la seccion mas extensa)

### price-to-market  ·  (1 empresas lo colocan)
- **CARFAX**: Banner de color sobre el precio en la tarjeta de anuncio del marketplace y en webs de dealer

### carfax snapshot  ·  (1 empresas lo colocan)
- **CARFAX**: VDP del anuncio (resumen rapido sin abrir el informe completo) y en Facebook Marketplace

### trade-in value / instant cash offer  ·  (1 empresas lo colocan)
- **CARFAX**: Pantalla /value/ (trade-in) y /sell-my-car/ (cash offer)

### service reminders / recall alerts / value tracking / favorite shop  ·  (1 empresas lo colocan)
- **CARFAX**: Dashboard por coche en la app myCARFAX/Car Care

### hbv + vhr para underwriting vin alert/skip trace en collections lienguard en title research  ·  (1 empresas lo colocan)
- **CARFAX**: Embebido en el LOS del prestamista (carfaxforlenders.com)

### total loss valuation  ·  (1 empresas lo colocan)
- **CARFAX**: Plataforma de claims del asegurador (carfaxforclaims.com / Duck Creek / Insuresoft)

### vin alerts crash reports license/partial plate  ·  (1 empresas lo colocan)
- **CARFAX**: App y web investigativa de CARFAX for Police

### number of owners + vehicle usage  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Tarjeta de cabecera central (icono de owners)

### autocheck score + score range  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Tarjeta de cabecera derecha con dial gráfico ('Similar vehicles usually range between X and Y') — elemento dominante

### resumen de problemas  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: 'Vehicle History at a Glance': rejilla de 9 tiles semáforo (Issue Found/No Issue/Severe) bajo la cabecera

### elegibilidad buyback protection  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Banner dedicado tras el 'at a Glance'

### accidentes/da o  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Accident & Damage' con diagrama del coche + tabla Date/Type/Severity

### open recalls  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Open Recall Check' (tabla + enlace NHTSA/dealer)

### mantenimiento oem por millaje  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Recommended Maintenance' (intervalos + Maintenance Minder)

### veredicto od metro  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Odometer Check' (State Title / Auction / Calculation)

### cronolog a completa de eventos  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Detailed Vehicle History': timeline agrupado por dueño con Event Date/Location/Odometer/Data Source/Details

### garant a restante  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'Warranty Check' (tabla por Coverage Type con remaining miles/time/status)

### definiciones  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Sección 'This Vehicle's Glossary' (Term/Section Location/Definition)

### escala bbdd / patente / legal  ·  (1 empresas lo colocan)
- **AutoCheck (by Experian)**: Footer (About AutoCheck, Patent Notice 8,005,759, T&C)

### autocheck score + score range + posicion below/within/above  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Modulo AutoCheck Score, parte superior del informe (hero number); tambien en API AccuSelect como 'AutoCheck Score (Low-High Range)' + Positive/Negative Score Factors

### vin decode + vehicle class  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Cabecera / Vehicle Snapshot del informe

### resumen semaforo problem/no-problem  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Vehicle History at a Glance' (vista de 2 segundos, justo bajo el score)

### severidad de siniestro point of impact airbag deployment auction damage  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Accident & Damage' (rediseno: visualizacion grafica + severity indicators)

### marcas de titulo  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Title Brand Check' (lista de brands con check)

### secuencia de lecturas + rollback/rollover/tampering/discrepancy  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Odometer Check'

### tipo de uso + flags abandoned/grey-market/lien/repo/theft  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Vehicle Use and Event Check'

### n de propietarios current owner start date open recalls  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Bloque Owners / Recalls del informe

### log cronologico  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Seccion 'Detailed / Full History (Chronological)' al final del informe

### elegibilidad de garantia de recompra  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Badge 'AutoCheck Buyback Protection' embebido en el informe

### todos los atributos de historial servidos como campos discretos  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Respuesta JSON de la API Auto AccuSelect, via 'option packs' seleccionables, para incrustar en portal/CRM/appraisal/DMS

### eventos de cambio de historial sobre una cartera/inventario  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Feed de alertas de AutoCheck Triggers (NO ficha de coche): notificacion daily/weekly/monthly/quarterly/custom al lender/dealer/OEM

### dealer sales performance registrations consumer demographics competitive trends  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Panel de market intelligence de AutoCheck Elite (dealer) + Dealer Locator placement

### title federal current state+issue date titulos previos por jurisdiccion odometro al titulo brands total-loss/salvage/junk/insurance  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Informe NMVTIS separado, emparejado al AutoCheck (mismo user ID/invoice/website)

### informe autocheck embebido en el listing  ·  (1 empresas lo colocan)
- **Experian Automotive (AutoCheck)**: Marketplaces/portales (Autotrader, Cars.com, CarGurus, KBB.com, Edmunds, TrueCar, eBay Motors, Carzing) y DMS/appraisal tools via AutoCheck Fast Link

### alertas cr ticas  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Alert banner rojo en lo más alto del informe — lo primero que ve el usuario

### estado de cada check  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Report summary grid: rejilla de badges semáforo pass (verde ✓) / alert (naranja-rojo ⚠) al inicio

### identidad / anti-fraude  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Secciones HPI Fraud Guard + VIN Match + Vehicle Documents

### spec del veh culo  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Vehicle Description (manufacturer spec)

### n mero de keepers anteriores  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Vehicle Ownership

### co2 + tax status/expiry  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Emissions & Tax

### finance pendiente  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Outstanding Finance expandible

### write-off  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Condition Alert expandible

### historial de matr culas / colores  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Plate Transfer + colour changes dentro de Vehicle Description

### fuel economy / coste  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Fuel Economy (DVLA records)

### valoraci n  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Vehicle Valuation — bloque único secundario, no es el foco

### millaje / clocking  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Sección Vehicle Mileage Check (NMR): alerta + tabla Date / Recorded by / Mileage Reading

### detalle de cada bloque  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Cada sección es expandible/colapsable con enlace 'Find out more'

### informe completo  ·  (1 empresas lo colocan)
- **HPI Check (HPI Ltd, a Solera company)**: Servido white-label en subdominios *.hpicheck.com (Gumtree, eBay, Parkers, AA/UCNI) con marca del partner

### vin make model body anio n fuentes/paises n fotos  ·  (1 empresas lo colocan)
- **carVertical**: Cabecera/Overview del informe (top) + nav de anclas

### uso taxi/rental/policia/autoescuela/transporte/adaptado  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Purpose: chips 'Record found / No record found' + descripcion

### robado ahora / en pasado / recuperado + paises comprobados  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Theft: banner de veredicto + checklist por pais

### ultimo km km medio de similares registros rollback  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Odometer: veredicto + tabla fecha/km + grafico de lineas con marca de rollback

### habitos de conduccion  ·  (1 empresas lo colocan)
- **carVertical**: Dentro de Odometer, derivado de la curva de kilometraje

### prestamo/leasing itv/mot scrap import/export  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Financial and legal status: checklist con estado + fecha + pais

### dano parte severidad coste estimado causa fecha pais  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Damage: banner de severidad + tarjeta por registro

### specs tecnicas + equipamiento oem  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Specs & equipment: tabla clave-valor + lista larga codigo->descripcion

### precio estimado banda historicos ventas forecast 7 anios  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Market Price: grafico con banda punteada + marcadores verdes + insights debajo

### estrellas de seguridad + sub-scores + recalls  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Safety: score en estrellas + desglose por area + subseccion Recalls

### exposicion a desastre tipo fecha mapa  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Natural disasters: banner + mapa de area afectada

### titulo salvage/rebuilt/junk  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Title check: estado + fecha del brand

### norma de emisiones / co2  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Emissions: par clave-valor

### fotos historicas  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Photos: galeria con fecha

### eventos cronologicos  ·  (1 empresas lo colocan)
- **carVertical**: Seccion Timeline (cierre): linea de tiempo vertical fecha+pais+evento+explicacion

### vin marca/modelo traccion antiguedad ultimo km expiracion seguro fecha informe qr  ·  (1 empresas lo colocan)
- **autoDNA**: Tarjeta 'Prior / Key Information' en cabecera del informe (lo primero que se ve)

### flags binarios + contador de eventos  ·  (1 empresas lo colocan)
- **autoDNA**: 'Key information' + 'History overview' dentro de la cabecera (semaforo de alarmas antes del detalle)

### specs decodificadas  ·  (1 empresas lo colocan)
- **autoDNA**: Bloque 'Vehicle Information' (segunda seccion)

### equipamiento de fabrica  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Equipment' (lista)

### llamadas a revision  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Manufacturer Recalls'

### robo multi-pais  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Stolen Vehicle Database' (resultado por pais)

### curva de kilometraje + fuente por lectura  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Odometer Readings': grafico de linea interactivo con anotacion de fuente por punto (delata rollback visualmente)

### eventos datados  ·  (1 empresas lo colocan)
- **autoDNA**: 'Vehicle History Timeline': lista cronologica, un card por evento con su ubicacion

### cuantas veces / desde donde se ha consultado el vin  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Last Enquiries' + mapa (senal social/anti-fraude)

### fotos de archivo  ·  (1 empresas lo colocan)
- **autoDNA**: Seccion 'Vehicle Archive Photos'

### acceso/compartir online  ·  (1 empresas lo colocan)
- **autoDNA**: Bloque 'QR Code' (cierre del informe)

### disponibilidad de datos  ·  (1 empresas lo colocan)
- **autoDNA**: Preview gratis tras meter el VIN en home: semaforo de que categorias existen, sin contenido (gancho de conversion)

### us title brands title records theft accidents junk/salvage/insurer sales offers  ·  (1 empresas lo colocan)
- **autoDNA**: Informe US con secciones propias (orientadas a title brand NMVTIS) + Glossary educativo al final

### us valor de mercado actual + msrp  ·  (1 empresas lo colocan)
- **autoDNA**: Bloque 'Vehicle Information' del informe US (unico sitio con 'valor')

### catalogo de paquetes y precios  ·  (1 empresas lo colocan)
- **autoDNA**: Paginas /business-packages y /packages (tabla de lotes con EUR/informe y ahorro)

### vin decoder / buscador  ·  (1 empresas lo colocan)
- **autoDNA**: Widgets embebidos en webs de socios (placement externo, fuera del propio sitio)

### vin / vehiculo / report id / fecha / boton pdf / thumbnail  ·  (1 empresas lo colocan)
- **ClearVin**: Cabecera del informe ('Vehicle History Report For ...')

### contadores por categoria  ·  (1 empresas lo colocan)
- **ClearVin**: Fila de 10 icon-badges (quick summary) justo bajo la cabecera

### clearvin rating  ·  (1 empresas lo colocan)
- **ClearVin**: En la fila de badges, como veredicto destacado (escala de letra)

### navegacion a secciones  ·  (1 empresas lo colocan)
- **ClearVin**: Tabla de contenidos con anclas (#specs, #owners, #carSales...)

### especificaciones tecnicas / decode  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Vehicle Specifications' en grid de campos

### historial de propietarios + usage + alerta multiple-owners  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Ownership History' = tabla por propietario

### odometro + average miles/year + flag overdriven + chart  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Odometer Reading' = tabla cronologica + grafico de progresion

### titulos current + historicos  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Title History' (bloque Current + tabla Historical)

### emission/safety inspection  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Emission & Safety Inspection' = tabla 1 fila

### total-loss de seguro  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Insurance Records' = tabla por insurer (con disclaimer)

### junk/salvage por entidad + disposition  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Junk & Salvage Records' = tabla por entidad

### dano/siniestro  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Accident & Damage History' = imagen de dano + detalles

### liens/impound  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Lien & Impound Records' = tabla historica con nota de verificacion DMV

### title brands  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Title Brand Information' = checklist exhaustivo (~90 codigos NMVTIS)

### valoracion trade-in / retail x rough/average/clean  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Black Book Market Values' = tabla 2x3

### listings de venta/subasta  ·  (1 empresas lo colocan)
- **ClearVin**: Seccion 'Sale History' = cards por listing con galeria de fotos grande (55+/58+/10+)

### disclaimer nmvtis + widget de busqueda  ·  (1 empresas lo colocan)
- **ClearVin**: Footer ('Instant Vehicle Report' CTA + 'Get Report Package')

### vhr summary scorecard as yes/no/count badges  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Header zone of the consumer VHR dashboard — an icon scorecard read at a glance, alongside the Vehicle Details block

### vehicle details  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Header zone of the VHR, adjacent to the summary scorecard

### accident & damage records  ·  (1 empresas lo colocan)
- **CARFAX Canada**: First vertical record section below the header — a chronological timeline

### registration records  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Vertical record section, chronological

### odometer readings  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Vertical record section — chronological mileage trail

### service & inspection records  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Vertical record section

### open recalls - stolen vehicle check - import/export records  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Sequential vertical sections after service

### insurance & claims history and lien information  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Lower vertical sections of the report

### market-based value as a value range split into 4 transaction scenarios  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Standalone Car Value tool result screen, after the input form (VIN or Y/M/M/T + engine/drivetrain/transmission/body/box-length + odometer + postal code)

### history-based estimated trade-in range + lead capture  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Embeddable Trade-in Widget (CTA box) on dealer websites and Kijiji / Kijiji Autos marketplace

### trust badges  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Overlaid on the online marketplace listing card via Badging API

### vin scan summary  ·  (1 empresas lo colocan)
- **CARFAX Canada**: B2B at-a-glance screening card in UI or API response, with upgrade path to full VHR/liens

### vin scan detail 10 attribute groupings  ·  (1 empresas lo colocan)
- **CARFAX Canada**: Per-VIN attribute file delivered via API or bulk sFTP (column dictionary pattern)

### vin scan monitoring status-change flags  ·  (1 empresas lo colocan)
- **CARFAX Canada**: B2B portfolio watchlist portal with email alerts + CSV

### resumen de existencia de datos  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Banda at-a-glance bajo cabecera (semaforo de presencia de contadores)

### navegacion del dossier  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Pestanas-ancla sticky: Vehicle details / Auction sales history / Ownership history / Damage history / Detailed History / Sales history

### pujas/ventas en subasta del vin  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion AUCTION SALES HISTORY (tabla)

### propiedad por dueno  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion OWNERSHIP HISTORY (tarjetas Owner 1..N)

### dano con localizacion  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion DAMAGE HISTORY con diagrama del coche (Front/Right/Back/Left)

### detalle de dano  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion DETAILED DAMAGE HISTORY (Date/Mileage/Source/Comments)

### cronologia completa de eventos por dueno  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion DETAILED HISTORY (timeline agrupado por dueno, Date/Mileage/Source/Comments)

### ventas/transferencias  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Seccion SALES HISTORY (tabla)

### disclaimer / cobertura legal  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Footer del informe

### ficha de lote de subasta  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Tarjeta de resultado del Free Auction History Checker

### seller reserve n de pujas lotes similares catalogo de piezas etk technical equipment  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Overlay de la extension StatVIN Tools directamente sobre la pagina de lote de Copart/IAAI

### decode rapido  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Herramienta standalone /vin-decoding

### owner information + vehicle condition  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Pagina /buy-report (reventa Carfax/AutoCheck; preview gratis del primer bloque)

### coste total de compra  ·  (1 empresas lo colocan)
- **Stat.vin (1VIN STAT)**: Calculador / factura del flujo de delivery (delivery.vin)

### mmr value + mmr range  ·  (1 empresas lo colocan)
- **Manheim**: VDP (ficha del vehículo) + SRP (resultados de búsqueda) + MMR pop-up/tool invocable; también vía API JSON

### mmr adjustments  ·  (1 empresas lo colocan)
- **Manheim**: Panel desplegable del MMR pop-up/tool

### comparables de transacci n  ·  (1 empresas lo colocan)
- **Manheim**: Pestaña 'Transactions' del MMR tool (muestra 30 días, hasta 100) + pestaña 'Auctions summary'

### autograde condition score  ·  (1 empresas lo colocan)
- **Manheim**: Cabecera del VDP + pantalla dedicada de Condition Report

### condition report detallado  ·  (1 empresas lo colocan)
- **Manheim**: Pantalla de Condition Report consolidada (2025), enlazada desde el VDP

### 360-degree images  ·  (1 empresas lo colocan)
- **Manheim**: Galería del VDP + flujo de Manheim Express

### sale light + announcements/remarks  ·  (1 empresas lo colocan)
- **Manheim**: VDP + SRP + display en vivo del 'block' en Simulcast/run list

### lane number / run number / sale date  ·  (1 empresas lo colocan)
- **Manheim**: Run list / pantalla de subasta en vivo (Simulcast)

### ev battery health score + chemistry + warranty + cable  ·  (1 empresas lo colocan)
- **Manheim**: VDP + Condition Report + toggle/ajuste en el MMR (solo EVs elegibles)

### for you recommendations + inventory curation  ·  (1 empresas lo colocan)
- **Manheim**: SRP + homepage de manheim.com

### guaranteed first bid  ·  (1 empresas lo colocan)
- **Manheim**: Flujo de listado de Manheim Express / nueva App (CTA principal)

### vehicle location + dtc codes column  ·  (1 empresas lo colocan)
- **Manheim**: App/web de LotVision (mapa del lote), búsqueda por VIN o work order, hasta 300 vehículos

### forecast valuations  ·  (1 empresas lo colocan)
- **Manheim**: API developer.manheim.com (Forecast Valuations) + projected value 'mes siguiente' en el MMR pop-up

### muvvi index + yoy/mom + 20 segmentos + three-year-old index + retention + conversion + days supply  ·  (1 empresas lo colocan)
- **Manheim**: Capa de Insights fuera de la ficha: coxautoinc.com/insights (5.º día hábil + mitad de mes), Auto Market Snapshot, Market Insights Video

### dealshield ds360  ·  (1 empresas lo colocan)
- **Manheim**: Como 'Buyer's Adjustment' en el sales slip + portal dealshield.com

### base mmr + wholesale above/average/below + mmr range + estimated retail  ·  (1 empresas lo colocan)
- **Cox Automotive**: Pantalla MMR (mmr.manheim.com / Manheim App): encabezado con Base MMR y MMR Range; tres columnas Above/Average/Below para wholesale y estimated retail

### ajustes que recalculan adjusted pricing al vin  ·  (1 empresas lo colocan)
- **Cox Automotive**: Pantalla MMR: bloque de ajustes que recalcula el Adjusted Pricing en vivo

### serie hist rica + proyecci n next month/next year  ·  (1 empresas lo colocan)
- **Cox Automotive**: Pantalla MMR: gráfico/serie histórica + bloque de proyección

### tabla de transacciones recientes con outliers marcados con asterisco e icono small-sample  ·  (1 empresas lo colocan)
- **Cox Automotive**: Pantalla MMR: tabla de transacciones al pie

### autograde score + condition report + iconos visuales de condici n  ·  (1 empresas lo colocan)
- **Cox Automotive**: Vehicle Details Page (VDP, manheim.com): Condition Assessment Area, con imágenes ancladas a cada zona exterior/interior

### seller s disclosures + announcements + structural condition + tires & wheels + odometer + obd-ii/diagnostic  ·  (1 empresas lo colocan)
- **Cox Automotive**: Vehicle Details Page (VDP): secciones de disclosures, estructura, neumáticos, odómetro y datos diagnósticos

### 6 im genes hd + 360 + autocheck snapshot  ·  (1 empresas lo colocan)
- **Cox Automotive**: Vehicle Details Page (VDP): fotos prominentes arriba; bid bar fijo al hacer scroll y checkout slide-out en la propia VDP

### inventario personalizado + mmr potenciado por ia  ·  (1 empresas lo colocan)
- **Cox Automotive**: Home del marketplace / feed de la Manheim App (Cox Automotive Intelligence): carrusel de recomendaciones con valoración IA inline

### guaranteed first bid / upside + mmr + autocheck + build data + captura 360/cr/obd-ii  ·  (1 empresas lo colocan)
- **Cox Automotive**: Manheim Express (flujo vendedor móvil): tarjeta tras escaneo de VIN, GFB como número/oferta destacada

### muvvi + sub- ndices con mom/yoy  ·  (1 empresas lo colocan)
- **Cox Automotive**: coxautoinc.com/insights + site.manheim.com/consulting: gráfico de serie temporal con PDF descargable y call trimestral

### cadsi  ·  (1 empresas lo colocan)
- **Cox Automotive**: Insights: scorecard de barras escala 0/50/100 por dimensión

### forecast de ventas + affordability index  ·  (1 empresas lo colocan)
- **Cox Automotive**: Insights: nota + tablas, PDF descargable + Industry Insights & Forecast Call trimestral

### ciclo de vida de cartera  ·  (1 empresas lo colocan)
- **Cox Automotive**: Dashboard VPM / Large Portfolio Owners: vista de cartera (no de coche individual)

### trade value + retail value + part-exchange value  ·  (1 empresas lo colocan)
- **Cox Automotive**: eVA (UK): ficha de tasación omnicanal alimentada por dataset wholesale (Manheim+Dealer Auction) + retail (Auto Trader); captura self-inspect/roadside/in-store

### identidad + 60+ fotos + 360 exterior/interior  ·  (1 empresas lo colocan)
- **ACV Auctions**: Cabecera de la VDP/listing de subasta en la app ACV (hub del comprador)

### condicion fisica paint meter virtual lift reproductor de amp obdii/dtcs/warning lights frame tire tread narrative announcements  ·  (1 empresas lo colocan)
- **ACV Auctions**: Pantalla dedicada Comprehensive Condition Report (150-puntos)

### acv estimate + high/low  ·  (1 empresas lo colocan)
- **ACV Auctions**: INCRUSTADO dentro del propio Condition Report (Market Report embebido, etiquetado pre/post-inspeccion) y en el flujo Send-to-Auction; patron distinto a Manheim (no es herramienta separada)

### acv estimate standalone + transacciones comparables + third-party pricing  ·  (1 empresas lo colocan)
- **ACV Auctions**: Herramienta ACV Market Report (busqueda Year/Make/Model)

### timer de subasta 20-min + live + proxy bid  ·  (1 empresas lo colocan)
- **ACV Auctions**: VDP de subasta / bloque de puja en vivo de la app

### predictive value por rooftop + turn/gross + days-to-acquisition + redistribution  ·  (1 empresas lo colocan)
- **ACV Auctions**: Dashboard/grid de inventario en ACV MAX

### appraisal de trade-in predictive value + kbb + oem packages + market comps + recomendacion retail/wholesale  ·  (1 empresas lo colocan)
- **ACV Auctions**: Pestana de tasacion (appraisal) en ACV MAX

### suggested price moves + reasoning + profit-vs-speed + predicted outcomes  ·  (1 empresas lo colocan)
- **ACV Auctions**: Side panel de ACV MAX Recommendations dentro de ACV MAX

### auction run lists  ·  (1 empresas lo colocan)
- **ACV Auctions**: Modulo Source/Buy de ACV MAX (sourcing agregado)

### descripciones ia seo + oem build data + window stickers oem con qr + vehicle history highlights + comps + dynamic pricing  ·  (1 empresas lo colocan)
- **ACV Auctions**: Digital Showroom / VDP publica del retailer (cara consumidor) + sticker fisico en el lote sincronizado

### da os anotados + tread 1/32 x4 + undercarriage + valuation range + predicted retail 30d + competitive analysis + oferta clearcar  ·  (1 empresas lo colocan)
- **ACV Auctions**: Appraisal auto-generado en ACV MAX tras drive-through por las torres VIPER; alerta SMS al equipo de servicio

### oferta real-time rooftop-specific + ai damage detection + reconditioning flags  ·  (1 empresas lo colocan)
- **ACV Auctions**: Widget ClearCar en la web del dealer (consumidor: VIN/plate/YMM + cuestionario + fotos outline-match); tambien service lane y lote

### reglas sobre 160+ campos + bids  ·  (1 empresas lo colocan)
- **ACV Auctions**: Pantalla de reglas S.A.M. (Alerts/Bids) o via S.A.M. API; actua sobre las subastas de 20 min

### vin / year-make-model / odometro  ·  (1 empresas lo colocan)
- **OPENLANE**: Cabecera del VDP (Vehicle Detail Page) del listing en el Marketplace

### galeria 25+ fotos + visual boost ai overlay  ·  (1 empresas lo colocan)
- **OPENLANE**: Galeria del VDP y pantalla del Condition Report

### code boost iq banner obd2  ·  (1 empresas lo colocan)
- **OPENLANE**: En lo ALTO de cada Condition Report de vehiculo dealer-consigned

### condition grade + link al cr  ·  (1 empresas lo colocan)
- **OPENLANE**: VDP (resumen) + pantalla dedicada del Condition Report

### paint depth / tire tread / optional equipment / engine audio / mecanica  ·  (1 empresas lo colocan)
- **OPENLANE**: Cuerpo del Condition Report (layout easy-to-read)

### market guide low/avg/high  ·  (1 empresas lo colocan)
- **OPENLANE**: Vehicle Details Page de OPENLANE Canada

### market guide 2.0 forecast 30/60/90 dias + filtros + search history  ·  (1 empresas lo colocan)
- **OPENLANE**: Herramienta Market Guide (buscador standalone, misma pantalla) en OPENLANE Canada

### autoniq panel multi-libro + autoniq wholesale index  ·  (1 empresas lo colocan)
- **OPENLANE**: App autoniq y extension Google Chrome (inyecta market data sobre el marketplace)

### carvalue wholesale + retail + retail-bid spread + % to retail + profit calculator  ·  (1 empresas lo colocan)
- **OPENLANE**: Search results, Condition Report, pagina My Bids, plugin autoniq, ADESA Clear/Simulcast y campo Guidebook Value de AutoIMS

### buy it now / bid / make offer + time remaining / floor price / top bidder / run list  ·  (1 empresas lo colocan)
- **OPENLANE**: Controles del VDP segun formato; Run List y consola Simulcast en vivo; estados Upcoming/Active/Closing/Pending en 45-min

### as described guarantee badge / elegibilidad  ·  (1 empresas lo colocan)
- **OPENLANE**: VDP (badge) + flujo de arbitraje/garantia en la cuenta post-compra

### pay with afc + estado de floorplan  ·  (1 empresas lo colocan)
- **OPENLANE**: Boton en el checkout del VDP + portal AFCDealer (gestion 24/7)

### openlane inspect  ·  (1 empresas lo colocan)
- **OPENLANE**: App movil EU (offline) -> envia al OPENLANE Sell portal

### condition grade  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Search result card + 'at the top of the vehicle details page' (VDP); report (kipper + defectos + imagenes) desplegable desde la ficha; tambien en Live Online / app BCA Buyer

### ev battery health grade  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: 'in the same place as the Condition Grading: on the vehicle search card and at the top of the vehicle details page, both in BCA Vehicle Search and within Live Bidding' (cita literal); AVILOO FLASH report completo desplegable

### guide price / cap clean price  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Search result card + filtros laterales de busqueda (CAP Clean price como faceta)

### informe mecanico  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Capa desplegable desde la VDP: resumen OK/Issue por categoria + seccion de notas; 128 como PDF descargable

### galeria de imagenes  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: VDP: visor full-screen con pan/zoom; Image Downloads alta calidad tras compra

### real-time valuation  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Pantalla de appraisal de BCA Dealer Pro (app del dealer), tras el guided appraisal journey

### valoracion de consumidor  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Widget/API white-label (Consumer Pro) embebido en la web del propio dealer, con su branding

### puja en vivo + concealed proxy bid  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Pantalla de Live Online / xBid / app BCA Buyer

### identidad y atributos del vehiculo  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Search result card + filtros (vehicle type, model group, colour, mileage, age, fuel, grade, sale channel) + free-text search

### market report  ·  (1 empresas lo colocan)
- **BCA (British Car Auctions)**: Capa de mercado FUERA de la ficha: notas de prensa mensuales a prensa de automocion

### ndice agregado de mercado  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Página AUTO1 Group Price Index (auto1-group.com/index) + press releases mensuales — publicación de mercado INDEPENDIENTE de la ficha de coche (patrón barómetro)

### esquema de inspecci n por veh culo  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Flujo EVA de 7 pasos secuenciales, un dato por pantalla; equipamiento preseleccionado por import DAT (no entrada desde cero)

### valor de trade-in en tiempo real + precio esperado  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Dentro del flujo de venta EVA/Remarketing, junto al campo donde el vendedor fija su precio esperado (no es un número aislado: respaldado por pujas en vivo)

### identidad + inspecci n + estado de subasta del coche  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Ficha de coche / listado de subasta del marketplace B2B (tras login solo-dealers): cabecera identidad → bloque condición 'fully documented' → bloque subasta

### puja por m ltiples coches bid agent watchlist alertas  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Live bidding dashboard del comprador (torre de control de compra, gestiona todos los trades en una vista)

### views y bids por coche en tiempo real + descarga de reportings  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Remarketing Dashboard / Live Reporting Tools del vendedor (panel de rendimiento de venta)

### filtros + search requests + notificaci n instant nea de coincidencias  ·  (1 empresas lo colocan)
- **AUTO1 Group**: Barra de búsqueda y alertas sobre el stock del marketplace (comprador)

### a-e  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: 出品票 — justo debajo del 評価点

### comentario del inspector  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: 出品票 — sección crítica de riesgo (la 'más importante' para el profesional)

### c digos de equipamiento  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: 出品票 — en línea con identidad

### im genes 360 interior / bajos / neum tico-llanta  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: CIS — visores de imagen dedicados ampliables dentro de la ficha

### precio en vivo + carril + estado  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: CIS — pantalla Internet Live (puja en tiempo real)

### + +  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: Capa de inteligencia PÚBLICA — tablas IR 月次データ (fuera de la ficha; termómetro del usado japonés)

### b squeda + fotos + + + mensajer a  ·  (1 empresas lo colocan)
- **USS (ユー・エス・エス) Co., Ltd.**: Portal NINJA (忍者) — ficha replicada para el comprador extranjero

### identidad cap value + glass s value lado a lado provenance 360+12 fotos hr nama grade surecheck report link fuel type lane/lot auction centre  ·  (1 empresas lo colocan)
- **Manheim UK**: A. Listing de catalogo (VDP trade-only en manheim.co.uk) — hub del lote; dato gratis solo con cuenta motor trade/business

### nama grade global + damage lines + surecheck checklist + vehicle history + previous usage + odours + equipment + wheel/tyre descriptions  ·  (1 empresas lo colocan)
- **Manheim UK**: B. Inspection report (pantalla/PDF interactivo dedicado, enlazado desde el listing)

### trade value + retail value + future value + part-exchange eva self-inspect eva underwrite guaranteed price eva insight rule-builder  ·  (1 empresas lo colocan)
- **Manheim UK**: C. eVA — capa de valoracion: widget white-label en la web del retailer / app movil / integracion DMS

### lista de lotes proximos con identidad/mileage/grade puja online en vivo o virtual proxy bidding  ·  (1 empresas lo colocan)
- **Manheim UK**: D. Pantalla de subasta (Simulcast / virtual auction)

### average sold price/mileage/age first-time conversion cap value movement wholesale supply index wholesale demand index market health retail forecasts commentary por segmento con days-to-sell volumenes yoy fuel split  ·  (1 empresas lo colocan)
- **Manheim UK**: E. Capa de inteligencia de mercado FUERA de la ficha: Data Dashboard (mensual, coxautoinc.eu) + Insight Quarterly (trimestral) + The Gavel (commentary por segmento)

### trade value + retail value lado a lado  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: eVA - vista de tasacion in-store / resultado de appraisal (una sola pantalla)

### inputs de tasacion  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: eVA Self-Inspect - flujo paso a paso en movil antes de visitar

### retail rating /100 + supply + demand + days-to-sell  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Dealer Auction - superpuesto sobre CADA listado/lote (semaforo accionable por vehiculo)

### average retail sold price + max/min + km  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Dealer Auction - anuncio a pagina completa del vehiculo

### grado nama + lineas de da o + ruedas/neumaticos  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Informe de inspeccion Manheim - PDF interactivo dentro del listado online del lote

### checklist mecanico surecheck  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Informe de inspeccion Manheim - seccion mecanica del PDF

### soh % de bateria + certificado  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Condition Report (CR) y Vehicle Detail Page (VDP) del lote (volcado automatico)

### new car regs/forecast used transactions/forecast production retail margin/demand/supply market health  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Market Insight Data Dashboard - bloque RETAIL/PRODUCCION (tiles superiores)

### days-to-sell sold price mileage age first-time % cap movements supply/demand index  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Market Insight Data Dashboard - bloque WHOLESALE (tiles inferiores)

### precio vin-recomendado reacondicionamiento distribucion days-in-stock residual riesgo  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: RMS Automotive - dashboard unico de portfolio (factory->disposal), modulos por necesidad

### credit line days on plan hammer/fees titulo auditoria  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: NextGear Capital - portal/app de floor plan (dashboard movil)

### finance quote / apr / monthly payment  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Codeweavers - calculadora embebida en la web del retailer/portal

### quote/estado/ubicacion de movimiento  ·  (1 empresas lo colocan)
- **Cox Automotive Europe**: Movex - app/plataforma de logistica

### autotrader retail rating + days to sell + puja/buy-it-now + mileage + age + fuel + location/distance + tiempo restante + thumbnail  ·  (1 empresas lo colocan)
- **Dealer Auction**: Grid de resultados de busqueda (tarjeta de cada lote); ordenable por Retail Rating, price, age, distance, average days to sell, ending soonest, newly listed

### galeria de imagenes + condition report + nama grade + description estructurada + mot/v5/service/owners + mileage/age/fuel/colour + special features  ·  (1 empresas lo colocan)
- **Dealer Auction**: Ficha del vehiculo / VDP (datos declarados y de condicion)

### retail rating + days to sell + market average + margen estimado  ·  (1 empresas lo colocan)
- **Dealer Auction**: Ficha del vehiculo / VDP, integrada junto al panel de puja (no en herramienta aparte)

### puja actual + incrementos 50/ 100/ 200 + maximum/proxy bid + buy it now + make me an offer + indicador de reserva  ·  (1 empresas lo colocan)
- **Dealer Auction**: Panel de puja de la ficha del vehiculo (VDP)

### lotes policy-matched con rating/dias/margen  ·  (1 empresas lo colocan)
- **Dealer Auction**: Stock Alerts por email (emparejamiento automatico a la Stock Policy del comprador)

### stand-in value reserve price subida de fotos+condition report luego cap performance vs subasta fisica dias a vender pujas cash en 5 dias  ·  (1 empresas lo colocan)
- **Dealer Auction**: Dashboard / flujo de listado del vendedor

### tablas por modelo/marca retail margin units sold edad km days to sell retail rating cap clean % average sold price segmentado por bracket de precio y combustible  ·  (1 empresas lo colocan)
- **Dealer Auction**: Indices publicados Retail Margin Monitor / EV Performance Review / Under the Hood (articulos web mensuales/trimestrales)

### standing buy orders / limit orders  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Dashboard BuyingMatrix del dealer comprador: rejilla estilo stock-market, una fila por orden; el sistema rellena y muestra matches con instant offer [RECONSTRUIDO]

### buy-it-now price  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Canal Buy-It-Now: lista paralela de 'cientos de vehiculos frescos/dia' con precio de compra inmediata por VIN

### tradegrade + instant offer + 45-day guarantee + set floor price  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Pantalla de venta/tasacion (point of appraisal) del trade-in del cliente: puja de la red en el momento; reserva con follow-up bids si no hay aprobacion en 24h [RECONSTRUIDO]

### condition report + vehicle history + photos + resultado de inspeccion pre-compra  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Panel 24 Hour With-a-Look: ventana de revision de 24h antes de procesar la compra; aprobar/declinar [VERIFICADO]

### buy fee + inspection fee + transporte + titulacion + arbitraje  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Checkout/transaccion consolidado en un solo bill of sale [RECONSTRUIDO]

### in-group offer + control central/tienda  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Vista Group Trade (multi-tienda): oferta in-group en tiempo real al punto de tasacion sobre todo el inventario del grupo [VERIFICADO]

### vin/plate + mileage + condition multiple dealer offers + highest offer  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Flujo Sell My Car / Instant Max Cash Offer (consumidor): pantalla 1 entrada de datos, pantalla 2 comparacion de ofertas con la highest destacada (en <2 min); flags de elegibilidad bloquean coches no aptos [VERIFICADO]

### imv + deal rating + days on market + price history + comparable cars + dealer rating  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Ficha de coche del marketplace consumidor (cargurus.com): IMV y Deal Rating badge encabezan el precio; resto debajo como contexto de mercado [VERIFICADO]

### price recommendation + market days supply + local competition + lead-potential forecast + missing details flag  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: PriceVantage en el workflow del dealer: por VIN, con deslizador de impacto en leads/turn-time; se sindica al IMS y se superpone via extension Chrome [VERIFICADO]

### next best deal rating / max margin / merchandise health / acquisition insights  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Reportes separados de Dealer Data Insights en el dashboard del dealer (y a nivel grupo) [PARCIAL]

### cargurus intelligence report  ·  (1 empresas lo colocan)
- **CarOffer (a CarGurus company)**: Reporting de mercado publico, fuera de la ficha, para concesionarios [VERIFICADO]

### make model trim body fuel kw doors transmission first-reg mileage location current bid countdown country sale name  ·  (1 empresas lo colocan)
- **Autorola**: Vehicle card in the auction / search-results list (Stock Locator) — Marketplace [verified live]

### filters make/model/year/mileage/fuel/country/sales-type/price-category/vat  ·  (1 empresas lo colocan)
- **Autorola**: Stock Locator search panel + saved Search Agent + Favourites — Marketplace [verified live]

### start price & buy-it-now and reserve price  ·  (1 empresas lo colocan)
- **Autorola**: On the card (start/buy-now) and seller config panel (reserve) — Marketplace

### vin equipment full condition/inspection report damages photo count keys service history  ·  (1 empresas lo colocan)
- **Autorola**: Vehicle detail page — behind 'approved dealer' login (not public)

### geo pricing export index european target price marketability score days-to-sell demand/supply best sale route  ·  (1 empresas lo colocan)
- **Autorola**: INDICATA remarketing/decision dashboard (the wholesale-intelligence tools)

### dealer performance/stock/sales  ·  (1 empresas lo colocan)
- **Autorola**: Dealer location & performance panel (which dealer to remarket each car to)

### lifecycle gateways lead-time registrations recalls servicing repossession  ·  (1 empresas lo colocan)
- **Autorola**: Fleet Monitor configurable dashboard + modules (Service/Order/Booking/Business Partner)

### per-vehicle conversation  ·  (1 empresas lo colocan)
- **Autorola**: Fleet Chat inside Fleet Monitor (chat anchored to the car)

### inspection data  ·  (1 empresas lo colocan)
- **Autorola**: VIS / IHS mobile app (step-by-step) → real-time sync to Fleet Monitor and the auction listing

### repair / claim status  ·  (1 empresas lo colocan)
- **Autorola**: eRepair platform (full repair-process visibility)

### physical status + location of vehicle  ·  (1 empresas lo colocan)
- **Autorola**: Real-time MI of Compound Services / Fleet Services

### stock exposed to buyers  ·  (1 empresas lo colocan)
- **Autorola**: Digital Showroom (online window integrated with Fleet Monitor)

### fees  ·  (1 empresas lo colocan)
- **Autorola**: Public per-country /pricing page [verified live]

### estimated retail value  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Embebido en la TARJETA DE LOTE de resultados (junto a Odometer) y en el bloque Lot Details/Vehicle Information de la ficha — ancla de valor visible antes de pujar [VERIFICADO render]

### year/make/model/trim + lot  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Cabecera de la tarjeta de lote, junto al botón Watch [VERIFICADO render]

### iconos de condici n  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Fila superior de la tarjeta de lote, junto al Lot # [VERIFICADO render]

### odometer + brand  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Bloque central de la tarjeta de lote [VERIFICADO render]

### title type + c digo + primary damage + keys  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Bloque inferior de la tarjeta de lote (con tooltip CERT OF TITLE-SALVAGE) [VERIFICADO render]

### location + item  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Pie de la tarjeta de lote (ej. TX - CORPUS CHRISTI) [VERIFICADO render]

### sale status / time left / current bid / bid now  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Columna derecha de la tarjeta (Upcoming lot | Auction in 2D 6H 17min | Current bid: $X | Bid now | Details) [VERIFICADO render]

### filtros con contadores + sort by sale light  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Panel de filtros izquierdo de lotSearchResults [VERIFICADO render]

### ai search unificado  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Top del Vehicle Finder / barra de cabecera [VERIFICADO render]

### decode/specs  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Bloque Vehicle Information de la ficha VDP [RECONSTRUIDO]

### secciones de spec/equipamiento  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Acordeones desplegables de la ficha VDP [VERIFICADO schema HTML]

### condition report  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Sección 'Order Products & Services' de la ficha VDP (lower right) [VERIFICADO]

### galer a 10 fotos hd + v deo de arranque  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Cabecera visual de la ficha VDP [VERIFICADO]

### proquote / preliminary proquote  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Plataforma de vendedor / Copart Seller Mobile usada por el PERITO durante la evaluación del siniestro — NO en la web pública del comprador [VERIFICADO uso]

### intelliseller  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Dashboard/flujo de consignación del VENDEDOR [VERIFICADO funcional]

### title express  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Portal de aseguradora + Lender Portal (lender entra payoff) + integración claims (One Inc. ClaimsPay) [VERIFICADO]

### sales data  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Menú Inventory → Sales Data (descarga tras login de miembro) [VERIFICADO]

### recomendaciones / voice search / watchlist / saved searches / vehicle alerts  ·  (1 empresas lo colocan)
- **Copart, Inc.**: Member dashboard 'Driver's Seat' [VERIFICADO]

### vin / year-make-model / stock  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Cabecera del VDP (ficha de vehiculo)

### 360 view + feature tour + premium imagery + engine starts + undercarriage  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Galeria de imagenes del VDP

### loss type / primary+secondary damage / start code / title-sale document / airbags / key / odometer  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Bloque Condition del VDP

### engine / cylinders / fuel / transmission / drive line / body style / colores / country of origin  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Bloque Build Data del VDP (decodificado por ChromeData)

### branch / lane-run / aisle-stall / sale date / seller / seller type / acv / sale status  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Bloque Sale Info del VDP

### iaa vehicle score  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Badge prominente en cada VDP (subscribers) + filtro de inventario por condicion

### iaa cost calculator  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Embebido en cada VDP tras login

### sale status + pre-bid/proxy/buy now/time extended  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Consola de subasta AuctionNow (run list en tiempo real)

### total loss predictor + loss advisor  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: IAA Inspection Services Portal / desk del perito de la aseguradora

### sales decision center + manage offers + market value  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Portal vendedor CSAToday (decision de reserva/rerun)

### salvage performance / timeline efficiencies / net returns / total loss files  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: Dashboard de CSAToday (vendedor/aseguradora)

### title status / title tracker  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: IAA Title Procurement Dashboard

### asp / acv / gross return % / negative equity / scrap / ev share  ·  (1 empresas lo colocan)
- **IAA (Insurance Auto Auctions)**: IAA Industry Report / Data Points (hub Insights, PDF+web)

### los 15+ data points  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Panel por vehiculo / Lightbulb (bombilla de un clic) — side-by-side; demo 'What do I know about this car'. PATRON ESTRELLA para la ficha de coche de cardeep

### stockwave max bid + strategy action  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Cierre del mismo panel por vehiculo: los outputs de decision rematan los 15 valores

### lista de oportunidades de 300+ marketplaces con kpi por fila  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Grid de sourcing (run-list enriquecido): columnas=data points, filtro por Profit Goal, Saved Searches/wish lists pre-filtran

### coste de recon + transporte vs target retail  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Glance — mini-calculador de margen embebido antes de pujar

### que categorias comprar  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Strategy Page (overview de stocking); en Plus muestra movimientos de mercado por segmento

### puja en vivo + lane monitor alert  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Simulcast: la puja se embebe junto a los data points del coche que baja por la lane; alerta cuando llega tu coche (Plus)

### valor + recomendacion inmediata por vin en campo  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: App movil AuctionGenius (VIN scan, run lists, notas, bid guidance, profit projections)

### appraisal desde cualquier listado externo  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: VIN-Click Extension (boton flotante en cualquier web)

### provision appraised value + kbb ico  ·  (1 empresas lo colocan)
- **Stockwave (vAuto · Cox Automotive)**: Conexiones cross-product: el valor de adquisicion viaja con el coche hasta la venta; la ICO trae su propia Lightbulb

### valor de mercado + ajuste por condicion great/good/fair  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: Valuador IBB/carandbike: pantalla de resultado de precio

### scores por sistema con x/10 + grado  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: Informe Autoinspekt: bloque de tarjetas de score por sistema

### overall quality score + rating textual + damage/accident/structural  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: Informe Autoinspekt: cabecera destacada del score global

### base valuation refurbishment parking taxes total cost to bidder  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: Informe Autoinspekt: bloque de valoracion (repo/finance)

### 12 categorias de fotos geo-etiquetadas + videos  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: Informe Autoinspekt: galeria de media

### facetas location/seller/category/auctiontype/eventtype/listings/start-end  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: eDiig: lista de eventos de subasta con filtros

### identidad del vehiculo + informe autoinspekt + precio de referencia ibb + reserve/current bid + buyer fees  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: eDiig: ficha de lote (catalogo)

### consulta de precio dealer  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: IBB partner portal: Price Check Premium (tras login; roles Admin/Call Center/Trade Manager)

### inventario por yard ubicacion/slot condicion intake/exit repo release refurb/logistica charging  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: YMS: dashboard centralizado (OEM/financiera) + client.autoyms.com

### market size/forecast suv share age mix asp trend procurement mix consumer behaviour rv trends  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: IBB Report anual: documento narrativo + estadistico

### listings de coche usado + on-road price nuevo + reviews + valuador embebido  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: carandbike: portal de contenido/clasificados B2C

### inventario de stock del dealer + crm/leads  ·  (1 empresas lo colocan)
- **Mahindra First Choice Wheels (MFCWL)**: DMS: dms.mahindrafirstchoice.com (Dealer/Surveyor login)

### estimated sale price  ·  (1 empresas lo colocan)
- **Motorway**: A. Landing / instant-valuation widget (motorway.co.uk home): registration + mileage -> precio instantaneo. Primer punto de contacto / anzuelo

### spec trim extras keys service history condition damage declarations 16 fotos  ·  (1 empresas lo colocan)
- **Motorway**: B. Profile builder (web + app, AI profiling tool): el vendedor construye la ficha que veran los dealers

### guide price  ·  (1 empresas lo colocan)
- **Motorway**: C. Guide price screen: precio guia tailored acordado tras perfilar (puede ser < estimate por costes de preparacion del dealer)

### highest offer / final sale price  ·  (1 empresas lo colocan)
- **Motorway**: D. Daily sale / offers screen (vendedor): el coche entra en subasta diaria, dealers pujan en tiempo real, vendedor ve y acepta la oferta mas alta

### current value + value history 24m + depreciation + monthly alerts  ·  (1 empresas lo colocan)
- **Motorway**: E. Car Value Tracker (dashboard consumidor): seguimiento de valor, hasta 6 vehiculos en la cuenta

### fotos detalladas + spec + condicion + service history + provenance total car check + guide/reserve  ·  (1 empresas lo colocan)
- **Motorway**: F. Dealer listing detail (pro.motorway, login): el VDP wholesale donde el dealer evalua y puja

### smart search filters + stock alerts + shortlist  ·  (1 empresas lo colocan)
- **Motorway**: G. Dealer browse/search (pro.motorway): listings shaped by dealer feedback

### max bid + auto-bid gbp 50 + gbp 1-sobre-siguiente + highest-bidder status  ·  (1 empresas lo colocan)
- **Motorway**: H. Dealer bid + post-win: tras ganar -> seller doc verification -> Motorway Move on-site appraisal -> Motorway Pay (seller+finance+fees en 1 transferencia)

### owners write-off finance logbook loan salvage stolen mot plate changes mileage  ·  (1 empresas lo colocan)
- **Motorway**: I. Total Car Check report (B2C, totalcarcheck.co.uk): informe de historial independiente

### price performance por modelo tech premium transmission split fuel/ev trends  ·  (1 empresas lo colocan)
- **Motorway**: J. Fast Forward Trends report (guias/PR, FUERA del flujo transaccional)

### private sale value + part-exchange value  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Landing del tasador de consumidor (/cars/valuation): un solo input (matricula) -> paso mileage -> dos numeros; friccion casi cero, bloque educativo de factores que suben/bajan valor

### retail valuation + price position  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Inline en cada fila de la stock list del Portal del retailer (portal.autotrader.co.uk) — inteligencia embebida en la tabla de inventario

### retail rating average days to sell supply/demand competitor view retail back calculator  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Retail Check: pantalla workbench por vehiculo ('todo el pricing de un coche en una pantalla')

### trended valuations  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Vehicle Edit -> tab 'Valuation and pricing' del Portal; tambien dentro de Retail Check

### alertas + performance reporting + competitor activity  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Retail Accelerator: dashboard agregado de TODO el forecourt — gestion por excepcion/alerta, no ficha individual

### supply / demand / market condition / days to sell  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Market Insight / Vehicle Insight dashboard — panel macro de mercado FUERA de la ficha, para decisiones de compra de stock

### like-for-like price growth % + mix growth % + average price por segmento  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Retail Price Index: informe mensual PUBLICO/PR (autoridad de mercado, citado por ONS y prensa)

### valuations + vehicle metrics + specs/features/history  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Autotrader Connect: como endpoints API (headless intelligence) para integradores/DMS — /valuations, /vehicle-metrics, /vehicles, Future/Historic Valuations

### vehicle specs technical data y standard/optional features  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Cuerpo de la ficha del anuncio (consumidor) y vehicle detail del Portal

### vehicle check  ·  (1 empresas lo colocan)
- **Auto Trader UK (Autotrader Group plc)**: Flujo de compra/ficha y via Vehicles API 'Full vehicle check'

### preisbewertung label  ·  (1 empresas lo colocan)
- **AutoScout24**: Badge en CADA tarjeta de resultado + ficha de detalle del coche (comprador); panel 'Fahrzeuge verwalten' y al introducir el precio (dealer); página de explicación dedicada del label

### marktpreis / preisdifferenz vs mercado  ·  (1 empresas lo colocan)
- **AutoScout24**: Junto al label en la ficha del vehículo y dentro de HändlerIQ

### fahrzeugbewertung  ·  (1 empresas lo colocan)
- **AutoScout24**: Resultado de la tasación B2C gratuita (enviado por email tras rellenar el formulario sin VIN)

### h ndleriq  ·  (1 empresas lo colocan)
- **AutoScout24**: Home del Händler-Dashboard (resumen) y por-vehículo en la lista de inventario, con Schnellaktionen one-click

### standzeitprognose  ·  (1 empresas lo colocan)
- **AutoScout24**: Métrica IA por vehículo dentro de HändlerIQ/Dashboard

### wettbewerbsanalyse preis-ranking + lista de rivales en vivo  ·  (1 empresas lo colocan)
- **AutoScout24**: Reiter/Tab 'Wettbewerbsanalyse' en la lista de vehículos; lista de rivales con precio/edad/km/Standtage/evolución

### distribuci n de mercado  ·  (1 empresas lo colocan)
- **AutoScout24**: Diagramas en la vista de detalle de la Wettbewerbsanalyse

### ausstattungsvergleich  ·  (1 empresas lo colocan)
- **AutoScout24**: Sección de comparación de equipamiento dentro de HändlerIQ

### kpis de performance  ·  (1 empresas lo colocan)
- **AutoScout24**: Home del Händler-Dashboard, vista central de KPIs

### h ndlerbewertungen + weiterempfehlungsrate  ·  (1 empresas lo colocan)
- **AutoScout24**: Home del Dashboard (notificación + tareas abiertas) + página de reseñas del dealer

### estad sticas de veh culo + h ndleriq + selectboost  ·  (1 empresas lo colocan)
- **AutoScout24**: Embebidos dentro del DMS/sistema del proveedor de datos (los 10 mayores; 6 con HändlerIQ) — donde el dealer trabaja a diario

### marktreport / golf-index / jahresanalyse  ·  (1 empresas lo colocan)
- **AutoScout24**: PDF/press release de mercado (mediacenter/daten), separado del per-vehículo

### smyle datos por coche  ·  (1 empresas lo colocan)
- **AutoScout24**: Ficha del coche en el shop online Smyle

### imv + barra de gradiente verde rojo con marcador del precio + pricedifferential  ·  (1 empresas lo colocan)
- **CarGurus**: Bloque 'Price Analysis' de la ficha del vehículo (VDP)

### savings vs imv + new price tachado  ·  (1 empresas lo colocan)
- **CarGurus**: Bloque de precio de la tarjeta SRP

### price history + days listed  ·  (1 empresas lo colocan)
- **CarGurus**: Ficha VDP, sección de precio/temporalidad

### payment calculator  ·  (1 empresas lo colocan)
- **CarGurus**: Ficha VDP, bloque de financiación

### dealer rating + review count + rese as + top rated dealer badge + chat 24/7  ·  (1 empresas lo colocan)
- **CarGurus**: Ficha VDP, bloque del concesionario

### imv retail + private sale value + trade-in value  ·  (1 empresas lo colocan)
- **CarGurus**: Pantalla Car Values (input matrícula/VIN/manual)

### avg price + 30d/90d/yoy % + biggest movers + cargurus index  ·  (1 empresas lo colocan)
- **CarGurus**: Página pública Price Trends (tabla por make/model + bloques de top movers)

### imv + deal rating + recomendaci n de precio vin-level + market days supply + competidores + forecast de leads  ·  (1 empresas lo colocan)
- **CarGurus**: Dealer Dashboard → Pricing Tool / PriceVantage (lista de inventario)

### search rank / search page / vdp views / saves / connections  ·  (1 empresas lo colocan)
- **CarGurus**: Dealer Dashboard → VDP Activity (por unidad)

### qu buscan los consumidores + recomendaciones de qu comprar  ·  (1 empresas lo colocan)
- **CarGurus**: Dealer Dashboard → Market Analysis / Acquisition Insights

### deal jackets + leads tipados  ·  (1 empresas lo colocan)
- **CarGurus**: Dealer Dashboard → Digital Deal tab (y CRM via ADF)

### index / demand index / intelligence report / consumer insights  ·  (1 empresas lo colocan)
- **CarGurus**: Páginas y PDFs de research/press (autoridad de marca + SEO + lead-gen)

### trade-in / private party / dealer retail  ·  (1 empresas lo colocan)
- **Edmunds**: Appraisal results: matriz por style/trim con 3 columnas + titular de rango ($low-$high), tras stepper de 6 pasos (Step 1 Location & Style ... Step 6 Report Delivery)

### edmunds suggested price  ·  (1 empresas lo colocan)
- **Edmunds**: Ficha de coche nuevo y listing: ENCIMA del MSRP; también en Build & Price

### deal rating great/good/fair + above/below market  ·  (1 empresas lo colocan)
- **Edmunds**: Cada listing (SRP card + VDP) via Price Checker, comparado con mismos year/model/trim

### edmunds rating + scorecard por categor as  ·  (1 empresas lo colocan)
- **Edmunds**: Hero de la ficha/review de coche nuevo, con Pros/Cons y 'Edmunds says'

### true cost to own  ·  (1 empresas lo colocan)
- **Edmunds**: Página TCO del vehículo: bloque 'TCO Summary' + 'Five-Year Details' (tabla año-a-año)

### consumer ratings  ·  (1 empresas lo colocan)
- **Edmunds**: Bloque de reviews: Overall ★(de 5) + barras de distribución 5★-1★ + Customer Summary AI + reviews ordenables/paginadas

### ev real-world range vs epa + consumption  ·  (1 empresas lo colocan)
- **Edmunds**: EV Range Test leaderboard / EV Hub; tax-credit finder en página EV

### calculadoras  ·  (1 empresas lo colocan)
- **Edmunds**: Página /calculators/ con tabs; las cifras se arrastran de un tab al siguiente

### incentivos / lease deals  ·  (1 empresas lo colocan)
- **Edmunds**: Páginas /car-incentives/ y /lease-deals/ filtrables por make/model/type/estado

### industry metrics  ·  (1 empresas lo colocan)
- **Edmunds**: Notas de prensa Insights + Data Center (gráficas + cifras mensuales/trimestrales)

### 11 inputs del tasador  ·  (1 empresas lo colocan)
- **coches.net**: Formulario del tasador (/tasacion-de-coches), una sola pantalla; bloque '¿Cómo calculamos la tasación?' (4 pasos) debajo

### doble precio + cta publicar anuncio / elegir profesional  ·  (1 empresas lo colocan)
- **coches.net**: Pantalla de resultado del tasador

### precio + rango + km/a o/combustible + datos t cnicos/equipamiento/extras + tipo de vendedor + garant a  ·  (1 empresas lo colocan)
- **coches.net**: Ficha de anuncio (detalle del coche en el marketplace VO)

### facetas de filtro mismos campos  ·  (1 empresas lo colocan)
- **coches.net**: Buscador de segunda mano

### datos t cnicos + precios por versi n + comparativa lado a lado  ·  (1 empresas lo colocan)
- **coches.net**: Sección Pruebas e información → Información técnica (Fichas técnicas / Comparador)

### price radar y comparador de precios avanzado  ·  (1 empresas lo colocan)
- **coches.net**: coches.net PRO, inline sobre el vehículo al insertar/gestionar el anuncio

### demand radar y detecci n de activos t xicos por antig edad  ·  (1 empresas lo colocan)
- **coches.net**: coches.net PRO, panel de stock

### performance por anuncio + informe mensual  ·  (1 empresas lo colocan)
- **coches.net**: coches.net PRO, Estadísticas avanzadas

### backend gated de la capa de insights pro  ·  (1 empresas lo colocan)
- **coches.net**: portal-insights.coches.net (gateway autenticado; raíz = health-check 'Test de conexión')

### precio medio/oferta/demanda/ventas por combustible-antig edad-ccaa  ·  (1 empresas lo colocan)
- **coches.net**: Blog PRO → Barómetros (nota de prensa mensual)

### ventas nuevo + ventas vo + series oferta/demanda + precio anual/mensual + encuesta de consumidor + voz del experto  ·  (1 empresas lo colocan)
- **coches.net**: Blog PRO → Mobility Trends (PDF mensual descargable, ~17 págs)

### tasaci n de coches informe de veh culos financiaci n seguros c mo vender tu coche  ·  (1 empresas lo colocan)
- **coches.net**: Menú Trámites y Servicios (consumo)

### price-rating badge  ·  (1 empresas lo colocan)
- **mobile.de**: Consumer vehicle listing-detail page, next to the price (traffic-light label since 2017)

### market price bar/scale with the car s position across the 5 tiers  ·  (1 empresas lo colocan)
- **mobile.de**: Consumer listing-detail page price area (verified via API labelRanges; exact visual layout inferred)

### battery health certificate + warranty battery-warranty filter  ·  (1 empresas lo colocan)
- **mobile.de**: EV listing-detail page (consumer) and search filters

### performance kpis  ·  (1 empresas lo colocan)
- **mobile.de**: Inserats-Analyse tool (dealer), per-vehicle Performance-Kennzahlen block

### mobile.de marktpreis + current price label + delta to reach next category  ·  (1 empresas lo colocan)
- **mobile.de**: Inserats-Analyse tool (dealer), Marktpreis + Preisbewertung block

### search-results position  ·  (1 empresas lo colocan)
- **mobile.de**: Inserats-Analyse tool (dealer), Position in den Suchergebnissen block

### 60-day sale probability  ·  (1 empresas lo colocan)
- **mobile.de**: Inserats-Analyse tool (dealer), 60-Tage-Verkaufswahrscheinlichkeit block

### similar competitor vehicles table  ·  (1 empresas lo colocan)
- **mobile.de**: Inserats-Analyse tool (dealer), Marktvergleich block

### which listings need attention  ·  (1 empresas lo colocan)
- **mobile.de**: Analyse-Übersicht (portfolio level) in the Händlerbereich / portal-insights

### per-listing access/engagement trends  ·  (1 empresas lo colocan)
- **mobile.de**: Nachfrageanalyse (demand analysis) panel in the dealer area

### listing quality score + sub-scores  ·  (1 empresas lo colocan)
- **mobile.de**: Quality-Check view (dealer / Data Partner)

### dealer reputation  ·  (1 empresas lo colocan)
- **mobile.de**: Dealer rating overview (profile/reviews) + Seller API rating/overview

### market health index by drivetrain / segment / age  ·  (1 empresas lo colocan)
- **mobile.de**: m.Q Market Intelligence report (point charts) for advertisers/OEM

### top searched equipment & vehicle types avg price & trends demand change  ·  (1 empresas lo colocan)
- **mobile.de**: m.Q Market Intelligence report (advertising.mobile.de)

### avg used price days-to-sell avg mileage stock price change by segment  ·  (1 empresas lo colocan)
- **mobile.de**: Preisbarometer / Autobarometer monthly market report (press/newsroom)

### estimated value + market price range  ·  (1 empresas lo colocan)
- **mobile.de**: Consumer Fahrzeugbewertung tool (Was ist mein Auto wert?), Schwacke-backed

### visibility products social/google reach direct offer  ·  (1 empresas lo colocan)
- **mobile.de**: Werbemanager / Booking Assistant in the dealer area; Feature Settings via API

### price rating + price graph  ·  (1 empresas lo colocan)
- **TrueCar**: Centro del New Car Price Report / Price Curve — elemento visual dominante en 4 bandas de color

### guaranteed savings amount + truecar price estimate  ·  (1 empresas lo colocan)
- **TrueCar**: Bloque de ahorro del Price Report -> Guaranteed Savings Certificate imprimible para llevar al dealer

### manufacturer/customer/dealer incentives  ·  (1 empresas lo colocan)
- **TrueCar**: Seccion de incentivos del Price Report + custom_dealer_offers de la red local

### badge de price rating  ·  (1 empresas lo colocan)
- **TrueCar**: Sobre el precio en la tarjeta de anuncio y en la VDP de coche usado (ancla visual)

### historial carfax o autocheck  ·  (1 empresas lo colocan)
- **TrueCar**: Bloque de historial dentro de la VDP de usado

### estimated monthly payment / lease  ·  (1 empresas lo colocan)
- **TrueCar**: Calculadora de pago en la VDP de usado

### true cash offer con valor recalculandose en vivo  ·  (1 empresas lo colocan)
- **TrueCar**: Flujo guiado de Sell/Trade: matricula/VIN -> mileage/color/options -> oferta -> CTA a Certified Dealer

### trim comparison + star rating + verified owner reviews + pros/cons  ·  (1 empresas lo colocan)
- **TrueCar**: Paginas de modelo/Research

### leads + analytics de mercado + true insights + pricing ia 5 niveles + dms verification  ·  (1 empresas lo colocan)
- **TrueCar**: DealerPortal (B2B) — dashboards de leads y mercado

### escalera msrp - advertised price - offer price - your price - drive-off price  ·  (1 empresas lo colocan)
- **TrueCar**: Marco de precios de 5 niveles, transversal — lleva al shopper de afinidad del precio publico al neto + drive-off all-in

### partner preferred pricing / member only offers / military appreciation package  ·  (1 empresas lo colocan)
- **TrueCar**: Sitios de afinidad 'powered by TrueCar' (AAA, Sam's Club, PenFed, AmEx, Navy Federal) + military.truecar.com

### deal badge high demand american-made index range score list price price drop est. /mo mileage dealer star rating distancia  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: SRP (Search Results Page) de Cars.com — tarjeta de anuncio; orden de arriba a abajo: foto -> badges -> year/make/model/trim -> precio(+price drop)+Est./mo -> mileage -> dealer+rating -> ciudad,estado(distancia). Barra de sort incluye 'Best deal' y 'Newest/Oldest listed'

### list price deal badge cpo badge specs free autocheck report calculadora de pago ev range score seller notes dealer rating  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: VDP (Vehicle Detail Page) de Cars.com — cabecera galeria + precio/Est.mo + badge; bloques de specs, historial AutoCheck (Experian), pago mensual/pre-approval, EV range, dealer; CTA contacto/lead + trade-in (AccuTrade)

### powerscore overall star rating desglose por dimension rese as + employee ratings + dealer response certified dealer/consumer satisfaction award/dealer of the year badges  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Pagina de concesionario en DealerRater / perfil de dealer en Cars.com

### estimated market value + lower/upper bound mdape accuracy  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Calculado por modelo XGBoost (1 año de usados, excluye list_price); se materializa como el deal_badge mostrado en SRP/VDP

### valor garantizado / rango + caducidad + deducciones itemizadas gross profit retail vs wholesale daily depreciation projected dom inventory intelligence score  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Pantalla de tasacion AccuTrade (entrada VIN/plate/YMM -> stepper de condicion -> resultado) y consola IMS (ver accu-trade.md §7)

### letter grade + fotos/videos + guaranteed condition rating de reputacion del vendedor bidding interactivo + public chat follow/block  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: App/web de subasta DealerClub — ficha de vehiculo + bloque de vendedor

### impresiones a in-market shoppers vin-level sales attribution location-based signals vdp conversion dealer website visits sales influenced  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Dashboard de reporting de campaña de Cars Commerce Media Network

### ncpi new sales/inventory/avg price/days on lot/model-year mix/mass-market vs luxury used inventory/price/days/affordability/body-style ev share market share by brand demand trade-in values  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Industry Insights Report mensual — estructura: executive summary -> seccion New -> seccion Used -> EV -> brand-level -> demand; entregado en web + PDF + Google Slides + email subscription

### instant loan approval/decision penny-perfect monthly payment apr term down payment lender match  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Calculadora/widget de financiacion CreditIQ embebido en VDP de Cars.com y en web del dealer (Dealer Inspire)

### vdp views leads + lead source conversion rate market position  ·  (1 empresas lo colocan)
- **Cars Commerce (Cars.com Inc.)**: Dashboard/consola de analitica de dealer (Experience) — patron de industria, no verificado en fuente oficial

### indicador price-to-market + frase explicativa  ·  (1 empresas lo colocan)
- **La Centrale**: Ficha de annonce: junto al precio en la cabecera Y en un bloc 'Prix' dedicado; también como tarjeta en la lista y como filtro de búsqueda

### mensualit  ·  (1 empresas lo colocan)
- **La Centrale**: Cabecera de la annonce, bajo el precio

### points forts detectados por ia  ·  (1 empresas lo colocan)
- **La Centrale**: Fila de badges bajo el título de la annonce

### caract ristiques  ·  (1 empresas lo colocan)
- **La Centrale**: Grid 'Caractéristiques' en el cuerpo de la annonce (Voir tout 20)

### quipements destacados  ·  (1 empresas lo colocan)
- **La Centrale**: Sub-bloque dentro de 'Équipements & options' (Voir tout 24)

### financement  ·  (1 empresas lo colocan)
- **La Centrale**: Bloque embebido en la propia ficha de annonce

### historial autoviza  ·  (1 empresas lo colocan)
- **La Centrale**: Bloque 'Historique' de confianza en la annonce + CTA 'Voir l'historique Autoviza'

### volution du prix / curva de depreciaci n futura  ·  (1 empresas lo colocan)
- **La Centrale**: Página de resultado de la cote, bajo el valor estimado

### toggle acheteur/vendeur  ·  (1 empresas lo colocan)
- **La Centrale**: Formulario de entrada de la cote

### bloc pricing de decisi n  ·  (1 empresas lo colocan)
- **La Centrale**: Dashboard de Pilot Price (un solo lugar de aide à la décision)

### overlay demande/concurrence/prix  ·  (1 empresas lo colocan)
- **La Centrale**: Pilot Match: superpuesto sobre sitios externos, plataformas de subastas y DMS donde el pro ya trabaja

### demande/offre por regi n y mod les demand s  ·  (1 empresas lo colocan)
- **La Centrale**: Pilot Trends (panel de sourcing pro)

### prix moyen/m dian vo + evoluci n por edad/motorizaci n  ·  (1 empresas lo colocan)
- **La Centrale**: Observatoire du prix VO: informe PDF trimestral (presse.lacentrale.fr) y prensa, separado de la ficha individual

### badges de confianza ++/ + +  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: Tarjeta de anuncio (lista de búsqueda), esquina superior sobre la foto

### + + enlace tags comerciales  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: Cuerpo de la tarjeta de anuncio en la lista

### opciones standard/choice/etc/tuning  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 2 (옵션정보)

### + / + fotos de bajos  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 3 (차량상태 / estado del vehículo)

### grado + /warranty  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 4 (보증현황 / estado de garantía)

### financiaci n  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 5 (금융)

### dealer + isverifyowner + contacto  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 6 (판매자정보)

### + / + tiers / + del modelo  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP — sección 9 (시세) y herramienta 엔카시세/내차시세 (cifra central + laterales + gráfico)

### viewcount + subscribecount  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: VDP, junto al anuncio (engagement como proxy de demanda)

### % medio de cambio mom + tabla por modelo + + nota ev + pie metodol gico  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: Boletín mensual de 시세 publicado a la prensa (no en la UI del producto)

### inspection badge p1/p2 + price + chassis code + free history report  ·  (1 empresas lo colocan)
- **Encar (엔카닷컴 / Encar.com)**: Tarjeta de anuncio del sitio de exportación (global.encar.com, en inglés)

### puntuaciones de en /5  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Página 口碑 del modelo (radar/barras + reseñas escritas por subítem)

### + %  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Tarjeta de valoración de usado en che168 (二手车之家), junto a km/matrícula/ciudad y badges de certificación

### % por modelo  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Tablas del ranking anual 保值率 (research) y consulta en che168

### 8 m dulos anal ticos  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Dashboard ejecutivo 车智云 para OEM (bigdata.autohome.com.cn), paneles con gráficas y predicción

### m dulos de leads  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Consola de marketing/CRM 销售宝 para concesionario, embebida en su flujo de venta

### ai + ai / / / + voc + 30% conversi n  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Capa AI transversal sobre el embudo (OEM+dealer) + AI数字人/asistente en la capa de consumo

### y  ·  (1 empresas lo colocan)
- **Autohome (汽车之家)**: Home del portal + flujo de transacción Autohome Mall (piloto Shenzhen/Xi'an)

### pre o anunciado + pre o fipe + valor m dio de similares  ·  (1 empresas lo colocan)
- **Webmotors**: VDP / ficha del anúncio, junto al precio — patrón estrella para cardeep

### selo super pre o  ·  (1 empresas lo colocan)
- **Webmotors**: VDP + tarjetas de resultado del buscador (inline)

### selo vistoriado  ·  (1 empresas lo colocan)
- **Webmotors**: VDP + filtro de búsqueda dedicado

### gr fico de hist rico de precio  ·  (1 empresas lo colocan)
- **Webmotors**: VDP (para algunos modelos)

### valor tabela fipe vs valor tabela webmotors  ·  (1 empresas lo colocan)
- **Webmotors**: comparador dedicado /tabela-fipe + tasador /quanto-meu-carro-vale

### filtro abaixo da fipe + filtros  ·  (1 empresas lo colocan)
- **Webmotors**: buscador / página de estoque (resultados)

### par metros de pre o + tempo m dio de venda  ·  (1 empresas lo colocan)
- **Webmotors**: Cockpit — Estoque del lojista, inline por vehículo

### autoguru margem ideal sortimento do p tio tempo de p tio pre o vs concorr ncia pr xima idade/km del estoque  ·  (1 empresas lo colocan)
- **Webmotors**: Cockpit — consejero IA (decisión de compra/venta por excepción)

### ndice webmotors varia o %  ·  (1 empresas lo colocan)
- **Webmotors**: Autoinsights (dashboard) + índice público citado por prensa; recortes por Estado/segmento/km en suscripción

### autoinsights rankings mais procurados preferencias estudos tem ticos  ·  (1 empresas lo colocan)
- **Webmotors**: fuera de la ficha — dashboard / Excel (dados brutos) / apresentação a medida

### laudo de inspe o  ·  (1 empresas lo colocan)
- **Webmotors**: PDF descargable enlazado desde la VDP vía selo Vistoriado

### inventario + leads  ·  (1 empresas lo colocan)
- **Webmotors**: API Sensedia (sindicación headless para integradores/gestores de estoque)

### precio + descuento + badges  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Tarjeta de resultados del listado domestico (search results card): foto, titulo marca+serie+ano+trim, linea de specs km/ciudad/ano, precio grande, insignias de confianza y tags de garantia

### visor de inspeccion 3d 360 + informe 259 puntos  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Ficha de detalle del vehiculo (domestica): galeria arriba con visor 3D; seccion de informe de inspeccion debajo con los defectos destacados primero

### estimacion oficial comparada con el precio pedido  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Ficha de detalle, junto al precio de venta (ancla de valor justo)

### financiacion  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Ficha de detalle, bloque de financiacion bajo el precio

### informe de accidentes gratuito + panel de garantias  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Ficha de detalle, panel de confianza/post-venta

### formulario de estimacion - resultado  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Pagina de venta/valoracion sell.guazi.com/evaluate (flujo guiado lead-gen)

### ranking indice de recomendacion curva de depreciacion 1-8 anos 9 insights anuales  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: NO en dashboard: publicados como informes/rankings en prensa y blog (placement editorial, no producto interactivo ni API)

### grado de condicion s-d + precio fob usd + seller type + toggle auction/buy-it-now/live  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Tarjeta de listing de exportacion (en.guazi.com): ancla por grado de condicion y precio FOB, no por estimacion

### sourcing a medida + inspeccion 300pt + garantia accident/flood-free + shipping + aduanas  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Pagina de dealers internacionales en.guazi.com/dealerships (propuesta mayorista B2B)

### contadores de inventario + flujo find- bid- deposit- win- 72h confirm- export  ·  (1 empresas lo colocan)
- **Guazi (瓜子二手车) / Chehaoduo Group**: Home y flujo de compra del sitio de exportacion en.guazi.com

### ex-showroom price + on-road por ciudad + emi editable  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Cabecera de la ficha de Coche Nuevo, geolocalizado con selector de ciudad; primer bloque arriba

### key specs  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Card resumen escaneable bajo el precio en la ficha de modelo

### variantes  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Tabla de variantes con checkbox Compare por fila

### specs completos  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Tab 'Specs' / acordeon por categoria (Engine, Dimensions, Safety, Features, Connected)

### expert review  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Seccion editorial de la ficha, autoria de probador propio

### user ratings + popular mentions por topico con conteo  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Prueba social a mitad de la ficha (Looks/Comfort/Mileage/Engine/Space/Price)

### comparador con rivales  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Seccion 'comparison with similar cars' + herramienta /compare-cars

### fair market price + rango  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Pantalla de resultado de la calculadora de valoracion, encadenada a CTA 'Sell My Car' (lead)

### precio + ahorro + ano/km/fuel/transmision + vendedor + owner count + sello ai expert  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Card de cada listing en resultados de Used Car Marketplace; filtros laterales (budget/body/collection)

### market share por marca top-10 modelos production/sales/export  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Automobile Industry Dashboard publico (pantalla de inteligencia SEO, separada de producto; fuente SIAM)

### rc/owner/seguro/puc  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Ficha de verificacion por matricula en la RTO tool; puerta a challan/service-history/health-check

### usados recomendados del mismo modelo  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Pie de la ficha de Coche Nuevo (puente nuevo->usado, conversion)

### leads consumer intelligence virtual showroom  ·  (1 empresas lo colocan)
- **CarDekho (Girnar Software Pvt Ltd / CarDekho Group)**: Fuera de la UI de consumo: apps/cloud de dealer y dashboards OEM (no en la ficha publica)

### price evaluation  ·  (1 empresas lo colocan)
- **Standvirtual**: 5 superficies oficiales (Netguru): Listing Page (resultados), Ad Details (ficha, junto al precio), Posting Form (al crear anuncio), My Ads (mis anuncios) y Sourcing Insights (profesional)

### etiqueta dentro da m dia  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — directamente junto/bajo el precio (verificado en vivo)

### hist rico de precio  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — junto al precio

### specs del veh culo  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — pestaña 'Especificações técnicas'

### garant a + hist rico + inspecci n  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — pestaña 'Estado e histórico' + bloque 'Verifique antes de comprar'

### servicios del vendedor  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — bloque 'Principais serviços do vendedor'

### simulador de financiaci n  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — dentro del anuncio (profesionales seleccionados; Santander Consumer/Cofidis)

### reputaci n del vendedor  ·  (1 empresas lo colocan)
- **Standvirtual**: Ad Details — bloque 'Informações sobre o vendedor'

### resultado del valuador  ·  (1 empresas lo colocan)
- **Standvirtual**: Pantalla de resultado de /avaliacao-do-carro (tras wizard de 2 pasos)

### sales-velocity + demanda por modelo  ·  (1 empresas lo colocan)
- **Standvirtual**: Portal de profesional (gated: contapessoal / portal-insights.standvirtual.com) + Sourcing Insights

### posici n del anuncio en b squeda  ·  (1 empresas lo colocan)
- **Standvirtual**: Portal de profesional — por anuncio

### perfil del comprador  ·  (1 empresas lo colocan)
- **Standvirtual**: Portal de profesional — tier Standard+

### autoiq  ·  (1 empresas lo colocan)
- **Standvirtual**: Portal de profesional / app AutoIQ (gated)

### insights de mercado abiertos  ·  (1 empresas lo colocan)
- **Standvirtual**: Diário Automóvel (editorial SEO, separado del per-vehículo)

### car valuation  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Página dedicada /car-valuations con selector de MODO arriba + form Make->Model->...; logo 'Supported by RedBook'; CTA cruzado a Instant Offer y Advertise

### priceassist  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Panel dentro del flujo de venta del member (trade-off precio<->velocidad)

### inspecci n / confianza  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Badge 'blue shield' en la ficha + report bajo pestaña 'Vehicle reports' dentro de 'Car details' (gratis de ver)

### specs del veh culo y reviews  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Ficha de detalle (pestañas Car details) para usado; Research/Showroom para coche nuevo (score /100, Compare cars, filtros Lifestyle/Body/Makes/Price)

### inteligencia de mercado dealer  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Dashboard LiveMarket dentro de AutoGate; weekly report de pricing opportunities + underperforming listings + benchmarking

### sourcing dealer  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Acquire: data junto a cada listing + pantalla Find Opportunities + analytics dashboard

### asistencia ia al dealer  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Sobre la ficha de lead/cliente en AutoGate (Gemini)

### audiencia/intenci n oem  ·  (1 empresas lo colocan)
- **carsales (carsales.com.au)**: Portal self-serve mediahouse 'Ignition' (insights por categoría) + dashboards de campaña (attribution CAPI)

### tasador  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: tasacion.autoscout24.es / autocasion.com/tasacion-de-coches: una pantalla con 'Asi funciona' debajo; salida = 3 preguntas-respuesta (valor de mercado / a que precio vender / que precio obtendre)

### etiqueta de precio price-to-market + rango de mercado + mediana  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: badge AL LADO del precio; filtro por etiqueta en el buscador/listado

### historial de precios del anuncio + alertas de precio  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: boton 'Historial de precios' junto al precio; alertas de similares

### datos basicos  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: bloque de especificaciones; facetas en el buscador

### historial de confianza  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: bloque de historial/estado del vehiculo

### cuota de financiacion / leasing  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Ficha de anuncio: CTA 'con financiacion'/'con leasing' (cuota mensual)

### valoraciones del concesionario + horario + ubicacion  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Tarjeta del vendedor en la ficha + paginas del directorio de concesionarios

### catalogo de specs + precio por version  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Autocasion 'Fichas tecnicas y precios' + Diccionario del motor

### leads tasa de conversion call tracking ia whatsapp ia multipublicacion ferias virtuales  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Area privada del profesional (B2B)

### tendencias de mercado days-to-sell modelos mas buscados precio medio por segmento forecasting  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Car Digital Track / portal-insights.sumauto.com (backend de insights gated, sin rutas publicas)

### days-to-sell ranking mas buscados precio medio top-10 precio por etiqueta  ·  (1 empresas lo colocan)
- **Sumauto (SUMAUTO MOTOR S.L.)**: Informes publicos de mercado (notas de prensa/blog) como activo de marca/lead-gen

### vin + model year  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Cabecera del Decoder web: dos campos (VIN, Model Year opcional 'si se entra, ignora el ano del VIN') + boton; unica puerta de entrada

### plant information  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Seccion dedicada AL FINAL de los resultados del decoder web ('Plant Information')

### engine / mechanical / battery  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Grupos colapsables por categoria en la ficha del decoder, uno por GroupName del catalogo

### exterior / dimensiones / body / truck / bus / trailer / motorcycle  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Grupos especificos por tipo de vehiculo; solo aparecen los relevantes al VIN decodificado

### active safety system  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Bloque 'Active Safety System' con sub-grupos (Forward Collision, Lane & Side Assist, Lighting, Backing Up & Parking), un check por feature

### passive safety  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Bloque 'Passive Safety System' / 'Air Bag Location'

### error code / error text / suggested vin / possible values  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Encabezado del resultado: estado de decodificacion + VIN corregido sugerido si el check-digit falla

### atributos crudos  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Respuesta de la API DecodeVin (estructurado) o DecodeVinValues (flat) - para integracion, no UI

### lote de vins  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Endpoint DecodeVINValuesBatch - procesamiento masivo backend (input vin,modelYear;vin,modelYear;...)

### fabricante / wmi / planta / documentos 565-566-586  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: MID: pantallas Organization, WMI, Equipment Plants, Part 565/566, Part 586 (Replica)

### makes / models / vehicle types / variables  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Endpoints de listado (GetAllMakes, GetModelsForMake*, GetVehicleVariableList) que alimentan dropdowns/cascadas

### canadian dimensions  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Pantalla Canadian Vehicle Specifications: seleccion Year/Make/Model -> tabla de medidas (metrico o US)

### modificadores  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Pantalla Modifier Search del MID

### db completa de vin decode  ·  (1 empresas lo colocan)
- **NHTSA vPIC (Product Information Catalog and Vehicle Listing)**: Pagina Downloads: backup MS SQL Server (.bak) / PostgreSQL (plain/custom) restaurable local, mensual

### resumen de hallazgos found  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Rejilla de tiles-contador en el top del informe (patrón Summary Cards)

### t tulo actual  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Title History' → subtabla 'Current Title Information'

### hist rico de t tulo  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Title History' → subtabla 'Historical Title Information'

### brands  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Title Brand Information' — checklist completo de brands

### od metro + flag overdriven  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Odometer Reading' — chart de tendencia + tabla

### junk & salvage  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Junk & Salvage Records' — tabla

### insurance / total loss  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Insurance Records' — tabla + disclaimer total-loss

### junk/salvage/total-loss unificado  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Sección 'Junk/Salvage/Total Loss' (layout VINData)

### nmvtis consumer access product disclaimer + glossary + data sources  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: Footer del informe (obligatorio en todo informe NMVTIS)

### verificaci n de t tulo pre-emisi n  ·  (1 empresas lo colocan)
- **NMVTIS / VehicleHistory.gov**: State Web Interface (SWI) — Integrated / Single VIN Inquiry / Batch (no UI de consumidor)

### historial per-veh culo  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Informe de un Vehículo (PDF) — secciones verticales: Datos del titular · Identificación · Seguro Obligatorio · ITV · Bajas · Cuentakilómetros · Cargas · Información técnica · Titulares · Medioambiental · Seguridad

### impedimentos/incidencias r pidas + fecha 1 matriculaci n  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Informe Reducido (gratis) — caja de matrícula en sede electrónica / app miDGT

### cargas o grav menes aislados  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Informe de Cargas — sección dedicada del informe

### parque agregado  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Panel de datos del parque de vehículos — cuadro de mando interactivo con drill nacional→autonómico→provincial→municipal e histórico

### matriculaciones / transferencias / bajas unitarias  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Microdatos MATRABA — ficheros ZIP/.txt de ancho fijo, frecuencia diaria y mensual (descarga libre en DGT en cifras)

### censo municipal completo de veh culos  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Fichero PADRÓN — descarga semestral (marzo/septiembre) para ayuntamientos/diputaciones

### matr cula distintivo ambiental domicilio de todos los veh culos  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: Fichero ZBE — listado diario vía interfaz DGT 3.0 para municipios con Zona de Bajas Emisiones

### tablas series hist ricas y narrativa anual  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: DGT en cifras + Anuario Estadístico General (Excel/PDF/HTML/TXT)

### consulta program tica per-veh culo  ·  (1 empresas lo colocan)
- **Dirección General de Tráfico (DGT)**: INTV Web Service — informe en PDF idéntico al del ciudadano, en lote, con certificado + interés legítimo

### matriculaciones turismos  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Cifras Clave -> 'Matriculaciones Turismos y Todoterreno': 4 vistas canónicas (últimos 12 meses / mes+acumulado / top del mes / top del año). Fuente IDEAUTO citada bajo cada tabla

### matriculaciones vcl e industriales/autobuses  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Cifras Clave, subsecciones por tipo de vehículo con la misma estructura de 4 vistas

### producci n y exportaci n + mapa de f bricas  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Cifras Clave -> 'Producción y exportación', incluye MAPA DE FÁBRICAS interactivo (planta x modelo x propulsión BEV/PHEV/HEV). Fuente ANFAC

### cifra mensual + variaci n + ranking superventas  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Nota de prensa (página HTML fechada por mes) con tablas embebidas + PDF; cada actualización engendra una nota (patrón SEO/timeline)

### indicadores compuestos de electromovilidad + puntos de recarga por potencia/ccaa + inoperativos  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Barómetro Electromovilidad (PDF trimestral) + presentación en evento; separado del dato bruto

### edad media del parque antig edad y etiqueta ambiental por ccaa  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Parque Vehículos (PDF anual ANFAC-IDEAUTO sobre datos DGT)

### saldo/exportaciones/importaciones de automoci n  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Comercio Exterior / Balanza Comercial de la Automoción (PDF mensual)

### cuota modal log stica y vol menes  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Logística (PDF anual + informes específicos por modo: carretera, ferroviario)

### facturaci n empleo i+d aportaci n al estado pib  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Informe Anual (PDF); foto macro del sector

### kpis objetivo 2030  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Plan España Auto 2030 (PDF + presentaciones por CCAA: Cataluña, Navarra)

### indicador va/vc y benchmark internacional  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Publicaciones -> Barómetro Vehículo Autónomo y Conectado (PDF anual, 'único en Europa')

### gobernanza miembros cuentas  ·  (1 empresas lo colocan)
- **ANFAC (Asociación Española de Fabricantes de Automóviles y Camiones)**: Portal de Transparencia (quiénes somos, junta directiva, comité de dirección)

### estado de tax  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Semaforo #1, top de la results page de vehicleenquiry.service.gov.uk: texto grande 'Taxed until {fecha}' o 'SORN' — lo primero y mas prominente

### estado de mot  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Semaforo #2, junto al de tax: 'MOT valid until {fecha}' / 'No MOT'. Los dos estados regulatorios encabezan la pagina

### atributos del vehiculo  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Panel 'Vehicle details / additional vehicle details' debajo de los semaforos

### color  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Oculto en el canal publico (solo por contacto directo/V888) — decision de privacidad/antifraude

### titular nombre direccion entitlements endorsements  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: NO en UI publica; gated tras KADOE/ADD/V888 con reasonable cause + reason code + fee — patron de dato sensible bajo llave

### historial mot  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Servido por DVSA (no DVLA): lista de tests con fecha/resultado/odometro y rfrAndComments por test

### schemas de dato para desarrolladores  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Developer portal: cada API en su pagina OpenAPI versionada (v1.2.0...) con request/response, ejemplos, codigos de error, rate limits

### gating de acceso  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Flujo de onboarding explicito: VES = self-service API key; KADOE/ADD = onboarding + JWT + contrato + reason code + fee

### consistencia visual  ·  (1 empresas lo colocan)
- **DVLA (Driver and Vehicle Licensing Agency)**: Toda la UI publica sigue el GOV.UK Design System (semantica, accesibilidad AA, minimalismo institucional, cero ruido)

### marca + modelo  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: titulo grande en cabecera + Overzicht > seccion acordeon 'Algemeen' (con codigos EU D.1/D.3)

### identidad/homologacion  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > 'Algemeen', cada fila con codigo comunitario EU y boton tooltip 'Meer informatie'

### numero de propietarios  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > 'Algemeen' (dato NO presente en open data)

### fechas apk / eerste toelating / tenaamstelling / inschrijving en nl  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > seccion acordeon 'Vervaldata en historie'

### pesos y capacidades de arrastre  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > seccion acordeon 'Gewichten' (codigos F.1/F.2/F.3/O.1/O.2)

### juicio antifraude de cuentakilometros  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > seccion acordeon 'Tellerstanden' (inline, con texto explicativo del veredicto)

### estado legal  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > seccion acordeon 'Status van het voertuig'

### recalls / terugroepacties  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: Overzicht > seccion acordeon 'Terugroepacties' (con aviso si hay abiertas)

### consumo y co2 potencia ruido autonomia ev  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: pestaña 'Motor & Milieu' > secciones 'Motor' / 'Milieuprestaties' / 'Uitstoot'

### emisiones  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: pestaña 'Motor & Milieu' > 'Milieuprestaties' / 'Uitstoot'

### tecnico y por eje  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: pestaña 'Technisch' > 'Eigenschappen' + sub-secciones 'As 1'/'As 2'

### fiscal  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: OVI: pestaña 'Fiscaal' [A — derivada del modelo de datos; no capturada a nivel de etiqueta por redireccion del navegador compartido]

### datos en bruto + endpoint api + columnas/data dictionary  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: Pagina de dataset Socrata (opendata.rdw.nl/.../{id}): grid filtrable + panel About (licencia CC0) + botones Visualize/Export/API con SoQL

### detalle de recall y de defecto apk  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: Datasets Terugroep_actie / Gebreken, enlazados desde el registro base via columnas api_* (expansion por relacion)

### tarifas de servicios de pago  ·  (1 empresas lo colocan)
- **RDW (Rijksdienst voor het Wegverkeer / Netherlands Vehicle Authority)**: Dataset Producten Catalogus (staatscourant_indeling/tariefclustering/omschrijving/eenheid/tarief)

### estado global del veh culo  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Informe Reducido (gratis) = semáforo de 3 estados (Sin incidencias / Con avisos / Con incidencias) — veredicto de un vistazo previo al informe de pago

### datos del titular + cotitulares + renting  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 1 'Datos del Titular' (arriba del Informe Completo PDF)

### identidad t cnica  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 2 'Identificación del Vehículo' del Completo

### seguro obligatorio  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 3 del Completo

### itv  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 4 'ITV' del Completo — tabla histórica por inspección

### bajas  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 5 'Historial de Bajas' del Completo

### kilometraje  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 6 'Historial de Lecturas del Cuentakilómetros' — tabla fecha · lectura · origen (ITV/declaración/taller)

### denegatoria  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 7 'Indicador Vehículo con Denegatoria'

### cargas  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 8 'Cargas o Gravámenes' — bloque crítico para compraventa

### datos t cnicos  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 9 'Información Técnica'

### historial de titulares  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 10 del Completo

### medioambiental  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 11 'Información Medioambiental'

### seguridad  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Sección 12 'Seguridad del Vehículo'

### secciones condicionales  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Patrón clave: 'si no aparece la sección, el vehículo no tiene anotación' → la AUSENCIA de bloque comunica 'limpio'

### datos del propio coche  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Panel privado del titular en miDGT (Mis trámites > Vehículos)

### parque / matriculaciones / transferencias / bajas  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Dashboards interactivos 'DGT en cifras' + microdatos descargables (plano agregado, separado del per-vehículo)

### identidad t cnica densa de homologaci n  ·  (1 empresas lo colocan)
- **DGT — Informe de Vehículo (Dirección General de Tráfico)**: Fichero MATRABA (ancho fijo .txt en ZIP) — feed estructurado por matriculación

### modelo puissance fiscale propietario actual 1a matriculacion y veredicto de situacion administrativa  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 0 'Synthese' (abre el informe): 2 columnas, 4 bloques h4; veredicto con icono de alto contraste ('Rien a signaler' / anomalia)

### 26 caracteristicas tecnicas con su codigo de carte grise + vin ptac cylindree puissance co2 energia places  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 1 'Vehicule' -> 'Caracteristiques techniques': tabla de 3 columnas (etiqueta · codigo oficial · valor), 26 filas

### titular anonimizado fecha de 1a matriculacion y fecha del certificado de matriculacion actual  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 2 'Titulaire et Titre': lista etiqueta->valor + sub-bloque 'Certificat d'immatriculation'

### gages oppositions declare vole declarations valant saisie suspensions estado del ci  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 3 'Situation administrative': 2 columnas x 3 secciones h3; cada una con veredicto NON/OUI de alto contraste + enlace a la norma legal (service-public.fr) + detalle por registro

### cronologia de operaciones del registro siv  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 4 'Historique' -> 'Historique des operations en France': tabla Date | Operation

### historial de controles tecnicos naturaleza resultado y kilometraje en cada paso  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 5 'Controles techniques': tabla Date | Nature | Resultat | Kilometrage

### evolucion del kilometraje para detectar manipulacion/rollback  ·  (1 empresas lo colocan)
- **HistoVec**: Pestana 6 'Kilometrage': serie temporal aislada (fecha + km) - senal anti-fraude estrella en su propia pestana

### marca modelo ano motor combustible masa plazas fechas de matricula  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Informacje' (Informacion) — primera pestana, identidad fria del vehiculo

### numero y tipo de propietarios por tramo voivodato de matricula  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Os czasu' (Linea de tiempo) — eje cronologico de cambios de titularidad, sin PII

### inspecciones tecnicas y odometro/przebieg por inspeccion + control policial  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Os czasu' — lecturas datadas junto a cada ITV; serie temporal que delata el retroceso; sustitucion de cuentakm como flag

### oc y estado legal  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Os czasu' (estado legal) + base nacional de robo

### szkody istotne  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Os czasu' — eventos de dano

### baja robo+recuperacion retirada temporal de circulacion  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Os czasu' (estado legal) + tabla de riesgos

### tabla de riesgos extranjeros + odometro extranjero  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Vista 'Dane zagraniczne' / Tabela ryzyka — FLAGS verde/rojo (rojo = confirmado), overlay autoDNA

### fotos de itv  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Nueva seccion 2026 (piloto SKP) [no verificado >=2]

### 69 campos tecnicos anonimizados filtrables por voivodato + rango de fechas  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: CEPiK Open API /pojazdy — superficie de analitica, no de consulta ciudadana

### censo del parque por marca/combustible/voivodato/ano  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: API /slowniki/{nazwa-slownika} — campos klucz-slownika + liczba-wystapien

### datos del propio vehiculo + multas + puntos karne  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Moj Pojazd / mPojazd en la app mObywatel (autenticado con Profil Zaufany)

### oc itv+proxima plazas masa odometro de la ultima itv de un autobus  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Bezpieczny Autobus (consulta por matricula)

### enlace al informe completo de pago  ·  (1 empresas lo colocan)
- **Historia Pojazdu (gov.pl) / CEPiK**: Upsell a autoDNA desde la tabla de riesgos del propio servicio gov

### niv / placa / folio de constancia  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Cabecera del formulario de Consulta Ciudadana: un campo + captcha + botón Consultar; única puerta de entrada pública

### sem foro de estatus de robo  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Indicador de color destacado del resultado — lo primero y más visible, resume el veredicto antes del detalle

### datos del veh culo  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Pestaña 1 'Datos del vehículo' — ficha de identidad para cotejar contra documentación física

### reporte de robo de fiscal a  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Pestaña 2 'PGJ' — reportes de las Fiscalías estatales

### reporte de robo a aseguradoras  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Pestaña 3 'OCRA' — reportes del sector asegurador, independiente de la pestaña PGJ

### constancia / nci exportable  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Botón 'Exportar PDF' (abajo a la derecha) o Ctrl+P → PDF con NCI y datos de registro

### estatus en tiempo real  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Arco de lectura RFID/LPR: el chip (NCI) y la placa se leen al paso del vehículo → alerta automática a la autoridad

### identidad f sica completa + propietario + grav menes + movimientos  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Portal autenticado de Sujetos Obligados/Entidades (:8046) + web service REST de integración (vista completa reservada a autoridad/sujetos obligados)

### documento legal vinculado al veh culo  ·  (1 empresas lo colocan)
- **REPUVE — Registro Público Vehicular**: Calcomanía REPUVE azul con logos dorados en el parabrisas + chip RFID intransferible (que se destruye al despegar)

### make/model/colour/fueltype/fecha de matriculacion  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: strip de identidad en cabecera (matricula estilo placa)

### mot expiry / proximo mot due  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: resumen de estado bajo la identidad (top)

### safety recall pendiente  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: banner prominente superior

### fecha del test + badge passed/failed  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: encabezado de cada tarjeta de test (lista cronologica inversa)

### odometervalue + mottestnumber  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: cuerpo de cada tarjeta de test

### defectos dangerous+major  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: lista 'Repair immediately' dentro de la tarjeta del test

### defectos minor+advisory  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: lista 'Monitor and repair if necessary' dentro de la tarjeta

### test location  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: detalle del test, tras introducir nº V5C de 11 digitos

### flag de clocking  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: MOT history: resaltado automatico en la secuencia de mileage

### taxstatus + taxduedate  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: VES UI: panel/semaforo izquierdo (Tax) — patron '2 semaforos'

### motstatus + motexpirydate  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: VES UI: panel/semaforo derecho (MOT)

### make + colour  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: VES UI: paso de confirmacion 'Is this the right vehicle?' antes del detalle

### yearofmanufacture enginecapacity co2emissions fueltype eurostatus realdrivingemissions typeapproval wheelplan revenueweight dateoflastv5cissued monthoffirstregistration markedforexport  ·  (1 empresas lo colocan)
- **GOV.UK MOT History & DVLA Vehicle Enquiry**: VES UI: panel expandible 'additional vehicle details'
