# Auditoría atómica — Sumauto (marca B2B de motor de Vocento · portales AutoScout24.es + Autocasión + datos/leads · SUMAUTO MOTOR S.L.)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Sumauto NO es una guía de tasación tipo Eurotax/Ganvam: es la **marca B2B paraguas** que opera los **portales verticales de motor de Grupo Vocento** (AutoScout24.es, Autocasión, Unoauto, RentingCoches.com, Motocasión, Mascus) y monetiza con **leads de calidad + software de gestión + capa de datos/insights** para concesionarios y compraventas.
> Web corporativa B2B: https://www.sumauto.com/ · Portales de consumo: autoscout24.es / autocasion.com / unoauto.com / rentingcoches.com · **Subdominio del encargo, `portal-insights.sumauto.com` → SÍ RESUELVE** (5.102.135.26, mismo IP que toda la infra Sumauto; backend Go gated, "404 page not found" en raíz y en todas las rutas probadas) — ver §Entrega.
> Fecha auditoría: 2026-06-30. Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). JAMÁS se inventa: lo no verificable se declara como Gap.
> Método: (a) **`WebFetch` bloqueado** para www.sumauto.com, www.autoscout24.es y www.autocasion.com (anti-bot / 403 al fetcher) → **rodeo con `curl` + UA Chrome** (devuelve 200 en los tres) y volcado de HTML crudo a disco + parseo estático; (b) **extracción del `__NEXT_DATA__` / JSON-LD** de una ficha real de AutoScout24.es (358 KB) → esquema atómico de vehículo completo; (c) **`nslookup` + `curl` de sondeo** sobre `portal-insights.sumauto.com` y subdominios; (d) **Wayback CDX** para mapa de assets del corporativo; (e) WebSearch para identidad legal (empresia/CNMV), propiedad (JV Vocento/Scout24) y notas de prensa de producto (Car Digital Track, Sumauto Connect IA, Call Tracking IA).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Sumauto** — "la marca B2B de motor de Vocento" | [V — corporativo] |
| Operador legal | **SUMAUTO MOTOR, S.L.** | [V — empresia] |
| CIF | **B88049341** | [V — empresia] |
| Nombre previo | **ALPINIA INVESTMENTS 2018, S.L.** (la "NewCo" de la JV) | [V — empresia + prensa CNMV] |
| Constitución | **05/03/2018**; integración de negocios cerrada/anunciada a CNMV **21-dic-2018** | [V] |
| HQ | **C/ Josefa Valcárcel 40 bis, 28027 Madrid** | [V — LinkedIn + empresia] |
| Capital social | **€13.510.113** | [V — empresia] |
| Plantilla | ~**61** (empresia) / rango LinkedIn **201-500** (72 visibles) | [V] |
| Director General | **Nicolás Cantaert** | [V — prensa] |
| Tipografía/branding | "Sumamos fuerzas para multiplicar tus resultados" · "#SumautoEstáContigo" · símbolo = **5 círculos** (= ciclo de vida compra-venta) | [V — corporativo] |
| Contacto profesional | **917 897 782** · atencionalprofesional@sumauto.com | [V — corporativo] |
| Auditor | PricewaterhouseCoopers Auditores SL | [V — empresia] |

### Cadena de propiedad (verificada a nivel de entidad) [V salvo donde se marca]
- **Joint venture (21-dic-2018):** AutoScout24 (España) + Autocasión integran sus negocios de clasificados de coche en España en una **NewCo** (= *Alpinia Investments 2018 SL* → renombrada **SUMAUTO MOTOR SL**). [V — DigiMedios/CNMV + empresia]
- **Control:** **50% + 1 acción por DESARROLLO DE CLASIFICADOS, S.L.** (filial de **Grupo Vocento**); resto del capital por **AutoScout24 / Scout24** (matriz alemana del portal). Estructura ~50/50 pero **Vocento controla**. [V — LinkedIn pulse + DigiMedios; el "50% Vocento / 50% Scout24" de DigiMedios concuerda con el "50%+1" de Vocento]
- **Paso previo:** Desarrollo de Clasificados compró el **40% de Autocasión que no controlaba por €7,2 M** (+€2 M earnout a 3 años). [V — DigiMedios/CNMV]
- **Consejo de SUMAUTO MOTOR SL:** DESARROLLO DE CLASIFICADOS SL (presidente, socio) · VOCENTO GESTIÓN DE MEDIOS Y SERVICIOS SL · **Gruhn Bastian** · **Manetti Gioia** (consejeros — representación del lado AutoScout24). Socios formales: Desarrollo de Clasificados SL + **VISTRA ADMINISTRATION SERVICES SL** (vehículo fiduciario del tramo AutoScout24). [V — empresia]
- **Cadena resultante:** **Grupo Vocento → Desarrollo de Clasificados S.L. (50%+1) + Scout24/AutoScout24 (resto) → SUMAUTO MOTOR S.L. → {AutoScout24.es, Autocasión, Unoauto, RentingCoches.com, Motocasión, Mascus}**. [V]

