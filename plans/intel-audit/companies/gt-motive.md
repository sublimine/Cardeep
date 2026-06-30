# Auditoría atómica — GT Motive (Allianz X)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de **datos de reparación / estimática de siniestros** de automoción. Web: https://gtmotive.com/en/ · UK: https://gtmotive.co.uk/ · DE: https://gtmotive.de/ · App: https://estimate.mygtmotive.com/
> Subdominio Cardeep (taxonomía interna): **valuation** (clasificación del universo, NO un subdominio web; `valuation.gtmotive.com` **no resuelve** — verificado vía DNS ENOTFOUND).
> Fecha auditoría: 2026-06-30. Método: navegación exhaustiva de los sitios EN/UK/DE + página de productos + **Manual de Usuario GT Estimate V21.1** (PDF 102 págs, extraído con PyMuPDF) + notas de prensa (Allianz, GT Fusion, GT QCheck, Eco Repair Score) + prensa sectorial (I Love Claims, Insurance Business, Claims Media) + `_audit_input.json` de Cardeep.
> Convención: [V] = verificado leyendo la fuente · [A] = asumido/inferido (marcado siempre).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **GT Motive** (producto estrella: **GT Estimate™**) | [V] |
| Razón social | **GT Motive, S.L.** | [V] |
| Grupo / owner actual | **Allianz X** (brazo de inversión digital de **Allianz Group / Allianz SE**) — **mayoría** | [V] |
| Adquisición | Anunciada **13-sep-2021**: Allianz X firma acuerdos vinculantes con los accionistas **Mitchell International, Inc.** y **Einsa Print, S.A.** para comprar la mayoría; sujeto a aprobación regulatoria | [V] |
| Accionista minoritario | **Grupo fundador Einsa** permanece como minoritario; equipo directivo se mantiene | [V] |
| Owner anterior | **Mitchell International** (accionista oficial desde la alianza estratégica de **2012**) + **Einsa** (mayoritario hasta 2021) | [V] |
| Fundación | **1971** — **José Carlos Martínez** funda **Guía de Tasaciones, S.L.** (productos en papel) | [V] |
| Hitos | 1971 Guía de Tasaciones (papel) → **1998** nace **Einsa Multimedia** (embrión actual) → **2000** primera solución digital → **2007** rebrand a **GT Motive** + expansión (oficina en Francia) → **2012** alianza con Mitchell (líder EEUU) → **2021** mayoría a Allianz X | [V] |
| HQ | España. Centro de **I+D en Andrade, Pontedeume (A Coruña, Galicia)** (Ctra. Campolongo–Monfero Km 0,4, 15614). Oficina UK en Londres (Lynton House, 7-12 Tavistock Square, WC1H 9LT). HQ comercial citado a veces como **Madrid** | [V] HQ ES / [A] Madrid exacto |
| Plantilla | **~300 empleados** | [V] |
| Certificaciones | **ISO 27001** (Seguridad de la Información, 2023); premio **ABP Repairers' Choice Award** "Best Estimating System" (2021) | [V] |
| Categoría | **Estimática de siniestros y datos de reparación** (colisión, lunas, mantenimiento, avería mecánica) + plataforma colaborativa de gestión de siniestros + ecosistema AI. **NO es una casa de valor residual / tasación de mercado** | [V] |

### Clientes objetivo (3 segmentos declarados) [V]
1. **Aseguradoras, peritos y gestión de siniestros** (insurance, assessors & accident management).
2. **Carrocerías / talleres y centros de reparación** (bodyshops & repair centers).
3. **Flota, renting/leasing y compañías de garantía** (fleet, leasing & warranty).

Clientes citados en web (logos) [V]: Pelayo, AON, Mutua Madrileña, Northgate, Bosch Car Service, AXA, LeasePlan, Arval, Renault Retail Group, Sixt, Drivelog, Car Garantie. (También integrador de peritación **autoiXpert** en DE.)

---

## 2. Cobertura

