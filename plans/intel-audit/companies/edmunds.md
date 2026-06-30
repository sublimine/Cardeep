# Edmunds — Auditoría atómica

> Slug: `edmunds` · Subdominio cardeep: **portal-insights** · Región: **EE. UU. (solo)**
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó.
> Naturaleza: **portal de consumo de investigación de coches** (reviews + ratings + precios + marketplace)
> con motor de **valoración** (TMV / Edmunds Suggested Price), inteligencia de mercado editorial y
> soluciones de marketing/lead-gen para dealers. Hoy **filial 100% de CarMax**.
> Web auditada: `https://www.edmunds.com/appraisal/` + docs `developer.edmunds.com` + Help Center.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre legal | **Edmunds.com, Inc.** | footer edmunds.com; Wikipedia |
| Fundación | **1966** por **Ludwig Arons** como *Edmunds Publications* (folletos impresos de specs) | Wikipedia |
| Propiedad histórica | **1988** comprada por **Peter Steinlauf**; familia Steinlauf mayoritaria hasta CarMax | Wikipedia |
| Salto digital | gopher **1994**; lanzamiento **edmunds.com 1995** (de los primeros sitios comerciales/auto); nombre legal *Edmunds.com, Inc.* **jun-1999** | Wikipedia |
| HQ | **Santa Monica, California** (Colorado Center desde 2016) + oficina satélite **Detroit, Michigan** | Wikipedia; CBInsights |
| Owner / grupo | **CarMax, Inc.** (NYSE: KMX) — **filial 100%** | footer edmunds.com; SEC 8-K CarMax |
| Cronología CarMax | **ene-2020** participación minoritaria **$50M** → **abr/jun-2021** adquisición del resto, **enterprise value ~$404M**; filial total desde **jun-2021** | investors.carmax.com; Wikipedia; VirginiaBusiness |
| CEO | **Avi Steinlauf** | Wikipedia |
| Adquisición propia | **CarCode** (startup de SMS), **oct-2014** (ganadora del reto interno *Hackomotive*) | prnewswire; Wikipedia |
| Reconocimientos | Webby 1997; Fast Company "Top 10 Most Innovative" 2015; Fortune "Best SMB" #26 (2016) | Wikipedia |
| Canales | edmunds.com · apps **iOS + Android** · **AI Assistant** (nuevo) · YouTube/Instagram(@edmundscars)/TikTok(@edmunds)/LinkedIn/Facebook/X · GitHub org `github.com/edmunds` | snapshot edmunds.com; apis.yml |

**Categorías de producto:** (1) **Portal de consumo** (expert reviews, Edmunds Rating, consumer reviews,
specs, fotos); (2) **Valoración/pricing** (TMV / Edmunds Suggested Price, appraisal, price checker / deal
rating); (3) **Marketplace de inventario** (New/Used Cars for Sale + Build & Price); (4) **Coste de
propiedad** (True Cost to Own); (5) **Herramientas financieras** (calculadoras, incentivos, lease deals);
(6) **Sell/Trade** (Instant Offer redimible en CarMax + venta privada vía Caramel); (7) **Soluciones de
dealer** (listings, CarCode, Ad Solutions, Dealer Reviews, Premier); (8) **Industry Insights** (analítica
de mercado, forecasts); (9) **Data API** (Vehicle/Editorial/Dealer/Media) — *programa abierto retirado*.

**Cliente objetivo:** **Consumidores** (compradores y vendedores) · **Dealers** franquiciados e
independientes (nuevo+usado) · **OEMs / anunciantes de automoción** · **Socios estratégicos / service
providers** (único acceso a la API desde 2018) · **Prensa/medios** (industry insights). Matriz: **CarMax**.

---

## 2. Cobertura

- **Geografía: EE. UU. exclusivamente.** Sin Europa, sin global, sin LATAM. La API cubre **solo vehículos
  vendidos en EE. UU.** y el dataset **se remonta a model year 1990 y no más atrás**. (Fuente: developer.edmunds.com overview.)
