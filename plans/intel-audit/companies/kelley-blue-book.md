# Kelley Blue Book — Auditoría atómica

> Slug: `kelley-blue-book` · Subdominio cardeep: **valuation** · Región: Norteamérica (US, +Canadá B2B)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[NO-VERIFICADO]` donde no se confirmó.
> Naturaleza: empresa de **valoración de vehículos** (la marca de valor de coche más reconocida de EE. UU.),
> hoy una marca de datos B2B + portal de consumo dentro de Cox Automotive.

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre | Kelley Blue Book (KBB) / "Blue Book" | kbb.com |
| Fundación | 1918 (Kelley Kar Company, Les Kelley); primer *Blue Book* publicado **1926** | Wikipedia; kbb.com/company/history |
| Owner / grupo | **Cox Automotive** (subsidiaria de **Cox Enterprises**, Atlanta, privada, ~$20B ingresos) | WebSearch; coxautoinc.com |
| HQ | **Irvine, California** | Wikipedia; mediaroom.kbb.com |
| Historia corporativa | AutoTrader.com adquirió KBB → consolidada en Cox Automotive (20+ marcas) | coxautoinc.com |
| Sitios | `kbb.com` (consumo), `b2b.kbb.com` (B2B EE. UU.), `b2b.kbb.ca` (B2B Canadá), `quickvalues.com` (self-service), `mediaroom.kbb.com` (prensa) | verificado |
| Posicionamiento | "Blue Book Value" es prácticamente un genérico del valor de coche en EE. UU. | múltiples |

**Categorías de producto:** (1) Valoración de vehículos (núcleo), (2) Datos/API de valores B2B,
(3) Herramientas de dealer (tasación, pricing, ICO, leads, listings, publicidad), (4) Contenido editorial
(ratings, reviews, awards), (5) Estudios de mercado/investigación (Brand Watch).

**Cliente objetivo:** Consumidores (portal kbb.com) · **Dealers** (franquicia + independiente) ·
**OEMs** (publicidad Tier 1/2/3) · **Lenders / instituciones financieras** (LTV, riesgo cartera, remarketing) ·
**Aseguradoras** · **Desarrolladores de software / sitios de terceros** (syndication API) ·
**Marketing de correo directo**. (Fuente: b2b.kbb.com.)

---

## 2. Cobertura

- **Geografía:** **EE. UU.** (núcleo) con **134 regiones geográficas** analizadas individualmente por
  precio/condiciones económicas locales. Presencia B2B en **Canadá** (`b2b.kbb.ca`, "Pricing Service API").
  **NO** hay cobertura europea ni global. (Fuente: b2b.kbb.com FAQ; b2b.kbb.ca.)
- **Nuevo y usado:** ambos. Usado es el corazón histórico; nuevo incluye MSRP/Invoice/Fair Purchase Price/Residual.
- **Tipos de vehículo:**
  - Turismos, **trucks (pickups), SUV, minivan** (núcleo). (kbb.com/car-values)
  - **Powersports:** motocicletas, ATV, mopeds/scooters, **snowmobiles**, **personal watercraft (PWC)**.
    (kbb.com/motorcycles; Quick Values; IDWS "Powersports Values".)
  - **NO** valora **barcos/boats**, ni motores fueraborda, ni remolques, ni **autocaravanas (RV)** —
    explícitamente porque la muestra de datos es insuficiente para su nivel de confianza. **[GAP]**
    (Fuente: kbb.com/car-advice/kelley-blue-book-boats.)
  - **NO** valora clásicos/colección (territorio de Hagerty/NADA). `[NO-VERIFICADO exhaustivo, pero ausente del catálogo]`

---

## 3. Productos + campos atómicos

### 3.1 Tipos de VALOR (la materia prima) — definiciones oficiales B2B

Fuente primaria: `b2b.kbb.com/kbb-vehicle-values/definitions-of-our-values/` + PDF *InfoDriver Display Requirements v5*.

**Nuevo:**
| Valor | Definición atómica |
|---|---|
| **MSRP** | Precio sugerido por el fabricante (incl. destino + equipo mínimo; excl. tasas/impuestos). |
| **Dealer Invoice** | Precio que el fabricante cobra al dealer (incl. destino; excl. costes/incentivos del dealer). |
| **New Car Fair Purchase Price** | Punto medio del Fair Market Range; lo que un consumidor puede esperar pagar **esta semana** en su zona, con sus opciones, excl. impuestos/tasas/incentivos. Basado en transacciones reales. |
| **New Car Fair Market Range** | Rango (low–high) de precio razonable esta semana. |
| **Residual Value** | Pronóstico del valor futuro de mercado; valor a fin de leasing (plazos **24–60 meses**). |
| **Resale Value (% retenido)** | % del MSRP retenido a **3, 4 y 5 años**; con gráfico de depreciación y comparación vs segmento e industria. |

**Usado:**
| Valor | Definición atómica |
|---|---|
| **Trade-In Value** | Lo que un consumidor recibe de un dealer al entregar su coche (asume tasación precisa de condición). |
| **Trade-In Range** | Rango semanal (low–high) de trade-in. |
| **Private Party Value** | Punto de partida de negociación entre particulares; "as-is", sin garantías. |
| **Private Party Range** | Rango semanal (low–high) particular. |
| **Typical Listing Price** | (antes "Suggested Retail Price") precio de salida que pide el dealer; asume reacondicionado total + título limpio. |
| **Used Car Fair Purchase Price** | Punto medio semanal de lo que se paga a un dealer (transacciones reales). |
| **Used Car Fair Market Range** | Rango semanal (low–high) compra a dealer. |
| **Auction Value** | Precio esperado en subasta mayorista (excl. fees de comprador y reacondicionado). **Prohibido mostrar en público — solo B2B.** |
| **Lending Value** | Valor de referencia para prestamistas wholesale y retail (asume buena condición + reacondicionado total). **Prohibido mostrar en público — solo B2B.** |
| **Instant Cash Offer (ICO)** | Oferta **fija** real de compra, válida **7 días**, redimible en dealer participante. |
| **Original MSRP** | MSRP original del vehículo usado (referencia de depreciación). |

**CPO (Certified Pre-Owned):**
| Valor | Definición |
|---|---|
| **Fair Purchase Price (CPO)** | Punto medio semanal para vehículos certificados según estándares del fabricante. |
| **Typical Listing Price (CPO)** | Precio de salida CPO (con garantía del fabricante). CPO suele añadir **$1.000–$2.000** al valor de mercado. |

### 3.2 Condición (modificador transversal del valor)

Tiers oficiales (texto del PDF de display): **Excellent** (<5% de vehículos; como nuevo, sin pintura/chapa,
sin óxido, neumáticos como nuevos, título limpio, pasa safety+smog, historial de servicio completo) ·
**Very Good** (defectos cosméticos menores, neumáticos ≥75% banda, casi todo el historial) ·
**Good** (defectos cosméticos reparables, neumáticos ≥50% banda, algo de historial — **la mayoría** de
vehículos de consumidor) · **Fair** (defectos a reparar, óxido reparable, neumáticos a cambiar, poco historial) ·
**Poor** (KBB **no** da valor). Solo Trade-In y Private Party requieren condición.
**Condition Quiz** evalúa: exterior, interior, mecánica, registros de mantenimiento, emisiones, título limpio,
neumáticos, óxido, pintura/chapa. (Fuente: PDF InfoDriver; kbb.com/detailed-condition-quiz.)

### 3.3 5-Year Cost to Own (5YCTO / TCO) — desglose atómico

Producto de coste total de propiedad. Esquema del objeto de respuesta de **InfoDriver Web Service 4.0**
(verbatim del PDF de display, sección "Technical Information"):

| Campo (API) | Significado | Definición/base de cálculo |
|---|---|---|
| `yearTotal.total` | **5-Year Cost to Own total** | Depreciación + gastos de bolsillo. |
| `depreciation.total` + `.year1..year5` | **Loss of Value / Depreciation** | Lo pagado − valor a 5 años. |
| `fuel.total` + `.year1..year5` | **Fuel** | 15.000 mi/año, 45% autopista / 55% ciudad, datos EPA. |
| `insurance.total` + `.year1..year5` | **Insurance** | Prima media estatal (colisión + responsabilidad). |
| `financing.total` + `.year1..year5` | **Financing** | APR **3,09%**, 60 meses, 10% entrada. |
| `stateFees.total` + `.year1..year5` | **State Fees** | Licencia, matrícula, impuesto venta (media nacional). |
| `maintenanceAndRepairs.total` + `.year1..year5` | **Maintenance & Repairs** | Mantenimiento = plan fabricante (media nacional piezas+mano de obra); Repairs = garantía extendida 5 años $0 franquicia. |
| (suma) | **Out of Pocket Expenses** | fuel+insurance+financing+stateFees+maintenance&repairs. |
| `costPerMile.cost` | **Cost per Mile** | Total 5 años / 75.000 millas. |
| `valueRating.rating` | **5YCTO Value Rating** | Among the Best / Lower Cost Than Most / Average Cost / Higher Cost Than Most. |

Regla de presentación: "Out of Pocket" y "Depreciation" **nunca** se muestran de forma independiente.
Disponible vía API para syndication desde 2019. (Fuentes: PDF; prnewswire 5YCTO API 2019.)

### 3.4 Ratings & contenido editorial (capa de confianza)

- **KBB.com Expert Rating:** escala **0.0–5.0** (décimas). Categorías: **Overall + performance, comfort,
  styling, value, quality, reliability** (de 5 estrellas). El equipo editorial vota/ordena vs rivales antes de puntuar.
- **KBB.com Consumer Rating:** mismas 6 categorías + Overall; "Based on N consumer ratings".
- **Expert Reviews**, **Consumer Reviews** (owner), **Editorial Top 10 Lists**, **Articles**.
  (Fuente: PDF InfoDriver §II; b2b IDWS; kbb.com/car-news/how-kelley-blue-book-rates-cars.)

### 3.5 Premios / investigación de mercado (productos de inteligencia)

| Producto | Qué mide | Métrica atómica |
|---|---|---|
| **Best Resale Value Awards** | Mejor retención de valor | % del MSRP retenido a 5 años (Top10 ≈ ≥55%; media industria ≈45%). Residual = valor futuro de subasta, condición media, **75.000 millas**, fin de leasing 5 años. |
| **Best Buy Awards** | Mejor compra por segmento | Pondera resale value + fiabilidad + 5YCTO. |
| **Consumer Choice Awards** (ex *Brand Image Awards*) | Entusiasmo de marca | Derivado del Brand Watch Study. |
| **5-Year Cost to Own Awards** | Menor coste total | 5YCTO. |
| **Brand Watch Study** | Consideración de marca | **12.000+** compradores in-market/año; **14 factores**: Durability/Reliability, Technology, Safety, Exterior Styling, Driving Comfort, Reputation, Driving Performance, Fuel Efficiency, Interior Layout, Ruggedness, Affordability, Prestige/Sophistication, value-for-money (… lista completa de 14 `[PARCIAL-VERIFICADO]`). |

### 3.6 Productos B2B (entrega de los valores anteriores)

| Producto | Qué es | Campos/valores que entrega |
|---|---|---|
| **Price Advisor** | Visual de Fair Market Range para pricing/merchandising de dealer | Fair Market Range, posición del precio (zona **Blanca**=bajo / **Verde**=dentro / **Roja**=sobre rango), badges **"Good Price" / "Great Price"** en SRP/VDP. 250+ fuentes, semanal. |
| **Quick Values** | Self-service `quickvalues.com` (créditos por uso) | MSRP, FPP, Invoice, Residual (nuevo); Typical Listing Price, FPP, Private Party, Trade-In Range (usado); Typical Listing + FPP (CPO); Lending Value, Auction Value (wholesale/fin); historial de valor retail desde **ene-2014**; snowmobiles + PWC. |
| **InfoDriver Web Service (IDWS) / Pricing Service API** | API **REST** para integrar en web/app/inventario/originación de préstamos | New: MSRP, FPP, FMR, Invoice, Residual · Used: Original MSRP, Typical Listing Price, FPP, FMR, Private Party Value+Range, Lending, Auction, Trade-In Value+Range · Powersports · Consumer/Expert Ratings & Reviews · Top 10 Lists · **VIN decode (nuevo + usado)** · 5YCTO. |
| **InfoDriver Batch VIN (IDBV)** | Valoración por lotes (archivo) | Inputs: VIN, Mileage (ajuste on/off), ZIP. Range-based pricing. **Historial de valor desde ene-2014**, múltiples fechas por archivo. Para marketing directo, financieras (riesgo cartera, remarketing), lenders (LTV). |
| **Instant Cash Offer (ICO)** | Oferta real redimible (dealer) | Oferta fija 7 días; ver §3.1 + §6. |
| **Trade-In Advisor / LeadDriver** | Tasación + generación de leads en sitio de dealer | Trade-In Value/Range + captura de lead. |
| **Vehicle Listings / Display Advertising / Service Advisor** | Publicidad de inventario y servicio | (marketing, no datos de valor). |
| **Vehicle History Reports** | Historial de vehículo **vía Experian AutoCheck** (partner) | Título, siniestros, odómetro, dueños (datos de AutoCheck, no propios de KBB). |

---

## 4. Metodología / fuentes de datos

- **Volumen:** **250+ fuentes** wholesale y retail; **~100.000 transacciones de subasta/semana**;
  **~3 billones (3 trillion) de data points**.
- **Fuentes:** resultados de subasta mayorista (Manheim, hermana en Cox), registros de transacción de
  dealers, ventas entre particulares (vía registros DMV estatales), relaciones con subastas/fabricantes/dealers.
- **Granularidad geográfica:** **134 regiones** EE. UU., cada una analizada por separado.
- **Ajuste por kilometraje:** estadísticos determinan el **kilometraje típico** por edad/tiempo en mercado;
  ajustan al alza/baja según desviación (menos km → más valor).
- **Ajuste por opciones/equipamiento:** información granular; los valores de cada opción **se deprecian** anualmente.
- **Factores macro:** coste de gasolina, niveles de producción, oferta/demanda, eventos catalíticos
  (huracanes, inundaciones, picos de gasolina), competencia por segmento, tendencias estacionales.
- **Proceso:** normalización → escrutinio del equipo de analítica (se descartan anomalías/datos faltantes)
  → data warehouse → **modelo de regresión semanal** → validación.
- **Actualización:** **al menos semanal**. Ventana de forecast **≤1 semana** antes de publicar
  (vs. competidores que pronostican con 3–4 semanas). Analistas regionales de campo (CA→NY).
- **Residual Value Guide:** *Kelley Blue Book Official Residual Value Guide*; residual = valor futuro de
  subasta/wholesale para vehículo limpio/reacondicionado, condición media, **75.000 millas**, fin de leasing 5 años.

(Fuentes: b2b.kbb.com; mediaroom.kbb.com press releases; originalpricing.com; vehicleremarket.com.)

---

## 5. Entrega

| Canal | Detalle |
|---|---|
| **Portal web consumo** | `kbb.com` (What's My Car Worth, Price New/Used Car, ratings, reviews, awards, 5YCTO). |
| **API REST** | InfoDriver Web Service / Pricing Service API (web, app móvil, inventario, originación de préstamos). |
| **Batch / archivo** | InfoDriver Batch VIN (formato de archivo flexible "as-is"; salida con/ sin ajuste de km). |
| **Self-service** | `quickvalues.com` (créditos prepago). |
| **Embebido en sitio de dealer** | Price Advisor (badges en SRP/VDP), Trade-In Advisor, ICO, Vehicle Listings. |
| **Integración DMS/CRM** | Quick Values e ICO integran con DMS y CRM principales; ecosistema Cox (vAuto, Dealertrack, VinSolutions, Manheim, Autotrader, Dealer.com, Xtime, NextGear Capital). |
| **Syndication de contenido** | Ratings/Reviews/Articles/5YCTO licenciables a terceros (con reglas de display estrictas). |

---

## 6. Precio

- **No hay tarifas públicas.** Modelo = **licencia/suscripción B2B + contactar ventas** (`b2b.kbb.com/contact`).
- **Quick Values:** **uso (créditos prepago)**, descuento por volumen ("cuantos más créditos, menor coste"),
  cotización a medida por dealer.
- **API / Batch / syndication:** licencia negociada (Order Form con "Update Period"); precio no divulgado. `[NO-VERIFICADO]` el importe.
- Portal de consumo `kbb.com`: **gratis** para el usuario (monetiza con leads/publicidad OEM/dealer).
(Fuente: b2b.kbb.com/solutions/quick-values; b2b.kbb.com/contact.)

---

## 7. Placement (patrón web — clave para cardeep)

> Esto es lo que cardeep imita para **dónde** colocar cada dato. Derivado del PDF oficial
> *InfoDriver Display Requirements v5 (2025-08-15)* + el portal kbb.com.

**A. Generación de valoración (formulario / ficha de entrada).** Antes de mostrar valor, se piden (atómico):
Year, Make, Model, **Trim, Engine, Transmission, Drivetrain**, Mileage, ZIP, **Optional equipment**,
y **Condition** (solo Trade-In/Private Party).

**B. Página de valor (la "ficha de valoración").** Debe contener, juntos:
1. Etiqueta del tipo de valor ("Kelley Blue Book® <tipo> Value").
2. **Fecha** de generación.
3. **ZIP** introducido.
4. Descripción del vehículo (Y/M/M/trim/engine/trans/drivetrain/mileage/opciones seleccionadas).
5. Definición del valor (9pt o **rollover/tooltip**).
6. Definición de la **condición** (rollover) cuando es Trade-In/Private Party.
7. Marca + copyright/disclaimer.

**C. Rango vs punto.** El valor se presenta como **Fair Market Range (low–high)** con el **Fair Purchase
Price** como punto medio destacado. En herramienta de dealer (Price Advisor) → barra de 3 zonas
**Blanca/Verde/Roja** + badge **Good/Great Price** sobre cada listing (SRP) y ficha de detalle (VDP).

**D. Ficha de coche nuevo.** Resale Value aparece **en todos los reportes de precio de coche nuevo**:
**gráfico de depreciación** + rating de retención de valor a **3 años**, con enlace "Learn More" →
comparación a **3/4/5 años** vs segmento e industria.

**E. Bloque 5-Year Cost to Own (ficha de modelo nuevo).** Encabezado "Kelley Blue Book® 5-Year Cost to
Own" + total; opción de **expandir** al desglose por componente (Fuel, Insurance, Financing, State Fees,
Maintenance & Repairs, Depreciation) con el total debajo; **Cost per Mile** y **Rating "How Does It Compare
to Similar Cars?"** opcionales.

**F. Bloque Ratings & Reviews (ficha de modelo).** Encabezado "KBB.com Expert/Consumer Ratings",
**Overall** + estrellas (de 5) + categorías (performance/comfort/styling/value/quality/reliability),
"Based on N ratings", y enlace "See more at KBB.com".

**G. Premios.** Badges/sellos (Best Buy, Best Resale Value, Consumer Choice) colocados en la ficha de modelo
como prueba de confianza.

**H. ICO (flujo transaccional propio).** Pantalla 1: VIN o matrícula → Pantalla 2: cuestionario de condición
(opciones, mecánica, interior/exterior, km) → Pantalla 3: **oferta fija** + validez 7 días + lista de
**dealers participantes** + nota de reajuste si la inspección/+50 millas difieren.

**Reglas de marca relevantes:** el logo del cliente domina; la "Kelley Mark" es secundaria; **Auction Value y
Lending Value NUNCA se muestran al público** (solo B2B/interno).

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Marca de confianza #1 de consumo** en EE. UU. (desde 1926); "Blue Book Value" es casi un genérico.
2. **Actualización semanal con forecast ≤1 semana** (competidores 3–4 semanas) → valores más frescos.
3. **Ecosistema Cox cerrado** wholesale→retail: **Manheim** (mayor subasta mayorista de EE. UU., ~100k
   transacciones/semana) + vAuto + Dealertrack + VinSolutions + Autotrader alimentan y consumen el dato.
4. **Instant Cash Offer:** no es un estimado, es una **oferta real redimible** que el dealer está obligado a
   honrar — producto transaccional, no solo informativo.
5. **Range-based pricing** (Fair Market Range) + **badging de 3 zonas** (Good/Great Price) listo para SRP/VDP.
6. **Capa de contenido y autoridad** empaquetada con el valor: Expert/Consumer Ratings+Reviews, Awards,
   Brand Watch, 5YCTO — un *halo* de confianza que pocos rivales de datos puros tienen.
7. **Historial de valor** consultable **desde enero 2014** (Quick Values / Batch VIN).
8. **Micro-regionalización** (134 regiones) en valores de consumo.

---

## 9. Gaps (lo que NO ofrece)

1. **Solo EE. UU.** (+ B2B limitado en Canadá). **Sin Europa ni global.** ← gran hueco para cardeep.
2. **No valora boats, RVs, fueraborda, remolques** (muestra insuficiente) ni clásicos/colección.
3. **No tiene historial/provenance VIN propio** — lo subcontrata a **Experian AutoCheck** (rival de Carfax).
4. **Auction Value y Lending Value vetados al público** — la inteligencia wholesale fina es B2B-gated.
5. **Kilometraje = input del usuario**, no telemetría/odómetro en vivo; sin feed de km real.
6. **Precio opaco** (sin tarifa pública); fricción de ventas.
7. **No es catálogo de specs profundo** — los specs (engine/trim/options/MPG) son capa de soporte, no
   producto estrella (Chrome Data/DataOne/Autovista van más hondo en specs/identificación).
8. **Métricas de velocidad de mercado** (days-to-sell, market days supply, price-to-market índice como
   métrica de consumo) **no** son producto KBB de cara al público — viven en **vAuto** (hermano Cox), no en
   KBB. `[PARCIAL: el dato existe en el grupo, pero no bajo marca KBB]`
9. **No publica curva de depreciación granular descargable** ni dataset crudo; entrega valores puntuales/rango.

---

## 10. Fuentes

- Definiciones de valores (B2B): https://b2b.kbb.com/kbb-vehicle-values/definitions-of-our-values/
- B2B home / soluciones: https://b2b.kbb.com/
- InfoDriver Web Service (IDWS): https://b2b.kbb.com/industry-solutions/info-driver-web-service-idws/
- InfoDriver Batch VIN (IDBV): https://b2b.kbb.com/industry-solutions/info-driver-batch-vin-idbv/
- Quick Values: https://b2b.kbb.com/solutions/quick-values/
- Price Advisor: https://b2b.kbb.com/solutions/price-advisor/
- **PDF InfoDriver Display Requirements v5 (placement bible):** https://www.coxautoinc.com/wp-content/uploads/sites/3/Kelley-Blue-Book-INFODRIVER-Display-Requirements.pdf
- Pricing Service API (Canadá): https://b2b.kbb.ca/industrysolutions/pricingserviceapi/
- 5YCTO API (syndication, 2019): https://www.prnewswire.com/news-releases/kelley-blue-book-5-year-cost-to-own-data-now-available-for-syndication-via-api-300925766.html
- TCO / 5-Year Cost to Own (consumo): https://www.kbb.com/new-cars/total-cost-of-ownership/
- Cómo califica KBB: https://www.kbb.com/car-news/how-kelley-blue-book-rates-cars/
- Instant Cash Offer FAQ: https://www.kbb.com/faq/ico/  · B2B ICO: https://b2b.kbb.com/solutions/ico/
- Condición / quiz: https://www.kbb.com/detailed-condition-quiz/
- Best Resale Value Awards 2026: https://mediaroom.kbb.com/2026-03-19-Kelley-Blue-Book-Announces-2026-Best-Resale-Value-Award-Winners
- Resale value en cada vehículo nuevo: https://mediaroom.kbb.com/press-releases?item=105717
- Brand Watch: https://www.coxautoinc.com/insights-hub/kelley-blue-book-revamps-brand-watch-toyota-and-lexus-top-the-leaderboard-in-2025-new-vehicle-consideration/
- Best Buy Awards: https://www.kbb.com/awards/best-buy-awards-2026/
- Boats (gap): https://www.kbb.com/car-advice/kelley-blue-book-boats/
- Powersports/motos: https://www.kbb.com/motorcycles/
- Metodología (semanal/regiones): https://mediaroom.kbb.com/press-releases?item=105826
- Identidad/owner: https://en.wikipedia.org/wiki/Kelley_Blue_Book ; https://www.coxautoinc.com/insights/kelley-blue-book-autotrader-align-common-leadership-team/

### Notas de verificación
- Tipos de valor, condición, inputs y placement: **doble fuente** (página B2B + PDF oficial de display). [VERIFICADO]
- 5YCTO sub-campos + esquema API: **PDF oficial** (sección técnica IDWS 4.0) + página TCO. [VERIFICADO]
- Lista completa de **14 factores** Brand Watch: 12 confirmados (report 2019 + notas 2025), 2 restantes `[PARCIAL-VERIFICADO]`.
- Importes de **precio B2B**: no divulgados públicamente. `[NO-VERIFICADO]`
- Days-to-sell / market days supply bajo marca KBB pública: ausente; existe en vAuto (Cox). `[PARCIAL]`
