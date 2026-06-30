# Auditoría atómica — Experian Automotive (AutoCheck®)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos e inteligencia de automoción centrada en HISTORIAL DE VEHÍCULO / PROVENANCE (VIN-history)**: informes de historial (AutoCheck®), score predictivo patentado, API de atributos en tiempo real (Auto AccuSelect™), monitorización de cartera (AutoCheck Triggers), informes de título federales (NMVTIS) y la base de datos norteamericana de 900M+ vehículos. **NO es un editor de valoración/cote** (no da residuales, retail/trade, days-to-sell): su materia prima es el *historial* de cada VIN (siniestros, título, odómetro, propietarios, uso, recalls, subasta).
> Web del scope (orquestador): https://www.experian.com/automotive/vehicle-history-services · Portal de producto consumidor: https://www.autocheck.com/ · API: https://www.experian.com/automotive/auto-accuselect · Plataforma de datos: https://www.experian.com/automotive/auto-vehicle-data
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **vin-history**.
> Fecha auditoría: 2026-06-30. Método: navegación de experian.com/automotive (vehicle-history-services, autocheck-business, auto-accuselect, auto-vehicle-data, autocheck-lenders, autocheck-integrations, automotive-autocheck-nmvtis(+new-customer), experian_autocheck_report, autocheck_score), blogs Experian Insights (newly-designed report, keeping-score, buyback-protection), notas de prensa experianplc.com (AutoCheck Elite 2012, AutoCheck Triggers 2013, AutoCheck Mobile 2011, KBB 2011), guías de lectura de informe de terceros (carvins.net, usedcargenius, cargurus), One Auto API (Experian AutoCheck UK — lineaje separado), CB Insights, AAMVA/BJA (NMVTIS), + cotejo de cobertura/identidad en ≥2 páginas.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). Discrepancias de cifras marcadas, NO resueltas por invención.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca producto | **AutoCheck®** (informe de historial) · **AutoCheck Score℠** (score patentado) · **Auto AccuSelect™** (API) · **AutoCheck Triggers** · **NMVTIS reports** · **AutoCheck Elite** · **AutoCheck Buyback Protection** · **Fraud Protect™** | [V] |
| División | **Experian Automotive** | [V] |
| Matriz | **Experian plc** — "global data and technology company" | [V] |
| HQ división (Automotive) | **475 Anton Boulevard, Costa Mesa, California 92626, EE.UU.** | [V — CB Insights] |
| HQ corporativo matriz | **Dublín, Irlanda** (sede corporativa registrada); HQ operativos: **Nottingham (UK)**, **Costa Mesa (California)**, **São Paulo (Brasil)** | [V] |
| Cotización | **London Stock Exchange, ticker EXPN**; constituyente **FTSE 100**; ADR OTC **EXPGY** | [V] |
| Plantilla matriz | **~22.500 personas / 32 países** (FY24 reporte) — variación con **"25.200 personas / 33 países"** citado en la web Experian.com (ver Gaps) | [V — variación de fuente] |
| Escala de datos de consumo (matriz) | "insights on **more than 250 million U.S. individuals**, miles de señales behavioral/lifestyle/purchase-intent" | [V] |
| Origen del producto AutoCheck | AutoCheck adquirido por Experian **~2002** vía compra de la división de vehicle-history report de **R.L. Polk & Co.** | [V — fuente única, ver Gaps] |
| Categoría | **Proveedor de historial de vehículo (VIN-history / provenance) + base de datos VIN + scoring predictivo**. Competidor directo de **Carfax**; complementario (no sustituto) de los editores de valor (KBB/J.D. Power). | [V] |

### Hitos / cronología [V]
- **~2002** Experian entra en vehicle-history al adquirir el negocio de la división Polk → nace **Experian Automotive / AutoCheck**.
- **2007-2008** Lanzamiento y difusión del **AutoCheck Score℠** (score patentado de comparación por clase/edad). (Nota de prensa Experian plc 2008.)
- **2011** **AutoCheck Mobile** (Android + iPhone, consumidor) · alianza **Kelley Blue Book** (AutoCheck en KBB.com).
- **2012 (1-feb)** **AutoCheck Elite** (programa dealer con market intelligence). Base de datos citada entonces: **650M+ vehículos**.
- **2013** **AutoCheck Triggers** (monitorización de cambios de historial en cartera/inventario para lenders, dealers y OEM CPO).
- **Reciente** Rediseño del informe AutoCheck (visualización de Accident & Damage con severidad, "Vehicle History at-a-Glance", "Chronological Detailed History"). **Auto AccuSelect™** (API REST de atributos) sobre base **900M+ vehículos / 11B+ registros**.

