# IAA (Insurance Auto Auctions) — Auditoría atómica

> **slug:** `iaa` · **subdominio cardeep:** `wholesale-intelligence` · **web:** https://www.iaai.com/ · **siblings:** `ca.iaai.com` (Canadá), `seller.iaaiuk.co.uk` / `auctions.synetiq.co.uk` (UK), `csatoday.iaai.com` (portal vendedor), `help.iaai.com` (ayuda) · **owner:** RB Global, Inc. (NYSE: RBA)
> **Región:** Norteamérica (EE. UU. núcleo + Canadá) + Reino Unido. **Base compradora en 170+ países.** **NO opera en España / Europa continental.**
> **Fecha auditoría:** 2026-06-30 · **Método:** WebSearch + WebFetch en vivo de iaai.com (home, Vehicles, vehicle-information, iaa-360-view, vehiclevalue, vehiclescore, total-loss-predictor) + snippets de páginas con bot-wall (selling-services, Reports, fees, bidding) + verificación cruzada (SEC/EDGAR, RB Global IR, gov.uk CMA, Business Wire, Auto Remarketing, AutoBidMaster, A Better Bid, SalvageBid, RideSafely, In Practise). **exa MCP NO disponible** en el entorno (ToolSearch "exa…" devolvió gbrain/claude-mem/Gmail/Drive/WebFetch/WebSearch) → investigación con WebSearch+WebFetch intensivos.
> **Doctrina VAM:** cada afirmación con fuente. `[V]` = verificado (≥2 fuentes o render directo) · `[V1]` = una sola fuente fiable · `[CLAIM]` = marketing del vendedor sin verificación independiente · `[3P]` = dato de tercero (importador/agregador que espeja a IAA) · `[NV]` = no verificado. Nada inventado; cuando la observación contradice una afirmación, gana la observación.
>
> **Naturaleza (qué es):** **IAA es el marketplace de subasta de vehículos SINIESTRADOS / TOTAL-LOSS** (el segundo de Norteamérica, par de Copart). NO es una guía de valoración retail (KBB/Black Book) ni un VHR (Carfax). Su capa de **"inteligencia" / `wholesale-intelligence`** son **herramientas data-science de DECISIÓN DE SINIESTRO TOTAL y de PRECIO DE SALVAMENTO** montadas sobre su propio flujo transaccional: `IAA Vehicle Value®` (valor predicho del salvamento), `IAA Vehicle Score™` (daño 0-50 por visión computacional), `IAA Total Loss Predictor™` (clasificación de siniestro), `Loss Advisor™` (umbral de total-loss), `BidFast®` (oferta de compra a aseguradora), `Sales Decision Center™`, más el `IAA Industry Report` / `Data Points` (índices de mercado de salvamento). El dato primario es la **transacción real de subasta de salvamento** (precio de martillo) de su propia red.
> **Verdict express:** dato de subasta first-party de salvamento US/CA/UK; valoración = de **salvamento** (no retail), seller-provided **ACV** (no calcula retail propio); cero presencia EU continental. Para cardeep vale como **PATRÓN DE FICHA (VDP)** y de **placement de score/daño/ACV**, no como fuente de huella española.
>
> **Patrón a copiar por cardeep:**
> 1. La **ficha de vehículo (VDP) "300+ data points"** con bloques claros: **Condition** (Loss Type / Primary+Secondary Damage / Start Code / Title-Sale Document / Airbags / Keys / Odometer) · **Build Data** (Engine/Cylinders/Fuel/Transmission/Drive Line/Body/Colores/Country of Origin, vía ChromeData) · **Sale Info** (Branch / Lane-Run / Aisle-Stall / Sale date / Seller / Seller Type / **ACV** / Sale Status).
> 2. El **`Vehicle Score` 0-50** como **badge prominente en cada VDP** + **filtro de inventario** por condición — un único número de daño que ordena miles de lotes.
> 3. El **`360 View` + `Feature Tour`** (spin interior/exterior + tour de equipamiento) y los **`Premium Imagery Sets` (hasta 75 fotos, undercarriage→tire tread)** como estándar de merchandising de imagen.
> 4. El **`Cost Calculator` embebido en cada VDP** (fee + transporte por zip) → coste total estimado antes de pujar.
> 5. Las **clasificaciones semáforo** (`Probable Repair` / `Borderline` / `Probable Total Loss`) como patrón de etiqueta de decisión.
> 6. El **`Sale Status`** (`Pure Sale` / `Minimum Bid` / `On Approval` / `If Bid`) como estado de venta de la ficha.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca pública | **IAA** (logo "IAA"), antes **Insurance Auto Auctions** | [V — home/footer] |
| Nombre legal | **IAA Holdings, LLC** / **IAA, Inc.** (operativa US: *Insurance Auto Auctions, Inc.*) | [V — RB Global IR + SEC] |
| Owner / grupo | **RB Global, Inc.** (NYSE: RBA · TSX: RBA), antes **Ritchie Bros. Auctioneers** | [V ×2 — PRNewswire + autoremarketing] |
| Fundación IAA | **1982** ("leading live and live-online salvage vehicle auction company") | [V ×2 — SEC 10-K + growjo] |
| HQ | **Westchester, Illinois** (área Chicago); tras la fusión, también HQ oficial de RB Global combinada | [V ×2 — RB Global + SEC] |
| Ritchie Bros. | Fundada **1958**; sigue incorporada en Canadá (oficinas Burnaby, BC) | [V — WebSearch] |
| Escala personal | **~4.500 empleados** | [V1 — RB Global overview] |
| Facilities | **~190–210+** instalaciones en **EE. UU., Canadá y Reino Unido** (cifra varía por fuente/fecha) | [V — múltiples; rango declarado] |
| Volumen | **2,5 M+ vehículos/año** (plataforma multicanal) | [V1 — IAA marketing] |
| Base compradora | **170+ países** | [V ×2 — RB Global IAA + marketing] |
| Vendedores (sellers) | **aseguradoras (núcleo), concesionarios, flotas/leasing/rent-a-car, organizaciones benéficas (donaciones)** | [V ×2] |
| Ticker propio (histórico) | **NYSE: IAA** (independiente jun-2019 → mar-2023; deslistada al cierre de la compra) | [V — SEC + autoremarketing] |
| Apps móviles | **"IAA Buyer Salvage Auctions"** (iOS/Android) · **"CSAToday by IAA"** (iOS/Android) | [V — App Store/Play] |

