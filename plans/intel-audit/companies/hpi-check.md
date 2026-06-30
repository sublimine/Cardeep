# HPI Check — Auditoría atómica

> **slug:** `hpi-check` · **subdominio de audit:** `vin-history` · **web:** https://www.hpi.co.uk/ (consumer: https://www.home.hpicheck.com/ · trade B2B: cap hpi)
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** el **estándar de facto del vehicle provenance check en UK** desde **1938** ("Britain's first vehicle provenance check").
> No es un valuador: es el **informe de historial/identidad** que cruza **finance + stolen (PNC) + write-off + clocking (NMR propia) + plate/colour changes
> + import/export/scrapped + keepers + recall + VIN/V5 match**, presentado como **rejilla de semáforos (pass/warning/alert) arriba + secciones
> expandibles abajo**. Marca consumer (hpicheck.com, £19.99, **£30.000 data guarantee**) + brazo B2B (trade check + **Vehicle Data API**) que corre
> sobre el **backend de datos de cap hpi** (mismo grupo Solera: CAP Code, NVD, Black Book, NMR). **Patrón estrella a copiar por cardeep:**
> la **report summary grid de badges de estado** + el **alert banner top-of-report** + el **NMR mileage timeline** (tabla fecha/fuente/lectura).

> **Relación con `cap-hpi.md`:** HPI Check y cap hpi son **dos caras del mismo activo Solera**. Este fichero cubre el eje **provenance/historial/identidad**
> (consumer + trade + history API). El eje **valoración/specs/datos B2B** está auditado en `cap-hpi.md`. Comparten backend, NMR y data guarantee.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **HPI** / **HPI Check®** ("hpi check" es marca registrada; avisan de imitaciones "FREE hpi check") | [VERIFICADO ≥2: hpi.co.uk, home.hpicheck.com] |
| Significado | **HPI = Hire Purchase Information** | [VERIFICADO ≥2: Wikipedia HPI Ltd, búsqueda] |
| Razón social | **HPI LIMITED** — Companies House nº **04068979** (HQ legal UK) | [VERIFICADO: GOV.UK Companies House] |
| Grupo / owner | **Solera** (Solera Holdings, Inc.) — "global leader in data & software for automotive, home ownership and digital identity management" | [VERIFICADO ≥2: hpi.co.uk footer, home.hpicheck.com, SEC 8-K] |
| Marca de datos B2B hermana | **cap hpi** (fusión CAP + HPI) — backend de valoración/specs/provenance del grupo | [VERIFICADO ≥2: cap-hpi.com, api.cap-hpi.co.uk] |
| HQ actual | **Leeds, UK** (base cap hpi). HQ histórico **Salisbury** cerrado en 2015 al fusionar operaciones UK | [VERIFICADO ≥2: búsqueda, Motor Trader] |
| Fundación | **1938**, por **seis compañías financieras** en respuesta al alza del fraude de coches; "Britain's first vehicle provenance check" | [VERIFICADO ≥2: Wikipedia, cap-hpi/about, home.hpicheck/about-us] |
| Cadena de propiedad | Origen mutual de finance houses → **Aviva** compra **HPI Group Holdings** (ago-2004) → **Solera** completa la compra el **19-dic-2008 por £94,4M** → CAP comprado por Solera (nov-2014) → marcas UK fusionadas como **"cap hpi"** (2015) | [VERIFICADO ≥2: Aviva newsroom, SEC 8-K FY2008, Motor Trader, CMA SoleraCAP decision] |
| Discrepancia precio 2008 | **£94,4M** (Motor Trader / búsqueda) vs **£78,3M** (Insurance Times "Solera completes £78.3m acquisition of HPI") — posible diferencia equity vs enterprise value | [DISCREPANCIA entre fuentes] |
| Otras marcas Solera | Audatex, Autodata, Sidexa, AutoData, AUTOonline, cap hpi | [VERIFICADO: búsqueda, cap-hpi.md] |
| Experiencia declarada | "**more than 900 years' industry experience**" combinada (editores de valoración + agentes de atención) | [VERIFICADO: hpi.co.uk] |
| Premios | **Car Dealer Power "Best Car Check Provider"** 2013, 2014, 2016-2023 · **"Best Valuations Provider"** 2013-2018, 2021-2023 | [VERIFICADO: hpi.co.uk] |

