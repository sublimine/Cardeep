# carVertical — Auditoría de inteligencia competitiva

> **Slug:** `carvertical` · **Web:** https://www.carvertical.com/ · **Subdominio asignado:** `vin-history`
> **Fecha auditoría:** 2026-06-30 · **Categoría:** Vehicle history report (informe de historial por VIN), no analítica de mercado/residuales.
> **Método:** navegación viva (Playwright sobre el sitio de producción), WebFetch del help center y blog, WebSearch + fuentes terciarias (Wikipedia, Crunchbase, prensa). PDF de informe de muestra real extraído y leído íntegro (17 páginas).
> **Nota de herramientas:** el MCP de Exa NO está configurado en este entorno; se usó WebSearch + WebFetch + Playwright a fondo. La SPA del visor de informe (`/sample-report`) está protegida contra automatización (no renderiza headless) — su estructura se reconstruyó desde el PDF de muestra oficial + help center, lo que da el layout y placement EXACTOS.

Etiquetas: `[V]` = verificado (leído en fuente directa) · `[V2]` = verificado en ≥2 fuentes · `[A]` = asumido/inferido (marcado, no presentado como hecho).

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre comercial | carVertical | [V2] |
| Razón social / entidad legal | **CV Group, UAB** | [V] (Wikipedia) |
| País sede (HQ) | **Lituania** | [V2] |
| Ciudad HQ | Vilnius (operación también en Kaunas) | [A] (una fuente cita Vilnius; miembro de la cámara de Kaunas) |
| Fundación | **2017** | [V2] |
| Fundadores | **Rokas Medonis** (Co-Founder & CEO), **Arnas Vasiliauskas** (Co-Founder & CPO / Chief Innovation & Product Officer), **Robertas Boravskis** (Co-Founder), **Audrius Kučinskas** (Co-Founder & CTO) | [V2] (Crunchbase/Craft + startuplithuania) |
| Origen del capital | **ICO de criptomoneda** (token "CV" / carVertical token, ERC-20) en enero 2018; captó ~€16M reportados | [V] importe en 1 fuente (LT) → marcar aprox.; ICO confirmado en ≥2 |
| Tecnología fundacional | Blockchain para integridad/inmutabilidad de datos de historial. Miembro de la iniciativa **MOBI** (blockchain en automoción) desde 2018 | [V2] |
| Membresías sector | **CITA** (International Motor Vehicle Inspection Committee) desde 2024 | [V] |
| Facturación 2024 | **€53.998.159** | [V] (Wikipedia, cifra de cuentas) |
| Empleados | ~150–159 (150+ en su propia web, 159 en cuentas 2025) | [V2] |
| Usuarios acumulados | 6.000.000+ personas | [V2] (web) |
| Usuarios únicos/año | 2.000.000+ | [V] (web) |
| Partners B2B | 11.000+ concesionarios/negocios | [V2] (páginas /business y /business/api) |
| Controversia legal | Jun-2023: el Tribunal de Apelación de Lituania determinó que carVertical "extrajo y reutilizó sin autorización" datos del clasificado **Autoplius.lt**; ordenó cese, borrado y €42.000 de indemnización | [V] (Wikipedia) |

**Posicionamiento:** marca de informes de historial por VIN orientada al **comprador particular de coche usado** y al **profesional B2B** (concesionarios, casas de subasta, leasing, aseguradoras). Fuerte presencia mediática (AutoBild, TopGear, Forbes, Reuters; 5.000+ publicaciones PR/año; 230.000+ seguidores).

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| Países de operación (actual) | **37 países / 38 "mercados"** | [V2] (home + /business + /business/api) |
| Fuentes de datos | **1.000+ bases de datos** (el informe de muestra de ene-2024 citaba "900+ fuentes en 35 países"; la web actual dice 1.000+) | [V2] |
| Cobertura de kilometraje | "1.000+ fuentes en 37 países"; marketing histórico citó "45+ países" para mileage | [V] |
| Regiones | Mayor parte de Europa (incl. Báltico y Europa del Este), Reino Unido, **EE.UU.**, **México**, **Australia** | [V2] (Wikipedia + web) |
| Países B2B nombrados (lista parcial visible) | US, United Kingdom, Australia, Lithuania, Estonia, Latvia, Poland, Romania, Hungary, France, Ukraine, Sweden, Belgium, Czech Republic, Croatia, Bulgaria, Slovakia, Serbia, Finland, Slovenia, Germany, Italy, Switzerland, Denmark **(+13)** | [V] (/business) |
| Idiomas del producto | Multi-idioma (selector de región/idioma por país; equipo habla EN/LT/FR/IT/PL/DE) | [V] |

