# CarNewsChina Data (China EV DataTracker) — Auditoría atómica

> Slug: `carnewschina-data` · Subdominio cardeep: **spec-catalog** · Región: **China (RPC)** · Auditado: 2026-06-30
> Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` = leído en vivo, `[PARCIAL]` = parcial/derivado,
> `[NO-VERIF]` = no confirmado / tras paywall. JAMÁS inventar.
> Naturaleza: **brazo de datos del medio editorial CarNewsChina.com** — un **catálogo de especificaciones de
> EV chinos + inteligencia de ventas/matriculaciones del mercado NEV de China**, vendido como SaaS de
> suscripción bajo la marca **"China EV DataTracker"** (web `data.carnewschina.com`, antes/también
> `db.carnewschina.com`). **NO es un libro de valoración de usado** (KBB/Eurotax): su núcleo es **coche
> NUEVO** — specs, precios de catálogo y datos de venta/registro al por mayor. El único componente residual
> es el **China EVs Depreciation Index (beta)** + **price history**. Construido por una redacción periodística,
> no por una consultora de datos — eso define su alcance y sus huecos.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Marca producto | **China EV DataTracker** (+ "China EV GPT") | data.carnewschina.com/premium |
| Marca matriz / medio | **CarNewsChina.com** ("China Auto News") | carnewschina.com/about |
| Razón social / grupo | **No divulgada como entidad legal formal.** Operado por el equipo editorial de CarNewsChina; el flujo de pago/contacto del DataTracker usa el dominio **`china-crunch.com`** (`hello@china-crunch.com`) → marca hermana **"China-Crunch / China EV Marketplace"** | data.carnewschina.com/privacy-policy; carnewschina.com/about (link "China EV Marketplace") |
| Fundación del medio | **Beijing, abril de 2010** | carnewschina.com/about |
| Lanzamiento del DataTracker | **16 de octubre de 2024** (construido en ~3 meses) | carnewschina.com/2024/10/16/… |
| Propietario / Editor-jefe | **Jiří Opletal** (checo; estudió en Taipei, 10 años entre Shenzhen y Europa; dueño y editor-jefe de CNC) | carnewschina.com/author/jiri-opletal; electrodad.cz (entrevista) |
| Equipo (5 perfiles) | Jiri Opletal (Editor-in-Chief), Dong Yi Chen, Denis Bobylev (Editor), Liu Miao, Adrian Leung | carnewschina.com/about |
| HQ declarado | **Beijing, China** (medio fundado allí); operación de facto repartida China ↔ Europa (Chequia). `china-crunch.com` alojado en **vshosting.cz** (hosting checo) | carnewschina.com/about; cert TLS `chinacrunch.vshosting.cz` |
| Contacto | `datatracker@carnewschina.com` · `hello@china-crunch.com` | privacy-policy; home |
| Copyright | © 2026 CarNewsChina.com | privacy-policy |

**Categorías de producto:** (1) **Catálogo de especificaciones de EV** (núcleo, gratuito), (2) **Comparador de EV**,
(3) **Inteligencia de ventas/matriculaciones** (retail/wholesale/export/insurance/city-level — de pago),
(4) **Datos del mercado de baterías**, (5) **Dashboard macro en tiempo real**, (6) **Depreciation Index + price
history** (beta), (7) **China EV GPT** (asistente IA, Enterprise), (8) **Newsletter + alertas** + **informes de
inteligencia / consultoría**.

**Cliente objetivo (declarado literal):** *"EV enthusiast, investor, journalist, EV consultant or global
automotive manager"* — i.e. **inversores, analistas, periodistas, consultores y managers de OEM/proveedor
globales** que necesitan leer el mercado EV chino. (`/premium`; press release.)

**Posicionamiento:** medio editorial independiente con un **producto de inteligencia de datos adjunto**; "entender
el mercado EV de China antes que los demás". No es proveedor de valoración aseguradora/financiera.

---

## 2. Cobertura

- **Geografía:** **solo China continental (RPC).** Sin multi-país. El valor para cardeep es como **fuente-país
  de China**, no como vendor global. (Toda la web es China-only.) `[VERIFICADO]`
- **Granularidad geográfica:** nacional + **>1.000 ciudades chinas** (ventas/matriculaciones por ciudad). `[VERIFICADO]` (press)
- **Nuevo vs usado:** **NUEVO** (catálogo de specs + precio de catálogo + ventas de fábrica/retail). **No hay
  valoración de usado / trade-in / retail de usado.** Único guiño a residual = **Depreciation Index** + **price
  history** (beta). `[VERIFICADO]`
- **Scope de propulsión:** **centrado en NEV/EV** — filtros de fuel type: **BEV, PHEV, EREV, FCEV** y **"Fake EV
  (HEV)"**. El **ICE** se incluye **solo en la capa de ventas/registro** (para comparar marcas legacy como VW,
  BMW, Mercedes y ciudades), **no** como catálogo de specs profundo. `[VERIFICADO]`
- **Tipos de carrocería (filtro):** SUV, Sedan, MPV, Hatchback, Convertible, Liftback, Supercar, Bus, Pickup
  truck, Coupe, Van, Wagon/Estate, City car, Others. `[VERIFICADO]`
- **Escala del catálogo (cifras divergentes por fuente/fecha/filtro — se reportan todas):**
  - Hero de la home: **"4.000 models & trims · 110 brands"**. `[VERIFICADO]`
  - Press de lanzamiento (oct-2024): **114 brands · 1.142 models · 1.000+ ciudades · 2.000.000+ data points**. `[VERIFICADO]`
  - `/database` renderizado en vivo: **~893 EV models** + "150+ manufacturers" en el filtro de marca. `[VERIFICADO]`
  - Una sola marca (BYD) lista **71 models** → el universo de modelos totales es muy superior; "1.142 models"
    es probablemente el subconjunto EV de oct-2024, hoy crecido. `[PARCIAL]`
- **Profundidad histórica:** **ventas de marca desde 2007**; **mínimo 3 años** de historia para el resto de
  métricas; "2 millones de data points". `[VERIFICADO]` (press + /premium)
- **Frecuencia:** **diaria** (catálogo) + **mensual** (ventas/baterías) + **semanal** (insurance registrations). `[VERIFICADO]`

---

## 3. Productos + campos atómicos

> El esquema de **specs por modelo** está **VERIFICADO en vivo** sobre 2 fichas completas (BYD Dolphin 2025 y
> BYD Han EV 2026); el set de campos es idéntico entre ambas → esquema estable. Las **fichas de detalle son
> GRATIS**; la **capa de ventas/analítica** está tras login (campos confirmados por press + `/premium` +
> búsqueda, valores no extraíbles sin cuenta).

### 3.1 Catálogo de especificaciones (ficha de modelo) — núcleo GRATUITO

URL: `/database/{brand}/{model-slug}` (p. ej. `/database/byd/byd-dolphin`).

**Bloque de identificación / clasificación:**

| Campo | Ejemplo (Dolphin / Han EV) |
|---|---|
| **Model name (EN)** | "BYD Dolphin" / "BYD Han EV" |
| **Chinese name (中文名)** | 海豚 / 汉EV |
| **Brand** | BYD |
| **Body type** | Hatchback / Sedan |
| **Fuel type** | BEV (BEV/PHEV/EREV/FCEV/HEV) |
| **Number of seats** | 5 |
| **Release / launch date** | Jul 2024 / Apr 2026 |
| **Product image / photo** | (a veces "Coming soon") |

**Bloque de precio:**

| Campo | Ejemplo |
|---|---|
| **Price range USD (min–max)** | $13.500 – $17.330 |
| **Price range CNY/yuan (min–max)** | ¥91.800 – ¥117.800 |
| **USD/CNY exchange rate usado** | 1 USD = 6,80 CNY (fechado) |
| **Per-trim price (USD y CNY)** | por variante |

**Bloque dimensiones y peso:**

| Campo | Unidad |
|---|---|
| **Length** | mm (4280) |
| **Width** | mm (1770) |
| **Height** | mm (1570) |
| **Wheelbase** | mm (2700) |
| **Curb weight** | kg (1.600) |

**Bloque powertrain / performance:**

| Campo | Unidad |
|---|---|
| **Total power** | kW (150 / 240) |
| **Total torque** | Nm (310 / 305) |
| **Top speed** | km/h (160 / 210) |
| **0–100 km/h acceleration** | s (— / 6,5) |
| **Drive type** | Front / Rear / AWD |

**Bloque batería y autonomía:**

| Campo | Unidad |
|---|---|
| **Battery capacity** | kWh (60,5 / 69,1) |
| **Battery type / chemistry** | LFP (LFP/NMC…) |
| **Range (CLTC)** | km (520 / 705) |
| **Energy consumption** | kWh/100km (12,9 / 10,8) |
| **DC charging 30→80%** | tiempo (0,4 h / "5 h") |

**Bloque tecnología / ADAS:**

| Campo | Ejemplo |
|---|---|
| **Assisted driving chip** | "NVIDIA DRIVE Orin N" |
| **ADAS system** | "DiPilot" / "DiPilot 100" |
| **Lidar (sí/no)** | filtro booleano de catálogo |

**Bloque trims / variantes (tabla):** nombre de la variante (p. ej. *"Dolphin 2025 Intelligent Drive 520KM
Rider Edition"*) + **precio por trim** + **etiqueta de autonomía por trim** (420KM/410KM/520KM…).

**Conversión de unidades:** toggle global **Metric / Imperial** → todos los campos métricos disponibles en
imperial (`/convert/metric`, `/convert/imperial`). `[VERIFICADO]`

**Datos de venta embebidos en la ficha (públicos parcialmente):** **ventas del último mes (uds)** + **MoM %**
(p. ej. Dolphin: 12.819 uds, MoM −9,8%; Han EV: 3.390 uds, MoM +19,6%). `[VERIFICADO]`

> Nota VAM: la ficha Dolphin marcaba **ausentes** (no renderizados): nº de puertas, llantas/neumáticos,
> suspensión, infoentretenimiento, rating de seguridad, garantía y volumen de maletero. No se confirma que esos
> campos existan en el esquema → **se reportan como GAP de profundidad**, no como campo ofrecido. `[VERIFICADO]`

### 3.2 EV Compare (comparador) — `/compare`

Comparación **lado a lado de 2+ modelos** usando **el mismo set de campos** de la ficha (§3.1) en columnas.
"Compare unlimited EV models" en planes de pago; gratis limitado. (No se pudo renderizar el set completo sin
añadir modelos en sesión → se asume = esquema §3.1.) `[PARCIAL]`

### 3.3 Inteligencia de ventas / matriculaciones — DE PAGO (`/sales`)

Campos/métricas confirmados (valores tras login):

- **Retail sales** (ventas minoristas, passenger vehicles). `[VERIFICADO press/premium]`
- **Wholesale** (ventas mayoristas / a fábrica).
- **Export** (exportación — **por modelo y por marca**).
- **Insurance registrations** (matriculaciones por seguro — **semanal + histórico**; métrica estrella para alertas).
- **Sales by brand** (leaderboard: rank · marca · uds · **market share %** · **MoM %** · **YoY %**). `[VERIFICADO home leaderboard: BYD 164.971 uds, 10,92% share]`
- **Sales by model** (leaderboard model-level).
- **City-level sales/registrations** (>1.000 ciudades; EV-only + **opción de añadir ICE** para comparar).
- **ICE brand sales** (VW, BMW, Mercedes… legacy — para contraste).
- **Dealer inventory / stock cars** (inventario de concesionario / coches en stock). `[VERIFICADO press]`

### 3.4 Datos del mercado de baterías

- **Battery installed volume** (GWh, mensual; p. ej. 71,9 GWh May-2026). `[VERIFICADO home]`
- **Battery maker / brand ranking** (TOP 10 a partir del plan Supporter).
- **Battery brand market share (%)**.

### 3.5 Dashboard macro en tiempo real (home)

KPIs/tiles destacados (May-2026 en vivo): `[VERIFICADO]`

- **China EV sales** (uds/mes) — 1.496.000.
- **China EV export** (uds/mes) — 446.000.
- **Battery installed** (GWh) — 71,9.
- **EV penetration (%)** — 63%.
- **Best-selling brand** (callout) — BYD.
- **Best-selling model** (callout).
- **Macro trends / series temporales** (desde 2007).

### 3.6 Beta / exclusivos (clave para cardeep)

- **China EVs Depreciation Index** ("exclusive", beta) — índice de depreciación de EVs chinos. `[VERIFICADO premium/press]`
- **Price history** (histórico de precio por cada EV — time series del precio de catálogo). `[VERIFICADO]`
- **EV's Plant Location** (ubicación de planta/fábrica del modelo). `[VERIFICADO premium]`
- **Export functionality** (función de exportar datos — listada como beta; **no es una API documentada**). `[PARCIAL]`

### 3.7 China EV GPT (asistente IA) + Newsletter

- **China EV GPT** — asistente IA conversacional sobre el dataset (Enterprise, "Beta, limited users"). `[VERIFICADO]`
- **Newsletter mensual "State of China EV Market"** (exclusivo de pago). `[VERIFICADO]`
- **Email notifications** al publicarse datos críticos (insurance registrations, etc.) — "ahead of others". `[VERIFICADO]`
- **Intelligence reports** + **2 h de consultoría/año** (Enterprise). `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Origen:** producto construido **in-house por la redacción de CarNewsChina** (Jiří Opletal), no por una
  consultora de datos; ~3 meses de desarrollo hasta el lanzamiento (oct-2024). `[VERIFICADO press]`
