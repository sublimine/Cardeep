# Autorola — Auditoría atómica de inteligencia competitiva

> **Slug:** `autorola` · **Categoría cardeep (subdominio):** `wholesale-intelligence` (B2B remarketing/subasta + inteligencia de mayorista) · **Web:** https://www.autorola.com/ (selector país → 25 sitios `autorola.<cc>`) · **Grupo:** https://www.autorolagroup.com/ · **Solutions:** https://autorolasolutions.com/ · **BI hermana:** https://indicata.com/
> **Auditoría:** 2026-06-30. **Método:** navegación de autorolagroup.com (vehicle-auctions, vehicle-inspections, compound-services, fleet-monitor, contact), autorolasolutions.com (digital-ecosystem + 4 product pages), indicata.com/fleet-remarketers, artículo **PwC "Autorola's Digital Revolution"** (identidad/escala/financieros), prensa (Fleet Europe, Fleet World, Motor Finance, Business Car) y **renderizado Playwright en VIVO** del marketplace `autorola.co.uk` (home, /auctions, auction 673301, /pricing) → campos de listado reales + **tarifas públicas**.
> **Convención:** **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (siempre marcado).
> **Nota de alcance / subdominio:** `wholesale-intelligence` es la **etiqueta de categoría interna de cardeep** (agrupa a Autorola con Manheim, ACV, OPENLANE, BCA, AUTO1, USS…), **no un subdominio DNS real**. Verificado: el host `wholesale-intelligence.autorola.com` resuelve por **DNS wildcard** (comparte rango IP con `*.autorola.com`) pero **no es un portal de producto** independiente. Esta auditoría cubre la **unidad Autorola Marketplace** (subasta/remarketing B2B) + **Autorola Solutions** (workflow/defleet) + la **inteligencia de mayorista** que el grupo expone vía INDICATA. **INDICATA tiene auditoría propia** (`indicata.md`); aquí se referencia sin duplicar, salvo los KPIs de *fleet remarketing* que son el núcleo "wholesale-intelligence".

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Autorola** (grupo: **Autorola Group**) | [V] |
| Categoría | **Remarketing de vehículos online B2B + IT/automatización de fleet management + business intelligence de VO**. Autodefinición: "Your global online vehicle remarketing **and business intelligence** partner" / "leader in online remarketing and automotive IT solutions for professional used car and fleet management" | [V — autorola.com/footer] |
| Estructura | **3 unidades de negocio**: (1) **Autorola Marketplace** (subasta/remarketing online B2B), (2) **Autorola Solutions** (software de workflow/defleet, IT a medida), (3) **INDICATA** (BI & market intelligence de VO) | [V — PwC + group] |
| Owner / propiedad | **Peter Grøftehauge = propietario único desde diciembre 2023** (compró la parte de su hermano Martin) | [V — PwC] |
| HQ | **Skibhusvej 52A, DK-5000 Odense C, Dinamarca** | [V — contact page] |
| Fundación | **1996** por los hermanos **Peter y Martin Grøftehauge**; plataforma de subastas online lanzada **1998**; "over 20 years of experience in online vehicle remarketing" | [V — PwC + vehicle-auctions] |
| Empleados (grupo) | **"over 700 employees globally"** | [V — PwC] |
| Países (grupo) | **19 países en 5 continentes** (PwC); **25 sitios de marketplace** localizados (ver Cobertura) | [V — PwC + selector país en vivo] |
| Escala marketplace | **"over 70,000 active buyers"** (dealers profesionales) | [V — múltiples páginas] |
| Facturación grupo (2024) | **> 1.000M DKK** (~€134M) ingresos; **83M DKK** beneficio; objetivo **+20% anual** durante 4 años (~100 contrataciones/año) | [V — PwC] |
| Tel / email (grupo) | **(+45) 70 20 16 61** · **kundecenter@autocom.dk** (raíz danesa Autocom/Bilpriser); soporte US **+1 678 366 4639**, **customercenter@autorola.com** | [V] |
| Tel UK marketplace | **01625 507000** (Macclesfield/Northampton ops) | [V — autorola.co.uk] |
| Liderazgo (BUs) | **Ib Kimose** — Global BU Director **Autorola Solutions** · **Andy Shields** — Global BU Director **INDICATA** · **Philip Browne** — MD Autorola Australia (eRepair) | [V — prensa] |
| Pila técnica | Marketplace web SaaS (React/SPA, `autorola.<cc>` + `m.autorola.<cc>` móviles); Solutions = SaaS cloud con SSO/RBAC; apps de inspección responsive Android/iOS | [V — render en vivo + solutions] |

