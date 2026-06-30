# Auditoría atómica — CARFAX (carfax.com)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos e inteligencia de automoción VIN-céntrica**: opera la **mayor base de datos de historial de vehículos del mundo** (30-38 mil millones de registros) y la convierte en (1) el **CARFAX Vehicle History Report** — estándar de facto del informe por VIN en EE.UU./Canadá—, (2) la **History-Based Value (HBV)**, valoración propietaria *ajustada por el historial concreto de cada VIN*, (3) un **marketplace de usados** (CARFAX Used Car Listings) donde cada anuncio lleva su historial, y (4) productos de datos B2B para **dealers, prestamistas, aseguradoras y policía**. El eje diferencial no es la cobertura de listings ni una guía editorial de valores trim-a-trim: es la **HUELLA DE EVENTOS POR VIN** (accidentes, títulos, propietarios, servicio, odómetro) y su impacto monetario en el valor. Web del scope: https://www.carfax.com/value/ (History-Based Value / "What's my car worth").
> Categoría taxonómica asignada por el orquestador (campo `subdomain`): **vin-history**. Es una **etiqueta de categoría**, no un host DNS verificado.
> Fecha auditoría: 2026-06-30. Método: WebSearch geolocalizado en EE.UU. (devuelve contenido de carfax.com en snippets sintetizados) + WebFetch sobre fuentes terceras no bloqueadas (Wikipedia, KBB, PRNewswire, carvins.net, indyautoman, police1, Duck Creek, S&P Global IR) + carfax.eu (fetch directo). **Limitación de entorno declarada**: el egress de WebFetch sale por Suiza (Swisscom/Zürich, verificado con ipinfo.io), por lo que `www.carfax.com/*` redirige 301→`carfax.eu/de` y los subdominios B2B (`support.`, `carfaxforlenders.`, `carfaxonline.`, `carfaxbig.`) devuelven 403 a fetch directo. Se compensó con WebSearch US-only y fuentes terceras; ningún campo se inventó.
> Convención: **[V]** = verificado leyendo la fuente (≥1 fuente; los núcleos con ≥2) · **[A]** = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **CARFAX** (CARFAX® Vehicle History Report™). Mascota: **Car Fox** (zorro de marca, originalmente marioneta). | [V] |
| Razón social | **Carfax, Inc.** | [V] |
| Categoría | **Proveedor de historial de vehículos por VIN + valoración basada en historial + marketplace de usados + datos B2B**. Estándar de facto del Vehicle History Report en Norteamérica. NO es guía editorial de valores trim-a-trim (tipo KBB/Black Book/J.D. Power) ni proveedor API-first de listings (tipo MarketCheck); su activo nuclear es la **huella de eventos por VIN** y su impacto en valor. | [V] |
| Fundación | **1984, en Columbia, Missouri (EE.UU.)** | [V — Wikipedia + HandWiki + múltiples] |
| Fundadores | **Ewin Barnett III** y **Robert Daniel Clark** | [V — Wikipedia] |
| HQ | **Centreville, Virginia (EE.UU.)** históricamente; **reubicación anunciada 2025 a Reston Station (Reston, VA)** (Comstock Holdings IR, "Comstock Welcomes CARFAX to Reston Station", 2025). | [V] |
| Propiedad | **Marca dentro de S&P Global Mobility** (unidad de S&P Global). | [V] |
| Cadena de propiedad | **1984** independiente → **otoño 1999** filial 100% de **R.L. Polk & Company** → **2013** **IHS** compra Polk+CARFAX (deal ~$1,4 B) → **marzo 2016** IHS + Markit = **IHS Markit** → **28-feb-2022** **S&P Global** compra IHS Markit; CARFAX pasa a **S&P Global Mobility** → **29-abr-2025** S&P Global anuncia intención de **escindir Mobility en una compañía pública independiente**. | [V — Wikipedia + Motley Fool + S&P Global IR + Auto Remarketing] |
| Liderazgo | **Bill Eager — CEO de CARFAX**; designado para **liderar S&P Global Mobility** (presidente desde 15-ago) y **CEO-designate** de la futura compañía escindida. | [V — Auto Remarketing] |
| Empleados | **~1.500** (cifra citada **1.491**, agregadores de 3os) | [A — LeadIQ/agregadores, baja fiabilidad] |
| Facturación | **No divulgada oficialmente.** Estimaciones de 3os divergen brutalmente (una cita ~**$300 M**; otras dan rango **$1 B–$10 B** confundiéndolo con la división Mobility). | [A — estimación 3os, ver Gaps] |
| Subsidiaria/afiliada | **CARFAX Canada** (entidad propia, carfax.ca) · **CARFAX Europe** (carfax.eu) · **CARFAX Banking & Insurance Group / BIG** (carfaxbig.com, carfaxforlenders.com, carfaxforclaims.com) · **CARFAX for Police** (carfaxforpolice.com). | [V] |

