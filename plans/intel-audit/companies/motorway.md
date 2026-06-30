# Motorway — Auditoría atómica

> Slug: `motorway` · Subdominio cardeep: **wholesale-intelligence** · Región: **Reino Unido (UK-only)**
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (≥2 fuentes), `[PARCIAL]` (1 fuente), `[CLAIM-VENDOR]` (marketing del vendedor sin verificación independiente), `[RECONSTRUIDO]` (compongo el dato de varias páginas), `[NO-VERIFICADO]`, `[VERIFICADO por ausencia]`.
> **Naturaleza (clave para no confundir con el resto del set):** Motorway **NO es un proveedor de datos/guía de valor** (no es CAP, Glass's, Autovista, JATO…). Es un **marketplace C2B online**: el **particular** vende su coche y **>8.000 dealers** pujan en una **subasta diaria**. Su "inteligencia" es (a) el motor ML de valoración **RPM (Real-Time Price Machine)** que da el precio instantáneo al vendedor, y (b) la capa de **provenance/historial Total Car Check** (adquirida 2023) que sostiene la exactitud del dato. Esa inteligencia está **embebida en su propio embudo**, no se vende como producto de datos a terceros. Por eso encaja en "wholesale-intelligence" como **canal de adquisición wholesale para dealers + valuación ML**, no como guía/feed de mercado.
> Sitios/marcas: `motorway.co.uk` (lado vendedor/consumidor), `pro.motorway.co.uk` (plataforma dealer), `help.motorway.co.uk` (centro de ayuda, campos atómicos), `totalcarcheck.co.uk` (provenance B2C), app móvil "Motorway - Sell your car".

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre de marca | **Motorway** | motorway.co.uk; pro.motorway.co.uk `[VERIFICADO ×2]` |
| Entidad legal | **MOTORWAY ONLINE LTD**, company number **10285711**, **incorporada 19-jul-2016**, status **Active**, private limited | Companies House `[VERIFICADO]` |
| Domicilio social | **12-13 Wells Mews, London, W1T 3HE** | Companies House `[VERIFICADO]` |
| HQ / oficinas | **Londres** (sede) + **Brighton** (segunda oficina) | Wikipedia; about page `[VERIFICADO ×2]` |
| Fundación (operativa) | **2017** (lanzamiento público; el copyright del sitio reza "2016-2026", consistente con incorporación jul-2016) | Wikipedia; pro.motorway footer `[VERIFICADO ×2]` |
| Fundadores | **Tom Leathes** (CEO), **Harry Jones**, **Alex Buttle** (los tres venían de **Top10.com**, comparador de banda ancha/móvil vendido a uSwitch en 2010; Buttle ya no figura en el equipo ejecutivo actual) | Wikipedia; about page `[VERIFICADO ×2]` |
| Owner / grupo | **Independiente** (no pertenece a grupo automotor). Respaldada por VC | Wikipedia `[VERIFICADO]` |
| Inversores | **Index Ventures**, **ICONIQ Growth/Capital**, **BMW i Ventures**, **LocalGlobe**, **Marchmont Ventures**, **Unbound** | about page; Wikipedia; bmwiventures.com `[VERIFICADO ×2]` |
| Valoración | **>$1.000 M (unicornio)** alcanzada en **Series C, nov-2021** | Wikipedia `[PARCIAL]` |
| Equipo ejecutivo | Tom Leathes (CEO & Founder), Liz Kistruck (CFO), James Wilson (COO), Naomi Walkland (CMO), Tanya Cordrey (Chief Product Officer), Nehal Bhayani (Chief People Officer), Nic Hartley (VP Seller Services), **David James (Director of Vehicle Data — fundador de Total Car Check)** | about page; am-online `[VERIFICADO ×2]` |
| Estatus regulatorio | **Appointed Representative de ITC Compliance Limited** (FCA reg. **313486**); credit broker, **no lender**. VAT **246940487** | pro.motorway footer `[VERIFICADO]` |

**Rondas de financiación (cronología):** Angel **£500k** → Seed **£2,75 M** (LocalGlobe, Marchmont) → **Series A (2019) £11 M** (Marchmont, LocalGlobe) → **Series B (jun-2021) £48 M / $67,7 M** (Index, BMW i Ventures, Unbound) → **Series C (nov-2021) $190 M** (Index + ICONIQ Growth) → unicornio. (Fuente: Wikipedia. `[PARCIAL]` — fuente única, pero ampliamente reportada.)

**Categorías de producto:** (1) **Marketplace de subasta diaria C2B** (particular→dealer); (2) **Motor ML de valoración RPM** (precio instantáneo al vendedor); (3) **Car Value Tracker** (tasador/seguimiento de valor para consumidor); (4) **Vehicle profiling** (perfil del coche con AI profiling tool); (5) **Provenance/historial = Total Car Check** (B2C + dato interno); (6) **Servicios transaccionales dealer:** **Motorway Pay** (pagos), **Motorway Move** (transporte + appraisal in situ), integración **stock funding** (NextGear); (7) **Inteligencia de mercado de marketing = "Fast Forward" Trends Report** (informe de tendencias anual).

**Cliente objetivo:** **dos lados** del marketplace — (a) **vendedores particulares** UK (B2C, lado motorway.co.uk); (b) **dealers** UK independientes, franquiciados y supermarkets (B2B, lado pro.motorway.co.uk). Total Car Check sirve además **consumidores compradores** (informes de historial B2C). `[VERIFICADO ×2]`

---

## 2. Cobertura

- **Geografía:** **Reino Unido únicamente.** No hay operación en otros países (contraste con Manheim/BCA/OPENLANE). `[VERIFICADO por ausencia de otros mercados]`
- **Nuevo vs usado:** **USADO** exclusivamente; **C2B** (stock privado de particular). No vende coche nuevo ni hace valoración de coche nuevo. `[VERIFICADO]`
- **Tipos de vehículo:** **cars + vans/LCV** (el centro de ayuda tiene perfilado específico de van: "Do I have to empty my van before taking photos"). **No** motos, trucks pesados ni plant/machinery. `[VERIFICADO]`
- **Escala (transaccional):**
  - **>8.000 dealers verificados** activos (antes "5.000-strong network"; cardealermagazine reportó **7.500** en hito intermedio; about page actual dice **8.000+**). `[VERIFICADO ×2]`
  - **"Dos de cada tres" dealers UK** usan la plataforma para comprar stock. `[PARCIAL]`
  - **>£7,8 bn** en transacciones acumuladas desde 2017. `[PARCIAL]`
  - Ventas de coche usado: **£1,7 bn (2022)** → **£2,2 bn (2023)**. `[PARCIAL]`
  - **>500.000 vehículos** vendidos acumulados (2024). `[PARCIAL]`
  - **>1 M de personas** han usado la plataforma (vendedores). `[VERIFICADO ×2]`
  - **Subasta diaria:** "up to 1.000+ cars/day"; cardealermagazine: "regularmente >2.000 cars" por sale. `[VERIFICADO ×2 — rangos de dos fuentes]`
  - **RPM:** **~8 M de valoraciones** servidas a consumidores UK desde 2021. `[VERIFICADO ×2]`
  - **Total Car Check:** **>42 M de checks** en 2022 (antes de la adquisición). `[VERIFICADO]`
- **Frescura del dato:** **valoración en tiempo real** (RPM, basada en "live market data" + outcomes de subasta reales en el momento); estimación válida **7 días** (re-confirmar mileage); subasta **diaria**. `[VERIFICADO ×2]`
- **Financieros:** revenue **£66,4 M (2024)**, pérdida operativa **£37,3 M (2024)**, revenue proyectado **£78 M (2025, +18%)**, objetivo de rentabilidad **2026**; préstamo de **£25 M** (finales 2024/2025). `[PARCIAL]`

---

## 3. Productos + campos atómicos

### 3.0 Resumen de productos

| Producto | Qué es | Salida principal | Campos (aprox.) |
|---|---|---|---|
| **RPM (Real-Time Price Machine)** | Motor ML de valoración instantánea (Vertex AI + BigQuery) | estimated sale price en tiempo real | ~9 |
| **Vehicle profile** (+ AI profiling tool) | Perfil del coche construido por el vendedor desde el móvil | identidad + spec + condición + historial + daños + **16 fotos** | ~24 |
| **Guide price** | Precio guía acordado tras perfilar (sustituye "reserve price") | guide price + reserve interno | ~3 |
| **Daily sale / subasta** | Subasta diaria con proxy bidding | max bid + £1-sobre-siguiente + highest offer | ~10 |
| **Car Value Tracker** | Tasador + seguimiento de valor para consumidor | valor actual + historial 24m + depreciación + alertas | ~12 |
| **Total Car Check** | Provenance/historial (B2C + dato interno) | owners + write-off + finance + MOT + robo + km | ~12 |
| **Motorway Pay** | Pagos (powered by Modulr) | pago a vendedor+finance+fees en 1 transferencia | ~4 |
| **Motorway Move** | Transporte + **on-site appraisal** | recogida + appraisal in situ (real-life check) | ~4 |
| **Fast Forward Trends Report** | Informe de tendencias de mercado (marketing/PR) | price performance + tech premium + transmission split | ~8 |

### 3.1 RPM — Real-Time Price Machine (motor de valoración ML, NÚCLEO de inteligencia)

> Lanzado **2021**. Da al vendedor un **"estimated sale price"** instantáneo con solo **matrícula + kilometraje**. Construido sobre **Google Cloud**: modelos propios en **Vertex AI**, datos en **BigQuery + Artifact Registry**. Combina **información del coche** (introducida por el vendedor) con **investigación de oferta/demanda de mercado en el momento de la valoración**. Impacto declarado: **+2% de revenue (2023)** → camino a **+15-17% (2024)** (algunas fuentes citan "+18% proyectado"). **~8 M de valoraciones** servidas.

| Campo / señal atómica | Definición | Fuente |
|---|---|---|
| **Registration (VRM)** | Matrícula — input primario | car-value-tracker; how-it-works `[VERIFICADO ×2]` |
| **Mileage** | Kilometraje — input primario | how-it-works `[VERIFICADO]` |
| **Make** | Marca (señal del modelo) | Google Cloud case study (vía WebSearch) `[VERIFICADO]` |
| **Model / derivative** | Modelo y derivado | car-value-tracker `[VERIFICADO]` |
| **Age / year** | Edad / año | car-value-tracker `[VERIFICADO]` |
| **Fuel type** | Combustible | car-value-tracker `[VERIFICADO]` |
| **Transmission** | Caja de cambios | car-value-tracker (report) `[VERIFICADO]` |
| **Service history (señal)** | Historial de servicio como señal del modelo | Google Cloud case study `[VERIFICADO]` |
| **Defects / condition (señal)** | Defectos/condición como señal del modelo | Google Cloud case study `[VERIFICADO]` |
| **Market supply & demand (en el momento)** | Oferta/demanda de cada vehículo en el instante de valorar | Google Cloud case study `[VERIFICADO]` |
| **Real auction outcomes (señal)** | Resultados reales de subastas del propio marketplace | how-it-works `[VERIFICADO]` |
| **Estimated sale price (output)** | Valor instantáneo "real-world"; puede cambiar al aprender spec/condición/historial | how-it-works; help (estimated-vs-guide) `[VERIFICADO ×2]` |

### 3.2 Vehicle profile (perfil del coche — campos atómicos, dealer-facing)

> El vendedor construye el perfil **desde el móvil en minutos** (con **AI profiling tool**, lanzado abr-2026, que arma un "sale-ready profile" sin experiencia automotriz). Es la "ficha de coche" que **los dealers ven para pujar**: "dealers base their offers on the information provided in your vehicle's profile". Es el equivalente Motorway al VDP del lote.

**Identidad / spec:**
| Campo | Definición | Fuente |
|---|---|---|
| **Registration / VRM** | Matrícula | help (profiling) `[VERIFICADO]` |
| **Make / Model / Derivative** | Identidad del vehículo | how-it-works `[VERIFICADO]` |
| **Trim level** | Nivel de acabado | householdmoneysaving; help `[VERIFICADO]` |
| **Optional extras / specification** | Equipamiento opcional / spec | help (profiling) `[VERIFICADO]` |
| **Mileage** | Kilometraje (amendable en el perfil) | help (change mileage) `[VERIFICADO]` |
| **Number of keys** | Número de llaves | how-it-works; help `[VERIFICADO ×2]` |
| **Number of owners / keepers** | Número de propietarios previos | search snippets; TCC `[PARCIAL]` |

**Condición / daños (declaración obligatoria):**
| Campo | Definición | Fuente |
|---|---|---|
| **Overall condition** | Condición general (detallada) | help (profile) `[VERIFICADO]` |
| **Wear and tear declaration** | Declaración obligatoria de desgaste, "no matter how superficial" (omitir → oferta reducida o cancelación) | help (declare wear and tear) `[VERIFICADO]` |
| **Stone chips declaration** | Declaración obligatoria de impactos de piedra | help (declare stone chips) `[VERIFICADO]` |
| **Alloy wheel damage** | Daño en llantas (kerb scuffs, chips al trim) | help (damaged alloys) `[VERIFICADO]` |
| **Tyre tread depth & condition** | Profundidad de banda y condición; flag de neumáticos **cracked/split** (perished entre tacos/sidewall) | help (photos; cracked tyres) `[VERIFICADO]` |
| **General damage declaration** | Cualquier daño no cubierto arriba | help (additional damage) `[VERIFICADO]` |
| **Profile-accuracy / re-guide flag** | Si aparece daño nuevo tras perfilar, se actualiza y puede recalcular el guide price | help (discovered additional damage) `[VERIFICADO]` |

**Historial de servicio:**
| Campo | Definición | Fuente |
|---|---|---|
| **Service history status** | **Full (FSH) / partial / missing**; FSH sube el valor vs partial/missing | help (what is service history) `[VERIFICADO]` |
| **Service records (photos)** | Fotos del **front page** de cada factura (detalles del vehículo + servicio) | help (every page of invoices) `[VERIFICADO]` |
| **Service intervals** | Intervalos por mileage (p.ej. 10.000 mi) o tiempo (p.ej. 12 meses), lo que ocurra antes | help (service history) `[VERIFICADO]` |
| **Source of records** | Service book / web del fabricante o retailer | help (where to get records) `[VERIFICADO]` |
| **Proof of purchase** | Si registered keeper desde hace <3 meses, prueba de compra | help (valid proof of purchase) `[VERIFICADO]` |

**Set de 16 fotos (estandarizado, vía link/app con guías on-screen; no se aceptan fotos previas ni vídeo):**
| Foto | Requisito atómico | Fuente |
|---|---|---|
| **4× exterior** | Una por cada esquina a **45°**, puertas cerradas, **matrícula visible**, coche entero en el frame, sin personas/mascotas | help (what photos) `[VERIFICADO]` |
| **Seats** | Asientos delanteros y traseros (lo máximo posible) | help (what photos) `[VERIFICADO]` |
| **Dashboard** | **Volante completo + consola central + palanca de cambios** (tomada desde el asiento trasero) | help (what photos) `[VERIFICADO]` |
| **Boot interior** | Maletero **vacío** | help (what photos) `[VERIFICADO]` |
| **Alloy wheels** | Head-on, llanta completa visible | help (what photos) `[VERIFICADO]` |
| **Tyre treads** | Head-on (delante y detrás / entre paso de rueda y rueda); debe verse **tread depth + condición** | help (what photos) `[VERIFICADO]` |
| **Convertible (condicional)** | Techo **arriba y abajo**, preferible front driver-side | help (what photos) `[VERIFICADO]` |

> **Nota van:** para vans, no se exige vaciar pero se recomienda (afecta a las fotos). `[VERIFICADO]`

### 3.3 Guide price (precio guía — sustituye "reserve price")

| Campo | Definición | Fuente |
|---|---|---|
| **Estimated sale price** | Valoración instantánea inicial (solo reg+mileage); cambia al aprender el coche | help (estimated vs guide) `[VERIFICADO]` |
| **Guide price** | Precio guía **acordado** tras perfilar (spec/service history/condición/daño); **puede ser menor** que el estimate (el dealer descuenta costes de preparación/retail) | help (estimated vs guide); how-it-works `[VERIFICADO ×2]` |
| **Reserve price (legacy)** | Término anterior; Motorway usa hoy "guide price". La mejor oferta de la red **puede superar** el guide | help (estimated vs reserve) `[VERIFICADO]` |
| **Final sale price** | La **oferta más alta aceptada** en la daily sale | how-it-works `[VERIFICADO]` |

### 3.4 Daily sale / subasta (dealer-facing — mecánica de puja)

| Campo / función | Definición | Fuente |
|---|---|---|
| **Max bid (proxy)** | El dealer fija su oferta máxima sobre el reserve | pro.motorway; cardealermagazine `[VERIFICADO ×2]` |
| **Auto-bid increment** | Motorway puja por él en incrementos de **£50** | WebSearch (cardealermagazine) `[VERIFICADO]` |
| **£1-above-next-bidder** | Solo pagas **£1 más** que el siguiente postor una vez el coche **alcanza reserve** | pro.motorway `[VERIFICADO ×2]` |
| **Highest-bidder status** | Notificación de si eres el postor más alto | pro.motorway `[VERIFICADO]` |
| **Smart search filters** | Filtros por body type (**SUVs, EVs, high-performance**), make/model y criterios; "listings shaped by dealer feedback" | pro.motorway `[VERIFICADO]` |
| **Stock alerts** | Alerta en el momento en que se lista stock que casa con las preferencias | pro.motorway; cardealermagazine `[VERIFICADO ×2]` |
| **Shortlist** | Lista corta de candidatos | pro.motorway `[VERIFICADO]` |
| **Seller document verification** | Motorway verifica la documentación del vendedor al cerrar | pro.motorway `[VERIFICADO]` |
| **Vehicle profile (link)** | Cada coche "fully profiled": fotos detalladas + spec + condición + service history | pro.motorway; cardealermagazine `[VERIFICADO ×2]` |
| **Personalisation engine** | Motor de personalización que casa coches con el interés del dealer (mileage, condition, age, price, make-model) | WebSearch (brainstation/Google Cloud) `[PARCIAL]` |

### 3.5 Car Value Tracker (tasador + seguimiento de valor, consumidor)

> Producto **gratuito** de consumidor (motorway.co.uk/car-value-tracker). Tasa por **age, make, model, mileage** con "live market data + our own sales stats".

`Vehicle registration` (input) · `Current mileage` (input) · **`Current market value`** (output) · **`Value history` (últimos 24 meses)** · **`Depreciation rate`** · **`Price trends across the year`** · **`Monthly email value-change alert`** · `7-day valuation validity` (re-confirmar mileage) · `Up to 6 tracked vehicles` (cuenta logueada) · Report: `make` · `model` · `year` · `registration` · `current mileage` · `fuel type` · `transmission` · `current value`. (Fuente: car-value-tracker page. `[VERIFICADO]`)

### 3.6 Total Car Check (provenance / historial — adquirido jul-2023)

> **Total Car Check (TCC)**, fundada por **David James (2009)**, adquirida por Motorway en **jul-2023** (sum no revelada). **>42 M checks en 2022**, +30% revenue YoY. James → **Director of Vehicle Data** de Motorway. Refuerza "accuracy and transparency" del dato para vendedores y dealers. Sigue operando como producto B2C en `totalcarcheck.co.uk`.

| Campo atómico | Definición | Fuente |
|---|---|---|
| **Previous owners / keepers** | Número de propietarios previos | am-online; cardealermagazine `[VERIFICADO ×2]` |
| **Accident / damage history** | Accidentes o daños sufridos | am-online `[VERIFICADO]` |
| **Write-off check** | Categoría de siniestro total (insurance write-off) | am-online `[VERIFICADO]` |
| **Outstanding finance check** | Financiación pendiente sobre el vehículo | am-online `[VERIFICADO]` |
| **Logbook loan check** | Préstamo con garantía del logbook | am-online `[VERIFICADO]` |
| **Salvage history check** | Historial de salvage | am-online `[VERIFICADO]` |
| **Stolen check** | Vehículo robado (origen del producto: familiar compró coche robado) | am-online `[VERIFICADO]` |
| **MOT history** | Estado/expiración MOT, mileage en cada MOT, advisories | totalcarcheck.co.uk; motorway MOT guide `[VERIFICADO ×2]` |
| **Plate change history** | Cambios de matrícula | am-online `[VERIFICADO]` |
| **Mileage / odometer check** | Verificación de km (anomalías) | totalcarcheck.co.uk `[PARCIAL]` |
| **Vehicle valuation (TCC)** | Valoración propia de TCC | totalcarcheck.co.uk `[PARCIAL]` |
| **Make/model/spec lookup** | Datos técnicos desde matrícula | totalcarcheck.co.uk `[PARCIAL]` |

### 3.7 Servicios transaccionales dealer (Motorway Pay / Move / stock funding)

`Motorway Pay` (**powered by Modulr**): paga al **vendedor + finance provider + fees** en **una sola transferencia**; pagos al vendedor en **"3 segundos"**; sin facturas. · `NextGear stock funding`: cubre **100% del coste** del vehículo en checkout (control de cashflow). · `Motorway Move` (transporte propio): desde **£99**; **on-site appraisal** = "real-life check" antes de comprar; reserva a cualquier site en pocos clics; alternativa: auto-recogida conectando con el vendedor. · Partnership **Le Capital (oct-2025)** para streamlining de financiación de dealers. (Fuentes: pro.motorway; Wikipedia. `[VERIFICADO ×2]`)

### 3.8 Fast Forward Trends Report (inteligencia de mercado — marketing/PR)

> Informe **anual** de tendencias (no es un índice wholesale en vivo tipo MUVVI; es contenido de marca con datos del propio marketplace + encuestas de consumidor).

Métricas que reporta: **price performance por make/model (YoY %)** (p.ej. Subaru Outback +32,67%, Land Rover Defender +6,29%, Hyundai Santa Fe +2,77%, Kia Rio +1,37%, VW Golf +2,59%, Vauxhall Corsa +4,8%, Renault Clio +4,99%) · **tech-feature price premium** (coches con tech vendieron **+91%** de media en 2025) · **transmission split** (manuales superaron a automáticos en **14,7%** en 2025) · **fuel-type / EV trends** · **demand por cohorte de edad / segmento** (preferencias de consumidor) · datos de personalización/estilo (encuesta). (Fuente: fast-forward guide. `[VERIFICADO]`)

---

## 4. Metodología / fuentes de datos

- **RPM = ML propio sobre Google Cloud.** Modelos en **Vertex AI**; datos en **BigQuery + Artifact Registry**. Señales: **make, mileage, service history, defects/condition** (del vendedor) + **oferta/demanda de mercado en el momento** + **outcomes reales de subasta** del propio marketplace. Impacto: **+2% revenue (2023) → +15-17% (2024)**. `[VERIFICADO ×2]`
- **Dato transaccional propio:** la valoración y el guide price se anclan en **resultados reales** de las subastas diarias Motorway (lo que dealers pagan de verdad), no en una guía de terceros. `[VERIFICADO]`
- **Provenance = Total Car Check** (propietario desde 2023): owners, write-off, finance, logbook loan, salvage, stolen, MOT, plate changes, mileage. Es la capa de **historial/título** que Motorway controla in-house. `[VERIFICADO ×2]`
- **Condición = autodeclaración del vendedor + fotos estandarizadas** (16 fotos guiadas) + **AI profiling tool** que ayuda a montar el perfil. **NO hay AI propietaria de detección de daño** documentada sobre las fotos (a diferencia de los players con computer-vision de daños); el daño lo **declara el vendedor** y lo **juzga el dealer** sobre las fotos; la verificación física real ocurre en el **on-site appraisal de Motorway Move** en la recogida. `[VERIFICADO por ausencia / RECONSTRUIDO]`
- **Sin guía de valor de terceros embebida:** no muestra CAP/Glass's; el precio es **su propio output ML (RPM/guide price)**. `[VERIFICADO por ausencia]`
- **Fast Forward** mezcla dato del marketplace con **encuestas de consumidor** → es **marketing/PR**, no un feed de mercado continuo. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Web vendedor (B2C)** | `motorway.co.uk`: instant valuation, profile builder, guide price, daily sale, aceptar oferta, Car Value Tracker. |
| **App móvil vendedor** | "Motorway - Sell your car" (Google Play / iOS): perfilar coche, fotos guiadas, seguir oferta. |
| **Plataforma dealer (B2B)** | `pro.motorway.co.uk` (login, verificación de dealership): browse/search, alerts, shortlist, proxy bidding, listing fully-profiled, Motorway Pay, Motorway Move. |
| **AI profiling tool** | Asistente que arma "sale-ready profile" desde el móvil sin experiencia (abr-2026). |
| **Provenance B2C** | `totalcarcheck.co.uk`: informes de historial de pago al consumidor comprador. |
| **Pagos** | **Motorway Pay** (powered by **Modulr**); integración **NextGear** (stock funding). |
| **Logística** | **Motorway Move** (transporte propio + on-site appraisal, desde £99) o auto-recogida. |
| **Inteligencia / reporting** | **Fast Forward Trends Report** (anual, marketing). |
| **API pública** | **No documentada** (no es proveedor de datos a terceros). `[VERIFICADO por ausencia]` |

---

## 6. Precio

> **Modelo de doble cobro** (desde may-2026 cobra a **ambos lados**; antes solo cobraba al dealer).

| Concepto | Precio | Fuente / nota |
|---|---|---|
| **Service fee VENDEDOR** | **Escalonado £29.99 – £99.99** según precio final de venta | service-fees; help; cardealermagazine `[VERIFICADO ×2]` |
| · ≤ £1.000 | **Gratis** | cardealermagazine `[VERIFICADO]` |
| · £1.000 – £4.999 | **£29.99** | cardealermagazine `[VERIFICADO]` |
| · £20.000+ | **£99.99** | cardealermagazine `[VERIFICADO]` |
| · bandas intermedias (£5k–£20k) | **no publicadas en tabla única** | `[PARCIAL]` |
| **Entrada en vigor del fee vendedor** | **6-may-2026** (antes el vendedor no pagaba) | cardealermagazine `[VERIFICADO]` |
| **Cobro del fee vendedor** | Deducido vía **Motorway Pay**, o pago por link seguro si el dealer transfiere directo | help; service-fees `[VERIFICADO]` |
| **No sale, no fee** | Si no se vende, el vendedor **no paga nada** | how-it-works `[VERIFICADO]` |
| **Fee DEALER (comprador)** | Motorway cobra al dealer un fee por compra; importe exacto **no publicado** (estimación foro **~£200/coche**) | help (how Motorway makes money); WebSearch `[PARCIAL]` |
| **Motorway Move (transporte)** | Desde **£99** | pro.motorway `[VERIFICADO]` |
| **Total Car Check (B2C)** | Pago por informe (tarifa en totalcarcheck.co.uk) | TCC `[PARCIAL]` |

> ⚠ **Aviso anti-confusión:** la página `pro.motorway.co.uk/pricing` **NO existe como tal**; intentos de navegación a ese path resolvieron (por contaminación de navegador compartido) a una **tabla de fees de Autorola** (£250 buying / £150 sale fee / transporte) que **NO es de Motorway** y queda **descartada**. Los fees de Motorway verificados son los de esta tabla. `[NOTA DE MÉTODO]`

---

## 7. Placement (patrón web/UI — clave para cardeep)

> Patrón rector: Motorway tiene **dos fichas espejo** sobre el mismo coche — la del **vendedor** (que construye el perfil y ve precio/ofertas) y la del **dealer** (que ve el perfil completo y puja). El **vehicle profile es el hub**: identidad + spec + condición/daños declarados + service history + **16 fotos**, enriquecido con **provenance (Total Car Check)**. El **precio** (RPM) vive en el **landing/instant-valuation** y se refina a **guide price** en el perfil. La **inteligencia macro** (Fast Forward) vive **fuera del flujo**, en guías/PR.

**A. Landing / Instant valuation (motorway.co.uk home).** Widget de entrada: **registration + mileage** → **estimated sale price** instantáneo (RPM). Es el primer punto de contacto y el "anzuelo".

**B. Profile builder (web + app, AI profiling tool).** Pantalla(s) donde el vendedor añade **make/model/derivative + trim + optional extras + number of keys + service history (FSH/partial/none + fotos de facturas) + condición + declaraciones de daño (wear&tear, stone chips, alloys, tyres) + 16 fotos guiadas**. "The stronger your profile, the more confident dealers are."

**C. Guide price screen.** Tras perfilar, Motorway **acuerda un guide price** tailored (puede ser < estimate). Muestra al vendedor la expectativa antes de la subasta.

**D. Daily sale / offers (vendedor).** El coche entra en la **subasta diaria**; los dealers pujan en tiempo real; el vendedor ve la **highest offer** y **acepta** → final sale price. Luego **collection + payment** (fondos antes de llevarse el coche).

**E. Car Value Tracker (consumidor, dashboard).** Pantalla de seguimiento: **valor actual + gráfico de historial 24 meses + tasa de depreciación + tendencias del año + alerta mensual**; hasta **6 vehículos** en la cuenta.

**F. Dealer listing detail (pro.motorway, login).** Ficha del lote para el dealer: **fotos detalladas + spec + condición + service history** ("fully profiled") + **provenance Total Car Check** + guide/reserve. Es el VDP wholesale.

**G. Dealer browse/search (pro.motorway).** **Smart search filters** (SUVs/EVs/high-performance, make/model, mileage/age/price/condition) + **stock alerts** + **shortlist**; "listings shaped by dealer feedback".

**H. Dealer bid + post-win.** **Max bid (proxy)** → auto-bid £50 → **£1-sobre-siguiente** al alcanzar reserve → **highest-bidder notification** → **seller doc verification** → **Motorway Move (on-site appraisal)** → **Motorway Pay** (pago a vendedor+finance+fees en una transferencia; NextGear 100%).

**I. Total Car Check report (B2C, totalcarcheck.co.uk).** Informe de historial independiente: owners, write-off, finance, logbook loan, salvage, stolen, MOT, plate changes, mileage.

**J. Fast Forward Trends (guías/PR, fuera del flujo).** Price performance por modelo, tech premium, transmission split, fuel/EV trends, preferencias por cohorte.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **El mayor embudo de stock PRIVADO C2B de UK convertido en canal wholesale para dealers.** No compra ni tiene inventario propio: agrega **stock privado fresco** (>1M vendedores) y lo subasta a **8.000+ dealers** a diario. Es un **origen de dato de transacción real** distinto de las subastas de fleet/trade clásicas. `[VERIFICADO ×2]`
2. **RPM = valoración ML en tiempo real anclada en outcomes reales de su propia subasta** (no en guía de terceros), con impacto de revenue medido (+15-17% en 2024). `[VERIFICADO ×2]`
3. **Provenance in-house (Total Car Check):** raro en un marketplace — **controla** la capa de historial/título (owners, write-off, finance, stolen, MOT) en vez de licenciarla. `[VERIFICADO ×2]`
4. **Proxy bidding "£1 sobre el siguiente" + auto-bid £50:** mecánica de subasta transparente y favorable al comprador. `[VERIFICADO ×2]`
5. **Stack transaccional integrado:** **Motorway Pay** (Modulr, pago en "3 s", una sola transferencia a vendedor+finance+fees) + **NextGear stock funding 100%** + **Motorway Move** (transporte propio **con on-site appraisal**). Cierra todo el ciclo dentro de la plataforma. `[VERIFICADO ×2]`
6. **Perfilado estandarizado de 16 fotos guiadas + AI profiling tool:** consistencia de la ficha que reduce fricción de tasación remota. `[VERIFICADO]`
7. **Car Value Tracker con historial de 24 meses + depreciación + alertas mensuales:** herramienta de **retención/seguimiento** de consumidor que la mayoría de marketplaces no da. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece)