**Qué es:** servicio de **comprobación de historial/identidad de vehículo (provenance check)** que, a partir de la **matrícula (VRM)**, devuelve
un **informe** que revela si el coche tiene **finance pendiente, está robado, ha sido siniestro total (write-off), tiene discrepancia de km
(clocking), ha cambiado de matrícula/color, ha sido importado/exportado/desguazado, cuántos keepers ha tenido, si hay recall pendiente y si la
identidad (VIN/V5) cuadra**. Lo respalda una **garantía de datos de £30.000**. Doble mercado: **consumer** (particular comprando/vendiendo) y
**trade/B2B** (dealers, fleets, insurers + Vehicle Data API).

### Categorías de producto
1. **Provenance / vehicle history check** (núcleo: HPI Check full, Basic, MultiCheck).
2. **Valoración** (free car valuation; respaldada por datos cap/HPI).
3. **MOT history check** (gratis).
4. **Safety recall check** (por matrícula real).
5. **TCO / cost of ownership check** (3 años).
6. **my hpi app** (gestión de coche: perfiles, recordatorios MOT/tax, valoración, TCO, recalls, doc storage).
7. **Vehicle Data API** (B2B: history + valuation + spec + MOT + DVLA por VIN/VRM).
8. **Trade check / HPI for business** (due diligence de dealer, vía backend cap hpi).

### Cliente objetivo
**Consumer** (comprador/vendedor particular de usado) · **Dealers & traders** · **Fleets** · **Motor insurers** · **Finance houses / lenders** ·
**Desarrolladores / integradores** (API) · **Partners white-label** (AA, eBay, Gumtree, Parkers…).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Mercado | **Reino Unido (UK) exclusivamente** — todo el dato atómico (DVLA, PNC, MIAFTR, NMR, finance interests) es UK | [VERIFICADO ≥2: home.hpicheck.com, hpi.co.uk] |
| Parque cubierto | "Hemos podido **actualizar y mejorar más del 97%** de los vehículos hoy en circulación" | [VERIFICADO: hpi.co.uk] |
| Finance interests | **8M+ live finance interests** = **>98% del mercado de motor finance UK** | [VERIFICADO: búsqueda B2B / claim HPI] |
| NMR (millaje) | **National Mileage Register** propia: **369M+ readings** (claim reciente; histórico citado 200M+), datos desde **1992** | [VERIFICADO ≥2: home.hpicheck/mileage, Carwow, búsqueda] |
| Frecuencia de "hidden history" | "**1 in 3** vehicles we check has some form of hidden history"; "**1 in 17 vans** is an insurance write-off" | [VERIFICADO ≥2: outstanding-finance page, van-check page] |
| Distribución white-label | HPI **alimenta checks de marca de terceros** vía subdominios `*.hpicheck.com`: **AA** (£14.99), **eBay/Gumtree** (£9.99), **Parkers** (£8.99), UCNI, etc. | [VERIFICADO ≥2: gumtree.hpicheck.com, parkers.hpicheck.com, búsqueda] |

### Scope de vehículo
- **Foco: USADO** (provenance). La valoración cubre además **price-when-new**.
- Tipos: **Cars · Vans / LCV · Motorbikes / Bikes** (checks dedicados: Van Check, Bike Check). Motorhome no confirmado como check propio. [VERIFICADO ≥2: home.hpicheck nav, van-check]
- Identificador de entrada: **VRM (matrícula UK)**; la API B2B acepta **VIN** y devuelve datos DVLA/SMMT/cap hpi.
- Histórico: NMR desde **1992**; provenance desde primera matriculación UK.

---

## 3. Productos + campos atómicos