- **Nuevo y usado** + **CPO** (Certified Pre-Owned). Fuerte foco **EV**.
- **Tipos de vehículo:** turismos, **SUV, trucks/pickups, vans/minivans**. El selector de marcas de consumo
  lista ~**60+ marcas** (actuales + recientes, p.ej. Tesla, Rivian, Lucid, Polestar, VinFast, INEOS…) y
  marcas históricas (Saturn, Pontiac, Hummer, Scion, smart…). **NO** motos/powersports, **NO** boats/RV,
  **NO** comerciales pesados ("no comprehensive commercial vehicle data"). (Fuente: snapshot dropdown +
  developer overview.)
- *Nota de dato:* un ejemplo de tercero (Postman api-evangelist) muestra `makesCount: 682`, pero es un
  **valor de ejemplo no oficial** → `[NO-VERIFICADO]`.

---

## 3. Productos + campos atómicos

### 3.1 Edmunds Appraisal — "My Car Value" (valoración de usado, consumo)

**Entrada (3 métodos):** pestañas **Year/Make/Model**, **VIN**, **License Plate** (VIN/placa → "appraisal
más preciso que puede subir el valor"). Año **1990–2027**.
**Flujo de 6 pasos** (verificado en render): **(1) Location and Style** [ZIP + style/trim], (2) mileage,
(3) exterior color, (4) options/equipment, (5) **condition**, (6) **Appraisal Report Delivery** [email].
("How it works": VIN/placa → color + condición → valor por datos recientes de tu zona.)

**Tiers de condición (5)** — definiciones oficiales:
| Tier | Definición atómica |
|---|---|
| **Outstanding** | Excepcional mecánica/exterior/interior, sin desgaste visible, sin reacondicionar; pintura con brillo; compartimento motor limpio; neumáticos casi nuevos; título limpio; pasa emisiones. (<pocos vehículos) |
| **Clean** | Desgaste normal, sin problemas mayores; reacondicionado limitado. |
| **Average** | Algunos problemas mecánicos/cosméticos; reacondicionado considerable; pintura apagada, arañazos/golpes, interior algo gastado, neumáticos con banda usable. |
| **Rough** | Varios problemas que requieren reparaciones significativas; quizá cambiar neumáticos; título limpio. |
| **Damaged** | Daño mecánico/carrocería mayor; posible estado no seguro. |
("La mayoría" de vehículos caen en *Clean* o *Average*.)

**Valores de salida (usado)** — presentados como **matriz por style/trim** con columnas:
- **Trade-In Value** (lo que da un dealer)
- **Private Party Value** (venta entre particulares; > trade-in)
- **Dealer Retail Value** (lo que pagaría un comprador en dealer)
- **Certified Pre-Owned (CPO) price** (al pie de resultados)
- Titular: **rango de valor** (p.ej. "2009 Honda Accord Value — $1,456–$7,701").
- Marca: **Edmunds True Market Value (TMV)** = **Edmunds Suggested Price**.

### 3.2 True Market Value (TMV) / Edmunds Suggested Price — motor de pricing (nuevo + usado)

Definición oficial: *estimación del **precio medio de transacción** ("lo que otros pagan") para vehículos
nuevos o usados en tu zona*. **No** es precio "out-the-door": **excluye** rebates manufacturer-to-consumer
(dealer cash), sales tax, DMV fees y **doc fees**.

**Tipos de valor:**
| Valor | Ámbito | Definición |
|---|---|---|
| **Edmunds Suggested Price** (ex-**TMV New**) | nuevo | Lo que Edmunds recomienda pagar (sin tasas/impuestos); avg transaction price; **se muestra encima del MSRP**. |
| **MSRP** | nuevo | Precio sugerido fabricante. |
| **Invoice / Dealer Invoice** | nuevo | Precio fabricante→dealer. |
| **Dealer Retail (Used TMV Retail)** | usado | Media de lo que paga un comprador en dealer. |
| **Private Party** | usado | Precio de venta entre particulares. |
| **Trade-In** | usado | Lo que recibe el vendedor de un dealer. |
| **Certified (CPO)** | usado | Precio de mercado certificado. |
| **TMV dealer-installed options** | nuevo/usado | TMV propio para opciones instaladas por el dealer. |

**Factores/ajustes:** options, **color**, mileage, condition, **region (ZIP)** (precio **national** si no
hay ZIP), incentives, supply & demand, recent nearby transactions.

**Campos del objeto `price` (API Style v3, verbatim):** `baseMSRP`, `baseInvoice`, `usedTmvRetail`,
`usedPrivateParty`, `usedTradeIn`, `estimateTmv`, `tmvRecommendedRating`, `deliveryCharges`.
**Endpoints TMV (5):** New by StyleID+ZIP · New by VIN+MSRP · Used by StyleID · Typically Equipped Used · Certified.

### 3.3 Price Checker / Deal Rating (en cada listing)

Sección de "price details" en **cada listing nuevo y usado**: si el precio ≤ TMV, etiqueta **Great / Good /
Fair** (o "high price") **+ cifra de cuánto por encima/debajo de mercado**, comparado con otros listings del
mismo year/model/trim. **Price Checker** para nuevos (introduces una cotización y devuelve rating
fair/good/great) y embebido en cada VDP.

### 3.4 True Cost to Own (TCO®) — coste de propiedad a 5 años

**8 componentes (verbatim):** **Depreciation** · **Interest on financing** (Financing) · **Taxes & Fees**
(sales tax, registration, gas-guzzler) · **Insurance** (prima media estatal) · **Fuel** (EPA + precio
combustible estatal; regular/premium/diésel) · **Maintenance** (mantenimiento programado del manual) ·
**Repairs** (reparaciones fuera de garantía) · **Federal Tax Credit** (vehículos de combustible alternativo).
Derivados: **Total Cash Price**, **True Cost to Own total**, desglose **año a año (year1..year5)**.
**Supuestos:** 15.000 mi/año, **10% entrada**, **60 meses**. **Solo 5 años** (>5 años no fiable).
**Estructura de página:** **TCO Summary** + **Five-Year Details** (tabla por año).
**Endpoints API:** TCO Total (New Car) · Total Cash Price (New Car) · Makes with TCO · Models with TCO · TCO Categories.

### 3.5 Expert Reviews + Edmunds Rating (scoring editorial)

- **Edmunds Rating: escala 0–10**, compuesto de **30+ scores**.
- **Categorías del scorecard:** **Driving/Performance · Comfort · Interior · Technology (Tech) · Storage/Utility
  · Fuel Economy (Economy) · Value (Good Value) · Wildcard**.
- **Sub-criterios** (metodología Top Rated): *Driving* (acceleration, braking, steering, handling, drivability)
  · *Comfort* (seat comfort, ride comfort, climate control, noise/vibration) · *Interior* (ease of use,
  getting in/out, driving position, roominess, visibility) · *Tech* (audio/nav, device integration, voice
  controls, driver aids) · *Storage* (cargo space, small-item storage, car seat, hauling/towing) · *Economy*
  (EPA + test propio) · *Good Value* (build quality, cost, warranty, ownership benefits) · *Wildcard* (subjetivo).
- **Testing:** **200–300+ vehículos/año**; **loop real de 115 millas** (city/freeway/canyon) + **test track**
  privado (instrumentado: acceleration, braking distance, fuel economy). Ratings relativos al segmento.
- **Componentes del review:** **Pros · Cons · What's new · "Edmunds says"** (veredicto) · trims · fotos/vídeo.

### 3.6 Consumer Ratings & Reviews (UGC)

Por vehículo/servicio: **Overall star rating (de 5)** · category ratings · **nº de reviews** · texto · fecha ·
**recommend %** · ordenación (Most Recent / Highest Rated / Lowest Rated) · **distribución 5★…1★** ·
**Customer Summary AI-generado**. (Ej. servicio appraisal: 4.5/5, 607 reviews; 5★70/4★18/3★5/2★2/1★5.)

### 3.7 Edmunds Top Rated Awards

**6 categorías:** Best Car · Best SUV · Best Truck + versiones **EV** de cada una · + **Best of the Best**.
Criterio = top de su clase por testing independiente Edmunds.

### 3.8 Inventory / Marketplace

**New Cars for Sale** · **Used Cars for Sale** (búsqueda por Make/Model, Type, Price, ZIP). VDP con: precio,
**Edmunds Suggested Price** (encima del MSRP), **deal rating** (price checker), mileage, **VIN**, dealer,
fotos, features, history. **Build & Price** (configurador) para nuevos.

### 3.9 Specs / datos de vehículo (Vehicle API)

Jerarquía: **Make → Model → Model/Year → Trim → Style** (IDs clave: **modelYearId**, **styleId**).
- **Style (v3):** `id, name, year, make, model, manufacturerCode, submodel(body, modelName, niceName), trim,
  numOfDoors, drivenWheels, engine, transmission, options, colors, price{…}, categories(market, EPAClass,
  vehicleSize, primaryBodyType, vehicleStyle, vehicleType), MPG(highway, city), squishVins`.
- **Engine:** `id, name, equipmentType, availability, compressionRatio, cylinder, size, displacement,
  configuration, fuelType, horsepower, torque, totalValves, manufacturerEngineCode, type, code, compressorType`.
- **Transmission:** `id, name, equipmentType, availability, automaticType, transmissionType, numberOfSpeeds`.
- **Colors:** `id, name, equipmentType(COLOR), manufactureOptionName, manufactureOptionCode, category,
  colorChips.primary{r,g,b,hex}, colorChips.secondary{r,g,b,hex}`. Categorías: Interior, Exterior, Roof,
  Interior Trim, Mechanical, Package, Additional Fees, Other.
- **Equipment (v3):** `equipmentType` ∈ {AUDIO_SYSTEM, COLOR, ENGINE, FEE, HOLDBACK, OPTION, TELEMATICS,
  TIRES, TRANSMISSION, UNKNOWN, WARRANTY, WHEELS}; `availability` ∈ {STANDARD, OPTIONAL, UNKNOWN}.
- **VIN Decoding (v2):** `/api/vehicle/v2/vins/{vin}` → make, model, year, style, trim, engine, transmission.
  **Squish VIN** = primeros 11 dígitos menos el 9º (check digit).
- **Service: Maintenance (v1):** `modelYearId, maintenanceActionId, frequencyId(1–9), intervalMileage,
  intervalMonth` (A-service, B-service, one-time, recurring, inspections I/II…).
- **Service: Recalls (v1)** · **Service: Safety (v2):** `/api/vehicle/v2/{make}/{model}/{year}/safety` y
  `/styles/{styleId}/safety` (campos de respuesta NHTSA/IIHS **`[NO-VERIFICADO]` exhaustivo** — docs SPA no rendean JSON).
- **Content: Ratings and Reviews (v2)** · **Media API: Photos (v2)** (stock photos).

### 3.10 Editorial API & Dealer API

- **Editorial:** Articles (v2), Expert Content (v3) — articles, **video reviews, vehicle pros, vehicle cons,
  safety reviews, performance reviews**.
- **Dealer:** **Details and Location (v5)** (location/identity, **franchises** `/dealership/{id}/franchises`),
  **Ratings and Reviews (v1)**. La **Dealership API** da inventario en tiempo real (search make/model, pricing,
  **schedule test drives**).

### 3.11 EV tools

**Edmunds EV Range Test** (real-world, propio): cargar a **100%**, ruta **60% city / 40% highway**, conducir
**hasta que queden 10 millas** según el ordenador del coche → **range real** + **consumption (kWh)** vs EPA.
**Leaderboard** de range; **EV tax credits/rebates/incentives finder**; **coste de cargador doméstico**
(estimado ~$1,616, 240V); **EV Hub**; listas "Longest-Range".

### 3.12 Calculadoras financieras

**Auto Loan** · **Lease** · **Lease vs Buy** · **Affordability** · **True Cost to Own**. Tabs que **arrastran
las cifras** de una calculadora a la siguiente. (Loan: vehicle→purchase price+sales tax+fees+rate, term por
defecto 36–60 meses.)

### 3.13 Incentivos & Lease Deals

**Best Car Deals & Incentives** (por make/model/type) · **Best Lease Deals** (incl. por **estado**, p.ej.
New York, y por umbral <$299/<$199) · cash rebates · low-APR financing · lease specials.

### 3.14 Sell / Trade — Instant Offer + Caramel

- **Instant Offer (online offer):** precio **firme** (no estimación), **válido 7 días**, redimible en
  **cualquier CarMax** / dealer participante. Inputs: placa/VIN → style/options → condición. **Elegibilidad:
  vehículo 2018 o anterior, valor < $30.000, CarMax a <100 millas del ZIP.**
- **Venta privada vía Caramel®:** escrow (retiene dinero hasta entrega de coche+título), **buyers ID-verified**,
  pago **50% al subir el título correcto + 50% al confirmar el hand-off**, **transferencia digital de título y
  registro** (compliant por estado).

### 3.15 Soluciones de Dealer

| Producto | Qué es |
|---|---|
| **Vehicle Listings Service** | Inventario nuevo+usado en marketplace Edmunds + sitios partner. |
| **CarCode** | Plataforma cloud de mensajería: **SMS + web chat + Facebook Messenger** unificados; botón "Text Us"; conversión **10–15%** (>5× email). |
| **Edmunds Ad Solutions** | Publicidad/display. |
| **Dealer Reviews** | Generación de reseñas/confianza. |
| **Premier Program** ("Core Products") | Listings + leads + **targeted advertising** + **audience data** a lo largo del journey; expone inventario en Edmunds + partners. |
| **Edmunds Instant Cash Offer (dealer)** | ICO para dealers. |

### 3.16 Industry Insights / datos de analista (data center)

Métricas publicadas (mensual/trimestral): **Average Transaction Price (ATP)** nuevo y usado (por edad: usado
1-año, **3-años**) · **monthly payment** (financiado) · **average loan amount** · **APR** · **down payment** ·
**loan term** · **% a 0% APR** · **% comprometido a $1.000+/mes** · **negative equity** · **SAAR / forecast de
ventas** (anual + mensual) · **quarterly used vehicle reports** · **days on lot** · **EV market share** ·
**lease penetration** · incentives como % de ATP.

---

## 4. Metodología / fuentes de datos

- **TMV / Edmunds Suggested Price:** "millones de data points" — **datos reales de transacción de dealers**
  (**CarMax es una de las fuentes** desde 2020/2021), supply, demand, incentives, options, color, mileage,
  condition, **región (ZIP)**, recent nearby transactions; ajuste regional por ZIP con fallback **national**.
- **Edmunds Rating:** testing **in-house instrumentado** (test track + loop 115 mi), **200–300+ vehículos/año**;
  ponderación ≈ performance 30% / subjetivo (comfort+tech) 40% / value+ownership 30% `[PARCIAL-VERIFICADO,
  fuente secundaria]`.
- **Specs:** datos OEM; **US-only**, **desde MY 1990**.
- **EV Range:** test real-world propietario (≠ ciclo EPA 55/45).
- **TCO:** modelos con supuestos fijos (15k mi/año, 10% down, 60 meses, EPA, manual del fabricante, garantía).
- **Industry Insights:** agregación de transacciones del network de dealers + CarMax.

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web consumo** | edmunds.com (reviews, ratings, pricing, appraisal, inventory, calculators, insights). |
| **Apps móviles** | iOS (App Store id393630966) + Android (`com.edmunds`). |
| **AI Assistant** | Asistente conversacional (nuevo) integrado en la nav. |
| **REST JSON API** | `api.edmunds.com` — **Vehicle / Editorial / Dealer / Media**; auth **`api_key` (query)**; formatos **JSON** (def.) / XML / JSONP; **SDKs JavaScript y Python**. ⚠ **Programa abierto RETIRADO: acceso deshabilitado efectivo 15-feb-2018**; hoy solo **strategic partners, service providers, dealers y anunciantes** (sin acceso académico). |
| **Plataforma de dealer** | Listings, CarCode, Ad Solutions, Dealer Reviews, Premier, ICO. |
| **Industry Insights** | Press releases + Insights Hub + Data Center. |
| **Syndication/embebido** | Widgets de pricing/ICO en sitios de dealers partner (p.ej. Elk Grove Honda). |
| **Caramel** | Integración para el flujo de venta privada (escrow + título digital). |

---

## 6. Precio

- **Consumo: gratis** (monetiza con **leads de dealer + publicidad**).
- **API:** **no público / partner-gated** desde 2018; históricamente niveles de acceso **Exploratory / Enhanced
  / Professional**. Importes **no divulgados**. `[NO-VERIFICADO]`
- **Soluciones de dealer:** suscripción/contrato publicitario (Premier, Listings, Ad Solutions); **CarCode**
  tuvo tier **gratuito** integrado en listings. Importes no públicos. `[NO-VERIFICADO]`
- **Instant Offer / appraisal:** **gratis** al consumidor.
- ⚠ **Aviso de fuente:** los tiers numéricos "Free 1.000/mes · Professional 100.000/mes · Enterprise" y los
  rate-limits (10/100/1000 rpm) del repo `api-evangelist/edmunds` son **SCAFFOLD de tercero (Kin Lane), no
  cifras oficiales de Edmunds** — el propio fichero lo declara ("scaffold defaults; replace with provider-
  published values"). **NO usar como precio oficial.** `[NO-VERIFICADO / no oficial]`

---

## 7. Placement (patrón web — clave para cardeep)

> Dónde sitúa Edmunds cada dato. Derivado del render real (appraisal + listings) y del Help Center.

**A. Appraisal (valor de usado).** Stepper de **6 pasos** ("Current Step 1: Location and Style" … "6:
Appraisal Report Delivery"). Entrada por **Year/Make/Model | VIN | License Plate**. Resultado = **matriz de
valores por style/trim** con columnas **Trade-In · Private Party · Dealer Retail** (+ **CPO** al pie) y
**titular de rango** ($low–$high). CTA destacado **"Get an Instant Cash Offer"** → `/sell-car/`. Bloques de
apoyo: "How it works" (3 iconos), "A quick guide to the car value tool" (definición TMV), FAQ, reviews del servicio.

**B. Ficha de coche nuevo (VDP/review).** **Edmunds Rating (/10)** como héroe + **scorecard** por categorías
(Driving/Comfort/Interior/Tech/Storage/Economy/Value). **Pros / Cons** · **"Edmunds says"**. Bloque de
precio: **Edmunds Suggested Price encima del MSRP** + Invoice. Trims, fotos/vídeo, **TCO**, consumer reviews,
incentives/lease. `[Placement de review por Help Center + páginas de ratings; render directo bloqueado por redirect de ad]`

**C. Listing (SRP/VDP nuevo y usado).** Precio + **deal badge Great/Good/Fair** + **$ por encima/debajo de
mercado** + **Price Checker** (comparado con mismos year/model/trim). Edmunds Suggested Price encima del MSRP.

**D. Página TCO.** Encabezado True Cost to Own + **TCO Summary** y **Five-Year Details** (tabla año-a-año:
Depreciation, Insurance, Financing, Taxes & Fees, Fuel, Maintenance, Repairs, [Federal Tax Credit]).

**E. Ratings & Reviews.** Overall ★ (de 5) + barras de **distribución 5★→1★** + **Customer Summary AI** +
reviews ordenables + paginación.

**F. EV.** **EV Range Test leaderboard** (range real vs EPA + consumption kWh), **tax-credit finder**.

**G. Calculadoras.** Página con **tabs** (Loan / Lease / Lease vs Buy / Affordability / TCO); las cifras se
**arrastran** entre tabs.

**H. Sell/Instant Offer.** placa/VIN → confirmar style/options → condición → **oferta firme 7 días** + redención
en **CarMax**; alternativa venta privada con **Caramel** (escrow, título digital).

**I. Industry Insights.** ATP / payment / APR / forecast en notas de prensa y Data Center (gráficas + cifras).

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad editorial independiente** (desde 1966): **Edmunds Rating (/10)** con **testing in-house
   instrumentado** (test track + 115-mi loop, 200–300+ coches/año) + **Top Rated Awards** — capa de confianza
   que un guía de valor puro no tiene.
2. **Propiedad de CarMax** → feed de **transacciones reales de usado** + **Instant Offer FIRME** redimible en
   cualquier CarMax (transaccional, no mero estimado).
3. **True Cost to Own (8 componentes a 5 años)** — de las herramientas de coste de propiedad más granulares de consumo.
4. **EV Range Test real-world propietario** (independiente del EPA) + EV tax-credit finder.
5. **Valoración nueva (Edmunds Suggested Price) y usada** + **deal rating (Great/Good/Fair) en cada listing**.
6. **Venta privada con Caramel** (escrow + transferencia digital de título) integrada.
7. **Suite gratuita de calculadoras** + agregación de **incentivos/lease deals** (incl. por estado).
8. **Foros/comunidad** de larga data + base de **specs desde 1990**.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo EE. UU.** — sin Europa/global/LATAM. ← **gran hueco para cardeep** (huella digital paneuropea).
2. **API abierta retirada (2018)** — sin feed de datos self-service; partner-gated; **precio opaco**.
3. **No motos/powersports, no boats/RV, no comerciales pesados**; specs **US-only** y **solo desde MY 1990**.
4. **No tiene producto propio de historial/provenance VIN** (sin accidentes/título/odómetro nativo) — depende
   de terceros. `[NO-VERIFICADO que lo subcontrate; ausente del catálogo]`
5. **No publica valores wholesale/subasta** como producto (no hay guía tipo Manheim/Black Book wholesale).
6. **Instant Offer muy acotado**: solo ≤2018, < $30.000, CarMax a <100 mi.
7. **Sin métricas de velocidad de mercado de consumo nombradas** (days-to-sell, market days supply,
   price-to-market index): solo "above/below market" en listing y "days on lot" en informes de industria.
8. **Sin guía de valores residuales de leasing** como producto (TCO tiene depreciation, no un residual ALG/KBB).
9. **No es potencia de identificación de specs** vs Chrome/DataOne (specs = capa de apoyo; API cerrada).
10. **Sin telemetría/odómetro en vivo** — mileage es input del usuario.

---

## 10. Fuentes

- Appraisal (render + condiciones): https://www.edmunds.com/appraisal/ · https://help.edmunds.com/hc/en-us/articles/206103047
- TMV pricing (qué es): https://help.edmunds.com/hc/en-us/articles/206102387 · https://www.edmunds.com/tmv.html
- Edmunds Suggested Price: https://help.edmunds.com/hc/en-us/articles/360024831253 · https://help.edmunds.com/hc/en-us/articles/12131482576407
- Dealer-installed options TMV: https://help.edmunds.com/hc/en-us/articles/206102987
- API overview (recursos/endpoints/IDs/1990/US-only): https://developer.edmunds.com/api-documentation/overview/
- Vehicle API: https://developer.edmunds.com/api-documentation/vehicle/
- TMV API: https://developer.edmunds.com/api-documentation/vehicle/price_tmv/v1/
- TCO API: https://developer.edmunds.com/api-documentation/vehicle/price_tco/v1/
- Style/Engine/Colors/Equipment specs: https://developer.edmunds.com/api-documentation/vehicle/spec_style/v3/ · /spec_engine_and_transmission/v2/ · /spec_colors_and_options/v3/ · /spec_equipment/v3/
- VIN decoding: https://developer.edmunds.com/api-documentation/vehicle/spec_vin_decoding/v2/
- Safety/Maintenance: https://developer.edmunds.com/api-documentation/vehicle/service_safety/v2/ · /service_maintenance/v1/
- API retirada (2018) / acceso: https://help.edmunds.com/hc/en-us/articles/206103257 · https://help.edmunds.com/hc/en-us/articles/4414038118679 · https://developer.edmunds.com/faq.html
- Cómo rate Edmunds (rating /10, 30+ scores): https://help.edmunds.com/hc/en-us/articles/206103147 · https://www.edmunds.com/new-car-ratings/
- Top Rated Awards (criterios): https://www.edmunds.com/top-rated/ · https://www.edmunds.com/car-news/more-about-edmunds-top-rated-awards-2026.html
- True Cost to Own (consumo, 8 componentes): https://www.edmunds.com/tco.html · https://www.edmunds.com/about/more-about-tco.html · https://help.edmunds.com/hc/en-us/articles/206102997
- Calculadoras: https://www.edmunds.com/calculators/
- EV Range Test / tax credits: https://www.edmunds.com/car-news/electric-car-range-and-consumption-epa-vs-edmunds.html · https://www.edmunds.com/electric-car/tax-credits-rebates-incentives/
- Incentivos / Lease deals: https://www.edmunds.com/car-incentives/ · https://www.edmunds.com/lease-deals/
- Sell / Instant Offer: https://www.edmunds.com/sell-car/ · https://www.edmunds.com/sell-car/start-with-an-online-offer-when-selling-or-trading-in-your-car.html
- Caramel (venta privada): https://www.edmunds.com/sell-car/private-party/ · https://www.drivecaramel.com/how-it-works
- Dealer solutions: https://www.edmunds.com/industry/new-car-dealers.html · https://www.edmunds.com/industry/used-car-dealers.html · https://help.edmunds.com/hc/en-us/articles/206103207
- CarCode / Premier: https://www.edmunds.com/about/press/car-shopping-site-edmundscom-acquires-mobile-startup-carcode... · https://www.edmunds.com/industry/press/edmunds-launches-premier-a-revamped-dealer-program...
- Industry Insights (ATP/payment/APR/forecast): https://www.edmunds.com/avg-transaction-price-atp/ · https://www.edmunds.com/insights/ · https://www.edmunds.com/industry/press/uncharted-territory-edmunds-forecasts-16-2-million-new-vehicle-sales-in-2025...
- Identidad / owner / CarMax: https://en.wikipedia.org/wiki/Edmunds_(company) · https://investors.carmax.com/news-and-events/news/news-details/2021/CarMax-to-Acquire-Remaining-Stake-in-Edmunds/
- Perfil API (endpoints/auth `api_key`, makesCount ejemplo, **planes scaffold no oficiales**): https://github.com/api-evangelist/edmunds

### Notas de verificación
- Owner/HQ/fundación/cronología CarMax: **doble fuente** (Wikipedia + CarMax IR/SEC). [VERIFICADO]
- Valores appraisal (Trade-In/Private Party/Dealer Retail) y flujo 6 pasos: **render real** + Help Center. [VERIFICADO]
- Campos API specs (Style/Engine/Transmission/Colors/Equipment): **docs oficiales developer.edmunds.com**. [VERIFICADO]
- Campos JSON de **Safety / Ratings&Reviews / Dealer details**: docs SPA no rendean el JSON vía fetch →
  endpoints verificados, **campos de respuesta `[NO-VERIFICADO]` exhaustivo**.
- **Pricing API y rate-limits numéricos**: no oficiales (scaffold de tercero). `[NO-VERIFICADO]`
- Ponderación del Edmunds Rating (30/40/30): fuente secundaria. `[PARCIAL-VERIFICADO]`
- `makesCount: 682`: ejemplo de tercero, no oficial. `[NO-VERIFICADO]`
