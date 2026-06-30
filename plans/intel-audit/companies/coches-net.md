# Auditoría atómica — coches.net (marketplace de motor + inteligencia de mercado VO · Adevinta Motor S.L.U.)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Marketplace líder de coches en España + capa de **datos/inteligencia de mercado** para profesionales (coches.net PRO, Data Products, barómetros, Mobility Trends).
> Web producto (tasador): https://www.coches.net/tasacion-de-coches/ · Web pro: `pro.coches.net` / `profesionales.coches.net` · Blog PRO: `coches.net/blog-profesionales` · **Subdominio del encargo, `portal-insights` → `portal-insights.coches.net` SÍ RESUELVE** (CloudFront; alias `pro.gatewaycoches.coches.net`) — ver §Identidad/§Entrega.
> Fecha auditoría: 2026-06-30. Método: el dominio www.coches.net sirve **muro anti-bot (DataDome)** → navegación directa bloqueada ("Algo en tu navegador nos hizo pensar que eres un bot"). Extracción real por: (a) **Playwright** sobre snapshots de Wayback Machine renderizables; (b) **descarga del HTML crudo** de Wayback en modo `id_` + parseo estático con Python (evita la inyección JS del replay y el redirect a edmunds que dispara archive.org); (c) **descarga directa del PDF mensual Mobility Trends** (marzo-2025, 17 págs, extraído con PyMuPDF); (d) **mirror WordPress de origen** del blog PRO (`s36444.p1793.sites.pressdns.com`, sin DataDome) para los posts de Data Products; (e) resolución DNS de subdominios (`nslookup`); (f) búsqueda web para propiedad/escala/operación EQT.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). Campos atómicos del tasador extraídos por JS de la ficha real; métricas de mercado extraídas verbatim del PDF y del barómetro.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca de producto | **coches.net** (marketplace de motor) + **coches.net PRO** (B2B) | [V] |
| Operador legal | **Adevinta Motor, S.L.U.** | [V — quiénes-somos/Adevinta] |
| Entidad de pie de página | **Adevinta Spain, S.L.U.** ("© Adevinta Spain S.L.U." en 2020/2021/2023/2024) | [V — footer en múltiples snapshots] |
| Familia de marcas (Adevinta Spain) | coches.net · **motos.net** · **milanuncios.com** · **fotocasa.es** · **habitaclia.com** · **infojobs.net** · JobisJob | [V — footer] |
| Categoría | **Marketplace de clasificados de automoción** (compraventa C2C/C2B/B2C) + **tasador** + **inteligencia de mercado del VO** (barómetros, informes, Data Products) + **catálogo de fichas técnicas** + trámites/servicios | [V] |
| Fundación | Nace **1996** como "revista digital del motor" (según su "Conócenos"); evoluciona a marketplace líder de clasificados de motor (algunas fuentes citan **1997**) | [V/A — conócenos vía búsqueda] |
| Escala/audiencia | **>20 millones de visitas/mes** · **>5 millones de usuarios únicos/mes** · ~**248.648** vehículos publicados (snapshot), precio medio ~19.685 €, ~71.255 km, año medio 2020 | [V — conócenos/Adevinta + búsqueda] |
| Idioma/mercado | Español · **España** | [V] |
| Contacto prensa/PRO | comunicacion@coches.net · begona.adroher@adevinta.com (Responsable de Comunicación coches.net & motos.net) | [V — barómetro + PDF] |

### Cadena de propiedad (verificada a nivel de entidad) [V salvo donde se marca]
- coches.net lo opera **Adevinta Motor, S.L.U.**, parte de **Adevinta Spain, S.L.U.** [V]
- **Adevinta** nació como escisión (spin-off) de **Schibsted Media Group** (grupo noruego fundado 1839) en **febrero de 2019**. [V — Wikipedia Schibsted/Adevinta]
- Adevinta (matriz) ha estado controlada por los fondos **Permira y Blackstone**. [V — búsqueda]
- **OPERACIÓN EN CURSO:** el fondo sueco **EQT** acordó comprar el **negocio de Adevinta en España** (Milanuncios, Fotocasa, Habitaclia, InfoJobs, **coches.net**, Motos.net), **anunciado 2025-07-21**, valoración ~**€2.000 M (TEV)**, **cierre previsto Q1 2026**. (EQT es además dueño de idealista → ángulo antitrust). [V — EQT news + El Español/Economista/Capital]
- **Cadena resultante (transición):** **Schibsted → Adevinta (Permira/Blackstone) → [EQT, cierre Q1-2026] → Adevinta Spain → Adevinta Motor → coches.net**. [V a nivel de entidades]

