# Auditoría atómica — iSeeCars (iSeeCars.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos e inteligencia de automoción B2C-first**: motor de búsqueda agregador de anuncios de coche (nuevo + usado) sobre ~75% de los listings de EE.UU., con un **algoritmo propietario de "deal rating"** que puntúa cada anuncio por precio vs. mercado, calidad del coche y reputación del concesionario. Vende valoración (Price My Car), informes por VIN (iVIN) por suscripción, y es una **fábrica de estudios de mercado** (depreciación, longevidad, days-to-sell, best-time-to-buy) que aliment la prensa nacional. Web (producto del scope): https://www.iseecars.com/.
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **market-intelligence**. **NO es un host DNS**: `market-intelligence.iseecars.com`, `data.iseecars.com`, `api.iseecars.com`, `insights.iseecars.com` → **NXDOMAIN verificado** (nslookup). Es una etiqueta de categoría, no un subdominio real.
> Fecha auditoría: 2026-06-30. Método: navegación de iseecars.com (home, about-us, research, /research/studies, vin, subscription-vin-plans, price-used-cars, página de listings used-honda-accord, estudios cars-that-hold-their-value / longest-lasting-cars / fastest-selling-cars / best-times-to-buy / how-much-is-my-car-worth) + verificación cruzada con Wikipedia, Grokipedia (403), highperformr, Dealroom, Crunchbase, PitchBook, Tracxn, ZoomInfo, Growjo, Apollo, prensa (ABC News, CBS, CNBC, Consumer Reports).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **iSeeCars** / **iSeeCars.com** | [V] |
| Razón social | **iSeeCars.com, Inc.** (privada) | [V] |
| Categoría | **Motor de búsqueda + research engine de automoción B2C** con scoring algorítmico de anuncios ("deal rating"), valoración de coche, informes por VIN (iVIN) y publicación de estudios de mercado. No es una guía editorial de valores (tipo KBB/Black Book) ni un API-provider de datos en bruto (tipo MarketCheck). Se autodefine como **"the Kayak.com for people in the market to buy a car"**. | [V] |
| Fundación | **Lanzamiento público 23-oct-2013** (Wikipedia). Idea concebida en **2008** (Phong Ly, tras 3 meses comprando un BMW 530i de 2003). Algunas BBDD citan **incorporación 2011** (Dealroom). | [V — con variación, ver Gaps] |
| HQ | **Woburn, Massachusetts, EE.UU.** (área de Boston); dirección citada **400 West Cummings Park, Ste 2950, Woburn, MA** | [V — Wikipedia + highperformr + Dealroom] |
| Propiedad | **Privada, bootstrapped — sin financiación externa conocida** ("has not raised any funding", Dealroom; sin rondas en Crunchbase/PitchBook) | [V] |
| Grupo matriz | **Ninguno** (independiente; no pertenece a Cox/J.D. Power/CDK ni similares) | [V] |
| Fundadores | **Phong Ly** y **Vineet Manohar** | [V] |
| Liderazgo | **Phong Ly — CEO & Co-founder** (ex-marketing SAP, MBA Harvard Business School). **Vineet Manohar — CTO & Co-founder** (ex-ingeniero TripAdvisor / Big Data, graduado IIT - Indian Institute of Technology). | [V — highperformr + ZoomInfo + Adapt] |
| Analistas / portavoces | **Karl Brauer — Executive Analyst** (analista de automoción reconocido; voz pública de los estudios). **Julie Blackley — Communications Manager / Executive Analyst**. | [V — Apollo + highperformr + prensa] |
| Empleados | **Equipo pequeño**: 2-10 (Dealroom), ~8 (a 31-dic-2021), ~9 (Growjo). **[A]** Probable infraestima de agregadores; una operación que analiza 10M+ listings/día se apoya fuertemente en automatización/infra. | [V — cifra de 3os, baja confianza, ver Gaps] |
| Facturación | **~$630k/año estimado** (Growjo, estimación de 3os) — **no divulgada oficialmente**; cifra de baja fiabilidad. | [A — estimación 3os] |
| Apps | **"Used Car Search Pro – iSeeCars"** en **iOS (App Store)** y **Android (Google Play)** con escaneo de **código de barras VIN**. | [V] |
| Partnerships | **eBay, Chrome Data** (decode/specs) y **múltiples concesionarios** (sindicación de inventario); integración opcional **CARFAX** en iVIN Pro. | [V — Wikipedia] |