### Posicionamiento [V]
Autorola = **brazo transaccional + operativo** del ecosistema (INDICATA es el brazo de datos). El "sweet spot" del grupo: combinar **market intelligence (INDICATA) + subasta B2B (Marketplace) + de-fleet/inspección/reparación (Solutions)** bajo un mismo dueño → workflow de VO de extremo a extremo (de-fleet → inspección → valoración → canal/país óptimo → subasta → entrega).

### Clientes objetivo (segmentos con página propia) [V]
**Leasing / Subscription / Fleets · Dealers & Dealer Groups · Manufacturers (OEM/NSC) · Service & Logistics Providers · Banks & Financial Institutions · Rental companies · Insurance.**

### Clientes / vendedores nombrados [V]
**Leasing/fleet:** Alphabet (Austria, Belgium), **Ayvens / ALD Automotive** (Italia, Luxemburgo AXUS), **Arval**, **Allane**, **Leasys**, **MHC Mobility** (Polonia), **Post Company Car** (Suiza). **Rental:** **Sixt** (Australia + Fleet Monitor 10 años Kia AT), **Enterprise** (Turquía multi-site + eRepair), **Hertz**, **East Coast Car Rentals**. **Seguros:** **AXA**, **Vittoria**. **OEM:** **BMW** (deal paneuropeo de remarketing), **Volvo**, **KIA** (Austria, 10 años Fleet Monitor; auctions UK KIA), **Mazda**, **Aston Martin** (eAuction UK). [V — render + prensa]

---

## 2. Cobertura

### Geográfica [V]
- **25 sitios de marketplace** localizados (selector país en vivo): **Dinamarca, Alemania, Países Bajos, Polonia, Suecia, Noruega, Luxemburgo, Italia, Australia, Portugal, Hungría, Eslovaquia, Estados Unidos, Turquía, Brasil, Reino Unido, Nueva Zelanda, México, Finlandia, España, Austria, Bélgica, Suiza, Chequia, Francia.**
- Página de contacto lista además **EAU (UAE)** como oficina → presencia operativa en Oriente Medio (Autorola Gulf).
- **Grupo:** "19 países en 5 continentes" (PwC). El número de *sitios* (25) > *países con oficina* (19) por sitios multi-vendedor.
- Auctions **"in any country and any language"**: subastas paneuropeas y cross-border; white-label por vendedor.

### Scope de vehículos [V/A]
- **Núcleo = vehículo de ocasión (VO) turismo** ex-fleet/leasing/OEM/rental. [V]
- **Vehículo comercial / LCV**: sí — "Autorola Daily Auction - **Commercial Vehicles**" en UK. [V]
- **Vehículos accidentados / no rodantes**: sí — sitio FR "Enchère - **Véhicules accidentés et non roulants**" (salvage/seguros). [V]
- **EV**: sí, categoría propia (filtro fuel + tarifa transporte "Electric road driven"). [V]
- **Premium/exclusivo**: "Exclusive car selection" (DE), Aston Martin eAuction (UK). [V]
- **No** se evidencian motos ni camión pesado como categorías destacadas. [A]

### Escala de transacción [V/A]
- **"over 70,000 active buyers"** (grupo); **"over 2,000 active dealers"** (UK). [V]
- **~200.000 vehículos/año** vía subastas de 24h. [A — reportado por agregador de búsqueda, no confirmado en fuente primaria]
- INDICATA (dato de mayorista): hasta **15M coches/día** analizados por image recognition; **6M VO** vivos en plataforma; tracking de **140.000 dealers** franquiciados y no-franquiciados. [V — PwC + indicata]

---

## 3. Productos + campos atómicos

