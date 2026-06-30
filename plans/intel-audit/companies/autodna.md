# autoDNA — Auditoría atómica

> **slug:** `autodna` · **subdominio de audit:** `vin-history` · **web:** https://www.autodna.com/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` = leído en fuente; `[NO-VERIFICADO]` lo no confirmado; `[DISCREPANCIA]` cuando las fuentes chocan; nada inventado.
> **Veredicto express:** autoDNA es el **decano europeo del informe de historial de vehículo por VIN** (≈"el Carfax de Europa del Este/Central"),
> producto **B2C-first**: el comprador particular mete un VIN, ve un **preview gratis de disponibilidad** y compra un **PDF de 24,99 €**.
> Su músculo es la **agregación de eventos de historial** (kilometrajes con fecha+fuente, daños, robo multi-país, taxi/leasing, fotos de archivo,
> embargos, inspecciones) sobre **26+ países europeos + EE.UU./Canadá**, **500M+ vehículos**, **23.000M de registros**, **50.000+ fuentes**.
> **No es una casa de valoración** (no da residual %, no da trade/retail recomendado, no da days-to-sell ni market-days-supply): su unidad de valor
> es el **evento de procedencia datado**, no el precio. El dato US lo **revende vía VinAudit (NMVTIS)**; el dato EU es agregación propia.
> Capa B2B real pero discreta: **WebAPI**, **widgets embebibles (VIN decoder + buscador)**, **paquetes de 20/50/100 informes** y **afiliados**.
> **Patrón a copiar por cardeep:** (1) el **preview de disponibilidad gratis** como gancho (semáforo de qué datos hay antes de pagar);
> (2) la **tarjeta "Key Information"** en cabecera con flags binarios (importado/robo/daño/siniestro total/servicio) + contador de eventos;
> (3) el **gráfico interactivo de odómetro** con anotación de fuente por punto; (4) el **timeline cronológico de eventos** con ubicación;
> (5) el bloque **"Last Enquiries" con mapa** (cuántas veces y desde dónde se ha consultado el coche) como señal social/anti-fraude.
> **Sombra:** Trustpilot **2,3/5**; quejas recurrentes de **informes vacíos sin reembolso** y un **dominio satélite `detailedautodna.com`** con
> patrón de **suscripción recurrente** (auto-renovación en T&C). Calidad del dato muy desigual por país.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **autoDNA** (marca; dominios `autodna.com`, `autodna.pl`, `autodna.de`, etc.) | [VERIFICADO ≥2: autodna.com, trustpilot] |
| Razón social | **autoDNA Sp. z o.o.** (sociedad limitada polaca) | [VERIFICADO ≥2: about-autodna, terms-and-conditions] |
| HQ | **Łódź, Polonia** — ul. Obywatelska 128/152, 94-104 Łódź | [VERIFICADO ≥2: about-autodna, terms]; [DISCREPANCIA: una comparativa de terceros dice "Warsaw" — error de tercero, prevalece la fuente legal propia] |
| Identificadores legales | **KRS 0000349742** · **NIP 5492391545** · **REGON 121164104** · capital social 50.000 PLN | [VERIFICADO: about-autodna / footer legal] |
| Entidad UK asociada | **AUTO DNA LTD** (Companies House nº **15234694**) — vehículo legal para mercado británico | [VERIFICADO: GOV.UK Companies House (búsqueda)] |
| Fundación | **2010** según la propia empresa ("15 años de experiencia", "desde 2010") | [VERIFICADO: about-autodna + homepage]; [DISCREPANCIA: Crunchbase/Tracxn datan **2003**; comparativas de terceros datan **2009** — probable dominio/predecesor previo a la constitución de la Sp. z o.o.] |
| Grupo / owner | **Independiente, privada, sin financiación externa declarada** ("has not raised any funding") | [VERIFICADO: Tracxn/Crunchbase resumen]; [NO-VERIFICADO el accionariado último/persona física — no se publica] |
| Owner erróneo en agregadores | Tracxn asocia "F Kenworthy Limited" / dirección Dunstable UK | [DISCREPANCIA / ruido de agregador — descartado, no fiable] |
| Empleados | "20–49" (estimación agregadores); Tracxn citó "2" en 2020 (obsoleto) | [NO-VERIFICADO / cifras de agregador, baja fiabilidad] |
| Reputación pública | **Trustpilot 2,3/5** (~576–671 reseñas, `autodna.com`); sitios localizados (.de, .pl, .at) con scores propios | [VERIFICADO ≥2: trustpilot.com/review/autodna.com, búsqueda] |
| Contacto | contact@autodna.com · soporte: support.autodna.com | [VERIFICADO: footer] |