> El informe HPI Check full es el activo central. Los **labels exactos** salen del **sample report** (`hpicheck.com/vehiclecheck/report/sample`).
> El backend de spec/valoración es **cap hpi** (ver `cap-hpi.md` para el detalle de NVD/Black Book/CAP Code).

### 3.1 HPI Check (full / standard) — informe de provenance estrella
**Qué es:** informe completo por VRM, **80+ data points**, con **£30.000 data guarantee**. £19.99 consumer.
**Campos atómicos (estructura real del informe, en orden):**

**A. Cabecera / resumen**
- `Check reference number`
- `Check performed date/time`
- `Vehicle image` ("for illustrative purposes only")
- **`Alert banner`** (alertas críticas top-of-report: outstanding finance / total loss / mileage discrepancy)
- **`Report summary grid`** = badges de estado: `Not recorded stolen`, `Not scrapped`, `Not exported`, `Recalls (checked/not)`, `Plate Changes`, `Imported`, `Outstanding Finance`, `Insurance Write-Off`, `Fraud Guard`, `Mileage discrepancy`, `MOT Expiry (date)`

**B. HPI Fraud Guard**
- `VIN (chassis number)`
- `V5 registration document issue date`
- `V5 serial number`

**C. Vehicle Description (manufacturer spec)**
- `Make`
- `Model` (derivative, p.ej. "300C SRT-8 AUTO")
- `Engine size (cc)`
- `Engine number`
- `Fuel` (type)
- `Body plan` (body type)
- `Colour` (current)
- `Number of colour changes`
- `Last colour change date`
- `Gearbox` (transmission)
- `Year of manufacture`
- `Current owner/keeper acquired on` (date)
- `Date of first registration in the UK`

**D. Vehicle Ownership**
- `Number of previous owners/keepers`

**E. Emissions & Tax**
- `CO2 emissions`
- `CO2 ratings` (band)
- `Tax Status` (taxed/SORN/due)
- `Tax Expiry Date`

**F. Export / Scrapped Status**
- `Exported` marker (DVLA)
- `Scrapped` marker (DVLA)

**G. Police Stolen Check**
- `Stolen` marker (Police National Computer / PNC)

**H. Insurance Theft**
- `Insurer theft` marker (recorded by an insurer)

**I. Outstanding Finance** (sección alerta)
- `Recorded against` (Licence plate and/or VIN)
- `Description` (vehículo del acuerdo)
- `Date` (of agreement)
- `Finance house` (company name)
- `Finance house telephone` (contact)
- `Agreement reference`
- `Agreement type` (Hire Purchase / PCP / lease / logbook loan)

**J. Condition Alert (Write-Off)** (sección alerta)
- `Recorded against` (Licence plate and/or VIN)
- `Description`
- `Date` (write-off date)
- `Category` (**Cat A / B / C / D / S / N** + descripción del daño)

**K. Plate Transfer**
- `Previous plates` (registration mark anterior)
- `Plate change date`

**L. Security Watch**
- `'At risk' marker` (security watch register)

**M. VIN Match**
- `VIN`
- `V5 issue date`
- `V5 serial number`
- (verificación cruzada anti-clon: VIN vs V5C)

**N. Vehicle Documents**
- `V5C (Logbook) issue date`
- `V5C (Logbook) serial number`

**O. Recall Check**
- `Recall status` (Outstanding / clear)
- `Issue` (defecto, p.ej. "DRIVE SHAFT LINKAGE")
- `Last update` (date)

**P. Fuel Economy (DVLA records)**
- `CO2 Emissions (g/km)`
- `Cylinder Capacity (cc)`
- `First Registered Date`
- `Urban MPG`
- `Extra urban MPG`
- `Combined MPG`
- `Estimated fuel cost (12,000 miles)`
- `VED for 12 months`

**Q. Vehicle Valuation**
- `Estimated market value`
- `Based on` (modelo de referencia)