### Hitos / cronología [V]
- **1984** Fundación en Columbia, Missouri (Barnett III + Clark).
- **1999** R.L. Polk adquiere CARFAX.
- **~2011** Patentes de **underwriting/rating de seguros** basado en historial de vehículo (PRNewswire).
- **2013** IHS compra Polk+CARFAX (~$1,4 B).
- **2016** Nace IHS Markit.
- **jun-2019** Lanza **Total Loss Valuation Service** (CarfaxForClaims) e **integración con Facebook Marketplace** (informes CARFAX gratis en anuncios de dealers participantes).
- **feb-2022** S&P Global adquiere IHS Markit → CARFAX en S&P Global Mobility.
- **dic-2022** **30.000 millones de registros** alcanzados (tardó 15+ años en llegar a 1.000 M; ahora suma 1.000 M cada 5 meses).
- **abr-2025** S&P Global anuncia escisión de Mobility (Bill Eager al frente).

### Clientes objetivo (segmentos) [V]
1. **Compradores de coche usado** (B2C — informe por VIN + marketplace + Buyback Guarantee).
2. **Vendedores particulares** (History-Based Value / Trade-In tool / "Sell my car").
3. **Dealers/concesionarios** (informes ilimitados, Used Car Listings advertising, HBV, Snapshot, Advantage/Top-Rated, Auction Quick Check).
4. **Prestamistas / bancos / cooperativas de crédito** (CARFAX for Lenders / BIG).
5. **Aseguradoras** (underwriting, claims, total loss — CarfaxForClaims / BIG).
6. **Fuerzas del orden** (CARFAX for Police, gratis a cambio de compartir datos de colisión).
7. **Partners / plataformas** (Facebook Marketplace, webs de dealer, plataformas de claims como Duck Creek/Insuresoft, LOS de lending como Origence/launcher.solutions) vía API/integración.
8. **Agencias gubernamentales** (títulos/registro).

---

## 2. Cobertura

### Geográfica [V]
- **Estados Unidos** (núcleo) — cubre **prácticamente todos los coches, light trucks y SUV fabricados/vendidos en EE.UU. desde 1981**.
- **Canadá** — vía **CARFAX Canada** (entidad propia): todas las provincias y territorios **excepto Northwest Territories** + datos de EE.UU.
- **Europa continental** — vía **CARFAX Europe** (carfax.eu): se posiciona como "la mayor base de datos internacional de historiales"; datos de **Alemania, Italia, EE.UU. y "muchos otros países"** (enfocado a importaciones/coches con pasado norteamericano y a detectar Tachomanipulation).

### Escala de datos (varias vintages — declarar fecha, ver Gaps) [V]
- **30.000 millones de registros** (PRNewswire, 6-dic-2022).
- **~35–38.000 millones de registros** (cifras 2024-2026 en distintas fuentes: Wikipedia "35B+ / 151.000 fuentes"; búsquedas "38B / 177.000 fuentes"; BIG "36B / 165.000 fuentes").
- **Fuentes de datos: 131.000 (2022) → 151.000 → 165.000 → 177.000** (progresión por año/fuente).
- **6,6 millones de registros cargados al día** (el mayor % = registros de servicio/mantenimiento).
- **CARFAX for Police**: base citada en **29.000 millones** y **6 millones de "tips" nuevos/día**; **5.100+ agencias** comparten datos.

### Scope de vehículos [V]
- **Coches de pasajeros, light trucks y SUV** (turismos/ligeros). Histórico desde **1981** (EE.UU.).
- **Usado** es el núcleo absoluto (historial). Cubre también nuevos en marketplace, pero el producto vive del usado.
- **CPO** (Certified Pre-Owned) marcado como indicador.
- **Sin** vehículo pesado/comercial, moto, RV ni maquinaria como verticales propios (ver Gaps).

---

## 3. Productos + campos atómicos

Arquitectura **datos por VIN → múltiples productos verticales**. Bloques: (A) Vehicle History Report (consumer), (B) History-Based Value, (C) Used Car Listings + marketplace, (D) myCARFAX / Car Care, (E) Buyback Guarantee, (F) CARFAX for Dealers, (G) CARFAX for Lenders, (H) CARFAX Banking & Insurance Group (seguros), (I) CARFAX for Police, (J) CARFAX Canada, (K) CARFAX Europe, (L) API/Partner Connection.

### — BLOQUE A: CARFAX VEHICLE HISTORY REPORT (consumer) —

### 3.1 Vehicle History Report — secciones y campos [V — carvins.net + thompsonsales + indyautoman + support.carfax.com]
Informe por VIN, estándar del sector. **Secciones (orden visual habitual):**

**(a) History-Based Value** (valor estimado VIN-específico, ver §3.4 — encabeza el informe).

**(b) Vehicle Overview / "At-a-glance" summary** (resumen con iconos/checkmarks):
- `vin`, `year`, `make`, `model`, `trim`, `body_style`, `powertrain/engine`
- `number_of_owners` (nº de propietarios)
- `vehicle_usage_type` (personal / lease / corporate-fleet / rental / **taxi** / **police** / commercial / gobierno / driver-ed)
- `last_reported_odometer` (último km/milla reportado)
- `damage_indicators` (resumen de daños)
- Badges resumen (1-Owner, No Accidents, Personal Use, Service History — §3.7)