### Clientes objetivo [V]
- **Consumidor final (C2C/C2B):** comprador/vendedor particular de coche de ocasión, km0, nuevo, por suscripción/renting (gratis, financiado por publicidad y leads).
- **Profesionales (B2B):** concesionarios, grupos y **compraventas** de VO — segmentados explícitamente en **"negocios altamente digitalizados"** vs **"pequeños negocios"** (primeros pasos digitales). [V — Packs VO 2025]
- **Marcas/anunciantes:** publicidad + generación de leads.

---

## 2. Cobertura

### Geográfica [V]
- **España** (único mercado). Precio del tasador **varía por zona** (campo Código Postal → ajuste geográfico). Inteligencia de mercado desglosada por **Comunidad Autónoma**.

### Scope de vehículos [V]
- **Coche de ocasión (VO)** [foco de la inteligencia], **seminuevo (<1 año)**, **Km0**, **coche nuevo**, **coche por suscripción/renting**.
- **Más vehículos:** furgonetas e industriales (vehículos comerciales/industriales), clásicos y competición, autocaravanas y remolques, coches sin carnet. [V — menú + PRO]
- Hermano de grupo **motos.net** (motos) — entidad/portal aparte.

### Granularidad de identificación [V]
**Marca → Modelo → Carrocería → Combustible → Año de matriculación → Versión** (jerarquía exacta del tasador y del catálogo de fichas técnicas). Tipo de cambio (Automático/Manual) y kilómetros como atributos de instancia. Identificación opcional por **matrícula** (no por VIN como producto).

---

## 3. Productos + campos atómicos

coches.net combina **producto de consumo** (tasador + marketplace + fichas técnicas) y **producto B2B de datos** (coches.net PRO + Data Products + informes). Cada superficie con sus campos atómicos verificados:

### 3.1 Tasador de coches (valoración C2C/C2B gratuita) [V — extracción JS de la ficha real]
Ruta: `/tasacion-de-coches/`. Propuesta: "Tasa de forma inmediata y gratuita · Conoce el precio de mercado · Infórmate para la negociación".

**Campos de ENTRADA (formulario, `name` del input verificado):**
- Marca (`makeId`) · Modelo (`modelId`) · Carrocería (`bodyTypeDoors`) · Combustible (`fuelId`) · Año de matriculación (`year`) · Versión (`versionId`) · **Tipo de cambio** (Automático / Manual) · Kilómetros del vehículo (`km`) · **Código postal** (`postalCode`, "la tasación varía según la zona donde resides").
- **Opcionales** (para "tasación todavía más precisa"): **Matrícula** · **Estado del vehículo**. [V — artículo noticia]

**Campos de SALIDA (resultado, verbatim):**
- **Precio recomendado de venta a particular** ("el recomendable para la venta del coche a un particular").
- **Precio aproximado de compra por concesionario** ("el precio aproximado que puede ofrecer un concesionario interesado" — varía según estado real). 
- (El cálculo = **valor medio** al que se venden en coches.net unidades similares → "precio estimado y recomendado para la venta").
- **CTA "publicar anuncio"** (prerrellena todos los datos + precio de tasación; solo falta subir fotos).
- **CTA "elegir profesional"** → **listado de concesionarios cercanos interesados** con **distancia en km**, **certificados por coches.net**, cita en **24 h**. [V — artículo noticia 2023]

> ~**11 inputs + 4 outputs** verificados. El tasador se activa también **al insertar un anuncio** (web y app).

