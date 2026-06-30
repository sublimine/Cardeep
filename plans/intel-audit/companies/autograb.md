# AutoGrab — Auditoría atómica

> **slug:** `autograb` · **subdominio de audit:** `market-intelligence` · **web:** https://www.autograb.com.au/
> **Fecha auditoría:** 2026-06-30 · **Doctrina:** cada campo lleva fuente; `[VERIFICADO]` lo leído, `[NO-VERIFICADO]` lo no confirmado; nada inventado.
> **Veredicto express:** AutoGrab es la **plataforma de inteligencia automotriz API-first** nacida en Melbourne (2020), hoy
> escalando a UK/Europa tras una **Serie B de A$80M a valoración A$230M (ene-2026)**. Su foso NO es un panel de tasación clásico:
> es **la mayor base independiente de Australia de TODO coche listado online**, recolectada de marketplaces (carsales, gumtree,
> autotrader, drive, tradingpost…) y **actualizada "cada segundo"**, sobre la que corre un **modelo ML de precios (retail + trade)
> recalibrado a diario/semanal** que devuelve valor + **confidence score 0-1** + **bandas upper/lower** vía REST. Cubre todo el
> ciclo del dealer (sourcing → valoración → recompra de cliente → venta) y domina el **seguro** (90%+ de las aseguradoras AU usan
> su dato para total loss / PAV). Patrón directo a copiar para cardeep: **dato de mercado (no anuncio aislado) → modelo →
> ficha de coche con valor+banda+confianza + "Market Overlay" lateral de comparables + widgets embebibles + reporte AIR (PDF/Excel)
> con Days-to-Sell y Retained Value%**. El **AGID** (identificador canónico de vehículo, color-agnóstico) es su llave de catálogo.

> **Aviso de desambiguación:** este informe cubre **AutoGrab Pty Ltd** (autograb.com.au / autograb.co.uk, automoción, ABN
> 79 638 468 569). NO confundir con: el competidor australiano **AlgoDriven** (ver `alg.md`), ni con **Datium Insights** (Pickles,
> ver `datium-insights.md`), ambos citados como competidores. "AutoGrab" también es el nombre de su app móvil (iOS/Android). Marcas
> subsidiarias propias: **CarAnalysis** (caranalysis.com.au) y **ValueMyCar** (valuemycar.com.au, B2C). [VERIFICADO ≥2: about-us, CB Insights]

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | **AutoGrab** (AutoGrab Pty Ltd) | [VERIFICADO] |
| ABN | **79 638 468 569** | [VERIFICADO: about-us] |
| Grupo / owner | **Independiente, respaldado por VC** (no pertenece a un grupo industrial; es scale-up) | [VERIFICADO ≥2: about-us, CB Insights] |
| Fundación | **2020** (incorporación; producto escalado ~2021-2022) | [VERIFICADO ≥2: CB Insights, SmartCompany] · ⚠ TEN13 describe "lanzamiento ~2022" |
| HQ | **10 River Street, South Yarra, Victoria 3141, Australia** (Melbourne) | [VERIFICADO ≥2: CB Insights, SmartCompany] |
| Oficinas (5) | **Melbourne (HQ), Sídney, Auckland (NZ), Kuala Lumpur (MY), Londres (UK)** | [VERIFICADO: about-us] |
| Empleados | **120+ globales** ("100% employee recommendation rate") | [VERIFICADO: about-us] |
| Financiación total | **~US$58,6M** acumulado (incl. Serie B) | [VERIFICADO: CB Insights] |
| Serie B | **A$80M a valoración A$230M**, anunciada **27-ene-2026** | [VERIFICADO ≥2: autograb PR, SmartCompany] |
| Inversores Serie B | **Octopus Ventures (UK, lead)** + **Movac (NZ, lead)** + **Premier Capital Partners** + **EVP / Equity Venture Partners** (existente) + **TEN13** (existente) | [VERIFICADO ≥2: autograb PR, CB Insights, TEN13] |
| Email / tel | contact@autograb.com.au · **1800 531 718** | [VERIFICADO] |
| Posicionamiento | "**Australia's Automotive Intelligence Platform**" · visión "Drive the Future, Intelligently" | [VERIFICADO ≥2: home, about-us] |

**Equipo / liderazgo** (about-us) [VERIFICADO]:
- **Daniel Werzberger** — Co-CEO & Co-Founder (AU). Antes fundó **areyouselling.com.au** (~A$30M/año, vendida a **Eclipx Group** en 2017); en automoción desde 2012.
- **Chris Gardner** — Co-CEO & Co-Founder (UK-based; lidera expansión británica). Ex Loke Digital / SugarUX.
- **Michael Kapel** — COO · **Stewart Bird** — CPO · **Steven Bearzatto** — CTO · **Raph Hennessy** — Head of Engineering · **Saxon Odgers** — CCO.

### Categorías de producto (15 productos comercializados + suite API)
1. **Realtime Pricing (RTP)** — app de tasación retail/trade en vivo (núcleo dealer).
2. **Sourcing** — buscador multi-marketplace de stock para comprar.
3. **AutoGrab Pricing / Valuation** — motor de valoración ML (API).
4. **Future / Residual Valuation** — valor futuro y curva de depreciación.
5. **AutoGauge** — indicador/gauge de precio vs mercado (API + iFrame).
6. **Market Overlay / Market Insights Snapshot** — comparables de mercado (panel + widget).
7. **Delve** — plataforma self-service de exploración de datos + lenguaje natural.
8. **AutoMate** — "ChatGPT para coches" (LLM sobre su catálogo + datos).
9. **AIR / AIR Pro** — Automotive Insights Report (PDF/Excel).
10. **EV Pulse** — tracker diario del mercado EV usado AU.
11. **Customer Recapture** — detecta cuándo un cliente pasado revende su coche.
12. **Pipeline** — DMS/lead pipeline con inteligencia de mercado.
13. **Dealer Direct / Prospects / Appraisals** — sourcing/leads/tasaciones para dealer.
14. **CarAnalysis** — reporte PDF de historial+valor (marca propia; PPSR).
15. **Insurance suite (PAV / AutoPAV / Repair Decision)** — total loss y reparar-vs-siniestrar.