### Hitos / cronología [V]
- **2008** Phong Ly concibe la idea tras una compra de coche usado frustrante (BMW 530i 2003, 3 meses de research).
- **~2011** Incorporación (según Dealroom).
- **23-oct-2013** Lanzamiento público de iSeeCars.com (motor de búsqueda + deal rating).
- **2013-2014** Primeros estudios virales (mejor momento para comprar; coches que llegan a 200k millas; Tesla usados que valen más que nuevos) recogidos por Consumer Reports, CNBC, CBS.
- **2014-2015** Finalista **MITX What's Next Awards**; **Webby Awards Honoree** (Car Sites & Culture).
- **2020s** Karl Brauer entra como Executive Analyst; los estudios (depreciación, longevidad, EV) se convierten en referencia recurrente de prensa (WIRED, WSJ, USA Today, Forbes).

### Clientes objetivo (segmentos) [V/A]
1. **Compradores de coche usado/nuevo** (núcleo B2C — el motor de búsqueda y el deal rating). [V]
2. **Vendedores particulares** (herramienta Price My Car / Price Your Used Car). [V]
3. **Compradores/vendedores que quieren due-diligence por VIN** (iVIN, suscripción). [V]
4. **Concesionarios** (sindican su inventario al motor; reciben leads/tráfico; aparecen en el Dealer Scorecard). [V — modelo lead-gen]
5. **Prensa / medios / analistas** (estudios syndicated; cita "según iSeeCars"). [V]
6. **[A]** Licenciatarios de datos / B2B research (la data alimenta estudios licenciables, pero no hay un producto API público autoservicio como el de MarketCheck).

---

## 2. Cobertura

### Geográfica [V]
- **Estados Unidos exclusivamente.** No hay cobertura de Canadá, UK ni Europa. El motor opera por **ZIP + radio** dentro de EE.UU.

### Escala (cifras divulgadas — varias vintages, ver Gaps) [V]
- **4 millones+** de coches en venta indexados en vivo (home / "largest online car search engine"). [V]
- **25.000 millones (25B+) de data points** ("and growing", about-us). [V]
- Analiza **>75% de todos los anuncios de coche usado de EE.UU.**; **10 millones+ de listings procesados a diario** (about-us). [V]
- **30 millones+ de anuncios** en la base usada para estudios (Wikipedia, cifra más antigua). [V]
- Estudios puntuales sobre datasets enormes: **~400 millones de coches** (longevidad), **950.000-960.000** coches de 1-5 años (depreciación / fastest-selling), **40 millones+** de ventas 2024-2025 (best-time-to-buy). [V]
- Contador de ahorro agregado al consumidor mostrado en web: **$449.672.974** (home, 2026); "**over $60 million** since launch" (about-us, cifra antigua). [V — vintages distintas]

### Scope de vehículos [V]
- **Coches nuevos + usados + certificados (CPO)** y **venta por particular** ("Cars for sale by owner"). El núcleo y la mayoría de herramientas son **usado**.
- Segmentos cubiertos en rankings: SUV (small/midsize/luxury/3-row/7-seater/crossover), trucks (midsize/full-size/heavy-duty), sedans, small cars, hatchbacks, wagons, minivans, sports cars, convertibles, coupes, EV, híbridos, PHEV.
- **Sin** RVs, motocicletas, comercial pesado ni maquinaria (a diferencia de MarketCheck US).

---

## 3. Productos + campos atómicos

Arquitectura **producto web + apps**, no API-first. Cinco bloques: (A) Motor de búsqueda + Deal Rating, (B) Price My Car (valoración), (C) iVIN (informes por VIN, suscripción), (D) VIN Check gratuito + Window Sticker/Build Sheet, (E) Research/Studies (la "market intelligence" pública).

### — BLOQUE A: MOTOR DE BÚSQUEDA + DEAL RATING —

