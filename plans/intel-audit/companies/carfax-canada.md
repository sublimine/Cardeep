# CARFAX Canada — Auditoría atómica

> Slug: `carfax-canada` · Subdominio cardeep: **vin-history** · Región: Norteamérica (Canadá)
> Auditado: 2026-06-30 (re-verificado en vivo, 6 oleadas WebFetch+WebSearch) · Doctrina VAM:
> cada afirmación con fuente; `[VERIFICADO]` (leído ≥1 fuente directa), `[VERIFICADO x2]` (≥2 fuentes),
> `[NO-VERIFICADO]` donde no se confirmó. Nunca se inventa.
> Naturaleza: **estándar de facto del HISTORIAL de vehículo por VIN en Canadá** (el "Carfax" canadiense),
> con una capa de **valoración** acoplada (Market-Based Value gratis + History-Based Value ajustado por
> historial). Origen: **CarProof** (búsqueda pancanadiense de gravámenes/liens + historial). B2C (informes
> de consumo) + B2B (banca, seguros, gobierno, dealers, remarketing/OEM, garantía extendida).
> Nota de acceso: `carfax.ca` se lee bien vía WebFetch en páginas estáticas; las **vistas de informe
> dinámicas** (`vhr.carfax.ca/.../sample`) y `apireference.carfax.ca` son SPA que NO renderizan a fetch
> (pantalla de carga / template Swagger). El layout del informe se reconstruyó con páginas propias
> (`/vehicle-history-report`, `/lien-check`, `go.carfax.ca/...`) + **2 guías terceras "how to read"**.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre actual | **CARFAX Canada** | carfax.ca/about |
| Nombre original | **CarProof Corporation** (CARPROOF) | Wikipedia (CarProof); IHS/BusinessWire 2015 |
| Fundación | **2000**, London, Ontario | carfax.ca/about ("Our journey began in 2000"); búsqueda x2 |
| Fundador | **Paul Antony** (co-fundador), London, Ont. — nace de la necesidad de una **búsqueda de liens pancanadiense** en usados | búsqueda (autoremarketing/canadianautodealer); Wikipedia |
| Rebranding | **1 nov 2018**: CARPROOF → CARFAX Canada (anunciado mar 2018, finalizado 1-nov-2018) | autoremarketing; autonews.com Canada |
| HQ | **100 Kellogg Lane, London, Ontario** (oficina "state-of-the-art", mudanza ~2020) | carfax.ca/about |
| Empleados | **130+** al momento de la adquisición (2015); cifra actual no divulgada | canadianautodealer 2015; `[PARCIAL actual]` |
| Owner / grupo | **S&P Global** (división **S&P Global Mobility**) | carfax.ca/about; búsqueda |
| Misión | "We empower millions of Canadians with insights to make better decisions about vehicles." | carfax.ca/about [VERIFICADO] |
| Valores | **Objective · Transparent · Integrity · Customer advocate · Solutions oriented** | carfax.ca/about [VERIFICADO] |
| Premios | Canada's Most Admired Corporate Cultures · London Chamber of Commerce Large Business of the Year · Southwestern Ontario's Top Employers · The Career Directory · Waterstone | carfax.ca/about [VERIFICADO] |

**Cadena de propiedad (verificada, doble/triple fuente):** `[VERIFICADO x2]`
1. **Jul 2013** — IHS Inc. adquiere **CARFAX (US)** (Carfax, Inc.), líder del historial de vehículo en EE. UU.
2. **28 dic 2015** — IHS Inc. adquiere **CARPROOF** (entonces PE-backed) por **CA$650 M (~US$460 M)**.
3. **2016** — IHS se fusiona con **Markit** → **IHS Markit**.
4. **1 nov 2018** — CARPROOF se renombra oficialmente **CARFAX Canada** (licencia/unifica la marca CARFAX).
5. **2022** — IHS Markit se fusiona con **S&P Global** → CARFAX Canada queda bajo **S&P Global Mobility**.

> **Relación CARFAX US ↔ CARFAX Canada:** **empresas hermanas** bajo el mismo grupo (S&P Global Mobility),
> NO la misma entidad. CARFAX US = `carfax.com` (Carfax, Inc., adquirida por IHS jul-2013). CARFAX Canada =
> `carfax.ca` (ex-CarProof, adquirida dic-2015). Comparten marca y sinergia de datos/producto pero operan
> red de datos y catálogo de informes **separados** por país. La base CARFAX global (US) superó **30 mil
> millones de registros** en dic-2022 — la mayor del mundo; CARFAX Canada "tiene acceso a 30+ mil millones de
> registros". (Fuente: IHS/BusinessWire 2013/2015; PRNewswire dic-2022; carfax.ca.) `[VERIFICADO x2]`

> ⚠ El grupo matriz **S&P Global Mobility** ya tiene ficha propia (`s-p-global-mobility.md`) y
> **J.D. Power Valuation Services** es otro proveedor norteamericano de valor; CARFAX Canada es la pieza de
> **historial por VIN** del grupo en Canadá. No confundir con **Canadian Black Book** (valoración pura, ficha
> aparte) ni con la hermana **CARFAX US** (`carfax.md`).