### Clientes objetivo [V]
- **Profesionales (B2B, foco real):** **concesionarios** y **compraventas** de VO/VN (>**3.700 clientes profesionales**). Propuesta: "empoderar al dealer con **leads de calidad demostrables y medibles**" y "recuperar el **poder de negociación**" frente a los marketplaces dominantes.
- **Consumidor final:** comprador/vendedor de coche (>**4 M usuarios únicos/mes**, ~**9 M visitas/mes**, ~**400.000 anuncios** publicados en el lanzamiento).
- **Marcas/anunciantes:** publicidad + generación de leads cualificados.

---

## 2. Cobertura

### Geográfica [V/A]
- **España** como mercado de operación de Sumauto. [V]
- **AutoScout24 es pan-europeo** ("el mayor mercado de automoción de Europa", 18 países) → la **BBDD de valoración (>10 M de anuncios)** y la comparación de precio tienen alcance europeo; Sumauto explota el mercado ES sobre esa base de datos del grupo AutoScout24. [V — label page + meta]

### Scope de vehículos [V]
- **Coche de ocasión (VO)** [foco de la inteligencia], **Km0 / demo**, **seminuevo**, **coche nuevo (VN)**, **certificados**, **clásicos**, **sin carnet**, **eléctricos**.
- **Renting** (RentingCoches.com: particulares, empresas, autónomos).
- **Motos** (Motocasión) · **vehículo industrial / maquinaria** (Mascus, ámbito internacional) · furgonetas/caravanas/remolques (en AS24).

### Granularidad de identificación [V — JSON-LD ficha AS24]
Taxonomía completa de catálogo: **Marca (`brand`) → Grupo de modelo (`modelGroup`) → Modelo (`model`/`modelId`) → Generación (`modelGeneration`/`modelGenerationId`) → Versión/Acabado (`modelVersionInput`/`modelVersionCustom`/`modelOrModelLineId`)**. Identificación de instancia por **matrícula** (`licensePlate`, `hasCarRegistration`) — **no hay producto de decode/valoración por VIN de 17 dígitos** (ver Gaps).

---

## 3. Productos + campos atómicos

Sumauto combina **producto de consumo** (portales: tasador + marketplace + fichas técnicas + evaluación de precio) y **producto B2B** (área privada del dealer + leads + IA + capa de datos **Car Digital Track / portal-insights**).

### 3.1 Tasador de coche (valoración de consumo, gratuita) [V]
Rutas: **`tasacion.autoscout24.es`** (AS24) y **`autocasion.com/tasacion-de-coches`** (Autocasión). Propuesta: "Tasa tu coche gratis al momento · fiable, rápida, gratis".

**Campos de ENTRADA (verificados en el formulario/labels):**
- **Marca · Modelo · Versión · Año de matriculación · Combustible · Potencia (CV/kW) · Kilómetros.** (AS24)
- Autocasión: **Marca · Modelo · Año de matriculación · Kilometraje · Combustible.**