**(c) Ownership History** (tabla por propietario):
- `owner_number` (Owner 1, 2, 3…)
- `year_purchased` (año de compra de cada propietario)
- `owner_type` / `usage_classification` (personal/lease/corporate/rental/taxi/police)
- `estimated_length_of_ownership` (duración estimada de cada tenencia)
- `state(s)_registered` (estado(s) de matriculación)
- `estimated_miles_driven_per_year` (millas/año estimadas)
- `last_reported_odometer` (por propietario)

**(d) Title History / Title Check** — *title brands* (DMV-issued):
- `salvage_title`, `junk_title`, `rebuilt/reconstructed_title`
- `fire_damage_title`, `flood_damage_title`, `hail_damage_title`
- `lemon/manufacturer_buyback_title`
- `odometer_brand: Not Actual Mileage`, `odometer_brand: Exceeds Mechanical Limits`, `odometer_rollback_indicator`
- `total_loss_record` (title)
- `title_issue_date`, `title_state`
- `lien/loan_record` (gravamen en eventos de título)
- `buyback_guarantee_eligibility` (flag de cobertura — §3.6)

**(e) Additional History — Accident / Damage:**
- `accident/damage_reported` (evento)
- `accident_date`
- `damage_severity` (**minor / moderate / severe**)
- `point_of_impact` / `impact_location` (diagrama del vehículo: front/rear/side/all-over)
- `airbag_deployment` (despliegue de airbag)
- `structural/frame_damage` (daño estructural)
- `total_loss_declaration` (siniestro total de seguro)
- `other_damage` (vandalismo, etc.)
- `damage_type`

**(f) Service / Maintenance History:**
- `service_record_date`
- `service_odometer` (km/milla del servicio)
- `service_description` (oil change, tire rotation, inspección, reparación, neumáticos…)
- `service_facility/dealer/location`
- `well_maintained_indicator`

**(g) Recalls & Safety:**
- `open_safety_recall` (recalls abiertos — nº + detalle)
- `recall_description`
- `nhtsa_safety_ratings` (model-wide)
- `iihs_safety_ratings` (model-wide)
- `warranty_status` (estado/garantía restante)

**(h) Registration & Inspection:**
- `registration_event` (emitida/renovada) + `registration_state`
- `emissions_test` / `safety_inspection` record + resultado

**(i) Theft / Stolen check:**
- `stolen/theft_record`, `stolen_recovery`

**(j) Detailed History** (la sección más extensa — **log cronológico**, columnas):
- `event_date` · `mileage_at_event` · `source_of_record` · `comments/event_description/location`
- Integra: pre-delivery inspections, ventas/compras, accidentes, transferencias de título, lecturas de odómetro, tests emisiones/seguridad, lien info, registros de servicio.

### — BLOQUE B: HISTORY-BASED VALUE (HBV) —

### 3.2 History-Based Value — el producto del scope (`/value/`) [V — support.carfax.com + KBB + AutoRevo + 4-factors + múltiples]
Valoración **VIN-específica**: un valor por coche concreto, **ajustado por su historial documentado** (no un valor "de catálogo" por año/trim). Input: **VIN o matrícula (license plate)**.

**Factores/inputs del modelo:**
- **Atributos del vehículo**: `year`, `make`, `model`, `trim`, `installed_features/options` (CARFAX destaca que muestra el **equipamiento instalado** como transparencia frente a métodos tradicionales), `mileage`, `condition`.
- **Historial VIN-específico (los "4 factores"):**
  1. **Accidents & Damage history** — revisa severidad, tipo de daño, si hubo reparación. *Impacto medio en precio retail: ~$500 si hubo accidente; salta a ~$2.100 de media si hubo daño severo.*
  2. **Service & Maintenance records** — buen historial de servicio → valor más alto.
  3. **Number of owners** — cuántos y cuánto tiempo cada uno (un único propietario de largo plazo = más valor).
  4. **Title history** — flood/salvage/lemon/odómetro bajan el valor de forma significativa.
- **Usage type** (personal/fleet/rental/commercial).
- **Factores de mercado**: `location`, `market_supply`, `season` — **actualizado SEMANALMENTE**.

**Outputs:**
- `carfax_value` (valor $ VIN-específico).
- Ajustes de valor desglosados (por accidente/daño, por title brand, por servicio, por nº propietarios, por usage, por km, por condición, por mercado/ubicación/estación).

### 3.3 Value tool consumer / Trade-In / "Sell my car" (`/value/`, `/sell-my-car/`) [V/A]
- **`trade_in_value`** (valor de tasación; la cifra que un dealer ofrece) — el tool se titula "Find Instant **Trade-In** Value". [V]
- **`instant_cash_offer`** (oferta de cash basada en condiciones de mercado actuales, condición del coche e histórico de ventas; vía "Sell My Car"). [V]
- **`private_party_value`** y **`dealer_retail_value`** — patrón estándar de estos tools (confirmado en Edmunds/KBB), **no verificado explícitamente como output CARFAX**. [A]

### — BLOQUE C: USED CAR LISTINGS + MARKETPLACE —

