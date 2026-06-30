# Auditoría atómica — Audatex España (Solera)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos/valoración/estimación de automoción. Web declarada: https://www.audatex.es/index · subdominio declarado: `valuation`.
> Fecha auditoría: 2026-06-30.
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre) · **[NO-VERIFICADO]** = no se pudo confirmar.

## 0. Nota de método y hallazgo de infraestructura (leer primero)

- **[V] `www.audatex.es` está fuera de servicio.** El host (IP `93.189.234.201:443`) **rechaza la conexión tanto desde egress US (WebFetch / navegador Playwright: `ECONNREFUSED` / `ERR_ABORTED`) como desde egress español local (curl: `Failed to connect to www.audatex.es port 443`).** No es geo-bloqueo: el servidor no sirve. Coherente con el **rebrand global de Audatex a Solera**: el dominio internacional `audatex.us` redirige 301 a `claims.solera.com`, y `solera.com/.../audatex/` redirige a `claims.solera.com/products/intelligent-estimating/`.
- **[V] El subdominio `valuation.audatex.es` NO resuelve** (`Non-existent domain` en DNS local; `valuation.audatex.com` también NXDOMAIN). La **capacidad "valuation"** existe como producto (AudaValue / VALUEpilot / Autosource / Typical Market Value / valor de mercado de AUTOonline), no como subdominio vivo a fecha de auditoría. Se documenta como hallazgo, no se inventa contenido del subdominio.
- **Entidades VIVAS auditadas en su lugar** (todas alcanzadas y leídas): `solerainc.es` (Solera España, catálogo ES), `claims.solera.com` (plataforma global de claims, 25 productos), `audatex.co.uk/about` (identidad), `audatex.ro` y `audanet.de` (AudaValue), help técnico `audatex.cn/audatexhelp` (VALUEpilot), más **2 informes Audatex reales en PDF** (peritaciones DEKRA y SegurCaixa Adeslas) que exponen el layout atómico de salida, y la serie técnica de `elchapista.com` sobre el sistema español.
- Identidad corporativa verificada con **≥2 fuentes ortogonales** (Wikipedia + audatex.co.uk + búsqueda corporativa). Campos atómicos de estimación verificados con **PDFs de informes reales** + serie técnica independiente.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca | **Audatex** (rebrandeada globalmente bajo **"Solera"** / "Audatex, a Solera company") | [V] |
| Producto insignia histórico | "El primer sistema automatizado de reparación de vehículos del mundo" (1966) | [V] |
| Grupo / owner | **Solera Holdings, Inc.** | [V] |
| Fundación de Audatex | **1966, Minden (Alemania)** | [V ≥2] |
| Nota HQ histórica | Audatex AG operó con sede en **Suiza** durante décadas (raíz europea); algunas fuentes citan origen suizo. Conflicto de fuentes marcado. | [A] |
| Fundación de Solera Holdings | **enero 2005** (fundador **Tony Aquila**) | [V] |
| HQ de Solera | **Westlake, Texas (EE.UU.)** | [V] |
| CEO actual (Solera) | Darko Dejanovic | [V] |
| Cotización | IPO **mayo 2007**, NYSE símbolo **"SLH"** | [V] |
| Adquisición de Audatex | **abril 2006**: Solera + private equity **GTCR** compran el **Claims Services Group de ADP** (NYSE: ADP) por **$975M** en efectivo | [V] |
| Privatización | **marzo 2016**: **Vista Equity Partners** compra Solera por ~**$6.500M** (con Goldman Sachs y Koch Industries); deja de cotizar | [V] |
| Llegada a España | **1979** (vía Grupo Solera) | [V] |
| Cuota de mercado en España | **~80% de las valoraciones de daños** del país | [V ≥2] |
| Escala España (década) | **+40 millones de siniestros** procesados | [V] |
| Escala global (cifras Solera) | **100+ países** · **+300.000 clientes/partners** · ~**6.500 empleados** (cifra ES-site) / 4.000 (Wikipedia 2015) — conflicto de cifras marcado | [V/conflicto] |
| Centros de documentación | **8 centros** de documentación en el mundo | [V] |
| Categoría | Datos, software y servicios de **gestión del ciclo de vida del vehículo**: estimación de daños/peritación, identificación, recambios, **valoración (valor venal/mercado)**, pérdida total, subasta de restos, analítica | [V] |

