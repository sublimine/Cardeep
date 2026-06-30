# Auditoría atómica — REPUVE (Registro Público Vehicular)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> **REPUVE** = **Registro Público Vehicular** de México. NO es una empresa comercial, ni guía de valoración, ni proveedor de inteligencia de mercado: es el **registro público nacional, gubernamental y gratuito** del Estado mexicano que da **seguridad pública y jurídica** a los actos sobre vehículos que circulan en el territorio. Es una **Dirección General que depende del Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)**. Su eje de valor es la **identidad legal del vehículo + estatus de robo/legal + padrón de propietario + chip RFID anti-robo**, no el precio ni el mercado.
> Web ciudadana: https://www2.repuve.gob.mx:8443/ciudadania/ · Portal sujetos obligados/entidades: http://entidades.sesnsp.gob.mx:8046/repuve/ · Info oficial: https://www.gob.mx/sesnsp/acciones-y-programas/consulta-ciudadana-del-registro-publico-vehicular-repuve
> Subdominio cardeep asignado por el orquestador (campo `subdomain`): **official-data**. Es una **etiqueta de categoría** ("dato oficial/gubernamental"), NO un host DNS de REPUVE.
> Fecha auditoría: 2026-06-30. Convención: **[V]** = verificado en fuente oficial (gob.mx / segob / Ley) · **[A]** = asumido/inferido (marcado) · **[3P]** = dato de tercero (guías mexicanas, prensa estatal), no oficial de SESNSP.
> ⚠ **Limitación de acceso:** el portal ciudadano `:8443` y el portal de entidades `:8046` **no respondieron desde esta red** (`ERR_CONNECTION_TIMED_OUT` / `ECONNREFUSED`) — están **geo-restringidos/limitados a redes MX** o protegidos. La estructura de la consulta ciudadana (3 pestañas, semáforo, campos) se reconstruyó con **≥2 fuentes concordantes** (páginas oficiales gob.mx + guías ciudadanas mexicanas) y se marca [3P] cuando la fuente primaria no fue accesible directamente.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **REPUVE — Registro Público Vehicular** | [V] |
| Naturaleza | **Registro público nacional gubernamental** (instrumento de información del Sistema Nacional de Seguridad Pública); no empresa, no ánimo de lucro, no producto comercial | [V] |
| Operador | **Dirección General del REPUVE**, dependiente del **Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)** | [V] |
| Adscripción | **Sistema Nacional de Seguridad Pública (SNSP)**; el SESNSP es órgano administrativo desconcentrado (históricamente coordinado con SEGOB; en la era actual con la SSPC) | [V] |
| HQ | **Ciudad de México** (administración central del SESNSP); operación territorial vía los **Secretariados Ejecutivos Estatales de Seguridad Pública (SESESP)** de las 32 entidades | [V/A] |
| Base legal | **Ley del Registro Público Vehicular**, publicada en el **DOF el 1-sep-2004** (última reforma 20-may-2021) | [V] |
| Reglamento | **Reglamento de la Ley del RPV**, publicado en **DOF 5-dic-2007** (en vigor +90 días) | [V] |
| Inicio de operación | **ACUERDO 03/2008** (DOF 3-mar-2008): procedimientos de inscripciones, avisos y notificaciones por medios electrónicos | [V] |
| Objeto legal | "Establecer y regular la operación, funcionamiento y administración del Registro Público Vehicular" | [V] |
| Misión | "Otorgar seguridad pública y jurídica a los actos que se realicen con vehículos que circulan en el territorio nacional"; coadyuvar a salvaguardar integridad, derechos y patrimonio de las personas | [V] |
| Modelo | **Gratuito, público** (inscripción, avisos y consultas siempre gratuitas por mandato de ley) | [V] |