**Campos de SALIDA (verbatim):**
- **"¿Cuál es el valor de mercado?"** (valor de mercado del vehículo).
- **"¿A qué precio debo vender?"** (precio recomendado de venta).
- **"¿Qué precio voy a obtener?"** (expectativa de precio de cierre).
- Marco verbatim: *"El precio recomendado por AutoScout24 se calcula **comparando ofertas similares** y tiene en cuenta numerosas variables"* · *"recomendaciones de precio basadas en cálculos de los **precios de mercado**"* · Autocasión: *"Analizamos el mercado teniendo en cuenta todas las características de tu coche y también **en función de la oferta y la demanda**"*. Bloque **"Así funciona nuestro tasador"** bajo el formulario.

### 3.2 Evaluación de precio / Etiqueta de precio (price-to-market) [V — JSON-LD + label page]
Rutas: `/valoracion-de-precio/` · `/promo/evaluacion-de-precio/` · explicación en `autoscout24.com/priceevaluation/...?culture=es-ES`. **Aplicada a CADA anuncio** del marketplace (`priceEvaluation` embebido en el JSON de la ficha). Campos atómicos:
- **`priceEvaluation`** = etiqueta/badge de relación precio-mercado. Escala verbatim observada: **"Superprecio"** (mejor valor) · **"Buen precio"** · … · **"Caro"** (`expensivePrice`). Título de UI: **"Valoración de precio"**; copy: *"La evaluación de precios proporciona información sobre la relación precio… de todas las ofertas"*. (`priceEvaluation:3` observado en una ficha con `median:19500`.) [V — escala de 5 niveles del grupo AS24; "Superprecio"/"Buen precio"/"Caro" verificados verbatim, niveles intermedios "precio justo/elevado" [A]]
- **`evaluationRanges`** = **rango de precio de mercado fiable** + **`median`** (mediana de mercado del segmento comparable). [V]
- **`conditionalPriceBadge`** / `enableNewPriceLabel` (badge condicional de precio). [V]
- **Sin etiqueta** cuando hay muy pocos comparables (raros, clásicos) o precios irreales. [V]

### 3.3 Ficha de anuncio (VO/VN) — esquema atómico de vehículo [V — JSON-LD/`__NEXT_DATA__` ficha real AS24]
La ficha de AutoScout24.es expone el **esquema de datos completo del grupo AutoScout24**. Campos atómicos verificados (nombre técnico del JSON):

**Precio y financiación:**
- `price` / `priceRaw` / `finalPrice` (precio de venta) · `netPrice` / `netPriceRaw` (**precio sin IVA / IVA deducible**, `isVatLabelLegallyRequired`) · `traderReducedPrice` (**precio rebajado** por profesional) · `costModel` · `dollarPrice`.
- **`basicPriceHistoryLink` + `extendedPriceHistoryLink`** → botón **"Historial de precios"** (evolución de precio del propio anuncio). [V — verbatim en DOM]
- **`financeRate` · `leasing` · `leasingRate` · `leasingDetails`** + CTAs "con financiación"/"con leasing" (**cuota mensual**). [V]
- `enablePriceAlertsSimilarListings` → **alertas de precio** de anuncios similares. [V]

**Identidad/taxonomía:** `brand` · `model` · `modelId` · `modelGroup` · `modelGeneration(Id)` · `modelOrModelLineId` · `modelVersionInput`/`modelVersionCustom` (**versión/acabado**) · `category`/`categoryName` · `body`/`bodyType` (**carrocería**) · `vehicleType` · `condition`/`traderVehicleCondition` (**estado**: nuevo/ocasión/Km0/seminuevo/clásico).

**Matriculación/uso/historial:** `firstRegistrationDate(Raw)` (**fecha 1ª matriculación**) · `productionDate` (**año de producción**) · `mileageInKm` (**kilometraje**) · `licensePlate` + `hasCarRegistration` (**matrícula**) · **`nextVehicleSafetyInspection`** (**próxima ITV**) · **`lastTechnicalServiceDate`** (**última revisión**) · **`lastBeltServiceDate`** (**último cambio de correa de distribución**) · **`hasFullServiceHistory`** (**libro de mantenimiento completo**) · **`damage` / `damageConditions`** (**daños / accidentado**) · **`carpassMileageUrl`** (**km certificado tipo Car-Pass**; campo del esquema, activo en BE, ver Gaps).