### Geográfica [V]
- **Volumen / red**: opera en **28 países** (declaración corporativa) · **>80 compañías** de seguros y leasing a nivel global · **>10.000 talleres** usan el sistema a diario · **>5 millones de presupuestos/año** (cifra histórica previa: >4 millones/año).
- **Lista de soporte país por país (Manual V21.1, 24 países con email dedicado)** [V]: Austria, Bélgica, Chequia, Dinamarca, Finlandia, Francia, **Alemania**, Grecia, Países Bajos, Hungría, Irlanda, Italia, **México**, **Namibia**, Noruega, Polonia, Portugal, Rumanía, Eslovaquia, **Sudáfrica**, Suecia, Suiza, **Túnez**, **Turquía**, **Reino Unido**. (Web añade España y otros; el "about" cita 28 países europeos + Sudáfrica, India, Túnez, Corea del Sur.)
- **Expansión vía partners** [V]: **India** (acuerdo de distribución con **XA Group**, 2022) · **Sudáfrica** (partner **Motomatix**, 2022).
- **Cobertura de parque (car parc)**: **96–98 %** del parque circulante europeo con **35–38 fabricantes** y **>1.500 modelos** (ver §3.1; cifras varían por página/fecha).

### Scope de vehículos [V]
- **Tipos**: turismos, vehículos comerciales ligeros (LCV), **motocicletas** (vía función **Z-Moto**).
- **Datos**: **colisión (carrocería), lunas/cristales, mantenimiento** y **avería mecánica**.
- **Nuevo/usado**: enfoque en **vehículo dañado/siniestrado** (no es valoración de VN/VO de mercado). Identificación por matrícula (VRN) y VIN de cualquier antigüedad documentada.
- **Powertrains**: combustión + **vehículo eléctrico/ADAS** (integración ADAS declarada en GT Global; datos de reparación EV en la base NextGen).
- **Modo manual** para vehículos no catalogados: **Z-Manual** (precios manuales), **Base Model** (hereda datos de otro modelo), **Z-Moto** (motos con mano de obra media).

---

## 3. Productos + campos atómicos

Catálogo: **GT Estimate™** (núcleo de datos), **GT Global™** (plataforma de siniestros), **GT QCheck** (verificación de piezas), **GT Fusion** (ecosistema AI), **Diagnostics**, **Servicio de CO₂ / reparación sostenible**, y módulos GT Global (Flota/Leasing, Neumáticos, Vehículo nuevo, Customer Solution Services).

### 3.1 GT Estimate™ — peritación y presupuesto de reparación (núcleo) [V]
Plataforma 100 % cloud, sin instalación, responsive. Acceso en `estimate.mygtmotive.com` con **Customer Number + User ID + Password**. Datos OEM actualizados **a diario** (precios de pieza OE) + altas de modelos **2 veces/mes**.

**Cobertura (varía por página)**:
- Página producto EN: **38 fabricantes**, **1.500 modelos**; colisión + lunas + mantenimiento.
- GT Global / "roundup": **38 fabricantes**, **>1.759 modelos**, **97–98 % car parc**.
- Página UK Solutions: **35 fabricantes**, **>1.500 modelos**, **96–98 % car parc**, modelos nuevos 2×/mes, precios OE a diario.
- I Love Claims: **>175 fuentes** de datos (incluidos OEM), **96–98 % car parc**.

**Identificación de vehículo (Vehicle Identification Screen)** [V]:
- **Reg. Number / VRN** (matrícula) + función **VRN Look-up**.
- **VIN Number** (bastidor) + **GT VIN Query™** (obtiene del fabricante: **marca, modelo, carrocería (bodywork), motor (engine), caja de cambios (gearbox), fecha de fabricación (manufacture date), equipamiento**).
- **VIN Scanner** (lectura del VIN desde foto).
- **Make, Model, Mileage** (kilometraje).
- **Equipment Screen**: lista de equipamiento de serie/opcional (autollenada por VIN Query).
- **Equipment Information Source**: VIN Decoder / VIN Query / Interface (origen del dato de equipamiento).
- **Estimate Id, User Code, Reference Number (opcional)**.

**Datos de pieza (Parts)** [V]:
- **Nº de pieza OEM / referencia** (números de pieza exactos por NextGen, incluso las más pequeñas/complejas).
- **Descripción** de pieza.
- **Precio de pieza OE** (actualizado a diario).
- **Multi-referencia** / selección de pieza más barata / **supersesión** (nº de pieza nuevo).
- **Cantidad (Quantity)**.
- **Part Colours Legend** (estado/color de la pieza en el gráfico).
- **Sundry Parts** (%, importe, importe máximo), **Parts Platform Filter (%)**, **Parts Suppliers**, **Suggested Part Selection**, **Preselection of the Cheapest Part**.
- **Parts Query Function**: introduces nº pieza OEM → lista de vehículos/operaciones y mano de obra asociada.
- **Información adicional de pieza** (Additional Parts Information).

