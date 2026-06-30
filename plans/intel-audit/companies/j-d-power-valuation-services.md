# J.D. Power Valuation Services — Auditoría atómica

> Slug: `j-d-power-valuation-services` · Subdominio cardeep: **valuation** · Región: **Norteamérica** (EE. UU. núcleo; Canadá vía ALG)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó.
> Naturaleza: empresa de **valoración de vehículos** heredera del legendario **NADA Used Car Guide** (1933).
> Es el estándar de "libro" de valores para el sector **financiero** (bancos, credit unions, lenders) y de
> seguros en EE. UU., hoy bajo el paraguas de la marca de investigación J.D. Power (Thoma Bravo).
> Marca pública: `J.D. Power Valuation Services` · sitio B2B: `jdpowervalues.com` · consumo: `jdpower.com/cars`.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre actual | **J.D. Power Valuation Services** (antes **NADA Used Car Guide** / **NADAguides**) | jdpowervalues.com; prnewswire 2015 |
| Origen del dato | **NADA Used Car Guide**, establecido por la **National Automobile Dealers Association en 1933** | prnewswire (cierre adquisición 2015) |
| Adquisición | J.D. Power **acuerda comprar** NADA UCG a la NADA (jul-2015) y **completa** la compra en el **3.er trimestre 2015** | prnewswire ×2 |
| Owner / grupo | **J.D. Power**, propiedad de **Thoma Bravo** (PE de Chicago) desde **2019**; fusionada con **Autodata Solutions** | thomabravo.com; Wikipedia; Crain's |
| Parent en 2015 | En el momento de comprar NADA UCG, J.D. Power era división de **McGraw Hill Financial (NYSE: MHFI)** | prnewswire 2015 |
| Adquisición ALG | **ALG** (autoridad de valores residuales) adquirida y **completada 30-nov-2020** | jdpowervalues.com (artículo ALG) |
| J.D. Power fundada | **1968** por James David Power III (investigación de satisfacción del cliente) | conocimiento general / Wikipedia `[VERIFICADO vía Wikipedia]` |
| HQ J.D. Power | **Troy, Michigan** (oficina única declarada); legacy 2015 en Westlake Village, CA | thomabravo/Wikipedia; prnewswire 2015 |
| HQ heredado NADA UCG | Operaciones históricas en **McLean, VA** / **Costa Mesa, CA** `[PARCIAL-VERIFICADO]` | prnewswire (contacto), inferido |
| CEO | **Joshua Peirez** (nombrado mayo-2025) | WebSearch (Thoma Bravo / prensa) |
| Sitios | `jdpower.com/cars` (consumo), **`jdpowervalues.com`** (B2B valoración), `jdpowervaluesonline.com`, `extapps.jdpowervalues.com/ValuesOnline/`, `ndg.jdpower.com`, `nadaguides.com` (legacy) | verificado navegando |
| Teléfonos de venta | **800-544-6232** (autos) · **800-966-6232** (specialty) | jdpowervalues.com |

**Categorías de producto:** (1) **Valoración de vehículos** (núcleo: retail/loan/trade-in/auction/residual),
(2) **Datos/API de valores B2B** (REST, web services, batch), (3) **Valores residuales ALG** (leasing/forecast),
(4) **Índices de mercado mayorista** (Used Vehicle Price Index / AuctionNet), (5) **Descripciones de vehículo /
VIN decode** (ChromeData/Autodata: specs, build data, imágenes, vídeos), (6) **Incentivos/rebates** (ChromeData
Lender Desk), (7) **Contenido de consumo** (portal jdpower.com: Consumer Verified Ratings, cars-for-sale).

**Cliente objetivo (declarado):** **Dealers** · **Banks, Credit Unions and Lenders** · **Insurance Companies** ·
**OEMs and Captive Finance** · **Rental Fleet Companies** · **Investment Community** · **Government Agencies** ·
**auctions** · **fleet/lease administrators**. (Fuente: jdpower.com/jd-power-pricing-and-values; jdpowervalues.com.)
**~500.000 suscriptores** declarados. El sesgo histórico es **financiero/lending** (el "valor de libro" para préstamos).

---