**Categorías de producto:**
1. **Vehicle History Report (VHR)** por VIN — núcleo.
2. **Lien Check** (gravámenes pancanadiense).
3. **Valoración** dual: **Market-Based Value** (gratis) + **History-Based Value** (ajustado por historial).
4. **Herramientas gratis** de captación (VIN Decoder, Recall Check, Car Value).
5. **Vehicle Monitoring** (suscripción anti-fraude/recall al consumidor).
6. **Suite B2B**: VIN Scan Summary/Detail/Monitoring · **Vehicle Valuation API** / **Valuation Suite** ·
   VHR Order/Look-up API · Liens API · **Badging API** + **CPO Badging** · **Trade-in Widget** · app dealer.

**Cliente objetivo:** **consumidores** (compra/venta de usados) + **B2B**: **Banking & Lending · Insurance ·
Government · Dealers · Remarketing & OEM (ARO) · Extended Warranty**. (go.carfax.ca/big/solutions;
go.carfax.ca/aro-solutions.) `[VERIFICADO]`

---

## 2. Cobertura

- **Geografía:** **Canadá** (foco de consumo y red de datos canadiense). Red de datos **norteamericana**
  (Canadá **+ EE. UU.**) para nutrir el historial (import/export, U.S. history). **No** hay producto de
  consumo europeo bajo CARFAX Canada; EE. UU. es la **hermana CARFAX US**. (carfax.ca/vehicle-history-data.)
- **Lien check:** **todas las provincias y territorios EXCEPTO Northwest Territories**; busca en
  jurisdicciones donde el vehículo **(i) está registrado actualmente y (ii) ha estado registrado
  históricamente**. (carfax.ca/.../lien-check + support.carfax.ca.) `[VERIFICADO x2]`
- **Tipos de vehículo:**
  - **Passenger cars + light trucks** (núcleo; el VIN Decoder está "optimizado para passenger cars y light
    trucks", 40+ fabricantes Acura→Volvo). `[VERIFICADO]`
  - **No** reconoce **motocicletas** ni vehículos **anteriores a 1981** en el VIN Decoder. `[VERIFICADO]`
  - **Recreational Vehicles (RV):** soportados en **lien checks** (recreational vehicle lien) y en VIN Scan;
    **excluidos** de History-Based Value. `[VERIFICADO]`
  - **Valoración (HBV) — exclusiones explícitas:** vehículos **fabricados antes de 2000**, **no-automóviles
    (motos, RVs, trailers, boats)**, **rare/exotic**, **con branding negativo**, y **valorados bajo $1,000**.
    "Not all vehicles are eligible for a valuation." `[VERIFICADO]`
- **Nuevo vs usado:** el negocio es **usado** (historial + valor de usado). VIN decode/valor parte de
  **MY 2000–2027** en la herramienta Car Value. (WebFetch car-value: Year 2000–2027.) `[VERIFICADO]`

---

## 3. Productos + campos atómicos

### 3.1 Vehicle History Report (VHR) — núcleo

Fuente: carfax.ca/vehicle-history-report · go.carfax.ca/big/solutions · /aro-solutions · 2 guías "how to read".
El VHR es el **mismo dato** servido a consumo (web) y a B2B (UI/API). Atributos atómicos:

**A) Resumen / badges (scorecard de cabecera):** `[VERIFICADO x2]`
- **Accident / Damage** (sí/no + nº)
- **Last Registered Province**
- **Service Records** (sí/no + nº)
- **U.S. History** (sí/no)
- **Open Recalls** (sí/no + nº)
- **Stolen Vehicle Check** (estado)
- **Import / Export Records** (sí/no)
- Indicadores derivados: **Accident-free vehicle indicator**, **One-owner vehicle status**.

**B) Vehicle details (decode de VIN):** `[VERIFICADO]`
- **Year** (carácter 10 del VIN) · **Make/manufacturer** (caracteres 1–3) · **Model** (posiciones 1–4: marca,
  body style, engine size & type, model series) · **Trim** (p. ej. "SuperCrew Pickup 4WD") · **Engine type**
  (p. ej. "6.2L V8") · **Fuel type** · **Assembly location** · **Last reported odometer reading**.

**C) Accident & Damage records (línea temporal):** `[VERIFICADO x2]`
- **Date** del evento
- **Estimated repair / damage cost** (importe; *a veces sin estimación*)
- **Damage type** (collision / structural)
- **Damage location / area of impact**
- **Frame or structural damage** (flag)
- **Flood damage** · **Hail damage** · **Weather damage**
- **Airbag deployment**
- **Total loss**
- **Source** (police · insurance · collision centre)

**D) Registration records (cronológico):** `[VERIFICADO x2]`
- **Province / Country** de registro
- **Registration type**: normal / **commercial** / **rental** / **fleet** / **lease**
- **Registration dates** · **First registration date** · **Current registration**
- **Branding status** en cada jurisdicción

**E) Branding (títulos):** `[VERIFICADO]`
- **Salvage title** · **Rebuilt title** · **Total loss** · **Lemon / CAMVAP designation** · **Inactive designation**.