1. **No es proveedor de datos/guía de valor a terceros.** No vende feed, índice ni API; RPM y el guide price son **internos a su embudo**. No es comparable a CAP/Glass's/Autovista/JATO como fuente licenciable. `[VERIFICADO por ausencia]`
2. **UK-only.** Sin cobertura de otros países. ← hueco frente a Manheim/BCA/OPENLANE; oportunidad para cardeep. `[VERIFICADO por ausencia]`
3. **Sin dashboard de inteligencia de mercado para dealers** (price-to-market, days-to-sell, market days supply, índices oferta/demanda en vivo). Las "buying tools" son search/alerts/proxy, **no analítica** tipo INDICATA/vAuto/Manheim Data Dashboard. `[VERIFICADO por ausencia]`
4. **Sin AI propietaria de detección de daño sobre fotos.** El daño se **autodeclara** (vendedor) y se juzga visualmente; la verificación física real es el **on-site appraisal humano** en la recogida. `[VERIFICADO por ausencia]`
5. **Sin valor residual / forecast a 36-48 meses, ni coche nuevo / MSRP.** El output es **precio presente** (estimate/guide); no hay curva de depreciación predictiva multianual (el Car Value Tracker mira **hacia atrás** 24m, no forecast forward). `[VERIFICADO por ausencia]`
6. **Sin grading estandarizado de condición** (no hay NAMA/grade 1-5 publicado): la condición es **descripción + fotos + declaraciones**, no una escala normalizada. `[VERIFICADO por ausencia]`
7. **Sin EV battery health score** propietario. `[VERIFICADO por ausencia]`
8. **Tipos de vehículo limitados:** **solo cars + vans**; no motos, trucks pesados ni plant. `[VERIFICADO]`
9. **Fees opacos en parte:** bandas intermedias del fee vendedor (£5k-£20k) y el **fee exacto del dealer** no están publicados. `[PARCIAL]`
10. **Histórico de marketing, no índice en vivo:** Fast Forward es **anual y PR**, no un benchmark wholesale continuo (no hay equivalente a un índice mensual servible). `[VERIFICADO]`
11. **Dato de listing dealer restringido tras login** (verificación de dealership); no hay catálogo público de campos del VDP dealer (reconstruido desde marketing + lado vendedor). `[PARCIAL]`

