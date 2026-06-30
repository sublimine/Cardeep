# IDEAUTO (IEA) — Auditoría atómica de inteligencia de automoción

> **Slug:** `ideauto-iea` · **Subdominio (categoría cardeep):** `market-intelligence`
> **Auditado:** 2026-06-30 · **Confianza global:** ALTA en identidad, catálogo de productos (API first-party) y campos del informe Parque (PDF first-party); ALTA en CAE y Distintivos (multi-fuente); MEDIA en el detalle de campos *dentro* de las apps BI (ID-Car/ID-Cube/Dashboard, tras login → descripción first-party pero campo-a-campo parcialmente inferido); BAJA/OPACA en precio B2B.
> **Convención:** cada afirmación va marcada `[VERIFICADO]` (leído en fuente) o `[ASUMIDO]` (inferencia declarada). Nunca se presenta un asumido como verificado.

> **Nota de naturaleza:** IDEAUTO **NO es una empresa de valoración** (no publica valor residual, retail/trade ni curva de depreciación como producto propio). Es la **consultora de datos e inteligencia de mercado filial de ANFAC** (la patronal de fabricantes). Su producto es el **dato de mercado del canal oficial/OEM**: matriculaciones (VN), parque circulante, VO, previsiones, y servicios operativos para fabricantes (rellamadas/recalls, COC, distintivos DGT, CAE). Históricamente fue además el **operador técnico (IT) del directorio de valoración de GANVAM** (`ideauto.es/ganvam/`), pero la valoración es de GANVAM, no de IEA. `[VERIFICADO]`

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre legal | **Instituto de Estudios de Automoción, S.L.U.** | `[VERIFICADO]` Empresite + aviso legal first-party |
| Marca corta | IDEAUTO · IEA | `[VERIFICADO]` |
| Denominación comercial | **Autodata** (nombre comercial registrado) | `[VERIFICADO]` Empresite |
| Marca de plataforma | **MoviliDATA** ("Avanzando en la MoviliDATA") | `[VERIFICADO]` informe Parque + prensa |
| Naturaleza | Sociedad limitada **unipersonal** (filial de datos/consultoría) | `[VERIFICADO]` |
| Propietario / grupo | **ANFAC** — Asociación Española de Fabricantes de Automóviles y Camiones (empresa filial) | `[VERIFICADO]` API ABOUTUS first-party + ANFAC + LinkedIn |
| CIF | **B82101809** | `[VERIFICADO]` Empresite + aviso legal |
| Constitución (entidad legal) | **10-09-1998** | `[VERIFICADO]` Empresite |
| Antigüedad declarada | "**más de 30 años**" de actividad (cuenta desde el área de estadística de ANFAC, anterior a la constitución de la SLU en 1998) | `[VERIFICADO]` (claim first-party) — discrepancia 1998↔30 años declarada honestamente |
| Registro Mercantil | Madrid, Tomo 13.392, folio 80, sección 8 del libro de sociedades | `[VERIFICADO]` aviso legal first-party |
| CNAE | **7320** — "Estudio de mercado y realización de encuestas de opinión pública" | `[VERIFICADO]` Empresite |
| HQ | **C/ Oquendo 23, Planta 3, 28006 Madrid** | `[VERIFICADO]` aviso legal + LinkedIn + Empresite |
| Tel / email | (91) 343 13 42 · **iea@ideauto.com** / office | `[VERIFICADO]` |
| Webs | web.ideauto.com (portal/marketing) · app.ideauto.com (launcher app, login) · distintivosambientales.ideauto.com (e-commerce) · ideauto.es (legacy) | `[VERIFICADO]` |
| Apps móviles | iOS `id6474176016` · Android `com.ideautoLauncherProd.mobile` ("Ideauto" launcher) | `[VERIFICADO]` enlaces store en home |
| Dirección | Presidente: **José López-Tafall** (Dir. Gral. ANFAC) · CEO: **Bruno Brito** | `[VERIFICADO]` mobilitycity + La Tribuna |
| Plantilla | 15 empleados (2025) / rango LinkedIn 11-50 | `[VERIFICADO]` Empresite + LinkedIn |
| Facturación | Entre 3 y 6 M€ (2024) | `[VERIFICADO]` Empresite |
| Certificación | **ISO/IEC 27001:2023** (gestión de seguridad de la información) | `[VERIFICADO]` LinkedIn + política de seguridad (PDF first-party) |
| Misión / Visión | "Ayudamos a entender la **Movilidad** facilitando la interpretación de la **información**" / "Ser referente en el desarrollo de soluciones para la nueva Movilidad" | `[VERIFICADO]` API ABOUTUS |