### 3.4 CARFAX Used Car Listings (`/cars-for-sale`) [V]
Marketplace de usados donde **cada anuncio incluye historial CARFAX** (accidentes, servicio, km, propietarios) + **informe CARFAX gratis por anuncio**. Sobre **151.000+ fuentes**.
- **Campos por anuncio**: `price`, `year/make/model/trim`, `mileage`, `location/dealer`, `photos`, `free_carfax_report_link`, **price-to-market badge (HBV)** (§3.9), **history badges** (§3.7), **dealer rating / Top-Rated** (§3.8).
- **CARFAX Snapshot** (resumen rápido sin abrir el informe completo): `reported_accidents`, `damage + damage_severity`, `open_recall_data`, `last_reported_odometer`, `vehicle_use_type`, `number_of_owners`, `reported_service_history`, indicadores de **well-maintained** y **CPO**.
- **Filtros**: `1-owner`, `no reported damage/accidents`, `with service records`, `personal use` + estándar (precio/año/km/marca/modelo/ubicación).

### — BLOQUE D: myCARFAX / CAR CARE —

### 3.5 myCARFAX / CARFAX Car Care (app iOS+Android, `/Service/`) [V]
App de mantenimiento para propietarios:
- `service_reminders` (recordatorios por email + push: **oil change, tire rotation, safety inspection, emission inspection**).
- `open_recall_alerts` (alerta de recalls abiertos).
- `maintenance_tracking` (almacén automático del historial de servicio).
- `value_tracking` (valor del coche en el tiempo — HBV).
- `favorite_shop` (taller favorito recomendado).
- `find_service_centers` (talleres cercanos por **reviews verificadas**).
- `odometer_update` (actualizar km) + `fuel_efficiency_tracking` (eficiencia de combustible).

### — BLOQUE E: BUYBACK GUARANTEE —

### 3.6 CARFAX Buyback Guarantee [V — support.carfax.com + múltiples]
Garantía: si el informe **NO** muestra un **title brand emitido por DMV** que **sí existía**, CARFAX puede recomprar el coche.
- **Cubre**: Salvage, Junk, Rebuilt, Fire, Flood, Hail, Lemon/Manufacturer Buyback, Not Actual Mileage, Exceeds Mechanical Limits.
- **Condiciones**: el brand debe haberse emitido ≥**60 días** antes del informe; reclamación dentro de **1 año** del informe; el reclamante debe ser dueño al reclamar; debe aportar copia (anverso/reverso) del título branded.
- **Pago**: el **menor** de (i) precio de compra (excl. fees/taxes/garantías/extras) y (ii) **110% de la History-Based Value actual**.
- **NO cubre**: accidentes/daños no reportados, defectos mecánicos, usos no titulados (taxi/ride-share salvo título acorde).

### — BLOQUE F: CARFAX FOR DEALERS —

### 3.7 History badges (consumer + dealer listings) [V]
- **CARFAX 1-Owner** (un solo propietario)
- **No Accidents or Damage Reported**
- **Personal Use** (uso personal)
- **Service History** (registros de servicio)
- **Certified Pre-Owned (CPO)** indicator · **well-maintained** indicator

### 3.8 Programas de dealer [V]
- **CARFAX Advantage Dealer**: dealers suscriptores comprometidos con transparencia → **VHR ilimitados + CARFAX Auction Quick Check + Consumer Information Pack por cada coche retailed**.
- **CARFAX Top-Rated Dealer**: distinción por **reviews de clientes verificadas** (umbral citado **4,7★+**, volumen mínimo, sostenido varios años).
- **Carfax Snapshot** (§3.4) y **History-Based Value** (§3.2) como herramientas de pricing/merchandising para "decenas de miles" de dealers.

### 3.9 Price-to-market badges (HBV en listings de dealer) [V]
Banner de color que compara precio del anuncio vs HBV regional:
- **Great Value** (verde oscuro): precio ≥ **$1.000 por debajo** de la HBV.
- **Good Value** (verde claro): **$0–$999 por debajo** de la HBV.
- **Fair Value**: precio **por encima** de la HBV.

### — BLOQUE G: CARFAX FOR LENDERS (carfaxforlenders.com) —

### 3.10 Productos para prestamistas [V — carfaxforlenders.com vía búsqueda]
Uso a lo largo del ciclo: **lead-gen, underwriting, title research, collections, remarketing, skip tracing**.
- **CARFAX Reports / Vehicle History Report**: valida colateral (tipo y condición), detecta fraude (**odometer rollback**, **title washing**), identifica **último estado de titulación** y **lien info**.
- **History-Based Value**: valor VIN-específico con **transparencia de features instaladas** (protege LTV).
- **VIN Alert**: monitoriza una cartera de VINs en los **50 estados**; **notifica al recibir nuevos registros** (service/title/accident/registration) → localizar colateral / skip tracing.
- **Skip Trace Pro**: **data feed automatizado** para grandes prestamistas / recovery con datos de historial únicos (gestión de cartera de collections).
- **LienGuard**: repositorio central de **información de lienholders** → perfección/liberación de gravámenes; identifica liens existentes.
- **QuickVIN**: **matrícula + estado → VIN decodificado + year/make/model** + acceso a VHR completo.

### — BLOQUE H: CARFAX BANKING & INSURANCE GROUP / SEGUROS (carfaxbig.com, carfaxforclaims.com) —

