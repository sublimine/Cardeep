# Percayso Vehicle Intelligence — Auditoría atómica

> **slug:** `percayso-vehicle-intelligence` · **subdominio de audit:** `valuation` · **web:** https://percayso-vehicle-intelligence.co.uk/ (301 → cazana.com)
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** el **retador "data-driven, retail-back"** de la valoración UK. Antítesis de cap/Glass's: **cero edición humana**,
> ML + quantile regression sobre **1.000M+ de anuncios** y **800k VRN/día**. Su músculo es la **valoración retail en tiempo real
> segmentada por canal** (Supermarket / Independent / Franchise) + **days-to-sell / profit corridor** + **timeline de historial
> construido desde anuncios** (con detección de daño y modificaciones por las fotos). Doble vertical: automoción **y** seguros
> (point-of-quote, fraude, total loss) bajo el grupo **Percayso Inform**. Entrega vía **portal + API REST (forecast hasta 10 años)**.
> Patrón a copiar por cardeep: la **valuation card** con valores por canal + velocidad de mercado, y el **timeline de provenance**.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **Percayso Vehicle Intelligence (PVI)** — *formerly* **Cazana**; en feb-2026 reactivan la marca de producto **"Cazana"** | [VERIFICADO ≥2: LinkedIn "Percayso Vehicle Intelligence (formerly Cazana)", motortrader, neconnected] |
| Grupo / owner | **Percayso Inform Limited** (t/a "Percayso") — proveedor de **insurance data intelligence**. Company No. **11377058** | [VERIFICADO ≥2: insurancebusinessmag, percayso-inform.com] |
| HQ | **Hine House, 25 Regent Street, Nottingham, NG1 5BS, England** | [VERIFICADO ≥2: insurancebusinessmag, percayso-inform.com] |
| HQ histórico Cazana | London — 41-43 Chalton St, Lower Ground Floor, NW1 1JD (perfil CB Insights) | [VERIFICADO: cbinsights] |
| Fundación grupo Percayso Inform | **2018**, por **Simon James** (antes fundó y salió de *Insurance Initiatives* en 2016); hoy **Chairman** | [VERIFICADO ≥2: búsqueda, percayso-inform.com] |
| Fundación Cazana | **2012** ("founded in 2012") — CB Insights indica **2013** (discrepancia menor) | [VERIFICADO ≥2: percayso-inform, am-online] / [DISCREPANCIA: cbinsights=2013] |
| CEO original Cazana | **Tom Wood** (CEO) — índice de precios por *machine learning* | [VERIFICADO: insightssuccess] |
| Cadena de propiedad | Cazana (2012) → adquirida por **Cazoo** en **2021 por £25M** → vendida a **Percayso Inform el 23-feb-2023** (precio no revelado) → relanzada como PVI | [VERIFICADO ≥2: insurancetimes, marketscreener, percayso-inform] |
| Inversión grupo | Percayso Inform: **£2,7M** (jul-2023) liderada por **Neil Utley** y **Praetura Ventures**; ronda previa **€3,14M** | [VERIFICADO ≥2: uktechnews, siliconcanals] |
| Funding histórico Cazana | **$8,11M** (CB Insights); inversores: Passion Capital, Robert Diamond, Experian, Cazoo, Percayso Inform | [VERIFICADO: cbinsights] |
| Liderazgo PVI | **Rich Tomlinson** (Percayso MD) · **Kieran Fisher** (lidera la propuesta de vehicle data insight; ex-Head of Insurance en Cazana 5 años) · **Ian Lilley** (Director of Automotive / Head of Partnerships) · **Derren Martin** (Automotive expert & lead spokesperson de market insight — ex-cap hpi) | [VERIFICADO ≥2: insurancebusinessmag, neconnected, motortrader] |
| Confianza institucional | Usado por **6 de los top 10 motor insurers UK**; **40+ clientes**; **"go-to data source"** del **Financial Ombudsman Service** | [VERIFICADO ≥2: insurancebusinessmag, percayso-inform] |

