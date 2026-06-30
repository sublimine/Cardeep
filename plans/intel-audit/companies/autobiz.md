# Auditoría atómica — autobiz (autobiz Group)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos/valoración e inteligencia de automoción. Web corporativa: https://corporate.autobiz.com/ · Web producto profesionales: https://office.autobiz.com/ · B2C: https://vendre.autobiz.fr/ (redirección desde www.autobiz.fr) · Subdominios técnicos: `valuation.autobiz.com` (motor de valoración, cerrado) y `pricing.autobiz.com` (portal de login).
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva de corporate.autobiz.com (catálogo de 22 productos + about-us + press releases), office.autobiz.com (suite autobizOffice de productos profesionales), vendre.autobiz.fr (B2C), renderizado JS con Playwright de `valuation.autobiz.com` y `pricing.autobiz.com`, + verificación cruzada con prensa (JATO Dynamics, IFRS13/Chappuis Halder) y agregadores (LinkedIn, PitchBook, CB Insights, Tracxn, LeadIQ).
> Convención: [V] = verificado leyendo la fuente · [A] = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **autobiz** (autobiz Group / autobiz Corporate) | [V] |
| Categoría | Datos e inteligencia de automoción centrada en **vehículo de ocasión (VO)**: valoración estadística de mercado, digitalización/industrialización de la reprise (trade-in), inteligencia de stock y precios, remarketing B2B, estudios de mercado de anuncios clasificados | [V] |
| Fundación | **2004** | [V — about-us + búsqueda] |
| HQ | **Courbevoie / región de París, Francia** | [V — búsqueda LeadIQ/agregadores; about-us no lo escribe literal] |
| Fundadores | **Christophe Louvard** y **Daniel Urbah** (2004); **Emmanuel Labi** se une en 2005 como tercer cofundador | [V] |
| CEO / Presidente | **Emmanuel Labi** (nombrado Presidente a inicios de **2022**) | [V] |
| Comité de dirección | Carlos Liñán (Deputy CEO) · Grégory Reboux (COO) · Bertrand Chataing (Chief Sales & Development Officer) · Marie-Pascale de Matharel (Directora RR.HH.) · Cédric di Luca (Managing Director **EasyReprise**) | [V — about-us] |
| Owner / accionariado | **Stellantis Group = accionista mayoritario** (con "independencia operativa" declarada). Partnership estratégico con Stellantis (ex-PSA) desde **2017** | [V — about-us] |
| Subsidiaria/marca | **EasyReprise** (reprise/buyback) | [V] |
| Empleados | **~280** (búsqueda) / **320 a 1-ene-2024** (about-us); equipos Big Data & Algorítmica >40 personas | [V — nota variación de cifra] |
| Facturación | **€130M (2023)**; supera **€100M**; 20º aniversario en **2024** | [V] |
| Oficinas / presencia | Subsidiarias en **Francia, Alemania, Italia, España-Portugal, Túnez**; oficinas citadas en **París, Berlín, Valencia, Milán** | [V] |
| Escala de datos | **15.000M+ anuncios clasificados** recopilados desde **2006**; **10.000M+ precios observados**; **50M+ expedientes de reprise**; 250.000 profesionales / **6.500 puntos de venta** monitorizados | [V] |

### Hitos corporativos [V]
- **2004** Fundación; crea la primera base de datos de profesionales de la distribución automovilística.
- **2007** Pionera en valoración de VO mediante **algoritmos big data**.
- **2010** Líder europeo en generación de **leads de reprise**.
- **2017** Partnership estratégico con **Stellantis (ex-PSA)**.
- **2020** Lanzamiento de la suite **autobizOffice**.
- **2024** 20º aniversario; facturación > €100M.
- **2026 (31-mar)** Partnership estratégico con **JATO Dynamics** (identificación VIN-a-specs + "specs-to-valuation").

### Clientes objetivo (7 segmentos declarados) [V]
1. Subastadores y empresas de **remarketing B2B**.
2. **Banca, finanzas y seguros**.
3. **Distribuidores** (concesionarios/redes).
4. **Fondos de inversión y consultoras**.
5. **Fabricantes (OEM)**.
6. **Marketplaces e internet pure players**.
7. **Alquiler** corto y largo plazo (rent-a-car / renting).
8. **Consumidores B2C** vía `vendre.autobiz.fr` / EasyReprise (canal aparte). [V]

### Clientes nombrados [V — home corporate]
Stellantis · BMW · Renault · Toyota · Volkswagen · Volvo · Nissan · Smart · ALD · Arval · BCA · Adevinta · Europcar / **Europcar Mobility Group** · Point S. Declara: **7 de los 10 mayores OEM europeos** (Cockpit), 10+ fabricantes, 300+ grupos de distribución.

---

## 2. Cobertura

### Geográfica (varía por producto) [V]
- **Núcleo valoración / mayoría de productos**: **22 países/mercados europeos** (cifra dominante; el press de IFRS13 cita "23" — variación menor).
- **Crawling/estudios de mercado (Joreca)**: **37 países** en 5 continentes; **500+ sitios** analizados al mes.
- **autobizAPI**: datos crawleados en **20 países**, **350 fuentes de datos**.
- **autobizAdsScan**: **6 países** (Francia, Alemania, Italia, España, Países Bajos, Bélgica); 50 infomediarios; 5M VO/día.
- **autobizTrade** (plataforma B2B): **10 países** europeos.
- **Noa** (IA de daños): **solo Francia**.
- **autobizClic2Sell**: Francia (alcance nacional vía red logística de socios).