**F) Odometer readings (rastro cronológico):** `[VERIFICADO x2]`
- **Date** · **Kilometres recorded** · **Reporting source** · detección de **rollback / discrepancia**.

**G) Service & inspection records:** `[VERIFICADO x2]`
- **Date** · **Odometer reading** · **Service location** · **Work description** (oil change, tire rotation,
  brake replacement, inspection).

**H) Recalls:** **Open / unfixed safety recalls** (manufacturer). `[VERIFICADO]`

**I) Stolen check:** **Actively declared stolen** (match contra bases de robo). `[VERIFICADO]`

**J) Import / U.S. history:** **Canada import records** · **Detailed U.S. history** · **export status**. `[VERIFICADO]`

**K) Insurance & claims:** **Canadian insurance & accident claims history** (ver §4 — DIFERENCIAL clave);
incluye reclamaciones de **accidentes, weather damage, vandalism, liability events**; **ICBC check** vía add-on
**Verified BC** (vehículos con registro en BC). `[VERIFICADO x2]`

**L) Lien / financiero (add-on):** ver §3.6.

### 3.2 Valoración — Market-Based Value (gratis)

Fuente: carfax.ca/whats-my-car-worth/car-value · go.carfax.ca/data-driven-valuation · clutch.ca. `[VERIFICADO x2]`

- **Qué es:** "Car Value" / "What's My Car Worth" — valor de mercado actual **regionalizado**, gratis, < 2 min.
  "Based on what others paid for similar vehicles, not just the asking price."
- **Inputs (form de consumo):** **VIN** **o** **Year/Make/Model** → luego **Select Trim · Select Engine ·
  Select Drivetrain · Select Transmission · Select Body Style · Select Box Length** (trucks) + **Odometer** +
  **Postal code** + checkbox "I own this vehicle".
- **Factores del modelo (ML):** **year/make/model/trim · odometer · province · seasonality · daily market
  data · location (postal code)**.
- **Output:** **NO una cifra única** sino un **Value Range** segmentado en **4 escenarios de transacción**
  (ver §7.B): **Selling Privately · Trading In (with tax savings factored in) · Buying Privately · Buying at
  a Dealership (Retail Price)**. `[VERIFICADO x2: clutch + página propia]`

### 3.3 Valoración — History-Based Value (HBV)

Fuente: carfax.ca/whats-my-car-worth/history-based-value · go.carfax.ca/aro-solutions · /data-driven-valuation
· BusinessWire feb-2023. `[VERIFICADO x2]`

- **Qué es:** **"first and only valuation model in Canada that automatically adjusts for each vehicle's unique
  history."** Lanzado **feb/mar 2023** (para dealers). "The most in-depth valuation, straight from the experts."
- **Mecánica:** **toma el Market-Based Value / Value Range y lo AJUSTA** por el historial específico de ESE VIN.
- **Factores de ajuste (atómico, verbatim):** **Accident/damage history · Service history · Ownership history
  (number of owners) · Vehicle use (rental, fleet, personal) · Odometer reading · Location (postal code) ·
  Weekly Adjusted Market Trends**.
- **Refresco del dato de mercado:** **cada 7 días** ("refreshed every seven days with the latest data").
- **Ventana de canje (consumo):** el **History-Based Value Report** debe **redimirse en 14 días** desde la
  compra ("the used vehicle market changes fast").
- **Acceso:** **gratis con la compra de un VHR** ("comes free with the purchase of a Vehicle History Report").
- **Elegibilidad (exclusiones):** ver §2 (pre-2000, no-autos, rare/exotic, branding negativo, < $1,000).
- **Motor (verificado en partnership AutoVerify):** "**machine learning model which uses current listings and
  recent sold prices of comparable vehicles to provide current and regionalized values**." `[VERIFICADO x2]`

### 3.4 Vehicle Valuation API / Valuation Suite (B2B)

Fuente: go.carfax.ca/data-driven-valuation · /big/solutions · /aro-solutions. `[VERIFICADO]`

| Capa | Inputs / factores | Casos de uso |
|---|---|---|
| **Market-Based Value (+ Value Range)** | year/make/model/trim · odometer · province · seasonality · daily market data | Sourcing/appraising; portfolio |
| **History-Based Value (VIN-Specific)** | Market-Based + accident/damage · service · ownership · use type · postal code | Loan value, total loss, policy pricing |

- **Casos B2B declarados:** **Lenders** (loan value, portfolio risk, repossession) · **Insurance**
  (estimated value, policy pricing, total loss) · **Extended Warranty** (policy pricing, portfolio risk,
  repossession). `[VERIFICADO]`
- **"Valuation Suite"** para dealers (sourcing + appraising). El B2B menciona **"five valuation outputs"** vía
  gráfico, sin desglosar. `[NO-VERIFICADO el detalle de los 5 outputs]`
- **Cobertura de dato (stat clave):** **acceso a >90% de TODOS los datos de listings de vehículos en Canadá**
  + "billions of data records from thousands of sources". `[VERIFICADO x2]`
- **Volumen de valoración:** **1.3 millones de informes de valoración completados en 2024**. `[VERIFICADO]`
- **Influencia de ubicación (verbatim):** "in urban areas, increased dealer competition and supply often lead
  to lower prices." `[VERIFICADO]`

