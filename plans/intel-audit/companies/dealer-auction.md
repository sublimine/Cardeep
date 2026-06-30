# Dealer Auction — Auditoría atómica

> Slug: `dealer-auction` · Subdominio cardeep: **wholesale-intelligence** · Región: **Reino Unido** (exclusivo) — sin presencia internacional
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (marketing del vendedor sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato de varias páginas sin que lo listen literal), `[NO-VERIFICADO]`.
> Naturaleza: **marketplace de subasta MAYORISTA (wholesale) trade-to-trade 100% DIGITAL de coche/furgoneta USADA en UK**, NO un libro de valor ni un proveedor de datos primario. Su ventaja es de **distribución de inteligencia ajena**: es una **JV 50/50 entre Cox Automotive (Manheim, wholesale físico/digital) y Auto Trader (el dato retail de consumo más grande de UK)**, y su moat es **inyectar el dato retail LIVE de Auto Trader (Retail Rating, Days to Sell, market average, margen potencial) dentro de cada lote de subasta wholesale**, de modo que el comprador trade ve *cómo rendirá el coche en su forecourt* antes de pujar. El dato NO es propio: Retail Rating / valoración / días-a-vender son **propiedad de Auto Trader** (licenciados); la condición/grading viene del lado **Manheim/NAMA**.
> Productos de "inteligencia" hacia el mercado: (1) el **propio marketplace** con la capa de datos Auto Trader sobre cada listing; (2) **Retail Margin Monitor (RMM)** — índice mensual público de margen retail potencial por modelo/marca; (3) **EV Performance Review (EVPR)** — índice mensual de rendimiento EV/híbrido wholesale; (4) **"Under the Hood"** — balance trimestral/anual de rendimiento de plataforma; (5) **Stock Policy + Alerts** — emparejamiento automático de stock; más **integraciones** de funding (NextGear Capital), logística (Movex) y rutas de venta retail (Auto Trader, Motors.co.uk).
> Sitio único: `www.dealerauction.co.uk` (marketplace + blog/insights). **El "subdominio wholesale-intelligence" es el bucket de taxonomía de cardeep, NO una propiedad web viva de la empresa**: `wholesale-intelligence.dealerauction.co.uk` **no resuelve en DNS** (sin registros A/AAAA) y `/wholesale-intelligence/` devuelve **HTTP 404** (verificado por `nslookup` + `curl`, 2026-06-30). `[VERIFICADO por ausencia]`

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **Dealer Auction** | dealerauction.co.uk `[VERIFICADO]` |
| Razón social | **Dealer Auction Limited**, company number **11514206**, Inglaterra y Gales | about-us; Companies House (nº de registro) `[VERIFICADO]` |
| Owner / grupo | **JV 50/50** entre **Cox Automotive (Europe)** y **Auto Trader UK** — empresa independiente con dos matrices | manchesterdigital; am-online; motorfinanceonline; fleetnews; coxautoinc.eu; about-us `[VERIFICADO ×2+]` |
| Anuncio de la JV | **16 ago 2018** | manchesterdigital; am-online; motortrader `[VERIFICADO ×2]` |
| Lanzamiento operativo | **enero 2019** | plc.autotrader.co.uk press; am-online `[VERIFICADO ×2]` |
| HQ | **Central House, Leeds Road, Rothwell, Leeds, West Yorkshire, LS26 0JE** | about-us `[PARCIAL]` |
| CEO (histórico) | **Le Etta Pearce** (con roles previos en Auto Trader y Cox) | búsqueda JV 2018/2019 `[PARCIAL — posiblemente desactualizado a 2026]` |
| Posición declarada | **"the UK's leading remarketing platform"** / **"the UK's smartest digital wholesale marketplace"** | about-us; dealerauction.co.uk `[CLAIM-VENDOR]` |
| Lema | **"Sell faster. Buy smarter."** | dealerauction.co.uk `[VERIFICADO]` |

**Plataformas predecesoras consolidadas (la JV fusionó 3 negocios en una sola plataforma):**

| Plataforma | Origen | Qué aportó | Fuente |
|---|---|---|---|
| **dealer-auction.com** | lanzada **2009**; adquirida por **Manheim 2012** | marketplace trade-to-trade (≈120.000 vehículos/año en 2019) | about-us; am-online `[VERIFICADO]` |
| **Manheim Online** | Cox/Manheim | ventas digitales de **fabricantes y flotas**, ventas cerradas y alcance nacional | about-us; am-online `[VERIFICADO]` |
| **Smart Buying** (ex **Autotrade-mail**) | Auto Trader | plataforma retailer-to-retailer con **data insights sobre los listings** | about-us; manchesterdigital `[VERIFICADO ×2]` |

**Estadísticas de escala (oficiales DA, con fecha):**

