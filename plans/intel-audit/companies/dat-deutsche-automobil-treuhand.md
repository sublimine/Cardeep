# DAT — Deutsche Automobil Treuhand GmbH

> Auditoría atómica · subdominio cardeep: **valuation** · prioridad 1
> Verificación: cada bloque marcado [V] (verificado ≥1 fuente directa DAT) o [V2] (≥2 fuentes ortogonales) o [NO-VERIFICADO].
> Fecha auditoría: 2026-06-30. Términos de producto se conservan en su idioma original (DE/ES/EN).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre legal | Deutsche Automobil Treuhand GmbH | [V2] |
| Marca comercial | **DAT** · plataforma **SilverDAT** · grupo **DAT Group / DAT International** | [V2] |
| Fundación | **1931** | [V2] |
| Forma jurídica | GmbH (sociedad limitada alemana) | [V] |
| Propiedad (socios fundadores, neutralidad institucional) | Tres asociaciones del sector, a partes: **VDA** (Verband der Automobilindustrie), **VDIK** (Verband der Internationalen Kraftfahrzeughersteller), **ZDK** (Zentralverband Deutsches Kraffahrzeuggewerbe) | [V2] |
| HQ | Hellmuth-Hirth-Straße 1, **73760 Ostfildern** (área de Stuttgart), Alemania · tel +49 711 4503-130 | [V2] |
| Plantilla | "más de 550 empleados en 22 países" (Europa + Asia) | [V] datgroup about-us |
| Dirección | Jens Nietzschmann (Chairman DE), Dr. Thilo Wagner (Productos), Helmut Eifert (Internacional) | [V] |
| Mandato | Intermediario **neutral** entre todos los actores del automóvil (mandato especial por su estructura accionarial tripartita) | [V2] |
| Versión SilverDAT actual | 5.10.07 (front) · módulos con versionado propio (valuateFinance 1.64.13) | [V] |

**Lectura para cardeep:** DAT es el equivalente alemán-institucional de lo que cardeep aspira a ser: una **autoridad neutral de dato** respaldada por las asociaciones del sector. Su credibilidad no nace del marketing sino de la gobernanza (VDA+VDIK+ZDK). 90+ años de serie histórica.

---

## 2. Categorías + cliente objetivo

**Categorías:** valoración VO/VN · identificación de vehículo (VIN/spec) · cálculo de costes de reparación · gestión de siniestros · reconocimiento de daños por IA · datos de vehículo + telemática/flota · pronóstico de valor residual · estudios de mercado · índice de alquiler.

**Clientes objetivo (cobertura completa de la cadena):**
- **Autohaus / concesionarios** y **talleres** (Werkstatt) — valoración, cálculo, webScan
- **Peritos / Kfz-Sachverständige** — valoración, cálculo, FastTrackAI, programa "DAT Expert Partner"
- **Aseguradoras** (Versicherungen) — siniestros, FastTrackAI, Mietwagenspiegel, Zentralruf
- **Bancos / financieras / leasing** — valuateFinance, Restwertprognose
- **Flotas / fuhrpark** — FleetForecast, SilverDAT Connect, telemática
- **OEM / importadores** — datos, configurador, retroalimentación de transacciones
- **Software houses / proveedores DMS** — Schnittstellenpartnerschaft (~400 partners)
- **Particulares / Autofahrer** — calculadora de valor online, localizador de peritos
- **Asesores fiscales/legales, abogados** — Bewertungsprotokoll, Mietwagenspiegel (defendible en tribunal)

---

## 3. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Huella DAT Group | "22 países" (about-us) / "25+" (home datgroup) Europa+Asia. Subsidiarias propias en DE, CH, China; oficinas regionales | [V] (cifra discrepa entre páginas → ~22-25) |
| **Valoración VO (valuateFinance) — países productivos** | **Alemania, Bulgaria, Francia, Grecia, Italia, Austria, Rumanía, Eslovaquia, España, República Checa, Hungría** (11 países) | [V] PDF producto |
| Comparativa nacional de valoración | "9 países" en otra fuente (DE, IT, ES, AT, FR, RO, RU, CZ, SK) | [V] datgroup |
| Asia | China, Corea del Sur | [V] |
| Scope tipo vehículo | **Pkw** (turismo), **Geländewagen/SUV**, **Zweiräder** (motos), **Transporter ≤3,5 t**, **schwere Lkw** (camión pesado) y **Aufbauten** (carrocerías/superestructuras) | [V] |
| Scope nuevo/usado | **Ambos** — VN (Neufahrzeug) y VO (Gebrauchtfahrzeug). Restwertprognose aplica a nuevos y usados | [V] |
| Edad valorable | Cotización hasta **20 años**; pronóstico residual hasta **72 meses** de edad / **200.000 km** | [V] |
| Cobertura de identificación | **99,8 %** del parque de turismos alemán identificable vía SilverDAT/VIN | [V2] |
| España (DAT Ibérica) | Valor de referencia oficial **GANVAM-DAT** (partnership GANVAM + DAT) | [V2] |