### 3.1 Used/New Car Search Engine + Deal Rating [V]
Buscador agregado sobre 4M+ coches; cada anuncio recibe un **rating algorítmico** y métricas propias. **Campos por anuncio (tarjeta de resultado):**
- **Deal rating badge**: **"Great Deal" / "Good Deal" / "Fair Deal" (Fair Value)** / **"Overpriced"/above market value**. (Filtro equivalente: **iSeeCars Price Rating** = Great/Good/Fair Value.)
- `price` (precio anunciado, grande/bold).
- `heading` = `year` + `make` + `model` + `trim`.
- `mileage` (ej. "77,443 Miles").
- `location` (city, state).
- **`remaining_lifespan`** — **métrica-firma**: años de vida útil restante estimada del coche (ej. "7.28 yrs"); derivada del modelo de longevidad (§3.13).
- **`savings_vs_market`** — "**$4,680 Below market value of $17,679**" (ahorro absoluto + valor de mercado estimado de referencia).
- `market_value` (valor de mercado estimado para ese coche).
- `days_listed` / days on market — "Listed 34 days ago".
- **`dealer_score`** (1-5 estrellas; §3.4).
- `photo` (imagen del vehículo).
- **Price drop indicator** (bajada de precio) [A — patrón estándar del sector, visible vía sort/keywords].

**Campos del detalle (expandible / VDP):** `engine` (4-cyl/6-cyl), `fuel_type`, `seating_capacity`/`seats`, `vin`, `features`/`options` (Bluetooth, backup camera, leather, 360 camera, Apple CarPlay, Android Auto, navigation, panoramic sunroof, adaptive cruise…), `transmission`, `exterior_color`, `interior_color`, `mpg` (combined; city/highway), `drivetrain` (FWD/AWD/4x4), `doors`.

**Filtros del buscador (sidebar) — granularidad atómica:** ZIP + radius · price range · make/model/year/trim · mileage · **condition (Used/New/Certified Used)** · body style · **market segment** · **iSeeCars Price Rating (Great/Good/Fair Value)** · **Remaining Lifespan** · **Dealer Score (1-5★)** · **Amount Below Market Price** · transmission · drivetrain · cylinders · horsepower · fuel type · exterior/interior colors · popular features (360 cam, CarPlay…) · listing details (**one owner**, photos availability) · seats · doors · **leg room / head room** · **cargo room** · **towing capacity** · vehicle size · MPG · **seller type (Owner/Dealer)** · keywords.

**Orden de resultados (sort):** Best Match · **Most Remaining Lifespan** · Price (low-high) · Mileage · Model Year · Date Listed · Distance.

### — BLOQUE B: VALORACIÓN —

### 3.2 Price My Car / "Price Your Used Car" (`/price-used-cars`) [V]
Herramienta de valoración para **vendedores**. **Inputs:** `VIN` **o** manual (`make`, `model`, `year`, `trim`, `cab type`, `style`, `mileage`, `zip`). **Outputs:**
- **`average_market_price`** (precio medio de comparables locales).
- **`price_range`** (rango con % de listings dentro de una desviación estándar).
- **Recomendaciones de precio de venta por urgencia**: **"In a Rush to Sell?"** (venta rápida) y **"Want to Make More Money?"** (máximo beneficio) — cada una con comparación vs. precio de mercado y **% de coches similares con precio superior**.
- **`demand_indicator`** (nivel de demanda relativo por cada tier de precio).
- **Gráfico comparativo interactivo**: tu coche vs. similares en venta, con la línea de **precio de mercado** como referencia.
- **Histórico 12 meses**: valor medio mensual del modelo.
- **Curva de depreciación por model-year**.

### 3.3 Tipos de valor definidos (`how-much-is-my-car-worth`) [V]
- **Market Value (= Private Party Value)**: lo que recibirías vendiendo a un particular.
- **Trade-In Value**: lo que un concesionario te ofrece por tu coche.
- **Retail Value**: lo que un comprador pagaría en concesionario.
- **Instant Cash Offer**: oferta de cash con validez limitada (7 días) de dealers online (Carvana, CarMax).
- **Factores de la valoración**: year, make, model, trim, style · mileage · vehicle condition · features/optional equipment · precios de comparables locales · **supply & demand** · location.

### 3.4 Dealer Scorecard [V]
Rating **propietario, independiente, 1-5 estrellas** de cada concesionario, sobre **3 criterios**:
- **Price competitiveness** — cuán competitivo es en pricing de usado.
- **Information transparency** — cuánto divulga (fotos, precio, kilometraje).
- **Responsiveness** — rapidez respondiendo a preguntas de shoppers.
Se compara cada dealer contra el resto; entra como factor en el deal rating global.

