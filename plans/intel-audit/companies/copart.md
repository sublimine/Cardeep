# COPART — Auditoría atómica

> **slug:** `copart` · **Subdominio cardeep:** **wholesale-intelligence** · **Web:** https://www.copart.com/ · **España:** https://www.copart.es/ · **UK:** https://www.copart.co.uk/ · **Cotiza:** NASDAQ: **CPRT** (Nasdaq-100 + S&P 500)
> **Auditado:** 2026-06-30 · **Método:** WebSearch + WebFetch intensivos + **render en vivo con Playwright** del Vehicle Finder y de los resultados de búsqueda (`lotSearchResults`) de copart.com. **Doctrina VAM:** cada afirmación lleva fuente; `[VERIFICADO]` (≥2 fuentes o render directo), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (marketing propio sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato de varias fuentes), `[NO-VERIFICADO]`. Nada inventado; si la observación contradice una afirmación previa, gana la observación.
>
> **Veredicto express:** Copart **NO es un libro de valor** (no es KBB/Black Book/cap/Eurotax) ni un VHR (no es Carfax). Es el **mayor marketplace mundial de subasta ONLINE de vehículos de salvamento/siniestro y usados**, B2B-first, cuyo proveedor primario de inventario son **aseguradoras (80–90% de la oferta US)**. Su capa de **"wholesale-intelligence"** tiene cuatro piezas reales: (1) el **dato transaccional first-party** — precio de martillo de ~3,5–4 M de vehículos/año, que el propio Copart usa para fijar y reaccionar a valores; (2) **ProQuote / ProQuote.ai** — motor ML + visión por computador que da a las aseguradoras una **estimación de valor de salvamento en tiempo real** para decidir reparar vs. declarar pérdida total; (3) **IntelliSeller** — ML que recomienda al vendedor cuándo poner *minimum bid* y cuándo re-subastar para maximizar retorno y minimizar *cycle time*; (4) **Sales Data** — descarga CSV de resultados de subasta para miembros. Encima: **Title Express** (procuración de título + pago a acreedores/lienholder), **VB3** (motor de subasta), **Condition Reports** ($35), **CrashedToys/NPA** (powersports) y **Cash For Cars** (canal de compra a particular).
>
> **Clave cardeep (Alemania/España):** en mercados como **Alemania y España, Copart cobra *listing fees* a peritos de seguros que usan la plataforma para determinar el VALOR RESIDUAL del vehículo *aunque no se venda* en Copart** — es decir, la plataforma de subasta funciona ya como herramienta de **valoración de salvamento** para el sector asegurador. `[PARCIAL — 1 fuente analista]`
>
> **Patrón a copiar por cardeep:** (1) la **tarjeta de lote** ultra-densa (YMM+Trim · Lot# · iconos de condición · Odometer+brand · **Estimated Retail Value** · Title type+code · Damage · Keys · Location · Item# · sale timing/Current bid) como ficha mínima de inventario; (2) el **panel de filtros facetado con contadores** (Clean Title (1.000+), Salvage Title (10.000+)…) y **Sort by: "Sale light"**; (3) el **AI Search** unificado ("enter Make, Model, Damage, Color, VIN, and more…"); (4) la sección **"Order Products & Services"** de la ficha como punto de venta del Condition Report; (5) el **ERV (valor de referencia aportado por el vendedor) embebido en cada tarjeta** como ancla de valor visible antes de pujar.

---

## 1. Identidad

| Campo | Valor | Fuente / estado |
|---|---|---|
| Nombre legal | **Copart, Inc.** | Wikipedia; SEC 10-K `[VERIFICADO]` |
| Fundación | **1982**, por **Willis J. Johnson** (34 años), en **Vallejo, California** | Wikipedia; Forbes; DCFmodeling `[VERIFICADO ×2]` |
| IPO / cotización | **17-mar-1994** a **$12/acción** (2,3 M acciones), NASDAQ ticker **CPRT**; hoy en **Nasdaq-100 y S&P 500** | Wikipedia; CEOCFO `[VERIFICADO ×2]` |
| HQ | **Dallas, Texas** (Copart Tower, ~53.000 sq ft). Antes Vallejo → Fairfield → **Dallas (2012)** | Wikipedia `[VERIFICADO]` |
| Propiedad / grupo | **Empresa pública independiente** (no filial de nadie). Willis Johnson = fundador/Chairman y mayor accionista individual | Wikipedia; Forbes `[VERIFICADO]` |
| Liderazgo | **Willis J. Johnson** (Founder/Chairman) · **Jay Adair** (Executive Chairman) · **Jeff Liaw** (CEO) | Wikipedia `[VERIFICADO]` |
| Empleados | **~11.600** (FY2025) | Wikipedia (datos FY2025) `[PARCIAL]` |
| Modelo de negocio | **Marketplace/agente de remarketing** de vehículos al final de su ciclo de vida; conecta vendedores (sobre todo aseguradoras) con compradores globales (desguazadores, reconstructores, dealers, exportadores) | anomalyinvestments; vizologi `[VERIFICADO ×2]` |
| Segmentos reportados | **United States** + **International** | SEC 10-K FY2025 `[VERIFICADO]` |

**Escala (con fuente y fecha):**

| Métrica | Valor | Fuente / estado |
|---|---|---|
| Ingresos FY2025 (12m a 31-jul-2025) | **$4.646,958 M** (~$4,65 B), +11,4% YoY | SEC 10-K FY2025 (vía publicnow/last10k) `[VERIFICADO]` |
| — Service revenues | **$3.968,662 M** (~$3,97 B), +11,4% | SEC 10-K FY2025 `[VERIFICADO]` |
| — Vehicle sales | **$678,296 M** (~$678 M), +0,4% | SEC 10-K FY2025 `[VERIFICADO]` |
| Operating income | **~$1,69 B** = **36%** de ingresos totales | Wikipedia FY2025; 10-K `[VERIFICADO ×2]` |
| Net income | **~$1,55 B** | Wikipedia FY2025 `[PARCIAL]` |
| Total assets | **~$10,1 B** | Wikipedia FY2025 `[PARCIAL]` |
| Vehículos vendidos/año | **"4+ millones"** (homepage; "used, wholesale and repairable") · analistas estiman **~3,0–3,5 M** de salvamento puro vía VB3 | copart.com; anomalyinvestments `[VERIFICADO homepage / RECONSTRUIDO salvaje]` |
| Miembros (compradores) registrados | **~1 millón** | anomalyinvestments; oneinc `[VERIFICADO ×2]` |
| Países donde hay compradores | **"165 países"** (analista) / **"185+ países"** (One Inc.) / **"+190"** en marketing | anomalyinvestments; oneinc `[PARCIAL — cifra varía]` |
| Localizaciones físicas (yards) | **"más de 200" / "250 yards"**; **>21.000 acres** de capacidad; **posee >90%** del suelo | Wikipedia; anomalyinvestments `[VERIFICADO ×2, rango]` |
| Cuota mercado salvamento US | **~48%** (rango "high 40s–mid 50s"); mercado total salvamento ~**6,8 M veh.** | anomalyinvestments `[PARCIAL — 1 fuente analista]` |

**Lineaje / adquisiciones (anti-confusión):**

| Hito | Año | Fuente / estado |
|---|---|---|
| Fundación (Vallejo, CA) | **1982** | Wikipedia `[VERIFICADO]` |
| IPO NASDAQ (CPRT) | **1994** | Wikipedia `[VERIFICADO]` |
| Adquisición **NER Auction Group** (duplica yards US) | **may-1995** | Wikipedia `[VERIFICADO]` |
| Lanzamiento **VB2** (primera subasta 100% online) | **2003** | Wikipedia `[VERIFICADO]` |
| Internacional: **Canadá** (2003), **UK** (2007), **Brasil/España/Irlanda/Alemania/Oriente Medio** (2012) | varios | Wikipedia `[VERIFICADO]` |
| Lanzamiento **VB3** | **ago-2013** | Wikipedia; anomalyinvestments `[VERIFICADO ×2]` |
| Adquisición **National Powersport Auctions (NPA)** / Cycle Express | **2017** | Wikipedia; crashedtoys `[VERIFICADO ×2]` |
| Adquisición **Autovahinkokeskus (AVK)** (Finlandia) | **2018** | Wikipedia `[VERIFICADO]` |
| Lanzamiento marca **CashForCars.com** (CA 2018, DE 2019, UK 2020) | 2018–2020 | Wikipedia `[VERIFICADO]` |

**Marcas/subsidiarias:** **Copart** (núcleo), **CrashedToys** (salvamento powersports/motos, "powered by Copart"), **National Powersport Auctions (NPA) / Cycle Express** (powersports, con su propio **"NPA Value Guide"**; yards en Atlanta, Cincinnati, Dallas, Philadelphia, San Diego), **Cash For Cars** (compra a particular), **Copart Dealer Services (CDS)**. `[VERIFICADO]`

**Categorías de producto/negocio:**
1. **Subasta online de salvamento/siniestro** (núcleo; aseguradoras → compradores globales).
2. **Subasta de usados/wholesale** (dealer, fleet/lease, bank/repossessed, rental).
3. **Inteligencia de salvamento para aseguradoras** — **ProQuote / ProQuote.ai** (decisión pérdida total), **IntelliSeller** (optimización de venta).
4. **Servicios de remarketing al vendedor** — pickup, transporte, almacenaje, **title processing (Title Express)**, marketing, subasta, reporting de datos.
5. **Dato de mercado al comprador** — **Sales Data (CSV)**, **Sales List**, **Condition Reports** ($35), Vehicle history (vía partners).
6. **Powersports** (CrashedToys + NPA).
7. **Cash For Cars** (compra directa a consumidor; Copart como *principal*).

**Clientes objetivo:**
- **Vendedores (oferta):** **aseguradoras (80–90% del volumen US)**, + bancos/financieras, flotas/renting, **charities** (donación de coche), dealers y particulares. `[VERIFICADO ×2]`
- **Compradores (demanda):** **dismantlers/desguaces, reconstructores/rebuilders, dealers, exportadores** y, según membresía, **público general**. Internacionales = **90% de las subastas de reconstruibles** y **40% del inventario US**. `[VERIFICADO ×2]`

---

## 2. Cobertura

- **Geografía (11 países):** **EE. UU.** (núcleo) + **Canadá, Reino Unido, Alemania, Irlanda, Brasil, España, Emiratos Árabes Unidos, Bahréin, Omán, Finlandia**. `[VERIFICADO ×2]` (Wikipedia; copart.com home)
- **España (`copart.es`) — PRESENTE y relevante para cardeep:**
  - **Opera desde 2016**; **>1.500 vehículos vendidos/mes**, crecimiento anual **>30%**; **+29.000 vehículos** vendidos acumulados (cifra histórica de prensa). `[VERIFICADO ×2]` (segurosnews; soymotor/ae-renting)
  - **9 campas activas**: **Sevilla, Madrid, Tarragona, Lugo, Albacete, Mallorca, La Rioja, Tenerife, Gran Canaria**. `[PARCIAL — 1 fuente]`
  - **Subastas a tiempo real, martes y jueves 11:00** (hora peninsular); adjudicación directa al mejor postor, **sin negociación posterior**. `[PARCIAL]`
  - **Aseguradoras clientes citadas:** **Allianz, AXA, Mutua Madrileña, Admiral Seguros, Generali, Helvetia Seguros España, Reale Seguros** y el **Consorcio de Compensación de Seguros**. `[PARCIAL — 1 fuente]`
  - Vendedores: **aseguradoras, concesionarios, flotas de alquiler y renting**. Compradores: **talleres, desguaces, compraventas, concesionarios**. Tipos: **coches, SUV, motocicletas, furgonetas** (para reparar o desguazar). `[VERIFICADO]`
  - Director comercial citado: **Eric Mañas**. Modelo: la aseguradora **compensa el 100% del valor** y el asegurado cede los derechos de venta del salvamento a través de Copart (Copart gestiona retirada, venta y documentación). `[PARCIAL]`
- **Nuevo vs usado:** **USADO + SALVAMENTO/SINIESTRO** (núcleo) + wholesale entre profesionales. **NO** maneja coche nuevo/MSRP. `[VERIFICADO]`
- **Tipos de vehículo:** turismos, SUV, light/heavy trucks, **motos/powersports** (CrashedToys/NPA), **boats, RV/motorhome, ATV, jet ski, trailers**, equipo industrial, clásicos/exóticos. `[VERIFICADO]` (render Vehicle Finder + CrashedToys)
- **Frescura del dato:** inventario nuevo **a diario**; **+500.000 vehículos disponibles cada día**; subastas **lun–vie** (US). Datasets de terceros que espejan Copart se actualizan **a diario**. `[VERIFICADO]`
- **Naturaleza del dato (clave):** **transacción REAL de subasta first-party** (precio de martillo entre profesionales/exportadores) + **ERV y repair cost aportados por el vendedor** + **clasificación de daño/título**. No es asking price ni listing especulativo. Copart **"reacciona a y a la vez fija"** valores porque ha vendido miles de unidades de cada modelo. `[VERIFICADO ×2]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **Lot listing / VDP** (VB3) | Ficha de vehículo en subasta | Tarjeta + ficha con identidad, daño, título, ERV, sale info, fotos | **~168 campos/lote** (36 nombrados) |
| **Condition Report (CR)** | Reporte de inspección de pago ($35) | Body/engine/interior/mechanical/tires + 2 vídeos + fotos extra + equipamiento | ~12+ |
| **ProQuote / ProQuote.ai** | Estimación ML+CV de valor de salvamento para aseguradora | Salvage value estimate + recomendación total-loss | ~6 |
| **Preliminary ProQuote** | Valor predictivo de salvamento con pocos datos | Salvage value predictivo temprano | ~3 |
| **IntelliSeller** | ML de optimización de venta para el seller | Minimum bid recom. + re-auction recom. + cycle-time | ~5 |
| **Sales Data (CSV)** | Descarga de resultados de subasta (miembros) | Histórico de ventas: precio + fecha + atributos | ~20+ |
| **Sales List** | Listas de venta del día/semana (run lists) | Orden de venta + lote + sale info | ~10 |
| **Title Express** | Procuración de título + pago a acreedor (aseguradoras/lenders) | Title status/tracking + lienholder/loan payoff | ~8 |
| **Vehicle Finder / AI Search** | Buscador facetado + búsqueda IA | Filtros + resultados | n/a (filtros) |
| **CrashedToys / NPA** | Subasta powersports + **NPA Value Guide** | Lote powersports + guía de valor | ~ (espejo) |

> **Fuente del schema atómico:** esquema de **dataset rebrowser/copart-dataset** (2.137.389 registros, ~55 columnas con tasa de relleno) + **scraper Apify parseforge** (168 campos, 36 nombrados) + **glosario de términos Copart UK** + **render en vivo de la tarjeta de lote** (lotSearchResults). Los `[Premium]` del dataset (VIN, ERV, high bid, BIN, seller, imágenes) marcan los campos que Copart restringe tras login.

### 3.1 Lot listing / VDP — campos atómicos del vehículo (núcleo del dato)

**(A) Identidad / decode**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `lot_number` / **Lot #** | Identificador único Copart del vehículo | render tarjeta; UK terms `[VERIFICADO]` |
| `item_number` / **Item #** | Orden en que el lote se vende en la sesión virtual | UK terms; render `[VERIFICADO]` |
| `vin` | VIN de 17 caracteres del fabricante `[Premium]` | render; rebrowser `[VERIFICADO]` |
| `year` · `make` · `modelGroup` · `modelDetail`/`model` · `trim` | Año/Marca/Modelo/Versión (ej. "2015 HONDA CR-V EXL") | render tarjeta `[VERIFICADO]` |
| `bodyStyle` | Carrocería | rebrowser `[VERIFICADO]` |
| `exteriorColor` / **Color** | Color exterior | rebrowser `[VERIFICADO]` |
| `engine` | Motor (según VIN) | rebrowser; UK terms `[VERIFICADO]` |
| `cylinders` | Nº de cilindros | rebrowser `[VERIFICADO]` |
| `drivetrain`/`drive` / **Drive** | Tracción (designación del fabricante del power train) | rebrowser; UK terms `[VERIFICADO]` |
| `transmission` | Transmisión | rebrowser `[VERIFICADO]` |
| `fuelType` / **Fuel** | Combustible | rebrowser `[VERIFICADO]` |
| `vehicleType` | Tipo (Automobile, Motorcycle, Boat, RV…) | rebrowser; render `[VERIFICADO]` |

**(B) Valoración / pricing**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `estRetailValue` / **Estimated Retail Value (ERV)** | **Valor de referencia del lote aportado por el VENDEDOR a Copart** (NO es valoración propia de Copart). Mostrado en la tarjeta (ej. "$16,875.63") `[Premium]` | render tarjeta; UK terms; AutoBidMaster `[VERIFICADO ×2]` |
| `repairCost` / **Repair Cost** | Coste estimado de reparación, aportado por el vendedor | UK terms; rebrowser `[VERIFICADO]` |
| `highBid` / **Current Bid** | Puja actual más alta (ej. "Current bid: $0.00USD") `[Premium]` | render; UK terms `[VERIFICADO]` |
| `buyItNowPrice` / **Buy It Now** | Precio de compra inmediata (VB3) `[Premium]` | rebrowser; render Featured "Buy It Now" `[VERIFICADO]` |
| `makeOfferEligible` / **Make An Offer** | Elegibilidad de oferta | rebrowser; anomalyinvestments `[VERIFICADO]` |
| **BID4U** | Proxy bid: representa al mejor postor en preliminar y en subasta virtual | UK terms `[VERIFICADO]` |
| **Monster Bid** | Puja de uno o más incrementos sobre la actual | UK terms `[VERIFICADO]` |
| `saleStatus` / **Sale Status** | **Pure Sale** (sin mínimo/reserva), **On Approval** (vendedor aprueba el high bid), **Minimum Bid** (reserva) | UK terms; render Featured "Pure Sale" `[VERIFICADO ×2]` |
| `currencyCode` | Moneda | rebrowser `[VERIFICADO]` |

**(C) Daño / condición**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `damageDescription` / **Primary Damage** | Daño primario (códigos de 2 letras: ALL OVER, BURN, HAIL, FRONT END, REAR END, SIDE, MECHANICAL, ROLLOVER, WATER/FLOOD, VANDALISM, +20) | UK terms; render ("Hail Damage", "Front End Damage", "Side Damage", "Rear End Damage") `[VERIFICADO ×2]` |
| `secondaryDamage` / **Secondary Damage** | Daño secundario (44% relleno) | rebrowser; UK terms `[VERIFICADO]` |
| `lotCondCode` / **Lot Condition Code** | Código de condición del lote | rebrowser `[VERIFICADO]` |
| `runsDrives` / **Run & Drive** | El vehículo arrancó, engranó y avanzó al llegar al yard (sin garantía en pickup). Icono "Run and Drive" en tarjeta | UK terms; render `[VERIFICADO ×2]` |
| **Engine Start Program** | Icono: el motor arranca (programa de arranque) | render tarjeta (icono) `[VERIFICADO]` |
| **Enhanced Vehicles** | Icono de vehículo "enhanced" | render tarjeta (icono) `[VERIFICADO]` |
| `hasKeys` / **Keys** | Llaves presentes ("Keys available") | render; rebrowser `[VERIFICADO]` |
| `accident_score` | Puntuación de accidente | Apify scraper `[PARCIAL]` |
| `autoGrade` | Score de condición 0–5 (estándar AutoGrade de **Manheim/NAAA**, no propietario de Copart; 2% relleno) | rebrowser; Manheim/NAAA `[VERIFICADO ownership=Manheim]` |
| `saleLight` | **Sale light** (verde/amarillo/roja) — semáforo de condición/venta; eje de "Sort by: Sale light" | render (Sort by: Sale light); rebrowser `[VERIFICADO]` |
| `announcements` · `specialNote` · **Current Sale Highlights** | Anuncios/notas especiales; "Highlights" = comentarios del General Manager de Copart sobre el lote | UK terms; rebrowser `[VERIFICADO]` |

**(D) Título / legal / odómetro**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `saleTitleType` / `title_code` / **Title type** | Tipo de título (ej. "Salvage Title", tooltip "CERT OF TITLE-SALVAGE", "Clean Title") | render ("Salvage Title (ST-CT)"); rebrowser `[VERIFICADO ×2]` |
| `saleTitleState` | Estado emisor del título (ej. "ST-MA", "ST-CT") | render; rebrowser `[VERIFICADO]` |
| `mileage`/`odometer` / **Odometer** | Lectura de odómetro (ej. "84502", "211164") | render; rebrowser `[VERIFICADO]` |
| `odometerBrand` / **Odometer brand** | Marca del odómetro: **ACTUAL / NOT ACTUAL / EXEMPT** (ej. "(ACTUAL)") | render ("0 (ACTUAL)"); rebrowser `[VERIFICADO]` |
| **VAT** (UK) | Indica si aplica IVA además del precio | UK terms `[VERIFICADO]` |
| **Loss category / ABI (UK/EU)** | **Cat A** (scrap, no recuperable), **Cat B** (breaker/despiece, licencia requerida), **Cat S** (reparable estructural), **Cat N** (reparable no estructural) | support.copart.co.uk; ABI Code of Practice `[VERIFICADO ×2]` |

**(E) Subasta / logística / ubicación**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `yardNumber` · `yardName` | Centro/yard que procesa la venta | rebrowser; UK terms `[VERIFICADO]` |
| `saleDate` · `saleDayOfWeek` · `saleTime` · `saleTimeZone` | Fecha/día/hora/zona de la subasta virtual | rebrowser `[VERIFICADO]` |
| **Time left / "Auction in 2D 6H 17min"** | Cuenta atrás dinámica del lote (VB3) | render `[VERIFICADO]` |
| `locationCity` · `locationState` · `locationZip` · `locationCountry` | Ubicación (ej. "TX - CORPUS CHRISTI", "PA - PHILADELPHIA") | render; rebrowser `[VERIFICADO]` |
| `latitude` · `longitude` | Geolocalización del yard | Apify scraper `[VERIFICADO]` |
| `gridRow` | Fila/posición en el grid del yard | rebrowser `[VERIFICADO]` |
| `offsiteAddress1/State/City/Zip` | Dirección offsite (ventas fuera de yard, 1% relleno) | rebrowser; render Featured "Offsite Sales" `[VERIFICADO]` |
| `rentals` (bool) · `wholesale` (bool) | Flags: alquiler / wholesale | rebrowser; render Featured `[VERIFICADO]` |

**(F) Vendedor / media**

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| `sellerName` / **Seller** | Nombre del vendedor (35% relleno) `[Premium]` | rebrowser `[VERIFICADO]` |
| **Seller type** | Insurance / Dealer / Fleet / Bank-Repossessed / Charity / Individual | anomalyinvestments; render Featured `[VERIFICADO]` |
| `images` · `images_high_res` · `imageThumbnail` | Galería de fotos (estándar **~10 imágenes**; HD) `[Premium]` | shopusedcars; rebrowser `[VERIFICADO]` |
| `engine_video_high_res` | Vídeo de arranque del motor (HD) | Apify scraper `[VERIFICADO]` |
| `listingUrl` / `item_url` | URL del lote `[Premium]` | rebrowser `[VERIFICADO]` |
| `build_sheet` (object) | Hoja de equipamiento de fábrica (opciones/specs por VIN) | Apify scraper `[VERIFICADO]` |

**(G) Secciones de especificación/equipamiento de la ficha** (bloques HTML que despliegan el detalle): `vehicle_assessment_description` · `technical_specifications` · `options` · `styles` · `engines` · `interior` · `safety` · `exterior` · `mechanical` · `entertainment`. `[VERIFICADO]` (webscraper.io)

### 3.2 Condition Report (CR) — inspección de pago

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| **Precio** | **$35** por reporte, desde la **sección "Order Products & Services"** de la ficha; entrega por email **<24 h** | shopusedcars; copart landing `[VERIFICADO]` |
| **Name / Make / Model** | Identidad del vehículo | shopusedcars `[VERIFICADO]` |
| **Registration number** | Matrícula | shopusedcars `[VERIFICADO]` |
| **Color** | Color | shopusedcars `[VERIFICADO]` |
| **Condition of body** | Estado de carrocería | shopusedcars `[VERIFICADO]` |
| **Engine condition** | Estado del motor | shopusedcars `[VERIFICADO]` |
| **Owner name** | Nombre del propietario | shopusedcars `[VERIFICADO]` |
| **2 vídeos internos/externos + fotos adicionales + equipamiento + condición** | Extras del CR sobre la galería estándar | search (copart CR landing) `[PARCIAL]` |

### 3.3 ProQuote / ProQuote.ai (inteligencia de salvamento para aseguradoras — NÚCLEO de valoración)

> **Servicio propietario** que asiste al vendedor (aseguradora) en la evaluación del siniestro dando una **estimación online de valor de salvamento**, para decidir **reparar vs. declarar pérdida total**.

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| **Salvage value estimate** | Estimación de valor de salvamento en tiempo real | repairerdrivennews; anomalyinvestments `[VERIFICADO ×2]` |
| **Motor** | **Computer vision + machine learning** sobre **decenas de millones de imágenes históricas** + **millones de resultados de subasta** | tikr; anomalyinvestments `[VERIFICADO ×2]` |
| **Recomendación total-loss** | "Cuándo y cuándo NO declarar pérdida total"; identifica **borderline total losses** más pronto y con menos variabilidad que el humano | repairerdrivennews; tikr `[VERIFICADO ×2]` |
| **Preliminary ProQuote** | Variante: **valor predictivo de salvamento con pocos datos** (vehículos económicamente ventajosos), desde la **app móvil del perito** | search (ProQuote.ai) `[PARCIAL]` |
| **Uso** | El perito/adjuster obtiene "a ProQuote" en la plataforma móvil; el valor se descuenta del payout al asegurado | avvo (uso real); search `[VERIFICADO uso]` |
| **Marca "Co.ai"** | Una fuente secundaria describe "Co.ai, a proprietary suite of total loss determination and valuation tools (ML + computer vision)" — **posible marca paraguas NO confirmada** (la búsqueda dirigida no la corroboró; ProQuote.ai sí está verificada) | search (1 fuente) `[NO-VERIFICADO]` |

### 3.4 IntelliSeller (optimización de venta para el vendedor)

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| **Minimum bid recommendation** | Cuándo y a qué nivel establecer un *minimum bid/reserve* | anomalyinvestments; pitchgrade `[VERIFICADO]` |
| **Re-auction recommendation** | Cuándo re-subastar una unidad para optimizar retorno | anomalyinvestments `[VERIFICADO]` |
| **Cycle-time optimization** | Minimiza el tiempo de ciclo asegurando retorno óptimo | anomalyinvestments `[VERIFICADO]` |
| **Historical performance insights** | Insights de rendimiento histórico de vehículos vendidos (millones de comparables) | anomalyinvestments; thedrive `[VERIFICADO ×2]` |
| **Motor** | Machine learning sobre **vehicle + sales data** propios | anomalyinvestments `[VERIFICADO]` |

### 3.5 Sales Data (CSV) — dato de mercado para el comprador

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| **Producto** | "CSV Sales Data" — descarga de **resultados de subasta** desde el menú **Inventory → Sales Data** | copart.com/buyer/sales/download-sales-data; render menú `[VERIFICADO]` |
| **Acceso** | **Login de miembro** (gratis para miembros; basic/premier) | search `[PARCIAL]` |
| **Columnas (espejo del dataset)** | lot/VIN, year/make/model/trim, **sale price/high bid**, sale date, odometer + brand, **primary/secondary damage**, title type/state, ERV, repair cost, body, color, engine, drive, transmission, fuel, keys, run&drive, location, seller, sale status | rebrowser dataset; Apify `[RECONSTRUIDO desde schema]` |
| **Sales List** | Listas de venta del día/semana (run lists) navegables (Today's Auctions, Auction Calendar) | render menú Auctions `[VERIFICADO]` |

### 3.6 Title Express (procuración de título + pago a acreedor)

| Campo atómico | Definición | Fuente / estado |
|---|---|---|
| **Procuración de título** | Asiste a aseguradoras en la obtención del título y el papeleo del total loss (state-required docs, total loss packet) | worktruckonline; copart careers `[VERIFICADO]` |
| **Lienholder/Loan payoff** | Llamadas iniciales al **lienholder** para asegurar payoff y título; **Lender Portal** para que el prestamista aporte el payoff | oneinc; worktruckonline `[VERIFICADO ×2]` |
| **VIN-based matching** | Emparejamiento por VIN + updates en tiempo real (integración con One Inc. ClaimsPay) | oneinc `[VERIFICADO]` |
| **Title tracking** | Herramientas de seguimiento del estado del título (member-news "Title Tracking") | copart member-news `[VERIFICADO]` |
| **Escala** | **>1 millón de títulos procesados/año** vía la plataforma | search (analista) `[PARCIAL]` |

### 3.7 Vehicle Finder / AI Search (descubrimiento — render en vivo)

**AI Search:** caja única "**NEW AI Search!** enter Make, Model, Damage, Color, VIN, and more…". `[VERIFICADO render]`

**Filtros del Vehicle Finder:** Condition (All/Used/Salvage) · Types (Automobile…) · **Odometer** (slider 0–250.000+) · Year (From/To) · Damage type · Make · Model · Location (Location / State-province / Zip) · **VIN/Lot #** lookup. `[VERIFICADO render]`

**Filtros del resultado (`lotSearchResults`):** Vehicle title type **con contadores** (Clean Title (1.000+), Salvage Title (10.000+)) · Odometer · Make/Model · Drive train · Sale date · +secciones colapsables. **Sort by: "Sale light"** + switch de orden. `[VERIFICADO render]`

**Categorías destacadas (Featured items, 23):** Arbitration-Eligible · Electric Vehicles · Hot Items · Fleet/Lease · Hybrid Vehicles · Inspected · Exotics · No License Required · **Buy It Now** · **Run and Drive** · **Pure Sale** · New Items · Featured Vehicles · Offsite Sales · Recovered Thefts · Rentals · Public and General Business · Bank/Repossessed · Commercial Vehicles · Specialty Vehicles · Classics · **Wholesale Vehicles**. `[VERIFICADO render]`

---

## 4. Metodología / fuentes de datos

- **Dato primario = transacción REAL de subasta first-party** (precio de martillo de ~3,5–4 M veh./año entre profesionales y exportadores de 165–185 países). Copart **fija y a la vez reacciona** a valores porque ha facilitado la venta de miles de unidades de cada modelo; los compradores valoran sobre las **medias de precio de subasta**. `[VERIFICADO ×2]`
- **ERV y Repair Cost = aportados por el VENDEDOR** (no valoración propia de Copart). Es input, no output del modelo. `[VERIFICADO]`
- **ProQuote.ai = computer vision + ML** sobre **decenas de millones de imágenes históricas + millones de resultados de subasta** → estimación de valor de salvamento + recomendación de pérdida total en tiempo real. `[VERIFICADO ×2]`
- **IntelliSeller = ML** sobre vehicle+sales data propios → minimum bid / re-auction / cycle-time. `[VERIFICADO]`
- **AI transversal (declarado por CEO Jeff Liaw):** pricing, decisión de pérdida total, soporte a clientes/agentes, recomendaciones a nivel de subasta, optimización de resultados de búsqueda, compresión de cycle-time en inventario y títulos; tooling "empowered by current generation LLM technologies". `[VERIFICADO]` (thedrive earnings call)
- **Image recognition** para inspección/tasación de daño (scratches, dents, condición) que ayuda a las aseguradoras a totalizar coches "con más precisión". `[VERIFICADO]`
- **Modelo de ingresos (relevante para metodología de dato):** **PIP (Percentage Incentive Program)** — Copart cobra un % del precio final de subasta (~10% en alto valor, ~20% en viejo/dañado) + **fees al comprador** (la mayoría del service revenue) + **vehicle sales** (Cash For Cars, como principal) + en **DE/ES, listing fees a peritos** que usan la plataforma para determinar **valor residual** aunque el coche no se venda en Copart. `[VERIFICADO modelo / PARCIAL listing-fee DE-ES]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Web marketplace (SPA Angular)** | `copart.com` (US) + 10 dominios país (`copart.es`, `copart.co.uk`, `copart.de`, `copart.ca`, `copart.ie`, `copart.com.br`, MENA…). Vehicle Finder + AI Search + lotSearchResults + ficha | render `[VERIFICADO]` |
| **Apps móviles** | **Copart – Online Auto Auctions** (iOS/Android, member) + **Copart Seller Mobile** (con ProQuote para peritos) | Google Play/App Store `[VERIFICADO ×2]` |
| **Motor de subasta** | **VB3 (Virtual Bidding 3)**, ago-2013: navegadores modernos sin plugins, móvil, **Buy It Now**, **Make An Offer**, cuenta atrás dinámica; quitó el requisito de membresía para *ver* subastas | Wikipedia; anomalyinvestments `[VERIFICADO ×2]` |
| **Sales Data** | **Descarga CSV** (Inventory → Sales Data), login de miembro | copart.com `[VERIFICADO]` |
| **Condition Report** | PDF/email **<24 h**, $35, desde "Order Products & Services" de la ficha | shopusedcars `[VERIFICADO]` |
| **ProQuote / IntelliSeller / Title Express** | Integrados en la **plataforma de vendedor** (web + Seller Mobile + Lender Portal); **integración con sistemas core de aseguradoras** (One Inc. ClaimsPay) y partners (Hi Marley) | oneinc; worktruckonline `[VERIFICADO ×2]` |
| **Member dashboard ("Driver's Seat")** | Recomendaciones por preferencias, **voice search**, watchlist, **saved searches**, **vehicle alerts**, resultados de subasta | member-news; app stores `[VERIFICADO]` |
| **Brokers / Copart Dealer Services** | Compra vía brokers (viewbroker) para no-licenciados; CDS para dealers | render (viewbroker) `[VERIFICADO]` |
| **API / feed / integración** | **Integración B2B con aseguradoras/lenders** (claims systems, Lender Portal, partners). **API REST pública auto-servible NO documentada**; el dato masivo se obtiene por scraping de terceros (Apify/rebrowser) o por Sales Data/login | search `[PARCIAL]` |

---

## 6. Precio

> **Doble cara:** GRATIS-con-comisión para el **vendedor** (Copart cobra % + fees, no le cuesta listar) y **fees por compra** para el **comprador**. El dato (ERV, sale results, ProQuote) se entrega como **parte del servicio**, no como SKU suelto al público.

**Comprador (US, 2026):**

| Concepto | Importe | Estado |
|---|---|---|
| **Basic membership** | **$59/año** | feecalculator; fixnflip `[VERIFICADO]` |
| **Premier membership** | **$259/año** (permite pujar en todo, incl. dealer-only) | feecalculator `[VERIFICADO]` |
| **Buyer fee** (por tramos de puja) | $59 (<$500) → $99 ($500–999) → $179 → $199 → $299 → $399 → $449 → **$549 o % de la puja (lo mayor) si >$8.000** | feecalculator `[VERIFICADO]` |
| **Virtual bid fee** | **$99/vehículo** por pujar online | feecalculator; fixnflip `[VERIFICADO ×2]` |
| **Gate fee** | **$95** por compra (movimiento de almacén a carga) | fixnflip `[VERIFICADO]` |
| **Title fee** | **~$15–$75** (según estado) | feecalculator `[VERIFICADO]` |
| **Environmental fee** | **~$15** | search `[PARCIAL]` |
| **Storage fee** | **~$25–$50/día** tras periodo de gracia | feecalculator `[PARCIAL]` |
| **Condition Report** | **$35**/reporte | shopusedcars `[VERIFICADO]` |
| **UK volume tiers** | High Volume Member (≥12 veh./año UK+IE) vs Low Volume (≤11) | UK terms `[VERIFICADO]` |

**Vendedor:** **PIP** ~**10%** (alto valor) a **~20%** (viejo/dañado) del precio final + servicios. **DE/ES:** **listing fee** a peritos por uso de la plataforma para valoración residual. `[VERIFICADO modelo / PARCIAL %]`

> Importes exactos de buyer fees y PIP **varían por localización y tipo de miembro**; verificar contra el listing. ProQuote/IntelliSeller/Title Express: **precio B2B no público** (contrato con aseguradora). `[PARCIAL / NO-VERIFICADO B2B]`

---

## 7. Placement — dónde coloca cada dato en su UI (patrón a copiar por cardeep)

> Patrón rector: **el inventario se navega por un Vehicle Finder facetado + AI Search**; cada vehículo vive en una **tarjeta de lote ultra-densa** que ancla la decisión de puja, y la **ficha (VDP)** despliega specs/daño/fotos/CR. La **inteligencia de valoración (ProQuote/IntelliSeller)** NO vive en la web pública del comprador: vive en la **plataforma de vendedor/aseguradora** (Seller Mobile + Lender Portal + integración claims). El **ERV** es el ancla de valor visible al comprador; el **valor real** es el **Current Bid**.

**A. Vehicle Finder (landing de inventario).** Panel de filtros: Condition (All/Used/Salvage) · Types · **Odometer slider** · Year From/To · Damage type · Make · Model · Location (Location/State/Zip) · **VIN/Lot# lookup**. Arriba: **AI Search** unificado. Debajo: tabs (All/Salvage/Used) + **23 categorías destacadas** (Buy It Now, Run and Drive, Pure Sale, Wholesale Vehicles, EV, Hybrid, Exotics, Fleet/Lease, Bank/Repossessed…). `[VERIFICADO render]`

**B. Resultados (`lotSearchResults`) — tarjeta de lote (FICHA MÍNIMA, lo más valioso para cardeep).** Cada fila/tarjeta coloca, en orden: **foto** → **Year Make Model Trim** + **Lot #** + **Watch** + **iconos de condición** (Run and Drive / Engine Start Program / Enhanced Vehicles) → **Odometer** + **brand (ACTUAL)** + **Estimated Retail Value** → **Title type + code** (Salvage Title (ST-XX)) + **Primary Damage** + **Keys available** → **Location** (TX - CORPUS CHRISTI) + **Item #** → **estado de venta** ("Upcoming lot" / "Auction in 2D 6H 17min" + **Current bid: $X** + **Bid now** + **Details**). Panel izq.: **filtros con contadores** y **Sort by: Sale light**. `[VERIFICADO render]`

**C. Ficha de vehículo (VDP).** (SPA pesada; layout RECONSTRUIDO de fuentes + schema.) Galería **~10 fotos HD + vídeo de arranque** → bloque de **identidad/decode** (VIN, YMM, body, color, engine, cylinders, drive, transmission, fuel) → **Lot Details / Vehicle Information** (Odometer+brand, Primary/Secondary Damage, Title type+state, Keys, Run&Drive, **ERV**, Repair Cost, Highlights/announcements) → **Sale Information / Bid Information** (sale date/time/yard, item#, sale status, Current Bid, Buy It Now, Make An Offer, BID4U) → secciones de spec/equipamiento (technical specs, options, interior, safety, exterior, mechanical, entertainment) → **"Order Products & Services"** (Condition Report $35, history). `[RECONSTRUIDO — schema rebrowser/Apify + AutoBidMaster "Bid Information"/"Auction Vehicle Details" + CR]`

**D. ProQuote (plataforma de aseguradora / Seller Mobile).** El **perito** obtiene "a ProQuote" (salvage value estimate) en la app móvil durante la evaluación del siniestro → **decisión reparar vs. pérdida total**; **Preliminary ProQuote** da el valor predictivo con pocos datos. El valor se **descuenta del payout**. NO está en la web pública del comprador. `[VERIFICADO uso / PARCIAL UI]`

**E. IntelliSeller (dashboard de vendedor).** Recomendaciones de **minimum bid** y **re-auction** + **historical performance insights** integradas en el flujo de consignación del vendedor. `[VERIFICADO funcional / NO-VERIFICADO UI exacta]`

**F. Title Express (portal de aseguradora + Lender Portal).** Estado/tracking del título + **lienholder/loan payoff** (VIN-based matching, updates en tiempo real); el lender entra sus datos de payoff por el **Lender Portal**; integración con claims systems (One Inc.). `[VERIFICADO]`

**G. Member dashboard ("Driver's Seat").** Recomendaciones personalizadas + **voice search** + watchlist + saved searches + **vehicle alerts** + resultados de subasta. `[VERIFICADO]`

**H. Sales Data / Sales List.** Descarga **CSV** (Inventory → Sales Data) + run lists del día/semana (Auctions → Today's Auctions / Auction Calendar). `[VERIFICADO]`

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Volumen transaccional de salvamento líder mundial.** ~3,5–4 M veh./año, ~48% del mercado US, **>500.000 lotes vivos a diario**: la mayor base de **precio de martillo real de coche siniestrado** del planeta. `[VERIFICADO ×2]`
2. **ProQuote.ai — valoración de salvamento por visión+ML sobre decenas de millones de imágenes y millones de subastas.** Da a la aseguradora la decisión **reparar vs. total-loss en tiempo real**, antes y con menos variabilidad que el humano. Nadie con su base de imágenes+outcomes. `[VERIFICADO ×2]`
3. **IntelliSeller — optimización de venta cerrada sobre su propio dato** (minimum bid, re-auction, cycle-time). `[VERIFICADO]`
4. **Integración profunda en el flujo de siniestros del asegurador** (Title Express + Loan Payoff + Lender Portal + claims systems One Inc./Hi Marley): no es solo subasta, es **infraestructura de remarketing end-to-end**. `[VERIFICADO ×2]`
5. **Red física + digital propia** (>200–250 yards, >21.000 acres, posee >90% del suelo) → control del activo y del dato de condición. `[VERIFICADO]`
6. **Alcance exportador global** (compradores en 165–185 países; 90% de reconstruibles y 40% del inventario US comprado por internacionales). `[VERIFICADO ×2]`
7. **En DE/ES la plataforma ya se usa como herramienta de valoración residual por peritos** (listing fee aunque no se venda). `[PARCIAL]`
8. **Tarjeta de lote ultra-densa con ERV embebido** + AI Search + filtros con contadores + Sort by Sale light: UX de inventario madura. `[VERIFICADO render]`
9. **Powersports con guía de valor propia** (NPA Value Guide) además del coche. `[VERIFICADO]`
10. **Presencia directa en España (9 campas, 2016, +30%/año)** con aseguradoras top — pisa España como operador físico+digital, no solo como libro. `[PARCIAL ×múltiples]`

---

## 9. Gaps (lo que NO ofrece)

1. **NO es libro de valor.** No publica residual %, retail/trade/wholesale book, days-to-sell, market days supply, price-to-market %, índice de demanda/oferta ni curva de depreciación multi-anual. El "valor" es **precio de subasta crudo + ERV aportado por el vendedor + ProQuote (salvamento, no retail)**. No compite con KBB/Black Book/cap/Eurotax/Autovista/J.D. Power. `[VERIFICADO por ausencia]`
2. **ERV no es valoración propia** — lo aporta el vendedor; puede estar inflado/desfasado. No es un valor de mercado calculado por Copart. `[VERIFICADO]`
3. **No es valoración de coche sano/retail al consumidor.** ProQuote valora **salvamento** para la aseguradora, no precio de venta retail de un coche en buen estado. `[VERIFICADO]`
4. **Sin valor de coche NUEVO / MSRP / equipamiento estructurado tipo build-data** como producto de dato (el build sheet es input de la ficha, no un SKU). `[VERIFICADO por ausencia]`
5. **Vehicle history NO propio** — depende de partners/terceros (no es Carfax/AutoCheck). `[PARCIAL]`
6. **Inteligencia de valoración (ProQuote/IntelliSeller) NO accesible al público** — es B2B con aseguradoras; el comprador minorista no la ve. `[VERIFICADO]`
7. **API pública auto-servible no documentada.** El dato masivo se consigue por scraping de terceros (Apify, rebrowser, stat.vin, bidfax) o por Sales Data tras login. `[PARCIAL]`
8. **Web SPA con anti-bot + login-gating** (VIN, ERV, high bid, BIN, seller, imágenes marcados `[Premium]`): no es fuente limpia/estable para ingestión directa; la ficha (VDP) ni siquiera hidrató en render headless. `[VERIFICADO]`
9. **Scope = salvamento/siniestro + usado wholesale, B2B-first.** No indexa la huella digital de **puntos de venta/concesionarios** (categoría de cardeep); es marketplace de inventario, no censo de dealers. `[VERIFICADO]`
10. **AutoGrade no es propietario** (es estándar Manheim/NAAA); Copart lo expone con relleno bajo (2%). `[VERIFICADO]`
11. **Precios B2B opacos** (ProQuote, IntelliSeller, Title Express, PIP%, listing fees DE/ES): todo contrato. `[NO-VERIFICADO importes]`
12. **Cifras macro variables entre fuentes** (miembros, países 165/185/190, veh./año 3 vs 4 M) — marketing vs analista vs 10-K. `[PARCIAL]`

---

## 10. Fuentes (URLs)

**Render en vivo (Playwright, 2026-06-30):**
- https://www.copart.com/vehicleFinder — Vehicle Finder: AI Search, filtros (Condition/Types/Odometer/Year/Damage/Make/Model/Location/VIN-Lot#), 23 Featured items, facetas (title type/states/makes/damage).
- https://www.copart.com/lotSearchResults?free=true&query=honda — **tarjeta de lote real** (YMM+Trim, Lot#, iconos Run and Drive/Engine Start/Enhanced, Odometer+ACTUAL, **Estimated Retail Value**, Title type+code "Salvage Title (ST-CT)", Primary Damage, Keys, Location, Item#, "Auction in 2D 6H 17min", "Current bid: $0.00USD", Bid now); filtros con contadores (Clean Title (1.000+), Salvage Title (10.000+)); **Sort by: Sale light**.
- https://www.copart.com/lot/99993045/... — ficha (VDP): SPA Angular no hidratada en headless (main vacío, placeholders `{{::locale...}}`) → layout RECONSTRUIDO.

**Identidad / corporativo / financiero:**
- https://en.wikipedia.org/wiki/Copart — fundación 1982 Willis Johnson, IPO 1994 $12, HQ Dallas 2012, 11 países, VB2/VB3, NER 1995, NPA 2017, AVK 2018, Cash For Cars, FY2025 ($4,65B/op $1,69B/net $1,55B/11.600 empleados).
- https://www.forbes.com/profile/willis-johnson/ — fundador.
- SEC 10-K FY2025 (vía) https://www.publicnow.com/view/DFD4F7A7BB9459AD0129D58236D158E49526742E + https://last10k.com/sec-filings/cprt/0001628280-25-042946.htm — revenue $4.646.958k (service $3.968.662k + vehicle sales $678.296k), +11,4%, US +$325,5M / Intl +$82,2M, op income 36%. (SEC directo dio 403 en WebFetch.)
- https://www.copart.com/content/copart-ceo-lettertostockholders-2025.pdf — carta a accionistas FY2025.
- https://anomalyinvestments.substack.com/p/copart-the-oldest-fleet-in-history — modelo (PIP 10–20%, buyer fees), VB3 (ago-2013, Buy It Now/Make An Offer), insurance 80–90%, ~1M miembros/165 países, intl 90% reconstruibles + 40% inventario US, 250 yards/21.000 acres/>90% suelo, cuota ~48%, **ProQuote.ai**, **IntelliSeller**, **listing fees a peritos en DE/ES para valor residual**.

**Productos / inteligencia / IA:**
- https://www.repairerdrivennews.com/2023/02/22/copart-co-ceo-says-total-losses-now-going-back-up... — ProQuote (cuándo/cuándo no totalizar).
- https://www.tikr.com/blog/copart-stock-has-dropped-36... — **ProQuote.ai** (computer vision + ML, decenas de M imágenes + M de subastas, borderline total losses).
- https://www.thedrive.com/news/even-the-junkyard-is-using-ai-now — Jeff Liaw: AI en pricing/total-loss/soporte/recomendaciones/búsqueda; "millions of similar vehicles... LLM technologies"; IntelliSeller historical insights.
- https://pitchgrade.com/companies/copart-ai-use-cases — IntelliSeller (minimum bid, re-auction).
- https://www.oneinc.com/resources/news/faster-lienholder-payments-one-inc-and-copart-lead-the-way... — **Title Express + Loan Payoff** + ClaimsPay, VIN-based matching, Lender Portal, ~1M miembros / 185+ países.
- https://www.worktruckonline.com/news/copart-and-one-inc-partner-to-improve-auto-claims-process — Title Express, total loss packet, lienholder calls.
- https://www.copart.com/content/us/en/landing-page/copart-title-express — landing Title Express (SPA).
- https://www.avvo.com/legal-answers/my-insurance-company-is-deducting-a-salvage-proquo-2855108.html — uso real: "salvage ProQuote" descontado del payout.

**Campos atómicos / schema:**
- https://github.com/rebrowser/copart-dataset — **dataset (2.137.389 reg., ~55 columnas con fill rate)**: lotId, vin[P], year, make, modelGroup, modelDetail, trim, bodyStyle, exteriorColor, engine, cylinders, drivetrain, transmission, fuelType, damageDescription, secondaryDamage, lotCondCode, runsDrives, saleTitleState, saleTitleType, hasKeys, yardNumber/Name, saleDate/DayOfWeek/Time/TimeZone, itemNumber, vehicleType, saleStatus, mileage, odometerBrand, estRetailValue[P], repairCost, highBid[P], buyItNowPrice[P], location*, gridRow, offsite*, currencyCode, specialNote, makeOfferEligible, rentals, wholesale, sellerName[P], saleLight, autoGrade, announcements, image*[P], listingUrl[P]. Update diario.
- https://apify.com/parseforge/copart-public-search-scraper — **168 campos/lote** (36 nombrados): imageUrl, lot_number, year, make, model, trim, vin, item_url, sale_status, current_bid, buy_it_now_price, estimated_retail_value, auction_date, sale_location, lat/long, zip, primary_damage, secondary_damage, odometer(+unit), color, engine, transmission, drive, fuel, title_code, keys, run_and_drive, accident_score, build_sheet, images(+high_res), engine_video_high_res; +"lot flags, dynamic bid state, seller metadata, title group, yard codes, service order type" (~132 más).
- https://webscraper.io/blog/how-to-scrape-copart-vehicle-listings — secciones HTML: vehicle_assessment, technical_specifications, options, styles, engines, interior, safety, exterior, mechanical, entertainment; campos auto_grade_score, lane_Item, notes.
- https://support.copart.co.uk/faq/what-do-copart-terms-mean/ — BID4U, Monster Bid, Current Bid, Lot#, Item#, VIN, Engine, Drive, **ERV** (del vendedor), **Repair Cost**, Sale status (Pure Sale/On Approval/Minimum Bid), damage codes, Operation Centres, Sale Date, **VAT**, Current Sale Highlights, High/Low Volume Member.
- https://support.copart.co.uk/faq/vehicle-types-and-grading/ + https://www.abi.org.uk/.../codepracticecategorisationmotorisedvehiclesalvagemay2025.pdf — **Cat A/B/S/N** (ABI; Cat B requiere licencia).
- https://helpcenter.autobidmaster.com/hc/en-us/articles/360020781991-Estimated-Retail-Value — ERV (provisto por el vendedor) + secciones "Bid Information"/"Auction Vehicle Details" (403 en fetch; vía búsqueda).
- https://shopusedcars.org/copart/getting-started/how-to-order-a-copart-vehicle-condition-report/ — **CR $35**, "Order Products & Services", <24h, campos (name/make/model, registration, color, body/engine condition, owner).

**España / Europa:**
- https://www.copart.es/ + https://www.copart.es/vehicleFinder — operación ES.
- https://segurosnews.com/.../eric-manas-copart-... — **>1.500 veh./mes, +30%/año**, modelo de cesión de salvamento, línea de desguace, digitalización docs, Eric Mañas.
- https://soymotor.com/coches/noticias/ganar-dinero-con-coches-averiados-y-siniestrados-las-subastas-de-copart + https://ae-renting.es/.../copart-lider-mundial... — desde 2016, 9 campas (Sevilla/Madrid/Tarragona/Lugo/Albacete/Mallorca/La Rioja/Tenerife/Gran Canaria), martes/jueves 11:00, aseguradoras (Allianz, AXA, Mutua, Admiral, Generali, Helvetia, Reale, Consorcio), +29.000 veh.

**Powersports / marcas:**
- https://www.crashedtoys.com/ + https://www.crashedtoys.com/content/us/en/member-news/copart-acquires-national-powersport-auctions — CrashedToys (powered by Copart), **NPA/Cycle Express** (2017; Atlanta/Cincinnati/Dallas/Philadelphia/San Diego); https://www.npauctions.com/cp/crashed-toys — **NPA Value Guide**.

**Pricing:**
- https://feecalculator.pro/copart-buyer-fees/ + https://fixnflipgarage.com/blog-post/overview-of-copart-fees/ — Basic $59 / Premier $259, buyer fee tiers $59→$549+, virtual bid $99, gate $95, title $15–75, environmental ~$15, storage $25–50/día.

**Sales Data:**
- https://www.copart.com/content/us/en/buyer/sales/download-sales-data — "CSV Sales Data" (login miembro; SPA, columnas reconstruidas del dataset).

### Notas de verificación / método
- **exa MCP NO disponible** en el entorno (ToolSearch "exa…" sólo devolvió gbrain/claude-mem/Gmail/Drive/logo/WebFetch/WebSearch + Playwright). Investigación con **WebSearch + WebFetch + Playwright (render)**. `[NOTA DE MÉTODO]`
- **Páginas SPA/403/cert-roto:** copart.com (aboutCopart 404; landing pages = Angular con `{{::locale.messages}}`), SEC 10-K directo (403), AutoBidMaster/cleaned.vin/carfast.express/autoastat (403), maxmotorsmissouri (cert mismatch). Datos tomados de fuentes equivalentes verificadas o de render Playwright.
- **"Co.ai":** marca paraguas mencionada por **1 sola fuente secundaria**; la búsqueda dirigida no la corroboró. **Marcado [NO-VERIFICADO]**. La marca verificada de valoración es **ProQuote / ProQuote.ai**.
- **Lot detail (VDP) layout:** la ficha SPA no hidrató en render headless → **[RECONSTRUIDO]** a partir del schema (rebrowser/Apify) + descripciones de terceros + la tarjeta de lote (sí verificada en vivo). La tarjeta de lote y el Vehicle Finder son **[VERIFICADO render]**.
- **Cifras variables** (miembros ~1M; países 165/185/190; veh./año 3–4M; veh. ES 29k acumulado / 1.500 mes): se citan con su fuente y rango; no se fuerza un número único.