- **Fuentes de datos concretas: NO divulgadas.** La privacy policy detalla recogida de datos *del usuario*
  (registro/newsletter) pero **no** cómo se obtienen las ventas/specs. Por el dominio editorial chino, las
  series de ventas/matriculaciones se nutren típicamente de **CPCA/CAAM-style wholesale+retail**, **insurance
  registration data** (la fuente que ellos citan explícitamente para alertas) y **battery alliance (CABIA-style)**
  para GWh — **[NO-VERIF]** en cuanto a proveedor nombrado; ellos no lo declaran. `[NO-VERIF fuente nombrada]`
- **Specs/precios:** del **catálogo oficial de fabricante / precios de lanzamiento chinos** (precio en CNY
  convertido a USD con tipo de cambio fechado). `[VERIFICADO: la ficha muestra CNY→USD con fecha de FX]`
- **Profundidad temporal:** ventas de marca **desde 2007**; resto **≥3 años**. `[VERIFICADO]`
- **Actualización:** **diaria** (catálogo "daily updated") + cadencia mensual/semanal según métrica. `[VERIFICADO]`
- **No publican** metodología del **Depreciation Index** (cómo se computa el índice). `[NO-VERIF]`

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web / dashboard** | `data.carnewschina.com` (antes/redirige `db.carnewschina.com`); dashboard macro en vivo + tablas + gráficas. | `[VERIFICADO]` |
| **EV Database** | Catálogo navegable de fichas (gratis, sin login). | `[VERIFICADO]` |
| **EV Compare** | Comparador interactivo lado a lado. | `[VERIFICADO]` |
| **Email alerts** | Notificación al publicarse datos críticos (insurance reg, etc.). | `[VERIFICADO]` |
| **Newsletter** | "State of China EV Market" mensual (email). | `[VERIFICADO]` |
| **China EV GPT** | Chat IA sobre el dataset (Enterprise). | `[VERIFICADO]` |
| **Consultoría** | 2 h/año individuales (Enterprise). | `[VERIFICADO]` |
| **"Export functionality"** | Listada como **beta**; alcance/formatos no documentados. | `[PARCIAL]` |
| **API REST** | **NO ofrecida / no anunciada.** Ningún endpoint, doc de API ni feed en toda la web. | `[VERIFICADO ausencia]` |
| **Excel/CSV/feed/integración DMS** | **No anunciados.** | `[VERIFICADO ausencia]` |

