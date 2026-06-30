# BCA (British Car Auctions) — Auditoría atómica

> **slug:** `bca` · **subdominio cardeep:** **wholesale-intelligence** · **web:** https://www.bca.co.uk/ (UK) · https://www.bca.com/ (grupo Europa)
> **Auditado:** 2026-06-30 · **Doctrina VAM:** cada afirmación con fuente; `[VERIFICADO]` (leído en página oficial vía navegador real + ≥2 fuentes o confirmado en la propia web), `[PARCIAL]` (1 fuente / agregador), `[CLAIM-VENDOR]` (marketing del propio BCA sin verificación independiente), `[RECONSTRUIDO]` (compongo de varias páginas), `[NO-VERIFICADO]`.
> **Naturaleza:** **la mayor empresa de remarketing (subasta MAYORISTA B2B) de vehículos usados de Europa.** No es una "guía de valor" tipo cap hpi ni un índice tipo Manheim MMR/MUVVI: su núcleo es el **marketplace de subasta físico + digital**, y su "inteligencia" es **dato transaccional first-party (precio de martillo real)** procesado por un motor de valoración propio (**BCA Market Price**, Azure ML, sobre ~5M de ventas históricas de subasta UK) que alimenta sus herramientas de tasación de dealer (**Dealer Pro / Consumer Pro**), más una capa de **datos de condición por vehículo** (grading cosmético 1–5, informe mecánico Assured/Essential Check/128, salud de batería EV vía AVILOO) y un **reporte mensual de valores de mercado** (precio medio, MoM%, YoY%).
> **Posición frente a cardeep:** es el equivalente europeo de **Manheim** (misma clasificación `wholesale-intelligence`). **Opera EN ESPAÑA** con centros físicos (Azuqueca, Bellvei, La Luisiana) y subastas online — caso raro entre los auditados: BCA **sí tiene presencia española viva**. Su patrón de **ficha de vehículo** (search card + VDP con grade/batería/precio guía) es el blueprint de placement; su dato es **hammer price + condición**, no huella digital de punto de venta retail (territorio de cardeep).
> **Ecosistema:** marca **B2B** de **Constellation Automotive Group** (TDR Capital). Hermanas: **We Buy Any Car** (compra a particular), **cinch** (retail B2C online), **CarNext**, **elmo** (suscripción EV), **Marshall Motor Group** (grupo dealer). **OJO:** **cap hpi NO es hermana de BCA** (cap hpi es de **Solera**, verificado en `cap-hpi.md`); no confundir el ecosistema.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **BCA** (British Car Auctions); en Europa "BCA Group" / "BCA Europe" | [VERIFICADO] |
| Razón social (UK) | **British Car Auctions Limited**, registrada en Inglaterra y Gales **No. 00438886** | [VERIFICADO: footer bca.co.uk] |
| Domicilio social (UK) | **Form 2, 18 Bartley Wood Business Park, Bartley Way, Hook, Hampshire, RG27 9XA, UK** · VAT GB 188155238 | [VERIFICADO: footer bca.co.uk] |
| Sede operativa histórica | **Blackbushe Airport, Yateley** (mayor sitio de subasta de vehículos de Europa) | [VERIFICADO ≥2: cardealermag, locations] |
| Owner / grupo | **Constellation Automotive Group Ltd** (propiedad de **TDR Capital**, private equity) | [VERIFICADO ≥2: Wikipedia, Car Dealer Mag, AIM Group] |
| HQ del grupo | **Bedford, Inglaterra** (Constellation) | [PARCIAL: Wikipedia] |
| Fundación | **1946**, como **Southern Counties Car Auctions**, por el oficial de la Royal Navy **David Wickins** (Farnham, Surrey). Primera subasta: **14 coches vendidos** | [VERIFICADO ≥2: Wikipedia, bca.com/about, David Wickins Wiki] |
| Antigüedad declarada | **"For over 70 years"** (bca.com) | [VERIFICADO: bca.com] |
| Posición | **"Europe's largest vehicle remarketing company"** / **"UK's largest used vehicle business"** | [VERIFICADO ≥2: bca.com, bca.co.uk] |

**Línea de tiempo de propiedad (verificada vía Wikipedia + prensa):**

| Año | Hito |
|---|---|
| **1946** | David Wickins funda Southern Counties Car Auctions → British Car Auctions; la convierte en el mayor negocio de subastas del mundo | [VERIFICADO] |
| Finales 1980s | Hawley Goodall (matriz de BCA) hace reverse takeover de **ADT Security Services**; ADT vende por separado las operaciones de Norteamérica y Europa | [VERIFICADO: Wikipedia] |
| **1995** | El brazo europeo lo compra un consorcio de ~40 inversores privados (incl. **Lord Ashcroft**) | [VERIFICADO: Wikipedia] |
| **Sep 2006** | Comprada por **Samuel Montagu & Co.** (división de HSBC) | [VERIFICADO: Wikipedia] |
| **Feb 2010** | Adquirida por **Clayton, Dubilier & Rice (CD&R)** (private equity) | [VERIFICADO ≥2: Wikipedia, CD&R] |
| **Mar 2015** | **Haversham Holdings** hace reverse takeover y la renombra **BCA Marketplace plc** (cotiza en LSE) por ~£1.2bn | [VERIFICADO ≥2: Wikipedia, Car Dealer Mag] |
| **Nov 2019** | Adquirida y retirada de bolsa por **TDR Capital** | [VERIFICADO ≥2] |
| **Oct 2020** | Renombrada **Constellation Automotive Group Ltd** | [VERIFICADO ≥2: Car Dealer Mag, AIM Group] |

**Marcas del grupo Constellation:** **BCA** (B2B/subasta), **We Buy Any Car** (compra a particular), **cinch** (retail B2C online), **CarNext**, **elmo** (suscripción de EV), **Marshall Motor Group** (grupo de concesionarios). `[VERIFICADO: Wikipedia Constellation]` · Adquisición reportada por prensa de **Aston Barclay** (subastas) por el dueño de BCA `[PARCIAL: Fleet News; no listada aún en Wikipedia]`.

