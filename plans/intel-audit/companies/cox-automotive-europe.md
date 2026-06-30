# Cox Automotive Europe — Auditoría de Inteligencia

> Slug: `cox-automotive-europe` · Subdominio objetivo: `wholesale-intelligence`
> Web matriz: https://www.coxautoinc.eu/ · Auditado: 2026-06-30
> Tipo: grupo paneuropeo de soluciones de automoción (remarketing + valoración + datos de mercado + funding + retail digital).
> NOTA metodológica: `coxautoinc.eu` está tras WAF de Azure Front Door y devuelve 403 ("The request is blocked") tanto a fetch directo como a headless y a proxy lector. La inteligencia se ha reconstruido vía (a) dominios de marca independientes que SÍ responden (`evavaluations.com`, `rmsautomotive.eu`, `manheim.co.uk`, `dealerauction.co.uk`, `nextgearcapital.co.uk`), (b) snippets de buscador de las propias páginas `coxautoinc.eu`, y (c) prensa sectorial. Cada dato lleva su marca de verificación.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Razón social (UK) | Cox Automotive UK Limited (Companies House nº 03183918) | [VERIFICADO] GOV.UK |
| Razón social (entidad europea) | Cox Automotive Europe Limited (Companies House nº 16409560) | [VERIFICADO] GOV.UK |
| HQ Europa | Central House, Leeds Road, Rothwell, **Leeds, LS26 0JE**, Reino Unido | [VERIFICADO] búsqueda corporativa |
| Origen operaciones UK | Operaciones UK desde **1996** (linaje Manheim Auctions UK) | [VERIFICADO con matices] — el dato "1996" se refiere a la operación UK, no a la matriz |
| Matriz directa | **Cox Automotive Inc.** (Atlanta, GA, EE.UU.; formada 2014 al consolidar Manheim, Autotrader, Kelley Blue Book, Dealertrack, NextGear…) | [VERIFICADO] |
| Matriz última | **Cox Enterprises Inc.** — conglomerado privado de la familia Cox, Atlanta; ~$22 bn de ingresos anuales; también dueña de Cox Communications y prensa (Atlanta Journal-Constitution) | [VERIFICADO] |
| Naturaleza | Privada (no cotiza). División europea de un grupo global de ~13 marcas de datos/servicios de automoción | [VERIFICADO] |
| Eslogan | "Transforming Automotive Ecosystems" / "Transforming the way the world buys, sells, owns and uses vehicles" | [VERIFICADO] |

**Categorías de negocio en Europa:** (1) Remarketing y subasta mayorista (Manheim, Manheim Express, Dealer Auction), (2) Valoración y tasación (eVA Valuations & Appraisals), (3) Inteligencia/datos de mercado (Market Insight Data Dashboard, The Gavel, Wholesale Price Index), (4) Software de gestión de flota/remarketing (RMS Automotive), (5) Funding de stock (NextGear Capital), (6) Retail digital y software de financiación (Modix, Codeweavers), (7) Logística de vehículos (Movex), (8) Inspección y servicios de vehículo (Manheim Inspection Services, Manheim Vehicle Services), (9) Electrificación (EV Battery Solutions).

**Clientes objetivo:** fabricantes/OEM, flotas y empresas de leasing, captives/financieras, concesionarios franquiciados e independientes, plataformas/portales. Modelo B2B puro.

---

## 2. Cobertura

| Eje | Detalle | Estado |
|---|---|---|
| Países (subasta física Manheim) | **Reino Unido, España, Portugal** (mayoristas multicanal) | [VERIFICADO] |
| Países (Manheim Express, dealer-to-dealer digital) | **Alemania** (lanzado 2020; base operativa Koblenz), **España, Portugal** (Europa continental) | [VERIFICADO] |
| Funding (NextGear Capital) | **Reino Unido e Irlanda** | [VERIFICADO] |
| Retail digital (Modix) | Global/EU (20+ años); Codeweavers UK | [VERIFICADO] |
| Logística (Movex) | Reino Unido (red nacional 600+ transportistas) | [VERIFICADO] |
| Scope vehículo | **Usado mayoritariamente** (remarketing/subasta/valoración usado); también **nuevo** (Manheim Vehicle Services prepara vehículo nuevo; new car registrations/forecasts en el dashboard) | [VERIFICADO] |
| Tipos de vehículo | **Turismo (car), LCV/furgoneta (van), camión (truck), maquinaria (plant), VE/EV**. eVA cubre car + LCV; Manheim subasta car/van/truck/plant | [VERIFICADO] |
| Huella física UK | 250.000+ vehículos/año procesados en 6 centros dedicados de Vehicle Services | [VERIFICADO] manheim.co.uk |