---

## 10. Fuentes

**Oficiales / producto (Motorway):**
- Home vendedor: https://motorway.co.uk/ · About: https://motorway.co.uk/about
- How it works: https://motorway.co.uk/how-it-works
- Service fees: https://motorway.co.uk/service-fees
- **Car Value Tracker:** https://motorway.co.uk/car-value-tracker
- Dealers (guía): https://motorway.co.uk/sell-my-car/guides/learn-more-about-the-dealers-on-motorway
- **Fast Forward Trends Report 2026:** https://motorway.co.uk/sell-my-car/guides/fast-forward
- **Plataforma dealer:** https://pro.motorway.co.uk/ (footer: Motorway Online Ltd., ITC Compliance FCA 313486, VAT 246940487; flujo de 5 pasos, proxy bidding £1, Motorway Pay/Move, NextGear) — **[VERIFICADO directo vía navegador, href confirmado]**
- Motorway Pay & Modulr: https://pro.motorway.co.uk/motorway-pay-modulr
- **Centro de ayuda — Profiling your vehicle (campos atómicos + 16 fotos):** https://help.motorway.co.uk/hc/en-gb/sections/4410270213138-Profiling-your-vehicle — **[VERIFICADO directo, href confirmado]**
  - What vehicle photos do I need to supply (set de 16): /articles/4911194449436
  - Do I have to declare wear and tear: /articles/4510828670876
  - What is my vehicle's service history: /articles/4510864131868