> Conclusión de entrega: es un **SaaS de consumo humano (dashboard + email + GPT)**, **no** una capa de
> integración máquina-a-máquina. Sin API/feed documentado → **gran hueco** frente a vendors B2B y frente a lo
> que cardeep necesitaría para ingesta automatizada.

---

## 6. Precio

> Tarifa **pública y autoservicio** (raro y valioso para benchmarking). 3 planes; precios en **USD**.
> Capturas en 2 páginas (`/premium` y `/get-full-access`) → conciliadas. El "anual" = **tarifa mensual
> efectiva con facturación anual** (más barata); el total anual exacto facturado queda `[PARCIAL]`.

| Plan | Mensual | Anual (efectivo/mes) | Incluye (verbatim, resumido) |
|---|---|---|---|
| **Supporter** | **$19/mo** | **~$15/mo** | No Ads · Compare unlimited EV models · historia limitada a **12 meses** · solo **TOP 20** brands/models/cities por tabla · solo **TOP 10** battery makers |
| **CarNewsChina Member** | **$59/mo** | **~$49/mo** | Todo lo anterior + **unlimited sales history (since 2007)** · **2 million data points** · **real-time email notifications** al publicarse datos críticos · **newsletter mensual exclusivo** |
| **Enterprise** | **$229/mo** | **~$199/mo** | Todo lo anterior + cuentas para **2 colegas** · **2 h de consultoría/año** · **China EV GPT (Beta)** · prioridad en nuevas features · "collectible EV model" (plan anual) |