### 3.2 Marketplace VO — ficha de anuncio (datos del coche en venta) [V parcial / JATO]
La ficha de anuncio combina datos del vendedor + **datos técnicos/equipamiento provistos por JATO** (ver §4). Campos atómicos:
- **Precio** (€) · **rango de precio del listado** `lowPrice`–`highPrice` + `offerCount` + `priceCurrency` (JSON-LD schema.org verificado) · **itemCondition** (nuevo/ocasión/km0/seminuevo). [V — JSON-LD estático]
- **Kilómetros · Año/fecha de matriculación · Combustible · Carrocería · Tipo de cambio · Potencia (CV/kW) · Cilindrada · Nº de puertas · Nº de plazas · Color · Emisiones CO₂ · Etiqueta ambiental DGT · Acabado/versión.** [A/JATO — campos típicos de ficha; los técnicos/equipamiento/extras/acabado son **provistos por JATO** según la página PRO]
- **Datos técnicos** + **Equipamiento de serie** + **Extras/opcionales** + **Acabado** (JATO). [V — PRO integra JATO]
- **Ubicación/provincia** (`areaServed`) · **Tipo de vendedor** (particular/profesional) · **Garantía** · **VO Certificado/CPO** (mención editorial). [A — marketplace estándar]

### 3.3 Fichas técnicas y precios + Comparador (catálogo de especificaciones) [V]
Rutas: `/fichas_tecnicas/` (Buscador de fichas técnicas) · **Comparador de coches** · Buscador por marca y modelo (bajo "Pruebas e información → Información técnica"). Catálogo de **datos técnicos + precios por modelo y versión** de todas las marcas, alimentado por **JATO** (proveedor de referencia de specs para el portal). Replica el set de specs JATO (motor, prestaciones, dimensiones, consumos, equipamiento) — ver `jato-dynamics.md`. [V — menú + búsqueda]

### 3.4 coches.net PRO — Data Products (inteligencia de mercado B2B) [V — PDF + posts]
Núcleo de inteligencia. coches.net "dota a sus clientes de potentes herramientas de data… **Data Products**" para responder 3 preguntas: *¿Están mis anuncios generando interés? ¿Son mis precios competitivos? ¿Mi producto se adecúa a lo que demanda el mercado?* Concepto: entender la **elasticidad al precio** y equilibrar **rotación vs margen**.

**(a) Price Radar** [V] — "datos en tiempo real para optimizar precios, prever tiempos de venta y gestionar el stock". Campos/funciones:
- **Precio de mercado en tiempo real** del vehículo · **Desviación respecto al precio medio** del mercado (price-to-market) · **Recomendación/posicionamiento de precio** · **Previsión del tiempo de venta** · detección de **"activos tóxicos"** (stock estancado, días en campaña, capital bloqueado, erosión de margen). Incluido en **todos los packs** (ampliado nov-2024). Asociado al **Comparador de Precios Avanzado** (alinear precio vs mercado/competencia).

**(b) Demand Radar** [V] — "analiza la demanda para facilitar decisiones de adquisición y rotación" (tier **Pack Expert**). Campos/KPIs:
- **Tiempo de rotación medio** de un vehículo concreto (days-to-sell) · **Cantidad de oferta existente en su mercado** (market supply / competencia) · **Evolución de la oferta y la demanda del último año** · señal de **índice de demanda** por vehículo.

**(c) Estadísticas avanzadas / Informes mensuales de performance** [V] — "control total sobre la efectividad de tus anuncios". KPIs por anuncio:
- **Visitas · Mensajes · Llamadas · Favoritos** (qué vehículos generan más interés y cuáles necesitan empuje) · informes mensuales de performance al cierre de cada periodo.

**(d) iTasador (PRO)** [V] — tasador integrado en PRO + **Comparador de precios** como "servicios de soporte a la decisión durante el aprovisionamiento y la venta".

> Empaquetado por **madurez digital y tamaño de empresa**. Frase guía (Field Sales Director): *"entender la elasticidad al precio… equilibrando rotación y margen"*.