### 3.5 Suite B2B — VIN Scan (3 niveles)

Fuente: go.carfax.ca/big/solutions · /aro-solutions. `[VERIFICADO x2]`

| Producto | Qué es | Campos / groupings atómicos |
|---|---|---|
| **VIN Scan Summary** | Historial "at a glance", coste-eficiente. UI o API. | **Trim-level decode** · **Total damage over $5,000** (flag) · **Title brands** · **Stolen status** · **Potential VIN clone detection** · **First registration date** · **Current registration** · **Mileage data** · flags sí/no de historial y valoración. **Upgrade path** a VHR completo o liens (fees apply). |
| **VIN Scan Detail** | Desglose profundo en **10 groupings** para underwriting/garantía/riesgo. API o **bulk sFTP**. | **1. Vehicle Description · 2. Vehicle Demographic · 3. Latest Activity · 4. Potential Problem Indicator · 5. Potential Damage · 6. Ownership History · 7. Severe Problem · 8. Proxy Odometer · 9. Potential Fraud · 10. (Data Dictionary)**. |
| **VIN Scan Monitoring** | Vigilancia continua de cambios de estado. Portal + CSV + email. | Monitoriza: **Title branding · Severe problem · Registration change · Service record · Exported · Inactive · VHR ordered · Recall · Stolen**. **Unlimited VINs**, frecuencia **customizable (hasta nightly)**, **email alerts**, **customized flagging**, carga bulk/single VIN. |

### 3.6 Lien Check (origen CarProof)

Fuente: carfax.ca/.../lien-check · support.carfax.ca · vinaudit.ca. `[VERIFICADO x2]`

- **Qué busca:** registros gubernamentales por VIN en cada provincia/territorio (**excepto Northwest
  Territories**), **actual + histórico**. Soporta **single / multi-province** y **RV lien**.
- **Campos devueltos cuando HAY lien (atómico):**
  - **Debtor information** — nombre y dirección del individuo/empresa que debe el dinero.
  - **Secured party** — nombre y dirección del **lender / institución financiera**.
  - **Registration agent** — quién registró el lien en nombre del lender.
  - **Collateral classification** — confirma que el lien está atado a ESE vehículo.
  - *(El **monto** exacto adeudado NO se especifica en la página — `[NO-VERIFICADO]`.)*

### 3.7 Integración y badging (dealers / marketplaces / OEM)

Fuente: go.carfax.ca/aro-solutions · autoverify.com · businesswire. `[VERIFICADO x2]`

| Producto | Qué es | Campos / outputs atómicos |
|---|---|---|
| **VHR Order/Look-up API** | Pedir/consultar VHR desde DMS/inventario | Quick VHR access · creación de **inventory management system** · **Auto VHR ordering** por inventario · más eficiencia en sistemas/procesos. |
| **Badging API** | Badges automáticos en listings online | **No Reported Accidents** (sin daño reportado a CARFAX) · **One Owner** (un único dueño previo, personal/personal lease) · **Low Kilometres** (**< 18,000 km/year** con patrón de odómetro normal) · **CPO Badge** (manufacturer-certified pre-owned que cumple el programa). |
| **CPO Badging** (OEM) | Promociona vehículos que cumplen el programa CPO del OEM | Badge mostrado **sobre el CARFAX Canada VHR**; diferenciación competitiva. |
| **Vehicle Trade-in Widget** (dealer) | Caja de trade-in embebible | **History-based estimated range** revisando trim/options/reported history; capta lead. Subdominio `truetrade.carfax.ca`. Integración **AutoVerify** → webs de dealer + **marketplace Kijiji** + Kijiji Autos. |
| **CARFAX Canada for Dealers** (app móvil iOS) | Lookup de VHR/valor en móvil | App Store id6523416646. `[campos no detallados]` |
| **Kijiji Autos price analysis** | CARFAX Canada **powers** la herramienta de análisis de precio de Kijiji Autos | Etiquetas/labels exactos del listing `[NO-VERIFICADO]` (press stub no renderiza). Partnership directo + vía AutoVerify. |

### 3.8 Herramientas gratis al consumidor + monitoring