| Métrica | Valor | Fuente / fecha |
|---|---|---|
| Vehículos disponibles en cualquier momento | **hasta 60.000** | búsqueda coxautoinc/about `[PARCIAL]` |
| Vehículos frescos añadidos / mes | **~11.000** | dealerauction.co.uk (home) `[PARCIAL]` |
| Subastas que terminan al día | **600+** | dealerauction.co.uk; buy-fast-buy-smart `[VERIFICADO ×2]` |
| Compradores trade activos | **5.000+** | dealerauction.co.uk; sellers `[VERIFICADO ×2]` |
| Vendedores registrados | **4.000+** | dealerauction.co.uk `[PARCIAL]` |
| **2024 — valor retail transaccionado** | **£510 M** | under-the-hood-2024; búsqueda `[VERIFICADO ×2]` |
| 2024 — pujas | **919.164** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — alertas enviadas | **11,5 M** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — beneficio trade generado | **£13 M** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — precio medio de venta | **£6.378** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — días medios a vender | **4 días** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — CAP Clean medio / pico | **103% / 128%** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — edad media / km medios | **8,9 años / 72.598 mi** | under-the-hood-2024 `[VERIFICADO]` |
| 2024 — cuota AFV | **3,44% (2023) → 5,6% (2024)** | under-the-hood-2024 `[VERIFICADO]` |
| **Q1 2026 — valor retail** | **£156 M** (récord) | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — pujas | **223.376** | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — alertas | **12 M** | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — beneficio trade | **£4,1 M** (2º mejor trimestre) | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — precio medio venta | **£7.684** (récord) | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — CAP Clean medio | **105%** | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — días a vender | **2,74 días** (récord rapidez, subasta digital natural) | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — edad / km medios | **7 años / 54.595 mi** | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2026 — cuota EV / híbrido | **2,56% / 9,81%** (récord) | under-the-hood-2026-q1 `[VERIFICADO]` |
| Q1 2025 — beneficio trade | **£5,5 M** (+65% YoY) | búsqueda RMM `[PARCIAL]` |

**Categorías de producto:** (1) **Marketplace de subasta wholesale digital** (timed / same-day / buy-it-now / make-me-an-offer; red abierta y cerrada); (2) **Capa de inteligencia retail sobre cada listing** (dato Auto Trader: Retail Rating, Days to Sell, market average, margen estimado); (3) **Índices/insight publicados**: Retail Margin Monitor (mensual + anual), EV Performance Review (mensual), "Under the Hood" (trimestral/anual); (4) **Stock Policy + Alerts** (emparejamiento automático); (5) **Servicios integrados**: funding (NextGear Capital), logística (Movex), rutas de venta (Auto Trader / Motors.co.uk), enlace de cuenta Manheim.

**Cliente objetivo:** **dealers trade** (franquiciados e independientes, compra/venta wholesale) + **vendedores institucionales**: **OEMs/fabricantes** (Hyundai Motor UK, Volkswagen, Renault, Nissan — confirmados), **flotas y leasing**, **casas de subasta**, y **stock de consumo** (part-ex) canalizado vía dealers. Requisito de cuenta: **número de IVA válido + comerciante de motor a tiempo completo**. (Fuentes: hyundai news; buyers; sellers; 30-day-free-trial. `[VERIFICADO ×2]`)

---

## 2. Cobertura