### Escala de procesamiento [V]
- **~2M anuncios clasificados analizados a diario** (profesionales + particulares), con deduplicación.
- **20M "lecturas de precio" procesadas al día** (varias observaciones de precio por anuncio/tiempo).
- **40.000+ inventarios** analizados a diario; **15.000+ referencias valoradas al día**; **2 actualizaciones de valoración al mes** (autobizMarket).
- Histórico: **17-20 años** de datos de VO.

### Scope de vehículos [V/A]
- **Vehículo de ocasión (VO)** como núcleo absoluto; valoración de **VN y futuro/residual** en autobizFuture y precios VN en autobizPricingPower. [V]
- Atributos por vehículo: marca, modelo, versión, energía/combustible, kilometraje, fecha de matriculación. [V]
- **No se mencionan** explícitamente motos, LCV ni vehículo industrial como tipos cubiertos (foco turismo). [A — ausencia, ver Gaps]

---

## 3. Productos + campos atómicos

Catálogo completo: **22 productos enumerados en corporate.autobiz.com/our-products** + suite **autobizOffice** (office.autobiz.com) que añade `autobizClic2Buy`, `autobizAdsScan`, `autobizTrade`, `autobizPilot`, `Noa`, `autobizAcademy`. Total ~28 productos/módulos. Organizados por función.

### — Bloque VALORACIÓN / DATOS —

### 3.1 autobizMarket — herramienta profesional de valoración (producto estrella) [V]
"La solución de reprise más fiable de Europa"; el motor `autobizMarket®` alimenta también el B2C. Identificación **por matrícula** + sistema de referencia VO exclusivo (meta-repositorio). Campos:
- **Valor B2C** (profesional → particular, retail).
- **Valor Network** (venta por distribuidores de la marca).
- **Valor C2C** (entre particulares).
- **Valor B2B** (trade/wholesale).
- **Valor de reprise** (trade-in).
- **"10 datos de mercado por valor"** que incluyen: rotación/turnover de stock, depreciación, valor B2B, periodos de reprise.
- **Tiempos de rotación / turnover**.
- **Posicionamiento de precio vs competidores** (local / regional / nacional).
- **Número de vehículos a la venta** (oferta de mercado).
- **Distribución de vendedores/concesionarios** (mapa).
- **Indicadores de transacciones pasadas**.
- **Análisis de stock en tiempo real** (rotación, calidad del anuncio, posicionamiento).
- **Sourcing** vía descarga de listados (valoración masiva).
- **Alertas** de oportunidades de mercado configurables.
- Grid de costes personalizado para fijar reprise.

### 3.2 autobizAPI — valores de mercado vía API [V]
Webservices de arquitectura **microservicios** (REST), compatible con cualquier base de datos. **99,5% disponibilidad media**. Datos crawleados en 20 países, 350 fuentes, 15B+ precios desde 2004. Devuelve:
- **Valores B2C / B2B**.
- **Future value** (valor futuro/residual).
- **Trade-in value** (valor de reprise).
- **Stock turnover / rotation** (rotación).
- **Vehicle attractiveness** (atractividad del vehículo).
- **Datos de ventas de los últimos 12 meses**.
- Acceso al **repositorio de vehículos autobiz** y al **directorio de concesionarios** (dealer directory).
- **Identificación instantánea** del vehículo independientemente de la BBDD del cliente.
- Inputs: **VIN**, **matrícula**, **texto/descripción**, make/model.
- Valores **personalizados** a medida del modelo de negocio del cliente.

### 3.3 autobizVIN — identificación por VIN [V]
"Identifica tus VO sin riesgo." Input = **número de serie (VIN)**; identificación en 3 pasos. Devuelve:
- Decode de **VIN**.
- **Versión / acabado** (trim) exacto.
- **Especificaciones del motor**.
- **Caja de cambios / transmisión**.
- **Equipamiento de fábrica** instalado.
- **Equipamiento opcional**.
- **País de origen**.
- **Fecha de producción**.
- Características y detalles del vehículo.
- (Desde 2026: enriquecido con taxonomía de **JATO Dynamics**, VIN-to-spec.)
- Multilingüe (EN/DE/FR/IT/ES/PT).

### 3.4 autobizDrag&Drop — valoración masiva por carga de fichero [V]
"Descarga y valora tus listados en pocos clics." Flujo: subir fichero (drag&drop) → identificación + valoración automática en segundos → recuperar fichero valorado. Devuelve:
- **4 valores automáticos por VO**: **Network, B2C, C2C y reprise (trade-in)**.
- Indicadores de mercado: **B2C Retail market value**, **C2C Retail rotation market value**.
- **Valores personalizados**: trade-in value, modelo de venta B2B.
- Identificación estandarizada vía **meta-repositorio internacional** autobiz.
- Cobertura 22 mercados europeos.

### 3.5 autobizFuture — valores residuales / futuros [V]
"Anticipa tus precios de valor residual con el método más claro y transparente en 22 países." Para banca/finanzas/leasing. Campos:
- **Proyecciones de valor residual** por versión y modelo.
- **Estimaciones de valor futuro** basadas en patrones de depreciación históricos por versión.
- **Factores de corrección** ajustables: crecimiento económico, evolución del precio del combustible, apreciación/depreciación de segmento, **timing de facelift** de modelo.
- Cumple **IFRS**; validado por el **BCE (ECB)**.
- Entrega: **importación de listados → fichero valorado en minutos** (batch).