### Qué es (y qué no es) [V]
- **Es:** el **padrón vehicular nacional oficial** que cruza altas/bajas/robos/gravámenes y da **certeza jurídica** sobre un vehículo; emite la **constancia de inscripción** (calcomanía con chip RFID); ofrece **consulta ciudadana gratuita** de estatus de robo y datos básicos; y opera una **red de arcos de lectura RFID** anti-robo en carreteras/ciudades.
- **No es:** guía de valor, índice de mercado, decodificador comercial de VIN, catálogo de equipamiento/specs de marketing, ni proveedor con API pública/SLA. **No vende nada y no estima precios.**
- **Rol en el ecosistema (para Cardeep):** es la **capa de "vida legal y de seguridad" del vehículo en México** — robo/recuperación/gravamen/situación legal/propietario registral — equivalente funcional de la capa Carfax/HPI/título, **pero estatal, gratuita y con chip físico**. NO aporta valoración ni specs comerciales: esa capa la dan otros (J.D. Power México, Libro Azul, guías comerciales).

### Clientes objetivo / usuarios [V]
- **Ciudadanía / compradores de autos usados** (consulta ciudadana antes de comprar).
- **Autoridades** (federales, estatales, municipales, fiscalías, policía) — consumo operativo vía arcos y portal.
- **Sujetos obligados** (armadoras, distribuidoras/concesionarias, importadores, aseguradoras, comercializadoras, instituciones de crédito/arrendadoras): **obligados por ley a inscribir y presentar avisos**.
- **Entidades federativas** (vía SESESP) que integran sus padrones de control vehicular y emplacamiento.

---

## 2. Cobertura

### Geográfica [V]
- **México — nacional, las 32 entidades federativas.** Registro federal único; operación e implantación física **dispar por estado** (cada SESESP despliega módulos fijos/móviles y arcos a su ritmo).
- **No multipaís.** Es exclusivamente mexicano.

### Scope de vehículos [V]
- **Todos los tipos:** automóviles, camiones/camionetas, **motocicletas**, vehículos de carga, transporte público, maquinaria; nacionales **e importados**.
- **Nuevo y usado:** el flujo arranca en origen — la **armadora/ensambladora inscribe el vehículo nuevo** y la distribuidora presenta el **aviso de venta**; los usados entran por avisos de cambio de propietario, emplacamiento estatal y regularización.
- **Enfoque:** **seguridad y certeza jurídica**, NO ámbito fiscal ni mercantil-comercial (lo dice la propia exposición de motivos).

### Escala (cifras estatales medidas, 2026) [3P — prensa estatal]
- Sin cifra nacional oficial única accesible en esta auditoría [A]. Indicadores estatales:
  - **Tlaxcala:** **465.781 unidades inscritas** sobre un parque estatal >800.000; **149 arcos** (fijos+móviles). 261 vehículos recuperados en 2026 (récord desde 2021).
  - **Zacatecas:** **113 arcos** de monitoreo (operación conjunta REPUVE + SESP estatal + SSPC).
- Tecnología de arco: **antenas RFID + cámaras LPR analíticas de alta precisión + iluminadores nocturnos**; identifica vehículos a **hasta 250 km/h**, día y noche. [3P]

### Temporal / vigencia del dato [V/3P]
- La consulta ciudadana puede tener **hasta 48 h de retraso** desde que se modifica el estatus (p. ej. desde la denuncia de robo). [3P, concordante en múltiples guías]
- **Vehículos no inscritos** (resultado "sin información"): típicamente **anteriores a 2008**, **motos no estandarizadas**, o **importados/"chocolate" sin regularizar**. [3P]
- Vida útil mínima del **chip RFID: 10 años** sin alterar funcionamiento. [3P]

---

## 3. Productos + campos atómicos

REPUVE es **una sola base de datos nacional** servida por **5 superficies**: (1) **Consulta Ciudadana** (web `:8443` + app), (2) **Constancia de Inscripción** (calcomanía + chip RFID), (3) **Red de arcos de lectura RFID**, (4) **Portal de Sujetos Obligados / Entidades** (inscripciones, avisos, consulta autenticada / web service), (5) **Padrón / base de datos del Registro** (la verdad central). El núcleo de valor para Cardeep son los **campos del padrón** y el **estatus legal/robo**.

