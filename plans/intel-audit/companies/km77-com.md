# Auditoría atómica — km77.com (catálogo de especificaciones de automóvil · grupo DriveK / AutoXY / GEDI · Exor)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Medio + base de datos técnica española de automóvil. Web producto: https://www.km77.com/ · Subdominios reales: `coches.km77.com` (VO), `blogs.km77.com` (revista), `coches77.com` (marketplace VO). Operador legal actual: **DRIVEK SOLUTION, S.L.** · Operador histórico: **Ruedas de Prensa, S.L.**
> Fecha auditoría: 2026-06-30. Método: navegación de km77.com (home + nav + aviso-legal + política-privacidad), extracción ATÓMICA por Playwright/JS de la ficha de un modelo real (BYD Seal Design 2024) en sus 3 superficies de dato — `/datos` (datos técnicos + precios), `/datos/equipamiento` (127 ítems en 7 secciones) y `/mediciones-propias` (mediciones propias km77) — + página de metodología del moose test + comparador + listado-completo por marca + sección /mercado + VO/coches77 + verificación cruzada de propiedad con DriveK (sobre-nosotros), MotorK (Wikipedia + motork.ai + business wire/Euronext), GEDI/AutoXY (BeBeez, TPI, Economyup).
> Convención: **[V]** = verificado leyendo la fuente · **[A]** = asumido/inferido (marcado siempre). El subdominio del encargo, **`spec-catalog`**, **NO resuelve** como `spec-catalog.km77.com` (DNS ENOTFOUND, ver §Gaps); "spec catalog" describe aquí el **activo nuclear** de km77 (catálogo estructurado de especificaciones/equipamiento/precios) que además nutre los configuradores multi-país DriveK.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca de producto | **km77.com** (revista + base de datos de coches) | [V] |
| Operador legal **actual** | **DRIVEK SOLUTION, S.L.** · CIF **B-67817312** | [V — aviso-legal] |
| Domicilio actual | **Avda. San Pablo 28 — Nave 27, 28823 Coslada (Madrid), España** | [V — aviso-legal] |
| Registro mercantil | **Registro Mercantil de Barcelona**, Hoja B-574669, Folio 180, Tomo 48171 | [V — aviso-legal] |
| Operador **histórico** | **Ruedas de Prensa, S.L.** · CIF **B-82262254** (Madrid) | [V — política-privacidad + DPOitlaw + búsqueda registral] |
| Categoría | **Catálogo de especificaciones técnicas + equipamiento + precios de coche nuevo**, **mediciones propias** (banco de pruebas), **comparador/buscador**, **revista** editorial, **marketplace VO** y **estadísticas de mercado** | [V] |
| Posicionamiento | "Revista de coches, novedades y pruebas… reportajes, noticias y artículos técnicos" + buscador de "informaciones, fichas e imágenes" y comparador de "precios, fichas y equipamiento" | [V — home] |
| Lanzamiento | Publica pruebas de coches vendidos en España **desde 1999** | [V — búsqueda + trayectoria] |
| Contacto | Administración **+34 91 724 05 70** · Publicidad **+34 91 513 04 95** · redaccion@/publi@/facturacion@/rrhh@km77.com | [V — aviso-legal] |
| Idioma/mercado | Español, mercado **España** | [V] |

### Cadena de propiedad (verificada a nivel de entidad) [V salvo donde se marca]
- El sitio km77.com lo opera hoy **DRIVEK SOLUTION, S.L.** (entidad española del grupo **DriveK**). [V — aviso-legal]
- **DriveK** nació como la marca **B2C** del grupo **MotorK** (MotorK se fundó como **"Drivek"** en **Milán (Italia), 2010**; fundadores **Marco Marlia / Fabio Gurgone / Marco De Michele**; salida a **Euronext Ámsterdam, 2021**, ~€75M). [V — Wikipedia MotorK + motork.ai]
- **MotorK desinvirtió** su unidad B2C **DriveK**: vendió el **80%** a **GEDI Gruppo Editoriale + AutoXY S.p.A.** (anunciado oct-2022, cerrado **dic-2022**) y el **20% restante** a **GEDI Digital** (cerrado **mar-2025**), combinando **DriveK + AutoXY** en el mayor marketplace de coche nuevo para consumidores en **Italia, Francia, España y Alemania**. [V — Business Wire + Euronext + BeBeez]
- **GEDI** adquirió el **78% de AutoXY** (jun-2021) y está **controlada por Exor N.V.** (holding de la **familia Agnelli**) desde 2020. [V — TPI + BeBeez + Economyup]
- **Cadena resultante:** **Exor (Agnelli) → GEDI Gruppo Editoriale → AutoXY S.p.A. → DriveK / DRIVEK SOLUTION, S.L. → km77.com**. [V a nivel de entidades]
- El paso intermedio **"MotorK adquirió km77 a Ruedas de Prensa"** (reportado ~ene-2021) **no pudo confirmarse** con nota de prensa en esta auditoría; se infiere del linaje DriveK/MotorK + cambio de operador (Ruedas de Prensa → DRIVEK SOLUTION). → **[A]** (ver §Gaps).