---

## 4. Productos de datos + campos ATÓMICOS

### 4.1 SilverDAT (plataforma web modular — núcleo del negocio)
Suite SaaS modular. Identificación → cálculo/valoración → siniestro → salida. Los módulos comparten la base de datos DAT y el €uropa-Code.

---

### 4.2 VIN-Abfrage + DAT €uropa-Code® (identificación / specs)
Identificación inequívoca de vehículo y equipamiento. **Métodos de entrada:** VIN de 17 dígitos · **€uropa-Code** (código DAT) · **KBA-Schlüssel** (HSN/TSN alemán) · selección manual por árbol (Suchbaum) · matrícula (ES).

**Campos atómicos devueltos:**
- `Baureihe` — serie/gama del modelo
- `Karosserieform` — tipo de carrocería
- `Motorisierung` — motorización
- `exakte Ausstattung ab Werk` — equipamiento exacto de fábrica
- `Serienausstattung` — equipamiento de serie (lista)
- `Sonderausstattung` — equipamiento opcional/especial (lista, con código)
- `DAT €uropa-Code` — código numérico de **15 dígitos** que cifra tipo de vehículo, fabricante, tipo principal y subtipo + características de equipamiento ligadas inseparablemente al vehículo
- `KBA-Schlüssel` — clave oficial alemana (HSN-TSN)
- `CO₂-Emissionen` — emisiones CO₂
- `Motorleistung` — potencia (kW/PS)
- `Verbrauchswerte` — consumos
- `Farbcode` — código de color/pintura
- `Fahrassistenzsysteme` — sistemas ADAS (relevantes para valoración)
- Cobertura: **99,8 %** del parque turismo DE
- Salida vía centro de datos DAT desde BBDD conectadas de fabricantes/importadores "en segundos"

> El €uropa-Code es el **identificador propietario** que normaliza vehículos cross-fabricante para comparación, flota y peritaje. DAT afirma que "ningún código comparable" logra esto. [V2]

---

### 4.3 SilverDAT Valuate / valuateFinance (valoración VO + pronóstico residual) — **NÚCLEO para cardeep**

**Tipos de valor (campos de salida):**
- `Händlereinkaufswert` — **valor de compra del concesionario** (≈ trade-in; bajo el de mercado por margen, riesgo y tiempo de stock)
- `Händlerverkaufswert` — **valor de venta del concesionario** (≈ retail; por encima de ofertas privadas comparables)
- `Privatverkaufswert` / `Marktwert` — **valor de venta privada / valor de mercado**
- `Wiederbeschaffungswert` — **valor de reposición** (típicamente 15-25 % sobre el Händlereinkaufswert; incluye preparación, garantía)
- `Restwert` — **valor residual** (sobre todo vehículo siniestrado; lo estima el perito)
- `Handelsspanne` — **margen comercial** configurable (DAT o el partner define; deriva einkauf↔verkauf)
- `Zeitwert` — valor temporal/depreciado (usado para depreciar opcionales)
- `Restwertprognose` — **pronóstico de valor residual futuro** (€ y %)
- `SoH (State of Health)` — **salud de batería** para VE (vía diagnóstico independiente)
- Bewertung `rückwirkend zu einem Stichtag` — **valoración retroactiva** a una fecha clave

**Inputs / factores de ajuste (campos de entrada):**
- `Erstzulassung` — primera matriculación
- `aktueller Kilometerstand` / `Laufleistung` — km actuales
- `Sonderausstattung` depreciada por `Zeitwert` o `Restwert` (recomendación DAT ajustable por el partner)
- `Zustandskriterien` — criterios de estado/condición
- `Reparaturen` — reparaciones / coste de reparación
- `Anzahl der Vorbesitzer` — nº de propietarios anteriores
- `Serien- und Sonderausstattung` — equipamiento completo

