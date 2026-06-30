# Accu-Trade (AccuTrade) — Auditoría atómica

> Slug: `accu-trade` · Subdominio cardeep: **valuation** · Región: **Norteamérica** (EE. UU. núcleo + Canadá)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[NO-VERIFICADO]` / `[CLAIM-VENDOR]` donde no se confirmó de forma independiente.
> Naturaleza: **motor de tasación/valoración de vehículos usados a nivel VIN + oferta de compra garantizada (real cash value)** para concesionarios, con **escaneo diagnóstico OBD-II**, **scoring de riesgo de inventario** y, desde 2026, un **Inventory Management System (IMS)**.
> Es el brazo de **adquisición de vehículo (vehicle acquisition / instant cash offer)** de **Cars Commerce** (ex Cars.com). El dato de valor lo aporta **Galves Market Data** (mayorista desde 1957).
> Marcas/sitios: `accu-trade.com` (→ redirige a `carscommerce.inc/accutrade`), `docs.accu-trade.com` (API Perseus), `help.accu-trade.com`, `galves.com`, `cars.com/sell/instant-offer`.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **AccuTrade** (estilizado; histórico **Accu-Trade**) | accu-trade.com; carscommerce.inc |
| Owner / grupo | **Cars.com Inc.** (NYSE: **CARS**), que opera como **Cars Commerce Inc.** | cars.com PR; cbinsights; streetinsider `[VERIFICADO]` |
| Entidad adquirida | **The Accu-Trade Group** + **Galves Market Data** + **MADE Logistics** | prnewswire (anuncio); cars.com `[VERIFICADO]` |
| Fundación Accu-Trade | **2015**, por **Robert (Bob) Hollenshead** — mayorista norteamericano y emprendedor de software de automoción | cbinsights (2015); WebSearch (Hollenshead) `[VERIFICADO]` |
| Vendedor en la adquisición | **Robert Hollenshead** (fundador; dueño también de **R. Hollenshead Auto Sales**, alto volumen) | prnewswire; autoremarketing `[VERIFICADO]` |
| Anuncio de adquisición | **8-feb-2022** | investor.cars.com; cars.com PR `[VERIFICADO]` |
| Importe | **$65 M** pago inicial en efectivo **+ ~$63 M** earnout por objetivos financieros (≈**$128 M** total) | cbinsights ($65–128 M); streetinsider ($63 M headline) `[VERIFICADO]` |
| Inversor previo | **TrueCar adquirió una participación** en Accu-Trade (2019) | prnewswire (título) `[VERIFICADO]` |
| HQ (entidad Accu-Trade) | **310 N. Ocean Blvd, Delray Beach, Florida 33483, EE. UU.** | cbinsights `[PARCIAL — fuente única]` |
| HQ del grupo | **Cars Commerce / Cars.com: Chicago, IL** | conocimiento general del emisor `[PARCIAL]` |
| Origen de Galves | **Galves**, "the professional's choice since **1957**"; historia hasta los **años 1920** | galves.com; cars.com PR; caredge `[VERIFICADO]` |
| Galves contacto/ubicación | Nueva Jersey (tel. **201-393-0051**, sales@galves.com); portal `galves.accu-trade.com` | galves.com `[PARCIAL]` |
| Lanzamiento solución Cars.com | Pre-pedido en **NADA, 11-mar-2022** | cars.com PR `[VERIFICADO]` |
| Lanzamiento **IMS** | **NADA Show, 4–6 feb 2026, Las Vegas** (booth #3723W); nota 2-feb-2026 | prnewswire; investor.cars.com `[VERIFICADO]` |

**Categorías de producto:** (1) **Motor de tasación/valoración a nivel VIN** (real cash value / guaranteed offer); (2) **Instant Cash Offer al consumidor** (web del dealer + marketplace Cars.com); (3) **App móvil de tasación + VIN scanner + OBD-II** (Accu-Trade Appraiser 3); (4) **VIN-Dow** (extensión de navegador para booking en subastas online); (5) **API Perseus** (integración de valoración para partners/retail digital); (6) **AccuTrade IMS** (gestión de inventario con Inventory Intelligence Scoring); (7) **Galves Market Data** (el "libro" mayorista subyacente + API de VIN decode/valor).

**Cliente objetivo:** **concesionarios** (franquiciados e independientes), grupos multi-punto, **dealers con service drive** (adquisición en taller), **retail digital/partners** vía API/iframe, y **consumidores** (vendedor particular) a través de Cars.com y de la web del dealer. (Fuentes: carscommerce.inc/accutrade; cars.com PR.)

---

## 2. Cobertura

- **Geografía:** **Estados Unidos** (núcleo) **+ Canadá**.
  - EE. UU.: Galves = "thousands of analyzed transactions… throughout the **US**". `[VERIFICADO]`
  - **Canadá:** Accu-Trade "comes to Canada" (**jun-2016**), introducido por **R. Hollenshead Auto Sales** con partner **Selectbidder**; posteriormente **TRADER** (AutoTrader.ca) se asocia con Accu-Trade para valoración online. La app integra **CarProof** (VHR canadiense). `[VERIFICADO ×2: autoremarketing + integración CarProof]`
  - **Europa / resto del mundo:** **sin cobertura.** ← hueco mayor para cardeep. `[VERIFICADO por ausencia]`
- **Nuevo vs usado:** **enfoque en USADO** (tasación de trade-in / adquisición / mayorista). El "vehicle of interest" (VOI) sí captura interés en **new/cpo/used** como lead, pero **el valor que produce es de usado**. `[VERIFICADO]`
- **Tipos de vehículo:** automóviles de pasajeros y light-duty trucks; afirma cubrir **"98% de todos los vehículos"**, incluyendo **exóticos, EVs, vehículos con mal historial y alto kilometraje (100.000+ mi)**. Fortaleza declarada de Galves en **lujo y exóticos**. `[CLAIM-VENDOR; galves luxury VERIFICADO]`
- **Profundidad de catálogo:** valores actualizados **a diario** por cada VIN; decodificación de trim/opciones vía **Chrome** (`chrome_style_id`, `chrome_body_id`). `[VERIFICADO]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal |
|---|---|---|
| **Motor de valoración AccuTrade** | Tasación VIN-específica con condición y mercado en tiempo real | Real cash value / oferta garantizada + rango |
| **Instant Cash Offer (consumer)** | Oferta de compra al particular en web del dealer y en Cars.com | Oferta garantizada (válida 3 días hábiles) |
| **Accu-Trade Appraiser 3 (móvil)** | VIN scanner + foto + condición + OBD-II en campo | Valor + condition report + deducciones |
| **VIN-Dow (extensión)** | Bookea automáticamente cada VIN en subastas online (ACV, Manheim Simulcast) | Valor/bid guidance + ajuste a inventario/mercado local |
| **API Perseus** | Integración de valoración para partners/retail digital (iframe + REST) | Endpoints de vehículo, oferta, mercado, equity, media |
| **AccuTrade IMS** (2026) | Gestión de inventario adquisición→retail/wholesale | Inventory Intelligence Score + profit retail/wholesale |
| **Galves Market Data** | Guía mayorista subyacente + API VIN decode/valor | Trade-in Value + Market Ready Value |