### Marcas hermanas dentro de Solera (relevantes para el dossier) [V]
**CAP HPI** (guías de valoración + historial UK), **HPI Ltd** (historial de vehículo, adq. 2008), **Autodata** (datos técnicos/reparación), **Hollander** (recambio/inventario), **Identifix** (diagnóstico), **DealerSocket**, **Omnitracs** (telemática), **eDriving/Mentor**, **Explore**, **Inpart** (gestión de recambio, adq. 2008), **SmartDrive**, **Digidentity**.
> **Implicación competitiva clave:** el GRUPO Solera ya posee valoración de VO/residuales (CAP HPI) e historial (HPI) — pero esos datos se venden bajo otras marcas; **Audatex en sí** es estimación de siniestros + valoración para pérdida total, no una guía de precios de VO al estilo CAP/Eurotax. **GT Motive NO pertenece a Solera** (es de Mitchell/Enlyte, competidor directo) — marcado para no confundir.

### Clientes objetivo (ecosistema declarado en España) [V]
Aseguradoras · Peritos (loss adjusters) · Talleres (chapa/pintura y mecánica) · Fabricantes/importadores (OEM) · Distribuidores de recambio · Compañías de renting/alquiler · Desguaces/compraventa · Compradores profesionales de restos · Particulares (vía AUTOonline) · Compañías de garantía mecánica.

---

## 2. Cobertura

### Geográfica [V]
- **Solera global:** 100+ países, 6 continentes (cifras corporativas; histórico 52 países en comunicación Audatex ES).
- **Audatex España:** mercado nacional, ~80% de las peritaciones; base que representa **99% del parque automovilístico** español.

### Scope de vehículos [V]
- **Tipos:** Turismos · Todoterreno/SUV · **Motocicletas** · Vehículo comercial ligero (LCV) · **Vehículo industrial pesado (HGV)**. (Audatex cubre industrial pesado, a diferencia de varios competidores de pura valoración.)
- **Estado:** vehículo **nuevo, usado y siniestrado/dañado** (valoración para reventa, seguro o pérdida económica).
- **Antigüedad valoración:** valor de mercado/venal para cualquier edad relevante a la peritación (no hay tope publicado).

### Escala de la base de datos [V]
- **Global:** **85+ marcas**, **36.000 modelos**, **~5 millones de recambios** identificados, **+1 millón de gráficos**, **+2,5 millones de datos** actualizados **mensualmente**.
- **España (cifras Audatex ES):** **1.000+ modelos** de **63 marcas**, ~**25.000 versiones**, **+104.000 motorizaciones/opciones**, ~**1 millón de gráficos**, **+12 millones de referencias** distintas.

---

## 3. Productos + campos atómicos

> Catálogo reconstruido de: catálogo España (`solerainc.es`), 25 productos de `claims.solera.com`, módulos AudaNet (AudaValue/VALUEpilot), serie técnica española y **2 informes reales en PDF**.

### 3.1 AudaPlus (plataforma web principal de peritación/estimación en España) [V]
Solución núcleo: identificación + catálogo de recambios + tiempos de mano de obra + pintura + valoración de daños. Integra **AudaVin**, **Intelligent Capturing** (gráficos inteligentes) y **módulo de mantenimiento**.
Campos/funciones de **identificación**:
- Identificación por **matrícula** o **nº de bastidor (VIN)**; o árbol de búsqueda manual ("Universal Search Tree").
- Selector marca → modelo → versión/variante → motorización → acabado comercial.
- Campo VIN admite estados: VIN estándar · "No accesible" · "Ilegible" · "Desconocido".
- Filtros: "Modelos Audatex" (activo por defecto) · Turismo · Motocicletas · Industrial.
- Identificación manual con documento base **PAD** genérico cuando no hay vehículo en catálogo.

### 3.2 Estimación de daños — campos atómicos (verificados en informes reales) [V]
Estructura exacta de salida (de los 2 PDFs de peritación reales leídos):

**a) Cabecera / DATOS VALORACIÓN:** Nº Valoración · Matrícula · Nº Bastidor · Marca-Modelo (+ variante) · Kms · Fecha Proceso · Fecha Impresión · Fecha Peritación · Estado/Situación ("Avance"/"En avance") · Ref. Expediente · Ref. Valoración · Nº Siniestro · Nº Póliza · Compañía aseguradora · Compromiso (SI/NO).

**b) DATOS GENERALES (taller/asegurado):** Nombre Taller · Dirección · Población · Provincia · CP · CIF Taller · Email Taller · Asegurado.

**c) EQUIPAMIENTO DEL VEHÍCULO:** Marca · Modelo · Variante · **Características** (lista de equipamiento de serie y opcional: climatizador, elevalunas, cierre, equipo de radio/multimedia, faros antiniebla, tapizado, regulaciones de asiento, volante, airbags por posición —rodilla, lateral, cabeza—, control de estabilidad/ESP, cilindrada **CC**, potencia **CV/KW**, tipo de cambio/caja, regulador de velocidad, medida de **neumáticos**, medida de **llanta**, alternador (A), norma anticontaminación **Euro**, nº de puertas/versión, **planta de producción**, **rango de fabricación** "DESDE mm-aaaa") · **Tipo de pintura** (Bicapa Metálico / Sólido) · indicador **barniz antirrayado** · **Valor Venal** (campo) · **Fecha de Matriculación**.