## 2. Cobertura

- **Geografía núcleo:** **Estados Unidos.** La FAQ oficial es taxativa: *"All valuations apply to vehicles
  manufactured for sale in the United States only."* La red de transacciones PIN cubre **"more than 16,000
  dealerships across North America"** pero los **valores de guía aplican a vehículos US-spec**. (Fuente:
  jdpowervalues.com/frequently-asked-questions; jdpower.com/trade-in-value.)
- **Canadá:** cubierto **vía ALG** (residuales) — existen los **Canada ALG Residual Value Awards** ("the Canadian
  automotive leasing industry's standard"). El dato residual ALG es **US + Canadá**. (Fuente: jdpower.com /
  canada.jdpower.com press releases ALG.)
- **Europa / global:** **SIN cobertura de valoración.** J.D. Power hace estudios de investigación globales, pero
  **Valuation Services es norteamericano**. ← gran hueco para cardeep. `[VERIFICADO por ausencia + FAQ US-only]`
- **Nuevo y usado:** ambos. New Vehicle Values (semanal) + universo usado completo (mensual). MSRP/typically-equipped.
- **Tipos de vehículo / activo (amplitud excepcional):**
  - **Passenger cars + light-duty trucks** (núcleo; guía impresa cubre MY **2018-2025**, 7 años).
  - **Commercial trucks** (web service + monthly guidelines con índice mayorista).
  - **Motorcycles, ATV, snowmobiles, personal watercraft (PWC)** → **Powersports Connect**.
  - **RVs / recreation vehicles** → **RV Connect**.
  - **Boats / marine + PWC** → **Marine Connect**. (≠ KBB, que NO valora barcos.)
  - **Manufactured homes** (usados y nuevos) → **MH Connect** (depreciated replacement cost en dólares retail).
  - **Classic cars** (vía Web Service - Specialty Data).
  - **Farm & outdoor power equipment** (mencionado en data-software-technology). `[PARCIAL-VERIFICADO]`
  (Fuentes: jdpowervalues.com/get-values/* ; api-and-web-services-solutions; values-online.)

---

## 3. Productos + campos atómicos

### 3.1 Tipos de VALOR (la materia prima) — definiciones oficiales

Fuente primaria: `jdpowervalues.com/get-values/values-online`, `/frequently-asked-questions`,
`jdpower.com/jd-power-pricing-and-values`, y la guía impresa.

| Valor | Definición atómica | Actualización |
|---|---|---|
| **New Vehicle Value** (Low / Average / High) | Valor de coche nuevo en tres niveles. | **Semanal** |
| **Auction Value** (Low / Average / High) | Precio esperado en subasta mayorista, tres niveles. | **Semanal** |
| **Trade-In Value** (**Rough / Average / Clean**) | Precio típico del vehículo al entregarlo a un dealer, por condición. | **Mensual** |
| **Clean Loan Value** | "the potential amount of credit that may be obtained on a vehicle" (referencia de préstamo). | **Mensual** |
| **Clean Retail Value** | "the typical selling price for a vehicle", con opción CPO. | **Mensual** |
| **DMA Retail Value** | Retail **hiperlocal** ajustado por **zip → DMA** (Designated Market Area), exclusivo de VIN Decode; sobre **~70% de las transacciones**. | derivado PIN |
| **Certified Pre-Owned (CPO) Value** | "the typical premium added to the retail value when a given vehicle is initially sold by a franchised dealer under a manufacturer's certification program". | **Mensual** |
| **Residual Value (ALG)** | Valor mayorista proyectado a fecha futura (típicamente fin de leasing); % del MSRP retenido. | guía ALG |
| **Short-Term Forecast Value** | % de ajuste de valor a futuro: **1-36 meses** (Values Online / MarketValues / API) y **3-60 meses** (forecast ALG en FAQ). Para depreciación/pricing/lending. | continuo |
| **Wholesale value / guideline** | Guía mayorista (commercial trucks, manufactured homes). | mensual |
| **Typically-equipped MSRP** / **Original MSRP** | MSRP de referencia para comparación y depreciación. | — |

> **Variación de horizonte de forecast documentada:** los productos (Values Online, MarketValues, REST API) exponen
> una **curva de 1-36 meses**; la FAQ describe el forecast subyacente de **ALG como 3-60 meses**; una fuente de API
> citó **3-36**. Se reporta el rango tal cual aparece por producto. `[VERIFICADO con discrepancia de fuente]`

**Estructura de presentación de cada valor (clave placement):**
*"Loan, Retail, Trade-In and Auction numbers are shown with **base values and adjustments for mileage and options**."*
→ patrón **Base + Mileage Adj + Options/Content Adj = Adjusted Value**. (Fuente: WebSearch sobre Values Online / hoja domino FCU.)

### 3.2 Condición (modificador transversal) — definiciones VERBATIM

Tres tiers (la guía y FAQ los citan literalmente; **no** hay tier "Excellent"/"Poor" como KBB — son tres):

| Tier | Definición oficial (resumida verbatim) |
|---|---|
| **Clean** | "No mechanical defects and passes all necessary inspections with ease; paint, body and wheels may have minor surface scratching with a high gloss finish; interior reflects minimal soiling and wear, all equipment in complete working order; clean title history; needs minimal reconditioning." |
| **Average** | "Mechanically sound but may require some repairs/servicing to pass inspections; paint/body/wheel surfaces have moderate imperfections; interior reflects some soiling and wear relative to age, equipment operable or minimal effort; clean title history; needs a fair degree of reconditioning." |
| **Rough** | "Significant mechanical defects requiring repairs to restore reasonable running condition; considerable cosmetic damage (dull/faded/oxidized paint, dents, frame damage, rust, previous repairs); interior above-average wear, inoperable equipment, damaged/missing trim; **may have a 'branded' title**." |

(Fuente: WebSearch verbatim de Values Online / jdpowervalues FAQ; carbuyerusa; sefinancial.)
**Trade-In** se publica en los tres tiers; **Loan** y **Retail** se publican como **Clean**.

### 3.3 VIN Precision+ / As-Built (la capa de precisión — diferencial fuerte)

| Capacidad | Detalle atómico | Fuente |
|---|---|---|
| **VIN decode** | Decodificación con **95% de precisión de trim**; usa el **VIN completo de 17 caracteres** (vs 11 básicos) para packaging/contenido/features. | values-online; prnewswire VIN Values |
| **VIN Precision+** | Combina valores JD Power + **ChromeData "as-built data"**; decodifica por **datos reales de fábrica del OEM** donde existen, o por **algoritmo de configuración** propio. Devuelve **"exact vehicle specifications"**. | features-enhance-our-products |
| **As-Built Valuation Service** | Devuelve **retail y wholesale para cualquier VIN**, con **valoración línea a línea de todas las opciones y add/deducts**, o un **único valor calculado** por vehículo. | WebSearch (As-Built) |
| **Content Adjustment** | Ajuste de valor por **opciones de fábrica conocidas** ("as-built"), en vez de valoración "typically equipped". | features page |
| **VIN Values** (jun-2019) | Extrae **trim, options y purchase history** del VIN de 17 dígitos para personalizar cada valoración. | prnewswire VIN Values |
| **Impacto financiero declarado** | Cartera de **500.000** vehículos: decode estándar = $10,3 B; VIN Precision+ revela **1,8% de diferencia = $180 M**. Cartera de **100.000**: decode estándar tiene **6-13%** de error de margen = **$25-35 M** de ajuste. | WebSearch; prnewswire |

### 3.4 ALG — valores residuales (producto de forecast de leasing)

- **Qué es:** *"the industry authority on automotive residual value projections in both the United States and Canada"*.
  **50+ años** de experiencia. **Adquirida 30-nov-2020.**
- **Residual value (def.):** *"the projected wholesale value of a vehicle at a future date, typically the end of a lease"*;
  driver clave del coste de leasing; refleja calidad/diseño/deseabilidad de marca a largo plazo.
- **Cobertura de uso:** informa **~40% de los lanzamientos de vehículo nuevo en Norteamérica** y **casi todas las
  transacciones de leasing del mercado US**. ~**1/3 de los coches nuevos se alquilan (lease)**, típicamente a **3 años**;
  el valor de las carteras de leasing vivas se estima en **$500 mil millones**.
- **Variables del forecast (atómico):** **mileage; condition; features & pricing; vehicle execution; used supply;
  market strategy; seasonality; macroeconomic factors** + "macro, industry, and market factors → benchmark depreciation forecasts".
- **ALG Residual Value Awards:** **US** = proyección a **3 años** (mayor % del MSRP retenido por segmento); **Canadá** =
  **4 años** (mass market) y **3 años** (premium).
- **Suite ALG:** "interactive software tools, custom reports, consulting and beyond" + **ALG Automotive Insights & Outlook**.

(Fuentes: jdpowervalues.com/alg-automotive-insights-outlook; /article ALG acquisition; press releases ALG US/Canada.)

### 3.5 Used Vehicle Price Index Service + AuctionNet (índice mayorista)

| Campo | Detalle atómico | Fuente |
|---|---|---|
| **Qué mide** | Movimiento **actual y futuro estimado de precios mayoristas** de usado, a nivel **industria** y **segmento**. | prnewswire (2017); used-vehicle-price-index |
| **Fuente de dato** | **AuctionNet®** = **>80% de las transacciones de subasta del país** (Manheim, ADESA, ServNet, ABC + casas independientes clave). | prnewswire; jdpowervalues |
| **Horizonte forecast** | Año en curso **+ 2 años hacia adelante**. | ambos |
| **Nivel 1 (industria)** | Histórico **desde 1995**, modelos de hasta **8 años**; **gratis** con suscripción Nivel 1. | prnewswire |
| **Nivel 2 (segmento)** | **14+ segmentos** de vehículo con forecast (suscripción de pago). | prnewswire |
| **Metodología** | **Pool fijo de vehículos** (elimina sesgo de edad/mix), filtra ventas no representativas, **ajusta km al típico por edad**, pondera vehículo→segmento→industria, aplica **depreciación estadística + ajustes estacionales**. | prnewswire |
| **Entrega** | **Reporte mensual** descargable en **Excel o CSV**; aviso por email. | jdpowervalues |
| **Commercial truck** | Guidelines mensuales con datos mayoristas + indexación de precio. | jdpowervalues |
| **Lanzamiento** | **14-ago-2017**. | prnewswire |

### 3.6 Descripciones de vehículo / ChromeData (Autodata) — capa de specs

| Producto | Qué entrega | Fuente |
|---|---|---|
| **ChromeData VIN Descriptions** | VIN decoding líder, **options/packages**, **validación de OEM build data**, con **AI/ML + catálogo de vehículo**; API devuelve el contenido del VIN. Estándar de industria para **descripciones consistentes cross-manufacturer**. | jdpower chromedata-vin-descriptions; prnewswire IAA |
| **Vehicle Descriptions** | "most detailed and comprehensive new vehicle, VIN, and historical data" + biblioteca de **imágenes y vídeos** de modelo. | jdpower-pricing-and-values |
| **ChromeData Lender Desk** | API multi-nivel: **OEM rates, rebates, incentives** + lenders independientes para advertising/retailing. | WebSearch (ChromeData) |
| **Incentives service** | Ofertas de incentivo **sourced del fabricante** y **mapeadas a zip/región**. | jdpower-pricing-and-values |
| **Media library** | Imágenes, vídeos y reviews integrados con el dato del vehículo. | WebSearch |

### 3.7 Contenido de consumo (portal jdpower.com/cars)

- **Consumer Verified Vehicle Ratings:** ratings/reviews/awards derivados de **encuestas a propietarios verificados**;
  atributos: **quality & reliability**, **driving experience**, **dealership sales experience**, **service experience**.
  Resumido por modelo → **car rankings por tipo de vehículo**. (Fuente: jdpower-pricing-and-values.)
- **Cars for Sale:** listings de inventario con **descripciones a nivel VIN** + **manufacturer-sourced build data**,
  integrados con **cientos de feeds de inventario de dealer**.
- **Compare (side-by-side, hasta 3):** **pricing, MPG, specs, pictures, safety features, warranty coverages**.
- **Vehicle history:** **NO propio** → vía **AutoCheck** (Experian) y partner **BeenVerified** (afiliado). Incluye
  millaje reportado, robos, salvage, accidentes, recalls, nº de dueños, CPO.

---

## 4. Metodología / fuentes de datos

- **Núcleo retail — PIN (Power Information Network®):** **datos de transacción 100% retail puros**, basados en
  **>294 millones de ventas** de vehículo nuevo y usado (histórico); **>16.000 dealerships** en Norteamérica;
  **>12 millones de transacciones retail/año**; procesado **diariamente / en tiempo real**.
  **Cada reporte genera >250 métricas únicas** para valorar un vehículo (make, model, trim, mileage, condition).
- **Diferencial metodológico explícito:** *"KBB and Black Book derive their trade-in values by **extrapolating from
  prices paid at wholesale auctions**. In contrast, JD Power produces ... values based on **more than 12 million
  retail vehicle transactions annually**."* → **JD Power = transacción retail real; KBB/Black Book = extrapolación de subasta.**
- **Mayorista — AuctionNet®:** **>80%** de las subastas del país (Manheim, ADESA, ServNet, ABC + independientes).
- **Build data — ChromeData / OEM:** datos de fábrica del OEM (alianzas, p.ej. **Ford** 2022) + algoritmo de configuración.
- **Residuales — ALG:** modelos de forecast con macro/industria/mercado (50+ años).
- **Legado:** **"90-year legacy"**; **>20 millones de transacciones/año analizadas**.
- **Frecuencia:** **New + Auction = semanal**; **Trade-In + Loan + Retail = mensual**; índice UVPI = mensual.
- **Ajustes:** **mileage** (al km típico por edad) y **options/accessory** (Content Adjustment); **DMA/zip** sobre ~70% de transacciones; **Early Release Values** para modelos sin historial usado.

(Fuentes: jdpower.com/trade-in-value; jdpower-pricing-and-values; jdpowervalues.com; prnewswire UVPI 2017.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web consumo** | `jdpower.com/cars` — values, trade-in, ratings, cars-for-sale, VIN lookup, compare, incentives, rankings. Pestañas **Autos / Motorcycles / Boats / RVs**. |
| **Web / desktop B2B** | **Values Online** (`extapps.jdpowervalues.com/ValuesOnline/`): lookups por crédito, inventory valuation, custom reporting, trends. |
| **App móvil** | **MarketValues App** (iOS/Android): VIN **scan**, DMA retail, forecast curve, VIN Precision+ specs; sincroniza con Values Online. App separada para **commercial trucks**. |
| **API REST / Web Service** | **REST API** con valores en tiempo real, **VIN Precision+**, DMA retail por zip, forecasts ALG; **Web Service Used Car/Light-Duty/Commercial Trucks** y **Web Service - Specialty Industry Data**. (SOAP/REST: REST confirmado; **SOAP no verificado**.) |
| **As-Built Valuation Service** | Servicio para **cualquier VIN** → retail+wholesale con add/deducts línea a línea (lenders, total-loss, fleet). |
| **Batch / archivo** | **Used Vehicle Price Index** en **Excel/CSV** mensual; valoración de cartera por lotes (lenders). `[PARCIAL: batch VIN para carteras inferido del caso 500k]` |
| **Guía impresa** | **Official Used Car Guide**: **pocket-sized**, **mensual**, **7 años** de valores, **10 ediciones regionales**. |
| **Suscripciones "Connect"** | **RV / Marine / Powersports / MH (Used+New) / Title & Registration Connect** (online, anual). |
| **Integración terceros / DMS** | Integraciones con scanners y plataformas: **Laser Appraiser**, **Carbly**, **Odessa** (lenders), **IAA** (subasta, ChromeData), CRMs automotrices. |

---

## 6. Precio (descubierto — inusualmente transparente para el self-service)

| Producto | Precio | Fuente |
|---|---|---|
| **Values Online** | **$945** / 1.000 lookups · **$1.335** con móvil · **+$300** por licencia de usuario adicional | values-online |
| **MarketValues App** | **$1.335/año** o **desde $85/mes** (hasta 1.000 valoraciones/año); apps de especialidad **$325-$392/año** | marketvalues |
| **Official Used Car Guide** (impreso) | **$662/año** (incl. envío estándar); descuento por volumen; **>125 suscripciones = 30% dto.** | official-used-car-guide |
| **RV Connect** | **$504/año** | api-and-web-services-solutions |
| **Marine Connect** | **$504/año** | id. |
| **Powersports Connect** | **$430/año** | id. |
| **Title & Registration Connect** | **$587/año** | id. |
| **MH Connect (Used)** | **$573/año** | id. |
| **MH Connect (New)** | **desde $550** por 10 price reports | id. |
| **Used Vehicle Price Index** | **Nivel 1 (industria) gratis**; **Nivel 2 (segmento) de pago** `[importe NO-VERIFICADO]` | prnewswire |
| **Web Services / REST API / As-Built / Enterprise** | **No público** — "Call 800-544-6232 / 800-966-6232" (licencia/suscripción negociada) `[NO-VERIFICADO importe]` | api-and-web-services-solutions |
| **Portal consumo jdpower.com** | **Gratis** (monetiza con leads, dealer quotes, publicidad, afiliados como BeenVerified) | jdpower.com/cars |

---

## 7. Placement (patrón web — clave para cardeep)

> Lo que cardeep imita para **dónde** colocar cada dato. Derivado de la navegación real al portal de consumo
> (`jdpower.com/cars`, `/trade-in-value`) y de la estructura de **Values Online / MarketValues** B2B.

**A. Entrada de valoración (consumo) — flujo de 4 pasos.** El widget de trade-in usa stepper numerado:
**(1) Car Basics** [Year, Make, Model, **Trim Level**] → **(2) Car Details** [mileage, condition, options] →
**(3) Plan Ahead** → **(4) Trade-In Value** (resultado). Los valores son **"customizable by mileage and options"**.

**B. Entrada de valoración (B2B Values Online / MarketValues).** Inputs: **VIN (con scan)** *o* Year-Make-Model,
**Mileage (obligatorio)**, **Zip (→ asigna DMA)**, **Trim (opcional)**. El VIN dispara **VIN Precision+** (specs de fábrica).

**C. Panel de valores (la "ficha de valoración" B2B).** Muestra **juntos** los tipos de valor y, por cada uno,
la fórmula **Base value → (+/–) Mileage Adjustment → (+/–) Options/Content Adjustment → Adjusted value**:
- **Trade-In** en columnas **Rough / Average / Clean**.
- **Clean Loan Value**, **Clean Retail Value** (+ toggle **CPO**), **Auction (Low/Avg/High)**, **New (Low/Avg/High)**.
- **DMA Retail Value** cuando hay zip (si no, regional/nacional).
- **VIN Precision+**: lista de **equipment/accessories** detectados con su **Content Adjustment**.

**D. Forecast / depreciación.** Bloque de **curva de forecast 1-36 meses** con insights de depreciación, junto al
valor actual — "a view into the future fluctuations of values" para pricing/marketing/portfolio.

**E. Ficha de modelo (consumo).** Combina **pricing & values** + **Consumer Verified Ratings** (overall + quality &
reliability, driving experience, dealer sales, dealer service) + **specs/MPG/safety/warranty** + **imágenes/vídeos**
(ChromeData) + **incentivos** mapeados a zip. Awards/sellos (**ALG Residual Value Award**, J.D. Power awards) como prueba de confianza.

**F. Cars for Sale (marketplace).** Listings con **descripción a nivel VIN** (build data del fabricante) + filtros por
body style/make/trim/fuel/location; quote de dealer (Make/Model/Zip).

**G. Comparador.** **Side-by-side hasta 3 vehículos**: pricing, MPG, specs, pictures, safety features, warranty.

**H. Índice de mercado (UVPI).** Entrega **fuera de la ficha**: **reporte mensual Excel/CSV** con gráfico de índice
mayorista a nivel **industria** (desde 1995) y **segmento** (14+), con **forecast a 2 años**. Es un panel de mercado, no de coche.

**I. Vehicle history.** Botón/CTA que deriva a **AutoCheck** (Experian) — no es dato propio embebido.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Valor basado en transacción RETAIL real (PIN)**, no en extrapolación de subasta: **>12 M transacciones retail/año**,
   **>16.000 dealers**, **>250 métricas por reporte**. Lo afirman explícitamente frente a **KBB y Black Book**.
2. **ALG = la autoridad de valores residuales** de Norteamérica: **casi todas las transacciones de leasing US** y
   **~40% de los lanzamientos** se apoyan en ALG (50+ años). Producto de forecast que KBB no iguala.
3. **VIN Precision+ / As-Built**: valoración con **VIN de 17 caracteres**, **opciones de fábrica línea a línea**
   (add/deducts), pensado para **lenders** (ejemplo de **$180 M** de discrepancia en cartera de 500k). Precisión de nicho.
4. **El estándar del sector financiero**: el legado **NADA (1933)** = el "libro" de **Loan Value** para bancos,
   credit unions y aseguradoras. Aceptación regulatoria/lending difícil de replicar.
5. **Amplitud de activos inigualable**: coches, light/commercial trucks, **motos, ATV, snowmobiles, PWC, RV, BARCOS,
   manufactured homes, classic cars, farm equipment**. (KBB **no** valora barcos/RV; J.D. Power **sí**.)
6. **Dos lados del mercado**: **PIN (retail)** + **AuctionNet (>80% de subastas)** → retail y mayorista bajo un techo.
7. **Índice de precio mayorista propio (UVPI)** con **forecast a 2 años** e histórico desde **1995**, en Excel/CSV.
8. **Ecosistema de datos completo** tras Autodata/ChromeData: **specs + VIN decode + build data + imágenes/vídeos +
   incentivos** — no solo valor, sino la descripción y la oferta.
9. **Precio self-service transparente** (Values Online/Connect con tarifas públicas) — más que KBB B2B.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo EE. UU.** para valores de guía ("US-spec only"); **Canadá solo vía ALG**; **sin Europa ni global.** ← hueco mayor para cardeep.
2. **Vehicle history NO propio** — depende de **AutoCheck (Experian)** y afiliados (BeenVerified); igual debilidad que KBB.
3. **Marca de consumo más débil que KBB**: el público dice "Blue Book", no "J.D. Power value"; J.D. Power es fuerte en
   **B2B/financiero**, no en notoriedad de consumidor.
4. **Refresco mensual** de Trade-In/Loan/Retail (vs. cadencia más fresca en algunos valores de rivales); solo New/Auction son semanales.
5. **Sin oferta transaccional real al consumidor** tipo **Instant Cash Offer** redimible de KBB. `[NO-VERIFICADO exhaustivo; ausente del catálogo]`
6. **Métricas de velocidad de mercado de consumo** (days-to-sell, **market days supply**, **price-to-market %**,
   índice oferta/demanda por listing) **no** son producto público destacado; MarketValues da retail hiperlocal + forecast,
   pero no el set de "market speed" estilo vAuto/CarGurus. `[PARCIAL / NO-VERIFICADO como producto nombrado]`
7. **Contenido enterprise gateado**: las páginas `/business/*` están **bloqueadas (403)** al público; **pricing enterprise opaco** (call for quote) → fricción.
8. **Millaje y condición = input del usuario/dealer**, no telemetría/odómetro en vivo.
9. **No publica curva de depreciación granular descargable** a nivel consumidor (la curva 1-36 m vive en herramientas de pago).
10. **Sin badges de pricing en SRP/VDP** estilo "Good/Great Price" de KBB Price Advisor para el inventario del dealer. `[NO-VERIFICADO; no aparece en su oferta]`

---

## 10. Fuentes

**Sitio B2B de valoración (jdpowervalues.com) — accesible:**
- Home: https://www.jdpowervalues.com/
- API & Web Services Solutions (catálogo + precios Connect): https://www.jdpowervalues.com/api-and-web-services-solutions
- Values Online (tipos de valor + precios): https://www.jdpowervalues.com/get-values/values-online
- Web Service - Specialty Data: https://www.jdpowervalues.com/get-values/web-services
- MarketValues: https://www.jdpowervalues.com/marketvalues
- Features that Enhance Our Products (VIN Precision+, As-Built): https://www.jdpowervalues.com/features-enhance-our-products
- FAQ (definiciones, condición, US-only, CPO, forecast 3-60m): https://www.jdpowervalues.com/frequently-asked-questions
- Official Used Car Guide (impreso, 7 años, 10 regiones, $662): https://www.jdpowervalues.com/get-values/adan-official-used-car-guide
- Used Vehicle Price Index (AuctionNet): https://www.jdpowervalues.com/get-values/used-vehicle-price-index
- ALG Automotive Insights & Outlook: https://www.jdpowervalues.com/alg-automotive-insights-outlook
- ALG acquisition article (30-nov-2020): https://www.jdpowervalues.com/article/jd-power-poised-set-new-vision-automotive-forecasting-after-completing-alg-acquisition

**Portal consumo (jdpower.com) — navegado vía Playwright (anti-bot en WebFetch):**
- Car values home: https://www.jdpower.com/cars
- Trade-In Value (flujo 4 pasos + metodología PIN vs KBB/Black Book): https://www.jdpower.com/trade-in-value
- JD Power Pricing and Values (4 pilares de consumo): https://www.jdpower.com/jd-power-pricing-and-values

**Prensa / terceros (verificación cruzada):**
- Adquisición NADA UCG (completada 2015, NADA 1933): https://www.prnewswire.com/news-releases/jd-power-completes-acquisition-of-nada-used-car-guide-expanding-its-analytics-and-modeling-capabilities-in-the-used-vehicle-industry-300107618.html
- VIN Values (jun-2019, márgenes 6-13%): https://www.prnewswire.com/news-releases/jd-power-helps-businesses-leap-over-data-bar-with-vin-values-300862120.html
- VIN-Specific Valuations: https://www.prnewswire.com/news-releases/jd-power-launches-vin-specific-vehicle-valuations-300742856.html
- Used Vehicle Price Index (2017, AuctionNet >80%, 2 años forecast): https://www.prnewswire.com/news-releases/jd-powers-used-vehicle-price-index-service-forecasts-prices-up-to-two-years-into-the-future-300503779.html
- Owner Thoma Bravo + Autodata: https://www.thomabravo.com/portfolio/jd-power ; https://www.chicagobusiness.com/finance-banking/thoma-bravo-finalizes-jd-power-acquisition
- J.D. Power (HQ Troy MI, CEO, historia): https://en.wikipedia.org/wiki/J.D._Power
- ChromeData VIN Descriptions / IAA: https://www.prnewswire.com/news-releases/iaa-implements-jd-power-chromedata-vin-descriptions-to-enhance-trim-coverage-302043962.html
- As-Built Valuation Service (página 403; contenido vía WebSearch): https://www.jdpower.com/business/built-valuation-service
- ChromeData VIN Descriptions (403; vía WebSearch): https://www.jdpower.com/business/chromedata-vin-descriptions

### Notas de verificación
- **Tipos de valor, condición (verbatim), update frequency, US-only, CPO, forecast:** doble fuente (Values Online +
  FAQ + página de consumo). **[VERIFICADO]**
- **Diferencial PIN retail vs KBB/Black Book auction:** texto literal en jdpower.com/trade-in-value. **[VERIFICADO]**
- **Precios self-service (Values Online, Connect, guía impresa):** página oficial jdpowervalues. **[VERIFICADO]**
- **Pricing enterprise / API / As-Built:** no divulgado (call for quote). **[NO-VERIFICADO importe]**
- **Horizonte de forecast:** 1-36 m (productos) vs 3-60 m (ALG en FAQ) vs 3-36 m (una fuente API) — discrepancia reportada. **[VERIFICADO con conflicto]**
- **HQ histórico de Valuation Services (McLean VA / Costa Mesa CA):** **[PARCIAL-VERIFICADO]**.
- **Ausencia de ICO, badges SRP/VDP, market-days-supply como producto nombrado:** inferida por ausencia del catálogo. **[NO-VERIFICADO exhaustivo]**
- **Páginas `/business/*`:** bloqueadas (403) incluso vía navegador headless; su contenido se reconstruyó por WebSearch + prensa.