**Datos de mano de obra (Labour)** [V]:
- **Tiempos de mano de obra** por operación (estándares OEM).
- **Hourly Labour Rate** (tarifa horaria), por **Skill Level (T1, T2, T3…)**.
- **Categorías de mano de obra**: Mechanics, Panel, Paint, Electrical, Trim.
- **Tipos de operación/tarea**: **Replace, Repair, Remove and refit, Paint, Anti-corrosion treatment, Verify, Adjust, Strip/refit, Polish**.
- **Repair by Hail Formula** (granizo; recargo de pieza de aluminio, conservación de cavidades, tecnología adhesiva).
- **(UK)** Door Skin Allowance, **Under-body Coating Matrix**, **Cavity Protection Matrix** (por fabricante; matriz de 33 marcas).

**Datos de pintura (Paint)** [V]:
- **Sistema de pintura**: **Manufacturer, AZT, Cevismap, Centro Zaragoza, Manual, Without Paint**.
- **Paint Material Index (%)**, **Pearlescent Uplift (%)**, **National Paint Adjustment (AZT only)**.
- Operación de pintura + tiempos.

**Cálculo / resultados (Results Screen)** [V]:
- **Total Breakdown**: total **Parts**, total **Labour**, total **Paint**.
- **Discounts** (descuentos por importe fijo o % — campo **I/D**), **Taxes** (tipo + valor %), **Excess** (franquicia).
- **Waste EPA Charge**: Used Oil (tipo: no aplicar / coste por litro / coste fijo), Used Tyres (tipo de gestión, tipo de neumático), Other.
- **Estimate Attributes**, **Vehicle Damages**.
- **Estado**: Open / Closed; Job Status / Estimate Status (Calculated / Not Calculated).
- **Foto / Photo Gallery** adjunta al presupuesto.
- **Reports** (PDF descargable, idioma y tipo configurables).
- **User Operations** (operación de usuario: Part name, Code, Information, Task, Job, Quantity, Price, Labour Time, Group; cargo de especialista, exclusión de impuesto, importe negativo) y **Auxiliary Operations**.

**Datos de valoración embebidos (clave para Cardeep)** [V]:
- **"Market Value of the vehicle"** — valor de mercado del vehículo obtenible en la pantalla (junto a **Manufacturer colour code** y **Vehicle Registration Date**). *"Not available in all markets"*. Es el gancho de **siniestro total** (umbral coste reparación vs valor del vehículo), NO una previsión de VR.

**Modos / funciones** [V]: Full Estimate Mode, **Query Mode**, **GT Compact** (no en todos los mercados); **Dynamic Composition (Graphics)** con joystick virtual; Active Group; Laterality Lock; Task Lock; Locate Part in Graphics; Find Related Operations; Base Model; Z-Manual; Z-Moto.

### 3.2 GT Global™ — plataforma colaborativa de siniestros [V]
Ecosistema abierto que conecta aseguradoras, peritos, redes de talleres y gestores de siniestros. 100 % online, device-agnostic, sin instalación, actualizaciones automáticas. Integra GT Estimate para presupuestar. Módulos y campos:
- **Total loss workflow**: **valoración integrada de vehículos no reparables** + **asignación de salvamento (salvage)** con **despliegue automático al partner de salvamento**.
- **Electronic invoicing** (facturación electrónica): casos de **siniestro total, vehículos reparados, costes de especialista y heredados (inherited), facturación retail**.
- **Advanced business rules / rulesets**: dirige compliance en la red, **reduce suplementos**, habilita **auto-aprobación**; **triage inteligente** que enruta tareas por criterios de negocio.
- **Profiles & schemes management** (condiciones de reparación aplicadas en la asignación).
- **Real-time collaboration** experto↔reparador (comunicación en vivo).
- **Claims automation** vía partners integrados (reconocimiento de imagen — ver GT Fusion).
- **ADAS integration** (calibración/sistemas de asistencia).
- **MI (Management Information)**: dashboard "simple e intuitivo", insights en tiempo real, **monitorización de tendencias**, acceso total a datos para descarga/reporting externo.
- **KPIs declarados**: reduce **coste de siniestro**, reduce **cycle time** (tiempo de ciclo).