**Discrepancia de cifras (declarada honestamente):** el conteo de países varía por fuente y por fecha — Wikipedia/terceros citan 28–30 (dato antiguo), la web actual 37; el PDF de muestra (ene-2024) decía 35. Se reporta el rango y se prioriza la web viva (37/38).

### Scope de vehículos
- **Coche usado** = caso de uso central. También cubre **coche nuevo** (specs de fábrica), **motos** (`/motorcycle-vin-check`), **camiones/trucks** y "otros" (la web dice explícitamente "también puedes comprobar motos, camiones, etc."). | [V2]
- Identificación **por VIN de 17 caracteres** (estándar post-1981). Vehículos sin VIN decodificable quedan fuera. | [V]

---

## 3. Productos + campos atómicos

carVertical no vende "métricas de mercado" sueltas: vende **un informe de historial por VIN** (consumer) y el **mismo dataset vía API** (B2B), más utilidades satélite. Los productos:

### P1 — Vehicle History Report (informe consumer)
Generado en ~40 s tras pago. Es el producto madre. Sus **secciones y campos atómicos** (orden y placement reales tomados del PDF de muestra oficial + help center + blog 2024):

#### 3.1 Cabecera / Overview
- VIN
- Make (marca)
- Model (modelo)
- Body type (carrocería)
- Manufacture year / model year
- Recuento de fuentes de datos consultadas + nº de países
- Nav de secciones (Theft, Purpose, Odometer, Financial and legal status, Damage, Photos…)
- Nº de fotos + fecha de las fotos

#### 3.2 Purpose (uso del vehículo) — cada ítem con estado "Record found / No record found" + descripción
- Usado como **Rental** (alquiler)
- Usado como **Taxi**
- Usado como **Transport** (vehículo de transporte)
- Usado como **Police** (policía)
- Usado como **Handicap** (vehículo adaptado)
- Usado como **Driving school** (autoescuela)

#### 3.3 Theft (robo)
- **Currently wanted as stolen** (en busca actualmente) — estado
- **Stolen in the past** (robado en el pasado) — estado
- **Vehicle has been recovered** (recuperado) — estado
- País de origen del robo + fecha
- Lista de bases policiales por país en las que se hizo la comprobación

#### 3.4 Odometer / Mileage (kilometraje)
- Flag "posible kilometraje falso"
- **Last known mileage** (último km conocido)
- **Average mileage for similar models** (km medio de modelos similares)
- Nº de registros de odómetro encontrados
- Registro de odómetro (por entrada: **fecha + km**)
- **Rollback flag** por registro (marca de manipulación a la baja)
- Gráfico de evolución del kilometraje (años)
- **Driving habits** (hábitos de conducción): media de **km/mes** entre lecturas + tramos de uso intensivo/ligero  *(feature 2024)*

#### 3.5 Financial and legal status — cada ítem con estado + descripción
- **Lease / outstanding loan** (préstamo o financiación pendiente)
- **Operating-lease** (arrendamiento operativo)
- **Unit-stocking finance** (financiación de stock)
- **Technical inspection (MOT/ITV)**: resultado pass/fail + fecha + país
- **Scrap** (marcado como desguazado)
- **Exported / Imported** (registros de exportación/importación)
- Property rights restrictions (restricciones de derechos de propiedad)

#### 3.6 Damage (daños) — por cada registro
- Nº total de daños + flag "severe damage" (daño grave / estructural)
- **Damage location / part** (parte: p.ej. "Front right / Bumper", "Exterior / Roof", "Rear / Trunk lid")
- **Severity** (severidad: Severe damage / Damage)
- **Estimated Repair Cost** (coste estimado de reparación, en rango: p.ej. €15,001–€20,000)
- **Possible Damage Cause** (causa posible)
- **Fecha + país** del daño
- **AI Damage Detection**: daños inferidos por IA desde fotos cuando no constan en bases *(feature 2024)*