### 3.1 Valores y métricas de SALIDA (la materia prima)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Real cash value / Guaranteed offer** (`price.offer`) | Oferta de compra exacta por el VIN, **garantizada** (Cars Commerce se compromete a recomprar al mismo valor). | docs API; carscommerce; cars.com PR `[VERIFICADO]` |
| **Rango de valor** (`price.range[]` / `range[lower,upper]`) | Banda baja–alta del valor cuando `pricing_type="ranged"`. | docs API `[VERIFICADO]` |
| **Estimación de punto único** (`value`, `pricing_type="gp"`) | Valor único (no rango) para estimación rápida. | docs API `[VERIFICADO]` |
| **Vigencia de la oferta** (`expirationDate`) | Caducidad de la oferta; en consumer = **3 días hábiles**, sujeta a verificación de inspección por el dealer. | docs API; cars.com `[VERIFICADO]` |
| **Galves Trade-in Value** | "actual cash value" del trade-in del consumidor (dealer-to-dealer), buena condición con reacondicionamiento menor. | galves.com; caredge `[VERIFICADO]` |
| **Galves Market Ready Value** | Valor superior para vehículo **excepcional/reacondicionado**, listo para retail/subasta, sin trabajo mecánico/cosmético. | galves.com `[VERIFICADO]` |
| **Gross profit retail (estimado)** | Beneficio bruto estimado si el VIN se vende **al detalle**. | carscommerce IMS (PRICE) `[VERIFICADO]` |
| **Gross profit wholesale (estimado)** | Beneficio bruto estimado si se **liquida en mayorista**. | carscommerce IMS `[VERIFICADO]` |
| **Daily adjusted VIN value** | Valor del VIN **re-ajustado a diario** según mercado. | carscommerce; galves `[VERIFICADO]` |
| **Daily depreciation rate** | Tasa de depreciación diaria del vehículo (rasgo del score). | prnewswire IMS `[VERIFICADO]` |
| **Projected days on market** | Días proyectados hasta la venta (rasgo del score). | prnewswire IMS `[VERIFICADO]` |
| **Reconditioning cost** | Coste estimado de reacondicionamiento (mecánico + cosmético), restado del valor. | carscommerce accuracy `[VERIFICADO]` |
| **OBD-II diagnostic deduction** | Deducción $ por fallos detectados en el escaneo; mapea códigos a coste de reparación. | carscommerce accuracy `[VERIFICADO]` |
| **VIN-level deductions (itemizadas)** | Lista de add/deducts por opción y por defecto/daño (sin "manual guessing"). | prnewswire IMS; docs (`vacs[]`) `[VERIFICADO]` |
| **Diminished value (VHR)** | Cálculo de **valor disminuido** por siniestros del historial (en la app móvil). | apps.apple `[PARCIAL]` |
| **Payoff / lien quote** (`offer/{id}/payoff`) | Importe de cancelación de préstamo/lease; lista de **lenders** (`equity/lenders`). | docs API `[VERIFICADO]` |