**Parámetros de pronóstico residual:**
- Horizonte hasta **72 meses** de edad y **200.000 km**
- Combinaciones libres de `Laufzeit` (plazo) × `Laufleistung` (km), y entre `Jahresfahrleistung` (km/año) y `Gesamtfahrleistung` (km totales)
- Cotización de vehículos hasta **20 años**
- Multi-divisa y multi-idioma

**Salidas (formato):**
- `allgemeine Darstellung` — vista general simplificada para el **cliente final**
- `Protokolldarstellung` / **Bewertungsprotokoll** — protocolo completo en **PDF** para el partner

**Base de datos:** investigación de mercado propia (`hauseigene Marktrecherchen`) + **valores de transacción reales retroalimentados** por fabricantes y clientes DAT (`rückgemeldete Echttransaktionswerte`) + datos de terceros (`Drittdaten`, asumidos sin verificar por DAT).

**Tipos cubiertos:** Pkw, SUV, motos, Transporter ≤3,5 t, Lkw pesado + Aufbauten.

---

### 4.4 SilverDAT Calculate (Reparaturkostenkalkulation — coste de reparación)
Basado en **datos originales de fabricante** (`Original-Herstellerdaten`) e instrucciones de reparación OEM.

**Campos atómicos:**
- `Ersatzteile` — piezas de recambio + nº de pieza + `topaktuelle Ersatzteilpreise` (precios al día)
- `Arbeitswerte (AW)` — unidades de trabajo / baremos de mano de obra
- `Lohnkosten` — coste de mano de obra
- `Lackierung` / `Lackierungsaufwände` — pintura: 3 sistemas → **DAT-Eurolack**, **AZT-Lack**, pintura del fabricante
- `Verbundarbeiten` — trabajos combinados/asociados
- `Verbundmaterialanzeige` — indicación de material compuesto (modelos nuevos)
- Daño de granizo (`Hagelschaden`) según norma **BVAT** / comisión alemana; `lackschadenfreie Hagelinstandsetzung`
- `Smart Repair` / `Spot Repair`
- Decisión reparar vs. sustituir
- Coste total de reparación
- Integración DMS + exportación

---

### 4.5 FastTrackAI® (reconocimiento de daños por IA)
**Detección/clasificación:**
- `Erkennung beschädigter Teile` — piezas dañadas (basado en datos OEM → diferencias por modelo)
- `Schadenart` — tipo de daño
- Descripción detallada con vías de reparación (Smart Repair vs. pintura extensa)
- `POI (Point of Impact / Einschlagpunkt)` — filtro punto de impacto → distingue daño viejo vs. nuevo

**Métricas de salida:**
- Coste de piezas de recambio
- Coste de mano de obra
- Coste de pintura
- Valoración total del daño
- Evaluación de **Totalschaden** (siniestro total)
- `Restwertprognose` (residual del siniestrado)

**Entrega:** webapp por enlace (sin descarga de store) + **API por componentes** (interfaz self-service, análisis de daño, cálculo) para embeber.

---

### 4.6 Schadenabwicklung / myClaim (gestión de siniestros)
Plataforma online paperless donde colaboran todas las partes.
**Campos/documentos:** `Schadensakte` (expediente digital) · `Fotos` · `Vollmachten` (poderes) · cálculo de coste · datos VIN (99,8 % precisión declarada) · valoración · `Freigabe` (autorización/liberación) · estado en tiempo real · facturación vía DMS.
**Partes:** Autohaus · Werkstatt · Versicherung · Sachverständige · Rechtsanwaltskanzleien.

---

### 4.7 webScan (análisis de mercado / price-to-market)
Escanea anuncios de **mobile.de** y **AutoScout24**. Análisis gráfico rápido del precio de oferta, criterios guardados, comparación por equipamiento. Es el panel "¿mi precio está en mercado?".

---

### 4.8 Mietwagenspiegel (índice de coche de alquiler)
**Campos:**
- **11 clases** de coche de alquiler (`Mietwagenklassen`) por coste de adquisición + motorización
- Coste regional (`regionale Kosten`): **min / max / media**
- `Nutzungsausfallentschädigung` — indemnización por privación de uso (incluye seguro, impuesto, depreciación, mantenimiento)
- Clase de vehículo de sustitución (vía VIN o selección)
- Reglas de reducción: −1 clase si >5 años, −2 clases si >10 años
- Defendible en tribunal (avalado por sentencias alemanas)

