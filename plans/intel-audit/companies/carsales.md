# carsales — Auditoría atómica

> **slug:** `carsales` · **subdominio de audit:** `portal-insights` · **web:** https://www.carsales.com.au/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído, `[VERIFICADO ≥2]` doble fuente, `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** el **mayor marketplace de automoción de Australia** y la **fuente primaria de dato vivo** del grupo. carsales no es una casa de valoración (eso es **RedBook**, su filial, auditada aparte) sino el **portal-marketplace + capa de insights** que **genera** el dato de mercado: precios anunciados live + delisted, views, leads, days-to-sell. Sobre ese foso construye **3 productos de precio al consumidor** (Car Valuation 3-modos powered-by-RedBook, **Price Indicator** Around/Below/Well-Below Market, **PriceAssist** para vendedor), **Instant Offer** (C2Dealer), **CarFacts** (historial PPSR), **RedBook Inspect** (inspección), y una suite dealer de inteligencia (**LiveMarket** + **Acquire** + IA AutoGate) + media OEM (**mediahouse**). Patrón de colocación directísimo para cardeep: el **Price Indicator sobre la ficha** y el **PriceAssist sobre el flujo de venta** son exactamente el blueprint "dato de mercado pegado al anuncio".

> **Desambiguación (crítico):** este informe cubre **carsales.com.au** (el marketplace AU de **CAR Group**). NO confundir con:
> **RedBook** (motor de valoración/specs del mismo grupo → `redbook.md`), **Encar** (Corea, mismo grupo → audit propio),
> **webmotors** (Brasil, mismo grupo → audit propio), **Trader Interactive** / **chileautos** (mismo grupo). carsales **alimenta** a RedBook con su feed; RedBook **devuelve** valoración a carsales. Son productos distintos. [VERIFICADO ≥2: redbook.md, footer carsales.com.au]

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **carsales** (estilizado minúscula; "carsales.com.au") | [VERIFICADO] |
| Razón social operadora | **carsales.com.au Pty Ltd** (footer "© carsales.com.au Pty Ltd 1999-2026") | [VERIFICADO: footer live] |
| Grupo / owner | **CAR Group Limited** (ASX: **CAR**) — antes "carsales.com Limited" | [VERIFICADO ≥2: Wikipedia CAR Group, cargroup.com] |
| Rebranding del grupo | "carsales.com Limited" → **CAR Group Limited** en **2023** (refleja escala fuera de AU) | [VERIFICADO ≥2: Wikipedia, búsqueda] |
| Constitución del grupo | **CAR Group Limited incorporada en 1996** | [VERIFICADO: búsqueda corporativa] |
| Fundación de carsales | **1997**, en **Melbourne**, por **Greg Roebuck** y **Wal Pisciotta** (idea: mover los clasificados de prensa de motor a internet) | [VERIFICADO ≥2: búsqueda + Wikipedia] |
| HQ | **Melbourne, Australia** | [VERIFICADO ≥2] |
| Bolsa | **ASX: CAR** · constituyente del **ASX 50** | [VERIFICADO ≥2] |
| Relación con inversores | shareholder.carsales.com.au / cargroup.com | [VERIFICADO: footer + búsqueda] |
| Posicionamiento | "Australia's Go-To for Cars — Buy It. Sell It. Love It.®"; "Australia's #1 auto website / largest online automotive marketplace" | [VERIFICADO ≥2: home title + business.carsales] |

**Qué es:** **marketplace digital de clasificados de automoción** (nuevo + usado, multi-vertical) que, gracias a ser el mayor de Australia, **produce el dato de mercado** (precios live/delisted, demanda, tiempos de venta) y lo monetiza en tres planos: (1) **consumidor** (valoración, indicador de precio, instant offer, historial, inspección); (2) **dealer** (gestión de stock/leads AutoGate + inteligencia LiveMarket/Acquire); (3) **OEM/marca** (publicidad y audiencia vía mediahouse).

### Categorías de producto
1. **Marketplace de clasificados** (carsales + red de verticales) — núcleo.
2. **Consumer pricing & valuation:** Car Valuation (3 modos), **Price Indicator** (sobre la ficha), **PriceAssist** (vendedor).
3. **Instant Offer** (venta C2Dealer en 24 h, oferta instantánea).
4. **Vehicle history / CarFacts** (informe de historial PPSR + market comparison).
5. **RedBook Inspect** (inspección física pre-compra / dealer) — filial.
6. **Research / Showroom** (catálogo de specs, reviews, comparador de coche nuevo).
7. **Dealer tools (AutoGate / Ignition):** gestión de inventario + leads + **LiveMarket** (inteligencia de mercado) + **Acquire** (sourcing) + capa **IA**.
8. **carsales mediahouse** (publicidad y datos de audiencia para OEM/marcas).
9. **RedBook** (valoración/specs B2B) — filial, audit propio.