**Cliente objetivo (verificado):** **fabricantes (OEM)** y sus redes, **concesionarios**, **importadores/marcas**, **empresas de renting/flotas**, **compañías logísticas**, **instaladores de punto de recarga**, **compañías energéticas** (sujetos obligados/delegados CAE), **talleres e ITV** (distintivos), **administraciones públicas** (proyectos de cooperación) y **conductores individuales** (solo distintivos). `[VERIFICADO]` API SERVICES + CAE press.

---

## 2. Cobertura

- **País:** **España exclusivamente** (mercado español, datos DGT/ANFAC). `[VERIFICADO]`
- **Scope:** **VN (nuevo) + VO (usado) + parque circulante** + "muchos otros datos vinculados a las distintas áreas de la nueva movilidad". `[VERIFICADO]` API ABOUTUS/SERVICES.
- **Tipos de vehículo (contadores en vivo home + informe Parque):** **Turismos, Comerciales ligeros, Industriales, Autobuses, Motos/Ciclos/Quad, Tractores**. `[VERIFICADO]` API TotalMarket + PDF Parque.
- **Motorizaciones (informe Parque):** Gasolina, Diésel, Gas, **HEV**, **Electrificados** (= **PHEV + BEV + FCEV**). `[VERIFICADO]` PDF.
- **Granularidad declarada/inferida:** por marca, modelo, combustible, **canal** (particular/empresa/alquilador), distintivo DGT, antigüedad y **geografía** (CCAA/provincia, vía ID-Geo y datos DGT). `[VERIFICADO marca/canal/combustible/distintivo/antigüedad]` / `[ASUMIDO CCAA-provincia fino]`.

---

## 3. Productos + campos atómicos

> Catálogo extraído **de la propia API pública** del portal (`api/Portal/Globalization`, sección PRODUCT/SERVICES) + informe Parque (PDF) + páginas de producto. Las 4 **familias de servicio** (SERVICES) son: **Business Intelligence**, **Consultoría**, **Rellamadas**, **Distintivos Ambientales**; a las que se añaden **COC'S** y la **plataforma CAE**.

### P1 — Dashboard (Cuadro de Mandos) · *Business Intelligence*
"Cuadro de mandos que reúne los **principales datos de negocio de VN y VO cada día**, con una representación gráfica y métrica de los datos que permite conocer la **evolución del mercado** de forma rápida e intuitiva." `[VERIFICADO]` API.
- Campos/KPI (verificados a nivel descripción; granularidad concreta `[ASUMIDO]`): `matriculaciones VN del día/mes` · `unidades` · `variación %` · `cuota de mercado` · `datos de negocio VO` · `evolución temporal` · representación `gráfica` + `métrica`.
- Nº campos atómicos: ~6.

### P2 — ID-Custom · *Business Intelligence*
"Aplicación de **Gestión Web con informes de vehículos predefinidos** y un amplio nivel de **detalle técnico** adaptado a las **especificaciones de cliente** para un rápido acceso a toda la información de mercado **diariamente**." `[VERIFICADO]` API.
- Campos: `informes predefinidos` · `detalle técnico del vehículo` · `personalización por cliente (a medida)` · `acceso diario`.
- Nº campos: ~4 (configurable por cliente OEM).

### P3 — ID-Cube · *Business Intelligence*
"Herramienta Web que permite **analizar y explorar la información completa de su base de datos e integración con otras fuentes**, proporcionando un **análisis interactivo por las diferentes dimensiones** de la información." `[VERIFICADO]` API → es un **cubo OLAP multidimensional**.
- Dimensiones (verificado "diferentes dimensiones"; lista `[ASUMIDO]` por su dominio de datos): `marca` · `modelo` · `versión` · `combustible` · `canal` · `geografía` · `periodo` · `segmento`; medidas: `unidades`, `variación`, `cuota`.
- Diferencial: `integración con otras fuentes` del cliente.
- Nº campos: ~10 (dimensiones × medidas).