### 3.1 CAMPOS ATÓMICOS — Padrón / base de datos del Registro
> Fuente normativa: **Ley del RPV (art. que define el contenido del Registro)** + Reglamento + práctica de los sujetos obligados. La base se conforma con "la información que de cada vehículo proporcionen las autoridades federales, las Entidades Federativas y los sujetos obligados".

**Identidad física del vehículo:**
- **Número de Identificación Vehicular (NIV / VIN)** — 17 caracteres. [V]
- **Número de serie** (chasis; en práctica suele coincidir con el NIV). [3P]
- **Número de motor.** [3P]
- **Marca.** [V]
- **Modelo / año-modelo.** [V]
- **Año.** [V]
- **Línea / versión.** [A — citado por algunas guías; no confirmado en fuente oficial]
- **Tipo** (de vehículo: particular, público, taxi, carga…). [V]
- **Clase.** [3P]
- **Color.** [V]
- **Tipo de combustible.** [V/3P]
- **Cilindrada / capacidad del motor.** [3P]
- **Número de puertas.** [A]
- **Capacidad** (pasajeros / carga). [3P]
- **Peso.** [3P]
- **Clave vehicular** (clave de registro del modelo). [3P — web service estatal]
- **Procedencia** (nacional / importado). [A]

**Identificadores registrales:**
- **Número de Constancia de Inscripción (NCI)** — **8 caracteres alfanuméricos**, único e irrepetible; identificador del vehículo en la BD. [V]
- **Folio de Constancia de Inscripción (FCI)** — folio del lote/holograma físico (longitud variable; impreso bajo el código de barras). [3P]
- **Número de placa(s) / emplacamiento.** [V]
- **Entidad federativa que registró el vehículo.** [V]
- **Fecha de inscripción / registro.** [V]
- **Estatus de inscripción** (correcto proceso de inscripción vehicular). [V]

**Datos del propietario:**
- **Nombre, denominación o razón social del propietario.** [V]
- **Domicilio del propietario.** [V]
- **RFC del propietario** (vista de sujetos obligados/autoridad). [3P]
- **CURP del propietario** (vista de sujetos obligados/autoridad). [3P]

**Estatus legal / de seguridad (el núcleo diferencial):**
- **Situación legal / estatus jurídico** — si está vinculado a algún proceso judicial. [V]
- **Reporte de robo (PGJ / Fiscalía General de Justicia)** — denuncia ante Ministerio Público. [V/3P]
- **Reporte de robo a aseguradora (OCRA — Oficina Coordinadora de Riesgos Asegurados)** — reporte de las aseguradoras afiliadas. [V/3P]
- **Reporte de recuperación** (vehículo recuperado). [V]
- **Semáforo de estatus de robo:** **Verde** (sin reporte) / **Amarillo** (recuperado) / **Rojo** (robo vigente) / **Sin resultado** (no inscrito). [3P, ≥3 guías concordantes]
- **Gravámenes** (liens). [V]
- **Bloqueos / restricciones.** [3P]

**Movimientos / avisos (datos que las autoridades y sujetos obligados deben suministrar para mantener actualizado el Registro):** [V — enumeración de la Ley]
- **Altas.**
- **Bajas.**
- **Cambios de propietario.**
- **Emplacamientos.**
- **Infracciones.**
- **Pérdidas.**
- **Robos.**
- **Recuperaciones.**
- **Pago de tenencias y contribuciones.**
- **Destrucción de vehículos.**

### 3.2 Consulta Ciudadana — superficie pública (web `:8443` + app) [V/3P]
Entrada por **NIV (17 caracteres)**, **Placas**, o **Folio de Constancia de Inscripción**, sin espacios ni guiones + **captcha** → botón "Consultar". Gratuita, sin registro. Resultado en segundos, organizado en **3 pestañas** (ver §7 Placement). Permite **Exportar PDF** (o Ctrl+P) de la constancia/resultado. [3P]