### 3.2 Scores / inteligencia (AccuTrade IMS — 2026)

| Campo | Definición atómica | Fuente |
|---|---|---|
| **Inventory Intelligence Score** | Score compuesto de **riesgo** del VIN basado en **oferta/demanda en tiempo real**, no en historial de ventas anticuado. "Evalúa por riesgo, no por edad." | prnewswire; carscommerce IMS `[VERIFICADO]` |
| **VIN-level risk score** | Estimación de riesgo que combina **historial, condición, kilometraje, accidentes, mantenimiento y datos de sensores** en un único número. | WebSearch IMS `[PARCIAL]` |
| **Vehicle pedigree** | Rasgo del score: "linaje"/calidad del vehículo concreto. | prnewswire IMS `[VERIFICADO]` |
| **Dealer fit** | Encaje del vehículo con **este** concesionario. | prnewswire IMS `[VERIFICADO]` |
| **Market fit** | Encaje con el **mercado local** (oferta/demanda). | prnewswire IMS `[VERIFICADO]` |
| **Projected days on market** | (ver 3.1) componente del score. | prnewswire IMS `[VERIFICADO]` |
| **Daily depreciation** | (ver 3.1) componente del score. | prnewswire IMS `[VERIFICADO]` |

### 3.3 Identidad y specs del vehículo (API Perseus — `vehicle`)

`gid` (id AccuTrade) · `source` / `vehicle_source` · `vehicle_source_id` · `vehicle_vin` (VIN 17) · `chrome_style_id` · `chrome_body_id` · `vehicle_year` · `vehicle_make` · `vehicle_model` · `vehicle_style` (trim) · `vehicle_mileage` (odómetro) · `vehicle_color` (+ `vehicle_color_hex`) · `vehicle_color_interior` · matrícula + estado (`plate`/`state` → VIN vía `common/vin_by_plate`) · `standard_equipment` · `specialized` (sin pricing AccuTrade). (Fuente: docs API `[VERIFICADO]`.)

**Opciones que mueven valor** — `vacs[]`: `ref_id`, `description`, `addded` = **"A" (add) / "D" (deduct)**, `selected` (booleano: incluida), `mutex[]` (excluyentes), `disabled`. (Fuente: docs API `[VERIFICADO]`.)

### 3.4 Condición / historial / daños (inputs que ajustan el valor — API Perseus `offer`)

**Condición base:** `approximate_condition` = **excellent / good / fair / poor**. Neumáticos: `front_tire_age`, `rear_tire_age` (excellent/good/poor). `key_fobs` (nº de llaves). `is_original_owner`.