**Qué es:** negocio de **datos e inteligencia de vehículo** que entrega **valoración de usado en tiempo real** (retail + trade,
segmentada por canal), **forecast de residuales**, **inteligencia de mercado/stock**, **historial/provenance** y un brazo de
**insurance intelligence** (point-of-quote, fraude, total loss). El motor es 100% ML/data-driven sobre un lago de anuncios.

### Categorías de producto
1. **Valoración usado en tiempo real** (retail + trade + por canal) — núcleo (Companion).
2. **Forecast / residual values** (1 mes → 5 años en portal; hasta 10 años por API; EV / defleet).
3. **Inteligencia de mercado / stock & pricing** (Stockview, Stockcompare).
4. **Historial / provenance / timeline** (MOT, keeper, plate, anuncios, daño, modificaciones).
5. **Insurance intelligence** (point-of-quote pre-fill, fraude, total loss / Claims Companion).
6. **Procesamiento masivo** (Multi — Excel/CSV bulk).
7. **API / data ingest** (feed REST embebido).

### Cliente objetivo (sectores declarados)
Car dealers (**independents · franchises · car supermarkets**) · Vehicle insurance · Vehicle manufacturers (OEM) ·
Vehicle finance / lenders · Vehicle leasing / fleet · Auctions/remarketing · (vía grupo) brokers, MGAs y comparison sites.

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado principal | **Reino Unido (UK)** — "the UK's leading valuation provider"; donde vive el dato atómico | [VERIFICADO ≥2: percayso-inform, búsqueda] |
| Internacional | Cazana fue "una de las leading data insight platforms de **la industria automotriz europea**"; PVI "supplies data in **Europe**". Cobertura europea **declarada pero no detallada/expuesta** por país | [VERIFICADO declaración: búsqueda] / [NO-VERIFICADO detalle por país] |
| Acuerdo histórico | Experian: acuerdo exclusivo a 5 años (financial services/banking) | [VERIFICADO: insightssuccess] |
| Volumen advert lake | **1.000M+ (one billion) live & historic vehicle adverts** desde **2012**, mapeados a VRM | [VERIFICADO ≥2: homepage, am-online, motorfinance] |
| Ingesta diaria | **~800.000 VRN únicos/día**; **~700.000–750.000+ precios retail únicos/día**; **12.000+ fuentes** (trade + private classified), actualizado a diario | [VERIFICADO ≥2: companion page, cardealermag, motorfinance] |
| Data points | **1.000M+ unique data points** (claim de escala de base de datos) | [VERIFICADO ≥2: insurancebusinessmag, percayso-inform] |

### Scope de vehículo
- **Principalmente USADO** (valoración retail/trade). Specs presentes; **no** hay catálogo NVD de coche nuevo tipo cap.
- Tipos: **Cars, Vans (LCV), Motorbikes/Motorcycles**.
- Forecast incluye **EV** y **defleet** residuals.
- Granularidad de valoración: por **VRM y VIN** (vehículo exacto), ajustada por **age, mileage, condition, specification**.
- Horizonte: histórico desde **2012**; forecast **1 mes → 5 años** (portal) / **hasta 10 años** (API).

---

## 3. Productos + campos atómicos

> Nota: el portal `percayso-vehicle-intelligence.co.uk` redirige (301) a `cazana.com`; el contenido de producto vive ahí.
> Páginas de marketing → algunos campos no se enumeran públicamente y se marcan como hueco.