### Clientes objetivo (segmentos declarados) [V]
1. **Dealers franquiciados** (franchise).
2. **Dealers independientes**.
3. **Lenders / financieras de auto** (riesgo de colateral, originación, cartera).
4. **OEMs** (incl. programas **Certified Pre-Owned**).
5. **Automotive aftermarket** (posventa).
6. **Ad agencies** (agencias de publicidad / marketing automoción).
7. **Allied auto industry** (industria auxiliar).
8. **Consumidores** (autocheck.com, app móvil, packs de informes).
9. **Marketplaces / portales** (Cars.com, CarGurus, KBB, Autotrader… vía integración).
10. **Aseguradoras** (loss/total-loss data, fraude). [A — implícito por uso de insurance loss data]

---

## 2. Cobertura

### Geográfica [V]
- **EE.UU.** (núcleo absoluto): base **North American Automotive Database℠** = "North America".
- **Canadá** (parcial): AccuSelect expone explícitamente **"Canadian & Grey Market Registration"** → cobertura de matrícula/título canadiense.
- **Reino Unido**: existe un **"Experian AutoCheck" UK** (autocheck.co.uk) y un servicio "Experian AutoCheck" revendido vía **One Auto API** con datos UK (MIAFTR, PNC, outstanding finance, keeper/plate changes). Se trata como **lineaje separado** del AutoCheck US (ver §3.13 y Gaps).

### Escala de la base de datos [V]
- **900+ millones de vehículos** en la North American Automotive Database (era **650M+** en 2012 — crecimiento verificado).
- **11+ mil millones (11B+) de registros de historial de vehículo**.
- Fuentes de siniestro: **"decenas de miles de fuentes de accidente distintas, la mayoría aportando datos en exclusiva a Experian"**.
- **114+ millones** de vehículos en circulación con **historial de accidente** (cifra citada en vehicle-history-services).
- "**More than 4 out of 10 cars** on the road have been in an accident" (página lenders).
- **Subastas**: cobertura **95% de las casas de subasta de EE.UU.** (cifra recurrente) — variación: **"98.86% U.S. auction house coverage"** (página autocheck-business). **4.5M+ "exclusive auction announcements"** (la mayoría reportando daño estructural); "Exclusive Auction Announcement data for up to **2.7% of vehicles in operation**".
- **Recalls (open recall)**: **99.82% manufacturer coverage of open recall data** (blog informe rediseñado + búsqueda) — variación: **"98.96% manufacturer coverage based on vehicles in operation"** (vehicle-history-services). Ver Gaps por la discrepancia.

> Discrepancia explícita de cifras (NO resuelta): recall 99.82% vs 98.96%; auction 95% vs 98.86%. La página autocheck-business arrojó además un dato anómalo ("329 million vehicles on road with exclusive auction announcements") que **no se corrobora** en otras páginas y se marca **[A — dudoso, posible error de lectura]**.

### Scope de vehículos [V]
- **Coches de pasajeros y light trucks** matriculados en EE.UU./Norteamérica (cualquier VIN de 17 dígitos).
- **Nuevo y usado**, pero el valor está en **usado / pre-owned / CPO** (decisión de compra-venta y financiación de VO).
- **VIN decode** (year/make/model/trim) vía **ACES codes**.
- **[A]** Sin verticales no-coche tipo RV/moto/heavy-equipment como producto diferenciado (a diferencia de MarketCheck US).

---

## 3. Productos + campos atómicos

Familia AutoCheck = **historial por VIN** entregado como (a) **informe** (consumidor/dealer), (b) **score**, (c) **API de atributos** (AccuSelect), (d) **monitorización de cartera** (Triggers), (e) **informe de título federal** (NMVTIS), (f) **base de datos / market intelligence** (Vehicle Data / Elite). A continuación, el desglose atómico.

### 3.1 AutoCheck® Vehicle History Report — el informe [V]
Informe de historial por VIN (consumidor y dealer). Estructura/secciones y **campos atómicos**:

**A) Encabezado / Vehicle Snapshot**
- `VIN`, decode de **year / make / model / trim / body** (vía ACES), **vehicle class** (cohorte de comparación).

**B) AutoCheck Score℠ + Score Range** (ver §3.2).

**C) "Vehicle History at a Glance"** — checklist resumen **Problem Found / No Problem Found** para:
- `State Title Brands` (marcas de título estatales)
- `Auction-Announced Issues` (anuncios de subasta)
- `Accident / Damage events`
- `Insurance Loss or Title Transfers`
- `Odometer discrepancies`
- `Liens or theft reports`

**D) Accident Check / Damage Check** (rediseño: visualización + indicadores de severidad)
- `accident reported` (sí/no), `accident count`
- `severity` / **`Max Vehicle Severity`** (indicador de severidad)
- `point of impact` (punto de impacto)
- `airbag deployment` (despliegue de airbag)
- `auction damage announcements` (daño estructural anunciado en subasta)
- `structural / frame damage`