---

### 4.9 SilverDAT Connect / FleetForecast + Telemática (flota)
- `OEM-Daten per VIN-Abfrage`
- `Marktentwicklung & Restwertprognose` (gestión de riesgo de flota)
- `Live übertragene Telematikdaten` (km en vivo)
- `Multimarkenkonfigurator` — configurador multimarca de VN (specs + listenpreis)
- Intervalos de servicio según km real
- Cálculo automático de **CO₂** y consumo (datos OEM + reales)
- Optimización de valor residual en devoluciones de leasing

---

### 4.10 DAT Report (estudio anual de mercado — desde 1974, 52ª ed. 2026)
Encuesta a **4.666** consumidores (2.598 compradores VO; 2.068 reparación). 84 páginas, 108 gráficos. Tres dominios: compra VN/VO · uso/posesión · taller.

**Métricas atómicas (cifras 2025, DAT Report 2026):**
- `Durchschnittspreis Gebrauchtwagen` — **18.310 €** (−1,6 % YoY; serie 2016: 11.430 → 2025: 18.310)
- `Durchschnittspreis Neuwagen` (privado) — **44.560 €** (precio real pagado, no PVP)
  - Dt. Premiummarken **58.920 €** · Deutsche Marken **50.570 €** · Importmarken **37.470 €**
  - PHEV **64.570 €** · BEV **47.160 €** · Benzin **33.150 €** · Diesel **50.030 €**
- `Jahresfahrleistung` — **13.140 km/año** (36 % trabajo, 59 % privado, 5 % negocio)
- VO: **>6 M** Besitzumschreibungen; cuota **freier Handel 38 %** vs **Markenhandel 36 %** vs **Privatmarkt 26 %**
- Financiación VO: **49 %** financiados, leasing **0 %**; VN: **56 %** financiados, **23 %** leasing, 21 % sin financiación
- BEV: **30 %** ha conducido un BEV; **13 %** compraría BEV usado; **72 %** preocupado por valor de reventa de VE
- Taller: `Wartungskosten` **542 €** (+27 % vs 2020); `Reparaturkosten` **604 €** (+30 % vs 2020)
- Satisfacción: **>90 %** recomendaría a su concesionario
- Comprador VO medio: 44 años, ingreso neto hogar 3.790 €/mes, 73 % hombres
- Compra 100 % online: aceptable solo para ~1/3 de compradores VO; 7 % de VN privados vía plataforma online

---

### 4.11 DAT Barometer (análisis mensual de mercado)
Publicación mensual, "cifras válidas y representativas". Temas rotan: `Pkw-Kaufplaner` · `Pkw-Halter` · `Handel` · `Flotte und Fuhrpark` · `E-Mobilität`. Fuentes: BBDD DAT + cifras **KBA** (Kraftfahrt-Bundesamt) + encuestas propias. Evolucionó del "DAT Diesel Barometer" (2017).

---

### 4.12 Gebrauchtwagenmarkt (observación mensual de mercado) — **muy relevante para cardeep**
Informe mensual de DAT con métricas operativas del mercado VO:
- `Besitzumschreibungen` — transferencias de propiedad (volumen mensual; p.ej. feb-2026: **500.119**, −3,5 % YoY)
- `Standtage` / `Standzeit` — **días en stock** hasta vender, por tipo de combustible (BEV ≈ **110 días** en 2025)
- `Risikobestand` — **inventario de riesgo**: vehículos sin vender **>90 días**; coste de tenencia medio **23 €/día**; alcanzó **29 %** del stock de concesionario (vs mínimo **18 %** en jul-2022)
- Cambios de precio por combustible (Benzin −0,3 pp; Diesel ≈−2 pp; BEV −2,6 pp desde inicio de año)
- Pérdida de valor VE a 36 meses: **35-50 %** (Tesla Model 3 ≈ 40-46 %)

---

### 4.13 DAT Ibérica (España) — productos locales
- `Valor GANVAM-DAT` — **valor de referencia oficial** del mercado VO español (partnership GANVAM + DAT Group)
- `fastVO` — valoración VO instantánea por matrícula/VIN con dato de mercado conectado
- `fastValuate` / `weDAT®` — identificación + acceso al Valor GANVAM-DAT + peritación/presupuesto
- `FastEquipments` — specs técnicas, extras, versión exacta, **PVP** (precio venta público oficial)
- `FastTrackAI®` — daños por IA (móvil)
- `SilverDAT / MyClaim` — gestión de siniestros
- Tiempos y baremos de reparación; ciclo de uso del vehículo