> Autorola comercializa por unidad: **Marketplace** (Vehicle Auctions, Vehicle Inspections, Compound Services) · **Solutions** (Fleet Monitor + módulos, TradeIn, IHS, Digital Showroom, eRepair, Fleet Services) · **INDICATA** (BI; auditada aparte — aquí solo el set de *remarketing wholesale intelligence*). Los campos de listado son **verificados en vivo** en autorola.co.uk; los de inspección/solutions, de las páginas de producto.

### 3.1 Autorola Marketplace — Vehicle Auctions (plataforma core de remarketing B2B) [V]
Subasta online B2B donde **vendedores profesionales** (fleet/leasing/OEM/banco/rental/seguro) venden a **dealers aprobados**.

**Formatos de subasta (todos nombrados):**
- **Open auction** (puja abierta).
- **Closed auction / Tender — Sealed/Closed bids** (tender de pujas ocultas).
- **Buy Now / Buy-It-Now** (compra inmediata a precio fijo).
- **Bid or Buy-Now Auction** (híbrido pujar-o-comprar-ya).
- **Live eAuction** (subasta en vivo) y **24-hour-a-day auction** (cronológica 24h).
- **White-label auction** (subasta con marca del vendedor: "Alphabet Austria", "Ayvens", "Premium Leasing", etc.).
- Configurable **"in any country and any language"**.

**Campos por vehículo — tarjeta de listado (search results) [V, render en vivo]:**
- **Make** (marca) · **Model** (modelo) · **Versión/trim** (descripción completa: p.ej. "2.0 e-Skyactiv G MHEV Sport Lux 5dr Auto").
- **Body type** (Hatchback / Estate / SUV / Commercial).
- **Fuel type** (Petrol/Diesel/Hybrid/Electric…).
- **Power en kW** (p.ej. "90 kW").
- **Nº de puertas** ("5d").
- **Transmission** (Auto / Manual / "6Spd" / Other).
- **First registered** (fecha 1ª matriculación MM/AAAA, p.ej. "02/2023").
- **Mileage** (kilometraje, p.ej. "17,735 miles").
- **Location** (ciudad/sede del vehículo, p.ej. "Northampton").
- **Current bid / price** (puja actual, "£ 14,400").
- **Time remaining / End time** (cuenta atrás, "6 h 20 m").
- **Auction/sale name** (nombre de la venta) · **Country** (país vendedor, "UK/AT/BE…").

**Filtros del Stock Locator / búsqueda [V, render en vivo]:**
- **Make · Model · First registered (rango año) · Mileage (rango) · Fuel type · Country · Sales type(s) · Price category · VAT status**.
- **Search Agent** (búsqueda guardada con notificaciones) · **Favourites** (favoritos).

**Campos de pricing por vehículo (fijados por el vendedor) [V]:**
- **Reserve price** (precio de reserva — oculto al pujador; "You set the reserve price").
- **Start price** (precio de salida).
- **Buy-It-Now price** (precio de compra inmediata).
- **VAT status / Price category** (margen vs IVA-deducible; "Danish Cars Tax-free" para export).

**Campos detalle de vehículo (ficha completa) — [A/GAP de acceso]:** VIN, lista de equipamiento, **condition report / inspection report** completo, daños, nº de llaves, historial de servicio, número de fotos → **tras login de "approved dealer"** (la ficha `/enrollment/{id}` exige aprobación). No accesible públicamente.

### 3.2 Autorola Marketplace — Vehicle Inspections (VIS) [V]
**VIS = Vehicle Inspection System**: herramienta profesional de inspección, **responsive web app (Android/iOS + desktop)**, **altamente configurable** (de handover/return receipts y pre-delivery hasta inspección profesional completa). Campos/datos capturados:
- **VIN** · **Mileage** (lectura odómetro).
- **Damage**: ubicación / tipo / severidad del daño.
- **Tyre condition** (estado de neumáticos).
- **Mechanical / technical condition** (evaluación mecánica).
- **High-quality photos** (fotos por punto).
- **Condition grade / report** según "leading industry standards" (proceso modular paso a paso).
- **Equipamiento / descripción** del vehículo.
- **Integración real-time con Fleet Monitor** + **traducible a todas las subastas Autorola** (nacional/internacional) → el report alimenta directamente el listado.