### Cliente objetivo
**Dealerships (concesionarios)**, **Insurance Providers (aseguradoras)**, **Lenders (financieras/bancos)**, **Fleet Operators (flotas)**,
**Wholesalers (mayoristas)** y **marketplaces** (clientes especiales). Clientes/partners nombrados: **Tony White Group**, **Western Ford**
(Sid Cetindag), **Commonwealth Bank** (partner 2025, 10M+ clientes banca retail), **LMG** (préstamos auto), **Westside Auto**, **Berwick
Jeep / Berwick Motor Group** (ejemplos de widget). 35 logos de partner sin nombrar en carrusel. [VERIFICADO ≥2: about-us, partnerships, autograb PR, brokernews]

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Regiones operativas (valoración) | **Australia (`au`), Nueva Zelanda (`nz`), Reino Unido (`uk`), Malasia (`my`)** | [VERIFICADO: Integration Overview, enum `region`] |
| Presencia/oficinas adicionales | **Filipinas (Manila)** citada como región operativa en home | [VERIFICADO: home] |
| Cobertura de datos/foto | Stock-photos enum incluye además **de, fr, be, it, lu, nl, es** (Europa) | [VERIFICADO: stock-photos OpenAPI enum] |
| "55 países" (API) | Claim de marketing de cobertura de datos en home | [VERIFICADO: home] · marketing, no = valoración |
| Estados AU | NSW, NT, QLD, SA, TAS, VIC, WA, ACT (rego requiere estado; valoración **state-based o nacional**) | [VERIFICADO: registration-plate-search, `state_for_pricing`] |
| Scope nuevo/usado | **Usado = núcleo** (precios de anuncios reales de marketplaces). **Nuevo**: RRP de catálogo + punto de partida de residual | [VERIFICADO: valuation-approach] |
| Tipos de vehículo | **Vehículos de pasajeros** (coche/SUV/ute/van ligera) — único catálogo con AGID y valoración | [VERIFICADO: upstream-vehicle-search] |
| Excluidos del catálogo | **Motos, caravanas, camiones pesados**: solo lookup "upstream" de la autoridad de matriculación, SIN AGID ni valoración | [VERIFICADO: upstream-vehicle-search] |
| Marcas | **500+ marcas/clientes** usan AutoGrab (home); catálogo cubre todas las marcas listadas en cada región (Facets devuelve el set completo: Abarth→Aston Martin→… por región) | [VERIFICADO: home, facet-search] |
| Base de datos | "**La mayor base independiente de Australia** que cubre TODO vehículo listado a la venta online", **actualizada cada segundo** | [VERIFICADO ≥2: TEN13, home/api] |
| Marketplaces fuente | carsales.com.au, gumtree.com.au, autotrader.com.au, drive.com.au, tradingpost.com.au (entre otros) | [VERIFICADO: market-overlay/history payloads] |
| Penetración AU | **1.000+ dealerships (~25% del mercado nacional)**; **90%+ de aseguradoras AU** usan su dato para total loss | [VERIFICADO ≥2: autograb PR, SmartCompany] |
| Build data | **40 fabricantes**, vehículos **desde 1999** (Audi, BMW, Mercedes, VW, Ford, Hyundai, KIA…) | [VERIFICADO: factory-build-data] |
| EV Pulse | EV usado AU **model years 2021-2025** | [VERIFICADO: ev-pulse] |

---

## 3. Productos + campos atómicos

> El contrato técnico se reconstruyó del **corpus completo de developer docs** (`devhub.autograb.com/llms-full.txt`, 8.173 líneas,
> AU+UK+NZ+MY) leído verbatim. Base API: `https://api.autograb.com.au/v2/` (AU) y `https://api.autograb.co.uk` (UK). Auth: header
> `ApiKey` (sec_/pub_) u OAuth bearer. OpenAPI 2.0. Rate-limit + cuota mensual por contrato.

### 3.0 AGID — AutoGrab ID (la llave canónica)
Identificador único de vehículo (ej. `3583316061320587`). Un VIN mapea a exactamente 1 AGID; todos los coches de igual make/model/spec
comparten AGID. **El color NO es factor del AGID.** Es la fuente canónica de metadatos de toda la plataforma. [VERIFICADO: FAQ]