---

## 5. Metodología / fuentes de dato

- **Transacciones reales retroalimentadas** (`rückgemeldete Echttransaktionswerte`) por fabricantes y clientes DAT — el núcleo del valor de mercado.
- **Investigación de mercado propia** (`hauseigene Marktrecherchen`) + observación continua de mercado (`DAT-Marktbeobachtung`).
- **>1.000.000 precios de transacción reales analizados al año** para el pronóstico residual.
- **Datos originales de fabricante/importador** (specs, equipamiento, instrucciones de reparación, precios de pieza).
- **Datos de terceros** (`Drittdaten`) — asumidos sin verificar (DAT no garantiza su exactitud).
- **webScan** sobre listings en vivo (mobile.de, AutoScout24) para benchmark de oferta.
- **Telemática** en vivo (km, consumo reales).
- **KBA** (oficina federal de tráfico) para volúmenes/matriculaciones.
- **Encuestas** a 4.666 consumidores (DAT Report) y paneles temáticos (Barometer).
- Metodología de pronóstico: **curvas de ciclo de vida** (`Lebenszykluskurve`) de modelos predecesores + **clustering de precios de transacción** + juicio experto de tendencia/competencia.

---

## 6. Entrega

| Canal | Detalle |
|---|---|
| **Webapp SilverDAT 3** | SaaS modular, responsive (iPad/Android/Windows), pantalla completa de cálculo |
| **API / Schnittstellen** | ~**400 partners de interfaz**; **>50 proveedores Software/DMS** con SilverDAT 3 integrado. Componentes API self-service (identificación, análisis de daño, cálculo). VIN-data liberado a todos los usuarios |
| **PDF** | `Bewertungsprotokoll` (protocolo de valoración), informes de siniestro, DAT Report |
| **Integración DMS** | exportación a marketplaces (heycar, mobile.de) y facturación |
| **Móvil** | FastTrackAI por enlace web; captura de fotos |
| **Publicaciones** | DAT Report (anual, de pago/pedido), Barometer (mensual), informes mensuales de mercado |
| **Multi-divisa / multi-idioma** | valuateFinance internacional |
| Protocolos exactos (REST/SOAP/XML) | [NO-VERIFICADO] — no publicados en abierto; se entregan a software houses bajo partnership |

---

## 7. Modelo de precio (descubierto vía calculadoras de partners)

> No es lista oficial DAT (son "Richtwerte" de partners autoixpert/dynarex), pero coherentes entre sí. [V2 entre 2 calculadoras]

**Modelo:** suscripción 12 meses (cancelable a fin de año) + cuota base mensual + **pago por transacción** + alta inicial + 2 usuarios incluidos.

| Tarifa | Cuota base | Incluido | Overage | Alta (año 1) | Coste año 1 / año 2+ |
|---|---|---|---|---|---|
| **Starter** | 49 €/mes | 2 transacciones | VIN 1,85 € · cálculo 20 € · valoración 4,50 € | 300 € | 960 € / 660 € |
| **Standard** | 135 €/mes | 185 cálculos/año | +10 €/cálculo extra | 825 € | 2.517 € / 1.692 € |
| **Premium** | 284 €/mes | 750 cálculos + 750 valoraciones/año | escalonado 5,40 €→4,30 € | 825 € | 4.305 € / 3.480 € |
| **Paquete inicial** | — | 100 cálculos + 100 valoraciones + alta | — | — | **1.680 €** pago único |

Add-ons: usuario extra **3,50 €/mes**; AZT-Lack **6 €/mes**; webinar **50 €**; Mietwagenspiegel incluido para evaluar transacciones.
Precios unitarios sueltos verificados: **VIN 1,85 € · valoración 4,50 € · cálculo 20 €**.

---

## 8. Patrón de COLOCACIÓN web (lo que cardeep imita)