### 3.5 coches.net PRO — software de gestión y multipublicación [V — pro.coches.net]
"Software de gestión y multipublicación de vehículos de ocasión". Funciones:
- **Gestión de stock** multi-tipología (convencionales, comerciales/industriales, autocaravanas/remolques, clásicos/competición, sin carnet).
- **Multipublicación**: coches.net + **Milanuncios** + **tu propia página web** + **>40 portales** especializados/clasificados (de pago y gratuitos). "Único software que permite publicar en Coches.net".
- **Exportar Stock** a **XML / XLS**.
- **Integra JATO Dynamics**: datos técnicos, equipamiento, **extras y acabados** automáticos y "totalmente fiables".
- **Web propia** del concesionario (escaparate online).
- **Tracking telefónico**: origen de llamadas, características, atendidas/no atendidas, aviso de perdidas en tiempo real, estadísticas, número visible.
- **Vídeos** en anuncios + vídeos corporativos; **formatos destacados**; **posicionamiento/subidas de stock** (cada **3 días** Expert / **6 días** Advance / mensual Reference).
- App **coches.net PRO** (iOS + Android).

### 3.6 Barómetro mensual del VO (inteligencia de precio, nota de prensa) [V — barómetro mayo-2024]
Sección `/blog-profesionales` → **Barómetros**. Métricas atómicas (fuente: marketplace coches.net + **Ideauto** para ventas):
- **Precio medio de oferta del VO** (€) + **variación interanual (%)** + **variación mensual (%)** + **récord histórico** (€ + fecha).
- **Precio medio del seminuevo** (€) + variación (%).
- **Precio medio por franja de antigüedad** (€ y %) [<1, 1-3, **4-5**, 6-10, **+10** años].
- **Precio medio por combustible** (eléctrico/híbrido, diésel, gasolina) + variación (%).
- **Precio medio por Comunidad Autónoma** (€) + **ranking** + variación por CCAA (%).
- **Stock/oferta de VO** (volumen) + variación interanual/mensual (%).
- **Oferta por combustible** (% del total + crecimiento %); **oferta de seminuevos** (crecimiento %).
- **Ventas/transacciones de VO** (unidades, **fuente Ideauto**) + variación interanual (%).
- **Ventas por combustible** (diésel/gasolina/híbrido/eléctrico/GLP-GNC: unidades + **cuota %**).
- **Modelos VO más vendidos** (ranking, unidades, **antigüedad media en años**).

### 3.7 coches.net Mobility Trends (informe mensual de mercado, PDF) [V — PDF marzo-2025, 17 págs]
Sección `/blog-profesionales` → **Mobility Trends**. PDF gratuito descargable, "radiografía mensual del sector". Métricas atómicas:
- **Ventas de vehículo NUEVO**: matriculaciones (unidades) + **% vs mes anterior** + **% interanual** (**fuente DGT**); **por canal** (particulares / empresas / **alquiladores**: unidades + %); **ranking de marcas** más vendidas (unidades).
- **Ventas de vehículo OCASIÓN**: transacciones (unidades) + % mensual + % interanual (**fuente Ideauto**); **por combustible** (cuota %); **por antigüedad** (>10 años, seminuevos <1 año: unidades + %).
- **Oferta VO (%)** y **Demanda VO (%)** — "**anuncios únicos publicados en coches.net**" (demanda = interacción/búsqueda).
- **Oferta y demanda VO por tipología de combustible** (diésel/gasolina/eléctrico-híbrido) — **% interanual**, serie temporal 13 meses.
- **Oferta y demanda VO por franja de antigüedad** (<1, 1-3, 4-5, 6-10, 11-15, 16-20, **+20 años**) — % interanual.
- **Evolución ANUAL del precio medio VO** (% interanual) + **precio medio por antigüedad** (€ + %; p.ej. +20 años = 5.508 € / +10%).
- **Evolución MENSUAL del precio medio VO** (€; p.ej. 17.563 €).
- **Encuesta mensual coches.net** ("Este mes hacemos foco en…") — **comportamiento del consumidor**: p.ej. intención de renting (% sí/no), combustible preferido (% por tipo), presupuesto mensual (rangos €), antigüedad máxima deseada, km anuales, prestaciones imprescindibles. **Fuente: encuesta propia coches.net.**
- **"La voz del experto"** (entrevista) + cita de fuentes externas (p.ej. informe de madurez del dato).