### Cliente objetivo
**Consumidor** (comprador/vendedor particular) · **Dealers** (concesionarios) · **OEM / marcas / agencias de medios** (vía mediahouse) · indirectamente **finance/insurance** (targeting y leads). [VERIFICADO ≥2: business.carsales + mediahouse]

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado de esta marca | **Australia** (todo el dato atómico vive aquí) | [VERIFICADO] |
| Grupo CAR — marketplaces propios | **Australia (carsales)**, **Corea del Sur (Encar)**, **EE.UU. (Trader Interactive)**, **Chile (chileautos)**; **mayoritario en Brasil (webmotors)** | [VERIFICADO ≥2: footer carsales + búsqueda corporativa] |
| Red AU de verticales | **carsales** (coches) · **bikesales** (motos) · **boatsales** (barcos) · **caravancampingsales** (caravanas/camping) · **trucksales** (camiones) · **constructionsales** (maquinaria construcción) · **farmmachinerysales** (maquinaria agrícola) · **tyresales** (neumáticos) · **RedBook** | [VERIFICADO ≥2: footer live + búsqueda] |
| Scope vehículo | **Nuevo + usado + demo/near-new**; turismos, SUV, ute/LCV; y por vertical: motos, barcos, caravanas, camiones, maquinaria | [VERIFICADO ≥2: nav /cars/used + verticales] |
| Catálogo coche nuevo (Showroom) | **405 modelos** disponibles para comprar/encargar · **64 makes** | [VERIFICADO: snapshot showroom 2026-06-30] |
| Inventario usado vivo (referencia) | "over **220,000 cars** listed on carsales.com.au" (citado en Acquire); "**275,000+** anuncios" citado en flujo de valoración | [VERIFICADO ≥2: Acquire news + flujo valoración] |
| Histórico de mercado (LiveMarket) | datos de delisted **hasta 12 meses atrás** | [VERIFICADO ≥2: LiveMarket + búsqueda] |
| Escala de audiencia (red) | **8.9M** avg monthly users · **16M** members · **10M+** avg monthly video views · **88M** avg monthly searches | [VERIFICADO: business.carsales home] |
| Escala (mediahouse) | **15.2M+** members · **3.7B+** user signals across network | [VERIFICADO: mediahouse/solutions] |
| Valoraciones gratis | "**10,000+** car valuations free per month" (citado en flujo) | [VERIFICADO: flujo valoración] |

---

## 3. Productos + campos atómicos

> Notación: campos confirmados en página de producto / FAQ help-centre / pantallas live capturadas con navegador (Playwright) / modal de indicador (csnstatic). Las fichas de detalle (`/cars/details/...`) están tras **captcha DataDome**; sus specs **espejan a RedBook** (que las suministra) y se documentan exhaustivamente en `redbook.md`.

### 3.1 Car Valuation — "Value my car" (powered by RedBook)
**Qué es:** valoración online gratuita en minutos, "based on the sales of thousands of listed cars". Logo "**Supported by RedBook**". [VERIFICADO ≥2: car-valuations live + redbook.md]
**Campos atómicos:**
- **Modo de valoración** (3): `I'm selling` · `I'm buying` · `I'm trading in` (contexto que cambia el precio de salida) [VERIFICADO: snapshot live]
- **Inputs:** `Make` → `Model` → (pasos siguientes: year/variant, kilometres, condition) [VERIFICADO: snapshot; pasos posteriores [NO-VERIFICADO en detalle]]
- **Output:** valor estimado tailored al coche concreto ("you'll know what price to expect") — rango/precio según modo [VERIFICADO: copy live; estructura exacta del output [NO-VERIFICADO]]
- Sin coste, **sin follow-up call** ("No strings attached") [VERIFICADO]
- Factores que influyen + método de cálculo expuestos en FAQ: "What factors influence the valuation", "How is the car valuation calculated", "What information do I need to provide" [VERIFICADO: FAQ headings live]

### 3.2 Price Indicator — indicador de precio sobre la ficha (clave placement)
**Qué es:** badge automático sobre anuncios que compara el precio con el de coches similares **recientemente anunciados** en carsales ("live market pricing"). [VERIFICADO ≥2: Price Indicators FAQ + modal csnstatic]
**Tiers (3):** `Around Market Price` · `Below Market Price` · `Well Below Market Price` [VERIFICADO ≥2: búsqueda help + modal]
**Atributos considerados (10):** `Make`, `Model`, `Badge`, `Year`, `Engine size`, `Body`, `Series`, `Transmission`, `Standard features`, `Kilometres` [VERIFICADO ≥2: modal v3/v5 csnstatic]
**Atributos NO considerados (5):** condición del vehículo · extras opcionales/customización · ubicación · "manufacturer certified" · beneficios de comprar vía dealer [VERIFICADO ≥2: modal]
**Exclusiones (no aparece indicador si):** precio **< AU$5,000 o > AU$70,000** · antigüedad **< 2 años o > 15 años** · datos insuficientes para comparar · coche con **hail damage** o **written-off** declarado [VERIFICADO ≥2: modal + búsqueda]
**Naturaleza:** dinámico — "fluctúa con el mercado" (mismo precio puede cambiar de tier semana a semana); no editable ni comprable por el vendedor [VERIFICADO ≥2]