### 3.3 Autorola Marketplace — Compound Services [V]
Servicios físicos de campa en cada mercado local para clientes fleet:
- **Vehicle collection & delivery** (recogida/entrega/transporte).
- **Inspection** (inspección en campa).
- **Refurbishment** (reacondicionamiento).
- **Storage** (almacenamiento).
- **Real-time management information**: estado y **ubicación** de cada vehículo (status + location MI). Clientes: bancos, contract-hire/leasing, OEM, dealers franquiciados/independientes, rental.

### 3.4 Wholesale / Remarketing Intelligence (set de decisión "wholesale-intelligence", motor INDICATA) [V]
El núcleo de la categoría: los datos que Autorola pone al remarketer para **maximizar retorno y minimizar días de stock**. Campos/métricas:
- **Geo Pricing** — precio del mismo vehículo **por país/geografía** → decide en qué mercado vender. [V]
- **Export Index** — índice de **atractivo de exportación / cross-border** del vehículo (cuándo y a dónde exportar). [V]
- **European Target Price** — **precio objetivo europeo** de referencia para fijar precios. [V]
- **Marketability Score** — **puntuación de comerciabilidad** (probabilidad/velocidad de venta) combinada con la valoración. [V]
- **Start pricing / Reserve pricing / Buy-it-now** recomendados (datos para fijar cada uno). [V]
- **Best sale route / channel decisioning** — canal y país óptimo de disposición por vehículo. [V]
- **Days-to-sell / reduce stocking days** — optimización de tiempo en stock. [V]
- **Demand / Supply** (live, por mercado) · **Live market value** (retail & trade). [V]
- **Dealer performance / stock / sales** sobre **140.000 dealers** → a qué dealer remarketar cada coche. [V]
- **Market trend analysis** diario (stock & sales activity). [V]
> Detalle completo de KPIs INDICATA (Market Days Supply, Price-to-Market %, Stock Turn, Inventory Age, etc.) en `indicata.md`.

### 3.5 Autorola Solutions — Fleet Monitor (plataforma core de workflow/asset management) [V]
"One Platform solution to fleet management": controla el ciclo **in-fleet → de-fleet** ("from acquisition to disposal") para optimizar lead-times y beneficio. **Dashboards configurables en tiempo real.**

**Gateways de ciclo de vida rastreados (cada vehículo los atraviesa):** **arrival · handover to drivers · return · inspection · sales** (+ call-back de coches en circulación, return inspections, sales preparation, online listing). [V]

**Módulos nombrados:**
- **Business Partner Module** — integra proveedores/partners externos con acceso individual restringido (RBAC granular). [V]
- **Service Module** — gestiona todos los servicios que un proveedor de fleet realiza para distintos fleet owners; soporta **acuerdos diversos + facturación**. [V]
- **Order Module** — colaboración estructurada con proveedores: **tracking de órdenes + lead-time** por gateway. [V]
- **Booking Module** — agenda de **inspecciones, mantenimiento y servicios** con **calendario en tiempo real** y asignación de recursos multi-sede. [V]
- **Fleet Chat** — **chat en vivo por vehículo** (mensajería específica de cada coche). [V]

**Datos gestionados:** servicing (mantenimiento), **registrations** (proceso de matriculación), **inspections**, **recalls** (campañas), **repossession stock management** (gestión de stock embargado), comunicación con proveedores, **document/certificate upload**, **receipt document generation**, **lead-time measurement** (medición/optimización continua). [V]

### 3.6 Autorola Solutions — TradeIn Solution [V]
App que cubre **todo el trade-in en 30 minutos**. Flujo: (1) **Inspección** con Inspection Helper → (2) **valoración de mercado en tiempo real** (real-time market valuations) → (3) **comunicación de precio + tracking** al cliente → (4) gestión completa del proceso. Entrega valoración "justa y precisa" al cliente. [V]

### 3.7 Autorola Solutions — Inspection Helper System (IHS) [V]
App de inspección "on the go" para partners (internos/externos), responsive Android/iOS, configurable por tipo (handover/return receipts, pre-delivery, profesional completa). Captura: **VIN, mileage, damage (location/type/severity), tyres, mechanical, high-quality photos, condition report**; **integración real-time con Fleet Monitor**. [V] (Variante operativa del VIS de Marketplace.)