| Dato | DÓNDE lo coloca DAT (sección/pantalla) |
|---|---|
| Identificación + specs (VIN, €uropa-Code, KBA, motor, CO₂, equipamiento) | **Cabecera de identificación**: caja de entrada VIN/matrícula → panel "identidad del vehículo" que se autorrellena en segundos antes de cualquier valoración |
| `Händlereinkaufswert` + `Händlerverkaufswert` | **Panel de resultado de valoración**: los dos valores como cifras protagonistas enfrentadas, con la `Handelsspanne` derivándolos. Vista "allgemeine Darstellung" para cliente final |
| Equipamiento de serie/opcional + su impacto en valor | Bloque desplegable bajo el panel de valor; opcionales con su depreciación (Zeitwert/Restwert) |
| Comparación de mercado (price-to-market) | **Pestaña/panel webScan** separado: listings vivos de mobile.de/AutoScout24 con distribución gráfica de precio |
| `Restwertprognose` (residual futuro) | **Curva de depreciación/ciclo de vida** con selectores de plazo × km; valor a fin de contrato. Dashboard para leasing/banca |
| Daño + coste (piezas/MO/pintura/total) | **Pantalla de siniestro (FastTrackAI/myClaim)**: foto con overlay + marcadores POI; desglose de coste; flag de Totalschaden; residual |
| KPIs de mercado (`Standtage`, `Risikobestand %`, índice de precio, volumen) | **Dashboard de observación mensual / Barometer**: series temporales + tiles KPI segmentados por combustible |
| Índice de alquiler | Selector de clase → tabla regional min/max/media + cifra `Nutzungsausfall` |
| Documento formal | **PDF (`Bewertungsprotokoll`)** para uso legal/pericial/tribunal |

**Patrón maestro DAT → cardeep:** (1) cabecera de identidad por VIN/matrícula → (2) dos cifras de valor protagonistas (compra/venta) con margen → (3) panel de comparación de mercado en vivo → (4) curva de depreciación/residual con sliders → (5) dashboard de KPIs de mercado por combustible → (6) salida PDF formal. Dos vistas por dato: simplificada (cliente) y protocolo completo (profesional).

---

## 9. Diferencial (lo que DAT ofrece y pocas/ninguna otra)

1. **Neutralidad institucional accionarial** (VDA+VDIK+ZDK) → estatus de "instancia neutral" y mandato especial; el dato es referencia de facto del sector DE.
2. **DAT €uropa-Code®** propietario de 15 dígitos: normalización cross-fabricante única para comparar/peritar/flota.
3. **Transacciones reales retroalimentadas por OEM y clientes** (no solo asking prices) como base del valor.
4. **Suite end-to-end** en una sola plataforma: identificación → valoración → cálculo de reparación → siniestro IA → residual → telemática. Pocos competidores cubren todo el ciclo.
5. **SoH de batería** integrado en la valoración de VE (vía diagnóstico independiente).
6. **Mietwagenspiegel defendible en tribunal** (avalado por sentencias) — nicho legal de privación de uso.
7. **DAT Report** (serie 1974) y observación mensual de mercado → autoridad de mercado, no solo herramienta.
8. **99,8 %** del parque turismo DE identificable.
9. Ecosistema **~400 partners de interfaz / >50 DMS** — distribución profunda.
10. **Valor GANVAM-DAT** como referencia oficial en España.

---

## 10. Gaps (lo que DAT NO ofrece / debilidades)

1. **Historial de vehículo** (siniestros previos, titularidades, fraude de km) — no es un proveedor de historial/procedencia tipo HPI Check / CARFAX. Captura km y Vorbesitzer puntuales en valoración, pero no un registro histórico consolidado.
2. **Días-para-vender por vehículo individual** y `market days supply` como métrica de instrumento por ficha — lo publica agregado (Standtage de mercado), no como dato por unidad en la ficha de valoración.
3. **`price-to-market %`** explícito por anuncio — webScan da comparación gráfica, pero no un índice numérico tipo "97 % del mercado" por vehículo (a diferencia de Indicata/vAuto).
4. **Cobertura geográfica de valoración limitada a ~11 países** (no pan-EU completa ni global; débil fuera de DACH+Sur/Este de Europa).
5. **API pública/autoservicio abierta**: no hay docs REST públicas; integración mediada por partnership (fricción para developers).
6. **Transparencia de precios**: lista oficial no pública; todo "bajo consulta".
7. **Datos de subasta/wholesale en vivo** y arbitraje cross-platform — no es su terreno (sí lo es de Black Book / AUTO1 / Manheim).
8. **Indicador demanda/oferta** y velocidad de rotación granular por modelo/región como producto analítico de stock (Indicata-style) — cubierto solo parcialmente vía Risikobestand/Standtage agregados.
9. **Foco geográfico**: producto y UI muy centrados en Alemania; el dato español llega vía DAT Ibérica/GANVAM, no como producto DAT homogéneo.
10. **Drittdaten sin garantía**: DAT declara explícitamente que no responde de actualidad/exactitud de datos de terceros.