**Qué es:** una de las mayores plataformas **e-commerce de informes de historial de vehículo usado** del mundo. El usuario
descodifica un **VIN de 17 caracteres** y obtiene un **informe-resumen del "ciclo de vida" del coche**. Negocio nacido y centrado en
**Europa central/oriental** (Polonia, Bálticos, DACH, etc.), con extensión a **EE.UU./Canadá** vía socio de datos.

### Categorías de producto
1. **Vehicle History Report (Europa)** — informe estrella, PDF de pago (núcleo del negocio).
2. **US Vehicle History Report / "Local history of the US vehicle"** — informe para coches americanos (datos NMVTIS vía VinAudit).
3. **VIN decoder / VIN Check / "Decoder VIN - Checker"** — descodificación gratuita + preview de disponibilidad (gancho de captación).
4. **Business Packages** — lotes de informes (20/50/100) para profesionales del usado e importadores.
5. **WebAPI + widgets embebibles** — VIN decoder y buscador como "ready-made elements" para webs de socios (capa B2B/integración).
6. **Affiliate Program** — `afilio.autodna.com` (monetización por referidos).

### Cliente objetivo (sectores declarados)
**Compradores particulares de usado** (núcleo) · **Concesionarios / dealers** (autorizados y no autorizados) · **Importadores de usado** ·
**Portales de anuncios/clasificados** (widgets que "hacen el anuncio transparente") · **Empresas del sector automoción** (procesos diarios) ·
**Webmasters/afiliados** (programa de afiliación).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía declarada | **26+ países de Europa + EE.UU. + Canadá**; "clientes alcanzados en 150+ países" | [VERIFICADO ≥2: homepage, vin-check, about] |
| Países enumerables (menú de idioma / menciones) | Polonia, Lituania, Letonia, Estonia, Rusia, Chequia, Rumanía, Hungría, Eslovenia, **Alemania, Italia, España, Portugal**, + menciones de **Francia, Bélgica** | [VERIFICADO: footer multidioma + vehicle-history]; [NO-VERIFICADO la lista completa exacta de los 26 — no se publica enumerada] |
| Volumen de vehículos | **500.000.000+ vehículos** en base | [VERIFICADO ≥2: homepage, vin-check] |
| Volumen de registros | **23.000.000.000 (23 mil millones) de registros** | [VERIFICADO ≥2: homepage, vin-check] |
| Fuentes de datos | **50.000+ instituciones** del sector automoción | [VERIFICADO ≥2: homepage, business-packages, vehicle-history] |
| Tracción comercial | **4M+ informes entregados · 4M+ clientes · 1.000+ clientes/día · 200M+ visitas web · 300+ dealers/depósitos socios** | [VERIFICADO: about-autodna] |
| Robo multi-país | Verificación contra bases de **robo de 13+ países** | [VERIFICADO: sample-report EU "Stolen Vehicle Database"] |
| Disponibilidad | Online, **24/7, 365 días**, entrega inmediata | [VERIFICADO ≥2: homepage, vehicle-history] |

### Scope de vehículo
- **Exclusivamente USADO / historial** (no hay catálogo de coche nuevo NVD ni libro de valoración).
- Identificación por **VIN de 17 caracteres** (no por matrícula como producto principal).
- Cobertura fuerte en **importados europeos** y **coches de origen US** (siniestros/salvage de subastas americanas) → nicho del importador.
- Tipos de vehículo: turismos principalmente (la descodificación VIN cubre lo que el WMI/VDS codifique).

---

## 3. Productos + campos atómicos

> El dato atómico se expone sobre todo en los **informes de muestra** (EU y US). Marketing no lista todo; lo enumerado abajo procede del
> análisis de los **sample reports** y de las páginas de producto. La estructura de secciones del informe **ES** el patrón de placement (ver §7).