**d) PIEZAS/RECAMBIOS:** Fecha Tarifa · por fila: Descripción · **Referencia OE** · **Descuento (%)** · **Precio (€)** · y **Total Pieza** (nº de piezas + importe).

**e) MANO DE OBRA:** línea de conversión **"10,00 UT = 1 HORA · PRECIO = X €/hora"** (BMW: 12 UT = 1 hora) · por fila: **Nº Operación/Código** · Descripción · **Tiempo (UT)** · **Total (€)**. Códigos de tipo de operación:
- **E** = Sustituir (ref. pieza + precio + nº op. + tiempo sustitución + pintura).
- **I** = Reparar (tiempo definido por usuario en UT o €; marcado con asterisco `*`).
- **N** = Desmontar/Montar (nº op. + tiempo D/M).
- **ET** = Sustitución parcial (ref. completa + precio + nº op. parcial + tiempo + M.O. pintura + materiales pintura).
- **IT** = Tiempo de reparación parcial.
- **P** = Comprobar/verificar.
- **V** = Verificar/alinear/marcar (p.ej. "VEH.CPL.ANTES DE REP VERIF.SIN ALINEAR").
- **H** = Tratamiento anticorrosivo · **U** = Tratamiento de bajos.
- **S** = Conceptos varios (posición 1000, entrada manual) · **R** = Daños ocultos (posición 1000, manual).
- **Código 55** = Importe fijo de pintura.
- **Descuento M.O. (%)** · **Total M.O. CH/MEC** (UT totales + €).
- Función **"E por I"**: muestra **diferencia en % y € entre Sustituir vs Reparar** (piezas + M.O. + pintura) → optimización de coste.

**f) PINTURA:** **Tipo de pintura** · **Baremo** usado (CESVIMAP / **Centro Zaragoza** / Fabricante / Manual) · por pieza: Descripción · Nº Operación · Descripción Operación (P. SUSTITUCIÓN / P. REPARACIÓN) · **Longitud** · **Superficie (dm²)**. **Resumen pintura:** Materiales de pintura por superficie · Material pintura (total) · **M.O. Pintura Carrocería (UTS)** · M.O. Pintura (UTS) · **Total Pintura**.
- **Niveles de daño pintura metálica:** LE (I, paneles exteriores sustituidos completos) · LS (II, superficial) · L (III, ≤8% sup. deformada) · LI (IV, 8-25%) · LI1 (V, >25%).
- **Niveles pintura plástico:** LE1 (I, nuevo sin imprimar) · LE (II, nuevo imprimado) · L (III, leve) · LI (IV, ≤6,24 dm²) · LI1 (V, >6,24 dm²).
- **Tecnología:** Solvent M.S. (base disolvente, medio sólidos) / New Technologies (alto sólidos y base agua).
- **Acabado plástico:** CC (color carrocería completo) · TC (texturado completo) · 2C (dos colores) · CP (carrocería parcial) · TP (texturado parcial).
- **Recargo perla/bicapa:** +2% en materiales de pintura.

**g) CÓDIGOS OPCIONALES (descuentos/recargos):** tabla Descripción · **Fijo** · **Mínimo** · **Máximo** · **Porcentaje**. Códigos vistos: **88** (descuento s/ total sin IVA %) · **24** (descuento s/ total recambios %) · **33** (descuento s/ total M.O. %) · **59** (descuento s/ total M.O. pintura %) · **MO** (tarifa €/hora) · **CZ** · **06** · **84** (eliminar constante de pintura CESVIMAP) · **NC**.

**h) TOTALES:** Total Piezas · Total Pintura · Total M.O. · Total Varios · **Base Imponible** · **Impuesto (IVA 21%)** · Subtotal · **Franquicia** · **TOTAL** · **Total Horas Reparación** (UTS → "12 h. 15 min.") · sello "Origen Sistema de Valoración Audatex" · **Texto legal** (juramento del perito, Art. 335.2 L.E.C. 1/2000) · datos de facturación/contacto de la aseguradora.

### 3.3 AudaVIN (decodificación de VIN) [V]
Captura por **foto del VIN** (móvil) → datos del build sheet del fabricante:
- Año · Marca · Modelo · **Tipo de motor** · **Transmisión** · **Nivel de acabado exacto** · **Paquetes y opciones exactos** · **Códigos de pintura** · Colores · **Fases de pintura (paint stages)** · equipamiento electrónico de seguridad y gadgets opcionales no detectables a simple vista.
- Cobertura **97% del VIO (EE.UU.)**; se integra dentro de **Qapter Estimating** y **Total Loss**.