- **Capa gratuita:** **EV Database (specs/precios/imágenes) + Compare básico + dashboard macro** son **gratis sin
  login**; el paywall cubre **profundidad de ventas/histórico/alertas/GPT**. `[VERIFICADO]`
- **Sin tier de API / licencia de datos / enterprise data feed** con precio. `[VERIFICADO ausencia]`

---

## 7. Placement (patrón web — clave para cardeep)

> DÓNDE coloca CADA dato en su UI. Verificado en vivo salvo lo marcado. Es el patrón que cardeep puede copiar
> para ubicar specs + señal de mercado de coche **nuevo** chino.

**A. Home = dashboard macro (landing).** Fila de **4 KPI tiles** grandes arriba (China EV sales · Export · Battery
installed GWh · EV penetration %), con **callouts de best-seller** (marca y modelo) y un **leaderboard de ventas
por marca** (rank · uds · market share %). Patrón: el macro del mercado es lo primero que ve el usuario, antes
que cualquier coche concreto. `[VERIFICADO]`

**B. EV Database (`/database`) = grid de tarjetas + sidebar de filtros.** Filtros (facetas): **Brand · Price (USD,
slider) · Body Type · Fuel Type · Lidar (toggle) · Battery Capacity (slider) · Motor Power (slider)**. Cada
**tarjeta de modelo** = imagen + nombre + marca + precio + specs clave + botón "Add to Compare". `[VERIFICADO]`