### 3.8 Autorola Solutions — Digital Showroom [V]
Escaparate online integrado con Fleet Monitor para que el vendedor exponga su stock a compradores: **browse / search / select / add to favourites / buy online**; muestra **descripciones detalladas + fotos de alta calidad**; permite **definir estrategias de venta por grupo de compradores** y gestionar product mix. "State-of-the-art window to your entire stock." [V]

### 3.9 Autorola Solutions — eRepair (2.0) [V]
Plataforma de **gestión de reparación de vehículos / claims management** (líder en rental AU/EU). Procesa **6.000 reparaciones/mes**; **~50.000 vehículos rental** activos. Clientes: Enterprise, Sixt, Hertz, East Coast Car Rentals (con sus cadenas de suministro integradas). eRepair 2.0 mejora **customización, automatización, integración de terceros** y da **visibilidad completa del proceso de reparación**. [V]

### 3.10 Autorola Solutions — Fleet Services (Compound Management, defleet/infleet) [V]
Nueva propuesta SaaS (tras 1,5 años de inversión) que lleva al cloud la gestión de **red de campas** (modernizada de la red de Autorola Dinamarca): in-fleet, de-fleet, **lead time management**, control de proveedores de servicio/logística, **auditabilidad**. [V]

---

## 4. Metodología y fuentes de datos [V]
- **Marketplace:** datos **transaccionales reales** de subasta (pujas, precios alcanzados, reserva/salida/buy-now, comerciabilidad observada) + **inspección física estandarizada** (VIS/IHS) → condition report que viaja con el listado, traducible a todas las subastas.
- **Wholesale intelligence (INDICATA):** valor **100% de mercado observado** — "collects, processes and analyses **live used car market data**" (demand, supply, pricing, inventories); escanea **classifieds online + webs de fabricantes/dealers franquiciados + retailers independientes**; **image recognition** lee hasta **15M coches/día**; **IA propia desde 2014**. Tracking continuo de **140.000 dealers**. Métodos estandarizados cross-market.
- **Solutions:** datos **operativos de proceso** (gateways, lead-times, órdenes, bookings, repairs) en tiempo real, integrados vía interfaz real-time entre VIS/IHS ↔ Fleet Monitor ↔ Marketplace.
- **Sinergia de grupo:** el dato de INDICATA (dónde/cuándo/a-quién vender) alimenta la decisión de canal/país en el Marketplace; Solutions ejecuta el workflow físico. Ecosistema cerrado de-fleet→venta.
- **Frecuencia:** marketplace **live/diario** (subastas 24h); INDICATA **live/diario** (intel) + **mensual** (Market Watch); Solutions **real-time**.

---

## 5. Entrega
- **Marketplace web SaaS:** `autorola.<cc>` (desktop SPA) + `m.autorola.<cc>` (móvil) en 25 mercados; multi-idioma; subastas white-label. [V]
- **Apps de inspección:** VIS / IHS — **responsive web app Android/iOS + desktop**, offline-capable, integradas real-time a Fleet Monitor. [V]
- **Solutions SaaS cloud:** Fleet Monitor + módulos; **SSO, RBAC, Integrations, Reporting, IT & Data Security, Cloud, Configuration, Communication** como capacidades compartidas. [V]
- **Integraciones:** a sistemas/cadena de suministro del cliente (eRepair integra supply chain; Fleet Monitor integra business partners). API implícita (no documentada públicamente). [V capacidad / A esquema]
- **Compound/físico:** campas locales (collection/delivery/inspection/refurb/storage) con **MI en tiempo real** de status+ubicación. [V]
- **BI/Informe:** INDICATA (dashboard Pro + Market Watch PDF mensual) — ver `indicata.md`. [V]

---

## 6. Precio
**Marketplace UK — TARIFAS PÚBLICAS (verificadas en vivo, autorola.co.uk/pricing; excl. IVA salvo indicación):** [V]