### 3.1 Vehicle History Report — Europa (producto estrella)

**Cabecera "Prior / Key Information"** (tarjeta resumen arriba del informe):
- `VIN number` (17 caracteres)
- `Make and model` (marca y modelo)
- `Drive type` (tipo de tracción)
- `Vehicle age` (antigüedad del vehículo)
- `Latest odometer reading` (última lectura de odómetro)
- `Insurance expiration date` (fecha de expiración del seguro)
- `Report generation date` / timestamp de generación
- `QR code` (acceso digital al informe online)
- **Flags binarios "Key information":** `imported/domestic status` (importado/nacional) · `theft` (robo) · `damage` (daño) · `total loss` (siniestro total) · `service actions` (acciones de servicio)
- `History overview` — **contador-resumen de eventos** detectados (cuántos de cada tipo)

**Sección "Vehicle Information" (specs / decode VIN):**
- `Make and model`
- `Body type` (tipo de carrocería)
- `Engine type` (tipo de motor)
- `Engine power` (potencia)
- `Engine capacity / displacement` (cilindrada)
- `Fuel type` (combustible) *(expuesto en vin-check)*
- `Country of origin` (país de origen)
- `Model year` / `year of production`
- `Gearbox type` (tipo de caja de cambios)
- `Steering system` (posición de volante LHD/RHD)
- `VIN check digit verification` (verificación del dígito de control del VIN)
- `Date of first registration` (fecha de primera matriculación)

**Sección "Equipment" (equipamiento de fábrica):**
- `Upholstery color` (color de tapicería)
- `Paint color` (color de pintura)
- `Exterior finish` (acabado exterior)
- `Window tint` / `windows` (lunas/tintado)
- `Climate control / heating systems` (climatización/calefacción)
- `Navigation system` (navegador)
- `Audio system specifications` (equipo de audio)
- `Airbag count` (número de airbags)
- `Electric windows` (elevalunas eléctricos)
- `Mirrors` (espejos)

**Sección "Manufacturer Recalls" (llamadas a revisión):**
- `Problem description` (descripción del problema)
- `Effects of defect` (efectos del defecto)
- `Required repairs` (reparaciones requeridas)
- `Production date ranges` (rangos de fechas de producción afectadas)
- `Source citations` (citas de fuente)

**Sección "Stolen Vehicle Database":**
- `Multi-country theft check` (verificación contra bases de robo de 13+ países)
- `Theft status indicators` (indicadores por país)

**Sección "Odometer Readings" (clave anti-rollback):**
- `Mileage value` + `date` por cada lectura
- `Source annotation` por punto (inspección técnica / visita de servicio / matriculación)
- **Gráfico de línea interactivo** que visualiza la curva de km y delata retrocesos

**Sección "Vehicle History Timeline" (eventos cronológicos):**
- `Odometer reading + date` (lectura con fecha)
- `Registration / deregistration event` (alta/baja de matrícula)
- `Tax liens` (embargos/cargas fiscales)
- `Vehicle listing price` (precio anunciado en venta histórica)
- `Technical inspection record` (registro de inspección técnica / ITV)
- `Damage documentation` (documentación de daño/siniestro)
- `Vehicle purpose / use` (uso: **taxi**, **leasing/flota**, **rental/alquiler**, particular)
- `Location data` (ubicación geográfica del evento)
- `Service entry` (entrada de servicio: piezas reemplazadas)
- `Insurance history` (tipos de póliza: **Liability / Comprehensive / Assistance**) + `coverage gaps` (huecos de cobertura)

**Sección "Last Enquiries" (consultas previas — señal social/anti-fraude):**
- `Check frequency` (cuántas veces se ha consultado el VIN)
- `Check timestamps` (cuándo)
- `Geographic origin of checks` (desde qué país/región)
- **Mapa** de visualización de las consultas

**Sección "Vehicle Archive Photos":**
- `Historical images` (fotos de archivo de distintos periodos)
- `Availability indicators` (indicador de si hay fotos)

**Otros flags de riesgo (de la página VIN Check):**
- `Scrapping / scrapped records` (desguace)
- `Technical inspection failures` (ITV fallidas)
- `Roadworthiness issues` (aptitud para circular)
- `Check digit errors` (errores de dígito de control)
- `Import/export` (importación/exportación)