**C. Página de marca (`/database/{brand}`) = lista de modelos** de esa marca (BYD: 71) con "Load More". Cada fila
enlaza a la ficha. `[VERIFICADO]`

**D. Ficha de modelo (`/database/{brand}/{model}`) = hoja de specs por bloques** (ver §3.1), en este orden de
arriba a abajo: **cabecera (nombre EN + 中文名 + body/fuel/seats + release date) → rango de precio (USD/CNY + FX) →
powertrain/performance → batería/autonomía → dimensiones/peso → ADAS/chip → tabla de trims (nombre + precio +
autonomía) → línea de ventas (uds último mes + MoM%)**. En planes de pago, sobre esta ficha se montan **price
history** y **depreciation index** (chart). Es el equivalente más directo a la "ficha de coche" de cardeep —
pero de **coche nuevo**. `[VERIFICADO esquema; price-history/deprec = premium]`

**E. EV Compare (`/compare`) = columnas lado a lado** del mismo set de specs para 2+ modelos. `[VERIFICADO existencia]`

**F. EV Sales (`/sales`) = tablas-leaderboard + gráficas de serie temporal.** Subvistas: **by brand · by model ·
by city · battery-brands**, con selector de **periodo (mes, p. ej. 2026-05)** y métricas rank/uds/share/MoM/YoY;
**city-level** con desglose por >1.000 ciudades y toggle para añadir ICE. (Tras login.) `[VERIFICADO estructura/URLs; valores gated]`