**R. Vehicle Mileage Check (National Mileage Register)**
- `Mileage discrepancy` alert
- **Tabla de millaje:** `Date Recorded` · `Recorded by` (fuente, p.ej. NMR) · `Mileage Reading`

**Transversal:**
- `£30,000 data guarantee` (activada con full check)
- `Cloned / false identity` indicator (derivado de VIN/V5 + identity check)
- `Imported` (incl. non-EU import) / `Exported` flags

### 3.2 Basic Check — provenance reducido
**Qué es:** £9.99, **sin detalle completo, sin mileage discrepancy, sin write-off detail, SIN £30.000 guarantee**.
**Campos atómicos:** `Outstanding finance` (flag) · `Stolen` (flag) · `Scrapped` (flag) · `Written-off` (flag) · `Imported` / `Exported` (flag). [VERIFICADO ≥2: búsqueda pricing, home.hpicheck]

### 3.3 MultiCheck — bundle
**Qué es:** **3 full checks** por **£29.97-£29.99** ("50% saving"). Mismos campos que el full, ×3 vehículos. [VERIFICADO ≥2]

### 3.4 Free Car Valuation
**Qué es:** valoración instantánea por VRM (gratis), respaldada por "industry-leading data from hpi and CAP Automotive".
**Campos atómicos:**
- `Private sale value`
- `Trade-in value`
- `Forecourt (retail) value`
- `Price when new` / at-new value (en el full check)
- `Past / historical values`
- `Future / projected values`
- `Depreciation` (cómo cae el valor en el tiempo)
- `Running cost estimates` (fuel, tax, servicing, maintenance)
- `Cost per year / per month / per mile`
- Ajuste por `mileage` y detalles del vehículo
- Entrega: resultado instantáneo + email. [VERIFICADO ≥2: home.hpicheck/car-valuation, hpi.co.uk]

### 3.5 MOT History Check (gratis)
**Campos atómicos:** `MOT status` · `MOT expiry date` · `Test date` · `Result (pass/fail)` · `Recorded mileage at test` · `Advisory notes` · `Previous status / failure reasons` · `Road tax renewal date`. Fuente: **DVSA/DVLA**. [VERIFICADO ≥2: hpi.co.uk, sample report]

### 3.6 Safety Recall Check (£2.95; gratis en app)
**Qué es:** "the only company that will check the **actual number plate** rather than just general make & model".
**Campos atómicos:** `Recall status` (outstanding/clear) · `Issue/defect description` · `Last update date` · `Make/model` · `Colour` · `First registered`. Marca el recall como resuelto si el fabricante ya reparó. Fuente: **fabricantes**. [VERIFICADO ≥2: hpi.co.uk/hpi-recall, sample report]

### 3.7 TCO Check / Total Cost of Ownership (3 años)
**Campos atómicos:** `Annual depreciation` · `Monthly/yearly running costs` · `Service & maintenance cost` · `Road tax (VED)` · `Fuel cost` · `Tyre replacement timing & cost` · `Brake pad replacement timing & cost` · `Value retention` · `3-year total cost breakdown` · comparativa "cheapest to run". Backend SMR/TotalCost de cap hpi. [VERIFICADO ≥2: hpi.co.uk, myhpi, cap-hpi.md]

### 3.8 my hpi (app iOS + web) — gratis
**Campos/funciones:** `Vehicle profiles` (coches que tienes o piensas comprar, ilimitados) · `Free instant valuations` (trade-in/private/forecourt) · `Depreciation past/present/future` · `MOT reports` · `Automatic MOT & Tax reminders` · `Customisable event alerts` · `3-year TCO breakdown` · `Running cost comparisons` · `Free recall checks` (normalmente £2.95) · `Document storage` (recibos/historial). [VERIFICADO ≥2: hpi.co.uk/myhpi, búsqueda]