### 3.4 AudaValue / Valuation Manager / VALUEpilot / ICV (VALORACIÓN — el "valuation" del encargo) [V]
Producto de **valoración del valor de mercado** de vehículos nuevos, usados o dañados (para reventa, tarificación de seguro o tasación de pérdida económica). Compuesto por módulos: **Valuation (Valuation Manager)** + **VALUEpilot** (módulo adicional con licencia especial) + **ICV (Insured's Declared Value)**. Entregan el **rango de valor presente (pre-siniestro)** del vehículo.

**Inputs (parámetros del algoritmo):**
- Identificación **VIN** (recupera automáticamente datos técnicos del fabricante) o árbol de búsqueda universal.
- Tipo de vehículo · Marca · Modelo · Submodelo.
- **Motor** (potencia, cilindrada) · **Transmisión** · **Posición del volante**.
- **Lista de equipamiento opcional** (configuración de equipamiento del vehículo).
- **Fecha de primera matriculación** · **Kilometraje** · **Nº de propietarios anteriores** · **Estado/condición técnica actual**.

**Fuentes/ajustes del algoritmo:**
- **Precio nuevo del fabricante** (precio de catálogo / MSRP).
- **Precios de transacciones reales** de portales especializados de venta de coches online.
- **Datos de la plataforma de subasta de restos AUTOonline** + ofertas reales de internet.
- **Histórico** + ofertas de mercado actuales de los principales marketplaces online.
- Ajuste por equipamiento opcional · por kilometraje · por antigüedad · por condición técnica · por historial de servicio.

**Output (VALUEpilot):** **"corredor de valor" (value corridor)** = un **rango** de valor de reposición (p.ej. "20.000 a 22.000 €"), **no un valor único**, con detalle de las ofertas de mercado subyacentes. Flujo: **identificar vehículo (Universal Search Tree) → configurar equipamiento → valoración corta/larga en Valuation Manager → corredor de valor VALUEpilot**. Entrega: **informe PDF** con información completa del vehículo + valoración.

### 3.5 Typical Market Value (informe de valoración US/global, combina AudaVIN + Autosource) [V]
- **Inputs:** VIN (decodificado por foto) · Kilometraje (opcional) · Estado/Región.
- **Salida — Sección 1 Descripción del vehículo:** Marca · Modelo · Año · **Edición** · Kilometraje · especificaciones de motor · tipo de transmisión · **color de pintura exterior** · **material/color de asientos interior**.
- **Salida — Sección 2 Valor de mercado típico (3 niveles):** valor a nivel **estatal** · **regional** · **nacional**.
- **Salida — Sección 3 Opciones/equipamiento de fábrica** (del VIN, excluye aftermarket/dealer): sistemas de entretenimiento · exterior · interior · componentes mecánicos · sistemas de seguridad · paquetes.
- **Salida — Sección 4 Original Equipment Guide (OEG):** precio retail base · **MSRP**.

### 3.6 Autosource | Vehicle Market Value (valor de mercado para pérdida total) [V]
- **Valores de mercado justos, locales y sensibles a la región** para vehículos siniestro total ("market-driven valuation").
- Base de datos integral de vehículos comparables; ajuste regional/local.
- Acceso vía app **GoTime Autosource** (iOS/Android).
- Permite ajuste del valor tras revisión de imágenes por: **daño previo al accidente**, **kilometraje** y **extras opcionales** (afinar el valor de liquidación investigado).

### 3.7 Total Loss Valuations / Total Loss Specialty Valuations [V]
- **Valoraciones de pérdida total de mercado, ajustadas regionalmente**, instantáneas y data-driven (motor Autosource).
- Cobertura amplia de vehículos "mainstream".
- **Specialty:** valoración **manual** de no-mainstream (barcos, maquinaria agrícola, autocaravanas/RV).
- Beneficio: reduce tiempo de ciclo, costes de almacenaje y de alquiler de sustitución.

### 3.8 AUTOonline (mercado/subasta de pérdida total y restos — producto estrella España) [V]
- **Valor de mercado del vehículo dañado "calculado al céntimo"**, a partir de identificación exacta del modelo por **matrícula**.
- **Subasta online** con resultado en **48 horas**.
- **Pujas de compradores profesionales** (3.300 en Europa).
- Gestión transaccional: **pago por transferencia** a la entrega + documentación · **retirada del vehículo en toda España** · gestión documental · **certificados DGT** de transferencia de responsabilidad.
- Métricas: **20 años** operando · **5.000 vehículos/día** · **80% de adopción** entre grandes aseguradoras/rentings (8 de cada 10).
- Usuarios: particulares · aseguradoras · rentings · compradores profesionales.

### 3.9 AudaCheck (verificación/validación de valoraciones) [V]
- Verificación y validación de valoraciones según **parámetros y reglas predeterminadas**.
- **Informe final** que ayuda a gestionar siniestros en aseguradoras, rentings y compañías de garantía mecánica.

### 3.10 AudaGlass (lunas/cristales) [V]
- Web service de **precios y referencias** de cualquier **luna/cristal** de vehículo y componentes necesarios, rápido.

### 3.11 Qapter Intelligent Estimating (estimación por IA — motor moderno) [V]
- **Estimaciones de reparación línea a línea automatizadas** + **método de reparación óptimo** a partir de **fotos del daño**.
- **Reconocimiento de imagen + deep learning**: localización del daño en las fotos.
- **Gráficos 3D** exclusivos con **rotación 360°** del vehículo.
- Lógica **reparar vs sustituir**.
- Estimaciones precisas en **<2 minutos**. Integra AudaVIN. (Qapter Mobile Inspection: pre-estimación en minutos por fotos.)

### 3.12 Intelligent Triage / Guided Image Capture [V]
- **Intelligent Triage:** evalúa **pérdida total vs reparable** mediante fotos en el FNOL.
- **Guided Image Capture:** guía de captura de fotos en móvil en el primer aviso (FNOL).

### 3.13 Solera Analytics / AudaEstadísticas (BI sobre +4M valoraciones/año) [V]
Cuatro funciones para el ecosistema (talleres/aseguradoras) y un set específico OEM:
- **Análisis de reparaciones:** distribución de tipos de reparación por **comunidad autónoma** (p.ej. reparaciones de paragolpes por región).
- **Estadísticas de gestión:** **benchmarking** del coste medio propio vs estándar de mercado por tipo de vehículo.
- **Potencial de mercado:** oportunidades del mercado de reparación por **marca** en España.
- **Cumplimiento:** verificación de adherencia a políticas establecidas.
- **Set OEM (fabricantes):** Facturación nacional/provincial · **Posicionamiento de precio** · **Cuota de mercado** · **Potencial de venta de recambios a talleres** (nacional/provincia) · **Nº de reparaciones** (nacional/provincial) · **Potencial de facturación** (provincia/código postal) · **Potencial de reparaciones** (provincia/CP) · trazabilidad del vehículo "de fábrica a desguace" · **54 tipos de transacción** · consultoría vs benchmarks de mercado.

### 3.14 Inpart (gestión de recambio — marca hermana en el ecosistema) [V]
- Plataforma de **gestión del recambio** (global.inpart.es): distribuidores **ofertan recambios, precios y servicios**; talleres consultan **precios, tiempos y pedido**. (Detalle de catálogo no expuesto públicamente — GAP.)

### 3.15 Otros módulos del ecosistema (España + global) [V]
- **AudaMobile / AudaPad:** app de peritación en **tablet** (presupuestos in situ, sin papel).
- **Audataller:** catálogo electrónico para talleres pequeños (actualización automática, identificación por gráficos).
- **AudaMantenimientos:** histórico/cálculo de mantenimiento.
- **AudaSubastas:** subasta online de vehículos siniestro total (precursor/equivalente de AUTOonline).
- **Mensaelect:** facturación electrónica del taller.
- **IRE:** sistema inteligente de estimación de daños de piezas exteriores con estándares de reparación 100% demostrables (asigna tiempos y materiales por fase automáticamente).
- Catálogo global de claims (`claims.solera.com`, 25 productos): FNOL Contact Center · XpertEstimate (peritación virtual por ajustador licenciado) · AutoFocus (gestión de taller) · AutoWatch (estado de reparación con fotos) · APU Parts Procurement (cotización de piezas OE/aftermarket/recicladas) · Direct-Hit (información de diagnóstico/reparación) · Managed Repair · Subrogation · Desk Review · **Sustainable Estimatics (CO2e del siniestro/reparación)** · Diminished Value · eProperty Water Mitigation.

---

## 4. Metodología y fuentes de datos [V]
- **Catálogo OEM:** 8 centros de documentación mundiales mantienen referencias de recambio, gráficos, tiempos de M.O. y precios; **actualización mensual** (+2,5M datos/mes); fecha de tarifa explícita en cada informe.
- **Tiempos de mano de obra:** baremos del fabricante en **U.T.** (10 UT = 1 hora; BMW 12 UT = 1 hora).
- **Pintura:** baremos de terceros integrados — **CESVIMAP**, **Centro Zaragoza**, baremo del fabricante o manual; niveles de daño I-V; materiales por superficie (dm²).
- **Valoración (AudaValue/VALUEpilot):** algoritmo que agrega **precio nuevo del fabricante** + **transacciones reales** de portales de venta online + **subastas AUTOonline** + ajustes por equipamiento/km/edad/condición/propietarios/historial → **corredor de valor** (rango).
- **Autosource:** valoración "market-driven" por **vehículos comparables** con sensibilidad **regional/local**; ajuste posterior por imágenes (daño previo, km, extras).
- **AUTOonline:** valor "al céntimo" desde matrícula + **descubrimiento de precio por subasta** real entre 3.300 compradores profesionales.
- **VIN:** AudaVIN decodifica el build sheet OEM por foto del VIN.
- **IA:** Qapter usa reconocimiento de imagen + deep learning para localizar daño y proponer método de reparación; Intelligent Triage clasifica total vs reparable por foto.
- **Analytics:** BI sobre **+4 millones de valoraciones anuales** (España).

---

## 5. Entrega [V]
- **Plataforma web/cloud:** AudaNet / AudaPlus (login portal de peritación) · catálogo claims.solera.com.
- **App móvil/tablet:** AudaMobile / AudaPad · GoTime Autosource (iOS/Android) · captura de foto VIN y de daños.
- **Informe PDF:** peritación de daños (layout §3.2) · informe de valoración AudaValue · Typical Market Value Report.
- **API / integración:** integración con sistemas de aseguradoras y **DMS** del taller; AudaVIN/valoración embebidos en Qapter y Total Loss (entrega B2B; documentación pública de API limitada — GAP).
- **Marketplace/subasta:** AUTOonline (mercado transaccional de restos, pago + logística + DGT).
- **BI/dashboards:** Solera Analytics (estadísticas por región/marca/tipo).
- **Feeds/estadística:** AudaEstadísticas para OEM (facturación, cuota, potencial por provincia/CP).
- **Facturación electrónica:** Mensaelect.

---

## 6. Precio
- **[V] No público.** No hay tarifa publicada. Modelo por **suscripción/licencia** B2B (módulos como VALUEpilot requieren **licencia especial**) + **por transacción** en AUTOonline (subasta de restos) + servicios gestionados. Importe concreto = **GAP** (no descubrible públicamente).

---

## 7. Placement — dónde se ubica cada dato en su UI/salida
> Patrón a copiar por Cardeep. El **informe de peritación** es el "ground truth" más valioso porque es la salida real y estandarizada que millones de actores españoles leen.

### Informe de peritación Audatex — orden de secciones (de PDFs reales) [V]
1. **Banda superior (cabecera azul "DATOS VALORACIÓN"):** identificadores administrativos del siniestro (Nº valoración, matrícula, bastidor, marca-modelo, kms, fechas, nº siniestro/póliza, compañía, compromiso). → *Patrón Cardeep: ficha-cabecera del coche con matrícula+VIN+IDs arriba del todo.*
2. **"DATOS GENERALES":** taller + asegurado (quién interviene). → *Patrón: bloque de actores/contexto.*
3. **"EQUIPAMIENTO DEL VEHÍCULO":** marca/modelo/variante + **lista de características** (equipamiento de serie/opcional, motor, cambio, neumáticos, llantas, airbags, emisiones, planta) + **tipo de pintura** + **Valor Venal** + **Fecha matriculación**. → *Patrón Cardeep: panel de specs/equipamiento del coche, con el valor venal/mercado como dato destacado junto a la ficha.*
4. **"PIEZAS/RECAMBIOS":** tabla descripción · referencia OE · descuento % · precio · total. → *Patrón: tabla de partes con referencia + precio.*
5. **"MANO DE OBRA":** tabla nº operación · descripción · tiempo (UT) · total; con tarifa €/hora declarada. → *Patrón: tabla de operaciones con tiempo y coste.*
6. **"PINTURA":** baremo + operaciones de pintura + superficie (dm²) + resumen (materiales + M.O.). → *Patrón: bloque de pintura separado.*
7. **"CÓDIGOS OPCIONALES":** matriz de descuentos/recargos (fijo/min/máx/%). → *Patrón: ajustes/descuentos en una matriz.*
8. **"TOTALES" (pie):** desglose Piezas/Pintura/M.O./Varios → Base Imponible → IVA 21% → Subtotal → **Franquicia** → **TOTAL** + **horas de reparación** + sello de origen + texto legal. → *Patrón Cardeep: caja de totales abajo-derecha con desglose, impuestos y total final.*

### AudaValue / VALUEpilot — pantalla de valoración [V]
- Flujo guiado en pasos: **árbol de búsqueda** → **configuración de equipamiento** → **Valuation Manager (valoración corta/larga)** → resultado.
- El resultado **NO es un número único** sino un **corredor de valor (rango min-máx)** con las **ofertas de mercado subyacentes** mostradas como evidencia. → *Patrón Cardeep: mostrar valor como rango con comparables que lo justifican, no un solo número.*

### Typical Market Value Report — layout de 4 secciones [V]
1. Descripción del vehículo (specs del VIN) → 2. **Valor de mercado en 3 niveles (estatal/regional/nacional)** apilados → 3. Opciones de fábrica agrupadas por categoría → 4. OEG (retail base + MSRP). → *Patrón: valor mostrado a múltiples granularidades geográficas a la vez.*

### Autosource (app GoTime) [V]
- Valor de mercado local + lista de **vehículos comparables**; ajuste posterior por **fotos** (daño previo, km, extras) que recalcula el valor de liquidación. → *Patrón: comparables + ajuste por estado con evidencia fotográfica.*

### AUTOonline — flujo de pérdida total [V]
- Entrada por **matrícula** → valor "al céntimo" → **subasta 48h** → puja ganadora → logística+DGT+pago. → *Patrón: del dato de valor directo a la acción transaccional (vender el resto).*

### Solera Analytics — dashboard [V]
- Vistas por **comunidad autónoma**, por **marca**, por **tipo de vehículo**, por **provincia/código postal**; benchmarking propio vs mercado. → *Patrón Cardeep: analítica geográfica (mapa de calor por región/CP) + benchmark.*

### Qapter — estimación visual [V]
- **Gráfico 3D 360°** del vehículo con el daño localizado por IA sobre la foto; estimación línea a línea al lado. → *Patrón: visual 3D del coche + líneas de coste.*

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Dominio del estándar de peritación en España (~80%)**: el informe Audatex es el lenguaje común entre aseguradora, perito y taller — barrera de entrada y efecto-red enormes.
- [V] **Valor de mercado "al céntimo" por descubrimiento de precio real vía subasta (AUTOonline)** entre 3.300 compradores profesionales + 5.000 coches/día: valor no estimado sino **transado de verdad**.
- [V] **Corredor de valor (rango) VALUEpilot** sobre transacciones reales + subastas + ofertas online, en vez de un punto único — más honesto y defendible legalmente.
- [V] **Ciclo completo del siniestro en un proveedor:** FNOL → triage total/reparable (IA) → identificación VIN → estimación 3D (Qapter) → recambio (Inpart/APU) → valoración pérdida total (AudaValue/Autosource) → **subasta de restos (AUTOonline)** → analítica. Pocos cubren del aviso a la venta del resto.
- [V] **Integración de baremos oficiales españoles** (CESVIMAP, Centro Zaragoza) y validez **pericial-legal** (juramento Art. 335.2 L.E.C. en el propio informe).
- [V] **3D 360° con IA** y captura por foto del VIN/daño (Qapter + AudaVIN) — automatización de la peritación.
- [V] **Cobertura de industrial pesado (HGV) y motos**, no solo turismos.
- [V] **Pertenencia a Solera**: acceso de grupo a CAP HPI (residuales/guía VO) e HPI (historial) — aunque bajo otras marcas.
- [V] **Sustainable Estimatics**: huella **CO2e** del siniestro/reparación (ESG) — raro en el sector.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **`www.audatex.es` y `valuation.audatex.es` no operativos** (servidor caído / subdominio NXDOMAIN): la marca local se ha replegado a `solerainc.es` y la global a `claims.solera.com`. El subdominio "valuation" del encargo **no resuelve hoy**.
- [V] **Audatex NO es una guía de precios de VO/residuales al estilo Eurotax/CAP/Schwacke**: su valoración es para **pérdida total / pre-siniestro**, no un índice retail/trade ni days-to-sell/market-days-supply/price-to-market normalizados. (Esa capa vive en CAP HPI, marca hermana, no en Audatex.)
- [V] **Sin métricas de mercado de VO tipo demanda/oferta, días-en-stock, price-to-market %**: no las publica como producto Audatex.
- [V] **Sin historial de siniestros/km certificado por VIN al estilo Carfax/autoDNA** desde Audatex (existe en HPI, marca hermana).
- [V] **Precio/tarifa no público** (GAP de importe).
- [V] **Documentación pública de API/diccionario de campos muy limitada**: el catálogo de datos no se expone (orientación B2B/comercial); detalle de Inpart y de algoritmos de valoración **no divulgado**.
- [A] **Sin marketplace de VO sano para consumidor** (su mercado es de **restos/siniestro total**, no compraventa retail de coches en buen estado).
- [A] **Foco aseguradora/taller**, no herramienta de pricing para dealer de VO ni para particular comprador.
- [V] **Cifras corporativas inconsistentes entre fuentes** (52 vs 80 vs 88 vs 100 países; 2.000 vs 4.000 vs 6.500 empleados) — opacidad/desactualización.

---

## 10. Fuentes (URLs)
- https://www.solerainc.es/solera-en-espana/ — Solera España: divisiones (AUTOS/HOGAR), +40M siniestros, clientes.
- https://www.solerainc.es/ — catálogo y enlaces de sección (aseguradoras/peritos/talleres/fabricantes/distribuidores-recambio/autoonline/renting/analytics).
- https://www.solerainc.es/autoonline/ — AUTOonline: valor "al céntimo", subasta 48h, 5.000 veh/día, 3.300 compradores, certificados DGT.
- https://www.solerainc.es/peritos/ — productos a peritos: Audatex, **Inpart**, AUTOonline; control del ciclo del siniestro.
- https://www.solerainc.es/aseguradoras/ — ciclo aseguradora: tarificación, FNOL, valoración, recambios, pérdida total.
- https://www.solerainc.es/talleres/ — Audatex (posventa) + Inpart + Mensaelect; flujo de taller; ahorro 15%.
- https://www.solerainc.es/distribuidores-recambio/ — Inpart (gestión recambio).
- https://www.solerainc.es/fabricantes/ — analítica OEM (facturación, cuota, potencial por provincia/CP, 54 transacciones).
- https://www.solerainc.es/solera-analytics/ — BI sobre +4M valoraciones/año (4 funciones).
- https://www.claims.solera.com/solutions/ — 25 productos globales de claims (lista + URLs).
- https://www.claims.solera.com/products/typical-market-value/ — Typical Market Value (inputs + 4 secciones, valor 3 niveles, OEG/MSRP).
- https://www.claims.solera.com/products/vehicle-market-value/ — Autosource (valor local pérdida total, app GoTime).
- https://www.claims.solera.com/products/total-loss-valuations/ — Total Loss + Specialty (no-mainstream manual).
- https://www.claims.solera.com/products/vin-decode/ — AudaVIN (campos del build sheet, 97% VIO US).
- https://www.claims.solera.com/products/intelligent-estimating/ — Qapter (línea a línea, 3D 360°, <2 min, IA).
- https://www.audanet.de/cms/web/ax-rs/audavalue — AudaValue: ValuePilot/Valuation/ICV, valor pre-siniestro, conexión AUTOonline.
- https://audatex.ro/ax/produse/audavalue.html — AudaValue: lista de inputs (VIN, motor, transmisión, volante, equipamiento, 1ª matriculación, km, propietarios, condición) + fuentes (precio nuevo, transacciones reales, condición, historial) + informe PDF.
- http://www.audatex.cn/audatexhelp/estimatics/ms-my/HTML/4216.htm — VALUEpilot: "value corridor" (rango) sobre AUTOonline + ofertas internet; flujo árbol→equipamiento→Valuation Manager.
- https://audatex.co.uk/about/ — identidad: fundada 1966 Minden (primer sistema automatizado del mundo), Solera 2006, Vista 2016, 100+ países, +300.000 clientes, marcas hermanas (CAP HPI, HPI, Autodata, Hollander, Identifix...).
- https://en.wikipedia.org/wiki/Solera_Holdings — Solera: fundada 2005 (Tony Aquila), HQ Westlake TX, IPO 2007 NYSE SLH, Vista Equity 2016 $6.5B, adquisición ADP Claims Services Group 2006 $975M (con GTCR), cartera de marcas.
- https://www.elchapista.com/conozca_audatex.html — Audatex en España: AudaPlus/Audataller/AudaMantenimientos/AudaCheck/AudaSubastas/AudaGlass/AudaEstadísticas/AudaVin/Intelligent Capturing; escala BBDD ES (63 marcas, 25k versiones, 12M referencias); 80% cuota; 8 centros.
- http://elchapista.com/valoraciones_funcionamiento_audatex.html (y partes _3/_4/_5) — mecánica atómica: códigos E/I/N/ET/IT/P/V/H/U/S/R, código 55, UT (10/hora, BMW 12), baremos CESVIMAP/Centro Zaragoza, niveles de pintura I-V, acabados plásticos, "E por I", lógica valor venal/pérdida total 80%.
- (PDF) g-static.copart.com .../PeritacionPresupuesto.pdf — informe Audatex real (DEKRA): cabecera, equipamiento, piezas, M.O., códigos opcionales, totales, IVA 21%, franquicia, valor venal.
- (PDF) g-static.copart.com .../O.pdf — informe Audatex real (SegurCaixa Adeslas): añade bloque PINTURA (Centro Zaragoza, dm², materiales+M.O.), total horas reparación, datos de facturación.
- https://www.posventa.info/.../audatex-lanza-una-app... + https://www.infotaller.tv/.../IRE-... — AudaMobile (tablet) e IRE (estándares de reparación).

> Verificación: identidad corporativa confirmada por ≥2 fuentes (audatex.co.uk + Wikipedia + búsqueda corporativa). Campos atómicos de estimación verificados contra **2 informes reales en PDF** + serie técnica independiente (elchapista). Campos de valoración verificados con ≥2 fuentes (audanet.de + audatex.ro + help VALUEpilot). No verificable públicamente (marcado GAP/[A]): importe de precios, diccionario de API, algoritmo exacto de ponderación, estado del subdominio `valuation` (no resuelve).