### 3.2 US Vehicle History Report — "Local history of the US vehicle"

> Datos **NMVTIS provistos por VinAudit Inc.** (socio oficial NMVTIS). Estructura distinta a la europea (orientada a *title brands* americanos).

**"Initial Information":** `Vehicle brand` · `model` · `version`

**"Vehicle Information" (specs US):**
- `Engine data` (datos de motor)
- `Fuel type` (combustible)
- `Fuel consumption` (consumo)
- `Dimensions` (dimensiones)
- `GVW` (Gross Vehicle Weight / peso bruto)
- `Manufacturer price (MSRP)` (precio de fábrica)
- `Current market value` (valor de mercado actual) ← *único punto "de valor" que da autoDNA, y solo en el informe US*

**"Title Brands Records" (4 subsecciones):**
- *Vehicle Status:* `Antique` · `Replica` · `Street Rod` · `ownership changes` · `buyback/warranty returns` (lemon) · `safety faults` · `VIN proceedings`
- *Vehicle Damage:* `junk` · `salvage` · `total loss`
- *Vehicle Use:* `taxi` · `agricultural` · `police` · `test vehicle`
- *Odometer Information:* `mileage discrepancies` · `replacement records`

**"Title Records":** historial de titularidad con `mileage reading` · `issuance date` · `state` (estado emisor)

**"Theft Records":** `stolen/recovered status` · `date` · `location` · `case number` · `reporter details`

**"Accidents Records":** `crash/collision event` · `date` · `location` · `case number` · `reporter information`

**"Junk, Salvage and Insurance Records":**
- *Insurer Entries:* `total loss claim` · `date` · `insurer details`
- *Vehicle Dismantling Shop Entries:* `scrappage proceedings` · `reporting person data`

**"Vehicle Sales Offers":** `listing price` · `advertised mileage` · `seller information`

**"Glossary":** definiciones de los tipos de *title brand* (capa educativa).

### 3.3 VIN decoder / VIN Check (gratuito — gancho)
- Descodificación de los 17 caracteres → `manufacturer` · `brand` · `model year` · `year of production` · `engine size` · `body style` · `drive type` · `engine type` · `factory equipment` · `assembly plant / production location` (carácter 11)
- **Preview de disponibilidad**: semáforo de **qué categorías de datos existen** para ese VIN antes de pagar (no muestra el contenido, solo si lo hay).

### 3.4 Business Packages (B2B — lotes de informes)
- Paquetes de **20 / 50 / 100 informes**, **validez 210 días**, compra anticipada sin necesidad de meter VIN al comprar.
- Soporte post-venta + representantes regionales on-site.

### 3.5 WebAPI + widgets (B2B — integración)
- `WebAPI` — "acceso a funciones avanzadas vía API" (consulta de historial/decode programática). *Endpoints/esquema no publicados.* [NO-VERIFICADO detalle técnico]
- `VIN decoder widget` — elemento embebible para webs de socios.
- `Search engine widget` — buscador embebible para portales/clasificados.

---