### P4 — ID-Car · *Business Intelligence*
"Aplicación de consulta que permite conocer la **información técnica del vehículo** o su **ciclo de vida** al instante." `[VERIFICADO]` API → consulta **por vehículo**.
- Campos: `ficha técnica / información técnica` · `equipamiento/specs` · `homologación` · **`ciclo de vida del vehículo`** (matriculación → transferencias → baja) · `distintivo ambiental`. `[VERIFICADO ciclo de vida + info técnica]` / `[ASUMIDO desglose campo a campo]`.
- Nº campos atómicos: ~6.

### P5 — ID-Geo · *Business Intelligence*
"**Representación en mapas** de sus datos para un fácil e intuitivo **análisis geográfico** de datos **de su marca y/o de Red**, enriqueciendo análisis y estudios de mercado." `[VERIFICADO]` API.
- Campos: `capa geográfica (mapa)` · `datos por territorio` · `datos de marca` · `datos de Red (concesionarios/puntos de venta)` · `análisis geo-comparativo`.
- Nº campos: ~5.

### P6 — Rellamadas (Recalls / campañas técnicas) · *familia propia*
"**Sistema Web de gestión de Rellamadas para fabricantes** que integra todas las etapas del proceso" · "Envío de comunicaciones de forma ágil, directa y **confidencial al propietario del vehículo** de las campañas técnicas activadas por el fabricante para subsanar fallos/deficiencias que afectan a la **seguridad vial**, usando **datos de contacto totalmente actualizados de DGT**." `[VERIFICADO]` API.
- Campos: `campaña técnica / recall` (id, fabricante, motivo de seguridad) · `vehículo afectado` (VIN/matrícula) · `propietario` · `datos de contacto actualizados (DGT)` · `estado de la comunicación` · `gestión multietapa del proceso` · `canal de comunicación`.
- Nº campos atómicos: ~7.

### P7 — COC'S (Certificados de Conformidad) · *familia propia*
"Envío de **Certificados de Conformidad** al cliente comprador con el **tipo de homologación** de su vehículo, en **formato impreso**, con criterios de agilidad y confidencialidad, usando datos de contacto **proporcionados por el fabricante**." `[VERIFICADO]` API.
- Campos: `Certificado de Conformidad (CoC)` · `tipo de homologación` · `comprador/propietario` · `datos de contacto (fabricante)` · `formato impreso (logística postal)`.
- Nº campos: ~5.

### P8 — Distintivos Ambientales (DGT) · *e-commerce + sistema B2B*
"Distribución y **Venta de etiquetas** para **conductores individuales** y un **Sistema de Gestión e Impresión de etiquetas online para Empresas** como Fabricantes, Concesionarios, Talleres, ITV…" · **"Distribuidor autorizado por"** (DGT). `[VERIFICADO]` API SERVICES + SPA renderizada.
- Flujo B2C: input **`matrícula`** (multi-placa, "+ Añade otra") → botón "Obtener distintivo del vehículo" → **distintivo ambiental DGT** (`0` / `ECO` / `B` / `C` / sin etiqueta). `[VERIFICADO]` snapshot Playwright.
- Páginas: `Tienda` · `Información General` · **`Tarifas`** (precio público, IVA incl.) · `Empresas` (B2B) · `Contacto`. `[VERIFICADO]`
- B2B: `sistema de gestión + impresión online de etiquetas` para fabricantes/concesionarios/talleres/ITV.
- Nº campos: ~6.

### P9 — Plataforma de gestión de CAE (Certificados de Ahorro Energético) · *lanzamiento 2025-2026*
Plataforma digital **única y abierta** para monetizar el ahorro energético del vehículo eléctrico. IEA "gestiona la **captura y validación** de esos expedientes; los **operadores** son responsables de su transacción". `[VERIFICADO]` ANFAC + La Tribuna (Bruno Brito).
- Campos: `expediente CAE` · `vehículo eléctrico` (matrícula/VIN) · **`formulario técnico TRA050`** (EV; posible expansión a otros) · `ahorro energético (kWh)` · `nº de CAE` (**1 CAE = 1 kWh** de ahorro anual) · `validación / captura` · `detección de fraude` · `agregación de expedientes` · `operador / sujeto obligado / entidad delegada` · `verificador autonómico (CCAA)` · `monetización` (**≈1.000 €/turismo** hasta 2030). `[VERIFICADO]`
- Punto de validación: **en el concesionario (punto de venta)**; automatización vía IA/programación. `[VERIFICADO]`
- Nº campos atómicos: ~11.

