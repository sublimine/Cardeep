# Auditoría atómica — MAHINDRA FIRST CHOICE WHEELS (MFCWL)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa india de **plataforma de coche de ocasión (used auto platform)** que combina **valoración (Indian Blue Book), inspección de terceros (Autoinspekt), subastas B2B (eDiig), gestión de patios/yards (YMS/AutoYMS), contenido y leads (carandbike), DMS para concesionarios, financiación (Autofin) y retail certificado + garantía**. Es el equivalente indio del *ecosistema Cox Automotive* (Manheim + vAuto + Kelley Blue Book) — y de hecho **Cox Automotive es inversor estratégico** (nov-2015).
> Web producto: https://www.mahindrafirstchoice.com/ · IBB consumidor: https://www.indianbluebook.com/ (redirige a carandbike) · IBB dealer: https://partner.indianbluebook.com/ · Subastas: https://www.ediig.com/ · Inspección: portales `aiv2portal.autoinspekt.com` / `aiv2client.autoinspekt.com` · Patios: `client.autoyms.com` · DMS: `dms.mahindrafirstchoice.com` · Grupo: Mahindra Group.
> Fecha auditoría: 2026-06-30. Método: navegación de mahindrafirstchoice.com (home, our-business, about-us, services/{indianbluebook, autoinspekt, ediig, yms}, industry-insights, warranty, quality-process), `nslookup`/`curl` para verificación de DNS del subdominio, **recuperación de 2 informes Autoinspekt VIVOS** (`aiv2portal.autoinspekt.com/report/...` y `/old_reports/...` → esquema atómico de campos), página VIVA de eDiig (campos de lote/evento), resumen del **IBB Report FY25** (VW news), comunicado **Cox Automotive** (3 fuentes: coxautoinc + PRNewswire + Manheim press), caso de estudio **purposeintopractice.org**, prensa (Autocar Professional, Auto Components India, Business Standard, MediaNama, Motoroids) y agregadores (CB Insights, Tracxn, ZaubaCorp, PitchBook).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).
> **Nota de alcance sobre el "subdominio: wholesale-intelligence"**: **VERIFICADO que NO es un sitio web vivo.** `wholesale-intelligence.mahindrafirstchoice.com` **carece de registro A (IPv4)**; sólo resuelve por un **comodín AAAA (IPv6)** que apunta al mismo host del apex y **no sirve contenido propio** (WebFetch → ENOTFOUND; curl -4/-6 → no resuelve). No existe vhost dedicado. "Wholesale intelligence" es el **descriptor de categoría** (clasificación de Cardeep) para el **stack B2B/wholesale** de MFCWL — y es término propio de la empresa: IBB describe **YMS** como *"innovative **wholesale inventory management platform**"*, y la división Enterprise sirve el canal mayorista/remarketing (bancos, NBFC, aseguradoras, OEM, flotas). Documentado con verificación negativa, sin inventar un portal inexistente.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Mahindra First Choice Wheels (MFCWL)** | [V] |
| Categoría | **Used auto platform / ecosistema de coche de ocasión**: valoración/pricing, inspección, subasta B2B, yard management, contenido+leads, DMS, financiación, retail certificado + garantía | [V] |
| Owner / grupo | **Mahindra Group** (conglomerado, fundado 1945) | [V] |
| Entidad legal | **Mahindra First Choice Wheels Limited** · **CIN U64200MH1994PLC083996** (sociedad constituida 1994) | [V — site + ZaubaCorp] |
| HQ | **602, 6th Floor, Tower-B, Embassy 247, LBS Marg, Vikhroli (West), Mumbai 400083, India** | [V] |
| Origen operativo | Iniciada como **Auto Mart India (2003)**; **rebautizada/relanzada por Anand Mahindra en 2008** para entrar en el aftermarket/used-car | [V — caso de estudio + prensa] |
| JV original | Three-way JV: **Mahindra Group + HDFC + Sah & Sanghi** | [V — prensa] |
| Inversores | **Phi Capital** (1ª PE, 2008) · **Valiant Capital** (minoría, **$15M valorando la empresa en $265M**, mar-2015) · **Cox Automotive** (inversión **estratégica** vía compra secundaria, **25-nov-2015**; HDFC vendió su participación) | [V — Business Standard + Mahindra PR + Cox PR ×3] |
| Adquisición clave | **carandbike** (portal de contenido+clasificados) adquirido en **2020** | [V] |
| Liderazgo (2025/26) | **Mohd. Turra** — CEO & MD · **Ankit Dhanuka** — CFO · **Kingshuk Sanyal** — Chief Business Officer (Services) · **Prasad Palla** — CTO · **Shivin Tikoo** — CHRO · **Jay Rungta** — Head Retail · **Abhratanu Bhattacharya** — Head Legal | [V — about-us] |
| Tagline | "India's leading **used auto platform** business which is organizing the market by aggregating demand and supply" | [V] |
| Posición declarada | **#1** Used Car Pricing Engine · **#1** Digital Auto Auction Portal · **#1** Vehicle Inspection Business · **#1** Collection of Certified Used Cars · **#2** Auto Content Portal (carandbike) | [V — about-us] |