**E) Title Brand Check** — marcas de título (cada una check sí/no):
- `Salvage` · `Junk / Scrapped` · `Flood / Water` · `Fire` · `Hail` · `Lemon / Manufacturer Buyback` · `Rebuilt / Rebuildable` · `Grey Market`
- Marcas relacionadas con odómetro (ver F): `Not Actual Miles`, `Broken Odometer`, `Exceeds Mechanical Limits`, `Mileage Discrepancy`

**F) Odometer Check**
- `odometer readings` (secuencia de lecturas en el tiempo)
- `rollback` (retroceso), `rollover`, `tampering` (manipulación)
- `mileage discrepancy` (incoherencia en la secuencia)
- Fuente: state DMV + auction sources

**G) Vehicle Use and Event Check** — tipo de uso:
- `Personal` · `Rental` (alquiler) · `Fleet` (flota) · `Lease` (renting) · `Taxi` · `Police` · `Government` · `Commercial`
- Flags de evento: `Abandoned`, `Grey Market import`, `Lien`, `Repossessed`, `Theft / recovery`

**H) Owners / Ownership**
- `number of owners` (nº de propietarios), `current owner start date`

**I) Recalls**
- `open recall` info por VIN (cobertura 99.82% / 98.96% según fuente)

**J) Detailed / Full History (Chronological)** — log cronológico, columnas por evento:
- `event date` · `event location (state/jurisdiction)` · `event mileage` · `data source` · `event type / description`

**K) AutoCheck Buyback Protection badge** (ver §3.8) — elegibilidad mostrada en el informe.

### 3.2 AutoCheck Score℠ — score predictivo patentado [V]
"Turns in-depth AutoCheck data into a simple, powerful score." **Patentado.**
- `AutoCheck Score` = escala **1-100**.
- `AutoCheck Score Range` = banda **low-high** de scores típicos para vehículos de **misma edad y clase** (cohorte). **Clave**: el score se lee SIEMPRE junto a su range.
- `score position` = **below / within / above** el range (un 84 dentro de 73-86 supera a un 89 cuyo range esperado era 90-95).
- **Predicción**: `likelihood the vehicle will be on the road in 5 years` (probabilidad de seguir circulando a 5 años).
- `Positive Score Factors` / `Negative Score Factors` (expuestos en AccuSelect).
- Factores del modelo (declarados): `Age` (más viejo → menor score), `Mileage` (más km → menor score relativo), `Number of Owners` (más de lo típico → baja), `accidents` y "otros factores de historial" (title brands, uso). Modelo propietario; detalle completo en white paper (no expuesto públicamente — ver Gaps).

### 3.3 Auto AccuSelect™ — API REST de atributos en tiempo real [V]
"Real-time access to key vehicle history attributes through an easy-to-use API." Arquitectura **RESTful**, entrega **instantánea/programática**, **"option packs"** seleccionables (summary-level overview ↔ deep-dive detail sets). Base **900M+ vehículos**. **Campos/atributos atómicos por categoría:**

- **Ownership & Title**: `Owner Count`, `Current Owner Start Date`, `Last Title Date`, `Last Title State`, `Title Brand Check`, `Corrected Title`, `Duplicate Title`, `Last Lien Date`, `Canadian Registration`, `Grey Market Registration`, `Repossessed flag`, `Abandon flag`, `Usage flags`.
- **Registration & Usage**: `Last Registration Date`, `Last Registration State`, `Usage Types`, `Odometer Readings`, `Odometer Issues`, `Rollback Detection`.
- **Damage / Accident / Insurance**: `Accident Check`, `Accident Count`, `Max Vehicle Severity`, `Damage History`, `Insurance Loss`, `Insurance Transfer`, `Auction Announcements`.
- **Recall & Service**: `Recall Check`, `Recall Count`, `Service Count`, `Last CPO (Certified Pre-Owned) Date`.
- **Fraud & Theft**: `Theft History`, `Odometer Problems`, `Abandon / Repossessed / Grey Market flags`.
- **Scoring & Decode**: `AutoCheck Score (Low–High Range)`, `Positive Score Factors`, `Negative Score Factors`, `VIN Decode`, `ACES Codes`.

### 3.4 Auto Vehicle Data Platform / North American Vehicle Database℠ [V]
**900M+ vehículos**, **11B+ registros**. "Latest information... weeks before the competition." Categorías y campos:
- **Vehicle Registration & Title Data**: title information, registration data, **mileage readings**, key events.
- **Vehicle History**: title brand information, accident-related events, branded titles, vehicle recalls.
- **Market Data**: automotive industry statistics, market insights/trends, **VIO (Vehicles in Operation)**, **Velocity automotive statistics**.
- **Account Management Data** (para lenders): `financing changes`, `refinance events`, `title loan additions`, `payoff indicators`.
- **Custom attributes**: VIN identification & decode, pre-owned **certification** validation, inventory management data, **warranty program validation**.
- Entrega del platform: API (AccuSelect option packs) + acceso a base / batch.