### Lineaje corporativo (anti-confusión) [V salvo marca]

| Hito | Año | Fuente / estado |
|---|---|---|
| **IAA fundada** (Insurance Auto Auctions) | **1982** | SEC/growjo [V] |
| **IAA** pasa a ser filial de **KAR Auction Services** (salvage de KAR vía *Insurance Auto Auctions Inc* US + *Impact Auto Auctions Ltd* CA + *HBC Vehicle Services Ltd* UK) | — | SEC 10-K [V] |
| **Impact Auto Auctions** entra en la familia IAA (Canadá) | **2007** | Business Wire [V] |
| KAR adquiere **HBC Vehicle Services** (UK) | **2015** (rebrand → IAA en **2019**) | autorecyclingworld [V] |
| **Spin-off de KAR** → IAA empresa pública independiente (**NYSE: IAA**); KAR sigue como "KAR" | **2019** | SEC Form 10-12B/A + 8-K [V] |
| IAA adquiere **SYNETIQ Ltd** (UK; salvage + desguace/dismantling) | **oct-2021**, **£225 M** (£186 M al cierre + £39 M contingente; **CMA** lo despeja sin condiciones **mar-2022**) | gov.uk CMA + autorecyclingworld [V ×2] |
| **Impact Auto Auctions (Canadá) → rebrand a IAA** (14 instalaciones CA) | **24-feb-2022** | Business Wire + iaai.com [V ×2] |
| IAA adquiere **DDI Technology** (Decision Dynamics LLC) = **electronic lien & title (ELT)**, integrada con **4.400+ entidades financieras** + DMVs de **26 estados** | (pre-2023) | dditechnology.com [V1] |
| **Ritchie Bros. completa la compra de IAA** → renombre a **RB Global** | **20-mar-2023** | PRNewswire + RB Global IR [V ×2] |
| **SYNETIQ (operaciones de subasta UK) → rebrand a IAA** | **2025** | ATF Professional + bodyshopmag [V ×2] |

**Categorías de negocio:** (1) **Marketplace de subasta de salvamento/total-loss** (live + digital `AuctionNow`); (2) **Total Loss Solutions** — suite B2B para aseguradoras (Inspection Services, Title Services, Loan Payoff, Total Loss Predictor, Loss Advisor); (3) **Inteligencia de valor/condición** (Vehicle Value, Vehicle Score, BidFast, Sales Decision Center); (4) **Gestión de inventario/reporting vendedor** (CSAToday, Active Inventory Management, Mobile Assignment); (5) **Servicios al comprador** (Interact/AuctionNow, Buy Now, Transport, Cost Calculator, financiación); (6) **Publicaciones de mercado** (Industry Report, Data Points, Insights); (7) **Remarketing whole-car** (dealer/flota/donación). [V]

**Cliente objetivo:** dos lados. **Sellers:** aseguradoras (P&C auto), flotas, leasing, rent-a-car, dealers, ONG/donación, gobierno. **Buyers:** desguazadores/recicladores, talleres/rebuilders, dealers de usado, exportadores (170+ países), público (donde la licencia lo permite). [V]

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| **Geografía operativa** | **EE. UU.** (núcleo, `iaai.com`) · **Canadá** (`ca.iaai.com`, ex-Impact Auto Auctions, **14 sites**, incl. contratos como **ICBC** en BC) · **Reino Unido** (`seller.iaaiuk.co.uk` / `auctions.synetiq.co.uk`, ex-HBC + ex-SYNETIQ) | [V ×2] |
| **Alcance compradores** | **170+ países** (subasta digital + exportación) | [V] |
| **España / EU continental** | **AUSENTE.** IAA no opera subastas ni publica datos en España ni en Europa continental. (Para cardeep: NO es fuente de huella española; solo patrón de UI.) | [V por ausencia] |
| **Nuevo vs usado** | **USADO / siniestrado exclusivamente.** No valora coche nuevo ni publica MSRP/curva de depreciación retail. | [V] |
| **Scope de vehículo** | **Total-loss, dañado, low-value** núcleo; también **clean-title reparable**, **whole-car** (remarketing dealer/flota), **donaciones**, **especialidad**. | [V] |
| **Tipos (Vehicles)** | **Cars · SUVs · Pickup Trucks · Electric Vehicles · Motorcycles** (competition/cruiser/racer/roadster/touring) · **ATVs** · **Heavy Trucks** (Freightliner/Peterbilt/Kenworth/Mack/International) · **Buses** · **RVs** (motorhomes, boats, jet skis/wave runners, snowmobiles, travel trailers) · **Trailers** (container chassis, dolly, dump, flatbed, grain) · **Rental Vehicles** | [V — iaai.com/Vehicles] |
| **Categorías de subasta** | **Live Auctions · Timed Auctions · Buy Now · Public Auctions · Gov Auctions · Dream Rides** (colección/lujo) · **Rec Rides** (recreativo/powersports) · **Electric Vehicle Auctions · Specialty · Virtual Lane** | [V — home nav] |
| **Frescura del dato** | Subastas **diarias** por localización; inventario en tiempo real (run list live + Time Extended); Vehicle Score/Value calculados **en el check-in**. | [V] |
| **Naturaleza del dato (clave)** | **Transacción REAL de subasta de salvamento first-party** (precio de martillo) de su red US/CA/UK. Volumen ~2,5 M/año. | [V] |
| **Conversión de venta** | **53,8%** (avg daily sales conversion, dic-2024) | [V1 — Industry Report] |

---

## 3. Productos + campos atómicos