### Clientes objetivo [V]
Dos hemisferios:
- **B2C / Retail**: compradores y vendedores de coche usado (consumidores), tráfico de carandbike.
- **B2B / Enterprise ("wholesale intelligence")**: **bancos, NBFC (financieras no bancarias), aseguradoras, OEM, operadores de flotas, leasing, concesionarios** (franquiciados y no franquiciados). Cox lo resume: *"a suite of products that serves **dealers, consumers, financial institutions and insurance companies**"*.

### Clientes/partners nombrados [V]
**Tata Motors Finance Ltd** (solicitante en informe Autoinspekt vivo) · **IKF Finance** (vendedor en eDiig vivo) · **100+ bancos y NBFC** partners de Autoinspekt · **Cox Automotive** (inversor) · **Volkswagen India** (publica el IBB Report en su hub) · **25+ financieras** en Autofin.

---

## 2. Cobertura

### Geográfica [V]
- **India, exclusivamente.** Empresa **mono-país**; sin operación internacional propia (a diferencia de los inversores Cox/Manheim que son globales).
- **Pan-India**: **1.650 concesionarios franquiciados** en **800+ ciudades/towns** (FY25); Cox citaba **650+ outlets en ~300 ciudades** (2015) → expansión ×2,5 en red.
- **Red de patios (YMS)**: **800+ yards en 400+ ciudades**, **40M+ sq.ft** de parking, **4M+ vehículos** aparcados.
- **Puntos de contacto retail**: **1.100+**.

### Escala de datos/operación [V]
- **IBB**: **10M+ price checks/año**; acceso a **millones de transacciones diarias** por múltiples canales (retail + wholesale); **"several thousand data points"** por valoración.
- **Autoinspekt**: **280.000+ inspecciones/mes**, **7.000+ assessors/evaluadores**, **100+ bancos/NBFC** partner.
- **eDiig**: **17.000+ compradores**, **1.000.000+ (10 lakh) vehículos vendidos** desde el lanzamiento en **2011**.
- **carandbike**: **14M+ usuarios únicos** (about-us); **2M+ usuarios** del valuador (carandbike).
- **Retail**: **2,5M+ coches vendidos** hasta la fecha; **1.000+ dealers** con stock certificado.

### Scope de vehículos [V]
Multi-tipo (más amplio que un puro turismo):
- **2W** (motos/scooters), **3W** (auto-rickshaws), **4W** (turismos), **CV** (vehículos comerciales), **CE** (construction equipment / maquinaria), **farm equipment / tractores**, **taxis**.
- Nuevo y usado en pricing (IBB valora **nuevo + ocasión**); núcleo de negocio = **ocasión**.

---

## 3. Productos + campos atómicos

MFCWL es un **portafolio de productos** (no un único producto). Inventario de **10 líneas** con su lista atómica de campos. Detalle máximo en IBB (valoración), Autoinspekt (esquema de informe vivo) y eDiig (campos de lote).

### 3.1 IndianBlueBook (IBB) — motor de pricing/valoración [V]
*"India's first and most trusted used vehicle pricing engine"* — el **"Kelley Blue Book de India"**. Algoritmo propietario ML que aprende de transacciones used a través de **múltiples canales (retail + wholesale)**; **OneVahan** integrado para verificación de vehículo.

**Inputs de valoración (verificados vía carandbike/IBB):**
- **Make / Brand**, **Model**, **Variant/Trim**, **Manufacturing year**, **Registration year/month**, **Fuel type**, **Transmission**, **Kilometers driven (odometer)**, **Number of owners**, **City**, **State/RTO**, **Vehicle condition**, **Insurance status**.