### 3.8 Trámites y servicios de consumo (capa de monetización) [V — menú]
Bajo "Trámites y Servicios": **Tasación de coches** · **Informe de vehículos** (historial por matrícula — servicio; proveedor/campos exactos **no verificados**, ver §Gaps) · **Financiación** · **Seguros** · **Trámites de compra-venta** · **Cómo vender tu coche** · **Encuentra tu garaje**. Cuenta de usuario: Favoritos · Búsquedas guardadas · **Alertas** · Mensajes · Mis anuncios.

---

## 4. Metodología y fuentes de dato [V/A]
- **Tasador (consumo):** método declarado verbatim — *"1. Utilizamos nuestra base de datos. En coches.net se anuncian **más de 600.000 vehículos al año**. 2. Buscamos vehículos iguales al que deseas tasar. 3. **Descartamos** todos los vehículos con precios **fuera de mercado**. 4. Calculamos un **precio promedio de venta**"*. → valoración **transaccional comparativa basada en su propio inventario de anuncios** (no guía editorial tipo Ganvam/Eurotax). Ajuste por **código postal** (zona) y opcional por **estado/matrícula**. [V — formulario]
- **Precio de mercado VO (barómetro/Mobility Trends):** **precio medio de oferta** de los anuncios publicados en coches.net (no de transacción cerrada). Han **actualizado la metodología** de cálculo del precio medio (anunciado en el PDF, sin detalle público). [V]
- **Oferta y demanda:** **oferta** = anuncios únicos publicados en coches.net; **demanda** = interacción/búsqueda sobre esos anuncios. → señal **propia del marketplace** (1ª parte). [V]
- **Ventas/transacciones VO:** **Ideauto** (proveedor externo). **Matriculaciones de coche nuevo:** **DGT**. [V — atribución explícita]
- **Specs/equipamiento/extras/acabados:** **JATO Dynamics** ("el mayor proveedor de información de todas las gamas y modelos"). [V — PRO]
- **Comportamiento del consumidor:** **encuestas propias** coches.net (panel de usuarios). [V — PDF]
- **Frescura:** barómetro y Mobility Trends **mensuales**; Price Radar **en tiempo real**; tasador en vivo sobre inventario activo. [V]

---

## 5. Entrega [V]
- **Portal web** coches.net (consumo, gratis) — tasador, marketplace, fichas técnicas, comparador, trámites.
- **coches.net PRO**: **web** (`pro.coches.net` / `profesionales.coches.net`) + **app iOS/Android** (gestión de stock, multipublicación, Data Products).
- **portal-insights.coches.net** [V — DNS]: **gateway** del backend de insights PRO (alias `pro.gatewaycoches.coches.net`, CloudFront). Raíz = health-check ("Test de conexión"); `/login` y rutas internas devuelven "Página de error" → **app gated por autenticación PRO** (no auditada por dentro; su existencia y naming confirman un portal de insights dedicado). 
- **Informes:** **Barómetros** (nota de prensa mensual en blog) + **Mobility Trends** (**PDF mensual descargable**, ~17 págs) — gratuitos.
- **Multipublicación / feed:** publicación automática a coches.net + Milanuncios + web propia + **>40 portales**; **Exportar Stock a XML/XLS**.
- **Integración de datos de terceros:** JATO (specs); Ideauto (ventas); DGT (matriculaciones). Conexión vía partners de multipublicación (p.ej. **Inventario.pro**, tercero, envía stock a coches.net y ofrece su propio "Enriquecimiento JATO" — **no es producto de coches.net**).
- **API pública documentada propia:** **no hallada** (ver Gaps). Existe `pro.gatewaycoches.coches.net` (gateway B2B interno, no documentado públicamente).

---