### 3.3 Constancia de Inscripción (calcomanía + chip RFID) [3P]
Calcomanía **rectangular, azul, con logos REPUVE y México en dorado**, adherida al parabrisas. Lleva un **dispositivo electrónico RFID** intransferible que **solo almacena el NCI** (no toda la ficha); al leerse en un arco, consulta el NCI contra la BD central y devuelve **estatus en tiempo real**. **Inviolable:** el chip se destruye si se intenta despegar (anti-falsificación/anti-reuso). Vida útil mínima **10 años**. Se coloca en **módulos REPUVE** fijos/móviles tras verificación documental y física del vehículo.

### 3.4 Red de arcos de lectura RFID [3P]
Infraestructura física en vías: **arcos fijos y unidades móviles** con **antenas RFID + cámaras LPR + iluminadores nocturnos**; leen NCI (chip) y placa (LPR) a alta velocidad → alerta automática si el vehículo tiene reporte. Es la capa de **detección operativa anti-robo**, exclusiva de un registro estatal.

### 3.5 Portal de Sujetos Obligados / Entidades (`:8046`) [V/3P]
Acceso **autenticado** (usuario/contraseña) para armadoras, distribuidoras, importadores, aseguradoras, comercializadoras, instituciones de crédito y entidades federativas: **inscripción de vehículos**, **presentación de avisos** (venta, baja, cambio de propietario, robo, recuperación, gravamen, destrucción), **consulta del RPV** (`consultaRPV.do`) y **notificaciones electrónicas**. Algunas entidades exponen **web services REST** que devuelven la ficha (placa, código REPUVE/NCI, clave vehicular, modelo, número de serie, número de motor, clase, tipo, color, combustible, cilindrada, peso, propietario con nombre/RFC/CURP). [3P — web service estatal Colima]

---

## 4. Metodología y fuentes de datos
- **Suministro obligatorio por ley** [V]: "Para mantener actualizado el Registro, las autoridades federales y las de las Entidades Federativas suministrarán la información relativa a altas, bajas, cambio de propietario, emplacamientos, infracciones, pérdidas, robos, recuperaciones, pago de tenencias y contribuciones, destrucción de vehículos, gravámenes y otros datos." Los **sujetos obligados** (armadoras, distribuidoras, importadores, aseguradoras, etc.) están obligados a **inscribir y presentar avisos**.
- **Origen en fábrica/importación** [V/3P]: el vehículo nuevo lo inscribe la **armadora**; el usado entra por avisos y por emplacamiento estatal; los importados, por regularización.
- **Cruce de bases para robo** [3P]: el estatus de robo resulta de **cruzar la base de las Fiscalías/PGJ (denuncia ante MP) con la de OCRA (aseguradoras)** — por eso un vehículo puede aparecer en OCRA y no en PGJ, o viceversa (3 pestañas separadas).
- **Identificación física en módulo** [3P]: técnicos certificados verifican documentación y físico del vehículo antes de colocar la constancia/chip.
- **Lectura RFID + LPR** [3P]: validación operativa en arcos (chip = NCI; cámara = placa) → consulta en tiempo real.
- **Latencia** [3P]: hasta **48 h** de retraso en reflejar cambios de estatus.
- **Administración técnica** [V]: "El Secretariado Ejecutivo integrará, coordinará, desarrollará, administrará y controlará la infraestructura tecnológica, los sistemas y procedimientos" del Registro.

---

## 5. Entrega
- **Consulta Ciudadana web** (HTML, `https://www2.repuve.gob.mx:8443/ciudadania/`): formulario NIV/Placa/Folio + captcha → resultado en 3 pestañas + **Exportar PDF**. [V/3P]
- **App móvil** (Android/iOS): consulta ciudadana desde el teléfono. Existe app de terceros (p. ej. Rastreator) y apps tipo "ChecaTuAuto Consulta Ciudadana" en Google Play; **estatus de oficialidad SESNSP no verificado** → marcado [A/3P].
- **Constancia de Inscripción** (calcomanía física + chip RFID en parabrisas) — entrega del dato como documento legal + dispositivo leíble. [3P]
- **Arcos de lectura RFID/LPR** (entrega operativa a autoridad, no al ciudadano). [3P]
- **Portal autenticado de Sujetos Obligados/Entidades** (`:8046`): alta/avisos/consulta + **web services** de integración (DMS estatal / sistemas de control vehicular). [V/3P]
- **NO hay API pública abierta para ciudadanos** (a diferencia de NHTSA vPIC): el acceso de integración es **autenticado** y reservado a sujetos obligados/entidades. [A — no se halló API pública documentada]