### — BLOQUE C: INFORMES POR VIN (iVIN, suscripción) —

### 3.5 iVIN Data Report — informe completo por VIN [V]
Informe de due-diligence por VIN (de pago, ver §6). **Secciones/campos:**
- **Market value price analysis** (valor de mercado justo local).
- **Vehicle condition analysis** (comparación de millas medias vs. su edad).
- **Similar cars comparison** (precio, kilometraje, market value de comparables).
- **Market demand & supply** (oferta/demanda del modelo).
- **Selling history** (cambios de precio, anuncios previos — historial del propio anuncio).
- **Dealer scorecard** (rating del vendedor).
- **Multi-year depreciation analysis** (depreciación estimada — típicamente 5 años forward).
- **Best time to buy / best time to sell** (recomendación temporal).
- **Title / lien information** (datos de título y gravamen, provistos por **DMV**).
- **Accident check** (historial de siniestros).
- **Production serial numbers & specifications**.
- **Standard & optional features**.
- **Safety ratings**.
- **Open recall check** (recalls abiertos y pasados).
- **Consumer complaints**.
- **Theft / stolen check** (base **NICB** — National Insurance Crime Bureau).
- **Window sticker information**.
- **Local market reports by ZIP & by vehicle** (solo iVIN Pro).
- **CARFAX report integration** (Pro; requiere suscripción CARFAX aparte).

### — BLOQUE D: VIN CHECK GRATIS + WINDOW STICKER / BUILD SHEET —

### 3.6 Free VIN Check & Decoder (`/vin`) [V]
Versión gratuita. Devuelve: **VIN decode + specs**, **vehicle features**, **recall check (abiertos + pasados)**, **theft/stolen record (NICB)**. (El resto de campos de §3.5 quedan tras el paywall iVIN.)

### 3.7 Window Sticker & Build Sheet lookup [V]
Herramientas de recuperación de la **etiqueta original (Monroney/window sticker)** y la **build sheet de fábrica** por VIN: MSRP original, opciones/packages de fábrica, equipamiento estándar, economía de combustible, datos de build. (Guías: Window Sticker vs Build Sheet; "5 Best Free Window Sticker Lookup Tools".)

### 3.8 Car Finder / Comparison [V]
- **Car Finder**: descubrimiento por criterios/uso.
- **Comparador** de coches (side-by-side de specs/precio).

### — BLOQUE E: RESEARCH / STUDIES (la "market intelligence" pública) —

iSeeCars **publica continuamente estudios data-driven** (la cara visible de su inteligencia de mercado). Métricas atómicas por estudio:

### 3.9 Cars That Hold Their Value (depreciación) [V]
Métrica: **% de depreciación a 5 años** (vs. MSRP **ajustado a inflación 2026 con datos del US Bureau of Labor Statistics**) + **$ de diferencia respecto al MSRP** + `segment`. Muestra: **>950.000** coches de 5 años vendidos **mar-2025 → feb-2026**. Media global 2026: **41,8% / $16.571**. Tabla: Rank · Model · Segment · Avg 5-Year Depreciation (%) · Avg $ Difference from MSRP.

### 3.10 Longest-Lasting Cars (longevidad) — base de "Remaining Lifespan" [V]
Métrica: **% de probabilidad de alcanzar 250.000 millas** (no años) + **multiplicador vs. media 4,8%**. Muestra: **~400 millones** de coches; modelo propietario sobre el odómetro medio por edad anual. Ej.: Toyota Sequoia #1 con **39,1%** (8,1× la media). Esta es la fuente del campo **`remaining_lifespan`** mostrado en cada anuncio (§3.1).

### 3.11 Fastest-Selling Cars (velocidad de venta) [V]
Métrica: **Days on Market (DOM)** medio por make/model. Muestra: **>960.000** ventas de coches de 1-5 años, **feb-2026**. Media global usado: **53,0 días**. Rango ejemplo: Tesla Model X **22,6 días** (más rápido) → Volvo XC60 híbrido **170,2 días** (3,21× la media). Tabla: Rank · Model · Days on Market · Compared to Average (multiplicador).