> **Fuente de verdad del schema** = página `vehicle-information` + snippet de **personalización del listado** de iaai.com (lista de columnas/campos del VDP) + páginas de producto `vehiclescore` / `vehiclevalue` / `total-loss-predictor` (render directo) + glosario IAA (boacon/ridesafely/salvagebid espejando a IAA). IAA declara **"300+ data points"** por vehículo `[CLAIM]`.

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **Marketplace / AuctionNow (VDP)** | Ficha de lote de subasta de salvamento | Datos del vehículo + condición + sale info + imágenes + estado de puja | ~40 |
| **IAA Vehicle Score™** | Score de daño por visión computacional | Nº 0–50 + banda de severidad | ~7 |
| **IAA Vehicle Value®** | Valor de salvamento predicho (ML) | Rango de valor predicho | ~9 |
| **IAA Total Loss Predictor™** | Clasificador de siniestro total | 3 clases (Repair/Borderline/Total) | ~7 |
| **Loss Advisor™** | Umbral de total-loss (puntos ponderados) | Decisión total-loss sí/no | ~4 |
| **BidFast®** | Oferta de compra a aseguradora | Importe de oferta (válido 30 días) | ~4 |
| **IAA Sales Decision Center™** | Datos a nivel de stock para el vendedor | Tablero de decisión (reserva/rerun) | ~5 |
| **360 View / Premium Imagery** | Merchandising de imagen | Spin 360 + tour + 75 fotos + engine starts | ~8 |
| **CSAToday®** | Portal de gestión/reporting vendedor | Dashboard + inventario + ofertas + market value | ~10 |
| **IAA Inspection Services®** | Inspección/tasación remota | Image set + estimación + virtual adjuster | ~6 |
| **IAA Title Services™** | Procura/gestión de títulos | Title Procurement Dashboard + Title Tracker | ~6 |
| **IAA Loan Payoff™** | Portal liquidación de lien/lease | Carta de garantía + ACH funding | ~6 |
| **IAA Transport™ / Cost Calculator™** | Entrega + coste total | Quote door-to-door + desglose de fees | ~7 |
| **Industry Report / Data Points** | Índices de mercado de salvamento | ASP/ACV/Gross Return/negative equity… | ~10 |

### 3.1 Marketplace / AuctionNow — ficha de vehículo (VDP) [V]

**Campos atómicos del VDP / listado** (etiquetas verbatim de la personalización de columnas de iaai.com):

| Bloque | Campos atómicos (verbatim) |
|---|---|
| **Identidad** | `VIN` · `Stock #` (+ `Public` badge) · `Year` · `Make` · `Model` · `Series` (trim) · `Vehicle Type` · `Vehicle SubType` · `Body Style` · `Country of Origin` |
| **Condition** | `Loss Type` · `Primary Damage` · `Secondary Damage` · `Start Code` (Run & Drive / Starts / Stationary) · `Title / Sale Document` · `Airbags` · `Key` · `Odometer` |
| **Build Data** (vía **ChromeData**) | `Engine` · `Cylinders` · `Fuel Type` · `Transmission` · `Drive Line Type` · `Exterior Color` · `Interior Color` (+ specs/equipamiento decodificados por VIN) |
| **Sale Info** | `Branch` (+ `Offsite` badge) · `Lane/Run` · `Aisle/Stall` · `Sale Info` (fecha/hora de venta) · `New Inventory Time` · `Market` · `Region` · `Seller` · `Seller Type` · **`ACV`** (Actual Cash Value) · `Sale Status` |
| **Imágenes** | `IAA 360 View` · `Feature Tour` · `IAA High Resolution Images` · `IAA Key Images` · `Premium Imagery Sets` (≤75) · `IAA Engine Starts` (vídeo 10 s) · imágenes de undercarriage |
| **Inteligencia (subscriber)** | `IAA Vehicle Score` (0–50, badge) |
| **Coste** | `IAA Cost Calculator` (fee + transporte, tras login) |

**Diccionario de campos clave (verbatim glosario IAA / espejo):**
- **`ACV` (Actual Cash Value)** = *"the estimated retail value of a vehicle if it were in an undamaged condition"*, **aportado por el SELLER** según KBB/Black Book/tasación independiente. [V] **Nota: IAA usa ACV; NO publica un "Est. Retail Value" calculado propio** (diferencia con Copart).
- **`Start Code`** — `Run & Drive`: *"motor started (with or without a jump) and idled, both forward and reverse gears engaged, and the steering wheel made one full rotation in each direction"*; `Starts`: *"motor started… and idled when it reached the yard"*; `Stationary`: *"will not start, has engine damage, or was not tested"*. [V]
- **`Primary Damage` / `Secondary Damage`** — daño principal y de contexto (ver §3.1b).
- **`Loss Type`** — causa del siniestro (ver §3.1b).
- **`Title / Sale Document`** — marca de título / documento de venta (ver §3.1b).

**Sale Status (estado de venta) [3P — espejo AutoBidMaster/A Better Bid + IAA Auction Rules]:**
- `Pure Sale` — sin reserva; el mejor postor gana, sin aprobación del vendedor.
- `Minimum Bid` / `On Minimum Bid` — el vendedor fijó un mínimo; tiene hasta **7:45 pm PST del día hábil siguiente** para aceptar / contraofertar / rechazar.
- `On Approval` — sin mínimo durante la puja; el vendedor puede aceptar/rechazar/contraofertar hasta **6 pm PST, 2 días hábiles** tras la venta.
- `If Bid` / `Sale Pending` — negociación pendiente.
- Todos los lotes son **"with reserve"** (sujeto a aprobación del consignador). [3P/V1]

**Mecánica de puja (AuctionNow):** `Pre-Bid` (proxy, hasta **1 h antes**; el pre-bid más alto se representa por proxy) · `Proxy Bid` · `Live bid` (subastas diarias por localización, run list en tiempo real, multi-watch) · `Buy Now` (precio fijo, factura instantánea) · **`Time Extended`** (reinicia el contador con alta actividad). [V]

#### 3.1b Taxonomías de Loss Type / Damage / Title

**`Loss Type` (verbatim, espejo SalvageBid):** `Collision` · `Fire` (subtipos: interior burn / exterior burn / total burn / **engine burn**) · `Theft` (recovered theft) · `Water/Flood` · `Repossession` · `Lease/Rental` · **`Remarketing`** (alta milla + daño leve) · `Other`. [3P]
**`Primary/Secondary Damage` (espejo RideSafely/auto4export):** `Front End` · `Rear End` · `Side` · `All Over` · `Top/Roof` · `Undercarriage` · `Mechanical` · `Engine Burn` · `Burn` · `Water/Flood` · `Hail` · `Vandalism` · `Rollover` · `Stripped` · `Frame Damage` · `Biohazard/Chemical` · `Minor Dents/Scratches` · `Normal Wear` · `Non-Repairable`. [3P — lista representativa, no exhaustiva oficial; marcado]
**`Title / Sale Document` (marcas):** `Clean/Clear Title` · `Salvage Title` · `Rebuilt/Reconstructed` · `Junk` · `Certificate of Destruction / Non-Repairable` · `Flood` · `Lemon` (+ variantes estatales US). [3P/V]

### 3.2 IAA Vehicle Score™ (daño 0–50 por visión computacional) [V — render vehiclescore]

> Subscripción dentro de `IAA Interact®`, exclusiva de compradores registrados de pago. **Mostrado prominentemente en CADA VDP** + usado como **filtro de inventario** por condición.