Fuente: carfax.ca/tools/* · /vehicle-monitoring-subscription. `[VERIFICADO x2]`

| Producto | Qué es | Campos / atómico |
|---|---|---|
| **VIN Decoder** (gratis) | Decode de 17 dígitos | **Model year** (char 10) · **Manufacturer** (char 1–3) · **Model/brand/body style/engine size&type/model series** (char 1–4) · **Engine type** (p. ej. "6.2L V8") · **Trim** (p. ej. "SuperCrew Pickup 4WD"). Detecta **VIN fraud / VIN cloning** (mismatch tipo: "VIN dice truck pero ves un SUV"). Solo passenger cars/light trucks; **no motos**, **no < 1981**. |
| **Recall Check** (gratis) | Recalls de seguridad por VIN | **Open recalls** (1 de 4 vehículos CA tiene un recall sin reparar). |
| **Car Value** (gratis) | = Market-Based Value (§3.2) | Value Range en 4 escenarios. |
| **Vehicle Monitoring Subscription** | Vigilancia anti-fraude/recall — **$88.95/año (< $8/mes)** | **3 capas:** (1) **Automatic Activity Alerts** — email cuando se detecta nueva actividad del VIN para confirmar que no es sospechosa; (2) **Monthly VIN Fraud Check** — escanea billones de registros (VIN clonado/comprometido); (3) **Monthly VHR** — recalls, service, condición, daño, odómetro, salvage/rebuild. **12 meses, NO auto-renueva**, email + VHR dashboard. **NO incluye History-Based Value ni Lien Check.** "Some instances of VIN fraud may not be detected." Solo detecta, no compensa. |

---

## 4. Metodología / fuentes de datos

- **Volumen:** "**access to billions of data records from thousands of trusted sources across North
  America**"; "**30+ billion data records**" (base CARFAX global, hito dic-2022); **5+ millones de VHR
  vendidos/año** + **1.3 M valoraciones en 2024**; **>90% de los datos de listings de Canadá**.
  (carfax.ca/vehicle-history-report; /vehicle-history-data; /data-driven-valuation; PRNewswire.) `[VERIFICADO x2]`
- **Tipos de fuente (atómico, verbatim página propia):** **Canadian + U.S. motor vehicle agencies ·
  insurance agencies · collision repair facilities · auto auctions · police departments** + "and more"
  (registries provinciales/territoriales, service shops, fleet/rental). `[VERIFICADO]`
- **DIFERENCIAL de fuente (moat) — `[VERIFICADO x2]` (búsqueda + dealer pages chilliwackvw/417nissan/autocan):**
  CARFAX Canada es **el único servicio que da al consumidor datos canadienses de SEGUROS y reclamaciones de
  siniestro**, con datos de la **industria aseguradora privada** + el **asegurador público de Saskatchewan
  (SGI)**; y, vía **Verified BC**, búsqueda instantánea en la base de **ICBC** (asegurador público de British
  Columbia). *(Nota de honestidad: esta afirmación de "único" NO aparece en la página oficial
  `/vehicle-history-data`; se sostiene en CARFAX marketing reproducido por dealers + autocan.ca.)*
- **Motor de valor:** **machine learning** sobre **current listings + recent sold prices** de comparables →
  valor **current + regionalizado**; HBV añade la capa de ajuste por historial del VIN; **refresco semanal**.
- **Partnerships de dato:** **AutoVerify** (2025; integra valoración CARFAX en webs de dealer + Kijiji +
  TD Auto Finance) · **Kijiji** (powers Kijiji Autos price analysis, abr-2025) · **ISB Global Services**
  (2025; expande VIN Scan a grandes aseguradoras canadienses) · colaboración policía/aseguradoras/registros
  para detección de robo y fraude (2024). `[VERIFICADO]`
- **Disclaimer (honesto, en su propia web):** el informe "**is based only on information supplied to CARFAX
  Canada by participating data sources**"; "**There may be other information about a vehicle that has not been
  reported**"; "there are still some [sources] that do not make their data available to anyone". →
  **incompleto por diseño**. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web de consumo** | `carfax.ca/order` → compra; **el VIN se introduce CUALQUIER momento DESPUÉS de la compra** ("No VIN? No problem!"). |
| **VHR dashboard online** | `vhr.carfax.ca` — vista de informe dinámica (SPA, no renderiza a fetch). |
| **API REST** | `apireference.carfax.ca` (Swagger UI; `integrationsupport@carfax.ca` / Peter Jardine): **VHR Order/Look-up · Vehicle Valuation · Liens · VIN Scan Summary/Detail · Badging**. `[schema exacto tras login — NO-VERIFICADO]` |
| **Bulk sFTP** | VIN Scan Detail (ficheros de atributos por VIN). |
| **CSV / email** | VIN Scan Monitoring (salida CSV + alertas email). |
| **Portal B2B** | `go.carfax.ca` (segmentos Banking/Insurance/Government + ARO + data-driven-valuation); portal de monitoring. |
| **Widget embebible** | **Trade-in Widget** (`truetrade.carfax.ca`) en webs de dealer + listings de **Kijiji** (vía AutoVerify). |
| **App móvil** | **CARFAX Canada for Dealers** (iOS). |
| **Badges en listings** | Badging API → badges automáticos en anuncios online + CPO sobre el VHR. |

---

## 6. Precio (consumo, CAD — vivo en `/order`) `[VERIFICADO]`

| Producto | Precio | Incluye |
|---|---|---|
| **VHR + Lien Check** (Essential) | **$77.95** | Historial completo + lien check (la opción "más comprehensiva"). |
| **VHR sin Lien Check** | **$58.95** | Igual sin lien. |
| **3 Reports + 1 Lien Check** (Best Deal) | **$146.95** | "25% Off $195.85" — 3 vehículos. |
| **History-Based Value** | **Gratis con VHR** | Redimir en 14 días; "not all vehicles eligible". |
| **Vehicle Monitoring Subscription** | **$88.95/año** (< $8/mes) | 12 meses, sin auto-renovación. |
| **VIN Decoder · Recall Check · Car Value (Market-Based)** | **Gratis** | Herramientas de captación. |
| **Lien add-on** (delta) | **~$19** | Diferencia $77.95 − $58.95. |

- **Add-on Verified BC (ICBC):** existe como complemento para vehículos con registro en BC. `[precio NO-VERIFICADO]`
- **B2B:** **sin tarifa pública** — licencia/suscripción + contactar ventas; bulk/volumen.
- **Nota de revendedores:** terceros citan $43.95 / $60.95 (precios antiguos o de reventa); el **vivo en
  carfax.ca/order = $58.95 / $77.95**. Existe arbitraje de revendedores. `[CONTRASTE]`

---

## 7. Placement (patrón web — clave para cardeep)

> Dónde coloca CARFAX Canada cada dato. Esto es lo que cardeep imita para ubicar cada métrica.

**A. VHR de consumo (dashboard online) — zona y orden:** `[VERIFICADO x2: clutch + carnation]`
- **Zona de cabecera (header):** conviven el **scorecard de badges/iconos resumen** (Accident/Damage ·
  Last Registered Province · Service Records · U.S. History · Open Recalls · Stolen Check · Import/Export —
  lectura sí/no/contador de un vistazo) y el **bloque Vehicle Details** (year/make/model/trim/engine/fuel/
  assembly/last odometer). *(Las dos guías difieren en cuál imprimen primero; ambos viven arriba.)*
- **Secuencia vertical de secciones de registro:**
  1. **Accident & Damage Records** — línea temporal; cada fila: **date · estimated cost · type ·
     location/impact · source** (police/insurance/collision).
  2. **Registration Records** — cronológico: province/country · registration type (normal/commercial/rental/
     fleet/lease) · dates · branding.
  3. **Odometer Readings** — rastro: date · km · source (detecta rollback).
  4. **Service Records** — date · odometer · location · work description.
  5. **Open Recalls** → 6. **Stolen Vehicle Check** → 7. **Import/Export Records**.
  8. **Insurance & Claims History** (diferencial CA) · 9. **Lien Information** (si se compró).
  10. **History-Based Value** anexado (valor gratis sobre el mismo VIN).
> *El historial vive en una ficha vertical rica encabezada por un scorecard de badges; el valor (HBV) cuelga
> al final como capa derivada del historial.*

**B. Car Value (consumo, standalone):** form de input (VIN **o** Y/M/M/T + engine/drivetrain/transmission/
body/box-length + odómetro + código postal) → pantalla de resultado = **Value Range** (rango, no cifra única)
**segmentado en 4 escenarios de transacción**: **Selling Privately · Trading In (con tax savings factorizado)
· Buying Privately · Buying at a Dealership (Retail Price)**. → patrón "valor como rango, partido por intención".

**C. Trade-in Widget (embed en web de dealer):** caja CTA; el shopper mete su coche → **rango estimado
history-based** + lead al dealer; mismo valor aparece en **Kijiji / Kijiji Autos**. → patrón "CTA de
valoración white-label que captura lead".

**D. Badges en marketplace (Badging API):** sobre el anuncio online, badges **No Reported Accidents / One
Owner / Low Kilometres / CPO**. → patrón "sellos de confianza sobre la tarjeta del coche".

**E. B2B VIN Scan Summary:** vista "at a glance" — flags sí/no + campos clave (trim, damage>$5k, brands,
stolen, VIN clone, registro, mileage) en UI o respuesta API; con **upgrade path** a VHR/liens. →
patrón "tarjeta de screening rápido con escalado".

**F. B2B VIN Scan Detail:** **10 groupings** de atributos (Vehicle Description, Demographic, Latest Activity,
Problem/Damage/Fraud indicators, Ownership, Severe Problem, Proxy Odometer) en fichero por VIN (API/sFTP). →
patrón "diccionario de atributos en columnas".

**G. B2B Monitoring:** **portal** con dashboard de cartera + **email alerts** + CSV; cada VIN levanta **flags**
al cambiar de estado (branding/severe/registro/service/recall/stolen/export/inactive). → patrón "watchlist con alertas".

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Estándar de facto del historial por VIN en Canadá** — 5M+ informes/año, acceso a 30B+ registros y **>90%
   de los listings de Canadá**; "more insight than any other source".
2. **Datos canadienses de SEGUROS y reclamaciones de siniestro** — **único** servicio con datos de la
   industria aseguradora privada CA + **SGI Saskatchewan** + **ICBC (Verified BC)**. Moat regulatorio/relacional.
3. **Lien Check pancanadiense** (origen CarProof) — capa **financiero-legal** con 4 campos atómicos (debtor,
   secured party, registration agent, collateral classification) que los puros proveedores de valor no dan.
4. **History-Based Value** — **primer y único** modelo en Canadá que **auto-ajusta por el historial único**
   del VIN (daño/servicio/dueños/uso/km/ubicación), refresco semanal; **gratis con el VHR**.
5. **Doble valor:** Market-Based (gratis, ML listings+sold) + History-Based (ajustado) — y ambos por **API /
   Valuation Suite**; **1.3M valoraciones en 2024**.
6. **Detección de VIN fraud / VIN cloning** + **Monitoring** continuo (consumo y B2B), reforzado por
   partnerships con policía/aseguradoras/ISB.
7. **Suite B2B granular:** VIN Scan Summary→Detail (**10 groupings**)→Monitoring, **Badging API** (4 sellos),
   **CPO Badging** OEM, VHR Order/Look-up API.
8. **Distribución en el punto de decisión:** powers **Kijiji Autos** price analysis + **AutoVerify** (dealer
   sites + Kijiji + TD Auto Finance) → valor en el marketplace donde el shopper ya está.
9. **Respaldo S&P Global Mobility** — sinergia de datos/tecnología con CARFAX US y el resto del grupo.
10. **Honestidad metodológica** publicada (disclaimer "incompleto por diseño") — transparencia poco común.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Canadá** en consumo (EE. UU. = hermana CARFAX US, entidad separada; sin Europa). ← hueco para cardeep.
2. **Lien NO cubre Northwest Territories**; **ICBC (BC)** requiere add-on **Verified BC**; el **lien** no está
   en el informe base (add-on ~$19).
3. **VIN Decoder / valoración limitados a passenger cars + light trucks**; **sin motos**, **sin < 1981**.
   **HBV excluye** pre-2000, no-autos, rare/exotic, branding negativo y < $1,000. Sin medium/heavy-duty.
4. **Car Value entrega solo RANGOS** — sin cifra exacta, sin oferta real desde la herramienta. HBV exige
   **comprar un VHR** (no es valor gratis standalone) y se **caduca a 14 días**.
5. **Sin forecast de valor residual / curva de depreciación / valor futuro 1–72m** (a diferencia de Canadian
   Black Book / J.D. Power) — la valoración es **solo valor actual**, no proyección.
6. **Sin KPIs de velocidad de mercado retail** (days-to-sell, market days' supply, price-to-market %) — no es
   inteligencia de inventario tipo vAuto / CBB Pulse / Retail Market Insights.
7. **VIN decode "ligero"** (year/make/model/engine/trim) — **no** es un catálogo profundo de specs/equipamiento
   /build-data como Chrome Data / DataOne / Autovista; el decode sirve al historial, no se vende como dataset.
8. **Datos incompletos por diseño** — solo lo que reportan fuentes participantes; no ve reparaciones en
   efectivo no declaradas, óxido, bajos, ni servicio no reportado.
9. **Precio relativamente alto** vs alternativas canadienses (VinAudit, etc.); arbitraje de revendedores.
10. **Monitoring no compensa** ante robo/fraude (detecta, no protege ni indemniza) y **excluye HBV + Lien**.
11. **Schema de API no público** (tras login/Swagger/contacto) — contrato exacto de campos `[NO-VERIFICADO]`.
12. **Etiquetas exactas del Kijiji Autos price analysis** (Great/Good/Fair price, etc.) `[NO-VERIFICADO]`.

---

## 10. Fuentes

**Páginas propias CARFAX Canada (verificadas en vivo 2026-06-30):**
- About / identidad: https://www.carfax.ca/about
- Car Value / "What's My Car Worth": https://www.carfax.ca/whats-my-car-worth/car-value
- History-Based Value: https://www.carfax.ca/whats-my-car-worth/history-based-value
- Vehicle History Report: https://www.carfax.ca/vehicle-history/vehicle-history-report
- Lien Check: https://www.carfax.ca/vehicle-history/vehicle-history-report/lien-check
- Sample report (SPA, no renderiza a fetch): https://www.carfax.ca/vehicle-history/sample-report · https://vhr.carfax.ca/en-ca/sample/vhrlc
- Order / precios: https://www.carfax.ca/order
- Fuentes de datos: https://www.carfax.ca/vehicle-history-data · soporte liens: https://support.carfax.ca/en/support/solutions/articles/17000134058-how-does-carfax-canada-check-for-liens-
- VIN Decoder: https://www.carfax.ca/tools/vin-decode · Recall Check: https://www.carfax.ca/tools/recall-check
- Vehicle Monitoring: https://www.carfax.ca/vehicle-monitoring-subscription
- Soluciones B2B (Banking/Insurance/Government): https://go.carfax.ca/en-ca/big/solutions
- Soluciones ARO (Remarketing/OEM): https://go.carfax.ca/aro-solutions
- Data-Driven Valuation (B2B): https://go.carfax.ca/data-driven-valuation
- API Reference (template Swagger): https://apireference.carfax.ca/
- Trade-in Widget: https://truetrade.carfax.ca/ · Kijiji press: https://www.carfax.ca/about-carfax/press-centre/carfax-canada-powers-kijijiji-autos-price-analysis-tool

**Terceros / verificación (≥2 fuentes):**
- Identidad/owner/S&P Global + cadena CarProof→IHS(2015,CA$650M/US$460M)→IHS Markit→S&P Global(2022), rebrand 1-nov-2018: https://en.wikipedia.org/wiki/CarProof · https://www.autoremarketing.com/arcanada/carfax-parent-company-buys-carproof/ · https://www.autoremarketing.com/arcanada/carproof-finalizes-rebranding-carfax-canada/ · https://canada.autonews.com/article/20180319/CANADA/180319724/carproof-rebranding-as-carfax-canada · https://canadianautodealer.ca/2015/12/carproof-sold-to-ihs-for-650-million/ · https://www.autonews.com/article/20151228/RETAIL05/151229941/carfax-owner-buys-canadian-vehicle-history-provider-for-460-million/
- History-Based Value (feb 2023 / first&only / factores / 7 días / ML): https://www.businesswire.com/news/home/20230223005988/en/CARFAX-Canada-Launches-History-Based-Value · https://www.autoremarketing.com/arcanada/carfax-canada-rolls-out-history-based-value-for-dealers/ · https://canadianautodealer.ca/2023/03/vehicle-history-and-vehicle-valuation-come-together/
- Insurance moat / SGI / ICBC / Verified BC: https://www.autocan.ca/carfax/ · https://www.chilliwackvw.ca/carfax-canada.html · https://www.417nissan.com/carfax/
- 30B registros (base global, dic-2022): https://www.prnewswire.com/news-releases/carfax-hits-30-billion-records-in-vehicle-history-database-301696301.html
- 90% listings + 1.3M valoraciones 2024 + ML listings/sold + AutoVerify/Kijiji/TD: https://autoverify.com/press-releases/autoverify-and-carfax-canada-partner-to-bring-more-accurate-vehicle-valuations-to-dealers-and-car-shoppers · https://canadianautodealer.ca/2025/06/autoverify-partners-with-carfax-canada-on-integration-2/ · https://www.businesswire.com/news/home/20250430242352/en/CARFAX-Canada-and-Kijiji-Partner-to-Deliver-Improved-Vehicle-Valuations
- Lien laws/coverage (NWT excl.): https://www.vinaudit.ca/blog/lien-search-laws-canada-provinces-territories
- Layout / "how to read" (placement) + Car Value 4 escenarios: https://www.clutch.ca/blog/posts/how-to-read-a-carfax-report · https://www.clutch.ca/blog/posts/carfax-car-value · https://autotrends.carnationcanadadirect.ca/post/carfax-canada-report-how-to-read-it-what-it-shows-and-what-to-check-before-you-buy-in-ontario
- ISB Global Services (VIN Scan a aseguradoras): https://www.businesswire.com/news/home/20250929882097/en/ISB-Global-Services-and-CARFAX-Canada-Expand-their-VIN-Scan-Partnership-to-Major-Canadian-Insurers
- Anti-fraude (policía/aseguradoras): https://www.businesswire.com/news/home/20240619120718/en/CARFAX-Canada-Helps-Canadians-Tackle-Auto-Theft-and-Fraud
- App de dealer (iOS): https://apps.apple.com/ca/app/carfax-canada-for-dealers/id6523416646

### Notas de verificación
- Owner S&P Global Mobility + cadena CarProof→IHS(2015,CA$650M)→IHS Markit→S&P Global(2022), rebranding 1-nov-2018: **triple+ fuente** (Wikipedia + autoremarketing + autonews + canadianautodealer + carfax.ca/about). **[VERIFICADO x2]**
- Relación CARFAX US (Carfax Inc, IHS jul-2013) como **hermana**; base global 30B+ (dic-2022): **[VERIFICADO x2]**
- Campos del VHR + 10 groupings de VIN Scan Detail + 2 value types + Badging (4 badges verbatim): páginas B2B `go.carfax.ca` (/big/solutions, /aro-solutions, /data-driven-valuation), leídas en vivo. **[VERIFICADO]**
- HBV "first and only" + factores + refresco 7 días + canje 14 días + exclusiones (pre-2000/no-autos/rare/branding/<$1,000) + ML listings/sold: businesswire + página propia HBV + ARO + AutoVerify. **[VERIFICADO x2]**
- Car Value: inputs (incl. Box Length) + Value Range + 4 escenarios (Selling/Trading w-tax/Buying/Dealership-Retail): página propia + clutch. **[VERIFICADO x2]**
- Lien: NWT excluido, current+historical, 4 campos (debtor/secured party/registration agent/collateral): página `/lien-check` + support + vinaudit. **[VERIFICADO x2]** — monto adeudado **[NO-VERIFICADO]**.
- Insurance/claims data como ÚNICO en CA + SGI + ICBC (Verified BC): **doble fuente** (autocan + dealer pages). **[VERIFICADO x2]** — *NO en página oficial /vehicle-history-data (marketing reproducido).*
- 90% de listings de Canadá + 1.3M valoraciones 2024: data-driven-valuation + AutoVerify. **[VERIFICADO x2]**
- Precio vivo $58.95 / $77.95 / $146.95 + monitoring $88.95 + VIN tras compra: carfax.ca/order. **[VERIFICADO]** — precios revendedores: **[CONTRASTE]**.
- VIN Decoder posiciones (char 10 año, 1-3 fabricante, 1-4 modelo) + no motos/no <1981: carfax.ca/tools/vin-decode. **[VERIFICADO]**
- Empleados actuales: **[PARCIAL]** (130+ en 2015). Schema exacto de la API: **[NO-VERIFICADO]** (SPA/Swagger tras acceso). Verified BC precio + "5 valuation outputs" + Kijiji labels: **[NO-VERIFICADO]**.