### 3.12 Best & Worst Times to Buy (índice de deals) [V]
Métrica: **disponibilidad de deals como % por encima/debajo de la media** por mes y por festivo. Un "deal" = anuncio **≥10% por debajo** del fair market value de iSeeCars. Muestra: **40M+** ventas 2024-2025. Hallazgos: Nov +38,4% / Dic +38,2% / Ene +19,9% / Oct +16,7% / Feb +4,8% (mejores); Jun −22,8%, May −28,3% (peores); MLK Day +65,5% (mejor festivo).

### 3.13 Catálogo de estudios y rankings adicionales [V]
- **Most Reliable** (cars/used/brands; rating de fiabilidad).
- **Best Used Cars for the Money** (valor para coches de 5 y 10 años).
- **Most Popular Used Cars** (ranking de ventas por **city y state**).
- **Used Hybrid Demand** (+41,8% reportado), **EV Market / EV depreciation**.
- **Car Recall Study** (frecuencia de recalls por marca).
- **Rising Gas Prices** (impacto de coste por estado / tipo de vehículo; +$706 citado).
- **Most/Least-Driven Cars** (millaje anual: híbrido vs EV vs gasolina).
- **Most Popular Car Colors** (cuota por color).
- **Cars to Buy New Over Used**.
- **Rankings 2026** por categoría y por precio: Best/Best-Used SUVs, trucks, EV, hybrid, luxury, family, for moms, for teens · Safest · Best Gas Mileage / MPG · Best Resale Value (brands + cars) · Most Affordable / Cheapest brands · Best for the Money · Performance / Turbo / Supercharged · AWD / 4x4 · Best Towing · Longest Range EV · Most Cargo Space · Most Horsepower · Off-Road · For Snow · Most Comfortable · For Tall People / Most Legroom · Manual / CVT · Trucks with Longest Beds · por feature (CarPlay, Android Auto, panoramic sunroof, adaptive cruise, navigation) · por país de origen (American/German/Japanese/Korean).

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = agregación/scraping de anuncios + scoring algorítmico, NO panel editorial ni transaccional**: rastrea los anuncios de coche de EE.UU. (>75% del usado) y los normaliza.
- **Fuentes**: webs de concesionario y marketplaces sindicados (incl. **eBay**); **Chrome Data** para decode/specs; **DMV** (título/lien en iVIN); **NICB** (robo); **CARFAX** (opcional, Pro); **US BLS** (ajuste de inflación en el estudio de depreciación). [V]
- **Volumen**: **10M+ listings/día**, **25B+ data points**, base histórica para estudios de **30M-400M** registros según el estudio. [V]
- **Algoritmo de Deal Rating** (propietario): combina **(1) Price** (cuánto por debajo del market value estimado, calculado sobre comparables de mismo year/make/model/trim/options/mileage + condiciones de oferta/demanda locales), **(2) Car quality** (history data, descripción del vendedor, kilometraje, fumado/no, nº de propietarios), **(3) Dealer** (scorecard: pricing competitiveness + transparencia + responsiveness), **(4) Market time** (días anunciado como proxy de días en mercado). Resultado → badge Great/Good/Fair/Overpriced + score. [V]
- **Market value** = modelo propietario sobre **comparables locales** (mismo year/make/model/trim/options/mileage) + supply/demand + location. [V]
- **Remaining Lifespan** = modelo de supervivencia sobre odómetro medio por edad (probabilidad de llegar a umbrales de millas). [V]
- **Ventas "inferidas"**: DOM y best-time-to-buy usan la **desaparición del anuncio** como proxy de venta (no transacciones/matrículas reales). [V]
- **Neutralidad declarada**: rating "objetivo, independiente y unbiased"; el negocio es B2C (no cobra al dealer por mejorar su nota). [V]

---

## 5. Entrega
- **Portal web** (iseecars.com) — canal primario: motor de búsqueda, Price My Car, VIN check, rankings, estudios. [V]
- **Apps móviles** iOS + Android ("Used Car Search Pro – iSeeCars") con **escáner de barras VIN**. [V]
- **Informes iVIN** por VIN (HTML on-line) bajo **suscripción mensual**; incluye **local market reports por ZIP** (Pro). [V]
- **Estudios / press releases / artículos** públicos (research hub) — distribución a medios (syndication editorial). [V]
- **Sindicación de inventario de dealers** hacia el motor (lead-gen / tráfico de vuelta al dealer). [V]
- **[A]** Sin **API pública autoservicio** documentada, sin **bulk data feeds / SFTP** ni integración DMS — contraste neto con MarketCheck. La data "se entrega" como producto terminado (rating, valoración, informe, estudio), no como feed crudo.