**Estadísticas de escala:**

| Métrica | Valor | Fuente / fecha |
|---|---|---|
| Vehículos vendidos / año | **>1.000.000** (Europa) | bca.com/about `[VERIFICADO ≥2]` |
| Volumen semanal | **>12.000 vehículos/semana** (físico + internet) | WebSearch agregada `[PARCIAL]` |
| Turnover anual | **>£4.000 millones** de vehículo vendido | growjo/WebSearch `[PARCIAL]` |
| Cuota subasta UK | **>50%** de todos los coches vendidos por subasta en UK | WebSearch `[PARCIAL]` |
| Centros (Europa) | **~50 centros** en **10 países** | bca.com `[VERIFICADO]` |
| Base de dato de valoración | **~5.000.000 de ventas históricas de subasta UK** (BCA Market Price) | am-online; motortrader `[VERIFICADO ≥2]` |

**Categorías de producto:** (1) **Marketplace de subasta** mayorista físico + digital (núcleo); (2) **Motor de valoración / inteligencia de precio** (BCA Market Price); (3) **Herramientas de tasación de dealer** (Dealer Pro, Consumer Pro, uCheck); (4) **Datos de condición por vehículo** (Vehicle Condition Grading, BCA Assured, Essential Check, 128 Inspection, EV Battery Health Grading); (5) **Reporte mensual de valores de mercado**; (6) **Servicios físicos / logística** (Automotive Services, Logistics, Vehicle Preparation, Bodyshop, Supreme/Wheel Refurbishment, Imaging/AutosOnShow, Image Downloads); (7) **Financiación de stock** (Partner Finance); (8) **Canal alternativo** (Driver Sales).