| Campo / parámetro | Valor | Estado |
|---|---|---|
| **Escala** | **0–50** | [V] |
| Banda `0–9` | **Non-Repairable** ("damage spans across panels with likely missing parts") | [V] |
| Banda `10–19` | **Severe Damage** (multiple panels, minimal reusable parts) | [V] |
| Banda `20–29` | **Major Damage** (likely multiple panels, may remain intact) | [V] |
| Banda `30–39` | **Moderate Damage** (most panels intact and aligned) | [V] |
| Banda `40–49` | **Minor Damage** (dents, scratches, light wear) | [V] |
| Banda `50` | **Little damage** (minor scratches, normal wear) | [V] |
| **Input** | **"a vehicle's four corner images"** (capturadas en check-in; reshoot si no pasan el umbral de calidad) | [V] |
| **Modelo** | **"over 2 million images annotated with location and damage severity"**; AI + Deep Learning; grade por esquina **combinado y ajustado con "unseen attributes"** | [V] |
| **Dimensiones evaluadas** | panels condition · drivability · airbag deployment status · interior/mechanical damage likelihood | [V] |

### 3.3 IAA Vehicle Value® (valor de salvamento predicho — ML) [V — render vehiclevalue]

> Output = **rango de valor predicho** (no punto único). Generado en el **check-in**. Ayuda al seller a fijar reservas y negociar pujas bajo reserva. Convive con Vehicle Score y Sales Decision Center.

**Inputs atómicos (verbatim):** `Historical Data` (ventas previas) · `Vehicle Attributes` (specs/equipamiento) · `Vehicle Information` (type, **airbags**, **odometer**, **engine type**, specs) · `Geography` (mercados regionales comparables) · `Damage Type` (collision/fire/theft/water/otro) · `Primary/Secondary Damage` (localización/clasificación) · `Market Activity` (**bidder counts** + **número de auction runs**) · **`IAA Vehicle Score™ Data`** ("computer vision-enabled damage matrix"). [V]
**Salida:** rango de valor → reserva, negociación bajo reserva, decisión de **rerun**. [V]

### 3.4 IAA Total Loss Predictor™ (clasificador de siniestro total) [V — render]

> Vive dentro del **IAA Inspection Services® Portal**; ayuda a ajustadores/peritos a **evitar inspecciones innecesarias**.

**3 clasificaciones (verbatim):** `Probable Repair` (identificación rápida; posibles constructive total losses) · `Borderline` (comparar coste reparación/claim vs retorno de salvamento, con **IAA Vehicle Value®**) · `Probable Total Loss` (checkpoint antes de cancelación; evita tows de retorno innecesarios). [V]
**Inputs atómicos:** `IAA Vehicle Value®` · `IAA Vehicle Score®` · `Damage description` · `Loss type` · `Run & Drive status` · `Airbag deployment` · `Vehicle age`. [V]

### 3.5 Loss Advisor™ (umbral de total-loss — puntos ponderados) [V1 — IAA Insights]

Determina si un vehículo es total-loss vía **sistema de puntos ponderado**. Inputs: `reported damage` · `Actual Cash Value (ACV)` · `salvage value`. **Customizable al umbral de total-loss específico de cada aseguradora.** Salida = decisión total-loss. [V1]

### 3.6 BidFast® (oferta de compra a aseguradora) [V1]

Da a la aseguradora una forma rápida de saber si un vehículo es **reparable o total-loss** mediante **análisis comprensivo orientado a mercado**; con base en él, la aseguradora puede dar al asegurado una **oferta de compra documentada**. **Usa el histórico de subasta de IAA** para formar un bid **válido 30 días**. [V1]

### 3.7 IAA Sales Decision Center™ (datos a nivel de stock) [V1]

Empodera al seller con **datos a nivel de stock** para decisiones data-driven: ventas **bajo reserva**, **negociaciones**, decisión de **rerun**. Maximiza retornos. [V1]

### 3.8 Imagen / merchandising (360 View · Premium Imagery · Engine Starts) [V]

| Componente | Detalle | Estado |
|---|---|---|
| **IAA 360 View™** | Spin 360° interior + exterior con **zoom** en cada aspecto; *"salvage auction industry's first 360° walk-around"*. Partner: **SpinCar®** (luego **Impel**). Pilot: **+$300–$600/veh** de precio de venta vs control. | [V ×2] |
| **Feature Tour** | Añadido al 360 View; identifica **value-added features y opciones** del vehículo | [V] |
| **Premium Imagery Sets** | **Hasta 75 fotos** en vehículos selectos, "undercarriage to tire tread" | [V] |
| **Undercarriage images** | Vistas del **bajo completo** (expansión de Inspection Services) | [V] |
| **IAA High Resolution Images / IAA Key Images** | Galería HD + imágenes clave | [V1] |
| **IAA Engine Starts** | **Vídeo de 10 s** del motor en marcha | [V1] |
| **CSAToday standard images** | **10 imágenes estándar** vía CSAToday (incl. undercarriage) | [V1] |

### 3.9 CSAToday® (portal de gestión/reporting del vendedor) [V — search]

> *"Anywhere, anytime"* (web + móvil iOS/Android). **Dashboard** = overview de **salvage performance**, **timeline efficiencies**, **net returns**, **total loss files** e inventario.

**Herramientas/campos atómicos:** `Active Inventory Management` · `Vehicles and Inventory` · `Assignments Received` · `Returns` · `Summary Reports` · `Manage Offers` · `Market Value` · `Accelerated Search`. **Mobile:** escanear `VIN`, **asignar vehículos** en segundos, **valoraciones de mercado en tiempo real**. [V]

### 3.10 IAA Inspection Services® (inspección/tasación remota) [V — search]

Proceso tech-based de **inspección y tasación remota** (desk reviews + estimates con **image set** comprensivo) para total-loss. Beneficios declarados: `días reducidos para asignación` · `coste de storage reducido` · `coste de rental reducido` · `ahorro de adjuster independiente` · `menos fleet vehicles` · **virtual adjuster 24/7**. Métricas marketing: reduce storage **hasta 10 días**, **+30% eficiencia**. [V/CLAIM]

### 3.11 IAA Title Services™ (procura/gestión de títulos) [V — search]