### P10 — Datos de Matriculaciones (VN) — núcleo de mercado
Contadores en vivo en home ("Mercado Español — Matriculaciones mes actual a fecha") y datos servidos a las apps BI / informes. `[VERIFICADO]` API TotalMarket.
- Campos por **tipo de vehículo** (Turismos, Comercial ligero, Industriales, Autobuses, Motos/Ciclos/Quad, Tractores): `unidades` (`mercado`,`unidades`,`unidadesA`=comparativa) · `icono`. `[VERIFICADO]`
- Dimensiones servidas: `cuota de mercado por marca` (verificado en legacy: Turismos-TT y Comerciales ≤3,5 t) · `por modelo` · `por combustible` · `por canal` · `por periodo (avance mensual)`. `[VERIFICADO marca/tipo]` / `[ASUMIDO modelo/canal a este nivel]`.
- Nº campos: ~8.

### P11 — Informe Parque de Vehículos (parque circulante) — **el más rico en campos verificados**
Fuente: **"Ideauto en base a datos de la DGT"**. Estructura del informe (PDF 2024) — 4 bloques. `[VERIFICADO]` PDF first-party.
- **Resumen** por tipo (Turismos, Comerciales ligeros, Industriales, Autobuses): `VOLUMEN` (`unidades` + `variación %`) · `EDAD MEDIA` (`años` + `diferencia de edad`).
- **Detalle medioambiental — distintivo DGT**: `Sin etiqueta` · `Etiqueta B` · `Etiqueta C` · `Etiqueta ECO` · `Etiqueta 0` → `Volumen` (uds + var %) + `Cuota` (% + `dif. p.p.`).
- **Detalle medioambiental — fuente de energía**: `Gasolina` · `Diésel` · `Gas` · `HEV` · `Electrificados` {`PHEV`, `BEV`, `FCEV`} → `Volumen` (uds + var %) + `Cuota` (% + dif. p.p.).
- **Antigüedad del parque**: bandas `≤5` · `5> y ≤10` · `10> y ≤15` · `15> y ≤20` · `>20` → `Volumen` + `Cuota`.
- **Parque por canal**: `Particular` (o `Particular/autónomo` en VCL/VI) · `Empresa` · `Alquilador` · `Desconocido` → `Volumen` + `Cuota`.
- Nº campos atómicos: ~24.

### P12 — Previsiones de mercado (forecasts)
"Realizamos **previsiones de mercado** uniendo las mejores técnicas predictivas con el conocimiento único del mercado." `[VERIFICADO]` API SERVICES.
- Campos: `previsión de matriculaciones` (`unidades` + `variación %`) por `segmento/tipo` y `horizonte` (corto/medio plazo); p.ej. proyección turismos+SUV ~998.150 uds / >1,04 M en 2025 (con GANVAM). `[VERIFICADO]` auto-revista.
- Nº campos: ~4.

### P13 — Estudios de mercado y Consultoría (a medida)
"Realizamos estudios de mercado y soporte de consultoría… para entidades privadas y proyectos de cooperación con instituciones públicas." `[VERIFICADO]` API SERVICES + ANFAC.
- Entregables: `estudios sectoriales` · `estudios a medida` · `consultoría` · `previsiones aplicadas`.

---

## 4. Metodología y fuentes de datos