### Clientes objetivo [V/A]
- **Consumidor final** (gratis, financiado por publicidad): comprador de coche nuevo/usado, aficionado técnico. [V]
- **Anunciantes / marcas / concesionarios**: publicidad display y generación de leads (`publi@km77.com`, depto. de publicidad). [V]
- **Partners editoriales / OEM / dealers** vía el hermano de grupo **DriveK** (configurador B2B embebido, integrado con **+20 partners editoriales**). [V — motork.ai/DriveK]

---

## 2. Cobertura

### Geográfica [V]
- **España** es el mercado de km77 (precios con fiscalidad española: IVA, impuesto de matriculación, distintivo DGT, tarifa por mes).
- El **catálogo de especificaciones** del grupo (DriveK) cubre **~40 marcas relevantes** y se publica en versiones de **España, Francia, Alemania e Italia**. [V — drivek.es]

### Scope de vehículos [V]
- **Turismos / coche nuevo** (foco principal): modelos **disponibles**, **próximos lanzamientos** y **descatalogados** (estado etiquetado en ficha: **Disponible / Descatalogado / Prototipo**). [V — snapshot ficha]
- Histórico de fichas de coches vendidos en España **desde ~1999/2000** (p.ej. fichas de Ford Fiesta 2008, Porsche Macan 2022). [V — URLs de ficha]
- **VO (vehículo de ocasión)**: marketplace **coches77.com / coches.km77.com / KM77 VO** (~72.000 coches de 2ª mano citados). [V]
- **No** cubre (como dato propio) camión/industrial, moto (más allá de contenidos de revista puntuales), náutica ni agrícola. [A]

### Granularidad de identificación (jerarquía del catálogo) [V — breadcrumb]
**Marca → Modelo → Año/Generación → Carrocería → Acabado (trim) → Versión** (motorización exacta).
Ej.: `BYD / Seal / 2024 / Estándar / Estándar / Seal Design`. Cada **versión** tiene ficha de **datos técnicos + equipamiento + precios**; cada **modelo/generación** puede tener **mediciones propias** de la unidad probada.

---

## 3. Productos + campos atómicos

km77 no vende "productos" B2B empaquetados con nombre comercial: su producto es **la ficha de coche** desplegada en superficies. Las superficies de DATO son tres pestañas por versión — **Datos técnicos**, **Equipamiento**, **Mediciones propias** — más **Comparador**, **Buscador**, **Precios/Ofertas**, **Mercado** (estadísticas) y **VO/tasación**.

### 3.1 Ficha — DATOS TÉCNICOS + PRECIOS (núcleo del "spec catalog") [V]
Ruta: `/coches/<marca>/<modelo>/<año>/<carroc>/<acabado>/<versión>/datos`. Tablas (caption) y campos atómicos **verificados** sobre BYD Seal Design:

**Bloque PRECIOS / fiscalidad:**
- Precio (con descuento y equipamiento seleccionado) · Descuento oficial · Precio sin impuestos · IVA (%) · Impuesto de matriculación (%) · Tarifa de (mes/año).

**Prestaciones y consumos homologados:**
- Velocidad máxima (km/h) · Aceleración 0-100 km/h (s) · Consumo WLTP combinado (l/100 km o kWh/100 km) · *(para EV)* Combinado batería cargada · *(para PHEV/EV)* Autonomía eléctrica WLTP (km) · Emisiones de CO₂ WLTP (g/km) · Normativa de emisiones · **Distintivo ambiental DGT** (0 emisiones / ECO / C / B).