**Título/historial:** `is_salvage_title` · `is_rebuilt_title` · `carfax_has_bad_vhr` (VHR negativo) · `was_stolen`. Integración VHR: **CarFax / AutoCheck / CarProof** (móvil).

**Accidentes/daños:** `has_accident` · `insurance_payout_amount` · `has_external_damage` (+ `external_damage_amount`) · `has_frame_damage` · `has_flood_damage` · `has_fire_damage` · `has_hail_damage` · `has_other_issues` (+ `other_issues_repair_cost`) · `has_odor` · `has_unnamed_issue`.

**Testigos de avería (dash/OBD):** `has_warning_lights` + por sistema: `4x4`, `ac`, `abs`, `airbag`, `battery`, `brake`, `engine`, `suspension_fault`, `srs`, `tpms`, `traction_control`.

**Averías mecánicas:** `has_mechanical_issues` + `engine`, `transmission`, `brakes`, `suspension`, `exhaust`, `ac`, `oil_leak`, `head_gasket`, `catalytic_converter`, `sunroof_moonroof`, `other` (+ `mechanical_other_note`).

**Modificaciones:** `has_modifications` + `aftermarket_kit`, `exhaust`, `catalytic_converter`, `performance`, `stereo`, `spoiler`, `suspension_lowered`, `suspension_lifted`, `sunroof_moonroof`, `wheel`; `has_aftermarket_tint`. (Fuente: docs API `[VERIFICADO]`.)

### 3.5 Lien / lease / equity (API Perseus)

`is_liened` · `liened_type` (loan/lease) · `owed_amount` (saldo del préstamo) · `lease_monthly_payment` · `lease_number_payments` (meses restantes) · `lease_amount_remaining` · `equity/lenders` (catálogo de prestamistas para payoff). (Fuente: docs API `[VERIFICADO]`.)

### 3.6 Mercado / regional (señales que entran al valor)

**Local market** (`offer/{id}/local_market`) = oferta/demanda retail local. **Real-time market data** = transacciones de subasta internas (~**1.000 vehículos/semana**, ver §4). **Regionalización** (Galves: valores regionalizados, no nacionales genéricos). Factores: **preferencia de color / demanda regional**, **tendencia de rendimiento del segmento**, **oferta/demanda retail local**. (Fuentes: docs API; carscommerce accuracy; galves `[VERIFICADO]`.)

### 3.7 Lead / consumidor / intención (API Perseus)

`consumer.first_name/last_name/email/phone/cell_phone/postal_code` · `best_time_to_contact` (0–3) · `preferred_contact_method` (email/phone/text) · `consent_tcpa` · `consent_ccpa`. **Timing:** `expect_transact_months` (0 ready now / 2 = 2-6 meses / 100 = just curious). **Vehículo de interés (VOI):** `new_vehicle_type` (new/cpo/used), `new_vehicle_year/make/model/style/vin/stock_number/odometer`. **Atribución:** `lead_source`, `origin_type`, `vdp`, `cid`, `aff_cid`, `pag_id`, `partner_offer_id`. (Fuente: docs API `[VERIFICADO]`.)

### 3.8 Reportes y contenido de salida

**Universal Condition Report** (deducciones/adiciones itemizadas, consumer-facing) · **descripción de vehículo / "seller notes" generadas por IA** (45 s vs 20 min manual) · **fotos** (`vehicle_photos[]`, `additional_images[]`, `vehicle_image`) + **photo overlays** de features/promos · **QR code** (tracking de campaña) · **recall info** + **common problems** + **transfer disclosure** (móvil) · **Profit Funnel report** · **Trade Capture report** · **acquisition/capture rate** + **gross profit tracking** (ROI). (Fuentes: carscommerce; prnewswire IMS; apps.apple `[VERIFICADO]`.)

---

## 4. Metodología / fuentes de datos