#### 3.7 Specs & equipment (especificaciones y equipamiento de fábrica)
Identificación y specs técnicas:
- Make, Model, Body type, Manufacture year
- **Powertrain displacement** (cilindrada, p.ej. 2 L)
- **Powertrain power** (potencia kW + hp)
- **Transmission type** (tipo de cambio)
- **Plant location** (planta de fabricación)
- **Drive layout** (tracción)
- **Emissions standard** (norma emisiones, p.ej. EU5)
- Base engine / engine specifications
- Fuel type / fuel system
- **Lista COMPLETA de equipamiento OEM por código de opción de fábrica** (decodificación PR-codes): airbags (conductor/pasajero/laterales/cortina), ABS/ESP, frenos delanteros/traseros, batería/alternador, espejos exteriores (asféricos/auto-atenuables/calefactados), ruedas (acero/medida), neumáticos (medida/marca), asientos y tapicería, reposacabezas, cinturones (delanteros/traseros), faros (halógenos/DRL/asistente), radio/altavoces/multimedia, climatización/AC, volante (cuero/multifunción), control de crucero, sensores de aparcamiento, navegación, alarma antirrobo, enganche de remolque, tapicería, molduras, etc. *(decenas de líneas, cada una código + descripción)*

#### 3.8 Market value / Market Price (valoración) *(feature 2024)*
- **Estimated market price** (precio de mercado estimado, actual e histórico)
- **Price range** (banda alta/baja, "dotted band" alrededor de la curva)
- **Historical prices** (precios históricos por año)
- **Recorded selling prices** (precios de venta registrados, "green markers")
- **Price trend forecast** (previsión de % de valor que perderá en **hasta 7 años**)
- Indicador de mejor momento de compra / mejor momento de venta
- Moneda + conversión por tipo de cambio (fecha de transacción / 1-ene del año / 1-ene actual)
- Base de comparación: mismo modelo y año en el país donde se generó el informe

#### 3.9 Safety (seguridad) *(feature 2024)*
- **Overall safety score** en estrellas (NHTSA 1–5; Euro NCAP & ANCAP 0–5)
- **Fuente** (organización: NHTSA / Euro NCAP / ANCAP según región)
- Explicación oficial del score
- Sub-scores de crash test: **Adult Occupant Protection**, **Child Occupant Protection**, **Vulnerable Road User Protection**, **Safety Assist**
- Resultados de crash test por área de impacto (frontal, lateral, rescate/extricación…)
- **Recalls** (llamadas a revisión): título, **status (Active/Solved/Unknown)**, recall number, **risk level**, descripción, fecha

#### 3.10 Natural disasters (desastres naturales) *(feature 2024)*
- Flag de exposición a desastre
- **Tipo** (inundación / erupción volcánica / ciclón tropical)
- Fecha del evento + ubicación
- Severidad del desastre
- Mapa de área afectada

#### 3.11 Title check (título, foco EE.UU.)
- Certificate of Title
- **Title brand** (salvage / rebuilt / junk)
- Estado del brand
- Fecha de adquisición del brand

#### 3.12 Emissions
- Norma/rating de emisiones
- Nivel de cumplimiento ambiental
- CO2 (de inspección técnica)

#### 3.13 Photos
- Imágenes históricas del vehículo
- Fecha de las fotos + recuento
- Evidencia de daños/modificaciones previas

#### 3.14 Timeline (cronología)
- Nº de registros
- Eventos cronológicos, cada uno con **fecha + país + tipo + explicación**: Was manufactured / Was registered / Was inspected / Damage detected / Wanted (stolen)

#### 3.15 Roadmap declarado (2024, parcial/limitado)
- **Maintenance schedules** (calendarios de mantenimiento por modelo, genéricos — no historial real de servicio) — anunciado Q2-2024 [A] estado actual
- **EV Battery health & range** (salud de batería y autonomía EV) — anunciado Q2-2024 [A] estado actual

---

### P2 — Advanced Vehicle History Report API (B2B)
- Mismo dataset del informe, entregado como **página web dinámica** o **PDF formateado** dentro del sistema del cliente. | [V]
- Personalizable por tipo de cliente (concesionario, subasta, leasing, aseguradora). | [V]

### P3 — Real-time VIN Decoder API (B2B)
- Decodificador VIN **potenciado por machine learning**; identifica variantes por mercado/fabricante/modelo/año con alta precisión; integrable en sistemas del cliente. | [V]

### P4 — US-origin alert (API, gratis para partners)
- **Flag de coche importado de EE.UU.** — detecta al instante origen norteamericano (señal de riesgo de daño/título). Gratis para partners. | [V]