### 3.9 Vehicle Data API (B2B) — history + spec + valuation por VIN/VRM
**Qué es:** "access to thousands of data points covering millions of cars, vans & motorcycles… build digital products with HPI". Corre sobre **api.cap-hpi.co.uk** (web services cap hpi). Modelo **pay-as-you-go → subscription**.
**Campos atómicos (datasets expuestos):**
- **Spec:** `make/model`, `engine capacity`, `torque`, `vehicle spec`, `colour`, `weight`, **factory-fit standard options**, `list price` ("UK's only factory-fit database")
- **Valuation:** condition-adjustable `private sale` / `trade-in` / `forecourt` / `at-new` + `past` & `future` values
- **MOT:** `MOT status`, `previous test results`, `advisory notes`
- **DVLA:** datos de registro DVLA por VIN
- **Finance:** `finance company`, `agreement type`, `agreement date`, `contact details`
- **Write-off:** `write-off date`, `damage category (Cat A/B/C/D/S/N)`
- **SMR:** `service`, `maintenance`, `repair cost estimates`
- **Mileage:** discrepancias del national mileage register
- **Recall:** alertas de fabricante por matrícula
- **Plate history:** `plate change dates`, `markers on previous plates`
- **Theft:** PNC stolen alerts
- **TCO:** annual running costs (insurance, fuel, tax, service, maintenance)
- **Emissions:** `Euro standard (Euro 1-6)`
- **Status flags:** import / export / scrapped (DVLA)
- Entrada: **VIN / VRM**. Update **diario o mensual** según suscripción. Formato (REST/JSON/XML) heredado de cap API. [VERIFICADO: hpi.co.uk/vehicle-data-api, hpi.co.uk/data, cap-hpi.md]

### 3.10 Trade check / HPI for business
**Qué es:** due diligence de dealer/fleet/insurer, "digs much deeper than public checks". Acceso vía **Trade Login**.
**Campos:** outstanding finance, theft (PNC), write-off (Cat S/N), provenance verificada para reventa legal; respaldo de **8M+ finance interests (98% del mercado)**. [VERIFICADO ≥2: búsqueda B2B, cap-hpi/hpi-check]

---

## 4. Metodología / fuentes de datos

| Fuente | Aporta | Estado |
|---|---|---|
| **DVLA** | Logbook/V5C, keepers, colour, scrapped, exported, tax status, fuel/CO2 | [VERIFICADO ≥2] |
| **Police National Computer (PNC)** | Stolen marker | [VERIFICADO ≥2] |
| **MIAFTR** (Motor Insurance Anti-Fraud & Theft Register, vía ABI insurers) | Write-off / total loss + theft por aseguradora | [VERIFICADO ≥2: búsqueda, RAC] |
| **Finance houses / lenders** | Outstanding finance (8M+ interests = 98% mercado UK), logbook loans | [VERIFICADO ≥2] |
| **NMR (National Mileage Register)** — propiedad de HPI | 369M+ lecturas de km desde 1992 (DVLA, V5, MOT/VOSA, auctions, leasing, insurance) | [VERIFICADO ≥2] |
| **SMMT** (Society of Motor Manufacturers & Traders) | Datos de fabricante / identidad | [VERIFICADO ≥2] |
| **DVSA** | MOT history, advisories | [VERIFICADO ≥2: sample report] |
| **Fabricantes (OEM)** | Safety recalls por matrícula | [VERIFICADO: hpi-recall] |
| **cap hpi backend** | Spec/NVD (CAP Code, factory-fit options, list price), valoración (Black Book), SMR/TCO | [VERIFICADO ≥2: vehicle-data-api, cap-hpi.md] |
| Declaración de cobertura | "20+ data sources", "80+ data points", "97%+ vehículos en circulación actualizados" | [VERIFICADO ≥2] |