### 3.6 autobizBarometer — barómetro de mercado [V]
"Anticipa la evolución del mercado antes que tus competidores." 17 años de histórico, 22 países, **30+ KPIs personalizables**. 3 categorías:
- **UC Request (demanda VO)**: progreso de búsquedas de clientes en internet → tendencias de demanda.
- **UC Offer (oferta VO)**: niveles de stock, antigüedad del inventario, tasas de rotación, composición vendedor profesional vs particular.
- **Price Developments (precios)**: precio medio de anuncios, cambios de valor de mercado, tendencias de depreciación, ajustes de precio de profesionales.
- Dashboard de señales de mercado más actualizadas.

### 3.7 autobizPortfolio — colateral automovilístico y riesgo [V]
"Estima el colateral automovilístico y monitoriza tus riesgos." Banca/finanzas/inversión/grandes grupos. Campos:
- **Valoración de cartera** de vehículos.
- **Fair value (valor razonable)** del stock.
- Cumplimiento **IFRS 13** (auditado por Chappuis Halder, 2017) y **directivas BCE**.
- **Stress tests** en máximo 5 días.
- Usa los ficheros del cliente "tal cual" (sin enriquecimiento previo).

### 3.8 autobizInsurance — auditoría de valores de mercado para seguros [V]
"Auditoría externa estándar de valores de mercado de seguro de auto." Creado con/para peritos. Campos:
- **Replacement value** (valor de reemplazo determinado por experto).
- **Standardised replacement value** (valor de reemplazo estandarizado de estudio de mercado).
- **Anuncios clasificados online** de vehículos similares como soporte.
- ~20 minutos ahorrados por expediente.

### 3.9 autobizCrossborder — potencial de exportación transfronteriza [V]
"Modelo de cálculo a medida que evalúa el potencial transfronterizo de todos tus vehículos." Output por vehículo (en minutos tras subir lista):
- **Valoración VO instantánea en los 22 mercados**.
- **Impuestos locales** (por jurisdicción).
- **Fiscalidad transfronteriza** (cross-border taxation).
- **Costes logísticos / de transporte**.
- **Cross-Border Potential Score** (puntuación de viabilidad de exportación).
- Reglas adaptadas a las especificidades del cliente, demanda local y pricing del cliente.

### — Bloque INTELIGENCIA DE STOCK / PRECIO —

### 3.10 autobizMyStock — posicionamiento del stock VO [V]
"Optimiza el posicionamiento de tu stock de VO." Actualización **diaria**. Campos:
- **20+ criterios** para evaluar el precio y la atractividad de marketing.
- **Controles de calidad del anuncio** (detecta anuncios sin fotos, precio desalineado, duración de publicación excesiva).
- **Scoring de marketing** + mecanismos de **alerta**.
- **Acceso a los stocks de otros profesionales de tu región** (inteligencia competitiva).
- **KPIs personalizables**.
- Ganancia observada: **−15 días de rotación**.

### 3.11 autobizPricingPower — seguimiento de precio vs competidores [V]
"Sigue los precios de tus vehículos en el mercado VO frente a los de tus competidores." VN y VO. Campos:
- **Dashboard 100% personalizable** vía **Tableau Software** (24/7).
- Definir **competidores** a seguir y **combinaciones edad/km**.
- **Actualización mensual**.
- "Visión de mercado imparcial."
- Usado a diario por 5 fabricantes.

### 3.12 autobizCockpit — KPIs de VO para redes (OEM) [V]
"Tus KPIs de VO más importantes en una interfaz amigable." Niveles jerárquicos: global → país (22) → grupo de distribución → punto de venta individual. KPIs:
- **Volúmenes de stock**.
- **Cifras de ventas**.
- **Turns (rotación de inventario)**.
- **Calidad del anuncio (ad quality)**.
- Histórico desde 2010. 80 supervisores de red (NSC) lo usan; 7 de 10 mayores OEM europeos.

### 3.13 autobizInterface — monitorización de remarketing de red [V]
"Optimiza el rendimiento de remarketing de tu red en tiempo real." Para OEM (10+ fabricantes, 300+ grupos, 22 países). Campos:
- **Monitorización de vehículos en tiempo real** en toda la red.
- **Análisis de precio** vs **valoración autobiz** (pricing dinámico).
- **Duración de publicación online** (listings online).
- **Visibilidad de inventario** de toda la red, configurable por nivel (coach VO, regional, sucursal).
- Ganancia: 5 días de rotación/año.

### 3.14 autobizPilot — optimización de estrategias de remarketing [V]
Centraliza la gestión de remarketing multicanal. Campos:
- **Asignación automática** de vehículos a canales de venta.
- **Optimización de precio** según rendimiento de remarketing, tendencias de mercado y objetivos de margen/rotación.
- **Recomendaciones inteligentes** de precio y método de venta.
- **Identificación de oportunidades de venta internacional** (10-15% de los vehículos).
- Niveles de automatización personalizables.

### 3.15 autobizTargeting — selección de compradores B2B [V]
"Herramienta de decisión operativa para seleccionar los compradores más relevantes." Dataset de 4M+ vehículos / 250.000 profesionales / 22 países. Campos por profesional/vehículo:
- **Make, model, rotación, precio de venta vs valor de mercado**.
- **Vehículos vendidos en los últimos 12 meses**.
- **Identificadores profesionales**: tax ID, afiliación de grupo, datos postales y legales.
- **Export para CRM** (matching con BBDD del cliente).