- Valuation (estimated vs guide vs reserve): https://help.motorway.co.uk/hc/en-gb/articles/4406714990610 · guide price: /articles/4853684956956
- How does Motorway make money: https://help.motorway.co.uk/hc/en-gb/articles/4410632392338
- App: https://play.google.com/store/apps/details?id=uk.co.motorway.customer
- Total Car Check (B2C): https://totalcarcheck.co.uk/ · MOT history: https://totalcarcheck.co.uk/MOT-History-Check

**Terceros / verificación cruzada:**
- **Companies House — MOTORWAY ONLINE LTD (10285711), inc. 19-jul-2016, 12-13 Wells Mews W1T 3HE:** https://find-and-update.company-information.service.gov.uk/company/10285711
- **Wikipedia (fundadores, funding, valoración, financieros, adquisiciones, partnerships):** https://en.wikipedia.org/wiki/Motorway_(brand)
- **Google Cloud case study (RPM, Vertex AI, BigQuery, Artifact Registry, señales, +2%→15-17%):** https://cloud.google.com/customers/motorway
- BMW i Ventures (inversión / "car auction platform of tomorrow"): https://www.bmwiventures.com/news/the-car-auction-platform-of-tomorrow-starting-in-the-uk-our-investment-in-motorway
- **Motorway adquiere Total Car Check (campos de provenance, 42M checks, David James):** https://www.am-online.com/news/acquisitions-and-deals/2023/07/24/motorway-acquires-vehicle-provenance-platform-total-car-check · https://cardealermagazine.co.uk/motorway-announces-acquisition-of-total-car-check-as-part-of-drive-for-accuracy-and-transparency/287274 · https://www.motortrader.com/motor-trader-news/automotive-news/motorway-acquires-total-car-check-26-07-2023
- **Fee al vendedor (6-may-2026, £29.99-£99.99, antes solo un lado):** https://cardealermagazine.co.uk/motorway-now-charging-sellers-a-fee-to-list-on-used-car-auction-platform/324097
- **7.500 dealers / dos de cada tres / £7,8bn:** https://cardealermagazine.co.uk/motorway-passes-7500-dealer-partners-with-two-in-three-retailers-now-using-platform/309842
- Qué es Motorway / qué ven los dealers / £50 increments: https://cardealermagazine.co.uk/in-detail-what-is-motorway-how-does-selling-a-used-car-on-motorway-work-whats-in-it-for-car-dealers/274938
- BrainStation (misión / personalización / RPM 8M): https://brainstation.io/magazine/motorways-mission-to-optimize-online-used-car-sales
- Review/ proceso (16 fotos, service history, fees): https://www.householdmoneysaving.com/how-does-selling-a-car-on-motorway-work/ · https://www.lovemoney.com/news/94140/