**Condición (3 tiers, con definición literal IBB):**
- **Great** — *"looks new, excellent mechanical condition, needs no reconditioning"*.
- **Good** — *"free of any major defects; needs some reconditioning to be sold at retail"*.
- **Fair** — *"some mechanical/cosmetic defects, needs servicing, still in reasonable running condition"*.
(La condición se evalúa con un proceso de **140-point inspection** que alimenta el precio.)

**Outputs / campos de precio:**
- **True/Fair market value** (valor de mercado calculado del *IBB Guide* + estado del vehículo {type, age, insurance, condition} + **real-time market data**).
- **Precio ajustado por condición** (Great/Good/Fair).
- **Residual Value (RV) report** — *"Only Provider of Residual Value report"* (exclusivo declarado).
- **Used car price**, **New car price**, **Upcoming car price**, **On-Road (GST) price**, **Ex-showroom price** (vía prodibb/carandbike).
- **IBB reference/benchmark price** (precio de referencia usado en eDiig y por bancos/NBFC).
- Herramienta dealer **Price Check Premium** (`partner.indianbluebook.com/dealer/tools/price_check/premium`) con roles **Admin / Call Center / Trade Manager** (campos de salida **tras login** = GAP).

**IBB Report (inteligencia de mercado publicada, anual):** ver §3.10.

### 3.2 Autoinspekt — inspección/valoración de terceros [V]
*"India's #1 vehicle inspection business"*. Informe **imparcial de tercero** tras inspección física por ingeniero entrenado; **quality score** por ML sobre *"millions of data points"*; **OneVahan** para repo valuations; media **geo-etiquetada** (fotos/vídeos con timestamp + GPS); revisión central de calidad (AI-based quality monitoring), **low TAT**.

> **Spec canónico [V — Autocar Pro / Auto Components]: 53 parameters across 8 vehicle systems** (algunos materiales de marketing citan "140+ point" → variación temporal; se reporta el dato oficial y la variante).

**Esquema de informe — identidad del vehículo (campos atómicos, verificados en 2 informes vivos):**
- **Registration Number**, **Make/Model/Variant**, **Manufacturing Year**, **Registration date (month/year)**, **Chassis Number (VIN)**, **Engine Number**, **Fuel Type**, **Body Type**, **Transmission**, **Color**, **Odometer Reading (km)**, **Number of Tyres**, **Tyre Condition (%)** / **Tyre life (% por rueda)**, **Stock ID**, **Report ID**, **Location**.

**Estado documental/propiedad:**
- **Owner Name**, **RC Status** (RC Available), **Number of Owners**, **Hypothecation** (financiera con prenda), **Insurance Status**, **PUC Certificate**, **Keys** (condition).

**Scores por sistema (8 sistemas, escala numérica + grado textual):**
- **Exterior** (p.ej. 7/10, "Fair"; con conteo *Issues* vs *Good items*), **Interior** (8/10), **Engine & Transmission** (8/10), **Suspension**, **Steering**, **Brakes**, **Electrical**, **AC Function**, **Battery**, **Mechanical Condition**, **Accessories** (p.ej. "BAD" — detecta faltantes: music system, floor mats, toolkit).
- **Overall quality score** (p.ej. **7.9**) + **Overall rating** textual (p.ej. **"Excellent Buy"**); grados de componente: **Great/Good/Fair/Average/BAD**.
- **Structural/accident check** (p.ej. *"RH Side All Pillars: Bad — Spot welding repaired"*), **Damage Status** ("No Damage Reported"), **Accident History**.

**Valoración embebida en el informe (caso repo/finance):**
- **Base Valuation** (₹), **Refurbishment cost** (₹), **Parking cost** (₹), **Taxes** (₹), **Total Cost to Bidder** (₹).

**Media/metadata:** **12 categorías de fotos** con timestamp + GPS, vídeos, **Evaluation Date**, **Inspector/Assessor**, **Requested By** (cliente).

### 3.3 eDiig — plataforma de subastas B2B [V]
*"India's #1 online auto auction portal"* (lanzada 2011; legado **Autobid**). Online + offline.