### 3.3 PriceAssist — inteligencia de precio para el vendedor (clave placement)
**Qué es:** herramienta gratis, exclusiva para members, en el flujo de venta; da insights en tiempo real del mayor marketplace AU "to make pricing your car easy". [VERIFICADO ≥2: búsqueda help PriceAssist]
**Campos atómicos (lo que muestra al vendedor):**
- **count** de coches como el tuyo **a la venta ahora** (oferta competidora) [VERIFICADO]
- **count** de coches como el tuyo **vendidos en los últimos 12 meses** [VERIFICADO]
- **comparación de precio** vs esos coches similares [VERIFICADO]
- **comparación de kilómetros** vs esos coches similares [VERIFICADO]
- **average time to sell** ("how long a car like yours takes to sell") [VERIFICADO]
- **recomendación de precio** "to suit your ideal time to sell" (trade-off precio↔velocidad) [VERIFICADO]

### 3.4 Instant Offer™ — venta instantánea C2Dealer
**Qué es:** oferta instantánea de un dealer acreditado; vende en hasta 24 h, pago al siguiente día hábil. "Powered by our exclusive pricing data". [VERIFICADO ≥2: instant-offer live + FAQ]
**Campos / parámetros atómicos:**
- **Input:** `Registration` (rego) + `State`; o **`Search by make/model`** (year/make/model/variant/odometer/condition vía "help-me-choose") [VERIFICADO: snapshot live + búsqueda FAQ]
- **Output:** valor de **Instant Offer** (oferta en efectivo de dealer) [VERIFICADO]
- **Validez:** **7 días** para aceptar [VERIFICADO ≥2: live + FAQ]
- **Claim de calidad de precio:** "**83% of Instant Offers are priced higher than a trade-in**" (basado en exclusive pricing data) [VERIFICADO: snapshot live]
- **Condicionalidad:** el precio se mantiene "as long as your car matches the description"; puede **ajustarse** (FAQ "Why might an Instant Offer be adjusted?") [VERIFICADO]
- **Flujo:** oferta (minutos) → inspección (concesionario o mobile/home en participantes) → pago siguiente día hábil; collection service (fee extra) [VERIFICADO ≥2: live + búsqueda]
- Basado en "**live market data from carsales' dealer network**" [VERIFICADO ≥2: búsqueda FAQ]

### 3.5 Vehicle History Report / CarFacts — historial (PPSR + mercado)
**Qué es:** informe de historial del vehículo. Consumer = "carsales vehicle history report" (carsales.com.au/facts); dealer = **CarFacts** (publicable vía AutoGate). [VERIFICADO ≥2: help vehicle-history-report + CarFacts business]
**Componentes / checks atómicos:**
- `PPSR Certificate` (Personal Property Securities Register; resumen en plain English) [VERIFICADO ≥2]
- `Finance Check` / financial encumbrances (money owing registrado) [VERIFICADO ≥2]
- `Written-Off Check` [VERIFICADO ≥2]
- `Stolen Check` [VERIFICADO ≥2]
- `Odometer Check` (rollback / discrepancias) [VERIFICADO: componentes CarFacts]
- `Registration Check` + `Registration Details` [VERIFICADO]
- `Warranty Check` [VERIFICADO]
- `Market Comparison` (powered by carsales — "Australia's largest source of car listing data"; pricing & market insights) [VERIFICADO ≥2]
- `Stock / listing activity` (actividad de anuncios) [VERIFICADO: título página /facts]
- `Vehicle Description` [VERIFICADO: componentes]
- `Expert reviews` (incluidos en el report de consumidor) [VERIFICADO]
- **Pricing Guide** dentro del report se **auto-actualiza 30 días** (resto de info persiste tras 30 días) [VERIFICADO ≥2: búsqueda /facts]

### 3.6 RedBook Inspect — inspección física pre-compra (filial)
**Qué es:** servicio de inspección móvil independiente, propiedad de carsales. Consumer (3 tiers) + Dealer (3 tipos). Alimenta el badge **carsales Approved**. [VERIFICADO ≥2: redbookinspect.com.au + business.carsales + búsqueda]
**Tiers consumidor:** `Lite` (motor + safety + tyres/wheels + test drive 2-3 km) · `Standard` (+ interior/exterior, damage repairs, test drive 3-5 km, post-inspection call, **carsales Car History Report** incluido) · `Ultimate` (+ video walkthrough HQ) [VERIFICADO ≥2: búsqueda]
**Checklist atómico (6 áreas, dealer):**
- `Engine fault codes` vía **scan tool** [VERIFICADO]
- `Exterior / underbody` (rust & repairs) [VERIFICADO]
- `Accident damage` con **paint depth gauge** [VERIFICADO]
- `Interior` (HVAC, belts, locks, lights) [VERIFICADO]
- `Road test` (brakes, noise, emissions, steering) [VERIFICADO]
- **Digital documentation** (photos, written-off history, stolen records) [VERIFICADO]
**Output:** `inspection rating` (estrellas, sobre 5) + report digital + (Ultimate) video [VERIFICADO]
**carsales Approved (auto-award):** min **4-star rating**, **< 160,000 km**, **< 10 años** → badge "blue shield" en la ficha, report visible gratis bajo pestaña **"Vehicle reports"** dentro de **"Car details"** [VERIFICADO ≥2: redbook-inspect business + help carsales-Approved]
**Tipos dealer + precio:** `Dealer Seller` (subscripción 3/6/12 meses, **$69 ex-GST/veh**, re-inspección **$40 ex-GST**) · `Dealer Buyer` (**$200/inspección**, sourcing nacional, remote) · `Dealer Pre-purchase` (referral, **$50/inspección completada** vía QR) [VERIFICADO ≥2: redbook-inspect business]