### 3.11 Productos de seguros [V — carfaxbig.com + carfaxforclaims.com + PRNewswire + Duck Creek]
Aplicaciones: **underwriting/rating, claims fraud detection, material damage assessment, subrogation, total loss valuation, SIU**.
- **Vehicle History Report (insurance)**: severe problems/branded titles, ownership history, potential damage, ownership type, **annual mileage** (info predictiva integrada).
- **Total Loss Valuation Report** (CarfaxForClaims, jun-2019): **pre-accident value** del coche siniestrado vía **HBV VIN-específica** (trim/options/mileage/condition/location + cientos de atributos) + **comparables side-by-side** (year/make/model/trim/options/location/mileage/history desde el marketplace) + **cálculo automatizado de taxes & fees** (mejora 2025).
- **Total Loss File**: eventos de historial que más impactan la valoración de siniestro total, incl. **Insurance Total Loss** (con o sin title brand).
- **Underwriting/Rating Files**: datos para tarificación (con **patentes** de underwriting/rating basado en historial).
- **Claims fraud detection**: detecta **VIN cloning, rate evasion, pre-existing damage** antes de pagar el claim.
- **QuickVIN** (también ofrecido a seguros).
- Integraciones: **Duck Creek** (partner ecosystem), **Insuresoft** (core ecosystem).

### — BLOQUE I: CARFAX FOR POLICE (carfaxforpolice.com) —

### 3.12 Suite investigativa para fuerzas del orden [V — police1 + carfaxforpolice + policemag]
**Gratis** para cualquier agencia; acceso ilimitado a cambio de **compartir datos de colisión** de su jurisdicción. App + web.
- `vin_alerts` (alertas fijadas por agentes en la red CARFAX-police)
- `service_records`, `crash_reports`, `license_plate_data`
- `partial_plate_identification` (identificación por matrícula parcial)
- Alertas: **stolen vehicle**, **odometer inconsistency**, **title washing**
- **Driver Exchange / crash response** (inteligencia en tiempo real)

### — BLOQUE J: CARFAX CANADA (carfax.ca) —

### 3.13 Productos Canadá [V — carfax.ca]
- **Vehicle History Report** (sin lien) · **VHR + Lien Check** (el más completo) · **Bundle 3 VHR + 1 Lien Check**.
- **Campos**: accident/damage history (incl. **glass repairs, police-reported accidents, repair estimates, insurance claims, completed repairs**), open safety recalls, **service records** (date, odometer, services completed), **branding**, **registration**, **stolen vehicle check**, **guaranteed Canadian lien search**, import history (CA/US).
- **Cobertura**: government records de cada provincia/territorio **excepto Northwest Territories** + EE.UU.
- **CPO badge program** (estándares OEM).

### — BLOQUE K: CARFAX EUROPE (carfax.eu) —

### 3.14 CARFAX Europe [V — carfax.eu fetch directo]
"Mayor base de datos internacional de historiales". Comprueba:
- accidentes/daños, mantenimiento/inspecciones, **odometer tampering (Tachomanipulation)**, **import history**, robos, cambios de propietario, **uso taxi/rental**, recalls de fabricante pendientes.
- Tools: **Odometer Check**, **Previous Owners & Usage Type**, free import history, **VIN Decoder** (incl. BMW).
- **ISO 27001** certificado. Pagos: Apple Pay, Google Pay, Maestro, Mastercard, PayPal, Visa.

### — BLOQUE L: API / PARTNER CONNECTION —

### 3.15 Integración de datos [V]
- **CARFAX API / Partner Connection** (developer.carfax.com/partners): llamadas **por VIN**; acceso **restringido a partners aprobados** (acuerdo comercial previo).
- **Facebook Marketplace** (2019): informes CARFAX gratis + filtros por datos del VHR + **CARFAX Snapshot** por anuncio.
- **Webs de dealer** (miles): inyecta información e HBV/pricing en el inventario online.
- **Partners B2B**: LOS de lending (Origence, launcher.solutions), plataformas de claims (Duck Creek, Insuresoft).

---

## 4. Metodología y fuentes de datos [V]
- **Modelo = agregación masiva de eventos reportados por VIN** (NO panel editorial de valores, NO scraping de listings como núcleo). Los registros se **conectan al vehículo concreto vía VIN** y el informe se genera bajo demanda.
- **Volumen**: **30–38 mil millones de registros**; **131.000–177.000 fuentes**; **6,6 M registros/día** (mayor % = servicio/mantenimiento).
- **Fuentes**: títulos y registros estatales (DMV), subastas (auto + salvage), motor vehicle records de Canadá, alquiler/flota, agencias de protección al consumidor, estaciones de inspección estatales, garantías extendidas, **aseguradoras**, bomberos/policía, fabricantes, inspectoras, **talleres de servicio/reparación**, dealers, import/export.
- **History-Based Value**: modelo propietario sobre **millones de listings de usado** + **trim/options/mileage/condition/location + cientos de atributos** + **historial VIN-específico** (accidentes, títulos, servicio, propietarios, usage), **recalculado semanalmente** por supply/season/location.
- **Limitación declarada (honestidad de la fuente)**: reporte **voluntario**. Los **service records aparecen solo del ~20–30% de los talleres**; mantenimiento DIY y muchos mecánicos independientes **nunca aparecen**. CARFAX **no captura accidentes no reportados** a ninguna de sus fuentes (origen del litigio *West v. CARFAX*).
- **Patentes**: underwriting/rating de seguros basado en historial.