### 3.16 autobizAdsScan — sourcing de VO de alto margen [V]
"Detecta las mejores gangas en toda Europa." 5M VO/día, 50 infomediarios (Leboncoin, AutoScout24, Mobile.de, Coches.net, Milanuncios…), 6 países, **15 filtros**. Por anuncio:
- **Écart à la cote / valuation gap** = diferencia entre **valoración autobiz** y **precio publicado** (indicador de margen).
- **Filtro por diferencial de precio** (margen deseado).
- **Make / model**.
- **Energía / combustible**.
- **Kilometraje**.
- **Fecha/año de matriculación**.
- **Precio publicado**.
- **Vendedor profesional vs particular**.
- **Enlace al anuncio original**.
- **Filtros geográficos** (departamento/región/país).
- **Alertas por email** + **búsquedas guardadas**.

### — Bloque REPRISE / SOURCING / INSPECCIÓN —

### 3.17 autobiziFrame — módulo de reprise/valoración para web [V]
Módulo embebible "llave en mano y personalizable" en la web del concesionario (logo, colores, transfer values). Campos:
- **Identificación del vehículo del cliente**.
- **Input de estado del vehículo**.
- **Estimación de reprise automática**.
- **Lead capture**: First Name, Last Name, Phone, Email, Message.
- Resultados: +100% leads, 8-15% conversión, 2M+ leads/año, 200+ despliegues / 22 países.

### 3.18 autobizTradeIn — leads de reprise desde la web [V]
"Aumenta ventas y leads de reprise desde tu propia web." Campos:
- **Formularios online** personalizados (colores, logos, **elección de preguntas**).
- **Valor de reprise personalizado** (considera costes y política comercial del cliente).
- Módulos **a medida o off-the-shelf**.
- **Ofertas de reprise remotas**.
- **Vinculación de expedientes** a las herramientas de reprise de punto de venta.
- 2M leads (2022), 25.000 ventas de vehículos (2022), 200+ sitios / 22 países.

### 3.19 autobizGuaranteed — precios de reprise garantizados online [V]
"Impulsa tu e-commerce con precios online garantizados" en 22 países sin visita física. Campos:
- **Precio de reprise online garantizado**.
- Pricing **100% automático** o **validado por unidad de supervisión**.
- **Derecho de tanteo (right of first refusal)** para la red.
- **NPS medio 70**.

### 3.20 autobizClic2Buy — sourcing del tráfico de taller [V]
"Convierte el tráfico de tu taller en sourcing de VO" vía **QR**. Campos:
- **Códigos QR únicos por ubicación** (taller, parking, recepción).
- **Formulario de inspección de 200 checkpoints**.
- **Ubicación del cliente** dentro del concesionario.
- **Coste de reacondicionamiento declarado por el cliente**.
- **Oferta de reprise instantánea** (auto-calculada).
- **Teléfono** (entrega del link vía **SMS**).
- **Intención/estado del proyecto de reprise**.
- **Alerta en tiempo real** al escanear el QR; interfaz de leads.
- Integra con autobizCarcheck.

### 3.21 autobizClic2Sell — reprise 100% remoto [V]
"Reprise remoto para un recorrido 100% digital." Campos:
- **Formulario de tasación con 30+ preguntas**.
- **Workflow iniciado por SMS** (link al cliente).
- **Guía paso a paso** + **auto-guardado** (pausar/retomar).
- **Mensajería personalizable** (SMS/email).
- **Tracking de progreso** de la tasación.
- **Integración de valoración** con herramientas de pricing autobiz.
- **Oferta de compra opcional** emitida por autobiz.
- Conversión ~30%; 50% de particulares prefieren tasación remota.

### 3.22 autobizCarcheck — tasación/inspección VO digitalizada [V]
"Tus tasaciones de VO estandarizadas, digitalizadas y bajo control." Campos:
- Identificación: **decode de matrícula**, **decode de VIN**, **escaneo de permiso de circulación** (grey card, opcional).
- **Perfil mecánico** (condición).
- **Perfil de carrocería** (bodywork).
- **Detección y documentación de daños**.
- **Inventario de equipamiento**.
- **Costes de reacondicionamiento** (auto-calculados con grid de costes personalizado).
- **Recomendación de precio / precio final**.
- **Fotos del vehículo**.
- **Informe de tasación PDF** con marca.
- **Disparo de tasación** automático o manual según fecha de entrada en stock.
- Push directo a **autobizTrade** (remarketing) + **webhooks** a sistemas externos.
- Integra **Noa** (IA de daños).

### 3.23 Noa — tasación automática de daños por IA [V]
IA de detección de daños sobre fotos, basada en **Machine Learning** con partner **Monk AI (desde 2021)**; cada tasación mejora la IA. **Solo Francia**. Campos:
- **Tipo de daño** detectado.
- **Severidad del daño**.
- **Parte de la carrocería afectada** (marcada **sobre la foto** en el informe).
- **Coste de reparación**.
- **Coste de reacondicionamiento estimado** (según grid de costes propio).
- **Alerta de discrepancia** (coste declarado por el comercial vs detectado por IA) en el expediente Carcheck.
- **Análisis comparativo** lado a lado (declarado vs IA).
- **Monitorización del rendimiento de compradores** (recon declarado vs IA).
- Métricas: 60% de tasaciones la IA detecta daño igual o mayor; media **4 daños** y **€700 de recon** por tasación; carrocería = 45% del recon.