## 4. Metodología / fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Modelo | **Agregación de eventos** desde 50.000+ instituciones, no modelo estadístico/ML de precio | [VERIFICADO: business-packages, vehicle-history] |
| Tipos de fuente (EU) | Registros estatales, **aseguradoras**, talleres, estaciones de inspección, **instituciones financieras**, **bases de datos policiales/robo**, concesionarios, depósitos | [VERIFICADO ≥2: vehicle-history, vin-check] |
| Fuente US | **NMVTIS vía VinAudit Inc.** (proveedor oficial NMVTIS) — title agencies estatales, aseguradoras, desguaces/junk-salvage, programa CARS | [VERIFICADO ≥2: sample-report-usa (autoDNA), vinaudit.com] |
| Fotos | Imágenes de archivo capturadas en distintos periodos del ciclo de vida | [VERIFICADO: sample-report EU] |
| Anuncios históricos | Precios anunciados y km anunciados se integran al timeline (señal de mercado, no valoración) | [VERIFICADO: sample reports EU+US] |
| Naturaleza del dato | **Determinista/documental** (eventos datados con fuente), NO predictivo. Sin residual %, sin trade/retail recomendado, sin days-to-sell | [VERIFICADO por ausencia: no aparece en ningún producto] |
| Calidad/cobertura | **Muy desigual por país**: fuerte en CEE/importados; informes "vacíos" frecuentes en algunos mercados (quejas Trustpilot) | [VERIFICADO ≥2: trustpilot, reviews] |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **PDF online** | Informe descargable, **24/7/365**, entrega inmediata tras pago | [VERIFICADO ≥2: homepage, vehicle-history] |
| **Cuenta web / portal** | Login → compra de paquetes → consumo de informes | [VERIFICADO: business-packages] |
| **QR / JPG** | Código QR enlazando al informe online (compartible) | [VERIFICADO: sample report EU] |
| **Preview gratis** | Resultado de descodificación VIN + semáforo de disponibilidad de datos | [VERIFICADO ≥2: homepage, vin-check] |
| **WebAPI** | Acceso programático a funciones (B2B) — esquema no publicado | [VERIFICADO existencia; NO-VERIFICADO detalle] |
| **Widgets embebibles** | VIN decoder + buscador como elementos en webs de socios | [VERIFICADO: partners-area] |
| **Afiliación** | `afilio.autodna.com` (referidos) | [VERIFICADO: footer/partners] |
| **Idiomas** | PL, LT, LV, RU, CS, RO, ET, HU, SL, DE, IT, ES, PT, EN | [VERIFICADO: footer multidioma] |
| Pagos | Mastercard, Visa, PayPal, PayU, e-transfer, vouchers | [VERIFICADO: footer] |

---

## 6. Precio (descubrible)

| Producto | Precio | Notas | Estado |
|---|---|---|---|
| 1 informe | **24,99 €** | precio unitario base | [VERIFICADO ≥2: homepage, business-packages] |
| 2 informes | **39,99 €** | 19,99 €/informe | [VERIFICADO: business-packages] |
| 3 informes | **49,99 €** | 16,66 €/informe | [VERIFICADO: business-packages] |
| 20 informes (Business) | **259,00 €** | 12,95 €/informe · validez 210 días | [VERIFICADO ≥2: business-packages, blog] |
| 50 informes (Business) | **559,00 €** | 11,18 €/informe · validez 210 días | [VERIFICADO ≥2: business-packages, blog] |
| 100 informes (Business) | **959,00 €** | 9,59 €/informe · validez 210 días | [VERIFICADO ≥2: business-packages, blog] |
| WebAPI / widgets | **bajo cotización** | no publicado; contacto comercial | [NO-VERIFICADO precio] |
| **Suscripción recurrente** | auto-renovación; cargo el **primer día de cada periodo** | vía T&C; asociada a `detailedautodna.com` (origen de muchas quejas) | [VERIFICADO: terms-and-conditions, trustpilot] |

> Modelo: **pago por informe** (B2C) + **prepago por lote** (B2B) + **suscripción** (controvertida). Posicionamiento de precio "medio-alto"
> frente a competidores (carVertical similar/algo más barato; **VinAudit claramente más barato** en US).

---

## 7. Placement (DÓNDE colocan cada dato) — núcleo para cardeep

> El informe de autoDNA es un **PDF/online de una sola pieza, scroll vertical, por secciones apiladas**. El orden es deliberado:
> primero el **veredicto rápido** (flags + contador), luego la **identidad/specs**, luego cada **dossier de evento**.