**Formatos de subasta:** **Online** (web/app), **Yard Auctions** (stock exclusivo en red de patios), **Banquet Hall Auctions** (salones en ciudades), **True Time Bids** (live **online-offline en tiempo real**: pujar por internet en subastas físicas con feed del yard), **E-Tenders** (cotización sellada), **Negotiated Sales** (Bulk/Scrap/Accident/Yard-Exit). Tipos de precio: **Pre-Approved**, **Post-Approved**, **Reserve Price**; **Open/Closed**.

**Campos de evento/lote (verificados en plataforma viva):**
- **Location** (estado/yard), **Seller** (nombre + tipo), **Category** (CV/4W/3W/2W/CE/farm/taxi), **Auction Type** (Open/Closed), **Event Type** (**Repo** / **Insurance Salvage**), **Number of Listings**, **Event Start Time**, **Event End Time**, **Reserve/Current bid**, **Buyer fees** (descuento para registrados).
- **Inteligencia por lote**: **Autoinspekt inspection report** + **IBB price analytics** embebidos (True Time Bids "provides vehicle inspection and pricing analytics powered by Autoinspekt and Indian Blue Book").

**Vendedores:** bancos, NBFC, aseguradoras (salvage), OEM, flotas, dealers. **Vehículos:** repossessed, used, scrap, accident.

### 3.4 YMS / AutoYMS — Yard Management System [V]
*"India's largest network of vehicle storage yards"* — descrito por la propia empresa como **"innovative wholesale inventory management platform"**. **800+ yards / 400+ ciudades / 40M+ sq.ft / 4M+ vehículos**.

**Campos/funciones atómicas:**
- **Vehicle tracking & condition monitoring** (tiempo real), **storage location/slot**, **vehicle intake/exit (release)**, **Repo agent & vehicle release management**, **24/7 CCTV security**, **insurance coverage**, **on-demand refurbishment**, **logistics/vehicle movement** (manufacturing→warehouse→delivery), **pre-delivery inspection checklists**, **vehicle charging con submeter (EV)**, **periodic cleaning**, **centralized dashboard** (OEM).
- **Modelo**: pay-per-use, **sin lock-in**, **standard fees across India**, zero admin cost.

**Clientes:** bancos/financieras (repo), flotas (cold storage), OEM (storage/dispatch). Acceso: **client.autoyms.com** + apps Android/iOS.

### 3.5 carandbike — contenido, clasificados y leads [V]
*"India's #1 used car portal, and #2 auto content portal"* (adquirido 2020; **14M+ usuarios únicos**). Funciones: **listings de coche usado**, **precios de coche nuevo / on-road (GST) price**, **reviews/contenido editorial**, **valuador (IBB) embebido**, **demanda/leads** para la red retail. Es el motor de **demand-gen B2C** del ecosistema.

### 3.6 DMS — Dealer Management System [V]
**dms.mahindrafirstchoice.com** (Dealer Login + Surveyor Login). Software para la red de franquicia: **inventory management** + **CRM** + **lead management** + gestión de stock del concesionario (el caso de estudio lo describe como *"IT system for inventory management and customer relationship management"*). Roles: **Dealer**, **Surveyor**.

### 3.7 Autofin — agregación de financiación [V]
*"Aggregating Finance Offerings for Dealers & Consumers"*: **25+ financieras**, hasta **100% funding**, **EMI Calculator**. Campos: monto, plazo, tasa/EMI, oferta por financiera.

### 3.8 Garantía y certificación retail (CertiFirst / WarrantyFirst+) [V]
- **CertiFirst** — programa de certificación; coches certificados pasan **check de inspección** (homepage: *"200+ inspection point check"*; quality-process: **"118 check points"** → **variación reportada, no fusionada**).
- **WarrantyFirst Plus** — *"India's most comprehensive 2-year used car warranty"* (plan sugerido según informe de inspección).
- **Buyback Guarantee**, **AssistFirst** (Road-Side Assistance 24×7).

### 3.9 Retail used cars + Scrappage (ELV) [V]
- **Buy / Sell used cars** (multibrand certified), **EMI Calculator**.
- **"Scrap your car"** — servicio **ELV (End-of-Life Vehicle)** / desguace.