### 3.7 Research / Showroom — catálogo de coche nuevo + reviews + comparador
**Qué es:** hub de research del coche nuevo (specs, pricing, reviews, comparación). [VERIFICADO ≥2: research live + showroom snapshot]
**Campos / elementos:**
- `Expert review score` (numérico, **/100**; "Top rated cars by carsales' experts") [VERIFICADO: research live]
- `Specs & features` por modelo/variant (specs suministradas por RedBook) [VERIFICADO; lista completa en redbook.md]
- `RRP / pricing` del coche nuevo [VERIFICADO: showroom "Reviews, Specs & Pricing"]
- `Compare cars` (comparador lado a lado) [VERIFICADO]
- `Owner reviews` [VERIFICADO]
- `New car calendar` (fechas de lanzamiento de modelos próximos) [VERIFICADO]
- Navegación por `Lifestyle` (Electric, Family, Tradie, First car, Hybrid, Prestige, Performance, Offroad 4x4) · `Body type` (Hatch, SUV, Sedan, Ute, Wagon, Convertible, Coupe, Van) · `Makes` (200+) · `Price ranges` (Under $25k … Over $80k) [VERIFICADO ≥2: research + showroom snapshot]
- Certified pre-owned info [VERIFICADO]

### 3.8 Listing / ficha de vehículo (atributos del anuncio)
**Qué es:** datos mostrados en cada anuncio (search card + detail page). Specs ampliadas vienen de RedBook. [VERIFICADO ≥2: nav de filtros + redbook.md; detalle exacto de la ficha tras captcha]
**Campos atómicos (confirmados por filtros de búsqueda y cards):**
- `Price` (advertised) + **Price Indicator** (§3.2)
- `Year` (build year) · `Build date` / `Compliance date` / `First registration` (distinción explicada por carsales) [VERIFICADO ≥2: búsqueda]
- `Make`, `Model`, `Badge`/variant, `Series`
- `Body type`, `Transmission`, `Drive`
- `Engine size`, `Fuel type`
- `Odometer` / `Kilometres`
- `Colour`, `Seats`/`Doors`
- `Standard features` / equipment list
- `Fuel consumption`, `ANCAP safety rating` (vía specs RedBook) [VERIFICADO: redbook.md]
- `Location` / `State`
- `Seller type` (dealer / private)
- `carsales Approved` badge (si aplica)
- Pestañas de ficha: **"Car details"** (con sub-pestaña **"Vehicle reports"**), botón **"Check vehicle history"** [VERIFICADO ≥2: help carsales-Approved + vehicle-history]
- Estimación de financiación / repayments [NO-VERIFICADO — presente en la industria; no confirmado en ficha carsales por captcha]

### 3.9 LiveMarket — inteligencia de mercado para dealers (clave placement B2B)
**Qué es:** "real-time insights to help price confidently, track demand shifts, and optimise inventory with data from Australia's #1 auto website". Dentro de AutoGate. [VERIFICADO ≥2: LiveMarket product + búsqueda]
**Campos / métricas atómicas:**
- `Views` (shopper demand por listing) [VERIFICADO ≥2]
- `Leads` / enquiries (por listing) [VERIFICADO ≥2]
- `Demand indicators` / `demand shift` (cambios de demanda del consumidor) [VERIFICADO ≥2]
- `Days to sell` / time to sell ("how long it takes to sell") [VERIFICADO ≥2]
- `Competitive positioning` / price-to-market ("whether your listings are competitively positioned"; "how stock is priced in your area") [VERIFICADO ≥2]
- `Real-time pricing` vs similar listings + `historical data` [VERIFICADO ≥2]
- `Price adjustments` (histórico de cambios de precio) [VERIFICADO ≥2]
- `Last delisted price` (último precio anunciado antes de retirar) [VERIFICADO ≥2]
- `Delisted / sold data` (hasta **12 meses** atrás) [VERIFICADO ≥2]
- `Annual stock turns` (rotación de stock) [VERIFICADO]
- `Stock age` (antigüedad del stock) [VERIFICADO]
- `Competitor pricing` (precio/market performance de coches similares listados) [VERIFICADO]
- **Weekly reports:** `pricing opportunities` + `underperforming listings` [VERIFICADO ≥2]
- `Benchmarking` vs el mercado [VERIFICADO]