### 3.1 Companion — valoración usado en tiempo real (producto estrella, SaaS)
**Qué es:** valoración instantánea por **VRM** basada en el **mercado retail en vivo** (no en guía mensual), con historial completo,
overview de mercado y forecast. "The most comprehensive real-time valuations available." Vehículos: cars, vans, motorbikes.
**Campos atómicos:**
- `Retail value` (precio retail actual del mercado en vivo)
- `Trade value` (precio recomendado de compra en auction/wholesale)
- **Valores retail por canal:** `Supermarket value` · `Independent value` · `Franchise value` (5 tipos junto a Trade + Retail) [VERIFICADO: MotorCheck partnership]
- `Real-time daily valuation` (valor diario en vivo)
- `Monthly valuation` (vista mensual estática para gestión de asset stock)
- `Five-year future residual value` (calculado sobre todos los vehículos)
- `Days to sale` / `Days to sell` (indicador de cuánto tardará en venderse)
- **`Profit corridor` indicator** (corredor de margen para decisión instantánea de compra/precio)
- `Market demand` indicator (rapidez de venta de similares)
- `Price positioning` vs vehículos comparables
- `Retail Intelligence` metrics
- `Market overview` (vehículo vs **whole retail market**)
- `Identical vehicles on the market today` (comparación de idénticos en venta)
- `Vehicle timeline` / `Vehicle history` (de fabricación → presente)
- `MOT test results` / MOT history
- `VRM changes` (cambios de matrícula)
- `Keeper (ownership) changes`
- `Sales event history` (con `images`, `mileage`, `price`, `listing text`)
- `Historical advert data` (provenance vía anuncios)
- `Full provenance check` (issues que afectan a un claim)
- **Damage detection** (vía imágenes de anuncios previos)
- **Modification identification**
- `Fraud detection`
- `Mileage estimate` (vía advert histórico + MOT)
- Ajustes por `age`, `mileage`, `condition`, `specification`
- `Depreciation` data
- `Technical specifications`
- `VIN-level detail` (valoración del vehículo exacto)
- `Valuation certificate` (soporte/justificante)
- Metodología transparente vía **live market listings**
- Entrega: **portal web (desktop + móvil)** + **API**

### 3.2 Companion Used Car Forecasts — forecast / residual values
**Qué es:** forecast de valor para part-exchange y residuales de leasing/defleet.
**Campos atómicos:**
- Forecast **1 mes → 5 años** (portal)
- Forecast **hasta 10 años** (vía API)
- `EV residual` forecast
- `Defleet residual` forecast
- `Future RV` (RV modelling, current + historical valuations como base)
- Uso: valorar **part-exchanges** (retailers) y predecir **EV/defleet residuals** (leasing)

### 3.3 Cazana Monthly — valoración mensual estática
**Qué es:** "static used car valuations for a fixed monthly view" (la vista de guía mensual clásica, para quien la necesita).
**Campos atómicos:**
- `Static monthly used car value` (trade + retail, vista mensual fija)
- Soporte a **asset stock management** / revaluación de asset register

### 3.4 Multi — valoración/datos en masa (bulk)
**Qué es:** procesa **grandes volúmenes** de datos de vehículo "all at once", resultados en minutos. Input Excel/CSV.
**Campos atómicos:**
- `Trade valuation` (bulk, real-time retail-backed)
- `Retail valuation` (bulk)
- `Residual value assessment` (bulk)
- `Vehicle history` (bulk)
- `Provenance information` (bulk)
- `General vehicle information`
- Input: **Excel / .csv** subido directamente ("thousands of rows" en minutos)
- Output: portal/dashboard
- Fuentes: **DVSA, DVLA, SMMT, MOT records, retail market data**
- Uso: stock assessment, **auction preparation**, **portfolio revaluation**

### 3.5 Stockview — add-on de stock para dealers
**Qué es:** add-on de Companion con pricing y consejo de reprice a nivel de stock + competencia local.
**Campos atómicos:**
- `Stock pricing`
- `Turnover data`
- `Repricing advice`
- `Local competitor insights`
- `Local vehicle insights`

### 3.6 Stockcompare — benchmarking regional (OEM / fleet / leasing)
**Qué es:** compara precios y demanda regionales vs competidores; protege residuales y optimiza remarketing.
**Campos atómicos:**
- `Regional price benchmark` vs competidores
- `Regional demand benchmark`
- Comparación **franchise vs independent** sales
- `Residual value protection`
- `Remarketing optimization`
- `Regional stock levels` a nivel **brand/model**
- `Stock location` (real-time, todas las marcas)
- `Secondary market performance` (cómo rinde el vehículo en mercado secundario)

### 3.7 API / Data Ingest / Data Solutions
**Qué es:** APIs REST modernas, baja latencia, gran volumen; "thousands of data fields" (no enumerados públicamente).
**Campos atómicos (expuestos):**
- `Real-time valuations`
- `Market forecasting` (hasta 10 años)
- `Rich vehicle history`
- Datos a nivel **VRM y VIN**
- `Vehicle specification`
- `Change of keeper`, `MOT history`
- `Images` y `descriptions`
- Integración: **Motors (Cazoo), Experian, Cartotrade, AUCA, One Auto API, MotorCheck**
- Entrega: **RESTful API** (formato JSON no confirmado explícitamente) [NO-VERIFICADO formato]