### 3.10 IBB Report — inteligencia de mercado publicada (anual) [V]
Informe sectorial **industry-first** (ediciones 1ª 2016 → 6ª 2023 → **FY24-25**). **Métricas atómicas que publica (FY25):**
- **Market size**: **5,9M unidades (FY24-25)**; **forecast 9,5M para 2030 @ 10% CAGR**.
- **SUV/compact-SUV share**: **>50%** del mercado used (desde 23% hace 4 años).
- **Age mix**: vehículos de **4-7 años = 30%** de transacciones organizadas.
- **Average selling price trend**: **+36% en 4 años**.
- **Procurement mix**: **exchange desde concesionarios de coche nuevo = 41%**.
- **Consumer behaviour**: brand loyalty **42%**; preferencia por dealer organizado **>70%**; warranty como add-on clave **66%**; **AI tools en compra 6%**; non-metro repurchase intent **68%**.
- **Residual value trends** (modelos con mayor RV → tenencia más larga + demanda aftermarket).

---

## 4. Metodología y fuentes de datos [V]
- **IBB pricing engine**: **algoritmo propietario ML** que *"continuously learns from used vehicle transactions across multiple channels"*; **"several thousand data points"**; acceso exclusivo a **millones de transacciones diarias** (retail **+ wholesale/auction** = ventaja de dato propio del ecosistema). Cálculo del valor = **IBB Guide + vehicle status (type, age, insurance, condition) + real-time market data**.
- **OneVahan**: integración con datos de registro (**VAHAN**, base oficial india) para **verificación de vehículo/RC** (registration, owners, hypothecation, RC status) — usado en valoración repo y en inspección.
- **Autoinspekt**: **inspección física** por ingeniero entrenado (**53 parámetros / 8 sistemas**) → **quality score por ML** sobre *"millions of data points"*; **media geo-etiquetada** (foto+GPS+timestamp) + **revisión central AI** de calidad.
- **Dato propio del ciclo cerrado**: el ecosistema captura precio en **subasta (eDiig)**, **inspección (Autoinspekt)**, **retail (red franquicia/DMS)** y **listados (carandbike)** → IBB se alimenta de todos esos canales (ventaja vs. un valuador puramente editorial).
- **Frecuencia**: valuador IBB **real-time/on-demand**; IBB Report **anual**; inspección **on-demand** (low TAT); subastas **eventos programados** (start/end).

---

## 5. Entrega
- **Web SaaS / portales** por producto: mahindrafirstchoice.com (retail+enterprise), **ediig.com** (subastas), **indianbluebook.com / carandbike.com** (valuador consumidor), **partner.indianbluebook.com** (dealer Price Check; roles Admin/Call Center/Trade Manager), **aiv2portal/aiv2client.autoinspekt.com** (inspección), **client.autoyms.com** (yards), **dms.mahindrafirstchoice.com** (Dealer/Surveyor login). [V]
- **Apps móviles**: **eDiig now** (Google Play), **Autoinspekt App** (Android, v2.0/v1.17), **AutoYMS** (Android/iOS). [V]
- **API / enterprise integration**: IBB para **"massive enterprise clients running thousands of price checks"** (banca/NBFC/aseguradoras). [V — existencia; esquema/auth/rate-limits = GAP, no público]
- **Informes**: **PDF de inspección** (Autoinspekt, con valoración y media), **IBB Report anual** (descarga), informe de **Residual Value**. [V]
- **Servicios físicos**: red de **patios/yards**, refurbishment, logística, retail certificado, ELV/scrappage. [V]

---

## 6. Precio
- **No público** (sin tarifa en web; todo vía contacto/enterprise). [V]
- Modelos descubribles:
  - **Autoinspekt**: ~**US$10/inspección** (caso de estudio purposeintopractice). [V — caso de estudio; tarifa actual = GAP]
  - **YMS**: **pay-per-use**, **sin lock-in**, **standard fees across India**, zero admin cost. [V]
  - **eDiig**: **buyer fees por vehículo** (con descuento a compradores registrados); doc de fees publicado por evento. [V — existencia; importes = GAP]
  - **IBB**: **price check** por uso + **suscripción/contrato enterprise** (banca/NBFC/OEM); valuador consumidor **gratuito**. [A modelo; importes = GAP]
  - **Warranty/Retail**: planes de garantía (precio por plan), financiación vía Autofin. [V existencia]
- **Importes concretos = GAP** (no descubribles públicamente).

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. El ecosistema MFCWL coloca cada dato en una **pantalla distinta según el rol** (consumidor / dealer / comprador de subasta / financiera). Mapeo pantalla → dato [V salvo marca].