### Notas de verificación y método
- **Identidad legal (MOTORWAY ONLINE LTD 10285711, inc. 19-jul-2016, Wells Mews W1T 3HE):** Companies House directo. **[VERIFICADO]**. Fundación operativa 2017 vs copyright "2016" reconciliado (incorporación 2016, lanzamiento 2017). **[VERIFICADO ×2]**
- **Fundadores / funding / valoración / financieros / adquisiciones:** Wikipedia (fuente única para algunas cifras → **[PARCIAL]**) corroborado por about page (fundadores/inversores) y bmwiventures. **[VERIFICADO ×2 lo corroborable]**
- **RPM (Vertex AI, BigQuery, Artifact Registry, señales make/mileage/service history/defects + supply/demand, +2%→15-17%, 8M valoraciones):** Google Cloud case study (vía WebSearch sobre cloud.google.com — el WebFetch de la página se truncaba) + Wikipedia. **[VERIFICADO ×2]**. WebFetch directo de cloud.google.com **truncó** el contenido; datos extraídos por WebSearch del mismo dominio. **[NOTA DE MÉTODO]**
- **Vehicle profile + set de 16 fotos + declaraciones + service history:** help.motorway.co.uk **directo vía navegador (href confirmado en cada extracción)**. **[VERIFICADO]**
- **Flujo dealer / proxy bidding £1 / £50 increments / Motorway Pay (Modulr)/Move/NextGear:** pro.motorway.co.uk **directo (href confirmado)** + cardealermagazine. **[VERIFICADO ×2]**
- **Total Car Check (owners/write-off/finance/logbook/salvage/stolen/MOT/plate/mileage, 42M checks, David James Director of Vehicle Data):** am-online + cardealermagazine + motortrader. **[VERIFICADO ×2]**
- **Fees vendedor (£29.99-£99.99, gratis ≤£1k, £29.99 £1k-4.999, £99.99 ≥£20k, vigor 6-may-2026):** cardealermagazine + service-fees + help. **[VERIFICADO ×2]**. Bandas £5k-£20k **[PARCIAL]**. Fee dealer ~£200 = estimación de foro **[PARCIAL]**.
- **⚠ CONTAMINACIÓN DE NAVEGADOR COMPARTIDO (descartada):** el navegador Playwright es **compartido entre agentes concurrentes** del workflow. Dos `evaluate` cayeron sobre páginas de **OTROS agentes** — `autorola.co.uk/pricing` (Autorola Group/INDICATA: fees £250 buying/£150 sale; **NO es Motorway**) y `copart.com/lot/...` (Copart). **Ambos contenidos quedan DESCARTADOS** y NO se atribuyen a Motorway. Cada extracción válida de Motorway se verificó con `window.location.href` apuntando a motorway.co.uk / pro.motorway.co.uk / help.motorway.co.uk. **[NOTA DE MÉTODO — anti-alucinación]**
- **exa MCP:** ToolSearch "exa…" **no** devolvió herramienta semántica dedicada (solo WebSearch/WebFetch + gbrain/claude-mem). Investigación con **WebSearch + WebFetch + navegador (Playwright) con verificación de href**. **[NOTA DE MÉTODO]**