| Dato / métrica | Dónde se coloca (sección / pantalla) |
|---|---|
| VIN, marca/modelo, tracción, antigüedad, último km, expiración seguro, fecha informe, QR | **Tarjeta "Prior / Key Information"** — cabecera del informe (lo primero que se ve) |
| Flags binarios (importado, robo, daño, siniestro total, acciones de servicio) | **"Key information"** dentro de la cabecera — semáforo de alarmas |
| Contador de eventos por tipo | **"History overview"** — resumen numérico junto a los flags |
| Specs decodificadas (carrocería, motor, potencia, cilindrada, combustible, caja, volante, país origen, dígito control) | Bloque **"Vehicle Information"** (segunda sección) |
| Equipamiento de fábrica (tapicería, pintura, climatización, navegador, audio, airbags, elevalunas, espejos) | Sección **"Equipment"** (lista) |
| Llamadas a revisión (problema, efecto, reparación, rango fechas, fuente) | Sección **"Manufacturer Recalls"** |
| Robo multi-país | Sección **"Stolen Vehicle Database"** (resultado por país) |
| Curva de kilometraje + fuente por lectura | Sección **"Odometer Readings"** — **gráfico de línea interactivo** con anotación de fuente por punto (delata rollback visualmente) |
| Eventos datados (km, alta/baja, embargo, precio anunciado, ITV, daño, uso taxi/leasing, ubicación, servicio, seguro) | **"Vehicle History Timeline"** — lista cronológica, un *card* por evento con su ubicación |
| Cuántas veces / desde dónde se ha consultado el VIN | Sección **"Last Enquiries"** + **mapa** (señal social / anti-fraude) |
| Fotos de archivo | Sección **"Vehicle Archive Photos"** |
| Acceso/compartir online | Bloque **"QR Code"** (cierre del informe) |
| Disponibilidad de datos (pre-pago) | **Preview gratis** tras meter el VIN en home — semáforo de qué categorías existen, sin contenido (gancho de conversión) |
| **US:** title brands, title records, theft, accidents, junk/salvage/insurer, sales offers | Informe US con **secciones propias** (orientadas a *title brand* NMVTIS) + **Glossary** educativo al final |
| **US:** valor de mercado actual + MSRP | Bloque **"Vehicle Information"** del informe US (único sitio donde aparece "valor") |
| Catálogo de paquetes y precios | **Página `/business-packages`** y `/packages` (tabla de lotes con €/informe y ahorro) |
| VIN decoder / buscador | **Widgets embebidos** en webs de socios (placement externo, fuera del propio sitio) |

**Lecciones de placement para cardeep:**
1. **Veredicto antes que detalle:** flags + contador arriba, evidencia abajo. El usuario sabe en 2s si el coche "huele mal".
2. **Semáforo de disponibilidad gratis** como conversión: enseñar *que hay* dato sin enseñar *el* dato.
3. **Odómetro como gráfico anotado por fuente** > tabla: el retroceso se ve, no se lee.
4. **Timeline cronológico geolocalizado** como columna vertebral del historial.
5. **"Last Enquiries" + mapa**: convertir el propio tráfico de consultas en una señal de confianza/uso del coche.

---

## 8. Diferencial (lo que ofrece y otras no)

- **Profundidad en importados CEE + origen US:** fuerte en coches de Europa central/oriental y **siniestros/salvage de subastas americanas** → nicho del importador europeo. [VERIFICADO ≥2: comparativas vinaudit, carlytics]
- **Cobertura de robo multi-país (13+ países)** en un solo informe. [VERIFICADO: sample EU]
- **Fotos de archivo** del vehículo en distintos periodos (donde existan). [VERIFICADO ≥2: sample, vinaudit comparison]
- **"Last Enquiries" con mapa** — señal de cuántas veces/desde dónde se ha mirado el VIN (poco común). [VERIFICADO: sample EU]
- **Antigüedad/escala de marca:** decano del segmento en Europa (líder histórico antes del auge de carVertical), 4M+ informes. [VERIFICADO: about, comparativas]
- **Doble motor de datos:** agregación propia EU + reventa NMVTIS (VinAudit) US → un único punto para ambos orígenes. [VERIFICADO ≥2]
- **Capa B2B de integración** (WebAPI + widgets) que muchos puros-B2C de VIN no exponen. [VERIFICADO: partners-area]

---

## 9. Gaps (lo que NO ofrece)

- **No es valoración:** sin **residual value %**, sin **trade/retail price recomendado**, sin **days-to-sell**, sin **market days supply**,
  sin **price-to-market %**, sin **curva de depreciación**, sin **índices de oferta/demanda**. Su único "valor" es `current market value` + MSRP, y **solo en el informe US**. [VERIFICADO por ausencia]