### 3.5 AutoCheck Triggers — monitorización de cartera/inventario [V]
"Track vital changes to vehicle history in your portfolio or inventory." Monitoriza **20 elementos (lenders)** / **28 elementos (OEM CPO programs y lenders)** — "more than 20 different data elements". **Eventos de trigger (atómicos):**
- `change in reported accidents` · `title brand change` · `failed emissions` · `auction announcement` · `AutoCheck Buyback Protection eligibility` · `vehicle repossession` · `Certified Pre-Owned eligibility` · `portfolio analysis`.
- (También integrable con monitorización **credit-based**: negative/positive events en el perfil de crédito del cliente.)
- **Frecuencia de alerta**: `daily` / `weekly` / `monthly` / `quarterly` / **custom timetable**.
- **Salida**: notificación con **el detalle del cambio + cuándo ocurrió**. Producto comercializado también como "Automotive Loan Account Monitoring".

### 3.6 AutoCheck for Lenders — riesgo de colateral / originación [V]
Usa el historial para decisiones de préstamo de VO:
- `accident data`, `hidden damage`, `title brands`, `frame damage` (citado como causa de **pérdida de valor ≥30%**), `odometer`, `AutoCheck Score` (resumen del pasado), `value estimation / loan-to-value (LTV)` (umbral para pricing).
- Casos: originación (pre-funding risk), cartera (lifecycle), análisis comparativo vs vehículos similares.
- Complementos lender: **Automotive Credit Reporting**, **Fraud Prevention / Fraud Protect™**, customer-credit-check.
- Cobertura citada: "billions of vehicle history records", "95% of all U.S. auto auction houses".

### 3.7 NMVTIS Title Reports — informe de título federal [V]
**National Motor Vehicle Title Information System** (federal, U.S. DOJ/BJA, operado por **AAMVA**). Experian es proveedor/revendedor; informe a **$0.43** (sin mínimo, sin compromiso). **Campos NMVTIS:**
- `current state of title` + `title issue date`
- `previous titles reported by jurisdiction` (historial de títulos por estado)
- `odometer reading recorded at title issuance`
- `brand records` (junk, salvage, flood, etc. aplicadas por agencias estatales)
- `total loss records` (determinación de pérdida total por aseguradora/auto-asegurado)
- `salvage records` · `junk records`
- `insurance records`
- `theft data` (en algunos casos)
- **Fuentes NMVTIS**: state motor vehicle titling agencies + insurance carriers + salvage/junk yards (obligados a reportar mensualmente si manejan ≥5 vehículos junk/salvage/total-loss al año).
- Experian recomienda **emparejar NMVTIS + AutoCheck** (un mismo user ID/invoice/website) porque "not every title brand is negative".

### 3.8 AutoCheck Buyback Protection — garantía de recompra [V]
Garantía gratuita ligada a comprar/recibir un informe AutoCheck:
- Cubre **solo state-reported title brands** que AutoCheck no detectó y que el estado había reportado a Experian **antes** de la fecha del informe.
- Compensación: **hasta 110% del valor retail publicado por J.D. Power NADAguides** + **hasta $500 en accesorios aftermarket**.
- Duración: **1 año** de cobertura; registro dentro de **90 días** de la compra.
- **No** cubre accidentes ni registros de fuentes comerciales (solo title brands estatales).

### 3.9 AutoCheck Elite — programa dealer con market intelligence [V] (lanzado 1-feb-2012)
- **Vehicle History Reporting** (accident, odometer issues, title brands, frame damage).
- **Market Intelligence Reports**: `dealer sales performance analysis`, `vehicle registration tracking`, `consumer demographics` por mercado.
- **Competitive Analysis**: rendimiento de ventas vs competencia, `sales trends` de makes/models populares.
- **Dealer Locator Placement** (posición destacada en el buscador de dealers de AutoCheck.com).
- **AutoCheck Score** + training/marketing support (best practices, sales event guide, showroom materials).

### 3.10 Canales de integración / AutoCheck Fast Link [V]
Entrega embebida (incluida en la suscripción). **Partners nombrados:**
- **Consumer shopping sites (8)**: Autotrader, Cars.com, CarGurus, Carzing, eBay Motors, Edmunds, KBB.com, TrueCar.
- **Dealer internal systems / DMS (16)**: Auto Base, Auto/Mate, AutoSoft, CDK, DealerCenter, DealerSocket, Dealertrack, Dominion Dealer Solutions, eLead, Frazer DMS, HomeNet, Liquid Motors, Max Inventory, Reynolds & Reynolds, vAuto, VinSolutions.
- **Web providers (≈12)**: Auto One, Captive Lead, Cobalt, Dealer.com, DealerFire, Dealer HD, Dealer Inspire, DealerOn, eCarList, Ford Direct, FusionZone, MJMI, Naked Lime.
- **Mobile apps (4)**: Autoniq, Black Book, Laser Appraiser, Vin Viper.