---

## 5. Entrega
- **Portal web consumer** (carfax.com): compra de VHR, History-Based Value, Used Car Listings, "Sell my car". [V]
- **Apps móviles**: **CARFAX Car Care / myCARFAX** (iOS+Android), **CARFAX for Police** (iOS+Android). [V]
- **Informe HTML por VIN** (compra unitaria o packs; dealers por suscripción). [V]
- **Portales B2B dedicados**: carfaxforlenders.com, carfaxbig.com, carfaxforclaims.com, carfaxforpolice.com. [V]
- **API por VIN / Partner Connection** (solo partners aprobados con acuerdo). [V]
- **Data feeds automatizados** (Skip Trace Pro = feed de cartera; VIN Alert = notificaciones). [V]
- **Integración en LOS / plataformas de claims** (Origence, launcher.solutions, Duck Creek, Insuresoft) y en **webs de dealer + Facebook Marketplace** (snapshot/badges embebidos). [V]
- **[A]** No se documenta entrega tipo **Excel/CSV bulk autoservicio** para consumidor; el B2B bulk va por feed/integración bajo contrato.

---

## 6. Precio
**Consumer: pago por informe / packs (sin "ilimitado" real para consumidor).** [V — agregadores de precio, contrastado en varias fuentes 2025-2026]

| Plan (consumer) | Precio | Por informe |
|---|---|---|
| **1 informe** | **$44,99** | $44,99 |
| **Pack 3 informes** | **$64,99** | ~$21,66 |
| **Pack 6 informes** | **$99,99** | ~$16,66 |
| "Ilimitado" 60 días | ~$99,99 | rate-limited (no honra ∞ por VIN) |

- **History-Based Value (valor)**: gratis al consultar (consumer) y embebido en marketplace/webs de dealer. [V]
- **Dealers (suscripción)** — estimaciones de 3os: **~$399/mes** (lote ~25 coches) → **~$949/mes** (lote ~250 coches). [A — estimación 3os]
- **CARFAX for Police**: **$0** (a cambio de compartir datos de colisión). [V]
- **B2B Lenders/Insurance**: precio **no público** (contrato/integración). [A]
- **Reventa con descuento**: existe un ecosistema de revendedores que ofrecen el informe oficial más barato ($5–17); no es pricing oficial CARFAX. [V — contexto]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep: mapeo pantalla/sección → dato.

### Vehicle History Report — informe por VIN [V]
- **Cabecera/top**: **History-Based Value** (el valor abre el informe) + **badges resumen** (1-Owner, No Accidents, Personal Use, Service History).
- **At-a-glance summary box** (iconos/checkmarks): nº propietarios, accidentes reportados, registros de servicio, último km, title check, usage — el "semáforo" de un vistazo.
- **Secuencia de secciones**: Overview → **Ownership History** (tabla por propietario: año compra, duración, estado, millas/año) → **Title Check** (brands DMV + odómetro) → **Additional History/Accident-Damage** (severidad minor/moderate/severe + **diagrama de impacto** + airbag + estructural + total loss) → **Service History** (date/odometer/description/facility) → **Recalls + Safety (NHTSA/IIHS)** → **Detailed History** (log cronológico al final: **date · mileage · source · comment**).

### History-Based Value — pantalla `/value/` [V]
- **Cifra central**: `carfax_value` VIN-específico (input VIN/matrícula).
- **Desglose**: los **4 factores** (accidents, service, owners, title) como drivers del valor; **features instaladas** mostradas como transparencia.
- **Trade-In / cash offer**: en `/value/` (trade-in) y `/sell-my-car/` (instant cash offer).

### Used Car Listings — tarjeta de anuncio + VDP [V]
- **Banner de color sobre el precio**: **Great/Good/Fair Value** (price-to-market vs HBV) — elemento visual dominante.
- **History badges** junto al anuncio: 1-Owner, No Accidents, Service History, Personal Use, CPO.
- **CARFAX Snapshot** en el VDP: accidentes, daño+severidad, recalls abiertos, último odómetro, usage, nº propietarios, servicio.
- **Informe CARFAX gratis** enlazado por anuncio + **rating del dealer / Top-Rated**.

### myCARFAX / Car Care — app [V]
- Dashboard por coche: **value tracking** (HBV en el tiempo), **service reminders**, **recall alerts**, historial de servicio almacenado, **favorite shop**, odómetro + fuel efficiency.