- **IAA Title Procurement Dashboard** (web) — gestión administrativa de titulación; overview de total-loss files + inventario.
- **IAA Title Management & Title Tracker** — seguimiento.
- Expertos en **leyes de título estatales** (transient losses, commercial losses, **aged pending files**).
- **Mobile notaries**: la aseguradora asigna documentos de título electrónicamente a notarios que se desplazan al propietario y ejecutan en persona.
- Backbone: **DDI Technology (ELT)** — 4.400+ entidades financieras + DMVs de 26 estados. [V/V1]

### 3.12 IAA Loan Payoff™ (liquidación de lien/lease) [V ×2]

> Lanzado **2019** (industry-exclusive). Punto único de entrada para todo total-loss **con lien o lease**; portal digital seguro que automatiza la comunicación carrier↔lender.

| Métrica / capacidad | Valor | Estado |
|---|---|---|
| Carta de garantía (letter of guarantee) | **auto-generada en ~1 día** (media de industria 10+ días) | [V] |
| Cobertura de lenders | **~100%** (negocio con casi todo lender US) | [V] |
| Integración digital directa | **~80% de los auto lenders US**, incl. **16 de los top 20** | [V] |
| Funding | **ACH** para positive y negative equity liens | [V] |
| Ahorro de tiempo | **~20 días** (negative equity) / **~10 días** (positive equity) | [V] |
| Ahorro por claim | **~$450/claim** (sobre todo en rental) | [V] |
| Lease functionality | añadida **jul-2021** | [V1] |
| Volumen | **$3.000 M+** en transacciones total-loss en **2022** | [V ×2] |

### 3.13 IAA Transport™ + Cost Calculator™ (entrega + coste total al comprador) [V]

- **IAA Transport™:** door-to-door **doméstico + internacional**, **quote en tiempo real**, status updates, pago + transporte en un paso, financiable; pickup/entrega **hasta 14 días hábiles**; tel. (855) 694-7502 / +1 (708) 572-0586; variante **IAA Transport Global** (envío internacional). [V]
- **IAA Cost Calculator™:** en **cada VDP tras login**; estima **coste total** = fees + **transporte por código postal**. (Disclaimer: estimación, no oferta.) [V]

### 3.14 Industry Report / Data Points (índices de mercado de salvamento) [V — search]

> Publicación **trimestral** (2023, 2024 Q3/Q4, 2025 Q2/Q3, etc.) en `iaai.com/Insights` y `/Reports`. Analiza economía US + industria auto + EV + salvamento.

**Métricas/series atómicas:** `Average Selling Price (ASP)` · `Actual Cash Value (ACV)` · **`Gross Return % on ACV`** · `Sales conversion rate` (diaria) · `Negative equity transactions` (Δ YoY) · `Depreciation %` · `Miles driven` (→ frecuencia de accidente/volumen) · `Steel / crushed-car (scrap) prices` · `EV share / trends` · `Foreign buyer demand`. Macro: GDP, inflación, labor, gas prices. [V]
**Valores muestra:** Q4-2024 ASP **−2% YoY**, Gross Return % on ACV **+2,6% QoQ**; negative equity **+12,2% (2022→23)** y **+8,6% (2023→24)**; Q3-2025 ASP en máximos, **+2,5% YoY** con ACV **−0,3%**. [V1]

---

## 4. Metodología / fuentes de datos

- **Dato primario = transacción REAL de subasta de salvamento first-party** (precio de martillo) de la red IAA US/CA/UK (~2,5 M veh/año). Sobre ese flujo se entrenan Vehicle Value (ML), BidFast (histórico), Industry Report/Data Points. [V]
- **`ACV` = aportado por el SELLER** (aseguradora) usando KBB/Black Book/tasación independiente — **IAA no calcula un valor retail propio**; lo refleja como dato de entrada. [V]
- **`Vehicle Score` = visión computacional/Deep Learning** sobre **4 imágenes de esquina** del check-in, modelo entrenado con **2 M+ imágenes anotadas** (localización + severidad). [V]
- **`Vehicle Value` = ML / data mining** sobre histórico de ventas + atributos + geografía + daño + market activity + Vehicle Score; output rango. [V]
- **`Total Loss Predictor` = data science** que combina Vehicle Value + Vehicle Score + damage description + loss type + Run&Drive + airbag + age. [V]
- **`Loss Advisor` = puntos ponderados** (damage + ACV + salvage value) vs umbral del carrier. [V1]
- **ChromeData** = decodificación de specs/equipamiento por VIN en el bloque Build Data. [V1]
- **Patentes USPTO** de "total loss / loss detection by image analysis" (12223549, 12469083, 12475513, 11574366, 12045893) respaldan la familia de modelos de imagen→siniestro. [V — USPTO]
- **NMVTIS:** como yarda de salvamento/aseguradora, IAA **alimenta** datos al sistema federal; **AutoCheck (Experian)** recoge ventas de subasta IAAI/Copart. IAA es **fuente** de dato de salvamento, **no** un proveedor de VHR al consumidor. [V — verificación cruzada]

---

## 5. Entrega (delivery del dato/servicio)

| Canal | Detalle | Estado |
|---|---|---|
| **Web marketplace** | `iaai.com` (US), `ca.iaai.com` (CA), `iaaiuk.co.uk`/`synetiq.co.uk` (UK); desktop + responsive | [V] |
| **App buyer** | **"IAA Buyer Salvage Auctions"** (iOS/Android) — buscar, pujar, AuctionNow | [V] |
| **App seller** | **"CSAToday by IAA"** (iOS/Android) — asignar, escanear VIN, market value | [V] |
| **Plataforma de puja** | `IAA Interact®` + motor `IAA AuctionNow®` (pre-bid/proxy/live/Buy Now/Time Extended) | [V] |
| **Portal vendedor** | `CSAToday®` (`csatoday.iaai.com`) + dashboards (Title Procurement, Inspection Services Portal) | [V] |
| **Integración claims (API)** | **IAA Salvage Accelerator** en **Guidewire ClaimCenter Marketplace** (descargable): auto-asignación, **routing automático del total-loss a la facility**, status en tiempo real, assignment→sale | [V — search] |
| **ELT / títulos** | DDI Technology (electronic lien & title) integrado con 4.400+ FIs + DMVs 26 estados | [V1] |
| **Transporte** | IAA Transport™ (door-to-door dom.+int’l) + IAA Transport Global | [V] |
| **Publicaciones** | Industry Report / Data Points (PDF + web) en `iaai.com/Insights` y `/Reports` | [V] |
| **API pública de datos / feed / Excel** | **NO documentada** públicamente. Datos **gated** tras login; existen **scrapers de terceros** (Apify, Rebrowser) que venden datasets IAAI → señal de que no hay feed abierto. Integración = vía partners de claims (Guidewire), no REST público. | [V por ausencia + 3P] |