### 3.11 AutoCheck Mobile (consumidor) [V]
App Android/iPhone (2011) para correr informes AutoCheck desde móvil.

### 3.12 Fraud Protect™ / AccuSelect fraud flags [V]
Detección de fraude: `theft history`, `odometer problems`, `abandon / repossessed / grey market flags`, inconsistencias de título.

### 3.13 (LINEAJE SEPARADO) Experian AutoCheck UK — vía One Auto API [V — flag]
Servicio "Experian AutoCheck" con datos **UK** (distinto del AutoCheck US). Campos:
- `vehicle identity / VIN confirm` · `outstanding finance` · `MIAFTR write-off` (insurer total-loss UK) · `PNC stolen status` (Police National Computer) · `previous keeper & plate-change history` · `high risk / security marker` (B2B).
- Precio (One Auto API): **PAYG £2.00 / Business £1.50 / Enterprise £1.10** por consulta.
- **No conflar con el AutoCheck US** (esquema y fuentes distintos; ver Gaps).

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = agregación de registros oficiales y comerciales por VIN** (no scraping de anuncios ni panel editorial). Se nutre de:
  - **State DMV / motor vehicle titling agencies** (título, registro, odómetro, brands).
  - **NMVTIS** (federal: título + total-loss + salvage/junk + insurance).
  - **Auction houses** (95% de EE.UU.): "exclusive auction announcements" (daño estructural, anuncios).
  - **Insurance carriers** (insurance loss / total loss / transfer).
  - **OEMs** (open recall data: 99.82%/98.96% manufacturer coverage; CPO).
  - **"Tens of thousands of distinct accident sources"** (la mayoría **exclusivas de Experian**) — police/repair/salvage/fleet/repair feeds.
  - Datos privados: salvage, fleet, repair.
- **Frecuencia**: AccuSelect **tiempo real**; informe on-demand por VIN; Triggers monitoriza en continuo y alerta daily→quarterly.
- **Métrica computada propietaria**: **AutoCheck Score** (modelo patentado de supervivencia a 5 años, comparación por edad/clase con un **Score Range** cohort-relativo) — combina age, mileage, owners, accidents, brands, uso. Es la "salsa secreta" frente a Carfax (que NO da score numérico comparativo).
- **Calidad/exclusividad**: posicionamiento en datos de **subasta y accidente exclusivos** + **score predictivo** + **garantía Buyback** como sello de confianza.
- **NMVTIS** se ofrece en paralelo porque AutoCheck (comercial) y NMVTIS (federal) cubren cosas distintas; Experian recomienda emparejarlos.

---

## 5. Entrega
- **Informe web/PDF on-demand** por VIN (autocheck.com consumidor; portal member dealer). [V]
- **App móvil** (AutoCheck Mobile, Android/iPhone). [V]
- **API REST en tiempo real** (**Auto AccuSelect™**) con "option packs" (summary ↔ deep-dive); docs developer-friendly. [V]
- **Integración en DMS / appraisal tools / inventory** (16 sistemas: CDK, Reynolds, vAuto, DealerSocket, Dealertrack, VinSolutions…) vía **AutoCheck Fast Link**. [V]
- **Embebido en marketplaces/portales** (Autotrader, Cars.com, CarGurus, KBB, Edmunds, TrueCar, eBay Motors, Carzing). [V]
- **Web providers** (Dealer.com, Dealer Inspire, DealerOn, Cobalt, Ford Direct…). [V]
- **Mobile appraisal apps** (Autoniq, Black Book, Laser Appraiser, Vin Viper). [V]
- **Alertas / feed de monitorización** (AutoCheck Triggers → notificaciones a lender/dealer/OEM). [V]
- **NMVTIS report** (mismo user ID/invoice/website que AutoCheck). [V]
- **Acceso a base / batch** (North American Vehicle Database, atributos custom, market data/VIO). [V]
- **Memberships dealer** (ilimitado o por volumen) + **Elite** (incluye market-intelligence + dealer-locator). [V]

---

## 6. Precio
**Modelo mixto: suscripción dealer (membership) + pago por informe (consumidor/volumen) + por consulta (API/NMVTIS).** [V con cifras parciales]