### — Bloque REMARKETING B2B / ESTUDIOS —

### 3.24 autobizTrade — plataforma de venta B2B (subastas) [V]
"Plataforma de venta B2B llave en mano." 10 países, red privada de dealers + compradores públicos + 4 subastadores socios. Campos:
- **Formatos de venta**: compra inmediata (precio fijo) · puja abierta (con/sin reserva) · **puja ciega (blind)** · pujas selladas · venta one-by-one · sesiones de venta agrupadas.
- **Precio de reserva**.
- **Tracking de pujas en tiempo real**.
- **Contraoferta inteligente** alineada con objetivos de margen.
- **Comparación de ofertas**.
- **Selección de audiencia** (solo dealers privados o toda la comunidad).
- autobiz actúa de **intermediario**. Margen extra medio **>€300/vehículo**; −10 días rotación; **cero coste de setup**.

### 3.25 JorecaPanel — base de datos de marketplaces [V]
"La referencia de los principales marketplaces del mundo." 15B+ anuncios desde 2006, 37 países, 500+ sitios/mes, 80+ clientes. Campos:
- **Cuota de mercado de anuncios** a nivel local por tipo de anuncio (precio, fotos, calidad de texto).
- **Conteo mensual de anunciantes profesionales por red**.
- **Tamaño de stock por región/provincia**.
- **Análisis de anunciantes e inventarios comunes entre sitios**.
- **Precio**, **nº de fotos**, **indicador de calidad de texto** por anuncio.
- Entrega vía dashboards en tiempo real. Usado en **5 fusiones (M&A)** de automoción desde 2019.

### 3.26 JorecaAdvertisers — base de datos de anunciantes [V]
"La única base de datos completa de anunciantes en internet." 37 países, **330.000+ profesionales** (auto + inmobiliaria), 40.000+ actualizados al mes. Campos:
- **Datos clave de inventario** (número y tipo de anuncios) por anunciante.
- **Cestas de gasto (baskets spent) por medio**.
- **+50 data points** (información de negocio, financiera o marketing).
- **Matching** con tablas internas de clientes/prospectos del cliente → integración CRM.
- Resultado: +30% de clientes potenciales en la 1ª implementación.

### — Bloque SERVICIOS —

### 3.27 autobizAcademy — formación VO [V]
Herramienta de formación para los oficios del VO (training academy). Sin campos de dato; servicio.

### 3.28 autobizCoaching — coaching de campo [V]
Equipos de campo autobiz que ayudan a mejorar el rendimiento de los concesionarios. Servicio de consultoría, sin campos de dato.

---

## 4. Metodología y fuentes de datos [V]
- **El "valor autobiz" es un valor de mercado 100% estadístico**, calculado automáticamente a partir de **precios realmente observados en el mercado** — no fijado por editor/experto.
- Base: **análisis diario de ~2M anuncios clasificados** publicados por profesionales y particulares, con **deduplicación**; **20M lecturas de precio/día**; **10.000M+ precios observados** históricos.
- **Triple valor de mercado**: **B2C** (profesional→particular), **Network** (distribuidores de la marca), **C2C** (entre particulares); más **B2B**, **reprise (trade-in)** y **future/residual value**.
- Técnicas: **principios matemáticos + Machine Learning**; equipos Big Data & Algorítmica >40 personas.
- **IFRS 13**: autobiz se declara **primera empresa de valoración de coches en cumplir IFRS13**; auditada por **Chappuis Halder** (fiabilidad, sinceridad, transparencia y auditabilidad → método "relevante y eficaz"); alineada con directivas del **BCE** para fair value de carteras.
- **Fuentes / infomediarios**: Leboncoin, Lacentrale, L'Argus, Ouest-France, AutoScout24, autoSélection, Paruvendu, autosphere, Mobile.de, Coches.net, Milanuncios. **350 fuentes** / **500+ sitios/mes**.
- **Partnership JATO Dynamics (31-mar-2026)**: JATO aporta base de **especificaciones + taxonomía** (identificación y descripción de vehículos, profundidad histórica); autobiz aporta modelos de valoración y previsión de residual → **framework "specs-to-valuation"**, VIN mejorado, dashboards combinados; en vivo con **Europcar Mobility Group**.
- **Partnership Monk AI (desde 2021)**: ML que alimenta Noa (detección de daños sobre foto); se retroalimenta con las tasaciones Carcheck.
- **Frecuencia**: valores de mercado **diarios** (autobizMarket: 2 actualizaciones/mes de la valoración); PricingPower **mensual**; MyStock/Cockpit **diario**; AdsScan **diario**; especificaciones enriquecidas vía JATO.
- Limpieza: MyStock/Market filtran anuncios sin foto, precio desalineado y duración excesiva.

---