---

## 6. Precio
**Freemium B2C: buscador + deal rating + VIN check básico GRATIS; informes iVIN por suscripción mensual.** [V]

| Plan | Precio | Reports/mes | Incluye |
|---|---|---|---|
| **Free VIN Check** | **$0** | — | VIN decode + specs, features, recall check (abiertos+pasados), theft/stolen (NICB) |
| **iVIN Lite** | **$9,95/mes** (tachado $40,00) | **50** | accident check, stolen, title/lien, listing history, recalls, consumer complaints, pricing analysis, **market value analysis**, safety ratings, app + escáner VIN |
| **iVIN Pro** | **$39,95/mes** (tachado $80,00) | **200** | todo lo de Lite + **No ads** + **local market reports (ZIP + por vehículo)** + integración **CARFAX** (requiere sub CARFAX aparte) |
| **Custom** | "Contact us" | — | plan a medida para alto volumen |

- **Solo facturación mensual** ("All of our current subscriptions are by the month"; sin plan anual). [V]
- **Buscar coches, Price My Car y deal rating = gratis** (monetización vía lead-gen/tráfico a dealers + advertising + suscripciones iVIN). [V/A]
- **No hay precio por llamada / API** (no es un proveedor de datos por volumen). [V]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: mapeo pantalla/sección → dato.

### Tarjeta de anuncio (resultados de búsqueda) — "ficha de coche" [V]
- **Badge superior/junto al precio**: **Deal Rating** (Great/Good/Fair/Overpriced) — el elemento visual dominante.
- **Bloque precio**: `price` (grande) + **`savings_vs_market`** ("$X Below market value of $Y").
- **Bloque identidad**: `heading` (year+make+model+trim) + foto.
- **Bloque salud/calidad** (lo distintivo de iSeeCars): **`remaining_lifespan` (años)** + `days_listed` + `dealer_score` (1-5★) + `mileage` + `location`.
- **Expandible/VDP**: specs completas (engine, transmission, drivetrain, colors, MPG, seats, doors, features/options, VIN).

### Sidebar de filtros — el dato como criterio de filtrado [V]
- Filtros propietarios destacados arriba: **iSeeCars Price Rating**, **Remaining Lifespan**, **Dealer Score**, **Amount Below Market Price** (junto a los specs estándar). Pone su inteligencia (rating, lifespan, ahorro) **al mismo nivel jerárquico** que precio/km.

### Price My Car — pantalla de valoración del vendedor [V]
- **Cifra central**: `average_market_price` + `price_range` (% dentro de 1σ).
- **Panel de recomendación dual**: "In a Rush to Sell?" (rápido) vs. "Want to Make More Money?" (máx beneficio), cada uno con % de similares más caros + indicador de demanda.
- **Gráfico**: scatter de comparables con **línea de market price**.
- **Tablas inferiores**: histórico 12 meses (valor medio mensual) + curva de depreciación por model-year.

### iVIN report — informe de due-diligence por VIN [V]
- Secuencia de secciones: **Market value analysis → Condition analysis → Similar cars → Demand/Supply → Selling history → Dealer scorecard → Multi-year depreciation → Best time to buy/sell → Title/Lien (DMV) → Accident → Specs/Serial → Features → Safety → Recalls → Consumer complaints → Theft (NICB) → Window sticker → (Pro) Local market report por ZIP + CARFAX**.