### 3.8 Insurance / Vehicle Intelligence — point-of-quote + Claims Companion + fraude
**Qué es:** uso del dato de vehículo en el lifecycle de seguro (cotización, claim, renovación, fraude). Brazo del grupo Percayso Inform.
**Campos atómicos:**
- **Point-of-quote pre-fill (desde VRM):** `vehicle value`, `mileage`, `date of purchase`
- Integración `DVLA data`, `DVSA`, `MOT history`
- `Market-backed valuation` (live retail) para **total loss / settlement**
- `Comparable vehicle data` (mercado actual)
- `Historic valuation data`
- `Fair cash-out value`
- `Written-off vehicle assessment`
- `Outstanding finance status`
- `PNC` (Police National Computer) records
- `Write-off indicator`
- `VIN-level detail`
- `Vehicle modifications` detection
- `MOT advisories`
- `Vehicle history records`
- `Historic vehicle advertisements`
- **Señales de fraude:** `unexpected provenance issues` · `discrepancies between declared and actual specs` · `suspicious non-disclosures` · `inflated valuations` · `risk flags` (cuando el cliente modifica el valor sugerido) · `quote manipulation indicators` · `behavioural risk indicators` · `intent/manipulation signals`
- `12-month claim probability` indicator
- **Claims Companion:** `condition` assessment · `value against similar listings` · `detailed history timeline`
- `Renewal pricing optimization` (vía MOT tracking)
- `Customer engagement triggers` (MOT reminders, pricing updates)

### 3.9 Finance / Lenders (configuración de Companion + Forecasts)
**Campos atómicos:**
- `PCP residuals`
- `Set-to-loan ratio` (LTV)
- `End-of-term settlement figures`
- `Negative equity` / depreciation monitoring
- `Future RVs`
- `Asset register valuation` / `financial exposure`
- `Depreciation trends` por **model, specs, age, mileage**
- Valoraciones retail-backed **diarias** (no mensuales)
- Provenance: MOT history, MOT advisories, registration changes, **cherished plate transfers**, previous adverts & text, **mileage irregularities**, keeper changes

### 3.10 Leasing / Fleet (configuración)
**Campos atómicos:**
- `Whole-of-market valuations`
- `Monthly rates` y `end-of-term values`
- `Regional stock levels` a nivel brand/model
- Retail valuations al **end of term**
- `Future RVs` (current + historical)
- `EV` / `defleet` residuals

---

## 4. Metodología / fuentes de datos