### P5 — Trust Badge (marketing para concesionario)
- Sello carVertical para anuncios/listings; los anuncios con el badge obtienen **+21% de clics** (dato propio). | [V]

### P6 — VIN Decoder gratuito (web pública) — campos de salida
- Validez del VIN
- **VIN breakdown** (desglose por secciones WMI/VDS/VIS)
- Country of manufacture
- Manufacturer (make), Model, Year
- Basic equipment info | [V]

### P7 — Apps móviles iOS/Android + Motorcycle VIN check | [V]

---

## 4. Metodología y fuentes de datos

- **Modelo:** carVertical **NO crea** datos; **agrega, limpia, traduce, categoriza y modela** registros de terceros en un informe estructurado. | [V2]
- **Volumen:** comprueba "**over a billion records**" (>1.000M); 330M+ registros de daños revisados; cita un "44% media global de coches dañados". | [V]
- **Tipos de fuente declarados:** registros nacionales/estatales de matriculación, **aseguradoras**, **fuerzas del orden / bases policiales**, talleres oficiales / repair shops, **centros de inspección técnica (ITV/MOT)**, instituciones financieras, **flotas de vehículos conectados**, clasificados, casas de subasta, ONGs, leasing. | [V2]
- **Opacidad deliberada:** la empresa evita publicar las bases concretas ("sin discutir bases/fuentes específicas"); el mismo dato puede venir de distintas fuentes y varía mucho por país. | [V]
- **Capas tecnológicas:** blockchain (integridad), **ML para VIN decoder**, **IA para detección de daños en fotos**, modelos estadísticos para valoración de mercado y media de kilometraje. | [V]
- **Limitaciones reconocidas:** no todos los accidentes/reparaciones llegan a bases oficiales; reparaciones informales y daños menores pueden faltar; valoración puede no existir en modelos nuevos (falta histórico). | [V]

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Informe web** | Acceso online tras login ("My reports" → View); **disponible 30 días** desde la compra | [V] |
| **PDF descargable** | Botón "Download report"; válido/compartible **indefinidamente** tras expirar el online | [V] |
| **App móvil** | iOS / Android | [V] |
| **API (B2B)** | Informe como web dinámica o PDF embebido en el sistema del cliente; VIN Decoder API; US-origin alert API | [V] |
| **Trust Badge** | Widget/sello para listings de concesionario | [V] |
| **Dashboard / cuenta** | Gestión "My reports"; sin panel de analítica de mercado | [V] |
| Velocidad | Informe en **~40 segundos** | [V2] |
| **NO ofrece** | feed/Excel masivo de mercado, integración DMS nombrada (solo API "custom"), portal de inventario en vivo | [V] (ausencia, ver Gaps) |

---

## 6. Precio

### Consumer (precios US capturados en vivo, 2026-06-30)
| Paquete | Precio/informe | Total | Descuento |
|---|---|---|---|
| 1 informe | $34.99 | $34.99 | — |
| 2 informes ("Most popular") | $24.99 | $49.98 (de $69.98) | −29% |
| 3 informes | $19.99 | $59.97 (de $104.97) | −43% (hasta −69% vs unidad) |
- Política de reembolso ("Refund policy") por informe inexacto/insatisfactorio. Descuento de estudiante mencionado. | [V] (los importes varían por país/región y promo)

### B2B (capturado en vivo en /business)
- **Suscripción:** $12/informe (planes de **10** o **30 informes/mes**), ahorro 66%.
- **Bundles de un pago:** 10 informes $150 ($15 c/u, −57%) · 30 informes $360 ($12 c/u, −66%) · 100 informes $1.100 ($11 c/u, −69%).
- Más volumen → **oferta a medida**. **Sin contratos ni obligaciones.** Informes no usados válidos **6 meses**. Ahorro declarado "más del 73%". Pago por transferencia/proforma e invoice disponibles. | [V]

### API
- Precio **custom** (contacto comercial). **US-origin alert gratis** para partners. Modelo subyacente: cada petición a las fuentes tiene coste (de ahí que el informe no sea gratis). | [V]

---

## 7. Placement (DÓNDE se coloca cada dato — patrón a copiar por cardeep)