### Páginas de estudios/rankings — "market intelligence" pública [V]
- Patrón de tabla repetido: **Rank · Model · [métrica del estudio] · Compared to Average (multiplicador)**. La métrica varía: depreciación % + $ vs MSRP (con `segment`), % a 250k millas, Days on Market, índice de deals por mes/festivo, resale %, reliability, MPG, HP, cargo, range, towing.
- Cada ranking enlaza al motor de búsqueda filtrado (research → shopping).

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Deal Rating algorítmico consumer-facing** (Great/Good/Fair/Overpriced) sobre ~75% del usado de EE.UU., con el **ahorro absoluto vs. market value impreso en cada tarjeta** — orientación de compra accionable e inmediata, gratis. (CarGurus es el competidor directo de este patrón; KBB/Black Book no lo hacen así.)
- [V] **"Remaining Lifespan" por anuncio** (años de vida útil restante) — métrica propietaria derivada de un modelo de longevidad sobre ~400M coches; **filtrable y ordenable**. Casi nadie expone esto a nivel de anuncio individual.
- [V] **Dealer Scorecard transparente (1-5★, 3 criterios)** integrado en el rating — reputación del vendedor como variable de decisión.
- [V] **Price My Car con recomendación dual por urgencia** (vender rápido vs. ganar más) + % de comparables más caros + demanda — más accionable que un único "valor estimado".
- [V] **Fábrica de estudios de mercado de alto impacto mediático** (depreciación, longevidad 250k millas, fastest-selling DOM, best-time-to-buy, EV/hybrid, colores, recalls) con metodología declarada y muestras enormes — convierte su data en autoridad de marca y SEO.
- [V] **iVIN: informe por VIN que fusiona valoración + historial + análisis de mercado** (market value + demand/supply + dealer score + best time + title/lien DMV + accident + recall + theft + window sticker) en un solo producto barato ($9,95-$39,95/mes), opcionalmente con CARFAX — empaqueta inteligencia que otros venden por separado.
- [V] **Window sticker + build sheet lookup** por VIN (MSRP/opciones de fábrica) integrados.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **Solo EE.UU.** — sin Canadá, UK ni Europa (irrelevante directamente para cobertura ES, pero define el patrón).
- [V] **No es proveedor de datos B2B API-first**: sin API pública autoservicio, sin bulk feeds/SFTP, sin integración DMS, sin pricing por llamada. La data se entrega "cocinada" (rating/valoración/informe/estudio), no en crudo. Contraste neto con MarketCheck.
- [V] **No es guía de valores editorial** con tablas trade/retail/wholesale normalizadas: aunque **define** market/trade-in/retail/instant-cash, su valoración nuclear es **un market value predicho + rango + comparables**; no publica matrices de valor por trim como KBB/Black Book/J.D. Power.
- [V] **Sin valores residuales / forecasting de RV** como producto B2B (la depreciación es retrospectiva/estimada en estudios e iVIN, no un servicio de residuals para leasing/flotas tipo Autovista/Black Book Lender).
- [V] **Sin TCO / running costs / SMR** (tiempos de reparación, precios de pieza, mantenimiento programado).
- [V] **Sin verticales no-coche** (RV/moto/comercial/maquinaria) — a diferencia de MarketCheck US.
- [V] **Provenance dependiente de 3os**: title/lien (DMV), robo (NICB), historial completo (CARFAX, sub aparte) — no hay informe de siniestros/propietarios propio tipo Carfax/AutoCheck.
- [V] **Ventas inferidas, no transaccionales**: DOM/best-time/sales studies infieren venta por desaparición del anuncio — riesgo de sesgo, no son matrículas reales.
- [V] **Cifras de escala de vintages mezcladas** (4M en vivo / 25B data points / 30M base / ahorro $60M vs $449M) — no hay un dato único consolidado y datado.
- [V] **Transparencia corporativa limitada**: bootstrapped sin rondas; **empleados (~8-10) y facturación (~$630k) son estimaciones de 3os** poco fiables y probablemente desactualizadas; iSeeCars no publica plantilla ni ingresos oficiales.
- [V] **Año de fundación ambiguo** (idea 2008 / incorporación ~2011 / lanzamiento 2013).
- [A] **Metodología del rating no auditable externamente**: "proprietary algorithm"; los pesos exactos (precio vs. calidad vs. dealer vs. tiempo) no se publican.
- [A] **Sin marketplace transaccional propio**: es buscador + scoring; la transacción ocurre en el dealer/marketplace de destino (modelo lead-gen).

---