### 3.10 Acquire — sourcing de stock para dealers (LiveMarket package)
**Qué es:** módulo que cuelga LiveMarket data junto a cada listing para decisiones de compra/sourcing. [VERIFICADO ≥2: Acquire news]
**Campos / features atómicos:**
- **Find Opportunities** — filtros avanzados (powered by LiveMarket data + listing performance metrics) sobre **220,000+** coches de carsales [VERIFICADO ≥2]
- `LiveMarket data alongside each listing` (vehicle performance + pricing trends por unidad) [VERIFICADO]
- **Appraisal:** on-the-go via AutoGate app + **remote inspections** del cliente; **Rego ID lookup** [VERIFICADO]
- **Acquisition management:** tracking de oportunidades, customer data management, status updates, appraisal reports [VERIFICADO]
- **Analytics dashboard:** key metrics + team performance + trend tracking [VERIFICADO]

### 3.11 Capa IA (AutoGate) — asistencia a dealer
**Qué es:** features de IA (Google **Gemini**) sobre el flujo de leads/venta del dealer. [VERIFICADO ≥2: seller-experience-ai-tools]
**Campos / features:**
- `Call transcription & summaries` (transcripción timestamped + searchable; resalta `buyer signals`: vehicle preferences, next steps) [VERIFICADO]
- `Lead prioritization` (highlight de leads con mayor probabilidad de convertir, por señales real-time) [VERIFICADO]
- `Intent detection` (flag de hot leads por patrones de comunicación) [VERIFICADO]
- `Contextual buyer summary` (vista unificada: past listings, pricing preferences, calls, email engagement) [VERIFICADO]
- `Offer creation support` (recomendaciones data-backed con **live market data + stock performance + buyer behavior**) [VERIFICADO]
- `Admin automation` (scheduling, document handling, deal progression) + `AI-guided re-engagement` (follow-ups por lifecycle stage) [VERIFICADO]

### 3.12 carsales mediahouse — publicidad + datos de audiencia (OEM/marcas)
**Qué es:** brazo de medios; vende audiencia y atribución a OEM, marcas y agencias. [VERIFICADO ≥2: mediahouse/solutions]
**Productos / capas de dato atómicas:**
- **Ignition** (self-serve: "real-time category-based insights to plan, buy and measure digital campaigns") [VERIFICADO]
- **Fuse** (managed, insight-led, auto y no-auto) [VERIFICADO]
- **carsales XT** (off-network: programmatic, social, paid search) [VERIFICADO]
- **carsales ID** (people-based targeting con rich behavioural data) [VERIFICADO]
- **carsales match** (partnership Adobe: first-party match + lookalike modeling) [VERIFICADO]
- **carsales CAPI** (privacy-compliant: campaign attribution, optimisation, advanced audience targeting) [VERIFICADO]
- **Audiencias / señales atómicas:** stage of buying journey · Auto Interest segmentation · socio-demographic profiles · intent-based audiences · Finance & Insurance targeting · interest-based categories [VERIFICADO]
- **Formatos creativos:** Homepage Buyout, Unmissable, Brand Terms (Standard/Premium), Video, Partnerships, Branded Content, Model Showcase; intent (Display, Native, Link Ads); Direct Response (1st-party data) [VERIFICADO]

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Fuente primaria (foso) | **El propio marketplace carsales** — el mayor de AU: precios anunciados **live** + **delisted/sold** (hasta 12 meses), views, leads, days-to-sell, stock turn. Dato propietario y exclusivo. | [VERIFICADO ≥2: LiveMarket + Instant Offer] |
| Valoración | **RedBook** (filial) — specs + valoración + RTV alimentan Car Valuation, Price Indicator y los reports; RedBook a su vez se nutre del feed carsales (bucle de datos del grupo) | [VERIFICADO ≥2: "Supported by RedBook" + redbook.md] |
| Price Indicator | comparación contra coches **similares recientemente anunciados** (no necesariamente precio final de venta) usando 10 atributos | [VERIFICADO ≥2: modal] |
| PriceAssist / LiveMarket | agregados de anuncios activos + vendidos (12m) de la red | [VERIFICADO ≥2] |
| Instant Offer | "live market data from carsales' dealer network" + exclusive pricing data | [VERIFICADO ≥2] |
| Historial (CarFacts) | **PPSR** (registro nacional de gravámenes/written-off/stolen) + datos de mercado carsales + government sources | [VERIFICADO ≥2] |
| Inspección | inspección física por inspector (scan tool, paint depth gauge, road test) | [VERIFICADO ≥2: redbook-inspect] |
| IA | **Google Gemini** para transcripción/summaries; modelos propios para lead scoring y recomendación de oferta | [VERIFICADO: seller-experience-ai-tools] |
| Audiencia (mediahouse) | first-party behavioural data de la red (3.7B+ signals), partnership Adobe para match | [VERIFICADO] |

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Web marketplace (consumer)** | carsales.com.au + apps iOS/Android; herramientas Value my car, Instant Offer, Check vehicle history sobre la web | [VERIFICADO ≥2: live + footer app links] |
| **Plataforma dealer — AutoGate / Ignition** | "inventory and enquiry management system"; aloja LiveMarket, Acquire, CarFacts publishing, IA; help.autogate.co; integrations.autogate.co | [VERIFICADO ≥2: business.carsales + autogate.co] |
| **App AutoGate** | appraisals on-the-go, remote inspections, gestión de leads | [VERIFICADO: Acquire] |
| **Integraciones / DMS** | vía integrations.autogate.co (3rd-party) | [VERIFICADO: business.carsales nav] |
| **Reports** | CarFacts (print / email al cliente; publish auto o manual) ; RedBook Inspect report digital + video | [VERIFICADO ≥2] |
| **Badges sobre la ficha** | Price Indicator, carsales Approved (blue shield), pestaña Vehicle reports | [VERIFICADO ≥2] |
| **mediahouse** | self-serve (Ignition) + managed (Fuse) + off-network (carsales XT); ad-specs publicadas | [VERIFICADO ≥2] |
| **RedBook (B2B)** | API REST + secure FTP + portal Fleetmaster (canal del dato de valoración/specs) | [VERIFICADO: redbook.md] |