**Submódulos GT Global** [V]: **GT Global for Fleet and Leasing** (plataforma de autorización de reparaciones; gestión e inspección de intervenciones), **Customer Solution Services** (call center para gestión de flota / autorizaciones / control de coste), **Tyre Services Module** (tarifas pactadas con distribuidores), **New Vehicle Module** (alta de flotas nuevas e info de proveedores), **Mechanical breakdown repairs**.

### 3.3 GT QCheck — verificación automatizada de listas de piezas [V]
Webservice (API in/out) que **valida la lista de piezas** de un presupuesto/pedido para máxima exactitud.
- **Confirma y corrige piezas**; **supersesión** (sustituye por el nº de pieza nuevo).
- **Verifica referencias OE** antes de la compra.
- **Mass parts list checking** (chequeo masivo).
- Reduce **parts leakage** (fuga de piezas), nº de pieza incorrecto y **duplicación**.
- Base de datos de piezas de las marcas más vendidas; repositorio en actualización constante (objetivo **~70 % de cobertura de datos de fabricante a finales de 2024**).
- Beneficio: menor coste para proveedores/aseguradoras, menor cycle time, mayor exactitud de factura.

### 3.4 GT Fusion — ecosistema abierto de IA [V]
Lanzado **11-mar-2021**. Capa de transformación que **convierte recomendaciones de IA/ML en especificaciones detalladas de reparación**, fusionando la estimática + base de datos de GT Motive con visión artificial de partners.
- **Flujo**: foto/imagen → **detección de daño por IA** (piezas dañadas) → identificación de vehículo + base de reparación GT Motive → **presupuesto automático**.
- **Partners nombrados** [V]: **Click-Ins** (inspección de daños por IA), **TonkaBI** (analítica de datos / automatización IA para logística de seguros), **Valora** (identificación de daños basada en IA).
- **Casos de uso**: pre-policy vehicle checks, triage de reparación, estimación automática.
- Red de partners AI/ML "en constante crecimiento" (modelo de elección del cliente).

### 3.5 Servicio de CO₂ / Reparación sostenible (con Eco Repair Score) [V]
Servicio de consultoría (lanzado ~ago-2024) para que aseguradoras/flotas analicen y controlen las **emisiones de CO₂ de las reparaciones**.
- **Baseline Report (modelo de cálculo por lotes)**: análisis masivo del histórico de siniestros; identifica reparaciones de mayor emisión; **qué piezas generan más emisiones**; segmentación por **marca, modelo, perito (appraiser), taller (repair shop)**.
- **Follow-Up Reports** mensuales: cuantifican el impacto de medidas correctoras.
- Metodología **Life Cycle Assessment** (LCA) de Eco Repair Score.

### 3.6 Diagnostics [V — existencia / [A] detalle]
Listado como solución (en páginas de aseguradoras/soluciones) pero **sin ficha detallada pública** (lectura de OBD/códigos de avería = [A]).

---

## 4. Metodología y fuentes de datos [V]
- **Datos OEM propios documentados con el proceso NextGen** ("100 % desarrollo GT Motive", algoritmos propios de decodificación / know-how management): nº de pieza exactos por modelo (+20 % piezas/modelo), +25 % modelos (2020), −30 % tiempo de documentación.
- **>175 fuentes de datos**, incluidos los **fabricantes (OEM)**.
- **Actualización**: precios de pieza OE **a diario** (overnight); altas de modelos **2 veces/mes**; info OEM diaria.
- **Identificación**: por **matrícula (VRN look-up)** y por **VIN Query/Decoder** (equipamiento de fábrica).
- **Valoración de mercado**: el "Market Value" del vehículo dentro de GT Estimate procede de fuentes/mercados locales (no de un modelo de VR propio) — **no en todos los mercados** [V que es local/parcial; fuente exacta = GAP].
- **CO₂**: metodología LCA de **Eco Repair Score** (partner).
- **IA**: visión artificial de partners (Click-Ins/Valora) + analítica (TonkaBI) vía GT Fusion; capa de transformación propia IA→presupuesto.
- **Recursos**: ~300 empleados; panel técnico (technical panel) para baremos (p.ej. Door Skin UK tras "extensive market research").

