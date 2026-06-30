# Autohome (汽车之家) — Auditoría atómica

> Slug: `autohome` · Subdominio cardeep: **portal-insights** · Región: **China (RPC)** · Auditado: 2026-06-30
> Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` = leído en vivo/fuente directa, `[PARCIAL]` =
> parcial/derivado/con fecha, `[NO-VERIF]` = no confirmado / tras login / no divulgado. JAMÁS inventar.
> Naturaleza: **el portal vertical de automoción nº1 de China por tráfico** (≈77,5M DAU móvil) — a la vez
> **medio/contenido + catálogo de coche nuevo + marketplace de usado + plataforma de transacción + brazo de
> datos/IA B2B** para fabricantes (主机厂) y concesionarios (经销商). Cotiza **NYSE: ATHM** (2013) y **HKEX: 2518**
> (2021). Desde **27-ago-2025 controlada por Haier Group** (vía CARTECH, ~43%), tras casi una década bajo
> **Ping An** (vía Yun Chen Capital). Se autodefine en transición de **"medio vertical basado en contenido" →
> "compañía tecnológica basada en datos"**. Opera tres plataformas: **autohome.com.cn** (portal), **che168.com**
> (二手车之家, usado) y **ttpai.cn** (天天拍车 / TTP, subasta C2B). NO es un "libro de valoración" puro tipo
> Eurotax/KBB: la valoración de usado y el 保值率 (residual) son **una capa más** dentro de un ecosistema mucho
> mayor de tráfico de consumo + inteligencia de mercado vendida a la industria.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Marca | **汽车之家 / Autohome** | autohome.com.cn |
| Razón social | **Autohome Inc.** (holding Cayman) | SEC 20-F; ir.autohome.com.cn |
| Cotización | **NYSE: ATHM** (ADS, dic-2013) · **HKEX: 2518** (acciones ordinarias, sec. listing mar-2021 `[PARCIAL fecha]`) | crunchbase; ir.autohome |
| Fundación | **2005** (portal lanzado 2005); incorporada en Cayman **2008** | dcfmodeling; crunchbase |
| Fundador | **李想 (Li Xiang)** — cofundador en 2005; después fundaría **Li Auto (理想汽车)** `[PARCIAL — ampliamente reportado, no re-verificado esta sesión]` | conocimiento general/prensa |
| HQ | **Pekín (Beijing), China** | crunchbase; SEC |
| Empleados | **4.415** (incl. **1.332 de TTP Car, Inc.**), a 31-dic-2024 | release Q4-2024 |
| Caja + inversiones CP | **RMB 23.320M (US$3.190M)** a 31-dic-2024 | release Q4-2024 |
| Misión declarada | "The leading online destination for automobile consumers in China"; "reducir sin descanso los costes de decisión y transacción del sector auto mediante tecnología avanzada" | release Q4-2024 (boilerplate oficial) |
| Posicionamiento estratégico | Transición de **"medio vertical basado en contenido" → "compañía tecnológica basada en datos"** ("用科技服务用户，用科技赋能经销商") | caam.org.cn; jiemian |

**Cambio de control (VERIFICADO, múltiples fuentes concordantes):**
- Histórico de propiedad: **Telstra (Australia)** → **Ping An** (2016, vía **Yun Chen Capital Cayman**) → **Haier Group**.
- **20-feb-2025:** Yun Chen Capital Cayman (filial de Ping An) firma SPA para vender **200.884.012 acciones (~41,91%)**
  a **CARTECH HOLDING COMPANY** (filial de **Haier Group Corporation**) por **~US$1.800M**.
- **Cierre 27-ago-2025:** CARTECH pasa a **~43,0%** y se convierte en **accionista de control**; Yun Chen (Ping An)
  baja a **~5,1%** y deja de controlar. Cambio simultáneo de **dirección/CEO**.
- (Fuentes: PR Newswire / ir.autohome "Change in Controlling Shareholder"; StockTitan ATHM; Clifford Chance
  "advises Haier on antitrust filings"; Law.asia "Firms steer Haier unit's USD1.8bn stake buy"; SEC 6-K FY2025.)

**Categorías de negocio (3 segmentos de reporte + capa de datos transversal):**
1. **Media Services (媒体服务)** — publicidad de fabricantes y concesionarios.
2. **Leads Generation Services (线索服务)** — **leads de venta + análisis de datos + servicios de marketing**
   para concesionarios; **aquí viven los productos de datos/IA** (suscripción dealer).
3. **Online Marketplace and Others (在线交易及其他)** — financiación de auto, seguro, **transacciones de usado**,
   aftermarket, **Autohome Mall**.
   (Fuente: boilerplate oficial release Q4-2024.)

**Cliente objetivo:** (a) **Consumidores** (selección/compra/uso/cambio de coche); (b) **Concesionarios (经销商)**
— suscripción + leads + herramientas de datos/IA; (c) **Fabricantes / OEM (主机厂/车企)** — publicidad + big data
estratégico (车智云); (d) indirectamente **financieras y aseguradoras** (vía datos de residual/保值率).
(Fuentes: SEC; caam.org.cn; bigdata.autohome.)

---

## 2. Cobertura

- **Geografía:** **China continental (RPC) únicamente.** Sin cobertura internacional. Granularidad **provincia +
  ciudad** (报价 de concesionario por ciudad; valoración de usado por ciudad). `[VERIFICADO]`
- **Nuevo y usado:**
  - **Nuevo:** catálogo de specs (车型库/参数配置), precios (指导价/经销商报价/车主价格), 口碑, ventas, 保值率.
  - **Usado:** marketplace **che168 (二手车之家)** + valoración + **subasta C2B TTP (天天拍车)**.
- **Tipos de vehículo (navegación del catálogo):** **轿车 (sedán)** · **SUV** · **MPV** · **跑车 (deportivo)** ·
  **皮卡 (pickup)** · **新能源 (NEV: BEV/PHEV/EREV/FCEV)** · **摩托车 (moto)**. `[VERIFICADO home/car catalog]`
- **Escala de datos (base del informe de 保值率 2021, cifras con fecha):** `[VERIFICADO release/news]`
  - **4,5M tipos de vehículo (车型)** en circulación.
  - **40M+ anuncios online** (vehicle listings).
  - **6M precios reales de propietario** (车主价格).
  - **200M+ registros de seguro** (datos de **Ping An**).
  - **1M+ registros de transacción de usado.**
- **Tráfico (métrica estrella, con fecha):** **DAU móvil promedio dic-2024 = 77,48M (+13,6% YoY)**; serie 2024:
  69,39M (mar) → 67,91M (jun) → 72,87M (sep) → 77,48M (dic). **Mayor plataforma de medios de auto de China por
  tráfico.** `[VERIFICADO releases trimestrales]`
- **Presencia física:** **150+ "Autohome Space" y satellite stores** (O2O). `[VERIFICADO Q4-2024]`

---

## 3. Productos + campos atómicos

> Mezcla de **consumo (gratis)** e **inteligencia B2B (de pago)**. Esquemas de specs y precios verificados en vivo
> (home, car catalog, che168, k.autohome); los productos B2B (车智云, 销售宝, suite AI) verificados por páginas de
> producto + artículos oficiales + releases; **valores numéricos B2B tras login/contrato → [NO-VERIF]**.

### 3.1 车型库 / 参数配置 (catálogo de specs de coche NUEVO) — núcleo gratuito

**Bloque de PRECIO (por modelo/版本):**
- **厂商指导价 (MSRP / precio guía del fabricante).**
- **经销商报价 / 经销商参考价 (precio del concesionario, regionalizado por ciudad).**
- **车主价格 (precio real de propietario)** — precio de transacción real subido por propietarios (requiere
  **factura**), señal de precio real de calle. Producto/columna propia "车主价格". `[VERIFICADO búsqueda + chejiahao]`
- **官方降价 / 降价 (caída de precio)** y **超级补贴 (subsidio super)** — promociones/descuento sobre el indicado.

**Taxonomía de categorías de specs (confirmada en la propia 百科/参数详解 de Autohome — la tabla de configuración
más exhaustiva de China; enumeración de cada campo individual `[PARCIAL]` por gate JS):** `[VERIFICADO categorías]`

| Categoría (CN) | Contenido atómico (campos representativos) |
|---|---|
| **基本参数/基本信息** | clase de vehículo (级别), 0–100 km/h, distancia de frenado, consumo combinado, garantía (质保) |
| **车身 (Body)** | largo/ancho/alto, **batalla (轴距)**, vías, distancia al suelo (离地间隙), nº de puertas/asientos (座位数), volumen de maletero (行李厢容积), peso |
| **发动机 (Engine)** | cilindrada (排量), tipo (自然吸气/涡轮增压/混动), potencia máx (最大功率), par máx (最大扭矩), nº cilindros, combustible, **norma de emisiones (排放标准)** |
| **电动机 (Motor eléctrico)** | potencia/par del motor, nº de motores, ubicación |
| **电池/充电 (Batería/Carga)** | capacidad de batería (kWh), tipo/química, **autonomía WLTC/CLTC/NEDC**, consumo eléctrico, tiempo de carga (rápida/lenta) |
| **变速箱 (Transmisión)** | tipo (manual/AT/CVT/doble embrague/secuencial), nº de marchas |
| **底盘转向 (Chasis/Dirección)** | tracción (前/后/四驱), suspensión delantera/trasera, tipo de dirección, **control por cable (线控)** |
| **车轮制动 (Ruedas/Freno)** | neumático delantero/trasero, llanta, rueda de repuesto, tipo de freno |
| **主动安全 (Seguridad activa)** | ABS/EBD/ESP, **frenada autónoma/anticolisión (主动刹车)**, aviso de colisión, control de crucero adaptativo (ACC), aviso/mantenimiento de carril `[campos típicos; enumeración exacta PARCIAL]` |
| **被动安全 (Seguridad pasiva)** | airbags (frontal/lateral/cortina/rodilla), anclajes ISOFIX, llamada de emergencia |
| **辅助/操控配置 (Asistencia/Manejo)** | sensores/cámara de aparcamiento, cámara 360°, aparcamiento automático, sensores, HUD, modos de conducción |
| **外部/防盗配置 (Exterior/Antirrobo)** | techo solar, barras de techo, llantas, alarma, cierre centralizado, entrada sin llave |
| **内部配置 (Interior)** | volante (cuero/multifunción/levas), pantalla, llave inteligente, arranque por botón |
| **座椅配置 (Asientos)** | material, ajustes eléctricos, calefacción/ventilación/masaje, memoria, abatible |
| **多媒体配置 (Multimedia)** | pantalla central, navegación, CarPlay/Android, sonido, conectividad, voz |
| **灯光配置 (Iluminación)** | tipo de faros (LED/láser), antiniebla, automáticos, adaptativos |
| **玻璃/后视镜 (Cristal/Espejos)** | elevalunas, espejos eléctricos/calefactados/abatibles, antideslumbrante |
| **空调/冰箱 (Clima/Nevera)** | A/A manual/auto, zonas, filtro PM2.5, nevera |
| **特色配置 / 智能硬件 (Especial/HW inteligente)** | configuración especial, hardware inteligente (chips ADAS, LIDAR, etc.) |

> Patrón: Autohome es **referencia de facto del catálogo de specs en China** (4,5M 车型). Incluye **comparador
> (车型对比)**, galería (图片/精图), **VR看车**, vídeo, **百科 (enciclopedia)** y **智能买车 (compra asistida IA)**.

### 3.2 口碑 (reseñas de propietario / word-of-mouth) — gratuito

- **Escala de puntuación: 5 puntos** (p. ej. "4,38分", "4,57分"). `[VERIFICADO k.autohome]`
- **Dimensiones de valoración (por modelo, media de propietarios):** **空间 (espacio)** · **动力 (potencia)** ·
  **操控 (manejo)** · **油耗/能耗 (consumo combustible/energía)** · **舒适性 (confort)** · **外观 (exterior)** ·
  **内饰 (interior)** · **配置 (equipamiento)** · **性价比 (relación valor/precio)** · (+ **续航/充电** y **智能化**
  para NEV). Cada dimensión con subítems (espacio frontal/trasero, maletero, ruido de cabina, suavidad de cambio,
  precisión de dirección, calidad de materiales, ADAS, etc.). `[VERIFICADO k.autohome]`
- Señal de **fiabilidad/uso (用车)**: satisfacción de mantenimiento + **tasa de fallo (故障率)**.

### 3.3 二手车估值 (valoración de usado — che168) — gratuito (tool de consumo)

**Inputs:** **品牌 (marca)** · **车型 (modelo)** · **上牌时间 (fecha de matriculación)** · **里程 (km)** ·
**城市 (ciudad)**. `[VERIFICADO che168/price]`

**Outputs (tres lados del mercado + residual):** `[VERIFICADO]`

| Campo (CN) | Significado |
|---|---|
| **个人收购价** | precio que un **particular** obtiene (lo que paga el comerciante al particular). |
| **商家收购价** | precio de **compra entre comerciantes** (wholesale/inter-dealer). |
| **商家零售价** | precio de **venta minorista del comerciante** (consumer-facing). |
| **保值率 (%)** | residual: valor actual frente al precio nuevo (指导价). |
| **新车价 / 新车参考价** | precio de referencia del coche nuevo equivalente. |
| **车龄** | edad (fecha matrícula) + km. |

> Estructura idéntica al patrón "matriz de 3 precios" del usado chino (cf. Che300: 收购/零售/个人). El **dictamen
> final autoritativo** lo da el **informe de inspección física del tasador**, no la estimación online.

### 3.4 保值率 (índice de retención de valor / residual) — producto de research, gratuito

- **Definición oficial:** "从新车购买之日起，使用一段时间后，**车辆交易价格 ÷ 新车厂商指导价(MSRP)** 的比值".
  (precio de transacción de usado / MSRP original). `[VERIFICADO autohome/news]`
- **Base de datos:** 4,5M 车型 + 40M+ anuncios + 6M precios de propietario + **200M+ registros de seguro (Ping An)**
  + 1M+ transacciones de usado. `[VERIFICADO]`
- **Segmentación del ranking:** `[VERIFICADO]`
  - **Por horizonte:** **保值率 a 3 años** (estándar para 燃油车) · **a 1 año** (estándar para NEV) (también 1/2/3 años).
  - **Por carrocería:** 轿车 / SUV / MPV · por tamaño (微型/紧凑/中型/大型).
  - **Por origen de marca:** importadas / japonesas / alemanas / italianas / francesas / **marcas chinas (自主)**.
  - **Por propulsión:** 燃油车 (combustión) / 纯电动 (BEV) / 插电混动 (PHEV).
  - **Métrica reportada:** **% exacto** de retención (p. ej. SUV 54,66%, sedán 56,28%, MPV 52,33%; Prado 3a 80,49%).
- Publicado como **ranking anual** ("中国汽车保值率排行榜") en colaboración con **TTP (天天拍车)** y citado por la
  **CADA / 中国汽车流通协会**. Referencia de mercado para consumidores, dealers, OEM y **financieras/aseguradoras**.

### 3.5 车况 / 检测报告 (historial e inspección de usado — che168/TTP)

- **检测报告 (informe de inspección):** **300+ ítems de calidad** (varía por programa de certificación de marca:
  Audi 110, Porsche 111, Volvo 123 puntos). Inspección física por **tasador certificado**. `[VERIFICADO búsqueda]`
- **车辆出险记录查询 (consulta de siniestros por seguro):** lookup **por VIN** (`che168.com/insurance`) — historial
  de partes/accidentes. `[VERIFICADO URL en vivo]`
- **维修保养 (registros de mantenimiento/reparación).**
- **公里数核查 (verificación de kilometraje)** — detección de manipulación de odómetro. `[PARCIAL]`
- **Bloques del sistema de inspección de TTP (天天拍车):** **车辆基本信息 (info básica)** · **配置信息 (config)** ·
  **事故车检测项 (detección de coche accidentado)** · **装置检查项 (verificación de dispositivos)** ·
  **外观检查项 (exterior)** · **内饰检查项 (interior)**. `[VERIFICADO chinadaily/ttpai]`

### 3.6 天天拍车 (TTP / ttpai.cn) — subasta C2B de usado

- **Modelo:** plataforma de **venta de particular a comerciante (C2B)** vía **subasta de segundo precio sellada
  (维克瑞竞价 / Vickrey, "暗标")** — el mejor postor gana y paga el **segundo** precio más alto. `[VERIFICADO]`
- **Servicios:** inspección y **estimación gratis a domicilio**, "闪电交易" (cierre el mismo día / <24h),
  competición nacional de pujas entre comerciantes. Coste 0 para el vendedor. `[VERIFICADO]`
- Es la **fuente de transacciones reales de usado** que alimenta el residual/保值率 y la valoración.

### 3.7 销量排行榜 (rankings de ventas) — gratuito

- **月销榜 (ranking mensual)** · **周销榜 (semanal)** · **品牌月销榜 (mensual por marca)** — por modelo, segmento,
  energía. Señal de demanda/popularidad de mercado. `[VERIFICADO home]`

### 3.8 车智云 (Chezhi Cloud) — BIG DATA estratégico para OEM (`bigdata.autohome.com.cn`)

> Plataforma de big data de **nivel estratégico para directivos de fabricantes**. Descompone el ciclo de vida del
> negocio del OEM (planificación, marketing, I+D) en **8 productos**. `[VERIFICADO chejiahao oficial + bigdata]`

**8 productos núcleo:**
1. **销量预测 (Sales Forecasting)** — predicción de ventas/tendencia de mercado.
2. **竞争格局 (Competitive Landscape)** — análisis de panorama competitivo / competidores.
3. **营销漏斗 (Marketing Funnel)** — embudo de marketing (atención→interés→lead→compra).
4. **传播监测 (Communication/Propagation Monitoring)** — monitoreo de difusión/舆情 (voz del mercado).
5. **线索分析 (Lead Analysis)** — análisis de leads.
6. **产品规划 (Product Planning)** — planificación de producto.
7. **配置策略 (Configuration Strategy)** — estrategia de configuración/equipamiento (qué specs llevar).
8. **产品改款 (Product Facelift/Redesign)** — estrategia de restyling/改款.

Escenarios de aplicación citados: **智策 (estrategia) / 智赢 (ganar) / 智造 (fabricar)** `[PARCIAL — el artículo
de detalle confirma los 8 productos pero no etiqueta explícitamente estos 3 tags]`. Cambia la lógica de decisión
de "问题导向" (orientada a problema) a "数据先行" (datos primero / predictiva).

### 3.9 Familia para CONCESIONARIO (销售宝 / 智慧网销 / 智慧集客)

- **销售宝 (Sales Pro)** — "primer producto de big data del sector hecho a medida del concesionario"; cubre
  **智慧集客 (captación inteligente)** + **智慧网销 (venta online inteligente)**. `[VERIFICADO]`
- Funciones núcleo: **智能展厅 (showroom inteligente)** · **智能选线索 (selección inteligente de leads)** ·
  **智能线索分配 (distribución inteligente de leads)** · **智能邀约提醒 (recordatorio de invitación)** ·
  **智能跟进推荐 (recomendación de seguimiento)**. `[VERIFICADO]`
- Otros productos "智慧系": **智慧数联 (Smart Data-Link)** — etiquetado/perfilado de usuario para targeting preciso;
  **智慧试驾 (Smart Test-Drive)** — SW+HW + control de calidad por IA para mejorar el test-drive. `[VERIFICADO]`
- Familia **车智库 (Vehicle Knowledge Base)** — datos de catálogo/configuración como servicio. `[PARCIAL]`

### 3.10 Suite AI 2025 — "五大数科产品线" (cinco líneas de producto data-science)

Productos AI que recorren todo el embudo de marketing (OEM + dealer): `[VERIFICADO chejiahao/cnr/sina]`
1. **AI营销大脑 (AI Marketing Brain)** — soporte de **decisión inteligente**; núcleo del framework **AI全域营销**
   (omni-domain marketing). Análisis multidimensional **VOC (Voice of Customer)**; **~30% de mejora de conversión**
   reportada. `[VERIFICADO ~30% release/cnr]`
2. **AI获客先锋 (AI Customer-Acquisition Pioneer)** — captación: ingreso de leads (线索入库), **pool de incubación
   automático (自动孵化池)**, operación por segmentos, aceleración de conversión.
3. **AI线索大师 (AI Lead Master)** — alcance/targeting preciso de usuario.
4. **AI销冠神器 (AI Sales Champion)** — empoderamiento de la capacidad de venta del comercial.
5. **AI查车专家 (AI Car-Inspection Expert)** — **evaluación de estado del vehículo / valoración de usado** asistida por IA.

**Base tecnológica IA:** `[VERIFICADO chinadaily/news.cn]`
- **仓颉大模型 (Cangjie/Canghai Large Model)** — **modelo fundacional propio** que potencia los servicios IA.
- **DeepSeek 智能体 (agente DeepSeek)** — agente desplegado para concesionarios (feb-2025).
- **AI数字人 (humano digital)** — avatar interactivo, asesoría 1:1 de selección de coche.
- **AI智能助手 (asistente inteligente)** — recomendación personalizada con **>90% de precisión de match**.
- Métrica de adopción: **>17 OEM** compraron productos "智能系" en 1T (vs 8 año previo); **>17.000 concesionarios**
  usan productos "智慧系" (vs 14.000); **ingreso de productos de datos +80% YoY**; 2023: **26.000+ dealers**, **5+
  productos por dealer**. `[VERIFICADO búsqueda/releases — cifras con fecha]`

### 3.11 Transacción / O2O (Online Marketplace)

- **Autohome Mall (商城)** — plataforma de transacción online. `[VERIFICADO SEC boilerplate]`
- **在线购车 (compra online completa)** — selección→pedido→aprobación financiera→factura (piloto Shenzhen/Xi'an, 2026).
- Ecosistema **nuevo + usado**: tasación/canje, financiación, seguro, **送车上门 (entrega a domicilio)**, cita de
  aftermarket. **硬货星期五 (Hardcore Friday)** — ofertas de usado subvencionadas. `[VERIFICADO news.cn 2026]`
- Servicios financieros: **financiación de auto, seguro** (segmento Online Marketplace). `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Comportamiento de usuario propio** (clickstream de ≈77,5M DAU): intención, configuraciones vistas, leads,
  embudo — base del 营销漏斗/线索分析 y del perfilado (智慧数联, user tagging por contrato y por usuario real,
  "20–500 usuarios cualificados por contrato"). `[VERIFICADO cnr]`