---

## 6. Precio

| Aspecto | Detalle | Estado |
|---|---|---|
| **Valoración consumidor** | **Gratis** (Car Valuation, Price Indicator, PriceAssist, Instant Offer) | [VERIFICADO ≥2] |
| **Vehicle History Report (consumidor)** | **AU$34** single; **3 reports = AU$49**; **5 reports = AU$59**; auto-update pricing 30 días, refresh con crédito | [VERIFICADO ≥2: búsqueda /facts] |
| **RedBook Inspect (consumidor)** | 3 tiers Lite/Standard/Ultimate (precio escalonado; no publicado exacto en esta auditoría) | [VERIFICADO tiers; precios consumer NO-VERIFICADO al detalle] |
| **RedBook Inspect (dealer)** | Seller **$69 ex-GST/veh** (+ re-inspección **$40**), Buyer **$200**, Pre-purchase referral **$50** | [VERIFICADO ≥2] |
| **Dealer advertising — subscripción mensual** (veh $1-$69,999, por nº de items) | 0-20: **$2,306** (incl. Promote Automation Budget $1,220) · 21-61: **$2,719** ($1,830) · 61-150: **$3,207** ($2,440) · 150+: **$3,721** ($3,050) | [VERIFICADO: búsqueda help "How much does an ad cost"] |
| **Dealer — pay per enquiry** | el dealer paga por cada enquiry recibida en un item; incluye AutoGate licence, lead mgmt, account mgmt, help desk | [VERIFICADO ≥2] |
| **Promote** | prioriza el listing en resultados; budget de automatización incluido en tiers | [VERIFICADO ≥2] |
| **Sales Event Packages** | bespoke (combinación de productos a medida de campaña) | [VERIFICADO] |
| **Cancelación dealer** | 30 días de aviso por escrito | [VERIFICADO] |
| **mediahouse** | quote-based / por campaña (CPM/programmatic); no published rate-card | [VERIFICADO: estructura; tarifa NO-VERIFICADA] |

---

## 7. Placement (patrón web a copiar por cardeep)

> Cómo carsales **coloca cada dato en su UI**. Es el blueprint directo para cardeep: dato de mercado **pegado al anuncio** y al **flujo de venta**.