| Elemento | Detalle | Estado |
|---|---|---|
| Filosofía | **100% data-driven, sin edición ni sesgo humano** — antítesis de las guías editoriales (cap/Glass's). "No human bias or editing applied" | [VERIFICADO ≥2: finance page, lenders page] |
| Técnicas | **Machine learning models** · **quantile regression** · **complex decision trees** | [VERIFICADO ≥2: dealers page, búsqueda] |
| Enfoque de valoración | **"Retail Back" methodology / top-down**: parte del precio retail en vivo y deriva hacia trade | [VERIFICADO ≥2: motorfinance, cardealermag] |
| Equipo | "data scientists and machine learning experts constantly building new models" | [VERIFICADO: insightssuccess] |
| Fuentes externas | **DVLA, DVSA, SMMT, MOT records**, + **12.000+ trade & private classified sources**, retail market data | [VERIFICADO ≥2: multi page, cardealermag] |
| Escala diaria | **~800.000 VRN/día** · **~700.000–750.000+ precios retail/día** · **1.000M+ anuncios** desde 2012 | [VERIFICADO ≥2] |
| Mapeo | Todo mapeado a **VRM**, con detalle a nivel **VIN** | [VERIFICADO ≥2] |
| Imágenes | Detección de **daño** y **modificaciones** a partir de **fotos de anuncios** archivados | [VERIFICADO: companion page] |

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Portal web (SaaS)** | Companion en **desktop + móvil**; "data portal significantly enhanced". Trade portal: `trade.percayso-vehicle-intelligence.co.uk` | [VERIFICADO ≥2: motorfinance, companion page] |
| **API REST** | "modern RESTful APIs, easy to integrate"; real-time + forecast **hasta 10 años**; baja latencia a escala | [VERIFICADO ≥2: api page, businessmotoring] |
| **Bulk Excel/CSV** | Multi: subida de hoja → resultados en portal en minutos ("thousands of rows") | [VERIFICADO: multi page] |
| **Data feed / ingest** | "API Data Ingest" — feed embebido en sistemas del cliente | [VERIFICADO: homepage nav] |
| **Certificados** | `Valuation certificate` (justificante de valoración) | [VERIFICADO: companion page] |
| **Integración / embebido** | Motors (Cazoo), **Experian**, **Cartotrade** (in-platform), **AUCA**, **One Auto API**, **MotorCheck** | [VERIFICADO ≥2: neconnected, motortrader, motorcheck, motortradenews] |
| **Frecuencia** | **Diaria** (real-time) o **mensual** (Cazana Monthly) | [VERIFICADO ≥2] |

---

## 6. Precio

| Aspecto | Detalle | Estado |
|---|---|---|
| Modelo | **Suscripción B2B**, quote-based; **sin tarifa pública** | [VERIFICADO indirecto: páginas "Talk to our team"] |
| Tool Cartotrade | **Gratis 3 meses** para miembros Cartotrade / trial; luego **add-on opcional**, **sin auto sign-up**; posicionado como alternativa a "costly contracts" | [VERIFICADO ≥2: cardealermag, motorfinance] |
| Trials | Free trial disponible (portal) | [VERIFICADO: cardealermag] |

---

## 7. Placement (patrón web a copiar por cardeep)

> Cómo PVI/Cazana **coloca cada dato en su UI**. Blueprint directo para la ficha de vehículo y el timeline de cardeep.

| Dato | Dónde lo coloca PVI |
|---|---|
| Retail / Trade value + valores por canal (Supermarket/Independent/Franchise) | **Valuation card** de Companion tras introducir **VRM (+ km)**: bloque de valores como salida principal |
| Days to sell + **Profit corridor** | **Indicadores en la misma valuation card** — ayudas de decisión instantánea (margen + velocidad) |
| Market demand / price positioning | **Panel de market overview** dentro de la card: comparación vs *whole retail market* |
| "Identical vehicles on the market today" | **Lista de comparables** en venta hoy, junto a la valoración |
| Forecast RV (1m→5a) | **Vista de forecast** (curva/tabla); horizonte **10 años** solo por API |
| Vehicle history timeline | **Pantalla de timeline** (fabricación→presente): MOT, VRM changes, keeper changes, **sales events con imágenes/km/precio/texto** |
| Provenance / daño / modificaciones | **Dentro del timeline** + sección de provenance check (daño inferido de fotos de anuncios) |
| Stock pricing / turnover / repricing | **Dashboard add-on Stockview** (competencia + vehículo local) |
| Benchmark regional precio/demanda | **Portal Stockcompare** (franchise vs independent) |
| Insurance point-of-quote | **Campos pre-rellenados** en el formulario de cotización (value, mileage, purchase date) |
| Total loss / settlement | **Vista de claim** (Claims Companion): valor vs similar listings + historic valuations + timeline |
| Fraude / risk flags | **Flags en point-of-quote** y al **modificar el valor sugerido** |
| Bulk | **Multi**: subida Excel/CSV → tabla de resultados en portal |
| Acceso programático | **API REST** embebida en DMS/sistema del cliente (sin UI propia) |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Cero edición humana**: valoración 100% ML/data-driven (quantile regression + decision trees) — frente a las guías editoriales mensuales de cap/Glass's. Velocidad y objetividad como bandera.
2. **Real-time diario** (no cadencia mensual): el valor se mueve con el mercado retail en vivo.
3. **Valores retail segmentados por canal** (`Supermarket` / `Independent` / `Franchise` + Trade + Retail): granularidad por tipo de retailer poco común en el sector.
4. **Lago de anuncios masivo** (1.000M+ desde 2012; 800k VRN/día; 12.000+ fuentes) mapeado a VRM/VIN — base de "retail-back".
5. **Métricas de velocidad de mercado nativas** (`days to sell`, `market demand`, `profit corridor`) integradas en la valuation card — más cerca de Auto Trader/Indicata que de cap/Glass's.
6. **Provenance por "arqueología de anuncios"**: timeline con **daño y modificaciones detectados desde las fotos** de anuncios previos — ángulo único.
7. **Forecast hasta 10 años** (API) + **EV/defleet residuals** explícitos.
8. **Doble vertical**: automoción **+** insurance intelligence (point-of-quote, fraude, total loss) respaldado por el grupo Percayso Inform (Quote/Policy/Bureau Intelligence).
9. **Ecosistema de embed**: Motors/Cazoo, Experian, Cartotrade, AUCA, One Auto API, MotorCheck — distribución vía terceros.
10. **Autoridad en seguros**: 6 de los top 10 motor insurers UK + fuente "go-to" del Financial Ombudsman Service.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **Transparencia de precio nula**: todo quote-based; sin self-serve público (salvo el trial Cartotrade).
2. **UK-céntrico**: cobertura europea **declarada pero no expuesta** por país; el dato atómico vive en UK.
3. **Sin docs de API públicos / sandbox**: "thousands of data fields" sin enumerar; el schema exige contacto comercial.
4. **Inestabilidad de marca/dominio**: `percayso-vehicle-intelligence.co.uk` redirige a `cazana.com`; sucesión de rebrands (Cazana → PVI → vuelta de "Cazana" 2026) — señal de fricción operativa/identidad.
5. **Sin catálogo NVD de coche nuevo** tipo cap (no 460k options/list prices, no WLTP/CO2/P11D atómico expuesto). Specs presentes pero no como base técnica enciclopédica.
6. **Sin SMR / TCO / whole-life-cost**: no modela costes de explotación, mantenimiento ni pence-per-mile (gap vs cap TotalCost).
7. **Sin producto provenance "check" de consumidor** equivalente a HPI Check: finance/PNC/write-off aparecen sobre todo en contexto de **seguros**, no como informe standalone para particulares.
8. **No expone "price-to-market %" ni "market days supply"** por nombre: tiene `days-to-sell` + `demand`, pero no el índice de posición de precio % al estilo Auto Trader. [NO-VERIFICADO que no exista internamente.]
9. **No es marketplace** ni vende stock: monetiza el **dato/valor**, no el inventario.
10. **No huella digital de punto de venta**: no cataloga dealers ni su presencia online (territorio propio de cardeep).
11. **Dependencia del advert lake**: el "retail-back" puede adelgazar en vehículos raros/baja rotación con pocos anuncios. [INFERIDO]
12. **Posicionamiento legado confuso**: CB Insights aún lo lista como "car search engine" (origen consumer), rol hoy abandonado.

---

## 10. Fuentes (URLs)

**Web de producto (cazana.com == contenido de percayso-vehicle-intelligence.co.uk)**
- https://percayso-vehicle-intelligence.co.uk/ (301 → cazana.com)
- http://cazana.com/products/companion/ (Companion: valores, days-to-sale, timeline, provenance)
- http://cazana.com/products/multi/ (Multi: bulk Excel/CSV, fuentes DVSA/DVLA/SMMT/MOT)
- http://cazana.com/products/api-data-solutions/ (API REST)
- http://cazana.com/solutions/dealers/ (days-to-sell, demand, quantile regression/decision trees, future RVs)
- http://cazana.com/solutions/insurance/ (point-of-quote pre-fill, fraude, total loss)
- http://cazana.com/solutions/finance/ (PCP residuals, set-to-loan, settlement, negative equity)
- http://cazana.com/solutions/leasing/ (whole-of-market, monthly rates, end-of-term)
- http://cazana.com/solutions/vehicle-manufacturers/ (future RVs, stock location, secondary market, Stockcompare)
- http://cazana.com/solutions/lenders (asset register, forecast RVs, provenance)
- https://trade.percayso-vehicle-intelligence.co.uk/ (trade portal)

**Identidad / grupo / adquisición**
- https://www.percayso-inform.com/ (grupo: Quote/Bureau/Policy/Vehicle Intelligence, Symphony, Enrich, Quote/Policy Lake)
- https://www.percayso-inform.com/percayso-inform-set-for-major-expansion-following-acquisition-of-cazana/ (adquisición 23-feb-2023, MD Rich Tomlinson, Kieran Fisher, 6/10 insurers, 40+ clientes, 1bn data points)
- https://www.insurancebusinessmag.com/uk/news/auto-motor/percayso-inform-acquires-automotive-data-insight-platform-437419.aspx (uso en seguros, Financial Ombudsman, Somerset Bridge, Ageas)
- https://www.insurancetimes.co.uk/news/cazoo-sells-cazana-to-percayso-inform-for-undisclosed-sum/1443899.article (Cazoo vende Cazana)
- https://www.marketscreener.com/.../Percayso-Inform-Limited-acquired-Cazana-Data-Platform-from-Cazoo-Group-Ltd-43064947/
- https://www.uktechnews.info/2023/07/27/percayso-inform-t-a-percayso-secures-2-7-million-investment-led-by-neil-utley-and-praetura-ventures/ (£2,7M, Simon James founder)
- https://www.cbinsights.com/company/cazana (funding $8,11M, inversores, HQ histórico London, fundación 2013)
- https://uk.linkedin.com/company/percaysoinformvehicleintelligence ("Percayso Vehicle Intelligence (formerly Cazana)")
- https://insightssuccess.com/cazana-providing-vehicle-data-valuations-and-audience-for-the-future-of-mobility/ (CEO Tom Wood, ML, Experian 5-year, days-to-sale)

**Relaunch 2026 + Cartotrade (productos y forecast)**
- https://neconnected.co.uk/respected-cazana-brand-returns-as-percayso-vehicle-intelligence-relaunches/ (roster: Companion, Forecasts, Monthly, Stockcompare, Stockview, API; 1m-5a; partners; Ian Lilley, Derren Martin)
- https://businessmotoring.co.uk/percayso-to-rebrand-as-cazana-to-support-fleets-with-enhanced-data/ (roster + 10-year API + EV/defleet)
- https://www.motortrader.com/motor-trader-news/automotive-news/cazana-returns-as-percayso-vehicle-intelligence-relaunches-25-02-2026 (RV modelling, stock/pricing comparison portal, sectores)
- https://www.motorfinanceonline.com/news/cazana-launches-real-time-retail-valuation/ (Companion: profit corridor, days-to-sale, top-down, retail+trade)
- https://cardealermagazine.co.uk/percayso-partners-with-cartotrade-to-provide-dealers-market-intelligence/310131 (750k precios/día, days-to-sell, VRM/VIN, free 3 meses)
- https://www.motorfinanceonline.com/news/percayso-partners-with-cartotrade-to-launch-uk-vehicle-market-intelligence-tool/ (Retail Back, lanzamiento nov-2024)
- https://help.motorcheck.co.uk/en/articles/9533741-motorcheck-partners-with-percayso (**5 valores: Trade/Retail/Supermarket/Independent/Franchise**; VRM/VIN; 700k/día)
- https://www.percayso-inform.com/how-percayso-is-delivering-next-generation-insurance-intelligence-services-with-leading-vehicle-data/ (Claims Companion, PNC, outstanding finance, write-off, fraude)
- https://www.motortradenews.com/dealer-insights/one-auto-api-adds-percayso-to-auto-intelligence-hub/ (integración One Auto API)

**Fuentes inaccesibles (403) — citadas por título/búsqueda, no fetch directo:** am-online.com (relaunch + Cartotrade), fleetnews.co.uk (relaunch fleet/finance), fleetworld.co.uk.

> **Marcas [NO-VERIFICADO] / inferencias:** cobertura europea por país; formato JSON de la API; ausencia interna de price-to-market%/market-days-supply;
> adelgazamiento del modelo en vehículos raros (inferido del enfoque retail-back); fundación 2012 vs 2013 (discrepancia entre fuentes).