El informe es una **página única scrollable** con **nav de anclas superior** (Theft · Purpose · Odometer · Financial and legal status · Damage · Photos · …). Patrón por bloques verticales, cada uno con un **veredicto/flag arriba** ("This vehicle may have a fake mileage!", "This vehicle was severely damaged!") y el **detalle de registros debajo**. Mapa de placement (del PDF real):

| Dato / métrica | Sección / pantalla | Forma de presentación |
|---|---|---|
| VIN, make, model, body, año, nº fuentes/países, nº fotos | **Cabecera** (top del informe) | Bloque de identidad + nav de anclas |
| Uso taxi/rental/policía/autoescuela/transporte/adaptado | **Purpose** | Lista de chips "Record found / No record found" + descripción |
| Robado ahora / en pasado / recuperado; países comprobados | **Theft** | Banner de veredicto + checklist por país |
| Último km, km medio de similares, registros, rollback | **Odometer** | Veredicto + tabla fecha/km + **gráfico de líneas** con marca de rollback |
| Hábitos de conducción (km/mes) | dentro de **Odometer** | Indicador derivado de la curva |
| Préstamo/leasing, ITV/MOT, scrap, import/export | **Financial and legal status** | Checklist con estado + fecha + país |
| Daños: parte, severidad, coste estimado, causa, fecha, país | **Damage** | Banner de severidad + **tarjetas por registro** |
| Specs técnicas + equipamiento OEM (PR-codes) | **Specs & equipment** | Tabla de pares clave-valor + lista larga código→descripción |
| Precio estimado, banda, históricos, ventas, forecast 7 años | **Market Price** | **Gráfico** con banda punteada + marcadores verdes + insights debajo |
| Estrellas de seguridad + sub-scores + recalls | **Safety** | Score en estrellas + desglose por área + subsección Recalls |
| Inundación/fuego/desastre, tipo, fecha, mapa | **Natural disasters** | Banner + mapa de área afectada |
| Título salvage/rebuilt/junk (US) | **Title check** | Estado + fecha del brand |
| Norma de emisiones / CO2 | **Emissions** | Par clave-valor |
| Fotos históricas (fecha, daños) | **Photos** | Galería con fecha |
| Eventos cronológicos (fabricado/matriculado/inspeccionado/dañado/robado) | **Timeline** (cierre del informe) | Línea de tiempo vertical: fecha + país + evento + explicación |

**Lecciones de placement para cardeep:** (1) un **veredicto/flag de alto contraste** abre cada bloque antes del detalle; (2) cada hecho lleva **fecha + país + estado de fuente** ("record found/not"); (3) métricas derivadas (km medio, hábitos, forecast) se muestran **junto** al dato crudo que las sustenta; (4) el **gráfico** se reserva para series temporales (kilometraje, precio); (5) cierre con **timeline** que reagrega todos los eventos.

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Cobertura europea profunda**, especialmente **Báltico y Europa del Este** (LT/LV/EE/PL/RO/HU/UA/RS…), donde Carfax/AutoCheck (US-céntricos) son débiles. | [V2]
2. **Datos cross-border + US-origin alert**: detección de importados de EE.UU. como señal de riesgo (clave en mercados europeos). | [V]
3. **Integridad por blockchain** de los registros de historial (narrativa fundacional). | [V2]
4. **Coste de daño granular**: parte concreta + severidad + **rango de coste de reparación** + causa, por registro. | [V]
5. **AI Damage Detection** desde fotos (daños no presentes en bases). | [V]
6. **Natural disasters** (inundación/volcán/ciclón) con mapa. | [V]
7. **Driving habits** (km/mes, uso intensivo/ligero) derivado de la curva de odómetro. | [V]
8. **Market Price con forecast de depreciación a 7 años** + ventana óptima compra/venta (orientativo). | [V]
9. **VIN decoder ML** gratuito + soporte **motos/camiones**. | [V]
10. **Motor de marketing** para concesionario (Trust Badge +21% clics, cobertura PR). | [V]
11. Generación **~40 s**, multi-idioma, app móvil. | [V2]

---

## 9. Gaps (lo que NO ofrece)