| Canal | Precio | Estado |
|---|---|---|
| **Informe consumidor — 1 informe** | **$24.99–$29.99** | [V — agregadores; precio de lista ronda $29.99] |
| **Pack consumidor — 25 informes / 21 días** | **$49.99** | [V] |
| **Pack — 5 informes** | **~$49.99–$59.99** | [V — variación] |
| **NMVTIS report** | **$0.43** (sin mínimo, sin compromiso) | [V — página NMVTIS new-customer] |
| **Membership dealer** | "unlimited report memberships con perks premium" / suscripción mensual para grupos pequeños; **integración incluida en la suscripción**; account manager en tiers altos | [V — sin tarifa pública] |
| **API AccuSelect / Triggers / Elite / lenders** | **No divulgado** (contacto comercial) | [V — sin precio público] |
| **Experian AutoCheck UK (One Auto API)** | PAYG **£2.00** / Business **£1.50** / Enterprise **£1.10** por consulta | [V — lineaje separado] |
| **Reventa de terceros** | informes sueltos ~$4.99–$8.50; bundles Carfax+AutoCheck ~$11–$12.75 | [V — resellers, no oficial] |

> El precio B2B (membership dealer, API, lenders, OEM) **no es público**: modelo "contacta ventas". El precio transparente es el de consumidor y el NMVTIS ($0.43).

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: para una empresa de **historial**, el orden del informe es jerárquico **score → resumen semáforo → bloques temáticos → timeline cronológico**.

### Informe AutoCheck (ficha de historial por VIN) [V]
1. **Cabecera / Vehicle Snapshot**: VIN + decode (year/make/model/trim) + **vehicle class** (cohorte).
2. **AutoCheck Score module** (arriba, prominente): cifra **1-100** + **Score Range** (banda de similares) + posición below/within/above. Es el "hero number" del informe.
3. **"Vehicle History at a Glance"** (semáforo resumen, *problem/no-problem*): title brands · auction issues · accident/damage · insurance loss/transfer · odometer · liens/theft. → vista de 2 segundos.
4. **Accident & Damage** (sección dedicada, rediseño con **visualización + severity indicators**): severidad, point of impact, airbag, auction damage announcements.
5. **Title Brand Check** (lista de brands con check): salvage/junk/flood/fire/hail/lemon/rebuilt/grey-market.
6. **Odometer Check**: secuencia de lecturas + rollback/rollover/tampering/discrepancy.
7. **Vehicle Use and Event Check**: tipo de uso (personal/rental/fleet/lease/taxi/police/government/commercial) + flags (abandoned/grey-market/lien/repossessed/theft).
8. **Owners / Recalls**: nº de propietarios, current owner start date; open recalls.
9. **Detailed / Full History (Chronological)**: tabla cronológica (date · location · mileage · data source · event detail) → "the vehicle's story".
10. **Buyback Protection badge**: sello de elegibilidad de garantía dentro del informe.

### API Auto AccuSelect (respuesta JSON) [V]
- **Option packs**: el cliente elige **summary-level** (overview: score+range, flags problem/no-problem, counts) o **deep-dive** (todos los atributos: owner count, title dates/state, accident count+severity, odometer readings, recalls, usage, CPO, fraud flags, ACES decode). → mismo dato del informe, servido como atributos discretos para incrustar en portal/CRM/appraisal.

### AutoCheck Triggers (dashboard/feed de cartera) [V]
- **No es ficha de coche**: es un **feed de alertas** sobre una cartera/inventario. Cada alerta = {elemento que cambió (accident/title brand/emissions/auction/repo/CPO/Buyback) + fecha del cambio + VIN}. Frecuencia configurable.

### AutoCheck Elite (panel dealer) [V]
- **Market Intelligence**: dealer sales performance, registration tracking, consumer demographics, competitive sales trends → panel de mercado para el dealer (no ficha de coche). + **Dealer Locator** (placement del dealer ante el comprador).