**Dimensiones, peso, capacidades:**
- Tipo de carrocería · Número de puertas · Longitud (mm) · Anchura (mm) · Altura (mm) · Batalla (mm) · Vía delantera (mm) · Vía trasera (mm) · Coeficiente Cx · Peso (kg) · Volumen mínimo de maletero con dos filas (l) · Volumen del segundo maletero (l) · *(ICE)* Capacidad del depósito [A] · Número de plazas · Distribución de asientos.

**Resumen del sistema de propulsión:**
- Potencia máxima (CV / kW) · Par máximo (Nm).

**Motor eléctrico (EV) [V]:** Finalidad · Potencia máxima (kW) · Régimen de potencia máxima (rpm) · Par máximo (Nm) · Régimen de par máximo (rpm) · Situación · Tensión nominal (V).
**Motor de combustión (ICE) [A — típico, no verificado sobre el EV]:** Disposición/nº de cilindros · Cilindrada (cm³) · Combustible · Distribución/válvulas · Alimentación/inyección · Sobrealimentación · Potencia máx + rpm · Par máx + rpm.

**Batería (EV) [V]:** Tipo · Situación · Capacidad total (kWh) · Capacidad útil (kWh).
**Carga (EV) [V]:** Potencia máxima de carga CC (kW) · Potencia máxima de carga CA (kW) · Tiempo de carga total a 11 kW · Tiempo de carga 10-80% en CC · *(equip.)* Carga bidireccional V2L (kW).

**Transmisión:** Tipo de tracción · Tipo de cambio · Número de relaciones/marchas · Tipo de mando · Tipo de embrague · Tipo de mecanismo.

**Bastidor y suspensión / frenos:** Estructura susp. delantera · Resorte susp. delantera · Estructura susp. trasera · Resorte susp. trasera · Barra estabilizadora delantera · Barra estabilizadora trasera · Tipo de freno delantero · Tipo de freno trasero.

**Dirección:** Tipo · Tipo de asistencia · Asistencia variable con la velocidad · Desmultiplicación variable con la velocidad · Desmultiplicación no lineal · Dirección a las cuatro ruedas · Diámetro de giro entre bordillos (m).

**Neumáticos y llantas:** Neumáticos delanteros · Neumáticos traseros · Medida de llanta delantera · Medida de llanta trasera.

> ~**70 campos** técnicos+fiscales por versión (varía EV/PHEV/ICE).

### 3.2 Ficha — EQUIPAMIENTO por versión [V — extracción JS, 7 secciones, 127 ítems]
Ruta: `…/datos/equipamiento`. Cada ítem se marca con icono de estado (**de serie / opcional / en paquete / no disponible**) por versión. Secciones y conteo verificados:

- **Seguridad y conducción (50):** Airbag central delantero · Airbag frontal acompañante · Airbag frontal conductor · Airbags de cabeza del. y tras. · Airbags laterales delanteros · Airbags laterales traseros · Aislamiento térmico/doble acristalamiento lateral · Alerta de cambio involuntario de carril · Alerta de fatiga del conductor · ABS · Asistente de cambio involuntario de carril · Asistente de frenada · Asistente de luz de cruce/carretera · Asistente de parada de emergencia · Asistente para atascos · Aviso de cinturón en todas las plazas · Aviso de colisión frontal + frenado autónomo de emergencia (AEB) · Aviso de colisión trasera · Ayuda de aparcamiento delantero · Ayuda de aparcamiento trasero · Ayuda de arranque en cuesta · Cierre de seguridad para niños · Cinturones delanteros regulables en altura · Control de crucero adaptativo (ACC) · Control de crucero inteligente · Control de estabilidad (ESP) · Control de presión de neumáticos (TPMS) · Control de tracción · Cámara de visión 360º · Cámara de visión trasera · Desactivación de airbag del pasajero · Detector de ángulo muerto · Dirección asistida · Distribución electrónica de frenado (EBD) · Faros LED · Faros antiniebla · ISOFIX plazas traseras exteriores · ISOFIX en acompañante · Llamada de emergencia (eCall) · Luneta térmica · Luz diurna LED · Mandos multifunción en volante · Ordenador de viaje · Reconocimiento de señales de tráfico · Retrovisor interior antideslumbramiento automático · Retrovisores exteriores con calefacción · Selector de modo de conducción · Tres reposacabezas traseros · Volante con ajuste horizontal · Volante con ajuste vertical.
- **Elementos de confort (42):** Acceso sin llave · Aire acondicionado · Apoyabrazos central delantero · Apoyabrazos central trasero · Arranque sin llave · Asiento conductor con memoria · Ajuste lumbar conductor · Asientos delanteros ajuste de altura · Asientos delanteros ajuste eléctrico (8 vías conductor / 6 acompañante) · Asientos delanteros con calefacción · Asientos delanteros deportivos · Asientos delanteros ventilados · Cierre centralizado · Climatización por bomba de calor · Climatizador bizona · Elevalunas eléctricos delanteros · Elevalunas eléctricos traseros · Filtro de aire PM 2.5 · Filtro de habitáculo · Freno de estacionamiento automático · Función Follow me home · Ionizador de aire · Limpiaparabrisas automático · Llave digital · Luces automáticas · Lunas tintadas · Lunas traseras sobretintadas · Luz anticharco · Luz de lectura delantera · Luz de lectura trasera · Luz en marcos de puertas · Luz interior ambiental · Luz interior en zona de pies · Mando de apertura a distancia · Parasoles con espejos iluminados · Portón trasero eléctrico · Preclimatización del habitáculo · Retrovisores ext. con memoria · Retrovisores ext. orientables eléctricamente · Retrovisores ext. plegables eléctricamente · Techo solar panorámico · Toma de 12 voltios.
- **Decoración exterior e interior (12):** Carcasas de retrovisores en color carrocería · Contorno de ventanillas cromado · Cuadro de instrumentos digital de 26 cm (10,25") · Luces traseras LED · Paragolpes en color carrocería · Pintura (color, p.ej. Ice Blue) · Pintura metalizada · Tapicería de cuero · Tiradores de puertas retráctiles eléctricamente · Tiradores exteriores en color carrocería · Volante con calefacción · Volante de cuero.
- **Equipaje y transporte (4):** 2 posavasos delanteros y 2 traseros · Asiento trasero abatible 40/60 · Guantera con iluminación · Maletero con iluminación.
- **Equipos de sonido y multimedia (10):** 4 puertos USB de carga (2×18 W, 2×60 W) · Apple CarPlay / Android Auto · Asistente de voz · Carga inalámbrica smartphone 15 W (2 puntos) · Bluetooth para teléfono · Navegador · Pantalla táctil orientable de 39,6 cm (15,6") · Radio digital · Servicios en la nube · Sonido Dynaudio de 12 altavoces.
- **Llantas y neumáticos (1+):** Llantas de aleación de 48 cm (235/45 R19) bicolor (medida/acabado por versión).
- **Varios (8):** Alarma antirrobo · Carga CA hasta 11 kW · Carga CC hasta 150 kW · Carga bidireccional V2L (3 kW) · Detección de alcohol (ADS) · Embellecedores metálicos en umbrales · Recuperación de energía de frenado · Servicios remotos.

> El **conjunto de ítems concretos varía por modelo**; lo estable es la **taxonomía de 7 secciones** con estado serie/opcional/paquete/no por versión. ~**127 ítems** en este modelo.

### 3.3 Ficha — MEDICIONES PROPIAS (banco de pruebas km77) [V — diferencial nuclear]
Ruta: `…/mediciones-propias`. Datos **medidos por km77** sobre la unidad probada (no homologados). Tablas/campos verificados:

**Habitabilidad — Primera fila:** Longitud (cm) · Anchura (cm) · Altura (cm) · Altura con techo solar (cm).
**Habitabilidad — Segunda fila:** Longitud (cm) · Anchura (cm) · Altura (cm) · Altura con techo solar (cm) · Isofix (cm).
**Maletero (medido):** Profundidad (cm) · Anchura (cm) · Altura (cm) · Altura del borde de carga (cm) · Volumen VDA (l).
**Aceleración, frenada y consumo:** Aceleración 40-80 km/h (s) · Aceleración 80-120 km/h (s) · Frenada 60-0 km/h (m) · Frenada 120-0 km/h (m) · Consumo (recorrido km77).
**Otros datos de la prueba:** Errores de velocímetro (velocidad indicada vs real a **50/90/120 km/h**) · Error del cuentakilómetros (%) · Error del ordenador de consumo (%) · **Consumo en recorrido km77** (l/100 km o kWh/100 km) · **Velocidad de la prueba de esquiva (moose test)** (km/h) · Kilómetros de la prueba (iniciales/finales) · Neumáticos de la unidad (medidas · marca/modelo).

**Metodología de la maniobra de esquiva (moose test):** norma **ISO-3888-2:2011** (sólo la 2ª parte, la más severa); ensayos entre **60 y 90 km/h**; sólo conductor, depósito lleno, presión de neumáticos de carga ligera; ≥2 conductores; válido el paso sin derribar conos; resultado = velocidad máxima superada. **No** publican comparación numérica cruzada entre coches (metodologías incomparables). [V — página de metodología]

> ~**25 campos** medidos por unidad. *(No se verificó fila de ruido/sonoridad; no se afirma.)*

### 3.4 Comparador [V]
`/comparador`. Comparativa **hasta 4 coches** lado a lado de **precios, datos técnicos y equipamiento** (botón "Añadir al comparador" en cada ficha). Reúne los campos de 3.1 y 3.2 en columnas. [V — snapshot + /comparador]

### 3.5 Buscador / Listados [V]
- **Buscador**: por **precio, especificaciones y equipamiento** (filtra el catálogo; selección de hasta 4 para comparar).
- **Listado completo por marca**: `/coches/<marca>/tecnica/listado-completo` (todas las versiones con precios/equipamiento/fotos/pruebas/fichas).
- **Listados temáticos** y **Próximos lanzamientos**. [V — home + URLs]

### 3.6 Precios y Ofertas [V]
PVP, **descuento oficial**, precio sin impuestos, IVA, impuesto de matriculación, **tarifa por mes**; bloque de **ofertas**. Herramientas en ficha: "**¿Cuánto vale tu coche?**" (afiliado), "**Calculadora de gasto anual**" (`/asesor-compra/calculadora/...`), "**Tasa tu coche gratis**". [V — snapshot ficha]

### 3.7 Mercado — estadísticas de matriculaciones [V]
Sección `/mercado/...` con **datos de ventas/matriculaciones** (p.ej. `/mercado/europa/2021/enero`): por **país, mes, marca y modelo**. Capa de inteligencia de mercado de coche nuevo. [V — URL]

### 3.8 VO / Coches77 — marketplace + tasación [V]
- **coches77.com / coches.km77.com / KM77 VO**: marketplace de 2ª mano (~72.000 anuncios). [V]
- **Tasación C2B "te ayudamos a vender / lo revisamos por ti"**: km77 recibe el coche **24-48 h**, hace **prueba mecánica** (consumo real, frenada, dirección…) + **inspección de taller** (chasis, motor, componentes de desgaste) y emite un **informe detallado** + **oferta de compra** y **precio de venta recomendado** ("precio idóneo"). [V — revista + KM77 VO]

### 3.9 Revista / Blog (editorial) [V]
`blogs.km77.com` y `/revista/`: noticias, pruebas, artículos técnicos, **vídeo** (YouTube/Dailymotion incl. vídeos del moose test). No es capa de "campos" sino de contenido. [V]

### 3.10 DriveK (hermano de grupo, B2B) — configurador como entrega del catálogo [V]
`drivek.es`: configurador de coche nuevo de **~40 marcas**, comparador hasta 4, solicitud de presupuesto a **concesionarios oficiales**; como producto MotorK, **integrado con +20 partners editoriales** (entrega embebida del catálogo a terceros). Parent declarado en copyright: **AutoXY S.p.A.** [V — drivek.es + motork.ai]

---

## 4. Metodología y fuentes de dato [V/A]
- **Datos homologados** (WLTP, dimensiones de fábrica, fiscalidad): de **fabricante/OEM** + tarifas oficiales; **tarifa fechada por mes** (trazabilidad temporal del precio). [V]
- **Equipamiento**: mapeo oficial por versión con estado **serie/opcional/paquete/no**. [V]
- **Mediciones propias**: ensayos **físicos propios** de km77 (banco de pruebas) — aceleración, frenada, **consumo en recorrido km77**, **moose test ISO-3888-2:2011**, habitabilidad y maletero medidos con cinta, **errores de velocímetro/cuentakilómetros/ordenador de consumo**. Condiciones estandarizadas (solo conductor, depósito lleno, presión de carga ligera). [V]
- **Consumo estimado** (asesor de compra): **algoritmo** que parte del **consumo homologado WLTP** y aplica **factores de corrección** para acercarse al uso real. [V — búsqueda]
- **Mercado**: matriculaciones oficiales por país/marca/modelo/mes. [V]
- **Tasación VO**: inspección física (mecánica + taller) + análisis del mercado de usado. [V]
- **Catálogo multi-país**: el mismo modelo de dato nutre los configuradores DriveK de ES/FR/DE/IT. [V]
- Frescura: tarifas mensuales; fichas actualizadas en continuo; estado del modelo (Disponible/Descatalogado/Prototipo). [V]

---

## 5. Entrega [V]
- **Portal web** km77.com (gratuito, financiado por publicidad) — ficha por versión con pestañas (Información · Fotos · **Precios, datos y equipamientos** · **Mediciones propias** · Todo).
- **Comparador** y **buscador** web.
- **Marketplace VO** (coches77.com / coches.km77.com).
- **Revista/blog** + **vídeo** (YouTube, Dailymotion), **newsletter**.
- **Publicidad / lead-gen** (B2B comercial) + enlaces de afiliación (Carwow, compramostucoche).
- **Configurador embebible DriveK** (entrega B2B del catálogo a +20 partners editoriales, multi-país). [V — motork.ai]
- **Sin API pública documentada** propia de km77 (ver Gaps). [V — no hallada]
- **Sin feed/Excel/DMS** público documentado por km77 (la vía B2B del dato es DriveK). [A]

---

## 6. Precio
- **Para el consumidor: gratis** (modelo publicitario). [V]
- **Tasación VO C2B: gratis** (informe sin compromiso). [V]
- **B2B**: publicidad display + generación de leads (tarifa no pública; contacto `publi@km77.com` / +34 91 513 04 95). [V]
- **DriveK SaaS/configurador** (grupo): precio **no público**. [V]
- **Importe concreto = GAP** (no descubrible públicamente). [V]

---

## 7. Placement — dónde ubica km77 cada dato (patrón a copiar por Cardeep)
> Mapeo pantalla/sección → dato. Es el patrón de ubicación más relevante de toda la auditoría para Cardeep.

### Jerarquía de navegación (breadcrumb) [V]
**Inicio → Marcas (`/coches`) → Marca → Modelo → Año/Generación → Carrocería → Acabado → Versión.** Etiqueta de estado del modelo (Disponible/Descatalogado/Prototipo) bajo el breadcrumb.

### Ficha de versión — pestañas superiores [V]
`Información` · `Fotos` · `Precios, datos y equipamientos` (`/datos`) · `Mediciones propias` (`/mediciones-propias`) · `Todo`. Dentro de `/datos`, **sub-pestañas**: `Datos técnicos` | `Equipamiento`.

### Dónde va cada dato [V]
1. **Precio + fiscalidad** (PVP, descuento, sin impuestos, IVA, matriculación, tarifa-mes): **tabla superior izquierda** de `/datos`, junto a 2 fotos del coche.
2. **Herramientas de ayuda** (¿cuánto vale tu coche?, calculadora de gasto anual, "tasa tu coche gratis"): **columna lateral** de la ficha.
3. **Prestaciones y consumos homologados** + **Distintivo DGT** (badge gráfico inline): primer bloque de **Datos técnicos**.
4. **Dimensiones/peso/capacidades**, **Propulsión**, **Motor**, **Batería**, **Carga**, **Transmisión**, **Bastidor/suspensión**, **Dirección**, **Neumáticos/llantas**: tablas sucesivas con **caption** en **Datos técnicos**.
5. **Equipamiento** (7 secciones, estado serie/opcional/paquete/no por versión): sub-pestaña **Equipamiento** de `/datos`.
6. **Mediciones propias** (habitabilidad por filas, maletero medido, aceleración/frenada, **moose test**, errores de instrumentación, consumo en recorrido km77): pestaña dedicada **Mediciones propias**.
7. **Comparador**: columnas paralelas (hasta 4 coches) que **reusan** precios+datos+equipamiento; botón "Añadir al comparador" en cada ficha.
8. **Listado completo por marca**: matriz de versiones (`/coches/<marca>/tecnica/listado-completo`).
9. **Mercado**: estadísticas de matriculaciones por país/marca/modelo/mes (sección propia).
10. **VO**: ficha de anuncio + **informe de inspección** + **oferta de compra/precio recomendado** en coches77/KM77 VO.

> **Patrón Cardeep:** ficha jerárquica marca→…→versión con (a) bloque precio+fiscalidad arriba, (b) tablas técnicas con caption por subsistema, (c) sub-pestaña de equipamiento booleano serie/opcional, (d) **pestaña separada de "mediciones propias"** que distingue dato homologado vs dato medido, y (e) comparador que reusa los mismos campos en columnas.

---

## 8. Diferencial (lo que ofrece y muchos no)
- [V] **Mediciones PROPIAS físicas** separadas del dato homologado: aceleración 40-80/80-120, frenada 60-0/120-0, **consumo real en recorrido km77**, habitabilidad y maletero **medidos a cinta** (VDA), y **errores de velocímetro/cuentakilómetros/ordenador de consumo** — transparencia métrica rarísima entre catálogos.
- [V] **Moose test (ISO-3888-2:2011)** con velocidad medida y vídeo — **firma reconocida internacionalmente** de km77.
- [V] **Equipamiento atómico por versión** con estado serie/opcional/paquete/no en 7 secciones (~100-130 ítems/modelo).
- [V] **Precio con fiscalidad española completa y tarifa fechada por mes** (trazabilidad temporal) + **distintivo ambiental DGT** integrado.
- [V] **Comparador de hasta 4 coches** sobre precio+ficha+equipamiento y **buscador por equipamiento**.
- [V] **Profundidad histórica** del catálogo (fichas desde ~1999/2000, incl. descatalogados y prototipos).
- [V] **Catálogo que nutre configuradores multi-país (DriveK, ES/FR/DE/IT, ~40 marcas)** y se entrega embebido a **+20 partners editoriales** — capacidad de distribución del dato.
- [V] **Estadísticas de mercado** (matriculaciones por país/marca/modelo/mes) como capa añadida.
- [V] **Cierre VO**: marketplace + **tasación física C2B** con informe técnico.

## 9. Gaps (lo que NO ofrece / no expone)
- [V] **El subdominio `spec-catalog` NO resuelve** (`spec-catalog.km77.com` → DNS ENOTFOUND). El "spec catalog" es el activo conceptual (catálogo de especificaciones), servido en km77.com y en los configuradores DriveK; **no existe ese host literal**.
- [V] **Sin API pública propia documentada** (ni endpoints, ni esquema JSON, ni auth, ni rate limits, ni diccionario de campos publicados por km77).
- [A] **Sin valoración financiera estructurada** (valor residual %, retail/trade, depreciación a futuro, ajuste por km como producto de dato): km77 da **precio nuevo** y **tasación VO puntual**, no curvas de RV ni cotización tipo guía (Ganvam/Eurotax). El **dato de valoración** vive fuera (su matriz es DriveK/AutoXY marketplace, no una guía de valores).
- [A] **Sin índices de mercado del usado** (days-to-sell, market-days-supply, price-to-market %, índice demanda/oferta): tiene matriculaciones de **coche nuevo**, no analítica transaccional del usado.
- [A] **Sin decode por VIN ni historial por matrícula/siniestros/km oficiales** como producto (a diferencia de Carfax/autoDNA/Motornet): el ID es por catálogo (marca→versión), no por VIN.
- [V] **Solo España** para precio/fiscalidad/mediciones (el multi-país es del configurador DriveK, no de km77).
- [A] **Scope a turismos**: sin moto/industrial/náutica/agrícola como dato propio.
- [A] **Paso de propiedad "MotorK→km77" no confirmado** por nota de prensa en esta auditoría (linaje DriveK/MotorK verificado a nivel de entidad operadora; el hito de adquisición concreto queda [A]).
- [V/A] **Mediciones por unidad probada** (no todos los modelos/versiones tienen mediciones propias; el EV auditado tenía consumo medido vacío). Cobertura de mediciones **parcial**, dependiente de qué unidades pasan por su banco.
- [V] **Contenido renderizado con fuerte carga publicitaria/JS** (el equipamiento y mediciones se sirven en sub-rutas y bloques dinámicos; ad-blocks ocupan el DOM en headless) — no hay endpoint abierto/CSV de las fichas.

---

## 10. Fuentes (URLs)
- https://www.km77.com/ — home, navegación (Marcas, Revista/Blog, Otras secciones, Comparador, Buscador), red DriveK/DriveMatch, VO/coches77, contacto Coslada.
- https://www.km77.com/aviso-legal — **DRIVEK SOLUTION, S.L.**, CIF **B-67817312**, Avda. San Pablo 28 Nave 27 Coslada, Registro Mercantil de Barcelona; subdominios operados; emails/teléfonos; referencias a DriveK/DriveMatch/Coches77.
- https://www.km77.com/politica-privacidad + https://www.dpoitlaw.com/en/portfolio_item/km77-com-2/ — operador histórico **Ruedas de Prensa, S.L.** (B-82262254), pruebas desde 1999.
- https://www.km77.com/coches/byd/seal/2024/estandar/estandar/seal-rwd/datos — datos técnicos + precios/fiscalidad + pestañas de ficha (extracción JS de tablas con caption).
- https://www.km77.com/coches/byd/seal/2024/estandar/estandar/seal-rwd/datos/equipamiento — **equipamiento**: 7 secciones / 127 ítems con estado serie/opcional (extracción JS).
- https://www.km77.com/coches/byd/seal/2024/estandar/mediciones-propias — **mediciones propias**: habitabilidad, maletero medido, aceleración/frenada, errores de instrumentación, consumo recorrido km77, velocidad de esquiva.
- https://www.km77.com/reportajes/varios/maniobra-de-esquiva-test-del-alce — metodología moose test (**ISO-3888-2:2011**, 60-90 km/h, condiciones).
- https://www.km77.com/comparador — comparador hasta 4 coches (precios, datos, equipamiento).
- https://www.km77.com/coches/bmw/tecnica/listado-completo — listado completo de versiones por marca.
- https://www.km77.com/mercado/europa/2021/enero.asp — estadísticas de matriculaciones por país/mes.
- https://www.km77.com/revista/general/cual-es-el-precio-idoneo-para-vender-mi-coche/ + https://www.km77.com/vo/te-ayudamos-con-la-venta-de-tu-vehiculo/ + https://coches.km77.com/ — VO + tasación C2B (24-48 h, prueba mecánica + inspección taller, informe + oferta).
- https://www.drivek.es/sobre-nosotros/ — DriveK: configurador ~40 marcas, ES/FR/DE/IT, parent **AutoXY S.p.A.**
- https://www.motork.ai/ + https://www.motork.io/drivek-car-configurator-portal/ — MotorK (LeadSparK/StockSparK/WebSparK); DriveK como configurador B2B integrado con +20 partners editoriales.
- https://en.wikipedia.org/wiki/MotorK — MotorK fundada como "Drivek" (Milán, 2010), fundadores, Euronext 2021.
- https://www.businesswire.com/news/home/20221215005663/en/MotorK-Completes-Sale-of-DriveK-Business-Unit + https://live.euronext.com/en/products/equities/company-news/2025-03-27-motork-completes-sale-remaining-20-stake-autoxy-spa-gedi — desinversión DriveK→GEDI/AutoXY (80% dic-2022, 20% mar-2025).
- https://www.tpi.it/economia/gruppo-gedi-giornali-auto-20210612795552/ + https://bebeez.it/private-equity/gedi-compra-il-78-del-motore-di-ricerca-dedicato-alle-quattro-ruote-autoxy/ + https://www.economyup.it/automotive/perche-gedi-ha-comprato-drivek-... — GEDI 78% de AutoXY (jun-2021), Exor/Agnelli controla GEDI.
- (ENOTFOUND) https://spec-catalog.km77.com/ — subdominio del encargo **inexistente** (DNS).

> Verificación: identidad/propiedad contrastada con ≥2 fuentes ortogonales (aviso-legal km77 + DPOitlaw para entidades; Wikipedia/MotorK + Business Wire/Euronext + BeBeez/TPI/Economyup para la cadena DriveK→GEDI/AutoXY→Exor). Campos atómicos **[V]** extraídos por Playwright/JS de las 3 superficies de dato de una ficha real (BYD Seal Design 2024). Campos de motor de combustión marcados **[A]** (no verificados sobre el EV auditado). Subdominio `spec-catalog` verificado inexistente. Ausencias (API, RV/valoración, índices de usado, VIN/historial) marcadas [A]/[V] como Gaps, sin inventar.