**Motor/propulsión:** `engine` · `enginePower` · **`hp`** (CV) + **`kw`** (kW) · `engineDisplacement`/`engineDisplacementInCCM`/`displacementInCCM` (**cilindrada**) · `cylinders` + `cylinderCapacity` · `driveTrain` (**tracción**) · `gear` + `gears` + `transmissionType`/`vehicleTransmission` (**tipo y nº de marchas/cambio**) · `fuel` + `fuelCategory` + `additionalFuel` + `allFuelTypes` (**combustible(s)**) · `isPluginHybrid` · `auxiliaryPower` · `engineCount` · `engineManufacturerName` · `engineCoolingSystem` · `engineMountingType` · `engineHours`.

**Eléctrico/híbrido:** `battery` · `batteryChargingTime` (**tiempo de carga**) · `batteryOwnershipType` (**batería en propiedad/alquiler**) · `electricRange` + `electricRangeCity` + `electricRangeWithFallback` (**autonomía eléctrica**).

**Consumo/emisiones/medioambiente:** `consumption` (**consumo de combustible/energía**) · `co2emissionInGramPerKmWithFallback` (**CO₂ g/km**) · **`emissionSticker`** (**etiqueta ambiental / distintivo DGT**) · `environment` · `environmentEuDirective` · `environmentLabelsWithFallback` · `environmentBImSchV35` · `environmentPkwEnVKV`.

**Carrocería/confort/dimensiones:** `color` + `bodyColor` + `bodyColorOriginal` + `bodyColorRaw` (**color exterior/original**) · `upholsteryColor` (**Color y Tapicería**) · `numberOfDoors` (**puertas**) · `numberOfSeats` (**plazas**) · `emptyWeight` (**peso en vacío**) · `grossVehicleWeight` (**MMA**) · `frontAxleWeightRating`.

**Equipamiento:** `equipment` + `equipmentCategory` agrupado en **Confort y conveniencia** (`comfortAndConvenience`) · **Seguridad** · **Entretenimiento / Medios** · **Extras** · ítems concretos (Climatizador automático, Bluetooth, Control de velocidad, …).

**Vendedor:** `dealer` · `dealerOffer` · `isDealer` · **`googleRatings`** (**valoraciones Google del concesionario**) + **"Valoraciones"** de usuarios (AS24 es el único portal ES que permite **puntuar al concesionario**) · `expandableDealerOpeningHours` (horario) · ubicación (provincia/ciudad/CP) · `leadsRange` + formularios de lead (`enableGalleryLeadForm`, `afterLeadPage`) · **denuncia de fraude** (`fraudReportSuccess/Unsuccess`).

> ~**70+ campos atómicos** de vehículo verificados por extracción directa del JSON de la ficha.

### 3.4 Fichas técnicas y precios / Catálogo (Autocasión) [V]
`autocasion.com/fichas-tecnicas` → **"Fichas técnicas y precios"**: catálogo de specs + **precio de catálogo por modelo y versión** + **Diccionario del motor**. Mismo set de specs que la ficha (motor, prestaciones, dimensiones, consumos, equipamiento).