## 5. Entrega [V]
- **Plataformas web/cloud (login `office-connect.autobiz.com` / suite autobizOffice)**: autobizMarket, MyStock, Cockpit, Carcheck, Clic2Sell, Trade, Pilot, Interface, etc. **7 idiomas**, 30.000+ usuarios.
- **API REST / microservicios (cloud, pago por uso)**: autobizAPI (99,5% disponibilidad), inputs VIN/matrícula/texto.
- **Módulos embebibles en web del cliente (iframe/widget)**: autobiziFrame, autobizTradeIn, autobizGuaranteed, Clic2Sell, Clic2Buy (QR). Host técnico probable: **`valuation.autobiz.com`** (cerrado al público, 403). [V host / A propósito]
- **Carga masiva de ficheros (batch)**: autobizDrag&Drop (fichero → valorado en segundos), autobizFuture (listados → valorado en minutos), autobizPortfolio (usa ficheros tal cual).
- **Dashboards BI**: **Tableau Software** (PricingPower); dashboards personalizados (Barometer 30+ KPIs, Cockpit jerárquico, MyStock).
- **Export CRM**: autobizTargeting, JorecaAdvertisers.
- **Integraciones DMS / herramientas de negocio**: **10+ integraciones**; **webhooks** (Carcheck).
- **Informe PDF**: Carcheck, informe de tasación Noa.
- **Plataforma de subasta B2B**: autobizTrade.
- **Canal B2C**: `vendre.autobiz.fr` (estimación gratis en 2 min → cita en punto socio → inspección → oferta firme → transferencia 48-72h); marca **EasyReprise**.

---

## 6. Precio
- **No público**. `pricing.autobiz.com` **redirige a login Auth0** (`login-office.autobiz.com`, universal-login, SSO "MyPeople") — portal cerrado, sin tarifas visibles. [V]
- Modelo = **suscripción** a la suite autobizOffice + **API pago por uso**; cotización vía contacto. autobizTrade declara **"cero coste de setup"**; **demo gratuita** disponible (`office.autobiz.com/en/demo/`). Soporte ES: tel. 960 25 88 68 / contactar@autobiz.com.
- **Importe concreto = GAP** (no descubrible públicamente).

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla/sección → dato.

### autobizMarket — pantalla de valoración + análisis de mercado [V]
- **Entrada por matrícula** → ficha con la versión exacta (referencia VO exclusiva).
- **Bloque de valores** (resultado): B2C / Network / C2C + B2B + reprise + 10 datos de mercado (rotación, depreciación, periodos de reprise).
- **Vista de posicionamiento de precio** vs mercado (local/regional/nacional) — **nube/scatter de precios** (price cloud) visualizando dónde cae cada vehículo.
- **Visualización de distribución de mercado** (distribución de concesionarios + nº de vehículos a la venta) — mostrada en interfaz tablet.
- **Vista de análisis de stock en tiempo real** (rotación, calidad de anuncio, posicionamiento).
- **Sección de sourcing** (descarga de listados para valoración masiva).
- **Alertas** configurables.

### autobizAdsScan — pantalla de resultados de sourcing (≈ "Market Radar" de autobiz) [V]
Cada fila/tarjeta de anuncio muestra: **make/model · energía · kilometraje · año de matriculación · precio publicado · écart à la cote (gap vs valor autobiz) · vendedor pro/particular · enlace al anuncio original**. Arriba: **15 filtros** + **filtro geográfico** (departamento/región/país) + **filtro por diferencial de margen**. Lateral: **búsquedas guardadas** + **alertas email**.

### autobizCarcheck — flujo de tasación (pantallas secuenciales) [V]
1. **Identificación**: matrícula / VIN / escaneo de permiso.
2. **Perfil mecánico** + **perfil de carrocería** (checklists de condición).
3. **Daños** (manual + **Noa marca el daño sobre la foto** dentro del informe).
4. **Costes de reacondicionamiento** (auto desde grid) + **alerta de discrepancia** declarado vs IA en el propio expediente.
5. **Página de pricing**: recomendación / precio final.
6. **Informe PDF** + push a autobizTrade / webhook.

### autobizMyStock — dashboard de una sola página [V]
- **Resumen de rendimiento en una página**; **20+ criterios** de precio y atractividad de marketing; **alertas** de calidad de anuncio (sin foto / precio desalineado / publicación larga); panel de **stocks de competidores de la región**; KPIs personalizables.

### autobizCockpit — dashboard jerárquico (OEM) [V]
- Navegación **global → país → grupo de distribución → punto de venta**; KPIs: volúmenes de stock, ventas, turns, calidad de anuncio; vista de comparación entre países/grupos; tendencias históricas (desde 2010).

### autobizPricingPower — dashboard Tableau [V]
- Dashboard **Tableau** 100% personalizable, 24/7; el usuario define **competidores** y **combinaciones edad/km** a seguir; actualización mensual.

### autobizBarometer — dashboard de señales de mercado [V]
- Tres bloques: **demanda VO / oferta VO / precios**; **30+ KPIs** personalizables de seguimiento y visualización.

### autobizCrossborder — salida por vehículo [V]
- Por cada vehículo de la lista: **valoración en los 22 mercados** + **impuestos locales** + **fiscalidad transfronteriza** + **costes logísticos** + **Cross-Border Potential Score**.

### autobiziFrame / autobizTradeIn — módulo embebido en web del concesionario [V]
- Branding del concesionario (logo/colores/transfer values); **identificación del vehículo del cliente** → **input de estado** → **estimación de reprise**; **formulario de lead** (nombre, apellidos, teléfono, email, mensaje); preguntas configurables.

### autobizClic2Buy — QR físico en concesionario [V]
- **QR único por zona** (taller/parking/recepción) → SMS al cliente → **autoinspección 200 checkpoints** → el dealer recibe datos del vehículo + **ubicación del cliente** + **oferta de reprise instantánea**; alerta en tiempo real.