| Dato | Dónde lo coloca carsales |
|---|---|
| **Navegación raíz** | Top-nav fija: **Buy** · **Sell** · **Research** · **Showroom** · **Value my car** + CTAs "Sell my car" / "Sign up-Log in" |
| **Indicador de precio** | **Badge sobre la ficha/anuncio** (search card + detail): `Around / Below / Well Below Market Price`, con modal explicativo (10 atributos, exclusiones) accesible desde el badge |
| **Valoración** | Página dedicada **/car-valuations** con selector de **modo** (selling/buying/trading-in) arriba, luego form `Make→Model→…`; logo "Supported by RedBook"; tarjetas "Driven by data / Tailored / No strings" + CTA a Instant Offer y a "Advertise" |
| **PriceAssist (vendedor)** | **Dentro del flujo de venta** (members): panel con count de coches similares (a la venta / vendidos 12m), comparación precio+km, **average time to sell**, y **slider/recomendación precio↔velocidad** |
| **Instant Offer** | Página **/instant-offer**: form mínimo (`Rego + State`) arriba; "How it works" en 3 pasos; bloque "Trusted — 83% priced higher than a trade-in"; cross-sell a "Advertise" (precio más alto) y "Free valuation" (vender luego) |
| **Specs del vehículo** | En la **ficha detail** (pestañas "Car details" / specs), y en **Research/Showroom** para coche nuevo (categorías Lifestyle/Body/Makes); specs por RedBook |
| **Historial** | Botón **"Check vehicle history"** en la ficha → report (PPSR + finance + written-off + stolen + odometer + registration + warranty + **Market Comparison**) |
| **Inspección / confianza** | **Badge "carsales Approved" (blue shield)** en la ficha + report bajo pestaña **"Vehicle reports"** dentro de **"Car details"** (gratis de ver) |
| **Reviews / comparación nuevo** | **Showroom/Research**: score **/100** de experto, owner reviews, **Compare cars**, new car calendar, filtros por lifestyle/body/price |
| **Inteligencia dealer (LiveMarket)** | **Dashboard dentro de AutoGate**: por listing → views, leads, days-to-sell, price-to-market vs similares, price adjustments, last delisted price; **weekly report** de pricing opportunities + underperforming listings; benchmarking |
| **Sourcing dealer (Acquire)** | **LiveMarket data junto a cada listing** + pantalla **Find Opportunities** (filtros sobre 220k+ coches) + analytics dashboard de team performance |
| **IA dealer** | Sobre la **ficha de lead/cliente** en AutoGate: transcripción de llamada, lead score, buyer summary, **offer creation support** (recomendación de precio data-backed) |
| **Audiencia OEM (mediahouse)** | Portal self-serve **Ignition** (insights por categoría) + dashboards de campaña (attribution vía CAPI) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Foso de dato de origen (no derivado):** carsales **genera** el dato de mercado AU (mayor marketplace), no lo compra. Precios live + delisted (12m), views, leads, days-to-sell son propietarios — la base que RedBook y todos consumen.
2. **Bucle de datos del grupo:** carsales (transacción/anuncio) ↔ RedBook (valoración/specs) ↔ Encar/webmotors/Trader Interactive (otros mercados). Pocos competidores tienen marketplace + casa de valoración + inspección bajo el mismo techo.
3. **Price Indicator pegado a la ficha** (Around/Below/Well Below Market) — placement consumidor exacto que cardeep imitará.
4. **PriceAssist con trade-off precio↔velocidad** (cuántos similares, cuánto tardan en venderse, precio recomendado por objetivo de tiempo) — inteligencia de venta para el particular, rara fuera de Auto Trader UK.
5. **Instant Offer C2Dealer** con red de dealers acreditados + claim "83% > trade-in".
6. **LiveMarket** entrega `last delisted price` + `price adjustments` + `stock turn`/`stock age` por unidad — granularidad de days-supply/price-to-market nativa del marketplace.
7. **Vertical multi-activo** (coche, moto, barco, caravana, camión, construcción, maquinaria agrícola, neumáticos) bajo una sola red.
8. **mediahouse** con `carsales ID` + `carsales match` (Adobe) + `CAPI`: monetiza la audiencia/intención de compra como dato publicitario — capa que las casas de valoración puras no tienen.
9. **Capa IA (Gemini)** integrada en el CRM del dealer (transcripción, lead scoring, offer support).
10. **carsales Approved + RedBook Inspect** cierran el ciclo confianza (inspección física → badge en la ficha).

---

## 9. Gaps (lo que NO ofrece / debilidades para cardeep)

1. **Geografía:** esta marca es **solo Australia**. El grupo cubre KR/US/CL/BR con **otras marcas** (Encar, Trader Interactive, chileautos, webmotors), no carsales. **Cero Europa / España** bajo carsales. Irrelevante directamente para el censo ES de cardeep salvo como patrón.
2. **No es censo de puntos de venta:** carsales lista **inventario y dealers que pagan por anunciarse**, no un **censo exhaustivo de la huella digital de todos los puntos de venta** (territorio propio de cardeep). No cataloga la presencia online (web/RRSS) de cada dealer como entidad.
3. **No vende el dato crudo de mercado en abierto:** LiveMarket/Acquire viven **tras login AutoGate** (dealer); no hay API pública del índice de precios ni feed abierto de days-to-sell/price-to-market. No hay self-serve público del dato B2B.
4. **Price Indicator con huecos declarados:** ignora condición real, extras, ubicación, certificación; excluye coches **<$5k / >$70k** y **<2 / >15 años** y los de hail/written-off → no cubre el extremo barato, premium ni clásico.
5. **Valoración = RedBook:** el motor fino (RTV, residual forecast, 800+ specs, NEVDIS, factory options por VIN) es **producto RedBook**, no carsales; carsales expone una capa de consumidor simplificada.
6. **History acotado a AU:** CarFacts/PPSR es nacional australiano (written-off/stolen/finance/odometer/registration) — no es CARFAX-style con histórico de siniestros/servicio profundo internacional.
7. **Especificación tras paywall/captcha:** las fichas de detalle están protegidas (DataDome); el schema fino del listing y el output exacto de la valoración no son scrapeables abiertamente.
8. **Sin telemática / uso real / comportamiento de conductor.**
9. **"Australia's Car Buyer Report"** existe como market research publicado, pero su contenido/metrics **no verificado** en esta auditoría (la búsqueda devolvió estudios de Cox US homónimos, **no** atribuibles a carsales). [NO-VERIFICADO]
10. **Estimación de financiación en la ficha:** estándar de industria pero **no confirmada** en carsales por el captcha. [NO-VERIFICADO]

