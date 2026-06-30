# Guazi (瓜子二手车) — Auditoría atómica

> Slug: `guazi` · Subdominio cardeep: **portal-insights** · Región: **China (RPC)** + **export internacional (2026)** · Auditado: 2026-06-30
> Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (leído en vivo), `[PARCIAL]` (prensa/parcial), `[NO-VERIF]` (no confirmado). Jamás inventar.
> Naturaleza: **NO es una guía de valoración ni un proveedor de datos licenciados** (a diferencia de Che300/KBB). Es la
> **mayor plataforma de TRANSACCIÓN de coche usado de China** (marketplace C2C → plataforma de terceros), del grupo
> **车好多 (Chehaoduo)**. Su "datos/inteligencia" vive **embebida en el producto de consumo** (informe de inspección de
> 259 puntos, estimación oficial de precio, garantías) y en **informes de mercado publicados** (保值率 / 推荐指数 /
> 年度趋势). En **2026** abrió un **brazo de EXPORTACIÓN internacional** (`en.guazi.com` / `globalguazi.com`):
> subasta + FOB para dealers/importadores de fuera de China.

---

## 0. Resumen de la dualidad (clave para leer todo el documento)

Guazi son hoy **dos negocios bajo la misma marca**, con productos y datos distintos:

| Capa | Dominio | Idioma | Público | Modelo | Estado |
|---|---|---|---|---|---|
| **A. Doméstica** (núcleo histórico) | `guazi.com`, `m.guazi.com`, `sell.guazi.com` | Chino | Consumidores + dealers chinos | C2C → **plataforma de terceros** (desde 2023) | Maduro, escala masiva |
| **B. Exportación** (nuevo) | `en.guazi.com` ("Guazi Official"), `globalguazi.com` | Inglés | **Dealers / importadores internacionales** | **Subasta (sealed-bid/live) + FOB fijo** | Lanzado/ampliado **jun-2026** |

> **Caveat de identidad corporativa `[PARCIAL]`:** las propiedades en inglés **NO mencionan a Chehaoduo** y declaran
> operadores distintos (ver §1). El dominio `en.guazi.com` es **subdominio oficial de `guazi.com`** (mismo control DNS) y
> `globalguazi.com` se autodeclara "**wholly-owned subsidiary of Guazi Co., Ltd.**" enlazando a `en.guazi.com` como
> "Guazi Official" → linkaje **oficial verosímil**, pero los números de inspección difieren (259 doméstico vs **200+/300**
> export) y el sistema de grados de subasta **S/A/B/C/D** del export **no existe** en el producto doméstico. Lo trato como
> un brazo oficial de exportación, marcando como `[PARCIAL]` lo que no pude cerrar a fuente primaria de la matriz Chehaoduo.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Marca | **瓜子二手车 (Guazi Used Car)** — "瓜子" = pipas de girasol | guazi.com; Wikipedia |
| Grupo matriz | **车好多集团 (Chehaoduo Group)** — opera **Guazi (usado)** + **Maodou 毛豆新车 (nuevo)** | Wikipedia; TechCrunch; dealstreetasia |
| Razón social (export, autodeclarada) | **Chongqing Guazi Enterprise Consultation Service Co., Ltd.** ("wholly-owned subsidiary of **Guazi Co., Ltd.**", fundada **sep-2015**) + co-operadores **Yilanqunche Automobile Services (Shanghai) Co., Ltd.** y **Guazi Automotive Technology (Tianjin) Co., Ltd.** | globalguazi.com; en.guazi.com/about |
| Fundador / Presidente / CEO | **杨浩涌 (Yang Haoyong / "Mark Yang")** — también fundador de **赶集网 (Ganji.com)** | Crunchbase; prnewswire; baike |
| Co-fundadores | **张小沛 (Zhang Xiaopei)**, **白如冰 (Bai Rubing)** | WebSearch (síntesis prensa) `[PARCIAL]` |
| Fundación | **2015** — Guazi nace dentro de **58赶集 (58/Ganji)**; **escisión nov-2015** como Guazi.com Inc. (Yang Haoyong >50%); Chehaoduo formado jul-2015. (Wikipedia data fundación 2014 dentro de Ganji; export site "founded September 2015".) | prnewswire; Wikipedia; globalguazi.com |
| HQ | **Pekín (Beijing)**, China | Wikipedia; CB Insights |
| Portavoz (export 2026) | **Li Yang** | financialcontent PR 2026-06-22 |
| Idioma producto | Doméstico: **solo chino**. Export: **inglés**. | guazi.com; en.guazi.com |