### autobizTrade — interfaz de subasta B2B [V]
- Publicación desde Carcheck/dashboard → **selección de audiencia** → **formato de venta** (fijo/puja abierta/blind/sellada/one-by-one/agrupada) + **reserva** → **tracking de pujas en tiempo real** → **contraoferta inteligente** vs margen objetivo.

### B2C (`vendre.autobiz.fr`) [V]
- Home: **estimación gratis en 2 min** (matrícula o marca + formulario de características) → estimación (motor `autobizMarket®`) → cita en punto socio → inspección + road test → **oferta firme** → transferencia 48-72h.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Valor de mercado 100% estadístico y observado** (no editorial): calculado a diario desde ~2M anuncios deduplicados — frente al modelo "reuniones editoriales" de Eurotax/Schwacke.
- [V] **Tres capas de valor de mercado en un solo producto** (B2C / Network / C2C) + B2B + reprise + futuro — granularidad de canal poco común.
- [V] **Certificación IFRS 13 (primera del sector)** + auditoría **Chappuis Halder** + alineación **BCE** → valores **bancables** para colateral y stress test de carteras (autobizPortfolio) — diferenciador frente a peers de valoración pura.
- [V] **Sistema operativo VO de extremo a extremo** en un solo proveedor: valoración → **sourcing** (AdsScan/Clic2Buy QR) → **tasación + IA de daños** (Carcheck+Noa) → **inteligencia de stock/precio** (MyStock/PricingPower/Cockpit) → **remarketing** (Trade/Pilot/Interface/Targeting) → **arbitraje transfronterizo** (Crossborder) → **plataforma de subasta B2B** (Trade) → **buyback B2C** (EasyReprise).
- [V] **Noa — IA de detección de daños sobre foto** (Monk AI): tipo/severidad/parte/coste de reparación + **alerta de discrepancia** declarado-vs-IA integrada en el expediente. Raro entre proveedores de valoración.
- [V] **autobizCrossborder**: valoración multi-mercado **con impuestos locales + fiscalidad transfronteriza + logística + score** — arbitraje de exportación accionable.
- [V] **Datasets Joreca de estudios de mercado**: 15B anuncios / 37 países / 330k+ anunciantes / cuota de mercado por tipo de anuncio; **usados en 5 operaciones de M&A** — inteligencia competitiva y de marketplace ausente en competidores de valoración.
- [V] **Motor de generación de leads de reprise** (iFrame/TradeIn): 2M+ leads/año, +100% leads, 8-15% conversión — orientación a captación comercial, no solo a dato.
- [V] **Sourcing omnicanal**: QR en concesionario (Clic2Buy) + reprise 100% remoto por SMS (Clic2Sell) + detección de gangas en infomediarios (AdsScan).
- [V] **Respaldo Stellantis** (accionista mayoritario, confianza OEM) + **partnership JATO** (specs/taxonomía) → "specs-to-valuation".

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Precio no público**: `pricing.autobiz.com` tras login Auth0; ningún importe descubrible (solo demo/contacto).
- [V] **Sin historial de vehículo / siniestros / fraude de cuentakilómetros por VIN** (tipo Carfax/autoDNA): Carcheck es una **inspección fresca**, no un informe de provenance/incidentes; autobizVIN da specs/equipamiento, no propietarios/accidentes/km certificado.
- [V] **Cobertura desigual por producto**: Noa y Clic2Sell solo **Francia**; AdsScan solo **6 países** (vs 22 de valoración); Trade **10 países**.
- [A] **Sin tipos de vehículo más allá de turismo declarados**: no se mencionan **motos, LCV ni industrial** (Eurotax sí cubre LCV/motos).
- [A] **Sin datos OEM de mantenimiento/reparación tipo SMR** (tiempos de mano de obra, precios de piezas, calendario de mantenimiento, TecDoc): autobiz calcula **coste de reacondicionamiento desde inspección**, no un catálogo SMR/repair (Autovista/DAT sí).
- [A] **Sin inteligencia de batería/EV** (kWh, química de celda, envíos) tipo EV Volumes.
- [A] **Sin TCO/coste total de propiedad** como producto (a diferencia de Car Cost Expert de Eurotax).
- [V] **`valuation.autobiz.com` cerrado (403)**: el público no puede inspeccionar el motor/widget de valoración embebido.
- [A] **Documentación técnica de API no pública**: sin esquema JSON, auth, rate limits ni diccionario de campos expuestos.
- [A] **Métricas tipo "price-to-market %" y "market days supply" no nombradas como índices normalizados**: usan **rotación/turnover**, **posicionamiento vs competidores** y **écart à la cote (valuation gap)** en su lugar.
- [A] **Sin marketplace transaccional propio de listados al consumidor**: el canal transaccional es subasta **B2B** (Trade) y **buyback B2C** (EasyReprise), no un portal de anuncios.

---