### 3.1 Vehicle Search / Discovery — resolución a AGID
Métodos: **Plain-text** (`/v2/vehicles?search=`), **Registration Plate** (`/v2/vehicles/registrations/{plate}?state=`), **VIN**
(`/v2/vehicles/vins/{vin}`), **Facet** (drop-downs), **Vehicle ID**, **Marketplace ID** (lead propio del marketplace), **VIN→Registration**
(reverse), **Upstream** (lo que dice la autoridad, sin AGID). [VERIFICADO: vehicle-search/*]

**Objeto `vehicle` (campos atómicos)** [VERIFICADO: payloads]:
`id` (AGID), `legacy_id`, `region`, `title`, `year`, `make`, `model`, `badge`, `series`, `model_year`, `release_month`, `release_year`,
`body_type`, `body_config` (ej. Dual Cab), `body_config_type`, `body_style`, `drive` / `drive_type`, `engine` / `engine_type`,
`fuel` / `fuel_type`, `transmission` / `transmission_type`, `wheelbase` / `wheelbase_type`, `roof_type`, `num_doors`, `num_seats`,
`num_gears`, `num_cylinders`, `capacity_cc`, `power_kw`, `torque_nm`, `range` (km), `weight_kg`, `battery_kwh`, `options[]`.
Envoltorio: `vin`, `colour`, `upstream_vehicle` (descripción de la autoridad), `confidence` (`standard`…), `additional_vehicles[]`,
`plate_module{plate, plate_state}`, `total`/`count`. **Facets disponibles:** `year, make, model, badge, series, transmission, body,
body_style, fuel, engine, wheelbase` (cada uno devuelve `value`+`count`).

**Plate/registration status:** `registration_status` (REGISTERED…), `registration_expiry`, `manufacture_year`, `compliance_plate`, `incidents[]`.

### 3.2 Vehicle Search Features (add-ons de enriquecimiento)
Comma-separated en `features=`. Cada feature un payload atómico [VERIFICADO: vehicle-search-features]:
- `extended_data`: `body_type_description`, `color_description`, `engine_number`, `make_code`, `make_description`, `model_code`, `model_description`, `vehicle_type_description`.
- `additional_upstream_data`: vin, year, make, model, badge, series, fuel_type, body_style, transmission, capacity_cc, colour, title.
- `vehicle_age`: `compliance_plate`, `year_of_manufacture`.
- `writeoff_info`: `incident_list[{code, damage_codes, jurisdiction, recorded_date, type_code}]` (ej. "Repairable Write-off", "Collision").
- `stolen_info`: `incident_list[{incident_type, jurisdiction, reported_date, summary}]`.
- `performance_info`: `power_kw`, `weight_tonnes`, `power_to_weight_ratio`.
- `registration_status`: `expiry_date`, `status`.
- `build_data`: `vin, make, model, features[{code, value}], build_date`.
- `vehicle_summary`: descripción narrativa generada (marketing/UX).

### 3.3 Detailed Specifications (powered by JATO)
`/v2/vehicles/{id}/detailed-specs` (catálogo `autograb` o `jato`). Devuelve `specs[]` con `{category, id, description, value, int_value, location}`.
**Contenido bespoke por contrato.** Categorías observadas: **Weights** (`kerb_weight`, `tare_weight`), **Version** (Make, Model, Version,
Body type, Seating capacity), **Equipment** (Air Conditioning type, Front/rear power windows con flag `S` y `location` `F`). [VERIFICADO: detailed-specifications-data]

### 3.3-UK Datos extendidos UKVD/DVLA (región `uk` — set mucho más rico)
[VERIFICADO: UK vehicle search extended payload]:
- DVLA: `vehicle_identification_number`, `dvla_manufacturer_desc`, `dvla_model_desc`, `dvla_wheelplan`, `dvla_body_desc`, `dvla_fuel_desc`, `registration_date`, `first_registration_date`, `used_before_first_registration`, `manufactured_year`, `v5c_qty`, `date_v5c_issued`, `engine_number`, `prior_ni_vrm`.
- `vehicle_status_details`: `is_non_eu_import`, `is_imported`, `certificate_of_destruction_issued`, `is_exported`, `exported_date`, `is_scrapped`, `scrapped_date`.
- `vehicle_excise_duty_details` (road tax): `co2_gkm`, `dvla_co2_band`, `12_month_rfl_y1`, `6_month_rfl_y2_to_y6_premium`, `12_month_rfl_y2_to_y6_premium`, `6_month_rfl_y2_to_y6`, `12_month_rfl_y2_to_y6`.
- `colour_details`: `colour`, `colour_changes_qty`, `original_colour`, `last_colour`, `date_of_last_colour_change`.
- `keeper_change_list`: `number_previous_keepers`, `date_of_last_keeper_change`. + `plate_change_list`.
- `model_data`: `ukvd_variant_code`, `manufacturer_desc`, `model_range_desc`, `model_desc`, `model_variant`, `ukvd_series_desc`, `ukvd_mark`, `model_start_date`, `model_end_date`, `emission_class`, `country_of_origin`, `ukvd_fuel_type_desc`, `cab_type_desc`, `type_approval_category`, `market_sector_code`, `vehicle_type`, `vehicle_taxation_class`.
- `body_details`: `ukvd_body_shape`, `ukvd_body_type_desc`, `fuel_capacity_litres`, `number_axles`, `number_doors`, `number_seats`, `payload_volume_square_metres`, `wheelbase_type_desc`, `platform_desc`, `is_platform_shared`.
- `dimensions`: `vehicle_height_mm`, `vehicle_length_mm`, `vehicle_width_mm`, `vehicle_wheelbase_mm`, `load_length_mm`.
- `weights`: `min_kerbweight_kg`, `gross_trainweight_kg`, `unladen_weight_kg`, `payload_weight_kg`, `gross_vehicleweight_kg`, `gross_combined_weight_kg`.
- `power_source`: `power_source_vehicle_type` (ICE/EV); `ice_details{engine_family, engine_stroke_mm, valves_per_cylinder, aspiration, number_cylinders, engine_location, cylinder_arrangement, valve_gear, ukvd_engine_desc, engine_bore_mm, engine_manufacturer, fuel_delivery, power_delivery, engine_capacity_cc, engine_badged_size_litres}`; `electric_details`.
- `euro_ncap`: `ncap_overall_rating`, `ncap_child_occupant_protection_percentage`, `ncap_adult_occupant_protection_percentage`, `ncap_pedestrian_protection_percentage`, `ncap_safety_assist_percentage`.
- `emissions`: `is_fuel_catalyst`, `co2_gkm`.
- `performance.torque`: `torque_nm`, `torque_lbft`, `torque_rpm`, `torque_derived_from`. `performance.power`: `power_bhp`, `power_ps`, `kilowatt`, `power_rpm`. `performance.statistics`: `0to60_mph`, `0to100_kmph`, `max_speed_kmh`, `top_speed_mph`.
- `fuel_economy`: `nedc_extra_urban_litres_100km`, `nedc_extra_urban_mpg`, `nedc_extra_urban_cold_litres_100km`, `nedc_extra_urban_cold_mpg`, `combined_litres_100km`, `combined_mpg`.
- `sound_levels`: `stationary_soundlevel_db`, `stationary_soundlevel_rpm`, `driveby_soundlevel_db`.
- `transmission`: `driving_axle`, `number_gears`, `transmission_type`, `drive_type_desc`.

### 3.4 Factory Build Data + Factory Fitted Options (FFO)
- **Build Data** (`/v2/vehicles/vins/{vin}/build-data`): `features[{code, value}]`, `build_date`. 40 OEMs, desde 1999. [VERIFICADO]
- **FFO** (UK, `/v2/vehicles/fitted_options`, JATO + ML): por opción `build_sheet_lines[]`, `option_id` (JATO), `option_code` (JATO), `option_title`, `option_details`, `match_score` (0.6-1), `match_category` (Matched / Included|Required|Price changed by <opt> / recursively / Prerequisites Met), `msrp` (precio opción). [VERIFICADO: factory-fitted-options]

### 3.5 Sourcing — Market Overlay (comparables de mercado) — NÚCLEO market-intelligence
`/v2/sourcing/market_overlay/{vehicle_id}`: comparables actualmente listados o recién vendidos (best-effort ≥4; ventana 60 días +10 hasta cuota).
**Params:** `vehicle_id`, `minimum_days` (60), `include_adjacent_years`, `exclude_outliers`, `exclude_all_delisted`, `include_all_active`,
`include_trash` (+`tag_ids` para trash/damaged/written-off), `odometer_range_min/max`, `features`, `region`. [VERIFICADO: market-overlay]
**Features (campos atómicos por lead/comparable):**
- `dealer_contact_details`: `contact_name`, `contact_number`.
- `lead_starting_price`: `starting_price`. · `lead_price_drops`: `price_drop_count`.
- `vehicle_rrp`: `price_when_new`.
- `listing_details[{source, url, price, drive_away_price, price_before_govt_charges, price_includes_govt_charges}]`.
- `listing_urls[{source, url}]` · `primary_description`.
- `cover_image` (`cover_image_url`, 90 días tras delisting) · `all_images[]`.
- `rego`, `VIN`, `stock_no`.
- `avg_kms` (`avg_odo`, `avg_kms`) · `avg_price`.
- **Market Statistics** (`/v2/sourcing/market_overlay/statistics/{vehicle_id}`): estadísticas agregadas del overlay (precio/odómetro medios, tamaño de muestra), mismas features. [VERIFICADO: market-statistics]

### 3.6 Vehicle History — historial de listings (rollback detector)
`/v2/sourcing/history` (VIN, o year+make+model+rego+state). `events[{type, odometer, price, marketplace, seller_type, timestamp}]`
con `type` = **`listing` / `delisting` / `price_change`** (delisting ≈ venta). Features: `price_changes` (subidas/bajadas), `listing_sources[]`,
`listing_urls[{source,url}]`, `primary_description`, `all_images` (5 primarias). Combina **odómetro de transacción Y de servicio** →
**detección de rollback de cuentakilómetros** ("best rollback detector in Australia"). [VERIFICADO ≥2: vehicle-history, sourcing-tools]

### 3.7 Valuation — motor de precio (retail + trade + max offer)
`POST /v2/valuations/predict` (también `/registrations/{rego}`, `/vins/{vin}`). [VERIFICADO: valuation-predict]
**Inputs:** `vehicle_id` (req), `region`, `kms` (si falta → media del modelo), `condition_score` (1-5), `state_for_pricing`
(estatal vs nacional), `rrp_overwrite`, `rrp_adjustment`, `rego`, `state`, `vin`, `features[]` (`bounds`, `equity`).
**Output `prediction`:** `id` (pricing id), `vehicle_id`, `created_at`, `kms`, `price`, `score` (**confidence 0-1**), `retail_price`,
`trade_price`, `adjustment`. **`bounds`:** `retail.lower/upper`, `trade.lower/upper`. **`equity`:** `positive_equity`, `equity_position`.
**`max_offer`:** `reconditioning`, `profit_margin`, `lot`, `transport`, `admin`, `price`.
**`adjustment` (regla):** `type` (account/vehicle/pricing_record), `enabled`, `trade_adjustment`, `retail_adjustment` (fixed/percentage),
`overrides[{min_kms, max_kms, trade_price, retail_price}]`.
**Tipos de valor (conceptuales):** **Private Sale Price**, **Dealer Sale Price**, **Estimated Retail**, **Estimated Trade**
(fórmula derivada del retail), **Max Offer** (% de descuento configurable sobre retail). [VERIFICADO: valuation-approach]
**Escala condición:** 1 Poor · 2 Fair · 3 Average · 4 Good · 5 Excellent.
- **Condition Array** (`/predict/conditions`): `conditions[{condition_score, trade_price}]` para 1-5 + `bounds.trade` por condición.
- **History:** `/v2/valuations/history/{PRICING_ID}` (recuperar) y `/v2/valuations/history` (lista paginada) + Price Changes API.
- **Max Offer Configuration** (`GET/PUT /v2/valuations/max_offer_configuration`): set de reconditioning/profit/lot/transport/admin.

### 3.8 Residual Valuation — valor futuro / curva de depreciación
`POST /v2/valuations/residual`. Inputs: `vehicle_id` (req), `region`, `initial_kms` (0), `yearly_kms` (req, 10000), `rrp_overwrite`,
`rrp_adjustment`, `color`. Output `predictions[{year, kms, valuation, score}]` (típ. 0-5 años). Usa tendencias de mercado actuales para
moldear la curva de depreciación de coches nuevos. Métrica clave derivada: **Retained Value % vs RRP**. [VERIFICADO ≥2: residual-valuations, api-future-valuation, ev-pulse]

### 3.9 AutoGauge — gauge/indicador de precio vs mercado
`POST /v2/valuations/gauge/`. Inputs: `region`, `odometer`, `listing_price`, `vehicle_id` | `vin` | `rego`+`state` | `marketplace`+`marketplace_id` | `vehicle_description`.
Output `gauge`: `id`, `fill` (0-1, posición en banda), `listing_price`, `market_range_min`, `market_range_max`, `confidence`, `sample_size`, `vehicle_title`. [VERIFICADO: gauge-api]

### 3.10 Embeddables (iFrame)
- **Gauge Widget** (`gauge.autograb.com.au`): valuation + market data; params `api_key, region, odometer, listing_price, layout (horizontal/vertical)` + tipo de vehículo. Eventos `AUTOGRAB_GAUGE_SHOW/HIDE`.
- **Valuation Widget** (`offer.autograb.com.au`): journey de **instant cash offer** que captura lead, auto-rellena coche, hace pregunta + oferta condicional según estrategia de precio. Eventos `AUTOGRAB_VALUATION_SUCCESS/ERROR/HIDE/DIMENSIONS/COMPLETE`. Lead → email o LMS.
- **Market Overlay Widget / Market Insights Snapshot**: insights de marketabilidad regional (auto-search por descripción+odo o selección manual). Eventos `AUTOGRAB_INSIGHTS_*`. [VERIFICADO: embeddables/*]

### 3.11 Stock Photos / Image Library
`/v2/vehicles/{id}/photos` (region au,nz,uk,my,de,fr,be,it,lu,nl,es). `images[{type (stock/generated), color, url, match_confidence (high/medium/low)}]`. Color por defecto: white. [VERIFICADO: stock-photos]

### 3.12 Reports — CarAnalysis / Certificates / PPSR
- **CarAnalysis** (`POST /v2/reports/car-analysis`, async, GET tras ≥20s): PDF modular. Identificación (VIN, rego+state, odometer);
fuente de valor por prioridad (Price Record ID → Lead ID → odometer); `brand` (white-label); campos marketplace (Marketplace Image URL,
Marketplace Price, Marketplace Price Type). **`sources` (módulos):** PPSR, **Vehicle Details**, **Odometer History** (resalta posibles
**rollbacks**), **Build Data**, **Fitted Options** (no disponible aún), **Valuation**. [VERIFICADO: car-analysis]
- **Certificate object** (CarAnalysis/PPSR): `id`, `vin`, `rego`, `rego_state`, `url` (PDF), `certificate_created_at`, `year`, `make`,
`model`, `body_type`, `colour`, **`has_safety_recalls`, `has_secured_parties`, `has_stolen_records`, `has_written_off_records`**.
- **PPSR** (federal): mismo objeto + updates `has_expired`, `has_changed`. [VERIFICADO: ppsr]

### 3.13 Customer Recapture — recompra de cliente
Sube clientes y avisa cuando revenden. `customer`: `id`, `last_updated`, `rego`, `state`, `vin`, `external_id`, `sale_date`,
`monitor_start_date`, `monitor_end_date`, `vehicle_title`, `additional_fields{}`, **`sightings[{at, lead_id, listing_url, listing_title,
listing_price, seller_type}]`**. Upload: `name`, `enable_rego_lookups`, totales (`total_uploaded/processed_customers`, `total_errors`).
**Webhooks:** `recapture_new`, `recapture_price_change`, `recapture_delist`, `claim_report_generated`, `ping`. [VERIFICADO: recapture, webhooks]

### 3.14 Insurance — PAV / AutoPAV / Repair Decision
- **PAV** (`POST /v2/insurance-claims/`): genera assessment de **Pre-Accident Valuation** para **total loss**; se ve en web app
`app.autograb.com.au/insurance-claims/<claim-id>`. Webhook `claim_report_generated` → `{claimID, claimNumber, claimValuation, reportURL}`.
- **AutoPAV** (`/v2/insurance-claims/autopav`): PAV 100% automatizado por API.
- **Repair Decision** (`/v2/repair-decisions/`): decisión reparar-vs-siniestrar. [VERIFICADO: insurance/*]

### 3.15 Pipeline + Stock Feeds + DMS
`POST /v2/stock` (stock feed), `POST /v2/external-enquiry/...` (enquiry externa con `enquirer{first_name,last_name,email,mobile}` +
`vehicle{make,model,badge,series,year}` + `rego/vin/stock_number/comment`), `upsert-external-dms`. Muestra el dato del cliente junto a
inteligencia de mercado. [VERIFICADO: pipeline/*, stock-feeds]

### 3.16 AIR / AIR Report Pro — informe de mercado (PDF/Excel)
**AIR = Automotive Insights Report.** Secciones/métricas [VERIFICADO: air-report-pro]:
- **Market Volume & Inventory:** volúmenes Dealer / Private / Demo; desglose por estado AU; filtro por Make, Model, Year, Fuel Type (ICE/Hybrid/EV); Segment Analysis.
- **Pricing & Valuation** (coches hasta 10 años): **Weighted Retained Value** (por Make/Model/Fuel Type); **Retention by Segment** (curvas de depreciación por clase).
- **Velocity & Performance:** **Days to Sell (DTS)** (hasta 10 años); **Performance Benchmarking** (velocidad de venta del dealer vs media nacional/estatal por Segment y Model).
- Entrega: **PDF** (presentación) + **Excel** (datos crudos). Pro añade desglose granular estatal + lenguaje natural (vía Delve).

### 3.17 Delve — exploración self-service + lenguaje natural
Plataforma de datos: (1) **Benchmarking & Market Comparisons**, (2) **Pricing & Sales Trend Analysis** (movimientos de precio, fluctuación
de oferta, time-to-sell), (3) **Custom Data Exploration**, (4) **AI-Driven Insights** (detección automática de cambios de mercado). Consulta
en **lenguaje natural** ("What were SUV sales like over the past 12 months?"). [VERIFICADO: delve]

### 3.18 AutoMate — "ChatGPT para coches" (LLM)
Chatbot LLM sobre catálogo + modelos de valoración + datos de mercado. Casos: tendencias de mercado, valoraciones básicas, comparaciones,
noticias/ofertas. **Disclaimer explícito**: respuestas ilustrativas/agregadas, no point-in-time; remite a Realtime Pricing/Catálogo/AIR para
precisión. Convierte procesos "de horas a segundos". [VERIFICADO: automate-usage-guidance, autograb PR]

### 3.19 EV Pulse — tracker EV diario (B2C/marketing)
EV usado AU (2021-2025), 3 métricas: **Supply & Demand**, **Retained Value % movement**, **Days to Sell**. Suavizado 7 días, **update
diario**. Dashboard en vivo + "Australian Used EV Market Report" descargable. [VERIFICADO: ev-pulse]

---

## 4. Metodología y fuentes de datos

| Aspecto | Detalle | Estado |
|---|---|---|
| Naturaleza del dato | **Precios de ANUNCIO (asking price)** de marketplaces — activos + recién delistados — no precio de transacción confirmado | [VERIFICADO: valuation-approach, FAQ] |
| Fuente | **La mayor base independiente AU** de todo coche listado online; scraping multi-marketplace (carsales, gumtree, autotrader, drive, tradingpost) | [VERIFICADO ≥2: TEN13, payloads] |
| Frescura | "Actualizada **cada segundo**"; modelo de precio **recalibrado semanalmente** con **ponderación por recencia** | [VERIFICADO ≥2: TEN13, valuation-approach] |
| Modelo | **Machine Learning** que captura relaciones no-lineales atributo→precio; trade derivado por fórmula del retail | [VERIFICADO ≥2: autograb-pricing, valuation-approach] |
| Confidence score | **0-1**; factores: (1) nº de coches listados últimos **365 días** para ese tipo, (2) análisis de exactitud del algoritmo. >0.8 alta / 0.5-0.8 media / <0.5 baja. Excluye listings de mala calidad (sin km/precio) | [VERIFICADO ≥2: autograb-confidence-score, FAQ] |
| Supuestos de valor | Incluye GST, excluye government charges; asume **buena condición + accesorios OEM estándar**; private excluye márgenes dealer | [VERIFICADO: valuation-approach] |
| Specs de tercero | **JATO** (detailed specs + FFO); **DVLA + UKVD** (UK); **NEVDIS** (AU rego/write-off/stolen); **PPSR** (gravámenes federal) | [VERIFICADO: detailed-specs, UK payload, registration-plate-search, ppsr] |
| Granularidad valor | AGID (make→model→variante) × km × condición(1-5) × estado (estatal vs nacional) × RRP override | [VERIFICADO: valuation-predict] |
| Test/calidad | Test cases zero-cost (REG4SUCCESS, VIN 000…, AGID 111…) para integración no facturable | [VERIFICADO: api-test-cases] |

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **REST API** | API-first; OpenAPI 2.0; `api.autograb.com.au/v2` (AU) / `api.autograb.co.uk` (UK); ApiKey + OAuth; rate-limit headers + cuota mensual | [VERIFICADO: integration-overview] |
| **Web app** | `app.autograb.com.au` — Realtime Pricing, leads, Market Overlay lateral, PAV (`/insurance-claims/<id>`) | [VERIFICADO ≥2: market-overlay, PAV] |
| **App móvil** | iOS (App Store) + Android (Play) | [VERIFICADO: home] |
| **Embeddables iFrame** | Gauge Widget, Valuation Widget (instant cash offer), Market Insights Snapshot | [VERIFICADO: embeddables] |
| **Reportes PDF** | CarAnalysis (white-label), PPSR, PAV report | [VERIFICADO: reports] |
| **PDF + Excel** | AIR / AIR Pro (informe de mercado) | [VERIFICADO: air-report-pro] |
| **Dashboard** | Delve (self-service + NL query), EV Pulse (live) | [VERIFICADO: delve, ev-pulse] |
| **Webhooks (push)** | recapture_new/price_change/delist, claim_report_generated, ping | [VERIFICADO: webhooks] |
| **Stock feeds / DMS** | `/v2/stock`, external-enquiry, upsert-external-dms (Pipeline); leads vía email o LMS | [VERIFICADO: stock-feeds, pipeline] |
| **Chat (LLM)** | AutoMate dentro de la app | [VERIFICADO: automate] |
| **Status** | status.autograb.com.au | [VERIFICADO] |

---

## 6. Precio (modelo)

| Producto | Modelo | Estado |
|---|---|---|
| Core (Pricing, Sourcing, API…) | **Contact-sales / demo** (sin tarifas públicas); prueba "Free Valuation" + "Schedule a Demo" | [VERIFICADO: autograb-pricing] |
| API | Cuota mensual + rate-limit **por contrato**; features por permiso comercial; lookups rego/VIN con **fee adicional** | [VERIFICADO: integration-overview, gauge-api] |
| **AIR Report Pro** | **Gold A$833/mes (A$9.996/año)** National Report · **Platinum A$2.000/mes (A$24.000/año)** incl. Delve + NL query | [VERIFICADO: air-report-pro] |
| Gratuito (lead-gen/B2C) | ValueMyCar (B2C), Free Valuation, EV Pulse dashboard, test cases API no facturables | [VERIFICADO ≥2: home, ev-pulse, api-test-cases] |

---

## 7. Placement (dónde colocan cada dato — patrón a copiar por cardeep)

| Dato / métrica | Dónde se coloca (pantalla/sección) | Estado |
|---|---|---|
| Identidad del vehículo (title/make/model/badge/series/spec) | **Car card** (tarjeta de coche) tras resolver rego/VIN/AGID — cabecera de la ficha en Realtime Pricing | [VERIFICADO: realtime-pricing] |
| Valor retail + trade + offer | **Car card / panel de valoración** en RTP ("retail and trade prices in seconds" + offer suggestions) | [VERIFICADO: realtime-pricing] |
| Banda upper/lower + confidence | Junto al valor (bounds + score) — y como **`fill` 0-1 en el AutoGauge** (aguja en banda min-max) | [VERIFICADO: valuation-predict, gauge] |
| Comparables de mercado (Market Overlay) | **Panel LATERAL** de la ficha del lead en la web app ("a view of similar leads ... on the side of the page") | [VERIFICADO: market-overlay] |
| Gráfico de mercado | **Market panel** de RTP (imagen "RTP-MarketOverlay-Graph") | [VERIFICADO: realtime-pricing] |
| Days to Sell / Retained Value% / Volúmenes | **Informe AIR (PDF/Excel)** por secciones (Volume & Inventory · Pricing & Valuation · Velocity & Performance) y **dashboards de Delve** | [VERIFICADO: air-report-pro, delve] |
| Tendencias / lenguaje natural | **Delve** (NL query) y **AutoMate** (chat) | [VERIFICADO: delve, automate] |
| Historial de precio / listings / rollback | **Workflow de sourcing** (analytics por vehículo) y **sección Odometer History del PDF CarAnalysis** | [VERIFICADO: sourcing-tools, car-analysis] |
| Instant cash offer | **Valuation Widget** embebido en la web del dealer (journey de captación de lead) | [VERIFICADO: valuation-widget] |
| Indicador de precio en listing | **Gauge Widget** embebido en la página del marketplace (aguja + rango) | [VERIFICADO: gauge-widget] |
| Marketability snapshot | **Market Insights Snapshot** (popup/iframe) en el listing | [VERIFICADO: market-overlay-widget] |
| PAV / total loss | **Web app PAV** (`/insurance-claims/<id>`) + PDF + webhook | [VERIFICADO: pre-accident-valuation] |
| Recompra de cliente | **Notificación/sighting** (webhook recapture_new) cuando el coche de un cliente reaparece listado | [VERIFICADO: recapture] |
| Specs/fitted options | Dentro del **workflow de valoración** ("factory fitted options during the valuation workflow") | [VERIFICADO: sourcing-tools] |
| EV market (supply/demand, RV%, DTS) | **Live dashboard EV Pulse** + reporte descargable | [VERIFICADO: ev-pulse] |

---

## 8. Diferencial (lo que ofrece y otros no)

1. **Base independiente de TODO el listado online AU + update "cada segundo"** — no depende de subastas (vs Datium) ni de un solo grupo; market-wide. [VERIFICADO]
2. **API-first integral**: cada producto es endpoint (search, valuation, residual, overlay, gauge, history, recapture, PAV, reports). [VERIFICADO]
3. **Confidence score 0-1 + bandas upper/lower** en cada valoración (transparencia de incertidumbre). [VERIFICADO]
4. **AGID** propio (identificador canónico color-agnóstico) como llave de catálogo. [VERIFICADO]
5. **Cobertura del ciclo completo del dealer**: sourcing → valoración → recompra → venta (Recapture detecta reventa del cliente). [VERIFICADO]
6. **Dominio del seguro AU**: 90%+ de aseguradoras usan su dato para total loss; PAV/AutoPAV/Repair Decision. [VERIFICADO ≥2]
7. **Rollback detector** combinando odómetro de transacción Y de servicio. [VERIFICADO]
8. **Embeddables listos** (gauge, instant-cash-offer, market snapshot) con postMessage events. [VERIFICADO]
9. **AutoMate (LLM) + Delve (NL query)**: capa conversacional sobre el dato. [VERIFICADO]
10. **Max Offer configurable** (reconditioning/profit/lot/transport/admin) integrado en la valoración. [VERIFICADO]
11. **UK con datos oficiales profundos** (DVLA+UKVD): road tax, keepers, NCAP, emisiones, scrapped/exported. [VERIFICADO]
12. **Multi-región** (AU/NZ/UK/MY) con un mismo contrato API. [VERIFICADO]

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Asking price, NO transaction price** — valora sobre precios de anuncio (activos+delistados), no ventas confirmadas (vs Datium/Pickles que sí tienen transacción real de subasta). [VERIFICADO]
2. **Solo vehículos de pasajeros** con AGID/valoración — **motos, caravanas, camiones pesados** quedan fuera (solo lookup upstream). [VERIFICADO]
3. **Days-to-Sell / Retained Value% / Supply-Demand** NO son campos discretos de la API pública — viven en AIR Pro/Delve/EV Pulse (productos de informe/dashboard), no en `/predict` ni `/market_overlay`. [VERIFICADO — ausentes del contrato API]
4. **Sin price-to-market % ni market days' supply** como métrica nombrada y atómica (a diferencia de incumbentes US). [NO-VERIFICADO — no aparece en docs] |
5. **Detailed specs son bespoke por contrato** — el set de campos no es universal; depende de JATO y del acuerdo. [VERIFICADO]
6. **Tarifas opacas** salvo AIR Pro; resto contact-sales. [VERIFICADO]
7. **Imágenes con caducidad** (cover/all_images del overlay se guardan solo 90 días tras delisting; stock photos `match_confidence` no siempre alta). [VERIFICADO]
8. **Cobertura "55 países" es de datos/marketing**, no de valoración — el motor de precio solo opera AU/NZ/UK/MY. [VERIFICADO]
9. **Build data limitado** a 40 OEMs y desde 1999; FFO solo UK. [VERIFICADO]
10. **Datos oficiales profundos (DVLA/UKVD)** observados en UK; el equivalente AU (NEVDIS) es más acotado (write-off/stolen/rego). [VERIFICADO]
11. **Empresa joven (2020)** y aún quemando capital ("cashflow breakeven" citado por TEN13 pero en fuerte inversión de expansión). [VERIFICADO]
12. **Sin valoración de coche nuevo "de mercado"** como tal — nuevo entra como RRP/punto de partida del residual. [VERIFICADO]

---

## 10. Fuentes

| # | URL | Qué verifica |
|---|---|---|
| 1 | https://www.autograb.com.au/ | Posicionamiento, 15 productos, segmentos, regiones (AU/NZ/UK/MY/PH), 500+ marcas, app, marcas propias |
| 2 | https://autograb.com.au/about-us/ | Fundadores/liderazgo, 5 oficinas, 120+ empleados, ABN, EVP, CarAnalysis/ValueMyCar |
| 3 | https://devhub.autograb.com/llms-full.txt | **Corpus completo de developer docs** (8.173 líneas): todos los endpoints y campos atómicos AU+UK+NZ+MY (descargado y leído verbatim) |
| 4 | https://devhub.autograb.com/llms.txt | Índice/mapa del API (vehicle-search, sourcing, valuation, vehicle-data, insurance, reports, recapture, embeddables, automate) |
| 5 | https://devhub.autograb.com/valuation/valuation-predict | `/v2/valuations/predict`: inputs (vehicle_id, kms, condition_score, state_for_pricing…) + outputs (retail/trade/score/bounds/equity/max_offer/adjustment) |
| 6 | https://docs.autograb.com.au/guide/valuation/ | Doc de valoración (host caído vía fetch/curl; contenido reconstruido del devhub espejo) |
| 7 | https://autograb.com.au/api/ | 4 áreas API: Discovery, Valuation, History, Enhanced Specifications (100+ fields) |
| 8 | https://autograb.com.au/api-future-valuation/ | Residual: year/kms/valuation/score, horizonte 5 años, iFrame |
| 9 | https://autograb.com.au/air-report-pro/ | AIR Pro: Volume/Inventory, Weighted Retained Value, Retention by Segment, Days to Sell, benchmarking; PDF+Excel; **Gold A$833/mes, Platinum A$2.000/mes** |
| 10 | https://autograb.com.au/realtime-pricing/ | RTP: car card + market panel (RTP-MarketOverlay-Graph), retail/trade + offer, Market Overlay |
| 11 | https://autograb.com.au/delve/ | Delve: benchmarking, pricing/sales trend, custom exploration, AI insights, NL query |
| 12 | https://autograb.com.au/sourcing-tools/ | Sourcing: multi-marketplace, search lists+alertas, rollback detector (transaction+service odo), fitted options en workflow |
| 13 | https://autograb.com.au/insurance-providers/ | PAV web app (PAVBrowser) + API, total loss, ~35 logos aseguradoras |
| 14 | https://autograb.com.au/ev-pulse/ | EV Pulse: Supply&Demand, Retained Value%, Days to Sell; EV usado 2021-2025; diario, 7-day rolling |
| 15 | https://autograb.com.au/automate/ ; https://devhub.autograb.com/automate/automate-usage-guidance.md | AutoMate (LLM): casos, disclaimer, remite a RTP/Catálogo/AIR |
| 16 | https://autograb.com.au/automotive-data-intelligence-provider-autograb-completes-80m-capital-raise-... | **Serie B A$80M @ A$230M (27-ene-2026)**; Octopus+Movac lead; 1.000+ dealers (~25%); 90%+ aseguradoras; CBA 10M+; quotes Werzberger/Gardner |
| 17 | https://www.smartcompany.com.au/startupsmart/autograb-80-million-raise-investment-car-intelligence-data-platform/ | Cross-verifica A$80M / A$230M / South Yarra / fundación 2020 |
| 18 | https://www.cbinsights.com/company/autograb | Fundación 2020, HQ 10 River St South Yarra, ~US$58,6M total, inversores, competidores (AlgoDriven, Keyloop, Orbee, Carketa, Nimbloo…) |
| 19 | https://www.ten13.vc/post/flight-plan-19-our-investment-in-autograb | Fundadores (Werzberger ex areyouselling→Eclipx 2017; Gardner), "mayor base independiente AU", "updated every second", 5 product lines |
| 20 | https://autograb.co.uk/ | UK: "UK's Automotive Intelligence Platform"; mismos productos; foco seguro (identificación precisa de vehículo); api.autograb.co.uk |
| 21 | https://www.brokernews.com.au/news/.../lmg-teams-up-with-...-autograb-... | Partner LMG (préstamos auto más rápidos) |
| 22 | https://premium.goauto.com.au/ai-uncovers-autograbs-secrets/ | Entrevista CCO Saxon Odgers sobre AutoMate (contenido promocional, no análisis independiente) |
| 23 | https://devhub.autograb.com/vehicle-data/detailed-specifications-data.md | Detailed specs (JATO): specs[category,id,description,value,int_value,location] bespoke |
| 24 | https://devhub.autograb.com/vehicle-data/vehicle-history.md ; .../sourcing/market-overlay.md | History events (listing/delisting/price_change) + Market Overlay features (avg_price/avg_kms/RRP/contact/images…) |
| 25 | https://devhub.autograb.com/.../uk-autograb-api-doc/... (recall-check, mot-tax, factory-fitted-options) | UK deltas: Recall, MOT&Tax, FFO (option_id/code/title/match_score/msrp), UKVD/DVLA extended (road tax, keepers, NCAP, emissions) |

> **Nota de método:** `docs.autograb.com.au` no resolvió por DNS (WebFetch y curl) — su contenido está espejado en `devhub.autograb.com`,
> que sí publica un corpus LLM-optimizado (`llms-full.txt`). Todo campo atómico se leyó verbatim de ese corpus descargado, no inferido.
> Donde no hubo confirmación se marcó `[NO-VERIFICADO]`. Discrepancia de fundación (CB Insights/SmartCompany 2020 vs TEN13 "~2022")
> declarada explícitamente. Cifra de financiación: A$80M Serie B (PR/SmartCompany) ≈ US$55,3M (CB Insights), consistente.