---

## 3. Productos y campos atómicos

### 3.1 eVA Valuations & Appraisals — *valoración + tasación* (NÚCLEO de datos para cardeep)
"A collection of state-of-the-art vehicle valuation, appraisal and buying solutions for retailers, manufacturers and fleets." Cubre **turismos y LCV**. [VERIFICADO]

**Salidas de valoración (campos):**
- **Trade value** (valor de trade-in / mayorista) [VERIFICADO]
- **Retail value** — precio de venta al público en vivo de **Auto Trader**, integrado desde nov-2025; primera vez que un appraisal tool muestra trade + retail en una sola vista [VERIFICADO: AIM Group, AM-online, bodyshopmag]
- **Valoración en tiempo real**, ajustable a las reglas/requisitos del concesionario [VERIFICADO]
- **Precisión declarada hasta el 99%** [VERIFICADO: prensa sectorial]
- Ajustes implícitos por **kilometraje, condición, derivado/especificación** (valoración tras tasación) [VERIFICADO parcial — los inputs de tasación alimentan el valor ajustado]

**Inputs de tasación capturados (eVA Self-Inspect + in-store + roadside):**
- Historial de servicio (service history)
- Número de llaves
- Imágenes/fotos del vehículo
- Daños (damage)
- Estado de neumáticos (tyre condition)
- Olor (odour) [VERIFICADO vía informe de inspección Manheim, criterio compartido]
- Equipamiento/features (ordenados por importancia)
- Derivado y especificación
- **LCV-específico:** condición de zona de carga (load area), rotulación (signwriting), estanterías/racking, accesorios, mayor tolerancia a uso/desgaste; grading **NAMA para LCV** [VERIFICADO]

**Volumen de datos motor de valoración:** "más de **800.000** observaciones de precio diarias" (evavaluations.com) / "más de **1.000.000** de observaciones de precio al día" (anuncios de la integración Auto Trader). Discrepancia por fuente/fecha — se reportan ambos. [VERIFICADO ambos, con conflicto declarado]

**Canales de tasación:** online (Self-Inspect, móvil, remoto), in-store, roadside. [VERIFICADO]

---

### 3.2 Dealer Auction — *marketplace mayorista digital* (JV Cox Automotive + Auto Trader)
"The smartest digital wholesale marketplace, giving buyers and sellers more choice, better insight and greater margin." Fusiona dealer-auction.com + Manheim Online + Auto Trader Smart Buy. [VERIFICADO]

**Escala:** 600+ subastas terminando/día · 5.000+ compradores activos · 120.000+ pujas/mes · 11.000+ vehículos nuevos/mes. [VERIFICADO]

**Campos/insights por vehículo (inteligencia de Auto Trader superpuesta a cada lote):**
- **Auto Trader Retail Rating** — puntuación **/100**, local al código postal del comprador; ≥80/100 = rinde bien en exposición. Se calcula con make/model + edad + kilometraje y tres medidas: [VERIFICADO: dealerauction.co.uk/blog]
  - **Live market supply** (oferta de la última semana vs media de 6 meses → alta/baja)
  - **Live buyer demand** (consumidores buscando ese vehículo vs lo habitual → mayor/menor)
  - **Average days to sell** (rapidez de venta al retail)
- **Auto Trader average days to sell** — días medios de venta al retail en el área local [VERIFICADO]
- **Average retail sold price** por vehículo, con resumen de precio **máximo/mínimo** y kilometraje [VERIFICADO]
- Smart pricing / price guidance · comparación de precios · predicción de rendimiento del vehículo en el área local · comportamiento de búsqueda del consumidor por región [VERIFICADO]
- Stock alerts / smart alerts (políticas + notificaciones por coincidencia) · intelligent bidding · lanes virtuales automáticos · filtros avanzados [VERIFICADO]
- Funding integrado (NextGear) + movimiento integrado (Movex) "al clic" [VERIFICADO]