- **Sin verificación blockchain/tamper-proof** (carVertical sí la usa como diferencial). [VERIFICADO: vinaudit comparison]
- **Sin aprobación NMVTIS propia** en US: depende de VinAudit como intermediario (menos credibilidad regulatoria directa, y más caro que ir a VinAudit). [VERIFICADO ≥2]
- **Calidad/cobertura muy desigual por país:** **informes "vacíos" frecuentes** (solo specs de decoder, sin historial real) → queja nº1. [VERIFICADO ≥2: trustpilot, reviews]
- **Política de reembolso percibida como mala:** muchos reportan **no reembolso ante informe vacío**; otros sí lo consiguen → inconsistente. [VERIFICADO ≥2: trustpilot]
- **Patrón de suscripción recurrente** (auto-renovación) y **dominio satélite `detailedautodna.com`** con quejas de cargos no esperados → riesgo reputacional. [VERIFICADO ≥2: terms, trustpilot]
- **WebAPI sin documentación pública** (endpoints, esquema, rate limits, formatos) — fricción para integradores frente a APIs documentadas (auto.dev, DataOne, Vehicle Databases). [VERIFICADO: ausencia de docs públicas]
- **Lista de 26 países no enumerada públicamente** ni cobertura/profundidad por país transparente. [VERIFICADO: ausencia]
- **No cubre matrícula como entrada principal** (centrado en VIN); búsqueda por VRM/plate no es el producto. [VERIFICADO]
- **Trustpilot 2,3/5** — confianza pública baja vs competidores mejor valorados. [VERIFICADO]

---

## 10. Fuentes

**Propias (autodna.com):**
- https://www.autodna.com/ (homepage — stats, free lookup, secciones)
- https://www.autodna.com/company/about-autodna/ (identidad, cifras)
- https://www.autodna.com/vehicle-history (contenido informe EU, fuentes, países)
- https://www.autodna.com/vin-check (categorías de riesgo, escala de datos)
- https://www.autodna.com/decoder-vin-checker (campos del decoder)
- https://www.autodna.com/sample-reports/vehicle-history-report-autodna (informe EU — campos atómicos)
- https://www.autodna.com/sample-reports/vehicle-history-usa (informe US — NMVTIS/VinAudit, campos)
- https://www.autodna.com/business-packages (precios y lotes B2B)
- https://www.autodna.com/blog/business-packages/ (detalle paquetes negocio)
- https://www.autodna.com/company/partners-area (WebAPI, widgets, sectores B2B)
- https://www.autodna.com/company/partners (logos OEM — coberturas, no integraciones)
- https://www.autodna.com/terms-and-conditions (facturación recurrente, reembolsos 14 días)

**Terceros / verificación cruzada:**
- https://www.trustpilot.com/review/autodna.com (TrustScore 2,3/5; quejas)
- https://www.trustpilot.com/review/detailedautodna.com (dominio satélite, suscripción)
- https://www.vinaudit.com/autodna-vs-carvertical-vs-vinaudit (comparativa, gaps, NMVTIS)
- https://www.vinaudit.com/nmvtis-data + https://vehiclehistory.bja.ojp.gov/nmvtis_vehiclehistory (VinAudit como proveedor oficial NMVTIS)
- https://www.carlytics.eu/autodna-vs-carvertical · https://autocheck24.eu/carvertical-review/ · https://www.csabastefan.com/en/carvertical-experiences-comparison-autodna.php (comparativas EU, fundación 2009, posicionamiento)
- https://tracxn.com/d/companies/autodna/... + Crunchbase (perfil corporativo; fundación 2003 — discrepancia; sin funding)
- https://find-and-update.company-information.service.gov.uk/company/15234694 (AUTO DNA LTD, entidad UK)

---

### Notas de verificación
- **Fundación:** triple discrepancia (2003 Crunchbase/Tracxn · 2009 comparativas · **2010 autoDNA**). Se lidera con la cifra propia (2010 / "15 años") y se marcan las demás.
- **HQ:** una comparativa de terceros dice "Warsaw"; prevalece la fuente legal propia (**Łódź**).
- **Owner:** independiente sin financiación; accionariado último **no publicado**; asociación "F Kenworthy" de Tracxn descartada como ruido.
- **WebAPI:** existencia verificada, **detalle técnico no publicado** → marcado NO-VERIFICADO donde aplica.
- **US data:** sourcing **VinAudit/NMVTIS** verificado por la propia autoDNA + VinAudit (≥2 fuentes).