---

## 6. Precio

> **Modelo:** **two-sided.** (a) **Buyers** pagan **buyer fees** por transacción (escalados por precio de venta + tipo de licencia + volumen) + fees de plataforma/online + storage/transport. (b) **Sellers** (aseguradoras/flotas): contratos de consignación + servicios B2B (Inspection/Title/Loan Payoff) — **precios no públicos**.

| Concepto | Valor | Estado |
|---|---|---|
| **Segmentos de buyer fee** | `Licensed` · `Non-Licensed` · `Heavy Vehicle` · `Rec Rides` | [V — fee pages titles] |
| **Tiers de licensed** | `Standard Volume` (≤24 uds **o** <$75k/12 m **o** ≥5 bidder accounts) vs `High-Volume` (licencia + 25+ uds **y** $75k+ **y** <5 bidder accounts) | [3P/V1 — scribd/SCA] |
| **Internet/Proxy Bid Fee** | **$29–$119** según precio de venta | [3P] |
| **Service Fee** | **$95/unidad** (pull-out + loading) | [3P] |
| **Environmental Fee** | **$15/unidad** | [3P] |
| **Late Payment Fee** | **$50 o 2%** del precio (el mayor) | [3P] |
| **Online Fees** | aplican a IAA Buy Now / Timed / AuctionNow | [V1] |
| **Buyer's Premium / Gate / Documentation** | terceros citan ~10% std (cap $500), 12% premium, 8% moto, 15% heavy; Gate $65; Doc $75; Storage $25/día tras 2 días gratis | **[NV — cifras de calculadoras de terceros, conflictivas; páginas oficiales con bot-wall]** |
| **Membership / Premier** | niveles de membresía de comprador (descuentos por volumen) | [V1] |

> **Marca de honestidad:** las páginas oficiales de fees (`iaai.com/marketing/standard-iaa-*-buyer-fees`) devolvieron **bot-wall** en esta pasada; los importes proceden de **calculadoras/PDF de terceros** y **divergen entre sí** → **estructura [V], importes [NV]**. IAA recuerda que *"it is the sole responsibility of each buyer to verify fees"*. [V]

---

## 7. Placement — dónde coloca cada dato (patrón a copiar por cardeep)

> Patrón rector: la **ficha de vehículo (VDP)** es el HUB. La inteligencia (Score/Value) y el coste (Calculator) se **superponen sobre la propia ficha**; la decisión de siniestro y el reporting viven en **portales de vendedor/aseguradora** separados.

**A. VDP del vehículo (comprador).** Arriba `VIN / Year-Make-Model / Stock #`. **Galería** con `360 View` + `Feature Tour` + `Premium Imagery` (≤75, undercarriage→tire) + `Engine Starts` (10 s). Bloque **Condition**: `Loss Type` · `Primary/Secondary Damage` · `Start Code` · `Title/Sale Document` · `Airbags` · `Key` · `Odometer`. Bloque **Build Data** (ChromeData): `Engine/Cylinders/Fuel/Transmission/Drive Line/Body/Colores/Country of Origin`. Bloque **Sale Info**: `Branch` · `Lane-Run` · `Aisle-Stall` · `Sale date` · `Seller / Seller Type` · **`ACV`** · `Sale Status`. **Badge `Vehicle Score` (0–50)** prominente. **`Cost Calculator`** embebido (tras login).

**B. Filtro/Buscador de inventario.** Facetas = make/model, year, new inventory, vehicle type/subtype, odometer, **start code**, series, fuel, cylinders, transmission, drive line, **airbags**, **primary damage**, **loss type**, keys, body style, country of origin, colores. **`Vehicle Score`** como filtro por condición (estrecha miles de lotes a un conjunto según preferencia).

**C. Consola de subasta (AuctionNow).** Run list en tiempo real, `LIVE`, multi-watch, `Pre-Bid`/`Proxy`, `Buy Now`, `Time Extended`, `Sale Status` (`Pure Sale`/`Minimum Bid`/`On Approval`/`If Bid`).

**D. Portal de aseguradora/vendedor (CSAToday + Inspection Services Portal).** Dashboard de **salvage performance / timeline efficiencies / net returns / total loss files**; `Total Loss Predictor` (semáforo Repair/Borderline/Total) y `Loss Advisor` en el desk del perito; `Sales Decision Center` (stock-level) y `Manage Offers`/`Market Value` para la decisión de reserva/rerun.

**E. Procura de título.** `Title Procurement Dashboard` + `Title Tracker` (estado de títulos, mobile notary).

**F. Publicación de mercado.** `Industry Report` / `Data Points` en hub `Insights` (índices ASP/ACV/Gross Return/negative equity/scrap/EV).

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Dato de subasta de SALVAMENTO first-party a escala** (~2,5 M veh/año, US/CA/UK), uno de los dos únicos pools de total-loss de Norteamérica (par de Copart). [V]
2. **`Vehicle Score` 0–50 por visión computacional** desde **4 imágenes de esquina** (2 M+ imágenes anotadas) — un **único número de daño** como badge en cada VDP y como filtro de inventario. Pocos players reducen el daño a un score buscable. [V]
3. **Suite Total Loss Solutions integrada para la ASEGURADORA** (Inspection Services + Title Services + Loan Payoff + Total Loss Predictor + Loss Advisor + BidFast) que cubre el claim **de extremo a extremo** — no solo subastar, sino **decidir el siniestro**. [V]
4. **`IAA Loan Payoff`**: portal de liquidación de lien/lease con **~80% de lenders US integrados (16 de top 20)**, carta de garantía en **~1 día**, **ACH**, **$3.000 M+/2022** — único en su categoría. [V]
5. **`360 View` + `Feature Tour` + `Premium Imagery` (75 fotos, undercarriage→tire) + `Engine Starts`** — merchandising de imagen líder en salvamento (pilot +$300–600/veh). [V]
6. **Salvage Accelerator en Guidewire ClaimCenter** — integración nativa en el core de claims del asegurador (auto-routing del total-loss). [V]
7. **`Industry Report` / `Data Points`** — índices propios de mercado de salvamento (ASP, ACV, Gross Return %, negative equity, scrap, EV) citados como referencia sectorial. [V]
8. **Footprint UK real** (ex-HBC + ex-SYNETIQ con **desguace/dismantling y reciclaje de piezas**) — capacidad de circular economy que el salvamento puro no tiene. [V]