**Garantía:** **£30.000 data guarantee** — HPI cubre hasta £30.000 si pierdes dinero por dato inexacto (solo full check). [VERIFICADO ≥2]

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **Web consumer** | `home.hpicheck.com` / `hpi.co.uk` — compra por VRM, informe online instantáneo | [VERIFICADO ≥2] |
| **Informe (report)** | Online interactivo: **summary grid de badges** + **alert banner** + secciones expandibles ("Find out more"); descargable | [VERIFICADO: sample report] |
| **App my hpi** | **iOS + navegador web**; perfiles, recordatorios, valoración, TCO, recalls | [VERIFICADO ≥2] |
| **Vehicle Data API (B2B)** | REST/web services vía **api.cap-hpi.co.uk**; pay-as-you-go → subscription; update diario/mensual | [VERIFICADO ≥2] |
| **Trade portal** | **Trade Login** separado (dealers/fleets/insurers) | [VERIFICADO: hpi.co.uk nav] |
| **White-label partners** | Subdominios `*.hpicheck.com` (gumtree, parkers, ucni/AA, eBay…) sirviendo informe con marca del partner | [VERIFICADO ≥2] |
| **Email** | Valoración entregada por email tras introducir VRM | [VERIFICADO: car-valuation page] |

---

## 6. Precio

| Producto | Precio | Notas | Estado |
|---|---|---|---|
| **Full / standard HPI Check** | **£19.99** | 80+ data points + £30.000 guarantee | [VERIFICADO ≥2] |
| **Basic Check** | **£9.99** | finance/stolen/scrapped/write-off/import-export, sin detalle ni guarantee ni mileage | [VERIFICADO ≥2] |
| **MultiCheck (×3 full)** | **£29.97-£29.99** | "50% saving" | [VERIFICADO ≥2] |
| **Safety Recall Check** | **£2.95** | gratis en la app my hpi | [VERIFICADO ≥2] |
| **Free Car Valuation** | **£0** | gratis (upsell a full check) | [VERIFICADO ≥2] |
| **MOT History Check** | **£0** | gratis | [VERIFICADO ≥2] |
| **Promo puntual** | full check visto a **£8.99** en página de valoración | promoción / precio variable | [VERIFICADO: car-valuation page] |
| **White-label** | AA £14.99 · eBay/Gumtree £9.99 · Parkers £8.99 | precio fijado por el partner | [VERIFICADO ≥2] |
| **Vehicle Data API / Trade** | **quote-based** (pay-as-you-go → subscription) | sin tarifa pública | [VERIFICADO indirecto] |

> ⚠ **Trustpilot:** quejas recurrentes de **cargo de suscripción ~£39 auto-renovable** poco claro tras el check y de problemas para canjear MultiCheck. Señal de **dark-pattern** en el flujo consumer. [VERIFICADO: Trustpilot hpicheck.com]

---

## 7. Placement (patrón web a copiar por cardeep)

> Cómo HPI **coloca cada dato en el informe**. Es el blueprint más directo para la **ficha de historial/identidad** de cardeep:
> primero un veredicto visual de un vistazo, luego el detalle por bloques con estado semáforo.