**Financiación / valoración:** `[PARCIAL — prensa]`
- **Total acumulado ≈ $4.3 B** (Crunchbase, hasta Serie E). El sitio export lo redondea a **"$4 billion"**.
- **SoftBank Vision Fund: $1.5 B (feb-2019)** a valoración **> $9 B**. Ronda previa ~**$200 M** (Sequoia China lid).
- **Inversores:** **HongShan / Sequoia Capital China**, **H Capital**, **IDG Capital**, **SoftBank Vision Fund**,
  **Tencent**, **HIKE Capital**, IDG. (TechCrunch; Bloomberg; en.guazi.com/about.)

**Categorías de producto:**
(1) **Marketplace de transacción de usado** (núcleo) — C2C / plataforma de terceros.
(2) **Inspección de vehículo** — informe **259 puntos** + **3D** (doméstico); **200+/300 puntos** (export).
(3) **Estimación/pricing oficial** (智能定价 "intelligent pricing") sobre datos de transacción propios.
(4) **Inteligencia de mercado publicada** — 保值率榜单 (residual), 推荐指数 (índice de recomendación), 年度趋势报告 (informe anual).
(5) **Servicios de transacción** — financiación, logística, garantías/post-venta, escrow.
(6) **Exportación internacional** (2026) — subasta + FOB para dealers de ultramar.
(7) **Hermano de grupo: Maodou (毛豆新车)** — venta de coche **nuevo** (venta directa + leasing financiero). [no es producto de datos]

**Cliente objetivo:** Consumidores chinos (comprar/vender), **10.000+ dealers certificados** (desde el giro a plataforma de
terceros 2023), y **dealers/importadores internacionales** (export 2026). (chinanews 2023; en.guazi.com.)

---

## 2. Cobertura

- **Doméstica:** **China continental** — **>200 ciudades / 30 provincias**. `[VERIFICADO]` (Wikipedia; PR 2026; guazi.com).
- **Export (2026):** envío a **50+ países** (en.guazi.com/about: "50+ active markets"; /dealerships: "70+ countries").
  Mercados tempranos declarados: **África, Oriente Medio, Asia Central, Europa del Este**. Operaciones concretas:
  **Georgia** (socio designado **AIG**) y **Ghana** (equipo local directo). Países citados en listings: Argelia, Ghana,
  Nigeria, Ruanda, Angola, EAU, Arabia Saudí, Kazajistán, Uzbekistán, Argentina, Chile, Colombia, Perú, Polonia, Albania.
  (en.guazi.com; financialcontent PR 2026-06-22.) `[VERIFICADO en vivo]`
- **Nuevo vs usado:** **usado** es el 100% de Guazi. El **nuevo** vive en la marca hermana **Maodou** (no auditada aquí). `[VERIFICADO]`
- **Tipos de vehículo:** turismo (sedán, hatchback, **SUV**, **MPV**, familiar/wagon, deportivo, **pickup**), y en filtro doméstico
  también **bus / camión (客车/货车)**. Energía: **燃油 (combustión)** y **新能源 (NEV/eléctrico)** como categoría propia. `[VERIFICADO]`
- **Escala de datos:** **>30 millones de vehículos inspeccionados** acumulados (PR 2026; ~15 M reportados a 2023 → coherente);
  **>3 millones de transacciones** de usado completadas; **200K+** vehículos listados/año, **300K+** transaccionados/año,
  **800K+ usuarios activos diarios** (export/about). `[PARCIAL — marketing/PR]`