- **Fuente primaria de parque + contacto + matriculaciones: la DGT.** El informe Parque lo declara explícitamente ("Ideauto en base a datos de la DGT") y Rellamadas usa "datos de contacto **totalmente actualizados de DGT**". `[VERIFICADO]`
- **Datos del fabricante/OEM:** COC'S usa "datos de contacto proporcionados por el fabricante"; su posición como **filial de ANFAC** le da acceso privilegiado al canal oficial. `[VERIFICADO]`
- **Integración multi-fuente:** ID-Cube "integra con otras fuentes" del cliente; plataforma "multi-source data integration". `[VERIFICADO]`
- **Previsiones:** "mejores técnicas predictivas + conocimiento único del mercado" (modelo econométrico/expertise, no detallado). `[VERIFICADO descripción]`.
- **CAE:** captura+validación de expedientes con **IA y automatización**, detección de fraude, sin compartir datos entre operadores. `[VERIFICADO]`
- **Actualización:** **diaria** (Dashboard/ID-Custom "cada día"); contadores de matriculación **mes-a-fecha**; informe Parque **anual**. `[VERIFICADO]`
- **Trayectoria histórica:** >30 años; **operador técnico del directorio de valoración GANVAM** (`ideauto.es/ganvam/` — directorio.asp, listados.asp, validacion.asp) y portales OEM a medida (p.ej. cliente Peugeot en `ideauto.com/clientes/peugeot`). `[VERIFICADO]` Wayback.

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| Apps web BI | Dashboard, ID-Custom, ID-Cube, ID-Car, ID-Geo (portal `app.ideauto.com`, login con **MFA/2FA**, AngularJS+React launcher) | `[VERIFICADO]` |
| App móvil | "Ideauto" launcher (iOS `id6474176016` / Android `com.ideautoLauncherProd.mobile`) | `[VERIFICADO]` |
| API | `apilaunch.ideauto.com/api/v1/` (app, **auth-gated**) + `api.ideauto.com/iIEAAPI/API/` (utils/portal públicos: Globalization, TotalMarket) | `[VERIFICADO]` (no hay API pública self-serve de datos) |
| Informes | Informes a medida + **PDF** (p.ej. Parque vía ANFAC), tablas personalizables | `[VERIFICADO]` |
| E-commerce | `distintivosambientales.ideauto.com` (venta unitaria + sistema B2B de impresión) | `[VERIFICADO]` |
| Logística postal | Envío **impreso** de COC y comunicaciones de Rellamadas (opción "Tengo un aviso de Correos" en contacto) | `[VERIFICADO]` |
| Plataforma CAE | Validación en **punto de venta del concesionario** + gestión de expedientes | `[VERIFICADO]` |
| Soluciones a medida | "soluciones **llave en mano** para cada cliente"; soporte "Datos & Aplicaciones" | `[VERIFICADO]` |
| Idiomas | ES / PT / EN | `[VERIFICADO]` |

---

## 6. Precio (modelo)

- **B2B (BI/Consultoría/Rellamadas/COC/CAE):** **a medida, opaco**, sin tarifa pública; venta consultiva ("socio de negocio", "llave en mano"). `[VERIFICADO]` (ausencia de precios) / `[NO VERIFICADO importes]`.
- **CAE:** el cliente final monetiza (**≈1.000 €/turismo**); IEA cobra por **gestión/validación** del expediente (importe no público). `[VERIFICADO modelo]` / `[NO VERIFICADO fee]`.
- **Distintivos Ambientales:** **precio público por unidad** (página *Tarifas*, IVA incl.) — único canal self-serve/transparente; **importe exacto no capturado** (cargado dinámicamente desde su API). `[VERIFICADO existencia]` / `[NO VERIFICADO importe €]`.
- **Conclusión:** pricing dominante = **contrato B2B a medida + membresía implícita del canal ANFAC/OEM**; transparencia solo en el e-commerce de pegatinas DGT.

---

## 7. Placement — DÓNDE se coloca cada dato (patrón a copiar por cardeep)

| Dato/métrica | Ubicación en UI/pantalla | Estado |
|---|---|---|
| Matriculaciones MTD por **tipo** (6 tarjetas: icono + mercado + unidades) | **Sección "Mercado" del home** ("Mercado Español — Matriculaciones mes actual a fecha"), contadores en vivo | `[VERIFICADO]` |
| KPIs de negocio **VN+VO** diarios + evolución | **Dashboard / Cuadro de Mandos** (cockpit con gráfica + métrica) | `[VERIFICADO]` |
| Análisis multidimensional (marca/modelo/combustible/canal/geo/periodo) | **ID-Cube** (explorador OLAP, pivot interactivo) | `[VERIFICADO]` |
| Ficha técnica + **ciclo de vida** del vehículo | **ID-Car** (pantalla de consulta por vehículo, resultado instantáneo) | `[VERIFICADO]` |
| Datos por territorio / marca / **Red** | **ID-Geo** (mapa coroplético, análisis geográfico) | `[VERIFICADO]` |
| Informes predefinidos con detalle técnico | **ID-Custom** (pantallas de informe a medida del OEM) | `[VERIFICADO]` |
| Parque: volumen/edad, distintivo, energía, antigüedad, canal | **Informe Parque** (PDF/report, 4 secciones: Resumen · Detalle medioambiental · Antigüedad · Canal) | `[VERIFICADO]` |
| Distintivo DGT por matrícula | **Caja de input de matrícula** en la landing de Distintivos → resultado etiqueta; precios en **Tarifas**; B2B en **Empresas** | `[VERIFICADO]` |
| Recall → propietario | Flujo de **Rellamadas** (gestión multietapa) + comunicación postal/digital | `[VERIFICADO]` |
| CoC → comprador | Flujo **COC'S** (impresión + envío postal) | `[VERIFICADO]` |
| Expediente CAE | Flujo de validación **en el concesionario** (punto de venta) | `[VERIFICADO]` |

