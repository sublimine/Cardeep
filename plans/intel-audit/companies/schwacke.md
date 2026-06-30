# Schwacke — Auditoría atómica

> Auditoría nivel institucional para cardeep · subdominio **valuation** · `slug: schwacke`
> Fecha: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; lo no verificado se marca `[NO-VERIFICADO]`.
> Web: https://www.schwacke.de/ · Portal app: schwackeNET (https://schadenmanager.schwacke.de) · Grupo: https://autovista.com

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Nombre legal | **Schwacke GmbH** (marca histórica: *Schwacke-Liste*; ex *EurotaxSchwacke GmbH*) | northdata, autovistagroup |
| Marca actual | **JD Power Schwacke** (footer "© 2026 JD Power Autovista") | autovista.com, schwacke.de |
| Grupo / owner | **Autovista Group** (marcas hermanas: Eurotax, Glass's, Rodboka) → propiedad de **J.D. Power** | autovistagroup, jdpower |
| Adquisición J.D. Power | Anunciada **sep-2023**, **cerrada en 2024**; ~750 empleados del grupo integrados | jdpower (close), autovista24 |
| Fundación | **Noviembre 1957**, por **Hanns W. Schwacke** en Frankfurt am Main (primer *"Marktbericht für Gebrauchtwagen"*) | autohaus.de, wikipedia DE |
| HQ | **Westendstraße 28, 60325 Frankfurt am Main** (Amtsgericht Frankfurt HRB 114451). Antes en **Maintal** (1994–2018) | northdata, flotte.de |
| Empleados (Schwacke GmbH) | ~51–200 (LinkedIn) `[rango no exacto]` | LinkedIn |
| Linaje corporativo | Schwacke (DE) + Eurotax (CH) + Glass's (UK) → *EurotaxGlass's* → **Autovista Group** (desde 2017) | wikipedia DE |

**Qué es:** especialista en *Automotive Business Intelligence*. Es la **autoridad de referencia del precio de coche usado en Alemania** (equivalente alemán a Kelley Blue Book / Glass's). Combina la herencia de la *Schwacke-Liste* con los feeds/APIs paneuropeos de Autovista.

**Categorías:** valoración de vehículos (nuevo y usado), pronóstico de valor residual, datos de especificación/identificación, costes de reparación y mantenimiento (SMR), TCO, gestión de daños/siniestros, gestión de stock, datos de mercado EV.

**Cliente objetivo (verificado):** comerciantes/concesionarios, fabricantes (OEM)/importadores, sociedades de financiación y leasing, alquiladoras/remarketing, **aseguradoras** (claims), talleres, peritos (Sachverständige), consultoras, proveedores de software/telemática.

---

## 2. Cobertura

- **Países (AutovistaSPEC, según Data Definition Doc v16.4):** AT, BE, CH, CZ, DE, ES, FR, GB, HR, HU, IT, NL, PL, PT, RO, SK, SI, NO (algunos "en gris/por llegar"). El producto se comercializa como **13–15 mercados** con datos de alta calidad de especificación. `[la web cita "99% de los vehículos europeos"]`
- **AutovistaVALUATION:** 15 mercados europeos · 99% de turismos y LCV.
- **Residual Value Monitor:** 17 mercados europeos · 38 marcas · 150 *model types* por mercado.
- **Residual Value Intelligence:** 7 mercados · 42 marcas · 14 segmentos.
- **Car Cost Expert (TCO):** 12 países · 600+ *model ranges* · 300+ escenarios edad/km.
- **Portal Schwacke / schwackeNET / SchadenManager:** foco **Alemania** (con HSN/TSN y interfaz GDV nacionales).
- **Scope vehículos:** nuevo + usado. Tipos: **Car, Off-road/SUV, LCV <3,5t, LCV <7,5t, motocicleta, micro, Moto4/Quad/ATV**; históricamente también **autocaravanas/Freizeitmobile**.

---

## 3. Productos + campos atómicos

> Tres familias: (A) **Plataformas/portales** alemanes, (B) **Feeds/APIs Autovista** (datos crudos), (C) **Apps de analítica/TCO**.

### A1 · Schwacke (portal SaaS / schwackeNET) — valoración + gestión de stock
Navegador (Edge/Chrome/Firefox). Núcleo: identificar → valorar → gestionar inventario.
**Campos/métricas:**
- **Einkaufspreis** (precio de compra / Händlereinkaufswert)
- **Verkaufspreis** (precio de venta / Händlerverkaufswert)
- **Schwacke Tagespreis** (precio diario, refleja *live retail market*)
- **geschätzte Wertminderung** (depreciación estimada → momento óptimo de venta)
- **Bewertungs-Details** (ventana de detalle de valoración / valor ajustado)
- **VIN-Abfrage** (identificación por VIN) + **VIN-Ausstattungsanzeige** (equipamiento de serie y opcional por VIN)
- **Restwert** / Restwertprognose (valor residual y su curva)
- **Standtage** (días en stock), **Marge/KPIs** (margen por vehículo), **vielversprechender Bestand** (stock prometedor por rentabilidad)
- **Wettbewerbspreise** (precios y estrategia de la competencia)
- **Reparaturkostenkalkulation** (cálculo de coste de reparación de daños)
- **Marktentwicklung** (panel de evolución de mercado en home)
- **automatische Neubewertung** (revaloración periódica automática)

### A2 · SchadenManager (gestión de siniestros) — schwackeNET
App web separada (schadenmanager.schwacke.de), versión schwackeNET. Para aseguradoras/talleres/peritos.
**Campos/métricas (verificados):**
- **Reparaturkostenkalkulation** (cálculo de coste de reparación)
- **Fahrzeugbewertung** (valoración del vehículo)
- **Wiederbeschaffungswert** (valor de reposición/reemplazo)
- **Schadenkalkulation** (cálculo del daño)
- **Nutzungsausfallentschädigung** (indemnización por privación de uso)
- **Mietwagen-Preisindex / Mietwagenklasse** (índice de precio de coche de alquiler / clase)
- **klassifizierende Daten** (datos clasificatorios del vehículo)
- Identificación: **VIN (Fahrgestellnummer)**, **HSN/TSN**, árbol de búsqueda
- **GDV-Schnittstelle** (interfaz GDV de intercambio con aseguradoras)
- `[NO-VERIFICADO, típicos del dominio de peritaje DE]` Restwert (valor de resto/chatarra), merkantiler Minderwert (minusvalía mercantil), regla 130% de pérdida total

### A3 · Schwacke-Liste (clásica) / Schwacke-Zertifikat
La lista histórica de referencia. **Valores:**
- **Händlereinkaufspreis** (precio de compra del comerciante) — `[VERIFICADO]`
- **Händlerverkaufspreis / Verkaufspreis** (precio de venta) — `[VERIFICADO]`
- `[NO-VERIFICADO en esta fuente, asociados a la marca]` Privatverkaufswert, Beleihungswert
- **Inputs de identificación:** Fahrzeugtyp, **HSN (Herstellerschlüsselnummer)** / **TSN (Typschlüsselnummer)**, Schwacke-Code, **Erstzulassung** (1ª matriculación), **Kilometerstand** (km), **Ausstattung** (equipamiento)
- **Ajustes:** km por encima de la media → valor más bajo; Sonderausstattung (equipamiento especial) → valor más alto

### B1 · AutovistaSPEC — datos de especificación/identificación (feed CSV tab + API)
Núcleo de datos. **99% de vehículos europeos**, hasta **20 años de historia**, enriquecido con *machine learning*. Entrega: **CSV separado por tabuladores** + API. (Fuente atómica: *AutovistaSPEC Data Definition Document V2.0.1*.)

**Identificación / estandarización:**
- **NatCode** (código nacional, clave de clasificación Autovista), **VIN**, **VRM/registration** (matrícula), **HSN/TSN** (DE)
- Vehicle type code, National market code, Country code
- **Make** (nacional + *standardised*), **Model** + Model-Level-One/Two/Three (nacional + standardised)
- **Facelift information** (nacional + internacional), Type name / Type name 2, Long type name
- **Segmentación:** Segmentation 1 / 2 (national), Segmentation **Autovista International**, Segmentation **FISITA**, Vehicle category, COC segmentation
- Import/Sale start (**TYPImpBegin**), Import/Sale end (**TYPImpEnd**), allocation to basic type
- Model year (tabla `modelyear.txt`), ETAG code, National & International Links, Swiss Stammnummer linking (`LINKING_STAMMNR_CH`), Italian system code (TYPEIT)

**Precio nuevo (PRICE) + historial (PRICEHistory, 20 años):**
- **New price incl. tax (NP1)**, **New price excl. tax (NP2)**, **Net price (NP3 / incl. all expenses)**
- **Tax rate %**, **VAT amount**, **Tax2 (road tax)**, **Recycling charge**, **Transport costs**, **Transport VAT**, **Immatriculation fee**, **NoVA rate** (AT)
- Provisional flag, validity dates (PRIVal/PRIValUntil)
- **Battery lease conditions & prices** (BatteryLease), **Battery price history** (BatteryPriceHistory)

**Técnica del motor (TECHNIC/TEC):**
- Engine type / Engine type suffix, **Number of strokes**, **Tax capacity (ccm)** / displacement, **Number of cylinders**, **Cylinder angle (V-engines)**, **Bore (mm)**, **Stroke (mm)**, **Compression ratio**
- **Power kW / HP** (rated speed rpm from/to), **Torque (Nm)** (rpm from/to), Number of chargers (turbo), Intercooler, Camshaft drive, Diagnosis system, Cooling medium
- **Fuel grade** (+ minimal), Mixture/feed system, Ignition, Engine alignment

**Datos técnicos extendidos (TypeInformationExtended / TIE):**
- **Brake horsepower (TIEBrakeHP)**, **Kerb/curb weight** (con / sin conductor + líquidos, máx)
- **Gas tank capacity** + unidad (vehículos de gas), **AdBlue need** + **AdBlue tank capacity (l)**
- LCV: **Platform length min/max**, **Platform width min/max**, **Cargo volume (l)**, **Min seats**
- **SAE autonomous level** (base + máximo alcanzable con opción)
- **Start-Stop system**, **Brake energy recovery**, **Start support**, **On-board voltage (V)**
- Híbrido: **Hybrid system kW / HP / Torque**
- **ABI Insurers group rating** (GB), retainer/saved costs para vehículos de alquiler

**Eléctrico (TIE + ElectricEngine/ELE + ChargingVariants/ECT):**
- **Number of electric engines (TIENumEEngines)**, función del motor eléctrico
- **Electric peak power kW / HP**, **Electric peak torque (Nm)**
- **Electric continuous power 30/60 min (kW/HP)**, **continuous torque 30/60 min (Nm)**
- **Power in national homologation papers (kW)**
- **Battery capacity (Ah)**, **Battery capacity (kWh)**, **Battery type**, **Battery voltage (V)**, **Battery warranty (months)**, **Battery location**
- **On-board charger power (kW)**, **Charging station power (kW)**, **Current type (AC/DC)**, **Connector type**, on-board charger standard indicator, **Charging time 80% (h)**, **Charging time 100% (h)**, charging variant valid from/until

**Consumo / emisiones (WLTP + NEDC/PKW-EnVKV + Pollution):**
- **WLTP consumption & norm data** (v1, v2, additional emission data)
- **NEDC** vía *German PKW-EnVKV* (gráfico + alternative fuels + options)
- **CO2**, **Pollution norm history**, **Gas consumption**, **Imperial fuel consumption**, Energy efficiency class
- Performance and consumption (CONSUMER): aceleración/velocidad punta `[implícito]`

**Equipamiento (Equipment module):**
- **Equipment code**, Equipment text / short, **Devaluation code (Entwertungscode)**, **Group code**, equipment importance, sorting
- **Colours:** Autovista colours (EuroCol), Manufacturer colours (ManuCol), Type colours (TypeCol), **Paint/Trim combinations**
- **Order codes** + Long order codes + Option order codes (códigos de pedido OEM)
- **ESACO** (clasificación estándar de equipamiento): exclusion groups, exclusions, multiselect, category group join, excluded codes
- **Group average prices (GrAvePri)**, **Combination prices (CombinationPrice)**, equipment price incl/excl tax, **Target group** (Fleet/retail)
- Special-edition texts, Basic-model texts, Option remarks (+ link Remark↔Addition)

**Ruedas / neumáticos / llantas:**
- **Tyres:** Width, Cross-section (ratio alto/ancho), Design, Diameter, Load rating, Speed index (ECE + DIN), Suffix
- **Rims:** Width, Diameter, Screw-hole circle, Number of bolts, Position of rim mounting, **Rim material**
- Wheels (JWHEEL)

**Media:** Image links, Image characteristics, Image types A/B/C.

**Tablas de sistema:** Markets/Countries, Languages, Currencies, Vehicle-Types per Market, Structure version, Report of delivery.

### B2 · AutovistaVALUATION — valores de mercado / valor residual usado (API/feed)
"Industry-leading residual value statements" para **turismos, vehículos comerciales y motocicletas**. Feed único armonizado, 15 mercados, 99% cobertura.
- **Used vehicle market value** (valor de mercado en tiempo real)
- **Trade value** y **Retail value** `[derivado de RV Monitor/Intelligence]`
- **Complete residual value dataset incl. average mileage** (kilometraje medio)
- **Mileage-adjusted valuation** (ajuste por km), local/regional market price adjustment
- Market observation continua / verificación de estimación

### B3 · AutovistaFORECAST — pronóstico de valor residual (API)
RV forecasts para **nuevos y usados (turismos + LCV)**.
- **Restwertprognose** en **% y absoluto**
- Horizonte: **hasta 6 años / 200.000 km** (producto DE); **hasta 120 meses / 10 años** (feed de grupo)
- **16 combinaciones edad-kilometraje** (age-mileage scenarios)
- Métricas de riesgo / optimización de rentabilidad fin de contrato

### B4 · AutovistaREFORECAST — revaloración de cartera / riesgo (feed + API)
- Evaluación de inventario/flota, identificación de riesgo por fase del contrato de leasing
- Funcionalidad **por VIN**, **carga masiva (bulk upload)**, datasets detallados por vehículo

### B5 · AutovistaREPAIR — costes de reparación (feed + API)
- **Repair cost estimate** (coste de reparación por vehículo)
- **OEM parts prices** (precios exactos de piezas OEM), identificación de pieza aun con nº OE reemplazado
- **Labour times** (tiempos de mano de obra)
- **AZT paint data** (datos de pintura para coste de pintado)
- **Wear part costs** (piezas de desgaste, para TCO)
- Compatibilidad **catálogo TecDoc**; **gráfico interactivo** (clic en cualquier pieza → precio)

### B6 · AutovistaSMR — Service/Maintenance/Repair (feed + API)
- **Service & maintenance parts + labour times (OEM)**
- **Maintenance intervals** (por tiempo y por distancia/km), **scheduled service items**
- **Maintenance cost forecast**, **OEM parts pricing**, **wear parts**
- **TCO components**; TecDoc opcional

### B7 · AutovistaAPI — capa de entrega API (cloud, pay-per-use)
Módulos: **Identifizierung (Identification)**, **Spezifikationen (Specifications)**, **Bewertung (Valuation)**, **Prognose (Forecast/RV)**, **Technik (Technical)**. Ajuste por km, registros por vehículo individual.

### C1 · Car Cost Expert — TCO (app web)
TCO para turismos y LCV, **actualización mensual**, 600+ model ranges, 300+ escenarios, 12 países. Export **Excel/PDF**.
**Componentes de coste:** **depreciación**, **financiación/intereses**, **impuestos (road tax)**, **consumo de combustible/energía**, **seguro**, **service-maintenance-repair**, **spare parts** (piezas), **neumáticos** `[implícito SMR]`, valor residual, precio de lista, descuento.
**Inputs ajustables por el usuario:** labour rate (tarifa MO), interest rate (interés), consumption (consumo), local taxes, energy prices, incentives; simulación de niveles de equipamiento/packs de servicio; filtros hasta nivel de **trim**.

### C2 · Residual Value Monitor — benchmarking de RV (dashboard)
17 mercados · 38 marcas · 150 model types/mercado · datos crudos **mensuales** · tendencias **4 años**.
- **Latest trade & retail values**, **RV performance**, **benchmark vs competidores** (like-for-like por cestas)
- **Ranking de modelos por performance**, **predecessor-successor tracking**, efecto facelift/lanzamiento
- Selección de mercados/modelos, export de datos crudos

### C3 · Residual Value Intelligence — tendencias de mercado usado (dashboard)
7 mercados · 42 marcas · 14 segmentos.
- **Residual values (trade & retail)**, **16 escenarios edad-km**
- **Price index** (índice de precios, **actualización semanal** sobre datos de mercado usado)
- Market trends, brand/segment performance, filtro por **tipo de combustible**, dashboard personalizable, 4 años de histórico, export de gráficos/datasets

### C4 · Compare (Eurotax) · Car To Market · EV Volumes
- **Compare:** "toda la realidad del valor residual en una aplicación" (RV paneuropeo unificado).
- **Car To Market:** consultoría de diseño de producto y go-to-market.
- **EV Volumes:** datos y **forecasts de mercado EV** (ventas/matriculaciones electrificados).

---

## 4. Metodología / fuentes de datos

- **Observación sistemática del mercado desde 1957** (origen *Marktbericht für Gebrauchtwagen*).
- **Base de datos actualizada semanalmente** (técnica, precios de lista y equipamiento históricos, valoraciones, pronósticos, piezas, TCO). Car Cost Expert y RV Monitor: **mensual**; Price Index (RV Intelligence): **semanal**.
- **Machine learning** para enriquecer/estandarizar AutovistaSPEC.
- **Valoración real-time** sobre *live retail market* (Tagespreis) + verificación continua de estimaciones.
- **Datos OEM** para piezas y tiempos (SMR/REPAIR); **AZT paint data**; vinculación **catálogo TecDoc**.
- **"Proven used vehicle data"** como benchmark del sector.
- Sistema de clasificación propietario **NatCode**; identificación por **VIN / VRM / HSN-TSN**; datos **estandarizados paneuropeos**.

---

## 5. Entrega

- **Portal web / SaaS:** schwackeNET (portal Schwacke + SchadenManager), navegador (Edge/Chrome/Firefox), multi-dispositivo.
- **Apps web dedicadas:** Car Cost Expert, Residual Value Monitor, Residual Value Intelligence, Compare.
- **Feeds de datos:** **CSV separado por tabuladores** (AutovistaSPEC), batch; guías de integración + scripts de import.
- **APIs:** **AutovistaAPI**, cloud, **pay-per-use**, por vehículo individual, ajuste por km.
- **Export:** **Excel / PDF** (Car Cost Expert), datos crudos (RV Monitor/Intelligence).
- **Integraciones:** **GDV-Schnittstelle** (aseguradoras), integración en DMS/sistemas propios ("es fallen Kosten für die Integration an").

---

## 6. Modelo de precio

- **APIs: pay-per-use** + **coste de integración** (verificado en schwacke.de/unsere-api).
- Resto (portal, feeds, apps): **suscripción / contacto comercial**; tarifas **no públicas**. `[NO-VERIFICADO importes]`
- Free trial disponible para SchadenManager (registro). Schwacke-Liste clásica: producto de pago (certificado).

---

## 7. Placement (DÓNDE coloca cada dato — patrón que cardeep imita)

| Dato | Ubicación en la UI Schwacke |
|---|---|
| Marktentwicklung (evolución de mercado) | **Dashboard/home** del portal |
| Einkaufspreis / Verkaufspreis / Tagespreis | **Pantalla de valoración** (resultado principal) |
| geschätzte Wertminderung (depreciación) | Valoración → indicador junto a precio (momento óptimo de venta) |
| Bewertungs-Details (valor ajustado) | **Ventana modal "Bewertungs-Details"** sobre la valoración |
| Equipamiento por VIN | **VIN-Ausstattungsanzeige** tras VIN-Abfrage (lista serie/opcional) |
| Restwert / curva RV | Herramienta de **seguimiento de restwert**: de resumen estratégico → hasta vehículo individual (niveles de agregación) |
| Standtage / Marge / KPIs / Wettbewerbspreise | **Módulo de gestión de stock** (tabla de inventario con días en stock y precios competencia) |
| automatische Neubewertung | Inventario → revaloración periódica automática |
| Reparaturkostenkalkulation (precio por pieza) | **AutovistaREPAIR: gráfico interactivo del vehículo** (clic en pieza → precio) |
| Wiederbeschaffungswert / Nutzungsausfall / Schadenkalkulation | **SchadenManager** (flujo de caso: identificación → cálculo → freigabe) |
| RV trade/retail + benchmark + ranking | **Dashboard Residual Value Monitor** (ranking de modelos + benchmark vs competidores + tendencia 4 años) |
| Price index + tendencias usado | **Dashboard Residual Value Intelligence** (índice + filtros marca/segmento/combustible) |
| TCO breakdown + inputs de usuario | **Car Cost Expert**: desglose TCO + filtros hasta trim + campos editables (labour/interés/consumo) + export Excel/PDF |

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Autoridad histórica del usado alemán** — la *Schwacke-Liste* es el estándar de facto en DE desde 1957 (peso de marca tipo "KBB alemán").
2. **Ecosistema de daños/siniestros insurance-grade** — SchadenManager con **Wiederbeschaffungswert, Nutzungsausfall, AZT paint, interfaz GDV** y árbol HSN/TSN. Pocos competidores lo cubren tan profundo en DE.
3. **AutovistaSPEC: profundidad de especificación extrema** — NatCode, ESACO (clasificación estándar de equipamiento), **20 años de precios de lista y equipamiento**, y bloque **EV de élite** (nº de motores eléctricos, potencia pico/continua 30/60 min, batería Ah/kWh/V/garantía/ubicación, variantes de carga AC/DC, tiempos de carga 80/100%, **nivel SAE de autonomía**, AdBlue).
4. **Datos paneuropeos armonizados** — un feed para 15–17 mercados (cross-border RV), vía Autovista.
5. **TCO granular y simulable** — Car Cost Expert con assumptions editables, 300 escenarios, export Excel/PDF.
6. **Reparación a nivel de pieza con gráfico interactivo** + TecDoc.
7. **EV Volumes** — datos y forecasts de mercado EV.
8. **Valoración diaria (Tagespreis)** reflejando live retail.

---

## 9. Gaps (lo que NO ofrece — oportunidad para cardeep)

1. **Sin provenance/historial por VIN** — no hay check de siniestros/odómetro/robo/financiación (territorio cap hpi/Carfax/HPI). REPAIR usa VIN para *spec*, no para *historia*.
2. **Sin censo de anuncios live a nivel individual** — es valoración **model-level**, no un índice nacional de listings/huella digital (lo de cardeep). El stock management usa el inventario propio del dealer + precios de competencia, no un censo nacional de puntos de venta.
3. **Sin índice explícito demanda/oferta, price-to-market %, market days supply** — Standtage es solo días en stock del propio dealer; RV Monitor es performance model-level. (Territorio INDICATA/vAuto). `[probable gap]`
4. **Sin mapa/censo de puntos de venta físicos ni huella digital de cada dealer** — Schwacke valora, no geolocaliza/cartografía la red comercial (núcleo de cardeep).
5. **Precios no transparentes** — todo es contacto comercial salvo el API pay-per-use.
6. **B2C casi inexistente** — es B2B; la valoración gratuita al consumidor no es su producto (ojo: `schwake.de` es un dominio *lookalike* ajeno, no Schwacke).
7. **Alcance geográfico EU-céntrico** — sin cobertura global propia (US/Asia llegan vía J.D. Power a nivel grupo, no marca Schwacke).
8. **Daños DE-específico** — el potente toolkit de siniestros (GDV, HSN/TSN) no se traslada igual fuera de Alemania.

---

## 10. Fuentes

- https://www.schwacke.de/ · https://schwacke.de/produkt/datenloesungen/ · https://schwacke.de/produkt/schwacke/ · https://schwacke.de/produkt/autovistaspec/ · https://schwacke.de/produkt/autovistavaluation/ · https://schwacke.de/produkt/forecast/ · https://schwacke.de/produkt/autovistareforecast/ · https://schwacke.de/produkt/autovistarepair/ · https://schwacke.de/produkt/autovistasmr · https://schwacke.de/produkt/schadenmanager/ · https://schwacke.de/produkt/ev-volumes/ · https://schwacke.de/unsere-api · https://schwacke.de/das-neue-schwacke-ist-da/ · https://schwacke.de/bewertung-prognosen/wie-kann-ich-restwertentwicklungen-nachverfolgen/
- https://schadenmanager.schwacke.de/ (schwackeNET login)
- https://autovista.com/ · https://autovista.com/product/data-solutions/ · https://autovista.com/product/autovistaspec/ · https://autovista.com/product/car-cost-expert/ · https://autovista.com/product/residual-value-monitor/ · https://autovista.com/product/residual-value-intelligence/ · https://autovistagroup.com/products-and-services/schwacke · https://autovistagroup.com/products-and-services/schwacke-data
- **AutovistaSPEC Data Definition Document V2.0.1 (External)** — https://glass.co.uk/wp-content/uploads/sites/2/2024/09/AutovistaSPEC-Data-Definition-Document-V-2.0.1-External.pdf · https://glass.co.uk/autovistaspec-product-enhancements-june-2025/
- Identidad/historia: https://www.autohaus.de/nachrichten/autohandel/neuer-firmensitz-schwacke-kehrt-nach-frankfurt-zurueck-2715137 · https://de.wikipedia.org/wiki/EurotaxSchwacke · https://flotte.de/artikel/114/13834/schwacke-wechselt-unternehmenssitz-nach-frankfurt · https://www.northdata.com/Schwacke+GmbH,+Frankfurt+a.+Main/Amtsgericht+Frankfurt+am+Main+HRB+114451
- Adquisición J.D. Power: https://www.jdpower.com/business/press-releases/autovista-group-acquisition-close · https://autovista24.autovistagroup.com/news/jd-power-completes-acquisition-of-autovista-group/ · https://www.thomabravo.com/press-releases/j.d.-power-sets-sights-on-european-expansion-with-completion-of-autovista-group-acquisition
- Schwacke-Liste clásica: https://www.pkw.de/magazin/schwacke-liste/ · https://www.ruv.de/kfz-versicherung/magazin/rund-ums-auto/schwacke-liste

> Verificación: identidad, owner, adquisición, cobertura y productos con ≥2 fuentes. Campos atómicos de AutovistaSPEC = fuente primaria (Data Definition Doc). Importes de precio y algunos valores de peritaje (Restwert/merkantiler Minderwert/Privatverkaufswert/Beleihungswert) marcados `[NO-VERIFICADO]`.