---

## 11. Fuentes (URLs)

**DAT directas (primarias):**
- https://www.dat.de/ — home, navegación, productos, identidad/HQ
- https://www.datgroup.com/datgroup/about-us/ — fundación 1931, VDA/VDIK/ZDK, 550 empleados/22 países, dirección
- https://www.datgroup.com/ — cobertura internacional, catálogo de soluciones
- https://www.datgroup.com/de-at/loesungen/fahrzeugbewertung/ — soluciones de valoración, 72m/200.000km, 9 países
- https://www.dat.de/silverdat/ — módulos SilverDAT
- https://www.dat.de/gebrauchtfahrzeugwerte/ — calculadora consumer
- https://www.dat.de/gebrauchtfahrzeugbewertung/ — valoración dealer, tipos de vehículo, SoH
- https://www.dat.de/vin-abfrage/ — VIN-Abfrage
- https://www.dat.de/europacode/ + .../produktbeschreibung-europa-code.pdf — €uropa-Code 15 dígitos
- https://www.dat.de/reparaturkostenkalkulation/ — cálculo de reparación, sistemas de pintura
- https://www.dat.de/fasttrack-ai/ — FastTrackAI (POI, salidas)
- https://www.dat.de/schadenabwicklung/ — myClaim
- https://www.dat.de/mietwagenspiegel/ — 11 clases, Nutzungsausfall
- https://www.dat.de/restwertprognose/ — pronóstico residual, >1M transacciones, ciclo de vida
- https://www.dat.de/fleet/ — FleetForecast / SilverDAT Connect / telemática
- https://www.dat.de/schnittstellen/ — ~400 partners, >50 DMS
- https://www.dat.de/barometer/ — Barometer, fuentes KBA
- https://www.dat.de/report/ — DAT Report metodología (4.666, 84p, desde 1974)
- https://www.dat.de/fileadmin/.../DAT-Report-2026-Kurzbericht.pdf — cifras 2025 (18.310 €, 44.560 €, 13.140 km, 542/604 €, 38/36/26 %)
- https://www.dat.de/fileadmin/de/download/rechtliches/produktbeschreibung-silverdat-valuatefinance.pdf — campos atómicos valoración, 11 países, métodos de ID
- https://www.dat.de/news/gebrauchtwagenmarkt-im-februar-2026/ — Besitzumschreibungen 500.119

**DAT Ibérica (España):**
- https://discover.datiberica.com/ — productos ES, Valor GANVAM-DAT
- https://discover.datiberica.com/fastvo/ — fastVO
- https://discover.datiberica.com/fastequipments — FastEquipments (PVP)

**Secundarias / verificación cruzada:**
- https://www.bewerta.de/auto-kfz-veraeusserungswert — definición de tipos de valor (Händlereinkaufswert/Wiederbeschaffungswert/Restwert)
- https://www.kfz-betrieb.vogel.de/...standzeiten-preise... — Risikobestand (>90 días, 23 €/día, 29 % vs 18 %), Standtage por combustible
- https://www.auto-medienportal.net/artikel/detail/69318 — DAT Report 2026 (cifras)
- https://www.autoixpert.de/dat-preisrechner — precios SilverDAT (tarifas Starter/Standard/Premium)
- https://dynarex.de/de/preisrechner/ — precios (confirma modelo)
- https://www.autohaus.de/.../dat-verfuegbare-vin-daten-fuer-alle-nutzer-freigegeben-2777943 — liberación de VIN-data
- https://www.pixelconcept.de/en/dat-fahrzeugbewertung.../ — uso dealer, DAT-Preis neutral

---

### Notas de verificación
- Plantilla/países: discrepancia 22 vs 25+ entre páginas DAT → reportada, no resuelta.
- Países de valoración: la cifra autoritativa es **11** (PDF de producto valuateFinance); "9 países" en datgroup incluye Rusia → lista distinta, marcada.
- Precios: son Richtwerte de partners (no lista oficial DAT), pero consistentes entre dos fuentes; DAT no publica tarifa abierta.
- Protocolos de API: NO verificados (no públicos).