### 3.5 Car Digital Track — capa de datos / inteligencia de mercado (B2B) [V — prensa ×3]
**Producto de dato núcleo de Sumauto.** Definición verbatim: *"su **'Car Digital Track'** o **laboratorio de datos** para convertir el **Big Data** en información valiosa sobre **tendencias de mercado** y **forecasting** que ayuden a los profesionales de la venta a tomar decisiones de negocio"*. Señales/métricas que publican (verificadas en sus informes de mercado):
- **Precio medio** (VO y VN) por **modelo / segmento / etiqueta ambiental / región** + **variación interanual (%)** (p.ej. top-10 VN: 14.236 € en 2014 → 23.977 € en 2024, +68%; etiquetas Cero/Eco 26.800 €).
- **Días medios hasta la venta (days-to-sell)** — global (**84 días** de media) y por tipo (un electrificado tarda **15 días menos** que diésel/gasolina: ~2,5 vs 3 meses; ranking "5 modelos que menos tardan en venderse").
- **Ranking de modelos más buscados** (señal de **demanda** por búsquedas; VW Golf #1 ene-abr 2024) + impacto de **ZBE** en búsquedas de eco.
- **Cuota de mercado** por origen/tecnología (p.ej. marcas chinas 4%).
- **Oferta vs demanda** (el tasador de Autocasión pondera explícitamente oferta y demanda).
- **Forecasting / tendencias** de mercado (output del laboratorio).

### 3.6 Sumauto Connect IA — suite B2B de IA + leads [V — prensa]
- **Call Tracking IA:** evolución del call-tracking; **tracking telefónico** (origen/atención de llamadas) + **WhatsApp IA 24/7** que **cualifica oportunidades** y atiende a cualquier hora. KPIs declarados: **+20% de leads incrementales** (clientes que no habrían contactado por otra vía) y **+55% de mejora en conversión** de leads con IA conversacional. [V]
- **Leads de calidad:** definición verbatim = *"anuncios que generan una **oportunidad real de negocio**"*; **tasa de conversión 18% vs 10%** de la media de mercado; objetivo de eliminar el *"screen shopping"*. [V]
- **Ferias virtuales** (eventos de venta online) para multiplicar visibilidad de stock. [V]

### 3.7 Área privada del profesional + gestión de stock [V]
Interfaz privada única del dealer: **gestión de todo el stock sin publicación manual** + servicios integrados de **financiación, valoración, garantía y seguros** + **multipublicación** a los portales Sumauto + **sincronización API en tiempo real** del stock (alta/cambio de precio/baja instantáneos vía partners de DMS como Inventario.pro).

---

## 4. Metodología y fuentes de dato [V/A]
- **Valoración / etiqueta de precio:** *"avanzados **algoritmos dinámicos de aprendizaje automático**"* + **base de datos >10 M de anuncios** (grupo AutoScout24) + conocimiento experto. Compara con ofertas comparables de **particulares y profesionales**; variables: **marca, modelo, edad, combustible, potencia, tipo de cambio, kilometraje y equipamiento**. **Excluye** sellos de certificación, vehículos dañados, mejoras potenciales y precios irreales. Salida = **rango de precio de mercado fiable** + etiqueta. [V — label page]
- **Inteligencia de mercado (Car Digital Track):** **oferta** = anuncios publicados en los portales Sumauto; **demanda** = búsquedas/interacción de >4 M usuarios → Big Data → tendencias + forecasting. Contexto de ventas/matriculaciones probablemente DGT/externo [A]. [V — Car Digital Track]
- **Frescura:** **stock en tiempo real** (sync API instantánea); etiqueta de precio recalculada de forma dinámica; informes de mercado periódicos. [V]
- **Specs/catálogo:** esquema del grupo AutoScout24 (no dato propietario OEM). [A]

---

## 5. Entrega
- **Portales web de consumo:** **autoscout24.es** (+ app AutoScout24 iOS/Android), **autocasion.com**, **unoauto.com** (VN + leads), **rentingcoches.com** (301→ renting), **motocasion.com**, **mascus** (industrial/maquinaria). [V]
- **B2B:** **área privada única del profesional** (gestión de stock + servicios integrados) + **Sumauto Connect IA** (Call Tracking IA + WhatsApp IA 24/7) + **multipublicación** + **ferias virtuales**. [V]
- **`portal-insights.sumauto.com`** [V — DNS+curl]: **backend de insights gated** (resuelve a 5.102.135.26, mismo IP que toda la infra; servidor **Go** → "404 page not found" en raíz y en **/login, /api, /v1, /stats, /insights, /dashboard, /graphql, /swagger, /robots.txt, /.well-known/...** — **sin rutas públicas**). Naming + existencia + el producto **Car Digital Track** confirman una **capa de insights dedicada** (interior **no auditable**: gated por auth). Mismo patrón que `portal-insights.coches.net`.
- **API real-time de stock:** integración vía partners DMS (Inventario.pro y otros): alta/cambio de precio/baja **instantáneos**. [V]
- **API pública documentada propia:** **no hallada** (ver Gaps).

---

## 6. Precio
- **Consumo (tasador, evaluación de precio, búsqueda, ficha):** **gratis**. [V]
- **B2B:** **suscripción** (importe **no público**). Hubo un **"plan de choque para publicar gratis el stock"** (promoción de captación) de Autocasión + AutoScout24. [V — El Publicista]
- **Add-ons:** Call Tracking IA / WhatsApp IA / Sumauto Connect IA, ferias virtuales (importe no público). [V]
- **Importe €/mes concreto = GAP** (no descubrible públicamente). [V]

---

## 7. Placement — dónde ubica Sumauto cada dato (patrón a copiar por Cardeep)
> Patrón clave: **etiqueta de precio (price-to-market) + historial de precios POR ANUNCIO** en la ficha pública; **historial técnico del coche** (ITV/revisión/correa/daños/full-service) como bloque de confianza; **capa de datos B2B separada** (Car Digital Track / portal-insights) para tendencias y days-to-sell; **leads + IA** como monetización.

1. **Tasador** (`tasacion.autoscout24.es` / `autocasion.com/tasacion-de-coches`): inputs Marca→Combustible+Km en una pantalla → **tres preguntas-respuesta** ("valor de mercado", "a qué precio vender", "qué precio obtendré"); bloque "Así funciona" debajo.
2. **Ficha de anuncio (detalle):** **precio** arriba con **badge `priceEvaluation` ("Superprecio"/"Buen precio") al lado del precio** + **rango de mercado / mediana** + botón **"Historial de precios"**; **datos básicos** (año, km, combustible, cambio, potencia CV/kW, puertas, plazas, color); **equipamiento** agrupado (Confort/Seguridad/Entretenimiento/Extras); **bloque de historial/confianza** (próxima ITV, última revisión, cambio de correa, libro de mantenimiento completo, daños); **cuota de financiación/leasing**; **tarjeta del concesionario con Valoraciones + Google ratings**; alertas de precio + denuncia de fraude.
3. **Buscador/listado:** facetas = los mismos campos (marca/modelo/precio/km/año/combustible/provincia/etiqueta ambiental…) + **filtro por etiqueta de precio**.
4. **Fichas técnicas y precios (Autocasión):** catálogo de specs + precio por versión + diccionario del motor.
5. **Directorio de concesionarios:** páginas de dealer con **Valoraciones** de usuarios (único en ES) + Google ratings + horario + ubicación.
6. **Área privada del profesional (B2B):** gestión de stock, **leads** (oportunidad real + tasa de conversión), **Call Tracking IA / WhatsApp IA** (llamadas + chats cualificados), multipublicación, ferias virtuales.
7. **Car Digital Track / `portal-insights.sumauto.com` (gated):** **capa de datos** — tendencias de mercado, **days-to-sell**, **modelos más buscados (demanda)**, precio medio por segmento/etiqueta/región, forecasting (no público; backend de insights).
8. **Informes públicos de mercado (prensa/blog):** days-to-sell (84 días), ranking de más buscados, precio medio top-10, precio por etiqueta — como activo de marca/lead-gen.

> **Patrón Cardeep:** (a) **etiqueta price-to-market + historial de precio en CADA ficha** (no solo un tasador suelto); (b) **bloque de historial técnico** (ITV/revisión/correa/daños/libro completo) como señal de confianza; (c) **capa de datos B2B separada y gated** (`portal-insights`-style) para tendencias + **days-to-sell** + **demanda por búsquedas**; (d) **ratings del concesionario** en su ficha; (e) **leads medibles + IA conversacional** como monetización con KPIs (+20% leads / +55% conversión / 18% vs 10%).

---

## 8. Diferencial (lo que ofrece y muchos no)
- [V] **Etiqueta de precio (price-to-market) por anuncio** ("Superprecio"/"Buen precio"/…/"Caro") calculada por **ML sobre >10 M de anuncios** comparables, con **rango de mercado + mediana** — semáforo de precio que la mayoría de guías de tasación no exponen al consumidor.
- [V] **Historial de precios del anuncio** ("Historial de precios") + **alertas de precio** de similares.
- [V] **Bloque de historial técnico del coche** nativo en la ficha: **próxima ITV, última revisión, último cambio de correa, libro de mantenimiento completo (`hasFullServiceHistory`), daños/accidentado, km certificado (Car-Pass)** — datos de confianza por anuncio.
- [V] **Valoraciones del concesionario** (ratings de usuarios) — **AS24 es el único portal ES** que lo permite; + Google ratings.
- [V] **Car Digital Track** = laboratorio de Big Data → **tendencias + forecasting + days-to-sell + demanda por búsquedas** (demanda real de >4 M usuarios), no solo precio.
- [V] **Capa IA de leads** (Call Tracking IA + **WhatsApp IA 24/7**) con KPIs medibles (+20% leads, +55% conversión, 18% vs 10% de mercado).
- [V] **Respaldo dual**: alcance de medios **Vocento** + **tecnología/datos pan-europeos de AutoScout24** (BBDD >10 M, 18 países).
- [V] **Esquema de vehículo muy rico** (70+ campos atómicos, incluido eléctrico: autonomía, tiempo de carga, batería en propiedad/alquiler).
- [V] **Sync de stock API en tiempo real** (alta/precio/baja instantáneos) vía DMS.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Sin decode ni valoración por VIN** (17 dígitos): identificación por **catálogo (marca→versión)** + **matrícula** opcional; existe `licensePlate` pero **no hay producto de historial por VIN**.
- [A] **Sin curva de valor residual / forecast de depreciación** financiero (RV% a 36/48 meses) tipo Eurotax/Autovista/J.D. Power: la valoración es **precio de mercado actual**, no proyección de residual.
- [V] **Precio = oferta** (precio de anuncio), no transacción cerrada; el "valor de mercado" es estadística de oferta comparable.
- [V] **Sin API pública documentada** (ni esquema, ni auth, ni rate limits, ni diccionario de campos). `portal-insights.sumauto.com` es **backend gated** (Go, 404 en todo); la ingestión es vía **partners DMS**, no API abierta.
- [V] **Sin doble precio explícito** retail-particular vs trade-dealer en el tasador (da "valor de mercado" + "a qué precio vender", no una oferta de compra de concesionario al lado, a diferencia de coches.net).
- [A] **Specs no son dato propietario** (esquema del grupo AS24, no build-data OEM por VIN); **sin decode de opciones de fábrica por VIN**.
- [V] **Campos de historial heredados del esquema AS24 pueden estar inactivos en ES** (p.ej. `carpassMileageUrl` = Car-Pass belga; algunos `environment*` son etiquetas alemanas BImSchV/EnVKV) — presentes en el schema pero no necesariamente poblados en España.
- [V] **Anti-bot** en portales de consumo (WebFetch bloqueado; requiere UA real) → dato no abiertamente scrapeable.
- [V] **Importe B2B no público** (precio opaco).
- [V] **Sin barómetro de marca tan estructurado/periódico** como el de coches.net (Mobility Trends PDF mensual); la inteligencia se publica como notas de prensa sueltas + capa interna Car Digital Track.

---

## 10. Fuentes (URLs)
- https://www.sumauto.com/ — **corporativo** (curl/UA Chrome, 200): "marca B2B de motor de Vocento", 5 círculos, "leads de calidad demostrables y medibles", soluciones para todo el ciclo de compra-venta, contacto 917 897 782 (WebFetch bloqueado; extraído por curl).
- https://es.linkedin.com/company/sumauto — descripción, HQ **Josefa Valcárcel 40 bis, Madrid 28027**, sector, productos IA (Call Tracking IA, Sumauto Connect IA, WhatsApp IA 24/7), portales, "3.700 clientes / 4 M usuarios".
- https://www.empresia.es/empresa/sumauto-motor/ — **identidad legal**: SUMAUTO MOTOR SL, **CIF B88049341**, constitución **05/03/2018**, ex-**ALPINIA INVESTMENTS 2018 SL**, capital €13,5 M, consejo (Desarrollo de Clasificados + Vocento Gestión + **Gruhn Bastian** + **Manetti Gioia**), socios + VISTRA, objeto social.
- https://digimedios.es/index.php/archivo/vocento-compra-la-totalidad-de-autocasion-para-fusionarlo-con-autoscout24/ — **JV 21-dic-2018**: NewCo 50% Vocento / 50% Scout24; Vocento compra 40% de Autocasión por **€7,2 M**; CNMV.
- (LinkedIn pulse "Autoscout24 crea una joint venture junto con Autocasión", Diego Gutiérrez) — control **50% + 1 acción Desarrollo de Clasificados**, resto AutoScout24.
- https://www.posventa.info/texto-diario/mostrar/2994481/... — lanzamiento Sumauto: **Car Digital Track** (laboratorio de datos → tendencias + forecasting), 4 M usuarios / 9 M visitas / 3.700 clientes / 400.000 anuncios, conversión **18% vs 10%**, leads = "oportunidad real de negocio", DG **Nicolás Cantaert**.
- https://www.autofacil.es/nace-summauto-marca-aglutina-portales/ + https://www.marketingdirecto.com/.../sumauto-irrumpe-en-el-mercado-... — confirman **Car Digital Track** y la estructura de 5 portales (2ª/3ª fuente).
- https://tasacion.autoscout24.es — **tasador AS24** (curl, 200): inputs marca/modelo/versión/combustible/matriculación/potencia/kilómetros; outputs "valor de mercado / a qué precio vender / qué precio obtendré"; método "comparando ofertas similares".
- https://www.autocasion.com/tasacion-de-coches — **tasador Autocasión** (curl): inputs marca/modelo/matriculación/kilometraje/combustible; método "en función de la **oferta y la demanda**", gratis.
- https://www.autoscout24.com/priceevaluation/price-label-explanation-page/...?culture=es-ES — **etiquetas de precio** ("Superprecio", "Buen precio", "Caro"), **ML + BBDD >10 M**, variables (marca/modelo/edad/combustible/potencia/cambio/km/equipamiento), rango de mercado, exclusiones.
- https://www.autoscout24.es/anuncios/ford-edge-...-bae80cdb-... — **ficha real**: `__NEXT_DATA__`/JSON-LD con **70+ campos atómicos** (price/priceEvaluation/evaluationRanges/median, PriceHistoryLink, financeRate/leasing, nextVehicleSafetyInspection, last(Technical/Belt)ServiceDate, hasFullServiceHistory, damageConditions, carpassMileageUrl, hp/kw, battery*, electricRange*, emissionSticker, equipment categories, googleRatings, leadsRange…).
- https://www.autoscout24.es/profesionales/ — **directorio de concesionarios** + **Valoraciones** (ratings de dealer).
- https://www.autocasion.com/profesional — área profesional, "Fichas técnicas y precios", 3039 concesionarios, certificados/Km0/demo, +60.000 ofertas.
- https://www.inventario.pro/inventario-pro-conecta-tiempo-real-sumauto-autocasion-autoscout24-api/ — **sync API en tiempo real** (alta/cambio precio/baja instantáneos) a Autocasión + AutoScout24.
- https://www.posventa.info/tag/autoscout24 + https://www.posventa.com/tag/sumauto — informes de mercado: **days-to-sell 84 días**, electrificado **-15 días**, **modelos más buscados** (VW Golf #1), precio top-10 +68% (14.236€→23.977€), precio etiquetas Cero/Eco 26.800€.
- https://www.elpublicista.es/anunciantes/autocasion-autoscout24-lanzan-plan-choque-para-publicar-gratis — "plan de choque para **publicar gratis** el stock".
- **DNS/curl:** `nslookup` → **portal-insights.sumauto.com = 5.102.135.26** (mismo IP que www/api/data/pro/insights); `curl` → **"404 page not found"** (servidor Go) en raíz y en /login, /api, /v1, /stats, /insights, /dashboard, /graphql, /swagger, /robots.txt, /.well-known/security.txt → **backend de insights gated sin rutas públicas**.

> Verificación: identidad legal + JV/propiedad contrastadas con **≥2 fuentes** (empresia + DigiMedios/CNMV + LinkedIn pulse). Campos de la ficha **[V]** por extracción directa del JSON real de AutoScout24.es. Etiquetas de precio **[V]** verbatim (Superprecio/Buen precio/Caro) de la label page + JSON. Car Digital Track **[V]** en 3 medios. `portal-insights` **[V]** por DNS+curl (existe, gated, Go). Ausencias (VIN decode, RV/forecast financiero, API pública, doble precio retail/trade, barómetro PDF) marcadas [V]/[A] sin inventar.