---

## 9. Gaps (lo que NO ofrece / debilidades — clave para cardeep)

1. **NO es valoración retail ni guía de precio de coche limpio.** Su "valor" es **de SALVAMENTO** (Vehicle Value) y el **ACV lo aporta el seller** (no lo calcula IAA). **Sin** retail/trade, days-to-sell, market days supply, price-to-market %, curva de depreciación multi-anual, residual %. No compite con KBB/Black Book/J.D. Power/Autovista. [V]
2. **Geografía = US/CA/UK. CERO España / EU continental.** **No es fuente de huella digital española** ni de censo de puntos de venta. Para cardeep sirve **solo como patrón de UI/placement**, no como dato. [V]
3. **No es VHR.** No emite informe de historial propio; depende de NMVTIS/AutoCheck. (Es *fuente* de dato de salvamento, no proveedor de VHR.) [V]
4. **No es censo de concesionarios ni marketplace de inventario de venta minorista.** Es marketplace de **liquidación de siniestros B2B**, no índice de la huella online de dealers. [V]
5. **Datos GATED / sin API pública.** Inventario y campos tras login; integración solo vía partners de claims (Guidewire). Existen **scrapers de terceros** que revenden datasets IAAI → no hay feed abierto/Excel. [V por ausencia + 3P]
6. **Bot-wall agresivo** en buena parte de iaai.com (selling-services, Reports, fees, bidding) → fuente difícil para scraping limpio y estable. [V — observado en esta pasada]
7. **Precios de fees opacos/inconsistentes** (páginas oficiales bloqueadas; importes solo en calculadoras de terceros que divergen). Servicios al seller **sin precio público**. [NV importes]
8. **Inteligencia atada a su propio flujo de salvamento** (no es un libro neutral multi-fuente tipo autoniq): Vehicle Value sirve para fijar reserva en SU subasta, no como valoración universal. [V]
9. **Scope de condición sesgado a daño** — su universo es total-loss/dañado; el segmento clean/whole-car (remarketing) es secundario y menor que en OPENLANE/Manheim. [V]
10. **Menor volumen que Copart** (~2,5 M vs ~4 M veh/año; cuota ~40% vs ~40%) → menos profundidad estadística por modelo/región en el pool de salvamento. [3P]

---

## 10. Fuentes (URLs)

**Identidad / corporativo / lineaje:**
- https://rbglobal.com/transaction-solutions/iaa/ — IAA como RB Global company; 170+ países; sellers (insurers/dealers/fleet/charity).
- https://www.iaai.com/marketing/ritchiebros-investor-relations — IAA adquirida por Ritchie Bros.
- https://www.prnewswire.com/news-releases/ritchie-bros-completes-acquisition-of-iaa-creating-a-premier-global-marketplace-leader-301776587.html — cierre 20-mar-2023; HQ Westchester IL; ~4.500 empleados / 210+ facilities US/CA/UK.
- https://www.autoremarketing.com/ar/with-iaa-acquisition-complete-ritchie-bros-rebrands-as-rb-global/ — rebrand RB Global; Ritchie Bros 1958.
- https://www.sec.gov/Archives/edgar/data/0001745041/000114036119010932/s002330x9_ex99-1.htm — IAA Spinco 10-12B/A (fundada 1982; KAR; Impact CA; HBC UK; spin-off 2019).
- https://www.sec.gov/Archives/edgar/data/1745041/000115752319001826/a52077822_ex991.htm — IAA 8-K spin-off 2019 (NYSE: IAA).
- gov.uk CMA: https://assets.publishing.service.gov.uk/media/6272536de90e0746ca7e55f0/IAA-SYNETIQ_-_Phase_1_Decision_.pdf — SYNETIQ £225M; clearance.
- https://autorecyclingworld.com/iaa-inc-announces-acquisition-of-synetiq-ltd/ — SYNETIQ 14 sites/~500 empleados, oct-2021.
- https://www.businesswire.com/news/home/20220224005408/en/IAA-Inc.-Announces-the-Rebrand-of-Impact-Auto-Auctions-to-IAA — Impact (CA, 2007) → IAA, 14 sites, 24-feb-2022.
- https://atfpro.co.uk/2025/04/11/iaa-announces-rebrand-of-synetiq-auction-operations-to-iaa/ — SYNETIQ→IAA UK 2025.
- https://www.dditechnology.com/iaa-acquires-ddi-technology/ — DDI Technology (ELT, 4.400+ FIs, DMVs 26 estados).

**Marketplace / VDP / campos atómicos / subasta:**
- https://www.iaai.com/ — auction types (Live/Timed/Buy Now/Gov/Public/Dream Rides/EV/Rec Rides/Specialty/Virtual Lane); IAA Interact/AuctionNow/Transport/Buy Now.
- https://www.iaai.com/buying-services/vehicle-information — "300+ data points"; ChromeData; 360 View; HD/Key Images; Engine Starts (10s); CarInspector.us.
- https://www.iaai.com/Vehicles — tipos de vehículo + facetas.
- https://www.iaai.com/buying-services/vehicle-search — filtros de búsqueda (lista de facetas).
- (snippet) personalización del listado iaai.com — columnas/campos VDP: Stock#, Title/Sale Document, Primary/Secondary Damage, Loss Type, Vehicle Type/SubType, Odometer, Start Code, Airbags, Key, Exterior/Interior Color, Engine, Fuel, Cylinders, VIN, Transmission, Drive Line Type, Body Style, Country of Origin, Branch, Lane/Run, Aisle/Stall, Market, Seller, Seller Type, ACV, Region.
- https://www.iaai.com/buying-services/bidding · https://help.iaai.com/s/article/Types-of-Auctions · https://www.iaai.com/AuctionRules — bidding/sale status (bot-wall; mecánica vía espejos).
- https://help.abetter.bid/en/articles/5315129 · https://blog.autobidmaster.com/2019/09/understanding-bidding-statuses/ — Sale Status (Pure Sale / Minimum Bid / On Approval) [3P].
- https://blog.salvagebid.com/iaa-secrets-using-loss-type-to-find-the-best-salvage-vehicle/ — Loss Types [3P].
- https://auction.ridesafely.com/guide-salvage-titles-identifying-common-damage/ · https://www.auto4export.com/blog/understanding-damage-codes-a-complete-guide-for-budget-buyers — damage/title codes [3P].
- https://www.boaconautos.com/iaa-terminologies-you-should-know/ — ACV + Start Codes (Run&Drive/Starts/Stationary) [3P espejo].