**G. Alertas + Newsletter (no-UI).** Email al publicarse cada dataset (insurance registrations semanales) +
boletín mensual "State of China EV Market". `[VERIFICADO]`

**H. China EV GPT.** Interfaz de chat que responde sobre el dataset (Enterprise). `[VERIFICADO existencia]`

> Lectura para cardeep: el patrón es **"macro-dashboard primero → catálogo filtrable → ficha-spec por bloques →
> comparador → leaderboards de venta/ciudad"**. La señal de mercado (ventas, share, MoM/YoY, insurance reg,
> inventario) vive en **leaderboards y series**, no en la ficha; la ficha solo lleva specs+precio+1 línea de
> ventas. cardeep, al ser de **huella digital de PUNTOS DE VENTA**, no de coche-modelo, copiaría el patrón de
> **dashboard macro + entidad-ficha por bloques + leaderboards/ranking + alertas por publicación de dato**.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Foco monopaís profundo en China NEV con voz editorial**: une **specs + ventas + matriculaciones + baterías +
   ciudad** del mercado EV chino bajo un medio con autoridad periodística (CarNewsChina, desde 2010).
2. **Insurance registrations semanales con alerta "ahead of others"**: dato de matriculación real, semanal,
   notificado por email al publicarse — señal temprana difícil de obtener fuera de China.
3. **City-level a >1.000 ciudades** con toggle EV vs ICE — granularidad geográfica intra-China poco común en
   vendors occidentales.
4. **Catálogo de specs EV GRATIS** (specs/precio/imagen sin login) — estrategia freemium editorial; el paywall es
   solo profundidad analítica.
5. **China EVs Depreciation Index + price history (beta)** — único toque de valor residual, exclusivo.
6. **China EV GPT** — capa IA conversacional sobre el dataset (pocos peers la tienen).
7. **Precio público y barato** ($19–$229/mo) y autoservicio — accesible vs los contratos enterprise opacos de
   S&P/GlobalData/Eurotax.
8. **Historia de ventas de marca desde 2007** + cobertura ICE legacy para contraste.
9. **EV Plant Location** (mapeo planta↔modelo) — dato industrial poco frecuente en catálogos de spec.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo China.** Cero multi-país. Para cardeep solo sirve como **fuente-país China**, no como vendor global. ← hueco mayor.
2. **No es valoración de usado.** Sin trade/retail/private de usado, sin days-to-sell, sin market-days-supply,
   sin price-to-market, sin ajuste por km, sin curva de depreciación granular por VIN. El "Depreciation Index"
   es un índice agregado beta, no una matriz de valor por configuración/condición/año (compárese con Che300 §3.1).
3. **Sin API / feed / CSV / integración DMS documentados.** Entrega = dashboard + email + GPT (consumo humano).
   "Export functionality" es beta sin especificar. → impide ingesta máquina-a-máquina. `[VERIFICADO ausencia]`
4. **Sin VIN.** No hay decodificación VIN ni atributos por VIN ni build-data. Trabaja a nivel **modelo/trim**, no unidad.
5. **Profundidad de specs limitada / desigual:** faltan (no renderizados) puertas, llantas/neumáticos, suspensión,
   infoentretenimiento, rating de seguridad, garantía, volumen de maletero, nº de motores, WLTP/NEDC (solo CLTC),
   potencia de carga en kW (solo tiempo 30–80%). `[VERIFICADO en ficha Dolphin]`