- **Dato de valor — Galves Market Data:** guía mayorista desde **1957**; valores movidos por **"miles de transacciones analizadas por un equipo de especialistas de remarketing por todo EE. UU."** (análisis humano, no solo fórmula); **actualización diaria**; **regionalizado**; incorpora **"equipamiento relevante y otros factores, descartando outliers"**, yendo más allá de color/km/condición. `[VERIFICADO]`
- **Dato de mercado en tiempo real:** transacciones de subasta **internas** (la red de Hollenshead/MADE Logistics): **~1.000 vehículos/semana**, rastreando **resultado de venta, patrones de comprador/vendedor, conducta de puja y asistencia**. Frente a competidores con **lookback de ~6 semanas**, AccuTrade afirma **actualización diaria**. `[CLAIM-VENDOR]`
- **VIN-specific + condición:** decodifica trim/opciones (Chrome) y aplica **add/deducts** por opción y por defecto/daño; ajusta por **color/región, segmento y oferta/demanda local**. `[VERIFICADO]`
- **OBD-II diagnostics:** escanea **109.000 trouble codes** (marketing) / **~11.000 códigos mapeados** a coste de reparación (página de accuracy); **~1 de cada 3 escaneos** halla problemas, con ahorro medio **$715**. `[VERIFICADO con matiz de cifra]`
- **Garantía:** **oferta garantizada al 100%** sobre el valor tasado; respaldo de **Cars Commerce** para **recompra al mismo valor** y opciones de liquidación sin riesgo. `[VERIFICADO]`
- **Precisión declarada:** **34% más preciso que KBB y Black Book**; **~4% de desviación estándar media** frente a precios finales de subasta; cobertura del **98%** de los VIN. `[CLAIM-VENDOR]`