---

## 3. Productos + campos atómicos

### 3.1 Ficha de vehículo / anuncio (doméstica) — `[VERIFICADO en vivo guazi.com]`

Campos mostrados por coche (tarjeta de resultados + detalle):

`品牌/marca` · `车系/serie` · `车型·款型/trim·edición` · `年份/año` · `上牌时间/fecha 1ª matrícula` ·
`行驶里程 (km)` · `车身类型/carrocería` (sedán/hatch/SUV/MPV/wagon/deportivo/pickup/bus/camión) ·
`排量/cilindrada (ej. 1.5L)` · `变速箱/transmisión (MT/AT)` · `发动机类型/tipo motor` · `驱动/tracción` ·
`车门数/puertas` · `能源类型 (燃油/新能源)` · `排放标准/norma emisiones` · `车身颜色/color` ·
`城市/ciudad` · `售价/precio de venta` · **`已减X万/descuento aplicado`** · **`官方估价/estimación oficial`** ·
`首付·月供/entrada·cuota (financiación)` · `卖家类型 (车商/个人)`.

**Insignias de condición/mercado (badges):** **`已检测` (inspeccionado)** · **`高保值` (alto valor residual)** ·
**`车主急售` (venta urgente del dueño)** + etiquetas de garantía **`终身全额退` / `3天无理由退车`**.

### 3.2 Ficha de vehículo (EXPORT, en.guazi.com) — `[VERIFICADO en vivo]`

Campos por listing internacional:

`make / model / year` · `engine displacement (1.5L)` · `mileage (km)` · `transmission (MT/AT)` ·
`drive type (2WD/4WD)` · `seat count` · **`condition grade (S / A / B / C / D)`** · **`FOB price (USD)`** ·
`seller type (Guazi Owned / Certified Dealer / Individual)` · `Newly listed` · `Guazi Inspected (badge)`.

**Rango FOB observado en muestras:** **$1,669 – $14,579**. **Tipo de listado:** `Sealed-Bid Auction` / `Live Auction` / `Buy It Now`.

**Filtros del inventario export** (en.guazi.com/used-cars): `Vehicle Source` (Guazi Owned/Certified Dealer/Individual) ·
`Make & Model` · `Price Range (solo buy-it-now)` · `Manufacturing Year` · `1st Registration Year` · `Model Year` (From/To) ·
`Mileage (0–100+)` · `Fuel Type & Battery` · **`EV Battery type & capacity`** · `Condition Grade S–D` · `Body Type` ·
**`Horsepower (0–1000+ ps)`** · `Engine displacement (0–10+ L)` · `Transmission & Drivetrain` · `Exterior Color` · `Seating`.
> Nota: al renderizar `/used-cars/` devolvió **"0 RESULTS"** (inventario carga vía JS / posible geo-gate); campos inferidos de filtros + tarjetas de muestra. `[PARCIAL]`

### 3.3 Informe de inspección — 259 puntos + 3D (doméstico) — `[VERIFICADO ×3 fuentes]`

**Sistema de inspección de 5 dimensiones:**
`人工信息核验` (verificación manual de info) → `259项专业检测` (259 inspecciones) → `保险/维修信息调取` (recuperación de
historial seguro/mantenimiento) → `二次车况复核` (re-verificación) → `上线前综合复检` (re-inspección integral pre-publicación).

**Estructura del informe (5 bloques):**
1. **评估师总结 + 评分** (resumen del tasador + puntuación del vehículo).
2. **车辆基本信息** (datos básicos).
3. **6 categorías mayores** (cada una con "各级小项目" = subítems, suman 259):
   - **主框架结构** (estructura del bastidor / chasis principal)
   - **外观内饰** (exterior e interior)
   - **安全气囊 / 灯光** (airbags y luces)
   - **发动机舱** (vano motor)
   - **启动检测** (arranque/funcionamiento)
   - **底盘悬挂** (chasis y suspensión)