6. **Sin historial de siniestros/km/condición** (no es un car-history provider).
7. **Metodología y fuentes no publicadas** (ni de ventas ni del Depreciation Index) → caja negra para auditoría. `[NO-VERIF]`
8. **Equipo pequeño (5 personas) y origen editorial** → riesgo de cobertura/continuidad vs proveedores de datos
   industriales; "construido en 3 meses" sugiere producto joven (lanzado oct-2024).
9. **Catálogo EV-céntrico:** el ICE solo aparece en la capa de ventas para comparar, no como catálogo de specs.
10. **Datos crudos no descargables** en abierto; el valor analítico profundo está tras paywall y sin export estructurado.

---

## 10. Fuentes

- Home / dashboard: https://data.carnewschina.com/
- EV Database (catálogo): https://data.carnewschina.com/database
- Ficha modelo (esquema specs, verificada): https://data.carnewschina.com/database/byd/byd-dolphin · https://data.carnewschina.com/database/byd/byd-han-ev
- Página de marca (modelos BYD): https://data.carnewschina.com/database/byd
- Comparador: https://data.carnewschina.com/compare
- Ventas: https://data.carnewschina.com/sales · https://data.carnewschina.com/sales/brands/2026-05
- Pricing / features: https://data.carnewschina.com/premium · https://data.carnewschina.com/get-full-access
- Privacy policy (entidad/contacto/GPT): https://data.carnewschina.com/privacy-policy
- Press de lanzamiento (cobertura/metodología/target): https://carnewschina.com/2024/10/16/carnewschina-introduces-ev-datatracker-a-tool-to-understand-the-china-ev-market-with-2-million-sales-datapoints/
- About del medio (fundación Beijing 2010, equipo): https://carnewschina.com/about
- Autor/owner Jiří Opletal: https://carnewschina.com/author/jiri-opletal/ · entrevista: https://www.electrodad.cz/cina-expanduje-v-automobilovem-svete-jiri-opletal-carnewschina-com
- Marca hermana / pago: dominio `china-crunch.com` (`hello@china-crunch.com`); host TLS `chinacrunch.vshosting.cz`
- Dominio alterno del producto: `db.carnewschina.com` → 301 → `data.carnewschina.com`

### Notas de verificación
- **Esquema de specs por modelo (§3.1): VERIFICADO en vivo** sobre 2 fichas completas (Dolphin + Han EV), set idéntico.
- **Pricing (§6): VERIFICADO** en 2 páginas (`/premium` + `/get-full-access`); total anual exacto facturado `[PARCIAL]` (las capturas difieren en si el anual es "$/año" o "$/mes efectivo").
- **Capa de ventas/analítica (§3.3): campos VERIFICADOS** por press + `/premium` + búsqueda; **valores tras login**, no extraídos.
- **Beta (Depreciation Index, price history, plant location): VERIFICADO** por `/get-full-access` + press + búsqueda; **metodología NO publicada**.
- **`spec-catalog.carnewschina.com` NO existe** (DNS ENOTFOUND, verificado) → "spec-catalog" es el **subdominio de taxonomía de cardeep**, no un host real.
- **Cifras de cobertura divergentes** (4.000 trims/110 brands vs 1.142 models/114 brands vs 893 EV models en vivo): reportadas todas; reconciliación exacta `[PARCIAL]`.
- **Fuentes de datos nombradas (CPCA/CAAM/insurance/CABIA): [NO-VERIF]** — la empresa no las declara; no se afirma como hecho.
- **Ausencia de API/CSV/DMS: VERIFICADO** por barrido de toda la web pública (ningún rastro de endpoint/doc/feed).
- **Entidad legal formal: NO divulgada**; vínculo china-crunch inferido del email de contacto/link "China EV Marketplace" `[PARCIAL]`.