| Bloque | Concepto | Tarifa |
|---|---|---|
| **BUYING** (fee del comprador, según precio de compra) | £0–£9.999 | **£250** |
| | £10.000–£19.999 | **£300** |
| | £20.000–£29.999 | **£375** |
| | £30.000–£39.999 | **£450** |
| | £40.000–£49.999 | **£550** |
| | £50.000–£59.999 | **£650** |
| | £60.000–£69.999 | **£750** |
| | £70.000+ | **£850** |
| **SELLING** | Sale fee | **£150** ("No sale, no charge") |
| **TRANSPORT** | ICE road-driven 0–400 mi | **£200** |
| | EV road-driven 0–200 / 201–300 mi | **£230 / £280** |
| | Transporter single 0–100 mi | **£230** (+**£1,80/mi** extra) |
| | Transporter multicar | **POA** |
| **PAYMENT** | Stock Funding / Direct Debit | **£0** |
| | Non-Direct-Debit penalty | **£100** |

- Modelo: **comisión de comprador por tramos + sale fee fija + transporte tarifado + "no sale no charge"** (el vendedor fija reserva). [V]
- **Solutions & INDICATA: precio NO público** → enterprise, vía contacto/demo (importe = GAP). [V]
- Tarifas de otros mercados (DE/ES/FR…) probablemente análogas pero **no verificadas** (cada sitio tiene su propia /pricing). [A]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por cardeep. Autorola separa **3 superficies**: (A) Marketplace transaccional (lista → ficha tras login), (B) inteligencia de mayorista (dashboards de decisión), (C) Solutions (workflow operativo).

| Dato | Dónde / pantalla |
|---|---|
| Make, model, trim, body, fuel, kW, puertas, transmisión, 1ª matrícula, mileage, location, puja actual, cuenta atrás, país, nombre de venta | **Tarjeta de vehículo** en la **lista de auction / search results** (Stock Locator) — Marketplace [V vivo] |
| Filtros: make/model/año/mileage/fuel/country/sales-type/price-category/VAT | **Panel de búsqueda Stock Locator** (lateral) + **Search Agent** (guardado) + **Favourites** — Marketplace [V vivo] |
| Reserve / Start / Buy-It-Now price, VAT/margin status | Definidos por el vendedor; **start/buy-now visibles en tarjeta**, **reserve oculto**; configuración en panel del vendedor [V] |
| VIN, equipamiento, condition/inspection report completo, daños, nº fotos, llaves, service history | **Ficha de vehículo (vehicle detail)** — **tras login de "approved dealer"** (no público) [V acceso] |
| Geo Pricing, Export Index, European Target Price, Marketability Score, days-to-sell, demand/supply, best sale route | **Dashboard de remarketing / decisión INDICATA** (herramientas de "wholesale intelligence") [V] |
| Dealer performance/stock/sales (140k) | **Mapa/panel de localización y performance de dealers** (a quién remarketar) [V] |
| Lifecycle status & gateways (arrival/handover/return/inspection/sales), lead-time, registrations, recalls, servicing, repossession | **Fleet Monitor** — dashboard configurable + módulos (Service/Order/Booking/Business Partner) [V] |
| Conversación por vehículo | **Fleet Chat** dentro de Fleet Monitor (chat anclado al coche) [V] |
| Inspección: daño/tyres/foto/VIN/grade | **App VIS / IHS** (móvil, paso a paso) → sync real-time a Fleet Monitor y a la subasta [V] |
| Estado de reparación / claim | **Plataforma eRepair** (visibilidad de proceso de reparación) [V] |
| Status + ubicación física del vehículo | **MI en tiempo real de Compound Services / Fleet Services** [V] |
| Stock expuesto a compradores (descripción + fotos) | **Digital Showroom** (escaparate integrado con Fleet Monitor) [V] |
| Tarifas (buying/selling/transport/payment) | **Página pública /pricing** del sitio de cada país [V vivo] |

---