**Patrón clave para cardeep:** (1) **portada con contadores de matriculación en vivo por tipo de vehículo** (tarjeta = icono + categoría + unidades + variación) como gancho de mercado; (2) **separación nítida entre el plano AGREGADO de mercado** (Dashboard cockpit, ID-Cube multidimensional, mapa ID-Geo, informe Parque por dimensiones) **y el plano POR-VEHÍCULO** (ID-Car: ficha técnica + ciclo de vida bajo búsqueda instantánea); (3) **datos operativos accionables** (recall, CoC, distintivo, CAE) presentados como **flujos de gestión**, no como tablas; (4) e-commerce de un microservicio (distintivo) como capa pública self-serve por encima del núcleo B2B gated.

---

## 8. Diferencial (lo que ofrece y casi nadie más)

1. **Filial de ANFAC** → posición **institucional/oficial** en el canal OEM y acceso privilegiado a datos de fabricantes + DGT; es de facto **la fuente de las métricas de referencia del mercado español de automoción**. `[VERIFICADO]`
2. **Amplitud única bajo un mismo techo:** matriculaciones VN + VO + **parque circulante** + previsiones + **rellamadas (recalls)** + **COC** + **distintivos DGT** + **CAE**. Ningún tasador puro cubre este abanico operativo. `[VERIFICADO]`
3. **Rellamadas y COC con datos de contacto vivos de DGT/fabricante** — productos **operativos** (no solo analíticos) que tocan al propietario real; pocos data houses los tienen. `[VERIFICADO]`
4. **Plataforma CAE** — pionera en **monetizar el ahorro energético del VE** (1 CAE=1 kWh, ~1.000 €/turismo, formulario TRA050), ligada al Ministerio de Transición Ecológica. `[VERIFICADO]`
5. **Parque DGT con granularidad medioambiental completa** (distintivo 0/ECO/B/C/sin + Gasolina/Diésel/Gas/HEV/PHEV/BEV/FCEV) × edad × canal × tipo. `[VERIFICADO]`
6. **Suite BI propia** (Dashboard, ID-Cube OLAP, ID-Car por-vehículo, ID-Geo mapas, ID-Custom a medida) integrable con fuentes del cliente. `[VERIFICADO]`
7. **Operador técnico histórico del directorio de valoración GANVAM** y de portales OEM a medida → know-how de 30+ años en sistemas de datos de automoción ES. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece / límites)

1. **No ofrece valoración propia:** sin **valor residual %**, sin **retail/trade price**, sin **curva de depreciación**, sin **price-to-market**. Eso es territorio de GANVAM-DAT/Eurotax/Autovista; IEA solo fue su **operador IT**. `[VERIFICADO por ausencia en catálogo]`
2. **Sin métricas de liquidez por anuncio:** no hay **days-to-sell**, **market days supply** ni índice oferta/demanda por listing. `[VERIFICADO ausencia]`
3. **Sin VIN-decode/valoración por VIN** ni informe de **historial per-VIN tipo Carfax** para consumidor (ID-Car es B2B y orientado a ficha técnica + ciclo de vida, no a siniestros/km histórico). `[VERIFICADO/ASUMIDO]`
4. **Sin scraping/feed de anuncios de VO** ni dataset de precios de oferta online propio. `[ASUMIDO fuerte]`
5. **Solo España.** Sin cobertura pan-europea. `[VERIFICADO]`
6. **Sin API pública self-serve de datos** ni pricing transparente B2B (portal gated con MFA; datos tras login). `[VERIFICADO]`
7. **VO poco profundo en lo público:** el detalle granular es **VN/parque-céntrico**; el VO aparece como KPI de Dashboard, sin producto de valoración/transacción VO propio. `[VERIFICADO]`
8. **Dependencia de DGT + ANFAC/OEM:** no opera un **panel propio de transacciones de concesionario** (a diferencia de GANVAM); su dato es registral/oficial, no de precio real de cierre. `[VERIFICADO/ASUMIDO]`
9. **Datos mayormente tras login;** apertura limitada (solo e-commerce de distintivos + resúmenes de prensa). `[VERIFICADO]`