## 10. Fuentes (URLs)
- https://corporate.autobiz.com/en/ — home corporate, posicionamiento, clientes.
- https://corporate.autobiz.com/en/about-us/ — identidad, fundación 2004, dirección, Stellantis mayoritario, 320 empleados, hitos.
- https://corporate.autobiz.com/en/our-solutions/ — 4 categorías de solución + catálogo de 22 productos.
- https://corporate.autobiz.com/en/our-products/autobizapi/ — API: valores, microservicios, 99,5%, 20 países, 350 fuentes.
- https://office.autobiz.com/en/ — suite autobizOffice (productos profesionales), 30.000 usuarios, 7 idiomas, 10+ integraciones.
- https://office.autobiz.com/en/autobizmarket/ y https://corporate.autobiz.com/en/our-products/autobizmarket/ — herramienta de valoración (B2C/Network/C2C, 10 datos de mercado, posicionamiento, 20M lecturas/día).
- https://corporate.autobiz.com/en/our-products/autobizvin/ — campos de identificación VIN.
- https://corporate.autobiz.com/en/our-products/autobizdraganddrop/ — 4 valores por VO, meta-repositorio.
- https://corporate.autobiz.com/en/our-products/autobizfuture/ — residual/futuro, factores de corrección, IFRS/BCE.
- https://corporate.autobiz.com/en/our-products/autobizbarometer/ — 30+ KPIs, demanda/oferta/precios.
- https://corporate.autobiz.com/en/our-products/autobizportfolio/ — fair value, IFRS13, stress test 5 días.
- https://corporate.autobiz.com/en/our-products/autobizinsurance-2/ — replacement value, peritaje.
- https://corporate.autobiz.com/en/our-products/autobizcrossborder/ — valoración 22 mercados + impuestos + logística + score.
- https://corporate.autobiz.com/en/our-products/autobizmystock/ — 20+ criterios, calidad de anuncio, −15 días rotación.
- https://corporate.autobiz.com/en/our-products/autobizpricingpower/ — Tableau, competidores, edad/km, mensual.
- https://corporate.autobiz.com/en/our-products/autobizcockpit/ — KPIs jerárquicos (stock/ventas/turns/ad quality).
- https://corporate.autobiz.com/en/our-products/autobizinterface/ — monitorización de red, pricing vs valoración.
- https://office.autobiz.com/en/autobizpilot/ — asignación a canales, recomendaciones, oportunidades internacionales.
- https://corporate.autobiz.com/en/our-products/autobiztargeting/ — dataset de compradores (make/model/rotación/precio vs mercado/tax ID).
- https://office.autobiz.com/en/autobizadsscan/ y https://office.autobiz.com/en/sourcing/ — écart à la cote, 50 infomediarios, 6 países, 15 filtros.
- https://corporate.autobiz.com/en/our-products/autobiziframe/ y .../autobiztradein/ — módulos web, lead capture, +100% leads.
- https://corporate.autobiz.com/en/our-products/autobizguaranteed/ — precio garantizado online, NPS 70.
- https://office.autobiz.com/en/autobizclic2buy/ — QR, 200 checkpoints, oferta instantánea.
- https://office.autobiz.com/en/autobizclic2sell/ — 30+ preguntas, SMS, conversión 30%.
- https://office.autobiz.com/en/autobizcarcheck/ y https://corporate.autobiz.com/en/our-products/autobizcarcheck/ — perfiles mecánico/carrocería, recon, webhooks, Noa.
- https://office.autobiz.com/en/noa/ — IA de daños (Monk AI), tipo/severidad/parte/coste, alerta discrepancia, solo Francia.
- https://office.autobiz.com/en/autobiztrade/ — formatos de subasta, contraoferta, 10 países, €300/veh.
- https://corporate.autobiz.com/en/our-products/jorecapanel/ — cuota de mercado por tipo de anuncio, 37 países, 5 M&A.
- https://corporate.autobiz.com/en/our-products/jorecaadvertisers/ — 330k+ anunciantes, +50 data points, CRM.
- https://vendre.autobiz.fr/ — B2C: estimación 2 min, motor autobizMarket®, oferta firme, transferencia 48-72h.
- https://valuation.autobiz.com/ — **403 Forbidden** (host cerrado del motor/widget de valoración) [renderizado Playwright].
- https://pricing.autobiz.com/ — **redirige a login Auth0** `login-office.autobiz.com` (precio no público) [renderizado Playwright].
- https://corporate.autobiz.com/en/press-release/autobiz-and-jato-dynamics-forge-strategic-european-partnership.../ — partnership JATO (31-mar-2026), specs-to-valuation, Europcar Mobility Group.
- https://corporate.autobiz.com/en/press-release/autobiz-the-first-car-valuation-company-to-meet-ifrs13-standards/ — IFRS13, auditoría Chappuis Halder, 10B precios, 40+ Big Data.
- https://www.jato.com/resources/media-and-press-releases/jato-dynamics-and-autobiz-forge-strategic-european-partnership — partnership JATO (2ª fuente).
- LinkedIn (autobiz-corporate), PitchBook (perfil 82429-21), CB Insights, Tracxn, LeadIQ — fundadores (Louvard/Urbah/Labi), HQ Courbevoie, empleados, facturación (verificación cruzada de identidad).

> Verificación: identidad corporativa contrastada con ≥2 fuentes (about-us + agregadores + 2 press releases). Campos de producto [V] leídos directamente de las páginas de producto (corporate + office). Metodología [V] de páginas de solución + press IFRS13 + descripción del valor en autobizMarket. Subdominios `valuation`/`pricing` verificados con renderizado Playwright (403 / login Auth0). Importe de precio = no verificable públicamente (GAP). Tipos de vehículo distintos de turismo, datos SMR/EV/TCO y docs de API = no hallados (marcados [A]/GAP, no inventados).