| Dato | Dónde lo coloca HPI |
|---|---|
| Alertas críticas (finance / write-off / mileage) | **`Alert banner` rojo en lo más alto del informe** — lo primero que ve el usuario |
| Estado de cada check | **`Report summary grid`**: rejilla de **badges pass (✓ verde) / alert (⚠ naranja-rojo)** — stolen, scrapped, exported, imported, plate changes, finance, write-off, fraud guard, mileage, recall, MOT expiry |
| Identidad/fraude (VIN/V5) | Sección **HPI Fraud Guard** + **VIN Match** + **Vehicle Documents** (V5C issue date/serial) |
| Spec del vehículo | Sección **Vehicle Description** (make/model/engine/fuel/body/colour/year/first reg) |
| Keepers | Sección **Vehicle Ownership** (nº previous owners) |
| Emisiones/impuesto | Sección **Emissions & Tax** (CO2, tax status/expiry) |
| Finance | Sección **Outstanding Finance** expandible: finance house, teléfono, agreement ref/type/date |
| Write-off | Sección **Condition Alert** expandible: categoría (Cat A/B/C/D/S/N) + descripción + fecha |
| Plate/colour history | **Plate Transfer** (matrículas previas + fecha) + colour changes dentro de Vehicle Description |
| Recall | Sección **Recall Check**: status + defecto + last update |
| Fuel economy / TCO | Sección **Fuel Economy** (MPG urban/extra/combined, est. fuel cost 12k, VED 12m) |
| Valoración | Sección **Vehicle Valuation** (estimated market value) — bloque único, no es el foco |
| Millaje / clocking | Sección **Vehicle Mileage Check (NMR)**: **alerta + tabla `Date / Recorded by / Mileage`** (timeline de lecturas) |
| Cada sección | **expandible/colapsable** con enlace **"Find out more"** |
| Multi-canal | Mismo informe servido white-label en `*.hpicheck.com` con marca del partner |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad de marca 1938**: "Britain's first vehicle provenance check"; "HPI Check" es casi genérico en UK (la gente dice "hacer un HPI"). Confianza institucional irreplicable.
2. **NMR propietaria** (National Mileage Register, **369M+ lecturas desde 1992**) — registro de clocking que casi nadie iguala; se presenta como **timeline de lecturas** con fuente.
3. **98% del mercado de motor finance UK** (8M+ live finance interests) — cobertura de finance pendiente difícil de batir.
4. **£30.000 data guarantee** — respaldo económico explícito al dato (full check), argumento anti "free check".
5. **Recall por matrícula real** (no solo make/model) — "the only company" que lo hace a ese nivel.
6. **UX del informe = veredicto de un vistazo**: alert banner + grid de badges semáforo, luego detalle expandible. Patrón de presentación maduro.
7. **Backend cap hpi compartido**: el mismo grupo le da spec (CAP Code, factory-fit options, list price), valoración (Black Book) y SMR/TCO — one-stop dentro de Solera.
8. **Red de distribución white-label** (AA, eBay, Gumtree, Parkers, UCNI…): HPI es el motor oculto detrás de muchos "car checks" UK.
9. **Cobertura de tipos**: car + van/LCV + bike, con mensajería específica (1 in 17 vans = write-off).
10. **Vehicle Data API** que empaqueta history + spec + valuation + MOT + DVLA por VIN para integradores.

---

## 9. Gaps (lo que NO ofrece / debilidades)

1. **UK-only**: todo el dato atómico es británico (DVLA/PNC/MIAFTR/NMR/finance). Sin provenance equivalente en otros países (fuera de UK, el grupo va vía filiales Solera).
2. **No es valuador de mercado en tiempo real**: la valoración es un **bloque secundario** del informe, derivada de cap (mensual/editorial), **sin** métricas de velocidad de mercado (days-to-sell, market days supply, price-to-market %, demand index) que sí tienen Indicata/Auto Trader/Percayso.
3. **Dark-pattern de suscripción** en consumer: cargo **~£39 auto-renovable** poco claro y fricción para canjear MultiCheck → quejas en Trustpilot. Riesgo reputacional.
4. **Sin docs de API públicas / sandbox abierto**: la Vehicle Data API remite a cap hpi (api.cap-hpi.co.uk) y exige subscriber ID; sin free tier ni schema público enumerado campo a campo.
5. **Campos de finance/write-off limitados en Basic**: el £9.99 da solo flags; el detalle y la guarantee exigen el £19.99 (fragmentación de valor).
6. **No expone telemetría / uso real / datos de conducción** ni daño desde fotos de anuncios (a diferencia de Percayso/Cazana).
7. **Specs no son el foco consumer**: el detalle NVD enciclopédico (460k options, WLTP/P11D atómico) vive en cap hpi B2B, no en el informe HPI Check.
8. **No es marketplace ni fuente de stock vivo**: vende el **informe/dato**, no inventario en venta.
9. **No huella digital de punto de venta**: no cataloga dealers ni su presencia online (territorio propio de cardeep).
10. **Recall data potencialmente incompleta**: "Recalls not checked" aparece si falta info; depende de feeds de fabricante.
11. **Solapamiento de marcas confuso** (HPI vs hpicheck.com vs cap hpi vs my hpi vs white-labels) — fricción de identidad y SEO contra clones "free HPI check".