**Cliente objetivo:** **vendedores (vendors):** OEMs/fabricantes e importadores, **leasing / contract hire / renting** (p.ej. subastas Alphabet en España), **flotas corporativas**, **rent-a-car**, **dealers / grupos de concesionarios**, **vehicle buying companies** (p.ej. We Buy Any Car). **Compradores:** dealers franquiciados e independientes, traders, exportadores (30+ países compradores). Es **exclusivamente profesional/B2B** ("exclusivo para profesionales del automóvil"). (Fuentes: bca.co.uk/about-us, bca.com/es_ES. `[VERIFICADO]`)

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Geografía núcleo | **Reino Unido** (UK's largest used vehicle business) | [VERIFICADO] |
| Europa | **10 países con marketplace local:** UK, Francia, Portugal, **España**, Alemania, Países Bajos, Suiza, Dinamarca, Italia, Suecia (+ Noruega listada) | [VERIFICADO ≥2: bca.com] |
| Selling / buying countries | **~14 países vendedores**, oferta a **>30 países compradores** | [VERIFICADO: bca.com/es_ES] |
| **España (clave cardeep)** | **BCA España** opera centros físicos: **Azuqueca** (Guadalajara, martes 09:30), **Bellvei** (Tarragona, martes 10:00), **La Luisiana** (Sevilla). Subastas **xBid** online + **Live Online** + **Subastas Alphabet** (renting, km garantizados) + **subastas diarias de BEV** con informe de salud de batería AVILOO | [VERIFICADO: bca.com/es_ES] |
| Nuevo vs usado | **USADO / wholesale** es el núcleo (remarketing entre profesionales). Además ofrece **New Vehicle Services** (PDI, servicing, accessory fitment, customización, almacenaje, logística port-to-dealer) como **servicio operacional**, no como valoración de coche nuevo | [VERIFICADO: bca.co.uk/about-us] |
| Tipos de vehículo | **Coches**, **LCV/vans** (light commercial), **Motorbikes** (motos), **Caravans & Motorhomes** (leisure vehicles), **EV/Hybrid**, **non-runners** | [VERIFICADO: facetas de búsqueda + grading pages] |
| Frescura del dato | Subastas físicas semanales + **online 24/7** (Bid Now timed, Buy Now fijo, EuroShop); valoración Market Price en **tiempo real** sobre hammer prices; reporte de mercado **mensual** | [VERIFICADO] |
| Naturaleza del dato (clave) | **Transacción REAL de subasta first-party (precio de martillo entre profesionales)**, no listing/asking price. Es la misma ventaja estructural que Manheim MMR | [VERIFICADO] |

---

## 3. Productos + campos atómicos

> Todas las listas de campos de las secciones 3.3–3.7 fueron **leídas directamente de las páginas oficiales de BCA vía navegador real** (Playwright, sorteando el bloqueo 403 a fetchers). Son por tanto fuente primaria leída = `[VERIFICADO]`.

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **BCA Market Price** | Motor de valoración propio (Azure ML) sobre ~5M ventas de subasta UK | Valoración en tiempo real | ~6 |
| **BCA Dealer Pro** | App de tasación + valoración + gestión de stock de part-exchange | Appraisal report + valor + disposal | ~15 |
| **BCA Consumer Pro** | API white-label de valoración de part-ex en web del dealer | Valor instantáneo (hammer-based) | ~4 |
| **Vehicle Condition Grading** | Grade cosmético estándar (exterior+interior) | Grade 1–5 / Unclassified + kipper | ~12 |
| **BCA Assured** | Informe mecánico de **45+ puntos** (vehículos <8 años / <120k mi) | OK/Issue por check + notas | ~45 |
| **BCA Essential Check** | Informe mecánico de **45+ áreas** (vehículos >8 años / >120k mi) | OK/Issue por check + notas | ~40 |
| **BCA 128 Vehicle Inspection** | Inspección de **128 puntos** + road test (vehículos >£45k) | Summary OK/Issue + PDF | ~7 áreas |
| **EV Battery Health Grading** | Salud de batería de tracción (powered by AVILOO) | Grade A–E + SoH% + FLASH report | ~3 |
| **Listing / Vehicle Search + BCA Buyer app** | Ficha de vehículo en subasta | Identidad + precio guía + grade + reports | ~20 |
| **Market Report mensual** | Comentario de valores de mercado | Precio medio + MoM% + YoY% (cars/LCV) | ~6 |

### 3.1 BCA Market Price (motor de valoración / inteligencia de precio)

> El activo de inteligencia de BCA. No se vende suelto: **subyace a Dealer Pro y Consumer Pro**.

| Campo / elemento | Definición | Estado |
|---|---|---|
| **Real-time valuation** | Valoración en tiempo real basada en **precios de martillo (hammer prices) actuales** de subasta BCA | [VERIFICADO: dealer-pro, consumer-pro] |
| **Base de datos** | **~5 millones de ventas históricas de subasta UK** (dataset propietario) | [VERIFICADO ≥2: am-online, motortrader] |
| **Variables del modelo** | Condición **cosmética**, condición **mecánica**, **color** y **equipamiento** del vehículo | [VERIFICADO: am-online] |
| **Motor** | Métodos estadísticos + **Microsoft Azure Machine Learning**; modelos en mejora/testeo continuo | [VERIFICADO: am-online] |
| **"Largest real time dataset in the industry"** | Claim de BCA sobre la base que alimenta Dealer Pro | [CLAIM-VENDOR: dealer-pro] |

### 3.2 BCA Dealer Pro (tasación + valoración + disposal)

> App (iOS/Android/UWP/desktop, online + offline) "appraise it, value it, maximise it" para gestionar part-exchange de appraisal a disposal.

| Campo atómico / función | Definición | Estado |
|---|---|---|
| **Guided appraisal journey** | Proceso de tasación guiado paso a paso con prompts | [VERIFICADO: dealer-pro; aftermarketonline] |
| **Vehicle lookup** | Carga de datos del vehículo (requiere Wi-Fi solo para el lookup) | [VERIFICADO: dealer-pro FAQ] |
| **Vehicle details** | Detalles del vehículo y **service history** | [VERIFICADO: aftermarketonline] |
| **Beauty images** | Imágenes "de belleza" del vehículo | [VERIFICADO] |
| **Damage images** | Imágenes de daños | [VERIFICADO] |
| **Kipper diagrams** | Registro de daños exterior/interior con diagramas estándar "kipper" | [VERIFICADO: aftermarketonline] |
| **Mechanical condition** | Documenta condición mecánica | [VERIFICADO] |
| **Non-standard equipment** | Registra equipamiento no estándar | [VERIFICADO] |
| **Real-time valuation** | Valoración en tiempo real (BCA Market Price) | [VERIFICADO: dealer-pro] |
| **Customer/salesperson signature** | Captura de firma de cliente y comercial | [VERIFICADO: aftermarketonline] |
| **Appraisal report (PDF/email)** | Informe de tasación que se imprime o envía por email | [VERIFICADO] |
| **Group stock management** | Gestión de stock de part-exchange en múltiples sitios | [VERIFICADO: dealer-pro] |
| **Disposal to auction** | Envío del vehículo a subasta BCA en pocos clics | [VERIFICADO] |
| **Funding request** | Solicitud de financiación vía cuenta BCA Partner Finance vinculada | [VERIFICADO: dealer-pro] |
| **DMS / lead-management integration** | Integra con **DealerWeb, enquiryMAX, Pinewood** (+ integraciones a medida) | [VERIFICADO: dealer-pro FAQ] |
| **Role-based access** | Permisos por rol configurables | [VERIFICADO: dealer-pro FAQ] |

### 3.3 BCA Consumer Pro (API white-label de valoración)

| Campo / función | Definición | Estado |
|---|---|---|
| **Instant online valuation** | Valoración de part-exchange en segundos en la web del dealer, **basada en hammer prices actuales** de BCA | [VERIFICADO: consumer-pro] |
| **White-label / branding** | El cliente solo ve la marca del dealer en todo el journey | [VERIFICADO] |
| **Drop into Dealer Pro** | Las valoraciones completadas caen directamente en la cuenta Dealer Pro | [VERIFICADO] |
| **Consumer Pro + (underwrite)** | Con "Consumer Pro +", BCA **underwrite** (garantiza la compra del) el part-exchange | [VERIFICADO] |
| **API integration** | API integrable con la web del dealer; sin set-up fees adicionales | [VERIFICADO] |

### 3.4 Vehicle Condition Grading (grading cosmético — Cars; equivalente UK y Europa)

> Escala **1–5 + Unclassified** sobre la condición **cosmética** (exterior + interior). Estándar alineado con NAMA. Revisión con **Standard Viewing Angle (SVA) a 2 metros, a 45° y 90°** (no bodyline check). Defectos significativos se imagen. Hay grading equivalente para **LCV (Commercial Vehicle Cosmetic Grading)**, **Motorbikes** y **Leisure Vehicles** (interior+exterior+habitación).

| Campo atómico | Definición | Estado |
|---|---|---|
| **Condition Grade** | **Grade 1 / 2 / 3 / 4 / 5 / Unclassified** (1 = menos daños) | [VERIFICADO: car-condition-grading] |
| **Grade 1** | Dents ≤30mm y/o scratches ≤25mm; chips ≤10mm en cristal; scratches ≤100mm en parachoques; ruedas con scratches/corrosión; interior con scuffing menor | [VERIFICADO] |
| **Grade 2** | Defectos de G1 + uno de: paint defect >25mm en panel o >100mm en bumper / dent >30mm / defecto cristal >10mm / trim significativo | [VERIFICADO] |
| **Grade 3** | G1+G2 + hasta 5 paneles con paint defect >25mm; hasta 3 paneles/bumpers con dents >30mm; trims/parts significativos | [VERIFICADO] |
| **Grade 4** | + panel con daño significativo (>30%) o crack en bumper; hasta 10 paneles con paint defect; hasta 7 con dents >30mm; múltiples trims | [VERIFICADO] |
| **Grade 5** | + >2 paneles/bumpers con cracks/daño significativo; ≥8 paneles con dents >30mm; ≥11 con paint defect; hasta 1 **panel estructural** con daño >30%; tears/holes en techos convertibles | [VERIFICADO] |
| **Unclassified** | Excede criterio de G5 / daño sustancial de accidente / partes significativas ausentes / uneconomical to appraise | [VERIFICADO] |
| **Structural panels (definición)** | **Roof panel, roof soft tops, rear quarter panels** | [VERIFICADO] |
| **Poor Previous Paintwork (PPR)** | Flag si es visible desde 2m en luz normal | [VERIFICADO] |
| **Kipper view** | Diagrama de daños (solo orientativo; complementa material escrito + fotográfico) | [VERIFICADO] |
| **Exterior cosmetic defects** | Dents, scratches, chips, paint defects, corrosión de ruedas (lista por panel) | [VERIFICADO] |
| **Interior cosmetic defects** | Scuffing, trim items (excluye operación mecánica/eléctrica, valet, desgaste normal) | [VERIFICADO] |
| **Ajuste >10 años** | En vehículos ≥10 años no se registran ítems menores (dents <30mm, scratches <25mm, chips, scuffs) | [VERIFICADO] |
| **Imagen de defectos** | Defectos significativos imagenados si visibles a la luz del día | [VERIFICADO] |

### 3.5 BCA Assured (informe mecánico 45+ puntos — <8 años / <120k millas)

> Inspección mecánica por inspectores **independientes**. Aplica a vehículos **<8 años, <120.000 millas**, todas las marcas, **EV/Hybrid, Motorhomes, LCVs**. Salida: resumen por categorías + estado por check + sección de notas.

**Engine Bay:** `engine oil level` · `oil/coolant contamination` · `brake fluid level` · `power steering fluid level` · `coolant system level` · `battery state of health (arranque)` · `engine running/smoothness` · `engine smoking` · `exhaust (leaks/secure)` · `aux belt/pulley noise`.
**Tyres:** `tyre tread` (4 ruedas × 3 puntos con galga) · `tyre observations` (cortes en pared, patrones de desgaste, pinchazos, lona expuesta).
**Interior — warning lights:** `engine management light` (+ diagnóstico OBD conectado si encendida) · `ABS warning light` · `brake wear indicator light` · `airbag warning light` · `other warning light`.
**Dynamic Operation:** `steering noise` (full lock L/R) · `handbrake/parking brake test` · `static gear selection` · `first & reverse test drive & clutch slipping` (≤20m, ≤15mph) · `brake efficiency test` (medidor de fuerzas g) · `suspension ride height` (20m) · `aircon receives power` · `S-Nav receives power` · `ICE receives power` · `central locking` (excl. key fob) · `convertible/sunroof electrics` · `horn`.
**EV/Hybrid Specific:** `traction pack diagnostics` (máquina de diagnóstico) · `inverter coolant level` · `charging status` (incl. carga regenerativa bajo frenado; celda individual NO testeada) · `charge port condition` · `charge lead 1 condition` (OEM o no) · `charge lead 2 condition` · `drive test take-up/deceleration` · `static ready-to-run selection`.
**Essential checks:** `electric window movement` · `wiper arm movement + washers` · `headlights` (high/low beam) · `brake lights` · `fog lights` · `side lights` · `indicators/hazards`.
**Notes section:** detalle adicional del check.
*(Fuente: bca.co.uk/services/assured, leído íntegro. `[VERIFICADO]`)*

### 3.6 BCA Essential Check (informe mecánico 45+ áreas — >8 años / >120k millas)

> Contraparte de Assured para vehículos **viejos / alto km** (>8 años **o** >120.000 millas), incl. LCVs. **£12.50 ex VAT**. **NB: OBD plug-in NO se realiza** (diferencia clave vs Assured). No es provenance/historial (es mecánico cosmético-funcional).

`engine running/starts/battery SoH` · `engine running/smoothness` · `engine smoking` · `coolant system level` · `engine oil level` · `oil/coolant contamination` · `tyre tread` (NSF/NSR/OSF/OSR × 3 puntos; LCV solo NS/OS; **sin observaciones de pared**) · **warning lights:** engine management, brake wear, ABS, oil, airbag, glow plug, other (comprobadas tras 10s con motor en marcha) · `handbrake test` · `static gear selection` · `clutch slip test` (manual) · `brake pedal pressure/servo` · `electric windows` (NSF/NSR/OSF/OSR) · `tailgate electric window` · `door mirror (NS/OS) glass + adjustment` · `rear view mirror` · `wiper arm movement` (front/rear) · `screen washers` (front/rear) · `horn` · **Driver visibility:** `headlights` (high/low, NSF/OSF) · `running/side lights` · `brake lights` (NS/OS/high level) · `fog lights` · `indicators/hazards` · `notes section`.
*(Fuente: bca.co.uk/services/essential-check, leído íntegro. `[VERIFICADO]`)*

### 3.7 BCA 128 Vehicle Inspection (alto valor >£45k)

> Inspección de **128 puntos** por inspectores independientes para vehículos **>£45.000** (EV/hybrids incl.). Incluye **road test offsite de hasta 10 millas / 70 mph** (donde esté permitido). Primera página = **summary OK / Issue** por área; informe **PDF descargable**.
**Áreas cubiertas:** `exhaust system` · `interior fittings and electrical controls` · `engine compartment` · `transmission and fuel system` · `road test (≤10 mi, 70 mph)` · `brakes, wheels and tyres` · `front and rear suspension, steering and underframe`.
*(Fuente: bca.co.uk/services/128-vehicle-inspection. `[VERIFICADO]`)*

### 3.8 BCA EV Battery Health Grading (powered by AVILOO)

| Campo atómico | Definición | Estado |
|---|---|---|
| **Battery Health Grade** | **A–E** (similar a condition rating) | [VERIFICADO: ev-battery-grading] |
| **State of Health (SoH) %** | Porcentaje de salud de la batería de tracción (más alto = mejor) | [VERIFICADO] |
| **AVILOO FLASH Test report + score** | Informe completo y score detallado (test independiente vía **OBD**); proveedor **AVILOO** | [VERIFICADO] |
| **Aplica a** | EVs en subasta (incl. subastas diarias de BEV en España) | [VERIFICADO: ev-battery-grading, bca.com/es_ES] |
| **Coste** | **£24 + VAT por vehículo** | [VERIFICADO] |
| **Reporte descargable/imprimible** | Para mostrar en venta / ofrecer como descarga | [VERIFICADO] |

### 3.9 Listing / Vehicle Search + BCA Buyer app (campos de la ficha de subasta)

> Acceso a stock vivo requiere **login de trade buyer** (auth.bca.co.uk). Campos reconstruidos de facetas de búsqueda públicas + descripción de la app BCA Buyer (App Store / Google Play / prensa).

**Identidad / atributos:** `Make` · `Model` · `Model group` · `Derivative` · `Year/Age` · `Mileage` · `Colour` · `Fuel type` (incl. Electric) · `Body type` · `Vehicle type` (Cars / LCV / Motorbikes / Caravans & Motorhomes) · `Equipment/spec` (búsqueda free-text: p.ej. *climate control*, *towbar*) · `registration details`.
**Subasta / comercial:** `Auction centre / location` · `Sale date` · `Vendor` · `Sale channel` (**Bid Now** timed / **Buy Now** fijo / **Live Online**) · `non-runner` flag.
**Precio / valor:** `Guide price` · `CAP Clean price` (referencia usada como filtro) · (hammer price tras venta).
**Condición / reports embebidos:** `Condition Grade (1–5)` · `BCA Assured report` (donde aplica) · `Essential Check` · `EV Battery Health Grade (A–E + SoH%)` · `images` (full-screen, pan/zoom) · `Image Downloads` (alta calidad tras compra).
**Interacción:** `concealed proxy bid` (puja proxy anticipada) · `live sale audio/video` · `saved searches` · `personal notes/watchlist`.
*(Fuentes: bca.co.uk facetas; BCA Buyer app stores; Business Car. `[VERIFICADO búsqueda+app]`)*

### 3.10 Market Report mensual (capa de inteligencia de mercado publicada)

| Métrica | Definición | Estado |
|---|---|---|
| **Average used car selling price (£)** | Precio medio de coche usado vendido en BCA en el mes | [VERIFICADO ≥2: Business Car, Motor Finance] |
| **Month-on-month change (£ y %)** | Variación mensual (p.ej. jul-2024 £7.800, +£233 / +3.2%) | [VERIFICADO] |
| **Year-on-year comparison** | Comparativa interanual (p.ej. +6.4% YoY en agosto) | [VERIFICADO] |
| **Average LCV/van selling price** | Precio medio de furgoneta (p.ej. sep-2025 £8.460, +7.2% MoM / +13.6% YoY) | [VERIFICADO ≥2] |
| **By sector/segment** | Comentario por sectores de mercado | [PARCIAL] |
| **Demand / engagement commentary** | Comentario cualitativo de demanda y "engagement" (COO Stuart Pearson) | [VERIFICADO] |

### 3.11 Servicios físicos / logística (no-dato, parte del ecosistema 360°)

- **BCA Automotive Services** — **mayor flota de transporte (transporter) de UK**; mueve vehículos de OEM de puerto a dealer y dealer→Exchange. `[VERIFICADO]`
- **BCA Logistics** — logística + inspección nacional; movimientos single + inspecciones para leasing/captive finance. `[VERIFICADO]`
- **Vehicle Preparation / Vehicle Bodyshop** — preparación y reparación on-site para subir el grade. `[VERIFICADO]`
- **Supreme Wheels / Wheel Refurbishment** — re-ingeniería de llantas a estándar OEM, **>500.000 ruedas/año**; "Europe's largest alloy wheel re-engineering specialist". `[VERIFICADO]`
- **Vehicle Imaging (AutosOnShow)** — vídeo + imágenes para dealers. `[VERIFICADO]`
- **Image Downloads** — descarga de imágenes de alta calidad tras compra. `[VERIFICADO]`
- **New Vehicle Services** — PDI, servicing, accessory fitment, customización, storage, logística port-to-dealer. `[VERIFICADO]`
- **Used Vehicle Refurbishment** — fleet management, end-of-life defleet, refurbishment. `[VERIFICADO]`
- **BCA Partner Finance** — floor-plan / stocking finance: **120 días** de financiación de compras en subasta BCA (incl. fees + VAT), cars + LCV; **>100.000 contratos** y **£1bn/año**; tecnología **Solifi**; también funding de part-exchange. `[VERIFICADO ≥2]`
- **BCA Driver Sales** — canal de remarketing alternativo (venta directa al conductor/empleado). `[VERIFICADO: services list]`
- **uCheck** — appraisal guiado para clientes offsite (vinculado a Dealer Pro). `[PARCIAL: citado en WebSearch dealer-pro]`

---

## 4. Metodología / fuentes de datos

- **Dato primario = transacción REAL de subasta first-party (hammer price).** BCA vende **>1M veh/año** en sus propias subastas; ese flujo transaccional es la materia prima de la valoración (igual que Manheim MMR). `[VERIFICADO]`
- **BCA Market Price:** base propietaria de **~5M ventas históricas de subasta UK**, modelada con **Microsoft Azure Machine Learning** + métodos estadísticos; variables: condición cosmética, condición mecánica, color, equipamiento; modelos en refinamiento continuo. `[VERIFICADO ≥2]`
- **Grading cosmético:** estándar 1–5 + Unclassified (alineado **NAMA**), por inspectores cualificados con **SVA a 2m / 45° / 90°**, sistema de puntos por tipo/severidad de daño. `[VERIFICADO]`
- **Informes mecánicos:** por **inspectores independientes** (Assured / Essential Check / 128), tests estáticos + (en 128) road test 10 mi. `[VERIFICADO]`
- **Salud de batería EV:** test independiente vía **OBD** powered by **AVILOO (FLASH Test)** → Grade A–E + SoH%. `[VERIFICADO]`
- **Reporte de mercado:** agregación mensual de los precios medios de venta de su propia subasta (cars + LCV), con MoM%/YoY%. `[VERIFICADO]`
- **NO usa** (a diferencia de cap hpi): metodología académica publicada, ni provenance propio (HPI/MOT/finance/write-off), ni índice macro tipo MUVVI. `[VERIFICADO por ausencia]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Subasta física** | ~50 centros en 10 países (UK + Europa incl. España: Azuqueca, Bellvei, La Luisiana); mayor sitio: Blackbushe | [VERIFICADO] |
| **Marketplace digital (web)** | **BCA Live Online** (subasta en vivo online con audio/vídeo) · **xBid** (puja online, España/Europa) · **Bid Now** (timed, fixed-end) · **Buy Now** (precio fijo instantáneo) · **EuroShop** (24/7, Europa) | [VERIFICADO] |
| **App móvil** | **BCA Buyer** (iOS/Android, UK): búsqueda, filtros, proxy bid, live sale audio/vídeo, grades, reports, EV battery health | [VERIFICADO ≥2: app stores] |
| **Herramientas de dealer** | **BCA Dealer Pro** (iOS/Android/UWP/desktop, online+offline) · **BCA Consumer Pro** (API white-label en web del dealer) | [VERIFICADO] |
| **Integración DMS** | DealerWeb, enquiryMAX, Pinewood + integraciones a medida; Consumer Pro vía API | [VERIFICADO] |
| **Informes (PDF)** | Appraisal report (Dealer Pro), 128 report descargable, AVILOO FLASH report, condition grade PDF (Europa) | [VERIFICADO] |
| **Reporte de mercado** | Notas de prensa mensuales (avg value, MoM%, YoY%, cars+LCV) a prensa de automoción | [VERIFICADO] |
| **Gating** | Stock vivo y fichas de vehículo **detrás de login de trade buyer** (auth.bca.co.uk); cuenta MyBCA con niveles | [VERIFICADO] |
| **Sin API pública self-serve de valoración** | Consumer Pro es B2B (request a demo); no hay sandbox público | [VERIFICADO por ausencia] |

---

## 6. Precio

| Concepto | Precio | Estado |
|---|---|---|
| **BCA EV Battery Health Grading** | **£24 + VAT / vehículo** | [VERIFICADO] |
| **BCA Essential Check** | **£12.50 ex VAT / vehículo** | [VERIFICADO] |
| **BCA Assured / 128 Inspection** | Tarifa según **nivel de cuenta MyBCA** (más compras = mejor descuento); excl. VAT | [VERIFICADO] |
| **BCA Dealer Pro** | **Suscripción** "menos que el coste de un café al día"; precio flexible | [VERIFICADO / CLAIM-VENDOR] |
| **BCA Consumer Pro** | Sin set-up fees adicionales; quote-based (request a demo) | [VERIFICADO] |
| **Buyer fees** | Fee de compra por vehículo según valor + nivel de cuenta MyBCA; importes exactos no públicos | [PARCIAL] |
| **BCA Partner Finance** | Financiación de stock 120 días (fees + interés); cotización B2B | [VERIFICADO modelo] |

> **Modelo:** **transaccional** (buy/sell fees por vehículo subastado, núcleo del negocio) + **servicios de valor añadido por uso** (grading mecánico, EV battery, inspección, prep, logística, finance) + **suscripción** de herramientas de dealer (Dealer Pro). El dato/valoración **no se vende como feed suelto**; viene embebido en el marketplace y en las herramientas. `[VERIFICADO]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca BCA **cada dato**. El hub es la **ficha de vehículo (VDP) en Vehicle Search / Live Online**, replicada en la **search result card** y en la **app BCA Buyer**.

**A. Search result card (tarjeta de resultado de búsqueda).** Muestra identidad básica (**Make/Model/Derivative, Year, Mileage, Colour, Fuel, Body**), **guide price**, **Condition Grade (1–5)** y — en EVs — el **EV Battery Health Grade (A–E)**, que va **"in the same place as the Condition Grading: on the vehicle search card"** (cita literal de BCA). Filtros laterales: vehicle type, model group, colour, mileage, **CAP Clean price**, age, grade, fuel type, sale channel.

**B. Vehicle Details Page (VDP).** Al hacer clic en la card: **Condition Grade** + **EV Battery Health Grade** **"at the top of the vehicle details page"** (cita literal); acceso al **Condition Grading report** (kipper diagram + defectos + imágenes), al **BCA Assured / Essential Check** report (resumen mecánico OK/Issue por categoría + notas), al **128 report** (PDF, vehículos de alto valor) y al **AVILOO FLASH report** completo (EVs). Galería de **imágenes full-screen con pan/zoom**.

**C. Live Online / xBid (pantalla de subasta en vivo).** Mismos datos de la card/VDP + **puja en vivo con audio/vídeo**; **concealed proxy bid** colocable por adelantado; el EV Battery Health Grade también aparece **"within Live Bidding"** (cita literal).

**D. App BCA Buyer (móvil).** Búsqueda free-text (mezcla sale location + registration + equipment, p.ej. *climate control*, *towbar*) + filtros; tracking/notas personales; reports (Assured, EV battery) accesibles desde la ficha.

**E. Herramienta de tasación del dealer (Dealer Pro).** Flujo: lookup → guided appraisal (beauty + damage images, kipper diagram, service history, mechanical condition, non-standard equipment) → **real-time valuation (Market Price)** → signature → appraisal report (PDF/email) → group stock management → disposal a subasta / funding request.

**F. Web del dealer (Consumer Pro).** Widget/API white-label: el cliente introduce su coche → **valoración instantánea (hammer-based)** con la marca del dealer → cae en Dealer Pro.

**G. Capa de mercado (fuera de la ficha).** **Market Report mensual** (avg value + MoM% + YoY%, cars + LCV) publicado vía prensa de automoción, no en la ficha.

> **Lección para cardeep:** BCA confirma el patrón **"grade + valor + salud de batería en lo alto de la ficha y replicado en la search card"**, con los **reports (cosmético / mecánico / batería) como capas desplegables** desde la ficha. Es el mismo blueprint que Manheim (VDP como hub) adaptado a Europa/España.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Mayor remarketer de Europa con presencia ESPAÑOLA viva.** Caso raro entre los auditados: **opera en España** (centros físicos + xBid + subastas Alphabet de renting + BEV diarias) → dato wholesale real de mercado español, no solo UK.
2. **Dato transaccional first-party (hammer price)** sobre **>1M veh/año** + base de **~5M ventas históricas** → valoración Market Price difícil de replicar sin el flujo de subasta propio (ventaja estructural tipo Manheim MMR).
3. **Marketplace + valoración + servicios físicos bajo un mismo techo** (proceso 360°: source→inspect→grade→value→list→sell→finance→transport→docs).
4. **Capa de condición por vehículo muy granular:** grading cosmético 1–5 **+** informe mecánico de 45+ puntos (Assured/Essential) **+** 128 puntos para alto valor **+** salud de batería EV A–E/SoH% (AVILOO) — todo accesible en la ficha.
5. **EV Battery Health Grading (AVILOO, A–E + SoH%)** integrado en la search card / VDP / live bidding — paridad con el EV Battery Health de Manheim, raro en Europa.
6. **Herramientas de tasación de dealer maduras** (Dealer Pro offline + Consumer Pro API white-label) que cierran el bucle part-exchange → subasta con el mismo motor de precio.
7. **Partner Finance** (floor-plan propio, £1bn/año) — financia la compra en su propia subasta, fidelizando al comprador.
8. **Escala operativa física** (mayor flota transporter de UK, Supreme Wheels 500k ruedas/año, bodyshops) que un proveedor de solo-dato no posee.
9. **Multi-tipo:** coches, LCV/vans, motos, caravanas/autocaravanas, EV, non-runners.

---

## 9. Gaps (lo que NO ofrece)

1. **No es una "guía de valor" ni un feed de dato vendible.** A diferencia de cap hpi (Black Book, data files, API REST/SOAP) o Manheim (MMR/MUVVI), BCA **no vende valoración/índice como producto de dato suelto**: Market Price viene embebido en sus herramientas; no hay tarifa de feed ni API pública de valoración self-serve. `[VERIFICADO por ausencia]`
2. **Sin índice macro de mercado** tipo MUVVI (1997=100) ni forecast de residual a años vista (Gold Book / ALG): solo **reporte mensual de precio medio + MoM/YoY**. **Sin curva de depreciación / future values multi-anual.** `[VERIFICADO por ausencia]`
3. **Provenance / historial NO propio.** No ofrece HPI Check / MOT / outstanding finance / write-off / mileage register como producto (eso es cap hpi, que **no** es del mismo grupo). El "Essential Check" es **mecánico**, no de historial — nombre engañoso. `[VERIFICADO]`
4. **Sin specs/new vehicle data (NVD)** tipo cap hpi/JATO (CO2/WLTP/dimensiones/equipment por derivative): BCA describe el coche concreto en subasta, no mantiene una base técnica de catálogo. `[VERIFICADO por ausencia]`
5. **Dato gated tras login de trade buyer.** Las fichas de vehículo y los precios no son públicos; se necesita cuenta profesional MyBCA. `[VERIFICADO]`
6. **Valoración atada al volumen de subasta UK.** Market Price se entrena sobre ventas de subasta UK (~5M); modelos/tipos con poco volumen o el mercado español (sin equivalente publicado) quedan peor cubiertos por la herramienta. `[RECONSTRUIDO]`
7. **Pan-europeo fragmentado.** Cada país tiene su marketplace local (bca.com/es_ES, /de_DE, etc.); **no hay un valor/índice paneuropeo homogéneo expuesto** ni un Market Price europeo público (el dato de valoración fuerte es UK). `[VERIFICADO por ausencia]`
8. **No es huella digital de punto de venta retail.** BCA cataloga **vehículos en subasta wholesale**, no los **puntos de venta / dealers y su presencia online** (territorio propio de cardeep). Consume/genera transacción, no indexa el mapa de vendedores. `[VERIFICADO]`
9. **Importes exactos de buyer/seller fees no públicos** (escalados por valor + nivel MyBCA). `[NO-VERIFICADO]`
10. **Sin telemática / uso real / VIN-decode universal** expuesto. `[VERIFICADO por ausencia]`

---

## 10. Fuentes (URLs)

**Oficiales — producto (leídas vía navegador real; bca.co.uk/bca.com bloquean fetchers con 403):**
- Servicios (catálogo): https://www.bca.co.uk/services
- BCA Dealer Pro: https://www.bca.co.uk/services/dealer-pro
- BCA Consumer Pro: https://www.bca.co.uk/services/dealer-pro/consumer-pro
- Vehicle Condition Grading (hub): https://www.bca.co.uk/buy/vehicle-condition-grading · Car: https://www.bca.co.uk/buy/vehicle-condition-grading/car-condition-grading
- **BCA Assured (45+ puntos, lista íntegra):** https://www.bca.co.uk/services/assured
- **BCA Essential Check (45+ áreas, lista íntegra):** https://www.bca.co.uk/services/essential-check
- **BCA 128 Vehicle Inspection:** https://www.bca.co.uk/services/128-vehicle-inspection
- **EV Battery Health Grading (A–E, SoH%, AVILOO, £24):** https://www.bca.co.uk/buy/ev-battery-grading
- Partner Finance: https://www.bca.co.uk/services/partner-finance · Logistics: https://www.bca.co.uk/services/logistics
- About us (servicios 360°, Automotive, Supreme Wheels, Imaging): https://www.bca.co.uk/about-us/
- Buyer app: https://www.bca.co.uk/buy/buyer-app · Proxy bidding: https://www.bca.co.uk/buy/proxy-bidding
- **Grupo Europa / cobertura 10 países:** https://www.bca.com/
- **BCA España (Azuqueca/Bellvei/La Luisiana, xBid, Alphabet, BEV+AVILOO):** https://www.bca.com/es_ES
- Europa — Condition Grade (1–5 + SMART/bodyshop/structural): https://www.bca.com/en/pt/m/Getting-Started/c/Professional-buyer/Appraisal-and-Mechanical-Report/Condition-Grade/

**App stores (campos BCA Buyer):**
- Google Play BCA Buyer: https://play.google.com/store/apps/details?id=com.bca.buyerapp · App Store: https://apps.apple.com/gb/app/bca-buyer/id1332601797
- BCA Dealer Pro V2 (Google Play): https://play.google.com/store/apps/details?id=com.bca.DealerPro
- Business Car (features Buyer app, EV battery grading): https://www.businesscar.co.uk/news/bca-adds-new-features-to-buyer-app/

**Inteligencia de precio / metodología:**
- BCA invierte en Market Price / big data (5M ventas, Azure ML, cosmética/mecánica/color/equipment): https://www.am-online.com/news/supplier-news/2017/09/11/bca-ramps-up-investment-in-big-data · https://www.motortrader.com/motor-trader-news/automotive-news/bca-ramps-investment-big-data-11-09-2017
- BCA Dealer Pro appraisal training (kipper, signatures, mechanical): https://aftermarketonline.net/bca-relaunches-vehicle-appraisal-training-programme/

**Market Report mensual (avg value, MoM%, YoY%, cars/LCV):**
- Business Car (rising used car values): https://businesscar.co.uk/news/2024/february/rising-used-car-values-reported-by-bca
- Motor Finance (julio 2024 £7.800; oct 2025 £7.638; LCV sep-2025 £8.460): https://www.motorfinanceonline.com/news/bca-reports-strongest-used-car-values-in-a-year-as-sales-surge-in-july-2024/ · https://www.motorfinanceonline.com/news/bca-lcv-values-rise-september-2025/ · https://www.motorfinanceonline.com/news/october-uk-used-car-values/

**Identidad / propiedad / verificación cruzada:**
- Wikipedia Constellation Automotive Group (subsidiarias + timeline propiedad): https://en.wikipedia.org/wiki/Constellation_Automotive_Group
- Wikipedia BCA Marketplace / David Wickins: https://en.wikipedia.org/wiki/BCA_Marketplace · https://en.wikipedia.org/wiki/David_Wickins
- Car Dealer Magazine (Constellation/£1.2bn Haversham): https://cardealermagazine.co.uk/who-is-constellation-automotive-group-what-does-it-own-and-how-profitable-is-it/253460 · https://cardealermagazine.co.uk/british-car-auctions-bought-haversham-holdings-1-2billion/91194
- AIM Group (renombre Constellation): https://aimgroup.com/2020/11/22/bca-owner-renames-itself-constellation-automotive-group/
- CD&R (adquisición 2010): https://www.cdr.com/news/clayton-dubilier-rice-to-acquire-europes-no1-vehicle-remarketing-company
- Fleet News (owner compra Aston Barclay): https://www.fleetnews.co.uk/news/bca-owner-buys-aston-barclay-to-secure-long-term-future-of-business
- Partner Finance + Solifi (£1bn, 100k contratos): https://www.solifi.com/news/bca-partner-finance-extends-solifi-wholesale-finance-contract/
- Escala/turnover (growjo): https://growjo.com/company/BCA_Europe

### Notas de verificación
- **Listas atómicas de Assured / Essential Check / 128 / grading / EV battery / Dealer Pro / Consumer Pro:** **leídas íntegras directamente de las páginas oficiales de BCA vía navegador real (Playwright)**, no de resúmenes. **[VERIFICADO]**.
- **Bloqueo técnico:** bca.co.uk y bca.com devuelven **HTTP 403** a fetchers (WebFetch); se sorteó con navegador real (Playwright). El stock vivo / fichas requieren login de trade buyer (auth.bca.co.uk) → campos de listing **reconstruidos** de facetas públicas + app stores + prensa. **[VERIFICADO búsqueda+app / RECONSTRUIDO ficha]**.
- **Propiedad:** Constellation Automotive Group (TDR Capital); timeline 1946→ADT→consorcio 1995→Samuel Montagu 2006→CD&R 2010→Haversham/BCA Marketplace 2015→TDR 2019→Constellation 2020 — **Wikipedia + prensa**. **[VERIFICADO]**. **cap hpi NO pertenece a Constellation** (es de Solera, ver `cap-hpi.md`). Aston Barclay: adquisición reportada por prensa, no en Wikipedia → **[PARCIAL]**.
- **España:** centros Azuqueca/Bellvei/La Luisiana, xBid, Alphabet, BEV+AVILOO — **leído en bca.com/es_ES**. **[VERIFICADO]**.
- **Market Price (5M ventas, Azure ML, variables):** am-online + motortrader. **[VERIFICADO ≥2]**.
- **Cifras de escala (12k/semana, £4bn, >50% UK):** agregadores/WebSearch, 1 fuente → **[PARCIAL]**. >1M veh/año y "Europe's largest" → bca.com **[VERIFICADO]**.
- **exa MCP:** NO disponible en el entorno (ToolSearch "exa…" devolvió gbrain/claude-mem/WebSearch/WebFetch, no exa). Investigación con **WebSearch + WebFetch + Playwright (navegador real) + lectura directa**. **[NOTA DE MÉTODO]**.