## 8. Diferencial (lo que ofrece y otras no)
1. [V] **Ecosistema cerrado de-fleet→venta bajo un dueño:** Marketplace (subasta) + Solutions (workflow físico/digital) + INDICATA (datos) — pocos competidores tienen las **tres** capas integradas con interfaz real-time entre ellas.
2. [V] **Wholesale intelligence accionable para decidir CANAL y PAÍS:** Geo Pricing + Export Index + European Target Price + Marketability Score → "en qué país y por qué ruta vendo cada coche para maximizar retorno" (arbitraje cross-border paneuropeo). Raro fuera de Autorola/INDICATA.
3. [V] **White-label auctions por vendedor** (Alphabet, Ayvens, Premium Leasing…) en cualquier país/idioma → el remarketer mantiene su marca.
4. [V] **Inspección estandarizada que viaja con el listado y es "traducible a todas las subastas"** (VIS) → un report sirve nacional e internacional.
5. [V] **eRepair a escala rental** (50k vehículos, 6.000 reparaciones/mes, Enterprise/Sixt/Hertz) — gestión de reparación/claims integrada con la cadena de suministro; nicho operativo poco común.
6. [V] **Tarifas de marketplace transparentes y públicas** (buyer fee por tramos, transporte ICE/EV, "no sale no charge") — inusual en B2B donde casi todos ocultan precio.
7. [V] **Cobertura de 25 mercados** con red de **70.000+ compradores** + compound físico local en cada mercado (no solo digital).
8. [V] **Soporta salvage / accidentados / no rodantes** (FR) y **comerciales** (UK) además de turismo VO.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Ficha de vehículo detallada (VIN, equipamiento, condition report, fotos) NO pública:** exige login de "approved dealer". Solo la **tarjeta resumida** es accesible sin cuenta.
- [V] **Sin documentación técnica de API pública:** no hay esquema, auth ni diccionario de campos publicado para Marketplace/Solutions/INDICATA.
- [V] **Precio de Solutions e INDICATA opaco** (solo el Marketplace UK publica tarifas).
- [A] **No es base de historial de vehículo por-VIN** (siniestros/propietarios/fraude km certificado) tipo Carfax/autoDNA: tiene condition report puntual de inspección y eventos operativos, no provenance histórica certificada.
- [A] **No es decode VIN-to-spec como producto** ni catálogo de specs/equipamiento de mercado (a diferencia de JATO/Autovista): describe el vehículo concreto inspeccionado, no un catálogo técnico universal.
- [A] **No es catálogo de reparación/SMR** (labour times, precios de piezas, TecDoc): eRepair **gestiona** reparaciones/claims, no provee el catálogo de tiempos/precios OEM.
- [A] **Sin TCO/coste total de propiedad** como producto (eso vive en Autovista/otros).
- [A] **Inteligencia EV granular limitada** (kWh/química/SoH) — más allá de filtro fuel y tarifa transporte EV; el detalle EV profundo es de INDICATA Market Watch, no del Marketplace.
- [A] **No es censo/directorio de puntos de venta ni huella digital de dealers** (el core de cardeep): expone *compradores aprobados* e *inventario en subasta*, no un mapa público de la red de PV.
- [A] **Foco geográfico Europa + LatAm + APAC selectivo:** EE.UU. presente como sitio pero el peso del marketplace es europeo; ausencias frente a players US (Manheim/ACV).
- [V] **Days-to-sell como índice nombrado vive en INDICATA**, no en la UI del Marketplace (el Marketplace muestra cuenta atrás de subasta, no time-to-sell de mercado).

---