### NMVTIS report [V]
- Informe federal separado (emparejado al AutoCheck): current title state + issue date, títulos previos por jurisdicción, odómetro al título, brands, total-loss/salvage/junk/insurance.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **AutoCheck Score℠ patentado** = único score numérico **1-100 con Score Range cohort-relativo** (edad/clase) que **predice probabilidad de seguir en circulación a 5 años**. Carfax NO da un score comparativo así; es el diferencial central de producto.
- [V] **Datos de subasta exclusivos** (95%+ casas de subasta US, 4.5M+ "exclusive auction announcements" con daño estructural) + **decenas de miles de fuentes de accidente, la mayoría exclusivas de Experian** — provenance que un editor de valor no tiene.
- [V] **AutoCheck Buyback Protection** = garantía de recompra (hasta 110% del valor retail J.D. Power NADAguides + $500 accesorios, 1 año) — sello de confianza que respalda el informe con dinero.
- [V] **AutoCheck Triggers** = monitorización continua de **20-28 elementos** de historial sobre **cartera/inventario** con alertas configurables — inteligencia de riesgo dinámica para lenders/OEM, no solo informe puntual.
- [V] **Auto AccuSelect™** = API REST en tiempo real con **option packs** (summary↔deep-dive) sobre **900M+ vehículos** — integración nativa en DMS/portales/CRM.
- [V] **NMVTIS oficial a $0.43** emparejado con el informe comercial — cubre el requisito legal (p.ej. California) + el historial comercial en un mismo flujo.
- [V] **Red de integración masiva** (8 marketplaces + 16 DMS + ~12 web providers + 4 apps) bajo "Fast Link" incluida en la suscripción — distribución ubicua del informe en el punto de decisión.
- [V] **Respaldo de Experian plc** (FTSE 100, base de 250M+ individuos US, 900M+ VINs, 11B+ registros) → cruce historial-de-vehículo × datos-de-consumidor/crédito que ningún rival puro de VHR posee (credit + automotive + marketing engine).
- [V] **Capa de market intelligence dealer** (Elite: sales performance, registrations, demographics, competitive trends) — va más allá del VHR puro.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **No es valoración**: NO da `residual value %`, `retail/trade/wholesale price`, `days-to-sell`, `market days supply`, `price-to-market %`, `curva de depreciación`, `ajuste por km` como índices de valor. (Solo *referencia* el valor J.D. Power NADAguides para calcular la compensación de Buyback.) Es **provenance**, no cote.
- [V] **Metodología del Score opaca**: modelo patentado; los pesos exactos de age/mileage/owners/accidents y el cálculo del Score Range **no se publican** (remite a white paper no expuesto).
- [V] **Cobertura inconsistente en cifras**: recall **99.82% vs 98.96%**, auction **95% vs 98.86%**, dato anómalo "329M auction announcements" sin corroborar — la propia web no es consistente.
- [V] **Buyback Protection muy limitada**: SOLO state-reported title brands omitidos; **excluye accidentes** y todo registro de fuente comercial → cobertura percibida > cobertura real.
- [V] **Foco geográfico EE.UU.**: Canadá parcial (grey-market/Canadian registration); **UK es un lineaje separado** (One Auto API, MIAFTR/PNC) que no comparte esquema; sin cobertura paneuropea propia.
- [V] **Sin precio B2B público**: API/lenders/OEM/Elite = "contacta ventas" (fricción de evaluación).
- [V] **Dependencia de reporte de terceros**: la calidad del historial depende de que estados/aseguradoras/subastas reporten; brand-late o no-reportado = ausente (riesgo inherente del modelo, igual que Carfax).
- [V] **Sin TCO / running costs / SMR / catálogo de piezas-mano de obra** (no es su negocio).
- [V] **Plantilla matriz inconsistente** (22.500/32 países vs 25.200/33 países en su propia web).
- [V] **Origen/fundación del producto poco documentado públicamente** (adquisición vía Polk ~2002 = fuente única; sin fecha de fundación nítida de "AutoCheck").
- [A] **autocheck.com renderiza en JS**: el detalle fino del informe consumidor se infiere de muestras y guías de terceros (carvins/usedcargenius/cargurus) + páginas Experian; el sample report PDF no se parseó (descarga binaria).
- [A] **Sin marketplace transaccional ni motor de reprise/lead B2C** propio: monetiza el dato, no la transacción del coche.

---