### Valuador IBB / carandbike (consumidor) [V]
- **Flujo de inputs en pasos**: brand → model → variant → year → fuel/transmission → km → city/state → owner/condition.
- **Resultado**: **valor de mercado / precio** + (selección de condición **Great/Good/Fair** ajusta el precio). FAQ *"How is the vehicle price decided"* explica el método in-line.

### Informe Autoinspekt (PDF/portal) [V]
- **Cabecera de identidad**: matrícula, make/model/variant, año, chasis (VIN), motor, fuel, body, color, km, nº tyres, owners, hypothecation, RC/PUC/insurance/keys.
- **Bloque de scores por sistema**: tarjetas **Exterior / Interior / Engine&Transmission / Suspension / Steering / Brakes / Electrical / AC / Battery / Accessories** con **score numérico (x/10)** + **grado** + conteo *Issues/Good items*.
- **Score global** destacado (p.ej. **7.9 — "Excellent Buy"**) + **Damage/Accident/Structural** check.
- **Bloque de valoración** (repo/finance): Base Valuation, Refurbishment, Parking, Taxes, **Total Cost to Bidder**.
- **Galería**: **12 categorías de fotos** geo-etiquetadas + vídeos.

### eDiig — listado de eventos y ficha de lote [V]
- **Lista de eventos** con facetas/filtros: **Location, Seller, Category, Auction Type, Event Type, Nº Listings, Start/End**.
- **Ficha de lote** (catálogo): identidad del vehículo + **informe Autoinspekt** + **precio de referencia IBB** + reserve/current bid + buyer fees.