**Inteligencia / data products:**
- https://www.iaai.com/selling-services/vehiclescore + https://www.iaai.com/marketing/iaa-vehicle-score — Vehicle Score 0-50, bandas, 4 corner images, 2M+ imágenes, dimensiones.
- https://www.iaai.com/selling-services/vehiclevalue + https://www.iaai.com/Blogs/iaa-vehicle-value — Vehicle Value (rango ML; inputs).
- https://www.iaai.com/Selling-Services/total-loss-predictor — Total Loss Predictor (3 clases + inputs).
- https://www.iaai.com/selling-services/loss-advisor — Loss Advisor (puntos ponderados; ACV/salvage/threshold).
- https://www.iaai.com/selling-services/bidfast/ — BidFast (oferta 30 días, histórico).
- https://www.iaai.com/Selling-Services/sales-decision-center — Sales Decision Center (stock-level).
- https://www.iaai.com/Blogs/iaa-sales-decision-center — contexto suite.
- https://www.autoremarketing.com/ar/iaa-adds-new-ai-machine-learning-tools-to-provide-data-driven-valuations/ — AI/ML valuations (Vehicle Value + Score).

**Total Loss Solutions / claims / títulos / loan payoff:**
- https://www.iaai.com/Selling-Services/inspection-services + /inspection-services-learn-more — Inspection Services.
- https://www.iaai.com/selling-services/iaa-title-services + https://corporate.openlane.com/insurance-auto-auctions-unveils-iaa-title-management-title-tracker/ — Title Services / Title Tracker.
- https://www.iaai.com/Selling-Services/iaa-loan-payoff(-learn-more) + https://autorecyclingworld.com/iaa-loan-payoff-exceeds-3-billion-in-total-loss-transactions-in-2022/ + https://www.businesswire.com/news/home/20210720005446/ — Loan Payoff ($3B 2022; ~1 día; 80% lenders/16 of top 20; lease jul-2021).
- https://www.iaai.com/Blogs/iaa-salvage-accelerator — Salvage Accelerator + Guidewire ClaimCenter.
- https://www.iaai.com/Articles/transforming-the-total-loss-process — suite end-to-end (bot-wall; vía search).
- USPTO: 12223549, 12469083, 12475513, 11574366, 12045893 — patentes total-loss por imagen.

**Imagen / merchandising:**
- https://www.iaai.com/Buying-Services/iaa-360-view + https://www.iaai.com/Articles/giving-buyers-a-better-view + https://www.businesswire.com/news/home/20191024005655/ — 360 View (SpinCar; +$300-600/veh); Feature Tour; Premium Imagery 75 fotos; undercarriage; CSAToday 10 imágenes.
- https://impel.ai/resource/iaa-case-study/ — Impel (ex-SpinCar) merchandising.

**Gestión vendedor / apps / entrega / Canadá / UK:**
- https://www.iaai.com/selling-services/csatoday + https://csatoday.iaai.com/ + https://play.google.com/store/apps/details?id=com.iaai.csatoday — CSAToday (tools, dashboard, mobile).
- https://www.iaai.com/selling-services/iaa-active-inventory-management — Active Inventory Management.
- https://www.iaai.com/Selling-Services/mobile-assignment — Mobile Assignment (CSAToday app, start codes).
- https://play.google.com/store/apps/details?id=com.iaai.android · https://apps.apple.com/us/app/iaa-buyer-salvage-auctions/id468532534 — app comprador.
- https://www.iaai.com/buying-services/iaa-transport-delivery + https://www.iaai.com/Marketing/iaa-transport-global + https://www.iaai.com/Buying-Services/cost-calculator — Transport + Cost Calculator.
- https://ca.iaai.com/ + https://ca.iaai.com/locations/icbc-lower-mainland — IAA Canadá (ICBC).
- https://seller.iaaiuk.co.uk/Support/Locations + https://auctions.synetiq.co.uk/ — IAA UK.

**Mercado / fees / competencia:**
- https://www.iaai.com/Reports/2024-q4-industry-report + /2025-q2 + https://www.iaai.com/Articles/iaa-data-points-offer-clarity-on-industry-trends + https://www.iaai.com/Articles/iaa-analyzes-negative-equity-depreciation-trends-Q2-2025 — Industry Report / Data Points (ASP/ACV/Gross Return/negative equity/conversion 53,8%).
- https://www.iaai.com/marketing/standard-iaa-licensed-buyer-fees (bot-wall) + https://www.scribd.com/document/422264088/ + https://help.sca.auction/en/articles/6177388 + https://www.iaaicalculator.com/ — fees (estructura V; importes 3P/NV).
- https://www.wcshipping.com/blog/copart-vs-iaa-comparison-for-salvage-car-importers + https://blog.autobidmaster.com/2026/04/iaai-vs-copart/ + https://inpractise.com/articles/copart-vs-iaa-competitive-dynamics-and-ritchie-brothers-acquisition-impact — IAA vs Copart (cuota ~40/40; 2,5M vs 4M; consignación insurer-centric vs 140+ acuerdos Copart).

### Notas de verificación / marcas [NV]
- **Importes de fees**: páginas oficiales con **bot-wall**; cifras de calculadoras de terceros **divergen** → **estructura [V], importes [NV]**.
- **Sale Status timing** (7:45 pm / 6 pm PST): espejo de importadores [3P], no renderizado en `AuctionRules` oficial esta pasada.
- **Listas de Loss Type / Damage codes**: representativas vía espejos [3P]; el set oficial completo (`help.iaai.com/Glossary-of-Terms`) dio **CSS-error/SPA**.
- **Cifras de escala** (190 vs 210 facilities; 2,5M veh): varían por fuente/fecha → rango declarado.
- **Australia**: una nota de prensa cita "IAA global salvage expertise to Australian market" — **no verificado** como operación IAA propia; **omitido** del scope confirmado (US/CA/UK).
- **exa MCP**: NO disponible en el entorno; investigación con WebSearch + WebFetch intensivos. Varias páginas iaai.com (selling-services, Reports, fees, bidding, cost-calculator, csatoday, loss-advisor, AIM, transforming-the-total-loss-process) devolvieron **bot-wall**; sus datos se tomaron de **snippets de búsqueda del propio iaai.com + notas de prensa corroboradas**.