## 10. Fuentes (URLs)
- https://www.autorola.com/ — autodefinición, 3 unidades, formatos subasta, 70.000 buyers, segmentos, países [V WebFetch].
- https://www.autorola.co.uk/ — marketplace en vivo: Stock Locator (1.588 veh), filtros, Search Agent, sellers (Alphabet/Ayvens/MHC/Post), 25 sitios [V Playwright].
- https://www.autorola.co.uk/auctions — eventos de subasta (Weekly Mazda/Volvo, Daily Commercial, Daily KIA, Dealer Exclusive, Aston Martin eAuction; internacionales) [V Playwright].
- https://www.autorola.co.uk/auctions/673301 — **campos de tarjeta de vehículo en vivo** (make/model/trim/body/fuel/kW/puertas/transmisión/1ª-matrícula/mileage/location/puja/cuenta-atrás) + filtros (make/model/año/mileage/fuel/country/sales-type/price-category/VAT) [V Playwright].
- https://www.autorola.co.uk/pricing — **tarifas públicas** buying/selling/transport/payment + "you set the reserve price / no sale no charge" + 2.000 dealers UK [V Playwright].
- https://www.autorolagroup.com/products-and-services/vehicle-auctions/ — 4 formatos, 24 países, 70k buyers, 20+ años, links a Inspections/Compound/Fleet Monitor/Market Intelligence [V].
- https://www.autorolagroup.com/products-and-services/vehicle-inspections/ — **VIS** (configurable, Android/iOS, integrado a Fleet Monitor, traducible a subastas) [V].
- https://www.autorolagroup.com/products-and-services/compound-services/ — collection/delivery/inspection/refurbishment/storage + real-time MI [V].
- https://www.autorolagroup.com/contact/ — **HQ Skibhusvej 52A DK-5000 Odense C**, +45 70 20 16 61, 18+ oficinas incl. UAE [V].
- https://autorolasolutions.com/ — Fleet Monitor, TradeIn, IHS, Digital Showroom; capacidades SSO/RBAC/cloud; 6 segmentos [V].
- https://autorolasolutions.com/digital-ecosystem/ — ecosistema completo + features (Configuration/Communication/Integrations/Reporting/RBAC/SSO/Security/Cloud) [V].
- https://autorolasolutions.com/digital-ecosystem/products/fleet-monitor/ — **módulos**: Business Partner, Service, Order, Booking, Fleet Chat; gateways arrival/handover/return/inspection/sales [V].
- https://autorolasolutions.com/digital-ecosystem/products/inspection-and-trade-in-app/ — **TradeIn** (30 min, 4 pasos, valoración real-time) [V].
- https://autorolasolutions.com/digital-ecosystem/products/inspection-helper-system/ — **IHS** (VIN/mileage/damage/tyres/mechanical/photos, configurable, real-time a Fleet Monitor) [V].
- https://autorolasolutions.com/digital-ecosystem/products/digital-showroom/ — browse/search/favourites/buy, descripciones+fotos, estrategias de venta [V].
- https://www.autorolagroup.com/solutions-dec24/ — Ib Kimose: eRepair + compound management; clientes Sixt/Enterprise [V referencia prensa].
- https://autorolasolutions.com/.../erepair... y autorola-solutions-announces-upgrades-to-its-erepair... — **eRepair 2.0**: 6.000 reparaciones/mes, ~50.000 vehículos, Enterprise/Sixt/Hertz/East Coast [V].
- https://indicata.com/fleet-remarketers/ — **Geo Pricing, Export Index, European Target Price, Marketability Scores**, start/reserve/buy-now, best sale route, 140k dealers [V].
- https://autorolasolutions.com/autorolas-digital-revolution-in-the-automotive-industry/ — **PwC**: 1996, Grøftehauge único dueño dic-2023, 19 países/5 continentes, 700+ empleados, >1.000M DKK / 83M DKK 2024, 3 unidades, INDICATA 15M coches/día image recognition, IA desde 2014, +20%/año [V].
- https://www.fleeteurope.com/.../autorola-signs-pan-european-remarketing-deal-bmw — deal BMW paneuropeo [V referencia].
- https://www.businesscar.co.uk/news/autorola-to-launch-big-data-used-car-pricing-tool/ — ~200k veh/año, 6M VO, 13 países INDICATA [A reportado].
- DNS: `wholesale-intelligence.autorola.com` resuelve por **wildcard `*.autorola.com`** (no portal de producto) → subdominio = etiqueta de categoría cardeep, no host de producto.

> Verificación: identidad/escala/financieros con ≥2 fuentes (PwC + contact + render). Campos de listado y **tarifas** [V] leídos en vivo (Playwright) del marketplace real. Productos/módulos [V] de páginas de producto. Wholesale intelligence (Geo Pricing/Export Index/Target Price/Marketability) [V] de indicata fleet-remarketers. eRepair métricas [V] de prensa Autorola. Ficha detallada de vehículo y APIs = tras login / no documentadas (GAP, no inventado). INDICATA en profundidad = `indicata.md`.