4. **瑕疵明示 en primera página** (los defectos se muestran directamente en la página 1).
5. **Informe 3D 360°** (control con el dedo para ver ángulos/detalles; "primer informe 3D del sector" según Guazi).

**Flags de condición derivados:** `事故车` (coche accidentado) · `泡水车` (inundado) · `火烧车` (incendiado) — además
**informe de historial de accidentes gratuito** entregado por la plataforma (desde 2023). `inspection_score` (puntuación de inspección).

> Inconsistencia de marketing a documentar: **doméstico = 259 puntos**; **export = "200+ point" (home) / "300-point" (dealerships) / "300+ quality checks"**. Mismo informe, cifras divergentes según página. `[VERIFICADO la divergencia]`

### 3.4 Estimación / pricing oficial (官方估价 / 智能定价) — `[VERIFICADO]`

- **Inputs (formulario "免费估价"/gratis):** `品牌车系` (marca/serie) · `上牌时间` (fecha matrícula) · `行驶里程` (km) ·
  `城市` (ciudad) · `联系方式` (contacto — lead-gen). Canales: app ("立即估价"/"免费估价"), web `/estimación`, mini-programa WeChat.
- **Output:** `车辆估价` (precio estimado). No se confirma públicamente si entrega rango o desglose. `[PARCIAL]`
- **Motor:** "智能定价/智能算法" sobre **"上百万的独家真实成交数据"** (millones de transacciones reales exclusivas) +
  **resultados de inspección** + **市场行情/最新行情** (condiciones de mercado vigentes) + antigüedad. (autohome chejiahao; bjd.com.cn.)
- **Activos:** **>15 M (2023) → >30 M (2026)** vehículos inspeccionados; datos de **3 M+ transacciones** propias.

### 3.5 Inteligencia de mercado publicada (informes) — el ángulo "insights" — `[VERIFICADO ×2]`

**(a) 保值率榜单 (Residual / retention rate report)** — sobre datos reales de transacción + stock en venta:
- **保值率 % a 1 / 2 / 3 años** por marca/serie; segmentado **燃油 (ICE)** vs **新能源 (NEV)**.
- Cifras citadas: ICE año-1 ≈ **66%**, año-3 ≈ **50%**; ICE top-3-años Toyota/Honda (汉兰达/飞度/雅阁) **>65%**;
  NEV se deprecia más rápido (3 años suele >50% de pérdida); **Xiaomi SU7 >90% a 1 año**, **Huawei 鸿蒙智行 86%**,
  **Porsche Taycan 80% / Panamera 70%**; lujo >500k RMB ~20% pierde +50% el año 1.