---

## 6. Precio
- **Gratuito por mandato de ley** [V]: "La inscripción de vehículos, la presentación de avisos y las consultas en el Registro serán gratuitas." La **Consulta Ciudadana no tiene costo**.
- **Excepciones de cobro (operativas, estatales)** [3P]:
  - Algunas entidades cobran **una pequeña suma por la entrega de la constancia física** de inscripción.
  - **Regularización de vehículos "chocolate" (importados irregulares):** ~**$2.500 MXN** por vehículo (programa de regularización). [3P]
- **Sin tarifas de API, sin suscripción, sin SLA comercial** — no es un producto de pago. [V/A]

---

## 7. Placement — dónde se ubica cada dato en su UI/entrega
> Patrón a copiar por Cardeep: superficie/pantalla → dato. El patrón REPUVE clave es **una sola entrada (NIV/Placa/Folio) → semáforo de estatus arriba + 3 pestañas por FUENTE de verdad** (vehículo / fiscalía / aseguradora). Separa la **ficha de identidad** del **estatus de robo por origen de reporte**.

| Dato | Dónde lo colocan (superficie / pantalla) |
|---|---|
| **NIV / Placa / Folio de constancia** (entrada) | Cabecera del formulario de **Consulta Ciudadana** (un campo + captcha + botón "Consultar"); única puerta de entrada pública. |
| **Semáforo de estatus de robo** (Verde/Amarillo/Rojo/No inscrito) | **Indicador de color destacado** del resultado — lo primero y más visible; resume el veredicto antes del detalle. |
| **Datos del vehículo** (Marca, Modelo, Año, Tipo, Color, Entidad de registro, NCI, Estatus de inscripción) | **Pestaña 1 "Datos del vehículo"** — ficha de identidad; el usuario coteja contra documentación física. |
| **Reporte de robo PGJ/Fiscalía** (denuncia ante Ministerio Público, por estado, hasta 48 h) | **Pestaña 2 "PGJ"** — reportes de las fiscalías estatales. |
| **Reporte de robo a aseguradoras (OCRA)** (27 aseguradoras afiliadas; solo por NIV) | **Pestaña 3 "OCRA"** — reportes del sector asegurador; independiente de la pestaña PGJ. |
| **Constancia / NCI exportable** | Botón **"Exportar PDF"** (abajo a la derecha) o Ctrl+P → PDF con NCI y datos de registro. |
| **Estatus en tiempo real (operativo)** | **Arco de lectura RFID/LPR**: el chip (NCI) + placa se leen al paso → alerta automática a la autoridad. |
| **Identidad física + propietario + gravámenes + movimientos** | **Portal autenticado de Sujetos Obligados/Entidades** (`:8046`) + web service de integración (vista completa con RFC/CURP). |
| **Documento legal en el vehículo** | **Calcomanía REPUVE** en el parabrisas (azul, logos dorados) + **chip RFID** (almacena solo NCI). |

---

## 8. Diferencial (lo que ofrece y otras no)
- [V] **Registro estatal único, oficial y gratuito** de identidad legal del vehículo en México — autoridad gubernamental + **certeza jurídica**; ninguna guía comercial puede igualar "$0 + carácter de fe pública".
- [V/3P] **Estatus de robo cruzado de DOS fuentes independientes** (Fiscalías/PGJ + aseguradoras/OCRA) presentado en pestañas separadas — captura casos que una sola fuente perdería.
- [3P] **Chip RFID físico anti-robo + red de arcos LPR** a hasta 250 km/h: capa de **detección operativa en vía pública** inexistente en cualquier proveedor comercial de datos.
- [3P] **Constancia inviolable** (se destruye al despegar) como **documento legal** vinculado al vehículo.
- [V] **Padrón con propietario registral, gravámenes, infracciones, tenencias y movimientos (altas/bajas/cambios/destrucción)** — capa de "vida legal" que las guías de valor no tienen.
- [V] **Obligatoriedad legal de suministro** (armadoras, distribuidoras, aseguradoras, autoridades) → cobertura de origen en fábrica/importación.