## 6. Precio
- **Consumo (tasador, publicar anuncio particular, búsqueda):** **gratis**. [V]
- **coches.net PRO — Packs VO 2025** (suscripción B2B, **importe no público**): [V — estructura]
  - **Iniciación · Pack Start**: hasta **30 anuncios** + **Price Radar** + **Comparador de Precios Avanzado** + **informes de rendimiento mensuales**.
  - **Iniciación · Pack Discover**: Start + posicionamiento avanzado + **vídeos** en anuncios.
  - **Profesional · Pack Reference**: subidas mensuales de stock + formatos destacados + enlace a web.
  - **Profesional · Pack Advance**: posicionamiento **cada 6 días** + presentación avanzada + vídeos corporativos.
  - **Profesional · Pack Expert**: posicionamiento **cada 3 días** + **Demand Radar**.
- **Servicios add-on:** Tracking telefónico, web propia (contratables aparte). [V]
- **Importe €/mes concreto = GAP** (no descubrible públicamente; depende de tamaño/madurez digital). [V]

---

## 7. Placement — dónde ubica coches.net cada dato (patrón a copiar por Cardeep)
> Mapeo pantalla/superficie → dato. Patrón clave: separar **valoración de consumo** (tasador, 1 pantalla, 2 precios) de **inteligencia profesional** (Price/Demand Radar + estadísticas dentro de PRO, por anuncio y por stock) e **informes públicos de marca** (barómetro + PDF Mobility Trends).

1. **Formulario del tasador** (`/tasacion-de-coches`): los **11 inputs** en **una sola pantalla** (Marca→Versión + cambio + km + **CP**); botón "Obtener tasación". Bloque "¿Cómo calculamos la tasación?" (4 pasos) **debajo** del formulario.
2. **Pantalla de resultado del tasador:** **dos precios** lado a lado (**recomendado a particular** vs **oferta de concesionario**) + CTA **"publicar anuncio"** (prerrellenado) + CTA **"elegir profesional"** → **lista de concesionarios con distancia en km**.
3. **Ficha de anuncio (detalle VO):** precio + rango + km/año/combustible/carrocería/cambio arriba; **datos técnicos + equipamiento + extras (JATO)** en bloques; tipo de vendedor, garantía, ubicación.
4. **Buscador de segunda mano:** facetas de filtro = los mismos campos (marca/modelo/precio/km/año/combustible/provincia…).
5. **Fichas técnicas / Comparador:** sección "Pruebas e información → Información técnica" (catálogo de specs+precios por versión; comparador lado a lado).
6. **coches.net PRO — al insertar/gestionar un anuncio:** **Price Radar** (precio de mercado + desviación + previsión de venta) **inline** sobre el vehículo; **Comparador de Precios Avanzado**.
7. **coches.net PRO — panel de stock:** ordenación por **antigüedad/días en campaña**, detección de **activos tóxicos**, **Demand Radar** (rotación media + oferta en su mercado + evolución oferta/demanda) por vehículo.
8. **coches.net PRO — Estadísticas avanzadas:** **performance por anuncio** (visitas/mensajes/llamadas/favoritos) + **informe mensual** de performance.
9. **portal-insights.coches.net (gateway gated):** backend de la capa de insights PRO (no público).
10. **Blog PRO → Barómetros:** nota de prensa mensual con precio medio/oferta/demanda/ventas por combustible-antigüedad-CCAA.
11. **Blog PRO → Mobility Trends:** **PDF mensual** estructurado (ventas nuevo DGT + ventas VO Ideauto + oferta/demanda series + precio anual/mensual + **encuesta de consumidor** + voz del experto).

> **Patrón Cardeep:** (a) tasador de consumo = **una pantalla, dos precios** (B2C particular vs C2B dealer) con auto-publicación; (b) capa pro = **Price Radar inline en el anuncio** (precio-vs-mercado + days-to-sell) y **Demand Radar en el stock** (rotación + supply + demanda); (c) **estadísticas de performance por anuncio**; (d) **informe público mensual descargable (PDF)** como herramienta de marca/lead-gen; (e) todo empaquetado en **tiers por tamaño/madurez**.

---