- **Curva de depreciación por antigüedad (1–8 años)**: **28% · 37.1% · 46.1% · 52.7% · 58.5% · 64.0% · 69.7% · 73.7%** (折价率).
- Dimensiones extra: **prima por color** (champán/negro/rojo más alto; gris-plata más bajo), **dispersión regional** (Shanghái–Xi'an gap 15%).

**(b) 推荐指数 (Recommendation Index)** — score **escala 10** sobre **5 dimensiones**:
`车辆质量` (calidad) · `使用成本` (coste de uso) · `消费热度` (popularidad/demanda) · `驾乘感受` (experiencia de conducción) ·
`保值率/折价率` (residual/depreciación). Salida: **Top-20 series** por tipo de carrocería con score por dimensión + global.

**(c) 年度趋势报告 — "九大数据洞察" (9 insights, anual)** — métricas atómicas:
1. **Ranking de保值率** (ICE+NEV). 2. **Mejor momento para vender** (curva precio×antigüedad). 3. **Estructura de车龄** (antigüedad vs media sector).
4. **Ranking de ventas/热销** (por nº de transacciones). 5. **Disparidad búsqueda↔venta** (关注度 vs 成交).
6. **Upgrade de consumo** (mix por banda de precio; Guazi mainstream >¥50k vs nacional 60% <¥50k).
7. **Flujo inter-provincial** (跨省: nacional **33.1%**; Guazi cross-city ~**90%**). 8. **Variación de precio regional** (Pekín media ¥100k+, Qinghai ~¥90k).
9. **Geografía NEV** (penetración nacional **11.2%** oct-2025; hubs regionales ≥30%).

### 3.6 Garantías / estándar de plataforma (atributos de servicio, no datos) — `[VERIFICADO ×2]`

Desde **mar-2023 (giro a plataforma de tercero, "primer estándar de garantía a nivel plataforma del sector")**, 3 categorías:
- **车况 (condición):** inspección real por profesional antes de entrega · **informe de accidentes gratuito** · **vídeo-inspección 1-a-1 del dealer**.
- **交易 (transacción):** **车款居间担保** (escrow/garantía del pago por la plataforma).
- **售后 (post-venta):** **7天无理由退车** (prueba 7 días / hasta 450 km, devolución sin motivo) · **30天可置换/全面保修** ·
  **1年或2万公里质保** · **重大事故/火烧/泡水车终身全额退** (reembolso íntegro de por vida). **NPS reportado: 52.0**.
- En export: **"accident-free & flood-free guarantee"**.

---

## 4. Metodología / fuentes de datos

- **Datos propietarios de transacción:** "上百万的独家真实成交数据" (millones de cierres reales exclusivos) — al ser el
  propio marketplace, Guazi observa **precio de listado, descuentos, tiempo y precio de cierre** de primera mano. `[VERIFICADO]`
- **Inspección propia:** **30 M+ vehículos** inspeccionados por técnicos certificados (259 puntos doméstico). Genera dataset
  de condición ligado a precio. `[PARCIAL — cifra PR]`
- **Historial externo cruzado:** recuperación de **保险 (seguro)** y **维修保养 (mantenimiento)** para el informe de condición. `[VERIFICADO]`
- **Modelo de pricing:** "智能算法/智能定价" (ML sobre transacciones reales + inspección + market行情 + antigüedad). Sin
  documento técnico público de pesos/curva. `[PARCIAL]`
- **Informes de mercado:** sobre **成交数据 (transacciones)** + **在售数据 (stock en venta en tiempo real)**; referencia cruzada
  con datos de la **中国汽车流通协会 (China Automobile Dealers Association)** en el informe anual. `[VERIFICADO ×2]`
- **Infraestructura de datos interna:** data warehouse (feb-2023), **Kafka**, formato **AVRO**, "90%+ de datos estructurados".
  Es ingeniería interna, **no un producto de datos vendido**. `[PARCIAL — blogs técnicos]`

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Web consumo** | `guazi.com` (compra) · `m.guazi.com` (móvil) · `sell.guazi.com/evaluate` (estimación) · `sell.guazi.com/market-pc/base` (高价卖车). Solo chino. |
| **App** | 瓜子二手车 (iOS/Android) — comprar/vender/估价/检测报告/车主. |
| **Mini-programa** | WeChat (估价 gratis). |
| **Web export** | **`en.guazi.com`** ("Guazi Official", inglés) — inventario, subasta, FOB, /dealerships, /about, /used-cars/[marca]. |
| **Web export 2** | **`globalguazi.com`** (Chongqing Guazi, "wholly-owned subsidiary"). |
| **Inspección** | Informe **259 puntos + 3D 360°** (in-app / ficha). Export: informe + **vídeo+fotos HD**. |
| **Informes / research** | 保值率榜单 · 推荐指数 · 年度趋势报告 (PR/medios: jiemian, sina, caijing) — **no es dashboard ni feed; son informes/notas de prensa**. |
| **Logística (doméstico)** | Línea logística propia nacional; entrega a puerto **3–5 días** (globalguazi). |
| **Logística (export)** | **Container + Ro-Ro**; entrega **35–45 días**; gestión de documentación de exportación + despacho de aduanas; tracking; pago por transferencia bancaria con registro oficial; soporte 24/7 multilingüe. |
| **API de datos** | **NO hay API/feed de datos oficial.** El "API de Guazi" que circula (`auto-api.com/guazi`) es un **revendedor/scraper de terceros**, no oficial. `[VERIFICADO]` |

---

## 6. Precio

- **Marketplace (consumo):** comprar/vender y **estimación = gratis** para el usuario (lead-gen: pide contacto). Guazi monetiza
  por **comisión/servicio de transacción, financiación y garantías** (modelo de plataforma de terceros desde 2023). `[PARCIAL]`
- **Export:** **FOB fijo (USD)** por coche (muestras **$1,669–$14,579**) **o** **subasta** (sealed-bid/live, con depósito de puja).
  Sin mínimos de pedido ni tarifa de servicio export divulgados. `[VERIFICADO el modelo / NO-VERIF importes de servicio]`
- **Datos/inteligencia:** **sin tarifa** — porque **no se vende como producto**; los informes son gratuitos (marketing). `[VERIFICADO]`

---

## 7. Placement (patrón web — clave para cardeep)

> Verificado en vivo (WebFetch, 2026-06-30) salvo donde se indica. Es el patrón "portal + insights" que cardeep replica.

**A. Tarjeta de resultados (listado doméstico).** Foto + título (marca+serie+año+trim) + línea de specs (km · ciudad · año) +
**precio grande** + **`已减X万` (descuento)** + **badges** (`已检测` / `高保值` / `车主急售`) + tags de garantía. → patrón de
"señal de confianza + ancla de precio" en la propia tarjeta.

**B. Ficha de detalle (doméstica).** Galería + **visor de inspección 3D 360°** arriba; **precio + `官方估价` (comparativa)**;
bloque **financiación (首付/月供)**; sección **informe 259 puntos** (defectos en página 1, 6 categorías, score, resumen del
tasador); **informe de accidentes gratuito**; **panel de garantías** (7 días / 30 días / 1 año·2万km / reembolso vitalicio /
escrow). → cada dato de confianza tiene su sección fija.

**C. Página de venta / estimación (`sell.guazi.com/evaluate`).** Formulario en pasos: marca·serie → fecha matrícula → km →
ciudad·contacto → **resultado de estimación**. → patrón de valoración guiada lead-gen.

**D. Insights (no dashboard).** Las métricas de mercado (保值率, 推荐指数 10-pt, curva de depreciación 1–8 años, 9 insights
anuales) se publican como **informes/rankings en prensa y blog**, no como panel interactivo ni API. → para cardeep: el dato
existe pero su *placement* es editorial, no producto.

**E. Tarjeta de listing EXPORT (`en.guazi.com`).** make·model·year + (displacement · mileage · transmission · drive · seats) +
**`condition grade S–D`** + **`FOB price USD`** + **`seller type`** + **`Guazi Inspected` badge** + toggle
**Auction / Buy-It-Now / Live Auction**. → ancla por **grado de condición (S–D)** y **precio FOB**, no por estimación.

**F. Página de dealers export (`/dealerships`).** Propuesta mayorista: inventario masivo + **sourcing a medida** + inspección
300-pt + garantía accident/flood-free + shipping (container/Ro-Ro, 35–45 días) + docs/aduanas + pago bancario con registro.

**G. Flujo de subasta export.** `Find → Bid → Register deposit → Win → 72h seller confirmation → Export & shipping`.
Contadores en vivo: "X Vehicles Under Auction" / "Y Vehicles Available (Buy It Now)".

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Datos de transacción de primera mano a escala nacional china:** es el **propio marketplace** (>3 M transacciones, 30 M+
   inspecciones) → ve precio de cierre real, descuento y tiempo, no solo anuncios. Pocos rivales globales tienen esta señal directa.
2. **Informe de inspección 259 puntos + 3D 360° orientado a consumidor**, con **defectos en la página 1** — UX de transparencia
   de condición muy por delante de una simple lista de specs.
3. **Estimación oficial embebida (`官方估价`)** anclada a transacciones reales + inspección propia, dentro de la ficha.
4. **Índice de recomendación de 5 dimensiones (calidad·coste·demanda·conducción·residual) en escala 10** + **curva de
   depreciación por antigüedad (1–8 años)** publicada — inteligencia de mercado lista para consumo.
5. **Estándar de garantía a nivel plataforma** (escrow + reembolso vitalicio por accidente/incendio/inundación + 7 días prueba) —
   diferencial de confianza en transacción.
6. **Capa de exportación 2026 (subasta + FOB) con grados S–D** que conecta inventario chino con **50–70+ países** — convierte el
   dato doméstico en producto transfronterizo (China-out), algo raro entre portales nacionales.
7. **Categoría NEV de primer nivel** (保值率 NEV específico, penetración regional, batería/capacidad en filtros export).

---

## 9. Gaps (lo que NO ofrece)

1. **NO es un proveedor de datos:** sin **API/feed/dataset licenciado** de valoración o specs (el único "API" es un **scraper de
   terceros** no oficial). Su inteligencia no es comprable como producto B2B (a diferencia de Che300/KBB/cap-hpi). ← gap central.
2. **Insights = editorial, no analítico:** residual, índice y tendencias salen como **informes de prensa**, no como **dashboard,
   query, ni serie histórica descargable**. No hay days-to-sell / market-days-supply / price-to-market como métrica-producto.
3. **Doméstico solo en chino** y **export aún incipiente** (jun-2026, Georgia/Ghana; inventario `/used-cars` daba 0 resultados al render). `[PARCIAL]`
4. **Estimación lead-gen:** exige `联系方�/contacto` y no garantiza desglose/rango público; no es valoración transparente abierta.
5. **Credibilidad de la inspección cuestionada:** exposés de **CCTV/央视** y prensa (coches泡水 pasados como "normales";
   crítica "juez y parte" — Guazi fija el estándar y emplea a los inspectores). Riesgo reputacional sobre el dato de condición. `[VERIFICADO la controversia]`
6. **Cifras de inspección inconsistentes** (259 vs 200+ vs 300) y métricas export tipo placeholder roto en globalguazi ("3 Vehicles
   Listed Every Year"). Señal de capas de marketing no reconciliadas. `[VERIFICADO]`
7. **Linkaje corporativo del export opaco:** las propiedades en inglés **no nombran a Chehaoduo** y citan 3 sociedades distintas. `[PARCIAL]`
8. **Sin VIN-decode-as-a-service, sin catálogo de specs profundo vendible, sin TCO, sin curva de depreciación por VIN/config descargable.**
9. **No valora coche nuevo como dato** (eso es Maodou, y es retail/leasing, no inteligencia).

---

## 10. Fuentes

**Producto en vivo (WebFetch 2026-06-30):**
- Doméstico: https://www.guazi.com/  · Estimación: https://sell.guazi.com/evaluate/ad  · 高价卖车: https://sell.guazi.com/market-pc/base
- Export: https://en.guazi.com/  · https://en.guazi.com/about/  · https://en.guazi.com/dealerships/  · https://en.guazi.com/used-cars/
- Export 2: https://www.globalguazi.com/  · https://www.globalguazi.com/application/used-cars-for-export-from-china

**Identidad / financiación:**
- Wikipedia: https://en.wikipedia.org/wiki/Guazi.com
- Crunchbase (Chehaoduo): https://www.crunchbase.com/organization/guazi-com  · Yang Haoyong: https://www.crunchbase.com/person/haoyong-yang
- CB Insights: https://www.cbinsights.com/company/guazi  · People: https://www.cbinsights.com/company/guazi/people
- SoftBank $1.5B / $9B: https://techcrunch.com/2019/02/28/softbank-invests-1-5-billion-in-chehaoduo/  · https://www.bloomberg.com/news/articles/2019-02-28/softbank-vision-fund-bets-1-5-billion-on-china-used-cars-giant  · https://www.dealstreetasia.com/stories/chehaoduo-softbank-vision-fund-123617
- Ganji→Guazi (Yang Haoyong CEO): https://www.prnewswire.com/news-releases/ganji-founder-to-serve-as-chairman-and-ceo-of-guazi-used-car-business-and-stepdown-as-58com-co-ceo-300184378.html
- Baidu Baike (Yang Haoyong): https://baike.baidu.com/en/item/Yang%20Haoyong/67829  · Guazi: https://baike.baidu.com/en/item/Guazi%20Used%20Car/18854

**Inspección / garantías / plataforma de terceros:**
- 3D / 259 puntos: https://news.mydrivers.com/1/552/552853.htm
- Estándar de garantía 2023 (3ª-parte): https://www.chinanews.com.cn/cj/2023/03-16/9972806.shtml  · http://www.cnautonews.com/houshichang/2023/03/24/detail_20230324355828.html
- 全国购 (cross-region, garantías): https://baike.baidu.com/item/瓜子二手车全国购/23798337 (HTTP 403 al fetch) · https://auto.youth.cn/xw/201903/t20190307_11890004.htm
- 7 días prueba / 三包: https://chejiahao.autohome.com.cn/info/15320732  · https://www.nbd.com.cn/articles/2020-10-06/1517822.html
- Controversia inspección (央视): http://jres2023.xhby.net/index/201908/t20190820_6304461.shtml  · https://www.jiemian.com/article/3483488.html

**Pricing / estimación:**
- Cómo funciona la estimación: https://chejiahao.autohome.com.cn/info/15320729  · https://wap.bjd.com.cn/news/2023/05/06/10422489.shtml

**Inteligencia de mercado (insights):**
- 保值率 NEV report: https://www.digitaling.com/articles/1287299.html  · https://m.mp.oeeee.com/a/BAAFRD0000202411181025876.html
- 2025 年度趋势 (9 insights): https://m.jiemian.com/article/13808985.html  · https://finance.sina.com.cn/stock/relnews/hk/2025-12-26/doc-inhecrxf2586257.shtml  · https://news.caijingmobile.com/article/detail/561285
- 推荐指数 report: https://www.pai.com.cn/203147.html
- 大数据 (极氪/理想 ejemplos): https://finance.sina.com.cn/jjxw/2024-12-12/doc-inczezhm2931140.shtml

**Export / expansión 2026:**
- PR (accesswire, 2026-06-22): https://markets.financialcontent.com/stocks/article/accwirecq-2026-6-22-guazi-expands-inspection-backed-used-car-sourcing-from-china-for-overseas-markets  · https://finance.yahoo.com/small-business/articles/guazi-expands-inspection-backed-used-074500831.html

**Tercero (NO oficial — solo para fields de listado):**
- Scraper/reseller: https://auto-api.com/guazi

### Notas de verificación
- **Dualidad doméstico/export, fichas, 259+3D, garantías 2023, modelo subasta+FOB, grados S–D, 9 insights, índice 5-dim, curva
  depreciación 1–8 años:** `[VERIFICADO]` en vivo o ×2 fuentes.
- **Linkaje corporativo del export con Chehaoduo, co-fundadores, importes de financiación exactos, rango/desglose de la estimación:** `[PARCIAL]`.
- **Importes de servicio export, mínimos de pedido, pesos del modelo de pricing, escala de车型库:** `[NO-VERIF]` (no divulgados).
- **Cifra de puntos de inspección:** divergencia real documentada (259 / 200+ / 300) — no se "resuelve", se reporta.
- `auto-api.com/guazi` es **scraper de terceros**, NO API oficial de Guazi — usado solo para confirmar nombres de campos de listado.