(Fuentes: galves.com; carscommerce.inc/vehicle-appraisal-accuracy; cars.com PR; carscommerce IMS.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Web / plataforma dealer** | Portal AccuTrade (login en `carscommerce.inc`/`accu-trade.com`); tasación en showroom. |
| **App móvil** | **Accu-Trade Appraiser 3** (iOS 14+, ~314 MB; Android `com.rhcapl.hercules3`): VIN scanner, foto, condición, VHR (CarFax/AutoCheck/CarProof), recall, reporting. Requiere suscripción. |
| **Instant Cash Offer (consumer)** | En **web del dealer** (trade-in machine) y en **Cars.com/sell/instant-offer** (audiencia ~25 M shoppers/mes). |
| **VIN-Dow (extensión navegador)** | Bookea cada VIN al salir a la venta en subastas online (**ACV Auctions**, **Manheim Simulcast**); bid guidance + push al siguiente paso del workflow. |
| **API Perseus (REST + iFrame)** | Módulos: `algol, common, contentpiece, equity, geo, member, misc, offer, vehicle`. iFrame embebible (mensajería `atInbound`/`atOutbound`). Auth propia. **Lease Self-Inspection App** (autoinspección de leasing). |
| **DMS / ecosistema** | **100+ integraciones** DMS/IMS/CRM/web/service. Push de tasación a **CRM como lead**; entrada de inventario/citas/repair orders desde DMS (service-lane). |
| **Integraciones nombradas** | **Cars.com** (Instant Offer + demanda real-time), **Dealer Inspire** (web/retail/chat), **DealerClub** (subasta dealer-to-dealer / liquidación), **vAuto** (push de pricing/inventario), **Gubagoo**, **Darwin**, **Hunter** (captura de inspección en service lane). |
| **AccuTrade IMS** | Consola de inventario: módulos **APPRAISE · STOCK (Intelligence Scoring) · PRICE · MERCHANDISE** + **ROI reporting** (Profit Funnel, Trade Capture). |
| **Galves** | Guía/portal `galves.accu-trade.com` + **REST API** (VIN decode + valor) + integración en scanners de terceros (**Laser Appraiser**, **Carbly**). |

---

## 6. Precio (parcialmente descubierto)

| Producto | Precio | Fuente / nota |
|---|---|---|
| **AccuTrade (núcleo, histórico pre-Cars.com)** | **~$199–$249 / mes** | Foro **DealerRefresh** (dealers) `[COMMUNITY-REPORTED]` |
| **AccuTrade (post-adquisición Cars.com)** | **~$1.500 / mes** (reportado; subida que motivó fuga a Carbly/Stockwave) | DealerRefresh `[NO-VERIFICADO oficial]` |
| **Dealer Inspire Website Trade-In Tool** | **Setup $499 (one-time), actualmente bonificado**; mensual/anual requiere login | theshop.com `[PARCIAL]` |
| **API Perseus / Enterprise / IMS** | **No público** — venta por demo/contacto (888-853-9458 / 855-870-9786) | carscommerce `[NO-VERIFICADO]` |
| **Galves Market Data** | **No público** — sales@galves.com / 201-393-0051 | galves.com `[NO-VERIFICADO]` |
| **Instant Offer (consumidor)** | **Gratis** para el consumidor (monetiza vía leads/transacción del dealer) | cars.com `[VERIFICADO]` |

> **Tensión de modelo:** tras la compra por Cars.com, el precio saltó de ~$199–249/mes a ~$1.500/mes según la comunidad de dealers; AccuTrade se reposiciona como **suite integrada** (no herramienta suelta), lo que explica el salto pero generó fricción/competencia (Carbly, Stockwave). `[COMMUNITY-REPORTED]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca AccuTrade **cada dato**. Reconstruido de la API Perseus (iframe + endpoints), las páginas de producto, el IMS y el flujo consumer de Cars.com.

**A. Entrada de tasación (3 vías de selección de vehículo).** El input ofrece **(1) VIN** (escaneo con cámara en móvil), **(2) matrícula + estado** (→ convierte a VIN), o **(3) Year → Make → Model → Style** en cascada (`vehicle/years|makes|models|styles`). Tras seleccionar, se piden **mileage**, **colores** (ext/int) y **opciones** (`vacs[]`).

**B. Cuestionario de condición (stepper de preguntas).** Pantallas secuenciales por bloque: **título/historial** → **accidentes/daños** (con importes) → **testigos de avería** (lista de luces por sistema) → **averías mecánicas** → **modificaciones** → **neumáticos/llaves/owner**. Cada respuesta **ajusta el valor en vivo** (`priceAdjustment` se emite del iframe al padre). El **escaneo OBD-II** inyecta automáticamente fallos/coste de recon en este bloque, sin tecleo manual.

**C. Resultado / ficha de oferta.** Se muestra **junto al vehículo** (imagen, Year/Make/Model/Style/VIN/mileage) **el valor garantizado** (`price.offer`) o el **rango** (`price.range`), con **fecha de caducidad** y, en consumer, el aviso de validez **3 días hábiles** sujeta a inspección. Debajo, **deducciones/adiciones itemizadas** (Universal Condition Report) explican el número.

**D. Panel de mercado / decisión (dealer).** En IMS, por cada VIN: **gross profit retail vs wholesale**, **daily adjusted value**, **projected days on market**, **daily depreciation** y el **Inventory Intelligence Score** (riesgo) — pensado para decidir **retener (retail) o liquidar (wholesale/DealerClub)**.

**E. VIN-Dow (overlay en subasta).** Mientras el dealer navega **ACV/Manheim Simulcast**, una **ventana flotante** "bookea" cada vehículo y muestra **valor/bid guidance + encaje con inventario y mercado local**; botón para **empujar la compra** al workflow.

**F. Service lane / driveway (campo).** App móvil para tasar en **taller, showroom o el camino de entrada del cliente**: scan VIN → foto → condición → OBD-II → valor + condition report compartible.

**G. Consumer Instant Offer (web dealer + Cars.com).** Widget **embebido en la VDP / lead form** del dealer y en `cars.com/sell`: el particular entra **plate/VIN + detalles + condición**, recibe la **oferta garantizada** y se le **conecta con el dealer local**; el mismo dato **se auto-popula en todos los canales** (web, chat Gubagoo/Darwin, retail). Comparativa **vender al dealer vs particular**.

**H. Merchandising / sindicación.** Tras adquirir: **descripción IA + photo overlays** y **sindicación multi-marketplace** (Cars.com y otros) desde el mismo registro.

**I. Reporting (ROI).** Fuera de la ficha: **Profit Funnel** y **Trade Capture** (capture rate, trades perdidos, gross profit por equipo).

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Oferta de compra GARANTIZADA a nivel VIN** (real cash value) **respaldada por Cars Commerce** para **recompra al mismo valor** — no es una "estimación" como KBB/Black Book, es un precio en firme transaccional.
2. **Escaneo OBD-II integrado en la tasación**: convierte **fallos diagnósticos reales** en **deducción de recon automática** (escanea ~109k códigos; ~1/3 halla problemas; ~$715 ahorro/issue). Pocos valuadores cierran el bucle "diagnóstico → $ → valor".
3. **Cuestionario de condición ultra-granular** (luces por sistema, averías mecánicas por componente, modificaciones por tipo, daños con importe, título/robo) → ajuste línea a línea, no tiers vagos.
4. **Inventory Intelligence Score (riesgo, no edad)** con rasgos atómicos: **pedigree, dealer fit, market fit, projected days on market, daily depreciation** → decisión retail vs wholesale por VIN.
5. **Dato propio de subasta en tiempo real** (~1.000 vehículos/semana de la red Hollenshead/MADE) + **Galves** (mayorista desde 1957, regionalizado, análisis humano) → **actualización diaria** vs lookback de semanas.
6. **Ciclo completo de adquisición**: consumer instant offer → tasación dealer → **service-lane/driveway** → **VIN-Dow en subasta** → **IMS** → **DealerClub** (liquidación) — todo bajo un techo y con el **mismo número** sincronizado por API.
7. **Distribución de audiencia Cars.com** (~25 M shoppers/mes; ~la mitad busca trade/sale; 82% no visita KBB) como **canal de captación** que un valuador puro no tiene.
8. **API Perseus + iFrame** muy completa para **retail digital/partners** (selección VIN/plate/YMM, oferta multi-paso, equity/payoff, media, lease self-inspection).

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Norteamérica (EE. UU. + Canadá)**; **sin Europa ni global.** ← hueco mayor para cardeep. `[VERIFICADO por ausencia]`
2. **Orientado a USADO/trade-in**; **no es libro de valor residual/leasing forecast** ni índice macro a años vista (a diferencia de ALG/J.D. Power). `[VERIFICADO por ausencia]`
3. **Sin valor de préstamo/loan ni retail "de libro" estandarizado** para banca/seguros: Galves publica **dos valores mayoristas** (trade-in / market ready), no el set lending/insurance. `[PARCIAL]`
4. **No es marca de consumidor** tipo "Blue Book": el valor vive **dentro del dealer/Cars.com**, no como autoridad pública citada por el comprador. `[VERIFICADO]`
5. **Vehicle history NO propio** — depende de **CarFax / AutoCheck / CarProof** (terceros). `[VERIFICADO]`
6. **Pricing opaco** (núcleo/API/IMS por demo) y **percibido como caro** tras la compra por Cars.com (~$1.500/mes reportado). `[COMMUNITY-REPORTED]`
7. **Sin métricas públicas de "market speed" por listing** estilo vAuto/CarGurus (market days supply, price-to-market %) **expuestas como producto nombrado**; existen señales internas (days on market proyectado, oferta/demanda local) pero **no un panel público de índices**. `[PARCIAL]`
8. **Condición y daños = input del dealer/consumidor + OBD-II**, no telemetría continua del vehículo. `[VERIFICADO]`
9. **Dependencia de ecosistema Cars Commerce** (Cars.com, Dealer Inspire, DealerClub): máximo valor solo dentro de su stack; fuera, menos diferencial. `[VERIFICADO]`
10. **Sin curva de depreciación granular descargable** a nivel consumidor; la depreciación diaria vive en herramientas de pago (IMS). `[PARCIAL]`

---

## 10. Fuentes

**Oficiales / producto (Cars Commerce, accesibles):**
- AccuTrade (home, redirect de accu-trade.com): https://www.carscommerce.inc/accutrade/
- Vehicle appraisal accuracy (34%, 4% std dev, OBD, $715, 98%): https://www.carscommerce.inc/vehicle-appraisal-accuracy/
- Integrations (DMS, Dealer Inspire, DealerClub, vAuto, Gubagoo, Darwin, Hunter): https://www.carscommerce.inc/accutrade/integrations/
- AccuTrade IMS (APPRAISE/STOCK/PRICE/MERCHANDISE): https://www.carscommerce.inc/accutrade-inventory-management-system/
- Simplify & Scale Car Appraisals (service lane/driveway, 109k códigos): https://www.carscommerce.inc/simplify-scale-car-appraisals/
- **API Perseus (docs, campos atómicos):** https://docs.accu-trade.com/
- Help Center (Acquire/Analyze/Dispose/Configure): https://help.accu-trade.com/en/
- VIN-Dow (ACV, Manheim Simulcast): https://help.accu-trade.com/en/articles/5698741-vin-dow-extension
- App móvil: https://apps.apple.com/us/app/accu-trade-appraiser-3/id1385938741 · https://play.google.com/store/apps/details?id=com.rhcapl.hercules3
- Galves Market Data (1957, valores, diario): https://www.galves.com/ · https://www.galves.com/the-galves-difference/
- Instant Offer consumidor: https://www.cars.com/sell/instant-offer/

**Prensa / IR / terceros (verificación cruzada):**
- CARS adquiere Accu-Trade Group (8-feb-2022, Hollenshead, Galves, MADE): https://www.prnewswire.com/news-releases/cars-to-acquire-the-accu-trade-group-adds-digital-vehicle-acquisition-to-the-cars-platform-301477093.html
- CARS lanza soluciones (NADA 2022, metodología Galves, dispositivo portátil): https://www.cars.com/articles/cars-launches-vehicle-acquisition-and-valuation-solutions-powered-by-accu-trade-447827/ · https://www.prnewswire.com/news-releases/cars-launches-vehicle-acquisition-and-valuation-solutions-powered-by-accu-trade-301498814.html
- Importe $63M / $65M+earnout: https://www.streetinsider.com/Corporate+News/Cars.com+Inc.+(CARS)+Acquires+The+Accu-Trade+Group+for+$63M/19571907.html
- TrueCar adquiere participación (2019): https://www.prnewswire.com/news-releases/truecar-acquires-stake-in-accu-trade-300796197.html
- IMS launch (NADA feb-2026, Intelligence Score, pedigree/dealer fit/market fit/days on market/daily depreciation): https://www.prnewswire.com/news-releases/accutrade-launches-a-single-solution-for-smarter-appraisals-and-inventory-management-302675475.html · https://investor.cars.com/2026-02-02-AccuTrade-Launches-a-Single-Solution-for-Smarter-Appraisals-and-Inventory-Management (403 directo; vía PRNewswire)
- Company facts (HQ Delray Beach FL, fundada 2015, $65–128M): https://www.cbinsights.com/company/accu-trade
- Accu-Trade comes to Canada (2016, Selectbidder): https://www.autoremarketing.com/arcanada/accu-trade-comes-canada/
- Galves values (independiente): https://caredge.com/guides/what-are-galves-values (403 directo; resumen vía WebSearch)
- Pricing comunidad de dealers (~$199–249 → ~$1.500/mes): https://forum.dealerrefresh.com/threads/i-need-a-replacement-for-accutrade-any-suggestions.10063/
- Reseller (Dealer Inspire trade tool, $499 setup): https://theshop.com/products/accutrade

### Notas de verificación
- **Owner Cars.com/Cars Commerce, adquisición 2022, importe, Galves+MADE, Hollenshead:** doble/triple fuente. **[VERIFICADO]**
- **Campos atómicos de la API Perseus (vehicle/offer/condición/lien/consumer/pricing):** documentación oficial `docs.accu-trade.com`. **[VERIFICADO]**
- **Intelligence Score y sus rasgos (pedigree, dealer fit, market fit, days on market, daily depreciation):** PRNewswire IMS + carscommerce. **[VERIFICADO]**
- **Galves: dos valores mayoristas (trade-in / market ready), diario, regionalizado, desde 1957:** galves.com + caredge + cars.com. **[VERIFICADO]**
- **Canadá:** autoremarketing (2016, Selectbidder) + CarProof en la app + partnership TRADER (search). **[VERIFICADO]**
- **OBD-II 109.000 vs 11.000 códigos:** dos cifras de distinto significado (escaneados vs mapeados a coste). **[VERIFICADO con matiz]**
- **Estadísticas de precisión/beneficio (34%, 4%, $2.700, $715, 87%, 38,2%, 75%, 90%, 20%, 98%, 82%, 25M):** material de marketing del vendedor. **[CLAIM-VENDOR]**
- **HQ Delray Beach FL:** fuente única (CB Insights). **[PARCIAL]**
- **Pricing núcleo/API/IMS/Galves:** no divulgado oficialmente; cifras mensuales = comunidad de dealers. **[NO-VERIFICADO oficial / COMMUNITY-REPORTED]**
- **exa MCP:** no disponible en el entorno (ToolSearch no devolvió tool exa); investigación hecha con WebSearch + WebFetch. **[NOTA DE MÉTODO]**
- **Páginas con 403 (investor.cars.com IMS, caredge, usedcarnews):** contenido reconstruido vía PRNewswire/WebSearch.