---

### 3.3 Manheim (Auction / Inspection / Vehicle Services) — *subasta + inspección + datos*
**Manheim Auction Services:** mayoristas multicanal UK/España/Portugal; subasta física + virtual/**Simulcast**; car/van/truck/plant. [VERIFICADO]
**Manheim Vehicle Services:** preparación de vehículo nuevo, in-life, **defleet**; 250k+/año en 6 centros. [VERIFICADO]
**Manheim Inspection Services:** inspección on-site y centralizada; **SureCheck** (mecánica), DataCleanse, Driver Sales. [VERIFICADO]

**Grading NAMA (cosmético) — turismo (campos atómicos):** [VERIFICADO: manheim.co.uk/campaigns/nama-grading-car]
- **Grade 1**: defectos cosméticos mínimos — abolladuras ≤30 mm, arañazos ≤25 mm, picotazos de cristal ≤10 mm, arañazos de paragolpes ≤100 mm, daño de llanta menor, roces de interior leves.
- **Grade 2**: Grade 1 + un defecto adicional (pintura >25 mm en panel / >100 mm en paragolpes, abolladura >30 mm, o cristal >10 mm).
- **Grade 3**: Grade 1-2 + hasta 5 paneles con defecto de pintura >25 mm, hasta 3 paneles/paragolpes con abolladura >30 mm.
- **Grade 4**: Grade 1-3 + 1 panel con >30% de daño o grieta significativa de paragolpes, hasta 10 paneles con defectos de pintura, hasta 7 paneles/paragolpes con abolladura >30 mm.
- **Grade 5**: Grade 1-4 + >2 paneles/paragolpes con >30% de daño, 8+ paneles/paragolpes con abolladura >30 mm, 11+ paneles con defectos de pintura, hasta 1 panel estructural con >30% de daño.
- **Grade U (Unclassified)**: "uneconomical to appraise" — supera Grade 5, daño de accidente sustancial, múltiples piezas faltantes, o km/edad muy altos.
- **Standard Viewing Angle (SVA):** 2 m a 90°, ±45°. Sistema de **puntos por tipo y severidad**. Sólo cosmético exterior+interior; **excluye** mecánica/eléctrica, bajos, motor, transmisión, historial. Variante **NAMA LCV** (furgonetas).

**Informe de inspección Manheim (campos):** [VERIFICADO: manheim.co.uk/campaigns/inspection-report]
- Historial del vehículo / uso previo (previous usage)
- Olor (odour)
- Equipamiento/features (orden de importancia definido por cliente)
- **Checklist SureCheck** (mecánica/seguridad): motor, transmisión/caja, dirección, frenos "y más"; inspectores IMI-approved y NAMA-accredited; variantes Cars / LCV / EV [VERIFICADO]
- Descripción de **ruedas y neumáticos** en cada informe
- Líneas de daño con **hasta 5 imágenes de alta resolución por línea**, ordenadas por **severidad de grado NAMA**
- Kilometraje
- Formato **PDF interactivo** (ver/imprimir/descargar) accesible desde el listado online (PC/portátil/tablet/móvil)

**Productos de datos Manheim:** **The Gavel** (insights trimestrales de subasta mayorista), buscador Truck & Plant Machinery, historial/provenance del vehículo, actualizaciones de stock, calendario de eventos personalizado. [VERIFICADO]

**Manheim Express:** plataforma de subasta digital dealer-to-dealer para Europa continental (DE/ES/PT). [VERIFICADO]

---

### 3.4 Market Insight — Data Dashboard + Wholesale Price Index (INTELIGENCIA DE MERCADO)
"Snapshot of the latest UK market data in one place", combinando datos propios (Manheim) con SMMT, Auto Trader y cap hpi. [VERIFICADO: snippets coxautoinc.eu/data-dashboard]

**Métricas — bloque RETAIL / MATRICULACIONES / PRODUCCIÓN:**
- New car registrations (fuente SMMT)
- **New car forecast** — 3 escenarios a 12 meses: **upside / baseline / downside** (macro, política, industria) — propio Cox, trimestral
- Used car transactions
- Used car forecast
- UK car production (SMMT)
- Retail margin
- Retail demand
- Retail supply
- **Market health**

**Métricas — bloque WHOLESALE (datos Manheim):**
- Average **days to sell** (p.ej. 35 días dic-2025)
- Average **sold price** (p.ej. £7.838 oct)
- Average **mileage** (p.ej. 67.500 dic-2025)
- Average **age (months)**
- **First-time conversion %** (p.ej. 78,4% vendidos a la primera, dic-2025)
- **cap value movements** (fuente cap hpi)
- **Wholesale supply index**
- **Wholesale demand index**
- **Wholesale Price Index** — índice de precio mayorista ajustado por **mix, kilometraje y estacionalidad** (metodología tipo MUVVI; el MUVVI = 206,0 es la versión USA, la UK publica su propio índice mensual) [VERIFICADO con matiz geográfico]

---

### 3.5 RMS Automotive — *software de remarketing/gestión de flota* (modular)
"Transforming remarketing outcomes for large fleet operators… full visibility and control." Vista única **factory order → disposal**. [VERIFICADO: rmsautomotive.eu]

**Campos/capacidades atómicas:**
- **Recomendación de precio VIN-específico** (data science)
- **Recomendación de reacondicionamiento** óptimo
- **Recomendación de distribución de inventario / canal**
- **Days in stock / days to sale** (aceleración, listado en punto de defleet)
- **Velocity** de venta
- **Residual value** management / optimización de valor del vehículo
- Identificación de **riesgo** y gestión de **costes**
- Etapa de **ciclo de vida** (factory order → disposal)
- KPIs de proceso y **reporting en tiempo real**; agregación de sistemas propios + terceros; automatización de informes/acciones
- Multi-mercado / transacciones cross-border

---

### 3.6 NextGear Capital — *funding de stock (floorplan)*
"Flexible, straightforward and dependable vehicle stock funding for independent and franchised dealers in the UK and Ireland." Desde 2014, £8 bn+ financiados. Financia usado + LCV. [VERIFICADO: nextgearcapital.co.uk]

**Campos atómicos:**
- **Credit line / límite de funding**
- Cobertura **100% del hammer price** + **buyer fees** + **delivery fees** en una transacción
- **Plazo de funding: hasta 150 días**
- **Days on plan** / unidades en plan
- Pago confirmado instantáneo en plataformas asociadas; compra desde cualquier fuente (subasta o no)
- Portal/app: info de floor plan + dashboards (móvil), **AutoPay**, flooring de compras no-subasta, visualización de **títulos**, gestión de **auditoría**

---

### 3.7 EV Battery Solutions — *electrificación / salud de batería*
Servicios de ciclo de vida de batería para fabricantes y flotas. [VERIFICADO en catálogo EU; detalle técnico mayormente USA]
**Campos:** **State of Health (SoH %)**, **degradación %**, salud de batería **VIN-específica**, **certificado PDF** de salud de batería; usa tecnología **LotVision** de Manheim; vuelca a Condition Reports (CR) y Vehicle Detail Pages (VDP). 6 centros de batería, 80 ubicaciones de reparación, 850+ técnicos, 30+ patentes. [VERIFICADO — geografía USA-céntrica, marca listada también en EU]

### 3.8 Codeweavers — *software de financiación/commerce retail*
Soluciones omni-canal para OEM/retailers/lenders/portales. [VERIFICADO: codeweavers.net]
**Campos:** calculadora de financiación, **finance quote**, **APR**, **monthly payment**, **deposit/term**, stock locator de coche nuevo, finance application, checkout, e-signing; integra DMS/CRM/POS.

### 3.9 Modix — *retail/marketing digital*
20+ años; webs de concesionario, merchandising online, generación de leads. Dato atómico escaso (es publicación/marketing). [VERIFICADO]

### 3.10 Movex — *logística de vehículos*
"Specialist logistics platform… connecting the UK's largest network of transport providers." 600+ transportistas. [VERIFICADO: coxautoinc.eu/our-products/movex]
**Campos:** **quote de movimiento** (precio), **booking**, **estado del movimiento**, **ubicación/tracking** del vehículo (ETA implícito).

---

## 4. Metodología y fuentes de datos
- **Datos propios mayoristas Manheim:** millones de transacciones reales de subasta UK/ES/PT → valores, índices, days-to-sell, conversión, mileage/age medios. [VERIFICADO]
- **Datos retail Auto Trader** (vía JV Dealer Auction y partnership eVA nov-2025): análisis diario de 1M+ vehículos de listings vivos + contribuciones de retailers/OEM/flotas/subastas → Retail Rating, retail price, supply/demand vivos. [VERIFICADO]
- **Terceros del dashboard:** SMMT (matriculaciones, producción), cap hpi (cap value movements), Auto Trader (retail). [VERIFICADO]
- **eVA engine:** combina wholesale Cox + retail (800k–1M+ observaciones/día), precisión hasta 99%. [VERIFICADO]
- **Wholesale Price Index:** ajuste estadístico por **mix, kilometraje, estacionalidad** para aislar el movimiento real de precio (metodología MUVVI replicada en UK). [VERIFICADO]
- **Grading NAMA:** estándar National Association of Motor Auctions; inspectores cualificados; sistema de puntos por severidad. [VERIFICADO]
- **EV SoH:** diagnóstico VIN-específico vía LotVision + lab de electrónica. [VERIFICADO]

---

## 5. Entrega (delivery)
| Canal | Producto/uso | Estado |
|---|---|---|
| **Dashboard web** | Market Insight Data Dashboard (snapshot UK mensual) | [VERIFICADO] |
| **Plataforma SaaS web** | RMS Automotive (modular), Dealer Auction (marketplace), Manheim (subasta online/Simulcast) | [VERIFICADO] |
| **App móvil** | eVA Self-Inspect (tasación remota), Movex (booking/tracking), NextGear (portal/dashboard) | [VERIFICADO] |
| **Widget embebido** | eVA valuation widget en web del concesionario; calculadoras Codeweavers en portales | [VERIFICADO] |
| **Integración DMS/CRM/POS** | eVA → DMS; Codeweavers → DMS/CRM/POS | [VERIFICADO] |
| **PDF / informe** | Informe de inspección Manheim (PDF interactivo), certificado EV SoH (PDF), The Gavel (publicación trimestral) | [VERIFICADO] |
| **Subasta física + virtual** | Manheim Auction Services (UK/ES/PT), Simulcast | [VERIFICADO] |
| **API / feed** | No documentada públicamente una API de datos abierta; integración es vía producto. Contacto de datos: manheim.data@coxautoinc.com | [ASUMIDO/no verificado — no hay portal de API público localizable bajo el WAF] |

---

## 6. Precio
- **No hay precios públicos.** Modelo B2B por cotización/contrato/suscripción según producto y volumen. [VERIFICADO por ausencia: ninguna página de pricing accesible]
- ⚠️ **DESCARTADO POR NO FIABLE:** una extracción automática inicial sugirió tarifas "$99/mes, tiers Valuations/Premium/Pro" para eVA. Es **incoherente** (eVA es UK, factura en £, B2B) y muy probablemente una **alucinación/confusión** del resumidor con otro producto USA. **NO se reporta como dato.** [marcado ASUMIDO-ERRÓNEO, excluido]
- NextGear: coste financiero sobre línea de funding (no publicado). [ASUMIDO]

---

## 7. Placement (DÓNDE se coloca cada dato — patrón a replicar por cardeep)

| Dato/métrica | Pantalla/sección donde aparece | Estado |
|---|---|---|
| Trade value + Retail value (lado a lado) | **eVA — vista de tasación in-store / resultado de appraisal** (una sola vista, primera vez trade+retail juntos) | [VERIFICADO] |
| Inputs de tasación (historial, llaves, fotos, daños, neumáticos, LCV load/racking) | **eVA Self-Inspect — flujo paso a paso en móvil** (cliente sube antes de visitar) | [VERIFICADO] |
| Retail Rating /100, supply, demand, days to sell | **Dealer Auction — superpuesto sobre CADA listado/lote** y en el anuncio a página completa | [VERIFICADO] |
| Average retail sold price + máx/mín + km | **Dealer Auction — anuncio a página completa del vehículo** | [VERIFICADO] |
| Grado NAMA + líneas de daño (5 fotos c/u) + ruedas/neumáticos | **Informe de inspección Manheim — PDF interactivo dentro del listado online del lote** | [VERIFICADO] |
| Checklist mecánico SureCheck | **Informe de inspección Manheim — sección mecánica del PDF** | [VERIFICADO] |
| SoH % batería + certificado | **Condition Report (CR) y Vehicle Detail Page (VDP)** del lote (vuelca automáticamente) | [VERIFICADO — patrón Manheim USA, exportable] |
| New car registrations/forecast, used transactions/forecast, production, retail margin/demand/supply, market health | **Market Insight Data Dashboard — bloque RETAIL/PRODUCCIÓN (tiles superiores)** | [VERIFICADO vía snippets] |
| Days to sell, sold price, mileage, age, first-time %, cap movements, supply/demand index | **Market Insight Data Dashboard — bloque WHOLESALE (tiles inferiores)** | [VERIFICADO vía snippets] |
| Precio VIN-recomendado, reacondicionamiento, distribución, days-in-stock, residual, riesgo | **RMS Automotive — dashboard de portfolio único (factory→disposal), módulos por necesidad** | [VERIFICADO] |
| Credit line, days on plan, hammer/fees, título, auditoría | **NextGear — portal/app de floor plan (dashboard móvil)** | [VERIFICADO] |
| Finance quote / APR / monthly payment | **Codeweavers — calculadora embebida en web del retailer/portal** | [VERIFICADO] |
| Quote/estado/ubicación de movimiento | **Movex — app/plataforma de logística** | [VERIFICADO] |

**Patrón maestro para cardeep:** Cox separa con nitidez (1) **datos del vehículo individual** (valoración trade/retail + grado de condición + fotos de daño + SoH + historial) que se incrustan en la **ficha/listado del lote** o en el **flujo de tasación**; de (2) **datos agregados de mercado** (índices, days-to-sell, supply/demand, forecast) que viven en un **dashboard separado** organizado por bloques retail vs wholesale. El **Retail Rating /100 local al código postal** es el patrón de "semáforo accionable" por lote: un único score compuesto (supply+demand+days-to-sell) colocado encima de cada vehículo.

---

## 8. Diferencial (lo que ofrece y otros no)
1. **Trade + Retail en una sola vista** dentro del appraisal (Cox wholesale + Auto Trader retail), primero del mercado UK (nov-2025). [VERIFICADO]
2. **Datos propios de subasta real** (Manheim UK/ES/PT) — no estimaciones: transacciones reales → days-to-sell, conversión, mileage/age medios, índices supply/demand mayoristas. [VERIFICADO]
3. **Retail Rating /100 hiperlocal** (al código postal) compuesto de supply+demand+days-to-sell vivos de Auto Trader, superpuesto a cada lote de subasta. [VERIFICADO]
4. **Valoración + tasación + grading NAMA + funding + logística integrados** en un mismo ecosistema (appraise → list → fund → move → sell sin salir). [VERIFICADO]
5. **eVA primer LCV appraisal/valuation remoto del mercado** (load area, signwriting, racking, NAMA-LCV). [VERIFICADO]
6. **SoH de batería VIN-específico** volcado a la ficha del lote (electrificación). [VERIFICADO patrón USA]
7. **Cobertura sur de Europa real** (España y Portugal con subasta física propia + Manheim Express), poco común en players UK-céntricos. [VERIFICADO]

## 9. Gaps (lo que NO ofrece / límites)
1. **Sin API de datos pública** ni pricing transparente: todo es B2B por contrato; muro de acceso (WAF) y producto cerrado. [VERIFICADO por ausencia]
2. **Cobertura geográfica fragmentada:** fuerte en UK; ES/PT/DE parciales por marca; **sin presencia France/Italia/Nordics** propia documentada (a diferencia de Autovista/Indicata). [VERIFICADO por ausencia]
3. **Dashboard de mercado = solo UK** (Market Insight es snapshot UK); no hay dashboard paneuropeo equivalente. [VERIFICADO]
4. **Valoración retail depende de Auto Trader** (partner externo), no de guía propia paneuropea tipo cap/Schwacke/Eurotax. [VERIFICADO]
5. **No es guía de valores histórica/forecast por VIN al estilo libro** (residual value curves a 36/48 meses por trim) como ALG/Autovista RV — su forecast es de mercado nuevo agregado, no curva de depreciación por vehículo. [ASUMIDO — no se halló producto de RV curve por trim en EU]
6. **Sin historial de siniestros/título estilo Carfax/HPI Check propio** dentro del paquete de datos europeo (provenance se menciona pero no como producto de historial al consumidor). [ASUMIDO/no verificado]
7. **Grading NAMA es solo cosmético** (excluye mecánica salvo SureCheck aparte). [VERIFICADO]
8. **eVA: posiciones de valoración exactas no documentadas** públicamente (no se confirma si expone cap clean/average/below ni mileage-adjusted explícito como números separados). [no verificado — marcado gap de transparencia]

---

## 10. Fuentes (URLs)
- https://www.coxautoinc.eu/our-products/ (taxonomía de marcas — vía proxy lector; original tras WAF) [VERIFICADO]
- https://www.coxautoinc.eu/data-dashboard/ (métricas dashboard — vía snippets de buscador; original 403) [VERIFICADO parcial]
- https://evavaluations.com/ (eVA features, 800k observaciones/día) [VERIFICADO]
- https://evavaluations.com/cox-automotive-launches-first-to-market-lcv-appraisal-and-valuation-platform/ (LCV: load area, signwriting, racking, NAMA-LCV) [VERIFICADO]
- https://aimgroup.com/2025/11/03/cox-automotive-adds-autotrader-pricing-data-to-eva-valuations-and-appraisals/ (trade+retail, 1M observaciones) [VERIFICADO]
- https://www.am-online.com/news/cox-automotive-teams-with-autotrader-on-valuation-data-integration [VERIFICADO]
- https://www.bodyshopmag.com/2025/news/cox-automotive-and-auto-trader-partner-on-vehicle-values/ [VERIFICADO]
- https://www.dealerauction.co.uk/about-us/ + https://www.dealerauction.co.uk/blog/how-to-make-dealer-auctions-data-work-for-you/ (Retail Rating /100, supply/demand/days-to-sell) [VERIFICADO]
- https://rmsautomotive.eu/ (RMS módulos, VIN pricing, days in stock, lifecycle) [VERIFICADO]
- https://www.manheim.co.uk/ (servicios, The Gavel, filtros) [VERIFICADO]
- https://www.manheim.co.uk/campaigns/nama-grading-car (Grades 1-5/U, SVA, umbrales mm) [VERIFICADO]
- https://www.manheim.co.uk/campaigns/inspection-report (campos del informe, 5 fotos/línea, PDF interactivo) [VERIFICADO]
- https://www.manheim.co.uk/our-services/inspection-services/surecheck (SureCheck mecánica) [VERIFICADO]
- https://nextgearcapital.co.uk/ + https://www.nextgearcapital.com/ (150 días, 100% hammer+fees, portal) [VERIFICADO]
- https://www.coxautoinc.com/ev-battery-solutions/ (SoH %, certificado, LotVision) [VERIFICADO]
- https://www.codeweavers.net/ (finance quote/APR/payment, e-signing) [VERIFICADO]
- https://www.coxautoinc.eu/our-products/movex/ (quote/booking/tracking, 600+ transportistas) [VERIFICADO vía snippet]
- https://find-and-update.company-information.service.gov.uk/company/16409560 (Cox Automotive Europe Ltd) + /company/03183918 (Cox Automotive UK Ltd) [VERIFICADO]
- https://en.wikipedia.org/wiki/Cox_Enterprises (matriz, Atlanta, ~$22bn) [VERIFICADO]
- https://www.coxautoinc.com/insights/manheim-used-vehicle-value-index-mid-december-2025-trends/ (metodología índice: mix/mileage/seasonality) [VERIFICADO]

### Conflictos / no verificados declarados
- Observaciones de precio diarias eVA: **800.000** (evavaluations.com) vs **1.000.000+** (anuncios Auto Trader) — ambos reportados.
- Pricing "$99/mes Valuations/Premium/Pro" → **descartado como erróneo** (incoherente con B2B/UK/£).
- API/feed de datos abierto, curvas de RV por trim, historial de siniestros propio EU → **no hallados** (marcados como gaps).
- `coxautoinc.eu` tras WAF Azure → placement del dashboard reconstruido por snippets, no por render directo de la página.