- **Geografía:** **Reino Unido, exclusivo.** Sin marketplace ni dato fuera de UK (a diferencia del Manheim/Cox global). **Sin España, sin Europa continental.** ← hueco total para cardeep. `[VERIFICADO por ausencia]`
- **Nuevo vs usado:** **USADO/wholesale**, núcleo absoluto. No es libro de coche nuevo ni MSRP. `[VERIFICADO]`
- **Tipos de vehículo:** **turismos (cars) + furgonetas / LCV (vans)**. ("Buy used cars and vans online | wholesale marketplace"). No motos. `[VERIFICADO]`
- **Naturaleza del dato (clave):** **dato transaccional de subasta real** (precio de martillo del propio marketplace, CAP performance) **+ dato retail LIVE licenciado de Auto Trader** (Retail Rating, Days to Sell, market average, demanda/oferta de consumo) **+ condición física** (condition report / grading estilo Manheim-NAMA). **No genera dato de valor propio**: la valoración y el rating son de Auto Trader; DA es la **superficie de distribución**. `[VERIFICADO]`
- **Frescura / profundidad:** el dato Auto Trader es **diario y live** (Auto Trader observa **1,3 M+ vehículos/día**, ~**500.000 listings trade/día** para valoración, ~**20.500 cambios de precio/día**); la subasta es de duración corta (la mayoría termina el mismo día → 2,74 días medios a vender en Q1'26). Los índices RMM/EVPR se recalculan **al inicio de cada mes** sobre la ventana del mes natural anterior. `[VERIFICADO ×2]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **Marketplace (listing/VDP)** | Lote de subasta con datos del vehículo + capa Auto Trader + panel de puja | Ficha por VIN/lote con rating, días-a-vender, margen, condición | ~30 |
| **Capa de inteligencia Auto Trader** | Dato retail live inyectado en cada listing | Retail Rating + Days to Sell + market average + margen estimado | ~7 |
| **Retail Margin Monitor (RMM)** | Índice mensual+anual de margen retail potencial por modelo/marca | Tabla modelo/marca: margen £, unidades, edad, km, días, rating | ~8 |
| **EV Performance Review (EVPR)** | Índice mensual de rendimiento EV/híbrido/AFV wholesale | Tabla: margen, precio venta, volumen, CAP%, edad, km, días | ~9 |
| **"Under the Hood"** | Balance trimestral/anual de plataforma | KPIs agregados de plataforma | ~14 |
| **Stock Policy + Alerts** | Emparejamiento automático de stock al perfil del comprador | Alertas por email de lotes que cumplen política | ~5 |
| **Mecánica de subasta** | Formatos de compra/venta | Bid/proxy/buy-now/make-offer, reserva, fees | ~10 |

### 3.1 Marketplace — campos por vehículo/lote (núcleo de la UI)

> Cada lote es una ficha por vehículo. Combina **datos declarados del vehículo** (vendedor) + **condición** + **capa de inteligencia Auto Trader** + **estado de subasta**.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Make** | Marca | buy-fast-buy-smart; RMM `[VERIFICADO]` |
| **Model** | Modelo | RMM; EVPR `[VERIFICADO]` |
| **Derivative / variant** | Versión/acabado | a-guide-to-buy (filtros) `[PARCIAL]` |
| **Registration year / age** | Año de matrícula / edad | buy-fast-buy-smart (orden por edad) `[VERIFICADO]` |
| **Mileage** | Kilometraje | buy-fast-buy-smart; 8-top-tips `[VERIFICADO]` |
| **Fuel type** | Combustible (petrol / diesel / EV / PHEV / HEV) | a-guide-to-buy; EVPR `[VERIFICADO]` |
| **Colour** | Color | under-the-hood-2024 (black/white/grey) `[VERIFICADO]` |
| **Images (count)** | Nº de fotos del lote — **2-5 fotos → 4,1 pujas; 11-20 fotos → 8,2 pujas** | double-bids-with-images `[VERIFICADO]` |
| **Condition report** | Reporte de condición: **daños, testigos de advertencia, equipamiento faltante, advisories de MOT** | 8-top-tips; double-bids-with-images `[VERIFICADO]` |
| **NAMA grade** | Grado de condición estilo NAMA (5 grados; "retail-ready" ≈ grado 4.0+) — DA heredó Manheim Online y enlaza cuentas Manheim | búsqueda NAMA/Manheim; sellers `[RECONSTRUIDO — condition report VERIFICADO; label NAMA inferido del linaje Manheim]` |
| **MOT status / advisories** | Estado de ITV y advertencias | 8-top-tips `[VERIFICADO]` |
| **V5 document** | Presencia del permiso de circulación (logbook) | 8-top-tips `[VERIFICADO]` |
| **Service history / service book** | Historial de mantenimiento | 8-top-tips `[VERIFICADO]` |
| **Previous owners / ownership history** | Nº de propietarios / historial | 8-top-tips `[VERIFICADO]` |
| **Pet-free / smoke-free status** | Atributos de uso (sin mascotas / sin humo) | 8-top-tips `[VERIFICADO]` |
| **Special features / equipment** | Equipamiento (sat-nav, asientos calefactables…) | 8-top-tips `[VERIFICADO]` |
| **Seller location** | Ubicación del vendedor | a-guide-to-buy (orden por distancia) `[VERIFICADO]` |
| **Distance from buyer (radius)** | Distancia al comprador; **el rating se calcula en radio de 50 millas** | a-guide-to-buy; streamlining-sourcing `[VERIFICADO ×2]` |
| **Stand-in value** | Valor interno del vendedor para fijar reserva | 8-top-tips `[VERIFICADO]` |
| **Reserve price** | Precio de reserva (recomendado **95-96% de CAP**; fijarlo bien **+20% de prob. de venta**) | 8-top-tips; a-guide-to-buy `[VERIFICADO ×2]` |
| **Description (estructurada)** | **overview + exterior condition + interior condition + terms** | 8-top-tips `[VERIFICADO]` |

### 3.2 Capa de inteligencia Auto Trader (overlay sobre cada listing — el moat)

> Lo que diferencia a DA de una subasta wholesale "ciega": cada lote lleva el **dato retail live de Auto Trader** que predice cómo rendirá el coche en el forecourt del comprador. **El dato es propiedad de Auto Trader (licenciado), no de DA.**

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Autotrader Retail Rating** | Puntuación **1-100** de "desirability" del vehículo basada en **demanda, oferta y días-a-vender**, ajustada por **ubicación del forecourt** (radio 50 mi). No cambia con el precio (mide el potencial a precio de mercado). Surfaced en listing y como criterio de orden | buy-fast-buy-smart; help.autotrader (vía búsqueda); RMM (valores 33,7-74,1) `[VERIFICADO ×2]` |
| **Days to Sell** | Días estimados que el vehículo tardará en venderse (forecast) | buy-fast-buy-smart; a-guide-to-buy `[VERIFICADO ×2]` |
| **Auto Trader market average / Retail Price** | Valoración media de mercado retail (make/model/derivative/edad/km, ajustada por extras) — base del cálculo de margen | RMM (metodología); price-to-live-market `[VERIFICADO ×2]` |
| **Estimated / potential retail margin (£)** | Margen potencial = **precio de venta wholesale vs market average de Auto Trader** | a-guide-to-buy; RMM `[VERIFICADO ×2]` |
| **Consumer demand** | Demanda nacional en Auto Trader **últimos 7 días vs últimos 6 meses** (componente del rating) | búsqueda Retail Rating `[VERIFICADO]` |
| **Live retail supply** | Volumen de vehículos similares en Auto Trader (componente del rating) | búsqueda Retail Rating `[VERIFICADO]` |
| **Price Indicator (label)** | Etiqueta retail de Auto Trader: **Great / Good / Fair / Higher / Lower price** + variación £ vs valoración | búsqueda Auto Trader Price Indicator `[PARCIAL — feature de Auto Trader; no confirmado que se muestre literal en la UI de DA]` |

### 3.3 Retail Margin Monitor (RMM) — índice mensual+anual de margen retail

> Índice público mensual (también roundup anual) que convierte el dato transaccional de DA en un ranking de **beneficio retail potencial por modelo/marca**. Es el producto de "wholesale intelligence" hacia el mercado/prensa.

**Metodología (verbatim, consistente en varias ediciones):** *"We track models meeting two key criteria: more than 20 units sold with a retail price of less than £10,000 (we also track any standout models that retail at more than £10,000). We then compare the sold price for each model with the Autotrader market average to reveal the potential margin. For the brand table, we compare models with more than 50 units sold."* Ventana = **mes natural (1-31)**, procesado **al inicio de cada mes**. `[VERIFICADO ×2]`

| Campo atómico (columna del índice) | Definición | Fuente |
|---|---|---|
| **Make / Model** | Identidad del modelo rankeado | rmm-may-2026; nov-2025 `[VERIFICADO]` |
| **Retail margin (£)** | Margen retail potencial (sold price vs Auto Trader market average) | todas las ediciones RMM `[VERIFICADO ×2]` |
| **Units sold** | Unidades vendidas (umbral **>20 modelo / >50 marca**) | metodología RMM `[VERIFICADO]` |
| **Average vehicle age** | Edad media (top-10 sub-£10k ≈ 10 años) | nov-2025 `[VERIFICADO]` |
| **Average mileage** | Km medios | rmm-may-2026 `[VERIFICADO]` |
| **Days to sell / days to retail** | Días a vender por modelo (30-40 días según modelo) | nov-2025 `[VERIFICADO]` |
| **Autotrader Retail Rating** | Rating del modelo (ej. Ford Kuga 74,1) | 2025-annual-round-up; nov-2025 `[VERIFICADO]` |
| **Engine / fuel type** | Diésel / gasolina / híbrido | rmm-may-2026 `[VERIFICADO]` |
| **Price bracket** | **Sub-£10.000** y **Over £10.000** (más límite global histórico £25.000) | rmm-may-2026; nov-2025 `[VERIFICADO]` |
| **Total retail value / trade profit** | Agregados mensuales (ej. RMM mar-2026: £52,6 M valor retail) | news headlines `[PARCIAL]` |

### 3.4 EV Performance Review (EVPR) — índice mensual EV/híbrido

> Feature mensual (lanzado **may-2024**) que sigue el rendimiento de **EV, híbrido y AFV** en la plataforma.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Make / Model** | Modelo EV/híbrido rankeado | evpr ago-2024 `[VERIFICADO]` |
| **Average retail margin (£)** | Margen retail medio AFV (ej. may-2026: £3.130) | evpr-may-2026 `[VERIFICADO]` |
| **Average sold price (£)** | Precio medio de venta (ej. may-2026: £13.844) | evpr-may-2026 `[VERIFICADO]` |
| **Sales volume / growth %** | Volumen y crecimiento (AFV +35% YoY; EV +78% mar-2026) | evpr ago-2024; news `[VERIFICADO ×2]` |
| **CAP Clean performance (%)** | % logrado sobre CAP Clean (top-10 ≈ 101,3%; Kia Niro 109,6%) | evpr ago-2024 `[VERIFICADO]` |
| **Conversion rate** | Tasa de conversión EV/híbrido (MoM/YoY) | evpr ago-2024 `[VERIFICADO]` |
| **Average age / mileage** | Edad media (4,1-5,5 años) / km (38.224-41.017) | evpr ago-2024; may-2026 `[VERIFICADO]` |
| **Days to sell** | Días a vender por modelo (Prius 29 / Leaf 52,5) | evpr ago-2024 `[VERIFICADO]` |
| **Bids (per vehicle / total)** | Pujas recibidas (vs media YTD) | evpr ago-2024 `[VERIFICADO]` |
| **Fuel-type split (EV/PHEV/HEV)** | Reparto por tipo de combustible alternativo | evpr ago-2024; may-2026 `[VERIFICADO]` |
| **Autotrader Retail Rating** | Rating del modelo (ej. Leaf 33,7) | evpr ago-2024 `[VERIFICADO]` |

### 3.5 "Under the Hood" — balance de plataforma (trimestral/anual)

> KPIs agregados de toda la plataforma (no por modelo). Campos atómicos: `bids placed` · `stock alerts sent` · `total retail value transacted (£)` · `estimated trade profit (£)` · `average sold price (£)` · `average CAP Clean performance (%) + peak` · `average days to sell` · `average vehicle age` · `average mileage` · `EV share (%)` · `hybrid share (%)` · `AFV share (%)` · `top models by CAP Clean` · `top models by margin`. (Fuentes: under-the-hood-2024; under-the-hood-2026-q1. `[VERIFICADO ×2]`)

### 3.6 Mecánica de subasta + Stock Policy

- **Formatos de compra:** **Timed auction** (puja en vivo, incrementos **£50 / £100 / £200**) · **Proxy / Maximum bid** ("set your maximum bid up front" — puja automática en incrementos de £50 hasta el máximo) · **Buy It Now** (precio fijo, compra inmediata) · **Make Me an Offer** (sobre **Retail Ready listings**; el vendedor acepta/rechaza/contraoferta hasta **5pm del día de fin**). `[VERIFICADO ×2]`
- **Formatos de venta:** **same-day / timed / buy-now**; **red abierta** (todo el mercado) o **red cerrada** (ventas OEM dirigidas a la red franquiciada). `[VERIFICADO]`
- **Stock Policy + Alerts:** el comprador define una política de stock → filtra miles de vehículos con un clic → recibe **alertas automáticas** de lotes que cumplen; **recomendaciones inteligentes** basadas en su **forecourt de Auto Trader + actividad de puja reciente**. `[VERIFICADO ×2]`
- **Orden/filtros del listado:** ending soonest (default) · newly listed · **Autotrader Retail Rating** · price (low/high) · age · distance · **average days to sell**. `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Dato retail = Auto Trader (licenciado).** El Retail Rating (1-100), Days to Sell, market average y margen estimado **son propiedad de Auto Trader**, no de DA. Auto Trader observa **1,3 M+ vehículos/día**, ~**500.000 listings trade/día** para valoración, ~**20.500 cambios de precio/día**, sobre Auto Trader + 3.000+ webs de retailers + forecourts + OEM/fleet/leasing + casas de subasta. `[VERIFICADO ×2]`
- **Retail Rating — cálculo:** desirability basada en **speed-of-sale nacional + condiciones de mercado (oferta y demanda)**, ajustada por **ubicación del forecourt**; **demanda** = actividad de consumidor últimos 7 días vs 6 meses; **no varía con el precio** (mide potencial a precio de mercado). `[VERIFICADO ×2]`
- **Dato wholesale = Cox/Manheim.** Transacción de subasta real (precio de martillo), **CAP Clean performance** (% logrado sobre el "libro" CAP), enlace de cuenta Manheim, grading de condición estilo **NAMA** (5 grados, "retail-ready" 4.0+). `[VERIFICADO]` (label NAMA en DA: `[RECONSTRUIDO]`)
- **Valoración market average (Auto Trader):** combina/analiza ~500.000 listings trade/día; ajusta por **make/model/derivative/edad/km + extras opcionales**; expresa variación en £ vs valoración (Price Indicator). `[VERIFICADO ×2]`
- **RMM:** sold price vs Auto Trader market average; umbral >20 unidades/modelo, >50/marca; ventana mensual. `[VERIFICADO ×2]`
- **Calidad del listing como señal:** nº de imágenes correlaciona con pujas (2-5 → 4,1; 11-20 → 8,2); **87%** de dealers valoran imágenes de calidad, **89%** se guían por el condition report. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Marketplace web** | `www.dealerauction.co.uk` — subasta digital 24/7, 600+ subastas/día; bid / buy-now / make-offer / proxy. (App móvil: probable pero no confirmada explícitamente → `[NO-VERIFICADO]`.) |
| **Ingesta de stock** | **API upload** · **data feed integration** · **CSV upload** (gestión de stock del vendedor). Es ingesta, **no** una API de consumo de datos. |
| **Stock Alerts (email)** | Alertas automáticas policy-matched al comprador. |
| **Insight / índices (web)** | Retail Margin Monitor (mensual + anual), EV Performance Review (mensual), "Under the Hood" (trimestral/anual) — publicados como artículos en `/retail-margin-monitor/`, `/ev-performance-review/`, `/blog/`. |
| **Integraciones financieras/logísticas** | **NextGear Capital** (floorplan/funding), **Movex** (logística/transporte), **enlace cuenta Manheim**, **DID number** de Auto Trader. |
| **Rutas de salida retail** | Listado en **Auto Trader** y **Motors.co.uk** (acceso a listings de consumo integrado). |
| **Pago al vendedor** | **Cash en 5 días** tras la venta. |
| **Soporte/registro** | `/sign-up/`, `/30-day-free-trial/`, `/contact-us/`. |

---

## 6. Precio (parcialmente descubierto)

| Concepto | Precio | Fuente / nota |
|---|---|---|
| **Suscripción mensual** | **£99/mes + IVA** (tras la prueba) | 30-day-free-trial; buyers; búsqueda `[VERIFICADO ×2]` |
| **Suscripción anual** | **£199/año + IVA** (facturado en enero; prorrateado si entras a mitad de año) | 30-day-free-trial `[PARCIAL]` |
| **Prueba gratuita** | **30 días** | múltiples páginas DA `[VERIFICADO ×2]` |
| **Promo independientes** | **Primera venta gratis cada mes** (solo dealers independientes en plan mensual) | 30-day-free-trial; búsqueda `[VERIFICADO]` |
| **Fee de comprador (transacción)** | Por vehículo; DA reclama **ahorro ~£250/coche vs subasta física** | buyers; buy-fast-buy-smart `[VERIFICADO ×2]` |
| **Modelo de cargos (terms)** | **Subscription Fee (mensual) + transaction fees** por venta/compra; importes exactos en el **Order Confirmation** (no públicos) | terms `[VERIFICADO]` |
| **Pago/sin contrato** | Sin permanencia, cancelable; suscripción a 30 días de factura, fees de transacción inmediatos; posible CPA en tarjeta | terms `[VERIFICADO]` |
| **Crédito al comprador** | Reembolso del transaction fee si el contrato falla por culpa del vendedor (evidencia en 30 días) | terms `[VERIFICADO]` |
| **Elegibilidad** | **IVA válido + comerciante de motor a tiempo completo** | 30-day-free-trial `[VERIFICADO]` |
| **Reclamo de vendedor** | **"6% more vs traditional remarketing routes"** | 30-day-free-trial `[CLAIM-VENDOR]` |

> El schedule exacto de transaction fees (por tramo) vive en el Order Confirmation privado, no en la web. `[PARCIAL]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Dónde coloca DA **cada dato**. Patrón rector: **el dato retail de Auto Trader se inyecta DENTRO del lote de subasta wholesale** (no en una herramienta aparte), de modo que el comprador trade ve el rendimiento retail predicho **en el momento de pujar**. Es el patrón exacto que cardeep replica: dato de consumo sobre el inventario mayorista.

**A. Listado / resultados de búsqueda (grid de lotes).** Por cada lote: **thumbnail + nº de fotos**, **make/model**, **puja actual / precio Buy-It-Now**, **Autotrader Retail Rating**, **Days to Sell**, **mileage**, **age**, **fuel type**, **location/distance**, **tiempo restante**. Ordenable por: ending soonest (default), newly listed, **Retail Rating**, price (low/high), age, distance, **average days to sell**. → cardeep: el rating/días-a-vender van **en la tarjeta de resultados**, no escondidos.

**B. Ficha del vehículo / VDP (el lote).** Hub del comprador: **galería de imágenes** (cuantas más, más pujas) · **condition report** (daños, testigos, equipamiento faltante, advisories MOT) · **NAMA grade** · **description estructurada** (overview / exterior / interior / terms) · **MOT / V5 / service history / owners** · **mileage / age / fuel / colour** · **special features** · y la **capa Auto Trader incrustada**: **Retail Rating + Days to Sell + market average + margen estimado**; **panel de puja** (puja actual, incrementos £50/£100/£200, **Maximum/proxy bid**, **Buy It Now**, **Make Me an Offer**) + indicador de **reserva**.

**C. Stock Alerts (email policy-matched).** Lotes que cumplen la política del comprador, con los campos clave (rating, días, margen) para decidir sin entrar.

**D. Dashboard / flujo del vendedor.** Al listar: **stand-in value** → **reserve price** (recom. 95-96% CAP) → subida de **fotos + condition report**. Tras listar: **CAP performance vs subasta física**, **días a vender**, **pujas**, resultado de venta, **cash en 5 días**. (Métricas de watchers/visualizaciones: `[NO-VERIFICADO]`.)

**E. Índices publicados (RMM / EVPR / Under the Hood).** Tablas agregadas por **modelo/marca**: **retail margin £**, **units sold**, **edad**, **km**, **days to sell**, **Retail Rating**, **CAP Clean %**, **average sold price**; segmentadas por bracket de precio (sub-£10k / over £10k) y por combustible (EVPR). Es el "informe" público de wholesale intelligence.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Fusión única Cox(wholesale) + Auto Trader(retail).** Es la **única plataforma que inyecta el dato retail LIVE de Auto Trader** (Retail Rating, Days to Sell, market average, margen) **dentro de una subasta wholesale**. El comprador trade ve *cómo rendirá el coche en su forecourt local antes de pujar*. Patrón directamente replicable por cardeep.
2. **Retail Rating ajustado por ubicación (radio 50 mi).** Deseabilidad **local** por comprador, no genérica.
3. **Retail Margin Monitor.** Índice público mensual de **beneficio retail potencial por modelo/marca** (sold price vs market average Auto Trader) — un "barómetro" de margen que la prensa cita.
4. **EV Performance Review.** Índice mensual dedicado al rendimiento **wholesale de EV/híbrido** (margen, CAP%, días, conversión) — granularidad EV poco común.
5. **Margen estimado en el propio lote.** El comprador ve el **£ de margen potencial** en la ficha, no solo el precio de puja.
6. **Stock Policy + recomendaciones basadas en el forecourt real del comprador** (su inventario Auto Trader + su histórico de puja).
7. **Ecosistema integrado:** funding (NextGear Capital) + logística (Movex) + rutas de venta retail (Auto Trader / Motors.co.uk) + enlace Manheim, sin salir de la plataforma.
8. **Red abierta + cerrada:** soporta ventas OEM dirigidas exclusivamente a la red franquiciada.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Reino Unido.** Sin España, Europa ni multipaís. ← hueco mayor para cardeep. `[VERIFICADO por ausencia]`
2. **No es proveedor de datos primario / no vende valoración como producto.** Retail Rating, market average y Days to Sell son **de Auto Trader (licenciados)**; DA es **superficie de distribución**, no el originador del dato. No hay un producto de valoración DA standalone. `[VERIFICADO]`
3. **No es libro de coche NUEVO / MSRP / residual-lease.** No publica **curvas de depreciación** ni forecast residual multi-anual (eso es cap hpi / Auto Trader / Autovista). `[VERIFICADO por ausencia]`
4. **Sin VHR ni checks productizados.** No genera vehicle history report, ni check de financiación pendiente / robo / siniestro total como producto — solo **condition report** del lote. `[VERIFICADO por ausencia]`
5. **Sin API de consumo de datos ni feed/Excel para analítica externa.** La API/CSV es **ingesta de stock**, no salida de datos para integradores. No hay docs de developer públicas. `[VERIFICADO por ausencia]`
6. **Sin índice propio de days'-supply / market days supply** para UK (Cox US tiene MUVVI/MDS; DA no publica un índice macro equivalente). `[VERIFICADO por ausencia]`
7. **Solo trade/wholesale.** No es marketplace de consumo ni guía pública de valor al consumidor. `[VERIFICADO]`
8. **RMM/EVPR son índices agregados a nivel modelo/marca**, no un dataset consultable por VIN ni una API — son contenido de PR/insight, no un producto de datos vendible. `[RECONSTRUIDO]`
9. **Fee schedule de transacción no público** (en Order Confirmation privado). `[PARCIAL]`
10. **Sin spec/equipamiento por VIN como base de datos productizada** (el equipamiento aparece en la description del lote, no como dataset estructurado). `[VERIFICADO por ausencia]`

---

## 10. Fuentes

**Oficiales DA (accesibles vía WebFetch):**
- Home / posicionamiento: https://www.dealerauction.co.uk/
- About (JV, historia, HQ, company nº 11514206, predecesoras): https://www.dealerauction.co.uk/about-us/
- Buyers (Retail Rating, Days to Sell, alertas, ahorro £250): https://www.dealerauction.co.uk/buyers/
- Sellers (CAP performance, formatos, API/feed/CSV, NextGear): https://www.dealerauction.co.uk/sellers/
- Buy fast buy smart (datos por listing + orden): https://www.dealerauction.co.uk/buy-fast-buy-smart/
- 30-day free trial (precio £99/mes, £199/año, primera venta gratis, IVA): https://www.dealerauction.co.uk/30-day-free-trial/
- Terms (Subscription Fee + transaction fees, pagos): https://www.dealerauction.co.uk/terms/
- News hub: https://www.dealerauction.co.uk/news/
- **Retail Margin Monitor** (metodología + columnas): https://www.dealerauction.co.uk/retail-margin-monitor/rmm-may-2026/ · https://www.dealerauction.co.uk/retail-margin-monitor/nov-2025/ · https://www.dealerauction.co.uk/retail-margin-monitor/2025-annual-round-up/ · https://www.dealerauction.co.uk/retail-margin-monitor/2025-roundup/
- **EV Performance Review** (hub + ediciones): https://www.dealerauction.co.uk/ev-performance-review/ · https://www.dealerauction.co.uk/ev-performance-review/ev-performance-accelerates-on-dealer-auction/ · https://www.dealerauction.co.uk/ev-performance-review/evpr-may-2026/
- **Under the Hood** (KPIs de plataforma): https://www.dealerauction.co.uk/blog/under-the-hood-of-dealer-auction-2024/ · https://www.dealerauction.co.uk/blog/under-the-hood-2026-q1/
- Mecánica de compra (formatos, proxy, make-me-an-offer, orden): https://www.dealerauction.co.uk/blog/a-guide-to-the-different-ways-to-buy-trade-stock/
- 8 top tips for selling (campos de listing del vendedor): https://www.dealerauction.co.uk/blog/8-top-tips-for-successful-selling/
- Imágenes duplican pujas (2-5→4,1; 11-20→8,2; 87%/89%): https://www.dealerauction.co.uk/news/wholesale-vehicle-sellers-double-bids-with-images/
- Streamlining sourcing (Retail Rating en radio 50 mi, Stock Policy, recomendaciones): https://www.dealerauction.co.uk/blog/streamlining-sourcing-used-vehicles-for-independent-car-dealers/
- Hyundai + OEMs (VW/Renault/Nissan; JV): https://www.dealerauction.co.uk/news/uks-biggest-digital-wholesale-marketplace-dealer-auction-signs-up-hyundai-motor-uk/

**Matrices / prensa de la JV (verificación de identidad):**
- Manchester Digital (JV Cox+Auto Trader, NextGear/Movex/Motors.co.uk): https://www.manchesterdigital.com/post/manchester-digital/cox-automotive-uk-and-auto-trader-uk-to-launch-a-new-joint-venture
- AM-online (JV, plataformas predecesoras, lanzamiento enero 2019): https://www.am-online.com/news/supplier-news/2018/08/16/cox-automotive-and-auto-trader-join-forces-in-dealer-auction-joint-venture · https://www.am-online.com/news/supplier-news/2019/01/02/auto-trader-and-cox-automotive-launch-dealer-auction-joint-venture
- Motor Finance Online: https://www.motorfinanceonline.com/news/cox-automotive-and-auto-trader-launch-online-dealer-auction-platform/
- Fleet News: https://www.fleetnews.co.uk/news/car-industry-news/2018/08/17/cox-automotive-and-autotrader-launch-dealer-auction-online-marketplace
- Auto Trader plc press: https://plc.autotrader.co.uk/press-centre/news-hub/auto-trader-cox-automotive-joint-venture-dealer-auction-launches-in-january/
- Cox Automotive Europe (producto Dealer Auction): https://www.coxautoinc.eu/our-products/dealer-auction/ `[403 en fetch — datos vía búsqueda]`

**Auto Trader (origen del dato licenciado):**
- Retail Rating (definición 1-100, demanda/oferta/días, ajuste por ubicación): https://help.autotrader.co.uk/hc/en-gb/articles/19690017165981-What-is-Retail-Rating · https://help.autotrader.co.uk/hc/en-gb/articles/21945900805405-Introduction-to-Retail-Rating `[403 en fetch — definición vía búsqueda que cita estas URLs + autotraderinsight blog]`
- Price to the live market / Market Insight (1,3M veh/día, 20.500 cambios/día): https://www.autotrader.co.uk/partners/retailer/data-and-insight/price-to-the-live-market · https://www.autotrader.co.uk/partners/retailer/solutions/market-insight `[403 en fetch — datos vía búsqueda]`
- Price Indicator (Great/Good/Fair/Higher/Lower + £ variación, ~500k listings/día): https://help.autotrader.co.uk/hc/en-gb/articles/19212037724957 · https://www.am-online.com/news/supplier-news/2017/05/31/consumers-now-told-if-vehicles-are-fairly-priced-on-auto-trader

**Sector (verificación cruzada):**
- NAMA grading (5 grados, retail-ready 4.0+, condition reports): https://www.nama-uk.com/grading/grading · https://www.manheim.co.uk/campaigns/nama-grading

### Notas de verificación
- **JV Cox Automotive + Auto Trader (50/50), anuncio ago-2018, lanzamiento enero-2019, fusión de dealer-auction.com + Manheim Online + Smart Buying:** manchesterdigital + am-online + motorfinanceonline + fleetnews + plc.autotrader + about-us. **[VERIFICADO ×2+]**
- **HQ Leeds (Rothwell, LS26 0JE) + company nº 11514206:** about-us (WebFetch). **[PARCIAL]** — un solo origen, aunque el nº de registro es dato público de Companies House.
- **CEO Le Etta Pearce:** de la prensa de la JV 2018/2019. **[PARCIAL — posiblemente desactualizado a 2026]**.
- **Retail Rating (1-100; demanda 7d vs 6m + oferta + días-a-vender; ajuste por ubicación 50 mi; no varía con precio):** búsqueda que cita help.autotrader + autotraderinsight + valores reales en RMM/EVPR (33,7-74,1). **[VERIFICADO ×2]**
- **Precio £99/mes + IVA (£199/año):** 30-day-free-trial + buyers + búsqueda. El **£99/mes** está **[VERIFICADO ×2]**; el **£199/año** es **[PARCIAL]** (un solo origen).
- **Metodología RMM (>20 unidades/modelo, >50/marca, sold price vs Auto Trader market average, ventana mensual):** consistente en rmm-may-2026 + nov-2025 + roundups. **[VERIFICADO ×2]**
- **KPIs de plataforma 2024 y Q1 2026:** under-the-hood (blog oficial DA). Dato **del propio vendedor**; **[VERIFICADO]** como cifra oficial, no auditado por tercero.
- **NAMA grade en la UI de DA:** la condición/condition report está **[VERIFICADO]**; el **label NAMA** concreto es **[RECONSTRUIDO]** del linaje Manheim Online + estándar de sector, no confirmado literal en una ficha de DA (requiere login).
- **Price Indicator en la UI de DA:** es feature de Auto Trader; **[PARCIAL]** si se muestra literal en el lote de DA (DA confirma Retail Rating + Days to Sell + market data, no el label Price Indicator).
- **Subdominio "wholesale-intelligence":** `wholesale-intelligence.dealerauction.co.uk` **NO resuelve** (nslookup sin A/AAAA) y `/wholesale-intelligence/` da **404** (curl). Es el **bucket de taxonomía de cardeep**, no una propiedad web de la empresa. **[VERIFICADO por ausencia, 2026-06-30]**
- **exa MCP:** NO disponible en el entorno (ToolSearch "exa search semantic" y "+exa" devolvieron solo WebSearch/WebFetch/gbrain/claude-mem/gmail/drive/logo). Investigación con **WebSearch + WebFetch + nslookup/curl**. **[NOTA DE MÉTODO]**
- **Páginas gated/bloqueadas:** Auto Trader help (403), coxautoinc.eu (403), sign-up (JS sin contenido) → datos tomados de búsquedas y páginas equivalentes verificadas.