---

## 10. Fuentes (URLs)

**First-party IDEAUTO**
- https://web.ideauto.com/ (portal SPA AngularJS; meta keywords: Matriculaciones, Previsiones, Rellamadas, Distintivos, Parque, BI; rutas /home /about /contact)
- `POST https://api.ideauto.com/iIEAAPI/API/api/Portal/Globalization` (catálogo PRODUCT/SERVICES/ABOUTUS — **fuente autoritativa del catálogo de productos**)
- `POST https://api.ideauto.com/iIEAAPI/API/api/Portal/TotalMarket` (contadores de matriculación en vivo por tipo de vehículo)
- https://app.ideauto.com/launcher/ (launcher React de la app de datos, login + MFA)
- https://apilaunch.ideauto.com/api/v1/ (API de la app, auth-gated)
- https://distintivosambientales.ideauto.com/ (e-commerce de distintivos DGT — render Playwright: input matrícula, Tarifas, Empresas)
- https://anfac.com/wp-content/uploads/2025/02/Informe-Ideauto-Parque-de-Vehiculos-Espana-2024.pdf (**informe Parque — campos atómicos verificados**)
- https://apps.apple.com/es/app/ideauto/id6474176016 · https://play.google.com/store/apps/details?id=com.ideautoLauncherProd.mobile (apps móviles)

**ANFAC (grupo propietario)**
- https://anfac.com/ideauto-presenta-una-plataforma-adaptada-al-nuevo-ecosistema-de-la-movilidad/ (plataforma MoviliDATA; CEO Bruno Brito; presidente López-Tafall)
- https://anfac.com/anfac-e-ideauto-impulsan-los-cae-como-instrumento-para-monetizar-el-ahorro-energetico-del-vehiculo-electrico/ (CAE: captura+validación, 1 CAE=1kWh, usuarios)
- https://anfac.com/publicaciones/informe-ideauto-parque-de-vehiculos-en-espana-2024/

**Terceros / verificación cruzada**
- https://es.linkedin.com/company/ideauto-iea (filial ANFAC, HQ Oquendo 23, 11-50 empleados, ISO 27001, specialties)
- https://empresite.eleconomista.es/INSTITUTO-ESTUDIOS-AUTOMOCION.html (**identidad legal**: CIF B82101809, 1998, SLU, CNAE 7320, Autodata, facturación)
- https://www.mobilitycity.es/n-oticias/ideauto-presenta-una-plataforma-adaptada-al-nuevo-ecosistema-de-la-movilidad/
- https://www.posventa.info/texto-diario/mostrar/3907118/ (lanzamiento plataforma)
- https://www.latribunadeautomocion.es/2026/06/bruno-brito-ideauto-... (entrevista CEO: CAE, TRA050, métricas VE abril 2026)
- https://www.auto-revista.com/texto-diario/mostrar/5188163/ (GANVAM + Ideauto previsiones de mercado)
- Wayback Machine `ideauto.es/odv2/ieasite/*` + `ideauto.es/ganvam/*` (legacy "Zona de datos IEA", directorio GANVAM, cuota por marca, previsiones/rodadura, cliente Peugeot)

---

## 11. Resumen para schema

- **slug:** `ideauto-iea`
- **subdominio:** `market-intelligence`
- **productos:** 13 (BI: Dashboard, ID-Custom, ID-Cube, ID-Car, ID-Geo · Operativos: Rellamadas, COC'S, Distintivos DGT, CAE · Datos: Matriculaciones VN, Informe Parque, Previsiones, Estudios/Consultoría).
- **diferencial central:** **filial de ANFAC** = fuente institucional del dato del **canal oficial/OEM** español (matriculaciones + parque DGT + previsiones) combinada con productos **operativos** únicos (recalls, COC, distintivos, CAE). No es tasador.
- **gap central para cardeep:** **no hay valoración/residual/retail-trade/days-to-sell propios**, ni historial per-VIN para consumidor, ni feed de anuncios VO; solo España; sin API pública self-serve; pricing opaco; dato registral (DGT), no precio real de cierre.