- **Precios:** **指导价** (del fabricante) + **经销商报价** (de la red, regionalizado) + **车主价格** (transacción
  real subida por propietario con factura). `[VERIFICADO]`
- **Residual/保值率:** 4,5M 车型 + 40M+ anuncios + 6M precios de propietario + **200M+ registros de seguro de
  Ping An** + 1M+ transacciones de usado; fórmula = precio de transacción usado / MSRP. `[VERIFICADO]`
- **Usado/condición:** transacciones reales de **TTP (subasta C2B)** + inspección física (300+ ítems) + **siniestros
  por VIN** (出险记录) + mantenimiento. `[VERIFICADO]`
- **VOC (Voice of Customer):** análisis multidimensional de feedback de cliente para los productos OEM. `[VERIFICADO]`
- **IA:** modelo fundacional propio **仓颉大模型** + integración DeepSeek; matching coche-cliente de alta precisión.
- ⚠ Nota de gobierno del dato: los **200M+ registros de seguro** provenían del ecosistema **Ping An**; tras el
  cambio de control a **Haier (ago-2025)** el acceso futuro a esa fuente **no está confirmado**. `[NO-VERIF post-2025]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web** | `autohome.com.cn` (选车/图库/排行榜/口碑/经销商/二手车/降价/用车…) | `[VERIFICADO]` |
| **Portal usado** | `che168.com` (二手车之家): listings, 估值, 保值率, 出险记录, 检测报告 | `[VERIFICADO]` |
| **Subasta C2B** | `ttpai.cn` (天天拍车 / TTP): estimación + inspección + subasta Vickrey | `[VERIFICADO]` |
| **Apps** | 汽车之家 · **汽车报价** (`athmapp.com/apps/price`) · 二手车之家 (`com.autohome.usedcar`) · 天天拍车 (`com.ttpai`) | `[VERIFICADO app stores]` |
| **SaaS OEM** | **车智云** (`bigdata.autohome.com.cn`) — dashboard de big data estratégico | `[VERIFICADO]` |
| **SaaS dealer** | **销售宝 / 智慧网销 / 智慧集客 / 智慧数联 / 智慧试驾** — consola de marketing/CRM | `[VERIFICADO]` |
| **Suite AI** | AI营销大脑 / AI获客先锋 / AI线索大师 / AI销冠神器 / AI查车专家 (+ DeepSeek智能体, AI数字人) | `[VERIFICADO]` |
| **Research** | Informe anual **保值率** (ranking) — PDF/artículo + colaboración CADA | `[VERIFICADO]` |
| **Transacción** | **Autohome Mall**, 在线购车, financiación, seguro, 送车上门 | `[VERIFICADO]` |
| **API/feed/Excel públicos** | **No anunciados** para consumo externo; la entrega B2B es **SaaS/dashboard/servicio gestionado**, no un feed/API de datos documentado para ingesta de terceros | `[NO-VERIF / ausencia]` |

---

## 6. Precio

> Empresa cotizada; **modelo de ingreso conocido, tarifas concretas NO públicas.** Sin autoservicio de precios.

- **Ingresos FY2024: RMB 7.039,6M (US$964,4M)**, en 3 segmentos: `[VERIFICADO releases/20-F]`
  - **Leads Generation Services ≈ RMB 3.100M** (suscripción dealer + leads + **productos de datos**; +0,8% YoY).
  - **Online Marketplace & Others ≈ RMB 2.400M** (transacción/financiación/seguro/usado; +3,2% YoY).
  - **Media Services ≈ RMB 1.500M** (publicidad; **−18,6% YoY** — el segmento que cae).
- **Productos de datos:** **ingreso +80% YoY** (motor de crecimiento declarado). `[VERIFICADO búsqueda]`
- **Consumidor:** catálogo, 口碑, valoración online, 保值率, rankings y estimación TTP = **gratis**.
- **B2B (OEM/dealer):** licencia/suscripción a 车智云, 销售宝 y suite AI — **importes no divulgados.** `[NO-VERIF]`

---

## 7. Placement (patrón web — clave para cardeep)

> DÓNDE coloca CADA dato en su UI. Es el patrón que cardeep puede copiar para ubicar specs + precio + señal de
> mercado + inteligencia. Verificado en vivo salvo lo marcado.

**A. Home del portal = hub de descubrimiento.** Barra de navegación con **选车 (seleccionar) · 排行榜 (rankings) ·
口碑 · 经销商 · 二手车 · 降价 (caídas de precio) · 超级补贴 (subsidios) · 用车**. Lo primero es elegir/comparar; los
rankings de ventas y las caídas de precio funcionan como ganchos de demanda. `[VERIFICADO]`

**B. Ficha de modelo nuevo (车型库) = bloque de precio arriba + tabla de specs por categorías.** Cabecera con
**指导价 / 经销商报价(por ciudad) / 车主价格(real) / 降价**, luego **参数配置** en ~18 categorías plegables
(基本/车身/发动机/电动机/电池/变速箱/底盘/制动/seguridad activa-pasiva/asistencia/exterior/interior/asientos/
multimedia/luces/cristales/clima/智能硬件), + **comparador 车型对比**, galería, VR, vídeo, **口碑** y botón de leads
(询底价/经销商). `[VERIFICADO categorías]`

**C. Página 口碑 = radar de dimensiones.** Puntuación global /5 + desglose por **空间/动力/操控/油耗/舒适性/外观/
内饰/配置/性价比** (radar/barras) con reseñas escritas de propietarios por subítem. → patrón de "valoración
multi-dimensión del producto". `[VERIFICADO]`

**D. Tarjeta de listing de usado (che168) = foto + título(año/modelo/版本) + km/matrícula/ciudad + 3 precios.**
La **valoración** muestra **个人收购价 / 商家收购价 / 商家零售价** + **保值率 %**; badges de certificación
(准新车/官方认证/N项检测) y enlace a **检测报告** y **出险记录**. → equivalente Autohome del "precio de mercado"
del usado, con la matriz de 3 lados. `[VERIFICADO]`

**E. Ranking de 保值率 = tablas segmentadas.** Por carrocería / origen de marca / propulsión / horizonte (1/2/3
años), con **% exacto** por modelo; bloque de research anual. `[VERIFICADO]`

**F. 车智云 (OEM) = dashboard ejecutivo por módulos.** 8 paneles (销量预测 / 竞争格局 / 营销漏斗 / 传播监测 /
线索分析 / 产品规划 / 配置策略 / 产品改款), cada uno con gráficas/series y predicción. Consumo por directivos del
OEM, no UI de consumo. `[VERIFICADO existencia/estructura]`

**G. 销售宝 (dealer) = consola de marketing/CRM.** Módulos 智能展厅 / 智能选线索 / 智能分配 / 邀约提醒 / 跟进推荐;
embebido en el flujo del concesionario. `[VERIFICADO]`

**H. Suite AI = capa transversal.** AI营销大脑 (decisión) sobre el embudo; AI获客/线索/销冠 (captación→conversión→
venta); AI查车专家 (estado del coche). Más **AI数字人 / asistente** en la capa de consumo. `[VERIFICADO]`

> Lectura para cardeep: el patrón es **"portal de tráfico (rankings/descubrimiento) → ficha de entidad por bloques
> (precio multi-fuente + specs categorizadas + reseñas radar) → señal de mercado (ventas, residual, 3-precios de
> usado) → dashboards de inteligencia B2B (predicción/embudo/competencia) → capa AI transversal"**. Autohome
> demuestra cómo un **portal de consumo** se monetiza vendiendo **insights** a la industria: el mismo dato que el
> consumidor ve gratis (precio real, ventas, residual) se reempaqueta como **predicción y embudo** para OEM/dealer.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Mayor activo de tráfico de auto de China** (~77,5M DAU móvil): genera un **lago de datos de comportamiento de
   primera parte** (intención, configuraciones, leads) imposible de replicar por un libro de valoración.
2. **Ecosistema de embudo completo**: contenido/medio → leads → datos → IA → **transacción** (Mall/在线购车) →
   usado (che168) → subasta (TTP), todo bajo una marca. Pocos competidores globales integran las 6 capas.
3. **Catálogo de specs más exhaustivo de China** (4,5M 车型, ~18 categorías de parámetros) + **口碑** masivo
   multi-dimensión — referencia de facto de consumidor.
4. **保值率 como autoridad de mercado** apoyado en **200M+ registros de seguro (Ping An)** + 1M+ transacciones —
   referencia citada por la asociación del sector (CADA).
5. **车智云 = big data estratégico predictivo para OEM** (销量预测/竞争格局/配置策略/产品改款): vende decisión de
   producto y marketing, no solo precio.
6. **Suite AI propia con LLM 仓颉 + agente DeepSeek**: 5 líneas data-science sobre el mismo grafo de datos; **+80%
   ingreso de datos** y **~30% mejora de conversión** reportados.
7. **Doble canal de usado**: **B2C (che168)** + **C2B subasta Vickrey (TTP)** — captura transacción real que
   alimenta la valoración.
8. **Inspección + historial integrados** (300+ ítems, 出险 por VIN, mantenimiento) dentro del propio marketplace.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo China.** Cero cobertura internacional/multi-país. ← mayor hueco para cardeep (sirve como **fuente-país
   China** de inteligencia de portal, no como vendor global). `[VERIFICADO]`
2. **No es un "libro de valoración" B2B por VIN**: la valoración de usado es un **tool de consumo** (3 precios +
   residual), **no** una API de matriz precio×condición×año por VIN como Che300/Eurotax; el dictamen "duro" exige
   inspección física. `[VERIFICADO]`
3. **Sin API/feed/Excel públicos documentados** para ingesta máquina-a-máquina; la entrega B2B es **SaaS/dashboard/
   servicio gestionado** → difícil de consumir programáticamente por un tercero. `[NO-VERIF / ausencia]`
4. **Precio B2B opaco** (sin tarifa pública, fricción de ventas) y **dependencia del ciclo publicitario** (Media
   −18,6% YoY). `[VERIFICADO]`
5. **Riesgo de fuente de datos por cambio de control**: los 200M+ registros de seguro venían de **Ping An**; bajo
   **Haier (ago-2025)** la continuidad de esa fuente y la estrategia de datos **no están confirmadas**. `[NO-VERIF]`
6. **Curva de depreciación granular por configuración/condición** descargable: no expuesta como producto público
   (publica % de 保值率 por modelo/segmento, no dataset abierto ni forward-curve por VIN). `[PARCIAL]`
7. **Sin TCO / coste total de propiedad** estructurado ni capa de telemetría/OBD en vivo (km verificado por
   inspección/seguro, no feed en tiempo real). `[PARCIAL]`
8. **Enumeración exhaustiva de cada campo de specs** gated por JS / app; auditable a nivel de categorías, no
   campo-a-campo en una sola request abierta. `[PARCIAL]`
9. **Métricas de velocidad de mercado** estilo days-to-sell / market-days-supply / price-to-market explícito: **no
   expuestas** como producto público (tiene ventas, 保值率 y 3-precios como proxies, pero no un índice de liquidez
   nombrado). `[PARCIAL]`

---

## 10. Fuentes

- Portal: https://www.autohome.com.cn/ · Catálogo/参数: https://car.autohome.com.cn/ ·
  百科/参数详解: https://car.autohome.com.cn/baike/detail_7_0_0.html · https://car.autohome.com.cn/baike/detail_7_19_0.html
- Config (ejemplo): https://www.autohome.com.cn/config/series/8564.html · 口碑: https://k.autohome.com.cn/
- Usado: https://www.che168.com/ · Valoración: https://www.che168.com/price/ · Siniestros VIN: https://www.che168.com/insurance/index.aspx
- Subasta C2B: https://www.ttpai.cn/ · App TTP: https://apps.apple.com/cn/app/id1031138508
- App 汽车报价: https://apps.apple.com/us/app/id415206413 · 报价 (web app): https://www.athmapp.com/apps/price/
- 保值率 (definición/metodología): https://www.autohome.com.cn/news/202108/1194933.html · ranking: https://chejiahao.autohome.com.cn/info/19242433
- 车智云 (big data OEM): https://bigdata.autohome.com.cn/ · detalle 8 productos: https://chejiahao.autohome.com.cn/info/2104911
- Transformación a "compañía de datos" / IA dealer: http://www.caam.org.cn/chn/3/cate_79/con_5213555.html ·
  digitalización del sector: https://www.jiemian.com/article/4495328.html
- Suite AI "五大数科" (AI营销大脑/获客先锋/线索大师/销冠神器/查车专家): https://chejiahao.autohome.com.cn/info/25171629 ·
  AI全域营销 + ~30% conversión: https://tech.cnr.cn/techph/20250410/t20250410_527129330.shtml · https://finance.sina.com.cn/stock/relnews/us/2025-04-11/doc-inesuhfy1692983.shtml
- DeepSeek 智能体 (dealer): https://tech.chinadaily.com.cn/a/202502/19/WS67b5a4caa310510f19ee7e6e.html
- Brand refresh 2026 (仓颉大模型/AI数字人/在线购车/送车上门): https://www.news.cn/tech/20260422/72d3c0b174af46b2a63d0da9d912a45a/c.html
- TTP (inspección/subasta Vickrey): https://cn.chinadaily.com.cn/a/202008/06/WS5f2bd5c9a310a859d09dc750.html
- Identidad/propiedad: https://dcfmodeling.com/blogs/history/athm-history-mission-ownership · https://www.crunchbase.com/organization/autohome
- Cambio de control Haier/CARTECH: https://www.prnewswire.com/news-releases/autohome-inc-announces-change-in-controlling-shareholder-and-management-change-302381330.html ·
  https://www.stocktitan.net/news/ATHM/autohome-inc-announces-completion-of-share-transfer-and-change-of-7flt0343qd8t.html ·
  https://www.cliffordchance.com/news/news/2025/09/clifford-chance-advises-haier-group-on-the-global-antitrust-filings.html · https://law.asia/cartech-autohome-acquisition/
- Segmentos/finanzas FY2024 + métricas: https://www.nasdaq.com/press-release/autohome-inc-announces-unaudited-fourth-quarter-and-full-year-2024-financial-results ·
  https://www.stocktitan.net/news/ATHM/autohome-inc-announces-unaudited-fourth-quarter-and-full-year-2024-ofm5qvih9ixb.html · 20-F FY2024: https://www.sec.gov/Archives/edgar/data/0001527636/000095017025053940/athm-20241231.htm
- "Autohome at a Glance" (IR): https://autohomeinc.gcs-web.com/about-us/

### Notas de verificación
- **Propiedad Haier/CARTECH 43% / Ping An salida (US$1,8B, cierre 27-ago-2025): VERIFICADO** (PR Newswire/IR + StockTitan + Clifford Chance + Law.asia + SEC 6-K).
- **Segmentos FY2024 (3,1B/2,4B/1,5B) y DAU 77,48M: VERIFICADO** (releases trimestrales/anual).
- **保值率 definición + base de datos (4,5M/40M/6M/200M Ping An/1M): VERIFICADO** (autohome/news + ranking).
- **车智云 8 productos: VERIFICADO** (artículo oficial chejiahao); etiquetas 智策/智赢/智造: `[PARCIAL]`.
- **Suite AI 5 líneas + ~30% conversión + 仓颉 + DeepSeek: VERIFICADO** (chejiahao/cnr/sina/chinadaily/news.cn).
- **Valoración che168 (个人收购/商家收购/商家零售 + 保值率): VERIFICADO** (che168/price render).
- **口碑 escala 5 + dimensiones: VERIFICADO** (k.autohome render).
- **Taxonomía de specs (~18 categorías): VERIFICADO a nivel de categoría** (百科 Autohome); **enumeración exacta de
  cada campo: [PARCIAL]** (tabla de config gated por JS; el navegador Playwright compartido entre agentes no permitió render fiable).
- **Fundador Li Xiang / fecha HKEX 2021: [PARCIAL]** (ampliamente reportado, no re-verificado con fuente directa esta sesión).
- **Continuidad de la fuente de datos de seguro Ping An tras control Haier: [NO-VERIF]**.
- **Ausencia de API/feed/Excel públicos: [NO-VERIF/ausencia]** (no anunciados en la web pública revisada).