## 9. Gaps (lo que NO ofrece / no expone)
- [V/A] **CERO valoración y CERO precio de mercado**: no hay trade/retail/wholesale, valor residual %, curva de depreciación, price-to-market, days-to-sell, market days supply, índice demanda/oferta ni forecasting. No es su propósito (explícitamente "no fiscal ni mercantil").
- [V/A] **Sin specs comerciales ni equipamiento de marketing**: no hay decodificación de trim/opciones, imágenes, colores RGB/HEX, packages ni MSRP. Solo atributos físicos básicos (marca/modelo/año/tipo/color/combustible/motor).
- [3P/A] **Sin historial de kilometraje ni de siniestros/daños**: no hay odómetro, fraude de km, ni historial de accidentes/peritaje. Solo cubre **robo / recuperación / situación legal / gravamen** — no la condición física ni el uso.
- [A] **No es decodificador de VIN genérico**: no decodifica un NIV arbitrario a specs (como NHTSA vPIC); solo devuelve **lo que está inscrito** en el padrón. Vehículo no inscrito → "sin información".
- [A] **Sin API pública abierta para ciudadanos**: acceso de integración **autenticado** y reservado a sujetos obligados/entidades; el ciudadano usa formulario web + captcha + app. Sin endpoints REST públicos documentados, sin key libre, sin batch.
- [V/3P] **Solo México**; **implantación dispar por estado** (módulos y arcos desiguales); datos dependientes de que autoridades/sujetos obligados reporten → huecos de densidad.
- [3P] **Latencia de hasta 48 h** en reflejar cambios de estatus (ventana de riesgo en compra-venta).
- [V/A] **Sin capa analítica de ningún tipo**: no hay comparador, dashboard de mercado, alertas comerciales, ni informe de valoración. Es registro + semáforo, no inteligencia.
- ⚠ [V] **Acceso geo-restringido**: portales `:8443` y `:8046` no respondieron desde red no-MX en esta auditoría → dependencia operativa de red mexicana; campos de consulta ciudadana verificados vía fuentes oficiales + ≥2 guías [3P], no por render directo de la página primaria.

---