---

## 5. Entrega [V]
- **App web/cloud (SaaS)**: GT Estimate (`estimate.mygtmotive.com`, `gtestimate.mygtmotive.com`), GT Global. Sin instalación, multidispositivo, login Customer Number+User ID+Password.
- **API abierta / web services**: acceso directo al backend de GT Motive vía **integración en sistemas de gestión existentes (DMS)** o UI propia; **GT QCheck** como webservice API in/out; integración de GT Estimate embebida en flujos de terceros (p.ej. autoiXpert en DE). Página "What is API" (UK) + "Schnittstellenoptimierung" (DE).
- **Informe PDF** del presupuesto (idioma y tipo configurables; cabecera/pie personalizables).
- **Dashboards MI** (GT Global) + **descarga de datos** para reporting externo.
- **Reports de CO₂** (Baseline + Follow-Up mensual).
- **Reduced modes**: Query Mode / GT Compact (consulta ligera de datos).

---

## 6. Precio
- **No público** (sin página de tarifas). Modelo declarado como **transaccional "pay-as-you-use"** (coste por uso por presupuesto) — posicionado explícitamente frente a las **cuotas mensuales fijas** del incumbente (Audatex/Solera). **Prueba gratuita de 15 días**. Importe exacto = **GAP** (cotización por contacto). [V que es pay-per-use y que no hay importe público]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla → dato (fuente principal: Manual GT Estimate V21.1).

### GT Estimate — Home Page (Estimates List) [V]
- **Tabla de presupuestos**, una fila por estimate, columnas: **Estimate Number · Vehicle Registration Number · Make · Model · Start Date · Modification Date · Job Status · Estimate Status**.
- Acciones por fila: **Edit, Copy, Delete, Report**. Buscador + filtros + ordenación por cualquier columna.
- Icono de menú → **User Data** (Regional Settings: idioma, país de la base de datos, zona horaria; cambio de contraseña), **My Operations**, **Parts Query**, **Work Environment**, **Logout**.

### GT Estimate — Work Environment / My Profile (configuración previa) [V]
- Pestañas: **Hourly Labour Rates · Paint · Parts · Taxes · Free Text · Reports · Configuration · Discounts · Waste EPA Charge · Functionalities**. Cada parámetro se predefine aquí y se hereda en todos los presupuestos.

### GT Estimate — Vehicle Identification Screen [V]
- **Parte superior**: Estimate Id, User Code, Reference Number.
- **Vehicle Information**: Reg. Number, VIN Number, Make, Model, Mileage. Iconos a la derecha: **VRN Look-up**, **VIN Query**, **VIN Scanner**.
- **Equipment Screen** (siguiente paso): bloques de equipamiento autollenados por VIN Query; el usuario confirma/edita.

### GT Estimate — Estimate Data [V]
- Bloques editables: labour rates, paint system, parts information, excess, taxes, **Estimate Attributes**, **Vehicle Damages**, waste EPA. Estrella para marcar **Favourites**; "View All" para desplegar todo.

### GT Estimate — Operations Selection Screen [V]
- **Functional Group** (zona del coche) seleccionable por barra desplegable o por el **gráfico dinámico** (Dynamic Composition) con **joystick virtual** central.
- Al elegir pieza → menú de **tareas** (Replace/Repair/Paint/…); se añaden a la **Actions/Operations List** (lateral) con **Ref. Number, Price, Quantity** editables y multi-referencia.
- **Market Value / colour code / Reg. Date** se obtienen aquí (mercados soportados).

### GT Estimate — Results Screen (Calculate) [V]
- **Panel oscuro a la derecha**: **Total Breakdown** desplegable (Parts / Labour / Paint / Discounts / Taxes / Totals).
- **Cuerpo central**: líneas de operación (Code, Description, Quantity, Price, Discount I/D). Lápiz = operación modificada. Botón **Reports** (abajo) → PDF.