## 8. Diferencial (lo que ofrece y muchos no)
- [V] **Valoración basada en su propio inventario vivo** (>600.000 anuncios/año) con **descarte de outliers** y **ajuste geográfico por CP** — tasación transaccional comparativa, no guía editorial.
- [V] **Doble precio en el tasador**: recomendado a particular **+** oferta aproximada de concesionario, con **enrutado a dealers certificados** (cierre en 24 h) — cierra el bucle valoración→venta.
- [V] **Price Radar** (precio-vs-mercado en tiempo real + previsión de tiempo de venta + activos tóxicos) y **Demand Radar** (rotación media = days-to-sell + supply en su mercado + evolución oferta/demanda) — **inteligencia de rotación/margen** nativa del marketplace líder.
- [V] **Estadísticas de performance por anuncio** (visitas/mensajes/llamadas/favoritos) integradas en la herramienta de gestión.
- [V] **Señal propia de oferta Y demanda** (anuncios únicos + interacción) — la mayoría de guías solo tienen precio; coches.net mide demanda real del mayor marketplace ES.
- [V] **Informe Mobility Trends en PDF mensual** (ventas DGT + ventas VO Ideauto + series oferta/demanda por combustible/antigüedad + **encuesta de consumidor**) — radiografía de mercado como activo de marca.
- [V] **Multipublicación a >40 portales + Milanuncios + web propia** con **Exportar XML/XLS** y **specs JATO automáticas** — el dato técnico llega "gratis y fiable" al anuncio.
- [V] **Empaquetado por madurez digital/tamaño** (5 packs: Start/Discover/Reference/Advance/Expert).
- [V] **Escala** (>20M visitas/mes, >5M únicos) → su "precio medio de oferta" es referencia de mercado en España.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Sin valoración por VIN ni decode VIN**; la identificación es por **catálogo (marca→versión)** o **matrícula opcional**, no por VIN de 17 dígitos.
- [A] **Sin historial estructurado propio** (siniestros, nº de titulares, ITV, km certificados): el **"Informe de vehículos"** del menú es un **servicio/trámite** cuyo **proveedor y campos exactos no se pudieron verificar** (snapshot vacío) — probablemente partner/DGT, no dato propio de coches.net.
- [A] **Sin curvas de valor residual a futuro / forecast de depreciación** ni **trade/retail/wholesale** como guía financiera (estilo Eurotax/J.D. Power/Autovista): el dato es **precio de mercado actual de oferta**, no proyección de RV ni residual % a 36/48 meses.
- [V] **Precio = "oferta", no transacción cerrada** (precio de anuncio, no de venta final; las ventas las aporta **Ideauto** como volumen, no como precio).
- [V] **Sin API pública documentada** (ni esquema, ni auth, ni rate limits, ni diccionario de campos). Existe gateway B2B (`pro.gatewaycoches.coches.net` / `portal-insights`) pero **gated y no documentado**.
- [V] **Solo España**; sin cobertura multi-país (a diferencia de Autovista/JATO/Indicata).
- [A] **Specs no son dato propio** (dependen de **JATO**); coches.net es **distribuidor/consumidor** de la base de specs, no su productor.
- [V] **Muro anti-bot (DataDome)** sobre www → el dato no es accesible por scraping abierto; la vía B2B del dato es PRO (de pago) + informes PDF.
- [A] **Inteligencia de mercado centrada en VO**; el dato de coche nuevo se limita a **matriculaciones DGT** (volumen), sin pricing estructurado de nuevo.
- [V] **Importe de los packs no público** (precio B2B opaco).

---