## 10. Fuentes (URLs)
- https://www2.repuve.gob.mx:8443/ciudadania/ — **portal primario Consulta Ciudadana** (NO accesible desde esta red, `ERR_CONNECTION_TIMED_OUT`; geo-restringido/MX).
- https://www.gob.mx/sesnsp/acciones-y-programas/consulta-ciudadana-del-registro-publico-vehicular-repuve — [V] consulta por NIV/Placas/Folio; campos del reporte (situación legal/robo, entidad de registro, características básicas marca/modelo/año/tipo/color, NCI, estatus jurídico, proceso de inscripción); operada por SESNSP; gratuita.
- https://www.gob.mx/sesnsp/acciones-y-programas/registro-publico-vehicular-repuve-168639 — [V] "REPUVE es una Dirección General que depende del SESNSP"; objetivo de seguridad pública y jurídica; todos los trámites gratuitos.
- https://www.gob.mx/segob/acciones-y-programas/consulta-al-registro-publico-vehicular — [V] consulta al RPV (datos devueltos: marca/modelo/versión, tipo, placas, fecha de registro, NIV, situación legal, cambios de propietario).
- http://segob.gob.mx/work/models/SEGOB/Resource/1325/1/images/Registro_Publico_Vehicular.pdf — [V — vía buscador] historia: Ley DOF 1-sep-2004, Reglamento DOF 5-dic-2007, ACUERDO 03/2008 DOF 3-mar-2008; propósito de seguridad pública.
- https://www.diputados.gob.mx/LeyesBiblio/pdf/269_200521.pdf — **Ley del Registro Público Vehicular** (últ. reforma 20-may-2021): el Registro se conforma con info de autoridades/sujetos obligados; enumeración de altas/bajas/cambio de propietario/emplacamientos/infracciones/pérdidas/robos/recuperaciones/tenencias/destrucción/gravámenes; info del vehículo incl. NIV; nombre/domicilio del propietario; el SESNSP administra. (PDF binario; texto extraído vía resumen de buscador.)
- https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LRPV.pdf — Reglamento de la Ley del RPV (constancia de inscripción art. ~18: calcomanía + dispositivo RFID con datos básicos; formato/colocación por el SESNSP). (No accesible directo, `ECONNREFUSED`; vía resumen de buscador.)
- https://mexicenter.com.mx/repuve/consulta/ — [3P] estructura de **3 pestañas** (Datos del vehículo / PGJ-Fiscalía / OCRA-aseguradoras); semáforo Verde/Amarillo/Rojo/No inscrito; OCRA solo por NIV; 27 aseguradoras; 48 h de retraso.
- https://mexicenter.com.mx/repuve/chip/ — [3P] **NCI** (8 alfanum., identificador del vehículo) vs **FCI** (folio del lote bajo el código de barras); el chip solo guarda el NCI; "Exportar PDF".
- https://www.repuve-consultar.com/chip-repuve y https://repuveconsulta.com/chip-repuve/ — [3P] constancia = calcomanía azul + logos dorados; RFID intransferible; se destruye al despegar; vida útil ≥10 años; lectura por arcos.
- https://www.rastreator.mx/seguros-de-auto/articulos-destacados/que-es-repuve — [3P] REPUVE depende del SESNSP; campos (inscripción, características, emplacamiento, estatus legal); entrada por placa/NIV/folio; constancia en parabrisas; consultas gratuitas.
- http://wstransporte.col.gob.mx/ — [3P] web service REST estatal (Colima): ficha con placa, código REPUVE/NCI, clave vehicular, modelo, número de serie, número de motor, clase, tipo, color, combustible, cilindrada, peso, propietario (nombre, RFC, CURP). (Redirige a col.gob.mx; campos vía resumen de buscador.)
- http://entidades.sesnsp.gob.mx:8046/repuve/login.jsp y http://sujetosobligados.repuve.gob.mx:8046/repuve/consultaRPV.do — [V — referencia] portal autenticado de entidades/sujetos obligados (alta/avisos/consulta). No accesible (auth + geo).
- https://www.385grados.com/tlaxcala/115778/ y https://www.tyt.com.mx/nota/nuevo-modelo-repuve-arranca-en-zacatecas — [3P] cifras estatales: Tlaxcala 465.781 inscritos / 149 arcos; Zacatecas 113 arcos; arco RFID+LPR hasta 250 km/h.
- https://www.cespcampeche.gob.mx/repuve/public/costo y https://www.cespcampeche.gob.mx/repuve/public/como-cuidar-chip — [3P] gratuidad del trámite; cuidados del chip.

> Verificación: identidad, operador (SESNSP), base legal (Ley DOF 2004), fundación y gratuidad contrastados con **≥2 fuentes oficiales gob.mx/segob + Ley**. Campos del padrón [V] de la enumeración de la Ley + páginas oficiales; campos físicos del vehículo (motor/serie/cilindrada/peso/clave/RFC/CURP) y estructura de 3 pestañas/semáforo [3P] de ≥2 guías ciudadanas mexicanas concordantes (portal primario `:8443` geo-restringido, no renderizable desde esta red — declarado, no inventado). Precio/gratis [V] de Ley + gob.mx. Cifras de escala [3P] son estatales, no nacional-oficial → marcadas. "official-data" = etiqueta de categoría del orquestador, no host DNS.