### B2B (lenders/insurance/police) [V]
- **Lenders**: HBV + VHR dentro del **LOS** (underwriting); **VIN Alert/Skip Trace Pro** como feed/alertas en el módulo de **collections**; **LienGuard** en title/lien research.
- **Insurance**: **Total Loss Valuation Report** = pre-accident value + **comparables side-by-side** + taxes&fees, dentro de la plataforma de claims (Duck Creek/Insuresoft).
- **Police**: app/web investigativa con VIN alerts, crash reports, license-plate y partial-plate.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **La mayor base de datos de historial por VIN del mundo** (30-38 B registros, 131-177 k fuentes, 6,6 M/día) — estándar de facto del VHR en Norteamérica; barrera de entrada por densidad de fuentes (DMV + talleres + subastas + seguros + policía).
- [V] **History-Based Value = valoración ajustada por el historial CONCRETO de cada VIN** (no por año/trim genérico): cuantifica en **$** el impacto de accidentes (~$500 leve / ~$2.100 severo), title brands, servicio, nº propietarios y usage. Esto es **único**: KBB/Black Book parten de condición/mercado; CARFAX parte del **evento documentado**.
- [V] **Price-to-market embebido (Great/Good/Fair Value vs HBV)** en miles de webs de dealer y en su marketplace — orienta la compra con su propio valor como ancla.
- [V] **Buyback Guarantee** con pago = **110% de la HBV** — garantía monetaria respaldada por su propio dato; ningún competidor de valoración la ofrece.
- [V] **Ecosistema VIN multi-vertical desde el mismo dato**: consumer (VHR+marketplace+app) + dealer (Advantage/Top-Rated/Snapshot) + lenders (VIN Alert/Skip Trace/LienGuard/QuickVIN) + insurance (Total Loss/underwriting/fraud, **patentado**) + **police gratis** (que a su vez **realimenta** crash data). Un volante de datos que se retroalimenta.
- [V] **Total Loss Valuation con pre-accident value + comparables + taxes&fees automáticos** — producto de claims que combina valoración e historial en un único informe.
- [V] **Marca/confianza consumer extrema** (Car Fox; "Show me the CARFAX") — pull B2C que fuerza al dealer a suscribirse.
- [V] **myCARFAX/Car Care** convierte la relación post-venta (recordatorios/recalls/servicio) en captación continua de datos de servicio (lado oferta del volante).

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **No es guía editorial de valores trim-a-trim** (trade/retail/wholesale/residual normalizados como KBB/Black Book/J.D. Power/Autovista): su valor nuclear es **un valor VIN-específico ajustado por historial**, no matrices por versión.
- [V] **Sin valores residuales / forecasting de RV** para leasing/flotas (la depreciación es retrospectiva por evento, no un servicio de residuals forward).
- [V] **Sin TCO / running costs / SMR / tiempos y precios de reparación de pieza** (no compite con Audatex/GT Motive/Mitchell en peritación de daño-coste).
- [V] **Cobertura geográfica = Norteamérica + Europa "de importación"**: fuerte en EE.UU./Canadá; en Europa el foco es coches con pasado norteamericano e historial de importación/odómetro, **no** un censo nativo de cada mercado UE. **Sin España nativa** como producto propio.
- [V] **Vehículos**: solo coches/light truck/SUV; **sin pesado/comercial, moto, RV, maquinaria** como verticales.
- [V] **Dependencia de reporte voluntario**: **service records solo del ~20-30% de talleres**; **accidentes no reportados no aparecen** → riesgo de falsos "clean" (litigio *West v. CARFAX* 2006-2009; caso Boston Globe 2024 de asignación errónea de accidente resistida).
- [V] **Sin un único score numérico de historial** (a diferencia del **AutoCheck Score** de Experian, que da un 1-100); CARFAX da valor + badges + detalle, no un índice comparativo único.
- [V] **API cerrada**: sin autoservicio público; requiere ser **partner aprobado** con acuerdo comercial.
- [V] **Pricing consumer caro y opaco en "ilimitado"** ($44,99/informe; el "ilimitado" está rate-limited) — origen de un ecosistema de revendedores.
- [A] **Transparencia corporativa limitada como unidad**: empleados (~1.500) y facturación (~$300 M / rango $1-10 B) son estimaciones de 3os no consolidadas; CARFAX no publica P&L propio (está dentro de S&P Global Mobility, en proceso de escisión).
- [A] **HBV no auditable externamente**: "cientos de atributos" y pesos propietarios no publicados; el impacto exacto por evento no es reproducible.

---