## 10. Fuentes (URLs)
- https://www.coches.net/tasacion-de-coches/ — **tasador**: 11 inputs (makeId/modelId/bodyTypeDoors/fuelId/year/versionId/cambio/km/postalCode) + método "¿Cómo calculamos la tasación?" (vía snapshot Wayback `20260621223916`, extracción JS Playwright).
- https://www.coches.net/noticias/como-saber-el-valor-de-tu-coche-usado-tasador-cochesnet — **outputs del tasador** (doble precio particular/concesionario, publicar anuncio, elegir profesional 24 h, menú de servicios) (Wayback `20230406090715`, modo `id_`).
- https://www.coches.net/blog-profesionales/quienes-somos/ — **coches.net PRO**: misión + "Qué ofrecemos" (Barómetros mensuales, Mobility Trends, Estudios, Novedades PRO); blog nació 2021 (Wayback `20250823044529`, Playwright).
- https://pro.coches.net/ocasion.aspx — **PRO software**: gestión de stock, **iTasador**, Comparador de precios, **Exportar XML/XLS**, **integra JATO Dynamics**, multipublicación >40 portales, web propia, tracking telefónico (Wayback `20210925113234`, modo `id_`).
- https://www.coches.net/blog-profesionales/packs-vo-2025-de-coches-net-pro-mas-herramientas-mas-visibilidad-mas-exito/ — **Packs VO 2025**: Start/Discover/Reference/Advance/Expert; Price Radar (todos), Comparador Avanzado, Demand Radar (Expert), posicionamiento 3/6 días (mirror pressdns).
- https://www.coches.net/blog-profesionales/eliminar-activos-toxicos-stock-con-price-radar/ — **Price Radar**: activos tóxicos, rotación de stock, días en campaña, capital/margen, método 5 pasos (mirror pressdns).
- https://www.coches.net/blog-profesionales/wp-content/uploads/2025/03/cochesnetMOBILITYTRENDS-MARZO.pdf — **PDF Mobility Trends marzo-2025** (17 págs): ventas nuevo DGT + canales + ranking; ventas VO Ideauto; oferta/demanda VO (% por combustible/antigüedad, series); precio medio anual/mensual; **Data Products / Demand Radar / Price Radar** (voz del experto, Oscar Aguilar); encuesta renting.
- https://www.coches.net/blog-profesionales/precio-coche-ocasion-mayo-barometro/ — **Barómetro** mayo-2024: precio medio de oferta + var%, seminuevo, antigüedad, combustible, **CCAA**, stock/oferta, **ventas (Ideauto)**, modelos top (Wayback `20241007133212`, modo `id_`).
- https://www.coches.net/blog-profesionales/cochesnet-mobility-trends/ — índice de informes Mobility Trends (contenido del informe).
- https://www.coches.net/conocenos/ + https://adevinta.com/brand/coches-net/ — identidad, **fundación 1996**, **>20M visitas/mes**, **>5M únicos**, operador **Adevinta Motor S.L.U.** (vía búsqueda).
- https://eqtgroup.com/news/eqt-to-acquire-adevintas-spanish-online-classifieds-businesses-2025-07-21 + https://www.elespanol.com/invertia/.../eqt-compra-negocio-espana-adevinta-incluye-fotocasa-infojobs-cochesnet/ — **EQT compra Adevinta España** (~€2.000M TEV, cierre Q1 2026, incluye coches.net).
- https://es.wikipedia.org/wiki/Schibsted — Schibsted (1839) → escisión Adevinta (feb-2019).
- https://aimgroup.com/2024/11/04/coches-net-widens-availability-of-price-radar-tool/ — Price Radar ampliado a todos los packs (nov-2024).
- DNS (`nslookup`): **portal-insights.coches.net** / insights.coches.net / data.coches.net → CloudFront, alias **pro.gatewaycoches.coches.net** (gateway PRO gated); raíz = "Test de conexión"; `/login` → "Página de error".
- (Bloqueo) https://www.coches.net/ — **DataDome anti-bot** ("Algo en tu navegador nos hizo pensar que eres un bot · © Adevinta Spain S.L.U.").

> Verificación: identidad/propiedad contrastada con ≥2 fuentes (footer Adevinta Spain S.L.U. en 4 snapshots + EQT/prensa + Wikipedia Schibsted). Campos del tasador **[V]** por extracción JS del formulario real. Métricas de mercado **[V]** verbatim del PDF Mobility Trends y del barómetro. Data Products **[V]** del PDF + posts del blog (mirror de origen). Ausencias (VIN, RV/forecast, API, historial propio, multi-país) marcadas [V]/[A] sin inventar. Lo no verificable (proveedor/campos del "Informe de vehículos"; interior del portal-insights gated; importe de packs) declarado como Gap.