### IBB dealer Price Check Premium (partner portal) [V — existencia; campos tras login = GAP]
- Tras login (Admin/Call Center/**Trade Manager**): consulta de precio para el dealer (fair/trade/retail = no verificable sin credenciales).

### YMS — dashboard de patios [V]
- **Dashboard centralizado** (OEM/financiera): inventario por yard, ubicación/slot, condición, intake/exit, repo release, refurb/logística, charging submeter.

### IBB Report — documento de mercado [V]
- **Narrativa + estadística**: market size/forecast, SUV share, age mix, ASP trend, procurement mix, consumer behaviour, RV trends.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Ecosistema integrado "Cox-style" en un solo país (India)**: **valoración (IBB) + inspección (Autoinspekt) + subasta B2B (eDiig) + yard management (YMS) + contenido/leads (carandbike) + DMS + financiación (Autofin) + retail/garantía** bajo un mismo techo. Equivalente indio de Manheim+vAuto+KBB+AutoTrader — y con **Cox Automotive como inversor estratégico** (sinergia de know-how).
- [V] **Dato propio de ciclo cerrado**: IBB se alimenta de transacciones reales de **sus propios** canales retail **y wholesale/auction** → pricing observado, no editorial.
- [V] **"Only Provider of Residual Value report"** en India (RV report exclusivo declarado).
- [V] **True Time Bids**: subasta **live online-offline en tiempo real** con **inspección + pricing analytics embebidos por lote** (Autoinspekt + IBB) — inteligencia accionable en el punto de puja.
- [V] **Mayor red de inspección y de patios de India**: 7.000+ assessors, 280k+ inspecciones/mes; 800+ yards / 4M+ vehículos ("wholesale inventory management platform").
- [V] **IBB = estándar de pricing de India** ("industry-first", el "Kelley Blue Book indio"), usado por **bancos/NBFC** para LTV y por aseguradoras.
- [V] **OneVahan/VAHAN integration** (dato oficial de registro: owners, hypothecation, RC status) — provenance regulatoria que un valuador puro no tiene.
- [V] **Multi-tipo de vehículo** (2W/3W/4W/CV/CE/farm/tractor/taxi), no sólo turismo.
- [V] **IBB Report** anual = autoridad de mercado (market size, forecasts, mix) citada por OEM (VW lo publica).

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **NO es un sitio "wholesale-intelligence"**: ese subdominio **no existe como web** (sin registro A; comodín AAAA sin vhost). Es descriptor de categoría, no un portal.
- [V] **Mono-país (India)**: sin cobertura ni datos internacionales (a diferencia de Cox/Manheim globales o INDICATA pan-EU).
- [V] **Precio no público**: sin tarifas; importes de IBB/Autoinspekt/eDiig/YMS = GAP.
- [V] **Sin documentación técnica de API pública**: existe acceso enterprise a IBB, pero **no hay esquema JSON, auth, rate-limits ni diccionario de campos** publicado.
- [V] **Campos del Price Check dealer tras login** (fair/trade/retail/wholesale por separado = no verificable sin credenciales).
- [V] **Variación de cifras de inspección sin reconciliar públicamente**: **53 params/8 sistemas** (Autoinspekt oficial) vs "140+ point" (marketing) vs retail **"200+"** vs **"118"** check points (CertiFirst). Reportado, no fusionado.
- [A] **Sin KPIs de mercado tipo INDICATA expuestos al usuario** (Market Days Supply, Price-to-Market %, Stock Turn, Days-to-Sell como índices nombrados): IBB da **precio** y el **IBB Report** da agregados, pero no un dashboard de market-intelligence operativo público para repricing diario.
- [A] **Sin VIN-decode-to-spec como producto** (identifica por make/model/variant + chasis/RC, no un descodificador de VIN a equipamiento tipo DataOne/JATO).
- [A] **Sin informe de historial/fraude de km/siniestros certificado al estilo Carfax/CARFAX**: la provenance proviene de **OneVahan (RC)** + **inspección física**, no un historial multi-fuente por VIN.
- [A] **Sin SMR / tiempos de mano de obra / catálogo de piezas** (no es Audatex/GT Motive): da coste de refurbishment estimado en el informe, no catálogo de reparación.
- [A] **Sin inteligencia EV granular** (kWh, química de celda, SoH); YMS sólo trackea carga por submeter.
- [A] **carandbike output labels** del valuador (rango/condición exactos) tras render JS — capturados parcialmente; el set completo de etiquetas de salida no se renderizó en HTML estático.

---

## 10. Fuentes (URLs)
- https://www.mahindrafirstchoice.com/ — home: productos, "200+ inspection point check", nav, dealer/surveyor login, helpline. [V]
- https://www.mahindrafirstchoice.com/our-business — 8 líneas de negocio + descripciones, carandbike #1/#2, Autofin, WarrantyFirst Plus, IBB "pricing engine". [V]
- https://www.mahindrafirstchoice.com/about-us — identidad, liderazgo, escala (800+ yards, 1.100+ touchpoints, 14M+ users, 17.000+ buyers, 2,5M+ cars), posiciones #1/#2. [V]
- https://www.mahindrafirstchoice.com/services/indianbluebook — IBB: ML engine, thousands of data points, OneVahan, "Only Provider of Residual Value report", 10M+ checks, vehicle types. [V]
- https://www.mahindrafirstchoice.com/services/autoinspekt — 280k+ inspecciones/mes, 7.000+ assessors, 100+ bancos/NBFC, OneVahan, geo-tagged media, low TAT, portales. [V]
- https://www.mahindrafirstchoice.com/services/ediig — formatos (Online/Yard/Banquet, Pre/Post-Approved/Reserve, E-Tenders, Negotiated), 17.000+ buyers, 1M+ vendidos, categorías 2W/3W/4W/taxi/farm/CE. [V]
- https://www.mahindrafirstchoice.com/services/yms — 800+ yards/400+ ciudades/40M sq.ft/4M+ vehículos, features, pay-per-use, client.autoyms.com. [V]
- https://www.mahindrafirstchoice.com/industry-insights — ediciones del IBB Report (2016 1ª → 2024-25). [V]
- https://www.mahindrafirstchoice.com/quality-process — CertiFirst/WarrantyFirst, **118 check points**. [V]
- https://www.ediig.com/ — **plataforma viva**: campos de evento/lote (Location, Seller {IKF Finance, Insurance Salvage}, Category CV/4W/CE/2W/3W, Auction Type Open/Closed, Event Type Repo/Insurance Salvage, Listings, Start/End). [V]
- https://aiv2portal.autoinspekt.com/report/view/MTg4MzQ5NA==/Q1ZSUE8xODgzNDk0 — **informe Autoinspekt vivo (CVRPO1883494)**: esquema atómico (identidad + scores por sistema + valoración: Base ₹916.300, Total to Bidder ₹232.000, parking/taxes/refurb; requested by Tata Motors Finance). [V]
- https://aiv2portal.autoinspekt.com/old_reports/report/viewpdfreport/MjkzODY4NDQ4/ZW5jb2RlZF9pZA== — **informe vivo (4WRTL293868448, Hyundai Santro)**: Stock ID, scores Exterior 7/10 / Interior 8/10 / Engine&Tx 8/10 / Overall 7.9 "Excellent Buy", 12 categorías de fotos GPS, structural "RH pillars Bad / spot welding". [V]
- https://www.indianbluebook.com/ → redirige a https://www.carandbike.com/used/car-valuation-price-calculator — valuador (inputs city/owner/km/transmission/variant/state/fuel; condición Great/Good/Fair). [V]
- http://www.indianbluebook.com/blog1/how-and-why-you-should-rely-on-ibb-used-car-valuation-guide — definiciones Great/Good/Fair + 140-point inspection. [V]
- https://partner.indianbluebook.com/dealer/tools/price_check/premium — **dealer Price Check Premium** (login Admin/Call Center/Trade Manager; campos tras auth = GAP). [V]
- https://www.volkswagen.co.in/.../india-used-car-market-races-past-5-9-million...-ibb-report-fy-25 — **métricas IBB Report FY25**: 5,9M→9,5M@10% CAGR, SUV>50%, 4-7yr=30%, ASP +36%, exchange 41%, loyalty 42%, organized >70%, warranty 66%, AI 6%, non-metro 68%. [V]
- https://www.coxautoinc.com/insights/cox-automotive-announces-strategic-investment-mahindra-first-choice-wheels/ — **Cox**: inversión estratégica 25-nov-2015, 650+ outlets/~300 ciudades, businesses (IBB "first and only used car pricing guide", eDiig, Autoinspekt), rationale. [V]
- https://press.manheim.com/2015-11-25-Cox-Automotive-Announces-Strategic-Investment-In-Indias-Mahindra-First-Choice-Wheels y https://www.prnewswire.com/news-releases/...-300184467.html — 2ª/3ª fuente del comunicado Cox. [V]
- https://www.business-standard.com/article/companies/hdfc-sells-mahindra-first-choice-stake-to-cox-automotive-115112400870_1.html — HDFC vende a Cox (403 al fetch; titular indexado). [V titular]
- https://www.business-standard.com/article/companies/mahindra-first-choice-sells-stake-to-pe-company-115032000494_1.html y PE Hub — **Valiant Capital $15M @ $265M** (mar-2015), Phi Capital (2008). [V]
- https://autocomponentsindia.com/mahindra-first-choice-wheels-launchestruetimebids/ y https://www.autocarpro.in/news-national/mahindra-choice-launches-online-offline-vehicle-auction-platform-22269 — **True Time Bids** + **Autoinspekt 53 parameters/8 systems** + IBB analytics por lote. [V]
- https://purposeintopractice.org/mahindra-first-choice-orchestrating-the-usedcars-ecosystem — caso de estudio: fundación 2008, inspección ~US$10, DMS (inventory+CRM), IBB "industry's first valuation guide", B2B auction de repo, supply-chain software, diagnosis system. [V]
- https://www.medianama.com/2014/06/223-mahindra-first-choice-online-auctions-autoinspekt/ y Motoroids — Autobid (1 lakh vendidos), lanzamiento Autoinspekt. [V]
- https://www.zaubacorp.com/company/.../U64200MH1994PLC083996 — CIN/constitución 1994. [V]
- Verificación negativa DNS: `nslookup wholesale-intelligence.mahindrafirstchoice.com` → sólo AAAA comodín (= IPv6 del apex), **sin A**; `curl -4/-6` → no resuelve; WebFetch → ENOTFOUND. → **subdominio no servido**. [V]

> Verificación: identidad/inversores/escala con **≥2-3 fuentes** (site + Cox PR ×3 + Business Standard + PitchBook/Tracxn). Esquema atómico de Autoinspekt **[V] leído de 2 informes vivos**; campos de eDiig **[V] de plataforma viva**; IBB inputs/condición **[V]**; métricas IBB Report FY25 **[V]**. Cifras de inspección con variación (53/140+/200+/118) **reportadas sin fusionar**. Precio, esquema de API y campos del Price Check dealer = **GAP** (no público / tras login), marcados, **jamás inventados**.