---

## 10. Fuentes (URLs)

**Consumidor (verificado live con navegador — DataDome en detail pages):**
- https://www.carsales.com.au/ (home; title/posicionamiento)
- https://www.carsales.com.au/car-valuations/ (Value my car — 3 modos, Supported by RedBook) [snapshot Playwright 2026-06-30]
- https://www.carsales.com.au/instant-offer/ (Instant Offer — rego+state, 7 días, 83%>trade-in) [snapshot Playwright]
- https://www.carsales.com.au/cars/ · /cars/used/ (marketplace + filtros: transmission/body/make)
- https://www.carsales.com.au/research/ · https://www.carsales.com.au/research/showroom/ (405 modelos/64 makes, score /100, compare) [snapshot Playwright]
- https://www.carsales.com.au/facts (vehicle history report — pricing/stock/history)

**Price Indicator / PriceAssist (placement consumidor):**
- https://help.carsales.com.au/hc/en-gb/articles/360015482932-carsales-Price-Indicators-FAQs
- https://resource.csnstatic.com/retail/price-indicator/info-modal-v3.html · v5.html (10 atributos, exclusiones, tiers)
- https://help.carsales.com.au/hc/en-gb/articles/204556705-Price-Assist
- https://help.carsales.com.au/hc/en-gb/articles/45164559713945-Pricing-insights-FAQ
- https://www.carsales.com.au/editorial/details/carsales-price-indicator-gives-car-buyers-confidence-115213/

**Historial / inspección:**
- https://help.carsales.com.au/hc/en-gb/articles/204556695-Vehicle-history-report
- https://business.carsales.com.au/dealer-tools-and-solutions/carfacts-history-reports/ (componentes CarFacts)
- https://business.carsales.com.au/products/car-dealers/carfacts-vehicle-history-reports/
- https://www.redbookinspect.com.au/ · /prepurchase/car (3 tiers + checklist)
- https://business.carsales.com.au/dealer-tools-and-solutions/redbook-inspect/ (dealer: precios $69/$200/$50 + criterios Approved)
- https://help.carsales.com.au/hc/en-gb/articles/4405798479001-What-is-carsales-Approved (badge + Vehicle reports tab)

**Dealer / LiveMarket / Acquire / IA / pricing:**
- https://business.carsales.com.au/dealer-tools-and-solutions/livemarket/ (métricas LiveMarket)
- https://help.datamotive.com.au/hc/en-gb/articles/360020895771-What-is-LiveMarket
- https://business.carsales.com.au/news-room/news/introducing-acquire-livemarket-package/ (Acquire — Find Opportunities, 220k cars)
- https://business.carsales.com.au/news-room/national-odometer-day-pricing-livemarket/
- https://business.carsales.com.au/news-room/tips-insights/seller-experience-ai-tools/ (IA Gemini, lead scoring, offer support)
- https://help.carsales.com.au/hc/en-gb/articles/34235710344217-How-much-does-an-ad-cost (tiers $2,306-$3,721 + pay-per-enquiry)
- https://business.carsales.com.au/products/car-dealers/sales-event-packages/ · /display-advertising/
- https://autogate.co/ (plataforma dealer "1999-2024")

**OEM / mediahouse:**
- https://mediahouse.carsales.com.au/ · /solutions (Ignition, Fuse, carsales XT, carsales ID, match, CAPI; 15.2M members / 3.7B signals)

**Insights / market:**
- https://business.carsales.com.au/insights/automotive/ (Car Buyer Report 2026; 8.9M/16M/10M+/88M)
- https://business.carsales.com.au/news-room/redbook-insider/redbook-auto-market-insight-dashboard/ (dashboard mensual: sales volumes, fuel-type breakdown, pricing trends, BEV) — producto RedBook
- https://business.carsales.com.au/news-room/redbook-insider/introducing-redbook-live-vehicle-intelligence-and-insights/

**Corporativo:**
- https://en.wikipedia.org/wiki/CAR_Group · https://en.wikipedia.org/wiki/Carsales
- https://cargroup.com/ (investor) · https://shareholder.carsales.com.au/
- Footer carsales.com.au (verticales + international marketplaces + "© carsales.com.au Pty Ltd 1999-2026")

> **Marcas [NO-VERIFICADO] / inferencias:** contenido/metrics del "Australia's Car Buyer Report" (búsqueda devolvió Cox US homónimo, no atribuible); output exacto del flujo de Car Valuation y pasos posteriores a Make/Model; estimación de financiación en la ficha; precios consumidor exactos de RedBook Inspect; existencia de tiers de display ad tipo "Spotlight/Premier" (esos son de Autotrader US, NO confirmados en carsales). Specs finos de la ficha = espejo de RedBook (ver redbook.md). Todo lo [VERIFICADO ≥2] tiene doble fuente; el resto, fuente única declarada.