### GT Global — Plataforma de siniestros [V parcial]
- **Dashboard MI** (panel "simple e intuitivo") con insights en tiempo real y monitorización de tendencias; **descarga de datos**.
- **Total loss**: la **valoración del no-reparable** y la **asignación de salvamento** viven en el flujo de siniestro total → despliegue automático al partner de salvage.
- **Electronic invoicing**: pantalla de facturación por tipo de caso (total / reparado / especialista / retail).
- **Business rules**: se aplican antes del envío de la autorización (flag de incidencias, auto-aprobación).
- **Colaboración** experto↔reparador en la ficha del siniestro (chat/comunicación en vivo).

### CO₂ / Eco Repair Score [V]
- **Baseline Report** (informe único por lotes) + **Follow-Up Reports** mensuales; segmentación marca/modelo/perito/taller; ranking de piezas/reparaciones por emisión.

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Datos OEM de reparación 100 % propios (NextGen)** con nº de pieza exactos + gráficos dinámicos interactivos (joystick, localización de pieza), actualizados a diario — alternativa creíble y auditada a Audatex/Solera.
- [V] **Modelo de precio transaccional "pay-as-you-use"** (vs cuota fija del incumbente) + 100 % cloud sin instalación — argumento anti-monopolio explícito ("time for choice").
- [V] **Ecosistema AI abierto (GT Fusion)** con multi-partner intercambiable (Click-Ins, TonkaBI, Valora) y **capa de transformación IA→presupuesto** propia (no atado a un único proveedor de visión).
- [V] **Respaldo Allianz X**: propiedad de una de las mayores aseguradoras del mundo → integración natural en flujos de siniestro de aseguradoras/flotas.
- [V] **GT QCheck**: verificación/supersesión automatizada de listas de piezas vía API (reduce fuga de piezas y errores de factura) — control de gasto en la cadena de suministro.
- [V] **Servicio de CO₂ por reparación** (Eco Repair Score, LCA) con segmentación por taller/perito — ESG aplicado al siniestro, poco común.
- [V] **Cobertura paneuropea de estimática** (96–98 % car parc, 28 países, 24 emails de soporte país) con identificación matrícula+VIN y soporte de motos (Z-Moto) y modos manuales (Z-Manual/Base Model).
- [V] **Facturación electrónica integral** (total/reparado/especialista/retail) + asignación de salvamento automatizada dentro del mismo flujo.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **NO es una casa de valor residual / tasación de mercado**: sin previsión de VR, sin curva de depreciación, sin retail/trade price, sin days-to-sell, sin price-to-market %, sin índices demanda/oferta. La "valoración" es solo **valor de mercado para umbral de siniestro total** (Market Value, *no en todos los mercados*) + valoración de no-reparable.
- [V] **Origen del "Market Value" no documentado** y limitado por mercado (probable dependencia de guías/terceros locales) — opacidad de fuente.
- [V] **Sin historial de vehículo por VIN tipo Carfax/autoDNA** (siniestros previos, propietarios, km certificado, ITV). VIN Query = equipamiento de fábrica, no historial.
- [V] **Sin verificación de fraude de kilometraje**.
- [V] **Precio no público** (importe = GAP); solo se confirma el modelo pay-per-use.
- [V] **Cobertura de catálogo "estrecha en marcas" (35–38 fabricantes)** frente a casas de specs/valoración (Eurotax/cap hpi ~99 %); se compensa con el 96–98 % de **parque circulante**, pero el long-tail de marcas raras/importación queda fuera (de ahí Z-Manual/Base Model).
- [V] **Documentación de API no pública** (no se exponen formatos, auth, rate limits ni diccionario de campos) — barrera para integradores.
- [A] **Diagnostics**, ADAS y datos EV **poco detallados** públicamente (existen como features, sin ficha de campos).
- [A] **Sin marketplace/subasta de salvamento propio**: asigna a un **partner** de salvage, no lo transacciona.
- [V] **Cifras de cobertura inconsistentes entre páginas** (35 vs 38 fabricantes; 1.500 vs 1.759 modelos; 96-98 vs 97-98 %; 4M vs 5M presupuestos) — marketing no normalizado.

---