## 10. Fuentes (URLs)
- https://www.carfax.com/value/ — History-Based Value / "Find Instant Trade-In Value" (producto del scope; redirige a carfax.eu desde egress europeo).
- https://www.carfax.com/vehicle-history-reports/ — Vehicle History Report (secciones/campos).
- https://support.carfax.com/article/what-is-carfax-value-and-how-is-it-calculated/ — cálculo de HBV: year/make/model/mileage/location/condition + accidentes/título/servicio/propietarios/usage; actualización semanal; impacto ~$500/~$2.100.
- https://www.carfax.com/4-factors — los 4 factores (accidents, service, owners, title).
- https://www.carfaxforlenders.com/products/history-based-value · /carfax-vehicle-history-report · /vin-alert · /skip-trace-pro/ · /lien-guard · /quickvin/ · /solutions/collections/ · /about/carfax-data/ — productos lenders + datos.
- https://www.carfaxbig.com/ · /home/insurance · /product/total-loss-file/Insurance · /product/total-loss-report/AutoFinance · /product/underwriting-rating-files/Insurance · /product/vehicle-history-report/Bank — Banking & Insurance Group.
- https://www.carfaxforclaims.com/ — Total Loss Valuation (pre-accident value + comparables + taxes&fees).
- https://www.duckcreek.com/partner/carfax/ y /blog/carfax-joins-duck-creek-partner-ecosystem... — integración claims (underwriting, fraud, total loss).
- https://www.carfaxforpolice.com/ y /tools/investigative-tools/ — suite policial gratis (VIN alerts, crash, plate, partial plate; 5.100+ agencias; 6M tips/día).
- https://www.police1.com/.../spotlight-carfax-digital-tools...free... — CARFAX for Police gratis, 29B registros, acuerdo de compartir crash data.
- https://www.carfax.com/Service/ + https://apps.apple.com/us/app/carfax-car-care/id552472249 + Google Play com.carfax.mycarfax — Car Care: reminders/recalls/value/favorite shop/odometer/fuel.
- https://www.carfax.com/cars-for-sale + https://support.carfax.com/article/what-is-carfax-used-car-listings/ — marketplace, badges, Snapshot, filtros.
- https://support.carfax.com/article/what-is-the-carfax-buyback-guarantee/ — términos Buyback (cobertura, 60 días/1 año, pago 110% HBV).
- https://www.kbb.com/carfax/ y https://www.autotrader.com/carfax — HBV vs KBB (Cox properties).
- https://www.carvins.net/blog/carfax-vs-autocheck-2025... — secciones del informe + comparativa AutoCheck (AutoCheck Score) + precio.
- https://www.indyautoman.com/blog/carfax-vehicle-history-report — secciones del informe (owners, body/engine, NHTSA/IIHS, service, accident, title, recalls, odometer, detailed history) + limitaciones.
- https://www.thompsonsales.com/whats-included-in-a-vehicle-history-report/ — 8 cosas del VHR.
- https://www.prnewswire.com/news-releases/carfax-hits-30-billion-records...301696301.html — 30B registros (dic-2022), 131k fuentes, 6,6M/día.
- https://www.prnewswire.com/news-releases/carfax-delivers-free-vehicle-history-reports-on-facebook-marketplace...300872377.html — integración FB Marketplace (2019) + Snapshot.
- https://www.prnewswire.com/news-releases/new-carfax-total-loss-valuation-service...300863842.html — Total Loss Valuation (jun-2019): pre-accident value + comparables side-by-side.
- https://www.prnewswire.com/news-releases/carfax-receives-patents-for-insurance-underwritingrating-of-vehicles-169221756.html — patentes underwriting/rating.
- https://en.wikipedia.org/wiki/Carfax_(company) — fundación 1984 Columbia MO (Barnett III + Clark), HQ Centreville VA, cadena Polk→IHS→IHS Markit→S&P Global Mobility, 35B+/151k fuentes, US/Canada/Europe, West v. CARFAX, Boston Globe 2024, Car Fox.
- https://investor.spglobal.com/news-releases/.../SP-Global-Announces-Intent-to-Separate-Mobility-Segment... — escisión Mobility (29-abr-2025).
- https://www.autoremarketing.com/ar/technology/carfax-ceo-to-lead-mobility-segment... — Bill Eager CEO CARFAX → presidente/CEO-designate Mobility.
- https://ir.comstock.com/news/.../Comstock-Welcomes-CARFAX-to-Reston-Station/ — reubicación a Reston Station (2025).
- https://www.fool.com/investing/general/2013/06/10/ihs-to-buy-carfax-owner-for-14-billion.aspx — IHS compra Polk/CARFAX ~$1,4B (2013).
- https://www.carfax.ca/vehicle-history/vehicle-history-report + /lien-check + /order — CARFAX Canada (VHR, Lien Check, bundle, campos, cobertura ex-NWT).
- https://www.carfax.eu/de — CARFAX Europe (Tachomanipulation, import, odometer check, VIN decoder, ISO 27001).
- https://developer.carfax.com/partners y https://www.carfax.com/company/partners — API / Partner Connection (acceso restringido a partners).
- Precio: https://vininfohub.com/carfax-report-cost · https://cheapcarfax.net/carfax-cost/ · https://vehicledatabases.com/articles/carfax-report-cost — $44,99 / $64,99 / $99,99; dealer ~$399-$949/mes (3os).
- Datos/metodología: https://snapclaim.com/how-does-carfax-get-its-information/ · https://vehicledatabases.com/articles/how-does-carfax-get-its-information — fuentes, 20-30% talleres, reporte voluntario.
- Geo egress: ipinfo.io → CH/Zürich/Swisscom (explica redirección carfax.com→carfax.eu y 403 en subdominios).

> Verificación: identidad y cadena de propiedad contrastadas con ≥3 fuentes independientes (Wikipedia + S&P Global IR + Auto Remarketing + Motley Fool). Campos del VHR [V] triangulados (carvins.net + indyautoman + thompsonsales + support.carfax.com vía búsqueda US-only). HBV [V] de support.carfax.com + KBB + AutoRevo + 4-factors. Productos B2B [V] de carfaxforlenders/carfaxbig/carfaxforclaims (vía búsqueda) + Duck Creek + PRNewswire. Precios [V] de múltiples agregadores 2025-2026. Discrepancias (escala de registros/fuentes por vintage, empleados, facturación, HQ Centreville vs Reston, private/retail value en el tool) marcadas explícitamente; **ninguna inventada**. Bloqueo de fetch directo a dominios CARFAX (geo-redirección a EU + 403 anti-bot desde egress suizo) declarado y compensado.