1. **No es plataforma de inteligencia de mercado / residuales.** No da: **days-to-sell**, **market days supply**, **price-to-market %**, **índice demanda/oferta**, **retail vs trade price split**, curva de residual % por trim. El "Market Price" es un **dato orientativo único por VIN**, explícitamente "no decidas solo con esto" y **ausente en modelos nuevos**. | [V]
2. **Sin inventario/feed en vivo** ni censo de puntos de venta — es historial por VIN, no señal de mercado activo. | [V] (ausencia)
3. **Sin integración DMS nombrada**: solo API "custom"; no hay conectores DMS/portal listados. | [V] (ausencia)
4. **Sin entrega masiva** (Excel/feed bulk) para analítica; producto unitario por VIN. | [V] (ausencia)
5. **Historial de mantenimiento/servicio real** inexistente; "maintenance schedules" es genérico por modelo y estaba en roadmap. | [V]/[A]
6. **EV battery health/range** en roadmap, cobertura limitada. | [A]
7. **Completitud dependiente de país**: reconocen que faltan accidentes/reparaciones informales; calidad muy desigual fuera de sus mercados core. | [V]
8. **Informe online solo 30 días** (luego solo PDF guardado por el usuario). | [V]
9. **Riesgo legal de sourcing**: precedente Autoplius.lt (reutilización no autorizada de clasificados). | [V]
10. **Opacidad de fuentes**: no publican qué bases alimentan cada dato → difícil auditar/replicar. | [V]
11. **Dependiente de VIN**: vehículos sin VIN o pre-1981 quedan fuera. | [V]

---

## 10. Fuentes

- https://www.carvertical.com/ (home, viva) — identidad, cifras, productos. [V2]
- https://www.carvertical.com/business (Playwright, vivo) — segmentos B2B, **pricing B2B**, features dealer, Trust Badge, países. [V]
- https://www.carvertical.com/en/business/api (Playwright, vivo) — **API products** (VHR API, VIN decoder ML, US-origin alert), stats, testimonios. [V]
- https://www.carvertical.com/pricing (Playwright, vivo) — **pricing consumer US**, value-props, fuentes de datos. [V]
- https://www.carvertical.com/vin-decoder (Playwright, vivo) — campos del **VIN decoder gratuito**. [V]
- https://www.carvertical.com/help/about-the-service/what-information-may-appear-in-the-carvertical-report — listado de 13 secciones. [V]
- https://www.carvertical.com/help/about-the-service/where-does-the-data-come-from — tipos de fuente. [V]
- https://www.carvertical.com/help/about-the-service/what-format-are-your-reports-available-in — formatos/entrega (web 30 días + PDF). [V]
- https://www.carvertical.com/help/about-the-service/information-about-all-road-accidents — límites de daños. [V]
- https://www.carvertical.com/help/features/market-value — **campos de Market Price** (banda, forecast 7 años, marcadores). [V]
- https://www.carvertical.com/gb/help/features/safety — **campos de Safety** (NHTSA/NCAP/ANCAP, sub-scores, recalls). [V]
- https://www.carvertical.com/gb/blog/carvertical-report-features-and-improvements-2024 — features 2024 (Title, Natural disasters, Safety, AI damage, roadmap). [V]
- https://www.carvertical.com/en/blog/carvertical-data-sources — categorías de fuentes. [V]
- https://www.carvertical.com/blog/natural-disasters-report-feature — feature desastres. [V]
- PDF informe de muestra real (carvertical-sample-report.pdf, 17 pág., ene-2024) extraído íntegro → **layout y placement exactos** (Purpose, Theft, Odometer, Financial&legal, Damage, Specs&equipment, Timeline). [V]
- https://en.wikipedia.org/wiki/CarVertical — entidad (CV Group, UAB), 2017, ICO, MOBI, facturación 2024 €53,99M, controversia Autoplius.lt. [V]
- Crunchbase / Craft.co — **fundadores** (Medonis CEO, Vasiliauskas CPO, Boravskis, Kučinskas CTO). [V2]
- startuplithuania / chamber.lt / CITA — sede Lituania, membresía CITA 2024. [V2]
- (terceros comparativos) windowstickerlookupbyvin.com, cbinsights, vizologi — contexto competitivo/cobertura histórica. [A] contexto.

> **Aviso anti-alucinación:** los importes de precio son específicos de región/promo (capturados en US, 2026-06-30). El importe del ICO (~€16M) procede de una sola fuente en lituano vía Wikipedia → tratado como aproximado. El conteo de países difiere por fuente/fecha (28/30 histórico vs 37/38 actual) → se prioriza la web viva. La SPA del visor `/sample-report` no renderiza headless; su estructura se reconstruyó del PDF oficial + help center (no inventada).