## 10. Fuentes (URLs)
- https://gtmotive.com/en/ — homepage (productos, segmentos, clientes, certificaciones, oficinas).
- https://gtmotive.com/en/products/ — catálogo (GT Fusion, GT Estimate, GT Global, GT Global Fleet&Leasing, Customer Solution Services, Tyre Services, New Vehicle Module).
- https://gtmotive.com/en/products/gt-estimate/ — GT Estimate (38 fabricantes/1.500 modelos, paint systems, VIN Query, business rules).
- https://gtmotive.com/en/products/gt-global/ — GT Global (total loss, e-invoicing, rulesets, ADAS, MI).
- http://gtmotive.com/en/company/about-gt-motive — historia (1971 José Carlos Martínez/Guía de Tasaciones → 1998 Einsa → 2007 → 2012 Mitchell), ~300 empleados, 28 países, HQ A Coruña + Londres.
- https://marketing.gtmotive.com/external/gt_estimate_complete_guide.pdf — **Manual GT Estimate V21.1** (102 págs): pantallas, campos, paint index, EPA, modos, 24 países de soporte, Market Value/colour code/Reg.Date.
- https://gtmotive.com/en/new-nextgen-documentation-process/ — proceso NextGen (nº de pieza exactos, +25 % modelos, −30 % tiempo, 100 % GT Motive).
- https://gtmotive.com/en/gt-motive-announces-the-release-of-gt-qcheck/ — GT QCheck (API, supersesión, 10.000+ talleres, 4M+ presupuestos).
- https://gtmotive.com/en/gt-motive-launches-gt-fusion/ — GT Fusion 11-mar-2021 (Click-Ins, TonkaBI, Valora; Demerie Hill).
- https://gtmotive.co.uk/solutions/ — soluciones (35 fabricantes/>1.500 modelos/96-98 % car parc, altas 2×/mes, OE a diario, Diagnostics).
- https://gtmotive.co.uk/customers/insurers/ — aseguradoras (total loss valuation, salvage, rulesets, dashboard).
- https://gtmotive.co.uk/gt-global/ — GT Global (total loss no-reparable, e-invoicing por tipo, auto-approval).
- https://gtmotive.co.uk/a-roundup-of-new-technologies-implemented-by-gt-motive-so-far/ — 38 fabricantes/1.759 modelos/97-98 %, ADAS, GT Fusion, QCheck (abr-2024).
- https://gtmotive.co.uk/what-is-api/ — integración API / DMS.
- https://gtmotive.de/gt-estimate/ y https://gtmotive.de/gt-estimate/schnittstellenoptimierung/ — versión DE (Herstellerdaten, VIN-Abfrage, integración).
- https://iloveclaims.com/motor_claims/gt-motive-its-time-for-choice-in-the-estimating-technology-arena/ — posicionamiento (96-98 % car parc, 175+ fuentes, 80+ aseguradoras/leasing, 5M+ presupuestos, 28 países, pay-as-you-use).
- https://www.ecorepairscore.com/fr/blog/gt-motive-launches-new-service-drive-sustainable-vehicle-repairs — servicio CO₂ (Baseline + Follow-Up, LCA, segmentación marca/modelo/perito/taller).
- https://www.allianz.com/en/mediacenter/news/financials/stakes_investments/210916_Allianz-X-to-invest-in-GT-Motive.html — Allianz X adquiere mayoría (sellers Mitchell + Einsa Print S.A.), 13-sep-2021.
- https://www.insurancebusinessmag.com/uk/news/auto-motor/allianz-x-acquires-majority-stake-in-gt-motive-310404.aspx + https://www.claimsmag.co.uk/2021/09/allianz-x-to-acquire-majority-stake-in-gt-motive/18491 — confirmación adquisición (≥2 fuentes).
- https://gtmotive.com/en/gt-motive-signs-a-strategic-alliance-with-american-company-mitchell-international/ — alianza Mitchell 2012.
- Crunchbase / PitchBook (gt-motive) — perfil corporativo (uso secundario).

> Verificación: campos de GT Estimate [V] de lectura directa del **Manual V21.1** (extraído con PyMuPDF) + páginas de producto EN/UK/DE. Identidad/owner verificada con ≥2 fuentes (Allianz.com + Insurance Business + Claims Media + about page). Cobertura/volumen verificada cruzando 4 páginas propias + I Love Claims. Importe de precio, fuente exacta del "Market Value" y HQ exacto (Madrid vs A Coruña) = no verificables públicamente (marcados [A]/GAP). El "subdominio valuation" del input de Cardeep es **taxonomía interna**, no URL (`valuation.gtmotive.com` no resuelve — [V] DNS).