## 10. Fuentes (URLs)
- https://www.iseecars.com/ — home: 4M+ coches, deal rating, ahorro agregado $449.672.974, "largest online car search engine".
- https://www.iseecars.com/about-us/ — identidad: fundadores Phong Ly / Vineet Manohar, "Kayak for car buyers", 25B+ data points, >75% del usado US, 10M+ listings/día, $60M ahorrado, partnerships eBay/Chrome Data, Dealer Scorecard (3 criterios).
- https://en.wikipedia.org/wiki/ISeeCars.com — lanzamiento 23-oct-2013, Woburn MA, privada, 30M+ listings, estudios (200k millas/Tesla/minivans), MITX + Webby, partnerships.
- https://www.iseecars.com/research y https://www.iseecars.com/research/studies — catálogo completo de estudios + todos los rankings 2026 + herramientas (Price My Car, VIN Check, Car Finder, Vehicle History, Window Sticker, Build Sheet).
- https://www.iseecars.com/vin — Free VIN Check (decode/specs/recalls/theft NICB) vs iVIN de pago; campos del informe.
- https://www.iseecars.com/subscription-vin-plans — precios iVIN Lite $9,95/mes (50 reports) y Pro $39,95/mes (200 reports, local market reports por ZIP, CARFAX), custom; solo mensual.
- https://www.iseecars.com/price-used-cars — Price My Car: inputs VIN/manual, market price, price range, recomendación dual (rush vs more money), demand, gráfico comparables, histórico 12m, curva depreciación.
- https://www.iseecars.com/articles/how-much-is-my-car-worth — tipos de valor (market/private party, trade-in, retail, instant cash offer) + factores de valoración.
- https://www.iseecars.com/used-cars/used-honda-accord-for-sale — tarjeta de anuncio: deal badge, savings vs market value, Remaining Lifespan (yrs), days listed, dealer score; filtros (Price Rating, Remaining Lifespan, Dealer Score, Amount Below Market…) y sorts.
- https://www.iseecars.com/cars-that-hold-their-value-study — depreciación: 5-yr %, $ vs MSRP (BLS-ajustado), segment; 950k coches mar25-feb26; media 41,8% / $16.571.
- https://www.iseecars.com/longest-lasting-cars-study — % de llegar a 250.000 millas vs media 4,8%; ~400M coches; base de "Remaining Lifespan".
- https://www.iseecars.com/fastest-selling-cars-study — Days on Market por modelo; 960k coches feb-2026; media 53,0 días; Tesla Model X 22,6 / Volvo XC60 hybrid 170,2.
- https://www.iseecars.com/best-times-to-buy-cars-study — índice de deals (% vs media) por mes/festivo; deal = ≥10% bajo FMV; 40M+ ventas 2024-25.
- https://www.highperformr.ai/company/iseecars-com — liderazgo (Phong Ly CEO, Vineet Manohar CTO, Julie Blackley Exec Analyst), HQ 400 West Cummings Park Woburn MA.
- https://www.apollo.io/people/Karl/Brauer/... — Karl Brauer, Executive Analyst en iSeeCars.
- https://www.zoominfo.com/p/Vineet-Manohar/... y https://www.adapt.io/contact/vineet-manohar/... — Vineet Manohar, Co-Founder & CTO.
- https://app.dealroom.co/companies/iseecars — bootstrapped/sin financiación, Woburn, 2-10 empleados, founded 2011 (variación).
- https://growjo.com/company/iSeeCars.com — ~9 empleados, ~$630k ingresos (estimación 3os, baja fiabilidad).
- https://www.crunchbase.com/organization/iseecars y https://pitchbook.com/profiles/company/96246-73 — perfil privado sin rondas de financiación.
- https://apps.apple.com/us/app/used-car-search-pro-iseecars/id1039018770 y https://play.google.com/store/apps/details?id=com.iseecars.android.app — apps móviles + escáner VIN.
- Prensa (verificación de autoridad/uso de datos): ABC News, CBS News, CNBC, Consumer Reports, WSJ, USA Today, Forbes, WIRED — citan estudios iSeeCars.
- nslookup: **market-intelligence / data / api / insights .iseecars.com = NXDOMAIN** (no resuelven; "market-intelligence" es etiqueta de categoría, no host).

> Verificación: identidad corporativa contrastada con ≥3 fuentes independientes (about-us + Wikipedia + highperformr/ZoomInfo/Dealroom). Esquema de campos [V] leído directamente de las páginas de producto (búsqueda, Price My Car, VIN, subscription plans) y de los estudios. Precios [V] de subscription-vin-plans. Métricas de estudios [V] de cada página de estudio con su metodología y muestra. Discrepancias (año de fundación, plantilla, ingresos, cifras de escala de distintas vintages) marcadas explícitamente, no resueltas por invención. Subdominio "market-intelligence" = etiqueta taxonómica del orquestador (NXDOMAIN como host), confirmado por nslookup.