## 10. Fuentes (URLs)
- https://www.experian.com/automotive/vehicle-history-services — [scope] productos (AutoCheck, AccuSelect, Triggers, NMVTIS, Fraud Protect, VIO, Velocity), fuentes de accidente "decenas de miles, exclusivas", 114M+ accident, 4.5M+ auction, recall 98.96%.
- https://www.experian.com/automotive/autocheck-business — informe dealer, secciones, auction 98.86%, structural damage 4.5M, delivery (dashboard/API/integraciones), segmentos.
- https://www.experian.com/automotive/auto-accuselect — **API AccuSelect**: catálogo atómico de atributos (ownership/title, registration/usage, damage/accident/insurance, recall/service, fraud/theft, score+factors, VIN/ACES), REST, option packs.
- https://www.experian.com/automotive/auto-vehicle-data — **900M+ vehículos, 11B+ registros**, categorías (registration/title, history, market data/VIO, account management: financing/refinance/title-loan/payoff), custom attributes, "weeks before competition".
- https://www.experian.com/automotive/autocheck-lenders — riesgo de colateral (accident, hidden damage, title, frame damage ≥30%, score, LTV), "95% auction houses", "4 of 10 cars in an accident", Automotive Credit Reporting, Fraud Prevention.
- https://www.experian.com/automotive/autocheck-integrations — Fast Link: 8 marketplaces / 16 DMS / ~12 web providers / 4 apps; "incluido en la suscripción".
- https://www.experian.com/automotive/automotive-autocheck-nmvtis y .../automotive-autocheck-nmvtis-new-customer — NMVTIS + AutoCheck (un user ID/invoice/website); **NMVTIS $0.43**; emparejar reports.
- https://www.experian.com/automotive/autocheck_score y https://www.autocheck.com/vehiclehistory/autocheck-score — Score 1-100 + Score Range (ej. 84 en 73-86 supera 89 en 90-95).
- https://www.experian.com/automotive/experian_autocheck_report — página informe/VIN check (muestras, sample PDF — JS, sin campos en texto).
- https://www.experian.com/blogs/insights/introducing-the-newly-designed-autocheck-vehicle-history-report/ — rediseño: Accident & Damage (visualización+severidad), Vehicle History at-a-Glance, Chronological Detailed History; recall **99.82%**, auction **95%**, **2.7% VIO** auction announcements.
- https://www.experian.com/blogs/insights/keeping-score/ — Score predice "on the road in 5 years", escala 1-100, comparación por edad/clase.
- https://www.experian.com/blogs/insights/what-is-autocheck-buyback-protection/ y https://www.autocheck.com/vehiclehistory/vehicle-buyback-protection (+ /buyback-terms) — garantía: 110% J.D. Power NADAguides + $500, 1 año, 90 días para registrar, solo state title brands.
- https://www.experianplc.com/newsroom/press-releases/2013/experian-automotive-launches-autocheck-triggers — Triggers: 20/28 elementos (accidents, title brands, failed emissions, auction announcements, Buyback eligibility), alertas daily/weekly/monthly/quarterly/custom.
- https://www.experian.com/automotive/auto-account-monitoring-wp — Automotive Loan Account Monitoring: portfolio analysis, repossession, CPO eligibility, credit-based triggers.
- https://www.experianplc.com/newsroom/press-releases/2012/experian-automotive-launches-autocheck-elite — Elite (1-feb-2012): VHR + market intelligence (sales performance, registrations, demographics) + competitive analysis + dealer locator; **650M+ vehículos** (2012).
- https://www.experianplc.com/newsroom/press-releases/2011/... — AutoCheck Mobile (Android/iPhone) + alianza Kelley Blue Book.
- https://www.cbinsights.com/company/experian-automotive — **HQ 475 Anton Blvd, Costa Mesa, CA 92626**; matriz Experian plc (25.200/33 países, Dublín); 250M+ individuos US.
- https://www.biia.com/experian-full-year-2024-revenue-up-8-2/ + experianplc.com FY24/FY25 — Experian plc: FTSE 100 (EXPN), Dublín; **22.500 personas / 32 países** (FY24); revenue +8% FY24.
- https://www.carvins.net/blog/carfax-vs-autocheck-2025-... — lectura de informe: secciones (Score+Range, At-a-Glance problem/no-problem, Accident/Damage point-of-impact+airbag, Title brands fire/hail/flood/junk/lemon/salvage/rebuilt + odometer brands Not-Actual-Miles/Broken/Exceeds-Mechanical-Limits/Mileage-Discrepancy, Odometer Check rollback/rollover/tampering, Use rental/fleet/lease/taxi/police/government/commercial + abandoned/grey-market/lien/repo/theft, Detailed History).
- https://vehiclehistory.bja.ojp.gov/nmvtis_understandingvhr + https://www.aamva.org/vehicles/nmvtis — definición NMVTIS: current title + issue date, previous titles por jurisdicción, odómetro al título, brands (junk/salvage/flood), total loss insurance, fuentes (DMV + insurers + salvage/junk, regla ≥5 vehículos/año).
- https://www.oneautoapi.com/service/experian-autocheck/ — **Experian AutoCheck UK** (lineaje separado): identity/VIN, outstanding finance, MIAFTR write-off, PNC stolen, keeper/plate changes, high-risk marker; PAYG £2.00 / Business £1.50 / Enterprise £1.10.
- https://www.experianplc.com/newsroom/press-releases/2008/dealers-finding-more-value-in-autocheck... — difusión del AutoCheck Score (2008).

> Verificación: identidad corporativa contrastada en ≥3 fuentes (Experian.com NMVTIS page + CB Insights + experianplc FY24/BIIA). Esquema de campos [V] leído de la página AccuSelect (atributos API uno a uno) + páginas de producto + guías de lectura de informe; Score 1-100/Range en ≥2 fuentes (autocheck_score + keeping-score + carvins). Precios [V] de NMVTIS new-customer ($0.43) + agregadores de consumo + One Auto API (UK). Discrepancias (recall 99.82 vs 98.96; auction 95 vs 98.86; plantilla 22.5k vs 25.2k; "329M" anómalo) marcadas explícitamente, NO resueltas por invención. El AutoCheck UK (One Auto API) se segrega como lineaje distinto del AutoCheck US. Subdominio "vin-history" = etiqueta taxonómica del orquestador, coherente con la naturaleza provenance/historial del producto.