---

## 10. Fuentes (URLs)

**Producto / informe (consumer)**
- https://www.hpi.co.uk/ (awards, nav, 900 años experiencia, 97%+ parque, parent Solera)
- https://www.home.hpicheck.com/ (productos, pricing, 80+ data points, data sources, £30k guarantee)
- https://www.home.hpicheck.com/what-is-a-hpi-check/ (lista de checks: stolen, finance, write-off, clocked, MOT, valuation, owners, plate, import/export, scrapped, logbook, VIN)
- https://hpicheck.com/vehiclecheck/report/sample (**sample report — estructura y labels exactos de cada sección**)
- https://www.home.hpicheck.com/car-valuation/ (private/trade/forecourt + depreciación + running costs)
- https://www.home.hpicheck.com/mileage-discrepancy-check/ (NMR 369M+ readings)
- https://www.home.hpicheck.com/outstanding-finance-check/ (finance fields, "1 in 3 hidden history")
- https://www.home.hpicheck.com/van-check/ (van/LCV scope, "1 in 17 vans")
- https://www.home.hpicheck.com/about-us/ (1938, pioneros, marca registrada)
- https://www.hpi.co.uk/hpi-recall.html (recall por matrícula real)
- https://www.hpi.co.uk/myhpi.html (app: perfiles, TCO 3 años, recordatorios)

**B2B / API / datos**
- https://www.hpi.co.uk/vehicle-data-api.html (campos API: spec, valuation, MOT, finance, write-off, SMR, recall, emissions)
- https://www.hpi.co.uk/data.html (datasets + partners AA/Confused/eBay/Gumtree/WhatCar/Shpock/CarWow)
- https://api.cap-hpi.co.uk/docs/index.html (developer docs cap hpi — backend de la API; render JS, no enumerado por fetch)
- https://www.cap-hpi.com/hpi-check/ (HPI Check for business)

**Identidad / propiedad / verificación cruzada**
- https://en.wikipedia.org/wiki/HPI_Ltd (1938, Hire Purchase Information, six finance companies)
- https://find-and-update.company-information.service.gov.uk/company/04068979 (HPI LIMITED)
- https://www.aviva.com/newsroom/news-releases/2004/08/aviva-acquires-hpi-group-holdings-ltd-in-the-uk-1825/ (Aviva 2004)
- https://www.sec.gov/Archives/edgar/data/0001324245/000119312508256398/dex991.htm (Solera 8-K, adquisición HPI 19-dic-2008)
- https://www.motortrader.com/magazine/hpi-acquired-by-solera-12-01-2009 (£94,4M)
- https://www.insurancetimes.co.uk/solera-completes-783m-acquistion-of-hpi/1376298.article (£78,3M — discrepancia)
- https://assets.publishing.service.gov.uk/media/557ac79d40f0b6154b000003/SoleraCAP_Decision.pdf (CMA: Solera compra CAP)
- https://www.motortrader.com/motor-trader-news/automotive-news/hpi-cap-merge-uk-operations-09-09-2015 (fusión UK 2015, Salisbury)

**Distribución white-label / reviews**
- https://gumtree.hpicheck.com/ · https://parkers.hpicheck.com/ · https://ucni.hpicheck.com/ (powered by HPI)
- https://uk.trustpilot.com/review/hpicheck.com (reviews; quejas suscripción £39)
- https://www.carwow.co.uk/used-cars/guides/national-mileage-register-explained (NMR independiente, mayor DB UK)

> **Marcas [NO-VERIFICADO] / discrepancias:** precio 2008 £94,4M vs £78,3M (equity vs EV, sin reconciliar); formato exacto (JSON/XML) de la Vehicle Data API
> (heredado de cap API, no re-confirmado en hpi.co.uk); existencia de check propio para motorhome; cifra NMR 200M vs 369M (claim antiguo vs reciente);
> schema campo-a-campo de la API B2B (tras login). Todo lo demás verificado en ≥2 fuentes o en el sample report oficial.
